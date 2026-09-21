# EXP-SCR-003 analysis (Executor, observations only)

This record separates observation, comparison, inference, and limitation per
docs/task-lifecycle.md §8. The Executor records no conclusion on H-SCR-003;
evidence strength and any state transition belong to Coordinator review.

## 1. Observation — what was measured

Planned runs (replication.planned_runs, expected_run_count 3), plus one
recorded repair re-execution:

| run | stage | terminal status | outcome |
|---|---|---|---|
| RUN-SCR-003-A | freeze_and_calibrate | failed_implementation | KeyError 'calibration_fixtures' in the screen's fixture loader before calibration executed; corpus manifest (30/30 pass) had been materialized. Preserved unmodified; implementation_error, evidence for nothing. |
| RUN-SCR-003-A-b | freeze_and_calibrate (repair of RUN-SCR-003-A) | completed_valid | Corpus 30/30 paths verified at pinned commit b8af1551 (zero missing, zero mismatches); calibration 3/3: CAL-PASS-SCR-003 → ADMIT, CAL-FAIL-SCR-003 → simulable_closed, CAL-SPLIT-SCR-003 → separation_certified at N3 (ε = 1) + N4 rejected. |
| RUN-SCR-003-B | dedup_classification | completed_valid | 8/8 families assigned a dedup class with a verified named owner; zero undecidable. |
| RUN-SCR-003-C | ns_tx_application_and_aggregate | completed_valid | N1–N5 applied to all 8 families; replay pass byte-identical (CTRL-REPLAY-DETERMINISM); split-gate tail checks pass; 4 residuals carried unscored; family_table.json and admission_decision.json emitted. |

Family table (family_table.json; admitted_family_count = 0):

| family | dedup class | separation verdict (N1–N3) | usefulness verdict (N4–N5) |
|---|---|---|---|
| F1 higher_order_public_equation_jets | prior_audited (THM-JETBARRIER1 T2/T4) | simulable_closed | not_scored_family_closed_by_dedup |
| F2 public_affine_or_algebraically_constrained_lifts | prior_audited (THM-JETBARRIER1 T1.3/T4) | simulable_closed | not_scored_family_closed_by_dedup |
| F3 finite_additive_formal_Witt_or_arithmetic_jet_targets | prior_audited (P1547, additive channel only) | simulable_closed | not_scored_family_closed_by_dedup |
| F4 nonadditive_lift_invariant_point_constraint | uninstantiated_residual (P1547 unclassified possibility) | separation_not_certified (N1 cannot_apply_without_oracle) | not_scored_no_oracle |
| F5 composite_handle_coordinate_oracle | model_seam_not_new_family (THM-JETBARRIER1 T6) | encoding_only_gap (not source-bearing) | fail_n4_raw_coordinate |
| F6 Weil_restriction_or_descent_jet | outside_prime_field_scope (G2 seam) | out_of_scope_not_scored | out_of_scope_not_scored |
| F7 Hasse_jet_multiplicity_code | prior_rejected_not_remaining (ECDLP-IDEA-268) | closed_by_prior_rejection (N1 hidden source-bearing advice) | not_scored_prior_rejection |
| F8 other_finding_representation_screens | prior_audited_not_reopened (FINDING-PF-IC-001, EV-EQJ-001, EV-TTN-001) | simulable_closed | not_scored_family_closed_by_dedup |

Per-class tally: prior_audited 3 (F1–F3), prior_audited_not_reopened 1 (F8),
prior_rejected_not_remaining 1 (F7), uninstantiated_residual 1 (F4),
model_seam_not_new_family 1 (F5), outside_prime_field_scope 1 (F6).
Residuals carried unscored: RESIDUAL-NONADDITIVE-TYPED-INVARIANT
(logical_placeholder_not_family), RESIDUAL-GGM-META-COMPLETENESS
(open_model_theory_not_candidate), RESIDUAL-DESCENT-G2
(extension_field_scope), RESIDUAL-CONCRETE-COORDINATE-ALGORITHM
(umbrella_open_problem). Falsification-class observations: none — no family
passed N1–N5 with a source-bearing transcript gap and complete charged
ledger.

## 2. Comparison — against the predefined controls

- CTRL-CORPUS-INTEGRITY: pass — 30/30 pinned blob SHA-1 matches, zero
  missing, zero SHA-256 drift (re-verified independently in all three valid
  runs; B and C re-bound to RUN-A's manifest).
- CTRL-SHEET-CALIBRATION: pass — 3/3 fixtures received their pre-declared
  verdicts before any corpus family was adjudicated (accuracy 1.0).
- CTRL-DEDUP-PRIOR-NEGATIVES: pass — 8/8 families carry a dedup class and
  named owner verified against the pinned corpus.
- CTRL-REPLAY-DETERMINISM: pass — two full screen passes produced
  byte-identical family tables (sha256 recorded in family_table.json).
- Tail checks: pass — no family recorded simulable from a usefulness failure;
  the F5 encoding_only_gap is recorded as non-source-bearing; zero verdict
  flips between passes.
- Pre-declared secondary expectations matched: encoding_only_gap flag = F5;
  separation_not_certified = F4 (cannot_apply_without_oracle);
  undecidable_items = 0; corpus_hash_mismatch_count = 0.

## 3. Inference — explanations compatible with the result

Deferred to Coordinator review. The Executor notes only what the instrument
did: the frozen screen, applied mechanically to the frozen corpus, emitted a
complete 8-family table with zero admitted families and 3/3 calibration. Per
AGENTS.md rule 6, a zero-admitted table can close only the exact checked
scope; per the spec's claim_tier_basis it is neither a universal
simulability theorem nor GGM completeness. Whether this observation supports,
weakens, or leaves H-SCR-003 unchanged is a Coordinator decision.

## 4. Limitation — what this experiment cannot establish

- Scope is the checked frozen representation corpus at pinned commit
  b8af1551; families outside the 8 frozen items, and any future
  representation, are untouched.
- The screen is as strong as its pinned owner records; it re-verifies their
  presence and tokens, not their proofs.
- F4 remains an uninstantiated residual (no oracle to test); F6 is outside
  prime-field scope; the 4 residuals are carried unscored.
- Toy claim tier: no medium- or cryptographic-scale claim in either
  direction.
- RUN-SCR-003-A's failed_implementation is an implementation event, not
  evidence about the hypothesis in either direction.
