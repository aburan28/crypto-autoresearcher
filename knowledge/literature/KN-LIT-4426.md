---
id: KN-LIT-4426
type: literature
title: "Improved Private Set Intersection against Malicious Adversaries"
authors:
  - "Peter Rindal"
  - "Mike Rosulek∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, protocol, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Private set intersection (PSI) refers to a special case of secure two-party computation in which the parties each have a set of items and compute the intersection of these sets without revealing any additional information. In this paper we present improvements to practical PSI providing security in the presence of malicious adversaries.

## Key claims (as reported)
- Our starting point is the protocol of Dong, Chen & Wen (CCS 2013) that is based on Bloom filters.
- We identify a bug in their malicious-secure variant and show how to fix it using a cut-and-choose approach that has low overhead while simultaneously avoiding one the main computational bottleneck in their original protocol.
- We also point out some subtleties that arise when using Bloom filters in malicious-secure cryptographic protocols.
- We have implemented our PSI protocols and report on its performance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210137 (1).pdf`
- `downloads/10210137.pdf`
