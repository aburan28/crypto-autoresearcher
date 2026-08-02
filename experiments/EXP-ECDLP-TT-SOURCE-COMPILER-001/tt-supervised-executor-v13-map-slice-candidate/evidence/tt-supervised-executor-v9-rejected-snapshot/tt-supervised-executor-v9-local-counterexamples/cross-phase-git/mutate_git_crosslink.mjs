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

function gitHash(type, body) {
  const bytes = Buffer.isBuffer(body) ? body : Buffer.from(body, "utf8");
  return createHash("sha1").update(Buffer.concat([Buffer.from(`${type} ${bytes.length}\0`, "utf8"), bytes])).digest("hex");
}

function commitText(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
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

function registerReplacement(index, editedPayload) {
  const original = records[index];
  const edited = rehash({ ...original, payload: editedPayload });
  if (stable(original) === stable(edited)) return false;
  records[index] = edited;
  replacements.set(original.sha256, edited.sha256);
  if (typeof original.payload.oid === "string" && typeof edited.payload.oid === "string" && original.payload.oid !== edited.payload.oid) replacements.set(original.payload.oid, edited.payload.oid);
  return true;
}

const p0Blob = records.find((record) => record.record_type === "git_blob_object" && record.payload.phase === "P0");
const p1BlobOriginal = records.find((record) => record.record_type === "git_blob_object" && record.payload.phase === "P1");
const p1TreeIndex = records.findIndex((record) => record.record_type === "git_tree_object" && record.payload.phase === "P1");
const p1TreePayload = structuredClone(records[p1TreeIndex].payload);
p1TreePayload.blob_record_sha256 = p0Blob.sha256;
p1TreePayload.blob_oid = p0Blob.payload.oid;
const p1TreeBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(p0Blob.payload.oid, "hex")]);
p1TreePayload.object_bytes_hex = p1TreeBytes.toString("hex");
p1TreePayload.oid = gitHash("tree", p1TreeBytes);
registerReplacement(p1TreeIndex, p1TreePayload);

for (let round = 0; round < 100; round += 1) {
  let changed = false;
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
    const payload = replaceMapped(record.payload, replacements);
    if (stable(payload) !== stable(record.payload)) changed = registerReplacement(index, payload) || changed;
  }

  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (record.record_type !== "git_tree_object") continue;
    const blob = records.find((candidate) => candidate.record_type === "git_blob_object" && candidate.sha256 === record.payload.blob_record_sha256);
    if (!blob) throw new Error(`missing blob for ${record.path}`);
    const body = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
    const payload = { ...record.payload, blob_oid: blob.payload.oid, object_bytes_hex: body.toString("hex"), oid: gitHash("tree", body) };
    if (stable(payload) !== stable(record.payload)) changed = registerReplacement(index, payload) || changed;
  }

  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (record.record_type !== "commit_object") continue;
    const intent = records.find((candidate) => candidate.record_type === "commit_intent" && candidate.sha256 === record.payload.intent_sha256);
    if (!intent) throw new Error(`missing intent for ${record.path}`);
    const text = commitText(intent.payload);
    const payload = { ...record.payload, commit_bytes: text, oid: gitHash("commit", text), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid };
    if (stable(payload) !== stable(record.payload)) changed = registerReplacement(index, payload) || changed;
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

const p1Blob = trace.final_record_universe.find((record) => record.record_type === "git_blob_object" && record.payload.phase === "P1");
const p1Tree = trace.final_record_universe.find((record) => record.record_type === "git_tree_object" && record.payload.phase === "P1");
const p1Intent = trace.final_record_universe.find((record) => record.record_type === "commit_intent" && record.payload.phase === "P1");
const p1Content = trace.final_record_universe.find((record) => record.record_type === "phase_content" && record.payload.phase === "P1");
const summary = {
  mutation: "P1 literal tree commits the P0 blob while the valid P1 blob is left unreferenced",
  original_p1_blob_sha256: p1BlobOriginal.sha256,
  final_p1_blob_sha256: p1Blob.sha256,
  p0_blob_sha256: p0Blob.sha256,
  p1_tree_blob_record_sha256: p1Tree.payload.blob_record_sha256,
  p1_intent_tree_record_sha256: p1Intent.payload.tree_record_sha256,
  p1_intent_content_sha256: p1Intent.payload.content_sha256,
  p1_content_record_sha256: p1Content.sha256,
  p1_content_payload_sha256: p1Content.payload.content_sha256,
  final_universe_sha256: trace.final_universe_sha256,
  final_journal_sha256: trace.final_journal_sha256,
};

writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("git-crosslink-summary.json", `${JSON.stringify(summary, null, 2)}\n`);
