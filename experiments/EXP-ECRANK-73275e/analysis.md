# EXP-ECRANK-73275e — Analysis (TASK-20260908-42eb79, REVIEW-PLAN-BATCH-24d356)

Composed 2026-09-08 by the Coordinator from: execution-report.yaml (producer,
observations only), the frozen blind re-derivation
(reviews/TASK-20260908-6f37e1/blind-rederivation.yaml, derivation frozen at
19709ca8b4 before any producer read), the validator report
(reviews/TASK-20260908-96178a/validation-report.yaml, J2+J3), and the red-team
report (reviews/TASK-20260908-b687fd/red-team-report.yaml, J1+J4). Sections
are strictly separated per docs/task-lifecycle.md.

## Observation

Recorded facts, each quoted from a named artifact (no interpretation):

- **Audit (R1/R2).** In-box fraction 24/24 = 1.000 across AT-0/1/2; planted
  meets 3/3/4 against expected 5.0 (N_a = 8000, |S| = 1600); reconstruction
  replay bit-identical; R1 synthetic 2-D known-answer case met exactly 5;
  plants (7,8), (11,12), (13,14) distinct, h0 7/11/13, no shared h0.
- **Construction n=6 (R3/R4).** found = 28 certified instances over 10^4
  b-tuples; feasible_tuples = 20 (feasibility fraction 0.002); counts_per_H
  {10^2: 15, 10^3: 22, 10^4: 28} (cumulative, r_height = max |numerator| of
  the g(b) vector — verified as the convention across all 28 entries);
  near_miss_total = 0; ops 9,191,003 (< 1.0e8 cap); R4 replay found[]
  bit-identical (sha256 e3c7cf49…90d92c7), ops equal; R4 re-derives from the
  frozen seed via construct_arm and reads R3's raw only post-hoc for the iv2
  flags (validator J3.3).
- **Construction n=8 (R5).** found = 0; exhaustion {kind: counted_ops_cap,
  ops: 100,002,120, b_index: 666}; ops_cap_respected = false (PD-2);
  enumeration used the integer (a,b) box of width min(H,20), not the full
  rational height-H lattice (PD-3, implementation.md IC-732-3).
- **Controls.** R6 null: found exactly [] (PD-1: null_proof_first overwritten
  in raw; frozen proof in source/null_family.py). R7 known-false d=(1..1):
  n=6 built = false on all 8 tuples (degenerate_deg_s_2); n=8 aggregate
  totals [5,6,7,7,7,7,6,7] vs expected 7. R8 planted: 0 of 9 plants built
  (degenerate_deg_s_2); recovered 0/0.
- **Provenance.** Executor resolved cursor-grok-4.6, fallback_used true,
  model_verified false; git_dirty_at_runs true at 5b83fed02e (dirty state was
  untracked outputs only; the 8 source files are content-hash-bound by per-run
  manifests, identical across runs/commit/worktree/snapshot; validator J3.6).
  Run package: 60/60 snapshot-receipt paths hash-verify at HEAD and at
  snapshot commit 03c6e3181b (content_first; validator J3.1).

## Comparison

Independent recomputation against the frozen contract and prior records:

- **Blind re-derivation (frozen before any producer read).** Q1: for
  b = (0,1,7,−14,16,−2), d = (−2310,30030,30030,−286,−286,−2310), the x^5
  ellipticity condition is genuinely quadratic in c with exact roots
  c = −28/13 and c = 324772/376343; both nondegenerate (deg s = 4,
  disc ≠ 0). The producer's b_index-579 instance matches the root −28/13
  exactly (delta, deg_s, disc_s, s, full r vector). r_height = 210 is the
  max |numerator| of g(b), a labeling convention, not the height of c.
  Q2: E = 8000/1600 = 5 exactly; Binomial sd ≈ 2.2354; P(meets ≤ 3) ≈ 0.2649
  — observed 3/3/4 consistent (z = −0.895/−0.895/−0.447). Verdicts: q1 holds,
  q2 holds.
