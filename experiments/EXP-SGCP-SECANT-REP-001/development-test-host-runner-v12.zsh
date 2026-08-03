#!/bin/zsh

set -u
setopt pipefail
umask 077
ulimit -f 4096
[[ "$(ulimit -f)" == "4096" ]] || exit 72

readonly MODE="${1-}"
readonly AUTH_HEAD="${2-}"
readonly PROTOCOL_COMMIT_ARG="${3-}"
readonly PROTOCOL_SHA256_ARG="${4-}"
readonly HOST_RUNNER_SHA256_ARG="${5-}"
readonly AUTH_VALIDATOR_SHA256_ARG="${6-}"
readonly CONTAINER_RUNNER_SHA256_ARG="${7-}"
readonly RESULT_VALIDATOR_SHA256_ARG="${8-}"

readonly REPO="/Volumes/Volume/crypto-autoresearcher-worktrees/recursive-s3-quotient-001"
readonly BRANCH_REF="refs/heads/codex/recursive-s3-quotient-001"
readonly COMMON_GIT_DIR="/Volumes/Volume/crypto-autoresearcher/.git"
readonly WORKTREE_GIT_DIR="/Volumes/Volume/crypto-autoresearcher/.git/worktrees/recursive-s3-quotient-001"
readonly EXP="experiments/EXP-SGCP-SECANT-REP-001"
readonly RUN_ID="DEV-SGCP-SECANT-PURE-CORE-V12"
readonly RUN_DIR="${REPO}/${EXP}/${RUN_ID}"
readonly BASE_COMMIT="6726de49c9b12afe024a2be190004d1119d42827"
readonly BASE_TREE="6511be9296e286aee26773f5bc7a37288be2cc25"
readonly PROTOCOL_PATH="${EXP}/development-test-execution-protocol-v12.json"
readonly HOST_RUNNER_PATH="${EXP}/development-test-host-runner-v12.zsh"
readonly AUTH_VALIDATOR_PATH="${EXP}/development-test-authorization-validator-v12.jq"
readonly RESULT_VALIDATOR_PATH="${EXP}/development-test-result-validator-v12.jq"
readonly CONTAINER_RUNNER_PATH="${EXP}/development-test-container-runner-v3.py"
readonly SOURCE_PATH="${EXP}/src/sgcp_secant_math_core.py"
readonly TEST_PATH="${EXP}/tests/test_sgcp_secant_math_core.py"
readonly DECISION_PATH="${EXP}/development-test-decision-v12.json"
readonly THEORY_PATH="${EXP}/development-test-theory-review-v12.json"
readonly ACCOUNTING_PATH="${EXP}/development-test-accounting-review-v12.json"
readonly RED_TEAM_PATH="${EXP}/development-test-red-team-review-v12.json"
readonly CONSUMPTION_REF="refs/crypto-autoresearcher/consumptions/EXP-SGCP-SECANT-REP-001-development-test-v12"
readonly RESULT_REF="refs/crypto-autoresearcher/results/EXP-SGCP-SECANT-REP-001-development-test-v12"
readonly CONTAINER_NAME="sgcp-v12-${PROTOCOL_COMMIT_ARG}"
readonly IMAGE="python@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly IMAGE_ID="sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly EXPECTED_SOURCE_SHA256="8b8781d688188afa41e87f33e15a306fc5a9f5326b8e93316247263ee8f933bd"
readonly EXPECTED_TEST_SHA256="2b0e34524f22cf5d2dd70c3eff857b186c10c9d8882bb2893999febc1352417a"

typeset -g CLASSIFICATION="INFRASTRUCTURE_FAILURE"
typeset -g CONSUMPTION_COMMIT="ABSENT"
typeset -g CONSUMPTION_REF_CREATED="false"
typeset -g RESULT_COMMIT="ABSENT"
typeset -g RESULT_REF_CREATED="false"
typeset -g CONTAINER_ID="ABSENT"
typeset -g CONTAINER_OWNED="false"
typeset -g CONTAINER_EVER_OWNED="false"
typeset -g CREATE_PENDING="false"
typeset -g RECOVERY_MODE="false"
typeset -g CLEANUP_DONE="false"
typeset -g CLEANUP_PROVED="false"
typeset -g RESULT_REF_PRESENT_UNVALIDATED="false"
typeset -g CONSUMPTION_REF_PRESENT_UNVALIDATED="false"
typeset -g INITIALIZED="false"
typeset -g STARTED_AT="ABSENT"
typeset -g FINISHED_AT="ABSENT"
typeset -g CONTAINER_SCRIPT=""
typeset -g EXACT_CONTAINER_ID_VALUE=""
typeset -g EXACT_GIT_OBJECT_ID_VALUE=""
typeset -g PRESEAL_HOST_ELAPSED_SECONDS=0
typeset -gr HOST_START_SECONDS=$SECONDS


git_safe() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s \
    /usr/bin/env -i \
      HOME=/tmp \
      TMPDIR=/tmp \
      LANG=C \
      LC_ALL=C \
      PATH=/usr/bin:/bin:/usr/sbin:/sbin \
      GIT_CONFIG_NOSYSTEM=1 \
      GIT_CONFIG_GLOBAL=/dev/null \
      GIT_OPTIONAL_LOCKS=0 \
      GIT_NO_REPLACE_OBJECTS=1 \
      /usr/bin/git \
        -c core.fsmonitor=false \
        -c core.hooksPath=/dev/null \
        -c core.attributesFile=/dev/null \
        -C "$REPO" "$@"
}


git_safe_ident() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s \
    /usr/bin/env -i \
      HOME=/tmp \
      TMPDIR=/tmp \
      LANG=C \
      LC_ALL=C \
      PATH=/usr/bin:/bin:/usr/sbin:/sbin \
      GIT_CONFIG_NOSYSTEM=1 \
      GIT_CONFIG_GLOBAL=/dev/null \
      GIT_OPTIONAL_LOCKS=0 \
      GIT_NO_REPLACE_OBJECTS=1 \
      GIT_AUTHOR_NAME="Codex Research Coordinator" \
      GIT_AUTHOR_EMAIL="codex@localhost" \
      GIT_COMMITTER_NAME="Codex Research Coordinator" \
      GIT_COMMITTER_EMAIL="codex@localhost" \
      /usr/bin/git \
        -c core.fsmonitor=false \
        -c core.hooksPath=/dev/null \
        -c core.attributesFile=/dev/null \
        -c commit.gpgSign=false \
        -C "$REPO" "$@"
}


docker_safe() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s \
    /opt/homebrew/bin/docker "$@"
}


docker_recovery_safe() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=1s 4s \
    /opt/homebrew/bin/docker "$@"
}


docker_control() {
  if [[ "$RECOVERY_MODE" == "true" ]]; then
    docker_recovery_safe "$@"
  else
    docker_safe "$@"
  fi
}


find_safe() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s \
    /usr/bin/find "$@"
}


sha256_file() {
  if [[ ! -f "$1" ]]; then
    /usr/bin/printf 'ABSENT'
    return 0
  fi
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}


sha256_commit_path() {
  git_safe show "${1}:${2}" |
    /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}'
}


verify_tool() {
  [[ "$(sha256_file "$1")" == "$2" ]]
}


raw_delta_signature() {
  git_safe diff-tree --raw --no-abbrev --no-commit-id -r "$1" |
    /usr/bin/awk '{print $1, $2, $5, $6}'
}


verify_physical_directory() {
  local path="$1"
  local physical

  [[ -d "$path" && ! -L "$path" ]] || return 1
  physical=$(cd -q -- "$path" && pwd -P) || return 1
  [[ "$physical" == "$path" ]]
}


verify_physical_ancestry() {
  verify_physical_directory "$REPO" &&
    verify_physical_directory "${REPO}/experiments" &&
    verify_physical_directory "${REPO}/${EXP}"
}


reject_effective_git_commands() {
  local output
  local status

  output=$(git_safe config --show-scope --get-regexp \
    '^(filter\..*\.(clean|process|smudge|required)|tar\..*\.command)$')
  status=$?
  [[ "$status" -eq 1 && -z "$output" ]]
}


materialize_commit_path() {
  git_safe show "${1}:${2}" >"$3"
}


record_failure() {
  CLASSIFICATION="$1"
  /usr/bin/printf '%s\n' "$2" >>"${RUN_DIR}/preflight.log" || return 71
  return "$3"
}


forbidden_paths_emit() {
  local ancestor

  find_safe "${REPO}/${EXP}" \
    \( -name '._*' -o -name '__pycache__' -o \
       -name '*.pyc' -o -name '*.pyo' \) -print || return 1
  for ancestor in \
    "${REPO}/._experiments" \
    "${REPO}/experiments/._EXP-SGCP-SECANT-REP-001" \
    "/Volumes/Volume/crypto-autoresearcher-worktrees/._recursive-s3-quotient-001"
  do
    if [[ -e "$ancestor" || -L "$ancestor" ]]; then
      /usr/bin/printf '%s\n' "$ancestor" || return 1
    fi
  done
}


inventory_capture() {
  local phase="$1"
  local output
  local path="${RUN_DIR}/${phase}-forbidden-paths.txt"

  output=$(forbidden_paths_emit) || return 1
  /usr/bin/printf '%s' "$output" >"$path" || return 1
  [[ -z "$output" ]]
}


inventory_empty_without_output() {
  local output

  output=$(forbidden_paths_emit) || return 1
  [[ -z "$output" ]]
}


json_integer_or_null() {
  local path="$1"
  local value

  if [[ ! -f "$path" ]]; then
    /usr/bin/printf 'null'
    return 0
  fi
  value="$(<"$path")"
  /usr/bin/printf '%s\n' "$value" |
    /usr/bin/grep -Eq '^[0-9]+$' || return 1
  /usr/bin/printf '%s' "$value"
}


