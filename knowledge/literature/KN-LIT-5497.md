---
id: KN-LIT-5497
type: literature
title: "On the Impossibility of Highly-Efficient Blockcipher-Based Hash Functions"
authors:
  - "John Black"
  - "Martin Cochran"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fix a small, non-empty set of blockcipher keys K. We say a blockcipher-based hash function is highly-efficient if it makes exactly one blockcipher call for each message block hashed, and all blockcipher calls use a key from K.

## Key claims (as reported)
- Although a few highly-efficient constructions have been proposed, no one has been able to prove their security.
- In this paper we prove, in the ideal-cipher model, that it is impossible to construct a highly-efficient iterated blockcipher-based hash function that is provably secure.
- Our result implies, in particular, that the Tweakable Chain Hash (TCH) construction suggested by Liskov, Rivest, and Wagner [7] is not correct under an instantiation suggested for this construction, nor can TCH be correctly instantiated by any other efficient means.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/34940527 (1).pdf`
- `downloads/34940527 (2).pdf`
- `downloads/34940527 (3).pdf`
- `downloads/34940527.pdf`
