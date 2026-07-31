# Research Goals 2026-07-29 — NIST PQC Selected (Standardized) Algorithms

**Date anchor:** 2026-07-29

**Status:** Planning record. Five `draft` goals, one per selected algorithm.
Nothing here is evidence. Every per-algorithm technical statement below is a
**research target sourced from secondary reporting or from recollection of the
literature, and is unverified by this program.** Companion record:
`research_goals_20260729_nist_pqc_signatures.md`, which covers the nine Round-3
additional-signature candidates.

## 1. Provenance and its limits

Same constraint as the companion record: **`csrc.nist.gov` and `nist.gov` are
blocked by this environment's network policy** (the agent proxy answers `403`
to `CONNECT`), so the requested selected-algorithms page was **not read**, and
**no FIPS text has been read by this program**. The roster and status below were
confirmed from secondary reporting via search.

| Algorithm | FIPS | Status (secondary reporting) |
|---|---|---|
| ML-KEM (Kyber) | 203 | finalized 2024-08-13 |
| ML-DSA (Dilithium) | 204 | finalized 2024-08-13 |
| SLH-DSA (SPHINCS+) | 205 | finalized 2024-08-13 |
| FN-DSA (FALCON) | 206 | draft submitted 2025-08-28, in final review; publication expected late 2026 / early 2027 |
| HQC | — | selected 2025 as the code-based backup KEM; standard not yet published |

A reported June 2026 US federal executive order sets migration deadlines of
2030 for key establishment and 2031 for signatures. Unverified here, and
recorded only as motivation for why estimate errors on *these* algorithms cost
more than on a Round-3 candidate.

## 2. Goal index

| Goal | Question | Algorithm | Central object under attack |
|---|---|---|---|
| `GOAL-MLKEM-003` | `RQ-MLKEM-003` | ML-KEM | the core-SVP convention vs. a memory-charged concrete sieve cost at FIPS 203 dimensions |
| `GOAL-MLDSA-001` | `RQ-MLDSA-001` | ML-DSA | SelfTargetMSIS as the least-scrutinized load-bearing assumption; the fault-proof boundary |
| `GOAL-SLHDSA-001` | `RQ-SLHDSA-001` | SLH-DSA | slack between the multi-target proof and the best concrete attack |
| `GOAL-FNDSA-001` | `RQ-FNDSA-001` | FN-DSA | distributional exactness of the Gaussian sampler, independent of timing |
| `GOAL-HQC-001` | `RQ-HQC-001` | HQC | correctness of the decoding-failure-rate model that carries IND-CCA |

## 3. Why these objects

A standardized algorithm is a harder research target than a candidate, and a
more consequential one. Nobody re-derives a published parameter set, so an
error in the *estimate* survives indefinitely; and any claim made against a
fielded algorithm carries operational weight the evidence usually cannot bear.
Both facts pushed the choice of object:

- **Prefer the measurable claim over the assumption.** For three of the five,
  the load-bearing statement is not "this problem is hard" but a quantity
  someone computed. HQC's IND-CCA rests on an analytic decoding-failure-rate
  model — a probability, measurable at reduced parameters where failures are
  actually observable, and the classic place code-based schemes have failed
  before. FN-DSA rests on its signature distribution being an exact discrete
  Gaussian — the assumption that killed NTRUSign, and one that a perfectly
  constant-time implementation can violate without leaving a timing trace.
  ML-KEM's categories rest on a core-SVP convention that deliberately omits
  sieve memory and memory-access cost on conservatism grounds. Each of those is
  attackable with instrumentation rather than argument.
- **Name the under-scrutinized assumption, not the famous one.** ML-DSA has
  three underlying problems. MLWE and MSIS inherit a large literature;
  SelfTargetMSIS was introduced to make the Fiat-Shamir-with-aborts proof go
  through and carries the least independent scrutiny per unit of load-bearing.
  That asymmetry is the goal.
- **Measure the slack when the assumption is genuinely solid.** SLH-DSA's hash
  assumption is the one this program has least reason to doubt, so the goal
  targets the *bound* instead: how much room sits between the
  interleaved-target-subset-resilience proof and the best concrete multi-target
  attack, classically and quantumly, reported as a sensitivity range over the
  quantum cost convention rather than a single number.
- **Two live pre-standardization windows.** FN-DSA (FIPS 206 in review) and HQC
  (standard unpublished) are the only two where a finding could still reach the
  document. `GOAL-FNDSA-001` is flagged for priority scheduling on that basis.

## 4. Non-duplication

- `GOAL-MLKEM-003` is explicitly complementary to the two ML-KEM goals this
  program already holds. `GOAL-MLKEM-001` and `GOAL-MLKEM-002` own the
  defensive implementation-conformance lane (the re-encryption comparison
  class). The new goal owns the parameter/cost-model lane only, and its
  `next_action` requires a scope check before ideation.
- `GOAL-HQC-001` shares the memory-charged ISD baseline with `GOAL-SDITH-001`
  from the companion Round-3 record. Both goals reference the other so the two
  code-based lanes do not derive two different memory-charging conventions.

## 5. Rules that bind every goal in this set

All six rules from the companion record apply unchanged (no inherited claims;
matched baseline before attack; certificates; toy-tier ceiling; mathematics
separate from implementation; three-model closure quorum). One is added, and it
is the reason these goals are written more conservatively than the Round-3 set:

7. **Deployment consequence.** These algorithms are fielded or nearly so. No
   result leaves this program at a claim tier above the one its evidence
   supports, and no toy-scale finding is phrased as a statement about fielded
   systems. AGENTS.md rule 7 is more binding here, not less.

## 6. State

All five goals are `status: draft` with `dispatch_queue_path: null` — created,
not dispatched. Activating any of them means: obtain the FIPS text or
specification and the relevant primary literature, file them as `KN-LIT`
entries, then run `/propose-ideas` against that goal's question.
