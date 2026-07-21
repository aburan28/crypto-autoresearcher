# Research-Director Idea Generation — 2026-07-17 (Batch 2)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Mission:** propose *mechanism-new*, falsifiable directions whose *complete* cost could
eventually beat the single-target Pollard-rho `0.886·sqrt(n)` baseline for ECDLP over
**ordinary prime fields**. Toy correctness, a new coordinate system, a relation certificate,
faster preprocessing, or a solver swap is explicitly **not** a breakthrough.

This is an autonomous scheduled run (no user present). A prior run today
(`research/idea_generation_20260717.md`, 12:48) already produced a 12-candidate batch
(A1 BKK/mixed-volume, A2 elliptic-net/EDS, A3 incidence-reporting, B1 jet/dual-number,
B2 tensor-train, B3 tropical/p-adic, C1 quiver-composition, C2 Lattès transfer-operator,
C3 xedni-2.0, D1–D3 barriers). **That run consumed every "outside-vocabulary" seed named in
the task prompt** (Hasse-jet, tropical/Newton-polytope, incidence-reporting, arithmetic-dynamical
transfer operator, noncommutative correspondence, tensor-network/separator-rank). This Batch-2
report therefore holds itself to a **double novelty bar**: each candidate must be mechanism-new
relative to (a) the ledger, and (b) the 12 Batch-1 candidates. Fingerprints for the Batch-1
twelve are treated as additional negative controls.

---

## 0. Review scope and inventory census

**Sources read (all four required, plus derived corpus and Batch-1):**

1. `research_ledger.md` (2.76 MB, 2248+ lines).
2. `ecdlp_index_calculus_state/research_ledger.md` (764 KB; ECFG functional-graph + direct-source
   packet track; open-frontier + ECFG-001.. hypotheses).
3. `research/non_generic_transfer_search_20260610.md` (390 lines; transfer channel search +
   PO-001..006 appendix; read in full).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` (10 primary entries; read in full).
5. Referenced corpus: `research/idea_generation_20260717.md` (Batch-1, read in full);
   negative-controls tables; RT-1472/RT-1476 frontier rows; the ISO-AR/ISO-SP Kani atlas;
   PO-transfer 003..006; Cartier–Manin TRANSFER-NR-011/015/016 rows.

**Census method.** Rather than re-derive the 638-ID inventory from scratch (Batch-1 already built
a machine-readable census of **638 distinct negative IDs**, **≈427 active hypotheses**, **≈968
positive signals** across families ECFG/TRANSFER/ISO-AR/ISO-SP/SHA1/`NR-`), this run **verified
that census by targeted keyword sweeps of both ledgers** and extended it with the mechanism-keyword
occurrence table below. The Batch-1 family map (M1 ECFG coordinate IC, M2 large-prime graph,
M3 implicit membership backend, M4 cover/Prym/Jacobian transfer, M5 oriented-CM isogeny/self-pairing,
M6 ECFG public selectors) is adopted verbatim; the six standing barriers (B-Dreg, B-trace-fiber,
B-permutation, B-preproc, B-explicit-edge, B-n=1 collapse) are respected as frontier constraints.

**Mechanism-keyword occurrence (both ledgers), used to certify LEDGER-NEW distinctions:**

| Mechanism keyword | main ledger | IC ledger | Interpretation |
|---|---:|---:|---|
| Kani | 24 | 0 | **M5 only** — isogeny reconstruction / self-pairing / connecting-map recovery; *never* a genus-2 Jacobian relation engine |
| modular composition | 3 | 0 | tried as FLINT **single-residual** membership (NEGATIVE, P1442/1443); **transposed/batched branch flagged OPEN** |
| Cartier / Hasse-Witt | 2 | 0 | certify *anchor-invariant* isotypic eigenvalues (TRANSFER-NR-011/015/016) — supports an order-only barrier |
| hypergraph | 2 | 0 | only a **null control** (PO73) that matched signal; **homology absent** |
| two-sided | 2 | 0 | statistics term ("two-sided sign test") only — **NFS two-sided relations absent** |
| special-q | 1 | 0 | one C3-augmentation Picard mention; no EC-IC descent accelerator |
| sumset | 2 | 0 | object mentioned; **sum-product / Bourgain–Gamburd growth bounds absent** |
| formal group | 0 | 0 | **absent** |
| real multiplication | 0 | 0 | **absent** ("RM" 460× = form/term/norm substring noise) |
| canonical lift / Serre–Tate | 0 | 0 | **absent** |
| representation technique / Howgrave | 0 | 0 | **absent** |
| Kedlaya / multipoint evaluation | 0 | 0 | **absent** (only FLINT modular composition) |
| p-curvature / crystalline / Dwork | 0 | 0 | **absent** |
| Waring / mixed-volume / elliptic net / dual-number / quiver / tensor-train | 0–1 | 0 | Batch-1 only; not yet in the *ledger* proper |

**Load-bearing bottom line (unchanged from Batch-1, re-verified):** *No ledger entry demonstrates a
complete-cost single-target speedup over Pollard rho on prime-field ECDLP.* Every empirical
"below rho" is amortized-many-target and/or setup-uncharged (e.g. ECFG-P845/846 public-factor
packets at 0.61× rho are relation-generation precursors, explicitly **not** target descent). The
only rho-beating paths on record are **two conditional restricted-model targets that remain
unrealized:**

- **ECFG-RT-1472** (2-large-prime graph): cost exponent `max(2ℓ,1−ℓ,1+1/5−2ℓ)`, minimized at
  `ℓ=1/3` → **2/3**. Crosses `1/2` only with explicit-advice **enrichment `δ>1/4`**, which every
  explicit 2-LP deck tried gives `δ≤1/4` (NR-1475: effective δ ≤ 0.021). *Under-attacked: all 12
  Batch-1 candidates went at RT-1476, none at RT-1472.*
- **ECFG-RT-1476** (m-ary implicit membership backend): total `2/(m+1−α)` for `α≤1`, else
  `(1+α)/m`; **m=4 needs `α<1`, m=5 needs `α<3/2`**, m≤3 impossible. All tried backends miss it
  (serial-S3 `L^1.675` NR-1477; resultants dense `4L²` MX-1478; char buckets no concentration
  NR-1475).

---

## 1. Novelty gate — Batch-1 fingerprints treated as negative controls

Each Batch-2 candidate is checked against these Batch-1 fingerprints (in addition to the ledger):

| B1-id | mechanism | primitive it owns (now a control) |
|---|---|---|
| A1 | BKK/mixed-volume | polyhedral-homotopy path count of `S_m` |
| A2 | elliptic-net/EDS | net-value column factorization |
| A3 | incidence-reporting | semialgebraic cell reporting over `F_p²` |
| B1 | jet/dual-number | Hasse-derivative tangent pre-filter |
| B2 | tensor-train | separator/Schmidt rank of the `S2|S3` operator |
| B3 | tropical/p-adic | valuation-stratified root lifting to `Q_p` |
| C1 | quiver-composition | noncommutative composition of `Cl(O)` correspondences |
| C2 | Lattès transfer op | Perron–Frobenius operator of `x∘[ℓ]` |
| C3 | xedni-2.0 | LLL/BKZ low-height global MW lift |
| D1/D2/D3 | barriers | nilpotent-no-rank / permutation-no-gain / separator-rank bound |

A Batch-2 candidate sharing a Batch-1 primitive is rejected as duplicate.

---

## 2. Twelve candidates

Notation: `q≈n` prime subgroup order; `B=L≈n^(1/5)` factor base; rho `≈0.886·n^(1/2)`.

### Group A — conservative extensions of known index calculus

---

## Candidate: A1 — Three-large-prime hypergraph homology enrichment (RT-1472 attack)

### One-sentence mechanism
Exploit the **k-uniform (k≥3) large-prime incidence complex** so that relations are read off its
**first simplicial homology `H_1` (cycle space of a 2-complex)** rather than a graph's cycle rank,
testing whether 3-LP hyperedge density supplies the advice-enrichment `δ>1/4` that RT-1472 needs to
push the 2-LP exponent below `1/2`.

### Status
HYPOTHESIS

### Novelty classification
**NOVELTY-UNVERIFIED** for the EC/Semaev setting (LEDGER-NEW: 3-LP / hypergraph-homology absent;
hypergraph appears only as a matched *null control*). **Literature caution (folded in):** the
standard double-large-prime trick already *is* an `H_1`-of-a-1-complex computation (Cavallar 2000/2002),
and the factoring 2LP→3LP jump gives only **constant-factor**, not exponent-level, yield gains — so
the honest prior is that `H_1` of a 2-complex likewise changes constants, not the exponent, unless
EC-addition structure biases facet incidence past the random-complex null.

### Semantic fingerprint
- object: `k`-uniform large-prime incidence complex `Δ` on residual columns of EC coordinate IC.
- ops: EC arithmetic, large-prime column tagging.
- hidden structure: `H_1(Δ)` (2-complex cycle space) vs graph nullity.
- discarded: full explicit `L²` (2-LP) / `L³` (3-LP) advice materialization.
- retained: the boundary map `∂_2` kernel (homological relations).
- relation primitive: `A+C=R + Σ(large primes)` with ≥3 shared large-prime facets.
- compression primitive: simplicial closure — relations = `ker ∂_1 / im ∂_2`.
- rank mechanism: `dim H_1(Δ)` (Betti number), not graph cycle count.
- descent: large-prime-log propagation (standard).
- dominant cost exponent: enrichment `δ` from 3-LP facet density — **the object of measurement**.

### Nearest ledger entries
1. **ECFG-RT-1472** — same target (cross `1/2` via `δ>1/4`), but RT-1472 is computed for **2-LP
   graphs (edges)**; A1 uses a **2-complex (triangles)**. *Distinction: `H_1` of a 2-complex can
   have Betti number growing with facet count in a way graph nullity cannot — the δ accounting is a
   different combinatorial quantity.*
2. **ECFG-NR-1475 (char buckets, δ≤0.021)** — both chase 2-LP enrichment; NR-1475 uses *character
   residue* columns, A1 uses *higher-arity incidence*. *Distinction: arity of the relation, not the
   column labels.*
3. **M2 large-prime graph** — A1 is its `k≥3` homological generalization. *Distinction: cycle
   space of a complex vs a graph.*
4. **PO73 "support-hypergraph relabel control"** — the ledger used a hypergraph *relabeling* as a
   null that reproduced signal. *Distinction: A1's homology is a genuine relation source, and its
   experiment must beat exactly that matched hypergraph null.*
5. **ECFG-RT-1476** — different frontier (membership backend); A1 does not touch it.

### Nearest literature
Lenstra–Manasse 1994 (two large primes); Leyland–Lenstra–Dodson–Muffett–Wagstaff 2002 (MPQS with
three large primes); **Cavallar 2000/2002 (NFS filtering / three-large-prime variant — the sharpest
threat: 2LP→3LP gives only constant-factor yield, and 2LP already equals `H_1` of the relation
1-complex)**; Gaudry–Thomé–Thériault–Diem 2007 (double-large-prime for hyperelliptic genus-≥3 IC,
`Õ(q^{2−2/g})`). Gap: no one has computed the *homological* (`H_1` Betti / 2-complex) relation yield
or the enrichment `δ_3` for **EC coordinate IC over `F_p`** at `B=n^(1/5)` with `k≥3` facets, and no
source establishes an *exponent* (vs constant-factor) gain there.

### Target family
Random ordinary prime-order short-Weierstrass `E/F_p`, `p` prime, `n=#E` prime, `j∉{0,1728}`,
`q≈L^{5}`. Excluded: anomalous, supersingular, small embedding degree, small-discriminant CM.

### Full algorithmic path
1. **Factor base:** `interval_x` base of size `B=L`; a large-prime column set of size `~L^{ℓ'}`.
2. **Relation generation:** collect five-term `A+C=R` events carrying **≥3** unmatched large-prime
   columns; each is a 2-simplex (triangle) on those columns.
3. **Witness extraction/verification:** replay EC additions; verify each facet's large-prime tags.
4. **Relation probability:** governed by 3-LP facet supply `~ (#events)·(L^{ℓ'})^{-2}` — measured.
5. **Matrix:** boundary operator `∂_1:C_1→C_0`; usable relations `= dim ker ∂_1 − dim im ∂_2`;
   target `≥ B−1` full-prime-eliminated rows.
