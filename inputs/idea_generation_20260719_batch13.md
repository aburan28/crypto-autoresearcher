# ECDLP Idea Generation — 2026-07-19 batch13 (run 19 overall)

**Role:** Research Director, empirical cryptanalysis lab.
**Target:** a non-generic prime-field ECDLP algorithm whose *complete* cost beats the
single-target Pollard-rho `0.886·sqrt(n)` baseline. Toy correctness, a new coordinate system,
a relation certificate, faster preprocessing, or a solver improvement alone is **not** a
breakthrough.
**Scope:** generated toy curves, public benchmark instances, synthetic data only. No wallets,
production keys, accounts, or unauthorized systems.

---

## 0. Executive summary

This is the **nineteenth** idea-generation run and the **thirteenth** dated `20260719`. It
**reconfirms mechanism saturation**: the 18 prior runs plus the two committed ledgers already
span ~60 mechanism lanes, and every honest sub-rho surface has collapsed onto exactly two live,
unrealized conditional theorems:

- **RT-1472** — two-large-prime graph enrichment must reach supply exponent `delta > 1/4` at
  `B = n^(1/5)` (cost exponent `max(2ell, 1-ell, 1+1/5-2ell)`, min `2/3` at `ell=1/3`);
- **RT-1476** — an m=5 implicit-membership backend must reach query exponent `alpha < 3/2`
  (setup `<= L^2`, random-like support, `Theta(L)` sparse rows).

The value this run, as in runs 8–18, is **not a claimed crossing**. It is (a) importing three
technology families that are **grep-verified 0-hit** across all 20 prior reports and both
ledgers, and (b) showing where each family's threshold **closes** a live gate. Twelve candidates
are generated; all twelve are near-certain **scoped negatives / lane-closures** that converge on
`delta <= 1/4` and `alpha >= 3/2`. **No break is claimed. RT-1472 and RT-1476 remain open.**

The three imported 0-hit families:

1. **Correlation & second-moment inequalities** (Janson, FKG–Harris, Paley–Zygmund,
   second-moment method) — RT-1472 supply arm. Distinct from every prior supply meter
   (Stein–Chen Poisson mean-field batch18, anti-concentration/small-ball batch18, large-sieve L²
   batch14, Shearer entropy batch8, singular-series batch15, ergodic recurrence batch17,
   hereditary discrepancy batch16): those bound counts / entropy / averages / additive-image
   spread; the **variance and pairwise-dependency** `Delta` of the enriched-pair count is a new
   operation.
2. **Formula-size / depth lower bounds** (Nechiporuk distinct-subfunction counting;
   Karchmer–Wigderson depth↔communication) — RT-1476 query arm. Distinct from every prior circuit
   / query / communication LB (shifted-partials depth-4 batch10, Nisan nc-ABP batch10,
   Raz-multilinear batch11, query-to-communication lifting batch7, cell-probe/round-elimination
   batch12/15, sensitivity/Huang batch13, evasiveness batch16, resolution-width batch17):
   Nechiporuk is a **general-formula size** bound via subfunction counting on a *variable
   partition* of the 5 membership coordinates.
3. **Geometric rank** (Kopparty–Moshkovitz–Zuiddam) and **Hochschild/cyclic homology** —
   representation arm, attacking the surviving P1512-R1 **nonlinear-circuit exception**. Geometric
   rank `GR(T) = codim{ (x_1..x_{d-1}) : T(x_1,..,x_{d-1},·)=0 }` is a **geometric codimension**
   invariant with `subrank <= GR <= slice rank` and `GR ~ analytic rank` asymptotically — it is
   **not** the commutative-determinant degree `deg(det M) <= dim` that closed P1512-R1. Distinct
   from asymptotic-spectrum batch5, analytic-rank batch11, slice-rank-1 batch4, Segre-excess
   batch13, Yangian batch18.

Winners: **SECOND-MOMENT-SUPPLY-A1** (conservative), **GEOMETRIC-RANK-B1** (representation),
**HARDNESS-MAGNIFICATION-C1** (high-risk). Each has a contract + first command in §6. The three
barrier candidates D1/D2/D3 are, as in every recent run, **higher expected value** than the
winners, because each threshold *closes* a gate the winners only *measure*.

---

## 1. Required input review — inventory

Read in full or by targeted extraction this run:

1. `/Volumes/Volume/git/autolab/research_ledger.md` (2478 lines; committed frontier `P1486` /
   `ECFG-P1470`; `ECFG-RT-1472`, `ECFG-RT-1476` gate rows re-read verbatim).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` (720 long lines,
   ~797 KB; IC frontier `P1509–P1513`; `P1512` linear-Chow atomizer + `P1513` shared-common-norm
   rows extracted).
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` (389 lines;
   PO-transfer-001..006 closeouts, all NEGATIVE/MODEL-BOUND; next open action = cyclic-cover
   `X_d: z^d = h(P)` label-conditioned factorization, not credited as crossing).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json`
   (10 entries: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013; FHJRV 2014 symmetrized;
   Kousidis–Wiemers 2015 first-fall; Karabina 2015; Amadori–Pintore–Sala 2017; McGuire–Mueller
   2017 Gröbner-free; Trimoska–Ionica–Dequen 2020 SAT).
5. All 20 prior `research/idea_generation_2026071*.md` reports (anti-dup catalogue, ~60 lanes).

**Machine-readable coverage.** Rather than re-sample recent entries, this run treated the anti-dup
catalogue (memory node `ecdlp-idea-generation-reports`) as the canonical inventory and
grep-verified every proposed family against it. Entry-family coverage confirmed present in the
ledgers/reports and therefore **excluded** as duplicates:

| Fingerprint slot | Families already consumed (excluded) |
|---|---|
| mechanism | Semaev/summation, Weil-descent/GHS, cover/Tian, split-Jacobian/bielliptic (PO-003..006), isogeny-transfer, index-calculus |
| representation | x-line, theta/Kummer, abelian-surface, trace-zero, Prym, Jacobian, tensor-net, quiver/path-algebra, GKZ D-module, immanant, nc-rank, Yangian R-matrix, positive-geometry, perverse-sheaf, FI-module |
| exploited structure | order/trace invariants, torsion, endomorphism/Frobenius, CM, large-prime graph, 2-core, group-law special-form (Elekes–Szabó) |
| factor base | rational-map, cover, symmetrized, large-prime, character-bucket, source-selector |
| relation shape | 5-pt Semaev, ternary cofiber, marked-resultant, common-norm, product-circuit |
| relation-generation | Gröbner, SAT, crossbred, resultant, sparse-interp (Prony), list-decoding, elliptic-net |
| compression | slice/border/analytic rank, apolarity/Waring, syzygy, Segre-excess, shifted-partials |
| linear-algebra object | sparse Krylov, block-Hankel, disjoint-dependency circuit, matroid-union |
| target-descent | serial-S3 backward-3-sum, descent-exponent tree |
| cost bottleneck | relation/membership generation (binding), sparse-LA `n^(2/5)` (NOT binding) |
| supply-side δ meters | Delsarte-LP, Shearer, container, VC, large-sieve, singular-series, hereditary-discrepancy, anti-concentration, ergodic recurrence, Lang-Weil, energy |
| query-side α LBs | approx-degree, sign-rank, lifting, NOF, VC, LDC, cell-probe, round-elimination, evasiveness, sensitivity/Huang, resolution-width, kernelization, minimax/Fano, quantum-adversary |
| outcome | all NEGATIVE / MODEL-BOUND / scoped; barriers converge δ≤1/4, α≥3/2 |

**Reviewed:** 20 reports + 2 ledgers + transfer doc + 10-entry bibliography. ID families covered:
`P/ECFG-P` (main, through `P1486`/`ECFG-P1470`), `P1509–P1513` (IC-state), `RT-1472`/`RT-1476`
(gates), `RT-1485` (closed Kummer-companion negative), report-proposed `ECFG-P1550..P1693`
(uncommitted). This run proposes **ECFG-P1694..P1705**.

**Grep-verified 0-hit** (this run's imports; searched across all 20 reports + both ledgers):
`Janson`, `FKG`, `Harris inequality`, `Paley-Zygmund`, `second moment`, `Talagrand`,
`log-Sobolev`, `Nechiporuk`, `Karchmer`, `geometric rank`, `Hochschild`, `cyclic homology`,
`hardness magnification`, `magnification`, `gate elimination`, `catalytic` — all **0 hits**.

---

## 2. Novelty standard applied

"New" = mechanism-new, judged by the semantic fingerprint

```
F(C) = (algebraic object, available public operations, hidden structure exploited,
        information discarded, information retained, relation-generation primitive,
        compression primitive, rank mechanism, descent mechanism, dominant cost exponent)
