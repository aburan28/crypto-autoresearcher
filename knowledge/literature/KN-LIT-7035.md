---
id: KN-LIT-7035
type: literature
title: "The Poly1305-AES message-authentication code"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Poly1305-AES is a state-of-the-art message-authentication code suitable for a wide variety of applications. Poly1305-AES computes a 16-byte authenticator of a variable-length message, using a 16-byte AES key, a 16-byte additional key, and a 16-byte nonce.

## Key claims (as reported)
- The security of Poly1305-AES is very close to the security of AES; the security gap is at most 14DdL/16e/2106 if messages have at most L bytes, the attacker sees at most 264 authenticated messages, and the attacker attempts D forgeries.
- Poly1305-AES can be computed at extremely high speed: for example, fewer than 3.1` + 780 Athlon cycles for an `-byte message.
- This speed is achieved without precomputation; consequently, 1000 keys can be handled simultaneously without cache misses.
- Special-purpose hardware can compute Poly1305-AES at even higher speed.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/35570033 (1).pdf`
- `downloads/35570033 (2).pdf`
- `downloads/35570033 (3).pdf`
- `downloads/35570033.pdf`
- `downloads/poly1305-20050329.pdf`
