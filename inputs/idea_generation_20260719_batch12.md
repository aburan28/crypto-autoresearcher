# ECDLP Idea Generation — 2026-07-19 batch12 (report 20 / batch18)

Research Director scheduled run. Target: a **non-generic, complete-cost**
single-target prime-field ECDLP algorithm that beats the Pollard-rho
`0.886*sqrt(n)` baseline. Toy correctness, new coordinates, relation
certificates, faster preprocessing, or a solver-only win are explicitly **not**
breakthroughs.

**Authorized scope:** generated toy curves, public benchmark instances,
synthetic data only. No wallets, production keys, or unauthorized systems.

---

## 0. Input review and machine-readable inventory

### 0.1 Sources read this run

1. `research_ledger.md` (2.8 MB main ledger) — frontier verified by bounded
   grep, not full read (size guard).
2. `ecdlp_index_calculus_state/research_ledger.md` (797 KB) — IC-state ledger.
3. `research/non_generic_transfer_search_20260610.md` — full read
   (transfer/decomposition channel history through PO-transfer-006).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` — 10 primary
   entries.
5. All 19 prior `research/idea_generation_*.md` reports, digested through the
   persistent anti-duplication catalogue.

### 0.2 Inventory (entries reviewed, ID families)

Verified frontier this run (direct grep):

- **main ledger:** P-max `P1486`, ECFG-P-max `ECFG-P1470`; families present:
  `P####`, `ECFG-P####`, `PO##`, `ECFG-NR###`, `ECFG-RT-####`, `RT-####`,
  `IDEA-*`, `DEC-*`, `TASK-*`, `KN-*`. Aggregate scale carried from batch15
  audit: ~7541 P / ~956 ECFG-P / ~522 PO / ~516 ECFG-NR.
- **IC-state ledger:** frontier `P1509–P1513` (Hasse-jet source-section chain +
  marked-resultant/DB-join lower bounds; scalar-linear Chow atomizer closed at
  `Omega(r^5)` = P1512-R1; only the **nonlinear-circuit exception** and P1513
  shared-common-norm survive).
- **report-proposed IDs:** `ECFG-P1471 … ECFG-P1681` live in the 19 report files
  (uncommitted). **This report allocates `ECFG-P1682 … ECFG-P1693`.**

Per-ID fingerprint fields extracted for every family (mechanism, representation,
exploited structure, factor base, relation shape, relation-generation method,
compression method, linear-algebra object, target-descent method, cost
bottleneck, outcome, scoped negative boundary, next branch) are maintained in
the catalogue; the binding facts for this run are the two live gates:

- **RT-1472** (P1472): explicit two-large-prime graph at `B=n^(1/5)`, advice
  `Theta(L^2)`, support `Theta(L^2)`, edges `Theta(L+B)`. Exact cost exponent
  `max(2ell, 1-ell, 1+1/5-2ell)`, minimized at `ell=1/3` giving `2/3`. Crossing
  rho needs **enrichment `delta>1/4`**; without it an implicit deck needs setup
  `o(L)`, query `o(sqrt(L))`.
- **RT-1476** (P1476): five-term implicit membership backend, `L=q^ell`, support
  `min(1,L^m/q)`, query `L^alpha`, `Theta(L)` rows, sparse LA `L^2`, descent same
  backend. Optimum `ell=1/(m+1-alpha)`, total `2/(m+1-alpha)` for `alpha<=1`;
  above linear `ell=1/m`, total `(1+alpha)/m`. m<=3 impossible, m=4 needs
  `alpha<1`, **m=5 needs `alpha<3/2`**, setup `<=L^2`, random-like support.

Closed/control-only territory honored (do not re-propose): same-field isogeny
invariants, scalar Weil pullback, explicit 2-LP advice graphs, joint
factor/large-prime Krylov, pair-residual character buckets, non-invariant CM
decks, materialized serial-S3 backward states, dense composed resultants,
crystalline/Cartier-Manin/Monsky-Washnitzer (batch2 D2), Kloosterman/character-
sum bias (batch2 C3), "poly-time sampler certifies delta>1/4" role (consumed by
batch5 MATUNION-A2 + batch11 LORENTZIAN-C2), Temperley-Lieb/Hecke planar
contraction (batch13 B3), and every prior barrier axis.

### 0.3 Saturation status and this run's organizing theme

After 19 reports spanning ~60 mechanism lanes, the **mechanism space is
saturated**; honest value is now (i) importing a genuinely 0-hit
lower-bound/representation technology that closes a live gate by name, and (ii)
scoping the near-certain negative precisely. This run imports **three
technology areas with grep-verified 0 corpus hits** (checked against all 19
reports, the IC-state ledger, and — via bounded fixed-string grep — the 2.8 MB
main ledger):

- **A — anti-concentration / small-ball probability** (Halász, Littlewood-
  Offord, Stein-Chen/Poisson approximation, Berry-Esseen): a probabilistic-
  number-theory supply meter for RT-1472 `delta`. **Distinct** from Wormald
  2-core *location* (batch4), Shearer entropy (batch8), Delsarte-LP (batch8),
  hypergraph container (batch9), large-sieve `L^2` (batch14), singular series
  (batch15), hereditary discrepancy (batch16), Furstenberg recurrence (batch17)
  — all of which bound *counts, entropy, or supply density*, none of which bound
  the **anti-concentration of the additive large-prime image**.
- **C — property testing / statistical-minimax query lower bounds** (locally
  testable codes, PCP-of-proximity, Fano/Le Cam/Assouad): a membership-tester
  `alpha` meter for RT-1476. **Distinct** from approx-degree (batch8),
  LDC (batch11), sensitivity (batch13), evasiveness (batch16), Haussler
  packing / round elimination (batch15), SQ statistical dimension (batch17,
  DEMOTED — detection threshold, not a minimax query floor).
- **B — finite-group-of-Lie-type / quantum-group representation** (Yangian
  R-matrix, communication fooling-set cover, Kazhdan-Lusztig cells, Deligne-
  Lusztig characters): representation changes of the 5-point membership object.
  **Distinct** from Temperley-Lieb/Hecke planar diagrams (batch13), immanant
  (batch12), FI-modules (batch16), nc-rank operator scaling (batch11), GKZ
  D-module (batch8) — the Yangian carries a **rational spectral parameter** and
  is the non-planar integrable completion those did not cover.

**No break is claimed.** Every attack candidate below is a near-certain scoped
negative or lane-closure; the three D-barriers are higher expected-value because
each threshold, if it bites, closes a live gate. RT-1472 and RT-1476 remain
open.

---

## GROUP A — Conservative extensions (anti-concentration supply meters)

## Candidate: HALASZ-SMALLBALL-A1  (ECFG-P1682)

### One-sentence mechanism
Exploit the **anti-concentration** (small-ball) structure `S` of the additive
image of the large-prime steps to bound the enrichment rate `C=delta` of the
RT-1472 two-large-prime graph below the honest baseline `1/4`.

### Status
HYPOTHESIS (as a delta-ceiling meter); the paired barrier is D1.

### Novelty classification
LEDGER-NEW (0 corpus hits for Littlewood-Offord / Halász / small-ball).

### Semantic fingerprint
F = (algebraic object: additive image in `Z/n` of weighted large-prime logs;
public ops: form 2-LP edges, hash to smooth box; hidden structure exploited:
GAP/arithmetic-progression concentration of the step multiset; info discarded:
edge identity; info retained: small-ball mass in the target window;
relation-generation primitive: 2-LP pairing; compression primitive: none (this
is a supply meter); rank mechanism: n/a; descent: n/a; dominant cost exponent:
`delta` via `sup` small-ball probability).

