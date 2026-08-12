# EXP-SCR-002 analysis (Executor observations only)

Scope: lifecycle step-8 separation for the Executor package. Observations
only — no conclusion that H-SCR-002 is supported or refuted; evidence-strength
assignment and any status transition belong to the Coordinator under
independent review. Claim tier: toy (static audit; authorizes no medium or
cryptographic claim in either direction).

## 1. Observation (what was measured)

- **Corpus integrity (RUN-SCR-002-A).** 23/23 pinned corpus paths verified at
  commit `b8af1551e45fbe4435745239d29f4d141eea3356` by git blob SHA-1, with
  SHA-256 recorded per file in `corpus_manifest.json`. Zero missing, zero
  mismatches.
- **Calibration (RUN-SCR-002-A, before any corpus verdict).**
  CAL-PASS-SCR-002 received ADMIT with recomputed symbolic aggregates
  (c_rel = 3/10, L_rel = 2/5, tau = 1/4, lambda = mu = 11/25 = 0.44) matching
  its declared terms; CAL-FAIL-SCR-002 (the real I5 record) failed at
  requirement_1 with R2 `fail_independently`. Accuracy 2/2.
- **Threshold recomputation (RUN-SCR-002-A, re-asserted in RUN-SCR-002-C).**
  The four frozen identities recompute exactly at beta = 1/5:
  B^(9/4) = N^(9/20) = 0.45, B^(5/2) = N^(1/2) = 0.50, B^3 = N^(3/5) = 0.60,
  B^(5/4) = N^(1/4) = 0.25; the pinned derivation text and the pinned
  `current_explicit_control` exponents match the recomputation. The named
  explicit control (I7) aggregates: lambda >= 3/5, mu = 3/5 (materialized),
  tau = 3/5 — failing R6 (tau > 1/4) and R7 (lambda, mu > 9/20) with
  certifiable work exponent at least 0.60.
- **Requirement matrix (RUN-SCR-002-B R1–R4 + RUN-SCR-002-C R5–R7).**
  Complete 7×7 = 49 cells over items I1–I7:
  R1 `fail` × 7; R2–R7 `fail_independently` × 7 each; zero `pass`; zero
  undecidable. First failure is
  `requirement_1_explicit_semantically_distinct_operation` for all 7 items.
- **Admissibility tally.** admissible_operation_count = 0. No falsification-
  class observation (no item passed R1–R7); the
  `falsification_observations` list in `admission_decision.json` is empty.
- **Dedup.** Rejection-basis coverage 1.0: every rejected item's named basis
  matches the frozen `audit_item_index` expected basis and the pinned
  BATCH-006 excluded_nonconstructors disposition (I1 hidden_input; I2
  renamed_IDEA-20260723-001_interface incl. the EV-CRYPTO-002 z_R closure; I3
  free_oracle; I4 target_dependent_leakage; I5
  exact_predicate_for_supplied_sources_not_a_locator; I6
  explicit_generic_baseline_not_semantically_distinct_costs_B3) or the named
  explicit control (I7 work_and_memory_exponent_0.60_fresh_query_0.60), with
  named owners on all.
- **Determinism replay (RUN-SCR-002-C).** Pass 1 (merged B+C cells) and pass 2
  (fresh full application) produced byte-identical matrix payloads
  (SHA-256 recorded in `requirement_matrix.json`); zero verdict flips.
- **Unknown exponent terms.** I1–I6: 20/20 cost terms unassigned (each an
  admission failure, never zero). I7: 15/20 unassigned; only stage-level
  exponents are pinned (a = a_m = 0.40, ell = 0.40 conditioned, ell_m = 0.20,
  r = 0 credited, eta_rank unknown).
- **Interval check.** No item scored lambda or mu in (0.45, 0.50]; the rule
  (any such score fails R7 explicitly) is recorded in the matrix.
- **Resources.** Wall 0.597 / 0.840 / 1.113 s; CPU 0.454 / 0.588 / 0.841 s;
  peak RSS 31.0 / 31.5 / 31.6 MB — far inside the 1800 s / 4 GB / 3-run
  budgets.

## 2. Comparison (against the frozen prediction and controls)

- The frozen preregistered prediction (`admissible_operation_count` = 0 with
  first failure at requirement_1) matches the observed matrix exactly: zero
  admissible, requirement_1 first failure on all 7 items.
- All five frozen controls passed in every run: CTRL-CORPUS-INTEGRITY,
  CTRL-SHEET-CALIBRATION (2/2), CTRL-THRESHOLD-RECOMPUTATION,
  CTRL-DEDUP-PRIOR-NEGATIVES (1.0), CTRL-REPLAY-DETERMINISM (byte-identical).
- The per-requirement dispositions match the pinned BATCH-006 producer record
  and the pinned RT-20260723-603 independent review: R1 fail, R2–R7
  fail_independently over the checked material.

## 3. Inference (explanations compatible with the result)

Recorded without adoption: (i) the checked SOURCE-LOCATOR-OPEN interface
material contains no typed operation in the sheet's sense, so every item
fails at R1 with the rest failing independently; (ii) the named explicit
control (I7) independently fails the simulator, replay, rank, charging,
fresh-query, and threshold gates with certifiable 0.60 exponents. The
Executor assigns no evidence strength and selects no transition.

## 4. Limitation (what this experiment cannot establish)

- Scoped sheet outcome over the frozen 7-item index and pinned snapshot only;
  per AGENTS.md rule 6 the zero-admissible matrix closes only the exact
  checked scope and proves no lower bound (no unrestricted GGM, arithmetic-
  circuit, incidence, kSUM, or ECDLP lower bound; no exclusion of future
  coordinate-sensitive locators outside the checked interfaces).
- Toy-tier static audit: no curve arithmetic, sampling, or cryptographic-scale
  computation was performed; nothing herein is medium- or crypto-scale
  evidence in either direction.
- The named control's N^0.60 is its complete measured cost, not a universal
  0.60 lower bound for every possible source-faithful algorithm (wording
  guard from RT-20260723-603, carried forward).
- A synthetic fixture ADMIT (CAL-PASS-SCR-002) proves only that the
  instrumented sheet can emit ADMIT; it is excluded from the corpus matrix
  and is not evidence about H-SCR-002.

## Anomalies and unexpected observations

- Pinned `knowledge/INDEX.md` at the frozen commit contains unresolved git
  merge-conflict markers (`<<<<<<<`). No sheet check reads INDEX.md (the
  frozen item list is the specification's `audit_item_index`); no verdict is
  affected. Recorded per rule 8.
- No corpus item required judgement beyond the mechanical sheet: every
  grounding check resolved pass/fail from pinned bytes; zero items received
  `undecidable_with_reason`.
- Worktree dirty basis: tracked modifications at run time were exclusively
  `._` AppleDouble exFAT artifacts; disclosed in every manifest.
- Protocol deviations DEV-1 (dual artifact naming sets, byte-identical) and
  DEV-2 (post-hoc memory enforcement on darwin) are recorded in
  `implementation.md` and the execution report.
