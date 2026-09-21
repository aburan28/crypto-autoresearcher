---
id: KN-LIT-7001
type: literature
title: "The IPS Compiler: Optimizations, Variants and Concrete Efficiency?"
authors:
  - "Yehuda Lindell"
  - "Eli Oxman"
  - "Benny Pinkas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent work, Ishai, Prabhakaran and Sahai (CRYPTO 2008) presented a new compiler (hereafter the IPS compiler) for constructing protocols that are secure in the presence of malicious adversaries without an honest majority, from protocols that are only secure in the presence of semi-honest adversaries. The IPS compiler has many important properties: it provides a radically different way of obtaining security in the presence of malicious adversaries with no honest majority, it is black-box in the underlying semi-honest protocol, and it has excellent asymptotic efficiency.

## Key claims (as reported)
- In this paper, we study the IPS compiler from a number of different angles.
- We present an efficiency improvement of the “watchlist setup phase” of the compiler that also facilitates a simpler and tighter analysis of the cheating probability.
- In addition, we present a conceptually simpler variant that uses protocols that are secure in the presence of covert adversaries as its basic building block.
- This variant can be used to achieve more efficient asymptotic security, as we show regarding black-box constructions of malicious oblivious transfer from semi-honest oblivious transfer.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410255 (1).pdf`
- `downloads/68410255 (2).pdf`
- `downloads/68410255 (3).pdf`
- `downloads/68410255.pdf`