```

A candidate is a duplicate if an existing entry has the same essential fingerprint even under
different terminology. Below, every candidate lists its five nearest ledger entries and the exact
mathematical distinction (not a wording distinction).

**Known closed / control-only territory** (re-affirmed; not re-proposed): same-field isogeny
invariants; scalar Weil pullback; explicit two-large-prime advice graphs; ordinary joint
factor/large-prime Krylov; pair-residual character buckets; non-invariant CM decks; materialized
serial-S3 backward states; dense composed resultants; source selectors without an honest hit
generator; relation validity without ECDLP recovery; preprocessing wins whose offline/memory/advice/
target-count loses to rho. Additionally closed by name in prior runs and **excluded**:
crystalline/Cartier-Manin/Kedlaya (batch2 D2); Kloosterman/character-sum bias (batch2 C3);
"poly-time sampler certifies δ>1/4" role (batch5 MATUNION-A2, batch11 LORENTZIAN-C2);
mixing-time/hypercontractivity sampler enrichment (batch14 D2, batch16 C1).

---

## 3. The twelve candidates

### Group A — conservative extensions of known work

---

## Candidate: SECOND-MOMENT-SUPPLY-A1

### One-sentence mechanism
Exploit the **variance and pairwise-dependency structure** `Delta` of the enriched-pair count
`N` on the two-large-prime graph to reduce the uncertainty in the supply exponent `delta` of
subproblem RT-1472 below the mean-field guess, testing whether the honest large-prime multiset
can carry `delta > 1/4` or is forced to concentrate at `delta = 1/4`.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (import), POSSIBLY NOVEL as an RT-1472 meter after documented search.

### Semantic fingerprint
- algebraic object: two-large-prime enrichment graph on `L = q^(1/5)` prime buckets, edge set =
  potential pair-relations;
- public operations: sample rows, read shared-large-prime incidences;
- hidden structure exploited: pairwise dependency between edges that share a large prime;
- information discarded: individual relation coefficients;
- information retained: the count `N` of enriched pairs and its second moment `E[N^2]`;
- relation-generation primitive: honest FFE/summation preflight (unchanged);
- compression primitive: none — this is a supply meter;
- rank mechanism: `rank <= #independent enriched pairs`;
- descent mechanism: inherited (not the object of this candidate);
- dominant cost exponent: measured `delta = log_q E[N] + correction from Var(N)`.

### Nearest ledger entries
1. **batch18 HALASZ-SMALLBALL-A1** (anti-concentration of additive images): both probe the
   enrichment supply; distinction — Halász bounds the *additive-image concentration* of a signed
   sum, A1 bounds the *variance of a count* via `Delta = sum over edge-pairs sharing a prime`.
   Different functional (small-ball spread vs count variance).
2. **batch14 LARGE-SIEVE-SUPPLY-A1** (L² dual inequality over the modulus family): both are
   L²-flavored; distinction — large sieve bounds `sum |S(a)|^2` over a well-spaced set; A1 bounds
   `E[N^2] - E[N]^2` over the dependency graph, a Janson/Chebyshev object, not a dual character sum.
3. **batch8 SHEARER-D3** (submodular entropy supply ceiling): Shearer bounds a joint entropy; A1
   bounds a variance. Entropy ≠ second moment.
4. **batch4 CORRELATED-PEEL-A3** (Wormald 2-core threshold of the dependent sum-graph): both use
   the dependent graph; distinction — Wormald tracks a differential-equation trajectory of the core
   size; A1 computes a static `Var(N)/E[N]^2` ratio and its `Delta` decomposition. Trajectory vs
   moment.
5. **batch18 STEIN-CHEN-POISSON-A2** (Poisson approximation of b2-clustering): Stein–Chen is a
   *first-moment / total-variation* mean-field bound; A1 is an explicit *second-moment* bound.
   Poisson-approx vs variance.

### Nearest literature
- Alon–Spencer, *The Probabilistic Method* (second-moment method; Janson's inequality; Chapters
  4, 8). Claim: for a sum of indicator variables, `P(N=0) <= exp(-E[N]^2 / (E[N] + 2·Delta))` and
  `Var(N) = E[N] + 2·Delta - (dependency corrections)`, with `Delta = sum_{i~j} E[X_i X_j]` over
  dependent pairs.
- Janson, Łuczak, Ruciński, *Random Graphs* (subgraph-count concentration). Assumption: identifies
  the exact regime where `Delta = o(E[N]^2)` gives concentration.
- Gap: none of these is instantiated on the *elliptic* large-prime incidence structure; the missing
  step is proving `Delta = o(E[N]^2)` (or not) for an honest Semaev large-prime multiset.

### Target family
Ordinary prime-field curves `E/F_p`, prime group order `n`, `p` prime, `j(E) != 0, 1728`, no CM by
small discriminant, no anomalous/MOV structure; `B = n^(1/5)` large-prime bound. Excluded: binary/
extension fields, supersingular, special-CM.

### Full algorithmic path
1. **Factor-base construction:** standard `L = q^(1/5)` bucketed factor base + large-prime bound
   `B`.
2. **Relation generation:** honest FFE/summation preflight producing one-large-prime rows; record,
   per row, which large prime(s) it touches (the incidence).
3. **Witness extraction/verification:** each enriched pair is an actual matched cancellation
   verified independently (claim tier: verified relation, not ECDLP recovery).
4. **Relation probability:** `E[N] = Theta(L^2 · p_pair)` where `p_pair` is the two-row shared-prime
   probability; `delta` read from `log_q E[N]`.
5. **Matrix dimensions/density/rank:** `Theta(L)` rows, sparse; rank `<= #independent enriched pairs`.
6. **Factor-log calibration:** unchanged (`q^(2/5)` sparse LA, not binding).
7. **Descent:** inherited.
8. **Offline/online separation:** the moment computation is offline/analytic; no extra online cost.
9. **Memory/parallelism:** incidence lists `Theta(L)`; embarrassingly parallel sampling.

### Cost model
Supply exponent `delta` compared to the RT-1472 threshold `1/4`. Total attack exponent stays
`max(2ell, 1-ell, 1+1/5-2ell)`; a crossing needs `delta > 1/4`, i.e. `Var(N)` small **and** `E[N]`
carrying strictly more than `L^(1/2)` excess pairs. Against rho `n^(1/2)`: crossing iff the min over
`ell` drops below `1/2`, which requires `delta > 1/4`. Setup/failed-attempt/verification costs are
`Theta(L)` and do not change the exponent.

### Why existing negative results do not already kill it
The prior supply meters bound counts (Lang-Weil), entropy (Shearer), averages (large-sieve), or
additive spread (Halász). None computes the **variance** of the enriched-pair count via its
dependency graph. The new operation is the explicit `Delta`-decomposition
`Var(N) = E[N] + 2·Delta - E[N]^2` restricted to edge-pairs sharing a large prime — a second-moment
object no prior meter evaluated.

### Likely fatal obstruction
Near-certain: the honest large-prime multiset is **Sidon-like / GAP-free** (each large prime is hit
by `O(1)` rows in the relevant regime), so `Delta = o(E[N]^2)`, `N` concentrates at its mean, and the
mean itself is the maximal-doubling value forcing `delta -> 1/4`. This is the **same maximal-doubling
kill** that closed batch18 HALASZ-A1, batch5 MATUNION, batch11 LORENTZIAN. In that case A1 does not
cross — it *promotes to the barrier* D1.

### Minimal falsifying experiment
Toy sizes `q in {2^16, 2^20, 2^24}` (three sizes); seeds `20260719..20260723` (five randomized
seeds); ordinary prime-order controls; **positive control** = a synthetic large-prime multiset with
planted heavy collisions (`Delta = Theta(E^2)`) that *should* show `delta > 1/4`; **negative control**
= an honest Sidon-like multiset that should show concentration at `1/4`. Measure `E[N]`, `Var(N)`,
`Delta`, and the fitted `delta`.

