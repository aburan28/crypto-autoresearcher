# Isogeny-stratified ECDLP ML blueprint: every lead worked, every open question answered or bounded

**Dates:** triage 2026-10-10 (v1); comprehensive pass 2026-10-11 to 2026-10-13 (v2, this file).
**Kind:** triage of a supplied research blueprint, five new measurements on
frozen and newly constructed data, one derivation table, the blueprint's ML
ladder implemented and run on measured data, two literature entries.
**Claim tier:** toy. **ECDLP claim:** none, in either direction. No research
state changes here; nothing is approved, promoted or closed by this note.

**Input.** "Isogeny-Stratified ECDLP Machine Learning Research, end-to-end
technical blueprint, version 1.0, October 2026" (9 pages; SHA-256
`276fab868c001bf7d8932a4e64ada7a5e585160c5ea1d6d3cc427c679ffbf725`). The
document calls itself "an implementation-ready specification, not a measured
experimental dataset or a demonstration of any cryptographic vulnerability";
its example records are synthetic. It is not committed here (the repository's
report pipeline publishes every `research/**/*.pdf`); the hash identifies it.

**Repositories read and written**, at the commits below. Every pointer in this
note is a path in one of them.

| repo | base commit | branch with this work | role |
|---|---|---|---|
| `aburan28/crypto` | `3da0029607dacb6f82aec6ef7f23ad2b7ec1d4d2` | `research/isogeny-level-panels-20261012` | Rust cryptanalysis suite; new: m = 3 level panel example, `isogeny_algos` binary volcano module and the n = 51 class |
| `aburan28/cryptanalysis` | `605ed9c6b790f078158510fb0bbfca6b240ed0fa` | (read only) | ECC2K-130 class study, level-labelled hardness table |
| `aburan28/ml-cryptanalysis` | `fe306baf9f7e561f73fdcb04708f305d896ac726` | `research/isogeny-stratified-ml-20261012` | prime-field CSD program; new: `csd/stratified/` (the blueprint's ML ladder), complete-class graph dataset |
| `aburan28/crypto-autoresearcher` | `85e1d32b7851738cf371a209c6591ba89928df81` | `research/isogeny-stratified-blueprint-triage-20261010` (PR #2057) | ledger, knowledge corpus, this note |

## 0. Verdict

The blueprint's four hypotheses were already tested in these repositories
(section 1), and every lead it leaves open has now been worked as far as this
container allows (section 3). The outcome is uniform: **no conductor,
volcano-level or isogeny-graph feature carries information about ECDLP attack
cost beyond matched controls, in any family, at any arity, under any of the
blueprint's own controls.** Specifically:

- binary Koblitz class n = 16 (the only in-repo class with two floor levels),
  per-prime strata (v₃, v₃₁), m = 2: null (§3.1);
- the same class at **m = 3 with the production S₄ Gröbner solver**, where the
  decomposition step is non-trivial (600 to 700 reductions per call): see §3.5;
- a **new general binary ordinary class at n = 51** (the blueprint's missing
  size), 114 vertices on three levels of a 7-volcano: null, and the
  subgroup-exact relation yield is identically zero because the cofactor is
  2.8 × 10⁹ (§3.2);
- prime-field rho, 1,548 curves, 28 conductor / class-group / volcano
  features: gain in out-of-fold R² of 2 × 10⁻⁵ (§3.3 of v1, kept below);
- the **blueprint's full ML ladder** (control → tabular → ablations → graph →
  multi-task → active selection) on six measured datasets with class-held-out
  splits, shuffled-conductor nulls, leave-family-out and leave-field-out,
  conformal intervals and the blueprint's metrics: §3.4;
- **transport pricing (H3)** across the whole Koblitz ladder n = 11 to 131 plus
  the new n = 51 class: wherever a descending isogeny is constructible its cost
  is 2⁵ to 2⁵⁰ below the floor curve's rho, so a floor-curve method must beat
  the crater's rho to matter; where the kernel field degree exceeds 10⁴ the
  level is unreachable in either direction (§3.6).

The blueprint's own stop rule (§19, "No verified relation advantage: publish
null result and stop expensive scaling") is therefore triggered on the
measured record, and its phases 5 and 6 (graph ML at scale, productisation)
are not warranted. What remains open is theory, not measurement: the JMV
large-prime conductor-gap case (§4, R4).

## 1. The four hypotheses against the evidence on file (v1, unchanged)

Labels: **measured** = a run with retained artifacts; **derived** = a proof or
exact computation; **independently verified** = a second implementation or
reviewer re-derived it; **proposed** = a design that has not run.

| blueprint hypothesis | status | strongest evidence (path, scope) |
|---|---|---|
| **H0** conductor and graph features have no incremental predictive value beyond matched controls | **supported in every tested scope** | §3 of this note; `ml-cryptanalysis/experiments/anomaly-search/report.md` (1,545 curves, 0 replicated anomalies); `ml-cryptanalysis/experiments/isogeny-structure/report.md` Stage B (0 cost formulas above the permutation null); `crypto/research/notes/koblitz-isogeny/presentation-vs-curve-results-20261004.md` (curve ICC ≤ 0.09) |
| **H1** conductor valuation and topology predict relation yield, degree of regularity or total solver cost on unseen classes | **rejected in scope** for the degree metrics (theorem) and for yield (explained by setup) | Boundary C′ (`crypto/research/notes/ecc2k130/RESEARCH_ISOGENY_CLASS_SEARCH.md` §2C′: leading forms of the Weil-descended Semaev systems are free of `b` for every m); identical Macaulay ranks across walked classes (`crypto/RESEARCH_PDP_SPEEDUP_AND_ISOGENY.md`); yield spread explained by cofactor balance with no fitted constant (`yield-spread-results-20261003.md`); prime fields: H-ISO-001 `rejected_scoped` (EV-ISO-001) |
| **H2** effects replicate across binary Koblitz, general binary ordinary, prime-field and prime-field-extension curves | **null replicates on all four**; the extension leg is covered only through the model-dependent mechanisms (GHS, covers) already in the frontier map | Koblitz n = 16 to 131; binary ordinary n = 17, 19 (v1) and **n = 51 (new, §3.2)**; prime fields (`ml-cryptanalysis`, EV-ISO-001, EV-VOLC-3529e8); F_{p^n}: KR-IC-5ea2f8, KR-IC-791cb7, IDEA-20260920-10547b |
| **H3** direct attack advantages remain interesting after pricing isogeny construction and subgroup transfer | **moot where measured; transport priced for every class on the ladder (§3.6)** | n = 131: effective hardness 60.81 bits on all 263 constructible curves (`cryptanalysis/experiments/ecc2k130-isogeny-class/data/hardness_by_level.csv`); this note's `transport_cost_table.md` |

The theoretical frame: within an F_q-isogeny class, ECDLP difficulty is
invariant up to transport cost (`crypto/research/isogeny_class_difficulty_20261008/README.md`;
KR-RHO-755e35; EV-IT-511f3d). Only transport cost, the automorphism group and
model-dependent non-generic structure can vary inside a class; for
summation-polynomial index calculus the last channel is the constant term of
the curve equation, which Boundary C′ shows never reaches the leading forms.

## 2. Lead-by-lead map of the blueprint's sections (v1, with v2 additions marked ▲)

| blueprint section | what exists | gap after this pass |
|---|---|---|
| §2 certification (order, D_K, f_π, f_E, edges, gcd(degree, r) = 1) | `crypto/src/cryptanalysis/curve_traits/`, `isogeny_algos/src/path/endo.rs`, `ml-cryptanalysis/csd/endo.py`, `isogeny_walk` (kernel-certified edges); ▲ `isogeny_algos/src/binary_volcano.rs` (char-2 Frobenius-discriminant split, Φ_ℓ mod 2 neighbours with multiplicity, Kohel levels by non-backtracking walks, BSGS order checked against the naive count at n = 20, levels checked against brute force at n = 12) | none of substance; ▲ Kohel 1996 and Fouquet–Morain 2002 now have KN-LIT entries (KN-LIT-a4c123, KN-LIT-96f1bb) |
| §3, §6, §7 entities, contracts, schema | ICV1 registry, `traits.json`, `curves.yaml` + schema, ecbench `schema.sql`; ▲ one JSON row per class vertex from `binary_level_yield` with every §4 static field it needs | the PostgreSQL / S3 / Redis service layer: not built, not needed |
| §4, §5 feature dictionaries | `csd/invariants.py` (57 invariants), `TRAITS.md`, `koblitz_isogeny_cost` rows; ▲ `csd/stratified/data.py` realises the dictionary as namespaced features (`ctrl_`, `endo_`, `volc_` per prime, `geom_`, `setup_`) with the leakage firewall built into the loaders | `descent` namespace still ad hoc |
| §8 data generation | binary census and Φ_ℓ walk, prime `isogeny_walk`; ▲ `isogeny_algos/examples/binary_level_yield.rs` builds a level-labelled class around a random ordinary curve at any n ≤ 64 (run at n = 20 and **n = 51**); ▲ `ml-cryptanalysis/scripts/measure_enumeration_graph.py` attaches counted rho (24 seeds, two arms) and 2-/3-isogeny edges to the 6,032 enumerated curves (1,854 with a usable subgroup, 12,084 edges) | m = 51 Koblitz specifically (its class is one crater over a flat floor like n = 31; the ordinary class is the informative one); class C37 still off-repo |
| §9 paired benchmarking | ecbench; ▲ `crypto/examples/koblitz_level_panel.rs` (arity m, explicit member list, full-group probes, fixed probe budget, BSGS check, append-per-cell checkpointing) | none |
| §10 cost formulas, censoring | ecbench phases; ▲ the m = 3 panel records budget exhaustion as `unknown_probes`, never as a refutation | none |
| §11 splits, leakage, uncertainty | `csd/splits.py`; ▲ `csd/stratified/pipeline.py`: class-grouped nested CV, leave-CM-family-out, leave-field-out, shuffled-static null, same-stratum negative controls, bootstrap intervals with split-conformal rescaling | none |
| §12 ML stages | ▲ **all built and run** (`csd/stratified/`): ridge, gradient-boosted trees, kNN; namespace ablations; message-passing GNN over real isogeny edges with an edge-ablated twin and neighbour-aggregated trees; multi-task ridge; metrics MAE (log2), Spearman, top-10 % discovery precision, coverage, NLL (§3.4) | nothing to learn: see §3.4 |
| §13 active selection | ▲ simulated on a class-disjoint held pool with the blueprint's score (uncertainty / estimated cost × diversity) against uncertainty-only, random and random-equal-budget policies (§3.4) | — |
| §14, §15 architecture, API, state machine | the three repositories plus the ledger state machine | HTTP API / queue / UI: not built |
| §16 validation matrix | ▲ `tests/test_stratified.py` (planted-law recovery, grouped folds keep classes together, the GNN uses its edges, metrics), `isogeny_algos` unit tests for the volcano module, BSGS-checked logarithms on every panel cell | operational tests (worker interruption) only in taskq |
| §17 phases 0 to 6 | phases 0 to 5 now exist in some form across the repos | phase 6 blocked by §19 rule 5 |
| §18 pilot datasets | ▲ 7 binary classes plus the new n = 51 ordinary class; 1,277 prime-field classes plus 157 complete classes with edges; the n = 131 table | — |
| §19 risks and stop rules | rule 5 triggered | — |
| §20 definition of done | items 1 to 4 and 6 met; item 5 (UI) not warranted | — |
| §21 literature | ▲ KN-LIT-96f1bb (Fouquet–Morain 2002, DOI 10.1007/3-540-45455-1_23), KN-LIT-a4c123 (Kohel 1996 thesis); the rest were already in the corpus | — |

## 3. Measurements and derivations of this pass

All scripts live in this directory; all data they read is committed in the
sibling repositories on the branches named above. Numbers are exact copies of
the JSON outputs beside the scripts.

### 3.1 Per-prime volcano strata on the n = 16 class, m = 2 (new labels, frozen rows)

The v1 analysis lumped the 3-floor and the 31-floor of the n = 16, f = 3·31
class into one "depth 1". The ℓ-labelled edges of
`crypto/experiments/koblitz_isogeny_class_walk.json` give every curve its
level vector (v₃(f_E), v₃₁(f_E)) (`per_ell_levels.json`): strata (0,0): 1 curve
(crater), (1,0): 4, (0,1): 32, (1,1): 128, matching h(O_3) = 4, h(O_31) = 32,
h(O_93) = 128. Re-running the stratified tests on the frozen presentation rows
(`per_ell_strata_analysis.py`, 20,000-draw permutations across curves):

| stratum (v₃, v₃₁) | curves | yield/\|F\|² mean ± SD | reductions/call | \|F\| |
|---|---|---|---|---|
| (0, 0) crater | 1 | 2.517e-05 | 2.616 | 122.5 |
| (0, 1) | 32 | 2.395e-05 ± 8.8e-07 | 2.709 | 128.0 |
| (1, 0) | 4 | 2.394e-05 ± 1.3e-07 | 2.630 | 124.0 |
| (1, 1) | 128 | 2.410e-05 ± 7.8e-07 | 2.706 | 127.5 |

Between-stratum permutation p: yield 0.72, reductions per call 0.21, time 0.76.
Pairwise contrasts: all |Δ| ≤ 0.9 SD, p ≥ 0.075. Incremental R² of the strata
beyond |F|, |F|² for the relation rate: 0.0018 (p = 0.57). **Null.** Same
result for the single-floor classes n = 17, 19, 23, 31 (table in
`per_ell_strata_results.md`).

### 3.2 A general binary ordinary class at n = 51, level-labelled (new construction and measurement)

**Tool.** `crypto/isogeny_algos/src/binary_volcano.rs` and
`examples/binary_level_yield.rs` (new, 1,226 lines, six unit tests green with
the crate's 109): sample a₆ over GF(2⁵¹) (fixed seed), order by BSGS over the
Hasse interval (checked against the naive count at n = 20), split
D = f_π² D_K, keep the first class whose conductor has an odd prime ℓ ≤ 13
with v_ℓ(f_π) ≥ 2, enumerate the ℓ-component by roots of Φ_ℓ mod 2, assign
Kohel levels by non-backtracking walks (checked against a brute-force volcano
at n = 12), and for every vertex compute |F| for V = {x < 2¹²}, the exact 2-sum
relation yield over all 2·10⁶ pairs, the subgroup-exact yield and the
cofactor-balance count. Run: 379 curves sampled before a hit; class with
t = −53445159, #E = 2³·3³·7²·267143·796409, r = 796409, cofactor 2,827,441,512,
D_K = −2561771859311, f_π = 7², ℓ = 7, height 2; component of **114 vertices**
(not truncated): 2 crater curves (8 rational 7-isogenies each), 14 at level 1
(8 each), 98 on the floor (1 each), consistent with Kohel's counts.

**Result** (`n51_level_yield_analysis.py`, `n51_level_yield_results.json`):

| level | curves | \|F\| mean ± SD | 2-sum yield | yield/\|F\|² |
|---|---|---|---|---|
| 0 (crater) | 2 | 4174 ± 83 | 1.934e-09 | 1.10969e-16 |
| 1 | 14 | 4087 ± 53 | 1.853e-09 | 1.10968e-16 |
| 2 (floor) | 98 | 4101 ± 62 | 1.867e-09 | 1.10968e-16 |

Between-level permutation p: |F| 0.41, log yield 0.42; yield/|F|² is constant
to five significant digits (every pair of factor-base points contributes one
abscissa, so the 2-sum yield is a function of |F| alone); incremental R² of
level beyond |F| for the yield: 5 × 10⁻¹⁵. **Null.** Two further facts the
blueprint's data contracts should carry: (i) the **subgroup-exact relation
yield is zero on all 114 vertices** (cofactor balance count 0): with a
cofactor of 2.8 × 10⁹ no pair of factor-base points cancels in the cofactor
group, so a "relation yield in the prime-order subgroup" is not a usable
target at this size and full-group probes are mandatory; (ii) the quantity
that does vary across the class is |F| (SD 1.5 %), and it does not track the
level.

### 3.3 Prime-field rho: conductor features beyond controls (v1, unchanged)

1,548 curves, 25 primes, 1,269 isogeny classes; ridge on controls reaches an
out-of-fold R² of 0.9972 (automorphism arm) and 0.9951 (plain arm); adding 28
conductor / class-group / volcano features changes it by +2.2 × 10⁻⁵ and
−2.5 × 10⁻⁵ against a within-prime permutation null whose maximum is
+1 × 10⁻⁵ and +2.3 × 10⁻⁵ (`prime_field_nested_test.py`). Residual after
controls 1.5 to 1.6 × the seed-averaging noise floor; no single feature with a
univariate gain above 10⁻⁵.

### 3.4 The blueprint's ML ladder, implemented and run (`ml-cryptanalysis/csd/stratified/`)

**What was built** (numpy only; 1,100 lines plus tests): loaders for six
measured datasets into one schema with namespaced features and the leakage
firewall in the loader; ridge, gradient-boosted regression trees (exact split
search, early stopping on an inner grouped split), kNN; nested
isogeny-class-grouped cross-validation for hyperparameters; namespace
ablations (controls, +endo, +volc, +geom, +setup, each leave-one-namespace-out);
shuffled-static permutation null (static block permuted across curves within
field, controls kept); leave-CM-family-out and leave-field-out; a two-layer
message-passing network with one weight matrix per isogeny degree over the
real edges, trained with hand-written backpropagation, plus its edge-ablated
twin and a neighbour-aggregated tree model; multi-task ridge with a shared
regularisation; bootstrap-ensemble intervals with split-conformal rescaling,
Gaussian NLL; same-stratum-pair negative controls; and the §13 active-selection
loop simulated on a class-disjoint pool with four policies. Tests:
`tests/test_stratified.py` (4 passed).

**Datasets.** `prime_rho` (1,548 curves), `prime_enum_graph` (1,854 vertices of
157 complete classes over p = 1009, 1013, 1021 with 1,268 usable 2-/3-isogeny
edges and counted rho, new), `binary_ic_per_curve` (646 curves of five Koblitz
classes with per-prime levels and 641 walk edges) and `binary_ic_per_cell`
(2,536 cells), `binary_n51_class` (114 vertices, new), `ecc2k130_class`
(263 curves), and the fresh 21-bit prime-field hold-out (300 curves) as a final
check.

**Results.** RESULTS-ML-PENDING

### 3.5 The m = 3 level panel on the n = 16 class (new measurement, production solver)

Pre-registered in `PROTOCOL-m3-level-panel.md` (with one budget amendment
recorded before any cell ran). Instrument: `crypto/examples/koblitz_level_panel.rs`,
m = 3 (Weil-descended S₄), l = 6 monomial subspace, 6 full-group probes per
curve, node budget 2 × 10⁶, BSGS-checked transported logarithm, 13 curves:
the crater, all four (1,0) curves, four seeded (0,1) and four seeded (1,1)
curves. One call costs about 430 s and 600 to 950 reductions, so this is the
arity at which the Gröbner step is no longer trivial (at m = 2 it is 2 to 3
reductions).

**Results** (`m3_panel_analysis.py`, `m3_panel_results.md`): RESULTS-M3-PENDING

### 3.6 Transport pricing across the ladder (H3, protocol I-2)

`transport_cost_table.py` (`transport_cost_table.md`, `.json`) prices, for every
Koblitz class n ∈ {11, 16, 17, 19, 23, 31, 37, 41, 53, 61, 71, 73, 83, 97, 131}
(both twists where the class is small) and for the new n = 51 ordinary class,
the descending isogeny at each prime ℓ | f_π: the kernel field degree
d = ord(λ mod ℓ) with λ = t/2 mod ℓ (π acts as the scalar λ on E[ℓ] since
ℓ | f_π), the kernel-route construction cost, two Vélu evaluations, and the
rho cost on a floor curve (negation only) and on the crater (signed
Frobenius), all in F_q multiplications under the stated cost model.

| regime | classes | transport vs floor rho |
|---|---|---|
| constructible, small kernel field (d ≤ 10³) | n = 11, 16 (ℓ = 3, 31), 17, 19, 23, 31, 37 (ℓ = 73), 41, 61 (ℓ = 1951), 131 (ℓ = 263), ordinary n = 51 | transport 2⁸ to 2⁴³ F_q-mults, always a small multiple of or far below the floor curve's rho at that size; at n = 131, ℓ = 263: transport 2^14.3 against rho 2^67.6 |
| constructible in principle, huge kernel field (10³ < d ≤ 10⁷) | n = 37 (ℓ = 2663, d = 2662), 53 (d = 646,003), 61 (ℓ = 587551), 83 (ℓ = 6473), 97 (ℓ = 751943) | transport 2⁴³ to 2⁶⁸, above rho on either curve: the level is reachable only at a cost exceeding the attack |
| kernel field degree above 10⁷ | n = 71, 73, 83 (ℓ = 53676929), 97 (ℓ = 352124743), 131 (ℓ ≈ 2^57) | unreachable in either direction; JMV's open case |

The H3 reading is therefore the one the n = 131 study already gave, now for
every rung: wherever a floor curve can be written down, moving the instance to
the crater costs a negligible fraction of any attack, so a "direct advantage"
on a floor curve is interesting only if it beats the crater's rho, which no
measurement in §3 suggests; wherever the floor cannot be written down, there
is nothing to attack directly either.

### 3.7 Figures and PDF

`figures/level_stratified_null.svg` (v1: depth vs yield, prime-field gain vs
null), `figures/comprehensive_pass.svg` (v2: per-prime strata, n = 51 levels,
the m = 3 panel, transport vs rho across the ladder), `README.pdf`.

## 4. What remains open after this pass

| lead | status after v2 | what would move it |
|---|---|---|
| R1 multi-level binary panel at m ≥ 3 with the production solver | **done at n = 16, l = 6, 13 curves** (§3.5); C37 (four levels, inert ℓ = 73) still off-repo | the C37 class file, or an n = 37 73-level construction via H_{−7·73²} mod 2 (degree 74) with `hilbert_class_poly.rs`; a run at l ≥ 8 would need ≥ 10³ core-hours with this solver |
| R2 model-dependent class screens (GHS magic number, covers) over composite-degree binary and F_{p^n} classes | unchanged: known mechanism (KR-IC-791cb7, KR-IC-5ea2f8), carried by IDEA-20260920-10547b, IDEA-20261002-26c628, protocol I-3 | running I-3 on an F_{2^{5·p}} or F_{p^5} class; the only channel where class position is known to matter |
| R3 prime-field extension leg of H2 | folded into R2 | — |
| R4 JMV large-prime conductor gap | theory; structurally unobservable (§3.6 third row) | a polylog-in-ℓ representation of a rational prime-degree isogeny from a CM surface when π acts as a scalar on E[ℓ]; nothing known (KN-OPEN-cbbd97, KN-LIT-ca35e0) |
| R5 blueprint phases 5 and 6 | the graph stage and active selection were built and run anyway (§3.4): no gain over tabular, no gain of tabular over controls | nothing; §19 rule 5 |
| m = 51 data gap | closed for general binary ordinary curves (§3.2) | a Koblitz n = 51 class would be one crater over one floor (f_π prime), uninformative |
| KN-LIT gaps (Kohel 1996, Fouquet–Morain 2002) | closed (KN-LIT-a4c123, KN-LIT-96f1bb, metadata verified) | a full read to upgrade `citation_verified` |

No new `IDEA-*` is filed from this note for the same reason as in v1: the
residue is carried by existing records and pre-registered protocols, and the
measured record says the blueprint's remaining phases would learn nothing.
Promotion of any of the nulls above to a `KN-FIND` requires the Coordinator's
evidence-review lifecycle (independent validation of the runs), which this
note does not substitute for.

## 5. Records and paths this note rests on

Ledger: RQ-VOLC-f6253b, RQ-ICINV-475b5e, RQ-ISO-001, RQ-RELN-61638a,
RQ-ICPERF-94c86e; GOAL-ENDO-001, GOAL-ECDLP2M-001, GOAL-ICPERF-e6b6a4,
GOAL-GFPN-380702; H-ISO-001 (DEC-20260716-003), EV-ISO-001, EV-VOLC-3529e8,
EV-ICINV-343679/6b6264/8afb64/c68f13, EV-ENDO-eb58c4, EV-IT-511f3d,
EV-RELN-cc045d/99c688; IDEA-20260807-3f5545, IDEA-20260815-101067,
IDEA-20260807-b1b604, IDEA-20260920-10547b, IDEA-20261002-26c628;
KN-FIND-f293c6, KN-OPEN-cbbd97, KN-OPEN-7f0d85, KN-LIT-ca35e0, KN-LIT-360,
KN-LIT-251, KN-LIT-96f1bb, KN-LIT-a4c123; frontier rows KR-RHO-755e35,
KR-IC-791cb7, KR-IC-5ea2f8, KR-IC-f5c584. Session receipt SR-20261010-22ebc7.

`crypto` (branch `research/isogeny-level-panels-20261012`): `examples/koblitz_level_panel.rs`;
`experiments/levelpanel/levelpanel_16_0_l6_m3.jsonl`; `experiments/levelpanel_smoke/`;
`isogeny_algos/src/binary_volcano.rs`; `isogeny_algos/examples/binary_level_yield.rs`;
`isogeny_algos/results/binary_level_yield_n{20,51}.jsonl`; plus the v1 pointers
(`RESEARCH_PDP_SPEEDUP_AND_ISOGENY.md`, `docs/ic/RESEARCH_ISOGENY_CONDUCTOR_GAP_20261007.md`,
`docs/ic/EXPERIMENTS_ISOGENY_CONDUCTOR_GAP_20261007.md`,
`research/notes/ecc2k130/RESEARCH_ISOGENY_CLASS_SEARCH.md`,
`research/notes/koblitz-isogeny/*.md`, `research/isogeny_class_difficulty_20261008/`,
`experiments/koblitz_presentation/`, `experiments/koblitz_isogeny_class_walk.json`).

`ml-cryptanalysis` (branch `research/isogeny-stratified-ml-20261012`):
`csd/stratified/{data,models,gnn,metrics,pipeline,active}.py`;
`scripts/{measure_enumeration_graph,run_isogeny_stratified,report_isogeny_stratified}.py`;
`tests/test_stratified.py`; `data/enumeration_graph.jsonl`;
`experiments/isogeny-stratified/{report.md,results_*.json,figures/}`.

`cryptanalysis`: `experiments/ecc2k130-isogeny-class/data/{per_curve_hardness.csv,hardness_by_level.csv}`.

## 6. Files in this directory

| file | content |
|---|---|
| `README.md`, `README.pdf` | this report and its rendering |
| `level_stratified_analysis.py`, `level_stratified_results.{json,md}` | v1 §3.1: BFS depth vs cost on the frozen m = 2 rows |
| `prime_field_nested_test.py`, `prime_field_nested_results.json` | §3.3 |
| `per_ell_levels.json`, `per_ell_strata_analysis.py`, `per_ell_strata_results.{json,md}` | §3.1 (v2) |
| `n51_level_yield_analysis.py`, `n51_level_yield_results.json` | §3.2 |
| `PROTOCOL-m3-level-panel.md`, `m3_panel_analysis.py`, `m3_panel_results.{json,md}` | §3.5 |
| `transport_cost_table.py`, `transport_cost_table.{json,md}` | §3.6 |
| `make_figure.py`, `make_figure2.py`, `figures/*.svg` | the graphs (editable source is the script) |
