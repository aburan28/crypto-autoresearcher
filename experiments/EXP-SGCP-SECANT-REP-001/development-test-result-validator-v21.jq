def exact_keys($expected):
  (keys | sort) == ($expected | sort);

def hex40:
  type == "string" and length == 40 and test("^[0-9a-f]{40}\\z");

def hex64:
  type == "string" and length == 64 and test("^[0-9a-f]{64}\\z");

def timestamp:
  type == "string" and
  length == 20 and
  test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\\z");

def uint:
  type == "number" and . >= 0 and . == floor;

def nonnegative_number:
  type == "number" and . >= 0;

($receipt | length == 1) and
($seal | length == 1) and
($receipt[0]) as $r |
($seal[0]) as $s |

($r | exact_keys([
  "authorization_head",
  "classification",
  "cleanup_exit_code",
  "cleanup_proved",
  "container_exit_code",
  "container_ever_owned",
  "container_id",
  "container_name",
  "consumption_commit",
  "consumption_ref",
  "evidence_stage",
  "experiment_id",
  "finished_at_utc",
  "hashes",
  "oom_killed",
  "operation_accounting",
  "pipeline_status",
  "pipeline_wrapper_exit_code",
  "preseal_host_elapsed_seconds",
  "protocol_commit",
  "result_ref",
  "resource_usage",
  "run_id",
  "started_at_utc",
  "target_scope",
  "timeout_observed"
])) and
($r.authorization_head == $expected.authorization_head) and
($r.protocol_commit == $expected.protocol_commit) and
($r.experiment_id == "EXP-SGCP-SECANT-REP-001") and
($r.run_id == $expected.run_id) and
($r.container_name == $expected.container_name) and
($r.consumption_ref == $expected.consumption_ref) and
($r.result_ref == $expected.result_ref) and
($r.evidence_stage == $expected.causal_tuple.evidence_stage) and
($r.consumption_commit == $expected.consumption_commit) and
($r.consumption_commit | hex40) and
($r.started_at_utc | timestamp) and
($r.finished_at_utc | timestamp) and
($r.preseal_host_elapsed_seconds |
  type == "number" and . >= 0 and . == floor) and
($r.cleanup_proved == true) and
($r.cleanup_exit_code == 0) and
($r.container_ever_owned == true) and
($r.container_id | hex64) and
($r.pipeline_wrapper_exit_code |
  . == null or (type == "number" and . >= 0 and . == floor)) and
($r.container_exit_code |
  . == null or (type == "number" and . >= 0 and . == floor)) and
($r.timeout_observed | . == null or type == "boolean") and
($r.oom_killed | . == null or type == "boolean") and
($r.pipeline_status |
  . == null or
  (type == "array" and length == 3 and
   all(type == "number" and . >= 0 and . == floor))) and
($expected.causal_tuple | exact_keys([
  "cleanup_exit_code",
  "cleanup_proved_from_artifacts",
  "container_exit_code",
  "container_exit_code_from_inspect",
  "container_state_status_from_inspect",
  "evidence_stage",
  "oom_killed",
  "oom_killed_from_inspect",
  "pipeline_status",
  "pipeline_wrapper_exit_code",
  "timeout_observed",
  "timeout_observed_from_controller"
])) and
($r.cleanup_exit_code == $expected.causal_tuple.cleanup_exit_code) and
($r.cleanup_proved ==
  $expected.causal_tuple.cleanup_proved_from_artifacts) and
($r.container_exit_code == $expected.causal_tuple.container_exit_code) and
($r.container_exit_code ==
  $expected.causal_tuple.container_exit_code_from_inspect) and
($r.oom_killed == $expected.causal_tuple.oom_killed) and
($r.oom_killed == $expected.causal_tuple.oom_killed_from_inspect) and
($r.pipeline_status == $expected.causal_tuple.pipeline_status) and
($r.pipeline_wrapper_exit_code ==
  $expected.causal_tuple.pipeline_wrapper_exit_code) and
($r.timeout_observed == $expected.causal_tuple.timeout_observed) and
($r.timeout_observed ==
  $expected.causal_tuple.timeout_observed_from_controller) and
($expected.causal_tuple.container_state_status_from_inspect |
  type == "string" and length > 0) and
($r.evidence_stage |
  . == "POST_RUN_INSPECTED_PIPELINE_COMPLETE" or
  . == "POST_RUN_INSPECTED_PIPELINE_INCOMPLETE") and
