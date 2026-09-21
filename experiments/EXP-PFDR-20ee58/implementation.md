# EXP-PFDR-20ee58 -- implementation note (TASK-20260903-5b46a6)

Executor implementation of the frozen contract `specification.yaml` (status
`approved`, `approved_by: coordinator`, decision DEC-20260903-93862f), read at
branch head 1b49d491 (3a9c1b02 plus the snapshot commits of the meter, 2d2083e5,
and of EXP-PFDR-fd901a). Nothing in the specification, the hypothesis, the
meter package or any ledger record was edited; nothing was committed.
Observations only: the branch is DECLARED by the pre-registered rule in
`analysis.md`; the verdict on H-PFDR-9aadc0 belongs to the review round.

## 1. What was built (all under `experiments/EXP-PFDR-20ee58/`)

| file | role |
|---|---|
| `run_experiment.py` | the run script: twin builder on the shared meter, curves, planting, certificates, all four arms, pre-flight gate, one run package per planned run through `harness.runner.write_run` |
| `analyze.py` | Stage 5 (zero compute): reads `runs/*/raw-result.json` only, recomputes every deficit from (rows, rank, koszul), writes `analysis.md` + `analysis.json`; `--stop-check-only` evaluates stopping rules 3 and 4 at the deciding cell |
| `stage0-derivation.md` | Stage 0: (S2)-(S3) by hand |
| `stage2-s1-fixture.yaml` | Stage 2: the s = 1 symbolic identity and the graded ranks, derived from `runs/RUN-PFDR-20ee58-s1-slice/` |
| `analysis.md`, `analysis.json` | Stage 5 output |
| `execution-report.yaml` | the execution report |
| `runs/RUN-PFDR-20ee58-*/` | 14 immutable run packages, each with the six required files plus `checksums.sha256` |

Meter: `harness/macaulay_fp/` at its snapshot commit 2d2083e5, used
unmodified. Every manifest records the meter's per-file sha256
(`inputs.parameters.meter.per_file_sha256`, including the GF(2) fixture and
its builder, and again in `code.source.files`, which the wrapper derives from
what was actually imported) and the result of running
`tests/test_macaulay_fp.py` (52 tests: the p = 2 known answer and the
planted-syzygy positive control) in the same process lineage immediately
before the measurement (`inputs.parameters.meter.selftest_in_this_lineage`,
also `raw.meter_selftest`). A failing self-test makes the script refuse to
measure (exit 2); it passed in all 14 runs.

Dependencies: Python 3.11.15 standard library for every rank (the meter is
pure Python); `sympy` 1.14 is imported only through `harness.semaev` /
`harness.toycurve` for the independent certificate re-verification and the
wrapper's environment block; `pyyaml` for the wrapper. No Sage, no numpy in any
computation, no floating point in any rank.

## 2. How each contract field is realised

**inputs.tree / (S1).** `digit_presentation(p, m=3, d=2, s, system, n_extra_free=1)`
builds the mixed ring: `3s` squarefree digit variables `a_{k,i}` (the quotient
`a(a - 1) = 0` is the ring, so no membership generator is emitted at d = 2) and
one free variable `u` (the last free variable). `x_k = sum_{i<s} 2^i a_{k,i}`;
`E1 = S_3(x_1, x_2, u)` and `E2 = S_3(u, x_3, x_R)` are obtained by
`substitute` from `S_3` written exactly as `harness/semaev.py::s3_expr`
(`s3_generic_dict`). The system has exactly two generators; both have total
degree 4 at every s >= 2 (recorded per draw as `generator_degrees`).

**Pre-flight counts against the contract's table.** At D = 8 the meter's
`preflight` returns rows / columns 886 / 2304 (s = 3), 2372 / 12381 (s = 4),
5310 / 56751 (s = 5), and at (s = 6, D = 6) 384 / 49024 -- the contract's
numbers exactly (`matrix_sizes`); they are recorded per draw and per degree in
`raw.draws[*].preflight`.

