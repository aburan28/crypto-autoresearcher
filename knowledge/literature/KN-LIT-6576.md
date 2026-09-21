---
id: KN-LIT-6576
type: literature
title: "Short and Stateless Signatures from the RSA Assumption"
authors:
  - "Susan Hohenberger"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first signature scheme which is “short”, stateless and secure under the RSA assumption in the standard model. Prior short, standard model signatures in the RSA setting required either a strong complexity assumption such as Strong RSA or (recently) that the signer maintain state.

## Key claims (as reported)
- A signature in our scheme is comprised of one element in Z∗N and one integer.
- The public key is also short, requiring only the modulus N , one element of Z∗N , one integer and one PRF seed.
- To design our signature, we employ the known generic construction of fully-secure signatures from weakly-secure signatures and a chameleon hash.
- We then introduce a new proof technique for reasoning about weakly-secure signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770642 (1).pdf`
- `downloads/56770642 (2).pdf`
- `downloads/56770642 (3).pdf`
- `downloads/56770642.pdf`
