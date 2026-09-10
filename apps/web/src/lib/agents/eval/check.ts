import { runEvalHarness } from "./run";

const MIN_PASS_RATE = 0.85;

const report = runEvalHarness();
const rate = `${Math.round(report.passRate * 100)} %`;

console.log(
  `Eval harness : ${report.passed}/${report.total} OK (${rate})`,
);
for (const [vertical, row] of Object.entries(report.byVertical)) {
  console.log(`  ${vertical}: ${row.passed}/${row.total}`);
}

if (report.mustFailed.length > 0) {
  console.error("Prompts démo (pitch) en échec :");
  for (const row of report.mustFailed) {
    console.error(`  ${row.id}: ${row.reasons.join(" ; ")}`);
  }
  process.exit(1);
}

if (report.passRate < MIN_PASS_RATE) {
  console.error(`Taux sous ${Math.round(MIN_PASS_RATE * 100)} %.`);
  for (const row of report.failed.slice(0, 12)) {
    console.error(`  ${row.id}: ${row.reasons.join(" ; ")}`);
  }
  process.exit(1);
}

if (report.failed.length > 0) {
  console.log("Échecs non bloquants :");
  for (const row of report.failed) {
    console.log(`  ${row.id}: ${row.reasons.join(" ; ")}`);
  }
}
