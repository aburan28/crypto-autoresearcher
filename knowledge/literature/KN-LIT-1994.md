---
id: KN-LIT-1994
type: literature
title: "A (Second) Preimage Attack on the GOST Hash Function"
authors:
  - "Florian Mendel"
  - "Norbert Pramstaller"
  - "Christian Rechberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we analyze the security of the GOST hash function with respect to (second) preimage resistance. The GOST hash function, defined in the Russian standard GOST-R 34.11-94, is an iterated hash function producing a 256-bit hash value.

## Key claims (as reported)
- As opposed to most commonly used hash functions such as MD5 and SHA-1, the GOST hash function defines, in addition to the common iterated structure, a checksum computed over all input message blocks.
- This checksum is then part of the final hash value computation.
- For this hash function, we show how to construct second preimages and preimages with a complexity of about 2225 compression function evaluations and a memory requirement of about 238 bytes.
- First, we show how to construct a pseudo-preimage for the compression function of GOST based on its structural properties.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860224 (1).pdf`
- `downloads/50860224 (2).pdf`
- `downloads/50860224 (3).pdf`
- `downloads/50860224.pdf`
