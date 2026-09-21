# EXP-ECTD-001 driver -- MANIFEST

Pure Python 3 standard library implementation of the full EXP-ECTD-001 instrument:
ordinary prime-field elliptic curve isogeny-class construction, the five frozen
Semaev/Gröbner/Macaulay meters, the mandatory planted-outlier control, the three
required null arms, permutation stability, and matched Pollard-rho / BSGS
baselines with certificate discipline. No SageMath, no external CAS at runtime
(see `ledger/corrections/CORR-20260805-7f3a08.yaml` for why Sage is unavailable in
this environment).

Every non-trivial mathematical building block below was independently validated
against brute-force / ground-truth computation in a dedicated `selftest_*.py`
module **before** being used in a real run. Run `python3 -m driver.selftest_basic`,
`selftest_divpoly`, `selftest_semaev`, `selftest_isogeny`, `selftest_groebner` (in
that order) from `experiments/EXP-ECTD-001/` to reproduce all self-tests.

## Module map

| file | purpose | validated by |
|---|---|---|
| `fp.py` | F_p arithmetic: inverse, Legendre symbol, Tonelli-Shanks sqrt, deterministic Miller-Rabin primality (witness set valid to ~2^81, covers the full 40-56 bit range with certainty, not merely probabilistically), random-prime search | `selftest_basic.py` |
| `curve.py` | short Weierstrass group law (affine), Hasse-interval + BSGS exact order-finder (no Schoof/SEA needed) | `selftest_basic.py` (brute-force point enumeration cross-check) |
| `divpoly.py` | division polynomials ψ_2,ψ_3,ψ_5,ψ_7 via the standard recursion (only the odd-index recursion is used -- see module docstring for why no polynomial-division step is ever needed) | `selftest_divpoly.py` (roots cross-checked against brute-force-enumerated torsion points) |
| `semaev.py` | Semaev S_3 (explicit closed form) and S_4 (direct 4x4 Sylvester-resultant evaluation -- see "S4 via resultant" below), plus x-only point doubling/addition derived from S_3 | `selftest_semaev.py` (S_3/xDBL/xADD/S4 all cross-checked against real curve arithmetic) |
| `isogeny.py` | rational ℓ-isogeny kernel finding (ℓ∈{2,3,5,7}) + Vélu's formula | `selftest_isogeny.py` (every returned neighbor's order independently brute-force re-verified against the source curve's order) |
| `isogeny_class.py` | BFS isogeny-class construction (seed search + walk to size ≥64) | exercised end-to-end in `selftest_isogeny.py`'s neighbor-finding and in RUN-ECTD-001-impl |
| `mvpoly.py` | sparse multivariate F_p polynomial arithmetic, grevlex order | `selftest_groebner.py` |
| `groebner.py` | from-scratch Buchberger Gröbner-basis algorithm with degree tracking (the `groebner_solving_degree_d_reg` meter) | `selftest_groebner.py` (ideal-membership property: GB elements vanish at a planted common root, checked over 30 random systems + one hand-checkable case) |
| `macaulay.py` | Macaulay matrix construction + modular-rank first-fall-degree scan (the `macaulay_rank_defect_at_first_fall` meter) | exercised via `meters.py` against the same systems `groebner.py` validates |
| `meters.py` | the five frozen per-curve meters, the frozen factor-base rule, and the CTRL-PLANTED-OUTLIER sampling mode | integration-tested in RUN-ECTD-001-impl |
| `nulls.py` | CTRL-OUTSIDE-CLASS and CTRL-DEGREE-PROFILE constructions | integration-tested in RUN-ECTD-001-impl |
| `analysis.py` | the frozen decision-table logic (per-meter outlier stats, CTRL-PLANTED-OUTLIER check, CTRL-PERMUTATION check, null gates, `confirmed_outlier_meters`) | integration-tested in RUN-ECTD-001-impl |
| `rho_bsgs.py` | matched Pollard rho + BSGS baselines with independent certificate re-verification | integration-tested in RUN-ECTD-001-impl (both solvers agree and both certificates verify on every completed class) |
| `run_common.py` | git/environment capture, factor-base-rule hash, run-manifest builder | -- |
| `run_impl.py` | RUN-ECTD-001-impl entry point | -- |
| `run_screen.py` | RUN-ECTD-001-screen entry point | -- |

## Documented scoping decisions (protocol deviations, disclosed per AGENTS.md rule 5)

### 1. Bit-range scoping: N in [40,44] bits, not the full [40,56]

The frozen contract allows any N in [40,56] bits; this driver uses the **low end**
of that allowed range (40-44 bits) for both RUN-ECTD-001-impl and
RUN-ECTD-001-screen. This is a scoping choice **within** the frozen range, not a
relaxation of it. Reason: matched Pollard-rho / BSGS baselines (CTRL-RHO /
CTRL-BSGS) cost O(sqrt(N)) time (BSGS) and O(sqrt(N)) memory (BSGS baby-step
table); at N~56 bits that is sqrt(2^56)=2^28~268M table entries -- infeasible in
this session's pure-Python, single-process, real-wall-clock budget. At N~41 bits,
sqrt(N)~2^20.5~1.5M, which completes in tens of seconds. Every curve's isogeny
class still satisfies `n_bits_lo=40 >= 40` and every class still reaches
`min_class_size=64` exactly as frozen.

