# Research-Director Idea Generation — 2026-07-18

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Mission:** propose *mechanism-new*, falsifiable directions whose **complete** cost could
eventually beat the single-target Pollard-rho `0.886·sqrt(n)` baseline for ECDLP over
**ordinary prime fields**. Toy correctness, a new coordinate system, a relation certificate,
faster preprocessing, or a solver swap is explicitly **not** a breakthrough.

Autonomous scheduled run (no user present); choices noted inline.

**Hard anti-duplication constraint for this run.** **Two** prior scheduled reports exist from
2026-07-17: `research/idea_generation_20260717.md` (batch1, 1390 lines) and
`research/idea_generation_20260717_batch2.md` (batch2, 1554 lines). Between them they consumed
*every* search seed named in this task's brief (Hasse-jet/dual-number lifting, tropical/Newton-polytope,
output-sensitive incidence reporting, arithmetic-dynamical transfer operators, noncommutative
correspondence/path algebras, tensor-network/separator-rank) **and** several beyond it (3-large-prime
homology, NFS two-sided, Kedlaya–Umans membership, Kani-RM genus-2, **Serre–Tate canonical lift**,
level-≥3 theta-bilinear, representation-MITM, p-curvature, **crystalline/Cartier–Manin**, **elliptic
character-sum bias**). This report is held to a **stricter** novelty bar: each candidate must be
mechanism-new against the ledger **and both** 07-17 reports. I treat both as inputs 13–14 and
fingerprint against them explicitly (see §0.1 for a disclosed reconciliation: three of my initial
candidates collided with batch2 and were demoted).

---

## 0. Review scope and inventory census

**Sources read (all four required inputs, plus derived corpus and the prior report):**

1. `research_ledger.md` (2.7 MB, 2462 lines; sections: open-frontier (103 items), active
   hypotheses, negative results, positive signals, baselines, literature map, graph-index
   frontier, negative controls, P1436/P1437 continuation, **new** division-character routing
   (NR-1484/RT-1485) and oriented-norm-Kani (ISO-NR-ONK/IKD-001..009)).
2. `ecdlp_index_calculus_state/research_ledger.md` (720 lines; ECFG functional-graph +
   direct-source packet track; **now at P1510–P1513**, a database worst-case-optimal-join /
   factorized-semijoin / linear-Chow-atomizer attack on the 5-term provenance query).
