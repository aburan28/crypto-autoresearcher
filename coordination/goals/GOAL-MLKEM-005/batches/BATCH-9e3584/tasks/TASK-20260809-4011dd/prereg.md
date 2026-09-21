# BATCH-9e3584 — FROZEN PRE-REGISTRATION

    goal        GOAL-MLKEM-005
    batch       BATCH-9e3584
    task        TASK-20260809-4011dd   (executor, PRE-REGISTRATION ONLY)
    written_at  2026-08-11
    claim_tier  TOY

**CLAIM TIER IS TOY AND STAYS TOY.** Nothing pre-registered in this document
bears on ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or
on any cost model. No number produced under this pre-registration may be
transported to `beta = 606`, `d = 1420`, or any other parameter set, by
extrapolation, by analogy, or by any other route.

**NO MEASUREMENT WAS PERFORMED IN WRITING THIS DOCUMENT.** No lattice was
built, no reduction was run, no draw was sampled, no arm statistic was computed,
and no candidate was scored. Section 0.4 lists exactly which closed-form algebra
was done in order to *state* the thresholds below, and exactly which committed
numbers were *read* (not recomputed) in order to state them.

---

## 0. Provenance, scope and the algebra done here

### 0.1 What governs this batch

    DEC-20260808-05b684        the decision that closed BATCH-cbe023 `revise`
                               and issued AM-10 .. AM-14
    EV-MLKEM-9b8f7f            the evidence record it rests on
    KN-FIND-f38a89             the ONLY citation route for AM4-OBS-1
    GOAL-MLKEM-005.yaml        the goal record; budget deliberately unbounded

AM-10 through AM-14 and their binding carries are **in force as written** and
are **not re-litigated** anywhere in this document.

### 0.2 The four sections, and their order

| § | section | what it is | gated |
| --- | --- | --- | --- |
| 2 | **R** | **THE LEAD.** `G-REL1`/`G-REL2` for `X8 = rdet`, `X9 = lam1n`, `X10 = hkz` over **all 8 frozen bases** at every mirrored pair; the parameter-determined null `X_null` scored through the **identical** gate and code path; `G-VAR` (AM-11) as a **refusal** criterion | — |
| 3 | **B'** | AM-13's **null family**: the 13 grid points rebuilt as 13 **independent** Haar frames from the carried seeds; `n_fire(c=6)` beside the real count and beside the Red Team's exact-null benchmark; the **decay check** | behind R |
| 4 | **C1** | AM-14 c,d: `tau_rel` re-derived from the **rebuilt null's own** distribution; the SUGGESTIVE band widened to `0.8*|t|crit` regardless of the relative floor; `SE_2way/SE_naive` at every target | behind R |
| 5 | **C2** | AM-14 b: a Section C positive control that **actually injects** and re-runs the **full** scoring path | behind R |

**Section R is the lead and the other three must not displace it.** The
dispatch queue gates §3, §4 and §5 behind §2 for exactly that reason. If the
budget binds, §3/§4/§5 are dropped and §2 is reported alone; §2 is never
dropped in favour of them.

### 0.3 Binding carries, restated so no successor has to reconstruct them

1. **ARTIFACT POLICY, NON-NEGOTIABLE FOR EVERY SECTION OF THIS BATCH.** Every
   run emits `command.txt`, `stdout.log` and `stderr.log` as **durable** files
   in its own task directory, and **no path is ever written into a folded YAML
   scalar**. BATCH-cbe023's Section C failed this (Validator F-5, Red Team
   RT-C7). It is an evidence-integrity gap and **never** a mathematical result.
   *This is hereby a required artifact of every section below.*
2. **AM-3 IS NOT RETIRED.** Its power is undemonstrated rather than disproved —
   now for a second time and by a second route — and its `0.096` family-wise
   false-failure bound stands, correctly derived and declared before any datum.
3. **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.** Its `INADMISSIBLE` verdict
   stands, its four `PARTIAL` cell readings stay **WITHHELD**, and its Section C
   verdict and detection floors remain **VOID IN BOTH DIRECTIONS**.
4. **NOT CITABLE FROM BATCH-cbe023 anywhere in this batch:** "the obstruction is
   relocated"; "**29 of 48**" unless its exact-null benchmark of **47 of 48**
   stands in the **same sentence**; and "**CONSISTENT**", in either direction.
5. **The `3.91%` detection floor may not be cited without the
   NEGATIVE-VARIANCE-COMPONENT qualifier in the same sentence.** The tightest
   non-degenerate floor is `10.83%`; the family-level bound over targets with a
   well-defined two-way SE is `~10.8%` relative.
6. **AM4-OBS-1 is cited ONLY through `knowledge/findings/KN-FIND-f38a89.md`.**
   Its premise is **REFUTED** for `D` (one probe, one run, two cells,
   single-source, the `L4` margin only `1.29x` its floor). Its surviving half is
   `OBS-GEN`: a derivation, **not** a machine-checked theorem and **not** an
   impossibility claim.
7. **fpylll's `k` counts the q-scaled rows, NOT the identity block (AM-9).**
   Throughout this batch `k = |K_I|` = the size of the **identity** block, and
   `k_fpylll = d - k`. Every basis is built **explicitly** as
   `B = [[I_k, A], [0, q I_{d-k}]]`; no fpylll basis generator is called. The
   convention is therefore fixed **structurally**, not by a label.
8. **An observable computed from the integer Gram matrix cannot be tested for
   ambient-isometry invariance**, since `G(BH) = B B^T` identically. A `0.0` T1
   residual there is **UNTESTED**, never "invariant".
9. **A q-sweep down to `q = 1` under `B = [[I_k,A],[0,q I_{d-k}]]` with `A`
   uniform on `[0,q)` compares a q-ary lattice against `Z^d`**, because `A = 0`
   and `B = I_d` at `q = 1`.
10. **The split-producer notarization pattern and the no-early-durability-commit
    rule are retained UNCHANGED.** They have now worked three times.
11. **`knowledge/INDEX.md` must NOT be written, regenerated or staged** by any
    task in this batch. It is a generated artifact, `.gitignore`d, and rebuilt
    on demand.
12. **Independence in this goal is PROCEDURAL AND NEVER MODEL-LEVEL**
    (AGENTS.md rule 12, **UNMET AND UNWAIVED**). Every manifest records
    `model_verified` and its reason. Procedural separation does not pass as
    independence.
13. **Never fabricate a measurement, timing, citation or run.** Missing data
    stays missing. A timeout, crash or missing dependency is **INFRASTRUCTURE
    SIGNAL** and is **never** negative mathematical evidence.

### 0.4 The algebra done here, and the committed numbers read here

Declared exhaustively, so a reviewer can separate "stating a threshold" from
"measuring something".

**Closed-form algebra performed (no data touched):**

* `t_crit(df = 7, two-sided 0.05) = 2.364624251592784` and
  `t_crit(df = 7, two-sided 0.01) = 3.4994832973504924`, from the Student-t
  quantile function. Used only to state §2's paired-test threshold and §2's
  detection floor.
* `log(3329) = 8.110427237575024`.
* The complete table of `X_null(B, beta) = (beta/d) * (1/d) * log|det B|` at
  every `(lattice, beta)` in §2's grid — **stated in advance in §2.6** — using
  `log|det B| = (d - k) * log q`, which is exact for
  `B = [[I_k, A],[0, q I_{d-k}]]`. This is parameter arithmetic and consumes no
  basis.
