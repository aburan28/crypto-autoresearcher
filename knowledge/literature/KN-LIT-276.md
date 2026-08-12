---
id: KN-LIT-276
type: literature
title: "ACCELERATING THE CM METHOD"
authors:
  - "ANDREW V. SUTHERLAND"
year: 2010
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1009.1082"
  url: "https://arxiv.org/abs/1009.1082"
tags: [elliptic-curve, endomorphism, finite-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given a prime q and a negative discriminant D, the CM method constructs an elliptic curve E/Fq by obtaining a root of the Hilbert class polynomial HD (X) modulo q. We consider an approach based on a decomposition of the ring class field defined by HD , which we adapt to a CRT setting.

## Key claims (as reported)
- This yields two algorithms, each of which obtains a root of HD mod q without necessarily computing any of its coefficients.
- Heuristically, our approach uses asymptotically less time and space than the standard CM method for almost all D.
- Under the GRH, and reasonable assumptions about the size of log q relative to |D|, we achieve a space complexity of O((m + n) log q) bits, where mn = h(D), which may be as small as O(|D|1/4 log q).
- The practical efficiency of the algorithms is demonstrated using |D| > 1016 and q ≈ 2256 , and also |D| > 1015 and q ≈ 233220 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1009.1082v4.pdf`
