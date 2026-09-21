---
id: KN-LIT-7529
type: literature
title: "XLS is not a Strong Pseudorandom Permutation"
authors:
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In FSE 2007, Ristenpart and Rogaway had described a generic method XLS to construct a length-preserving strong pseudorandom permutation (SPRP) over bit-strings of size at least n. It requires a lengthpreserving permutation E over all bits of size multiple of n and a blockcipher E with block size n.

## Key claims (as reported)
- The SPRP security of XLS was proved from the SPRP assumptions of both E and E.
- In this paper we disprove the claim by demonstrating a SPRP distinguisher of XLS which makes only three queries and has distinguishing advantage about 1/2.
- XLS uses a multi-permutation linear function, called mix2.
- In this paper, we also show that if we replace mix2 by any invertible linear functions, the construction XLS still remains insecure.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730197 (1).pdf`
- `downloads/88730197 (2).pdf`
- `downloads/88730197 (3).pdf`
- `downloads/88730197.pdf`
