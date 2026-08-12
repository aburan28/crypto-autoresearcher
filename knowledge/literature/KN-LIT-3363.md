---
id: KN-LIT-3363
type: literature
title: "Decentralized Multi-Client"
authors:
  - "Duong Hieu Phan"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a situation where multiple parties, owning data that have to be frequently updated, agree to share weighted sums of these data with some aggregator, but where they do not wish to reveal their individual data, and do not trust each other. We combine techniques from Private Stream Aggregation (PSA) and Functional Encryption (FE), to introduce a primitive we call Decentralized Multi-Client Functional Encryption (DMCFE), for which we give a practical instantiation for Inner Product functionalities.

## Key claims (as reported)
- This primitive allows various senders to non-interactively generate ciphertexts which support inner-product evaluation, with functional decryption keys that can also be generated non-interactively, in a distributed way, among the senders.
- Interactions are required during the setup phase only.
- We prove adaptive security of our constructions, while allowing corruptions of the clients, in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272256 (1).pdf`
- `downloads/11272256.pdf`
