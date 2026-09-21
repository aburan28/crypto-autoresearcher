---
id: KN-LIT-3005
type: literature
title: "Comparing Elliptic Curve Cryptography and RSA on 8-bit CPUs"
authors:
  - "Nils Gura"
  - "Arun Patel"
  - "Arvinderpal Wander"
  - "Hans Eberle"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, elliptic-curve, extension-field, factoring, pairing, prime-field, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Strong public-key cryptography is often considered to be too computationally expensive for small devices if not accelerated by cryptographic hardware. We revisited this statement and implemented elliptic curve point multiplication for 160-bit, 192-bit, and 224-bit NIST/SECG curves over GF(p) and RSA-1024 and RSA-2048 on two 8-bit microcontrollers.

## Key claims (as reported)
- To accelerate multiple-precision multiplication, we propose a new algorithm to reduce the number of memory accesses.
- Implementation and analysis led to three observations: 1.
- Public-key cryptography is viable on small devices without hardware acceleration.
- On an Atmel ATmega128 at 8 MHz we measured 0.81s for 160-bit ECC point multiplication and 0.43s for a RSA-1024 operation with exponent e = 216 + 1.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560117 (1).pdf`
- `downloads/31560117 (2).pdf`
- `downloads/31560117.pdf`
