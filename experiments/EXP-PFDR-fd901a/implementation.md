# EXP-PFDR-fd901a -- implementation note (TASK-20260903-5a62de)

Executor implementation of the frozen contract `specification.yaml`
(status `approved`, `approved_by: coordinator`, decision DEC-20260903-93862f,
read at commit 3a9c1b02 which is level with `origin/main`). Nothing in the
specification, the hypothesis, the meter package or any ledger record was
edited. Observations only; the verdict on H-PFDR-09e1b0 belongs to the review
round.

## 1. What was built

| file | role |
|---|---|
| `run_experiment.py` | the run script: curves, planting, certificates, all arms, the meter calls, one run package per stage through `harness.runner.write_run` |
| `analyze.py` | Stage 4 (zero compute): reads `runs/*/raw-result.json` only and writes `analysis.md` + `analysis.json` |
| `stage0-derivation.md` | Stage 0: the (2, 2, 3) family at D = 4, minor-degree bound, content primes |
| `analysis.md`, `analysis.json` | Stage 4 output |
| `execution-report.yaml` | the execution report (handoff deliverable name) |
| `runs/RUN-PFDR-fd901a-*/` | six immutable run packages, each with the six required files plus `checksums.sha256` |

Meter: `harness/macaulay_fp/` at its snapshot commit 2d2083e5 (tooling
TASK-20260903-ba41aa), used unmodified. Every manifest records the meter's
per-file sha256 (`inputs.parameters.meter.per_file_sha256`, and again in
`code.source.files` which the wrapper derives from what was actually imported)
and the result of running `tests/test_macaulay_fp.py` (52 tests, p = 2 known
answer and planted-syzygy control included) in the SAME process lineage
immediately before the measurement (`inputs.parameters.meter.selftest_in_this_lineage`,
also `raw.meter_selftest`). A failing self-test makes the script refuse to
measure (exit 2); it passed in all six runs.

Dependencies: Python 3.11.15 standard library for every rank; `sympy` 1.14
only for (a) the independent second implementation in the fixture run and
(b) a second primality confirmation; `pyyaml` for the wrapper. No Sage, no
numpy in the computation, no floating point in any rank.

## 2. How each contract field is realised

**inputs.shape / generators.** `digit_presentation(p, m=2, d=2, s=3, system)`
builds the squarefree ring on 6 digit variables (membership a(a-1) is the ring
quotient, so the Hilbert series is (1 + z)^6 and the column space at D <= 6 is
the 64 squarefree monomials), with ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}; the
single explicit generator is S_3(ell_1, ell_2, x_R) reduced in the quotient
(`s3_dict` writes S_3 exactly as `harness/semaev.py::s3_expr`, then
`substitute`). Its degree is 4, giving the contract's null series
(1 + z)^6 (1 - z^4); null d_reg = 5 and D_null = 6 are both recorded in every
manifest (`parameters.conventions` / analysis).

**inputs.primes.** 4099; 2^64 - 59; the P-256 prime. The 64-bit prime is
re-confirmed in the sweep manifests (`parameters.prime_check`): deterministic
Miller-Rabin with the 12 bases 2..37 (deterministic below 3.3e24), `sympy.isprime`,
and an exhaustive Miller-Rabin scan of the 58 integers between it and 2^64
(none prime), so "largest prime below 2^64" holds and the contract's fallback
(nearest prime above 2^64) did NOT fire. The P-256 prime passes both tests.

**inputs.curves.** Per prime, curve k uses seed 1100 + k: A, B =
SHA-256("EXP-PFDR-fd901a:curve:p:seed:A|B:attempt") mod p, rejecting
discriminant 0 or fewer than two x in [0, 8) with x^3 + Ax + B a square (the
rejection counts are in `metrics.curve_rejections`: one rejection in total,
curve seed 1102 at p = 4099, first attempt had one window x). The named NIST
P-256 curve (A = p - 3, B = 0x5ac635d8...2604b, public parameters, recorded in
`parameters.named_curve`) has on-curve window x = {0, 5, 6}, so its cell is
PLANTED (no random-target fallback fired).

