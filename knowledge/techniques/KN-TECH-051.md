---
id: KN-TECH-051
type: technique
title: Quantum cost models for the CSIDH class-group action, and the resource-constraint dispute
tags: [csidh, class-group-action, quantum, hidden-shift, kuperberg, collimation-sieve, quantum-memory, resource-constrained, cost-model, parameter-selection, security-estimate, contested, post-quantum, adjacent]
confidence: reported
complexity: subexponential in the class-group order; the collimation sieve is reported to use exponentially less quantum memory than earlier hidden-shift algorithms, and the resulting security level depends on whether the adversary's quantum memory is bounded
applicability: any claim about CSIDH's quantum security or parameter sizing; the worked example of a cost-model convention moving a security level without any algorithmic disagreement
source_refs: [KN-LIT-127, KN-LIT-128, KN-LIT-129, KN-LIT-071, KN-LIT-069, KN-LIT-070, KN-TECH-027, KN-TECH-040, KN-TECH-044]
added: 2026-07-25
superseded_by: null
---

## Method
CSIDH's secret-key recovery reduces to a hidden-shift problem in a commutative
group (`KN-LIT-069`, `KN-LIT-070`, `KN-TECH-027`), so its quantum security is set
by the cost of a hidden-shift algorithm — and that cost is a function of the
resource model, not of the algorithm alone. Three positions in the corpus:

1. **Subexponential hidden-shift attack exists.** Kuperberg, then Regev, then
   Childs-Jao-Soukharev applied to isogenies (`KN-LIT-071`). This establishes the
   asymptotic shape.
2. **Collimation sieve, concretely costed** (`KN-LIT-127`). Kuperberg's c-sieve
   improves on the earlier algorithms, notably by using **exponentially less
   quantum memory** and offering more parameter tradeoffs. Peikert generalises it
   to arbitrary finite cyclic groups, supplies a **classical simulator**, and runs
   experiments up to the true CSIDH-512 group order. Alongside it,
   `KN-LIT-128` analyses CSIDH's proposed parameters against the
   Childs-Jao-Soukharev route.
3. **Resource-constrained re-costing** (`KN-LIT-129`). The SQALE authors respond
   that a **resource-constrained** collimation sieve gives a different, precise
   quantum security level, and derive CSIDH parameters for NIST levels 1-3 with
   primes reported to range from roughly 2000 to 9000 bits.

The methodological point is the same one `KN-TECH-040` records for lattices: a
security level here is a joint function of an algorithm and a declared resource
model. Positions 2 and 3 are not principally a disagreement about what the
adversary can compute. They are a disagreement about how much quantum memory the
adversary is allowed to have.

## How to use this in a claim
State the resource model before stating the number. A CSIDH quantum security
figure quoted without saying whether quantum memory is bounded — and if so, by
what — is not a claim this program can check, and the same applies to any
mechanism `GOAL-SSI-001` proposes against a commutative group action. If a
proposal's advantage over the baseline is smaller than the spread between
positions 2 and 3, the advantage is inside the convention's noise and the
comparison has not been made.

Note also that the response to the attack was a **large parameter increase**
rather than a refutation. That is the honest shape of a survived cryptanalysis
and the shape a program result of this kind should take.

## Applicability limits
This entry does not state CSIDH's quantum security level, because the corpus does
not know it. It identifies the dispute, its axis, and the three positions, so a
proposal can be located relative to them. `KN-OPEN-014` — the concrete quantum
security of CSIDH and the parameter sizes it forces — **remains open** and is not
closed by these entries.

The scope is CSIDH and commutative group actions. It does not transfer to the
endomorphism-ring or CGL path-finding assumptions, whose cost models are
`KN-TECH-050`'s subject, and it says nothing about SIDH/SIKE, which are broken by
a different route entirely (`KN-LIT-065`-`067`).

## Verified vs reported
All three source entries (`KN-LIT-127`, `KN-LIT-128`, `KN-LIT-129`) are
`citation_verified: web`, written under an egress policy that blocked every
direct fetch; their bibliographic details are corroborated across independent
primary-index listings but their abstracts were not read from a primary source.

Specifically **unverified and material**: `KN-LIT-128`'s actual verdict on
CSIDH's parameters was not obtained, only its subject; `KN-LIT-127`'s concrete
complexity for CSIDH-512 was not obtained; and `KN-LIT-129`'s refined estimates
and resulting security levels were not obtained. The existence and axis of the
dispute are well corroborated. Its resolution is not recorded here, and no
program record may cite this entry for a CSIDH security number.