* `1.67 * 0.01496443 = 0.0249906...`, the §4 floor derivation.

**Committed numbers READ (quoted, not recomputed, not rescored):**

* The four rebuilt-null median relative differences quoted in AM-14(c) —
  `0.00645684`, `0.00976958`, `0.00768319`, `0.01496443` — read from
  `BATCH-cbe023/tasks/TASK-20260808-3a5f18/results_am7.json` keys
  `nulls[N-A__d100_b40 | N-A__d140_b40 | N-B__d100_b40 | N-B__d140_b40].median_relative_difference`.
  Used **only** to state §4's floor before any re-scoring, as AM-14(c) requires.
* The Red Team's L7/L8 replication figures quoted in §2.9, from
  `BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md`. **A review
  measurement, not a pre-registered result and not a baseline.**
* Section B's committed real count `29` of `48` at `c = 6` and the Red Team's
  exact-null benchmark `47` of `48`, used in §3 under carry 4 above.

Nothing else was read from any results file, and nothing at all was computed
from a basis, a frame, a draw or a reduction.

---

## 1. The frozen objects, carried unchanged

### 1.1 Bases

`B = [[I_k, A], [0, q I_{d-k}]]`, built **explicitly** in exact integer
arithmetic, never by a generator. `A = make_A(d, k, q, i)` from
`numpy.random.default_rng([1, d, k, i])`, `i = 0 .. 7`. `K_I` = coordinates
`0..k-1`; `K_q` = coordinates `k..d-1`. `q = 3329` throughout §2 unless a
`q`-ladder rung is named.

**THE 8 FROZEN BASES ARE `i = 0 .. 7`.** BATCH-cbe023 evaluated `G-REL` at
`i = 0` only. That is the defect this section exists to close.

### 1.2 Lattices and the mirrored pairs

    L1  (100, 30)   L2  (100, 70)      mirror pair, d = 100
    L4  (140, 40)   L5  (140,100)      mirror pair, d = 140
    L7  ( 20,  6)   L8  ( 20, 14)      mirror pair, d =  20
    L9  ( 30,  9)   L10 ( 30, 21)      mirror pair, d =  30
    L11 ( 40, 12)   L12 ( 40, 28)      mirror pair, d =  40

A **mirror** is `k -> d - k` at fixed `d`, `q` and `i`.

### 1.3 The beta grid, carried verbatim

    d = 100 :  15, 30, 35, 50, 65
    d = 140 :  20, 40, 45, 70, 95
    d =  20 :   5, 10, 15                 (d/4, d/2, 3d/4)
    d =  30 :   7, 15, 22
    d =  40 :  10, 20, 30

`REL-1` endpoints: `d = 100 -> (15, 65)`, `d = 140 -> (20, 95)`, and for the
small-`d` family the first and last point of its own grid. The small-`d`
`REL-1` endpoints were **not** pinned by BATCH-cbe023's prereg and were recorded
there as an interpretation; that interpretation is **carried unchanged here**
and re-declared as such so it is not silently promoted to a frozen clause.

### 1.4 The observables in play in §2

| id | name | definition | scale floor `s_X` |
| --- | --- | --- | --- |
| `X8` | `rdet` | `exp( log|det M| / d )` | `1.0` |
| `X9` | `lam1n` | `exp( 0.5*log(lambda_1^2) - logdet/d )` from the HKZ profile | `1.0` |
| `X10` | `hkz` | `mean_i>=d-beta( log ||b*_i|| ) - logdet/d` from the HKZ profile | `1.0` |
| `X_null` | `null` | `(beta/d) * (1/d) * log|det B|` — **the parameter-determined null (AM-11)** | `1.0` |
| `X_mp` | `rawtail` | `mean_i>=d-beta( log ||b*_i|| ) - logdet/d` from the **UNREDUCED** GSO of `B` — **the declared MUST-PASS candidate (AM-10 c)** | `1.0` |

`X_mp = rawtail` is `X10` computed on the **raw** basis instead of the
HKZ-reduced one: one QR, **no reduction of any kind**. It is introduced here as
an **instrument control**, not as a research candidate, and it is not proposed
as an admissible observable for any purpose in this goal.

**Why `X_mp` must pass `G-REL`, stated before it is scored.** For
`B = [[I_k, A],[0, q I_{d-k}]]` the raw Gram–Schmidt profile is sharply
two-tiered: the trailing `d - k` rows are `q * e_j` exactly, and the leading `k`
rows have `O(1)`-to-`O(sqrt(k) q)` norms depending on `A`. `rawtail` averages
`log ||b*_i||` over the **last `beta`** indices, so as `beta` grows the window
slides across the block boundary at index `k`, and as `k -> d - k` the boundary
itself moves. The statistic therefore depends on `beta` **and** on `k` **by
construction**, and it depends on `A` — so it is basis-dependent and has
non-zero dispersion. A relevance criterion that cannot see this dependence
cannot see any.

### 1.5 The criteria, carried verbatim from BATCH-cbe023 prereg 2.2/2.5

    rho(X_b, X_a, s) = |X_b - X_a| / max(|X_a|, s)

    G-REL1  beta-dependence      rho( X(beta_hi), X(beta_lo), s_X ) >= tau_rel = 0.10
    G-REL2  block attribution    rho( X(d, d-k, beta), X(d, k, beta), s_X ) >= tau_rel = 0.10
    G-REL   PASS iff BOTH clauses pass

**`tau_rel = 0.10` is carried unchanged and is not re-derived here.** §2 does
not repair the threshold; it repairs the **replication**, the **normalization
disclosure** and the **could-not-PASS guard**, which is what AM-10 requires.

---

## 2. SECTION R — THE LEAD

> **THE QUESTION.** Is BATCH-cbe023's `R3`/`R1` boundary a fact about
> observables, or a property of `G-REL`'s normalization at one basis index? And
> does the AM-4/AM-8 admissibility gate — which AM-8 makes **binding over every
> candidate observable in this goal** — admit an observable that carries no
> information at all?

### 2.1 What is computed

**(a) Replication.** `G-REL1` and `G-REL2` are recomputed for `X8 = rdet`,
`X9 = lam1n`, `X10 = hkz` — and for `X_null` and `X_mp` through the **identical
code path** — over **all 8 frozen bases** `i = 0..7`, at **every** mirrored pair
`L1/L2`, `L4/L5`, `L7/L8`, `L9/L10`, `L11/L12`, at **every** beta of §1.3.

**(b) Reported per candidate and per pair**, for the mirrored gap
`g_i = X(d, d-k, beta, i) - X(d, k, beta, i)` over `i = 0..7`:

    mean_g       = mean_i g_i
    sd_k         = sd_i X(d, k,   beta, i)     [ddof = 1]   -- between-basis sd, k side
    sd_dmk       = sd_i X(d, d-k, beta, i)     [ddof = 1]   -- between-basis sd, mirror side
    sd_g         = sd_i g_i                    [ddof = 1]   -- paired
    t_paired     = mean_g / ( sd_g / sqrt(8) ) ,  df = 7

