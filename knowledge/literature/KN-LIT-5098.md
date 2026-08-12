---
id: KN-LIT-5098
type: literature
title: "New Collision Attacks on Round-Reduced Keccak"
authors:
  - "Kexin Qiao"
  - "Ling Song"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we focus on collision attacks against Keccak hash function family and some of its variants. Following the framework developed by Dinur et al. at FSE 2012 where 4-round collisions were found by combining 3-round differential trails and 1-round connectors, we extend the connectors one round further hence achieve collision attacks for up to 5 rounds.

## Key claims (as reported)
- The extension is possible thanks to the large degree of freedom of the wide internal state.
- By linearization of all S-boxes of the first round, the problem of finding solutions of 2-round connectors are converted to that of solving a system of linear equations.
- However, due to the quick freedom reduction from the linearization, the system has solution only when the 3-round differential trails satisfy some additional conditions.
- We develop a dedicated differential trail search strategy and find such special differentials indeed exist.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210340 (1).pdf`
- `downloads/10210340.pdf`
