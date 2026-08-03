import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const builderBytes = readFileSync(fileURLToPath(import.meta.url));
const protocol = "EXP-ECDLP-TT-SOURCE-COMPILER-001/tt-supervised-executor/8";

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

function clone(value) {
  return structuredClone(value);
}

function same(left, right) {
  return canonical(left) === canonical(right);
}

function writeJson(name, value) {
  writeFileSync(join(here, name), `${JSON.stringify(value, null, 2)}\n`);
}

function unique(values) {
  return [...new Set(values)];
}

function conditionMatches(actual, expected) {
  return Array.isArray(expected)
    ? expected.some((candidate) => canonical(candidate) === canonical(actual))
    : canonical(actual) === canonical(expected);
}

function predicateMatches(source, predicate) {
  return Object.entries(predicate).every(([field, expected]) => conditionMatches(source[field], expected));
}

function subsetMatches(actual, expected) {
  if (expected !== null && typeof expected === "object" && !Array.isArray(expected)) {
    return actual !== null && typeof actual === "object"
      && Object.entries(expected).every(([key, value]) => subsetMatches(actual[key], value));
  }
  return conditionMatches(actual, expected);
}

const phaseOrder = ["P0", "P1", "P2", "P3", "P4", "P5", "E0"];
const candidatePhases = phaseOrder.slice(0, 6);
const candidatePhaseModes = candidatePhases.map((phase) => `${phase}:not_applicable`);
const nonEvaluatePhaseModes = [...candidatePhaseModes, "E0:close_prior_failure"];
const allPhaseModes = [...nonEvaluatePhaseModes, "E0:evaluate"];
const attemptOrdinals = Array.from({ length: 33 }, (_, index) => `A${index}`);
const recoveryOrdinals = attemptOrdinals.slice(1);
const attemptIdentities = attemptOrdinals.map((ordinal) => ({
  run_mode: ordinal === "A0" ? "normal" : "recovery",
  admission_kind: ordinal === "A0" ? "normal" : "recovery",
  ordinal,
}));
const recoveryMaxima = Array.from({ length: 33 }, (_, index) => index);
const recoveryBudgetAvailableStates = recoveryMaxima.flatMap((maximum) =>
  Array.from({ length: maximum }, (_, consumed) => ({
    maximum,
    consumed,
    next_ordinal: `A${consumed + 1}`,
    status: "available",
  })),
);
const recoveryBudgetExhaustedStates = recoveryMaxima.map((maximum) => ({
  maximum,
  consumed: maximum,
  next_ordinal: "none",
  status: "exhausted",
}));
const liveStates = [
  "UNSEEN", "RESERVED", "LAUNCH_INTENT_DURABLE", "SPAWN_FAILED", "SPAWNED",
  "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME",
  "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE", "COMMIT_INTENT_DURABLE",
  "COMMIT_OBJECT_EXACT", "REF_APPLIED", "COMMITTED",
];
const liveEvents = [
  "reservation_durable", "launch_intent_durable", "spawn_returned_error",
  "spawn_returned_pid", "spawn_failure_terminal_durable", "child_reaped",
  "bounded_result_retained", "runtime_failure_terminal_durable", "content_durable",
  "valid_terminal_durable", "validation_failure_terminal_durable",
  "commit_intent_durable", "commit_object_exact", "initial_ref_cas_applied",
  "existing_ref_cas_applied", "commit_reparsed_exact", "root_crashed",
];
const privateMapStates = [
  "MAP_UNSEEN", "MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED",
  "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE", "not_applicable",
];
const recoveryPrivateMapIdentities = [
  { state: "not_applicable", binding: "not_applicable", relation: "valid" },
  { state: "MAP_OPENED_RECEIPT_DURABLE", binding: "valid_current", relation: "valid" },
  { state: "invalid", binding: "invalid", relation: "invalid" },
];
const privateMapEvents = [
  "request_open_intent", "open_syscall_success", "open_syscall_failure",
  "publish_opened_receipt", "dispatch_live_supervisor", "root_crashed",
  "private_map_open_syscall",
];

const resourceFixture = {
  schema: "tt-supervised-resource-input-v2",
  overlap_policy: "conservative_possible_overlap_complete",
  attempts: [
    { id: "A0", bootstrap_observed: 13, bootstrap_cap: 20, meter_observed_preterminal: 7, meter_preterminal_cap: 10, meter_terminal_cap: 2, wall_cap: 40, io_charge: 11, disk_charge: 5 },
    { id: "A1", bootstrap_observed: null, bootstrap_cap: 17, meter_observed_preterminal: 11, meter_preterminal_cap: 15, meter_terminal_cap: 2, wall_cap: 45, io_charge: 13, disk_charge: 7 },
  ],
  memory_vertices: [{ id: "A0", capacity: 31 }, { id: "A1", capacity: 37 }, { id: "closure", capacity: 5 }],
  possible_overlap_edges: [["A0", "A1"], ["A1", "closure"]],
};

