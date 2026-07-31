---
id: KN-LIT-7203
type: literature
title: "Towards Accountability in CRS Generation"
authors:
  - "Prabhanjan Ananth"
  - "Gilad Asharov"
  - "Hila Dahari"
  - "Vipul Goyal"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
It is well known that several cryptographic primitives cannot be achieved without a common reference string (CRS). Those include, for instance, non-interactive zero-knowledge for NP, or maliciously secure computation in fewer than four rounds.

## Key claims (as reported)
- The security of those primitives heavily relies upon on the assumption that the trusted authority, who generates the CRS, does not misuse the randomness used in the CRS generation.
- However, we argue that there is no such thing as an unconditionally trusted authority and every authority must be held accountable for any trust to be well-founded.
- Indeed, a malicious authority can, for instance, recover private inputs of honest parties given transcripts of the protocols executed with respect to the CRS it has generated.
- While eliminating trust in the trusted authority may not be entirely feasible, can we at least move towards achieving some notion of accountability?

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960266 (1).pdf`
- `downloads/126960266.pdf`
