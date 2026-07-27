---
id: KN-LIT-2641
type: literature
title: "Automated Unbounded Analysis of Cryptographic Constructions in the Generic Group Model"
authors:
  - "Miguel Ambrona"
  - "Gilles Barthe"
  - "Benedikt Schmidt"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We develop a new method to automatically prove security statements in the Generic Group Model as they occur in actual papers. We start by defining (i) a general language to describe security definitions, (ii) a class of logical formulas that characterize how an adversary can win, and (iii) a translation from security definitions to such formulas.

## Key claims (as reported)
- We prove a Master Theorem that relates the security of the construction to the existence of a solution for the associated logical formulas.
- Moreover, we define a constraint solving algorithm that proves the security of a construction by proving the absence of solutions.
- We implement our approach in a fully automated tool, the gga∞ tool, and use it to verify different examples from the literature.
- The results improve on the tool by Barthe et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650340 (1).pdf`
- `downloads/96650340.pdf`
