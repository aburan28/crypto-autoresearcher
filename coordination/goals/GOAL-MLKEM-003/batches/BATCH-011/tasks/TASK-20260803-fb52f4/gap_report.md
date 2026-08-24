# Accounting for the published-vs-estimator dual-attack cost gap at FIPS 203 parameters

**TASK-20260803-fb52f4 · GOAL-MLKEM-003 · BATCH-011 · executor · 2026-08-03**

Artifacts: `dual_gap_decomposition.py`, `results.json`, `heuristics.yaml`,
`receipt.json`, `run_stdout.log`, `run_stderr.log` (all in this directory).

---

## 0. What this is, and what it is not

**Everything below is a COST-MODEL ESTIMATE.** Nothing was measured. Every figure
comes from lattice-estimator pinned at `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`,
driven Sage-free through `tools/sage_free_estimator`, plus the eighteen numbered
modelling choices in `heuristics.yaml`.

- **No ML-KEM break is claimed and none is implied.** No solve, no relation, no
  certificate; `certificate.kind: none`.
- **No security proof is claimed either.** A decomposition explains a discrepancy
  between two cost estimates. It establishes neither of them.
- **`arora_gb`, `dual` and `primal_hybrid` do not execute in this harness**, and
  `matzov` fails under `RC.Kyber`. No sentence here says "best attack"; every
  comparison is scoped to `primal_bdd`, `dual_hybrid(fft=True)` and `matzov`
  under the reduction cost models named.
- **AGENTS.md rule 12 is UNMET and UNWAIVED.** Nothing here changes, corrects, or
  treats as corrected EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or
  KN-FIND-014.
- This is an **executor record**: observations, sized differences, and stated
  residuals. It reaches no verdict on a hypothesis and validates no heuristic.

---

## 1. The instrument validated first (CTRL-1), verbatim

`tools/sage_free_estimator/known_answer_control.py` was run as a **subprocess,
before any other computation**, and exited **0**:

```
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

Kyber512   143.7884782479     143.7884782479   3.13e-13     dual_hybrid(fft=True)
Kyber768   203.7878630676     203.7878630676   2.27e-13     dual_hybrid(fft=True)

PASS: every reference reproduced against lattice-estimator 3e48ef421ec2 -- primal_bdd exactly (delta 0.0), dual_hybrid(fft=True) within 1e-09.
Scope: primal_bdd and dual_hybrid(fft=True) under RC.MATZOV.
KNOWN UNAVAILABLE in this harness, all verified by running them: arora_gb (PowerSeriesRing is a stub that raises), dual (ZeroDivisionError), primal_hybrid (ZeroDivisionError). Any 'best attack' claim is scoped to the attacks actually served.
exit_code = 0
```

`primal_bdd` exact (delta 0.0); `dual_hybrid(fft=True)` within 1e-9. The script
aborts non-zero on any other outcome.

Five further controls ran, three of which can fail non-trivially
(`results.json → controls`):

| control | what it checks | result |
|---|---|---|
| CTRL-2 | the `.n()` patch (§3) is inert on every path CTRL-1 covers | pass — primal_bdd delta **0.0**, dual delta ≤ 3.13e-13 |
| CTRL-3 | patched `matzov` vs the estimator's **own committed Sage doctest** at the pin | pass — every integer parameter exact, every log2 to printed precision, under **both** RC.MATZOV and RC.ADPS16 |
| CTRL-4 | null on the patch: 30-bit rounding vs full 200-bit precision | pass — optimum moves by 0.0 / **1.41e-11** / 0.0 bits |
| CTRL-5 | archived Carrier Table C.1 arithmetic, `n_enu+n_fft+n_lat = n` | pass — 9 of 9 rows |
| CTRL-6 | sign null: mis-paired comparisons must produce **both** signs | pass — +67.2357 and −120.0440 |
| CTRL-7 | the refinement machinery reproduces the estimator's own optimum when restricted to the estimator's own grid | pass on all three sets, delta < 1e-9 |

CTRL-6 and CTRL-7 are the discriminating ones: CTRL-6 would catch a gap
arithmetic that can only produce one sign, and CTRL-7 would catch a refinement
loop that "finds" improvements because it evaluates a different objective.