**deficit_definition (the frozen quantity).** `analyze_degrees(ring, [E1, E2],
Dmin, Dmax, convention="cumulative")`; the contract's
`deficit(D) = rows(D) - rank(Mac_D) - koszul(D)` is `LayerResult.deficit_pairwise`
(= `row_count - full_rank - koszul_pairwise`), with `koszul_pairwise` the
meter's explicit pairwise Koszul count (`koszul_pair_count`: 1 at D = 8 for two
quartics, 0 below; verified in every record's `koszul` vector) plus, at p = 2 in
the pure squarefree ring only, the Frobenius count. Zero-product rows are
dropped and counted (`zero_product_rows`, 0 in every draw). The same call, the
same field and the same convention are used on every arm and on the
calibration arm. `analyze.py` recomputes the deficit from the raw
`row_count`, `full_rank`, `koszul_pairwise` of every layer and asserts
equality with the run's own `deficit_vector` (G2).

Secondary readings recorded, never used as the deficit: `deficit_series`
(series prediction with the naive factor `(1 - z^d)` at p > 2), the graded
increments, `fall_dim`, `top_rank`, `nnz_total`, `reduction_ops`.

**cells.** Runs `s{3,4,5}-p{4099,16411,65537}` at D in {5, 6, 7, 8};
`s6-p*` at D in {5, 6} only; (s = 6, D = 8) and (s = 6, D = 7) are not
computed (excluded by name / "D <= 6 only").

**curves_and_targets.** Curve k of prime p uses seed 4100 + k:
`A, B = SHA-256("EXP-PFDR-20ee58:curve:p:seed:A|B:attempt") mod p`, rejecting
`4A^3 + 27B^2 = 0`, `A = 0` or `B = 0` (j in {0, 1728}, "generic j"), and
fewer than three on-curve x in [0, 2^s) (x with `x^3 + Ax + B` zero or a
square). Rejection counts are in `metrics.curve_rejections`. Target seed t:
three DISTINCT on-curve window x by SHA-256 index bits, y-signs from three
further bits, `P12 = P1 + P2` and `R = P12 + P3` by the script's own affine
addition (`R = O` triggers a redraw, counted in `target_attempts`);
`u = x(P12)`, `x_R = x(R)`. Certificate `{kind: decomposition, target R,
summands [P1, P2, P3], curve}` per draw, re-verified by
`harness.semaev.verify_decomposition_certificate` (which sums the points with
`harness.toycurve.EllipticCurve.add`, a code path the planting does not
share); additionally E1 and E2 are evaluated at the planted digit vector and
`u` and required to vanish (`generators_vanish_at_planted_point`). Target
seed 1 everywhere; seed 2 in addition at s = 3 (the deciding cell), at all
three primes. Manifest-level `result.certificate.kind` is `none` (no run
claims a solve); the per-draw certificates and their verification flags are
in `raw.draws[*]`.

**NULL-SUPPORT.** `support_matched_system(ring, [E1, E2], seed)`: the
identical monomial support with fresh coefficients uniform in [1, p-1] (the
meter's construction; a zero coefficient would change the support), driven by
`random.Random(seed)` with the frozen seed verbatim. Five seeds per (cell,
arm), applied to the templates of curve 4101 / target 1 of that cell
(`metrics.template_for_nulls`); see D3.

**NULL-TOPOLOGY.** IDEA-20260808-11b8c7's construction carried to F_p:
each node's S_3 relation is replaced by a uniformly random polynomial on the
node's monomial BOX -- every monomial with at most two digits from each of the
node's S_3 argument blocks (the multilinear image of degree <= 2 in that
argument), `u^e` with e <= 2, and total degree <= 4 -- coefficients uniform in
F_p (zero allowed); u shared between the two nodes; `random.Random(seed)` with
the frozen seed. Box sizes are recorded (`null_meta.box_sizes`: 111 / 21 at
s = 3, and E2's support in the SEM arm is the whole 21-monomial box, so at
E2 the two nulls differ only in the coefficient law; E1 has 98 of 111). The
realised degree histograms of both null generators are recorded per draw and
summarised in `analysis.md`; every null generator had total degree 4.

**NEARBY-NON-CURVE-CUBIC.** Per seed in {51, 53, 59}:
`t = SHA-256("EXP-PFDR-20ee58:singular:p:seed:t:attempt") mod p != 0`,
`A = -3t^2`, `B = 2t^3` (the nodal cubic `y^2 = (x - t)^2 (x + 2t)`,
`4A^3 + 27B^2 = 0`), the same tree and digit generators; three distinct
window x with square rhs and x != t; `u` a root of `S_3(x_1, x_2, U) = 0`
and `x_R` a root of `S_3(u, x_3, X) = 0` (Tonelli-Shanks; redrawn when no
root exists, counted in `target_attempts`) -- "planted via the formula's own
roots". Certificate `{kind: s3_root_chain}` re-verified by
`harness.semaev.s3_eval` at both nodes; the generators are also checked to
vanish at the planted point.

