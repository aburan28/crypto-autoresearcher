---
id: KN-LIT-3012
type: literature
title: "Compiler Assisted Masking"
authors:
  - "Andrew Moss"
  - "Elisabeth Oswald"
  - "Dan Page"
  - "Michael Tunstall"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Differential Power Analysis (DPA) attacks find a statistical correlation between the power consumption of a cryptographic device and intermediate values within the computation. Randomization via (Boolean) masking of intermediate values breaks this statistical dependence and thus prevents such attacks (at least up to a certain order).

## Key claims (as reported)
- Especially for software implementations, (first-order) masking schemes are popular in academia and industry, albeit typically not as the sole countermeasure.
- The current practice then is to manually ‘insert’ Boolean masks: essentially software developers need to manipulate low-level assembly language to implement masking.
- In this paper we make a first step to automate this process, at least for first-order Boolean masking, allowing the development of compilers capable of protecting programs against DPA.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280054 (1).pdf`
- `downloads/74280054 (2).pdf`
- `downloads/74280054 (3).pdf`
- `downloads/74280054.pdf`
