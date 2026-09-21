import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/13";
const artifactPath = "supervised-executor-closed-kernel-v13.json";
const workDirectory = "map-failure-regression-inputs-v13";

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

function mapObservation(records) {
  const observation = records.find((record) => record.record_type === "private_map_open_observation");
  const receipt = observation && records.find((record) => record.record_type === "observation_receipt" && record.payload.observation_kind === "private_map_open" && record.payload.domain_record_sha256s.includes(observation.sha256));
  if (!observation || !receipt) throw new Error("map observation missing");
  return { observation, receipt };
}

function mutateMapObservationReceipt(records, editor) {
  const { receipt } = mapObservation(records);
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
const failureTrace = artifact.traces.find((trace) => trace.id === "SEC13-TRACE-E0-MAP-FAILURE");
const closeTrace = artifact.traces.find((trace) => trace.id === "SEC13-TRACE-P0-RUNTIME-FAILURE");
if (!cleanTrace || !failureTrace || !closeTrace) throw new Error("required V13 traces missing");

const cases = [
  {
    id: "map_observation_wrong_request",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_BINDING_MISMATCH",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.request_sha256 = "0".repeat(64); }),
  },
  {
    id: "map_observation_wrong_subject",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_BINDING_MISMATCH",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.subject_sha256 = "f".repeat(64); }),
  },
  {
    id: "map_observation_empty_context",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_CONTEXT_MISMATCH",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.context = ""; }),
  },
  {
    id: "map_observation_null_context",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_CONTEXT_MISMATCH",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.context = null; }),
  },
  {
    id: "map_observed_value_domain_mismatch",
    trace: failureTrace,
    expected_rejection: "OBSERVATION_RECORD_MISMATCH",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.observed_value = "map_opened"; }),
  },
  {
    id: "map_observation_invalid_value",
    trace: failureTrace,
    expected_rejection: "MAP_OBSERVATION_VALUE_INVALID",
    mutate: (records) => mutateMapObservationReceipt(records, (payload) => { payload.observed_value = "map_open_unknown"; }),
  },
  {
    id: "map_domain_wrong_request",
    trace: failureTrace,
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "private_map_open_observation", () => true, (payload) => { payload.request_action_receipt_sha256 = "0".repeat(64); }),
  },
  {
    id: "map_domain_cross_ordinal",
    trace: failureTrace,
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate: (records) => mutateTrackedGraphRecord(records, "private_map_open_observation", () => true, (payload) => { payload.ordinal = "A1"; }),
  },
  {
    id: "map_domain_cross_intent",
    trace: failureTrace,
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate(records) {
      const foreignIntent = cleanTrace.final_record_universe.find((record) => record.record_type === "private_map_open_intent");
      return mutateTrackedGraphRecord(records, "private_map_open_observation", () => true, (payload) => { payload.open_intent_sha256 = foreignIntent.sha256; });
    },
  },
  {
    id: "map_observation_after_close_mode",
    trace: closeTrace,
    expected_rejection: "MAP_OBSERVATION_NOT_PENDING",
    mutate(records) {
      const source = records.filter((record) => record.record_type === "observation_receipt").sort((left, right) => right.payload.sequence - left.payload.sequence)[0];
      const finalAction = records.filter((record) => record.record_type === "action_receipt").sort((left, right) => right.payload.sequence - left.payload.sequence)[0];
      const sequence = Math.max(...records.map((record) => record.payload.sequence)) + 1;
      const late = structuredClone(source);
      late.path = source.path.replace(/journal\/\d+-observation\.json$/, `journal/${String(sequence).padStart(4, "0")}-observation.json`);
      late.payload.sequence = sequence;
      late.payload.observation_kind = "private_map_open";
      late.payload.context = finalAction.payload.next_context;
      late.payload.request_sha256 = "0".repeat(64);
      late.payload.subject_sha256 = "f".repeat(64);
      late.payload.observed_value = "map_opened";
      late.payload.domain_record_sha256s = [];
      records.push(rehash(late));
      return relinkJournals(records);
    },
  },
  {
    id: "map_domain_active_e0_close_mode",
    trace: closeTrace,
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate(records) {
      const closeId = closeTrace.id;
      const reservation = records.find((record) => record.record_type === "phase_reservation" && record.payload.phase === "E0");
      const ordinal = reservation.payload.ordinal;
      const requestSource = failureTrace.final_record_universe.find((record) => record.record_type === "action_receipt" && record.payload.selected_rule === "P001");
      const intentSource = failureTrace.final_record_universe.find((record) => record.record_type === "private_map_open_intent");
      const observationSource = failureTrace.final_record_universe.find((record) => record.record_type === "private_map_open_observation");
      const receiptSource = failureTrace.final_record_universe.find((record) => record.record_type === "observation_receipt" && record.payload.observation_kind === "private_map_open");
      const sequence = Math.max(...records.map((record) => record.payload.sequence)) + 1;

      const intentDraft = structuredClone(intentSource);
      intentDraft.path = `kernel/${closeId}/phases/E0/private-map-intent.json`;
      intentDraft.payload = { ...intentDraft.payload, sequence, campaign_id: closeId, ordinal, reservation_sha256: reservation.sha256 };
      const intent = rehash(intentDraft);

      const requestDraft = structuredClone(requestSource);
      requestDraft.path = `kernel/${closeId}/journal/${String(sequence).padStart(4, "0")}-action.json`;
      requestDraft.payload = { ...requestDraft.payload, sequence, campaign_id: closeId, selected_rule: "P001", selected_action: "write_private_map_open_intent", next_context: "e0_private_map", domain_record_sha256s: [intent.sha256] };
      const request = rehash(requestDraft);

      const observationDraft = structuredClone(observationSource);
      observationDraft.path = `kernel/${closeId}/phases/E0/private-map-observation.json`;
      observationDraft.payload = { ...observationDraft.payload, sequence: sequence + 1, campaign_id: closeId, ordinal, request_action_receipt_sha256: request.sha256, open_intent_sha256: intent.sha256, outcome: "opened", descriptor_token: `private-map:${ordinal}:E0` };
      const observation = rehash(observationDraft);

      const receiptDraft = structuredClone(receiptSource);
      receiptDraft.path = `kernel/${closeId}/journal/${String(sequence + 1).padStart(4, "0")}-observation.json`;
      receiptDraft.payload = { ...receiptDraft.payload, sequence: sequence + 1, campaign_id: closeId, context: "e0_private_map", request_sha256: request.sha256, subject_sha256: intent.sha256, observed_value: "map_opened", domain_record_sha256s: [observation.sha256] };
      const receipt = rehash(receiptDraft);
      return ordered([...records, intent, request, observation, receipt]);
    },
  },
  {
    id: "forced_p002_after_p001_wait",
    trace: cleanTrace,
    expected_rejection: "ACTION_EXECUTED_WHILE_NOT_READY",
    mutate(records) {
      const request = records.find((record) => record.record_type === "action_receipt" && record.payload.selected_rule === "P001");
      const source = records.find((record) => record.record_type === "action_receipt" && record.payload.selected_rule === "P004");
      const sequence = request.payload.sequence + 1;
      const forced = structuredClone(source);
      forced.path = source.path.replace(/journal\/\d+-action\.json$/, `journal/${String(sequence).padStart(4, "0")}-action.json`);
      forced.payload = { ...forced.payload, sequence, selected_rule: "P002", selected_action: "open_private_map_trusted_descriptor", next_context: "e0_private_map", domain_record_sha256s: [] };
      const prefix = records.filter((record) => record.payload.sequence <= request.payload.sequence);
      prefix.push(rehash(forced));
      return relinkJournals(prefix);
    },
  },
  {
    id: "p003_extra_domain_record",
    trace: failureTrace,
    expected_rejection: "ACTION_RECORD_MISMATCH",
    mutate(records) {
      const p003 = records.find((record) => record.record_type === "action_receipt" && record.payload.selected_rule === "P003");
      return mutateTrackedGraphRecord(records, "ref_observation_pre", (record) => record.payload.phase === "E0", (payload) => { payload.sequence = p003.payload.sequence; });
    },
  },
  {
    id: "p001_attempts_to_author_map_observation",
    trace: failureTrace,
    expected_rejection: "PRIVATE_MAP_OBSERVATION_INVALID",
    mutate(records) {
      const { observation } = mapObservation(records);
      const request = records.find((record) => record.record_type === "action_receipt" && record.sha256 === observation.payload.request_action_receipt_sha256);
      const replacements = new Map();
      replaceTracked(records, observation.path, (record) => { record.payload.sequence = request.payload.sequence; }, replacements);
      relinkDerivedGraph(records, replacements);
      return ordered(records);
    },
  },
  {
    id: "map_observation_producer_action_authority_forgery",
    trace: failureTrace,
    expected_rejection: "PRODUCER_UNAUTHORIZED",
    mutate: (records) => mutateTrackedGraphRecord(records, "private_map_open_observation", () => true, (payload, record) => { record.producer = "root_supervisor"; }),
  },
  {
    id: "duplicate_map_observation_consumption",
    trace: failureTrace,
    expected_rejection: "MAP_OBSERVATION_REUSED",
    mutate(records) {
      const source = mapObservation(records).receipt;
      const sequence = Math.max(...records.map((record) => record.payload.sequence)) + 1;
      const duplicate = structuredClone(source);
      duplicate.path = source.path.replace(/journal\/\d+-observation\.json$/, `journal/${String(sequence).padStart(4, "0")}-observation.json`);
      duplicate.payload.sequence = sequence;
      duplicate.payload.domain_record_sha256s = [];
      records.push(rehash(duplicate));
      return relinkJournals(records);
    },
  },
  {
    id: "unconsumed_map_observation_domain",
    trace: failureTrace,
    expected_rejection: "MAP_OBSERVATION_ONE_SHOT_INVALID",
    mutate(records) {
      const receiptPath = mapObservation(records).receipt.path;
      return ordered(records.filter((record) => record.path !== receiptPath));
    },
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
  schema: "tt-supervised-executor-map-failure-regressions-v13",
  protocol,
  status: failed.length === 0 ? "PASS" : "FAIL",
  evidence_status: ["MODEL-BOUND", "ZERO-RUN"],
  source_artifact: { path: artifactPath, sha256: digest(artifactBytes) },
  validator_snapshots: {
    harness: { path: "run_map_failure_regressions_v13.mjs", sha256: digest(readFileSync("run_map_failure_regressions_v13.mjs")) },
    builder: { path: "build_v13_closed_kernel.mjs", sha256: digest(readFileSync("build_v13_closed_kernel.mjs")) },
    verifier: { path: "verify_v13_closed_kernel.mjs", sha256: digest(readFileSync("verify_v13_closed_kernel.mjs")) },
  },
  case_count: results.length,
  pass_count: results.filter((result) => result.pass).length,
  results,
  limitations: [
    "These controls cover only the V13 typed private-map-open observation boundary and E0 map-failure vertical slice.",
    "Mutations establish the preregistered first rejection; downstream selector sources and actions are not causally regenerated, so a case may retain secondary rejection causes.",
    "They do not establish restart, process reconciliation, infrastructure finalization, or selector rule totality.",
    "The observation gateway is replayed as typed finite-model evidence; OS truthfulness and crash atomicity remain outside the model.",
    "No runtime or cryptanalytic campaign was executed.",
  ],
};
writeFileSync("map-failure-regressions-v13.json", `${JSON.stringify(receipt, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({
  status: receipt.status,
  receipt: "map-failure-regressions-v13.json",
  receipt_sha256: digest(readFileSync("map-failure-regressions-v13.json")),
  cases: results.length,
  passes: receipt.pass_count,
  failed: failed.map((result) => ({ id: result.id, expected: result.expected_rejection, builder: result.builder_decision.rejection, verifier: result.verifier_decision.rejection })),
})}\n`);
if (failed.length > 0) process.exitCode = 1;
