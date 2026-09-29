# EXP-MONO-7c653b — Implementation notes

Single-file harness: `experiments/EXP-MONO-7c653b/implementation/run_experiment.py`.
Invoked as `python3 run_experiment.py <seed> <outdir>`; writes `<outdir>/raw-result.json`.

Reuses `harness/semaev.py`'s `s3_expr`, `s4_expr` and `harness/toycurve.py`'s
`EllipticCurve`, `_sqrt_mod` directly (imported, not reimplemented). Pure
Python 3 stdlib + sympy (1.14.0), matching the frozen contract's dependency
constraint. No modification was made to either shared module.

## `s5_expr`: local copy, disclosed reason

The contract and handoff ask whether `s5_expr` is added to the shared
`harness/semaev.py` or written as a local copy, with an explicit instruction
not to silently duplicate the existing resultant pattern if extending the
shared module is equally viable.

**This run defines `s5_expr` LOCALLY in
`implementation/run_experiment.py`, not in `harness/semaev.py`.** The reason
is not a stylistic preference: this task's own operating instructions
explicitly restrict this session's writes to
`experiments/EXP-MONO-7c653b/` and explicitly prohibit any `git` command in
this shared worktree (a different, unrelated concurrent session currently
owns this branch). Extending `harness/semaev.py` -- a shared file outside
that declared scope -- was therefore not an equally viable option for this
run, so the "do not silently duplicate if extension is viable" clause does
not bind here; a local definition is the correct choice under the
constraint actually in force, and is disclosed here rather than silently
assumed. `s5_expr(a, b, v1, v2, v3, v4)` follows the IDENTICAL pattern
`s4_expr` already uses -- `S_5 = Res_U(S_4(x1,x2,x3,U), S_3(x4,T,U))` -- but
takes NUMERIC coordinates `v1..v4` and substitutes them before the
resultant elimination (`S4.subs({x1:v1,x2:v2,x3:v3}).subs(x4,U)`, then
`resultant(..., s3_expr(a,b).subs({x1:v4,x2:T,x3:U}), U)`), returning a
sympy expression in `T` alone. This numeric-first-then-resultant order is
the same tractability precedent EXP-MONO-805a02's own Stage 2 established
(`build_s5_root_set_and_deg`) and is required by the contract for this
reason.

`s5_expr` is guarded by a hard `signal.SIGALRM`-based 300-second timeout
(`s5_expr_with_timeout`) per the frozen contract's own stopping rule ("If
the s5_expr resultant elimination fails to terminate within 300 seconds at
either p, abort that cell as failed_infrastructure"). This timeout was
never triggered in either official run (measured per-tuple m=5 cost was a
small fraction of a second; see Timing below).

## Seed-derivation rule: exact formula, and one disclosed resolution

