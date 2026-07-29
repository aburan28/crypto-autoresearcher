# Research Goals 2026-07-29 — NIST Additional Digital Signatures, Round 3

**Date anchor:** 2026-07-29

**Status:** Planning record. Nine `draft` goals, one per Round-3 candidate.
Companion record: `research_goals_20260729_nist_pqc_selected.md`, covering the
five selected (standardized) algorithms.
Nothing here is evidence. Every per-scheme technical statement below is a
**research target sourced from secondary reporting or from recollection of the
literature, and is unverified by this program.** No experiment may be designed
against any of these goals until the relevant primary sources are read and
filed as `KN-LIT` entries.

## 1. Provenance and its limits

NIST concluded the second evaluation round of the Additional Digital Signatures
process on 2026-05-14 and advanced nine candidates to Round 3; submission teams
may file updated specifications and implementations by 2026-08-14, and the
round is expected to run roughly two years, with the 7th PQC Standardization
Conference expected in the first half of 2027. Five candidates — CROSS, LESS,
Mirath, PERK, RYDE — were eliminated.

**`csrc.nist.gov` and `nist.gov` are blocked by this environment's network
policy** (the agent proxy answers `403` to `CONNECT`), so the requested page
`csrc.nist.gov/Projects/pqc-dig-sig/round-3-additional-signatures` was **not
read**. The roster, the elimination list, and the dates above were confirmed
from secondary reporting via search. The Round-3 specification bundle has not
been read by this program at all. Each goal's `next_action` therefore blocks
ideation on obtaining primary sources first, and each research question carries
an explicit `provenance` field saying so.

## 2. Goal index

| Goal | Question | Scheme | Family | Central object under attack |
|---|---|---|---|---|
| `GOAL-FAEST-001` | `RQ-FAEST-001` | FAEST | symmetric / VOLE-in-the-Head | tightness of the chain AES one-wayness → VOLEitH soundness → Fiat-Shamir |
| `GOAL-HAWK-001` | `RQ-HAWK-001` | HAWK | lattice (module-LIP) | the reported polynomial-time smLIP key recovery, heuristic by heuristic |
| `GOAL-MAYO-001` | `RQ-MAYO-001` | MAYO | multivariate (whipped UOV) | the whipping/emulsification map and any invariant it preserves |
| `GOAL-MQOM-001` | `RQ-MQOM-001` | MQOM | MPCitH / TCitH over MQ | forgery-bound tightness + measured MQ hardness at its field sizes |
| `GOAL-QRUOV-001` | `RQ-QRUOV-001` | QR-UOV | multivariate (quotient-ring UOV) | whether quotient-ring key compression is security-neutral |
| `GOAL-SDITH-001` | `RQ-SDITH-001` | SDitH | code-based MPCitH | the d-split SD instance vs. the plain-SD estimate it inherits |
| `GOAL-SNOVA-001` | `RQ-SNOVA-001` | SNOVA | multivariate (noncommutative-ring UOV) | the (v, o, ℓ, q) → security map under wedge-product / group-action attacks |
| `GOAL-SQISIGN-001` | `RQ-SQISIGN-001` | SQIsign | isogeny | signing-transcript leakage vs. the zero-knowledge simulation assumption |
| `GOAL-UOV-001` | `RQ-UOV-001` | UOV | multivariate (foundational) | measured calibration of the plain-UOV cost model |

## 3. Portfolio logic

The nine goals are not nine copies of "attack scheme X". Each names a distinct
**object** in the sense of `docs/inventor-protocol.md`, chosen so that a
negative result is still informative:

- **One shared baseline.** `GOAL-UOV-001` is scheduled first among the
  multivariate goals because MAYO, QR-UOV, and SNOVA are all measured against
  the plain-UOV cost model. Three independently derived UOV cost conventions
  would make the Pareto comparisons in the other three goals meaningless. Its
  deliverable is a *calibrated* model — anchored by certified toy recoveries
  and a solving-degree census — not a quoted asymptotic.
- **Structure-tax questions.** MAYO, QR-UOV, and SNOVA each buy a size
  advantage with added structure. In each case the goal is stated as: does the
  structure cost security relative to the matched baseline? That question has a
  publishable answer in both directions.
- **Assumption-vs-instance questions.** FAEST and SDitH both inherit a
  conservative headline assumption (AES one-wayness; random-SD hardness) while
  handing the attacker a more structured instance. Both goals target the gap,
  and both require the matched baseline to be charged for memory and grinding
  before any attack is scored.
- **Verification of an external claim.** `GOAL-HAWK-001` is the one goal whose
  primary job is to check somebody else's break rather than find a new one.
  Reported 2026 work claims classical probabilistic-polynomial-time HAWK key
  recovery under four number-theoretic heuristics, via a reduction of rank-2
  module-LIP to nrdPIP enabled by an automorphism that van Gent and Pulles
  (2025) had shown would halve the effective rank. Whether NIST revises HAWK's
  parameters, its security claims, or its standing was still open as of
  2026-07-28. This is exactly the shape of result
  `docs/target-result-profile.md` calls for — conditional on explicit numbered
  heuristics — so the useful contribution is an independent, certified check of
  whether it holds at deployed parameters.
- **Deliberate non-overlap with `GOAL-SSI-001`.** The existing isogeny goal
  owns the endomorphism-ring / path-finding lane and holds the matched
  full-cost baselines in `KN-TECH-057` (VW p^{1/2} over F_{p²}, or p^{1/4} over
  F_p conditional on mixing — not the easier MITM p^{2/3} or DG p^{1/3}).
  `GOAL-SQISIGN-001` therefore takes the protocol flank instead: whether the
  signing transcript is as simulatable as claimed. The two goals must not both
  claim the hard-problem lane.

## 4. Rules that bind every goal in this set

1. **No inherited claims.** Figures repeated in these records from secondary
   reporting — SNOVA margin loss of 2^8–2^39, one weak key in 500 at 2^97,
   SNOVA-I at 94 bits, HAWK polynomial-time recovery — are flagged unverified
   in the records themselves and may not be restated as this program's results
   until reproduced from primary text.
2. **Matched baseline before attack.** No cost is reported without the
   best-known baseline at *identical* parameters, with memory, preprocessing,
   and verification charged. This program's documented failure mode is a
   partial win that dies once those are charged.
3. **Certificates.** Any claimed break carries a certificate the run wrapper
   re-verifies independently — a recovered key annihilating the public map, or
   a forged signature that verifies. See `docs/claims-and-verification.md`.
4. **Toy-tier ceiling.** AGENTS.md rule 7: no toy-scale result is reported as a
   statement about deployed parameters. Extrapolations are stated conditionally
   on numbered heuristics.
5. **Mathematics separate from implementation.** Fault and side-channel results
   (MAYO's vinegar-seed routes, VOLEitH masking attacks, SQIsign's
   side-channel-hard signing) are a distinct claim class and may never be
   scored as a break of the underlying map or assumption.
6. **Closure.** No goal here reaches `completed` without the three-model
   closure quorum in AGENTS.md rule 13. Under this harness that usually
   requires deliberately routing three different backends; if that is not
   possible, the goal stays `paused` and says so.

## 5. State

All nine goals are `status: draft` with `dispatch_queue_path: null` — created,
not dispatched. Per AGENTS.md, a goal is committed with its initial question
before dispatch; the handoff is written when a batch is actually launched.
Activating any of them means: obtain the Round-3 specification and the relevant
attack papers, file them as `KN-LIT` entries, then run `/propose-ideas` against
that goal's question.
