---
id: KN-LIT-5417
type: literature
title: "On the (in)security of ROS"
authors:
  - "Fabrice Benhamouda"
  - "Tancrède Lepoint"
  - "Julian Loss"
  - "Michele Orrù"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an algorithm solving the ROS (Random inhomogeneities in a Overdetermined Solvable system of linear equations) problem mod p in polynomial time for ` > log p dimensions. Our algorithm can be combined with Wagner’s attack, and leads to a sub-exponential solution for any dimension ` with best complexity known so far.

## Key claims (as reported)
- When concurrent executions are allowed, our algorithm leads to practical attacks against unforgeability of blind signature schemes such as Schnorr and Okamoto–Schnorr blind signatures, threshold signatures such as GJKR and the original version of FROST, multisignatures such as CoSI and the two-round version of MuSig, partially blind signatures such as Abe–Okamoto, and conditional blind signatures such as ZGP17.
- Schemes for e-cash and anonymous credentials (such as Anonymous Credentials Light) inspired from the above are also affected.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960077 (1).pdf`
- `downloads/126960077.pdf`
