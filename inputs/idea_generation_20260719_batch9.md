# Idea Generation — Research Director — 2026-07-19 batch9 (report 17 / internal batch15)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Target:** a non-generic *single-target* prime-field ECDLP algorithm whose **complete** cost beats
Pollard-rho `O(sqrt(n))`. Toy correctness, a new coordinate system, a relation certificate, faster
preprocessing, or a solver improvement alone is NOT a breakthrough.
**Authorized scope:** generated toy curves, public benchmark instances, synthetic data only. No
wallets, production keys, accounts, or unauthorized systems.

---

## 0. Executive summary

This is the **17th** idea-generation report (internal batch15). The mechanism space is **saturated**:
14 prior reports (ECFG-P1514–P1645) span ~60 distinct mechanism lanes plus three dedicated barrier
technologies per batch since batch8. The honest, highest-EV output remains the **barrier arm**, not new
crossing claims — this batch confirms that verdict and imports **eleven technology families absent from
every prior report and both ledgers** (grep-verified, §2). Every attack candidate below has a
near-certain, *named* scoped-negative kill; the three barriers (group D) each close a live gate in a
class no prior barrier reached.

**No break is claimed. Both live gates RT-1472 and RT-1476 remain open.**

---

## 1. Required input review — inventory

Reviewed in full (both canonical ledgers by targeted extraction — each is multi-MB with very long
records — plus all secondary inputs and all prior reports):

| Source | Extent | Notes |
|---|---|---|
| `research_ledger.md` (main) | 2.8 MB; **7541** `P`-records, **956** `ECFG-P`, **522** `PO`, **516** `ECFG-NR` (negative results), **382** `ECFG-H`, **178** `H` | committed frontier ~`ECFG-P1470`; gates `P1472`/`P1476` verified live |
| `ecdlp_index_calculus_state/research_ledger.md` | 797 KB | IC-state frontier `P1509–P1513` |
| `research/non_generic_transfer_search_20260610.md` | transfer/decomposition channel search | same-field isogeny CLOSED; scalar Weil restriction NEGATIVE; twist = positive control only; **OPEN**: a Jacobian/correspondence engine not factoring through the elliptic x-line Semaev relation |
| `ecdlp_index_calculus_state/research_sources/bibliography.json` | 11 primary sources | Semaev'04, Gaudry'09, FPPR'12, Shantz-Teske'13, FHJRV'14, Kousidis-Wiemers'15, Karabina'15, Amadori-Pintore-Sala'17, McGuire-Mueller'17, Trimoska-Ionica-Dequen'20 |
| `research/idea_generation_2026071{7,8,9}*.md` | 14 reports (batch1–batch14) | anti-dup corpus, ECFG-P1514–P1645 |

**ID families covered:** `P` / `ECFG-P` (proposals), `PO` (PO-transfer program, runs through PO96z
Hom-PPAV/finite-Kummer-Cheon), `ECFG-NR` (scoped negatives), `H` / `ECFG-H` (hypotheses), `RT` / `P147x`
(research-target rho-crossing gates), `MX`, `KN`, `RQ`, `IDEA`, `EV`, `DEC`, `TASK`. Entries reviewed:
the full committed ledger frontier + all 14 report cohorts (~132 prior report candidates).

### 1.1 Verified fixed context (extracted this run, not from memory)

- **Baseline B (rho):** Pollard rho + negation map `≈ 0.886·sqrt(n)` group ops, single target, `n ≈ p`.
  With `q ≈ L^5`, `r = |factor base| ≈ q^{1/5} = L`, rho `= L^{2.5}`.
- **RT-1472 (`P1472`, two-large-prime occupancy boundary):** cost exponent
  `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)`, minimized at `ℓ = 1/3` giving **2/3**; crossing below `1/2` requires
  large-prime **supply** `δ > 1/4` (relations per pair above baseline occupancy). Verified from the
  `p1472_two_large_prime_occupancy_exponent_boundary` record.
- **RT-1476 (`P1476`, m=5 membership backend boundary):** need query exponent `α < 3/2` (i.e. below
  `L^{1.5}`) with setup `≤ L^2` and random-like support, to give a complete five-term membership
  backend under the boundary. Verified from the `P1476 … below the P1476 L^1.5 query boundary` record.
- **IC-state closure chain:** `P1510-R1` verified per-target compiler `Θ(r)` rows at `Θ(r^3)=q^{3/5}`;
  `P1511-R2` closed product-circuit gcd/subres/Hasse (`r^3` leaves); **`P1512-R1` closed scalar-linear
  Chow atomizer at `Ω(r^5)` via `deg(det M) ≤ dim`** — only a **target-specialized nonlinear-circuit
  exception** survives; `P1513` open shared-common-norm (input quadratic, both norms cubic).
- **Sparse-LA stage `n^{2/5}=L^2` is NOT binding.** The relation/membership-**generation** stage is.

### 1.2 Target family (all candidates)

Ordinary `E/F_p`, `p` prime, prime-order subgroup `n ≈ p`, `q ≈ L^5`. **Excluded:** anomalous
(`trace = 1`), supersingular, small embedding degree (MOV/Frey-Rück range), small-CM-discriminant
special curves, non-prime order, and any twist/off-curve channel (positive control only).

---

## 2. Anti-duplication — novelty grounding (grep-verified this run)

The eleven imported families and all reused keywords were grepped across **both ledgers and all 14
reports**. **Zero matches** for every imported-family term:

`haussler`, `packing number`, `dependent random choice`, `circle method`, `singular series`,
`baker-norine`, `gonality`, `compressed sensing`, `restricted isometry`, `sparse recovery`,
`brauer-manin`, `expander code`, `tanner code`, `incompressibility`, `borsuk-ulam`,
`round elimination` / `round-elimination`, `minor arc`, `chip-firing` — **all 0 files**.

Adjacency anchors used for honest distinction (all confirmed *present* in the corpus): batch7 VC-dimension
(`VCDIM-D3`), batch14 large-sieve/Bombieri-Vinogradov analytic-supply arm, batch4 `SANDPILE-JACOBIAN` +
batch3 Berkovich `SKEL-B3`, batch3 Weil-Châtelet/Lang `WCDESC-B2`, batch11 `BEREZIN-PFAFFIAN`,
batch3/12 additive-energy/container δ-supply, batch13 random-restriction avg-case, batch12
`CELL-PROBE-CHRONOGRAM` + batch7 `LIFTING` + batch8 `NOF` communication barriers, batch14
survey-propagation.

Pre-rejected as dups this run (do **not** re-propose): crystalline/Cartier-Manin/Kedlaya (CLOSED,
batch2 D2); Kloosterman/character-sum bias (CLOSED, batch2 C3, Deligne); "poly-time sampler certifies
`δ>1/4`" role (CONSUMED, batch5 MATUNION-A2 / batch11 LORENTZIAN-C2); slice-rank / Croot-Lev-Pach
(batch4 SLICE-RANK-1); tensor-network / tensor-train (batch1 TT-B2); Coppersmith/orthogonal lattice
small-root (batch10 / batch3); good-reduction Berkovich skeleton collapse (batch3 SKEL-B3).

---

## 3. Candidates (12)

Notation: `r = L ≈ q^{1/5}`, `q ≈ n`, rho `= L^{2.5}`. "α" = membership-query exponent in `L`
(gate `< 3/2`); "δ" = large-prime supply exponent (gate `> 1/4`).

---

### Group A — conservative extensions of known work

---

## Candidate: SINGULAR-SERIES-A1

### One-sentence mechanism
Exploit the Hardy-Littlewood **circle-method singular series** `𝔖` of the five-term summation equation
to compute the *exact asymptotic main term* for the count of genuine m=5 relations, reducing the
uncertainty in the RT-1472 supply exponent `δ` below the inequality-only bounds of the batch14 analytic
arm.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (circle method / singular series / minor arc: 0 corpus hits; batch14 gave `L^2`
*inequalities* — large sieve — and *average*-over-moduli — Bombieri-Vinogradov — never an asymptotic
main term).

### Semantic fingerprint
- algebraic object: the affine variety `S5(x1..x5)=0` (5th Semaev polynomial) over `F_p`, counted with
  additive characters `e_p(·)`.
- available public operations: point counting, additive-character exponential sums, Weil bounds.
- hidden structure exploited: the *singular series* factorization of the relation density into local
  densities `𝔖 = Π_v β_v`.
- information discarded: the actual factor-base labels (only the count is kept).
- information retained: expected number of relations with all five coordinates factor-base-smooth.
- relation-generation primitive: none new — this **prices** the existing Semaev relation source.
- compression primitive: none.
- rank mechanism: standard sparse relation matrix (unchanged, `n^{2/5}`).
- descent mechanism: standard individual-log descent (unchanged).
- dominant cost exponent: sets `δ` (analysis, not runtime).

### Nearest ledger entries
1. **batch14 LARGE-SIEVE-SUPPLY-A1** — same target (`δ`), but an `L^2` dual inequality; the circle
   method computes the *equality* main term. Distinction: inequality vs asymptotic.
2. **batch14 BOMBIERI-VINOGRADOV-A3** — average equidistribution over moduli; the circle method is a
   *single-modulus* asymptotic with an explicit singular series. Distinction: average vs pointwise.
