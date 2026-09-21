#!/bin/zsh

set -u
setopt pipefail
umask 077

readonly PROTOCOL_FILE="${1-}"
readonly HOST_FILE="${2-}"
readonly RUNNER_FILE="${3-}"
readonly MARKER="__SGCP_V27_SHELL_CONTROL_STATUS__="
readonly ZSH_SHA256="528da649cc69510bd3c0bc565298cb602076b74a8ac3f18e793211b2a3c725e8"


sha256_file() {
  /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'
}


byte_count() {
  /usr/bin/wc -c <"$1" | /usr/bin/awk '{print $1}'
}


verify_toolchain() {
  [[ "$(sha256_file /bin/zsh)" == "$ZSH_SHA256" ]] &&
    [[ "$(sha256_file /usr/bin/awk)" ==
      "3868b14602a4851218210ae1b08732fbdee703ac2c1e2d1898272b42fd33151a" ]] &&
    [[ "$(sha256_file /usr/bin/printf)" ==
      "f2a76beee50f16a1193244519ecfad592b3af0623276b41c088c0ef8650c05f7" ]] &&
    [[ "$(sha256_file /usr/bin/shasum)" ==
      "0812595f981a26f813d98dc380af14d4af427626c9339eda29eb849ae13de1e3" ]] &&
    [[ "$(sha256_file /usr/bin/wc)" ==
      "32f22e2b385cbc5250c5cc9a11465f5afa74c024724040f47d9edb71ce429e1a" ]] &&
    [[ "$(sha256_file /usr/bin/cmp)" ==
      "bf0111a82ee28deeb99a83eaee6f0829a743e09dcf8193ebd49b4c4190ad2457" ]] &&
    [[ "$(sha256_file /opt/homebrew/bin/jq)" ==
      "e0a718e60bd1098fc134b354da3821a96d4a7510a15465ff64669b04349fc37c" ]]
}


verify_inputs() {
  [[ "$#" -eq 3 ]] || return 1
  [[ -f "$PROTOCOL_FILE" && ! -L "$PROTOCOL_FILE" ]] || return 1
  [[ -f "$HOST_FILE" && ! -L "$HOST_FILE" ]] || return 1
  [[ -f "$RUNNER_FILE" && ! -L "$RUNNER_FILE" ]] || return 1
  [[ "${PROTOCOL_FILE:t}" ==
    "development-test-recovery-protocol-v27.json" ]] || return 1
  [[ "${HOST_FILE:t}" ==
    "development-test-recovery-host-runner-v27.zsh" ]] || return 1
  [[ "${RUNNER_FILE:t}" ==
    "development-test-recovery-shell-control-runner-v27.zsh" ]] || return 1
  /opt/homebrew/bin/jq -e '
    .recovery_protocol.id
      == "EXP-SGCP-SECANT-REP-001-DEVELOPMENT-TEST-RECOVERY-PROTOCOL-V27" and
    .recovery_protocol.status == "review_required_zero_run"
  ' "$PROTOCOL_FILE" >/dev/null
}


verify_no_special_assignments() {
  /usr/bin/awk '
    function bad_declaration(line, count, fields, field_index, token) {
      sub(/^[[:space:]]+/, "", line)
      if (line !~ /^(local|readonly|typeset)([[:space:]]|$)/) {
        return 0
      }
      count = split(line, fields, /[[:space:]]+/)
      for (field_index = 2; field_index <= count; field_index++) {
        token = fields[field_index]
        if (token ~ /^-/) {
          continue
        }
        sub(/=.*/, "", token)
        if (token == "status" || token == "path") {
          return 1
        }
      }
      return 0
    }
    {
      if ($0 ~ /(^|[;[:space:]])(status|path)=/) {
        bad = 1
      }
      if (bad_declaration($0)) {
        bad = 1
      }
    }
    END {
      exit bad
    }
  ' "$1"
}


verify_outcome() {
  local requested="$1"
  local payload
  local producer_rc
  local retained

  payload=$(
    /bin/zsh -f -c \
      '/usr/bin/printf "host-byte-line\n"; exit "$1"' -- "$requested"
    producer_rc=$?
    /usr/bin/printf '%s%s' "$MARKER" "$producer_rc"
  )
  [[ "$payload" == *"${MARKER}"<-> ]] || return 1
  producer_rc="${payload##*${MARKER}}"
  retained="${payload%${MARKER}${producer_rc}}"
  [[ "$producer_rc" == "$requested" ]] || return 1
  [[ "$retained" == $'host-byte-line\n' ]]
}