---

## 2. The finding in one paragraph

**The gap is dominated by a comparison against the wrong estimator function, and
that term alone is 96% / 85% / 81% of it.**
`estimator.lwe_dual.dual_hybrid(..., fft=True)` — the object EV-MLKEM-015
compared the published figures against — is **not** the estimator's MATZOV
attack. It is the Espitau–Joux–Kharchenko dual hybrid with a Guo–Johansson FFT
solver, whose distinguisher hardcodes the FFT modulus to 2 and cites the
Independence Heuristic of ia.cr/2023/302. The estimator's implementation of
MATZOV Theorem 7.6 is `estimator.lwe_dual.matzov`, and `estimator/lwe.py:13`
reads `from .lwe_dual import matzov as dual_hybrid` — so the estimator's *public*
`LWE.dual_hybrid` name resolves to `matzov`, not to `lwe_dual.dual_hybrid`. The
two differ by **4.13 / 7.42 / 11.48 bits**, growing with β, which is the observed
growth. Once the right function is used, and once the estimator's own optimiser
slack inside that same cost function is relaxed, the pinned public estimator
reproduces Carrier's published headline to **−0.48 / −0.61 / +0.30 bits**.

---

## 3. Method

Four stages, each evaluating the **same** MATZOV Theorem-7.6 cost function
(`estimator/lwe_dual.py:566-626`) under **the same** reduction cost model
(`RC.MATZOV`) at **the same** pin. Stages 2–4 relax *optimiser* choices, not
cost-model content, so each is ≥ 0 by construction (H9, verified by CTRL-7).

One instrument gap had to be closed to run `matzov` at all:
`estimator/lwe_dual.py:607` calls Sage's `RealNumber.n(30)`, which the harness
shim does not provide, so `matzov` raises `AttributeError` — the same class of
harness gap BATCH-010 defect D4 found for `dual`/`primal_hybrid`. The script
rebinds **one name**, `estimator.lwe_dual.exp`, **inside its own process**;
`tools/sage_free_estimator` is not modified and nothing is written to it. The
patch's correctness is not assumed: CTRL-2, CTRL-3 and CTRL-4 test it from three
directions (H4, H5).

---

## 4. The decomposition

All values `log2(rop)`, `RC.MATZOV`, pin `3e48ef4`.

| stage | what changes | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|---|
| **S0** | `lwe_dual.dual_hybrid(fft=True)` — the EV-MLKEM-015 object | 143.788478 | 203.787863 | 273.817268 |
| **S1** | `lwe_dual.matzov` (= `LWE.dual_hybrid`) | 139.656041 | 196.366243 | 262.335680 |
| **S2** | + fine `(p, k_enum, k_fft, β)` grid (estimator uses step 10) | 139.356554 | 195.554189 | 262.000223 |
| **S3** | + optimise sample count `m` (estimator fixes `m = n`) | 139.321810 | 194.491769 | 260.004744 |
| **S4** | + explicit second block size `β_sieve` | 139.015882 | 194.491769 | 260.004744 |

### The named differences, sized in bits

| id | named modelling difference | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|---|
| **D1** | **attack-function identity** — `dual_hybrid(fft=True)` is the EspJouKha/GJ21 hybrid, not MATZOV Thm 7.6 | **+4.132437** | **+7.421620** | **+11.481588** |
| **D2** | **optimiser grid resolution** — `early_abort_range(..., 10)` searches `k_enum`, `k_fft` on a step-10 grid (`lwe_dual.py:657-658`) | +0.299487 | +0.812054 | +0.335457 |
| **D3** | **sample count not optimised** — `matzov` fixes `m = params.n` (`lwe_dual.py:583-584`); the published analyses optimise `m` | +0.034744 | +1.062420 | +1.995479 |
| **D4** | **explicit second block size** — `matzov.__call__` never passes `beta_sieve` | +0.305928 | 0.000000 | 0.000000 |
| | **total attributed** | **+4.772596** | **+9.296094** | **+13.812524** |

### The residual, stated explicitly