6. **Factor-log calibration:** standard, after large-prime elimination via `H_1` generators.
7. **Descent:** one-factor online descent per target.
8. **Offline/online:** complex construction is per-curve offline; homology solve online.
9. **Memory/parallel:** facet collection embarrassingly parallel; homology is sparse-`GF(p)` rank.

### Cost model
Setup: collect `Θ(L^{1+1/5})` events; facet incidence `Θ(L^{3ℓ'})`. Relations from `H_1` cost the
same sparse-LA `L²`. **Promotion requires** the measured enrichment `δ_3` (extra relations per unit
advice beyond the 2-LP null) to satisfy `δ_3>1/4`, moving the RT-1472 exponent below `1/2`.
Compare: rho `n^{0.5}`; 2-LP frontier `n^{2/3}`; A1 target `<n^{1/2}` iff `δ_3>1/4`.

### Why existing negative results do not kill it
Avoids **NR-1475** (character buckets — different column labels *and* arity 2) and the **RT-1472
explicit-2-LP `δ≤1/4` boundary** (computed for graphs, not 2-complexes). New operation:
**simplicial `H_1` closure of a `k≥3`-uniform large-prime complex.**

### Likely fatal obstruction
For random incidence the 2-complex is **homologically trivial in the sparse regime** (Linial–Meshulam
threshold): below the connectivity threshold `H_1` is spanned by "obvious" boundaries and carries no
enrichment, so `δ_3→0` just like `δ_2`. The bet is that EC-addition structure biases facet incidence
away from the random-complex null — which is exactly what the matched hypergraph null (PO73) failed
to show at arity 2.

### Minimal falsifying experiment
Six ordinary prime-order curves with `q≈L^5`, `L∈{16,32,64}` (train) and `{128,256}` (holdout);
seeds `20260717..20260722`; collect 3-LP facets; compute `dim H_1(Δ)` and the enrichment `δ_3`
vs (i) a matched random 3-uniform hypergraph null and (ii) the 2-LP `δ_2` control. Positive control:
a planted low-arity structured deck (should show `δ_3>δ_2`). Negative control: uniform-random x-deck.

### Quantitative promotion gate
Measured `δ_3>1/4` **and** growing with `L` across all three train sizes **and** surviving on
holdout, yielding sparse full-rank `t≥B−1` after large-prime elimination. Correctness alone fails
the gate.

### Proof track
Theorem: for the EC-addition-induced large-prime complex, `dim H_1(Δ) = ω(L·δ_2)` with `δ_3>1/4`.
Would follow from a facet-incidence concentration theorem beating the Linial–Meshulam random null.

### Disproof track
`δ_3≤1/4` at all sizes (matching the random-complex null) ⇒ reusable negative extending RT-1472:
"higher-arity large-prime homology gives no advice enrichment past the graph boundary," closing the
k-LP lane in this accounting.

### Reproduction artifact
- contract: `research/experiment_contract_b2a1_three_lp_homology_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2a1_klp_homology_enrichment.sage`
- result/audit: `.../b2a1_klp_result.json`, `.../b2a1_klp_verify.sage`
- ledger id: `KLP-HOM-A1`

---

## Candidate: A2 — NFS-style two-sided coincidence relations (two independent factor bases)

### One-sentence mechanism
Exploit a **two-sided coincidence** — a probe point that decomposes simultaneously over two
*independent* factor bases `F_1` (interval-x) and `F_2` (rational-map / `x^L=1` subgroup) — so a
single event couples logs across both bases, importing the NFS/FFS two-sided relation-density gain
into EC index calculus.

### Status
HYPOTHESIS

### Novelty classification
**POSSIBLY NOVEL, construction-blocked** (LEDGER-NEW: "two-sided" appears only as a statistics term;
literature agent found no two-independent-factor-base EC-IC scheme). **Caution (folded in):** NFS
two-sidedness transferred cleanly to `F_{p^n}^*` DLP (JLSV06, Joux–Pierrot) precisely because a
single integer/polynomial has two independently-smoothness-testable coordinate systems tied by a ring
homomorphism; an ordinary prime-field `E` has **no known second smoothness-supporting "algebraic
side."** Constructing that side *is* the open research question, prior to any algorithm.

### Semantic fingerprint
- object: pair of independent factor bases `(F_1,F_2)`, each `≈L`, over the same `E/F_p`.
- ops: EC arithmetic; two independent membership predicates.
- hidden structure: correlation (if any) between the two decomposition events of the same `R`.
- discarded: single-base-only relations.
- retained: two-sided coincidence events (both decompositions succeed for one `R`).
- relation primitive: `R = Σ_{F_1} = Σ_{F_2}` (one point, two decompositions).
- compression primitive: the shared point `R` links two log-blocks (NFS "shared side" analog).
- rank mechanism: block matrix `[F_1 | F_2]`, full-rank via cross-base coincidences.
- descent: standard one-factor descent on either block.
- dominant cost exponent: two-sided coincidence probability — **object of measurement**.

### Nearest ledger entries
1. **M1 five-term relations (single base)** — A2 requires *two simultaneous* decompositions.
   *Distinction: relation is a coincidence of two independent smoothness surrogates, not one.*
2. **B-n=1 collapse** — the two-sided trick is exactly NFS's answer to "one side has no smoothness";
   A2 tests whether two EC bases together create a usable coincidence rate. *Distinction: two
   surrogates vs one.*
3. **ECFG-NR-1408 (rational-map image bases)** — used a rational-map base *alone*; A2 pairs it with
   an independent interval base and scores coincidences. *Distinction: pairing, not single base.*
4. **Batch-1 A3 (incidence reporting)** — A3 reports pairs *within one base*; A2 seeks agreement
   *across two bases*. *Distinction: cross-base coincidence vs intra-base incidence.*
5. **RT-1476** — A2 is not a single-backend query; it is a two-backend coincidence, a different lane.

### Nearest literature
Buhler–Lenstra–Pomerance 1993 (NFS two-sided: rational + algebraic side); Joux–Lercier–Smart–
Vercauteren 2006 (JLSV, two-sided NFS for `F_{p^n}^*`, two polynomials sharing a factor mod `p`);
Joux–Pierrot 2013 (special NFS two-sided in `F_{p^n}`). Gap (sharpest threat = Joux–Pierrot): those
show the *ring-theoretic infrastructure* two-sidedness needs — two coordinate systems for one object
— which EC-DLP over `F_p` has no known analog of; the "side 2" construction is itself the open problem.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Factor bases:** `F_1` = interval-x (`|x|<X`), `F_2` = `x^L=1` subgroup points; each `≈L`.
2. **Relation gen:** for probe `R=aP+bQ`, attempt `S_m` decomposition over `F_1` **and** over `F_2`;
   keep only `R` where both succeed.
3. **Witness/verify:** replay both decompositions; verify group law both ways.
4. **Relation probability:** `Pr(both) = Pr_1·Pr_2·(1+ρ)` where `ρ` is the measured correlation.
5. **Matrix:** `Θ(L)×2L` block-coupled, target sparse full-rank `≥2L−1`.
6–9: standard calibration/descent; both membership backends offline per curve; parallel.

### Cost model
Per two-sided event: `1/Pr(both)` attempts × (two membership tests). If the events are
**independent**, `Pr(both)=Pr_1·Pr_2 ≪ Pr_1` → *worse* than one-sided. If **positively correlated**
(`ρ>0` via a shared algebraic constraint), the coincidence rate can exceed the product and the
per-relation cost can beat single-base at the same rank yield. Compare rho `n^{0.5}`, single-base
explicit join `n^{0.6}`. **Only a measured `ρ>0` that grows (or stays constant) with `L` matters.**

### Why existing negative results do not kill it
Not a single-base decomposition (≠ M1), not intra-base incidence (≠ Batch-1 A3), not a rational-map
image base alone (≠ NR-1408). New operation: **cross-base coincidence with log coupling.**

### Likely fatal obstruction
The two decomposition events are almost certainly **independent** for generic bases (no shared
"norm" object as NFS has), so `Pr(both)=Pr_1·Pr_2` and the coincidence is *rarer*, not cheaper —
NFS's gain comes from a shared *integer/ideal*, which EC decomposition lacks. The whole bet is that
a structured base pair (e.g. `F_2` = image of `F_1` under an endomorphism) manufactures the shared
object; that risks collapsing to the B-permutation no-gain result.

### Minimal falsifying experiment
`p≈2^20,2^24,2^28`, seeds `20260717..`; for `10^4` probes measure `ρ = Pr(both)/(Pr_1·Pr_2) − 1`
for (a) independent bases (expect `ρ≈0`), (b) endomorphism-linked bases (positive control, expect
`ρ>0`), (c) random-set bases (negative control). Fit `ρ` vs `L`.

### Quantitative promotion gate
`ρ>0` non-vanishing as `L→∞` **and** the resulting two-sided relation-gen exponent `<1/2` in `n`
with sparse full-rank; a shared-object base pair that does not collapse to a permutation.

### Proof track
Theorem: there exists a base pair `(F_1,F_2)` with a common algebraic invariant giving
`Cov(1_{F_1-decomp},1_{F_2-decomp})>0` of order `Pr_1·Pr_2·L^{c}`.

### Disproof track
`ρ→0` for all non-permutation base pairs ⇒ reusable negative: "EC decomposition has no NFS-style
shared side; two-sided coincidence gives no relation-density gain over `F_p`."

### Reproduction artifact
- contract: `research/experiment_contract_b2a2_two_sided_coincidence_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2a2_two_sided_relations.sage`
- result/audit: `.../b2a2_result.json`, `.../b2a2_verify.sage`
- ledger id: `NFS2S-A2`

---

## Candidate: A3 — Transposed/batched Kedlaya–Umans membership (amortization-law backend)

### One-sentence mechanism
Exploit the **transposition principle + Kedlaya–Umans `n^{1+o(1)}` multipoint evaluation** so that
the `Θ(L)` factor-base membership queries needed for one target **share a single near-linear
precomputation**, driving the *amortized* per-query membership exponent below the RT-1476 boundary
that FLINT single-residual modular composition (NR-1442) could not reach.

### Status
HYPOTHESIS

### Novelty classification
**POSSIBLY NOVEL** for the mechanism (literature agent: no EC-IC scheme uses Kedlaya–Umans / fast
multipoint evaluation — the entire Semaev/Gaudry/FPPR/Faugère line is Gröbner/FGLM/resultant based),
but **LEDGER-ADJACENT** (the ledger's FLINT single-residual composition test was NEGATIVE and
explicitly flagged the transposed/batched branch as OPEN). The distinction is a *complexity model*
(amortized shared work), not a solver swap. **Reduction gap (folded in):** Semaev membership is a
*multivariate existence-of-completion* question, not fixed-modulus univariate evaluation; the
reduction to a KU-amenable multipoint-eval form is nontrivial and **undemonstrated** — this is the
first thing the experiment must establish.

### Semantic fingerprint
- object: the `S_m` membership predicate as a polynomial map evaluated at `Θ(L)` points.
- ops: EC arithmetic; fast modular composition (Kedlaya–Umans / transposed).
- hidden structure: shared subresultant/evaluation work across the `Θ(L)` queries of one target.
- discarded: per-query independent evaluation (FLINT model).
- retained: a single `n^{1+o(1)}` batched evaluation table.
- relation primitive: five-term `A+C=R` membership via batched multipoint eval.
- compression primitive: transposition principle (evaluation ↔ interpolation duality).
- rank mechanism: unchanged sparse factor-log matrix.
- descent: same batched backend.
- dominant cost exponent: **amortized** query exponent `α_amort` — object of measurement.

### Nearest ledger entries
1. **ECFG-NR-1442 / H683 (FLINT modular composition)** — same subproblem, but measured **per-query**
   FLINT cost (opaque overhead, `15.89×` global direct scan). *Distinction: A3 measures the
   **amortized** exponent under the transposition principle, the branch the ledger left open.*
2. **TRANSFER-NR-028** — "move only to balanced fast polynomial products or modular composition" —
   A3 is exactly that named next step, with an exponent (not wall-clock) accounting.
3. **RT-1476** — A3 is a concrete backend candidate targeting `α<3/2` (m=5). *Distinction: candidate
   vs gate.*
