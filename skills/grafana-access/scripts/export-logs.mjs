#!/usr/bin/env node

import { writeFile } from "node:fs/promises";
import process from "node:process";
import { pathToFileURL } from "node:url";

import { GrafanaClient } from "./grafana-client.mjs";
import {
  assertNodeVersion,
  maybeLoadEnvForArgs,
  redactUrl,
  resolveInstance,
} from "./grafana-env.mjs";
import { parseQueryArgs } from "./query-logs.mjs";

assertNodeVersion();

function parseExportArgs(argv) {
  const args = parseQueryArgs(argv);
  args.output = undefined;
  args.format = "ndjson";

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--output") {
      args.output = argv[index + 1];
      index += 1;
    } else if (token === "--format") {
      args.format = argv[index + 1];
      index += 1;
    }
  }

  return args;
}

function serializeExport(payload, format) {
  if (format === "json") {
    return `${JSON.stringify(payload, null, 2)}\n`;
  }

  if (format === "ndjson") {
    return (
      payload.entries.map((entry) => JSON.stringify(entry)).join("\n") + "\n"
    );
  }

  if (format === "text") {
    return (
      payload.entries
        .map((entry) => {
          const prefix = entry.timestamp ? `[${entry.timestamp}] ` : "";
          return `${prefix}${entry.line}`;
        })
        .join("\n") + "\n"
    );
  }

  throw new Error(`Unsupported format "${format}". Use json, ndjson, or text.`);
}

async function main() {
  const args = parseExportArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: export-logs.mjs --expr '{service_name="example-api"} |= "error"' --output /tmp/logs.ndjson [--format ndjson|json|text] [--instance ID] [--from now-1h] [--to now] [--limit 1000] [--json]

Runs a LogQL query and writes results to a file.

Choose labels from the consumer project observability runbook.`);
    process.exit(0);
  }

  if (!args.expr) {
    console.error("--expr is required");
    process.exit(1);
  }

  if (!args.output) {
    console.error("--output is required");
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

    const content = serializeExport(payload, args.format);
    await writeFile(args.output, content, { encoding: "utf8", flag: "wx", mode: 0o600 });

    const summary = {
      output: args.output,
      format: args.format,
      count: payload.count,
      instance: payload.instance,
      query: payload.query,
    };

    console.log(JSON.stringify(summary, null, args.json ? 2 : 0));
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
