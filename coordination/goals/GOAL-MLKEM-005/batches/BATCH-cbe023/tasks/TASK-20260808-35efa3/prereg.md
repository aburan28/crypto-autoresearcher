# BATCH-cbe023 pre-registration — the AM-4 admissibility gate and the two instrument repairs, frozen before any data

TASK-20260808-35efa3 / BATCH-cbe023 / GOAL-MLKEM-005
Executor artifact. **Claim tier TOY.** Nothing in this document, and nothing any
measurement it governs can produce, bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model.

Governing authority: `ledger/decisions/DEC-20260806-607779.yaml`, amendments
**AM-6** (a positive control must present a real violation and its step selection
must not maximise the injection's own denominator), **AM-7** (the SE of a
cross-family tail-quantile comparison must contain the variance that dominates
it, with a replicated null calibration and a relative-effect floor above the
null's own median), **AM-8** (the AM-4 triple plus a `q`-sweep and a rank sweep
are a PRE-REGISTRATION GATE over every candidate observable), and **AM-9** (the
`k` nomenclature). `AM-3` and `AM-4` are RETAINED. `AM-1`'s 13-point `t` grid is
RETAINED and not re-litigated.

This document governs three measurement tasks:

| task | section | what it runs |
|---|---|---|
| TASK-20260808-2a9085 | **A** | the AM-4 admissibility gate over every candidate observable — exhibit an admissible one, or archive the obstruction |
| TASK-20260808-cece0c | **B** | AM-6: the AM-3 positive control rebuilt, `c_min` in closed form at all 12 steps of all 4 cells |
| TASK-20260808-3a5f18 | **C** | AM-7: the matched-`V` comparison rebuilt with an SE that contains the variance it omitted |

---

## 0. What this document is, and what was NOT done to produce it

### 0.1 The declaration

**No measurement of any kind was performed in producing this document.** No
lattice was generated, no lattice was reduced, no basis was built, no GSO frame
was computed, no error draw was sampled, no quantile was estimated, and no
`E_I`, `V`, `m3`, `D`, `c_min`, invariance residual or arm statistic was
evaluated. No `fpylll` call, no `numpy` RNG draw, and no lattice code was
executed. The only code executed was closed-form design arithmetic in
`(d, beta, k, n, S, E, R, alpha, nu)` — Student-`t` tail quantiles via
`scipy.stats.t`, Wilson binomial interval endpoints, `E[V]_haar`, the TL
reachable-`V` intervals, and elementary projector algebra. Section 6 enumerates
every constant with its class so a reviewer can check this claim mechanically
rather than take it on trust.

### 0.2 The three classes of number

* **[carried]** — a structural constant of the design, fixed by
  `DEC-20260805-4823db` / `DEC-20260806-00deff` / `DEC-20260806-14ac13` /
  `DEC-20260806-607779`, or carried verbatim from the committed frozen text of
  BATCH-436ddd / BATCH-f19c37 / BATCH-a44d08.
* **[quoted: source]** — a value read out of a committed artifact or a review
  report, with its source named. A quoted value is never a result of this batch
  and is never scored here.
* **[closed form]** — evaluated here from an algebraic expression in the design
  parameters alone. **No [closed form] number below is a function of any
  lattice, any frame, any draw, or any measurement.**

### 0.3 The producer split and the notarization pattern, carried unchanged

`EV-MLKEM-94c773` and `EV-MLKEM-cd9878` record that the split-producer freeze
worked twice: the freeze is a separate commit, made by a separate task,
containing nothing but the frozen text and its receipt, and an ancestor of every
commit carrying a measurement artifact — a property of the repository rather
than an assertion by a producer. The Validator verified that chain in both
directions for BATCH-a44d08 (NC-1..NC-10) **[quoted: validation_report.yaml]**.
The pattern is retained without modification. TASK-20260808-e725b4
snapshot-commits this directory **before** TASK-20260808-2a9085, -cece0c or
-3a5f18 is dispatched. Two carried corrections bind every measurement task here:

* **V-7.** Assert `git merge-base --is-ancestor <notarizing commit> HEAD`
  against the **notarizing commit itself**, never its parent, and record the sha
  asserted. BATCH-f19c37's check would have passed had the notarization never
  happened **[quoted: validation_report.yaml N-1 / V-7]**.
* **No early durability commit.** No measurement task makes one, for any reason
  **[carried: `DEC-20260806-14ac13`]**.

Each measurement re-hashes this file, compares against the notarized receipt,
**aborts on mismatch**, and quotes the digest in its report. A mismatch is a
harness failure, not a result.

### 0.4 The arrangement in which THIS card could not fail — in both directions

The program has now scored a check in the one arrangement where its own defect
was invisible **eight** times: G3, P3, F-A1, CTRL-BS, CTRL-POSHOM, CTRL-IDXMAP,
Section A's `E_I` arm, and BATCH-a44d08's AM-3 positive control **[quoted:
`DEC-20260806-607779` rationale; `EV-MLKEM-cd9878` OBS-X2]**. The eighth was of
a new kind: the pre-registration named two could-not-fail forms, both of the
shape *the gate cannot fire*, and did not name the mirror, *a positive control
that cannot pass* — which is the one it ran in. Both directions are named here,
for this card and for each section.

**Direction 1 — the card could not fail (thresholds chosen to be met).** A
pre-registration written after the numbers exist, or with thresholds chosen
because the writer already knows what the data will do, cannot fail: every
falsifier it declares is one it has already seen pass.

*Why this card is not in it.* (a) The freeze is externally notarized before the
measurement tasks are dispatched (0.3); the ordering is a property of the git
record. (b) Every threshold below is **[carried]** or **[closed form]** and is
listed in section 6 with its provenance; a reader can recompute each without any
datum of this batch. (c) The residue this cannot close is off-repository
pre-computation, and 0.1 is the declaration that answers it; it is closed by
harness structure, not by cryptography **[quoted: validation_report.yaml N-2]**.

**Direction 2 — the card could not PASS (thresholds no producer can ever
meet).** A pre-registration whose gates are unreachable makes every outcome an
instrument outcome. Then "no admissible observable exists", "the gate cannot
fire" and "the falsifier is uncalibrated" are properties of this document, not
findings, and the batch is unfalsifiable in the direction that matters.

*Why this card is not in it — computed in advance, per section.*

1. **Section A.** The gate carries two POSITIVE CONTROLS that are exact
   invariants by construction (`X8` root-determinant, `X9` normalized `lambda_1`)
   and one TRIVIAL control (`X7 = tr(P^2) = beta`) that must pass invariance.
   If the invariance criterion refuses `X8`, the gate is INSTRUMENT-LIMITED and
   **no refusal of any candidate may be reported** (2.10).
2. **Section B.** `c_min(i)` is finite at every step with `SE_diff > 0` and the
   report covers all 12 steps of all 4 cells with no selection at all, so there
   is no step at which the control can be trapped. The closed-form relation
   `c_min(i) > c_pos(i)` (3.2) guarantees that every reported firing sits on a
   genuinely positive post-injection `Delta`, which is exactly what
   BATCH-a44d08's control could not produce.
3. **Section C.** The calibration gate `G-CAL = 0.040` is reachable at the
   declared replication: at `R = 200` the Wilson 95% upper bound is `0.01885`,
   `0.02777`, `0.03572` at `0`, `1`, `2` observed false falsifications — all
   below `0.040` — and `0.04317` at `3`, which refuses **[closed form]**. So the
   gate can pass and can fail, and both were computed before any datum exists.
   `R_min = 200` is a hard floor precisely because at `R = 100` even a perfect
   null (`0` of `100`) has Wilson upper `0.03699`, which passes `0.040` only by
   `0.003` and leaves no room to refuse — and at a `0.025` gate would have made
   PASS unreachable outright. That computation is why `R_min` and `G-CAL` are
   what they are.

**Direction 3 — the residue I cannot close.** I chose which observables to put
on Section A's candidate list, which nulls to build in Section C, and which
summaries to freeze. A different choice tests a different proposition. Sections
2.11, 3.9 and 4.11 name, per section, the specific proposition that section does
**not** reach, and 2.6 states in advance what would make Section A's obstruction
an artifact of my list rather than a general fact.

### 0.5 Inference record for this card (verbatim)

```
requested_policy: executor-implementation
degraded_allowed: false ; fallback_allowed: false
resolved: under the Claude Code runtime, per CLAUDE.md, per-role model selection is
  process-level and subagents keep model: inherit, so the resolved model is the session model
fallback_used: false
model_verified: false (no adapter probe receipt for this session)
```

---

## 1. Constants and conventions carried into all three sections

All **[carried]** unless marked:

* `q = 3329`; error law `CBD_{eta=2}` (`mu_4 = 2.5` exactly).
* Statistic `R = ||Q^T e||^2 / ||e||^2`, `Q` the orthonormal tail-`beta` GSO
  frame taken as the last `beta` columns of `Q` from `QR(B^T)`; `P = Q Q^T`.
* `E_I(beta) = (1/beta) sum_{a in K_I} P_aa`;
  `V = sum_a P_aa^2 - beta^2/d`;
  `m3 = sum_a (P_aa - beta/d)^3`.
* `q_emp(p) = sort(R)[round(p*N) - 1]` at `N = 2^20` per pool; index `1023` at
  `p = 2^-10`; `D = q_emp(2^-10)/q_Beta(2^-10) - 1`,
  `q_Beta(2^-10) = betaincinv(beta/2, (d-beta)/2, 2^-10)`.
* `E[V]_haar = 2*beta*(d-beta) / (d*(d+2))` — exact, re-derived independently by
  the Validator from `P_aa ~ Beta(beta/2, (d-beta)/2)` **[quoted:
  validation_report.yaml]**.
* `8` draws per arm (`n = 8`), every arm including every null.
* Carried seed formulas: `seed_basis_k(d,k,i) = 810000 + d*1000 + k*10 + i`;
  `seed_error(d) = 20260805 + d`; `seed_graded(d,beta,j) = 500000 + d*1000 +
  beta*10 + j`; `seed_haar(d,beta,j) = 900000 + d*1000 + beta*10 + j`.
* Graded family `Q_t = QR( sqrt(1-t) * E_S + sqrt(t) * G )` on the AM-1 13-point
  `t` grid `{0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.25,
  0.5, 1.0}`, giving 12 consecutive steps.
* Gate `SE_diff(A,t) = sqrt(sd_A^2/8 + sd_haar^2/8)`; `4.0` is a nominal factor,
  not a p-value, and its realized one-sided false-positive rate was measured at
  `0.0015-0.0025` against a nominal `3e-5` **[quoted: validation_report.yaml
  item 4 / V-5]**. Every report citing the gate states this.
* `t_{7,0.998} = 4.2071245566046755`; `P(t_7 > t_crit) = 0.0019999999999982102`
  **[closed form]**.

New streams introduced by this document use a collision-free tuple seed:
`rng = numpy.random.default_rng([TAG, d, k, beta, r])` with `TAG` fixed in
section 6. Carried scalar seeds are used unchanged wherever a reproduction
against a committed record is required.

### 1.1 AM-9: the `k` convention, disclosed structurally

**Throughout this document `k = |K_I|`, the size of the IDENTITY block**, and
`d - k = |K_q|`, the number of `q`-scaled rows. `fpylll`'s
`IntegerMatrix.random(d, "qary", k=..., q=...)` parameter counts the **`q`-scaled
rows**, i.e. `|K_q|`, and is written `k_fpylll = d - k` wherever it appears
**[quoted: report_k.md section 3; Red Team RT-X2]**. The two coincide only at
`k = d/2`, which is why no committed record could distinguish them, and no
committed number in this goal changes.

**The convention is disclosed structurally and not by a label**: every basis in
Sections A and C is BUILT EXPLICITLY as `B = [[I_k, A], [0, q*I_{d-k}]]` with
`A` of shape `(k, d-k)`, so the block roles are fixed by the construction and
not by a generator's documentation. Where `fpylll`'s generator is called at all
(Section C's committed unreduced arm, at `k = d/2`, where the two conventions
agree), the call is written with `k_fpylll` and the report states both readings.

