# L1 Isogeny Corpus Baseline Notes

## Scope

This note records the generation of the deterministic baseline artifacts for
`TASK-20260807-c9c6e4`.

- Artifact bundle: `artifacts/isogeny_class_manifest.yaml`
- Baseline bundle: `artifacts/control_baseline_report.json`
- Seeds: `artifacts/seed_register.yaml`

## Generation command

Reproducibility command used for this lane:

```bash
sage -python coordination/goals/GOAL-ECDLP-001/proposals/NON-INDEX-ECDLP-III-20260807/artifacts/build_l1_isogeny_corpus_generator.sage
```

The script is stored in-repo at
`artifacts/build_l1_isogeny_corpus_generator.sage` and artifacts are frozen by
value in the manifest.

## Data contract satisfied in this lane

- At least three families were produced: `FAM-101-A`, `FAM-113-B`, `FAM-167-C`.
- Each family has at least two explicit isogeny chains (`isogeny_chains` entries C01/C02),
  each chain of length 2.
- Family curves include:
  - prime field modulus, short-Weierstrass coefficients `a4`, `a6`
  - `j_invariant`
  - `group_order` and `group_structure`
  - `trace_of_frobenius`
  - `two_torsion_rank` and `automorphism_count`
  - `order_factors`
- Controls included:
  - isomorphic-coordinate control (`CTRL-ISO`) derived by fixed scale transform
  - random cyclic matched-order control (`CTRL-CYCLIC`) with seeded search

## Control behavior assumptions

This lane is a **scaffolding corpus only**; no cryptanalytic claim is inferred at
this stage.

- `expected_rho_*` values are toy-scale synthetic envelopes computed from the
  deterministic curve profile (not an implemented Pollard rho run).
- `isomorphic_coordinate` controls reuse the same order/j-invariant class under scale
  transform as expected for short-Weierstrass coordinate change.
- `random_cyclic_matched_order` controls are explicitly order-matched to each family
  base curve, using a seeded search constrained to equal group order.

## Seeds and provenance

- Family streams: `seed_register.seed_streams` entries with labels
  `FAM-XXX-family` and `FAM-XXX-cyclic-control`.
- Seed register includes artifact signature to support immutable reruns.
- Manifest includes `reproducibility` block with target artifact paths.

## Next step for subproblem decomposition

`TASK-20260807-89508a` can now run with `isogeny_class_manifest.yaml` as fixed,
including `variant_id` mapping and `chain_id` references for invariance comparisons.

