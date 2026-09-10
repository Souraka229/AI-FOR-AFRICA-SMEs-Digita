import { runQaAgent } from "./qa";

const passingVision = {
  passed: true,
  score: 90,
  summary: "OK",
  issues: [],
};

const ok = runQaAgent({
  unit: { lint: true, types: true, contracts: true, pay: true },
  e2e: { studio: true, storefront: true, desktop: true, mobile: true },
  gate5: { migrationOnCopy: true, backupVerified: true, rollbackReady: true },
  vision: passingVision,
});
if (!ok.passed) throw new Error(`QA nominal doit passer : ${ok.errors.join(" ; ")}`);

const noPlaywright = runQaAgent({
  unit: { lint: true, types: true, contracts: true, pay: true },
  e2e: { studio: false, storefront: true, desktop: true, mobile: true },
  gate5: { migrationOnCopy: true, backupVerified: true, rollbackReady: true },
});
if (noPlaywright.passed || !noPlaywright.errors.some((item) => item.includes("Playwright"))) {
  throw new Error("QA doit bloquer sans spec Studio Playwright.");
}

const noBackup = runQaAgent({
  unit: { lint: true, types: true, contracts: true, pay: true },
  e2e: { studio: true, storefront: true, desktop: true, mobile: true },
  gate5: { migrationOnCopy: true, backupVerified: false, rollbackReady: true },
});
if (noBackup.passed || !noBackup.errors.some((item) => item.includes("backup"))) {
  throw new Error("QA doit bloquer Gate 5 sans backup vérifié.");
}

const production = runQaAgent({
  unit: { lint: true, types: true, contracts: true, pay: true },
  e2e: { studio: true, storefront: true, desktop: true, mobile: true },
  gate5: { migrationOnCopy: true, backupVerified: true, rollbackReady: true },
  productionTarget: true,
});
if (production.passed) throw new Error("QA ne doit jamais valider une cible production.");

console.log("check:qa OK · unitaires · Playwright · gate 5 · refus prod");