**inputs.targets.** Target seed t picks two DISTINCT on-curve window x by
SHA-256("EXP-PFDR-fd901a:target:p:curve_seed:t") (index bits), y-signs from two
further hash bits, R = P_1 + P_2 by the script's own affine addition (distinct
x guarantees an affine sum), x_R = x(R). Certificate
`{kind: decomposition, target, summands, curve}` per draw, RE-VERIFIED by
`harness.semaev.verify_decomposition_certificate` (which uses
`harness.toycurve.EllipticCurve.add`, a code path the planting does not share).
Additionally S~ is evaluated at the planted digit vector and required to be 0
(`stilde_vanishes_at_planted_point`). Both held in all 40 + 40 + 45 Semaev
draws; no `invalid_measurement` draw occurred. Manifest-level
`result.certificate.kind` is `none` (no solve is claimed by any run); the
per-draw certificates and their verification flags are in `raw.draws[*]`.

**controls.CTRL-FROZEN-FIXTURE.** EXP-PFDR-5726af has no run directory, so the
contract's fallback applies: the fixture run compares the meter with an
independent second implementation in the same run -- S~ rebuilt by sympy from
`s3_expr` with symbolic ell_k and a_i^2 -> a_i, dense Macaulay layers built
from that polynomial with `itertools.combinations`, ranks by sympy
`DomainMatrix(...,GF(p)).rank()` and by a naive Gauss-Jordan; compared at every
D in 3..6 on rows, columns, full rank and top rank, plus coefficient-level
equality of S~. All agree (analysis.md section CTRL-FROZEN-FIXTURE).

**controls.CTRL-POSITIVE-P-DEPENDENCE.** `direct_presentation(p, 2, B, system)`
with B = round(sqrt p) = 64 / 128, generators S_3(x_1, x_2, x_R), f_V(x_1),
f_V(x_2); curves 2101..2103 with window [0, B); targets 1..2; per-layer profile
for D = 4..B + 2; recorded per draw: first-fall d_ff, `first_nontrivial_syzygy`,
the first D with top_rank = #monomials(D) (`d_top_full`), and the series d_reg.