| comparison | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|
| total gap S0 − published (Carrier) | +4.288478 | +8.687863 | +14.117268 |
| **unattributed residual after D1 only** (S1 − Carrier) | **+0.156041** | **+1.266243** | **+2.635680** |
| **unattributed residual after D1–D4** (S4 − Carrier) | **−0.484118** | **−0.608231** | **+0.304744** |
| total gap S0 − published (MATZOV-2022) | +6.288478 | +10.287863 | +16.017268 |
| **unattributed residual after D1 only** (S1 − MATZOV) | **+2.156041** | **+2.866243** | **+4.535680** |
| **unattributed residual after D1–D4** (S4 − MATZOV) | **+1.515882** | **+0.991769** | **+2.204744** |

Two accountings are given deliberately, and neither is hidden:

- **After D1 only** — the honest *like-for-like* comparison, both sides at their
  own author's optimiser setting. Residual vs Carrier **+0.16 / +1.27 / +2.64**.
- **After D1–D4** — the estimator additionally re-optimised inside its own cost
  function. This **over-attributes** at Kyber-512 and Kyber-768: the residual goes
  **negative** (−0.48, −0.61), i.e. the re-optimised estimator is *cheaper* than
  Carrier's published figure. A negative residual is not a tighter explanation;
  it means the true attribution lies **between** the two rows. Stated rather than
  suppressed.

### The growth is gone

The Coordinator's scouting observed the gap growing superlinearly in β
(gap/β = 0.01067 / 0.01411 / 0.01632). This run reproduces those ratios exactly
(0.01067 / 0.01410 / 0.01632 at β = 402 / 616 / 865). After the decomposition:

| | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|
| gap/β before (β from S0) | 0.01067 | 0.01410 | 0.01632 |
| residual/β after D1 only (β from S1) | 0.00040 | 0.00215 | 0.00320 |
| residual/β after D1–D4 | −0.00125 | −0.00103 | +0.00037 |

The systematic, monotone, β-scaling component is entirely inside D1 and D3. What
is left brackets zero and does not scale.

### Independent convergence of the attack parameters

Not used in the arithmetic; recorded because it is the strongest non-numerical
corroboration available. Stage 3 was reached by minimising the estimator's cost
function, with no knowledge of Carrier's operating point:

| | β_bkz | β_sieve | m | cost |
|---|---|---|---|---|
| Kyber512 — estimator S3/S4 | 383–386 | 390 | 481 | 139.02–139.32 |
| Kyber512 — Carrier Table C.1 CC | 384 | 387 | 475 | `log2(Tsample)` 139.51 |
| Kyber768 — estimator S3 | 583 | 576 | 644 | 194.49 |
| Kyber768 — Carrier Table C.1 CC | 581 | 574 | 636 | `log2(Tsample)` 194.81 |
| Kyber1024 — estimator S3 | 816 | 797 | 814 | 260.00 |
| Kyber1024 — Carrier Table C.1 CC | 811 | 792 | 802 | `log2(Tsample)` 259.35 |

