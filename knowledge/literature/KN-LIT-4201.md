---
id: KN-LIT-4201
type: literature
title: "High-Order Conversion From Boolean to Arithmetic Masking Jean-Sébastien Coron"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking with random values is an effective countermeasure against side-channel attacks. For cryptographic algorithms combining arithmetic and Boolean masking, it is necessary to switch from arithmetic to Boolean masking and vice versa.

## Key claims (as reported)
- Following a recent approach by Hutter and Tunstall, we describe a high-order Boolean to arithmetic conversion algorithm whose complexity is independent of the register size k.
- Our new algorithm is proven secure in the Ishai, Sahai and Wagner (ISW) framework for private circuits.
- In practice, for small orders, our new countermeasure is one order of magnitude faster than previous work.
- We also describe a 3rd-order attack against the 3rd-order Hutter-Tunstall algorithm, and a constant, 4th-order attack against the t-th order HutterTunstall algorithms, for any t ≥ 4.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529114 (1).pdf`
- `downloads/10529114.pdf`
