---
id: KN-LIT-1870
type: literature
title: "Sequence-Level Security for Active Weighted Signature Reconfiguration"
authors:
  - "Sunghyeon Jo"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1013"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1013"
tags: [mov-fr, mpc, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Active weighted threshold signatures support dynamic changes to signer weights, thresholds, and committee membership. We show that local validity of weighted update operations is not a compositional security abstraction: a sequence of individually valid updates can move an initially sub-threshold coalition into an authorized reachable state.

## Key claims (as reported)
- We introduce rank-exposure guards, a compiler that enforces a reconstruction-safety invariant over live, stale, derivative, public, and transient signing material.
- The compiler wraps ledger-sound one-step update engines with atomic activation and old-epoch digest-bound transition certificates, lifting fixed-state weighted unforgeability and update soundness to sequence-level active unforgeability.
- We instantiate the compiler as REG-ADAPT, a guarded GLI reconfiguration scheme built around ADAPT-style local updates, and implement it on top of the public ADAPT Go artifact.
- Our evaluation shows that the artifact detects and rejects unsafe update sequences, while adding only microsecondscale metadata and rank-audit overhead.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1013.pdf`