### Nearest ledger entries
1. RT-1472 / P1472 — same gate; **distinction:** P1472 costs the *explicit
   occupancy exponent*; A1 bounds it from above by the **Halász small-ball rate**
   `O(1/sqrt(k))` of the `k`-term large-prime sum — a different mathematical
   object (anti-concentration, not occupancy counting).
2. batch4 CORRELATED-PEEL / Wormald 2-core — measures giant-core *location*;
   **distinction:** A1 measures the *additive-image concentration* that feeds edge
   creation, upstream of any core.
3. batch14 LARGE-SIEVE-SUPPLY-A1 — dual `L^2` inequality over moduli;
   **distinction:** large sieve bounds a *sum over the whole family*; Halász
   bounds a *single sum's small-ball mass* — the ELO/Halász inequality is not a
   large-sieve inequality.
4. batch15 SINGULAR-SERIES-A1 — circle-method major arc `S`; **distinction:**
   `S` is a *mean* (major-arc main term); small-ball is a *sup over shift* of the
   probability, controlled by minor-arc + step structure.
5. batch8 SHEARER-D3 — submodular entropy supply ceiling; **distinction:**
   entropy bounds *log count*; Halász bounds *point mass*, and the two coincide
   only for product measures.

### Nearest literature
- Halász (1977), small-ball / concentration-function inequality: `Q(S,r) <=
  C r / sqrt(V)` unless the steps concentrate on a GAP (Nguyen-Vu
  inverse-Littlewood-Offord, 2011–2013). Claim: sub-Gaussian anti-concentration
  is `Theta(1/sqrt(k))` for `k` random-like steps. Assumption: steps not
  contained in a short GAP. **Gap:** the large-prime log multiset over `Z/n` is
  not literally i.i.d.; the inverse theorem must be instantiated for the
  `2-LP` step distribution.

### Target family
Ordinary prime-order curves over `F_p`, `p` prime, `n=#E(F_p)` prime,
`t=p+1-n`, generic `j`. Excluded: anomalous (`n=p`), low-embedding-degree,
CM-discriminant `|D|` tiny, and any curve where the large-prime factor base has
engineered arithmetic structure.

### Full algorithmic path (this is a **meter**, stages instantiated)
1. **factor base:** large primes `<= B=n^(1/5)`, `Theta(L^2)` pair advice.
2. **relation generation:** 2-LP pairing hashed to the smooth target box.
3. **witness extraction/verification:** edge = valid 2-LP relation, re-verified
   by the run wrapper (claim tier: relation only).
4. **relation probability:** `= Q(S, w)` = small-ball mass of the `k`-term
   large-prime sum in a window `w` — the quantity A1 meters.
5. **matrix dims/density/rank:** not binding (LA stage `n^(2/5)`).
6. **factor-log calibration:** n/a (supply prefilter).
7. **descent:** inherited.
8. **offline/online:** advice `Theta(L^2)` offline; occupancy online.
9. **memory/parallelism:** advice-dominated; parallel over edges.

### Cost model
Enrichment exponent `delta = log_L( E[extra edges] / baseline )`. Halász gives
`Q <= C/sqrt(k)`, so extra occupancy `<= L^2 * C/sqrt(k)`; with `k=Theta(L)`
this yields `delta <= 1/4 + o(1)`. Crossing needs `Q >> L^{-1/2}`, i.e.
**GAP-concentration** of the steps. Compare: rho `n^{1/2}`; RT-1472 explicit
exponent `2/3` at `ell=1/3`; A1 says the explicit exponent cannot fall below
`2/3` unless the steps concentrate.

### Why existing negatives do not already kill it
Wormald/Shearer/large-sieve/singular-series all bound counts or averages; none
rules out a *concentrated* step multiset raising `Q` above `L^{-1/2}`. A1 is the
first meter that directly tests that concentration.

### Likely fatal obstruction
Near-certain: the honest large-prime multiset is Sidon-like / GAP-free
(maximal doubling — same phenomenon that killed batch5 MATUNION and batch11
LORENTZIAN), so `Q=Theta(L^{-1/2})` and `delta->1/4`. A1 then **promotes to
barrier D1**, closing RT-1472 for the small-ball advice class, rather than
crossing.

### Minimal falsifying experiment
Toy `p in {1009, 4099, 16411}` (three sizes), seeds `20260719..20260723`,
ordinary prime-order controls. **Positive control:** a *planted* GAP step
multiset (large primes chosen inside an AP) should show `Q ~ L^{-1/4}`,
`delta>1/4`. **Negative control:** honest random large primes should show
`Q ~ L^{-1/2}`, `delta<=1/4`. Measure empirical `Q(S,w)` vs `k` and fit the
exponent.

### Quantitative promotion gate
Promote only if honest (non-planted) ordinary curves show measured
`delta = -d log Q / d log L > 1/4` with a fitted trend stable across all three
sizes and ordinary controls — a *measured supply exponent crossing 1/4*, not
correctness.

### Proof track
Theorem to establish: the large-prime-log step distribution mod `n` satisfies an
inverse-Halász hypothesis failure, i.e. it is not `L^{-o(1)}`-close to any GAP of
volume `L^{1-eps}`, hence `Q<=C L^{-1/2}` and `delta<=1/4` unconditionally.

### Disproof track
Exhibit an ordinary prime-order curve family whose honest large-prime multiset
provably concentrates on a short GAP (would kill A1's ceiling and the D1
barrier).

### Reproduction artifact
Contract `research/exp_halasz_smallball_supply.md`; implementation
`experiments/ecdlp_index_calculus/halasz_smallball_meter.sage`; result
`experiments/ecdlp_index_calculus/halasz_smallball_result.json`; audit
`experiments/ecdlp_index_calculus/halasz_smallball_verify.sage`; ledger
`ECFG-P1682`.

---

## Candidate: STEIN-CHEN-POISSON-A2  (ECFG-P1683)

### One-sentence mechanism
Exploit Poisson approximation (Stein-Chen) of the 2-LP **collision count** to
meter whether local dependence raises the RT-1472 enrichment `delta` above the
mean-preserving Poisson baseline.

### Status
HEURISTIC (detectability meter; feeds D1).

### Novelty classification
LEDGER-NEW (0 hits Stein-Chen / Poisson approximation).

### Semantic fingerprint
F = (object: indicator sum of 2-LP box-hits; ops: pair+hash; hidden structure:
positive dependence among overlapping-prime edges; discarded: edge identity;
retained: total-variation distance to Poisson; primitive: 2-LP pairing;
compression: none; rank: n/a; descent: n/a; cost exponent: `delta` via
dependence correction to Poisson mean).

### Nearest ledger entries
RT-1472/P1472 (same gate, distinction: Stein-Chen bounds *TV distance to
Poisson* of the count, not the occupancy exponent); batch4 CORRELATED-PEEL
(replica-symmetric peeling — distinction: Stein-Chen is a coupling bound on
dependence, not a DE fixed point); batch14 A1 large-sieve; batch15 A1 singular
series; batch8 Shearer. Distinction from all: the Chen-Stein `b1,b2` coupling
terms quantify dependence directly.

### Nearest literature
Barbour-Holst-Janson (1992), Poisson approximation: TV `<= b1 + b2 + b3`; the
mean is preserved and only local clustering can shift occupancy. Gap: the 2-LP
dependence graph's `b2` must be computed for the elliptic large-prime source.

### Target family
As A1.

### Full algorithmic path
1–3 as A1. 4. relation probability `= 1 - exp(-lambda)` under Poisson, corrected
by `b2`. 5–9 as A1.

### Cost model
If TV`->0`, occupancy is mean-preserving `Poisson(lambda)` with `lambda=Theta(L^{?})`
matching the baseline `delta=1/4`; crossing needs `b2` (clustering) to inflate
occupancy by `L^{>1/4}`. Compare to rho and RT-1472 `2/3`.

