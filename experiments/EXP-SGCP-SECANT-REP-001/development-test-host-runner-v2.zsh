#!/bin/zsh

set -u
umask 077

readonly MODE="${1-}"
readonly AUTH_HEAD="${2-}"
readonly REPO="/Volumes/Volume/crypto-autoresearcher-worktrees/recursive-s3-quotient-001"
readonly EXP="experiments/EXP-SGCP-SECANT-REP-001"
readonly RUN_ID="DEV-SGCP-SECANT-PURE-CORE-V2"
readonly RUN_DIR="${REPO}/${EXP}/${RUN_ID}"
readonly BASE_COMMIT="1ed6a17e4deffd88e5c07c8788aa18fb1f0d3407"
readonly PROTOCOL_PATH="${EXP}/development-test-execution-protocol-v2.json"
readonly HOST_RUNNER_PATH="${EXP}/development-test-host-runner-v2.zsh"
readonly CONTAINER_RUNNER_PATH="${EXP}/development-test-container-runner-v2.py"
readonly SOURCE_PATH="${EXP}/src/sgcp_secant_math_core.py"
readonly TEST_PATH="${EXP}/tests/test_sgcp_secant_math_core.py"
readonly DECISION_PATH="${EXP}/development-test-decision-v2.json"
readonly THEORY_PATH="${EXP}/development-test-theory-review-v2.json"
readonly ACCOUNTING_PATH="${EXP}/development-test-accounting-review-v2.json"
readonly RED_TEAM_PATH="${EXP}/development-test-red-team-review-v2.json"
readonly IMAGE="python@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly IMAGE_ID="sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly CONTAINER_NAME="dev-sgcp-secant-pure-core-v2"
readonly EXPECTED_SOURCE_SHA256="8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd"
readonly EXPECTED_TEST_SHA256="2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a"


sha256_file() {
  if [[ ! -f "$1" ]]; then
    /usr/bin/printf 'ABSENT'
    return 0
  fi
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}


verify_tool() {
  local path="$1"
  local expected="$2"
  [[ "$(sha256_file "$path")" == "$expected" ]]
}


write_receipt() {
  local classification="$1"
  local wrapper_status="$2"
  local finished_at
  local docker_status="ABSENT"
  local timeout_observed="false"
  local oom_killed="unknown"

  finished_at=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')
  [[ -f "${RUN_DIR}/docker-exit-code.txt" ]] &&
    docker_status="$(<"${RUN_DIR}/docker-exit-code.txt")"
  [[ -f "${RUN_DIR}/timeout-observed.txt" ]] &&
    timeout_observed="$(<"${RUN_DIR}/timeout-observed.txt")"
  [[ -f "${RUN_DIR}/oom-killed.txt" ]] &&
    oom_killed="$(<"${RUN_DIR}/oom-killed.txt")"

  /usr/bin/printf '%s\n' "$finished_at" >"${RUN_DIR}/finished-at-utc.txt"
  /usr/bin/printf '%s\n' "$classification" >"${RUN_DIR}/classification.txt"
  /usr/bin/printf '%s\n' "$wrapper_status" >"${RUN_DIR}/worker-wrapper-exit-code.txt"
  {
    /usr/bin/printf 'run_id=%s\n' "$RUN_ID"
    /usr/bin/printf 'authorization_head=%s\n' "$AUTH_HEAD"
    /usr/bin/printf 'started_at_utc=%s\n' "$(<"${RUN_DIR}/started-at-utc.txt")"
    /usr/bin/printf 'finished_at_utc=%s\n' "$finished_at"
    /usr/bin/printf 'classification=%s\n' "$classification"
    /usr/bin/printf 'worker_wrapper_exit_code=%s\n' "$wrapper_status"
    /usr/bin/printf 'docker_exit_code=%s\n' "$docker_status"
    /usr/bin/printf 'timeout_observed=%s\n' "$timeout_observed"
    /usr/bin/printf 'oom_killed=%s\n' "$oom_killed"
    /usr/bin/printf 'source_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/container-input/sgcp_secant_math_core.py")"
    /usr/bin/printf 'test_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/container-input/test_sgcp_secant_math_core.py")"
    /usr/bin/printf 'container_runner_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/container-input/runner.py")"
    /usr/bin/printf 'stdout_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/stdout.jsonl")"
    /usr/bin/printf 'stderr_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/stderr.log")"
    /usr/bin/printf 'resource_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/resource.txt")"
    /usr/bin/printf 'docker_inspect_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/docker-inspect.json")"
  } >"${RUN_DIR}/run-receipt.txt"
}


