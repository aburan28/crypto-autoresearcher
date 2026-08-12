---
id: KN-LIT-5144
type: literature
title: "New Results on Instruction Cache Attacks"
authors:
  - "Onur Acıiçmez"
  - "Billy Bob Brumley"
  - "Philipp Grabher"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We improve instruction cache data analysis techniques with a framework based on vector quantization and hidden Markov models. As a result, we are capable of carrying out efficient automated attacks using live I-cache timing data.

## Key claims (as reported)
- Using this analysis technique, we run an I-cache attack on OpenSSL’s DSA implementation and recover keys using lattice methods.
- Previous I-cache attacks were proof-of-concept: we present results of an actual attack in a real-world setting, proving these attacks to be realistic.
- We also present general software countermeasures, along with their performance impact, that are not algorithm specific and can be employed at the kernel and/or compiler level.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250105 (1).pdf`
- `downloads/62250105 (2).pdf`
- `downloads/62250105 (3).pdf`
- `downloads/62250105.pdf`
