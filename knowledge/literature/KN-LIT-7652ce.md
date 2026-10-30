---
id: KN-LIT-7652ce
type: literature
title: Deterministic Integer 3SUM in O(n^1.999017) Time via a Sharper Binomial-Tail
  Analysis
authors:
- 宇轩 徐
year: 2026
venue: hexagon:2610.00221v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00221v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: c3f7f56b1ace91a623f6651aaef45cf4ada0af7bd7687c241a5e42ca5efdaff5
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00221v1](https://hexagonmath.org/pdf/2610.00221v1); PDF SHA-256 `c3f7f56b1ace91a623f6651aaef45cf4ada0af7bd7687c241a5e42ca5efdaff5`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Keeping the binomial tail in a preprocessing analysis gives a smaller 3SUM exponent within an inherited thin-matrix/Exact-Triangle framework.

- Polynomially bounded integers and logarithmic word size
- Three distinct input indices, even when values coincide
- Include preprocessing, prime selection, query and witness costs

## Integration and evidence boundary

Status: `research_constraint`. Exact rational interval certificates reported; improved runtime not Lean-formalized or locally implemented.

- `crypto:src/cryptanalysis/ic_framework/planner.rs`
- `crypto:research/hexagon_cscc_20261030/README.md`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