3. `research/non_generic_transfer_search_20260610.md` (390 lines; transfer/decomposition
   channel search + PO-transfer-001..006 appendix; twist positive control, trace-fiber lemma).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` (10 primary IC entries:
   Semaev 2004, Gaudry 2009, FPPR 2012, Shantz–Teske 2013, FHJRV 2014, Kousidis–Wiemers 2015,
   Karabina 2015, Amadori–Pintore–Sala 2017, McGuire–Mueller 2017, Trimoska–Ionica–Dequen 2020).
5. Referenced corpus: 1108 files in `research/` (178 `PO_transfer` contracts, 169 `ISO-AR`
   atlas entries, `PAPER_*`, `p14xx` barrier/theorem notes), plus the full 2026-07-17 report.

**Census (machine-readable counts, this run):**

- **Distinct negative IDs (numeric, ECFG-NR): 501**, span `303..1484`; plus TRANSFER-NR ≈ 53,
  ISO-AR/SP/CW-NR ≈ 59, ISO-NR-ONK/IKD 3, core `NR-` 13, SHA1-N 9. **Total distinct negatives
  ≈ 638** (unchanged family structure vs 07-17; the delta since is division-character +
  oriented-Kani rows, both isogeny-finding, off the rho lane).
- **Active hypotheses:** ECFG-H 382 (`H303..H687`), ISO-AR/SP 33, TRANSFER-H 8, SHA1-H 4 ≈ **427**.
- **Positive signals:** ECFG-P 937 (`..P1513`), TRANSFER-P/PO ≈ 95, ISO-AR-POS ≈ 36 ≈ **1068**.
- **Restricted-model rows (rho-relevant):** ECFG-RT 3 (`RT-1472`, `RT-1476`, `RT-1485`).
- **ID families covered:** ECFG (coordinate index-calculus + Evans functional graph — the
  dominant lane; now with a database-join sub-lane P1510–P1513), TRANSFER/PO (cover/Prym/Jacobian
  correspondence), ISO-AR/ISO-SP/ONK/IKD (oriented-CM isogeny + self-pairing + oriented-ideal
  Kani recovery), SHA-1 seed bounty (off-topic to ECDLP), bare `NR-` core.

**Extracted fingerprint fields per family** (mechanism / representation / exploited structure /
factor base / relation shape / relation-generation / compression / linear-algebra object /
target-descent / cost bottleneck / outcome / scoped negative boundary / next branch) are
tabulated in §1. **Load-bearing bottom line, re-confirmed:** *no ledger entry, and no candidate
in the 07-17 report, demonstrates a complete-cost single-target speedup over Pollard rho on
prime-field ECDLP.* Every empirical "below rho" is amortized-many-target and/or setup-uncharged.
The only rho-crossing paths on record are **two conditional restricted-model targets that remain
unrealized: RT-1472 (2-large-prime enrichment `δ>1/4`) and RT-1476 (m-ary membership backend
`α<3/2`).** These two, plus the standing barriers, are the constraints every candidate must respect.

---

## 0.1 Batch-2 anti-duplication reconciliation (disclosed)

**Process note (integrity).** I initially fingerprinted only against batch1 and drafted twelve
candidates. Re-checking the second 07-17 report (`..._batch2.md`, 1554 lines) — which I had not read
before drafting — revealed that **three of my candidates collided with batch2 mechanisms**. I disclose
and correct rather than silently overwrite:

| My draft candidate | Batch2 collision | Batch2's verdict | Resolution here |
|---|---|---|---|
| **B1** canonical-lift Serre–Tate formal log | batch2 **B2 (`STATE-B2`)** — *identical* mechanism (Serre–Tate coordinate, formal-log additivity `log_ST(kB)=k·log_ST(B)`, anomalous positive control) | **LITERATURE-ADJACENT / settled-negative** for the linearization form (Voloch unifies Smart/Satoh–Araki/Semaev as one trace-1-only mechanism; for `n≠p` the formal group sees only the trivial `p`-part) | **DEMOTED to DUPLICATE / REJECTED.** No longer the representation winner. |
| **B2** Cartier–Manin cohomology operator | batch2 **D2** — crystalline/Cartier–Manin **order-only barrier** (already a theorem-grade barrier there) | barrier established | **RECLASSIFIED** as a restatement of batch2 D2 + Achter et al.; cite, do not re-propose. |
| **C2** Kloosterman importance-sampling | batch2 **C3 (high-risk winner)** — elliptic character-sum **bias relation oracle** | POSSIBLY NOVEL, paired equidistribution barrier | **DEMOTED to ADJACENT.** Distinct sub-mechanism (sampler *weight* vs relation *count* bias) but the same Deligne-equidistribution obstruction; not a winner. |

**Corrected winner slate** (see §4): conservative **A1** (sparse-interpolation — safe, absent from both
batches), high-risk **C1** (approximate-homomorphism stability — safe), and a **replacement
representation winner B4** (Semaev summation-tensor **border rank / bilinear complexity** — verified
absent from both batches, and distinct from batch1's *separator*-rank B2, a different tensor-complexity
invariant). Candidates that survive as genuinely mechanism-new against *both* batches: **A1, A2, A3, B3,
B4, C1** (six — the mandate's minimum outside dominant vocabulary), plus the three new barriers D1–D3.
The colliding B1/B2/C2 are retained below only as documented duplicates for the fingerprint record.

---

## 1. Fingerprint inventory by mechanism family (compressed)

`F(entry) = (object, ops, hidden-structure, discarded, retained, relation-primitive,
compression-primitive, rank-mechanism, descent-mechanism, dominant-cost-exponent)`.

| Fam | Object | Structure exploited | Relation / compression primitive | Rank mechanism | Descent | Dominant cost | Outcome / scoped boundary |
|---|---|---|---|---|---|---|---|
| **M1 ECFG coordinate IC** | `E/F_p`, `B≈n^(1/5)` | recursive `S1,S2,S3` five-term `A+C=R`; bases `interval_x`, `x_mod4`, rational-map, `x^L=1` subgroup, autos | pair-compiler, shared-x buckets, CRT/product trees, preimage DAG | weighted factor-log matrix, sparse | one-factor online descent | membership / generator cost | **TOY, no single-target win.** Explicit join `B^3=n^0.6`; end-to-end `22..66× rho`. |
| **M1b ECFG join-query** (P1510–P1513) | 5-term provenance query as DB join | acyclic join tree, FD width, factorized semijoin, linear-Chow atomizer, shared common-norm | worst-case-optimal join, subresultant/gcd semijoin | determinantal / Chow cycle length | shared | **input-iterator `r^3=q^(3/5)`** | **NEGATIVE (verified):** every atomizer provably cubic (`det`-degree ≥ dim); output-sensitive common-norm still `Ω(r^(5/2))`; input floor unbroken. |
| **M2 large-prime graph** | 1-LP / 2-LP endpoint graph | residual-column occupancy; endpoint-incidence cycles | pair table, signless nullity | graph cycle rank | LP-log propagation | 1-LP `(1+β)/2=0.6`; 2-LP setup `Θ(L²)` | **RT-1472:** 2-LP crosses `1/2` iff advice enrichment `δ>1/4`; explicit decks give `δ≤1/4`. |
| **M3 implicit membership backend** | m-ary Semaev pair/5-term membership | `x^L=1` sparse S3, char buckets, CM orbit, serial-S3 state, resultants | implicit predicate eval | sparse full-rank | shared backend | query exponent `α` | **RT-1476:** backend with `α<3/2` (m=5), setup `≤L²`, random support, full-rank → conditionally beats rho. **All tried backends miss it.** |
| **M4 cover/Prym/Jacobian transfer** | genus-2/3 covers, Pryms, `Z[π]` lattices | hidden E-isotypic block, C3/deck projectors, norm labels `z^d=h(P)` | source principal-divisor / ternary constant-sum, LP closure | C3-module kernels, Rosati Gram | calibrated logs → point lookup | Prym cert + cover setup | **RESTRICTED THMs:** deck/Prym maps scalar-or-zero on visible E; best recovery `~3376× rho`. |
| **M5 oriented-CM isogeny + Kani** | oriented `O_K`, volcano, `θ`, Kani, oriented ideals | target-free kernel construction, oriented-ideal norm floor `ceil(|D|/4)`, `n^2=d+Norm(a)` | — | — | — | torsion-field degree | **OBS/RESTR-THM, TOY.** Isogeny-**finding**/vectorization + oriented-ideal-Kani planting; does **not** attack rho. |
| **M6 ECFG public selectors** | Evans graph `k→x(kB)` | depth/component/indegree as leaf selectors | frozen gates route relation leaves | selected-event yield vs uniform | shift-lookup | full graph = N edges | **NEGATIVE chain:** every selector wins post-hoc, fails prospective; reverse index amortized-only. |

**Standing barriers / restricted theorems (frontier constraints every candidate must respect):**

- **B-Dreg:** degree-of-regularity **conservation** over `F_p` (`PAPER_prime_field_ecdlp_resistance_map.md`,
  Yokoyama-2020-consistent): naive Semaev/Gröbner, coordinate reparametrization, scalar
  Weil-restriction/abelian-surface (NR-022), crossbred `m=3`, multi-target rho — none lowers the
  exploitable solving degree.
- **B-trace-fiber (PO-005):** for a group hom `τ:H→G`, full kernel fibers multiply successes and
  trials equally → no relation-probability or rank gain.
- **B-permutation (TRANSFER-NR-001, ISO-CW-NR-001):** a measure-preserving correspondence
  preserves multiplicities → no rank gain.
- **B-preproc (Corrigan-Gibbs/Kogan; CHW SGGM):** generic frontier `S·T² = Ω̃(εq)`; structured
  success `≤ Õ(S·T²/q + δ·T)`. Fixed-curve online wins sit on this frontier once advice, bandwidth,
  success prob, and supported target count are charged.
- **B-explicit-edge (P1434):** explicit terminal source-edge coordinate circuits admit **no**
  compressed exact promoting rule. **Loophole left open:** *generative / sketch-based witness
  recovery* (non-explicit membership).
- **B-n=1 collapse (Gaudry/Diem):** prime-field `n=1` has no proper base field to Weil-restrict →
  Semaev degree blows up. A candidate must survive this or bypass polynomial-system solving.
- **B-cubic-join (M1b, P1510–P1513, new):** the source-labelled 5-term provenance query has input
  size `r^3=q^(3/5)`; database join planning (AGM/WCOJ), factorized semijoin, and scalar-linear
  Chow/determinant atomizers are all provably `≥` cubic. **Loophole left open:** a *target-specialized
  nonlinear* circuit (explicitly preregistered but unrealized in P1512/P1513).

**07-17 report candidates (must not be re-proposed):** A1 BKK/mixed-volume, A2 elliptic-net/EDS
smoothness, A3 output-sensitive incidence-reporting (polynomial partitioning), B1 dual-number/jet
filter, B2 tensor-train/separator-rank, B3 tropical/p-adic-lift, C1 quiver/groupoid CM-correspondence
composition, C2 Lattès transfer operator (rejected, incomplete), C3 xedni-2.0 height lift, D1
nilpotent-lift no-rank-gain theorem, D2 correspondence-permutation no-gain theorem, D3 separator-rank
lower bound.

---

## 2. Known-closed / control-only territory

A candidate is a **duplicate** unless it breaks a measured obstruction with a *new mathematical
operation*:

1. Ordinary same-field isogeny invariants — TRANSFER-NR-001/044, ISO-CW-NR-001.
2. Scalar Weil pullback / level-2 theta / Kummer charts (Dreg-preserving) — NR-022, TRANSFER-NR-005/010/030/045/046.
3. Explicit two-large-prime advice graphs — ECFG-NR-1471; RT-1472 (`δ>1/4` needed).
4. Joint factor / large-prime block-Krylov solving — TRANSFER-NR-042, NR-033/036.
5. Pair-residual character buckets — ECFG-NR-1475.
6. Non-invariant CM endpoint decks — ECFG-NR-1474.
7. Materialized serial-S3 backward-state polynomials (`L^1.675`) — ECFG-NR-1477.
8. Dense composed resultants (`4L²`, zero held-out prediction) — ECFG-MX-1478.
9. **Database join planning / factorized semijoin / scalar-linear Chow atomizer** (all `≥` cubic
   `r^3`) — ECFG-P1510/P1511/P1512, `P1512-R1`. **(new control)**
10. Source selectors / post-hoc scheduling without an honest hit generator — ECFG-N001..061 chain.
11. Relation validity without relation-derived ECDLP recovery — ECFG-NR-418/420/424/425/427/428.
12. Preprocessing wins that lose to rho on offline/memory/advice/target count — ECFG-NR-1406/1433.
13. Twist / extension-field channels — `ISO_GOAL_FOUND_p224_twist`.
14. Materialized serial-S3 factor-log linear feature spaces `≤L^(1/2)` — ECFG-NR-1479.
15. **All twelve 07-17 candidate mechanisms** (BKK, EDS, incidence-report, jet, tensor-train,
    tropical, quiver-composition, Lattès, xedni, and the three barrier theorems). **(new control)**
16. Oriented-ideal Kani recovery / SCALLOP-style planting — ISO-NR/OBS-ONK/IKD (isogeny-finding,
    not a rho attack).

High-numbered ECFG-NR provenance/containment rows, SHA1-N, and the ISO-AR "V-chain" are
instrumentation negatives, **not** mathematical dead-ends.

---

## 3. Twelve candidates

Notation: `q≈n` prime subgroup order; `B≈n^(1/5)` factor base; `L≈B`; rho `≈0.886·n^(1/2)`;
IC total `≈ B·(cost/relation) + B²(sparse LA) + descent`; `B²=n^(2/5)<n^(1/2)`, so the sparse-LA
stage is **not** binding — the **relation/membership stage** is. The named open gate is **RT-1476**:
a complete m-ary membership backend with query exponent below `3/2` (`m=5`), `≤L²` setup, random-like
support, sparse full-rank.

**Design principle for this run.** Six-plus candidates begin *outside* the ledger's dominant
vocabulary (Semaev/Gröbner, cover/Prym, isogeny/CM, large-prime, database-join): I draw from
sparse-polynomial interpolation, combinatorial design theory, algebraic coding / list-decoding,
p-adic canonical lifts + formal-group logarithms, crystalline/Cartier–Manin cohomology, discrete
Fourier / dual-group analysis, quantitative additive combinatorics (approximate homomorphisms),
and exponential-sum (Kloosterman) biasing. Novelty verdicts are cross-checked by the Literature
Agent against primary sources (see §3.13 for its integrated findings).

### Group A — conservative extensions of known IC work

---

## Candidate: A1 — Sparse-interpolation (Prony / Ben-Or–Tiwari) output-sensitive Semaev root backend

### One-sentence mechanism
Exploit that the univariate elimination polynomial of the m-point decomposition system has
**few `F_p`-roots per query** to recover its **root-locator** by transform-domain **sparse
polynomial interpolation** (Prony/Ben-Or–Tiwari/sparse-FFT) in time `Õ(roots)` rather than the
dense `Θ(L²)` resultant, reducing per-relation membership cost `C` below the RT-1476 boundary.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (sparse interpolation is mature in computer algebra; never applied to Semaev
root extraction; distinct from the 07-17 BKK path and from the P1513 common-norm path — see below).

### Semantic fingerprint
- object: `m∈{4,5}`-point EC decomposition system over `F_p`, `B≈n^(1/5)`.
- ops: public curve arithmetic; multipoint evaluation; Prony/BOT solving.
- hidden structure: **sparsity of the root set** (few relevant `F_p`-roots per shift), and
  sparsity of the elimination polynomial in the division-polynomial / Chebyshev-adapted basis.
- discarded: dense monomial coefficients of the resultant.
- retained: the root-locator (degree = number of roots).
- relation primitive: five-term `A+C=R` membership.
- compression primitive: **evaluation-interpolation of a sparse locator**, not elimination.
- rank mechanism: unchanged weighted factor-log matrix (sparse full-rank target).
- descent: standard one-factor online descent.
- dominant cost exponent: `log(#roots + locator-sparsity)/log L` — **the object of measurement**.

### Nearest ledger entries
1. **ECFG-MX-1478 (dense resultant `4L²`, zero held-out prediction)** — MX-1478 *materializes*
   the dense resultant; A1 never forms it, interpolating only its sparse root-locator from
   `Õ(sparsity)` evaluations. **Distinction: evaluation-interpolation vs elimination.**
2. **ECFG-P1513 (shared bivariate common-norm, `Ω(r^(5/2))`)** — P1513 computes a *resultant norm*
   `Res_U(T,H)` and finds it cubic/`r^(5/2)`; A1 targets the *root count* of the univariate
   projection, a strictly smaller object, via a sparse transform. **Distinction: root-locator
   sparsity vs norm degree.**
3. **ECFG-NR-1477 (serial-S3 state `L^1.675`)** — measured dense *state polynomials*; A1 measures
   *root-set* size. **Distinction: variety-fibre size vs state density.**
4. **07-17 A1 (BKK/mixed-volume)** — BKK counts homotopy paths via the Newton polytope; A1 uses
   no polytope and no homotopy, recovering the locator by Prony from field evaluations.
   **Distinction: transform-domain interpolation vs polyhedral path count.**
5. **RT-1476** — A1 is a concrete backend candidate, not a new gate. **Distinction: candidate vs gate.**

### Nearest literature
Ben-Or–Tiwari 1988 (sparse interpolation); Prony 1795; Giesbrecht–Labahn–Lee 2009 (finite-field sparse
interpolation); **Bi–Cheng–Rojas, arXiv:1602.00208 (sublinear root-finding for `t`-nomials over `F_q`)**
and von zur Gathen–Shoup (finite-field root-finding); Semaev 2004; McGuire–Mueller 2017 (Gröbner-free
summation-polynomial *evaluation* — closest IC precedent, enumerates, does not interpolate a locator).
**Literature Agent correction (load-bearing):** Ben-Or–Tiwari exploits *monomial-support* sparsity, but
`S_m` is generically *monomial-dense*; what A1 actually needs is *root-count* (output) sparsity — a
**different notion**, closer to output-sensitive `t`-nomial root-finding than to sparse interpolation.
**Before any run, the Algebra-System Agent must measure `S_m`'s monomial support**; if dense, A1 is
reframed as "output-sensitive root-finding of a low-individual-degree dense multivariate system" (also
underexplored), not sparse interpolation. Gap: neither framing has been analyzed for Semaev.

### Target family
Random ordinary prime-order short-Weierstrass `E/F_p`, `p` prime, `n=#E` prime, `j∉{0,1728}`.
Excluded: anomalous, supersingular, small embedding degree, small-CM-discriminant.

### Full algorithmic path
1. **Factor base:** `interval_x`/rational-map base, size `B≈n^(1/5)`, `O(B)` group ops.
2. **Relation generation:** for a public shift `R`, form the univariate projection `Ψ_R(x)` of the
   `S_m` system (eliminate all but one factor variable *symbolically once*, curve-independent);
   evaluate `Ψ_R` at `Õ(t)` points where `t` = a guessed root/sparsity bound; run BOT/Prony to
   recover the root-locator `Λ_R`; its roots give the factor indices.
3. **Witness extraction/verification:** each root replays exact EC additions `A+C=R`; verify.
4. **Relation probability:** `≈ K·B^5/q = Θ(B)` supply per `K=Θ(B)` shifts.
5. **Matrix:** `Θ(B)×B`, density `O(1/B)`, target sparse full-rank (`t≥B−1`).
6. **Factor-log calibration:** standard.
7. **Descent:** one-factor online descent per target.
8. **Offline/online:** the symbolic projection template is curve-independent (offline); evaluation
   + Prony is online.
9. **Memory/parallel:** `O(t)` per query; embarrassingly parallel over shifts.

### Cost model
Per-relation `= (#evaluations of Ψ_R) · (eval cost) + (Prony solve of size t)`. If the root count
per valid shift is `Θ(1)` **and** the locator is `t`-sparse with `t=B^{o(1)}`, cost is `B^{o(1)}`
and total relation-gen `= B·B^{o(1)} = n^{1/5+o(1)} ≪ n^{1/2}`. **Promotion requires** measured
`t < B^{3/2}` (RT-1476 `m=5`), ideally `t=poly(m)·B^{o(1)}`. Compare rho `n^0.5`; explicit-join IC
`n^0.6`; P1513 norm `q^(3/5)`.

### Why existing negatives do not kill it
Avoids **B-cubic-join / MX-1478 / P1513** (never forms the dense resultant or norm), avoids
**B-Dreg** (no Gröbner solving degree). New operation: **transform-domain recovery of the Semaev
root-locator by sparse interpolation.**

### Likely fatal obstruction
The univariate projection `Ψ_R` is itself **dense of degree `Θ(L²)`** (MX-1478/P1513 both saw
dense norms); evaluating a degree-`L²` polynomial at even one point costs `Θ(L²)`, so the *evaluation*
stage — not the root count — dominates, and Prony's advantage over root-finding evaporates. Sparse
interpolation helps only if `Ψ_R` is *sparse* (few nonzero terms), which the dense-resultant evidence
argues against. (This is exactly what the experiment measures, and the paired barrier D1 formalizes.)

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`, seeds `20260718..20260723`, `m=4,5`: (i) build `Ψ_R` for a public shift and
measure its *monomial sparsity* and *root count*; (ii) time Prony-recovery of `Λ_R` vs direct
root-finding vs full join. Positive control = a deliberately sparse toy elimination polynomial
(BOT should win). Negative control = a random dense polynomial of matched degree (BOT should lose).
Fit `log t/log B` and `log(root count)/log B`.

### Quantitative promotion gate
Measured locator-sparsity **and** evaluation cost together give relation-gen exponent `<1/2` in `n`
across all three sizes, **and** relations reach sparse rank `t≥B−1`. Correctness alone is *not* the gate.

### Proof track
Theorem: `Ψ_R` has `O(B^{3/2−ε})` nonzero terms in the division-polynomial-adapted basis. Would
follow from a sparsity structure theorem on the `S_m` elimination ideal.

### Disproof track
Measured dense `Ψ_R` (`Θ(L²)` terms) at all sizes ⇒ scoped negative "Semaev elimination polynomials
are transform-dense; sparse interpolation gives no membership backend," refining MX-1478 from
*coefficient* density to *basis-invariant* sparsity.

### Reproduction artifact
- contract: `research/experiment_contract_a1_sparse_interp_20260718.md`
- impl: `experiments/ecdlp_prime_field/a1_sparse_locator.sage`
- result/audit: `.../a1_sparse_result.json`, `.../a1_sparse_verify.sage`
- ledger id: `SPARSE-A1`

---

## Candidate: A2 — Combinatorial-design (Sidon / B_h) factor base

### One-sentence mechanism
Choose the factor base so its x-coordinates form a **Sidon set (B_2) / B_h set / perfect-difference
set** in `F_p`, so that factor-base pair/`h`-sums have **controlled collision multiplicity**, and
test whether design-controlled supply raises the relation-matrix rank *quality* (independent
relations per unit work) above a generic-interval base.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (Sidon/B_h sets are classical additive combinatorics; used in coding and compressed
sensing, never as an EC index-calculus factor-base design; distinct from all ledger bases, which are
value-membership designs, not additive designs).

### Semantic fingerprint
- object: `E/F_p`, factor base `S = {P_i : x(P_i) ∈ Sidon set}`.
- ops: EC arithmetic; membership by set lookup.
- hidden structure: **sum-distinctness of the x-coordinate design**.
- discarded: geometric locality of an interval base.
- retained: additive-design collision structure.
- relation primitive: `A+C=R` pair membership.
- compression primitive: design guarantees few coincidences → predictable sparse pattern.
- rank mechanism: **rank quality of the design-structured relation matrix — object of measurement**.
- descent: standard.
- dominant cost exponent: relations-per-attempt vs rank, as a function of design.

### Nearest ledger entries
1. **M1 `interval_x` / `x_mod4` / rational-map / `x^L=1` bases** — all value-membership designs;
   none chosen for *sum-distinctness*. **Distinction: additive combinatorial design vs value predicate.**
2. **ECFG-NR-1475 (pair-residual character buckets)** — buckets group by a residual character; A2
   chooses the *base points themselves* by an additive design. **Distinction: base design vs bucket.**
3. **B-permutation / B-trace-fiber** — A2 does not transport a base; it constructs one. **Distinction:
   construction vs correspondence.**
4. **07-17 A2 (EDS smoothness)** — unrelated (net values); A2 here is a set-design of x-coordinates.
5. **RT-1476 / RT-1472** — A2 could feed either backend a better-structured base. **Distinction:
   base design, not backend.**

### Nearest literature
**Singer, Trans. AMS 1938** (perfect difference sets); **Bose–Chowla 1962** (`B_h[1]` sets);
Erdős–Turán (Sidon); Ruzsa. **Literature Agent (POSSIBLY NOVEL, absence-based/provisional):** no hit
for design-based factor bases in *any* index calculus (EC or classical NFS); standard EC bases are
smoothness/membership-selected, never `B_h`-designed. **Cross-link to C1 (load-bearing):** Ahmadi–
Shparlinski-type `F_p` sum-product bounds may impose an *unconditional ceiling* on how Sidon-like a set of
*curve x-coordinates* can be (unlike unconstrained subsets of `F_p`) — pursue A2 and C1/D2 jointly; that
ceiling would convert A2 from "untried" into "bounded design space," sharper either way. Gap: no
additive-design factor base for point decomposition, and no derivation of the `x(E)` design ceiling.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Factor base:** construct a Sidon/B_h set `Σ⊂F_p` of size `B≈n^(1/5)` (Singer/Bose–Chowla
   construction, offline), keep the `P_i` with `x(P_i)∈Σ` (roughly half exist by quadratic residue).
2. **Relation generation:** standard `A+C=R` search over the design base.
3. **Witness/verify:** replay `A+C=R`.
4. **Relation probability:** `Θ(B)` supply; **measured** collision pattern vs interval base.
5. **Matrix:** `Θ(B)×B`; **measured** rank vs a matched interval/random base.
6–9: standard calibration/descent/offline-online/parallel.

### Cost model
Same asymptotic supply as a generic base; the bet is on **rank quality** — if the design yields
`≥B−1` independent relations from `o(B)`-fewer attempts (a *constant* in the exponent that
compounds), or removes rank-deficiency that forces large-prime repair (the M1/M4 failure mode),
it lowers the effective relation-gen exponent. Compare rho `n^0.5`.

### Why existing negatives do not kill it
No ledger base is an additive design; the sum-distinctness property is untested. New operation:
**Sidon/B_h sum-distinct factor-base design.**

### Likely fatal obstruction (paired with D2)
The EC group law scrambles the design: `x(A+B)` is *not* `x(A)+x(B)`, so sum-distinctness of
x-coordinates does **not** transfer to sum-distinctness of the *group sums* that define relations.
The design property is destroyed by the addition law (the "hash-like sumset" wall, ECFG-NR sumset
rows). Expected: rank identical to a random base.

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`: build a Sidon base and a matched interval/random base; measure (i) relation
yield per attempt, (ii) matrix rank at fixed `t`, (iii) fraction requiring large-prime repair.
Positive control = a toy group where the design *is* preserved (e.g. `(Z/p,+)` itself). Negative
control = random base (should match). Fit rank-vs-attempts.

### Quantitative promotion gate
Design base reaches `t≥B−1` at a *measurably smaller* attempt-exponent than the interval base,
stable and growing across three sizes (an exponent gain, not a one-off constant).

### Proof track
Theorem: the group-sum image of a Sidon x-set retains `Ω(1)` sum-distinctness density. Would need an
additive-energy bound for `x(E)` restricted to a design — likely false, which is the value.

### Disproof track
Measured rank/attempts identical to random ⇒ scoped negative "additive x-designs do not survive the
EC addition law," a clean quantitative statement of the sumset-scrambling wall.

### Reproduction artifact
- contract: `research/experiment_contract_a2_sidon_base_20260718.md`
- impl: `experiments/ecdlp_prime_field/a2_sidon_factor_base.sage`
- result/audit: `.../a2_sidon_result.json`, `.../a2_sidon_verify.sage`
- ledger id: `SIDON-A2`

---

## Candidate: A3 — List-decoding (Guruswami–Sudan) generative membership backend

### One-sentence mechanism
Cast per-query decomposition as **curve-fitting / algebraic list-decoding**: fit a low-degree
bivariate `Q(x,y)` vanishing on the factor-base graph `{(x(F_i), x(R−F_i))}`, then **factor `Q`**
(Guruswami–Sudan / Roth–Ruckenstein) to *list* all decompositions in `Õ(output)` — instantiating
the P1434 "generative / sketch-based witness recovery" loophole and the RT-1476 backend.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (Literature Agent: **Zhang–Liu, IACR eprint 2018/795 / ProvSec 2019** already
marries Guruswami–Sudan list-decoding to ECDLP — but at *curve level* (whole ECDLP as a
minimum-weight-codeword problem on an elliptic AG-code, no complexity advantage shown, min-weight
NP-hard under RP-reduction). A3's object — a *factor-base-indexed evaluation code* whose decodable
codewords are the `A+C=R` decompositions — is materially different (local/relational vs global/structural)
and not covered; still distinct from the 07-17 incidence-reporting range-DS).

### Semantic fingerprint
- object: factor-base "received word" `{(a_i, b_i)} = {(x(F_i), x(R−F_i))}` over `F_p`.
- ops: EC arithmetic; bivariate interpolation; polynomial factorization.
- hidden structure: decompositions lie on a **low-degree algebraic curve** (the Semaev `S_2`/`S_3`
  locus) through the received points.
- discarded: exhaustive pair enumeration `B²`.
- retained: the low-degree fit and its factors (the codeword list).
- relation primitive: `A+C=R` = a point on the fitted curve that is *also* in the base.
- compression primitive: **interpolate-then-factor** (Sudan) instead of enumerate.
- rank mechanism: unchanged sparse factor-log matrix.
- descent: standard.
- dominant cost exponent: interpolation degree × factorization cost — object of measurement.

### Nearest ledger entries
1. **P1434 explicit-edge lower bound** — A3 lives in the *generative/sketch* regime P1434 explicitly
   leaves open. **Distinction: A3 targets the named loophole with a decoder.**
2. **07-17 A3 (incidence reporting)** — that builds a polynomial-partition *range-reporting DS*; A3
   here *interpolates a fitting polynomial and factors it* — no space partition. **Distinction:
   decode-by-factoring vs geometric cell DS.**
3. **ECFG-MX-1478 / P1513 (dense resultant/norm)** — A3 fits a *low-degree* curve to *sampled* base
   points, not the full elimination ideal. **Distinction: sampled low-degree fit vs full elimination.**
4. **M1 five-term relations** — same relation, different recovery. **Distinction: recovery subroutine.**
5. **RT-1476** — candidate backend. **Distinction: candidate vs gate.**

### Nearest literature
Sudan 1997; Guruswami–Sudan 1999; Roth–Ruckenstein 2000 (bivariate factorization decoding);
**Zhang–Liu 2018 (eprint 2018/795, "Solving ECDLP via List Decoding")** — curve-level AG-code /
min-weight-codeword reformulation, no rho-beating complexity, min-weight NP-hard under RP-reduction;
Cheng–Wan (RS-decoding ⇔ DLP hardness, `𝔽_{q^h}^×` not EC). Gap: no source treats *factor-base
decomposition search itself* as list-decoding over a factor-base-indexed evaluation code; whether the
base-restricted Semaev locus admits interpolation degree `o(B)`. **Reuse note:** Zhang–Liu's elliptic-code
construction is worth reading as the "code" for a factor-base-indexed version, and their min-weight
hardness obstruction may or may not transfer to the local decomposition problem.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Factor base** `B≈n^(1/5)`; precompute `{x(F_i)}`.
2. **Relation gen:** for query `R`, form the received word `{(x(F_i), x(R−F_i))}`; interpolate a
   bivariate `Q` of controlled `(1,k)`-weighted degree vanishing on it with multiplicity; factor `Q`;
   each `y=f(x)` factor whose `(x,f(x))` hits two base points is a relation.
3. **Witness/verify:** replay `A+C=R`.
4. **Relation probability:** `Θ(B)` supply.
5. **Matrix:** sparse full-rank target.
6–9: standard; the interpolation template is offline per curve.
### Cost model
Interpolation `= Õ(B·D²)` for fitting degree `D`; factorization `Õ(D^{ω})`. Beats birthday `B²` iff
`D=B^{α}` with `α<1` (RT-1476 `m≥4`). **Promotion** requires measured GS list size `Θ(1)` and
`D<B` across sizes. Compare explicit join `B^3` per pass.

### Why existing negatives do not kill it
Attacks the P1434 generative loophole with a decoder (not an explicit edge circuit, not a partition
DS); avoids MX-1478/P1513 (no dense elimination). New operation: **bivariate interpolate-and-factor
list-decoding of the Semaev locus.**

### Likely fatal obstruction
The Semaev `S_2`/`S_3` locus has *high* degree in the relevant variables, forcing GS interpolation
degree `D=Θ(L)` (or larger), so `Q` is as expensive as the full pair set and the list size approaches
`Θ(L)` — no output-sensitivity. The GS radius may also exceed the actual agreement, returning a
useless list. (Paired with the incidence/agreement side of D1.)

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`: fit `Q` at several weighted degrees; measure minimal `D` giving a nonempty
correct list, list size, and factorization time vs full scan. Positive control = points sampled from
a low-degree curve (GS should decode cheaply). Negative control = random points (no low-degree fit).
Fit `log D/log B` and list-size exponent.

### Quantitative promotion gate
Measured `D=B^{α}` with `α<1` (or `<3/2` in the `m=5` instantiation), list size `B^{o(1)}`, sparse
full-rank, across three sizes.

### Proof track
Theorem: the base-restricted Semaev locus is fit by a bivariate of weighted degree `o(B)`. Requires a
degree/agreement bound for `S_m` restricted to `B` points.

### Disproof track
Minimal `D=Θ(B)` at all sizes ⇒ scoped negative "the Semaev locus is not list-decodable below
birthday at `B=q^(1/5)`," refining P1447/incidence walls to a coding-theoretic statement.

### Reproduction artifact
- contract: `research/experiment_contract_a3_list_decode_20260718.md`
- impl: `experiments/ecdlp_prime_field/a3_gs_decode_membership.sage`
- result/audit: `.../a3_gs_result.json`, `.../a3_gs_verify.sage`
- ledger id: `LDEC-A3`

### Group B — representation changes

---

## Candidate: B1 — Canonical-lift (Serre–Tate) formal-group elliptic-log relation channel  *(DUPLICATE of batch2 `STATE-B2` — REJECTED; retained for fingerprint record)*

> **Reconciliation (see §0.1):** this is the *same mechanism* as batch2's B2 (`STATE-B2`), which
> already gave the settled-negative analysis (Voloch: Smart/Satoh–Araki/Semaev are one trace-1-only
> formal-group attack; for `n≠p` the Serre–Tate formal log sees only the trivial `p`-part → ~0 target
> bits). My "formal-log additivity" framing adds nothing batch2 did not already test. **Rejected as a
> duplicate; not the representation winner.** The section is preserved below for the fingerprint record;
> the barrier it feeds (D1) subsumes and is consistent with batch2 D2.

### One-sentence mechanism
Lift the ordinary curve to its **canonical lift `Ẽ/Z_p`** (Serre–Tate/Satoh), where the
**formal-group logarithm linearizes addition** (`log(P⊕Q)=log P + log Q`), and test whether the
reduction map `Ẽ(Z_p)→E(F_p)` plus the `p`-adic elliptic log exposes an *additive* relation channel
that no `F_p`-only representation has — a representation change of the base **ring**, not the
coordinates.

### Status
CONJECTURE

### Novelty classification
**DUPLICATE of batch2 `STATE-B2` (settled-negative).** LEDGER-NEW vocabulary but *not* mechanism-new
against batch2, which already tested the canonical-lift formal-log linearization and folded in Voloch's
trace-1-only unification. (Still distinct from xedni-2.0 (batch1 C3, global height) and tropical lift
(batch1 B3, valuation strata), but *not* from batch2 B2.) Retained only for the fingerprint record.

### Semantic fingerprint
- object: canonical lift `Ẽ/Z_p`, its formal group `Ê` and `p`-adic logarithm `log_Ê`.
- ops: Satoh-style canonical-lift + AGM/Newton lift; `p`-adic formal-log evaluation.
- hidden structure: **additivity of `log_Ê` on the kernel of reduction** (`Ê(pZ_p)≅(pZ_p,+)`).
- discarded: `F_p` field structure (moves to `Z_p`).
- retained: the `p`-adic additive coordinate of the reduction-kernel filtration.
- relation primitive: an *additive* relation `Σ a_i log_Ê(P̃_i) ≡ 0 (mod p^k)`.
- compression primitive: linearization of the group law by the formal log.
- rank mechanism: `Z/p^k`-linear dependence among lifted factor-base logs.
- descent: `p`-adic-log expression of the lifted target.
- dominant cost exponent: lift precision `k` vs usable additive information — object of measurement.

### Nearest ledger entries
1. **07-17 C3 (xedni-2.0 global height lift)** — number-field lift, MW-rank/height obstruction; B1 is
   a `Z_p` lift using the formal log. **Distinction: local (`Z_p`, formal log) vs global (`ℚ̄`, height).**
2. **07-17 B3 (tropical p-adic lift)** — uses valuation *strata* of the Semaev variety; B1 uses the
   *formal-group logarithm's additivity*, not tropical combinatorics. **Distinction: additive log vs
   valuation polytope.**
3. **NR-022 / scalar Weil restriction** — restriction within char `p`; B1 leaves char `p` by lifting.
   **Distinction: char-0 lift vs `F_p`-split.**
4. **M5 oriented-CM (Satoh appears for isogeny/counting)** — the canonical lift is used there for
   *counting/isogeny*, never for DLP relations. **Distinction: DLP channel vs counting.**
5. **B-n=1 collapse** — B1 sidesteps polynomial-system solving entirely (no Semaev). **Distinction:
   additive channel, no `S_m` system.**

### Nearest literature
Serre–Tate canonical lift; Satoh 2000 (`p`-adic point counting via canonical lift); Mestre AGM;
Silverman 1994 (formal groups, `p`-adic elliptic log). **Literature Agent, confirming POSSIBLY NOVEL
for general `n`:** every lifting-for-DLP paper found is degenerate or refuted — **Yasuda, WAIFI 2010**
("The ECDLP over the `p`-adic field and formal groups") handles only the *anomalous* `n=p`
(Smart/Satoh–Araki) case; **arXiv:1702.07107** is a *non-canonical* lift restricted to safe-prime order;
**Silverman's 4-scenario lifting survey (LNCS 5808, ~2009)** enumerates the canonical-lift scenario and
states none has solved ECDLP; xedni (Silverman 1998; refuted by Jacobson–Koblitz–Silverman–Stein–Teske
2000) is the *global-height* failure mode, structurally different from a *local* formal-log channel. Gap:
no work uses the Serre–Tate canonical-lift formal log as a DLP relation source for a *generic ordinary
prime-order* curve (`n` arbitrary prime, not `n=p`, not safe-prime). **Next lit step:** read Silverman's
survey for the stated reason each scenario "does not obviously work" — it may already informally rule out
the general-`n` channel.

### Target family
Ordinary prime-order `E/F_p` (ordinarity is required for a canonical lift); excluded: supersingular
(no canonical lift), and the usual specials.

### Full algorithmic path
1. **Factor base:** points `F_i∈E(F_p)`; compute their canonical Teichmüller lifts `P̃_i∈Ẽ(Z_p)` to
   precision `p^k` (Satoh/AGM).
2. **Relation generation:** evaluate `ℓ_i = log_Ê(P̃_i) ∈ Z_p`; search for `Z/p^k`-linear
   dependencies `Σ a_i ℓ_i ≡ 0`, which (if they descend) give `F_p` relations among the `F_i`.
3. **Witness/verify:** reduce the lifted relation mod the group order; replay on `E(F_p)`.
4. **Relation probability:** governed by how much *scalar* information survives reduction — **measured**.
5. **Matrix:** `Z/p^k` exponent matrix.
6. **Calibration/descent:** express the lifted target via its `p`-adic log; reduce.
7–9: precision `k` is the memory/time driver; offline lift, online log-search.

### Cost model
Cost `= B·(canonical-lift cost at precision k) + (lattice search for additive relations)`. The lift
costs `Õ(k^2)` field ops per point (Satoh). **Promotion requires** that a precision `k=O(log q)`
suffices to extract additive relations carrying the *order-n* discrete log — i.e. the formal log's
top-degree coefficient couples to the mod-`n` scalar. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Not a coordinate reparametrization (leaves `F_p`), not a number-field lift (local, formal log), not a
Semaev system. New operation: **canonical-lift formal-group logarithm as an additive DLP coordinate.**

### Likely fatal obstruction (paired with D3)
**The reduction map annihilates exactly the DLP information.** `log_Ê` linearizes addition on the
*kernel of reduction* `Ê(pZ_p)`, which is `p`-torsion-free and reduces to `O∈E(F_p)`; the mod-`n`
scalar lives in `E(F_p)`, orthogonal to the formal-log filtration. The canonical lift's Frobenius
determines the *order/trace* (why Satoh counts points), **not** per-target logs — the same class-function
wall that sank 07-17 C2 (Lattès). Almost certainly no scalar leakage; B1's whole bet is that the
Teichmüller lift's higher `p`-adic digits carry residual target-dependent information.

### Minimal falsifying experiment
For toy ordinary `E/F_p`, `p≈2^12,2^16,2^20` (lift is expensive; small `p`): lift `[k]G` for known
`k`; compute `log_Ê([k]G)` to precision `p^3`; test whether any `p`-adic digit is a *non-constant
function of `k`* (mutual information with `k mod n`) beyond the trivial `[k]G` group value. Positive
control = the multiplicative group `(Z/p^k)^*` where the `p`-adic log *does* linearize the DLP
(should show full leakage). Negative control = a random labelling. Measure `I(digit; k mod n)`.

### Quantitative promotion gate
A `p`-adic-log coordinate with mutual information `Ω(log n)` about `k mod n`, extractable at precision
`k=O(log q)`, yielding sparse `Z/p^k` relations of rank `≥B−1` across three sizes. (Expected to fail
— but a *clean* refutation precisely locates where the canonical lift stops leaking, which is itself
a load-bearing barrier the ledger lacks.)

### Proof track
Theorem: the canonical-lift formal log carries `Ω(log n)` bits about the mod-`n` scalar. Would
contradict the "class-function" heuristic; if true, revolutionary.

### Disproof track (see D3)
Prove the formal-log filtration is `n`-torsion-orthogonal (carries only order/trace) ⇒ a clean
"canonical-lift reduction annihilates the scalar" barrier, closing the `p`-adic-additive lane the way
JKSST closed xedni.

### Reproduction artifact
- contract: `research/experiment_contract_b1_canonical_lift_20260718.md`
- impl: `experiments/ecdlp_prime_field/b1_canonical_lift_log.sage`
- result/audit: `.../b1_canlift_result.json`, `.../b1_canlift_verify.sage`
- ledger id: `CANLIFT-B1`

---

## Candidate: B2 — Cartier–Manin / crystalline linear-operator representation of translation

### One-sentence mechanism
Represent translation-by-`P` as a **linear operator on the de Rham / rigid (Monsky–Washnitzer)
cohomology `H^1` of `E`** (where Frobenius already acts linearly via the Cartier–Manin/Hasse–Witt
matrix), and test whether the eigen-decomposition of the *translation* operator exposes a per-target
coordinate that linearizes descent — a representation change of the algebraic **object** (point →
cohomology class).

### Status
CONJECTURE

### Novelty classification
**DUPLICATE of batch2 D2 (crystalline / Cartier–Manin order-only barrier).** Batch2 already established,
as a theorem-grade barrier, that crystalline/Cartier–Manin data is a class function of Frobenius carrying
only order/trace (genus-1 Hasse–Witt is `1×1`, Achter et al. arXiv:1710.10726). The ledger uses
Cartier–Manin only as a cover-transfer certifier (PO9/PO77). B2 is therefore **not mechanism-new**; it is
a restatement confirming batch2 D2 and feeding this run's D1. Retained for the fingerprint record.

### Semantic fingerprint
- object: `H^1_{dR}(E/F_p)` (or rigid `H^1`), a 2-dim `F_p`-space; translation `τ_P^*` acting on it.
- ops: cohomology basis `{du/y, u du/y}`; Cartier operator; pullback by translation.
- hidden structure: whether `τ_P^*` is *nontrivial* on `H^1` and encodes `P`.
- discarded: the group law's nonlinearity.
- retained: a linear operator per point.
- relation primitive: an eigen/linear relation among `{τ_{P_i}^*}`.
- compression primitive: 2-dimensional linear algebra.
- rank mechanism: rank of the operator family — object of measurement.
- descent: (speculative) linear inversion of `τ_{[k]G}^*`.
- dominant cost exponent: undefined until the operator's `P`-dependence is measured.

### Nearest ledger entries
1. **Ledger Cartier–Manin rows (PO9/PO77 cover certifiers)** — used to *certify Jacobian
   correspondences*, never as a DLP operator. **Distinction: DLP eigenproblem vs cover certificate.**
2. **07-17 C2 (Lattès transfer operator, rejected incomplete)** — both are operator-theoretic; C2
   used the `[ℓ]`-map's transfer operator on `P^1`, B2 uses translation on `H^1`. **Distinction:
   cohomology of `E` vs dynamics on the x-line.**
3. **M5 Frobenius/SEA** — Frobenius on `H^1` gives *order*; B2 asks whether *translation* gives more.
   **Distinction: translation operator vs Frobenius.**
4. **B-Dreg** — B2 abandons polynomial-system solving. **Distinction: linear-algebra representation.**
5. **RT-1476** — different lane (not a membership backend).

### Nearest literature
Cartier–Manin; Kedlaya 2001 (`p`-adic cohomology point counting — *counting only*); Monsky–Washnitzer;
Manin's theorem on the Hasse–Witt matrix. **Literature Agent (decisive): Achter et al., arXiv:1710.10726**
confirms the genus-1 Hasse–Witt / Cartier–Manin matrix is a `1×1` scalar, and Frobenius on the rank-2
`H^1_dR(E)` has char. poly `X²−tX+p` — *exactly the point-counting datum*. Coleman/Kim `p`-adic
cohomology is used only for number-field rational-point finding, never finite-field DLP. Gap: no mechanism
by which translation-by-`P` (a torsor/point-level operation) acts on this curve-level rank-2 object
without collapsing to the known `X²−tX+p` representation. B2 is a *barrier in disguise* — its value is a
clean, citable "cohomology of `E` is translation-blind" lemma (feeds D1).

### Target family
Ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path (INCOMPLETE unless the operator is non-trivial)
1. build `H^1_{dR}(E)` basis; compute the Cartier–Manin matrix.
2. compute `τ_P^*` on `H^1` for factor-base points; **check whether it depends on `P` at all.**
3. **Stages 3–9 depend on step 2:** if `τ_P^*=id` for all `P` (expected — translations act trivially
   on `H^1`), there is *no* relation channel and the candidate is **INCOMPLETE / barrier**. Only if a
   nontrivial `P`-dependence appears (e.g. via a *non-invariant* differential or a jet-thickened
   `H^1` of `E×E`) do relation/rank/descent stages become definable.

### Cost model
Undefined until step 2. If `τ_P^*=id`, cost is irrelevant (no channel). A rejection criterion.

### Why existing negatives do not kill it
Orthogonal to every measured lane, but *because* it may not be an algorithm — its honest role is a
**negative-theory probe**: does any cohomological operator see a point's *translation class*?

### Likely fatal obstruction
Translations act trivially on `H^1` (standard); the point-dependent information lives in `H^0` of a
torsor / the Albanese, not in `H^1` of `E`. Almost certainly no per-target coordinate. This is a
class-function wall analogous to B1/D3 and 07-17 C2.

### Minimal falsifying experiment
Theory-Agent + toy check: for `E/F_p`, `p≈2^12,2^16`, compute `τ_P^*` on `H^1` for 100 points; test
`τ_P^*=id` exactly. Positive control = a construction where translation *does* act (e.g. on `H^1` of a
`G_a`-torsor / the jet space `E(F_p[ε])`, connecting to 07-17 B1). Negative control = plain `H^1(E)`.

### Quantitative promotion gate
Not eligible until step 2 exhibits a nontrivial, `P`-encoding operator with a defined relation/descent
path. **Rejected at ranking on incompleteness** unless the toy check surprises; retained as a Theory
formalization / barrier seed.

### Proof/disproof track
Disprove: prove `τ_P^*=id` on `H^1(E)` for all `P` (translations homotopic to identity) ⇒ a clean
"cohomology of `E` is translation-blind" barrier, unifying with B1/D3 and 07-17 C2 into a single
class-function no-leakage principle.

### Reproduction artifact
- note: `research/b2_cohomology_translation_formalization_20260718.md`
- impl: `experiments/ecdlp_prime_field/b2_cartier_translation_check.sage`
- ledger id: `COHO-B2`

---

## Candidate: B3 — Discrete-Fourier / dual-group factor-base indicator

### One-sentence mechanism
Represent the factor base by its **indicator function on the cyclic group `Z/n`** (the "dual"
side of `E(F_p)≅Z/n`) and use a **partial discrete Fourier / additive-character estimate** — computed
from x-coordinate statistics *without knowing logs* — to detect a spectral bias whose inverse
transform reveals log relations; a representation change of the **domain** (point set → spectrum).

### Status
CONJECTURE

### Novelty classification
NOVELTY-UNVERIFIED (Fourier analysis on `Z/n` underlies Pohlig–Hellman and Shor; a *log-free* partial
character estimate of an EC factor base is not in the ledger; the ledger's character work (NR-1475) is
*multiplicative residual buckets on pairs*, not a group-dual spectral transform).

### Semantic fingerprint
- object: indicator `1_S: Z/n → {0,1}` of factor-base logs `S={log F_i}`, and its DFT `\hat{1_S}`.
- ops: additive characters `χ_a(k)=e(ak/n)`; character sums estimated via x-coordinate proxies.
- hidden structure: **spectral concentration** of `\hat{1_S}` (a bias ⇒ additive structure ⇒ relations).
- discarded: the geometric point representation.
- retained: the character spectrum.
- relation primitive: a large Fourier coefficient ⇒ an approximate arithmetic progression in `S` ⇒
  a relation `Σ a_i F_i = O`.
- compression primitive: sparse spectrum (few large coefficients).
- rank mechanism: rank of the AP/relation structure detected spectrally.
- descent: express the target's log via the detected spectral structure.
- dominant cost exponent: how cheaply a large character sum can be *estimated without logs* — the crux.

### Nearest ledger entries
1. **ECFG-NR-1475 (pair-residual character buckets)** — *multiplicative* character on *pair residuals*;
   B3 is an *additive* character on the *group dual `Z/n`*. **Distinction: group-dual DFT vs residual bucket.**
2. **M6 ECFG functional graph** — a combinatorial statistic of `k→x(kB)`; B3 is its *spectral* dual.
   **Distinction: Fourier transform vs graph statistic.**
3. **B-preproc** — any spectral precompute must beat `S·T²=Ω̃(εq)`.
4. **07-17 C1/C2 (isogeny/Lattès)** — unrelated. **Distinction: dual-group harmonic analysis.**
5. **Pohlig–Hellman (implicit baseline)** — DFT on `Z/n` for *smooth* `n`; B3 targets *prime* `n`.
   **Distinction: prime-order spectral bias vs smooth-order factorization.**

### Nearest literature
Pohlig–Hellman 1978; Shor 1994 (period finding — the quantum dual); Gauss sums / Deligne bounds
(character-sum sizes); Green–Tao (Fourier/AP). Gap: for *prime* `n` the DFT has no cheap classical
handle; whether a *log-free x-coordinate estimator* of a character sum exists is entirely open.

### Target family
Ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path (path validity hinges on the estimator)
1. **Factor base** `B`; the (unknown) log-set `S⊂Z/n`.
2. **Relation gen:** estimate character sums `\hat{1_S}(a)=Σ_{P∈S} χ_a(log P)` for many `a`, using an
   x-coordinate proxy for `χ_a(log P)` that does **not** require `log P`; a large `|\hat{1_S}(a)|`
   flags additive structure ⇒ a relation.
3. **Witness/verify:** convert the flagged structure to an explicit `Σ a_i F_i=O`; replay.
4. **Relation probability / rank:** measured from detected spectral peaks.
5–9: standard once relations exist.

### Cost model
Dominated by the **estimator**: if `χ_a(log P)` can be approximated in `poly(log q)` from `x(P)` (no
log), the transform is cheap and any bias is exploitable; if not, computing even one character sum
needs the logs (circular) or `Θ(n)` work. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Not a pair-residual bucket (group-dual, additive), not a graph statistic (spectral). New operation:
**log-free partial DFT of the factor-base indicator on the group dual.**

### Likely fatal obstruction (paired with D1)
For prime `n`, a random-looking `S` has a **flat spectrum** (`|\hat{1_S}(a)|≈sqrt(B)` for all `a≠0`,
no concentration), and — decisively — there is **no known log-free estimator** of `χ_a(log P)`: the
additive character on `Z/n` is *defined* through the discrete log, so estimating it is DLP-hard
(circularity). Deligne-type bounds show EC character sums are square-root-cancelling (no exploitable
bias). This is the deepest wall; B3's bet is that a *non-generic* curve invariant provides a partial,
biased estimator.

### Minimal falsifying experiment
For toy prime-order `E/F_p`, `p≈2^16,2^20,2^24` where logs are computable by brute force (to *check*,
not to run the attack): compute the true spectrum `\hat{1_S}` for interval / rational-map / subgroup
bases; measure peak concentration vs a random subset of `Z/n`. Separately, test any candidate log-free
estimator's correlation with the true `χ_a(log P)`. Positive control = a base that *is* an AP in `Z/n`
(should show a sharp peak). Negative control = random `S` (flat).

### Quantitative promotion gate
(i) A structured base with spectral concentration `Ω(B^{1/2+c})` in `o(B)` coefficients, **and**
(ii) a log-free estimator correlating `Ω(1)` with `χ_a(log P)` at `poly(log q)` cost — both across
three sizes. Absent (ii), the candidate is a barrier, not an attack.

### Proof track
Theorem: some public curve invariant yields a `poly(log q)` estimator of an additive character on the
DLP. Would essentially be a DLP break; extraordinary evidence required.

### Disproof track (see D1)
Prove no log-free additive-character estimator exists (the character *is* the log) and that
Deligne-bounded EC sums are bias-free ⇒ a clean "group-dual spectrum is DLP-locked" barrier.

### Reproduction artifact
- contract: `research/experiment_contract_b3_dual_fourier_20260718.md`
- impl: `experiments/ecdlp_prime_field/b3_dft_indicator.sage`
- result/audit: `.../b3_dft_result.json`, `.../b3_dft_verify.sage`
- ledger id: `DFT-B3`

---

## Candidate: B4 — Semaev summation-tensor border rank / bilinear complexity  *(REPRESENTATION WINNER)*

### One-sentence mechanism
Represent the `m`-term Semaev relation as a **multilinear form (tensor) `T_{S_m}`** and measure its
**border rank / bilinear complexity** (Bini/Strassen-style), so that *batched* membership evaluation over
the factor base runs via an approximate bilinear algorithm in `Õ(borderrank)` multiplications — a
representation change of the *algebraic-complexity object* distinct from batch1's *separator*-rank
(a different tensor invariant) and from every density/degree measurement in the ledger.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (verified absent from ledger and *both* 07-17 batches: `border rank`/`bilinear
complexity`/`Strassen`/`Bini`/`CP-rank` = 0 hits in each. Border/CP rank is a *different* tensor-complexity
invariant than batch1 B2's separator/Schmidt rank — a tensor can be high-separator-rank yet low-border-rank
and vice versa — so this is mechanism-new, not a rename).

### Semantic fingerprint
- object: the symmetric summation tensor `T_{S_m}` of `S_m(x_1,…,x_m)` (multilinear in a monomial lift).
- ops: EC arithmetic to build local factors; approximate/exact bilinear algorithm (Bini scheme).
- hidden structure: **border rank `R̲(T_{S_m})`** — the bilinear complexity of evaluating `S_m`.
- discarded: dense monomial coefficients (NR-1477) and contraction-order/treewidth (batch1 B2).
- retained: the tensor's minimal (approximate) rank-1 decomposition.
- relation primitive: five/`m`-term `A+C=R` membership as one evaluation of the multilinear form.
- compression primitive: rank-`R̲` bilinear algorithm amortized over the `Θ(B)`-shift batch.
- rank mechanism (linear-algebra downstream): unchanged sparse factor-log matrix.
- descent: standard one-factor online descent (shared backend).
- dominant cost exponent: `log R̲(T_{S_m}) / log L` amortized over the batch — **the object of measurement**.

### Nearest ledger entries
1. **batch1 B2 (tensor-train / separator rank)** — measures Schmidt rank across a *cut* / contraction
   treewidth; B4 measures **border/CP rank of the whole tensor** (bilinear complexity). **Distinction:
   two inequivalent tensor invariants; a low-treewidth network can still have high border rank and
   conversely.**
2. **ECFG-NR-1477 (dense serial-S3 state `L^1.675`)** — density of a state polynomial; B4 measures
   *multilinear rank*, orthogonal to density. **Distinction: rank vs density.**
3. **ECFG-MX-1478 / P1513 (dense resultant/norm)** — B4 never forms the resultant; it decomposes the
   evaluation tensor. **Distinction: bilinear decomposition vs elimination.**
4. **batch2 A3 (Kedlaya–Umans membership)** — KU is fast modular composition/multipoint evaluation
   (a *black-box* evaluation speedup); B4 exploits the *tensor structure* of `S_m` for a Bini-style
   approximate bilinear algorithm. **Distinction: structured bilinear decomposition vs black-box KU.**
5. **RT-1476** — B4 is a concrete membership backend candidate: if `R̲=L^{α}` with `α<1` (`m≥4`) it
   meets the gate. **Distinction: candidate vs gate.**

### Nearest literature
Strassen 1969 (bilinear complexity); Bini 1980 (border rank / approximate bilinear algorithms);
Bürgisser–Clausen–Shokrollahi (algebraic complexity theory); Landsberg (tensor border rank). IC: none —
no border-rank analysis of Semaev/summation tensors exists. Gap: the border rank of `T_{S_m}` is a
load-bearing, uncomputed number.

### Target family
Random ordinary prime-order short-Weierstrass `E/F_p`, `p` prime, `n=#E` prime, `j∉{0,1728}`; excluded
specials as A1.

### Full algorithmic path
1. **Factor base** `B≈n^(1/5)`; build the multilinear lift of `S_m` and its local rank-1 factors.
2. **Relation generation:** compute (offline) a border-rank-`R̲` approximate bilinear scheme for `T_{S_m}`;
   online, evaluate membership for each shift `R` and factor slot via the scheme, batched over `Θ(B)` shifts;
   nonzero evaluation ⇒ decomposition, recovered from the scheme's witness.
3. **Witness/verify:** replay exact EC additions `A+C=R`.
4. **Relation probability:** `Θ(B)` supply.
5. **Matrix:** `Θ(B)×B` sparse full-rank target.
6–9: standard; the bilinear scheme is curve-independent (offline), the local factors per-curve.

### Cost model
Batched membership `= Õ(R̲(T_{S_m})) · (field-op cost)` amortized over `Θ(B)` shifts. **Promotion iff**
`R̲=O(L^{α})` with `α<1` (`m≥4`) / `α<3/2` (`m=5`), giving total relation-gen `<n^{1/2}`; approximate
(border-rank) schemes must have precision cost `O(polylog)` over `F_p` (degeneration order small). Compare
rho `n^0.5`; explicit join `n^0.6`; batch1-B2 separator-rank target `r<L^{1/2}`.

### Why existing negatives do not kill it
Measures a **new invariant** (border/CP rank) never computed for Semaev; distinct from separator rank
(batch1 B2), density (NR-1477), and KU black-box evaluation (batch2 A3). New operation: **approximate
bilinear (Bini) decomposition of the summation tensor.**

### Likely fatal obstruction (paired with D3)
Generic tensors have **maximal border rank**; the symmetric near-generic summation tensor is very likely
`R̲=Θ(L^2)` (or the `m`-linear analogue), giving no gain — and *border* rank over `F_p` may incur a
degeneration-order (precision) blow-up that erases any constant. This is exactly what the experiment and
the D3 (now border-rank-extended) barrier measure.

### Minimal falsifying experiment
For `p≈2^20,2^24,2^28`, `m=4,5`, seeds `20260718..20260723`: bound `R̲(T_{S_m})` numerically (Bini
degeneration / flattening-rank lower bounds + explicit small schemes) vs the trivial `Θ(L^2)`; measure
degeneration order. Positive control = a deliberately low-border-rank toy tensor (matrix-mult-like).
Negative control = a random symmetric tensor of matched dimension (maximal rank). Fit `log R̲/log L`.

### Quantitative promotion gate
Measured `R̲=L^{α}` with `α<1` (`m=4`) and bounded degeneration order across all three sizes, **and** a
working `R̲`-scheme recovers `≥B−1` sparse-independent relations and blind targets. Correctness alone is
*not* the gate.

### Proof track
Theorem: `R̲(T_{S_m})=O(L^{1−ε})`. Would follow from a structured (Toeplitz/symmetric) low-border-rank
decomposition of the EC summation multilinear form.

### Disproof track (see D3-extended)
Flattening/substitution lower bound `R̲=Ω(L^{1+c})` ⇒ closes the tensor-complexity loophole for both the
separator-rank (batch1 B2) and border-rank views, a strong unified statement.

### Reproduction artifact
- contract: `research/experiment_contract_b4_border_rank_20260718.md`
- impl: `experiments/ecdlp_prime_field/b4_semaev_border_rank.sage`
- result/audit: `.../b4_border_result.json`, `.../b4_border_verify.sage`
- ledger id: `BORDER-B4`

### Group C — high-risk speculative

---

## Candidate: C1 — Approximate-homomorphism stability of the x-map (Bogolyubov–Ruzsa)  *(HIGH-RISK WINNER)*

### One-sentence mechanism
Ask whether a **positive-density subset** of `E(F_p)` on which `x(A+B)` is *close* to a **bilinear/affine
function** of `x(A),x(B)` exists, using **quantitative additive-combinatorics stability** (Bogolyubov–Ruzsa /
Balog–Szemerédi–Gowers): if the EC addition law is "approximately linear" on a large set, that set is a
cheap relation engine — the exact question the ledger's sum-product wall assumes away but never *stability-tests*.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (Literature Agent: **arXiv:2510.03828 (2025), "Additive Rigidity for x-Coordinates
of Rational Points on Elliptic Curves,"** *proves* — via genuine Freiman/BSG/Bogolyubov–Ruzsa machinery —
that positive-density x-coordinate sets cannot sit in low-complexity generalized APs, but **over number
fields** (MW/archimedean-height regime), not `F_p`; and **Ahmadi–Shparlinski (arXiv:0806.0640)** gives a
sum-product dichotomy for `x(E)` over `F_p` — direct counter-evidence in the target regime. No source runs
the general small-doubling test on `x:E(F_p)→F_p`. So the *machinery* and *counter-evidence* exist; the
specific `F_p` transfer is unexecuted).

