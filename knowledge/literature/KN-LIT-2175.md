---
id: KN-LIT-2175
type: literature
title: "A one-time single-bit fault leaks all previous NTRU-HRSS session keys to a chosen-ciphertext attack"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents an efficient attack that, in the standard IND-CCA2 attack model plus a one-time single-bit fault, recovers the NTRU-HRSS session key. This type of fault is expected to occur for many users through natural DRAM bit flips.

## Key claims (as reported)
- In a multi-target IND-CCA2 attack model plus a one-time single-bit fault, the attack recovers every NTRU-HRSS session key that was encapsulated to the targeted public key before the fault.
- Software carrying out the full multi-target attack, using a simulated fault, is provided for verification.
- This paper also explains how a change in NTRU-HRSS in 2019 enabled this attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ntrw-20220829.pdf`
- `downloads/ntrw-20221025.pdf`