### Why existing negatives do not kill it
No prior meter isolates the *clustering* term `b2`; DE-peeling (batch4) assumes
a specific degree sequence.

### Likely fatal obstruction
Near-certain: the 2-LP dependence is weak (`b2=o(1)`), so occupancy is
mean-preserving and `delta->1/4`. Feeds D1.

### Minimal falsifying experiment
Same three sizes/seeds/controls as A1; positive control = planted
prime-sharing clusters (`b2=Theta(1)`); negative control = disjoint-prime edges.
Measure empirical TV to Poisson and occupancy exponent.

### Quantitative promotion gate
Honest ordinary curves show occupancy exponent `>1/4` attributable to a
measured `b2` bounded away from 0 across all sizes.

### Proof track
`b2 = o(1)` for honest large-prime sources ⇒ occupancy `~Poisson` ⇒ `delta<=1/4`.

### Disproof track
An ordinary family with `b2=Theta(1)` and occupancy exponent `>1/4`.

### Reproduction artifact
Contract `research/exp_steinchen_poisson_supply.md`; impl
`.../steinchen_poisson_meter.sage`; result `.../steinchen_poisson_result.json`;
audit `.../steinchen_poisson_verify.sage`; ledger `ECFG-P1683`.

---

## Candidate: BERRY-ESSEEN-RATE-A3  (ECFG-P1684)

### One-sentence mechanism
Exploit the multivariate Berry-Esseen convergence *rate* of the large-prime sum
to bound how fast the occupancy distribution approaches its Gaussian limit,
metering the residual that could carry `delta>1/4`.

### Status
OPEN (thin; INCOMPLETE-risk — flagged, feeds D1 not a standalone winner).

### Novelty classification
LEDGER-NEW (0 hits Berry-Esseen).

### Semantic fingerprint
As A1/A2 but retained info = third-moment CLT rate `Theta(rho_3 / sqrt(k))`.

### Nearest ledger entries
RT-1472; batch15 singular series (distinction: BE is a rate, singular series a
main term); A1 (distinction: A1 = sup small-ball, A3 = CLT-rate residual).

### Nearest literature
Bentkus (2003) multivariate BE rate `C d^{1/4} rho_3 / sqrt(k)`. Gap: `d` here
is the box dimension; over `Z/n` the lattice BE rate must be instantiated.

### Target family
As A1.

### Full algorithmic path
Meter only; stages inherited from A1. **Labeled INCOMPLETE** for the
descent/relation stages — it contributes a residual estimate, not a standalone
backend.

### Cost model
Residual occupancy `<= L^2 * rho_3/sqrt(k) = O(L^{2-1/2})` ⇒ `delta<=1/4`
consistent with A1; no crossing route on its own.

### Why existing negatives do not kill it
No prior BE-rate meter exists; but its value is confirmatory, not independent.

### Likely fatal obstruction
Bounded third moment ⇒ standard rate ⇒ `delta->1/4`.

### Minimal falsifying experiment
Same sizes/seeds/controls as A1; measure the BE residual exponent.

### Quantitative promotion gate
Residual exponent `>1/4` — near-impossible without heavy-tailed steps.

### Proof track
Bounded `rho_3` ⇒ BE rate ⇒ `delta<=1/4`.

### Disproof track
Heavy-tailed large-prime step law with slow BE rate.

### Reproduction artifact
Contract `research/exp_berryesseen_rate_supply.md`; ledger `ECFG-P1684`.

---

## GROUP B — Representation changes (finite-Lie-type / quantum-group)

## Candidate: YANGIAN-RMATRIX-B1  (ECFG-P1685)

### One-sentence mechanism
Represent the symmetric 5-point Semaev membership as a **spectral-parameter
R-matrix / Yangian transfer-matrix contraction** whose bond dimension — *not*
`deg(det M)<=dim` — controls membership cost, attacking the surviving P1512-R1
nonlinear-circuit exception.

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (0 hits Yangian / R-matrix / quantum group; no ECDLP prior art
found in the primary search; the nearest is the *planar* Temperley-Lieb/Hecke
attempt, batch13 B3, which is a strict specialization).

### Semantic fingerprint
F = (object: symmetrized Semaev 5-tensor as a lattice-model partition function;
public ops: evaluate `S_5`-symmetric summation polynomial; hidden structure:
`S_n`-symmetry = potential Yang-Baxter integrability with rational spectral
parameter; discarded: leaf enumeration; retained: transfer-matrix bond
dimension; relation-generation primitive: MPS/transfer-matrix contraction;
compression primitive: matrix-product-state truncation; rank mechanism:
bond dimension `chi`; descent: same transfer matrix; dominant cost exponent:
`log_L chi`).

### Nearest ledger entries
1. batch13 HECKE-TL-B3 — Temperley-Lieb planar contraction; **distinction:** TL
   is the *planar, non-spectral* quotient; the Yangian R-matrix is *non-planar*
   and carries a rational spectral parameter `u`, so B1 must be checked
   independently even though the likely kill is shared.
2. batch12 IMMANANT-INTERPOLATION-B2 — character-weighted determinant;
   **distinction:** immanant is a single symmetric-group class function; the
   R-matrix is a full braided-category morphism (quantum-group comodule).
3. batch11 NONCOMMUTATIVE-RANK-B2 — free-skew inner rank; **distinction:**
   nc-rank measures a pencil; the transfer matrix measures a *product* of
   R-matrices with a spectral flow.
4. P1512-R1 — closes scalar-linear Chow at `Omega(r^5)`; **distinction:** the
   R-matrix contraction is *not* a commutative determinant, so `deg(det)<=dim`
   does not bind it — B1 lives exactly in the nonlinear-circuit exception.
5. batch8 GKZ-DMODULE-B2 — holonomic rank = BKK volume; **distinction:** GKZ
   counts branches; the transfer matrix would *contract* them without
   materializing leaves.

### Nearest literature
Drinfeld Yangian `Y(gl_n)`; Baxter's commuting transfer matrices; Reshetikhin-
Turaev functor. Claim: a Yang-Baxter-solvable lattice model computes its
partition function by a poly-bond-dimension transfer matrix. Assumption: the
weights satisfy YBE. **Gap:** whether the elliptic addition law yields an
R-matrix satisfying YBE — almost certainly it does **not** (YBE would force a
free-fermion/6-vertex structure, i.e. a bilinear addition law).

### Target family
Ordinary prime-order `F_p`; excluded: curves with extra automorphisms (`j=0,
1728`) where the summation polynomial degenerates.

### Full algorithmic path
1. **factor base:** `L=q^ell` source-line points.
2. **relation generation:** membership of a 5-tuple = nonzero contraction of the
   R-matrix product `T(u)=R_{12}R_{13}...` over the source bond space.
3. **witness/verification:** transfer-matrix value `!=0` ⇒ relation; re-verified
   by exact EC-addition (claim tier: relation).
4. **relation probability:** `min(1, L^5/q)` (unchanged; representation change,
   not a probability change).
5. **matrix dims/density/rank:** transfer matrix `chi x chi`; `Theta(L)` rows.
6. **factor-log calibration:** standard.
7. **descent:** same transfer matrix on the target-marked tuple.
8. **offline/online:** R-matrix precompute offline `<=L^2`.
9. **memory/parallelism:** `chi^2` memory; parallel over bond blocks.

### Cost model
Membership query cost `= poly(chi) * L`. If `chi=O(polylog)`, query exponent
`alpha=1+o(1)<3/2` ⇒ **crosses** at m=5. If `chi=Theta(L)` (non-integrable),
`alpha>=3/2` reproducing the `r^5`/`r^3` floor. Compare rho `n^{1/2}`, RT-1476
`2/5` total at `alpha=1`.