**(c) Both normalizations, side by side, with the ratio printed (AM-10 b).**
Every `G-REL` entry is reported at `max(|X|, s_X)` **and** at `|X|`, with
`s_X / |X|` printed **beside** each entry, so a reader sees at a glance where
the scale floor is the binding term.

**(d) `X_null` on the scored list (AM-11).** `X_null` is on the frozen
candidate list of this section and is pushed through the **identical** gate and
the **identical** code path as every other candidate, with its between-basis
dispersion reported at every `(lattice, beta)`.

**(e) `G-VAR`, the refusal criterion (AM-11).** Defined in §2.5.

**(f) `X_mp` MUST-PASS (AM-10 c).** Defined in §1.4, predicted in §2.3, and
its failure mode is §2.8.

### 2.2 Units of every threshold in this section

| symbol | value | **units** |
| --- | --- | --- |
| `tau_rel` | `0.10` | **dimensionless ratio**: `|X_b - X_a|` divided by `max(|X_a|, s_X)`. Not a percentage of `X`, not a p-value, not a probability. |
| `s_X` | `1.0` for every candidate in §1.4 | **same units as `X`** (all five candidates are logs or log-normalized ratios, hence dimensionless), acting as an **absolute floor** on the denominator. When `|X| < 1.0`, `tau_rel` degenerates to an **absolute** difference test at `0.10` in `X`'s own units. |
| `t_crit` | `2.364624251592784` | **Student-t quantile**, `df = 7`, two-sided `0.05`. Reported alongside `3.4994832973504924` at two-sided `0.01`. |
| `tau_var` | **exactly `0`** | **variance units of `X`**: the between-basis sample sd over `i = 0..7` at fixed `(d, k, beta, q)`. Zero means bit-level zero; see §2.5 for how that is decided. |
| detection floor | `t_crit * sd_g / sqrt(8)` | **same units as `X`** — the smallest `|mean_g|` this paired test can call at `df = 7`. Reported per candidate per pair per beta. |

### 2.3 Predictions, stated before any datum

| # | prediction | basis for it |
| --- | --- | --- |
| **P-R1** | `X_mp = rawtail` **PASSES both `G-REL` clauses** at a majority of pairs. | §1.4: the dependence on `beta` and on `k` is structural. |
| **P-R2** | `X_null` **PASSES `G-REL1`, `G-REL2`, `G-NUM`, `G-INV` and `G-Q`** — i.e. it walks the entire AM-4 gate — while carrying **exactly zero** information about any basis. | §2.6: closed form; the `G-INV` and `G-Q` passes are **FORCED**, see §2.7. |
| **P-R3** | `X_null` has **exactly zero** between-basis dispersion at every `(d, k, beta, q)`. | §2.6: it is a function of `(d, k, beta, q)` alone. |
| **P-R4** | Therefore `G-VAR` **FIRES**, and the AM-4/AM-8 gate is declared **INADMISSIBLE**, with **no admissibility claim reportable from it**. | P-R2 + P-R3 + §2.5. |
| **P-R5** | For `X8 = rdet` and `X9 = lam1n`, `G-REL1` is **identically `0` by algebra** (neither takes a `beta` argument), so `REL-1` is **UNTESTED** for them, **not** "failed". | Carried from DEC-20260808-05b684 rationale (i). |
| **P-R6** | For `X10 = hkz` at `L7/L8`, the mirrored gap is **small against its own between-basis spread** and `|t_paired| < t_crit` at `beta = 5`. | Quoted Red Team review measurement, §2.9 — **to be agreed or disagreed with as a measurement of our own, never inherited.** |
| **P-R7** | For at least one candidate and pair, the `max(|X|, s_X)` and `|X|` normalizations **disagree on the verdict**. | Quoted Red Team RT unit-mutation observation; `s_hkz = 1.0` exceeded every realized `|hkz|` by `2.2x`–`15.1x`. |

**P-R1 is the guard.** If P-R1 fails, `G-REL` has failed to detect a dependence
that is present by construction, and §2 reports that `G-REL` is **not a
relevance criterion**, in place of any statement about `rdet`, `lam1n` or `hkz`.

### 2.4 Falsifiers, stated before any datum

| prediction | **falsifier** |
| --- | --- |
| P-R1 | `X_mp` fails `G-REL1` or `G-REL2` at a majority of computable pairs. |
| P-R2 | `X_null` fails any one of `G-NUM`, `G-INV`, `G-Q`, `G-REL1`, `G-REL2` under the identical code path. |
| P-R3 | any measured between-basis sd of `X_null` is `> 0` at any `(d, k, beta, q)`. |
| P-R4 | `G-VAR` does not fire — i.e. no candidate on the scored list has zero dispersion while passing the gate. |
| P-R5 | `rdet` or `lam1n` produces a non-zero `REL-1` value at any lattice. |
| P-R6 | our own `L7/L8` `beta = 5` replication yields `|t_paired| >= t_crit`, or a mean gap large against `sd_g`. |
| P-R7 | the two normalizations agree on every candidate at every pair and beta. |

### 2.5 `G-VAR` — the refusal criterion (AM-11), with its threshold in units

> ### **`G-VAR`: an admissible observable MUST have NON-ZERO between-basis dispersion at fixed `(d, k, beta, q)`. A gate that admits a zero-dispersion closed form is declared INADMISSIBLE, and NO admissibility claim may be reported from it.**

**Statistic.** `sd_i X(d, k, beta, i)` over the 8 frozen bases, `ddof = 1`, in
`X`'s own units.

**Threshold.** `tau_var = 0` **exactly**. The decision is made **structurally,
not by tolerance**: a candidate is declared zero-dispersion iff the 8 values are
**bit-for-bit identical** as IEEE-754 doubles (`len(set(map(float.hex, vals))) == 1`).
The float sample sd is reported **beside** the bit test at every cell, but does
not decide it. This removes the failure mode in which a tolerance is chosen
loosely enough that nothing is ever refused, and the symmetric one in which
float noise in an otherwise-closed-form quantity manufactures dispersion.

**`X7 = tr(P^2)` CANNOT serve as this control, and is not used as one.** It is
`q`-independent and `k`-independent, so it tests only whether the gate refuses a
**constant** — not whether it refuses **parameter arithmetic**. `X_null` is the
control precisely because it *does* move with `d`, `k`, `beta` and `q`, and
still carries no information about any basis.

### 2.6 `X_null`, computed in closed form **in advance**

`X_null(B, beta) = (beta/d) * (1/d) * log|det B|` and, for
`B = [[I_k, A],[0, q I_{d-k}]]`, `|det B| = q^(d-k)` exactly, independent of
`A`. Hence

    X_null = (beta / d^2) * (d - k) * log q

which contains **no basis index**. With `q = 3329`, `log q = 8.110427237575024`:

