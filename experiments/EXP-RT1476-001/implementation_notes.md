# EXP-RT1476-001 — implementation notes

Task: TASK-20260728-001 (Executor). Experiment: `EXP-RT1476-001` version 1,
status `approved`, `approved_by: coordinator`, `approved_by_decision:
DEC-20260728-002`. Hypothesis: `H-RT1476-001`. Batch `BATCH-010`, goal
`GOAL-ECDLP-001`.

This file records **what was actually implemented** and **every place the
implementation had to choose something the frozen specification did not fix**.
It contains no interpretation of the numbers. The numbers are in
`runs/*/raw-result.json` and `results_summary.json`; the threshold comparisons
are in `analysis.md`.

The measurement module is `experiments/EXP-RT1476-001/subresultant_meter.py`.
`experiments/EXP-RT1476-001/specification.yaml` was not modified.

---

## 0. Anti-tautology compliance

The binding rule (`specification.yaml`
`metrics.metric_isolation_rule_anti_tautology`; handoff constraint 2) is that no
threshold, expected value, verdict or answer key may be visible to the measuring
code path.

What was done:

- `subresultant_meter.py` contains none of the pre-registered constants `0.3`,
  `0.6`, `0.2`, `1.5` (verified by grep on the final file; the only near-miss,
  an `n ** 0.2` inside the factor-base sizing helper, was rewritten to exact
  integer arithmetic with the arity `m = 5` named explicitly, so no float
  exponent literal remains).
- The module emits **no** pass/fail value, no verdict string, and no comparison
  of a measured quantity against any constant. `summarize()` computes slopes
  only. Slopes are measurements; the comparison of a slope against a threshold
  happens in `analysis.md` and again, independently, in TASK-20260728-003.
- Every quantity that any gate in the specification is evaluated on is written
  into `raw-result.json` under `gate_values` (and per target under
  `measured_targets`). Nothing a gate depends on exists only in stdout.
- Nothing in the module branches on the arm in a way that changes the
  measurement algorithm, except where a branch is forced by the absence of a
  group law on `negctl` (section 6); those branches are declared there.

The anti-pattern this rule exists to prevent (`experiments/EXP-GGM-001/
simulability_test.py`, a dict of `expected_verdict` strings keyed on its own
input names, compared against itself) has no analogue here: there is no table of
expected outcomes anywhere in the module.

---

## 1. Environment and the Sage substitution (DEV-1)

Sage is unavailable. Per DEV-1 the port is Python 3 over GF(p).

```
Python      3.13.1 (CPython), macOS-26.6-arm64 (Darwin 25.6.0), arm64
sympy       1.14.0
numpy       2.4.0      (present; NOT used in the measurement path)
pyyaml      6.0.3      (not used by the module)
in-repo     harness/toycurve.py, harness/semaev.py
```

**sympy is used in exactly three places, all outside the counted measurement
path**, and this is load-bearing for INVALID-7:

1. `sympy.isprime` — the run-time primality check on `p` and on the candidate
   group order `n`;
2. `sympy.resultant` — in `--selftest` only, as the *independent* reference the
   hand-written resultant is checked against;
3. `sympy.Poly` — in `--selftest` only, for the same purpose.

No sympy call occurs inside `membership_query`, inside the resultant/PRS layer,
or inside any operation whose cost is counted. Every GF(p) operation on the
counted path goes through the hand-written layer in section 2. `ops_success` is
therefore a counted integer, not a proxy, and INVALID-7 does **not** fire.

Wall-clock is recorded but is used only to drive the stopping rules and as a
diagnostic. It is never used to fit `beta_ops` and supports no cost claim
(DEV-1, `metrics_that_DO_NOT_SURVIVE_the_substitution`).

---

## 2. The instrumented GF(p) arithmetic layer

`class FieldOps` holds `p` and three integer counters: `mul`, `add`, `inv`.

- Polynomials over GF(p) are little-endian Python lists of ints, normalised so
  the zero polynomial is `[]` and no trailing zero coefficient survives.
