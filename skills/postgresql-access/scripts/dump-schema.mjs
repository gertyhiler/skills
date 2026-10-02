#!/usr/bin/env node

import { writeFile } from "node:fs/promises";
import process from "node:process";
import { pathToFileURL } from "node:url";
import { loadPostgresRuntime } from "./postgres-env.mjs";
import { runReadOnlyQuery } from "./postgres-client.mjs";

const CATALOG_SQL = `
WITH tables AS (
  SELECT
    n.nspname AS schema_name,
    c.relname AS table_name,
    c.relkind AS relkind
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND c.relkind IN ('r', 'p', 'v', 'm', 'f')
)
SELECT
  t.schema_name,
  t.table_name,
  CASE t.relkind
    WHEN 'r' THEN 'table'
    WHEN 'p' THEN 'partitioned table'
    WHEN 'v' THEN 'view'
    WHEN 'm' THEN 'materialized view'
    WHEN 'f' THEN 'foreign table'
    ELSE t.relkind::text
  END AS object_type,
  a.attname AS column_name,
  pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
  a.attnotnull AS not_null
FROM tables t
JOIN pg_class c ON c.relname = t.table_name
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = t.schema_name
JOIN pg_attribute a ON a.attrelid = c.oid
WHERE a.attnum > 0
  AND NOT a.attisdropped
ORDER BY t.schema_name, t.table_name, a.attnum
`.trim();

function parseArgs(argv) {
  const args = {
    envFile: undefined,
    catalog: false,
    output: undefined,
    help: false,
    ddl: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--env-file") {
      args.envFile = argv[index + 1];
      index += 1;
    } else if (token === "--catalog") {
      args.catalog = true;
    } else if (token === "--output") {
      args.output = argv[index + 1];
      index += 1;
    } else if (token === "--ddl") {
      args.ddl = true;
    } else if (token === "--help" || token === "-h") {
      args.help = true;
    }
  }

  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: dump-schema.mjs [--env-file PATH] [--catalog] [--output FILE]

Node-only schema inspection supports catalog snapshots only.`);
    process.exit(0);
  }

  if (args.ddl) {
    console.error(
      "--ddl has been removed. Node-only PostgreSQL access supports --catalog only.",
    );
    process.exit(1);
  }

  try {
    const runtime = await loadPostgresRuntime({
      explicitEnvFile: args.envFile,
    });
    const result = await runReadOnlyQuery(runtime, CATALOG_SQL);
    const output = `${JSON.stringify(result.rows, null, 2)}\n`;

    if (args.output) {
      await writeFile(args.output, output, { encoding: "utf8", flag: "wx", mode: 0o600 });
    } else {
      process.stdout.write(output);
    }
  } catch (error) {
    console.error("PostgreSQL helper failed. Check the selected env file, consumer pg dependency and access contract; raw errors are suppressed.");
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
