---
id: KN-LIT-5768
type: literature
title: "Pinpointing the Side-Channel Leakage of Masked AES Hardware Implementations ?"
authors:
  - "Stefan Mangard"
  - "Kai Schramm"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This article starts with a discussion of three different attacks on masked AES hardware implementations. This discussion leads to the conclusion that glitches in masked circuits pose the biggest threat to masked hardware implementations in practice.

## Key claims (as reported)
- Motivated by this fact, we pinpointed which parts of masked AES S-boxes cause the glitches that lead to side-channel leakage.
- The analysis reveals that these glitches are caused by the switching characteristics of XOR gates in masked multipliers.
- Masked multipliers are basic building blocks of most recent proposals for masked AES S-boxes.
- We subsequently show that the side-channel leakage of the masked multipliers can be prevented by fulfilling timing constraints for 3 · n XOR gates in each GF (2n ) multiplier of an AES S-box.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/07 (1).pdf`
- `downloads/07 (2).pdf`
- `downloads/07 (3).pdf`
- `downloads/07.pdf`