- `padd`, `psub`, `pneg`, `pmul`, `pscal`, `pdivmod`, `pexactdiv`, `peval`,
  `ppow`, `pmonic`, `pgcd`, `ppowmod` are hand-written on top of Python ints
  with explicit `% p`.

**Counting convention (declared).** Counters are incremented by the exact number
of coefficient operations the interpreter executed on that call, accumulated in
a local and added once at the end of each tight loop. This is exact, not an
estimate: for example `pmul` counts one `mul` and one `add` for each
`(i, j)` inner-loop iteration that was actually executed, and iterations skipped
because a coefficient is zero are not counted. Specifically:

| operation | counted as |
|---|---|
| `a*b % p` inside a convolution | 1 mul + 1 add (the accumulate) |
| coefficientwise `+`/`-` | 1 add each |
| `pow(x, -1, p)` | 1 inv |
| Horner step in `peval` | 1 mul + 1 add |
| scalar multiple of a polynomial | 1 mul per coefficient |

**Weighting (declared).** The combined figure reported as
`total_unit_weighted` gives every counted operation weight 1. This is the
weighting `beta_ops` is fitted on. The three counters are also always reported
separately (`ops_success_mul`, `ops_success_add`, `ops_success_inv`) precisely
so that a reviewer can apply any other weighting — e.g. charging an inversion
`ceil(log2 p)` multiplications — directly from the raw record without rerunning
anything. Inversions are a negligible fraction of the total on this path (they
occur only in polynomial division and in the interpolation fallback), so the
exponent is insensitive to the weighting; the raw counters let that be checked
rather than asserted.

**Elliptic-curve group operations are NOT counted in `ops_success`.** They are a
different unit. `harness.toycurve.EllipticCurve` is used unmodified for the
group law (certificates, factor bases, the group-law backward state, the
meet-in-the-middle screen). None of that is on the counted membership-query
path. This is declared rather than hidden: `ops_success` measures the field
operations of the *algebraic* membership query, which is the object the
hypothesis's cost claim is about.

---

## 3. Resultants: which algorithm, and why

The frozen contract names *subresultant PRS* as the device. What was
implemented:

- `resultant(F, A, B)` computes `Res_x(A, B)` where `A, B` are polynomials in
  the eliminated variable `x` whose coefficients lie in `GF(p)[t]`, by **one-step
  fraction-free (Bareiss) Gaussian elimination on the Sylvester matrix**.
  Fraction-free elimination on the Sylvester matrix is the matrix form of the
  subresultant algorithm: its intermediate entries are the subresultants and
  every division it performs is exact in `GF(p)[t]`. Row swaps are used when a
  pivot vanishes.
- Degenerate degrees are handled before building the Sylvester matrix:
  `Res(A, B) = A^deg B` when `deg_x A = 0`, symmetrically for `B`, and `0` when
  either is the zero polynomial. Actual (post-normalisation) degrees are always
  used, never declared ones.
- **Fallback.** If an exact division ever fails (which would mean the pivoting
  broke the fraction-free property), the call falls back to
  `det_eval_interp`, an independent evaluation-and-interpolation determinant
  over `GF(p)[t]`, still fully instrumented. The number of fallbacks is counted
  and written to `raw-result.json` as `bareiss_fallbacks` per query. **In every
  production run this counter is 0**; the fallback never fired.
- `prs_remainder_degrees` implements the *polynomial-remainder-sequence* form
  separately, by pseudo-division over `GF(p)[t]`. It is used only to record the
  secondary metric `prs_step_count`, on a declared sample of factors per query
  (`--prs-sample 4`, i.e. the first four eliminations of each query). The PRS
  variant is recorded as **pseudo-remainder sequence over the polynomial
  coefficient domain**, and the observed remainder degree sequences are written
  verbatim into `raw-result.json` (`prs_degree_sequences_sampled`), so the step
  count is reproducible relative to the declared variant as
  `metrics.secondary.prs_step_count` requires.

**Correctness evidence, not assertion.** `--selftest` (run before the production
set and reproducible by `python3 experiments/EXP-RT1476-001/subresultant_meter.py
--selftest`) checks three things against code independent of the solver:

| self-test | result |
|---|---|
| the hard-coded `S_3` monomial table reproduces `harness.semaev.s3_eval` at 40 random points | `true` |
| `resultant()` equals `sympy.resultant` on 25 random bivariate input pairs | 25/25 |
| `Res_{x5}(S3(w2,x5,x_R), f_V(x5)) == prod_{v in V} S3(w2, v, x_R)` (the factor-base elimination identity of section 4), computed with sympy | holds, constant `1` |

---

## 4. The algebraic chain that was actually eliminated

Backward leg as frozen:
`S3(u,x3,w1)=0`, `S3(w1,x4,w2)=0`, `S3(w2,x5,x_R)=0`, with `x3,x4,x5 in V`, and
the factor-base constraints `f_V(x_i) = prod_{v in V}(x_i - v)`.

**Choice the specification did not fix: the elimination order and the treatment
of the factor-base constraints.** Implemented as:

1. The factor-base variables `x3, x4, x5` are eliminated by the *evaluation-product
   form* of the resultant. `f_V` is monic and splits over `GF(p)` by construction
   (its roots are the elements of `V`), so
   `Res_{x}(A, f_V) = prod_{v in V} A(x = v)` exactly, up to the sign
   `(-1)^{deg A · deg f_V}`. This factorises the backward eliminant as

   ```
   B_R(u) = prod over (v3,v4,v5) in V^3  of  G_{v3,v4,v5}(u)
   ```

2. Inside each factor, the two chain variables are eliminated by the
   subresultant/fraction-free routine of section 3:

   ```
   Q_{v4,v5}(w1) = Res_{w2}( S3(w1, v4, w2),  S3(w2, v5, x_R) )      4x4 Sylvester over GF(p)[w1]
   G_{v3,v4,v5}(u) = Res_{w1}( S3(u, v3, w1), Q_{v4,v5}(w1) )        6x6 Sylvester over GF(p)[u]
   ```

   so `deg_{w1} Q <= 4` and `deg_u G <= 8` — the eight sign patterns
   `(e3,e4,e5) in {+-1}^3`.

3. `deg_u B_R = sum over triples of deg_u G`, computed exactly. `B_R` is never
   materialised.

**Why not the literal iterated-resultant chain.** Eliminating `x5`, then `w2`,
then `x4`, then `w1`, then `x3` as full multivariate resultants produces
intermediate bivariate objects of size `8L^3 x 2L` — about 9.8 million
coefficients at `L = 28`. That is not affordable inside this budget, and the
per-triple factorisation is *the same polynomial* up to a nonzero constant, by
the identity verified in the self-test above. This is an implementation choice,
it is declared, and it is exact.

**Common-subexpression elimination (declared).** `Q_{v4,v5}` does not depend on
`v3`, so it is computed `L^2` times, not `L^3`, and cached per query. The
operation counters reflect the computation actually performed, i.e. with the
cache. A reviewer recomputing `ops_success` without the cache would get a larger
number; the cached form is the algorithm that was measured.

---

## 5. The membership query (the counted path)

Per target `x_R`, for every triple `(v3,v4,v5)` in `V^3` in a fixed
deterministic order:

1. build `Q_{v4,v5}` (from cache if present) and `G_{v3,v4,v5}` as above;
2. accumulate `deg_u G` into the eliminant degree;
3. test the meet by **evaluating `G` at every element of the forward state
   `F`**, which is the mechanism's own prescription ("evaluating a low-degree
   univariate object at each forward value").

Every GF(p) operation of steps 1–3 is counted. Recorded per query: `mul`,
`add`, `inv`, `total_unit_weighted`, `deg_u_backward_eliminant`,
`triples_processed`, `zero_factors`, number of `hits`, a sample of hits,
`distinct_hit_u`, `prs_step_count_sampled`, `bareiss_fallbacks`, `seconds`,
`timed_out`.

**Choices the specification did not fix:**

- **The forward state is built once per cell and is not charged to the query.**
  It is the amortised part of index calculus. Its size and its construction time
  are reported separately (`forward_state`).
