---
id: KN-LIT-a81352
type: literature
title: The Euclidean algorithm is not optimal among uniform processes
authors:
- Jason Davies
year: 2026
venue: hexagon:2610.00604v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00604v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: c86443a64680722b8dc78d6c37b62720854d2d468fc5b640bd840844e31c161f
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00604v1](https://hexagonmath.org/pdf/2610.00604v1); PDF SHA-256 `c86443a64680722b8dc78d6c37b62720854d2d468fc5b640bd840844e31c161f`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Reusable Euclidean prefixes reduce remainder-only derivation length. Uniform-process existence does not by itself supply a faster finite-program gcd implementation.

- The cost counts remainder calls, not selection or bit complexity
- The Main Conjecture for algorithms remains open

## Integration and evidence boundary

Status: `research_constraint`. Main remainder-call bounds reported formalized; best-uniform-process theorem imported.

- `crypto:research/hexagon_cscc_20261030/README.md`
- `crypto:src/utils`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