| lattice | `(d,k)` | beta values → `X_null` |
| --- | --- | --- |
| `L1` | `(100,30)` | 15 → 0.851595 · 30 → 1.703190 · 35 → 1.987055 · 50 → 2.838650 · 65 → 3.690244 |
| `L2` | `(100,70)` | 15 → 0.364969 · 30 → 0.729938 · 35 → 0.851595 · 50 → 1.216564 · 65 → 1.581533 |
| `L4` | `(140,40)` | 20 → 0.827595 · 40 → 1.655189 · 45 → 1.862088 · 70 → 2.896581 · 95 → 3.931074 |
| `L5` | `(140,100)` | 20 → 0.331038 · 40 → 0.662076 · 45 → 0.744835 · 70 → 1.158632 · 95 → 1.572430 |
| `L7` | `(20,6)` | 5 → 1.419325 · 10 → 2.838650 · 15 → 4.257974 |
| `L8` | `(20,14)` | 5 → 0.608282 · 10 → 1.216564 · 15 → 1.824846 |
| `L9` | `(30,9)` | 7 → 1.324703 · 15 → 2.838650 · 22 → 4.163353 |
| `L10` | `(30,21)` | 7 → 0.567730 · 15 → 1.216564 · 22 → 1.784294 |
| `L11` | `(40,12)` | 10 → 1.419325 · 20 → 2.838650 · 30 → 4.257974 |
| `L12` | `(40,28)` | 10 → 0.608282 · 20 → 1.216564 · 30 → 1.824846 |

**These numbers are pre-registered.** The measuring task recomputes them
through the identical code path and must reproduce this table; a departure is a
defect in the code path, not a finding.

The `G-REL` consequences follow by arithmetic and are also pre-registered:

* `REL-1` at `L1`: `|3.690244 - 0.851595| / max(0.851595, 1.0) = 2.838650 >= 0.10` → **PASS**.
* `REL-2` at `L1/L2`, `beta = 15`: `|0.364969 - 0.851595| / max(0.851595, 1.0) = 0.486626 >= 0.10` → **PASS**.

`X_null` therefore reaches `R1` on the `G-REL` clauses **before any basis is
built**, which is the point.

### 2.7 What is FORCED, and is therefore UNTESTED rather than passed

Reported as **UNTESTED**, never as "invariant" and never as a passed test:

* **`X_null` under `G-INV`.** `|det B|` is invariant under any unimodular `U`
  (`|det UB| = |det B|`) and under any ambient isometry `H`
  (`|det BH| = |det B|`), **by algebra**. Its `T1`/`T2`/`T3` residuals are `0`
  identically. This is not a test that could have failed.
* **`X8 = rdet` under `G-INV`** for the same reason — determinant invariance.
* **`X9`, `X10` under `T1` (ambient isometry)**, because they are computed
  through the integer Gram matrix and `G(BH) = B B^T` identically (binding carry
  8).
* **`REL-1` for `X8` and `X9`**, which take no `beta` argument, so
  `X(beta_hi) - X(beta_lo) = 0` bit-for-bit. **UNTESTED, not failed** (P-R5).

### 2.8 The arrangement in which this section's own check COULD NOT FAIL — **both directions**

BATCH-cbe023's Section A named both directions for INVARIANCE and for
SENSITIVITY and **neither for RELEVANCE**, which is the arrangement it actually
ran in. That is the exact hole this section exists to close. It is not
reopened elsewhere: each check below is named in both directions and shown not
to be in either arrangement.

**Check 1 — `G-REL` as a relevance criterion.**

* *Could-not-PASS arrangement:* every candidate has `|X| << s_X = 1.0`, so the
  denominator is pinned at `1.0` and `G-REL` becomes an **absolute** `0.10`
  test in `X`'s own units, which small log-normalized quantities can essentially
  never clear. In that arrangement "no candidate is relevant" is a statement
  about the **units**, not about lattices.
  *We are not in it, and the evidence is pre-registered:* `X_mp = rawtail` is
  declared **MUST-PASS** (P-R1), and `X_null` is predicted to pass (P-R2). Two
  candidates on the scored list are predicted to clear the criterion. If
  **neither** clears it, the criterion is refuted as a criterion and §2 reports
  that instead of any candidate verdict.
* *Could-not-FAIL arrangement:* the criterion is evaluated at `|X|`
  normalization only, where any candidate with a small `|X|` clears `0.10` on
  noise alone.
  *We are not in it:* **both** normalizations are reported at every entry with
  `s_X / |X|` beside them (AM-10 b), and the paired `t` with its own detection
  floor is reported beside both, so a gap that is small against its own
  between-basis spread cannot be read as a pass under either normalization.

**Check 2 — `G-VAR` as a refusal criterion.**

* *Could-not-FIRE arrangement:* the dispersion threshold is a loose tolerance
  (say `sd > 1e-12`), and float noise in an essentially closed-form quantity
  lifts it above the bar, so nothing is ever refused.
  *We are not in it:* the decision is the **bit-identity** test of §2.5, not a
  tolerance. `X_null` contains no basis index at all, so its 8 values are
  produced by the same arithmetic on the same inputs and are bit-identical or
  the code path is broken.
* *Could-not-PASS arrangement (i.e. `G-VAR` refuses everything):* every
  candidate on the list is a closed form, so `G-VAR` fires on all of them and
  the gate is trivially inadmissible.
  *We are not in it:* `rdet`, `lam1n`, `hkz` and `rawtail` all consume `A`,
  which is drawn per basis index `i`, and are predicted to show **non-zero**
  dispersion. If they do not, that is itself the report: the frozen basis family
  does not vary at these parameters, and **no** dispersion criterion can be
  applied to it.

**Check 3 — the `X_mp` MUST-PASS guard.**

* *Could-not-FAIL arrangement:* `X_mp` is chosen after seeing which candidates
  pass, so it is guaranteed to pass.
  *We are not in it:* `X_mp` is defined in §1.4 of this notarized document,
  before any measurement, and its predicted pass is stated with the structural
  reason. Its failure is a **live** outcome with a row in §2.10 (`R-OUT-5`).

### 2.9 The Red Team's `L7/L8` replication — a review measurement, quoted, **not** a baseline

    beta = 5    frozen REL-2 at i = 0   0.06969
                over 8 bases  min 0.00852  med 0.03261  max 0.06969  sd 0.02008
                relative at i = 0       0.40360
                over 8 bases  min 0.04203  med 0.17833  max 0.40360
                between-basis sd of hkz WITHIN a cell:  k=6  0.02389   k=14  0.03924
                mean mirrored gap 0.00103   paired t over 8 bases  -0.064  (df 7)
    beta = 10   mean mirrored gap 0.00065   paired t  +0.088
    beta = 15   mean mirrored gap 0.00253   paired t  -0.784
    HKZ verified, max violation 0.0.  0.22 s per mirrored pair; 2.86 s for the null.

    [quoted: BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md,
     RT-A2 and section 2.2; quoted in DEC-20260808-05b684]

**This is a REVIEW MEASUREMENT. It is not a pre-registered result, it is not a
rescoring, and it is not this batch's baseline.** §2 reproduces `L7/L8` as one
of its five pairs and reports **agreement or disagreement as a measurement of
its own**. The quoted timings are the reviewer's measurement; this section's
own timings are its own to measure and report, and the wall-clock budget is a
**STOP, never a target**.

### 2.10 Outcome map — **a row for every outcome** (AM-12 a, b, c)