### Semantic fingerprint
- object: the addition law graph `Γ={(x(A),x(B),x(A+B))}⊂F_p^3`.
- ops: EC arithmetic; additive-energy / BSG computation on sampled sets.
- hidden structure: **existence of a large approximately-affine piece** of `Γ`.
- discarded: exact algebraic form of the addition law.
- retained: the density and structure of the near-linear set.
- relation primitive: on the near-linear set, `A+C=R` becomes an (approximate) *linear* condition,
  cheaply invertible.
- compression primitive: linearization on a positive-density subset.
- rank mechanism: relations from the linear piece.
- descent: linear inversion on the structured set.
- dominant cost exponent: density × linearity-defect of the largest near-affine set — object of measurement.

### Nearest ledger entries
1. **Ahmadi–Shparlinski sum-product wall (P1447, `|x(F)+x(F)|·|x(F+F)|`)** — a *lower bound* on
   sumset expansion; C1 runs the *dual stability question* (is there a large non-expanding piece?).
   **Distinction: stability/inverse theorem vs expansion bound.**
2. **B-Dreg** — C1 does not solve `S_m`; it looks for a subset where no solving is needed.
   **Distinction: approximate-linearity vs exact degree.**
3. **ECFG "hash-like sumset" rows** — those assert `x(E)` sumsets look random *on average*; C1 asks
   about the *largest structured exception*. **Distinction: worst-case set vs average.**
