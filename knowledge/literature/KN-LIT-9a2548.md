---
id: KN-LIT-9a2548
type: literature
title: A Three-Polynomial Counterexample to the Generalized Effective Hypercube Nullstellensatz
authors:
- YURAN XIU
year: 2026
venue: hexagon:2610.00327v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00327v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 46867c11115644eb3b98df259fd21398a9ee17b360e8316670cdcd710c9e06ee
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00327v1](https://hexagonmath.org/pdf/2610.00327v1); PDF SHA-256 `46867c11115644eb3b98df259fd21398a9ee17b360e8316670cdcd710c9e06ee`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Three low-degree Boolean generators can require unbounded reduced-product certificate degree even when their product is zero. Selector gadgets preserve hard faces.

- Real coefficients and Boolean-cube multilinearization
- Does not contradict the two-generator theorem
- Input degree alone does not bound certificate or solving degree

## Integration and evidence boundary

Status: `bounded_control`. Unbounded theorem reported Lean-checked; local controls only check finite witness properties.

- `crypto:tools/complexity-catalog/src/controls.rs`
- `crypto:src/cryptanalysis/groebner_f4.rs`
- `crypto:src/cryptanalysis/f4_fp_tower.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