| id | condition | reported as |
| --- | --- | --- |
| `R-OUT-1` | `X_null` passes the full gate **and** has zero dispersion → `G-VAR` fires | **THE GATE IS INADMISSIBLE UNDER `G-VAR`.** No admissibility claim is reportable from it. `R1`/`R3` labels from BATCH-cbe023 are not repaired by this batch and stay not-citable. |
| `R-OUT-2` | `X_null` **fails** some gate clause | `G-VAR` does not fire on `X_null`. Report **which** clause refused it and at which cell, and report the gate as **NOT SHOWN INADMISSIBLE BY THIS CONTROL** — which is not the same as admissible. |
| `R-OUT-3` | `X_null` passes the gate but its dispersion is **non-zero** | The code path does not reproduce §2.6's closed form. **DEFECT IN THE INSTRUMENT**, reported as such; no admissibility claim either way. |
| `R-OUT-4` | `X_mp` **passes** `G-REL` | The could-not-PASS guard holds; `G-REL` verdicts on `rdet`/`lam1n`/`hkz` are reportable *as verdicts of that criterion*. |
| `R-OUT-5` | `X_mp` **fails** `G-REL` | **`G-REL` IS NOT A RELEVANCE CRITERION** at this scope: it cannot see a dependence present by construction. **No `G-REL` verdict on any other candidate is reported**, in either direction. |
| `R-OUT-6` | `hkz`'s `L7/L8` mirrored gap is small against `sd_g` and `|t_paired| < t_crit` | `R3` for `hkz` **survives replication at this pair**, and the *reason* is that the thresholded quantity has an expectation indistinguishable from zero against a spread many times its mean — **not** that `0.0697 < 0.10`. |
| `R-OUT-7` | `hkz`'s `L7/L8` gap is large against `sd_g` and `|t_paired| >= t_crit` | `R3` for `hkz` **does not survive replication**; report the pair, beta, mean, sd and `t`, and state that the BATCH-cbe023 boundary moves — **without** re-labelling the earlier batch, which is not rescored. |
| `R-OUT-8` | the two normalizations **disagree** at any entry | The `R1`/`R3` boundary is **decided by a units convention**. Report every disagreeing entry with both values and `s_X/|X|`. |
| `R-OUT-9` | the two normalizations **agree everywhere** | P-R7 is falsified; the boundary is not a units artifact **at the tested cells**, and the report says exactly that and no more. |
| `R-OUT-10` | a candidate is **NOT COMPUTABLE** at a pair within `d <= 40` and no-new-reduction | Reported as **NOT COMPUTED** with its structural reason. **Never** a zero, never a pass, never a fail, and **never entered into any count.** |
| `R-OUT-11` | a budget or resource cap binds | The partial grid is reported **with its floor**, and the cap is recorded as **INFRASTRUCTURE SIGNAL** — never a refusal, never an obstruction, never a negative result. |
| `R-OUT-12` | any conditional exclusion's **condition itself fails** | The exclusion does **not** apply; the affected candidate is scored and reported in the outcome field, not in prose. *(This row exists because AM-12(c) records exactly that failure against BATCH-cbe023's treatment of `D`.)* |

`R-OUT-1`..`R-OUT-3` are exclusive of each other; `R-OUT-4`/`R-OUT-5` are
exclusive; `R-OUT-6`/`R-OUT-7` are exclusive; `R-OUT-8`/`R-OUT-9` are exclusive.
`R-OUT-10`..`R-OUT-12` are orthogonal and may co-occur with any of the above.

**No refutation clause in this section has a trigger list containing only
candidates for which the tested premise holds by algebra (AM-12 b).** `G-VAR`'s
trigger is *any* candidate on the scored list with zero dispersion, evaluated
per candidate against its own measured dispersion — not a fixed sub-list.

### 2.11 Which frozen clause is LOAD-BEARING for each verdict (AM-14 a)

| verdict | load-bearing clause | is the verdict invariant to the quantity under repair? |
| --- | --- | --- |
| `R-OUT-1` (gate INADMISSIBLE) | `G-VAR` (§2.5), newly built here | **No.** Remove `G-VAR` and the verdict cannot be reached. `G-VAR` is rebuilt by this section, so the verdict is not determined by a threshold the section did not build. |
| `R-OUT-5` (`G-REL` refuted) | `tau_rel = 0.10` **carried unchanged** | **Partly yes, and it is disclosed:** `tau_rel` is *not* rebuilt here. The verdict is therefore reported **with** `X_mp`'s realized value at both normalizations, so a reader can see how far from the carried threshold it fell and re-score at any other. |
| `R-OUT-6`/`R-OUT-7` (`hkz` replication) | the paired `t` and `sd_g`, **both built here** over 8 bases | **No.** Both are new quantities of this section; neither existed in BATCH-cbe023, whose `G-REL` was a single draw at `i = 0`. |
| `R-OUT-8`/`R-OUT-9` (normalization) | `s_X = 1.0`, **carried unchanged** | **Yes, by design** — that is precisely the quantity being interrogated. Both normalizations are reported, so the verdict is a statement about the pair of conventions, not a consequence of one of them. |

### 2.12 Detection floor for §2

Per candidate, per pair, per beta:

    floor(mean_g) = t_crit(7, 0.05) * sd_g / sqrt(8) = 2.364624251592784 * sd_g / 2.8284271247461903

reported in `X`'s own units alongside the realized `mean_g`. A pair whose
`|mean_g|` falls below its floor is reported as **BELOW THE PAIRED-TEST
DETECTION FLOOR** — never as zero, never as absence, and never as agreement.

### 2.13 Bounds and required artifacts

* **BOUNDED:** minutes of compute. `d <= 40` for any reduction. **NO NEW
  REDUCTION** beyond the frozen HKZ pipeline as committed at snapshot
  `6bafef862` with its repair in place. The frozen basis construction is reused
  **exactly**; no new BKZ is run.
* `X9`/`X10` are computable only on the small-`d` family `L7..L12`. `L1/L2` and
  `L4/L5` are declared **NOT COMPUTED** for `X9`/`X10` in advance, with that
  structural reason. `X8`, `X_null` and `X_mp` are computable at every pair.
* **REQUIRED ARTIFACTS:** `measure_relvar.py`, `results_relvar.json`,
  `report_relvar.md`, `run_manifest.yaml`, and **durable** `command.txt`,
  `stdout.log`, `stderr.log` in the task directory. No path in a folded YAML
  scalar.
* The notarized `prereg_sha256` is verified against the committed blob and
  quoted in the report. **ABORT ON MISMATCH.**

---

## 3. SECTION B' — the AM-13 NULL FAMILY

Behind the lead. Seconds of compute on carried seeds.

### 3.1 What is built

The 13 grid points of the AM-1 `t` grid
`[0.0, 0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.05, 0.1, 0.25, 0.5, 1.0]`
are **regenerated as 13 INDEPENDENT Haar frames** from the carried seeds, so
that `E[Delta_i] = 0` at **every** step. **Pure numpy. NO BKZ. NO LLL. NO
reduction of any kind.**

Frame `g` at grid index `m`, draw `j`, cell `(d, beta)`:

    rng   = numpy.random.default_rng( seed_nullfam(d, beta, j, m) )
    Q     = qr( rng.standard_normal((d, beta)) ).Q     -> float32, as carried

    seed_nullfam(d, beta, j, m) = 700000 + d*1000 + beta*10 + j + 100000*(m+1)

The seed formula is **declared here, before any draw**, and is a translation of
the carried `seed_haar(d, beta, j) = 900000 + d*1000 + beta*10 + j` into a
per-grid-index family. It is disclosed as a **completion**, not as a carry: the
carried seed table has no 13-frame-family entry because no such family was ever
built.

