---
id: KN-LIT-2163
type: literature
title: "A New Variant of PMAC: Beyond the Birthday Bound"
authors:
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, rsa, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a PMAC-type mode of operation that can be used as a highly secure MAC (Message Authentication Code) or PRF (Pseudo-Random Function). Our scheme is based on the assumption that the underlying n-bit blockcipher is a pseudo-random permutation.

## Key claims (as reported)
- Our construction, which we call PMAC Plus, involves extensive modification to PMAC, requiring three blockcipher keys.
- The PMAC Plus algorithm is a first rate-1 (i.e., one blockcipher( call per ) n-bit message block) blockcipher-based MAC secure against O 22n/3 queries, increasing the ( ) O 2n/2 security of PMAC at a low additional cost.
- Our analysis uses some of the security-proof techniques developed with the sum construction (Eurocrypt 2000) and with the encrypted-CBC sum construction (CT-RSA 2010).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410593 (1).pdf`
- `downloads/68410593 (2).pdf`
- `downloads/68410593 (3).pdf`
- `downloads/68410593.pdf`
