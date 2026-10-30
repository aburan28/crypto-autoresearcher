---
id: KN-LIT-b972e0
type: literature
title: Subset Sum in time O(2^{0.4877n})
authors:
- Annanay Kapila
year: 2026
venue: hexagon:2610.00261v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00261v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 1fa891e6ce4a32a171977e9f00c6d24f6bf54f6586d5e16a8d5e09bdf9caca32
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00261v1](https://hexagonmath.org/pdf/2610.00261v1); PDF SHA-256 `1fa891e6ce4a32a171977e9f00c6d24f6bf54f6586d5e16a8d5e09bdf9caca32`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Phase-summed aliases and a pattern-selected checksum-filter family refine a randomized Subset Sum algorithm; checksums must not silently discard repeated representations.

- Polynomially bounded input bit lengths
- Uniform randomized word-RAM algorithm with bounded error
- Arb certificates verify numerical inequalities, not the entire algorithm

## Integration and evidence boundary

Status: `research_constraint`. Written proof importing an earlier algorithm plus numerical certificates; fast Subset Sum engine not ported.

- `crypto:src/cryptanalysis/ic_framework/large_prime.rs`
- `crypto:research/hexagon_cscc_20261030/README.md`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
