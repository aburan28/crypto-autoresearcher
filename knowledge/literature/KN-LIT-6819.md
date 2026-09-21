---
id: KN-LIT-6819
type: literature
title: "Strengthening Zero-Knowledge Protocols Using Signatures"
authors:
  - "Juan A. Garay"
  - "Philip MacKenzie"
  - "Ke Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently there has been an interest in zero-knowledge protocols with stronger properties, such as concurrency, unbounded simulation soundness, non-malleability, and universal composability. In this paper, we show a novel technique to convert a large class of existing honest-verifier zero-knowledge protocols into ones with these stronger properties in the common reference string model.

## Key claims (as reported)
- More precisely, our technique utilizes a signature scheme existentially unforgeable against adaptive chosen-message attacks, and transforms any Σ-protocol (which is honest-verifier zero-knowledge) into an unbounded simulation sound concurrent zero-knowledge protocol.
- We also introduce Ω-protocols, a variant of Σ-protocols for which our technique further achieves the properties of non-malleability and/or universal composability.
- In addition to its conceptual simplicity, a main advantage of this new technique over previous ones is that it avoids the Cook-Levin theorem, which tends to be rather inefficient.
- Indeed, our technique allows for very efficient instantiation based on the security of some efficient signature schemes and standard number-theoretic assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560177 (1).pdf`
- `downloads/26560177 (2).pdf`
- `downloads/26560177.pdf`
