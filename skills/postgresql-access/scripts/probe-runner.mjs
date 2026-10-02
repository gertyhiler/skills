#!/usr/bin/env node

import process from "node:process";
import { pathToFileURL } from "node:url";
import {
  loadPostgresRuntime,
  redactDsn,
  resolvePgModule,
} from "./postgres-env.mjs";

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
    console.log(`Usage: probe-runner.mjs [--env-file PATH] [--json]

Validates env loading and confirms that pg resolves from the consumer project.`);
    process.exit(0);
  }

  try {
    const runtime = await loadPostgresRuntime({
      explicitEnvFile: args.envFile,
    });
    const { pgPath } = resolvePgModule(runtime.consumerRoot);
    const payload = {
      selected: "node_pg",
      consumerRoot: runtime.consumerRoot,
      envFilePath: runtime.envFilePath,
      dsnKey: runtime.connection.dsnKey,
      redactedDsn: redactDsn(runtime.connection.dsn),
      pgPath,
      nodeVersion: process.versions.node,
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