4. **07-17 A2/A3** — unrelated (EDS / incidence). **Distinction: additive-energy stability.**
5. **B-explicit-edge (P1434)** — C1's structured set would be a *non-explicit generative* witness
   source (the P1434 loophole). **Distinction: statistical structure, not explicit edges.**

### Nearest literature
Bogolyubov–Ruzsa (Sanders 2012 bounds); Balog–Szemerédi–Gowers; **Ahmadi–Shparlinski arXiv:0806.0640
(EC sum-product over `F_p`)**; **arXiv:2510.03828 (2025), additive rigidity for x-coordinates over number
fields** — a ready-made BSG/Bogolyubov–Ruzsa proof template in the *wrong* regime; Bourgain–Glibichuk–
Konyagin. Gap: no small-doubling/inverse-theorem analysis of `x:E(F_p)→F_p`. **Highest-value next step
(from Lit Agent):** have the Theory Agent port arXiv:2510.03828's proof to `F_p` — check which steps use
archimedean height (non-transferable) vs pure group-law identities (transferable). That single task decides
whether C1/D2 becomes a `RESTRICTED THEOREM` (negative, `F_p` rigidity) or stays `OPEN`, *without running
the experiment*.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1 (special curves might *have* structure —
they are the positive control, not the target).

### Full algorithmic path
1. **Sample** `m≈B^2` random triples `(x(A),x(B),x(A+B))`.
2. **Measure additive energy / BSG** to find the largest subset `T` where `x` is `δ`-approximately
   affine; extract the approximate linear form.