4. **Batch-1 A3 (incidence reporting)** — data-structure reporting; A3-here is straight
   algebraic-complexity fast evaluation. *Distinction: multipoint-eval amortization vs geometric
   cell reporting.*
5. **ECFG-NR-1477 (serial-S3 dense state)** — A3 never materializes state; it batch-evaluates.

### Nearest literature
Kedlaya–Umans 2011 (fast modular composition / multipoint eval, `n^{1+o(1)}`); van der Hoeven–Lecerf
2019 (fast multivariate multipoint eval); Bostan–Schost (transposition principle). **Sharpest threat
= Faugère–Gaudry–Huot–Renault 2014 (ISSAC, sub-cubic change of ordering) and the symmetrized-summation
line:** the EC-IC community invested heavily in exactly this membership bottleneck and converged on
Gröbner/FGLM tricks, *not* multipoint evaluation — suggesting either the KU reduction is unnatural or
simply unexplored (the search cannot distinguish). KU is also historically noted as impractical below
large sizes (the `o(1)`/galactic-constant risk).

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Factor base:** interval/rational-map base `B=L`.
2. **Relation gen:** encode the `Θ(L)` pair-sum membership tests for one target as multipoint
   evaluation of a single composed polynomial; batch-evaluate via KU/transposed composition.
3. **Witness/verify:** replay each reported membership `A+C=R`.
4. **Relation probability:** unchanged `Θ(B)` supply.
5. **Matrix:** `Θ(L)×L` sparse full-rank target.
6–9: standard; the batched evaluation table is per-target online but shared across its `Θ(L)`
queries; embarrassingly parallel across targets in the descent phase.

### Cost model
FLINT model: `Θ(L)` queries × (opaque single-composition cost) → `≥L²`. KU/transposed model: one
`L^{1+o(1)}` batched evaluation → **amortized** `α_amort = 1+o(1)` per relation batch, i.e. total
relation-gen `L·L^{o(1)} = n^{1/5+o(1)} < n^{1/2}` *if the o(1) is genuinely sub-`L^{1/2}`*.
Promotion iff measured amortized exponent `<3/2` (m=5) / `<1` (m=4). Compare NR-1442 `15.89×` scan.

### Why existing negative results do not kill it
NR-1442 measured the *per-query* FLINT constant, not the *amortized* exponent; the transposition
principle is precisely the operation that converts `Θ(L)` independent compositions into one shared
near-linear evaluation. New operation: **transposition-principle batching of the membership map.**

### Likely fatal obstruction
Kedlaya–Umans is `n^{1+o(1)}` with a **large `o(1)` / galactic constant**; at `L≈n^{1/5}` (small),
the crossover where KU beats FLINT's `L²` may lie far above cryptographic `L`, so the *measured*
exponent at reachable sizes stays ≥ the FLINT scan — the same wall NR-1442 hit, now hidden in the
`o(1)`.

### Minimal falsifying experiment
`p≈2^20,2^24,2^28`; implement (i) FLINT single-residual baseline, (ii) a transposed/batched
composition; measure **operation-count exponent** (not wall-clock) of amortized per-relation
membership vs `L`. Positive control: a synthetic batched-evaluation task where KU provably wins.
Negative control: the FLINT per-query path. Fit `log(ops/relation)/log L`.

### Quantitative promotion gate
Amortized membership operation-count exponent `α_amort<3/2` (m=5) across all three sizes, with a
crossover below `L≈n^{1/5}` at the largest size, and sparse full-rank relations recovered.

### Proof track
Theorem: transposed KU composition answers the `Θ(L)`-query membership batch in `L^{1+o(1)}` field
ops with `o(1)` bounded by a computable function `<1/2` at `L≥L_0` reachable at toy scale.

### Disproof track
Amortized exponent `≥3/2` at all reachable `L` ⇒ reusable negative: "fast modular composition's
`o(1)` overhead keeps EC membership above the RT-1476 boundary at cryptographically reachable
sizes," closing the composition-backend lane on complexity-constant grounds.

### Reproduction artifact
- contract: `research/experiment_contract_b2a3_transposed_ku_membership_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2a3_transposed_ku.sage`
- result/audit: `.../b2a3_result.json`, `.../b2a3_verify.sage`
- ledger id: `KU-BATCH-A3`

### Group B — representation changes

---

## Candidate: B1 — Kani-torsion-glued genus-2 Jacobian with real multiplication (REPRESENTATION CANDIDATE)

### One-sentence mechanism
Exploit a **Kani `(N,N)`-torsion gluing** of `E×E'` into a genuine principally-polarized abelian
surface `Jac(H)` (genus-2 curve `H`) that carries **real multiplication (RM)** by a real quadratic
order, then run **RM-accelerated genus-2 index calculus** in `Jac(H)` whose relation/factor-base
cost is `o(q)` — projecting the recovered logs back to the original `E`-factor — thereby routing the
prime-field DLP through a surface whose intrinsic IC is *not* the elliptic x-line Semaev relation.

### Status
CONJECTURE

### Novelty classification
LEDGER-NEW for the construction (Kani used *only* for isogeny reconstruction in M5, never to build
a relation-carrying Jacobian; "real multiplication", "genus-2 index", "Humbert", "Diem" all 0/1);
LITERATURE-ADJACENT to Gaudry genus-2 IC and to SIDH-attack Kani gluing (which solves *isogeny*
problems, not ECDLP).

### Semantic fingerprint
- object: PP abelian surface `A=Jac(H)` from a Kani `(N,N)`-glue of `E×E'`, with RM by `O_{√d}`.
- ops: EC arithmetic, `(N,N)`-isogeny evaluation, Mumford divisor arithmetic on `Jac(H)`.
- hidden structure: RM eigenform splitting of `H^0(A,Ω^1)` → faster relations.
- discarded: the elliptic x-line Semaev relation (never formed).
- retained: intrinsic genus-2 Riemann–Roch relations, RM-graded.
- relation primitive: degree-2 function on `H` vanishing on factor-base divisors (native genus-2).
- compression primitive: RM eigen-projection halving the effective decomposition dimension.
- rank mechanism: Jacobian relation matrix with RM block structure.
- descent: isogeny-transfer descent from `Jac(H)`-logs to `E`-logs (poly per edge).
- dominant cost exponent: RM-accelerated genus-2 relation exponent vs `q` — object of measurement.

### Nearest ledger entries
1. **NR-022 (scalar Weil restriction / abelian surface)** — that surface is `Res_{F_p^2/F_p}(E)`
   or `E×E` over `F_p`, a **split/scalar** object with the elliptic Semaev degree preserved.
   *Distinction: B1's Kani-glue is a **non-split PP surface with RM**, whose relations are native
   genus-2, not an `F_p`-linear split of the x-line relation.*
2. **PO-transfer-003..006 (cover/Prym)** — those push principal divisors **back to the elliptic
   quotient / x-line** (`z^d=h(P)`, ternary constant-sum on `E1`). *Distinction: B1's relations
   live and are solved **in `Jac(H)`**, never projected to the elliptic Semaev relation.*
3. **M5 Kani atlas (ISO-AR/ISO-PK, 24 entries)** — those use the balanced Kani map for
   **isogeny/connecting-map reconstruction** (order-preserving, no relations). *Distinction: B1
   uses Kani to **build a relation-carrying Jacobian**, not to find an isogeny.*
4. **B-n=1 collapse (Gaudry/Diem)** — the central threat (see D3): fixed-genus IC over the prime
   field `F_p` (no proper subfield) costs `Ω̃(q^{2−2/g})≥q^{1/2}`. *Distinction: B1's only escape is
   RM, which lowers the effective relation dimension — the explicit object of measurement.*
5. **B-permutation (TRANSFER-NR-001)** — an isogeny-transported base gives no rank gain.
   *Distinction: B1's win (if any) is the **RM eigen-split of the surface**, not a transported base.*

### Nearest literature
Kani 1997 (*J. Reine Angew. Math.* 485 — the `(N,N)` anti-isometry gluing criterion / "Kani's Lemma");
Castryck–Decru 2022 (eprint 2022/975) and Robert 2022 (eprint 2022/1038) — revive Kani for **SIDH
isogeny recovery** (torsion data from a protocol transcript, *not* ECDLP); Smith 2008 (genus-3
isogeny transfer of DLP — nearest "move DLP to a friendlier curve," but genus-3→genus-3); **Gaudry
2009 (JSC — sharpest threat: genus-≤2 abelian-variety IC over `F_q` costs `Õ(q)`, a strict loss vs
rho `Õ(√q)` absent a subfield/amortization win)**; Gaudry–Schost (genus-2 RM point counting). Gap:
no construction glues a **bare single prime-field** `E`-ECDLP instance into an **RM-genus-2 Jacobian**
and measures its IC exponent — and there is no free connecting-isogeny data for a bare instance
(supplying `E'`/`N` may itself cost as much as the DLP). SIDH-Kani solves isogenies, not ECDLP.

### Target family
Ordinary prime-order `E/F_p` for which an auxiliary `E'` and `N` exist so the Kani glue is a smooth
genus-2 Jacobian with RM by a **small** real quadratic order. Excluded: cases where the glue is a
product (reducible), or where RM is trivial/large-discriminant (→ the negative control = D3 barrier).

### Full algorithmic path
1. **Factor-base construction:** choose `E'`, `N`; build `H` and `Jac(H)`; RM-eigen-split the
   differentials; factor base = degree-1 places of `H` with `x`-coordinate in an interval, RM-graded.
2. **Relation generation:** search Mumford divisors `D` with `D ∼ Σ (base places)` via native
   genus-2 Riemann–Roch (degree-2 function search), using the RM eigen-projection to reduce the
   decomposition dimension.
3. **Witness/verify:** replay Jacobian arithmetic; verify `D` is principal-plus-base.
4. **Relation probability:** RM-graded smoothness probability — measured vs the non-RM genus-2 null.
5. **Matrix:** Jacobian relation matrix, RM-block, target full-rank on the `E`-isotypic block.
6. **Factor-log calibration:** on the `E`-isotypic RM block.
7. **Target descent:** lift the `E`-target into `Jac(H)`; descend via the RM-block relations; project
   the recovered log back to `E`.
8. **Offline/online:** `H`, `Jac(H)`, RM data per curve offline; relation collection online.
9. **Memory/parallel:** divisor search parallel; memory = factor-base size.

### Cost model
Non-RM genus-2 IC over `F_p`: relation cost `Θ̃(q^{2−2/2})=Θ̃(q)` (Gaudry) — **loses to rho `q^{1/2}`**.
RM escape: if RM splits the relation search into two 1-dimensional problems, the effective exponent
could drop toward `q^{1/2}` or below; **promotion requires a measured genus-2 relation exponent
`<1/2` in `q` on the `E`-block.** Setup: `(N,N)`-isogeny + genus-2 construction, `poly(log q)`.
Compare rho `q^{0.5}`, BSGS `q^{0.5}`+memory, Gaudry genus-2 `q^{1}`.

### Why existing negative results do not kill it
Not a scalar Weil restriction (≠ NR-022: non-split PP surface with RM), not an x-line cover pullback
(≠ PO-003..006: native genus-2 relations), not an isogeny-finding Kani map (≠ M5). New operation:
**Kani torsion-gluing to an RM abelian surface whose relations are solved intrinsically.**

### Likely fatal obstruction
D3: fixed-genus IC natively over `F_p` costs `Ω̃(q^{2−2/g})`; for `g=2` that is `q`, far above rho.
RM is known to give **constant-factor** (not exponent) speedups in genus-2 point counting; if the
same holds for IC relation collection, B1 collapses to `q` and loses. The construction may also be
forced into a **product** (reducible) surface, where it degenerates to `E×E'` (no gain).

### Minimal falsifying experiment
Toy `p≈2^12,2^16,2^20` (genus-2 arithmetic is heavy); construct an RM Kani glue at each; measure the
genus-2 relation exponent on the `E`-block with and without the RM eigen-projection. Positive
control: a genus-2 curve with **large** RM (known faster arithmetic) — should show the split help.
Negative control: a non-RM (generic) genus-2 Jacobian — should show exponent `≈1` (Gaudry).

### Quantitative promotion gate
Measured `E`-block relation-generation exponent `<1/2` in `q` across all three sizes **with** RM,
strictly below the non-RM null, **and** an end-to-end blind `E`-target descent under full charging.

