# ECDLP-IDEA-065 — Fitting-minor export-form generator

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_merged`
- Evidence scale: `toy` symbolic-module derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: semantic merge with rejected ideas `013/052` and the occupied determinantal source-decoder lane
- Breakthrough claim: **none**; a rank-drop minor or missing-column row is not an ECDLP break.

## Falsifiable hypothesis

The universal module of source-form coefficients for the ledger's relation family has a
low-codimension Fitting stratum whose explicit minor is nonzero exactly when an exported
source row contains a required missing-column direction. Cofactor data parametrizes every
source witness before certificate materialization, produces rank-productive rows with
sub-square-root total cost, and supports factor-log calibration and blind target descent.

## Mechanism-new operation

The proposed operation was a **source-labelled Fitting-minor biconditional**. A universal
presentation matrix is formed over public source parameters; a specified determinantal
minor detects the desired coefficient support, while its adjugate/syzygy cofactors recover
the actual source form. This would alter generation before rows exist.

Generic minor computation, signature measurement, sorting existing certificates, a rank
certificate without atoms, or a solver substitution is a duplicate/control.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N` and challenge `Q=[x]P`.
2. The universal source-form presentation is complete on all addition charts and target independent.
3. One bounded-size minor is necessary and sufficient for the requested exported-column support.
4. Cofactors lift each accepted minor to exact source parameters and curve points.
5. Stratum density, presentation construction, minor evaluation, output, rank, calibration, descent, verification, and memory are charged.
6. No post-hoc row selection, scalar-labelled parameters, or precomputed certificate corpus is used.
7. All claims are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`universal_source_form_module | explicit_Fitting_stratum | missing_column_minor_iff | adjugate_syzygy_source_parameterization | pre_certificate_generation | rank_and_target_descent`

No curve-specific biconditional or source parametrization was supplied. Fitting ideals
therefore remain a generic existence detector already covered by ideas `013/052`; this
record is a merge, not an independently deferred mechanism.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-18`, the explicit column-targeted source-form generator question.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H667`, the closest structural-minor/rank diagnostic.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H665`, the closest confluent determinant/power-sum relation surface.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H629`, the closest pre-certificate source-generation lane.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H638`, the closest source-signature/support decoder control.

## Closest primary literature

- Fitting, [Die Determinantenideale eines Moduls](https://eudml.org/doc/146122), introduces determinantal ideals but no elliptic source decoder.
- Eagon and Northcott, [Ideals defined by matrices and a certain complex associated with them](https://doi.org/10.1098/rspa.1962.0170), supplies determinantal complexes and grade conditions.
- Buchsbaum and Eisenbud, [What makes a complex exact?](https://doi.org/10.1016/0021-8693(73)90044-6), supplies exactness criteria, not a below-rho witness generator.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the nearby relation equations.

No checked source proves the required elliptic biconditional or source lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source parameter space, export convention, and missing coefficient directions.
2. Derive a complete universal presentation matrix over the public parameters.
3. Identify a bounded minor and prove its vanishing/nonvanishing biconditional for desired source rows.
4. Use cofactors to recover sources and independently verify every exported relation.
5. Collect enough fresh directions to calibrate all factor-base logs and verify them.
6. Apply the same presentation and minor to randomized `Q+[t]P` sources.
7. Complete target descent from recovered sources and calibrated logs.
8. Remove `t` and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let presentation dimension be `N^d`, minor-evaluation
exponent `kappa`, source-stratum reciprocal density `N^delta`, independent-rank loss
`N^r`, factor-base size `N^beta`, target density `N^delta_t`, and memory `N^mu`.
If one accepted specialization emits one row, at least `B=N^beta` accepted rows are
required for calibration. The complete exponent is
`lambda=max(d,beta+kappa+delta+r,2beta,kappa+delta_t,mu)`, including coefficient output,
cofactor recovery, failed parameters, and verification. A small minor with an
`N^(1/2)` residual source fiber does not beat rho.

## Likely fatal obstruction

Fitting ideals describe support/rank loci but usually do not identify points in a fiber.
The useful minor can have dimension or degree proportional to the factor base, while its
cofactor fiber contains all candidate sources. Forcing one missing column may reduce hit
density or duplicate existing dependent rows, leaving calibration and descent unchanged.

## Proof track

Prove completeness of the presentation, the minor biconditional, bounded source fiber,
and nonzero independent-rank contribution; then bound all relation and descent costs below rho.

## Disproof track

Find a false minor/source implication, prove all bounded minors are identically zero or
source-ambiguous, show fresh-rank gain vanishes, or establish complete `lambda>=1/2`.

## Positive and negative controls

- Positive algebra control: a planted presentation with known determinantal support and cofactors.
- Positive source control: exhaustive tiny-curve source forms containing the requested columns.
- Negative rank control: correct but dependent exported rows.
- Mechanism control: post-hoc search over the existing certificate corpus.
- Leakage control: no target-selected minor, scalar parameter, or discarded failed specialization.

## Quantitative promotion and falsification gates

No promotion gate remains because the missing minor/source biconditional is the same
missing operation as rejected ideas `013/052`. The historical preflight required zero source errors,
at least `0.8` fresh rank per accepted row, 1,000 verified relations, 100 blind descents,
and upper 95% `lambda,mu<=0.45`. Falsify on any biconditional error, lower 95% source
fiber or presentation exponent at least `1/2` in `N`, or complete `lambda>=0.50`.

## Artifact plan

- Missing identity: `ideas/artifacts/ECDLP-IDEA-065/fitting_source_biconditional.md`
- Presentation: `ideas/artifacts/ECDLP-IDEA-065/universal_presentation.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-065/verify_sources.sage`
- Future runs: `ideas/artifacts/ECDLP-IDEA-065/runs/<run-id>/`
- Retain matrices, minors, cofactors, parameters, sources, relations, ranks, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected hypothesis is toy, heuristic, model-bound, and novelty-unverified. A rank
defect or valid row is not source recovery, target descent, or a breakthrough.

## Exactly one next executable action

1. Preserve `ideas/artifacts/ECDLP-IDEA-065/fitting_source_biconditional.md` as the exact merge boundary; do not create a contract unless a future curve-specific theorem supplies the missing biconditional and source parametrization.
