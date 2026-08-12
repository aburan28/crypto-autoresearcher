---
id: KN-LIT-1735
type: literature
title: "MIPSBLEED: Uncovering Microarchitectural Timing Leaks in Pervasive Embedded Processors"
authors:
  - "Ahmed Najeeb"
  - "Billy Bob Brumley"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2606.16372"
  url: "https://arxiv.org/abs/2606.16372"
tags: [cryptanalysis, elliptic-curve, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Despite their age, MIPS processors remain deeply embedded in routers, industrial controllers, and IoT systems, yet their security against modern side-channel attacks has received little attention. This paper exposes how Simultaneous Multithreading (SMT), a feature increasingly used to boost performance in these environments, creates powerful cross-core timing channels on MIPS-based platforms.

## Key claims (as reported)
- We introduce MIPSBLEED, a systematic analysis and exploitation framework that uncovers leakage in three shared microarchitectural components: the L1 data cache, L1 instruction cache, and the execution engine.
- Through carefully crafted assembly-level probes and quantitative leakage assessment, we demonstrate practical, high-resolution timing attacks that operate without requiring privileged access.
- Our evaluation reveals significant information leakage across all three channels and culminates in a single trace key recovery attack on a real elliptic curve cryptographic toolkit.
- These results position MIPS as an overlooked yet critical target in the study of microarchitectural security and underscore the urgent need for lightweight isolation mechanisms in resource-constrained, SMTenabled embedded systems.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2606.16372v2.pdf`
