#!/usr/bin/env bash
# Launcher for EXP-CERTBIN-060020 (records command.txt, environment.json,
# stdout.log, stderr.log; applies the machine-protection limits).
#
#   impl/launch.sh main        RUN_ID [--resume]   # specification execution.command
#   impl/launch.sh determinism RUN_ID              # execution.determinism_command
#   impl/launch.sh backend     RUN_ID              # execution.backend_command
#   impl/launch.sh verify      RUN_ID              # execution.verify_command
#   impl/launch.sh aggregate   RUN_ID              # driver --resume after phase 6
#
# Development rehearsals only: OUTROOT (outside runs/), DEV_ARGS, VERIFY_DEV_ARGS.
set -u
STAGE=$1; RUN_ID=$2; shift 2
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$ROOT"
E=experiments/EXP-CERTBIN-060020
OUTROOT=${OUTROOT:-$E/runs}
PLAN=${PLAN:-$E/trial-plan-v1.json}
OUT=$OUTROOT/$RUN_ID
SPEC=$E/specification.yaml
mkdir -p "$OUT"
export CRYPTO_AR_GF2_BACKEND=native PYTHONDONTWRITEBYTECODE=1
export CRYPTO_AR_GF2_THREADS=${CRYPTO_AR_GF2_THREADS:-2} OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2
ulimit -v $((3 * 1024 * 1024))   # 3 GiB address-space cap (machine protection)
WD="timeout --signal=TERM 172800"
DRV="python3 $E/impl/driver.py --spec $SPEC --plan $PLAN --run-id $RUN_ID --out $OUT ${DEV_ARGS:-}"
case "$STAGE" in
  main)
    python3 $E/impl/record_env.py "$OUT"
    if [ "${1:-}" = "--resume" ]; then
      CMD="$DRV --resume"
    else
      CMD="python3 $E/impl/engine_provenance.py --out $OUT/engine-provenance && python3 $E/impl/selftest.py --out $OUT/selftest.json ${SELFTEST_DEV_ARGS:-} && $DRV"
    fi ;;
  determinism) CMD="$DRV --phase determinism" ;;
  backend) CMD="CRYPTO_AR_GF2_BACKEND=reference $DRV --phase backend" ;;
  verify) CMD="python3 $E/verifier/verify_n19.py --run $OUT --spec $SPEC --out $OUT ${VERIFY_DEV_ARGS:-}" ;;
  aggregate) CMD="$DRV --resume" ;;
  *) echo "unknown stage $STAGE"; exit 64 ;;
esac
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  echo "# [$START] stage=$STAGE cwd=$ROOT"
  echo "# env: CRYPTO_AR_GF2_BACKEND=$CRYPTO_AR_GF2_BACKEND CRYPTO_AR_GF2_THREADS=$CRYPTO_AR_GF2_THREADS OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1; ulimit -v $((3 * 1024 * 1024)); run watchdog: $WD"
  echo "$CMD"
} >> "$OUT/command.txt"
echo "===== [$START] stage=$STAGE =====" >> "$OUT/stdout.log"
echo "===== [$START] stage=$STAGE =====" >> "$OUT/stderr.log"
$WD bash -c "$CMD" >> "$OUT/stdout.log" 2>> "$OUT/stderr.log"
RC=$?
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "# [$END] stage=$STAGE exit=$RC" >> "$OUT/command.txt"
echo "stage $STAGE exit $RC"
exit $RC
