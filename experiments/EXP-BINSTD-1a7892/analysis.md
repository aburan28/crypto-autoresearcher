# Analysis: EXP-BINSTD-1a7892 (H-BINSTD-6e3bd4)

Review plan: `experiments/EXP-BINSTD-1a7892/review/review-plan.yaml`
(`REVIEW-BINSTD-1a7892-20261001`), written before this analysis.
Producer: TASK-20261001-d6b2b5. Decision target: `replicate` preferred over
`support` for this first empirical OPEN/calibration package.

## Observation

**Validity (J1).** 31 run directories under `runs/`; execution_report lists the
same 31 completed IDs, `invalid: []`, `failed: []`. Every run has
`manifest.yaml`, `raw-result.json`, `environment.json`, `stdout.log`,
`stderr.log`, `command.txt`. All `valid: true`, `termination_reason:
completed`. Stage split: 1 Stage 0 (`RUN-BINSTD-e10267`), 1 Stage 1
(`RUN-BINSTD-e3a2f8`), 29 Stage 2 (20 Tk seeds + 5 null + 4 non-Tk). Within
`maximum_runs: 40`.

Stage 2 Tk cells: 5 seeds × g∈{2,4,6,8}. Per-seed `per_trial_xor_word_ops`
in manifests match `stage2/cost-vs-g-table.yaml` exactly; recomputed medians
291 / 9564 / 112776 / 661920 match the table. All 20 Tk decomposition
certificates have `kind: decomposition` and `verified: true`. Five null
runs report `null_reports_no_construction: true` and
`Tk_construction_possible: false`. Four non-Tk same-arity controls report
finite xor-word_ops at g=2,4,6,8 (one seed each, disclosed deviation).

**Stage 0 (J2).** Recomputed from formula+parameters alone (blind joint):

| k | g | naive_bits | rho_reg |
|---|---|------------|---------|
| 11 | 10 | 50.591061 | 0.625 |
| 13 | 12 | 58.168789 | 0.750 |
| 17 | 16 | 74.250140 | 1.000 |
| 19 | 18 | 82.729751 | 1.125 |
| 23 | 22 | 100.474588 | 1.375 |

All within ±0.5 bit / ±0.01 of frozen expectations. Dual rho margins present
with separate reused vs canonical columns; canonical margins ~0.2–0.3 bit
larger. `reachability-table-cell.yaml`: `verdict: OPEN`, named missing
quantity = per-trial decomposition/relation-solving cost at arity g∈{10..22}
over F₂¹⁶. `break_claim_filed: false`, `DEFINED_deployed_attack_cost_filed:
false`. T4 fields present on every naive_bits-bearing artifact. ECC2K-130
null note: prime n=131 ⇒ no T_k operational transfer. Corpus recheck: Stage 0
adds no arity≥4 deployed measured cost cell.

**Stage 1 (J3).** Gorla–Massierer iacr:2014/318 retrieved (`provenance:
retrieved`, `verified_by: executor`, PDF sha256 recorded). g=2: median solve
wall 0.001525 s; paper ~2q systems for q relations ⇒ trials/relation
calibration_ratio 1.0 vs H2 2!. g=4: median hybrid GB wall 1.29 s; full
arity-4 H2 wall ratio left `null` because paper uses JV arity-3 + hybrid —
`calibration_ratio_full_arity4_H2_reason` disclosed; overall
`g4_full_arity_H2_calibration: incomplete_due_to_JV_hybrid_implementation`.

**Stage 2 (J4).** Median xor_word_ops strictly increasing in g on the toy
ladder. Fitted law `log2(xor_word_ops)=a+b*g` with a≈5.13, b≈1.85,
rmse_log2≈0.62; `extrapolation_distance_to_g22=14`; modeled (not DEFINED)
log2 ops at g=22 ≈45.8. Truncation: Macaulay D≤3 with equation degree
clipped ≤2; full total_degree recorded under system_shape (4,32,192,1024).
Optimistic bias for attack cost disclosed. `DO3_surviving_margin_claimed:
false`. Certificate pass rate 1.0 by g.

**Protocol deviations (producer).** (1) Truncated dense F₂ Macaulay GE as
cost proxy, not full Gröbner. (2) non-Tk control: 1 seed per g (not 5).
(3) Stage 1 g=4 vs H2 4! calibration incomplete (JV+hybrid).

## Comparison

- Matches preregistered Stage 0 predictions for naive_bits, rho_reg, dual
  margins direction, and OPEN cell (DO-1 arithmetic half).
- Stage 1 g=2 probability factor near H2; does **not** match a full g=4
  H2-only wall prediction because the literature object differs (JV/hybrid) —
  correctly left incomplete rather than forced.
- Stage 2 growth direction matches the a priori “cost increases in g”
  prediction under the **proxy instrument**; absolute levels are not
  comparable to Gorla–Massierer Magma wall seconds (different cost unit and
  truncation).
- Non-Tk xor-word_ops track Tk-shaped proxy closely (272 vs 291 at g=2;
  659296 vs 661920 at g=8), consistent with an arity-/matrix-size-driven
  instrument rather than a T_k-polynomial-specific signal.
- Null / ECC2K-130 objects behave as required (no finite T_k cost).

## Inference

Within the tested scope, the producer package supports the hypothesis’s
**table-correctness** claim: Arm B naive charged numbers at the five ANSI
c2pnb* rows are arithmetically reproducible, rho_reg≥1 at 3/5 rows, and the
reachability cell remains **OPEN** with the per-trial arity-10–22 solving
cost named — not DEFINED, not a break. Stage 2 shows rapid growth of a
**truncated Macaulay xor-word-ops proxy** at g≤8 with stated extrapolation
distance 14 to g=22; that is consistent with a large missing per-trial
quantity but is **not** a deployed attack-cost model and must not be read as
one. Stage 1 upgrades Gorla–Massierer to retrieved and calibrates only the
g=2 probability half near 1; (D) is not discharged at deployed arity.

Distinguishable outcome: **DO-1-open-confirmed** (arithmetic + OPEN), with
Stage 2 proxy growth as supporting flavor under disclosed instrument limits —
not DO-2 promotion to DEFINED, not DO-3 break-adjacent surviving margin.

**Decision implication (pre-registered preference):** `replicate`, evidence
strength `preliminary`. Do **not** `support`. Do **not** file DEFINED
deployed cost. Hypothesis → `analyzed`.

## Limitation

- Stage 2 cost is a truncated Macaulay GE proxy (D≤3); full Gröbner
  total_degree grows to 1024 at g=8 — proxy **understates** true solving
  cost (optimistic for any attack reading).
- Toy ladder only: g≤8 vs deployed g up to 22; extrapolation distance 14;
  fitted law is modeled, not validated at target scale.
- non-Tk controls undersampled (1 seed/g vs protocol ≥5).
- g=4 H2 full-arity wall calibration incomplete by literature object mismatch.
- Run tree recorded `code.dirty: true` at producer commit; implementation
  later bound via execution_report `implementation_commit`.
- No independent validator/red-team session in this round (review-plan PD-1);
  a later support / DEFINED / DO-3 reading requires review-adversarial or
  review-breakthrough as applicable.
- ECC2K-130: methodological null only; zero operational transfer.
- Claim tier for empirical Stage 2 growth: **toy**. Stage 0 is arithmetic on
  crypto-parameter identities, not a crypto-scale attack measurement.
