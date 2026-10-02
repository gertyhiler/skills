"""Contract tests use temporary consumers and fictional HTTP/database fixtures."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GRAFANA = ROOT / 'skills/grafana-access/scripts/grafana.py'
POSTGRES = ROOT / 'skills/postgresql-access/scripts/postgres.py'
sys.path.insert(0, str(GRAFANA.parent))
from access_common import AccessError, load_env, write_private

def module(name, script):
    spec = importlib.util.spec_from_file_location(name, script)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

grafana = module('grafana', GRAFANA)
postgres = module('postgres', POSTGRES)

class Contracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skills-python-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', self.root], check=True)
        self.local = self.root / '.agents/local'
        self.local.mkdir(parents=True)
        self.envfile = self.local / '.env.agents'

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=30,
                              env=os.environ | {'DATABASE_URL': 'postgresql://ambient:secret@invalid/db'})

    def test_env_literal_nearest_checkout_and_override(self):
        self.envfile.write_text('VALUE="$(touch must-not-exist)&${HOME}"\n')
        child = self.root / 'nested'
        child.mkdir()
        self.assertEqual(load_env(cwd=child)['VALUE'], '$(touch must-not-exist)&${HOME}')
        self.assertFalse((self.root / 'must-not-exist').exists())
        subprocess.run(['git', 'init', '-q', child], check=True)
        with self.assertRaises(AccessError):
            load_env(cwd=child)
        self.assertEqual(load_env(str(self.envfile), child)['VALUE'], '$(touch must-not-exist)&${HOME}')

    def test_missing_config_does_not_fall_back(self):
        (self.root / '.env').write_text('DATABASE_URL=wrong\n')
        with self.assertRaises(AccessError):
            load_env(cwd=self.root)
        self.envfile.write_text('OTHER=value\n')
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://ambient:secret@invalid/db'}):
            with self.assertRaises(AccessError):
                postgres.connection_config(load_env(cwd=self.root))

    def test_pg_tls_and_diagnostics(self):
        url = 'postgresql://reader:secret@db.example.invalid/app'
        self.assertEqual(postgres.connection_config({'DATABASE_URL': url})['sslmode'], 'verify-full')
        self.assertEqual(postgres.connection_config({'DATABASE_URL': url+'?sslmode=disable'})['sslmode'], 'disable')
        for suffix in ('?sslmode=require', '?password=secret', '?host=wrong', '?sslmode=disable&sslmode=verify-full'):
            with self.assertRaises(AccessError):
                postgres.connection_config({'DATABASE_URL': url+suffix})
        self.envfile.write_text('DATABASE_URL='+url+'\n')
        result = self.cli(POSTGRES, 'config')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('secret', result.stdout+result.stderr)
        self.assertNotIn('reader', result.stdout)

    def test_pg_writes_rejected_before_connection(self):
        for sql in ('UPDATE example SET value=1', 'SET TRANSACTION READ WRITE', 'COMMIT', ''):
            result = self.cli(POSTGRES, 'query', '--sql', sql)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('Blocked', result.stderr)
        result = self.cli(POSTGRES, 'query', '--sql', 'SELECT 1', '--allow-write')
        self.assertEqual(result.returncode, 2)

    def test_grafana_explicit_selection_and_url_validation(self):
        env = dict(GRAFANA_INSTANCES='dev,stage', GRAFANA_USERNAME='reader', GRAFANA_PASSWORD='secret',
                   GRAFANA_DEV_URL='https://dev.example.invalid', GRAFANA_STAGE_URL='https://stage.example.invalid')
        with self.assertRaises(AccessError):
            grafana.configuration(env)
        self.assertEqual(grafana.configuration(env, 'stage')['id'], 'stage')
        for url in ('https://u:secret@example.invalid', 'https://example.invalid?token=secret', 'file:///tmp/private'):
            with self.assertRaises(AccessError) as error:
                grafana.configuration(env | {'GRAFANA_STAGE_URL': url}, 'stage')
            self.assertNotIn('secret', str(error.exception))

    def test_evidence_does_not_overwrite_and_is_private(self):
        target = self.local / 'evidence.json'
        write_private(target, 'original')
        with self.assertRaises(AccessError):
            write_private(target, 'replacement')
        self.assertEqual(target.read_text(), 'original')
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_grafana_http_contract(self):
        state = {'mode': 'normal', 'multi': False, 'basic': False, 'seen': []}
        case = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def respond(self, payload, content_type='application/json', status=200, cookie=None):
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                if cookie:
                    self.send_header('Set-Cookie', cookie)
                self.end_headers()
                self.wfile.write((json.dumps(payload) if content_type == 'application/json' else payload).encode())
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
                state['seen'].append((self.path, self.headers.get('Authorization')))
                if self.path == '/grafana/login':
                    case.assertEqual(body['password'], 'fixture-password')
                    self.respond({}, status=302 if state['mode'] == 'redirect' else 200, cookie='grafana_session=fixture-session; Path=/')
                    return
                self.query_response()
            def query_response(self):
                case.assertIn('grafana_session=fixture-session', self.headers.get('Cookie', ''))
                if state['mode'] == 'slow':
                    self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
                    try:
                        for _ in range(60):
                            self.wfile.write(b' '); self.wfile.flush(); time.sleep(0.03)
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                elif state['mode'] == 'html':
                    self.respond('<html>sign in</html>', 'text/html')
                elif state['mode'] == 'malformed':
                    self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b'private_payload_123')
                elif state['mode'] == 'error':
                    self.respond({'results': {'A': {'error': 'private_payload_123', 'status': 400}}})
                else:
                    self.respond({'results': {'A': {'frames': [{'schema': {'fields': [{'name': 'Time', 'type': 'time'}, {'name': 'Line'}]}, 'data': {'values': [[1780000000000], ['request-example completed']]}}]}}})
            def do_GET(self):
                if self.path == '/grafana/api/health':
                    self.respond({'database': 'ok', 'version': 'fixture'})
                elif self.path == '/grafana/api/datasources':
                    self.respond([{'uid': 'logs', 'type': 'loki'}, {'uid': 'metrics', 'type': 'prometheus'}] + ([{'uid': 'other', 'type': 'loki'}] if state['multi'] else []))
                elif '/api/v1/series?' in self.path:
                    self.respond({'status':'success','data':[{'job':'example','exported_source':'cache'}]})
                elif '/api/v1/query' in self.path:
                    if state['mode'] in ('html','malformed'):
                        self.query_response()
                    else:
                        self.respond({'status':'success','data':{'resultType':'vector','result':[{'metric':{'job':'example'},'value':[1780000000,'1']}]}})
                else:
                    self.respond({}, status=404)
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        self.envfile.write_text(f'GRAFANA_URL=http://127.0.0.1:{server.server_port}/grafana\nGRAFANA_USERNAME=fixture-reader\nGRAFANA_PASSWORD=fixture-password\n')
        for args in [('check',), ('logs','--expr','{service_name="example"}'), ('metrics','--expr','up','--instant'), ('metrics','--expr','up'), ('labels','--metric','app_events_total')]:
            result = self.cli(GRAFANA, *args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
            self.assertNotIn('fixture-password', result.stdout+result.stderr)
            self.assertNotIn('fixture-session', result.stdout+result.stderr)
        state['multi'] = True
        self.assertEqual(self.cli(GRAFANA, 'logs','--expr','{}').returncode, 1)
        self.assertEqual(self.cli(GRAFANA, 'logs','--expr','{}','--datasource-uid','logs').returncode, 0)
        state['multi'] = False
        for mode in ('html', 'malformed', 'error'):
            state['mode'] = mode
            result = self.cli(GRAFANA, 'logs','--expr','{}')
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn('private_payload_123', result.stderr)
        state['mode'] = 'redirect'
        self.assertEqual(self.cli(GRAFANA, 'logs','--expr','{}').returncode, 0)
        state['mode'] = 'slow'
        began = time.monotonic()
        result = self.cli(GRAFANA, 'logs','--expr','{}','--timeout-ms','80')
        self.assertEqual(result.returncode, 1)
        self.assertIn('deadline', result.stderr)
        self.assertLess(time.monotonic() - began, 1.6)
        state['mode'] = 'normal'
        with self.envfile.open('a') as stream:
            stream.write('GRAFANA_BASIC_AUTH_USER=ingress\nGRAFANA_BASIC_AUTH_PASSWORD=fixture-ingress\n')
        self.assertEqual(self.cli(GRAFANA, 'logs','--expr','{}').returncode, 0)
        self.assertTrue(state['seen'][-1][1].startswith('Basic '))

    def test_copied_skills_execute_with_isolated_locked_dependencies(self):
        # Neither the repository venv nor consumer package dependencies are needed.
        (self.root / 'pyproject.toml').write_text('[project]\nname="unrelated-consumer"\nversion="0.0.0"\nrequires-python=">=3.12"\ndependencies=["does-not-exist-consumer-package-123"]\n')
        self.envfile.write_text('GRAFANA_URL=https://grafana.example.invalid\nGRAFANA_USERNAME=reader\nGRAFANA_PASSWORD=fixture-secret\nDATABASE_URL=postgresql://reader:fixture-secret@db.example.invalid/example\n')
        for name, entry in [('grafana-access','grafana.py'),('postgresql-access','postgres.py')]:
            destination = self.root / 'installed' / name
            shutil.copytree(ROOT / 'skills' / name, destination)
            result = subprocess.run(['uv', 'run', '--locked', '--offline', str(destination/'scripts'/entry), 'config'], cwd=self.root, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('fixture-secret', result.stdout+result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)

    def test_vendored_common_and_dependency_versions_match(self):
        import tomllib
        self.assertEqual((GRAFANA.parent/'access_common.py').read_bytes(), (POSTGRES.parent/'access_common.py').read_bytes())
        project = tomllib.loads((ROOT/'pyproject.toml').read_text())
        requirements = set(project['project']['dependencies'])
        for script in (GRAFANA,POSTGRES):
            metadata = '\n'.join(line[2:] for line in script.read_text().split('# ///')[1].splitlines()[1:] if line.startswith('# '))
            self.assertTrue(set(tomllib.loads(metadata)['dependencies']) <= requirements)

    @unittest.skipUnless(os.environ.get('SKILLS_TEST_DATABASE_URL'), 'requires disposable PostgreSQL fixture')
    def test_postgres_integration(self):
        url = os.environ['SKILLS_TEST_DATABASE_URL']
        self.envfile.write_text('DATABASE_URL='+url+'\n')
        config = postgres.connection_config({'DATABASE_URL': url})
        with patch.dict(os.environ, {'PGHOSTADDR':'192.0.2.1', 'PGSERVICE':'nonexistent-fixture-service', 'PGSERVICEFILE':'/nonexistent-fixture-file'}):
            self.assertEqual(postgres.read_query(config, 'SELECT 42 AS answer')['rows'][0]['answer'], 42)
            self.assertEqual(os.environ['PGHOSTADDR'], '192.0.2.1')
        with self.assertRaises(Exception) as error:
            postgres.read_query(config, 'CREATE TABLE should_not_exist (id int)')
        self.assertIn('read-only', str(error.exception))
        with self.assertRaises(Exception) as error:
            postgres.read_query(config, 'SELECT 1; SELECT 2')
        self.assertIn('multiple commands', str(error.exception))
        for args in [('query','--sql','SELECT 42 AS answer'), ('check',), ('schema',), ('query','--sql','SELECT 1','--explain')]:
            result=self.cli(POSTGRES,*args)
            self.assertEqual(result.returncode,0,result.stderr)
        result = self.cli(POSTGRES, 'query', '--sql', "SELECT 'private_payload_123'::int")
        self.assertEqual(result.returncode,1)
        self.assertNotIn('private_payload_123',result.stderr)

if __name__ == '__main__':
    unittest.main()