### Quantitative promotion gate
Fit `delta(q)` across the three sizes. **Promote** only if the honest (negative-control) multiset
yields `delta >= 1/4 + c` for `c >= 0.03` with the trend *increasing* in `q` (a real excess-supply
exponent). Correctness of the count is **not** the gate. If honest `delta -> 1/4` from below/at, the
candidate converts to barrier D1.

### Proof track
Theorem to establish: for the honest elliptic large-prime incidence measure, `Delta = o(E[N]^2)`
(equivalently the incidence graph is a.a.s. locally tree-like), whence Chebyshev gives concentration
and `delta = 1/4` exactly. (This *proves the barrier*, i.e. the negative.)

### Disproof track
Exhibit an honest (non-planted) toy family with `Delta = Theta(E[N]^2)` and measured `delta > 1/4`
stable across sizes — this would keep the crossing hope alive and refute the barrier.

### Reproduction artifact
- contract: `research/idea_generation_20260719_batch13.md` §6.1
- implementation: `experiments/ecdlp_supply/second_moment_enrichment_variance.sage`
- result JSON: `experiments/ecdlp_supply/second_moment_enrichment_variance_result.json`
- audit: `experiments/ecdlp_supply/second_moment_enrichment_variance_verify.sage`
- ledger ID: `ECFG-P1694`

---

## Candidate: JANSON-LOWERTAIL-A2

### One-sentence mechanism
Exploit Janson's inequality to bound the **lower tail** `P(N <= (1-e)E[N])` of the enriched-pair
count, certifying whether under-supply is exponentially rare (so the *typical* run achieves the mean
supply that A1 measures) — the complementary tail control A1 does not provide.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (import); INCOMPLETE-risk (see stage 7).

### Semantic fingerprint
As A1 but the retained object is `P(N <= (1-e)E[N])` bounded by `exp(-e^2 E[N]^2 / (2(E[N]+Delta)))`;
rank/descent inherited; dominant exponent = the tail-decay rate, not directly `delta`.

### Nearest ledger entries
1. **A1** (this run): A2 is the *tail* companion of A1's *mean/variance*; distinction — Janson's
   inequality is a specific exponential lower-tail bound, not the Chebyshev second-moment ratio.
2. **batch18 STEIN-CHEN-POISSON-A2**: Stein–Chen gives a TV distance to Poisson; Janson gives a
   one-sided exponential tail. Different inequalities, different constants.
3. **batch4 CORRELATED-PEEL-A3**: DE-method trajectory vs static exponential tail.
4. **batch14 LARGE-SIEVE-SUPPLY-A1**: dual L² sum vs union-of-events lower tail.
5. **batch9 CONTAINER-CEILING-A3**: container method bounds independent-set counts (upper); Janson
   bounds a lower tail. Opposite direction.

### Nearest literature
Janson (1990); Alon–Spencer Ch. 8. Claim: `P(N=0) <= exp(-E[N] + Delta)` and the extended lower-tail
form. Gap: converting a *probability* bound into a *supply exponent* requires a translation lemma
(the INCOMPLETE stage).

### Target family
As A1.

### Full algorithmic path
Stages 1–6 as A1. **Stage 7 (descent) — INCOMPLETE:** A2 bounds a probability, not an exponent; the
map "lower-tail rate → guaranteed `delta`" is not constructed here. Labelled INCOMPLETE and demoted
(feeds D1, does not stand alone).

### Cost model / obstruction / falsification
Same regime as A1. Likely fatal obstruction: if `Delta` is small the Janson bound is essentially the
Poisson/independent bound (mean-field), so A2 reproduces the `delta = 1/4` conclusion. Feeds D1.

### Reproduction artifact
- ledger ID: `ECFG-P1695`; shares the A1 harness with a lower-tail estimator. **Status: INCOMPLETE,
  supporting only.**

---

## Candidate: NECHIPORUK-FORMULA-A3

### One-sentence mechanism
Exploit the **Nechiporuk distinct-subfunction bound** on a variable partition of the five membership
coordinates to lower-bound the *formula size* of any m=5 implicit-membership backend, testing whether
the query exponent `alpha` is forced `>= 3/2` in the general-formula model.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (import); POSSIBLY NOVEL as an RT-1476 meter.

### Semantic fingerprint
- algebraic object: the m=5 membership predicate `f(x_1..x_5)` as a formula over `F_q`;
- public operations: evaluate `f` and its restrictions;
- hidden structure exploited: the number of distinct subfunctions induced on a coordinate block when
  the others are fixed;
- discarded: circuit sharing across blocks;
- retained: `sum over blocks of log_2(#distinct subfunctions)`;
- relation-generation primitive: membership backend (unchanged);
- compression primitive: none — a lower-bound meter;
- rank mechanism: n/a;
- descent mechanism: same backend for descent (RT-1476 assumption);
- dominant cost exponent: `alpha = log_L(formula size lower bound)`.

### Nearest ledger entries
1. **batch10 SHIFTED-PARTIALS-A1** (depth-4 shifted-partial dimension): both lower-bound circuit
   size; distinction — shifted-partials is an *algebraic depth-4* measure via the partial-derivative
   matrix; Nechiporuk is a *general-formula* measure via subfunction counting on a variable partition.
   Different model, different combinatorial object.
2. **batch10 NISAN-NC-RANK-A2** (nc-ABP width = Hankel rank): Nisan bounds *non-commutative ABP*
   width by coefficient-matrix rank; Nechiporuk bounds *formula* size by subfunction count. ABP ≠
   formula; rank ≠ subfunction count.
3. **batch11 RAZ-MULTILINEAR-D3** (multilinear-formula partial-derivative rank): Raz uses a random
   partition and partial-derivative matrix rank; Nechiporuk uses a *fixed* partition and *subfunction
   multiplicity*. Rank vs count.
4. **batch7 LIFTING-D1** (query→communication lifting): lifting transfers a query LB to communication;
   Nechiporuk is a direct formula-size bound with no lifting gadget. Different technology.
5. **batch13 SENSITIVITY-BLOCK-A1** (Huang `s`/`bs`/`C`/`D` chain): sensitivity is a query/decision-tree
   measure; Nechiporuk is a formula-size measure. Decision tree ≠ formula.

### Nearest literature
Nechiporuk (1966); Jukna, *Boolean Function Complexity*, Ch. 6. Claim: formula size
`L(f) >= (1/4) · sum_i log_2 s_i` where `s_i` = number of distinct subfunctions on block `i`.
Karchmer–Wigderson (1990): formula depth = communication complexity of the associated relation.
Gap: Nechiporuk's method is capped at `~ N^2/log N` for `N` input bits, and the membership backend is
a **field** circuit (arithmetic over `F_q`), not a Boolean formula — the bit↔field-op translation may
land the exponent *below* `3/2` (the same failure mode as batch13 SENSITIVITY-DEGREE-D1).

### Target family
As RT-1476: `E/F_p` ordinary prime-order, `m=5`, `L = q^(1/(m+1-alpha))`.

### Full algorithmic path
1–3 (factor base / relation / witness) inherited from the m=5 IC skeleton. 4 relation probability
`min(1, L^5/q)`. 5 matrix `Theta(L)` rows sparse `q^(2/5)`. 6 calibration inherited. 7 descent = same
backend. 8 the Nechiporuk bound is offline/analytic. 9 negligible. The candidate is a **meter on the
backend's formula size**, not a new backend.

### Cost model
`alpha >= log_L(Nechiporuk bound)`. RT-1476 needs `alpha < 3/2`. If Nechiporuk forces
`alpha >= 3/2 + c`, closes RT-1476 for the formula class (→ barrier D2). If it maxes below `3/2`,
inconclusive.

### Why existing negatives do not kill it
No prior α-LB used **subfunction counting on a variable partition**. Sensitivity/Huang counts local
influences; shifted-partials counts a derivative-space dimension; lifting transfers a query bound.
Subfunction multiplicity on a coordinate block is a distinct combinatorial object.

### Likely fatal obstruction
Near-certain: Nechiporuk's `N^2/log N` ceiling, translated through `N = O(log q)` membership-input
field-elements, yields an `alpha` bound at or below `3/2` — boundary, not strict closure. Also
symmetry of the membership predicate reduces the distinct-subfunction count. Feeds D2.