json_boolean_or_null() {
  local path="$1"
  local value

  if [[ ! -f "$path" ]]; then
    /usr/bin/printf 'null'
    return 0
  fi
  value="$(<"$path")"
  [[ "$value" == "true" || "$value" == "false" ]] || return 1
  /usr/bin/printf '%s' "$value"
}


write_run_receipt() {
  local wrapper_exit
  local container_exit
  local timeout_observed
  local oom_killed
  local cleanup_exit
  local protocol_hash
  local authorization_validator_hash
  local result_validator_hash
  local input_hash
  local stdout_hash
  local stderr_hash
  local resource_hash
  local inspect_pre_hash
  local inspect_post_hash

  FINISHED_AT=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ') || return 1
  PRESEAL_HOST_ELAPSED_SECONDS=$((SECONDS - HOST_START_SECONDS))
  wrapper_exit=$(json_integer_or_null \
    "${RUN_DIR}/pipeline-wrapper-exit-code.txt") || return 1
  container_exit=$(json_integer_or_null \
    "${RUN_DIR}/container-state-exit-code.txt") || return 1
  timeout_observed=$(json_boolean_or_null \
    "${RUN_DIR}/timeout-observed.txt") || return 1
  oom_killed=$(json_boolean_or_null "${RUN_DIR}/oom-killed.txt") || return 1
  cleanup_exit=$(json_integer_or_null \
    "${RUN_DIR}/docker-cleanup-exit-code.txt") || return 1
  protocol_hash=$(sha256_file \
    "${RUN_DIR}/evidence-input/protocol.json") || return 1
  authorization_validator_hash=$(sha256_file \
    "${RUN_DIR}/evidence-input/authorization-validator.jq") || return 1
  result_validator_hash=$(sha256_file \
    "${RUN_DIR}/evidence-input/result-validator.jq") || return 1
  input_hash=$(sha256_file "${RUN_DIR}/input.tar") || return 1
  stdout_hash=$(sha256_file "${RUN_DIR}/stdout.json") || return 1
  stderr_hash=$(sha256_file "${RUN_DIR}/stderr.log") || return 1
  resource_hash=$(sha256_file "${RUN_DIR}/resource.txt") || return 1
  inspect_pre_hash=$(sha256_file \
    "${RUN_DIR}/docker-inspect-pre.json") || return 1
  inspect_post_hash=$(sha256_file \
    "${RUN_DIR}/docker-inspect-post.json") || return 1

  /usr/bin/printf '%s\n' "$FINISHED_AT" \
    >"${RUN_DIR}/finished-at-utc.txt" || return 1
  /usr/bin/printf '%s\n' "$CLASSIFICATION" \
    >"${RUN_DIR}/classification.txt" || return 1
  /opt/homebrew/bin/jq -cnS \
    --arg authorization_head "$AUTH_HEAD" \
    --arg classification "$CLASSIFICATION" \
    --argjson cleanup_exit_code "$cleanup_exit" \
    --argjson container_exit_code "$container_exit" \
    --arg container_id "$CONTAINER_ID" \
    --arg container_name "$CONTAINER_NAME" \
    --arg consumption_commit "$CONSUMPTION_COMMIT" \
    --arg consumption_ref "$CONSUMPTION_REF" \
    --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
    --arg finished_at_utc "$FINISHED_AT" \
    --argjson cleanup_proved "$CLEANUP_PROVED" \
    --argjson container_ever_owned "$CONTAINER_EVER_OWNED" \
    --argjson preseal_host_elapsed_seconds \
      "$PRESEAL_HOST_ELAPSED_SECONDS" \
    --argjson oom_killed "$oom_killed" \
    --argjson pipeline_wrapper_exit_code "$wrapper_exit" \
    --arg protocol_commit "$PROTOCOL_COMMIT_ARG" \
    --arg result_ref "$RESULT_REF" \
    --arg run_id "$RUN_ID" \
    --arg started_at_utc "$STARTED_AT" \
    --argjson timeout_observed "$timeout_observed" \
    --arg protocol_sha256 "$protocol_hash" \
    --arg host_runner_sha256 "$HOST_RUNNER_SHA256_ARG" \
    --arg authorization_validator_sha256 "$authorization_validator_hash" \
    --arg result_validator_sha256 "$result_validator_hash" \
    --arg container_runner_sha256 "$CONTAINER_RUNNER_SHA256_ARG" \
    --arg source_sha256 "$EXPECTED_SOURCE_SHA256" \
    --arg test_sha256 "$EXPECTED_TEST_SHA256" \
    --arg input_tar_sha256 "$input_hash" \
    --arg stdout_sha256 "$stdout_hash" \
    --arg stderr_sha256 "$stderr_hash" \
    --arg resource_sha256 "$resource_hash" \
    --arg docker_inspect_pre_sha256 "$inspect_pre_hash" \
    --arg docker_inspect_post_sha256 "$inspect_post_hash" \
    '{
      authorization_head: $authorization_head,
      classification: $classification,
      cleanup_exit_code: $cleanup_exit_code,
      cleanup_proved: $cleanup_proved,
      container_exit_code: $container_exit_code,
      container_ever_owned: $container_ever_owned,
      container_id: $container_id,
      container_name: $container_name,
      consumption_commit: $consumption_commit,
      consumption_ref: $consumption_ref,
      experiment_id: $experiment_id,
      finished_at_utc: $finished_at_utc,
      hashes: {
        authorization_validator_sha256: $authorization_validator_sha256,
        container_runner_sha256: $container_runner_sha256,
        docker_inspect_post_sha256: $docker_inspect_post_sha256,
        docker_inspect_pre_sha256: $docker_inspect_pre_sha256,
        host_runner_sha256: $host_runner_sha256,
        input_tar_sha256: $input_tar_sha256,
        protocol_sha256: $protocol_sha256,
        resource_sha256: $resource_sha256,
        result_validator_sha256: $result_validator_sha256,
        source_sha256: $source_sha256,
        stderr_sha256: $stderr_sha256,
        stdout_sha256: $stdout_sha256,
        test_sha256: $test_sha256
      },
      preseal_host_elapsed_seconds: $preseal_host_elapsed_seconds,
      oom_killed: $oom_killed,
      pipeline_wrapper_exit_code: $pipeline_wrapper_exit_code,
      protocol_commit: $protocol_commit,
      result_ref: $result_ref,
      run_id: $run_id,
      started_at_utc: $started_at_utc,
      timeout_observed: $timeout_observed
    }' >"${RUN_DIR}/run-receipt.json" || return 1
  require_canonical_json_line "${RUN_DIR}/run-receipt.json"
}


generate_artifact_manifest() {
  local manifest="${RUN_DIR}/artifact-manifest.sha256"
  local file
  local relative
  local digest
  typeset -a entries

  entries=("${RUN_DIR}"/**/*(DN))
  for file in "${entries[@]}"; do
    [[ "$file" != *$'\n'* ]] || return 1
    [[ -d "$file" && ! -L "$file" || -f "$file" && ! -L "$file" ]] ||
      return 1
  done
  : >"$manifest" || return 1
  for file in "${RUN_DIR}"/**/*(.DN); do
    [[ "$file" == "$manifest" ||
      "$file" == "${RUN_DIR}/result-seal.json" ]] && continue
    relative="${file#${RUN_DIR}/}"
    digest=$(sha256_file "$file") || return 1
    /usr/bin/printf '%s\n' "$digest" |
      /usr/bin/grep -Eq '^[0-9a-f]{64}$' || return 1
    /usr/bin/printf '%s  %s\n' "$digest" "$relative" \
      >>"$manifest" || return 1
  done
  [[ -s "$manifest" ]]
}


validate_valid_artifact_set() {
  local file
  local relative
  typeset -a actual
  typeset -a expected
  typeset -a entries
  typeset -a directories

  entries=("${RUN_DIR}"/**/*(DN))
  for file in "${entries[@]}"; do
    [[ "$file" != *$'\n'* ]] || return 1
    [[ -d "$file" && ! -L "$file" || -f "$file" && ! -L "$file" ]] ||
      return 1
  done
  for file in "${RUN_DIR}"/**/*(.DN); do
    relative="${file#${RUN_DIR}/}"
    actual+=("$relative")
  done
  directories=("${RUN_DIR}"/**/*(/DN))
  [[ "${#directories}" -eq 1 &&
    "${directories[1]}" == "${RUN_DIR}/evidence-input" ]] || return 1
  expected=(
    "authorization-validation.txt"
    "classification.txt"
    "consumption-blob-sha1.txt"
    "consumption-candidate-blob-sha1.txt"
    "consumption-candidate-commit-sha1.txt"
    "consumption-candidate-tree-sha1.txt"
    "consumption-commit-sha1.txt"
    "consumption-git-paths.txt"
    "consumption-tree-sha1.txt"
    "consumption.json"
    "container-id.txt"
    "container-state-exit-code.txt"
    "docker-cleanup-exit-code.txt"
    "docker-cleanup-stderr.log"
    "docker-cleanup-verify-exit-code.txt"
    "docker-cleanup-verify-stderr.log"
    "docker-cleanup-verify-stdout.log"
    "docker-cleanup.log"
    "docker-create-cid.txt"
    "docker-create-exit-code.txt"
    "docker-create-stderr.log"
    "docker-create-stdout.txt"
    "docker-inspect-post-stderr.log"
    "docker-inspect-post.json"
    "docker-inspect-pre-stderr.log"
    "docker-inspect-pre.json"
    "docker-name-cleanup-verify-exit-code.txt"
    "docker-name-cleanup-verify-stderr.log"
    "docker-name-cleanup-verify-stdout.log"
    "evidence-input/accounting.json"
    "evidence-input/authorization-validator.jq"
    "evidence-input/decision.json"
    "evidence-input/protocol.json"
    "evidence-input/red-team.json"
    "evidence-input/result-validator.jq"
    "evidence-input/theory.json"
    "final-forbidden-paths.txt"
    "finished-at-utc.txt"
    "git-archive-stderr.log"
    "input.tar"
    "oom-killed.txt"
    "pipeline-status.txt"
    "pipeline-wrapper-exit-code.txt"
    "post-execution-forbidden-paths.txt"
    "post-run-cleanup-inspect-exit-code.txt"
    "post-run-cleanup-inspect-stderr.log"
    "post-run-cleanup-inspect.json"
    "post-run-cleanup-ownership-basis.txt"
    "pre-execution-forbidden-paths.txt"
    "preflight.log"
    "resource.txt"
    "run-receipt.json"
    "started-at-utc.txt"
    "stderr.log"
    "stdout-canonical.json"
    "stdout.json"
    "tee-stderr.log"
    "timeout-controller.log"
    "timeout-observed.txt"
  )
  actual=(${(on)actual})
  expected=(${(on)expected})
  [[ "${(j:\n:)actual}" == "${(j:\n:)expected}" ]]
}


