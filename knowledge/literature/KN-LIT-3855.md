---
id: KN-LIT-3855
type: literature
title: "Fault Attacks on RSA Signatures with Partially Unknown Messages"
authors:
  - "Pascal Paillier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fault attacks exploit hardware malfunctions to recover secrets from embedded electronic devices. In the late 90’s, Boneh, DeMillo and Lipton [6] introduced fault-based attacks on crt-rsa.

## Key claims (as reported)
- These attacks factor the signer’s modulus when the message padding function is deterministic.
- However, the attack does not apply when the message is partially unknown, for example when it contains some randomness which is recovered only when verifying a correct signature.
- In this paper we successfully extends rsa fault attacks to a large class of partially known message configurations.
- The new attacks rely on Coppersmith’s algorithm for finding small roots of multivariate polynomial equations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470445 (1).pdf`
- `downloads/57470445 (2).pdf`
- `downloads/57470445 (3).pdf`
- `downloads/57470445.pdf`
