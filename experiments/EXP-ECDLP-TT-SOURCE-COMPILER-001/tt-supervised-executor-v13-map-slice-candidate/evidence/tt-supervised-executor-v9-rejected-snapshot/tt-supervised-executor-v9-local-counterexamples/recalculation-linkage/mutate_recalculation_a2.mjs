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

const artifactPath = "supervised-executor-closed-kernel-v9.json";
const artifact = JSON.parse(readFileSync(artifactPath, "utf8"));
const trace = artifact.traces.find((candidate) => candidate.id === "SEC9-TRACE-A2-END-TO-END");
const original = trace.final_record_universe;
const recalculation = structuredClone(original.find((record) => record.record_type === "recalculation_receipt"));
const lockRelease = structuredClone(original.find((record) => record.record_type === "lock_release"));
const recalculationSequence = recalculation.payload.sequence;
const releaseSequence = lockRelease.payload.sequence;
const recalculationJournal = structuredClone(original.find((record) => record.record_type === "action_receipt" && record.payload.sequence === recalculationSequence));
const releaseJournal = structuredClone(original.find((record) => record.record_type === "action_receipt" && record.payload.sequence === releaseSequence));

recalculation.payload.campaign_terminal_sha256 = "0".repeat(64);
recalculation.payload.derived_totals_sha256 = "f".repeat(64);
const forgedRecalculation = rehash(recalculation);

const prefixRecalculation = ordered(original.filter((record) => record.payload.sequence < recalculationSequence));
recalculationJournal.payload.domain_record_sha256s = [forgedRecalculation.sha256];
recalculationJournal.payload.post_domain_universe_sha256 = digest(ordered([...prefixRecalculation, forgedRecalculation]));
const forgedRecalculationJournal = rehash(recalculationJournal);

lockRelease.payload.recalculation_receipt_sha256 = forgedRecalculation.sha256;
const forgedLockRelease = rehash(lockRelease);
const prefixRelease = ordered([...prefixRecalculation, forgedRecalculation, forgedRecalculationJournal]);
releaseJournal.payload.previous_journal_sha256 = forgedRecalculationJournal.sha256;
releaseJournal.payload.pre_universe_sha256 = digest(prefixRelease);
releaseJournal.payload.domain_record_sha256s = [forgedLockRelease.sha256];
releaseJournal.payload.post_domain_universe_sha256 = digest(ordered([...prefixRelease, forgedLockRelease]));
const forgedReleaseJournal = rehash(releaseJournal);

trace.final_record_universe = ordered([
  ...original.filter((record) => record.payload.sequence < recalculationSequence),
  forgedRecalculation,
  forgedRecalculationJournal,
  forgedLockRelease,
  forgedReleaseJournal,
]);
trace.final_universe_sha256 = digest(trace.final_record_universe);
trace.final_journal_sha256 = forgedReleaseJournal.sha256;

writeFileSync(artifactPath, `${JSON.stringify(artifact, null, 2)}\n`);
writeFileSync("counterexample-summary.json", `${JSON.stringify({
  mutation: "A2 recalculation receipt binds nonexistent terminal and fabricated totals",
  original_recalculation_sha256: recalculation.sha256,
  forged_recalculation_sha256: forgedRecalculation.sha256,
  forged_campaign_terminal_sha256: forgedRecalculation.payload.campaign_terminal_sha256,
  forged_derived_totals_sha256: forgedRecalculation.payload.derived_totals_sha256,
  relinked_lock_release_sha256: forgedLockRelease.sha256,
  relinked_final_journal_sha256: forgedReleaseJournal.sha256,
  relinked_final_universe_sha256: trace.final_universe_sha256,
}, null, 2)}\n`);
