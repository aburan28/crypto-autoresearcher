---
id: KN-LIT-7571
type: literature
title: Post-Quantum Anonymous Signatures from the Lattice Isomorphism Group Action
authors: [van Noorden Chris, de Perthuis Paola]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/436'
identifiers:
  eprint: iacr:2026/436
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/436
tags: [group-action, cryptographic-group-action, lattice-isomorphism-problem, lip, isogeny, class-group-action, blind-signature, designated-verifier, zero-knowledge, non-commutative, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Generalizes the cryptographic-group-action framework so that it covers the group
action underlying the **Lattice Isomorphism Problem (LIP)**, where the acting group is
countably infinite and non-commutative — a case earlier generic group-action
constructions could not express. From zero-knowledge proofs of OR statements it builds
generic blind signatures and strong designated-verifier signatures with
non-delegability, under standard assumptions for a **generalised group action inverse
problem**.

## Key claims (as reported)
- Post-quantum assumptions cannot rely on finding secret subgroups the way many
  classical schemes did; the field has moved to more general **group actions**, hoping
  quantum algorithms are less helpful in the less structured setting.
- Group-action constructions began with **isogenies, where an ideal class group acts on
  elliptic curves**; equivalence problems in error-correcting codes and in lattices
  exhibit the same structure.
- Prior anonymity-preserving constructions in the generic group-action framework were
  **not general enough to cover LIP**, whose acting group is countably infinite and
  non-commutative.
- The paper bridges that gap, obtaining generic blind signatures and strong
  designated-verifier signatures with non-delegability from standard assumptions
  corresponding to a generalised group action inverse problem.

## Relevance to this program
`adjacent` — a construction paper, not cryptanalysis — recorded for the **structural
taxonomy** it makes explicit, which is directly germane to how this program reasons
about what the ECDLP is.

The corpus already holds the commutative case in `KN-TECH-027` (CSIDH commutative
class-group action and the quantum hidden-shift attack) and `KN-OPEN-014` (concrete
quantum security of CSIDH given Kuperberg-sieve cost). The relevant fact recorded
there is that **commutativity is what Kuperberg's algorithm exploits**: a regular
abelian group action is subexponentially attackable quantumly in a way a
non-commutative one is not known to be. This paper is a current data point that the
non-commutative, infinite-group regime is now being built on deliberately, for exactly
that reason.

The connection back to the ECDLP is a framing one and should not be overstated: the
discrete logarithm in a cyclic group is the *maximally* structured end of this
spectrum — a free, transitive, **commutative** action of `Z/n` — which is why
`KN-TECH-005`'s generic-group square-root bound applies so cleanly and why Shor's
period-finding applies at all. The taxonomy commutative-and-finite (DL, CSIDH) versus
non-commutative-and-infinite (LIP) is a useful axis for the program's own barrier
reasoning: results that depend on the group action's commutativity do not transfer,
in either direction.

Forecloses nothing on the ECDLP and supplies no attack.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-03-03, last of 16 revisions 2026-07-25 — a **heavily revised paper whose
latest revision fell in the 2026-07-19..26 window**, not a first posting. No DOI;
peer-review status not established.

NOT verified here: the constructions, the security proofs, the precise statement of
the "generalised group action inverse problem" and whether it is a standard assumption
in the sense claimed, the non-delegability property, and the LIP hardness picture
generally. The commutativity/Kuperberg framing under "Relevance" is this entry's own
reading drawn from `KN-TECH-027`, not a claim made by this paper.
