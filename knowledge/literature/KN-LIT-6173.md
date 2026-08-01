---
id: KN-LIT-6173
type: literature
title: "Reconsidering Generic Composition"
authors:
  - "Chanathip Namprempre"
  - "Phillip Rogaway"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the context of authenticated encryption (AE), generic composition has referred to the construction of an AE scheme by gluing together a conventional (privacy-only) encryption scheme and a MAC. Since the work of Bellare and Namprempre (2000) and then Krawczyk (2001), the conventional wisdom has become that there are three forms of generic composition, with Encrypt-then-MAC the only one that generically works.

## Key claims (as reported)
- However, many caveats to this understanding have surfaced over the years.
- Here we explore this issue further, showing how this understanding oversimplifies the situation because it ignores the results’ sensitivity to definitional choices.
- When encryption is formalized differently, making it either IV-based or nonce-based, rather than probabilistic, and when the AE goal is likewise changed to take in a nonce, qualitatively different results emerge.
- We explore these alternatives versions of the generic-composition story.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410253 (1).pdf`
- `downloads/84410253 (2).pdf`
- `downloads/84410253 (3).pdf`
- `downloads/84410253.pdf`
