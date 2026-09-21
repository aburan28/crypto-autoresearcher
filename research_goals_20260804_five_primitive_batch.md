# Research Goals 2026-08-04 — FrodoKEM, RSA, ECDSA, ML-DSA, SQIsign

**Date anchor:** 2026-08-04

**Status:** Planning record. Five `draft` goals, one per requested primitive.
Nothing here is evidence. Every per-primitive technical statement below is a
**research target read from a search-tool excerpt on 2026-08-04 and unverified
by this program.** No source named here has been filed as a `KN-LIT` entry, and
every goal in the set carries a constraint forbidding experiment design until
its primary sources are filed. Companion precedents:
`research_goals_20260729_nist_pqc_selected.md` and
`research_goals_20260729_nist_pqc_signatures.md`.

## 1. What was asked and what was created

The request was a goal for each of FrodoKEM, RSA, ECDSA, ML-DSA and SQIsign.
Two of the five already had goals — `GOAL-MLDSA-001` and `GOAL-SQISIGN-001`,
both opened 2026-07-29 and both still `draft`. Neither was edited. For those two
the new goals take **disjoint lanes** and declare the separation in a
`non_duplication` block, following the pattern `GOAL-MLKEM-003` used against
`GOAL-MLKEM-001/002`.

| Goal | Question | Primitive | Object under attack |
|---|---|---|---|
| `GOAL-FRODO-001` | `RQ-FRODO-3260cc` | FrodoKEM | the Rényi divergence and decryption failure rate, recomputed exactly at the standardized parameter sets |
| `GOAL-RSA-001` | `RQ-RSA-afe33c` | RSA | the NFS cost model itself: does it reproduce the record computations, and what does it say with memory charged |
| `GOAL-ECDSA-001` | `RQ-ECDSA-87625f` | ECDSA | the memory-charged nonce-leakage frontier and the 1-bit boundary at deployed curve sizes |
| `GOAL-MLDSA-002` | `RQ-MLDSA-ffa0f5` | ML-DSA | the signing-only rejection conditions, and FIPS 204's unquantified t0-secrecy assertion |
| `GOAL-SQISIGN-002` | `RQ-SQISIGN-39f231` | SQIsign | the published-data surface, audited against the SIDH/Kani attack template |

Goal identifiers use the legacy three-digit suffix because
`tools/validate_ledger.py` still pins `GOAL-[A-Z0-9]+-\d{3}`; the questions use
random six-hex tokens minted with `tools/allocate_id.py --next research_question`
and confirmed with `--check`, per AGENTS.md rule 14.

## 2. The selection criterion, stated so it can be argued with

Five primitives were named. Within each, the choice of *object* was made on one
criterion: **decisive evidence reachable inside a campaign budget**, preferred
over the most important-sounding question. That criterion is doing real work
here, and it pushed the set away from the obvious targets in four of five cases.

The obvious ECDSA goal is ECDLP. The obvious RSA goal is factoring. The obvious
FrodoKEM and ML-DSA goals are lattice estimates. All four are questions this
program cannot settle, and three of the four are already owned by existing goals
that have been working on them for many batches. What is left when those are set
aside is not scraps: it is the set of **quantities that were computed once and
inherited ever since**, which is where an error survives longest precisely
because nobody re-derives a published parameter set.

Three of the five goals target such a quantity directly:

- **FrodoKEM** is the standout, and the reason is unusual enough to state
  plainly: its two load-bearing numbers are *finite exact computations at the
  real parameter sets*. The error distribution is a table of at most thirteen
  entries; the failure rate is a convolution over it. This program almost never
  gets to work at cryptographic parameters, and here it can, in exact rational
  arithmetic, with no extrapolation heuristic anywhere in the chain.
- **ML-DSA** offers two statements in a fielded standard that were asserted
  rather than derived — the rejection conditions the verifier does not check,
  and the claim that t0 is reconstructible from "a small number of signatures"
  when the published attack puts that number at 200,000 to 500,000. Both are
  measurable at the real parameter sets with certificates that cost
  microseconds.
