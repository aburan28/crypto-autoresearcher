---
id: KN-LIT-3806
type: literature
title: "Fast Message Franking: From Invisible Salamanders to Encryptment"
authors:
  - "Yevgeniy Dodis"
  - "Paul Grubbs"
  - "Thomas Ristenpart"
  - "Joanne Woodage"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Message franking enables cryptographically verifiable reporting of abusive messages in end-to-end encrypted messaging. Grubbs, Lu, and Ristenpart recently formalized the needed underlying primitive, what they call compactly committing authenticated encryption (AE), and analyze security of a number of approaches.

## Key claims (as reported)
- But all known secure schemes are still slow compared to the fastest standard AE schemes.
- For this reason Facebook Messenger uses AES-GCM for franking of attachments such as images or videos.
- We show how to break Facebook’s attachment franking scheme: a malicious user can send an objectionable image to a recipient but that recipient cannot report it as abuse.
- The core problem stems from use of fast but non-committing AE, and so we build the fastest compactly committing AE schemes to date.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993428 (1).pdf`
- `downloads/10993428.pdf`