**controls.NULL-SUPPORT.** `support_matched_system(ring, [S~], seed)`: the
IDENTICAL monomial support of S~ with fresh coefficients uniform in [1, p-1]
(the meter's construction; a zero coefficient would change the support). Five
draws per (curve, target, p) with the frozen labels 7, 11, 13, 17, 19 mixed
into the RNG seed as SHA-256("EXP-PFDR-fd901a:null:p:curve_seed:target_seed:label")
mod 2^62 (recorded per draw as `rng_seed_mixed`) -- see deviation D3. Not
planted (the contract does not plant it; the flatness label of the null arm is
over null draws only, so no label mixes planted and unplanted objects).

**controls.NEARBY-NON-CURVE-CUBIC.** Per curve seed, t =
SHA-256("EXP-PFDR-fd901a:singular:p:seed:t:attempt") mod p, t != 0, A = -3t^2,
B = 2t^3 (so 4A^3 + 27B^2 = 0, the nodal cubic y^2 = (x - t)^2 (x + 2t)); the
SAME digit generators; x_1 != x_2 chosen among window x with x^3 + Ax + B a
square and x != t; x_R a root of the quadratic S_3(x_1, x_2, X) = 0 (Tonelli-
Shanks), redrawn when the discriminant is a non-residue (`root_attempts` per
draw). Certificate `{kind: s3_root}` re-verified by `harness.semaev.s3_eval`
(independent evaluation); the generator is also checked to vanish at the
planted digits.

**controls.CTRL-SECONDARY-DIRECT-FIXED-B.** Direct presentation at B = 8, m = 2,
at each sweep prime, curves 2101..2103 (seeds re-used from the positive-control
list; the contract names no seeds for this arm -- deviation D4), targets 1..2,
per-layer profile for D = 4..10, inside each sweep run.

**controls.CTRL-NAMED-CURVE.** Inside the P-256 sweep run: 5 planted targets
on NIST P-256 (`arm: semaev_named_p256`) and their 25 support-matched nulls
(`null_support_named_p256`), compared with the random-curve modal profile in
the tail checks.

**controls.CTRL-CONFOUNDERS-NAMED.** No Groebner basis is computed anywhere;
no subset-column rank; no ideal-level invariant; only generator-level graded
ranks are read. Timing and RSS are recorded as covariates only.

**metrics.** Per draw and per D in 3..6 (per-layer, the macaulay.py convention
that defines fall_dim and d_ff in IDEA-20260903-e1e38b D1): row_count,
ncols_full, ncols_top, full_rank, top_rank, fall_dim, syzygy_dim,
koszul_pairwise, pred_rank, deficit_series, deficit_pairwise,
top_deficit_series, nnz, reduction_ops; d_ff = first D with fall_dim > 0;
`first_nontrivial_syzygy` as a second reading; the cumulative-convention
profile as a secondary record for the digit arms. Flatness labels, rank-drop
rates (with exact Clopper-Pearson 95 % intervals computed in `Fraction`
arithmetic) and the Semaev-minus-null table are computed by `analyze.py` from
these records.

**preregistered_prediction.** Frozen, copied into `analyze.py::FROZEN` for the
comparison only; never adjusted. The comparison for (3) pairs draw (curve seed,
target seed[, null seed]) at 2^64 - 59 with the same labels at the P-256 prime
and counts pairs on which EVERY recorded invariant is identical (a modal-
reference count is reported alongside). Rank-drop event at 4099 (4): a Semaev
draw with some full_rank(D) or top_rank(D) STRICTLY BELOW the 64-bit modal
profile; "any difference" is counted separately. Stopping rule 3 uses the
any-difference fraction.

**budget / stopping.** `RLIMIT_AS` = 8 GB and `signal.alarm(3600)` per run;
an alarm raises inside the measurement, is caught, and yields status
`failed_infrastructure` with the partial draws preserved (never fired: the
longest run took 3.3 s wall). Runs were executed strictly in the contract's
order with the stopping rules checked between stages (fixture agreement before
Stage 2; positive control not flat before Stage 3; stopping rule 3 evaluated
by `analyze.py --stop-check-only` after the 64-bit run: any-difference
fraction 0.0, not triggered, before the 256-bit run). Six runs of the twelve
allowed; no re-run was needed.

**run packages.** `runner.write_run` writes manifest.yaml, command.txt,
environment.json, stdout.log, stderr.log, raw-result.json; the manifest
carries commit, dirty flag (false: no tracked file modified), the sha256 of
every executed source file (`code.source.files`, including the meter modules
and the run script), the inference block, wall time, peak RSS, cpu seconds,
seeds and parameters. `checksums.sha256` (sidecar, written once, never
rewritten) lists the sha256 of the six files, since a manifest cannot contain
its own hash. `stderr.log` is empty in every run: nothing was written to
stderr (the shell-level capture of the process stderr was also empty).

## 3. Deviations and conventions (all recorded, none silent)

- **D1 (wrapper bracket).** `harness.runner.run_wrapped` requires the terminal
  status before the run function executes, but the status of these runs
  (`completed_valid | failed_infrastructure | invalid_measurement`) is decided
  by the measurement. The script therefore reproduces `run_wrapped`'s body
  verbatim (wall clock + monotonic bracket around the run function, then
  `write_run(..., wall_seconds=t1 - t0)`) and passes the decided status;
  `timing.timing_source` reads "run_experiment.py bracket (harness.runner.run_wrapped
  body verbatim; status decided after fn)" so no manifest claims a bracket it
  did not have. Timing is a covariate, never a metric, in this contract.
- **D2 (fixture second implementation).** EXP-PFDR-5726af has not run;
  the contract's own fallback (independent second implementation in the same
  run) was used, as described above.
- **D3 (null RNG seeds).** The frozen null seeds 7, 11, 13, 17, 19 are mixed
  with (p, curve seed, target seed) into the RNG seed. Used verbatim, the same
  seed on the same support would have produced the IDENTICAL null polynomial
  for every (curve, target), collapsing 40 draws to 5 objects per prime. The
  mixed integer is recorded per draw.
