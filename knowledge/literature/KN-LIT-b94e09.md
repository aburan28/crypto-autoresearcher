---
id: KN-LIT-b94e09
type: literature
title: 'A Verified Constructive Reduction of the Cook-Levin Theorem in Lean 4: Bridging
  the Gap Between Complexity Theory and Formal SAT Encodings'
authors:
- Jonathan 𝑓(n) Reed
year: 2026
venue: hexagon:2610.00152v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00152v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 6f4a167d35e3f32455160a0ef1bddb55d3400bd9ba1807e338948367ea201cbb
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00152v1](https://hexagonmath.org/pdf/2610.00152v1); PDF SHA-256 `6f4a167d35e3f32455160a0ef1bddb55d3400bd9ba1807e338948367ea201cbb`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

A concrete machine-to-CNF reduction needs injective variable indexing and encoding soundness. A high-level theorem alone does not certify an emitted solver instance.

- Check indexing domains, boundary times, initialization, transitions and acceptance
- Record auxiliary-variable growth
- The claimed complete formalization needs a statement and axiom audit

## Integration and evidence boundary

Status: `research_constraint`. Lean snippets and claimed formalization in paper; complete source build not independently reproduced.

- `crypto:src/cryptanalysis/sat.rs`
- `crypto:src/cryptanalysis/semaev_sat.rs`
- `crypto:crates/hashed-ecdl-tensor/src/network.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
