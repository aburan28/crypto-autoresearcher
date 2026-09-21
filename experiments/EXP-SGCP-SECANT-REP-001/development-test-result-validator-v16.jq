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
  "experiment_id",
  "finished_at_utc",
  "hashes",
  "oom_killed",
  "pipeline_status",
  "pipeline_wrapper_exit_code",
  "preseal_host_elapsed_seconds",
  "protocol_commit",
  "result_ref",
  "run_id",
  "started_at_utc",
  "timeout_observed"
])) and
($r.authorization_head == $expected.authorization_head) and
($r.protocol_commit == $expected.protocol_commit) and
($r.experiment_id == "EXP-SGCP-SECANT-REP-001") and
($r.run_id == $expected.run_id) and
($r.container_name == $expected.container_name) and
($r.consumption_ref == $expected.consumption_ref) and
($r.result_ref == $expected.result_ref) and
($r.consumption_commit == $expected.consumption_commit) and
($r.consumption_commit | hex40) and
($r.started_at_utc | timestamp) and
($r.finished_at_utc | timestamp) and
($r.preseal_host_elapsed_seconds |
  type == "number" and . >= 0 and . == floor) and
($r.cleanup_proved == true) and
($r.cleanup_exit_code == 0) and
($r.container_ever_owned | type == "boolean") and
(if $r.container_ever_owned then
   ($r.container_id | hex64)
 else
   ($r.container_id == "ABSENT")
 end) and
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
  "container_exit_code",
  "oom_killed",
  "pipeline_status",
  "pipeline_wrapper_exit_code",
  "timeout_observed",
  "timeout_observed_from_controller"
])) and
($r.cleanup_exit_code == $expected.causal_tuple.cleanup_exit_code) and
($r.container_exit_code == $expected.causal_tuple.container_exit_code) and
($r.oom_killed == $expected.causal_tuple.oom_killed) and
($r.pipeline_status == $expected.causal_tuple.pipeline_status) and
($r.pipeline_wrapper_exit_code ==
  $expected.causal_tuple.pipeline_wrapper_exit_code) and
($r.timeout_observed == $expected.causal_tuple.timeout_observed) and
($r.timeout_observed ==
  $expected.causal_tuple.timeout_observed_from_controller) and
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
([$r.hashes[]] |
  if $r.classification == "VALID_DEVELOPMENT_TEST" then
    all(hex64)
  else
    all(hex64 or . == "ABSENT")
  end
) and

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
  ($r.timeout_observed == false) and
  ($r.oom_killed == false) and
  ($r.cleanup_exit_code == 0)
elif $r.classification == "TEST_FAILURE" then
  ($r.pipeline_wrapper_exit_code == 1) and
  ($r.pipeline_status == [0, 0, 1]) and
  ($r.container_exit_code == 1) and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false)
elif $r.classification == "PREFLIGHT_FAILURE" then
  ($r.pipeline_wrapper_exit_code == 70) and
  ($r.pipeline_status == [0, 0, 70]) and
  ($r.container_exit_code == 70) and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false)
elif $r.classification == "TIMEOUT" then
  ($r.pipeline_wrapper_exit_code | . == 124 or . == 137) and
  ($r.timeout_observed == true) and
  ($r.oom_killed != true)
elif $r.classification == "RESOURCE_EXHAUSTION" then
  ($r.oom_killed == true)
elif $r.classification == "INFRASTRUCTURE_FAILURE" then
  ($r.timeout_observed != true) and
  ($r.oom_killed != true)
else
  false
end