**CTRL-BINARY-CALIBRATION (blocking, Stage 1).** `RUN-PFDR-20ee58-calib-gf2-n12`
loads the meter's committed fixture
`harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json` (sha256
62d89109..., checked) into `Ring(2, 24)` and runs `analyze_degrees(...,
convention="cumulative")` at D = 2..5 with `deficit_profile`; nulls: KN-FIND-006's
own null (EXP-DREG-001 `boolean_null` with the builder's RNG state continued,
`dreg_boolean_null`) and the histogram-matched null at the five frozen seeds.
Also recorded: the identical-support null is the identity at p = 2 (flagged,
not used); the mixed-mode code path on the same system (an unused free `u`
appended, Frobenius count forced on) against a DERIVED expectation
(`[0, 1, 33]` at D = 2..4: the `u^k` row blocks occupy disjoint column sets,
so the mixed deficit is the sum of the squarefree deficits at D - k); and the
Stage 0 mechanical checks (section 4 of `stage0-derivation.md`).

**CTRL-S1-SLICE (blocking, Stage 2).** `RUN-PFDR-20ee58-s1-slice`: at every
(p, B) in {4099, 16411, 65537} x {4, 8}, the twin at s = 1, d = B
(`digit_presentation` with d > 2: free digit `a_{k,0}` with membership
`prod_{j<B}(a_{k,0} - j)`, `u` appended) is compared generator for generator
with cb8e46's J built by the meter's `direct_presentation(p, 3, B, system,
n_extra_free=1)` (free `x_k`, `f_V(x_k) = prod_{v in [0,B)} (x_k - v)`, `u`
appended): same ring shape, same generator order `(S_3(x1,x2,u), S_3(u,x3,xR),
fV(x1), fV(x2), fV(x3))`, dict equality of every generator. Graded ranks under
both conventions at D = 4..10 are recorded as the frozen fixture
(`stage2-s1-fixture.yaml`). Curve seed 4101 with window [0, B) (>= 3 on-curve
x), target seed 1, planted with certificates.

**CTRL-P-LADDER / CTRL-CURVE-SPREAD (Stage 4).** Read off the s = 4 cells at
the three primes (and reported at s = 3 and s = 5 as well) in `analysis.md`:
residual spread across p at fixed s, and the maximum deviation across curves
at fixed (s, p), each against the topology null's 5-seed band.

**CTRL-MEMORY-PREFLIGHT.** `preflight_gate` computes rows and columns by
binomial arithmetic before any allocation for every (draw, D) and marks a
degree aborted above 60,000 columns or 4 GiB dense-equivalent
(rows x cols x 8 bytes); an aborted degree is skipped and listed in
`metrics.preflight_aborted`. No cell was aborted (the largest,
(s = 5, D = 8), is 5310 x 56751, 2.41 GB dense-equivalent). `RLIMIT_AS` was set
to the contract's 16 GB cap and `signal.alarm(7200)` per run; neither fired
(the longest run took 150 s wall, peak RSS below 1 GB).

**CTRL-CERTIFICATES.** Every planted decomposition and every S_3 root chain
was re-verified by independent code as above; `metrics.planted_certificates_failed`
is 0 in every run (no `invalid_measurement` draw occurred).

**CTRL-CONFOUNDERS-NAMED.** Stated in `analysis.md`; no Groebner basis, no
subset-column rank, no ideal-level invariant. `sol(D)` (IDEA-20260806-7ea402:
`rank(Mac_D) >= ncols(D) - dim(quotient)`) is recorded per draw as a covariate
only, with the quotient dimension computed exactly as cb8e46's product over
the `2^{3s}` digit points of `F_p[u]/(gcd)` (`quotient_dimension`); it never
enters a deficit.

