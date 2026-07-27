---
id: KN-FIND-007
type: finding
title: >-
  GLV/CM orbit folding of Semaev relations buys a bounded constant (save_IC ~ 3-6,
  flat over p ~ 2^12..2^24), not a scaling advantage; an apparent ~30x saving was
  a collection-free/small-c measurement artifact
tags: [semaev, index-calculus, glv, cm, endomorphism, symmetry, orbit-folding, factor-base, prime-field, ecdlp, bounded-constant, negative-result, external-corpus]
confidence: reported
status: established
source_refs: [KN-OPEN-003, KN-TECH-018, KN-TECH-012, KN-TECH-003, KN-LIT-004]
added: 2026-07-26
superseded_by: null
---

## Finding

Folding the lambda-redundant (GLV/CM) orbit relations of a Semaev index-calculus
system onto factor-L-fewer unknowns yields a **bounded constant** saving, not an
exponent improvement.

- Measured `save_IC ~ 3-6`, **flat** across p ~ 2^12 .. 2^24, for all five tested
  D = 5 mod 8 discriminants. Flat across 12 octaves of field size is the
  signature of a constant, not a scaling law.
- An earlier apparent **~30x** seed-efficiency was traced to a **measurement
  artifact**: a collection-free accounting (relation-collection cost excluded) at
  small `c`. Once collection is charged and `c` is realistic, the effect reduces
  to the bounded 3-6.
- The verifier passed 250/250 on the folded relations, so the effect is *real
  arithmetic*, just not *asymptotically useful*: no ECDLP break and no SCALLOP
  break follows.

This answers the prime-field half of KN-OPEN-003 in the negative for the
symmetry/endomorphism lane: curve symmetry reduces decomposition work by a
constant factor, in the same family as the classical GLV/GLS and negation-map
constant-factor rho speedups (KN-TECH-018), not by changing the exponent.

## Scope and limitations

- **External-corpus provenance.** Produced in a separate workspace
  (`/Volumes/Volume/research/isogeny-semaev/`, with `RESULTS_PILOT.md` and the
  scaling deliverables), *not* under this repo's ledger, contracts, or run-receipt
  discipline. It is not Coordinator-approved evidence here and has not been
  re-run under this harness. Treat as a strong prior, not as an internal EV record.
- Toy-to-moderate scale: p ~ 2^12..2^24 is far below crypto scale; the claim is
  about the *shape* of the curve (flat) over that range, not an asymptotic proof.
- Restricted to D = 5 mod 8 prime-order curves, which is where the fold is
  available; other discriminant classes were not swept.
- "Bounded constant" is an empirical verdict over the tested range, not a theorem.

## Evidence

- External: `/Volumes/Volume/research/isogeny-semaev/` — scaling sweep
  deliverables and `RESULTS_PILOT.md`; verifier 250/250.
- Companion result, same program: [KN-FIND-008](KN-FIND-008.md) (the alpha-stable
  enrichment that does *not* lower solving degree).
- Consistent in shape with [KN-FIND-006](KN-FIND-006.md) (bounded syzygy content).
