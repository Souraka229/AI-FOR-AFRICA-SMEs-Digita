export type AuditEvent = {
  at: string;
  agent: string;
  action: string;
  result: string;
  model?: string;
  tokens?: number;
  cacheReadTokens?: number;
  durationMs?: number;
  estimatedCostXof?: number;
};

const AGENT_LABELS: Record<string, string> = {
  intent: "Intent Agent",
  product_architect: "Product Architect",
  gate1: "Gate 1",
};

const ACTION_LABELS: Record<string, string> = {
  normalize_prompt: "Normalisation du besoin",
  build_blueprint: "Construction du Blueprint",
  validate_schema: "Contrôle schéma et budget",
};

export function auditAgentLabel(agent: string): string {
  return AGENT_LABELS[agent] ?? agent;
}

export function auditActionLabel(action: string): string {
  return ACTION_LABELS[action] ?? action;
}

export function formatAuditClock(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("fr-BJ", {
    timeZone: "Africa/Porto-Novo",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);
}