($r.hashes | exact_keys([
  "authorization_validator_sha256",
  "container_runner_sha256",
  "container_state_exit_code_sha256",
  "docker_cleanup_exit_code_sha256",
  "docker_inspect_post_sha256",
  "docker_inspect_pre_sha256",
  "fixed_overhead_write_plan_sha256",
  "host_runner_sha256",
  "input_tar_sha256",
  "oom_killed_sha256",
  "pipeline_status_sha256",
  "pipeline_wrapper_exit_code_sha256",
  "protocol_sha256",
  "resource_sha256",
  "result_validator_sha256",
  "source_sha256",
  "stderr_sha256",
  "stdout_sha256",
  "test_sha256",
  "timeout_controller_sha256",
  "timeout_observed_sha256"
])) and
($r.hashes == $expected.hashes) and
($r.operation_accounting == {
  group_operations: "not_applicable",
  memory_bandwidth_bytes: "not_measured",
  offline_field_operations: "not_applicable",
  online_field_operations: "not_applicable",
  reason:
    "fixed_public_unit_test_control_without_relation_generation_or_ecdlp_solver"
}) and
($r.target_scope == {
  curve_structure: "not_applicable",
  ecdlp_targets_supported: 0,
  field_modulus_structure: "not_applicable",
  generator_fixed: "not_applicable",
  probabilistic_status: "not_claimed",
  public_test_method_count: 5,
  success_probability_claim: "not_applicable",
  supported_target_domain: "fixed_public_unit_test_methods_only",
  trial_count: 1
}) and
($r.resource_usage | exact_keys([
  "average_shared_memory_size_raw",
  "average_unshared_data_size_raw",
  "average_unshared_stack_size_raw",
  "block_input_operations",
  "block_output_operations",
  "command_terminated_abnormally",
  "cycles_elapsed",
  "instructions_retired",
  "involuntary_context_switches",
  "maximum_resident_set_size_raw",
  "messages_received",
  "messages_sent",
  "page_faults",
  "page_reclaims",
  "peak_memory_footprint_raw",
  "real_seconds",
  "schema",
  "signals_received",
  "swaps",
  "system_seconds",
  "user_seconds",
  "voluntary_context_switches"
])) and
($r.resource_usage.schema == "macos_usr_bin_time_lp_v1") and
($r.resource_usage.command_terminated_abnormally | type == "boolean") and
($r.resource_usage.real_seconds | nonnegative_number) and
($r.resource_usage.user_seconds | nonnegative_number) and
($r.resource_usage.system_seconds | nonnegative_number) and
([
  $r.resource_usage.average_shared_memory_size_raw,
  $r.resource_usage.average_unshared_data_size_raw,
  $r.resource_usage.average_unshared_stack_size_raw,
  $r.resource_usage.block_input_operations,
  $r.resource_usage.block_output_operations,
  $r.resource_usage.cycles_elapsed,
  $r.resource_usage.instructions_retired,
  $r.resource_usage.involuntary_context_switches,
  $r.resource_usage.maximum_resident_set_size_raw,
  $r.resource_usage.messages_received,
  $r.resource_usage.messages_sent,
  $r.resource_usage.page_faults,
  $r.resource_usage.page_reclaims,
  $r.resource_usage.peak_memory_footprint_raw,
  $r.resource_usage.signals_received,
  $r.resource_usage.swaps,
  $r.resource_usage.voluntary_context_switches
] | all(uint)) and
($expected.resource_usage == $r.resource_usage) and
(if $r.evidence_stage == "POST_RUN_INSPECTED_PIPELINE_COMPLETE" then
   ($r.pipeline_status |
     type == "array" and length == 3 and
     all(type == "number" and . >= 0 and . == floor)) and
   ([$r.hashes[]] | all(hex64))
 elif $r.evidence_stage == "POST_RUN_INSPECTED_PIPELINE_INCOMPLETE" then
   ($r.pipeline_status == null) and
   ($r.hashes.pipeline_status_sha256 == "ABSENT") and
   ($r.hashes | to_entries |
     map(select(.key != "pipeline_status_sha256") | .value) |
     all(hex64))
 else false
 end) and

($s | exact_keys([
  "artifact_count",
  "artifact_manifest_sha256",
  "authorization_head",
  "classification",
  "consumption_commit",
  "consumption_ref",
  "experiment_id",
  "result_ref",
  "run_id",
  "run_receipt_sha256",
  "sealed_at_utc"
])) and
($s.artifact_count == $expected.artifact_count) and
($s.artifact_count | type == "number" and . > 0 and . == floor) and
($s.artifact_manifest_sha256 == $expected.artifact_manifest_sha256) and
($s.artifact_manifest_sha256 | hex64) and
($s.run_receipt_sha256 == $expected.run_receipt_sha256) and
($s.run_receipt_sha256 | hex64) and
($s.authorization_head == $r.authorization_head) and
($s.classification == $r.classification) and
($s.consumption_commit == $expected.consumption_commit) and
($s.consumption_commit == $r.consumption_commit) and
($s.consumption_ref == $r.consumption_ref) and
($s.experiment_id == $r.experiment_id) and
($s.result_ref == $r.result_ref) and
($s.run_id == $r.run_id) and
($s.sealed_at_utc == $r.finished_at_utc) and

if $r.classification == "VALID_DEVELOPMENT_TEST" then
  ($r.container_id | hex64) and
  ($r.pipeline_wrapper_exit_code == 0) and
  ($r.pipeline_status == [0, 0, 0]) and
  ($r.container_exit_code == 0) and
  ($expected.causal_tuple.container_state_status_from_inspect == "exited") and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false) and
  ($r.cleanup_exit_code == 0)
elif $r.classification == "TEST_FAILURE" then
  ($r.pipeline_wrapper_exit_code == 1) and
  ($r.pipeline_status == [0, 0, 1]) and
  ($r.container_exit_code == 1) and
  ($expected.causal_tuple.container_state_status_from_inspect == "exited") and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false)
elif $r.classification == "PREFLIGHT_FAILURE" then
  ($r.pipeline_wrapper_exit_code == 70) and
  ($r.pipeline_status == [0, 0, 70]) and
  ($r.container_exit_code == 70) and
  ($expected.causal_tuple.container_state_status_from_inspect == "exited") and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false)
elif $r.classification == "TIMEOUT" then
  ($r.pipeline_wrapper_exit_code | . == 124 or . == 137) and
  ($r.timeout_observed == true) and
  ($r.oom_killed != true)
elif $r.classification == "RESOURCE_EXHAUSTION" then
  ($r.oom_killed == true) and
  ($expected.causal_tuple.container_state_status_from_inspect == "exited")
elif $r.classification == "INFRASTRUCTURE_FAILURE" then
  ($r.timeout_observed != true) and
  ($r.oom_killed != true)
else
  false
end
