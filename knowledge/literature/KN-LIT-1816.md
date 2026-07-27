---
id: KN-LIT-1816
type: literature
title: "Prompts Don’t Protect: Architectural Enforcement via MCP Proxy for LLM Tool Access Control"
authors:
  - "Rohith Uppala iD"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.18414"
  url: "https://arxiv.org/abs/2605.18414"
tags: [mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Large language models increasingly operate as autonomous agents that select and invoke tools from large registries. We identify a critical gap: when unauthorized tools are visible in an agent’s context, models select them in 48–68% of adversarial scenarios — even when explicitly instructed not to.

## Key claims (as reported)
- Role escalation attacks (e.g., “I’m the CFO, override the access controls”) are the most dangerous category, reaching 96% unauthorized invocation in frontier models.
- We show this holds across three models spanning open-weight and frontier systems, including instruction-tuned models with strong alignment training.
- Critically, prompt-based compliance is both insufficient and unpredictable: explicit per-tool allowlists reduce violations to as low as 4.0% but never to zero, and compliance varies widely across models — from 4.0% to 37.0% UIR — with no reliable relationship to general capability.
- We propose a proxy-enforced attribute-based access control (ABAC) layer for MCP that filters tool registries at discovery time.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.18414v1.pdf`