### 1.2 What AM-4 requires, stated once

AM-4 requires an ADJUDICATOR of a claim about a lattice to be invariant under
(a) ambient isometry `B -> BH`, `H` orthogonal; (b) row permutation of `B`;
(c) unimodular `B -> UB`, `U in GL_d(Z)`. (b) is a special case of (c) and is
listed separately because it is the cheapest transform and catches any
implementation that depends on row order. Invariance under (b) and (c) means the
observable is a function of the LATTICE and not of a basis; invariance under (a)
means it is a function of the ISOMETRY CLASS.

**AM4-OBS-1 is a MEASURED ARGUMENT FROM ONE RED-TEAM SESSION, NOT A THEOREM.**
Its `E_I`, `m3` and `D` table is a single session on its own frames at one
`(d, beta, k)`, not pre-registered and not replicated; only `V`'s
non-invariance is corroborated across batches **[quoted: `EV-MLKEM-cd9878`
named_finding, OBS-X1]**. Section A tests it, including the test that could
refute it (2.4), and does not inherit it.

### 1.3 Binding carries, stated here and repeated in each section's report

1. **AM-3 IS NOT RETIRED.** Its `0.096` family-wise false-failure bound is
   correctly derived, was declared before any datum existed, and is mechanically
   free of every run-supplied quantity. Its POWER is UNDEMONSTRATED, not
   disproved. Retiring it on a defective positive control would be premature
   closure in the exact sense `docs/inventor-protocol.md` section 4 names
   **[carried: `DEC-20260806-607779` amendment_disposition AM-3]**.
2. **Section C's proposition — whether `D` depends on the frame only through `V`
   at the `2^-10` quantile — stays OPEN IN BOTH DIRECTIONS.** No successor may
   cite "L2 tail sufficiency falsified" or "L2 tail sufficiency consistent" from
   BATCH-a44d08, and no successor may cite its eight non-firing pairs as upper
   bounds; those floors are VOID because they are computed from the invalid SE
   **[carried: AM-7 consequence_for_the_record]**.
3. **The `E_I` arm may NOT be re-frozen without a `q`-sweep and a rank sweep**
   **[carried: AM-8]**. Section A runs both over every candidate.
4. **Claim tier TOY, unconditionally.** No number measured at `d <= 140` is
   transported to `beta = 606`, `d = 1420`, to any FIPS 203 parameter set, to any
   attack cost, or to any other parameter set, by extrapolation or by analogy.
5. **Budget exhaustion, timeout, crash, or a missing dependency is INFRASTRUCTURE
   SIGNAL and is NEVER negative mathematical evidence** (`AGENTS.md` rule 3).
   `gmpy2` is ABSENT in this environment and nothing here may depend on it;
   `numpy 2.4.0`, `sympy 1.14.0`, `mpmath 1.3.0`, `scipy 1.15.3` and
   `fpylll 0.6.4` were verified present by import **[quoted: task card]**.
6. **`certificate.kind: none`** for all three runs, stated explicitly: no
   discrete-log solve and no factor-base relation is claimed or produced, so
   `docs/claims-and-verification.md` requires no solution certificate. The
   independent re-verifications these runs carry are INSTRUMENT CHECKS and are
   labelled as such, never as certificates.

---

## 2. SECTION A — the AM-4 admissibility gate, applied BEFORE anything is frozen

Run by TASK-20260808-2a9085. This is the batch's lead. Under AM-8 the gate is a
PRE-REGISTRATION requirement over every candidate observable, not a post-hoc
review criterion. It has now refused five statistics (P3 and `V` in BATCH-f19c37;
`E_I`, `m3`, `D` in BATCH-a44d08) **[quoted: `DEC-20260806-607779`
amendment_disposition AM-4]**.

**THE OBSTRUCTION IS THE PREFERRED OUTCOME.** AM-4 already declares it so, and
`docs/inventor-protocol.md` section 4 sets the standard it must meet: a named
obstruction, an argument, and forward guidance naming what remains open. It is
pre-registered here as a first-class result with its own reporting requirements
(2.6), not as a fallback for a failed search. A fifth statistic that AM-4 refuses
is worth less than an archived obstruction with an argument.

### 2.1 The transform triple and the two sweeps, frozen

Applied to every candidate observable, on every test lattice, at every `beta`:

| id | transform | acts as | preserves |
|---|---|---|---|
| `T1` | ambient isometry `B -> B H`, `H` Haar orthogonal `d x d` | `Q -> H^T Q`, `P -> H^T P H` **[closed form]** | the lattice up to isometry |
| `T2` | row permutation `B -> Pi B`, `Pi` a random permutation matrix | a unimodular change of basis | the lattice exactly |
| `T3` | unimodular `B -> U B`, `U in GL_d(Z)`, `det U = +-1` | a general change of basis | the lattice exactly |
| `T0` | round trip `B -> B H H^T` | numerically non-trivial identity | everything |

`T0` is the NUMERICAL CONTROL. It is mathematically the identity and passes
through the identical float64 QR path, so its residual measures float noise and
nothing else. It is required and reported for every candidate.

Sweeps, required by AM-8 for every candidate:

* **`q`-sweep**: `q in {1, 2, 4, 16, 64, 256, 1009, 3329}` at fixed `(d, k, beta)`
  and fixed seeds. At `q = 1` the basis `[[I_k, A],[0, I_{d-k}]]` is unimodular
  and the lattice is `Z^d` — an object with no `q`-ary structure that no spill
  mechanism can be about **[quoted: red_team_report.md section 1.2]**.
* **rank sweep**: `rank(A) in {1, 5, 10, 20, k}` forced exactly (by constructing
  `A = A_1 A_2` with inner dimension `r`, entries uniform on `[0,q)`), at fixed
  `(d, k, beta, q)`.
* **`Z^d` in its identity basis**: `B = I_d`, run as a separate lattice, as AM-8
  requires ("at least one test lattice plus `Z^d` in its identity basis").

### 2.2 The invariance residual, its scale, and the thresholds — with units

For an observable `X`, a transform `T`, a basis `B` and a replicate `r`:

```
rho_T(X; B, r)  =  | X(T_r B) - X(B) |  /  max( |X(B)| , s_X )        [dimensionless]
```

`s_X > 0` is a DECLARED SCALE FLOOR for `X`, a function of `(d, beta, k)` alone,
fixed in the table below. Where `|X(B)| >= s_X` the residual is an ordinary
relative difference; the floor exists only so that an observable passing near
zero cannot manufacture an infinite residual.

| candidate | `s_X` | class | provenance |
|---|---|---|---|
| `E_I` | `1.0` | its full range `[0,1]` | [closed form] |
| `V` | `E[V]_haar = 2 beta (d-beta)/(d(d+2))` | the Haar expectation | [closed form] |
| `m3` | `E[V]_haar^{3/2}` | dimensional match to a third moment | [closed form] |
| `D` | `0.01` | half the smallest committed `|D|` in this goal (`0.0189`) | [closed form from a quoted magnitude] |
| `W` | `sqrt( k * 2 beta (d-beta) / (d^2 (d+2)) )` | Haar sd of a `k`-term diagonal sum, covariance neglected; used ONLY as a scale | [closed form] |
| `OD` | `E[V]_haar` | inherits `V`'s scale by the identity in 2.4 | [closed form] |
| `TRIV` | `beta` | its own value | [closed form] |
| `rdet` | `1.0` | `X` is already normalized: `|det B|^{1/d}` | [closed form] |
| `lam1n` | `1.0` | `X` is already normalized: `lambda_1(L)/|det B|^{1/d}` | [closed form] |
| `hkz` | `1.0` | `X` is a log-ratio, `O(1)` by construction | [closed form] |

**Thresholds, frozen, all dimensionless multiples of `s_X`:**

```
tau_num = 1e-6     numerical floor: max_r rho_T0 must be <= tau_num for the arm to adjudicate
tau_inv = 0.01     invariance:  PASS iff  max over {T1,T2,T3} x replicates x beta x lattices  rho_T <= tau_inv
tau_q   = 0.10     sensitivity: PASS iff  | X(q=3329) - X(q=1) | / max(|X(q=3329)|, s_X) >= tau_q
tau_rel = 0.10     relevance:   both clauses of G-REL below, at the same 10% of scale
```

Why `tau_inv = 0.01`. It sits four orders above the float64 QR noise these
constructions carry (`T0` measures it and the run reports it) and one order
below every effect this goal has ever called meaningful: Section C's own
"practically meaningful" floor is `5%` relative, and a bare row permutation was
measured moving `D` by `13.3%` **[quoted: red_team_report.md section 4]**. An
observable that moves by less than `1%` of its own scale under a
lattice-preserving re-presentation is treated as invariant to within
measurement; one that moves by more is REFUSED. Why `tau_q = tau_rel = 0.10`:
one order above `tau_inv`, so that no observable can satisfy invariance and
sensitivity through numerical noise alone, and at the order of the differences
this goal reports (`17%` to `24%` relative in Section C; `1.000 -> 0.502` in
`E_I` under `T1`).

### 2.3 The candidate observable list, frozen now

Fixing the list in advance is what stops "no admissible observable exists" from
being a statement about a search I steered. Every candidate below is scored
through the identical code path and reported whatever it does.

| id | observable | class | role |
|---|---|---|---|
| `X1` | `E_I(beta)` | `f(P)` | carried; refused in BATCH-a44d08, re-tested |
| `X2` | `V(beta)` | `f(P)` | carried; refused twice, re-tested |
| `X3` | `m3(beta)` | `f(P)` | carried; refused, re-tested |
| `X4` | `D(beta)` | `f(P, e)` | carried; refused, re-tested |
| `X5` | `W = sum_{a<=k} P_aa - beta k/d` | `f(P)` | the degree-1 alternative `EV-MLKEM-94c773` recorded as "the space is not empty" |
| `X6` | `OD = sum_{a!=b} P_ab^2` | `f(P)` | the naive "use the off-diagonal instead" repair |
| `X7` | `TRIV = tr(P^2)` | `f(P)` | **negative control**: must PASS invariance and must FAIL `q`-sensitivity |
| `X8` | `rdet = |det B|^{1/d}` | `f(L)` | **positive control 1**: an exact invariant; must PASS invariance |
| `X9` | `lam1n = lambda_1(L)/|det B|^{1/d}`, small `d` only | `f(L)` | **positive control 2**: an exact invariant that is lattice-geometric |
| `X10` | `hkz(beta) = (1/beta) sum_{i>d-beta} log||b_i*|| - (1/d) sum_i log||b_i*||` on an HKZ-reduced basis, small `d` only | `f(L)` | the one candidate that could be admissible AND relevant |

`X8`, `X9`, `X10` are the non-`f(P)` candidates AM-8's "exhibit an observable
that is not a function of `diag(QQ^T)`" clause calls for. `X9` and `X10` are
computable only where exact SVP / HKZ reduction is feasible; that is a budget
fact, declared in 2.9 with its infrastructure branch, and a failure to compute
them is INFRASTRUCTURE and never a refusal.

### 2.4 The structural argument to be TESTED, and the probe that could refute AM4-OBS-1

Two closed-form statements are recorded here as **arguments to be checked
numerically by the run**, not as established results. Both are elementary and a
reader can check them by hand; neither is a machine-checked proof.

**OBS-GEN (stronger than AM4-OBS-1, and not about `diag`).** Let `f` be any
function of the tail-frame projector `P` alone with `f(H^T P H) = f(P)` for every
orthogonal `H`. Every rank-`beta` orthogonal projector in `R^d` is conjugate to
every other by some orthogonal `H`, so `f` is constant on that entire set:
`f = f(d, beta)`. **Hence no function of the tail-`beta` frame alone can be both
AM-4-invariant under `T1` and informative about anything.** `X7 = tr(P^2) = beta`
is not an arbitrary control: it is the canonical representative of the whole
class that passes `T1`, which is exactly why the gate needs the `q`-sensitivity
criterion as well as the invariance criterion.

