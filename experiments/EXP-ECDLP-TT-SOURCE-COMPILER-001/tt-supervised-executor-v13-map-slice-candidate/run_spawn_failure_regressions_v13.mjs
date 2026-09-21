import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/13";
const artifactPath = "supervised-executor-closed-kernel-v13.json";
const workDirectory = "spawn-failure-regression-inputs-v13";

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

function gitHash(type, value) {
  const bytes = Buffer.isBuffer(value) ? value : Buffer.from(value, "utf8");
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

function replaceRecord(records, path, editor) {
  const index = records.findIndex((record) => record.path === path);
  if (index < 0) throw new Error(`record not found: ${path}`);
  const edited = structuredClone(records[index]);
  editor(edited);
  const replacement = rehash(edited);
  records[index] = replacement;
  return replacement;
}

function replaceTracked(records, path, editor, replacements) {
  const original = records.find((record) => record.path === path);
  const replacement = replaceRecord(records, path, editor);
  replacements.set(original.sha256, replacement.sha256);
  return replacement;
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

function propagateDigestReferences(records, replacements) {
  for (let round = 0; round < 128; round += 1) {
    let changed = false;
    for (const record of [...records]) {
      if (["action_receipt", "observation_receipt"].includes(record.record_type)) continue;
      const payload = replaceMapped(record.payload, replacements);
      if (stable(payload) === stable(record.payload)) continue;
      replaceTracked(records, record.path, (edited) => { edited.payload = payload; }, replacements);
      changed = true;
    }
    if (!changed) return;
  }
  throw new Error("digest-reference propagation did not converge");
}

function relinkDerivedGraph(records, replacements) {
  for (let round = 0; round < 128; round += 1) {
    propagateDigestReferences(records, replacements);
    let changed = false;
    for (const tree of records.filter((record) => record.record_type === "git_tree_object")) {
      const blob = records.find((record) => record.record_type === "git_blob_object" && record.sha256 === tree.payload.blob_record_sha256);
      if (!blob) continue;
      const objectBytes = Buffer.concat([Buffer.from("100644 phase.json\0", "utf8"), Buffer.from(blob.payload.oid, "hex")]);
      const payload = { ...tree.payload, blob_oid: blob.payload.oid, object_bytes_hex: objectBytes.toString("hex"), oid: gitHash("tree", objectBytes) };
      if (stable(payload) === stable(tree.payload)) continue;
      const oldOid = tree.payload.oid;
      const changedTree = replaceTracked(records, tree.path, (record) => { record.payload = payload; }, replacements);
      if (oldOid !== changedTree.payload.oid) replacements.set(oldOid, changedTree.payload.oid);
      changed = true;
    }
    propagateDigestReferences(records, replacements);
    for (const object of records.filter((record) => record.record_type === "commit_object")) {
      const intent = records.find((record) => record.record_type === "commit_intent" && record.sha256 === object.payload.intent_sha256);
      if (!intent) continue;
      const bytes = commitText(intent.payload);
      const payload = { ...object.payload, commit_bytes: bytes, oid: gitHash("commit", bytes), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid };
      if (stable(payload) === stable(object.payload)) continue;
      const oldOid = object.payload.oid;
      const changedObject = replaceTracked(records, object.path, (record) => { record.payload = payload; }, replacements);
      if (oldOid !== changedObject.payload.oid) replacements.set(oldOid, changedObject.payload.oid);
      changed = true;
    }
    if (!changed) {
      propagateDigestReferences(records, replacements);
      return;
    }
  }
  throw new Error("derived Git graph relinking did not converge");
}

function relinkJournals(input, initialReplacements = new Map()) {
  const records = ordered(input);
  const replacements = new Map(initialReplacements);
  let previous = null;
  const receiptPaths = records
    .filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type))
    .sort((left, right) => left.payload.sequence - right.payload.sequence)
    .map((record) => record.path);
  for (const receiptPath of receiptPaths) {
    relinkDerivedGraph(records, replacements);
    const oldReceipt = records.find((record) => record.path === receiptPath);
    const sequence = oldReceipt.payload.sequence;
    const prefix = ordered(records.filter((record) => record.payload.sequence < sequence));
    const group = ordered(records.filter((record) => record.payload.sequence === sequence));
    const domain = group.filter((record) => !["action_receipt", "observation_receipt"].includes(record.record_type));
    const edited = structuredClone(oldReceipt);
    edited.payload = replaceMapped(edited.payload, replacements);
    edited.payload.previous_journal_sha256 = previous;
    edited.payload.pre_universe_sha256 = digest(prefix);
    edited.payload.domain_record_sha256s = domain.map((record) => record.sha256);
    edited.payload.post_domain_universe_sha256 = digest(ordered([...prefix, ...domain]));
    const receipt = rehash(edited);
    records[records.findIndex((record) => record.path === oldReceipt.path)] = receipt;
    replacements.set(oldReceipt.sha256, receipt.sha256);
    previous = receipt.sha256;
  }
  return ordered(records);
}

