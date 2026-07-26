---
id: KN-LIT-6248
type: literature
title: "Reverse Cycle Walking and Its Applications"
authors:
  - "Sarah Miracle"
  - "Scott Yilek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of constructing a block-cipher on a “possibly-strange” set S using a block-cipher on a larger set T . Such constructions are useful in format-preserving encryption, where for example the set S might contain “valid 9-digit social security numbers” while T might be the set of 30-bit strings.

## Key claims (as reported)
- Previous work has solved this problem using a technique called cycle walking, first formally analyzed by Black and Rogaway.
- Assuming the size of S is a constant fraction of the size of T , cycle walking allows one to encipher a point x ∈ S by applying the block-cipher on T a small expected number of times and O(N ) times in the worst case, where N = |T |, without any degradation in security.
- We introduce an alternative to cycle walking that we call reverse cycle walking, which lowers the worst-case number of times we must apply the block-cipher on T from O(N ) to O(log N ).
- Additionally, when the underlying block-cipher on T is secure against q = (1 − )N adversarial queries, we show that applying reverse cycle walking gives us a cipher on S secure even if the adversary is allowed to query all of the domain points.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031217 (1).pdf`
- `downloads/10031217.pdf`
