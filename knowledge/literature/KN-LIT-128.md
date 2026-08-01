---
id: KN-LIT-128
type: literature
title: Quantum Security Analysis of CSIDH
authors: [Bonnetain Xavier, Schrottenloher Andre]
year: 2020
venue: 'Advances in Cryptology - EUROCRYPT 2020, Springer'
identifiers:
  eprint: iacr:2018/537
  doi: 10.1007/978-3-030-45724-2_17
  url: https://eprint.iacr.org/2018/537
tags: [quantum, csidh, class-group-action, hidden-shift, kuperberg, childs-jao-soukharev, parameter-selection, security-estimate, cost-model, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
A quantum security analysis of CSIDH's proposed parameters. CSIDH is a
post-quantum non-interactive key exchange similar in design to the
Couveignes-Rostovtsev-Stolbunov scheme but aiming at a better efficiency/security
balance, and its authors proposed concrete parameters intended to meet stated
quantum security levels. This paper analyses those parameters against the
hardness of recovering the hidden isogeny, via the quantum subexponential
algorithm of Childs-Jao-Soukharev and its hidden-shift building blocks.

## Key claims (as reported)
- CSIDH's proposed parameters were selected to meet desired quantum security
  levels; this work re-examines whether they do.
- The analysis routes through recovering a hidden isogeny between two curves
  using the Childs-Jao-Soukharev quantum subexponential algorithm
  (`KN-LIT-071`), which combines a quantum algorithm for hidden shift in a
  commutative group with other components.
- Presented at EUROCRYPT 2020 alongside `KN-LIT-127`; the two together are what
  the subsequent literature refers to as the reassessment of CSIDH's quantum
  security.

## Relevance to this program
The companion to `KN-LIT-127` for `KN-OPEN-014`, and the entry that gives
`KN-LIT-071` (Childs-Jao-Soukharev, already in the corpus) its concrete
consequence. Before these two entries the corpus could state that a quantum
subexponential attack on commutative group actions exists; it could not state
that the attack had been costed against real CSIDH parameters and found them
wanting.

For `GOAL-SSI-001` this matters in a specific way: CSIDH is one of the three
surviving assumptions the goal is scoped to, and its quantum security is the
axis on which it is contested. A novelty screen that does not surface this pair
would let a proposal re-derive a known parameter criticism as if it were new.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2018/537, Springer/ACM DOI 10.1007/978-3-030-45724-2_17, EUROCRYPT 2020); direct
fetches returned HTTP 403 under this session's egress policy. Title, author list,
year and venue are corroborated across independent results. The description above
paraphrases the opening of an abstract returned by search; the LNCS volume was
not confirmed and is omitted.

NOT verified here: **the paper's actual conclusion about CSIDH's parameters** —
the direction and size of any security-level revision, the concrete costs
derived, the assumed quantum memory model, and how its figures compare with
`KN-LIT-127`'s. This entry records that the analysis exists and what it analyses.
It does not record its verdict, and no program record may cite a CSIDH security
number to it.
