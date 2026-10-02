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
import { parseTimeToUnixSeconds } from "./time-utils.mjs";

assertNodeVersion();

function usage() {
  return `Usage:
  inspect-metric.mjs --metric app_events_total [--instance prod] [--from now-24h] [--to now] [--json]
  inspect-metric.mjs --match 'app_events_total{route_group="example"}' [--json]

Inspects Prometheus series labels for a metric through Grafana.

Options:
  --metric NAME          Metric name. Builds {__name__="NAME"} selector.
  --match SELECTOR       Prometheus series selector. Overrides --metric.
  --from TIME            Series lookup start. Default: now-24h.
  --to TIME              Series lookup end. Default: now.
  --limit NUMBER         Max sample series and label values. Default: 20.
  --prometheus-uid UID   Use a specific Prometheus datasource UID.
  --instance ID          Grafana instance id from .agents/local/.env.agents.
  --timeout-ms NUMBER    HTTP timeout. Default: 30000.
  --json                 Pretty-print JSON output.
  --help, -h             Show this help.

Use this before writing PromQL against a metric you have not queried recently.`;
}

function parseInspectArgs(argv) {
  const common = parseCommonArgs(argv);
  const args = {
    ...common,
    metric: undefined,
    match: undefined,
    from: "now-24h",
    to: "now",
    limit: 20,
    timeoutMs: 30_000,
    prometheusUid: undefined,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--metric") {
      args.metric = argv[index + 1];
      index += 1;
    } else if (token === "--match") {
      args.match = argv[index + 1];
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
    } else if (token === "--prometheus-uid") {
      args.prometheusUid = argv[index + 1];
      index += 1;
    }
  }

  return args;
}

function selectorForArgs(args) {
  if (args.match) return args.match;
  if (args.metric) return `{__name__="${args.metric}"}`;
  throw new Error("--metric or --match is required");
}

function summarizeSeries(series, limit) {
  const labelValues = new Map();

  for (const item of series) {
    for (const [key, value] of Object.entries(item)) {
      if (!labelValues.has(key)) labelValues.set(key, new Set());
      labelValues.get(key).add(value);
    }
  }

  const labels = [...labelValues.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, values]) => ({
      key,
      count: values.size,
      values: [...values].sort().slice(0, limit),
    }));

  const exportedLabels = labels
    .filter((item) => item.key.startsWith("exported_"))
    .map((item) => item.key);

  return {
    seriesCount: series.length,
    labelKeys: labels.map((item) => item.key),
    labels,
    sampleSeries: series.slice(0, limit),
    hints: buildHints(labels, exportedLabels),
  };
}

function buildHints(labels, exportedLabels) {
  const hints = [];
  const labelKeys = new Set(labels.map((item) => item.key));
  const sourceLabel = labels.find((item) => item.key === "source");

  if (exportedLabels.length > 0) {
    hints.push(
      `Found exported labels: ${exportedLabels.join(", ")}. Prometheus may have renamed colliding app labels.`,
    );
  }

  if (labelKeys.has("exported_source")) {
    hints.push(
      sourceLabel?.values?.includes("otel")
        ? 'Inspect exported_source values separately from the source target label.'
        : 'Check exported_source values against the project metric contract.',
    );
  }

  if (labelKeys.has("service_name")) {
    hints.push('Use service_name="..." for service filtering.');
  }

  return hints;
}

async function main() {
  const args = parseInspectArgs(process.argv.slice(2));

  if (args.help) {
    console.log(usage());
    process.exit(0);
  }

  if (!Number.isFinite(args.limit) || args.limit <= 0) {
    console.error("--limit must be a positive integer");
    process.exit(1);
  }

  try {
    await maybeLoadEnvForArgs(args);
    const config = resolveInstance(process.env, args.instance);
    const client = new GrafanaClient(config, { timeoutMs: args.timeoutMs });
    const selector = selectorForArgs(args);
    const result = await client.metricSeries({
      match: selector,
      start: parseTimeToUnixSeconds(args.from),
      end: parseTimeToUnixSeconds(args.to),
      prometheusUid: args.prometheusUid,
    });
    const summary = summarizeSeries(result.series, args.limit);

    const payload = {
      instance: config.id,
      url: redactUrl(config.url),
      query: {
        match: result.match,
        start: result.start,
        end: result.end,
        datasourceUid: result.datasourceUid,
      },
      ...summary,
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

export { parseInspectArgs, summarizeSeries };
