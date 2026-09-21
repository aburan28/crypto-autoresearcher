# Idea Generation — ECDLP over ordinary prime fields — 2026-07-19 (batch7 / 9th report)

Research Director, empirical cryptanalysis laboratory.
Scope: generated toy curves, public benchmark instances, synthetic data only. No
wallets, production keys, accounts, or unauthorized systems.

Primary target: a non-generic algorithm whose **complete** cost beats the
single-target Pollard-rho `0.886*sqrt(n)` baseline. Toy correctness, a new
coordinate system, a relation certificate, faster preprocessing, or a solver swap
alone is not a breakthrough.

---

## 0. Required-input review and machine-readable inventory

Reviewed in full before proposing:

1. `/Volumes/Volume/git/autolab/research_ledger.md` (2478 lines; ~1244 distinct
   `P####` IDs `P001..P1486`; active `SHA1-H001..H004`; the two conditional
   rho-crossing gates `ECFG-RT-1472`, `ECFG-RT-1476`; the `PO36..PO96z`
   correspondence/Prym/Jacobian/Hom-PPAV/Kummer-Cheon transfer program; the
   low-term relation-collector and source-scheduling lanes).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md`
   (720 lines: `ECFG-001..043` functional-graph selector hypotheses, almost all
   NEGATIVE/OBSERVATION; `ECFG-NR-1500..1508`; active IC frontier
   `ECFG-P1509..P1513-R? ` implementing `IDEA-049/050/052/053/056/058/059/068/115/117`).
   Frontier fact carried forward: **P1512-R1 closes the scalar-linear Chow/Tate/
   determinant-of-cohomology atomizer at `Omega(r^5)`; only the target-specialized
   nonlinear-circuit exception survives; P1511-R2 closes the product-circuit
   factorized-semijoin route (input degree `r^3`); P1513 leaves the shared
   common-norm both-norms-cubic.**
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md`
   (`PO-transfer-001..038+` through the `PO96*` goals: same-field isogeny closed;
   twist positive control; scalar-Weil diagnostic-only; bielliptic/trielliptic
   cofiber negatives; cyclic-cover / Hom-PPAV / finite-Kummer-Cheon frontier).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json`
   (10 primary sources: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013;
   FHJRV 2014 symmetrized; Kousidis–Wiemers 2015 first-fall-degree; Karabina 2015;
   Amadori–Pintore–Sala 2017 prime-field; McGuire–Mueller 2017 Gröbner-free;
   Trimoska–Ionica–Dequen 2020 SAT).
5. Current experiment contracts (`p1509..p1513`), negative-result tables
   (`ECFG-*`, `PO96*`, `PO-transfer-*`), open-frontier questions, and the
   literature maps embedded in (1)–(3).
6. All **eight** prior idea reports (the anti-duplication corpus):
   `idea_generation_20260717{,_batch2}.md`, `idea_generation_20260718{,_batch2,
   _batch3,_batch4,_batch5,_batch6}.md`.

**Entries reviewed:** the two ledgers plus the transfer program contribute on the
order of **1,300+ distinct record IDs** (`~1244` main `P-series` + `~80`
`ECFG/NR/P15xx` + `~90` `PO-transfer/PO96` + `SHA1-H*`, `RT-*`, `F5-*`, `KN-*`,
`IDEA-*`); the eight prior reports contribute **96 catalogued candidates**
(12 × 8). **ID families covered:** `RQ-*`, `IDEA-*`, `H-*`, `EXP-*`, `RUN-*`,
`EV-*`, `DEC-*`, `TASK-*`, `KN-*`, `P-series` (`P001..P1486`, report `P1514..P1549`),
`PO-series` (`PO36..PO96z`, `PO-transfer-001..038+`), `ECFG-series`
(`ECFG-001..043`, `NR-1500..1508`, `P1509..P1513`), `RT-series` (`RT-1471/1472/1476`),
`F5-series`, `SHA1-H001..H004`.

### Condensed inventory of exploited-structure axes (unchanged from batch6, extended)

| Axis | Values already occupied across the ledgers + 8 reports |
|---|---|
| mechanism | Semaev/summation membership; point-decomposition IC; large-prime/graph enrichment; correspondence/Prym/Jacobian/Hom-PPAV/Kummer-Cheon transfer; functional-graph (ECFG) selectors; source-scheduled relation collectors; endomorphism/CM transfer; scalar-Weil/theta charts |
| representation | short-Weierstrass x-line; Kummer/theta (lvl 2,3); split genus-2/3 covers; trace-zero/Weil restriction; canonical/Serre–Tate lift; Cartier–Manin/crystalline; formal group; tensor-train/border-rank/asymptotic-spectrum; SOS/apolarity/syzygy; Mahler/automatic; Fourier–Mukai kernel; arboreal tree; matroid/graphon/graph-limit |
| exploited structure | order/trace invariants; addition-law algebra; torsion/level; isogeny-class geometry; class-group/CM; graph cycle-space/homology/matroid/coboundary; additive energy; spectral gap; Gauss–Manin/p-curvature; L-function zeros |
| relation-generation | Gröbner/resultant/SAT/crossbred; symmetrized Semaev; rational-map/cover factor base; two/three-large-prime; native cover divisors; source-scheduled row emission; Hasse-jet source section; power-projection; graph peeling |
| compression | negation; symmetrization; large-prime graphs; landmark/cycle ECFG index; border-rank/tensor-train; SOS/apolarity certificate; cosystole; low-rank graphon kernel |
| linear-algebra object | sparse GF(p) relation matrix (`n^{2/5}` at m=5, **not binding**); cycle-incidence; Hom/Fitting module; determinant-of-cohomology; block-Krylov (closed NR-1502) |
| target descent | Semaev individual-log; cover push-forward; ECFG reverse index; correspondence label return; descent-tree branching-exponent meter |
| dominant cost | membership/relation-generation query exponent (**binding**); enrichment `delta`; per-target compiler `Theta(r^3)`; MITM memory |
| barrier technology used | border-rank; slice-rank; Chow/Tate atomizer `Omega(r^5)`; class-function; arboreal-maximality; asymptotic-spectrum; SOS/Positivstellensatz degree; Lang–Weil point count; circuit-`tau`; fine-grained OV/3SUM |
| outcome | overwhelmingly NEGATIVE / SCOPED-NEGATIVE / OBSERVATION; positives are toy-correctness or amortized-many-target, never single-target complete-cost sub-rho |

### The only two live rho-crossing surfaces (unchanged since batch5)

Both are open, unrealized **conditional** theorems; every ledger "below rho" is
amortized-many-target or setup-uncharged. The sparse-LA stage (`n^{2/5}`) is **not**
binding — the **relation/membership-generation** stage is.

- **RT-1472** (`ECFG-RT-1472`): an honest 2-large-prime summation graph at
  `B=n^{1/5}` needs cycle-space enrichment `delta > 1/4` to push
  `max(2l, 1-l, 1+1/5-2l)` below `1/2`. Prior `delta` meters (3-LP homology,
  graphic-matroid cycle basis, effective resistance, matroid union,
  correlated-peeling, HDX coboundary, graphon cut-norm) never demonstrated
  `delta > 1/4`.
- **RT-1476** (`ECFG-RT-1476`): a five-term (`m=5`) implicit-membership backend
  with query exponent `alpha < 3/2`, setup `<= L^2`, random-like support, sparse
  full-rank relations. Exact optimum `l = 1/(m+1-alpha)`; `m<=3` impossible,
  `m=4` needs `alpha<1`, `m=5` needs `alpha<3/2`. Strong prior: `beta -> 3/2`
  eliminant degree; **P1512-R1 `Omega(r^5)` scalar-linear atomizer closed**; only
  the **target-specialized nonlinear-circuit exception** survives.

### Meta-finding (carried and reconfirmed for a fourth report)

The mechanism vocabulary is **saturated**: eight reports span ~48 distinct
mechanism lanes and all six task-brief search seeds (Hasse-jet, tropical/Newton-
polytope, output-sensitive incidence, transfer-operator, path-algebra, tensor-
network) are exhausted. batch7 therefore continues the batch4–batch6 discipline:
candidates drawn from lanes **outside** the ledger vocabulary, weighted toward
(a) **exact measurement/backend primitives** sharpening the two live gates and
(b) **barriers built on lower-bound technologies no prior barrier used**
(query-to-communication *lifting*, algebraic-proof-system *Nullstellensatz/PC*
degree, and *VC-dimension* shatter bounds — all structurally distinct from the
algebraic and fine-grained barriers already on file). **One task-brief seed set
that was never actually consumed — arithmetic-dynamical elliptic divisibility
sequences / elliptic nets — is investigated here (C2).** **No break is claimed.
All results are scoped negatives, exact meters, or barriers.**

---

## 1. Twelve candidates

Groups: **A** conservative extensions · **B** representation changes · **C**
high-risk speculative · **D** negative-theory / barrier. Candidates beginning
outside the ledger's dominant vocabulary are marked ⊗ (ten of twelve). Semantic
fingerprint `F(C) = (algebraic object, public operations, hidden structure, info
discarded, info retained, relation-gen primitive, compression primitive, rank
mechanism, descent mechanism, dominant cost exponent)`.

---

## Candidate: BENORTIWARI-A1 — Output-sensitive Ben-Or–Tiwari/Prony sparse-interpolation membership backend

### One-sentence mechanism
Exploit **Ben-Or–Tiwari sparse polynomial interpolation** (recover a `t`-sparse
polynomial from `2t` black-box evaluations via a Hankel/Prony generalized-
eigenvalue solve) to read the `r` valid source rows of the RT-1476 membership
object from `O(r)` evaluations of the verified P1510 per-target compiler, testing
whether output-sensitivity in the *number of relations* escapes the P1511-R2
cubic-input floor of subproblem P.

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (Ben-Or–Tiwari is textbook sparse interpolation; its use as
the RT-1476 relation reader is ledger-absent, but it is a sibling of two existing
meters and targets the same binding stage they do).

### Semantic fingerprint
(object: the P1510 marked-resultant black box as an evaluation oracle; public ops:
field eval of the compiler, Hankel-matrix solve, root-finding, Vandermonde
transpose solve; hidden structure: the output is `r`-sparse in the source-tag
monomials; info discarded: the dense `r^3` intermediate product; info retained:
the `r` nonzero source terms; relation-gen primitive: Prony recovery from
evaluations; compression primitive: Hankel low-rank of the output stream; rank
mechanism: unchanged sparse GF(p); descent: same Semaev individual-log; dominant
cost: `#evaluations × cost-per-evaluation` = `r × Theta(r^2)`).

### Nearest ledger entries
1. `POWERPROJ-A1` (batch5) — transposed power-projection meters solution *count*
   via traces; BENORTIWARI recovers the *support monomials/coefficients*, a
   different Prony/Hankel object, but both evaluate a per-target oracle `O(r)` times.
