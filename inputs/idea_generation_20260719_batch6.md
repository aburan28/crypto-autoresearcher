# Idea Generation — ECDLP over ordinary prime fields — 2026-07-19 batch6 (report 14 / batch 12)

Research Director empirical-cryptanalysis run. Target: a non-generic single-target
algorithm whose **complete** cost beats Pollard-rho `~0.886*sqrt(n)` group ops.
Toy correctness, a new coordinate system, a relation certificate, faster
preprocessing, or a solver swap alone is **not** a breakthrough.

Authorized scope only: generated toy curves, public benchmark instances,
synthetic data. No wallets/keys/accounts.

---

## 0. Input review and machine-readable inventory

### 0.1 Files read this run

1. `/Volumes/Volume/git/autolab/research_ledger.md` (~2478 lines; committed frontier ~P1486; gate rows ECFG-RT-1472, ECFG-RT-1476, ECFG-RT-1485).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (~720 lines; frontier P1509–P1513, plus NR-1500..1508).
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (PO-transfer-001..006 closeouts; the Prym/trace-zero/cover lane).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json` (~113 lines, 12 keyed entries).
5. All 13 prior idea-generation reports `research/idea_generation_2026071{7,8,9}*.md` via the running anti-dup catalogue in memory `ecdlp-idea-generation-reports`.

### 0.2 Entries reviewed and ID families covered

- **Main ledger** `ECFG-*`: gate rows RT-1472, RT-1476, RT-1485; committed frontier through P1486; **~1470 numbered `P####` fingerprints scanned**.
- **IC-state ledger** `ECFG-NR-1500..1508` + `ECFG-P1509..P1513` (+ R-suffixed refinements P1510-R1, P1511-R1, P1511-R2, P1512-R1). This is the live index-calculus frontier (**14 core records + 6 refinements**).
- **Report P-IDs** through **ECFG-P1609** (batch11). This report proposes **ECFG-P1610..P1621**.
- **Transfer program**: PO-transfer-001..036+ contracts, NR-1500..1508, ECDLP-IDEA-049..117 (Prym/trace-zero/cover lane, closed or cost-negative).
- **ID families covered**: `ECFG-P` (main + report), `ECFG-NR` (IC-state transfer negatives), `ECFG-RT` (conditional-theorem gates), `PO-transfer-###`, `ECDLP-IDEA-###`.
- Prior-report mechanism lanes: **~60 distinct lanes across 13 reports** (memory catalogue). For each ledger entry I extracted mechanism / representation / exploited structure / factor base / relation shape / relation-generation method / compression method / linear-algebra object / target-descent method / cost bottleneck / outcome / scoped negative boundary / next branch; the machine-readable form is the memory catalogue plus §0.4 below.

**Barrier & representation technologies already spent (do not re-propose):** border / slice / asymptotic-spectrum / analytic-partition / noncommutative-inner rank; communication lifting + 5-party NOF + internal-information direct-sum; VC / Sauer-Shelah; approximate degree + dual polynomials + probabilistic polynomials; Shearer / Lang-Weil / hypergraph-container / matroid-union / Delsarte-LP / additive-energy / Croot-Sisask / Barvinok supply & entropy; p-adic Adolphson-Sperber + Ax-Katz; Nullstellensatz-degree + PolyCalc/IPS + combinatorial-NSS; τ-conjecture-roots; arithmetic-circuit LB (shifted partials, Nisan noncommutative-ABP width, Raz random-partition multilinear, depth-reduction chasm, elusive functions, algebraic natural proofs); GCT occurrence + GKZ D-module holonomic rank; restriction/Kakeya; matching-vector codes; Elekes-Szabó; fine-grained OV/3SUM; Valiant rigidity; sign-rank/γ2; syzygy/Betti; SOS/Lasserre SDP; apolarity/catalecticant; Coppersmith lattice; LDC local decodability; low-degree likelihood ratio; Berezin/Pfaffian/matchgate; Lorentzian log-concave; Ore/skew resultant; proof-complexity space / red-blue pebbling.

### 0.3 The only two live rho-crossing surfaces (unchanged since batch4)

Both are **conditional, unrealized** theorems in `research_ledger.md`:

- **RT-1472** (2-large-prime enrichment): exact cost exponent `max(2*ell, 1-ell, 1+1/5-2*ell)`, minimized at `ell=1/3` giving `2/3`. Crossing requires an enrichment `delta>1/4` at `L=q^{1/5}`; the honest summation graph is a.a.s. subcritical (`delta=0`). **Meter target: delta.**
- **RT-1476** (m=5 membership backend): optimum `ell=1/m`, total `(1+alpha)/m`; m=5 crosses rho iff query exponent `alpha<3/2`. **Meter target: alpha.**

(RT-1485 is a *closed* Kummer-companion negative — constant fibers, quadratic key/source support, source slope exactly 2 — reconfirming that the explicit differential Kummer state is not a sub-`L^{1.5}` object. Not a live crossing surface; used only as a negative control.)

### 0.4 The IC-state frontier chain, restated as one obstruction

The P1509–P1513 chain is one story:
- **P1510-R1**: an exact **per-target** truncated marked-resultant compiler exists — `O(r^2 + r*M(r)*log r)` work, `O(r^2)` state — a genuine output-sensitive summation-polynomial FFE primitive. Independently verified, `15/15` component hashes.
- **P1511-R1/R2**: every route to share/batch it across the `Theta(r)` relation rows re-materializes a **product-circuit input of degree `r^3`** (`r^3` provenance leaves); favorable degree-`r` gcd output does **not** remove the cubic input floor. Leaf-count / rho ratio is `sqrt(r)`. Batching `= Theta(r^3)=Theta(q^{3/5})` — above rho. FD-width and factorized-semijoin branches closed.
- **P1512-R1**: the scalar-**linear** source-labelled Chow/Tate atomizer carries the **full canonical-multiset cycle payload** `L=binom(2r+4,5)=Omega(r^5)`; standard determinant control `deg(det M) <= dim(M)` forces a degree-`r^3` batch object to cubic matrix dimension. **Closed** (`m>=ceil(binom(2r+4,5)/3)=Omega(r^5)`). The **single** surviving representational escape is a **target-specialized NONLINEAR circuit** computing the shared object below `r^3` without materializing the `r^2` leaves per target.
- **P1513**: the shared bivariate input circuit `H(U,W)` is exactly **quadratic** (`r^2` leaves), but both explicit norms `N_T=Res_U(T,H)`, `N_F=Res_U(F,H)` remain **cubic**. Open theorem gate: an output-sensitive common-norm recurrence below `r^{5/2}`.

