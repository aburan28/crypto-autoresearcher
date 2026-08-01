---
id: KN-LIT-6676
type: literature
title: "Simulatable Adaptive Oblivious Transfer"
authors:
  - "Jan Camenisch"
  - "Gregory Neven"
  - "abhi shelat"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study an adaptive variant of oblivious transfer in which a sender has N messages, of which a receiver can adaptively choose to receive k one-after-the-other, in such a way that (a) the sender learns nothing about the receiver’s selections, and (b) the receiver only learns about the k requested messages. We propose two practical protocols for this primitive that achieve a stronger security notion than previous schemes with comparable efficiency.

## Key claims (as reported)
- In particular, by requiring full simulatability for both sender and receiver security, our notion prohibits a subtle selective-failure attack not addressed by the security notions achieved by previous practical schemes.
- Our first protocol is a very efficient generic construction from unique blind signatures in the random oracle model.
- The second construction does not assume random oracles, but achieves remarkable efficiency with only a constant number of group elements sent during each transfer.
- This second construction uses novel techniques for building efficient simulatable protocols.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150573 (1).pdf`
- `downloads/45150573 (2).pdf`
- `downloads/45150573 (3).pdf`
- `downloads/45150573.pdf`
