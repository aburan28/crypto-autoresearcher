---
id: KN-LIT-4911
type: literature
title: "Message-Locked Encryption and Secure Deduplication"
authors:
  - "Mihir Bellare"
  - "Sriram Keelveedhi"
  - "Thomas Ristenpart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We formalize a new cryptographic primitive that we call Message-Locked Encryption (MLE), where the key under which encryption and decryption are performed is itself derived from the message. MLE provides a way to achieve secure deduplication (space-efficient secure outsourced storage), a goal currently targeted by numerous cloudstorage providers.

## Key claims (as reported)
- We provide definitions both for privacy and for a form of integrity that we call tag consistency.
- Based on this foundation, we make both practical and theoretical contributions.
- On the practical side, we provide ROM security analyses of a natural family of MLE schemes that includes deployed schemes.
- On the theoretical side the challenge is standard model solutions, and we make connections with deterministic encryption, hash functions secure on correlated inputs and the samplethen-extract paradigm to deliver schemes under different assumptions and for different classes of message sources.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810294 (1).pdf`
- `downloads/78810294 (2).pdf`
- `downloads/78810294 (3).pdf`
- `downloads/78810294.pdf`
