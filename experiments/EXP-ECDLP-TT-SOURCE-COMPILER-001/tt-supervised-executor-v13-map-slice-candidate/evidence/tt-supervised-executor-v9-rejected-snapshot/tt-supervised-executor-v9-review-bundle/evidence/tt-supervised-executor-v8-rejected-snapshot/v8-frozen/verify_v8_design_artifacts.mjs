import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/8";
const transitionName = "supervised-executor-transition-matrix-v7.json";
const controlName = "supervised-executor-control-matrix-v7.json";
const builderName = "build_v8_design_artifacts.mjs";
const verifierName = "verify_v8_design_artifacts.mjs";
const contractName = "supervised-executor-contract-v8.md";
const topologyName = "supervised-executor-topology-decision-v7.md";
const snapshotNames = [transitionName, controlName, builderName, verifierName, contractName, topologyName];
const byteSnapshots = Object.fromEntries(snapshotNames.map((name) => [name, readFileSync(join(here, name))]));
const transition = JSON.parse(byteSnapshots[transitionName].toString("utf8"));
const control = JSON.parse(byteSnapshots[controlName].toString("utf8"));
const checks = [];

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function sha256(value) {
  const bytes = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha256").update(bytes).digest("hex");
}

function sha1(value) {
  const bytes = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha1").update(bytes).digest("hex");
}

function clone(value) {
  return structuredClone(value);
}

function same(left, right) {
  return canonical(left) === canonical(right);
}

function fail(code, detail = "") {
  const error = new Error(`${code}${detail ? `: ${detail}` : ""}`);
  error.code = code;
  throw error;
}

function check(name, condition, detail) {
  if (!condition) fail("CHECK_FAILED", `${name}: ${detail}`);
  checks.push({ name, status: "pass", detail });
}

function conditionMatches(actual, expected) {
  return Array.isArray(expected) ? expected.some((candidate) => same(candidate, actual)) : same(actual, expected);
}

function getPath(root, path) {
  return path.split(".").reduce((value, key) => value?.[key], root);
}

function setPath(root, path, value) {
  const keys = path.split(".");
  let cursor = root;
  for (const key of keys.slice(0, -1)) cursor = cursor[key];
  cursor[keys.at(-1)] = value;
}

const phaseOrder = ["P0", "P1", "P2", "P3", "P4", "P5", "E0"];
const attemptOrdinals = Array.from({ length: 33 }, (_, index) => `A${index}`);
const recoveryOrdinals = attemptOrdinals.slice(1);
const rules = transition.rules;
const schemas = transition.source_schemas;
const rulesBySchema = Object.fromEntries(Object.keys(schemas).map((schemaId) => [schemaId, rules.filter((rule) => rule.source_schema === schemaId)]));

function phaseId(source) {
  if (source.evaluation_context === "e0_private_map" || source.e0_mode) return "E0";
  if (typeof source.phase_mode === "string") return source.phase_mode.split(":")[0];
  if (phaseOrder.includes(source.target_phase)) return source.target_phase;
  fail("PHASE_IDENTITY_MISSING", source.variant || source.evaluation_context);
}

function attemptOrdinal(source) {
  if (attemptOrdinals.includes(source.attempt_identity?.ordinal)) return source.attempt_identity.ordinal;
  if (attemptOrdinals.includes(source.attempt_ordinal)) return source.attempt_ordinal;
  if (attemptOrdinals.includes(source.admission_ordinal)) return source.admission_ordinal;
  if (recoveryOrdinals.includes(source.recovery_budget_state?.next_ordinal)) return source.recovery_budget_state.next_ordinal;
  if (source.run_mode === "normal" || source.admission_kind === "normal") return "A0";
  fail("ATTEMPT_ORDINAL_MISSING", source.variant || source.evaluation_context);
}

function privateMapState(source) {
  return source.private_map_state || source.private_map_identity?.state;
}

function privateMapBinding(source) {
  return source.private_map_binding || source.private_map_identity?.binding;
}