3. **Relation gen:** on `T`, solve `A+C=R` by the linear form (cheap); verify exactly on `E`.
4. **Relation probability:** = density of `T` × correctness of the linear form — **measured**.
5. **Matrix:** relations from `T`; rank measured.
6–9: standard; the structured set is found offline per curve.

### Cost model
If `|T|=Θ(B^2)` with linearity-defect `o(1)`, relations come at `poly(log q)` per hit → total
`n^{1/5+o(1)}`. If `|T|=B^{o(1)}` (only trivial structure), no gain. Compare rho `n^0.5`.

### Why existing negatives do not kill it
The ledger has the *bound* (expansion) but never the *inverse theorem* (structure of the exception);
BSG/Bogolyubov–Ruzsa is a genuinely new operation. New operation: **additive-energy stability search
for an approximately-linear piece of the EC addition law.**

### Likely fatal obstruction (paired with D1)
Ahmadi–Shparlinski-type sum-product bounds likely imply the *inverse* statement too: any large subset
of `x(E)` has near-maximal additive energy defect (no dense linear piece), because a dense linear piece
would contradict square-root cancellation of EC character sums. Expected: `|T|=B^{o(1)}`, structure
trivial. C1's bet is that *some* ordinary curve, or some coordinate (not `x` but a rational function),
admits a dense near-affine set.

### Minimal falsifying experiment
For `p≈2^18,2^22,2^26`, sample triples; run BSG/energy to bound the largest `δ`-affine set for several
`δ`. Positive control = an anomalous or `j∈{0,1728}` curve with extra automorphisms (should show more
structure). Negative control = a random ordinary curve. Fit `log|T|/log B` vs `δ`.

