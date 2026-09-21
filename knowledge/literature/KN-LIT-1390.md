---
id: KN-LIT-1390
type: literature
title: "Experimentally studying path-finding problem between conjugates in supersingular isogeny graphs: Optimizing primes and powers to speed-up cycle finding Madhurima Mukhopadhyay"
authors: []
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/189"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/189"
tags: [dlp, elliptic-curve, endomorphism, finite-field, hash, isogeny, mov-fr, pqc, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of finding paths between conjugate supersingular elliptic curves, a subroutine of cycle finding algorithm in the graph χl (Fp ) of all supersingular elliptic curves over Fp2 , connected by l isogenies for primes l, p. We prove that asymptotically the most time-efficient way of traversing the graph to find conjugate paths is seeing i(= 3) steps together, a question posed in Remark 3.5 by Eisenträger et. al.

## Key claims (as reported)
- We outline procedures for choosing l which will accelerate the process of conjugate path-finding.
- We have experimentally investigated the paths between frobenius conjugates for wide ranges of small prime l, which adds to previous studies [ACNL+ 23].
- Experiments confirm that selecting l, i optimally speedens up the cycle finding, in an analogous way as the equivalent problem of isogeny finding to subfield curve was hastened by the Supersolver method [CRSCS22].
- We introduce sets to experimentally study the structure of the isogeny graphs when short cycles are present.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-189.pdf`