2. `PWRSUM-A3` (batch3) — power-sum composed resultant on a C-finite oracle;
   BENORTIWARI is sparse-support recovery, not a power-sum recurrence.
3. `ECFG-P1511-R2` factorized semijoin — proved the P1510 product circuit has
   input degree `r^3`; BENORTIWARI asks whether *evaluations* (never forming the
   product) dodge that floor — the exact open crack it leaves.
4. `ECFG-P1510-R1` compiler — the black box BENORTIWARI evaluates.
5. `BAURSTRASSEN-A1` (batch6) — adjoint witness opener; BENORTIWARI is
   forward-evaluation Prony recovery, orthogonal.

### Nearest literature
Ben-Or & Tiwari (1988) sparse interpolation; Prony (1795); Kaltofen–Yang–Zhi
early-termination Prony; Giesbrecht–Labahn–Lee numeric-symbolic sparse interp.
**Gap:** none bounds the *number of black-box evaluations of a Θ(r²) elliptic
compiler* needed to certify five-term membership; the coupling of Prony sample
count to the P1510 per-eval cost is uncomputed.

### Target family
Ordinary `E/F_p`, prime order `n | #E(F_p)`, non-anomalous, non-supersingular,
large embedding degree. Excluded: `j in {0,1728}`, small-disc CM, singular
reductions.

### Full algorithmic path
1. factor base `B = {P : x(P) in [0,L)}`, `L=q^{1/5}`; 2. relation gen: fix a
target row, treat the P1510 compiler as `f(z)` in a source-tag evaluation
variable, sample `f` at `2r+O(1)` geometric points, run Prony to recover the
`r`-sparse support = valid decompositions; 3. witness verify: independent EC
re-addition; 4. relation prob: inherited RT-1476 `min(1, L^m/q)`; 5. matrix
`Theta(L)` rows, density `Theta(m)`, GF(p); 6. factor-log calibration standard;
7. descent: same backend on the target row; 8. offline: compiler synthesis once;
online: `O(r)` evals + one Hankel solve per target; 9. memory `Theta(r)` for the
Prony system, embarrassingly parallel over evaluation points.

### Cost model
Per target: `(2r+O(1)) × C_eval(P1510) + O(M(r) log r)` for the Hankel/root/
Vandermonde solve. With `C_eval = Theta(r^2)` (P1510-R1), total `= Theta(r^3)` —
**identical exponent** to P1511-R2 unless a batched multipoint evaluation shares
work across the `2r` points below `Theta(r^2)` each. Sub-rho requires the total
membership exponent `< 3/2` in `L=q^{1/5}`. vs rho `1/2`; vs BSGS `1/2`; vs the
P1510 per-target compiler: same exponent unless multipoint sharing wins.

### Why the existing negative results do not already kill it
P1511-R2 lower-bounded the *materialized product circuit* (`r^3` leaves);
Ben-Or–Tiwari never materializes the product — it interpolates from values. The
open question is whether `2r` evaluations of a `Θ(r²)` compiler can be batched
(multipoint evaluation / transposed Vandermonde) below `Θ(r³)` total.

### Likely fatal obstruction
The P1510 compiler is not a low-degree univariate in one evaluation variable that
admits fast multipoint evaluation; each of the `2r` evaluations independently
costs `Θ(r²)`, so total stays `Θ(r³)` — reproduces the cubic floor. Near-certain.

### Minimal falsifying experiment
Toy `p in {1009, 4099, 40009}` (also `q=Theta(r^5)` synthetic `r in {4,6,8,12,16,24}`),
seeds `s=1..5`, ordinary prime-order controls. Positive control: a planted
`r`-sparse target where Prony provably recovers all rows. Negative control: a dense
(non-sparse) output where Prony must fail. Measure total field-op exponent
`#evals × cost/eval` and confirm whether multipoint sharing drops it below `r^2`
per eval.

### Quantitative promotion gate
Reject unless the **measured total membership exponent** drops below `3/2` in
`L=q^{1/5}` on `>=3` sizes with a fitted trend crossing it. Recovering correct rows
at cubic cost is a scoped negative, not a promotion.

### Proof track
Theorem: the P1510 compiler restricted to the source-tag evaluation line admits a
degree-`d=O(r)` structure enabling `2r`-point evaluation in `O(M(r) log r)` total,
giving membership recovery in `o(r^3)`.

### Disproof track
Show each evaluation is `Omega(r^2)` and evaluations do not share (distinct
Vandermonde nodes force independent full compiler runs) → total `Omega(r^3)`;
reproduces P1511-R2.

### Reproduction artifact
contract `experiment_contract_p1550_benor_tiwari_membership_backend.md`; impl
`tasks/ecdlp_index_calculus/p1550_benor_tiwari_backend.py`; result
`p1550_benor_tiwari_backend.json`; audit `p1550_benor_tiwari_backend_audit.json`;
ledger `ECFG-P1550`.

---

## Candidate: ADOLPHSPERBER-A2 ⊗ — p-adic Newton-polygon (Adolphson–Sperber) relation-supply meter

### One-sentence mechanism
Exploit the **Adolphson–Sperber p-adic Newton-polygon bound** on the Frobenius
slopes / p-adic valuations of the point count of the m-th Semaev hypersurface to
pin the *p-adic* component of the relation-supply exponent — the valuation-side
complement of batch6's archimedean Lang–Weil count meter — closing a second
heuristic assumption in every prior "below rho" supply estimate.

### Status
HYPOTHESIS (measurement primitive)

### Novelty classification
LEDGER-NEW (the ledger's occupancy `P1471/P1472` are empirical hit ratios; batch6
`LANGWEIL-METER-A3` gives the archimedean *magnitude* `p^{m-2}+O(p^{m-2-1/2})`;
no entry computes the **p-adic Newton polygon / Frobenius slopes** of the Semaev
variety, which control the valuation distribution and hence low-valuation
relation clustering).

