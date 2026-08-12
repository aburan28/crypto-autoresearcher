def exact_keys($expected):
  (keys | sort) == ($expected | sort);

def nonnegative_integer:
  type == "number" and . >= 0 and . == floor;

def runtime_ok:
  type == "object"
  and exact_keys([
    "cpu_stat",
    "memory_current_bytes",
    "memory_peak_bytes",
    "pids_current",
    "pids_peak"
  ])
  and (.cpu_stat | type == "object")
  and (.cpu_stat | exact_keys([
    "burst_usec",
    "nice_usec",
    "nr_bursts",
    "nr_periods",
    "nr_throttled",
    "system_usec",
    "throttled_usec",
    "usage_usec",
    "user_usec"
  ]))
  and ([.cpu_stat[]] | all(nonnegative_integer))
  and (.memory_current_bytes | nonnegative_integer)
  and (.memory_peak_bytes | nonnegative_integer)
  and (.pids_current | nonnegative_integer)
  and (.pids_peak | nonnegative_integer)
  and .memory_current_bytes <= 1073741824
  and .memory_peak_bytes <= 1073741824
  and .pids_current <= 64
  and .pids_peak <= 64;

def projection_ok($inspect; $expected; $oom_kill_disable):
  ($inspect | length == 1)
  and ($inspect[0].Id == $expected.container_id)
  and ($inspect[0].Name == ("/" + $expected.container_name))
  and ($inspect[0].Image == $expected.image_id)
  and ($inspect[0].Config.Hostname == $expected.container_id[0:12])
  and ($inspect[0].Config.Domainname == "")
  and ($inspect[0].Config.User == "65534:65534")
  and ($inspect[0].Config.Entrypoint == ["/bin/sh"])
  and ($inspect[0].Config.Cmd == [
    "-c",
    $expected.container_script,
    "sgcp-v23",
    $expected.container_runner_sha256,
    $expected.container_runner_path,
    $expected.source_path,
    $expected.test_path
  ])
  and ($inspect[0].Config.OpenStdin == true)
  and ($inspect[0].Config.AttachStdin == true)
  and ($inspect[0].Config.AttachStdout == true)
  and ($inspect[0].Config.AttachStderr == true)
  and ($inspect[0].Config.Tty == false)
  and ($inspect[0].Config.StdinOnce == true)
  and ($inspect[0].Config.StopTimeout == 1)
  and ($inspect[0].Config.ExposedPorts == null)
  and ($inspect[0].Config.Volumes == null)
  and ($inspect[0].Config.WorkingDir == "")
  and ($inspect[0].Config.NetworkDisabled == null)
  and ($inspect[0].Config.MacAddress == null)
  and ($inspect[0].Config.OnBuild == null)
  and ($inspect[0].Config.StopSignal == null)
  and ($inspect[0].Config.Shell == null)
  and (($inspect[0].Config.Env | length) == 9)
  and (($inspect[0].Config.Env | sort) == ([
    "HOME=/tmp",
    "LANG=C",
    "LC_ALL=C",
    "PYTHONHASHSEED=0",
    "PYTHONDONTWRITEBYTECODE=1",
    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
    "PYTHON_VERSION=3.11.15",
    "PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625"
  ] | sort))
  and ($inspect[0].Config.Healthcheck.Test == ["NONE"])
  and ($inspect[0].Config.Labels == {
    "org.crypto-autoresearcher.authorization":
      $expected.source_authorization_commit_sha1,
    "org.crypto-autoresearcher.consumption":
      $expected.source_consumption_commit_sha1
  })
  and ($inspect[0].HostConfig.Binds == null)
  and ($inspect[0].HostConfig.VolumesFrom == null)
  and ($inspect[0].HostConfig.LogConfig == {"Type":"none","Config":{}})
  and ($inspect[0].HostConfig.NetworkMode == "none")
  and ($inspect[0].HostConfig.RestartPolicy
       == {"Name":"no","MaximumRetryCount":0})
  and ($inspect[0].HostConfig.AutoRemove == false)
  and ($inspect[0].HostConfig.CapAdd == null)
  and ($inspect[0].HostConfig.CapDrop == ["ALL"])
  and ($inspect[0].HostConfig.CgroupnsMode == "private")
  and ($inspect[0].HostConfig.IpcMode == "private")
  and ($inspect[0].HostConfig.Runtime == "runc")
  and ($inspect[0].HostConfig.OomKillDisable == $oom_kill_disable)
  and ($inspect[0].HostConfig.Privileged == false)
  and ($inspect[0].HostConfig.PublishAllPorts == false)
  and ($inspect[0].HostConfig.PortBindings == {})
  and ($inspect[0].HostConfig.VolumeDriver == "")
  and ($inspect[0].HostConfig.GroupAdd == null)
  and ($inspect[0].HostConfig.CgroupParent == "")
  and ($inspect[0].HostConfig.Cgroup == "")
  and ($inspect[0].HostConfig.Dns == [])
  and ($inspect[0].HostConfig.DnsOptions == [])
  and ($inspect[0].HostConfig.DnsSearch == [])
  and ($inspect[0].HostConfig.ExtraHosts == null)
  and ($inspect[0].HostConfig.Links == null)
  and ($inspect[0].HostConfig.Init == null)
  and ($inspect[0].HostConfig.Sysctls == null)
  and ($inspect[0].HostConfig.StorageOpt == null)
  and ($inspect[0].HostConfig.PidMode == "")
  and ($inspect[0].HostConfig.UsernsMode == "")
  and ($inspect[0].HostConfig.Devices == [])
  and ($inspect[0].HostConfig.DeviceRequests == null)
  and ($inspect[0].HostConfig.ReadonlyRootfs == true)
  and ($inspect[0].HostConfig.SecurityOpt == ["no-new-privileges"])
  and ($inspect[0].HostConfig.Tmpfs
       == {"/tmp":"rw,noexec,nosuid,nodev,size=64m"})
  and ($inspect[0].HostConfig.ShmSize == 8388608)
  and ($inspect[0].HostConfig.Memory == 1073741824)
  and ($inspect[0].HostConfig.MemorySwap == 1073741824)
  and ($inspect[0].HostConfig.NanoCpus == 1000000000)
  and ($inspect[0].HostConfig.PidsLimit == 64)
  and ($inspect[0].HostConfig.Ulimits == [
    {"Name":"fsize","Hard":1048576,"Soft":1048576},
    {"Name":"nofile","Hard":128,"Soft":128}
  ])
  and ($inspect[0].HostConfig.MaskedPaths == [
    "/proc/acpi","/proc/asound","/proc/interrupts","/proc/kcore",
    "/proc/keys","/proc/latency_stats","/proc/sched_debug",
    "/proc/scsi","/proc/timer_list","/proc/timer_stats",
    "/sys/devices/virtual/powercap","/sys/firmware"
  ])
  and ($inspect[0].HostConfig.ReadonlyPaths == [
    "/proc/bus","/proc/fs","/proc/irq","/proc/sys",
    "/proc/sysrq-trigger"
  ])
  and ($inspect[0].Mounts == []);

