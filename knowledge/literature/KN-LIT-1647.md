---
id: KN-LIT-1647
type: literature
title: "Fast Isogeny Evaluation on Binary Curves"
authors:
  - "Gustavo Banegas"
  - "Nicolas Sarkis"
  - "Benjamin Smith"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/704"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/704"
tags: [binary-field, curve-arithmetic, dlp, elliptic-curve, finite-field, isogeny, pairing, pqc, protocol, quantum, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give efficient formulas to evaluate isogenies of ordinary elliptic curves over finite fields of characteristic 2, extending the oddcharacteristic techniques of Hisil–Costello and Renes to binary fields. For odd prime degree l = 2s + 1, our affine product evaluation computes the image x-coordinate using 5sM field multiplications, or 4sM when the kernel points are normalized.

## Key claims (as reported)
- We derive an inversion-free variant that evaluates the x-map in projective and twisted Kummer coordinates, allowing carried points to remain projective across successive isogeny steps.
- Over F2511 , microbenchmarks show that the inversion-free projective and twisted variants are faster than Vélu-style x-evaluation when outputs are kept in projective/twisted form, while the affine one-inversion variant is about 4.2× faster.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-704.pdf`
