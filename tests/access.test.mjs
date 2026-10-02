import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { execFileSync, spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';
import { readProjectEnv as readPgEnv } from '../skills/postgresql-access/scripts/project-env.mjs';
import { readProjectEnv as readGrafanaEnv } from '../skills/grafana-access/scripts/project-env.mjs';
import { resolveClientConfig, redactDsn, loadPostgresRuntime } from '../skills/postgresql-access/scripts/postgres-env.mjs';
import { runReadOnlyQuery } from '../skills/postgresql-access/scripts/postgres-client.mjs';
import { resolveInstance, redactUrl } from '../skills/grafana-access/scripts/grafana-env.mjs';
import { GrafanaClient } from '../skills/grafana-access/scripts/grafana-client.mjs';
const root = fileURLToPath(new URL('../', import.meta.url));
async function fixture(t) {
 const dir = await mkdtemp(path.join(tmpdir(), 'skills-access-'));
 t.after(() => rm(dir, {recursive:true, force:true}));
 execFileSync('git', ['init','-q',dir]);
 await mkdir(path.join(dir,'.agents/local'),{recursive:true});
 return dir;
}
async function cli(script,args,cwd) {
 const child=spawn(process.execPath,[path.join(root,script),...args],{cwd,env:{...process.env,DATABASE_URL:'postgresql://ambient:secret@invalid/db'}});
 let stdout='',stderr='';child.stdout.on('data',d=>stdout+=d);child.stderr.on('data',d=>stderr+=d);
 const [code]=await once(child,'close');return {code,stdout,stderr};
}
for (const [name,read] of [['pg',readPgEnv],['grafana',readGrafanaEnv]]) {
 test(`${name}: local env is literal, nearest checkout and explicit override wins`,async t=>{
  const dir=await fixture(t),nested=path.join(dir,'nested');await mkdir(nested);
  await writeFile(path.join(dir,'.agents/local/.env.agents'),'VALUE="$(touch do-not-create)&literal"\n');
  assert.equal((await read(undefined,nested)).env.VALUE,'$(touch do-not-create)&literal');
  execFileSync('git',['init','-q',nested]);
  await assert.rejects(read(undefined,nested),/Cannot read/);
  const custom=path.join(dir,'custom.env');await writeFile(custom,'VALUE=explicit\n');
  assert.equal((await read(custom,nested)).env.VALUE,'explicit');
 });
 test(`${name}: no application env fallback`, async t=>{
  const dir=await fixture(t);await writeFile(path.join(dir,'.env'),'DATABASE_URL=secret\n');
  await assert.rejects(read(undefined,dir),/Cannot read/);
 });
}
test('pg: no inherited credentials, TLS verified, query secrets redacted',async t=>{
 const dir=await fixture(t);await writeFile(path.join(dir,'.agents/local/.env.agents'),'OTHER=value\n');
 await assert.rejects(loadPostgresRuntime({cwd:dir}),/DATABASE_URL/);
 const url='postgresql://reader:secret@db.example.invalid/app';
 assert.equal(resolveClientConfig({DATABASE_URL:url}).ssl.rejectUnauthorized,true);
 assert.equal(resolveClientConfig({DATABASE_URL:url+'?sslmode=disable'}).ssl,false);
 assert.throws(()=>resolveClientConfig({DATABASE_URL:url+'?sslmode=require'}),/verify-full/);
 assert.doesNotMatch(redactDsn(url+'?password=secret'),/reader|secret|password/);
 assert.doesNotMatch(redactUrl('https://u:secret@example.invalid/?token=secret'),/secret|token/);
});
test('pg CLI blocks writes and obsolete write override before connection',async t=>{
 const dir=await fixture(t);
 for (const args of [['--sql','UPDATE example SET value=1'],['--sql','SELECT 1','--allow-write'],['--sql','SET TRANSACTION READ WRITE']]) {
  const result=await cli('skills/postgresql-access/scripts/run-query.mjs',args,dir);
  assert.equal(result.code,2,result.stderr);assert.match(result.stderr,/Blocked/);assert.doesNotMatch(result.stderr,/ambient|secret/);
 }
});
test('Grafana requires explicit multi-instance selection and forbids URL credentials',()=>{
 const env={GRAFANA_INSTANCES:'dev,stage',GRAFANA_USERNAME:'reader',GRAFANA_PASSWORD:'secret',GRAFANA_DEV_URL:'https://example.invalid',GRAFANA_STAGE_URL:'https://stage.example.invalid'};
 assert.throws(()=>resolveInstance(env),/Select --instance/);
 assert.equal(resolveInstance(env,'stage').id,'stage');
 assert.throws(()=>resolveInstance({...env,GRAFANA_STAGE_URL:'https://u:secret@example.invalid'},'stage'),/invalid base URL/);
});
test('Grafana CLI login, subpath, logs, metrics, datasource ambiguity and API errors',async t=>{
 const dir=await fixture(t);let multi=false,queryError=false;const seen=[];
 const server=createServer(async(req,res)=>{
  let body='';for await (const chunk of req) body+=chunk;
  seen.push({url:req.url,auth:req.headers.authorization,cookie:req.headers.cookie});
  res.setHeader('content-type','application/json');
  if(req.url==='/grafana/login') {assert.equal(JSON.parse(body).password,'fixture-password');res.setHeader('set-cookie','grafana_session=fixture-session; Path=/');res.end('{}');return;}
  assert.equal(req.headers.cookie,'grafana_session=fixture-session');
  if(req.url==='/grafana/api/datasources') {res.end(JSON.stringify([{uid:'logs',name:'logs',type:'loki'},{uid:'metrics',name:'metrics',type:'prometheus'},...(multi?[{uid:'other',type:'loki'}]:[])]));return;}
  if(req.url==='/grafana/api/ds/query') {res.end(JSON.stringify(queryError?{results:{A:{error:'fixture-sensitive-message',status:400}}}:{results:{A:{frames:[{schema:{fields:[{name:'Time',type:'time'},{name:'Line'}]},data:{values:[[1780000000000],['request-example completed']]}}]}}}));return;}
  if(req.url.startsWith('/grafana/api/datasources/proxy/uid/metrics/api/v1/query?')) {res.end(JSON.stringify({status:'success',data:{resultType:'vector',result:[{metric:{job:'example'},value:[1780000000,'1']}]}}));return;}
  res.statusCode=404;res.end('{}');
 });
 server.listen(0,'127.0.0.1');await once(server,'listening');t.after(()=>new Promise(resolve=>server.close(resolve)));
 const url=`http://127.0.0.1:${server.address().port}/grafana`;
 await writeFile(path.join(dir,'.agents/local/.env.agents'),`GRAFANA_URL=${url}\nGRAFANA_USERNAME=fixture-reader\nGRAFANA_PASSWORD=fixture-password\n`);
 const script='skills/grafana-access/scripts/query-logs.mjs';
 let result=await cli(script,['--expr','{service_name="example"}','--json'],dir);
 assert.equal(result.code,0,result.stderr);assert.equal(JSON.parse(result.stdout).entries[0].line,'request-example completed');assert.doesNotMatch(result.stdout,/fixture-password|fixture-session/);
 result=await cli('skills/grafana-access/scripts/query-metrics.mjs',['--expr','up','--instant','--json'],dir);
 assert.equal(result.code,0,result.stderr);assert.match(result.stdout,/'1'|"1"/);
 multi=true;result=await cli(script,['--expr','{}'],dir);assert.notEqual(result.code,0);assert.match(result.stderr,/Multiple/);
 result=await cli(script,['--expr','{}','--loki-uid','logs'],dir);assert.equal(result.code,0,result.stderr);
 queryError=true;result=await cli(script,['--expr','{}','--loki-uid','logs'],dir);assert.notEqual(result.code,0);assert.doesNotMatch(result.stderr,/fixture-sensitive/);
 assert.ok(seen.length>0);assert.ok(seen.every(r=>r.auth===undefined));
});

test('Grafana rejects HTML success and suppresses malformed JSON bodies', async t => {
 const original = globalThis.fetch;
 t.after(() => { globalThis.fetch = original; });
 for (const kind of ['html', 'malformed']) {
  globalThis.fetch = async url => {
   if (String(url).endsWith('/login')) return new Response('{}', {headers:{'content-type':'application/json','set-cookie':'grafana_session=fixture; Path=/'}});
   return new Response(kind === 'html' ? '<html>sign in</html>' : 'private_payload_123', {headers:{'content-type':kind === 'html' ? 'text/html' : 'application/json'}});
  };
  const client = new GrafanaClient({url:'http://fixture.invalid',username:'reader',password:'fixture'});
  for (const query of [() => client.queryLogs({expr:'{}',lokiUid:'logs'}), () => client.queryMetricsInstant({expr:'up',prometheusUid:'metrics'})]) {
   await assert.rejects(query(), error => {
    assert.doesNotMatch(error.message,/private_payload_123|<html>/);
    assert.match(error.message,/Unexpected|malformed|query failed/);
    return true;
   });
  }
 }
});

test('PostgreSQL integration: read result, write transaction denial, one statement, CLI', {skip:!process.env.SKILLS_TEST_DATABASE_URL}, async t=>{
 const dir=await fixture(t);await symlink(path.join(root,'node_modules'),path.join(dir,'node_modules'),'dir');
 await writeFile(path.join(dir,'.agents/local/.env.agents'),`DATABASE_URL=${process.env.SKILLS_TEST_DATABASE_URL}\n`);
 const runtime=await loadPostgresRuntime({cwd:dir});
 assert.equal((await runReadOnlyQuery(runtime,'SELECT 42 AS answer')).rows[0].answer,42);
 await assert.rejects(runReadOnlyQuery(runtime,'CREATE TABLE should_not_exist (id int)'),/read-only/);
 await assert.rejects(runReadOnlyQuery(runtime,'SELECT 1; SELECT 2'),/multiple commands/);
 const result=await cli('skills/postgresql-access/scripts/run-query.mjs',['--sql','SELECT 42 AS answer'],dir);
 assert.equal(result.code,0,result.stderr);assert.equal(JSON.parse(result.stdout).rows[0].answer,42);
});
