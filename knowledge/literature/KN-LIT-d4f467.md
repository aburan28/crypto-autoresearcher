---
id: KN-LIT-d4f467
type: literature
title: "Embedded Elliptic Curves and Embedded Families for SNARK-Friendly Elliptic Curves"
authors:
  - "Aurore Guillevic"
  - "Simon Masson"
year: 2024
venue: "Cryptology ePrint Archive / ACM CCS 2024 (paper 2024/1737)"
identifiers:
  eprint: iacr:2024/1737
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1737"
tags: [embedded-curve, snark, pairing, bandersnatch, cm-method, schnorr]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Systematizes and constructs *embedded* elliptic curves (defined over a field
of order equal to the group order of a pairing/signature-adjacent curve) used
in SNARKs. Revisits the Bandersnatch construction (Masson–Sanso–Zhang 2021)
built with the CM method (discriminant D = -8) for efficient scalar
multiplication and presents embedded *families* of curves, generalizing the
single-curve approach.

## Key claims (as reported)
- Embedded curve = curve over the group-order field of a target curve, so the
  zk-SNARK statement runs on E1 while the proof is expressed on E2; necessary
  for BN/BLS pairing-friendly baselines.
- Bandersnatch via CM with tiny discriminant enables very fast scalar
  multiplication.
- Generalizes to embedded families rather than isolated curves.

## Relevance
- In the ECDLP/baseline spine: scalar multiplication cost on embedded curves
  (Schnorr/BLS-style signatures with a small trace) is a common cost model
  cell. The paper's concrete curves (JubJub, CØCØ, Bandersnatch) serve as
  testbeds for the program's cost-modeling of pairing-based SNARKs and for
  ECDLP-in-subgroup baselines underpinning those schemes.

## Not verified here
- Concrete curve parameters / scalar-mult benchmarks come from the abstract;
  full sections (velocity tables, D field searches) not inspected for this
  entry.