**Consequences fixed in advance, each falsifiable by the run.**

* For a projector, `P^2 = P`, so `(P^2)_aa = P_aa` and
  `sum_{a!=b} P_ab^2 = sum_a P_aa - sum_a P_aa^2 = beta - V - beta^2/d`
  **[closed form]**. So `X6 = OD` is an EXACT AFFINE FUNCTION of `V`: the "use
  the off-diagonal energy instead" repair is dead by algebra, before any datum.
  The run must verify `OD + V + beta^2/d = beta` to `<= 1e-10` at every frame; a
  failure is an implementation error, not a finding.
* Under Gaussian errors, `R = ||Q^T e||^2/||e||^2 ~ Beta(beta/2, (d-beta)/2)`
  EXACTLY for every orthonormal frame, so `D` would be frame-independent and
  carry no information at all **[closed form]**. Everything `D` measures comes
  from the interaction of the non-Gaussian `CBD` law with the STANDARD
  coordinate basis — i.e. from presentation-dependence. This is checked as an
  instrument control in Section C (4.5 `N-C`).
* `Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d)` is a function of `V` alone
  **[carried: prereg 4.1]**, and for a projector the third-cumulant terms
  `sum_a P_aa (P^2)_aa` and `sum_{a!=b} P_aa P_ab^2` also collapse to
  `sum_a P_aa^2` and `sum_a P_aa^2 - sum_a P_aa^3` **[closed form]**. Whether
  `D` depends on `P` beyond `diag(P)` at all therefore enters only at higher
  order, and is decided empirically by the probe below rather than asserted.

**The DIAGONAL-COLLISION PROBE — the test that could REFUTE AM4-OBS-1.**
AM4-OBS-1 asserts that every observable in this goal is a function of
`diag(QQ^T)` in the standard basis. That premise is CHECKED, not inherited.
Construct a collision pair `(P1, P2)`: take the two-level frame on `2 beta`
coordinates paired as `(a_m, b_m)` with diagonal `(u, 1-u)`, and let `P2` be the
same construction with the `a`-indices permuted among themselves while the
`b`-indices are left fixed. Then `diag(P2) = diag(P1)` EXACTLY (the multiset of
diagonal entries and their coordinate positions are unchanged) while
`P2 != P1` off the diagonal **[closed form]**. For each candidate `X`:

```
coll(X) = |X(P2) - X(P1)| / max(|X(P1)|, s_X)

coll(X) <= tau_num   ->  X is DIAGONAL-DETERMINED on this probe (AM4-OBS-1's premise holds for X)
coll(X) >  tau_inv   ->  X is NOT a function of diag alone   (AM4-OBS-1's premise is REFUTED for X)
otherwise            ->  INDETERMINATE at the probe's resolution; reported as such, never rounded
```

For `X4 = D` the probe is run against the pooled SE of `D` at the declared
`(S, E)` of Section C and its outcome is reported as an UPPER BOUND when it
falls below that floor — "`D` is diagonal-determined to within `<floor>`", never
"`D` is a function of the diagonal".

**AM4-OBS-1 is REFUTED IN PART if** any of `X1, X2, X3, X5` returns
`coll > tau_inv` (its premise fails), **or** if any of `X1, X2, X3, X4, X5`
returns `rho_T1 <= tau_inv` at every replicate (its measured conclusion fails).
Either outcome is reported as a refutation of the corresponding half, with the
other half's status stated separately. This is pre-registered so that a
corroboration cannot be manufactured by not looking.

### 2.5 The five gate criteria, and what COUNTS as an admissible observable

```
G-NUM  numerical adequacy   max_r rho_T0(X) <= tau_num = 1e-6
G-INV  invariance           max over {T1,T2,T3} x replicates x beta x lattices rho_T(X) <= tau_inv = 0.01
G-Q    q-sensitivity        |X(q=3329) - X(q=1)| / max(|X(q=3329)|, s_X) >= tau_q = 0.10
G-REL  relevance, BOTH clauses:
       REL-1 beta-dependence   |X(beta_hi) - X(beta_lo)| / max(|X(beta_lo)|, s_X) >= tau_rel
                               at (beta_lo, beta_hi) = (15, 65) for d = 100 and (20, 95) for d = 140
       REL-2 block attribution |X(d,k,beta) - X(d,d-k,beta)| / max(|X(d,k,beta)|, s_X) >= tau_rel
                               at at least one beta of the grid, on the mirrored cell pair
G-RANK rank attribution     reported for every candidate; an observable proposed as measuring the
                            identity-block size k is REFUSED AS A BLOCK-CONTENT ADJUDICATOR if its
                            departure index b*(X) = min{ beta : |X(beta) - X(beta_min)| > tau_inv * s_X }
                            tracks min(rank(A_S), beta) rather than min(k, beta)
```

> ### **AN OBSERVABLE IS ADMISSIBLE iff it passes G-NUM, G-INV, G-Q and G-REL.**
> Passing `G-INV` alone is not admissibility: a constant passes it. Passing
> `G-INV` and `G-Q` without `G-REL` is ADMISSIBLE BUT NOT RELEVANT and is
> reported as its own outcome (2.7 `R3`), never as an answer to the spill
> question. `G-RANK` is a refusal criterion for block-content claims and is
> reported for every candidate regardless.

Every criterion is reported per candidate as a NUMBER with its threshold beside
it, never as a bare PASS/FAIL: the residual distribution (min / median / max over
replicates) for each of `T0, T1, T2, T3`, the `q`-ladder, the rank ladder, and
both `G-REL` clauses.

### 2.6 What counts as the OBSTRUCTION BEING GENERAL rather than an artifact of the observables tried

The obstruction may be recorded as ESTABLISHED AT ITS DECLARED SCOPE only if all
three hold. Any one failing means it is recorded as NOT ESTABLISHED, with the
reason, which is a legitimate and reportable outcome.

* **GEN-1 STRUCTURAL.** The `OBS-GEN` argument of 2.4 is stated in the report in
  full, and its numerical corollaries are verified: `X7 = tr(P^2)` is invariant
  under `T1, T2, T3` to `<= tau_num`; `OD + V + beta^2/d = beta` holds to
  `<= 1e-10`; and **every** `f(P)`-class candidate fails `G-INV` or `G-Q`, with
  the residual reported. An obstruction argued only by counting refused
  statistics is a fatigue report and its honest status is `unverified`
  (`docs/inventor-protocol.md` section 4).
* **GEN-2 COVERAGE.** At least `3` `f(P)`-class and at least `2` non-`f(P)`-class
  candidates were actually scored, and each candidate's class is decided BY THE
  COLLISION PROBE of 2.4 rather than by assertion. If the non-`f(P)` candidates
  could not be computed (budget, `fpylll`, HKZ infeasibility), `GEN-2` FAILS and
  the outcome is **"OBSTRUCTION NOT ESTABLISHED — ARTIFACT OF THE OBSERVABLES
  ACTUALLY TESTED"**, reported with the list of what was and was not reached.
* **GEN-3 SCOPE.** The claim is stated only over the class it covers —
  observables that are functions of the tail-`beta` frame projector alone, at the
  tested `(d, k, beta, q)` grid, at `n = 8` bases — together with the explicit
  statement that it is NOT a theorem that no admissible statistic exists, and
  with forward guidance naming the two repairs that remain open:
  **(i)** weaken AM-4 to the basis-change subgroup `{T2, T3}` only, retaining the
  standard coordinate frame, under which the spill question is well posed and the
  goal's existing observables are candidates again; or **(ii)** restate the
  target question in isometry-invariant terms (for example about the GSO profile
  of a canonical reduction, `X10`), which is a DIFFERENT question and must be
  labelled as one.

The leading candidate obstruction, stated in advance so that finding it is not a
discovery made after the fact: **the spill question as posed across four batches
— "does the tail-`beta` GSO window lie in `K_I` or in `K_q`" — is a question
about the pair (lattice, standard coordinate frame), not about the lattice's
isometry class, and AM-4 requires adjudicators to be functions of the isometry
class.** If the run's outcome is `R2`, this is the statement it must argue for,
with `OBS-GEN` as the mechanism and the candidate table as the evidence. It is
an ARGUMENT ABOUT THE FORM OF THE QUESTION, and it is not a theorem.

### 2.7 The outcome map — fixed now, exhaustive, mutually exclusive

Each possible result maps to exactly one outcome. The mapping is evaluated in
order; the first matching row is the outcome.

| # | condition | OUTCOME |
|---|---|---|
| `R5` | `G-NUM` fails for a candidate (`rho_T0 > tau_num`), or a dependency is missing, or a declared budget cap binds before that candidate's arm completes | **INSTRUMENT-LIMITED / INFRASTRUCTURE** for that candidate. It is reported as NOT ADJUDICATED. No refusal and no admissibility claim may be made for it, and it does not count toward `GEN-2` |
| `R4` | any of `X1, X2, X3, X5` has `coll > tau_inv`, or any of `X1..X5` passes `G-INV` at every replicate | **AM4-OBS-1 REFUTED IN PART**, naming which half (premise or measured conclusion) and for which observable. Reported first, then the remaining rows are evaluated on the rest |
| `R1` | some candidate passes `G-NUM`, `G-INV`, `G-Q` and **both** clauses of `G-REL` | **ADMISSIBLE OBSERVABLE EXHIBITED**, with its full residual table, its sweeps, and its scope limits (`d`, `k`, `beta`, `q`, and the reduction used) |
| `R3` | some candidate passes `G-NUM`, `G-INV` and `G-Q` but fails `G-REL` | **ADMISSIBLE BUT NOT RELEVANT — the obstruction is relocated, not removed.** Reported as its own result, never as `R1` and never as `R2` |
| `R2` | no candidate reaches `R1` or `R3`, and `GEN-1`, `GEN-2`, `GEN-3` all hold | **NO ADMISSIBLE PREDICATE EXISTS AT THE DECLARED SCOPE — OBSTRUCTION ARCHIVED**, with the argument, the candidate table, and the forward guidance of `GEN-3` |
| `R2'` | no candidate reaches `R1` or `R3`, and any of `GEN-1..3` fails | **OBSTRUCTION NOT ESTABLISHED — ARTIFACT OF THE OBSERVABLES ACTUALLY TESTED**, with the failing condition named |

`R1` and `R3` are not exclusive of each other across candidates: if one candidate
reaches `R1` and another `R3`, both are reported, and the headline is `R1`.
`R2` and `R2'` are exclusive of `R1` and `R3` by construction.

**I record now which outcome I expect, so that expectation is on the record and
can be wrong**: `R3` for `X8` and `X9` (exact invariants that carry no `beta`
dependence, hence fail `REL-1`), together with `R2` for the `f(P)` class, and
`R1` for `X10` only if HKZ reduction proves both feasible and canonical enough at
small `d`. If `X10` reaches `R1` its scope limit — `d <= 40`, far below this
goal's `d in {100, 140}` — is part of the result and not a footnote.

### 2.8 Pre-registered predictions that could fail

* **PRED-A1 (two-sided, quantitative).** Under `T1`, the mean `E_I` over `8`
  isometry draws lies within `max(4 SE, 0.02)` of `k/d`, and the mean `V` within
  `max(4 SE, 0.02 * E[V]_haar)` of `E[V]_haar = 2 beta (d-beta)/(d(d+2))`. Both
  targets are exact Haar expectations **[closed form]** and both could fail. If
  either fails, the `T1` implementation is suspect and the arm is reported as
  INSTRUMENT-LIMITED before any refusal is drawn from it.
* **PRED-A2.** Every `f(P)`-class candidate fails `G-INV` or `G-Q`. Falsifier:
  any of them passing both.
