---
id: KN-LIT-126
type: literature
title: 'Quantum Cryptanalysis in the RAM Model: Claw-Finding Attacks on SIKE'
authors: [Jaques Samuel, Schanck John M]
year: 2019
venue: 'Advances in Cryptology - CRYPTO 2019, Springer'
identifiers:
  eprint: iacr:2019/103
  doi: 10.1007/978-3-030-26948-7_2
  url: https://eprint.iacr.org/2019/103
tags: [quantum, supersingular, isogeny, sike, sidh, claw-finding, ram-model, cost-model, gate-count, depth-width, memory, full-cost, resource-estimate, security-estimate, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Introduces models of computation that permit **direct comparison between
classical and quantum algorithms**, and uses them to revisit the security of
SIDH and SIKE. Building on prior work on quantum computation and error
correction, the paper justifies gate-count and depth-times-width as the cost
metrics for quantum circuits, then applies them to claw-finding attacks. The
reported effect is to **increase** the security estimates for SIDH and SIKE.

## Key claims (as reported)
- Gate-count and depth-times-width are the justified cost metrics for quantum
  circuits; the justification is physical, resting on error-correction
  requirements, not merely conventional.
- Applying these metrics **raises** SIDH/SIKE security estimates relative to
  previous analyses — a quantum attack that looked cheaper under a
  free-memory model becomes more expensive once memory is charged.
- The models, analyses and physical justifications are stated to apply to
  memory-intensive quantum algorithms generally, not only to isogenies.
- Received the Best Young Researcher Paper award at CRYPTO 2019.

## Relevance to this program
This is the quantum half of the BATCH-002 cost-model question, and it carries a
result the program should find striking: charging memory moved a security
estimate **upward**. The program's full-cost discipline (`KN-TECH-035`,
`KN-TECH-044`) is usually invoked to deflate an apparent advantage; this is the
same discipline producing the opposite sign. Any `GOAL-SSI-001` claim that a
quantum attack improves on a classical baseline must state which quantum cost
model it uses, because the choice is worth more than most algorithmic
improvements.

It also generalises `KN-TECH-044` (charging memory in lattice sieving) and
`KN-LIT-094` (Wiener's full cost) into the quantum setting, and so belongs to
the same cross-domain thread as `KN-OPEN-017`.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2019/103, DBLP `journals/iacr/JaquesS19`, ACM/Springer DOI
10.1007/978-3-030-26948-7_2, CRYPTO 2019); all direct fetches returned HTTP 403
under this session's egress policy. Title, author list, year and venue are
corroborated across independent results; the claims above paraphrase an abstract
returned by search.

NOT verified here: the definitions of the cost models, the size of the security
increase, which SIKE parameter sets were analysed, the assumed error-correction
parameters, and how these estimates interact with the classical vOW figures in
`KN-LIT-124` / `KN-LIT-125`. The LNCS volume was not confirmed and is omitted.
