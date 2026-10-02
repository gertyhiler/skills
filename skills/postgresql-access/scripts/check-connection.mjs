#!/usr/bin/env node

import process from "node:process";
import { pathToFileURL } from "node:url";
import {
  loadPostgresRuntime,
  redactDsn,
} from "./postgres-env.mjs";
import { withPostgresClient } from "./postgres-client.mjs";

const CHECK_CONNECTION_SQL = `
SELECT
  current_database() AS current_database,
  current_user AS current_user,
  current_setting('server_version') AS server_version
`.trim();

function parseArgs(argv) {
  const args = {
    envFile: undefined,
    json: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--env-file") {
      args.envFile = argv[index + 1];
      index += 1;
    } else if (token === "--json") {
      args.json = true;
    } else if (token === "--help" || token === "-h") {
      args.help = true;
    }
  }

  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: check-connection.mjs [--env-file PATH] [--json]

Verifies PostgreSQL connectivity through the Node pg client.`);
    process.exit(0);
  }

  try {
    const runtime = await loadPostgresRuntime({
      explicitEnvFile: args.envFile,
    });
    const row = await withPostgresClient(runtime, async (client) => {
      const result = await client.query(CHECK_CONNECTION_SQL);
      return result.rows[0] ?? {};
    });
    const payload = {
      ...row,
      runner: "node_pg",
      consumerRoot: runtime.consumerRoot,
      envFilePath: runtime.envFilePath,
      redactedDsn: redactDsn(runtime.connection.dsn),
    };

    if (args.json) {
      console.log(JSON.stringify(payload, null, 2));
    } else {
      console.log(JSON.stringify(payload, null, 2));
    }
  } catch (error) {
    console.error("PostgreSQL helper failed. Check the selected env file, consumer pg dependency and access contract; raw errors are suppressed.");
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