### Quantitative promotion gate
Largest near-affine set has density `|T|=B^{1+c}` (superlinear structure) with defect small enough that
its relations reach rank `≥B−1`, across three sizes — a measured structural exponent, not a constant.

### Proof track
Theorem: some ordinary `E/F_p` has a positive-density approximately-affine `x`-subset. Would contradict
the strong sum-product heuristic; if true for a *family*, a real channel.

### Disproof track (see D1)
Measured `|T|=B^{o(1)}` uniformly ⇒ an *inverse-theorem* strengthening of Ahmadi–Shparlinski: "no dense
approximately-linear piece of `x(E)`," turning the expansion bound into a structural barrier the ledger
can cite against all future "structured subset" ideas.

### Reproduction artifact
- contract: `research/experiment_contract_c1_approx_hom_stability_20260718.md`
- impl: `experiments/ecdlp_prime_field/c1_bsg_stability.sage`
- result/audit: `.../c1_bsg_result.json`, `.../c1_bsg_verify.sage`
- ledger id: `STAB-C1`

---

## Candidate: C2 — Kloosterman / exponential-sum-biased importance-sampling relation generator

### One-sentence mechanism
Use a **computable elliptic exponential sum (Kloosterman-type) bias** to **importance-sample** the
pair-sum search toward regions of higher relation density, so that the *expected number of attempts per
relation* drops below the uniform `1/Prob` — a biased generator, not a new relation.

### Status
CONJECTURE

### Novelty classification
**ADJACENT to batch2 C3 (its high-risk winner, "elliptic character-sum bias relation oracle").** C2's
sub-mechanism is distinct — an importance-sampling *weight* on the pair generator vs batch2 C3's
character-sum bias on the relation *count/oracle* — but both rest on the **same Deligne-equidistribution
obstruction**, so C2 is not independently novel and is **not promoted**. Demoted; retained to record the
distinction. Defer to batch2 C3 as the canonical character-sum probe.

### Semantic fingerprint
- object: pair-sum distribution over the factor base; an auxiliary character/Kloosterman sum weight.
- ops: EC arithmetic; evaluation of a short character sum as a sampling weight.
- hidden structure: **non-uniformity of relation density** across the base, if any.
- discarded: uniform sampling.
- retained: a computable importance weight.
- relation primitive: `A+C=R` membership (unchanged).
- compression primitive: variance reduction via importance sampling.
- rank mechanism: unchanged sparse factor-log matrix.
- descent: standard.
- dominant cost exponent: attempts-per-relation under the biased sampler — object of measurement.

### Nearest ledger entries
1. **M6 selectors / ECFG-N001..061** — post-hoc selectors that fail prospectively; C2 uses a *provable*
   character-sum weight, not a trained selector. **Distinction: analytic bias vs learned gate.**
2. **ECFG-NR-1475 (character buckets)** — buckets *partition*; C2 *weights the sampler*. **Distinction:
   importance weight vs bucket.**
3. **B-explicit-edge (P1434)** — C2 is a generative sampler, but must beat the uniform generator's
   exponent, not just reshuffle it. **Distinction: variance reduction vs edge circuit.**
4. **07-17 candidates** — none use exponential-sum biasing. **Distinction: analytic importance sampling.**
5. **RT-1476** — C2 could lower the constant in a backend but must change the *exponent* to matter.

### Nearest literature
Kloosterman sums; Deligne (Weil bounds); Bombieri; Shparlinski (character sums over EC points);
Kohel–Shparlinski (distribution of EC points). Gap: no importance-sampling IC generator; the sums are
studied for *equidistribution* (which argues the bias is `O(sqrt)` small).

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. **Factor base** `B`; precompute a Kloosterman/character weight `w(F_i)` per point.
2. **Relation gen:** sample pairs with probability `∝ w(F_i)w(F_j)`; test `A+C=R`.
3–9: standard; the weight is offline per curve.

### Cost model
Uniform sampling needs `≈q/B^{m-1}` attempts per relation. Importance sampling helps by a factor
`= 1/(1 - variance-reduction)`, which is a **constant** unless the relation density is *polynomially*
non-uniform. Deligne bounds say EC character sums are square-root-small ⇒ the density is near-uniform
⇒ only constant gain. **Promotion requires** a measured *polynomial* non-uniformity. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Analytic (provable) weight, not a trained selector; never tried. New operation: **exponential-sum
importance weighting of the relation sampler.**

### Likely fatal obstruction
Equidistribution: Weil/Deligne bounds force relation density to be uniform up to `O(1/sqrt(q))`, so
importance sampling yields only a *constant-factor* improvement — never an exponent change. (This is the
generic reason biasing cannot beat rho, and the honest prior.)

### Minimal falsifying experiment
For `p≈2^18,2^22,2^26`: measure relation-density variance across the base and the attempts-per-relation
under uniform vs Kloosterman-weighted sampling. Positive control = a curve with engineered non-uniformity.
Negative control = uniform. Fit attempts-per-relation exponent.

### Quantitative promotion gate
Biased sampler lowers the *attempts-per-relation exponent* (not constant) across three sizes. Almost
certainly fails; a clean failure quantifies EC relation-density equidistribution.

### Proof track
Theorem: relation density is polynomially non-uniform for some ordinary `E`. Would contradict
equidistribution; unlikely.

### Disproof track
Measured constant-only gain ⇒ "exponential-sum biasing cannot change the IC relation exponent," a
reusable statement that closes the entire importance-sampling lane.

### Reproduction artifact
- contract: `research/experiment_contract_c2_kloosterman_sampler_20260718.md`
- impl: `experiments/ecdlp_prime_field/c2_biased_sampler.sage`
- result/audit: `.../c2_kloos_result.json`, `.../c2_kloos_verify.sage`
- ledger id: `KLOOS-C2`

---

## Candidate: C3 — CM ideal-factorization index calculus (endomorphism-ring class group)

### One-sentence mechanism
For an ordinary curve with `End(E)=O` in an imaginary quadratic field, map factor-base points to
**ideals of `O`** via the CM/Kronecker correspondence and build relations from **prime-ideal
factorizations of small norm** — an index calculus in the endomorphism-ring class group rather than
on the curve, seeking a genuinely *multiplicative* smoothness structure the curve itself lacks.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (CM theory and class-group index calculus are known; the *point→ideal* relation
map for DLP is the open, likely-circular step; distinct from isogeny/class-group-action work
(07-17 C1, ISO-AR), which acts on *curves*, not on the DLP scalar).

### Semantic fingerprint
- object: `End(E)=O`, `Cl(O)`, prime ideals of small norm.
- ops: CM correspondence, ideal factorization, form composition (Gauss).
- hidden structure: **multiplicative prime-ideal factorization** (a real smoothness notion).
- discarded: the additive group law on `E`.
- retained: ideal-class factorization exponents.
- relation primitive: `[k]G ↔ ideal class`; smooth ideal ⇒ multiplicative relation.
- compression primitive: prime-ideal factor base of small norm.
- rank mechanism: exponent matrix of ideal factorizations.
- descent: factor the target's ideal over the prime-ideal base.
- dominant cost exponent: cost of the *point→ideal* map — the crux.

### Nearest ledger entries
1. **07-17 C1 (quiver/groupoid CM-correspondence composition)** — acts on *isogenous curves* via
   `Cl(O)`; C3 maps the *DLP scalar's point* to an ideal. **Distinction: scalar→ideal vs curve→curve.**
2. **ISO-AR / M5 oriented-CM** — isogeny finding/vectorization in `Cl(O)`; C3 wants DLP relations.
   **Distinction: DLP index calculus vs vectorization.**
3. **B-permutation** — the `Cl(O)` action on curves is a torsor (permutation); C3 uses ideal
   *factorization*, not the action. **Distinction: factorization vs torsor action.**
4. **M4 cover norm labels `z^d=h(P)`** — both seek a factorization channel; C3's is in `O`, not a
   cover. **Distinction: endomorphism-ring ideals vs cover norms.**
5. **NR-033/T-ISO-4** — no weak isogenous curve; C3 seeks *smoothness*, not weakness. **Distinction:
   ideal smoothness vs weak destination.**

### Nearest literature
Deuring; class-group index calculus (Hafner–McCurley); CM theory (Cox); imaginary-quadratic DLP.
Gap: mapping a *specific point* `[k]G` to its ideal class **requires knowing `k`** (the CM
correspondence is via the class-group action on the curve, not a per-point label) — the map is almost
certainly DLP-circular; C3's value is to pin down exactly why.

### Target family
Ordinary prime-order `E/F_p` with small-discriminant CM (navigable `Cl(O)`) — the *only* setting where
`Cl(O)` is small enough to be a factor base; deployed random curves have huge `|disc|≈p`, excluded.
**Scope caveat:** this restricts to special (small-CM) curves, which are already excluded from the main
target family — so a positive here would be special-curve-only unless the map generalizes.

### Full algorithmic path (INCOMPLETE at the point→ideal map)
1. **Factor base:** prime ideals of `O` of norm `≤B`.
2. **Relation gen:** map factor-base *points* to ideal classes; factor over the prime-ideal base.
   **Stage 2 is the open crux — no known log-free point→ideal map exists.**
3–9: standard class-group IC *if* stage 2 existed.

### Cost model
`Cl(O)` index calculus is subexponential `L_{|disc|}(1/2)`; if `|disc|` is *small* (CM), this is
polynomial — but the point→ideal map is the DLP itself. **Promotion requires** a `poly(log q)` log-free
point→ideal map. Compare rho `n^0.5`.

### Why existing negatives do not kill it
Uses ideal *factorization* (not the torsor action, not a cover); a genuinely multiplicative smoothness.
New operation: **point→ideal factorization in `End(E)`.**

### Likely fatal obstruction
The correspondence between `E(F_p)` points and `O`-ideals is realized through the class-group action on
the *set of curves*, which labels *isogenies*, not the scalar `k` of a point on one curve; recovering
`k` from the ideal is the original DLP. Circular. C3 is retained as a **negative-theory probe** of
whether any non-circular point→ideal labelling exists.

### Minimal falsifying experiment
For small-CM toy curves (`|disc|` small), attempt to construct *any* `poly`-time map from `[k]G` to a
nontrivial `O`-ideal without using `k`; measure whether the recovered ideal's class depends on `k`
beyond the trivial `[k]G` value. Positive control = imaginary-quadratic-field DLP where ideals *are*
the native objects (index calculus works). Negative control = the point→ideal map (expected circular).

### Quantitative promotion gate
A log-free point→ideal map computable in `poly(log q)` whose output factors over an `≤B`-norm prime base
with rank `≥B−1` — across three small-CM sizes. (Expected to fail at stage 2; a precise circularity proof
is the deliverable.)

### Proof track
Theorem: a non-circular point→ideal labelling exists. Would likely break small-CM ECDLP; extraordinary.

### Disproof track
Prove every point→ideal map factors through the DLP (circularity) ⇒ a clean "endomorphism-ideal channel
is DLP-locked" barrier, complementing NR-033.

### Reproduction artifact
- note: `research/c3_cm_ideal_factorization_formalization_20260718.md`
- impl: `experiments/ecdlp_isogeny/c3_point_to_ideal_probe.sage`
- ledger id: `CMIDEAL-C3`

### Group D — negative-theory candidates (expose a loophole or barrier)

---

## Candidate: D1 — Class-function no-leakage barrier for linear/spectral representations  *(BARRIER — pairs B1, B2, B3, C1)*

### One-sentence mechanism
Prove that every *linear or spectral* representation whose defining data is a **class function of
Frobenius / a translation-invariant of `E`** (canonical-lift formal log, `H^1` cohomology operators,
group-dual character spectrum) carries only **order/trace information, not per-target scalar
information**, exactly bounding what B1/B2/B3 (and 07-17 C2) can extract.

### Status
HYPOTHESIS (provable-looking, in the restricted "invariant representation" model)

### Novelty classification
LEDGER-NEW (the ledger has no unified class-function no-leakage principle; individual walls exist
piecemeal for graph inversion and Frobenius).

### Semantic fingerprint
object: representations `ρ: E(F_p) → V` that factor through a Frobenius/translation invariant;
retained: the mutual information `I(ρ(P); log P)`; rank mechanism: **the theorem's object**; cost: n/a.

### Nearest ledger entries
M5 Frobenius/SEA (order only), 07-17 C2 (Lattès, rejected), B1/B2/B3 (its partners), M6 graph-inversion
negatives. Distinction: **a single mutual-information criterion** subsuming all "invariant representation"
no-leakage cases.

### Nearest literature
Shoup generic-group bound (a *different* model — encoding-generic, not representation-invariant);
class-field-theory invariance; Kedlaya/Satoh (why cohomology/canonical-lift give *counting*). Gap: no
information-theoretic no-leakage statement for invariant EC representations.

### Target family
All ordinary prime-order `E/F_p`.

### Full algorithmic path (theory + toy)
1. Define the "invariant representation" class: `ρ(P)` depends only on `(E, P)` through a Frobenius/
   translation-invariant functor (cohomology, canonical lift, character on `Z/n` with unknown log).
2. Show `ρ` is constant on translation classes / factors through order-trace data ⇒ `I(ρ(P);log P)=0`
   beyond the trivial group value.
3. Verify on toy curves: B1's `p`-adic-log digits, B2's `τ_P^*`, B3's spectrum all fail an MI test.

### Cost model
n/a (barrier). Consequence: B1/B2/B3 can only be *filters/constants*, never scalar channels — a
promotion filter that saves running three dead lanes at scale.

### Why existing negatives do not kill it
New unifying theorem.

### Likely fatal obstruction
The class is hard to define crisply — some "invariants" (jet-thickened `H^1`, non-invariant differentials)
*do* see more; the theorem must carefully exclude exactly the escape cases (which then become the real
candidates), so its value is the *boundary*, not a blanket no.

### Minimal falsifying experiment
Toy MI test at `p≈2^12,2^16,2^20` for B1/B2/B3 representations vs `k mod n`; theorem predicts `I≈0`. A
positive `I` falsifies (and promotes that representation).

