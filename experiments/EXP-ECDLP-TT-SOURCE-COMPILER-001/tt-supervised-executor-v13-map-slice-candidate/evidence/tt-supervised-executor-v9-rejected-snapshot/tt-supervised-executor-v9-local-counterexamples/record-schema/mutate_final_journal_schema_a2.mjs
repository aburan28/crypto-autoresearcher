import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function digest(value) {
  const input = typeof value === "string" || Buffer.isBuffer(value) ? value : stable(value);
  return createHash("sha256").update(input).digest("hex");
}

function ordered(records) {
  return structuredClone(records).sort((left, right) => left.path.localeCompare(right.path));
}

function rehash(record) {
  const { canonical_bytes: ignoredBytes, sha256: ignoredDigest, ...body } = structuredClone(record);
  const canonicalBytes = stable(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: digest(canonicalBytes) };
}

const path = "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(path, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
const journals = trace.final_record_universe.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((left, right) => left.payload.sequence - right.payload.sequence);
const original = journals.at(-1);
const changed = structuredClone(original);
changed.schema = "attacker-selected-record-schema-v0";
const forged = rehash(changed);
trace.final_record_universe = ordered(trace.final_record_universe.map((record) => record.path === original.path ? forged : record));
trace.final_journal_sha256 = forged.sha256;
trace.final_universe_sha256 = digest(trace.final_record_universe);
writeFileSync(path, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("counterexample-summary.json", `${JSON.stringify({
  mutation: "A2 final action receipt uses an attacker-selected record schema literal",
  path: forged.path,
  original_sha256: original.sha256,
  forged_sha256: forged.sha256,
  forged_schema: forged.schema,
  final_universe_sha256: trace.final_universe_sha256,
}, null, 2)}\n`);