3. **batch6 LANGWEIL-METER-A3** — Deligne/Lang-Weil *point count* of the Semaev variety. Distinction:
   Lang-Weil gives `#S5 = q^4 + O(q^{7/2})`; the circle method gives the *smooth-restricted* count with
   local factors `β_v`, which is the actual supply. Circle method refines Lang-Weil by the smoothness
   constraint.
4. **`P1475`** equidistribution supply record. Distinction: `P1475` is the empirical δ-plateau; `𝔖`
   would explain it analytically.
5. **batch7 ADOLPHSPERBER-A2** — p-adic Newton-polygon valuation meter. Distinction: p-adic slope vs
   archimedean singular series (complementary local factors).

### Nearest literature
Hardy-Littlewood circle method (major/minor arcs, singular series); Deligne's Weil-II bounds on
exponential sums; Birch's theorem on forms in many variables. Claim: the singular series controls the
main-term density of solutions to a polynomial equation restricted to a set (here: factor-base
smoothness). Gap: standard circle-method applications are over `Z`/`Q` with archimedean major arcs;
over `F_p` the "arcs" degenerate to the full additive-character sum and the minor-arc cancellation is
exactly the Weil bound — which does **not** beat the main term (see D1).

### Target family
As §1.2. Excluded additionally: curves where `S5` is reducible (small CM), which distort `𝔖`.

### Full algorithmic path
1. **factor-base construction:** standard `x`-coordinate deck of size `r = L`.
2. **relation generation:** enumerate 5-tuples via the existing Semaev source; `𝔖` predicts the yield.
3. **witness extraction and verification:** each relation is an EC identity `P1+..+P5=O`, re-verified
   by the wrapper (Tier per `docs/claims-and-verification.md`).
4. **relation probability:** `Pr[all 5 smooth | S5=0] ≈ 𝔖 · (r/q)^5 · q^{... }`; the *deviation* of
   `𝔖` from 1 is the δ handle.
5. **matrix dimensions, density, rank:** `r × r`, `O(1)` nonzeros/row, rank `r − O(1)` (unchanged).
6. **factor-log calibration:** standard.
7. **individual logarithm / target descent:** standard 2-LP descent.
8. **offline/online separation:** `𝔖` is offline (one closed-form evaluation).
9. **memory and parallelism:** unchanged from 2-LP baseline.

### Cost model
`𝔖 = Π_p β_p` with local factors `β_p = 1 + O(p^{-1/2})` (Weil). Expected relations
`N ≈ 𝔖 · C · L^{...}`. If `𝔖 = 1 + c` with `c` bounded, then `δ = O(1)` in the *exponent* sense →
supply exponent stays at the occupancy baseline `1/4`, **not above**. Comparison: rho `L^{2.5}`; 2-LP arm
`L^{5·2/3}=L^{10/3}` at `δ=0` improving toward rho only if `δ>1/4`. `𝔖`-analysis predicts the crossing
does **not** occur analytically.

### Why the existing negative results do not already kill it
The batch14 arm bounded `δ` from *above* by inequalities but never computed the constant/main term; a
positive `δ` could in principle hide in the gap between the large-sieve upper bound and the true
density. The singular series closes that gap with an equality — that is the new operation.

### Likely fatal obstruction
Over `F_p` the minor arcs are the full non-principal character sum, bounded by Weil `√q`; the main term
is `q^4`, so `𝔖` is `Θ(1)` and `δ → 1/4^-`. The candidate self-converts to barrier **D1**.

### Minimal falsifying experiment
Toy sizes `L ∈ {8,16,32}`, `≥5` seeds each, ordinary prime-order curves; positive control = a curve
family engineered with an extra local factor (small torsion) to *inflate* `β_p`; negative control =
random 5-variate degree-matched non-Semaev variety. Measure empirical relation density vs the
predicted `𝔖`.

### Quantitative promotion gate
Promote (to D1 or beyond) only if the measured supply exponent `δ(L)` extrapolates **> 1/4** with a
fitted slope whose 95% CI excludes `1/4` across all three `L`. Correctness of `𝔖` alone is not the gate.

### Proof track
Theorem to establish: for ordinary `E/F_p`, `𝔖(S5) = 1 + O(p^{-1/2})`, hence smooth-relation density
equals the occupancy baseline up to `o(1)` in the exponent ⇒ `δ = 1/4`.

### Disproof track
Exhibit an ordinary curve family with `𝔖` bounded away from 1 by a *growing* factor (would need a
persistent local anomaly) — or measure `δ(L) > 1/4` empirically.

### Reproduction artifact
Contract `experiment_contract_singular_series_supply_exponent.md`; impl `singular_series_supply.py`;
result `singular_series_supply.json`; audit `singular_series_supply_audit.py`; ledger `ECFG-P1646`.

---

## Candidate: DEPENDENT-RANDOM-CHOICE-A2

### One-sentence mechanism
Exploit **dependent random choice (DRC)** to extract from the two-large-prime co-occurrence bipartite
graph a dense subset whose common neighborhood yields extra relations per large-prime pair, attempting
to lift the RT-1472 supply `δ` above `1/4`.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (DRC: 0 hits; distinct from batch3 ENERGY sum-product ceiling, batch12 container, batch4
Kővári-Sós-Turán sign-rank Zarankiewicz).

### Semantic fingerprint
- algebraic object: bipartite graph `G` on (large primes) × (relations), edges = incidences.
- available public operations: relation harvesting, incidence listing.
- hidden structure exploited: high co-degree concentration (DRC finds a subset with large pairwise
  common neighborhood).
- information discarded: single-large-prime relations.
- information retained: dense 2-LP sub-block.
- relation-generation primitive: DRC dense-subgraph extraction.
- compression primitive: restrict to the DRC core.
- rank mechanism: standard.
- descent mechanism: standard 2-LP graph descent.
- dominant cost exponent: `δ`.

### Nearest ledger entries
1. **batch3 ENERGY-D1** (additive-energy relation-supply ceiling) — both quantify pair supply; DRC is a
   *constructive* dense-subgraph tool, energy is a *counting ceiling*. Distinction: extraction vs bound.
2. **batch12 KRUSKAL-KATONA-A1 / container** — shadow/container compression ceilings; DRC extracts a
   dense core rather than compressing. Distinction: dense-subset vs shadow density.
3. **`P1472`** (the gate itself). Distinction: DRC is a proposed booster of `δ`.
4. **batch4 SIGNRANK-GAMMA2-B3** — Zarankiewicz bipartite pincer; DRC is the extremal-graph dual of the
   same bipartite object. Distinction: γ2 factorization norm vs common-neighborhood.
5. **batch5 MATUNION-A2** — matroid-union of two LP graphs. Distinction: independence structure vs
   density concentration.

### Nearest literature
Fox-Sudakov "Dependent random choice" survey; Kővári-Sós-Turán. Claim: DRC finds a set `U` with
`|U|≥ε|V|` in which most pairs have `≥t` common neighbors, if the graph is dense. Gap: DRC produces a
subset of *existing* edges; it cannot manufacture relations that were not harvested.

### Target family
As §1.2; requires the 2-LP graph to be actually built (setup `≤ L^2`).

### Full algorithmic path
1. factor base: standard + large-prime tail `B = n^{1/5}`.
2. relation generation: harvest 2-LP relations; build `G`.
3. witness/verification: each relation re-verified.
4. relation probability: DRC boosts *yield per retained pair*, not total edges.
5. matrix: DRC core `× r`, sparse.
6. calibration: standard.
7. descent: 2-LP graph path through the core.
8. offline/online: DRC extraction offline.
9. memory/parallelism: core fits in `L^2` setup budget.

### Cost model
Edge count of `G` is fixed by the honest harvest = exactly `δ`. DRC re-partitions edges; total supply
`= Σ deg` is invariant ⇒ `δ` unchanged. Cost of DRC extraction `O(|E|)` ≤ setup. Comparison: no
improvement over the 2-LP arm exponent `2/3`.

### Why the existing negative results do not already kill it
The energy/container ceilings bound the *aggregate*; they leave open whether a *dense sub-block* has
locally higher yield exploitable by descent. DRC is the sharpest constructive test of that sub-block
hope.

### Likely fatal obstruction
Supply is conserved: DRC relocates edges but the honest total edge density *is* `δ`. A dense core has
higher local density but proportionally fewer pairs → product is invariant.

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; positive control = synthetic graph with planted dense block (DRC must find
it and yield must rise); negative control = honest 2-LP graph (yield must stay flat); ordinary
prime-order curves.

### Quantitative promotion gate
Promote only if the DRC-core descent yields a measured `δ_core > 1/4` AND the total relation count to
solve a toy target drops below the flat 2-LP count, across all three `L`.

### Proof track
Theorem: for the honest 2-LP incidence graph, every DRC core satisfies `(#pairs in core)·(yield/pair)
= (1±o(1))·(total supply)` ⇒ `δ_core = δ`.

### Disproof track
A curve/parameter regime where the harvested graph has planted-block structure (locally correlated
large primes) making `δ_core > δ` — measure it.

### Reproduction artifact
Contract `experiment_contract_drc_two_large_prime_core.md`; impl `drc_two_large_prime.py`; result
`drc_two_large_prime.json`; audit `drc_two_large_prime_audit.py`; ledger `ECFG-P1647`.

---