Implemented exactly as `inputs.seed_derivation_rule` specifies: for a draw
in `[0, M)`, `digest = SHA256(domain + "|" + label + "|" + decimal(p) + "|"
+ decimal(m) + "|" + decimal(counter))`, `h = int(digest, 16)`, reject if
`h >= floor(2**256 / M) * M`, else accept `h % M`; `counter` starts at 0 and
advances once per digest CONSUMED (accepted or rejected), per label, per
`(p, m)` cell. `draw_distinct()` uses this stream to sample `k` distinct
elements from a base list via sequential pop-without-replacement (fully
determined by the stream's running counter state). Labels used, exactly the
three the contract names: `"twisted-fb-tuple"` (Stage 3 tuple draws),
`"mutant-tuple"` (Stage 4a tuple draws), `"mutant-delta-prime"` (Stage 4a's
wrong rescaling constant). Stage 1's fixture-triple draw uses a fourth label,
`"fixture-triple"`, which the contract's own `battery.STAGE1-HARD-GATE-
FIXTURE` text names explicitly even though it is absent from the three-item
list under `inputs.seed_derivation_rule`; both are read together as the
authoritative label set (four labels total across the whole battery), not as
a conflict.

**DISCLOSED RESOLUTION, not a silent substitution.** The contract's own
formula (`domain || "|" || label || "|" || p || "|" || m || "|" || counter`)
does not itself include `master_seed` as a hash component, yet the same
clause requires "a third party reproduces every instance bit-for-bit from
`(master_seed, domain, label, p, m, counter)`" -- master_seed must
therefore enter somewhere, and the only place left is `domain` itself.
EXP-MONO-805a02 resolved the identical tension in its own domain string by
folding the run's master_seed into a per-run domain suffix
(`"EXP-MONO-805a02/v1/run-20260830"`). This run follows that exact
precedent: `domain = f"EXP-MONO-7c653b/v1/run-{seed}"`. This is verified to
matter: RUN-MONO-7c653b-1 (seed 20260905) and RUN-MONO-7c653b-2 (seed
20260906) draw genuinely different Stage 3/4a tuples and a genuinely
different Stage 4a `delta'` (102 vs. 206; see `independent_sample_check`
and `stage4a.delta_prime` in each run's own `raw-result.json`), which is
what this contract's own `replication.independent_instances: 2` requires.
Had `domain` been the bare literal `"EXP-MONO-7c653b/v1"` with no per-seed
suffix, the two "replication" runs would have drawn IDENTICAL samples under
different nominal seeds -- exactly EXP-MONO-805a02's own disclosed Stage-2
protocol deviation, which this resolution avoids rather than repeats.

## Factor-base constructions (deterministic, no randomness)

- **Twisted factor base** (`twisted_factor_base`): exactly
  `inputs.non_residue_and_delta_construction` -- ascending-x scan
  `x=0,...,p-1`, accept `x` iff `f(x) != 0 mod p` and
  `pow(f(x), (p-1)//2, p) == p-1` (strict Euler-criterion non-residue). The
  first accepted `x` is `DELTA_SOURCE`; `delta = f(DELTA_SOURCE) mod p`. The
  full ordered accepted list is the twisted factor base; its size and the
  SHA-256 digest of its canonical decimal-lines encoding are computed
  BEFORE any Stage-3/4a tuple is drawn (this order is enforced by the code
  structure: `twisted_factor_base()` runs to completion, including the
  digest, before any `SeedStream` for `"twisted-fb-tuple"` is consulted).
  Measured: `p=211` -> 100 non-residue x's, `delta=57`,
  digest `f4491f21...`; `p=1009` -> 473 non-residue x's, `delta=19`,
  digest `3fe9d721...` (both digests identical across both official runs,
  confirming the construction is seed-independent as required).
- **On-curve factor base** (`on_curve_factor_base`, Stage 1 only):
  analogous ascending-x scan selecting `x` with `f(x)` a NONZERO quadratic
  RESIDUE (`pow(f(x), (p-1)//2, p) == 1`), i.e. genuine non-ramified
  on-curve x-coordinates. The contract does not spell out this
  construction explicitly beyond "drawn from the on-curve factor base"; this
  is the natural residue-analogue of the twisted-factor-base construction
  the contract DOES spell out, and is disclosed here as the reading used.

## Stage 1 (hard gate)

Draws 193 triples of 3 distinct x-coordinates from the p=211 on-curve
factor base under label `"fixture-triple"`, specializes `s4_expr(37,57)` at
`x1,x2,x3`, and factors the resulting degree-4-in-`x4` polynomial mod 211
(see "Polynomial split analysis" below for why the degree is 4, not 8).
Both official runs: 193/193 `split_with_multiplicity`, 193/193
`split_distinct`, 193/193 root-set match against the group-law prediction
`{x(+-P1+-P2+-P3)}`. **Gate passes in both runs; Stages 3 and 4a were
interpreted in both.**

Reconstruction caveat identical to EXP-MONO-805a02's own disclosed one: the
literal historical 193 triples from KN-FIND-c41ea9's census are not
committed anywhere machine-readable, so this is a freshly, deterministically
seeded 193-triple sample of the IDENTICAL construction, not the literal
historical triples.

## Polynomial split analysis: multiplicity-aware AND distinct, always separate

`poly_split_analysis()` builds `sympy.Poly(expr, var, modulus=p)` (computing
the degree correctly OVER F_p directly via the `modulus=` argument, which
avoids EXP-MONO-805a02's own documented "degree drop" bug from computing the
degree over Z first). It reports, as two SEPARATE fields, never pooled:
- `split_with_multiplicity`: does the sum of multiplicities of all
  degree-1 irreducible factors (via `Poly.factor_list()`) equal the
  polynomial's own degree? (Product-of-linear-factors, repeats allowed.)
- `split_distinct`: does the count of DISTINCT roots found by brute-force
  evaluation over `range(p)` equal the degree? (No repeated root.)

It also reports the full `factor_degree_multiset` (every irreducible
factor's degree, with multiplicity) per specialization, aggregated per cell
into the Stage-3 secondary metric. Observed: EVERY factor at EVERY tested
(m,p) cell in both runs has degree exactly 1 (no irreducible factor of
degree >= 2 was ever observed) -- i.e. every tested j=m-1 specialization
splits completely into linear factors with multiplicity; `split_distinct`
alone occasionally reads slightly below 1.000 at some cells (a repeated
root, not a partial split) -- see Stage 3 results below.

**Degree note (not a bug, a structural fact of the fixture):** `deg_T S4 =
4`, not 8, because `x(P) = x(-P)` always, so the 8 sign vectors
`{+-eps_1,+-eps_2,+-eps_3}` collapse pairwise (global sign flip) into 4
distinct x-values. Analogously `deg_T S5 = 8` for `m=5` (16 sign vectors
collapsing to 8 x-values). Both are the affine degree of the ACTUAL
specialized polynomial mod p, as reported by `sympy.Poly(..., modulus=p)`,
and both match the observed `factor_degree_multiset` totals per cell.

## Stage 3 (twist-cost-identity exact-match test)

For each `(m,p)` cell (m in {4,5}, p in {211,1009}; n=500 for m=4, n=200
for m=5), draws n tuples of `m-1` distinct x-coordinates from that p's
twisted factor base under label `"twisted-fb-tuple"`. For each tuple:

- **Direct route**: specialize `s4_expr`/`s5_expr` and run
  `poly_split_analysis`, taking the DISTINCT root set as the direct-route
  x(Q) set.
- **Twist route**: for each `x_i`, `y_i' = sqrt_mod(f(x_i) * inverse(delta)
  mod p, p)` (via `harness.toycurve._sqrt_mod`, the same primitive
  `EllipticCurve.lift_x` itself uses); construct
  `E_delta = EllipticCurve(p, a*delta*delta % p, b*delta**3 % p)` (NO
  modification to `EllipticCurve` -- direct instantiation, per the
  contract); for every sign vector in `{+1,-1}^{m-1}` with the first sign
  fixed to `+1` (`2**(m-2)` distinct sign classes), fold in all `m-1`
  signed points via `EllipticCurve.add`, starting from `acc = None` (the
  point at infinity) so that folding `m-1` points costs EXACTLY `m-1`
  `.add()` calls (not `m-2`); rescale `x(Q) := X(R) * inverse(delta) mod
  p`.
- **Compare**: SET equality between the direct-route root set and the
  twist-route x(Q) set, per tuple.

**Result, both official runs, every (m,p) cell: exact-match rate = 1.000
(no exceptions, no mismatches, `first_mismatch: null` in every cell of both
runs' `raw-result.json`).** `split_with_multiplicity` rate = 1.000 at every
cell in both runs (byproduct sanity check against H-MONO-45183a Part A, not
a re-test of the general claim). `split_distinct` rate is 1.000 at
`m4_p211` in both runs and reads slightly below 1.000 at the other three
cells (0.99/0.992 at `m4_p1009`, 0.94/0.925 at `m5_p211`, 0.955/0.945 at
`m5_p1009`, run 2 / run 1 respectively) -- in every such case
`split_with_multiplicity` is still 1.000, meaning the polynomial still
splits completely into linear factors, just with an occasional repeated
root (two different sign combinations coinciding in x by a rare genuine
coincidence, matching EXP-MONO-805a02's own documented explanation for the
identical phenomenon).

**Operation-count reconciliation** (reported beside, never folded into,
H-MONO-40aca5's own `D_trial(E)=m-1` count for j=0): per attempt, exactly
`m-1` `EllipticCurve.add` calls (instrumented directly via an `AddCounter`
wrapper on `E_delta.add`, exactly as EXP-MONO-805a02's own Stage 3 does for
`E.add`) plus one final F_p multiplication. Measured
`add_calls_measured == n_completed * 2**(m-2) * (m-1)` EXACTLY at every
cell in both runs (`reconciles_exactly: 0` everywhere) -- e.g.
`m4_p211`: 500 tuples * 4 sign classes * 3 adds = 6000 measured, 6000
expected. The twisted-factor-base BUILD cost (the ascending-x scan) is
timed and reported separately (`twisted_factor_base_build`,
sub-millisecond at both p in both runs), never charged against per-attempt
cost, per H-MONO-40aca5's own H2 convention.

## Stage 4a (wrong-rescaling-constant mutant control)

m=4, p=211, j=3, n=50 trials, tuples drawn under label `"mutant-tuple"`
(distinct SHA-256 draw stream from Stage 3's `"twisted-fb-tuple"` stream by
construction). `delta'` is drawn ONCE for the whole stage under label
`"mutant-delta-prime"`, from the same twisted-factor-base non-residue
values, excluding `DELTA_SOURCE` itself (i.e. any non-residue x distinct
from the one that produced `delta`).

**Disclosed interpretation choice.** The contract's mechanism text does not
unambiguously state whether `delta'` is drawn once for the whole stage or
redrawn per trial ("a deliberately wrong final rescaling constant" reads
naturally as singular; "a generically different value at every trial" in
the predicted-effect text is read here as describing the derived quantity
`X(R)*inverse(delta')`, which varies per trial simply because `X(R)` does,
not as requiring `delta'` itself to be redrawn). This run draws `delta'`
ONCE (measured: `delta=57`, `delta'=102` from non-residue source x=106 in
run 1; `delta'=206` from source x=199 in run 2), the simpler and equally
valid reading. If a future reviewer judges per-trial redraw was intended,
this is the exact point of divergence to amend.

For each of the 50 trials: direct-route root set (identical procedure to
Stage 3's direct route, `s4_expr`); mutant twist-route x-set (identical
twist-sum construction using the CORRECT `delta` throughout the sum, but
rescaled by `inverse(delta')` instead of `inverse(delta)` at the final
step). Neither excluded mutant (a sign flip on `y_i'`; rebuilding both the
twist and the rescaling with the same `delta'`) is implemented anywhere in
this code.

**Result, both official runs: mutant agreement rate = 0.000 (0/50 in each
run). `control_holds_discriminating_power: true` in both runs.** Stage 3's
exact-match test is not vacuous by this control's own measure.

## Independent-sample check (Stage 4a vs. Stage 3)

`independent_sample_check()` recomputes BOTH Stage 3's own 500-tuple
`m4_p211` sample and Stage 4a's 50-tuple sample from their respective
SeedStreams and checks set overlap directly (not merely asserted from
"different label implies independent" -- verified empirically). Measured:
`overlap_count: 0` in both runs.

## Budget and timing

Both official runs completed well under the 1800s wall-clock cap: run 1
(seed 20260905) 454.25s measured (`total_wall_seconds` from
`time.perf_counter()`, the authoritative figure); run 2 (seed 20260906)
445.79s. No cell hit the 300s per-cell s5 timeout at any point (measured
per-m5-tuple cost was on the order of 0.2-0.3s; see the smoke/timing checks
in this session's own working notes, not committed as a separate artifact).
Memory was not separately instrumented (pure Python + sympy, no large
in-memory structures beyond small-degree polynomials and factor-base lists
of size < 1009); informal monitoring during the run did not approach the
2GB cap.

**A `/usr/bin/time -l` wrapper was used for RUN-MONO-7c653b-1's launch only
and failed a subsidiary `sysctl` call under this session's sandbox** ("sysctl
kern.clockrate: Operation not permitted"), captured verbatim into that run's
`stderr.log`. This is the wrapper's own benign sandbox artifact, not an
error or warning from `run_experiment.py` itself, which produced no stderr
output in either run and exited 0 in both. The wrapper DID still print
`453.76 user` / `0.59 sys` seconds before failing, which is recorded as
`resources.cpu_seconds` in RUN-1's manifest; RUN-2 was launched without the
wrapper (no useful measurement gained from repeating a failing wrapper), so
its `cpu_seconds` is `null`, disclosed as such rather than fabricated.

## Certificate discipline

`certificate.kind: none` in both runs' manifests. No discrete-log solve or
factor-base relation is claimed anywhere in this record; it is a pure
exact-computation representation-reduction / cost-identity check (set
equality between two independently-computed x-coordinate sets, verified
directly in-line by the harness itself using the SAME direct-route
poly-factoring code for both Stage 3 and Stage 4a's comparison, and an
independent group-law construction for the twist route) plus a
proves-too-much control. Per `docs/claims-and-verification.md`, this
requires no separate certificate-verification step.

## Files

- `implementation/run_experiment.py` -- the only source file.
- `runs/RUN-MONO-7c653b-{1,2}/` -- the two required replication runs (seeds
  20260905, 20260906), each containing `manifest.yaml` (nested schema),
  `command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
  `raw-result.json`.

## Protocol deviations, summarized

1. `s5_expr` is defined LOCALLY (not added to `harness/semaev.py`), for the
   disclosed reason above (this task's own write-scope and no-git
   constraints, not stylistic preference).
2. The `domain` string is resolved as `f"EXP-MONO-7c653b/v1/run-{seed}"`
   (master_seed folded in as a per-run suffix), following
   EXP-MONO-805a02's own precedent for the identical formula/reproduction
   tension; verified empirically to produce independent draw streams
   across the two replication runs.
3. Stage 4a's `delta'` is drawn ONCE per stage rather than per trial (a
   disclosed reading of ambiguous mechanism text, not a silent choice).
4. `RUN-MONO-7c653b-1`'s `/usr/bin/time` wrapper failed a `sysctl` call
   under this session's sandbox; its stderr artifact is preserved verbatim
   and disclosed as benign, not a run-time error.

None of these deviations affect any preregistered value, tolerance, or
decision rule; no protocol amendment was required.
