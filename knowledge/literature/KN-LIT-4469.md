---
id: KN-LIT-4469
type: literature
title: "Incremental Proofs of Sequential Work"
authors:
  - "Nico Döttling"
  - "Russell W. F. Lai"
  - "Giulio Malavolta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A proof of sequential work allows a prover to convince a verifier that a certain amount of sequential steps have been computed. In this work we introduce the notion of incremental proofs of sequential work where a prover can carry on the computation done by the previous prover incrementally, without affecting the resources of the individual provers or the size of the proofs.

## Key claims (as reported)
- To date, the most efficient instance of proofs of sequential work √ [Cohen and Pietrzak, Eurocrypt 2018] for N steps require the prover to have N memory and √ to run for N + N steps.
- Using incremental proofs of sequential work we can bring down the prover’s storage complexity to log N and its running time to N .
- We propose two different constructions of incremental proofs of sequential work: Our first scheme requires a single processor and introduces a poly-logarithmic factor in the proof size when compared with the proposals of Cohen and Pietrzak.
- Our second scheme assumes log N parallel processors but brings down the overhead of the proof size to a factor of 9.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760353 (1).pdf`
- `downloads/114760353.pdf`
