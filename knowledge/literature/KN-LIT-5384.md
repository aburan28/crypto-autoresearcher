---
id: KN-LIT-5384
type: literature
title: "On QA-NIZK in the BPK Model"
authors:
  - "Behzad Abdolmaleki"
  - "Helger Lipmaa"
  - "Janno Siim"
  - "Michał Zając"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, Bellare et al. defined subversion-resistance (security in the case the CRS creator may be malicious) for NIZK. In particular, a Sub-ZK NIZK is zero-knowledge, even in the case of subverted CRS.

## Key claims (as reported)
- We study Sub-ZK QA-NIZKs, where the CRS can depend on the language parameter.
- First, we observe that subversion zero-knowledge (SubZK) in the CRS model corresponds to no-auxiliary-string non-black-box NIZK in the Bare Public Key model, and hence, the use of non-blackbox techniques is needed to obtain Sub-ZK.
- Second, we give a precise definition of Sub-ZK QA-NIZKs that are (knowledge-)sound if the language parameter but not the CRS is subverted and zero-knowledge even if both are subverted.
- Third, we prove that the most efficient known QA-NIZK for linear subspaces by Kiltz and Wee is Sub-ZK under a new knowledge assumption that by itself is secure in (a weaker version of) the algebraic group model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110240 (1).pdf`
- `downloads/12110240.pdf`
