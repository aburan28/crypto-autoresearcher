# Technical review: TASK-20260724-224 / EXP-MLKEM-001 / H-MLKEM-001

Independent Reviewer challenge of outcome classification and claim boundary.
Official state is unchanged here.

## Scope and authority

This review covers only the mathematical classification of `EXP-MLKEM-001` and
the scoped implication for `H-MLKEM-001`. Validator task `TASK-20260724-223`
already admitted the run package (`accept_with_qualifications`). Integrity is
taken as admissible; interpretation is not.

Inference: requested `review-xhigh`, resolved `cursor-grok-4.5-high`,
`fallback_used: true` per coordinator amendment.

## Reported classification

Executor / execution report:

- **Primary:** `implementation_mismatch`
- **Key localization:** pinned no-compression pairing uses
  `B1 = CBD(ke) * CBD(ks)` rather than algebraic `e * y` with `y ~ CBD(ke_ct)`
- **Aligned float residual:** `max_abs_delta ≈ 4.16e-17`
- **Algebraic float residual (pointwise):** `max_abs_delta ≈ 0.0107`
- **Secondary:** paper-scale artifact; joint-dependence union slack;
  six FIPS ties-up vs Python half-even decompress mismatches
- **Not claimed:** `exact_marginal_discrepancy`
- **Not tested:** `n = 256`; listed FIPS rare-event exponents

## Challenge 1 — Is `implementation_mismatch` the right primary label?

**Verdict: yes under frozen precedence; no as a standalone reading of H.**

The specification orders outcomes:

1. `invalid_control_or_port`
2. `implementation_mismatch`
3. `exact_marginal_discrepancy`
4. `joint_dependence_only`
5. `paper_scale_artifact`

Any positive pairing TV or tie-mismatch count forces primary
`implementation_mismatch`. That rule fired correctly:

- Exact Fraction TV between algebraic FIPS pairing and the estimator-aligned
  pairing is **nonzero only for ML-KEM-512 toys** (`eta1 = 3 ≠ eta2 = 2`),
  about **0.046** at `(n,k)=(2,2)` up to about **0.053** at `(8,4)`.
- For ML-KEM-768/1024 toys (`eta1 = eta2 = 2`) that TV is **exactly 0**.
- After pairing alignment, float comparison to the faithful port has
  `mismatch_count_aligned = 0` and machine-epsilon `max_abs_delta`.
- Decompress tie tables contribute exactly six FIPS-vs-Python mismatches.

Two reading errors must be blocked:

1. **Not a port-fidelity failure.** `CTRL-PORT-FIDELITY` passed
   (`source_vs_port max_abs_delta = 0`). The pairing lives in pinned
   `Kyber_failure.py` (`B1 = law_product(chie_pk, chiRs)` with
   `chie_pk ~ CBD(ke)`, `chiRs ~ CBD(ks)` when rounding is trivialized). The
   port reproduces it. Classification localizes a **baseline model convention**
   relative to algebraic `e*y`, not a non-faithful port.
2. **Not H-falsification.** Hypothesis `implementation_mismatch` and the
   experiment success criterion both treat semantic/port-local gaps as
   comparison repairs that must **not** be attributed to Thorns. After
   alignment, the H-relevant residue is zero aligned no-compression marginal
   gap plus the compatible secondary signals.

So: accept the primary label; require evidence/decision prose to lead with the
aligned residue, not with “mismatch” as if the audit failed.

## Challenge 2 — Metric boundary (delta vs TV)

`RUN-MLKEM-004` summary reports `algebraic_no_compression_float_tv_max =
0.010685…`. That field is the **maximum absolute pointwise mass delta** from
float support comparison, **not** total variation.

Exact TV is already in `RUN-MLKEM-002` as
`tv_algebraic_vs_estimator_pairing` (Fraction strings). On ML-KEM-512 toys that
TV is ~0.046–0.053. Reviewer objection `OBJ-224-02`: do not understate the
pairing gap by quoting only the pointwise delta, and do not call either quantity
an aligned residual.

Aligned residual remains ~`1e-17` float presentation noise with zero
mismatches at `atol = 1e-12`. That is enough to reject
`exact_marginal_discrepancy` for **no-compression** toys; it is not a rational
bit-identical certificate against the float estimator table, and need not be
oversold as one.

## Challenge 3 — Do secondary signals survive?

