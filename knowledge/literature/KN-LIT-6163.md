---
id: KN-LIT-6163
type: literature
title: "Really fast syndrome-based hashing"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christiane Peters"
  - "Peter Schwabe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, hyperelliptic, implementation, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The FSB (fast syndrome-based) hash function was submitted to the SHA-3 competition by Augot, Finiasz, Gaborit, Manuel, and Sendrier in 2008, after preliminary designs proposed in 2003, 2005, and 2007. Many FSB parameter choices were broken by Coron and Joux in 2004, Saarinen in 2007, and Fouque and Leurent in 2008, but the basic FSB idea appears to be secure, and the FSB submission remains unbroken.

## Key claims (as reported)
- On the other hand, the FSB submission is also quite slow, and was not selected for the second round of the competition.
- This paper introduces RFSB, an enhancement to FSB.
- In particular, this paper introduces the RFSB-509 compression function, RFSB with a particular set of parameters.
- RFSB-509, like the FSB-256 compression function, is designed to be used inside a 256-bit collision-resistant hash function: all known attack strategies cost more than 2128 to find collisions in RFSB-509.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/rfsb-20110508 (1).pdf`
- `downloads/rfsb-20110508.pdf`
