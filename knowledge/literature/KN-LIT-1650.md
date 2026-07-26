---
id: KN-LIT-1650
type: literature
title: "Faster NTRU-based Bootstrapping with"
authors:
  - "Sorting-based Techniques"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1447"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1447"
tags: [fhe, lattice, mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NTRU-based bootstrapping offers a high-performance variant of FHEWlike bootstrapping schemes and is simpler than its RLWE-based counterparts. Nevertheless, it remains costly in terms of both memory and time.

## Key claims (as reported)
- A key computational bottleneck arises from the constraint q | 2N which links the LWE ciphertext modulus q to the NTRU dimension N .
- In this work, we apply extended techniques to remove the limitation q | 2N .
- With a large modulus q, we are able to complete the bootstrapping algorithms using a relatively small N -dimensional ring, thereby improving both time and memory efficiency.
- Additionally, we employ sorting-based techniques to eliminate unnecessary operations, which further enhances time performance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1447.pdf`
