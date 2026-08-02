import { readFileSync, writeFileSync } from "node:fs";

const path = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(path, "utf8"));
artifact.evidence_manifest.repair_handoff_v8.relative_path = "evidence/alias/supervised-executor-repair-handoff-v8.yaml";
writeFileSync(path, `${JSON.stringify(artifact, null, 2)}\n`);
