import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

function stable(value) {
  if (Array.isArray(value)) return `[${value.map(stable).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}
function digest(value) { const input = typeof value === "string" || Buffer.isBuffer(value) ? value : stable(value); return createHash("sha256").update(input).digest("hex"); }
function ordered(records) { return structuredClone(records).sort((left, right) => left.path.localeCompare(right.path)); }
function rehash(record) {
  const { canonical_bytes: ignoredBytes, sha256: ignoredDigest, ...body } = structuredClone(record);
  const canonicalBytes = stable(body); return { ...body, canonical_bytes: canonicalBytes, sha256: digest(canonicalBytes) };
}
function replaceMapped(value, replacements) {
  if (typeof value === "string") { let current = value; const seen = new Set(); while (replacements.has(current) && !seen.has(current)) { seen.add(current); current = replacements.get(current); } return current; }
  if (Array.isArray(value)) return value.map((item) => replaceMapped(item, replacements));
  if (value !== null && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, replaceMapped(item, replacements)]));
  return value;
}

const artifactPath = process.argv[2] || "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
let records = structuredClone(trace.final_record_universe);
const replacements = new Map();
function replaceRecord(index, payload) {
  const original = records[index]; const edited = rehash({ ...original, payload }); records[index] = edited; replacements.set(original.sha256, edited.sha256); return edited;
}

const p0Result = records.find((record) => record.record_type === "phase_result" && record.payload.phase === "P0");
const p0Content = records.find((record) => record.record_type === "phase_content" && record.payload.phase === "P0");
const p1TerminalIndex = records.findIndex((record) => record.record_type === "phase_terminal" && record.payload.phase === "P1");
const terminalPayload = { ...records[p1TerminalIndex].payload, predecessor_sha256: p0Content.sha256, result_sha256: p0Result.sha256, content_sha256: p0Content.sha256 };
const terminal = replaceRecord(p1TerminalIndex, terminalPayload);

for (let round = 0; round < 100; round += 1) {
  let changed = false;
  for (let index = 0; index < records.length; index += 1) {
    const record = records[index];
    if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
    const payload = replaceMapped(record.payload, replacements);
    if (stable(payload) === stable(record.payload)) continue;
    replaceRecord(index, payload); changed = true;
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
  prefix = ordered([...prefix, ...domain, receipt]); previous = receipt.sha256;
}
trace.final_record_universe = ordered(records);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = previous;
writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("terminal-crossphase-summary.json", `${JSON.stringify({ mutation: "P1 valid-outcome terminal points to P0 result/content/predecessor", terminal_sha256: terminal.sha256, terminal: terminal.payload, p0_result_sha256: p0Result.sha256, p0_content_sha256: p0Content.sha256, final_universe_sha256: trace.final_universe_sha256, final_journal_sha256: trace.final_journal_sha256 }, null, 2)}\n`);
