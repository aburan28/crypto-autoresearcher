import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/7";

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  const bytes = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha256").update(bytes).digest("hex");
}

function same(left, right) {
  return canonical(left) === canonical(right);
}

function conditionMatches(actual, expected) {
  return Array.isArray(expected) ? expected.some((candidate) => same(candidate, actual)) : same(actual, expected);
}

const transitionPath = join(here, "supervised-executor-transition-matrix-v6.json");
const controlPath = join(here, "supervised-executor-control-matrix-v6.json");
const builderPath = join(here, "build_v7_design_artifacts.mjs");
const transition = JSON.parse(readFileSync(transitionPath, "utf8"));
const control = JSON.parse(readFileSync(controlPath, "utf8"));
const checks = [];

function check(name, condition, detail) {
  if (!condition) throw new Error(`${name}: ${detail}`);
  checks.push({ name, status: "pass", detail });
}

check("transition_schema", transition.schema === "tt-supervised-executor-transition-matrix-v6", transition.schema);
check("control_schema", control.schema === "tt-supervised-executor-control-matrix-v6", control.schema);
check("protocol", transition.protocol === protocol && control.protocol === protocol, protocol);
check("authorization", [transition, control].every((artifact) => artifact.artifact_freeze_authorized === false && artifact.code_implementation_authorized === false && artifact.control_execution_authorized === false && artifact.campaign_execution_authorized === false), "all implementation and execution flags false");
check("transition_binding", control.source_transition_artifact_sha256 === sha256(readFileSync(transitionPath)), control.source_transition_artifact_sha256);
check("builder_binding", control.builder_artifact_sha256 === sha256(readFileSync(builderPath)), control.builder_artifact_sha256);

const requiredContexts = ["entry_preflight", "attempt_admission", "prior_attempt_safety", "live_supervisor", "live_transition", "recovery_reconstruction", "campaign_progression", "repository_validation", "meter_finalization", "e0_private_map"];
check("contexts", same(transition.contexts, requiredContexts), requiredContexts.join(","));

const rules = transition.rules;
const ruleIds = new Set(rules.map((rule) => rule.id));
check("rule_count", transition.rule_count === rules.length, `${rules.length}`);
check("rule_ids_unique", ruleIds.size === rules.length, `${ruleIds.size} unique`);
for (const rule of rules) {
  check(`predicate:${rule.id}`, sha256(rule.compiled_predicate) === rule.compiled_predicate_sha256, rule.compiled_predicate_sha256);
  const schema = transition.source_schemas[rule.source_schema];
  check(`schema_ref:${rule.id}`, Boolean(schema), rule.source_schema);
  check(`predicate_fields:${rule.id}`, Object.keys(rule.compiled_predicate).every((field) => schema.permitted.includes(field)), rule.source_schema);
}