### Quantitative promotion gate
Theorem proved + toy `I≈0` at three sizes ⇒ closes the invariant-representation lane; any `I>0` ⇒
promotes the leaking representation.

### Proof track
Translation-invariance / class-function argument + a data-processing inequality.

### Disproof track
A toy invariant with `I(ρ(P);log P)>0`.

### Reproduction artifact
- proof note: `research/d1_class_function_no_leakage_20260718.md`
- impl: `experiments/ecdlp_prime_field/d1_mutual_information_check.sage`
- ledger id: `CLASSFN-D1`

---

## Candidate: D2 — Addition-law scrambling lower bound for additive designs  *(BARRIER — pairs A2, C1)*

### One-sentence mechanism
Prove that the EC addition law **destroys any additive design** on x-coordinates: for a Sidon/B_h or
approximately-affine x-set `Σ`, the *group-sum* image `{x(A+B): x(A),x(B)∈Σ}` has near-maximal additive
energy defect, so design/near-linear structure gives **no** relation-rank or attempts-per-relation gain
(bounding A2 and C1).

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (the ledger asserts "hash-like sumsets" empirically; a *quantitative* additive-energy lower
bound tied to designs/stability is unproved).

### Semantic fingerprint
object: group-sum image of an x-design; retained: additive energy of the image; rank mechanism: **the
theorem's object**; cost: n/a.

### Nearest ledger entries
ECFG "hash-like sumset" rows, Ahmadi–Shparlinski (P1447), A2/C1 (partners). Distinction: **a proved
energy bound** vs an empirical observation; ties design *and* stability into one wall.

### Nearest literature
Ahmadi–Shparlinski (EC sum-product); Bourgain–Glibichuk–Konyagin; Bogolyubov–Ruzsa (inverse). Gap: no
bound specialized to *designed/structured* input sets.

### Target family
Ordinary prime-order `E/F_p`.

### Full algorithmic path (theory + toy)
1. Take `Σ` a Sidon/near-affine x-set; consider `T(Σ)={x(A+B)}`.
2. Bound the additive energy `E^+(T(Σ))` from below (image is near-random) via character-sum cancellation.
3. Conclude relation rank/attempts match a random base. Verify on toy curves (A2/C1 measurements).

### Cost model
n/a (barrier). Consequence: A2's design and C1's near-affine set both give random-base behavior.

### Why existing negatives do not kill it
New quantitative theorem generalizing the empirical hash-like observation.

### Likely fatal obstruction
A *tight* bound may need deep sum-product machinery; the fallback is the toy measurement (A2/C1 already
run it), so D2's marginal value is the *proof* — a citable barrier for all future design/structure ideas.

### Minimal falsifying experiment
Toy: measure `E^+(T(Σ))` for design vs random `Σ` at `p≈2^16,2^20,2^24`; theorem predicts near-equality.

### Quantitative promotion gate
Proved energy bound + toy near-equality ⇒ closes the additive-design/stability lane; a design with
`E^+(T(Σ))` polynomially below random ⇒ promotes A2/C1.

### Proof track
Character-sum cancellation (Deligne/Weil) applied to `T(Σ)`.

### Disproof track
A design whose group-sum image retains low energy (would promote A2/C1).

### Reproduction artifact
- proof note: `research/d2_addition_scrambling_bound_20260718.md`
- impl: `experiments/ecdlp_prime_field/d2_energy_check.sage`
- ledger id: `SCRAMBLE-D2`

---

## Candidate: D3 — Semaev transform-sparsity / border-rank lower bound  *(BARRIER — pairs A1, A3, B4)*

### One-sentence mechanism
Prove the univariate Semaev elimination polynomial `Ψ_R` is **dense/high-degree in every efficiently
computable basis** (monomial, division-polynomial, Chebyshev-adapted) **and** that the summation tensor
`T_{S_m}` has **near-maximal border rank**, so sparse interpolation (A1), low-degree list-decoding (A3),
and bilinear-complexity evaluation (B4) all fail to beat the dense `Θ(L²)` / birthday cost — upgrading
MX-1478's *coefficient* density to a basis-invariant *transform-sparsity + border-rank* lower bound.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (MX-1478/P1513 measured density/degree in fixed presentations; a basis-invariant sparsity
lower bound is a strictly stronger, unmeasured quantity).

### Semantic fingerprint
object: `Ψ_R` and its sparsity across bases; retained: min-over-bases term count; rank mechanism: **the
theorem's object**; cost: `log(sparsity)/log L`.

### Nearest ledger entries
ECFG-MX-1478 (dense resultant), ECFG-P1513 (cubic norm), NR-1477 (dense state), A1/A3 (partners),
RT-1476 (the gate). Distinction: **transform/basis-invariant sparsity vs fixed-presentation density.**

### Nearest literature
Sparse-interpolation complexity (Ben-Or–Tiwari lower bounds); shift/dictionary sparsity; Kousidis–
Wiemers (first-fall degree). Gap: no sparsity bound for `Ψ_R`.

### Target family
Ordinary prime-order `E/F_p`, `L≈n^(1/5)`.

### Full algorithmic path (theory + measurement)
1. Construct `Ψ_R`; compute term counts in monomial, division-polynomial, and Chebyshev bases;
   estimate min-sparsity over a family of shifts/bases.
2. Prove a lower bound via the Newton-polygon / degree-of-`Ψ_R` and root-count structure.
3. Confirm numerically at three sizes; feed A1/A3 the verdict.

### Cost model
n/a (barrier), but decides A1/A3: sparsity `Ω(L^{3/2})` ⇒ both fail RT-1476; `o(L^{3/2})` ⇒ opens them.

### Why existing negatives do not kill it
Strengthens MX-1478 to a basis-invariant quantity.

### Likely fatal obstruction
A truly *basis-invariant* bound is hard (adversary picks the basis); the honest fallback is a bound over
a *fixed family* of natural bases plus the numeric measurement.

### Minimal falsifying experiment
Compute `Ψ_R` term counts in three bases at `p≈2^20,2^24,2^28`; a basis giving `o(L^{3/2})` terms opens
A1/A3.

### Quantitative promotion gate
Proved `Ω(L^{3/2})` min-sparsity (closes A1/A3 / part of RT-1476) **or** measured `o(L^{3/2})` in a
computable basis (opens them). Either is decisive.

### Proof track
Newton-polygon / root-structure argument for `Ψ_R`.

### Disproof track
A sparse basis for `Ψ_R` (opens A1/A3).

### Reproduction artifact
- proof note: `research/d3_semaev_transform_sparsity_20260718.md`
- impl: `experiments/ecdlp_prime_field/d3_psi_sparsity_profile.sage`
- ledger id: `SPARSEBND-D3`

---

## 3.13 Literature Agent integration (completed — verdicts reconciled)

The Literature Agent's source-backed verdicts (families 1–6 = A3, A1, B1, B2, C1, A2) are reconciled into
each candidate's "Nearest literature" and "Novelty classification" above. **Corrected summary:**

| Family / cand | Verdict | Load-bearing primary source | Consequence for this run |
|---|---|---|---|
| A3 list-decoding | **LITERATURE-ADJACENT** (was POSSIBLY NOVEL) | Zhang–Liu, eprint 2018/795 / ProvSec 2019 (GS-decoding of ECDLP, curve-level, no rho win) | A3's *factor-base-indexed* code is still distinct; but list-decoding-for-ECDLP is not green field — read Zhang–Liu first. |
| A1 sparse-interp | **POSSIBLY NOVEL (contingent)** | Ben-Or–Tiwari 1988; Bi–Cheng–Rojas arXiv:1602.00208 | Monomial-sparsity ≠ root-sparsity; measure `S_m` support first or reframe as output-sensitive root-finding. |
| B1 canonical-lift | **POSSIBLY NOVEL (general `n`)**; LITERATURE-ADJACENT for anomalous/safe-prime | Yasuda WAIFI 2010 (only `n=p`); Silverman survey LNCS 5808; arXiv:1702.07107 (safe-prime) | Genuine gap for generic ordinary `n`; read Silverman's survey for the informal "why not" per scenario. |
| B2 cohomology | **NOVELTY-UNVERIFIED → barrier** | Achter et al. arXiv:1710.10726 (genus-1 Hasse–Witt is a scalar; `H^1` Frobenius = `X²−tX+p`) | Confirms B2 rejection; convert to a citable "cohomology is translation-blind" lemma (D1). |
| C1 approx-hom stability | **LITERATURE-ADJACENT** (was POSSIBLY NOVEL) | arXiv:2510.03828 (2025, x-coordinate additive rigidity, number-field); Ahmadi–Shparlinski arXiv:0806.0640 (`F_p` sum-product) | The exact BSG machinery exists in the wrong regime; **port the 2025 proof to `F_p` — may settle C1/D2 without an experiment.** |
| A2 Sidon design | **POSSIBLY NOVEL (provisional)** | Singer 1938; Bose–Chowla 1962 | Absence-based; pursue jointly with C1 — Ahmadi–Shparlinski may cap `x(E)` Sidon-ness. |

**Cross-cutting Lit-Agent finding:** *none* of the six families has any published *complete-cost vs
Pollard-rho* analysis for ordinary prime-order curves — each targets a different group, regime, or is a
reformulation with admitted no-speedup. That missing rho-comparable cost analysis is the common gap and the
first artifact to produce on promotion. **B3 (dual-group DFT), C2 (Kloosterman sampler), C3 (CM ideal)**
were outside the six-family request and remain **NOVELTY-UNVERIFIED** pending a targeted second pass
(log-free additive-character estimators; exponential-sum importance sampling; non-circular point→ideal maps).
No `literature.md` exists in the repo root; the Synthesis Agent should create it and log these six on promotion.

---

## 4. Ranking

Scores 0–5 on: **N** distance from prior ledger *and 07-17* mechanisms; **V** plausibility of an exact
verifier; **X** chance of changing an *exponent* (not a constant); **P** complete-path coverage; **F**
falsifiability at toy scale; **L** literature-novelty confidence; **R⁻** *low* hidden preprocessing/memory
risk (5=low). Reject if N<3, or no complete route to descent, or no quantitative rho comparison, or no
precise distinction from the closest ledger/07-17 entry.

| Cand | N | V | X | P | F | L | R⁻ | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A1** sparse-interp backend | 4 | 5 | 4 | 5 | 5 | 4 | 4 | **31** | **KEEP — conservative winner** |
| A2 Sidon/B_h base | 4 | 5 | 3 | 5 | 5 | 4 | 5 | 31 | keep (paired D2) |
| A3 list-decode backend | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 26 | keep (paired D3; Zhang–Liu adjacent) |
| ~~B1~~ canonical-lift formal log | 1 | 4 | 4 | 4 | 3 | 2 | 2 | (dup) | **REJECT — DUPLICATE of batch2 `STATE-B2`** |
| ~~B2~~ Cartier–Manin operator | 1 | 3 | 2 | 1 | 3 | 3 | 4 | (dup) | **REJECT — DUPLICATE of batch2 D2** |
| B3 dual-group Fourier | 4 | 3 | 3 | 2 | 3 | 3 | 3 | 21 | keep (weak; barrier-leaning) |
| **B4** Semaev-tensor border rank | 5 | 4 | 4 | 4 | 4 | 4 | 3 | **28** | **KEEP — representation winner** |
| **C1** approx-hom stability | 5 | 4 | 4 | 4 | 4 | 3 | 3 | **27** | **KEEP — high-risk winner** (X: exponent-capable; beats C2/C3-echo on upside) |
| ~~C2~~ Kloosterman sampler | 2 | 5 | 2 | 5 | 5 | 3 | 4 | (adj) | **REJECT — ADJACENT to batch2 C3 (not novel)** |
| C3 CM ideal factorization | 3 | 3 | 3 | 1 | 3 | 3 | 3 | 19 | **REJECT — INCOMPLETE (circular map)** |
| D1 class-function barrier | 5 | 5 | — | 5 | 4 | 4 | 5 | (barrier) | KEEP |
| D2 scrambling barrier | 4 | 5 | — | 5 | 5 | 4 | 5 | (barrier) | KEEP |
| D3 transform-sparsity/border-rank barrier | 4 | 5 | — | 5 | 5 | 4 | 5 | (barrier) | KEEP |

*(D-candidates are barriers; X is N/A — scored on decisiveness instead.)*

**Rejected as duplicates (batch2 collision, see §0.1):** B1 (canonical-lift = batch2 `STATE-B2`,
settled-negative); B2 (Cartier–Manin = batch2 D2 order-only barrier); C2 (Kloosterman = batch2 C3
character-bias, adjacent). **Rejected as incomplete:** C3 (point→ideal map DLP-circular — retained as a
negative-theory probe). **Surviving genuinely-new set:** A1, A2, A3, B3, B4, C1 (six, meeting the mandate),
plus barriers D1–D3.

**Winners:**
1. **Conservative — A1** (sparse-interpolation output-sensitive Semaev root backend).
2. **Representation — B4** (Semaev summation-tensor border rank / bilinear complexity).
3. **High-risk — C1** (approximate-homomorphism stability of the x-map).

All three (i) are outside the dominant ledger vocabulary *and* distinct from every candidate in **both**
07-17 batches by a named new operation, (ii) have an exact toy verifier, (iii) come with a paired barrier
(A1↔D3; B4↔D3-border-rank extension; C1↔D2) so a negative still advances the barrier map, and (iv) target
a *measured exponent that could cross 1/2* — not correctness.

---

## 5. Winner experiment contracts + first executable command

### Experiment Contract: A1 — sparse-interpolation Semaev root backend

- **Hypothesis:** the univariate Semaev projection `Ψ_R` for `m∈{4,5}` at `B≈n^(1/5)` has root-locator
  sparsity + evaluation cost giving membership exponent `α<3/2` (RT-1476), hence relation-gen `<1/2` in `n`.
- **Null:** `Ψ_R` is transform-dense (`Θ(L²)` terms / evaluations), no sparse handle (D3).
- **Parameters:** random ordinary prime-order `E/F_p`, `p≈2^20,2^24,2^28`; seeds `20260718..20260723`;
  `m=4,5`; `B=ceil(n^(1/5))`.
- **Metrics:** monomial/basis sparsity of `Ψ_R`, root count per shift, Prony/BOT recovery time, evaluation
  cost, relations, sparse rank, group/field ops, wall-clock, memory.
