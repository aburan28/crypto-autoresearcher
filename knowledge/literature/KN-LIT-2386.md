---
id: KN-LIT-2386
type: literature
title: "Algebraic Attacks on Rasta and Dasta Using Low-Degree Equations"
authors:
  - "Fukang Liu"
  - "Santanu Sarkar"
  - "Willi Meier"
  - "Takanori Isobe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, mov-fr, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Rasta and Dasta are two fully homomorphic encryption friendly symmetric-key primitives proposed at CRYPTO 2018 and ToSC 2020, respectively. We point out that the designers of Rasta and Dasta neglected an important property of the χ operation.

## Key claims (as reported)
- Combined with the special structure of Rasta and Dasta, this property directly leads to significantly improved algebraic cryptanalysis.
- Especially, it enables us to theoretically break 2 out of 3 instances of full Agrasta, which is the aggressive version of Rasta with the block size only slightly larger than the security level in bits.
- We further reveal that Dasta is more vulnerable against our attacks than Rasta for its usage of a linear layer composed of an ever-changing bit permutation and a deterministic linear transform.
- Based on our cryptanalysis, the security margins of Dasta and Rasta parameterized with (n, κ, r) ∈ {(327, 80, 4), (1877, 128, 4), (3545, 256, 5)} are reduced to only 1 round, where n, κ and r denote the block size, the claimed security level and the number of rounds, respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900055 (1).pdf`
- `downloads/130900055.pdf`