function validateSource(schemaId, source) {
  const schema = transition.source_schemas[schemaId];
  if (!schema) return { ok: false, reason: "SCHEMA_UNKNOWN" };
  if (!same(Object.keys(source).sort(), schema.permitted)) return { ok: false, reason: "SCHEMA_KEYS_MISMATCH" };
  for (const [field, expected] of Object.entries(schema.fixed)) if (!conditionMatches(source[field], expected)) return { ok: false, reason: `SCHEMA_FIXED_MISMATCH:${field}` };
  for (const [field, domain] of Object.entries(schema.domains)) if (!domain.some((value) => same(value, source[field]))) return { ok: false, reason: `SCHEMA_DOMAIN_MISMATCH:${field}` };
  if (schemaId === "locked_entry_ineligible_v2" && source.budget_relation === "exhausted_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps)
      || source.recovery_slots_consumed !== source.approval_maximum_recovery_bootstraps
      || source.recovery_budget !== "exhausted") return { ok: false, reason: "SCHEMA_BUDGET_EXHAUSTION_RELATION_INVALID" };
  }
  if (schemaId === "locked_recovery_eligible_v2" && source.budget_relation === "available_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps)
      || !Number.isInteger(source.recovery_slots_consumed)
      || !Number.isInteger(source.next_recovery_ordinal)
      || source.recovery_slots_consumed >= source.approval_maximum_recovery_bootstraps
      || source.next_recovery_ordinal !== source.recovery_slots_consumed + 1
      || source.recovery_budget !== "available") return { ok: false, reason: "SCHEMA_BUDGET_AVAILABILITY_RELATION_INVALID" };
  }
  if (schemaId === "meter_finalization_v2") {
    const relationValid = (source.run_mode === "normal" && source.admission_kind === "normal" && source.attempt_ordinal === "A0")
      || (source.run_mode === "recovery" && source.admission_kind === "recovery" && source.attempt_ordinal === "A1");
    if (!relationValid) return { ok: false, reason: "SCHEMA_METER_ATTEMPT_RELATION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v2") {
    const relationValid = source.phase_mode === "E0:evaluate"
      ? source.private_map_state === "MAP_OPENED_RECEIPT_DURABLE" && source.private_map_binding === "valid_current" && source.phase_private_map_relation === "valid"
      : source.private_map_state === "not_applicable" && source.private_map_binding === "not_applicable" && source.phase_private_map_relation === "valid";
    if (!relationValid) return { ok: false, reason: "SCHEMA_RECOVERY_PRIVATE_MAP_RELATION_INVALID" };
  }
  return { ok: true, reason: "SCHEMA_VALID" };
}

const bySchema = Object.fromEntries(Object.keys(transition.source_schemas).map((id) => [id, rules.filter((rule) => rule.source_schema === id).sort((a, b) => a.priority - b.priority)]));
function selectRule(schemaId, source) {
  const validation = validateSource(schemaId, source);
  if (!validation.ok) return { id: "SCHEMA_REJECT", reason: validation.reason, next_action: "none" };
  return bySchema[schemaId].find((rule) => Object.entries(rule.compiled_predicate).every(([field, expected]) => conditionMatches(source[field], expected)))
    || { id: "DEFAULT", reason: "STATE_PRODUCT_UNMATCHED", next_action: "request_infrastructure_failure" };
}

function enumerateSchema(schemaId, callback) {
  const schema = transition.source_schemas[schemaId];
  const fields = Object.keys(schema.domains);
  const source = { ...schema.fixed };
  function visit(index) {
    if (index === fields.length) { callback(structuredClone(source)); return; }
    const field = fields[index];
    for (const value of schema.domains[field]) { source[field] = structuredClone(value); visit(index + 1); }
  }
  visit(0);
}

const recomputedSchemaManifests = [];
const recomputedPartitions = new Map();
let recomputedCases = 0;
for (const schemaId of Object.keys(transition.source_schemas)) {
  const digest = createHash("sha256");
  let ordinal = 0;
  enumerateSchema(schemaId, (source) => {
    const selected = selectRule(schemaId, source);
    const row = { schema: schemaId, ordinal: ++ordinal, source_sha256: sha256(source), selected_rule: selected.id, next_action: selected.next_action };
    digest.update(`${canonical(row)}\n`);
    const key = `${schemaId}:${selected.id}`;
    recomputedPartitions.set(key, (recomputedPartitions.get(key) || 0) + 1);
  });
  recomputedCases += ordinal;
  recomputedSchemaManifests.push({ source_schema: schemaId, case_count: ordinal, ordered_case_stream_sha256: digest.digest("hex") });
}
const recomputedPartitionRows = [...recomputedPartitions.entries()].map(([key, cardinality]) => {
  const split = key.lastIndexOf(":");
  return { source_schema: key.slice(0, split), partition: key.slice(split + 1), cardinality };
}).sort((a, b) => `${a.source_schema}:${a.partition}`.localeCompare(`${b.source_schema}:${b.partition}`));
check("symbolic_case_count", transition.totality.symbolic_domain_cardinality === recomputedCases, `${recomputedCases}`);
check("symbolic_schema_manifests", same(transition.totality.schema_manifests, recomputedSchemaManifests), `${recomputedSchemaManifests.length} schemas`);
check("symbolic_partitions", same(transition.totality.partitions, recomputedPartitionRows), `${recomputedPartitionRows.length} partitions`);
check("symbolic_digest", transition.totality.symbolic_case_digest === sha256(recomputedSchemaManifests), transition.totality.symbolic_case_digest);