* **PRED-A3.** `X7 = tr(P^2)` passes `G-INV` at `<= tau_num` and fails `G-Q`
  (its value is `beta` at every `q`). Falsifier: either half. `X7` failing
  `G-INV` means the code is wrong; `X7` passing `G-Q` means the sensitivity
  criterion does not discriminate and the whole gate is INADMISSIBLE — declared
  now, and the run reports that as its result if it happens.
* **PRED-A4.** `X8 = rdet` passes `G-INV` at `<= tau_num` under `T1` and `T2`,
  and at `<= tau_inv` under `T3` (where integer growth in `U` can cost float
  precision). Falsifier: either. `X8` failing `G-INV` means the gate cannot pass
  and **no refusal may be reported from this run** (2.10).
* **PRED-A5.** The `q`-ladder for `X1 = E_I` is monotone in `q` and
  `1 - E_I ~ q^{-2}` **[quoted: red_team_report.md section 1.1, reported there at
  16.4x / 15.6x / 16.0x / 169x]**. Quoted as the prior that motivated the sweep;
  scored here as a prediction of THIS run that can fail.

**Detection floor for Section A.** Every negative is an upper bound at a declared
floor, never an absence. For invariance: "`X` is invariant under `T` to within
`rho_max` of its scale `s_X` at `n = 8` bases and `8` replicates" with `rho_max`
printed. For sensitivity: "`X` distinguishes `q = 3329` from `q = 1` by at most
`<value>` of scale", printed. The wording ban is carried: no arm may be described
as "absent", "no departure", "vanishes", "consistent with zero" or any synonym,
in the report, the JSON or the script.

### 2.9 Construction, seeds, replicates, and the budget ladder

**Bases**, built explicitly in exact integer arithmetic, never by a generator:

```
A   = default_rng([1, d, k, i]).integers(0, q, size=(k, d-k))     i = 0..7
B   = [[ I_k , A ], [ 0 , q * I_{d-k} ]]        K_I = coords 1..k ; K_q = coords k+1..d
rank-r variant: A = A1 @ A2 mod q, A1 (k x r), A2 (r x d-k), entries uniform on [0,q)
frame: last beta columns of Q from QR(B^T), float64
```

