#!/bin/bash
# J4(i): run the snapshot-committed pipeline (copied to src/pipeline_perm, instrument.py patched ONLY in the walk;
# run_generic.py and analysis.py byte-identical to the snapshot) on a keyed BIJECTION of [0, 2^20) at
# T = 64, W = 64, cap 8W, a = 1/4, seeds 1..3, all arms (U = 16T; eps_ss(8T) is reported), then the
# pipeline's own analysis (S1/S3/G1 verdicts).  Review control, not an experiment run; writes only here.
set -u
TD=/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-90e7cf
PIPE=$TD/src/pipeline_perm
cd /home/user/crypto-autoresearcher
for KIND in permutation affine_xorshift; do
  RD=$TD/results/j4_perm/$KIND
  mkdir -p $RD
  for S in 1 2 3; do
    OUT=$RD/RUN-RT-90e7cf-$KIND-s$S
    mkdir -p $OUT
    CMD="RT_WALK_KIND=$KIND OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 timeout 600s /usr/bin/time -v python3 $PIPE/run_generic.py --n-bits 20 --a 1/4 --seed $S --outdir $OUT"
    echo "$CMD" > $OUT/command.txt
    START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    RT_WALK_KIND=$KIND OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0 timeout 600s /usr/bin/time -v python3 $PIPE/run_generic.py --n-bits 20 --a 1/4 --seed $S --outdir $OUT > $OUT/stdout.log 2> $OUT/stderr.log
    RC=$?
    END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    WALL=$(grep "Elapsed (wall clock)" $OUT/stderr.log | awk '{print $NF}')
    RSS=$(grep "Maximum resident set size" $OUT/stderr.log | awk '{print $NF}')
    # minimal manifest with exactly the fields the producer's analysis.py reads
    cat > $OUT/manifest.yaml <<M
run:
  id: RUN-RT-90e7cf-$KIND-s$S
  kind_note: RED TEAM review control (proves-too-much object, J4(i)); NOT an experiment run of EXP-ECDLP-612fb1
  status: $([ $RC -eq 0 ] && echo completed_valid || echo failed_infrastructure)
  exit_code: $RC
  walk_kind: $KIND
  code:
    pipeline_copy: $PIPE
    snapshot_commit: 840df8a5b51bff046007d1c12b3a45553d76dc11
    diff_applied: $PIPE/instrument.py.diff
  inputs:
    parameters: {kind: generic, n_bits: 20, a: 0.25, seed: $S, stage: G}
    seed: $S
  timing: {started_at: '$START', finished_at: '$END', wall_seconds: '$WALL'}
  resources: {peak_rss_bytes: $((RSS * 1024)), max_rss_kb_from_time_v: $RSS}
  result: {valid: $([ $RC -eq 0 ] && echo true || echo false), invalid_reason: null}
M
    echo "[$KIND seed $S] rc=$RC wall=$WALL maxrss_kb=$RSS"
  done
  mkdir -p $RD/analysis
  echo "OMP_NUM_THREADS=1 python3 $PIPE/analysis.py --runs-dir $RD --stages G --outdir $RD/analysis --resamples 2000" > $RD/analysis/command.txt
  OMP_NUM_THREADS=1 /usr/bin/time -v python3 $PIPE/analysis.py --runs-dir $RD --stages G --outdir $RD/analysis --resamples 2000 > $RD/analysis/stdout.log 2> $RD/analysis/stderr.log
  echo "[$KIND analysis] rc=$? wall=$(grep 'Elapsed (wall clock)' $RD/analysis/stderr.log | awk '{print $NF}')"
done
