---
id: KN-LIT-3172
type: literature
title: "Correlated Pseudorandomness from Expand-Accumulate Codes"
authors:
  - "Elette Boyle"
  - "Geoffroy Couteau"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, mpc, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A pseudorandom correlation generator (PCG) is a recent tool for securely generating useful sources of correlated randomness, such as random oblivious transfers (OT) and vector oblivious linear evaluations (VOLE), with low communication cost. We introduce a simple new design for PCGs based on so-called expandaccumulate codes, which first apply a sparse random expander graph to replicate each message entry, and then accumulate the entries by computing the sum of each prefix.

## Key claims (as reported)
- Our design offers the following advantages compared to state-of-the-art PCG constructions: – Competitive concrete efficiency backed by provable security against relevant classes of attacks; – An offline-online mode that combines near-optimal cache-friendliness with simple parallelization; – Concretely efficient extensions to pseudorandom correlation functions, which enable incremental generation of new correlation instances on demand, and to new kinds of correlated randomness that include circuit-dependent correlations.
- To further improve the concrete computational cost, we propose a method for speeding up a full-domain evaluation of a puncturable pseudorandom function (PPRF).
- This is independently motivated by other cryptographic applications of PPRFs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070429 (1).pdf`
- `downloads/135070429.pdf`