materialize_commit_path() {
  local commit="$1"
  local source_path="$2"
  local target_path="$3"
  /usr/bin/git -C "$REPO" show "${commit}:${source_path}" >"$target_path"
}


worker_fail() {
  /usr/bin/printf '%s\n' "$1" >"${RUN_DIR}/classification.txt"
  /usr/bin/printf '%s\n' "$2" >>"${RUN_DIR}/preflight.log"
  return "$3"
}


worker_main() {
  local protocol_commit
  local observed_head
  local observed_topology
  local -a topology_words
  local protocol_topology
  local protocol_delta
  local authorization_delta
  local observed_image_id
  local observed_image_platform
  local observed_docker_client
  local observed_docker_server
  local protocol_hash
  local host_runner_hash
  local container_runner_hash
  local source_hash
  local test_hash
  local decision_protocol_hash
  local docker_status
  local timeout_observed="false"
  local inspect_oom="unknown"

  cd "$REPO" || return 71
  : >"${RUN_DIR}/preflight.log"

  observed_head=$(/usr/bin/git rev-parse HEAD) ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot resolve HEAD" 70; return $?; }
  [[ "$observed_head" == "$AUTH_HEAD" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "HEAD changed before worker" 70; return $?; }

  observed_topology=$(/usr/bin/git rev-list --parents -n 1 "$AUTH_HEAD") ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot resolve authorization topology" 70; return $?; }
  topology_words=(${(z)observed_topology})
  [[ "${topology_words[1]-}" == "$AUTH_HEAD" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "authorization commit identity mismatch" 70; return $?; }
  [[ "${#topology_words}" -eq 2 ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "authorization commit is not single-parent" 70; return $?; }
  protocol_commit="${topology_words[2]}"

  protocol_topology=$(/usr/bin/git rev-list --parents -n 1 "$protocol_commit") ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot resolve protocol topology" 70; return $?; }
  [[ "$protocol_topology" == "${protocol_commit} ${BASE_COMMIT}" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "protocol commit parent mismatch" 70; return $?; }

  protocol_delta=$(/usr/bin/git diff-tree --no-commit-id --name-status -r "$protocol_commit") ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot resolve protocol delta" 70; return $?; }
  [[ "$protocol_delta" == $'A\t'"${CONTAINER_RUNNER_PATH}"$'\nA\t'"${PROTOCOL_PATH}"$'\nA\t'"${HOST_RUNNER_PATH}" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "protocol delta mismatch" 70; return $?; }

  authorization_delta=$(/usr/bin/git diff-tree --no-commit-id --name-status -r "$AUTH_HEAD") ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot resolve authorization delta" 70; return $?; }
  [[ "$authorization_delta" == $'A\t'"${ACCOUNTING_PATH}"$'\nA\t'"${DECISION_PATH}"$'\nA\t'"${RED_TEAM_PATH}"$'\nA\t'"${THEORY_PATH}" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "authorization delta mismatch" 70; return $?; }

  verify_tool /usr/bin/env \
    6e8b85a2efe5bf44ad11302f2b7b7e8c6b2f2c94f9bf117f5d4654b79bf85271 &&
    verify_tool /usr/bin/git \
      44a68ddc1983d6cff3fd35ba3f9ba5f82004216f1dcde69892b3d1b06e408698 &&
    verify_tool /bin/zsh \
      528da649cc69510bd3c0bc565298cb602076b74a8ac3f18e793211b2a3c725e8 &&
    verify_tool /bin/mkdir \
      eb3b48e064031c5491bcb9a99bbf44753c9ee074d10c69d114cb4cbc236ca02c &&
    verify_tool /bin/date \
      28f40376c23f2d4f8bd58eb27c9aa86c25a51fe949f12dab1bc0254f906aa9f6 &&
    verify_tool /usr/bin/printf \
      f2a76beee50f16a1193244519ecfad592b3af0623276b41c088c0ef8650c05f7 &&
    verify_tool /usr/bin/time \
      e3671328199c5cfc1554f51b6eb887ab568c543c88f44e94e00448ccf002ea4a &&
    verify_tool /opt/homebrew/bin/gtimeout \
      c0572ac780194a47daa9af4a6a8ec17f355c79fa30e852c1d58206119f8fcdd3 &&
    verify_tool /usr/bin/shasum \
      0812595f981a26f813d98dc380af14d4af427626c9339eda29eb849ae13de1e3 &&
    verify_tool /usr/bin/awk \
      3868b14602a4851218210ae1b08732fbdee703ac2c1e2d1898272b42fd33151a &&
    verify_tool /bin/chmod \
      ce1db41c1e8a607749097ec27fd59e1edf92db9008689242936e1fa3758cae1a &&
    verify_tool /opt/homebrew/bin/jq \
      e0a718e60bd1098fc134b354da3821a96d4a7510a15465ff64669b04349fc37c &&
    verify_tool /opt/homebrew/bin/docker \
      5ceb5704cfdf26acc8ff5e47727e58b4360bb6ecc825642de04121e61cf44c06 &&
    verify_tool /usr/bin/grep \
      e9e8aa8089241c6dcb8fa744d0dd4a7eabd3b1dae657cc824946d17e3dc457e8 &&
    verify_tool /usr/bin/find \
      05aa84ee15d95122cfa3de6a132ace019eb78b27da57534b5d555719c8380f7b ||
    { worker_fail "PREFLIGHT_FAILURE" "host tool digest mismatch" 70; return $?; }

  /bin/mkdir "${RUN_DIR}/evidence-input" "${RUN_DIR}/container-input" ||
    { worker_fail "INFRASTRUCTURE_FAILURE" "cannot create input directories" 71; return $?; }

  materialize_commit_path "$AUTH_HEAD" "$PROTOCOL_PATH" \
    "${RUN_DIR}/evidence-input/protocol.json" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize protocol" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$DECISION_PATH" \
    "${RUN_DIR}/evidence-input/decision.json" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize decision" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$THEORY_PATH" \
    "${RUN_DIR}/evidence-input/theory.json" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize theory receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$ACCOUNTING_PATH" \
    "${RUN_DIR}/evidence-input/accounting.json" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize accounting receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$RED_TEAM_PATH" \
    "${RUN_DIR}/evidence-input/red-team.json" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize red-team receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$CONTAINER_RUNNER_PATH" \
    "${RUN_DIR}/container-input/runner.py" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize container runner" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$SOURCE_PATH" \
    "${RUN_DIR}/container-input/sgcp_secant_math_core.py" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize protected source" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$TEST_PATH" \
    "${RUN_DIR}/container-input/test_sgcp_secant_math_core.py" ||
    { worker_fail "PREFLIGHT_FAILURE" "cannot materialize test source" 70; return $?; }

  /bin/chmod 0444 "${RUN_DIR}"/evidence-input/* "${RUN_DIR}"/container-input/* ||
    { worker_fail "INFRASTRUCTURE_FAILURE" "cannot make inputs read-only" 71; return $?; }
  /bin/chmod 0555 "${RUN_DIR}/evidence-input" "${RUN_DIR}/container-input" ||
    { worker_fail "INFRASTRUCTURE_FAILURE" "cannot make input directories read-only" 71; return $?; }

  protocol_hash="$(sha256_file "${RUN_DIR}/evidence-input/protocol.json")"
  host_runner_hash="$(sha256_file "${RUN_DIR}/host-runner.zsh")"
  container_runner_hash="$(sha256_file "${RUN_DIR}/container-input/runner.py")"
  source_hash="$(sha256_file "${RUN_DIR}/container-input/sgcp_secant_math_core.py")"
  test_hash="$(sha256_file "${RUN_DIR}/container-input/test_sgcp_secant_math_core.py")"
  decision_protocol_hash=$(
    /opt/homebrew/bin/jq -er '.execution_protocol_sha256' \
      "${RUN_DIR}/evidence-input/decision.json"
  ) || { worker_fail "PREFLIGHT_FAILURE" "decision protocol hash missing" 70; return $?; }

  [[ "$protocol_hash" == "$decision_protocol_hash" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "decision protocol hash mismatch" 70; return $?; }
  [[ "$source_hash" == "$EXPECTED_SOURCE_SHA256" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "protected source hash mismatch" 70; return $?; }
  [[ "$test_hash" == "$EXPECTED_TEST_SHA256" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "test source hash mismatch" 70; return $?; }

  /opt/homebrew/bin/jq -e \
    --arg protocol_commit "$protocol_commit" \
    --arg protocol_hash "$protocol_hash" \
    --arg host_hash "$host_runner_hash" \
    --arg container_hash "$container_runner_hash" \
    --arg source_hash "$source_hash" \
    --arg test_hash "$test_hash" \
    --arg image "$IMAGE" \
    '
      .status == "approved_for_one_development_test" and
      .maximum_runs == 1 and
      .protocol_commit_sha1 == $protocol_commit and
      .execution_protocol_sha256 == $protocol_hash and
      .host_runner_sha256 == $host_hash and
      .container_runner_sha256 == $container_hash and
      .protected_source_sha256 == $source_hash and
      .test_source_sha256 == $test_hash and
      .container_image == $image and
      (.review_receipt_sha256 | keys == ["accounting","red_team","theory"])
    ' "${RUN_DIR}/evidence-input/decision.json" >/dev/null ||
    { worker_fail "PREFLIGHT_FAILURE" "decision semantic gate failed" 70; return $?; }

  local role
  local receipt_file
  local receipt_hash
  for role in theory accounting red_team; do
    case "$role" in
      theory) receipt_file="${RUN_DIR}/evidence-input/theory.json" ;;
      accounting) receipt_file="${RUN_DIR}/evidence-input/accounting.json" ;;
      red_team) receipt_file="${RUN_DIR}/evidence-input/red-team.json" ;;
    esac
    receipt_hash="$(sha256_file "$receipt_file")"
    [[ "$receipt_hash" == "$(
      /opt/homebrew/bin/jq -er --arg role "$role" \
        '.review_receipt_sha256[$role]' \
        "${RUN_DIR}/evidence-input/decision.json"
    )" ]] ||
      { worker_fail "PREFLIGHT_FAILURE" "${role} receipt hash mismatch" 70; return $?; }
    /opt/homebrew/bin/jq -e \
      --arg role "$role" \
      --arg protocol_commit "$protocol_commit" \
      --arg protocol_hash "$protocol_hash" \
      --arg host_hash "$host_runner_hash" \
      --arg container_hash "$container_runner_hash" \
      --arg source_hash "$source_hash" \
      --arg test_hash "$test_hash" \
      '
        .role == $role and
        .verdict == "GO" and
        .observed_head_sha1 == $protocol_commit and
        .execution_protocol_sha256 == $protocol_hash and
        .host_runner_sha256 == $host_hash and
        .container_runner_sha256 == $container_hash and
        .protected_source_sha256 == $source_hash and
        .test_source_sha256 == $test_hash and
        .findings == []
      ' "$receipt_file" >/dev/null ||
      { worker_fail "PREFLIGHT_FAILURE" "${role} receipt semantic gate failed" 70; return $?; }
  done

  [[ "$(
    /opt/homebrew/bin/jq -r \
      '[.reviewer_principal_id] | length' \
      "${RUN_DIR}/evidence-input/theory.json"
  )" == "1" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "theory principal missing" 70; return $?; }
  [[ "$(
    /opt/homebrew/bin/jq -sr \
      'map(.reviewer_principal_id) | unique | length' \
      "${RUN_DIR}/evidence-input/theory.json" \
      "${RUN_DIR}/evidence-input/accounting.json" \
      "${RUN_DIR}/evidence-input/red-team.json"
  )" == "3" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "reviewer principals are not distinct" 70; return $?; }

  observed_image_id=$(
    /opt/homebrew/bin/docker image inspect "$IMAGE" --format '{{.Id}}'
  ) || { worker_fail "PREFLIGHT_FAILURE" "container image unavailable" 70; return $?; }
  [[ "$observed_image_id" == "$IMAGE_ID" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "container image ID mismatch" 70; return $?; }
  observed_image_platform=$(
    /opt/homebrew/bin/docker image inspect "$IMAGE" --format '{{.Os}}/{{.Architecture}}'
  ) || { worker_fail "PREFLIGHT_FAILURE" "container platform unavailable" 70; return $?; }
  [[ "$observed_image_platform" == "linux/arm64" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "container platform mismatch" 70; return $?; }
  observed_docker_client=$(
    /opt/homebrew/bin/docker version --format '{{.Client.Version}}'
  ) || { worker_fail "PREFLIGHT_FAILURE" "Docker client version unavailable" 70; return $?; }
  observed_docker_server=$(
    /opt/homebrew/bin/docker version --format '{{.Server.Version}}'
  ) || { worker_fail "PREFLIGHT_FAILURE" "Docker server version unavailable" 70; return $?; }
  [[ "$observed_docker_client" == "28.5.1" &&
    "$observed_docker_server" == "29.4.3" ]] ||
    { worker_fail "PREFLIGHT_FAILURE" "Docker version mismatch" 70; return $?; }
  if /opt/homebrew/bin/docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    worker_fail "PREFLIGHT_FAILURE" "reserved container name already exists" 70
    return $?
  fi

  /usr/bin/printf '%s\n' "$AUTH_HEAD" >"${RUN_DIR}/authorization-head.txt"
  /usr/bin/printf '%s\n' "$protocol_commit" >"${RUN_DIR}/protocol-commit.txt"
  /usr/bin/printf '%s\n' "$protocol_hash" >"${RUN_DIR}/protocol-sha256.txt"
  /usr/bin/printf '%s\n' "$host_runner_hash" >"${RUN_DIR}/host-runner-sha256.txt"
  /usr/bin/printf '%s\n' "$container_runner_hash" \
    >"${RUN_DIR}/container-runner-sha256.txt"
  /usr/bin/printf '%s\n' "$source_hash" >"${RUN_DIR}/source-sha256.txt"
  /usr/bin/printf '%s\n' "$test_hash" >"${RUN_DIR}/test-sha256.txt"
  /usr/bin/printf '%s\n' "$observed_image_id" >"${RUN_DIR}/container-image-id.txt"

  /opt/homebrew/bin/gtimeout --verbose --signal=TERM --kill-after=5s 180s \
    /opt/homebrew/bin/docker run \
      --name "$CONTAINER_NAME" \
      --pull never \
      --platform linux/arm64 \
      --network none \
      --memory 1g \
      --memory-swap 1g \
      --cpus 1 \
      --pids-limit 64 \
      --ulimit nofile=128:128 \
      --ulimit fsize=1048576:1048576 \
      --read-only \
      --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
      --cap-drop ALL \
      --security-opt no-new-privileges \
      --user 65534:65534 \
      --env HOME=/tmp \
      --env LANG=C \
      --env LC_ALL=C \
      --env PYTHONHASHSEED=0 \
      --label "org.crypto-autoresearcher.authorization=${AUTH_HEAD}" \
      --mount "type=bind,source=${RUN_DIR}/container-input,target=/input,readonly" \
      --entrypoint /usr/local/bin/python3 \
      "$IMAGE" \
      -I -S -P -B /input/runner.py \
      /input/sgcp_secant_math_core.py \
      /input/test_sgcp_secant_math_core.py \
      >"${RUN_DIR}/stdout.jsonl" 2>"${RUN_DIR}/stderr.log"
  docker_status=$?
  /usr/bin/printf '%s\n' "$docker_status" >"${RUN_DIR}/docker-exit-code.txt"

  if [[ "$docker_status" -eq 124 || "$docker_status" -eq 137 ]] &&
    /usr/bin/grep -q 'sending signal' "${RUN_DIR}/stderr.log"; then
    timeout_observed="true"
  fi
  /usr/bin/printf '%s\n' "$timeout_observed" >"${RUN_DIR}/timeout-observed.txt"

  if /opt/homebrew/bin/docker container inspect "$CONTAINER_NAME" \
    >"${RUN_DIR}/docker-inspect.json" 2>"${RUN_DIR}/docker-inspect-error.log"; then
    inspect_oom=$(
      /opt/homebrew/bin/jq -r '.[] | .State.OOMKilled' \
        "${RUN_DIR}/docker-inspect.json"
    )
  fi
  /usr/bin/printf '%s\n' "$inspect_oom" >"${RUN_DIR}/oom-killed.txt"

  /opt/homebrew/bin/docker container rm -f "$CONTAINER_NAME" \
    >"${RUN_DIR}/docker-cleanup.log" 2>&1
  /usr/bin/printf '%s\n' "$?" >"${RUN_DIR}/docker-cleanup-exit-code.txt"

  if [[ -e "${REPO}/${EXP}/._${RUN_ID}" ]] ||
    /usr/bin/find "$RUN_DIR" \
      \( -name '._*' -o -name '__pycache__' -o -name '*.pyc' -o -name '*.pyo' \) \
      -print | /usr/bin/grep -q .; then
    /usr/bin/printf '%s\n' "INFRASTRUCTURE_FAILURE" >"${RUN_DIR}/classification.txt"
    /usr/bin/printf '%s\n' "forbidden sidecar or Python cache appeared" \
      >>"${RUN_DIR}/preflight.log"
    return 71
  fi

  if [[ "$timeout_observed" == "true" ]]; then
    /usr/bin/printf '%s\n' "TIMEOUT" >"${RUN_DIR}/classification.txt"
    return 124
  fi
  if [[ "$inspect_oom" == "true" ]]; then
    /usr/bin/printf '%s\n' "RESOURCE_EXHAUSTION" >"${RUN_DIR}/classification.txt"
    return 137
  fi

  if [[ "$docker_status" -eq 0 ]] &&
    /opt/homebrew/bin/jq -e \
      '
        .classification == "VALID_DEVELOPMENT_TEST" and
        .tests_started == 5 and
        .failures == 0 and
        .errors == 0 and
        .skipped == 0 and
        .expected_failures == 0 and
        .unexpected_successes == 0 and
        (.events | length == 5) and
        ([.events[].outcome] | all(. == "ok")) and
        ([.events[].id] == [
          "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_scalar_congruence_and_least_slope_selection",
          "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_witnesses_fibers_representatives_diagnostics_and_ops",
          "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_every_reachable_domain_error_and_charged_prefix",
          "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_first_error_precedence",
          "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_public_results_and_inputs_are_immutable"
        ])
      ' "${RUN_DIR}/stdout.jsonl" >/dev/null &&
    [[ ! -s "${RUN_DIR}/stderr.log" ]]; then
    /usr/bin/printf '%s\n' "VALID_DEVELOPMENT_TEST" >"${RUN_DIR}/classification.txt"
    return 0
  fi

  if [[ "$docker_status" -eq 1 ]] &&
    /opt/homebrew/bin/jq -e \
      '.classification == "TEST_FAILURE" and .tests_started == 5' \
      "${RUN_DIR}/stdout.jsonl" >/dev/null 2>&1; then
    /usr/bin/printf '%s\n' "TEST_FAILURE" >"${RUN_DIR}/classification.txt"
    return 1
  fi

  if [[ "$docker_status" -eq 70 ]] &&
    /opt/homebrew/bin/jq -e '.classification == "PREFLIGHT_FAILURE"' \
      "${RUN_DIR}/stdout.jsonl" >/dev/null 2>&1; then
    /usr/bin/printf '%s\n' "PREFLIGHT_FAILURE" >"${RUN_DIR}/classification.txt"
    return 70
  fi

  /usr/bin/printf '%s\n' "INFRASTRUCTURE_FAILURE" >"${RUN_DIR}/classification.txt"
  return 71
}


launch_main() {
  local started_at
  local wrapper_status
  local classification

  [[ -n "$AUTH_HEAD" ]] || return 72
  cd "$REPO" || return 72
  /bin/mkdir "$RUN_DIR" || return 73
  started_at=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')
  /usr/bin/printf '%s\n' "$started_at" >"${RUN_DIR}/started-at-utc.txt"
  /usr/bin/printf '%s\n' "INFRASTRUCTURE_FAILURE" >"${RUN_DIR}/classification.txt"

  materialize_commit_path "$AUTH_HEAD" "$HOST_RUNNER_PATH" \
    "${RUN_DIR}/host-runner.zsh" || {
      write_receipt "PREFLIGHT_FAILURE" 70
      return 70
    }
  /bin/chmod 0444 "${RUN_DIR}/host-runner.zsh" || {
    write_receipt "INFRASTRUCTURE_FAILURE" 71
    return 71
  }

  /usr/bin/time -lp -o "${RUN_DIR}/resource.txt" \
    /opt/homebrew/bin/gtimeout --verbose --signal=TERM --kill-after=10s 240s \
      /bin/zsh -f "${RUN_DIR}/host-runner.zsh" worker "$AUTH_HEAD" \
      >"${RUN_DIR}/worker-wrapper-stdout.log" \
      2>"${RUN_DIR}/worker-wrapper-stderr.log"
  wrapper_status=$?

  if [[ "$wrapper_status" -eq 124 || "$wrapper_status" -eq 137 ]] &&
    /usr/bin/grep -q 'sending signal' "${RUN_DIR}/worker-wrapper-stderr.log"; then
    /usr/bin/printf '%s\n' "true" >"${RUN_DIR}/timeout-observed.txt"
    /usr/bin/printf '%s\n' "TIMEOUT" >"${RUN_DIR}/classification.txt"
    if /opt/homebrew/bin/docker container inspect "$CONTAINER_NAME" \
      >"${RUN_DIR}/docker-inspect.json" 2>"${RUN_DIR}/docker-inspect-error.log"; then
      /opt/homebrew/bin/docker container rm -f "$CONTAINER_NAME" \
        >"${RUN_DIR}/docker-cleanup.log" 2>&1
      /usr/bin/printf '%s\n' "$?" >"${RUN_DIR}/docker-cleanup-exit-code.txt"
    fi
  fi

  classification="$(<"${RUN_DIR}/classification.txt")"
  write_receipt "$classification" "$wrapper_status"

  case "$classification" in
    VALID_DEVELOPMENT_TEST) return 0 ;;
    TEST_FAILURE) return 1 ;;
    PREFLIGHT_FAILURE) return 70 ;;
    INFRASTRUCTURE_FAILURE) return 71 ;;
    TIMEOUT) return 124 ;;
    RESOURCE_EXHAUSTION) return 137 ;;
    *) return 71 ;;
  esac
}


case "$MODE" in
  launch)
    launch_main
    exit $?
    ;;
  worker)
    worker_main
    exit $?
    ;;
  *)
    exit 72
    ;;
esac