function mutateTrackedGraphRecord(records, type, predicate, editor) {
  const replacements = new Map();
  const record = records.find((candidate) => candidate.record_type === type && predicate(candidate));
  if (!record) throw new Error(`tracked mutation record missing: ${type}`);
  replaceTracked(records, record.path, (changed) => editor(changed.payload, changed, replacements), replacements);
  relinkDerivedGraph(records, replacements);
  return relinkJournals(records, replacements);
}

function spawnObservation(records, phase) {
  const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === phase);
  const receipt = records.find((record) => record.record_type === "observation_receipt" && record.payload.observation_kind === "phase_spawn" && record.payload.domain_record_sha256s.includes(spawn.sha256));
  if (!spawn || !receipt) throw new Error(`spawn observation missing: ${phase}`);
  return { spawn, receipt };
}

function mutateSpawnObservation(records, phase, editor) {
  const { receipt } = spawnObservation(records, phase);
  replaceRecord(records, receipt.path, (record) => editor(record.payload));
  return relinkJournals(records);
}

function replay(validatorPath, inputPath) {
  const run = spawnSync(process.execPath, [validatorPath, "--replay-file", inputPath], { encoding: "utf8" });
  const lines = run.stdout.trim().split("\n").filter(Boolean);
  if (lines.length !== 1) throw new Error(`${validatorPath} emitted invalid replay output: ${run.stdout}${run.stderr}`);
  return { ...JSON.parse(lines[0]), exit_code: run.status };
}

const artifactBytes = readFileSync(artifactPath);
const artifact = JSON.parse(artifactBytes);
const cleanTrace = artifact.traces.find((trace) => trace.id === "SEC13-TRACE-A0-END-TO-END");
const failureTrace = artifact.traces.find((trace) => trace.id === "SEC13-TRACE-P0-SPAWN-FAILURE");
if (!cleanTrace || !failureTrace) throw new Error("required V13 traces missing");