preclaim_main() {
  local current_head
  local current_branch
  local replace_output
  local graft_path
  local protocol_topology
  local authorization_topology
  local ref_status
  local result_ref_status
  local consumption_symref_output
  local consumption_symref_status
  local result_symref_output
  local result_symref_status
  local image_id
  local image_platform
  local docker_client
  local docker_server

  [[ "$MODE" == "launch" ]] || return 72
  [[ -n "$AUTH_HEAD" && -n "$PROTOCOL_COMMIT_ARG" &&
    -n "$PROTOCOL_SHA256_ARG" && -n "$HOST_RUNNER_SHA256_ARG" &&
    -n "$AUTH_VALIDATOR_SHA256_ARG" && -n "$CONTAINER_RUNNER_SHA256_ARG" &&
    -n "$RESULT_VALIDATOR_SHA256_ARG" ]] ||
    return 72
  verify_physical_ancestry || return 72
  cd "$REPO" || return 72

  current_head=$(git_safe rev-parse HEAD) || return 72
  [[ "$current_head" == "$AUTH_HEAD" ]] || return 72
  current_branch=$(git_safe symbolic-ref -q HEAD) || return 72
  [[ "$current_branch" == "$BRANCH_REF" ]] || return 72
  replace_output=$(git_safe replace -l) || return 72
  [[ -z "$replace_output" ]] || return 72
  graft_path=$(git_safe rev-parse --git-path info/grafts) || return 72
  [[ ! -e "$graft_path" ]] || return 72
  reject_effective_git_commands || return 72
  [[ "$(git_safe rev-parse --git-dir)" == "$WORKTREE_GIT_DIR" ]] || return 72
  [[ "$(git_safe rev-parse --git-common-dir)" == "$COMMON_GIT_DIR" ]] || return 72

  protocol_topology=$(git_safe rev-list --parents -n 1 "$PROTOCOL_COMMIT_ARG") ||
    return 72
  authorization_topology=$(git_safe rev-list --parents -n 1 "$AUTH_HEAD") ||
    return 72
  [[ "$protocol_topology" == "${PROTOCOL_COMMIT_ARG} ${BASE_COMMIT}" ]] ||
    return 72
  [[ "$authorization_topology" == "${AUTH_HEAD} ${PROTOCOL_COMMIT_ARG}" ]] ||
    return 72
  [[ "$(raw_delta_signature "$PROTOCOL_COMMIT_ARG")" ==
    ":000000 100644 A ${AUTH_VALIDATOR_PATH}"$'\n'\
":000000 100644 A ${PROTOCOL_PATH}"$'\n'\
":000000 100644 A ${HOST_RUNNER_PATH}"$'\n'\
":000000 100644 A ${RESULT_VALIDATOR_PATH}" ]] || return 72
  [[ "$(raw_delta_signature "$AUTH_HEAD")" ==
    ":000000 100644 A ${ACCOUNTING_PATH}"$'\n'\
":000000 100644 A ${DECISION_PATH}"$'\n'\
":000000 100644 A ${RED_TEAM_PATH}"$'\n'\
":000000 100644 A ${THEORY_PATH}" ]] || return 72

  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$PROTOCOL_PATH")" ==
    "$PROTOCOL_SHA256_ARG" ]] || return 72
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$HOST_RUNNER_PATH")" ==
    "$HOST_RUNNER_SHA256_ARG" ]] || return 72
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$AUTH_VALIDATOR_PATH")" ==
    "$AUTH_VALIDATOR_SHA256_ARG" ]] || return 72
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$RESULT_VALIDATOR_PATH")" ==
    "$RESULT_VALIDATOR_SHA256_ARG" ]] || return 72
  [[ "$(sha256_commit_path "$AUTH_HEAD" "$CONTAINER_RUNNER_PATH")" ==
    "$CONTAINER_RUNNER_SHA256_ARG" ]] || return 72
  [[ "$(sha256_commit_path "$AUTH_HEAD" "$SOURCE_PATH")" ==
    "$EXPECTED_SOURCE_SHA256" ]] || return 72
  [[ "$(sha256_commit_path "$AUTH_HEAD" "$TEST_PATH")" ==
    "$EXPECTED_TEST_SHA256" ]] || return 72

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

  git_safe show-ref --verify --quiet "$CONSUMPTION_REF"
  ref_status=$?
  [[ "$ref_status" -eq 1 ]] || return 73
  consumption_symref_output=$(git_safe symbolic-ref -q "$CONSUMPTION_REF")
  consumption_symref_status=$?
  [[ "$consumption_symref_status" -eq 1 &&
    -z "$consumption_symref_output" ]] || return 73
  git_safe show-ref --verify --quiet "$RESULT_REF"
  result_ref_status=$?
  [[ "$result_ref_status" -eq 1 ]] || return 73
  result_symref_output=$(git_safe symbolic-ref -q "$RESULT_REF")
  result_symref_status=$?
  [[ "$result_symref_status" -eq 1 && -z "$result_symref_output" ]] ||
    return 73
  [[ ! -e "$RUN_DIR" && ! -L "$RUN_DIR" ]] || return 73
  [[ ! -e "${REPO}/${EXP}/._${RUN_ID}" ]] || return 73
  verify_physical_ancestry || return 73
  inventory_empty_without_output || return 73

  image_id=$(docker_safe image inspect "$IMAGE" --format '{{.Id}}') ||
    return 72
  image_platform=$(docker_safe image inspect "$IMAGE" \
    --format '{{.Os}}/{{.Architecture}}') || return 72
  docker_client=$(docker_safe version --format '{{.Client.Version}}') ||
    return 72
  docker_server=$(docker_safe version --format '{{.Server.Version}}') ||
    return 72
  [[ "$image_id" == "$IMAGE_ID" && "$image_platform" == "linux/arm64" &&
    "$docker_client" == "28.5.1" && "$docker_server" == "29.4.3" ]] ||
    return 72
  /bin/zsh -f -c 'ulimit -f 4096; [[ "$(ulimit -f)" == "4096" ]]' ||
    return 72

  /bin/mkdir "$RUN_DIR" || return 73
  INITIALIZED="true"
  STARTED_AT=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')
  /usr/bin/printf '%s\n' "$STARTED_AT" \
    >"${RUN_DIR}/started-at-utc.txt" || return 73
  : >"${RUN_DIR}/preflight.log" || return 73
  return 0
}


require_canonical_json_line() {
  local path="$1"
  local canonical
  local line_count

  line_count=$(/usr/bin/wc -l <"$path") || return 1
  [[ "$line_count" -eq 1 ]] || return 1
  canonical=$(/opt/homebrew/bin/jq -cS . "$path") || return 1
  [[ "$(<"$path")" == "$canonical" ]]
}


