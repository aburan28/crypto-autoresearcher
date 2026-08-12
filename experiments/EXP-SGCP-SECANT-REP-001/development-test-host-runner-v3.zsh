#!/bin/zsh

set -u
setopt pipefail
umask 077

readonly MODE="${1-}"
readonly AUTH_HEAD="${2-}"
readonly PROTOCOL_COMMIT_ARG="${3-}"
readonly PROTOCOL_SHA256_ARG="${4-}"
readonly HOST_RUNNER_SHA256_ARG="${5-}"
readonly AUTH_VALIDATOR_SHA256_ARG="${6-}"
readonly CONTAINER_RUNNER_SHA256_ARG="${7-}"

readonly REPO="/Volumes/Volume/crypto-autoresearcher-worktrees/recursive-s3-quotient-001"
readonly BRANCH_REF="refs/heads/codex/recursive-s3-quotient-001"
readonly EXP="experiments/EXP-SGCP-SECANT-REP-001"
readonly RUN_ID="DEV-SGCP-SECANT-PURE-CORE-V3"
readonly RUN_DIR="${REPO}/${EXP}/${RUN_ID}"
readonly BASE_COMMIT="c2048512ae6d151e532eff41bfd13de5a77316da"
readonly BASE_TREE="cb542cec707c0b9c81da02ef67c341a859dab3f0"
readonly PROTOCOL_PATH="${EXP}/development-test-execution-protocol-v3.json"
readonly HOST_RUNNER_PATH="${EXP}/development-test-host-runner-v3.zsh"
readonly AUTH_VALIDATOR_PATH="${EXP}/development-test-authorization-validator-v3.jq"
readonly CONTAINER_RUNNER_PATH="${EXP}/development-test-container-runner-v3.py"
readonly SOURCE_PATH="${EXP}/src/sgcp_secant_math_core.py"
readonly TEST_PATH="${EXP}/tests/test_sgcp_secant_math_core.py"
readonly DECISION_PATH="${EXP}/development-test-decision-v3.json"
readonly THEORY_PATH="${EXP}/development-test-theory-review-v3.json"
readonly ACCOUNTING_PATH="${EXP}/development-test-accounting-review-v3.json"
readonly RED_TEAM_PATH="${EXP}/development-test-red-team-review-v3.json"
readonly CONSUMPTION_MARKER_PATH="${EXP}/development-test-consumption-v3.json"
readonly IMAGE="python@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly IMAGE_ID="sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly EXPECTED_SOURCE_SHA256="8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd"
readonly EXPECTED_TEST_SHA256="2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a"

typeset -g CLASSIFICATION="INFRASTRUCTURE_FAILURE"
typeset -g CONSUMPTION_COMMIT="ABSENT"
typeset -g CONTAINER_ID="ABSENT"
typeset -g INITIALIZED="false"
typeset -g STARTED_AT="ABSENT"


sha256_file() {
  if [[ ! -f "$1" ]]; then
    /usr/bin/printf 'ABSENT'
    return 0
  fi
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}


sha256_commit_path() {
  local commit="$1"
  local path="$2"
  GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" show "${commit}:${path}" |
    /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}'
}


verify_tool() {
  [[ "$(sha256_file "$1")" == "$2" ]]
}


raw_delta_signature() {
  GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" \
    diff-tree --raw --no-abbrev --no-commit-id -r "$1" |
    /usr/bin/awk '{print $1, $2, $5, $6}'
}


materialize_commit_path() {
  GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" \
    show "${1}:${2}" >"$3"
}


record_failure() {
  CLASSIFICATION="$1"
  /usr/bin/printf '%s\n' "$2" >>"${RUN_DIR}/preflight.log"
  return "$3"
}


inventory_to_file() {
  local phase="$1"
  local sidecar_file="${RUN_DIR}/${phase}-sidecars.txt"
  local cache_file="${RUN_DIR}/${phase}-caches.txt"

  /usr/bin/find "${REPO}/${EXP}" -name '._*' -print >"$sidecar_file" ||
    return 1
  /usr/bin/find "${REPO}/${EXP}" \
    \( -type d -name '__pycache__' -o -type f \
       \( -name '*.pyc' -o -name '*.pyo' \) \) \
    -print >"$cache_file" || return 1
  [[ ! -s "$sidecar_file" && ! -s "$cache_file" ]]
}