**Paper-scale artifact:** confirmed. Ratios are exactly `4/sigma^2`
(`4`, `1`, `0.04` at `sigma ∈ {1,2,10}`). Equal-moment surrogate changes frozen
tail order at `sigma ∈ {1,10}`. No FIPS inference follows (`KN-LIT-080` already
flagged this).

**Joint dependence / union slack:** confirmed. At `n=2,k=1,eta1=eta2=2`,
`nontrivial_indep_gap` is true and `all_union_ok` holds at all 19 thresholds
(`0 ≤ P(any) ≤ n·p`). Independence formula `1-(1-p)^n` remains a labeled
negative control. This matches `joint_dependence_only` and does **not** attack
the estimator’s final `n·p` union step.

**LDP repair:** derivation artifact asserts speed-`R` rate preservation under
the outward center shift. Validator did not re-prove it; Reviewer accepts it as
a local Gaussian repair claim only—no CBD/FIPS transfer.

## Challenge 4 — Compressed scalar and `exact_marginal_discrepancy`

Falsification of H’s no-marginal-gap prediction inside this protocol requires a
**strictly positive aligned compressed-scalar TV** that survives FIPS ties,
representatives, both exact engines, and port fidelity.

What was actually emitted:

- Exact engines agree on no-compression laws.
- `n=1` compressed scalar: `identity_failures = 0`,
  `failure_probability = 0` for all three families and both messages.
- **No** compressed-scalar TV versus the estimator adaptation appears in
  run summaries.

Therefore:

- Claiming `exact_marginal_discrepancy` would be **unsupported**.
- Claiming the compressed half of the success criterion is **fully closed**
  would also be **overreach**. Zero failure indicators at `n=1` are expected
  and non-discriminative; they do not prove estimator agreement on the full
  compressed noise law.

Reviewer position: **no discrepancy claimed and none evidenced** →
non-falsification within tested compressed controls; leave compressed
estimator-TV as an optional narrow follow-up, not as a reason to weaken H.

## Challenge 5 — Claim boundary (toy ≠ crypto-scale)

Hard exclusions held:

- `n=256` not executed
- no Monte Carlo / rare-event estimation of `2^-138.8`, `2^-164.8`, `2^-174.8`
- no deploy, oracle, or key-recovery surface

Nothing in the package authorizes revising FIPS 203 rates. Thorns
(`KN-LIT-080` / ePrint 2026/1022) remains a correlation-modeling lead with a
confirmed printed scale artifact and a locally repairable LDP gap; it does not
become an exact ML-KEM marginal theorem via these toys.

## H-MLKEM-001 recommendation

**`supported_within_toy_boundary`**

| Prediction | Status |
|---|---|
| Surrogate/product second-moment ratio `4/sigma^2` | Confirmed |
| Repaired LDP rate `I(u)=c*(‖u‖_1-1)` | Confirmed in derivation artifact |
| Aligned no-compression one-coordinate TV = 0 | Confirmed at float presentation tolerance after pairing alignment |
| Joint event ≠ independence formula; `P(any)≤n·p` | Confirmed |
| Aligned compressed scalar TV vs estimator = 0 unless gap survives | Not falsified; estimator TV not emitted |

Compatible experiment language: paper-scale artifact and joint-dependence-only
findings are explicitly allowed alongside scoped support. The primary
`implementation_mismatch` label records comparison repair, then yields to that
support reading.

Not chosen:

- **`weakened` / `reject_scoped`:** no surviving aligned no-compression
  marginal gap; no compressed exact_marginal_discrepancy artifact.
- **`inconclusive`:** core no-compression and scale/joint predictions are
  determinate after alignment.
- **`refine`:** optional compressed-TV emission is hygiene, not a blocker for
  the tested no-compression claim tier.

## Required followups (non-blocking for scoped support)

1. When drafting EV/DEC, separate mismatch localization from aligned support
   signals and cite `RUN-MLKEM-00{1,2,3,4}` with exact TV fractions.
2. Optional tiny follow-up: emit exact compressed-scalar TV vs FIPS-aligned
   estimator adaptation at `n=1` only—if compressed closure is desired at
   claim-tier strength.
3. Do **not** expand to `n=256`, FIPS DFR revision, or attack claims from this
   experiment.

## Receipt summary

- Outcome class: **accept** `implementation_mismatch` (precedence-correct;
  reading-qualified).
- H-MLKEM-001: **`supported_within_toy_boundary`**.
- FIPS rates: **unchanged**.
- `n=256`: **not tested**.
