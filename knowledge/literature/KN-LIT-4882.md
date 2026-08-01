---
id: KN-LIT-4882
type: literature
title: "Meet-in-the-Middle and Impossible Differential Fault Analysis on AES"
authors:
  - "Patrick Derbez"
  - "Pierre-Alain Fouque"
  - "Delphine Leresteux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, rsa, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since the early work of Piret and Quisquater on fault attacks against AES at CHES 2003, many works have been devoted to reduce the number of faults and to improve the time complexity of this attack. This attack is very efficient as a single fault is injected on the third round before the end, and then it allows to recover the whole secret key in 232 in time and memory.

## Key claims (as reported)
- However, since this attack, it is an open problem to know if provoking a fault at a former round of the cipher allows to recover the key.
- Indeed, since two rounds of AES achieve a full diffusion and adding protections against fault attack decreases the performance, some countermeasures propose to protect only the three first and last rounds.
- In this paper, we give an answer to this problem by showing two practical cryptographic attacks on one round earlier of AES-128 and for all keysize variants.
- The first attack requires 10 faults and its complexity is around 240 in time and memory, an improvement allows only 5 faults and its complexity in memory is reduced to 224 while the second one requires either 1000 or 45 faults depending on fault model and recovers the secret key in around 240 in time and memory.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170275 (1).pdf`
- `downloads/69170275 (2).pdf`
- `downloads/69170275 (3).pdf`
- `downloads/69170275.pdf`
