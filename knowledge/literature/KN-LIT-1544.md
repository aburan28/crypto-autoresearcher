---
id: KN-LIT-1544
type: literature
title: "An Evidence-driven Protocol for Trustworthy CI Pipelines"
authors:
  - "Fernando Castillo"
  - "Eduardo Brito"
  - "Pille Pullonen-Raudvere"
  - "Sebastian Werner"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.21089"
  url: "https://arxiv.org/abs/2605.21089"
tags: [provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Enterprise software supply chains are increasingly vulnerable to infrastructure attacks, resulting in financial and reputational damage. Ensuring the integrity and provenance of software artifacts remains a significant challenge, where re-execution of the build and tests by every consumer to guarantee provenance produces a verification bottleneck and credibility reduction.

## Key claims (as reported)
- This paper presents an evidence-driven protocol for trustworthy Continuous Integration (CI) pipelines that combines Deterministic Build Systems (DBS) with Trusted Execution Environments (TEEs).
- The approach provides cryptographically verifiable guarantees of integrity, authenticity, and attestation for CI artifacts in distributed environments, reducing implicit trust without requiring costly re-execution by consumers.
- We introduce a protocol that binds deterministic builds with TEEbased attestations, formalizing the evidence life cycle, together with a practical implementation using Nix and Intel TDX.
- Experimental results show that artifact verification is reduced from redundant computation to lightweight signature and policy checks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.21089v1.pdf`
