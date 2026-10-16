#!/bin/sh
# Native command and receipt orchestration only; no mathematical implementation.
set -u
mode=$1
run_dir=$2
if [ "$mode" = check ]; then
  test -s "$run_dir/manifest.yaml" && test -s "$run_dir/raw-result.json"
  exit $?
fi
case "$mode" in construct|verify) ;; *) exit 64 ;; esac
case "$run_dir" in /*) ;; *) exit 64 ;; esac
test ! -e "$run_dir/manifest.yaml" && test ! -e "$run_dir/native" || exit 73
binary='/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/compact-final-e82d80feaf/isogeny'
binary_hash=$(shasum -a 256 "$binary") || exit 74
case "$binary_hash" in b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b' '*) ;; *) exit 74 ;; esac
: > "$run_dir/native.stdout.log"
: > "$run_dir/native.stderr.log"
started=false
native_exit=0
case "$mode" in
construct)
  unset ISOGENY_REPLAY_TRACE
  started=true
  /usr/bin/time -l "$binary" compact-cm construct --exponent 44497 --out "$run_dir/native" --timeout 1800 > "$run_dir/native.stdout.log" 2> "$run_dir/native.stderr.log"
  native_exit=$?
  record="$run_dir/native/construction.json"
  exp=EXP-ISOU-0c7e60
  if [ "$native_exit" -eq 0 ] && test -s "$run_dir/native/certificate.json"; then
    shasum -a 256 "$run_dir/native/certificate.json" > "$run_dir/certificate.sha256" || exit 74
  fi
  ;;
verify)
  unset ISOGENY_REPLAY_TRACE
  exp=EXP-ISOU-0c7e60
  if test -s '/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/construction.json' && grep -Eq '"status"[[:space:]]*:[[:space:]]*"CONSTRUCTED"' '/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/construction.json' && grep -Eq '"status"[[:space:]]*:[[:space:]]*"PASS"' '/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/native.receipt.json' && shasum -a 256 -c '/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/certificate.sha256'; then
    started=true
    /usr/bin/time -l "$binary" compact-cm verify --input '/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/certificate.json' --out "$run_dir/native" --timeout 3600 > "$run_dir/native.stdout.log" 2> "$run_dir/native.stderr.log"
    native_exit=$?
    record="$run_dir/native/verification.json"
  else
    printf '{"status":"NOT_STARTED","reason":"construction_not_passed_or_certificate_hash_changed","scientific_promotion":false}\n' > "$run_dir/raw-result.json"
    record="$run_dir/raw-result.json"
  fi
  ;;
esac
if [ "$record" != "$run_dir/raw-result.json" ]; then
  if test -s "$record"; then cp "$record" "$run_dir/raw-result.json"; else
    printf '{"status":"INCOMPLETE","native_exit_code":%s,"scientific_promotion":false}\n' "$native_exit" > "$run_dir/raw-result.json"
  fi
fi
status=completed
if [ "$native_exit" -ne 0 ]; then status=failed; fi
if [ "$started" = false ]; then status=not_started; fi
native_exit_field=$native_exit
if [ "$started" = false ]; then native_exit_field=null; fi
rid=${run_dir##*/}
cat > "$run_dir/manifest.yaml" <<EOF
run:
  id: $rid
  experiment_id: $exp
  status: $status
  status_note: Observation delivery only; native result and censor remain authoritative.
  code:
    commit: e82d80feaf82d3730576ccd9137911b336f9dab8
    source_repository: aburan28/crypto
    command: /bin/sh coordination/goals/GOAL-ISOU-f30a07/m44497/native-command.sh $mode $run_dir
    binary_sha256: b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b
  environment: $run_dir/environment.json
  inputs:
    parameters:
      operation: $mode
      native_process_started: $started
  timing:
    cpu_seconds: null
    public_command_time_and_native_stderr: $run_dir/native.stderr.log
    note: /usr/bin/time -l raw user/system/real and RSS are captured if the native process started; keep actual units and scope, do not infer missing CPU.
  result:
    raw_result: $run_dir/raw-result.json
    native_exit_code: $native_exit_field
    scientific_promotion: false
    certificate:
      kind: none
EOF
# A native reject/censor is a complete observation, not scientific success.
exit 0