const admissionRules = Object.fromEntries(["E012", "E013", "D001", "D002", "D003", "D004"].map((id) => [id, rules.find((rule) => rule.id === id)]));
check("admission_reserve_before_start", admissionRules.E012.next_action === "reserve_normal_admission" && admissionRules.E013.next_action === "reserve_recovery_admission" && admissionRules.D001.next_action === "write_linked_attempt_start" && admissionRules.D002.next_action === "write_linked_attempt_start", "token actions precede linked starts");
check("admission_dispatch_after_start", admissionRules.D003.compiled_predicate.linked_attempt_record === "durable" && admissionRules.D004.compiled_predicate.linked_attempt_record === "durable", "both dispatches require durable linked start");
check("repository_before_start_forbidden", transition.admission_protocol.repository_action_before_start_forbidden === true, "explicitly forbidden");

const meterStages = transition.meter_finalization_protocol.stages;
const expectedMeterActions = ["write_resource_receipt_only", "write_attempt_end_only", "release_recoverable_lock", "publish_attested_terminal_only", "publish_infrastructure_terminal_only", "perform_readonly_recalculation", "release_final_lock"];
check("meter_stage_actions", same(meterStages.map((row) => row.action), expectedMeterActions), expectedMeterActions.join(","));
check("meter_single_write", transition.meter_finalization_protocol.one_campaign_owned_record_per_write_action === true && transition.meter_finalization_protocol.terminal_last_campaign_owned_write === true, "single-record stages and terminal last");

const e0EventSchema = transition.source_schemas.live_transition_e0_evaluate_v2;
check("e0_event_guard_fields", e0EventSchema.fixed.private_map_state === "MAP_OPENED_RECEIPT_DURABLE" && e0EventSchema.fixed.private_map_binding === "valid_current", "receipt and binding are closed event fields");
check("e0_event_projection_count", transition.e0_private_map_protocol.event_projection_case_count === 168, "168 projected event cases");
check("e0_closed_source_count", transition.e0_private_map_protocol.closed_source_product_case_count === transition.source_schemas.e0_private_map_v2.domain_cardinality && transition.e0_private_map_protocol.closed_source_product_case_count === 672, "672 closed source cases including descriptor state");

const counterTypes = {
  root_admissions: ["normal_admission", "recovery_admission"], root_attempt_starts: ["attempt_start"],
  normal_consumptions: ["normal_admission"], recovery_slots: ["recovery_admission"],
  phase_reservations: ["candidate_phase_reservation", "evaluator_phase_reservation"], candidate_phase_reservations: ["candidate_phase_reservation"], evaluator_phase_reservations: ["evaluator_phase_reservation"],
  phase_spawns: ["phase_spawn"], phase_reaps: ["phase_reap"], commit_intents: ["commit_intent"], commit_objects: ["commit_object"], ref_cas_attempts: ["ref_cas_attempt"], committed_phases: ["committed_phase"], meter_finalizations: ["attempt_end"],
};

const liveStates = transition.live_phase_protocol.states;
function phaseId(source) {
  if (source.evaluation_context === "e0_private_map" || source.e0_mode) return "E0";
  return (source.phase_mode || "P0:not_applicable").split(":")[0];
}

function attemptOrdinal(source) {
  if (source.admission_kind === "recovery" || source.run_mode === "recovery") {
    const ordinal = Number.isInteger(source.next_recovery_ordinal) ? source.next_recovery_ordinal : 1;
    return `A${ordinal}`;
  }
  return "A0";
}

