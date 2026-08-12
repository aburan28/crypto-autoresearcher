---
id: KN-LIT-4616
type: literature
title: "KVaC: Key-Value Commitments for Blockchains and Beyond"
authors:
  - "Shashank Agrawal"
  - "Srinivasan Raghuraman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, number-theory, pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
As blockchains grow in size, validating new transactions becomes more and more resource intensive. To deal with this, there is a need to discover compact encodings of the (effective) state of a blockchain — an encoding that allows for efficient proofs of membership and updates.

## Key claims (as reported)
- In the case of account-based cryptocurrencies, the state can be represented by a key-value map, where keys are the account addresses and values consist of account balance, nonce, etc.
- We propose a new commitment scheme for key-value maps whose size does not grow with the number of keys, yet proofs of membership are of constant-size.
- In fact, both the encoding and the proofs consist of just two and three group elements respectively (in groups of unknown order like class groups).
- Verifying and updating proofs involves just a few group exponentiations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491306 (1).pdf`
- `downloads/12491306.pdf`
