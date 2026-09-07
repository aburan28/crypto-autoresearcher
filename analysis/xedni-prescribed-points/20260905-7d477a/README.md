# Prescribed-point constructions and XEDNI: research proposals

Date: 2026-09-05. Portfolio: IDEA-20260905-7d477a.

Status: advisory proposals and draft experiment designs. No experiment was implemented or run; no hypothesis or goal changed status. This package is local and unarchived. The individual direction and study names are local labels, not allocated ledger records. Machine-readable details are in [portfolio.yaml](portfolio.yaml).

There is useful modern material to investigate, but this search did not locate a result combining arbitrary prescribed finite-field point data, a compatible rational curve, effective rational lifts, controlled heights, and a useful certified dependence. This is a bounded literature-search result, not a claim that no such work exists.

The first correction is to the objective. Classical XEDNI wants the lifted points to be dependent. A high rank lower bound does not imply that. A rank upper bound below the number of prescribed points is sufficient for dependence modulo torsion; obtaining an exact relation also requires handling torsion. Directly certifying dependence is another option. The relevant design question is therefore how many prescribed points can be accommodated relative to the rank of their span, with what heights and construction cost. The abstract of the original companion analysis explicitly describes dependence as the desired event and identifies a relation-coefficient obstruction in its setting. Its full proof was not retrieved here, so this report does not extend that obstruction to arbitrary modern constructions. [Jacobson, Koblitz, Silverman, Stein and Teske, 2000](https://link.springer.com/article/10.1023/A:1008312401197).

The input fixes residue data. It does not uniquely fix rational representatives of those residues, an entire polynomial section, or a rational curve model. This freedom matters. Conversely, an algorithm that is handed rational lifts or a suitable rational point on an auxiliary variety may already have been handed the difficult part.

## What the retrieved literature provides

| Source | Relevant ingredient | Boundary |
|---|---|---|
| [Elkies, submitted 26 August 2026](https://arxiv.org/html/2608.25406v1) | Explicit rank-17 K3 fibration, sections and height matrix; quadratic and biquadratic base changes giving ranks at least 18 and 19 in the stated settings. | These make a concrete construction family inspectable. They do not assert arbitrary prescribed-point interpolation. Much of the underlying construction was announced in 2006–2007; the new paper provides equations and proofs. |
| [Elkies and Klagsbrun, 2020](https://arxiv.org/pdf/2003.00077) | Improved searches in elliptic fibrations, with descent and rational-point searches used to certify ranks. | Efficiently screening specializations is distinct from fitting externally prescribed points. Several families impose rational torsion, which constrains their possible reductions. |
| [Will Sawin, MathOverflow, 19 December 2025](https://mathoverflow.net/questions/506133/families-of-elliptic-curves-passing-through-three-prescribed-x-coordinates) | Eliminating two coefficients for three prescribed rational x-coordinates gives a quadric; a known rational point permits parametrization. | This is an informal mathematical answer, not a high-rank theorem. Its input already has a rational seed. The displayed formula has apparent transcription errors and must be re-derived. Prescribed x-coordinates are weaker than prescribed pairs or finite-field data with specified y-residues. |
| [Loughran and Salgado, 2022](https://www.numdam.org/item/10.5802/aif.3457.pdf) | Under stated geometric hypotheses, rank-jumping fibres form a non-thin set; conic bundles and changing bisections are central. | Non-thinness is neither a uniform point-fitting algorithm nor a height bound in every prescribed residue class. |
| [Melistas, published online 13 January 2025](https://doi.org/10.1017/S0004972724001175) | Rank upper bounds for infinitely many specializations under rational 2-torsion and discriminant hypotheses, using descent and almost-prime values. | These assumptions need to survive an incidence constraint. A bound can be too large to force dependence. Rational 2-torsion excludes odd-order good reductions at odd primes. |

All five sources above were opened in this session. The two modern journal articles were read at the relevant theorem/method level; the 2026 preprint and 2020 search paper were inspected for their explicit constructions. The 2000 analysis was available at publisher-abstract level only. Source-specific provenance is recorded in the YAML. A focused search across these leads is not an exhaustive citation-graph review.

## Six directions

### A. Measure the image of the published marked family

**Question.** Which curve-and-point configurations can the explicit 2026 family actually reach?

Treat a family with named sections as a map from its parameter space to a curve together with marked points. Study three nested conditions: the reduction has the desired curve isomorphism class; the selected sections have the desired point reductions; those sections have the desired dependence or independence properties. Keep the maps explicit so coordinate changes cannot masquerade as new freedom.

**Minimal test.** On small synthetic finite fields, enumerate the good parameter values of the published family. Compare the image of its first one, two and three labelled sections against externally sampled point tuples. Separately test tuples generated from the same family as positive fixtures. Count exact pointed isomorphisms, not merely equal j-invariants.

**Prediction to test.** There is a measurable extra loss from matching points after matching the curve. A multi-parameter deformation might reduce that loss, but no rate is assumed.

**Falsification.** A claim of universal coverage fails on any verified missing configuration. A claim that a modification improves coverage fails if its entire image is unchanged after quotienting coordinate and parameter changes. Failure here concerns the selected sections and family; their image need not equal the image of every rational point on every fibre.

**Cost and value.** Count all tested parameters, mapping work, image storage and duplicate outputs. This is the cheapest way to test whether modern high-rank machinery has the kind of flexibility the user needs.

### B. Audit the difference between fixed sections and fixed fibre values

**Question.** Does fixing only the required evaluation leave useful deformation directions that were removed by older experiment models?

The existing draft H-XEDN-beb408 fixes complete x-polynomials. The proposed alternative fixes a fibre and the values of both coordinates there, while leaving higher coefficients adjustable. First reproduce the old fixed-polynomial boundary exactly. Then analyze the incidence system with evaluation constraints, removing coordinate gauges and separating components by singularity and section coincidences.

**Minimal test.** For the existing small-degree rational-surface shape, compare the dimension and differential rank of the two incidence maps at reproducible points. Search for non-gauge directions that change the marked configuration while preserving the section identities. Attempt exact deformations only after a direction survives the differential check.

**Prediction to test.** At least one smooth component has more usable evaluation freedom than its fixed-polynomial slice. This is not a prediction of generic surjectivity or useful dependence.

**Falsification.** The apparent freedom consists entirely of reparametrizations, singular components, duplicated sections, or tangent directions that do not integrate. A second failure mode is that dependence forces an additional condition on the target tuple, consuming the apparent gain.

**Why this is a distinct proposal.** The internal four-section threshold is a proposed genericity model for a stronger input constraint. It does not settle this evaluation-only question. The proposed work audits that difference without declaring the previous model false in its stated scope.

### C. Follow the prescribed-abscissa geometry before asking for rank

**Question.** How far does the three-abscissa quadric construction extend when one adds rationality, specified residues and further points?

Use the elementary elimination behind the December 2025 discussion as a boundary fixture. Compare three, four and five fixed rational x-coordinates with free y-coordinates, then impose specified y-residues. Classify the resulting auxiliary varieties before choosing an arithmetic search method. Do not assume that each stage is rational or that a local point gives a rational point.

**Minimal test.** Separate a seeded arm, where the starting rational point is supplied, from an unseeded arm, where only the small finite-field data are supplied. Charge rational-seed discovery to the unseeded arm. Record local obstruction, unresolved rational solvability, and verified rational solution as different outcomes.

**Prediction to test.** The seeded three-abscissa construction provides a cheap control, while some constrained slices retain a parametrizable component. The useful novelty would be a way to find that component and its rational seed under prescribed residues at controlled height.

**Falsification.** All apparent successes depend on a supplied seed, omit the y-residue condition, return singular curves, or achieve small residues only with uncontrolled rational height. Failure at four or five coordinates does not close other models or congruence-only formulations.

### D. Make multisections compatible with a prescribed fibre

**Question.** Can the conic-bundle or multisection method create an additional section that satisfies a chosen point condition?

A rational multisection becomes a section after base change. Modern rank-jump work provides geometric tools for varying such multisections. The new ingredient to seek is control of their intersection with the selected fibre together with an effective rational point on the new base. Each applicable theorem must be checked after the constraints are imposed.

**Minimal test.** Begin with an explicit conic-bundle example from the rank-jump literature and impose one synthetic point condition. Compare a moving multisection with a fixed base change and with a pure reparametrization. Count rational points on the auxiliary base, their heights, and newly attained point reductions.

**Falsification.** The prescribed condition forces a reducible multisection, destroys the needed rational point, changes the residue field, or only repeats the old sections. Also distinguish new sections from new base-curve coverage: for a fixed change t=f(u), its old fibres are selected from the original family. It cannot enlarge the original set of j-values just by reparametrization.

**Limitation.** A rank increase is a geometric ingredient, not evidence of dependence among the points XEDNI needs.

### E. Combine incidence constraints with certified rank upper bounds

**Question.** Can a family retain prescribed points while allowing a small, rigorous rank upper bound?

This borrows a useful part of modern rank searches: descent and rank certification. Investigate whether a point-incidence slice is compatible with the hypotheses of a low-rank-specialization theorem or with tractable descent. Compare certified rank intervals with heuristic rank scores. A lower bound from explicitly independent points cannot stand in for an upper bound.

**Minimal test.** Use small rational curves with independently checked marked points. After imposing incidence, compute supported upper bounds and compare with the number of marked points, tracking torsion separately. Include a positive fixture with an explicitly known dependence and a fixture with a certified independent tuple. A rank computation that does not finish remains unresolved.

**Falsification.** The imposed points already force independence, the available upper bound never falls below their count, or the theorem's torsion/discriminant assumptions fail on the incidence slice. Rational 2-torsion and an odd-order good reduction are a required incompatibility control at odd primes.

**Limitation.** This measures a necessary mathematical interface. It does not implement discrete-log extraction or assert an attack speedup.

### F. Optimize bounded-height reduction coverage

**Question.** Does extra certified rank actually buy more distinct low-height point reductions per unit of construction and verification cost?

For a fixed rational curve and a declared finite catalogue of rational points of bounded height, measure the number of distinct reductions. Many independent rational points can still collide modulo a prime. A large rank with a costly basis or poor coverage can lose to a lower-rank family.

**Minimal test.** Compare matched families and fixed catalogues with their ranks, logarithmic coefficient heights, point heights, height-pairing determinants, and reduction-image sizes all reported. If only a catalogue is enumerated, call the resulting count catalogue coverage; do not claim it enumerates every rational point below the height bound.

**Exact control.** For a catalogue whose reduction image is I inside a finite group G, a uniform independent target lands in I with probability exactly |I|/|G|. Independently drawn k-tuples land in I^k with probability (|I|/|G|)^k. This identity is a sampling control, not a model for dependent, adaptively selected, or without-replacement tuples.

**Falsification.** A proposed benefit disappears after matching height and cost, or after deduplicating reductions and accounting for catalogue construction. A fixed-curve lattice-counting asymptotic supplies no automatic uniform estimate when the curve, regulator and prime vary together.

## Three initial study designs

The sequence is recommended for information gained per unit of work. These studies are drafts, with approval null. Their implementation, source fixtures, software versions and artifact hashes must be frozen through a Coordinator handoff before execution. Budgets below are proposed ceilings, not measured runtimes.

| Study | Main question | Initial boundary | Proposed ceiling |
|---|---|---|---|
| Reachability | Can the explicit rank-17 family's labelled sections match externally selected small point data? | p in {101,211,431}; 16 synthetic curve models per prime; k in {1,2,3}; 64 point tuples per model and k, plus separate planted fixtures. | 2 CPU hours, 4 GiB, one worker. |
| Evaluation freedom | Does relaxing fixed polynomials to fixed values produce non-gauge, integrable directions? | Existing degree bounds deg a≤4, deg b≤6, deg x≤2, deg y≤3; k in {1,2,3,4,5}; p in {7,13,19}; symbolic checks over Q where valid. | 2 CPU hours, 4 GiB, one worker. |
| Rationality and height | Does a seeded abscissa parametrization survive genuinely external residue data? | Three fixed x-coordinates; p in {11,19,31}; paired seeded and unseeded inputs; naive coordinate-height ceilings 16,64,256. | 4 CPU hours, 4 GiB, one worker. |

The YAML specifies input distributions, controls, primary metrics, stopping rules, artifact requirements and distinct positive, negative and inconclusive branches. No fit to an asymptotic exponent is authorized from these tiny fields. Failure to complete symbolic elimination or rational-point search is an operational or bounded-search outcome, not a mathematical nonexistence result.

Directions D and E require a separate theorem-applicability pass before their own computational protocol is frozen. Direction F supplies metrics for every study. A publication-worthy intermediate result could be an explicit marked family with a proved local image description and a height bound, even if it supplies no cryptanalytic improvement.

## Prior-work and novelty boundary

Source-level lookup found the following direct overlap:

- H-XEDN-beb408 and EXP-XEDN-5202c1 concern prescribed full x-polynomials. They remain proposed and review-required respectively; only the experiment specification was found.
- H-XEDN-2945b2 and H-XEDN-40037f already propose distinctions between generic section relations and finite-fibre relations, including specialization-image measurements. A new proposal should extend their measurement boundary rather than rename it.
- IDEA-20260807-fd2d89 and draft EXP-GGMB-b902c5 discuss CM restrictions and heights. Their sweeping height dichotomy is not used as evidence here.
- DEC-20260724-021 explicitly limits its uniform slot census and states that it did not measure the distribution from fitting a surface to prescribed points. That boundary is preserved.

The knowledge-search command failed because the configured embedded in-memory index contained no collection. Read-only file search was used as a fallback. The lookup was bounded, including a separate source-lookup agent; this was not an independent mathematical validation or a claim-changing review. Historical experiments were not rerun and archive receipts were not revalidated.

Every extension here has novelty status unverified. The mathematical ingredients have identified sources; the proposed compositions and measurements have not undergone exhaustive novelty checking. No lane is closed. No asymptotic improvement is claimed. Across time, memory and data/query costs, the portfolio's SOTA delta is zero demonstrated improvement; its proposed contribution is a better specified, falsifiable construction problem.
