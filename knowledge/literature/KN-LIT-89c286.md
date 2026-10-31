---
id: KN-LIT-89c286
type: literature
title: Set Cover by Cyclic Rotations Is NP-Complete
authors:
- YURAN XIU
year: 2026
venue: hexagon:2610.00307v2
identifiers:
  url: https://hexagonmath.org/abs/2610.00307v2
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 29362165430615aee9a3981d297220b75ac5a282e5b127c22c113c90830ae20e
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00307v2](https://hexagonmath.org/pdf/2610.00307v2); PDF SHA-256 `29362165430615aee9a3981d297220b75ac5a282e5b127c22c113c90830ae20e`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Restricting set cover to rotations of one pattern does not guarantee tractability. The reduction's full indicator word and binary budget are part of the complexity claim.

- Explicitly listed pattern
- All rotations and empty patterns included
- Cyclic symmetry alone does not imply a fast exact coverage selector

## Integration and evidence boundary

Status: `research_constraint`. Reduction, machine-level encoding and NP membership reported formalized.

- `crypto:src/cryptanalysis/ic_framework/subspace_select.rs`
- `crypto:research/hexagon_cscc_20261030/README.md`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