### Minimal falsifying / promotion / proof / disproof
Three toy `m=5` field sizes, five seeds, positive control = a predicate with maximal subfunction
diversity (should show large `alpha`), negative control = a symmetric predicate (should collapse).
Promote iff measured `alpha >= 3/2 + 0.05` trending up. Proof track: Nechiporuk lower bound instantiated
on the exact symmetrized Semaev membership formula. Disproof: a formula with `< L^(3/2)` size that
decides membership.

### Reproduction artifact
- ledger ID: `ECFG-P1696`;
  `experiments/ecdlp_membership/nechiporuk_subfunction_count.sage` (+ `_result.json`, `_verify.sage`).
  **Status: supporting; INCOMPLETE-risk on the field-op translation.**

---

### Group B — genuine representation changes

---

## Candidate: GEOMETRIC-RANK-B1

### One-sentence mechanism
Exploit the **geometric rank** `GR(T) = codim{ (x_1,..,x_4) : T(x_1,..,x_4,·)=0 }` of the symmetrized
Semaev five-tensor `T` — a codimension invariant with `subrank <= GR <= slice rank` that is **not** the
commutative-determinant degree `deg(det M) <= dim` — to lower-bound any atomizing decomposition of the
relation tensor, directly attacking the surviving P1512-R1 **nonlinear-circuit exception**.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (documented search: geometric rank has no ECDLP prior art; the KMZ paper is combinatorics/
matrix-multiplication).

### Semantic fingerprint
- algebraic object: symmetrized 5-linear Semaev tensor `T` over `\bar{F_q}`;
- public operations: contract `T` against slices, test vanishing locus;
- hidden structure exploited: the **codimension of the slice-degeneracy variety** of `T`;
- discarded: coordinate presentation (GR is basis-independent, hence survives the change of variables
  the linear-Chow atomizer used);
- retained: `GR(T)`;
- relation-generation primitive: unchanged;
- compression primitive: any decomposition into `<= k` atoms forces `GR(T) <= f(k)`;
- rank mechanism: `partition rank >= subrank`-side control via `GR`;
- descent mechanism: inherited;
- dominant cost exponent: number of independent atoms `>= GR(T)`.

### Nearest ledger entries
1. **batch5 ASYMPSPEC-D1** (Strassen asymptotic spectrum / border rank): both are tensor-rank
   technologies; distinction — asymptotic spectrum studies the *ordered semiring of rank under tensor
   powers*; GR is a *single-tensor codimension* invariant. Spectrum ≠ codimension of a degeneracy
   locus.
2. **batch11 ANALYTIC-RANK-BIAS-B1** (`-log bias` of the tensor): GR relates to analytic rank
   *asymptotically* but is defined geometrically (codim of a variety) not analytically (Fourier bias).
   Over finite `F_q` they can differ by constants; the geometric definition is what evades
   `deg(det M)`.
3. **batch4 SLICE-RANK-1-D2** (CLP/slice-rank vacuous in rank-1 cyclic `E(F_p)`): slice rank was the
   *upper* bound; `GR <= slice rank`, so GR is a **tighter** lower-side handle and is *not* rank-1
   vacuous because it measures a codimension, not a single slice.
4. **batch13 SEGRE-EXCESS-B1** (Fulton excess normal-bundle Segre class): both are algebraic-geometry
   invariants of the relation locus; distinction — Segre-excess measures the *excess intersection* of
   two cycles; GR measures the *codimension of the total slice-degeneracy locus*. Different varieties.
5. **P1512-R1** (scalar-linear Chow atomizer, `Omega(r^5)` via `deg(det M) <= dim`): P1512 closed the
   *linear* class by a determinant-degree argument; GR is precisely a functional **outside**
   `deg(det M)`, so it is the licensed probe of the surviving nonlinear-circuit exception.

### Nearest literature
- Kopparty, Moshkovitz, Zuiddam, *Geometric rank of tensors and subrank of matrix multiplication*
  (arXiv:2002.09472, ITCS 2020 / journal). Claim: `GR(T) = codim` of the slice-degeneracy locus;
  `subrank(T) <= GR(T) <= slice rank(T)`; `GR ~ analytic rank` asymptotically; used to match Strassen's
  matrix-multiplication subrank lower bound.
- Tao (slice rank), Naslund (partition rank, `= slice rank` for `k=3`, `<` for `k>3`), Gowers–Wolf /
  Lovett (analytic rank).
- Gap: KMZ compute GR for matrix-multiplication and generic tensors, **not** for the elliptic
  symmetrized-Semaev tensor. The missing lemma is the exact `GR(T_Semaev)` as a function of `r`.

### Target family
`E/F_p` ordinary prime-order; symmetrized 5-point Semaev relation; over the algebraic closure for the
codimension computation, specialized to `F_q` for the atom count. Excluded: degenerate `j`, CM,
supersingular.

### Full algorithmic path
1. Factor base: `L = q^(1/5)` symmetrized. 2. Relation generation: symmetrized Semaev, `Theta(L)` rows.
3. Witness: verified relations (claim tier). 4. Relation probability inherited. 5. Matrix: any atomizer
producing `k` independent atoms is constrained by `GR(T) <= h(k)`; `rank <= #atoms`. 6. Calibration
inherited. 7. Descent inherited. 8. GR computation is offline/algebraic. 9. Memory of the codimension
computation is `poly(r)` symbolic.

### Cost model
If `GR(T_Semaev) = Theta(r)`, then any decomposition needs `Theta(r)` atoms each of the P1510 leaf
degree, reproducing the `r^5` leaf floor (`P1511-R2`), i.e. `alpha` at the closed value. A crossing
needs `GR` to *drop* to `o(r)` while atoms stay cheap — geometrically, the slice-degeneracy locus would
have to have **large codimension deficit** specific to the elliptic structure. Compare to rho: only a
`GR`-certified sub-`r^5` atomizer would matter, and none is known.

### Why existing negatives do not kill it
P1512-R1's `deg(det M) <= dim` bounds the *ordinary/commutative* atomizer class. GR is basis-free and
not a determinant degree, so P1512-R1 does not constrain it — GR is the sharpest licensed probe of the
nonlinear-circuit exception since batch11 nc-rank, batch12 immanant, batch13 Segre-excess, batch18
Yangian, because those either reduce to `deg(det)` (immanant via Bürgisser dichotomy) or need a special
algebraic structure (YBE, free-fermionic) the elliptic relation lacks.

### Likely fatal obstruction
Near-certain: the Semaev tensor is "generic enough" that `GR(T) = Theta(r)` (the slice-degeneracy locus
has the expected codimension), so GR only certifies `Theta(r)` atoms and, combined with per-atom degree,
**reproduces the `r^5` floor** — closing the geometric-rank representation lane by name rather than
crossing. Second obstruction: over `F_q` (not closed) the codimension can drop, but the drop is a
constant/`log` effect (KMZ: `GR ~ analytic rank` up to constants), not an exponent change.

### Minimal falsifying experiment
Compute `GR` of the symmetrized Semaev tensor for `r in {3,4,5}` factor-base widths over three toy
primes, five seeds; **positive control** = a low-geometric-rank structured tensor (e.g. a Coppersmith–
Winograd-type tensor) that *should* atomize cheaply; **negative control** = a generic 5-tensor of the
same format (should give `GR = Theta(r)`); ordinary prime-order EC controls throughout.

### Quantitative promotion gate
Fit `GR(T_Semaev)` vs `r`. **Promote** only if `GR = o(r)` (sublinear) with a trend implying an
atomizer exponent `< r^5` translating to `alpha < 3/2`. `GR = Theta(r)` → barrier/lane-closure.
Correctness of the codimension computation is **not** the gate.

### Proof track
Theorem: `GR(T_Semaev) = Theta(r)` (equivalently the slice-degeneracy locus of the symmetrized Semaev
tensor has full expected codimension), which *proves* the atomizer floor and closes the lane.

### Disproof track
Exhibit an elliptic factor-base family where `GR(T_Semaev) = o(r)` with a matching cheap atomizer —
this would keep the nonlinear-exception crossing hope alive.

### Reproduction artifact
- contract: §6.2;
  `experiments/ecdlp_membership/geometric_rank_semaev_tensor.sage` (+ `_result.json`, `_verify.sage`);
  ledger ID `ECFG-P1697`.

---

## Candidate: HOCHSCHILD-TRACE-B2

