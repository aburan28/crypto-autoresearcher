# ECDLP-IDEA-144 — Berkovich reduced-divisor source lift

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `-`
- State: `merged_rejected_skeleton_residue_source_collapse`
- Cohort: `20260717-h`
- Evidence scale: semantic/literature audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: prospective tests are `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a reduced graph divisor, valid specialization, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Lift the public curve and factor base to a semistable nonarchimedean model, specialize each relation divisor to the Berkovich skeleton, compute the unique target-reduced chip-firing representative, and canonically lift its chips to exact factor-base points. If skeleton size and residue ambiguity stay sub-rho, the representation supplies relations and blind descent.

## Mechanism-new operation

The proposed operation is **unique reduced graph divisor plus canonical chip-to-source lift**. Tropical reduction would compress divisor equivalence to a graph algorithm, while a residue-section theorem would retain exact point provenance.

Semantic audit merges/rejects the present proposal. Skeleton specialization preserves aggregate divisor class while collapsing all points in a residue disc. The unique reduced graph divisor therefore does not specify which factor-base point produced a chip. A canonical source lift requires the full residue/source dictionary or a new source-faithful atlas, exactly IDEA-016, IDEA-017, IDEA-029, IDEA-032, IDEA-076, and IDEA-103.

## Assumptions

1. Public `E/F_p`, `<P>`, `N`, target `Q`, and signed factor base `F` of size `B=N^beta` admit one uniform, efficiently constructed semistable lift.
2. The skeleton has sub-rho size and specialization is compatible with every relation and masked target.
3. Reduced divisors retain multiplicity, sign, infinity, and exact source labels through a canonical public residue section.
4. Lift/model/skeleton construction, chip firing, residue search, output, rank, factor logs, descent, and memory are charged.
5. Same-field isogeny/model changes and fixed bounded component groups are controls.

## Semantic fingerprint

`semistable_nonarchimedean_lift | Berkovich_skeleton_specialization | unique_target_reduced_divisor | canonical_chip_to_factor_point_section | exact_relation_and_blind_descent`

Only a source-faithful residue section would be new. Aggregate skeleton/divisor reduction is the rejected duplicate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the missing public source-fiber generator that a chip-to-point section cannot assume.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1474`, where a natural structured CM orbit fails to preserve an invariant sparse deck.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the complete source-query exponent boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-P047`, where formal elliptic completion is a functional representation control rather than a non-generic advantage.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-043`, whose completion-point signal is reproduced by matched random/hypergraph controls.

## Closest primary literature

- Baker and Norine, [Riemann–Roch and Abel–Jacobi theory on a finite graph](https://doi.org/10.1016/j.aim.2007.04.012), establish reduced-divisor/chip-firing structure on graphs, not point-source lifting.
- Baker, [Specialization of linear systems from curves to graphs](https://doi.org/10.2140/ant.2008.2.613), proves specialization results that can lose residue-disc information.
- Mikhalkin and Zharkov, [Tropical curves, their Jacobians and theta functions](https://doi.org/10.1090/conm/465/09104), describe tropical Jacobians and theta data, again at aggregate divisor-class level.

No checked source supplies the required finite-field source section. Novelty remains unverified, while the stated skeleton transform is occupied.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, semistable lift/model, skeleton, specialization/retraction, reduced-divisor basepoint, residue sections, and verifier.
2. Lift and specialize factor points and known-log targets, recording every model/skeleton/source-dictionary cost.
3. Compute target-reduced divisors, lift every chip to exact signed factor points, and verify elliptic relations.
4. Collect rank `B`, solve and verify factor logs.
5. Repeat unchanged on fresh masked targets, enumerate residue ambiguity, and accept only `[x]P=Q`.
6. Charge lift, skeleton, chip firing, residue enumeration, output, rank, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let lift/skeleton setup be `N^a,N^a_m`, skeleton/dictionary payload `N^c`, reduced-divisor/residue-inverse time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, source output `o`, residue ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Residue dictionaries and all chip lifts are charged. Toy graph sizes are model-bound.

## Likely fatal obstruction

Retraction to a skeleton is many-to-one on rational points. Divisor class and chip-firing reduction preserve sums but not arbitrary point ancestry. Making the lift unique requires a residue-level choice that is the original source selector; making the skeleton fine enough to separate all factor points can restore `B` labels and high-degree/height/model cost without improving relation density.

## Proof track

Prove a uniform semistable model and source-faithful specialization/section, including all residue discs and exceptional fibers, with complete `lambda,mu<=0.45`.

## Disproof track

Exhibit distinct source tuples with the same reduced skeleton divisor, prove any section consumes a source dictionary, or show model/ambiguity cost reaches rho. The present proposal is rejected by this collapse.

## Positive and negative controls

- **Positive control:** metric graphs with known unique reduced divisors and supplied chip labels.
- **Positive control:** tiny semistable curves with exhaustive residue-disc point lists.
- **Negative control:** distinct factor points in one residue disc, shuffled residue labels, and matched random divisors with the same skeleton image.
- **Negative control:** component-group CRT, faithful-tropical-atlas, and explicit source-dictionary baselines.
- **End-to-end control:** rho/BSGS and blind targets with lift/dictionary costs charged.

## Quantitative promotion and falsification gates

This record is merged/rejected absent a source-faithful specialization theorem. A new ID requires exact source injectivity/section and `lambda,mu<=0.45`. One source collision, residue dictionary, uncharged model height, or complete exponent at least `0.5` falsifies the operation.

## Artifact plan

- Skeleton-collapse reduction: `ideas/artifacts/ECDLP-IDEA-144/skeleton_source_collapse.md`
- Prospective source-section theorem: `ideas/artifacts/ECDLP-IDEA-144/source_faithful_specialization.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-144/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-144/cost_analysis.md`

No artifact exists.

## Interpretation boundary

This is rejected, novelty-unverified evidence. Tests would be toy and costs heuristic/model-bound. A graph divisor identity is not exact point recovery, a below-rho algorithm, or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-144/skeleton_source_collapse.md` with the smallest pair of distinct factor-source divisors sharing a skeleton image and the residue information required to separate them.
