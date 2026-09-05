# General polynomial solver ML benchmark — engineering contract v1

This is a self-contained computational-algebra software benchmark. It does not
implement elliptic curves, isogenies, summation polynomials, point decomposition,
discrete logarithms, or a research-campaign dispatcher. Its acceptance criterion
is a reproducible working pipeline, not a mathematical or cryptanalytic advance.

Inputs are generated two-variable polynomial systems over primes at most 31.
Three training families (dense quadratics, sparse cubics, triangular systems)
are split by prime into train/validation/test. Dense cubics are an additional
held-out family. All input systems have a planted solution, and every completed
solver result is checked against exhaustive integer modular evaluation of the
original equations. Planted solutions and family/split identifiers are excluded
from model features. Root extraction enumerates the small finite-field grid;
it is an exact educational baseline, not an efficient general root algorithm.

Actions are the Cartesian product of SymPy's public Buchberger/F5B methods and
lexicographic/graded-reverse-lexicographic orders. The primary cost is median
symbolic construction + basis construction + basis-grid root extraction time.
All repetitions, process overhead, source hashes, raw outputs, root counts,
peak process RSS, label acquisition, verification, fitting, and prediction
costs are retained. Input features use the unsolved polynomial descriptions.

A supervised multi-output ridge model predicts log costs. A one-step softmax
policy-gradient contextual bandit trains in an offline simulator of the measured
training cost table. This is not multi-step RL, and acquiring the complete table
is charged. Controls are fixed action, training-set-best fixed action, seeded
uniform selection, exact uniform expected cost, and a retrospective oracle.
Synthetic positive/constant-reward and train-label-shuffle controls are reported.
Model normalization and parameters use training rows only. Validation/test rows
never choose hyperparameters or checkpoints. Model checkpoints are plain JSON.

Quick profile: 23 cases, one repetition per action. Standard profile: 58 cases,
two repetitions per action. One subprocess at a time; default per-action timeout
5 seconds; whole-run budget 600 seconds. Each output directory is new and is
never reused. A timeout is censored and charged PAR-2 (twice its time limit),
never a fast solve. Exceptions, malformed outputs, and root mismatches stop the
pipeline and preserve a failed receipt. Exhausting the global budget preserves
partial observations without claiming a completed run. Linux subprocesses have
a 2 GiB address-space limit; local macOS records RSS and enforces the observed
limit after return. Harbor supplies the container's 2 GiB memory limit.

The independent software verifier checks hashes, regenerates input cases,
enumerates roots, recomputes model selections and summary metrics, and rejects
missing/duplicated labels or split leakage. Harbor's reward is a binary software
integrity/completion gate. Measured speedups are reported separately and are not
an authenticated competitive leaderboard score. There is no required speedup:
a correctly measured slower learner is a valid result. Tiny timings are noisy
and do not establish asymptotic behavior or transfer to other problem families.
