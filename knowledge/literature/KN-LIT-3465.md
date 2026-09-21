---
id: KN-LIT-3465
type: literature
title: "DORAM revisited: Maliciously secure RAM-MPC with logarithmic overhead"
authors:
  - "Brett Falk"
  - "Daniel Noble"
  - "Rafail Ostrovsky"
  - "Matan Shtepel"
  - "Jacob Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Distributed Oblivious Random Access Memory (DORAM) is a secure multiparty protocol that allows a group of participants holding a secret-shared array to read and write to secret-shared locations within the array. The efficiency of a DORAM protocol is measured by the amount of communication required per read/write query into the array.

## Key claims (as reported)
- DORAM protocols are a necessary ingredient for executing Secure Multiparty Computation (MPC) in the RAM model.
- Although DORAM has been widely studied, all existing DORAM protocols have focused on the setting where the DORAM servers are semihonest.
- Generic techniques for upgrading a semi-honest DORAM protocol to the malicious model typically increase the asymptotic communication complexity of the DORAM scheme.
- In this work, we present a 3-party DORAM protocol which requires O((κ+D) log N ) communication per query, for a database of size N with D-bit values, where κ is the security parameter.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369122 (1).pdf`
- `downloads/14369122.pdf`
