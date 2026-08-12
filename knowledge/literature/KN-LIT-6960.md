---
id: KN-LIT-6960
type: literature
title: "The cryptoint library"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
C/C++ code is often designed to run in constant time so that secret information is not leaked through timings. This code relies on a variety of replacements for secret branches, secret comparisons, and secret bool.

## Key claims (as reported)
- However, this protection has been undermined by various “optimizations” in gcc and clang that sometimes introduce branches and timing variations into the assembly for C/C++ code where earlier compiler versions had generated constant-time assembly.
- The cryptoint library provides functions such as crypto_int64_max with implementations designed to defend against such “optimizations”.
- Some previous work aims at stopping compilers from introducing branches for conditional selection; cryptoint aims at stopping compilers from internally introducing any bool conditions in the first place.
- The cryptoint defenses include (1) usage of a global volatile zero variable for portable code and (2) assembly for various platforms.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/cryptoint-20250424.pdf`
