---
id: KN-LIT-1939
type: literature
title: "Trout++: Robust Asynchronous Two-Round ECDSA for Arbitrary Thresholds"
authors:
  - "Ariel Nof"
  - "Luke Parker"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1455"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1455"
tags: [ecdsa, elliptic-curve, implementation, pairing, protocol, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present Trout++, a complete threshold signing suite for ECDSA signatures. Trout++ descends from the recent Trout protocol (Dahari-Garbian, Nof, and Parker, ACM CCS 2025) and inherits its transparent setup, two-round structure, and strong security guarantees, while introducing several significant improvements.

## Key claims (as reported)
- Unlike Trout, Trout++ offers pre-signing, where the first round is key-, signing-set-, and message- independent.
- This property is not only important in its own right but also enables us to apply the ROAST transformation (Ruffing, Ronge, Jin, Schneider-Bensch, and Schröder, ACM CCS 2022) to our protocol, yielding the first arbitrary-threshold (including with a dishonest majority), robust, asynchronous signing protocol for ECDSA signatures.
- Furthermore, we introduce several optimizations to the building blocks in Trout that reduce both bandwidth and computation.
- Our benchmark results show that our implementation of Trout++ is approximately twice as fast and twice as small compared to the prior implementation of Trout.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1455.pdf`