write_receipt() {
  local status="$1"
  local finished_at
  local docker_exit="ABSENT"
  local timeout_observed="false"
  local oom_killed="unknown"
  local cleanup_exit="ABSENT"

  finished_at=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')
  [[ -f "${RUN_DIR}/docker-exit-code.txt" ]] &&
    docker_exit="$(<"${RUN_DIR}/docker-exit-code.txt")"
  [[ -f "${RUN_DIR}/timeout-observed.txt" ]] &&
    timeout_observed="$(<"${RUN_DIR}/timeout-observed.txt")"
  [[ -f "${RUN_DIR}/oom-killed.txt" ]] &&
    oom_killed="$(<"${RUN_DIR}/oom-killed.txt")"
  [[ -f "${RUN_DIR}/docker-cleanup-exit-code.txt" ]] &&
    cleanup_exit="$(<"${RUN_DIR}/docker-cleanup-exit-code.txt")"

  /usr/bin/printf '%s\n' "$finished_at" >"${RUN_DIR}/finished-at-utc.txt"
  /usr/bin/printf '%s\n' "$status" >"${RUN_DIR}/classification.txt"
  {
    /usr/bin/printf 'run_id=%s\n' "$RUN_ID"
    /usr/bin/printf 'authorization_head=%s\n' "$AUTH_HEAD"
    /usr/bin/printf 'protocol_commit=%s\n' "$PROTOCOL_COMMIT_ARG"
    /usr/bin/printf 'consumption_commit=%s\n' "$CONSUMPTION_COMMIT"
    /usr/bin/printf 'container_id=%s\n' "$CONTAINER_ID"
    /usr/bin/printf 'started_at_utc=%s\n' "$STARTED_AT"
    /usr/bin/printf 'finished_at_utc=%s\n' "$finished_at"
    /usr/bin/printf 'classification=%s\n' "$status"
    /usr/bin/printf 'docker_exit_code=%s\n' "$docker_exit"
    /usr/bin/printf 'timeout_observed=%s\n' "$timeout_observed"
    /usr/bin/printf 'oom_killed=%s\n' "$oom_killed"
    /usr/bin/printf 'docker_cleanup_exit_code=%s\n' "$cleanup_exit"
    /usr/bin/printf 'protocol_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/evidence-input/protocol.json")"
    /usr/bin/printf 'authorization_validator_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/evidence-input/authorization-validator.jq")"
    /usr/bin/printf 'container_runner_sha256=%s\n' \
      "$CONTAINER_RUNNER_SHA256_ARG"
    /usr/bin/printf 'source_sha256=%s\n' "$EXPECTED_SOURCE_SHA256"
    /usr/bin/printf 'test_sha256=%s\n' "$EXPECTED_TEST_SHA256"
    /usr/bin/printf 'input_tar_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/input.tar")"
    /usr/bin/printf 'stdout_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/stdout.json")"
    /usr/bin/printf 'stderr_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/stderr.log")"
    /usr/bin/printf 'resource_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/resource.txt")"
    /usr/bin/printf 'docker_inspect_pre_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/docker-inspect-pre.json")"
    /usr/bin/printf 'docker_inspect_post_sha256=%s\n' \
      "$(sha256_file "${RUN_DIR}/docker-inspect-post.json")"
  } >"${RUN_DIR}/run-receipt.txt"
}


