---
id: KN-LIT-3115
type: literature
title: "Constant-round Leakage-resilient Zero-knowledge from Collision Resistance"
authors:
  - "Susumu Kiyoshima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, side-channel, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a constant-round leakage-resilient zero-knowledge argument system under the existence of collision-resistant hash function family. That is, using collision-resistant hash functions, we construct a constant-round zero-knowledge argument system such that for any cheating verifier that can obtain arbitrary amount of leakage of the prover’s state, there exists a simulator that can simulate the adversary’s view by obtaining at most the same amount of leakage of the witness.

## Key claims (as reported)
- Previously, leakage-resilient zero-knowledge protocols were constructed only under a relaxed security definition (Garg-Jain-Sahai, CRYPTO’11) or under the DDH assumption (Pandey, TCC’14).
- Our leakage-resilient zero-knowledge argument system satisfies an additional property that it is simultaneously leakage-resilient zero-knowledge, meaning that both zero-knowledgeness and soundness hold in the presence of leakage.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650114 (1).pdf`
- `downloads/96650114.pdf`