**Lattices.** `L1 = (d,k) = (100,30)`; `L2 = (100,70)` (`L1`'s mirror, for
`REL-2`); `L3 = (100,50)` (the cell AM4-OBS-1's table was measured at);
`L4 = (140,40)`; `L5 = (140,100)` (`L4`'s mirror); `L6 = Z^100` in the identity
basis `B = I_d`; small-`d` family `L7..L12 = (20,6), (20,14), (30,9), (30,21),
(40,12), (40,28)` for `X9` and `X10`.

**`beta` grids** `[carried]`: `d = 100`: `{15, 30, 35, 50, 65}`; `d = 140`:
`{20, 40, 45, 70, 95}`; small `d`: `{d/4, d/2, 3d/4}` rounded down.

**Replicates.** `8` bases per lattice `[carried]`; `8` draws each of `H`
(`default_rng([2,d,k,beta,h])`), of the row permutation
(`default_rng([3,d,k,beta,h])`), and of `U` (`default_rng([4,d,k,beta,h])`).
`U` is built as a random permutation, a random sign flip, and `d/2` elementary
operations `R_i <- R_i + s R_j`, `s in {-1,+1}`, `i != j` — each factor has
determinant `+-1` by construction, so `det U = +-1` by construction; this is
verified exactly with `sympy` at `d <= 40` and asserted by construction above it,
and the entry-growth diagnostic `max|UB|` is reported because float64 `QR` of a
badly scaled `UB` is exactly how a `T3` residual can be manufactured.

**The `D` arm** (`X4`) needs error pools: `E = 3` independent pools of `N = 2^20`
`CBD_{eta=2}` vectors, `default_rng([7, d, p])`, `p = 0..2`, evaluated in chunks
of `2^16` rows so peak RSS stays well under the `8 GB` budget; `4` bases and
`3` replicates per transform, at `L3` `beta = 40` and `L4` `beta = 45` only.

**Cost is MODELED, not measured.** The only measured anchor is
BATCH-a44d08's Section C: `16.80 s` of `5400` for `160` `D`-evaluations at
`N = 2^20` **[quoted: `EV-MLKEM-cd9878` infrastructure_note; vmatch_report.md]**,
i.e. of order `0.1 s` per `D`-evaluation on a shared host at load `180-660`. The
`D` arm above is `2 x 4 x 3 x 4 x 3 = 288` evaluations, MODELED at order `30 s`
and capped at `3000 s`. Everything else in Section A is `QR` and small linear
algebra. These are MODELED numbers and are labelled as such; the ladder below is
keyed to WALL-CLOCK CHECKPOINTS and never to the model.

**Budget ladder, declared now** (`10800 s`, `8 GB`, `maximum_runs = 1`):

1. `X1, X2, X3, X5, X6, X7, X8` on `L1..L6`, all transforms and sweeps. If not
   complete at `3600 s`, drop `L2` and `L5` (the mirrors) and record `REL-2` as
   NOT MEASURED.
2. `X4` (`D` arm) with the caps above. If the `3000 s` cap binds, drop to `E = 1`
   pool and report the reduced replication and its consequence for the floor.
3. `X9` (exact SVP at small `d`) with a `300 s` cap per lattice. On cap: `X9` is
   NOT MEASURED at that `d` — INFRASTRUCTURE.
4. `X10` (HKZ) with a `300 s` cap per (lattice, presentation) and `3600 s` total.
   On cap, fall back to `BKZ-20` and label the arm **NON-CANONICAL**, in which
   case a `T3` residual is NOT evidence of non-invariance and must be reported as
   uninformative for `G-INV`. On the second cap: NOT MEASURED — INFRASTRUCTURE.

Any step not reached is reported as not reached, with the checkpoint that bound.
A cap that binds is INFRASTRUCTURE SIGNAL and is never a refusal of a candidate
and never an obstruction (`AGENTS.md` rule 3).

### 2.10 The arrangement in which Section A could not fail — in BOTH directions

**Form 1 — the gate could not REFUSE (it admits anything).** Set `tau_inv` so
loose, or pick candidates so degenerate, that something always passes. A constant
observable passes any invariance test.
*Guard:* `X7 = tr(P^2) = beta` is on the list precisely as the canonical
representative of the class that passes `T1` (2.4 `OBS-GEN`), and `G-Q` must
REFUSE it. **If `X7` passes `G-Q`, the gate is declared INADMISSIBLE and no
admissibility claim may be reported from this run** — declared now.

**Form 2 — the gate could not PASS (it refuses everything).** This is the mirror
BATCH-a44d08's control ran in and the direction its pre-registration did not
name. If `tau_inv` sits below the float noise of the transform path, then "no
admissible observable exists" is a property of this threshold, and the batch's
preferred outcome would be manufactured by arithmetic.
*Guards, three, all declared in advance:* (a) `T0`, the mathematically-identity
round trip, is run for every candidate and its residual is the measured noise
floor; `G-NUM` requires it `<= 1e-6`, four orders below `tau_inv`. (b) `X8` and
`X9` are EXACT invariants by construction and MUST pass `G-INV`. **If `X8` fails
`G-INV`, the gate is INSTRUMENT-LIMITED and NO REFUSAL OF ANY CANDIDATE MAY BE
REPORTED** — the run reports that as its result. (c) `X8` must also pass `G-Q`
(`|det B| = q^{d-k}` varies with `q` by construction), so the pair (`X7`, `X8`)
demonstrates that the two criteria discriminate in opposite directions before any
candidate is judged.

**Form 3 — the obstruction could not fail (the list is all one class).** If every
candidate is an `f(P)` observable then `OBS-GEN` makes their refusal a theorem,
and "no admissible predicate exists" would be a restatement of my own list.
*Guard:* `GEN-2` requires at least `2` non-`f(P)` candidates actually scored, and
class membership is decided by the collision probe rather than by my assertion.
If the non-`f(P)` candidates cannot be computed, the outcome is `R2'` — NOT
ESTABLISHED — and not `R2`.

**Form 4 — AM4-OBS-1 could not be refuted (it is inherited rather than tested).**
*Guard:* 2.4 fixes, in advance, two distinct events that refute it — a
collision-probe separation (its premise) and a `T1`-invariant carried observable
(its measured conclusion) — and `R4` reports either.

### 2.11 What Section A does not reach

It measures the behaviour of ten observables under three lattice-preserving
transforms, two sweeps and one collision probe, on explicitly constructed q-ary
bases and `Z^d`, at `d in {20,30,40,100,140}`, `q <= 3329`, `n = 8` bases. It
adjudicates NOTHING about which spill mechanism is correct, nothing about
reduction, nothing about the `2^-10` tail law, and nothing about ML-KEM. An
`R2` outcome is a statement about the observables tested and the question as
posed — not a theorem that no admissible statistic exists, and not a closure of
the M-K / M-D question, which remains where `DEC-20260806-607779` left it: NOT
DECIDED, and not decidable by `E_I`.

---

## 3. SECTION B — AM-6: the AM-3 positive control, rebuilt to present a REAL violation

Run by TASK-20260808-cece0c, on the AM-1 13-point `t` grid, which is RETAINED and
not re-litigated. The AM-3 criterion of BATCH-a44d08 prereg 3.2 is carried
UNCHANGED; only the positive control changes, as AM-6 requires.

### 3.1 What is being measured, and what is not on trial

**This section measures THE CONTROL'S POWER.** BATCH-a44d08's control could not
PASS: its argmax-`SE_diff` step rule selected the step whose lower endpoint had
the largest `SE_diff`, `SE_diff` is largest at the head of the descent where
`|Delta_i|` is `11x` to `26x` the injection unit, and the Validator's
recomputation found the post-injection `Delta` at `c = 6` STILL NEGATIVE in three
of four cells — so no monotonicity violation of any size was ever presented to
the gate, and a monotonicity gate declining to flag a net decrease is behaving
correctly **[quoted: validation_report.yaml item d; red_team_report.md section
2.3]**.

Three things are frozen here as binding statements of scope:

1. **AM-3 IS NOT ON TRIAL FOR ITS LIFE, AND IS NOT RETIRED.** Its `0.096`
   family-wise false-failure bound stands: correctly derived, declared before any
   datum, mechanically free of every run-supplied quantity, and confirmed by both
   reviews **[quoted]**. Its power is UNDEMONSTRATED, not disproved.
2. **A FINDING THAT THE GATE CAN FIRE DOES NOT REINSTATE BATCH-a44d08'S
   READINGS.** The frozen `INADMISSIBLE` verdict of BATCH-a44d08 stands as the
   output of its frozen rule on its frozen data and is NOT rescored here. The
   four `PARTIAL` cell readings stay WITHHELD and may not be lifted out.
3. **The Red Team's `c_min` table and bootstrap, and the Validator's
   post-injection `Delta` recomputation, are REVIEW MEASUREMENTS.** They are
   cited here only as the ground for AM-6 and as the prior for PRED-B1, exactly
   as AM-6's prohibition permits, and never as a rescoring **[carried: AM-6
   prohibition]**.

### 3.2 `c_min` and `c_pos` in closed form, derived here

Injecting `+ c * SE_diff(A, t_i)` into every draw at grid point `t_{i+1}` shifts
the paired difference at step `i` by a CONSTANT, so it shifts `Delta_i` by
`+ c * SE_diff(t_i)` and leaves `SE_step(i)`, `SE_diff(t_i)` and
`epsilon_i = 1.0 * SE_diff(t_i)` unchanged. Hence, with
`t_crit = 4.2071245566046755` `[carried]`:

```
stat_i(c) = ( Delta_i + (c - 1) * SE_diff(t_i) ) / SE_step(i)

c_min(i)  = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i)        [closed form]
            the smallest c at which step i is a VIOLATION

c_pos(i)  = max( 0 , - Delta_i / SE_diff(t_i) )                          [closed form]
            the smallest c at which the post-injection Delta is positive,
            i.e. at which a monotonicity violation EXISTS AT ALL
```

**The closed-form guarantee that makes this control valid.** At `c = c_min(i)`
the post-injection `Delta` equals `epsilon_i + t_crit * SE_step(i)`, which is
strictly positive whenever `SE_diff(t_i) > 0` and `SE_step(i) > 0`. Therefore

```
c_min(i)  >  c_pos(i)        strictly, at every step             [closed form]
```

so **every firing the AM-3 gate can produce sits on a genuinely positive
post-injection `Delta`**: the gate cannot be made to fire on a step that is still
decreasing. The BATCH-a44d08 defect was the converse and is repaired by removing
the selection, not by weakening the gate. The run verifies `c_min(i) > c_pos(i)`
numerically at all 48 steps; a violation is an implementation error, not a
finding.

Degenerate cases, frozen: if `SE_diff(t_i) = 0`, use `SE_diff(t_{i+1})`; if both
are `0`, or if `SE_step(i) = 0`, the step is flagged `DEGENERATE`, `c_min` and
`c_pos` are reported as `undefined` with the reason, and the step is excluded
from the counts with the exclusion printed. No division by zero is performed.

### 3.3 The step-selection rule: THERE IS NONE

**Every one of the 12 steps of every one of the 4 cells is reported.** No step is
selected, so no selection rule can maximise the quantity the injection is
denominated in — AM-6 clause (b) is satisfied by removing the object that carried
the defect rather than by replacing it. AM-6 clause (c) is satisfied by reporting
`c_min` in closed form, which is strictly stronger, cheaper and lottery-free
**[carried: AM-6]**.

Two SUMMARY statistics are reported beside the full table, both labelled:

* **S1, grid-position summary (data-independent):** the median and range of
  `c_min(i)` over the steps `i in {5,...,11}`, i.e. those with lower endpoint
  `t_i >= 0.015`. The selection uses only the position in the frozen `t` grid and
  no measured quantity whatsoever.
* **S2, near-flat summary (data-DEPENDENT, labelled as such):** the median and
  range of `c_min(i)` over the steps with `|Delta_i| <= 1.0 * SE_diff(t_i)`,
  which is the subset where AM-6 clause (a)'s identification "the injection
  creates a violation of exactly that size" is valid. This uses the data and is
  reported as descriptive, never as the frozen headline.

Cells: `d100_b30`, `d100_b40`, `d140_b30`, `d140_b40` `[carried]`.

### 3.4 Reported quantities — all 48 steps, nothing omitted

For every step `i = 0..11` of every cell, the report prints:

```
t_lo, t_hi, Delta_i, SE_step(i), SE_diff(t_i), epsilon_i,
c_pos(i), c_min(i), c_min(i)/4  (in units of the design's own 4.0*SE_diff gate width),
post-injection Delta at c in {0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32},
fires(c) for the same c grid,
flag: Delta_i > 0 in the raw data (yes/no), DEGENERATE (yes/no)
```

The post-injection `Delta` is printed at every `c` of the grid, at every step, as
the task card requires, so a reader can check on the page that every reported
firing sits on a real violation.

**Power curve, frozen:** `n_fire(cell, c) = #{ i : c_min(i) <= c }` for
`c in {1, 2, 3, 4, 6, 8, 12, 16, 24, 32}`, per cell and pooled over the 48.

### 3.5 The prediction, its threshold, its falsifier, and the detection floor

> ### **PRED-B1 (frozen): `n_fire(cell, c=6) >= 4` in EVERY one of the four cells.**
> Threshold unit: a COUNT OF STEPS out of 12. Falsifier: any cell with
> `n_fire(c=6) <= 3`.

Provenance of the number, stated so it cannot be mistaken for a carried result:
the Red Team's review measurement reports the identical injection firing at
`c <= 6` at `6, 7, 9, 7` of the 12 steps in the four cells **[quoted:
red_team_report.md section 2.2]**. That is a REVIEW MEASUREMENT which AM-6
forbids citing as a rescoring; it is used here only to set a prior, and `4` is
chosen strictly below all four quoted values so that the prediction is a genuine
two-sided claim about THIS run's own recomputation rather than a restatement of
the quoted numbers.

**Secondary frozen statement (not a prediction, a definition of what is
reported):** whether the AM-3 gate CAN fire is answered by
`n_fire(pooled, c=6) > 0` and is stated PLAINLY and SEPARATELY from whether it
DID fire in BATCH-a44d08, in those words, in the report's headline paragraph.

**Detection floor.** `c_min` is a deterministic function of the recorded
per-draw values, so the floor is a REPRODUCTION floor and not a sampling floor:

* The graded family and the Haar null are regenerated from the carried seeds
  (`seed_graded`, `seed_haar`, `seed_error`) with **NO NEW BKZ, no LLL, no
  reduction of any kind** — the arms are pure `numpy` and the seeds are the cache
  `[carried]`. The run reports `max |r_regenerated - r_committed|` against the
  committed `results_g3.json` over all 448 values.
* Expected non-zero deviation, declared in advance: BATCH-a44d08 measured
  `2.220446049250313e-16`, confined to `d = 140`, uniform at one ULP, and traced
  to a one-ULP difference in the deterministic reference divisor
  `betaincinv(beta/2, (d-beta)/2, 2^-10)` under `scipy 1.15.3` **[quoted:
  `EV-MLKEM-cd9878` seed_integrity]**. **It must NOT be rounded to `0.0`.**
* **Admissibility threshold: `max |dev| <= 1e-9` on `r`, AND
  `max |c_min(regenerated) - c_min(committed)| <= 0.01` in `c` units** (i.e. one
  hundredth of one `SE_diff`). If either is exceeded, the arm is
  INSTRUMENT-LIMITED, that is reported as the result, and no power statement is
  made.

### 3.6 Negative controls, mandatory

* **NC-B1, `c = 0`:** the un-injected family must return `0` violations of 48,
  reproducing the committed `AM3-TIE` in all four cells with max statistic
  `-0.19342160540508713` **[quoted: validation_report.yaml MR-B1]**. A gate that
  fires without an injection is broken.
* **NC-B2, `c = -6`:** a NEGATIVE injection (making every selected step more
  strongly decreasing) must return `0` violations of 48. A gate that fires on a
  reinforced decrease is broken.
* **NC-B3, `Delta_i > 0` steps flagged:** BATCH-a44d08 recorded `9` of `48` steps
  with `Delta_i > 0` in the raw data **[quoted: validation_report.yaml MR-B1]**.
  At such a step a small `c` fires partly on a pre-existing increase rather than
  on the injection. Every such step is FLAGGED in the table and `n_fire` is
  additionally reported with those steps excluded, both numbers printed.

Any of NC-B1 or NC-B2 failing makes the run INSTRUMENT-LIMITED and no power
statement is made from it.

### 3.7 Uncertainty on `c_min` — quantification, not selection

`Delta_i`, `SE_step(i)` and `SE_diff(t_i)` are each estimated from `8` draws, so
`c_min(i)` carries sampling uncertainty. The run reports a bootstrap
distribution: resample the `8` draw indices JOINTLY across every `t` and the Haar
null, `B = 20000`, `default_rng([9, d, beta, 0])`, and report per step the
fraction of replicates with `c_min(i) <= 6` and the `2.5 / 50 / 97.5` percentiles
of `c_min(i)`.

This is UNCERTAINTY QUANTIFICATION on a reported quantity. It is **not** a
selection rule and no verdict is taken from it — that distinction is exactly what
BATCH-a44d08's argmax lottery got wrong, and repeating the bootstrap while
keeping a selection would repeat it. The frozen headline (PRED-B1) is scored on
the point estimates of the full 48-step table.

### 3.8 The arrangement in which Section B could not fail — in BOTH directions

**Form 1 — the control could not FAIL (weakness is invisible).** Reporting
`c_min` with an unbounded `c` axis makes "the gate fires at SOME `c`" true at
every non-degenerate step by construction, since `c_min(i)` is finite whenever
`SE_diff(t_i) > 0`. A headline of that shape is vacuous.
*Guard:* the frozen headline is not "does it fire at some `c`" but PRED-B1, a
count against a fixed threshold at a fixed `c = 6`, plus `c_min(i)/4` reported in
units of the design's own `4.0 * SE_diff` gate width so a reader can see directly
whether the firing amplitude is inside or outside the range the design calls
detectable. A cell where every `c_min` exceeds `6` falsifies PRED-B1 and is
reported as such.

**Form 2 — the control could not PASS (no violation is ever presented).** This is
the arrangement BATCH-a44d08 ran in, and the mirror its pre-registration failed
to name.
*Guards, three:* (a) `c_pos(i)` is computed and printed at every step, so the
step's own reality threshold is on the page beside its firing threshold;
(b) the closed-form relation `c_min(i) > c_pos(i)` (3.2) is verified numerically
at all 48 steps, so every firing provably sits on a positive post-injection
`Delta`; (c) there is NO step selection at all, so no rule can place the control
where the injection cannot create the condition.

**Form 3 — the control could pass trivially (the step was already increasing).**
At a step with `Delta_i > 0` the gate can fire on the pre-existing increase
rather than on the injection.
*Guard:* NC-B3 flags every such step and reports `n_fire` both with and without
them; PRED-B1 is scored on the full table with the flagged count printed beside
it.

**Form 4 — the reproduction could hide a defect.** If the regenerated family
silently differs from the committed one, `c_min` is computed on a different
object than the one BATCH-a44d08 scored.
*Guard:* 3.5's reproduction floor, with the expected one-ULP `d = 140` deviation
declared in advance and explicitly forbidden from being rounded to `0.0`.

### 3.9 What Section B does not reach

It characterizes the POWER of one positive control on one recorded graded family
at four cells, `n = 8` draws, `N = 2^20`. It licenses nothing about lattices in
either direction; `INADMISSIBLE`, `INVALID` and `PARTIAL` are INSTRUMENT
outcomes `[carried]`. It does not rescore BATCH-a44d08, does not reinstate any
withheld reading, does not retire AM-3, and does not establish that the AM-3 gate
is adequate — a demonstration that a gate CAN fire at an injected violation is
not a demonstration that it fires at a real one. Every "0 violations" remains an
upper bound at the declared floor, never an absence.

---

## 4. SECTION C — AM-7: the matched-`V` comparison rebuilt with an SE that contains the variance it omitted

Run by TASK-20260808-3a5f18. AM-5 named the matched-`V` cross-family comparison
as F-A1's replacement; AM-7 BLOCKS it until three conditions hold. This section
freezes all three.

### 4.1 The proposition, and that it stays OPEN IN BOTH DIRECTIONS

The proposition is L2's mechanism content stripped of its magnitude map:
**`D` depends on the frame only through `V`, at the `2^-10` quantile.**

**BATCH-a44d08's Section C verdict is VOID IN BOTH DIRECTIONS.** It may not be
cited, reproduced as a baseline, or used as a prior. "L2 tail sufficiency
falsified" is not a result of this program; neither is "consistent"; and the
eight non-firing pairs' detection floors (`6.29%` to `17.23%`) are not upper
bounds, because they are computed from the invalid SE **[carried: AM-7
consequence_for_the_record; `EV-MLKEM-cd9878` section_C reading]**. This section
REBUILDS THE INSTRUMENT. It does not re-score that output and does not begin from
it.

The boundary is carried so that no verdict here overreaches:
`Var(e^T P e) = 2 beta + (mu_4 - 3)(V + beta^2/d)` IS a function of `V` alone, so
L2's derivation is correct AT SECOND ORDER and nothing here touches it
`[carried: prereg 4.1]`. What is open is only whether the `2^-10` tail quantile
inherits that. A falsification below refutes the TAIL-LEVEL claim and not the
variance-level derivation, and the report must say so in those words.

### 4.2 The two families, with INDEPENDENT support draws

* **GR — the graded family**, `Q_t = QR(sqrt(1-t) E_S + sqrt(t) G)`, seeds
  `seed_graded(d,beta,j)`, `j = 0..7`, on the AM-1 13-point grid `[carried]`.
* **TL — the two-level family.** A rank-`beta` projector supported on `2 beta`
  coordinates with `P_aa in {u, 1-u}`, `beta` coordinates of each, built as
  `beta` mutually orthogonal rank-1 projectors on disjoint coordinate PAIRS.
  Closed form `[carried]`, with `m = beta/d`:

```
V_TL(u)  = beta[ (u-m)^2 + (1-u-m)^2 ] + (d - 2 beta) m^2       increasing on [1/2, 1]
m3_TL(u) = beta[ (u-m)^3 + (1-u-m)^3 ] + (d - 2 beta) (-m)^3
inverse  : u = 1/2 + sqrt( S/2 - (1/2 - m)^2 ),  S = ( V - (d-2beta) m^2 ) / beta
```

**THE REPAIR, stated exactly.** The superseded `vmatch.py`'s `tl_frame` was
DETERMINISTIC on ONE fixed coordinate support — the pairs `(a, a+beta)` — so all
8 TL draws shared it, the TL arm carried no independent randomness of its own,
and the frozen `SE` omitted the between-support variance entirely **[quoted:
red_team_report.md section 3.2; measured there at `2.54x` and `3.20x` the pairs'
ENTIRE reported SE]**. Replaced by independent support draws, frozen here:

```
for TL support index s = 0..7:
    rng  = numpy.random.default_rng([5, d, beta, s])          (null: TAG 6)
    perm = rng.permutation(d)
    support = perm[0 : 2*beta]
    pairs   = [ (support[2m], support[2m+1]) for m = 0 .. beta-1 ]
    P_s     = sum over pairs of the 2x2 rank-1 projector with diagonal (u, 1-u)
              and off-diagonal +sqrt(u(1-u))
```

Both the SUPPORT and the PAIRING are drawn afresh at every `s`. **`V_TL` and
`m3_TL` depend on `u` alone and not on the support or the pairing** — they are
sums over coordinates of functions of the diagonal, and the diagonal's multiset
is fixed by `u` **[closed form]** — so independent supports do NOT break the
`V`-matching. That is why this repair is available at zero cost to the design.

**`V`-matching, frozen `[carried]`:** `|V_TL - V_GR| <= 1e-9` absolute, achieved
by the closed-form inverse in **float64 throughout** (the frozen `1e-9` is
unattainable at the committed float32 frame precision; BATCH-a44d08 reported both
conventions and the Validator bounded the consequence at `|dD| <= 8.2e-09`
**[quoted]**). `u_j` is solved per GR draw `j` and TL support `s = j` is matched
to it. The ACHIEVED `|V_TL - V_GR|` and `|m3` separation`|` are reported for
every pair, scored or not.

### 4.3 The SE — three variance sources, the decomposition reported

For family `F in {GR, TL}`, support/draw index `j = 1..S`, error pool
`p = 1..E`:

```
D_{F,j,p} = q_emp,F,j,p(2^-10) / q_Beta(2^-10) - 1
Delta_{j,p} = D_{GR,j,p} - D_{TL,j,p}                    (index-matched pairing)
Delta_bar   = mean over the S x E table
```

`S = 8` supports/draws `[carried n = 8]`; **`E = 4` INDEPENDENT ERROR POOLS per
cell**, exceeding AM-7's minimum of `3`: pool `p = 0` is the carried
`seed_error(d)` (so the GR side reproduces the committed record), pools
`p = 1,2,3` are `default_rng([7, d, p])`, each `N = 2^20` `CBD_{eta=2}` vectors.
`D_bar` is therefore a mean over `S x E = 32` order statistics drawn from `4`
independent pools — **`D` is no longer one order statistic of a single shared
pool**, which is the structural defect AM-7 names.

Two-way random-effects decomposition on the `S x E` table of `Delta_{j,p}`
(supports and pools crossed, no interaction term modelled):

```
MS_S  (between supports, df = S-1 = 7)     E[MS_S]  = sigma_e^2 + E * sigma_S^2
MS_P  (between pools,    df = E-1 = 3)     E[MS_P]  = sigma_e^2 + S * sigma_P^2
MS_res(residual,         df = 21)          E[MS_res]= sigma_e^2

Var(Delta_bar) = sigma_S^2/S + sigma_P^2/E + sigma_e^2/(S E)
SE^2(Delta_bar) = ( MS_S + MS_P - MS_res ) / (S * E)                      [closed form]

nu_eff = (MS_S + MS_P - MS_res)^2
         / [ MS_S^2/(S-1) + MS_P^2/(E-1) + MS_res^2/((S-1)(E-1)) ]        (Satterthwaite)
```

If `MS_S + MS_P - MS_res <= 0` the estimate is replaced by `MS_res/(S E)`, the
pair is FLAGGED `NEGATIVE-VARIANCE-COMPONENT`, and both the flagged status and
the raw mean squares are printed. `nu_eff` is computed per target and printed
with the critical value it produced; it is data-dependent by construction and
that is declared here, in advance.

**MANDATORY REPORTING:** for every pair, `sigma_S^2`, `sigma_P^2`, `sigma_e^2`,
their three contributions to `SE^2(Delta_bar)`, each as an absolute value and as
a percentage of the total, and `nu_eff`. AM-7 clause (1) is satisfied only if
this decomposition is on the page.

### 4.4 Targets, the criterion, the floor, and the verdicts

**Targets**, by the carried data-independent rule `[carried: prereg 4.3]`: per
cell, take the 13 graded grid points, drop any whose `V` is UNREACHABLE for TL,
drop any degenerate point (`|V - beta(1 - beta/d)| <= 1e-9`), order the survivors
by `t` ascending and take the FIRST and the THIRD; add the cell's unreduced
real-lattice arm as a third target where its committed `V` is TL-reachable.
Cells `(100,30), (100,40), (140,30), (140,40)` `[carried]`; reachable `V`
intervals `[6.000000, 21.000000]`, `[4.000000, 24.000000]`,
`[8.571429, 23.571429]`, `[8.571429, 28.571429]` **[closed form]**.

```
n_C declared = 8 graded + 3 unreduced = 11
  the (140,30) unreduced arm is UNREACHABLE by the frozen rule: committed V = 6.750435
  < V_TL(1/2) = 8.571429  [quoted: EV-MLKEM-94c773 ; re-derived closed form here]
n_C = 8 if fpylll is unavailable (declared now, with its own level, so nothing is selected after the fact)
alpha_pair = 0.10 / 11 = 0.0090909090909...   (family-wise 0.10, Bonferroni)   [closed form]
|t| crit   = t.ppf(1 - alpha_pair/2, nu_eff)  computed per target at its own nu_eff
             reference values: nu=7 -> 3.5704944643 ; nu=10 -> 3.2254414968 ;
                               nu=21 -> 2.8736397407 ; nu=31 -> 2.7829734812   [closed form]
```

The realized `n_C` is recomputed by the frozen rule and BOTH the declared and
realized counts and levels are reported `[carried]`.

A matched-`V` pair is a **FALSIFYING PAIR** iff BOTH hold:

```
(i)  | Delta_bar | / SE(Delta_bar)                          >  |t| crit at nu_eff
(ii) | Delta_bar | / max( |D_bar_GR| , |D_bar_TL| )          >  tau_rel = 0.15
```

> ### **THE RELATIVE-EFFECT FLOOR IS `tau_rel = 0.15`, SET ABOVE THE NULL'S OWN MEDIAN.**
> BATCH-a44d08's frozen `5%` bar did no work: two independent reviewers, using
> two different null constructions, measured the NULL's own MEDIAN relative
> difference at `8.4%` and `9.0%` **[quoted: red_team_report.md section 3.3 N2;
> `EV-MLKEM-cd9878` OBS-C2]**. `0.15` is `1.67x` the top of that measured range —
> the smallest round multiple that puts the floor clearly above the null's central
> tendency rather than at its edge. The cost is power, and it is declared: a real
> effect below `15%` relative will be reported as UNDERPOWERED, never as absent
> and never as CONSISTENT. The two void BATCH-a44d08 relative differences are NOT
> used to set this floor and are not a target effect size.

**Detection floor per pair, reported always:**
`floor = |t|crit(nu_eff) * SE(Delta_bar) / max(|D_bar_GR|, |D_bar_TL|)`, in
percent relative.

**Verdicts:**

* **L2 TAIL-SUFFICIENCY FALSIFIED AT THE `2^-10` QUANTILE** — at least one
  FALSIFYING PAIR, and the calibration gate of 4.6 PASSED. Refutes the tail-level
  claim only, explicitly not the second-order derivation (4.1).
* **CONSISTENT** — no FALSIFYING PAIR, the calibration gate PASSED, and at least
  one INFORMATIVE pair has `floor < tau_rel`.
* **UNDERPOWERED — UPPER BOUND** — no FALSIFYING PAIR and `floor >= tau_rel` for
  every pair. Reported as "any difference is bounded above by `<number>` percent
  relative at `S = 8`, `E = 4`, `N = 2^20`", **never** as CONSISTENT and never as
  absence. **If the rebuilt instrument still cannot separate, THAT IS THE
  RESULT.**
* **WITHHELD — INSTRUMENT UNCALIBRATED** — the calibration gate of 4.6 FAILED.
  No verdict on the proposition is stated in either direction; the batch's Section
  C result is the estimated false-falsification rate with its interval, and the
  proposition stays open exactly as it is now.
* A pair with `|t|` in `[0.8 |t|crit, |t|crit)` and relative difference above
  `tau_rel` is recorded as **SUGGESTIVE, NOT FALSIFYING**, with its exact values,
  so a near miss is on the record rather than discarded.

`m3` informativeness is carried: a pair is INFORMATIVE iff
`|m3_GR - m3_TL| > 0.1 * max(|m3_GR|, |m3_TL|)`; non-informative pairs are
reported with their values and excluded from `n_C` BEFORE the critical value is
fixed `[carried: prereg 4.5]`.

### 4.5 The null calibration — three nulls, replicated to ESTIMATE a rate

AM-7 clause (2) requires a rate ESTIMATED from a replicated null, not bounded
analytically. Three null objects, all scored through the IDENTICAL code path and
the IDENTICAL criterion (4.4), including the same `tau_rel` and the same SE
construction:

* **N-A — TL versus TL'' at identical `u`, independent supports.** Two TL
  families whose supports and pairings are drawn independently
  (`TAG 5` and `TAG 6`) at the SAME `u_j`. `V` and `m3` are identical by
  construction; the `CBD` law is i.i.d. across coordinates, so the two are equal
  in distribution and the TRUE EFFECT IS EXACTLY ZERO. Every firing is a FALSE
  FALSIFICATION. **Exactness check, mandatory:** `max |V - V''| <= 1e-12` and
  `max |m3 - m3''| <= 1e-12` over every null pair, printed; if exceeded, the null
  is not exact, the calibration is reported as INVALID, and no rate is claimed.
* **N-B — GR versus `pi(GR)`.** The same graded frame with its ambient
  coordinates permuted by a random permutation (`default_rng([10, d, beta, r])`).
  A coordinate permutation preserves `V` and `m3` EXACTLY, and the i.i.d. `CBD`
  law is exchangeable, so this too is an exact null — and it mirrors the GR side
  of the real comparison, where N-A mirrors the TL side. Two nulls of different
  construction, as BATCH-a44d08's two reviewers independently demonstrated is
  necessary **[quoted: `EV-MLKEM-cd9878` OBS-C2]**.
* **N-C — the GAUSSIAN control (secondary, and an exact instrument check).**
  Replace `CBD` with i.i.d. `N(0,1)` errors (`default_rng([8, d, p])`). For
  Gaussian `e`, `R = ||Q^T e||^2/||e||^2 ~ Beta(beta/2, (d-beta)/2)` EXACTLY for
  every orthonormal frame **[closed form]**, so `E[D]` is frame-independent and
  `Delta_bar` has expectation `0` for ANY pair of frames. Any firing is a false
  falsification arising purely from the shared-pool structure. If N-C fires at a
  rate materially above N-A and N-B, the defect is in the pool sharing rather
  than in the frame families, and the report says so.

**Replication, and how the rate is estimated with its uncertainty:**

```
cells for the null: (100,40) and (140,40)   -- the two cells BATCH-a44d08's nulls were built in,
                                               so the comparison is like-for-like
R_target = 300 replicates per cell per null (N-A, N-B) ; 60 per cell for N-C (secondary)
R_min    = 200 per cell   -- below this the calibration gate is UNDECIDED (4.6)
pool bank: 20 pools per cell, generated on demand from default_rng([7, d, p]), p = 0..19;
           replicate r uses the quadruple { (4r) mod 20, ..., (4r+3) mod 20 },
           so the R replicates fall into 5 DISJOINT pool-quadruple CLUSTERS
```

Reported for each null and each cell:

* the raw count `x` of FALSIFYING pairs out of `R`, and the point estimate `x/R`;
* the **Wilson 95% interval** on `x/R`, and its UPPER bound explicitly;
* the per-cluster rates over the `5` pool quadruples, their dispersion, and a
  **cluster bootstrap 95% interval** resampling the `5` clusters — because
  replicates sharing a pool quadruple are NOT independent, so the Wilson interval
  is a LOWER bound on the true uncertainty and is labelled as such;
* the median and the `95th` percentile of the null `|t|`, and the median null
  relative difference, so the two quantities BATCH-a44d08's nulls reported
  (`median |t| ~ 11`, `median relative 8.4-9.0%`) have direct successors.

### 4.6 The calibration gate — `G-CAL`, and its reachability computed in advance

> ### **G-CAL: the rebuilt falsifier is CALIBRATED iff, for BOTH N-A and N-B, in BOTH null cells, the WILSON 95% UPPER BOUND of the estimated per-pair false-falsification rate is `<= 0.040`.**

Derivation of `0.040`: `4 x` the per-pair nominal level at the declared
`n_C = 11` (`4 x 0.00909091 = 0.03636`), rounded UP to `0.040` for exactly one
reason, which is reachability, computed here **[closed form]**:

```
Wilson 95% upper bound, x false falsifications of R:

  R = 100 :  x=0 -> 0.03699   x=1 -> 0.05449   x=2 -> 0.07001
  R = 200 :  x=0 -> 0.01885   x=1 -> 0.02777   x=2 -> 0.03572   x=3 -> 0.04317
  R = 300 :  x=0 -> 0.01264   x=2 -> 0.02398   x=4 -> 0.03378   x=5 -> 0.03842   x=6 -> 0.04294
```

**Both directions, before any datum exists:**

* The gate **CAN PASS**: at `R = 200` it passes with up to `2` false
  falsifications, at `R = 300` with up to `5`. It does not demand a perfect null.
* The gate **CAN FAIL**: at `R = 200` it refuses at `3` of `200` (rate `0.015`),
  at `R = 300` at `6` of `300` (rate `0.020`).
* It would have REFUSED the superseded instrument by one to two orders: the two
  independently built BATCH-a44d08 nulls fired at `0.246-0.85` per pair
  **[quoted]**.
* `R_min = 200` is a HARD FLOOR and this is why: at `R = 100` even a PERFECT null
  (`0` of `100`) has Wilson upper `0.03699`, clearing `0.040` by `0.003` with no
  room to refuse anything; and against the arithmetically natural `2x` gate
  (`0.0182`) a perfect null at `R = 100` would FAIL, making PASS unreachable
  outright. **That is the could-not-PASS arrangement for this section, and the
  declared `R_min` and `G-CAL` are chosen to exclude it.**

If the realized `R < 200` in either null cell, the gate is **UNDECIDED**, the
Section C verdict is **WITHHELD**, and the run reports the realized `R` with its
interval. `UNDECIDED` is an instrument outcome, never evidence about the
proposition.

### 4.7 The positive control — `delta_min` in closed form at EVERY target

The mirror of AM-6's requirement, applied to Section C: the control must present
a REAL effect, and its size must be reported at every target rather than at one
selected one.

Inject a constant additive offset into every TL value at a target,
`a = sign(Delta_bar) * delta * M` with `M = max(|D_bar_GR|, |D_bar_TL|)`. A
constant shift of a paired difference leaves `SE(Delta_bar)`, all three variance
components and `nu_eff` UNCHANGED, and moves `|Delta_bar|` to
`|Delta_bar| + delta M` **[closed form]**. Hence

```
delta_min = max(  ( |t|crit(nu_eff) * SE(Delta_bar) - |Delta_bar| ) / M ,
                  tau_rel - |Delta_bar| / M  ,  0 )                        [closed form]
          = max( detection floor , tau_rel ) - ( realized relative difference ) , floored at 0
```

`delta_min` is reported AT EVERY TARGET, in relative units, with both terms of
the maximum printed separately, and with the post-injection relative difference
printed so a reader can verify on the page that the injection creates an effect
above the floor by construction. The frozen power grid is
`delta in {0.05, 0.10, 0.15, 0.20, 0.30, 0.50}` and `fires(delta)` is tabulated.

> **Frozen admissibility clause.** If the criterion does not fire at
> `delta = 0.50` — a `50%` relative offset, more than `3x` the `tau_rel` floor —
> at EVERY target, the rebuilt instrument is declared **UNDERPOWERED BY
> CONSTRUCTION**, the Section C verdict is WITHHELD, and the run reports that as
> its result.

Note the two clauses of this section's gate point in opposite directions by
construction: `G-CAL` refuses an instrument that fires too easily, and the
`delta = 0.50` clause refuses one that cannot fire at all. Neither can be
satisfied by making the SE larger or smaller.

### 4.8 Pre-registered predictions that could fail

* **PRED-C1.** With the rebuilt SE, both N-A and N-B satisfy `G-CAL` in both
  cells. Falsifier: any Wilson upper bound above `0.040`. If it fails, the
  rebuilt instrument is STILL uncalibrated, that is the section's result, and the
  proposition stays open in both directions.
* **PRED-C2 (the AM-7 diagnosis, tested rather than assumed).** The between-
  support and between-pool components together contribute `>= 50%` of
  `SE^2(Delta_bar)` at a majority of targets. Ground: the omitted between-support
  sd was measured at `2.54x` and `3.20x` the ENTIRE superseded SE **[quoted]**.
  Falsifier: those components contributing `< 50%` at a majority of targets,
  which would mean the diagnosis behind AM-7 does not reproduce in the rebuilt
  design — recorded plainly if it happens.
* **PRED-C3 (instrument check, exact).** Under N-C's Gaussian errors, the paired
  `|Delta_bar|` collapses to the sampling floor: `0` FALSIFYING pairs of `60` per
  cell. Falsifier: any firing. A firing here is an implementation error or a
  pool-sharing artifact, not a finding about `V`.
* **NO PREDICTION IS MADE ABOUT THE PROPOSITION ITSELF.** Whether `D` depends on
  the frame only through `V` at the `2^-10` quantile is OPEN, and this document
  declares no expected direction for it.

### 4.9 Budget ladder, declared now

Budget `5400 s`, `4 GB`, `maximum_runs = 1`. Cost is MODELED from one measured
anchor — BATCH-a44d08's Section C used `16.80 s` of `5400` for about `160`
`D`-evaluations at `N = 2^20`, i.e. of order `0.1 s` per evaluation on a shared
host at load `180-660` **[quoted: `EV-MLKEM-cd9878` infrastructure_note]**. A
null replicate is `2 x S x E = 64` evaluations. These are MODELED numbers; the
ladder is keyed to WALL-CLOCK CHECKPOINTS.

1. Reproduction check of the GR side and the unreduced arm against the committed
   record, `max |dev|` reported (expected `2.220446049250313e-16`, NOT rounded to
   `0.0` **[quoted]**). Then the main comparison at all targets, and the
   `delta_min` table. Checkpoint `t1`.
2. N-A, cell `(100,40)`, in 5 clusters of 60. Then N-A, cell `(140,40)`.
3. N-B, same two cells, same structure.
4. N-C, `60` replicates per cell.
5. **Ladder:** at the end of every cluster, if elapsed `> 4200 s`, stop the
   current null at the completed clusters and report the realized `R` with its
   widened interval. If a null cell would finish below `R_min = 200`, that null
   cell is reported UNDECIDED (4.6). Priority order if the budget binds: N-A both
   cells first, then N-B, then N-C — declared now so nothing is chosen after the
   fact.
6. Memory: pools are evaluated in chunks of `2^16` rows, `CBD` samples stored as
   `int8`, at most one quadruple resident; target peak RSS well below `4 GB`.
   `gmpy2` is ABSENT and nothing here depends on it.

### 4.10 The arrangement in which Section C could not fail — in BOTH directions

**Form 1 — the falsifier could not FIRE.** An SE inflated by adding variance
components, plus a floor raised to `15%`, can make firing impossible; then
"CONSISTENT" is a property of the instrument. This is the mirror of
BATCH-a44d08's defect and is the direction a repair naturally overshoots into.
*Guards:* (a) the `delta_min` positive control at EVERY target with the frozen
`delta = 0.50` admissibility clause (4.7); (b) UNDERPOWERED is a MANDATORY
verdict and may never be rounded into CONSISTENT; (c) the detection floor is
printed for every pair; (d) the SE decomposition is printed, so an SE dominated
by a component that should not be there is visible on the page.

**Form 2 — the falsifier could not PASS ITS CALIBRATION.** If `G-CAL` is
unreachable at the declared replication, "still uncalibrated" is a property of
this document. *Guard:* 4.6 computes the reachability in closed form before any
datum — the gate passes at up to `2` of `200` and `5` of `300`, and refuses at
`3` of `200` and `6` of `300` — and `R_min = 200` is declared precisely to
exclude the `R = 100` arrangement in which a perfect null barely clears.

**Form 3 — the null could be built QUIET.** A null constructed at a `u`, a cell
or a support distribution where the statistic happens not to fire makes "well
calibrated" a property of my choice. The Red Team named this risk against its own
null **[quoted: red_team_report.md section 5]**.
*Guards:* (a) TWO nulls of DIFFERENT construction (N-A on the TL side, N-B on the
GR side) plus a third of a different kind entirely (N-C on the error law), with
all rates reported and any disagreement between them reported rather than
resolved by choosing one; (b) both nulls run in the two cells whose supports and
`u` values the real targets occupy; (c) the exactness checks
(`|V - V''| <= 1e-12`, `|m3 - m3''| <= 1e-12`, and the coordinate-permutation
identity for N-B) are mandatory and printed, so a "null" that is not a null is
caught rather than credited.

**Form 4 — the pairing could force agreement.** Matching at the degenerate
`V = beta(1 - beta/d)`, where both families are the same coordinate projector up
to a permutation and equality is forced by identity `[carried: prereg 4.6 Form
2]`. *Guard:* the degenerate point is excluded BY RULE at `1e-9` before any data,
and is additionally reported as an INSTRUMENT CHECK whose agreement is never
counted as support for anything.

**Form 5 — a decoy second family.** A TL family whose `m3` tracks GR's, so equal
`V` implies equal everything `[carried: prereg 4.6 Form 3]`. *Guard:* the carried
informativeness rule requires a declared `10%` separation in `m3` for a pair to
enter the family at all, and `m3` is printed for every frame.

### 4.11 What Section C does not reach

It compares two synthetic frame families, plus up to three unreduced
real-lattice frames, at `d <= 140`, `beta <= 40`, `S = 8` supports, `E = 4`
pools, `N = 2^20`, at the `2^-10` quantile only, with no reduction beyond what
the committed unreduced arms already carry. It tests the tail-level sufficiency
of `V` and nothing else: not the variance-level identity, which is established
and untouched; not any reduced arm; not any lattice invariant — none of these
observables satisfies AM-4 and none is offered as an adjudicator of a claim about
a lattice (Section 2 is where that question lives). Both of BATCH-a44d08's
firing pairs were synthetic-versus-synthetic and none of its real-lattice pairs
fired **[quoted]**; whether the proposition holds for LATTICE tail frames is
untouched in either direction by anything this section can produce at this
replication.

---

## 5. What the three measurements may not do

1. No status change, no hypothesis movement, no evidence record. Each is an
   executor artifact of observations. No section may declare a hypothesis
   supported, rejected or closed, or a heuristic validated or refuted.
2. **Claim tier TOY, unconditionally.** No number measured here is transported to
   `beta = 606`, `d = 1420`, to any FIPS 203 parameter set, to any attack cost, or
   to any other parameter set, by extrapolation or by analogy.
3. No interpretation beyond the declared outcomes of 2.7, 3.5 and 4.4.
4. No "absent", "no departure", "vanishes", "consistent with zero" or any synonym
   applied to a measured arm, in any wording, without its floor. Frozen
   completion-gate item; the scan covers the report, the JSON and the script.
5. No editing of this document, no re-derivation of its thresholds, no
   substitution of a "better" grid, and no reaching for a rule this document does
   not contain. **If a measurement believes a threshold here is wrong, it records
   the objection in its report and RUNS THE FROZEN SPECIFICATION ANYWAY** — which
   is what all three BATCH-a44d08 producers did, correctly, and every defect they
   named was the defect a reviewer then demonstrated **[quoted:
   `EV-MLKEM-cd9878` OBS-P1]**.
6. No post-hoc alternative rule computed and presented beside a frozen verdict.
   If one is computed for forward guidance it is labelled POST-HOC and stated to
   be uncitable as a result.
7. Budget exhaustion, timeout, crash, or a missing dependency is **never**
   negative mathematical evidence (`AGENTS.md` rule 3). It is reported as
   INFRASTRUCTURE and the affected arm is reported as not measured. In Section A
   specifically, a budget cap is never a refusal of a candidate and never an
   obstruction.
8. **No AM-4 adjudicator claim outside Section 2's own gate.** Sections B and C
   operate on presentation-dependent observables and neither offers any verdict
   as an adjudication of a claim about a lattice.
9. **AM-3 is not retired; BATCH-a44d08's Section C verdict is void in both
   directions and is not cited, reproduced as a baseline, or used as a prior; the
   `E_I` arm is not re-frozen anywhere without the `q`-sweep and rank sweep of
   Section 2; `fpylll`'s `k` counts the `q`-scaled rows** (1.1, 1.3).
10. Independence in this batch is **procedural** — separate sessions, no shared
    scratch, snapshot before review — and never model-level. Every report records
    it that way, with `model_verified` and its reason. Rule 12 remains UNMET and
    UNWAIVED in this goal and is recorded, not smoothed.
11. Every run manifest carries the full `AGENTS.md` artifact policy fields
    INCLUDING an `inference` block and `model_verified` with its probe status —
    the gap recorded against BATCH-a44d08 (three manifests missing one or both)
    is not repeated **[quoted: validation_report.yaml AC-4 / F-6]**.
12. `certificate.kind: none` is stated explicitly in every manifest, with the
    reason (no solve, no factor-base relation is claimed or produced).

---

## 6. Provenance of every constant

| constant | value | class |
|---|---|---|
| `d` | `{100, 140}` primary; `{20, 30, 40}` for `X9`/`X10` only | [carried] / set here |
| `q` | `3329` | [carried] |
| error law / `mu_4` | `CBD_{eta=2}` / `2.5` | [carried] |
| draws per arm `n` = supports `S` | `8` | [carried] |
| errors per pool `N` | `2^20` | [carried] |
| tail level / estimator | `2^-10`, `sort(R)[1023]` | [carried] |
| gate factor | `4.0 * SE_diff` (nominal, not a p-value) | [carried] |
| AM-1 `t` grid | 13 values, 12 steps | [carried, RETAINED] |
| carried seed formulas | section 1 | [carried] |
| `E[V]_haar` | `2 beta (d-beta)/(d(d+2))` | [closed form, exact] |
| `t_{7,0.998}` | `4.2071245566046755`; `P(t_7>t_crit)=0.0019999999999982102` | [closed form] |
| **A**: transform triple `T1,T2,T3` + round trip `T0` | section 2.1 | [carried: AM-4] + `T0` set here |
| **A**: `q` ladder | `{1,2,4,16,64,256,1009,3329}` | set here; `q=1` required by AM-8 |
| **A**: rank ladder | `{1,5,10,20,k}` | set here; required by AM-8 |
| **A**: `tau_num` | `1e-6` | set here, four orders above the float64 QR path's noise, which `T0` measures |
| **A**: `tau_inv` | `0.01` | set here; one order below the `5%` practical floor and the `13.3%` row-permutation move **[quoted]** |
| **A**: `tau_q`, `tau_rel` | `0.10` | set here, one order above `tau_inv` |
| **A**: scales `s_X` | table in 2.2 | [closed form] except `s_D` = `0.01` (half the smallest committed `|D|`, `0.0189` **[quoted]**) |
| **A**: candidate list `X1..X10` | table in 2.3 | set here, frozen before any run |
| **A**: `OD + V + beta^2/d = beta` | identity for projectors | [closed form] |
| **A**: `OBS-GEN` | any `O(d)`-invariant `f(P)` is `f(d,beta)` | [closed form, elementary, to be verified numerically] |
| **A**: PRED-A1 targets `k/d`, `E[V]_haar` | exact Haar expectations | [closed form] |
| **A**: `1-E_I ~ q^-2` prior | `16.4x / 15.6x / 16.0x / 169x` | [quoted: red_team_report.md 1.1] |
| **B**: AM-3 criterion, `epsilon_i = 1.0*SE_diff(t_i)`, `t_crit` | unchanged | [carried: BATCH-a44d08 prereg 3.2] |
| **B**: `c_min(i) = 1 + (t_crit SE_step_i - Delta_i)/SE_diff(t_i)` | derived in 3.2 | [closed form] |
| **B**: `c_pos(i) = max(0, -Delta_i/SE_diff(t_i))`; `c_min > c_pos` | derived in 3.2 | [closed form] |
| **B**: `c` grid | `{0,1,2,3,4,6,8,12,16,24,32}` and `-6` for NC-B2 | set here |
| **B**: PRED-B1 threshold | `n_fire(c=6) >= 4` of 12, every cell | set here, strictly below the quoted `6/7/9/7` |
| **B**: quoted priors `6/7/9/7`, plateau medians `3.98/2.72/3.76/4.17`, `P(INADMISSIBLE)=0.997`, post-injection `Delta` at `c=6` | — | [quoted: red_team_report.md 2.2/2.3; validation_report.yaml item d] — REVIEW MEASUREMENTS, never a rescoring |
| **B**: reproduction floor | `max|dev| <= 1e-9` on `r`; `max|d c_min| <= 0.01` | set here; expected `2.220446049250313e-16` at `d=140` **[quoted]** |
| **B**: bootstrap | `B = 20000`, joint draw-index resample | set here, UQ only |
| **C**: `V_TL(u)`, `m3_TL(u)`, inverse, reachable intervals | section 4.2, 4.4 | [closed form] |
| **C**: independent TL support/pairing draws | `TAG 5` / `TAG 6` | set here — the AM-7 repair |
| **C**: `V`-match tolerance / degeneracy exclusion | `1e-9` | [carried] |
| **C**: `E` (error pools) | `4` per cell | set here, above AM-7's minimum of `3` |
| **C**: SE decomposition, `nu_eff` | two-way random effects + Satterthwaite | set here, satisfies AM-7 (1) |
| **C**: `n_C` | `11` declared (`8` graded + `3` unreduced); `8` without fpylll | [closed form from the carried rule] |
| **C**: `alpha_pair` | `0.10/11 = 0.00909090909...` | [closed form] |
| **C**: `|t|` crit reference at `nu = 7/10/21/31` | `3.5704944643 / 3.2254414968 / 2.8736397407 / 2.7829734812` | [closed form] |
| **C**: `tau_rel` | `0.15` | set here, `1.67x` the top of the measured null median `8.4-9.0%` **[quoted]** |
| **C**: `(140,30)` unreduced arm UNREACHABLE | `6.750435 < 8.571429` | [quoted] + [closed form] |
| **C**: nulls N-A, N-B, N-C | section 4.5 | set here; two constructions plus an exact-distribution check |
| **C**: `R_target` / `R_min` / clusters | `300` / `200` / `5` quadruples | set here, from the Wilson reachability table |
| **C**: `G-CAL` | `0.040` | set here `= 4 x alpha_pair` rounded up for reachability |
| **C**: Wilson upper bounds `0.03699 / 0.01885 / 0.02777 / 0.03572 / 0.04317 / 0.01264 / 0.03842 / 0.04294` | — | [closed form] |
| **C**: `delta_min` closed form and `delta = 0.50` admissibility clause | section 4.7 | [closed form] / set here |
| **C**: superseded null rates `0.246-0.85`, median null `|t| ~ 11`, between-support sd `2.54x`/`3.20x` | — | [quoted: red_team_report.md 3.3; validation_report.yaml CC-8/CC-9] — grounds for AM-7 only |

**Seed TAG table** for the tuple scheme
`numpy.random.default_rng([TAG, ...])`, fixed here:

| TAG | stream |
|---|---|
| 1 | Section A basis matrix `A` (and its rank-`r` factors) |
| 2 | ambient isometry `H` (`T1`) |
| 3 | row permutation (`T2`) |
| 4 | unimodular `U` (`T3`) |
| 5 | TL support and pairing draw (real arm) |
| 6 | TL'' support and pairing draw (null N-A) |
| 7 | error pool `p` (`CBD_{eta=2}`) |
| 8 | Gaussian control pool (null N-C) |
| 9 | bootstrap resample (Section B) |
| 10 | ambient coordinate permutation (null N-B) |

Nothing in this table depends on a measurement that does not yet exist. The only
quantities computed at run time are those declared as such: the residuals
`rho_T`, the `q` and rank ladders, the collision residuals, `Delta_i`,
`SE_step`, `SE_diff`, `c_min`, `c_pos`, the per-frame `E_I`, `V`, `m3`, `D`, the
variance components, `nu_eff`, the achieved `V`-match, the null counts, and the
per-pair floors.

---

## 7. Notarization

* `prereg_sha256.txt` in this directory contains the sha256 of this file and
  nothing else.
* TASK-20260808-e725b4 snapshot-commits this directory in **one** commit
  containing exactly these two artifacts and its own receipt, **before**
  TASK-20260808-2a9085, -cece0c or -3a5f18 is dispatched. No early durability
  commit is made for any producer, for any reason. The commit message contains
  the record id `GOAL-MLKEM-005` — BATCH-a44d08's first archive attempt was
  rejected by the dispatcher's post-commit verifier for omitting it **[quoted:
  task card]**.
* Each measurement re-hashes this file, compares against the notarized receipt,
  **aborts on mismatch**, quotes the digest in its report, and asserts
  `git merge-base --is-ancestor <notarizing commit> HEAD` against the notarizing
  commit ITSELF and not its parent.
* A mismatch is a harness failure, not a result, and the run does not proceed.
* Whether this ordering closes the notarization gap for this batch is for the
  Validator (TASK-20260808-768137) to judge against the git record, not for this
  document to assert. The residue it cannot close is off-repository
  pre-computation, and 0.1 is the declaration that answers it.

**Declaration, on the record: no lattice was generated or reduced, no basis was
built, no frame was computed, no draw was sampled, no error pool was created, and
no `E_I`, `V`, `m3`, `D`, `c_min`, invariance residual, null count or arm
statistic was evaluated in the production of this document. The only executed
code was closed-form design arithmetic in the design parameters alone.**