def expected_test_ids:
  [
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_scalar_congruence_and_least_slope_selection",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_witnesses_fibers_representatives_diagnostics_and_ops",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_every_reachable_domain_error_and_charged_prefix",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_first_error_precedence",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_public_results_and_inputs_are_immutable"
  ];

($stdout | length == 1) and
($pre | length == 1) and
($post | length == 1) and
($source_consumption | length == 1) and
($seal | length == 1) and

($stdout[0]) as $out |
($pre[0]) as $pre_inspect |
($post[0]) as $post_inspect |
($source_consumption[0]) as $consume |
($seal[0]) as $s |

($out | type == "object") and
($out | exact_keys([
  "classification",
  "details",
  "errors",
  "events",
  "expected_failures",
  "failures",
  "runtime_after",
  "runtime_before",
  "skipped",
  "tests_started",
  "unexpected_successes"
])) and
($out.classification == "VALID_DEVELOPMENT_TEST") and
($out.details == []) and
($out.errors == 0) and
($out.expected_failures == 0) and
($out.failures == 0) and
($out.skipped == 0) and
($out.tests_started == 5) and
($out.unexpected_successes == 0) and
($out.runtime_before | runtime_ok) and
($out.runtime_after | runtime_ok) and
($out.events | map(.id) == expected_test_ids) and
($out.events | all(
  type == "object"
  and exact_keys(["id","outcome"])
  and .outcome == "ok"
)) and