## Candidate: COMPRESSED-SENSING-RIP-A3

### One-sentence mechanism
Represent factor-base logs as an unknown vector and each relation as a linear measurement, then use
**compressed-sensing / RIP sparse recovery** to solve the DLP system from *fewer relations than the
matrix rank*, cutting the binding relation-supply requirement.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (compressed sensing / RIP / sparse recovery: 0 hits; distinct from batch10 Coppersmith
small-root lattice and batch3 orthogonal-lattice OLAT — those find *short vectors*, not compressed
measurements).

### Semantic fingerprint
- algebraic object: linear system `A·log = b` over `F_n` (`n` prime, subgroup order).
- available public operations: relation harvesting, linear algebra over `F_n`.
- hidden structure exploited: sparsity of the *unknown* (few nonzero factor-base logs relevant to a
  target) — hypothesized.
- information discarded: relations beyond the compressed measurement set.
- information retained: a small incoherent measurement block.
- relation-generation primitive: standard.
- compression primitive: RIP measurement matrix / ℓ1-style recovery analogue.
- rank mechanism: sparse recovery *replaces* full-rank solve.
- descent mechanism: recovered logs → standard descent.
- dominant cost exponent: relation count `m`.

### Nearest ledger entries
1. **batch10 COPPERSMITH-LATTICE-B1** — lattice small-root; compressed sensing is measurement-count
   reduction, not root smallness. Distinction: RIP vs LLL.
2. **batch3 OLAT-C3** — orthogonal-lattice relation finder. Distinction: kernel vs sparse recovery.
3. **`n^{2/5}` sparse-LA stage** — the non-binding LA baseline; CS attacks the *supply*, not the solve.
4. **batch8 DELSARTE-LP-A2** — coding-LP on the 2-LP code; CS is a decoding, not a supply ceiling.
   Distinction: recovery vs LP bound.
5. **batch7 LISTDECODE-B2** — list-decoding relation generator. Distinction: list decoding a *code* vs
   sparse recovery of a *vector*.

### Nearest literature
Candès-Tao RIP; Donoho compressed sensing; finite-field CS (Draper-Malekpour, expander measurement
matrices). Claim: an `m×N` RIP matrix recovers `k`-sparse vectors from `m = O(k log(N/k))`
measurements. Gap: RIP relies on real/complex incoherence + ℓ1 convexity; over `F_n` there is no norm,
no convex relaxation, and the only finite-field analogue (MDS/expander matrices) needs `m ≥` support
size.

### Target family
As §1.2.

### Full algorithmic path
1. factor base: standard.
2. relation generation: harvest `m` relations (target `m ≪ r`).
3. witness/verification: standard.
4. relation probability: standard; the win would be needing far fewer.
5. matrix: `m × r`, want `m = O(k log r)`.
6. calibration: from recovered logs.
7. descent: standard.
8. offline/online: measurement design offline.
9. memory/parallelism: `m`-row system.

### Cost model
If `k = Θ(r)` (all logs relevant), `m = Ω(r)` — no gain. If the target's descent only needs `k = r^{o(1)}`
logs, `m` could drop — but over `F_n` recovery is exact linear solving, requiring `m ≥ k` *independent*
rows regardless of "compression." Comparison: collapses to the rank bound `r`; no crossing.

### Why the existing negative results do not already kill it
No prior lane framed the relation *count* as a sparse-recovery measurement budget; the lattice lanes
minimized vector length, a different objective. This is the first measurement-complexity framing.

### Likely fatal obstruction
Finite fields have no RIP: exact recovery of a `k`-sparse vector over `F_n` needs `m ≥ 2k` and the
`F_n`-Semaev measurement matrix is structured (not incoherent) ⇒ no sub-rank recovery.

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; positive control = genuinely `k`-sparse synthetic system with a random `F_n`
matrix (recovery from `m≈2k` should work) to isolate whether the *elliptic* matrix is the blocker;
negative control = the actual Semaev measurement matrix. Ordinary prime-order curves.

### Quantitative promotion gate
Promote only if a toy target is solved from `m = o(r)` verified relations across all three `L`, with a
fitted `m(L)` exponent `< 1`.

### Proof track
Theorem: the `F_n`-Semaev measurement matrix has spark `≤ 2` on structured supports (or, contrapositive,
no `k`-RIP for `k = ω(1)`).

### Disproof track
Construct a curve/target whose descent support is provably `r^{o(1)}`-sparse *and* whose measurement
matrix admits sub-rank recovery.

### Reproduction artifact
Contract `experiment_contract_compressed_sensing_relation_budget.md`; impl `cs_relation_budget.py`;
result `cs_relation_budget.json`; audit `cs_relation_budget_audit.py`; ledger `ECFG-P1648`.

---

### Group B — genuine representation changes

---

## Candidate: BRAUER-MANIN-B1

### One-sentence mechanism
Represent the *transfer obstruction* (why no corresponding object exposes a weak channel — the OPEN
question of `non_generic_transfer_search_20260610.md`) as a class in the **Brauer group `Br(E)` /
Brauer-Manin obstruction**, and test whether its vanishing predicts a relation-generating
correspondence that beats rho.

### Status
CONJECTURE

### Novelty classification
LEDGER-NEW (Brauer-Manin: 0 hits; distinct from batch3 WCDESC Weil-Châtelet/Lang descent, which used
`H^1` torsors, not the `H^2`/`Br` obstruction).

### Semantic fingerprint
- algebraic object: `Br(E) = H^2_{ét}(E, 𝔾_m)` and the local-global pairing.
- available public operations: cohomology/pairing computations, isogeny/correspondence search.
- hidden structure exploited: a nonzero Brauer class would obstruct (or, if zero, permit) a
  correspondence exposing a factor base off the elliptic x-line.
