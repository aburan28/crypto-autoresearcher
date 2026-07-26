---
id: KN-LIT-5225
type: literature
title: "Non-Malleable Time-Lock Puzzles and Applications"
authors:
  - "Cody Freitag"
  - "Ilan Komargodski"
  - "Rafael Pass"
  - "Naomi Sirkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Time-lock puzzles are a mechanism for sending messages “to the future”, by allowing a sender to quickly generate a puzzle with an underlying message that remains hidden until a receiver spends a moderately large amount of time solving it. We introduce and construct a variant of a time-lock puzzle which is non-malleable, which roughly guarantees that it is impossible to “maul” a puzzle into one for a related message without solving it.

## Key claims (as reported)
- Using non-malleable time-lock puzzles, we achieve the following applications: – The first fair non-interactive multi-party protocols for coin flipping and auctions in the plain model without setup. – Practically efficient fair multi-party protocols for coin flipping and auctions proven secure in the (auxiliary-input) random oracle model.
- As a key step towards proving the security of our protocols, we introduce the notion of functional non-malleability, which protects against tampering attacks that affect a specific function of the related messages.
- To support an unbounded number of participants in our protocols, our time-lock puzzles satisfy functional non-malleability in the fully concurrent setting.
- We additionally show that standard (non-functional) nonmalleability is impossible to achieve in the concurrent setting (even in the random oracle model).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420202 (1).pdf`
- `downloads/130420202.pdf`
