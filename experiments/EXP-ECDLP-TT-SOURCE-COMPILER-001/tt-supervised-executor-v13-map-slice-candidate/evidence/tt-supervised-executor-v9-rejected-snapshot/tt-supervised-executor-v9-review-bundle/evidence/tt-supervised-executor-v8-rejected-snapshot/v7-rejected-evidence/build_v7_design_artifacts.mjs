import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
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

function clone(value) {
  return structuredClone(value);
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
const privateMapEvents = [
  "request_open_intent", "open_syscall_success", "open_syscall_failure",
  "publish_opened_receipt", "dispatch_live_supervisor", "root_crashed",
  "private_map_open_syscall",
];

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
    variant: "attempt_admission_v1", evaluation_context: "attempt_admission",
    root_lock: "valid_current", campaign_terminal: "absent",
    prior_attempt_closure: "none_unclosed", admission_record: "valid_current",
    admission_binding: "valid_current", repository_action_count: 0, dispatcher_match: true,
  },
  prior_attempt_safety: {
    variant: "prior_attempt_safety_v1", evaluation_context: "prior_attempt_safety",
    root_lock: "valid_current", campaign_terminal: "absent",
    safety_scope: "process_identity_and_launch_records_only", dispatcher_match: true,
  },
  live_candidate: {
    variant: "live_candidate_action_v2", evaluation_context: "live_supervisor",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid",
    private_map_state: "not_applicable", private_map_binding: "not_applicable",
    capability_receipt: "valid_current", phase_private_map_relation: "valid",
    phase_capability_relation: "valid", dispatcher_match: true,
  },
  live_e0: {
    variant: "live_e0_evaluate_action_v2", evaluation_context: "live_supervisor",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid", phase_mode: "E0:evaluate",
    private_map_state: "MAP_OPENED_RECEIPT_DURABLE", private_map_binding: "valid_current",
    capability_receipt: "valid_current", phase_private_map_relation: "valid",
    phase_capability_relation: "valid", dispatcher_match: true,
  },
  recovery: {
    variant: "recovery_reconstruction_v2", evaluation_context: "recovery_reconstruction",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", admission_binding: "valid_current",
    prior_attempt_closure: "none_unclosed", consumption_record: "valid",
    private_selection_match: "match", repository_identity: "valid", phase_chain: "valid",
    capability_receipt: "valid_current", phase_capability_relation: "valid",
    dispatcher_match: true,
  },
  progression: {
    variant: "campaign_progression_v2", evaluation_context: "campaign_progression",
    root_lock: "valid_current", campaign_terminal: "absent", attempt_record: "valid_current",
    admission_record: "valid_current", prior_attempt_closure: "none_unclosed",
    consumption_record: "valid", private_selection_match: "match",
    repository_identity: "valid", phase_chain: "valid", active_phase: "none",
    dispatcher_match: true,
  },
  meter: {
    variant: "meter_finalization_v2", evaluation_context: "meter_finalization",
    root_lock: "valid_current", bootstrap_status: "reaped",
    admission_record: "valid_current", attempt_record: "valid_current",
    admission_binding: "valid_current", attempt_relation: "valid",
    dispatcher_match: true,
  },
  e0_map: {
    variant: "e0_private_map_v2", evaluation_context: "e0_private_map",
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
  locked_dangling_admission_v1: makeSchema({
    fixed: {
      variant: "locked_dangling_admission_v1", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
    },
    domains: {
      admission_record: ["valid_unstarted", "invalid", "conflict"],
      admission_kind: ["normal", "recovery", "invalid"],
      admission_ordinal: ["valid_current", "invalid"],
      admission_binding: ["valid_current", "invalid"],
    },
  }),
  locked_entry_ineligible_v2: makeSchema({
    fixed: {
      variant: "locked_entry_ineligible_v2", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent", admission_record: "absent",
    },
    domains: {
      run_mode: ["normal", "recovery"], normal_consumption: ["absent", "valid"],
      recovery_budget: ["not_applicable", "available", "exhausted"],
      approval_maximum_recovery_bootstraps: ["not_applicable", 0, 2, 32],
      recovery_slots_consumed: ["not_applicable", 0, 2, 32],
      budget_relation: ["not_applicable", "available_exact", "exhausted_exact", "invalid"],
    },
    notes: { repository_and_phase_fields_forbidden: true },
  }),
  locked_normal_eligible_v2: makeSchema({
    fixed: {
      variant: "locked_normal_eligible_v2", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
      admission_record: "absent", run_mode: "normal", normal_consumption: "absent",
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
  locked_recovery_eligible_v2: makeSchema({
    fixed: {
      variant: "locked_recovery_eligible_v2", evaluation_context: "entry_preflight",
      root_lock: "valid_current", campaign_terminal: "absent",
      prior_attempt_closure: "none_unclosed", attempt_record: "absent",
      admission_record: "absent", run_mode: "recovery", normal_consumption: "valid",
      private_selection_match: "match", recovery_budget: "available",
      budget_relation: "available_exact",
    },
    domains: {
      approval_maximum_recovery_bootstraps: [0, 2, 32],
      recovery_slots_consumed: [0, 1, 2, 31, 32],
      next_recovery_ordinal: [1, 2, 3, 32, "invalid"],
      recovery_slot: ["not_applicable", "valid_current", "invalid"],
      repository_identity: ["valid", "invalid", "conflict"],
      phase_chain: ["valid", "invalid", "conflict"],
      ref_relation: ["absent_initial", "at_last_commit", "other", "invalid"],
      initial_phase_state: ["empty", "recoverable_nonempty", "invalid"],
      entry_product_relation: ["valid_normal", "valid_recovery", "invalid"],
    },
  }),
  attempt_admission_v1: makeSchema({
    fixed: common.attempt_admission,
    domains: {
      run_mode: ["normal", "recovery"], admission_kind: ["normal", "recovery", "invalid"],
      admission_ordinal: ["valid_current", "invalid"], linked_attempt_record: ["absent", "durable", "invalid"],
      normal_consumption_binding: ["valid", "not_applicable", "invalid"],
      recovery_budget_binding: ["valid", "not_applicable", "invalid"],
    },
  }),
  prior_attempt_safety_v1: makeSchema({
    fixed: common.prior_attempt_safety,
    domains: {
      selected_precedence_reason: ["RESOURCE_PRIOR_ATTEMPT_OBSERVATION_INCOMPLETE", "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID"],
      precedence_binding: ["valid", "invalid"],
      prior_attempt_record: ["valid_unclosed", "invalid", "conflict"],
      launch_identity_evidence: ["complete", "absent", "invalid"],
      process_absence: ["kernel_confirmed_absent", "one_exact_identity_live", "ambiguous", "unkillable", "invalid"],
    },
    notes: { ordinary_repository_and_phase_fields_forbidden: true },
  }),
  live_candidate_action_v2: makeSchema({
    fixed: common.live_candidate,
    domains: {
      run_mode: ["normal", "recovery"], phase_mode: nonEvaluatePhaseModes,
      state: liveStates, launch_prerequisite: ["not_applicable", "satisfied", "invalid"],
    },
  }),
  live_e0_evaluate_action_v2: makeSchema({
    fixed: common.live_e0,
    domains: {
      run_mode: ["normal", "recovery"], state: liveStates,
      launch_prerequisite: ["not_applicable", "satisfied", "invalid"],
    },
  }),
  live_transition_candidate_v2: makeSchema({
    fixed: { ...common.live_candidate, variant: "live_transition_candidate_v2" },
    domains: { run_mode: ["normal", "recovery"], phase_mode: nonEvaluatePhaseModes, state: liveStates, event: liveEvents },
  }),
  live_transition_e0_evaluate_v2: makeSchema({
    fixed: { ...common.live_e0, variant: "live_transition_e0_evaluate_v2" },
    domains: { run_mode: ["normal", "recovery"], state: liveStates, event: liveEvents },
  }),
  recovery_reconstruction_v2: makeSchema({
    fixed: common.recovery,
    domains: {
      run_mode: ["recovery"], phase_mode: allPhaseModes, state: liveStates,
      private_map_state: ["not_applicable", "MAP_OPENED_RECEIPT_DURABLE", "invalid"],
      private_map_binding: ["not_applicable", "valid_current", "invalid"],
      phase_private_map_relation: ["valid", "invalid"],
      process_reconciliation: ["not_applicable", "kernel_confirmed_absent", "one_exact_identity_live", "multiple_token_matches", "pid_identity_mismatch", "unkillable", "invalid"],
      recoverable_result: ["not_applicable", true, false],
    },
  }),
  campaign_progression_v2: makeSchema({
    fixed: common.progression,
    domains: {
      run_mode: ["normal", "recovery"], trigger: ["normal_consumption", "phase_committed"],
      last_committed_phase: ["none", ...phaseOrder],
      last_phase_outcome: ["none", "valid_outcome", "harness_failure", "quarantine"],
      ref_relation: ["absent_initial", "at_last_commit", "other", "invalid"],
    },
  }),
  meter_finalization_v2: makeSchema({
    fixed: common.meter,
    domains: {
      run_mode: ["normal", "recovery"], admission_kind: ["normal", "recovery"],
      attempt_ordinal: ["A0", "A1"],
      process_absence: ["kernel_confirmed_absent", "one_exact_identity_live", "ambiguous", "unkillable"],
      durable_state: ["valid", "invalid"], terminal_request: ["absent", "attested_closure", "infrastructure_failure", "invalid", "conflict"],
      resource_receipt: ["absent", "durable", "invalid"], attempt_end: ["absent", "durable", "invalid"],
      campaign_terminal: ["absent", "valid_attested_closure", "valid_infrastructure_failure", "invalid"],
      recalculation: ["not_started", "complete", "invalid"], lock_release: ["held", "released", "invalid"],
    },
  }),
  e0_private_map_v2: makeSchema({
    fixed: common.e0_map,
    domains: {
      run_mode: ["normal", "recovery"], e0_mode: ["evaluate", "close_prior_failure"],
      map_state: privateMapStates, event: privateMapEvents,
      descriptor_state: ["absent", "trusted_meter_only", "closed", "invalid"],
    },
  }),
  git_commit_validation_v1: makeSchema({
    fixed: {
      variant: "git_commit_validation_v1", evaluation_context: "repository_validation",
      root_lock: "valid_current", campaign_terminal: "absent", repository_identity: "valid",
      phase_chain: "valid", dispatcher_match: true,
    },
    domains: {
      phase_mode: allPhaseModes,
      commit_intent_relation: ["valid_self_excluding", "invalid_self_including", "invalid"],
      commit_object_state: ["absent", "exact", "invalid"],
      ref_relation: ["absent_initial", "at_parent", "other", "invalid"],
      cas_status: ["not_attempted", "applied", "conflict"],
    },
  }),
};

function materializedRule({ id, priority, context, sourceSchema, when, state, action, reason, nextContext = context }) {
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
add({ id: "E007", priority: 8, context: "entry_preflight", sourceSchema: "locked_dangling_admission_v1", when: { admission_record: "valid_unstarted", admission_kind: ["normal", "recovery"], admission_ordinal: "valid_current", admission_binding: "valid_current" }, state: "ADMISSION_ATTEMPT_START_READY", action: "handoff_attempt_admission", reason: "ADMISSION_DURABLE_ATTEMPT_START_ABSENT", nextContext: "attempt_admission" });
add({ id: "E008", priority: 9, context: "entry_preflight", sourceSchema: "locked_dangling_admission_v1", when: { admission_record: ["invalid", "conflict"] }, state: "ADMISSION_INVALID", action: "request_infrastructure_failure_no_new_attempt", reason: "ADMISSION_RECORD_INVALID" });
add({ id: "E009", priority: 10, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v2", when: { run_mode: "normal", normal_consumption: "valid", recovery_budget: "not_applicable", approval_maximum_recovery_bootstraps: "not_applicable", recovery_slots_consumed: "not_applicable", budget_relation: "not_applicable" }, state: "NORMAL_REPLAY_REJECTED", action: "reject_normal_replay_no_write", reason: "CONSUMPTION_NORMAL_REPLAY" });
add({ id: "E010", priority: 11, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v2", when: { run_mode: "recovery", normal_consumption: "absent", approval_maximum_recovery_bootstraps: [0, 2, 32], recovery_slots_consumed: 0, budget_relation: "not_applicable" }, state: "RECOVERY_REJECTED", action: "reject_recovery_without_consumption_no_write", reason: "CONSUMPTION_RECOVERY_WITHOUT_RECORD" });
add({ id: "E011", priority: 12, context: "entry_preflight", sourceSchema: "locked_entry_ineligible_v2", when: { run_mode: "recovery", normal_consumption: "valid", recovery_budget: "exhausted", approval_maximum_recovery_bootstraps: [0, 2, 32], recovery_slots_consumed: [0, 2, 32], budget_relation: "exhausted_exact" }, state: "RECOVERY_EXHAUSTED_UNTERMINATED", action: "reject_recovery_exhausted_no_write", reason: "CONSUMPTION_RECOVERY_BUDGET_EXHAUSTED" });
add({ id: "E012", priority: 13, context: "entry_preflight", sourceSchema: "locked_normal_eligible_v2", when: { normal_consumption: "absent", private_selection_match: "not_applicable", recovery_budget: "not_applicable", recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: "absent_initial", initial_phase_state: "empty", entry_product_relation: "valid_normal" }, state: "NORMAL_ADMISSION_READY", action: "reserve_normal_admission", reason: "ADMISSION_NORMAL_RESERVATION_READY", nextContext: "attempt_admission" });
add({ id: "E013", priority: 14, context: "entry_preflight", sourceSchema: "locked_recovery_eligible_v2", when: { normal_consumption: "valid", private_selection_match: "match", recovery_budget: "available", approval_maximum_recovery_bootstraps: [2, 32], recovery_slots_consumed: [0, 1, 2, 31], next_recovery_ordinal: [1, 2, 3, 32], budget_relation: "available_exact", recovery_slot: "not_applicable", repository_identity: "valid", phase_chain: "valid", ref_relation: ["absent_initial", "at_last_commit"], initial_phase_state: ["empty", "recoverable_nonempty"], entry_product_relation: "valid_recovery" }, state: "RECOVERY_ADMISSION_READY", action: "reserve_recovery_admission", reason: "ADMISSION_RECOVERY_RESERVATION_READY", nextContext: "attempt_admission" });

add({ id: "D001", priority: 1, context: "attempt_admission", sourceSchema: "attempt_admission_v1", when: { run_mode: "normal", admission_kind: "normal", admission_ordinal: "valid_current", linked_attempt_record: "absent", normal_consumption_binding: "valid", recovery_budget_binding: "not_applicable" }, state: "ATTEMPT_START_READY", action: "write_linked_attempt_start", reason: "ADMISSION_NORMAL_LINKED_START_READY" });
add({ id: "D002", priority: 2, context: "attempt_admission", sourceSchema: "attempt_admission_v1", when: { run_mode: "recovery", admission_kind: "recovery", admission_ordinal: "valid_current", linked_attempt_record: "absent", normal_consumption_binding: "valid", recovery_budget_binding: "valid" }, state: "ATTEMPT_START_READY", action: "write_linked_attempt_start", reason: "ADMISSION_RECOVERY_LINKED_START_READY" });
add({ id: "D003", priority: 3, context: "attempt_admission", sourceSchema: "attempt_admission_v1", when: { run_mode: "normal", admission_kind: "normal", admission_ordinal: "valid_current", linked_attempt_record: "durable", normal_consumption_binding: "valid", recovery_budget_binding: "not_applicable" }, state: "NORMAL_ATTEMPT_STARTED", action: "dispatch_normal_campaign_progression", reason: "ADMISSION_NORMAL_START_DURABLE", nextContext: "campaign_progression" });
add({ id: "D004", priority: 4, context: "attempt_admission", sourceSchema: "attempt_admission_v1", when: { run_mode: "recovery", admission_kind: "recovery", admission_ordinal: "valid_current", linked_attempt_record: "durable", normal_consumption_binding: "valid", recovery_budget_binding: "valid" }, state: "RECOVERY_ATTEMPT_STARTED", action: "dispatch_recovery_reconstruction", reason: "ADMISSION_RECOVERY_START_DURABLE", nextContext: "recovery_reconstruction" });

const priorReasons = ["RESOURCE_PRIOR_ATTEMPT_OBSERVATION_INCOMPLETE", "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID"];
add({ id: "S001", priority: 1, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v1", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", prior_attempt_record: ["valid_unclosed", "invalid", "conflict"], launch_identity_evidence: "complete", process_absence: "kernel_confirmed_absent" }, state: "PRIOR_ATTEMPT_METER_FINALIZATION_READY", action: "handoff_meter_finalization_infrastructure", reason: "RESOURCE_PRIOR_PROCESS_ABSENCE_PROVED", nextContext: "meter_finalization" });
add({ id: "S002", priority: 2, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v1", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: "complete", process_absence: "one_exact_identity_live" }, state: "PRIOR_PROCESS_RECONCILIATION", action: "retain_lock_and_reconcile_prior_process", reason: "RESOURCE_PRIOR_PROCESS_STILL_LIVE" });
add({ id: "S003", priority: 3, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v1", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: "complete", process_absence: ["ambiguous", "unkillable", "invalid"] }, state: "PRIOR_PROCESS_ABSENCE_UNPROVED", action: "retain_lock_and_stop_no_terminal", reason: "RESOURCE_PRIOR_PROCESS_ABSENCE_UNPROVED" });
add({ id: "S004", priority: 4, context: "prior_attempt_safety", sourceSchema: "prior_attempt_safety_v1", when: { selected_precedence_reason: priorReasons, precedence_binding: "valid", launch_identity_evidence: ["absent", "invalid"] }, state: "PRIOR_PROCESS_EVIDENCE_INVALID", action: "retain_lock_and_stop_no_terminal", reason: "RESOURCE_PRIOR_LAUNCH_IDENTITY_INVALID" });

function addLiveActions(sourceSchema, phaseModes) {
  const prefix = sourceSchema === "live_e0_evaluate_action_v2" ? "AE" : "AN";
  add({ id: `${prefix}001`, priority: 1, context: "live_supervisor", sourceSchema, when: { state: "RESERVED", phase_mode: phaseModes, launch_prerequisite: "satisfied" }, state: "RESERVED", action: "create_launch_intent", reason: "STATE_LIVE_CREATE_LAUNCH_INTENT" });
  add({ id: `${prefix}002`, priority: 2, context: "live_supervisor", sourceSchema, when: { state: "LAUNCH_INTENT_DURABLE", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "LAUNCH_INTENT_DURABLE", action: "spawn_phase", reason: "STATE_LIVE_SPAWN_PHASE" });
  add({ id: `${prefix}003`, priority: 3, context: "live_supervisor", sourceSchema, when: { state: "SPAWN_FAILED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "SPAWN_FAILED", action: "publish_harness_failure_phase_terminal", reason: "STATE_LIVE_CLOSE_SPAWN_FAILURE" });
  add({ id: `${prefix}004`, priority: 4, context: "live_supervisor", sourceSchema, when: { state: "SPAWNED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "SPAWNED", action: "reap_phase", reason: "STATE_LIVE_REAP_PHASE" });
  add({ id: `${prefix}005`, priority: 5, context: "live_supervisor", sourceSchema, when: { state: "REAPED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "REAPED", action: "retain_bounded_result_or_harness_failure", reason: "STATE_LIVE_RETAIN_RESULT" });
  add({ id: `${prefix}006`, priority: 6, context: "live_supervisor", sourceSchema, when: { state: "RESULT_RETAINED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "RESULT_RETAINED", action: "publish_phase_content", reason: "STATE_LIVE_PUBLISH_CONTENT" });
  add({ id: `${prefix}007`, priority: 7, context: "live_supervisor", sourceSchema, when: { state: "CONTENT_PUBLISHED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "CONTENT_PUBLISHED", action: "publish_valid_or_harness_phase_terminal", reason: "STATE_LIVE_PUBLISH_PHASE_TERMINAL" });
  add({ id: `${prefix}008`, priority: 8, context: "live_supervisor", sourceSchema, when: { state: ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"], phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "PHASE_TERMINAL", action: "create_commit_intent", reason: "STATE_LIVE_CREATE_COMMIT_INTENT" });
  add({ id: `${prefix}009`, priority: 9, context: "live_supervisor", sourceSchema, when: { state: "COMMIT_INTENT_DURABLE", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "COMMIT_INTENT_DURABLE", action: "create_ledgered_commit_objects", reason: "STATE_LIVE_CREATE_COMMIT_OBJECTS" });
  if (phaseModes.includes("P0:not_applicable")) {
    add({ id: `${prefix}010I`, priority: 10, context: "live_supervisor", sourceSchema, when: { state: "COMMIT_OBJECT_EXACT", phase_mode: "P0:not_applicable", launch_prerequisite: "not_applicable" }, state: "COMMIT_OBJECT_EXACT", action: "cas_create_initial_ref", reason: "STATE_LIVE_CREATE_INITIAL_REF" });
  }
  const existingRefModes = phaseModes.filter((mode) => mode !== "P0:not_applicable");
  if (existingRefModes.length > 0) {
    add({ id: `${prefix}010E`, priority: 11, context: "live_supervisor", sourceSchema, when: { state: "COMMIT_OBJECT_EXACT", phase_mode: existingRefModes, launch_prerequisite: "not_applicable" }, state: "COMMIT_OBJECT_EXACT", action: "cas_update_existing_ref", reason: "STATE_LIVE_UPDATE_EXISTING_REF" });
  }
  add({ id: `${prefix}011`, priority: 12, context: "live_supervisor", sourceSchema, when: { state: "REF_APPLIED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "REF_APPLIED", action: "reparse_exact_commit_then_progress", reason: "STATE_LIVE_REPARSE_COMMIT" });
  add({ id: `${prefix}012`, priority: 13, context: "live_supervisor", sourceSchema, when: { state: "COMMITTED", phase_mode: phaseModes, launch_prerequisite: "not_applicable" }, state: "COMMITTED", action: "dispatch_campaign_progression", reason: "STATE_LIVE_DISPATCH_COMMITTED_PHASE", nextContext: "campaign_progression" });
}

addLiveActions("live_candidate_action_v2", nonEvaluatePhaseModes);
addLiveActions("live_e0_evaluate_action_v2", ["E0:evaluate"]);

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

addLiveEventRules("live_transition_candidate_v2", nonEvaluatePhaseModes);
addLiveEventRules("live_transition_e0_evaluate_v2", ["E0:evaluate"]);

const recoveryActions = [
  ["R001", "UNSEEN", "resume_campaign_progression_from_predecessor", "STATE_RECOVERY_PHASE_UNSEEN"],
  ["R002", "RESERVED", "publish_quarantine_phase_terminal", "STATE_PHASE_WITHOUT_TERMINAL"],
  ["R003", ["LAUNCH_INTENT_DURABLE", "SPAWNED"], "reconcile_process_then_publish_quarantine_phase_terminal", "STATE_UNREAPED_PROCESS_POSSIBLE"],
  ["R004", "SPAWN_FAILED", "publish_harness_failure_phase_terminal", "STATE_RECOVERY_CLOSE_SPAWN_FAILURE"],
  ["R005", "REAPED", "retain_recoverable_result_else_publish_quarantine_phase_terminal", "STATE_RECOVERY_REAP_RESIDUE"],
  ["R006", "RESULT_RETAINED", "publish_phase_content", "STATE_RECOVERY_RESULT_RETAINED"],
  ["R007", "CONTENT_PUBLISHED", "publish_valid_or_harness_phase_terminal", "STATE_RECOVERY_CONTENT_PUBLISHED"],
  ["R008", ["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"], "create_commit_intent", "STATE_RECOVERY_PHASE_TERMINAL"],
  ["R009", "COMMIT_INTENT_DURABLE", "create_ledgered_commit_objects", "STATE_RECOVERY_COMMIT_INTENT"],
  ["R010", "REF_APPLIED", "reparse_exact_commit_then_progress", "STATE_RECOVERY_REPARSE_COMMIT"],
  ["R011", "COMMITTED", "resume_campaign_progression_from_committed_phase", "STATE_RECOVERY_PHASE_COMMITTED"],
];
for (const [id, state, action, reason] of recoveryActions) {
  add({ id, priority: 100 + rules.length, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v2", when: { state, process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: "not_applicable" }, state: `RECOVERY_${Array.isArray(state) ? "MULTI" : state}`, action, reason });
}
add({ id: "R012I", priority: 500, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v2", when: { state: "COMMIT_OBJECT_EXACT", phase_mode: "P0:not_applicable", process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: "not_applicable" }, state: "COMMIT_OBJECT_EXACT", action: "cas_create_initial_ref", reason: "STATE_RECOVERY_CREATE_INITIAL_REF" });
add({ id: "R012E", priority: 501, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v2", when: { state: "COMMIT_OBJECT_EXACT", phase_mode: allPhaseModes.filter((mode) => mode !== "P0:not_applicable"), process_reconciliation: ["not_applicable", "kernel_confirmed_absent"], recoverable_result: "not_applicable" }, state: "COMMIT_OBJECT_EXACT", action: "cas_update_existing_ref", reason: "STATE_RECOVERY_UPDATE_EXISTING_REF" });
add({ id: "R013", priority: 502, context: "recovery_reconstruction", sourceSchema: "recovery_reconstruction_v2", when: { process_reconciliation: ["multiple_token_matches", "pid_identity_mismatch", "unkillable", "invalid"] }, state: "RECOVERY_INTEGRITY_INVALID", action: "request_infrastructure_failure", reason: "STATE_PROCESS_RECONCILIATION_FAILED" });

add({ id: "C001", priority: 1, context: "campaign_progression", sourceSchema: "campaign_progression_v2", when: { trigger: "normal_consumption", last_committed_phase: "none", last_phase_outcome: "none", ref_relation: "absent_initial" }, state: "NEXT_PHASE_READY", action: "reserve_P0_then_live_supervisor", reason: "STATE_NEXT_PHASE_P0", nextContext: "live_supervisor" });
add({ id: "C002", priority: 2, context: "campaign_progression", sourceSchema: "campaign_progression_v2", when: { trigger: "phase_committed", last_committed_phase: ["P0", "P1", "P2", "P3", "P4"], last_phase_outcome: "valid_outcome", ref_relation: "at_last_commit" }, state: "NEXT_PHASE_READY", action: "reserve_successor_then_live_supervisor", reason: "STATE_NEXT_CANDIDATE_PHASE", nextContext: "live_supervisor" });
add({ id: "C003", priority: 3, context: "campaign_progression", sourceSchema: "campaign_progression_v2", when: { trigger: "phase_committed", last_committed_phase: "P5", last_phase_outcome: "valid_outcome", ref_relation: "at_last_commit" }, state: "EVALUATOR_READY", action: "reserve_E0_evaluate_then_private_map", reason: "STATE_EVALUATOR_AFTER_P5", nextContext: "e0_private_map" });
add({ id: "C004", priority: 4, context: "campaign_progression", sourceSchema: "campaign_progression_v2", when: { trigger: "phase_committed", last_committed_phase: candidatePhases, last_phase_outcome: ["harness_failure", "quarantine"], ref_relation: "at_last_commit" }, state: "CLOSURE_READY", action: "reserve_E0_close_prior_failure_then_live_supervisor", reason: "STATE_CLOSURE_AFTER_FAILED_PHASE", nextContext: "live_supervisor" });
add({ id: "C005", priority: 5, context: "campaign_progression", sourceSchema: "campaign_progression_v2", when: { trigger: "phase_committed", last_committed_phase: "E0", last_phase_outcome: ["valid_outcome", "harness_failure", "quarantine"], ref_relation: "at_last_commit" }, state: "CAMPAIGN_CLOSURE_READY", action: "request_attested_closure", reason: "STATE_E0_COMMITTED", nextContext: "meter_finalization" });

add({ id: "M001", priority: 1, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: ["one_exact_identity_live", "ambiguous", "unkillable"], lock_release: "held" }, state: "METER_PROCESS_RECONCILIATION", action: "retain_lock_and_reconcile_processes", reason: "METER_PROCESS_ABSENCE_NOT_PROVED" });
add({ id: "M002", priority: 2, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "absent", attempt_end: "absent", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "RESOURCE_WRITE_READY", action: "write_resource_receipt_only", reason: "METER_RESOURCE_RECEIPT_READY" });
add({ id: "M003", priority: 3, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "absent", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "ATTEMPT_END_WRITE_READY", action: "write_attempt_end_only", reason: "METER_ATTEMPT_END_READY" });
add({ id: "M004", priority: 4, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", durable_state: "valid", terminal_request: "absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "RECOVERABLE_RELEASE_READY", action: "release_recoverable_lock", reason: "METER_RECOVERABLE_RELEASE_READY" });
add({ id: "M005", priority: 5, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", durable_state: "valid", terminal_request: "attested_closure", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "ATTESTED_TERMINAL_WRITE_READY", action: "publish_attested_terminal_only", reason: "METER_ATTESTED_TERMINAL_READY" });
add({ id: "M006", priority: 6, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", durable_state: ["valid", "invalid"], terminal_request: ["infrastructure_failure", "invalid", "conflict"], resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "INFRASTRUCTURE_TERMINAL_WRITE_READY", action: "publish_infrastructure_terminal_only", reason: "METER_INFRASTRUCTURE_TERMINAL_READY" });
add({ id: "M007", priority: 7, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", durable_state: "invalid", terminal_request: ["absent", "attested_closure"], resource_receipt: "durable", attempt_end: "durable", campaign_terminal: "absent", recalculation: "not_started", lock_release: "held" }, state: "INFRASTRUCTURE_TERMINAL_WRITE_READY", action: "publish_infrastructure_terminal_only", reason: "METER_DURABLE_STATE_INVALID" });
add({ id: "M008", priority: 8, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: ["valid_attested_closure", "valid_infrastructure_failure"], recalculation: "not_started", lock_release: "held" }, state: "READONLY_RECALCULATION_READY", action: "perform_readonly_recalculation", reason: "METER_TERMINAL_DURABLE_RECALC_READY" });
add({ id: "M009", priority: 9, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "durable", campaign_terminal: ["valid_attested_closure", "valid_infrastructure_failure"], recalculation: "complete", lock_release: "held" }, state: "FINAL_LOCK_RELEASE_READY", action: "release_final_lock", reason: "METER_READONLY_RECALC_COMPLETE" });
add({ id: "M010", priority: 10, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { campaign_terminal: "invalid", lock_release: "held" }, state: "INVALID_TERMINAL_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "CAMPAIGN_TERMINAL_INVALID_OCCUPIED_PATH" });
add({ id: "M011", priority: 11, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "invalid", campaign_terminal: "absent", lock_release: "held" }, state: "RESOURCE_RECEIPT_INVALID_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "METER_RESOURCE_RECEIPT_INVALID" });
add({ id: "M012", priority: 12, context: "meter_finalization", sourceSchema: "meter_finalization_v2", when: { process_absence: "kernel_confirmed_absent", resource_receipt: "durable", attempt_end: "invalid", campaign_terminal: "absent", lock_release: "held" }, state: "ATTEMPT_END_INVALID_UNRECOVERABLE", action: "retain_lock_and_stop_no_terminal", reason: "METER_ATTEMPT_END_INVALID" });

const e0MapRuleSpecs = [
  ["P001", "evaluate", "MAP_UNSEEN", "request_open_intent", "absent", "MAP_OPEN_INTENT_DURABLE", "write_private_map_open_intent", "E0_PRIVATE_MAP_INTENT_READY"],
  ["P002", "evaluate", "MAP_OPEN_INTENT_DURABLE", "open_syscall_success", "absent", "MAP_OPENED_UNRECEIPTED", "open_private_map_trusted_descriptor", "E0_PRIVATE_MAP_OPEN_SUCCEEDED"],
  ["P003", "evaluate", "MAP_OPEN_INTENT_DURABLE", "open_syscall_failure", "absent", "MAP_OPEN_FAILED_DURABLE", "publish_map_open_harness_failure_terminal", "E0_PRIVATE_MAP_OPEN_FAILED"],
  ["P004", "evaluate", "MAP_OPENED_UNRECEIPTED", "publish_opened_receipt", "trusted_meter_only", "MAP_OPENED_RECEIPT_DURABLE", "write_private_map_opened_receipt", "E0_PRIVATE_MAP_RECEIPT_READY"],
  ["P005", "evaluate", "MAP_OPENED_RECEIPT_DURABLE", "dispatch_live_supervisor", "trusted_meter_only", "E0_LIVE_READY", "dispatch_e0_live_supervisor", "E0_PRIVATE_MAP_LAUNCH_GATE_SATISFIED"],
  ["P006", "evaluate", "MAP_OPEN_FAILED_DURABLE", "dispatch_live_supervisor", "absent", "COMMIT_INTENT_DURABLE", "create_commit_intent", "E0_PRIVATE_MAP_FAILURE_COMMIT_READY"],
];
for (const [id, mode, mapState, event, descriptorState, state, action, reason] of e0MapRuleSpecs) {
  add({ id, priority: rules.length + 1, context: "e0_private_map", sourceSchema: "e0_private_map_v2", when: { e0_mode: mode, map_state: mapState, event, descriptor_state: descriptorState }, state, action, reason, nextContext: action === "dispatch_e0_live_supervisor" ? "live_supervisor" : action === "create_commit_intent" ? "repository_validation" : "e0_private_map" });
}
for (const mapState of privateMapStates.filter((state) => state !== "not_applicable")) {
  add({ id: `PH-${mapState}`, priority: rules.length + 100, context: "e0_private_map", sourceSchema: "e0_private_map_v2", when: { e0_mode: "evaluate", map_state: mapState, event: "root_crashed" }, state: "E0_RECOVERY_HANDOFF", action: "handoff_recovery_reconstruction", reason: "E0_PRIVATE_MAP_ROOT_CRASH", nextContext: "recovery_reconstruction" });
}
add({ id: "PCLOSE", priority: 9999, context: "e0_private_map", sourceSchema: "e0_private_map_v2", when: { e0_mode: "close_prior_failure", event: privateMapEvents }, state: "E0_PRIVATE_MAP_FORBIDDEN", action: "request_infrastructure_failure", reason: "E0_PRIVATE_MAP_FORBIDDEN_IN_CLOSURE_MODE" });

add({ id: "G001", priority: 1, context: "repository_validation", sourceSchema: "git_commit_validation_v1", when: { commit_intent_relation: "valid_self_excluding", commit_object_state: "absent", cas_status: "not_attempted" }, state: "COMMIT_OBJECT_CREATION_READY", action: "create_ledgered_commit_objects", reason: "GIT_COMMIT_INTENT_SELF_EXCLUDING" });
add({ id: "G002", priority: 2, context: "repository_validation", sourceSchema: "git_commit_validation_v1", when: { commit_intent_relation: ["invalid_self_including", "invalid"] }, state: "GIT_INTENT_INVALID", action: "request_infrastructure_failure", reason: "GIT_COMMIT_INTENT_SELF_CYCLE" });
add({ id: "G003", priority: 3, context: "repository_validation", sourceSchema: "git_commit_validation_v1", when: { phase_mode: "P0:not_applicable", commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "absent_initial", cas_status: "not_attempted" }, state: "INITIAL_CAS_READY", action: "cas_create_initial_ref", reason: "GIT_INITIAL_REF_RELATION_VALID" });
add({ id: "G004", priority: 4, context: "repository_validation", sourceSchema: "git_commit_validation_v1", when: { phase_mode: allPhaseModes.filter((mode) => mode !== "P0:not_applicable"), commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", ref_relation: "at_parent", cas_status: "not_attempted" }, state: "EXISTING_CAS_READY", action: "cas_update_existing_ref", reason: "GIT_EXISTING_REF_RELATION_VALID" });
add({ id: "G005", priority: 5, context: "repository_validation", sourceSchema: "git_commit_validation_v1", when: { commit_intent_relation: "valid_self_excluding", commit_object_state: "exact", cas_status: "applied" }, state: "COMMIT_REPARSE_READY", action: "reparse_exact_commit_then_progress", reason: "GIT_CAS_APPLIED_REPARSE_REQUIRED" });

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
  if (schemaId === "locked_entry_ineligible_v2" && source.budget_relation === "exhausted_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps)
      || source.recovery_slots_consumed !== source.approval_maximum_recovery_bootstraps
      || source.recovery_budget !== "exhausted") {
      return { ok: false, reason: "SCHEMA_BUDGET_EXHAUSTION_RELATION_INVALID" };
    }
  }
  if (schemaId === "locked_recovery_eligible_v2" && source.budget_relation === "available_exact") {
    if (!Number.isInteger(source.approval_maximum_recovery_bootstraps)
      || !Number.isInteger(source.recovery_slots_consumed)
      || !Number.isInteger(source.next_recovery_ordinal)
      || source.recovery_slots_consumed >= source.approval_maximum_recovery_bootstraps
      || source.next_recovery_ordinal !== source.recovery_slots_consumed + 1
      || source.recovery_budget !== "available") {
      return { ok: false, reason: "SCHEMA_BUDGET_AVAILABILITY_RELATION_INVALID" };
    }
  }
  if (schemaId === "meter_finalization_v2") {
    const relationValid = (source.run_mode === "normal" && source.admission_kind === "normal" && source.attempt_ordinal === "A0")
      || (source.run_mode === "recovery" && source.admission_kind === "recovery" && source.attempt_ordinal === "A1");
    if (!relationValid) return { ok: false, reason: "SCHEMA_METER_ATTEMPT_RELATION_INVALID" };
  }
  if (schemaId === "recovery_reconstruction_v2") {
    const mapRelationValid = source.phase_mode === "E0:evaluate"
      ? source.private_map_state === "MAP_OPENED_RECEIPT_DURABLE" && source.private_map_binding === "valid_current" && source.phase_private_map_relation === "valid"
      : source.private_map_state === "not_applicable" && source.private_map_binding === "not_applicable" && source.phase_private_map_relation === "valid";
    if (!mapRelationValid) return { ok: false, reason: "SCHEMA_RECOVERY_PRIVATE_MAP_RELATION_INVALID" };
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

function durableRecord(path, recordType, payload, producer = "fixture_seed") {
  const body = { schema: "tt-supervised-durable-record-v1", path, record_type: recordType, payload, producer };
  const canonicalBytes = canonical(body);
  return { ...body, canonical_bytes: canonicalBytes, sha256: sha256(canonicalBytes) };
}

function validateUniverse(records) {
  const paths = new Set();
  for (const record of records) {
    if (paths.has(record.path)) throw new Error(`duplicate durable path ${record.path}`);
    paths.add(record.path);
    const { canonical_bytes: canonicalBytes, sha256: digest, ...body } = record;
    if (canonical(body) !== canonicalBytes) throw new Error(`noncanonical durable bytes ${record.path}`);
    if (sha256(canonicalBytes) !== digest) throw new Error(`durable digest mismatch ${record.path}`);
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
    if (!resource || !end) throw new Error(`campaign terminal linkage invalid ${record.path}`);
  }
  for (const record of records.filter((row) => row.record_type === "launch_intent")) {
    const capability = records.find((row) => row.record_type === "capability_receipt" && row.sha256 === record.payload.capability_receipt_sha256);
    if (!capability) throw new Error(`launch capability linkage invalid ${record.path}`);
    if (record.payload.phase_mode === "E0:evaluate") {
      const receipt = records.find((row) => row.record_type === "private_map_opened_receipt" && row.sha256 === record.payload.private_map_receipt_sha256);
      if (!receipt) throw new Error(`E0 launch private-map linkage invalid ${record.path}`);
    }
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
  return (source.phase_mode || "P0:not_applicable").split(":")[0];
}

function attemptOrdinal(source) {
  if (source.admission_kind === "recovery" || source.run_mode === "recovery") {
    const ordinal = Number.isInteger(source.next_recovery_ordinal) ? source.next_recovery_ordinal : 1;
    return `A${ordinal}`;
  }
  return "A0";
}

function seedRecordUniverse(controlId, schemaId, source) {
  const records = [];
  const addRecord = (suffix, type, payload = {}) => records.push(durableRecord(`fixtures/${controlId}/${suffix}.json`, type, payload));
  const ensureRecord = (suffix, type, payload = {}) => {
    const path = `fixtures/${controlId}/${suffix}.json`;
    if (!records.some((record) => record.path === path)) records.push(durableRecord(path, type, payload));
  };
  const admissionDigest = (ordinal) => records.find((record) => ["normal_admission", "recovery_admission"].includes(record.record_type) && record.payload.ordinal === ordinal)?.sha256;
  if (source.prior_attempt_closure === "valid_unclosed" || source.prior_attempt_record === "valid_unclosed") {
    addRecord("admissions/A0", "normal_admission", { ordinal: "A0" });
    addRecord("attempts/A0/start", "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: admissionDigest("A0") });
  }
  if (["valid_unstarted", "valid_current"].includes(source.admission_record)) {
    const recovery = source.admission_kind === "recovery" || source.run_mode === "recovery";
    addRecord(`admissions/${recovery ? "A1" : "A0"}`, recovery ? "recovery_admission" : "normal_admission", { ordinal: recovery ? "A1" : "A0" });
  }
  if (source.normal_consumption === "valid" || source.normal_consumption_binding === "valid" || source.consumption_record === "valid") {
    if (!records.some((record) => record.record_type === "normal_admission")) addRecord("admissions/A0", "normal_admission", { ordinal: "A0" });
  }
  if (source.run_mode === "recovery") {
    if (!records.some((record) => record.record_type === "normal_admission")) addRecord("admissions/A0", "normal_admission", { ordinal: "A0" });
    if (!records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === "A0")) addRecord("attempts/A0/start", "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: admissionDigest("A0") });
    if (!records.some((record) => record.record_type === "attempt_end" && record.payload.ordinal === "A0")) addRecord("attempts/A0/end", "attempt_end", { ordinal: "A0", outcome: "recoverable_crash" });
  }
  if (["durable", "valid_current"].includes(source.attempt_record) || source.linked_attempt_record === "durable") {
    const ordinal = source.admission_kind === "recovery" || source.run_mode === "recovery" ? "A1" : "A0";
    if (!records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === ordinal)) addRecord(`attempts/${ordinal}/start`, "attempt_start", { ordinal, admission_ordinal: ordinal, admission_sha256: admissionDigest(ordinal) });
  }
  if (source.launch_identity_evidence === "complete") addRecord("process/launch-identity", "launch_identity", { exact_kernel_identity: true });
  if (source.resource_receipt === "durable") addRecord(`attempts/${attemptOrdinal(source)}/resource`, "resource_receipt", { ordinal: attemptOrdinal(source), complete: true });
  if (source.attempt_end === "durable") addRecord(`attempts/${attemptOrdinal(source)}/end`, "attempt_end", { ordinal: attemptOrdinal(source), complete: true, terminal_request: source.terminal_request || "unknown" });
  if (source.capability_receipt === "valid_current") addRecord("capability/launch-barrier", "capability_receipt", { descriptor_schema: "candidate_boundary_descriptor_v2", binding: "valid_current" });
  const needsE0Reservation = source.evaluation_context === "e0_private_map" || source.private_map_state === "MAP_OPENED_RECEIPT_DURABLE";
  if (needsE0Reservation) ensureRecord("phases/E0/reservation", "evaluator_phase_reservation", { phase: "E0", binding: source.reservation_binding || source.private_map_binding });
  const mapState = source.map_state || source.private_map_state;
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(mapState)) {
    const reservation = records.find((record) => record.record_type === "evaluator_phase_reservation" && record.payload.phase === "E0");
    ensureRecord("E0/private-map-intent", "private_map_open_intent", { reservation_binding: "valid_current", reservation_sha256: reservation?.sha256 });
  }
  if (mapState === "MAP_OPENED_RECEIPT_DURABLE") {
    const reservation = records.find((record) => record.record_type === "evaluator_phase_reservation" && record.payload.phase === "E0");
    const intent = records.find((record) => record.record_type === "private_map_open_intent");
    ensureRecord("E0/private-map-receipt", "private_map_opened_receipt", { reservation_binding: "valid_current", reservation_sha256: reservation?.sha256, open_intent_sha256: intent?.sha256 });
  }
  if (mapState === "MAP_OPEN_FAILED_DURABLE") {
    const intent = records.find((record) => record.record_type === "private_map_open_intent");
    ensureRecord("E0/terminal", "phase_terminal", { phase: "E0", outcome: "harness_failure", reason: "private_map_open_failed", open_intent_sha256: intent?.sha256 });
  }

  if (source.state && liveStates.includes(source.state) && source.state !== "UNSEEN") {
    const phase = phaseId(source);
    const reservationType = phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation";
    ensureRecord(`phases/${phase}/reservation`, reservationType, { phase });
    const atOrAfter = (threshold) => liveStates.indexOf(source.state) >= liveStates.indexOf(threshold);
    if (atOrAfter("LAUNCH_INTENT_DURABLE")) {
      const capability = records.find((record) => record.record_type === "capability_receipt");
      const mapReceipt = records.find((record) => record.record_type === "private_map_opened_receipt");
      ensureRecord(`phases/${phase}/launch-intent`, "launch_intent", { phase, phase_mode: source.phase_mode, capability_receipt_sha256: capability?.sha256, private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? mapReceipt?.sha256 : null });
    }
    if (["SPAWNED", "REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) ensureRecord(`phases/${phase}/spawn`, "phase_spawn", { phase });
    if (["REAPED", "RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) ensureRecord(`phases/${phase}/reap`, "phase_reap", { phase });
    if (["RESULT_RETAINED", "CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state)) ensureRecord(`phases/${phase}/result`, "phase_result", { phase });
    if (["CONTENT_PUBLISHED", "TERMINAL_VALID_OUTCOME"].includes(source.state)) ensureRecord(`phases/${phase}/content`, "phase_content", { phase });
    if (["TERMINAL_VALID_OUTCOME", "TERMINAL_HARNESS_FAILURE", "TERMINAL_QUARANTINE"].includes(source.state) || atOrAfter("COMMIT_INTENT_DURABLE")) ensureRecord(`phases/${phase}/terminal`, "phase_terminal", { phase, outcome: source.state });
    if (atOrAfter("COMMIT_INTENT_DURABLE")) ensureRecord(`phases/${phase}/commit-intent`, "commit_intent", { phase, relation: "valid_self_excluding" });
    if (atOrAfter("COMMIT_OBJECT_EXACT")) ensureRecord(`phases/${phase}/commit-object`, "commit_object", { phase, exact: true });
    if (atOrAfter("REF_APPLIED")) ensureRecord(`phases/${phase}/ref-cas`, "ref_cas_attempt", { phase, applied: true });
    if (atOrAfter("COMMITTED")) ensureRecord(`phases/${phase}/committed`, "committed_phase", { phase, reparsed: true });
  }

  if (schemaId === "git_commit_validation_v1") {
    const phase = phaseId(source);
    ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    if (source.commit_intent_relation !== "invalid") ensureRecord(`phases/${phase}/commit-intent`, "commit_intent", { phase, relation: source.commit_intent_relation });
    if (source.commit_object_state === "exact") ensureRecord(`phases/${phase}/commit-object`, "commit_object", { phase, exact: true });
    if (source.cas_status === "applied") ensureRecord(`phases/${phase}/ref-cas`, "ref_cas_attempt", { phase, applied: true });
  }

  if (source.last_committed_phase && source.last_committed_phase !== "none") {
    const phase = source.last_committed_phase;
    ensureRecord(`phases/${phase}/reservation`, phase === "E0" ? "evaluator_phase_reservation" : "candidate_phase_reservation", { phase });
    ensureRecord(`phases/${phase}/committed`, "committed_phase", { phase, outcome: source.last_phase_outcome });
  }
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal)) {
    if (!records.some((record) => record.record_type === "normal_admission")) addRecord("admissions/A0", "normal_admission", { ordinal: "A0" });
    if (!records.some((record) => record.record_type === "attempt_start")) {
      const admission = records.find((record) => record.record_type === "normal_admission");
      addRecord("attempts/A0/start", "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: admission.sha256 });
    }
    if (!records.some((record) => record.record_type === "resource_receipt")) addRecord("attempts/A0/resource", "resource_receipt", { ordinal: "A0", complete: true });
    if (!records.some((record) => record.record_type === "attempt_end")) addRecord("attempts/A0/end", "attempt_end", { ordinal: "A0", complete: true });
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
  retain_recoverable_result_else_publish_quarantine_phase_terminal: "phase_terminal",
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
  const phase = phaseId(source);
  const ordinal = attemptOrdinal(source);
  if (action === "reserve_normal_admission") return `fixtures/${controlId}/admissions/A0.json`;
  if (action === "reserve_recovery_admission") return `fixtures/${controlId}/admissions/${ordinal}.json`;
  if (action === "write_linked_attempt_start") return `fixtures/${controlId}/attempts/${ordinal}/start.json`;
  if (action.includes("reserve_E0")) return `fixtures/${controlId}/phases/E0/reservation.json`;
  if (action.startsWith("reserve_")) return `fixtures/${controlId}/phases/${phase}/reservation.json`;
  if (action === "create_launch_intent") return `fixtures/${controlId}/phases/${phase}/launch-intent.json`;
  if (action === "spawn_phase") return `fixtures/${controlId}/phases/${phase}/spawn.json`;
  if (action === "reap_phase") return `fixtures/${controlId}/phases/${phase}/reap.json`;
  if (action.includes("phase_terminal") || action === "publish_map_open_harness_failure_terminal") return `fixtures/${controlId}/phases/${phase}/terminal.json`;
  if (action === "publish_phase_content") return `fixtures/${controlId}/phases/${phase}/content.json`;
  if (action === "create_commit_intent") return `fixtures/${controlId}/phases/${phase}/commit-intent.json`;
  if (action === "create_ledgered_commit_objects") return `fixtures/${controlId}/phases/${phase}/commit-object.json`;
  if (action.startsWith("cas_")) return `fixtures/${controlId}/phases/${phase}/ref-cas.json`;
  if (action === "reparse_exact_commit_then_progress") return `fixtures/${controlId}/phases/${phase}/committed.json`;
  if (action === "write_resource_receipt_only") return `fixtures/${controlId}/attempts/${ordinal}/resource.json`;
  if (action === "write_attempt_end_only") return `fixtures/${controlId}/attempts/${ordinal}/end.json`;
  if (action.includes("terminal_only")) return `fixtures/${controlId}/campaign-terminal.json`;
  if (action === "write_private_map_open_intent") return `fixtures/${controlId}/phases/E0/private-map-intent.json`;
  if (action === "write_private_map_opened_receipt") return `fixtures/${controlId}/phases/E0/private-map-receipt.json`;
  return `fixtures/${controlId}/actions/${action}.json`;
}

function executeAction(controlId, selection, source, records) {
  const output = clone(records);
  const type = actionRecordTypes[selection.next_action];
  const delta = [];
  if (type) {
    const path = actionRecordPath(controlId, selection.next_action, source);
    const ordinal = attemptOrdinal(source);
    const admission = records.find((candidate) => ["normal_admission", "recovery_admission"].includes(candidate.record_type) && candidate.payload.ordinal === ordinal);
    const typePayload = ["normal_admission", "recovery_admission", "attempt_start"].includes(type)
      ? { ordinal, admission_ordinal: ordinal, ...(type === "attempt_start" ? { admission_sha256: admission?.sha256 } : {}) }
      : {};
    const resource = records.find((candidate) => candidate.record_type === "resource_receipt");
    const attemptEnd = records.find((candidate) => candidate.record_type === "attempt_end");
    const capabilityReceipt = records.find((candidate) => candidate.record_type === "capability_receipt");
    const privateMapReceipt = records.find((candidate) => candidate.record_type === "private_map_opened_receipt");
    const evaluatorReservation = records.find((candidate) => candidate.record_type === "evaluator_phase_reservation" && candidate.payload.phase === "E0");
    const privateMapIntent = records.find((candidate) => candidate.record_type === "private_map_open_intent");
    const terminalPayload = type === "campaign_terminal" ? {
      kind: selection.next_action === "publish_attested_terminal_only" ? "valid_attested_closure" : "valid_infrastructure_failure",
      resource_receipt_sha256: resource?.sha256,
      attempt_end_sha256: attemptEnd?.sha256,
      terminal_request: source.terminal_request,
    } : {};
    const attemptEndPayload = type === "attempt_end" ? {
      ordinal,
      outcome: source.durable_state === "valid" && source.terminal_request === "absent"
        ? "recoverable_crash"
        : source.durable_state === "valid" && source.terminal_request === "attested_closure"
          ? "attested_closure"
          : "infrastructure_failure",
      terminal_request: source.terminal_request,
      durable_state: source.durable_state,
    } : {};
    const launchPayload = type === "launch_intent" ? {
      phase_mode: source.phase_mode,
      capability_receipt_sha256: capabilityReceipt?.sha256,
      private_map_receipt_sha256: source.phase_mode === "E0:evaluate" ? privateMapReceipt?.sha256 : null,
    } : {};
    const privateMapIntentPayload = type === "private_map_open_intent" ? {
      reservation_sha256: evaluatorReservation?.sha256,
      reservation_binding: source.reservation_binding,
    } : {};
    const privateMapReceiptPayload = type === "private_map_opened_receipt" ? {
      reservation_sha256: evaluatorReservation?.sha256,
      open_intent_sha256: privateMapIntent?.sha256,
      reservation_binding: source.reservation_binding,
    } : {};
    const mapFailurePayload = selection.next_action === "publish_map_open_harness_failure_terminal" ? {
      outcome: "harness_failure",
      reason: "private_map_open_failed",
      open_intent_sha256: privateMapIntent?.sha256,
    } : {};
    const record = durableRecord(path, type, {
      action: selection.next_action, selected_rule: selection.id || selection.selected_rule,
      phase: phaseId(source), attempt_ordinal: attemptOrdinal(source),
      ...typePayload,
      ...attemptEndPayload,
      ...terminalPayload,
      ...launchPayload,
      ...privateMapIntentPayload,
      ...privateMapReceiptPayload,
      ...mapFailurePayload,
    }, selection.next_action);
    if (addExactRecord(output, record)) delta.push(record);
  }
  const actionStatePatches = {
    reserve_normal_admission: { admission_record: "valid_current", admission_kind: "normal", admission_ordinal: "A0", normal_consumption: "valid" },
    reserve_recovery_admission: { admission_record: "valid_current", admission_kind: "recovery", admission_ordinal: attemptOrdinal(source) },
    write_linked_attempt_start: { linked_attempt_record: "durable", attempt_record: "valid_current" },
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
  const statePatch = actionStatePatches[selection.next_action] || {};
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
  } else {
    throw new Error(`${fault.id}: unknown fault kind ${fault.kind}`);
  }
  if (canonical(pre) === canonical(observed) || mutations.length === 0) throw new Error(`${fault.id}: non-none fault made no change`);
  return { observed, mutations };
}

function evidenceConsistency(source, records) {
  const has = (type) => records.some((record) => record.record_type === type);
  const hasPhase = (type, phase = phaseId(source)) => records.some((record) => record.record_type === type && record.payload.phase === phase);
  const requireEvidence = (condition, present, reason) => condition && !present ? reason : null;
  const ordinal = attemptOrdinal(source);
  const currentAdmissionType = source.admission_kind === "recovery" || source.run_mode === "recovery" ? "recovery_admission" : "normal_admission";
  let missing = requireEvidence(["valid_current", "valid_unstarted"].includes(source.admission_record), records.some((record) => record.record_type === currentAdmissionType && record.payload.ordinal === ordinal), "EVIDENCE_ADMISSION_MISSING");
  if (missing) return missing;
  missing = requireEvidence(source.attempt_record === "valid_current", records.some((record) => record.record_type === "attempt_start" && record.payload.ordinal === ordinal), "EVIDENCE_CURRENT_ATTEMPT_START_MISSING");
  if (missing) return missing;
  if (source.linked_attempt_record === "durable" && !has("attempt_start")) return "EVIDENCE_ATTEMPT_START_MISSING";
  if (source.resource_receipt === "durable" && !has("resource_receipt")) return "EVIDENCE_RESOURCE_RECEIPT_MISSING";
  if (source.attempt_end === "durable" && !has("attempt_end")) return "EVIDENCE_ATTEMPT_END_MISSING";
  if (source.capability_receipt === "valid_current" && !has("capability_receipt")) return "EVIDENCE_CAPABILITY_RECEIPT_MISSING";
  if ((source.map_state === "MAP_OPENED_RECEIPT_DURABLE" || source.private_map_state === "MAP_OPENED_RECEIPT_DURABLE") && !has("private_map_opened_receipt")) return "EVIDENCE_PRIVATE_MAP_RECEIPT_MISSING";
  if (source.evaluation_context === "e0_private_map" && !hasPhase("evaluator_phase_reservation", "E0")) return "EVIDENCE_E0_RESERVATION_MISSING";
  if (["MAP_OPEN_INTENT_DURABLE", "MAP_OPENED_UNRECEIPTED", "MAP_OPENED_RECEIPT_DURABLE", "MAP_OPEN_FAILED_DURABLE"].includes(source.map_state || source.private_map_state) && !has("private_map_open_intent")) return "EVIDENCE_PRIVATE_MAP_INTENT_MISSING";
  if (["valid_attested_closure", "valid_infrastructure_failure"].includes(source.campaign_terminal) && !has("campaign_terminal")) return "EVIDENCE_CAMPAIGN_TERMINAL_MISSING";
  if (source.state && liveStates.includes(source.state) && source.state !== "UNSEEN") {
    const stateIndex = liveStates.indexOf(source.state);
    const atOrAfter = (state) => stateIndex >= liveStates.indexOf(state);
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

function makeTransitionControl(spec) {
  const preRecords = spec.records ? clone(spec.records) : seedRecordUniverse(spec.id, spec.source_schema, spec.source);
  const pre = { source: clone(spec.source), records: preRecords };
  const { observed, mutations } = applyFault(pre, { id: spec.id, ...(spec.fault || { kind: "none" }) });
  const consistencyReason = evidenceConsistency(observed.source, observed.records);
  const selection = consistencyReason
    ? { selected_rule: "EVIDENCE_REJECT", reason: consistencyReason, state: "CONTROL_INVALID", next_action: "none", next_context: "control_validation" }
    : selectRule(spec.source_schema, observed.source);
  const executableSelection = {
    ...selection,
    id: selection.id || selection.selected_rule,
    next_action: selection.next_action,
    next_context: selection.next_context,
  };
  const executed = spec.execute_action === false
    ? { records: clone(observed.records), action_delta: [], post_state: { evaluation_context: executableSelection.next_context, state: executableSelection.state, selected_rule: executableSelection.id, reason: executableSelection.reason, last_action: "selection_only" } }
    : executeAction(spec.id, executableSelection, observed.source, observed.records);
  const fixture = {
    schema: "tt-supervised-transition-witness-v1", source_schema: spec.source_schema,
    pre_state: pre.source, pre_record_universe: pre.records,
    fault: spec.fault || { kind: "none" }, fault_mutations: mutations,
    observed_state_after_fault: observed.source, observed_record_universe_after_fault: observed.records,
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
    id: spec.id, category: spec.category || "v7_transition_witness", claim: spec.claim,
    target_kind: spec.target_kind || "matrix", fixture,
    fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_witness_engine",
  };
}

function makeRuleControl(rule) {
  const source = completeSource(rule);
  return makeTransitionControl({
    id: `SEC7-RULE-${rule.id}`, category: "complete_rule_guard_selection",
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

target("SEC7-ADMISSION-001", "normal admission is durable before A0 attempt-start", "E012", { assert: { selected_rule: "E012", selected_action: "reserve_normal_admission", post_action_counters: { values: { root_admissions: 1, root_attempt_starts: 0 } } } });
target("SEC7-ADMISSION-002", "A0 start consumes the existing normal admission and no second token", "D001", { assert: { selected_rule: "D001", selected_action: "write_linked_attempt_start", post_action_counters: { values: { root_admissions: 1, root_attempt_starts: 1 } } } });
target("SEC7-ADMISSION-003", "recovery admission is durable before recovery attempt-start", "E013", { assert: { selected_rule: "E013", selected_action: "reserve_recovery_admission", post_action_counters: { values: { root_admissions: 2, root_attempt_starts: 1, recovery_slots: 1, meter_finalizations: 1 } } } });
target("SEC7-ADMISSION-004", "recovery start uses the existing slot and cannot allocate another", "D002", { assert: { selected_rule: "D002", selected_action: "write_linked_attempt_start", post_action_counters: { values: { root_admissions: 2, root_attempt_starts: 2, recovery_slots: 1, meter_finalizations: 1 } } } });
target("SEC7-ENTRY-001", "normal entry rejects an invalid recovery-slot field", "E012", { fault: { kind: "replace", path: "source.recovery_slot", before: "not_applicable", after: "invalid" }, assert: { selected_rule: "DEFAULT" } });
target("SEC7-ENTRY-002", "recovery entry rejects an invalid ref relation", "E013", { fault: { kind: "replace", path: "source.ref_relation", before: "absent_initial", after: "invalid" }, assert: { selected_rule: "DEFAULT" } });
target("SEC7-ENTRY-003", "recovery entry rejects an invalid initial phase state", "E013", { fault: { kind: "replace", path: "source.initial_phase_state", before: "empty", after: "invalid" }, assert: { selected_rule: "DEFAULT" } });
target("SEC7-PRECEDENCE-001", "prior-attempt selection hands off only to the safety context", "E005", { execute_action: false, assert: { selected_rule: "E005", post_state: { evaluation_context: "prior_attempt_safety" } } });
target("SEC7-PRECEDENCE-002", "unproved prior-process absence retains the lock and writes no terminal", "S003", { assert: { selected_rule: "S003", selected_action: "retain_lock_and_stop_no_terminal" } });
target("SEC7-PRECEDENCE-003", "an invalid prior-attempt record preserves its distinct entry reason through the safety scan", "S001", {
  edits: { selected_precedence_reason: "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID", prior_attempt_record: "invalid" },
  execute_action: false,
  assert: { selected_rule: "S001", pre_state: { selected_precedence_reason: "RESOURCE_PRIOR_ATTEMPT_RECORD_INVALID" } },
});
target("SEC7-PRECEDENCE-004", "a mismatched reason-to-record binding cannot enter meter finalization", "S001", {
  fault: { kind: "replace", path: "source.precedence_binding", before: "valid", after: "invalid" },
  assert: { selected_rule: "DEFAULT", selected_action: "request_infrastructure_failure" },
});
target("SEC7-E0-GUARD-001", "E0 launch transition requires a bound private-map receipt", "TE-L002", { assert: { selected_rule: "TE-L002" } });
target("SEC7-E0-GUARD-002", "removing the E0 receipt makes the event evidence-invalid", "TE-L002", {
  fault: { kind: "remove_record", record_path: "fixtures/SEC7-E0-GUARD-002/E0/private-map-receipt.json" },
  records: (() => {
    const admission = durableRecord("fixtures/SEC7-E0-GUARD-002/admissions/A0.json", "normal_admission", { ordinal: "A0" });
    const reservation = durableRecord("fixtures/SEC7-E0-GUARD-002/phases/E0/reservation.json", "evaluator_phase_reservation", { phase: "E0", binding: "valid_current" });
    const intent = durableRecord("fixtures/SEC7-E0-GUARD-002/E0/private-map-intent.json", "private_map_open_intent", { reservation_binding: "valid_current", reservation_sha256: reservation.sha256 });
    return [
      admission,
      durableRecord("fixtures/SEC7-E0-GUARD-002/attempts/A0/start.json", "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: admission.sha256 }),
      durableRecord("fixtures/SEC7-E0-GUARD-002/capability/launch-barrier.json", "capability_receipt", { descriptor_schema: "candidate_boundary_descriptor_v2", binding: "valid_current" }),
      reservation,
      intent,
      durableRecord("fixtures/SEC7-E0-GUARD-002/E0/private-map-receipt.json", "private_map_opened_receipt", { reservation_binding: "valid_current", reservation_sha256: reservation.sha256, open_intent_sha256: intent.sha256 }),
    ];
  })(),
  assert: { selected_rule: "EVIDENCE_REJECT", selected_reason: "EVIDENCE_PRIVATE_MAP_RECEIPT_MISSING" },
});
target("SEC7-E0-OPEN-001", "private-map open syscall failure produces one harness-failure phase terminal", "P003", { assert: { selected_rule: "P003", selected_action: "publish_map_open_harness_failure_terminal", post_action_counters: { values: { root_attempt_starts: 1 } } } });
target("SEC7-E0-OPEN-002", "a durable map-open failure terminal proceeds to one E0 commit intent without launching the evaluator", "P006", { assert: { selected_rule: "P006", selected_action: "create_commit_intent", post_action_counters: { values: { commit_intents: 1, phase_spawns: 0 } } } });
target("SEC7-METER-001", "meter writes only the resource record at the first durable stage", "M002", { assert: { selected_rule: "M002", selected_action: "write_resource_receipt_only" } });
target("SEC7-METER-002", "meter resumes from durable resource by writing only attempt-end", "M003", { assert: { selected_rule: "M003", selected_action: "write_attempt_end_only", post_action_counters: { values: { meter_finalizations: 1 } } } });
target("SEC7-METER-003", "meter resumes from durable attempt-end by publishing only attested terminal", "M005", { assert: { selected_rule: "M005", selected_action: "publish_attested_terminal_only" } });
target("SEC7-METER-004", "meter resumes after terminal with read-only recalculation", "M008", { assert: { selected_rule: "M008", selected_action: "perform_readonly_recalculation" } });
target("SEC7-METER-005", "an invalid resource receipt retains the lock and cannot be overwritten", "M011", { assert: { selected_rule: "M011", selected_action: "retain_lock_and_stop_no_terminal" } });
target("SEC7-METER-006", "an invalid attempt-end retains the lock and cannot be overwritten", "M012", { assert: { selected_rule: "M012", selected_action: "retain_lock_and_stop_no_terminal" } });
target("SEC7-COUNTER-001", "commit-intent action increments from its literal record", "AN008", { assert: { selected_rule: "AN008", selected_action: "create_commit_intent", post_action_counters: { values: { commit_intents: 1 } } } });
target("SEC7-COUNTER-002", "commit-object action increments from its literal record", "AN009", { assert: { selected_rule: "AN009", selected_action: "create_ledgered_commit_objects", post_action_counters: { values: { commit_objects: 1 } } } });
target("SEC7-COUNTER-003", "initial CAS action increments from its literal record", "AN010I", { assert: { selected_rule: "AN010I", selected_action: "cas_create_initial_ref", post_action_counters: { values: { ref_cas_attempts: 1 } } } });
target("SEC7-COUNTER-004", "existing CAS action increments from its literal record", "AN010E", { assert: { selected_rule: "AN010E", selected_action: "cas_update_existing_ref", post_action_counters: { values: { ref_cas_attempts: 1 } } } });
target("SEC7-COUNTER-006", "spawn action increments from one literal spawn record", "AN002", { assert: { selected_rule: "AN002", selected_action: "spawn_phase", post_action_counters: { values: { phase_spawns: 1 } } } });
target("SEC7-COUNTER-007", "reap action increments from one literal reap record", "AN004", { assert: { selected_rule: "AN004", selected_action: "reap_phase", post_action_counters: { values: { phase_spawns: 1, phase_reaps: 1 } } } });
target("SEC7-COUNTER-008", "commit reparse increments the committed-phase counter", "AN011", { assert: { selected_rule: "AN011", selected_action: "reparse_exact_commit_then_progress", post_action_counters: { values: { committed_phases: 1 } } } });
target("SEC7-COUNTER-009", "P0 reservation increments the candidate reservation counter", "C001", { assert: { selected_rule: "C001", selected_action: "reserve_P0_then_live_supervisor", post_action_counters: { values: { candidate_phase_reservations: 1 } } } });
target("SEC7-COUNTER-010", "E0 reservation increments evaluator but not candidate runs", "C003", { assert: { selected_rule: "C003", selected_action: "reserve_E0_evaluate_then_private_map", post_action_counters: { values: { candidate_phase_reservations: 1, evaluator_phase_reservations: 1 } } } });
target("SEC7-COUNTER-005", "removing a durable attempt-start is detected before action", "D003", {
  fault: { kind: "remove_record", record_path: "fixtures/SEC7-COUNTER-005/attempts/A0/start.json" },
  assert: { selected_rule: "EVIDENCE_REJECT", selected_reason: "EVIDENCE_ATTEMPT_START_MISSING" },
});
target("SEC7-TERMINAL-001", "adding a lower field materially invalidates the closed terminal source", "E002", {
  fault: { kind: "add_source_property", property: "repository_identity", value: "invalid" },
  assert: { selected_rule: "SCHEMA_REJECT", selected_reason: "SCHEMA_KEYS_MISMATCH" },
});
target("SEC7-GIT-001", "a self-excluding commit intent permits exact object creation", "G001", {
  assert: { selected_rule: "G001", selected_action: "create_ledgered_commit_objects", post_action_counters: { values: { commit_objects: 1 } } },
});
target("SEC7-GIT-002", "injecting the intent's own commit OID is a material self-cycle transform", "G001", {
  fault: { kind: "replace", path: "source.commit_intent_relation", before: "valid_self_excluding", after: "invalid_self_including" },
  assert: { selected_rule: "G002", selected_reason: "GIT_COMMIT_INTENT_SELF_CYCLE" },
});
target("SEC7-GIT-003", "an invalid initial-ref relation cannot execute CAS", "G003", {
  fault: { kind: "replace", path: "source.ref_relation", before: "absent_initial", after: "other" },
  assert: { selected_rule: "DEFAULT", selected_action: "request_infrastructure_failure" },
});

function budgetControl(maximum) {
  const normalAdmission = durableRecord(`fixtures/SEC7-BUDGET-${maximum}/admissions/A0.json`, "normal_admission", { ordinal: "A0" });
  const records = [normalAdmission];
  records.push(durableRecord(`fixtures/SEC7-BUDGET-${maximum}/attempts/A0/start.json`, "attempt_start", { ordinal: "A0", admission_ordinal: "A0", admission_sha256: normalAdmission.sha256 }));
  for (let index = 1; index <= maximum; index += 1) {
    const admission = durableRecord(`fixtures/SEC7-BUDGET-${maximum}/admissions/A${index}.json`, "recovery_admission", { ordinal: `A${index}` });
    records.push(admission);
    records.push(durableRecord(`fixtures/SEC7-BUDGET-${maximum}/attempts/A${index}/start.json`, "attempt_start", { ordinal: `A${index}`, admission_ordinal: `A${index}`, admission_sha256: admission.sha256 }));
  }
  const source = completeSource(rules.find((rule) => rule.id === "E011"));
  source.approval_maximum_recovery_bootstraps = maximum;
  source.recovery_slots_consumed = maximum;
  return makeTransitionControl({
    id: `SEC7-BUDGET-${String(maximum).padStart(2, "0")}`, category: "attempt_budget_boundary",
    claim: `recovery maximum ${maximum} rejects after exactly ${1 + maximum} admissions and starts`,
    source_schema: "locked_entry_ineligible_v2", source, records, execute_action: false,
    assert: { selected_rule: "E011", source_counters: { values: { root_admissions: 1 + maximum, root_attempt_starts: 1 + maximum, recovery_slots: maximum } } },
  });
}

const targetedControls = targetedSpecs.map(makeTransitionControl);
const budgetControls = [0, 2, 32].map(budgetControl);

const capabilityDescriptor = {
  schema: "candidate_boundary_descriptor_v2",
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
  const id = `SEC7-CAP-${field.replaceAll("_", "-").toUpperCase()}`;
  const pre = { descriptor: clone(capabilityDescriptor) };
  const fault = { id, kind: "replace", path: `descriptor.${field}`, before: clone(capabilityDescriptor[field]), after: clone(invalidValue) };
  const { observed, mutations } = applyFault(pre, fault);
  const result = validateCapability(observed.descriptor);
  const fixture = { schema: "tt-supervised-capability-witness-v1", pre_descriptor: pre.descriptor, fault, fault_mutations: mutations, observed_descriptor: observed.descriptor, derived_result: result };
  if (result.valid) throw new Error(`${id}: invalid descriptor accepted`);
  return { id, category: "candidate_capability_denial", claim: `${field} mutation is denied before launch`, target_kind: "capability", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_capability_validator" };
}

const capabilityMutations = {
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
  capabilityControls.unshift({ id: "SEC7-CAP-VALID", category: "candidate_capability_positive", claim: "the exact closed candidate descriptor passes before launch", target_kind: "capability", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_closed_capability_validator" });
}

function computeResources(input) {
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

const resourceFixture = {
  attempts: [
    { id: "A0", bootstrap_observed: 13, bootstrap_cap: 20, meter_observed_preterminal: 7, meter_preterminal_cap: 10, meter_terminal_cap: 2, wall_cap: 40, io_charge: 11, disk_charge: 5 },
    { id: "A1", bootstrap_observed: null, bootstrap_cap: 17, meter_observed_preterminal: 11, meter_preterminal_cap: 15, meter_terminal_cap: 2, wall_cap: 45, io_charge: 13, disk_charge: 7 },
  ],
  memory_vertices: [{ id: "A0", capacity: 31 }, { id: "A1", capacity: 37 }, { id: "closure", capacity: 5 }],
  possible_overlap_edges: [["A0", "A1"], ["A1", "closure"]],
};

function resourceControl(id, claim, fault = { kind: "none" }) {
  const exact = computeResources(resourceFixture);
  const pre = { resources: clone(resourceFixture), claimed_result: clone(exact) };
  const applied = applyFault(pre, { id, ...fault });
  const preResult = computeResources(pre.resources);
  const observedResult = computeResources(applied.observed.resources);
  const claimValid = canonical(applied.observed.claimed_result) === canonical(observedResult);
  const fixture = {
    schema: "tt-supervised-resource-arithmetic-witness-v1",
    pre_input: pre.resources, pre_claimed_result: pre.claimed_result,
    fault, fault_mutations: applied.mutations,
    observed_input: applied.observed.resources,
    observed_claimed_result: applied.observed.claimed_result,
    pre_result: preResult, derived_result: observedResult,
    derived_validation: { valid: claimValid, reason: claimValid ? "RESOURCE_ARITHMETIC_EXACT" : "RESOURCE_ARITHMETIC_MISMATCH" },
  };
  return { id, category: "numeric_resource_arithmetic", claim, target_kind: "accounting", fixture, fixture_sha256: sha256(fixture), oracle_origin: "derived_by_numeric_resource_evaluator" };
}

const resourceControls = [
  resourceControl("SEC7-RESOURCE-001", "CPU, memory, wall, I/O, and disk are numerically derived"),
  resourceControl("SEC7-RESOURCE-002", "a changed terminal CPU cap changes the derived total", { kind: "replace", path: "resources.attempts.1.meter_terminal_cap", before: 2, after: 9 }),
  resourceControl("SEC7-RESOURCE-003", "removing a possible-overlap edge changes memory from summed component to serial maximum", { kind: "replace", path: "resources.possible_overlap_edges", before: [["A0", "A1"], ["A1", "closure"]], after: [] }),
  resourceControl("SEC7-RESOURCE-004", "an off-by-one CPU claim is rejected", { kind: "replace", path: "claimed_result.cpu", before: 52, after: 51 }),
  resourceControl("SEC7-RESOURCE-005", "a serial-maximum memory claim is rejected when overlap is unproved", { kind: "replace", path: "claimed_result.memory", before: 73, after: 37 }),
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
        const source = { ...sourceSchemas.e0_private_map_v2.fixed, run_mode: runMode, e0_mode: e0Mode, map_state: mapState, event, descriptor_state: mapState === "MAP_OPENED_UNRECEIPTED" || mapState === "MAP_OPENED_RECEIPT_DURABLE" ? "trusted_meter_only" : "absent" };
        const selected = selectRule("e0_private_map_v2", source);
        e0Manifest.push({ ordinal: ++e0Ordinal, run_mode: runMode, e0_mode: e0Mode, map_state: mapState, event, descriptor_state: source.descriptor_state, selected_rule: selected.id || selected.selected_rule, next_action: selected.next_action });
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

const allControls = [...ruleControls, ...targetedControls, ...budgetControls, ...capabilityControls, ...resourceControls];
const priorBundle = join(dirname(here), "tt-supervised-executor-v6-review-bundle");
const priorFiles = [
  "supervised-executor-contract-v6.md", "supervised-executor-topology-decision-v5.md",
  "supervised-executor-transition-matrix-v5.json", "supervised-executor-control-matrix-v5.json",
  "build_v6_design_artifacts.mjs", "verify_v6_design_artifacts.mjs",
];
const preservedV6Manifest = Object.fromEntries(priorFiles.map((name) => [name, sha256(readFileSync(join(priorBundle, name)))]));

const transition = {
  schema: "tt-supervised-executor-transition-matrix-v6", protocol,
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
  live_phase_protocol: { states: liveStates, events: liveEvents, edges: liveEdges, candidate_event_schema: "live_transition_candidate_v2", e0_event_schema: "live_transition_e0_evaluate_v2", e0_launch_requires_private_map_receipt: true },
  e0_private_map_protocol: { states: privateMapStates, events: privateMapEvents, event_projection_case_count: e0Manifest.length, event_projection_sha256: sha256(e0Manifest), closed_source_product_case_count: sourceSchemas.e0_private_map_v2.domain_cardinality, descriptor_state_is_separately_enumerated_in_symbolic_totality: true, closure_mode_all_events_forbidden: true, open_failure_outcome: "harness_failure_phase_terminal" },
  meter_finalization_protocol: { one_campaign_owned_record_per_write_action: true, terminal_last_campaign_owned_write: true, stages: meterReachableStages, crash_replay_from_every_stage: true },
  candidate_boundary_descriptor: capabilityDescriptor,
  accounting_policy: { formulas_executable: true, cpu: "sum observed else cap plus terminal cap", memory: "max connected possible-overlap component sum", wall: "sum attempt wall caps", io: "sum attempt charges", disk: "sum attempt charges" },
  totality: { symbolic_domain_cardinality: symbolicCaseCount, symbolic_partition_count: symbolicPartitions.length, symbolic_case_digest: sha256(symbolicSchemaManifests), schema_manifests: symbolicSchemaManifests, partitions: symbolicPartitions },
  preserved_v6_negative_evidence: preservedV6Manifest,
};

writeJson("supervised-executor-transition-matrix-v6.json", transition);
const transitionSha256 = sha256(readFileSync(join(here, "supervised-executor-transition-matrix-v6.json")));
const builderSha256 = sha256(readFileSync(fileURLToPath(import.meta.url)));

const control = {
  schema: "tt-supervised-executor-control-matrix-v6", protocol,
  status: ["HYPOTHESIS", "MODEL-BOUND", "UNTESTED", "ZERO-RUN"],
  artifact_freeze_authorized: false, code_implementation_authorized: false,
  control_execution_authorized: false, campaign_execution_authorized: false,
  source_transition_artifact: "supervised-executor-transition-matrix-v6.json",
  source_transition_artifact_sha256: transitionSha256,
  builder_artifact: "build_v7_design_artifacts.mjs", builder_artifact_sha256: builderSha256,
  witness_policy: {
    trusted_inherited_oracles: false,
    pre_state_complete: true, explicit_fault_transform_required: true,
    non_none_fault_must_materially_change_state: true, action_applied_by_reducer: true,
    post_state_derived: true, complete_durable_record_universe_required: true,
    counters_derived_from_record_bytes: true, numeric_resource_evaluator_required: true,
  },
  controls: allControls,
  static_control_count: allControls.length,
  rule_selection_control_count: ruleControls.length,
  targeted_transition_control_count: targetedControls.length,
  budget_boundary_control_count: budgetControls.length,
  capability_control_count: capabilityControls.length,
  resource_control_count: resourceControls.length,
  generated_suites: [
    { id: "SEC7-GENERATED-001", claim: "closed source products select one rule, schema rejection, or default", case_count: symbolicCaseCount, partition_count: symbolicPartitions.length, schema_manifests: symbolicSchemaManifests, manifest_sha256: sha256(symbolicSchemaManifests) },
    { id: "SEC7-GENERATED-002", claim: "complete E0 evaluate and closure event projection with canonical descriptor-state derivation; the full descriptor cross-product is in GENERATED-001", case_count: e0Manifest.length, closed_source_product_case_count: sourceSchemas.e0_private_map_v2.domain_cardinality, manifest: e0Manifest, manifest_sha256: sha256(e0Manifest) },
    { id: "SEC7-GENERATED-003", claim: "every reachable meter durable boundary has an idempotent selector", case_count: meterReachableStages.length, manifest: meterReachableStages, manifest_sha256: sha256(meterReachableStages) },
    { id: "SEC7-GENERATED-004", claim: "every denied capability field has a materialized negative transform", case_count: capabilityControls.length, manifest: capabilityControls.map((row) => ({ id: row.id, result: row.fixture.derived_result })), manifest_sha256: sha256(capabilityControls.map((row) => ({ id: row.id, result: row.fixture.derived_result }))) },
  ],
  preserved_v6_negative_evidence: preservedV6Manifest,
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

writeJson("supervised-executor-control-matrix-v6.json", control);
