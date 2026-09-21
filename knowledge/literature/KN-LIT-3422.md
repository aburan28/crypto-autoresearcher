---
id: KN-LIT-3422
type: literature
title: "Differential Fault Analysis on DES Middle Rounds"
authors:
  - "Matthieu Rivain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Differential Fault Analysis (DFA) is a powerful cryptanalytic technique that disturbs cryptographic computations and exploits erroneous results to infer secret keys. Over the last decade, many works have described and improved DFA techniques against block ciphers thus showing an inherent need to protect their implementations.

## Key claims (as reported)
- A simple and widely used solution is to perform the computation twice and to check that the same result is obtained.
- Since DFA against block ciphers usually targets the last few rounds, one does not need to protect the whole ciphering thus saving computation time.
- However the number of rounds to protect must be chosen very carefully in order to prevent security flaws.
- To determine this number, one must study DFA targeting middle rounds of the cipher.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470460 (1).pdf`
- `downloads/57470460 (2).pdf`
- `downloads/57470460 (3).pdf`
- `downloads/57470460.pdf`