const cases = [
  {
    id: "spawn_observation_empty_context",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_CONTEXT_MISMATCH",
    mutate: (records) => mutateSpawnObservation(records, "P0", (payload) => { payload.context = ""; }),
  },
  {
    id: "spawn_observation_null_context",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_CONTEXT_MISMATCH",
    mutate: (records) => mutateSpawnObservation(records, "P0", (payload) => { payload.context = null; }),
  },
  {
    id: "spawn_observation_wrong_request",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_BINDING_MISMATCH",
    mutate: (records) => mutateSpawnObservation(records, "P0", (payload) => { payload.request_sha256 = "0".repeat(64); }),
  },
  {
    id: "spawn_observation_wrong_subject",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_BINDING_MISMATCH",
    mutate: (records) => mutateSpawnObservation(records, "P0", (payload) => { payload.subject_sha256 = "f".repeat(64); }),
  },
  {
    id: "consumed_spawn_request_reused_by_e0",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_BINDING_MISMATCH",
    mutate(records) {
      const p0 = spawnObservation(records, "P0").receipt;
      const e0 = spawnObservation(records, "E0").receipt;
      replaceRecord(records, e0.path, (record) => {
        record.payload.request_sha256 = p0.payload.request_sha256;
        record.payload.subject_sha256 = p0.payload.subject_sha256;
      });
      return relinkJournals(records);
    },
  },
  {
    id: "spawn_domain_wrong_request",
    trace: failureTrace,
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_spawn", (record) => record.payload.phase === "P0", (payload) => { payload.request_action_receipt_sha256 = "0".repeat(64); }),
  },
  {
    id: "spawn_domain_cross_phase_launch",
    trace: failureTrace,
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate(records) {
      const foreignLaunch = cleanTrace.final_record_universe.find((record) => record.record_type === "launch_intent" && record.payload.phase === "P1");
      return mutateTrackedGraphRecord(records, "phase_spawn", (record) => record.payload.phase === "P0", (payload) => { payload.launch_intent_sha256 = foreignLaunch.sha256; });
    },
  },
  {
    id: "spawn_domain_cross_ordinal",
    trace: failureTrace,
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_spawn", (record) => record.payload.phase === "P0", (payload) => { payload.ordinal = "A1"; }),
  },
  {
    id: "spawn_failed_followed_by_reap",
    trace: cleanTrace,
    expected_rejection: "PHASE_REAP_INVALID",
    mutate(records) {
      const { spawn, receipt } = spawnObservation(records, "P0");
      const replacements = new Map();
      replaceTracked(records, spawn.path, (record) => {
        record.payload.outcome = "spawn_failed";
        record.payload.process_token = null;
      }, replacements);
      replaceRecord(records, receipt.path, (record) => { record.payload.observed_value = "spawn_failed"; });
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "spawn_failure_terminal_over_pid",
    trace: cleanTrace,
    expected_rejection: "TERMINAL_EVENT_EVIDENCE_INVALID",
    mutate(records) {
      const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === "P0");
      return mutateTrackedGraphRecord(records, "phase_terminal", (record) => record.payload.phase === "P0", (payload) => {
        payload.event_kind = "spawn_failure";
        payload.outcome = "TERMINAL_HARNESS_FAILURE";
        payload.predecessor_sha256 = spawn.sha256;
        payload.result_sha256 = null;
        payload.content_sha256 = null;
      });
    },
  },
  {
    id: "forged_failure_envelope_bytes",
    trace: failureTrace,
    expected_rejection: "GIT_BLOB_BYTES_MISMATCH",
    mutate(records) {
      const replacements = new Map();
      const blob = records.find((record) => record.record_type === "git_blob_object" && record.payload.phase === "P0");
      const forged = Buffer.from("{\"forged\":true}\n", "utf8");
      const oldOid = blob.payload.oid;
      const changed = replaceTracked(records, blob.path, (record) => {
        record.payload.object_bytes_hex = forged.toString("hex");
        record.payload.oid = gitHash("blob", forged);
      }, replacements);
      replacements.set(oldOid, changed.payload.oid);
      relinkDerivedGraph(records, replacements);
      return relinkJournals(records, replacements);
    },
  },
  {
    id: "forged_failure_source_kind",
    trace: failureTrace,
    expected_rejection: "GIT_BLOB_BYTES_MISMATCH",
    mutate: (records) => mutateTrackedGraphRecord(records, "git_blob_object", (record) => record.payload.phase === "P0", (payload) => { payload.source_kind = "phase_content"; }),
  },
  {
    id: "forged_failure_source_record",
    trace: failureTrace,
    expected_rejection: "GIT_BLOB_BYTES_MISMATCH",
    mutate(records) {
      const foreignTerminal = cleanTrace.final_record_universe.find((record) => record.record_type === "phase_terminal" && record.payload.phase === "P1");
      return mutateTrackedGraphRecord(records, "git_blob_object", (record) => record.payload.phase === "P0", (payload) => { payload.source_record_sha256 = foreignTerminal.sha256; });
    },
  },
  {
    id: "failure_intent_nonnull_success_links",
    trace: failureTrace,
    expected_rejection: "GIT_INTENT_LINK_MISSING",
    mutate(records) {
      const foreignResult = cleanTrace.final_record_universe.find((record) => record.record_type === "phase_result" && record.payload.phase === "P1");
      const foreignContent = cleanTrace.final_record_universe.find((record) => record.record_type === "phase_content" && record.payload.phase === "P1");
      return mutateTrackedGraphRecord(records, "commit_intent", (record) => record.payload.phase === "P0", (payload) => {
        payload.result_sha256 = foreignResult.sha256;
        payload.content_sha256 = foreignContent.sha256;
      });
    },
  },
  {
    id: "e0_close_after_valid_predecessor",
    trace: cleanTrace,
    expected_rejection: "RESERVATION_FAILURE_PREDECESSOR_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_reservation", (record) => record.payload.phase === "E0", (payload) => { payload.phase_mode = "E0:close_prior_failure"; }),
  },
  {
    id: "skipped_phases_without_failure_close",
    trace: failureTrace,
    expected_rejection: "RESERVATION_PREDECESSOR_MISMATCH",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_reservation", (record) => record.payload.phase === "E0", (payload) => { payload.phase_mode = "E0:evaluate"; }),
  },
  {
    id: "spawn_observed_value_domain_mismatch",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_RECORD_MISMATCH",
    mutate: (records) => mutateSpawnObservation(records, "P0", (payload) => { payload.observed_value = "pid_returned"; }),
  },
  {
    id: "an002_attempts_to_author_spawn",
    trace: failureTrace,
    expected_rejection: "PHASE_SPAWN_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_spawn", (record) => record.payload.phase === "P0", (payload) => { payload.sequence = 7; }),
  },
  {
    id: "spawn_producer_action_authority_forgery",
    trace: failureTrace,
    expected_rejection: "PRODUCER_UNAUTHORIZED",
    mutate: (records) => mutateTrackedGraphRecord(records, "phase_spawn", (record) => record.payload.phase === "P0", (payload, record) => { record.producer = "root_supervisor"; }),
  },
];

