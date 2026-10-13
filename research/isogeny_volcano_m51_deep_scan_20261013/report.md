---
title: "m=51 deep conductor endpoint discovery"
subtitle: "Descriptive report for sealed run m51-deep-scan-run-d2dd22d7"
date: "2026-10-13"
geometry: margin=0.72in
fontsize: 10pt
---

This is a descriptive discovery report. It records observations only; it does
not approve, promote, support, weaken, or reject an ECDLP or weak-curve claim.

# Scope

The run exhausted the frozen global rank interval `[0, 3,600,000,000)` in 256
shards. It searched the ordinary Koblitz isogeny class over `GF(2^51)` with
modulus `x^51+x^6+x^3+x+1` and models
`E_b: y^2+xy=x^3+b`. The shared curve order was
`N=2,251,799,852,369,764`, with `D_K=-7` and
`f_pi=32,756,041=271*120871`.

# Recorded observations

| Quantity | Recorded value |
| --- | ---: |
| Planned/scanned shards | 256 / 256 |
| Sieve hits | 42 |
| Certified source-parent pairs | 42 / 42 |
| Frozen selected pairs | 32 |
| Selection cutoff | 2,531,725,702 |
| Admitted failures | 0 |
| Blocking failures | 0 |
| Passed frozen controls | 21 / 21 |

Every certificate records a source/bottom conductor
`f_E=32,756,041`, a target/parent conductor `f_E=120,871`, orbit sizes 51,
and a separable degree-271 ascending edge over `GF(2^51)`. The first 32
eligible distinct parent orbits were selected in global-rank order; all ten
later certified hits remain preserved.

![Cumulative certified hits over the complete 3.6-billion-rank scan. The plot contains all n=42 recorded hit ranks; the dashed guides show the frozen quota and 32nd selected rank. Source: `results/hits.csv`; run `m51-deep-scan-run-d2dd22d7`.](discovery-yield.png)

# Conductor-lattice context

The blue edge below is one exact selected bottom-parent example; the same
certificate shape holds for all 42 classified hits. The green edge is a frozen
positive control. Dashed degree-120871 lines are only conductor-lattice
adjacencies: this run supplied neither those endpoint maps nor their field of
definition. No horizontal edge was searched or measured.

![Certified and unresolved relationships in the four-level conductor lattice. Every vertex gives `(D_K,f_pi,f_E)` and a full representative model. Solid edges name their certification scope; dashed edges are not supplied maps.](conductor-lattice.png)

# Artifact and audit summary

The complete deterministic archive is `run1.tar.zst` (2,445,167 bytes), with
its SHA-256 and root-manifest SHA-256 bound in `ARCHIVE.md`. All 1,665 listed
files passed manifest verification in both the live sealed
tree and an extracted archive, and the two trees compared byte-for-byte equal.
See `ARCHIVE.md`, `AUDIT.md`, and `ATTEMPTS.md` for the reproducible checks and
failure accounting.

# Explicit boundary

All 42 certificates record `map_evaluator_serialized=0`, `dual_serialized=0`,
and `transfer_claim_permitted=0`. This result therefore supplies certified
endpoint-native conductor and edge facts only. It does not supply an
executable evaluator or dual, subgroup preservation or scalar recovery,
comparative ECDLP measurements, a conductor-caused hardness effect, a weak
representative, source-transfer weakness, or weakness of a named curve.
