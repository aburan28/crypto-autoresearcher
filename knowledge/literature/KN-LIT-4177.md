---
id: KN-LIT-4177
type: literature
title: "Hedged Public-Key Encryption:"
authors:
  - "Gil Segev"
  - "Hovav Shacham"
  - "Scott Yilek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Public-key encryption schemes rely for their IND-CPA security on per-message fresh randomness. In practice, randomness may be of poor quality for a variety of reasons, leading to failure of the schemes.

## Key claims (as reported)
- Expecting the systems to improve is unrealistic.
- What we show in this paper is that we can, instead, improve the cryptography to offset the lack of possible randomness.
- We provide public-key encryption schemes that achieve IND-CPA security when the randomness they use is of high quality, but, when the latter is not the case, rather than breaking completely, they achieve a weaker but still useful notion of security that we call IND-CDA.
- This hedged public-key encryption provides the best possible security guarantees in the face of bad randomness.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120224 (1).pdf`
- `downloads/59120224 (2).pdf`
- `downloads/59120224 (3).pdf`
- `downloads/59120224.pdf`
