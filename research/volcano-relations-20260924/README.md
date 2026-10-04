# Isogeny volcanoes, factor bases and relation-system complexity

Experiment design bundle, 24 September 2026. Repository: **aburan28/crypto-autoresearcher**, not `aburan28/crypto`.

**Question:** Can a certified, efficiently reachable isogenous model, combined with an explicitly specified factor base and polynomial formulation, reduce the cost of useful relations or a precisely defined solving-degree quantity?

This is a concrete design and integration plan, **not a result, dispatched campaign, or new attack implementation**. It contains ten experiment designs, fixed initial parameter panels, dependencies, controls, metrics, falsifiers and implementation deliverables. `campaign.json` is the machine-readable companion. All measurements remain unperformed. A local contract check is not a mathematical certificate.

## 1. How this fits existing work

Read these records rather than allocating duplicate experiments:

| Existing record | Integration boundary |
|---|---|
| `experiments/EXP-DREG-dd668d/specification.yaml` | Existing F_4 chained t=4 edge and meter protocol. Reuse valid builders/certificates, not its labels as interchangeable degree definitions. Its characteristic-2 degree-2 edge is **not** the ell != characteristic ordinary-volcano experiment below. |
| `EXP-DREG-ab3fee`, `EXP-DREG-6de989`, `EXP-DREG-c3e8c9` | Related extension-rung, attribution and graph-encoding contracts described in PR #1369. Inspect their actual artifacts before reuse; approval is not execution evidence. |
| `EXP-DREG-d76c97` | Related rebuilt-versus-pullback contract in PR #1372. It does not replace a multi-target equal-point-support experiment. |
| `RQ-DREG-d7b6d6`, `RQ-DREG-c8ae8d` | Existing research questions for degree growth and within-class variation. |
| `ledger/DEC-20260716-003.yaml` | Scoped-negative earlier neighbor screen: one toy base, ell in {2,3,5}. Preserve the decision; do not extrapolate it to all fields/levels or relaunch its m=3 screen under a new name. |

Repository records were retrieved through the connected GitHub API in this authoring session. No claim is made to have audited their run artifacts or independently replicated their conclusions.

**Registration:** local keys such as `transport` and `native` are design slots, not canonical EXP/H/IDEA IDs. Before scientific dispatch, the Coordinator maps each slot to an exact existing contract or creates an additive successor using `tools/allocate_id.py --next ...` and `--check`. No archived contract, hypothesis status, approval or run record is changed by this bundle. Standing user authorization already covers the work; missing adapter/fixture readiness is technical work, not a request for another user approval.

## 2. Mathematical and measurement contract

### Transport is a conservation control

On a selected prime-order subgroup G of order r with gcd(deg(phi),r)=1, phi is injective. For an actual point base B contained in G and target R in G,

    sum(P_i) = R  <=>  sum(phi(P_i)) = phi(R).

Thus the ordered decomposition counts over B and phi(B) must agree target by target, with the same repeated-point convention. A mismatch is an encoding/map/oracle bug, not a better relation yield. A faster solve for the same decompositions is a meaningful representation gain.

Also, summing the number of ordered m-decompositions over every R in G gives exactly |B|^m. Changing an equal-cardinality base can redistribute decompositions and change the nonempty-target probability, but not this mean. Freeze the distribution of targets independently of solutions. Constructed-solvable fixtures are useful only in a separately labelled correctness panel.

Native bases and transported bases are different experiments. Equal x-space dimension, equal x-support size and equal actual point cardinality are not synonymous. Never silently trim an orbit or subspace support to force a match; record missing exact-cardinality cells.

### A graph distance is not a volcano level

Use ordinary curves, separable ell-isogenies with ell different from the characteristic, explicit maps and dual/composition certificates. Record the conductor of Z[pi] separately from that of End(E). Store an unknown level as null. Verify a vertical edge through endomorphism-ring evidence; graph distance or a square factor of the Frobenius discriminant alone is not certification.

A rational isogeny can have a Galois-stable kernel without individually rational kernel points. Do not filter the graph by requiring ell to divide #E(F_q). A bounded search is a neighborhood inventory, not an exhaustive class census. Distinguish F_q-isomorphism classes, not just j-invariants, and retain field/embedding certificates.

For toy map checking, exhaustive point tests are valuable, but tests on E(F_q) alone are not a proof of equality of rational maps: retain symbolic curve/homomorphism and dual-composition certificates where claimed. Record every omitted or unclassified vertex.

### Degree labels must remain separate

Record these fields separately:

| Field | Admissible interpretation |
|---|---|
| `input_max_degree` | Degree of the actual supplied generators in the recorded ring. |
| `final_basis_max_degree` | Maximum degree in a completed final basis, not the cost of computing it. |
| `max_processed_degree` | Maximum processed polynomial/Macaulay degree in a named backend trace, with sugar/signature degrees separately labelled. |
| `certified_solving_degree` | A value for a precisely stated solving-degree definition, algorithm and monomial order, with its required certificate; otherwise null. |
| `first_observed_fall`, `last_observed_fall_through_D` | Observations within a stated finite truncation. |
| `certified_last_fall_degree` | Requires a valid completion/stabilization argument, not the last fall noticed before a cutoff. |
| `dreg_top_homogeneous` | Optional metric for a stated homogeneous/top-degree ideal under an applicable definition; not an alias for affine solving degree. |

**Legacy metric quarantine:** the existing F_4 contract's `grevlex` paragraph describes a final-basis-degree quantity with an S-pair condition. Do not silently import that value into `certified_solving_degree`. Preserve its original name/definition and add an explicit semantic mapping only when the underlying trace and certificate justify it. This bundle does not amend that immutable record.

Use full-column Macaulay matrices. Boolean rings require the declared squarefree quotient and field equations. Invertible linear changes preserve the underlying mathematical problem but do not justify assuming every generator-truncated affine rank profile or backend schedule is invariant. Test the exact claimed invariant. Never assume that low first fall degree bounds later processing.

## 3. Experiment matrix

All experiments inherit the shared protocol, cost accounting and invalidation rules in `campaign.json`.

| Order / local key | Experiment and decisive comparison | Primary output |
|---|---|---|
| 1 / `topology` | Certify vertical/horizontal edges, level, field of definition, torsion and map complexity before looking at solving costs. | Reproducible fixtures and certificates, including unavailable edges. |
| 1 / `meter` | Independent tiny-system references, identity replay, known easy/harder systems and low-first-fall examples on F4/F5. | Trustworthy separated degree telemetry and demonstrated dynamic range. |
| 2 / `transport` | Domain B versus phi(B), rebuilt membership versus graph encoding, with exact count and solution-set conservation. | Same-problem representation cost and correctness. |
| 3 / `coordinates` | Eight valid same-curve coordinate/basis changes versus the neighbor and support-matched random controls. | Attribution to coordinates, backend behavior or a surviving neighbor effect. |
| 4 / `native` | Native structured versus transported versus uniform point bases of the same actual size; vertical and horizontal comparisons separated. | Relation distribution, membership cost and depth-versus-feature diagnostics. |
| 5 / `symmetry` | Raw chained S3 versus permutation/torsion-adapted formulations and symmetry-aware linear algebra. | Net cost after quotient reconstruction, stabilizers and dependent rows. |
| 5 / `frobenius` | Orbit-aware subfield root versus a neighbor with a certified action and a neighbor without reuse. | Solver gains minus lost/expensive Frobenius benefits. |
| 5 / `function_first` | Strongest verified Semaev versus function-first, fixed-span quotient and transported function-support formulations. | Support constraint complexity and full useful-relation cost. |
| Separate / `cover` | Small composite-field descent/cover constructions on source and neighboring curves with verified hypotheses. | Explicit correspondence, genus, construction cost and measured feasibility. |
| 6 / `holdout` | Frozen candidate rule versus strongest baseline and best coordinate-only control on unseen trace classes. | Replicated costs, mechanism witnesses, complete toy-pipeline accounting and limits. |

Each machine-readable entry names the hypothesis, arms, parameters, controls, metrics, success test, falsifier, next action and implementation component. A negative or unavailable optional mechanism lane does not prevent testing valid candidates from another lane.

### Mechanism details that must not be lost

**Symmetry:** prove the action preserves the fixed-target problem, or explicitly work with paired target orbits. Simultaneously applying Frobenius usually moves R as well as the decomposition. For a fixed target only its stabilizer acts internally. Account for short orbits, repeated points and lifts. A claimed block decomposition requires its algebraic hypotheses; characteristic dividing the group order can prevent a naive semisimple decomposition.

**Function-first:** H divides L_V is a proposed support constraint only when V and the divisor semantics actually match the formulation. Arbitrary transported x-support is not automatically a vector space. Use its true vanishing polynomial when appropriate; account for signs, repeated x-coordinates, multiplicities, poles and the full Riemann--Roch condition. Compare with the same base and targets, and include quotient-span setup, failed solves and extraction. Do not call a sound-but-incomplete relaxation an equivalent solver.

