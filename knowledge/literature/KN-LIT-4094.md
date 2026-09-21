---
id: KN-LIT-4094
type: literature
title: "Generic Lower Bounds for Root Extraction and Signature Schemes in General Groups"
authors:
  - "Ivan Damgård"
  - "Maciej Koprowski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, complexity-theory, dlp, factoring, number-theory, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of root extraction in finite Abelian groups, where the group order is unknown. This is a natural generalization of the problem of decrypting RSA ciphertexts.

## Key claims (as reported)
- We study the complexity of this problem for generic algorithms, that is, algorithms that work for any group and do not use any special properties of the group at hand.
- We prove an exponential lower bound on the generic complexity of root extraction, even if the algorithm can choose the ”public exponent” itself.
- In other words, both the standard and the strong RSA assumption are provably true w.r.t. generic algorithms.
- The results hold for arbitrary groups, so security w.r.t. generic attacks follows for any cryptographic construction based on root extracting.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/DKea2002 (1).pdf`
- `downloads/DKea2002 (2).pdf`
- `downloads/DKea2002.pdf`