**Consolidated batch12 restatement (continuing batch10/11's decoupling program).** Every prior *attack* winner probes the surviving P1512-R1 nonlinear-circuit exception with a functional the report argues is *decoupled from `deg(det)<=dim`* (batch11: nc-rank via operator scaling, Berezin/Pfaffian; batch10: dequantized stable rank; batch9: NSS certificate). Every prior *barrier* imports a lower-bound resource unused before it. Both arms are now deep. Batch12's marginal contribution is to import functional families that are **indifferent to shape rather than degree**, from three technology areas untouched by all 13 reports:

1. **Extremal-set compression** — Kruskal-Katona *shadow density*, Bollobás *set-pair* exterior dimension, and Alweiss-Lovett-Wu-Zhang *sunflower-free* bounds. These meter RT-1472 δ by the **shape** of the relation family (shadows, cross-intersections, sunflowers), a family of bounds orthogonal to every entropy/count/energy supply meter already spent.
2. **Resource-tradeoff lower bounds new to the program** — dynamic **cell-probe** (Larsen chronogram; a memory-probe tradeoff distinct from batch11's static circuit-space pebbling) and **quantum query / span-program** witness size (`Q(f) <= R(f)` gives a rigorous classical `alpha` floor; span programs also give constructive quantum backends).
3. **LP-hierarchy and character-weighted-determinant representations** — **Sherali-Adams** lift-and-project LP pseudo-distributions (an LP hierarchy strictly cheaper than the SOS SDP spent in batch4) and the **immanant** `d_lambda` (a character-weighted determinant interpolating det↔perm; **not** subject to `deg(det)<=dim`, and distinct from Pfaffian/matchgate).

Fine-grained **k-hyperclique** (k=5 is the natural arity of the membership, distinct from the 2-quantifier OV/3SUM of batch6) closes the barrier arm.

### 0.5 Claim discipline

Nothing below is a break. Every candidate is a scoped, falsifiable meter or barrier on RT-1472/RT-1476. Toy evidence, heuristics, and restricted models are labelled. A failed candidate is a scoped negative result, never evidence that prime-field ECDLP cannot be improved. Correctness of an evaluator, a relation certificate, or a preprocessing win is explicitly **not** a promotion gate anywhere below; only a measured exponent or complete-cost trend that could cross `1/2` is.

---

# GROUP A — Conservative extensions of known work

## Candidate: KRUSKAL-KATONA-SHADOW-A1  *(conservative winner)*

### One-sentence mechanism
Exploit the **Kruskal-Katona shadow bound** — the extremal density of the lower shadow of a uniform set family — to cap the number of complete `L`-smooth relations any 2-large-prime enrichment can hold (subproblem P = RT-1472 δ), so `delta>1/4` is possible only if the enriched relation hypergraph's shadow **exceeds** the compression-optimal shape, which the honest elliptic incidence provably does not (baseline B = rho `q^{2/3}`).

### Status
HYPOTHESIS (as an exact δ supply ceiling). The Kruskal-Katona / shifting theorem is a THEOREM.

### Novelty classification
POSSIBLY NOVEL (documented search: shadow/compression bounds unused on ECDLP; distinct from every entropy/count/energy supply meter already spent).

### Semantic fingerprint F(C)
- algebraic object: the `k`-uniform relation hypergraph `R` whose vertices are `L`-smooth factor-base primes and whose edges are complete relations;
- available public operations: enumerate incidences, compute the lower shadow `∂R` (sub-relations obtained by deleting one prime);
- hidden structure exploited: **shadow density / colex-compression optimality** of `R`;
- information discarded: which specific primes; kept only the family's profile `(|R|, |∂R|)`;
- information retained: the shadow-vs-size ratio;
- relation-generation primitive: none — this is a supply ceiling;
- compression primitive: colex shifting (the KK extremal operation);
- rank mechanism: n/a (extremal-set, not matrix rank);
- descent mechanism: n/a;
- dominant cost exponent: `delta` via the maximal shadow-consistent `|R|`.

### Nearest ledger entries
1. **SHEARER-D3 (batch8)** — Shearer submodular *entropy* ceiling. KK is a *shadow-density* extremal bound, not an entropy inequality; the two are distinct combinatorial functionals (entropy bounds projections; KK bounds one-element shadows via compression). Distinct object.
2. **CONTAINER-CEILING-A3 (batch9)** — hypergraph container δ-ceiling. Containers bound independent sets via a container family; KK bounds shadows via shifting. Different extremal machinery, different quantity.
3. **DELSARTE-LP-A2 (batch8)** — coding-LP supply ceiling. LP bounds via distance distribution / MacWilliams; KK bounds via colex order. Distinct.
4. **ENERGY-D1 (batch3)** — additive-energy supply ceiling. Energy is a second-moment count; KK is a shadow shape bound. Distinct.
5. **MATUNION-A2 (batch5)** — matroid-union independence. Distinct (matroid rank vs shadow density).

Exact distinction: no prior entry meters δ by the **shadow/compression** profile of the relation family; all prior supply meters bound *counts* or *entropy*, not the size-vs-shadow relation that KK pins exactly.

### Nearest literature
- Kruskal (1963), Katona (1968) shadow minimization; Frankl's shifting/compression method; the Lovász form `|∂R| >= binom(x, k-1)` for `|R|=binom(x,k)`.
- Bollobás-Thomason and hypergraph-degree extensions.
- Gap: KK is stated for uniform families on abstract ground sets; the elliptic relation family has algebraic constraints (each edge is a genuine summation-to-`O` incidence), so the *achievable* shadow may be far below the KK extremal bound — which only helps the ceiling (δ smaller), but the two-sided version (does the enrichment push the shadow toward extremal?) needs the honest-graph shadow measured.

### Target family
Ordinary prime-field `E/F_p`, prime order `n`, `L=q^{1/5}`, honest vs 2-LP-enriched summation graph. Excludes supersingular / anomalous / small-embedding-degree and any curve with leaked `E[k]` structure (NR-1501 gcd conditions).

### Full algorithmic path
1. **factor base**: `L`-smooth relation primes as the ground set.
2. **relation generation**: n/a — A1 is a supply ceiling over any generator.
3. **witness extraction/verification**: each enumerated incidence is an exact P1510 relation (verified).
4. **relation probability**: bounded above by the max `|R|` consistent with the measured shadow.
5. **matrix dims/density/rank**: n/a (the point is that no matrix stage is reached if supply `< L`).
6. **factor-log calibration**: n/a.
7. **individual log / descent**: n/a (supply, not descent).
8. **offline/online**: offline shadow enumeration on toy cells; online n/a.
9. **memory/parallelism**: `O(|R|)` edge storage; shadow computation streaming.

Complete (all stages accounted; stages 2,4–7 are "n/a — supply ceiling", not missing).

### Cost model
δ enrichment at `ell=1/3` needs `|R| >= L^{1+delta}` with `delta>1/4`, i.e. shadow-consistent supply above `L^{5/4}`. If the measured honest+enriched shadow forces `|R| = O(L^{1+1/4})` or below, then `delta<=1/4` ⇒ rho exponent stays `2/3`. vs rho `q^{2/3}`; vs BSGS `q^{1/2}` memory; vs nearest IC baseline (subcritical honest graph `delta=0`).

### Why existing negatives do not already kill it
Shearer/container/Delsarte/energy bound *how many* relations or *how much entropy*; none uses the size↔shadow compression identity, which is a **sharper, shape-sensitive** ceiling that can rule out an enrichment even when the crude count is permissive. New operation: colex shifting / shadow computation.

### Likely fatal obstruction
KK is tight only for colex-initial-segment families; the elliptic relation family is far from a colex segment, so KK gives a *loose* (over-permissive) ceiling that admits `delta>1/4` numerically — an **inconclusive** ceiling, not a barrier. It would still produce the first shadow-profile datum on the honest graph.

### Minimal falsifying experiment
Toy sizes `r in {4,8,16}` (`q ~ r^5`, primes `{1031, 32771, 1048583}`), seeds `{20260719..20260723}`. Enumerate the honest and 2-LP-enriched `L`-smooth relation hypergraphs; compute `(|R|, |∂R|)` and the KK-implied max `|R|`. **Positive control**: a colex-initial family (shadow must hit KK exactly). **Negative control**: a random `k`-uniform family of the same size (shadow strictly above KK minimum). Ordinary prime-order controls throughout.

### Quantitative promotion gate
Measured max shadow-consistent supply exponent `1+delta_hat` fit across the three sizes **crosses `5/4` downward** (i.e. `delta_hat<1/4` certified by the KK ceiling), *or* the enriched family's shadow is shown to require `delta>1/4` supply that the ceiling forbids. Correctness / enumeration completeness alone is NOT the gate.

### Proof track
Theorem: the honest and 2-LP-enriched elliptic relation `k`-hypergraph has `|R| <= binom(x, k)` with `x` forcing `|R| = O(L^{1+1/4})`, so `delta<=1/4` unconditionally at `L=q^{1/5}`. (This form doubles as barrier D-adjacent evidence.)

### Disproof track
Exhibit an enriched relation family whose measured `(|R|,|∂R|)` is consistent with `|R| = Omega(L^{1+1/4+eps})` — that would license the RT-1472 enrichment (report immediately, cross-check against the honest subcriticality result).

### Reproduction artifact
- contract `ecdlp_index_calculus_state/experiment_contract_p1610_kruskal_katona_shadow_delta_ceiling.md`
- impl `tasks/ecdlp_index_calculus/p1610_kruskal_katona_shadow.py`
- result `p1610_kruskal_katona_shadow.json`
- audit `p1610_kruskal_katona_shadow_audit.py`
- ledger `ECFG-P1610`.

---

## Candidate: BOLLOBAS-SETPAIR-A2

### One-sentence mechanism
Exploit the **Bollobás set-pair inequality** (and its skew/exterior-algebra form) to upper-bound the number of *critical* source-labelled relation pairs `(A_i, B_i)` with `A_i ∩ B_j = ∅ iff i=j` in the 2-large-prime advice graph, giving an exact ceiling on the source-label state and hence the enrichment δ (subproblem P = RT-1472 δ / the source-label state P1506 measures).

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW (Bollobás set-pairs / skew cross-intersection inequality unused; distinct from VC and syzygy).

### Semantic fingerprint F(C)
- algebraic object: the family of cross-intersecting pairs `{(A_i, B_i)}` where `A_i` is a relation's small-prime support and `B_i` its large-prime advice;
- available public operations: test disjointness `A_i ∩ B_j`, build the exterior/tensor witness vectors;
- hidden structure exploited: **cross-intersection criticality** (Bollobás dimension bound `sum 1/binom(a_i+b_i, a_i) <= 1`);
- information discarded: the intersection contents;
- information retained: the incidence pattern of the pair system;
- relation-generation primitive: none (state ceiling);
- compression primitive: exterior-algebra generic-hyperplane argument (Lovász's proof);
- rank mechanism: dimension of a generic exterior/tensor span;
- descent mechanism: n/a;
- dominant cost exponent: the maximal critical-pair count exponent → δ.

### Nearest ledger entries
1. **VCDIM-D3 (batch7)** — Sauer-Shelah shattering. Bollobás bounds *cross-intersecting critical pairs*, a different extremal quantity from shattered sets. Distinct combinatorial functional.
2. **SIGNRANK-GAMMA2-B3 (batch4)** — γ2 factorization-norm / Zarankiewicz pincer. Bollobás is an exterior-dimension inequality, not a matrix-norm bound. Distinct.
3. **WEDGE / P1506 (NR-1506)** — the exterior source-label expansion had state `= binom(B,2)`. Bollobás bounds the *number of usable critical pairs* below that surface — a complementary extremal cap, not the same wedge identity.
4. **SYZYGY-REGULARITY-B2 (batch4)** — Betti table. Distinct (free resolution vs set-pair dimension).
5. **DELSARTE-LP-A2 (batch8)** — coding LP. Distinct.

Distinction: no prior entry uses the **Bollobás/skew set-pair exterior-dimension** bound on the advice-graph pair system.

### Nearest literature
- Bollobás (1965) set-pair inequality; Frankl's skew version; Lovász's tensor/exterior-algebra proof (generic hyperplanes); Füredi's uniform-cover extensions.
- Gap: the inequality bounds *critical* (tight cross-intersecting) pairs; the 2-LP advice pairs may not be critical (they can share large primes across rows), weakening the bound to vacuous unless a criticality-reduction is proven.

### Target family
As A1; ordinary prime-field, `L=q^{1/5}`.

### Full algorithmic path
1. factor base = `L`-smooth primes; 2. n/a (state ceiling); 3. verified per pair; 4. bounded by the set-pair inequality; 5. n/a; 6. n/a; 7. n/a; 8. offline pair-system assembly; 9. `O(#pairs)`.
Complete (state ceiling).

### Cost model
If the max critical-pair count is `O(L^{1+1/4})` then the source-labelled enrichment cannot exceed `delta=1/4` ⇒ rho `2/3` unbeaten. If the pairs are non-critical and the bound is vacuous, no ceiling. vs rho `q^{2/3}`.

### Why existing negatives do not already kill it
VC bounds shattering (worst-case labelings); Bollobás bounds *simultaneously-critical* pairs, exactly the structure a 2-LP enrichment would need to be information-dense. Never metered.

### Likely fatal obstruction
Real 2-LP advice pairs share large primes (they are not a critical cross-intersecting system), so the Bollobás inequality is not tight and returns a vacuous ceiling. Near-certain, but the *criticality fraction* is itself a first-time datum.

### Minimal falsifying experiment
`r in {4,8,16}`; build the honest and enriched advice-pair systems; measure the fraction that is cross-intersecting-critical and the Bollobás-implied max. **Positive control**: a synthetic critical pair system (must saturate the inequality). **Negative control**: a random shared-prime system (bound vacuous). Seeds `{20260719..}`.

### Quantitative promotion gate
Critical-pair exponent fit crosses `5/4` downward with the inequality certifying `delta<=1/4`. A vacuous (non-critical) system is a clean scoped negative on the enrichment structure.

### Proof track
Lemma: the source-labelled 2-LP pairs form a critical cross-intersecting family ⇒ `sum 1/binom(a_i+b_i,a_i) <= 1` bounds their number by `O(L^{5/4})`.

### Disproof track
Show the pairs are non-critical (shared large primes) ⇒ inequality vacuous (expected).

### Reproduction artifact
contract `..._p1611_bollobas_setpair_state_ceiling.md`; impl `p1611_bollobas_setpair.py`; result/audit; ledger `ECFG-P1611`.

---

## Candidate: DISCREPANCY-CORRUPTION-A3

### One-sentence mechanism
Exploit the **communication discrepancy / corruption bound** of the two-party (source-holder vs evaluator) m=5 membership predicate to lower-bound its randomized communication, hence — via a query-to-communication reduction — its query exponent `alpha` (subproblem P = RT-1476 α), so `alpha<3/2` requires the membership matrix to have discrepancy above a threshold the elliptic incidence structure does not reach.

### Status
HYPOTHESIS (meter). Discrepancy and corruption bounds are THEOREMS.

### Novelty classification
LITERATURE-ADJACENT (communication lane exists; the **discrepancy/corruption** functional is unused — prior communication work used lifting, NOF, internal-information, and sign-rank).

### Semantic fingerprint F(C)
- algebraic object: the 2-party membership sign matrix `M[x,y] = [T(x,y) member]`;
- available public operations: evaluate the predicate on a distribution, compute rectangle discrepancy / corruption;
- hidden structure exploited: **spectral / rectangle discrepancy** of `M`;
- information discarded: which side holds which sources;
- information retained: the average bias over rectangles;
- relation-generation primitive: none (LB meter);
- compression primitive: none;
- rank mechanism: `||M||` spectral norm / max-rectangle bias (NOT sign-rank);
- descent mechanism: same predicate per target;
- dominant cost exponent: `alpha` via `log(1/disc)`.

### Nearest ledger entries
1. **LIFTING-D1 (batch7)** — query→communication lifting. A3 uses the *communication* discrepancy directly (the target of lifting), a distinct bound; discrepancy lower-bounds randomized/BPP-communication, lifting transports a *query* bound. Distinct direction.
2. **SIGNRANK-GAMMA2-B3 (batch4)** — sign-rank / γ2 (bounds UPP / unbounded-error). Discrepancy bounds *bounded-error* (BPP) communication — a different, incomparable regime. Distinct functional.
3. **NOF-COMM-D2 (batch8)** — 5-party NOF cube norm. A3 is 2-party discrepancy. Distinct axis.
4. **DIRECTSUM-INFO-A2 (batch11)** — internal-information direct-sum. Discrepancy is a single-instance rectangle bound, not an amortized-info bound. Distinct.
5. **APPROXDEG-D1 (batch8)** — approximate degree. Discrepancy and approx-degree are related but distinct (γ2 vs rectangle bias); the specific corruption argument is unused.

Distinction: no prior entry uses the **rectangle discrepancy / corruption** communication functional.

### Nearest literature
- Babai-Frankl-Simon (discrepancy method); Klauck (corruption / one-sided-error bound); Chattopadhyay-Pitassi survey; Sherstov "pattern matrix" method connecting approx-degree to discrepancy.
- Gap: discrepancy lower-bounds *communication*, and converting to a *query* `alpha` needs a tight lifting theorem for this specific predicate; the gadget overhead may loosen the bound below `3/2`.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`. Excludes curves with symmetric membership matrices that inflate discrepancy artificially.

### Full algorithmic path
1. factor base = deck split across two parties; 2. n/a (meter); 3. verified per query; 4. n/a; 5. n/a; 6. n/a; 7. same predicate per descent; 8. offline matrix build, online communication; 9. `O(r^2)` matrix storage on toy cells.
Complete (meter).

### Cost model
If corruption gives randomized communication `C = Omega(r^{3/2})`, then via lifting `alpha >= 3/2` and `(1+alpha)/5 >= 1/2` = rho. Crossing needs discrepancy large enough that `C = o(r^{3/2})`. vs rho `q^{1/2}`.

### Why existing negatives do not already kill it
Sign-rank (batch4) bounds the *unbounded-error* regime and approx-degree the polynomial regime; the *bounded-error rectangle discrepancy* is a distinct, often stronger bound for structured predicates, never applied here.

### Likely fatal obstruction
The membership matrix may have high discrepancy (small max-rectangle bias) yet still admit a cheap query algorithm through the *structured* (non-worst-case) inputs the backend actually sees — discrepancy is a worst-case-distribution bound and may not transfer to the elliptic input distribution, giving `alpha=Omega(1)` below `3/2` (inconclusive).

### Minimal falsifying experiment
`r in {4,8,16}`; build `M`, estimate discrepancy under the uniform and elliptic input distributions. **Positive control**: inner-product matrix (discrepancy `2^{-Theta(n)}`, communication `Omega(n)`). **Negative control**: a low-rank / structured matrix (discrepancy `Omega(1)`, cheap). Seeds `{20260719..}`.

### Quantitative promotion gate
Estimated `log(1/disc)/log r` fit crosses `3/2` (upward = barrier, downward-with-cheap-protocol = crossing candidate) across sizes. Correctness of the protocol alone is not the gate.

### Proof track
Theorem: the m=5 membership matrix has corruption bound giving randomized communication `Omega(r^{3/2})` under the elliptic distribution ⇒ `alpha>=3/2`.

### Disproof track
A low-discrepancy structured sub-block admitting an `o(r^{3/2})` protocol (⇒ query crossing candidate).

### Reproduction artifact
contract `..._p1612_discrepancy_corruption_alpha_meter.md`; impl `p1612_discrepancy_corruption.py`; result/audit; ledger `ECFG-P1612`.

---

# GROUP B — Genuine representation changes

## Candidate: SHERALI-ADAMS-PSEUDODIST-B1

### One-sentence mechanism
Represent the enriched relation set by a **Sherali-Adams lift-and-project LP pseudo-distribution** of degree `t` (not the SOS SDP), so a degree-`t=O(1)` feasible SA pseudo-distribution over `L`-smooth relations would sample `delta>1/4` enrichment in `L^{O(t)}` LP time (subproblem P = RT-1472 δ; baseline B = rho `2/3`).

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW (Sherali-Adams LP hierarchy unused; distinct from SOS/Lasserre SDP and coding-LP).

### Semantic fingerprint F(C)
- algebraic object: the SA degree-`t` pseudo-distribution `μ` over relation indicator variables;
- available public operations: solve the SA LP relaxation, extract marginals;
- hidden structure exploited: **LP-hierarchy pseudo-marginals** consistent up to `t`-wise;
- information discarded: `>t`-wise correlations;
- information retained: `t`-wise consistent marginals;
- relation-generation primitive: LP-rounding / conditioning of `μ`;
- compression primitive: the polytope's low-degree face structure;
- rank mechanism: n/a (LP feasibility, not SDP PSD-ness);
- descent mechanism: n/a;
- dominant cost exponent: `delta` via SA rounding success at degree `t`.

### Nearest ledger entries
1. **SOS-LASSERRE-A1 / SOS-LB-D1 (batch4)** — moment-SOS **SDP** hierarchy. SA is the strictly-weaker, strictly-cheaper **LP** hierarchy (no PSD constraint); its integrality behavior and cost are different, and an SA solution rounds via conditioning, not eigen-decomposition. Distinct hierarchy and distinct rounding.
2. **DELSARTE-LP-A2 (batch8)** — a *single-level* coding LP (MacWilliams), not a lift-and-project hierarchy. SA lifts to degree `t`. Distinct.
3. **LDLR-DELTA-METER-A3 (batch11)** — low-degree likelihood ratio. SA is an optimization relaxation, LDLR a spectral detection statistic. Related in the low-degree world but distinct objects (SA rank vs LDLR norm).
4. **CONTAINER / MATUNION** — combinatorial; SA is convex-relaxation. Distinct.
5. **RT-1472-CYCLEMAT-A2** — cycle-basis enrichment; B1 asks whether that enrichment is SA-roundable.

Distinction: no prior entry uses the **Sherali-Adams LP hierarchy** as a δ representation.

### Nearest literature
- Sherali-Adams (1990) reformulation-linearization; Laurent's comparison of LP/SDP hierarchies; Charikar-Makarychev-Makarychev and Grigoriev SA integrality-gap lower bounds; Chan-Lee-Raghavendra-Steurer LP-extension lower bounds.
- Gap: SA relaxations of *dense* structured CSPs often have large integrality gaps at low degree; whether the elliptic enrichment polytope is SA-roundable at `O(1)` degree is open (and the barrier D2 below is the likely answer).

### Target family
Ordinary prime-field, `L=q^{1/5}`, enriched 2-LP relation polytope.

### Full algorithmic path
1. factor base = `L`-smooth edges; 2. solve SA-degree-`t` LP, round to relations; verify; 3. exact; 4. relation prob = rounding success; 5. `Theta(L)` variables; 6. standard; 7. n/a; 8. offline LP; 9. `L^{O(t)}` LP memory.
Complete.

### Cost model
If SA degree `t=O(1)` rounds to `delta>1/4` enrichment, LP cost `L^{O(1)}` and RT-1472 crosses. If SA gap persists to degree `Omega(L^{1/4})`, no cheap LP certifies enrichment ⇒ δ≤1/4. vs rho `2/3`.

### Why existing negatives do not already kill it
The SOS/SDP work (batch4) bounds the *SDP* hierarchy; the LP hierarchy is incomparable in general (weaker relaxation, cheaper solve) and can succeed where SDP rounding is analyzed differently, or fail with a *cheaper* certificate — either way new data.

### Likely fatal obstruction
SA is weaker than SOS, so if SOS already showed a δ gap, SA has at least as large a gap ⇒ no low-degree LP rounds the enrichment (this is exactly barrier D2). B1 most likely returns a scoped negative confirming the gap at lower cost.

### Minimal falsifying experiment
`r in {4,8,16}`; solve SA degree `t in {2,3,4}` on the enriched vs honest polytope; measure rounding-recovered enrichment. **Positive control**: a genuinely SA-roundable planted dense subgraph. **Negative control**: a random sparse graph (SA gap). Seeds `{20260719..}`.

### Quantitative promotion gate
Rounded enrichment `delta_hat>1/4` at `t=O(1)` across sizes. Any persistent gap is a scoped negative (feeds D2).

### Proof track
Theorem: the enrichment polytope has SA rank `O(1)` (roundable) — or its negation (integrality gap to degree `q^{1/4}`).

### Disproof track
Exhibit the SA integrality gap at degree `q^{1/4}` (⇒ D2 barrier).

### Reproduction artifact
contract `..._p1613_sherali_adams_pseudodist_delta.md`; impl `p1613_sherali_adams_pseudodist.py`; result/audit; ledger `ECFG-P1613`.

---

## Candidate: IMMANANT-INTERPOLATION-B2  *(representation winner)*

### One-sentence mechanism
Represent the batched five-point incidence count as an **immanant** `d_lambda(M)` (a Young-character-weighted sum over `S_n`, interpolating determinant `lambda=(1^n)` and permanent `lambda=(n)`) of the incidence matrix rather than its determinant, so if the count equals a **near-hook / small-Young-diagram** immanant — a functional **not** subject to `deg(det)<=dim` — it evaluates below the `Omega(r^5)` cycle-payload floor P1512-R1 proved for the determinant (subproblem P = the P1512-R1 nonlinear-circuit exception; baseline B = rho `r^{5/2}`).

### Status
HYPOTHESIS.

### Novelty classification
POSSIBLY NOVEL (documented search: immanants / character-weighted determinants unused on ECDLP; distinct from determinant P1512, Pfaffian/Berezin batch11, permanent-matchgate P1504, and Schur/plethysm batch7 which expanded symmetric functions, not a matrix immanant).

### Semantic fingerprint F(C)
- algebraic object: the incidence matrix `M(x)` with entries the signed source markers, evaluated by `d_lambda(M) = sum_{sigma in S_n} chi_lambda(sigma) prod_i M[i,sigma(i)]`;
- available public operations: evaluate `d_lambda` for a chosen partition `lambda` (Hartmann / Bürgisser-style immanant evaluation);
- hidden structure exploited: **character weighting** that can suppress the `Omega(r^5)` cycle payload the determinant carries;
- information discarded: the full determinant expansion;
- information retained: the `chi_lambda`-weighted permutation sum;
- relation-generation primitive: nonzero immanant support = incidence;
- compression primitive: the immanant's Young-diagram-controlled complexity (Bürgisser dichotomy);
- rank mechanism: immanant value (NOT `deg(det)`-capped);
- descent mechanism: same immanant per target;
- dominant cost exponent: `beta_imm(lambda)` in `r`.

### Nearest ledger entries
1. **P1512-R1** — scalar-linear Chow atomizer closed at `Omega(r^5)` by `deg(det M)<=dim(M)` on the **determinant**. B2 replaces the determinant by an **immanant** `d_lambda`, whose degree/complexity obeys a **different** (Bürgisser-Curticapean) dichotomy, not `deg(det)<=dim`. This is a precise, named instance of the surviving target-specialized nonlinear-circuit exception.
2. **BEREZIN-PFAFFIAN-C1 (batch11)** — Pfaffian = `sqrt(det)` of a skew matrix (character `lambda` trivial-signed on a matching structure). The immanant is a *different* character family (general `lambda`), not the Pfaffian. Distinct functional.
3. **P1504 (matchgate/permanent)** — permanent is the `lambda=(n)` extreme (matchgate Boolean signatures), shown to have zero shared-GL2 bases. B2 uses **intermediate** `lambda` (near-hook), the untested middle of the det↔perm interpolation. Distinct.
4. **NONCOMMUTATIVE-RANK-B2 (batch11)** — free-skew inner rank. Immanant is a commutative character-weighted functional; distinct object and distinct evasion of the determinant cap.
5. **SCHURPLETHYSM-B3 (batch7)** — Schur/plethysm symmetric-function *expansion*. The immanant is a *matrix functional*, not a symmetric-function decomposition of the polynomial. Distinct.

Exact distinction: B2 is the only candidate that evaluates a **character-weighted determinant** of the incidence matrix; `deg(det)<=dim` — the exact lever of P1512-R1 — does not bound immanants.

### Nearest literature
- Littlewood (immanants); Bürgisser "The computational complexity of immanants" (SIAM J. Comput.) — dichotomy: immanants of partitions far from `(1^n)` are VNP-hard, near-hook immanants are in VP-ish regimes; Hartmann's algorithm; Brylawski-Lascoux; Curticapean-Marx immanant / Holant dichotomy; Merris-Watkins immanant inequalities.
- Gap: Bürgisser's dichotomy says the *interesting* immanants (far from det) are hard; the crux is whether the elliptic incidence count is a **near-hook** (easy) immanant or a far-from-det (hard) one — the latter reproduces the `r^3`/`r^5` floor.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`; exclude incidence matrices provably equal to a determinant (`lambda=(1^n)`, already P1512-closed) or a permanent (`lambda=(n)`, P1504-closed).

### Full algorithmic path
1. factor base = deck ⇒ incidence-matrix entries; 2. build `M(x)`; 3. evaluate `d_lambda(M)` for candidate near-hook `lambda`; nonzero ⇒ verified incidence; 4. relation prob = immanant-nonzero density; 5. matrix dim, sparse; 6. standard; 7. same immanant per target; 8. offline matrix build, online immanant eval; 9. `poly(dim)` for near-hook `lambda`.
Complete.

### Cost model
If the count is a **near-hook** immanant (`lambda = (n-k, 1^k)`, `k=O(1)`), Hartmann-style evaluation costs `poly(r) * n^{O(k)}`, potentially `o(r^{5/2})` per target and shareable. If `lambda` is far from det, Bürgisser ⇒ VNP-hard ⇒ `>= r^3` (rho-lost). vs rho `r^{5/2}`; vs P1512 determinant `Omega(r^5)`.

### Why existing negatives do not already kill it
P1512-R1's proof is `deg(det M)<=dim(M)` — a *determinant* identity. Immanants of non-trivial character do **not** satisfy this bound (their degree/complexity is governed by the Young diagram, per Bürgisser), so the `Omega(r^5)` cycle-payload argument does not transfer. New operation: character-weighted (immanant) evaluation.

### Likely fatal obstruction
The elliptic five-point incidence count is generically a **far-from-determinant** immanant (or a permanent-like object), landing in Bürgisser's VNP-hard regime ⇒ `>= r^3`, reproducing P1511-R2. Near-certain kill; but classifying *which* `lambda` the count realizes is a first-time datum, and if it is a near-hook it closes the P1512-R1 exception with a crossing.

### Minimal falsifying experiment
`r in {4,8,16}`; express the incidence count as `d_lambda(M)` and identify the partition `lambda`; measure evaluation cost for the identified `lambda` vs the `r^3` product. **Positive control**: a near-hook immanant (Hartmann-fast). **Negative control**: the permanent (`lambda=(n)`, hard). Ordinary prime-order; seeds `{20260719..}`.

### Quantitative promotion gate
Identified `lambda` is near-hook (`k=O(1)`) **and** measured `beta_imm<5/2` across sizes with shared reuse. Any far-from-det `lambda` is a scoped barrier datum closing the immanant sub-case of the P1512-R1 exception.

### Proof track
Theorem: the elliptic five-point incidence count equals `d_lambda(M)` for a near-hook `lambda` (⇒ Hartmann-fast, sub-rho) — or its negation (far-from-det ⇒ VNP-hard).

### Disproof track
Show the count is a far-from-determinant immanant (Bürgisser VNP-hard) or a permanent (P1504) ⇒ no fast evaluation (expected).

### Reproduction artifact
contract `..._p1614_immanant_interpolation_atomizer.md`; impl `p1614_immanant_interpolation.py`; result/audit; ledger `ECFG-P1614`.

---

## Candidate: DELTA-MATROID-COUPLING-B3

### One-sentence mechanism
Represent the P1513 shared pair-coupling as a **Bouchet delta-matroid** rather than a matchgate, so if the coupling is an **even/representable delta-matroid** its common-norm feasibility is decidable by a delta-matroid greedy/parity algorithm below the `r^3` product (subproblem P = P1513 shared common-norm).

### Status
HEURISTIC.

### Novelty classification
LITERATURE-ADJACENT (delta-matroids generalize matchgates; the intrinsic delta-matroid representation is unused, distinct from the shared-GL2 matchgate basis search of P1504).

### Semantic fingerprint F(C)
- algebraic object: the set system of feasible source-pair supports as a delta-matroid `(V, F)` with symmetric-exchange;
- available public operations: test the symmetric-exchange axiom, run delta-matroid greedy / parity;
- hidden structure exploited: **symmetric-exchange (delta-matroid) structure** of the coupling supports;
- information discarded: the explicit resultant leaves;
- information retained: the feasible-support set system;
- relation-generation primitive: greedy over the delta-matroid;
- compression primitive: delta-matroid rank oracle;
- rank mechanism: delta-matroid rank (matroid-parity-style);
- descent mechanism: same per target;
- dominant cost exponent: greedy/parity cost.

### Nearest ledger entries
1. **P1504 (matchgate obstruction)** — shared-GL2 matchgate bases exhausted, zero found. Delta-matroids are the **combinatorial** structure underlying matchgates (even delta-matroids ↔ Pfaffian-tractable), but B3 tests **intrinsic** delta-matroid representability with **no fixed GL2** — a strictly larger class (odd/non-even delta-matroids the matchgate search could not see). Distinct object.
2. **BEREZIN-PFAFFIAN-C1 (batch11)** — Pfaffian integral. Even delta-matroids give Pfaffian tractability; B3 also covers **non-even** delta-matroids (matroid-parity-tractable, not Pfaffian). Distinct/broader.
3. **MATUNION-A2 (batch5)** — matroid union (ordinary matroids). Delta-matroids are a strict generalization with symmetric (not monotone) exchange. Distinct.
4. **LORENTZIAN-C2 (batch11)** — log-concave/M-convex (matroid) generating polynomials. Delta-matroids need not be Lorentzian; distinct structural test.
5. **P1513** — the shared common-norm B3 represents.

Distinction: no prior entry uses the **delta-matroid / symmetric-exchange** representation.

### Nearest literature
- Bouchet (1987) "Greedy algorithm and symmetric matroids"; even delta-matroids and the matchgate/Pfaffian connection (Kazda-Kolmogorov-Rolínek); Geelen-Iwata-Murota delta-matroid parity.
- Gap: delta-matroid parity is poly-time only for *linear/representable* delta-matroids; whether the elliptic coupling supports are a representable delta-matroid is the open crux, and generic couplings are not.

### Target family
Ordinary prime-field, `m=5`; exclude non-representable coupling supports.

### Full algorithmic path
1. factor base = deck; 2. build the feasible-support set system, test symmetric exchange; 3. if delta-matroid, greedy/parity gives feasibility; verify; 4. feasibility density; 5. `Theta(r)` rows; 6. standard; 7. same; 8. offline set-system build; 9. rank-oracle memory.
Status: **INCOMPLETE-risk** — stage 2 requires the supports to satisfy symmetric exchange, unproven. Label INCOMPLETE until a Phase-0 representability lemma.

### Cost model
If representable even delta-matroid, feasibility in `poly(r)` (Pfaffian) — matching P1513's `o(r^{5/2})` target if shared. If non-representable, no poly algorithm ⇒ `r^3`. vs rho `r^{5/2}`.

### Why existing negatives do not already kill it
P1504 closed shared-GL2 matchgate bases (a fixed-transform search); the intrinsic delta-matroid class is larger and includes non-even (matroid-parity) couplings the matchgate search structurally could not represent.

### Likely fatal obstruction
The elliptic coupling supports fail symmetric exchange (they are a generic set system, not a delta-matroid), so no greedy/parity applies — collapsing to the resultant. Near-certain.

### Minimal falsifying experiment
`r in {4,8}`; test the symmetric-exchange axiom on the coupling supports. **Positive control**: a linear delta-matroid (parity poly-time). **Negative control**: a generic set system (axiom fails). Seeds `{20260719..}`.

### Quantitative promotion gate
Supports certified representable delta-matroid **and** feasibility cost `o(r^{5/2})` with shared reuse. Axiom failure is a clean scoped negative.

### Proof track
Lemma: the P1513 coupling supports form a representable (even) delta-matroid.

### Disproof track
Exhibit a symmetric-exchange violation ⇒ not a delta-matroid (expected).

### Reproduction artifact
contract `..._p1615_delta_matroid_coupling.md`; impl `p1615_delta_matroid_coupling.py`; result/audit; ledger `ECFG-P1615`.

---

# GROUP C — High-risk speculative mechanisms

## Candidate: QUANTUM-ADVERSARY-SPAN-C1  *(high-risk winner)*

### One-sentence mechanism
Represent the m=5 membership backend as a **span program** and use the **general adversary bound** (`= quantum query complexity`) both as a rigorous classical lower bound `alpha >= Q(membership)` (since `R >= Q`) and, in the constructive direction, as a candidate quantum-then-classically-simulated backend whose witness size could beat `r^{3/2}` queries (subproblem P = RT-1476 α).

### Status
HEURISTIC / high-risk (two-sided: rigorous LB below, speculative UB above).

### Novelty classification
LEDGER-NEW (quantum query / general adversary / span programs unused; distinct from all classical query meters — LDC, approx-degree, VC, probabilistic-poly).

### Semantic fingerprint F(C)
- algebraic object: a span program `P` computing the membership predicate; its witness-size complexity measure;
- available public operations: evaluate the predicate, compute the adversary matrix `Gamma` and its spectral norm;
- hidden structure exploited: **general adversary bound** `ADV(f) = Q(f)` (Reichardt);
- information discarded: query order;
- information retained: the adversary spectral witness;
- relation-generation primitive: span-program positive/negative witnesses;
- compression primitive: span-program witness size;
- rank mechanism: `||Gamma||` / span-program complexity;
- descent mechanism: same span program per target;
- dominant cost exponent: `alpha` via `Q(membership)` (LB) or witness size (UB).

### Nearest ledger entries
1. **LDC-A1 (batch11)** — classical local-decodability query LB. Quantum adversary is a *different* (spectral) query LB that is often tight (`= Q`), and unlike LDC it is exactly computable as an SDP. Distinct functional.
2. **APPROXDEG-D1 (batch8)** — approximate degree (a *lower* bound on `Q`). The general adversary bound is *tight* for `Q` (Reichardt), strictly stronger than approx-degree in general. Distinct and sharper.
3. **PROBABILISTIC-POLY-C3 (batch8)** — randomized polynomial degree. Quantum query is not a polynomial-degree measure. Distinct.
4. **DEQUANTIZED-SAMPLING-C1 (batch10)** — sample-and-query dequantization of a *linear-algebra* speedup. C1-here is a *query-model* span program, not a linear-algebra sampler. Distinct model.
5. **P1511-R2** — product-circuit cubic input. The span-program witness is a model-independent alternative whose size the adversary bound pins.

Distinction: no prior entry uses the **quantum general adversary bound / span-program witness size**.

### Nearest literature
- Reichardt (2009, 2011) "Span programs and quantum query complexity: the general adversary bound is nearly tight"; Høyer-Lee-Špalek negative-weight adversary; Belovs learning-graph span programs.
- Gap: `R >= Q` gives only a *classical* LB of `alpha >= Q`, and `Q` can be quadratically smaller than `R`, so the LB may land well below `3/2` (weak). The constructive side needs a *classically simulable* span program, which generic span programs are not.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`.

### Full algorithmic path
1. factor base = deck; 2. build the membership span program / adversary matrix; 3. compute `ADV`; nonzero-witness ⇒ verified membership; 4. n/a (meter) / witness density (constructive); 5. n/a; 6. standard; 7. same span program per descent; 8. offline SDP for `ADV`, online witness eval; 9. span-program memory.
Complete (both directions accounted).

### Cost model
LB: `alpha >= Q(membership) = ADV(membership)`; if `ADV = Omega(r^{3/2})` then rho unbeaten in the query model. UB: if a *classically simulable* span program has witness size `o(r^{3/2})`, the backend crosses. vs rho `q^{1/2}`.

### Why existing negatives do not already kill it
All prior query meters (LDC, approx-degree, VC) are classical and either loose or not tight for `Q`; the general adversary bound is the *tight* query measure and is a new, exactly-computable functional on the membership predicate.

### Likely fatal obstruction
`Q` can be `Theta(sqrt(R))`, so the adversary LB likely gives `alpha >= Q = o(r^{3/2})` — a weak (inconclusive) classical floor — while the constructive span program is not classically simulable (a quantum-only speedup, irrelevant to the classical rho baseline). Near-certain that C1 is inconclusive as a classical crossing.

### Minimal falsifying experiment
`r in {4,8,16}`; compute the `ADV` SDP for the membership predicate on toy cells; compare to the classical query cost. **Positive control**: OR/AND (known `Q=sqrt`, `R=n`). **Negative control**: parity (`Q=R=n`). Seeds `{20260719..}`.

### Quantitative promotion gate
Either `ADV`-fit crosses `3/2` upward (classical-relevant barrier only if `R` is forced near `Q`) **or** a classically-simulable span program with witness exponent `<3/2` is exhibited. A quantum-only `o(r^{3/2})` witness with no classical simulation is explicitly **not** a crossing.

### Proof track
Theorem: `ADV(m=5 membership) = Theta(r^{3/2})` (classical query floor `alpha>=3/2` if `R=Theta(Q)`).

### Disproof track
A classically simulable span program with witness size `o(r^{3/2})` (⇒ classical crossing candidate).

### Reproduction artifact
contract `..._p1616_quantum_adversary_span_alpha.md`; impl `p1616_quantum_adversary_span.py`; result/audit; ledger `ECFG-P1616`.

---

## Candidate: ELL-ADIC-BETTI-MILNOR-THOM-C2

### One-sentence mechanism
Represent the per-target membership branch count by the **sum of ℓ-adic Betti numbers** of the Semaev fiber (the ℓ-adic Milnor-Thom / Bombieri-Katz bound), so if that Betti sum is `o(r^{5/2})` an output-sensitive count of the actual branches beats the `r^3` eliminant (subproblem P = P1513 / RT-1476 branch count).

### Status
HEURISTIC / high-risk.

### Novelty classification
LITERATURE-ADJACENT (ℓ-adic point-count = Lang-Weil batch6 uses the *count*; the **Betti-sum** oscillation bound is a distinct invariant, unused).

### Semantic fingerprint F(C)
- algebraic object: the ℓ-adic cohomology of the Semaev membership fiber `V_R`;
- available public operations: bound `sum_i dim H^i_c(V_R, Q_ℓ)` via Bombieri/Katz/Adolphson-Sperber;
- hidden structure exploited: **total Betti number** (complexity, not just cardinality);
- information discarded: exact points;
- information retained: cohomological complexity;
- relation-generation primitive: branch enumeration bounded by Betti sum;
- compression primitive: the degree/Newton-polytope control on Betti numbers;
- rank mechanism: Betti sum;
- descent mechanism: same fiber per target;
- dominant cost exponent: branch-count exponent via Betti sum.

### Nearest ledger entries
1. **LANGWEIL-METER-A3 (batch6)** — Deligne/Lang-Weil *point count* of the Semaev variety. C2 bounds the **sum of Betti numbers** (the error-term complexity / number of components), a strictly different invariant that controls the eliminant's branching, not its cardinality. Distinct.
2. **GKZ-DMODULE-B2 (batch8)** — holonomic rank = normalized volume. Betti sum is a cohomological dimension, not a D-module rank. Distinct (though both degree-controlled).
3. **ADOLPHSPERBER-A2 (batch7)** — p-adic Newton-polygon *slopes*. C2 uses Adolphson-Sperber for the **Betti bound**, a different output of the same theory. Distinct output.
4. **ZETA-MONODROMY-C3 (batch9)** — zeta/monodromy (rejected, incomplete). C2 is the Betti *bound*, not the monodromy action. Distinct.
5. **P1512-R1** — determinant cycle payload `Omega(r^5)`. The Betti sum is a nonlinear cohomological invariant not capped by `deg(det)<=dim`.

Distinction: no prior entry uses the **sum of ℓ-adic Betti numbers** as the branch-count meter.

### Nearest literature
- Milnor-Thom / Oleinik-Petrovsky (sum of Betti numbers `<= d(2d-1)^{n-1}`); Bombieri "On exponential sums in finite fields"; Katz "Sommes exponentielles"; Adolphson-Sperber Betti-number bounds via Newton polytopes.
- Gap: the Betti-sum bound is `~ degree^{n}`, which for the degree-`r`, `n=5`-ish Semaev fiber gives `~ r^5` — likely **above** rho, reproducing the determinant floor rather than beating it.

### Target family
Ordinary prime-field, `m=5`, `q=Theta(r^5)`.

### Full algorithmic path
1. factor base = deck; 2. bound Betti sum of the fiber; 3. enumerate branches up to the bound, verify; 4. branch density; 5. `Theta(r)` rows; 6. standard; 7. same; 8. offline Betti bound; 9. branch storage.
Complete.

### Cost model
If Betti sum `= o(r^{5/2})`, output-sensitive branch count sub-rho. If `= Theta(r^5)` (generic degree bound), rho-lost. vs rho `r^{5/2}`.

### Why existing negatives do not already kill it
Lang-Weil bounds *how many* points; the Betti sum bounds *how complex* the fiber is (its branch/component count), a distinct output-sensitivity handle never metered.

### Likely fatal obstruction
The Milnor-Thom/Adolphson-Sperber Betti bound scales as `degree^n ~ r^5`, well above `r^{5/2}`, so the count is not output-small — reproducing the P1512 floor. Near-certain.

### Minimal falsifying experiment
`r in {4,8}`; compute the actual Betti sum (via toy point-counting over `F_{p^k}` and the zeta function) of the fiber. **Positive control**: a curve of small genus (small Betti sum). **Negative control**: a high-degree complete intersection (large Betti sum). Seeds `{20260719..}`.

### Quantitative promotion gate
Measured Betti-sum exponent `<5/2` across sizes **and** an output-sensitive enumerator meeting it. Any `Theta(r^5)` Betti sum is a scoped negative.

### Proof track
Theorem: the Semaev membership fiber has Betti sum `o(r^{5/2})` (⇒ output-sensitive branch count) — or `Theta(r^5)` (barrier).

### Disproof track
Show Betti sum `= Theta(r^5)` on toy cells via the zeta function (expected).

### Reproduction artifact
contract `..._p1617_elladic_betti_milnor_thom_branch.md`; impl `p1617_elladic_betti_milnor_thom.py`; result/audit; ledger `ECFG-P1617`.

---

## Candidate: SUNFLOWER-FREE-SUPPLY-C3

### One-sentence mechanism
Represent the enriched 2-large-prime relation family as a **sunflower system**: if a large sunflower (many relations sharing a common core) exists, its core gives a cheap combinatorial relation generator; if the family is provably **sunflower-free**, the Alweiss-Lovett-Wu-Zhang bound caps its size, forcing `delta<=1/4` (subproblem P = RT-1472 δ; two-sided).

### Status
HEURISTIC / high-risk.

### Novelty classification
POSSIBLY NOVEL (sunflower / sunflower-free bounds unused on ECDLP; distinct from container / energy / PFR / Croot-Sisask).

### Semantic fingerprint F(C)
- algebraic object: the relation set as a `w`-uniform family; its sunflower structure;
- available public operations: search for sunflowers (petals with a common core), or certify sunflower-freeness;
- hidden structure exploited: **sunflower core** (shared sub-support across many relations);
- information discarded: petal contents;
- information retained: the common core + petal count;
- relation-generation primitive: enumerate petals of a found core (cheap generator);
- compression primitive: the core (all petals share it);
- rank mechanism: n/a;
- descent mechanism: n/a;
- dominant cost exponent: `delta` via petal count / sunflower-free ceiling.

### Nearest ledger entries
1. **CONTAINER-CEILING-A3 (batch9)** — hypergraph container ceiling. Sunflower-free is a *distinct* extremal bound (ALWW), not a container decomposition. Distinct.
2. **ENERGY-D1 (batch3)** — additive energy. Sunflowers are set-system cores, not additive structure. Distinct.
3. **PFR-DICHOTOMY-C2 (batch9)** — polynomial Freiman-Ruzsa doubling. Sunflowers are cross-support cores, not sumset structure. Distinct.
4. **CROOTSISASK-C3 (batch7)** — almost-periodicity bundling. Distinct (approximate periodicity vs exact core).
5. **KRUSKAL-KATONA-A1 (this batch)** — shadow density. Sunflower-free is a different extremal shape bound (petals vs shadow). Distinct.

Distinction: no prior entry uses the **sunflower / sunflower-free** structure as a two-sided δ handle.

### Nearest literature
- Erdős-Rado sunflower lemma; Alweiss-Lovett-Wu-Zhang (2020) improved bound `(log w)^{w(1+o(1))}`; Naslund-Sawin sunflower-free-set cap-bound via slice rank; Rao's exposition.
- Gap: a sunflower core in the relation family need not correspond to a *usable* algebraic relation (the core primes may not close a summation), so a found sunflower may be an algebraically-vacuous generator; and sunflower-freeness gives only a `(log)^w` factor, not a polynomial δ ceiling.

### Target family
Ordinary prime-field, `L=q^{1/5}`, enriched 2-LP family.

### Full algorithmic path
1. factor base = `L`-smooth primes; 2. search for sunflower cores, enumerate petals (generator) OR certify sunflower-free; verify each petal is a real relation; 3. exact; 4. relation prob = petal density; 5. `Theta(petals)`; 6. standard; 7. n/a; 8. offline sunflower search; 9. `O(family)`.
Complete.

### Cost model
If a core with `Omega(L^{1/4+eps})` real petals exists, cheap enrichment `delta>1/4`. If sunflower-free, ALWW caps `|R|` (weakly) ⇒ `delta<=1/4`. vs rho `2/3`.

### Why existing negatives do not already kill it
Container / energy / PFR bound different structures; the sunflower core is a *constructive* shared-support generator none tested, and its absence is a distinct ceiling.

### Likely fatal obstruction
Real elliptic relations sharing a common prime-core do **not** form additional independent relations (the core is algebraically constrained), so any found sunflower is a vacuous generator; and sunflower-freeness gives only a `(log)^w` (not polynomial) ceiling. Near-certain vacuity.

### Minimal falsifying experiment
`r in {4,8,16}`; search the enriched family for sunflowers; test whether petals are independent real relations. **Positive control**: a planted sunflower of real relations (cheap generator). **Negative control**: an honest family (few/vacuous sunflowers). Seeds `{20260719..}`.

### Quantitative promotion gate
A found sunflower yields `delta_hat>1/4` **independent** real relations across sizes. Vacuous cores / sunflower-freeness is a scoped negative.

### Proof track
Theorem: the enriched relation family is sunflower-free of bounded size ⇒ `delta<=1/4` (weak), or contains a large real-petal sunflower ⇒ crossing.

### Disproof track
Show every large sunflower core is algebraically vacuous (expected).

### Reproduction artifact
contract `..._p1618_sunflower_free_supply.md`; impl `p1618_sunflower_free_supply.py`; result/audit; ledger `ECFG-P1618`.

---

# GROUP D — Negative-theory / barrier candidates

*Each imports a lower-bound technology no prior barrier used; each threshold CLOSES a live gate if it bites.*

## Candidate: CELL-PROBE-CHRONOGRAM-D1

### One-sentence mechanism
Import the **dynamic cell-probe / chronogram** lower-bound method: model the batched membership as an online data structure (insert a target, query its relation), and a Larsen-style chronogram bound forces any backend with `S=O(r^2)` words of memory to make `t=Omega(r^2 / log^2 r)` probes per query, so the `Theta(r)`-target campaign costs `Omega(r^3/polylog)` (closes RT-1476 batching in the cell-probe model).

### Status
CONJECTURE (barrier).

### Novelty classification
LEDGER-NEW (dynamic cell-probe / chronogram unused; distinct from batch11's static circuit-space pebbling and from all communication/degree barriers).

### Semantic fingerprint F(C)
- algebraic object: the batched membership as a dynamic problem (updates = targets, queries = relations);
- available public operations: cell probes into `S` memory words;
- hidden structure exploited: **update-query memory-probe tradeoff** (chronogram epochs);
- rank mechanism: n/a (probe complexity);
- dominant cost exponent: probe-time `t` per query given space `S`.

### Nearest ledger entries
PROOF-SPACE-PEBBLING-D1 (batch11, **static** circuit space / red-blue pebbling), LIFTING-D1 (batch7, communication), NOF-COMM-D2 (batch8), APPROXDEG-D1 (batch8), RIGIDITY-A1 (batch8). All bound **static space, communication, or degree**; D1-here bounds **dynamic cell-probe time-vs-memory** (Fredman-Saks chronogram / Larsen), a distinct resource. The P1510 `O(r^2)` STATE claim + `Theta(r)` online targets is exactly a dynamic data-structure instance.

### Nearest literature
- Fredman-Saks (chronogram); Pătrașcu-Demaine (epoch/information-transfer); Larsen (2012) "The cell probe complexity of dynamic range counting" (first `Omega((log n / log log n)^2)` and higher polynomial bounds via the cell-sampling method).
- Gap: cell-probe bounds are for genuine dynamic problems with independent updates; the membership targets are algebraically related (shared factor base), so the update-independence the chronogram needs may fail, weakening the bound.

### Target family / path / cost / gate
Ordinary prime-field, `m=5`. Barrier form: chronogram/cell-sampling on the batched membership gives `t*log(S) = Omega(r^2)` per query with `S=O(r^2)` ⇒ `t=Omega(r^2/polylog)` ⇒ batch `Omega(r^3/polylog)=Omega(q^{3/5}/polylog)` ⇒ rho-lost. Promotion gate: measured probe-count trends `Omega(r^2/polylog)` on toy dynamic instances. Proof: the batched membership has cell-probe complexity `Omega(r^2/polylog)` per query at space `O(r^2)`. Disproof: an `O(r^2)`-space, `o(r^2)`-probe backend (= the sub-rho algorithm).

### Reproduction artifact
contract `..._p1619_cell_probe_chronogram_barrier.md`; impl `p1619_cell_probe_chronogram.py`; result/audit; ledger `ECFG-P1619`.

---

## Candidate: SHERALI-ADAMS-RANK-BARRIER-D2

### One-sentence mechanism
Import the **Sherali-Adams integrality-gap / LP-rank** lower bound (asymptotic partner of B1): if the SA rank of the 2-large-prime enrichment polytope is `Omega(q^{1/4})`, then no LP relaxation of degree `< q^{1/4}` certifies `delta>1/4`, so `delta<=1/4` unconditionally in the LP-hierarchy model (closes RT-1472 δ for all cheap lift-and-project LPs).

### Status
CONJECTURE (barrier).

### Novelty classification
POSSIBLY NOVEL (SA-rank-as-barrier unused; distinct from SOS-LB SDP degree batch4 and from the LDLR barrier batch11).

### Semantic fingerprint
As B1 in the impossibility direction: large SA rank ⇒ LP-hierarchy integrality gap ⇒ δ ceiling. LP hierarchy, not SDP (batch4) and not spectral LDLR (batch11).

### Nearest ledger entries
SOS-LB-D1 (batch4, SOS **SDP** degree / pseudo-calibration), LDLR-DETECTION-BARRIER-D2 (batch11, spectral low-degree norm), DELSARTE-LP-A2 (batch8, single-level LP), CONTAINER-CEILING-A3 (batch9). All bound SDP degree, spectral norm, or single-level LP; D2-here bounds **lift-and-project LP rank** (Charikar-Makarychev-Makarychev / Grigoriev), a distinct hierarchy. Pairs with B1 as APPROXDEG↔PROB-POLY (batch8) and A3↔D2 (batch11).

### Nearest literature
- Grigoriev; Charikar-Makarychev-Makarychev (SA integrality gaps for MAX-CUT/vertex-cover); Chan-Lee-Raghavendra-Steurer (LP extension complexity). Gap: SA-rank lower bounds are proved for specific CSPs; the elliptic enrichment polytope must be shown to inherit the gap.

### Target / gate
Ordinary prime-field, `L=q^{1/5}`. Barrier bites if SA rank `= Omega(q^{1/4})` ⇒ δ≤1/4 in the LP-hierarchy model. Promotion gate: empirical SA integrality gap persists across degrees `t=2,3,4` and sizes. Proof: SA rank of the enrichment polytope `= Omega(q^{1/4})`. Disproof: SA rounds at `O(1)` degree (⇒ B1 crossing candidate).

### Reproduction artifact
contract `..._p1620_sherali_adams_rank_barrier.md`; impl `p1620_sherali_adams_rank_barrier.py`; result/audit; ledger `ECFG-P1620`.

---

## Candidate: HYPERCLIQUE-FINEGRAINED-D3

### One-sentence mechanism
Import the **k-hyperclique / min-weight-k-clique** fine-grained hardness hypothesis at `k=5` (the natural arity of the membership): the m=5 membership is a weighted 5-uniform-hyperclique detection, and under the exact-weight-5-hyperclique conjecture no algorithm detects a complete relation in truly-sub-`r^{5/2}` time, giving a conditional `alpha` floor (closes RT-1476 α under a standard fine-grained assumption).

### Status
CONJECTURE (barrier, conditional on a fine-grained hypothesis).

### Novelty classification
POSSIBLY NOVEL (k-hyperclique at k=5 unused; distinct from the 2-quantifier OV/3SUM of batch6).

### Semantic fingerprint
- algebraic object: the 5-partite relation hypergraph; a complete relation = a weighted 5-hyperclique;
- available public operations: the fine-grained reduction from exact-weight-5-hyperclique;
- hidden structure exploited: **k-clique/k-hyperclique fine-grained hardness**;
- dominant cost exponent: conditional `alpha` floor from the hyperclique exponent.

### Nearest ledger entries
FINEGRAINED-OV-D1 (batch6, **2-quantifier** OV/3SUM). D3 uses **k=5-hyperclique / min-weight-clique**, a *different* fine-grained problem matching the membership arity (OV/3SUM are 2- and 3-sum problems; 5-membership is naturally a 5-clique). Distinct hypothesis and distinct reduction. Also distinct from all communication/degree barriers (this is a fine-grained *conditional* bound).

### Nearest literature
- Abboud-Backurs-Vassilevska Williams (clique-based fine-grained lower bounds); Lincoln-Vassilevska Williams-Williams (weighted clique / min-plus); Vassilevska Williams (hyperclique hypothesis survey); the exact-weight-k-clique and 5-uniform-hyperclique conjectures.
- Gap: the reduction from exact-weight-5-hyperclique to the *elliptic* membership must preserve the weight structure; the elliptic constraint may make the instance easier than worst-case hyperclique (the reduction is the crux), so D3 is conditional and possibly loose.

### Target / gate
Ordinary prime-field, `m=5`. Barrier bites if a weight-preserving reduction from exact-weight-5-hyperclique to elliptic membership exists ⇒ under the hyperclique hypothesis, `alpha >= 3/2` (no truly-sub-`r^{5/2}` batch detection). Promotion gate: an explicit reduction verified on toy cells + the conditional exponent. Proof: reduction exact-weight-5-hyperclique `<=` elliptic-membership. Disproof: the elliptic instance is a *special* (sub-worst-case) hyperclique solvable faster (⇒ representation crossing candidate).

### Reproduction artifact
contract `..._p1621_hyperclique_finegrained_barrier.md`; impl `p1621_hyperclique_finegrained.py`; result/audit; ledger `ECFG-P1621`.

---

# RANKING

Scores 0–5 on: (1) distance from prior ledger mechanisms, (2) plausibility of an exact verifier, (3) chance of changing an exponent (not a constant), (4) complete-path coverage, (5) falsifiability at toy scale, (6) literature-novelty confidence, (7) low risk of hidden preprocessing/memory cost. Reject if semantic novelty <3, no complete route to descent, no rho comparison, or no precise distinction from the closest ledger entry.

| Cand | (1) | (2) | (3) | (4) | (5) | (6) | (7) | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A1 KRUSKAL-KATONA** | 4 | 5 | 3 | 5 | 5 | 4 | 5 | 31 | **conservative winner** |
| A2 BOLLOBAS-SETPAIR | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 28 | keep |
| A3 DISCREPANCY | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 28 | keep |
| B1 SHERALI-ADAMS | 4 | 4 | 3 | 5 | 4 | 4 | 3 | 27 | keep (pairs D2) |
| **B2 IMMANANT** | 5 | 5 | 4 | 5 | 4 | 5 | 4 | 32 | **representation winner** |
| B3 DELTA-MATROID | 4 | 3 | 3 | 2 | 3 | 3 | 3 | 21 | keep (INCOMPLETE — Phase 0 lemma) |
| **C1 QUANTUM-ADVERSARY** | 5 | 4 | 3 | 4 | 4 | 5 | 3 | 28 | **high-risk winner** |
| C2 ELL-ADIC-BETTI | 4 | 4 | 3 | 4 | 4 | 4 | 3 | 26 | keep (near-certain r^5 floor) |
| C3 SUNFLOWER-FREE | 4 | 4 | 2 | 4 | 4 | 4 | 4 | 26 | keep (near-certain vacuity) |
| **D1 CELL-PROBE** | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 31 | keep (high-EV barrier) |
| **D2 SA-RANK** | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 30 | keep (high-EV barrier) |
| **D3 HYPERCLIQUE** | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 31 | keep (high-EV barrier) |

No candidate scores novelty <3; none rejected outright. B3 is retained but flagged INCOMPLETE pending its Phase-0 delta-matroid-representability lemma.

**Selected winners:**
1. **Conservative:** KRUSKAL-KATONA-SHADOW-A1 (ECFG-P1610).
2. **Representation:** IMMANANT-INTERPOLATION-B2 (ECFG-P1614).
3. **High-risk:** QUANTUM-ADVERSARY-SPAN-C1 (ECFG-P1616).

The three **D barriers are higher expected-value than the winners** (as in batches 6–11): each threshold, if reached, CLOSES a live gate (D1→RT-1476 batching cell-probe time; D2→RT-1472 δ LP-hierarchy rank; D3→RT-1476 α under the 5-hyperclique hypothesis). The winners are the sharpest *attack* probes but each carries a near-certain scoped-negative kill.

---

# WINNER CONTRACTS + FIRST COMMANDS

## Contract 1 — ECFG-P1610 Kruskal-Katona shadow δ-ceiling (conservative)

```yaml
id: ECFG-P1610
title: Kruskal-Katona shadow density as an exact RT-1472 delta supply ceiling
hypothesis: >
  The honest and 2-large-prime-enriched elliptic relation k-hypergraph has size bounded
  by its lower-shadow via Kruskal-Katona, forcing max supply exponent 1+delta <= 5/4,
  so no enrichment reaches delta>1/4 at L=q^{1/5}.
null_hypothesis: >
  The enriched family's measured (size, shadow) is consistent with supply Omega(L^{1+1/4+eps}).
model: restricted; extremal set family / colex-shifting on the L-smooth relation hypergraph.
target_family: ordinary prime-field E/F_p, prime order, m=5, q=Theta(r^5); excludes supersingular/anomalous/small-embedding-degree.
sizes: r in {4,8,16}; toy primes {1031, 32771, 1048583}.
seeds: [20260719,20260720,20260721,20260722,20260723]
metrics:
  - max shadow-consistent supply exponent 1+delta_hat (primary)
  - measured (|R|, |shadow R|) for honest vs enriched
  - colex-compression tightness ratio
positive_control: colex-initial-segment family (shadow hits KK exactly).
negative_control: random k-uniform family same size (shadow strictly above KK minimum).
success_criterion: fitted 1+delta_hat crosses 5/4 downward across sizes with a KK ceiling forbidding delta>1/4 (barrier datum), OR enriched shadow requires delta>1/4 the ceiling forbids.
falsification: enriched (|R|,|shadow|) consistent with delta_hat > 1/4 (RT-1472 enrichment licensed; cross-check honest subcriticality).
verifier: independent shadow recomputation + colex-shift replay + mutation rejections.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1610_kruskal_katona_shadow_delta_ceiling.md
  impl: tasks/ecdlp_index_calculus/p1610_kruskal_katona_shadow.py
  result: p1610_kruskal_katona_shadow.json
  audit: p1610_kruskal_katona_shadow_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1610_kruskal_katona_shadow.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --emit p1610_kruskal_katona_shadow.json
```

## Contract 2 — ECFG-P1614 immanant-interpolation atomizer (representation)

```yaml
id: ECFG-P1614
title: Immanant (character-weighted determinant) representation of the five-point incidence count
hypothesis: >
  The batched five-point elliptic incidence count equals a near-hook immanant d_lambda(M)
  (lambda=(n-k,1^k), k=O(1)), which is NOT capped by deg(det)<=dim, so Hartmann-style
  evaluation atomizes below rho with beta_imm < 5/2.
null_hypothesis: >
  The count is a far-from-determinant immanant (Buergisser VNP-hard) or a permanent (P1504),
  reproducing the r^3/r^5 floor.
model: character-weighted determinant (immanant) of the source-marked incidence matrix.
target_family: ordinary prime-field, m=5, q=Theta(r^5); excludes determinant (P1512) and permanent (P1504) extremes.
sizes: r in {4,8,16}; toy primes as P1610.
seeds: [20260719..20260723]
metrics:
  - identified partition lambda and its distance from (1^n) (primary)
  - fitted beta_imm(lambda) in r
  - immanant evaluation cost vs r^3 product
positive_control: near-hook immanant (Hartmann-fast).
negative_control: the permanent lambda=(n) (VNP-hard).
success_criterion: identified lambda near-hook (k=O(1)) AND beta_imm < 5/2 with shared reuse.
falsification: lambda far from determinant (scoped negative; closes the immanant sub-case of the P1512-R1 exception).
verifier: independent immanant recomputation (character sum + Hartmann) + count cross-check on P1510 transcript + mutations.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1614_immanant_interpolation_atomizer.md
  impl: tasks/ecdlp_index_calculus/p1614_immanant_interpolation.py
  result: p1614_immanant_interpolation.json
  audit: p1614_immanant_interpolation_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1614_immanant_interpolation.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --identify-lambda --emit p1614_immanant_interpolation.json
```

## Contract 3 — ECFG-P1616 quantum adversary / span-program α (high-risk)

```yaml
id: ECFG-P1616
title: General adversary bound (quantum query) as a classical alpha floor on m=5 membership
hypothesis: >
  ADV(m=5 membership) = Theta(r^{3/2}); since R >= Q = ADV, this is a classical query floor
  alpha >= 3/2 when R=Theta(Q). Constructive side: a classically simulable span program with
  witness exponent < 3/2 would cross rho.
null_hypothesis: >
  Q = o(r^{3/2}) (a weak/inconclusive classical floor) and no classically simulable span program
  beats r^{3/2}; the quantum speedup is quantum-only, irrelevant to the classical baseline.
model: span program / general adversary SDP on the membership predicate (classical R >= Q).
target_family: ordinary prime-field, m=5, q=Theta(r^5).
sizes: r in {4,8,16}; toy primes as P1610.
seeds: [20260719..20260723]
metrics:
  - ADV(membership) SDP value and fitted exponent (primary)
  - classical query cost R for comparison (R/Q ratio)
  - span-program witness size (constructive side)
positive_control: OR/AND (Q=sqrt(n), R=n).
negative_control: parity (Q=R=n).
success_criterion: ADV-fit crosses 3/2 upward with R=Theta(Q) (classical-relevant barrier), OR a classically simulable span program with witness exponent < 3/2.
falsification: Q = o(r^{3/2}) with R >> Q (inconclusive classical floor); quantum-only witness is NOT a crossing.
verifier: independent ADV-SDP recomputation + classical query audit + control replay + mutations.
artifacts:
  contract: ecdlp_index_calculus_state/experiment_contract_p1616_quantum_adversary_span_alpha.md
  impl: tasks/ecdlp_index_calculus/p1616_quantum_adversary_span.py
  result: p1616_quantum_adversary_span.json
  audit: p1616_quantum_adversary_span_audit.py
requested_policy: <from handoff>
```

**First executable command:**
```bash
python3 tasks/ecdlp_index_calculus/p1616_quantum_adversary_span.py --sizes 4,8,16 --seeds 20260719,20260720,20260721,20260722,20260723 --compare-classical --emit p1616_quantum_adversary_span.json
```

---

# RED-TEAM: are the three winners disguised repetitions or cost-negative?

**A1 (Kruskal-Katona) — disguised repetition?** Nearest priors are SHEARER-D3 (batch8), CONTAINER-CEILING-A3 (batch9), DELSARTE-LP-A2 (batch8), ENERGY-D1 (batch3) — all supply/entropy ceilings. Verdict: **not a repetition** — KK meters the size↔one-element-shadow compression identity, a shape-sensitive extremal bound distinct from entropy submodularity, container decomposition, coding LP, or additive energy. **Cost-negative risk: HIGH.** The honest obstruction is that KK is tight only for colex-initial segments; the elliptic relation family is far from colex, so the ceiling is loose and most likely admits `delta>1/4` numerically — an inconclusive ceiling, not a barrier. Retained because even a loose ceiling produces the first shadow-profile datum on the honest 2-LP graph and is a clean, exactly-computable verifier.

**B2 (immanant) — disguised repetition?** Nearest priors are P1512-R1 (determinant, `deg(det)<=dim`), P1504 (permanent/matchgate), BEREZIN-PFAFFIAN-C1 (batch11, Pfaffian). Verdict: **not a repetition** — the immanant `d_lambda` is a character-weighted determinant at *intermediate* `lambda` (near-hook), the untested middle of the det↔perm interpolation, and its complexity obeys the Bürgisser dichotomy, **not** `deg(det)<=dim`. This is the sharpest named instance of the surviving P1512-R1 nonlinear-circuit exception since batch11's nc-rank. **Cost-negative risk: HIGH but not certain.** The near-certain kill is Bürgisser's dichotomy: the elliptic incidence count is generically a *far-from-determinant* immanant (VNP-hard) or a permanent (P1504-closed), reproducing the `r^3`/`r^5` floor. If it collapses, B2 closes the immanant sub-case of the exception *by name* (high value either way); if the count is a near-hook, it is a genuine crossing.

**C1 (quantum adversary / span) — disguised repetition?** Nearest priors are LDC-A1 (batch11, classical local decodability) and APPROXDEG-D1 (batch8, approx-degree ≤ Q). Verdict: **not a repetition** — the general adversary bound is the *tight* query measure (`= Q`, Reichardt), an exactly-computable SDP strictly sharper than approx-degree and orthogonal to LDC's length-query argument. **Cost-negative risk: VERY HIGH.** The near-certain obstruction is the classical-quantum gap: `Q` can be `Theta(sqrt(R))`, so the rigorous classical floor `alpha >= Q` most likely lands below `3/2` (inconclusive), and the constructive span program is generically *not* classically simulable — a quantum-only speedup irrelevant to the classical rho baseline. C1 is the one route that imports the tight query functional, but it most likely yields an inconclusive classical floor plus a quantum-only (non-crossing) upper bound.

**Global red-team verdict.** All three winners are **scoped tightenings / lane-closures / high-variance probes, not crossings.** Each has a named, near-certain kill that (if realized) converts it into a scoped negative closing a specific escape hatch on RT-1476/RT-1472. The **three D barriers (D1 cell-probe, D2 Sherali-Adams rank, D3 5-hyperclique) are higher expected value**: each imports a lower-bound technology no prior barrier used and each threshold, if reached, closes a live gate (D1 unconditionally in the cell-probe model, D2 unconditionally in the LP-hierarchy model, D3 conditionally under a standard fine-grained hypothesis). Consistent with batches 6–11, the mechanism space is **saturated** (14 reports, ~60 lanes); the marginal value this batch is (a) importing three technology families indifferent to shape rather than degree — extremal-set compression (shadow/set-pair/sunflower), resource tradeoffs (cell-probe, quantum query), and LP-hierarchy/character-weighted-determinant representations (Sherali-Adams, immanant) — all provably outside the commutative-determinant-degree functional that gated the P151x chain, and (b) the barrier arm.

**No break is claimed. RT-1472 and RT-1476 remain open.** Every result above is toy-scale, model-bounded, and scoped to the tested curves/parameters/solver/budget. A failed candidate is a scoped negative result, not evidence that prime-field ECDLP cannot be improved.

---

## Sources (external literature grounding)

- Kruskal (1963) / Katona (1968) shadow theorem; Frankl shifting/compression; Bollobás-Thomason.
- Bollobás (1965) set-pair inequality; Lovász exterior-algebra proof; Frankl skew version; Füredi uniform-cover extensions.
- Babai-Frankl-Simon (discrepancy method); Klauck (corruption bound); Sherstov pattern-matrix method; Chattopadhyay-Pitassi communication survey.
- Sherali-Adams (1990) reformulation-linearization; Grigoriev; Charikar-Makarychev-Makarychev SA integrality gaps; Chan-Lee-Raghavendra-Steurer LP extension complexity; Laurent LP/SDP hierarchy comparison.
- Bürgisser, "The computational complexity of immanants" (SIAM J. Comput.); Hartmann immanant algorithm; Brylawski-Lascoux; Curticapean-Marx immanant/Holant dichotomy; Merris-Watkins immanant inequalities.
- Bouchet (1987) symmetric matroids / delta-matroids and greedy; Kazda-Kolmogorov-Rolínek even delta-matroids & matchgates; Geelen-Iwata-Murota delta-matroid parity.
- Reichardt (2009/2011) span programs & the general adversary bound (nearly tight for quantum query); Høyer-Lee-Špalek negative-weight adversary; Belovs learning graphs.
- Milnor-Thom / Oleinik-Petrovsky sum-of-Betti-numbers bound; Bombieri "On exponential sums in finite fields"; Katz "Sommes exponentielles"; Adolphson-Sperber Newton-polytope Betti bounds.
- Erdős-Rado sunflower lemma; Alweiss-Lovett-Wu-Zhang, "Improved bounds for the sunflower lemma" (2020); Naslund-Sawin sunflower-free sets via slice rank.
- Fredman-Saks (chronogram); Pătrașcu-Demaine information-transfer; Larsen (2012), "The cell probe complexity of dynamic range counting."
- Abboud-Backurs-Vassilevska Williams clique-based fine-grained lower bounds; Lincoln-Vassilevska Williams-Williams weighted clique / min-plus; Vassilevska Williams hyperclique-hypothesis survey.
