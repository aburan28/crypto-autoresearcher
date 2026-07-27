---
id: KN-LIT-3436
type: literature
title: "Direct Construction of Recursive MDS Diffusion Layers using Shortened BCH Codes"
authors:
  - "Daniel Augot"
  - "Matthieu Finiasz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
MDS matrices allow to build optimal linear diffusion layers in block ciphers. However, MDS matrices cannot be sparse and usually have a large description, inducing costly software/hardware implementations.

## Key claims (as reported)
- Recursive MDS matrices allow to solve this problem by focusing on MDS matrices that can be computed as a power of a simple companion matrix, thus having a compact description suitable even for constrained environments.
- However, up to now, finding recursive MDS matrices required to perform an exhaustive search on families of companion matrices, thus limiting the size of MDS matrices one could look for.
- In this article we propose a new direct construction based on shortened BCH codes, allowing to efficiently construct such matrices for whatever parameters.
- Unfortunately, not all recursive MDS matrices can be obtained from BCH codes, and our algorithm is not always guaranteed to find the best matrices for a given set of parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400109 (1).pdf`
- `downloads/85400109 (2).pdf`
- `downloads/85400109 (3).pdf`
- `downloads/85400109.pdf`
