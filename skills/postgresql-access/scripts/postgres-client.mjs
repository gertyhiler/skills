#!/usr/bin/env node

import { resolveClientConfig, resolvePgModule } from "./postgres-env.mjs";

export async function withPostgresClient(runtime, callback) {
  const { Client } = resolvePgModule(runtime.consumerRoot);
  const client = new Client(resolveClientConfig(runtime.env));
  try {
    await client.connect();
    return await callback(client);
  } finally {
    await client.end().catch(() => {});
  }
}

export async function runReadOnlyQuery(runtime, sql) {
  return withPostgresClient(runtime, async (client) => {
    await client.query("BEGIN READ ONLY");

    try {
      const result = await client.query({ text: sql, queryMode: "extended" });
      await client.query("ROLLBACK");
      return result;
    } catch (error) {
      await client.query("ROLLBACK").catch(() => {});
      throw error;
    }
  });
}
