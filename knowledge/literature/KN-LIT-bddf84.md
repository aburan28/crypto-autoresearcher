---
id: KN-LIT-bddf84
type: literature
title: What Does the Refutation of the Exponential Time Hypothesis Mean for Learning
  Theory?
authors:
- Xiaoyu Li
year: 2026
venue: hexagon:2610.00613v1
identifiers:
  url: https://hexagonmath.org/abs/2610.00613v1
tags:
- hexagon
- complexity
- source-integration
confidence: reported
citation_verified: read
provenance: retrieved
verified_by: Codex /root, 2026-10-30, statements and limits only
source_sha256: 0302872eb0536c1954fa0379fe94be26408cb7f76e5556b512bdfcc52dc91303
added: '2026-10-30'
superseded_by: null
---

## Source and review scope

[hexagon:2610.00613v1](https://hexagonmath.org/pdf/2610.00613v1); PDF SHA-256 `0302872eb0536c1954fa0379fe94be26408cb7f76e5556b512bdfcc52dc91303`. The primary PDF was retrieved and its statements and relevant limitations reviewed. The complete proof was not independently audited and no Lean build was run.

## Learning and applicability

Locality, description length, accuracy and coefficient representation govern the transfer from counting to learning and exact inference. Fixed-width SETH and unbounded-width CNF-SETH are different hypotheses.

- Bound the bits read by each local factor
- Include precision and sample/formula length
- Do not infer a bound for arbitrary dense models

## Integration and evidence boundary

Status: `reference_backend`. Imported ETH counting theorems and written reductions; no local formal verification.

- `crypto:crates/hashed-ecdl-tensor/src/weighted.rs`
- `crypto:src/ml_dataset`

Canonical snapshot and scoped report: `crypto:research/hexagon_cscc_20261030/`. Native software checks are not independent verification of the source runtime theorem. No program hypothesis, attack-cost claim or ledger status is promoted by this note.
