# EXP-HZM-001 primary-gate disposition — composition analysis

Record: composed 2026-09-08 under BATCH-98edec, TASK-20260908-79b1b3,
REVIEW-PLAN-BATCH-98edec. This file does NOT overwrite the producer's
analysis.md (RUN-HZM-001-a/-d round); it disposes
RUN-HZM-001-c-primary-gate-only. Zero scientific runs in this batch.

## Observation

RUN-HZM-001-c-primary-gate-only (status completed_valid, snapshot
3794391b64; authorized by DEC-20260907-5b500d / amendment V2-CHG-1;
produced under TASK-20260907-d2164a) evaluated the pinned closed-form
charged-cost model at exactly the two authorized primary gate points
and nothing else (no curve, no seed, no enumeration):

- (N=4096, L=12, d=1): M=13, H=1, q=0.003169183122016195,
  charged_expected_signatures=315.5387244911908, rho_bound=64,
  survives_rho_gate=False (ratio 4.93).
- (N=65536, L=16, d=1): M=17, H=1, q=0.00025936775151069735,
  charged_expected_signatures=3855.5294333064226, rho_bound=256,
  survives_rho_gate=False (ratio 15.06).

Disclosures carried by the run: H/q is the signature-count bottleneck
term only (eight charged stages omitted; true cost can only be
larger); poly(log N) bit-cost assumption; H uses the SPEC's pinned
formula (moot at d=1).

## Comparison

Declared comparison act (Coordinator, post-freeze; prior P1-P4
committed before dispatch):

- **J1 red team** (RT-20260908-5d29c2, freeze 93ebc69381): verdict
  HOLDS on all six attacks A1-A6. Six objections, none disqualifying:
  RT98-O2 (boundary: closure must be stated at EXPONENT level, the
  constant margins are frozen-convention comparisons), RT98-O3
  (boundary: four forbidden scope extensions), RT98-O1/O4/O5/O6
  (notes: docstring overclaim, amendment's stale status: proposed
  superseded by verbatim DEC adoption, inherited validator pass not in
  the formal dispatch chain, decision schema-completion postdating the
  handoff but non-substantive). Authority chain verified logically and
  temporally; receipt ADMISSIBLE for a claim-changing decision. Bonus
  robustness: even the most route-favorable base-2L reading of M fails
  both gates (164.32 vs 64; 1986.42 vs 256).
- **J2 blind re-derivation** (TASK-20260908-422afa, freeze 033b76cf7b):
  verdict HOLDS. Exact-rational derivation matches every
  integer/boolean field exactly; the committed floats are BIT-EXACT
  reproductions of the float64 pipeline 1.0/(1.0-(1.0-1.0/N)**M) and
  differ from correctly-rounded exact doubles by 10 ulp / 588 ulp —
  evaluation-precision rounding, verdict unaffected. Independent exact
  gate characterization s(N-1)^m >= (s-1)N^m holds at both points;
  sufficient condition s*m <= (s-1)^2 holds (832<=3969; 4352<=65025);
  Bernoulli bound charged >= N/(L+1) reproduces the spec's audit bound
  at d=1. Passing-point control (64,16,1): charged 4.257500486510538 <
  8, survives=True, machinery_sane=true. Sensitivity D4: q-bound
  substitution shifts figures by 0.4618/0.4706 — committed figures
  come from the exact pinned formula. PD-H1 discloses that the handoff's
  uncertainty_reduced field quoted the target figures (reads_allowed,
  not blind_from); J2 attests its exact derivation predates and is
  independent of that exposure, and the ulp/pipeline structure cannot
  come from exposure to a 16-digit float.
- **Inherited validator** VAL-20260907-612101: passed, triple
  reproduction, one flagged archival-fidelity limitation
  (COMMAND-ARTIFACT-DISCREPANCY: command.txt is a simplified
  reconstruction missing the timing field; substantive fields
  bit-for-bit identical across three methods; J1 A5 concurs:
  not-disqualifying).

