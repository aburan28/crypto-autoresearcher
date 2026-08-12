---
id: KN-LIT-5954
type: literature
title: "PrORAM Fast O(log n) Authenticated Shares ZK ORAM"
authors:
  - "David Heath"
  - "Vladimir Kolesnikov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a concretely efficient Zero Knowledge (ZK) Oblivious RAM (ORAM) for ZK Proof (ZKP) systems based on authenticated sharings of arithmetic values. It consumes 2 log n oblivious transfers (OTs) of length-2σ secrets per access of an arithmetic value, for statistical security parameter σ and array size n.

## Key claims (as reported)
- This is an asymptotic and concrete improvement over previous best (concretely efficient) ZK ORAM BubbleRAM of Heath and Kolesnikov ([HK20a], CCS 2020), whose access cost is 12 log2 n OTs of length-2σ secrets.
- ZK ORAM is essential for proving statements that are best expressed as RAM programs, rather than Boolean or arithmetic circuits.
- Our construction is private-coin ZK.
- We integrate it with [HK20a]’s ZKP protocol and prove the resulting ZKP system secure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900014 (1).pdf`
- `downloads/130900014.pdf`