- **No early abort inside the query.** The full `V^3` scan runs even after a hit.
  This is the deterministic choice: an aborting variant's cost would depend on
  where in the enumeration order the first hit happens to sit, which is not a
  property of the mathematics. The consequence is that the reported
  `ops_success` is an *upper* figure for an aborting implementation on the
  success subset. It does not affect the ops of the failure subset (a failing
  query scans everything either way), so `ops_all` and the success/failure
  contrast are unaffected.
- **`ops_success` vs `ops_all`.** `ops_success` is the mean over measured
  targets that carry a verified relation certificate. `ops_all` is the mean over
  all measured targets (successes and matched failures alike). They are never
  pooled, and `beta_ops` is fitted on `ops_success` only, as the red-team
  amendment requires. Both are in every raw record.

---

## 6. Backward and forward states: two independent computations

`backward_state_support_size` is the specification's primary metric and is
required to be exact and CAS-free. Two computations are implemented:

- **Group law (`backward_state_group_law`)** — used on `main` and `posctl`.
  Propagates `x_R -> W2 -> W1 -> u` in the *same order as the S3 chain*, adding
  each of the `2L` signed factor-base points at each level and deduplicating on
  **x-coordinates** at every level. Deduplicating on `x` is exact: an
  x-coordinate determines the point up to sign, and the sign of an intermediate
  point is absorbed by the free sign on the next factor-base point. Paths whose
  intermediate sum is the point at infinity terminate, exactly as they do in the
  `S3` chain (the corresponding `S3` has no root there).
- **Algebraic chain propagation (`backward_state_chain`)** — the same three
  levels, but computed by solving the quadratic `link(·, v, z) = 0` for its
  roots in `GF(p)` at every step. Uses no group law and therefore works on
  `negctl` too. Square roots use `pow(a,(p+1)/4,p)` for `p = 3 mod 4` and a
  hand-written Tonelli–Shanks otherwise.

On `main` and `posctl` **both** are run on a declared sample of targets
(`--support-cross-check 2`, the first two measured targets of each cell) and the
two must produce identical sets at all three levels; the boolean
`backward_support_cross_check_agrees` is written per target.

`forward_state_size` is likewise computed by the group law on `main`/`posctl`
and cross-checked against the roots of `S3(x1,x2,u)` over `V x V` on every cell
(`forward_state.cross_check.agrees`).

**Declared arm difference.** On `negctl` there is no group law, so the backward
state is measured by chain propagation only and `backward_state_support_group_law`
is `null` with that reason. This is forced by the control's construction and is
already flagged in the specification
(`controls.CTRL-NEG.comparability_limit_declared`).

---

## 7. Curve construction

`harness.toycurve.generate_instance` is **not** used (spec
`implementation_constraint_recorded_because_it_is_a_real_trap`; handoff
constraint). Instead:

- `p` is verified prime at run time with `sympy.isprime` and the check is
  recorded in `raw-result.json.primality_check`. All three moduli passed
  (`1009`, `65521`, `16769023`). No modulus was substituted.
- `(a, b)` are drawn from the SHA-256 seed stream `det_int(seed, "a{t}")`,
  `det_int(seed, "b{t}")`, `t = 1, 2, ...`, and the **full** predicate is
  rejection-tested: non-singular (`4a^3 + 27b^2 != 0`), `j(E) not in {0, 1728}`
  (computed as `j = 1728 * 4a^3 / (4a^3 + 27b^2)` and compared to `0` and
  `1728 mod p`), `#E` prime, non-anomalous (`n != p`), and trace `!= 0`
  (`n != p+1`, which also excludes supersingularity). The per-cell rejection
  count and its breakdown by cause are recorded
  (`curve.rejected_candidates`, `curve.rejection_breakdown`). A rejection is a
  property of the sampler and is not evidence.
- The group order uses **BSGS on the Hasse interval**, not the naive `O(p)`
  count: find `t` with `(p+1-t)Q = O` by baby-step/giant-step, then accept
  `n = p+1-t` only if `n` is prime, lies in the Hasse interval and annihilates
  `Q != O`. That conjunction is a proof that `#E = n`: `ord(Q) = n` divides
  `#E`, both `n` and `#E` lie in the Hasse interval, and the interval is shorter
  than `n`, so `#E / n < 2` and `#E = n`. The curve is therefore certified
  prime-order, not assumed to be.
