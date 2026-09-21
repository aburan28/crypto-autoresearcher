---
id: KN-LIT-081
type: literature
title: On Reduction Probability Models in Lattice Sieving
authors: [Marc Stevens, Michael Yonli]
year: 2026
venue: Cryptology ePrint Archive, Report 2026/1465
identifiers:
  eprint: 2026/1465
  doi: null
  url: https://eprint.iacr.org/2026/1465
tags: [ml-kem, lattice-sieving, reduction-probability, sphere-model, ball-model, cost-estimation, memory]
confidence: reported
citation_verified: full_text
added: 2026-07-23
superseded_by: null
---

> **ID remapping (2026-07-24):** originally filed as `KN-LIT-027` on the ML-KEM branch; renumbered to `KN-LIT-081` to resolve an add/add collision with `main`'s Gröbner knowledge corpus. Historical archive commits retain the old path. See `ledger/corrections/CORR-20260724-001.yaml`.


## Contribution

Derives exact reduction-probability and output-length distributions for sphere,
uniform-ball, and selected nonuniform isotropic-ball models. Within the stated
iid model, the sphere-to-ball reduction-probability advantage is asymptotically
constant rather than exponential.

## Verified scope

- The sign-matched uniform-ball factors approach 2.25 for global and 1.5 for
  local reductions. The larger headline factors compare optimized-sign ball
  cases with a fixed-sign sphere denominator.
- All stated admissible models preserve the
  \((3/4)^{n/2}/\sqrt n\) probability scale and the approximately
  \(0.2075187n\) list exponent.
- The local Lemma 1 prints `min`, while definitions, proofs, and constants use
  `max`; the reported 1.5/3 constants are max-rule results.
- The nonuniform global limit would benefit from an explicit domination or
  tail-truncation argument before being treated as fully rigorous.

## ML-KEM relevance

The paper changes local model constants, not a sieve exponent or any current
ML-KEM security estimate. A valid concrete update must coherently propagate a
joint radial-angle-filter law through list supply, filters, recursion, memory,
routing, BKZ, and outer attack optimization. Subtracting the logarithm of a
local probability factor from a security estimate is invalid.

Reviewed in `EV-MLKEM-003` and `DEC-20260723-005`.
