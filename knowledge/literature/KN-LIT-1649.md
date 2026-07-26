---
id: KN-LIT-1649
type: literature
title: "Faster Isogeny Group Action for Post-Quantum NIKE"
authors:
  - "Andrea Basso"
  - "Giacomo Borin"
  - "Ryan Rueger"
  - "Sina Schaeffler"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/896"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/896"
tags: [class-group, curve-arithmetic, elliptic-curve, implementation, isogeny, number-theory, pairing, pqc, protocol, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
There are two kinds of cryptographic group actions: restricted and unrestricted. While unrestricted actions like (qt-)PEGASIS are needed for more advanced constructions, restricted ones like dCTIDH are sufficient for instantiating a NIKE and usually much more efficient.

## Key claims (as reported)
- In this work, we propose CORAL, a significantly faster algorithm to evaluate the same action as (qt-)PEGASIS, but in a restricted fashion; CORAL only computes two-dimensional 2-isogenies to evaluate the action and outperforms both recent unrestricted (KLaPoTi, (qt-)PEGASIS) and (restricted) CSIDH-based approaches (SQALE, dCTIDH).
- In essence, CORAL trades off unrestrictedness for efficiency.
- Our unoptimised C implementation evaluates a group-action in 240 ms with a 2032-bit prime.
- When used to construct a non-interactive key exchange, CORAL yields an actively secure post-quantum NIKE with compact public keys (e.g.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-896.pdf`
