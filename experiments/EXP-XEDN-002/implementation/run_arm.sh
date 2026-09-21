#!/usr/bin/env bash
# EXP-XEDN-002 run driver.  Creates the run directory, records the exact command,
# and executes one arm with stdout/stderr redirected into the run record so the
# logs are real captured streams.  No git write commands are ever issued.
#
#   usage: bash experiments/EXP-XEDN-002/implementation/run_arm.sh <TAG> [extra args]
#     TAG in {A, B, C, CTRL}
#
# Must be invoked from the repository root.
set -u -o pipefail

TAG="${1:?usage: run_arm.sh <A|B|C|CTRL> [extra args]}"
shift || true

case "$TAG" in
  A|A2) SCRIPT=arm_a_closed_form.py ;;
  B)    SCRIPT=arm_b_exhaustive.py ;;
  C)    SCRIPT=arm_c_histogram.py ;;
  CTRL) SCRIPT=controls.py ;;
  *)    echo "unknown arm tag: $TAG" >&2; exit 2 ;;
esac

RUN_ID="RUN-XEDN-002-${TAG}"
RUN_DIR="experiments/EXP-XEDN-002/runs/${RUN_ID}"
IMPL="experiments/EXP-XEDN-002/implementation"

if [ -e "${RUN_DIR}/manifest.yaml" ]; then
  echo "refusing to overwrite immutable run record ${RUN_DIR}" >&2
  exit 3
fi
mkdir -p "$RUN_DIR"

INNER="python3 ${IMPL}/${SCRIPT} --run-id ${RUN_ID} $*"
OUTER="bash ${IMPL}/run_arm.sh ${TAG} $*"

{
  echo "# reproduction entry point (from repository root):"
  echo "$OUTER"
  echo "# exact inner command executed by the driver:"
  echo "$INNER > ${RUN_DIR}/stdout.log 2> ${RUN_DIR}/stderr.log"
} > "${RUN_DIR}/command.txt"

export XEDN2_COMMAND="$INNER"
export XEDN2_OUTER_COMMAND="$OUTER"
export PYTHONHASHSEED=0

START_EPOCH=$(date -u +%s)
eval "$INNER" > "${RUN_DIR}/stdout.log" 2> "${RUN_DIR}/stderr.log"
STATUS=$?
END_EPOCH=$(date -u +%s)

echo "driver: arm ${TAG} exit=${STATUS} wall=$((END_EPOCH - START_EPOCH))s -> ${RUN_DIR}"
exit $STATUS
