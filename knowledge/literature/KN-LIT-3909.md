---
id: KN-LIT-3909
type: literature
title: "Flash Memory ‘Bumping’ Attacks"
authors:
  - "Sergei Skorobogatov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a new class of optical fault injection attacks called bumping attacks. These attacks are aimed at data extraction from secure embedded memory, which usually stores critical parts of algorithms, sensitive data and cryptographic keys.

## Key claims (as reported)
- As a security measure, read-back access to the memory is not implemented leaving only authentication and verification options for integrity check.
- Verification is usually performed on relatively large blocks of data, making brute force searching infeasible.
- This paper evaluates memory verification and AES authentication schemes used in secure microcontrollers and a highly secure FPGA.
- By attacking the security in three steps, the search space can be reduced from infeasible > 2100 to affordable ≈ 215 guesses per block of data.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250150 (1).pdf`
- `downloads/62250150 (2).pdf`
- `downloads/62250150 (3).pdf`
- `downloads/62250150.pdf`
