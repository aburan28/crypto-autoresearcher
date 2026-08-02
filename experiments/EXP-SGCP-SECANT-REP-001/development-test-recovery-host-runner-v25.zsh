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
readonly HOST_SHA256_ARG="${5-}"
readonly AUTH_VALIDATOR_SHA256_ARG="${6-}"
readonly RESULT_VALIDATOR_SHA256_ARG="${7-}"
readonly SOURCE_MANIFEST_SHA256_ARG="${8-}"

readonly REPO="/Users/adamburan/crypto-autoresearcher-worktrees/recursive-s3-quotient-v25"
readonly BRANCH_REF="refs/heads/codex/recursive-s3-quotient-v25"
readonly COMMON_GIT_DIR="/Volumes/Volume/crypto-autoresearcher/.git"
readonly WORKTREE_GIT_DIR="/Volumes/Volume/crypto-autoresearcher/.git/worktrees/recursive-s3-quotient-v25"
readonly BASE_COMMIT="eb8e263e15bf623744c446a98b94d8365dbc820a"
readonly BASE_TREE="1c1d9f62c015c6d0ae0aaf31cdf000b256bac87f"
readonly EXP="experiments/EXP-SGCP-SECANT-REP-001"
readonly PROTOCOL_PATH="${EXP}/development-test-recovery-protocol-v25.json"
readonly HOST_PATH="${EXP}/development-test-recovery-host-runner-v25.zsh"
readonly AUTH_VALIDATOR_PATH="${EXP}/development-test-recovery-authorization-validator-v25.jq"
readonly RESULT_VALIDATOR_PATH="${EXP}/development-test-recovery-result-validator-v25.jq"
readonly SOURCE_MANIFEST_PATH="${EXP}/development-test-recovery-source-manifest-v25.json"
readonly THEORY_PATH="${EXP}/development-test-recovery-theory-review-v25.json"
readonly ACCOUNTING_PATH="${EXP}/development-test-recovery-accounting-review-v25.json"
readonly RED_TEAM_PATH="${EXP}/development-test-recovery-red-team-review-v25.json"
readonly DECISION_PATH="${EXP}/development-test-recovery-decision-v25.json"

readonly SOURCE_REPO="/Users/adamburan/crypto-autoresearcher-worktrees/recursive-s3-quotient-v23"
readonly SOURCE_RUN="${SOURCE_REPO}/${EXP}/DEV-SGCP-SECANT-PURE-CORE-V23"
readonly SOURCE_BRANCH_REF="refs/heads/codex/recursive-s3-quotient-v23"
readonly SOURCE_PROTOCOL_COMMIT="217a9ca71416c1f0a034ae7ef50583a9201f1409"
readonly SOURCE_PROTOCOL_SHA256="0b76513583c74153ed1fb1090fa4f0f631909a9808dc94f0efb419162c41ee15"
readonly SOURCE_AUTH_COMMIT="a655f7fb13e400d71819448c158413ddaf3810eb"
readonly SOURCE_CONSUMPTION_COMMIT="eb6267b128a410bbd6cb0f25683b14a4872d398e"
readonly SOURCE_CONSUMPTION_REF="refs/crypto-autoresearcher/consumptions/EXP-SGCP-SECANT-REP-001-development-test-v23"
readonly SOURCE_RESULT_REF="refs/crypto-autoresearcher/results/EXP-SGCP-SECANT-REP-001-development-test-v23"
readonly SOURCE_RUN_ID="DEV-SGCP-SECANT-PURE-CORE-V23"
readonly SOURCE_STARTED_AT="2026-07-29T17:32:12Z"
readonly SOURCE_STDOUT_SHA256="191f1f26ea73d8eeda885bbe61e8d49468f9e8559851ec61272484be0ff6d018"

readonly RECOVERY_ID="RECOVERY-SGCP-SECANT-V23-V25"
readonly RECOVERY_DIR="${REPO}/${EXP}/${RECOVERY_ID}"
readonly RECOVERY_CONSUMPTION_REF="refs/crypto-autoresearcher/recovery-consumptions/EXP-SGCP-SECANT-REP-001-v23-v25"
readonly RECOVERY_RESULT_REF="refs/crypto-autoresearcher/recovery-results/EXP-SGCP-SECANT-REP-001-v23-v25"
readonly CONTAINER_ID="22f6bbf23ede11686f8a99a9e116ac38cfaf5f22e6602315bfa367ed5af295d2"
readonly CONTAINER_NAME="sgcp-v23-217a9ca71416c1f0a034ae7ef50583a9201f1409"
readonly IMAGE_ID="sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0"
readonly CONTAINER_RUNNER_SHA256="8ab5ae9c6495a430badcb803956cca1a02593a510a0b1def5e2c5d065d3e5cf5"
readonly CONTAINER_RUNNER_PATH="${EXP}/development-test-container-runner-v3.py"
readonly SOURCE_PATH="${EXP}/src/sgcp_secant_math_core.py"
readonly TEST_PATH="${EXP}/tests/test_sgcp_secant_math_core.py"
readonly CONTAINER_SCRIPT=$'set -eu\numask 077\nroot=/tmp/archive\n/usr/bin/mkdir "$root"\n/usr/bin/tar --no-same-owner --no-same-permissions -xf - -C "$root"\n/usr/bin/printf "%s  %s\\n" "$1" "$root/$2" | /usr/bin/sha256sum -c - >/dev/null\nexec /usr/local/bin/python3 -I -S -P -B "$root/$2" "$root/$3" "$root/$4"'
readonly ZERO_SHA1="0000000000000000000000000000000000000000"