Prior comparison: P1 satisfied (J1 holds with boundary flags, no
break); P2 satisfied in refined form (integer/boolean fields
bit-exact; floats bit-exact as float64-pipeline evaluations; control
passes). Composition proceeds under clause P3.

## Inference

The frozen contract's pre-registered falsification_criterion(b) is
MET: the route's charged operation-level work at BOTH primary gate
sizes meets-or-exceeds the frozen rho bound under its own pinned
published formulas. Per the criterion's own disjunctive language, the
route is CLOSED as non-sub-rho under its own published model — the
prior audit's expected outcome. The gate-survival leg of H-HZM-001 is
refuted at derivation-note grade (refutation-note-primary-gate-
20260908.md): exact characterization machine-checked at both points,
conditional-algebra asymptotic corollary charged >= N/(L+1) =
N^(1-o(1)) > N^(1/2) for L = Theta(log N), lower-bound direction sound
(omitted stages can only add cost). Decision: reject_scoped;
H-HZM-001 approved -> rejected within exactly this scope; evidence
strength replicated (five independent derivations/reproductions);
KN-FIND-3d6f78 promoted per the pre-named warrant in
DEC-20260907-5b500d.

## Limitation

- Scope (rule 6): the negative closes EXACTLY gate survival at d=1
  under the pinned formulas at the two primary gate sizes, plus the
  conditional-algebra statement under the same pinned formulas. It
  does NOT adjudicate: the external publications' claims beyond their
  pinned model; the general d in {2,3} manuscript-alignment question
  (base ambiguity live; inconclusive_misalignment stands); the
  enumeration leg (RUN-HZM-001-b never opened; factor-of-2 realization
  untested and now moot for gate survival); any standardized curve
  (none instantiated).
- Exponent-level statement (RT98-O2 adopted): the closure is stated at
  the exponent level N^(1-o(1)) vs N^(1/2); the 4.93x/15.06x margins
  are frozen-convention comparisons under the poly(log N) bit-cost
  assumption, not group-operation-equivalent multiples of rho.
- The asymptotic corollary is conditional algebra from the pinned
  formulas (spec scale_relevance), not a toy measurement and not a
  theorem about the route's actual cost independent of its model.
- Precision: committed floats are float64-pipeline values (10/588 ulp
  from correctly-rounded exact doubles); verdict-insensitive.
- COMMAND-ARTIFACT-DISCREPANCY stands as an archival-hygiene item for
  a future pass; not disqualifying (triple reproduction + J1 A5).
- PD-H1: blindness edge in the dispatch documents (target figures
  quoted in the blind task's own handoff); disclosed, adjudicated, and
  lesson recorded in the plan.
- The general block on RUN-HZM-001-b / full-scope RUN-HZM-001-c STANDS
  unchanged; this decision does not lift it, and no enumeration result
  could now rescue gate survival (a cost the model's own bottleneck
  term already fails).

## Citations

Run: RUN-HZM-001-c-primary-gate-only (snapshot 3794391b64). Reviews:
RT-20260908-5d29c2 (…/reviews/TASK-20260908-5d29c2/red-team-report.yaml),
blind J2 (…/reviews/TASK-20260908-422afa/blind-rederivation.yaml),
VAL-20260907-612101 (experiments/EXP-HZM-001/reviews/validator-primary-gate/report.yaml),
composition attestation (…/reviews/TASK-20260908-79b1b3/composition-attestation.yaml).
Authorization: DEC-20260907-5b500d, amendment
v2_primary_gate_cost_check.yaml, TASK-20260907-d2164a. Contract:
experiments/EXP-HZM-001/specification.yaml. Refutation artifact:
experiments/EXP-HZM-001/refutation-note-primary-gate-20260908.md.
Records: EV-CRYPTO-ad7fa2, DEC-20260908-1d04cc, KN-FIND-3d6f78.
