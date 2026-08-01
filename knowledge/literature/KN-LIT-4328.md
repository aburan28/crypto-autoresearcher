---
id: KN-LIT-4328
type: literature
title: "Idealizing Identity-Based Encryption"
authors:
  - "Dennis Hofheinz"
  - "Christian Matt"
  - "Ueli Maurer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We formalize the standard application of identity-based encryption (IBE), namely non-interactive secure communication, as realizing an ideal system which we call delivery controlled channel (DCC). This system allows users to be registered (by a central authority) for an identity and to send messages securely to other users only known by their identity.

## Key claims (as reported)
- Quite surprisingly, we show that existing security definitions for IBE are not sufficient to realize DCC.
- In fact, it is impossible to do so in the standard model.
- We show, however, how to adjust any IBE scheme that satisfies the standard security definition IND-ID-CPA to achieve this goal in the random oracle model.
- We also show that the impossibility result can be avoided in the standard model by considering a weaker ideal system that requires all users to be registered in an initial phase before any messages are sent.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520216 (1).pdf`
- `downloads/94520216.pdf`
