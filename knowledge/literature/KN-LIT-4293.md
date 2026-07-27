---
id: KN-LIT-4293
type: literature
title: "How to Meet Ternary LWE Keys"
authors:
  - "Alexander May∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The LWE problem with its ring variants is today the most prominent candidate for building efficient public key cryptosystems resistant to quantum computers. NTRU-type cryptosystems use an LWE-type variant with small max-norm secrets, usually with ternary coefficients from the set {−1, 0, 1}.

## Key claims (as reported)
- The presumably best attack on these schemes is a hybrid attack that combines lattice reduction techniques with Odlyzko’s Meet-in-the-Middle approach.
- Odlyzko’s algorithm is a classical combinatorial attack that for key space size S runs in time S 0.5 .
- We substantially improve on this Meet-in-the-Middle approach, using the representation technique developed for subset sum algorithms.
- Asymptotically, our heuristic Meet-in-the-Middle attack runs in time roughly S 0.25 , which 1 also beats the S 3 complexity of the best known quantum algorithm.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826226 (1).pdf`
- `downloads/12826226.pdf`