### Proof track
Theorem: RM by `O_{√d}` reduces the genus-2 relation-search dimension so the exponent drops from
`q^{2−2/g}` to `<q^{1/2}` on the RM-eigen block. (Almost certainly false — see D3 — but the exact
RM-vs-exponent statement is the open question.)

### Disproof track (see D3)
RM gives only a constant-factor speedup ⇒ exponent stays `≈q` ⇒ reusable negative closing the
"fixed-genus-over-`F_p` with RM" lane and formalizing D3.

### Reproduction artifact
- contract: `research/experiment_contract_b2b1_kani_rm_genus2_20260717.md`
- impl: `experiments/ecdlp_isogeny/b2b1_kani_rm_genus2_ic.sage`
- result/audit: `.../b2b1_result.json`, `.../b2b1_verify.sage`
- ledger id: `KANI-RM-B1`

---

## Candidate: B2 — Serre–Tate canonical-lift coordinate linearization

### One-sentence mechanism
Exploit the **canonical (Serre–Tate/Deligne) lift `E^can/Z_p`** of an ordinary `E/F_p` and its
**Serre–Tate parameter / unit-root Frobenius** to test whether a canonical `p`-adic coordinate makes
part of the discrete-log action **additive** (linearizable), giving a per-target descent cheaper than
generic search on the `E`-block.

### Status
CONJECTURE

### Novelty classification
**LITERATURE-ADJACENT — settled-negative for the naive (linearization) form.** LEDGER-NEW (canonical
lift / Serre–Tate / crystalline all 0/0) and distinct from Batch-1 B3 (generic `Q_p` lift). **But
(folded in):** Voloch's unification note shows the Smart / Satoh–Araki / Semaev formal-group attacks
are the *same* mechanism, valid **only** for trace-1 (`#E=p`) curves, where the kernel-of-reduction
is `(F_p,+)`; the Hasse bound forbids `p|#E` for trace≠1, so there is no analogous additive quotient.
POSSIBLY NOVEL only for a *non-linearization* deformation-theoretic use (the escape hatch tested here).

### Semantic fingerprint
- object: `E^can/Z_p` (canonical lift), Serre–Tate parameter `q_{ST}`, unit-root `u` of Frobenius.
- ops: canonical-lift computation (Satoh-style), `p`-adic point arithmetic.
- hidden structure: canonical `p`-adic coordinate where `[k]` may act linearly.
- discarded: `F_p` field structure (moves to `Z_p`), but via the *canonical* lift, not a generic one.
- retained: crystalline/Frobenius-rigid `p`-adic invariants.
- relation primitive: additive Serre–Tate-log relation `log_{ST}(kB)=k·log_{ST}(B)` (if it exists).
- compression primitive: canonical-lift rigidity (no height explosion, unlike xedni).
- rank mechanism: n/a if linearization works (direct solve); else standard.
- descent: `p`-adic Serre–Tate log inversion.
- dominant cost exponent: does the canonical log see the `n`-torsion log? — object of measurement.

### Nearest ledger entries
1. **Batch-1 B3 (tropical/`p`-adic lift)** — B3 lifts generically and tracks valuations; B2 uses the
   **unique canonical Frobenius-fixed lift**. *Distinction: canonical (rigid) vs arbitrary lift.*
2. **Batch-1 C3 (xedni height lift)** — xedni's failure is height explosion; the canonical lift has
   **no height** (it is `p`-adic, not global). *Distinction: `p`-adic canonical vs global MW height.*
3. **M5 self-pairing / Frobenius (ISO-AR)** — those use Frobenius eigenvalues for *order/isogeny*;
   B2 asks whether the **unit-root** carries a *per-target log*. *Distinction: per-target vs order.*
4. **B-n=1 collapse** — B2 adds a canonical `Z_p` structure the prime field lacks. *Distinction:
   canonical lift, not Weil restriction.*
5. **Smart/Satoh–Araki anomalous attack (not in ledger)** — the canonical-lift/formal-log attack
   that works **only for trace-1 (anomalous)** curves; B2 asks how far into the ordinary family any
   leakage extends. *Distinction: general ordinary vs anomalous special case.*

### Nearest literature
Serre–Tate 1968 (deformation theory); Satoh 2000 (canonical-lift point counting — order only, a class
function of `E` with no `Q`-dependence); Smart 1999 (trace-1 attack); Satoh–Araki 1998; Semaev 1998;
**Voloch (sharpest threat: unifies Smart/Satoh–Araki/Semaev as one formal-group mechanism, all
trace-1-restricted)**. Gap: canonical-lift methods give **point counting/order**, never a **per-target
discrete log** for a non-anomalous ordinary curve; the only unexplored angle is a non-linearization
Dwork-style deformation use.

### Target family
Ordinary prime-order `E/F_p`, `trace≠1` (non-anomalous). Excluded: anomalous (`#E=p`, already easy),
supersingular. The anomalous case is the **positive control**, not the target.

### Full algorithmic path
1. **Construct** `E^can/Z_p` to precision `π` (Satoh); compute Serre–Tate parameter and unit-root.
2. **Relation/linearization test:** compute `log_{ST}` of `B` and candidate targets; test additivity
   `log_{ST}(kB)=k·log_{ST}(B) (mod p^π)`.
3. **Witness/verify:** if additive, solve for `k` directly by `p`-adic division; verify `kB=Q`.
4. **Relation probability:** n/a if linearization holds; else fall back to a factor base.
5–6. **Matrix/calibration:** only if linearization is *partial* (recovers `k mod p^j`), combine with
   a residual search on the remaining `log(n/p^j)` bits.
7. **Target descent:** `p`-adic log inversion for the recovered part; residual search for the rest.
8. **Offline/online:** canonical lift per curve offline; per-target log online.
9. **Memory/parallel:** precision-bounded; parallel across targets.

### Cost model
If `log_{ST}` linearizes the full `n`-torsion log: cost `= p`-adic-log at precision `π=O(log q)` →
**polynomial**, a break (almost certainly impossible). Realistic: `log_{ST}` sees only the
`p`-primary part, which is **trivial** for prime-order-`n` curves with `n≠p` → **zero** per-target
information. Promotion requires a measured recovery of `≥ε·log_2 n` target bits from the canonical
coordinate. Compare rho `n^{0.5}`.

### Why existing negative results do not kill it
Not a generic lift (≠ Batch-1 B3), not a global height lift (≠ Batch-1 C3), not Frobenius-order data
(≠ M5). New operation: **canonical-lift Serre–Tate coordinate as a per-target log probe.**

### Likely fatal obstruction
The canonical lift and Serre–Tate parameter are **moduli/deformation** data (they encode the
`j`-line direction and the unit-root of Frobenius = order information). The `[k]`-action on
`E^can(Z_p)` reduces to the same hard DLP; the only additive structure is the formal group along the
identity, which sees the `p`-part — **trivial** for `n≠p`. So B2 almost certainly recovers **0**
target bits for non-anomalous curves (this is the D2 barrier direction).

### Minimal falsifying experiment
`p≈2^16,2^20,2^24`; for each, build `E^can`, compute `log_{ST}(kB)` for random `k`, and measure the
number of correctly recovered `k`-bits vs `k`. Positive control: an **anomalous** curve (`#E=p`) —
must recover all bits (Smart). Negative control: a random non-anomalous ordinary curve — expected 0
bits. Sweep precision `π`.

### Quantitative promotion gate
Recovered target-bit fraction `>ε>0` and **growing** with `π` for non-anomalous curves across three
sizes (would be a genuine partial break). Zero recovery ⇒ feeds D2.

### Proof track
Theorem: the Serre–Tate log of an ordinary `E/F_p` restricted to the prime-order-`n` subgroup
(`n≠p`) is identically the reduction map composed with the hard DLP — no additive shortcut.

### Disproof track (= D2 direction)
Prove/measure zero non-anomalous leakage ⇒ reusable negative closing the canonical-lift lane and
sharpening the anomalous-only boundary of formal-group attacks.

### Reproduction artifact
- contract: `research/experiment_contract_b2b2_serre_tate_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2b2_canonical_lift_log.sage`
- result/audit: `.../b2b2_result.json`, `.../b2b2_verify.sage`
- ledger id: `STATE-B2`

---

## Candidate: B3 — Riemann-bilinear (level-≥3 theta) low-degree membership relation

### One-sentence mechanism
Represent factor-base points in a **level-`ℓ` (ℓ≥3) algebraic-theta embedding** with the full
**Heisenberg (theta-group) action**, and use the **bilinear Riemann theta relations** as a
**degree-2 membership predicate**, replacing the degree-`2^{m−2}` Semaev condition with a chain of
bilinear constraints whose exploitable solving degree could be lower than the B-Dreg-conserved
Semaev degree.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (theta/Kummer machinery appears in M4/M5, but as **scalar level-2**
Kummer/Weil (NR-022, closed) or **balanced (8,8) isogeny** reconstruction (M5)); the **level-≥3
non-scalar Heisenberg bilinear-relation** membership predicate is distinct.

### Semantic fingerprint
- object: `E` in a level-`ℓ` theta embedding `P^{ℓ-1}`, with theta-group `H_ℓ` action.
- ops: theta-coordinate arithmetic; bilinear Riemann relations.
- hidden structure: bilinearity of the theta addition law (degree 2 vs Semaev degree `2^{m−2}`).
- discarded: the high-degree elliptic Semaev polynomial.
- retained: a chain of bilinear membership constraints.
- relation primitive: `A+C=R` expressed as bilinear theta identities.
- compression primitive: degree-2 constraint chain (lower first-fall degree, if genuine).
- rank mechanism: standard sparse factor-log matrix after solving the bilinear chain.
- descent: standard.
- dominant cost exponent: exploitable solving degree of the bilinear chain — object of measurement.

### Nearest ledger entries
1. **NR-022 / scalar level-2 Kummer (closed)** — level-2 theta is **scalar** (Kummer line, no
   Heisenberg), and is Dreg-preserving. *Distinction: B3 uses **level ≥3 with the non-scalar
   Heisenberg action** and the genuine bilinear addition, absent at level 2.*
2. **M5 balanced (8,8) theta (ISO-AR-POS-006..)** — those use theta for **isogeny-branch selection**,
   not decomposition relations. *Distinction: relation generation vs isogeny reconstruction.*
3. **B-Dreg** — the central threat: coordinate reparametrization preserves the exploitable degree.
   *Distinction: B3's bet is that the **bilinear** theta chain has a genuinely lower first-fall
   degree than Semaev — a measurable claim, not a coordinate relabel.*
4. **Batch-1 A1 (mixed volume)** — both attack the decomposition-solve cost; A1 via polytope, B3 via
   degree. *Distinction: solving-degree of a bilinear system vs mixed volume of `S_m`.*
5. **M1 five-term relations** — B3 replaces the degree-`2^{m−2}` predicate with bilinear constraints.
   *Distinction: relation encoding degree.*

