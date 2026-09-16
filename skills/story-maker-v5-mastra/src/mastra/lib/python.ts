import { execFile, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { env, SKILL_ROOT } from "../config.js";

export interface PythonResult {
  code: number;
  stdout: string;
  stderr: string;
}

/** Run a skill script under the skill root. Does not throw on nonzero exit —
 * callers inspect `code` (validators signal failure via exit 1). */
export function runPython(
  script: string,
  args: string[],
  timeoutMs = 10 * 60 * 1000,
): Promise<PythonResult> {
  return new Promise((resolve, reject) => {
    execFile(
      env.pythonBin,
      [script, ...args],
      { cwd: SKILL_ROOT, timeout: timeoutMs, maxBuffer: 64 * 1024 * 1024 },
      (error, stdout, stderr) => {
        if (error && typeof error.code !== "number") {
          reject(new Error(`${script} failed to run: ${error.message}\n${stderr}`));
          return;
        }
        resolve({
          code: typeof error?.code === "number" ? error.code : 0,
          stdout: String(stdout),
          stderr: String(stderr),
        });
      },
    );
  });
}

export function mustRun(script: string, args: string[], timeoutMs?: number): Promise<PythonResult> {
  return runPython(script, args, timeoutMs).then((r) => {
    if (r.code !== 0) {
      throw new Error(`${script} exited ${r.code}:\n${r.stderr || r.stdout}`);
    }
    return r;
  });
}

/**
 * Validate an artifact with scripts/validate.py. Returns the parsed
 * <artifact>.validation.json ({ ok, errors, warnings }).
 */
export async function validateArtifact(
  artifactPath: string,
  schema: string,
  extraArgs: string[] = [],
): Promise<{ ok: boolean; errors: string[]; warnings: string[] }> {
  const res = await runPython("scripts/validate.py", [
    artifactPath,
    "--schema",
    schema,
    ...extraArgs,
  ]);
  const validationPath = `${artifactPath}.validation.json`;
  if (fs.existsSync(validationPath)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(validationPath, "utf8"));
      return {
        ok: Boolean(parsed.ok),
        errors: (parsed.errors ?? []).map(String),
        warnings: (parsed.warnings ?? []).map(String),
      };
    } catch {
      // fall through to exit-code verdict
    }
  }
  return {
    ok: res.code === 0,
    errors: res.code === 0 ? [] : [res.stderr || res.stdout || "validator failed"],
    warnings: [],
  };
}

/**
 * Fire-and-forget launch of render_all.py — renders take hours and the
 * script is already resumable via render_state.json, so it runs detached
 * with output appended to <runDir>/render.log. Returns the pid + log path.
 */
export function launchRenderDetached(runDir: string): { pid: number; logFile: string } {
  const logFile = path.join(runDir, "render.log");
  const fd = fs.openSync(logFile, "a");
  const child = spawn(env.pythonBin, ["scripts/render_all.py", "--output-dir", runDir], {
    cwd: SKILL_ROOT,
    detached: true,
    stdio: ["ignore", fd, fd],
    env: process.env,
  });
  child.unref();
  fs.closeSync(fd);
  fs.writeFileSync(
    path.join(runDir, "render.pid"),
    JSON.stringify({ pid: child.pid, launched: new Date().toISOString(), logFile }),
  );
  return { pid: child.pid ?? -1, logFile };
}
