#!/usr/bin/env node

import { readProjectEnv } from "./project-env.mjs";
import process from "node:process";
import { pathToFileURL } from "node:url";

const ALIAS_MAP = [
  ["GRAFANA_USER", "GRAFANA_USERNAME"],
  ["GRAFANA_PASS", "GRAFANA_PASSWORD"],
  ["GRAFANA_LOGIN_PASSWORD", "GRAFANA_PASSWORD"],
  ["GRAFANA_BASIC_USER", "GRAFANA_BASIC_AUTH_USER"],
];

export function assertNodeVersion(minMajor = 22) {
  const major = Number.parseInt(process.versions.node.split(".")[0], 10);
  if (Number.isNaN(major) || major < minMajor) {
    throw new Error(
      `Node.js ${minMajor}+ is required. Current: ${process.versions.node}`,
    );
  }
}

export function normalizeEnv(source = process.env) {
  const env = { ...source };

  for (const [alias, canonical] of ALIAS_MAP) {
    if (!env[canonical] && env[alias]) {
      env[canonical] = env[alias];
    }
  }

  return env;
}

export { parseEnv as parseEnvContent } from "node:util";

export async function loadEnvForArgs(args, cwd = process.cwd()) {
  const runtime = await readProjectEnv(args.envFile, cwd);
  for (const key of Object.keys(process.env)) {
    if (key.startsWith("GRAFANA_")) delete process.env[key];
  }
  for (const [key, value] of Object.entries(runtime.env)) {
    if (key.startsWith("GRAFANA_")) process.env[key] = value;
  }
  return { path: runtime.envFilePath };
}
export const maybeLoadEnvForArgs = loadEnvForArgs;

export function instanceKey(instanceId) {
  return instanceId.toUpperCase().replace(/[^A-Z0-9]/g, "_");
}

export function listInstances(env = process.env) {
  const normalized = normalizeEnv(env);

  if (normalized.GRAFANA_INSTANCES?.trim()) {
    return normalized.GRAFANA_INSTANCES.split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  if (normalized.GRAFANA_URL?.trim()) {
    return ["default"];
  }

  return [];
}

export function resolveInstance(env = process.env, instanceId) {
  const normalized = normalizeEnv(env);
  const instances = listInstances(normalized);

  if (instances.length === 0) {
    throw new Error(
      "No Grafana instances configured. Set GRAFANA_INSTANCES or GRAFANA_URL in .agents/local/.env.agents.",
    );
  }

  if (!instanceId && instances.length > 1) throw new Error("Select --instance explicitly when multiple instances are configured.");
  const id = instanceId ?? instances[0];
  if (!instances.includes(id)) {
    throw new Error(
      `Unknown instance "${id}". Available: ${instances.join(", ")}`,
    );
  }

  const key = instanceKey(id);
  const url =
    id === "default"
      ? normalized.GRAFANA_URL
      : normalized[`GRAFANA_${key}_URL`];

  const basicAuthPassword =
    id === "default"
      ? normalized.GRAFANA_BASIC_AUTH_PASSWORD
      : normalized[`GRAFANA_${key}_BASIC_AUTH_PASSWORD`];

  const config = {
    id,
    url: url?.trim().replace(/\/+$/, "") ?? "",
    username: normalized.GRAFANA_USERNAME?.trim() ?? "",
    password: normalized.GRAFANA_PASSWORD ?? "",
    basicAuthUser: normalized.GRAFANA_BASIC_AUTH_USER?.trim() ?? "",
    basicAuthPassword: basicAuthPassword ?? "",
  };

  validateInstanceConfig(config);
  return config;
}

export function validateInstanceConfig(config) {
  const missing = [];

  if (!config.url) missing.push("url");
  if (!config.username) missing.push("GRAFANA_USERNAME");
  if (!config.password) missing.push("GRAFANA_PASSWORD");
  if (Boolean(config.basicAuthUser) !== Boolean(config.basicAuthPassword)) missing.push("both ingress basic auth fields");

  if (missing.length > 0) {
    throw new Error(
      `Instance "${config.id}" is missing required config: ${missing.join(", ")}`,
    );
  }

  try {
    const parsed = new URL(config.url);
    if (!["http:", "https:"].includes(parsed.protocol)) {
      throw new Error("URL must use http or https");
    }
    if (parsed.username || parsed.password || parsed.search || parsed.hash) {
      throw new Error("URL must not include credentials, query or fragment");
    }
  } catch (error) {
    throw new Error(
      `Instance "${config.id}" has invalid base URL; use http(s) without credentials, query or fragment.`,
    );
  }
}

export function redactUrl(rawUrl) {
  try {
    const parsed = new URL(rawUrl);
    if (parsed.password) parsed.password = "***";
    if (parsed.username) parsed.username = "***";
    parsed.search = ""; parsed.hash = "";
    return parsed.toString();
  } catch {
    return "<invalid-url>";
  }
}

export function summarizeEnv(env = process.env, instanceId) {
  const instances = listInstances(env);
  const selected = resolveInstance(env, instanceId);

  return {
    instances,
    selected: {
      id: selected.id,
      url: redactUrl(selected.url),
      hasUsername: Boolean(selected.username),
      hasBasicAuthUser: Boolean(selected.basicAuthUser),
      hasPassword: Boolean(selected.password),
      hasBasicAuthPassword: Boolean(selected.basicAuthPassword),
    },
  };
}

export function parseCommonArgs(argv) {
  const args = {
    json: false,
    instance: undefined,
    envFile: undefined,
    help: false,
    timeoutMs: undefined,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--json") {
      args.json = true;
    } else if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--instance") {
      args.instance = argv[index + 1];
      index += 1;
    } else if (token === "--env-file") {
      args.envFile = argv[index + 1];
      index += 1;
    } else if (token === "--timeout-ms") {
      args.timeoutMs = Number.parseInt(argv[index + 1], 10);
      index += 1;
    }
  }

  return args;
}

async function main() {
  assertNodeVersion();
  const args = parseCommonArgs(process.argv.slice(2));

  if (args.help) {
    console.log(`Usage: grafana-env.mjs [--instance ID] [--json]

Validates Grafana env from the current process environment.
Pass --env-file PATH to override the consumer checkout configuration.`);
    process.exit(0);
  }

  try {
    await maybeLoadEnvForArgs(args);
    const summary = summarizeEnv(process.env, args.instance);
    if (args.json) {
      console.log(JSON.stringify(summary, null, 2));
    } else {
      for (const [key, value] of Object.entries(summary)) {
        console.log(`${key}=${JSON.stringify(value)}`);
      }
    }
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  main();
}