Everything downstream is **carried byte-for-byte**: `q = 3329`,
`CBD_{eta=2}` errors from `seed_error(d) = 20260805 + d` with `N = 2^20` and
`chunk = 2^15` (the chunking **is** part of the RNG consumption order),
`R = ||Q^T e||^2 / ||e||^2`, `q_emp(p) = sort(R)[round(p*N) - 1]` at
`p = 2^-10`, `n_draw = 8`, `GATE_K = 4.0`,
`SE_diff(A,t) = sqrt(sd_A^2/8 + sd_haar^2/8)`, the four cells
`(100,30), (100,40), (140,30), (140,40)`, and the AM-3 closed forms

    Delta_i    = m(t_{i+1}) - m(t_i)
    SE_step(i) = sd_j( r_j(t_{i+1}) - r_j(t_i) ) / sqrt(8)          [ddof = 1, paired]
    stat_i(c)  = ( Delta_i + (c-1) * SE_diff(t_i) ) / SE_step(i)
    c_min(i)   = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i)
    t_crit     = 4.2071245566046755            (t_{7, 0.998})

`n_fire(c)` counts steps with `c_min(i) <= c`, over `4 cells x 12 steps = 48`.

### 3.2 The required sentence (binding carry 4)

The headline **must** be reported in this exact form, all three counts in one
sentence:

> On the rebuilt **null family**, `n_fire(c = 6)` is `<NULL>` of 48, against the
> committed real count of **29 of 48** and the Red Team's exact-null benchmark of
> **47 of 48**.

`29 of 48` may not appear in any artifact of this batch without `47 of 48` in
the same sentence.

### 3.3 The decay check — pre-registered as the pass/fail criterion (AM-13)

`n_fire(c)` is tabulated on the null family over the full carried
`c`-grid `[0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32]` and the criterion is:

> **PASS (the count is an effect):** `n_fire` on the null family is
> **materially below** the real count at `c = 6`, and `n_fire(c)` **decays** as
> `c` decreases toward the negative control.
>
> **FAIL (the count is an artifact):** `n_fire` on the null family is **at or
> above** the real count at `c = 6`. A quantity that does not decay when the
> parameter meant to destroy the effect is applied is an artifact
> (`docs/inventor-protocol.md` §3).

**Units.** `n_fire` is a **count out of 48**, not a rate and not a p-value.
`c` is in units of `SE_diff(A, t_i)` — multiples of the injection unit.
"Materially below" is fixed **in advance** as a difference of at least
`8 of 48` (one sixth of the family), so the criterion is not read off the
realized numbers.

### 3.4 Prediction, falsifier, detection floor

* **P-B1:** the null family gives `n_fire(c = 6)` **at or above 29 of 48**, and
  the criterion of §3.3 therefore **FAILS** — i.e. the committed count is not
  evidence of an effect. Grounds: the Red Team's exact null already reached
  `47 of 48`, and `c_min` on a null is driven by `t_crit * SE_step / SE_diff`,
  a ratio with no dependence on the graded path.
* **Falsifier of P-B1:** the null family gives `n_fire(c = 6) <= 21 of 48`
  (i.e. at least `8` below the real count).
* **Detection floor:** the count is an integer out of 48, so the floor is
  **1 step of 48 = 2.083 percentage points**; no difference smaller than one
  step is resolvable, and none is claimed.

### 3.5 Could-not-fail, both directions

* *Could-not-FIRE (the null can never look like the real arm):* the null is
  built with a **different** pipeline from the real arm, so any difference is a
  pipeline difference rather than a path-structure difference.
  *We are not in it:* the null family differs from the graded family in
  **exactly one** respect — the 13 frames are drawn independently instead of
  from a shared `(S_j, G_j)` path. Errors, projection, chunking, quantile
  estimator, `n_draw`, `SE` construction, `t_crit` and the `c` grid are
  **identical and carried byte-for-byte**.
* *Could-not-PASS (the null can never differ from the real arm):* if `c_min` is
  dominated by `t_crit * SE_step / SE_diff` and the two arms have similar `SE`
  ratios, the counts coincide **whatever** the path structure is — in which case
  `n_fire` was never a measure of the effect.
  *We are not in it, and this is the point of the section:* that arrangement is
  precisely what P-B1 predicts, and §3.3 declares in advance that it is a
  **FAIL** — an artifact — rather than a null result. The section is designed so
  that the coincidence is a *reportable finding about the statistic*, not a
  silent pass.

### 3.6 Load-bearing clause (AM-14 a)

The load-bearing quantity for both verdicts of §3.3 is `n_fire` itself, and it
is **rebuilt** here on a new object. `t_crit = 4.2071245566046755`, `GATE_K`,
`c = 6` and the `c` grid are **carried, not rebuilt**, and the verdict *is*
sensitive to `c`: `n_fire(c)` is reported over the full grid, so a reader can
check that the verdict is not an artifact of the single value `c = 6`.

### 3.7 Required artifacts

`measure_nullfam.py`, `results_nullfam.json`, `report_nullfam.md`,
`run_manifest.yaml`, and **durable** `command.txt`, `stdout.log`, `stderr.log`.

---

## 4. SECTION C1 — AM-14 (c), (d), (e): the re-derived floor and the widened band

Behind the lead.

> ### **THIS SECTION IS A RE-SCORE OF COMMITTED BATCH-cbe023 DATA UNDER A POST-BATCH THRESHOLD, AND IS LABELLED AS SUCH THROUGHOUT.**
> It is **not** a fresh measurement. It does **not** reinstate `CONSISTENT`, and
> it does **not** establish its negation. Every table it produces carries that
> label in its own header.

### 4.1 The floor, re-derived and stated **before** any re-scoring (AM-14 c)

The frozen design rule of BATCH-cbe023 prereg 4.4 is carried **unchanged**:
`tau_rel` = `1.67x` the top of the measured range of the **null's own median
relative difference** — "the smallest round multiple that puts the floor clearly
above the null's central tendency rather than at its edge". Only the *input* to
that rule changes, from the superseded instrument's nulls to **this batch's
rebuilt nulls**, which is exactly what AM-14(c) requires.

Rebuilt-null median relative differences, **read** from the committed
`results_am7.json` (§0.4):

    N-A  d100_b40   0.00645684        N-B  d100_b40   0.00768319
    N-A  d140_b40   0.00976958        N-B  d140_b40   0.01496443   <- top of range

    tau_rel_rebuilt = 1.67 * 0.01496443 = 0.02499060...  ->  0.025

> ### **THE RE-DERIVED FLOOR IS `tau_rel = 0.025`, STATED HERE BEFORE ANY RE-SCORING, AGAINST THE FROZEN `0.15`.**
> The exact product `0.0249906...` is reported beside the rounded `0.025` at
> every use, and the re-score is run at `0.025`, which is the value AM-14(c)
> itself names.