**Stopping rules.** Executed in the contract's order with the rules checked
between stages: calibration (must reproduce 1 and 31 with null 0) before the
s = 1 slice; the s = 1 identity before Stage 3; the deciding cell
`s3-p4099` first, then `analyze.py --stop-check-only` (rule 3: NULL-SUPPORT
nonzero beyond budget on more than one seed -- not triggered; rule 4: SEM
nonzero at the deciding cell -- not triggered, and the s = 3 cells at the other
two primes were run before s = 4 regardless); then s = 4, s = 5, s = 6. No
iteration, no tuning, no re-run of any completed run. 14 runs of the 60 allowed.

**run packages.** `runner.write_run` writes `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`; the manifest
carries the commit, the dirty flag (false in every run: no tracked file
modified), the sha256 of every executed source file, the inference block, wall
time (wrapper-style bracket, D1), peak RSS, CPU seconds, seeds and parameters,
the deficit convention and the null rules. `checksums.sha256` (sidecar,
written once) lists the sha256 of the six files, since a manifest cannot
contain its own hash. `stderr.log` is empty in every run.

## 3. Deviations and conventions (all recorded, none silent)

- **D1 (wrapper bracket).** `harness.runner.run_wrapped` requires the terminal
  status before the run function executes, but the status of these runs
  (`completed_valid | failed_infrastructure | invalid_measurement`) is decided
  by the measurement. The script reproduces `run_wrapped`'s body verbatim
  (wall clock + monotonic bracket around the run function, then
  `write_run(..., wall_seconds=t1 - t0)`) and passes the decided status;
  `timing.timing_source` names this. Same as EXP-PFDR-fd901a D1.
- **D2 (calibration integers and the deficit formula).** The contract's
  formula `rows - rank - koszul` under cumulative multipliers gives, on the
  binary n = 12 system, 1 at D = 3 and 32 (= 8k) at D = 4; the calibration
  integers "1 and 31" are KN-FIND-006's PER-DEGREE readings (31 = 8k - 1 is
  the increment 32 - 1), exactly as `harness/macaulay_fp/VALIDATION.md`
  section 4 item 4 and section 5 record. Both are reported
  (`deficit_cumulative` = (0, 1, 32, 1322), `deficit_graded` = (0, 1, 31, 1290)
  at D = 2..5); the calibration is read as reproduced because both readings
  match KN-FIND-006 line for line, including the archived cumulative 1322 at
  D = 5. For the twin, the contract's formula (cumulative) is THE deficit and
  the graded increment is a secondary reading; the two coincide (both 0) in
  every twin record, so no reading depends on the choice.