projection_ok($pre_inspect; $expected; false) and
projection_ok($post_inspect; $expected; null) and
($pre_inspect[0].State.Status == "created") and
($pre_inspect[0].State.Running == false) and
($pre_inspect[0].State.OOMKilled == false) and
($pre_inspect[0].State.ExitCode == 0) and
($pre_inspect[0].State.StartedAt == "0001-01-01T00:00:00Z") and
($post_inspect[0].State.Status == "exited") and
($post_inspect[0].State.Running == false) and
($post_inspect[0].State.OOMKilled == false) and
($post_inspect[0].State.ExitCode == 0) and
($post_inspect[0].State.StartedAt
 | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T.*Z\\z")) and
($post_inspect[0].State.FinishedAt
 | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T.*Z\\z")) and

($consume == {
  "authorization_commit_sha1": $expected.source_authorization_commit_sha1,
  "experiment_id": $expected.experiment_id,
  "id": "CONSUME-SGCP-SECANT-DEVELOPMENT-TEST-V23",
  "maximum_runs_remaining": 0,
  "protocol_commit_sha1": $expected.source_protocol_commit_sha1,
  "run_id": $expected.source_run_id,
  "started_at_utc": $expected.source_started_at_utc,
  "status": "authorization_consumed_before_protected_execution"
}) and

($s | type == "object") and
($s | exact_keys([
  "classification",
  "cleanup_proved",
  "container_exit_code",
  "container_id",
  "current_absence_receipt_sha256",
  "evidence_status",
  "experiment_id",
  "id",
  "interpretation",
  "oom_killed",
  "operation_accounting",
  "pipeline_status",
  "post_inspect_normalization",
  "preprocessing_accounting",
  "recovered_at_utc",
  "recovery_authorization_commit_sha1",
  "recovery_consumption_commit_sha1",
  "recovery_protocol_commit_sha1",
  "source_authorization_commit_sha1",
  "source_consumption_commit_sha1",
  "source_manifest_sha256",
  "source_original_result_ref",
  "source_original_result_ref_absent",
  "source_protocol_commit_sha1",
  "source_run_id",
  "source_stdout_sha256",
  "target_scope",
  "test_ids",
  "tests_started",
  "timeout_observed"
])) and
($s.id == "RECOVERY-SEAL-SGCP-SECANT-V23-V25") and
($s.experiment_id == $expected.experiment_id) and
($s.classification == "RECOVERED_VALID_DEVELOPMENT_TEST") and
($s.evidence_status == "separate_recovery_seal_original_R_absent") and
($s.source_run_id == $expected.source_run_id) and
($s.source_protocol_commit_sha1 == $expected.source_protocol_commit_sha1) and
($s.source_authorization_commit_sha1
 == $expected.source_authorization_commit_sha1) and
($s.source_consumption_commit_sha1
 == $expected.source_consumption_commit_sha1) and
($s.source_original_result_ref == $expected.source_original_result_ref) and
($s.source_original_result_ref_absent == true) and
($s.source_manifest_sha256 == $expected.source_manifest_sha256) and
($s.source_stdout_sha256 == $expected.source_stdout_sha256) and
($s.tests_started == 5) and
($s.test_ids == expected_test_ids) and
($s.container_id == $expected.container_id) and
($s.container_exit_code == 0) and
($s.oom_killed == false) and
($s.timeout_observed == false) and
($s.pipeline_status == [0,0,0]) and
($s.cleanup_proved == true) and
($s.post_inspect_normalization == {
  "field": "HostConfig.OomKillDisable",
  "pre_start": false,
  "post_exit": null,
  "scope": "post_exit_representation_only"
}) and
($s.operation_accounting == {
  "group_operations": "not_applicable",
  "memory_bandwidth": "not_measured",
  "offline_field_operations": "not_applicable",
  "online_field_operations": "not_applicable"
}) and
($s.preprocessing_accounting == {
  "cryptanalytic_preprocessing": "not_applicable",
  "fixed_curve_advice_bytes": "not_applicable",
  "recovery_control_plane_work": "not_an_attack_cost_measurement",
  "recovery_fixed_overhead": "not_measured"
}) and
($s.target_scope == {
  "curve_structure": "not_applicable",
  "field_modulus": "not_applicable",
  "generator": "not_applicable",
  "probability_claim": "none",
  "supported_ecdlp_targets": 0,
  "test_methods": 5,
  "trials": 1
}) and
($s.recovery_protocol_commit_sha1 == $expected.recovery_protocol_commit_sha1) and
($s.recovery_authorization_commit_sha1
 == $expected.recovery_authorization_commit_sha1) and
($s.recovery_consumption_commit_sha1
 == $expected.recovery_consumption_commit_sha1) and
($s.current_absence_receipt_sha256
 == $expected.current_absence_receipt_sha256) and
($s.recovered_at_utc == $expected.recovered_at_utc) and
($s.recovered_at_utc
 | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\\z")) and
($s.interpretation == $expected.interpretation)