**Cover lane:** the initial towers are F_(2^6)/F_(2^2) and F_(2^12)/F_(2^4), both relative degree three. Check the selected construction's full hypotheses, not merely the field degree. Lower genus without an explicit suitable map is unmeasured feasibility, and lower genus alone is not a runtime result. This separate lane supplies no intermediate-subfield assumption for prime extension degree 131.

**Mechanism witness:** an interesting degree drop triggers extraction of a specific syzygy, membership-constraint simplification or certified invariant responsible for it. Repeat on adjacent models and coordinate controls. A graph-local cost valley is exploratory until it predicts held-out performance; rank curves by a frozen rule, never choose the best holdout retrospectively.

## 4. Initial sampling and stopping protocol

| Parameter | Correctness smoke panel | Paired discovery/holdout panel |
|---|---|---|
| Odd prime fields | 101, 127, 163, 211 | 257, 509, 1021 |
| Binary fields | Degrees 4, 6, 8 over F_2 | Degrees 9, 11, 13 over F_2 |
| Isogeny primes | 2, 3, 5, 7, excluding characteristic | Same |
| Requested classes per field | 2 | 6: first 4 discovery, final 2 holdout |
| Vertices / graph distance | At most 8 / 3 | At most 12 / 3 |
| Actual factor-base sizes | 4, 8 | 4, 8 |
| Decomposition length | 4 | 4, then 5 after correctness |
| Targets per paired cell | 8 | 32 |
| Seeds / timing repetitions | 1 / 1 | 5 / 3 |
| Degree checkpoint | 4 | 8 |

These are requested coverage, not claims that matching vertical edges or bases exist. Freeze up to 128 seeded coefficient candidates and first eligible trace classes before solving; do not replace unfavorable classes after measurements. Missing cells stay visible. Preserve curve-family strata and never pool unrelated fields into a paired speed ratio. Treat B^m/r <0.25, 0.25..4 and >4 as separate density strata.

At smoke scale the independent oracle can enumerate all decompositions, or compute the all-target histogram exactly by group-law dynamic programming. Check the histogram sum |B|^m and target-wise transport conservation. Freeze the oracle/solver interface before comparing outputs.

The degree checkpoint is a truncation, not a mathematical upper/lower bound on an unfinished solve. A 600-second process watchdog and 8 GiB memory limit protect the machine; they do not cap the research campaign. Checkpoint and label censored work. Extending a frozen scientific ladder requires an additive protocol with named changes. Never relabel a timeout as large degree, no relation, or a disproved hypothesis.

## 5. What counts as a win

The **chosen experimental promotion threshold**, not a promised effect, is at least **20% lower total cost per rank-increasing verified relation** against the strongest matched available baseline. Report reduced-degree claims separately from speed, and speed separately from an asymptotic claim.

For relation usefulness, define a fixed set of columns and anchors across the campaign's relation matrix. Work over the subgroup coefficient field F_r, not automatically F_2. Do not add a fresh unknown column for every target, which would manufacture rank. Retain target/anchor coefficient records and verify every row independently. Compare the same rank checkpoint (initially floor(0.8*B) for the common B unknown columns) and also report the full scheduled-target panel; rank saturation must not create a denominator advantage. Full toy completion is a separate endpoint.

Charge candidate search, graph construction, isogeny evaluation, factor-base construction, polynomial construction, preprocessing, **all** successful and unsuccessful solves, extraction, verification, duplicate/rank filtering, final linear algebra and toy completion checks. Record CPU time, wall time, field operations when available and peak memory. Missing stage implementations prevent a full-pipeline claim.

Report cold setup and explicit reuse scenarios K=1,10,100. Do not present warm-cache costs as cold or treat a hypothetical reusable setup as measured amortization. Keep time/memory Pareto tradeoffs visible. Mark zero useful relations explicitly; do not give them zero cost.

Use paired per-class ratios, median, geometric mean and exploratory 95% class-cluster bootstrap intervals with 10,000 resamples. Preserve pairing and include all admitted classes. Discovery chooses the candidate rule; entire unseen trace classes test it. Require at least three completed size rungs and six held-out trace classes overall before a replicated-panel label. Require no increased failure rate and interval upper bound below one as additional gates. These thresholds do not establish a general theorem; do not fit an ECDLP exponent from tiny instances.

If censoring prevents a fair cost comparison, retain the censored observations and report that the gate is undecided. Never claim an aggregate win from only the convenient completed subset. A complete toy-pipeline comparison with an existing rho reference is allowed only when both timings solve the same complete synthetic task on matched hardware; relation throughput is not comparable directly with rho iterations per second.

