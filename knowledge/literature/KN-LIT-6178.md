---
id: KN-LIT-6178
type: literature
title: "Recovering the tight security proof of SPHINCS+"
authors:
  - "Andreas Hülsing"
  - "Mikhail Kudinov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2020, Kudinov, Kiktenko, and Fedorov pointed out a flaw in the tight security proof of the SPHINCS+ construction. This work gives a new tight security proof for SPHINCS+ .

## Key claims (as reported)
- The flaw can be traced back to the security proof for the Winternitz one-time signature scheme (WOTS) used within SPHINCS+ .
- In this work, we give a stand-alone description of the WOTS variant used in SPHINCS+ that we call WOTS-TW.
- We provide a security proof for WOTS-TW and multi-instance WOTS-TW against non-adaptive chosen message attacks where the adversary only learns the public key after it made its signature query.
- Afterwards, we show that this is sufficient to give a tight security proof for SPHINCS+ .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910192 (1).pdf`
- `downloads/137910192.pdf`
