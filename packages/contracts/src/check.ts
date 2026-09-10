import { BlueprintSchema } from "./blueprint.schema";
import { ALL_EXAMPLES } from "./examples";
import {
  GENERATION_GUARDRAILS,
  deniedDiffMatchers,
  deniedPathMatcher,
} from "./guardrails";

let failed = 0;
for (const example of ALL_EXAMPLES) {
  const result = BlueprintSchema.safeParse(example);
  if (!result.success) {
    failed += 1;
    console.error(example.tenant.slug, result.error.flatten());
  } else {
    console.log("ok", example.vertical, example.tenant.slug);
  }
}

const deniedPath = deniedPathMatcher();
const diffMatchers = deniedDiffMatchers();
if (!deniedPath.test(".github/workflows/deploy.yml")) {
  failed += 1;
  console.error("guardrails: chemin CI non bloqué");
}
if (deniedPath.test("src/app/page.tsx")) {
  failed += 1;
  console.error("guardrails: chemin légitime bloqué");
}
if (!diffMatchers.some((matcher) => matcher.regex.test("+ paymentStatus = 'confirmed'"))) {
  failed += 1;
  console.error("guardrails: logique argent non bloquée");
}
if (diffMatchers.length !== GENERATION_GUARDRAILS.denied_diff_patterns.length) {
  failed += 1;
  console.error("guardrails: patterns manquants");
}
console.log(
  `ok guardrails v${GENERATION_GUARDRAILS.schema_version} · ${diffMatchers.length} règles diff`,
);

if (failed > 0) {
  process.exit(1);
}