## 6. Implementation work packages and handoff

1. **Fixture and oracle adapters.** Read existing edge builders, add conductor/field certificates, actual point bases, paired target generation, and all-target count conservation. Deliver `fixture_manifest.json`, `edge_certificates.json`, `factor_bases.json`, `targets.json`, exact oracle outputs and map tests.
2. **Meter and encoding adapters.** Add named degree traces and full-system hashes; compare identical systems through available F4/F5 backends. Deliver system serialization, full-column degree/rank traces, independent completion certificates and explicit unavailable-backend labels.
3. **Representation mechanisms.** Add native, coordinate, symmetry, Frobenius and function-first adapters only after shared correctness passes. Preserve each arm's construction and extraction costs. Cover construction remains its own method-specific adapter.
4. **Analysis and independent review.** Emit immutable per-attempt JSONL, relation rows, rank certificates, cost breakdown, environment/hardware versions and a paired summary. An independent reviewer checks the map/support invariants; a separate re-derivation checks any claimed mathematical degree. This session claims neither review occurred.

Before dispatch, the Coordinator records exact adapter commands, software versions, concrete fixture hashes, canonical experiment/successor IDs, owned output paths, archival task and technical admission gates. Use the existing `run` entry point; this bundle adds no scheduler, infrastructure deployment or autonomous execution. Normal protocol readiness and evidence review remain intact.

### What is included now

- `campaign.json`: all ten designs and the shared protocol.
- `check_plan.py`: standard-library design checker; it neither runs nor approves research.
- `test_plan.py`: 27 contract regressions for scope, dependencies, metrics, costs and evidence boundaries.
- This plan, including prior-work integration and implementation acceptance criteria.

Run local design checks from the repository root:

```sh
python3 research/volcano-relations-20260924/check_plan.py
python3 -m unittest discover -s research/volcano-relations-20260924 -p 'test_*.py' -v
```

These tests check the structure and selected guardrails of this design; they do not validate every prose statement, test an elliptic-curve solver, prove a mathematical hypothesis, or replace the repository-wide ledger/harness checks.

## 7. Literature pointers and provenance

These primary-source pages were retrieved or their search metadata inspected on 2026-09-24 by the authoring assistant. **Reading level: abstract/metadata, not a new full-text review.** They motivate the directions; method-specific implementation must check the full hypotheses and cite the exact section. No new state-of-the-art or novelty claim is asserted here.

- Galbraith, Hess and Smart, *Extending the GHS Weil Descent Attack*, EUROCRYPT 2002. Isogeny-assisted selection of a favorable descent setting: https://research-information.bris.ac.uk/en/publications/extending-the-ghs-weil-descent-attack/ (provenance: retrieved, abstract).
- Galbraith, Gilchrist and Robert, *Improved algorithms for ascending isogeny volcanoes, and applications*, 2025/1243. Navigation, not a theorem about lower relation solving degree: https://eprint.iacr.org/2025/1243 (provenance: retrieved, abstract).
- Faugere, Huot, Joux, Renault and Vitse, *Symmetrized summation polynomials: using small order torsion points to speed up elliptic curve index calculus*, EUROCRYPT 2014: https://inria.hal.science/hal-00935050 (provenance: retrieved, bibliographic metadata).
- Galbraith, Granger, Merz and Petit, *On Index Calculus Algorithms for Subfield Curves*, SAC 2020: https://eprint.iacr.org/2020/1315 (provenance: retrieved, bibliographic metadata).
- Kosters and Yeo, *Notes on summation polynomials*: https://arxiv.org/abs/1503.08001 (provenance: retrieved, abstract; warns about first-fall heuristics).
- Caminata and Gorla, *Solving degree, last fall degree, and related invariants*: https://arxiv.org/abs/2112.05579 (provenance: retrieved, abstract; precise degree framework).
- Euler and Petit, *New results on quasi-subfield polynomials*: https://arxiv.org/abs/1909.11326 (provenance: retrieved, abstract; constructions and limitations, not an established speedup).
- Tian, *Cover attacks for elliptic curves with prime order*: https://arxiv.org/abs/2012.07173 (provenance: retrieved, abstract; separate cover/correspondence direction).

**Bottom line:** search for an explained and reproducible improvement in the joint choice of curve, factor base and equation system. Measure volcano depth; do not assume it predicts ease. Preserve both useful engineering gains and scoped negative results without calling either an ECDLP breakthrough.
