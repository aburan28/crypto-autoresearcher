---
id: KN-LIT-7082
type: literature
title: "The TinyTable protocol for 2-Party Secure Computation, or: Gate-scrambling Revisited"
authors:
  - "Ivan Damgård"
  - "Jesper Buus Nielsen"
  - "Michael Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new protocol, nicknamed TinyTable, for maliciously secure 2-party computation in the preprocessing model. One version of the protocol is useful in practice and allows, for instance, secure AES encryption with latency about 1ms and amortized time about 0.5 μs per AES block on a fast cloud set-up.

## Key claims (as reported)
- Another version is interesting from a theoretical point of view: we achieve a maliciously and unconditionally secure 2-party protocol in the preprocessing model for computing a Boolean circuit, where both the communication complexity and preprocessed data size needed is O(s) where s is the circuit size, while the computational complexity is O(k s) where k is the statistical security parameter and  < 1 is a constant.
- For general circuits with no assumption on their structure, this is the best asymptotic performance achieved so far in this model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401199 (1).pdf`
- `downloads/10401199.pdf`
