---
id: KN-LIT-3094
type: literature
title: "Conditional Oblivious Cast ?"
authors:
  - "Cheng-Kang Chu"
  - "Wen-Guey Tzeng"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new notion of conditional oblivious cast (COC), which involves three parties: a sender S and two receivers A and B. Receivers A and B own their secrets x and y, respectively, and the sender S holds the message m.

## Key claims (as reported)
- In a COC scheme for the predicate Q (Q-COC), A and B send x and y in a masked form to S, and then S sends m to A and B such that they get m if and only if Q(x, y) = 1.
- Besides, the secrets x and y can not be revealed to another receiver nor the sender.
- We also extend COC to 1-out-of-2 COC (COC12 ) in which S holds two messages m0 and m1 , and A and B get m1 if Q(x, y) = 1 and m0 otherwise.
- We give the definitions for COC and COC12 , and propose several COC and COC12 schemes for “equality”, “inequality”, and “greater than” predicates.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580452 (1).pdf`
- `downloads/39580452 (2).pdf`
- `downloads/39580452 (3).pdf`
- `downloads/39580452.pdf`