- **Validator (J2 holds, J3 holds).** All audit quantities reproduce from the
  predecessor committed bytes at a20a49b6a; audit strictly precedes
  construction (R2 finished 16:30:08.119 < R3 started 16:30:08.122); all 28
  certificates pass direct exact rechecks (s(b_i) = d_i·g(b_i)^2 ∀i, deg s = 4,
  recomputed discriminant = recorded disc_s, g(b_i) ≠ 0, class keys); the
  committed certifier reproduces aggregate_total exactly on 5 spot instances
  (6,2,2,6,6). Three minor documentation findings (F-J3-1 near-miss ledger
  semantics narrower than a literal spec reading; F-J3-2 an implementation.md
  "recorded in every R5 raw" claim not literally present; F-J3-3 the IV-8
  statement lives in the execution report, not the R3 raw).
- **Red team (J1 holds, J4 breaks).** Exact derivation from the M2 statement:
  the d=(1..1) control object has deg s = 2 at n=6 on ALL 8 R7 tuples (conic,
  genus 0 — NOT elliptic; nonzero x² coefficients computed per tuple) and
  deg s = 3 at n=8 (elliptic). The n=8 shortfalls localize to F_l-certifier
  lower-bound limits (prime bound 1500): b_index 0 certifies 5/8, b_index 1
  and 6 certify 6/8; an independent reproduction with the committed certifier
  matches the recorded totals 8/8; the closed form supports 7 on all three.
- **Against the frozen success criterion.** G1 (M-A): satisfied at the tested
  scope. G2 (M-B): N_6(10^4) = 28 ≥ 1 with the IV-8 clause satisfied via the
  explicit untested statement (coverage single-class, all 28 are 3-class).
  G3: N_8 reported at its own scope (zero, cap-limited, box-narrowed).
  G4: R7/R8 did not pass their pre-registered checks AS WRITTEN.
- **Against HEUR-1 (carried, construction-side).** The recorded H-decade
  ratios of N_6 are 22/15 ≈ 1.47 and 28/22 ≈ 1.27 (two-decade total 28/15
  ≈ 1.87) against the exponent-+2 prediction of ×100 per decade. The
  execution report did not report these ratios (a frozen tail_check); they
  are computed here from counts_per_H. NOT reconciled: either the r_height
  convention measures something other than HEUR-1's H, or the construction-
  side realization of HEUR-1 is orders of magnitude below prediction at the
  tested scale.
- **Against the draw-route wall (EV-ECRANK-8b35bb).** Measured construction
  incidence 28/10^4 = 2.8e-3 per b-tuple vs the recorded draw-route bound
  3e-4 per b-tuple at n=8 (the obstruction block's units are per b-tuple;
  red-team J4d): a valid same-units comparison ABOVE the bound, with the
  different-n caveat disclosed (measurement at n=6, bound measured at n=8).

## Inference

Coordinator inferences from the comparisons above (each labeled with what
licenses it):

1. **The predecessor zero is attributed to square-pattern incidence density,
   not sampler geometry, at the audited scope** (G1 satisfied; IV-5/IV-7/IV-9
   passed; audit arithmetic independently derived twice). This discharges the
   J4-F3 route of the predecessor's review round at the tested scope.
2. **The R7/R8 control failures are CONTRACT-DESIGN DEFECTS, not
   implementation defects** (red-team J1 exact derivation): at n=6 the
   d=(1..1) control objects are conics, so degenerate_deg_s_2 is the correct
   rejection and the expected certified total 5 was unsatisfiable through any
   pipeline enforcing deg s ∈ {3,4}; at n=8 the objects are elliptic and all
   shortfalls are certifier lower-bound limits consistent with the closed
   form. The pipeline and solver behaved correctly on every control.
