---
id: KN-TECH-062
type: technique
title: Proof-architecture portfolio - boundary lifts, observation collisions, stronger invariants, telescoping potentials, and method ceilings
tags: [methodology, proof-architecture, theorem-search, baseline-embedding, identifiability, observation-collision, strengthened-invariant, potential-method, telescoping, specialization, quantifier-audit, method-ceiling, counterexample, agentic-harness, cross-domain]
confidence: reported
complexity: not an algorithmic cost claim - a pre-compute search and review protocol whose cheap audits should run before implementation or large experiments
applicability: >-
  Proof-oriented research tasks, asymptotic claims, certificate constructions,
  reductions, impossibility or closure arguments, and any experiment whose
  interpretation depends on an invariant or observable being identifying.
source_refs: [KN-LIT-7637, KN-TECH-055, KN-TECH-056]
added: 2026-08-01
superseded_by: null
---

## Epistemic status

This is the program's abstraction from the architectures visible in
`KN-LIT-7637`. It is adopted as a protocol on its own merits. It does **not**
assert that the ten source proofs are correct, that these transforms are
complete, or that using them raises the probability of a breakthrough. No
mathematical result transfers from the source domains to ECDLP merely because
the architecture looks reusable.

## Mandatory cheap audits

Every proof-oriented proposal fills a `proof_search_map` before compute. Four
audits are mandatory unless the proposal records a concrete reason they do not
apply.

1. **Exact bottleneck and baseline embedding.** Name the step whose removal
   changes the final theorem or exponent. If the proposal enlarges a known
   family, exhibit the exact parameter slice that reproduces the baseline and
   check it symbolically or with a frozen regression fixture. A numerical
   resemblance is not an embedding.
2. **Observation-collision test.** Name the observable, invariant, transcript,
   quotient, functor, or certificate on which the conclusion relies. Search for
   two distinct ground-truth objects with the same observable, especially one
   satisfying and one violating the target conclusion. If such a pair exists,
   the observable is insufficient until an added condition separates it.
3. **Quantifier-order audit.** Rewrite the claim with explicit `forall` and
   `exists` order. Test whether witnesses may depend on the instance, family
   member, characteristic, parameter, or random seed in a way the claimed
   uniform conclusion forbids.
4. **Method ceiling and nearby-object control.** Bound the strongest result the
   proposed measure could certify even under ideal tuning. Apply the same
   method to the closest object where the hoped-for conclusion is known or
   expected to fail. A method that cannot distinguish the pair has not yet
   identified the load-bearing structure.

These are falsification aids, not bureaucratic gates: a candidate that fails
one may still yield a useful obstruction, counterexample, or revised object.

## Constructive transform cards

After the cheap audits, select only the cards whose hypotheses are visible in
the target problem.

### A. Baseline-as-boundary lift

Enlarge a scalar, rank-one, degree-zero, or otherwise restricted certificate
family so the old method is the boundary case. The proof obligation is
strictness: identify a feasible inward direction and prove the gain is not a
grid-search or floating-point artifact. If there is a hierarchy, prove that
each inclusion is real and state whether the limit can be exchanged with the
problem-size limit.

### B. Stronger compositional invariant

When the target property does not survive recursion, preserve a stronger state
that implies the target and composes locally. Record all three maps:
`strong state -> target property`, `one-step preservation`, and `initialization`.
The red-team control deletes one component of the strong state and searches
for the first failed step.

### C. Telescoping-potential replacement

When a local estimate pays a rare-event denominator or has an uncontrolled
worst step, define a monotone or martingale potential over a reveal, filtration,
or layer sequence. Randomize the location of the charged increment and prove
that the total potential budget telescopes. Report the normalization explicitly:
conditioning cost, number of increments, and endpoint potential must all be
visible in the final bound.

### D. Specialize-measure-pack

Invent a target-specific measure that lower-bounds the resource of interest.
Construct a specialization making that measure large, prove it survives the
specialization, and pack disjoint blocks only after proving additivity and
non-overlap. Then prove the method's intrinsic ceiling; otherwise a saturated
framework may be mistaken for evidence that the problem itself is saturated.

### E. Representation and reduction chain

Move the problem into a representation where the hypothesis becomes an exact
equality, dimension, rank, or vanishing condition. Decompose the final result
into interface lemmas with separate responsibilities: encoding, completeness,
soundness or reconstruction, transfer, and cost/exponent degradation. Every
arrow records its hypotheses and whether it preserves determinism, success
probability, dimension, memory, and approximation factor.

### F. Observable-fiber counterexample

For rigidity, identifiability, and certificate claims, deliberately vary the
structure forgotten by the observable while holding the observable fixed.
Then search for an intrinsic invariant that distinguishes points in that
fiber. The deliverable is useful even when no counterexample exists: it records
which forgotten degrees of freedom were exhausted and which remain open.

## Proof-obligation decomposition

The existing single-responsibility rule remains in force. This protocol adds
two obligations that are often missing:

- **strictness**, separate from feasibility or correctness, for any claimed
  improvement over a boundary baseline;
- **interface preservation**, separate for every reduction or representation
  change, including the exact loss in the quantity being optimized.

A theorem assembly should therefore cite, as applicable: baseline reproduction,
feasibility, strictness, size, runtime, memory, correctness, success probability,
interface preservation, and scope. One lemma may discharge more than one only
when the dependency is explicit and a reviewer can check the parts separately.

## How this changes harness behavior

- The Idea Generator records the map before recommending compute.
- The Coordinator rejects proof-oriented dispatches whose claimed bottleneck
  is not decision-changing or whose baseline is not reproduced exactly.
- The Validator checks baseline fixtures, strictness witnesses, reduction
  interfaces, and machine-readable counterexamples from the committed snapshot.
- The Red Team attacks observation fibers, quantifier order, nearby objects,
  and method ceilings before disputing constants or implementation details.

The operative schema is in `templates/research-records.md`; the role-level
rules are in `agents/idea-generator.md`, `agents/coordinator.md`,
`agents/validator.md`, and `agents/red-team.md`.

## ECDLP limits

This protocol does not relax the public-endpoint, source-recovery, relation,
descent, scalar-orientation, memory, or full-cost gates. A prettier invariant,
certificate hierarchy, or reduction diagram is not an attack unless it yields
the entire charged source-to-target path and beats the correct rho or
specialized baseline in both time and memory.