preclaim_main() {
  local current_head
  local current_branch
  local status_output
  local replace_output
  local graft_path
  local protocol_topology
  local authorization_topology
  local protocol_tree
  local host_hash
  local validator_hash
  local container_hash
  local source_hash
  local test_hash
  local image_id
  local image_platform
  local docker_client
  local docker_server

  [[ "$MODE" == "launch" ]] || return 72
  [[ -n "$AUTH_HEAD" && -n "$PROTOCOL_COMMIT_ARG" &&
    -n "$PROTOCOL_SHA256_ARG" && -n "$HOST_RUNNER_SHA256_ARG" &&
    -n "$AUTH_VALIDATOR_SHA256_ARG" && -n "$CONTAINER_RUNNER_SHA256_ARG" ]] ||
    return 72
  cd "$REPO" || return 72

  current_head=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git rev-parse HEAD
  ) || return 72
  [[ "$current_head" == "$AUTH_HEAD" ]] || return 72
  current_branch=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git symbolic-ref -q HEAD
  ) || return 72
  [[ "$current_branch" == "$BRANCH_REF" ]] || return 72
  status_output=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git status --porcelain --untracked-files=all
  ) || return 72
  [[ -z "$status_output" ]] || return 72

  replace_output=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git replace -l
  ) || return 72
  [[ -z "$replace_output" ]] || return 72
  graft_path=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git rev-parse --git-path info/grafts
  ) || return 72
  [[ ! -e "$graft_path" ]] || return 72

  protocol_topology=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git rev-list --parents -n 1 \
      "$PROTOCOL_COMMIT_ARG"
  ) || return 72
  [[ "$protocol_topology" ==
    "${PROTOCOL_COMMIT_ARG} ${BASE_COMMIT}" ]] || return 72
  authorization_topology=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git rev-list --parents -n 1 "$AUTH_HEAD"
  ) || return 72
  [[ "$authorization_topology" ==
    "${AUTH_HEAD} ${PROTOCOL_COMMIT_ARG}" ]] || return 72

  [[ "$(raw_delta_signature "$PROTOCOL_COMMIT_ARG")" ==
    ":000000 100644 A ${AUTH_VALIDATOR_PATH}"$'\n'\
":000000 100644 A ${CONTAINER_RUNNER_PATH}"$'\n'\
":000000 100644 A ${PROTOCOL_PATH}"$'\n'\
":000000 100644 A ${HOST_RUNNER_PATH}" ]] || return 72
  [[ "$(raw_delta_signature "$AUTH_HEAD")" ==
    ":000000 100644 A ${ACCOUNTING_PATH}"$'\n'\
":000000 100644 A ${DECISION_PATH}"$'\n'\
":000000 100644 A ${RED_TEAM_PATH}"$'\n'\
":000000 100644 A ${THEORY_PATH}" ]] || return 72

  protocol_tree=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git rev-parse \
      "${PROTOCOL_COMMIT_ARG}^{tree}"
  ) || return 72
  [[ -n "$protocol_tree" ]] || return 72
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$PROTOCOL_PATH")" ==
    "$PROTOCOL_SHA256_ARG" ]] || return 72
  host_hash="$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$HOST_RUNNER_PATH")" ||
    return 72
  validator_hash="$(
    sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$AUTH_VALIDATOR_PATH"
  )" || return 72
  container_hash="$(
    sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$CONTAINER_RUNNER_PATH"
  )" || return 72
  source_hash="$(sha256_commit_path "$AUTH_HEAD" "$SOURCE_PATH")" || return 72
  test_hash="$(sha256_commit_path "$AUTH_HEAD" "$TEST_PATH")" || return 72
  [[ "$host_hash" == "$HOST_RUNNER_SHA256_ARG" ]] || return 72
  [[ "$validator_hash" == "$AUTH_VALIDATOR_SHA256_ARG" ]] || return 72
  [[ "$container_hash" == "$CONTAINER_RUNNER_SHA256_ARG" ]] || return 72
  [[ "$source_hash" == "$EXPECTED_SOURCE_SHA256" ]] || return 72
  [[ "$test_hash" == "$EXPECTED_TEST_SHA256" ]] || return 72

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
      05aa84ee15d95122cfa3de6a132ace019eb78b27da57534b5d555719c8380f7b &&
    verify_tool /usr/bin/tee \
      d284dd54c2e98bd7da539085105bf50a5455eb467c5aaf382413bc0b9b02a226 &&
    verify_tool /usr/bin/cmp \
      bf0111a82ee28deeb99a83eaee6f0829a743e09dcf8193ebd49b4c4190ad2457 &&
    verify_tool /usr/bin/wc \
      32f22e2b385cbc5250c5cc9a11465f5afa74c024724040f47d9edb71ce429e1a ||
    return 72

  [[ ! -e "$RUN_DIR" && ! -L "$RUN_DIR" ]] || return 73
  [[ ! -e "${REPO}/${CONSUMPTION_MARKER_PATH}" &&
    ! -L "${REPO}/${CONSUMPTION_MARKER_PATH}" ]] || return 73
  [[ ! -e "${REPO}/${EXP}/._${RUN_ID}" ]] || return 73
  [[ -z "$(
    /usr/bin/find "${REPO}/${EXP}" -name '._*' -print
  )" ]] || return 73
  [[ -z "$(
    /usr/bin/find "${REPO}/${EXP}" \
      \( -type d -name '__pycache__' -o -type f \
         \( -name '*.pyc' -o -name '*.pyo' \) \) -print
  )" ]] || return 73
  [[ ! -e "${REPO}/._experiments" &&
    ! -e "${REPO}/experiments/._EXP-SGCP-SECANT-REP-001" &&
    ! -e "/Volumes/Volume/crypto-autoresearcher-worktrees/._recursive-s3-quotient-001" ]] ||
    return 73

  image_id=$(
    /opt/homebrew/bin/docker image inspect "$IMAGE" --format '{{.Id}}'
  ) || return 72
  image_platform=$(
    /opt/homebrew/bin/docker image inspect "$IMAGE" \
      --format '{{.Os}}/{{.Architecture}}'
  ) || return 72
  docker_client=$(
    /opt/homebrew/bin/docker version --format '{{.Client.Version}}'
  ) || return 72
  docker_server=$(
    /opt/homebrew/bin/docker version --format '{{.Server.Version}}'
  ) || return 72
  [[ "$image_id" == "$IMAGE_ID" && "$image_platform" == "linux/arm64" &&
    "$docker_client" == "28.5.1" && "$docker_server" == "29.4.3" ]] ||
    return 72
  /bin/zsh -f -c 'ulimit -f 4096; [[ "$(ulimit -f)" == "4096" ]]' ||
    return 72

  /bin/mkdir "$RUN_DIR" || return 73
  INITIALIZED="true"
  STARTED_AT=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')
  /usr/bin/printf '%s\n' "$STARTED_AT" >"${RUN_DIR}/started-at-utc.txt"
  : >"${RUN_DIR}/preflight.log"
  return 0
}


validate_authorization() {
  local protocol_tree
  local theory_hash
  local accounting_hash
  local red_team_hash
  local expected_json

  /bin/mkdir "${RUN_DIR}/evidence-input" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot create evidence input" 71; return $?; }

  materialize_commit_path "$AUTH_HEAD" "$PROTOCOL_PATH" \
    "${RUN_DIR}/evidence-input/protocol.json" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize protocol" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$DECISION_PATH" \
    "${RUN_DIR}/evidence-input/decision.json" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize decision" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$THEORY_PATH" \
    "${RUN_DIR}/evidence-input/theory.json" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize theory receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$ACCOUNTING_PATH" \
    "${RUN_DIR}/evidence-input/accounting.json" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize accounting receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$RED_TEAM_PATH" \
    "${RUN_DIR}/evidence-input/red-team.json" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize red-team receipt" 70; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$AUTH_VALIDATOR_PATH" \
    "${RUN_DIR}/evidence-input/authorization-validator.jq" ||
    { record_failure "PREFLIGHT_FAILURE" "cannot materialize authorization validator" 70; return $?; }

  /bin/chmod 0444 "${RUN_DIR}"/evidence-input/* ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot make evidence read-only" 71; return $?; }
  /bin/chmod 0555 "${RUN_DIR}/evidence-input" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot seal evidence directory" 71; return $?; }

  [[ "$(sha256_file "${RUN_DIR}/evidence-input/protocol.json")" ==
    "$PROTOCOL_SHA256_ARG" ]] ||
    { record_failure "PREFLIGHT_FAILURE" "protocol digest mismatch" 70; return $?; }
  [[ "$(sha256_file "${RUN_DIR}/evidence-input/authorization-validator.jq")" ==
    "$AUTH_VALIDATOR_SHA256_ARG" ]] ||
    { record_failure "PREFLIGHT_FAILURE" "validator digest mismatch" 70; return $?; }

  protocol_tree=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" \
      rev-parse "${PROTOCOL_COMMIT_ARG}^{tree}"
  ) || { record_failure "PREFLIGHT_FAILURE" "cannot resolve protocol tree" 70; return $?; }
  theory_hash="$(sha256_file "${RUN_DIR}/evidence-input/theory.json")"
  accounting_hash="$(sha256_file "${RUN_DIR}/evidence-input/accounting.json")"
  red_team_hash="$(sha256_file "${RUN_DIR}/evidence-input/red-team.json")"

  expected_json=$(
    /opt/homebrew/bin/jq -cn \
      --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
      --arg protocol_tree_sha1 "$protocol_tree" \
      --arg base_commit_sha1 "$BASE_COMMIT" \
      --arg base_tree_sha1 "$BASE_TREE" \
      --arg protocol_sha256 "$PROTOCOL_SHA256_ARG" \
      --arg host_runner_sha256 "$HOST_RUNNER_SHA256_ARG" \
      --arg authorization_validator_sha256 "$AUTH_VALIDATOR_SHA256_ARG" \
      --arg container_runner_sha256 "$CONTAINER_RUNNER_SHA256_ARG" \
      --arg protected_source_sha256 "$EXPECTED_SOURCE_SHA256" \
      --arg test_source_sha256 "$EXPECTED_TEST_SHA256" \
      --arg container_image "$IMAGE" \
      --arg container_image_id "$IMAGE_ID" \
      '{
        protocol_commit_sha1: $protocol_commit_sha1,
        protocol_tree_sha1: $protocol_tree_sha1,
        base_commit_sha1: $base_commit_sha1,
        base_tree_sha1: $base_tree_sha1,
        protocol_sha256: $protocol_sha256,
        host_runner_sha256: $host_runner_sha256,
        authorization_validator_sha256: $authorization_validator_sha256,
        container_runner_sha256: $container_runner_sha256,
        protected_source_sha256: $protected_source_sha256,
        test_source_sha256: $test_source_sha256,
        container_image: $container_image,
        container_image_id: $container_image_id
      }'
  ) || { record_failure "INFRASTRUCTURE_FAILURE" "cannot build expected authorization" 71; return $?; }

  /opt/homebrew/bin/jq -e -n \
    --argjson expected "$expected_json" \
    --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
    --arg protocol_tree_sha1 "$protocol_tree" \
    --arg base_commit_sha1 "$BASE_COMMIT" \
    --arg base_tree_sha1 "$BASE_TREE" \
    --arg protocol_sha256 "$PROTOCOL_SHA256_ARG" \
    --arg host_runner_sha256 "$HOST_RUNNER_SHA256_ARG" \
    --arg authorization_validator_sha256 "$AUTH_VALIDATOR_SHA256_ARG" \
    --arg container_runner_sha256 "$CONTAINER_RUNNER_SHA256_ARG" \
    --arg protected_source_sha256 "$EXPECTED_SOURCE_SHA256" \
    --arg test_source_sha256 "$EXPECTED_TEST_SHA256" \
    --arg container_image "$IMAGE" \
    --arg container_image_id "$IMAGE_ID" \
    --arg theory_receipt_sha256 "$theory_hash" \
    --arg accounting_receipt_sha256 "$accounting_hash" \
    --arg red_team_receipt_sha256 "$red_team_hash" \
    --slurpfile protocol "${RUN_DIR}/evidence-input/protocol.json" \
    --slurpfile decision "${RUN_DIR}/evidence-input/decision.json" \
    --slurpfile theory "${RUN_DIR}/evidence-input/theory.json" \
    --slurpfile accounting "${RUN_DIR}/evidence-input/accounting.json" \
    --slurpfile red_team "${RUN_DIR}/evidence-input/red-team.json" \
    -f "${RUN_DIR}/evidence-input/authorization-validator.jq" \
    >"${RUN_DIR}/authorization-validation.txt" ||
    { record_failure "PREFLIGHT_FAILURE" "authorization validator rejected package" 70; return $?; }
  [[ "$(<"${RUN_DIR}/authorization-validation.txt")" == "true" ]] ||
    { record_failure "PREFLIGHT_FAILURE" "authorization validator did not emit true" 70; return $?; }
  return 0
}


commit_consumption_marker() {
  local marker_sha
  local marker_topology
  local marker_delta
  local status_output

  /opt/homebrew/bin/jq -cn \
    --arg id "CONSUME-SGCP-SECANT-DEVELOPMENT-TEST-V3" \
    --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
    --arg run_id "$RUN_ID" \
    --arg authorization_commit_sha1 "$AUTH_HEAD" \
    --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
    --arg started_at_utc "$STARTED_AT" \
    '{
      id: $id,
      experiment_id: $experiment_id,
      run_id: $run_id,
      authorization_commit_sha1: $authorization_commit_sha1,
      protocol_commit_sha1: $protocol_commit_sha1,
      started_at_utc: $started_at_utc,
      status: "authorization_consumed_before_protected_execution",
      maximum_runs_remaining: 0
    }' >"${REPO}/${CONSUMPTION_MARKER_PATH}" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot write consumption marker" 71; return $?; }
  /bin/chmod 0644 "${REPO}/${CONSUMPTION_MARKER_PATH}" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot set marker mode" 71; return $?; }
  marker_sha="$(sha256_file "${REPO}/${CONSUMPTION_MARKER_PATH}")"
  /usr/bin/printf '%s\n' "$marker_sha" >"${RUN_DIR}/consumption-marker-sha256.txt"

  GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" add -- \
    "$CONSUMPTION_MARKER_PATH" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot stage consumption marker" 71; return $?; }
  GIT_AUTHOR_NAME="Codex Research Coordinator" \
  GIT_AUTHOR_EMAIL="codex@localhost" \
  GIT_COMMITTER_NAME="Codex Research Coordinator" \
  GIT_COMMITTER_EMAIL="codex@localhost" \
  GIT_NO_REPLACE_OBJECTS=1 \
    /usr/bin/git -C "$REPO" \
      -c core.hooksPath=/dev/null \
      -c commit.gpgSign=false \
      commit --no-verify --no-gpg-sign \
      -m "research: consume SGCP development test v3" \
      -- "$CONSUMPTION_MARKER_PATH" \
      >"${RUN_DIR}/consumption-commit-stdout.log" \
      2>"${RUN_DIR}/consumption-commit-stderr.log" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot commit consumption marker" 71; return $?; }

  CONSUMPTION_COMMIT=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" rev-parse HEAD
  ) || { record_failure "INFRASTRUCTURE_FAILURE" "cannot resolve consumption commit" 71; return $?; }
  marker_topology=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" \
      rev-list --parents -n 1 "$CONSUMPTION_COMMIT"
  ) || { record_failure "INFRASTRUCTURE_FAILURE" "cannot resolve marker topology" 71; return $?; }
  [[ "$marker_topology" == "${CONSUMPTION_COMMIT} ${AUTH_HEAD}" ]] ||
    { record_failure "INFRASTRUCTURE_FAILURE" "consumption topology mismatch" 71; return $?; }
  marker_delta="$(raw_delta_signature "$CONSUMPTION_COMMIT")" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot resolve marker delta" 71; return $?; }
  [[ "$marker_delta" ==
    ":000000 100644 A ${CONSUMPTION_MARKER_PATH}" ]] ||
    { record_failure "INFRASTRUCTURE_FAILURE" "consumption delta mismatch" 71; return $?; }
  [[ "$(sha256_commit_path "$CONSUMPTION_COMMIT" "$CONSUMPTION_MARKER_PATH")" ==
    "$marker_sha" ]] ||
    { record_failure "INFRASTRUCTURE_FAILURE" "committed marker digest mismatch" 71; return $?; }

  status_output=$(
    GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C "$REPO" \
      status --porcelain --untracked-files=normal
  ) || { record_failure "INFRASTRUCTURE_FAILURE" "cannot inspect post-marker status" 71; return $?; }
  [[ "$status_output" == "?? ${EXP}/${RUN_ID}/" ]] ||
    { record_failure "INFRASTRUCTURE_FAILURE" "unexpected post-marker worktree state" 71; return $?; }
  /usr/bin/printf '%s\n' "$CONSUMPTION_COMMIT" \
    >"${RUN_DIR}/consumption-commit.txt"
  return 0
}


validate_container_inspect() {
  local inspect_path="$1"

  /opt/homebrew/bin/jq -e \
    --arg cid "$CONTAINER_ID" \
    --arg image_id "$IMAGE_ID" \
    --arg consumption_commit "$CONSUMPTION_COMMIT" \
    --arg authorization_head "$AUTH_HEAD" \
    '
      length == 1 and
      .[0].Id == $cid and
      .[0].Image == $image_id and
      .[0].Config.User == "65534:65534" and
      .[0].Config.Image ==
        "python@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0" and
      .[0].Config.Entrypoint == ["/bin/sh"] and
      .[0].Config.OpenStdin == true and
      .[0].Config.AttachStdin == true and
      .[0].Config.AttachStdout == true and
      .[0].Config.AttachStderr == true and
      .[0].Config.Tty == false and
      .[0].Config.StdinOnce == true and
      .[0].Config.StopTimeout == 1 and
      .[0].Config.Env == [
        "HOME=/tmp",
        "LANG=C",
        "LC_ALL=C",
        "PYTHONHASHSEED=0",
        "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
        "PYTHON_VERSION=3.11.15",
        "PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625"
      ] and
      .[0].Config.Healthcheck.Test == ["NONE"] and
      .[0].Config.Labels["org.crypto-autoresearcher.authorization"] ==
        $authorization_head and
      .[0].Config.Labels["org.crypto-autoresearcher.consumption"] ==
        $consumption_commit and
      .[0].Config.WorkingDir == "" and
      .[0].Config.Volumes == null and
      .[0].HostConfig.Binds == null and
      .[0].HostConfig.VolumesFrom == null and
      .[0].HostConfig.LogConfig == {"Type":"none","Config":{}} and
      .[0].HostConfig.NetworkMode == "none" and
      .[0].HostConfig.RestartPolicy == {"Name":"no","MaximumRetryCount":0} and
      .[0].HostConfig.AutoRemove == false and
      .[0].HostConfig.CapAdd == null and
      .[0].HostConfig.CapDrop == ["ALL"] and
      .[0].HostConfig.CgroupnsMode == "private" and
      .[0].HostConfig.IpcMode == "private" and
      .[0].HostConfig.Privileged == false and
      .[0].HostConfig.PublishAllPorts == false and
      .[0].HostConfig.PidMode == "" and
      .[0].HostConfig.UsernsMode == "" and
      .[0].HostConfig.Devices == [] and
      .[0].HostConfig.DeviceRequests == null and
      .[0].HostConfig.ReadonlyRootfs == true and
      .[0].HostConfig.SecurityOpt == ["no-new-privileges"] and
      .[0].HostConfig.Tmpfs == {
        "/tmp":"rw,noexec,nosuid,nodev,size=64m"
      } and
      .[0].HostConfig.ShmSize == 8388608 and
      .[0].HostConfig.Memory == 1073741824 and
      .[0].HostConfig.MemorySwap == 1073741824 and
      .[0].HostConfig.NanoCpus == 1000000000 and
      .[0].HostConfig.PidsLimit == 64 and
      .[0].HostConfig.Ulimits == [
        {"Name":"fsize","Hard":1048576,"Soft":1048576},
        {"Name":"nofile","Hard":128,"Soft":128}
      ] and
      .[0].Mounts == []
    ' "$inspect_path" >/dev/null
}


create_container() {
  local container_script
  local create_output

  container_script=$'set -eu\numask 077\nroot=/tmp/archive\n/usr/bin/mkdir \"$root\"\n/usr/bin/tar --no-same-owner --no-same-permissions -xf - -C \"$root\"\n/usr/bin/printf \"%s  %s\\n\" \"$1\" \"$root/$2\" | /usr/bin/sha256sum -c - >/dev/null\nexec /usr/local/bin/python3 -I -S -P -B \"$root/$2\" \"$root/$3\" \"$root/$4\"'

  create_output=$(
    /opt/homebrew/bin/docker create \
      -i \
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
      --shm-size 8m \
      --cap-drop ALL \
      --security-opt no-new-privileges \
      --user 65534:65534 \
      --log-driver none \
      --no-healthcheck \
      --stop-timeout 1 \
      --env HOME=/tmp \
      --env LANG=C \
      --env LC_ALL=C \
      --env PYTHONHASHSEED=0 \
      --label "org.crypto-autoresearcher.authorization=${AUTH_HEAD}" \
      --label "org.crypto-autoresearcher.consumption=${CONSUMPTION_COMMIT}" \
      --entrypoint /bin/sh \
      "$IMAGE" \
      -c "$container_script" sgcp-v3 \
      "$CONTAINER_RUNNER_SHA256_ARG" \
      "$CONTAINER_RUNNER_PATH" \
      "$SOURCE_PATH" \
      "$TEST_PATH" \
      2>"${RUN_DIR}/docker-create-stderr.log"
  ) || { record_failure "INFRASTRUCTURE_FAILURE" "docker create failed" 71; return $?; }
  /usr/bin/printf '%s\n' "$create_output" |
    /usr/bin/grep -Eq '^[0-9a-f]{64}$' ||
    { record_failure "INFRASTRUCTURE_FAILURE" "container ID length mismatch" 71; return $?; }
  CONTAINER_ID="$create_output"
  /usr/bin/printf '%s\n' "$CONTAINER_ID" >"${RUN_DIR}/container-id.txt"

  /opt/homebrew/bin/docker inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-inspect-pre.json" \
    2>"${RUN_DIR}/docker-inspect-pre-stderr.log" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "pre-start inspect failed" 71; return $?; }
  validate_container_inspect "${RUN_DIR}/docker-inspect-pre.json" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "pre-start HostConfig mismatch" 71; return $?; }
  return 0
}


run_container() {
  local pipeline_script
  local wrapper_status

  pipeline_script=$'set -u\nsetopt pipefail\nrepo=\"$1\"\ncommit=\"$2\"\nrunner=\"$3\"\nsource=\"$4\"\ntest=\"$5\"\ninput_tar=\"$6\"\narchive_stderr=\"$7\"\ntee_stderr=\"$8\"\ncid=\"$9\"\ncontainer_stderr=\"${10}\"\npipeline_status=\"${11}\"\nGIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -C \"$repo\" archive --format=tar \"$commit\" \"$runner\" \"$source\" \"$test\" 2>\"$archive_stderr\" | /usr/bin/tee \"$input_tar\" 2>\"$tee_stderr\" | /bin/zsh -f -c '\\''/opt/homebrew/bin/docker start -a -i \"$1\" 2>\"$2\"'\\'' -- \"$cid\" \"$container_stderr\"\nstatuses=(\"${pipestatus[@]}\")\n/usr/bin/printf \"%s\\n\" \"${statuses[@]}\" >\"$pipeline_status\"\n[[ \"${statuses[1]}\" -eq 0 && \"${statuses[2]}\" -eq 0 ]] || exit 74\nexit \"${statuses[3]}\"'

  /bin/zsh -f -c '
    ulimit -f 4096
    [[ "$(ulimit -f)" == "4096" ]] || exit 75
    /usr/bin/time -lp -o "$1" \
      /opt/homebrew/bin/gtimeout --verbose --signal=TERM --kill-after=5s 180s \
        /bin/zsh -f -c "$2" -- \
          "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" \
        >"${14}" 2>"${15}"
  ' -- \
    "${RUN_DIR}/resource.txt" \
    "$pipeline_script" \
    "$REPO" \
    "$CONSUMPTION_COMMIT" \
    "$CONTAINER_RUNNER_PATH" \
    "$SOURCE_PATH" \
    "$TEST_PATH" \
    "${RUN_DIR}/input.tar" \
    "${RUN_DIR}/git-archive-stderr.log" \
    "${RUN_DIR}/tee-stderr.log" \
    "$CONTAINER_ID" \
    "${RUN_DIR}/stderr.log" \
    "${RUN_DIR}/pipeline-status.txt" \
    "${RUN_DIR}/stdout.json" \
    "${RUN_DIR}/timeout-controller.log"
  wrapper_status=$?
  /usr/bin/printf '%s\n' "$wrapper_status" >"${RUN_DIR}/docker-exit-code.txt"

  if [[ "$wrapper_status" -eq 124 || "$wrapper_status" -eq 137 ]] &&
    /usr/bin/grep -q '^timeout: sending signal ' \
      "${RUN_DIR}/timeout-controller.log"; then
    /usr/bin/printf '%s\n' "true" >"${RUN_DIR}/timeout-observed.txt"
  else
    /usr/bin/printf '%s\n' "false" >"${RUN_DIR}/timeout-observed.txt"
  fi
  return 0
}


inspect_and_cleanup_container() {
  local post_valid="false"
  local cleanup_status
  local cleanup_verify_status
  local docker_server
  local oom_value="unknown"

  if /opt/homebrew/bin/docker inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-inspect-post.json" \
    2>"${RUN_DIR}/docker-inspect-post-stderr.log"; then
    if validate_container_inspect "${RUN_DIR}/docker-inspect-post.json"; then
      post_valid="true"
      oom_value=$(
        /opt/homebrew/bin/jq -r '.[0].State.OOMKilled' \
          "${RUN_DIR}/docker-inspect-post.json"
      )
    fi
  fi
  /usr/bin/printf '%s\n' "$post_valid" >"${RUN_DIR}/docker-post-inspect-valid.txt"
  /usr/bin/printf '%s\n' "$oom_value" >"${RUN_DIR}/oom-killed.txt"

  if [[ "$post_valid" != "true" ]]; then
    /usr/bin/printf '%s\n' "NOT_ATTEMPTED_UNVERIFIED_ID" \
      >"${RUN_DIR}/docker-cleanup-exit-code.txt"
    return 71
  fi

  /opt/homebrew/bin/docker rm -f "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-cleanup.log" \
    2>"${RUN_DIR}/docker-cleanup-stderr.log"
  cleanup_status=$?
  /usr/bin/printf '%s\n' "$cleanup_status" \
    >"${RUN_DIR}/docker-cleanup-exit-code.txt"
  [[ "$cleanup_status" -eq 0 ]] || return 71

  docker_server=$(
    /opt/homebrew/bin/docker version --format '{{.Server.Version}}'
  ) || return 71
  [[ "$docker_server" == "29.4.3" ]] || return 71
  /opt/homebrew/bin/docker inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-cleanup-verify-stdout.log" \
    2>"${RUN_DIR}/docker-cleanup-verify-stderr.log"
  cleanup_verify_status=$?
  /usr/bin/printf '%s\n' "$cleanup_verify_status" \
    >"${RUN_DIR}/docker-cleanup-verify-exit-code.txt"
  [[ "$cleanup_verify_status" -ne 0 ]] || return 71
  /usr/bin/grep -Fq "No such object: ${CONTAINER_ID}" \
    "${RUN_DIR}/docker-cleanup-verify-stderr.log" || return 71
  return 0
}


validate_valid_result() {
  local line_count

  line_count=$(/usr/bin/wc -l <"${RUN_DIR}/stdout.json") || return 1
  [[ "$line_count" -eq 1 ]] || return 1
  /opt/homebrew/bin/jq -cS . "${RUN_DIR}/stdout.json" \
    >"${RUN_DIR}/stdout-canonical.json" || return 1
  /usr/bin/cmp -s "${RUN_DIR}/stdout.json" \
    "${RUN_DIR}/stdout-canonical.json" || return 1
  [[ ! -s "${RUN_DIR}/stderr.log" ]] || return 1

  /opt/homebrew/bin/jq -e -s \
    '
      length == 1 and
      (.[0] | keys) == [
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
      ] and
      .[0].classification == "VALID_DEVELOPMENT_TEST" and
      .[0].details == [] and
      .[0].errors == 0 and
      .[0].failures == 0 and
      .[0].expected_failures == 0 and
      .[0].skipped == 0 and
      .[0].unexpected_successes == 0 and
      .[0].tests_started == 5 and
      .[0].events == [
        {
          "id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_scalar_congruence_and_least_slope_selection",
          "outcome":"ok"
        },
        {
          "id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_witnesses_fibers_representatives_diagnostics_and_ops",
          "outcome":"ok"
        },
        {
          "id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_every_reachable_domain_error_and_charged_prefix",
          "outcome":"ok"
        },
        {
          "id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_first_error_precedence",
          "outcome":"ok"
        },
        {
          "id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_public_results_and_inputs_are_immutable",
          "outcome":"ok"
        }
      ] and
      ([.[0].runtime_before, .[0].runtime_after] |
        all(
          (keys | sort) == [
            "cpu_stat",
            "memory_current_bytes",
            "memory_peak_bytes",
            "pids_current",
            "pids_peak"
          ] and
          (.memory_current_bytes | type == "number" and . >= 0 and . <= 1073741824) and
          (.memory_peak_bytes | type == "number" and . >= 0 and . <= 1073741824) and
          (.pids_current | type == "number" and . >= 1 and . <= 64) and
          (.pids_peak | type == "number" and . >= 1 and . <= 64) and
          (.cpu_stat | type == "object") and
          (.cpu_stat | keys | sort) == [
            "burst_usec",
            "nice_usec",
            "nr_bursts",
            "nr_periods",
            "nr_throttled",
            "system_usec",
            "throttled_usec",
            "usage_usec",
            "user_usec"
          ] and
          (.cpu_stat.usage_usec | type == "number" and . >= 0) and
          (.cpu_stat.user_usec | type == "number" and . >= 0) and
          (.cpu_stat.system_usec | type == "number" and . >= 0) and
          (.cpu_stat.nr_periods | type == "number" and . >= 0) and
          (.cpu_stat.nr_throttled | type == "number" and . >= 0) and
          (.cpu_stat.throttled_usec | type == "number" and . >= 0)
        )
      ) and
      .[0].runtime_after.memory_peak_bytes >=
        .[0].runtime_before.memory_peak_bytes and
      .[0].runtime_after.cpu_stat.usage_usec >=
        .[0].runtime_before.cpu_stat.usage_usec
    ' "${RUN_DIR}/stdout.json" >/dev/null
}


classify_result() {
  local docker_exit
  local timeout_observed
  local oom_killed
  local state_exit
  local state_status
  local cleanup_exit
  local post_valid

  docker_exit="$(<"${RUN_DIR}/docker-exit-code.txt")"
  timeout_observed="$(<"${RUN_DIR}/timeout-observed.txt")"
  oom_killed="$(<"${RUN_DIR}/oom-killed.txt")"
  cleanup_exit="$(<"${RUN_DIR}/docker-cleanup-exit-code.txt")"
  post_valid="$(<"${RUN_DIR}/docker-post-inspect-valid.txt")"
  state_exit=$(
    /opt/homebrew/bin/jq -er '.[0].State.ExitCode' \
      "${RUN_DIR}/docker-inspect-post.json"
  ) || return 71
  state_status=$(
    /opt/homebrew/bin/jq -er '.[0].State.Status' \
      "${RUN_DIR}/docker-inspect-post.json"
  ) || return 71

  [[ "$post_valid" == "true" && "$cleanup_exit" == "0" ]] || return 71

  if [[ "$oom_killed" == "true" ]]; then
    CLASSIFICATION="RESOURCE_EXHAUSTION"
    return 137
  fi
  if [[ "$timeout_observed" == "true" ]]; then
    CLASSIFICATION="TIMEOUT"
    return 124
  fi
  [[ "$state_status" == "exited" ]] || return 71
  if [[ "$docker_exit" == "0" && "$state_exit" == "0" ]] &&
    validate_valid_result; then
    CLASSIFICATION="VALID_DEVELOPMENT_TEST"
    return 0
  fi
  if [[ "$docker_exit" == "1" && "$state_exit" == "1" ]] &&
    /opt/homebrew/bin/jq -e -s \
      'length == 1 and .[0].classification == "TEST_FAILURE"' \
      "${RUN_DIR}/stdout.json" >/dev/null 2>&1; then
    CLASSIFICATION="TEST_FAILURE"
    return 1
  fi
  if [[ "$docker_exit" == "70" && "$state_exit" == "70" ]] &&
    /opt/homebrew/bin/jq -e -s \
      'length == 1 and .[0].classification == "PREFLIGHT_FAILURE"' \
      "${RUN_DIR}/stdout.json" >/dev/null 2>&1; then
    CLASSIFICATION="PREFLIGHT_FAILURE"
    return 70
  fi
  CLASSIFICATION="INFRASTRUCTURE_FAILURE"
  return 71
}


main() {
  local result_status

  preclaim_main || return $?
  validate_authorization || return $?
  commit_consumption_marker || return $?
  inventory_to_file "pre-execution" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "pre-execution inventory rejected" 71; return $?; }
  create_container || return $?
  run_container || return $?
  inspect_and_cleanup_container
  result_status=$?
  if [[ "$result_status" -ne 0 ]]; then
    CLASSIFICATION="INFRASTRUCTURE_FAILURE"
  else
    classify_result
    result_status=$?
  fi
  inventory_to_file "post-execution" || {
    CLASSIFICATION="INFRASTRUCTURE_FAILURE"
    return 71
  }
  return "$result_status"
}


main
typeset -g MAIN_STATUS=$?
if [[ "$INITIALIZED" == "true" ]]; then
  write_receipt "$CLASSIFICATION"
fi

case "$CLASSIFICATION" in
  VALID_DEVELOPMENT_TEST) exit 0 ;;
  TEST_FAILURE) exit 1 ;;
  PREFLIGHT_FAILURE) exit 70 ;;
  INFRASTRUCTURE_FAILURE) exit 71 ;;
  TIMEOUT) exit 124 ;;
  RESOURCE_EXHAUSTION) exit 137 ;;
  *) exit "$MAIN_STATUS" ;;
esac
