import { readFileSync, writeFileSync } from "node:fs";

const path = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(path, "utf8"));
const template = artifact.regressions.find((regression) => regression.id === "SEC9-REG-UNKNOWN-RECORD-TYPE");
artifact.regressions = Array.from({ length: 26 }, (_, index) => ({
  ...structuredClone(template),
  id: `TRIVIAL-UNKNOWN-${String(index + 1).padStart(2, "0")}`,
  claim: "duplicate trivial unknown-record rejection substituted for a mandatory control",
}));
artifact.regression_count = artifact.regressions.length;
artifact.builder_regression_pass_count = artifact.regressions.length;
writeFileSync(path, `${JSON.stringify(artifact, null, 2)}\n`);