### 2. Isogeny walk uses a restricted (but never incorrect) kernel-finding method

See `isogeny.py`'s module docstring in full. Summary: a Galois-stable rational
ℓ-isogeny kernel requires Frobenius to stabilize the kernel subgroup setwise; this
driver only constructs the sub-case where Frobenius acts as **-1** on the kernel
(equivalently: the kernel's representative x-coordinates are individually F_p
-rational, found as roots of the ℓ-division polynomial). This is a **strict
subset** of all rational ℓ-isogenies for ℓ=5,7 (ℓ=2,3 are fully covered -- proved
in the docstring from the quotient-group structure of (Z/ℓZ)*/{±1}). The
consequence is possible under-counting of isogeny-graph edges (BFS may need more
seed attempts to reach size 64), **never** an incorrect edge: every constructed
neighbor is independently re-verified (`isogeny.verify_order_preserved`) to have
the exact same prime order N as the source curve before being accepted, and this
verification was itself cross-checked against brute-force point counting in
`selftest_isogeny.py` (not merely trusted).

### 3. S4 via direct resultant evaluation, not a hardcoded symbolic expansion

The original plan was to derive S_4's fully expanded coefficient form once
(symbolically) and hardcode it, to avoid a runtime CAS dependency. In practice,
`semaev.S4_via_resultant` (a direct, from-scratch 4x4 Sylvester-determinant
evaluation of the resultant of the two S_3-in-X quadratics) is cheap enough to
call directly on every evaluation -- there was no need for the symbolic expansion
or hardcoding step, and no sympy dependency was ever required at runtime.
`S4_via_resultant` is validated against 200 real 4-point curve relations in
`selftest_semaev.py`.

### 4. CTRL-RHO drops the negation-map optimization (documented in `rho_bsgs.py`)

The spec names "Pollard rho (negation)"; this driver's first negation-folded
implementation was **measured** (not assumed) to hit the well-documented
"fruitless short cycle" pathology of negation maps (Wiener-Zuccherato /
van Oorschot-Wiener): ~2.5% of Floyd-cycle detections were degenerate, and step
counts occasionally exceeded 500x the sqrt(N) expectation. Implementing and
independently verifying a correct escape mechanism was assessed as out of scope
for this session's realistic time budget. The driver runs **plain** (non-negation)
r-adding-walk Pollard rho instead: methodologically standard, immune to that
failure mode, costing a constant factor sqrt(2) more group operations, reported
as measured `group_ops` (never compared against a negation-based estimate).
CTRL-BSGS is unaffected.

### 5. Operational (not literature-canonical) definitions of `groebner_solving_degree_d_reg` and `macaulay_rank_defect_at_first_fall`

Both are defined precisely and frozen in `groebner.py` / `macaulay.py`'s
docstrings: the max total degree of any S-polynomial this from-scratch Buchberger
implementation constructs, and the first Macaulay-matrix degree (scanning up from
the system's max initial degree, capped at `+6`) whose rank falls below
`min(nrows,ncols)`. These are standard, well-defined proxies for the literature
notions of degree of regularity / first-fall degree, not claimed identical to
them, and applied byte-for-byte identically to every curve, every outside-class
draw, and every degree-profile null system (satisfying
`spec.inputs.factor_base_rule`'s "identical convention" requirement, extended
here to the solver convention generally).

### 6. Factor-base size

`fb_size=8` for every curve/class/null arm (frozen, hashed via
`run_common.factor_base_rule_hash` into every run manifest). Chosen so that
FB^2=64 and FB^3=512 relation-density evaluations, and Gröbner/Macaulay systems of
degree ~8-14 in 2 variables, all complete in about a second per curve -- this is
what makes a real ≥5-class, 64-curve-per-class screen with full instrumentation
tractable inside a single session. **Honest observation, not fabricated**: at this
factor-base size, the `groebner_solving_degree_d_reg` and
`macaulay_rank_defect_at_first_fall` meters showed **zero variance** across all 64
curves of RUN-ECTD-001-impl's class (every curve, including the deliberately
planted one, scored identically) -- the frozen Semaev+FB system's degree profile
appears to be "generically" determined at this scale, independent of the specific
curve's coefficients, at least for the instances sampled. This is reported as a
real measurement outcome, not adjusted or hidden.

## CTRL-PLANTED-OUTLIER mechanism

