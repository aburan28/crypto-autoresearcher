---
id: KN-LIT-4946
type: literature
title: "Modular Security Specifications Framework"
authors:
  - "Amir Herzberg"
  - "Hemi Leibowitz"
  - "Ewa Syta"
  - "Sara Wrótniak"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Applied cryptographic protocols have to meet a rich set of security requirements under diverse environments and against diverse adversaries. However, currently used security specifications, based on either simulation [11,28] (e.g., ‘ideal functionality’ in UC) or games [8,30], are monolithic, combining together different aspects of protocol requirements, environment and assumptions.

## Key claims (as reported)
- Such security specifications are complex, error-prone, and foil reusability, modular analysis and incremental design.
- We present the Modular Security Specifications (MoSS) framework, which cleanly separates the security requirements (goals) which a protocol should achieve, from the models (assumptions) under which each requirement should be ensured.
- This modularity allows us to reuse individual models and requirements across different protocols and tasks, and to compare protocols for the same task, either under different assumptions or satisfying different sets of requirements.
- MoSS is flexible and extendable, e.g., it can support both asymptotic and concrete definitions for security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826185 (1).pdf`
- `downloads/12826185.pdf`
