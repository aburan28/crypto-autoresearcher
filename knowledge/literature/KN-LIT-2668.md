---
id: KN-LIT-2668
type: literature
title: "Batching Base Oblivious Transfers?"
authors:
  - "Ian McQuoid"
  - "Mike Rosulek"
  - "Lawrence Roy"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protocols that make use of oblivious transfer (OT) rarely require just one instance. Usually, a batch of OTs is required — notably, when generating base OTs for OT extension.

## Key claims (as reported)
- There is a natural way to optimize 2-round OT protocols when generating a batch, by reusing certain protocol messages across all instances.
- In this work we show that this batch optimization is error prone.
- We catalog many implementations and papers that have an incorrect treatment of this batch optimization, some of them leading to catastrophic leakage in OT extension protocols.
- We provide a full treatment of how to properly optimize recent 2-round OT protocols for the batch setting.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900209 (1).pdf`
- `downloads/130900209.pdf`