function validateRecords(records) {
  const paths = new Set();
  const admissions = new Map();
  const starts = new Set();
  for (const record of records) {
    if (paths.has(record.path)) throw new Error(`duplicate path ${record.path}`);
    paths.add(record.path);
    const { canonical_bytes: bytes, sha256: digest, ...body } = record;
    if (canonical(body) !== bytes || sha256(bytes) !== digest) throw new Error(`record bytes invalid ${record.path}`);
    if (["normal_admission", "recovery_admission"].includes(record.record_type)) {
      if (admissions.has(record.payload.ordinal)) throw new Error(`duplicate admission ${record.payload.ordinal}`);
      admissions.set(record.payload.ordinal, record);
    }
  }
  for (const record of records.filter((row) => row.record_type === "attempt_start")) {
    const ordinal = record.payload.ordinal;
    const admission = admissions.get(ordinal);
    if (!admission || starts.has(ordinal)) throw new Error(`unlinked or duplicate start ${ordinal}`);
    if (record.payload.admission_ordinal !== ordinal || record.payload.admission_sha256 !== admission.sha256) throw new Error(`invalid admission digest link ${ordinal}`);
    starts.add(ordinal);
  }
  for (const record of records.filter((row) => row.record_type === "campaign_terminal")) {
    const resource = records.find((row) => row.record_type === "resource_receipt" && row.sha256 === record.payload.resource_receipt_sha256);
    const end = records.find((row) => row.record_type === "attempt_end" && row.sha256 === record.payload.attempt_end_sha256);
    if (!resource || !end) throw new Error(`invalid campaign terminal link ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "launch_intent")) {
    const capability = records.find((row) => row.record_type === "capability_receipt" && row.sha256 === record.payload.capability_receipt_sha256);
    if (!capability) throw new Error(`invalid launch capability link ${record.path}`);
    if (record.payload.phase_mode === "E0:evaluate") {
      const receipt = records.find((row) => row.record_type === "private_map_opened_receipt" && row.sha256 === record.payload.private_map_receipt_sha256);
      if (!receipt) throw new Error(`invalid E0 launch map link ${record.path}`);
    }
  }
  for (const record of records.filter((row) => row.record_type === "private_map_open_intent")) {
    const reservation = records.find((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256);
    if (!reservation) throw new Error(`invalid map intent link ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "private_map_opened_receipt")) {
    const reservation = records.find((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256);
    const intent = records.find((row) => row.record_type === "private_map_open_intent" && row.sha256 === record.payload.open_intent_sha256);
    if (!reservation || !intent) throw new Error(`invalid map receipt link ${record.path}`);
  }
}

function deriveSnapshot(records) {
  validateRecords(records);
  const evidence = Object.fromEntries(Object.entries(counterTypes).map(([counter, types]) => [counter, records.filter((record) => types.includes(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }))]));
  const values = Object.fromEntries(Object.entries(evidence).map(([counter, rows]) => [counter, rows.length]));
  const countable = new Set(Object.values(counterTypes).flat());
  const noncounter = records.filter((record) => !countable.has(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }));
  return { schema: "tt-supervised-counter-snapshot-v3", values, counter_evidence: evidence, noncounter_records: noncounter, complete_universe_sha256: sha256(records), counter_evidence_sha256: sha256(evidence), universe_record_count: records.length };
}

