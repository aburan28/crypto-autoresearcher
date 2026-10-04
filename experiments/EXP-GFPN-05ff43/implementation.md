# EXP-GFPN-05ff43 — implementation note

Executor task **TASK-20260920-dd8205** (resumed under the dispatching session's
**TASK-20260921-98561a** archive). Frozen contract:
`experiments/EXP-GFPN-05ff43/specification.yaml` (approved `coordinator`,
`DEC-20260920-fe73de`). Hypothesis `H-GFPN-9a29be`; heuristic under test
`HEUR-GFPN-DFLAT`. **The specification and its `preregistered_prediction` were
not edited.** No amendment was requested or applied.

This note records what was implemented, what deviates from the protocol, and every
infrastructure event. Observations live in the run packages and in the execution
report; nothing here concludes that the heuristic is supported or refuted.

## 1. What the code computes

### 1.1 Field and curves

`implementation/gfpn5_core.py`. `F_q = F_p[z]/(z^5 - c)` via python-flint
`fq_default` (`fmpz_mod_poly` modulus, `var="z"`); `c` is the smallest positive
integer that is not a fifth power mod `p'`, which makes `z^5 - c` irreducible
because every ladder prime satisfies `p' = 1 (mod 5)`. Curves are general
Weierstrass cubics `y^2 = x^3 + a2 x^2 + a4 x + a6` over `F_q` with affine group
law; the EcGFp5-shaped curves are the double-odd model
`y^2 = x(x^2 + 2x + c z)` of `inputs/PORNIN-2022-274-ECGFP5/` (§ "We define, over
GF(p^5), an elliptic curve of equation y^2 = x(x^2 + 2x + 263z)"), so `a6 = 0`
and `T = (0,0)` is the rational 2-torsion point, with `x(P + T) = b/x(P)` for
`b = a4`.

### 1.2 Summation polynomials — two independent evaluators

Semaev/summation polynomials are never manipulated symbolically in many
variables; they are **evaluated numerically** two ways and cross-checked:

* **(A) product formula.** `S_{n}(x_1..x_{n-1}, X)` as a polynomial in `X` is
  `S_{n-1}(x_1..x_{n-1})^2 * prod_{eps in {+-}^{n-2}} (X - x(P_1 + eps_2 P_2 + ...))`,
  computed from actual curve points.
* **(B) resultant recursion.** `S_n = Res_Y(S_3(x_1,x_2,Y), S_{n-1}(x_3..,Y))`
  with `S_3` from an explicit closed form for the general cubic, and `S_2 = x_1 - x_2`.
  Point-free.

`gfpn5_core.self_test()` checks `S_4`, `S_5`, `S_6` agree coefficient-for-coefficient
between (A) and (B), that `S_3` reproduces the textbook Semaev `S_3` on `a2 = 0`
curves, that `S_n` vanishes at a genuine sum, and that it is symmetric. This test
runs as the first check of every validation run.

Two bugs were found and fixed by this cross-check, both before any measurement:

* the resultant must use the **formal** degree of the second argument
  (`lc(A)^{deg B}`); using the actual degree made `S_5` disagree with (A) at the
  five interpolation nodes where the degree drops;
* the recursion needs `x_1 != x_2`; the degenerate case is handled by permuting a
  distinct coordinate into slot 2 (the polynomial is symmetric) or, when all
  coordinates coincide, by interpolating in the last slot.

### 1.3 Arms

Let `m` be the number of factor-base points and `K = 2^{m-1}`.

* **(i) `raw`** — `S_{m+1}(x_1..x_m, x_R)` in the `x_i` themselves, obtained by
  tensor-product (grid) interpolation on a `(K+1)^m` grid of `F_p` nodes drawn
  from the factor-base pool, then Weil-descended. This is the system the EcGFp5
  design note costs.
* **(ii) `S5`/`S4`** — the same polynomial written in `e_1..e_m`, the elementary
  symmetric polynomials of `x_1..x_m` (`|S_m| = m!`).
* **(iii) `torsion_S5`/`torsion_S4`** — the FHJRV construction
  (`research/equation-schemes-20260905/retrieved-pages/hal-00935050.txt`,
  Prop. 8 and §4.1: with a rational 2-torsion point and `b` the constant of
  `y^2 = x(x^2 + a x + b)`, `x(P + T) = b/x(P)`, and the degree-2 map is
  equivariant). The relation-defining function used here is
  `Q(t_1..t_m; t_R) = S_{m+1}(x; X) * S_{m+1}(x^{(1)}; X)` where
  `x^{(1)} = (b/x_1, x_2, ..., x_m)`, normalised by `(prod x_i * prod x^{(1)}_i)^{K/2} X^K`
  into a Laurent polynomial in `X` invariant under `X -> b/X`, hence a polynomial of
  degree `K` in `t_R = X + b/X`, and symmetric in the `t_i = x_i + b/x_i`, hence a
  polynomial in `e(t_1..t_m)`. The factor base for this arm is the FHJRV
  `phi`-factor base `{P : x(P) + b/x(P) in F_p}` (`|G| = 2^{m-1} m!`).
* **`identity`** — degenerate-symmetrisation control: the *same interpolation
  machinery* with the trivial group (full monomial box in the `x_i`). It must
  reproduce arm (i) exactly.

Each arm's polynomial is obtained by **exact interpolation**: evaluate the
numeric summation polynomial at `N + 96` random sample points, solve the dense
`N x N` system over `F_p` (python-flint `nmod_mat`, `N = C(m + K, m)`, e.g.
`N = 20349` at `m = 5`), then verify the result on the held-out rows
(`held_out_mismatches` is recorded in every manifest and is `0` for every accepted
polynomial). The polynomial is built **once per (prime, curve, arm)** with the
target coordinate symbolic, and specialised per target; both the construction and
the specialisation are charged (C-5).

### 1.4 Descent, solver, degree

The single equation over `F_q` is Weil-descended into **5 equations over `F_p`**
by splitting each `F_q` coefficient into its `z`-components, and written in
msolve's input format. msolve 0.6.5 (`-v 2 -t T -P 1`) computes a DRL Gröbner
basis (F4) and a rational parametrization (FGLM). `D` is msolve's own
`Dimension of quotient`. The `F_p` operation figures are **proxies derived from
msolve's printed per-round matrix shapes** — measured shapes, modeled op counts —
and are reported as such:

* `ops_proxy_rows_cols_density = sum over rounds of rows*cols*density` (lower
  bound: every stored nonzero touched once);
* `ops_proxy_reduction_total = sum over rounds of (new+zero)*(rows-new-zero)*cols*density`
  (dense Gaussian-elimination estimate), which is the figure used for
  `fp_operations_per_pdp`;
* FGLM: `2*D*nnz(multiplication matrix)` from msolve's printed dimension,
  non-trivial column count and density;
* plus the **counted** `F_q` operations of specialisation and orbit lifting,
  converted at `1 F_q mul = 29 F_p mul` and `1 F_q inv = 150 F_q mul`.

msolve's rational-parametrization convention was determined **empirically**, not
assumed: on a planted `m = 3` raw system whose three `x` values are known, the
only convention reproducing them is `x_i = -v_i(r) / (c_i * den(r))` over the
roots `r` of the eliminating polynomial, with the last original variable equal to
`r` when msolve added no linear form. This is asserted in the validation run.

### 1.5 Lifting, certificates, independent verification

A rational solution is lifted by forming `T^m - e_1 T^{m-1} + ...`, taking its
roots in `F_p` (arm ii: the `x_i`; arm iii: the `t_i`, then `x` from
`X^2 - t X + b`), lifting each `x` to a curve point, and searching the `2^m` sign
vectors for `sum eps_i P_i = R` (arm iii also accepts `= R + T`, corrected by
`P_1 -> P_1 + T`). Every accepted relation is written as a JSON **decomposition
certificate** and re-verified by `implementation/verify_independent.py`, which
shares **no code** with the solver path: pure-Python integer arithmetic for
`F_p[z]/(z^5-c)` and the group law, no flint, no PARI, no msolve. It checks that
`R = [k]G` (known scalar), `[n]G = O`, that every listed point is on the curve
**and satisfies that arm's factor-base condition**, and that the signed sum is
`R`. Success is counted in **lifted, verified points**, never in solutions.

## 2. Ladder selection

`implementation/ladder_select.py`, output frozen into
`implementation/ladder.json`. Primes are the smallest `p' >= 2^k` with
`p' = 1 (mod 5)`, primality **proved** by PARI `isprime` and independently
re-checked by trial division (all `p' < 2^31`). Curves are searched
deterministically from seed `2026092002`; orders come from PARI `ellcard` over
`F_{p'^5}` and are factored with PARI `factor`, so each cofactor is recorded, not
assumed.

## 3. Deviations from the approved protocol

Recorded here, and again in the execution report. None of them changes the
hypothesis, the success criteria, the prediction, or the metric definitions.

* **D-1 (memory ceiling).** The contract's `maximum_memory_gb` is 32; this machine
  has 15 GB with no swap. Every solver child and every construction process runs
  under a 12 GB address-space cap (`prlimit --as=12000000000`, plus `ulimit -v`
  inside `run_msolve`), one at a time. This is machine protection, and it is the
  reason some cells may end `not_measured / resource_exhaustion` rather than with
  a degree.
* **D-2 (`F_p` operation counts are proxies).** The contract asks for instrumented
  `F_{p'}` operation counts. msolve is an external binary and does not report a
  field-operation counter, so the F4/FGLM figures are computed from msolve's own
  printed matrix shapes as described in §1.4 and are labelled `*_proxy`
  everywhere. Only the construction and lifting operations are directly counted.
* **D-3 (17-bit rung is anchor-only).** msolve 0.6.5 on this host **segfaults in
  its rational-parametrization step for prime characteristics between about 2^16
  and 2^18** (reproduced on a two-variable toy system at `p = 65537`, `65539`,
  `65551`; the same system is fine at `4099`, `262147`, `1048583`, `16777259`,
  `1073741827`, and `-g 1` leading-ideal output succeeds at `65551`). This is an
  infrastructure property of the solver, not a mathematical observation. The
  17-bit rung is therefore used only where a parametrization is not required.
* **D-4 (m = 5 not attempted at every ladder prime).** The m = 5 systems are the
  same size at every prime — the monomial count `C(m + 2^{m-1}, m) = 20349` and
  the descended shape depend on `m` and the arm, not on `p'`, and every ladder
  prime is below `2^31` so msolve uses the same 32-bit modular path. The 13-bit
  rung is therefore the *cheapest* m = 5 case, and it already exhausts the cap.
  The m = 5 boundary is consequently documented at `p' = 4111` for arms (ii) and
  (iii) rather than re-purchased at every rung; the larger rungs carry the
  m = 4 Joux–Vitse fallback, which is what the contract's stopping rule makes the
  observable for a cell whose m = 5 attempt is `not_measured`.
* **D-5 (early stop on repeated identical exhaustion).** A cell stops after a
  small number of *consecutive* `not_measured` targets instead of re-confirming
  the same host limit twenty times (`--max-consecutive-not-measured`, default 3;
  2 for the m = 5 cells). `targets_planned` stays 20 and every unattempted target
  is listed in `not_measured` with class `resource_exhaustion` and the stop
  reason, so nothing is silently dropped.
* **D-6 (arm (iii) is a cruder realisation than FHJRV's).** FHJRV express the
  symmetrised object in the invariant ring itself (`P_{phi,n}` in
  `s_1..s_{n-1}, e_n` via the equivariant degree-2 map `phi`, which needs `b` to
  be a square in `F_q`), and report 4125 terms for `n = 6`. The construction used
  here instead multiplies the two summation polynomials of the `T`-orbit and
  rewrites the product in `t_i = x_i + b/x_i`; this quotients by the same group
  and needs no square root of `b`, but the resulting polynomial has twice the
  degree in the target coordinate (16 rather than 8) and is dense (20349 terms).
  That difference is a plausible part of why the m = 5 F4 step exhausts memory
  here while FHJRV report seconds with FGb, and it is stated because it bounds
  what these `not_measured` outcomes can mean: **they are a property of this
  construction, this solver and this 11 GB host, not of the ideal degree.**

## 4. Infrastructure and protocol events (all of them)

* **Five validation iterations.** `RUN-GFPN-4892a8` (failed,
  `infrastructure_error`: `IndexError` in the independent verifier, which was
  handed 3-element coefficient lists from `ladder.json` where it expected 5 —
  fixed by padding in `pdp_common.pad5`), `RUN-GFPN-f55fbd` and
  `RUN-GFPN-650471` and `RUN-GFPN-a0fb62` (failed, `implementation_error`: three
  successive *fixtures* were wrong, not the verifier — a base point whose `x` is
  not in `F_p`, then a search for a prime-order point inside the factor base that
  cannot generally exist, then an assertion that `x in F_p` implies
  `x + b/x in F_p`, which is false because `b = c z` lies in `F_q \ F_p`).
  `RUN-GFPN-b336b6` passes all sixteen checks. Every iteration is kept.
* **`RUN-GFPN-bbed6f` is an INVALID anchor record and must be superseded.** All
  five of its targets died with SIGSEGV (`returncode -11`) inside msolve at the
  17-bit rung, and the run's own code nevertheless recorded
  `status: completed_valid` with a `median_wall_seconds` of 0.013 s and
  `faster_than_published: true` — figures that are meaningless because no Gröbner
  basis was computed. The status logic was wrong: it counted a target as timed
  successfully whenever it had not *timed out*. This was fixed
  (`outcome in {ok, timeout, memory_exhausted, crashed}`), and the valid anchor is
  `RUN-GFPN-61bba9` at the 25-bit rung. **The Coordinator should register
  `RUN-GFPN-bbed6f` as superseded by `RUN-GFPN-61bba9`**; the Executor does not
  edit an archived run record, and `tools/run_supersession_registry.yaml` is
  outside this task's write scope.
* **`RUN-GFPN-a716d4`** (build, p' = 4111): terminated by the Executor 39 minutes
  in to re-stage the build order after the m = 5 probe; closed out as
  `failed / infrastructure_error`. One polynomial it completed (arm (ii), m = 5,
  EcGFp5-shaped) is deterministic from its recorded seed, was held-out verified,
  and is reused with its sha256 by `RUN-GFPN-42a000`.
* **`RUN-GFPN-61a67b`** (cell, arm (iii), m = 5, p' = 4111): target 0
  `memory_exhausted` after 856.6 s at the 11 GB cap; stopped by the Executor
  during target 1 and re-run as `RUN-GFPN-805701` with the in-driver early stop.
  Closed out as `failed / resource_exhaustion` by
  `implementation/close_terminated_run.py`.
* **A scratch feasibility probe was killed by the dispatching session's memory
  guard** at 13.1 GB. It was a pre-run sizing test of the interpolation step, not
  a run record, and no number in this experiment comes from it. The construction
  code was then changed to hold a single interpolation matrix and to fill it in
  blocks, and every child since runs under an explicit address-space cap.
* **msolve peak memory is measured per child** from `/proc/<pid>/status` `VmHWM`
  and `VmPeak`, not from `RUSAGE_CHILDREN`, which is a maximum over every child a
  process has ever reaped and would have attributed one target's peak to the next.

## 5. Ladder actually used

| rung | p' | bits | field | EcGFp5-shaped curve | order | cofactor |
|---|---|---|---|---|---|---|
| 1 | 4111 | 13 | `F_p[z]/(z^5-2)` | `y^2 = x(x^2+2x+63z)` | 2 · prime | 2 |
| 2 | 262151 | 19 | `F_p[z]/(z^5-3)` | `y^2 = x(x^2+2x+84z)` | 2 · prime | 2 |
| 3 | 16777291 | 25 | `F_p[z]/(z^5-2)` | `y^2 = x(x^2+2x+59z)` | 4 · prime | 4 |
| anchor-only | 65551 | 17 | `F_p[z]/(z^5-2)` | — | — | — |

Span 13 → 25 bits = **12 bits over three primes**, meeting the contract's floor.
Matched controls at rung 1: `random_2torsion` `y^2 = x(x^2+ax+b)` (cofactor 2) and
`random_no2torsion` `y^2 = x^3+ax+b` with irreducible cubic (cofactor 1), both with
`a, b` drawn from the seeded stream. The 31-bit rung (1073741831) was selected but
never used: the m = 5 systems it would carry are the same size as at 13 bits, which
already exhausted the cap.

## 6. What was and was not measured

**The contract's own cells** use random known-scalar targets `R = [k]G`. At m = 5 they
all ended `not_measured / resource_exhaustion`. At m = 4 they completed, and — as the
Joux–Vitse (n−1)-point method predicts for an overdetermined system — no random target
decomposed, so those cells measure decomposition-**test** cost and a success rate of
0/20, and leave `D` undefined.

**Supplementary constructed-solvable cells** (clearly labelled `target_kind:
constructed_solvable`, not the contract's cells) build a decomposable target by summing
m factor-base points and defining `G := that sum`, `k := 1`. The planted points are
never given to the solver: msolve solves the same system and its own solutions are
lifted and independently re-verified. These are the only cells with a defined ideal
degree, and their success rate is 1 by construction — recorded as
`success_rate_by_construction`, never as `decomposition_success_rate`. (In the **raw**
arm's runs the field `decomposition_success_rate` was nevertheless filled with 1.0;
`cmd_raw` was not given the same split as `cmd_cell`. Read it as
"recovery rate on constructed-solvable targets", not as a decomposition probability.)

`fp_operations_per_pdp` is a **proxy** (§1.4). The m = 4 values are nearly identical
across primes and across arms because the proxy is built from msolve's matrix shapes,
which are p-independent, and because arms (ii) and (iii) produce systems of the same
shape under this construction (D-6).
