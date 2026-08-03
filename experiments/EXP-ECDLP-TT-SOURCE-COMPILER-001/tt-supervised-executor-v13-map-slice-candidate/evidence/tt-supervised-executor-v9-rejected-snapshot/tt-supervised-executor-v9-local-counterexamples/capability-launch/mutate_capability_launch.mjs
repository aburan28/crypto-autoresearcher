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
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, replaceMapped(item, replacements)]));
  return value;
}

const artifactPath = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
let records = structuredClone(trace.final_record_universe);
const replacements = new Map();

function mutate(recordType, predicate, mutator) {
  const index = records.findIndex((record) => record.record_type === recordType && predicate(record));
  if (index < 0) throw new Error(`missing ${recordType}`);
  const original = records[index];
  const payload = structuredClone(original.payload);
  mutator(payload, original);
  const edited = rehash({ ...original, payload });
  records[index] = edited;
  replacements.set(original.sha256, edited.sha256);
  return { original, edited };
}

const alternateToken = "private-map:A0:P0:fd=99:target=public-decoy";
mutate("private_map_open_observation", (record) => record.payload.phase === "E0", (payload) => {
  payload.descriptor_token = alternateToken;
});
mutate("private_map_opened_receipt", (record) => record.payload.phase === "E0", (payload) => {
  payload.descriptor_token = alternateToken;
});
mutate("launch_intent", (record) => record.payload.phase === "E0", (payload) => {
  payload.private_map_receipt_sha256 = null;
});
const spawnMutation = mutate("phase_spawn", (record) => record.payload.phase === "E0", (payload) => {
  payload.process_token = "process:A0:P0:replayed";
});
replacements.set(spawnMutation.original.payload.process_token, spawnMutation.edited.payload.process_token);

for (let round = 0; round < 100; round += 1) {
  let changed = false;
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
    const payload = replaceMapped(record.payload, replacements);
    if (stable(payload) === stable(record.payload)) continue;
    const edited = rehash({ ...record, payload });
    records[index] = edited;
    replacements.set(record.sha256, edited.sha256);
    changed = true;
  }
  if (!changed) break;
  if (round === 99) throw new Error("dependency relink did not converge");
}

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
  prefix = ordered([...prefix, ...domain, receipt]);
  previous = receipt.sha256;
}

trace.final_record_universe = ordered(records);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = previous;

const find = (type, phase) => trace.final_record_universe.find((record) => record.record_type === type && (!phase || record.payload.phase === phase));
const summary = {
  mutation: "alternate E0 descriptor token plus null launch map binding and replayed process token",
  map_observation: find("private_map_open_observation", "E0").payload,
  map_receipt: find("private_map_opened_receipt", "E0").payload,
  launch: find("launch_intent", "E0").payload,
  spawn: find("phase_spawn", "E0").payload,
  launch_identity_A2: trace.final_record_universe.find((record) => record.record_type === "launch_identity" && record.payload.ordinal === "A2").payload,
  final_universe_sha256: trace.final_universe_sha256,
  final_journal_sha256: trace.final_journal_sha256,
};

writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("capability-launch-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
