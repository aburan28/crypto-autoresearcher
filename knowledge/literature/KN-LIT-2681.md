---
id: KN-LIT-2681
type: literature
title: "Better Security-Efficiency Trade-Offs in Permutation-Based Two-Party Computation"
authors:
  - "Yu Long Chen"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We improve upon the security of (tweakable) correlationrobust hash functions, which are essential components of garbling schemes and oblivious-transfer extension schemes. We in particular focus on constructions from permutations, and improve upon the work by Guo et al.

## Key claims (as reported)
- (IEEE S&P ’20) in terms of security and efficiency.
- We present a tweakable one-call construction which matches the security of the most secure two-call construction – the resulting security bound takes form O((p + q)q/2n ), where q is the number of construction evaluations and p is the number of direct adversarial queries to the underlying n-bit permutation, which is modeled as random.
- Moreover, we present a new two-call construction with much better security degradation – in particular, for applications of interest, where only a constant number of evaluations per tweak are made, the security degrades √ as O(( qp + q 2 )/2n ).
- Our security proof relies on on the sum-capture theorems (Babai 02; Steinberger 12, Cogliati and Seurin 18), as well as on new balls-into-bins combinatorial lemmas for limited independence ball-throws.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900168 (1).pdf`
- `downloads/130900168.pdf`