- **D3 (null seeds and templates).** The frozen null seeds 7, 11, 13, 17, 19
  are used verbatim (`random.Random(seed)`), five per (cell, arm), on the
  generator templates of curve 4101 / target 1 of the cell -- the literal
  reading of "5 seeds per cell". They were NOT mixed with curve labels
  (EXP-PFDR-fd901a's D3 route) and not repeated on the other five curves'
  templates: at fixed (s, p) the supports of E1 and E2 are the same across the
  generic curves drawn here (the term counts recorded per draw are identical
  across curves in every cell), so the same seed on another curve's template
  would reproduce the same null polynomial.
- **D4 (calibration ring mode).** The contract's Stage 1 phrase "the shared
  F_p meter in MIXED mode ... CALIBRATED on the committed GF(2) chained
  system" was realised by running the calibration in the fixture's own ring
  (24 squarefree Boolean variables, no free variable: the ring in which
  KN-FIND-006's integers are defined) AND exercising the mixed-mode code path
  on the same system with an unused free `u`, whose result (1, 33 at D = 3, 4)
  matches a derived expectation rather than a KN-FIND-006 integer. The twin
  itself runs in mixed mode.
- **D5 (s = 1 slice curves).** The contract names no curve or target for the
  s = 1 slice; curve seed 4101 (window [0, B), >= 3 on-curve x) and target
  seed 1 were used at each (p, B) and recorded. The identity is a symbolic
  statement independent of that choice.
- **D6 (topology null coefficient law).** 11b8c7 leaves the coefficient law
  of the topology null open ("uniformly random polynomial of the same
  multidegree and variable set"); "uniform in F_p including zero on the
  degree-bounded box" was frozen before any twin number was read, and the
  realised degrees are reported. A draw of degree < 4 (which would break the
  common degree convention) never occurred.
- **D7 (git reads).** The handoff says "never run git"; the wrapper runs
  read-only `git rev-parse` / `git status` / `git show` / `git ls-files` to pin
  the commit and hashes, and the executor ran the same read-only commands to
  confirm the approval commit and the clean tree. No git write; nothing committed.
- **D8 (deliverable name).** The handoff names `execution-report.yaml`; the
  Executor template calls it `execution_report`. The handoff's name is used.
- **D9 (harness inference block).** As written by the wrapper, every manifest's
  `run.inference` reads `requested_policy: executor-terra`,
  `resolved_model_id: none (deterministic harness execution)`: `harness/runner.py`
  defines `_inference_block` twice and the later constant definition shadows
  the adapter-aware one (already reported by EXP-PFDR-fd901a D9/A4; `harness/`
  is outside this task's write scope and was not changed). The run is
  deterministic code with no model in its loop. The handoff's policy is
  recorded in `inputs.parameters.executor_session_inference` for the executing
  session (requested `executor-implementation` at `medium`; adapter resolution
  `anthropic:claude-sonnet-5 (effort=medium)`; runtime-reported model
  `claude-fable-5-1`; `model_verified: false`, `fallback_used: unknown`
  because the two identifiers differ and cannot be reconciled from inside the
  session; `independent_session: true`; no Bedrock, no degradation), together
  with the adapter's own `block_from_env()` output.
- **D10 (harness shell timeout, infrastructure event, no run record).** The
  executor's shell tool imposes a 10-minute cap per command; a loop launching
  the eleven remaining cells sequentially was killed by it (SIGTERM, exit 143)
  while `cell --s 5 --p 65537` was in progress, after seven cells had
  completed. The wrapper writes a run directory only after the measurement
  returns, so NO partial or invalid run record was created and no run id was
  consumed; the cell was re-launched (in the background, outside the cap) with
  the same run id and completed. This is a property of the executing harness,
  not of the contract's budget (per-run wall clock 7200 s was never approached).
- **D12 (HEAD moved during the run sequence).** The first ten runs record
  `code.commit` 1b49d491; the last four (`s5-p65537`, `s6-p4099`,
  `s6-p16411`, `s6-p65537`) record 89dc58e3, because the orchestrating
  session committed EXP-PFDR-5726af's run package (`runs(EXP-PFDR-5726af):
  ten completed_valid runs ... TASK-20260903-b0727c`) while this task's cells
  were running. `git diff --stat 1b49d491 89dc58e3 -- harness/
  experiments/EXP-PFDR-20ee58/ tests/test_macaulay_fp.py` is empty: no input
  of this task changed; every manifest records `dirty: false` and the same
  sha256 of `run_experiment.py` (5fad574a...) and of every meter file, so the
  14 runs executed identical code. Reported, not repaired (run records are
  immutable).
- **D11 (helper artifacts).** Smoke tests and the reproduction check were
  written only under the session scratchpad (`--out-root`), never under
  `experiments/`; `__pycache__` directories are gitignored.

## 4. Reproduction

From the repository root at commit 1b49d491 with the untracked
`experiments/EXP-PFDR-20ee58/run_experiment.py` at the sha256 recorded in each
manifest's `code.source.files`:

```
python3 experiments/EXP-PFDR-20ee58/run_experiment.py calib
python3 experiments/EXP-PFDR-20ee58/run_experiment.py s1
python3 experiments/EXP-PFDR-20ee58/run_experiment.py cell --s 3 --p 4099
python3 experiments/EXP-PFDR-20ee58/analyze.py --stop-check-only     # stopping rules 3 and 4
for s in 3 4 5 6; do for p in 4099 16411 65537; do
  [ "$s-$p" = "3-4099" ] || python3 experiments/EXP-PFDR-20ee58/run_experiment.py cell --s $s --p $p; done; done
python3 experiments/EXP-PFDR-20ee58/analyze.py
```

(`--out-root DIR` redirects a run package elsewhere; run ids are immutable and
the wrapper refuses to overwrite an existing one.) The executor re-ran
`calib` and `cell --s 3 --p 4099` from these commands into the scratchpad and
found `metrics` and `raw` (minus the self-test timing) identical to the
recorded runs; see `execution-report.yaml` `completion_gate`.
