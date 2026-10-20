# Formal and evidence validation slice — 2026-10-20

**Status:** scoped audit and correction. No experiment was launched, no hypothesis or finding was promoted, and no new performance measurement was made. This report is a review of committed material at `crypto-autoresearcher` main `18f0d9613a3b7ad575b190941a26b826312e4bc3` and `cryptanalysis` main `5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14`.

## Scope and inventory

The two main trees contain 2,750 and 326 tracked experiment directories respectively. The autoresearcher has 66 frozen formal target specifications: 61 refer to a present theorem file and five are undischarged because the named file is absent. File presence is **not** a successful Lean build or a semantic review. The five undischarged targets are `ncp-affine-normal-form`, `ncp-commutator-ideal-refutation`, `ncp-reachability`, `scoped-odd-torsion-translation`, and `semaev-decomposition-certificate`. The cryptanalysis main tree has 91 tracked Lean files. This inventory establishes the work queue; it does not certify all historical experiments or proofs.

## Finding 1 — the Semaev first-fall conclusion is broader than the evidence

**Measured:** The eight cells in [`ffd_semaev_results.json`](../../../research/verification/ffd_semaev_results.json) cover `n=4..7`, `n'=3,4`, and ten Semaev draws per cell. They report 70 draws with `d_ff=2` and ten with `d_ff=3`. [The chart](fall_counts.svg) shows each cell and its recorded counts. These are toy-system summaries; they omit the individual target abscissas and coefficient vectors.

**Source discrepancy:** [`FFD_SEMAEV_MEASUREMENT1.md`](../../../research/FFD_SEMAEV_MEASUREMENT1.md) says `d_ff` is pinned at two in every cell. Its [frozen formal target](../../../formal/targets/semaev-s3-degree2-fall-witness.yaml) says the trace witness proves a degree-two fall uniformly. The actual [Lean file](../../../formal/CryptoResearch/Semaev/DegreeTwoFall.lean) states its narrower boundary in its header: it proves annihilation of the quadratic part, while a nonzero surviving lower-degree residue is unproved. That missing step matters because a zero combination creates no nontrivial fall. The archived table also has degree-three outcomes; their cause is unknown from the summary.

**Validation decision:** Treat the trace identity as a proved algebraic cancellation *conditional on its formal premises*, and the toy `d_ff` distribution as measured. Withhold a universal nontrivial first-fall theorem, any solving-degree extrapolation, and any ECDLP-cost conclusion. The [problem record](../../../problems/semaev-degree-two-fall-nonzero-bridge.md) names the exact formal and replay obligations. The original frozen target and raw results remain intact.

## Finding 2 — a specific orbit-summation invariant can be formalized

**Proved and implementation-checked:** In the sibling cryptanalysis change, `OrbitQuotient.triple_matches_iff_pair_lookup` shows that a three-summand match modulo `r` is equivalent to a lookup in an enumerated two-slot residue index followed by the third representative. It is the algebraic premise of [`pair_index` and `m3_truths`](https://github.com/aburan28/cryptanalysis/blob/5ab7d5bc5a16ff4d87a5ef8bed45cf9543f47c14/experiments/orbit-quotient-summation/orbit_core.py). Lean 4.34.1 compiled the new declaration, and `#print axioms` reported only `propext` and `Quot.sound`. A separate small-modulus test compared the Python lookup with direct triple enumeration for both representative policies; four orbit tests passed.

The theorem assumes the scalar representative lists have already been enumerated. It does not certify the elliptic-curve arithmetic, orbit construction, four-summand counts, Boolean interpolation, the degree-131 projection, or a cryptanalytic speedup. [The diagram](proof_boundary.svg) makes the proven and open links explicit.

## Dashboard and graph review

The [primary benchmark snapshot](../../../ui/benchmarks/cryptanalysis-primary.json) was regenerated from the committed cryptanalysis main archive at `5ab7d5bc…`. Its source archive SHA-256 is `3886d486bf05ba476c00a67c9d7b20ed07250862273019a3b59195a22d60b973`; the exported file SHA-256 is `4cc3b31ab805b34d9f2d1103e574f8130a6902d09703d49337c467257568ae5e`. The [catalog pin](../../../ui/benchmarks/catalog.json) and [nine comparison receipt pointers](../../../ui/receipts.json) were updated together. Candidate identities and recorded online times changed from the older snapshot. The source exporter checked committed bytes, candidate and workload hashes, curve binding, and target counts. The `recorded_verified` badge still means the source receipt reports verification; it is not a new independent scalar replay.

The Compare dashboard covers **all nine rows of the primary N13 toy archive**, not the other historical archives or the whole research corpus. No canonical isogeny, curve, or performance figure was changed: this review produced no new scientific measurement and did not alter the data behind those figures. The new chart visualizes only the already committed Semaev counts. The dashboard snapshot is a refreshed reader over archived results, not a performance claim.

## Reproduction and limits

- Cryptanalysis: `python3 experiments/ic-candidate-catalog/analyze.py experiments/ic-bench/baseline/primary.jsonl` accepted all nine main-branch rows; Lean 4.34.1 compiled `OrbitPairIndex.lean`; its axiom audit showed `propext` and `Quot.sound`; four orbit unit tests passed on Python 3.12.15.
- Autoresearcher: six benchmark reader tests passed on the new main-based branch; 145 focused UI tests passed on the original complete checkout (`8b77d405e297f275a15cba425cdebb09fcc799c3`) with the refreshed snapshot. The Lean smoke project built on pinned Lean 4.22.0. The smoke project checks the verifier plumbing, not the Semaev theorem. A full `formal/` Mathlib build and independent semantic review of all 66 targets were not completed in this slice.
- The complete checkout's static UI build emitted 55,152 files (519.9 MB); its `data/comparisons.json` contained all nine refreshed rows with source commit `5ab7d5bc…` and no benchmark payload error. This validates the generated reader payload, not a live published Pages deployment. Browser DOM tests were unavailable on this host because Node/npm were absent.
- This report's visual source is [`render.py`](render.py). `report.typ` embeds both SVGs in the [PDF](report.pdf). The counts are derived only by summing the archived eight-row JSON. There are no new trial runs, uncertainty intervals, or inferred attack advantages.
