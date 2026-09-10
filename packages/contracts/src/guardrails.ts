import guardrails from "../generation-guardrails.json";

export type GuardrailPattern = {
  id: string;
  pattern: string;
  message: string;
};

export const GENERATION_GUARDRAILS: {
  schema_version: string;
  denied_path_pattern: string;
  denied_path_message: string;
  denied_diff_patterns: GuardrailPattern[];
} = guardrails;

export function deniedPathMatcher(): RegExp {
  return new RegExp(GENERATION_GUARDRAILS.denied_path_pattern, "i");
}

export function deniedDiffMatchers(): (GuardrailPattern & { regex: RegExp })[] {
  return GENERATION_GUARDRAILS.denied_diff_patterns.map((entry) => ({
    ...entry,
    regex: new RegExp(entry.pattern, "i"),
  }));
}
