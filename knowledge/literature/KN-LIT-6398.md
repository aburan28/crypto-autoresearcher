---
id: KN-LIT-6398
type: literature
title: "Secret Exponent Attacks on RSA-type Schemes with Moduli N = pr q"
authors:
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider RSA-type schemes with modulus N = pr q for r ≥ 2. We present two new attacks for small secret exponent d.

## Key claims (as reported)
- Both approaches are applications of Coppersmith’s method for solving modular univariate polynomial equations [5].
- From these new attacks we directly derive partial key exposure attacks, i.e. attacks when the secret exponent is not necessarily small but when a fraction of the secret key bits is known to the attacker.
- Interestingly, all of these attacks work for public exponents e of arbitrary size.
- Additionally, we present partial key exposure attacks for the value dp = d mod p−1 which is used in CRT-variants like Takagi’s scheme [11].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470216 (1).pdf`
- `downloads/29470216 (2).pdf`
- `downloads/29470216.pdf`
