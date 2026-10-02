#!/usr/bin/env node

import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import { readProjectEnv } from "./project-env.mjs";

const DSN_KEYS = [
  "DATABASE_URL",
  "DATABASE_DSN",
  "DB_DSN",
  "DSN",
  "DB",
  "POSTGRES_DSN",
  "POSTGRES_URL",
  "PGURL",
];

export function assertNodeVersion(minMajor = 22) {
  const major = Number.parseInt(process.versions.node.split(".")[0], 10);
  if (Number.isNaN(major) || major < minMajor) {
    throw new Error(
      `Node.js ${minMajor}+ is required. Current: ${process.versions.node}`,
    );
  }
}

export function normalizePostgresEnv(source = process.env) {
  const env = { ...source };

  if (!env.DATABASE_URL) {
    const dsnKey = DSN_KEYS.find((key) => env[key]);
    if (dsnKey) {
      env.DATABASE_URL = env[dsnKey];
    }
  }

  return env;
}

export function resolveConnectionSpec(env = process.env) {
  const normalizedEnv = normalizePostgresEnv(env);
  const dsnKey = DSN_KEYS.find((key) => normalizedEnv[key]);
  const dsn = dsnKey ? normalizedEnv[dsnKey] : undefined;
  if (!dsn) throw new Error("Set DATABASE_URL in the selected env file.");
  return { dsnKey, dsn };
}

export function redactDsn(dsn) {
  if (!dsn) {
    return undefined;
  }

  try {
    const parsed = new URL(dsn);
    if (parsed.password) {
      parsed.password = "***";
    }
    if (parsed.username) {
      parsed.username = parsed.username ? "***" : parsed.username;
    }
    parsed.search = ""; parsed.hash = "";
    return parsed.toString();
  } catch {
    return "<redaction-failed>";
  }
}

export function resolveClientConfig(env = {}) {
  const connection = resolveConnectionSpec(env);
  if (!connection.dsn) throw new Error("Set DATABASE_URL in the selected env file; ambient PG variables are not used.");
  let url;
  try { url = new URL(connection.dsn); } catch { throw new Error("Invalid PostgreSQL URL."); }
  if (!["postgres:", "postgresql:"].includes(url.protocol) || !url.hostname || !url.username || !url.password || !url.pathname.slice(1)) throw new Error("PostgreSQL URL must contain scheme, host, database and credentials.");
  const mode = url.searchParams.get("sslmode") || env.PGSSLMODE || "verify-full";
  if (!["verify-full", "disable"].includes(mode)) throw new Error("Use sslmode=verify-full, or disable only for a documented local connection/tunnel.");
  if ([...url.searchParams.keys()].some(key => !["sslmode", "application_name"].includes(key))) throw new Error("Unsupported PostgreSQL URL parameter; use the project-specific adapter.");
  url.searchParams.delete("sslmode");
  return {
    connectionString: url.toString(),
    ssl: mode === "disable" ? false : { rejectUnauthorized: true },
    connectionTimeoutMillis: 10000,
    statement_timeout: 15000,
    query_timeout: 20000,
  };
}

export function resolvePgModule(consumerRoot) {
  const requireFromConsumer = createRequire(
    path.join(consumerRoot, "__postgresql_access_resolver__.cjs"),
  );

  try {
    const pgPath = requireFromConsumer.resolve("pg");
    const pg = requireFromConsumer("pg");
    if (!pg?.Client) {
      throw new Error("Resolved module does not expose Client.");
    }
    return {
      Client: pg.Client,
      pgPath,
    };
  } catch {
    throw new Error(
      `Could not resolve consumer project dependency "pg" from ${consumerRoot}. Install pg in the consumer project and rerun.`,
    );
  }
}

export async function loadPostgresRuntime({
  cwd = process.cwd(),
  explicitEnvFile,
} = {}) {
  assertNodeVersion();
  const runtime = await readProjectEnv(explicitEnvFile, cwd);
  const env = normalizePostgresEnv(runtime.env);
  const connection = resolveConnectionSpec(env);
  resolveClientConfig(env);

  return {
    ...runtime,
    env,
    connection,
  };
}
