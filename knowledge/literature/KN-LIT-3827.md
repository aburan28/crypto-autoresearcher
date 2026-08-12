---
id: KN-LIT-3827
type: literature
title: "Faster batch forgery identification"
authors:
  - "Daniel J. Bernstein"
  - "Jeroen Doumen"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, hyperelliptic, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Batch signature verification detects whether a batch of signatures contains any forgeries. Batch forgery identification pinpoints the location of each forgery.

## Key claims (as reported)
- Existing forgery-identification schemes vary in their strategies for selecting subbatches to verify (individual checks, binary search, combinatorial designs, etc.) and in their strategies for verifying subbatches.
- This paper exploits synergies between these two levels of strategies, reducing the cost of batch forgery identification for ellipticcurve signatures.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/badbatch-20120919.pdf`
