---
id: KN-LIT-2210
type: literature
title: "A Quantum Cipher with Near Optimal Key-Recycling"
authors:
  - "Ivan Damgård"
  - "Thomas Brochmann Pedersen"
  - "Louis Salvail"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Assuming an insecure quantum channel and an authenticated classical channel, we propose an unconditionally secure scheme for encrypting classical messages under a shared key, where attempts to eavesdrop the ciphertext can be detected. If no eavesdropping is detected, we can securely re-use the entire key for encrypting new messages.

## Key claims (as reported)
- If eavesdropping is detected, we must discard a number of key bits corresponding to the length of the message, but can re-use almost all of the rest.
- We show this is essentially optimal.
- Thus, provided the adversary does not interfere (too much) with the quantum channel, we can securely send an arbitrary number of message bits, independently of the length of the initial key.
- Moreover, the key-recycling mechanism only requires one-bit feedback.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/36210490 (1).pdf`
- `downloads/36210490 (2).pdf`
- `downloads/36210490 (3).pdf`
- `downloads/36210490.pdf`