capture_bootstrap() {
  local payload
  local producer_rc

  payload=$(
    /opt/homebrew/bin/jq -j \
      '.recovery_protocol.canonical_bootstrap.runner_script_lines |
       join("\n"), "\n"' "$PROTOCOL_FILE"
    producer_rc=$?
    /usr/bin/printf '%s%s' "$MARKER" "$producer_rc"
  )
  [[ "$payload" == *"${MARKER}"<-> ]] || return 1
  producer_rc="${payload##*${MARKER}}"
  typeset -g BOOTSTRAP_TEXT="${payload%${MARKER}${producer_rc}}"
  [[ "$producer_rc" == "0" && "$BOOTSTRAP_TEXT" == *$'\n' ]]
}


verify_host_roundtrip() {
  local payload
  local producer_rc
  local host_text

  payload=$(
    /usr/bin/awk '1' "$HOST_FILE"
    producer_rc=$?
    /usr/bin/printf '%s%s' "$MARKER" "$producer_rc"
  )
  [[ "$payload" == *"${MARKER}"<-> ]] || return 1
  producer_rc="${payload##*${MARKER}}"
  host_text="${payload%${MARKER}${producer_rc}}"
  [[ "$producer_rc" == "0" && "$host_text" == *$'\n' ]] || return 1
  /usr/bin/printf '%s' "$host_text" | /usr/bin/cmp -s "$HOST_FILE" -
}


main() {
  local expected_host_sha
  local expected_host_bytes
  local runner_sha
  local host_sha
  local host_bytes
  local bootstrap_sha
  local bootstrap_bytes

  verify_toolchain || return 72
  verify_inputs "$@" || return 72
  expected_host_sha=$(
    /opt/homebrew/bin/jq -er \
      '.recovery_protocol.review_target.host_runner_sha256' "$PROTOCOL_FILE"
  ) || return 72
  expected_host_bytes=$(
    /opt/homebrew/bin/jq -er \
      '.recovery_protocol.review_target.host_runner_bytes' "$PROTOCOL_FILE"
  ) || return 72
  host_sha=$(sha256_file "$HOST_FILE") || return 72
  host_bytes=$(byte_count "$HOST_FILE") || return 72
  [[ "$host_sha" == "$expected_host_sha" ]] || return 72
  [[ "$host_bytes" == "$expected_host_bytes" ]] || return 72

  verify_no_special_assignments "$HOST_FILE" || return 72
  verify_outcome 0 || return 72
  verify_outcome 1 || return 72
  verify_outcome 128 || return 72
  verify_host_roundtrip || return 72
  capture_bootstrap || return 72
  /usr/bin/printf '%s' "$BOOTSTRAP_TEXT" |
    verify_no_special_assignments /dev/stdin || return 72

  runner_sha=$(sha256_file "$RUNNER_FILE") || return 72
  bootstrap_sha=$(
    /usr/bin/printf '%s' "$BOOTSTRAP_TEXT" |
      /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}'
  ) || return 72
  bootstrap_bytes=$(
    /usr/bin/printf '%s' "$BOOTSTRAP_TEXT" |
      /usr/bin/wc -c | /usr/bin/awk '{print $1}'
  ) || return 72

  /opt/homebrew/bin/jq -cnS \
    --arg id "SHELL-CONTROL-SGCP-SECANT-V23-V27" \
    --arg runner_sha256 "$runner_sha" \
    --arg host_runner_sha256 "$host_sha" \
    --argjson host_runner_bytes "$host_bytes" \
    --arg bootstrap_template_sha256 "$bootstrap_sha" \
    --argjson bootstrap_template_bytes "$bootstrap_bytes" \
    --arg zsh_sha256 "$ZSH_SHA256" \
    '{
      shell_control_receipt: {
        id: $id,
        schema_version: 1,
        classification: "SAFE_PREAUTH_SHELL_CONTROL",
        inputs: {
          shell_control_runner_sha256: $runner_sha256,
          host_runner_sha256: $host_runner_sha256,
          host_runner_bytes: $host_runner_bytes,
          bootstrap_template_sha256: $bootstrap_template_sha256,
          bootstrap_template_bytes: $bootstrap_template_bytes
        },
        toolchain: {
          zsh_path: "/bin/zsh",
          zsh_sha256: $zsh_sha256
        },
        controls: {
          outcome_matrix: [
            {requested: 0, observed: 0, payload_terminal_lf_retained: true},
            {requested: 1, observed: 1, payload_terminal_lf_retained: true},
            {requested: 128, observed: 128, payload_terminal_lf_retained: true}
          ],
          actual_host_marker_roundtrip: true,
          bootstrap_terminal_lf: true,
          no_status_or_path_assignments: true
        },
        authority: {
          repository_ref_access: false,
          docker_access: false,
          protected_source_access: false,
          archive_extraction: false,
          recovery_execution: false
        },
        interpretation:
          "Deterministic shell and byte-retention control only; no recovery authority or cryptanalytic evidence."
      }
    }'
}


main "$@"
