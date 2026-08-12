---
id: KN-LIT-846
type: literature
title: "Collisions in Supersingular Isogeny Graphs and the SIDH-based Identification Protocol"
authors:
  - "Wissam Ghantous"
  - "Shuichi Katsumata"
  - "Federico Pintore"
  - "Mattia Veroni"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1051"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1051"
tags: [class-group, cryptanalysis, dlp, ecdlp, elliptic-curve, hash, isogeny, number-theory, pairing, pqc, protocol, quantum, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The digital signature schemes that have been proposed so far in the setting of the Supersingular Isogeny Diffie-Hellman scheme (SIDH) were obtained by applying the Fiat-Shamir transform - and a quantum-resistant analog, the Unruh transform - to an interactive identification protocol introduced by De Feo, Jao and Plût. The security of the resulting schemes is therefore deduced from that of the base identification protocol.

## Key claims (as reported)
- In this paper, we revisit the proofs that have appeared in the literature for the special soundness property of the aforementioned SIDH-based identification protocol.
- All such proofs consider the same extraction algorithm, which is claimed to always extract the witness for a statement x when given two valid transcripts, with the same commitment and different challenges, relative to x itself.
- We show that this is not always the case, with some explicit counterexamples.
- The general argument fails due to some special cycles, which we call collisions, in supersingular isogeny graphs.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1051.pdf`
