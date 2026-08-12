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
function ordered(records) { return structuredClone(records).sort((left, right) => left.path.localeCompare(right.path)); }
function rehash(record) {
  const { canonical_bytes: ignoredBytes, sha256: ignoredDigest, ...body } = structuredClone(record);
  const canonicalBytes = stable(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: digest(canonicalBytes) };
}

const artifactPath = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
let records = structuredClone(trace.final_record_universe);
const template = records.find((record) => record.record_type === "resource_lifetime" && record.payload.ordinal === "A2");
const extra = rehash({
  ...template,
  path: `kernel/${trace.id}/attempts/A3/lifetime.json`,
  payload: {
    ...template.payload,
    sequence: 0,
    ordinal: "A3",
    bootstrap_observed: null,
    bootstrap_cap: 23,
    meter_observed_preterminal: 10,
    meter_preterminal_cap: 13,
    wall_cap: 43,
    io_charge: 14,
    disk_charge: 8,
    memory_capacity: 49,
    interval_start: 24,
    interval_end: 34,
  },
});
records.push(extra);
records = ordered(records);

let prefix = ordered(records.filter((record) => record.payload.sequence === 0));
let previous = null;
const receipts = records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).sort((left, right) => left.payload.sequence - right.payload.sequence);
for (const oldReceipt of receipts) {
  const group = ordered(records.filter((record) => record.payload.sequence === oldReceipt.payload.sequence));
  const domain = group.filter((record) => !["action_receipt", "observation_receipt"].includes(record.record_type));
  const edited = structuredClone(oldReceipt);
  edited.payload.previous_journal_sha256 = previous;
  edited.payload.pre_universe_sha256 = digest(prefix);
  edited.payload.domain_record_sha256s = domain.map((record) => record.sha256);
  edited.payload.post_domain_universe_sha256 = digest(ordered([...prefix, ...domain]));
  const receipt = rehash(edited);
  records[records.findIndex((record) => record.path === oldReceipt.path)] = receipt;
  prefix = ordered([...prefix, ...domain, receipt]); previous = receipt.sha256;
}

trace.final_record_universe = ordered(records);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = previous;

const sourceRegression = artifact.regressions.find((regression) => regression.id === "SEC9-REG-SOURCE-CONTEXT-RESEED");
const sequenceThree = trace.final_record_universe.find((record) => record.record_type === "action_receipt" && record.payload.sequence === 3);
const mutatedReceipt = structuredClone(sequenceThree);
mutatedReceipt.payload.next_context = "campaign_progression";
sourceRegression.operation.after_record = rehash(mutatedReceipt);

const summary = {
  mutation: "valid A3 resource_lifetime injected into A2 sequence-zero trusted root with no admission, start, or semantic consumer",
  extra_record: extra,
  final_universe_sha256: trace.final_universe_sha256,
  final_journal_sha256: trace.final_journal_sha256,
  rebased_source_context_regression_sha256: sourceRegression.operation.after_record.sha256,
};
writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("sequence-zero-extra-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
