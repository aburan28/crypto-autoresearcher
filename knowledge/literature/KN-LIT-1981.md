---
id: KN-LIT-1981
type: literature
title: "1-out-of-n Signatures from a Variety of Keys"
authors:
  - "Masayuki Abe"
  - "Miyako Ohkubo"
  - "Koutarou Suzuki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mov-fr, mpc, provable-security, quantum, rsa, signature, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper addresses how to use public-keys of several different signature schemes to generate 1-out-of-n signatures. Previously known constructions are for either RSA-keys only or DL-type keys only.

## Key claims (as reported)
- We present a widely applicable method to construct a 1-out-of-n signature scheme that allows mixture use of different flavors of keys at the same time.
- The resulting scheme is more efficient than previous schemes even if it is used only with a single type of keys.
- With all DL-type keys, it yields shorter signatures than the ones of the previously known scheme based on the witness indistinguishable proofs by Cramer, et. al.
- With all RSA-type keys, it reduces both computational and storage costs compared to that of the Ring signatures by Rivest, et. al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/25010414 (1).pdf`
- `downloads/25010414 (2).pdf`
- `downloads/25010414.pdf`