typeset -g RECOVERY_CONSUMPTION_COMMIT="ABSENT"
typeset -g RECOVERED_AT="ABSENT"


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


sha256_file() {
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}


sha256_commit_path() {
  git_safe show "${1}:${2}" |
    /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}'
}


raw_delta() {
  git_safe diff-tree --raw --no-abbrev --no-commit-id -r "$1" |
    /usr/bin/awk '{print $1, $2, $5, $6}'
}


require_canonical_json_line() {
  local path="$1"
  local canonical
  local bytes

  [[ -f "$path" && ! -L "$path" ]] || return 1
  bytes=$(/usr/bin/wc -c <"$path" | /usr/bin/awk '{print $1}') || return 1
  [[ "$bytes" -gt 1 ]] || return 1
  canonical=$(
    /opt/homebrew/bin/jq -ceS \
      'walk(if type == "number" then . + 0 else . end)' "$path"
  ) || return 1
  /usr/bin/printf '%s\n' "$canonical" | /usr/bin/cmp -s "$path" -
}


exact_text() {
  /usr/bin/printf '%s' "$2" | /usr/bin/cmp -s "$1" -
}


docker_safe() {
  /opt/homebrew/bin/gtimeout --signal=TERM --kill-after=5s 30s \
    /opt/homebrew/bin/docker "$@"
}


verify_physical_directory() {
  local path="$1"
  local physical

  [[ -d "$path" && ! -L "$path" ]] || return 1
  physical=$(cd -q -- "$path" && pwd -P) || return 1
  [[ "$physical" == "$path" ]]
}


verify_tool() {
  [[ "$(sha256_file "$1")" == "$2" ]]
}


verify_tools() {
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
    verify_tool /bin/chmod \
      ce1db41c1e8a607749097ec27fd59e1edf92db9008689242936e1fa3758cae1a &&
    verify_tool /usr/bin/printf \
      f2a76beee50f16a1193244519ecfad592b3af0623276b41c088c0ef8650c05f7 &&
    verify_tool /usr/bin/shasum \
      0812595f981a26f813d98dc380af14d4af427626c9339eda29eb849ae13de1e3 &&
    verify_tool /usr/bin/awk \
      3868b14602a4851218210ae1b08732fbdee703ac2c1e2d1898272b42fd33151a &&
    verify_tool /usr/bin/find \
      05aa84ee15d95122cfa3de6a132ace019eb78b27da57534b5d555719c8380f7b &&
    verify_tool /usr/bin/sort \
      a61f82d2598a7a5b9cc273e2426b8c19c532eb72963f34dc97c9cd3d1210486f &&
    verify_tool /usr/bin/stat \
      a3119dde345aa860c2f2e293ecd5f9f3db450d2570343e3319838ac154617b65 &&
    verify_tool /usr/bin/wc \
      32f22e2b385cbc5250c5cc9a11465f5afa74c024724040f47d9edb71ce429e1a &&
    verify_tool /usr/bin/cmp \
      bf0111a82ee28deeb99a83eaee6f0829a743e09dcf8193ebd49b4c4190ad2457 &&
    verify_tool /opt/homebrew/bin/jq \
      e0a718e60bd1098fc134b354da3821a96d4a7510a15465ff64669b04349fc37c &&
    verify_tool /opt/homebrew/bin/gtimeout \
      c0572ac780194a47daa9af4a6a8ec17f355c79fa30e852c1d58206119f8fcdd3 &&
    verify_tool /opt/homebrew/bin/docker \
      5ceb5704cfdf26acc8ff5e47727e58b4360bb6ecc825642de04121e61cf44c06
}


verify_ref_absent() {
  local ref="$1"
  local path
  local output
  local status

  path=$(git_safe rev-parse --git-path "$ref") || return 1
  [[ ! -e "$path" && ! -L "$path" ]] || return 1
  output=$(git_safe show-ref --verify --quiet "$ref" 2>&1)
  status=$?
  [[ "$status" -eq 1 && -z "$output" ]]
}


verify_direct_ref_value() {
  local ref="$1"
  local expected="$2"
  local observed

  observed=$(git_safe for-each-ref \
    --format='%(objectname)%09%(symref)' "$ref") || return 1
  [[ "$observed" == "${expected}"$'\t' ]]
}


