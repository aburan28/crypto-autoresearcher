---
id: KN-LIT-4f99af
type: literature
title: A Polynomial Separation for Adaptive Fourier-Overlap Parity Decision Trees
authors:
- YURAN XIU
year: 2026
venue: hexagon:2610.00308v2
identifiers:
  url: https://hexagonmath.org/abs/2610.00308v2
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: a744def9cfe67d4c1b0231b203660eceb5f2dc03abfd7db0a788e3ebdf083665
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00308v2](https://hexagonmath.org/pdf/2610.00308v2); PDF SHA-256 `a744def9cfe67d4c1b0231b203660eceb5f2dc03abfd7db0a788e3ebdf083665`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Maximizing Fourier-support overlap can force polynomial-depth parity trees under every adaptive tie policy, even when unrestricted parity trees have logarithmic depth.

- Lower bound concerns this support-overlap query rule only
- Characters must be nonconstant on the current affine domain
- A singleton Fourier support need not mean a constant function

## Integration and evidence boundary

Status: `research_constraint`. Adaptive separation reported Lean-checked; no general parity-tree lower bound claimed.

- `crypto:src/cryptanalysis/boolean.rs`
- `crypto:src/cryptanalysis/ic_framework/planner.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