function isSafeNonnegativeInteger(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function validateResourceInput(input) {
  if (input === null || typeof input !== "object" || Array.isArray(input)) return { ok: false, reason: "RESOURCE_INPUT_NOT_OBJECT" };
  const required = ["schema", "overlap_policy", "attempts", "memory_vertices", "possible_overlap_edges"];
  if (canonical(Object.keys(input).sort()) !== canonical(required.sort())) return { ok: false, reason: "RESOURCE_INPUT_KEYS_MISMATCH" };
  if (input.schema !== "tt-supervised-resource-input-v2") return { ok: false, reason: "RESOURCE_INPUT_SCHEMA_INVALID" };
  if (input.overlap_policy !== "conservative_possible_overlap_complete") return { ok: false, reason: "RESOURCE_OVERLAP_POLICY_INVALID" };
  if (!Array.isArray(input.attempts) || input.attempts.length === 0) return { ok: false, reason: "RESOURCE_ATTEMPTS_INVALID" };
  const attemptIds = new Set();
  const chargeFields = ["bootstrap_cap", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge"];
  for (const attempt of input.attempts) {
    const fields = ["id", "bootstrap_observed", "bootstrap_cap", "meter_observed_preterminal", "meter_preterminal_cap", "meter_terminal_cap", "wall_cap", "io_charge", "disk_charge"];
    if (attempt === null || typeof attempt !== "object" || canonical(Object.keys(attempt).sort()) !== canonical(fields.sort())) return { ok: false, reason: "RESOURCE_ATTEMPT_KEYS_INVALID" };
    if (!attemptOrdinals.includes(attempt.id) || attemptIds.has(attempt.id)) return { ok: false, reason: "RESOURCE_ATTEMPT_ID_INVALID" };
    attemptIds.add(attempt.id);
    if (!chargeFields.every((field) => isSafeNonnegativeInteger(attempt[field]))) return { ok: false, reason: "RESOURCE_ATTEMPT_CHARGE_INVALID" };
    for (const [observedField, capField] of [["bootstrap_observed", "bootstrap_cap"], ["meter_observed_preterminal", "meter_preterminal_cap"]]) {
      const observed = attempt[observedField];
      if (observed !== null && (!isSafeNonnegativeInteger(observed) || observed > attempt[capField])) return { ok: false, reason: "RESOURCE_OBSERVATION_INVALID" };
    }
  }
  if (!Array.isArray(input.memory_vertices) || input.memory_vertices.length === 0) return { ok: false, reason: "RESOURCE_MEMORY_VERTICES_INVALID" };
  const vertexIds = new Set();
  for (const vertex of input.memory_vertices) {
    if (vertex === null || typeof vertex !== "object" || canonical(Object.keys(vertex).sort()) !== canonical(["capacity", "id"])) return { ok: false, reason: "RESOURCE_MEMORY_VERTEX_KEYS_INVALID" };
    if (typeof vertex.id !== "string" || vertex.id.length === 0 || vertexIds.has(vertex.id) || !isSafeNonnegativeInteger(vertex.capacity)) return { ok: false, reason: "RESOURCE_MEMORY_VERTEX_INVALID" };
    vertexIds.add(vertex.id);
  }
  if (!Array.isArray(input.possible_overlap_edges)) return { ok: false, reason: "RESOURCE_OVERLAP_EDGES_INVALID" };
  const edgeKeys = new Set();
  for (const edge of input.possible_overlap_edges) {
    if (!Array.isArray(edge) || edge.length !== 2 || !vertexIds.has(edge[0]) || !vertexIds.has(edge[1]) || edge[0] === edge[1]) return { ok: false, reason: "RESOURCE_OVERLAP_EDGE_ENDPOINT_INVALID" };
    const key = [...edge].sort().join("\u0000");
    if (edgeKeys.has(key)) return { ok: false, reason: "RESOURCE_OVERLAP_EDGE_DUPLICATE" };
    edgeKeys.add(key);
  }
  return { ok: true, reason: "RESOURCE_INPUT_VALID" };
}

function makeSchema({ fixed = {}, domains = {}, notes = {} }) {
  const permitted = unique([...Object.keys(fixed), ...Object.keys(domains)]).sort();
  return {
    required: permitted,
    permitted,
    fixed,
    domains,
    additional_properties: false,
    domain_cardinality: Object.values(domains).reduce((product, values) => product * values.length, 1),
    ...notes,
  };
}

const common = {
  attempt_admission: {
    variant: "attempt_admission_v2", evaluation_context: "attempt_admission",
    root_lock: "valid_current", campaign_terminal: "absent",
    prior_attempt_closure: "none_unclosed", admission_record: "valid_current",
    admission_binding: "valid_current", repository_action_count: 0, dispatcher_match: true,
  },
  prior_attempt_safety: {
    variant: "prior_attempt_safety_v2", evaluation_context: "prior_attempt_safety",
    root_lock: "valid_current", campaign_terminal: "absent",
    safety_scope: "process_identity_and_launch_records_only", dispatcher_match: true,
  },
  live_candidate: {
    variant: "live_candidate_action_v3", evaluation_context: "live_supervisor",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid",
    private_map_state: "not_applicable", private_map_binding: "not_applicable",
    capability_receipt: "valid_current", phase_private_map_relation: "valid",
    phase_capability_relation: "valid", dispatcher_match: true,
  },
  live_e0: {
    variant: "live_e0_evaluate_action_v3", evaluation_context: "live_supervisor",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid", phase_mode: "E0:evaluate",
    private_map_state: "MAP_OPENED_RECEIPT_DURABLE", private_map_binding: "valid_current",
    capability_receipt: "valid_current", phase_private_map_relation: "valid",
    phase_capability_relation: "valid", dispatcher_match: true,
  },
  recovery: {
    variant: "recovery_reconstruction_v3", evaluation_context: "recovery_reconstruction",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", admission_binding: "valid_current", admission_kind: "recovery",
    prior_attempt_closure: "none_unclosed", consumption_record: "valid",
    private_selection_match: "match", repository_identity: "valid", phase_chain: "valid",
    capability_receipt: "valid_current", phase_capability_relation: "valid",
    dispatcher_match: true,
  },
  progression: {
    variant: "campaign_progression_v3", evaluation_context: "campaign_progression",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid", active_phase: "none",
    dispatcher_match: true,
  },
  meter: {
    variant: "meter_finalization_v3", evaluation_context: "meter_finalization",
    root_lock: "valid_current", bootstrap_status: "reaped",
    admission_record: "valid_current", attempt_record: "valid_current",
    admission_binding: "valid_current", attempt_relation: "valid",
    launch_identity_evidence: "complete", kernel_observation_evidence: "complete",
    resource_measurement: "valid_current", dispatcher_match: true,
  },
  e0_map: {
    variant: "e0_private_map_v3", evaluation_context: "e0_private_map",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", reservation_binding: "valid_current",
    evaluator_identity: "valid_current", dispatcher_match: true,
  },
};

const sourceSchemas = {
  prelock_v2: makeSchema({
    fixed: { variant: "prelock_v2", evaluation_context: "entry_preflight" },
    domains: { root_lock: ["invalid", "conflict", "unavailable"] },
    notes: { campaign_fields_forbidden: true },
  }),
  locked_terminal_v3: makeSchema({
    fixed: { variant: "locked_terminal_v3", evaluation_context: "entry_preflight", root_lock: "valid_current" },
    domains: { campaign_terminal: ["valid_attested_closure", "valid_infrastructure_failure", "invalid"] },
    notes: { lower_campaign_fields_forbidden: true },
  }),
  locked_prior_unclosed_v2: makeSchema({
    fixed: { variant: "locked_prior_unclosed_v2", evaluation_context: "entry_preflight", root_lock: "valid_current", campaign_terminal: "absent" },
    domains: { prior_attempt_closure: ["valid_unclosed", "invalid", "conflict"] },
    notes: { lower_campaign_fields_forbidden_except_safety_handoff: true },
  }),
  locked_dangling_admission_v2: makeSchema({
    fixed: {
      variant: "locked_dangling_admission_v2", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
    },
    domains: {
      admission_record: ["valid_unstarted", "invalid", "conflict"],
      admission_kind: ["normal", "recovery", "invalid"],
      admission_ordinal: [...attemptOrdinals, "invalid"],
      admission_binding: ["valid_current", "invalid"],
    },
  }),
  locked_entry_ineligible_v3: makeSchema({
    fixed: {
      variant: "locked_entry_ineligible_v3", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent", admission_record: "absent",
    },
    domains: {
      run_mode: ["normal", "recovery"], normal_consumption: ["absent", "valid"],
      recovery_budget: ["not_applicable", "available", "exhausted"],
      approval_maximum_recovery_bootstraps: ["not_applicable", ...recoveryMaxima],
      recovery_slots_consumed: ["not_applicable", ...recoveryMaxima],
      budget_relation: ["not_applicable", "available_exact", "exhausted_exact", "invalid"],
    },
    notes: { repository_and_phase_fields_forbidden: true },
  }),
  locked_normal_eligible_v3: makeSchema({
    fixed: {
      variant: "locked_normal_eligible_v3", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
      admission_record: "absent", run_mode: "normal", admission_ordinal: "A0", normal_consumption: "absent",
      private_selection_match: "not_applicable", recovery_budget: "not_applicable",
    },
    domains: {
      recovery_slot: ["not_applicable", "valid_current", "invalid"],
      repository_identity: ["valid", "invalid", "conflict"],
      phase_chain: ["valid", "invalid", "conflict"],
      ref_relation: ["absent_initial", "at_last_commit", "other", "invalid"],
      initial_phase_state: ["empty", "recoverable_nonempty", "invalid"],
      entry_product_relation: ["valid_normal", "valid_recovery", "invalid"],
    },
  }),
  locked_recovery_eligible_v3: makeSchema({
    fixed: {
      variant: "locked_recovery_eligible_v3", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
      admission_record: "absent", run_mode: "recovery", normal_consumption: "valid",
      private_selection_match: "match", recovery_budget: "available", budget_relation: "available_exact",
    },
    domains: {
      recovery_budget_state: recoveryBudgetAvailableStates,
      recovery_slot: ["not_applicable", "valid_current", "invalid"],
      repository_identity: ["valid", "invalid", "conflict"],
      phase_chain: ["valid", "invalid", "conflict"],
      ref_relation: ["absent_initial", "at_last_commit", "other", "invalid"],
      initial_phase_state: ["empty", "recoverable_nonempty", "invalid"],
      entry_product_relation: ["valid_normal", "valid_recovery", "invalid"],
    },
  }),
  attempt_admission_v2: makeSchema({
    fixed: common.attempt_admission,
    domains: {
      run_mode: ["normal", "recovery"], admission_kind: ["normal", "recovery", "invalid"],
      admission_ordinal: [...attemptOrdinals, "invalid"], linked_attempt_record: ["absent", "durable", "invalid"],
      normal_consumption_binding: ["valid", "not_applicable", "invalid"],
      recovery_budget_binding: ["valid", "not_applicable", "invalid"],
    },
  }),
  prior_attempt_safety_v2: makeSchema({
    fixed: common.prior_attempt_safety,
    domains: {
      selected_precedence_reason: ["RESOURCE_PRIOR_ATTEMPT_OBSERVATION_INCOMPLETE", "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID"],
      precedence_binding: ["valid", "invalid"],
      prior_attempt_record: ["valid_unclosed", "invalid", "conflict"],
      attempt_ordinal: attemptOrdinals,
      launch_identity_evidence: ["complete", "absent", "invalid"],
      kernel_observation_evidence: ["complete", "absent", "invalid"],
      process_absence: ["kernel_confirmed_absent", "one_exact_identity_live", "ambiguous", "unkillable", "invalid"],
    },
    notes: { ordinary_repository_and_phase_fields_forbidden: true },
  }),
  live_candidate_action_v3: makeSchema({
    fixed: common.live_candidate,
    domains: {
      run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, phase_mode: nonEvaluatePhaseModes,
      state: liveStates, result_disposition: ["not_applicable", true, false], launch_prerequisite: ["not_applicable", "satisfied", "invalid"],
    },
  }),
  live_e0_evaluate_action_v3: makeSchema({
    fixed: common.live_e0,
    domains: {
      run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, state: liveStates,
      result_disposition: ["not_applicable", true, false], launch_prerequisite: ["not_applicable", "satisfied", "invalid"],
    },
  }),
  live_transition_candidate_v3: makeSchema({
    fixed: { ...common.live_candidate, variant: "live_transition_candidate_v3", evaluation_context: "live_transition", event_record_binding: "valid_current" },
    domains: { run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, phase_mode: nonEvaluatePhaseModes, state: liveStates, event: liveEvents },
  }),
  live_transition_e0_evaluate_v3: makeSchema({
    fixed: { ...common.live_e0, variant: "live_transition_e0_evaluate_v3", evaluation_context: "live_transition", event_record_binding: "valid_current" },
    domains: { run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, state: liveStates, event: liveEvents },
  }),
  recovery_reconstruction_v3: makeSchema({
    fixed: common.recovery,
    domains: {
      run_mode: ["recovery"], attempt_ordinal: recoveryOrdinals, phase_mode: allPhaseModes, state: liveStates,
      private_map_identity: recoveryPrivateMapIdentities,
      process_reconciliation: ["not_applicable", "kernel_confirmed_absent", "one_exact_identity_live", "multiple_token_matches", "pid_identity_mismatch", "unkillable", "invalid"],
      recoverable_result: ["not_applicable", true, false],
    },
  }),
  campaign_progression_v3: makeSchema({
    fixed: common.progression,
    domains: {
      run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, trigger: ["normal_consumption", "phase_committed"],
      last_committed_phase: ["none", ...phaseOrder],
      last_phase_outcome: ["none", "valid_outcome", "harness_failure", "quarantine"],
      ref_relation: ["absent_initial", "at_last_commit", "other", "invalid"],
    },
  }),
  meter_finalization_v3: makeSchema({
    fixed: common.meter,
    domains: {
      attempt_identity: attemptIdentities,
      process_absence: ["kernel_confirmed_absent", "one_exact_identity_live", "ambiguous", "unkillable"],
      durable_state: ["valid", "invalid"], terminal_request: ["absent", "attested_closure", "infrastructure_failure", "invalid", "conflict"],
      resource_receipt: ["absent", "durable", "invalid"], attempt_end: ["absent", "durable", "invalid"],
      campaign_terminal: ["absent", "valid_attested_closure", "valid_infrastructure_failure", "invalid"],
      recalculation: ["not_started", "complete", "invalid"], lock_release: ["held", "released", "invalid"],
    },
  }),
  e0_private_map_v3: makeSchema({
    fixed: common.e0_map,
    domains: {
      run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, e0_mode: ["evaluate", "close_prior_failure"],
      map_state: privateMapStates, event: privateMapEvents,
      descriptor_state: ["absent", "trusted_meter_only", "closed", "invalid"],
    },
  }),
  git_commit_validation_v2: makeSchema({
    fixed: {
      variant: "git_commit_validation_v2", evaluation_context: "repository_validation",
      root_lock: "valid_current", campaign_terminal: "absent", repository_identity: "valid",
      phase_chain: "valid", dispatcher_match: true,
    },
    domains: {
      run_mode: ["normal", "recovery"], attempt_ordinal: attemptOrdinals, phase_mode: allPhaseModes,
      commit_intent_relation: ["absent", "valid_self_excluding", "invalid_self_including", "invalid"],
      commit_object_state: ["absent", "exact", "invalid"],
      ref_relation: ["absent_initial", "at_parent", "other", "invalid"],
      cas_status: ["not_attempted", "applied", "conflict"],
    },
  }),
};

function materializedRule({ id, priority, context, sourceSchema, when, state, action, reason, nextContext = context }) {
  if (sourceSchemas[sourceSchema].fixed.evaluation_context !== context) throw new Error(`${id}: context ${context} disagrees with ${sourceSchema}`);
  const predicate = { ...(sourceSchemas[sourceSchema].fixed || {}), ...when };
  for (const field of Object.keys(predicate)) {
    if (!sourceSchemas[sourceSchema].permitted.includes(field)) throw new Error(`${id}: field ${field} absent from ${sourceSchema}`);
  }
  return {
    id, priority, evaluation_context: context, source_schema: sourceSchema,
    compiled_predicate: predicate, compiled_predicate_sha256: sha256(predicate),
    state, next_action: action, reason, next_context: nextContext,
  };
}

const rules = [];
const add = (spec) => rules.push(materializedRule(spec));

add({ id: "E000", priority: 1, context: "entry_preflight", sourceSchema: "prelock_v2", when: { root_lock: ["invalid", "conflict"] }, state: "ROOT_LOCK_INVALID", action: "reject_root_lock_invalid_no_write", reason: "BOOTSTRAP_CAMPAIGN_LOCK_IDENTITY_INVALID" });
add({ id: "E001", priority: 2, context: "entry_preflight", sourceSchema: "prelock_v2", when: { root_lock: "unavailable" }, state: "ROOT_LOCK_UNAVAILABLE", action: "reject_root_lock_unavailable_no_write", reason: "BOOTSTRAP_CAMPAIGN_ROOT_ALREADY_LIVE" });
add({ id: "E002", priority: 3, context: "entry_preflight", sourceSchema: "locked_terminal_v3", when: { campaign_terminal: "valid_attested_closure" }, state: "CAMPAIGN_TERMINAL", action: "exit_terminal_read_only", reason: "CAMPAIGN_TERMINAL_VALID_ATTESTED_CLOSURE" });
add({ id: "E003", priority: 4, context: "entry_preflight", sourceSchema: "locked_terminal_v3", when: { campaign_terminal: "valid_infrastructure_failure" }, state: "CAMPAIGN_TERMINAL", action: "exit_terminal_read_only", reason: "CAMPAIGN_TERMINAL_VALID_INFRASTRUCTURE_FAILURE" });
add({ id: "E004", priority: 5, context: "entry_preflight", sourceSchema: "locked_terminal_v3", when: { campaign_terminal: "invalid" }, state: "INVALID_TERMINAL_UNRECOVERABLE", action: "exit_invalid_terminal_read_only", reason: "CAMPAIGN_TERMINAL_INVALID_OCCUPIED_PATH" });
add({ id: "E005", priority: 6, context: "entry_preflight", sourceSchema: "locked_prior_unclosed_v2", when: { prior_attempt_closure: "valid_unclosed" }, state: "PRIOR_ATTEMPT_SAFETY_REQUIRED", action: "handoff_prior_attempt_safety_scan", reason: "RESOURCE_PRIOR_ATTEMPT_OBSERVATION_INCOMPLETE", nextContext: "prior_attempt_safety" });
add({ id: "E006", priority: 7, context: "entry_preflight", sourceSchema: "locked_prior_unclosed_v2", when: { prior_attempt_closure: ["invalid", "conflict"] }, state: "PRIOR_ATTEMPT_SAFETY_REQUIRED", action: "handoff_prior_attempt_safety_scan", reason: "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID", nextContext: "prior_attempt_safety" });
add({ id: "E007", priority: 8, context: "entry_preflight", sourceSchema: "locked_dangling_admission_v2", when: { admission_record: "valid_unstarted", admission_kind: ["normal", "recovery"], admission_ordinal: attemptOrdinals, admission_binding: "valid_current" }, state: "ADMISSION_ATTEMPT_START_READY", action: "handoff_attempt_admission", reason: "ADMISSION_DURABLE_ATTEMPT_START_ABSENT", nextContext: "attempt_admission" });
add({ id: "E008", priority: 9, context: "entry_preflight", sourceSchema: "locked_dangling_admission_v2", when: { admission_record: ["invalid", "conflict"] }, state: "ADMISSION_INVALID", action: "request_infrastructure_failure_no_new_attempt", reason: "ADMISSION_RECORD_INVALID" });
add({ id: "E009", priority: 10, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v3", when: { run_mode: "normal", normal_consumption: "valid", recovery_budget: "not_applicable", approval_maximum_recovery_bootstraps: "not_applicable", recovery_slots_consumed: "not_applicable", budget_relation: "not_applicable" }, state: "NORMAL_REPLAY_REJECTED", action: "reject_normal_replay_no_write", reason: "CONSUMPTION_NORMAL_REPLAY" });
add({ id: "E010", priority: 11, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v3", when: { run_mode: "recovery", normal_consumption: "absent", approval_maximum_recovery_bootstraps: recoveryMaxima, recovery_slots_consumed: 0, budget_relation: "not_applicable" }, state: "RECOVERY_REJECTED", action: "reject_recovery_without_consumption_no_write", reason: "CONSUMPTION_RECOVERY_WITHOUT_RECORD" });
add({ id: "E011", priority: 12, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v3", when: { run_mode: "recovery", normal_consumption: "valid", recovery_budget: "exhausted", approval_maximum_recovery_bootstraps: recoveryMaxima, recovery_slots_consumed: recoveryMaxima, budget_relation: "exhausted_exact" }, state: "RECOVERY_EXHAUSTED_UNTERMINATED", action: "reject_recovery_exhausted_no_write", reason: "CONSUMPTION_RECOVERY_BUDGET_EXHAUSTED" });
add({ id: "E012", priority: 13, context: "entry_preflight", sourceSchema: "locked_normal_eligible_v3", when: { normal_consumption: "absent", private_selection_match: "not_applicable", recovery_budget: "not_applicable", recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: "absent_initial", initial_phase_state: "empty", entry_product_relation: "valid_normal" }, state: "NORMAL_ADMISSION_READY", action: "reserve_normal_admission", reason: "ADMISSION_NORMAL_RESERVATION_READY", nextContext: "attempt_admission" });
add({ id: "E013", priority: 14, context: "entry_preflight", sourceSchema: "locked_recovery_eligible_v3", when: { normal_consumption: "valid", private_selection_match: "match", recovery_budget: "available", recovery_budget_state: recoveryBudgetAvailableStates, budget_relation: "available_exact", recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: ["absent_initial", "at_last_commit"], initial_phase_state: ["empty", "recoverable_nonempty"], entry_product_relation: "valid_recovery" }, state: "RECOVERY_ADMISSION_READY", action: "reserve_recovery_admission", reason: "ADMISSION_RECOVERY_RESERVATION_READY", nextContext: "attempt_admission" });

add({ id: "D001", priority: 1, context: "attempt_admission", sourceSchema: "attempt_admission_v2", when: { run_mode: "normal", admission_kind: "normal", admission_ordinal: "A0", linked_attempt_record: "absent", normal_consumption_binding: "valid", recovery_budget_binding: "not_applicable" }, state: "ATTEMPT_START_READY", action: "write_linked_attempt_start", reason: "ADMISSION_NORMAL_LINKED_START_READY" });
add({ id: "D002", priority: 2, context: "attempt_admission", sourceSchema: "attempt_admission_v2", when: { run_mode: "recovery", admission_kind: "recovery", admission_ordinal: recoveryOrdinals, linked_attempt_record: "absent", normal_consumption_binding: "valid", recovery_budget_binding: "valid" }, state: "ATTEMPT_START_READY", action: "write_linked_attempt_start", reason: "ADMISSION_RECOVERY_LINKED_START_READY" });
add({ id: "D003", priority: 3, context: "attempt_admission", sourceSchema: "attempt_admission_v2", when: { run_mode: "normal", admission_kind: "normal", admission_ordinal: "A0", linked_attempt_record: "durable", normal_consumption_binding: "valid", recovery_budget_binding: "not_applicable" }, state: "NORMAL_ATTEMPT_STARTED", action: "dispatch_normal_campaign_progression", reason: "ADMISSION_NORMAL_START_DURABLE", nextContext: "campaign_progression" });
add({ id: "D004", priority: 4, context: "attempt_admission", sourceSchema: "attempt_admission_v2", when: { run_mode: "recovery", admission_kind: "recovery", admission_ordinal: recoveryOrdinals, linked_attempt_record: "durable", normal_consumption_binding: "valid", recovery_budget_binding: "valid" }, state: "RECOVERY_ATTEMPT_STARTED", action: "dispatch_recovery_reconstruction", reason: "ADMISSION_RECOVERY_START_DURABLE", nextContext: "recovery_reconstruction" });

const priorReasons = ["RESOURCE_PRIOR_ATTEMPT_OBSERVATION_INCOMPLETE", "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID"];
add({ id: "S001", priority: 1, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v2", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", prior_attempt_record: ["valid_unclosed", "invalid", "conflict"], launch_identity_evidence: "complete", kernel_observation_evidence: "complete", process_absence: "kernel_confirmed_absent" }, state: "PRIOR_ATTEMPT_METER_FINALIZATION_READY", action: "handoff_meter_finalization_infrastructure", reason: "RESOURCE_PRIOR_PROCESS_ABSENCE_PROVED", nextContext: "meter_finalization" });
add({ id: "S002", priority: 2, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v2", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: "complete", kernel_observation_evidence: "complete", process_absence: "one_exact_identity_live" }, state: "PRIOR_PROCESS_RECONCILIATION", action: "retain_lock_and_reconcile_prior_process", reason: "RESOURCE_PRIOR_PROCESS_STILL_LIVE" });
add({ id: "S003", priority: 3, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v2", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: "complete", kernel_observation_evidence: "complete", process_absence: ["ambiguous", "unkillable", "invalid"] }, state: "PRIOR_PROCESS_ABSENCE_UNPROVED", action: "retain_lock_and_stop_no_terminal", reason: "RESOURCE_PRIOR_PROCESS_ABSENCE_UNPROVED" });
add({ id: "S004", priority: 4, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v2", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: ["absent", "invalid"] }, state: "PRIOR_PROCESS_EVIDENCE_INVALID", action: "retain_lock_and_stop_no_terminal", reason: "RESOURCE_PRIOR_LAUNCH_IDENTITY_INVALID" });

function addLiveActions(sourceSchema, phaseModes) {
  const prefix = sourceSchema === "live_e0_evaluate_action_v3" ? "AE" : "AN";
  const ordinary = { phase_mode: phaseModes, result_disposition: "not_applicable" };
  add({ id: `${prefix}001`, priority: 1, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "RESERVED", launch_prerequisite: "satisfied" }, state: "RESERVED", action: "create_launch_intent", reason: "STATE_LIVE_CREATE_LAUNCH_INTENT" });
  add({ id: `${prefix}002`, priority: 2, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "LAUNCH_INTENT_DURABLE", launch_prerequisite: "not_applicable" }, state: "LAUNCH_INTENT_DURABLE", action: "spawn_phase", reason: "STATE_LIVE_SPAWN_PHASE" });
  add({ id: `${prefix}003`, priority: 3, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "SPAWN_FAILED", launch_prerequisite: "not_applicable" }, state: "SPAWN_FAILED", action: "publish_harness_failure_phase_terminal", reason: "STATE_LIVE_CLOSE_SPAWN_FAILURE" });
  add({ id: `${prefix}004`, priority: 4, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "SPAWNED", launch_prerequisite: "not_applicable" }, state: "SPAWNED", action: "reap_phase", reason: "STATE_LIVE_REAP_PHASE" });
  add({ id: `${prefix}005R`, priority: 5, context: "live_supervisor", sourceSchema, when: { state: "REAPED", phase_mode: phaseModes, result_disposition: true, launch_prerequisite: "not_applicable" }, state: "REAPED", action: "retain_bounded_result", reason: "STATE_LIVE_RETAIN_VALID_RESULT" });
  add({ id: `${prefix}005F`, priority: 6, context: "live_supervisor", sourceSchema, when: { state: "REAPED", phase_mode: phaseModes, result_disposition: false, launch_prerequisite: "not_applicable" }, state: "REAPED", action: "publish_runtime_failure_phase_terminal", reason: "STATE_LIVE_RETAIN_RESULT_FAILED" });
  add({ id: `${prefix}006`, priority: 7, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "RESULT_RETAINED", launch_prerequisite: "not_applicable" }, state: "RESULT_RETAINED", action: "publish_phase_content", reason: "STATE_LIVE_PUBLISH_CONTENT" });
  add({ id: `${prefix}007`, priority: 8, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "CONTENT_PUBLISHED", launch_prerequisite: "not_applicable" }, state: "CONTENT_PUBLISHED", action: "publish_valid_or_harness_phase_terminal", reason: "STATE_LIVE_PUBLISH_PHASE_TERMINAL" });
  add({ id: `${prefix}008`, priority: 9, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"], launch_prerequisite: "not_applicable" }, state: "REPOSITORY_VALIDATION_REQUIRED", action: "handoff_repository_validation", reason: "STATE_LIVE_PHASE_TERMINAL_REPOSITORY_HANDOFF", nextContext: "repository_validation" });
  add({ id: `${prefix}009`, priority: 10, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: ["COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED"], launch_prerequisite: "not_applicable" }, state: "REPOSITORY_VALIDATION_REQUIRED", action: "handoff_repository_validation", reason: "STATE_LIVE_GIT_STATE_REPOSITORY_HANDOFF", nextContext: "repository_validation" });
  add({ id: `${prefix}010`, priority: 11, context: "live_supervisor", sourceSchema, when: { ...ordinary, state: "COMMITTED", launch_prerequisite: "not_applicable" }, state: "COMMITTED", action: "dispatch_campaign_progression", reason: "STATE_LIVE_DISPATCH_COMMITTED_PHASE", nextContext: "campaign_progression" });
}

addLiveActions("live_candidate_action_v3", nonEvaluatePhaseModes);
addLiveActions("live_e0_evaluate_action_v3", ["E0:evaluate"]);

const liveEdges = [
  ["L001", ["UNSEEN"], "reservation_durable", "RESERVED"],
  ["L002", ["RESERVED"], "launch_intent_durable", "LAUNCH_INTENT_DURABLE"],
  ["L003", ["LAUNCH_INTENT_DURABLE"], "spawn_returned_error", "SPAWN_FAILED"],
  ["L004", ["LAUNCH_INTENT_DURABLE"], "spawn_returned_pid", "SPAWNED"],
  ["L005", ["SPAWN_FAILED"], "spawn_failure_terminal_durable", "TERMINAL_HARNESS_FAILURE"],
  ["L006", ["SPAWNED"], "child_reaped", "REAPED"],
  ["L007", ["REAPED"], "bounded_result_retained", "RESULT_RETAINED"],
  ["L008", ["REAPED"], "runtime_failure_terminal_durable", "TERMINAL_HARNESS_FAILURE"],
  ["L009", ["RESULT_RETAINED"], "content_durable", "CONTENT_PUBLISHED"],
  ["L010", ["CONTENT_PUBLISHED"], "valid_terminal_durable", "TERMINAL_VALID_OUTCOME"],
  ["L011", ["CONTENT_PUBLISHED"], "validation_failure_terminal_durable", "TERMINAL_HARNESS_FAILURE"],
  ["L012", ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"], "commit_intent_durable", "COMMIT_INTENT_DURABLE"],
  ["L013", ["COMMIT_INTENT_DURABLE"], "commit_object_exact", "COMMIT_OBJECT_EXACT"],
  ["L014I", ["COMMIT_OBJECT_EXACT"], "initial_ref_cas_applied", "REF_APPLIED"],
  ["L014E", ["COMMIT_OBJECT_EXACT"], "existing_ref_cas_applied", "REF_APPLIED"],
  ["L015", ["REF_APPLIED"], "commit_reparsed_exact", "COMMITTED"],
];

function addLiveEventRules(sourceSchema, phaseModes) {
  for (const [id, from, event, to] of liveEdges) {
    if (id === "L014I" && !phaseModes.includes("P0:not_applicable")) continue;
    const guardedPhases = id === "L014I" ? ["P0:not_applicable"] : id === "L014E" ? phaseModes.filter((mode) => mode !== "P0:not_applicable") : phaseModes;
    if (guardedPhases.length === 0) continue;
    add({ id: `${sourceSchema.includes("e0") ? "TE" : "TN"}-${id}`, priority: 100 + rules.length, context: "live_transition", sourceSchema, when: { state: from, event, phase_mode: guardedPhases }, state: to, action: "accept_declared_transition", reason: "STATE_DECLARED_EVENT", nextContext: "live_supervisor" });
  }
  for (const state of liveStates) {
    add({ id: `${sourceSchema.includes("e0") ? "TEH" : "TNH"}-${state}`, priority: 1000 + rules.length, context: "live_transition", sourceSchema, when: { state, event: "root_crashed", phase_mode: phaseModes }, state: "RECOVERY_HANDOFF", action: "handoff_recovery_reconstruction", reason: "STATE_ROOT_CRASH_HANDOFF", nextContext: "recovery_reconstruction" });
  }
}

addLiveEventRules("live_transition_candidate_v3", nonEvaluatePhaseModes);
addLiveEventRules("live_transition_e0_evaluate_v3", ["E0:evaluate"]);

const recoveryActions = [
  ["R001", "UNSEEN", "resume_campaign_progression_from_predecessor", "STATE_RECOVERY_PHASE_UNSEEN"],
  ["R002", "RESERVED", "publish_quarantine_phase_terminal", "STATE_PHASE_WITHOUT_TERMINAL"],
  ["R003", ["LAUNCH_INTENT_DURABLE", "SPAWNED"], "reconcile_process_then_publish_quarantine_phase_terminal", "STATE_UNREAPED_PROCESS_POSSIBLE"],
  ["R004", "SPAWN_FAILED", "publish_harness_failure_phase_terminal", "STATE_RECOVERY_CLOSE_SPAWN_FAILURE"],
  ["R006", "RESULT_RETAINED", "publish_phase_content", "STATE_RECOVERY_RESULT_RETAINED"],
  ["R007", "CONTENT_PUBLISHED", "publish_valid_or_harness_phase_terminal", "STATE_RECOVERY_CONTENT_PUBLISHED"],
  ["R008", ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"], "handoff_repository_validation", "STATE_RECOVERY_PHASE_TERMINAL"],
  ["R009", ["COMMIT_INTENT_DURABLE", "COMMIT_OBJECT_EXACT", "REF_APPLIED"], "handoff_repository_validation", "STATE_RECOVERY_GIT_REPOSITORY_HANDOFF"],
  ["R011", "COMMITTED", "resume_campaign_progression_from_committed_phase", "STATE_RECOVERY_PHASE_COMMITTED"],
];
for (const [id, state, action, reason] of recoveryActions) {
  add({ id, priority: 100 + rules.length, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v3", when: { state, process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: "not_applicable" }, state: `RECOVERY_${Array.isArray(state) ? "MULTI" : state}`, action, reason, nextContext: action === "handoff_repository_validation" ? "repository_validation" : action.includes("progression") ? "campaign_progression" : "recovery_reconstruction" });
}
add({ id: "R005T", priority: 498, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v3", when: { state: "REAPED", process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: true }, state: "RECOVERY_RESULT_RETAIN_READY", action: "retain_recoverable_result", reason: "STATE_RECOVERY_RETAIN_VALID_RESULT" });
add({ id: "R005F", priority: 499, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v3", when: { state: "REAPED", process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: false }, state: "RECOVERY_QUARANTINE_READY", action: "publish_quarantine_phase_terminal", reason: "STATE_RECOVERY_RESULT_NOT_RETAINABLE" });
add({ id: "R013", priority: 502, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v3", when: { process_reconciliation: ["multiple_token_matches", "pid_identity_mismatch", "unkillable", "invalid"] }, state: "RECOVERY_INTEGRITY_INVALID", action: "request_infrastructure_failure", reason: "STATE_PROCESS_RECONCILIATION_FAILED" });

add({ id: "C001", priority: 1, context: "campaign_progression", sourceSchema: "campaign_progression_v3", when: { trigger: "normal_consumption", last_committed_phase: "none", last_phase_outcome: "none", ref_relation: "absent_initial" }, state: "NEXT_PHASE_READY", action: "reserve_P0_then_live_supervisor", reason: "STATE_NEXT_PHASE_P0", nextContext: "live_supervisor" });
add({ id: "C002", priority: 2, context: "campaign_progression", sourceSchema: "campaign_progression_v3", when: { trigger: "phase_committed", last_committed_phase: ["P0", "P1", "P2", "P3", "P4"], last_phase_outcome: "valid_outcome", ref_relation: "at_last_commit" }, state: "NEXT_PHASE_READY", action: "reserve_successor_then_live_supervisor", reason: "STATE_NEXT_CANDIDATE_PHASE", nextContext: "live_supervisor" });
add({ id: "C003", priority: 3, context: "campaign_progression", sourceSchema: "campaign_progression_v3", when: { trigger: "phase_committed", last_committed_phase: "P5", last_phase_outcome: "valid_outcome", ref_relation: "at_last_commit" }, state: "EVALUATOR_READY", action: "reserve_E0_evaluate_then_private_map", reason: "STATE_EVALUATOR_AFTER_P5", nextContext: "e0_private_map" });
add({ id: "C004", priority: 4, context: "campaign_progression", sourceSchema: "campaign_progression_v3", when: { trigger: "phase_committed", last_committed_phase: candidatePhases, last_phase_outcome: ["harness_failure", "quarantine"], ref_relation: "at_last_commit" }, state: "CLOSURE_READY", action: "reserve_E0_close_prior_failure_then_live_supervisor", reason: "STATE_CLOSURE_AFTER_FAILED_PHASE", nextContext: "live_supervisor" });
add({ id: "C005", priority: 5, context: "campaign_progression", sourceSchema: "campaign_progression_v3", when: { trigger: "phase_committed", last_committed_phase: "E0", last_phase_outcome: ["valid_outcome", "harness_failure", "quarantine"], ref_relation: "at_last_commit" }, state: "CAMPAIGN_CLOSURE_READY", action: "request_attested_closure", reason: "STATE_E0_COMMITTED", nextContext: "meter_finalization" });

add({ id: "M001", priority: 1, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: ["one_exact_identity_live", "ambiguous", "unkillable"], campaign_terminal: ["absent", "valid_attested_closure", "valid_infrastructure_failure"], lock_release: "held" }, state: "METER_PROCESS_RECONCILIATION", action: "retain_lock_and_reconcile_processes", reason: "METER_PROCESS_ABSENCE_NOT_PROVED" });
add({ id: "M002", priority: 2, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "absent", attempt_end: "absent", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "RESOURCE_WRITE_READY", action: "write_resource_receipt_only", reason: "METER_RESOURCE_RECEIPT_READY" });
add({ id: "M003", priority: 3, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "absent", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "ATTEMPT_END_WRITE_READY", action: "write_attempt_end_only", reason: "METER_ATTEMPT_END_READY" });
add({ id: "M004", priority: 4, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", durable_state: "valid", terminal_request: "absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "RECOVERABLE_RELEASE_READY", action: "release_recoverable_lock", reason: "METER_RECOVERABLE_RELEASE_READY" });
add({ id: "M005", priority: 5, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", durable_state: "valid", terminal_request: "attested_closure", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "ATTESTED_TERMINAL_WRITE_READY", action: "publish_attested_terminal_only", reason: "METER_ATTESTED_TERMINAL_READY" });
add({ id: "M006", priority: 6, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", durable_state: ["valid", "invalid"], terminal_request: ["infrastructure_failure", "invalid", "conflict"], resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "INFRASTRUCTURE_TERMINAL_WRITE_READY", action: "publish_infrastructure_terminal_only", reason: "METER_INFRASTRUCTURE_TERMINAL_READY" });
add({ id: "M007", priority: 7, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", durable_state: "invalid", terminal_request: ["absent", "attested_closure"], resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "INFRASTRUCTURE_TERMINAL_WRITE_READY", action: "publish_infrastructure_terminal_only", reason: "METER_DURABLE_STATE_INVALID" });
add({ id: "M008", priority: 8, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: ["valid_attested_closure", "valid_infrastructure_failure"], recalculation: "not_started", lock_release: "held" }, state: "READONLY_RECALCULATION_READY", action: "perform_readonly_recalculation", reason: "METER_TERMINAL_DURABLE_RECALC_READY" });
add({ id: "M009", priority: 9, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: ["valid_attested_closure", "valid_infrastructure_failure"], recalculation: "complete", lock_release: "held" }, state: "FINAL_LOCK_RELEASE_READY", action: "release_final_lock", reason: "METER_READONLY_RECALC_COMPLETE" });
add({ id: "M010", priority: 10, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { campaign_terminal: "invalid", lock_release: "held" }, state: "INVALID_TERMINAL_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "CAMPAIGN_TERMINAL_INVALID_OCCUPIED_PATH" });
add({ id: "M011", priority: 11, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "invalid", campaign_terminal: "absent", lock_release: "held" }, state: "RESOURCE_RECEIPT_INVALID_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "METER_RESOURCE_RECEIPT_INVALID" });
add({ id: "M012", priority: 12, context: "meter_finalization", sourceSchema: "meter_finalization_v3", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "invalid", campaign_terminal: "absent", lock_release: "held" }, state: "ATTEMPT_END_INVALID_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "METER_ATTEMPT_END_INVALID" });

const e0MapRuleSpecs = [
  ["P001", "evaluate", "MAP_UNSEEN", "request_open_intent", "absent", "MAP_OPEN_INTENT_DURABLE", "write_private_map_open_intent", "E0_PRIVATE_MAP_INTENT_READY"],
  ["P002", "evaluate", "MAP_OPEN_INTENT_DURABLE", "open_syscall_success", "absent", "MAP_OPENED_UNRECEIPTED", "open_private_map_trusted_descriptor", "E0_PRIVATE_MAP_OPEN_SUCCEEDED"],
  ["P003", "evaluate", "MAP_OPEN_INTENT_DURABLE", "open_syscall_failure", "absent", "MAP_OPEN_FAILED_DURABLE", "publish_map_open_harness_failure_terminal", "E0_PRIVATE_MAP_OPEN_FAILED"],
  ["P004", "evaluate", "MAP_OPENED_UNRECEIPTED", "publish_opened_receipt", "trusted_meter_only", "MAP_OPENED_RECEIPT_DURABLE", "write_private_map_opened_receipt", "E0_PRIVATE_MAP_RECEIPT_READY"],
  ["P005", "evaluate", "MAP_OPENED_RECEIPT_DURABLE", "dispatch_live_supervisor", "trusted_meter_only", "E0_LIVE_READY", "dispatch_e0_live_supervisor", "E0_PRIVATE_MAP_LAUNCH_GATE_SATISFIED"],
  ["P006", "evaluate", "MAP_OPEN_FAILED_DURABLE", "dispatch_live_supervisor", "absent", "REPOSITORY_VALIDATION_REQUIRED", "handoff_repository_validation", "E0_PRIVATE_MAP_FAILURE_REPOSITORY_READY"],
];
for (const [id, mode, mapState, event, descriptorState, state, action, reason] of e0MapRuleSpecs) {
  add({ id, priority: rules.length + 1, context: "e0_private_map", sourceSchema: "e0_private_map_v3", when: { e0_mode: mode, map_state: mapState, event, descriptor_state: descriptorState }, state, action, reason, nextContext: action === "dispatch_e0_live_supervisor" ? "live_supervisor" : ["publish_map_open_harness_failure_terminal", "handoff_repository_validation"].includes(action) ? "repository_validation" : "e0_private_map" });
}
for (const mapState of privateMapStates.filter((state) => state !== "not_applicable")) {
  add({ id: `PH-${mapState}`, priority: rules.length + 100, context: "e0_private_map", sourceSchema: "e0_private_map_v3", when: { e0_mode: "evaluate", map_state: mapState, event: "root_crashed" }, state: "E0_RECOVERY_HANDOFF", action: "handoff_recovery_reconstruction", reason: "E0_PRIVATE_MAP_ROOT_CRASH", nextContext: "recovery_reconstruction" });
}
add({ id: "PCLOSE", priority: 9999, context: "e0_private_map", sourceSchema: "e0_private_map_v3", when: { e0_mode: "close_prior_failure", event: privateMapEvents }, state: "E0_PRIVATE_MAP_FORBIDDEN", action: "request_infrastructure_failure", reason: "E0_PRIVATE_MAP_FORBIDDEN_IN_CLOSURE_MODE" });

add({ id: "G000", priority: 1, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { commit_intent_relation: "absent", commit_object_state: "absent", cas_status: "not_attempted" }, state: "COMMIT_INTENT_CREATION_READY", action: "create_commit_intent", reason: "GIT_COMMIT_INTENT_ABSENT" });
add({ id: "G001", priority: 2, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { commit_intent_relation: "valid_self_excluding", commit_object_state: "absent", cas_status: "not_attempted" }, state: "COMMIT_OBJECT_CREATION_READY", action: "create_ledgered_commit_objects", reason: "GIT_COMMIT_INTENT_SELF_EXCLUDING" });
add({ id: "G002", priority: 3, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { commit_intent_relation: ["invalid_self_including", "invalid"] }, state: "GIT_INTENT_INVALID", action: "request_infrastructure_failure", reason: "GIT_COMMIT_INTENT_SELF_CYCLE" });
add({ id: "G003", priority: 4, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { phase_mode: "P0:not_applicable", commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "absent_initial", cas_status: "not_attempted" }, state: "INITIAL_CAS_READY", action: "cas_create_initial_ref", reason: "GIT_INITIAL_REF_RELATION_VALID" });
add({ id: "G004", priority: 5, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { phase_mode: allPhaseModes.filter((mode) => mode !== "P0:not_applicable"), commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "at_parent", cas_status: "not_attempted" }, state: "EXISTING_CAS_READY", action: "cas_update_existing_ref", reason: "GIT_EXISTING_REF_RELATION_VALID" });
add({ id: "G005I", priority: 6, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { phase_mode: "P0:not_applicable", commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "absent_initial", cas_status: "applied" }, state: "COMMIT_REPARSE_READY", action: "reparse_exact_commit_then_progress", reason: "GIT_INITIAL_CAS_APPLIED_REPARSE_REQUIRED", nextContext: "campaign_progression" });
add({ id: "G005E", priority: 7, context: "repository_validation", sourceSchema: "git_commit_validation_v2", when: { phase_mode: allPhaseModes.filter((mode) => mode !== "P0:not_applicable"), commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "at_parent", cas_status: "applied" }, state: "COMMIT_REPARSE_READY", action: "reparse_exact_commit_then_progress", reason: "GIT_EXISTING_CAS_APPLIED_REPARSE_REQUIRED", nextContext: "campaign_progression" });

const schemaRules = Object.fromEntries(Object.keys(sourceSchemas).map((schemaId) => [schemaId, rules.filter((rule) => rule.source_schema === schemaId).sort((a, b) => a.priority - b.priority)]));

function validateSource(schemaId, source) {
  const schema = sourceSchemas[schemaId];
  if (!schema) return { ok: false, reason: "SCHEMA_UNKNOWN" };
  if (canonical(Object.keys(source).sort()) !== canonical(schema.permitted)) return { ok: false, reason: "SCHEMA_KEYS_MISMATCH" };
  for (const [field, value] of Object.entries(schema.fixed)) {
    if (!conditionMatches(source[field], value)) return { ok: false, reason: `SCHEMA_FIXED_MISMATCH:${field}` };
  }
  for (const [field, domain] of Object.entries(schema.domains)) {
    if (!domain.some((value) => canonical(value) === canonical(source[field]))) return { ok: false, reason: `SCHEMA_DOMAIN_MISMATCH:${field}` };
  }
  if (schemaId === "locked_entry_ineligible_v3" && source.budget_relation === "exhausted_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps)
      || source.recovery_slots_consumed !== source.approval_maximum_recovery_bootstraps
      || source.recovery_budget !== "exhausted") {
      return { ok: false, reason: "SCHEMA_BUDGET_EXHAUSTION_RELATION_INVALID" };
    }
  }
  if (schemaId === "locked_recovery_eligible_v3" && source.budget_relation === "available_exact") {
    const budget = source.recovery_budget_state;
    if (!budget || !Number.isInteger(budget.maximum) || !Number.isInteger(budget.consumed)
      || budget.maximum < 1 || budget.maximum > 32 || budget.consumed < 0
      || budget.consumed >= budget.maximum || budget.status !== "available"
      || budget.next_ordinal !== `A${budget.consumed + 1}`
      || source.recovery_budget !== "available") {
      return { ok: false, reason: "SCHEMA_BUDGET_AVAILABILITY_RELATION_INVALID" };
    }
  }
  if (schemaId === "locked_dangling_admission_v2") {
    const relationValid = source.admission_ordinal === "invalid"
      || (source.admission_kind === "normal" && source.admission_ordinal === "A0")
      || (source.admission_kind === "recovery" && recoveryOrdinals.includes(source.admission_ordinal));
    if (!relationValid) return { ok: false, reason: "SCHEMA_DANGLING_ADMISSION_ORDINAL_INVALID" };
  }
  if (schemaId === "attempt_admission_v2") {
    const relationValid = source.admission_ordinal === "invalid"
      || (source.run_mode === "normal" && source.admission_kind === "normal" && source.admission_ordinal === "A0")
      || (source.run_mode === "recovery" && source.admission_kind === "recovery" && recoveryOrdinals.includes(source.admission_ordinal));
    if (!relationValid) return { ok: false, reason: "SCHEMA_ATTEMPT_ADMISSION_ORDINAL_INVALID" };
  }
  if (schemaId === "meter_finalization_v3") {
    const identity = source.attempt_identity;
    const relationValid = identity && ((identity.run_mode === "normal" && identity.admission_kind === "normal" && identity.ordinal === "A0")
      || (identity.run_mode === "recovery" && identity.admission_kind === "recovery" && recoveryOrdinals.includes(identity.ordinal)));
    if (!relationValid) return { ok: false, reason: "SCHEMA_METER_ATTEMPT_RELATION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v3") {
    const map = source.private_map_identity;
    const mapRelationValid = source.phase_mode === "E0:evaluate"
      ? map?.state === "MAP_OPENED_RECEIPT_DURABLE" && map.binding === "valid_current" && map.relation === "valid"
      : map?.state === "not_applicable" && map.binding === "not_applicable" && map.relation === "valid";
    if (!mapRelationValid) return { ok: false, reason: "SCHEMA_RECOVERY_PRIVATE_MAP_RELATION_INVALID" };
  }
  const ordinalSchemas = new Set([
    "live_candidate_action_v3", "live_e0_evaluate_action_v3",
    "live_transition_candidate_v3", "live_transition_e0_evaluate_v3",
    "campaign_progression_v3", "e0_private_map_v3", "git_commit_validation_v2",
  ]);
  if (ordinalSchemas.has(schemaId)) {
    const relationValid = (source.run_mode === "normal" && source.attempt_ordinal === "A0")
      || (source.run_mode === "recovery" && recoveryOrdinals.includes(source.attempt_ordinal));
    if (!relationValid) return { ok: false, reason: "SCHEMA_RUN_ATTEMPT_ORDINAL_INVALID" };
  }
  if (["live_candidate_action_v3", "live_e0_evaluate_action_v3"].includes(schemaId)) {
    const resultRelationValid = source.state === "REAPED"
      ? [true, false].includes(source.result_disposition)
      : source.result_disposition === "not_applicable";
    if (!resultRelationValid) return { ok: false, reason: "SCHEMA_LIVE_RESULT_DISPOSITION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v3") {
    const resultRelationValid = source.state === "REAPED"
      ? [true, false].includes(source.recoverable_result)
      : source.recoverable_result === "not_applicable";
    if (!resultRelationValid) return { ok: false, reason: "SCHEMA_RECOVERY_RESULT_DISPOSITION_INVALID" };
  }
  return { ok: true, reason: "SCHEMA_VALID" };
}

function completeSource(rule) {
  const schema = sourceSchemas[rule.source_schema];
  const source = { ...schema.fixed };
  for (const [field, values] of Object.entries(schema.domains)) source[field] = clone(values[0]);
  for (const [field, expected] of Object.entries(rule.compiled_predicate)) source[field] = clone(Array.isArray(expected) ? expected[0] : expected);
  const validated = validateSource(rule.source_schema, source);
  if (!validated.ok) throw new Error(`${rule.id}: generated source invalid: ${validated.reason}`);
  return source;
}

function selectRule(schemaId, source) {
  const validation = validateSource(schemaId, source);
  if (!validation.ok) {
    return { selected_rule: "SCHEMA_REJECT", reason: validation.reason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" };
  }
  const matches = schemaRules[schemaId].filter((rule) => predicateMatches(source, rule.compiled_predicate));
  if (matches.length > 1) throw new Error(`${schemaId}: overlapping rules ${matches.map((rule) => rule.id).join(",")}`);
  const selected = matches[0];
  return selected || { selected_rule: "DEFAULT", reason: "STATE_PRODUCT_UNMATCHED", state: "INFRASTRUCTURE_REQUESTED", next_action: "request_infrastructure_failure", next_context: "meter_finalization" };
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

function sha1(value) {
  const bytes = typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value);
  return createHash("sha1").update(bytes).digest("hex");
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
  const parentPhase = predecessorPhase(phase);
  return {
    schema: "tt-supervised-git-intent-v2",
    phase,
    attempt_ordinal: attemptOrdinal(source),
    tree_oid: sha1(`tree:${phase}:public-artifacts`),
    parent_oid: parentPhase === null ? null : sha1(`commit:${parentPhase}:expected-parent`),
    intended_ref: "refs/autolab/supervised-campaign",
    message: `record supervised phase ${phase}`,
    self_exclusion: "commit_oid_forbidden",
  };
}

function gitCommitBytes(intent) {
  const parent = intent.parent_oid === null ? "" : `parent ${intent.parent_oid}\n`;
  return `tree ${intent.tree_oid}\n${parent}author AutoLab <autolab@example.invalid> 0 +0000\ncommitter AutoLab <autolab@example.invalid> 0 +0000\n\n${intent.message}\n`;
}

function resourceMeasurementPayload(input = resourceFixture) {
  const validation = validateResourceInput(input);
  if (!validation.ok) throw new Error(validation.reason);
  const result = computeResources(input);
  return {
    schema: "tt-supervised-resource-measurement-v2",
    input: clone(input),
    input_sha256: sha256(input),
    result,
    result_sha256: sha256(result),
    policy: input.overlap_policy,
  };
}

function durableRecord(path, recordType, payload, producer = "fixture_seed") {
  const body = { schema: "tt-supervised-durable-record-v2", path, record_type: recordType, payload, producer };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

function validateUniverse(records) {
  const paths = new Set();
  const logicalKeys = new Set();
  for (const record of records) {
    if (paths.has(record.path)) throw new Error(`duplicate durable path ${record.path}`);
    paths.add(record.path);
    const { canonical_bytes: canonicalBytes, sha256: digest, ...body } = record;
    if (canonical(body) !== canonicalBytes) throw new Error(`noncanonical durable bytes ${record.path}`);
    if (sha256(canonicalBytes) !== digest) throw new Error(`durable digest mismatch ${record.path}`);
    if (record.schema !== "tt-supervised-durable-record-v2") throw new Error(`durable schema mismatch ${record.path}`);
    const phaseMatch = record.path.match(/\/phases\/(P[0-5]|E0)\//);
    if (phaseMatch && record.payload.phase !== phaseMatch[1]) throw new Error(`phase path-payload mismatch ${record.path}`);
    const attemptMatch = record.path.match(/\/attempts\/(A(?:0|[1-9][0-9]*))\//);
    if (attemptMatch && (record.payload.ordinal ?? record.payload.attempt_ordinal) !== attemptMatch[1]) throw new Error(`attempt path-payload mismatch ${record.path}`);
    const admissionMatch = record.path.match(/\/admissions\/(A(?:0|[1-9][0-9]*))\.json$/);
    if (admissionMatch && record.payload.ordinal !== admissionMatch[1]) throw new Error(`admission path-payload mismatch ${record.path}`);
    let logicalId = record.path;
    if (["normal_admission", "recovery_admission", "attempt_start", "attempt_end", "resource_receipt", "launch_identity", "kernel_process_observation"].includes(record.record_type)) logicalId = record.payload.ordinal || record.payload.attempt_ordinal;
    if (["candidate_phase_reservation", "evaluator_phase_reservation", "launch_intent", "phase_spawn", "phase_reap", "phase_result", "phase_content", "phase_terminal", "commit_intent", "commit_object", "ref_observation", "ref_cas_attempt", "committed_phase", "private_map_open_intent", "private_map_opened_receipt", "root_crash_observation"].includes(record.record_type)) logicalId = record.payload.phase;
    if (["campaign_terminal", "capability_receipt", "resource_measurement"].includes(record.record_type)) logicalId = "singleton";
    const logicalKey = `${record.record_type}:${logicalId}`;
    if (logicalKeys.has(logicalKey)) throw new Error(`duplicate logical record ${logicalKey}`);
    logicalKeys.add(logicalKey);
  }

  const admissions = new Map();
  for (const record of records.filter((row) => ["normal_admission", "recovery_admission"].includes(row.record_type))) {
    const ordinal = record.payload.ordinal;
    if (!/^A(?:0|[1-9][0-9]*)$/.test(ordinal)) throw new Error(`invalid admission ordinal ${record.path}`);
    if (record.record_type === "normal_admission" && ordinal !== "A0") throw new Error(`normal admission must be A0: ${record.path}`);
    if (record.record_type === "recovery_admission" && ordinal === "A0") throw new Error(`recovery admission cannot be A0: ${record.path}`);
    if (admissions.has(ordinal)) throw new Error(`duplicate admission ordinal ${ordinal}`);
    admissions.set(ordinal, record);
  }
  const starts = new Set();
  for (const record of records.filter((row) => row.record_type === "attempt_start")) {
    const ordinal = record.payload.ordinal;
    const admission = admissions.get(ordinal);
    if (!admission) throw new Error(`attempt-start without admission ${ordinal}`);
    if (record.payload.admission_ordinal !== ordinal || record.payload.admission_sha256 !== admission.sha256) throw new Error(`attempt-start admission link invalid ${ordinal}`);
    if (starts.has(ordinal)) throw new Error(`duplicate attempt-start ordinal ${ordinal}`);
    starts.add(ordinal);
  }
  for (const record of records.filter((row) => row.record_type === "campaign_terminal")) {
    const resource = records.find((row) => row.record_type === "resource_receipt" && row.sha256 === record.payload.resource_receipt_sha256);
    const end = records.find((row) => row.record_type === "attempt_end" && row.sha256 === record.payload.attempt_end_sha256);
    if (!resource || !end || resource.payload.ordinal !== end.payload.ordinal) throw new Error(`campaign terminal linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "launch_intent")) {
    const reservation = records.find((row) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(row.record_type) && row.sha256 === record.payload.reservation_sha256);
    const capability = records.find((row) => row.record_type === "capability_receipt" && row.sha256 === record.payload.capability_receipt_sha256);
    if (!reservation || reservation.payload.phase !== record.payload.phase) throw new Error(`launch reservation linkage invalid ${record.path}`);
    if (!capability) throw new Error(`launch capability linkage invalid ${record.path}`);
    if (!attemptOrdinals.includes(record.payload.attempt_ordinal)) throw new Error(`launch attempt ordinal invalid ${record.path}`);
    if (record.payload.phase_mode === "E0:evaluate") {
      const receipt = records.find((row) => row.record_type === "private_map_opened_receipt" && row.sha256 === record.payload.private_map_receipt_sha256);
      if (!receipt) throw new Error(`E0 launch private-map linkage invalid ${record.path}`);
    }
  }
  for (const record of records.filter((row) => row.record_type === "phase_spawn")) {
    const intent = records.find((row) => row.record_type === "launch_intent" && row.sha256 === record.payload.launch_intent_sha256);
    if (!intent || intent.payload.phase !== record.payload.phase || !["pid_returned", "spawn_error"].includes(record.payload.outcome)) throw new Error(`phase spawn linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "phase_reap")) {
    const spawn = records.find((row) => row.record_type === "phase_spawn" && row.sha256 === record.payload.phase_spawn_sha256);
    if (!spawn || spawn.payload.phase !== record.payload.phase || record.payload.outcome !== "exited") throw new Error(`phase reap linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "phase_result")) {
    const reap = records.find((row) => row.record_type === "phase_reap" && row.sha256 === record.payload.phase_reap_sha256);
    if (!reap || reap.payload.phase !== record.payload.phase || record.payload.bounded !== true || typeof record.payload.recovery !== "boolean") throw new Error(`phase result linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "phase_content")) {
    const result = records.find((row) => row.record_type === "phase_result" && row.sha256 === record.payload.phase_result_sha256);
    if (!result || result.payload.phase !== record.payload.phase || !/^[0-9a-f]{64}$/.test(record.payload.content_sha256 || "")) throw new Error(`phase content linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "phase_terminal")) {
    const predecessorDigest = record.payload.predecessor_sha256 || record.payload.open_intent_sha256;
    const predecessor = records.find((row) => row.sha256 === predecessorDigest && row.payload.phase === record.payload.phase);
    if (!predecessor || !["candidate_phase_reservation", "evaluator_phase_reservation", "private_map_open_intent", "phase_spawn", "phase_reap", "phase_content"].includes(predecessor.record_type)) throw new Error(`phase terminal linkage invalid ${record.path}`);
    if (!["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"].includes(record.payload.outcome)) throw new Error(`phase terminal outcome invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "private_map_open_intent")) {
    const reservation = records.find((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256);
    if (!reservation) throw new Error(`private-map intent reservation linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "private_map_opened_receipt")) {
    const reservation = records.find((row) => row.record_type === "evaluator_phase_reservation" && row.sha256 === record.payload.reservation_sha256);
    const intent = records.find((row) => row.record_type === "private_map_open_intent" && row.sha256 === record.payload.open_intent_sha256);
    if (!reservation || !intent) throw new Error(`private-map receipt linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "kernel_process_observation")) {
    const identity = records.find((row) => row.record_type === "launch_identity" && row.sha256 === record.payload.launch_identity_sha256);
    if (!identity || identity.payload.attempt_ordinal !== record.payload.attempt_ordinal) throw new Error(`kernel observation identity linkage invalid ${record.path}`);
  }
  for (const measurement of records.filter((row) => row.record_type === "resource_measurement")) {
    const validation = validateResourceInput(measurement.payload.input);
    if (!validation.ok || measurement.payload.input_sha256 !== sha256(measurement.payload.input)) throw new Error(`resource measurement input invalid ${measurement.path}`);
    const result = computeResources(measurement.payload.input);
    if (measurement.payload.schema !== "tt-supervised-resource-measurement-v2" || !same(measurement.payload.result, result) || measurement.payload.result_sha256 !== sha256(result) || measurement.payload.policy !== measurement.payload.input.overlap_policy) throw new Error(`resource measurement result invalid ${measurement.path}`);
  }
  for (const receipt of records.filter((row) => row.record_type === "resource_receipt")) {
    const measurement = records.find((row) => row.record_type === "resource_measurement" && row.sha256 === receipt.payload.measurement_sha256);
    if (!measurement || receipt.payload.input_sha256 !== measurement.payload.input_sha256 || receipt.payload.result_sha256 !== measurement.payload.result_sha256 || !same(receipt.payload.result, measurement.payload.result)) throw new Error(`resource receipt measurement linkage invalid ${receipt.path}`);
  }
  for (const object of records.filter((row) => row.record_type === "commit_object")) {
    const intent = records.find((row) => row.record_type === "commit_intent" && row.sha256 === object.payload.intent_sha256);
    if (!intent || Object.hasOwn(intent.payload, "forbidden_commit_oid")) throw new Error(`commit object intent linkage invalid ${object.path}`);
    const expectedBytes = gitCommitBytes(intent.payload);
    if (object.payload.commit_bytes !== expectedBytes || object.payload.oid !== gitObjectOid("commit", expectedBytes) || object.payload.tree_oid !== intent.payload.tree_oid || object.payload.parent_oid !== intent.payload.parent_oid) throw new Error(`commit object bytes invalid ${object.path}`);
  }
  for (const cas of records.filter((row) => row.record_type === "ref_cas_attempt")) {
    const object = records.find((row) => row.record_type === "commit_object" && row.sha256 === cas.payload.commit_object_sha256);
    const observation = records.find((row) => row.record_type === "ref_observation" && row.sha256 === cas.payload.ref_observation_sha256);
    if (!object || !observation || cas.payload.new_oid !== object.payload.oid || cas.payload.expected_old_oid !== observation.payload.observed_oid) throw new Error(`CAS linkage invalid ${cas.path}`);
  }
  for (const committed of records.filter((row) => row.record_type === "committed_phase")) {
    const object = records.find((row) => row.record_type === "commit_object" && row.sha256 === committed.payload.commit_object_sha256);
    const cas = records.find((row) => row.record_type === "ref_cas_attempt" && row.sha256 === committed.payload.ref_cas_sha256);
    if (!object || !cas || cas.payload.outcome !== "applied" || committed.payload.commit_oid !== object.payload.oid) throw new Error(`committed phase linkage invalid ${committed.path}`);
  }
}

function deriveCounterSnapshot(records) {
  validateUniverse(records);
  const evidence = {};
  for (const [counter, types] of Object.entries(counterTypes)) {
    evidence[counter] = records.filter((record) => types.includes(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }));
  }
  const values = Object.fromEntries(Object.entries(evidence).map(([counter, rows]) => [counter, rows.length]));
  const countableTypes = new Set(Object.values(counterTypes).flat());
  const noncounterRecords = records.filter((record) => !countableTypes.has(record.record_type)).map((record) => ({ path: record.path, sha256: record.sha256, record_type: record.record_type }));
  const covered = new Set([...Object.values(evidence).flat(), ...noncounterRecords].map((row) => `${row.path}:${row.sha256}`));
  if (covered.size !== records.length) throw new Error("durable universe coverage mismatch");
  return {
    schema: "tt-supervised-counter-snapshot-v3", values, counter_evidence: evidence,
    noncounter_records: noncounterRecords, complete_universe_sha256: sha256(records),
    counter_evidence_sha256: sha256(evidence), universe_record_count: records.length,
  };
}

function phaseId(source) {
  if (source.evaluation_context === "e0_private_map" || source.e0_mode) return "E0";
  if (typeof source.phase_mode === "string") return source.phase_mode.split(":")[0];
  if (typeof source.target_phase === "string" && phaseOrder.includes(source.target_phase)) return source.target_phase;
  throw new Error(`phase identity absent from ${source.variant || source.evaluation_context}`);
}

function attemptOrdinal(source) {
  if (source.attempt_identity && attemptOrdinals.includes(source.attempt_identity.ordinal)) return source.attempt_identity.ordinal;
  if (attemptOrdinals.includes(source.attempt_ordinal)) return source.attempt_ordinal;
  if (attemptOrdinals.includes(source.admission_ordinal)) return source.admission_ordinal;
  if (source.recovery_budget_state && recoveryOrdinals.includes(source.recovery_budget_state.next_ordinal)) return source.recovery_budget_state.next_ordinal;
  if (source.run_mode === "normal" || source.admission_kind === "normal") return "A0";
  throw new Error(`attempt ordinal absent from ${source.variant || source.evaluation_context}`);
}

function sourceRunMode(source) {
  if (source.run_mode) return source.run_mode;
  if (source.attempt_identity?.run_mode) return source.attempt_identity.run_mode;
  const ordinal = source.attempt_ordinal || source.admission_ordinal || source.recovery_budget_state?.next_ordinal;
  if (!attemptOrdinals.includes(ordinal)) return null;
  return ordinal === "A0" ? "normal" : "recovery";
}

function sourcePrivateMapState(source) {
  return source.private_map_state || source.private_map_identity?.state;
}

function sourcePrivateMapBinding(source) {
  return source.private_map_binding || source.private_map_identity?.binding;
}

function actionPhaseId(action, source) {
  if (action === "reserve_P0_then_live_supervisor") return "P0";
  if (["reserve_E0_evaluate_then_private_map", "reserve_E0_close_prior_failure_then_live_supervisor"].includes(action)) return "E0";
  if (action === "reserve_successor_then_live_supervisor") {
    const index = candidatePhases.indexOf(source.last_committed_phase);
    if (index < 0 || index >= candidatePhases.length - 1) throw new Error(`successor unavailable after ${source.last_committed_phase}`);
    return candidatePhases[index + 1];
  }
  return phaseId(source);
}

function seedRecordUniverse(controlId, schemaId, source) {
  const records = [];
  const addRecord = (suffix, type, payload = {}) => {
    const record = durableRecord(`fixtures/${controlId}/${suffix}.json`, type, payload);
    records.push(record);
    return record;
  };
  const ensureRecord = (suffix, type, payload = {}) => {
    const path = `fixtures/${controlId}/${suffix}.json`;
    const existing = records.find((record) => record.path === path);
    if (existing) return existing;
    const record = durableRecord(path, type, payload);
    records.push(record);
    return record;
  };
  const ensureAdmission = (ordinal) => ensureRecord(`admissions/${ordinal}`, ordinal === "A0" ? "normal_admission" : "recovery_admission", { ordinal });
  const ensureStart = (ordinal) => {
    const admission = ensureAdmission(ordinal);
    return ensureRecord(`attempts/${ordinal}/start`, "attempt_start", { ordinal, admission_ordinal: ordinal, admission_sha256: admission.sha256 });
  };
  const ensureEnd = (ordinal, outcome = "recoverable_crash") => ensureRecord(`attempts/${ordinal}/end`, "attempt_end", { ordinal, outcome, terminal_request: "absent", durable_state: "valid" });
  const currentOrdinal = (() => {
    try { return attemptOrdinal(source); } catch { return null; }
  })();

  if (source.recovery_budget_state) {
    ensureStart("A0");
    ensureEnd("A0");
    for (let index = 1; index <= source.recovery_budget_state.consumed; index += 1) {
      ensureStart(`A${index}`);
      ensureEnd(`A${index}`);
    }
  }
  if (source.prior_attempt_closure === "valid_unclosed" || source.prior_attempt_record === "valid_unclosed") {
    ensureStart(currentOrdinal || "A0");
  }
  if (["valid_unstarted", "valid_current"].includes(source.admission_record)) {
    ensureAdmission(currentOrdinal || "A0");
  }
  if (source.normal_consumption === "valid" || source.normal_consumption_binding === "valid" || source.consumption_record === "valid") {
    ensureAdmission("A0");
  }
  if (sourceRunMode(source) === "recovery") {
    ensureStart("A0");
    ensureEnd("A0");
  }
  if (["durable", "valid_current"].includes(source.attempt_record) || source.linked_attempt_record === "durable") {
    ensureStart(currentOrdinal || "A0");
  }
  if (source.launch_identity_evidence === "complete") {
    const ordinal = currentOrdinal || "A0";
    const identity = ensureRecord(`attempts/${ordinal}/launch-identity`, "launch_identity", { attempt_ordinal: ordinal, process_token: `kernel-token-${ordinal}`, executable_sha256: "c".repeat(64) });
    if (source.kernel_observation_evidence === "complete") {
      ensureRecord(`attempts/${ordinal}/kernel-observation`, "kernel_process_observation", { attempt_ordinal: ordinal, launch_identity_sha256: identity.sha256, observation: source.process_absence });
    }
  }
  if (source.resource_measurement === "valid_current" || schemaId === "meter_finalization_v3") {
    ensureRecord("accounting/resource-measurement", "resource_measurement", resourceMeasurementPayload());
  }
  if (source.resource_receipt === "durable") {
    const measurement = records.find((record) => record.record_type === "resource_measurement");
    ensureRecord(`attempts/${currentOrdinal}/resource`, "resource_receipt", { ordinal: currentOrdinal, measurement_sha256: measurement.sha256, input_sha256: measurement.payload.input_sha256, result_sha256: measurement.payload.result_sha256, result: measurement.payload.result });
  }
  if (source.attempt_end === "durable") ensureRecord(`attempts/${currentOrdinal}/end`, "attempt_end", { ordinal: currentOrdinal, outcome: source.durable_state === "valid" ? "complete" : "infrastructure_failure", terminal_request: source.terminal_request || "absent", durable_state: source.durable_state || "valid" });
  if (source.capability_receipt === "valid_current") addRecord("capability/launch-barrier", "capability_receipt", { descriptor_schema: "candidate_boundary_descriptor_v3", binding: "valid_current" });
  const needsE0Reservation = source.evaluation_context === "e0_private_map" || sourcePrivateMapState(source) === "MAP_OPENED_RECEIPT_DURABLE";
  if (needsE0Reservation) ensureRecord("phases/E0/reservation", "evaluator_phase_reservation", { phase: "E0", binding: source.reservation_binding || sourcePrivateMapBinding(source) });
  const mapState = source.map_state || sourcePrivateMapState(source);
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(mapState)) {
    const reservation = records.find((record) => record.record_type === "evaluator_phase_reservation" && record.payload.phase === "E0");
    ensureRecord("phases/E0/private-map-intent", "private_map_open_intent", { phase: "E0", reservation_binding: "valid_current", reservation_sha256: reservation?.sha256 });
  }
  if (mapState === "MAP_OPENED_RECEIPT_DURABLE") {
    const reservation = records.find((record) => record.record_type === "evaluator_phase_reservation" && record.payload.phase === "E0");
    const intent = records.find((record) => record.record_type === "private_map_open_intent");
    ensureRecord("phases/E0/private-map-receipt", "private_map_opened_receipt", { phase: "E0", reservation_binding: "valid_current", reservation_sha256: reservation?.sha256, open_intent_sha256: intent?.sha256 });
  }
  if (mapState === "MAP_OPEN_FAILED_DURABLE") {
    const intent = records.find((record) => record.record_type === "private_map_open_intent");
    ensureRecord("phases/E0/terminal", "phase_terminal", { phase: "E0", outcome: "TERMINAL_HARNESS_FAILURE", predecessor_sha256: intent?.sha256, reason: "private_map_open_failed", syscall_error: { domain: "posix_errno", code: "EACCES" }, open_intent_sha256: intent?.sha256 });
  }

  const ensureValidGitChain = (phase, through) => {
    const prospectiveIntent = gitIntentPayload({ ...source, phase_mode: source.phase_mode || `${phase}:not_applicable` });
    const relation = phase === "P0" ? "absent_initial" : "at_parent";
    const observedOid = phase === "P0" ? null : prospectiveIntent.parent_oid;
    const refObservation = ensureRecord(`phases/${phase}/ref-observation`, "ref_observation", { phase, ref: prospectiveIntent.intended_ref, observed_oid: observedOid, relation });
    const intent = ensureRecord(`phases/${phase}/commit-intent`, "commit_intent", prospectiveIntent);
    if (through === "intent") return { refObservation, intent };
    const commitBytes = gitCommitBytes(intent.payload);
    const commitObject = ensureRecord(`phases/${phase}/commit-object`, "commit_object", { phase, commit_bytes: commitBytes, oid: gitObjectOid("commit", commitBytes), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid, intent_sha256: intent.sha256 });
    if (through === "object") return { refObservation, intent, commitObject };
    const cas = ensureRecord(`phases/${phase}/ref-cas`, "ref_cas_attempt", { phase, ref: intent.payload.intended_ref, expected_old_oid: observedOid, new_oid: commitObject.payload.oid, outcome: "applied", commit_object_sha256: commitObject.sha256, ref_observation_sha256: refObservation.sha256 });
    if (through === "cas") return { refObservation, intent, commitObject, cas };
    const committed = ensureRecord(`phases/${phase}/committed`, "committed_phase", { phase, commit_oid: commitObject.payload.oid, commit_object_sha256: commitObject.sha256, ref_cas_sha256: cas.sha256 });
    return { refObservation, intent, commitObject, cas, committed };
  };

  if (source.state && liveStates.includes(source.state) && source.state !== "UNSEEN") {
    const phase = phaseId(source);
    const reservationType = phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation";
    const reservation = ensureRecord(`phases/${phase}/reservation`, reservationType, { phase });
    const atOrAfter = (threshold) => liveStates.indexOf(source.state) >= liveStates.indexOf(threshold);
    let launchIntent = records.find((record) => record.record_type === "launch_intent" && record.payload.phase === phase);
    if (atOrAfter("LAUNCH_INTENT_DURABLE")) {
      const capability = records.find((record) => record.record_type === "capability_receipt");
      const mapReceipt = records.find((record) => record.record_type === "private_map_opened_receipt");
      launchIntent = ensureRecord(`phases/${phase}/launch-intent`, "launch_intent", { phase, phase_mode: source.phase_mode, attempt_ordinal: currentOrdinal, reservation_sha256: reservation.sha256, capability_receipt_sha256: capability?.sha256, private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? mapReceipt?.sha256 : null });
    }
    let spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === phase);
    if (source.state === "SPAWN_FAILED") spawn = ensureRecord(`phases/${phase}/spawn`, "phase_spawn", { phase, launch_intent_sha256: launchIntent?.sha256, outcome: "spawn_error" });
    if (["SPAWNED", "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) spawn = ensureRecord(`phases/${phase}/spawn`, "phase_spawn", { phase, launch_intent_sha256: launchIntent?.sha256, outcome: "pid_returned" });
    let reap = records.find((record) => record.record_type === "phase_reap" && record.payload.phase === phase);
    if (["REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) reap = ensureRecord(`phases/${phase}/reap`, "phase_reap", { phase, phase_spawn_sha256: spawn?.sha256, outcome: "exited" });
    let result = records.find((record) => record.record_type === "phase_result" && record.payload.phase === phase);
    if (["RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) result = ensureRecord(`phases/${phase}/result`, "phase_result", { phase, phase_reap_sha256: reap?.sha256, bounded: true, recovery: source.evaluation_context === "recovery_reconstruction" });
    let content = records.find((record) => record.record_type === "phase_content" && record.payload.phase === phase);
    if (["CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) content = ensureRecord(`phases/${phase}/content`, "phase_content", { phase, phase_result_sha256: result?.sha256, content_sha256: sha256(`content:${phase}`) });
    if (["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) {
      const outcome = ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"].includes(source.state) ? source.state : "TERMINAL_VALID_OUTCOME";
      const predecessor = content || reap || spawn || reservation;
      ensureRecord(`phases/${phase}/terminal`, "phase_terminal", { phase, outcome, predecessor_sha256: predecessor.sha256 });
    }
    if (atOrAfter("COMMIT_INTENT_DURABLE")) ensureValidGitChain(phase, source.state === "COMMIT_INTENT_DURABLE" ? "intent" : source.state === "COMMIT_OBJECT_EXACT" ? "object" : source.state === "REF_APPLIED" ? "cas" : "committed");
  }

  if (source.event && source.event_record_binding === "valid_current") {
    const phase = phaseId(source);
    const reservation = records.find((record) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(record.record_type) && record.payload.phase === phase)
      || ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    if (source.event === "reservation_durable") ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    if (source.event === "launch_intent_durable") {
      const capability = records.find((record) => record.record_type === "capability_receipt");
      const mapReceipt = records.find((record) => record.record_type === "private_map_opened_receipt");
      ensureRecord(`phases/${phase}/launch-intent`, "launch_intent", { phase, phase_mode: source.phase_mode, attempt_ordinal: currentOrdinal, reservation_sha256: reservation.sha256, capability_receipt_sha256: capability?.sha256, private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? mapReceipt?.sha256 : null });
    }
    const launchIntent = records.find((record) => record.record_type === "launch_intent" && record.payload.phase === phase);
    if (["spawn_returned_error", "spawn_returned_pid"].includes(source.event)) ensureRecord(`phases/${phase}/spawn`, "phase_spawn", { phase, launch_intent_sha256: launchIntent?.sha256, outcome: source.event === "spawn_returned_error" ? "spawn_error" : "pid_returned" });
    const spawn = records.find((record) => record.record_type === "phase_spawn" && record.payload.phase === phase);
    if (source.event === "child_reaped") ensureRecord(`phases/${phase}/reap`, "phase_reap", { phase, phase_spawn_sha256: spawn?.sha256, outcome: "exited" });
    const reap = records.find((record) => record.record_type === "phase_reap" && record.payload.phase === phase);
    if (source.event === "bounded_result_retained") ensureRecord(`phases/${phase}/result`, "phase_result", { phase, phase_reap_sha256: reap?.sha256, bounded: true, recovery: false });
    const result = records.find((record) => record.record_type === "phase_result" && record.payload.phase === phase);
    if (source.event === "content_durable") ensureRecord(`phases/${phase}/content`, "phase_content", { phase, phase_result_sha256: result?.sha256, content_sha256: sha256(`content:${phase}`) });
    if (["spawn_failure_terminal_durable", "runtime_failure_terminal_durable", "valid_terminal_durable", "validation_failure_terminal_durable"].includes(source.event)) {
      const outcome = source.event === "valid_terminal_durable" ? "TERMINAL_VALID_OUTCOME" : "TERMINAL_HARNESS_FAILURE";
      const content = records.find((record) => record.record_type === "phase_content" && record.payload.phase === phase);
      const predecessor = content || reap || spawn || reservation;
      ensureRecord(`phases/${phase}/terminal`, "phase_terminal", { phase, outcome, predecessor_sha256: predecessor.sha256 });
    }
    if (source.event === "commit_intent_durable") ensureValidGitChain(phase, "intent");
    if (source.event === "commit_object_exact") ensureValidGitChain(phase, "object");
    if (["initial_ref_cas_applied", "existing_ref_cas_applied"].includes(source.event)) ensureValidGitChain(phase, "cas");
    if (source.event === "commit_reparsed_exact") ensureValidGitChain(phase, "committed");
    if (source.event === "root_crashed") ensureRecord(`phases/${phase}/root-crash-observation`, "root_crash_observation", { phase, attempt_ordinal: currentOrdinal, observation: "root_crashed" });
  }

  if (schemaId === "git_commit_validation_v2") {
    const phase = phaseId(source);
    ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    const prospectiveIntent = gitIntentPayload(source);
    const observedOid = source.ref_relation === "absent_initial" ? null : source.ref_relation === "at_parent" ? prospectiveIntent.parent_oid : source.ref_relation === "other" ? sha1(`other-ref:${phase}`) : "invalid";
    const refObservation = ensureRecord(`phases/${phase}/ref-observation`, "ref_observation", { phase, ref: prospectiveIntent.intended_ref, observed_oid: observedOid, relation: source.ref_relation });
    let intent = null;
    if (source.commit_intent_relation !== "absent") {
      const intentPayload = source.commit_intent_relation === "valid_self_excluding"
        ? prospectiveIntent
        : source.commit_intent_relation === "invalid_self_including"
          ? { ...prospectiveIntent, forbidden_commit_oid: gitObjectOid("commit", gitCommitBytes(prospectiveIntent)) }
          : { schema: "invalid-git-intent", phase, attempt_ordinal: currentOrdinal };
      intent = ensureRecord(`phases/${phase}/commit-intent`, "commit_intent", intentPayload);
    }
    let commitObject = null;
    if (source.commit_object_state !== "absent") {
      const baseIntent = intent?.payload || prospectiveIntent;
      const commitBytes = gitCommitBytes(prospectiveIntent);
      const exactOid = gitObjectOid("commit", commitBytes);
      commitObject = ensureRecord(`phases/${phase}/commit-object`, "commit_object", {
        phase, commit_bytes: commitBytes, oid: source.commit_object_state === "exact" ? exactOid : "0".repeat(40),
        tree_oid: baseIntent.tree_oid, parent_oid: baseIntent.parent_oid, intent_sha256: intent?.sha256,
      });
    }
    if (source.cas_status !== "not_attempted") {
      ensureRecord(`phases/${phase}/ref-cas`, "ref_cas_attempt", {
        phase, ref: prospectiveIntent.intended_ref, expected_old_oid: observedOid,
        new_oid: commitObject?.payload.oid, outcome: source.cas_status, commit_object_sha256: commitObject?.sha256,
        ref_observation_sha256: refObservation.sha256,
      });
    }
  }

  if (source.last_committed_phase && source.last_committed_phase !== "none") {
    const phase = source.last_committed_phase;
    ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    ensureValidGitChain(phase, "committed");
  }
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal)) {
    ensureStart("A0");
    const measurement = ensureRecord("accounting/resource-measurement", "resource_measurement", resourceMeasurementPayload());
    if (!records.some((record) => record.record_type === "resource_receipt")) ensureRecord("attempts/A0/resource", "resource_receipt", { ordinal: "A0", measurement_sha256: measurement.sha256, input_sha256: measurement.payload.input_sha256, result_sha256: measurement.payload.result_sha256, result: measurement.payload.result });
    if (!records.some((record) => record.record_type === "attempt_end")) ensureEnd("A0", "complete");
    const resource = records.find((record) => record.record_type === "resource_receipt");
    const end = records.find((record) => record.record_type === "attempt_end");
    addRecord("campaign-terminal", "campaign_terminal", { kind: source.campaign_terminal, resource_receipt_sha256: resource.sha256, attempt_end_sha256: end.sha256 });
  }
  return records.sort((a, b) => a.path.localeCompare(b.path));
}

function addExactRecord(records, record) {
  const existing = records.find((candidate) => candidate.path === record.path);
  if (existing) {
    if (existing.sha256 !== record.sha256) throw new Error(`occupied path conflict ${record.path}`);
    return false;
  }
  records.push(record);
  records.sort((a, b) => a.path.localeCompare(b.path));
  return true;
}

const actionRecordTypes = {
  reserve_normal_admission: "normal_admission",
  reserve_recovery_admission: "recovery_admission",
  write_linked_attempt_start: "attempt_start",
  reserve_P0_then_live_supervisor: "candidate_phase_reservation",
  reserve_successor_then_live_supervisor: "candidate_phase_reservation",
  reserve_E0_evaluate_then_private_map: "evaluator_phase_reservation",
  reserve_E0_close_prior_failure_then_live_supervisor: "evaluator_phase_reservation",
  create_launch_intent: "launch_intent",
  spawn_phase: "phase_spawn",
  reap_phase: "phase_reap",
  publish_harness_failure_phase_terminal: "phase_terminal",
  publish_quarantine_phase_terminal: "phase_terminal",
  reconcile_process_then_publish_quarantine_phase_terminal: "phase_terminal",
  retain_bounded_result: "phase_result",
  retain_recoverable_result: "phase_result",
  publish_runtime_failure_phase_terminal: "phase_terminal",
  publish_phase_content: "phase_content",
  publish_valid_or_harness_phase_terminal: "phase_terminal",
  create_commit_intent: "commit_intent",
  create_ledgered_commit_objects: "commit_object",
  cas_create_initial_ref: "ref_cas_attempt",
  cas_update_existing_ref: "ref_cas_attempt",
  reparse_exact_commit_then_progress: "committed_phase",
  write_resource_receipt_only: "resource_receipt",
  write_attempt_end_only: "attempt_end",
  publish_attested_terminal_only: "campaign_terminal",
  publish_infrastructure_terminal_only: "campaign_terminal",
  write_private_map_open_intent: "private_map_open_intent",
  write_private_map_opened_receipt: "private_map_opened_receipt",
  publish_map_open_harness_failure_terminal: "phase_terminal",
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

function executeAction(controlId, selection, source, records) {
  const output = clone(records).sort((left, right) => left.path.localeCompare(right.path));
  const type = actionRecordTypes[selection.next_action];
  const delta = [];
  if (type) {
    const path = actionRecordPath(controlId, selection.next_action, source);
    const ordinal = attemptOrdinal(source);
    const action = selection.next_action;
    const phase = ["normal_admission", "recovery_admission", "attempt_start", "resource_receipt", "attempt_end", "campaign_terminal"].includes(type) ? null : actionPhaseId(action, source);
    const admission = records.find((candidate) => ["normal_admission", "recovery_admission"].includes(candidate.record_type) && candidate.payload.ordinal === ordinal);
    const reservation = phase === null ? null : records.find((candidate) => ["candidate_phase_reservation", "evaluator_phase_reservation"].includes(candidate.record_type) && candidate.payload.phase === phase);
    const launchIntent = phase === null ? null : records.find((candidate) => candidate.record_type === "launch_intent" && candidate.payload.phase === phase);
    const spawn = phase === null ? null : records.find((candidate) => candidate.record_type === "phase_spawn" && candidate.payload.phase === phase);
    const reap = phase === null ? null : records.find((candidate) => candidate.record_type === "phase_reap" && candidate.payload.phase === phase);
    const phaseResult = phase === null ? null : records.find((candidate) => candidate.record_type === "phase_result" && candidate.payload.phase === phase);
    const phaseContent = phase === null ? null : records.find((candidate) => candidate.record_type === "phase_content" && candidate.payload.phase === phase);
    const resource = records.find((candidate) => candidate.record_type === "resource_receipt" && candidate.payload.ordinal === ordinal);
    const attemptEnd = records.find((candidate) => candidate.record_type === "attempt_end" && candidate.payload.ordinal === ordinal);
    const measurement = records.find((candidate) => candidate.record_type === "resource_measurement");
    const capabilityReceipt = records.find((candidate) => candidate.record_type === "capability_receipt");
    const privateMapReceipt = records.find((candidate) => candidate.record_type === "private_map_opened_receipt");
    const evaluatorReservation = records.find((candidate) => candidate.record_type === "evaluator_phase_reservation" && candidate.payload.phase === "E0");
    const privateMapIntent = records.find((candidate) => candidate.record_type === "private_map_open_intent");
    let payload;
    if (["normal_admission", "recovery_admission"].includes(type)) payload = { ordinal };
    if (type === "attempt_start") payload = { ordinal, admission_ordinal: ordinal, admission_sha256: admission?.sha256 };
    if (["candidate_phase_reservation", "evaluator_phase_reservation"].includes(type)) {
      const predecessor = records.find((candidate) => candidate.record_type === "committed_phase" && candidate.payload.phase === source.last_committed_phase);
      const phaseMode = phase === "E0" ? (action.includes("evaluate") ? "E0:evaluate" : "E0:close_prior_failure") : `${phase}:not_applicable`;
      payload = { phase, phase_mode: phaseMode, attempt_ordinal: ordinal, predecessor_committed_sha256: predecessor?.sha256 || null, binding: "valid_current" };
    }
    if (type === "launch_intent") payload = { phase, phase_mode: source.phase_mode, attempt_ordinal: ordinal, reservation_sha256: reservation?.sha256, capability_receipt_sha256: capabilityReceipt?.sha256, private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? privateMapReceipt?.sha256 : null };
    if (type === "phase_spawn") payload = { phase, launch_intent_sha256: launchIntent?.sha256, outcome: "pid_returned" };
    if (type === "phase_reap") payload = { phase, phase_spawn_sha256: spawn?.sha256, outcome: "exited" };
    if (type === "phase_result") payload = { phase, phase_reap_sha256: reap?.sha256, bounded: true, recovery: action === "retain_recoverable_result" };
    if (type === "phase_content") payload = { phase, phase_result_sha256: phaseResult?.sha256, content_sha256: sha256(`content:${phase}`) };
    if (type === "phase_terminal") {
      const predecessor = phaseContent || reap || spawn || reservation || privateMapIntent;
      payload = { phase, outcome: action.includes("quarantine") ? "TERMINAL_QUARANTINE" : action === "publish_valid_or_harness_phase_terminal" ? "TERMINAL_VALID_OUTCOME" : "TERMINAL_HARNESS_FAILURE", predecessor_sha256: predecessor?.sha256 };
      if (action === "publish_map_open_harness_failure_terminal") payload = { ...payload, outcome: "TERMINAL_HARNESS_FAILURE", reason: "private_map_open_failed", syscall_error: { domain: "posix_errno", code: "EACCES" }, open_intent_sha256: privateMapIntent?.sha256 };
    }
    if (type === "commit_intent") payload = gitIntentPayload(source);
    if (type === "commit_object") {
      const intent = records.find((candidate) => candidate.record_type === "commit_intent" && candidate.payload.phase === phase);
      const commitBytes = gitCommitBytes(intent.payload);
      payload = { phase, commit_bytes: commitBytes, oid: gitObjectOid("commit", commitBytes), tree_oid: intent.payload.tree_oid, parent_oid: intent.payload.parent_oid, intent_sha256: intent.sha256 };
    }
    if (type === "ref_cas_attempt") {
      const intent = records.find((candidate) => candidate.record_type === "commit_intent" && candidate.payload.phase === phase);
      const object = records.find((candidate) => candidate.record_type === "commit_object" && candidate.payload.phase === phase);
      const observation = records.find((candidate) => candidate.record_type === "ref_observation" && candidate.payload.phase === phase);
      payload = { phase, ref: intent.payload.intended_ref, expected_old_oid: observation.payload.observed_oid, new_oid: object.payload.oid, outcome: "applied", commit_object_sha256: object.sha256, ref_observation_sha256: observation.sha256 };
    }
    if (type === "committed_phase") {
      const object = records.find((candidate) => candidate.record_type === "commit_object" && candidate.payload.phase === phase);
      const cas = records.find((candidate) => candidate.record_type === "ref_cas_attempt" && candidate.payload.phase === phase);
      payload = { phase, commit_oid: object.payload.oid, commit_object_sha256: object.sha256, ref_cas_sha256: cas.sha256 };
    }
    if (type === "resource_receipt") payload = { ordinal, measurement_sha256: measurement?.sha256, input_sha256: measurement?.payload.input_sha256, result_sha256: measurement?.payload.result_sha256, result: measurement?.payload.result };
    if (type === "attempt_end") payload = { ordinal, outcome: source.durable_state === "valid" && source.terminal_request === "absent" ? "recoverable_crash" : source.durable_state === "valid" && source.terminal_request === "attested_closure" ? "attested_closure" : "infrastructure_failure", terminal_request: source.terminal_request, durable_state: source.durable_state, resource_receipt_sha256: resource?.sha256 };
    if (type === "campaign_terminal") payload = { kind: action === "publish_attested_terminal_only" ? "valid_attested_closure" : "valid_infrastructure_failure", resource_receipt_sha256: resource?.sha256, attempt_end_sha256: attemptEnd?.sha256, terminal_request: source.terminal_request };
    if (type === "private_map_open_intent") payload = { phase: "E0", reservation_sha256: evaluatorReservation?.sha256, reservation_binding: source.reservation_binding };
    if (type === "private_map_opened_receipt") payload = { phase: "E0", reservation_sha256: evaluatorReservation?.sha256, open_intent_sha256: privateMapIntent?.sha256, reservation_binding: source.reservation_binding };
    if (!payload) throw new Error(`payload reducer missing for ${action}`);
    const record = durableRecord(path, type, payload, action);
    if (addExactRecord(output, record)) delta.push(record);
  }
  const actionStatePatches = {
    reserve_normal_admission: { admission_record: "valid_current", admission_kind: "normal", admission_ordinal: "A0", normal_consumption: "valid" },
    reserve_recovery_admission: { admission_record: "valid_current", admission_kind: "recovery" },
    write_linked_attempt_start: { linked_attempt_record: "durable", attempt_record: "valid_current" },
    reserve_P0_then_live_supervisor: { target_phase: "P0", phase_mode: "P0:not_applicable", phase_state: "RESERVED" },
    reserve_successor_then_live_supervisor: { phase_state: "RESERVED" },
    reserve_E0_evaluate_then_private_map: { target_phase: "E0", phase_mode: "E0:evaluate", phase_state: "RESERVED" },
    reserve_E0_close_prior_failure_then_live_supervisor: { target_phase: "E0", phase_mode: "E0:close_prior_failure", phase_state: "RESERVED" },
    create_launch_intent: { phase_state: "LAUNCH_INTENT_DURABLE" },
    spawn_phase: { phase_state: "SPAWNED" },
    reap_phase: { phase_state: "REAPED" },
    retain_bounded_result: { phase_state: "RESULT_RETAINED" },
    retain_recoverable_result: { phase_state: "RESULT_RETAINED" },
    publish_phase_content: { phase_state: "CONTENT_PUBLISHED" },
    publish_valid_or_harness_phase_terminal: { phase_state: "TERMINAL_VALID_OUTCOME" },
    publish_harness_failure_phase_terminal: { phase_state: "TERMINAL_HARNESS_FAILURE" },
    publish_runtime_failure_phase_terminal: { phase_state: "TERMINAL_HARNESS_FAILURE" },
    publish_quarantine_phase_terminal: { phase_state: "TERMINAL_QUARANTINE" },
    create_commit_intent: { git_state: "COMMIT_INTENT_DURABLE" },
    create_ledgered_commit_objects: { git_state: "COMMIT_OBJECT_EXACT" },
    cas_create_initial_ref: { git_state: "REF_APPLIED" },
    cas_update_existing_ref: { git_state: "REF_APPLIED" },
    reparse_exact_commit_then_progress: { git_state: "COMMITTED" },
    write_resource_receipt_only: { resource_receipt: "durable" },
    write_attempt_end_only: { attempt_end: "durable" },
    publish_attested_terminal_only: { campaign_terminal: "valid_attested_closure" },
    publish_infrastructure_terminal_only: { campaign_terminal: "valid_infrastructure_failure" },
    perform_readonly_recalculation: { recalculation: "complete" },
    release_recoverable_lock: { lock_release: "released" },
    release_final_lock: { lock_release: "released" },
    write_private_map_open_intent: { map_state: "MAP_OPEN_INTENT_DURABLE" },
    open_private_map_trusted_descriptor: { map_state: "MAP_OPENED_UNRECEIPTED", descriptor_state: "trusted_meter_only" },
    write_private_map_opened_receipt: { map_state: "MAP_OPENED_RECEIPT_DURABLE" },
    publish_map_open_harness_failure_terminal: { map_state: "MAP_OPEN_FAILED_DURABLE", state: "TERMINAL_HARNESS_FAILURE" },
  };
  const statePatch = clone(actionStatePatches[selection.next_action] || {});
  if (selection.next_action === "reserve_recovery_admission") statePatch.admission_ordinal = attemptOrdinal(source);
  if (selection.next_action === "write_linked_attempt_start") statePatch.attempt_ordinal = attemptOrdinal(source);
  if (selection.next_action === "reserve_successor_then_live_supervisor") {
    statePatch.target_phase = actionPhaseId(selection.next_action, source);
    statePatch.phase_mode = `${statePatch.target_phase}:not_applicable`;
  }
  return {
    records: output,
    action_delta: delta,
    post_state: {
      evaluation_context: selection.next_context,
      state: selection.state,
      selected_rule: selection.id || selection.selected_rule,
      reason: selection.reason,
      last_action: selection.next_action,
      derived_field_patch: statePatch,
    },
  };
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

function applyFault(pre, fault) {
  const observed = clone(pre);
  if (fault.kind === "none") return { observed, mutations: [] };
  const mutations = [];
  if (fault.kind === "replace") {
    const before = clone(getPath(observed, fault.path));
    if (canonical(before) !== canonical(fault.before)) throw new Error(`${fault.id}: fault before mismatch at ${fault.path}`);
    setPath(observed, fault.path, clone(fault.after));
    mutations.push({ path: fault.path, before, after: clone(fault.after) });
  } else if (fault.kind === "add_source_property") {
    if (Object.hasOwn(observed.source, fault.property)) throw new Error(`${fault.id}: property already exists`);
    observed.source[fault.property] = clone(fault.value);
    mutations.push({ path: `source.${fault.property}`, before: "__absent__", after: clone(fault.value) });
  } else if (fault.kind === "remove_record") {
    const index = observed.records.findIndex((record) => record.path === fault.record_path);
    if (index < 0) throw new Error(`${fault.id}: record absent ${fault.record_path}`);
    const [removed] = observed.records.splice(index, 1);
    mutations.push({ path: `records:${fault.record_path}`, before: removed.sha256, after: "__absent__" });
  } else if (fault.kind === "replace_record") {
    const index = observed.records.findIndex((record) => record.path === fault.record_path);
    if (index < 0) throw new Error(`${fault.id}: record absent ${fault.record_path}`);
    const before = observed.records[index];
    if (before.sha256 !== fault.before_sha256) throw new Error(`${fault.id}: record digest before mismatch ${fault.record_path}`);
    if (fault.after_record.path !== fault.record_path || fault.after_record.sha256 === before.sha256) throw new Error(`${fault.id}: invalid replacement record ${fault.record_path}`);
    observed.records[index] = clone(fault.after_record);
    observed.records.sort((left, right) => left.path.localeCompare(right.path));
    mutations.push({ path: `records:${fault.record_path}`, before: before.sha256, after: fault.after_record.sha256 });
  } else {
    throw new Error(`${fault.id}: unknown fault kind ${fault.kind}`);
  }
  if (canonical(pre) === canonical(observed) || mutations.length === 0) throw new Error(`${fault.id}: non-none fault made no change`);
  return { observed, mutations };
}

function deriveGitEvidence(source, records) {
  const phase = phaseId(source);
  const intent = records.find((record) => record.record_type === "commit_intent" && record.payload.phase === phase);
  const expectedIntent = gitIntentPayload(source);
  let commitIntentRelation = "absent";
  if (intent) {
    if (Object.hasOwn(intent.payload, "forbidden_commit_oid")) commitIntentRelation = "invalid_self_including";
    else commitIntentRelation = same(intent.payload, expectedIntent) ? "valid_self_excluding" : "invalid";
  }
  const object = records.find((record) => record.record_type === "commit_object" && record.payload.phase === phase);
  let commitObjectState = "absent";
  if (object) {
    const expectedBytes = gitCommitBytes(expectedIntent);
    const exact = intent && commitIntentRelation === "valid_self_excluding"
      && object.payload.intent_sha256 === intent.sha256
      && object.payload.commit_bytes === expectedBytes
      && object.payload.oid === gitObjectOid("commit", expectedBytes)
      && object.payload.tree_oid === expectedIntent.tree_oid
      && object.payload.parent_oid === expectedIntent.parent_oid;
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
    const linked = object && observation
      && cas.payload.commit_object_sha256 === object.sha256
      && cas.payload.ref_observation_sha256 === observation.sha256
      && cas.payload.new_oid === object.payload.oid
      && cas.payload.expected_old_oid === observation.payload.observed_oid;
    casStatus = linked && ["applied", "conflict"].includes(cas.payload.outcome) ? cas.payload.outcome : "invalid";
  }
  return { commit_intent_relation: commitIntentRelation, commit_object_state: commitObjectState, ref_relation: refRelation, cas_status: casStatus };
}

function compileSourceEvidence(schemaId, source, records) {
  const compiled = clone(source);
  const mutations = [];
  if (schemaId === "git_commit_validation_v2") {
    const derived = deriveGitEvidence(source, records);
    for (const [field, value] of Object.entries(derived)) {
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
  if (source.event === "spawn_failure_terminal_durable") record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_HARNESS_FAILURE");
  if (source.event === "runtime_failure_terminal_durable") record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_HARNESS_FAILURE");
  if (source.event === "child_reaped") record = byType("phase_reap", (candidate) => candidate.payload.outcome === "exited");
  if (source.event === "bounded_result_retained") record = byType("phase_result", (candidate) => candidate.payload.bounded === true);
  if (source.event === "content_durable") record = byType("phase_content");
  if (source.event === "valid_terminal_durable") record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_VALID_OUTCOME");
  if (source.event === "validation_failure_terminal_durable") record = byType("phase_terminal", (candidate) => candidate.payload.outcome === "TERMINAL_HARNESS_FAILURE");
  if (source.event === "commit_intent_durable") record = byType("commit_intent", (candidate) => same(candidate.payload, gitIntentPayload(source)));
  if (source.event === "commit_object_exact") record = byType("commit_object");
  if (source.event === "initial_ref_cas_applied") record = byType("ref_cas_attempt", (candidate) => candidate.payload.outcome === "applied" && candidate.payload.expected_old_oid === null);
  if (source.event === "existing_ref_cas_applied") record = byType("ref_cas_attempt", (candidate) => candidate.payload.outcome === "applied" && candidate.payload.expected_old_oid !== null);
  if (source.event === "commit_reparsed_exact") record = byType("committed_phase");
  if (source.event === "root_crashed") record = byType("root_crash_observation", (candidate) => candidate.payload.attempt_ordinal === ordinal && candidate.payload.observation === "root_crashed");
  if (!record) return null;
  return { event: source.event, path: record.path, sha256: record.sha256, record_type: record.record_type };
}

function evidenceConsistency(source, records) {
  try { validateUniverse(records); } catch (error) { return `EVIDENCE_UNIVERSE_INVALID:${error.message}`; }
  const has = (type) => records.some((record) => record.record_type === type);
  const hasPhase = (type, phase = phaseId(source)) => records.some((record) => record.record_type === type && record.payload.phase === phase);
  const ordinal = (() => { try { return attemptOrdinal(source); } catch { return null; } })();
  const currentAdmissionType = source.admission_kind === "recovery" || source.attempt_identity?.admission_kind === "recovery" || source.run_mode === "recovery" ? "recovery_admission" : "normal_admission";
  if (["valid_current", "valid_unstarted"].includes(source.admission_record) && !records.some((record) => record.record_type === currentAdmissionType && record.payload.ordinal === ordinal)) return "EVIDENCE_ADMISSION_MISSING";
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
  if ((source.map_state === "MAP_OPENED_RECEIPT_DURABLE" || sourcePrivateMapState(source) === "MAP_OPENED_RECEIPT_DURABLE") && !has("private_map_opened_receipt")) return "EVIDENCE_PRIVATE_MAP_RECEIPT_MISSING";
  if (source.evaluation_context === "e0_private_map" && !hasPhase("evaluator_phase_reservation", "E0")) return "EVIDENCE_E0_RESERVATION_MISSING";
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(source.map_state || sourcePrivateMapState(source)) && !has("private_map_open_intent")) return "EVIDENCE_PRIVATE_MAP_INTENT_MISSING";
  if ((source.map_state || sourcePrivateMapState(source)) === "MAP_OPEN_FAILED_DURABLE" && !hasPhase("phase_terminal", "E0")) return "EVIDENCE_PRIVATE_MAP_FAILURE_TERMINAL_MISSING";
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal) && !has("campaign_terminal")) return "EVIDENCE_CAMPAIGN_TERMINAL_MISSING";
  if (source.event_record_binding === "valid_current") {
    const receipt = exactEventReceipt(source, records);
    if (!receipt || !(eventRecordTypes[source.event] || []).includes(receipt.record_type)) return "EVIDENCE_EVENT_RECORD_MISSING_OR_INVALID";
  }
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

function makeTransitionControl(spec) {
  const preRecords = spec.records ? clone(spec.records) : seedRecordUniverse(spec.id, spec.source_schema, spec.source);
  const pre = { source: clone(spec.source), records: preRecords };
  const { observed, mutations } = applyFault(pre, { id: spec.id, ...(spec.fault || { kind: "none" }) });
  const sourceCompilation = compileSourceEvidence(spec.source_schema, observed.source, observed.records);
  const selectionSource = sourceCompilation.compiled;
  const consistencyReason = evidenceConsistency(selectionSource, observed.records);
  const selection = consistencyReason
    ? { selected_rule: "EVIDENCE_REJECT", reason: consistencyReason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" }
    : selectRule(spec.source_schema, selectionSource);
  const executableSelection = {
    ...selection,
    id: selection.id || selection.selected_rule,
    next_action: selection.next_action,
    next_context: selection.next_context,
  };
  const executed = spec.execute_action === false
    ? { records: clone(observed.records).sort((left, right) => left.path.localeCompare(right.path)), action_delta: [], post_state: { evaluation_context: executableSelection.next_context, state: executableSelection.state, selected_rule: executableSelection.id, reason: executableSelection.reason, last_action: "selection_only", derived_field_patch: {} } }
    : executeAction(spec.id, executableSelection, selectionSource, observed.records);
  const expectedPostUniverse = [...observed.records, ...executed.action_delta].sort((left, right) => left.path.localeCompare(right.path));
  if (!same(expectedPostUniverse, executed.records)) throw new Error(`${spec.id}: post-universe is not exact append-only union`);
  const fixture = {
    schema: "tt-supervised-transition-witness-v2", source_schema: spec.source_schema,
    pre_state: pre.source, pre_record_universe: pre.records,
    fault: spec.fault || { kind: "none" }, fault_mutations: mutations,
    observed_state_after_fault: observed.source, observed_record_universe_after_fault: observed.records,
    compiled_state_for_selection: selectionSource, source_derivation_mutations: sourceCompilation.mutations,
    observed_event_receipt: exactEventReceipt(selectionSource, observed.records),
    selected_rule: executableSelection.id, selected_reason: executableSelection.reason,
    selected_action: executableSelection.next_action, action_executed: spec.execute_action !== false,
    action_record_delta: executed.action_delta, post_state: executed.post_state,
    post_record_universe: executed.records,
    source_counters: deriveCounterSnapshot(pre.records),
    observed_counters_after_fault: deriveCounterSnapshot(observed.records),
    post_action_counters: deriveCounterSnapshot(executed.records),
  };
  if (spec.assert) {
    for (const [field, expected] of Object.entries(spec.assert)) {
      const actual = getPath({ fixture }, `fixture.${field}`);
      if (!subsetMatches(actual, expected)) throw new Error(`${spec.id}: assertion ${field}: ${canonical(actual)} does not contain ${canonical(expected)}`);
    }
  }
  return {
    id: spec.id, category: spec.category || "v8_transition_witness", claim: spec.claim,
    target_kind: spec.target_kind || "matrix", fixture,
    fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_witness_engine",
  };
}

function makeRuleControl(rule) {
  const source = completeSource(rule);
  return makeTransitionControl({
    id: `SEC8-RULE-${rule.id}`, category: "complete_rule_guard_selection",
    claim: `${rule.id} selects from a complete ${rule.source_schema} source`,
    source_schema: rule.source_schema, source, fault: { kind: "none" }, execute_action: false,
    assert: { selected_rule: rule.id, selected_reason: rule.reason, selected_action: rule.next_action },
  });
}

const ruleControls = rules.map(makeRuleControl);

function sourceFor(ruleId, edits = {}) {
  const rule = rules.find((candidate) => candidate.id === ruleId);
  if (!rule) throw new Error(`unknown rule ${ruleId}`);
  return { source_schema: rule.source_schema, source: { ...completeSource(rule), ...edits } };
}

const targetedSpecs = [];
function target(id, claim, ruleId, options = {}) {
  const base = sourceFor(ruleId, options.edits || {});
  targetedSpecs.push({ id, claim, ...base, ...options, assert: options.assert || { selected_rule: ruleId } });
}

target("SEC8-ADMISSION-A0", "normal admission is durable before the linked A0 start", "E012", { assert: { selected_rule: "E012", selected_action: "reserve_normal_admission", post_action_counters: { values: { root_admissions: 1, root_attempt_starts: 0 } } } });
target("SEC8-ADMISSION-A2", "the second recovery slot remains A2 through admission publication", "E013", { edits: { recovery_budget_state: { maximum: 32, consumed: 1, next_ordinal: "A2", status: "available" } }, assert: { selected_rule: "E013", selected_action: "reserve_recovery_admission", post_state: { derived_field_patch: { admission_ordinal: "A2" } }, post_action_counters: { values: { root_admissions: 3, root_attempt_starts: 2, recovery_slots: 2 } } } });
target("SEC8-START-A0", "A0 start links the exact A0 admission digest", "D001", { assert: { selected_rule: "D001", selected_action: "write_linked_attempt_start", post_action_counters: { values: { root_admissions: 1, root_attempt_starts: 1 } } } });
target("SEC8-START-A2", "A2 start links the exact A2 admission digest", "D002", { edits: { admission_ordinal: "A2" }, assert: { selected_rule: "D002", selected_action: "write_linked_attempt_start", post_state: { derived_field_patch: { attempt_ordinal: "A2" } } } });
target("SEC8-STALE-START", "a stale A0 start cannot dispatch an A2 recovery", "D004", { edits: { admission_ordinal: "A2" }, records: (() => { const a0 = durableRecord("fixtures/SEC8-STALE-START/admissions/A0.json", "normal_admission", { ordinal: "A0" }); const a2 = durableRecord("fixtures/SEC8-STALE-START/admissions/A2.json", "recovery_admission", { ordinal: "A2" }); return [a0, durableRecord("fixtures/SEC8-STALE-START/attempts/A0/start.json", "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: a0.sha256 }), a2]; })(), assert: { selected_rule: "EVIDENCE_REJECT", selected_reason: "EVIDENCE_ATTEMPT_START_ORDINAL_MISSING" } });
target("SEC8-ENTRY-001", "normal entry rejects an invalid recovery-slot field", "E012", { fault: { kind: "replace", path: "source.recovery_slot", before: "not_applicable", after: "invalid" }, assert: { selected_rule: "DEFAULT" } });
target("SEC8-PRECEDENCE-001", "prior-attempt selection hands off only to process safety", "E005", { execute_action: false, assert: { selected_rule: "E005", post_state: { evaluation_context: "prior_attempt_safety" } } });
target("SEC8-PRECEDENCE-002", "unproved process absence retains the lock", "S003", { assert: { selected_rule: "S003", selected_action: "retain_lock_and_stop_no_terminal" } });
target("SEC8-PRECEDENCE-003", "removing the exact kernel observation blocks safety completion", "S001", { fault: { kind: "remove_record", record_path: "fixtures/SEC8-PRECEDENCE-003/attempts/A0/kernel-observation.json" }, assert: { selected_rule: "EVIDENCE_REJECT", selected_reason: "EVIDENCE_KERNEL_OBSERVATION_RECORD_MISSING" } });
target("SEC8-E0-EVENT", "E0 launch-intent durability is backed by a literal launch-intent", "TE-L002", { assert: { selected_rule: "TE-L002" } });
target("SEC8-E0-OPEN-001", "private-map syscall failure writes bounded errno evidence and enters repository validation", "P003", { assert: { selected_rule: "P003", selected_action: "publish_map_open_harness_failure_terminal", post_state: { evaluation_context: "repository_validation" }, post_action_counters: { values: { phase_spawns: 0 } } } });
target("SEC8-E0-OPEN-002", "a restarted durable map failure hands off without spawning or writing Git outside repository validation", "P006", { assert: { selected_rule: "P006", selected_action: "handoff_repository_validation", post_state: { evaluation_context: "repository_validation" }, post_action_counters: { values: { commit_intents: 0, phase_spawns: 0 } } } });
target("SEC8-METER-001", "meter writes one receipt bound to canonical measured input and result", "M002", { assert: { selected_rule: "M002", selected_action: "write_resource_receipt_only" } });
target("SEC8-METER-002", "meter resumes from the bound receipt by writing only attempt-end", "M003", { assert: { selected_rule: "M003", selected_action: "write_attempt_end_only", post_action_counters: { values: { meter_finalizations: 1 } } } });
target("SEC8-METER-003", "meter resumes from attempt-end by publishing only attested terminal", "M005", { assert: { selected_rule: "M005", selected_action: "publish_attested_terminal_only" } });
target("SEC8-METER-004", "meter resumes after terminal with read-only recalculation", "M008", { assert: { selected_rule: "M008", selected_action: "perform_readonly_recalculation" } });
target("SEC8-RESULT-TRUE", "recovery retains a valid reaped result", "R005T", { assert: { selected_rule: "R005T", selected_action: "retain_recoverable_result" } });
target("SEC8-RESULT-FALSE", "recovery closes a non-retainable result with quarantine", "R005F", { assert: { selected_rule: "R005F", selected_action: "publish_quarantine_phase_terminal" } });
target("SEC8-STATE-TERMINAL", "removing a phase terminal blocks repository handoff", "AN008", { fault: { kind: "remove_record", record_path: "fixtures/SEC8-STATE-TERMINAL/phases/P0/terminal.json" }, assert: { selected_rule: "EVIDENCE_REJECT", selected_reason: "EVIDENCE_PHASE_TERMINAL_MISSING" } });
target("SEC8-COUNTER-SPAWN", "spawn increments from one linked literal record", "AN002", { assert: { selected_rule: "AN002", selected_action: "spawn_phase", post_action_counters: { values: { phase_spawns: 1 } } } });
target("SEC8-COUNTER-REAP", "reap increments from one linked literal record", "AN004", { assert: { selected_rule: "AN004", selected_action: "reap_phase", post_action_counters: { values: { phase_spawns: 1, phase_reaps: 1 } } } });
target("SEC8-COUNTER-P0", "P0 reservation carries phase P0 in path and payload", "C001", { assert: { selected_rule: "C001", selected_action: "reserve_P0_then_live_supervisor", post_action_counters: { values: { candidate_phase_reservations: 1 } } } });
target("SEC8-COUNTER-E0", "E0 reservation carries phase E0 in path and payload", "C003", { assert: { selected_rule: "C003", selected_action: "reserve_E0_evaluate_then_private_map", post_action_counters: { values: { evaluator_phase_reservations: 1 } } } });
target("SEC8-GIT-INTENT", "repository validation alone writes a self-excluding intent", "G000", { assert: { selected_rule: "G000", selected_action: "create_commit_intent", post_action_counters: { values: { commit_intents: 1 } } } });
target("SEC8-GIT-OBJECT", "commit bytes and OID are derived from the literal intent", "G001", { assert: { selected_rule: "G001", selected_action: "create_ledgered_commit_objects", post_action_counters: { values: { commit_objects: 1 } } } });
target("SEC8-GIT-CAS-I", "initial CAS is derived from an absent initial ref", "G003", { assert: { selected_rule: "G003", selected_action: "cas_create_initial_ref", post_action_counters: { values: { ref_cas_attempts: 1 } } } });
target("SEC8-GIT-CAS-E", "existing CAS is derived from the exact parent ref", "G004", { assert: { selected_rule: "G004", selected_action: "cas_update_existing_ref", post_action_counters: { values: { ref_cas_attempts: 1 } } } });
target("SEC8-GIT-COMMITTED", "applied CAS reparses into one linked committed-phase record", "G005I", { assert: { selected_rule: "G005I", selected_action: "reparse_exact_commit_then_progress", post_action_counters: { values: { committed_phases: 1 } } } });
target("SEC8-TERMINAL-001", "adding a lower field materially invalidates the closed terminal source", "E002", { fault: { kind: "add_source_property", property: "repository_identity", value: "invalid" }, assert: { selected_rule: "SCHEMA_REJECT", selected_reason: "SCHEMA_KEYS_MISMATCH" } });

const gitSelfCycleControlId = "SEC8-GIT-SELF-CYCLE";
const gitSelfCycleBase = sourceFor("G001");
const gitSelfCycleRecords = seedRecordUniverse(gitSelfCycleControlId, gitSelfCycleBase.source_schema, gitSelfCycleBase.source);
const gitSelfCycleIntent = gitSelfCycleRecords.find((record) => record.record_type === "commit_intent");
const gitSelfCycleReplacement = durableRecord(
  gitSelfCycleIntent.path,
  "commit_intent",
  { ...gitSelfCycleIntent.payload, forbidden_commit_oid: gitObjectOid("commit", gitCommitBytes(gitSelfCycleIntent.payload)) },
  "fault_injection",
);
target(gitSelfCycleControlId, "injecting a commit OID into literal intent bytes derives the self-cycle rejection", "G001", {
  records: gitSelfCycleRecords,
  fault: { kind: "replace_record", record_path: gitSelfCycleIntent.path, before_sha256: gitSelfCycleIntent.sha256, after_record: gitSelfCycleReplacement },
  assert: { selected_rule: "G002", selected_action: "request_infrastructure_failure", compiled_state_for_selection: { commit_intent_relation: "invalid_self_including" } },
});

function budgetControl(maximum) {
  const normalAdmission = durableRecord(`fixtures/SEC8-BUDGET-${maximum}/admissions/A0.json`, "normal_admission", { ordinal: "A0" });
  const records = [normalAdmission];
  records.push(durableRecord(`fixtures/SEC8-BUDGET-${maximum}/attempts/A0/start.json`, "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: normalAdmission.sha256 }));
  for (let index = 1; index <= maximum; index += 1) {
    const admission = durableRecord(`fixtures/SEC8-BUDGET-${maximum}/admissions/A${index}.json`, "recovery_admission", { ordinal: `A${index}` });
    records.push(admission);
    records.push(durableRecord(`fixtures/SEC8-BUDGET-${maximum}/attempts/A${index}/start.json`, "attempt_start", { ordinal: `A${index}`, admission_ordinal: `A${index}`, admission_sha256: admission.sha256 }));
  }
  const source = completeSource(rules.find((rule) => rule.id === "E011"));
  source.approval_maximum_recovery_bootstraps = maximum;
  source.recovery_slots_consumed = maximum;
  return makeTransitionControl({
    id: `SEC8-BUDGET-${String(maximum).padStart(2, "0")}`, category: "attempt_budget_boundary",
    claim: `recovery maximum ${maximum} rejects after exactly ${1 + maximum} admissions and starts`,
    source_schema: "locked_entry_ineligible_v3", source, records, execute_action: false,
    assert: { selected_rule: "E011", source_counters: { values: { root_admissions: 1 + maximum, root_attempt_starts: 1 + maximum, recovery_slots: maximum } } },
  });
}

const targetedControls = targetedSpecs.map(makeTransitionControl);
const budgetControls = [0, 2, 32].map(budgetControl);

function appendMeterObservationBoundary(traceId, ordinal, records) {
  const pre = clone(records).sort((left, right) => left.path.localeCompare(right.path));
  const post = clone(pre);
  const identity = durableRecord(`fixtures/${traceId}/attempts/${ordinal}/launch-identity.json`, "launch_identity", {
    attempt_ordinal: ordinal,
    process_token: `kernel-token-${ordinal}`,
    executable_sha256: "c".repeat(64),
  }, "external_meter");
  const observation = durableRecord(`fixtures/${traceId}/attempts/${ordinal}/kernel-observation.json`, "kernel_process_observation", {
    attempt_ordinal: ordinal,
    launch_identity_sha256: identity.sha256,
    observation: "kernel_confirmed_absent",
  }, "external_meter");
  const measurement = durableRecord(`fixtures/${traceId}/accounting/resource-measurement.json`, "resource_measurement", resourceMeasurementPayload(), "external_meter");
  const delta = [identity, observation, measurement];
  for (const record of delta) addExactRecord(post, record);
  validateUniverse(post);
  if (!same([...pre, ...delta].sort((left, right) => left.path.localeCompare(right.path)), post)) throw new Error(`${traceId}: observation boundary is not exact append-only union`);
  return {
    schema: "tt-supervised-external-observation-boundary-v1",
    producer: "external_meter",
    ordinal,
    pre_record_universe: pre,
    observation_record_delta: delta,
    post_record_universe: post,
    pre_universe_sha256: sha256(pre),
    post_universe_sha256: sha256(post),
  };
}

function makeComposedTraceControl(id, claim, specs) {
  let records = null;
  const steps = [];
  const boundaries = [];
  for (let index = 0; index < specs.length; index += 1) {
    const spec = specs[index];
    if (spec.observation_boundary === "meter_A2") {
      if (records === null) throw new Error(`${id}: observation boundary cannot be first`);
      const boundary = appendMeterObservationBoundary(id, "A2", records);
      if (!same(boundary.pre_record_universe, records)) throw new Error(`${id}: observation boundary input drift`);
      boundaries.push({ before_step: index + 1, ...boundary });
      records = boundary.post_record_universe;
    }
    const base = sourceFor(spec.rule, spec.edits || {});
    const nested = makeTransitionControl({
      id: `${id}-STEP-${String(index + 1).padStart(2, "0")}`,
      category: "composed_trace_step",
      claim: `${id} step ${index + 1} selects ${spec.rule}`,
      ...base,
      ...(records === null ? {} : { records }),
      assert: { selected_rule: spec.rule, ...(spec.assert || {}) },
    });
    if (records !== null && !same(nested.fixture.pre_record_universe, records)) throw new Error(`${id}: step ${index + 1} reseeded its pre-universe`);
    steps.push({
      ordinal: index + 1,
      expected_rule: spec.rule,
      fixture_sha256: nested.fixture_sha256,
      fixture: nested.fixture,
    });
    records = nested.fixture.post_record_universe;
  }
  const chain = steps.map((step, index) => ({
    step: step.ordinal,
    pre_universe_sha256: sha256(step.fixture.pre_record_universe),
    post_universe_sha256: sha256(step.fixture.post_record_universe),
    predecessor_post_sha256: index === 0 ? null : sha256(steps[index - 1].fixture.post_record_universe),
    boundary_before_step: boundaries.find((boundary) => boundary.before_step === step.ordinal)?.post_universe_sha256 || null,
  }));
  for (const row of chain.slice(1)) {
    const expected = row.boundary_before_step || row.predecessor_post_sha256;
    if (row.pre_universe_sha256 !== expected) throw new Error(`${id}: literal post-universe chain broke before step ${row.step}`);
  }
  const fixture = {
    schema: "tt-supervised-composed-transition-trace-v1",
    no_reseeding_between_steps: true,
    steps,
    observation_boundaries: boundaries,
    chain,
    final_record_universe: records,
    final_universe_sha256: sha256(records),
  };
  return {
    id,
    category: "composed_transition_trace",
    claim,
    target_kind: "trace",
    fixture,
    fixture_sha256: sha256(fixture),
    oracle_origin: "derived_by_literal_post_universe_composition",
  };
}

const traceControls = [
  makeComposedTraceControl("SEC8-TRACE-E0-01", "C003 reserves literal E0 state that P001 consumes without reseeding", [
    { rule: "C003", assert: { selected_action: "reserve_E0_evaluate_then_private_map", post_state: { derived_field_patch: { target_phase: "E0", phase_mode: "E0:evaluate" } } } },
    { rule: "P001", assert: { selected_action: "write_private_map_open_intent" } },
  ]),
  makeComposedTraceControl("SEC8-TRACE-REC-A2", "A2 admission, start, dispatch, and meter receipt preserve the exact ordinal", [
    { rule: "E013", edits: { recovery_budget_state: { maximum: 32, consumed: 1, next_ordinal: "A2", status: "available" } }, assert: { selected_action: "reserve_recovery_admission" } },
    { rule: "D002", edits: { admission_ordinal: "A2" }, assert: { selected_action: "write_linked_attempt_start" } },
    { rule: "D004", edits: { admission_ordinal: "A2" }, assert: { selected_action: "dispatch_recovery_reconstruction" } },
    { rule: "M002", edits: { attempt_identity: { run_mode: "recovery", admission_kind: "recovery", ordinal: "A2" } }, observation_boundary: "meter_A2", assert: { selected_action: "write_resource_receipt_only" } },
  ]),
  makeComposedTraceControl("SEC8-TRACE-L002-CANDIDATE", "AN001 launch-intent bytes cause the exact TN-L002 event", [
    { rule: "AN001", assert: { selected_action: "create_launch_intent" } },
    { rule: "TN-L002", assert: { selected_action: "accept_declared_transition", observed_event_receipt: { event: "launch_intent_durable", record_type: "launch_intent" } } },
  ]),
  makeComposedTraceControl("SEC8-TRACE-L002-E0", "AE001 launch-intent bytes cause the exact TE-L002 event", [
    { rule: "AE001", assert: { selected_action: "create_launch_intent" } },
    { rule: "TE-L002", assert: { selected_action: "accept_declared_transition", observed_event_receipt: { event: "launch_intent_durable", record_type: "launch_intent" } } },
  ]),
];

const capabilityDescriptor = {
  schema: "candidate_boundary_descriptor_v3",
  executable_sha256: "a".repeat(64), executable_path: "candidate/bin/run",
  argv: ["candidate/bin/run", "--public-input", "candidate/public/input.json"],
  environment: { LANG: "C", PATH: "/usr/bin:/bin" }, cwd: "candidate/work",
  readable_roots: ["candidate/public", "candidate/work"], writable_roots: ["candidate/work"],
  inherited_descriptors: [0, 1, 2], private_artifact_labels: "deny",
  path_resolution: "beneath_no_symlinks_no_magiclinks_no_xdev",
  mount_namespace: "private_unmounted_public_readonly",
  directory_handle_policy: "deny_unlisted_dirfds",
  syscall_profile: "candidate_no_network_no_process_control",
  resource_limits: { cpu_seconds: 300, address_space_bytes: 1073741824, open_files: 16, processes: 1, output_bytes: 67108864 },
  signal_policy: "self_and_supervisor_only",
  network: "deny", fork: "deny", exec: "deny_after_initial_image", ipc: "deny",
  debugger: "deny", task_port: "deny", ptrace: "deny",
  timeout_ms: 300000, kill_policy: "term_then_kill", reap_policy: "exact_identity_required",
  launch_barrier_receipt: "valid_current",
};

const capabilityChecks = {
  schema: (value) => value === "candidate_boundary_descriptor_v3",
  executable_sha256: (value) => value === capabilityDescriptor.executable_sha256,
  executable_path: (value) => value === "candidate/bin/run",
  argv: (value) => canonical(value) === canonical(capabilityDescriptor.argv),
  environment: (value) => canonical(value) === canonical(capabilityDescriptor.environment),
  cwd: (value) => value === "candidate/work",
  readable_roots: (value) => canonical(value) === canonical(capabilityDescriptor.readable_roots),
  writable_roots: (value) => canonical(value) === canonical(capabilityDescriptor.writable_roots),
  inherited_descriptors: (value) => canonical(value) === canonical([0, 1, 2]),
  private_artifact_labels: (value) => value === "deny",
  path_resolution: (value) => value === "beneath_no_symlinks_no_magiclinks_no_xdev",
  mount_namespace: (value) => value === "private_unmounted_public_readonly",
  directory_handle_policy: (value) => value === "deny_unlisted_dirfds",
  syscall_profile: (value) => value === "candidate_no_network_no_process_control",
  resource_limits: (value) => canonical(value) === canonical(capabilityDescriptor.resource_limits),
  signal_policy: (value) => value === "self_and_supervisor_only",
  network: (value) => value === "deny",
  fork: (value) => value === "deny",
  exec: (value) => value === "deny_after_initial_image",
  ipc: (value) => value === "deny",
  debugger: (value) => value === "deny",
  task_port: (value) => value === "deny",
  ptrace: (value) => value === "deny",
  timeout_ms: (value) => Number.isInteger(value) && value > 0 && value <= 300000,
  kill_policy: (value) => value === "term_then_kill",
  reap_policy: (value) => value === "exact_identity_required",
  launch_barrier_receipt: (value) => value === "valid_current",
};

function validateCapability(descriptor) {
  if (canonical(Object.keys(descriptor).sort()) !== canonical(Object.keys(capabilityDescriptor).sort())) return { valid: false, reason: "CAPABILITY_KEYS_MISMATCH" };
  for (const [field, check] of Object.entries(capabilityChecks)) if (!check(descriptor[field])) return { valid: false, reason: `CAPABILITY_${field.toUpperCase()}_INVALID` };
  return { valid: true, reason: "CAPABILITY_DESCRIPTOR_VALID" };
}

function capabilityControl(field, invalidValue) {
  const id = `SEC8-CAP-${field.replaceAll("_", "-").toUpperCase()}`;
  const pre = { descriptor: clone(capabilityDescriptor) };
  const fault = { id, kind: "replace", path: `descriptor.${field}`, before: clone(capabilityDescriptor[field]), after: clone(invalidValue) };
  const { observed, mutations } = applyFault(pre, fault);
  const result = validateCapability(observed.descriptor);
  const fixture = { schema: "tt-supervised-capability-witness-v1", pre_descriptor: pre.descriptor, fault, fault_mutations: mutations, observed_descriptor: observed.descriptor, derived_result: result };
  if (result.valid) throw new Error(`${id}: invalid descriptor accepted`);
  return { id, category: "candidate_capability_denial", claim: `${field} mutation is denied before launch`, target_kind: "capability", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_capability_validator" };
}

const capabilityMutations = {
  schema: "candidate_boundary_descriptor_untrusted",
  executable_sha256: "z".repeat(64), executable_path: "candidate/bin/other",
  argv: [...capabilityDescriptor.argv, "--private-map"], environment: { ...capabilityDescriptor.environment, PRIVATE_MAP: "/private/map" },
  cwd: "private", readable_roots: [...capabilityDescriptor.readable_roots, "private"], writable_roots: [...capabilityDescriptor.writable_roots, "campaign"],
  inherited_descriptors: [0, 1, 2, 9], private_artifact_labels: "allow", network: "allow",
  path_resolution: "follow_symlinks", mount_namespace: "host_shared",
  directory_handle_policy: "allow_any_dirfd", syscall_profile: "unrestricted",
  resource_limits: { ...capabilityDescriptor.resource_limits, processes: 64 }, signal_policy: "any_process",
  fork: "allow", exec: "allow", ipc: "allow", debugger: "allow", task_port: "allow", ptrace: "allow",
  timeout_ms: 0, kill_policy: "none", reap_policy: "pid_only", launch_barrier_receipt: "absent",
};
const capabilityControls = Object.entries(capabilityMutations).map(([field, value]) => capabilityControl(field, value));
{
  const result = validateCapability(capabilityDescriptor);
  if (!result.valid) throw new Error("valid capability descriptor rejected");
  const fixture = { schema: "tt-supervised-capability-witness-v1", pre_descriptor: capabilityDescriptor, fault: { kind: "none" }, fault_mutations: [], observed_descriptor: capabilityDescriptor, derived_result: result };
  capabilityControls.unshift({ id: "SEC8-CAP-VALID", category: "candidate_capability_positive", claim: "the exact closed candidate descriptor passes before launch", target_kind: "capability", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_capability_validator" });
}

function computeResources(input) {
  const validation = validateResourceInput(input);
  if (!validation.ok) throw new Error(validation.reason);
  const cpu = input.attempts.reduce((sum, attempt) => sum
    + (attempt.bootstrap_observed ?? attempt.bootstrap_cap)
    + (attempt.meter_observed_preterminal ?? attempt.meter_preterminal_cap)
    + attempt.meter_terminal_cap, 0);
  const wall = input.attempts.reduce((sum, attempt) => sum + attempt.wall_cap, 0);
  const io = input.attempts.reduce((sum, attempt) => sum + attempt.io_charge, 0);
  const disk = input.attempts.reduce((sum, attempt) => sum + attempt.disk_charge, 0);
  const vertices = input.memory_vertices;
  const adjacency = Object.fromEntries(vertices.map((vertex) => [vertex.id, new Set([vertex.id])]));
  for (const [left, right] of input.possible_overlap_edges) { adjacency[left].add(right); adjacency[right].add(left); }
  const seen = new Set();
  const componentCharges = [];
  for (const vertex of vertices) {
    if (seen.has(vertex.id)) continue;
    const stack = [vertex.id];
    let charge = 0;
    const members = [];
    while (stack.length) {
      const id = stack.pop();
      if (seen.has(id)) continue;
      seen.add(id); members.push(id);
      charge += vertices.find((candidate) => candidate.id === id).capacity;
      for (const neighbor of adjacency[id]) stack.push(neighbor);
    }
    componentCharges.push({ members: members.sort(), charge });
  }
  return { cpu, memory: Math.max(0, ...componentCharges.map((component) => component.charge)), wall, io, disk, memory_components: componentCharges };
}

function resourceControl(id, claim, fault = { kind: "none" }) {
  const exact = computeResources(resourceFixture);
  const pre = { resources: clone(resourceFixture), claimed_result: clone(exact) };
  const applied = applyFault(pre, { id, ...fault });
  const preResult = computeResources(pre.resources);
  const inputValidation = validateResourceInput(applied.observed.resources);
  const observedResult = inputValidation.ok ? computeResources(applied.observed.resources) : null;
  const claimValid = inputValidation.ok && canonical(applied.observed.claimed_result) === canonical(observedResult);
  const fixture = {
    schema: "tt-supervised-resource-arithmetic-witness-v2",
    pre_input: pre.resources, pre_claimed_result: pre.claimed_result,
    fault, fault_mutations: applied.mutations,
    observed_input: applied.observed.resources,
    observed_claimed_result: applied.observed.claimed_result,
    pre_result: preResult, input_validation: inputValidation, derived_result: observedResult,
    derived_validation: { valid: claimValid, reason: !inputValidation.ok ? inputValidation.reason : claimValid ? "RESOURCE_ARITHMETIC_EXACT" : "RESOURCE_ARITHMETIC_MISMATCH" },
  };
  return { id, category: "numeric_resource_arithmetic", claim, target_kind: "accounting", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_numeric_resource_evaluator" };
}

const resourceControls = [
  resourceControl("SEC8-RESOURCE-001", "CPU, memory, wall, I/O, and disk are numerically derived"),
  resourceControl("SEC8-RESOURCE-002", "a changed terminal CPU cap changes the derived total", { kind: "replace", path: "resources.attempts.1.meter_terminal_cap", before: 2, after: 9 }),
  resourceControl("SEC8-RESOURCE-003", "removing a possible-overlap edge changes memory from summed component to serial maximum", { kind: "replace", path: "resources.possible_overlap_edges", before: [["A0", "A1"], ["A1", "closure"]], after: [] }),
  resourceControl("SEC8-RESOURCE-004", "an off-by-one CPU claim is rejected", { kind: "replace", path: "claimed_result.cpu", before: 52, after: 51 }),
  resourceControl("SEC8-RESOURCE-005", "a serial-maximum memory claim is rejected when overlap is unproved", { kind: "replace", path: "claimed_result.memory", before: 73, after: 37 }),
  resourceControl("SEC8-RESOURCE-006", "a negative observation is rejected before arithmetic", { kind: "replace", path: "resources.attempts.0.bootstrap_observed", before: 13, after: -100 }),
  resourceControl("SEC8-RESOURCE-007", "an observation above its cap is rejected before arithmetic", { kind: "replace", path: "resources.attempts.0.bootstrap_observed", before: 13, after: 21 }),
  resourceControl("SEC8-RESOURCE-008", "duplicate memory vertex identifiers are rejected", { kind: "replace", path: "resources.memory_vertices.1.id", before: "A1", after: "A0" }),
  resourceControl("SEC8-RESOURCE-009", "unknown overlap endpoints are rejected", { kind: "replace", path: "resources.possible_overlap_edges.1.1", before: "closure", after: "unknown" }),
  resourceControl("SEC8-RESOURCE-010", "unsafe integer charges are rejected", { kind: "replace", path: "resources.attempts.1.wall_cap", before: 45, after: 9007199254740992 }),
];

function enumerateSchema(schemaId, callback) {
  const schema = sourceSchemas[schemaId];
  const fields = Object.keys(schema.domains);
  const source = { ...schema.fixed };
  function visit(index) {
    if (index === fields.length) { callback(clone(source)); return; }
    const field = fields[index];
    for (const value of schema.domains[field]) { source[field] = clone(value); visit(index + 1); }
  }
  visit(0);
}

if (process.env.V8_PRINT_SCHEMA_CARDINALITIES === "1") {
  process.stdout.write(`${JSON.stringify(Object.fromEntries(Object.entries(sourceSchemas).map(([schemaId, schema]) => [schemaId, schema.domain_cardinality])), null, 2)}\n`);
  process.exit(0);
}

const partitionCounts = new Map();
const symbolicSchemaManifests = [];
let symbolicCaseCount = 0;
for (const schemaId of Object.keys(sourceSchemas)) {
  let ordinal = 0;
  const digest = createHash("sha256");
  enumerateSchema(schemaId, (source) => {
    const selected = selectRule(schemaId, source);
    const ruleId = selected.id || selected.selected_rule;
    const key = `${schemaId}:${ruleId}`;
    partitionCounts.set(key, (partitionCounts.get(key) || 0) + 1);
    const row = { schema: schemaId, ordinal: ++ordinal, source_sha256: sha256(source), selected_rule: ruleId, next_action: selected.next_action };
    digest.update(`${canonical(row)}\n`);
  });
  symbolicCaseCount += ordinal;
  symbolicSchemaManifests.push({ source_schema: schemaId, case_count: ordinal, ordered_case_stream_sha256: digest.digest("hex") });
}
const symbolicPartitions = [...partitionCounts.entries()].map(([key, cardinality]) => {
  const split = key.lastIndexOf(":");
  return { source_schema: key.slice(0, split), partition: key.slice(split + 1), cardinality };
}).sort((a, b) => `${a.source_schema}:${a.partition}`.localeCompare(`${b.source_schema}:${b.partition}`));

const e0Manifest = [];
let e0Ordinal = 0;
for (const runMode of ["normal", "recovery"]) {
  for (const e0Mode of ["evaluate", "close_prior_failure"]) {
    for (const mapState of privateMapStates) {
      for (const event of privateMapEvents) {
        const attemptOrdinal = runMode === "normal" ? "A0" : "A1";
        const source = { ...sourceSchemas.e0_private_map_v3.fixed, run_mode: runMode, attempt_ordinal: attemptOrdinal, e0_mode: e0Mode, map_state: mapState, event, descriptor_state: mapState === "MAP_OPENED_UNRECEIPTED" || mapState === "MAP_OPENED_RECEIPT_DURABLE" ? "trusted_meter_only" : "absent" };
        const selected = selectRule("e0_private_map_v3", source);
        e0Manifest.push({ ordinal: ++e0Ordinal, run_mode: runMode, attempt_ordinal: attemptOrdinal, e0_mode: e0Mode, map_state: mapState, event, descriptor_state: source.descriptor_state, selected_rule: selected.id || selected.selected_rule, next_action: selected.next_action });
      }
    }
  }
}

const meterReachableStages = [
  { stage: "RESOURCE_ABSENT", rule: "M002", action: "write_resource_receipt_only" },
  { stage: "RESOURCE_DURABLE", rule: "M003", action: "write_attempt_end_only" },
  { stage: "ATTEMPT_END_DURABLE_RECOVERABLE", rule: "M004", action: "release_recoverable_lock" },
  { stage: "ATTEMPT_END_DURABLE_ATTESTED", rule: "M005", action: "publish_attested_terminal_only" },
  { stage: "ATTEMPT_END_DURABLE_INFRASTRUCTURE", rule: "M006", action: "publish_infrastructure_terminal_only" },
  { stage: "TERMINAL_PUBLISHED", rule: "M008", action: "perform_readonly_recalculation" },
  { stage: "RECALCULATED", rule: "M009", action: "release_final_lock" },
];

const allControls = [...ruleControls, ...targetedControls, ...traceControls, ...budgetControls, ...capabilityControls, ...resourceControls];
const controlsById = Object.fromEntries(allControls.map((control) => [control.id, control]));
const p0Fixture = controlsById["SEC8-COUNTER-P0"].fixture;
const p0ActionRecord = p0Fixture.action_record_delta[0];
const gitObjectFixture = controlsById["SEC8-GIT-OBJECT"].fixture;
const gitObjectIntent = gitObjectFixture.observed_record_universe_after_fault.find((record) => record.record_type === "commit_intent");
const committedFixture = controlsById["SEC8-GIT-COMMITTED"].fixture;
const committedActionRecord = committedFixture.action_record_delta[0];
const verifierMutationSuite = [
  {
    id: "SEC8-VERIFY-MUTATION-POST-STATE",
    target_control: "SEC8-COUNTER-P0",
    target_fixture_sha256: controlsById["SEC8-COUNTER-P0"].fixture_sha256,
    operation: { kind: "replace", path: "post_state.derived_field_patch.target_phase", before: "P0", after: "P1" },
    expected_rejection: "POST_STATE_MISMATCH",
  },
  {
    id: "SEC8-VERIFY-MUTATION-OCCUPIED-PATH",
    target_control: "SEC8-COUNTER-P0",
    target_fixture_sha256: controlsById["SEC8-COUNTER-P0"].fixture_sha256,
    operation: {
      kind: "append_record",
      path: "post_record_universe",
      record: durableRecord(p0ActionRecord.path, p0ActionRecord.record_type, { ...p0ActionRecord.payload, binding: "conflicting_overwrite" }, "verifier_mutation"),
    },
    expected_rejection: "DUPLICATE_DURABLE_PATH",
  },
  {
    id: "SEC8-VERIFY-MUTATION-DROP-PREREQUISITE",
    target_control: "SEC8-GIT-OBJECT",
    target_fixture_sha256: controlsById["SEC8-GIT-OBJECT"].fixture_sha256,
    operation: { kind: "remove_record", path: "observed_record_universe_after_fault", record_path: gitObjectIntent.path, before_sha256: gitObjectIntent.sha256 },
    expected_rejection: "FAULT_RECONSTRUCTION_MISMATCH",
  },
  {
    id: "SEC8-VERIFY-MUTATION-UNRELATED-REPLACEMENT",
    target_control: "SEC8-GIT-COMMITTED",
    target_fixture_sha256: controlsById["SEC8-GIT-COMMITTED"].fixture_sha256,
    operation: {
      kind: "replace_record",
      path: "post_record_universe",
      record_path: committedActionRecord.path,
      before_sha256: committedActionRecord.sha256,
      after_record: durableRecord(committedActionRecord.path, "committed_phase", { phase: "P0", commit_oid: "f".repeat(40), commit_object_sha256: "e".repeat(64), ref_cas_sha256: "d".repeat(64) }, "verifier_mutation"),
    },
    expected_rejection: "COMMITTED_PHASE_LINKAGE_INVALID",
  },
];
const priorBundle = join(dirname(here), "tt-supervised-executor-v7-rejected-snapshot");
const priorFiles = [
  "REJECTED.md", "SHA256SUMS", "build_v7_design_artifacts.mjs", "local-verification-v7.json",
  "supervised-executor-contract-v7.md", "supervised-executor-control-matrix-v6.json",
  "supervised-executor-red-team-draft-review-v7.md", "supervised-executor-theory-draft-review-v7.md",
  "supervised-executor-topology-decision-v6.md", "supervised-executor-transition-matrix-v6.json",
  "verify_v7_design_artifacts.mjs",
];
const preservedV7Manifest = Object.fromEntries(priorFiles.map((name) => [name, sha256(readFileSync(join(priorBundle, name)))]));
const repairObligations = ["V8-ORDINAL-01", "V8-ORDINAL-02", "V8-PHASE-01", "V8-TRACE-01", "V8-EVENT-01", "V8-RECOVERY-01", "V8-EVIDENCE-01", "V8-IDENTITY-01", "V8-POST-01", "V8-UNIQUE-01", "V8-GIT-01", "V8-GIT-02", "V8-CONTEXT-01", "V8-OVERLAP-01", "V8-CAPABILITY-01", "V8-RESOURCE-01", "V8-RESOURCE-02", "V8-PUBLISH-01"];

const transition = {
  schema: "tt-supervised-executor-transition-matrix-v7", protocol,
  status: ["HYPOTHESIS", "MODEL-BOUND", "UNTESTED", "ZERO-RUN"],
  artifact_freeze_authorized: false, code_implementation_authorized: false,
  control_execution_authorized: false, campaign_execution_authorized: false,
  contexts: ["entry_preflight", "attempt_admission", "prior_attempt_safety", "live_supervisor", "live_transition", "recovery_reconstruction", "campaign_progression", "repository_validation", "meter_finalization", "e0_private_map"],
  source_schemas: sourceSchemas,
  rules,
  rule_count: rules.length,
  entry_order: ["lock", "terminal", "prior_attempt", "dangling_admission", "invocation_eligibility", "admission_reservation", "attempt_start", "campaign_or_recovery_dispatch"],
  admission_protocol: {
    durable_order: ["bounded_admission_token", "linked_attempt_start", "repository_or_phase_action"],
    normal_token: "A0 normal admission doubles as one-time consumption",
    recovery_tokens: "R1 through Rk approval-bounded O_EXCL slots",
    crash_after_token_before_start: "resume same token and publish at most one linked start",
    maximum_admissions: "1 + approval.maximum_recovery_bootstraps",
    maximum_attempt_starts: "number of valid admission tokens",
    repository_action_before_start_forbidden: true,
  },
  prior_attempt_safety_policy: {
    precedence_reason_immutable: true,
    permitted_reads: ["exact_launch_identity_records", "kernel_process_identity_status"],
    forbidden_reads: ["repository_state", "phase_semantics", "candidate_results"],
    absence_unproved_action: "retain_lock_and_stop_no_terminal",
  },
  live_phase_protocol: { states: liveStates, events: liveEvents, edges: liveEdges, candidate_event_schema: "live_transition_candidate_v3", e0_event_schema: "live_transition_e0_evaluate_v3", e0_launch_requires_private_map_receipt: true },
  e0_private_map_protocol: { states: privateMapStates, events: privateMapEvents, event_projection_case_count: e0Manifest.length, event_projection_sha256: sha256(e0Manifest), closed_source_product_case_count: sourceSchemas.e0_private_map_v3.domain_cardinality, descriptor_state_is_separately_enumerated_in_symbolic_totality: true, closure_mode_all_events_forbidden: true, open_failure_outcome: "TERMINAL_HARNESS_FAILURE" },
  meter_finalization_protocol: { one_campaign_owned_record_per_write_action: true, terminal_last_campaign_owned_write: true, exact_process_identity_receipts_required: true, stages: meterReachableStages, crash_replay_from_every_stage: true },
  candidate_boundary_descriptor: capabilityDescriptor,
  accounting_policy: { formulas_executable: true, cpu: "sum observed else cap plus terminal cap", memory: "max connected possible-overlap component sum", wall: "sum attempt wall caps", io: "sum attempt charges", disk: "sum attempt charges" },
  totality: { symbolic_domain_cardinality: symbolicCaseCount, symbolic_partition_count: symbolicPartitions.length, symbolic_case_digest: sha256(symbolicSchemaManifests), schema_manifests: symbolicSchemaManifests, partitions: symbolicPartitions },
  repair_obligations: repairObligations,
  publication_policy: { one_in_memory_builder_snapshot: true, transition_bytes_serialized_once_before_write: true, moving_file_rereads_for_binding_forbidden: true },
  preserved_v7_negative_evidence: preservedV7Manifest,
};

const transitionArtifact = "supervised-executor-transition-matrix-v7.json";
const transitionBytes = Buffer.from(`${JSON.stringify(transition, null, 2)}\n`, "utf8");
const transitionSha256 = sha256(transitionBytes);
const builderSha256 = sha256(builderBytes);
writeFileSync(join(here, transitionArtifact), transitionBytes);

const control = {
  schema: "tt-supervised-executor-control-matrix-v7", protocol,
  status: ["HYPOTHESIS", "MODEL-BOUND", "UNTESTED", "ZERO-RUN"],
  artifact_freeze_authorized: false, code_implementation_authorized: false,
  control_execution_authorized: false, campaign_execution_authorized: false,
  source_transition_artifact: transitionArtifact,
  source_transition_artifact_sha256: transitionSha256,
  builder_artifact: "build_v8_design_artifacts.mjs", builder_artifact_sha256: builderSha256,
  publication_snapshot: { builder_sha256: builderSha256, transition_sha256: transitionSha256, transition_byte_length: transitionBytes.length, hashes_derived_from_in_memory_bytes: true },
  witness_policy: {
    trusted_inherited_oracles: false,
    pre_state_complete: true, explicit_fault_transform_required: true,
    non_none_fault_must_materially_change_state: true, action_applied_by_reducer: true,
    post_state_derived: true, complete_durable_record_universe_required: true,
    counters_derived_from_record_bytes: true, numeric_resource_evaluator_required: true,
    source_fields_derived_from_literal_records_where_applicable: true,
    event_receipt_must_name_exact_record_digest: true,
    composed_traces_forbid_reseeding: true,
  },
  controls: allControls,
  static_control_count: allControls.length,
  rule_selection_control_count: ruleControls.length,
  targeted_transition_control_count: targetedControls.length,
  composed_trace_control_count: traceControls.length,
  budget_boundary_control_count: budgetControls.length,
  capability_control_count: capabilityControls.length,
  resource_control_count: resourceControls.length,
  generated_suites: [
    { id: "SEC8-GENERATED-001", claim: "closed source products select one rule, schema rejection, or default", case_count: symbolicCaseCount, partition_count: symbolicPartitions.length, schema_manifests: symbolicSchemaManifests, manifest_sha256: sha256(symbolicSchemaManifests) },
    { id: "SEC8-GENERATED-002", claim: "complete E0 evaluate and closure event projection with canonical descriptor-state derivation; the full descriptor cross-product is in GENERATED-001", case_count: e0Manifest.length, closed_source_product_case_count: sourceSchemas.e0_private_map_v3.domain_cardinality, manifest: e0Manifest, manifest_sha256: sha256(e0Manifest) },
    { id: "SEC8-GENERATED-003", claim: "every reachable meter durable boundary has an idempotent selector", case_count: meterReachableStages.length, manifest: meterReachableStages, manifest_sha256: sha256(meterReachableStages) },
    { id: "SEC8-GENERATED-004", claim: "every denied capability field has a materialized negative transform", case_count: capabilityControls.length, manifest: capabilityControls.map((row) => ({ id: row.id, result: row.fixture.derived_result })), manifest_sha256: sha256(capabilityControls.map((row) => ({ id: row.id, result: row.fixture.derived_result }))) },
    { id: "SEC8-GENERATED-005", claim: "literal post-universe composition closes E0, A2 meter, candidate launch, and E0 launch traces", case_count: traceControls.length, manifest: traceControls.map((row) => ({ id: row.id, fixture_sha256: row.fixture_sha256, final_universe_sha256: row.fixture.final_universe_sha256 })), manifest_sha256: sha256(traceControls.map((row) => ({ id: row.id, fixture_sha256: row.fixture_sha256, final_universe_sha256: row.fixture.final_universe_sha256 }))) },
    { id: "SEC8-GENERATED-006", claim: "independent verification rejects post-state mutation, occupied overwrite, prerequisite deletion, and unrelated replacement", case_count: verifierMutationSuite.length, manifest: verifierMutationSuite, manifest_sha256: sha256(verifierMutationSuite) },
  ],
  verifier_mutation_suite: verifierMutationSuite,
  verifier_mutation_count: verifierMutationSuite.length,
  repair_obligations: repairObligations,
  preserved_v7_negative_evidence: preservedV7Manifest,
  self_audit: {
    control_ids_unique: new Set(allControls.map((row) => row.id)).size,
    fixture_hashes_unique: new Set(allControls.map((row) => row.fixture_sha256)).size,
    non_none_fault_count: allControls.filter((row) => row.fixture.fault?.kind && row.fixture.fault.kind !== "none").length,
    materialized_non_none_fault_count: allControls.filter((row) => row.fixture.fault?.kind && row.fixture.fault.kind !== "none" && row.fixture.fault_mutations?.length > 0).length,
  },
};

if (control.self_audit.control_ids_unique !== allControls.length) throw new Error("duplicate control IDs");
if (control.self_audit.fixture_hashes_unique !== allControls.length) throw new Error("duplicate fixture hashes");
if (control.self_audit.non_none_fault_count !== control.self_audit.materialized_non_none_fault_count) throw new Error("non-materialized fault");

const controlArtifact = "supervised-executor-control-matrix-v7.json";
const controlBytes = Buffer.from(`${JSON.stringify(control, null, 2)}\n`, "utf8");
writeFileSync(join(here, controlArtifact), controlBytes);
process.stdout.write(`${JSON.stringify({
  protocol,
  transition_artifact: transitionArtifact,
  transition_sha256: transitionSha256,
  control_artifact: controlArtifact,
  control_sha256: sha256(controlBytes),
  builder_sha256: builderSha256,
  symbolic_case_count: symbolicCaseCount,
  static_control_count: allControls.length,
  composed_trace_control_count: traceControls.length,
  verifier_mutation_count: verifierMutationSuite.length,
})}\n`);