**`N-C` is excluded from the derivation, and here is the reason, declared before
the re-score.** `N-C` is the secondary Gaussian instrument check. For Gaussian
errors, `R ~ Beta(beta/2, (d-beta)/2)` **exactly** for every orthonormal frame,
so `D = q_emp/q_Beta - 1` is driven to `~0` on both sides and the *denominator*
`max(|D_GR|, |D_TL|)` of the relative difference collapses. Its median relative
differences (`1.0216`, `1.0050`) are therefore an artifact of a vanishing
denominator, not a measure of null central tendency, and `N-C` ran at `R = 60`,
below the frozen `R_min = 200`. AM-14(c) names exactly the four `N-A`/`N-B`
medians. Both the exclusion and the two excluded numbers are reported.

### 4.2 The widened SUGGESTIVE band (AM-14 d)

Carried band: `|t|` in `[0.8*|t|crit, |t|crit)` **and** relative difference
above `tau_rel`.

> ### **WIDENED BAND: ANY pair with `|t| >= 0.8*|t|crit` is recorded as SUGGESTIVE, REGARDLESS OF THE RELATIVE FLOOR**, with its exact `|t|`, `|t|crit`, `Delta_bar`, `SE`, `nu_eff` and relative difference, so a near miss reaches the record instead of being discarded.

`|t|crit = t.ppf(1 - alpha_pair/2, nu_eff)` per target at its own `nu_eff`,
`alpha_pair = 0.10/11 = 0.0090909090909...` — **carried, not re-derived.**

### 4.3 `SE_2way / SE_naive` at every target (AM-14 e)

    SE_naive(target) = sd( Delta_table flattened, ddof=1 ) / sqrt(S*E) ,  S=8, E=4
    SE_2way(target)  = the committed two-way (support x pool) SE with Satterthwaite nu_eff

The ratio is reported at **every** target. **A ratio below `1` is in tension
with AM-7 clause (1) and is disclosed explicitly**, per target, in the report
body and not only in a table.

### 4.4 Units

| symbol | value | units |
| --- | --- | --- |
| `tau_rel_rebuilt` | `0.025` (exact `0.0249906...`) | **dimensionless ratio** `\|Delta_bar\| / max(\|D_GR\|, \|D_TL\|)`. Not a percentage of `Delta`, not a p-value. |
| `0.8 * \|t\|crit` | per target | **Student-t units** at that target's own `nu_eff`. |
| `SE_2way/SE_naive` | per target | **dimensionless ratio of two standard errors**, both in `D`'s units. |
| detection floor | `\|t\|crit * SE / max(\|D_GR\|,\|D_TL\|)` | **relative, reported in percent.** |

### 4.5 Prediction, falsifier, detection floor

* **P-C1a:** lowering the floor from `0.15` to `0.025` moves **at least one**
  target out of "floor `>=` tau_rel" and into a decidable state.
  *Falsifier:* no target changes state.
* **P-C1b:** at least one pair enters the **widened** SUGGESTIVE band that the
  carried band excluded.
  *Falsifier:* the widened band admits nothing the carried band did not.
* **P-C1c:** at least one target has `SE_2way/SE_naive < 1`.
  *Falsifier:* every target has ratio `>= 1`.
* **Detection floor:** unchanged from the committed instrument and **carried
  with its qualifier**: the tightest **non-degenerate** floor is `10.83%`
  relative, and the family-level bound over targets with a well-defined two-way
  SE is `~10.8%` relative. The `3.91%` figure is **not citable without the
  NEGATIVE-VARIANCE-COMPONENT qualifier in the same sentence**, and this section
  reports it only in that form.

> **Consequence, pre-registered:** with a detection floor of `~10.8%` relative
> and a re-derived floor of `2.5%`, the floor is **no longer the binding term**
> — the `|t|` clause is. This section therefore **cannot** produce a
> falsification that the carried scoring did not already produce; it can only
> change *labels* and expose near misses. **That limit is declared here, before
> the re-score, so it is not discovered afterwards and reported as a result.**

### 4.6 Could-not-fail, both directions

* *Could-not-FIRE:* the re-score changes nothing because clause (i) (`|t|`) is
  binding at every target and clause (ii) never bound.
  *We are not blind to it:* §4.5's consequence note declares this **as the most
  likely outcome**, and P-C1a/b/c are stated so that "nothing moved" is a
  recorded falsification of this section's own predictions rather than a
  non-result.
* *Could-not-PASS:* the widened band is so wide that every target enters it,
  making SUGGESTIVE meaningless.
  *We are not in it:* the band is `[0.8|t|crit, |t|crit)` — a `20%` window below
  the critical value in `t` units, not an open lower bound — and the count of
  targets entering it is reported **out of the total**, with the carried band's
  count beside it.

### 4.7 Load-bearing clause (AM-14 a)

`tau_rel` is the quantity under repair, and it **is** rebuilt here. The verdict
is checked for invariance to it: the section reports every target's state at
**both** `0.15` and `0.025`, so a verdict identical under both is disclosed as
**invariant to the repair** — which, per §4.5, is the predicted case.

### 4.8 Required artifacts

`rescore_c1.py`, `results_c1.json`, `report_c1.md`, `run_manifest.yaml`, and
**durable** `command.txt`, `stdout.log`, `stderr.log`.

---

## 5. SECTION C2 — AM-14 (b): a positive control that ACTUALLY INJECTS

Behind the lead.

### 5.1 What is done

For every Section C target, a declared constant offset `delta` is **added to
every entry of the committed `Delta_table_S_by_E`** and the **full scoring path
is re-run end to end** on the injected table:

    two-way (support x pool) variance decomposition
      -> SE(Delta_bar)
      -> Satterthwaite nu_eff
      -> |t| = |Delta_bar| / SE
      -> |t|crit = t.ppf(1 - alpha_pair/2, nu_eff)
      -> relative difference = |Delta_bar| / max(|D_GR|, |D_TL|)
      -> FALSIFYING-PAIR verdict under BOTH clauses

**No closed-form shortcut is used anywhere.** AM-14(b) exists because
closed-form arithmetic *in the SE the control is meant to validate* cannot
detect SE inflation. The injected table is re-decomposed from scratch.

### 5.2 The injected magnitudes, declared in advance, in units

`delta` is expressed in units of the target's **committed** `SE(Delta_bar)`:

    delta / SE  in  { 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0 }
    plus the negative control  delta = 0  (no injection)

and the **absolute** offset `delta` is reported in `D`'s own units at every
target beside the ratio.

> ### **DECLARED IN ADVANCE — what the instrument SHOULD and SHOULD NOT catch:**
>
> * **SHOULD NOT catch:** `delta/SE = 0.5` and `1.0`. These are at or below the
>   noise level; a `FALSIFYING` verdict at `delta/SE <= 1.0` at any target means
>   the instrument fires on nothing and is **over-sensitive**.
> * **SHOULD catch:** `delta/SE = 8.0` and `12.0`, at every target whose
>   `|t|crit` is below `8` — i.e. wherever the injection exceeds the critical
>   value by a clear margin **and** the relative difference clears the floor in
>   use.
> * **The interesting band** is `2.0 .. 6.0`, where `|t|crit` (which ranges from
>   `~2.78` at `nu_eff = 31` to `~3.57` at `nu_eff = 7`, and higher at the
>   degenerate `nu_eff`) sits. No prediction is made inside it beyond
>   monotonicity (§5.3).

