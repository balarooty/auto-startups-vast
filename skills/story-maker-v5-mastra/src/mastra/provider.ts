import { env } from "./config.js";

export type AgentRole = "authoring" | "vision" | "critique";

// Default model per provider, used when the role-level env vars are unset.
// Anything the Mastra model router understands ("provider/model") works.
const DEFAULT_MODEL: Record<string, string> = {
  anthropic: "anthropic/claude-sonnet-4-5",
  openai: "openai/gpt-5",
  google: "google/gemini-2.5-pro",
};

/**
 * Resolve the model for an agent. Resolution order:
 *   1. MODEL_<AGENT_ID>   — per-agent override, may be a full "provider/model"
 *   2. Role-level var     — VISION_MODEL / CRITIQUE_MODEL / LLM_MODEL
 *   3. Provider default   — LLM_PROVIDER's entry in DEFAULT_MODEL
 *
 * A bare model id ("gpt-5") is prefixed with LLM_PROVIDER; a value that
 * already contains "/" is used verbatim so agents can mix providers.
 */
export function modelFor(role: AgentRole, agentId?: string): string {
  const agentKey = agentId?.toUpperCase().replace(/[^A-Z0-9]/g, "_");
  const perAgent = agentKey ? process.env[`MODEL_${agentKey}`] : undefined;
  const roleModel =
    role === "vision"
      ? env.visionModel || env.llmModel
      : role === "critique"
        ? env.critiqueModel || env.llmModel
        : env.llmModel;

  const resolved =
    perAgent || roleModel || DEFAULT_MODEL[env.llmProvider] || DEFAULT_MODEL.anthropic;

  return resolved.includes("/") ? resolved : `${env.llmProvider}/${resolved}`;
}
