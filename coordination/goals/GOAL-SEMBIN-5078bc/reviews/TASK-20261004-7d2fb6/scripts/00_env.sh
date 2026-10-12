# Source this file. Scratch work directory (binaries, bulk output) lives outside the write scope.
export SP=/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/v7d2fb6
export WS=/home/user/crypto-autoresearcher/coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261004-7d2fb6
export CODE=/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code
export M4RI_PREFIX=$SP/m4ri_prefix          # my own build of release-20240729 (see scripts/01_build_m4ri.sh)
export LD_LIBRARY_PATH=$M4RI_PREFIX/lib
export PYTHONPATH=/home/user/crypto-autoresearcher/harness/macaulay_fp/fixtures
ulimit -v 3145728   # 3 GB cap on every shell that sources this
