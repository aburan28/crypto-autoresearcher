---
id: KN-LIT-3263
type: literature
title: "Cryptanalysis of the DECT Standard Cipher"
authors:
  - "Karsten Nohl"
  - "Erik Tews"
  - "Ralf-Philipp Weinmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The DECT Standard Cipher (DSC) is a proprietary 64-bit stream cipher based on irregularly clocked LFSRs and a non-linear output combiner. The cipher is meant to provide confidentiality for cordless telephony.

## Key claims (as reported)
- This paper illustrates how the DSC was reverse-engineered from a hardware implementation using custom firmware and information on the structure of the cipher gathered from a patent.
- Beyond disclosing the DSC, the paper proposes a practical attack against DSC that recovers the secret key from 215 keystreams on a standard PC with a success rate of 50% within hours; somewhat faster when a CUDA graphics adapter is available.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470001 (1).pdf`
- `downloads/61470001 (2).pdf`
- `downloads/61470001 (3).pdf`
- `downloads/61470001.pdf`