- **Cross-check of the order routine.** At `p = 1009` and `p = 65521` the BSGS
  order is additionally checked against a naive Legendre-symbol point count and
  the agreement is recorded (`curve.order_cross_check`). At `p = 16769023` the
  naive count is not affordable and the field is `null` with that reason.
- The same `(p, seed)` gives the same curve in all three arms of a cell, because
  the sampler is a pure function of `(p, seed)`. Each run recomputes it
  independently; nothing is cached across runs.

`L = round(q^(1/5))` is computed from the **measured** `q = n` by exact integer
comparison. Measured values: `L = 4, 9, 28` at `q = 1013 / 65407 / 16773769`
(seed 20260728; the other seeds give the same `L` at each size — see
`results_summary.json`).

---

## 8. Factor bases and links, per arm

| arm | factor base | chain links | differs from `main` in |
|---|---|---|---|
| `main` | `harness.semaev.build_factor_base` — `L` distinct deterministic on-curve x-coordinates | Semaev `S_3` | — |
| `posctl` | **planted**: `{x([i]P) : i = 1..L}` | Semaev `S_3` | the factor base only |
| `negctl` | same construction as `main` | four independent **random dense trivariates** (one forward link, three backward links) | the chain links only |

Everything else — `p`, the sampled curve, `n`, `L`, the seed stream, the target
count, the resultant routine, the operation counter, the stopping rules, the
session and the machine — is identical across the three arms of a cell, as
`control_comparability_requirements` demands.

**Choice the specification did not fix: the exact monomial support of the random
dense link.** The spec says "the same total degree and the same per-variable
degrees as `S3` (degree 2 in each of its three variables)". `S_3` has
per-variable degree 2 and total degree 4; a fully dense per-variable-degree-2
polynomial has total degree 6. The reading implemented is the maximal set
satisfying **both** stated constraints: all monomials `X^i Y^j Z^k` with
`i,j,k <= 2` **and** `i+j+k <= 4`, each with an independent uniform GF(p)
coefficient from the seed stream. The realised coefficients of all four links
are written verbatim into `raw-result.json` under `links.monomials`, so the
control is exactly reconstructible.

---

## 9. Sampling design, and the one place the frozen design had to be capped

Stage A (screening), per cell, 1200 targets, exactly as frozen:

- `main` / `posctl`: `R = [r]P` with `r` uniform in `[1, q-1]` from the
  deterministic seed stream. Meet-in-the-middle over the signed 2-sum and 3-sum
  tables of `V`; every hit is materialised as an explicit signed 5-tuple.
  **Planted targets are not used anywhere**, and no planted-target diagnostic
  was run at all.
- `negctl`: there is no group law and no point `R`, so the target is a uniform
  `x_R` in `GF(p)` from the same seed stream, and the success predicate is
  root-existence in the forward state, computed as an algebraic meet: the
  backward chain from `x_R` is propagated two levels to `W1(x_R)`, and the
  forward state is propagated one level forward through `link1` to a set
  `W1_fwd`; the two meet iff `u`-level meet exists. This equivalence is exact
  (both sides say: there exist `u in F`, `v3`, `w1` with `link1(u,v3,w1)=0` and
  `w1 in W1(x_R)`), and stopping at `W1` avoids expanding the `u` level for
  every one of 1200 targets.

Stage B (measurement): **capped**.

The frozen text says "ALL certified successes from stage A (expected order 10)".
The realised number of certified successes per cell is in the hundreds, not
about ten — the frozen expectation `L^5/(5! q)` omits the factor `2^5` of free
signs (see `analysis.md`, where this is reported as an observation). Measuring
an eliminant for every certified success is not affordable inside the 1800 s
cell budget at `L = 28`, where one query costs about 14 s.

Declared cap: **10 certified successes and 10 matched failures per cell**, taken
in ascending target index, uniform across all 27 runs. The cap was fixed from a
timing pilot before the production set was launched, on measured seconds per
query only; it is recorded in every `raw-result.json`
(`inputs.max_measured_successes`, `inputs.max_measured_failures`) and in every
manifest. It does not interact with INVALID-1, which counts *certified successes
in the cell* (hundreds), not measured ones. It is a budget stop under STOP-2 and
is reported as one. `beta_ops` is a mean over the measured success subset; the
cap raises the noise on that mean, it does not bias it.

