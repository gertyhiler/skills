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

async function main() {
  const args = parseCommonArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: check-connection.mjs [--instance ID] [--json] [--timeout-ms 30000]

Checks Grafana health, login, Loki datasource availability, and Prometheus datasource availability.`);
    process.exit(0);
  }

  try {
    await maybeLoadEnvForArgs(args);
    const config = resolveInstance(process.env, args.instance);
    const client = new GrafanaClient(config, { timeoutMs: args.timeoutMs });

    const health = await client.health();
    if (!health.ok) {
      throw new Error(
        `Grafana health check failed (${health.status}). Ingress basic auth may be wrong.`,
      );
    }

    const login = await client.login();
    const loki = await client.findLokiDatasource();
    const prometheus = await client.findPrometheusDatasource();

    const payload = {
      instance: config.id,
      url: redactUrl(config.url),
      health,
      login,
      loki,
      prometheus,
    };

    if (args.json) {
      console.log(JSON.stringify(payload, null, 2));
    } else {
      console.log(JSON.stringify(payload, null, 2));
    }
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