- **Positive control:** an engineered sparse elimination polynomial (BOT wins).
- **Negative control:** random dense polynomial of matched degree (BOT loses).
- **Success:** membership exponent `α<3/2` and relation-gen `<1/2` across all three sizes **and** sparse
  rank `t≥B−1`.
- **Falsification:** dense `Ψ_R` at every size (feed D3).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/a1_sparse_locator.sage \
    --sizes 20,24,28 --m 4,5 --seeds 20260718-20260723 \
    --out experiments/ecdlp_prime_field/a1_sparse_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/a1_sparse_locator.sage \
    --sizes 20 --m 4 --seeds 20260718 --stage sparsity_profile_only \
    --out experiments/ecdlp_prime_field/a1_smallest_probe.json
  ```

### Experiment Contract: B4 — Semaev summation-tensor border rank

- **Hypothesis:** the `m∈{4,5}` summation tensor `T_{S_m}` has border rank `R̲=O(L^{1−ε})` (`m=4`) with
  bounded degeneration order, so batched membership over `Θ(B)` shifts runs in `o(L²)` and instantiates the
  RT-1476 backend.
- **Null:** `R̲=Θ(L²)` (near-maximal, generic symmetric tensor), or degeneration order blows up precision —
  no gain (D3-border-rank extension).
- **Parameters:** random ordinary prime-order `E/F_p`, `p≈2^20,2^24,2^28`; `m=4,5`; `L=ceil(n^(1/5))`;
  seeds `20260718..20260723`.
- **Metrics:** flattening ranks / border-rank bounds of `T_{S_m}`, explicit small bilinear schemes,
  degeneration order, relations recovered, blind targets, group/field ops, memory.
- **Positive control:** a matrix-multiplication-like low-border-rank toy tensor (Bini scheme applies).
- **Negative control:** a random symmetric tensor of matched dimension (maximal border rank).
- **Success:** `log R̲/log L < 1` (`m=4`) with bounded degeneration at all sizes **and** an `R̲`-scheme
  recovers `≥B−1` independent relations and blind targets.
- **Falsification:** `R̲=Θ(L²)` at every size (feed the D3 border-rank lower-bound track).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/b4_semaev_border_rank.sage \
    --sizes 20,24,28 --m 4,5 --seeds 20260718-20260723 \
    --out experiments/ecdlp_prime_field/b4_border_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/b4_semaev_border_rank.sage \
    --sizes 20 --m 4 --seeds 20260718 --stage flattening_rank_only \
    --out experiments/ecdlp_prime_field/b4_smallest_probe.json
  ```

### Experiment Contract: C1 — approximate-homomorphism stability of the x-map

- **Hypothesis:** some ordinary `E/F_p` has an approximately-affine x-subset of density `|T|=B^{1+c}`,
  giving a `poly(log q)`-per-relation engine with rank `≥B−1`.
- **Null:** every large x-subset has near-maximal additive-energy defect (`|T|=B^{o(1)}`) — the
  sum-product/scrambling wall (D2).
- **Parameters:** random ordinary prime-order `E/F_p`, `p≈2^18,2^22,2^26`; seeds `20260718..`; defect
  thresholds `δ∈{0.01,0.05,0.1}`; sample size `m≈B²`.
- **Metrics:** largest `δ`-affine set size, additive energy, BSG parameters, relations from `T`, rank,
  attempts-per-relation, memory.
- **Positive control:** an anomalous / `j∈{0,1728}` curve with extra automorphisms (more structure).
- **Negative control:** random ordinary curve (should be flat).
- **Success:** `|T|=B^{1+c}` (superlinear structure) with defect small enough for rank `≥B−1`, across
  three sizes — a structural exponent, not a constant.
- **Falsification:** `|T|=B^{o(1)}` uniformly (feed D2 the inverse-theorem barrier).
- **Reproduction command:**
  ```bash
  sage experiments/ecdlp_prime_field/c1_bsg_stability.sage \
    --sizes 18,22,26 --delta 0.01,0.05,0.1 --seeds 20260718-20260721 \
    --out experiments/ecdlp_prime_field/c1_bsg_result.json
  ```
- **First executable command (smallest slice):**
  ```bash
  sage experiments/ecdlp_prime_field/c1_bsg_stability.sage \
    --sizes 18 --delta 0.05 --seeds 20260718 --stage energy_profile_only \
    --out experiments/ecdlp_prime_field/c1_smallest_probe.json
  ```

---

## 6. Red team — are the three winners disguised repetitions or cost-negative?

**A1 (sparse-interpolation backend).**
- *Disguised repeat of MX-1478 / P1513 (dense resultant/norm)?* No: MX-1478/P1513 *materialize* the dense
  object; A1 interpolates only a sparse locator from evaluations. **But** the sharpest challenge is that the
  *evaluation* of `Ψ_R` is itself `Θ(L²)` if `Ψ_R` is dense — so A1's advantage evaporates exactly when
  MX-1478's density holds, which is the empirical prior. **Cost-negative risk:** high — Prony over `F_p`
  needs `2t` evaluations of a possibly-dense polynomial; if `t=Θ(L²)` the whole thing is `L⁴`. **Verdict:**
  genuinely new *measurement* (basis-invariant sparsity of `Ψ_R` — a load-bearing number nobody has
  computed), most likely negative, valuable as the D3 barrier's empirical core.

**B4 (Semaev-tensor border rank).**
- *Disguised repeat of batch1 B2 (tensor-train / separator rank)?* This is the sharpest challenge. No:
  batch1 B2 measured *separator/Schmidt rank* across a cut (contraction treewidth); B4 measures *border/CP
  rank* of the whole tensor (bilinear complexity) — inequivalent invariants (a tensor can be low-treewidth
  yet high-border-rank and vice versa). **But** both are "the Semaev structure is rank-poor" bets, and the
  honest prior for a symmetric near-generic tensor is **maximal border rank** `R̲=Θ(L²)`, i.e. B4 closes
  rather than opens. **Cost-negative risk:** *border* rank uses approximate (degenerating) schemes; over
  `F_p` the degeneration order can add a `poly` precision factor that erases a small-`ε` gain — so B4 needs
  `α` comfortably below 1, not marginally. **Verdict:** genuinely new invariant (border rank of `T_{S_m}`,
  never computed), decisive either way (opens RT-1476 or, via the D3 border-rank extension, closes both the
  separator- and border-rank tensor loopholes), honest prior that it closes.

**C1 (approximate-homomorphism stability).**
- *Disguised repeat of the Ahmadi–Shparlinski sum-product wall (P1447)?* No: P1447 is an *expansion lower
  bound*; C1 runs the dual *inverse/stability* question (largest non-expanding piece) with BSG/Bogolyubov–
  Ruzsa — a genuinely new operation. **But** the same sum-product machinery that proves expansion very
  likely implies the inverse (no dense linear piece), so D2 is the favorite and `|T|=B^{o(1)}` is expected.
  **Cost-negative risk:** BSG on `m≈B²` samples is `Õ(B²)` — fine at toy scale, but the structured set, if
  found, might be special-curve-only (the positive control is `j∈{0,1728}`), not transferring to random
  ordinary curves. **Verdict:** weakest upside; its value is that D2 (an inverse-theorem barrier tying
  design *and* stability into one citable wall) is worth proving regardless, and C1 is the experiment that
  either proves D2 empirically or finds its one exception.

**Cross-cutting red-team conclusion.** All three winners are **most likely negative results** — the same
honest posture as the 07-17 winners, and unsurprising given that the frontier is defined by two *conditional*
theorems (RT-1472, RT-1476) that every prior mechanism has failed to realize. What makes this run's set worth
running anyway: each winner is (a) mechanism-distinct from every inventoried entry **and** every 07-17
candidate by a *named new operation* (sparse-interpolation locator recovery; canonical-lift formal-log
additivity; additive-energy stability search), (b) equipped with an exact toy verifier, and (c) attached to a
paired barrier theorem (A1→D3 transform-sparsity; B1→D1 class-function no-leakage; C1→D2 scrambling
inverse-theorem) so that the likely negative outcome *sharpens the barrier map* rather than merely failing.
The three barriers D1/D2/D3 are, arguably, the higher-value deliverables: they would convert three empirical
"hash-like / dense / no-leakage" observations into citable lower bounds that pre-emptively close whole
classes of future proposals.

---

## 7. Claim discipline

- Every candidate is `HYPOTHESIS`/`CONJECTURE` — **no** performance claim is made. No candidate solves any
  ECDLP instance; all are unrun proposals.
- "Relations" ≠ "ECDLP recovery": every contract requires relation-derived blind target descent under full
  charging, not relation validity alone.
- Evidence targeted is `TOY` / `MODEL-BOUND`; novelty verdicts are search-bounded (`POSSIBLY NOVEL` =
  "no equivalent found in this ledger + the 07-17 report + one literature pass," not certified;
  `NOVELTY-UNVERIFIED` where the literature pass is incomplete).
- Four candidates are rejected and retained only for the fingerprint record: **B1, B2, C2** as
  **duplicates of batch2** (`STATE-B2` / D2 / C3 — disclosed in §0.1, not silently dropped), and **C3** as
  **INCOMPLETE** (DLP-circular point→ideal map, a negative-theory seed).
- A failed candidate is a **scoped negative result**, not evidence that prime-field ECDLP cannot be improved.

## 8. Next three pushes (Research-Director decision)

1. **Conservative:** run A1's `sparsity_profile_only` slice — compute the basis-invariant term count and
   root count of the `m=4` `Ψ_R` for one 20-bit curve. One cheap number that either motivates the
   sparse-interpolation lane or (with D3) closes it and refines MX-1478.
2. **Representation:** run B4's `flattening_rank_only` slice in parallel — the flattening/border-rank
   lower bound of the `m=4` summation tensor `T_{S_m}` on one 20-bit curve directly decides whether the
   tensor-complexity backend can meet RT-1476, feeding the D3 border-rank extension either way. (The
   demoted B1/B2/C2 need *no* run — batch2 already settled Serre–Tate, Cartier–Manin, and character-bias.)
3. **High-risk / barrier (highest leverage, possibly no experiment needed):** commission **D2** from the
   Theory Agent regardless of C1's outcome. The Literature Agent found a ready-made proof template —
   **arXiv:2510.03828 (2025), x-coordinate additive rigidity** — that already runs the BSG/Bogolyubov–Ruzsa
   argument, but over number fields. **First action: port its proof to `F_p`**, classifying each step as
   archimedean-height-dependent (non-transferable) vs pure group-law identity (transferable). If the core
   steps transfer, D2 becomes a `RESTRICTED THEOREM` closing both the additive-design (A2) and stability
   (C1) lanes *without running an experiment* — the single highest-value move this run identifies.

---

## 9. Comparison to both 2026-07-17 runs (anti-duplication audit)

**vs batch1** (`idea_generation_20260717.md`):

| batch1 seed / candidate | Reused? | This run's distinct mechanism |
|---|---|---|
| BKK / mixed-volume (b1 A1) | No | A1 = **sparse interpolation** of the root-locator, no polytope/homotopy |
| EDS / elliptic nets (b1 A2) | No | A2 = **Sidon/B_h additive designs**, not net-value factorization |
| incidence-reporting (b1 A3) | No | A3 = **interpolate-and-factor list-decoding**, not a range-DS |
| dual-number jets (b1 B1) | No | (B1-mine rejected as batch2 dup; no jet reuse) |
| **tensor-train / separator rank (b1 B2)** | No | **B4 = border/CP rank** (bilinear complexity) — an inequivalent tensor invariant |
| tropical p-adic lift (b1 B3) | No | B3-mine = **group-dual DFT**, not valuation strata |
| quiver CM composition (b1 C1) | No | C3 = **ideal factorization in `End(E)`**, not correspondence composition |
| Lattès operator (b1 C2) | No | subsumed into the D1 **class-function barrier** |
| xedni height lift (b1 C3) | No | (no height-lift candidate survives here) |

**vs batch2** (`idea_generation_20260717_batch2.md`) — three collisions found and disclosed (§0.1):

| batch2 candidate | Collision? | Resolution |
|---|---|---|
| B2 Serre–Tate (`STATE-B2`) | **YES** = my B1 | **B1 REJECTED as duplicate** (settled-negative, Voloch trace-1-only) |
| D2 crystalline/Cartier–Manin | **YES** = my B2 | **B2 REJECTED as duplicate** (order-only barrier already established) |
| C3 character-sum bias | **ADJACENT** = my C2 | **C2 REJECTED** (same equidistribution wall; sampler-weight vs count-bias distinction only) |
| A1 3-LP homology, A2 NFS two-sided, A3 Kedlaya–Umans, B1 Kani-RM, B3 theta-bilinear, C1 rep-MITM, C2 p-curvature | No | A1(sparse-interp)/A2(Sidon)/A3(list-decode)/B4(border-rank)/C1(stability) are all mechanism-distinct; B4 vs batch2 A3 = **structured bilinear decomposition** vs black-box KU evaluation |

**Surviving genuinely-new (vs ledger AND both batches):** A1, A2, A3, B3, B4, C1 (six — mandate met),
plus barriers D1–D3. The three runs are complementary: batch1 probed *geometry/tensor-contraction*
structure; batch2 probed *transfer/lift/analytic* channels; this run probes *transform-domain sparsity*
(A1/A3/D3), *additive-combinatorial design & stability* (A2/C1/D2), and *algebraic (bilinear) complexity*
(B4/D3). The disclosed B1/B2/C2 collisions confirm the anti-duplication process works as intended: the
frontier's mechanism space is now dense enough that independent runs re-derive the same Serre–Tate,
Cartier–Manin, and character-sum ideas — which is itself evidence that the *untried* lanes (sparse
interpolation, combinatorial design, list-decoding, border rank, additive-stability) are the genuinely
open ones.

---

*End of report. Strongest scoped result: the frontier remains the two unrealized conditional theorems
RT-1472 and RT-1476; this run adds three mechanism-new probes (A1, B1, C1) and three new barrier theorems
(D1, D2, D3), each of which — pass or fail — sharpens the map of what a sub-rho prime-field ECDLP algorithm
would have to do.*
