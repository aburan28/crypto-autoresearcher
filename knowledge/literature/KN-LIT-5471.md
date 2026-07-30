---
id: KN-LIT-5471
type: literature
title: "On the Feasibility of Unclonable Encryption, and More"
authors:
  - "Prabhanjan Ananth"
  - "Fatih Kaleoglu Xingjian Li"
  - "Qipeng Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Unclonable encryption, first introduced by Broadbent and Lord (TQC’20), is a one-time encryption scheme with the following security guarantee: any non-local adversary (A, B, C) cannot simultaneously distinguish encryptions of two equal length messages. This notion is termed as unclonable indistinguishability.

## Key claims (as reported)
- Prior works focused on achieving a weaker notion of unclonable encryption, where we required that any nonlocal adversary (A, B, C) cannot simultaneously recover the entire message m.
- Seemingly innocuous, understanding the feasibility of encryption schemes satisfying unclonable indistinguishability (even for 1-bit messages) has remained elusive.
- We make progress towards establishing the feasibility of unclonable encryption. – We show that encryption schemes satisfying unclonable indistinguishability exist unconditionally in the quantum random oracle model. – Towards understanding the necessity of oracles, we present a negative result stipulating that a large class of encryption schemes cannot satisfy unclonable indistinguishability. – Finally, we also establish the feasibility of another closely related primitive: copy-protection for single-bit output point functions.
- Prior works only established the feasibility of copy-protection for multi-bit output point functions or they achieved constant security error for single-bit output point functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070396 (1).pdf`
- `downloads/135070396.pdf`