### Why existing negatives do not kill it
`deg(det M)<=dim` (P1512-R1) bounds the commutative-determinant functional; the
R-matrix contraction is a non-commutative braided morphism outside that
functional. TL (batch13) only ruled out the *planar* sub-case.

### Likely fatal obstruction
Near-certain: the elliptic 5-point relation is **not Yang-Baxter integrable**
(the group law is not free-fermionic), so no fixed-bond R-matrix exists and
`chi=Theta(L)` ⇒ reproduces the floor. B1 then **closes the integrable-transfer-
matrix lane by name**.

### Minimal falsifying experiment
Toy `p in {1009, 4099, 16411}`, seeds `20260719..20260723`. **Positive
control:** a genuinely YBE-solvable toy relation (6-vertex / free-fermion
surrogate) should contract at bond `chi=O(1)`. **Negative control:** random
degree-matched non-integrable 5-tensor should force `chi=Theta(L)`. Measure the
minimal bond dimension (via TT-SVD truncation error `<10^-10`) of the actual
symmetrized Semaev tensor vs both controls, across all three sizes.

### Quantitative promotion gate
Promote only if the measured bond-dimension exponent
`c = d log chi / d log L < 1/2` for the **honest** symmetrized Semaev tensor
(giving `alpha<3/2`), stable across sizes — a *measured contraction exponent*,
not correctness.

### Proof track
Theorem: the symmetrized Semaev polynomial's transfer operator admits a
rational R-matrix satisfying YBE with bond dimension `O(L^{1/2-eps})`.

### Disproof track
Show the elliptic addition R-matrix violates YBE (spectral-curve genus `>1`),
forcing `chi=Theta(L)` — the expected outcome, which closes the lane.

### Reproduction artifact
Contract `research/exp_yangian_rmatrix_membership.md`; impl
`experiments/ecdlp_index_calculus/yangian_rmatrix_bond.sage`; result
`.../yangian_rmatrix_result.json`; audit `.../yangian_rmatrix_verify.sage`;
ledger `ECFG-P1685`.

---

## Candidate: FOOLING-SET-COVER-B2  (ECFG-P1686)

### One-sentence mechanism
Represent the m=5 membership matrix as a two-party communication problem and use
its **fooling-set / nondeterministic cover number** as an exact `alpha` meter for
RT-1476.

### Status
HYPOTHESIS (meter; feeds D3).

### Novelty classification
LEDGER-NEW (0 hits fooling set; `log-rank` has 1 unrelated hit, avoided).

### Semantic fingerprint
F = (object: membership matrix `M[x, (y,z,w,v)]`; ops: query rows/cols; hidden
structure: monochromatic-rectangle cover; discarded: exact value; retained:
cover/fooling-set size; primitive: rectangle cover; compression: nondeterministic
protocol; rank: cover number; descent: same protocol; cost exponent: `alpha` via
`log_L(cover)`).

### Nearest ledger entries
batch4 SIGNRANK-GAMMA2-B3 (sign-rank / `gamma_2` — distinction: fooling set is a
*combinatorial* cover, not a factorization norm); batch7 LIFTING-D1 (query-to-
communication lifting — distinction: fooling set is the base object, not the
lift); batch12 DISCREPANCY-CORRUPTION-A3 (discrepancy — distinction: fooling set
is a nondeterministic, not distributional, measure); batch15 round elimination;
P1476.

### Nearest literature
Yao (1979) fooling sets; Kushilevitz-Nisan (1997). Claim: `alpha >= log(fooling
set)/log L`. Gap: constructing a large fooling set for the elliptic membership
matrix.

### Target family
As B1.

### Full algorithmic path
1. factor base `L=q^ell`. 2. relation = row-column membership. 3. verified by
EC-addition. 4. prob `min(1,L^5/q)`. 5. matrix `L x L^4`; cover number metered.
6–9 standard.

### Cost model
`alpha >= log(cover)/log L`; if cover `>= L^{3/2}`, `alpha>=3/2` closes RT-1476.
If cover `= O(L)`, inconclusive (boundary). Compare rho, RT-1476.

### Why existing negatives do not kill it
Sign-rank/discrepancy are analytic; fooling set is combinatorial and can be
larger, giving a tighter floor.

### Likely fatal obstruction
Near-certain: the algebraic membership matrix has a *small* nondeterministic
cover (a single low-degree certificate covers many tuples), so cover `=O(L)` and
`alpha>=1<3/2` — boundary, not closure. Feeds D3.

### Minimal falsifying experiment
Three toy sizes/seeds/controls; positive control = random matrix (fooling set
`Theta(L^2)`); negative control = rank-1 matrix (fooling set `O(1)`). Measure the
fooling-set exponent of the honest membership matrix.

### Quantitative promotion gate
Honest membership fooling-set exponent `>3/2` across sizes.

### Proof track
Lower-bound the fooling set of the Semaev membership matrix by `L^{3/2}`.

### Disproof track
Exhibit an `O(L)` nondeterministic cover (the expected outcome).

### Reproduction artifact
Contract `research/exp_fooling_set_membership.md`; ledger `ECFG-P1686`.

---

## Candidate: KAZHDAN-LUSZTIG-CELL-B3  (ECFG-P1687)

### One-sentence mechanism
Decompose the S_5 descent of five-point membership along **Kazhdan-Lusztig
cells** of the Hecke algebra, hoping a small two-sided cell carries the whole
descent with sub-`L^{3/2}` cost.

### Status
OPEN (INCOMPLETE-risk — flagged; no established descent path yet).

### Novelty classification
LEDGER-NEW (0 hits Kazhdan-Lusztig / Bruhat).

### Semantic fingerprint
F = (object: Hecke module of the symmetrized backend; ops: KL-basis change;
hidden structure: cell partition of `S_5`; discarded: full basis; retained:
dominant cell dimension; primitive: cell projection; compression: two-sided cell;
rank: cell dimension; descent: cell-restricted; cost exponent: `log_L(cell dim)`).

### Nearest ledger entries
batch16 FI-MODULE-STABILITY-B1 (symmetric-tower generation degree — distinction:
KL cells are a *basis stratification*, not FI-generation); batch12 immanant;
batch13 HECKE-TL-B3 (TL is a Hecke *quotient*; KL cells are a *basis of the full
Hecke algebra*); batch7 SCHURPLETHYSM-B3; P1512-R1.

### Nearest literature
Kazhdan-Lusztig (1979); cells of `S_n`. Claim: cells refine the regular
representation into `RSK`-shaped blocks. Gap: whether membership descent
factors through a single small cell — no reason it should.

### Target family
As B1. **Labeled INCOMPLETE:** the map from EC-addition descent to a KL cell is
not constructed; needs a Phase-0 lemma.

### Full algorithmic path
Stages 1–4 as B1; **stage 5–7 (cell projection ⇒ descent) UNSPECIFIED** ⇒
INCOMPLETE.

### Cost model
If descent lives in a cell of dimension `L^{<3/2}`, `alpha<3/2`. No evidence it
does.

### Why existing negatives do not kill it
Cells are a genuinely new stratification; but the missing descent map is fatal
to completeness.

### Likely fatal obstruction
The membership descent spreads across all cells (RSK shape not concentrated), so
cell dimension `=Theta(L^{3/2})` — reproduces the floor. Plus the descent map is
unconstructed.

### Minimal falsifying experiment
Toy `S_5` Hecke-algebra decomposition of the symmetrized backend at three
sizes; measure the dominant-cell dimension exponent.

### Quantitative promotion gate
Dominant-cell exponent `<3/2` AND a constructed descent map.

### Proof track
The elliptic 5-point condition projects onto a single two-sided cell.