validate_authorization() {
  local protocol_tree
  local theory_hash
  local accounting_hash
  local red_hash
  local expected_json

  /bin/mkdir "${RUN_DIR}/evidence-input" ||
    { record_failure "INFRASTRUCTURE_FAILURE" "cannot create evidence input" 71; return $?; }
  materialize_commit_path "$AUTH_HEAD" "$PROTOCOL_PATH" \
    "${RUN_DIR}/evidence-input/protocol.json" || return 70
  materialize_commit_path "$AUTH_HEAD" "$DECISION_PATH" \
    "${RUN_DIR}/evidence-input/decision.json" || return 70
  materialize_commit_path "$AUTH_HEAD" "$THEORY_PATH" \
    "${RUN_DIR}/evidence-input/theory.json" || return 70
  materialize_commit_path "$AUTH_HEAD" "$ACCOUNTING_PATH" \
    "${RUN_DIR}/evidence-input/accounting.json" || return 70
  materialize_commit_path "$AUTH_HEAD" "$RED_TEAM_PATH" \
    "${RUN_DIR}/evidence-input/red-team.json" || return 70
  materialize_commit_path "$AUTH_HEAD" "$AUTH_VALIDATOR_PATH" \
    "${RUN_DIR}/evidence-input/authorization-validator.jq" || return 70
  materialize_commit_path "$AUTH_HEAD" "$RESULT_VALIDATOR_PATH" \
    "${RUN_DIR}/evidence-input/result-validator.jq" || return 70
  require_canonical_json_line "${RUN_DIR}/evidence-input/decision.json" ||
    return 70
  require_canonical_json_line "${RUN_DIR}/evidence-input/theory.json" ||
    return 70
  require_canonical_json_line "${RUN_DIR}/evidence-input/accounting.json" ||
    return 70
  require_canonical_json_line "${RUN_DIR}/evidence-input/red-team.json" ||
    return 70
  /bin/chmod 0444 "${RUN_DIR}"/evidence-input/* || return 71
  /bin/chmod 0555 "${RUN_DIR}/evidence-input" || return 71

  [[ "$(sha256_file "${RUN_DIR}/evidence-input/protocol.json")" ==
    "$PROTOCOL_SHA256_ARG" ]] || return 70
  [[ "$(sha256_file "${RUN_DIR}/evidence-input/authorization-validator.jq")" ==
    "$AUTH_VALIDATOR_SHA256_ARG" ]] || return 70
  [[ "$(sha256_file "${RUN_DIR}/evidence-input/result-validator.jq")" ==
    "$RESULT_VALIDATOR_SHA256_ARG" ]] || return 70
  protocol_tree=$(git_safe rev-parse "${PROTOCOL_COMMIT_ARG}^{tree}") ||
    return 70
  theory_hash="$(sha256_file "${RUN_DIR}/evidence-input/theory.json")"
  accounting_hash="$(sha256_file "${RUN_DIR}/evidence-input/accounting.json")"
  red_hash="$(sha256_file "${RUN_DIR}/evidence-input/red-team.json")"
  expected_json=$(
    /opt/homebrew/bin/jq -cn \
      --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
      --arg authorization_head "$AUTH_HEAD" \
      --arg protocol_tree_sha1 "$protocol_tree" \
      --arg base_commit_sha1 "$BASE_COMMIT" \
      --arg base_tree_sha1 "$BASE_TREE" \
      --arg protocol_sha256 "$PROTOCOL_SHA256_ARG" \
      --arg host_runner_sha256 "$HOST_RUNNER_SHA256_ARG" \
      --arg authorization_validator_sha256 "$AUTH_VALIDATOR_SHA256_ARG" \
      --arg result_validator_sha256 "$RESULT_VALIDATOR_SHA256_ARG" \
      --arg container_runner_sha256 "$CONTAINER_RUNNER_SHA256_ARG" \
      --arg protected_source_sha256 "$EXPECTED_SOURCE_SHA256" \
      --arg test_source_sha256 "$EXPECTED_TEST_SHA256" \
      --arg container_image "$IMAGE" \
      --arg container_image_id "$IMAGE_ID" \
      '$ARGS.named'
  ) || return 71
  /opt/homebrew/bin/jq -e -n \
    --argjson expected "$expected_json" \
    --arg theory_receipt_sha256 "$theory_hash" \
    --arg accounting_receipt_sha256 "$accounting_hash" \
    --arg red_team_receipt_sha256 "$red_hash" \
    --slurpfile protocol "${RUN_DIR}/evidence-input/protocol.json" \
    --slurpfile decision "${RUN_DIR}/evidence-input/decision.json" \
    --slurpfile theory "${RUN_DIR}/evidence-input/theory.json" \
    --slurpfile accounting "${RUN_DIR}/evidence-input/accounting.json" \
    --slurpfile red_team "${RUN_DIR}/evidence-input/red-team.json" \
    -f "${RUN_DIR}/evidence-input/authorization-validator.jq" \
    >"${RUN_DIR}/authorization-validation.txt" || return 70
  [[ "$(<"${RUN_DIR}/authorization-validation.txt")" == "true" ]]
}


consume_authorization() {
  local marker_blob
  local marker_tree
  local marker_commit
  local observed_ref
  local ref_status
  local zero="0000000000000000000000000000000000000000"

  /opt/homebrew/bin/jq -cnS \
    --arg id "CONSUME-SGCP-SECANT-DEVELOPMENT-TEST-V12" \
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
    }' >"${RUN_DIR}/consumption.json" || return 71
  require_canonical_json_line "${RUN_DIR}/consumption.json" || return 71
  marker_blob=$(git_safe hash-object -w --no-filters \
    "${RUN_DIR}/consumption.json") || return 71
  marker_tree=$(
    /usr/bin/printf '100644 blob %s\tconsumption.json\n' "$marker_blob" |
      git_safe mktree
  ) || return 71
  marker_commit=$(
    /usr/bin/printf 'SGCP development test V12 authorization consumption\n' |
      git_safe_ident commit-tree "$marker_tree" -p "$AUTH_HEAD"
  ) || return 71
  /usr/bin/printf '%s\n' "$marker_blob" \
    >"${RUN_DIR}/consumption-candidate-blob-sha1.txt" || return 71
  /usr/bin/printf '%s\n' "$marker_tree" \
    >"${RUN_DIR}/consumption-candidate-tree-sha1.txt" || return 71
  /usr/bin/printf '%s\n' "$marker_commit" \
    >"${RUN_DIR}/consumption-candidate-commit-sha1.txt" || return 71
  git_safe update-ref --no-deref --create-reflog -m \
    "consume SGCP development test V12" \
    "$CONSUMPTION_REF" "$marker_commit" "$zero" || return 71
  CONSUMPTION_REF_CREATED="true"
  CONSUMPTION_COMMIT="$marker_commit"

  observed_ref=$(git_safe rev-parse "$CONSUMPTION_REF") || return 71
  [[ "$observed_ref" == "$marker_commit" ]] || return 71
  git_safe symbolic-ref -q "$CONSUMPTION_REF" >/dev/null 2>&1
  [[ "$?" -eq 1 ]] || return 71
  [[ "$(git_safe rev-list --parents -n 1 "$marker_commit")" ==
    "${marker_commit} ${AUTH_HEAD}" ]] || return 71
  [[ "$(git_safe rev-parse "${marker_commit}^{tree}")" == "$marker_tree" ]] ||
    return 71
  [[ "$(git_safe show "${marker_commit}:consumption.json" |
    /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}')" ==
    "$(sha256_file "${RUN_DIR}/consumption.json")" ]] || return 71

  /usr/bin/printf '%s\n' "$marker_blob" \
    >"${RUN_DIR}/consumption-blob-sha1.txt" || return 71
  /usr/bin/printf '%s\n' "$marker_tree" \
    >"${RUN_DIR}/consumption-tree-sha1.txt" || return 71
  /usr/bin/printf '%s\n' "$marker_commit" \
    >"${RUN_DIR}/consumption-commit-sha1.txt" || return 71
  {
    /usr/bin/printf '%s/objects/%s/%s\n' \
      "$COMMON_GIT_DIR" "${marker_blob[1,2]}" "${marker_blob[3,-1]}"
    /usr/bin/printf '%s/objects/%s/%s\n' \
      "$COMMON_GIT_DIR" "${marker_tree[1,2]}" "${marker_tree[3,-1]}"
    /usr/bin/printf '%s/objects/%s/%s\n' \
      "$COMMON_GIT_DIR" "${marker_commit[1,2]}" "${marker_commit[3,-1]}"
    /usr/bin/printf '%s/%s\n' "$COMMON_GIT_DIR" "$CONSUMPTION_REF"
    /usr/bin/printf '%s/logs/%s\n' "$COMMON_GIT_DIR" "$CONSUMPTION_REF"
    /usr/bin/printf '%s/refs/crypto-autoresearcher\n' "$COMMON_GIT_DIR"
    /usr/bin/printf '%s/refs/crypto-autoresearcher/consumptions\n' \
      "$COMMON_GIT_DIR"
    /usr/bin/printf '%s/logs/refs/crypto-autoresearcher\n' "$COMMON_GIT_DIR"
    /usr/bin/printf '%s/logs/refs/crypto-autoresearcher/consumptions\n' \
      "$COMMON_GIT_DIR"
  } >"${RUN_DIR}/consumption-git-paths.txt" || return 71

  git_safe show-ref --verify --quiet "$CONSUMPTION_REF"
  ref_status=$?
  [[ "$ref_status" -eq 0 ]] || return 71
  return 0
}


validate_inspect() {
  local path="$1"

  /opt/homebrew/bin/jq -e \
    --arg cid "$CONTAINER_ID" \
    --arg image "$IMAGE_ID" \
    --arg auth "$AUTH_HEAD" \
    --arg consume "$CONSUMPTION_COMMIT" \
    --arg name "$CONTAINER_NAME" \
    --arg script "$CONTAINER_SCRIPT" \
    --arg runner_hash "$CONTAINER_RUNNER_SHA256_ARG" \
    --arg runner_path "$CONTAINER_RUNNER_PATH" \
    --arg source_path "$SOURCE_PATH" \
    --arg test_path "$TEST_PATH" \
    '
      length == 1 and
      .[0].Id == $cid and
      .[0].Name == ("/" + $name) and
      .[0].Image == $image and
      .[0].Config.Hostname == $cid[0:12] and
      .[0].Config.Domainname == "" and
      .[0].Config.User == "65534:65534" and
      .[0].Config.Entrypoint == ["/bin/sh"] and
      .[0].Config.Cmd == [
        "-c", $script, "sgcp-v12", $runner_hash,
        $runner_path, $source_path, $test_path
      ] and
      .[0].Config.OpenStdin == true and
      .[0].Config.AttachStdin == true and
      .[0].Config.AttachStdout == true and
      .[0].Config.AttachStderr == true and
      .[0].Config.Tty == false and
      .[0].Config.StdinOnce == true and
      .[0].Config.StopTimeout == 1 and
      .[0].Config.ExposedPorts == null and
      .[0].Config.Volumes == null and
      .[0].Config.WorkingDir == "" and
      .[0].Config.NetworkDisabled == null and
      .[0].Config.MacAddress == null and
      .[0].Config.OnBuild == null and
      .[0].Config.StopSignal == null and
      .[0].Config.Shell == null and
      (.[0].Config.Env | length == 9) and
      (.[0].Config.Env | sort) == ([
        "HOME=/tmp",
        "LANG=C",
        "LC_ALL=C",
        "PYTHONHASHSEED=0",
        "PYTHONDONTWRITEBYTECODE=1",
        "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D",
        "PYTHON_VERSION=3.11.15",
        "PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625"
      ] | sort) and
      .[0].Config.Healthcheck.Test == ["NONE"] and
      .[0].Config.Labels == {
        "org.crypto-autoresearcher.authorization": $auth,
        "org.crypto-autoresearcher.consumption": $consume
      } and
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
      .[0].HostConfig.Runtime == "runc" and
      .[0].HostConfig.OomKillDisable == false and
      .[0].HostConfig.Privileged == false and
      .[0].HostConfig.PublishAllPorts == false and
      .[0].HostConfig.PortBindings == {} and
      .[0].HostConfig.VolumeDriver == "" and
      .[0].HostConfig.GroupAdd == null and
      .[0].HostConfig.CgroupParent == "" and
      .[0].HostConfig.Cgroup == "" and
      .[0].HostConfig.Dns == [] and
      .[0].HostConfig.DnsOptions == [] and
      .[0].HostConfig.DnsSearch == [] and
      .[0].HostConfig.ExtraHosts == null and
      .[0].HostConfig.Links == null and
      .[0].HostConfig.Init == null and
      .[0].HostConfig.Sysctls == null and
      .[0].HostConfig.StorageOpt == null and
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
      .[0].HostConfig.MaskedPaths == [
        "/proc/acpi","/proc/asound","/proc/interrupts","/proc/kcore",
        "/proc/keys","/proc/latency_stats","/proc/sched_debug",
        "/proc/scsi","/proc/timer_list","/proc/timer_stats",
        "/sys/devices/virtual/powercap","/sys/firmware"
      ] and
      .[0].HostConfig.ReadonlyPaths == [
        "/proc/bus","/proc/fs","/proc/irq","/proc/sys",
        "/proc/sysrq-trigger"
      ] and
      .[0].Mounts == []
    ' "$path" >/dev/null
}


validate_minimal_ownership() {
  /opt/homebrew/bin/jq -e \
    --arg cid "$CONTAINER_ID" \
    --arg auth "$AUTH_HEAD" \
    --arg consume "$CONSUMPTION_COMMIT" \
    --arg name "$CONTAINER_NAME" \
    '
      length == 1 and
      .[0].Id == $cid and
      .[0].Name == ("/" + $name) and
      .[0].Config.Labels["org.crypto-autoresearcher.authorization"] == $auth and
      .[0].Config.Labels["org.crypto-autoresearcher.consumption"] == $consume
    ' "$1" >/dev/null
}


exact_no_object_receipt() {
  local status="$1"
  local stdout_path="$2"
  local stderr_path="$3"
  local identifier="$4"

  [[ "$status" -eq 1 ]] || return 1
  /usr/bin/printf '[]\n' |
    /usr/bin/cmp -s "$stdout_path" - || return 1
  /usr/bin/printf 'Error: No such object: %s\n' "$identifier" |
    /usr/bin/cmp -s "$stderr_path" -
}


valid_container_id() {
  [[ "${#1}" -eq 64 && "$1" != *[^0-9a-f]* ]]
}


read_exact_container_id_file() {
  local path="$1"
  local expected_bytes="$2"
  local size
  local value

  [[ -f "$path" && ! -L "$path" ]] || return 1
  size=$(/usr/bin/wc -c <"$path" | /usr/bin/awk '{print $1}') ||
    return 1
  [[ "$size" == "$expected_bytes" ]] || return 1
  value="$(<"$path")"
  valid_container_id "$value" || return 1
  EXACT_CONTAINER_ID_VALUE="$value"
}


valid_git_object_id() {
  [[ "${#1}" -eq 40 && "$1" != *[^0-9a-f]* ]]
}


read_exact_loose_ref() {
  local path="$1"
  local size
  local value

  [[ -f "$path" && ! -L "$path" ]] || return 1
  size=$(/usr/bin/wc -c <"$path" | /usr/bin/awk '{print $1}') ||
    return 1
  [[ "$size" == "41" ]] || return 1
  value="$(<"$path")"
  valid_git_object_id "$value" || return 1
  EXACT_GIT_OBJECT_ID_VALUE="$value"
}


observe_loose_result_ref() {
  read_exact_loose_ref "${COMMON_GIT_DIR}/${RESULT_REF}" || return 1
  RESULT_COMMIT="$EXACT_GIT_OBJECT_ID_VALUE"
  RESULT_REF_PRESENT_UNVALIDATED="true"
  CLASSIFICATION="RESULT_PRESENT_UNVALIDATED"
}


observe_loose_consumption_ref() {
  read_exact_loose_ref "${COMMON_GIT_DIR}/${CONSUMPTION_REF}" || return 1
  CONSUMPTION_COMMIT="$EXACT_GIT_OBJECT_ID_VALUE"
  CONSUMPTION_REF_PRESENT_UNVALIDATED="true"
  CLASSIFICATION="CONSUMPTION_PRESENT_UNVALIDATED"
}


verify_container_name_absent() {
  local status
  local stdout_path="${RUN_DIR}/docker-name-cleanup-verify-stdout.log"
  local stderr_path="${RUN_DIR}/docker-name-cleanup-verify-stderr.log"

  docker_control inspect "$CONTAINER_NAME" >"$stdout_path" 2>"$stderr_path"
  status=$?
  /usr/bin/printf '%s\n' "$status" \
    >"${RUN_DIR}/docker-name-cleanup-verify-exit-code.txt" || return 1
  exact_no_object_receipt "$status" "$stdout_path" "$stderr_path" \
    "$CONTAINER_NAME"
}


cleanup_owned_container() {
  local prefix="$1"
  local inspect_path="${RUN_DIR}/${prefix}-cleanup-inspect.json"
  local inspect_status
  local ownership_status="not_observed"
  local cleanup_status
  local verify_status

  [[ "$CONTAINER_OWNED" == "true" && "$CLEANUP_DONE" == "false" ]] ||
    return 0
  docker_control inspect "$CONTAINER_ID" >"$inspect_path" \
    2>"${RUN_DIR}/${prefix}-cleanup-inspect-stderr.log"
  inspect_status=$?
  if [[ "$inspect_status" -eq 0 ]] &&
    validate_minimal_ownership "$inspect_path"; then
    ownership_status="labels_and_returned_create_id"
  else
    ownership_status="returned_create_id_only"
  fi
  /usr/bin/printf '%s\n' "$inspect_status" \
    >"${RUN_DIR}/${prefix}-cleanup-inspect-exit-code.txt" || return 71
  /usr/bin/printf '%s\n' "$ownership_status" \
    >"${RUN_DIR}/${prefix}-cleanup-ownership-basis.txt" || return 71
  if exact_no_object_receipt "$inspect_status" "$inspect_path" \
    "${RUN_DIR}/${prefix}-cleanup-inspect-stderr.log" "$CONTAINER_ID"; then
    : >"${RUN_DIR}/docker-cleanup.log" || return 71
    : >"${RUN_DIR}/docker-cleanup-stderr.log" || return 71
    cleanup_status=0
  else
    [[ "$inspect_status" -eq 0 ]] || return 71
    docker_control rm -f "$CONTAINER_ID" \
      >"${RUN_DIR}/docker-cleanup.log" \
      2>"${RUN_DIR}/docker-cleanup-stderr.log"
    cleanup_status=$?
  fi
  /usr/bin/printf '%s\n' "$cleanup_status" \
    >"${RUN_DIR}/docker-cleanup-exit-code.txt" || return 71
  [[ "$cleanup_status" -eq 0 ]] || return 71
  docker_control inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-cleanup-verify-stdout.log" \
    2>"${RUN_DIR}/docker-cleanup-verify-stderr.log"
  verify_status=$?
  /usr/bin/printf '%s\n' "$verify_status" \
    >"${RUN_DIR}/docker-cleanup-verify-exit-code.txt" || return 71
  exact_no_object_receipt "$verify_status" \
    "${RUN_DIR}/docker-cleanup-verify-stdout.log" \
    "${RUN_DIR}/docker-cleanup-verify-stderr.log" "$CONTAINER_ID" ||
    return 71
  verify_container_name_absent || return 71
  CLEANUP_DONE="true"
  CLEANUP_PROVED="true"
  CONTAINER_OWNED="false"
  return 0
}


recover_pending_container() {
  local inspect_path="${RUN_DIR}/create-pending-recovery-inspect.json"
  local stderr_path="${RUN_DIR}/create-pending-recovery-inspect-stderr.log"
  local status
  local candidate

  [[ "$CREATE_PENDING" == "true" ]] || return 0
  docker_control inspect "$CONTAINER_NAME" >"$inspect_path" 2>"$stderr_path"
  status=$?
  if exact_no_object_receipt "$status" "$inspect_path" "$stderr_path" \
    "$CONTAINER_NAME"; then
    CREATE_PENDING="false"
    CONTAINER_OWNED="false"
    CLEANUP_DONE="true"
    CLEANUP_PROVED="true"
    return 0
  fi
  [[ "$status" -eq 0 ]] || return 71
  candidate=$(
    /opt/homebrew/bin/jq -er \
      --arg name "$CONTAINER_NAME" \
      --arg auth "$AUTH_HEAD" \
      --arg consume "$CONSUMPTION_COMMIT" '
        if length == 1 and
          (.[0].Id |
            type == "string" and
            length == 64 and
            test("^[0-9a-f]{64}\\z")) and
          .[0].Name == ("/" + $name) and
          .[0].Config.Labels == {
            "org.crypto-autoresearcher.authorization": $auth,
            "org.crypto-autoresearcher.consumption": $consume
          }
        then .[0].Id
        else error("pending container ownership mismatch")
        end
      ' "$inspect_path"
  ) || return 71
  valid_container_id "$candidate" || return 71
  CONTAINER_ID="$candidate"
  CONTAINER_OWNED="true"
  CONTAINER_EVER_OWNED="true"
  CREATE_PENDING="false"
  cleanup_owned_container "create-pending-recovery"
}


prove_cleanup_for_seal() {
  if [[ "$CREATE_PENDING" == "true" ]]; then
    recover_pending_container || return 71
  fi
  [[ "$CREATE_PENDING" == "false" ]] || return 71
  if [[ "$CONTAINER_OWNED" == "true" ]]; then
    cleanup_owned_container "seal-gate" || return 71
  fi
  [[ "$CONTAINER_OWNED" == "false" ]] || return 71
  if [[ "$CONTAINER_EVER_OWNED" == "false" ]]; then
    : >"${RUN_DIR}/docker-cleanup.log" || return 71
    : >"${RUN_DIR}/docker-cleanup-stderr.log" || return 71
    /usr/bin/printf '0\n' >"${RUN_DIR}/docker-cleanup-exit-code.txt" ||
      return 71
  fi
  verify_container_name_absent || return 71
  CLEANUP_DONE="true"
  CLEANUP_PROVED="true"
  return 0
}


create_container() {
  local output=""
  local create_status
  local candidate=""
  local cidfile_value=""
  local stdout_valid="false"
  local cidfile_valid="false"
  local cidfile="${RUN_DIR}/docker-create-cid.txt"
  local recovery="${RUN_DIR}/docker-create-recovery-inspect.json"
  local recovery_status

  CONTAINER_SCRIPT=$'set -eu\numask 077\nroot=/tmp/archive\n/usr/bin/mkdir \"$root\"\n/usr/bin/tar --no-same-owner --no-same-permissions -xf - -C \"$root\"\n/usr/bin/printf \"%s  %s\\n\" \"$1\" \"$root/$2\" | /usr/bin/sha256sum -c - >/dev/null\nexec /usr/local/bin/python3 -I -S -P -B \"$root/$2\" \"$root/$3\" \"$root/$4\"'
  CREATE_PENDING="true"
  docker_safe create -i --pull never --platform linux/arm64 \
    --name "$CONTAINER_NAME" --cidfile "$cidfile" \
    --network none --memory 1g --memory-swap 1g --cpus 1 \
    --pids-limit 64 --ulimit nofile=128:128 \
    --ulimit fsize=1048576:1048576 --read-only \
    --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m --shm-size 8m \
    --cap-drop ALL --security-opt no-new-privileges \
    --user 65534:65534 --log-driver none --no-healthcheck \
    --stop-timeout 1 --env HOME=/tmp --env LANG=C --env LC_ALL=C \
    --env PYTHONHASHSEED=0 --env PYTHONDONTWRITEBYTECODE=1 \
    --label "org.crypto-autoresearcher.authorization=${AUTH_HEAD}" \
    --label "org.crypto-autoresearcher.consumption=${CONSUMPTION_COMMIT}" \
    --entrypoint /bin/sh "$IMAGE" \
    -c "$CONTAINER_SCRIPT" sgcp-v12 "$CONTAINER_RUNNER_SHA256_ARG" \
    "$CONTAINER_RUNNER_PATH" "$SOURCE_PATH" "$TEST_PATH" \
    >"${RUN_DIR}/docker-create-stdout.txt" \
    2>"${RUN_DIR}/docker-create-stderr.log"
  create_status=$?
  /usr/bin/printf '%s\n' "$create_status" \
    >"${RUN_DIR}/docker-create-exit-code.txt" || return 71

  if read_exact_container_id_file \
    "${RUN_DIR}/docker-create-stdout.txt" 65; then
    output="$EXACT_CONTAINER_ID_VALUE"
    stdout_valid="true"
  fi
  if read_exact_container_id_file "$cidfile" 64; then
    cidfile_value="$EXACT_CONTAINER_ID_VALUE"
    cidfile_valid="true"
  fi
  if [[ "$create_status" -eq 0 ]] &&
    [[ "$stdout_valid" == "true" && "$cidfile_valid" == "true" ]] &&
    [[ "$cidfile_value" == "$output" ]]; then
    candidate="$cidfile_value"
  else
    docker_safe inspect "$CONTAINER_NAME" >"$recovery" \
      2>"${RUN_DIR}/docker-create-recovery-inspect-stderr.log"
    recovery_status=$?
    /usr/bin/printf '%s\n' "$recovery_status" \
      >"${RUN_DIR}/docker-create-recovery-inspect-exit-code.txt" || return 71
    if [[ "$recovery_status" -eq 0 ]] &&
      /opt/homebrew/bin/jq -e \
        --arg name "$CONTAINER_NAME" \
        --arg auth "$AUTH_HEAD" \
        --arg consume "$CONSUMPTION_COMMIT" '
          length == 1 and
          (.[0].Id |
            type == "string" and
            length == 64 and
            test("^[0-9a-f]{64}\\z")) and
          .[0].Name == ("/" + $name) and
          .[0].Config.Labels == {
            "org.crypto-autoresearcher.authorization": $auth,
            "org.crypto-autoresearcher.consumption": $consume
          }
        ' "$recovery" >/dev/null; then
      candidate=$(/opt/homebrew/bin/jq -r '.[0].Id' "$recovery") ||
        return 71
    fi
  fi

  if [[ -n "$candidate" ]]; then
    CONTAINER_ID="$candidate"
    CONTAINER_OWNED="true"
    CONTAINER_EVER_OWNED="true"
    CREATE_PENDING="false"
    /usr/bin/printf '%s\n' "$CONTAINER_ID" \
      >"${RUN_DIR}/container-id.txt" || return 71
  fi

  if [[ "$create_status" -ne 0 || -z "$candidate" ||
    "$output" != "$candidate" || ! -f "$cidfile" ||
    "$cidfile_value" != "$candidate" ]]; then
    if [[ "$CREATE_PENDING" == "true" ]]; then
      recover_pending_container || return 71
    fi
    cleanup_owned_container "create-command-rejection" || return 71
    return 71
  fi

  docker_safe inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-inspect-pre.json" \
    2>"${RUN_DIR}/docker-inspect-pre-stderr.log" || {
      cleanup_owned_container "create-rejection"
      return 71
    }
  validate_inspect "${RUN_DIR}/docker-inspect-pre.json" || {
    cleanup_owned_container "create-rejection"
    return 71
  }
  return 0
}


run_container() {
  local pipeline_script
  local wrapper_status

  pipeline_script=$'set -u\nsetopt pipefail\nrepo=\"$1\"\ncommit=\"$2\"\nrunner=\"$3\"\nsource=\"$4\"\ntest=\"$5\"\ninput_tar=\"$6\"\narchive_stderr=\"$7\"\ntee_stderr=\"$8\"\ncid=\"$9\"\ncontainer_stderr=\"${10}\"\npipeline_status=\"${11}\"\n/opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s /usr/bin/env -i HOME=/tmp TMPDIR=/tmp LANG=C LC_ALL=C PATH=/usr/bin:/bin:/usr/sbin:/sbin GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_OPTIONAL_LOCKS=0 GIT_NO_REPLACE_OBJECTS=1 /usr/bin/git -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.attributesFile=/dev/null -C \"$repo\" archive --format=tar \"$commit\" \"$runner\" \"$source\" \"$test\" 2>\"$archive_stderr\" | /usr/bin/tee \"$input_tar\" 2>\"$tee_stderr\" | /bin/zsh -f -c '\\''/opt/homebrew/bin/docker start -a -i \"$1\" 2>\"$2\"'\\'' -- \"$cid\" \"$container_stderr\"\nstatuses=(\"${pipestatus[@]}\")\n/usr/bin/printf \"%s\\n\" \"${statuses[@]}\" >\"$pipeline_status\" || exit 76\n[[ \"${statuses[1]}\" -eq 0 && \"${statuses[2]}\" -eq 0 ]] || exit 74\nexit \"${statuses[3]}\"'
  /bin/zsh -f -c '
    ulimit -f 4096
    [[ "$(ulimit -f)" == "4096" ]] || exit 75
    /usr/bin/time -lp -o "$1" \
      /opt/homebrew/bin/gtimeout --verbose --signal=TERM --kill-after=5s 180s \
        /bin/zsh -f -c "$2" -- \
          "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" "${11}" "${12}" "${13}" \
        >"${14}" 2>"${15}"
  ' -- \
    "${RUN_DIR}/resource.txt" "$pipeline_script" "$REPO" "$AUTH_HEAD" \
    "$CONTAINER_RUNNER_PATH" "$SOURCE_PATH" "$TEST_PATH" \
    "${RUN_DIR}/input.tar" "${RUN_DIR}/git-archive-stderr.log" \
    "${RUN_DIR}/tee-stderr.log" "$CONTAINER_ID" "${RUN_DIR}/stderr.log" \
    "${RUN_DIR}/pipeline-status.txt" "${RUN_DIR}/stdout.json" \
    "${RUN_DIR}/timeout-controller.log"
  wrapper_status=$?
  /usr/bin/printf '%s\n' "$wrapper_status" \
    >"${RUN_DIR}/pipeline-wrapper-exit-code.txt" || return 71
  if [[ "$wrapper_status" -eq 124 || "$wrapper_status" -eq 137 ]] &&
    /usr/bin/grep -q '^timeout: sending signal ' \
      "${RUN_DIR}/timeout-controller.log"; then
    /usr/bin/printf '%s\n' "true" >"${RUN_DIR}/timeout-observed.txt" ||
      return 71
  else
    /usr/bin/printf '%s\n' "false" >"${RUN_DIR}/timeout-observed.txt" ||
      return 71
  fi
  return 0
}


post_inspect_and_cleanup() {
  local oom
  local state_exit
  local inspect_status=0

  docker_safe inspect "$CONTAINER_ID" \
    >"${RUN_DIR}/docker-inspect-post.json" \
    2>"${RUN_DIR}/docker-inspect-post-stderr.log" || inspect_status=71
  if [[ "$inspect_status" -eq 0 ]]; then
    validate_inspect "${RUN_DIR}/docker-inspect-post.json" ||
      inspect_status=71
  fi
  if [[ "$inspect_status" -eq 0 ]]; then
    oom=$(/opt/homebrew/bin/jq -r '.[0].State.OOMKilled' \
      "${RUN_DIR}/docker-inspect-post.json") || inspect_status=71
    state_exit=$(/opt/homebrew/bin/jq -r '.[0].State.ExitCode' \
      "${RUN_DIR}/docker-inspect-post.json") || inspect_status=71
  fi
  if [[ "$inspect_status" -eq 0 ]]; then
    /usr/bin/printf '%s\n' "$oom" >"${RUN_DIR}/oom-killed.txt" ||
      inspect_status=71
    /usr/bin/printf '%s\n' "$state_exit" \
      >"${RUN_DIR}/container-state-exit-code.txt" || inspect_status=71
  fi
  cleanup_owned_container "post-run" || return 71
  return "$inspect_status"
}


require_canonical_stdout_json() {
  local line_count

  line_count=$(/usr/bin/wc -l <"${RUN_DIR}/stdout.json") || return 1
  [[ "$line_count" -eq 1 ]] || return 1
  /opt/homebrew/bin/jq -cS . "${RUN_DIR}/stdout.json" \
    >"${RUN_DIR}/stdout-canonical.json" || return 1
  /usr/bin/cmp -s "${RUN_DIR}/stdout.json" \
    "${RUN_DIR}/stdout-canonical.json"
}


validate_valid_result() {
  [[ "$(<"${RUN_DIR}/pipeline-status.txt")" == $'0\n0\n0' ]] || return 1
  require_canonical_stdout_json || return 1
  [[ ! -s "${RUN_DIR}/stderr.log" ]] || return 1
  /opt/homebrew/bin/jq -e -s \
    '
      def uint:
        type == "number" and . >= 0 and . == floor;
      length == 1 and
      (.[0] | keys) == [
        "classification","details","errors","events","expected_failures",
        "failures","runtime_after","runtime_before","skipped",
        "tests_started","unexpected_successes"
      ] and
      .[0].classification == "VALID_DEVELOPMENT_TEST" and
      .[0].details == [] and
      .[0].errors == 0 and .[0].failures == 0 and
      .[0].expected_failures == 0 and .[0].skipped == 0 and
      .[0].unexpected_successes == 0 and .[0].tests_started == 5 and
      .[0].events == [
        {"id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_scalar_congruence_and_least_slope_selection","outcome":"ok"},
        {"id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_witnesses_fibers_representatives_diagnostics_and_ops","outcome":"ok"},
        {"id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_every_reachable_domain_error_and_charged_prefix","outcome":"ok"},
        {"id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_first_error_precedence","outcome":"ok"},
        {"id":"test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_public_results_and_inputs_are_immutable","outcome":"ok"}
      ] and
      ([.[0].runtime_before, .[0].runtime_after] |
        all(
          (keys | sort) == [
            "cpu_stat","memory_current_bytes","memory_peak_bytes",
            "pids_current","pids_peak"
          ] and
          (.memory_current_bytes | uint and . <= 1073741824) and
          (.memory_peak_bytes | uint and . <= 1073741824) and
          (.pids_current | uint and . >= 1 and . <= 64) and
          (.pids_peak | uint and . >= 1 and . <= 64) and
          (.cpu_stat | keys | sort) == [
            "burst_usec","nice_usec","nr_bursts","nr_periods",
            "nr_throttled","system_usec","throttled_usec",
            "usage_usec","user_usec"
          ] and
          ([.cpu_stat[]] | all(uint))
        )
      ) and
      .[0].runtime_after.memory_peak_bytes >=
        .[0].runtime_before.memory_peak_bytes and
      .[0].runtime_after.cpu_stat.usage_usec >=
        .[0].runtime_before.cpu_stat.usage_usec
    ' "${RUN_DIR}/stdout.json" >/dev/null
}


classify_result() {
  local wrapper
  local state_exit
  local state_status
  local timeout
  local oom

  wrapper="$(<"${RUN_DIR}/pipeline-wrapper-exit-code.txt")"
  state_exit="$(<"${RUN_DIR}/container-state-exit-code.txt")"
  timeout="$(<"${RUN_DIR}/timeout-observed.txt")"
  oom="$(<"${RUN_DIR}/oom-killed.txt")"
  state_status=$(/opt/homebrew/bin/jq -r '.[0].State.Status' \
    "${RUN_DIR}/docker-inspect-post.json") || return 71

  if [[ "$oom" == "true" ]]; then
    CLASSIFICATION="RESOURCE_EXHAUSTION"
    return 137
  fi
  if [[ "$timeout" == "true" ]]; then
    CLASSIFICATION="TIMEOUT"
    return 124
  fi
  [[ "$state_status" == "exited" ]] || return 71
  if [[ "$wrapper" == "0" && "$state_exit" == "0" ]] &&
    validate_valid_result; then
    CLASSIFICATION="VALID_DEVELOPMENT_TEST"
    return 0
  fi
  if [[ "$wrapper" == "1" && "$state_exit" == "1" &&
    "$(<"${RUN_DIR}/pipeline-status.txt")" == $'0\n0\n1' ]] &&
    require_canonical_stdout_json &&
    /opt/homebrew/bin/jq -e -s \
      'length == 1 and .[0].classification == "TEST_FAILURE"' \
      "${RUN_DIR}/stdout.json" >/dev/null 2>&1; then
    CLASSIFICATION="TEST_FAILURE"
    return 1
  fi
  if [[ "$wrapper" == "70" && "$state_exit" == "70" &&
    "$(<"${RUN_DIR}/pipeline-status.txt")" == $'0\n0\n70' ]] &&
    require_canonical_stdout_json &&
    /opt/homebrew/bin/jq -e -s \
      'length == 1 and .[0].classification == "PREFLIGHT_FAILURE"' \
      "${RUN_DIR}/stdout.json" >/dev/null 2>&1; then
    CLASSIFICATION="PREFLIGHT_FAILURE"
    return 70
  fi
  CLASSIFICATION="INFRASTRUCTURE_FAILURE"
  return 71
}


recover_consumption_state() {
  local status
  local observed

  git_safe symbolic-ref -q "$CONSUMPTION_REF" >/dev/null 2>&1
  [[ "$?" -eq 1 ]] || return 1
  git_safe show-ref --verify --quiet "$CONSUMPTION_REF"
  status=$?
  if [[ "$status" -eq 1 ]]; then
    return 1
  fi
  [[ "$status" -eq 0 ]] || return 1
  observed=$(git_safe rev-parse "$CONSUMPTION_REF") || return 1
  valid_git_object_id "$observed" || return 1
  CONSUMPTION_COMMIT="$observed"
  CONSUMPTION_REF_CREATED="true"
}


recover_result_state() {
  local status
  local observed
  local topology
  local tree_signature
  local manifest="${RUN_DIR}/artifact-manifest.sha256"
  local receipt="${RUN_DIR}/run-receipt.json"
  local seal="${RUN_DIR}/result-seal.json"
  local artifact_count
  local manifest_hash
  local receipt_hash
  local expected_json
  local validation
  local recovered_classification

  [[ "$CONSUMPTION_REF_CREATED" == "true" ]] || return 1
  git_safe symbolic-ref -q "$RESULT_REF" >/dev/null 2>&1
  [[ "$?" -eq 1 ]] || return 1
  git_safe show-ref --verify --quiet "$RESULT_REF"
  status=$?
  [[ "$status" -eq 0 ]] || return 1
  observed=$(git_safe rev-parse "$RESULT_REF") || return 1
  valid_git_object_id "$observed" || return 1
  topology=$(git_safe rev-list --parents -n 1 "$observed") || return 1
  [[ "$topology" == "${observed} ${CONSUMPTION_COMMIT}" ]] || return 1
  tree_signature=$(
    git_safe ls-tree "$observed" |
      /usr/bin/awk '{print $1, $2, $4}'
  ) || return 1
  [[ "$tree_signature" ==
    $'100644 blob artifact-manifest.sha256\n100644 blob result-seal.json' ]] ||
    return 1
  [[ "$(sha256_commit_path "$observed" "artifact-manifest.sha256")" ==
    "$(sha256_file "$manifest")" ]] || return 1
  [[ "$(sha256_commit_path "$observed" "result-seal.json")" ==
    "$(sha256_file "$seal")" ]] || return 1
  require_canonical_json_line "$receipt" || return 1
  require_canonical_json_line "$seal" || return 1

  artifact_count=$(/usr/bin/wc -l <"$manifest" |
    /usr/bin/awk '{print $1}') || return 1
  /usr/bin/printf '%s\n' "$artifact_count" |
    /usr/bin/grep -Eq '^[1-9][0-9]*$' || return 1
  manifest_hash=$(sha256_file "$manifest") || return 1
  receipt_hash=$(sha256_file "$receipt") || return 1
  expected_json=$(
    /opt/homebrew/bin/jq -cn \
      --argjson artifact_count "$artifact_count" \
      --arg artifact_manifest_sha256 "$manifest_hash" \
      --arg authorization_head "$AUTH_HEAD" \
      --arg container_name "$CONTAINER_NAME" \
      --arg consumption_ref "$CONSUMPTION_REF" \
      --arg protocol_commit "$PROTOCOL_COMMIT_ARG" \
      --arg result_ref "$RESULT_REF" \
      --arg run_id "$RUN_ID" \
      --arg run_receipt_sha256 "$receipt_hash" \
      '$ARGS.named'
  ) || return 1
  validation=$(
    /opt/homebrew/bin/jq -e -n \
      --argjson expected "$expected_json" \
      --slurpfile receipt "$receipt" \
      --slurpfile seal "$seal" \
      -f "${RUN_DIR}/evidence-input/result-validator.jq"
  ) || return 1
  [[ "$validation" == "true" ]] || return 1
  recovered_classification=$(
    /opt/homebrew/bin/jq -er '.classification' "$seal"
  ) || return 1
  case "$recovered_classification" in
    VALID_DEVELOPMENT_TEST | TEST_FAILURE | PREFLIGHT_FAILURE | \
      INFRASTRUCTURE_FAILURE | TIMEOUT | RESOURCE_EXHAUSTION) ;;
    *) return 1 ;;
  esac

  RESULT_REF_CREATED="true"
  RESULT_COMMIT="$observed"
  CLASSIFICATION="$recovered_classification"
}


create_result_seal() {
  local manifest="${RUN_DIR}/artifact-manifest.sha256"
  local receipt="${RUN_DIR}/run-receipt.json"
  local seal="${RUN_DIR}/result-seal.json"
  local artifact_count
  local manifest_hash
  local receipt_hash
  local expected_json
  local validation
  local manifest_blob
  local seal_blob
  local result_tree
  local result_commit
  local zero="0000000000000000000000000000000000000000"

  artifact_count=$(/usr/bin/wc -l <"$manifest" |
    /usr/bin/awk '{print $1}') || return 1
  /usr/bin/printf '%s\n' "$artifact_count" |
    /usr/bin/grep -Eq '^[1-9][0-9]*$' || return 1
  manifest_hash=$(sha256_file "$manifest") || return 1
  receipt_hash=$(sha256_file "$receipt") || return 1
  /usr/bin/printf '%s\n' "$manifest_hash" |
    /usr/bin/grep -Eq '^[0-9a-f]{64}$' || return 1
  /usr/bin/printf '%s\n' "$receipt_hash" |
    /usr/bin/grep -Eq '^[0-9a-f]{64}$' || return 1

  /opt/homebrew/bin/jq -cnS \
    --argjson artifact_count "$artifact_count" \
    --arg artifact_manifest_sha256 "$manifest_hash" \
    --arg authorization_head "$AUTH_HEAD" \
    --arg classification "$CLASSIFICATION" \
    --arg consumption_commit "$CONSUMPTION_COMMIT" \
    --arg consumption_ref "$CONSUMPTION_REF" \
    --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
    --arg result_ref "$RESULT_REF" \
    --arg run_id "$RUN_ID" \
    --arg run_receipt_sha256 "$receipt_hash" \
    --arg sealed_at_utc "$FINISHED_AT" \
    '{
      artifact_count: $artifact_count,
      artifact_manifest_sha256: $artifact_manifest_sha256,
      authorization_head: $authorization_head,
      classification: $classification,
      consumption_commit: $consumption_commit,
      consumption_ref: $consumption_ref,
      experiment_id: $experiment_id,
      result_ref: $result_ref,
      run_id: $run_id,
      run_receipt_sha256: $run_receipt_sha256,
      sealed_at_utc: $sealed_at_utc
    }' >"$seal" || return 1
  require_canonical_json_line "$seal" || return 1

  expected_json=$(
    /opt/homebrew/bin/jq -cn \
      --argjson artifact_count "$artifact_count" \
      --arg artifact_manifest_sha256 "$manifest_hash" \
      --arg authorization_head "$AUTH_HEAD" \
      --arg container_name "$CONTAINER_NAME" \
      --arg consumption_ref "$CONSUMPTION_REF" \
      --arg protocol_commit "$PROTOCOL_COMMIT_ARG" \
      --arg result_ref "$RESULT_REF" \
      --arg run_id "$RUN_ID" \
      --arg run_receipt_sha256 "$receipt_hash" \
      '$ARGS.named'
  ) || return 1
  validation=$(
    /opt/homebrew/bin/jq -e -n \
      --argjson expected "$expected_json" \
      --slurpfile receipt "$receipt" \
      --slurpfile seal "$seal" \
      -f "${RUN_DIR}/evidence-input/result-validator.jq"
  ) || return 1
  [[ "$validation" == "true" ]] || return 1

  manifest_blob=$(git_safe hash-object -w --no-filters "$manifest") ||
    return 1
  seal_blob=$(git_safe hash-object -w --no-filters "$seal") || return 1
  result_tree=$(
    {
      /usr/bin/printf '100644 blob %s\tartifact-manifest.sha256\n' \
        "$manifest_blob"
      /usr/bin/printf '100644 blob %s\tresult-seal.json\n' "$seal_blob"
    } | git_safe mktree
  ) || return 1
  result_commit=$(
    /usr/bin/printf 'SGCP development test V12 immutable result seal\n' |
      git_safe_ident commit-tree "$result_tree" -p "$CONSUMPTION_COMMIT"
  ) || return 1
  [[ "$(git_safe rev-list --parents -n 1 "$result_commit")" ==
    "${result_commit} ${CONSUMPTION_COMMIT}" ]] || return 1
  [[ "$(git_safe rev-parse "${result_commit}^{tree}")" == "$result_tree" ]] ||
    return 1
  [[ "$(sha256_commit_path "$result_commit" "artifact-manifest.sha256")" ==
    "$manifest_hash" ]] || return 1
  [[ "$(sha256_commit_path "$result_commit" "result-seal.json")" ==
    "$(sha256_file "$seal")" ]] || return 1
  git_safe update-ref --no-deref --create-reflog -m \
    "seal SGCP development test V12 result" \
    "$RESULT_REF" "$result_commit" "$zero" || return 1
  recover_result_state
}


prepare_and_seal_result() {
  prove_cleanup_for_seal || return 1
  [[ "$CLEANUP_PROVED" == "true" && "$CLEANUP_DONE" == "true" &&
    "$CONTAINER_OWNED" == "false" ]] || return 1
  inventory_capture "final" || return 1
  inventory_empty_without_output || return 1
  write_run_receipt || return 1
  if [[ "$CLASSIFICATION" == "VALID_DEVELOPMENT_TEST" ]]; then
    validate_valid_artifact_set || return 1
  fi
  generate_artifact_manifest || return 1
  create_result_seal
}


emergency_cleanup() {
  if [[ "$INITIALIZED" == "true" && "$CREATE_PENDING" == "true" ]]; then
    RECOVERY_MODE="true"
    recover_pending_container >/dev/null 2>&1
    RECOVERY_MODE="false"
  fi
  if [[ "$INITIALIZED" == "true" && "$CONTAINER_OWNED" == "true" &&
    "$CLEANUP_DONE" == "false" ]]; then
    RECOVERY_MODE="true"
    cleanup_owned_container "exit-fallback" >/dev/null 2>&1
    RECOVERY_MODE="false"
  fi
}


handle_host_signal() {
  trap - TERM INT HUP
  emergency_cleanup
  if observe_loose_result_ref >/dev/null 2>&1; then
    exit 76
  fi
  if [[ "$CONSUMPTION_REF_CREATED" == "false" ]] &&
    observe_loose_consumption_ref >/dev/null 2>&1; then
    exit 77
  fi
  if [[ "$CONSUMPTION_REF_CREATED" == "true" ]]; then
    CLASSIFICATION="INCOMPLETE_INFRASTRUCTURE_FAILURE"
    exit 75
  fi
  CLASSIFICATION="INFRASTRUCTURE_FAILURE"
  exit 71
}


trap emergency_cleanup EXIT
trap handle_host_signal TERM INT HUP


main() {
  local result_status

  preclaim_main || return $?
  validate_authorization || {
    record_failure "PREFLIGHT_FAILURE" "authorization package rejected" 70
    return $?
  }
  consume_authorization || {
    record_failure "INFRASTRUCTURE_FAILURE" "durable consumption failed" 71
    return $?
  }
  inventory_capture "pre-execution" || {
    record_failure "INFRASTRUCTURE_FAILURE" "pre-execution inventory rejected" 71
    return $?
  }
  create_container || {
    record_failure "INFRASTRUCTURE_FAILURE" "container creation rejected" 71
    return $?
  }
  run_container || return $?
  post_inspect_and_cleanup || {
    record_failure "INFRASTRUCTURE_FAILURE" "post-run inspect or cleanup failed" 71
    return $?
  }
  classify_result
  result_status=$?
  inventory_capture "post-execution" || {
    CLASSIFICATION="INFRASTRUCTURE_FAILURE"
    return 71
  }
  return "$result_status"
}


main
typeset -g MAIN_STATUS=$?
if [[ "$INITIALIZED" == "true" ]]; then
  emergency_cleanup
  recover_consumption_state >/dev/null 2>&1
  recover_result_state >/dev/null 2>&1
  if [[ "$CONSUMPTION_REF_CREATED" == "true" &&
    "$RESULT_REF_CREATED" == "false" ]]; then
    prepare_and_seal_result || CLASSIFICATION="INCOMPLETE_INFRASTRUCTURE_FAILURE"
  elif [[ "$CONSUMPTION_REF_CREATED" == "false" ]]; then
    CLASSIFICATION="INFRASTRUCTURE_FAILURE"
  fi
  recover_result_state >/dev/null 2>&1
fi

if [[ "$CONSUMPTION_REF_CREATED" == "true" &&
  "$RESULT_REF_CREATED" == "false" ]]; then
  if ! observe_loose_result_ref >/dev/null 2>&1; then
    CLASSIFICATION="INCOMPLETE_INFRASTRUCTURE_FAILURE"
  fi
elif [[ "$CONSUMPTION_REF_CREATED" == "false" ]] &&
  observe_loose_consumption_ref >/dev/null 2>&1; then
  CLASSIFICATION="CONSUMPTION_PRESENT_UNVALIDATED"
fi

case "$CLASSIFICATION" in
  VALID_DEVELOPMENT_TEST) exit 0 ;;
  TEST_FAILURE) exit 1 ;;
  PREFLIGHT_FAILURE) exit 70 ;;
  INFRASTRUCTURE_FAILURE) exit 71 ;;
  INCOMPLETE_INFRASTRUCTURE_FAILURE) exit 75 ;;
  RESULT_PRESENT_UNVALIDATED) exit 76 ;;
  CONSUMPTION_PRESENT_UNVALIDATED) exit 77 ;;
  TIMEOUT) exit 124 ;;
  RESOURCE_EXHAUSTION) exit 137 ;;
  *) exit "$MAIN_STATUS" ;;
esac