- **D4 (secondary-arm seeds).** The contract names no seeds for
  CTRL-SECONDARY-DIRECT-FIXED-B (3 curves, 2 targets); the positive-control
  seeds 2101..2103 / 1..2 were used and recorded.
- **D5 (positive-control reading).** The frozen prediction states
  "d_ff = B + 1" (65 / 129). Under the contract's d_ff definition (first degree
  with fall_dim > 0 in the per-layer Macaulay matrix, the same definition used
  for every other arm) the measured first fall is B + 2 (66 / 130) in all 12
  draws, while the first degree at which the top block reaches full column
  rank -- the observable that equals the semi-regular series d_reg = B + 1 of
  IDEA-20260808-093497 -- is exactly 65 / 129. Both readings are reported in
  `analysis.md`; the prediction is not adjusted and no reading is re-scored.
  The control's forced disposition "strictly increasing from 4099 to 16411"
  holds under either reading, so stopping rule 2 (flat control) did not fire.
- **D6 (D = 3 layer).** With one generator of degree 4, the per-layer matrix
  at D = 3 has no rows; all its invariants are 0 and are recorded as such
  (the contract lists D in 3..6).
- **D7 (git reads).** The handoff says "never run git"; the wrapper itself
  runs read-only `git rev-parse` / `git status` / `git show` / `git ls-files`
  to pin the commit and hashes, and the executor ran the same read-only
  commands to confirm the approval commit. No git write of any kind; nothing
  committed.
- **D8 (deliverable name).** The handoff names `execution-report.yaml`; the
  task text says `execution_report.yaml`. The handoff (authoritative) name is
  used.
- **D9 (helper artifacts).** Smoke tests were written only under the session
  scratchpad (`--out-root`), never under `experiments/`. Empty shell-redirect
  files created during the run chain were removed before the package was
  declared; `__pycache__` directories are gitignored.

## 4. Inference block

Every manifest carries `run.inference` written by the wrapper. As written it
reads `requested_policy: executor-terra`, `resolved_model_id: none
(deterministic harness execution)`, `fallback_used: false`: `harness/runner.py`
defines `_inference_block` twice and the later constant definition (line 701)
shadows the adapter-aware one (line 183), so the wrapper records a harness
default rather than the handoff's policy. `harness/` is outside this task's
write scope and was not changed; the finding is reported (deviation D9,
anomaly A4). The run is deterministic code with no model in its loop. The
handoff's policy is recorded in `inputs.parameters.executor_session_inference`
for the executing SESSION: requested policy executor-implementation at medium
effort; adapter resolution `anthropic:claude-sonnet-5 (effort=medium)`;
runtime-reported model `claude-fable-5-1`; `model_verified: false` and
`fallback_used: unknown` because the two identifiers differ and cannot be
reconciled from inside the session (the same disclosure as the meter's
VALIDATION.md section 11); `independent_session: true`; no Bedrock, no
degradation.

## 5. Reproduction

From repository root at commit 3a9c1b02 with the untracked
`experiments/EXP-PFDR-fd901a/run_experiment.py` at the sha256 recorded in each
manifest's `code.source.files`:

```
python3 experiments/EXP-PFDR-fd901a/run_experiment.py fixture
python3 experiments/EXP-PFDR-fd901a/run_experiment.py posctrl-4099
python3 experiments/EXP-PFDR-fd901a/run_experiment.py posctrl-16411
python3 experiments/EXP-PFDR-fd901a/run_experiment.py sweep-4099
python3 experiments/EXP-PFDR-fd901a/run_experiment.py sweep-64
python3 experiments/EXP-PFDR-fd901a/analyze.py --stop-check-only   # stopping rule 3
python3 experiments/EXP-PFDR-fd901a/run_experiment.py sweep-256
python3 experiments/EXP-PFDR-fd901a/analyze.py
```

(`--out-root DIR` redirects a run package elsewhere; run ids are immutable and
the wrapper refuses to overwrite an existing one.) The executor re-ran the
fixture and the 64-bit sweep from these commands into the scratchpad and found
`metrics` and `raw` (minus the self-test timing) byte-identical to the recorded
runs; see execution-report.yaml `completion_gate`.
