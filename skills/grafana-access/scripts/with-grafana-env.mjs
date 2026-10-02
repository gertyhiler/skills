#!/usr/bin/env node
import { spawn } from "node:child_process";
import { readProjectEnv } from "./project-env.mjs";

const argv = process.argv.slice(2);
if (argv.includes("--help")) {
  console.log("Usage: with-grafana-env.mjs [--env-file PATH] -- node SKILL_SCRIPT [ARGS]");
} else {
  try {
    const split = argv.indexOf("--");
    const prefix = argv.slice(0, split);
    if (split < 0 || !argv[split + 1] || (prefix.length && (prefix.length !== 2 || prefix[0] !== "--env-file"))) throw new Error("Invalid wrapper arguments; use --help.");
    const runtime = await readProjectEnv(prefix[1]);
    const child = spawn(argv[split + 1], [...argv.slice(split + 2), "--env-file", runtime.envFilePath], { stdio: "inherit" });
    child.on("error", () => { console.error("Could not start Grafana helper."); process.exitCode = 1; });
    child.on("exit", (code) => { process.exitCode = code ?? 1; });
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
