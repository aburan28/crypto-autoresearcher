---
id: KN-LIT-270
type: literature
title: "The Certicom Challenges ECC2-X"
authors:
  - "Daniel V. Bailey"
  - "Brian Baldwin"
  - "Lejla Batina"
  - "Daniel J. Bernstein"
year: 2009
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2009/466"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2009/466"
tags: [binary-field, dlp, ecdlp, elliptic-curve, endomorphism, extension-field, hyperelliptic, implementation, pairing, pollard-rho, prime-field, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To encourage research on the hardness of the elliptic-curve discrete-logarithm problem (ECDLP) Certicom has published a series of challenge curves and DLPs. This paper analyzes the costs of breaking the Certicom challenges over the binary fields F2131 and F2163 on a variety of platforms.

## Key claims (as reported)
- We describe details of the choice of step function and distinguished points for the Koblitz and non-Koblitz curves.
- In contrast to the implementations for the previous Certicom challenges we do not restrict ourselves to software and conventional PCs, but branch out to cover the majority of available platforms such as various ASICs, FPGAs, CPUs and the Cell Broadband Engine.
- For the field arithmetic we investigate polynomial and normal basis arithmetic for these specific fields; in particular for the challenges on Koblitz curves normal bases become more attractive on ASICs and ⋆ This work has been supported in part by the National Science Foundation under grant ITR-0716498 and in part by the European Commission through the ICT Programme under Contract ICT–2007–216676 ECRYPT II.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2009-466.pdf`
- `downloads/ecc2x-20090901 (1).pdf`
- `downloads/ecc2x-20090901.pdf`
