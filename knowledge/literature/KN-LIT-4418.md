---
id: KN-LIT-4418
type: literature
title: "Improved Masking for Tweakable Blockciphers with Applications to Authenticated Encryption"
authors:
  - "Robert Granger"
  - "Philipp Jovanovic"
  - "Bart Mennink"
  - "Samuel Neves"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, finite-field, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A popular approach to tweakable blockcipher design is via masking, where a certain primitive (a blockcipher or a permutation) is preceded and followed by an easy-to-compute tweak-dependent mask. In this work, we revisit the principle of masking.

## Key claims (as reported)
- We do so alongside the introduction of the tweakable Even-Mansour construction MEM.
- Its masking function combines the advantages of word-oriented LFSR- and powering-up-based methods.
- We show in particular how recent advancements in computing discrete logarithms over finite fields of characteristic 2 can be exploited in a constructive way to realize highly efficient, constanttime masking functions.
- If the masking satisfies a set of simple conditions, then MEM is a secure tweakable blockcipher up to the birthday bound.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650279 (1).pdf`
- `downloads/96650279.pdf`