### One-sentence mechanism
Exploit the **Hochschild / cyclic homology** `HH_*` of the path algebra of the summation-relation
quiver as a deformation/trace invariant of the atomizer, testing whether a nonzero higher `HH` class
obstructs cheap atomization independently of `deg(det M)`.

### Status
OPEN

### Novelty classification
LEDGER-NEW (import); INCOMPLETE-risk.

### Semantic fingerprint
- object: path algebra `A = k Q` of the summation quiver `Q`;
- retained: `HH_i(A)`, `HC_i(A)` (trace/deformation classes);
- discarded: the representation dimension itself (that was batch3 QUIV);
- rank mechanism: obstruction to flat deformation of the atomizer;
- dominant exponent: n/a unless a nonzero class forces `Omega(r^c)` atoms.

### Nearest ledger entries
1. **batch3 QUIV-C1** (quiver/path-algebra representation): QUIV used the *representation*; B2 uses the
   *homology of the algebra*. Rep dimension ≠ Hochschild class.
2. **batch11 NONCOMMUTATIVE-RANK-B2** (free-skew-field inner rank): nc-rank is a rank of a matrix over
   the free skew field; `HH_*` is a homological invariant of an algebra. Different objects.
3. **batch18 YANGIAN-RMATRIX-B1**: Yangian used a spectral R-matrix bond dimension; `HH_*` is
   homological, no spectral parameter.
4. **batch13 HECKE-TL-B3**: Temperley–Lieb planar-diagram contraction; `HH_*` is not diagrammatic.
5. **batch4 SYZYGY-REGULARITY-B2**: syzygy uses the minimal free resolution / Betti table (a *commutative*
   homological invariant); `HH_*` is the *non-commutative* (path-algebra) analogue. Adjacent but distinct
   (commutative Tor vs Hochschild).

### Nearest literature
Loday, *Cyclic Homology*; Weibel, *Homological Algebra* Ch. 9. Claim: for a hereditary (path) algebra,
`HH_i = 0` for `i >= 2`, and `HH_1` is controlled by the cycles of `Q`. Gap: computing `HH_*` for the
specific summation quiver.

### Full algorithmic path — INCOMPLETE
The descent path (stage 7) and the map "nonzero `HH` class → atomizer cost exponent" are not
constructed. **Labelled INCOMPLETE.**

### Likely fatal obstruction
Near-certain: the summation quiver is a **tree / acyclic** (the relation DAG has no directed cycles), so
`HH_{>=1} = 0`, the obstruction is vacuous, and B2 says nothing about the atomizer floor. **DEMOTED.**

### Reproduction artifact
- ledger ID `ECFG-P1698`. **Status: DEMOTED / INCOMPLETE, supporting only.**

---

## Candidate: CONTINUANT-ORTHPOLY-B3

### One-sentence mechanism
Exploit a **three-term (orthogonal-polynomial / continuant) recurrence** representation of the serial-S3
backward-3-sum state, seeking a non-materializing linear-recurrence encoding of the backward state that
avoids the `r^3` leaf explosion.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (to batch5 MAHLER automatic-sequence and batch8 FORMALGROUP linearization).

### Semantic fingerprint
- object: backward-3-sum state as a continuant `det` of a tridiagonal matrix / three-term recurrence;
- retained: recurrence coefficients;
- rank mechanism: continuant degree;
- dominant exponent: state period.

### Nearest ledger entries
1. **batch5 MAHLER-B1** (automatic-sequence rep of `x([k]P)`): both seek a compressed linear-state
   encoding; distinction — Mahler used base-`p` automata; B3 uses a three-term orthogonal recurrence.
2. **batch8 FORMALGROUP-B1** (Honda formal-group/Coleman log linearization): linearization vs continuant
   recurrence.
3. **batch8 CLUSTER-MUTATION-B3** (Somos-4 / cluster recurrence): Somos is a *quadratic* bilinear
   recurrence; a continuant is a *linear* three-term recurrence. Different order.
4. **batch5 POWERPROJ-A1** (transposed power projection / Bostan–Schost): both touch structured linear
   algebra; power-projection is a dual evaluation, continuant is a determinant recurrence.
5. **P1511-R2** (product-circuit `r^3` leaves): B3 tries to beat exactly the `r^3` leaf count P1511
   closed.

### Likely fatal obstruction
Near-certain: any three-term recurrence over `F_p` is **eventually periodic** with period dividing the
order of the state-transition matrix, i.e. `Omega(ord P) = Omega(n)` — reproducing BSGS, the same
periodicity kill as MAHLER / FORMALGROUP. **REJECTED** (scoped negative; retained as a periodicity
control).

### Reproduction artifact
- ledger ID `ECFG-P1699`. **Status: REJECTED (periodicity), control only.**

---

### Group C — high-risk speculative mechanisms

---

## Candidate: HARDNESS-MAGNIFICATION-C1

### One-sentence mechanism
Exploit a **hardness-magnification** theorem — a *weak* `Omega(L^(1+e))` lower bound on a sparse/
parameterized sub-instance of m=5 membership magnifies to a super-polynomial bound — turning the RT-1476
question into a dichotomy: either a fast backend exists (and a whole circuit class collapses), or
`alpha >= 3/2` follows for the sparse membership language.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (documented search: hardness magnification has no ECDLP prior art; DISTINCT by the
sparsity/magnification axis from batch10 ALGEBRAIC-NATURAL-PROOFS-D3 which was a *meta*-barrier, not a
magnification theorem).

### Semantic fingerprint
- object: the m=5 membership language as a **sparse** NP-style language (few YES instances per length);
- public operations: evaluate membership;
- hidden structure exploited: sparsity `L^5/q` of the support (random-like, few witnesses);
- discarded: the field structure of individual queries;
- retained: the magnification threshold (a circuit-size boundary);
- relation-generation primitive: backend (unchanged);
- rank/descent: inherited;
- dominant exponent: `alpha` via the magnified circuit-size floor.

### Nearest ledger entries
1. **batch10 ALGEBRAIC-NATURAL-PROOFS-D3** (Forbes–Shpilka–Volk/GKSS meta-barrier): both are meta-level;
   distinction — D3 asks whether an efficient *algebraic α-barrier can exist*; C1 imports a *magnification
   theorem* that reduces a strong bound to a weak one. Magnification ≠ natural-proofs pseudorandomness.
2. **batch17 KERNELIZATION-COMPRESSION-A1** (OR-cross-composition / instance compression): both are
   parameterized-complexity imports; distinction — kernelization *compresses the instance*; magnification
   *amplifies a weak lower bound*. Compression ≠ amplification.
3. **batch7 LIFTING-D1** (query→communication lifting): lifting transfers a bound *across models* at the
   same strength; magnification transfers *within a model* from weak to strong. Different transfer.
4. **batch6 CIRCUIT-TAU-D3** (τ-conjecture root-vs-size): τ bounds roots by circuit size; magnification
   bounds size by a sparse sub-instance bound. Different implication direction.
5. **RT-1476**: C1 is the sharpest conditional engagement with the m=5 backend since the gate opened —
   it relates `alpha` to a class collapse.

### Nearest literature
- Chen, Hirahara, Oliveira, Pich, Rajgopal, Santhanam, *Beyond Natural Proofs: Hardness Magnification and
  Locality* (arXiv:1911.08297, ITCS 2020 / JACM 2022). Claim: strong separations reduce to weak-circuit
  lower bounds for sparse problems; the **locality (localization) barrier** — existing LB techniques
  extend to circuits with small-fan-in oracle gates, exactly the regime magnification needs, so they
  cannot cross the threshold.
- Chen, Jin, Williams, *Hardness Magnification for all Sparse NP Languages* (FOCS 2019).
- Gap: no instantiation on the elliptic membership language; and the locality barrier is expected to
  block the unconditional direction.

### Target family
`E/F_p` ordinary prime-order, m=5, sparse support `L^5/q`.

### Full algorithmic path
Backend stages 1–7 inherited. The magnification argument is offline/meta. C1 does **not** build a new
backend — it asks whether the *existence* of a sub-`L^(3/2)` backend is consistent with the locality
barrier. If the barrier blocks the unconditional bound, C1 yields only a **conditional** `alpha >= 3/2`
(under a standard non-collapse assumption), feeding D3.

