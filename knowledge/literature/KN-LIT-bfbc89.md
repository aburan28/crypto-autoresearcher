---
id: KN-LIT-bfbc89
type: literature
title: 'Polynomial Fault Detection Without Bounded Width: Exact Reachable Sets in
  Priority Controllers'
authors:
- Idris Ali Shaik
year: 2026
venue: hexagon:2610.00503v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00503v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: fc78672c5fd93457caa65d778b6b8eca4b6dde4308c907e58f27bf50ddfaf4cb
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00503v1](https://hexagonmath.org/pdf/2610.00503v1); PDF SHA-256 `fc78672c5fd93457caa65d778b6b8eca4b6dde4308c907e58f27bf50ddfaf4cb`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Exact reachable images can make a specified fault-detection problem tractable despite large native width. Changing the fault type, optimization objective or counting task changes complexity.

- Only the specified bridge fault and guarded-decoder class
- Do not transfer detection algorithms to minimum witnesses or counts
- Retain full native CNF encoding and witness replay

## Integration and evidence boundary

Status: `research_constraint`. Image statements reported formalized; broader algorithms and hardness are written arguments.

- `crypto:src/cryptanalysis/sat.rs`
- `crypto:src/cryptanalysis/prepared_sat_control.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
