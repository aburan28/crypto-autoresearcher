---
id: KN-LIT-1712
type: literature
title: "Labeled Multi-Key Batched IBE"
authors:
  - "Guru-Vamsi Policharla"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1452"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1452"
tags: [mov-fr, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study Batched IBE through the lens of Multi-Message Signatures – a natural extension of standard digital signatures in which a single signing operation signs an entire vector of messages at once. A public open algorithm then derives an opening for each message, allowing anyone to verify that an individual message was signed.

## Key claims (as reported)
- First we show that Multi-Message Signatures are essential by constructing a Multi-Message Signature scheme from every Batched IBE scheme with a sufficiently large plaintext space.
- We then show how to construct a Batched IBE scheme from a Multi-Message Signature with deterministic verification given an extractable witness encryption for the verification relation, similar to the duality between IBE and digital signatures.
- Such a witness encryption scheme can be instantiated efficiently for the special case of linearlyverifiable pairing-based multi-message signatures.
- Next we analyze existing constructions of Batched IBE and extract linearly-verifiable Multi-Message Signatures which provide us with valuable insight into the inner workings of various Batched IBE schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1452.pdf`
