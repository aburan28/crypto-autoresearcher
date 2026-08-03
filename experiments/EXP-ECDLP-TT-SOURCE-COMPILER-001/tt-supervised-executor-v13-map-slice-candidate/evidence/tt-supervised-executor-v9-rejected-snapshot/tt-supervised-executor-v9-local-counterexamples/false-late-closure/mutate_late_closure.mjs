import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  }
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

function replaceMapped(value, replacements) {
  if (typeof value === "string") {
    let current = value;
    const seen = new Set();
    while (replacements.has(current) && !seen.has(current)) {
      seen.add(current);
      current = replacements.get(current);
    }
    return current;
  }
  if (Array.isArray(value)) return value.map((item) => replaceMapped(item, replacements));
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, replaceMapped(item, replacements)]));
  }
  return value;
}

const artifactPath = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
let records = structuredClone(trace.final_record_universe);
const replacements = new Map();

function mutateType(recordType, predicate, mutator) {
  const index = records.findIndex((record) => record.record_type === recordType && predicate(record));
  if (index < 0) throw new Error(`missing ${recordType}`);
  const original = records[index];
  const edited = structuredClone(original);
  mutator(edited.payload);
  const replacement = rehash(edited);
  records[index] = replacement;
  replacements.set(original.sha256, replacement.sha256);
}

mutateType("closure_request", () => true, (payload) => {
  payload.last_committed_sha256 = "0".repeat(64);
});

mutateType("resource_receipt", (record) => record.payload.ordinal === "A2", (payload) => {
  payload.input_sha256 = "e".repeat(64);
  payload.result_sha256 = "f".repeat(64);
  payload.result = { ...payload.result, cpu: payload.result.cpu + 1000000, memory: payload.result.memory + 1000000 };
});

mutateType("attempt_end", (record) => record.payload.ordinal === "A2", (payload) => {
  payload.outcome = "recoverable_crash";
  payload.terminal_request = "resume_recovery";
});

mutateType("recalculation_receipt", () => true, (payload) => {
  payload.campaign_terminal_sha256 = "0".repeat(64);
  payload.derived_totals_sha256 = "f".repeat(64);
});

mutateType("lock_release", () => true, (payload) => {
  payload.status = "held";
});

let changed = true;
while (changed) {
  changed = false;
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
    const nextPayload = replaceMapped(record.payload, replacements);
    if (stable(nextPayload) === stable(record.payload)) continue;
    const edited = rehash({ ...record, payload: nextPayload });
    records[index] = edited;
    replacements.set(record.sha256, edited.sha256);
    changed = true;
  }
}

records = ordered(records);
let prefix = ordered(records.filter((record) => record.payload.sequence === 0));
let previous = null;
const receipts = records
  .filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type))
  .sort((left, right) => left.payload.sequence - right.payload.sequence);

for (const oldReceipt of receipts) {
  const sequence = oldReceipt.payload.sequence;
  const group = ordered(records.filter((record) => record.payload.sequence === sequence));
  const domain = group.filter((record) => !["action_receipt", "observation_receipt"].includes(record.record_type));
  const edited = structuredClone(oldReceipt);
  edited.payload.previous_journal_sha256 = previous;
  edited.payload.pre_universe_sha256 = digest(prefix);
  edited.payload.domain_record_sha256s = domain.map((record) => record.sha256);
  edited.payload.post_domain_universe_sha256 = digest(ordered([...prefix, ...domain]));
  const receipt = rehash(edited);
  const index = records.findIndex((record) => record.path === oldReceipt.path);
  records[index] = receipt;
  prefix = ordered([...prefix, ...domain, receipt]);
  previous = receipt.sha256;
}

trace.final_record_universe = ordered(records);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = previous;

const summary = {
  mutation: "fully relinked A2 closure/resource/outcome/recalculation/lock forgery",
  final_universe_sha256: trace.final_universe_sha256,
  final_journal_sha256: trace.final_journal_sha256,
  records: Object.fromEntries(["closure_request", "resource_receipt", "attempt_end", "recalculation_receipt", "lock_release"].map((type) => {
    const record = trace.final_record_universe.find((candidate) => candidate.record_type === type);
    return [type, { sha256: record.sha256, payload: record.payload }];
  })),
};

writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("late-closure-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
