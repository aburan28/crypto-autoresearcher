#!/bin/bash
# 20 curves, 4 at a time; safe to relaunch after a restart (finished steps are skipped; flock prevents doubles).
cd "$(dirname "$0")"
exec 9>batch.lock; flock -n 9 || exit 0
seq 1 20 | xargs -P 4 -n 1 ./curve.sh
echo ALLDONE > batch.done