preclaim() {
  local expected_p_delta
  local expected_a_delta
  local replacements
  local grafts
  local info_attributes
  local config_output
  local config_status

  [[ "$MODE" == "launch" ]] || return 70
  verify_tools || return 70
  [[ "${#AUTH_HEAD}" -eq 40 && "$AUTH_HEAD" != *[^0-9a-f]* ]] || return 70
  [[ "${#PROTOCOL_COMMIT_ARG}" -eq 40 &&
    "$PROTOCOL_COMMIT_ARG" != *[^0-9a-f]* ]] || return 70
  for digest in \
    "$PROTOCOL_SHA256_ARG" \
    "$HOST_SHA256_ARG" \
    "$AUTH_VALIDATOR_SHA256_ARG" \
    "$RESULT_VALIDATOR_SHA256_ARG" \
    "$SOURCE_MANIFEST_SHA256_ARG"
  do
    [[ "${#digest}" -eq 64 && "$digest" != *[^0-9a-f]* ]] || return 70
  done

  verify_physical_directory "$REPO" || return 70
  verify_physical_directory "${REPO}/experiments" || return 70
  verify_physical_directory "${REPO}/${EXP}" || return 70
  verify_physical_directory "$SOURCE_REPO" || return 70
  verify_physical_directory "$SOURCE_RUN" || return 70
  [[ "$(git_safe rev-parse --git-dir)" == "$WORKTREE_GIT_DIR" ]] || return 70
  [[ "$(git_safe rev-parse --git-common-dir)" == "$COMMON_GIT_DIR" ]] ||
    return 70
  [[ "$(git_safe symbolic-ref -q HEAD)" == "$BRANCH_REF" ]] || return 70
  [[ "$(git_safe rev-parse HEAD)" == "$AUTH_HEAD" ]] || return 70
  [[ "$(git_safe rev-list --parents -n 1 "$PROTOCOL_COMMIT_ARG")" ==
    "${PROTOCOL_COMMIT_ARG} ${BASE_COMMIT}" ]] || return 70
  [[ "$(git_safe rev-parse "${BASE_COMMIT}^{tree}")" == "$BASE_TREE" ]] ||
    return 70
  [[ "$(git_safe rev-list --parents -n 1 "$AUTH_HEAD")" ==
    "${AUTH_HEAD} ${PROTOCOL_COMMIT_ARG}" ]] || return 70

  expected_p_delta=$(
    /usr/bin/printf '%s\n' \
      ":000000 100644 A ${AUTH_VALIDATOR_PATH}" \
      ":000000 100644 A ${HOST_PATH}" \
      ":000000 100644 A ${PROTOCOL_PATH}" \
      ":000000 100644 A ${RESULT_VALIDATOR_PATH}" \
      ":000000 100644 A ${SOURCE_MANIFEST_PATH}"
  ) || return 71
  [[ "$(raw_delta "$PROTOCOL_COMMIT_ARG")" == "$expected_p_delta" ]] ||
    return 70
  expected_a_delta=$(
    /usr/bin/printf '%s\n' \
      ":000000 100644 A ${ACCOUNTING_PATH}" \
      ":000000 100644 A ${DECISION_PATH}" \
      ":000000 100644 A ${RED_TEAM_PATH}" \
      ":000000 100644 A ${THEORY_PATH}"
  ) || return 71
  [[ "$(raw_delta "$AUTH_HEAD")" == "$expected_a_delta" ]] || return 70

  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$PROTOCOL_PATH")" ==
    "$PROTOCOL_SHA256_ARG" ]] || return 70
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$HOST_PATH")" ==
    "$HOST_SHA256_ARG" ]] || return 70
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$AUTH_VALIDATOR_PATH")" ==
    "$AUTH_VALIDATOR_SHA256_ARG" ]] || return 70
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$RESULT_VALIDATOR_PATH")" ==
    "$RESULT_VALIDATOR_SHA256_ARG" ]] || return 70
  [[ "$(sha256_commit_path "$PROTOCOL_COMMIT_ARG" "$SOURCE_MANIFEST_PATH")" ==
    "$SOURCE_MANIFEST_SHA256_ARG" ]] || return 70

  [[ ! -e "$RECOVERY_DIR" && ! -L "$RECOVERY_DIR" ]] || return 70
  verify_ref_absent "$RECOVERY_CONSUMPTION_REF" || return 70
  verify_ref_absent "$RECOVERY_RESULT_REF" || return 70
  verify_ref_absent "$SOURCE_RESULT_REF" || return 70
  verify_direct_ref_value "$SOURCE_BRANCH_REF" "$SOURCE_AUTH_COMMIT" ||
    return 70
  verify_direct_ref_value \
    "$SOURCE_CONSUMPTION_REF" "$SOURCE_CONSUMPTION_COMMIT" || return 70

  replacements=$(git_safe replace -l) || return 70
  [[ -z "$replacements" ]] || return 70
  grafts=$(git_safe rev-parse --git-path info/grafts) || return 70
  [[ ! -e "$grafts" ]] || return 70
  info_attributes=$(git_safe rev-parse --git-path info/attributes) || return 70
  [[ ! -e "$info_attributes" && ! -L "$info_attributes" ]] || return 70
  config_output=$(git_safe config --show-scope --get-regexp \
    '^(filter\..*\.(clean|process|smudge|required)|tar\..*\.command)$')
  config_status=$?
  [[ "$config_status" -eq 1 && -z "$config_output" ]] || return 70

  /bin/mkdir "$RECOVERY_DIR" || return 71
  /bin/mkdir "${RECOVERY_DIR}/evidence-input" || return 71
  return 0
}


