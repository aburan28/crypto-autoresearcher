---
id: KN-LIT-4677
type: literature
title: "Leakage Resilient Value Comparison With Application to Message Authentication"
authors:
  - "Christoph Dobraunig"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel attacks are a threat to secrets stored on a device, especially if an adversary has physical access to the device. As an effect of this, countermeasures against such attacks for cryptographic algorithms are a well-researched topic.

## Key claims (as reported)
- In this work, we deviate from the study of cryptographic algorithms and instead focus on the sidechannel protection of a much more basic operation, the comparison of a known attacker-controlled value with a secret one.
- Comparisons sensitive to side-channel leakage occur in tag comparisons during the verification of message authentication codes (MACs) or authenticated encryption, but are typically omitted in security analyses.
- Besides, also comparisons performed as part of fault countermeasures might be sensitive to sidechannel attacks.
- In this work, we present a formal analysis on comparing values in a leakage resilient manner by utilizing cryptographic building blocks that are typically part of an implementation anyway.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960142 (1).pdf`
- `downloads/126960142.pdf`
