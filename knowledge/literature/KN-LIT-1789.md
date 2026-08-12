---
id: KN-LIT-1789
type: literature
title: "On the Secrecy of the Encapsulation Coin in ML-KEM"
authors:
  - "M. G. Tehrani∗"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1117"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1117"
tags: [hash, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ML-KEM (FIPS 203) draws a fresh 32-byte coin at each encapsulation. The shared secret is a deterministic function of the public key and this coin, so a known coin is a recovered key.

## Key claims (as reported)
- We ask instead how well the coin’s secrecy is protected in practice, and we answer by experiment.
- On six unmodified libraries (OpenSSL 3.5, wolfSSL 5.9, AWS-LC, Go 1.26, Bouncy Castle 1.83, and CIRCL), and a from-scratch reference, the coin-recovery is reachable in every one; what differs is the guard, from a test-walled package in Go to an ordinary production call in wolfSSL.
- A second path needs no injection function at all: substituting the generator at build time makes the ordinary encapsulation predictable, while the public re-seed interface correctly refuses to.
- Outside the validated FIPS-140-3 configuration that most deployments do not yet use, the coin’s secrecy rests on convention, not construction.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1117.pdf`