materialize_authorization() {
  local path

  for path in \
    "$PROTOCOL_PATH" \
    "$SOURCE_MANIFEST_PATH" \
    "$AUTH_VALIDATOR_PATH" \
    "$RESULT_VALIDATOR_PATH" \
    "$DECISION_PATH" \
    "$THEORY_PATH" \
    "$ACCOUNTING_PATH" \
    "$RED_TEAM_PATH"
  do
    git_safe show "${AUTH_HEAD}:${path}" \
      >"${RECOVERY_DIR}/evidence-input/${path:t}" || return 70
  done
  git_safe show \
    "${SOURCE_PROTOCOL_COMMIT}:${EXP}/development-test-execution-protocol-v23.json" \
    >"${RECOVERY_DIR}/evidence-input/excluded-source-protocol-v23.json" ||
    return 70
  [[ "$(sha256_file \
    "${RECOVERY_DIR}/evidence-input/excluded-source-protocol-v23.json")" ==
    "$SOURCE_PROTOCOL_SHA256" ]] || return 70
  /bin/chmod 0444 "${RECOVERY_DIR}"/evidence-input/* || return 71
  /bin/chmod 0555 "${RECOVERY_DIR}/evidence-input" || return 71
}


validate_authorization() {
  local protocol="${RECOVERY_DIR}/evidence-input/${PROTOCOL_PATH:t}"
  local decision="${RECOVERY_DIR}/evidence-input/${DECISION_PATH:t}"
  local theory="${RECOVERY_DIR}/evidence-input/${THEORY_PATH:t}"
  local accounting="${RECOVERY_DIR}/evidence-input/${ACCOUNTING_PATH:t}"
  local red_team="${RECOVERY_DIR}/evidence-input/${RED_TEAM_PATH:t}"
  local validator="${RECOVERY_DIR}/evidence-input/${AUTH_VALIDATOR_PATH:t}"
  local expected
  local protocol_tree
  local theory_hash
  local accounting_hash
  local red_hash

  require_canonical_json_line "$decision" || return 70
  require_canonical_json_line "$theory" || return 70
  require_canonical_json_line "$accounting" || return 70
  require_canonical_json_line "$red_team" || return 70
  protocol_tree=$(git_safe rev-parse "${PROTOCOL_COMMIT_ARG}^{tree}") ||
    return 70
  theory_hash=$(sha256_file "$theory") || return 71
  accounting_hash=$(sha256_file "$accounting") || return 71
  red_hash=$(sha256_file "$red_team") || return 71
  expected=$(
    /opt/homebrew/bin/jq -cnS \
      --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
      --arg protocol_tree_sha1 "$protocol_tree" \
      --arg base_commit_sha1 "$BASE_COMMIT" \
      --arg base_tree_sha1 "$BASE_TREE" \
      --arg protocol_sha256 "$PROTOCOL_SHA256_ARG" \
      --arg host_runner_sha256 "$HOST_SHA256_ARG" \
      --arg authorization_validator_sha256 "$AUTH_VALIDATOR_SHA256_ARG" \
      --arg result_validator_sha256 "$RESULT_VALIDATOR_SHA256_ARG" \
      --arg source_manifest_sha256 "$SOURCE_MANIFEST_SHA256_ARG" \
      --arg source_protocol_commit_sha1 "$SOURCE_PROTOCOL_COMMIT" \
      --arg source_protocol_sha256 "$SOURCE_PROTOCOL_SHA256" \
      --arg source_authorization_commit_sha1 "$SOURCE_AUTH_COMMIT" \
      --arg source_consumption_commit_sha1 "$SOURCE_CONSUMPTION_COMMIT" \
      --arg source_stdout_sha256 "$SOURCE_STDOUT_SHA256" \
      '$ARGS.named'
  ) || return 71
  /opt/homebrew/bin/jq -e -n \
    --argjson expected "$expected" \
    --arg theory_receipt_sha256 "$theory_hash" \
    --arg accounting_receipt_sha256 "$accounting_hash" \
    --arg red_team_receipt_sha256 "$red_hash" \
    --slurpfile protocol "$protocol" \
    --slurpfile decision "$decision" \
    --slurpfile theory "$theory" \
    --slurpfile accounting "$accounting" \
    --slurpfile red_team "$red_team" \
    --slurpfile excluded_source \
      "${RECOVERY_DIR}/evidence-input/excluded-source-protocol-v23.json" \
    -f "$validator" >"${RECOVERY_DIR}/authorization-validation.txt" ||
    return 70
  exact_text "${RECOVERY_DIR}/authorization-validation.txt" $'true\n' ||
    return 70
}


consume_recovery_authorization() {
  local payload="${RECOVERY_DIR}/recovery-consumption.json"
  local blob
  local tree
  local commit
  local observed

  RECOVERED_AT=$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ') || return 71
  /opt/homebrew/bin/jq -cnS \
    --arg id "CONSUME-RECOVERY-SGCP-SECANT-V23-V25" \
    --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
    --arg protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
    --arg authorization_commit_sha1 "$AUTH_HEAD" \
    --arg source_consumption_commit_sha1 "$SOURCE_CONSUMPTION_COMMIT" \
    --arg started_at_utc "$RECOVERED_AT" \
    '{
      id: $id,
      experiment_id: $experiment_id,
      protocol_commit_sha1: $protocol_commit_sha1,
      authorization_commit_sha1: $authorization_commit_sha1,
      source_consumption_commit_sha1: $source_consumption_commit_sha1,
      started_at_utc: $started_at_utc,
      maximum_runs_remaining: 0,
      status: "recovery_authorization_consumed_before_source_validation"
    }' >"$payload" || return 71
  require_canonical_json_line "$payload" || return 71
  blob=$(git_safe hash-object -w --no-filters "$payload") || return 71
  tree=$(
    /usr/bin/printf '100644 blob %s\trecovery-consumption.json\n' "$blob" |
      git_safe mktree
  ) || return 71
  commit=$(
    /usr/bin/printf 'SGCP V23/V25 recovery authorization consumption\n' |
      git_safe_ident commit-tree "$tree" -p "$AUTH_HEAD"
  ) || return 71
  git_safe update-ref --no-deref \
    "$RECOVERY_CONSUMPTION_REF" "$commit" "$ZERO_SHA1" || return 71
  observed=$(git_safe rev-parse "$RECOVERY_CONSUMPTION_REF") || return 71
  [[ "$observed" == "$commit" ]] || return 71
  [[ "$(git_safe rev-list --parents -n 1 "$commit")" ==
    "${commit} ${AUTH_HEAD}" ]] || return 71
  RECOVERY_CONSUMPTION_COMMIT="$commit"
  /usr/bin/printf '%s\n' "$commit" \
    >"${RECOVERY_DIR}/recovery-consumption-commit-sha1.txt" || return 71
}


validate_source_inventory() {
  local manifest="${RECOVERY_DIR}/evidence-input/${SOURCE_MANIFEST_PATH:t}"
  local current="${RECOVERY_DIR}/source-inventory.tsv"
  local expected="${RECOVERY_DIR}/expected-source-inventory.tsv"
  local rel
  local hash
  local bytes
  local mode
  local path
  local unexpected
  local directories

  [[ "$(sha256_file "$manifest")" == "$SOURCE_MANIFEST_SHA256_ARG" ]] ||
    return 70
  /opt/homebrew/bin/jq -e \
    --arg run "$SOURCE_RUN" \
    '
      .recovery_source_manifest.id
        == "RECOVERY-SOURCE-MANIFEST-SGCP-SECANT-V23-V25" and
      .recovery_source_manifest.run_directory == $run and
      .recovery_source_manifest.file_count == 53 and
      .recovery_source_manifest.directories
        == [{"mode":"555","path":"evidence-input"}] and
      .recovery_source_manifest.required_absent_paths
        == ["artifact-manifest.sha256","result-seal.json","run-receipt.json"] and
      (.recovery_source_manifest.files | length) == 53 and
      (.recovery_source_manifest.files | map(.path) | unique | length) == 53
    ' "$manifest" >/dev/null || return 70

  : >"$current" || return 71
  while IFS= read -r -d '' path; do
    rel="${path#${SOURCE_RUN}/}"
    [[ "$rel" != *$'\n'* && "$rel" != *$'\t'* ]] || return 70
    hash=$(sha256_file "$path") || return 71
    bytes=$(/usr/bin/wc -c <"$path" | /usr/bin/awk '{print $1}') ||
      return 71
    mode=$(/usr/bin/stat -f '%Lp' "$path") || return 71
    /usr/bin/printf '%s\t%s\t%s\t%s\n' "$rel" "$hash" "$bytes" "$mode" \
      >>"$current" || return 71
  done < <(/usr/bin/find "$SOURCE_RUN" -type f -print0 | /usr/bin/sort -z)
  /opt/homebrew/bin/jq -r '
    .recovery_source_manifest.files[] |
    [.path,.sha256,(.bytes|tostring),.mode] | @tsv
  ' "$manifest" >"$expected" || return 71
  /usr/bin/cmp -s "$current" "$expected" || return 70

  directories=$(
    /usr/bin/find "$SOURCE_RUN" -mindepth 1 -type d -print
  ) || return 71
  [[ "$directories" == "${SOURCE_RUN}/evidence-input" ]] || return 70
  [[ "$(/usr/bin/stat -f '%Lp' "${SOURCE_RUN}/evidence-input")" == "555" ]] ||
    return 70
  unexpected=$(
    /usr/bin/find "$SOURCE_RUN" -mindepth 1 ! -type f ! -type d -print
  ) || return 71
  [[ -z "$unexpected" ]] || return 70
}


validate_source_git() {
  local consumption_blob
  local consumption_tree

  [[ "$(git_safe rev-list --parents -n 1 "$SOURCE_CONSUMPTION_COMMIT")" ==
    "${SOURCE_CONSUMPTION_COMMIT} ${SOURCE_AUTH_COMMIT}" ]] || return 70
  consumption_tree=$(git_safe rev-parse "${SOURCE_CONSUMPTION_COMMIT}^{tree}") ||
    return 70
  consumption_blob=$(git_safe rev-parse \
    "${SOURCE_CONSUMPTION_COMMIT}:consumption.json") || return 70
  [[ "$(git_safe ls-tree "$SOURCE_CONSUMPTION_COMMIT")" ==
    "100644 blob ${consumption_blob}"$'\t'"consumption.json" ]] || return 70
  [[ "$(sha256_commit_path "$SOURCE_CONSUMPTION_COMMIT" consumption.json)" ==
    "72dd1e0b278ed0758eba6cb0a9b2c689f2e5560663298e78d4df7069a387fb29" ]] ||
    return 70
  [[ "$consumption_tree" == "ad581ef2c2576b4b6f415437bf9245771d0db1bf" ]] ||
    return 70
  verify_ref_absent "$SOURCE_RESULT_REF" || return 70
}


validate_source_text_receipts() {
  exact_text "${SOURCE_RUN}/authorization-validation.txt" $'true\n' || return 70
  exact_text "${SOURCE_RUN}/pipeline-status.txt" $'0\n0\n0\n' || return 70
  exact_text "${SOURCE_RUN}/pipeline-wrapper-exit-code.txt" $'0\n' || return 70
  exact_text "${SOURCE_RUN}/timeout-observed.txt" $'false\n' || return 70
  exact_text "${SOURCE_RUN}/docker-create-exit-code.txt" $'0\n' || return 70
  exact_text "${SOURCE_RUN}/docker-cleanup-exit-code.txt" $'0\n' || return 70
  exact_text "${SOURCE_RUN}/docker-cleanup-verify-exit-code.txt" $'1\n' ||
    return 70
  exact_text "${SOURCE_RUN}/docker-name-cleanup-verify-exit-code.txt" $'1\n' ||
    return 70
  exact_text "${SOURCE_RUN}/docker-cleanup-verify-stdout.log" $'[]\n' ||
    return 70
  exact_text "${SOURCE_RUN}/docker-name-cleanup-verify-stdout.log" $'[]\n' ||
    return 70
  exact_text "${SOURCE_RUN}/docker-cleanup-verify-stderr.log" \
    "Error: No such object: ${CONTAINER_ID}"$'\n' || return 70
  exact_text "${SOURCE_RUN}/docker-name-cleanup-verify-stderr.log" \
    "Error: No such object: ${CONTAINER_NAME}"$'\n' || return 70
  exact_text "${SOURCE_RUN}/container-id.txt" "${CONTAINER_ID}"$'\n' || return 70
  exact_text "${SOURCE_RUN}/docker-cleanup.log" "${CONTAINER_ID}"$'\n' ||
    return 70
  exact_text "${SOURCE_RUN}/post-run-cleanup-ownership-basis.txt" \
    $'labels_and_returned_create_id\n' || return 70
  exact_text "${SOURCE_RUN}/preflight.log" \
    $'post-run inspect or cleanup failed\n' || return 70
  [[ ! -s "${SOURCE_RUN}/stderr.log" ]] || return 70
  [[ ! -s "${SOURCE_RUN}/timeout-controller.log" ]] || return 70
  [[ ! -s "${SOURCE_RUN}/git-archive-stderr.log" ]] || return 70
  [[ ! -s "${SOURCE_RUN}/tee-stderr.log" ]] || return 70
  [[ ! -s "${SOURCE_RUN}/final-forbidden-paths.txt" ]] || return 70
  [[ ! -s "${SOURCE_RUN}/pre-execution-forbidden-paths.txt" ]] || return 70
}


capture_current_absence() {
  local status

  docker_safe inspect "$CONTAINER_ID" \
    >"${RECOVERY_DIR}/current-id-absence-stdout.log" \
    2>"${RECOVERY_DIR}/current-id-absence-stderr.log"
  status=$?
  /usr/bin/printf '%s\n' "$status" \
    >"${RECOVERY_DIR}/current-id-absence-exit-code.txt" || return 71
  [[ "$status" -eq 1 ]] || return 70
  exact_text "${RECOVERY_DIR}/current-id-absence-stdout.log" $'[]\n' ||
    return 70
  exact_text "${RECOVERY_DIR}/current-id-absence-stderr.log" \
    "Error: No such object: ${CONTAINER_ID}"$'\n' || return 70

  docker_safe inspect "$CONTAINER_NAME" \
    >"${RECOVERY_DIR}/current-name-absence-stdout.log" \
    2>"${RECOVERY_DIR}/current-name-absence-stderr.log"
  status=$?
  /usr/bin/printf '%s\n' "$status" \
    >"${RECOVERY_DIR}/current-name-absence-exit-code.txt" || return 71
  [[ "$status" -eq 1 ]] || return 70
  exact_text "${RECOVERY_DIR}/current-name-absence-stdout.log" $'[]\n' ||
    return 70
  exact_text "${RECOVERY_DIR}/current-name-absence-stderr.log" \
    "Error: No such object: ${CONTAINER_NAME}"$'\n' || return 70
}


absence_hash_json() {
  /opt/homebrew/bin/jq -cnS \
    --arg id_exit "$(sha256_file "${RECOVERY_DIR}/current-id-absence-exit-code.txt")" \
    --arg id_stdout "$(sha256_file "${RECOVERY_DIR}/current-id-absence-stdout.log")" \
    --arg id_stderr "$(sha256_file "${RECOVERY_DIR}/current-id-absence-stderr.log")" \
    --arg name_exit "$(sha256_file "${RECOVERY_DIR}/current-name-absence-exit-code.txt")" \
    --arg name_stdout "$(sha256_file "${RECOVERY_DIR}/current-name-absence-stdout.log")" \
    --arg name_stderr "$(sha256_file "${RECOVERY_DIR}/current-name-absence-stderr.log")" \
    '{
      id_exit_code: $id_exit,
      id_stderr: $id_stderr,
      id_stdout: $id_stdout,
      name_exit_code: $name_exit,
      name_stderr: $name_stderr,
      name_stdout: $name_stdout
    }'
}


build_and_validate_seal() {
  local absence_hashes
  local expected
  local test_ids
  local seal="${RECOVERY_DIR}/recovery-seal.json"
  local validator="${RECOVERY_DIR}/evidence-input/${RESULT_VALIDATOR_PATH:t}"

  require_canonical_json_line "${SOURCE_RUN}/stdout.json" || return 70
  require_canonical_json_line "${SOURCE_RUN}/docker-inspect-pre.json" ||
    return 70
  require_canonical_json_line "${SOURCE_RUN}/docker-inspect-post.json" ||
    return 70
  require_canonical_json_line "${SOURCE_RUN}/consumption.json" || return 70
  absence_hashes=$(absence_hash_json) || return 71
  test_ids='[
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_scalar_congruence_and_least_slope_selection",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_chart_witnesses_fibers_representatives_diagnostics_and_ops",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_every_reachable_domain_error_and_charged_prefix",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_first_error_precedence",
    "test_sgcp_secant_math_core.TestSgcpSecantMathCore.test_public_results_and_inputs_are_immutable"
  ]'
  /opt/homebrew/bin/jq -cnS \
    --arg id "RECOVERY-SEAL-SGCP-SECANT-V23-V25" \
    --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
    --arg source_run_id "$SOURCE_RUN_ID" \
    --arg source_protocol_commit_sha1 "$SOURCE_PROTOCOL_COMMIT" \
    --arg source_authorization_commit_sha1 "$SOURCE_AUTH_COMMIT" \
    --arg source_consumption_commit_sha1 "$SOURCE_CONSUMPTION_COMMIT" \
    --arg source_original_result_ref "$SOURCE_RESULT_REF" \
    --arg source_manifest_sha256 "$SOURCE_MANIFEST_SHA256_ARG" \
    --arg source_stdout_sha256 "$SOURCE_STDOUT_SHA256" \
    --arg container_id "$CONTAINER_ID" \
    --arg recovery_protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
    --arg recovery_authorization_commit_sha1 "$AUTH_HEAD" \
    --arg recovery_consumption_commit_sha1 "$RECOVERY_CONSUMPTION_COMMIT" \
    --arg recovered_at_utc "$RECOVERED_AT" \
    --arg interpretation \
      "Recovered seal of one fixed five-method public development test; original V23 R remains absent; no registered seed, campaign, scaling, rho, relation-generation, or ECDLP-improvement claim." \
    --argjson test_ids "$test_ids" \
    --argjson absence "$absence_hashes" \
    '{
      id: $id,
      experiment_id: $experiment_id,
      classification: "RECOVERED_VALID_DEVELOPMENT_TEST",
      evidence_status: "separate_recovery_seal_original_R_absent",
      source_run_id: $source_run_id,
      source_protocol_commit_sha1: $source_protocol_commit_sha1,
      source_authorization_commit_sha1: $source_authorization_commit_sha1,
      source_consumption_commit_sha1: $source_consumption_commit_sha1,
      source_original_result_ref: $source_original_result_ref,
      source_original_result_ref_absent: true,
      source_manifest_sha256: $source_manifest_sha256,
      source_stdout_sha256: $source_stdout_sha256,
      tests_started: 5,
      test_ids: $test_ids,
      container_id: $container_id,
      container_exit_code: 0,
      oom_killed: false,
      timeout_observed: false,
      pipeline_status: [0,0,0],
      cleanup_proved: true,
      post_inspect_normalization: {
        field: "HostConfig.OomKillDisable",
        pre_start: false,
        post_exit: null,
        scope: "post_exit_representation_only"
      },
      operation_accounting: {
        offline_field_operations: "not_applicable",
        online_field_operations: "not_applicable",
        group_operations: "not_applicable",
        memory_bandwidth: "not_measured"
      },
      preprocessing_accounting: {
        cryptanalytic_preprocessing: "not_applicable",
        fixed_curve_advice_bytes: "not_applicable",
        recovery_control_plane_work: "not_an_attack_cost_measurement",
        recovery_fixed_overhead: "not_measured"
      },
      target_scope: {
        trials: 1,
        test_methods: 5,
        supported_ecdlp_targets: 0,
        probability_claim: "none",
        generator: "not_applicable",
        field_modulus: "not_applicable",
        curve_structure: "not_applicable"
      },
      recovery_protocol_commit_sha1: $recovery_protocol_commit_sha1,
      recovery_authorization_commit_sha1:
        $recovery_authorization_commit_sha1,
      recovery_consumption_commit_sha1:
        $recovery_consumption_commit_sha1,
      current_absence_receipt_sha256: $absence,
      recovered_at_utc: $recovered_at_utc,
      interpretation: $interpretation
    }' >"$seal" || return 71
  require_canonical_json_line "$seal" || return 71

  expected=$(
    /opt/homebrew/bin/jq -cnS \
      --arg experiment_id "EXP-SGCP-SECANT-REP-001" \
      --arg source_run_id "$SOURCE_RUN_ID" \
      --arg source_protocol_commit_sha1 "$SOURCE_PROTOCOL_COMMIT" \
      --arg source_authorization_commit_sha1 "$SOURCE_AUTH_COMMIT" \
      --arg source_consumption_commit_sha1 "$SOURCE_CONSUMPTION_COMMIT" \
      --arg source_original_result_ref "$SOURCE_RESULT_REF" \
      --arg source_manifest_sha256 "$SOURCE_MANIFEST_SHA256_ARG" \
      --arg source_stdout_sha256 "$SOURCE_STDOUT_SHA256" \
      --arg source_started_at_utc "$SOURCE_STARTED_AT" \
      --arg container_id "$CONTAINER_ID" \
      --arg container_name "$CONTAINER_NAME" \
      --arg image_id "$IMAGE_ID" \
      --arg container_script "$CONTAINER_SCRIPT" \
      --arg container_runner_sha256 "$CONTAINER_RUNNER_SHA256" \
      --arg container_runner_path "$CONTAINER_RUNNER_PATH" \
      --arg source_path "$SOURCE_PATH" \
      --arg test_path "$TEST_PATH" \
      --arg recovery_protocol_commit_sha1 "$PROTOCOL_COMMIT_ARG" \
      --arg recovery_authorization_commit_sha1 "$AUTH_HEAD" \
      --arg recovery_consumption_commit_sha1 "$RECOVERY_CONSUMPTION_COMMIT" \
      --arg recovered_at_utc "$RECOVERED_AT" \
      --arg interpretation \
        "Recovered seal of one fixed five-method public development test; original V23 R remains absent; no registered seed, campaign, scaling, rho, relation-generation, or ECDLP-improvement claim." \
      --argjson current_absence_receipt_sha256 "$absence_hashes" \
      '$ARGS.named'
  ) || return 71
  /opt/homebrew/bin/jq -e -n \
    --argjson expected "$expected" \
    --slurpfile stdout "${SOURCE_RUN}/stdout.json" \
    --slurpfile pre "${SOURCE_RUN}/docker-inspect-pre.json" \
    --slurpfile post "${SOURCE_RUN}/docker-inspect-post.json" \
    --slurpfile source_consumption "${SOURCE_RUN}/consumption.json" \
    --slurpfile seal "$seal" \
    -f "$validator" >"${RECOVERY_DIR}/recovery-validation.txt" || return 70
  exact_text "${RECOVERY_DIR}/recovery-validation.txt" $'true\n' || return 70
}


seal_recovery_ref() {
  local seal_blob
  local manifest_blob
  local validation_blob
  local id_exit_blob
  local id_stdout_blob
  local id_stderr_blob
  local name_exit_blob
  local name_stdout_blob
  local name_stderr_blob
  local tree
  local commit
  local observed
  local tree_spec="${RECOVERY_DIR}/result-tree-spec.txt"

  verify_ref_absent "$SOURCE_RESULT_REF" || return 70
  seal_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/recovery-seal.json") || return 71
  manifest_blob=$(git_safe rev-parse \
    "${PROTOCOL_COMMIT_ARG}:${SOURCE_MANIFEST_PATH}") || return 71
  validation_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/recovery-validation.txt") || return 71
  id_exit_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-id-absence-exit-code.txt") || return 71
  id_stdout_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-id-absence-stdout.log") || return 71
  id_stderr_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-id-absence-stderr.log") || return 71
  name_exit_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-name-absence-exit-code.txt") || return 71
  name_stdout_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-name-absence-stdout.log") || return 71
  name_stderr_blob=$(git_safe hash-object -w --no-filters \
    "${RECOVERY_DIR}/current-name-absence-stderr.log") || return 71

  /usr/bin/printf '%s\n' \
    "100644 blob ${id_exit_blob}"$'\t'"current-id-absence-exit-code.txt" \
    "100644 blob ${id_stderr_blob}"$'\t'"current-id-absence-stderr.log" \
    "100644 blob ${id_stdout_blob}"$'\t'"current-id-absence-stdout.log" \
    "100644 blob ${name_exit_blob}"$'\t'"current-name-absence-exit-code.txt" \
    "100644 blob ${name_stderr_blob}"$'\t'"current-name-absence-stderr.log" \
    "100644 blob ${name_stdout_blob}"$'\t'"current-name-absence-stdout.log" \
    "100644 blob ${seal_blob}"$'\t'"recovery-seal.json" \
    "100644 blob ${validation_blob}"$'\t'"recovery-validation.txt" \
    "100644 blob ${manifest_blob}"$'\t'"source-manifest.json" \
    >"$tree_spec" || return 71
  tree=$(git_safe mktree <"$tree_spec") || return 71
  commit=$(
    /usr/bin/printf 'SGCP V23/V25 recovered development-test seal\n' |
      git_safe_ident commit-tree "$tree" -p "$RECOVERY_CONSUMPTION_COMMIT"
  ) || return 71
  git_safe update-ref --no-deref \
    "$RECOVERY_RESULT_REF" "$commit" "$ZERO_SHA1" || return 71
  observed=$(git_safe rev-parse "$RECOVERY_RESULT_REF") || return 71
  [[ "$observed" == "$commit" ]] || return 71
  [[ "$(git_safe rev-list --parents -n 1 "$commit")" ==
    "${commit} ${RECOVERY_CONSUMPTION_COMMIT}" ]] || return 71
  [[ "$(git_safe rev-parse "${commit}^{tree}")" == "$tree" ]] || return 71
  verify_ref_absent "$SOURCE_RESULT_REF" || return 70
  /usr/bin/printf '%s\n' "$commit" \
    >"${RECOVERY_DIR}/recovery-result-commit-sha1.txt" || return 71
}


main() {
  preclaim || return $?
  materialize_authorization || return $?
  validate_authorization || return $?
  consume_recovery_authorization || return $?
  validate_source_git || return $?
  validate_source_inventory || return $?
  validate_source_text_receipts || return $?
  capture_current_absence || return $?
  build_and_validate_seal || return $?
  validate_source_inventory || return $?
  seal_recovery_ref || return $?
  return 0
}


main