- **RSA** targets the cost model rather than the modulus. This program holds
  `KN-TECH-057` as its exemplar of a matched full-cost baseline and has no
  analogue for factoring, which means every RSA equivalence it might ever cite
  is inherited. The record computations plus the published NFS simulation
  methodology make this an exact-baseline-reproduction audit in the sense of
  `KN-TECH-080`, available off the shelf.

The remaining two target structure rather than a number:

- **ECDSA** has a fast-moving published frontier — predicate-augmented lattice
  reduction, sieving with a predicate, and a lattice/Fourier tradeoff reaching
  1-bit and sub-1-bit leakage at 160 bits — and no one has put the two families
  on a single frontier with **memory** charged. The published resource figures
  make clear why that matters: a 1-bit recovery at 160 bits is quoted at
  ~2^25 samples, 824 minutes and 1939 GiB against a variant at 2^36 samples,
  279 minutes and 850 GiB. Those are different machines, not different rows of
  one table.
- **SQIsign** rests much of its post-SIDH confidence on a single structural
  claim — that it does not publish the auxiliary torsion-point information the
  SIDH break consumed. The redesigned scheme builds its response *out of*
  torsion images by construction, so the claim is a statement about the boundary
  between internally computed and published data. Boundaries get audited item by
  item, not summarized.

## 3. Why not the ranking that would look better

`docs/target-result-profile.md` biases toward exponent-moving results on central
hard problems. **None of these five goals is that,** and the set should not be
presented as though it were. Four of the five produce measurements, inventories
or baselines; the fifth produces a named obstruction if it succeeds. The reason
is stated rather than hidden: the exponent-moving lanes for these primitives are
either already owned by existing goals in this ledger or are not reachable by
this harness, and `docs/inventor-protocol.md` treats a fatigue report dressed as
a closure as a failure mode. A baseline that reproduces published measurements
is a smaller claim than an exponent, and it is one this program can actually
support.

The honest ranking by *reachable decisive evidence*, which is a Coordinator
scheduling input and not a judgement of importance:

1. **`GOAL-FRODO-001`** — crypto-tier arithmetic claim, exact, at real
   parameters, inside budget. Highest evidence-per-batch in the set.
2. **`GOAL-MLDSA-002`** — crypto-tier measurement at real parameters, cheap
   certificates, one published reproduction target to anchor against.
3. **`GOAL-SQISIGN-002`** — cheap reading task and toy instantiation; the
   deliverable is most likely a negative result, which the closure standard
   recognizes.
4. **`GOAL-ECDSA-001`** — a certified crypto-scale solve is reachable at a
   generous rung, but the published frontier sits at terabyte-scale memory and
   the campaign will not reach it.
5. **`GOAL-RSA-001`** — no record computation is in scope; the deliverable is a
   validated model, and the validation gate may simply fail. A failure there is
   a result and closes the expensive branch early.

## 4. Non-duplication

- **`GOAL-MLDSA-002` vs `GOAL-MLDSA-001`.** The existing goal owns which of
  MLWE / MSIS / SelfTargetMSIS binds at each FIPS 204 category, and the boundary
  of the fault-injection security proof. The new goal re-estimates no assumption
  and injects no fault; both its objects are measurable with an unmodified,
  correctly-executing implementation. `GOAL-MLKEM-002`, which completed on the
  ML-KEM re-encryption comparison, is the structural precedent for treating a
  conformance lane as its own goal.
- **`GOAL-SQISIGN-002` vs `GOAL-SQISIGN-001` and `GOAL-SSI-001`.** Three-way
  split: hard-problem hardness and the `KN-TECH-057` baselines stay with
  `GOAL-SSI-001`; transcript-versus-simulation distinguishability stays with
  `GOAL-SQISIGN-001`; the published-data surface and the Kani template are new.
- **`GOAL-ECDSA-001` vs the ECDLP program.** The new goal says nothing about
  plain ECDLP in either direction. `KN-TECH-019` already records that the
  HNP-plus-lattice pipeline is not a plain ECDLP attack, and `KN-OPEN-011` owns
  whether the technique transfers; that question stays with `GOAL-ECDLP-001` and
  `GOAL-PATH-001`. It is also distinct from `RQ-ALECF-001` (imported Autolab
  quantum point-addition circuit scores on secp256k1) — same curve, unrelated
  object.