### Disproof track
The RSK image is spread — the expected outcome.

### Reproduction artifact
Contract `research/exp_kl_cell_descent.md`; ledger `ECFG-P1687`. **Not selected
(INCOMPLETE).**

---

## GROUP C — High-risk speculative mechanisms

## Candidate: PROXIMITY-TESTER-C1  (ECFG-P1688)

### One-sentence mechanism
Replace exact five-point membership with a **sublinear property-testing
proximity oracle** (accept tuples on/near the Semaev variety, reject far ones)
plus a rho fallback on the tested residue, seeking a sub-`L^{3/2}` average-case
backend.

### Status
HYPOTHESIS.

### Novelty classification
POSSIBLY NOVEL (0 hits locally testable / property testing / PCP of proximity;
distinct from all prior avg-case backends by the *proximity-gap* axis).

### Semantic fingerprint
F = (object: Semaev variety `V` and its `epsilon`-neighborhood; ops: `q`
coordinate queries; hidden structure: local testability / proximity gap of `V`;
discarded: exact membership on `epsilon`-close tuples; retained: proximity
verdict; relation-generation primitive: tester-accepted tuples; compression:
oblivious tester; rank: standard; descent: tester + rho fallback; cost exponent:
tester query `alpha`).

### Nearest ledger entries
batch13 RANDOM-RESTRICTION-C1 (Håstad shrinkage avg-case — distinction: tester
uses a *proximity gap*, not restriction shrinkage); batch10 DEQUANTIZED-SAMPLING-
C1 (sample-and-query — distinction: proximity testing, not stable-rank
sampling); batch16 HYPERCONTRACTIVITY-SSE-C1; batch15 KOLMOGOROV-C1; P1476.

### Nearest literature
Rubinfeld-Sudan (1996) low-degree testing; Ben-Sasson et al. PCP-of-proximity;
Ben-Sasson-Sudan robust LTCs. Claim: some low-degree codes are testable with
`O(1)` queries under a proximity gap. Assumption: a robust proximity gap exists.
Gap: whether the single hypersurface `V` (codim 1, not a code) is locally
testable.

### Target family
As B1; excluded: degenerate `j`.

### Full algorithmic path
1. factor base `L=q^ell`. 2. relation generation via tester-accepted 5-tuples.
3. **witness/verification:** every tester-accepted tuple is re-verified exactly
   by EC-addition before use (claim tier: relation; false accepts discarded).
4. relation probability `= min(1,L^5/q)` on the accepted set.
5. matrix `L x` sources; sparse LA `L^2`.
6. calibration standard.
7. descent: tester on target-marked tuple + rho fallback on the residue.
8. offline: tester precompute `<=L^2`.
9. memory: tester query buffer; parallel over tuples.

### Cost model
If `V` is `(epsilon,q)`-testable with `q=L^{1/2-delta'}`, membership query
`alpha=1/2-delta'<3/2` ⇒ **crosses** with slack. If `V` needs `q=Theta(deg V)=
Theta(L^{1/2+})` queries, `alpha>=3/2` and the tester is no cheaper than exact.
Compare rho, RT-1476.

### Why existing negatives do not kill it
Prior avg-case backends attacked shrinkage/sampling/incompressibility; none
tested the *proximity-gap* property of `V`. The exact-vs-tester gap is new.

### Likely fatal obstruction
Near-certain self-defeating: a codim-1 algebraic hypersurface has **no robust
proximity gap** — flipping one coordinate moves an on-variety point to Hamming-
distance 1 but the point is then genuinely off `V`, so "close" tuples are
exactly the reject set; testing = exact deciding, `alpha>=3/2`. C1 then **feeds
D2** (property-testing query barrier). This mirrors batch13 C1's no-shrinkage and
batch16 C1's no-SSE self-defeats.

### Minimal falsifying experiment
Three toy sizes/seeds/ordinary controls. **Positive control:** a genuine
low-degree Reed-Muller codeword (known `O(1)`-testable) — tester should accept
with few queries. **Negative control:** a random codim-1 hypersurface — tester
should need `Theta(deg)` queries. Measure the tester query exponent needed for
proximity-gap `epsilon=0.1` on the honest Semaev `V` vs both controls.

### Quantitative promotion gate
Honest `V` tester query exponent `<3/2` at fixed proximity gap, stable across
sizes AND end-to-end backend total exponent `<2/5` — a *measured query
exponent* plus complete-cost trend, not correctness.

### Proof track
The Semaev hypersurface admits a robust local test with query complexity
`o(L^{3/2})`.

### Disproof track
Prove no proximity gap: a `1`-local perturbation family that is `epsilon`-far but
`O(1)`-query-indistinguishable ⇒ `alpha>=3/2` (the expected outcome; = D2).

### Reproduction artifact
Contract `research/exp_proximity_tester_membership.md`; impl
`experiments/ecdlp_index_calculus/proximity_tester_backend.sage`; result
`.../proximity_tester_result.json`; audit `.../proximity_tester_verify.sage`;
ledger `ECFG-P1688`.

---

## Candidate: ALGEBRAIC-REGULARITY-EXCESS-C2  (ECFG-P1689)

### One-sentence mechanism
Apply the **(algebraic) Szemerédi regularity lemma** to the 2-LP bipartite graph
to find a dense regular pair carrying an excess-edge sub-block with `delta>1/4`.

### Status
HEURISTIC (feeds D1).

### Novelty classification
LEDGER-NEW (0 hits regularity lemma / Ramsey).

### Semantic fingerprint
F = (object: 2-LP bipartite graph; ops: regularity partition; hidden structure:
dense regular pair; discarded: irregular pairs; retained: densest regular block;
primitive: 2-LP pairing; compression: regularity partition; rank: n/a; descent:
n/a; cost exponent: `delta` via densest-block density).

### Nearest ledger entries
batch6 GRAPHON-CUTNORM-B3 (cut-norm density — distinction: regularity is the
*partition* behind cut-norm, and Tao's algebraic regularity gives `O(1)` parts
for definable graphs); batch4 CORRELATED-PEEL; batch16 hereditary discrepancy;
P1472.

### Nearest literature
Szemerédi (1975); Tao (2012) algebraic regularity for definable graphs over
`F_q` (bounded VC ⇒ `O(1)` regular parts, density `0/1+o(1)`). Claim: definable
graphs are *super-regular* with near-`0/1` densities. Gap: this predicts **no**
intermediate dense excess block.

### Target family
As A1.

### Full algorithmic path
Supply meter; stages as A1.

### Cost model
Densest regular block density `d`; excess `delta=log_L(d * block / baseline)`.
Algebraic regularity ⇒ `d in {o(1), 1-o(1)}`, so either no block or a trivial
full block — neither gives `delta>1/4`. Compare rho, RT-1472.

### Why existing negatives do not kill it
Cut-norm (batch6) measured global density; regularity localizes to the densest
pair — a genuinely new localization.

### Likely fatal obstruction
Near-certain: Tao algebraic regularity forces `0/1` densities for the definable
2-LP graph ⇒ no intermediate excess ⇒ `delta<=1/4`. Feeds D1.

### Minimal falsifying experiment
Three sizes/seeds; positive control = planted dense bipartite block; negative
control = honest algebraic 2-LP graph. Measure densest-regular-pair density
exponent.

### Quantitative promotion gate
Honest densest regular block yields `delta>1/4` across sizes.

### Proof track
The definable 2-LP graph has an intermediate-density regular pair (contra Tao).

### Disproof track
Algebraic regularity `0/1` dichotomy (expected).

### Reproduction artifact
Contract `research/exp_algebraic_regularity_supply.md`; ledger `ECFG-P1689`.

---

## Candidate: DELIGNE-LUSZTIG-SAMPLER-C3  (ECFG-P1690)