rmSync(workDirectory, { recursive: true, force: true });
mkdirSync(workDirectory, { recursive: true });
const results = [];
for (const spec of cases) {
  const records = spec.mutate(structuredClone(spec.trace.final_record_universe));
  const input = { schema: "tt-supervised-executor-replay-input-v13", protocol, mutation_id: spec.id, records };
  const inputPath = join(workDirectory, `${spec.id}.json`);
  const bytes = Buffer.from(`${JSON.stringify(input, null, 2)}\n`, "utf8");
  writeFileSync(inputPath, bytes);
  const builderDecision = replay("build_v13_closed_kernel.mjs", inputPath);
  const verifierDecision = replay("verify_v13_closed_kernel.mjs", inputPath);
  const decisionsMatch = builderDecision.decision === verifierDecision.decision && builderDecision.rejection === verifierDecision.rejection;
  const expectedMatch = builderDecision.decision === "REJECT" && builderDecision.rejection === spec.expected_rejection && verifierDecision.rejection === spec.expected_rejection;
  results.push({
    id: spec.id,
    source_trace: spec.trace.id,
    expected_rejection: spec.expected_rejection,
    input_artifact: inputPath,
    input_sha256: digest(bytes),
    record_universe_sha256: digest(ordered(records)),
    record_count: records.length,
    journal_count: records.filter((record) => ["action_receipt", "observation_receipt"].includes(record.record_type)).length,
    relinking: "changed_records_rehashed_digest_references_and_git_objects_propagated_journal_roots_recomputed_first_rejection_only",
    builder_decision: builderDecision,
    verifier_decision: verifierDecision,
    decisions_match: decisionsMatch,
    expected_rejection_match: expectedMatch,
    pass: decisionsMatch && expectedMatch,
  });
}

const failed = results.filter((result) => !result.pass);
const receipt = {
  schema: "tt-supervised-executor-spawn-failure-regressions-v13",
  protocol,
  status: failed.length === 0 ? "PASS" : "FAIL",
  evidence_status: ["MODEL-BOUND", "ZERO-RUN"],
  source_artifact: { path: artifactPath, sha256: digest(artifactBytes) },
  validator_snapshots: {
    harness: { path: "run_spawn_failure_regressions_v13.mjs", sha256: digest(readFileSync("run_spawn_failure_regressions_v13.mjs")) },
    builder: { path: "build_v13_closed_kernel.mjs", sha256: digest(readFileSync("build_v13_closed_kernel.mjs")) },
    verifier: { path: "verify_v13_closed_kernel.mjs", sha256: digest(readFileSync("verify_v13_closed_kernel.mjs")) },
  },
  case_count: results.length,
  pass_count: results.filter((result) => result.pass).length,
  results,
  limitations: [
    "These controls cover only the V13 P0 spawn-failure and failure-commit vertical slice.",
    "Mutations establish the preregistered first rejection; downstream selector sources and actions are not causally regenerated, so a case may retain secondary rejection causes.",
    "They do not establish positive reachability for map, reap, restart, recovery, infrastructure, or all selector rules.",
    "The observation gateway is replayed as typed finite-model evidence; OS truthfulness and crash atomicity remain outside the model.",
    "No runtime or cryptanalytic campaign was executed.",
  ],
};
writeFileSync("spawn-failure-regressions-v13.json", `${JSON.stringify(receipt, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({
  status: receipt.status,
  receipt: "spawn-failure-regressions-v13.json",
  receipt_sha256: digest(readFileSync("spawn-failure-regressions-v13.json")),
  cases: results.length,
  passes: receipt.pass_count,
  failed: failed.map((result) => ({ id: result.id, expected: result.expected_rejection, builder: result.builder_decision.rejection, verifier: result.verifier_decision.rejection })),
})}\n`);
if (failed.length > 0) process.exitCode = 1;