### Nearest literature
Mumford (algebraic theta / Riemann relations); Lubicz–Robert (theta arithmetic / isogenies);
Faugère–Huot–Joux–Renault–Vitse 2014 (symmetrized `S_m` via small torsion — the closest "lower the
degree via structure" result). Gap: no theta-level-≥3 bilinear membership predicate for `F_p` EC
decomposition, and no first-fall-degree measurement of it vs Semaev.

### Target family
Ordinary prime-order `E/F_p` with rational level-`ℓ` theta structure (`ℓ`-torsion available or via a
small extension for the embedding only). Excluded: specials as A1.

### Full algorithmic path
1. **Factor base:** theta-coordinate representatives of `B=L` base points at level `ℓ`.
2. **Relation gen:** encode `A+C=R` as the bilinear Riemann relations; solve the bilinear chain
   (linear-algebra-heavy, low degree) for factor-base decompositions.
3. **Witness/verify:** map back to affine `E`; verify `A+C=R`.
4. **Relation probability:** `Θ(B)` supply if the bilinear chain has solutions.
5. **Matrix:** sparse factor-log matrix, target full-rank `≥B−1`.
6–9: standard; theta setup per curve offline; parallel.

### Cost model
Semaev membership: solving degree governed by first-fall/Dreg (B-Dreg conserved). B3: if the bilinear
chain has first-fall degree `d_B ≪ d_{Semaev}`, the solve cost drops from `q^{Θ(d_{Semaev})}` toward
`q^{Θ(d_B)}`. Promotion iff **measured** exploitable degree `d_B` gives relation-gen exponent `<1/2`.
Compare rho `n^{0.5}`, Semaev/Gröbner baseline.

### Why existing negative results do not kill it
Not scalar level-2 Kummer (≠ NR-022: uses Heisenberg + bilinearity), not isogeny theta (≠ M5). New
operation: **level-≥3 Riemann bilinear relations as a low-degree membership predicate.**

### Likely fatal obstruction
B-Dreg: theta coordinates are a **change of variables**; the bilinear chain, when eliminated to the
decomposition variables, likely reconstructs the same Semaev first-fall degree (Dreg conservation),
so `d_B=d_{Semaev}` and there is no gain — theta bilinearity is bookkeeping, not a real degree drop.

### Minimal falsifying experiment
`p≈2^16,2^20,2^24`; build level-`ℓ` (`ℓ=3,4`) theta systems for `m=4` decomposition; measure the
**first-fall degree** of the bilinear chain vs the standard `S_4` first-fall degree. Positive
control: symmetrized `S_m` with small torsion (known degree drop). Negative control: level-2 scalar
Kummer (should match Semaev). Fit degree vs `log q`.

### Quantitative promotion gate
Measured first-fall degree `d_B` strictly below Semaev's across three sizes **and** yielding
relation-gen exponent `<1/2` with sparse full-rank — a genuine Dreg violation via theta bilinearity.

### Proof track
Theorem: the level-`ℓ` bilinear membership chain for `E/F_p` has first-fall degree `< d_{Semaev}`.
Would refine/contradict the Dreg-conservation proof for non-scalar theta charts.

### Disproof track
`d_B = d_{Semaev}` at all sizes ⇒ reusable negative extending B-Dreg to level-≥3 theta charts:
"non-scalar theta bilinearity is Dreg-preserving," closing the theta-degree lane.

### Reproduction artifact
- contract: `research/experiment_contract_b2b3_theta_bilinear_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2b3_theta_bilinear_membership.sage`
- result/audit: `.../b2b3_result.json`, `.../b2b3_verify.sage`
- ledger id: `THETA-BILIN-B3`

### Group C — high-risk speculative mechanisms

---

## Candidate: C1 — Non-generic representation-technique MITM (coordinate-smoothness redundancy)

### One-sentence mechanism
Import the **subset-sum representation technique (HGJ/BCJ)** — represent the target scalar in a
**redundant factor-base-log basis** so it has exponentially many decompositions — and combine it
with **non-generic coordinate smoothness** (which factor-base points a random combination lands near)
to attempt a meet-in-the-middle below `n^{1/2}` that escapes the generic bound.

### Status
CONJECTURE

### Novelty classification
**LITERATURE-ADJACENT — already a published three-paper line (folded in).** LEDGER-NEW (representation
technique absent from the ledger), **but** Delaplace–May (2019/2020) and Delaplace–Fouque–Kirchner–May
apply the representation technique to ECDLP over `F_{p^ℓ}` (`ℓ≥2`), obtaining unconditional `O(p)` and
`p^{4/5}`-with-precomputation — **explicitly falling short of rho / Bernstein–Lange.** Crucially, that
line is **non-generic** (it exploits point coordinates / Semaev structure), so it is *consistent with*
Shoup, not a violation. The **only open sub-case** is `ℓ=1` (pure prime field, no precomputation) with
a **faster zero-testing / evaluation routine** — flagged as open by those authors — which is exactly
this candidate's narrowed target.

### Semantic fingerprint
- object: target `k∈Z/n` in a redundant generating system `{g_i}` (factor-base logs).
- ops: EC arithmetic + a non-generic membership/near-test on coordinates.
- hidden structure: many representations `k=Σ a_i g_i` + coordinate proximity of partial sums.
- discarded: the unique-representation constraint of plain MITM.
- retained: the ambiguity (representation count) as a collision multiplier.
- relation primitive: partial-sum collision under a coordinate near-predicate.
- compression primitive: representation-count amplification of collisions.
- rank mechanism: n/a (direct collision, not linear algebra).
- descent: direct (this *is* the descent).
- dominant cost exponent: representation-vs-search tradeoff exponent — object of measurement.

### Nearest ledger entries
1. **BSGS / M-baseline** — plain MITM at `n^{1/2}`; C1 adds representation ambiguity. *Distinction:
   redundant-representation collision multiplier, not straight MITM.*
2. **M1 IC** — IC uses coordinate smoothness for relations; C1 uses it as a **collision near-test**
   inside a representation MITM. *Distinction: MITM-with-representations vs relation matrix.*
3. **Batch-1 C3 (xedni)** — both are "beat MITM/rho by structure"; C3 lifts to char 0, C1 stays in
   `F_p` with representation ambiguity. *Distinction: representation combinatorics vs global lift.*
4. **B-preproc** — any precomputed representation tables must beat `S·T²=Ω̃(εq)`.
5. **Shoup generic bound (→ D1)** — the central threat: if C1 uses only group ops it is generic and
   `Ω(√n)`. *Distinction: C1's bet is the **non-generic coordinate near-test** breaks genericity.*

### Nearest literature
Howgrave-Graham–Joux 2010; Becker–Coron–Joux 2011 (subset-sum representations, `2^{0.291n}`);
**Delaplace–May 2019/2020 (*J. Math. Cryptology* / eprint 2019/800 — representation-technique ECDLP
over `F_{p^2}`, `p^{1.314}`) and Delaplace–Fouque–Kirchner–May (unconditional `O(p)`, `p^{4/5}` with
`p^{6/5}` precomputation, generalized to `F_{p^ℓ}` giving `p^{2ℓ/(2ℓ+1)}` after `p^{(ℓ+1)/(2ℓ+1)}`
precomputation) — the sharpest threat: this exact mechanism is tried, tuned, and admits falling short
of Bernstein–Lange**; Shoup 1997 (generic bound — does *not* bind this non-generic line); Bernstein–
Lange 2013 (precomputation baseline). Gap (author-stated, open): whether a faster zero-testing routine
pushes the **unconditional `ℓ=1` (single prime field)** exponent below `1/2` in `p` — untested.

### Target family
Ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Setup:** choose a redundant generating set `{g_i}` (factor-base points) with `|{g_i}|=r>log n`.
2. **Representation MITM:** enumerate partial sums `Σ_{i∈S} a_i g_i` for structured `S`; store by a
   **coordinate near-key** (e.g. high bits of `x`); match halves under the representation constraint.
3. **Witness/verify:** a matched pair yields `k`; verify `kB=Q`.
4–6. relation/matrix: n/a (collision-based).
7. **Descent:** the match *is* the answer.
8. **Offline/online:** representation tables (`{g_i}` multiples) offline; matching online.
9. **Memory/parallel:** memory = table size (the risk); distinguished-point variant to bound it.

### Cost model
Plain MITM `n^{1/2}` time+memory. BCJ-style representation gives `2^{cn}` with `c<1/2` **only when a
modular constraint supplies many representations that cancel** — DLP has a *unique* `k mod n` and no
such cancellation, so the generic version stays `n^{1/2}` (D1). The bet: the coordinate near-key
supplies a *non-generic* filtration lowering the exponent. Compare rho/BSGS `n^{0.5}`, memory `n^{0.5}`.

### Why existing negative results do not kill it
Not a relation-matrix IC (≠ M1), not a char-0 lift (≠ C3). New operation: **redundant-representation
collision amplification under a coordinate near-predicate.**

### Likely fatal obstruction (= D1)
**Not genericity — the published line is already non-generic and still loses.** Delaplace–Fouque–
Kirchner–May tuned exactly this coordinate-exploiting representation MITM and reached only `O(p)`
(matching, not beating rho) for `ℓ≥2`, with `ℓ=1` never shown sub-`√p`. The zero-testing/multipoint
subroutine is the binding cost; a genuinely faster one is unknown and may not exist. The generic
*core* is still Shoup-bounded (D1), so any win must come entirely from the non-generic evaluation
routine — precisely the ingredient that has resisted three papers.

### Minimal falsifying experiment
`p≈2^20,2^24,2^28`; implement a representation MITM with a coordinate near-key; measure the
**time-memory product exponent** vs `n`. Positive control: a **modular-constrained** synthetic
subset-sum instance where BCJ provably beats MITM. Negative control: plain BSGS. Fit exponent.

### Quantitative promotion gate
Measured time-memory-product exponent `<1` (i.e. genuinely below the `n^{1/2}·n^{1/2}` MITM
frontier) across three sizes, via the coordinate near-test — a measured escape from genericity.

### Proof track
Theorem: the coordinate near-predicate is a non-generic oracle enabling a sub-`√n` representation
MITM. (Almost certainly false; the value is the precise refutation.)

### Disproof track (= D1)
Show the near-test provides no non-generic advantage ⇒ Shoup applies ⇒ `Ω(√n)`; reusable barrier.

### Reproduction artifact
- contract: `research/experiment_contract_b2c1_representation_mitm_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2c1_representation_mitm.sage`
- result/audit: `.../b2c1_result.json`, `.../b2c1_verify.sage`
- ledger id: `REPMITM-C1`

---

## Candidate: C2 — p-curvature / arithmetic-holonomy per-target descent

### One-sentence mechanism
Test whether the **p-curvature of the Gauss–Manin connection** (or an arithmetic-holonomy / D-module
invariant attached to a family through `E` and a target `Q`) carries **per-target discrete-log
information**, giving a descent that is not a class-function of Frobenius.

### Status
CONJECTURE (high-risk; borderline INCOMPLETE — see path)

### Novelty classification
LEDGER-NEW (p-curvature / crystalline absent; Cartier–Manin used only for *anchor-invariant* isotypic
certification); POSSIBLY NOVEL as an ECDLP mechanism, but with a strong suspected barrier (D2).

### Semantic fingerprint
- object: Gauss–Manin connection on an `E`-family; its p-curvature `ψ_p`; Cartier–Manin matrix.
- ops: differential-operator computation on the family; Frobenius action on de Rham cohomology.
- hidden structure: whether `ψ_p` depends on the *target point* `Q`, not just the curve.
- discarded: group-law composition.
- retained: (speculative) target-dependent holonomy invariant.
- relation primitive: (speculative) a p-curvature identity encoding `log_B Q`.
- compression primitive: differential-operator evaluation (if target-dependent).
- rank mechanism: undefined until a target-dependent invariant is exhibited.
- descent: (speculative) inversion of the holonomy invariant.
- dominant cost exponent: undefined until formalized.

### Nearest ledger entries
1. **TRANSFER-NR-011/015/016 (Cartier–Manin certification)** — the ledger's Cartier–Manin eigenvalues
   are **anchor-invariant** (`-11` at both anchors `24,598`), i.e. class-functions of Frobenius.
   *Distinction: C2 asks whether p-curvature can be made **target-dependent** — the exact quantity
   the ledger's use is not.*
2. **M5 Frobenius/self-pairing** — order/isogeny data from Frobenius spectrum. *Distinction: C2 seeks
   per-target, not order.*
3. **Batch-1 C2 (Lattès transfer operator)** — both are "spectral, likely order-only"; the operators
   differ (Perron–Frobenius of `x∘[ℓ]` vs p-curvature of Gauss–Manin). *Distinction: dynamical
   transfer operator vs arithmetic D-module.*
4. **B-preproc** — any family precomputation must beat the generic frontier.
5. **ECFG-001 (direct graph inversion negative)** — C2 must avoid re-deriving an order-only invariant.

### Nearest literature
Katz 1970 (nilpotent connections / p-curvature); Hasse 1934, Manin 1961 (Hasse–Witt / Cartier–Manin
matrix); **Achter–Casalaina-Martin–Vakil, "Hasse–Witt and Cartier–Manin matrices: a warning and a
request" (sharpest threat: for `g=1` the Hasse–Witt matrix is `1×1` — a single scalar, the Hasse
invariant — a curve-level invariant of `H^1_dR(E)`/Frobenius with no point-dependence by
construction)**; Lauder (p-adic point counting). Gap: no cryptanalytic construction extracts a
**per-target discrete log** from p-curvature; all known uses give order/supersingularity. Only a
Gauss–Manin *deformation-family* invariant (evaluated as a function of the family parameter coupling
`Q`) is unexplored — and no reduction from "p-curvature vanishes" to "reveals `k`" is known.