### Cost model
`alpha >= 3/2` for the sparse membership language *if* a magnification theorem applies and the weak
sub-instance bound is provable outside the locality barrier. Against rho: a conditional closure of
RT-1476, not a crossing.

### Why existing negatives do not kill it
No prior candidate used magnification. The natural-proofs meta-barrier (batch10 D3) is about the
non-existence of efficient *distinguishers*; magnification is a *reduction* between lower-bound
strengths. Distinct mechanism.

### Likely fatal obstruction
Near-certain **self-defeating**: the magnification threshold sits exactly where the **locality barrier**
(Chen et al.) says current LB techniques cannot reach — the same wall as algebraic natural proofs
(batch10 D3). So C1 yields at most a *conditional* barrier, no unconditional `alpha` bound, and no
crossing. Feeds D3.

### Minimal falsifying experiment
Not a wet experiment — a **proof-obligation probe**: attempt to instantiate a Chen–Jin–Williams-style
magnification statement for the sparse m=5 membership language and check whether the required weak bound
is oracle-robust (locality-barrier test). Positive control = a sparse language with a known magnification
theorem; negative control = a dense language (magnification inapplicable). Toy verification that the
sparsity `L^5/q < 1` regime holds for `m=5, ell=1/5`.

### Quantitative promotion gate
Promote to a *conditional* barrier only if the magnification statement is instantiated **and** the weak
sub-instance bound is provably outside the locality barrier (oracle-non-robust). Otherwise → D3
diagnostic. No crossing gate — this candidate cannot itself cross rho.

### Proof track
Theorem: a hardness-magnification statement for the sparse m=5 membership language + an oracle-non-robust
weak lower bound ⇒ unconditional `alpha >= 3/2`.

### Disproof track
Show the required weak bound is oracle-robust (extends to small-fan-in-oracle circuits) ⇒ locality
barrier blocks it ⇒ magnification arm is vacuous for RT-1476.

### Reproduction artifact
- contract: §6.3;
  `experiments/ecdlp_membership/magnification_locality_probe.sage` (sparsity check) +
  `research/magnification_locality_proof_obligation.md`; ledger ID `ECFG-P1700`.

---

## Candidate: PALEY-ZYGMUND-ENRICH-C2

### One-sentence mechanism
Exploit the **Paley–Zygmund lower bound** `P(N >= theta·E[N]) >= (1-theta)^2 E[N]^2 / E[N^2]` to seek
*upper-tail* enrichment configurations with local supply `delta > 1/4` even when the mean supply is
`1/4`, attempting a crossing via rare high-supply events rather than typical supply.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (import); genuine crossing attempt (not a barrier).

### Semantic fingerprint
As A1 but retaining the **upper tail** `P(N >= theta E[N])` and asking whether a resampled high-supply
graph realizes `delta > 1/4`.

### Nearest ledger entries
1. **A1** (this run): A1 measures the mean/variance; C2 exploits the *upper tail* to *try to cross*.
   Same object, opposite use (barrier-feed vs crossing attempt).
2. **batch18 HALASZ-SMALLBALL-A1**: anti-concentration is a *spread* statement; Paley–Zygmund is a
   *second-moment lower tail*. Different inequality.
3. **batch9 METHOD-OF-MULTIPLICITIES-C1**: both are genuine crossing attempts with an amortization kill;
   multiplicities used jet order `s`, C2 uses tail events. Different resource.
4. **batch5 MATUNION-A2**: matroid-union tried to certify `delta>1/4` by independence; C2 tries via tail
   mass. Independence vs tail.
5. **RT-1472**: C2 is a direct (rare-event) crossing attempt on the supply gate.

### Nearest literature
Paley–Zygmund (1932); Alon–Spencer Ch. 4. Claim: the second-moment lower bound on the upper tail. Gap:
the *cost* of finding a tail configuration is not addressed by the inequality.

### Target family / algorithmic path
As A1. Crucially stage 8 (offline/online): finding a `delta>1/4` tail configuration requires resampling
the large-prime structure; the number of resamples is the hidden cost.

### Cost model
Even if `P(N >= theta E[N]) = Omega(1)` for some `theta > 1`, the *typical* run that rho charges sees the
mean; realizing the tail costs `1/P(tail)` resamples. If the tail with `delta > 1/4` has probability
`exp(-L^c)`, the amortized cost **loses to rho**.

### Why existing negatives do not kill it
No prior candidate exploited the *upper tail* of the enriched-pair count as a crossing route; prior
supply candidates all argued about the mean/typical supply.

### Likely fatal obstruction
Near-certain **self-defeating on amortization**: high-supply tail configurations are exponentially rare
in the honest ensemble (concentration, cf. A1), so the resampling cost `exp(Omega(L^c))` swamps any
per-configuration gain. This is the classic tail-vs-typical amortization loss.

### Minimal falsifying / promotion / proof / disproof
Three toy sizes, five seeds; measure `P(N >= theta E[N])` and the amortized cost `(resamples)·(per-run)`.
Promote only if the amortized exponent `< 1/2`. Proof track: an efficient *sampler* that hits the
`delta>1/4` tail in `poly(L)` (not just proves it exists). Disproof: tail probability `exp(-Omega(L^c))`.

### Reproduction artifact
- ledger ID `ECFG-P1701`;
  `experiments/ecdlp_supply/paley_zygmund_tail_enrichment.sage`. **Status: high-risk, near-certain
  amortization loss.**

---

## Candidate: CATALYTIC-BACKEND-C3

### One-sentence mechanism
Exploit **catalytic computation** (Buhrman–Cleve–Koucký–Loff–Speelman) — use the already-materialized
factor-base/large-prime table as a *full but restorable* catalytic register — to run the m=5 membership
backend in sub-`L^(3/2)` *working space*, testing whether catalytic space reduces the binding query cost.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (import); DEMOTED (self-defeat on the binding axis).

### Semantic fingerprint
- object: catalytic Turing machine / register program for membership;
- retained: compute-uncompute reversible transcript over a full auxiliary register;
- rank/descent inherited;
- dominant exponent: *working space*, not query `alpha`.

### Nearest ledger entries
1. **batch16 STREAMING-SKETCH-C2** (augmented-indexing online backend): both trade space; streaming
   bounded *pass-space*, catalytic uses *full restorable space*. Different space model.
2. **batch11 PROOF-SPACE-PEBBLING-D1**: pebbling bounded proof space; catalytic *uses* full space
   constructively. Barrier vs algorithm.
3. **batch13 BORODIN-COOK-TIMESPACE-D3**: time-space tradeoff LB; catalytic is an upper-bound technique.
4. **batch17 METRIC-NN-EXPANSION-C1**: both are data-structure backends; metric-NN uses cell-probe,
   catalytic uses restorable registers.
5. **RT-1476**: C3 targets the m=5 backend space, not its query exponent.

### Nearest literature
Buhrman, Cleve, Koucký, Loff, Speelman, *Computing with a full memory* (STOC 2014). Claim: catalytic
space can compute functions (e.g. `TC^1`) not known in the same *clean* space. Gap: catalytic gains are
in **space**, and RT-1476 binds on **query count `alpha`**, not space.

### Likely fatal obstruction
Near-certain **self-defeating on the binding axis**: RT-1476's cost is the number of field-op *queries*
`L^alpha`, not working space; the catalytic register does not reduce the query count, so `alpha` is
unchanged. Space ≠ query. **DEMOTED.**

### Reproduction artifact
- ledger ID `ECFG-P1702`. **Status: DEMOTED (space≠query), control only.**

---

### Group D — negative-theory candidates (barriers / loopholes)

---

## Candidate: JANSON-CORRELATION-BARRIER-D1

### One-sentence mechanism
Over any honest **GAP-free / Sidon-like** large-prime advice, the enriched-pair count has pairwise
dependency `Delta = o(E[N]^2)`, so by the second-moment method + Janson it **concentrates** at its mean,
forcing `delta <= 1/4` unconditionally — closing RT-1472 for correlation-structured advice.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL — **first correlation-inequality barrier** in the program. DISTINCT from batch14
LARGE-SIEVE-BARRIER (L² dual), batch16 HEREDITARY-DISCREPANCY-BARRIER (Beck–Fiala), batch18
HALASZ-BARRIER (anti-concentration inverse-Littlewood-Offord), batch17 ERGODIC-SZEMEREDI-BARRIER
(Furstenberg): those bound entropy/discrepancy/additive-image/recurrence; D1 bounds **count variance
via the dependency graph**.

