---
id: KN-LIT-e1b37e
type: literature
title: Deterministic Factoring in Time $N^{o(1)}$
authors:
- Isaac Rudich
- Louis-Martin Rousseau
year: 2026
venue: hexagon:2610.00600v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00600v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: e57f24481d2474a6f2c342d86312572f024710835ca583beb31e2bb1f9ceae40
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00600v1](https://hexagonmath.org/pdf/2610.00600v1); PDF SHA-256 `e57f24481d2474a6f2c342d86312572f024710835ca583beb31e2bb1f9ceae40`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Count nontrivial divisors by binary prefix, choose the least feasible prefix, and repeat smallest-factor extraction for complete factorization.

- One fixed machine in the asymptotic statement
- The local counter is OpenAI-based, not the paper's Anthropic engine
- The stronger sqrt-log-log rate is a conjecture

## Integration and evidence boundary

Status: `implemented_reduction`. Theorem 1 reported Lean-checked; Theorem 2 is a written corollary; source proof not rebuilt locally.

- `crypto:crates/hashed-ecdl-tensor/src/factoring.rs`
- `crypto:crates/hashed-ecdl-tensor/src/bin/tensor-factor.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
