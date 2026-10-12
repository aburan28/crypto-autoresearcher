# Cross-repository volcano / index-calculus experiment runbook

Status: **integration runbook, not a new verified benchmark**. Execute on pinned commits and record SHA for all three repositories.

## Repositories and existing experiments

- `aburan28/cryptanalysis/experiments/volcano-ic`: Sage/PolyBoRi complete IC at m=19; 457-curve census; 310/310 verified logs; tau-invariant factor-base and CryptoMiniSat comparisons.
- `aburan28/cryptanalysis/experiments/volcano-descendants-hardness`: Sage 10.9 ECC2K-130 degree-263 descendants and conductor invariants.
- `aburan28/cryptanalysis/suite/src/isogeny/volcano.rs`: volcano mapping library.
- `aburan28/crypto/RESEARCH_PDP_SPEEDUP_AND_ISOGENY.md`: Rust PDP and Macaulay probes, with source `examples/isogeny_pdp_probe.rs` and `examples/macaulay_syzygy_probe.rs`.
- `aburan28/crypto-autoresearcher/research/ecc2k130_conductor_isogenies_20261007`: independent conductor/isogeny study.

## Prerequisites

Install SageMath (the m=131 descendant sweep documents Sage 10.9), Python 3, PARI/GP, Rust/Cargo, and the dependencies declared by each repository. The m=19 IC experiment uses Sage's PolyBoRi; its normal-basis SAT comparison uses CryptoMiniSat. Confirm `sage --version`, `cargo --version`, and availability of `sage -python`. Do not assume the m=131 field polynomial is shared across studies: normalize field isomorphisms before comparing coordinate-dependent factor bases.

## Reproduce existing results

Clone each repository side by side. Run the following from the indicated directory. These are documented repository entry points; commands have **not** been rerun by this PR.

```bash
cd cryptanalysis/experiments/volcano-ic
sage run.sage census 0 1
sage run.sage ecdlp 0 1 results/tierb-ids-1.txt
sage run.sage taucmp 0 1
python3 crosscheck.py
sage crosscheck.sage
sage -python analyze.py
sage -python build_report.py
```

Check the current `run.sage` argument parser before running the ecdlp command: the README documents `<ids>` but the file-list interpretation must be verified against source. The census covers 457 curves and full IC is expensive; use shards and bounded jobs in practice.

```bash
cd cryptanalysis/experiments/volcano-descendants-hardness
sage sweep.sage
```

For the Rust probes, inspect their CLI arguments before execution:

```bash
cd crypto
cargo run --release --example isogeny_pdp_probe -- --help
cargo run --release --example macaulay_syzygy_probe -- --help
```

The `--help` flag is a discovery attempt, not a guaranteed supported interface; consult source if either binary rejects it.

## Required new integration work

1. Export a shared versioned JSONL manifest for curve pairs: `curve_id, field_model, field_modulus, q, trace, group_order, subgroup_order, conductor, conductor_factorization, volcano_prime, depth, j_invariant, isogeny_degree, isogeny_certificate, source_commit`.
2. Export per-target fixtures with identical scalar/seed, base-point order, target points, factor-base recipe and canonical field mapping. For paired comparisons transport P and Q by the verified isogeny; do not compare unrelated random targets.
3. Add adapters for `direct`, `trace_zero`, `tau_orbit`, `phase_aware`, `normal_basis_sat`, and `double_large_prime`. An adapter MUST declare `unsupported` if no correct implementation exists; never substitute a different solver silently. The tau-orbit variant is not natively available on generic descendants.
4. Each attempt writes `run_id, curve_id, variant, solver, target_id, seed, factor_base_size, orbit_count, decomposition_attempts, successes, failures, timeouts, duplicate_relations, verified_relations, independent_rank, dreg, matrix_rows, matrix_cols, setup_cpu_s, collection_cpu_s, solver_cpu_s, verification_cpu_s, linear_algebra_cpu_s, transfer_cpu_s, total_wall_s, hardware, status, error`.
5. Require exact verification of every point relation and recovered log; record the rank of the actual coefficient matrix mod subgroup order.
6. Run paired, randomized/interleaved target order with pinned CPU affinity/NUMA and environment metadata. Report bootstrap confidence intervals and an equivalence/control test. Distinguish time per independent relation from full attack time, including precomputation and transport.
7. Produce a machine-readable report comparing each variant with direct IC, and with the strategy of transferring the target to the crater and using crater IC. Record asymptotic extrapolations separately from measurements.

## Preexisting negative controls (do not erase)

The m=19 study found no detectable per-solve curve effect in its interleaved test (Friedman p=0.42), and 310/310 full logs verified. Randomizing the factor-base subspace largely removed the apparent curve differences. Trace-zero factor bases improved modeled attempts but were not run end-to-end. On the crater, the tau-orbit variant reported 444 -> 70 CPU seconds per DLP, while the normal-basis CryptoMiniSat variant reported 668 seconds. These results are not evidence that a large conductor gap intrinsically weakens ECDLP.

The m=131 descendant study constructed all 262 degree-263 descendants; the much larger conductor-changing degree 146505763881528721 remains algebraic/theoretical only. Do not describe its endpoints as instantiated.

## Acceptance gates

- Reproduce archived small-field baselines and explain any differences.
- Confirm field model, isogeny certificates, target transport, and all verified logs.
- Run direct and each supported variant on matched pairs with all misses and timeouts.
- Publish raw JSONL, hashes, environment, confidence intervals and scripts.
- Claim >=2x improvement only on total verified independent-relation cost, and separately evaluate full ECDLP cost.
- Do not claim a fundamental hardness difference when an efficient isogeny reduction transfers the advantage.
