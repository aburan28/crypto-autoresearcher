def exact_keys($expected):
  (keys | sort) == ($expected | sort);

def hex40:
  type == "string" and test("^[0-9a-f]{40}$");

def hex64:
  type == "string" and test("^[0-9a-f]{64}$");

def timestamp:
  type == "string" and
  test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$");

($receipt | length == 1) and
($seal | length == 1) and
($receipt[0]) as $r |
($seal[0]) as $s |

($r | exact_keys([
  "authorization_head",
  "classification",
  "cleanup_exit_code",
  "container_exit_code",
  "container_id",
  "container_name",
  "consumption_commit",
  "consumption_ref",
  "experiment_id",
  "finished_at_utc",
  "hashes",
  "host_elapsed_seconds",
  "oom_killed",
  "pipeline_wrapper_exit_code",
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
($r.consumption_commit | hex40) and
($r.started_at_utc | timestamp) and
($r.finished_at_utc | timestamp) and
($r.host_elapsed_seconds | type == "number" and . >= 0 and . == floor) and
($r.hashes | exact_keys([
  "authorization_validator_sha256",
  "container_runner_sha256",
  "docker_inspect_post_sha256",
  "docker_inspect_pre_sha256",
  "host_runner_sha256",
  "input_tar_sha256",
  "protocol_sha256",
  "resource_sha256",
  "result_validator_sha256",
  "source_sha256",
  "stderr_sha256",
  "stdout_sha256",
  "test_sha256"
])) and
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
($s.consumption_commit == $r.consumption_commit) and
($s.consumption_ref == $r.consumption_ref) and
($s.experiment_id == $r.experiment_id) and
($s.result_ref == $r.result_ref) and
($s.run_id == $r.run_id) and
($s.sealed_at_utc == $r.finished_at_utc) and

if $r.classification == "VALID_DEVELOPMENT_TEST" then
  ($r.container_id | hex64) and
  ($r.pipeline_wrapper_exit_code == 0) and
  ($r.container_exit_code == 0) and
  ($r.timeout_observed == false) and
  ($r.oom_killed == false) and
  ($r.cleanup_exit_code == 0)
else
  ($r.classification | IN(
    "TEST_FAILURE",
    "PREFLIGHT_FAILURE",
    "INFRASTRUCTURE_FAILURE",
    "INCOMPLETE_INFRASTRUCTURE_FAILURE",
    "TIMEOUT",
    "RESOURCE_EXHAUSTION"
  ))
end
