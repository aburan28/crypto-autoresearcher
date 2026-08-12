---
id: KN-LIT-6731
type: literature
title: "SoftSpokenOT: Quieter OT Extension From Small-Field Silent VOLE in the Minicrypt Model"
authors:
  - "Lawrence Roy⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, mpc, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given a small number of base oblivious transfers (OTs), how does one generate a large number of extended OTs as efficiently as possible? The answer has long been the seminal work of IKNP (Ishai et al., Crypto 2003) and the family of protocols it inspired, which only use Minicrypt assumptions.

## Key claims (as reported)
- Recently, Boyle et al.
- (Crypto 2019) proposed the Silent-OT technique that improves on IKNP, but at the cost of a much stronger, non-Minicrypt assumption: the learning parity with noise (LPN) assumption.
- We present SoftSpokenOT, the first OT extension to improve on IKNP’s communication cost in the Minicrypt model.
- While IKNP requires security parameter λ bits of communication for each OT, SoftSpokenOT only needs λ/k bits, for any k, at the expense of requiring 2k−1 /k times the computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070290 (1).pdf`
- `downloads/135070290.pdf`