### Target family
Ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path (borderline INCOMPLETE — flagged)
1. Build a one-parameter family through `E` (and, crucially, a construction coupling the target `Q`).
2. Compute the Gauss–Manin connection and its p-curvature `ψ_p`; compute Cartier–Manin.
3. **Stage 3–9 conditional:** *only if* `ψ_p` (or a derived invariant) is shown target-dependent do
   witness extraction, relation shape, and descent become definable. **If it is a class-function of
   Frobenius (expected), the candidate is INCOMPLETE and closes to D2.**

### Cost model
Undefined until a target-dependent invariant exists. Cannot yet compare to rho — a rejection risk
shared with Batch-1 C2. The value is a **decisive barrier** (D2) if the invariant is order-only.

### Why existing negative results do not kill it
Orthogonal to all measured lanes — but that is because no target-coupling construction is yet
specified. New operation (if it exists): **target-dependent arithmetic-holonomy invariant.**

### Likely fatal obstruction (= D2)
p-curvature and Cartier–Manin are invariants of the **curve/family**, determined by Frobenius; they
are **class-functions of the characteristic polynomial** (order data), as the ledger's own
anchor-invariant eigenvalues show. No per-target log is expected.

### Minimal falsifying experiment
Theory-first: attempt to construct a family/D-module whose p-curvature at `E` **depends on `Q`**.
Empirically at `p≈2^12,2^16`: compute `ψ_p` for many targets on one curve; measure whether any
functional of `ψ_p` correlates with `log_B Q`. Positive control: anomalous curve (where formal-log
leakage is known). Negative control: random ordinary curve (expected no correlation).

### Quantitative promotion gate
A functional of `ψ_p` recovers `>ε·log_2 n` target bits for non-anomalous curves across sizes — else
rejected/closed to D2. Not eligible for promotion without a complete relation/descent path.

### Proof track (mainly D2)
Theorem: every p-curvature/Cartier–Manin invariant of an ordinary `E/F_p` is a class-function of
Frobenius ⇒ carries order, not per-target log.

### Disproof track
Exhibit a target-dependent holonomy invariant (would be a major result and open a new lane).

### Reproduction artifact
- note: `research/b2c2_p_curvature_formalization_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2c2_p_curvature_probe.sage`
- ledger id: `PCURV-C2`

---

## Candidate: C3 — Elliptic character-sum bias relation oracle

### One-sentence mechanism
Exploit a hypothesized **failure of square-root (Weil/Deligne) equidistribution** — a bias in a
curve-attached exponential/character sum counting decompositions `R=A+C` (`A,C` in the base) — as a
**cheap batch oracle** that flags `R` with anomalously many factor-base decompositions, harvesting
relations faster than birthday search.

### Status
CONJECTURE

### Novelty classification
LEDGER-NEW (sum-product / Bourgain–Gamburd / character-sum-bias absent; "sumset" only as an object);
POSSIBLY NOVEL as a relation oracle, with a strong suspected equidistribution barrier.

### Semantic fingerprint
- object: the decomposition-count function `N(R)=#{(A,C)∈F×F : A+C=R}` and its character-sum transform.
- ops: EC arithmetic; additive/multiplicative character evaluation on `x`-coordinates.
- hidden structure: bias/concentration of `N(R)` beyond the `B²/n ± O(√·)` Weil main term.
- discarded: per-pair enumeration.
- retained: the biased `R`-set (high-`N` shifts).
- relation primitive: `A+C=R` at biased `R` (many decompositions ⇒ cheap relations).
- compression primitive: character-sum (spectral) detection of the bias set.
- rank mechanism: standard sparse factor-log matrix.
- descent: standard.
- dominant cost exponent: bias magnitude / detection cost — object of measurement.

### Nearest ledger entries
1. **Batch-1 A3 (incidence reporting)** — A3 *lists* incident pairs; C3 seeks a **statistical bias**
   in the *count*. *Distinction: equidistribution failure vs output-sensitive reporting.*
2. **ECFG-NR-1408 ("do not compress the tested EC sumsets")** — the ledger found EC sumsets
   *hash-like* (no compression) after flattening; C3 asks whether a **character-sum bias** survives
   that the flattening test misses. *Distinction: spectral bias vs image compression.*
3. **P1447 sum-product/incidence barrier (Ahmadi–Shparlinski)** — the ledger fears the
   `|x(F)+x(F)|·|x(F+F)|` energy bound; C3 directly tests whether energy concentration exists.
   *Distinction: C3 measures the energy/bias as a relation source, not just a barrier.*
4. **M2 large-prime graph** — both harvest "lucky" `R`; C3 selects them by spectral bias, not LP
   cycles. *Distinction: character-sum selection vs graph cycles.*
5. **Batch-1 A2 (EDS)** — both seek a smoothness surrogate; C3 uses count-bias, not net values.

### Nearest literature
Weil / Deligne (Riemann-hypothesis bounds → square-root equidistribution); Bourgain–Gamburd
(spectral gap / expansion); Ahmadi–Shparlinski (EC sum-product / additive energy); Sárközy
(sum-set additive energy). Gap: no measurement of decomposition-count bias for EC factor bases as a
*relation oracle*; equidistribution predicts **no** exploitable bias (the suspected barrier).

### Target family
Ordinary prime-order `E/F_p`; excluded specials as A1 (specials could induce spurious bias).

### Full algorithmic path
1. **Factor base** `B=L`; define `N(R)=#{A+C=R}` and its character transform `Ñ(χ)`.
2. **Relation gen:** compute `Ñ(χ)` in batch (FFT-like over the group/character set); identify `R`
   with `N(R) ≫ B²/n` (bias); harvest their decompositions.
3. **Witness/verify:** replay `A+C=R` at biased `R`.
4. **Relation probability:** amplified at biased `R` — measured bias magnitude.
5. **Matrix:** sparse full-rank target.
6–9: standard; character-transform is offline per curve; parallel/FFT.

### Cost model
Main term `N(R)=B²/n` uniform; Weil bound gives fluctuation `O(√· )`. If a **structured bias**
`N(R)≥B²/n·(1+Δ)` exists on a `poly`-detectable `R`-set with `Δ` non-vanishing, relations at those
`R` cost `≈1/Δ` less. Detection via character sums is `Õ(n)` offline (too much) unless the bias is
low-frequency (few characters), giving `Õ(B·something)` — the crux. Compare rho `n^{0.5}`.

### Why existing negative results do not kill it
Not incidence *reporting* (≠ Batch-1 A3), not sumset *image compression* (≠ NR-1408). New operation:
**spectral (character-sum) detection of decomposition-count bias.**

### Likely fatal obstruction
Deligne/Weil equidistribution: for a random ordinary curve the decomposition count is
square-root-equidistributed, so `Δ=O(n^{-1/2}·something)` → **no exploitable bias** (this is exactly
the Ahmadi–Shparlinski energy barrier the ledger already respects). Any bias would be a special-curve
artifact.

### Minimal falsifying experiment
`p≈2^16,2^20,2^24`; compute the empirical distribution of `N(R)` and its top character coefficients
vs the equidistribution null. Positive control: a curve with planted additive structure (small
torsion / CM) — should show low-frequency bias. Negative control: random ordinary curve — should
match equidistribution. Fit bias magnitude and detection cost vs `L`.

### Quantitative promotion gate
A `poly`-detectable, non-vanishing bias `Δ` (few low-frequency characters) yielding relation-gen
exponent `<1/2` across three sizes — a measured violation of square-root equidistribution for a
generic ordinary curve.

### Proof track
Theorem: for structured `E`, `N(R)` has a low-frequency character-sum bias `Δ=Ω(L^{-c})`,
`c<...`, detectable in `o(n)`. (Expected false for generic curves by Deligne.)

### Disproof track
`N(R)` matches square-root equidistribution ⇒ reusable negative sharpening P1447/Ahmadi–Shparlinski:
"EC decomposition counts have no exploitable low-frequency bias," closing the spectral-bias lane.

### Reproduction artifact
- contract: `research/experiment_contract_b2c3_character_bias_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2c3_decomposition_count_bias.sage`
- result/audit: `.../b2c3_result.json`, `.../b2c3_verify.sage`
- ledger id: `CHARBIAS-C3`

### Group D — negative-theory candidates (expose a loophole or barrier)

---

## Candidate: D1 — Generic-model barrier for representation-technique MITM (↔C1)

### One-sentence mechanism
Prove that the representation-technique MITM's **generic core** is Shoup-`Ω(√n)`-bounded and that its
**non-generic evaluation subroutine** (the only escape) faces the same zero-testing cost that pinned
the published Delaplace–May line to `O(p)` for `ℓ≥2` — characterizing exactly what a faster `ℓ=1`
zero-testing routine would have to achieve to cross `1/2`.

### Status
HYPOTHESIS (provable-looking from Shoup + a genericity reduction)

### Novelty classification
LEDGER-NEW (no Shoup/generic-representation analysis in the ledger); the theorem + the exact
non-generic escape condition is new.

### Semantic fingerprint
object: representation-MITM as a straight-line program in group ops + a coordinate predicate;
structure: generic vs non-generic; retained: the escape condition (what the predicate must reveal);
rank mechanism: n/a; cost exponent: n/a (a barrier).

### Nearest ledger entries
Shoup bound (baseline barrier, cited in `non_generic_transfer_search`), C1 (its partner), BSGS
baseline, B-preproc frontier. Distinction: a **representation-specific** genericity theorem + escape
condition, absent from the ledger.

### Nearest literature
Shoup 1997 / Nechaev 1994 (generic `Ω(√n)`); Becker–Coron–Joux 2011 (representation technique);
Delaplace–May 2019/2020 and Delaplace–Fouque–Kirchner–May (ECDLP representation MITM, `O(p)` for
`ℓ≥2`, `ℓ=1` open); Bernstein–Lange 2013 (precomputation baseline). Gap: no statement isolating the
generic core (Shoup-bound) from the non-generic zero-testing subroutine, nor the exact `ℓ=1` routine
cost that would cross `1/2`.

### Target family
All ordinary prime-order `E/F_p`.

### Full algorithmic path (theory)
(1) Model the representation MITM as a generic straight-line program plus calls to a coordinate
predicate `Π`. (2) If `Π` is simulatable from the group encoding, the algorithm is generic ⇒ Shoup
`Ω(√n)`. (3) When `Π` is a genuine non-generic coordinate/Semaev oracle (as in Delaplace–May), Shoup
does not bind; instead the cost is set by the zero-testing/multipoint subroutine. (4) Reduce that
subroutine's `ℓ=1` cost to a known algebraic-complexity quantity and show it stays `≥p^{1/2}` unless
a specific (unknown) evaluation speedup exists — i.e., C1's only door is the same one the published
`ℓ≥2` line could not open, now at `ℓ=1`.

### Cost model
n/a (barrier). Consequence: C1's upside requires a non-generic oracle at least as strong as the IC
membership backend RT-1476 already seeks.

### Why existing negative results do not kill it
New theorem tying representation-MITM to Shoup and to RT-1476.

### Likely fatal obstruction
The coordinate near-test *might* be a weak non-generic oracle that still helps by a constant — the
theorem must separate "no exponent gain" from "no help at all."

### Minimal falsifying experiment
Toy `p≈2^16,2^20,2^24`: measure the time-memory product of a representation MITM with the coordinate
predicate vs plain BSGS; the theorem predicts **no exponent improvement**. An exponent drop falsifies
it (and vindicates C1).

### Quantitative promotion gate
Theorem proved + toy exponent-equality confirmed at three sizes ⇒ closes C1's generic core; an
exponent drop ⇒ promotes C1.

### Proof track
Shoup reduction + simulatability of the coordinate predicate.

### Disproof track
A coordinate predicate that provably lowers the MITM exponent.

### Reproduction artifact
- proof note: `research/b2d1_representation_generic_barrier_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2d1_mitm_exponent_check.sage`
- ledger id: `GEN-BAR-D1`

---

## Candidate: D2 — Crystalline / Cartier–Manin order-only barrier (↔B2, C2)

### One-sentence mechanism
Prove that every **crystalline / p-curvature / Cartier–Manin / canonical-lift spectral invariant** of
an ordinary `E/F_p` is a **class-function of the Frobenius characteristic polynomial** — hence carries
**order/isogeny-class information only, never a per-target discrete log** — bounding B2 and C2.

