---
id: KN-LIT-2984
type: literature
title: "Commuting Signatures and Verifiable Encryption"
authors:
  - "Georg Fuchsbauer⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Verifiable encryption allows one to encrypt a signature while preserving its public verifiability. We introduce a new primitive called commuting signatures and verifiable encryption that extends this in multiple ways, such as enabling encryption of both signature and message while proving validity.

## Key claims (as reported)
- More importantly, given a ciphertext, a signer can create a verifiably encrypted signature on the encrypted (unknown) message, which leads to the same result as first signing the message and then verifiably encrypting the message/signature pair; thus, signing and encrypting commute.
- Our instantiation is based on the recently introduced automorphic signatures and Groth-Sahai proofs, which we show to be homomorphic.
- We also prove a series of other properties and provide a novel approach to simulation.
- As an application, we give an instantiation of delegatable anonymous credentials, a primitive introduced by Belenkiy et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320227 (1).pdf`
- `downloads/66320227 (4).pdf`
- `downloads/66320227 (6).pdf`
- `downloads/66320227.pdf`
