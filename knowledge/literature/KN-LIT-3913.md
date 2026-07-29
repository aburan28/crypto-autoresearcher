---
id: KN-LIT-3913
type: literature
title: "FleXOR: Flexible garbling for XOR gates that beats free-XOR"
authors:
  - "Vladimir Kolesnikov"
  - "Payman Mohassel"
  - "Mike Rosulek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, mpc, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Most implementations of Yao’s garbled circuit approach for 2-party secure computation use the free-XOR optimization of Kolesnikov & Schneider (ICALP 2008). We introduce an alternative technique called flexible-XOR (fleXOR) that generalizes free-XOR and offers several advantages.

## Key claims (as reported)
- First, fleXOR can be instantiated under a weaker hardness assumption on the underlying cipher/hash function (related-key security only, compared to related-key and circular security required for freeXOR) while maintaining most of the performance improvements that free-XOR offers.
- Alternatively, even though XOR gates are not always “free” in our approach, we show that the other (non-XOR) gates can be optimized more heavily than what is possible when using free-XOR.
- For many circuits of cryptographic interest, this can yield a significantly (over 30%) smaller garbled circuit than any other known techniques (including free-XOR) or their combinations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160110 (1).pdf`
- `downloads/86160110 (2).pdf`
- `downloads/86160110 (3).pdf`
- `downloads/86160110 (4).pdf`
- `downloads/86160110 (5).pdf`
- `downloads/86160110 (6).pdf`
- (+1 more duplicate copies)
