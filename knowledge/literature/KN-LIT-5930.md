---
id: KN-LIT-5930
type: literature
title: "Programmable Distributed Point Functions"
authors:
  - "Elette Boyle"
  - "Niv Gilboa"
  - "Yuval Ishai"
  - "Victor I. Kolobov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A distributed point function (DPF) is a cryptographic primitive that enables compressed additive sharing of a secret unit vector across two or more parties. Despite growing ubiquity within applications and notable research efforts, the best 2-party DPF construction to date remains the tree-based construction from (Boyle et al, CCS’16), with no significantly new approaches since.

## Key claims (as reported)
- We present a new framework for 2-party DPF construction, which applies in the setting of feasible (polynomial-size) domains.
- This captures in particular all DPF applications in which the keys are expanded to the full domain.
- Our approach is motivated by a strengthened notion we put forth, of programmable DPF (PDPF): in which a short, inputindependent “offline” key can be reused for sharing many point functions. – PDPF from OWF.
- We construct a PDPF for feasible domains from the minimal assumption that one-way functions exist, where the second “online” key size is polylogarithmic in the domain size N .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070364 (1).pdf`
- `downloads/135070364.pdf`
