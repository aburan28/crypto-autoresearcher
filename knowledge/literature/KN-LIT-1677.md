---
id: KN-LIT-1677
type: literature
title: "Heartbeat-Bound Hierarchical Credentials: Cryptographic Revocation for AI Agent Swarms"
authors:
  - "Saurabh Deochake"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.20704"
  url: "https://arxiv.org/abs/2605.20704"
tags: [cryptanalysis, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Autonomous AI agents that spawn sub-agent swarms create a safety gap: existing credential revocation mechanisms, OAuth 2.0 introspection, OCSP, and W3C Status Lists, require network connectivity to a central authority, leaving “zombie agents” executing privileged operations for minutes to hours after operator shutdown. We present HeartbeatBound Hierarchical Credentials (HBHC), a cryptographic protocol that binds credential validity to periodic parent liveness proofs.

## Key claims (as reported)
- Verifiers enforce freshness using only a cached public key and local clock; no network round-trip is required.
- When heartbeat generation ceases, all descendant credentials become unusable within a deterministically bounded window Wz ≤ Wmax +∆h +ε, conditional on bounded clock skew and parent keys held in secure enclaves.
- Evaluation at the protocol layer and with real LLM-backed agent swarms (GPT-4o-mini) demonstrates a 90× reduction in the zombie window over OAuth 2.0, 0.26 ms full authentication in Rust, 18,000+ verifications per second under concurrent HTTP load, and stable per-verification latency from 10 to 10,000 agents.
- Real-agent experiments show 0.71% end-to-end overhead on tool calls, zero postrevocation tool calls under prompt injection that bypasses applicationlayer guardrails, and cascading revocation across a 49-agent four-level hierarchy within the theoretical bound.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.20704v1.pdf`
