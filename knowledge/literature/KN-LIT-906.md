---
id: KN-LIT-906
type: literature
title: "One-way functions and malleability oracles: Hidden shift attacks on isogeny-based protocols"
authors: []
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/282"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/282"
tags: [class-group, cryptanalysis, dlp, elliptic-curve, endomorphism, factoring, finite-field, hash, isogeny, lattice, number-theory, pairing, pqc, protocol, provable-security, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Supersingular isogeny Diffie-Hellman key exchange (SIDH) is a post-quantum protocol based on the presumed hardness of computing an isogeny between two supersingular elliptic curves given some additional torsion point information. Unlike other isogeny-based protocols, SIDH has been widely believed to be immune to subexponential quantum attacks because of the non-commutative structure of the endomorphism rings of supersingular curves.

## Key claims (as reported)
- We contradict this commonly believed misconception in this paper.
- More precisely, we highlight the existence of an abelian group action on the SIDH key space, and we show that for sufficiently unbalanced and overstretched SIDH parameters, this action can be efficiently computed (heuristically) using the torsion point information revealed in the protocol.
- This reduces the underlying hardness assumption to a hidden shift problem instance which can be solved in quantum subexponential time.
- We formulate our attack in a new framework allowing the inversion of one-way functions in quantum subexponential time provided a malleability oracle with respect to some commutative group action.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960029 (1).pdf`
- `downloads/126960029.pdf`
- `downloads/2021-282.pdf`