Because a **constant** offset shifts `Delta_bar` by exactly `delta` and leaves
every variance component unchanged **in exact arithmetic**, the control's real
job is to verify that the **implemented** path actually behaves that way —
including at the `NEGATIVE-VARIANCE-COMPONENT` targets, where `nu_eff` falls back
to the residual df `(S-1)(E-1) = 21` and where the closed-form intuition is
least reliable. That is the SE-inflation failure AM-14(b) names, and it is why
the decomposition is re-run rather than assumed.

### 5.3 Predictions, falsifiers, detection floor

* **P-C2a:** at `delta/SE = 0`, every target reproduces its committed
  `Delta_bar`, `SE`, `nu_eff`, `|t|` and verdict **bit-for-bit** (tolerance
  `1e-12` relative, declared).
  *Falsifier:* any target departs.
* **P-C2b:** `|t|` is **monotone non-decreasing** in `delta` at every target,
  once `delta` exceeds `|Delta_bar_committed|`.
  *Falsifier:* a non-monotone `|t|` at any target.
* **P-C2c:** **no** target returns `FALSIFYING` at `delta/SE <= 1.0`.
  *Falsifier:* any does — the instrument is over-sensitive and the finding is
  reported as such.
* **P-C2d:** **every** target with `|t|crit < 8` returns `FALSIFYING` at
  `delta/SE = 12.0` **under the floor in use**.
  *Falsifier:* one does not; report which, its `|t|`, `|t|crit`, `nu_eff`, its
  relative difference and which clause blocked it.
* **P-C2e:** the recovered SE at `delta > 0` equals the committed SE to `1e-12`
  relative at every target. **A departure is SE inflation**, which is the exact
  defect AM-14(b) was written to detect, and it is reported as a **finding about
  the instrument**.
  *Falsifier:* SEs match everywhere — the instrument is clean on this axis.
* **Detection floor:** the smallest injection this control resolves is set by
  the `delta/SE` ladder's spacing, `0.5 SE` at the bottom. Nothing below
  `0.5 SE` is tested and nothing below it is claimed.

### 5.4 Could-not-fail, both directions

* *Could-not-FIRE:* the injection is applied to `Delta_bar` **after** the
  variance decomposition, so `SE` is unchanged by construction and inflation can
  never be detected. **This is the exact defect AM-14(b) names.**
  *We are not in it:* the offset is added to the **raw `S x E` table**, and the
  decomposition is re-run **from that table**. If the implementation inflates
  `SE`, P-C2e catches it.
* *Could-not-PASS:* the ladder starts so high that every rung fires, so
  "detects the injection" is vacuous.
  *We are not in it:* the ladder starts at `0.5 SE`, **below** every target's
  `|t|crit`, and P-C2c declares that the bottom two rungs **must not** fire. The
  control has a live failure mode at both ends.

### 5.5 Load-bearing clause (AM-14 a)

The load-bearing quantity is the **two-way SE and its `nu_eff`**, and both are
**rebuilt** here on the injected table. `alpha_pair` and the verdict rule are
carried. The control's verdicts are reported at **both** `tau_rel = 0.15` and
`tau_rel = 0.025` (§4.1) so that no C2 verdict is determined by a threshold this
batch did not rebuild.

### 5.6 Required artifacts

`posctl_c2.py`, `results_c2.json`, `report_c2.md`, `run_manifest.yaml`, and
**durable** `command.txt`, `stdout.log`, `stderr.log`.

---

## 6. Frozen constants — one table, all sections

| § | constant | value | provenance |
| --- | --- | --- | --- |
| R | `tau_rel` | `0.10` | **[carried]** BATCH-cbe023 prereg 2.2/2.5 |
| R | `s_X` (all five candidates) | `1.0` | **[carried]** |
| R | `t_crit(7, 0.05)` | `2.364624251592784` | **[closed form]** |
| R | `t_crit(7, 0.01)` | `3.4994832973504924` | **[closed form]** |
| R | `tau_var` | **exactly `0`**, decided by bit-identity | **set here** (AM-11) |
| R | `n_bases` | `8`, `i = 0..7` | **[carried]** |
| R | `log q`, `q = 3329` | `8.110427237575024` | **[closed form]** |
| B' | AM-1 `t` grid (13 pts) | `0, .0025, .005, .0075, .01, .015, .02, .03, .05, .1, .25, .5, 1.0` | **[carried, verbatim]** |
| B' | `t_crit` | `4.2071245566046755` (`t_{7,0.998}`) | **[carried]** |
| B' | `GATE_K` | `4.0` | **[carried]** |
| B' | `c` grid | `0,1,2,3,4,6,8,12,16,24,32` | **[carried]** |
| B' | `c` for the headline | `6` | **[carried]** |
| B' | family size | `4 cells x 12 steps = 48` | **[carried]** |
| B' | "materially below" | `>= 8 of 48` | **set here**, before any datum |
| B' | `seed_nullfam(d,beta,j,m)` | `700000 + d*1000 + beta*10 + j + 100000*(m+1)` | **completion, declared here** |
| C1 | `tau_rel_rebuilt` | `0.025` (exact `0.0249906...`) | **derived here** by the carried rule from the rebuilt nulls (AM-14 c) |
| C1 | `alpha_pair` | `0.10/11 = 0.0090909090909...` | **[carried]** |
| C1 | SUGGESTIVE band | `\|t\| >= 0.8*\|t\|crit`, **no floor condition** | **set here** (AM-14 d) |
| C1 | non-degenerate detection floor | `10.83%` relative; family bound `~10.8%` | **[carried, with its qualifier]** |
| C2 | `delta/SE` ladder | `0, 0.5, 1, 2, 3, 4, 6, 8, 12` | **set here**, before any datum |
| C2 | reproduction tolerance | `1e-12` relative | **set here** |
| all | claim tier | **TOY** | **[carried]** |

---

## 7. What this pre-registration does NOT do

* It does **not** re-litigate AM-10 .. AM-14 or their binding carries.
* It does **not** rescore BATCH-a44d08 in any respect.
* It does **not** reinstate or negate `CONSISTENT`.
* It does **not** claim that any observable in this goal is admissible. §2's
  most likely outcome (`R-OUT-1`) is that the **gate itself** is inadmissible,
  from which **no admissibility claim is reportable in either direction**.
* It does **not** propose an algorithm, a cost model or an attack, and there is
  therefore **no cryptographic baseline** to compare against and no
  `dominated_by` / `sota_delta` that could be non-null. Any successor presenting
  any of this against a cryptographic baseline must first supply the baseline;
  **there is none here.**
* It does **not** produce, and does not claim, any solution certificate. No
  discrete-log solve and no factor-base relation is claimed anywhere in this
  batch, so `docs/claims-and-verification.md` requires none;
  `certificate.kind: none` in every manifest, with that reason. The
  cross-checks in §2 (bit-identity dispersion, closed-form `X_null`
  reproduction, HKZ violation verification) are **INSTRUMENT CHECKS** and are
  labelled as such, never as certificates.

**THE REFUSAL IS A LEGITIMATE AND PREFERRED OUTCOME.** "The gate is
INADMISSIBLE under `G-VAR`" is §2's result if the measurement says so, and it is
worth more than a statistic that survives only by a normalization.

---

*END OF FROZEN PRE-REGISTRATION. Nothing below the notarizing commit may amend
it; a change requires a superseding record.*
