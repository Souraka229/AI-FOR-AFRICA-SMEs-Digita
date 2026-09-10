import {
  GENERATION_GUARDRAILS,
  deniedDiffMatchers,
  deniedPathMatcher,
  type VisionCritique,
} from "@afrosite/contracts";

export type QualityCheck = {
  passed: boolean;
  errors: string[];
};

export function scanGeneratedArtifact(input: {
  files: string[];
  diff: string;
}): QualityCheck {
  const errors: string[] = [];
  const deniedPath = deniedPathMatcher();
  for (const file of input.files) {
    if (deniedPath.test(file.replaceAll("\\", "/"))) {
      errors.push(`${GENERATION_GUARDRAILS.denied_path_message}: ${file}`);
    }
  }
  for (const matcher of deniedDiffMatchers()) {
    if (matcher.regex.test(input.diff)) errors.push(matcher.message);
  }
  return { passed: errors.length === 0, errors };
}

export function gateQuality(input: {
  lint: boolean;
  types: boolean;
  contracts: boolean;
  e2e: boolean;
  vision?: VisionCritique;
}): QualityCheck {
  const errors: string[] = [];
  if (!input.lint) errors.push("lint en échec");
  if (!input.types) errors.push("typecheck en échec");
  if (!input.contracts) errors.push("contrats en échec");
  if (!input.e2e) errors.push("Playwright en échec");
  if (input.vision && !input.vision.passed) errors.push("Vision Critic en échec");
  return { passed: errors.length === 0, errors };
}
