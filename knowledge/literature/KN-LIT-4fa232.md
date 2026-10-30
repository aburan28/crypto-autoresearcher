---
id: KN-LIT-4fa232
type: literature
title: On counting satisfying assignments via polynomial separation
authors:
- Scott Kominers
year: 2026
venue: hexagon:2610.00574v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00574v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 4d23c13745bb213808942364eda9e8972ab93bc143eeae0818c9c0a0a1e14552
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00574v1](https://hexagonmath.org/pdf/2610.00574v1); PDF SHA-256 `4d23c13745bb213808942364eda9e8972ab93bc143eeae0818c9c0a0a1e14552`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Separate the counting recovery interface from the construction supplying polynomial separation. Reconstruct exactly from Taylor data and Hermite interpolation.

- Account for construction, query and interpolation costs
- Qualitative epsilon-dependent constants are not concrete benchmark parameters

## Integration and evidence boundary

Status: `existing_backend_context`. Expository qualitative proof; independent implementation audit remains open.

- `crypto:crates/hashed-ecdl-tensor/src/contraction/deformation.rs`
- `crypto:crates/hashed-ecdl-tensor/src/contraction/recursive.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
