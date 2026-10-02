#!/usr/bin/env node

import process from "node:process";
import { pathToFileURL } from "node:url";

import { GrafanaClient } from "./grafana-client.mjs";
import {
  assertNodeVersion,
  maybeLoadEnvForArgs,
  parseCommonArgs,
  redactUrl,
  resolveInstance,
} from "./grafana-env.mjs";

assertNodeVersion();

function parseQueryArgs(argv) {
  const common = parseCommonArgs(argv);
  const args = {
    ...common,
    expr: undefined,
    from: "now-1h",
    to: "now",
    limit: 1000,
    timeoutMs: 30_000,
    lokiUid: undefined,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--expr") {
      args.expr = argv[index + 1];
      index += 1;
    } else if (token === "--from") {
      args.from = argv[index + 1];
      index += 1;
    } else if (token === "--to") {
      args.to = argv[index + 1];
      index += 1;
    } else if (token === "--limit") {
      args.limit = Number.parseInt(argv[index + 1], 10);
      index += 1;
    } else if (token === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[index + 1], 10);
      index += 1;
    } else if (token === "--loki-uid") {
      args.lokiUid = argv[index + 1];
      index += 1;
    }
  }

  return args;
}

async function main() {
  const args = parseQueryArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: query-logs.mjs --expr '{service_name="example-api"} |= "error"' [--instance ID] [--from now-1h] [--to now] [--limit 1000] [--json]

Runs a LogQL range query through Grafana and prints normalized log entries.

Choose labels from the consumer project observability runbook.`);
    process.exit(0);
  }

  if (!args.expr) {
    console.error("--expr is required");
    process.exit(1);
  }

  if (!Number.isFinite(args.limit) || args.limit <= 0) {
    console.error("--limit must be a positive integer");
    process.exit(1);
  }

  try {
    await maybeLoadEnvForArgs(args);
    const config = resolveInstance(process.env, args.instance);
    const client = new GrafanaClient(config, { timeoutMs: args.timeoutMs });
    const result = await client.queryLogs({
      expr: args.expr,
      from: args.from,
      to: args.to,
      limit: args.limit,
      lokiUid: args.lokiUid,
    });

    const payload = {
      instance: config.id,
      url: redactUrl(config.url),
      query: {
        expr: result.expr,
        from: result.from,
        to: result.to,
        limit: result.limit,
        datasourceUid: result.datasourceUid,
      },
      count: result.entries.length,
      entries: result.entries,
    };

    console.log(JSON.stringify(payload, null, args.json ? 2 : 0));
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}

export { parseQueryArgs };