function validateSource(schemaId, source) {
  const schema = schemas[schemaId];
  if (!schema) return { ok: false, reason: "SCHEMA_UNKNOWN" };
  if (!same(Object.keys(source).sort(), schema.permitted)) return { ok: false, reason: "SCHEMA_KEYS_MISMATCH" };
  for (const [field, expected] of Object.entries(schema.fixed)) if (!conditionMatches(source[field], expected)) return { ok: false, reason: `SCHEMA_FIXED_MISMATCH:${field}` };
  for (const [field, domain] of Object.entries(schema.domains)) if (!domain.some((value) => same(value, source[field]))) return { ok: false, reason: `SCHEMA_DOMAIN_MISMATCH:${field}` };
  if (schemaId === "locked_entry_ineligible_v3" && source.budget_relation === "exhausted_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps) || source.recovery_slots_consumed !== source.approval_maximum_recovery_bootstraps || source.recovery_budget !== "exhausted") return { ok: false, reason: "SCHEMA_BUDGET_EXHAUSTION_RELATION_INVALID" };
  }
  if (schemaId === "locked_recovery_eligible_v3" && source.budget_relation === "available_exact") {
    const budget = source.recovery_budget_state;
    if (!budget || !Number.isInteger(budget.maximum) || !Number.isInteger(budget.consumed) || budget.maximum < 1 || budget.maximum > 32 || budget.consumed < 0 || budget.consumed >= budget.maximum || budget.status !== "available" || budget.next_ordinal !== `A${budget.consumed + 1}` || source.recovery_budget !== "available") return { ok: false, reason: "SCHEMA_BUDGET_AVAILABILITY_RELATION_INVALID" };
  }
  if (schemaId === "locked_dangling_admission_v2") {
    const valid = source.admission_ordinal === "invalid" || (source.admission_kind === "normal" && source.admission_ordinal === "A0") || (source.admission_kind === "recovery" && recoveryOrdinals.includes(source.admission_ordinal));
    if (!valid) return { ok: false, reason: "SCHEMA_DANGLING_ADMISSION_ORDINAL_INVALID" };
  }
  if (schemaId === "attempt_admission_v2") {
    const valid = source.admission_ordinal === "invalid" || (source.run_mode === "normal" && source.admission_kind === "normal" && source.admission_ordinal === "A0") || (source.run_mode === "recovery" && source.admission_kind === "recovery" && recoveryOrdinals.includes(source.admission_ordinal));
    if (!valid) return { ok: false, reason: "SCHEMA_ATTEMPT_ADMISSION_ORDINAL_INVALID" };
  }
  if (schemaId === "meter_finalization_v3") {
    const identity = source.attempt_identity;
    const valid = identity && ((identity.run_mode === "normal" && identity.admission_kind === "normal" && identity.ordinal === "A0") || (identity.run_mode === "recovery" && identity.admission_kind === "recovery" && recoveryOrdinals.includes(identity.ordinal)));
    if (!valid) return { ok: false, reason: "SCHEMA_METER_ATTEMPT_RELATION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v3") {
    const map = source.private_map_identity;
    const valid = source.phase_mode === "E0:evaluate" ? map?.state === "MAP_OPENED_RECEIPT_DURABLE" && map.binding === "valid_current" && map.relation === "valid" : map?.state === "not_applicable" && map.binding === "not_applicable" && map.relation === "valid";
    if (!valid) return { ok: false, reason: "SCHEMA_RECOVERY_PRIVATE_MAP_RELATION_INVALID" };
  }
  const ordinalSchemas = new Set(["live_candidate_action_v3", "live_e0_evaluate_action_v3", "live_transition_candidate_v3", "live_transition_e0_evaluate_v3", "campaign_progression_v3", "e0_private_map_v3", "git_commit_validation_v2"]);
  if (ordinalSchemas.has(schemaId)) {
    const valid = (source.run_mode === "normal" && source.attempt_ordinal === "A0") || (source.run_mode === "recovery" && recoveryOrdinals.includes(source.attempt_ordinal));
    if (!valid) return { ok: false, reason: "SCHEMA_RUN_ATTEMPT_ORDINAL_INVALID" };
  }
  if (["live_candidate_action_v3", "live_e0_evaluate_action_v3"].includes(schemaId)) {
    const valid = source.state === "REAPED" ? [true, false].includes(source.result_disposition) : source.result_disposition === "not_applicable";
    if (!valid) return { ok: false, reason: "SCHEMA_LIVE_RESULT_DISPOSITION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v3") {
    const valid = source.state === "REAPED" ? [true, false].includes(source.recoverable_result) : source.recoverable_result === "not_applicable";
    if (!valid) return { ok: false, reason: "SCHEMA_RECOVERY_RESULT_DISPOSITION_INVALID" };
  }
  return { ok: true, reason: "SCHEMA_VALID" };
}

function predicateMatches(source, predicate) {
  return Object.entries(predicate).every(([field, expected]) => conditionMatches(source[field], expected));
}

function selectRule(schemaId, source) {
  const validation = validateSource(schemaId, source);
  if (!validation.ok) return { selected_rule: "SCHEMA_REJECT", reason: validation.reason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" };
  const matches = rulesBySchema[schemaId].filter((rule) => predicateMatches(source, rule.compiled_predicate));
  if (matches.length > 1) fail("RULE_OVERLAP", `${schemaId}:${matches.map((rule) => rule.id).join(",")}`);
  return matches[0] || { selected_rule: "DEFAULT", reason: "STATE_PRODUCT_UNMATCHED", state: "INFRASTRUCTURE_REQUESTED", next_action: "request_infrastructure_failure", next_context: "meter_finalization" };
}

function isSafeNonnegativeInteger(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function validateResourceInput(input) {
  if (input === null || typeof input !== "object" || Array.isArray(input)) return { ok: false, reason: "RESOURCE_INPUT_NOT_OBJECT" };
  if (!same(Object.keys(input).sort(), ["attempts", "memory_vertices", "overlap_policy", "possible_overlap_edges", "schema"])) return { ok: false, reason: "RESOURCE_INPUT_KEYS_MISMATCH" };
  if (input.schema !== "tt-supervised-resource-input-v2") return { ok: false, reason: "RESOURCE_INPUT_SCHEMA_INVALID" };
  if (input.overlap_policy !== "conservative_possible_overlap_complete") return { ok: false, reason: "RESOURCE_OVERLAP_POLICY_INVALID" };
  if (!Array.isArray(input.attempts) || input.attempts.length === 0) return { ok: false, reason: "RESOURCE_ATTEMPTS_INVALID" };
  const attemptIds = new Set();
  const attemptKeys = ["bootstrap_cap", "bootstrap_observed", "disk_charge", "id", "io_charge", "meter_observed_preterminal", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap"];
  for (const attempt of input.attempts) {
    if (attempt === null || typeof attempt !== "object" || !same(Object.keys(attempt).sort(), attemptKeys)) return { ok: false, reason: "RESOURCE_ATTEMPT_KEYS_INVALID" };
    if (!attemptOrdinals.includes(attempt.id) || attemptIds.has(attempt.id)) return { ok: false, reason: "RESOURCE_ATTEMPT_ID_INVALID" };
    attemptIds.add(attempt.id);
    for (const field of ["bootstrap_cap", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge"]) if (!isSafeNonnegativeInteger(attempt[field])) return { ok: false, reason: "RESOURCE_ATTEMPT_CHARGE_INVALID" };
    for (const [observedField, capField] of [["bootstrap_observed", "bootstrap_cap"], ["meter_observed_preterminal", "meter_preterminal_cap"]]) {
      const observed = attempt[observedField];
      if (observed !== null && (!isSafeNonnegativeInteger(observed) || observed > attempt[capField])) return { ok: false, reason: "RESOURCE_OBSERVATION_INVALID" };
    }
  }
  if (!Array.isArray(input.memory_vertices) || input.memory_vertices.length === 0) return { ok: false, reason: "RESOURCE_MEMORY_VERTICES_INVALID" };
  const vertexIds = new Set();
  for (const vertex of input.memory_vertices) {
    if (vertex === null || typeof vertex !== "object" || !same(Object.keys(vertex).sort(), ["capacity", "id"])) return { ok: false, reason: "RESOURCE_MEMORY_VERTEX_KEYS_INVALID" };
    if (typeof vertex.id !== "string" || vertex.id.length === 0 || vertexIds.has(vertex.id) || !isSafeNonnegativeInteger(vertex.capacity)) return { ok: false, reason: "RESOURCE_MEMORY_VERTEX_INVALID" };
    vertexIds.add(vertex.id);
  }
  if (!Array.isArray(input.possible_overlap_edges)) return { ok: false, reason: "RESOURCE_OVERLAP_EDGES_INVALID" };
  const edges = new Set();
  for (const edge of input.possible_overlap_edges) {
    if (!Array.isArray(edge) || edge.length !== 2 || !vertexIds.has(edge[0]) || !vertexIds.has(edge[1]) || edge[0] === edge[1]) return { ok: false, reason: "RESOURCE_OVERLAP_EDGE_ENDPOINT_INVALID" };
    const key = [...edge].sort().join("\0");
    if (edges.has(key)) return { ok: false, reason: "RESOURCE_OVERLAP_EDGE_DUPLICATE" };
    edges.add(key);
  }
  return { ok: true, reason: "RESOURCE_INPUT_VALID" };
}

function computeResources(input) {
  const validation = validateResourceInput(input);
  if (!validation.ok) fail("RESOURCE_INPUT_INVALID", validation.reason);
  const cpu = input.attempts.reduce((sum, attempt) => sum + (attempt.bootstrap_observed ?? attempt.bootstrap_cap) + (attempt.meter_observed_preterminal ?? attempt.meter_preterminal_cap) + attempt.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, attempt) => sum + attempt.wall_cap, 0);
  const io = input.attempts.reduce((sum, attempt) => sum + attempt.io_charge, 0);
  const disk = input.attempts.reduce((sum, attempt) => sum + attempt.disk_charge, 0);
  const adjacency = Object.fromEntries(input.memory_vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [left, right] of input.possible_overlap_edges) { adjacency[left].add(right); adjacency[right].add(left); }
  const seen = new Set();
  const components = [];
  for (const vertex of input.memory_vertices) {
    if (seen.has(vertex.id)) continue;
    const stack = [vertex.id];
    const members = [];
    let charge = 0;
    while (stack.length) {
      const id = stack.pop();
      if (seen.has(id)) continue;
      seen.add(id);
      members.push(id);
      charge += input.memory_vertices.find((candidate) => candidate.id === id).capacity;
      for (const neighbor of adjacency[id]) stack.push(neighbor);
    }
    components.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(0, ...components.map((component) => component.charge)), wall, io, disk, memory_components: components };
}

function gitObjectOid(type, content) {
  const bytes = Buffer.from(content, "utf8");
  return sha1(Buffer.concat([Buffer.from(`${type} ${bytes.length}\0`, "utf8"), bytes]));
}

function predecessorPhase(phase) {
  const index = phaseOrder.indexOf(phase);
  return index > 0 ? phaseOrder[index - 1] : null;
}

function gitIntentPayload(source) {
  const phase = phaseId(source);
  const predecessor = predecessorPhase(phase);
  return {
    schema: "tt-supervised-git-intent-v2",
    phase,
    attempt_ordinal: attemptOrdinal(source),
    tree_oid: sha1(`tree:${phase}:public-artifacts`),
    parent_oid: predecessor === null ? null : sha1(`commit:${predecessor}:expected-parent`),
    intended_ref: "refs/autolab/supervised-campaign",
    message: `record supervised phase ${phase}`,
    self_exclusion: "commit_oid_forbidden",
  };
}

function gitCommitBytes(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
}

function durableRecord(path, recordType, payload, producer) {
  const body = { schema: "tt-supervised-durable-record-v2", path, record_type: recordType, payload, producer };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

const counterTypes = {
  root_admissions: ["normal_admission", "recovery_admission"],
  root_attempt_starts: ["attempt_start"],
  normal_consumptions: ["normal_admission"],
  recovery_slots: ["recovery_admission"],
  phase_reservations: ["candidate_phase_reservation", "evaluator_phase_reservation"],
  candidate_phase_reservations: ["candidate_phase_reservation"],
  evaluator_phase_reservations: ["evaluator_phase_reservation"],
  phase_spawns: ["phase_spawn"],
  phase_reaps: ["phase_reap"],
  commit_intents: ["commit_intent"],
  commit_objects: ["commit_object"],
  ref_cas_attempts: ["ref_cas_attempt"],
  committed_phases: ["committed_phase"],
  meter_finalizations: ["attempt_end"],
};

function validateUniverse(records) {
  const paths = new Set();
  const logicalKeys = new Set();
  for (const record of records) {
    if (paths.has(record.path)) fail("DUPLICATE_DURABLE_PATH", record.path);
    paths.add(record.path);
    const { canonical_bytes: bytes, sha256: digest, ...body } = record;
    if (canonical(body) !== bytes || sha256(bytes) !== digest || record.schema !== "tt-supervised-durable-record-v2") fail("DURABLE_RECORD_BYTES_INVALID", record.path);
    const phaseMatch = record.path.match(/\/phases\/(P[0-5]|E0)\//);
    if (phaseMatch && record.payload.phase !== phaseMatch[1]) fail("PHASE_PATH_PAYLOAD_MISMATCH", record.path);
    const attemptMatch = record.path.match(/\/attempts\/(A(?:0|[1-9][0-9]*))\//);
    if (attemptMatch && (record.payload.ordinal ?? record.payload.attempt_ordinal) !== attemptMatch[1]) fail("ATTEMPT_PATH_PAYLOAD_MISMATCH", record.path);
    const admissionMatch = record.path.match(/\/admissions\/(A(?:0|[1-9][0-9]*))\.json$/);
    if (admissionMatch && record.payload.ordinal !== admissionMatch[1]) fail("ADMISSION_PATH_PAYLOAD_MISMATCH", record.path);
    let identity = record.path;
    if (["normal_admission", "recovery_admission", "attempt_start", "attempt_end", "resource_receipt", "launch_identity", "kernel_process_observation"].includes(record.record_type)) identity = record.payload.ordinal || record.payload.attempt_ordinal;
    if (["candidate_phase_reservation", "evaluator_phase_reservation", "launch_intent", "phase_spawn", "phase_reap", "phase_result", "phase_content", "phase_terminal", "commit_intent", "commit_object", "ref_observation", "ref_cas_attempt", "committed_phase", "private_map_open_intent", "private_map_opened_receipt", "root_crash_observation"].includes(record.record_type)) identity = record.payload.phase;
    if (["campaign_terminal", "capability_receipt", "resource_measurement"].includes(record.record_type)) identity = "singleton";
    const logicalKey = `${record.record_type}:${identity}`;
    if (logicalKeys.has(logicalKey)) fail("DUPLICATE_LOGICAL_RECORD", logicalKey);
    logicalKeys.add(logicalKey);
  }
  const admissions = new Map();
  for (const record of records.filter((row) => ["normal_admission", "recovery_admission"].includes(row.record_type))) {
    const ordinal = record.payload.ordinal;
    if (!attemptOrdinals.includes(ordinal) || (record.record_type === "normal_admission" && ordinal !== "A0") || (record.record_type === "recovery_admission" && ordinal === "A0") || admissions.has(ordinal)) fail("ADMISSION_IDENTITY_INVALID", record.path);
    admissions.set(ordinal, record);
  }
  const starts = new Set();
  for (const record of records.filter((row) => row.record_type === "attempt_start")) {
    const ordinal = record.payload.ordinal;
    const admission = admissions.get(ordinal);
    if (!admission || starts.has(ordinal) || record.payload.admission_ordinal !== ordinal || record.payload.admission_sha256 !== admission.sha256) fail("ATTEMPT_START_LINKAGE_INVALID", record.path);
    starts.add(ordinal);
  }
  for (const record of records.filter((row) => row.record_type === "launch_intent")) {
    const reservation = records.find((row) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(row.record_type) && row.sha256 === record.payload.reservation_sha256);
    const capability = records.find((row) => row.record_type === "capability_receipt" && row.sha256 === record.payload.capability_receipt_sha256);
    if (!reservation || reservation.payload.phase !== record.payload.phase || !capability || !attemptOrdinals.includes(record.payload.attempt_ordinal)) fail("LAUNCH_INTENT_LINKAGE_INVALID", record.path);
    if (record.payload.phase_mode === "E0:evaluate" && !records.some((row) => row.record_type === "private_map_opened_receipt" && row.sha256 === record.payload.private_map_receipt_sha256)) fail("E0_LAUNCH_MAP_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "phase_spawn")) {
    const intent = records.find((row) => row.record_type === "launch_intent" && row.sha256 === record.payload.launch_intent_sha256);
    if (!intent || intent.payload.phase !== record.payload.phase || !["pid_returned", "spawn_error"].includes(record.payload.outcome)) fail("PHASE_SPAWN_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "phase_reap")) {
    const spawn = records.find((row) => row.record_type === "phase_spawn" && row.sha256 === record.payload.phase_spawn_sha256);
    if (!spawn || spawn.payload.phase !== record.payload.phase || record.payload.outcome !== "exited") fail("PHASE_REAP_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "phase_result")) {
    const reap = records.find((row) => row.record_type === "phase_reap" && row.sha256 === record.payload.phase_reap_sha256);
    if (!reap || reap.payload.phase !== record.payload.phase || record.payload.bounded !== true || typeof record.payload.recovery !== "boolean") fail("PHASE_RESULT_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "phase_content")) {
    const result = records.find((row) => row.record_type === "phase_result" && row.sha256 === record.payload.phase_result_sha256);
    if (!result || result.payload.phase !== record.payload.phase || !/^[0-9a-f]{64}$/.test(record.payload.content_sha256 || "")) fail("PHASE_CONTENT_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "phase_terminal")) {
    const predecessorDigest = record.payload.predecessor_sha256 || record.payload.open_intent_sha256;
    const predecessor = records.find((row) => row.sha256 === predecessorDigest && row.payload.phase === record.payload.phase);
    if (!predecessor || !["candidate_phase_reservation", "evaluator_phase_reservation", "private_map_open_intent", "phase_spawn", "phase_reap", "phase_content"].includes(predecessor.record_type)) fail("PHASE_TERMINAL_LINKAGE_INVALID", record.path);
    if (!["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"].includes(record.payload.outcome)) fail("PHASE_TERMINAL_OUTCOME_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "private_map_open_intent")) {
    if (!records.some((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256)) fail("PRIVATE_MAP_INTENT_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "private_map_opened_receipt")) {
    const reservation = records.find((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256);
    const intent = records.find((row) => row.record_type === "private_map_open_intent" && row.sha256 === record.payload.open_intent_sha256);
    if (!reservation || !intent) fail("PRIVATE_MAP_RECEIPT_LINKAGE_INVALID", record.path);
  }
  for (const record of records.filter((row) => row.record_type === "kernel_process_observation")) {
    const identity = records.find((row) => row.record_type === "launch_identity" && row.sha256 === record.payload.launch_identity_sha256);
    if (!identity || identity.payload.attempt_ordinal !== record.payload.attempt_ordinal) fail("KERNEL_OBSERVATION_LINKAGE_INVALID", record.path);
  }
  for (const measurement of records.filter((row) => row.record_type === "resource_measurement")) {
    const validation = validateResourceInput(measurement.payload.input);
    const result = validation.ok ? computeResources(measurement.payload.input) : null;
    if (!validation.ok || measurement.payload.schema !== "tt-supervised-resource-measurement-v2" || measurement.payload.input_sha256 !== sha256(measurement.payload.input) || !same(measurement.payload.result, result) || measurement.payload.result_sha256 !== sha256(result) || measurement.payload.policy !== measurement.payload.input.overlap_policy) fail("RESOURCE_MEASUREMENT_INVALID", measurement.path);
  }
  for (const receipt of records.filter((row) => row.record_type === "resource_receipt")) {
    const measurement = records.find((row) => row.record_type === "resource_measurement" && row.sha256 === receipt.payload.measurement_sha256);
    if (!measurement || receipt.payload.input_sha256 !== measurement.payload.input_sha256 || receipt.payload.result_sha256 !== measurement.payload.result_sha256 || !same(receipt.payload.result, measurement.payload.result)) fail("RESOURCE_RECEIPT_LINKAGE_INVALID", receipt.path);
  }
  for (const object of records.filter((row) => row.record_type === "commit_object")) {
    const intent = records.find((row) => row.record_type === "commit_intent" && row.sha256 === object.payload.intent_sha256);
    if (!intent || Object.hasOwn(intent.payload, "forbidden_commit_oid")) fail("COMMIT_OBJECT_INTENT_INVALID", object.path);
    const bytes = gitCommitBytes(intent.payload);
    if (object.payload.commit_bytes !== bytes || object.payload.oid !== gitObjectOid("commit", bytes) || object.payload.tree_oid !== intent.payload.tree_oid || object.payload.parent_oid !== intent.payload.parent_oid) fail("COMMIT_OBJECT_BYTES_INVALID", object.path);
  }
  for (const cas of records.filter((row) => row.record_type === "ref_cas_attempt")) {
    const object = records.find((row) => row.record_type === "commit_object" && row.sha256 === cas.payload.commit_object_sha256);
    const observation = records.find((row) => row.record_type === "ref_observation" && row.sha256 === cas.payload.ref_observation_sha256);
    if (!object || !observation || cas.payload.new_oid !== object.payload.oid || cas.payload.expected_old_oid !== observation.payload.observed_oid || !["applied", "conflict"].includes(cas.payload.outcome)) fail("CAS_LINKAGE_INVALID", cas.path);
  }
  for (const committed of records.filter((row) => row.record_type === "committed_phase")) {
    const object = records.find((row) => row.record_type === "commit_object" && row.sha256 === committed.payload.commit_object_sha256);
    const cas = records.find((row) => row.record_type === "ref_cas_attempt" && row.sha256 === committed.payload.ref_cas_sha256);
    if (!object || !cas || cas.payload.outcome !== "applied" || committed.payload.commit_oid !== object.payload.oid) fail("COMMITTED_PHASE_LINKAGE_INVALID", committed.path);
  }
  for (const terminal of records.filter((row) => row.record_type === "campaign_terminal")) {
    const resource = records.find((row) => row.record_type === "resource_receipt" && row.sha256 === terminal.payload.resource_receipt_sha256);
    const end = records.find((row) => row.record_type === "attempt_end" && row.sha256 === terminal.payload.attempt_end_sha256);
    if (!resource || !end || resource.payload.ordinal !== end.payload.ordinal) fail("CAMPAIGN_TERMINAL_LINKAGE_INVALID", terminal.path);
  }
}

function deriveCounterSnapshot(records) {
  validateUniverse(records);
  const evidence = Object.fromEntries(Object.entries(counterTypes).map(([counter, types]) => [counter, records.filter((record) => types.includes(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }))]));
  const values = Object.fromEntries(Object.entries(evidence).map(([counter, rows]) => [counter, rows.length]));
  const countable = new Set(Object.values(counterTypes).flat());
  const noncounter = records.filter((record) => !countable.has(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }));
  const covered = new Set([...Object.values(evidence).flat(), ...noncounter].map((row) => `${row.path}:${row.sha256}`));
  if (covered.size !== records.length) fail("COUNTER_UNIVERSE_COVERAGE_INVALID");
  return { schema: "tt-supervised-counter-snapshot-v3", values, counter_evidence: evidence, noncounter_records: noncounter, complete_universe_sha256: sha256(records), counter_evidence_sha256: sha256(evidence), universe_record_count: records.length };
}

function deriveGitEvidence(source, records) {
  const phase = phaseId(source);
  const expectedIntent = gitIntentPayload(source);
  const intent = records.find((record) => record.record_type === "commit_intent" && record.payload.phase === phase);
  let commitIntentRelation = "absent";
  if (intent) commitIntentRelation = Object.hasOwn(intent.payload, "forbidden_commit_oid") ? "invalid_self_including" : same(intent.payload, expectedIntent) ? "valid_self_excluding" : "invalid";
  const object = records.find((record) => record.record_type === "commit_object" && record.payload.phase === phase);
  let commitObjectState = "absent";
  if (object) {
    const bytes = gitCommitBytes(expectedIntent);
    const exact = intent && commitIntentRelation === "valid_self_excluding" && object.payload.intent_sha256 === intent.sha256 && object.payload.commit_bytes === bytes && object.payload.oid === gitObjectOid("commit", bytes) && object.payload.tree_oid === expectedIntent.tree_oid && object.payload.parent_oid === expectedIntent.parent_oid;
    commitObjectState = exact ? "exact" : "invalid";
  }
  const observation = records.find((record) => record.record_type === "ref_observation" && record.payload.phase === phase);
  let refRelation = "invalid";
  if (observation) {
    if (phase === "P0" && observation.payload.observed_oid === null) refRelation = "absent_initial";
    else if (phase !== "P0" && observation.payload.observed_oid === expectedIntent.parent_oid) refRelation = "at_parent";
    else if (/^[0-9a-f]{40}$/.test(observation.payload.observed_oid || "")) refRelation = "other";
  }
  const cas = records.find((record) => record.record_type === "ref_cas_attempt" && record.payload.phase === phase);
  let casStatus = "not_attempted";
  if (cas) {
    const linked = object && observation && cas.payload.commit_object_sha256 === object.sha256 && cas.payload.ref_observation_sha256 === observation.sha256 && cas.payload.new_oid === object.payload.oid && cas.payload.expected_old_oid === observation.payload.observed_oid;
    casStatus = linked && ["applied", "conflict"].includes(cas.payload.outcome) ? cas.payload.outcome : "invalid";
  }
  return { commit_intent_relation: commitIntentRelation, commit_object_state: commitObjectState, ref_relation: refRelation, cas_status: casStatus };
}

function compileSourceEvidence(schemaId, source, records) {
  const compiled = clone(source);
  const mutations = [];
  if (schemaId === "git_commit_validation_v2") {
    for (const [field, value] of Object.entries(deriveGitEvidence(source, records))) {
      if (!same(compiled[field], value)) mutations.push({ path: `source.${field}`, before: clone(compiled[field]), after: clone(value), derivation: "literal_git_records" });
      compiled[field] = value;
    }
  }
  return { compiled, mutations };
}

const eventRecordTypes = {
  reservation_durable: ["candidate_phase_reservation", "evaluator_phase_reservation"],
  launch_intent_durable: ["launch_intent"],
  spawn_returned_error: ["phase_spawn"], spawn_returned_pid: ["phase_spawn"],
  spawn_failure_terminal_durable: ["phase_terminal"], runtime_failure_terminal_durable: ["phase_terminal"],
  child_reaped: ["phase_reap"], bounded_result_retained: ["phase_result"], content_durable: ["phase_content"],
  valid_terminal_durable: ["phase_terminal"], validation_failure_terminal_durable: ["phase_terminal"],
  commit_intent_durable: ["commit_intent"], commit_object_exact: ["commit_object"],
  initial_ref_cas_applied: ["ref_cas_attempt"], existing_ref_cas_applied: ["ref_cas_attempt"],
  commit_reparsed_exact: ["committed_phase"], root_crashed: ["root_crash_observation"],
};

function exactEventReceipt(source, records) {
  if (!source.event || source.event_record_binding !== "valid_current") return null;
  const phase = phaseId(source);
  const ordinal = attemptOrdinal(source);
  const byType = (type, predicate = () => true) => records.find((record) => record.record_type === type && record.payload.phase === phase && predicate(record));
  let record = null;
  if (source.event === "reservation_durable") record = records.find((candidate) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(candidate.record_type) && candidate.payload.phase === phase);
  if (source.event === "launch_intent_durable") record = byType("launch_intent", (candidate) => candidate.payload.phase_mode === source.phase_mode && candidate.payload.attempt_ordinal === ordinal);
  if (source.event === "spawn_returned_error") record = byType("phase_spawn", (candidate) => candidate.payload.outcome === "spawn_error");
  if (source.event === "spawn_returned_pid") record = byType("phase_spawn", (candidate) => candidate.payload.outcome === "pid_returned");
  if (["spawn_failure_terminal_durable", "runtime_failure_terminal_durable", "validation_failure_terminal_durable"].includes(source.event)) record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_HARNESS_FAILURE");
  if (source.event === "child_reaped") record = byType("phase_reap", (candidate) => candidate.payload.outcome === "exited");
  if (source.event === "bounded_result_retained") record = byType("phase_result", (candidate) => candidate.payload.bounded === true);
  if (source.event === "content_durable") record = byType("phase_content");
  if (source.event === "valid_terminal_durable") record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_VALID_OUTCOME");
  if (source.event === "commit_intent_durable") record = byType("commit_intent", (candidate) => same(candidate.payload, gitIntentPayload(source)));
  if (source.event === "commit_object_exact") record = byType("commit_object");
  if (source.event === "initial_ref_cas_applied") record = byType("ref_cas_attempt", (candidate) => candidate.payload.outcome === "applied" && candidate.payload.expected_old_oid === null);
  if (source.event === "existing_ref_cas_applied") record = byType("ref_cas_attempt", (candidate) => candidate.payload.outcome === "applied" && candidate.payload.expected_old_oid !== null);
  if (source.event === "commit_reparsed_exact") record = byType("committed_phase");
  if (source.event === "root_crashed") record = byType("root_crash_observation", (candidate) => candidate.payload.attempt_ordinal === ordinal && candidate.payload.observation === "root_crashed");
  return record ? { event: source.event, path: record.path, sha256: record.sha256, record_type: record.record_type } : null;
}

function evidenceConsistency(source, records) {
  try { validateUniverse(records); } catch (error) { return `EVIDENCE_UNIVERSE_INVALID:${error.code || error.message}`; }
  const has = (type) => records.some((record) => record.record_type === type);
  const hasPhase = (type, phase = phaseId(source)) => records.some((record) => record.record_type === type && record.payload.phase === phase);
  let ordinal = null;
  try { ordinal = attemptOrdinal(source); } catch {}
  const admissionType = source.admission_kind === "recovery" || source.attempt_identity?.admission_kind === "recovery" || source.run_mode === "recovery" ? "recovery_admission" : "normal_admission";
  if (["valid_current", "valid_unstarted"].includes(source.admission_record) && !records.some((record) => record.record_type === admissionType && record.payload.ordinal === ordinal)) return "EVIDENCE_ADMISSION_MISSING";
  if (source.attempt_record === "valid_current" && !records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === ordinal)) return "EVIDENCE_CURRENT_ATTEMPT_START_MISSING";
  if (source.linked_attempt_record === "durable" && !records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === ordinal)) return "EVIDENCE_ATTEMPT_START_ORDINAL_MISSING";
  if (source.resource_measurement === "valid_current" && !has("resource_measurement")) return "EVIDENCE_RESOURCE_MEASUREMENT_MISSING";
  if (source.resource_receipt === "durable" && !records.some((record) => record.record_type === "resource_receipt" && record.payload.ordinal === ordinal)) return "EVIDENCE_RESOURCE_RECEIPT_MISSING";
  if (source.attempt_end === "durable" && !records.some((record) => record.record_type === "attempt_end" && record.payload.ordinal === ordinal)) return "EVIDENCE_ATTEMPT_END_MISSING";
  if (source.capability_receipt === "valid_current" && !has("capability_receipt")) return "EVIDENCE_CAPABILITY_RECEIPT_MISSING";
  if (source.launch_identity_evidence === "complete") {
    const identity = records.find((record) => record.record_type === "launch_identity" && record.payload.attempt_ordinal === ordinal);
    if (!identity) return "EVIDENCE_LAUNCH_IDENTITY_RECORD_MISSING";
    const observation = records.find((record) => record.record_type === "kernel_process_observation" && record.payload.attempt_ordinal === ordinal && record.payload.launch_identity_sha256 === identity.sha256);
    if (source.kernel_observation_evidence === "complete" && (!observation || observation.payload.observation !== source.process_absence)) return "EVIDENCE_KERNEL_OBSERVATION_RECORD_MISSING";
  }
  const mapState = source.map_state || privateMapState(source);
  if (mapState === "MAP_OPENED_RECEIPT_DURABLE" && !has("private_map_opened_receipt")) return "EVIDENCE_PRIVATE_MAP_RECEIPT_MISSING";
  if (source.evaluation_context === "e0_private_map" && !hasPhase("evaluator_phase_reservation", "E0")) return "EVIDENCE_E0_RESERVATION_MISSING";
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(mapState) && !has("private_map_open_intent")) return "EVIDENCE_PRIVATE_MAP_INTENT_MISSING";
  if (mapState === "MAP_OPEN_FAILED_DURABLE" && !hasPhase("phase_terminal", "E0")) return "EVIDENCE_PRIVATE_MAP_FAILURE_TERMINAL_MISSING";
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal) && !has("campaign_terminal")) return "EVIDENCE_CAMPAIGN_TERMINAL_MISSING";
  if (source.event_record_binding === "valid_current") {
    const receipt = exactEventReceipt(source, records);
    if (!receipt || !(eventRecordTypes[source.event] || []).includes(receipt.record_type)) return "EVIDENCE_EVENT_RECORD_MISSING_OR_INVALID";
  }
  const liveStates = transition.live_phase_protocol.states;
  if (source.state && liveStates.includes(source.state) && source.state !== "UNSEEN") {
    const phase = phaseId(source);
    if (!hasPhase(phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", phase)) return "EVIDENCE_PHASE_RESERVATION_MISSING";
    if (["LAUNCH_INTENT_DURABLE", "SPAWN_FAILED", "SPAWNED", "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("launch_intent", phase)) return "EVIDENCE_LAUNCH_INTENT_MISSING";
    if (["SPAWN_FAILED", "SPAWNED", "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("phase_spawn", phase)) return "EVIDENCE_PHASE_SPAWN_MISSING";
    if (["REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("phase_reap", phase)) return "EVIDENCE_PHASE_REAP_MISSING";
    if (["RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("phase_result", phase)) return "EVIDENCE_PHASE_RESULT_MISSING";
    if (["CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("phase_content", phase)) return "EVIDENCE_PHASE_CONTENT_MISSING";
    if (["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE", "COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("phase_terminal", phase)) return "EVIDENCE_PHASE_TERMINAL_MISSING";
    if (["COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("commit_intent", phase)) return "EVIDENCE_COMMIT_INTENT_MISSING";
    if (["COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("commit_object", phase)) return "EVIDENCE_COMMIT_OBJECT_MISSING";
    if (["REF_APPLIED", "COMMITTED"].includes(source.state) && !hasPhase("ref_cas_attempt", phase)) return "EVIDENCE_REF_CAS_MISSING";
    if (source.state === "COMMITTED" && !hasPhase("committed_phase", phase)) return "EVIDENCE_COMMITTED_PHASE_MISSING";
  }
  if (source.variant === "git_commit_validation_v2") {
    const derived = deriveGitEvidence(source, records);
    for (const field of ["commit_intent_relation", "commit_object_state", "ref_relation", "cas_status"]) if (derived[field] !== source[field]) return `EVIDENCE_GIT_DERIVATION_MISMATCH:${field}`;
  }
  if (source.last_committed_phase && source.last_committed_phase !== "none" && !records.some((record) => record.record_type === "committed_phase" && record.payload.phase === source.last_committed_phase)) return "EVIDENCE_LAST_COMMITTED_PHASE_MISSING";
  return null;
}

function applyFault(pre, fault) {
  const observed = clone(pre);
  if (fault.kind === "none") return { observed, mutations: [] };
  const mutations = [];
  if (fault.kind === "replace") {
    const before = clone(getPath(observed, fault.path));
    if (!same(before, fault.before)) fail("FAULT_BEFORE_MISMATCH", fault.path);
    setPath(observed, fault.path, clone(fault.after));
    mutations.push({ path: fault.path, before, after: clone(fault.after) });
  } else if (fault.kind === "add_source_property") {
    if (Object.hasOwn(observed.source, fault.property)) fail("FAULT_PROPERTY_EXISTS", fault.property);
    observed.source[fault.property] = clone(fault.value);
    mutations.push({ path: `source.${fault.property}`, before: "__absent__", after: clone(fault.value) });
  } else if (fault.kind === "remove_record") {
    const index = observed.records.findIndex((record) => record.path === fault.record_path);
    if (index < 0) fail("FAULT_RECORD_MISSING", fault.record_path);
    const [removed] = observed.records.splice(index, 1);
    mutations.push({ path: `records:${fault.record_path}`, before: removed.sha256, after: "__absent__" });
  } else if (fault.kind === "replace_record") {
    const index = observed.records.findIndex((record) => record.path === fault.record_path);
    if (index < 0) fail("FAULT_RECORD_MISSING", fault.record_path);
    const before = observed.records[index];
    if (before.sha256 !== fault.before_sha256 || fault.after_record.path !== fault.record_path || fault.after_record.sha256 === before.sha256) fail("FAULT_RECORD_REPLACEMENT_INVALID", fault.record_path);
    observed.records[index] = clone(fault.after_record);
    observed.records.sort((left, right) => left.path.localeCompare(right.path));
    mutations.push({ path: `records:${fault.record_path}`, before: before.sha256, after: fault.after_record.sha256 });
  } else fail("FAULT_KIND_UNKNOWN", fault.kind);
  if (same(pre, observed) || mutations.length === 0) fail("FAULT_NOT_MATERIALIZED", fault.kind);
  return { observed, mutations };
}

function actionPhaseId(action, source) {
  if (action === "reserve_P0_then_live_supervisor") return "P0";
  if (["reserve_E0_evaluate_then_private_map", "reserve_E0_close_prior_failure_then_live_supervisor"].includes(action)) return "E0";
  if (action === "reserve_successor_then_live_supervisor") {
    const index = phaseOrder.slice(0, 6).indexOf(source.last_committed_phase);
    if (index < 0 || index >= 5) fail("SUCCESSOR_PHASE_INVALID", source.last_committed_phase);
    return phaseOrder[index + 1];
  }
  return phaseId(source);
}

const actionRecordTypes = {
  reserve_normal_admission: "normal_admission", reserve_recovery_admission: "recovery_admission", write_linked_attempt_start: "attempt_start",
  reserve_P0_then_live_supervisor: "candidate_phase_reservation", reserve_successor_then_live_supervisor: "candidate_phase_reservation",
  reserve_E0_evaluate_then_private_map: "evaluator_phase_reservation", reserve_E0_close_prior_failure_then_live_supervisor: "evaluator_phase_reservation",
  create_launch_intent: "launch_intent", spawn_phase: "phase_spawn", reap_phase: "phase_reap",
  publish_harness_failure_phase_terminal: "phase_terminal", publish_quarantine_phase_terminal: "phase_terminal", reconcile_process_then_publish_quarantine_phase_terminal: "phase_terminal",
  retain_bounded_result: "phase_result", retain_recoverable_result: "phase_result", publish_runtime_failure_phase_terminal: "phase_terminal",
  publish_phase_content: "phase_content", publish_valid_or_harness_phase_terminal: "phase_terminal",
  create_commit_intent: "commit_intent", create_ledgered_commit_objects: "commit_object", cas_create_initial_ref: "ref_cas_attempt", cas_update_existing_ref: "ref_cas_attempt", reparse_exact_commit_then_progress: "committed_phase",
  write_resource_receipt_only: "resource_receipt", write_attempt_end_only: "attempt_end", publish_attested_terminal_only: "campaign_terminal", publish_infrastructure_terminal_only: "campaign_terminal",
  write_private_map_open_intent: "private_map_open_intent", write_private_map_opened_receipt: "private_map_opened_receipt", publish_map_open_harness_failure_terminal: "phase_terminal",
};

function actionRecordPath(controlId, action, source) {
  const ordinal = attemptOrdinal(source);
  const phase = () => actionPhaseId(action, source);
  if (action === "reserve_normal_admission") return `fixtures/${controlId}/admissions/A0.json`;
  if (action === "reserve_recovery_admission") return `fixtures/${controlId}/admissions/${ordinal}.json`;
  if (action === "write_linked_attempt_start") return `fixtures/${controlId}/attempts/${ordinal}/start.json`;
  if (action.includes("reserve_E0")) return `fixtures/${controlId}/phases/E0/reservation.json`;
  if (action.startsWith("reserve_")) return `fixtures/${controlId}/phases/${phase()}/reservation.json`;
  if (action === "create_launch_intent") return `fixtures/${controlId}/phases/${phase()}/launch-intent.json`;
  if (action === "spawn_phase") return `fixtures/${controlId}/phases/${phase()}/spawn.json`;
  if (action === "reap_phase") return `fixtures/${controlId}/phases/${phase()}/reap.json`;
  if (["retain_bounded_result", "retain_recoverable_result"].includes(action)) return `fixtures/${controlId}/phases/${phase()}/result.json`;
  if (action.includes("phase_terminal") || action === "publish_map_open_harness_failure_terminal") return `fixtures/${controlId}/phases/${phase()}/terminal.json`;
  if (action === "publish_phase_content") return `fixtures/${controlId}/phases/${phase()}/content.json`;
  if (action === "create_commit_intent") return `fixtures/${controlId}/phases/${phase()}/commit-intent.json`;
  if (action === "create_ledgered_commit_objects") return `fixtures/${controlId}/phases/${phase()}/commit-object.json`;
  if (action.startsWith("cas_")) return `fixtures/${controlId}/phases/${phase()}/ref-cas.json`;
  if (action === "reparse_exact_commit_then_progress") return `fixtures/${controlId}/phases/${phase()}/committed.json`;
  if (action === "write_resource_receipt_only") return `fixtures/${controlId}/attempts/${ordinal}/resource.json`;
  if (action === "write_attempt_end_only") return `fixtures/${controlId}/attempts/${ordinal}/end.json`;
  if (action.includes("terminal_only")) return `fixtures/${controlId}/campaign-terminal.json`;
  if (action === "write_private_map_open_intent") return `fixtures/${controlId}/phases/E0/private-map-intent.json`;
  if (action === "write_private_map_opened_receipt") return `fixtures/${controlId}/phases/E0/private-map-receipt.json`;
  return `fixtures/${controlId}/actions/${action}.json`;
}

function expectedAction(controlId, selection, source, records, executed) {
  if (!executed) return { records: clone(records).sort((a, b) => a.path.localeCompare(b.path)), delta: [], postState: { evaluation_context: selection.next_context, state: selection.state, selected_rule: selection.id || selection.selected_rule, reason: selection.reason, last_action: "selection_only", derived_field_patch: {} } };
  const output = clone(records).sort((a, b) => a.path.localeCompare(b.path));
  const delta = [];
  const action = selection.next_action;
  const type = actionRecordTypes[action];
  if (type) {
    const ordinal = attemptOrdinal(source);
    const phase = ["normal_admission", "recovery_admission", "attempt_start", "resource_receipt", "attempt_end", "campaign_terminal"].includes(type) ? null : actionPhaseId(action, source);
    const find = (recordType) => records.find((record) => record.record_type === recordType && (phase === null || record.payload.phase === phase));
    const admission = records.find((record) => ["normal_admission", "recovery_admission"].includes(record.record_type) && record.payload.ordinal === ordinal);
    const reservation = records.find((record) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(record.record_type) && record.payload.phase === phase);
    const launch = find("launch_intent");
    const spawn = find("phase_spawn");
    const reap = find("phase_reap");
    const result = find("phase_result");
    const content = find("phase_content");
    const measurement = records.find((record) => record.record_type === "resource_measurement");
    const resource = records.find((record) => record.record_type === "resource_receipt" && record.payload.ordinal === ordinal);
    const end = records.find((record) => record.record_type === "attempt_end" && record.payload.ordinal === ordinal);
    const capability = records.find((record) => record.record_type === "capability_receipt");
    const mapReceipt = records.find((record) => record.record_type === "private_map_opened_receipt");
    const evaluatorReservation = records.find((record) => record.record_type === "evaluator_phase_reservation" && record.payload.phase === "E0");
    const mapIntent = records.find((record) => record.record_type === "private_map_open_intent");
    let payload = null;
    if (["normal_admission", "recovery_admission"].includes(type)) payload = { ordinal };
    if (type === "attempt_start") { if (!admission) fail("ACTION_PREREQUISITE_MISSING", "admission"); payload = { ordinal, admission_ordinal: ordinal, admission_sha256: admission.sha256 }; }
    if (["candidate_phase_reservation", "evaluator_phase_reservation"].includes(type)) {
      const predecessor = records.find((record) => record.record_type === "committed_phase" && record.payload.phase === source.last_committed_phase);
      const phaseMode = phase === "E0" ? (action.includes("evaluate") ? "E0:evaluate" : "E0:close_prior_failure") : `${phase}:not_applicable`;
      payload = { phase, phase_mode: phaseMode, attempt_ordinal: ordinal, predecessor_committed_sha256: predecessor?.sha256 || null, binding: "valid_current" };
    }
    if (type === "launch_intent") { if (!reservation || !capability) fail("ACTION_PREREQUISITE_MISSING", "launch"); payload = { phase, phase_mode: source.phase_mode, attempt_ordinal: ordinal, reservation_sha256: reservation.sha256, capability_receipt_sha256: capability.sha256, private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? mapReceipt?.sha256 : null }; }
    if (type === "phase_spawn") { if (!launch) fail("ACTION_PREREQUISITE_MISSING", "launch-intent"); payload = { phase, launch_intent_sha256: launch.sha256, outcome: "pid_returned" }; }
    if (type === "phase_reap") { if (!spawn) fail("ACTION_PREREQUISITE_MISSING", "spawn"); payload = { phase, phase_spawn_sha256: spawn.sha256, outcome: "exited" }; }
    if (type === "phase_result") { if (!reap) fail("ACTION_PREREQUISITE_MISSING", "reap"); payload = { phase, phase_reap_sha256: reap.sha256, bounded: true, recovery: action === "retain_recoverable_result" }; }
    if (type === "phase_content") { if (!result) fail("ACTION_PREREQUISITE_MISSING", "result"); payload = { phase, phase_result_sha256: result.sha256, content_sha256: sha256(`content:${phase}`) }; }
    if (type === "phase_terminal") {
      const predecessor = content || reap || spawn || reservation || mapIntent;
      if (!predecessor) fail("ACTION_PREREQUISITE_MISSING", "terminal predecessor");
      payload = { phase, outcome: action.includes("quarantine") ? "TERMINAL_QUARANTINE" : action === "publish_valid_or_harness_phase_terminal" ? "TERMINAL_VALID_OUTCOME" : "TERMINAL_HARNESS_FAILURE", predecessor_sha256: predecessor.sha256 };
      if (action === "publish_map_open_harness_failure_terminal") payload = { ...payload, outcome: "TERMINAL_HARNESS_FAILURE", reason: "private_map_open_failed", syscall_error: { domain: "posix_errno", code: "EACCES" }, open_intent_sha256: mapIntent?.sha256 };
    }
    if (type === "commit_intent") payload = gitIntentPayload(source);
    if (type === "commit_object") {
      const intent = find("commit_intent");
      if (!intent) fail("ACTION_PREREQUISITE_MISSING", "commit-intent");
      const bytes = gitCommitBytes(intent.payload);
      payload = { phase, commit_bytes: bytes, oid: gitObjectOid("commit", bytes), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid, intent_sha256: intent.sha256 };
    }
    if (type === "ref_cas_attempt") {
      const intent = find("commit_intent"); const object = find("commit_object"); const observation = find("ref_observation");
      if (!intent || !object || !observation) fail("ACTION_PREREQUISITE_MISSING", "CAS inputs");
      payload = { phase, ref: intent.payload.intended_ref, expected_old_oid: observation.payload.observed_oid, new_oid: object.payload.oid, outcome: "applied", commit_object_sha256: object.sha256, ref_observation_sha256: observation.sha256 };
    }
    if (type === "committed_phase") {
      const object = find("commit_object"); const cas = find("ref_cas_attempt");
      if (!object || !cas) fail("ACTION_PREREQUISITE_MISSING", "commit/CAS");
      payload = { phase, commit_oid: object.payload.oid, commit_object_sha256: object.sha256, ref_cas_sha256: cas.sha256 };
    }
    if (type === "resource_receipt") { if (!measurement) fail("ACTION_PREREQUISITE_MISSING", "resource measurement"); payload = { ordinal, measurement_sha256: measurement.sha256, input_sha256: measurement.payload.input_sha256, result_sha256: measurement.payload.result_sha256, result: measurement.payload.result }; }
    if (type === "attempt_end") { if (!resource) fail("ACTION_PREREQUISITE_MISSING", "resource receipt"); payload = { ordinal, outcome: source.durable_state === "valid" && source.terminal_request === "absent" ? "recoverable_crash" : source.durable_state === "valid" && source.terminal_request === "attested_closure" ? "attested_closure" : "infrastructure_failure", terminal_request: source.terminal_request, durable_state: source.durable_state, resource_receipt_sha256: resource.sha256 }; }
    if (type === "campaign_terminal") { if (!resource || !end) fail("ACTION_PREREQUISITE_MISSING", "resource/end"); payload = { kind: action === "publish_attested_terminal_only" ? "valid_attested_closure" : "valid_infrastructure_failure", resource_receipt_sha256: resource.sha256, attempt_end_sha256: end.sha256, terminal_request: source.terminal_request }; }
    if (type === "private_map_open_intent") { if (!evaluatorReservation) fail("ACTION_PREREQUISITE_MISSING", "E0 reservation"); payload = { phase: "E0", reservation_sha256: evaluatorReservation.sha256, reservation_binding: source.reservation_binding }; }
    if (type === "private_map_opened_receipt") { if (!evaluatorReservation || !mapIntent) fail("ACTION_PREREQUISITE_MISSING", "map intent"); payload = { phase: "E0", reservation_sha256: evaluatorReservation.sha256, open_intent_sha256: mapIntent.sha256, reservation_binding: source.reservation_binding }; }
    if (!payload) fail("ACTION_PAYLOAD_UNSUPPORTED", action);
    const record = durableRecord(actionRecordPath(controlId, action, source), type, payload, action);
    const occupied = output.find((candidate) => candidate.path === record.path);
    if (occupied && occupied.sha256 !== record.sha256) fail("OCCUPIED_PATH_CONFLICT", record.path);
    if (!occupied) { output.push(record); output.sort((a, b) => a.path.localeCompare(b.path)); delta.push(record); }
  }
  const patches = {
    reserve_normal_admission: { admission_record: "valid_current", admission_kind: "normal", admission_ordinal: "A0", normal_consumption: "valid" },
    reserve_recovery_admission: { admission_record: "valid_current", admission_kind: "recovery" },
    write_linked_attempt_start: { linked_attempt_record: "durable", attempt_record: "valid_current" },
    reserve_P0_then_live_supervisor: { target_phase: "P0", phase_mode: "P0:not_applicable", phase_state: "RESERVED" },
    reserve_successor_then_live_supervisor: { phase_state: "RESERVED" },
    reserve_E0_evaluate_then_private_map: { target_phase: "E0", phase_mode: "E0:evaluate", phase_state: "RESERVED" },
    reserve_E0_close_prior_failure_then_live_supervisor: { target_phase: "E0", phase_mode: "E0:close_prior_failure", phase_state: "RESERVED" },
    create_launch_intent: { phase_state: "LAUNCH_INTENT_DURABLE" }, spawn_phase: { phase_state: "SPAWNED" }, reap_phase: { phase_state: "REAPED" },
    retain_bounded_result: { phase_state: "RESULT_RETAINED" }, retain_recoverable_result: { phase_state: "RESULT_RETAINED" }, publish_phase_content: { phase_state: "CONTENT_PUBLISHED" },
    publish_valid_or_harness_phase_terminal: { phase_state: "TERMINAL_VALID_OUTCOME" }, publish_harness_failure_phase_terminal: { phase_state: "TERMINAL_HARNESS_FAILURE" }, publish_runtime_failure_phase_terminal: { phase_state: "TERMINAL_HARNESS_FAILURE" }, publish_quarantine_phase_terminal: { phase_state: "TERMINAL_QUARANTINE" },
    create_commit_intent: { git_state: "COMMIT_INTENT_DURABLE" }, create_ledgered_commit_objects: { git_state: "COMMIT_OBJECT_EXACT" }, cas_create_initial_ref: { git_state: "REF_APPLIED" }, cas_update_existing_ref: { git_state: "REF_APPLIED" }, reparse_exact_commit_then_progress: { git_state: "COMMITTED" },
    write_resource_receipt_only: { resource_receipt: "durable" }, write_attempt_end_only: { attempt_end: "durable" }, publish_attested_terminal_only: { campaign_terminal: "valid_attested_closure" }, publish_infrastructure_terminal_only: { campaign_terminal: "valid_infrastructure_failure" },
    perform_readonly_recalculation: { recalculation: "complete" }, release_recoverable_lock: { lock_release: "released" }, release_final_lock: { lock_release: "released" },
    write_private_map_open_intent: { map_state: "MAP_OPEN_INTENT_DURABLE" }, open_private_map_trusted_descriptor: { map_state: "MAP_OPENED_UNRECEIPTED", descriptor_state: "trusted_meter_only" }, write_private_map_opened_receipt: { map_state: "MAP_OPENED_RECEIPT_DURABLE" }, publish_map_open_harness_failure_terminal: { map_state: "MAP_OPEN_FAILED_DURABLE", state: "TERMINAL_HARNESS_FAILURE" },
  };
  const patch = clone(patches[action] || {});
  if (action === "reserve_recovery_admission") patch.admission_ordinal = attemptOrdinal(source);
  if (action === "write_linked_attempt_start") patch.attempt_ordinal = attemptOrdinal(source);
  if (action === "reserve_successor_then_live_supervisor") { patch.target_phase = actionPhaseId(action, source); patch.phase_mode = `${patch.target_phase}:not_applicable`; }
  return { records: output, delta, postState: { evaluation_context: selection.next_context, state: selection.state, selected_rule: selection.id || selection.selected_rule, reason: selection.reason, last_action: action, derived_field_patch: patch } };
}

function normalizeSelection(selection) {
  return {
    id: selection.id || selection.selected_rule,
    reason: selection.reason,
    state: selection.state,
    next_action: selection.next_action,
    next_context: selection.next_context,
  };
}

function verifyTransitionFixture(controlId, fixture) {
  if (fixture.schema !== "tt-supervised-transition-witness-v2") fail("TRANSITION_FIXTURE_SCHEMA_INVALID", controlId);
  const preValidation = validateSource(fixture.source_schema, fixture.pre_state);
  if (!preValidation.ok) fail("PRE_SOURCE_INVALID", `${controlId}:${preValidation.reason}`);
  validateUniverse(fixture.pre_record_universe);
  const pre = { source: fixture.pre_state, records: fixture.pre_record_universe };
  const applied = applyFault(pre, fixture.fault);
  if (!same(applied.observed.source, fixture.observed_state_after_fault) || !same(applied.observed.records, fixture.observed_record_universe_after_fault) || !same(applied.mutations, fixture.fault_mutations)) fail("FAULT_RECONSTRUCTION_MISMATCH", controlId);
  const compilation = compileSourceEvidence(fixture.source_schema, applied.observed.source, applied.observed.records);
  if (!same(compilation.compiled, fixture.compiled_state_for_selection) || !same(compilation.mutations, fixture.source_derivation_mutations)) fail("COMPILED_SOURCE_MISMATCH", controlId);
  const receipt = exactEventReceipt(compilation.compiled, applied.observed.records);
  if (!same(receipt, fixture.observed_event_receipt)) fail("EVENT_RECEIPT_MISMATCH", controlId);
  const evidenceReason = evidenceConsistency(compilation.compiled, applied.observed.records);
  const selected = evidenceReason
    ? { selected_rule: "EVIDENCE_REJECT", reason: evidenceReason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" }
    : selectRule(fixture.source_schema, compilation.compiled);
  const normalized = normalizeSelection(selected);
  if (fixture.selected_rule !== normalized.id || fixture.selected_reason !== normalized.reason || fixture.selected_action !== normalized.next_action) fail("SELECTION_MISMATCH", controlId);
  const reconstructed = expectedAction(controlId, normalized, compilation.compiled, applied.observed.records, fixture.action_executed);
  validateUniverse(fixture.post_record_universe);
  if (!same(reconstructed.delta, fixture.action_record_delta)) fail("ACTION_DELTA_MISMATCH", controlId);
  if (!same(reconstructed.postState, fixture.post_state)) fail("POST_STATE_MISMATCH", controlId);
  if (!same(reconstructed.records, fixture.post_record_universe)) fail("POST_UNIVERSE_MISMATCH", controlId);
  const exactUnion = [...applied.observed.records, ...fixture.action_record_delta].sort((left, right) => left.path.localeCompare(right.path));
  if (!same(exactUnion, fixture.post_record_universe)) fail("POST_APPEND_ONLY_UNION_MISMATCH", controlId);
  if (!same(deriveCounterSnapshot(fixture.pre_record_universe), fixture.source_counters)) fail("PRE_COUNTER_SNAPSHOT_MISMATCH", controlId);
  if (!same(deriveCounterSnapshot(applied.observed.records), fixture.observed_counters_after_fault)) fail("OBSERVED_COUNTER_SNAPSHOT_MISMATCH", controlId);
  if (!same(deriveCounterSnapshot(fixture.post_record_universe), fixture.post_action_counters)) fail("POST_COUNTER_SNAPSHOT_MISMATCH", controlId);
  return { selected_rule: normalized.id, selected_action: normalized.next_action, post_universe_sha256: sha256(fixture.post_record_universe) };
}

function verifyTraceControl(traceControl) {
  const fixture = traceControl.fixture;
  if (fixture.schema !== "tt-supervised-composed-transition-trace-v1" || fixture.no_reseeding_between_steps !== true || fixture.steps.length < 2) fail("TRACE_SCHEMA_INVALID", traceControl.id);
  const boundaries = new Map(fixture.observation_boundaries.map((boundary) => [boundary.before_step, boundary]));
  let priorPost = null;
  for (const step of fixture.steps) {
    if (step.ordinal < 1 || step.expected_rule !== step.fixture.selected_rule || step.fixture_sha256 !== sha256(step.fixture)) fail("TRACE_STEP_BINDING_INVALID", `${traceControl.id}:${step.ordinal}`);
    const boundary = boundaries.get(step.ordinal);
    let expectedPre = priorPost;
    if (boundary) {
      if (!same(boundary.pre_record_universe, priorPost)) fail("TRACE_BOUNDARY_INPUT_DRIFT", `${traceControl.id}:${step.ordinal}`);
      validateUniverse(boundary.pre_record_universe);
      validateUniverse(boundary.post_record_universe);
      const union = [...boundary.pre_record_universe, ...boundary.observation_record_delta].sort((left, right) => left.path.localeCompare(right.path));
      if (!same(union, boundary.post_record_universe) || boundary.pre_universe_sha256 !== sha256(boundary.pre_record_universe) || boundary.post_universe_sha256 !== sha256(boundary.post_record_universe)) fail("TRACE_BOUNDARY_UNION_INVALID", `${traceControl.id}:${step.ordinal}`);
      if (!boundary.observation_record_delta.every((record) => record.producer === "external_meter")) fail("TRACE_BOUNDARY_PRODUCER_INVALID", `${traceControl.id}:${step.ordinal}`);
      expectedPre = boundary.post_record_universe;
    }
    if (expectedPre !== null && !same(step.fixture.pre_record_universe, expectedPre)) fail("TRACE_RESEED_DETECTED", `${traceControl.id}:${step.ordinal}`);
    verifyTransitionFixture(`${traceControl.id}-STEP-${String(step.ordinal).padStart(2, "0")}`, step.fixture);
    priorPost = step.fixture.post_record_universe;
  }
  const expectedChain = fixture.steps.map((step, index) => ({
    step: step.ordinal,
    pre_universe_sha256: sha256(step.fixture.pre_record_universe),
    post_universe_sha256: sha256(step.fixture.post_record_universe),
    predecessor_post_sha256: index === 0 ? null : sha256(fixture.steps[index - 1].fixture.post_record_universe),
    boundary_before_step: boundaries.get(step.ordinal)?.post_universe_sha256 || null,
  }));
  if (!same(expectedChain, fixture.chain) || !same(priorPost, fixture.final_record_universe) || fixture.final_universe_sha256 !== sha256(priorPost)) fail("TRACE_FINAL_BINDING_INVALID", traceControl.id);
}

function validateCapability(descriptor) {
  const expected = transition.candidate_boundary_descriptor;
  if (!same(Object.keys(descriptor).sort(), Object.keys(expected).sort())) return { valid: false, reason: "CAPABILITY_KEYS_MISMATCH" };
  const validators = {
    schema: (value) => value === "candidate_boundary_descriptor_v3",
    executable_sha256: (value) => value === expected.executable_sha256,
    executable_path: (value) => value === "candidate/bin/run",
    argv: (value) => same(value, expected.argv), environment: (value) => same(value, expected.environment), cwd: (value) => value === "candidate/work",
    readable_roots: (value) => same(value, expected.readable_roots), writable_roots: (value) => same(value, expected.writable_roots), inherited_descriptors: (value) => same(value, [0, 1, 2]),
    private_artifact_labels: (value) => value === "deny", path_resolution: (value) => value === "beneath_no_symlinks_no_magiclinks_no_xdev", mount_namespace: (value) => value === "private_unmounted_public_readonly",
    directory_handle_policy: (value) => value === "deny_unlisted_dirfds", syscall_profile: (value) => value === "candidate_no_network_no_process_control", resource_limits: (value) => same(value, expected.resource_limits),
    signal_policy: (value) => value === "self_and_supervisor_only", network: (value) => value === "deny", fork: (value) => value === "deny", exec: (value) => value === "deny_after_initial_image", ipc: (value) => value === "deny",
    debugger: (value) => value === "deny", task_port: (value) => value === "deny", ptrace: (value) => value === "deny", timeout_ms: (value) => Number.isInteger(value) && value > 0 && value <= 300000,
    kill_policy: (value) => value === "term_then_kill", reap_policy: (value) => value === "exact_identity_required", launch_barrier_receipt: (value) => value === "valid_current",
  };
  for (const [field, validator] of Object.entries(validators)) if (!validator(descriptor[field])) return { valid: false, reason: `CAPABILITY_${field.toUpperCase()}_INVALID` };
  return { valid: true, reason: "CAPABILITY_DESCRIPTOR_VALID" };
}

function verifyCapabilityControl(candidate) {
  const fixture = candidate.fixture;
  if (fixture.schema !== "tt-supervised-capability-witness-v1" || !same(fixture.pre_descriptor, transition.candidate_boundary_descriptor)) fail("CAPABILITY_FIXTURE_INVALID", candidate.id);
  const applied = applyFault({ descriptor: fixture.pre_descriptor }, fixture.fault);
  if (!same(applied.observed.descriptor, fixture.observed_descriptor) || !same(applied.mutations, fixture.fault_mutations)) fail("CAPABILITY_FAULT_MISMATCH", candidate.id);
  if (!same(validateCapability(applied.observed.descriptor), fixture.derived_result)) fail("CAPABILITY_RESULT_MISMATCH", candidate.id);
}

function verifyResourceControl(candidate) {
  const fixture = candidate.fixture;
  if (fixture.schema !== "tt-supervised-resource-arithmetic-witness-v2") fail("RESOURCE_FIXTURE_INVALID", candidate.id);
  const pre = { resources: fixture.pre_input, claimed_result: fixture.pre_claimed_result };
  const applied = applyFault(pre, { id: candidate.id, ...fixture.fault });
  if (!same(applied.observed.resources, fixture.observed_input) || !same(applied.observed.claimed_result, fixture.observed_claimed_result) || !same(applied.mutations, fixture.fault_mutations)) fail("RESOURCE_FAULT_MISMATCH", candidate.id);
  const preResult = computeResources(fixture.pre_input);
  const validation = validateResourceInput(fixture.observed_input);
  const result = validation.ok ? computeResources(fixture.observed_input) : null;
  const valid = validation.ok && same(fixture.observed_claimed_result, result);
  const derivedValidation = { valid, reason: !validation.ok ? validation.reason : valid ? "RESOURCE_ARITHMETIC_EXACT" : "RESOURCE_ARITHMETIC_MISMATCH" };
  if (!same(preResult, fixture.pre_result) || !same(validation, fixture.input_validation) || !same(result, fixture.derived_result) || !same(derivedValidation, fixture.derived_validation)) fail("RESOURCE_RESULT_MISMATCH", candidate.id);
}

function applyVerifierMutation(fixture, operation) {
  const mutated = clone(fixture);
  if (operation.kind === "replace") {
    if (!same(getPath(mutated, operation.path), operation.before)) fail("VERIFIER_MUTATION_BEFORE_INVALID", operation.path);
    setPath(mutated, operation.path, clone(operation.after));
  } else if (operation.kind === "append_record") {
    const records = getPath(mutated, operation.path);
    records.push(clone(operation.record));
    records.sort((left, right) => left.path.localeCompare(right.path));
  } else if (operation.kind === "remove_record") {
    const records = getPath(mutated, operation.path);
    const index = records.findIndex((record) => record.path === operation.record_path && record.sha256 === operation.before_sha256);
    if (index < 0) fail("VERIFIER_MUTATION_RECORD_MISSING", operation.record_path);
    records.splice(index, 1);
  } else if (operation.kind === "replace_record") {
    const records = getPath(mutated, operation.path);
    const index = records.findIndex((record) => record.path === operation.record_path && record.sha256 === operation.before_sha256);
    if (index < 0) fail("VERIFIER_MUTATION_RECORD_MISSING", operation.record_path);
    records[index] = clone(operation.after_record);
    records.sort((left, right) => left.path.localeCompare(right.path));
  } else fail("VERIFIER_MUTATION_KIND_UNKNOWN", operation.kind);
  return mutated;
}

function enumerateSchema(schemaId, callback) {
  const schema = schemas[schemaId];
  const fields = Object.keys(schema.domains);
  const source = { ...schema.fixed };
  function visit(index) {
    if (index === fields.length) { callback(clone(source)); return; }
    const field = fields[index];
    for (const value of schema.domains[field]) { source[field] = clone(value); visit(index + 1); }
  }
  visit(0);
}

check("transition_schema", transition.schema === "tt-supervised-executor-transition-matrix-v7", transition.schema);
check("control_schema", control.schema === "tt-supervised-executor-control-matrix-v7", control.schema);
check("protocol", transition.protocol === protocol && control.protocol === protocol, protocol);
check("authorization", [transition, control].every((artifact) => artifact.artifact_freeze_authorized === false && artifact.code_implementation_authorized === false && artifact.control_execution_authorized === false && artifact.campaign_execution_authorized === false), "all execution flags false");
check("transition_byte_binding", control.source_transition_artifact === transitionName && control.source_transition_artifact_sha256 === sha256(byteSnapshots[transitionName]), control.source_transition_artifact_sha256);
const allowStaleBuilder = process.env.V8_VERIFY_ALLOW_STALE_BUILDER === "1";
if (!allowStaleBuilder) check("builder_byte_binding", control.builder_artifact === builderName && control.builder_artifact_sha256 === sha256(byteSnapshots[builderName]), control.builder_artifact_sha256);
check("publication_snapshot", control.publication_snapshot.hashes_derived_from_in_memory_bytes === true && control.publication_snapshot.transition_sha256 === sha256(byteSnapshots[transitionName]) && control.publication_snapshot.transition_byte_length === byteSnapshots[transitionName].length, `${byteSnapshots[transitionName].length} bytes`);
check("publication_policy", transition.publication_policy.one_in_memory_builder_snapshot === true && transition.publication_policy.transition_bytes_serialized_once_before_write === true && transition.publication_policy.moving_file_rereads_for_binding_forbidden === true, "single byte snapshots required");

const requiredContexts = ["entry_preflight", "attempt_admission", "prior_attempt_safety", "live_supervisor", "live_transition", "recovery_reconstruction", "campaign_progression", "repository_validation", "meter_finalization", "e0_private_map"];
check("contexts", same(transition.contexts, requiredContexts), requiredContexts.join(","));
check("rule_count", transition.rule_count === rules.length && new Set(rules.map((rule) => rule.id)).size === rules.length, `${rules.length} unique rules`);
for (const rule of rules) {
  const schema = schemas[rule.source_schema];
  check(`rule:${rule.id}`, Boolean(schema) && rule.evaluation_context === schema.fixed.evaluation_context && sha256(rule.compiled_predicate) === rule.compiled_predicate_sha256 && Object.keys(rule.compiled_predicate).every((field) => schema.permitted.includes(field)), `${rule.source_schema}:${rule.evaluation_context}`);
}

const requiredObligations = ["V8-ORDINAL-01", "V8-ORDINAL-02", "V8-PHASE-01", "V8-TRACE-01", "V8-EVENT-01", "V8-RECOVERY-01", "V8-EVIDENCE-01", "V8-IDENTITY-01", "V8-POST-01", "V8-UNIQUE-01", "V8-GIT-01", "V8-GIT-02", "V8-CONTEXT-01", "V8-OVERLAP-01", "V8-CAPABILITY-01", "V8-RESOURCE-01", "V8-RESOURCE-02", "V8-PUBLISH-01"];
check("repair_obligations", same(transition.repair_obligations, requiredObligations) && same(control.repair_obligations, requiredObligations), `${requiredObligations.length} obligations`);

const priorSnapshot = join(dirname(here), "tt-supervised-executor-v7-rejected-snapshot");
const preservedBytes = Object.fromEntries(Object.keys(transition.preserved_v7_negative_evidence).map((name) => [name, readFileSync(join(priorSnapshot, name))]));
const preservedManifest = Object.fromEntries(Object.entries(preservedBytes).map(([name, bytes]) => [name, sha256(bytes)]));
check("preserved_v7_negative_evidence", same(preservedManifest, transition.preserved_v7_negative_evidence) && same(preservedManifest, control.preserved_v7_negative_evidence), `${Object.keys(preservedManifest).length} immutable files`);

const controls = control.controls;
check("control_count", controls.length === control.static_control_count && new Set(controls.map((candidate) => candidate.id)).size === controls.length, `${controls.length} controls`);
check("control_fixture_hashes_unique", new Set(controls.map((candidate) => candidate.fixture_sha256)).size === controls.length, `${controls.length} unique fixture hashes`);
for (const candidate of controls) {
  if (candidate.fixture_sha256 !== sha256(candidate.fixture)) fail("FIXTURE_HASH_MISMATCH", candidate.id);
  if (candidate.fixture.schema === "tt-supervised-transition-witness-v2") verifyTransitionFixture(candidate.id, candidate.fixture);
  else if (candidate.fixture.schema === "tt-supervised-composed-transition-trace-v1") verifyTraceControl(candidate);
  else if (candidate.fixture.schema === "tt-supervised-capability-witness-v1") verifyCapabilityControl(candidate);
  else if (candidate.fixture.schema === "tt-supervised-resource-arithmetic-witness-v2") verifyResourceControl(candidate);
  else fail("CONTROL_FIXTURE_KIND_UNKNOWN", candidate.id);
}
check("all_controls_reconstructed", true, `${controls.length} controls`);

const controlsById = Object.fromEntries(controls.map((candidate) => [candidate.id, candidate]));
const skipMutations = process.env.V8_VERIFY_SKIP_MUTATIONS === "1";
if (!skipMutations) {
  for (const mutation of control.verifier_mutation_suite) {
    const target = controlsById[mutation.target_control];
    if (!target || target.fixture_sha256 !== mutation.target_fixture_sha256) fail("VERIFIER_MUTATION_TARGET_INVALID", mutation.id);
    const mutated = applyVerifierMutation(target.fixture, mutation.operation);
    let rejection = null;
    try { verifyTransitionFixture(target.id, mutated); } catch (error) { rejection = error.code || "UNKNOWN"; }
    if (rejection !== mutation.expected_rejection) fail("VERIFIER_MUTATION_REJECTION_MISMATCH", `${mutation.id}:${rejection}:${mutation.expected_rejection}`);
    checks.push({ name: `mutation:${mutation.id}`, status: "pass", detail: rejection });
  }
}
check("verifier_mutation_count", control.verifier_mutation_count === control.verifier_mutation_suite.length && control.verifier_mutation_suite.length === 4, "four postcondition mutations rejected");

const skipExhaustive = process.env.V8_VERIFY_SKIP_EXHAUSTIVE === "1";
if (!skipExhaustive) {
  const schemaManifests = [];
  const partitions = new Map();
  let caseCount = 0;
  for (const schemaId of Object.keys(schemas)) {
    const digest = createHash("sha256");
    let ordinal = 0;
    enumerateSchema(schemaId, (source) => {
      const selected = selectRule(schemaId, source);
      const id = selected.id || selected.selected_rule;
      const row = { schema: schemaId, ordinal: ++ordinal, source_sha256: sha256(source), selected_rule: id, next_action: selected.next_action };
      digest.update(`${canonical(row)}\n`);
      const key = `${schemaId}:${id}`;
      partitions.set(key, (partitions.get(key) || 0) + 1);
    });
    caseCount += ordinal;
    schemaManifests.push({ source_schema: schemaId, case_count: ordinal, ordered_case_stream_sha256: digest.digest("hex") });
  }
  const partitionRows = [...partitions.entries()].map(([key, cardinality]) => {
    const split = key.lastIndexOf(":");
    return { source_schema: key.slice(0, split), partition: key.slice(split + 1), cardinality };
  }).sort((left, right) => `${left.source_schema}:${left.partition}`.localeCompare(`${right.source_schema}:${right.partition}`));
  check("symbolic_case_count", caseCount === transition.totality.symbolic_domain_cardinality, `${caseCount}`);
  check("symbolic_schema_manifests", same(schemaManifests, transition.totality.schema_manifests), `${schemaManifests.length} schemas`);
  check("symbolic_partitions", same(partitionRows, transition.totality.partitions), `${partitionRows.length} partitions`);
  check("symbolic_case_digest", transition.totality.symbolic_case_digest === sha256(schemaManifests), transition.totality.symbolic_case_digest);
}

for (const suite of control.generated_suites) {
  if (suite.manifest && suite.manifest_sha256 !== sha256(suite.manifest)) fail("GENERATED_SUITE_HASH_MISMATCH", suite.id);
}
const e0Suite = control.generated_suites.find((suite) => suite.id === "SEC8-GENERATED-002");
for (const row of e0Suite.manifest) {
  const { ordinal, selected_rule: expectedRule, next_action: expectedActionName, ...fields } = row;
  const source = { ...schemas.e0_private_map_v3.fixed, ...fields };
  const selected = selectRule("e0_private_map_v3", source);
  if ((selected.id || selected.selected_rule) !== expectedRule || selected.next_action !== expectedActionName || expectedRule === "SCHEMA_REJECT") fail("E0_PROJECTION_INVALID", String(ordinal));
}
check("e0_projection", e0Suite.case_count === e0Suite.manifest.length && transition.e0_private_map_protocol.event_projection_sha256 === sha256(e0Suite.manifest), `${e0Suite.case_count} valid projected cases`);

const expectedMeterActions = ["write_resource_receipt_only", "write_attempt_end_only", "release_recoverable_lock", "publish_attested_terminal_only", "publish_infrastructure_terminal_only", "perform_readonly_recalculation", "release_final_lock"];
check("meter_protocol", transition.meter_finalization_protocol.exact_process_identity_receipts_required === true && same(transition.meter_finalization_protocol.stages.map((stage) => stage.action), expectedMeterActions), expectedMeterActions.join(","));
check("control_breakdown", control.rule_selection_control_count === 153 && control.targeted_transition_control_count === 30 && control.composed_trace_control_count === 4 && control.budget_boundary_control_count === 3 && control.capability_control_count === 28 && control.resource_control_count === 10, "153 rule, 30 targeted, 4 trace, 3 budget, 28 capability, 10 resource");

const receipt = {
  schema: "tt-supervised-executor-local-verification-v8",
  protocol,
  status: skipExhaustive || skipMutations || allowStaleBuilder ? "DEVELOPMENT_PARTIAL" : "PASS",
  claim_boundary: ["MODEL-BOUND", "ZERO-RUN", "NO_IMPLEMENTATION_AUTHORIZATION", "NO_CAMPAIGN_AUTHORIZATION", "NO_ECDLP_CLAIM"],
  immutable_input_snapshots: Object.fromEntries(Object.entries(byteSnapshots).map(([name, bytes]) => [name, { sha256: sha256(bytes), byte_length: bytes.length }])),
  preserved_v7_snapshot_sha256: preservedManifest,
  exhaustive_symbolic_replay: !skipExhaustive,
  verifier_mutations_executed: !skipMutations,
  builder_binding_executed: !allowStaleBuilder,
  symbolic_case_count: skipExhaustive ? null : transition.totality.symbolic_domain_cardinality,
  control_count: controls.length,
  verifier_mutation_count: control.verifier_mutation_suite.length,
  check_count: checks.length,
  checks,
};
const receiptName = "local-verification-v8.json";
const receiptBytes = Buffer.from(`${JSON.stringify(receipt, null, 2)}\n`, "utf8");
writeFileSync(join(here, receiptName), receiptBytes);
process.stdout.write(`${JSON.stringify({ status: receipt.status, receipt: receiptName, receipt_sha256: sha256(receiptBytes), checks: checks.length, controls: controls.length, symbolic_cases: receipt.symbolic_case_count })}\n`);
