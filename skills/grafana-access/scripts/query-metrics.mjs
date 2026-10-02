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
import {
  normalizePrometheusStep,
  parseTimeToUnixSeconds,
} from "./time-utils.mjs";

assertNodeVersion();

function usage() {
  return `Usage:
  query-metrics.mjs --expr 'up' [--instance prod] [--range --from now-1h --to now --step 60s] [--json]
  query-metrics.mjs --expr 'up' --instant [--time now] [--json]

Runs a PromQL query through the Grafana Prometheus datasource.

Options:
  --expr TEXT             PromQL expression. Required.
  --range                Run a range query. Default mode.
  --instant              Run an instant query.
  --from TIME            Range start. Default: now-1h.
  --to TIME              Range end. Default: now.
  --step DURATION        Range step. Default: 60s.
  --time TIME            Instant query time. Default: now.
  --prometheus-uid UID   Use a specific Prometheus datasource UID.
  --instance ID          Grafana instance id from .agents/local/.env.agents.
  --timeout-ms NUMBER    HTTP timeout. Default: 30000.
  --json                 Pretty-print JSON output.
  --help, -h             Show this help.

TIME accepts now, now-1h, Unix seconds, or an ISO timestamp.`;
}

export function parseMetricsArgs(argv) {
  const common = parseCommonArgs(argv);
  const args = {
    ...common,
    expr: undefined,
    mode: "range",
    from: "now-1h",
    to: "now",
    step: "60s",
    time: "now",
    timeoutMs: 30_000,
    prometheusUid: undefined,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--expr") {
      args.expr = argv[index + 1];
      index += 1;
    } else if (token === "--range") {
      args.mode = "range";
    } else if (token === "--instant") {
      args.mode = "instant";
    } else if (token === "--from") {
      args.from = argv[index + 1];
      index += 1;
    } else if (token === "--to") {
      args.to = argv[index + 1];
      index += 1;
    } else if (token === "--step") {
      args.step = argv[index + 1];
      index += 1;
    } else if (token === "--time") {
      args.time = argv[index + 1];
      index += 1;
    } else if (token === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[index + 1], 10);
      index += 1;
    } else if (token === "--prometheus-uid") {
      args.prometheusUid = argv[index + 1];
      index += 1;
    }
  }

  return args;
}

async function main() {
  const args = parseMetricsArgs(process.argv.slice(2));

  if (args.help) {
    console.log(usage());
    process.exit(0);
  }

  if (!args.expr) {
    console.error("--expr is required");
    process.exit(1);
  }

  if (!Number.isFinite(args.timeoutMs) || args.timeoutMs <= 0) {
    console.error("--timeout-ms must be a positive integer");
    process.exit(1);
  }

  try {
    await maybeLoadEnvForArgs(args);
    const config = resolveInstance(process.env, args.instance);
    const client = new GrafanaClient(config, { timeoutMs: args.timeoutMs });
    const result =
      args.mode === "instant"
        ? await client.queryMetricsInstant({
            expr: args.expr,
            time: parseTimeToUnixSeconds(args.time),
            prometheusUid: args.prometheusUid,
          })
        : await client.queryMetricsRange({
            expr: args.expr,
            start: parseTimeToUnixSeconds(args.from),
            end: parseTimeToUnixSeconds(args.to),
            step: normalizePrometheusStep(args.step),
            prometheusUid: args.prometheusUid,
          });

    const payload = {
      instance: config.id,
      url: redactUrl(config.url),
      query: {
        mode: args.mode,
        expr: result.expr,
        datasourceUid: result.datasourceUid,
        ...(args.mode === "instant"
          ? { time: result.time }
          : { start: result.start, end: result.end, step: result.step }),
      },
      resultType: result.resultType,
      count: result.result.length,
      result: result.result,
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