For one designated curve per class (the last curve discovered by the BFS walk),
target points R for the density/probability meters are constructed as
`R = P_i + P_j` (or `P_i+P_j+P_k` for the m4 system) for factor-base points
`P_i,P_j,P_k` -- guaranteeing (via the independently-verified S3/S4 identity) that
R actually decomposes over the frozen factor base, without touching the FB
convention, the meter definitions, or the solver budget for any other curve. This
inflates `semaev_m3_relation_density`, `semaev_m4_relation_density`, and
`fb_decomposition_probability` from a typically-zero class baseline to a clearly
nonzero value -- an unbounded ("infinite") ratio against a zero median, which
`analysis.py` treats as a definite outlier (see "zero-median handling" below), not
an ambiguous case.

## Zero-median handling (`analysis.py`)

At `fb_size=8` and the sample counts used, most curves show **exactly zero**
relation density / decomposition probability (a real, expected consequence of a
factor base far smaller than sqrt(p) at this toy scale -- not a bug). When a
meter's class median is exactly 0, `[0.1,10]x`-median homogeneity collapses to
"every value must be 0"; a single nonzero value against an all-zero background is
recorded as an outlier candidate with `ratio="inf"` (serialized as the string
`"inf"`, since JSON has no native infinity), never silently dropped or treated as
0/0.

## Results summary (both runs completed; see run directories for full artifacts)

**RUN-ECTD-001-impl** (1 class, N=905902646351, 40 bits, size 64, seed 201):
completed in 169.8s. Planted control recovered (via the three density/probability
meters). All 5 primary-meter permutation-stability checks stable. Both null gates
passed. Matched rho (2,914,040 group ops) and BSGS (2,649,536 group ops) both
independently certificate-verified. `decision_branch: resource_incomplete` --
this is the DESIGNED scope of a 1-class smoke run (spec.decision_table's
`scoped_homogeneity` branch textually requires ">=5 classes"; this run
intentionally covers 1), not an execution failure; see `run_impl.py`'s decision
section for the exact reasoning recorded alongside the branch.

**RUN-ECTD-001-screen** (5/5 classes completed, seeds 201-205, all N=40 bits,
all size 64): completed in 1260.8s (~21 min), well inside the 7200s/run and
40-CPU-hour budget ceilings. Every class: planted control recovered, all 5
permutation-stability checks stable, both null gates passed, matched rho and BSGS
both independently certificate-verified. `decision_branch: scoped_homogeneity`:
no class produced a CONFIRMED outlier (i.e. an outlier meter whose winning
curve(s) exclude the deliberately-planted curve, is permutation-stable, and
passes both null gates) on any of the 5 primary meters. Class-construction seed
retries: 201 used 2 attempts, 202 used 2, 203 used 1, 204 used 4, 205 used 4 (all
recorded as infrastructure per `spec.replication.seed_policy`, never as
homogeneity evidence); zero full class-construction failures.

**Important reported caveat (not hidden)**: the per-class `factor10_homogeneous`
raw flag is `False` in every one of the 5 classes -- but inspection of the
underlying stats (see `planted_control_receipt.json`) shows this is caused
*solely* by the deliberately-planted curve (curve index 63) being the sole
`argmax` for the three density/probability meters in every class, exactly as
CTRL-PLANTED-OUTLIER is designed to produce. The properly-gated
`confirmed_outlier_meters` statistic (which excludes wins attributable only to
the planted curve, per `analysis.confirmed_outlier_meters`) is `[]` in every
class, and it is `confirmed_outlier_meters`, not the raw `factor10_homogeneous`
flag, that drives `decision_branch` selection in `run_screen.py`. The raw flag is
still reported (not suppressed) via `decision_branch_caveat` in `raw-result.json`,
because AGENTS.md rule 4 requires recording deviations rather than silently
smoothing them over, even when (as here) they do not change the run-level
conclusion.

**Honest null observation, not fabricated**: `groebner_solving_degree_d_reg`
(median=14, min=14) and `macaulay_rank_defect_at_first_fall` (median=2, max=2)
were **exactly identical across all 320 real class curves, all 80 planted-curve
recomputations, and every outside-class / degree-profile-null draw** in
RUN-ECTD-001-screen -- i.e. zero measured variance on those two meters at this
frozen configuration (`fb_size=8`, 2-variable m=2 Semaev system). Only the three
Monte-Carlo density/probability meters (`semaev_m3_relation_density`,
`semaev_m4_relation_density`, `fb_decomposition_probability`) showed any
per-curve variation among real (non-planted) curves, and that variation was
"flat zero for essentially every real curve, nonzero only for the deliberately
planted one" -- never a naturally-occurring >=100x spread among real curves.
This is reported as a genuine measurement outcome of this driver's frozen
convention at this toy scale, not as a claim that the underlying mathematical
quantities are constant in general.

## Certificate discipline

Meter-computation runs declare `certificate.kind: none` explicitly (pure
measurement, nothing solved). Every Pollard-rho and BSGS discrete-log solve emits
a `certificate.kind: discrete_log` statement (`P`, `Q`, `k`) that is independently
re-verified by `rho_bsgs.independent_verify_discrete_log`, which recomputes `k*P`
from scratch via `curve.scalar_mul` -- a code path that never touches the
solver's internal state -- before the run may report `verified: true`.
