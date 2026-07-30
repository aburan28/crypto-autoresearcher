---
id: KN-LIT-4399
type: literature
title: "Improved Differential Attacks for ECHO and Grøstl"
authors:
  - "Thomas Peyrin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, provable-security, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present improved cryptanalysis of two second-round SHA-3 candidates: the AESbased hash functions ECHO and Grøstl. We explain methods for building better differential trails for ECHO by increasing the granularity of the truncated differential paths previously considered.

## Key claims (as reported)
- In the case of Grøstl, we describe a new technique, the internal differential attack, which shows that when using parallel computations designers should also consider the differential security between the parallel branches.
- Then, we exploit the recently introduced start-from-the-middle or SuperSbox attacks, that proved to be very efficient when attacking AES-like permutations, to achieve a very efficient utilization of the available freedom degrees.
- Finally, we obtain the best known attacks so far for both ECHO and Grøstl.
- In particular, we are able to mount a distinguishing attack for the full Grøstl-256 compression function.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230369 (1).pdf`
- `downloads/62230369 (2).pdf`
- `downloads/62230369 (3).pdf`
- `downloads/62230369.pdf`