### One-sentence mechanism
Build an average-case membership estimator from **Deligne-Lusztig virtual
character** orthogonality on the finite group of Lie type carrying `E(F_p)`,
projecting onto the relation subspace with a rho fallback.

### Status
OPEN (reject-tier probe; retained for the finite-Lie-type import).

### Novelty classification
LEDGER-NEW (0 hits Deligne-Lusztig).

### Semantic fingerprint
F = (object: class functions on the Lie-type group; ops: character sums; hidden
structure: DL virtual-character orthogonality; discarded: exact tuple; retained:
character-projected membership estimate; primitive: character sampling;
compression: virtual-character basis; rank: standard; descent: character
estimator + rho; cost exponent: sampler query).

### Nearest ledger entries
batch14 KATZ-SARNAK-SYMMETRY-C3 (family monodromy — distinction: DL characters
are of the *group itself*, an explicit projector, not a monodromy symmetry);
batch2 C3 closed character-sum bias (Deligne equidistribution — **this is the
likely kill**); batch8 RKHS-KERNEL-C2 (Peter-Weyl Gram — distinction: DL is the
Lie-type refinement of Peter-Weyl).

### Nearest literature
Deligne-Lusztig (1976). Claim: irreducible characters of finite reductive groups
come from `ell`-adic cohomology of DL varieties. Gap: `E(F_p)` is a *commutative*
group (a torus at the level of the abelian variety points), so its characters are
just additive/multiplicative characters.

### Target family
As B1.

### Full algorithmic path
Estimator; stages inherited; **descent via character estimator + rho fallback**.

### Cost model
If DL characters gave a low-rank membership projector, sampler query `<L^{3/2}`.
But abelian ⇒ characters are 1-dimensional ⇒ projector rank `Theta(n)` ⇒ no gain.

### Why existing negatives do not kill it
DL is the non-abelian refinement; must be checked even though `E(F_p)` is
abelian.

### Likely fatal obstruction
Near-certain: `E(F_p)` abelian ⇒ DL degenerates to additive characters ⇒
collapses to the **closed character-sum lane** (batch2 C3), Deligne
equidistribution kill.

### Minimal falsifying experiment
Three sizes/seeds; measure DL-projector rank on the toy group; compare to
additive-character projector.

### Quantitative promotion gate
DL-projector rank `o(n)` giving sampler query `<L^{3/2}` — near-impossible for
abelian groups.

### Proof track
A non-abelian Lie-type structure on `E(F_p)`-membership with low-rank DL
projector.

### Disproof track
Abelian collapse to additive characters (expected).

### Reproduction artifact
Contract `research/exp_deligne_lusztig_sampler.md`; ledger `ECFG-P1690`. **Not
selected (near-certain closed-lane collapse).**

---

## GROUP D — Negative-theory / barrier candidates (higher-EV)

## Candidate: HALASZ-ANTICONCENTRATION-BARRIER-D1  (ECFG-P1691)

### One-sentence mechanism
Prove Halász/inverse-Littlewood-Offord ⇒ small-ball mass `O(L^{-1/2})` for any
honest large-prime step multiset without GAP structure ⇒ `delta<=1/4`
**unconditional**, closing RT-1472 for anti-concentration-countable advice.

### Status
CONJECTURE (barrier; partner of A1). **Highest-EV of this run.**

### Novelty classification
POSSIBLY NOVEL (first anti-concentration barrier; distinct from batch14 large-
sieve, batch15 singular-series, batch16 hereditary-discrepancy, batch17 ergodic
supply barriers).

### Semantic fingerprint
As A1 but as a *lower bound on the exponent's ceiling*: retained = inverse-ELO
GAP dichotomy.

### Nearest ledger entries / literature
RT-1472; batch14 LARGE-SIEVE-BARRIER-D1 (distinction: large sieve is a dual
`L^2` inequality over moduli; ELO/Halász is a single-sum anti-concentration
dichotomy); Nguyen-Vu (2011) optimal inverse-Littlewood-Offord; Tao-Vu (2009).
Claim: `Q(S,r)=L^{-1/2+o(1)}` unless `>1-eps` mass of steps lies in a GAP of
volume `L^{o(1)}`.

### Target family
Ordinary prime-order `F_p`; advice class = any 2-LP deck whose edges are
generated by a bounded linear form in the large-prime logs.

### Full algorithmic path
Barrier — closes the enrichment stage of RT-1472; no descent path required (it
is a no-go on `delta`).

### Cost model
`delta = 1 + log_L Q <= 1 + (-1/2) = 1/2`... in the occupancy normalization
`delta = 1/4 + (log_L Q + 1/2)`, so `Q<=L^{-1/2}` ⇒ `delta<=1/4`. Any advice with
`delta>1/4` must exhibit inverse-ELO GAP concentration.

### Why existing negatives do not kill it
No prior supply barrier used anti-concentration; large-sieve/singular-series
bound different objects and leave the small-ball route formally open.

### Likely fatal obstruction (to the barrier)
The inverse-ELO theorem is *qualitative*; converting "not in a short GAP" to a
quantitative `delta<=1/4` needs a boundary lemma at exactly `1/4` — the same
qualitative→quantitative gap as batch17 D1.

### Minimal falsifying / confirming experiment
Same as A1 across three sizes; the barrier is confirmed if honest ordinary
curves never exceed `Q=L^{-1/2}` and planted-GAP controls do.

### Quantitative promotion gate
A proof (or unconditional measured ceiling) that honest advice has `delta<=1/4`.

### Proof track
Inverse-Littlewood-Offord (Nguyen-Vu) + a `1/4`-boundary quantitative lemma ⇒
`delta<=1/4` for all GAP-free advice.

### Disproof track
An ordinary family with GAP-concentrated large primes and `delta>1/4`.

### Reproduction artifact
Shares A1's artifacts; ledger `ECFG-P1691` (barrier record).

---

## Candidate: PCPP-TESTER-QUERY-BARRIER-D2  (ECFG-P1692)

### One-sentence mechanism
Prove the Semaev hypersurface has no robust proximity gap ⇒ any property tester
needs `Omega(L^{1/2+})` queries ⇒ `alpha>=3/2`, closing RT-1476 in the tester
class (partner of C1).

### Status
CONJECTURE (barrier). High-EV.

### Novelty classification
POSSIBLY NOVEL (first property-testing/PCPP query barrier; distinct from batch8
approx-degree, batch13 sensitivity, batch11 LDC, batch16 evasiveness, batch15
packing/round-elimination).

### Semantic fingerprint
Object: codim-1 hypersurface `V`; retained: proximity-gap query lower bound.

### Nearest ledger entries / literature
RT-1476/P1476; batch11 LDC (distinction: LDC = length-vs-query decoding; PCPP =
proximity testing); Ben-Sasson-Harsha-Raskhodnikova (2005) lower bounds for
testing; Fischer (2004). Claim: testers for "hard" properties need many queries;
codim-1 algebraic sets lack the tensor/product structure LTCs exploit.

### Target family
As C1.

### Full algorithmic path
Barrier on the membership-tester stage.

### Cost model
No proximity gap ⇒ `epsilon`-far tuples include Hamming-distance-1 perturbations
⇒ tester query `>= Omega(deg V) = Omega(L^{1/2+})` ⇒ `alpha>=3/2`.

### Why existing negatives do not kill it
Prior `alpha` barriers used degree/rank/communication; none used the
proximity-gap/local-testability axis.

### Likely fatal obstruction (to the barrier)
If a *robust* sub-hypersurface with a genuine gap exists (e.g. via a lifted
tensor code encoding the relation), the tester could be cheaper — but codim-1
membership almost surely lacks it.

