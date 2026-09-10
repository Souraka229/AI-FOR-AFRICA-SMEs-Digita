import { runBaselinePipeline } from "@/lib/agents/pipeline";
import { EVAL_CASES, MUST_PASS_IDS, type EvalCase } from "./cases";

export type CaseScore = {
  id: string;
  vertical: string;
  expected: string;
  passed: boolean;
  reasons: string[];
  credits: number;
  slug: string;
};

export function scoreCase(item: EvalCase): CaseScore {
  const { intent, blueprint, gate1 } = runBaselinePipeline(item.prompt);
  const reasons: string[] = [];

  if (intent.vertical !== item.expected) {
    reasons.push(`vertical ${intent.vertical} ≠ ${item.expected}`);
  }
  if (item.mustPass && !gate1.passed) {
    reasons.push(`Gate 1: ${gate1.errors.join(" · ") || "échec"}`);
  }
  if (blueprint.currency !== "XOF") {
    reasons.push("devise hors XOF");
  }
  if (blueprint.catalog.length < 1) {
    reasons.push("catalogue vide");
  }
  if (blueprint.estimated_cost_credits > blueprint.gates.budget_credits_max) {
    reasons.push("budget crédits dépassé");
  }
  if (item.mustSlug && blueprint.tenant.slug !== item.mustSlug) {
    reasons.push(`slug ${blueprint.tenant.slug} ≠ ${item.mustSlug}`);
  }

  return {
    id: item.id,
    vertical: intent.vertical,
    expected: item.expected,
    passed: reasons.length === 0,
    reasons,
    credits: blueprint.estimated_cost_credits,
    slug: blueprint.tenant.slug,
  };
}

export function runEvalHarness() {
  const scores = EVAL_CASES.map(scoreCase);
  const byVertical = {
    commerce: scores.filter((row) => row.id.startsWith("commerce")),
    restaurant: scores.filter((row) => row.id.startsWith("restaurant")),
    services: scores.filter((row) => row.id.startsWith("services")),
  };
  const passRate = scores.filter((row) => row.passed).length / scores.length;
  const must = scores.filter((row) =>
    (MUST_PASS_IDS as readonly string[]).includes(row.id),
  );
  const mustFailed = must.filter((row) => !row.passed);

  return {
    total: scores.length,
    passed: scores.filter((row) => row.passed).length,
    passRate,
    byVertical: Object.fromEntries(
      Object.entries(byVertical).map(([key, rows]) => [
        key,
        {
          total: rows.length,
          passed: rows.filter((row) => row.passed).length,
        },
      ]),
    ),
    mustFailed,
    failed: scores.filter((row) => !row.passed),
  };
}
