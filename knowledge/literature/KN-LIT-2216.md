---
id: KN-LIT-2216
type: literature
title: "A Refined Power-Analysis Attack on Elliptic Curve Cryptosystems Louis Goubin"
authors:
  - "CP Crypto Lab"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, elliptic-curve, pairing, prime-field, protocol, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
As Elliptic Curve Cryptosystems are becoming more and more popular and are included in many standards, an increasing demand has appeared for secure implementations that are not vulnerable to sidechannel attacks. To achieve this goal, several generic countermeasures against Power Analysis have been proposed in recent years.

## Key claims (as reported)
- In particular, to protect the basic scalar multiplication – on an elliptic curve – against Differential Power Analysis (DPA), it has often been recommended using “random projective coordinates”, “random elliptic curve isomorphisms” or “random field isomorphisms”.
- So far, these countermeasures have been considered by many authors as a cheap and secure way of avoiding the DPA attacks on the “scalar multiplication” primitive.
- However we show in the present paper that, for many elliptic curves, such a DPA-protection of the “scalar” multiplication is not sufficient.
- In a chosen message scenario, a Power Analysis attack is still possible even if one of the three aforementioned countermeasures is used.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/25670199 (1).pdf`
- `downloads/25670199 (2).pdf`
- `downloads/25670199.pdf`
