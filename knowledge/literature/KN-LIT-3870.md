---
id: KN-LIT-3870
type: literature
title: "FHE-Based Bootstrapping of Designated-Prover NIZK"
authors:
  - "Zvika Brakerski"
  - "Sanjam Garg"
  - "Rotem Tsabary"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a novel tree-based technique that can convert any designated-prover NIZK proof system (DP-NIZK) which maintains zero-knowledge only for single statement, into one that allows to prove an unlimited number of statements in ZK, while maintaining all parameters succinct. Our transformation requires leveled fully-homomorphic encryption.

## Key claims (as reported)
- We note that single-statement DP-NIZK can be constructed from any one-way function.
- We also observe a two-way derivation between DP-NIZK and attribute-based signatures (ABS), and as a result derive now constructions of ABS and homomorphic signatures (HS).
- Our construction improves upon the prior construction of lattice-based DP-NIZK by Kim and Wu (Crypto 2018) since we only require leveled FHE as opposed to HS (which also translates to improved LWE parameters when instantiated).
- Alternatively, the recent construction of NIZK without preprocessing from either circular-secure FHE (Canetti et al., STOC 2019) or polynomial Learning with Errors (Peikert and Shiehian, Crypto 2019) could be used to obtain a similar final statement.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550232 (1).pdf`
- `downloads/12550232.pdf`