### Semantic fingerprint
(object: the exponential-sum / zeta function of `V_m` via its Newton polytope
`Delta`; public ops: Newton-polygon construction, Hodge-polygon comparison,
p-adic valuation counting; hidden structure: Frobenius slope distribution; info
discarded: individual points; info retained: slope multiset + p-adic supply
correction; relation-gen primitive: unchanged; compression: none; rank mechanism:
supply → expected rank; descent: standard; dominant cost: sharpens the *supply*
exponent's p-adic term).

### Nearest ledger entries
1. `LANGWEIL-METER-A3` (batch6) — archimedean magnitude; ADOLPHSPERBER is the
   p-adic-slope complement (valuations, not size).
2. batch2 `C2` p-curvature — a mod-p connection *barrier*; ADOLPHSPERBER is a
   Newton-polygon *count* refinement, not a connection.
3. `P1471/P1472` occupancy — empirical; ADOLPHSPERBER is the exact p-adic bound.
4. Kousidis–Wiemers first-fall-degree — bounds solving degree; ADOLPHSPERBER
   bounds supply valuation.
5. batch3 `ENERGY-D1` — additive-energy supply ceiling; ADOLPHSPERBER is
   cohomological/p-adic, an independent method.

### Nearest literature
Adolphson–Sperber (1989) "Exponential sums and Newton polyhedra"; Wan's
generic-Newton-polygon / Hodge–Stickelberger theory; Dwork p-adic cohomology.
**Gap:** the Newton polytope of the *symmetrized* m=5 Semaev polynomial and its
generic p-adic Newton polygon are uncomputed, as is whether the slope distribution
biases low-valuation (smooth) relation supply enough to change the exponent.

### Target family
Ordinary prime-order `E/F_p`; m in {3,4,5}; exclude p dividing the Newton-polytope
denominators (degenerate slope) and singular-dominated toy primes.

### Full algorithmic path
Measurement-only for the p-adic supply term, plugged into the RT-1472/RT-1476
skeleton: 1. build `V_m` and its Newton polytope `Delta`; 2. compute the generic
Newton polygon (Wan) and compare to the Hodge polygon; 3. count `F_p`-points by
valuation class (toy-exact); 4. relation prob = low-valuation smooth-point density
→ corrected supply exponent; 5–7 inherited; 8. offline none; 9. memory negligible.

### Cost model
Toy-exact `O(p^{m-1})` (toy only); the deliverable is the p-adic correction to the
supply *exponent constant* feeding the rho comparison, not a runnable attack.
Compares the p-adic-corrected supply exponent against the heuristic used in
RT-1472/RT-1476.

### Why the existing negative results do not already kill it
It is not an attack; it removes the second (p-adic) half of the smoothness
heuristic that Lang–Weil alone does not cover — potentially *tightening* the
barriers rather than crossing them.

### Likely fatal obstruction
The generic Newton polygon almost certainly coincides with the Hodge polygon
(ordinary case), giving the expected slope distribution and **confirming** the
heuristic supply exponent — value is in closing an assumption, not crossing `1/2`.

### Minimal falsifying experiment
Toy `p in {101,211,431,809,1601,4099}`, seeds `1..5`; compute the generic Newton
polygon of `V_m` for m=3,4,5 and the valuation-stratified point count; compare to
the archimedean count and to empirical occupancy `P1471`. Positive control: a
variety with a known supersingular (non-ordinary) Newton-polygon jump (elevated
low-valuation clustering). Negative control: an ordinary variety matching the Hodge
polygon.

### Quantitative promotion gate
Barrier-grade meter: "promotion" = a *measured* p-adic supply correction that moves
the RT-1472/RT-1476 optimum by a computable amount. If the corrected exponent still
forbids `delta>1/4` / `alpha<3/2`, record as a tightened barrier (pairs
LANGWEIL-SUPPLY-D2).

### Proof track
Theorem: the generic Newton polygon of the symmetrized m=5 Semaev variety equals
its Hodge polygon on a positive-density ordinary curve family, fixing the p-adic
supply term.

### Disproof track
A curve family with an anomalous Newton-polygon jump (extra low-valuation supply)
would be a positive lead worth escalating.

### Reproduction artifact
contract `experiment_contract_p1551_adolphson_sperber_supply_meter.md`; impl
`tasks/ecdlp_index_calculus/p1551_adolphson_sperber_supply.py`; result + audit;
ledger `ECFG-P1551`.

---

## Candidate: POLYPART-A3 ⊗ — Guth–Katz polynomial-partitioning batch-membership data structure

### One-sentence mechanism
Exploit **polynomial partitioning** (Guth–Katz algebraic method: a degree-`D`
partitioning polynomial whose zero set splits space into `O(D^m)` cells each
containing few factor-base points) as a *range-searching data structure* that
answers a batch of `T` five-point membership queries in sublinear amortized cost,
testing whether algebraic point-location lowers the per-query exponent `alpha`
below the resultant/Gröbner backend on subproblem P (RT-1476).

### Status
HYPOTHESIS

### Novelty classification
LITERATURE-ADJACENT (the algebraic method appears nowhere as an ECDLP data
structure; distinct from batch1 `INC-A3` output-sensitive *incidence reporting*,
which counted incidences via Szemerédi–Trotter/finite-field bounds — POLYPART
*builds a partition* and does point-location, an algorithmic use, not a counting
bound).

### Semantic fingerprint
(object: the arrangement of the Semaev hypersurface `S_m=0` and the factor-base
point set; public ops: partitioning-polynomial construction, cell membership,
per-cell brute check; hidden structure: low incidence between few surfaces and
partitioned points; info discarded: cross-cell pairs; info retained: per-cell
candidate lists; relation-gen primitive: point-location + local check;
compression primitive: the partition tree; rank mechanism: unchanged; descent:
locate the target in cells; dominant cost: `#cells × per-cell cost` amortized
over `T` queries).

### Nearest ledger entries
1. `INC-A3` (batch1) output-sensitive incidence — counting bound; POLYPART is a
   partition data structure answering location queries.
2. batch4 `SIGNRANK-GAMMA2-B3` — Zarankiewicz supply/query pincer; POLYPART is a
   constructive partition, not an extremal bound.
3. `RT-1476-SUBRES-A1` (batch2) — eliminant-degree query; POLYPART sidesteps the
   eliminant with geometric location.
4. batch6 `FINEGRAINED-OV-D1` — conditional query lower bound; POLYPART is a
   candidate upper-bound construction it would constrain.
5. `ECFG-RT-1476` gate — POLYPART is an `alpha`-reduction attempt for it.

### Nearest literature
Guth–Katz (2015) Erdős distinct distances; Agarwal–Matoušek–Sharir algebraic
range searching; Dvir polynomial method. **Gap:** over `F_p` (not `R`), the
partitioning polynomial's cell structure and the polynomial-ham-sandwich theorem
degrade — finite-field analogues (Bukh–Tsimerman) give weaker guarantees, and no
result bounds batched Semaev membership by cell decomposition.

### Target family
Ordinary prime-order `E/F_p`; m in {4,5}; exclude curves whose factor-base image
concentrates on a low-degree subvariety (degenerate partition).

### Full algorithmic path
1. factor base `B`; 2. build a degree-`D` partitioning polynomial for the
factor-base image; 3. relation gen: for each of `T` targets, locate its
Semaev-fiber constraint in the `O(D^m)` cells and brute-check the few points per
cell; 4. verify by EC re-addition; 5. sparse GF(p) matrix standard; 6–7 standard
/ target location; 8. offline: partition build once (amortized over `T`); online:
per-target location; 9. memory `Theta(#cells + |B|)`.

### Cost model
Build `~ poly(D)`; per query `~ (#cells hit) × (points/cell)`. With `|B|=L=q^{1/5}`
points and degree `D`, cells `~ D^m`, points/cell `~ L/D^{m-1}`; balancing gives a
per-query exponent that **only improves the constant / low-order term unless the
Semaev surface degree stays bounded**, which at m=5 it does not. Sub-rho needs the
amortized per-query exponent `< 3/2` in `L`. vs rho `1/2`.

### Why the existing negative results do not already kill it
The `Omega(r^5)` Chow atomizer bound is for scalar-linear determinantal atomizers;
polynomial partitioning is a geometric point-location model with a different cost
(cell count × local work), not a determinant.

### Likely fatal obstruction
Over `F_p` the polynomial-ham-sandwich/partition guarantees are weak (Bukh–
Tsimerman), and the Semaev surface degree at m=5 forces cells to still contain
`Omega(L)` candidates → no exponent gain; near-certain reproduction of the linear
per-query floor.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`, batch `T=Theta(L)` queries; build the
partition, measure amortized per-query field-op exponent vs a brute backend and vs
the eliminant backend. Positive control: a low-degree planted surface where
partitioning provably helps. Negative control: a full-degree Semaev surface.

### Quantitative promotion gate
Reject unless the **amortized** per-query membership exponent drops below `3/2`
(equivalently `alpha<3/2`) on `>=3` sizes with a crossing trend. Constant-factor
location speedups do not promote.

### Proof track
Theorem: a degree-`D` finite-field partition answers batched m=5 Semaev membership
in amortized `o(L^{3/2})` field ops.

### Disproof track
Show cells retain `Omega(L)` candidates at m=5 (near-certain) → amortized exponent
`>= 3/2`; scoped negative and evidence toward FINEGRAINED-OV-D1.

### Reproduction artifact
contract `experiment_contract_p1552_polynomial_partition_membership.md`; impl
`tasks/ecdlp_index_calculus/p1552_poly_partition_membership.py`; result + audit;
ledger `ECFG-P1552`.

---

## Candidate: RONKIN-B1 ⊗ — Ronkin-function / non-archimedean coamoeba relation-density representation

### One-sentence mechanism
Exploit the **Ronkin function** of the Semaev polynomial (whose Monge–Ampère
measure is the density of the amoeba and whose gradient is the order map counting
lattice points in Newton-polytope cells) — in its non-archimedean / tropical
incarnation over `F_p` — to represent relation density analytically and predict
relation-rich Newton-cells before Semaev evaluation.

### Status
CONJECTURE

### Novelty classification
LEDGER-NEW as an object (tropical/Newton-polytope decomposition appeared as
`POLY-A1`/`TROP-B3`, but those used the *polytope combinatorics*; the Ronkin
function is the analytic potential whose Hessian measure is a *density*, a
strictly finer invariant, and it is ledger-absent).

### Semantic fingerprint
(object: Ronkin function `N_S(x) = log-integral of |S|` and its Monge–Ampère
measure; public ops: valuation map, order-map gradient, Legendre transform;
hidden structure: amoeba density concentration; info discarded: phases; info
retained: cell densities; relation-gen primitive: density-guided cell sampling;
compression primitive: piecewise-linear tropicalization; rank mechanism: standard;
descent: standard; dominant cost: whether density concentration beats uniform by
more than a constant).

### Nearest ledger entries
1. `POLY-A1` Newton-polytope decomposition — polytope combinatorics; RONKIN is the
   density potential on it.
2. `TROP-B3` tropical five-point membership — tropical variety; RONKIN is the
   Ronkin/amoeba analytic layer above the tropical skeleton.
3. batch3 `SKEL-B3` Berkovich skeleton — non-arch skeleton; RONKIN is the density
   measure, not the retraction skeleton.
4. batch6 `LANGWEIL-METER-A3` — exact point count; RONKIN is an analytic density
   approximation.
5. batch6 `EXPLICIT-FORMULA-C3` — L-function density bias; RONKIN is polytope/
   valuation density.

### Nearest literature
Ronkin (2001); Passare–Rullgård amoeba/Monge–Ampère; Purbhoo lopsidedness;
Einsiedler–Kapranov–Lind non-archimedean amoebas. **Gap:** amoebas are an
*archimedean* (complex) construction; over `F_p` only the tropical shadow survives,
and whether a usable density (finer than the Newton polytope already tested)
exists non-archimedeanly for the Semaev polynomial is unestablished — the core
risk.

### Target family
Ordinary prime-order `E/F_p`; m in {3,4,5}; exclude curves where the Semaev Newton
polytope degenerates.

### Full algorithmic path
1. factor base `B`; 2. relation gen: compute the tropical/Ronkin density, sample
factor-base tuples weighted by predicted cell density; 3. verify by EC re-addition;
4. relation prob = density-lifted yield; 5–7 standard; 8. offline: density map;
9. memory negligible. **INCOMPLETE risk flagged:** if no non-archimedean density
beyond the Newton polytope exists over `F_p`, there is no relation-gen content — in
that case the candidate degrades to a negative about archimedean-method transfer.

### Cost model
Best case: a density-guided constant-factor yield lift; crossing `1/2` requires
super-constant density concentration, which the Newton-polytope test (`POLY-A1`,
negative) already suggests is absent. vs rho `1/2`; likely constant-only.

### Why the existing negative results do not already kill it
`POLY-A1`/`TROP-B3` tested the polytope combinatorics and the tropical variety, not
the *density measure* (Monge–Ampère of the Ronkin potential); a concentrated
density could in principle bias sampling beyond what the polytope shape shows.

### Likely fatal obstruction
Over `F_p` there is no archimedean amoeba; the non-archimedean density collapses to
the tropical/polytope data already found inert (`POLY-A1` negative) → constant-only.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; compute the tropical density and measure
relation-yield lift vs a uniform sampler and vs the Newton-polytope-only sampler
(isolating the density's marginal value). Positive control: a planted
concentrated-density polynomial. Negative control: a uniform-density polytope.

### Quantitative promotion gate
Reject unless the yield lift is super-constant (changes the sampling exponent)
beyond both the uniform and Newton-polytope-only baselines on `>=3` sizes.

### Proof track
Theorem: the Semaev Ronkin Monge–Ampère measure concentrates relation supply by a
super-constant factor over the Newton-polytope-uniform baseline.

### Disproof track
Show the non-archimedean density equals the Newton-polytope data (near-certain) →
constant-only; scoped negative on archimedean-density transfer.

### Reproduction artifact
contract `experiment_contract_p1553_ronkin_density_representation.md`; impl
`tasks/ecdlp_index_calculus/p1553_ronkin_density.py`; result + audit; ledger
`ECFG-P1553`. **Flagged INCOMPLETE-risk (relation-gen content contingent on a
non-trivial non-archimedean density existing).**

---

## Candidate: LISTDECODE-B2 ⊗ — Guruswami–Sudan list-decoding of the source-coded relation predicate as a batch relation generator

### One-sentence mechanism
Exploit **algebraic list-decoding** (Guruswami–Sudan / folded-RS): treat the
source-coded Hasse-jet factor labels of `IDEA-068` (P1509) as evaluations of an
unknown low-degree codeword, so that decoding within the Johnson radius returns the
**entire list** of factor-base decompositions of a target in one interpolation +
root-finding pass, replacing per-tuple Semaev search on subproblem P (RT-1476).

### Status
CONJECTURE

### Novelty classification
LITERATURE-ADJACENT (Reed–Solomon *source codes* already label factors in P1509,
but as a labeling/verification device; using the *list-decoding algorithm itself*
as the relation-generation primitive — the decoder's output list = the
decomposition batch — is ledger-absent and a distinct mechanism from the
constructive Hasse section).

### Semantic fingerprint
(object: the factor-label code + a received word derived from the target; public
ops: bivariate interpolation, root-finding over `F_p[x]`, RS decoding; hidden
structure: valid decompositions lie on a low-degree curve in code space; info
discarded: non-codeword noise; info retained: the decoded list; relation-gen
primitive: list-decode; compression primitive: the interpolation polynomial;
rank mechanism: standard sparse GF(p); descent: decode the target's received word;
dominant cost: interpolation degree × list size).

### Nearest ledger entries
1. `ECFG-P1509` Hasse-jet source section — RS codes *label* factors; LISTDECODE
   *decodes* to enumerate decompositions.
2. `ECFG-P1510-R1` marked-resultant compiler — per-target eliminant; LISTDECODE is
   a decoding backend, not an eliminant.
3. batch5 `POWERPROJ-A1` — power-projection count; LISTDECODE returns the explicit
   list, not a count.
4. batch4 `APOLARITY-ATOMIZER-A2` — Waring/catalecticant compiler; LISTDECODE is
   an interpolation-decoding compiler.
5. `ECFG-RT-1476` — LISTDECODE is an `alpha`-reduction attempt for it.

### Nearest literature
Sudan (1997); Guruswami–Sudan (1999); Guruswami–Rudra folded-RS (2008);
Coppersmith–Sudan multivariate. **Gap:** no reduction expresses five-point Semaev
membership as decoding a specific RS/AG code, and the Johnson-radius list size vs
the `L^m/q` relation count is uncomputed — whether the decodable radius even
contains the valid decompositions is open and the core risk.

### Target family
Ordinary prime-order `E/F_p`; m in {4,5}; exclude curves whose factor-label code
is not MDS (degenerate decoding).

### Full algorithmic path
1. factor base `B` with P1509 source codes; 2. relation gen: form a received word
from the target's Semaev constraint, run Guruswami–Sudan (interpolate a bivariate
`Q`, root-find `Q(x,y)=0` for `y=f(x)`), output the list of consistent
decompositions; 3. verify by EC re-addition; 4. relation prob = fraction of valid
tuples inside the decoding radius; 5. sparse GF(p) matrix standard; 6–7 standard /
target decode; 8. offline: code design once; online: interpolation + root-find per
target; 9. memory `Theta(codeword length)`.

### Cost model
Per target: interpolation `~ O(list × length^2)` + root-finding `~ O~(length ×
list)` field ops. Sub-rho requires this `< L^{3/2}` at `L=q^{1/5}` **and** the
decoding radius to contain `Omega(1)` fraction of valid decompositions. vs rho
`1/2`; vs Semaev-Gröbner backend (superlinear in `L`).

### Why the existing negative results do not already kill it
P1509 established the *code* and exact labels; it did not test decoding as a
*generator*. The `Omega(r^5)` atomizer bound is for scalar-linear determinantal
atomizers; list-decoding is an interpolation model with cost interpolation-degree ×
list-size, not a determinant.

### Likely fatal obstruction
The valid decompositions almost surely lie **outside** the Johnson radius (they are
not a low-degree codeword perturbation of one another), so the decoder returns an
empty or wrong list; and forcing them inside the radius blows the list size to
`Omega(L)` → no gain. Near-certain.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}` and synthetic `q=Theta(r^5)`, seeds `1..5`; encode the
factor base, form target received words, run GS decoding, measure list
completeness/soundness and the per-target field-op exponent. Positive control: a
planted codeword whose agreements are exactly the decompositions (decodable).
Negative control: random decompositions (outside any radius).

### Quantitative promotion gate
Reject unless (a) the decoding radius provably contains `Omega(1)` of valid
decompositions **and** (b) the per-target exponent `< 3/2` on `>=3` sizes with a
crossing trend. Correct decoding of a planted control alone does not promote.

### Proof track
Theorem: five-point Semaev membership reduces to decoding an explicit RS/AG code
within its list-decoding radius with list size `O(polylog)`.

### Disproof track
Show valid decompositions require agreement below the Johnson bound or force
`Omega(L)` list size (near-certain) → no exponent gain; scoped negative.

### Reproduction artifact
contract `experiment_contract_p1554_listdecode_relation_generator.md`; impl
`tasks/ecdlp_index_calculus/p1554_listdecode_generator.py`; result + audit; ledger
`ECFG-P1554`.

---

## Candidate: SCHURPLETHYSM-B3 ⊗ — Schur / plethysm symmetric-function representation of symmetrized membership

### One-sentence mechanism
Exploit the fact that the **symmetrized** summation polynomial (FHJRV 2014) lives
in the ring of symmetric functions to expand five-point membership in the **Schur
basis**, testing whether Littlewood–Richardson / plethysm structure yields a
membership test whose cost is governed by a small number of Schur components rather
than the dense symmetric polynomial.

### Status
CONJECTURE

### Novelty classification
LEDGER-NEW (symmetrization is used for the factor base and torsion speedups, but
the *Schur-basis / plethysm* expansion of the relation is ledger-absent; distinct
from `APOLARITY-ATOMIZER-A2` (Waring/catalecticant, the *dual* apolar side) and
from `SYZYGY-REGULARITY-B2` (free resolution of the ideal)).

### Semantic fingerprint
(object: the symmetrized Semaev relation as an element of `Lambda` (symmetric
functions); public ops: Schur expansion, LR coefficients, plethysm; hidden
structure: sparsity in the Schur basis; info discarded: monomial-basis density;
info retained: nonzero Schur components; relation-gen primitive: Schur-component
membership; compression primitive: Schur-basis sparsity; rank mechanism: standard;
descent: expand the target constraint in Schur basis; dominant cost: number of
nonzero Schur components at m=5).

### Nearest ledger entries
1. `APOLARITY-ATOMIZER-A2` (batch4) — apolar/Waring dual; SCHURPLETHYSM is the
   Schur/plethysm primal expansion.
2. `SYZYGY-REGULARITY-B2` (batch4) — Betti table of the ideal; SCHURPLETHYSM is a
   basis change of the polynomial, not a resolution.
3. FHJRV 2014 symmetrized Semaev — uses symmetry for torsion speedup;
   SCHURPLETHYSM uses the *representation-theoretic decomposition* of the same ring.
4. batch1 `TT-B2` tensor-train — contracts the fixed tensor; SCHURPLETHYSM
   re-expands the polynomial in an irreducible basis.
5. `ECFG-RT-1476` — SCHURPLETHYSM is an `alpha`-reduction attempt for it.

### Nearest literature
Macdonald "Symmetric Functions and Hall Polynomials"; FHJRV 2014 symmetrized
summation polynomials; plethysm/LR-rule (Stanley EC2). **Gap:** the Schur expansion
of the symmetrized m=5 Semaev polynomial and whether it is sparse (few components)
are uncomputed; symmetric-function methods have never been applied to the Semaev
membership cost.

### Target family
Ordinary prime-order `E/F_p`; m=5 symmetrized; exclude small-characteristic p where
the Schur basis over `F_p` degenerates (`p <= m`).

### Full algorithmic path
1. factor base `B` (symmetrized coordinates); 2. relation gen: expand the target's
symmetrized membership constraint in the Schur basis, test membership by nonzero
components; 3. verify by EC re-addition; 4. relation prob unchanged; 5. sparse
GF(p) matrix standard; 6–7 standard / Schur-basis target expansion; 8. offline:
Schur transition once; online: component test per target; 9. memory `Theta(#Schur
components)`.

### Cost model
If the symmetrized relation has `s = polylog` nonzero Schur components, membership
is `O(s)` per candidate; sub-rho requires `s` and the transition cost to give a
per-query exponent `< 3/2`. But the number of Schur functions of degree `d` in `m`
variables grows like the partition count `p(d)` — likely exponential in the Semaev
degree at m=5. vs rho `1/2`.

### Why the existing negative results do not already kill it
Prior work used symmetrization only for torsion/degree reduction; no prior meter
tested the *Schur-basis sparsity* of the relation, which is a different quantity
than monomial density or apolar rank.

### Likely fatal obstruction
The Schur expansion of a high-degree symmetric polynomial has `Omega(p(deg))`
components (exponential), so no compression; near-certain reproduction of the dense
cost.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; compute the exact Schur expansion of the
symmetrized m=3,4,5 Semaev polynomial and count nonzero components vs degree.
Positive control: a symmetric polynomial known to be Schur-sparse (a single Schur
function). Negative control: a generic symmetric polynomial (dense in Schur basis).

### Quantitative promotion gate
Reject unless the Schur-component count is `polylog` (super-polynomially fewer than
the partition bound) **and** the per-query exponent `< 3/2` on `>=3` sizes.

### Proof track
Theorem: the symmetrized m=5 Semaev polynomial has `O(polylog q)` nonzero Schur
components.

### Disproof track
Count `Omega(p(deg))` components (near-certain) → no compression; scoped negative.

### Reproduction artifact
contract `experiment_contract_p1555_schur_plethysm_membership.md`; impl
`tasks/ecdlp_index_calculus/p1555_schur_plethysm.py`; result + audit; ledger
`ECFG-P1555`.

---

## Candidate: ACFA-C1 ⊗ — Hrushovski twisted-Lang–Weil difference-variety Frobenius-fiber probe

### One-sentence mechanism
Exploit **ACFA / difference-field** structure (Hrushovski's twisted Lang–Weil
estimates for varieties cut by `Frobenius`-difference equations) by adjoining the
Frobenius `sigma` to the Semaev membership system, testing whether the
difference-variety `{x : S_m(x)=0, sigma(x)=x^p}` has a sharply-counted fiber
structure that exposes a sub-`sqrt(n)` decomposition shortcut.

### Status
OPEN

### Novelty classification
POSSIBLY NOVEL (difference-field / ACFA / twisted-Lang–Weil counting is
ledger-absent; distinct from batch6 `LANGWEIL-METER-A3` (plain variety count),
batch4 `PILA-WILKIE-C2` (o-minimal char-0 counting), and all arithmetic-dynamical
candidates (`SPEC-C2`, `ARBOREAL-C1`, `DML-ORBIT-C1`) which act on iteration/orbit
maps, not on the Frobenius-difference structure of the membership variety).

### Semantic fingerprint
(object: the difference variety `(V_m, sigma)` in `ACFA`; public ops: Frobenius,
Semaev test, Hrushovski point count; hidden structure: `sigma`-fiber /
transformal-dimension of membership; info discarded: non-`sigma`-closed points;
info retained: the twisted count; relation-gen primitive: difference-fiber
enumeration; compression primitive: transformal degree; rank mechanism: standard;
descent: solve the `sigma`-fiber over the target; dominant cost: cost of locating
a `sigma`-fixed decomposition).

### Nearest ledger entries
1. batch6 `LANGWEIL-METER-A3` — plain Lang–Weil count; ACFA is the *twisted*
   (difference-equation) count.
2. batch4 `PILA-WILKIE-C2` — o-minimal counting (char 0); ACFA is difference-field
   (char p).
3. report1 `SPEC-C2` Lattès transfer operator — iteration dynamics; ACFA is the
   Frobenius-difference structure, not iteration.
4. batch5 `ARBOREAL-C1` — preimage tree of a self-map; ACFA is the `sigma`-closure
   of the membership variety.
5. batch6 `DML-ORBIT-C1` — additive translation orbit; ACFA is Frobenius, not
   translation.

### Nearest literature
Hrushovski "The Elementary Theory of the Frobenius Automorphism" (twisted Lang–Weil);
Chatzidakis–Hrushovski ACFA model theory; Macintyre difference fields. **Gap:** over
a *prime* field `F_p` the Frobenius `x -> x^p` is the **identity**, so `sigma=id`
and the difference structure is trivial on `F_p`-points — the twisted count degrades
to the plain one. Whether adjoining a *nontrivial* `sigma` (via a small extension
`F_{p^k}` carrier that still returns the `F_p` subgroup) yields exploitable fibers
is the open, high-risk question.

### Target family
Ordinary prime-order `E/F_p`; the difference structure is probed on a controlled
extension carrier `F_{p^k}`, `k` small, returning the `F_p` target subgroup.

### Full algorithmic path
1. factor base `B` over the extension carrier; 2. relation gen: cut the Semaev
system with `sigma(x)=x^p`, enumerate `sigma`-fibers via the twisted count;
3. verify by EC re-addition into the `F_p` subgroup; 4. relation prob = twisted
fiber density; 5. sparse GF(p) matrix standard; 6–7 standard / `sigma`-fiber
descent; 8. offline: difference-ideal setup; 9. memory standard. **INCOMPLETE risk:
if `sigma=id` on `F_p` the relation-gen stage is empty.**

### Cost model
If a nontrivial `sigma` gives a transformal-dimension drop exposing decompositions
in `o(sqrt(n))`, sub-rho; but the trivial-`sigma` collapse gives cost `= Theta(n/|X|)`
(no shortcut). vs rho `1/2`.

### Why the existing negative results do not already kill it
It is a genuinely different framing (Frobenius-difference variety) from every prior
count/dynamics candidate; the plain Lang–Weil meter did not consider the
`sigma`-closed subvariety.

### Likely fatal obstruction
On `F_p`, `Frobenius = id`, so the difference variety adds no constraint and the
count collapses to Lang–Weil; on an extension carrier the returned subgroup is the
`F_{p^k}` object (Gaudry-barriered), not the native `F_p` target — the twist buys
nothing for the original subgroup. Near-certain.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, small `k in {2,3}`, seeds `1..5`; construct the
difference variety, compute the twisted point count and the `sigma`-fiber structure,
and test for any sub-`sqrt(n)` decomposition locator returning the `F_p` subgroup.
Positive control: a char-p difference variety with a known nontrivial transformal
fiber. Negative control: the `sigma=id` (prime-field) case (expected trivial).

### Quantitative promotion gate
Reject unless a `sigma`-fiber locator returns native-`F_p`-subgroup decompositions
with exponent `<1/2` on `>=3` sizes. The `sigma=id` collapse is a scoped negative.

### Proof track
Theorem: the twisted Semaev difference variety over an `F_{p^k}` carrier admits a
transformal-dimension drop yielding native-`F_p`-subgroup decompositions below
`sqrt(n)`.

### Disproof track
Show `sigma=id` on `F_p` (trivial) and the extension carrier returns only the
`F_{p^k}` subgroup (Gaudry) → no native gain; scoped negative.

### Reproduction artifact
contract `experiment_contract_p1556_acfa_difference_variety.md`; impl
`tasks/ecdlp_index_calculus/p1556_acfa_difference.py`; result + audit; ledger
`ECFG-P1556`. **Flagged INCOMPLETE-risk (relation-gen empty if `sigma=id`).**

---

## Candidate: ELLNET-C2 ⊗ — Elliptic-net (Stange) bilinear-recurrence relation oracle [task-brief EDS seed]

### One-sentence mechanism
Exploit the **elliptic net / elliptic divisibility sequence** (Ward; Stange's
multi-dimensional nets, which satisfy a bilinear recurrence and compute the Tate
pairing) as a relation oracle: since the net `W(v)` vanishes exactly when a
`Z`-linear combination `sum v_i P_i` equals `O`, testing membership /
decomposition becomes reading a bilinear-recurrence net value instead of solving a
Semaev system.

### Status
OPEN

### Novelty classification
POSSIBLY NOVEL (the task brief lists "elliptic divisibility sequences" as a search
seed **never actually consumed** by the eight reports; distinct from `MAHLER-B1`
(base-p digit automata), `SPEC-C2`/`ARBOREAL-C1` (iteration/preimage dynamics), and
`PWRSUM-A3` (C-finite power sums) — the elliptic net is a **bilinear** recurrence on
a lattice, a different recurrence class).

### Semantic fingerprint
(object: the elliptic net `W: Z^k -> F_p` of the factor-base points; public ops:
the bilinear net recurrence, net-value evaluation; hidden structure: `W(v)=0` iff
`sum v_i P_i = O`; info discarded: intermediate net values; info retained: the
zero locus of `W`; relation-gen primitive: net-value vanishing test; compression
primitive: the bilinear recurrence; rank mechanism: standard; descent: locate a
net zero involving the target; dominant cost: net-value evaluation cost vs orbit
size).

### Nearest ledger entries
1. batch5 `MAHLER-B1` — automatic/base-p digit sequence; ELLNET is a bilinear
   lattice recurrence, a different automaticity class.
2. batch3 `PWRSUM-A3` — C-finite power-sum recurrence; ELLNET is bilinear, not
   linear-recurrent.
3. report1 `SPEC-C2` Lattès transfer operator — iteration; ELLNET is the divisibility
   sequence, not a self-map spectrum.
4. batch5 `ARBOREAL-C1` — preimage tree; ELLNET is the forward net value.
5. `ECFG-001` direct Evans `k -> x(kB)` functional graph (NEGATIVE) — ELLNET reframes
   membership as a net-zero, not a preimage search.

### Nearest literature
Ward (1948) elliptic divisibility sequences; Stange (2011) "Elliptic nets and
elliptic curves" (net computation of Tate/Weil pairing); Shipsey elliptic-net DL
algorithms. **Gap:** elliptic-net DL algorithms compute pairings and are known to
cost `Omega(n)` (the net index grows with the scalar); no result gives a sub-`sqrt(n)`
membership test from net values, and the entry size of `W(v)` grows like the naive
`[v]P` — the near-certain obstruction.

### Target family
Ordinary prime-order `E/F_p`; k-dimensional nets for `k = m = 5`; exclude curves
with net-degenerate torsion.

### Full algorithmic path
1. factor base `B`; 2. relation gen: for a candidate lattice vector `v`, evaluate
`W(v)` by the bilinear recurrence; `W(v)=0` certifies `sum v_i P_i = O` (a relation);
3. verify by EC re-addition; 4. relation prob = density of net zeros in the search
box; 5. sparse GF(p) matrix standard; 6–7 standard / net-zero descent for the target;
8. offline: initial net block; online: recurrence steps per candidate; 9. memory
`Theta(net block)`.

### Cost model
Evaluating `W(v)` for `|v| ~ B` costs `Theta(log|v|)` recurrence steps **but** each
step's operands and the reachable-relation search still range over `Theta(n/|X|)`
candidate vectors — the net gives no shortcut to *finding* a zero, only to *testing*
one. Sub-rho requires a sublinear locator of net zeros, which the growth of `W`
forbids. vs rho `1/2`.

### Why the existing negative results do not already kill it
The elliptic net is a genuinely new recurrence class (bilinear, task-brief seed
never consumed); `ECFG-001` was a direct preimage negative, not a net-zero framing;
`MAHLER-B1`/`PWRSUM-A3` are linear recurrences.

### Likely fatal obstruction
Net values grow with the scalar (the sequence is a divisibility sequence with
`Omega(n)`-size index structure), and locating a net zero is exactly the DLP —
periodicity/growth kill, as with `MAHLER-B1` and `DML-ORBIT-C1`. Near-certain.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; build the k=2..5 elliptic net, enumerate
net zeros in a `B`-box, and test for any sub-box / recurrence structure enabling a
zero-locator with exponent `<1/2`. Positive control: a small net where all zeros are
known and checkable. Negative control: a random `F_p`-array (no net structure).

### Quantitative promotion gate
Reject unless net-zero location has an exponent `<1/2` on `>=3` sizes. Correct
net-value testing at `Theta(n/|X|)` search cost is a scoped negative.

### Proof track
Theorem: the elliptic-net zero set `{v : W(v)=0}` admits a description finer than the
DLP lattice, exploitable for sublinear zero location.

### Disproof track
Show net-zero location is equivalent to the DLP with no sub-AP structure
(near-certain) → collapses to BSGS/rho; scoped negative.

### Reproduction artifact
contract `experiment_contract_p1557_elliptic_net_oracle.md`; impl
`tasks/ecdlp_index_calculus/p1557_elliptic_net_oracle.py`; result + audit; ledger
`ECFG-P1557`.

---

## Candidate: CROOTSISASK-C3 ⊗ — Croot–Sisask almost-periodicity relation-bundling

### One-sentence mechanism
Exploit **Croot–Sisask almost periodicity** (a large Bohr-set-structured subset of
the factor base on which the membership indicator is `L^2`-almost-invariant under
translation) to generate valid relations in **structured bundles** — each verified
relation implying many nearby ones by almost-periodicity — reducing the amortized
per-relation membership cost of subproblem P.

### Status
HEURISTIC

### Novelty classification
LITERATURE-ADJACENT (additive-combinatorial predictors appeared as
`NILSEQ-C2` (higher-order Fourier) and `ENERGY-D1` (sum-product energy ceiling);
Croot–Sisask almost periodicity is a distinct tool — an `L^p`-invariance /
Bogolyubov-type structure — not a nilsequence correlation or an energy count).

### Semantic fingerprint
(object: the membership indicator as an `L^2` function on the factor base; public
ops: convolution, Bohr-set construction, translation; hidden structure: almost-
translation-invariance on a large Bohr set; info discarded: non-Bohr part; info
retained: bundled relations; relation-gen primitive: translate a seed relation
across the Bohr set; compression primitive: Bohr-set parametrization; rank
mechanism: standard; descent: standard; dominant cost: whether the bundle size
beats uniform by more than a constant factor).

### Nearest ledger entries
1. batch3 `NILSEQ-C2` nilsequence predictor — higher-order Fourier; CROOTSISASK is
   `L^p`-almost-periodicity, a different structure.
2. batch3 `ENERGY-D1` additive-energy ceiling — bounds low-weight supply; CROOTSISASK
   *generates* bundles, not a ceiling.
3. batch6 `EXPLICIT-FORMULA-C3` — L-function residue bias; CROOTSISASK is
   translation-invariance bias.
4. `P1449` ancestry-permutation invariance — CROOTSISASK must beat a permutation null.
5. `ECFG-014` RHS graph enrichment (NEGATIVE) — empirical selector; CROOTSISASK is an
   analytic almost-periodicity structure.

### Nearest literature
Croot–Sisask (2010) "A probabilistic technique for finding almost-periods of
convolutions"; Sanders' Bogolyubov–Ruzsa; Schoen–Shkredov. **Gap:** almost
periodicity gives Bohr sets of dimension `O(eps^{-2} log|A|)` — the bundle sizes are
polynomial in log, a *constant-order* effect on relation yield, and no application to
elliptic membership exists.

### Target family
Ordinary prime-order `E/F_p`; `B=q^{1/5}`.

### Full algorithmic path
1. factor base `B`; 2. relation gen: find a seed relation, construct the Bohr set on
which membership is almost-invariant, emit the bundle of translated relations;
3. verify each by EC re-addition; 4. relation prob = bundle size / cost; 5–7 standard;
8/9 standard.

### Cost model
Best case: a bundle of `polylog` relations per seed → a `polylog` amortized yield
factor; crossing `1/2` requires super-constant (polynomial-in-`L`) bundles, which
Bohr-set dimension bounds forbid. vs rho `1/2`; likely constant/polylog-only.

### Why the existing negative results do not already kill it
Almost periodicity is a distinct additive-combinatorial mechanism from nilsequences
and energy counts; no prior meter tested translation-invariant relation bundling.

### Likely fatal obstruction
Croot–Sisask Bohr-set dimension gives only `polylog` bundle sizes → constant-order
yield improvement, not an exponent change. Near-certain.

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; construct the almost-period Bohr set,
measure the relation-bundle size per seed and the amortized yield vs a uniform
sampler and vs the `P1449` permutation null. Positive control: a planted
translation-invariant relation family. Negative control: uniform sampling.

### Quantitative promotion gate
Reject unless the amortized bundle yield is super-constant (changes the sampling
exponent) against both uniform and permutation nulls on `>=3` sizes.

### Proof track
Theorem: elliptic membership is `L^2`-almost-invariant on a Bohr set large enough to
bundle `Omega(L^c)` relations per seed for some `c>0`.

### Disproof track
Bohr-set dimension bounds cap bundles at `polylog` (near-certain) → constant-only;
scoped negative.

### Reproduction artifact
contract `experiment_contract_p1558_croot_sisask_bundling.md`; impl
`tasks/ecdlp_index_calculus/p1558_croot_sisask.py`; result + audit; ledger
`ECFG-P1558`.

---

## Candidate: LIFTING-D1 ⊗ — Query-to-communication lifting lower bound on the membership exponent (barrier; pairs LISTDECODE-B2, POLYPART-A3)

### One-sentence mechanism
Apply a **query-to-communication lifting theorem** (Raz–McKenzie / Göös–Pitassi–
Watson): compose the decision-tree complexity of a base membership predicate with a
gadget to obtain a communication lower bound, so that a backend with `alpha < 3/2`
at m=5 would violate the lifted communication lower bound — a barrier from a
lower-bound technology no prior barrier used.

### Status
CONJECTURE (barrier)

### Novelty classification
POSSIBLY NOVEL as a barrier type (every prior barrier is algebraic — border-rank,
slice-rank, Chow-atomizer `Omega(r^5)`, class-function, arboreal-maximality,
asymptotic-spectrum — or fine-grained/conditional (`FINEGRAINED-OV-D1`) or
point-counting (`LANGWEIL-SUPPLY-D2`); **query-to-communication lifting** is a
distinct lower-bound machinery, unconditional given a base query bound).

### Semantic fingerprint
(object: the membership decision problem and its decision-tree/communication
complexity; public ops: the lifting gadget composition; hidden structure: the base
predicate's query complexity lifts to communication; info discarded: nothing;
info retained: the lower bound; relation-gen: n/a; compression: n/a; rank mechanism:
n/a; descent: n/a; dominant cost exponent: lower-bounds `alpha`).

### Nearest ledger entries
1. batch4 `SIGNRANK-GAMMA2-B3` — `gamma_2`/sign-rank communication *norm* (a supply/
   query pincer); LIFTING derives the communication bound *from a query bound via a
   theorem*, a different route.
2. batch6 `FINEGRAINED-OV-D1` — SETH/3SUM reduction; LIFTING is unconditional given
   the base query complexity.
3. `P1512-R1` Chow-atomizer `Omega(r^5)` — algebraic determinantal; LIFTING is
   communication-complexity-based.
4. batch5 `ASYMPSPEC-D1` — bilinear complexity; LIFTING is decision complexity.
5. `ECFG-RT-1476` — LIFTING directly bounds its `alpha`.

### Nearest literature
Raz–McKenzie (1999); Göös–Pitassi–Watson (2018) "Query-to-communication lifting";
Chattopadhyay–Koucký–Loff–Mukhopadhyay. **Gap:** no base query lower bound for
five-point elliptic membership is proven, and no gadget composition is constructed —
both are the research obligation; the lift is only as strong as the (unproven) base
bound.

### Target family
The m-point decomposition decision problem for ordinary prime-order `E/F_p`.

### Full algorithmic path (as a barrier)
1. establish a decision-tree lower bound for a base membership predicate; 2. compose
with a lifting gadget (e.g. inner-product / index); 3. conclude a communication lower
bound that any `alpha<3/2` backend would violate. No relation/descent stage — this is
a lower bound (labeled a barrier, not INCOMPLETE).

### Cost model
Delivers a lower bound `alpha >= alpha_0`; if `alpha_0 >= 3/2` the RT-1476 crossing is
closed under this model. Compares the lifted bound to the `3/2` target.

### Why the existing negative results do not already kill it
It is a new lower-bound technology; the algebraic barriers bound *determinantal/
tensor* complexity, not *decision/communication* complexity, and the fine-grained
barrier is conditional.

### Likely fatal obstruction
No nontrivial base query lower bound for elliptic membership may exist (the predicate
could have low decision-tree complexity), making the lift vacuous; the barrier may
fail to reach `3/2`.

### Minimal falsifying experiment
Toy: construct the base predicate's decision tree at m=3,4 exhaustively, measure its
query complexity, apply a small gadget, and measure the resulting communication lower
bound vs the observed backend cost. Positive control: a predicate with a known lift
(e.g. `set-disjointness`). Negative control: a low-query predicate (vacuous lift).

### Quantitative promotion gate
This is a barrier: "promotion" = a proven `alpha >= 3/2` (closing RT-1476 under the
communication model). A lift below `3/2` is a partial barrier recorded with its exact
exponent.

### Proof track
Theorem: five-point elliptic membership has decision-tree complexity `Omega(L^c)`
whose lift gives communication `Omega(L^{3/2})`, forcing `alpha >= 3/2`.

### Disproof track
Exhibit a low-query membership decision procedure (vacuous base bound) → the lift does
not reach `3/2`; the barrier is weaker than hoped.

### Reproduction artifact
contract `experiment_contract_p1559_lifting_communication_barrier.md`; impl
`tasks/ecdlp_index_calculus/p1559_lifting_barrier.py`; result + audit; ledger
`ECFG-P1559`.

---

## Candidate: POLYCALC-D2 ⊗ — Polynomial-Calculus / Ideal-Proof-System degree barrier on membership refutation

### One-sentence mechanism
Bound the **Polynomial Calculus (Nullstellensatz) / Ideal Proof System degree**
required to refute non-membership of a target in the factor-base decomposition
ideal; since PC degree lower-bounds the first-fall/solving degree of any Gröbner-
style backend, a PC-degree bound `Omega(L^{1/2})` forces the eliminant/query
exponent `alpha >= 3/2` — an algebraic-proof-system barrier distinct from the SOS
(Positivstellensatz) barrier already on file.

### Status
CONJECTURE (barrier)

### Novelty classification
LITERATURE-ADJACENT as a barrier type (batch4 `SOS-LB-D1` used SOS/Positivstellensatz
degree via pseudo-calibration — a *semidefinite/real* proof system; **Polynomial
Calculus / IPS** is the *algebraic/Nullstellensatz* proof system with distinct
degree lower-bound machinery (Razborov, Grochow–Pitassi), directly matched to the
Gröbner first-fall degree the ledger already measures).

### Semantic fingerprint
(object: the polynomial ideal of the decomposition system; public ops: PC
derivations, Nullstellensatz certificates; hidden structure: minimal refutation
degree; info discarded: nothing; info retained: the degree bound; relation-gen: n/a;
compression: n/a; rank mechanism: n/a; descent: n/a; dominant cost exponent:
lower-bounds the solving degree `beta`, hence `alpha`).

### Nearest ledger entries
1. batch4 `SOS-LB-D1` — SOS/Positivstellensatz degree (semidefinite); POLYCALC is
   Nullstellensatz/PC degree (algebraic), a different proof system.
2. `P1512-R1` Chow-atomizer `Omega(r^5)` — determinantal; POLYCALC is proof-degree.
3. Kousidis–Wiemers first-fall-degree — *upper* bounds the solving degree; POLYCALC
   *lower*-bounds it.
4. batch2 `RT-1476-SUBRES-A1` — measures eliminant degree empirically; POLYCALC
   proves a degree lower bound.
5. `ECFG-RT-1476` — POLYCALC bounds its `alpha` via `beta`.

### Nearest literature
Razborov (1998) PC degree lower bounds; Impagliazzo–Pudlák–Sgall Nullstellensatz;
Grochow–Pitassi Ideal Proof System (2018). **Gap:** no PC/Nullstellensatz degree
lower bound is proven for the elliptic decomposition ideal; whether the known
first-fall *upper* bound is matched by a PC *lower* bound is the open obligation.

### Target family
The m-point decomposition ideal for ordinary prime-order `E/F_p`; m in {4,5}.

### Full algorithmic path (as a barrier)
1. formulate non-membership as an unsatisfiable polynomial system; 2. prove a PC/
Nullstellensatz degree lower bound (e.g. via a designed pseudo-expectation /
gauge); 3. conclude the solving degree `beta = Omega(L^{1/2})`, forcing
`alpha >= 3/2`. Lower bound; no relation/descent stage.

### Cost model
Delivers `beta >= beta_0`; if `beta_0` gives `alpha >= 3/2`, RT-1476 is closed under
the Gröbner/PC model. Compares to the `3/2` target and to the Kousidis–Wiemers upper
bound.

### Why the existing negative results do not already kill it
The SOS barrier bounds a *different* (semidefinite) proof system; PC/Nullstellensatz
degree is the one directly controlling Gröbner first-fall degree, and it is unproven
for this ideal.

### Likely fatal obstruction
The elliptic decomposition ideal may have *low* PC degree (efficient Nullstellensatz
certificate), making the barrier vacuous — the same risk that keeps RT-1476 open.

### Minimal falsifying experiment
Toy `p in {1009,4099}`, m=3,4; compute exact PC/Nullstellensatz refutation degrees for
non-membership instances vs system size; extrapolate the exponent. Positive control:
a system with a known high PC degree (e.g. a pigeonhole/Tseitin encoding). Negative
control: a system with a known low-degree Nullstellensatz certificate.

### Quantitative promotion gate
Barrier: "promotion" = a proven PC degree giving `alpha >= 3/2`. A measured degree
trend below that is a partial barrier recorded with its exponent.

### Proof track
Theorem: refuting five-point non-membership requires PC/Nullstellensatz degree
`Omega(L^{1/2})`, forcing `beta -> 3/2` and `alpha >= 3/2`.

### Disproof track
Exhibit a low-degree Nullstellensatz certificate (vacuous bound) → RT-1476 stays
open under this model; the barrier fails.

### Reproduction artifact
contract `experiment_contract_p1560_polynomial_calculus_degree_barrier.md`; impl
`tasks/ecdlp_index_calculus/p1560_pc_degree_barrier.py`; result + audit; ledger
`ECFG-P1560`.

---

## Candidate: VCDIM-D3 ⊗ — VC-dimension / Sauer–Shelah relation-diversity ceiling (barrier; pairs RT-1472 δ)

### One-sentence mechanism
Bound the **VC dimension** of the factor-base membership set system and apply
**Sauer–Shelah** to cap the number of *distinct* membership patterns (hence the
number of independent relations / the usable cycle-space rank), giving a
combinatorial ceiling on the enrichment `delta` of subproblem P (RT-1472) that no
process-based `delta` meter has expressed.

### Status
CONJECTURE (barrier)

### Novelty classification
LEDGER-NEW barrier type (all prior `delta` analyses were process/spectral/topological
— peeling, effective resistance, matroid union, coboundary, graphon; **VC-dimension /
shatter-function** is a set-system combinatorial-dimension bound, structurally new).

### Semantic fingerprint
(object: the set system `{ S_t = valid tuples for target t }` on the factor base;
public ops: shatter test, Sauer–Shelah count; hidden structure: bounded VC dimension
of membership; info discarded: pattern identities; info retained: the pattern-count
ceiling; relation-gen: n/a; compression: n/a; rank mechanism: pattern count →
independent-relation ceiling; descent: n/a; dominant cost exponent: upper-bounds
`delta`).

### Nearest ledger entries
1. batch6 `HDX-COBOUNDARY-A2` — cosystolic expansion (topological); VCDIM is a
   set-system dimension.
2. batch5 `MATUNION-A2` — matroid-union packing; VCDIM is shatter-function, not a
   matroid.
3. batch3 `EFFRES-A2` — effective resistance (spectral); VCDIM is combinatorial.
4. batch4 `SIGNRANK-GAMMA2-B3` — Zarankiewicz (a set-system extremal bound); VCDIM is
   the VC/shatter refinement (Zarankiewicz is the closest; VC dimension bounds the
   *pattern count*, a distinct quantity from the incidence-count Zarankiewicz gives).
5. `ECFG-RT-1472` — VCDIM upper-bounds its achievable `delta`.

### Nearest literature
Sauer (1972); Shelah; Vapnik–Chervonenkis; Matoušek "Lectures on Discrete Geometry"
(bounded-VC set systems of algebraic origin). **Gap:** the VC dimension of the
elliptic five-point membership set system is uncomputed; whether it is bounded (giving
a polynomial Sauer–Shelah pattern ceiling that caps `delta <= 1/4`) is open.

### Target family
Ordinary prime-order `E/F_p`; `B=q^{1/5}`; the membership set system on the factor
base.

### Full algorithmic path (as a barrier)
1. define the membership set system; 2. bound its VC dimension `d` (algebraic set
systems have `d = O(deg)`); 3. apply Sauer–Shelah: distinct patterns `<= O(|B|^d)`,
capping independent relations and hence `delta`. Upper bound; no relation/descent
stage.

### Cost model
If `d = O(1)` (bounded by the Semaev degree), pattern count `= O(|B|^d)` caps the
independent-relation supply, forcing `delta <= 1/4`. Compares the ceiling to the
RT-1472 requirement `delta > 1/4`.

### Why the existing negative results do not already kill it
Every prior `delta` meter is process- or spectral-based (a lower-bound attempt);
VCDIM is a set-system *upper* bound on relation diversity — the complementary
direction, and a distinct combinatorial dimension from the Zarankiewicz incidence
count.

### Likely fatal obstruction
The VC dimension may be large enough (growing with the Semaev degree) that Sauer–
Shelah permits `delta > 1/4`, leaving the gate open; or the bound may match the
already-known random-graph `delta = 1/4` exactly (confirming rather than tightening).

### Minimal falsifying experiment
Toy `p in {1009,4099,40009}`, seeds `1..5`; exhaustively compute the shatter function
and VC dimension of the m=3,4 membership set system; derive the Sauer–Shelah pattern
ceiling and the implied `delta` bound. Positive control: a set system of known VC
dimension (halfplanes). Negative control: a full-shatter (unbounded-VC) system.

### Quantitative promotion gate
Barrier: "promotion" = a proven VC bound giving `delta <= 1/4` (closing RT-1472 under
the diversity model). A ceiling permitting `delta > 1/4` leaves the gate open and is
recorded as such.

### Proof track
Theorem: the elliptic m=5 membership set system has VC dimension `O(1)`, so
Sauer–Shelah caps independent relations at `O(|B|^{O(1)})` and forces `delta <= 1/4`.

### Disproof track
Show the VC dimension grows with `L` (unbounded shatter) → Sauer–Shelah permits
`delta > 1/4`; the gate stays open.

### Reproduction artifact
contract `experiment_contract_p1561_vc_dimension_delta_ceiling.md`; impl
`tasks/ecdlp_index_calculus/p1561_vc_dimension_ceiling.py`; result + audit; ledger
`ECFG-P1561`.

---

## 2. Ranking

Scores 0–5 on: (1) distance from prior ledger mechanisms; (2) plausibility of an
exact verifier; (3) chance of changing an exponent (not a constant); (4)
complete-path coverage; (5) falsifiability at toy scale; (6) literature-novelty
confidence; (7) *inverse* risk of hidden preprocessing/memory cost (5 = low hidden
cost). Candidates with novelty `< 3`, no complete route to descent, no rho
comparison, or no precise distinction from the closest ledger entry are rejected.

| Cand | (1)dist | (2)verif | (3)exp | (4)path | (5)fals | (6)nov | (7)¬hidden | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| BENORTIWARI-A1 | 3 | 5 | 2 | 5 | 5 | 3 | 4 | 27 | keep (conservative winner) |
| ADOLPHSPERBER-A2 | 4 | 5 | 1 | 4 | 5 | 4 | 5 | 28 | keep (meter) |
| POLYPART-A3 | 4 | 4 | 2 | 5 | 4 | 4 | 3 | 26 | keep |
| RONKIN-B1 | 4 | 3 | 1 | 3 | 4 | 4 | 4 | 23 | keep (INCOMPLETE-risk) |
| LISTDECODE-B2 | 4 | 5 | 3 | 5 | 5 | 4 | 4 | 30 | keep (representation winner) |
| SCHURPLETHYSM-B3 | 4 | 5 | 2 | 4 | 5 | 4 | 4 | 28 | keep |
| ACFA-C1 | 5 | 3 | 2 | 3 | 4 | 5 | 3 | 25 | keep (INCOMPLETE-risk) |
| ELLNET-C2 | 4 | 5 | 2 | 5 | 5 | 5 | 3 | 29 | keep (high-risk winner) |
| CROOTSISASK-C3 | 3 | 4 | 1 | 4 | 4 | 3 | 4 | 23 | keep |
| LIFTING-D1 | 5 | 3 | 4 | 4 | 3 | 5 | 5 | 29 | keep (barrier) |
| POLYCALC-D2 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | 28 | keep (barrier) |
| VCDIM-D3 | 5 | 4 | 3 | 4 | 4 | 4 | 5 | 29 | keep (barrier) |

No candidate scores novelty `< 3` on axis (1); all carry a complete path (or an
explicit INCOMPLETE-risk flag on RONKIN-B1 and ACFA-C1) and an rho comparison. Column
(3) is uniformly low for the meters/barriers by design — they *bound* the exponent
rather than claim to cross it; the three *attack* candidates (BENORTIWARI, LISTDECODE,
ELLNET) carry the exponent-crossing risk.

### Selected winners

1. **Best conservative — BENORTIWARI-A1.** Directly probes the exact crack P1511-R2
   leaves open (evaluation-based recovery vs materialized `r^3` product), has an exact
   verifier, complete path, and is the most decision-relevant conservative test.
2. **Best representation-changing — LISTDECODE-B2.** Highest total: a genuine
   relation-generation primitive change (decode-a-list vs solve-a-system), exact
   verifier via decoding soundness, complete path, and a real — if unlikely — shot at
   batching membership below `alpha=3/2`.
3. **Best high-risk — ELLNET-C2.** Consumes the one task-brief seed (elliptic
   divisibility sequences / elliptic nets) never actually used in eight reports;
   POSSIBLY NOVEL, exact verifier, complete path; near-certain periodicity/growth kill
   makes it a clean scoped-negative-in-waiting.

---

## 3. Experiment contracts and first executable commands (three winners)

### Contract W1 — BENORTIWARI-A1 (`ECFG-P1550`)

```yaml
id: ECFG-P1550
title: Output-sensitive Ben-Or–Tiwari sparse-interpolation membership backend
hypothesis: >
  Recovering the r valid source rows of the RT-1476 five-point membership object by
  Ben-Or–Tiwari/Prony sparse interpolation from O(r) evaluations of the verified
  P1510 per-target compiler achieves total membership exponent < 3/2 in L=q^{1/5},
  escaping the P1511-R2 cubic-input floor.
null_hypothesis: >
  Each of the 2r+O(1) compiler evaluations costs Theta(r^2) and evaluations do not
  share work, so total cost stays Theta(r^3) (alpha >= 3/2); Prony recovers correct
  rows but at the cubic floor.
targets:
  toy_primes: [1009, 4099, 40009]
  synthetic_q_theta_r5_r: [4, 6, 8, 12, 16, 24]
  seeds: [1, 2, 3, 4, 5]
  family: ordinary prime-order E/F_p, non-anomalous, non-supersingular, j != 0,1728
factor_base: {x_in: [0, L), L: "ceil(q^(1/5))"}
method:
  - fix a target row; view the P1510 compiler as f(z) in a source-tag eval variable
  - sample f at 2r+O(1) geometric points; run Prony (Hankel solve + root-find + transposed Vandermonde)
  - output the recovered r-sparse support = candidate decompositions
metrics:
  - evaluations_per_target
  - field_ops_per_evaluation (must test multipoint sharing < Theta(r^2))
  - total_membership_exponent (fit over sizes)
  - recovery_completeness, recovery_soundness (vs EC re-addition)
positive_control: planted r-sparse target where Prony provably recovers all rows
negative_control: dense (non-sparse) output where Prony must fail to certify
baseline: rho exponent 1/2; P1510-R1 per-target Theta(r^2); P1511-R2 product Theta(r^3)
promotion_gate: measured total exponent < 3/2 on >= 3 sizes with a crossing trend
falsification: per-evaluation cost Omega(r^2) with no sharing => total Omega(r^3)
verifier: independent EC re-addition of every recovered tuple; replay Prony solve
artifacts:
  contract: experiment_contract_p1550_benor_tiwari_membership_backend.md
  impl: tasks/ecdlp_index_calculus/p1550_benor_tiwari_backend.py
  result: p1550_benor_tiwari_backend.json
  audit: p1550_benor_tiwari_backend_audit.json
```

First executable command:

```bash
python3 tasks/ecdlp_index_calculus/p1550_benor_tiwari_backend.py \
  --primes 1009,4099,40009 --synthetic-r 4,6,8,12,16,24 --seeds 1,2,3,4,5 \
  --measure eval-count,eval-cost,total-exponent,recovery \
  --out ecdlp_index_calculus_state/p1550_benor_tiwari_backend.json
```

### Contract W2 — LISTDECODE-B2 (`ECFG-P1554`)

```yaml
id: ECFG-P1554
title: Guruswami–Sudan list-decoding of the source-coded relation predicate as a batch relation generator
hypothesis: >
  Five-point Semaev membership reduces to list-decoding an explicit RS/AG code within
  its Johnson radius, returning the full decomposition list per target in O(list x
  length^2) field ops with per-target exponent < 3/2 in L=q^{1/5}, provided the
  decoding radius contains an Omega(1) fraction of valid decompositions.
null_hypothesis: >
  Valid decompositions lie outside the Johnson radius (not a low-degree codeword
  perturbation), so the decoder returns empty/wrong lists; forcing them inside blows
  list size to Omega(L), giving no exponent gain.
targets:
  toy_primes: [1009, 4099, 40009]
  synthetic_q_theta_r5_r: [4, 6, 8, 12, 16, 24]
  seeds: [1, 2, 3, 4, 5]
  family: ordinary prime-order E/F_p; m in {4,5}; MDS factor-label code
factor_base: {x_in: [0, L), L: "ceil(q^(1/5))", source_codes: P1509_RS_labels}
method:
  - encode factor base with P1509 source codes
  - form target received word from its Semaev constraint
  - run Guruswami–Sudan (bivariate interpolation of Q; root-find Q(x,y)=0 for y=f(x))
  - output the list of consistent decompositions
metrics:
  - decoding_radius_coverage (fraction of valid decompositions inside radius)
  - list_size (vs L)
  - field_ops_per_target, per_target_exponent (fit)
  - list_completeness, list_soundness (vs EC re-addition)
positive_control: planted codeword whose agreements are exactly the decompositions
negative_control: random decompositions (outside any decoding radius)
baseline: rho 1/2; Semaev-Gröbner backend superlinear in L; P1512-R1 Omega(r^5) scalar-linear
promotion_gate: radius covers Omega(1) of decompositions AND per-target exponent < 3/2 on >= 3 sizes
falsification: agreement below Johnson bound OR list size Omega(L) => no gain
verifier: independent EC re-addition of every listed decomposition; replay interpolation + root-find
artifacts:
  contract: experiment_contract_p1554_listdecode_relation_generator.md
  impl: tasks/ecdlp_index_calculus/p1554_listdecode_generator.py
  result: p1554_listdecode_generator.json
  audit: p1554_listdecode_generator_audit.json
```

First executable command:

```bash
python3 tasks/ecdlp_index_calculus/p1554_listdecode_generator.py \
  --primes 1009,4099,40009 --synthetic-r 4,6,8,12,16,24 --seeds 1,2,3,4,5 \
  --m 5 --measure radius-coverage,list-size,per-target-exponent,soundness \
  --out ecdlp_index_calculus_state/p1554_listdecode_generator.json
```

### Contract W3 — ELLNET-C2 (`ECFG-P1557`)

```yaml
id: ECFG-P1557
title: Elliptic-net (Stange) bilinear-recurrence relation oracle
hypothesis: >
  The elliptic-net zero set {v : W(v)=0} (W(v)=0 iff sum v_i P_i = O) admits a
  structure finer than the DLP lattice, enabling a sublinear (exponent < 1/2)
  locator of net zeros involving the target.
null_hypothesis: >
  Net values grow with the scalar and locating a net zero is equivalent to the DLP
  with no sub-AP structure; net-value TESTING is Theta(log|v|) but net-zero LOCATION
  is Theta(n/|X|) => collapses to BSGS/rho.
targets:
  toy_primes: [1009, 4099, 40009]
  net_dims_k: [2, 3, 4, 5]
  seeds: [1, 2, 3, 4, 5]
  family: ordinary prime-order E/F_p; non-net-degenerate torsion
method:
  - build the k-dimensional elliptic net W of the factor-base points (Stange recurrence)
  - enumerate net zeros in a B-box; test each W(v)=0 by the bilinear recurrence
  - search for sub-box / recurrence structure enabling a sublinear zero locator
metrics:
  - net_value_test_cost (expected Theta(log|v|))
  - net_zero_location_exponent (fit; the decisive quantity)
  - zero_density_in_box
  - recovery_soundness (vs EC re-addition: sum v_i P_i == O)
positive_control: small net with all zeros known and independently checkable
negative_control: random F_p array (no net structure) — locator must fail
baseline: rho 1/2; BSGS 1/2; ECFG-001 direct preimage negative
promotion_gate: net-zero location exponent < 1/2 on >= 3 sizes
falsification: net-zero location equivalent to DLP with no sub-AP structure => scoped negative
verifier: independent EC re-addition confirming sum v_i P_i = O for every claimed zero
artifacts:
  contract: experiment_contract_p1557_elliptic_net_oracle.md
  impl: tasks/ecdlp_index_calculus/p1557_elliptic_net_oracle.py
  result: p1557_elliptic_net_oracle.json
  audit: p1557_elliptic_net_oracle_audit.json
```

First executable command:

```bash
python3 tasks/ecdlp_index_calculus/p1557_elliptic_net_oracle.py \
  --primes 1009,4099,40009 --net-dims 2,3,4,5 --seeds 1,2,3,4,5 \
  --measure test-cost,location-exponent,zero-density,soundness \
  --out ecdlp_index_calculus_state/p1557_elliptic_net_oracle.json
```

---

## 4. Red-team: are the three winners disguised repetitions or cost-negative?

**BENORTIWARI-A1 — "this is POWERPROJ-A1 / PWRSUM-A3 relabeled."** Partly fair: all
three evaluate a per-target oracle and solve a Hankel-type system. The genuine
distinction is the *recovered object* — power-projection returns the solution
*count* (minimal polynomial / trace form), power-sum returns a *C-finite recurrence*,
Ben-Or–Tiwari returns the *support monomials and coefficients* (the explicit
decompositions). But the red-team's deeper charge lands: **the binding cost is
`#evaluations × cost-per-evaluation`, and P1510-R1 already fixed cost-per-evaluation
at `Theta(r^2)`**; unless multipoint evaluation shares work across the `2r` Prony
nodes below `Theta(r^2)` each — which the compiler's structure almost certainly
forbids — the total is `Theta(r^3)`, identical to P1511-R2. **Verdict: near-certain
cost-negative; a clean scoped negative that closes the "evaluate-don't-materialize"
crack P1511-R2 left open. Not a disguised repeat (different recovered object) but
almost surely the same exponent.**

**LISTDECODE-B2 — "the RS source codes are already in P1509; this is circular."** The
red-team is right that P1509 supplies the code; the novelty is using the *decoding
algorithm* as the generator, not the labels as a verifier. The fatal charge is
sharper: **list-decoding only helps if the valid decompositions are an agreement set
of a low-degree codeword — i.e. they must be "close" in the code metric.** There is no
reason elliptic decompositions of one target cluster near a single low-degree
codeword; generically they are *independent* points, so the Johnson radius contains
`O(1)` of them (useless) or, forced wider, produces an `Omega(L)` list (no gain). The
`Omega(r^5)` atomizer bound (P1512-R1) does not directly apply (different model), so
the barrier is *decoding-radius geometry*, not algebra. **Verdict: not a repeat
(distinct primitive), but the decoding-radius obstruction is near-certain to make it
cost-negative; worth running only for the exact radius-coverage measurement, which is
itself a novel meter on the decomposition geometry.**

**ELLNET-C2 — "this is Mahler-B1 / DML-C1 / ECFG-001 in new clothes."** The mechanism
class is genuinely new (bilinear net recurrence, a task-brief seed never consumed),
so it is not a *relabeling*. But the red-team's structural kill is decisive and shared
with all three cited negatives: **the elliptic net is a divisibility sequence whose
index structure grows with the scalar, and locating a net zero is exactly the DLP.**
Net-value *testing* is cheap (`Theta(log|v|)`), but *finding* a zero has no sublinear
structure over `F_p` — the same periodicity/growth wall that killed Mahler and DML.
The only honest deliverable is the exact zero-density and location-exponent
measurement confirming the wall. **Verdict: not a disguised repeat, but near-certain
cost-negative by the same periodicity barrier; a POSSIBLY-NOVEL scoped negative that
finally consumes the EDS seed.**

**Cross-cutting red-team.** All three *attack* winners share the report's standing
pattern: the sparse-LA stage is not binding, so each lives or dies on the
relation/membership-generation exponent, and each faces a near-certain wall
(cubic-evaluation floor; decoding-radius geometry; net-zero periodicity). None is
projected to cross rho. Their value is: (a) BENORTIWARI closes the last "evaluate vs
materialize" crack under P1511-R2; (b) LISTDECODE yields a new decomposition-geometry
meter (radius coverage) regardless of outcome; (c) ELLNET consumes the final
untouched task-brief seed with an exact periodicity measurement. The three barriers
(LIFTING-D1, POLYCALC-D2, VCDIM-D3) are the higher-EV items: each imports a
lower-bound technology **no prior barrier used** (query-to-communication lifting;
Nullstellensatz/PC degree; VC-dimension shatter), and any one that reaches its
threshold would *close* a live gate (RT-1476 `alpha>=3/2` for LIFTING/POLYCALC;
RT-1472 `delta<=1/4` for VCDIM) rather than merely fail to open it.

---

## Claim discipline

Correctness is distinguished from performance throughout; candidate relations are
distinguished from verified ECDLP recovery. All twelve candidates are toy-scale,
heuristic, or restricted-model proposals; none is a demonstrated single-target
complete-cost sub-rho algorithm. **No break is claimed. The two live rho-crossing
surfaces `RT-1472` and `RT-1476` remain open.** A failed candidate here is a scoped
negative result under its tested model, never evidence that prime-field ECDLP cannot
be improved.
```
