---
id: KN-LIT-c132ad
type: literature
title: The Exact Junta Bound for Degree-Two Boolean Functions on q-ary Hamming Cubes
authors:
- YURAN XIU
year: 2026
venue: hexagon:2610.00301v2
identifiers:
  url: https://hexagonmath.org/abs/2610.00301v2
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: b418c47224062e98a80c590f4a7fcd54703b8725d9436fae306e4d44dd39a5d6
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00301v2](https://hexagonmath.org/pdf/2610.00301v2); PDF SHA-256 `b418c47224062e98a80c590f4a7fcd54703b8725d9436fae306e4d44dd39a5d6`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Boolean functions of Hamming degree at most two over a q-symbol alphabet have at most max(4,q+1) relevant coordinates; the larger-than-four case has selector structure.

- Hamming/junta degree, not ordinary univariate polynomial degree
- Boolean output range
- The selector conclusion does not make every four-junta two-query

## Integration and evidence boundary

Status: `research_constraint`. Exact bound and selector structure reported formalized; no local proof replay.

- `crypto:src/cryptanalysis/boolean.rs`
- `crypto:crates/hashed-ecdl-tensor/src/weighted.rs`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
