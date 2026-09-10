import type { VisionCritique } from "@afrosite/contracts";
import { gateQuality, type QualityCheck } from "@/lib/agents/quality";

export const QA_E2E_SPECS = ["studio", "storefront"] as const;
export const QA_VIEWPORTS = ["desktop", "mobile"] as const;

export type QaUnitFlags = {
  lint: boolean;
  types: boolean;
  contracts: boolean;
  pay: boolean;
};

export type QaE2eFlags = {
  studio: boolean;
  storefront: boolean;
  desktop: boolean;
  mobile: boolean;
};

export type QaGate5Flags = {
  migrationOnCopy: boolean;
  backupVerified: boolean;
  rollbackReady: boolean;
};

export type QaAgentInput = {
  unit: QaUnitFlags;
  e2e: QaE2eFlags;
  gate5: QaGate5Flags;
  vision?: VisionCritique;
  productionTarget?: boolean;
};

export type QaAgentReport = QualityCheck & {
  gate: "g5";
  specs: string[];
};

export function runQaAgent(input: QaAgentInput): QaAgentReport {
  const errors: string[] = [];
  if (input.productionTarget) {
    errors.push("QA Agent refuse une cible production (gate 6).");
  }
  if (!input.unit.pay) errors.push("check:pay en échec");
  const quality = gateQuality({
    lint: input.unit.lint,
    types: input.unit.types,
    contracts: input.unit.contracts,
    e2e: QA_E2E_SPECS.every((spec) => input.e2e[spec]) &&
      QA_VIEWPORTS.every((viewport) => input.e2e[viewport]),
    vision: input.vision,
  });
  errors.push(...quality.errors);
  if (!input.gate5.migrationOnCopy) {
    errors.push("Gate 5 : migration non testée sur une copie");
  }
  if (!input.gate5.backupVerified) {
    errors.push("Gate 5 : backup non vérifié");
  }
  if (!input.gate5.rollbackReady) {
    errors.push("Gate 5 : rollback non prêt");
  }
  return {
    passed: errors.length === 0,
    errors,
    gate: "g5",
    specs: [...QA_E2E_SPECS],
  };
}