- **`GOAL-FRODO-001` vs the ML-KEM goals.** `GOAL-MLKEM-003` and
  `GOAL-MLKEM-004` own core-SVP conventions and memory-charged sieve cost. The
  Frodo goal does not re-estimate LWE hardness and hands off if a batch finds
  itself doing so.
- **`GOAL-RSA-001` vs `GOAL-ECTD-001` and `GOAL-ECDSA-001`.** Hidden-SNFS
  trapdoor claims stay with `GOAL-ECTD-001`; SNFS appears here only as a control
  on the cost model. `GOAL-RSA-001` and `GOAL-ECDSA-001` share a charged-cost
  discipline, and whichever runs second binds to the other's memory-charging
  convention or records why it cannot.

## 5. One observation recorded, not acted on

Reported second-round status language describes SQIsign's redesign — from
KLPT-based path-finding to higher-dimensional isogenies — as letting the
response isogeny be sampled from a more natural distribution and thereby
clarifying its zero-knowledge properties. If accurate, that may have moved the
object `GOAL-SQISIGN-001` was written against on 2026-07-29. This is an
observation from an unverified excerpt, not a finding. It is recorded under
AGENTS.md rule 8 in `GOAL-SQISIGN-002.non_duplication` and in this document;
`GOAL-SQISIGN-001` was **not edited**, and revising it is a matter for a
Coordinator ledger archive after the Round-3 specification has actually been
read.

## 6. Rules that bind every goal in this set

The six rules from the 2026-07-29 records apply unchanged — no inherited
claims, matched baseline before attack, certificates, claim-tier ceilings,
mathematics kept separate from implementation, and deployment consequence for
fielded algorithms. Three are added or sharpened because of what this particular
set contains:

8. **The source gate is shut on all five.** Every figure in these records came
   from a search-tool excerpt, at least one of which (FrodoKEM Table A.3) is
   visibly extraction-damaged, and one of which carries an unexplained
   discrepancy that is preserved rather than smoothed over (RSA-250's phase
   times as quoted sum to 2830 against a headline 2700). No experiment may be
   designed until the relevant primary sources are filed as `KN-LIT` entries at
   stated provenance levels. This is the `GOAL-HQC-001` BATCH-001-to-BATCH-002
   sequence, whose lesson was that acquisition does not discharge filing and
   that a corpus entry is immutable once filed.
9. **Controls before belief, in the specific form each goal needs.** FrodoKEM
   requires a mutation control that detects a seeded one-unit table
   perturbation before agreement counts as verification. ML-DSA requires a null
   in which t0 is resampled independently of the key. SQIsign requires a
   weakened variant against which the audit must *fire*. RSA gets its control
   free from the literature: factorization and discrete logarithm were run at
   the same 240-digit size, and a model reproducing one but not the other is
   caught. In each case the control is a precondition, not a robustness check.
10. **Claim tiers split within a goal, not just between goals.** FrodoKEM and
    ML-DSA can support crypto-tier *arithmetic and measurement* claims while
    supporting nothing above toy tier for any *security* reading, and both goal
    records say so explicitly. A batch that blurs the two has failed regardless
    of what it computed. Recovering t0 is not a key recovery; a verifying
    non-conforming signature is not a forgery; a divergence discrepancy is not
    an attack; a certified ECDSA recovery under assumed leakage is a statement
    about the leakage model and not about ECDLP.

## 7. State

All five goals are `status: draft` with `dispatch_queue_path: null` — created,
not dispatched, and **not activated**. Activation is a Coordinator action taken
on explicit direction and recorded as such; `GOAL-HQC-001`'s
`status_value_history` is the precedent for how a user authorization to launch
is written down rather than self-granted. Activating any of them means:
acquire the primary sources, file them as `KN-LIT` entries, then run
`/propose-ideas` against that goal's question — in that order, which every one
of the five `next_action` fields states.
