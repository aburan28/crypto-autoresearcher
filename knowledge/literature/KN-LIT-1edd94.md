---
id: KN-LIT-1edd94
type: literature
title: 'An Approximate Solution to the Minimum Vertex Cover Problem: The Salvador
  Algorithm'
authors:
- Frank Vega
year: 2026
venue: hexagon:2610.00337v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00337v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 1db96e3ef4968d3372ccd11e32148738b5d19382c778055fc64f86266157bfe3
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00337v1](https://hexagonmath.org/pdf/2610.00337v1); PDF SHA-256 `1db96e3ef4968d3372ccd11e32148738b5d19382c778055fc64f86266157bfe3`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

An ensemble's per-instance certificate must be separated from its conjectured universal approximation guarantee. Keep every heuristic arm and exact lower-bound witness.

- The universal 3/2 ratio remains conjectural
- The 2*tau-r bound has different scope
- Test-suite success is not a universal approximation proof

## Integration and evidence boundary

Status: `research_constraint`. Written bounds and empirical suite; stronger guarantee explicitly conjectured.

- `crypto:src/cryptanalysis/ic_framework/planner.rs`
- `crypto:research/hexagon_cscc_20261030/README.md`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
