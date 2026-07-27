---
id: KN-LIT-127
type: literature
title: He Gives C-Sieves on the CSIDH
authors: [Peikert Chris]
year: 2020
venue: 'Advances in Cryptology - EUROCRYPT 2020, LNCS 12106, Springer'
identifiers:
  eprint: iacr:2019/725
  doi: 10.1007/978-3-030-45724-2_16
  url: https://eprint.iacr.org/2019/725
tags: [quantum, csidh, class-group-action, hidden-shift, kuperberg, collimation-sieve, quantum-memory, cost-model, security-estimate, simulation, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Generalises Kuperberg's collimation sieve ("c-sieve") to arbitrary finite cyclic
groups, adds practical efficiency improvements, supplies a **classical
simulator** for it, runs experiments up to the actual CSIDH-512 group order, and
concretely quantifies the c-sieve's complexity against CSIDH. The target is the
hidden-shift structure of the CSIDH commutative group action, which is what lets
a quantum adversary recover a CSIDH secret key from a public key.

## Key claims (as reported)
- CSIDH is a candidate post-quantum commutative group action giving
  non-interactive Diffie-Hellman-like key exchange with small communication.
- Kuperberg, and subsequently Regev, gave asymptotically subexponential quantum
  algorithms for hidden-shift problems applicable to recovering the CSIDH key.
- Kuperberg's **collimation sieve** improves on those, in particular by using
  **exponentially less quantum memory** and offering more parameter tradeoffs.
- This work generalises the c-sieve to arbitrary finite cyclic groups, improves
  its practical efficiency, gives a classical simulator, and reports experiments
  for a wide range of parameters up to the true CSIDH-512 group order.

## Relevance to this program
Directly addresses `KN-OPEN-014` ("What is the concrete quantum security of
CSIDH, and how large must parameters be given the Kuperberg-sieve cost?"), which
until now had a question but no attack literature behind it. `RQ-SSI-001` lists
class-group-action / hidden-shift attacks on CSIDH as an in-scope method, and
`GOAL-SSI-001` names CSIDH as one of three surviving assumptions; this and
`KN-LIT-128` are the two papers that reset its quantum security.

Two features are methodologically relevant beyond isogenies. First, the headline
quantum-memory reduction is again a **resource-tradeoff** result rather than a
new attack idea, reinforcing the pattern in `KN-LIT-124` and `KN-TECH-040`.
Second, the classical simulator is an instrument for studying a quantum
algorithm's behaviour without a quantum computer — the same move the program
makes when it studies a mechanism at toy scale, and subject to the same
extrapolation caveats.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2019/725, Springer DOI 10.1007/978-3-030-45724-2_16, EUROCRYPT 2020 / LNCS
12106); direct fetches of the ePrint page and of the author-hosted PDF at
`web.eecs.umich.edu` both returned HTTP 403 under this session's egress policy.
Title, author, year and venue are corroborated across independent results.

NOT verified here — and this is the important part for `KN-OPEN-014`: **no
concrete complexity figure, qubit count, query count, or CSIDH-512 security
level from this paper is recorded in this entry**, because none could be read
from a primary source. The entry establishes that the paper exists and what it
claims to do. It does not settle the number, and `KN-OPEN-014` stays open.