---

## 10. Certificates

Every claimed relation on `main` and `posctl` is written to
`runs/<RUN-ID>/certificates.json` as `{target R, five signed summand points,
curve (p,a,b)}` and is re-verified **twice**, by two implementations that do not
share code with the meet-in-the-middle search that produced it:

1. `harness.semaev.verify_decomposition_certificate` (in-repo, pre-existing,
   generic over the number of summands: it checks each summand is on `E` and
   accumulates them with the harness group law);
2. `subresultant_meter.independent_recheck`, a separate reimplementation of
   curve membership and the group law written directly in modular arithmetic
   inside this module, which does not call `harness.toycurve` at all.

A certificate counts as verified only if **both** accept. The per-certificate
booleans and the per-run count of failures are recorded. A hit found by the
counted algebraic query is a **candidate**, never a relation: the certified
success set is the group-law meet-in-the-middle set, and `ops_success` is
restricted to targets in that set.

`negctl` has `certificate.kind: none`, stated explicitly, with the reason: a
random dense system has no group law, so no relation exists to certify.

---

## 11. Determinism and reproducibility

- All randomness is the SHA-256 stream `sha256(f"{seed}:{tag}:{ctr}")`. Sources:
  curve coefficients `(a,b)`, factor-base x-coordinates, target scalars `r` /
  target `x_R`, and the negative control's link coefficients. There is no
  unseeded randomness anywhere in the measurement path; the equal-degree
  splitting used in root finding uses the deterministic shift sequence
  `c = 0, 1, 2, ...` rather than random shifts.
- No floating point is used anywhere in the measurement path. `math.log` appears
  only when deriving `log q` and the slopes in the summariser.
- Each of the 27 runs is a separate `python3` subprocess with its own real
  stdout/stderr captured to `stdout.log` / `stderr.log`. Nothing is computed
  once and serialised many times: the curve, the factor base, the states, the
  screening and every query are recomputed inside each subprocess from its own
  `(arm, p, seed)`.
- Reproduction of a single run: the exact command is in
  `runs/<RUN-ID>/command.txt` and in `manifest.yaml` under `code.command`.
- Reproduction of the whole set: the specification's `reproduction_command`,
  with the two Stage-B caps of section 9 supplied explicitly.

---

## 12. Deviations from the frozen protocol, collected

| # | what | why | where recorded |
|---|---|---|---|
| D1 | Sage → Python/sympy over GF(p) | Sage unavailable | already frozen as DEV-1 |
| D2 | factor-base variables eliminated by the monic evaluation-product identity rather than by a Sylvester resultant against `f_V` | the literal chain produces ~10^7-coefficient intermediates; the identity is exact and was verified against sympy | §4, self-test 3 |
| D3 | subresultant computation in fraction-free (Bareiss) matrix form; PRS form used only for `prs_step_count` | correctness is checkable against `sympy.resultant`; the two forms compute the same subresultant sequence | §3 |
| D4 | Stage B capped at 10 successes + 10 failures per cell instead of all certified successes | ~14 s per query at `L = 28`; the realised success count is hundreds, not the frozen expectation of ~10 | §9, STOP-2 |
| D5 | `negctl` screening uses a two-level algebraic meet rather than the three-level chain | exactly equivalent, and affordable at 1200 targets | §9 |
| D6 | EC group operations are not counted in `ops_success` | different unit; the counted path is the algebraic query | §2 |
| D7 | forward-state construction excluded from the per-query count | amortised once per cell, reported separately | §5 |

None of these changes a metric definition, a control, a criterion, a budget or
an interpretation limit. `specification.yaml` was not edited.

---

## 13. What this file does not do

It assigns no evidence strength, states no verdict, changes no record status,
and draws no conclusion about `H-RT1476-001`, about RT-1476-SUBRES-A1, or about
ECDLP. Those are not the Executor's to make.
