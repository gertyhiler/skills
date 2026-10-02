#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import process from "node:process";
import { pathToFileURL } from "node:url";
import { loadPostgresRuntime } from "./postgres-env.mjs";
import { runReadOnlyQuery } from "./postgres-client.mjs";

const WRITE_PATTERN = /\b(insert|update|delete|merge|alter|drop|create|truncate|grant|revoke|vacuum|call|do|copy|comment|reindex|cluster|refresh|analyze|begin|start\s+transaction|commit|rollback|savepoint|release|lock|set|reset|discard|end|prepare|execute|deallocate)\b/i;

function stripTrailingSemicolon(sql) {
  return sql.trim().replace(/;+\s*$/u, "");
}

export function looksWriteCapable(sql) {
  return WRITE_PATTERN.test(sql);
}

export async function readSql(sql, filePath) {
  if (Boolean(sql) === Boolean(filePath)) {
    throw new Error("Provide exactly one of --sql or --file.");
  }

  if (sql) {
    return sql;
  }

  return readFile(filePath, "utf8");
}

export function wrapExplain(sql) {
  return `EXPLAIN ${stripTrailingSemicolon(sql)};`;
}

function parseArgs(argv) {
  const args = {
    envFile: undefined,
    sql: undefined,
    file: undefined,
    allowWrite: false,
    explain: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--env-file") {
      args.envFile = argv[index + 1];
      index += 1;
    } else if (token === "--sql") {
      args.sql = argv[index + 1];
      index += 1;
    } else if (token === "--file") {
      args.file = argv[index + 1];
      index += 1;
    } else if (token === "--allow-write") {
      args.allowWrite = true;
    } else if (token === "--explain") {
      args.explain = true;
    } else if (token === "--help" || token === "-h") {
      args.help = true;
    }
  }

  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: run-query.mjs [--env-file PATH] (--sql "SELECT 1" | --file query.sql) [--explain]

Runs SQL through the Node pg client and blocks write-capable queries by default.`);
    process.exit(0);
  }

  try {
    const sql = await readSql(args.sql, args.file);
    const isWrite = looksWriteCapable(sql);

    if (isWrite || args.allowWrite) {
      console.error(
        "Blocked write-capable SQL. This investigation helper is read-only; use the project mutation workflow.",
      );
      process.exit(2);
    }

    if (args.explain && isWrite) {
      console.error(
        "EXPLAIN is only supported for read-only SQL in this helper.",
      );
      process.exit(1);
    }

    const runtime = await loadPostgresRuntime({
      explicitEnvFile: args.envFile,
    });

    const result = args.explain
      ? await runReadOnlyQuery(runtime, wrapExplain(sql))
      : await runReadOnlyQuery(runtime, sql);

    process.stdout.write(
      `${JSON.stringify(
        {
          rowCount: result.rowCount,
          rows: result.rows,
        },
        null,
        2,
      )}\n`,
    );
  } catch (error) {
    console.error("PostgreSQL query failed. Check selected configuration, connection, schema and query; raw server errors are suppressed.");
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