### Nearest literature
Janson (1990); Nguyen–Vu inverse-Littlewood-Offord (for the GAP-free structural input); Alon–Spencer.
Claim: `Delta = o(E[N]^2)` ⇒ `Var(N)/E[N]^2 -> 0` ⇒ concentration. Gap: the qualitative
`Delta = o(E[N]^2)` must be sharpened to the **quantitative 1/4-boundary lemma** (same residual as
batch17 D1 / batch18 D1).

### Cost model / why it bites
Closes RT-1472 (`delta <= 1/4`) for all advice whose large-prime incidence graph is locally tree-like
(GAP-free). Pairs A1/A2/C2. This is the **highest-EV candidate this run** (a live gate closes if the
boundary lemma is proved).

### Minimal falsifying experiment
Same harness as A1 with the negative control (honest Sidon multiset): confirm `Var(N)/E[N]^2 -> 0` and
`delta -> 1/4` across three sizes / five seeds. Disproof: an honest advice with `Delta = Theta(E[N]^2)`
and `delta > 1/4`.

### Reproduction artifact
- ledger ID `ECFG-P1703`;
  `experiments/ecdlp_supply/janson_correlation_barrier.sage` (+ proof note
  `research/janson_delta_quarter_boundary_lemma.md`).

---

## Candidate: NECHIPORUK-KW-BARRIER-D2

### One-sentence mechanism
Nechiporuk's subfunction-count bound on a partition of the five membership coordinates, combined with
Karchmer–Wigderson depth↔communication, forces formula size `Omega(L^(3/2+))` / depth `Omega(log)`,
closing RT-1476's `alpha >= 3/2` in the **general-formula / bounded-depth** model.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL — **first formula-size barrier** in the program. DISTINCT from batch10 SHIFTED-PARTIALS /
DEPTH-REDUCTION-CHASM (algebraic depth-4), batch11 RAZ-MULTILINEAR (random-partition rank), batch7
LIFTING (query→communication), batch13 SENSITIVITY-DEGREE (decision-tree).

### Nearest literature
Nechiporuk (1966); Karchmer–Wigderson (1990); Jukna Ch. 6. Claim: `L(f) >= (1/4) sum_i log_2 s_i`; depth
= relation communication. Gap: the **field-op vs Boolean-formula** translation — the membership backend
is arithmetic over `F_q`, and Nechiporuk's `N^2/log N` ceiling may translate to `alpha` at or below
`3/2`; the nonlinear-circuit exception (P1512-R1) may evade the fixed-partition assumption.

### Cost model / why it bites
Closes RT-1476 for the formula/depth class if the subfunction count on the symmetrized Semaev membership
predicate is `>= L^(3/2+)`. Pairs A3/C1.

### Minimal falsifying / disproof
Same as A3; disproof = a formula of size `< L^(3/2)` deciding membership, or a subfunction count that
saturates Nechiporuk's ceiling below `3/2` after the field-op translation.

### Reproduction artifact
- ledger ID `ECFG-P1704`; `experiments/ecdlp_membership/nechiporuk_kw_barrier.sage`.

---

## Candidate: MAGNIFICATION-LOCALITY-BARRIER-D3

### One-sentence mechanism
A **meta-barrier**: the locality (localization) barrier to hardness magnification shows that the weak
lower bound C1 needs is oracle-robust, so magnification cannot yield an *unconditional* `alpha` bound —
deciding whether the entire magnification arm (C1) is viable for RT-1476.

### Status
CONJECTURE (meta-barrier / diagnostic)

### Novelty classification
POSSIBLY NOVEL — **first magnification-locality meta-barrier**. DISTINCT from batch10
ALGEBRAIC-NATURAL-PROOFS-D3 (which was about efficient algebraic distinguishers); D3 here is the
*locality* barrier specific to magnification (Chen–Hirahara–Oliveira–Pich–Rajgopal–Santhanam).

### Nearest literature
Chen et al., *Beyond Natural Proofs: Hardness Magnification and Locality* (ITCS 2020 / JACM). Claim:
existing LB techniques extend to small-fan-in-oracle circuits, exactly the magnification regime, so they
cannot cross the threshold. Gap: whether the elliptic membership weak bound is oracle-robust
(near-certain yes).

### Cost model / role
No rho gate — a **diagnostic** that prices the C1 arm. Near-certain outcome: the weak bound is
oracle-robust, the locality barrier bites, and the magnification arm yields at most a *conditional*
`alpha >= 3/2`. This closes the "just magnify a weak bound" hope by name.

### Reproduction artifact
- ledger ID `ECFG-P1705`; `research/magnification_locality_proof_obligation.md`.

---

## 4. Ranking

Scores 0–5 on: (1) distance from prior ledger mechanisms; (2) plausibility of an exact verifier;
(3) chance of changing an **exponent** (not a constant); (4) complete-path coverage; (5) falsifiability
at toy scale; (6) literature-novelty confidence; (7) **low** risk of hidden preprocessing/memory cost.

| Candidate | (1) | (2) | (3) | (4) | (5) | (6) | (7) | verdict |
|---|---|---|---|---|---|---|---|---|
| SECOND-MOMENT-SUPPLY-A1 | 4 | 5 | 2 | 5 | 5 | 4 | 5 | **conservative winner** |
| JANSON-LOWERTAIL-A2 | 4 | 4 | 1 | 2 | 4 | 4 | 5 | supporting (INCOMPLETE) |
| NECHIPORUK-FORMULA-A3 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | supporting (feeds D2) |
| GEOMETRIC-RANK-B1 | 5 | 4 | 3 | 4 | 3 | 5 | 4 | **representation winner** |
| HOCHSCHILD-TRACE-B2 | 4 | 2 | 1 | 1 | 2 | 4 | 4 | DEMOTED (INCOMPLETE) |
| CONTINUANT-ORTHPOLY-B3 | 2 | 4 | 1 | 3 | 4 | 2 | 4 | REJECTED (periodicity) |
| HARDNESS-MAGNIFICATION-C1 | 5 | 3 | 3 | 3 | 2 | 5 | 3 | **high-risk winner** |
| PALEY-ZYGMUND-ENRICH-C2 | 4 | 4 | 2 | 4 | 4 | 4 | 2 | high-risk (amortization loss) |
| CATALYTIC-BACKEND-C3 | 4 | 3 | 1 | 2 | 3 | 4 | 2 | DEMOTED (space≠query) |
| JANSON-CORRELATION-BARRIER-D1 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | **highest-EV** |
| NECHIPORUK-KW-BARRIER-D2 | 5 | 4 | 4 | 4 | 4 | 5 | 4 | high-EV |
| MAGNIFICATION-LOCALITY-BARRIER-D3 | 5 | 3 | 3 | 3 | 3 | 5 | 4 | high-EV diagnostic |

Rejection filter (novelty < 3, no descent route, no rho comparison, no precise ledger distinction):
B3 rejected (periodicity = BSGS), B2/C3 demoted (INCOMPLETE / wrong axis), A2 supporting only.

**Selected winners:** conservative **SECOND-MOMENT-SUPPLY-A1** (`ECFG-P1694`),
representation **GEOMETRIC-RANK-B1** (`ECFG-P1697`), high-risk **HARDNESS-MAGNIFICATION-C1**
(`ECFG-P1700`). The three barriers D1/D2/D3 are higher-EV than the winners and are the honest
deliverable of this run.

---

## 5. Claim discipline

Every candidate is CONJECTURE / HYPOTHESIS / OPEN. All evidence proposed is **toy-scale** and
**correctness-tier** (verified relations, not ECDLP recovery) unless a measured exponent crosses.
Correctness is never the promotion gate; a measured exponent or complete-cost trend crossing `1/2`
(δ) or `3/2` (α) is. Each candidate is scoped to the tested curves/params/solver/budget. A failed
candidate is a **scoped negative result**, not evidence that prime-field ECDLP is unimprovable.
**No break is claimed. RT-1472 and RT-1476 remain open.**

---

## 6. Winner contracts + first commands

### 6.1 SECOND-MOMENT-SUPPLY-A1 (`ECFG-P1694`)

