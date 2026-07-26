---
id: KN-LIT-3756
type: literature
title: "Efficient Adaptively-Secure Byzantine Agreement for Long Messages"
authors:
  - "Amey Bhangale"
  - "Chen-Da Liu-Zhang⋆"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate the communication complexity of Byzantine agreement protocols for long messages against an adaptive adversary. In this setting, prior n-party protocols either achieved a communication complexity of O(nl·poly(κ)) or O(nl+n2 ·poly(κ)) for l-bit long messages and security parameter κ.

## Key claims (as reported)
- We improve the state of the art by presenting protocols with communication complexity O(nl + n · poly(κ)) in both the synchronous and asynchronous communication models.
- The synchronous protocol tolerates t ≤ (1 − ε) n2 corruptions and assumes a VRF setup, while the asynchronous protocol tolerates t ≤ (1 − ε) n3 corruptions under further cryptographic assumptions.
- Our protocols are very simple and combine subcommittee election with the recent approach of Nayak et al.
- Surprisingly, the analysis of our protocols is all but simple and involves an interesting new application of Mc Diarmid’s inequality to obtain almost optimal corruption thresholds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910208 (1).pdf`
- `downloads/137910208.pdf`
