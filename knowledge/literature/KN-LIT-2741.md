---
id: KN-LIT-2741
type: literature
title: "Blind Identity-Based Encryption and Simulatable Oblivious Transfer"
authors:
  - "Matthew Green"
  - "Susan Hohenberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In an identity-based encryption (IBE) scheme, there is a key extraction protocol where a user submits an identity string to a master authority who then returns the corresponding secret key for that identity. In this work, we describe how this protocol can be performed efficiently and in a blind fashion for several known IBE schemes; that is, a user can obtain a secret key for an identity without the master authority learning anything about this identity.

## Key claims (as reported)
- We formalize this notion as blind IBE and discuss its many practical applications.
- In particular, we build upon the recent work of Camenisch, Neven, and shelat [12] to construct oblivious transfer (OT) schemes which achieve full simulatability for both sender and receiver.
- OT constructions with comparable efficiency prior to Camenisch et al. were proven secure in the weaker half-simulation model.
- Our OT schemes are constructed from the blind IBE schemes we propose, which require only static complexity assumptions (e.g., DBDH) whereas prior comparable schemes require dynamic assumptions (e.g., q-PDDH).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330265 (1).pdf`
- `downloads/48330265 (2).pdf`
- `downloads/48330265 (3).pdf`
- `downloads/48330265.pdf`