### Minimal falsifying / confirming experiment
As C1; barrier confirmed if honest `V` tester query exponent `>=3/2` while
Reed-Muller control is `O(1)`.

### Quantitative promotion gate
Proof or measured `alpha>=3/2` for the honest tester.

### Proof track
No-proximity-gap lemma for codim-1 algebraic hypersurfaces over `F_q`.

### Disproof track
A robust tensor-code encoding of the Semaev relation with `O(1)`-query test.

### Reproduction artifact
Shares C1's artifacts; ledger `ECFG-P1692` (barrier record).

---

## Candidate: FANO-LECAM-MINIMAX-BARRIER-D3  (ECFG-P1693)

### One-sentence mechanism
Use Fano/Le Cam/Assouad statistical-minimax lower bounds ⇒ any backend
distinguishing relation-tuples from random tuples must acquire `Omega(log|V|)`
bits ⇒ query `Omega(L^{1/2+})` ⇒ `alpha>=3/2`, closing RT-1476 in the
information-theoretic backend class.

### Status
CONJECTURE (barrier).

### Novelty classification
POSSIBLY NOVEL (first statistical-minimax barrier; distinct from batch17 SQ
statistical dimension — SQ is a *detection-threshold* over queries to a
distribution oracle; Fano/Le Cam/Assouad is a *minimax estimation* query floor).

### Semantic fingerprint
Object: hypothesis test relation-vs-random; retained: mutual-information floor
⇒ query count.

### Nearest ledger entries / literature
RT-1476; batch17 SQ-STATISTICAL-DIMENSION-C3 (distinction above); batch11 LDLR
(low-degree likelihood — distinction: LDLR is a *detectability* meter, Fano is a
*query* floor); Yu (1997) Le Cam/Fano/Assouad; Tsybakov (2009). Claim: to
identify the correct tuple among `|V|` alternatives with constant error, need
`Omega(log|V|/I)` samples where `I` is per-query information.

### Target family
As C1.

### Full algorithmic path
Barrier on the membership/descent stage.

### Cost model
Per coordinate query yields `O(log q)` bits; identifying the relation among
`|V|=Theta(L^4)` requires `Omega(L^{1/2+})` queries when the per-query
information is `o(L^{-1/2})` ⇒ `alpha>=3/2`.

### Why existing negatives do not kill it
SQ/LDLR bound *detection*; Fano/Le Cam bound the *query cost of recovery*, which
is what RT-1476 charges.

### Likely fatal obstruction (to the barrier)
If a single query is *highly* informative (an algebraic short-circuit revealing
many coordinates at once), the Fano floor loosens below `3/2`. The nonlinear
membership circuit exception is exactly such a potential short-circuit.

### Minimal falsifying / confirming experiment
Three sizes/seeds; estimate empirical per-query mutual information between a
coordinate query and the membership bit; confirm the Fano floor exponent.

### Quantitative promotion gate
Proof or measured `alpha>=3/2` from the information floor.

### Proof track
Per-query information `o(L^{-1/2})` for the elliptic membership channel ⇒ Fano
floor `alpha>=3/2`.

### Disproof track
A high-information algebraic query (the nonlinear-circuit exception realizing
`o(L^{-1/2})` failure).

### Reproduction artifact
Contract `research/exp_fano_lecam_minimax_barrier.md`; ledger `ECFG-P1693`
(barrier record).

---

## RANKING

Scores (0–5): D1 = distance-from-ledger, D2 = exact-verifier plausibility,
D3 = exponent-not-constant, D4 = complete-path, D5 = toy falsifiability,
D6 = literature-novelty confidence, D7 = hidden-preprocessing risk (5 = low
risk). Rejected if novelty `<3`, no descent path, no rho comparison, or no
precise distinction from the closest ledger entry.

| Cand | D1 | D2 | D3 | D4 | D5 | D6 | D7 | verdict |
|---|---|---|---|---|---|---|---|---|
| **HALASZ-SMALLBALL-A1** | 4 | 5 | 4 | 4 | 5 | 4 | 4 | **conservative winner** |
| STEIN-CHEN-POISSON-A2 | 4 | 4 | 3 | 4 | 5 | 4 | 4 | retained (feeds D1) |
| BERRY-ESSEEN-RATE-A3 | 3 | 4 | 2 | 2 | 4 | 4 | 4 | INCOMPLETE (feeds D1) |
| **YANGIAN-RMATRIX-B1** | 5 | 4 | 5 | 4 | 4 | 4 | 3 | **representation winner** |
| FOOLING-SET-COVER-B2 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | retained (feeds D3) |
| KAZHDAN-LUSZTIG-CELL-B3 | 4 | 3 | 3 | 1 | 3 | 4 | 3 | REJECTED (INCOMPLETE) |
| **PROXIMITY-TESTER-C1** | 5 | 4 | 5 | 4 | 4 | 4 | 3 | **high-risk winner** |
| ALGEBRAIC-REGULARITY-C2 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | retained (feeds D1) |
| DELIGNE-LUSZTIG-C3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | REJECTED (closed-lane) |
| **HALASZ-BARRIER-D1** | 5 | 4 | 5 | 4 | 5 | 5 | 4 | **highest-EV** |
| PCPP-BARRIER-D2 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | high-EV |
| FANO-LECAM-BARRIER-D3 | 5 | 4 | 5 | 4 | 4 | 5 | 4 | high-EV |

**Selected three winners** (per required output): conservative =
**HALASZ-SMALLBALL-A1**, representation = **YANGIAN-RMATRIX-B1**, high-risk =
**PROXIMITY-TESTER-C1**. Contracts and first commands below. The three
**D-barriers are higher expected-value** than the winners because each threshold,
if it bites, closes a live gate (D1→RT-1472, D2/D3→RT-1476); they are recorded as
the true priority.

---

## WINNER CONTRACTS + FIRST COMMANDS

### Contract 1 — HALASZ-SMALLBALL-A1 (ECFG-P1682)

```yaml
experiment: EXP-ICSUPPLY-HALASZ-001
hypothesis: >
  For honest ordinary prime-order curves, the two-large-prime step multiset is
  GAP-free, so Halasz small-ball mass Q ~ L^{-1/2} and the RT-1472 enrichment
  delta <= 1/4 (no rho crossing). Planted-GAP advice exceeds it.
null_hypothesis: honest advice already achieves delta > 1/4 via concentration.
target_family: ordinary prime-order F_p; exclude anomalous / tiny-CM / low-k.
sizes: [1009, 4099, 16411]
seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
controls:
  positive: planted-GAP large-prime multiset (steps in an AP)
  negative: honest random large primes
  ordinary_prime_order: required per size
metrics: [smallball_mass_Q, occupancy_exponent_delta, gap_volume_estimate]
baseline: rho log2(0.886*sqrt(n)); RT-1472 explicit exponent 2/3 at ell=1/3
promotion_gate: honest delta > 1/4 stable across all sizes (measured supply exponent)
falsification: honest delta <= 1/4 and only planted-GAP exceeds it (=> promote D1)
claim_tier: relation-supply meter only; no ECDLP recovery claimed
artifacts:
  contract: research/exp_halasz_smallball_supply.md
  impl: experiments/ecdlp_index_calculus/halasz_smallball_meter.sage
  result: experiments/ecdlp_index_calculus/halasz_smallball_result.json
  audit: experiments/ecdlp_index_calculus/halasz_smallball_verify.sage
  ledger: ECFG-P1682
```

First command:
```bash
sage experiments/ecdlp_index_calculus/halasz_smallball_meter.sage \
  --sizes 1009,4099,16411 --seeds 20260719,20260720,20260721,20260722,20260723 \
  --B-exponent 0.2 --controls planted_gap,honest_random \
  --out experiments/ecdlp_index_calculus/halasz_smallball_result.json
```

