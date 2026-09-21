---
id: KN-FIND-14bbd9
type: internal_finding
title: "The prescribed square-pattern construction yields certified multi-class elliptic instances abundantly at n=6 over declared toy samples -- replicated with fresh seeds on the same machine, every certificate exactly recomputed and blind re-derived from the mechanism statement alone, detection validated by 9/9 planted recovery, counts MEASURED at the tested scope; construction incidence ~9x above the draw-route bound; the realized decade growth of N_6(H) sits more than an order of magnitude below the exponent-+2 (x100/decade) prediction under BOTH height conventions"
tags: [ecdlp-adjacent, elimination-theory, prescribed-construction, square-pattern, multi-class-instances, n6, replicated, same-machine, toy-tier, heur1-tension, decade-ratio, dual-convention, measured-counts, planted-detection, q-rank-defect, genuine-dependencies, n8-unresolved]
confidence: replicated_fresh_seed_same_machine_plus_blind_rederivation_plus_validator_exact_recheck_plus_redteam_exact_algebra
evidence_level: replicated_toy_tier_measurement
source_refs: [BATCH-e3cf55, BATCH-2f2b56, TASK-20260908-5291f8, TASK-20260909-9e06b1, TASK-20260909-868163, TASK-20260909-b56824, TASK-20260909-403113]
internal_refs: [EV-ECRANK-d7e05f, DEC-20260909-5756cb, EV-ECRANK-2222bd, DEC-20260908-d361ab, EV-ECRANK-8b35bb]
sibling_findings_narrowed: []
sibling_findings_note: >-
  This entry promotes the scoped positive half of the EXP-ECRANK-73275e
  lineage (H-ECRANK-36d8d7 / RQ-ECRANK-27dcc5 / GOAL-ECRANK-002) at
  replicated strength. It stands beside the draw-route obstruction entry
  lineage (EV-ECRANK-8b35bb is the standing draw-route wall measurement;
  this finding is the resource_check reading vindicated: the construction
  route succeeds where the draw route was measured to fail). It narrows no
  prior   entry and is narrowed by none; the HEUR-1 decade-ratio tension
  first surfaced in EV-ECRANK-2222bd is carried INSIDE this entry as a
  recorded scoped tension (branch TENSION-REAL), not resolved by it.
  A completed PRIOR review round over the same execution (BATCH-8fa16f;
  DEC-20260909-b61396 / EV-ECRANK-039664) recorded the same bounded
  support with statuses unchanged; the two rounds conflict in no finding
  (this entry's chain cites both), and the duplication is a recorded
  coordination finding, not a corpus disagreement.
proof_status: empirical_only
proof_refs:
  - experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json
  - experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R13-construct-n6-replay/raw-result.json
  - experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R10-planted-elliptic-n6/raw-result.json
review_refs:
  - coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-9e06b1/blind-rederivation.yaml
  - coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-868163/validation-report.yaml
  - coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-b56824/red-team-report.yaml
added: '2026-09-09'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY.** n in {6,8}; H <= 10^4 (n=6) / H <= 10^3 (n=8);
affine normal-form b-tuples with b_3..b_n distinct integers in [-20,20]
excluding {0,1}; declared samples of 10^4 b-tuples; exact rational
arithmetic. NOTHING here transfers to cryptographic parameters, and no
asymptotic claim is made. The frozen contract's correspondence to ECDLP is
null by construction; this is elimination-theory machinery measured on its
own terms.

**THIS ENTRY DOES NOT SAY HEUR-1 IS FALSE.** The construction-side count
law's decade growth is measured far below prediction at the tested scope
(see below), but the law's asymptotic regime is unmeasured; F2_n6 did not
fire; the tension is recorded, dual-convention, and open (successor N4).

**THIS ENTRY DOES NOT SAY ANYTHING AT n=8.** The n=8 arm completed in-cap
with a zero on the disclosed integer (a,b) sub-lattice; the full rational
lattice is unmeasured; F3_n8 did not fire. Separately, the n=8 d=(1..1)
CONTROL family exhibits genuine dependencies (three of eight tuples plateau
at certified total 6, Q-rank 6, surviving a 400-prime enlargement) --
recorded as a finding with the explicit second Q-relation NOT exhibited
(successor N5); this entry does not interpret it.

The finding, in one sentence:

> Over the frozen declared sample at n=6, the prescribed square-pattern
> construction (solve the univariate ellipticity condition in c per
> (b,d)-tuple; take exact rational roots; build s of degree 3) produces
> **33 certified multi-class instances per 10^4 b-tuples** (feasibility
> 0.0022; all n_classes = 3; certificates 33/33 PASS), **replicated with a
> fresh seed** and bit-identically replayed, with every certificate exactly
> recomputed by an independent validator and five instance entries blind
> re-derived from the mechanism statement alone with exact field-level
> agreement.

## The measured numbers (fresh-seed round, seed 760906)

- found 33 / 10^4 declared b-tuples; feasible_tuples 22; exhaustion null;
  counted ops 9,447,724 < 1.0e8 cap.
- Certificates 33/33 PASS; n_classes distribution {3:33}; zero instances
  with n_classes >= 4 (the multi-class certificate path is exercised at 3
  classes only -- an explicit coverage statement).
- Deterministic replay (seed 760906, second run): instance list, canonical
  counts, and op ledger bit-for-bit identical (IV-2R). This establishes
  determinism over a shared code path, NOT independent implementation --
  the independent-implementation evidence is the blind re-derivation below.
- Detection path validated: 9/9 planted ELLIPTIC n=6 instances recovered
  (R10, IV-3R(a)); by the pre-registered upgrade clause this lifts count
  readings from lower bounds to MEASURED at the tested scope. The planted
  exponent/calibration gates (b)/(c) failed as recorded and void only the
  planted-height calibration reading.
- Incidence context: construction incidence 3.3e-3 per b-tuple (v1 round:
  2.8e-3) vs the draw-route bound 3e-4 per b-tuple (EV-ECRANK-8b35bb,
  measured at n=8) -- construction-over-draw at the tested scope, with the
  different-n caveat disclosed.
- Decade growth of N_6(H), BOTH conventions, exact values, blind-verified
  arithmetic: convention A (root height) {100:20, 1000:28, 10000:33} ->
  ratios [1.4, 1.1785714285714286], two-decade 1.65; convention B (HEUR-1
  H) {100:26, 1000:33, 10000:33} -> ratios [1.2692307692307692, 1.0],
  two-decade 1.2692307692307692. The frozen exponent-+2 prediction is x100
  per decade. Branch TENSION-REAL selected; HEUR-1's construction-side
  count law stands UNVALIDATED with this recorded scoped tension.

## The evidence chain (why "replicated" and what it qualifies)

1. Execution: BATCH-e3cf55, seven runs R9-R15, all in-cap, snapshot-bound
   (commit 796eed5fa0, 62/62 content-path hashes verified).
2. Blind re-derivation (TASK-20260909-9e06b1, holds): derivation frozen at
   b8a0b94128 BEFORE any producer read; at three frozen (b,d) pairs
   (b_index 649, 1299, 4995) five derived nondegenerate rational roots
   match all five recorded found[] entries EXACTLY (r vectors, r_heights,
   cross-tabulation h_A/h_B, s, deg_s, memberships under both conventions).
   Blind finding carried: at pair 649 the ellipticity condition is LINEAR
   in c (A = 0) -- the "single univariate quadratic" label is a family
   label, not a per-tuple guarantee.
3. Validator (TASK-20260909-868163, holds, 10/10 PASS): all 33
   certificates exactly recomputed from recorded instance fields; counts,
   feasibility, and ratios recompute exactly under both conventions;
   verbatim N2R predicates match the frozen source lines; R13/R12 identity
   independently re-hashed; manifests conform.
4. Red team (TASK-20260909-b56824, breaks): breaks the INTERPRETATION
   joints -- the same-machine replication read as machine-independent, the
   toy ratios read as HEUR-1 refutation, the integer-box zero read as
   lattice-wide absence, and the IV-1C shortfalls read as a prime-bound
   artifact (exact algebra: genuine Q-rank-6 dependencies at three of eight
   n=8 control tuples). The scoped positive survives every
   proves-too-much control; the over-readings do not.

**The replication is same-machine, same-runtime** (executor resolved
vllm/qwen3.8-27b, fallback_used true, model_verified false; disclosed in
every manifest). It tests seed sensitivity and pipeline determinism; it
does NOT test machine-dependent behavior. Every "replicated" statement
carries this qualification until N6 runs.

## Reproduce

- Contract: experiments/EXP-ECRANK-73275e/specification.yaml (v1, frozen)
  + amendments/v2_replication_protocol.yaml (sha256
  6f61031861c9...847d; DEC-20260908-614199).
- Runs: RUN-ECRANK-73275e-R12-construct-n6-replication (primary),
  R13 (replay), R10 (planted detection), under
  experiments/EXP-ECRANK-73275e/runs/.
- Synthesis: experiments/EXP-ECRANK-73275e/analysis-v2.md;
  EV-ECRANK-d7e05f; DEC-20260909-5756cb.
- Caveat OBS-1: run_v2.py was modified mid-sequence (non-binding; it is
  outside bound_source_hashes); R9/R10/R11 manifests pin the pre-fix
  source c0eb13a0, R12-R15-final pin 583b0b42.

## Open successors carried by this entry

- N4: adjudicate TENSION-REAL -- extended-H dual-convention measurement or
  a theoretical density analysis (small-height scarcity / local-obstruction
  reading is the live resource_check hypothesis).
- N5: n=8 existence on the full rational lattice; exhibit the explicit
  second Q-relation at the shortfall tuples; reconcile with the M4
  ceiling / EV-ECRANK-6695dc reading.
- N6: machine-independent replication of the n=6 construct arm.
