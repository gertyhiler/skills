import { readFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { parseEnv } from "node:util";

export function consumerRoot(cwd = process.cwd()) {
  const result = spawnSync("git", ["rev-parse", "--show-toplevel"], {
    cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"],
  });
  return result.status === 0 ? result.stdout.trim() : path.resolve(cwd);
}

export async function readProjectEnv(explicit, cwd = process.cwd()) {
  const root = consumerRoot(cwd);
  const envFilePath = explicit
    ? path.resolve(cwd, explicit)
    : path.join(root, ".agents/local/.env.agents");
  let raw;
  try { raw = await readFile(envFilePath, "utf8"); }
  catch { throw new Error("Cannot read agent env file. Use --env-file PATH or configure .agents/local/.env.agents in the consumer checkout."); }
  // No shell evaluation, interpolation, ambient credential merging or fallback.
  return { consumerRoot: root, envFilePath, env: parseEnv(raw) };
}