Carrier's columns come from the archived extract
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page37_tables_C1_C2.txt`
(CTRL-5). Three block sizes agreeing to within 3–5, three sample counts to within
6–12, and three costs to within 0.35–0.65 bits, from independent optimisations.

---

## 5. The other four hypotheses, each sized

### (1) Sieve cost model — sized, and it is *not* the explanation

`RC.MATZOV` subclasses `RC.GJ21` overriding **nothing but** the `NN_AGPS`
coefficient table (`reduction.py:963`), so `GJ21 − MATZOV` isolates MATZOV's
sieve gate-count revision exactly:

| | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|
| `matzov` under `RC.GJ21` | 145.211 | 202.913 | 268.582 |
| `matzov` under `RC.MATZOV` | 139.656 | 196.366 | 262.336 |
| **MATZOV sieve re-costing worth** | **5.5551** | **6.5465** | **6.2462** |

MATZOV's own archived text (`matzov_v2_loci.txt`, contribution 2) claims "the
cost of sieving is reduced by ≈ 6 bits in rank 400". Computed here: 5.56–6.55
bits at sieve dimensions 391 / 583 / 804. **The primary claim is reproduced.**
But both sides of the comparison already use it — Carrier states "in the same
nearest-neighbor cost model as in [SAB+20, MAT22]" — so it cancels and explains
none of the gap. Full 10-model sweep in `results.json → axis_A_...`;
`RC.Kyber` fails for `matzov` (`unexpected keyword argument 'sieve_dim'`) and is
recorded as a failure rather than dropped.

### (2) FFT / distinguisher accounting — this *is* inside D1, and part is unsized

The two functions differ structurally, not by a tuning constant:

| | `dual_hybrid(fft=True)` | `matzov` | Carrier CC (archived) |
|---|---|---|---|
| FFT modulus `p` | **2, hardcoded** (`size_fft = 2**t`) | optimised: **5 / 4 / 4** | not sourced (see H14) |
| guessed coords ζ / `k_enum` | 19 / 31 / 41 | 0 / 20 / 0 (S1) → 7 / 23 / 3 (S2) | `n_enu` 5 / 6 / 10 |
| FFT coords `t` / `k_fft` | 76 / 120 / 165 | 50 / 60 / 120 (S1) → 42 / 59 / 115 (S2) | `n_fft` 52 / 93 / 131 |
| sample count | 512 / 693 / 889 | 512 / 768 / 1024 (fixed at `n`) | 475 / 636 / 802 |
| `repetitions` | 1 / 1 / 1 | none — μ = 0.5 hardcoded in `Nf`, no outer repeat | `log2(R)` **9.39 / 9.49 / 15.15** |
| sample-count law | Independence Heuristic, `4·exp(4π²σ²)(log(2^t·size) − log log(1/prob))` | MATZOV p.29 `Nf`, "we're ignoring O()" | Theorem 4.1 (not archived) |

The distinguisher difference is *inside* D1 and is therefore sized as part of it.
What is **not** sized (H17): the repetition/success-probability bookkeeping.
Carrier carries an outer `log2(R)` of 9.39 / 9.49 / 15.15 that has **no
counterpart** in the estimator's MATZOV path, and μ = 0.5 is a hardcoded literal
inside `Nf`. Exposing either would change the frozen cost model, which the
executor contract forbids without an amendment. **Recorded as an unsized named
difference, not absorbed into the residual.**

### (3) Dimensions-for-free — sized, applied by both sides

| | with d4f | without d4f | **worth** | d4f(β*) |
|---|---|---|---|---|
| Kyber512 | 139.6560 | 147.6544 | **+7.9984** | 35.68 |
| Kyber768 | 196.3662 | 206.6718 | **+10.3055** | 47.86 |
| Kyber1024 | 262.3357 | 275.3269 | **+12.9912** | 61.10 |

Large — larger than the gap at Kyber-512 and Kyber-768 — and applied on **both**
sides, so it cancels. Estimator side: `RC.MATZOV` inherits `Kyber.d4f` through
`GJ21` and applies it at `reduction.py:903`. Published side: MATZOV's archived
contribution 3 states the BKZ phase "enjoys the so-called 'dimensions-for-free'
trick [Duc18]" and the final sieve runs "this time without using
dimensions-for-free ... we use a different block size for this task" — which is
precisely the estimator's β / β_sieve split, and precisely what Carrier's Table
C.1 prints as two separate columns.

### (4) Core-SVP vs gate counts — sized, and rejected

| | core-SVP (`RC.ADPS16`) | gates (`RC.MATZOV`) | units differ by |
|---|---|---|---|
| Kyber512 | 115.510 | 139.656 | 24.15 |
| Kyber768 | 174.324 | 196.366 | 22.04 |
| Kyber1024 | 241.756 | 262.336 | 20.58 |

A units mismatch would be a **20–24 bit** effect against a **4–14 bit** gap, and
it would *shrink* with parameter size while the observed gap *grows*. Both
primary sources declare gate-count units (MATZOV Table 1: "All of the costs are
log2 in the gate-count metric"; Carrier: "in the same nearest-neighbor cost
model as in [SAB+20,MAT22]"). **Falsified as an explanation, and sized.**

### (5) Archived Carrier extracts — what they let us check directly

- Table C.1 splits verified arithmetically on all nine rows (CTRL-5).
- Table C.2 CC `log2(Tsample)` dominates: summing all three C.2 terms gives
  139.510031 / 194.810446 / 259.350009, i.e. the sampling term carries the
  headline to within 3.1e-5 / 4.5e-4 / 9.2e-6 bits (H16). The estimator's
  `matzov` splits the same way (Kyber512: `red` 139.5466 vs `guess` 135.8809).
  So comparing totals compares like with like.
- **An internal discrepancy in the archived source, recorded not resolved:** that
  sum reproduces the Kyber-512 headline 139.5 to 0.0100 bits but sits 0.2896 /
  0.3500 bits *below* the 195.1 / 259.7 headlines. Table 5.1 itself is not in the
  archive. This is 0.29–0.35 bits of the residual that belongs to the source, not
  to the estimator.
- Carrier's `k_fft` column meaning is **explicitly marked unsourced** (H14). The
  offsets `log2(TFFT) − k_fft·log2 q` = 18.6921 / 19.3378 / 19.7734 are
  consistent with an FFT over `Z_q^{k_fft}`, but that is inference from archived
  numbers, not a quotation. Nothing in the decomposition depends on it.

---

## 6. Direction of the evidence

**The decomposition supports neither branch of the question as posed, because the
gap it was asked to explain is not evidence about the published analyses at all.**

Stated precisely:

1. **The recorded gap is dominated by the comparison object, not by a modelling
   disagreement.** D1 — a difference between two functions *inside the
   estimator*, only one of which implements MATZOV — is 96.4% / 85.4% / 81.3% of
   the total gap. It is also the entire source of the superlinear-in-β growth.

2. **The pinned public estimator does reproduce Carrier's published headline.**
   Like-for-like (S1 vs published): **+0.16 / +1.27 / +2.64 bits**. With the
   estimator's own optimiser slack relaxed inside the same cost function
   (S4): **−0.48 / −0.61 / +0.30 bits**. On the "the estimator is right, so the
   published headlines are optimistic" branch, this run finds **no support for
   Carrier being optimistic** — the estimator lands on the same number.

3. **A residual against MATZOV-2022 survives and is stated:** **+1.52 / +0.99 /
   +2.20 bits** unattributed after all four terms (**+2.16 / +2.87 / +4.54**
   like-for-like). Named unsized candidates in `heuristics.yaml`: H15 (the
   polar-code decoder and zero-secret iteration, not implemented in this
   instrument) and H17 (μ and the repetition count R). **This residual is not
   explained here.**

4. **What follows arithmetically, and what does not.** If Carrier's figures are
   right — and this run reproduces them in an independent instrument — then by
   H8's cutoffs they sit 3.5 / 11.9 / 12.3 bits below 143 / 207 / 272. The
   estimator's own re-optimised MATZOV figures give 3.98 / 12.51 / 12.00. **This
   is not an ML-KEM break claim and it is not a security claim.** It is one cost
   model, at one parameter set, for one attack family, under eighteen numbered
   heuristics of which H8, H10, H15 and H17 are unvalidated and H8 is
   *unverifiable in this environment* — the cutoffs themselves have never been
   read from primary NIST text by this program.

5. **Two-cost-models-agreeing is not validation of either.** The estimator's
   `matzov` implements MATZOV's `Nf` — the very sample-count law whose
   independence assumptions Ducas–Pulles (KN-LIT-111) argue are unsound, and
   which KN-OPEN-016 was opened over. Carrier's stated contribution is precisely
   to *avoid* those assumptions. That two analyses resting on different
   foundations land within a bit of each other is an observation, not a
   corroboration of the foundation. **KN-OPEN-016's actual question — whether the
   heuristics survive repair — is untouched by this batch.**

---

## 7. Observation flagged for the Coordinator, recorded not adjudicated

Under `RC.MATZOV` at the pin, `estimator.lwe_dual.matzov` is **cheaper** than
`primal_bdd` on all three sets:

| | `primal_bdd` (CTRL-1) | `matzov` S1 | primal − matzov | `matzov` S4 | primal − S4 |
|---|---|---|---|---|---|
| Kyber512 | 140.199473 | 139.656041 | **+0.543432** | 139.015882 | +1.183591 |
| Kyber768 | 200.958715 | 196.366243 | **+4.592472** | 194.491769 | +6.466946 |
| Kyber1024 | 270.723623 | 262.335680 | **+8.387943** | 260.004744 | +10.718879 |

EV-MLKEM-015 records "Dual does not beat primal (gaps +3.59 / +2.83 / +3.09
bits)". That statement is **true of the function it names** — `dual_hybrid+fft`,
which this run reproduces at 143.788478 / 203.787863 / 273.817268 — and the
observation above concerns a different function. **I do not assert that this
corrects, contradicts or qualifies EV-MLKEM-015, and I have not treated it as
doing so.** Whether it rises to a rule-12 "contradiction of established
evidence" is a Coordinator/Reviewer determination, not an executor's. It is
surfaced here because it bears directly on KN-OPEN-016's headline question and
because suppressing it would be the failure AGENTS.md rule 9 names.

---

## 8. What would settle what remains

1. **A Sage-computed reference for `matzov` at Kyber-768 and Kyber-1024.** CTRL-3
   covers Kyber-512 only, via the estimator's own committed doctests. The 768 and
   1024 `matzov` figures are an **uncovered path**. Cheapest route: run the
   estimator's own doctest suite under real Sage at the pin, or archive a Sage
   run of `LWE.estimate(schemes.Kyber768/1024)`.
2. **Size H17.** Expose μ in `Nf` and add an outer repetition factor, then sweep.
   This changes the frozen cost model and needs a Coordinator amendment; it is
   the largest *nameable* remaining term against MATZOV-2022.
3. **Reorder the stages** to bound H10: D2/D3/D4 are order-dependent, D1 and the
   total are not. One cheap re-run settles the share attribution.
4. **Globalise the stage-2/3 search.** The boxes are local (`p∈[2,8]`, `k_enum±8`,
   `k_fft±8`, `β±8`, `m∈[0.6n, n]`), so D2+D3+D4 *understates* estimator-side
   slack and the MATZOV-2022 residual is an **upper** bound.
5. **Recover Carrier's Table 5.1** into the archive. 0.29–0.35 bits of the
   Kyber-768/1024 residual is an internal difference between the archived Table
   C.2 and the abstract's headline, not an estimator/publication disagreement.
6. **The question KN-OPEN-016 actually asks** — whether the MATZOV-family success
   probabilities survive the Ducas–Pulles objection — is untouched here and needs
   distribution-level work at dimensions where the prediction can be checked.

---

## 9. Deviations from the task card

- The dispatch-queue handoff's `deliverables` and `completion_gate` blocks are
  **stale**: they name `memory_charged_derivation.py`, `derivation_report.md` and
  a critical memory exponent `c*`, which belong to BATCH-010's question. The same
  handoff's `objective`, its `artifact_paths`, and the Coordinator's launch
  message all specify the gap decomposition and the file names used here. I
  followed the objective and `artifact_paths`. `c*` is not applicable to a gap
  decomposition and was not computed; β and d are reported per set and agree with
  CTRL-1; the memory-unit gate item does not arise because **no memory figure is
  used anywhere in this package**.
- `experiments/EXP-MLKEM-015` was **not** re-run. As in BATCH-010 this is a
  derivation on a pinned instrument, and the EXP-MLKEM-015 baseline is
  **reproduced, not executed** (CTRL-1, delta 0.0).
- The repository `HEAD` moved from `75f6c8e0d749` to `428bb71364f0` mid-task (a
  merge of `origin/main` into the branch, not made by me). Verified before
  proceeding: `git diff` over `tools/sage_free_estimator` and
  `inputs/MLKEM-DUAL-SOURCES-20260802` between the two commits is **empty**, so
  neither the instrument nor the archived sources changed. Recorded in
  `receipt.json → anomalies`.
- Four exploratory instrument probes were run before the deliverable run; they
  are listed with their purpose in `receipt.json → exploratory_probes`. No number
  from a probe is reported anywhere except as reproduced inside the single
  deliverable run.
