---
id: KN-LIT-4908
type: literature
title: "Message Franking via Committing Authenticated Encryption"
authors:
  - "Paul Grubbs"
  - "Jiahui Lu"
  - "Thomas Ristenpart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of message franking, recently introduced in Facebook’s end-to-end encrypted message system. It targets verifiable reporting of abusive messages to Facebook without compromising security guarantees.

## Key claims (as reported)
- We capture the goals of message franking via a new cryptographic primitive: compactly committing authenticated encryption with associated data (AEAD).
- This is an AEAD scheme for which a small part of the ciphertext can be used as a cryptographic commitment to the message contents.
- Decryption provides, in addition to the message, a value that can be used to open the commitment.
- Security for franking mandates more than that required of traditional notions associated with commitment.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401394 (1).pdf`
- `downloads/10401394.pdf`