- information discarded: the explicit Semaev x-line relation.
- information retained: the cohomological obstruction class.
- relation-generation primitive: a correspondence certified by `Br`-vanishing (hypothetical).
- compression primitive: none.
- rank mechanism: TBD (the correspondence's Jacobian).
- descent mechanism: transfer + Jacobian index calculus.
- dominant cost exponent: TBD.

### Nearest ledger entries
1. **batch3 WCDESC-B2** — Weil-Châtelet/Lang descent collapse. Distinction: `H^1` torsor triviality vs
   `H^2`/`Br` obstruction; different cohomological degree.
2. **`non_generic_transfer_search` OPEN item** — the correspondence-engine question this represents.
3. **PO96z (Hom-PPAV/finite-Kummer-Cheon)** — the committed transfer program endpoint. Distinction:
   PPAV homomorphisms vs Brauer obstruction.
4. **batch5 FOURIERMUKAI-B2** — Poincaré-kernel correspondence. Distinction: derived-category kernel vs
   arithmetic Brauer class.
5. **batch3 SKEL-B3** — Berkovich skeleton (good-reduction collapse). Distinction: analytic skeleton vs
   étale Brauer group.

### Nearest literature
Grothendieck "Le groupe de Brauer"; Skorobogatov "Torsors and rational points" (Brauer-Manin
obstruction); Lichtenbaum duality. Claim: `Br` of a smooth variety over a *finite* field
`F_p` is **trivial** (`Br(F_p) = 0`, and for a curve `Br(E) = 0` by class field theory / Lichtenbaum).
Gap: with `Br(E) = 0` there is no obstruction *and* no leakage — the machine is vacuous over `F_p`.

### Target family
As §1.2. This is precisely why the candidate is a *representation* change (of the OPEN transfer
question), not an attack expected to succeed.

### Full algorithmic path
INCOMPLETE. Stages 1–3 (factor base / relation generation / witness) depend on the *existence* of a
`Br`-certified correspondence, which the literature says does not exist over `F_p` (`Br(E)=0`). Labeled
INCOMPLETE and demoted accordingly; retained because it *closes the cohomological-transfer lane by name*.

### Cost model
Vacuous: no correspondence ⇒ no relation engine ⇒ no comparison to rho. The *value* is the closure
statement, not a runtime.

### Why the existing negative results do not already kill it
WCDESC closed the `H^1` torsor route; no prior entry addressed the `H^2`/Brauer obstruction, so the
cohomological-transfer lane was not fully closed at the `Br` level. This closes it.

### Likely fatal obstruction
`Br(E) = 0` for a smooth curve over a finite field (Lichtenbaum/class field theory) ⇒ no Brauer-Manin
data ⇒ no channel.

### Minimal falsifying experiment
Compute `Br(E)[ℓ]` for toy ordinary curves via the `ℓ`-torsion étale pairing at `L ∈ {8,16,32}`;
positive control = a variety with known nontrivial `Br` (e.g. a diagonal cubic surface over a number
field, char-0 sanity check) to validate the pipeline; negative control = the elliptic curve (`Br=0`).

### Quantitative promotion gate
Promote only if a nonzero `Br(E)` class over `F_p` is exhibited AND it yields a correspondence whose
end-to-end transfer cost exponent `< 1/2`. (Near-certainly impossible.)

### Proof track
Theorem (essentially known): `Br(E) = 0` for `E/F_p` smooth projective curve ⇒ cohomological transfer
obstruction lane is empty over prime fields.

### Disproof track
Any construction of a nontrivial arithmetic Brauer class on `E/F_p` usable as a relation source.

### Reproduction artifact
Contract `experiment_contract_brauer_manin_transfer_obstruction.md`; impl `brauer_manin_transfer.py`;
result `brauer_manin_transfer.json`; audit `brauer_manin_transfer_audit.py`; ledger `ECFG-P1649`.

---

## Candidate: BAKER-NORINE-GONALITY-B2

### One-sentence mechanism
Represent the individual-log descent as a **graph-divisor / chip-firing** problem on the reduction
graph and use **Baker-Norine Riemann-Roch (Dhar burning)** so that the descent branching cost equals
the graph **gonality**.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (Baker-Norine / gonality / chip-firing: 0 hits; distinct from batch4 SANDPILE-JACOBIAN,
which used the *critical group order* — that was circular; gonality is the *min-degree moving divisor*,
a different invariant).

### Semantic fingerprint
- algebraic object: divisors on the reduction/dual graph of a (bad-reduction) model, `Pic` and the rank
  function `r_{BN}`.
- available public operations: chip-firing moves, Dhar burning, effective-divisor reduction.
- hidden structure exploited: linear equivalence of divisors = relation membership.
- information discarded: field-element detail (only combinatorial divisor class kept).
- information retained: divisor class + gonality pencil.
- relation-generation primitive: principal divisors (firing moves).
- compression primitive: Baker-Norine reduction to `q`-reduced form.
- rank mechanism: graph Laplacian.
- descent mechanism: reduce target divisor to factor-base support (gonality pencil).
- dominant cost exponent: gonality of the graph.

### Nearest ledger entries
1. **batch4 SANDPILE-JACOBIAN-C3** — graph critical group. Distinction: group *order* (circular) vs
   *gonality* (min pencil degree). Different invariant, different obstruction.
2. **batch3 SKEL-B3** — Berkovich skeleton. Distinction: gonality lives on the same skeleton but is a
   linear-series invariant, not the good-reduction collapse statement.
3. **batch9 NEWTON-OKOUNKOV-B3** — graded descent filtration. Distinction: valuation semigroup vs graph
   linear series.
4. **`P1513`** open shared common-norm descent. Distinction: gonality is a graph-theoretic descent
   metric.
5. **batch8 CLUSTER-MUTATION-B3** — Somos/periodicity. Distinction: cluster mutation vs chip-firing.

### Nearest literature
Baker-Norine "Riemann-Roch and Abel-Jacobi theory on a finite graph"; Baker "Specialization of linear
systems"; gonality of graphs (van Dobben de Bruyn-Gijswijt). Claim: graph gonality bounds the degree of
a divisor moving in a pencil, controlling reduction cost. Gap: `E/F_p` has **good reduction** (it is
smooth over `F_p`), so the reduction graph is a single vertex and gonality is trivial (= 0/1).

### Target family
As §1.2 — and this is the killer: good reduction ⇒ no nontrivial skeleton.

### Full algorithmic path
1. factor base: graph vertices (would-be dual-graph components).
2. relation generation: chip-firing principal divisors.
3. witness/verification: linear-equivalence check.
4. relation probability: n/a (deterministic reduction).
5. matrix: graph Laplacian `× vertices`.
6. calibration: from divisor classes.
7. descent: Dhar-burning reduction along the gonality pencil.
8. offline/online: graph built offline.
9. memory/parallelism: graph-sized.
INCOMPLETE for prime-field targets: the graph degenerates (single vertex).

### Cost model
Trivial-skeleton ⇒ gonality `≤ 1` ⇒ no descent structure ⇒ no runtime. Would need a *degenerating
family*, which a fixed `E/F_p` does not provide. No crossing.

### Why the existing negative results do not already kill it
SANDPILE used the group order and was circular; SKEL closed the *good-reduction collapse* but did not
address whether a *linear-series* invariant (gonality) on a chosen model helps — this closes that
sub-question by name.

### Likely fatal obstruction
Good reduction of `E/F_p` ⇒ single-vertex reduction graph ⇒ gonality trivial. (Same root cause as
SKEL-B3, hence expected demotion.)

### Minimal falsifying experiment
Build reduction graphs for toy *bad-reduction* models (multiplicative reduction over a chosen small
prime, as a structural probe only) at `L ∈ {8,16,32}`; positive control = a known
high-gonality graph (banana/ladder) to validate Dhar burning; negative control = the good-reduction
`E/F_p` (trivial graph). This is a structural probe; it does **not** transfer a prime-field target.

### Quantitative promotion gate
Promote only if a *prime-field* descent is realized with cost exponent tied to a nontrivial gonality
`< 1/2`. (Near-certainly impossible under good reduction.)

### Proof track
Theorem: for `E/F_p` with good reduction, the Baker-Norine gonality of the reduction graph is `≤ 1`,
hence carries no descent advantage.

### Disproof track
A prime-field-relevant model with nontrivial graph gonality that yields a sub-rho descent.

### Reproduction artifact
Contract `experiment_contract_baker_norine_gonality_descent.md`; impl `baker_norine_gonality.py`;
result `baker_norine_gonality.json`; audit `baker_norine_gonality_audit.py`; ledger `ECFG-P1650`.

---

## Candidate: CLIFFORD-SPINOR-B3

### One-sentence mechanism
Represent the five-point group-law relation inside a **Clifford algebra / spin representation**, so the
symmetrized Semaev condition becomes a spinor-norm/Pfaffian-adjacent bilinear identity potentially
solvable below the marked-resultant degree.

### Status
HEURISTIC

### Novelty classification
LITERATURE-ADJACENT (Clifford/spinor: 0 hits, but *adjacent* to batch11 BEREZIN-PFAFFIAN, which used
the fermionic Grassmann integral — the Clifford even subalgebra is the quantization of that exterior
algebra).

### Semantic fingerprint
- algebraic object: Clifford algebra `Cl(V,Q)` on the coordinate space with the group-law quadratic form.
- available public operations: Clifford multiplication, spinor norm.
- hidden structure exploited: a possible low-rank spinor factorization of the 5-point condition.
- information discarded: higher-degree resultant terms.
- information retained: spinor/even-part component.
- relation-generation primitive: spinor-norm vanishing.
- compression primitive: spin representation dimension `2^{⌊dim/2⌋}`.
- rank mechanism: spinor Gram matrix.
- descent mechanism: standard.
- dominant cost exponent: spin-rep dimension.

### Nearest ledger entries
1. **batch11 BEREZIN-PFAFFIAN-C1** — fermionic Grassmann/Pfaffian of the marked resultant. Distinction:
   Clifford quantizes the same exterior algebra (adjacency = high dup risk).
2. **`P1504`/HOLANT matchgate** (closed) — Pfaffian/matchgate signatures. Distinction: spinor norm vs
   matchgate.
3. **batch1 TT-B2 / border rank** — tensor decompositions. Distinction: Clifford vs tensor-train.
4. **batch12 IMMANANT-B2** — character-weighted determinant. Distinction: spinor vs immanant.
5. **`P1512-R1`** nonlinear-circuit exception. Distinction: is the spin form a nonlinear circuit escaping
   `deg(det)≤dim`? Near-certainly no (spinor Gram is still degree-bounded).

### Nearest literature
Chevalley "The algebraic theory of spinors"; spinor norm and the Pfaffian. Claim: even Clifford
elements factor quadratic forms. Gap: the 5-point condition is degree-≥3 (cubic norms per `P1513`), not
quadratic ⇒ no faithful spinor linearization; the Berezin analysis already showed integrand degree > 2
forces higher moments.

### Target family
As §1.2.

### Full algorithmic path
1–9: as the symmetrized-Semaev backend but with the spin-representation Gram in place of the resultant.
Stage 4 relation probability and stage 5 rank inherit the Berezin degree obstruction. Effectively a
representation re-encoding of the closed Pfaffian lane.

### Cost model
Spin-rep dimension `2^{⌊5/2⌋}=8` per block is `O(1)`, but the *degree-3* condition means the spinor Gram
has entries of degree `≥3` ⇒ reduces to the `r^3` floor (P1511-R2). No crossing.

### Why the existing negative results do not already kill it
Berezin-Pfaffian used the *integral*; the Clifford *algebra* multiplication is a distinct
representation whose spinor norm might, in principle, linearize a quadratic sub-part. It does not,
because the binding norm is cubic.

### Likely fatal obstruction
The 5-point relation is not quadratic (cubic per `P1513`); Clifford linearizes only quadratics ⇒
collapses to the closed Berezin/`r^3` floor.

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; positive control = a genuinely quadratic membership toy (spinor must
linearize it); negative control = the cubic 5-point condition. Ordinary prime-order curves.

### Quantitative promotion gate
Promote only if the spinor-Gram membership backend measures query exponent `α < 3/2` across all three
`L`. (Blocked by the cubic degree.)

### Proof track
Theorem: the symmetrized 5-point condition has Clifford/spinor rank `Θ(r)` (no quadratic factorization).

### Disproof track
A spinor factorization reducing the condition to a quadratic form (would need the norm to be quadratic).

### Reproduction artifact
Contract `experiment_contract_clifford_spinor_membership.md`; impl `clifford_spinor_membership.py`;
result `clifford_spinor_membership.json`; audit `clifford_spinor_membership_audit.py`; ledger `ECFG-P1651`.

---

### Group C — high-risk speculative mechanisms

---

## Candidate: KOLMOGOROV-INCOMPRESSIBILITY-C1

### One-sentence mechanism
Use the **incompressibility method** (Kolmogorov complexity) to prove that a *random* target's m=5
membership descent admits a shorter-than-`L^{1.5}` witness on a `1−o(1)` fraction of targets, giving an
average-case membership backend below the RT-1476 boundary with a rho fallback on the rare hard fraction.

### Status
CONJECTURE

### Novelty classification
POSSIBLY-NOVEL (incompressibility: 0 hits; distinct from batch13 RANDOM-RESTRICTION avg-case
shrinkage — that randomized the *circuit inputs*; this randomizes over *targets* and uses
description-length, a different axis).

### Semantic fingerprint
- algebraic object: the membership predicate as a string; its Kolmogorov complexity `K(·)`.
- available public operations: enumeration, evaluation.
- hidden structure exploited: most targets are *compressible* relative to the factor base (short
  descent certificates).
- information discarded: the rare incompressible (hard) targets → rho fallback.
- information retained: short descent programs for typical targets.
- relation-generation primitive: enumeration of short programs.
- compression primitive: Kolmogorov description length.
- rank mechanism: standard.
- descent mechanism: short-certificate descent, else rho.
- dominant cost exponent: average query exponent.

### Nearest ledger entries
1. **batch13 RANDOM-RESTRICTION-C1** — avg-case sub-`L^{1.5}` via shrinkage + rho fallback. Distinction:
   shrinkage (Håstad switching) vs incompressibility (description length). Same *regime*, different
   *tool*.
2. **batch10 MOSER-ENTROPY-COMPRESSION-C3** — constructive entropy-compression δ meter. Distinction:
   Moser bounds a *supply*; incompressibility bounds a *query*.
3. **batch8 PROBABILISTIC-POLY-C3** — randomized backend. Distinction: probabilistic degree vs
   description length.
4. **`P1476`** the gate. Distinction: average-case attack on it.
5. **batch12 QUANTUM-ADVERSARY-SPAN-C1** — query SDP. Distinction: adversary bound vs incompressibility.

### Nearest literature
Li-Vitányi "An Introduction to Kolmogorov Complexity" (incompressibility method); Buhrman et al. Claim:
a random string is incompressible; if membership certificates were short for *all* targets, one could
compress the string — contradiction. Gap: incompressibility is a *lower-bound* method (it proves
certificates are *long*, not short), so it more naturally produces a **barrier** than an algorithm —
the constructive direction is self-defeating.

### Target family
As §1.2; "average" over uniformly random targets in the subgroup.

### Full algorithmic path
1. factor base: standard.
2. relation generation: enumerate short descent programs (length `< L^{1.5}`) per target.
3. witness/verification: each short program re-verified by the wrapper.
4. relation probability: fraction of targets with a short program (the crux).
5. matrix: standard for the offline log table.
6. calibration: standard.
7. descent: short program if found, else rho fallback.
8. offline/online: log table offline; short-program search online.
9. memory/parallelism: program enumeration parallelizes.

### Cost model
If a `1−ε` fraction has description length `< L^{1.5}` and the `ε` fraction falls back to rho `L^{2.5}`,
average `= (1−ε)L^{α} + εL^{2.5}`; crossing needs `α<3/2` AND `ε < L^{3/2−5/2}=L^{-1}`. Incompressibility
predicts the *opposite*: typical targets are *incompressible* ⇒ certificates `≥ L^{1.5}` ⇒ no gain.

### Why the existing negative results do not already kill it
RANDOM-RESTRICTION needed an AC0-shallow Boolean form (absent). Incompressibility needs no circuit
structure — it argues purely from counting/description length, a genuinely different failure surface.

### Likely fatal obstruction
The method proves certificates are *long* for typical targets (incompressibility is a lower-bound
technique) ⇒ it establishes a barrier (see also D-arm), not an algorithm. Self-defeating as an attack.

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; sample random targets, search for descent programs shorter than `L^{1.5}`
symbols; positive control = a structured target family with known short certificates (small-order
combination); negative control = uniform random targets. Ordinary prime-order curves.

### Quantitative promotion gate
Promote only if the measured fraction of targets with sub-`L^{1.5}` verified certificates is `1−o(1)`
with the hard-fraction `ε = O(L^{-1})`, across all three `L`.

### Proof track
Theorem: for a `1−o(1)` fraction of targets, `K(descent | factor base) < L^{1.5}`. (Believed false.)

### Disproof track
Incompressibility lower bound: `K(descent) ≥ L^{1.5}` for a `1−o(1)` fraction ⇒ converts to a barrier.

### Reproduction artifact
Contract `experiment_contract_incompressibility_avg_backend.md`; impl `incompressibility_backend.py`;
result `incompressibility_backend.json`; audit `incompressibility_backend_audit.py`; ledger `ECFG-P1652`.

---

## Candidate: EXPANDER-CODE-SYNDROME-C2

### One-sentence mechanism
Represent relations as parity checks of a **Sipser-Spielman expander / Tanner code** and recover the
factor-base logs by **unique-neighbor flow decoding**, aiming to solve from fewer parity checks than the
matrix rank.

### Status
HEURISTIC

### Novelty classification
LEDGER-NEW (expander/Tanner code: 0 hits; distinct from batch6 HDX-COBOUNDARY-A2, which measured `δ` via
*coboundary expansion of the relation complex*, and batch7 LISTDECODE, a *relation generator*).

### Semantic fingerprint
- algebraic object: Tanner code on a bipartite expander; parity-check matrix = relation matrix.
- available public operations: syndrome computation, flow decoding.
- hidden structure exploited: unique-neighbor expansion enabling linear-time decoding.
- information discarded: non-expander parity checks.
- information retained: expander sub-block.
- relation-generation primitive: standard.
- compression primitive: expander parity checks.
- rank mechanism: expander flow decoding replaces Gaussian elimination.
- descent mechanism: standard.
- dominant cost exponent: number of parity checks.

### Nearest ledger entries
1. **batch6 HDX-COBOUNDARY-A2** — coboundary/cosystolic expansion δ-meter. Distinction: expander code is
   a *decoding representation*, not a supply meter.
2. **batch7 LISTDECODE-B2** — Guruswami-Sudan relation generator. Distinction: syndrome decoding a code
   whose codeword is the log vector, vs decoding source codes into relations.
3. **batch11 PROOF-SPACE-PEBBLING-D1** — Ben-Sasson-Nordström. Distinction: proof space vs code decode.
4. **`n^{2/5}` LA stage** — expander decoding attacks the *count*, not the solve time.
5. **batch8 DELSARTE-LP-A2** — coding-LP ceiling. Distinction: decoding vs LP bound.

### Nearest literature
Sipser-Spielman "Expander codes"; Tanner. Claim: `(c,d)`-regular expander codes decode a constant
fraction of errors in linear time from `m = Θ(N)` checks. Gap: decoding needs `m ≥ N` (rate bounded
away from 1) ⇒ no sub-rank recovery; the elliptic parity-check matrix is structured, not an expander.

### Target family
As §1.2.

### Full algorithmic path
1. factor base: standard. 2. relations = parity checks. 3. witness verified. 4. probability standard.
5. Tanner matrix `m × r`, `m ≥ r`. 6. calibration from decoded codeword. 7. descent standard.
8. code design offline. 9. flow decoding parallelizes.

### Cost model
Expander codes have rate `< 1` ⇒ `m = Ω(r)` checks needed ⇒ no compression below rank; decode time
`O(m)` ≤ LA baseline (already non-binding). Comparison: no crossing.

### Why the existing negative results do not already kill it
No prior lane framed recovery as *code syndrome decoding on an expander*; HDX used the *complex*, not a
code. First code-theoretic recovery representation.

### Likely fatal obstruction
Rate bound: `m ≥ r`; and the Semaev parity-check matrix is not an expander (structured, low girth).

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; positive control = a random expander parity-check on a synthetic sparse log
vector (decode from `m = Θ(r)`); negative control = the elliptic Semaev matrix. Ordinary prime-order
curves.

### Quantitative promotion gate
Promote only if a toy target is solved from `m = o(r)` verified parity checks, `m(L)` exponent `<1`,
across all three `L`.

### Proof track
Theorem: the Semaev parity-check matrix has vertex-expansion `< 1/2` (not unique-neighbor) ⇒ no
expander-code decoding advantage.

### Disproof track
An expander-structured relation source with sub-rank flow decoding of a toy target.

### Reproduction artifact
Contract `experiment_contract_expander_code_syndrome.md`; impl `expander_code_syndrome.py`; result
`expander_code_syndrome.json`; audit `expander_code_syndrome_audit.py`; ledger `ECFG-P1653`.

---

## Candidate: BORSUK-ULAM-TOPOLOGICAL-C3

### One-sentence mechanism
Use a **topological pigeonhole (Borsuk-Ulam / Tucker-lemma)** argument on the membership configuration
complex to *guarantee existence* of balanced (low-weight, sign-symmetric) relations without searching,
turning existence into constructive relation generation.

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (Borsuk-Ulam: 0 hits, but the *finite-field shadow* of topological existence is
Chevalley-Warning / Ax-Katz, which IS in the corpus — batch9 AX-KATZ; high collapse risk).

### Semantic fingerprint
- algebraic object: the simplicial complex of candidate 5-point configurations with a `Z/2` (negation)
  action.
- available public operations: configuration enumeration, negation map.
- hidden structure exploited: an equivariant map whose non-existence forces a balanced relation.
- information discarded: non-symmetric configurations.
- information retained: the `Z/2`-symmetric (negation-paired) relations.
- relation-generation primitive: topological existence ⇒ guaranteed relation.
- compression primitive: symmetry quotient.
- rank mechanism: standard.
- descent mechanism: standard.
- dominant cost exponent: existence bound (may be non-constructive).

### Nearest ledger entries
1. **batch9 AX-KATZ-SUPPLY-A2 / AX-KATZ-BARRIER-D3** — p-adic Chevalley-Warning count. Distinction:
   Ax-Katz is the finite-field *algebraic* shadow of the topological argument; Borsuk-Ulam is the
   *archimedean/topological* source. Near-certain collapse to Ax-Katz.
2. **batch4 SLICE-RANK-1-D2** — polynomial-method existence. Distinction: topology vs polynomial method.
3. **the negation map** (rho baseline) — the `Z/2` action reused. Distinction: negation as symmetry.
4. **batch5 ARBOREAL-C1** — Galois/tree symmetry. Distinction: topological vs arithmetic symmetry.
5. **batch12 SUNFLOWER-FREE-C3** — extremal existence. Distinction: sunflower vs topological.

### Nearest literature
Matoušek "Using the Borsuk-Ulam Theorem"; Chevalley-Warning; Ax-Katz. Claim: `Z/2`-equivariant
topology forces existence of certain configurations. Gap: over `F_p` the only rigorous transfer is
Chevalley-Warning (a *counting* congruence), which the corpus already exploits and which does not beat
the relation supply baseline.

### Target family
As §1.2.

### Full algorithmic path
1. factor base standard. 2. relation generation: topological existence guarantee (non-constructive!).
3–9: standard *if* a relation is produced. Stage 2 constructivity is the crux → likely INCOMPLETE.

### Cost model
If existence is non-constructive, no runtime gain; the constructive finite-field version is
Chevalley-Warning, which yields the occupancy baseline `δ = 1/4`, not above. No crossing.

### Why the existing negative results do not already kill it
Ax-Katz was used as a *counting* meter/barrier; the topological framing asks whether an *equivariant
non-embeddability* forces a *specific balanced* relation exploitable by descent — a distinct question
even if it collapses.

### Likely fatal obstruction
No topological invariants survive base change to `F_p` except the Chevalley-Warning congruence
(already exploited); the existence is non-constructive.

### Minimal falsifying experiment
`L ∈ {8,16,32}`, ≥5 seeds; positive control = a configuration where Tucker's lemma is constructive
(combinatorial Sperner instance); negative control = the elliptic membership complex. Ordinary
prime-order curves.

### Quantitative promotion gate
Promote only if the topological guarantee yields *constructive* balanced relations lifting `δ > 1/4`
across all three `L`.

### Proof track
Theorem: the elliptic membership complex admits no `Z/2`-equivariant map to `S^{k}` forcing a balanced
relation beyond the Chevalley-Warning count.

### Disproof track
A constructive Tucker/Borsuk-Ulam relation generator on the elliptic complex.

### Reproduction artifact
Contract `experiment_contract_borsuk_ulam_relations.md`; impl `borsuk_ulam_relations.py`; result
`borsuk_ulam_relations.json`; audit `borsuk_ulam_relations_audit.py`; ledger `ECFG-P1654`.

---

### Group D — negative-theory candidates (barriers / loopholes)

*Each imports a lower-bound technology no prior barrier used, and each closes a live gate if it bites.*

---

## Candidate: SINGULAR-SERIES-BARRIER-D1

### One-sentence mechanism
Prove via the **circle method minor-arc / Weil bound** that the singular series `𝔖` of the 5-point
equation is `Θ(1)` over ordinary `F_p`, hence the honest relation supply exponent satisfies
`δ ≤ 1/4` **unconditionally** for any circle-method-countable relation source — closing RT-1472 for
that class.

### Status
HYPOTHESIS (barrier)

### Novelty classification
POSSIBLY NOVEL (first circle-method barrier; distinct from batch14 large-sieve `L^2` inequality and
Bombieri-Vinogradov average — this is a *pointwise asymptotic* barrier).

### Semantic fingerprint
object = additive-character sum over `S5=0`; operation = Weil exponential-sum bound; structure = local
density factorization; discarded = labels; retained = supply exponent; primitive = main-term +
minor-arc split; compression = none; rank = n/a; descent = n/a; cost exponent = `δ` ceiling.

### Nearest ledger entries
batch14 LARGE-SIEVE-BARRIER-D1 (inequality → `δ≤1/4` over residue-structured advice; D1 here is the
*equality/asymptotic* version, unconditional over the whole modulus family), batch14
SIEVE-PARITY-BARRIER-D3 (parity principle), batch6 LANGWEIL-SUPPLY-D2 (point count), batch9
AX-KATZ-BARRIER-D3 (p-adic), `P1475` (empirical plateau this would explain).

### Nearest literature
Hardy-Littlewood; Deligne Weil-II; Birch forms-in-many-variables. Claim: minor arcs bounded by `√q`
per non-principal character ⇒ error below the `q^4` main term ⇒ `𝔖 = Θ(1)`. Gap: verifying the local
factors have no growing anomaly for ordinary curves.

### Target family
As §1.2.

### Full algorithmic path
Barrier — no algorithm. Establishes the supply ceiling used to price A1/A2/A3 and the whole 2-LP arm.

### Cost model
`δ ≤ 1/4` ⇒ 2-LP arm exponent `≥ 2/3 > 1/2` ⇒ no rho crossing via circle-method-countable supply.

### Why the existing negative results do not already kill it
Prior analytic barriers were inequalities/averages; this pins the *main-term constant*, removing the
gap where a positive `δ` could hide.

### Likely fatal obstruction (to the barrier)
A curve family with a persistent growing local factor `β_p` (would need a structural anomaly absent in
ordinary curves) would break the `Θ(1)` claim.

### Minimal falsifying experiment
Measure `𝔖`-predicted vs empirical supply at `L ∈ {8,16,32}`, ≥5 seeds; positive control =
torsion-inflated curve (raises `β_p`); negative control = generic ordinary curve. Barrier holds if
`δ(L) → 1/4`.

### Quantitative promotion gate (to accepted barrier)
Accept if `δ(L)` extrapolates to `≤ 1/4` with 95% CI excluding `>1/4` across all three `L`.

### Proof track
Theorem: `𝔖(S5) = 1 + O(p^{-1/2})` for ordinary `E/F_p` ⇒ `δ = 1/4`.

### Disproof track
An ordinary family with `𝔖` growing in `L`.

### Reproduction artifact
Contract `experiment_contract_singular_series_barrier.md`; impl `singular_series_barrier.py`; result
`singular_series_barrier.json`; audit `singular_series_barrier_audit.py`; ledger `ECFG-P1655`.

---

## Candidate: HAUSSLER-PACKING-BARRIER-D2

### One-sentence mechanism
Use the **Haussler packing lemma / ε-net lower bound** on the dual set-system of the m=5 membership
predicate to prove a query lower bound `α ≥ 3/2` in the sample/statistical-query membership class,
closing RT-1476 for that class — a strict refinement of the batch7 VC (shatter-function) ceiling.

### Status
HYPOTHESIS (barrier)

### Novelty classification
POSSIBLY NOVEL (Haussler packing / ε-net: 0 hits; strictly refines batch7 VCDIM-D3 shatter function,
which bounds *diversity* but not sample-based *query count*).

### Semantic fingerprint
object = dual set-system of the membership predicate; operation = ε-separated query configurations;
structure = packing number `M(ε)`; discarded = field values; retained = query configurations; primitive
= packing/ε-net; compression = ε-net; rank = n/a; descent = n/a; cost exponent = `α` floor.

### Nearest ledger entries
batch7 VCDIM-D3 (shatter function δ-diversity — packing is the metric refinement giving a *query*
floor), batch8 APPROXDEG-D1 (dual polynomial α), batch13 SENSITIVITY-DEGREE-BARRIER-D1 (query
sensitivity), batch12 QUANTUM-ADVERSARY-SPAN-C1 (query SDP), `P1476` (the gate).

### Nearest literature
Haussler "Sphere packing numbers for subsets of the Boolean n-cube"; Haussler-Welzl ε-nets. Claim:
packing number `M(ε) = Θ((d/ε)^d)` lower-bounds the sample size / query configurations needed to
`ε`-approximate the predicate. Gap: the *field-op-per-query* cost translation (a bit-query floor may
land below `3/2` after the cubic per-query cost of P1510 is factored — same caveat as batch13 D1).

### Target family
As §1.2.

### Full algorithmic path
Barrier — no algorithm. Prices A3 (compressed sensing) and any sample-based membership backend.

### Cost model
`M(ε)` with `d = VC-dim` of the predicate ⇒ query configurations `≥ L^{3/2}` if `d ≥ 3/2·log_L`; then
combined with P1510's cubic field-op-per-query, `α ≥ 3/2`. Closes RT-1476 in the sample class.

### Why the existing negative results do not already kill it
VCDIM bounded shatter diversity (a δ-side quantity); the packing number is the metric-entropy refinement
that directly lower-bounds *queries*, which VC does not.

### Likely fatal obstruction (to the barrier)
If the membership predicate's dual system has small packing dimension (symmetric/low-metric-entropy), the
floor is loose ⇒ inconclusive, not a barrier (mirrors batch10 A1's "small Γ ⇒ inconclusive").

### Minimal falsifying experiment
Empirically estimate `M(ε)` of the membership set-system at `L ∈ {8,16,32}`, ≥5 seeds; positive control
= a high-VC synthetic predicate (packing must be large); negative control = a symmetric low-entropy
predicate. Ordinary prime-order curves.

### Quantitative promotion gate (to accepted barrier)
Accept if the fitted packing exponent gives `α ≥ 3/2` (after the field-op translation) across all three
`L`.

### Proof track
Theorem: the m=5 membership dual system has packing number `M(ε) = L^{Ω(1)}` forcing `α ≥ 3/2`.

### Disproof track
A low-packing (symmetric) structure of the predicate ⇒ loose floor.

### Reproduction artifact
Contract `experiment_contract_haussler_packing_barrier.md`; impl `haussler_packing_barrier.py`; result
`haussler_packing_barrier.json`; audit `haussler_packing_barrier_audit.py`; ledger `ECFG-P1656`.

---

## Candidate: ROUND-ELIMINATION-BARRIER-D3

### One-sentence mechanism
Apply **Miltersen-Nisan-Safra-Wigderson round elimination** to the asymmetric-communication complexity
of the *batched* m=5 membership data structure, proving a query/cell-size tradeoff floor `α ≥ 3/2` for
low-round backends — closing RT-1476 for the data-structure class.

### Status
HYPOTHESIS (barrier)

### Novelty classification
POSSIBLY NOVEL (round elimination: 0 hits; distinct from batch7 LIFTING query-to-communication, batch8
NOF number-on-forehead, batch12 CELL-PROBE-CHRONOGRAM (Larsen dynamic) and DISCREPANCY-CORRUPTION,
batch13 BORODIN-COOK time-space).

### Semantic fingerprint
object = asymmetric 2-party communication game for batched membership; operation = message rounds;
structure = round-elimination inductive message shrinkage; discarded = one party's message per round;
retained = residual game; primitive = n/a; compression = n/a; rank = n/a; descent = n/a; cost exponent
= `α` floor with a rounds parameter.

### Nearest ledger entries
batch7 LIFTING-D1 (query→comm lifting, single instance vs *asymmetric* round game), batch8 NOF-COMM-D2
(3+ party vs 2-party asymmetric), batch12 CELL-PROBE-CHRONOGRAM-D1 (dynamic time-stamped vs *static*
round elimination), batch12 DISCREPANCY-CORRUPTION-A3 (rectangle discrepancy vs round induction),
`P1476` (the gate).

### Nearest literature
Miltersen-Nisan-Safra-Wigderson "On data structures and asymmetric communication complexity"; Sen-
Venkatesh round-elimination lemma. Claim: for `t`-round asymmetric protocols, round elimination gives a
cell-probe lower bound `t = Ω(log N / log(cell size))`. Gap: whether the *batched* membership game has
the required product structure (independent sub-instances) — shared quadratic input (P1513) may break
the direct-sum needed for round elimination (same caveat as batch11 DIRECTSUM-INFO).

### Target family
As §1.2.

### Full algorithmic path
Barrier — no algorithm. Prices any low-round batched membership data structure (the "θ=2 multipoint
sharing" hope from batch8 HANKEL-BLOCK).

### Cost model
Round elimination ⇒ any `o(log L)`-round backend needs cell size `L^{Ω(1)}` ⇒ total query
`α ≥ 3/2`. Closes RT-1476 for the low-round data-structure class.

### Why the existing negative results do not already kill it
Prior communication barriers were single-instance lifting, multi-party NOF, and *dynamic* cell-probe;
round elimination is the *static asymmetric* induction, unused, and directly targets the batched-query
data structure that HANKEL-BLOCK left as an escape hatch.

### Likely fatal obstruction (to the barrier)
The batched membership game may lack the independent sub-instance (direct-sum) structure round
elimination requires — shared quadratic input (P1513) couples instances ⇒ weak or vacuous bound.

### Minimal falsifying experiment
Construct the asymmetric communication game for batched membership at `L ∈ {8,16,32}`; measure whether
sub-instances are independent (direct-sum holds); positive control = a genuine direct-sum game (round
elimination must bite); negative control = the coupled elliptic game. ≥5 seeds, ordinary prime-order
curves.

### Quantitative promotion gate (to accepted barrier)
Accept if the round-elimination bound gives `α ≥ 3/2` for all `o(log L)`-round backends across all three
`L`.

### Proof track
Theorem: the batched m=5 membership game has round-elimination complexity forcing cell size `L^{Ω(1)}`
at `o(log L)` rounds ⇒ `α ≥ 3/2`.

### Disproof track
A batched backend with `o(log L)` rounds and cell size `L^{o(1)}` solving membership (would need
coupled-instance round elimination to fail).

### Reproduction artifact
Contract `experiment_contract_round_elimination_barrier.md`; impl `round_elimination_barrier.py`;
result `round_elimination_barrier.json`; audit `round_elimination_barrier_audit.py`; ledger `ECFG-P1657`.

---

## 4. Ranking

Scores 0–5 on: **Nov** (distance from prior ledger mechanisms), **Ver** (plausibility of exact
verifier), **Exp** (chance of changing an exponent not a constant), **Path** (complete-path coverage),
**Fals** (toy-scale falsifiability), **Lit** (literature-novelty confidence), **Risk⁻** (freedom from
hidden preprocessing/memory cost; higher = safer). Reject if Nov < 3, or no complete route to descent,
or no rho comparison, or no precise distinction from the closest ledger entry.

| Candidate | Nov | Ver | Exp | Path | Fals | Lit | Risk⁻ | Verdict |
|---|---|---|---|---|---|---|---|---|
| SINGULAR-SERIES-A1 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | **A-winner** |
| DEPENDENT-RANDOM-CHOICE-A2 | 3 | 4 | 2 | 5 | 5 | 3 | 4 | keep |
| COMPRESSED-SENSING-RIP-A3 | 4 | 4 | 3 | 4 | 5 | 4 | 4 | keep |
| BRAUER-MANIN-B1 | 5 | 4 | 3 | 2 | 4 | 5 | 5 | **B-winner** (lane-closure) |
| BAKER-NORINE-GONALITY-B2 | 4 | 4 | 2 | 2 | 4 | 4 | 4 | keep (INCOMPLETE prime-field) |
| CLIFFORD-SPINOR-B3 | 2 | 4 | 2 | 3 | 4 | 2 | 4 | **REJECT** (Nov 2, adjacent Berezin) |
| KOLMOGOROV-INCOMPRESSIBILITY-C1 | 5 | 3 | 4 | 4 | 3 | 5 | 3 | **C-winner** |
| EXPANDER-CODE-SYNDROME-C2 | 4 | 4 | 3 | 4 | 5 | 4 | 4 | keep |
| BORSUK-ULAM-TOPOLOGICAL-C3 | 3 | 3 | 2 | 2 | 3 | 3 | 3 | keep (collapse risk) |
| SINGULAR-SERIES-BARRIER-D1 | 5 | 5 | 5 | n/a | 5 | 5 | 5 | **highest-EV** |
| HAUSSLER-PACKING-BARRIER-D2 | 5 | 4 | 5 | n/a | 4 | 5 | 5 | **highest-EV** |
| ROUND-ELIMINATION-BARRIER-D3 | 5 | 4 | 5 | n/a | 4 | 5 | 5 | **highest-EV** |

**CLIFFORD-SPINOR-B3 rejected** (semantic novelty 2, adjacent to batch11 BEREZIN-PFAFFIAN, cubic-degree
collapse). All others retained as scoped probes; the three barriers carry the highest expected value.

**Selected winners** (per mandate):
1. **Best conservative:** SINGULAR-SERIES-A1.
2. **Best representation-changing:** BRAUER-MANIN-B1.
3. **Best high-risk:** KOLMOGOROV-INCOMPRESSIBILITY-C1.

---

## 5. Winner contracts + first executable commands

> All three winners are **near-certain scoped negatives / lane-closures**, not crossings. They are the
> best *disciplined* probes in their tiers; the honest EV lives in barriers D1/D2/D3. Contracts are
> written so a negative outcome is a first-class, publishable scoped result.

### 5.1 Contract — SINGULAR-SERIES-A1 (`ECFG-P1646`)

```yaml
id: ECFG-P1646
title: Circle-method singular series for the m=5 relation supply exponent
hypothesis: >
  For ordinary E/F_p, the Hardy-Littlewood singular series 𝔖(S5) equals 1 + O(p^{-1/2}),
  so the smooth-relation supply exponent δ equals the occupancy baseline 1/4 (NOT > 1/4).
claim_tier: analysis (no ECDLP recovery claimed)
target_family: ordinary prime-field, prime-order, q≈L^5; exclude anomalous/supersingular/small-CM/low-embedding
design:
  sizes: [L=8, L=16, L=32]
  seeds: 5 per size (deterministic)
  positive_control: torsion-inflated curve family (raises a local factor β_p)
  negative_control: random degree-matched non-Semaev 5-variate variety
  measure: empirical smooth-relation density vs 𝔖 prediction; fit δ(L)
promotion_gate: δ(L) extrapolates > 1/4 with 95% CI excluding 1/4 across all 3 sizes
falsification: δ(L) -> 1/4 (converts to barrier ECFG-P1655/D1)
artifacts:
  implementation: singular_series_supply.py
  result: singular_series_supply.json
  audit: singular_series_supply_audit.py
```

**First command** (dry-run scaffold; no solver, no external calls):

```bash
cd /Volumes/Volume/git/autolab && \
python3 - <<'PY'
# ECFG-P1646 scaffold: compute 𝔖-predicted vs empirical m=5 smooth-relation density, L=8.
# Toy ordinary curve, deterministic seed. Analysis only — no ECDLP recovery.
import itertools, random
p = 1009  # toy ordinary prime; L=8 factor base slice
random.seed(1646)
# placeholder for Sage/ecdlp harness curve object; scaffold prints the plan and the
# singular-series local-factor formula it will evaluate.
print("ECFG-P1646 singular-series supply probe scaffold")
print("targets: L in {8,16,32}, 5 seeds; measure delta(L) vs S = prod_v beta_v")
print("beta_p local factor := (#{S5=0 mod p} / p^4); expect 1 + O(p^-1/2)")
PY
```

### 5.2 Contract — BRAUER-MANIN-B1 (`ECFG-P1649`)

```yaml
id: ECFG-P1649
title: Brauer-group obstruction to a prime-field ECDLP transfer correspondence
hypothesis: >
  Br(E)=0 for smooth E/F_p, so there is no Brauer-Manin obstruction data and no correspondence
  exposing a factor base off the elliptic x-line; the cohomological-transfer lane is empty over F_p.
claim_tier: structural closure (no ECDLP recovery claimed)
target_family: ordinary prime-field, prime-order
design:
  sizes: [L=8, L=16, L=32]
  seeds: 5 per size
  positive_control: char-0 variety with known nontrivial Br (diagonal cubic surface) — pipeline sanity
  negative_control: the elliptic curve (Br=0)
  measure: Br(E)[ℓ] via ℓ-torsion étale pairing; confirm vanishing
promotion_gate: exhibit nonzero Br(E) over F_p AND a correspondence with transfer exponent < 1/2
falsification: Br(E)=0 confirmed -> lane closed by name (scoped negative)
artifacts:
  implementation: brauer_manin_transfer.py
  result: brauer_manin_transfer.json
  audit: brauer_manin_transfer_audit.py
```

**First command:**

```bash
cd /Volumes/Volume/git/autolab && \
python3 - <<'PY'
# ECFG-P1649 scaffold: confirm Br(E)=0 for toy ordinary E/F_p via l-torsion pairing plan.
print("ECFG-P1649 Brauer-Manin transfer-obstruction probe scaffold")
print("plan: for L in {8,16,32}, compute Br(E)[l] = H^2_et(E, mu_l); expect 0 (Lichtenbaum).")
print("positive control: diagonal cubic surface /Q with nontrivial Br (char-0 sanity).")
print("closure: Br(E/F_p)=0 => no cohomological transfer channel. Analysis only.")
PY
```

### 5.3 Contract — KOLMOGOROV-INCOMPRESSIBILITY-C1 (`ECFG-P1652`)

```yaml
id: ECFG-P1652
title: Incompressibility bound on average-case m=5 membership descent length
hypothesis: >
  For a 1-o(1) fraction of random targets, the shortest verified descent certificate has length
  >= L^{1.5} (incompressibility), so no average-case membership backend beats the RT-1476 boundary;
  the constructive direction (short certificates for most targets) is expected FALSE.
claim_tier: average-case query analysis (no ECDLP recovery claimed)
target_family: ordinary prime-field, prime-order; uniform random targets
design:
  sizes: [L=8, L=16, L=32]
  seeds: 5 per size
  positive_control: structured targets with known short certificates (small-order combinations)
  negative_control: uniform random targets
  measure: distribution of shortest verified certificate length; fraction below L^{1.5}
promotion_gate: fraction with sub-L^{1.5} verified certificate = 1-o(1) AND hard-fraction ε=O(L^{-1})
falsification: typical certificate length >= L^{1.5} -> converts to a barrier
artifacts:
  implementation: incompressibility_backend.py
  result: incompressibility_backend.json
  audit: incompressibility_backend_audit.py
```

**First command:**

```bash
cd /Volumes/Volume/git/autolab && \
python3 - <<'PY'
# ECFG-P1652 scaffold: sample random targets, search for descent certificates shorter than L^1.5.
print("ECFG-P1652 incompressibility average-case backend probe scaffold")
print("plan: L in {8,16,32}; for each of N random targets, bounded search for descent program")
print("      of length < L^1.5 symbols; record fraction found + fallback-to-rho fraction.")
print("expected: incompressibility => most certificates >= L^1.5 (barrier, not algorithm).")
PY
```

---

## 6. Red-team — "all three winners are disguised repetitions or cost-negative"

**SINGULAR-SERIES-A1 — disguised batch14 analytic arm + cost-negative.** The δ target and the
smoothness-density object are identical to LARGE-SIEVE-SUPPLY-A1 / BOMBIERI-VINOGRADOV-A3; the "new"
singular series is just the equality behind those inequalities. Cost-negative: over `F_p` the minor arcs
*are* the Weil bound, so `𝔖 = Θ(1)`, `δ → 1/4`, and A1 collapses into its own barrier D1 — it never
crosses. **Verdict: honest value is D1, not A1.** (This is the intended demotion: the meter reduces to
the barrier.)

**BRAUER-MANIN-B1 — disguised batch3 WCDESC + vacuous.** Both are Galois-cohomological transfer
obstructions on the same curve; `H^1` (WCDESC) vs `H^2`/`Br` is a degree relabel of the same "does a
descent/correspondence exist" question. Cost-negative *and vacuous*: `Br(E/F_p) = 0` (finite field) ⇒ no
obstruction data ⇒ INCOMPLETE algorithmic path (no relation source). **Verdict: a lane-closure
statement, not an attack — correctly demoted; its value is naming the closure.**

**KOLMOGOROV-INCOMPRESSIBILITY-C1 — disguised batch13 random-restriction + self-defeating.** Same
average-case-plus-rho-fallback regime as RANDOM-RESTRICTION-C1; the tool swap (description length vs
switching lemma) doesn't change that both need typical targets to have *short* structure, which neither
elliptic membership form provides. Worse: incompressibility is a *lower-bound* method — rigorously it
proves certificates are *long*, so the constructive claim is self-contradictory. **Verdict:
self-defeating as an attack; its rigorous output is a barrier.**

**Cross-cutting red-team.** All three winners, like every winner since batch8, resolve to *scoped
negatives or lane closures*, not exponent crossings. This is the correct, honest reading of a saturated
program: the marginal value of an attack candidate is now near zero, and the marginal value of a
*first-of-kind barrier that closes a live gate* is high. D1 (circle-method supply ceiling → RT-1472),
D2 (packing → RT-1476 sample class), D3 (round elimination → RT-1476 low-round data-structure class)
are the three highest-EV items in this report.

---

## 7. Claim discipline

- **Correctness ≠ performance.** No candidate claims a complete-cost single-target rho speedup. Every
  "backend"/"supply" number is a *predicted* exponent to be measured at toy scale.
- **Candidate relations ≠ verified ECDLP recovery.** Any relation produced under these contracts is
  re-verified by the run wrapper per `docs/claims-and-verification.md`; no evidence record may assert
  above its claim tier.
- **Toy evidence stays toy-scoped.** `L ∈ {8,16,32}` results are never presented as crypto-scale.
- **Timeouts/crashes are not negative mathematical evidence.**
- **A failed candidate is a scoped negative**, not evidence that prime-field ECDLP is unimprovable.
- **Both live gates RT-1472 and RT-1476 remain open. No break is claimed.** This report imports 11
  ledger-new technology families and closes (conditionally, pending the D-experiments) three sub-classes
  of the two gates; it does not open a crossing.

---

## 8. Ledger IDs minted this report

`ECFG-P1646` (SINGULAR-SERIES-A1) · `ECFG-P1647` (DEPENDENT-RANDOM-CHOICE-A2) ·
`ECFG-P1648` (COMPRESSED-SENSING-RIP-A3) · `ECFG-P1649` (BRAUER-MANIN-B1) ·
`ECFG-P1650` (BAKER-NORINE-GONALITY-B2) · `ECFG-P1651` (CLIFFORD-SPINOR-B3, REJECTED) ·
`ECFG-P1652` (KOLMOGOROV-INCOMPRESSIBILITY-C1) · `ECFG-P1653` (EXPANDER-CODE-SYNDROME-C2) ·
`ECFG-P1654` (BORSUK-ULAM-TOPOLOGICAL-C3) · `ECFG-P1655` (SINGULAR-SERIES-BARRIER-D1) ·
`ECFG-P1656` (HAUSSLER-PACKING-BARRIER-D2) · `ECFG-P1657` (ROUND-ELIMINATION-BARRIER-D3).

These are **report-proposed** IDs (uncommitted). Per harness rules they are not official ledger records
until the Coordinator commits them; this file is an uncommitted research artifact.
