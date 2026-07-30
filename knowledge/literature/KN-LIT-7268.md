---
id: KN-LIT-7268
type: literature
title: "Trick or Tweak: On the (In)security of OTR’s Tweaks"
authors:
  - "Raphael Bost"
  - "Olivier Sanders"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Tweakable blockcipher (TBC) is a powerful tool to design authenticated encryption schemes as illustrated by Minematsu’s Offset Two Rounds (OTR) construction. It considers an additional input, called tweak, to a standard blockcipher which adds some variability to this primitive.

## Key claims (as reported)
- More specifically, each tweak is expected to define a different, independent pseudo-random permutation.
- In this work we focus on OTR’s way to instantiate a TBC and show that it does not achieve independence for a large amount of parameters.
- We indeed describe collisions between the input masks derived from the tweaks and explain how they result in practical attacks against this scheme, breaking privacy, authenticity, or both, using a single encryption query, with advantage at least 1/4.
- We stress however that our results do not invalidate the OTR construction as a whole but simply prove that the TBC’s input masks should be designed differently.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031113 (1).pdf`
- `downloads/10031113.pdf`