### Contract 2 — YANGIAN-RMATRIX-B1 (ECFG-P1685)

```yaml
experiment: EXP-ICMEMB-YANGIAN-001
hypothesis: >
  The symmetrized five-point Semaev tensor is NOT Yang-Baxter integrable, so its
  transfer-matrix bond dimension chi = Theta(L) (alpha >= 3/2), reproducing the
  P1512-R1 floor and closing the integrable-transfer-matrix lane.
null_hypothesis: chi = O(polylog) giving alpha < 3/2 (would cross).
target_family: ordinary prime-order F_p; exclude j in {0,1728}.
sizes: [1009, 4099, 16411]
seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
controls:
  positive: 6-vertex / free-fermion YBE-solvable surrogate (chi=O(1))
  negative: random degree-matched non-integrable 5-tensor (chi=Theta(L))
  ordinary_prime_order: required
metrics: [min_bond_dim_chi, tt_svd_truncation_error, bond_exponent_c]
baseline: rho; RT-1476 total 2/5 at alpha=1
promotion_gate: honest bond exponent c < 1/2 (=> alpha < 3/2) stable across sizes
falsification: honest c ~ 1 (=> closes lane, no crossing)
claim_tier: membership representation; every accepted tuple re-verified by EC-add
artifacts:
  contract: research/exp_yangian_rmatrix_membership.md
  impl: experiments/ecdlp_index_calculus/yangian_rmatrix_bond.sage
  result: experiments/ecdlp_index_calculus/yangian_rmatrix_result.json
  audit: experiments/ecdlp_index_calculus/yangian_rmatrix_verify.sage
  ledger: ECFG-P1685
```

First command:
```bash
sage experiments/ecdlp_index_calculus/yangian_rmatrix_bond.sage \
  --sizes 1009,4099,16411 --seeds 20260719,20260720,20260721,20260722,20260723 \
  --tt-tol 1e-10 --controls sixvertex,random_nonintegrable \
  --out experiments/ecdlp_index_calculus/yangian_rmatrix_result.json
```

### Contract 3 — PROXIMITY-TESTER-C1 (ECFG-P1688)

```yaml
experiment: EXP-ICMEMB-PROXTEST-001
hypothesis: >
  The codim-1 Semaev hypersurface has no robust proximity gap, so any property
  tester needs Omega(deg) = Omega(L^{1/2+}) queries (alpha >= 3/2); testing is no
  cheaper than exact deciding.
null_hypothesis: a robust gap gives a sublinear tester with alpha < 3/2.
target_family: ordinary prime-order F_p; exclude degenerate j.
sizes: [1009, 4099, 16411]
seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
controls:
  positive: Reed-Muller codeword (O(1)-query testable)
  negative: random codim-1 hypersurface (Theta(deg)-query)
  ordinary_prime_order: required
metrics: [tester_query_exponent_alpha, proximity_gap_epsilon, false_accept_rate]
baseline: rho; RT-1476 alpha<3/2 gate; end-to-end total exponent target <2/5
promotion_gate: honest tester alpha < 3/2 at eps=0.1 AND backend total < 2/5
falsification: honest tester alpha >= 3/2 (=> feeds D2, exact=test)
claim_tier: membership; all tester-accepted tuples re-verified exactly by EC-add
artifacts:
  contract: research/exp_proximity_tester_membership.md
  impl: experiments/ecdlp_index_calculus/proximity_tester_backend.sage
  result: experiments/ecdlp_index_calculus/proximity_tester_result.json
  audit: experiments/ecdlp_index_calculus/proximity_tester_verify.sage
  ledger: ECFG-P1688
```

First command:
```bash
sage experiments/ecdlp_index_calculus/proximity_tester_backend.sage \
  --sizes 1009,4099,16411 --seeds 20260719,20260720,20260721,20260722,20260723 \
  --proximity-eps 0.1 --controls reed_muller,random_hypersurface \
  --out experiments/ecdlp_index_calculus/proximity_tester_result.json
```

---

## RED-TEAM: are the three winners disguised repetitions or cost-negative?

**HALASZ-SMALLBALL-A1.** *Disguised repetition?* The anti-concentration /
small-ball object (`Q(S,r)`, inverse-Littlewood-Offord GAP dichotomy) is
grep-verified absent from all 19 reports and both ledgers; it is genuinely
distinct from the count/entropy/average supply meters (Wormald, Shearer,
Delsarte-LP, container, large sieve, singular series, hereditary discrepancy,
Furstenberg). *Cost-negative?* **Near-certain yes** — the honest large-prime
multiset is Sidon-like/GAP-free (the same maximal-doubling phenomenon that killed
batch5 MATUNION and batch11 LORENTZIAN), so `Q=Theta(L^{-1/2})` and `delta->1/4`.
A1 is therefore a **scoped negative that promotes to barrier D1**, not a
crossing. Its value is that D1 would close RT-1472 for the anti-concentration
advice class by name.

**YANGIAN-RMATRIX-B1.** *Disguised repetition?* The rational-spectral-parameter
R-matrix / Yangian transfer matrix is a strict superset of the *planar*
Temperley-Lieb/Hecke attempt (batch13 B3) and outside the immanant (batch12),
nc-rank (batch11), and GKZ (batch8) representations; it is genuinely new. It also
correctly targets the one surviving P1512-R1 nonlinear-circuit exception, since
`deg(det)<=dim` does not bind a braided-category contraction. *Cost-negative?*
**Near-certain yes** — the elliptic addition law is not free-fermionic, so no
R-matrix satisfies the Yang-Baxter equation, the bond dimension is `Theta(L)`,
and the contraction reproduces the `r^5`/`r^3` floor. B1 is a **lane-closure by
name** (integrable transfer-matrix backend), not a crossing. Residual risk: the
bond-dimension measurement is the binding cost and TT-SVD truncation must be
audited for hidden preprocessing (D7=3).

**PROXIMITY-TESTER-C1.** *Disguised repetition?* The property-testing /
proximity-gap axis is distinct from every prior average-case backend (random
restriction batch13, dequantized sampling batch10, hypercontractivity batch16,
Kolmogorov batch15) — those attacked shrinkage/sampling/incompressibility, not
local testability. *Cost-negative?* **Near-certain yes, self-defeating** — a
codim-1 algebraic hypersurface has no robust proximity gap, so `epsilon`-far
tuples are exactly the reject set, testing equals exact deciding, and
`alpha>=3/2`. C1 thus **feeds barrier D2**, mirroring the no-shrinkage (batch13
C1) and no-SSE (batch16 C1) self-defeats.

**Overall.** All three winners are near-certain **scoped negatives / lane
closures**, not rho crossings; each pairs with a higher-EV D-barrier (A1↔D1,
B1↔D2 via the property-testing floor is C1's, C1↔D2, and D3 as an independent
information-theoretic floor on RT-1476). The three D-barriers converge on
conclusions the analytic-supply arm (RT-1472 δ≤1/4) and the query-complexity arm
(RT-1476 α≥3/2) already point to, imported through three grep-verified 0-hit
technology areas. **No break is claimed. RT-1472 and RT-1476 remain open.**

---

## Claim discipline

Every result above is a **meter, representation, or barrier** at toy scale;
none is a verified ECDLP recovery. Correctness (relation validity, tensor
contraction, tester acceptance) is distinguished throughout from performance
(supply exponent `delta`, membership exponent `alpha`, complete-cost vs rho). All
tester/backend acceptances are re-verified exactly by EC-addition before use
(relation claim tier only). A failed candidate is a **scoped negative result**
bounded to the tested curves, parameters, solver, and budget — not evidence that
prime-field ECDLP is unimprovable. Reports live as uncommitted files; not
committed unless the Coordinator asks.