function evidenceConsistency(source, records) {
  const has = (type) => records.some((record) => record.record_type === type);
  const hasPhase = (type, phase = phaseId(source)) => records.some((record) => record.record_type === type && record.payload.phase === phase);
  const ordinal = attemptOrdinal(source);
  const admissionType = source.admission_kind === "recovery" || source.run_mode === "recovery" ? "recovery_admission" : "normal_admission";
  if (["valid_current", "valid_unstarted"].includes(source.admission_record) && !records.some((record) => record.record_type === admissionType && record.payload.ordinal === ordinal)) return "EVIDENCE_ADMISSION_MISSING";
  if (source.attempt_record === "valid_current" && !records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === ordinal)) return "EVIDENCE_CURRENT_ATTEMPT_START_MISSING";
  if (source.linked_attempt_record === "durable" && !has("attempt_start")) return "EVIDENCE_ATTEMPT_START_MISSING";
  if (source.resource_receipt === "durable" && !has("resource_receipt")) return "EVIDENCE_RESOURCE_RECEIPT_MISSING";
  if (source.attempt_end === "durable" && !has("attempt_end")) return "EVIDENCE_ATTEMPT_END_MISSING";
  if (source.capability_receipt === "valid_current" && !has("capability_receipt")) return "EVIDENCE_CAPABILITY_RECEIPT_MISSING";
  if ((source.map_state === "MAP_OPENED_RECEIPT_DURABLE" || source.private_map_state === "MAP_OPENED_RECEIPT_DURABLE") && !has("private_map_opened_receipt")) return "EVIDENCE_PRIVATE_MAP_RECEIPT_MISSING";
  if (source.evaluation_context === "e0_private_map" && !hasPhase("evaluator_phase_reservation", "E0")) return "EVIDENCE_E0_RESERVATION_MISSING";
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(source.map_state || source.private_map_state) && !has("private_map_open_intent")) return "EVIDENCE_PRIVATE_MAP_INTENT_MISSING";
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal) && !has("campaign_terminal")) return "EVIDENCE_CAMPAIGN_TERMINAL_MISSING";
  if (source.state && liveStates.includes(source.state) && source.state !== "UNSEEN") {
    const index = liveStates.indexOf(source.state);
    const atOrAfter = (state) => index >= liveStates.indexOf(state);
    if (!hasPhase(phaseId(source) === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation")) return "EVIDENCE_PHASE_RESERVATION_MISSING";
    if (atOrAfter("LAUNCH_INTENT_DURABLE") && !hasPhase("launch_intent")) return "EVIDENCE_LAUNCH_INTENT_MISSING";
    if ((["SPAWNED", "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) && !hasPhase("phase_spawn")) return "EVIDENCE_PHASE_SPAWN_MISSING";
    if ((["REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) && !hasPhase("phase_reap")) return "EVIDENCE_PHASE_REAP_MISSING";
    if (atOrAfter("COMMIT_INTENT_DURABLE") && !hasPhase("commit_intent")) return "EVIDENCE_COMMIT_INTENT_MISSING";
    if (atOrAfter("COMMIT_OBJECT_EXACT") && !hasPhase("commit_object")) return "EVIDENCE_COMMIT_OBJECT_MISSING";
    if (atOrAfter("REF_APPLIED") && !hasPhase("ref_cas_attempt")) return "EVIDENCE_REF_CAS_MISSING";
    if (atOrAfter("COMMITTED") && !hasPhase("committed_phase")) return "EVIDENCE_COMMITTED_PHASE_MISSING";
  }
  if (source.variant === "git_commit_validation_v1") {
    if (source.commit_intent_relation !== "invalid" && !hasPhase("commit_intent")) return "EVIDENCE_GIT_INTENT_MISSING";
    if (source.commit_object_state === "exact" && !hasPhase("commit_object")) return "EVIDENCE_GIT_OBJECT_MISSING";
    if (source.cas_status === "applied" && !hasPhase("ref_cas_attempt")) return "EVIDENCE_GIT_CAS_MISSING";
  }
  return null;
}

function getPath(root, path) {
  return path.split(".").reduce((value, key) => value?.[key], root);
}

function setPath(root, path, value) {
  const keys = path.split(".");
  let cursor = root;
  for (const key of keys.slice(0, -1)) cursor = cursor[key];
  cursor[keys.at(-1)] = structuredClone(value);
}

function replayFault(pre, fault) {
  const observed = structuredClone(pre);
  if (fault.kind === "none") return { observed, mutations: [] };
  const mutations = [];
  if (fault.kind === "replace") {
    const before = structuredClone(getPath(observed, fault.path));
    if (!same(before, fault.before)) throw new Error(`fault before mismatch ${fault.path}`);
    setPath(observed, fault.path, fault.after);
    mutations.push({ path: fault.path, before, after: structuredClone(fault.after) });
  } else if (fault.kind === "add_source_property") {
    if (Object.hasOwn(observed.source, fault.property)) throw new Error(`fault property occupied ${fault.property}`);
    observed.source[fault.property] = structuredClone(fault.value);
    mutations.push({ path: `source.${fault.property}`, before: "__absent__", after: structuredClone(fault.value) });
  } else if (fault.kind === "remove_record") {
    const index = observed.records.findIndex((record) => record.path === fault.record_path);
    if (index < 0) throw new Error(`fault record absent ${fault.record_path}`);
    const [removed] = observed.records.splice(index, 1);
    mutations.push({ path: `records:${fault.record_path}`, before: removed.sha256, after: "__absent__" });
  } else {
    throw new Error(`unknown fault ${fault.kind}`);
  }
  return { observed, mutations };
}

const actionRecordTypes = {
  reserve_normal_admission: "normal_admission", reserve_recovery_admission: "recovery_admission", write_linked_attempt_start: "attempt_start",
  reserve_P0_then_live_supervisor: "candidate_phase_reservation", reserve_successor_then_live_supervisor: "candidate_phase_reservation", reserve_E0_evaluate_then_private_map: "evaluator_phase_reservation", reserve_E0_close_prior_failure_then_live_supervisor: "evaluator_phase_reservation",
  create_launch_intent: "launch_intent", spawn_phase: "phase_spawn", reap_phase: "phase_reap",
  publish_harness_failure_phase_terminal: "phase_terminal", publish_quarantine_phase_terminal: "phase_terminal", reconcile_process_then_publish_quarantine_phase_terminal: "phase_terminal", retain_recoverable_result_else_publish_quarantine_phase_terminal: "phase_terminal",
  publish_phase_content: "phase_content", publish_valid_or_harness_phase_terminal: "phase_terminal",
  create_commit_intent: "commit_intent", create_ledgered_commit_objects: "commit_object", cas_create_initial_ref: "ref_cas_attempt", cas_update_existing_ref: "ref_cas_attempt", reparse_exact_commit_then_progress: "committed_phase",
  write_resource_receipt_only: "resource_receipt", write_attempt_end_only: "attempt_end", publish_attested_terminal_only: "campaign_terminal", publish_infrastructure_terminal_only: "campaign_terminal",
  write_private_map_open_intent: "private_map_open_intent", write_private_map_opened_receipt: "private_map_opened_receipt", publish_map_open_harness_failure_terminal: "phase_terminal",
};

const controls = control.controls;
check("control_count", control.static_control_count === controls.length, `${controls.length}`);
check("control_ids_unique", new Set(controls.map((row) => row.id)).size === controls.length, `${controls.length}`);
check("fixture_hashes_unique", new Set(controls.map((row) => row.fixture_sha256)).size === controls.length, `${controls.length}`);

let nonNone = 0;
let materialized = 0;
for (const row of controls) {
  check(`fixture_hash:${row.id}`, sha256(row.fixture) === row.fixture_sha256, row.fixture_sha256);
  const fixture = row.fixture;
  if (fixture.fault?.kind && fixture.fault.kind !== "none") {
    nonNone += 1;
    if ((fixture.fault_mutations || []).length > 0) materialized += 1;
  }
  if (fixture.schema === "tt-supervised-transition-witness-v1") {
    const replayed = replayFault({ source: fixture.pre_state, records: fixture.pre_record_universe }, fixture.fault);
    check(`fault_replay:${row.id}`, same(replayed.observed.source, fixture.observed_state_after_fault) && same(replayed.observed.records, fixture.observed_record_universe_after_fault) && same(replayed.mutations, fixture.fault_mutations), `${replayed.mutations.length} mutations`);
    const consistencyReason = evidenceConsistency(fixture.observed_state_after_fault, fixture.observed_record_universe_after_fault);
    const expectedSelection = consistencyReason
      ? { id: "EVIDENCE_REJECT", reason: consistencyReason, next_action: "none" }
      : selectRule(fixture.source_schema, fixture.observed_state_after_fault);
    check(`selection:${row.id}`, fixture.selected_rule === expectedSelection.id && fixture.selected_reason === expectedSelection.reason && fixture.selected_action === expectedSelection.next_action, `${expectedSelection.id}/${expectedSelection.next_action}`);
    for (const [recordsField, snapshotField] of [["pre_record_universe", "source_counters"], ["observed_record_universe_after_fault", "observed_counters_after_fault"], ["post_record_universe", "post_action_counters"]]) {
      check(`snapshot:${row.id}:${snapshotField}`, same(deriveSnapshot(fixture[recordsField]), fixture[snapshotField]), `${fixture[recordsField].length} records`);
    }
    const observedDigests = new Set(fixture.observed_record_universe_after_fault.map((record) => record.sha256));
    check(`action_delta:${row.id}`, fixture.action_record_delta.every((record) => !observedDigests.has(record.sha256) && fixture.post_record_universe.some((post) => post.sha256 === record.sha256)), `${fixture.action_record_delta.length} new records`);
    const expectedType = actionRecordTypes[fixture.selected_action];
    if (fixture.action_executed && expectedType) {
      check(`action_type:${row.id}`, fixture.action_record_delta.length === 1 && fixture.action_record_delta[0].record_type === expectedType && fixture.action_record_delta[0].producer === fixture.selected_action, expectedType);
    } else {
      check(`action_type:${row.id}`, fixture.action_record_delta.length === 0, "no durable action record");
    }
    const expectedPostCount = fixture.observed_record_universe_after_fault.length + fixture.action_record_delta.length;
    check(`post_universe:${row.id}`, fixture.post_record_universe.length === expectedPostCount, `${expectedPostCount} records`);
  } else if (fixture.schema === "tt-supervised-capability-witness-v1") {
    const replayed = replayFault({ descriptor: fixture.pre_descriptor }, fixture.fault);
    check(`fault_replay:${row.id}`, same(replayed.observed.descriptor, fixture.observed_descriptor) && same(replayed.mutations, fixture.fault_mutations), `${replayed.mutations.length} mutations`);
  } else if (fixture.schema === "tt-supervised-resource-arithmetic-witness-v1") {
    const replayed = replayFault({ resources: fixture.pre_input, claimed_result: fixture.pre_claimed_result }, fixture.fault);
    check(`fault_replay:${row.id}`, same(replayed.observed.resources, fixture.observed_input) && same(replayed.observed.claimed_result, fixture.observed_claimed_result) && same(replayed.mutations, fixture.fault_mutations), `${replayed.mutations.length} mutations`);
  }
}
check("fault_materialization", nonNone === materialized && nonNone === control.self_audit.non_none_fault_count, `${materialized}/${nonNone}`);

function byId(id) {
  const row = controls.find((controlRow) => controlRow.id === id);
  if (!row) throw new Error(`missing control ${id}`);
  return row;
}

for (const [maximum, expected] of [[0, 1], [2, 3], [32, 33]]) {
  const row = byId(`SEC7-BUDGET-${String(maximum).padStart(2, "0")}`);
  check(`budget_${maximum}`, row.fixture.pre_state.approval_maximum_recovery_bootstraps === maximum && row.fixture.source_counters.values.root_admissions === expected && row.fixture.source_counters.values.root_attempt_starts === expected, `${expected} admissions and starts`);
}
check("e0_missing_receipt", byId("SEC7-E0-GUARD-002").fixture.selected_rule === "EVIDENCE_REJECT", "missing receipt rejected before launch");
for (const id of ["SEC7-COUNTER-001", "SEC7-COUNTER-002", "SEC7-COUNTER-003", "SEC7-COUNTER-004", "SEC7-COUNTER-006", "SEC7-COUNTER-007", "SEC7-COUNTER-008", "SEC7-COUNTER-009", "SEC7-COUNTER-010"]) {
  check(`action_counter:${id}`, byId(id).fixture.action_record_delta.length === 1, `${byId(id).fixture.action_record_delta[0].record_type}`);
}
check("git_self_cycle", byId("SEC7-GIT-002").fixture.selected_rule === "G002" && byId("SEC7-GIT-002").fixture.fault_mutations.length === 1, "materialized self-cycle selects G002");
check("terminal_lower_field", Object.hasOwn(byId("SEC7-TERMINAL-001").fixture.observed_state_after_fault, "repository_identity") && byId("SEC7-TERMINAL-001").fixture.selected_rule === "SCHEMA_REJECT", "extra lower field physically present and rejected");

const capabilityRows = controls.filter((row) => row.fixture.schema === "tt-supervised-capability-witness-v1");
check("capability_count", capabilityRows.length === 27, `${capabilityRows.length}`);
for (const row of capabilityRows) {
  const independentlyValid = same(row.fixture.observed_descriptor, transition.candidate_boundary_descriptor);
  check(`capability_recompute:${row.id}`, row.fixture.derived_result.valid === independentlyValid, independentlyValid ? "exact descriptor" : "descriptor differs" );
}
check("capability_positive", byId("SEC7-CAP-VALID").fixture.derived_result.valid === true, "valid descriptor accepted");
check("capability_denials", capabilityRows.filter((row) => row.id !== "SEC7-CAP-VALID").every((row) => row.fixture.fault_mutations.length === 1 && row.fixture.derived_result.valid === false), "26/26 denied mutations materialized");

function computeResources(input) {
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
    const stack = [vertex.id]; let charge = 0; const members = [];
    while (stack.length) {
      const id = stack.pop(); if (seen.has(id)) continue;
      seen.add(id); members.push(id); charge += input.memory_vertices.find((candidate) => candidate.id === id).capacity;
      for (const neighbor of adjacency[id]) stack.push(neighbor);
    }
    components.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(0, ...components.map((component) => component.charge)), wall, io, disk, memory_components: components };
}

const resourceRows = controls.filter((row) => row.fixture.schema === "tt-supervised-resource-arithmetic-witness-v1");
for (const row of resourceRows) check(`resource_recompute:${row.id}`, same(computeResources(row.fixture.observed_input), row.fixture.derived_result), canonical(row.fixture.derived_result));
check("resource_positive", byId("SEC7-RESOURCE-001").fixture.derived_validation.valid === true && byId("SEC7-RESOURCE-001").fixture.derived_result.cpu === 52 && byId("SEC7-RESOURCE-001").fixture.derived_result.memory === 73, "CPU 52, memory 73");
check("resource_negative", ["SEC7-RESOURCE-002", "SEC7-RESOURCE-003", "SEC7-RESOURCE-004", "SEC7-RESOURCE-005"].every((id) => byId(id).fixture.derived_validation.valid === false), "4 wrong or changed claims rejected");

const preservedDir = join(dirname(here), "tt-supervised-executor-v6-review-bundle");
for (const [name, digest] of Object.entries(transition.preserved_v6_negative_evidence)) check(`preserved_v6:${name}`, sha256(readFileSync(join(preservedDir, name))) === digest && control.preserved_v6_negative_evidence[name] === digest, digest);

const report = {
  schema: "tt-supervised-executor-v7-local-verification-v1",
  status: "PASS",
  claim_boundary: ["MODEL-BOUND", "UNTESTED", "ZERO-RUN"],
  transition_sha256: sha256(readFileSync(transitionPath)),
  control_sha256: sha256(readFileSync(controlPath)),
  check_count: checks.length,
  checks,
};

process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
