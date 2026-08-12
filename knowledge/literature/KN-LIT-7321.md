---
id: KN-LIT-7321
type: literature
title: "Two-Round Stateless Deterministic"
authors:
  - "Two-Party Schnorr Signatures"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, hash, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Schnorr signatures are a popular choice due to their simplicity, provable security, and linear structure that enables relatively easy threshold signing protocols. The deterministic variant of Schnorr (where the nonce is derived in a stateless manner using a PRF from the message and a long term secret) is widely used in practice since it mitigates the threats of a faulty or poor randomness generator (which in Schnorr leads to catastrophic breaches of security).

## Key claims (as reported)
- Unfortunately, threshold protocols for the deterministic variant of Schnorr have so far been quite inefficient, as they make non black-box use of the PRF involved in the nonce generation.
- In this paper, we present the first two-party threshold protocol for Schnorr signatures, where signing is stateless and deterministic, and only makes black-box use of the underlying cryptographic algorithms.
- We present a protocol from general assumptions which achieves covert security, and a protocol that achieves full active security under standard factoring-like assumptions.
- Our protocols make crucial use of recent advances within the field of pseudorandom correlation functions (PCFs).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850131 (1).pdf`
- `downloads/140850131.pdf`
