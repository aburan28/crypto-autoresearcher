---
id: KN-LIT-2402
type: literature
title: "Algebraic Meet-in-the-Middle Attack on LowMC"
authors:
  - "Fukang Liu"
  - "Santanu Sarkar"
  - "Gaoli Wang"
  - "Willi Meier"
  - "Takanori Isobe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, hash, mov-fr, mpc, pairing, pqc, prime-field, signature, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
By exploiting the feature of partial nonlinear layers, we propose a new technique called algebraic meet-in-the-middle (MITM) attack to analyze the security of LowMC, which can reduce the memory complexity of the simple difference enumeration attack over the state-of-the-art. Moreover, while an efficient algebraic technique to retrieve the full key from a differential trail of LowMC has been proposed at CRYPTO 2021, its time complexity is still exponential in the key size.

## Key claims (as reported)
- In this work, we show how to reduce it to constant time when there are a sufficiently large number of active S-boxes in the trail.
- With the above new techniques, the attacks on LowMC and LowMC-M published at CRYPTO 2021 are further improved, and some LowMC instances could be broken for the first time.
- Our results seem to indicate that partial nonlinear layers are still not well-understood.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910089 (1).pdf`
- `downloads/137910089.pdf`