3. **Invalidation adjudication (IV-1/F4 textual conflict).** Reading A (IV-1
   literal, "voids ALL runs") proves too much — it voids runs whose checks
   passed (R1/R2/R4/R6) without textual warrant (red-team J4c). Reading B
   (F4, pipeline-defect premise) has a false premise. **Reading C is ADOPTED**
   (F4 with the contract-design-defect premise): no run is "affected" in the
   sense F4 names, so no run is voided; all eight survive as measurements.
   This resolution is a Coordinator ruling on a frozen-contract textual
   conflict, recorded here and in DEC-20260908-d361ab; it re-scores no run
   and edits no protocol field — the successor contract repairs the control
   expectations by versioned amendment.
4. **The construction route is validated in the EXISTENCE sense at n=6 at the
   tested scope**: 28 certified instances, every certificate exactly
   rechecked, one instance blind re-derived from the mechanism statement
   alone. The "too sparse to construct" reading of the measured obstruction
   is falsified at this scope (the resource_check reading of EV-ECRANK-8b35bb
   is vindicated for existence).
5. **The n=6 solver's DETECTION path is unvalidated** (red-team J4a breaks):
   R8's plants were the non-elliptic d=(1..1) family, so no planted elliptic
   control ever exercised detection; counts are therefore LOWER BOUNDS
   (completeness unmeasured). R3's found instances are unaffected (validated
   by certification, not by detection).
6. **The n=8 zero is inert in both directions** (stopping_rules): cap breach
   (PD-2) plus box narrowing (PD-3) make it an incomplete scan under a
   narrowed convention — neither evidence of absence nor a falsification
   (F3_n8 did not fire: no infeasibility pattern recorded).
7. **HEUR-1's construction-side count law is NOT confirmed and is in tension
   with the recorded decade ratios** (1.47/1.27 vs ×100/decade) under the
   recorded height convention; the convention mismatch must be reconciled
   before any count-law reading. F2_n6 did not fire (instances found), so
   nothing is falsified; the law simply stands unvalidated with a recorded
   tension.

## Limitation

- Toy tier throughout (contract's own scale_relevance): n ∈ {6,8}, b-tuples
  in [-20,20], H ≤ 10^4, exact rational arithmetic, counted-ops cap 1.0e8.
  NO transfer assumption to cryptographic parameters is made or licensed;
  correspondence is null in the frozen contract.
- Single execution round: R4 is a determinism replay, not an independent
  replication (same machine, same runtime, same seed). Evidence strength is
  single_run; the `replicate` decision follows the first-observation rule for
  surprising results (construction incidence 9.3× above the draw-route bound).
- Counts are lower bounds (Limitation from Inference 5); near-miss ledger
  semantics narrower than a literal spec reading (validator F-J3-1).
- n=8 statements are confined to the integer-box convention and the breached
  cap; nothing about the full rational height-H lattice at n=8 was measured.
- PD-1 leaves the R6 infeasibility proof recorded only in source (frozen
  pre-run), not in the run raw.
- Executor provenance qualifications stand: unverified resolved model
  (cursor-grok-4.6, fallback), dirty tree at runs (untracked outputs only;
  sources hash-bound). These are disclosure facts, not evidence.
- The blind round carries one documented procedure deviation: the post-freeze
  comparison reads (declared in the plan's comparison_after_freeze) intersect
  the blind_from prefixes; the mechanical independence check flags this by
  construction; freeze ordering is git-verifiable (derivation frozen at
  19709ca8b4 before comparison commit 05fbe8feb0). See
  REVIEW-PLAN-BATCH-24d356 procedure_deviations PD-R1.
- C1 stays OPEN and UNPROMOTED (IMP-2); nothing in this analysis touches the
  C1-closure candidate of DEC-20260905-7adca0; no closure, breakthrough, or
  established-evidence contradiction is proposed, so no review-breakthrough
  gate is engaged by this batch.