### Status
HYPOTHESIS (strongly supported; the ledger's Cartier–Manin eigenvalues are already anchor-invariant)

### Novelty classification
LEDGER-NEW as a *stated barrier* (the ledger uses Cartier–Manin operationally but never proves the
order-only bound); unifies the expected failure of B2 and C2.

### Semantic fingerprint
object: crystalline/p-adic-Hodge invariants of `E/F_p` (Frobenius, unit-root, Serre–Tate, p-curvature,
Cartier–Manin); structure: dependence on Frobenius char poly only; retained: the class-function
criterion; rank mechanism: n/a; cost exponent: n/a (barrier).

### Nearest ledger entries
TRANSFER-NR-011/015/016 (anchor-invariant Cartier–Manin eigenvalues `-11`), M5 Frobenius/self-pairing
(order data), B2 (canonical lift), C2 (p-curvature). Distinction: a **general theorem** that all such
invariants are order-only, subsuming the empirical anchor-invariance the ledger observed.

### Nearest literature
Katz 1970 (crystalline / p-curvature); Hasse 1934, Manin 1961 (Hasse–Witt — for `g=1` a `1×1`
scalar); **Achter–Casalaina-Martin–Vakil ("a warning and a request" — these matrices are invariants
of `H^1_dR`/Frobenius, not of any point/scalar)**; Serre–Tate 1968 (canonical lift); Voloch
(Smart/Satoh–Araki/Semaev unification, trace-1 exception). Gap: no crisp "order-only" statement
separating the anomalous exception from the general ordinary case, though the `g=1` naive form is
near-definitionally settled.

### Target family
Ordinary prime-order `E/F_p`, `trace≠1`; the anomalous `#E=p` case is the **explicit exception**.

### Full algorithmic path (theory)
(1) Show the listed invariants factor through the isogeny class (Frobenius char poly). (2) Show the
`[k]`-action on any associated `p`-adic/crystalline structure restricted to the prime-order-`n`
subgroup (`n≠p`) reduces to the abstract DLP with no additive shortcut. (3) Isolate the anomalous
exception (`n=p`) where the formal-group log linearizes. (4) Conclude B2/C2 recover 0 non-anomalous
target bits. Verify by the toy bit-recovery experiments of B2/C2.

### Cost model
n/a (barrier). Consequence: closes the entire canonical-lift / crystalline-spectral lane for
non-anomalous curves, and precisely bounds where formal-log attacks live.

### Why existing negative results do not kill it
New unifying theorem; upgrades the ledger's empirical anchor-invariance to a proof.

### Likely fatal obstruction
A cleverly *target-coupled* family (as C2 hopes) might evade the "curve-only" premise; the theorem
must show any such coupling still factors through order — or find the exception.

### Minimal falsifying experiment
The B2 and C2 bit-recovery experiments: measure recovered target bits for non-anomalous curves
(predicted 0) and anomalous curves (predicted full). Any non-anomalous recovery falsifies D2.

### Quantitative promotion gate
Theorem proved + toy zero-recovery for non-anomalous curves at three sizes ⇒ closes B2/C2; any
non-anomalous leakage ⇒ promotes B2/C2.

### Proof track
Class-function/isogeny-invariance argument + formal-group restriction to the `n≠p` subgroup.

### Disproof track
A target-dependent crystalline invariant with non-anomalous leakage.

### Reproduction artifact
- proof note: `research/b2d2_crystalline_order_only_barrier_20260717.md`
- impl: `experiments/ecdlp_prime_field/b2d2_bit_recovery_check.sage`
- ledger id: `CRYST-BAR-D2`

---

## Candidate: D3 — Gaudry fixed-genus-over-F_p IC-cost barrier delimiting the RM escape (↔B1)

### One-sentence mechanism
Prove/measure that **index calculus in a fixed-genus-`g` Jacobian natively over the prime field
`F_p`** (no proper subfield) costs `Ω̃(q^{2−2/g}) ≥ q^{1/2}` for `g≥2`, so the **only** escape for the
Kani-glued surface (B1) is a **real-multiplication eigen-split** — and characterize exactly how much
RM would have to lower the relation dimension to cross `1/2`.

### Status
HYPOTHESIS (Gaudry/Diem complexity is known; the RM-escape boundary is the new content)

### Novelty classification
LEDGER-NEW as a *stated barrier with the RM escape condition* (Gaudry cited once; genus-2 IC cost and
the RM boundary never written down here); delimits B1.

### Semantic fingerprint
object: genus-`g` Jacobian `Jac(H)/F_p` (from B1's Kani glue) and its IC relation cost; structure:
base-field-`F_p` (n=1) obstruction + RM eigen-split; retained: the exponent `2−2/g` and the RM
reduction factor; rank mechanism: n/a; cost exponent: `2−2/g` (the barrier), RM-reduced (the escape).

### Nearest ledger entries
B-n=1 collapse (Gaudry/Diem), NR-022 (scalar Weil restriction), B1 (its partner),
`non_generic_transfer_search` (transfer must beat `√n`). Distinction: an **explicit exponent bound +
RM escape condition** for the Kani-glued surface, absent from the ledger.

### Nearest literature
Gaudry 2009 (abelian-surface/genus-2 IC, `Õ(q^{2−2/g})`); Diem (IC in Jacobians / when it beats
generic); Gaudry–Schost (RM in genus-2). Gap: no statement of how much RM must reduce the effective
relation dimension of a **prime-field** genus-2 Jacobian to beat rho.

### Target family
Genus-2 Jacobians over `F_p` arising from B1's Kani glue, with/without RM.

### Full algorithmic path (theory + measurement)
(1) State Gaudry's `Õ(q^{2−2/g})` relation cost for `Jac(H)/F_p`; for `g=2` this is `Õ(q)`. (2) Show
that over `F_p` (no proper subfield) there is no Weil-restriction descent to lower the base, so the
`n=1` obstruction applies. (3) Formalize the RM eigen-split: RM by `O_{√d}` could reduce the relation
search to two lower-dimensional problems; compute the exponent that split must achieve (`<1/2` on the
`E`-block). (4) Measure whether RM delivers an **exponent** reduction (expected: only a **constant**).

### Cost model
n/a (barrier), but decides B1: non-RM `q`, RM-reduced `q^{1−δ_{RM}}`; B1 wins only if `δ_{RM}>1/2`,
i.e. RM more than halves the exponent — far beyond the known constant-factor RM speedups.

### Why existing negative results do not kill it
New explicit-exponent barrier + escape condition, subsuming B-n=1 for the Kani-glue construction.

### Likely fatal obstruction
Proving RM gives no exponent gain (only constant) may require the full genus-2 IC analysis; the
fallback is the direct measurement (which B1 runs), so D3's marginal value is the **proof + the exact
`δ_{RM}>1/2` boundary**.

### Minimal falsifying experiment
Numerically fit the genus-2 IC relation exponent over `F_p` with and without RM at `p≈2^12,2^16,2^20`;
the barrier predicts `≈q^{1}` non-RM and `≈q^{1−o(1)}` (constant-only) with RM. An RM exponent
`<q^{1/2}` falsifies D3 and promotes B1.

### Quantitative promotion gate
Proved/measured RM exponent reduction `δ_{RM}≤1/2` (closes B1) **or** measured `δ_{RM}>1/2` (opens
B1) at three sizes.

### Proof track
Gaudry relation-count + RM eigen-projection dimension analysis.

### Disproof track
An RM genus-2 Jacobian over `F_p` with measured IC exponent `<1/2` (opens B1 — would be major).

### Reproduction artifact
- proof note: `research/b2d3_gaudry_genus_barrier_20260717.md`
- impl: `experiments/ecdlp_isogeny/b2d3_genus2_rm_exponent.sage`
- ledger id: `GAUDRY-BAR-D3`

---

## 3. Ranking

Scores 0–5: **N** distance from prior ledger *and Batch-1* mechanisms; **V** plausibility of an exact
verifier; **X** chance of changing an *exponent* (not a constant); **P** complete-path coverage;
**F** falsifiability at toy scale; **L** literature-novelty confidence; **R⁻** *low* hidden
preprocessing/memory risk (5 = low). Reject if N<3, no complete route to target descent, no
quantitative rho comparison, or no precise distinction from the closest ledger entry.

Scores below are **post-literature-reconciliation** (the Literature Agent's findings moved several
`L` and `X` scores). **N = distance from prior *ledger* mechanisms** (separate from the literature
verdict `L`).

| Cand | N | V | X | P | F | L | R⁻ | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A1** 3-LP homology | 4 | 5 | 3 | 5 | 5 | 3 | 4 | **29** | **KEEP — conservative winner** (uniquely attacks the *other* open theorem RT-1472) |
| A2 two-sided coincidence | 4 | 4 | 3 | 4 | 4 | 4 | 3 | 26 | keep (construction-blocked) |
| A3 transposed-KU membership | 3 | 5 | 3 | 5 | 4 | 4 | 3 | 27 | keep (POSSIBLY NOVEL; reduction gap) |
| **B1** Kani-RM genus-2 | 5 | 4 | 4 | 4 | 3 | 4 | 2 | **26** | **KEEP — representation winner** |
| B2 Serre–Tate lift | 4 | 4 | 2 | 4 | 4 | 2 | 4 | 24 | keep (settled-negative naive form; paired D2) |
| B3 theta-bilinear | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 24 | keep (paired B-Dreg) |
| C1 representation-MITM | 4 | 4 | 3 | 4 | 4 | 2 | 2 | 23 | keep — **demoted** (published Delaplace–May line, already-mined) |
| C2 p-curvature | 4 | 2 | 2 | 2 | 3 | 2 | 3 | 18 | **REJECT — INCOMPLETE** (no target-coupling) + settled-negative `g=1`; D2 seed |
| **C3** character-bias | 4 | 4 | 3 | 4 | 4 | 4 | 3 | **26** | **KEEP — high-risk winner** (POSSIBLY NOVEL; paired equidistribution barrier) |
| D1 generic/subroutine barrier | 5 | 5 | — | 5 | 5 | 4 | 5 | (barrier) | KEEP |
| D2 crystalline barrier | 5 | 5 | — | 5 | 5 | 5 | 5 | (barrier) | KEEP |
| D3 Gaudry/RM barrier | 4 | 5 | — | 5 | 4 | 4 | 5 | (barrier) | KEEP |

**Rejected:** C2 (no target-coupling construction ⇒ INCOMPLETE; `g=1` Hasse–Witt is a `1×1` scalar,
near-definitionally order-only; retained only as a Theory-Agent seed feeding D2). All others pass
N≥3 with a complete descent route and a quantitative rho comparison.

**Literature-driven winner change:** C1 was the provisional high-risk pick, but the Literature Agent
found a **published three-paper trajectory** (Delaplace–May 2019/2020; Delaplace–Fouque–Kirchner–May)
applying the representation technique to ECDLP and *explicitly falling short of rho* — demoting C1 to
`L=2` (already-mined). **C3** (character-sum bias, POSSIBLY NOVEL, no equivalent found) is the honest
high-risk winner.

**Winners:**
1. **Conservative — A1** (3-LP hypergraph homology enrichment): uniquely attacks **RT-1472**, the
   open theorem the entire Batch-1 set ignored. *Honest prior: likely constant-factor (Cavallar),
   but the measurement on the under-attacked theorem is the value.*
2. **Representation — B1** (Kani-RM genus-2 Jacobian IC): highest novelty (N=5); a genuine
   non-x-line relation engine; paired with the decisive D3 barrier.
3. **High-risk — C3** (elliptic character-sum bias relation oracle): POSSIBLY NOVEL after a
   documented search; paired with the Deligne-equidistribution barrier.

All three (i) are outside the dominant ledger *and* Batch-1 vocabulary, (ii) have an exact toy
verifier, (iii) come with a paired disproof/barrier (A1↔RT-1472 δ-boundary; B1↔D3 RM-escape;
C3↔Deligne equidistribution), and (iv) target a *measured exponent that could cross 1/2*, not
correctness.

---

## 4. Winner experiment contracts + first executable command

### Experiment Contract: A1 — three-large-prime hypergraph homology enrichment

- **Hypothesis:** the EC-addition-induced 3-uniform large-prime complex has `H_1` enrichment
  `δ_3>1/4`, pushing the RT-1472 exponent below `1/2`.
- **Null:** `δ_3≤1/4` (matches the Linial–Meshulam random-complex / matched-hypergraph null).
- **Parameters:** six ordinary prime-order `E/F_p`, `q≈L^5`, `L∈{16,32,64}` train / `{128,256}`
  holdout; seeds `20260717..20260722`.
- **Metrics:** `dim H_1(Δ)`, enrichment `δ_3`, vs 2-LP `δ_2` and a matched random 3-uniform null;
  usable relations after large-prime elimination; sparse rank; group/field ops; memory.
- **Positive control:** planted low-arity structured deck (`δ_3>δ_2`).
- **Negative control:** uniform-random x-deck (`δ_3≈δ_2^{random}`).
- **Success:** `δ_3>1/4` growing with `L`, surviving holdout, sparse rank `t≥B−1`.
- **Falsification:** `δ_3≤1/4` at every size.
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/b2a1_klp_homology_enrichment.sage \
    --sizes 16,32,64 --holdout 128,256 --arity 3 --seeds 20260717-20260722 \
    --out experiments/ecdlp_prime_field/b2a1_klp_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/b2a1_klp_homology_enrichment.sage \
    --sizes 16 --arity 3 --seeds 20260717 --stage h1_delta_vs_null \
    --out experiments/ecdlp_prime_field/b2a1_smallest_probe.json
  ```

### Experiment Contract: B1 — Kani-RM genus-2 Jacobian index calculus

- **Hypothesis:** an RM Kani-glued genus-2 Jacobian over `F_p` has `E`-block relation-generation
  exponent `<1/2` in `q` (RM eigen-split beats the `q^{2−2/g}=q` Gaudry null).
- **Null:** RM gives only a constant-factor speedup ⇒ exponent `≈q` (D3).
- **Parameters:** toy `p≈2^12,2^16,2^20`; auxiliary `E'` and `N` chosen so the glue is a smooth
  RM genus-2 Jacobian; seeds `20260717..`.
- **Metrics:** `E`-block relation exponent with vs without RM eigen-projection; relation yield;
  sparse rank on the `E`-isotypic block; blind `E`-target descent; group ops; memory.
- **Positive control:** a large-RM genus-2 curve (known faster arithmetic).
- **Negative control:** a non-RM (generic) genus-2 Jacobian (exponent `≈1`, Gaudry).
- **Success:** RM exponent `<1/2` across three sizes, strictly below the non-RM null, with
  end-to-end blind `E`-target recovery.
- **Falsification:** RM exponent `≈q` (constant-only) at every size (→ feed D3).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_isogeny/b2b1_kani_rm_genus2_ic.sage \
    --sizes 12,16,20 --seeds 20260717-20260720 \
    --out experiments/ecdlp_isogeny/b2b1_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_isogeny/b2b1_kani_rm_genus2_ic.sage \
    --sizes 12 --seeds 20260717 --stage construct_and_rm_split_only \
    --out experiments/ecdlp_isogeny/b2b1_smallest_probe.json
  ```

### Experiment Contract: C3 — elliptic character-sum decomposition-count bias

- **Hypothesis:** for a structured ordinary `E/F_p` the decomposition count `N(R)=#{A+C=R : A,C∈F}`
  has a `poly`-detectable low-frequency character-sum bias `Δ=Ω(L^{-c})` (non-vanishing) yielding
  relation-gen exponent `<1/2`.
- **Null:** `N(R)` is square-root-equidistributed (Deligne/Weil) ⇒ `Δ=O(n^{-1/2})`, no exploitable
  bias (= the Ahmadi–Shparlinski energy barrier).
- **Parameters:** ordinary prime-order `E/F_p`, `p≈2^16,2^20,2^24`; `B=L=⌈n^{1/5}⌉`; seeds
  `20260717..20260722`.
- **Metrics:** empirical distribution and top character coefficients of `N(R)` vs the equidistribution
  null; bias magnitude `Δ`; detection cost (number of significant characters); relations harvested at
  biased `R`; sparse rank; group/field ops.
- **Positive control:** a curve with planted additive structure (small rational torsion / small-disc
  CM) — should show a low-frequency bias.
- **Negative control:** a random ordinary curve — should match square-root equidistribution.
- **Success:** non-vanishing, low-frequency, `o(n)`-detectable `Δ` giving relation-gen exponent
  `<1/2` across all three sizes.
- **Falsification:** `N(R)` matches equidistribution at every size (→ reusable P1447 refinement).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/b2c3_decomposition_count_bias.sage \
    --sizes 16,20,24 --seeds 20260717-20260722 \
    --out experiments/ecdlp_prime_field/b2c3_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/b2c3_decomposition_count_bias.sage \
    --sizes 16 --seeds 20260717 --stage count_distribution_vs_null \
    --out experiments/ecdlp_prime_field/b2c3_smallest_probe.json
  ```

---

## 5. Red team — are the three winners disguised repetitions or cost-negative?

**A1 (3-LP hypergraph homology).**
- *Disguised repeat of M2 (2-LP graph) or NR-1475 (char buckets)?* No: those are arity-2 with graph
  cycle rank; A1 is arity-≥3 with simplicial `H_1`. **But** the ledger's own hypergraph-relabel null
  (PO73) *matched* signal at arity 2 — strong prior that the arity-3 complex is also homologically
  trivial in the sparse regime (Linial–Meshulam). **Cost-negative risk:** collecting 3-LP facets
  costs `Θ(L^{1+1/5})` events and `L^{3ℓ'}` incidence — if `δ_3→0`, this is pure overhead. **Verdict:**
  genuinely new *measurement* on the *under-attacked* open theorem (RT-1472); most likely a negative
  that extends RT-1472 to higher arity — which is itself frontier-advancing.

**B1 (Kani-RM genus-2).**
- *Disguised repeat of NR-022 (scalar Weil) or PO-003..006 (covers)?* No: NR-022 is a split/scalar
  surface with the Semaev degree preserved; PO-003..006 push back to the elliptic x-line relation;
  B1 solves natively in a **non-split RM Jacobian**. **The sharpest challenge is D3:** genus-2 IC
  over `F_p` costs `q^{2−2/g}=q`, and RM is only known to give constant-factor speedups — so the
  honest prior is that B1 collapses to `q` and **loses to rho**. **Cost-negative risk: high** —
  genus-2 Jacobian arithmetic and the `(N,N)`-isogeny construction carry large constants and memory.
  **Verdict:** highest novelty of the batch and a genuine non-x-line engine, but honestly most likely
  a negative that *formalizes D3's RM-escape boundary* — the decisive value.

**C3 (character-sum bias) — the high-risk winner after C1's demotion.**
- *Disguised repeat of Batch-1 A3 (incidence) or NR-1408 (sumsets hash-like)?* No: A3 *reports* pairs
  and NR-1408 tested *image compression*; C3 seeks a **spectral bias in the decomposition count**, a
  quantity neither measured. **But the honest prior is strongly negative:** Deligne/Weil
  equidistribution predicts `N(R)` is square-root-uniform for a generic ordinary curve, so any bias
  is a special-curve artifact — exactly the Ahmadi–Shparlinski energy wall the ledger already fears
  (P1447). **Cost-negative risk:** full character analysis is `Õ(n)` unless the bias is low-frequency;
  if it is not, detection alone dominates. **Verdict:** genuinely novel *measurement* (POSSIBLY NOVEL
  after a documented search), most likely a clean negative that sharpens P1447 into "EC decomposition
  counts carry no exploitable low-frequency bias" — a reusable barrier.

**On the demoted C1 (representation-MITM).** Kept in the batch but *not* a winner: the Literature Agent
found Delaplace–May (2019/2020) and Delaplace–Fouque–Kirchner–May already apply this exact mechanism
to ECDLP over `F_{p^ℓ}` (`ℓ≥2`), reaching only `O(p)` / `p^{4/5}`-with-precomputation and admitting
they fall short of Bernstein–Lange. C1 survives *only* as the narrowed, author-flagged-open `ℓ=1`
sub-question (a faster zero-testing routine); its value is now to attack that precise open sub-case,
with D1 as the paired barrier.

**Cross-cutting red-team conclusion.** As with Batch-1, all three winners are **most likely negative
results** — but each is (a) mechanism-distinct from every inventoried entry *and* from the 12 Batch-1
candidates by a *named new operation*, (b) equipped with an exact toy verifier, and (c) attached to a
paired barrier (A1→RT-1472 δ-boundary at higher arity; B1→D3 RM-escape; C3→Deligne equidistribution),
so a negative outcome still *advances the barrier map*. Crucially, **A1 is the first candidate in
either batch to attack RT-1472** rather than RT-1476 — closing a real gap in the lab's frontier
coverage. The two conditional theorems (RT-1472 enrichment `δ>1/4`; RT-1476 backend `α<3/2`) remain
the whole frontier; this batch adds the higher-arity homology probe of the former (A1) plus a genuine
non-x-line relation engine (B1) and orthogonal complexity/analytic probes, each of which either
realizes a new channel or sharpens its barrier. **Post-literature honesty note:** of the twelve, the
most already-mined are C1 (three published ECDLP papers) and B2 (settled-negative for trace≠1); the
most genuinely open (construction-gap, not proven-cost-bound) are B1, A3, and A2.

---

## 6. Claim discipline

- Every candidate is `HYPOTHESIS`/`CONJECTURE` — **no** performance claim is made.
- "Relations" ≠ "ECDLP recovery": every contract requires relation-derived **blind** target descent
  under full charging, not relation validity alone (cf. ECFG-P845/846: 0.61× rho packets are
  *relation-generation precursors*, explicitly not target descent).
- All evidence targeted is `TOY` / `MODEL-BOUND`; novelty verdicts are search-bounded
  (`LEDGER-NEW` = "absent from the two ledgers + Batch-1"; `POSSIBLY NOVEL`/`LITERATURE-ADJACENT` =
  the outcome of the completed Literature-Agent primary-source pass, not a certification).
- A failed candidate is a **scoped negative result**, not evidence that prime-field ECDLP cannot be
  improved.

**Literature-Agent reconciliation (completed, folded into every candidate above).** A dedicated
primary-source pass corrected four verdicts against the initial ledger-only novelty check: **C1**
(representation-MITM) is a *published* ECDLP line (Delaplace–May 2019/2020; Delaplace–Fouque–Kirchner–
May) that falls short of rho for `F_{p^ℓ}`, `ℓ≥2` → demoted, and the honest open case is `ℓ=1` +
faster zero-testing; **B2** (Serre–Tate) is settled-negative for trace≠1 (Voloch unification);
**C2** (p-curvature) is near-definitionally order-only for `g=1` (Hasse–Witt is `1×1`; Achter–
Casalaina-Martin–Vakil); **A1** (3-LP homology) faces Cavallar's finding that 2LP→3LP is
constant-factor, not exponent, in the analogous factoring setting → `NOVELTY-UNVERIFIED`. The most
genuinely open (construction-gap rather than proven-cost-bound) are **B1** (Kani-RM genus-2, obstructed
by Gaudry's `Õ(q)` unless RM lowers the exponent), **A3** (Kedlaya–Umans membership, obstructed by the
undemonstrated system-solve→multipoint-eval reduction), and **A2** (NFS two-sided, obstructed by the
missing second smoothness-side).

## 7. Next three pushes (Research-Director decision)

1. **Conservative:** run A1's smallest probe (`h1_delta_vs_null`, one 16-scale `q≈L^5` curve) — one
   cheap number (`δ_3` vs the matched null) that either motivates or closes the higher-arity RT-1472
   lane the whole lab has so far left untouched.
2. **Representation:** run B1's `construct_and_rm_split_only` slice — build one RM Kani glue and
   measure whether the RM eigen-split even changes the relation-search dimension before committing to
   genus-2 IC.
3. **High-risk / barrier:** run **C3**'s `count_distribution_vs_null` slice (one 16-scale curve — a
   cheap decomposition-count histogram vs the equidistribution null) and, in parallel, commission
   **D2** (crystalline order-only barrier) from the Theory Agent regardless of B2/C2 outcomes — D2
   upgrades the ledger's already-observed Cartier–Manin *anchor-invariance* (TRANSFER-NR-011/015)
   into a theorem and closes the entire canonical-lift/p-curvature lane for non-anomalous curves,
   the single highest-leverage barrier in this batch.
