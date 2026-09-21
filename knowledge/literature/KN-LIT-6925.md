---
id: KN-LIT-6925
type: literature
title: "Tag Size Does Matter: Attacks and Proofs for the TLS Record Protocol"
authors:
  - "Kenneth G. Paterson"
  - "Thomas Ristenpart"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We analyze the security of the TLS Record Protocol, a MACthen-Encode-then-Encrypt (MEE) scheme whose design targets confidentiality and integrity for application layer communications on the Internet. Our main results are twofold.

## Key claims (as reported)
- First, we give a new distinguishing attack against TLS when variable length padding and short (truncated) MACs are used.
- This combination will arise when standardized TLS 1.2 extensions (RFC 6066) are implemented.
- Second, we show that when tags are longer, the TLS Record Protocol meets a new length-hiding authenticated encryption security notion that is stronger than IND-CCA.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730368 (1).pdf`
- `downloads/70730368 (2).pdf`
- `downloads/70730368 (3).pdf`
- `downloads/70730368.pdf`