```yaml
# experiment_contract_p1694_second_moment_enrichment_variance.yaml
id: ECFG-P1694
title: Second-moment / dependency-graph variance of the two-large-prime enriched-pair count
gate: RT-1472
hypothesis: >
  For honest large-prime advice, the enriched-pair count N on the two-large-prime graph at
  B=n^(1/5) has pairwise dependency Delta = o(E[N]^2), so N concentrates at its mean and the
  supply exponent delta -> 1/4 (no excess supply). A crossing requires an honest advice with
  Delta = Theta(E[N]^2) and measured delta > 1/4.
null_hypothesis: honest advice is GAP-free/Sidon-like => Delta=o(E^2) => delta<=1/4.
parameters:
  q_sizes: [65537, 1048583, 16777259]     # ~2^16, 2^20, 2^24 toy primes
  seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
  B: q^(1/5)
  ell_grid: [0.28, 0.30, 0.32, 0.34]
controls:
  positive: synthetic large-prime multiset with planted heavy collisions (Delta=Theta(E^2))
  negative: honest Sidon-like multiset (expected concentration, delta->1/4)
metrics: [E_N, Var_N, Delta, delta_fit, var_over_mean_sq]
promotion_gate: negative-control delta >= 0.25 + 0.03 with increasing trend in q
claim_tier: verified-relation (counts), NOT ECDLP recovery
```

First command:

```bash
sage experiments/ecdlp_supply/second_moment_enrichment_variance.sage \
  --q 65537,1048583,16777259 --seeds 20260719,20260720,20260721,20260722,20260723 \
  --B-exp 0.2 --ell 0.28,0.30,0.32,0.34 --controls sidon,planted \
  > experiments/ecdlp_supply/second_moment_enrichment_variance_result.json
```

### 6.2 GEOMETRIC-RANK-B1 (`ECFG-P1697`)

```yaml
# experiment_contract_p1697_geometric_rank_semaev.yaml
id: ECFG-P1697
title: Geometric rank of the symmetrized Semaev five-tensor as a non-deg(det) atomizer floor
gate: RT-1476 (representation arm, P1512-R1 nonlinear exception)
hypothesis: >
  GR(T_Semaev) = codim of the slice-degeneracy locus of the symmetrized Semaev 5-tensor is
  Theta(r); since subrank <= GR <= slice rank and GR is basis-free (not deg(det M)<=dim), any
  atomizer needs Theta(r) atoms, reproducing the r^5 leaf floor (P1511-R2). A crossing requires
  GR = o(r).
null_hypothesis: GR(T_Semaev)=Theta(r) (generic codimension) => no sub-r^5 atomizer.
parameters:
  r_widths: [3, 4, 5]
  q_sizes: [101, 431, 1601]                # toy ordinary prime-order curves
  seeds: [20260719, 20260720, 20260721, 20260722, 20260723]
controls:
  positive: low-geometric-rank structured tensor (e.g. CW-type) -> cheap atomizer
  negative: generic 5-tensor of same format -> GR=Theta(r)
metrics: [GR_fit_vs_r, slice_rank, atom_count, per_atom_degree]
promotion_gate: GR = o(r) with atomizer exponent implying alpha < 3/2
claim_tier: verified-relation, NOT ECDLP recovery
```

First command:

```bash
sage experiments/ecdlp_membership/geometric_rank_semaev_tensor.sage \
  --r 3,4,5 --q 101,431,1601 --seeds 20260719,20260720,20260721,20260722,20260723 \
  --controls cw_structured,generic \
  > experiments/ecdlp_membership/geometric_rank_semaev_tensor_result.json
```

### 6.3 HARDNESS-MAGNIFICATION-C1 (`ECFG-P1700`)

```yaml
# experiment_contract_p1700_magnification_locality.yaml
id: ECFG-P1700
title: Hardness-magnification dichotomy for the sparse m=5 membership language + locality-barrier probe
gate: RT-1476
hypothesis: >
  A Chen-Jin-Williams-style magnification theorem reduces a strong alpha>=3/2 lower bound for the
  sparse m=5 membership language to a weak Omega(L^{1+e}) sub-instance bound. The weak bound is
  near-certainly oracle-robust, so the locality barrier blocks the unconditional direction and only
  a conditional alpha>=3/2 follows. This candidate cannot itself cross rho.
null_hypothesis: the weak bound is oracle-robust => locality barrier => no unconditional alpha bound.
parameters:
  m: 5
  ell: 0.2                                 # support sparsity L^5/q < 1
  q_sizes: [1601, 16411, 65537]
proof_obligations:
  - instantiate a magnification statement for the sparse membership language
  - test oracle-robustness (locality barrier) of the required weak lower bound
controls:
  positive: sparse language with a known magnification theorem
  negative: dense language (magnification inapplicable)
promotion_gate: conditional-barrier only if weak bound is provably oracle-NON-robust
claim_tier: meta / proof-obligation, NOT ECDLP recovery
```

First command:

```bash
sage experiments/ecdlp_membership/magnification_locality_probe.sage \
  --m 5 --ell 0.2 --q 1601,16411,65537 --controls sparse_known,dense \
  > experiments/ecdlp_membership/magnification_locality_probe_result.json
```

---

## 7. Red-team — are the three winners disguised repetitions or cost-negative?

**Claim: all three winners are scoped negatives / lane-closures, not crossings.**

- **SECOND-MOMENT-SUPPLY-A1** is a *supply meter*, not a hit generator. Its near-certain outcome
  (`Delta = o(E[N]^2)` for honest GAP-free advice) is the **same maximal-doubling / Sidon kill** that
  closed batch18 HALASZ-A1, batch5 MATUNION-A2, batch11 LORENTZIAN-C2. It does not cross; it *promotes
  to D1*. Cost-negative risk: none charged (analytic), but it also produces no crossing. **Disguised
  repetition of the supply-ceiling family? No — the variance/`Delta` object is new — but the
  *conclusion* (`delta -> 1/4`) is the same the analytic arm already reached.**

- **GEOMETRIC-RANK-B1** attacks the *same* P1512-R1 nonlinear-circuit exception as batch11 nc-rank,
  batch12 immanant, batch13 Segre-excess, batch14 positive-geometry, batch17 perverse-sheaf, batch18
  Yangian. Its near-certain outcome (`GR = Theta(r)`) **reproduces the `r^5` floor** exactly as those
  did — it closes the geometric-rank lane by name. It is *not* a disguised repetition (GR is a genuinely
  distinct codimension invariant, `subrank<=GR<=slice rank`, not deg(det)), but it is **cost-negative in
  the near-certain branch**: `Theta(r)` atoms × per-atom degree = the closed floor.

- **HARDNESS-MAGNIFICATION-C1** cannot itself cross rho — by construction it yields at most a
  *conditional* `alpha >= 3/2`. Its near-certain self-defeat (the **locality barrier**, D3) is the same
  wall as batch10 algebraic natural proofs. It is not a disguised repetition of kernelization (batch17
  A1) — magnification amplifies rather than compresses — but it is **cost-neutral**: a meta-argument, no
  backend, no crossing.

**Convergence, not crossing.** All three winners and all three barriers point at the *same* two
conclusions the last several runs reached: `delta <= 1/4` (RT-1472) and `alpha >= 3/2` (RT-1476). The
three barriers D1/D2/D3 are higher-EV precisely because each *closes* a live gate where the winners only
*measure* it. **No break is claimed. RT-1472 and RT-1476 remain open. The mechanism space remains
saturated after 19 runs.**

---

## Sources (external literature this run)

- Kopparty, Moshkovitz, Zuiddam, *Geometric rank of tensors and subrank of matrix multiplication*,
  [arXiv:2002.09472](https://arxiv.org/abs/2002.09472).
- Chen, Hirahara, Oliveira, Pich, Rajgopal, Santhanam, *Beyond Natural Proofs: Hardness Magnification and
  Locality*, [arXiv:1911.08297](https://arxiv.org/pdf/1911.08297).
- Chen, Jin, Williams, *Hardness Magnification for all Sparse NP Languages*, FOCS 2019.
- Janson, Łuczak, Ruciński, *Random Graphs* (Janson's inequality, second-moment method); Alon–Spencer,
  *The Probabilistic Method* (Janson, Paley–Zygmund).
- Nechiporuk (1966) formula-size lower bound; Karchmer–Wigderson (1990) depth↔communication;
  Jukna, *Boolean Function Complexity*.
