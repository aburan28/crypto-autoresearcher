---
id: KN-LIT-7464
type: literature
title: "Verifiable Set Operations over Outsourced Databases?"
authors:
  - "Ran Canetti"
  - "Omer Paneth"
  - "Dimitrios Papadopoulos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of verifiable delegation of computation over outsourced data, whereby a powerful worker maintains a large data structure for a weak client in a verifiable way. Compared to the well-studied problem of verifiable computation, this setting imposes additional difficulties since the verifier also needs to check the consistency of updates succinctly and without maintaining large state.

## Key claims (as reported)
- We present a scheme for verifiable evaluation of hierarchical set operations (unions, intersections and set-differences) applied to a collection of dynamically changing sets of elements from a given domain.
- The verification cost incurred is proportional only to the size of the final outcome set and to the size of the query, and is independent of the cardinalities of the involved sets.
- The cost of updates is optimal (involving O(1) modular operations per update).
- Our construction extends that of [Papamanthou et al., CRYPTO 2011] and relies on a modified version of the extractable collision-resistant hash function (ECRH) construction, introduced in [Bitansky et al., ITCS 2012] that can be used to succinctly hash univariate polynomials.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830235 (1).pdf`
- `downloads/83830235 (2).pdf`
- `downloads/83830235 (3).pdf`
- `downloads/83830235 (4).pdf`
- `downloads/83830235 (5).pdf`
- `downloads/83830235.pdf`
