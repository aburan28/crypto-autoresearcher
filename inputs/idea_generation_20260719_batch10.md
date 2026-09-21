# Idea Generation — Research Director — 2026-07-19 batch10 (report 18 / internal batch16)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Target:** a non-generic *single-target* prime-field ECDLP algorithm whose **complete** cost beats
Pollard-rho `O(sqrt(n))`. Toy correctness, a new coordinate system, a relation certificate, faster
preprocessing, or a solver improvement alone is NOT a breakthrough.
**Authorized scope:** generated toy curves, public benchmark instances, synthetic data only. No
wallets, production keys, accounts, or unauthorized systems.

---

## 0. Executive summary

This is the **18th** idea-generation report (internal batch16). The mechanism space remains
**saturated**: 17 prior reports (`ECFG-P1514–P1657`) span ~60 distinct mechanism lanes plus a
dedicated three-barrier arm every batch since batch8. The honest, highest-EV output continues to be
the **barrier arm**, not a new crossing claim — and this batch confirms that verdict by importing
**eight technology families absent from every prior report and both ledgers** (grep-verified, §2),
concentrated in two areas no prior batch touched: (i) **topological / combinatorial query and
set-system lower bounds** (evasiveness, hereditary discrepancy, sharp-threshold influences), and
(ii) **functorial / Hopf-algebraic representations of the symmetric summation tower** (FI-modules,
incidence-Hopf antipode, species).

Every attack candidate below carries a near-certain, *named* scoped-negative kill; the three barriers
(group D) each attack a live gate with a lower-bound technology no prior barrier used. One barrier —
**HEREDITARY-DISCREPANCY-BARRIER-D2** — is the sharpest new item this run: a Beck–Fiala degree-2
argument gives an *unconditional* `O(1)` discrepancy of the two-large-prime incidence system, and the
only surviving gap is the translation from coloring-discrepancy to occupancy-supply `δ`.

**No break is claimed. Both live gates RT-1472 and RT-1476 remain open.**

---

## 1. Required input review — inventory

Reviewed (both canonical ledgers by targeted extraction — each is multi-MB with very long records —
plus all secondary inputs and all 17 prior reports):

| Source | Extent | Notes |
|---|---|---|
| `research_ledger.md` (main) | 2.95 MB, 2478 record-lines; `P` / `ECFG-P` (frontier ~`ECFG-P1470` committed), `PO`, `ECFG-NR`, `ECFG-H`, `H` families | gates `P1472` / `P1476` verified live (both present in ledger) |
| `ecdlp_index_calculus_state/research_ledger.md` | 720 lines | IC-state frontier `P1509–P1513` |
| `research/non_generic_transfer_search_20260610.md` | transfer/decomposition channel search | same-field isogeny CLOSED; scalar Weil restriction NEGATIVE; twist = positive control only; **OPEN**: a Jacobian/correspondence engine not factoring through the elliptic x-line Semaev relation |
| `ecdlp_index_calculus_state/research_sources/bibliography.json` | 113 lines, 11 primary sources | Semaev'04, Gaudry'09, FPPR'12, Shantz–Teske'13, FHJRV'14, Kousidis–Wiemers'15, Karabina'15, Amadori–Pintore–Sala'17, McGuire–Mueller'17, Trimoska–Ionica–Dequen'20 |
| `research/idea_generation_2026071{7,8,9}*.md` | 17 reports (batch1–batch15 internal) | anti-dup corpus, `ECFG-P1514–P1657` |

**ID families covered:** `P` / `ECFG-P` (proposals), `PO` (PO-transfer program, runs through PO96z
Hom-PPAV / finite-Kummer-Cheon), `ECFG-NR` (scoped negatives), `H` / `ECFG-H` (hypotheses), `RT` /
`P147x` (rho-crossing gates), `MX`, `KN`, `RQ`, `IDEA`, `EV`, `DEC`, `TASK`. Entries reviewed: the full
committed ledger frontier + IC-state frontier + all 17 report cohorts (~144 prior report candidates,
`ECFG-P1514–P1657`).

### 1.1 Verified fixed context (extracted this run, not from memory)

- **Baseline B (rho):** Pollard rho + negation map `≈ 0.886·sqrt(n)` group ops, single target, `n ≈ p`.
  With `q ≈ L^5`, `r = |factor base| ≈ q^{1/5} = L`, rho `= L^{2.5}`.
- **RT-1472 (`P1472`, two-large-prime occupancy boundary):** cost exponent `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)`,
  minimized at `ℓ = 1/3` giving **2/3**; crossing below `1/2` requires large-prime **supply**
  `δ > 1/4` (relations per pair above baseline occupancy).
- **RT-1476 (`P1476`, m=5 membership backend boundary):** need query exponent `α < 3/2` (below
  `L^{1.5}`) with setup `≤ L^2` and random-like support, to give a complete five-term membership
  backend under the boundary.
- **IC-state closure chain:** `P1510-R1` verified per-target compiler `Θ(r)` rows at `Θ(r^3)=q^{3/5}`;
  `P1511-R2` closed product-circuit gcd/subres/Hasse (`r^3` leaves); **`P1512-R1` closed scalar-linear
  Chow atomizer at `Ω(r^5)` via `deg(det M) ≤ dim`** — only a **target-specialized nonlinear-circuit
  exception** survives; `P1513` open shared-common-norm (input quadratic, both norms cubic).
- **Sparse-LA stage `n^{2/5}=L^2` is NOT binding.** The relation/membership-**generation** stage is.

### 1.2 Target family (all candidates)

Ordinary `E/F_p`, `p` prime, prime-order subgroup `n ≈ p`, `q ≈ L^5`. **Excluded:** anomalous
(`trace = 1`), supersingular, small embedding degree (MOV/Frey–Rück range), small-CM-discriminant
special curves, non-prime order, and any twist/off-curve channel (positive control only).

---

## 2. Anti-duplication — novelty grounding (grep-verified this run)

The eight imported families and their keyword aliases were grepped across **both ledgers and all 17
reports**. **Zero matches** for every imported-family term:

`evasive` / `Kahn-Saks` / `Rivest-Vuillemin` (topological query LB), `hereditary discrepancy` /
`Spencer` / `Banaszczyk` / `Beck-Fiala` (combinatorial set-system discrepancy), `Friedgut` /
`sharp threshold` (influence / threshold-width), `hypercontractiv` / `small-set expansion`
(noise-operator smoothing), `FI-module` / `representation stability` (functorial symmetric tower),
`incidence Hopf` / `antipode` (Möbius-cancellation eliminant), `combinatorial species` / `umbral` /
`Sheffer` (labelled-structure EGF), `augmented indexing` (streaming/sketch information cost) — **all 0
files**.

One near-keyword, `Bourgain`, returns 4 files — but only in the **additive-combinatorics / sum-product
/ Gowers** sense already logged (batch3 `NILSEQ`, batch9 `PFR`). This report does **not** use
Bourgain's metric-embedding theorem; `metric embedding` and `distortion` are both 0-hit and are left
unused to avoid any overlap.

**Adjacency anchors (all confirmed *present*, used for honest distinction):** batch13 Huang
sensitivity (`SENSITIVITY-BLOCK`, spectral/query — A1/D1 distinct by using *topology* not spectra),
batch10 Raz elusive functions (`ELUSIVE-FUNCTIONS-D1`, *algebraic* image-elusiveness — distinct from
*topological* evasiveness), batch12 communication-rectangle discrepancy (`DISCREPANCY-CORRUPTION-A3` —
distinct from *combinatorial set-system* discrepancy), batch4 Wormald DE 2-core threshold
(`CORRELATED-PEEL-A3` — location, not *width/influence*), batch13 random-restriction avg-case
(`RANDOM-RESTRICTION-C1` — restriction axis, not *noise/hypercontractive* axis), batch11 analytic-rank
bias (`ANALYTIC-RANK-BIAS-B1` — log-bias, not hypercontractivity), batch8 GKZ D-module
(`GKZ-DMODULE-B2` — holonomic rank, not FI-functorial), batch5 Mahler automatic sequences
(`MAHLER-B1` — the C3 collapse anchor), batch12/13 cell-probe (`CELL-PROBE-CHRONOGRAM`,
`BORODIN-COOK` — distinct from *streaming/augmented-indexing* information cost).

**Pre-rejected as dups this run (do NOT re-propose):** crystalline/Cartier–Manin/Kedlaya (CLOSED,
batch2 D2); Kloosterman/character-sum bias (CLOSED, batch2 C3, Deligne); "poly-time sampler certifies
`δ>1/4`" role (CONSUMED, batch5 `MATUNION-A2` / batch11 `LORENTZIAN-C2`); slice-rank / Croot–Lev–Pach
(batch4 `SLICE-RANK-1`); tensor-network / tensor-train (batch1 `TT-B2`); Coppersmith / orthogonal
lattice (batch10 / batch3); Berkovich good-reduction skeleton (batch3 `SKEL-B3`); chip-firing /
sandpile / Baker–Norine (batch4 `SANDPILE-JACOBIAN`, batch15 `BAKER-NORINE-GONALITY`).

---

## 3. Candidates (12)

Notation: `r = L ≈ q^{1/5}`, `q ≈ n`, rho `= L^{2.5}`. "α" = membership-query exponent in `L`
(gate `< 3/2`); "δ" = large-prime supply exponent (gate `> 1/4`).

---

### Group A — conservative extensions of known work

---

## Candidate: EVASIVENESS-KSS-A1

### One-sentence mechanism
Exploit the **topological collapsibility (Euler-characteristic) obstruction** of the m=5 membership
complex to compute an exact decision-tree lower bound on the RT-1476 query cost `α`, importing the
Kahn–Saks–Sturtevant / Rivest–Vuillemin evasiveness machinery in place of the spectral
sensitivity chain used in batch13.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (evasiveness / Kahn–Saks / Rivest–Vuillemin: 0 corpus hits; batch13 `SENSITIVITY-BLOCK`
used Huang's *spectral* `s ≥ √deg`, and batch10 `ELUSIVE-FUNCTIONS` used Raz's *algebraic*
image-elusiveness — neither uses the *topological fixed-point / collapsibility* argument that defines
evasiveness).

### Semantic fingerprint
F(C) = (algebraic object: the boundary complex `Δ` of the monotone membership set-family
`{S ⊆ FB : some 5-completion of S sums to O}`; public operations: query "is factor-base element `e_i`
in the completing set"; hidden structure exploited: the `Z_p`-action collapsibility obstruction of
`Δ`; information discarded: the field-arithmetic *values*, keeping only incidence; information
retained: the monotone membership pattern; relation-generation primitive: adaptive decision tree over
`r` completions; compression primitive: none (this is a *meter*); rank mechanism: reduced homology
`H̃_*(Δ)` ≠ 0 ⇒ non-collapsible ⇒ evasive; descent mechanism: N/A (meter); dominant cost exponent:
the tree depth as a power of `r`).

### Nearest ledger entries
1. `SENSITIVITY-BLOCK-A1` (batch13) — same *goal* (RT-1476 `α` via query complexity) but Huang's
   spectral polynomial method; **distinction:** evasiveness is a *homological/topological* bound
   (`H̃_*(Δ)≠0`), provably incomparable to sensitivity (evasive functions can have low sensitivity).
2. `ELUSIVE-FUNCTIONS-D1` (batch10) — Raz's *algebraic* elusiveness of polynomial maps;
   **distinction:** that is a circuit-lower-bound for image-avoidance, not a decision-tree depth bound;
   different measure, different theorem.
3. `LIFTING-D1` (batch7) — query→communication lifting; **distinction:** lifting *transfers* a query
   bound to communication, it does not *produce* the query bound topologically.
4. `QUANTUM-ADVERSARY-SPAN-C1` (batch12) — query SDP; **distinction:** adversary bound is `Q` (quantum),
   evasiveness is deterministic `D`; `D ≥ Q^2` only, opposite regime.
5. `CERTIFICATE-DUAL-A2` (batch13) — certificate complexity `C`; **distinction:** `C` can be `√D` for
   evasive functions, so certificate does not detect evasiveness.

### Nearest literature
- Kahn, Saks, Sturtevant, *A topological approach to evasiveness* (Combinatorica 1984): monotone graph
  properties on `p^k` vertices are evasive via a `Z_p`-fixed-point argument. Claim: non-collapsibility
  ⇒ evasive. **Gap:** proven for *monotone graph properties* with a vertex-transitive symmetry group;
  the m=5 membership family is monotone but its symmetry group is `Aut(E)` acting on the factor base,
  which is *not* the required prime-power transitive action.
- Rivest–Vuillemin (1976): non-trivial monotone transitive Boolean functions have `D ≥ n/`polylog.
- Miller (2013), Kozlov *Combinatorial Algebraic Topology*: collapsibility algorithms for `Δ`.

### Target family
Ordinary `E/F_p`, prime order `n`; factor base = `x`-coordinates below bound `B ≈ L`. Excluded: the
degenerate factor bases with a non-transitive automorphism action (positive control uses a
random-support proxy).

### Full algorithmic path
1. **Factor-base construction:** `r = Θ(L)` low-`x` points, standard.
2. **Relation generation:** decision tree — given 4 fixed points, adaptively query factor-base elements
   for the 5th completing point that zeroes `f_5`.
3. **Witness extraction & verification:** a completing element is a verified relation iff `f_5 = 0`
   (exact, re-checked by the wrapper — Tier-0 certificate).
4. **Relation probability:** unchanged from the P1510 compiler (`Θ(r^{-2})` per random 4-tuple).
5. **Matrix dims/density/rank:** unchanged; this candidate only *meters* stage-2.
6. **Factor-log calibration:** unchanged.
7. **Individual log / descent:** unchanged; the meter does not touch descent.
8. **Offline/online:** the complex `Δ` and its collapsibility are computed **offline** once (`Θ(r)`
   simplices' homology); the online cost is the metered tree depth.
9. **Memory/parallelism:** `Δ` homology fits in `Õ(r)`; embarrassingly parallel over targets.

### Cost model
Setup: build `Δ`, compute `H̃_*(Δ)` in `Õ(r^ω)` **offline** (uncharged against online). Online: the
metered decision-tree depth `D(Δ)`. Evasiveness would give `D = Θ(r)` ⇒ `α = 1`. **This is the honest
problem:** `α = 1 < 3/2`, so a *positive* evasiveness result is **consistent with a crossing** and does
not by itself close RT-1476 as a barrier; the *weighted* Rivest–Vuillemin refinement would be needed to
push toward `3/2`, and is unproven here. As a **meter**, `α = 1` is a genuine improvement over the
`r^3` P1511-R2 floor only if the field-op cost per query is `O(1)` — but each membership query still
costs a `f_5` evaluation at `r^{1/2}` amortized, giving `α = 1.5` net, exactly the floor.
Compare: rho `L^{2.5}`; BSGS `L^{2.5}`; nearest IC baseline P1510 `r^3 = L^3`.

### Why the existing negative results do not already kill it
`P1512-R1` closes the *scalar-linear Chow* atomizer via `deg(det M) ≤ dim`; that is a *degree* bound on
an eliminant polynomial. Evasiveness is a *depth* bound on an adaptive query process and is provably
decoupled from polynomial degree (Boolean topology, not `F_p` algebra), so `deg(det)≤dim` does not
apply. It also avoids the spectral-sensitivity kill of batch13 because homology can be nonzero where
sensitivity is low.

### Likely fatal obstruction
The membership family's symmetry group is `Aut(E)`, not the prime-power transitive group KSS requires;
without transitivity the topological argument yields at most `α = 1` (linear), which is **below** the
`3/2` gate — so even a fully successful evasiveness proof reproduces the `L^{1.5}` floor rather than
crossing it. Meter, not crossing.

### Minimal falsifying experiment
Three toy sizes `p ∈ {≈2^{20}, ≈2^{26}, ≈2^{32}}`, ≥3 random ordinary prime-order curves each, seeds
`{1,2,3}`. Build `Δ` for `m=5` membership; compute reduced Euler characteristic `χ̃(Δ)` and, where
feasible, `H̃_*(Δ;Z_p)`. Positive control: a genuinely evasive monotone property (parity-of-triangles
proxy). Negative control: a non-evasive property (matches a cone). Measure: does `χ̃(Δ) ≠ 0` and does
the *field-op-weighted* depth scale as `r^{1.0}` or `r^{1.5}`?

### Quantitative promotion gate
Promote only if the **field-op-weighted** query exponent `α` is *measured* below `1.5` on all three
sizes with a monotone downward trend as `r` grows. Correctness of the homology computation alone does
NOT promote.

### Proof track
Theorem to establish: the m=5 membership complex `Δ_r` is non-`Z_p`-collapsible for infinitely many `r`,
and the field-op-weighted decision-tree depth is `Θ(r^{1.5-ε})` for some `ε>0`.

### Disproof track
Exhibit a cone point (a factor-base element in every completing set) ⇒ `Δ` collapsible ⇒ `α ≤ 1` with
`O(1)`-field-op queries ⇒ still `≥ 1.5` net, killing the crossing; or measure `χ̃(Δ)=0` at all sizes.

### Reproduction artifact
Contract `experiment_contract_p1658_evasiveness_membership_collapsibility.md`; implementation
`p1658_evasiveness_kss_membership.sage`; result `p1658_evasiveness_kss_membership.json`; audit
`p1658_evasiveness_kss_membership_audit.json`; ledger `ECFG-P1658`.

---

## Candidate: SPENCER-DISCREPANCY-A2

### One-sentence mechanism
Exploit the **hereditary combinatorial discrepancy** of the two-large-prime incidence system as an
exact ceiling on the RT-1472 supply `δ`, importing Spencer/Beck–Fiala/Banaszczyk set-system
discrepancy in place of the entropy (Shearer), coding-LP (Delsarte) and analytic (large-sieve) supply
meters of prior batches.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (hereditary discrepancy / Spencer / Beck–Fiala / Banaszczyk: 0 hits). **Distinct from
batch12 `DISCREPANCY-CORRUPTION-A3`**, which used *communication-complexity rectangle discrepancy*
(a 2-party protocol measure); combinatorial set-system discrepancy is a different quantity with a
different lower-bound theory (Roth `1/4`-power, determinant lower bound, `γ_2` upper bound).

### Semantic fingerprint
F(C) = (algebraic object: the `{0,1}` incidence matrix `A` of relations × large-prime-pairs; public
operations: select a sub-collection of relations; hidden structure exploited: bounded column degree
(each relation has exactly 2 large primes) and the arithmetic incidence pattern; information discarded:
the field values of small-prime parts; information retained: which pair each relation hits; relation
gen primitive: enrich by choosing a `±1` (keep/drop) coloring; compression: none (meter); rank
mechanism: `herdisc(A)` = max over submatrices of min-over-colorings of `‖Ax‖_∞`; descent: N/A;
dominant cost exponent: `δ` as controlled by `herdisc(A)/√(occupancy)`).

### Nearest ledger entries
1. `DISCREPANCY-CORRUPTION-A3` (batch12) — communication discrepancy; **distinction:** protocol vs
   set-system; the two "discrepancies" are unrelated quantities.
2. `SHEARER-D3` (batch8) — entropy submodular supply ceiling; **distinction:** entropy bounds *count*,
   discrepancy bounds *coloring imbalance*; Beck–Fiala gives an `O(1)` bound entropy cannot.
3. `DELSARTE-LP-A2` (batch8) — coding-LP supply; **distinction:** LP-dual of a code, not a coloring.
4. `LARGE-SIEVE-SUPPLY-A1` (batch14) — analytic `L^2` inequality; **distinction:** Fourier/modulus
   average, not a combinatorial `±1` balance.
5. `MATUNION-A2` (batch5) — matroid-union independence; **distinction:** matroid rank, not discrepancy.

### Nearest literature
- Spencer, *Six standard deviations suffice* (1985): `disc(H) = O(√(n))` for `n` sets on `n` points.
- Beck–Fiala (1981): degree-`t` set systems have `disc ≤ 2t−1`. **For the 2-large-prime graph `t=2`,
  giving `disc ≤ 3 = O(1)` unconditionally** — the load-bearing fact behind D2.
- Lovász–Spencer–Vesztergombi (1986): `herdisc` transference; `γ_2`-norm upper bound (Matoušek–Nikolov).
- Banaszczyk (1998): vector-balancing `O(√log n)`.

### Target family
As §1.2; the incidence system is the honest (no fabricated-advice) two-large-prime graph at
`B = n^{1/5}`.

### Full algorithmic path
1. FB construction: standard; large primes in `(B, B^2]`.
2. Relation gen: honest 2-LP relations; build `A` (relations × pairs).
3. Witness/verification: each relation Tier-0 re-checked.
4. Relation probability: baseline occupancy fixes the null `δ`.
5. Matrix: `A` has column degree 2; row count `Θ(r^{1+2δ})`.
6. Calibration: enrichment = a keep/drop selection; the achievable extra supply is bounded by
   `herdisc(A)`.
7. Descent: N/A (supply meter feeding the RT-1472 exponent).
8. Offline/online: `herdisc(A)` estimated offline via the `γ_2` SDP relaxation.
9. Memory/parallelism: `A` is `Θ(r)`-sparse.

### Cost model
The RT-1472 exponent is `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)`; a crossing needs `δ > 1/4`. The claim to measure:
the enrichment achievable above baseline occupancy is `Θ(herdisc(A)/√occupancy)`. Beck–Fiala gives
`herdisc(A) = O(1)` ⇒ the enrichment is `o(√occupancy)` ⇒ `δ ≤ 1/4`. If true this is a *ceiling*, not
a crossing. Compare: rho `L^{2.5}`, RT-1472 optimum `L^{2/3·2.5}=L^{5/3}`.

### Why the existing negative results do not already kill it
Prior δ-ceilings (Lang–Weil count, Shearer entropy, large-sieve inequality) all bound the *number* of
relations; none bounds the *balanced-selection* structure that a two-large-prime *enrichment* actually
exploits. Discrepancy is the first meter matched to the selection operation itself.

### Likely fatal obstruction
The translation "supply `δ` = `herdisc/√occupancy`" is heuristic: `δ` measures raw pair-occupancy, not
signed-coloring balance. If enrichment gains come from *unsigned* pair multiplicity (many relations per
pair, no cancellation), discrepancy is silent and the meter is vacuous.

### Minimal falsifying experiment
Three sizes as above; build `A`; compute the `γ_2`/SDP `herdisc` upper bound and a determinant lower
bound; measure the *actually achieved* enrichment `δ̂` from an honest 2-LP relation harvest. Positive
control: a random degree-2 system (Beck–Fiala tight). Negative control: a Hadamard-like high-discrepancy
system. Gate check: does `δ̂` track `herdisc/√occupancy`?

### Quantitative promotion gate
Promote to a *ceiling* only if measured `δ̂ ≤ 1/4` across all three sizes AND `herdisc(A) = O(1)` is
confirmed; promote to D2 barrier only if the `herdisc → δ` translation is proven (see D2).

### Proof track
Theorem: the honest 2-LP incidence matrix has `herdisc = O(1)` (Beck–Fiala) and the maximal
enrichment supply is `O(herdisc·log r)` ⇒ `δ ≤ 1/4`.

### Disproof track
Exhibit an arithmetic 2-LP family with `δ̂ > 1/4` despite `O(1)` discrepancy ⇒ the translation is false
⇒ meter dead.

### Reproduction artifact
Contract `experiment_contract_p1659_hereditary_discrepancy_two_large_prime.md`; impl
`p1659_spencer_discrepancy.sage`; result/audit JSON pair; ledger `ECFG-P1659`.

---

## Candidate: SHARP-THRESHOLD-FRIEDGUT-A3

### One-sentence mechanism
Exploit **Friedgut's junta / sharp-threshold theorem** on the two-large-prime supply function to decide
whether the RT-1472 `δ`-window is a *sharp* threshold (no exploitable intermediate plateau, symmetric)
or a *coarse* one (junta ⇒ few-coordinate exploitable structure), importing the influence/threshold-width
machinery no prior batch used.

### Status
HEURISTIC

### Novelty classification
LEDGER-NEW (Friedgut / sharp threshold / influences: 0 hits). **Distinct from batch4
`CORRELATED-PEEL-A3`**, which used the Wormald differential-equation method to locate the 2-core
*threshold position*; this candidate measures the threshold *width/sharpness* via total influence, a
different theorem (Friedgut–Kalai symmetry ⇒ sharpness; Bourgain–Friedgut junta ⇒ coarseness).

### Semantic fingerprint
F(C) = (algebraic object: the monotone supply property `P_B` = "enough 2-LP relations exist at bound
`B`" as a function on the product space of prime inclusions; operations: vary `B`; hidden structure: the
symmetry group of the arithmetic incidence; discarded: relation values; retained: threshold sharpness;
relation-gen primitive: the threshold crossing; compression: none; rank mechanism: total influence
`I(P_B)` at the critical `B`; descent: N/A; dominant exponent: threshold width Δ`B`).

### Nearest ledger entries
1. `CORRELATED-PEEL-A3` (batch4) — 2-core threshold *location* (Wormald DE); **distinction:** width vs
   location; Friedgut bounds `ΔB`, Wormald bounds `B_c`.
2. `SHARP` supply arm batch14 (`LARGE-SIEVE`) — analytic; **distinction:** influences vs `L^2` sieve.
3. `CONTAINER-CEILING-A3` (batch9) — hypergraph container; **distinction:** container counts
   independent sets, not threshold sharpness.
4. `HDX-COBOUNDARY-A2` (batch6) — coboundary expansion; **distinction:** cohomological, not influence.
5. `LDLR-DELTA-METER-A3` (batch11) — low-degree detectability; **distinction:** detection vs threshold.

### Nearest literature
- Friedgut (1998), *Boolean functions with low average sensitivity depend on few coordinates*; the
  sharp-threshold criterion.
- Friedgut–Kalai (1996): symmetric monotone properties have sharp thresholds.
- Bourgain's appendix to Friedgut (1999): coarse threshold ⇒ local (junta-like) cause.

### Target family
As §1.2; monotone supply property over the honest prime-inclusion product space.

### Full algorithmic path
1–5 as SPENCER-DISCREPANCY-A2 (shared incidence/supply setup).
6. Calibration: estimate total influence `I(P_B)` and threshold width from a Monte-Carlo sweep in `B`.
7. Descent: N/A.
8. Offline/online: influence estimated offline.
9. Memory/parallelism: trivial.

### Cost model
Meter only. If Friedgut–Kalai symmetry holds ⇒ sharp threshold ⇒ the supply jumps from `δ<1/4` to
saturated with **no `δ∈(1/4, ½)` plateau** ⇒ RT-1472 window is empty (feeds D3). If coarse ⇒ Bourgain
junta ⇒ a few large-prime coordinates dominate ⇒ an exploitable low-dimensional enrichment (the *only*
positive branch this candidate offers). Compare vs rho as A2.

### Why the existing negative results do not already kill it
Prior batches metered supply *magnitude*; none metered the *threshold geometry*. A coarse threshold is
the precise loophole under which a `δ>1/4` window could exist — and Friedgut is the exact tool that
detects it.

### Likely fatal obstruction
Friedgut–Kalai symmetry almost certainly applies (the 2-LP property is invariant under prime
relabeling) ⇒ sharp threshold ⇒ **no plateau** ⇒ negative (feeds D3), with the coarse-threshold
positive branch near-certainly excluded.

### Minimal falsifying experiment
Three sizes; sweep `B` finely; estimate `I(P_B)` and width `ΔB`. Positive control: a coarse-threshold
property (biased-majority proxy). Negative control: a sharp-threshold property (connectivity proxy).
Gate: is `ΔB = o(B_c)` (sharp) or `Θ(B_c)` (coarse)?

### Quantitative promotion gate
Promote the positive branch only if measured coarse threshold AND a junta of `≤ r^{ε}` primes carries a
measured `δ̂ > 1/4`. Otherwise record the sharp-threshold negative (D3).

### Proof track
Theorem: the honest 2-LP supply property is symmetric ⇒ (Friedgut–Kalai) has a sharp threshold ⇒ no
`δ>1/4` window.

### Disproof track
Measure a coarse threshold with an exploitable junta ⇒ opens a genuine enrichment lane.

### Reproduction artifact
Contract `experiment_contract_p1660_sharp_threshold_two_large_prime.md`; impl
`p1660_sharp_threshold_friedgut.sage`; result/audit JSON; ledger `ECFG-P1660`.

---

### Group B — genuine representation changes

---

## Candidate: FI-MODULE-STABILITY-B1

### One-sentence mechanism
Represent the **tower of symmetrized summation polynomials** `{f̃_m}_{m≥2}` as an **FI-module**
(functor from finite sets with injections), so that if its multiplicities are representation-stable the
m=5 eliminant admits a *uniform, m-independent* generating description whose complexity is the stable
degree — a functional provably **outside** the `deg(det M) ≤ dim` bound that closed the scalar-linear
Chow atomizer (P1512-R1).

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (FI-module / representation stability: 0 hits; no ECDLP prior art located). Distinct
from batch8 `GKZ-DMODULE-B2` (holonomic rank of a *fixed* polytope) and batch12
`IMMANANT-INTERPOLATION-B2` (character-weighted determinant of a *fixed* matrix) — FI-modules track the
*asymptotic in `m`* representation-theoretic multiplicities, a different object.

### Semantic fingerprint
F(C) = (algebraic object: the FI-module `m ↦ (coordinate ring / syzygy module of the symmetrized
Semaev ideal `I_m`)`, an `S_m`-representation sequence; operations: the injection-induced transition
maps `I_m → I_{m+1}`; hidden structure exploited: representation stability (finitely generated FI-module
⇒ multiplicities eventually polynomial in `m`); information discarded: the `m`-specific coordinates;
information retained: the stable irreducible pattern; relation-gen primitive: read off the m=5
generators from the stable presentation; compression primitive: FI-generation degree (the "stable
range"); rank mechanism: the FI-module's generation degree `≪` naive `dim`; descent mechanism: the
stable presentation yields a uniform per-target solver; dominant exponent: stable-range power of `r`).

### Nearest ledger entries
1. `GKZ-DMODULE-B2` (batch8) — A-hypergeometric holonomic rank; **distinction:** GKZ is a single
   `D`-module for fixed exponents; FI tracks the `m→∞` functor. Different category.
2. `IMMANANT-INTERPOLATION-B2` (batch12) — `d_λ` character determinant; **distinction:** a fixed
   functional, not a stabilizing sequence.
3. `SCHURPLETHYSM-B3` (batch7) — plethysm expansion; **distinction:** plethysm is one decomposition,
   FI is the stabilization *of a sequence* of them.
4. `NONCOMMUTATIVE-RANK-OPSCALING-B2` (batch11) — nc-rank; **distinction:** free-skew-field rank of one
   pencil, not a representation-stable tower.
5. `SYZYGY-REGULARITY-B2` (batch4) — Betti table of the factor-base ideal; **distinction:** a single
   resolution, whereas FI-modules bound the *whole family's* regularity uniformly (Church–Ellenberg
   Noetherianity).

### Nearest literature
- Church–Ellenberg–Farb, *FI-modules and stability for representations of symmetric groups* (Duke
   2015): finitely generated FI-modules over a Noetherian ring have eventually-polynomial dimension and
   bounded generation degree.
- Church–Ellenberg, *Homology of FI-modules* (2017): regularity/generation-degree bounds.
- Sam–Snowden, twisted commutative algebras: Gröbner theory of FI. **Gap:** whether the *summation*
  ideal sequence `I_m` is a finitely generated FI-module — the transition map "add a point to the sum"
  is not obviously an FI-morphism (adding a point is a group-law merge, not a free injection of a label).

### Target family
As §1.2; the symmetric summation tower `f̃_m` for `m = 2,…,5` and its stabilization proxy up to `m ≈ 8`.

### Full algorithmic path
1. FB construction: standard.
2. Relation gen: from the *stable FI-presentation*, instantiate the m=5 generators uniformly per target.
3. Witness/verification: Tier-0 re-check of each produced relation.
4. Relation probability: unchanged if the presentation is faithful.
5. Matrix: the point is that the generator count is the FI stable degree, not `r^5`.
6. Calibration: standard.
7. Descent: the same stable presentation drives individual-log descent (uniform per target).
8. Offline/online: the FI-presentation is computed **once offline**; online instantiation is cheap iff
   the stable degree is sub-`r^{1.5}`.
9. Memory/parallelism: presentation is `m`-independent, `Õ(1)` in `r` if stable.

### Cost model
The whole bet: does the FI generation degree of `I_5` (drawn from the stabilized tower) give a
membership backend at `α < 3/2`? If the tower is a f.g. FI-module with generation degree `d`, the
per-target eliminant instantiation costs `Θ(r^{c(d)})` with `c(d)` the stable-degree exponent. **Only a
crossing if `c(d) < 1.5`.** Compare: P1512-R1 floor `Ω(r^5)`, P1511-R2 `r^3`, rho `L^{2.5}`.

### Why the existing negative results do not already kill it
`P1512-R1`'s `deg(det M) ≤ dim` bounds the degree of a *single* eliminant determinant. FI-generation
degree is an *asymptotic-in-`m`* invariant of the *sequence* of ideals; the Church–Ellenberg
Noetherianity that would bound it is not a determinant-degree statement, so `deg(det)≤dim` does not
close it. This is the sharpest genuinely-new attack on the surviving nonlinear-circuit exception since
batch11 nc-rank.

### Likely fatal obstruction
The summation tower almost certainly is **not** a finitely generated FI-module: "adding a summand" is a
group-law composition, not a free label injection, so the FI-functoriality axioms fail — and even if a
weaker (e.g. `FI`-`#` or `VIC`) structure holds, the stable range is plausibly `Θ(m)` giving generation
degree `Θ(r)` per coordinate ⇒ `Θ(r^{≥3})`, reproducing the floor. Cubic irreducibility of each `f_m`
(P1513 context) further blocks stabilization.

### Minimal falsifying experiment
Three sizes; compute the `S_m`-decomposition of `(I_m)_d` for `m = 2..8` at low degrees `d`; test
whether multiplicities are eventually polynomial in `m` (stability) and estimate the generation degree.
Positive control: a known f.g. FI-module (e.g. the FI-module of the `m`-point configuration space
cohomology). Negative control: a non-f.g. sequence. Gate: does generation degree stay bounded and yield
`c(d) < 1.5`?

### Quantitative promotion gate
Promote only if (a) representation stability is *measured* (polynomial multiplicities) AND (b) the
resulting per-target membership exponent is *measured* `< 1.5` on all three sizes.

### Proof track
Theorem: the symmetrized summation ideal sequence is a finitely generated FI-module (or `FI#`) with
generation degree `d` giving `c(d) < 3/2`.

### Disproof track
Show the transition maps are not FI-morphisms, or exhibit unbounded generation degree ⇒ candidate dead.

### Reproduction artifact
Contract `experiment_contract_p1661_fi_module_summation_tower.md`; impl `p1661_fi_module_stability.sage`;
result/audit JSON; ledger `ECFG-P1661`.

---

## Candidate: INCIDENCE-HOPF-ANTIPODE-B2

### One-sentence mechanism
Represent the m=5 eliminant via the **antipode of the incidence Hopf algebra** of the summation poset,
seeking massive Möbius sign-cancellation (Benedetti–Sagan style) that computes membership with fewer
than `r^5` surviving terms — a cancellation-driven functional distinct from any determinant.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (incidence Hopf / antipode: 0 hits). Distinct from batch8 `CLUSTER-MUTATION-B3` (cluster
algebra), batch4 `SYZYGY-REGULARITY-B2` (free resolution), and the additive-combinatorics inclusion–
exclusion used implicitly in occupancy counts.

### Semantic fingerprint
F(C) = (algebraic object: the incidence Hopf algebra `H` of the poset of partial summation states of 5
marked points; operations: coproduct = split a partial sum, product = merge; hidden structure: the
antipode `S` and its cancellation; discarded: nothing at the algebra level; retained: the full membership
functional as `S`-evaluation; relation-gen primitive: evaluate `S(f_5-state)`; compression primitive:
Möbius/antipode sign cancellation; rank mechanism: number of *surviving* (post-cancellation) terms;
descent: the antipode formula reused per target; dominant exponent: surviving-term count as a power of
`r`).

### Nearest ledger entries
1. `CLUSTER-MUTATION-B3` (batch8) — Hopf-adjacent recurrence; **distinction:** mutation periodicity vs
   antipode cancellation.
2. `SYZYGY-REGULARITY-B2` (batch4) — homological cancellation in a resolution; **distinction:** free
   resolution differentials vs Hopf antipode; different cancellation source.
3. `IMMANANT-INTERPOLATION-B2` (batch12) — signed character sum; **distinction:** immanant is a fixed
   determinant-family, antipode is a poset Möbius sum.
4. `ELL-ADIC-BETTI-MILNOR-THOM-C2` (batch12) — Betti/branch count; **distinction:** topological count,
   not Hopf cancellation.
5. `APOLARITY-ATOMIZER-A2` (batch4) — catalecticant atomizer; **distinction:** apolarity pairing, not
   coalgebra antipode.

### Nearest literature
- Schmitt, *Incidence Hopf algebras* (1994); Benedetti–Sagan, *cancellation-free antipode formulas*
   (2017). Claim: for many posets the antipode has a cancellation-free (few-term) form. **Gap:** whether
   the *summation* poset is such a poset, or is the Boolean lattice (standard inclusion–exclusion,
   `O(2^5)` per relation but `Θ(r^5)` relations — no `r`-direction cancellation).

### Target family
As §1.2.

### Full algorithmic path
1. FB: standard. 2. Relation gen: evaluate antipode-compiled membership per 4-tuple. 3. Verify: Tier-0.
4. Probability: unchanged. 5. Matrix: unchanged; meters term count. 6. Calibration: standard. 7. Descent:
antipode reused. 8. Offline/online: antipode formula derived offline. 9. Memory: `O(1)` per relation.

### Cost model
If the summation poset is Boolean, `S` = inclusion–exclusion ⇒ `O(2^m)=O(1)` terms per relation but the
relation set is still `Θ(r^5)` ⇒ reproduces the P1512 floor. A crossing needs cancellation in the
*`r`-direction* (across factor-base choices), which the antipode does not obviously provide. Compare vs
rho `L^{2.5}`.

### Why the existing negative results do not already kill it
The antipode is a *coalgebra* operation, not a polynomial determinant, so `deg(det)≤dim` (P1512-R1)
does not bound its surviving-term count. It is the first coalgebra-cancellation representation tried.

### Likely fatal obstruction
The summation poset is (near-certainly) the Boolean subset lattice ⇒ antipode = standard signed
inclusion–exclusion with cancellation only in the `2^m` direction (`m=5` = constant), never in the `r`
direction that dominates cost ⇒ reproduces `Θ(r^5)`.

### Minimal falsifying experiment
Three sizes; construct the summation poset for 5 marked points; compute its antipode symbolically; count
surviving terms as a function of `r`. Positive control: a poset with known cancellation-free antipode
(e.g. the partition lattice). Negative control: Boolean lattice (no `r`-cancellation). Gate: surviving
terms `o(r^{1.5})`?

### Quantitative promotion gate
Promote only if surviving-term count is *measured* `o(r^{1.5})` across all three sizes.

### Proof track
Theorem: the summation poset has a cancellation-free antipode with `o(r^{1.5})` surviving terms.

### Disproof track
Show the poset is Boolean / antipode has `Θ(r^5)` surviving terms.

### Reproduction artifact
Contract `experiment_contract_p1662_incidence_hopf_antipode_summation.md`; impl
`p1662_incidence_hopf_antipode.sage`; result/audit JSON; ledger `ECFG-P1662`.

---

## Candidate: COMBINATORIAL-SPECIES-B3

### One-sentence mechanism
Represent labelled 5-point summation configurations as a **combinatorial species** and compute relation
counts via species composition / cycle-index series, seeking a generating-function shortcut to the m=5
witness count.

### Status
OPEN

### Novelty classification
LEDGER-NEW (combinatorial species: 0 hits) but **flagged thin** — near-adjacent to batch8
`GKZ-DMODULE-B2` (mixed-volume count) and batch7 `SCHURPLETHYSM-B3` (symmetric-function expansion). The
composition operation is genuinely new; the *count it produces* is likely identical to BKK mixed volume.

### Semantic fingerprint
F(C) = (algebraic object: the species `F` of labelled summation trees, EGF `F(x)`; operations: species
sum/product/composition; hidden structure: automorphisms of the summation labelling; discarded:
geometry; retained: labelled count; relation-gen primitive: extract `[x^n] F`; compression: cycle-index
symmetry reduction; rank mechanism: N/A; descent: none provided; dominant exponent: the EGF growth
rate).

### Nearest ledger entries
1. `GKZ-DMODULE-B2` (batch8) — mixed-volume branch count; **distinction:** analytic species vs holonomic
   `D`-module; likely equal counts.
2. `SCHURPLETHYSM-B3` (batch7) — plethysm; **distinction:** species composition ≈ plethysm on cycle
   indices — this is the adjacency risk.
3. `MOTIVIC-B3` (batch5) — arc-space measure; **distinction:** motivic vs enumerative.
4. `ELL-ADIC-BETTI-C2` (batch12) — Betti count; **distinction:** topological vs species EGF.
5. `NEWTON-OKOUNKOV-B3` (batch9) — graded filtration count; **distinction:** valuation vs EGF.

### Nearest literature
- Joyal, *Une théorie combinatoire des séries formelles* (1981); Bergeron–Labelle–Leroux, *Combinatorial
   Species and Tree-like Structures*. **Gap:** species give *counts*, not a *descent* path; no route from
   an EGF to individual-logarithm recovery.

### Target family
As §1.2.

### Full algorithmic path
1. FB: standard. 2. Relation gen: species-derived count only. 3. Verify: N/A at count level. 4.
Probability: from EGF coefficient. 5–7. **MISSING** — no matrix, calibration, or descent path.
8–9. Offline EGF derivation.

**INCOMPLETE** (stages 5–7 absent — no target-descent route).

### Cost model
Not applicable beyond a count; provides no `α` or `δ` improvement, hence no rho comparison. Cost-neutral.

### Why the existing negative results do not already kill it
It is a counting/representation reframing untried in the ledger; but counting is not the binding stage.

### Likely fatal obstruction
Species composition reproduces the BKK/mixed-volume count already known (batch8), and offers no
descent — INCOMPLETE by construction.

### Minimal falsifying experiment
Verify at three toy sizes that `[x^n]F` matches the measured 5-relation count; then confirm no descent
map exists. Positive control: a species with known EGF (rooted trees). Negative control: none needed.

### Quantitative promotion gate
Cannot promote without a *new* descent stage; recorded as INCOMPLETE unless a species-to-descent map is
exhibited.

### Proof track
N/A (no complexity claim).

### Disproof track
Confirm count = BKK volume ⇒ demote.

### Reproduction artifact
Contract `experiment_contract_p1663_combinatorial_species_summation.md`; impl
`p1663_combinatorial_species.sage`; result/audit JSON; ledger `ECFG-P1663`.

---

### Group C — high-risk speculative mechanisms

---

## Candidate: HYPERCONTRACTIVITY-SSE-C1

### One-sentence mechanism
Treat the m=5 membership indicator `1[f_5 = 0]` as a function on `(F_p)^{coords}` and, **if** it is a
low-influence / small-set-expanding ("smooth") function, apply the noise operator `T_ρ` to build a
*hypercontractive-smoothed average-case sampler* that emits genuine relations in sub-`L^{1.5}` on a
`1−o(1)` fraction of targets, with rho fallback on the rest.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (hypercontractivity / small-set expansion: 0 hits). Distinct from batch13
`RANDOM-RESTRICTION-C1` (Håstad *restriction* shrinkage — a different randomization axis) and batch11
`ANALYTIC-RANK-BIAS-B1` (log-bias of the tensor, not the noise operator / `(2,q)`-hypercontractive
inequality).

### Semantic fingerprint
F(C) = (algebraic object: `g = 1[f_5=0]: F_p^k → {0,1}` with its `F_p`-Fourier/character expansion;
operations: apply `T_ρ`, sample from the smoothed distribution; hidden structure: small-set expansion
(low `(2,4)`-hypercontractivity ratio) of the level sets; discarded: exact membership on an `o(1)`
target fraction; retained: average-case membership on `1−o(1)`; relation-gen primitive: noise-smoothed
importance sampling; compression: spectral concentration on low levels; rank mechanism: N/A; descent:
per-target smoothed sampler + rho fallback; dominant exponent: `α_avg < 1.5` on the good fraction).

### Nearest ledger entries
1. `RANDOM-RESTRICTION-C1` (batch13) — avg-case backend + rho fallback; **distinction:** noise vs
   restriction; hypercontractivity smooths, restriction fixes coordinates.
2. `PROBABILISTIC-POLY-C3` (batch8) — randomized backend; **distinction:** probabilistic *degree*, not
   noise smoothing.
3. `ANALYTIC-RANK-BIAS-B1` (batch11) — tensor log-bias; **distinction:** bias of one tensor vs
   hypercontractive ratio of the indicator.
4. `LDLR-DELTA-METER-A3` (batch11) — low-degree likelihood ratio; **distinction:** detection meter, not
   a sampler.
5. `SPECTRAL-INDEPENDENCE-SAMPLER-C2` (batch14) — Glauber sampler; **distinction:** spectral independence
   of a Gibbs measure, not hypercontractivity of a fixed indicator.

### Nearest literature
- O'Donnell, *Analysis of Boolean Functions* (hypercontractivity, `(2,q)`-norms, small-set expansion).
- Bonami–Beckner over `Z_p^k`; Keevash–Long, hypercontractivity for global functions. **Gap:** algebraic
   indicators of high-codimension varieties are typically *high-influence* along the constraint
   directions ⇒ not small-set-expanding.

### Target family
As §1.2.

### Full algorithmic path
1. FB: standard. 2. Relation gen: noise-smoothed sampler on the good target fraction; rho on the rest.
3. Verify: Tier-0 re-check (avoids false positives from smoothing). 4. Probability: measured hit rate
under `T_ρ`. 5. Matrix: unchanged. 6. Calibration: standard. 7. Descent: smoothed sampler + rho
fallback; **complete-cost must include the fallback fraction**. 8. Offline/online: spectral profile
estimated offline; sampler online. 9. Memory: `Õ(r)`.

### Cost model
Complete cost = `f·L^{α_avg} + (1−f)·L^{2.5}` where `f = 1−o(1)`. A crossing needs `α_avg < 1.5` AND
`(1−f)·L^{2.5} = o(L^{2.5})`, i.e. the fallback fraction `o(1)`. Compare vs rho `L^{2.5}`, floor
`L^{1.5}`.

### Why the existing negative results do not already kill it
`P1512-R1` (degree) and `P1511-R2` (product-circuit) bound *worst-case exact* backends; a
noise-smoothed *average-case* backend on a `1−o(1)` fraction is a different regime (as batch13 argued
for restriction) and is not covered by any exact-degree floor.

### Likely fatal obstruction
Self-defeating in the batch13 pattern: the membership indicator of a codimension-1 variety has a
**heavy-influence junta** along the algebraic constraint direction, so its `(2,4)`-hypercontractive
ratio is large ⇒ `T_ρ` provides no concentration ⇒ `α_avg` stays at the `L^{1.5}` floor. Small-set
expansion fails precisely because the constraint is rigid.

### Minimal falsifying experiment
Three sizes; estimate the level-`k` Fourier weight and total influence of `g` over `F_p`; measure the
smoothed sampler hit-rate vs `ρ`. Positive control: a genuinely smooth (low-influence) indicator.
Negative control: a rigid high-influence indicator (a linear equation). Gate: does the smoothed sampler
achieve `α_avg < 1.5` on `1−o(1)` of targets?

### Quantitative promotion gate
Promote only if measured *complete* cost (smoothed good fraction + rho fallback) trends below `L^{2.5}`
with a fitted `α_avg < 1.5` across all three sizes.

### Proof track
Theorem: `g` is small-set-expanding (bounded `(2,4)` ratio) ⇒ `T_ρ` concentrates ⇒ `α_avg < 3/2`.

### Disproof track
Measure heavy influence along the constraint ⇒ no smoothing ⇒ candidate dead.

### Reproduction artifact
Contract `experiment_contract_p1664_hypercontractivity_sse_backend.md`; impl
`p1664_hypercontractivity_sse.sage`; result/audit JSON; ledger `ECFG-P1664`.

---

## Candidate: STREAMING-SKETCH-C2

### One-sentence mechanism
Maintain an `F_p`-linear **sketch** of the factor base (AMS / augmented-indexing style) and answer m=5
membership by a sketch query, hoping the sublinear sketch size yields a sub-`L^{1.5}` online backend.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (augmented indexing / streaming sketch: 0 hits). Distinct from batch12
`CELL-PROBE-CHRONOGRAM-D1` and batch13 `BORODIN-COOK-TIMESPACE-D3` — those are *dynamic/branching-program
time-space* lower bounds; the streaming information-cost model (one-pass, augmented indexing) is a
different communication regime.

### Semantic fingerprint
F(C) = (algebraic object: a linear sketch `Sx` of the factor-base indicator vector `x`; operations:
update, query; hidden structure: linearity of `f_5` membership under the sketch map; discarded: exact
positions; retained: an approximate membership signature; relation-gen primitive: sketch query;
compression primitive: dimension reduction `S`; rank mechanism: sketch rank; descent: per-target sketch
query; dominant exponent: sketch size × query cost).

### Nearest ledger entries
1. `CELL-PROBE-CHRONOGRAM-D1` (batch12) — dynamic cell probe; **distinction:** streaming one-pass vs
   dynamic updates.
2. `BORODIN-COOK-TIMESPACE-D3` (batch13) — branching-program T·S; **distinction:** multi-output offline
   vs one-pass online.
3. `DIRECTSUM-INFO-A2` (batch11) — internal information direct-sum; **distinction:** direct-sum over a
   batch, not one-pass streaming.
4. `DEQUANTIZED-SAMPLING-C1` (batch10) — sample-and-query; **distinction:** stable-rank sampling, not a
   linear sketch.
5. `RIGIDITY-A1` (batch8) — matrix rigidity of the eval matrix; **distinction:** rigidity vs sketch
   dimension.

### Nearest literature
- Alon–Matias–Szegedy (1996), linear sketches; Miltersen–Nisan–Safra–Wigderson, *augmented indexing*
   communication lower bound. **Gap:** augmented indexing lower-bounds the sketch at `Ω(r)` bits for
   exact membership.

### Target family
As §1.2.

### Full algorithmic path
1. FB: standard. 2. Relation gen: sketch-query membership. 3. Verify: Tier-0 (sketch is approximate;
must re-check). 4. Probability: sketch collision rate. 5. Matrix: unchanged. 6. Calibration: standard.
7. Descent: per-target sketch query + re-check. 8. Offline/online: `S` built offline, sketch online.
9. Memory: sketch size `s`.

### Cost model
Augmented-indexing information cost is `Ω(r)` bits per exact membership target ⇒ sketch size `s=Ω(r)`
and query `Ω(r)`; combined with the `f_5` re-check the online exponent stays `≥ 1.5`. **Self-defeating
as an algorithm:** the AI lower bound *is* the barrier (feeds a streaming-space D-argument), not a
crossing. Compare vs rho `L^{2.5}`.

### Why the existing negative results do not already kill it
No prior candidate used the *one-pass streaming* information-cost model; it is a genuinely new
communication regime even though its verdict is negative.

### Likely fatal obstruction
Augmented indexing forces `Ω(r)` sketch bits per target for exact 5-point membership ⇒ no sublinear
online backend ⇒ `α ≥ 1.5`; the value is the lower bound, not the sketch.

### Minimal falsifying experiment
Three sizes; build linear sketches of increasing size; measure exact-membership recall vs sketch size;
fit the size needed for `1−o(1)` recall. Positive control: a sparse vector recoverable by a small sketch.
Negative control: a dense uniform vector (`Ω(r)` sketch). Gate: sub-`r` sketch with `1−o(1)` exact
recall?

### Quantitative promotion gate
Promote (as an *algorithm*) only if a sketch of size `o(r)` gives `1−o(1)` exact-membership recall with
online query `o(L^{1.5})` — near-certainly impossible; otherwise record the streaming lower bound.

### Proof track
Theorem: an `o(r)` linear sketch answers 5-point membership at `α<3/2`.

### Disproof track
Augmented-indexing reduction ⇒ `Ω(r)` sketch ⇒ candidate dead (feeds a barrier).

### Reproduction artifact
Contract `experiment_contract_p1665_streaming_sketch_membership.md`; impl
`p1665_streaming_sketch.sage`; result/audit JSON; ledger `ECFG-P1665`.

---

## Candidate: UMBRAL-SHEFFER-C3

### One-sentence mechanism
Represent the multiplication-by-`k` map `x([k]P)` via an **umbral / Sheffer-sequence linear functional
recurrence**, hoping a finite-state umbral operator computes discrete logs faster than periodicity
allows.

### Status
OPEN — **DEMOTED**

### Novelty classification
LEDGER-NEW keyword (umbral / Sheffer: 0 hits) but **DEMOTED**: mechanism-adjacent to batch5 `MAHLER-B1`
(automatic-sequence / Mahler representation of `x([k]P)`), which was killed by `F_p` periodicity.

### Semantic fingerprint
F(C) = (algebraic object: the Sheffer sequence / umbral operator representing `k ↦ x([k]P)`; operations:
umbral shift; hidden structure: linear-functional recurrence; discarded: nothing new; retained: the
scalar-multiplication orbit; relation-gen primitive: umbral evaluation; compression: recurrence order;
rank mechanism: N/A; descent: solve the recurrence for `k`; dominant exponent: state complexity ≈
`ord(P)`).

### Nearest ledger entries
1. `MAHLER-B1` (batch5) — automatic-sequence rep of `x([k]P)`; **distinction:** umbral vs Mahler basis —
   same target function, same periodicity collapse.
2. `FORMALGROUP-B1` (batch8) — Coleman/formal-group log; **distinction:** `p`-adic vs umbral, both
   collapse at `gcd(p,n)=1`.
3. `ELLNET-C2` (batch7) — elliptic-net recurrence; **distinction:** bilinear net vs umbral shift.
4. `CLUSTER-MUTATION-B3` (batch8) — Somos recurrence; **distinction:** cluster vs umbral.
5. `DML-ORBIT-C1` (batch6) — dynamical Mordell–Lang orbit; **distinction:** orbit intersection vs umbral
   recurrence.

### Nearest literature
- Rota–Roman, umbral calculus / Sheffer sequences. **Gap:** over `F_p` the orbit `k ↦ [k]P` is periodic
   with period `ord(P) = n`, so any finite recurrence has state complexity `Ω(n)`.

### Target family
As §1.2.

### Full algorithmic path
1. FB: standard. 2. Relation gen: umbral recurrence for `x([k]P)`. 3. Verify: Tier-0.
4–7. Descent = solve the recurrence; **state complexity `Ω(ord P) = Ω(n)` ⇒ no gain over BSGS**.
8–9. Trivial.

### Cost model
State complexity `Ω(n) = Ω(L^5)` ⇒ far worse than rho `L^{2.5}`. Cost-negative.

### Why the existing negative results do not already kill it
It is a keyword-new basis; but the periodicity obstruction (batch5 MAHLER) is basis-independent.

### Likely fatal obstruction
`F_p` periodicity: `[k]P` has period `n`, forcing `Ω(n)` recurrence states — identical to the MAHLER
collapse. DEMOTED.

### Minimal falsifying experiment
Three sizes; fit the minimal umbral recurrence order for `x([k]P)`; confirm it is `Θ(n)`. Positive
control: a genuinely low-order Sheffer sequence. Negative control: `x([k]P)`.

### Quantitative promotion gate
Cannot promote (state complexity `Ω(n)`).

### Proof track
N/A.

### Disproof track
Recurrence order `Θ(n)` ⇒ dead (expected).

### Reproduction artifact
Contract `experiment_contract_p1666_umbral_sheffer_scalarmult.md`; impl `p1666_umbral_sheffer.sage`;
result/audit JSON; ledger `ECFG-P1666`.

---

### Group D — negative-theory candidates (barriers / loopholes)

---

## Candidate: EVASIVENESS-BARRIER-D1

### One-sentence mechanism
Prove the m=5 membership decision process is **evasive** (full-depth) in the topological sense, so any
deterministic membership backend must make `Ω(r)` field-op-weighted queries — a first topological query
barrier on RT-1476.

### Status
HYPOTHESIS (barrier)

### Novelty classification
LEDGER-NEW (evasiveness barrier: 0 hits). Distinct from batch13 `SENSITIVITY-DEGREE-BARRIER-D1`
(spectral Huang) and batch10 `ELUSIVE-FUNCTIONS-D1` (algebraic Raz); this uses `Z_p`-collapsibility.

### Semantic fingerprint
As EVASIVENESS-KSS-A1, in barrier polarity: `H̃_*(Δ)≠0` ⇒ evasive ⇒ `α ≥ 1` (field-op-weighted `≥ 1.5`).

### Nearest ledger entries
1. `SENSITIVITY-DEGREE-BARRIER-D1` (batch13) — Huang `s≥√deg`; **distinction:** spectral vs homological.
2. `ELUSIVE-FUNCTIONS-D1` (batch10) — algebraic elusiveness; **distinction:** circuit vs decision-tree.
3. `LIFTING-D1` (batch7) — query→comm; **distinction:** transfer, not source bound.
4. `CUTTING-PLANES-RANK-BARRIER-D2` (batch13) — proof rank; **distinction:** proof vs query.
5. `RAZ-MULTILINEAR-FORMULA-D3` (batch11) — formula LB; **distinction:** formula vs decision tree.

### Nearest literature
- Kahn–Saks–Sturtevant (1984); Rivest–Vuillemin (1976); Lovász–Young survey. **Gap:** KSS needs a
   prime-power transitive symmetry the membership family lacks.

### Target family
As §1.2.

### Full algorithmic path
As A1; the barrier claims the collapsibility obstruction holds for infinitely many `r`.

### Cost model
Best honest outcome: `α ≥ 1` (unweighted) ⇒ field-op-weighted `≥ 1.5` = **reproduces the floor, does
not push above it**. To *close* RT-1476 the barrier would need weighted evasiveness giving `α ≥ 1.5`
strictly, which is exactly the gate value — a boundary, not a strict closure.

### Why the existing negative results do not already kill it
Topological depth is decoupled from polynomial degree (P1512) and from spectral sensitivity (batch13),
so it is a genuinely new lower-bound route even if it lands at the boundary.

### Likely fatal obstruction (to the barrier)
Missing transitive symmetry ⇒ KSS gives only linear (`α≥1`) evasiveness ⇒ **below** the `3/2` needed to
strictly close the gate; a cone point would even give `α<1`.

### Minimal falsifying experiment
As A1 (`χ̃(Δ)`, weighted depth) but scored as a *barrier*: does the weighted lower bound reach `1.5`?

### Quantitative promotion gate (to accepted barrier)
Accept only if a *proof* gives field-op-weighted `α ≥ 3/2` for infinitely many `r`. Measurement of
`χ̃≠0` alone gives at most `α≥1`, insufficient.

### Proof track
Theorem: weighted decision-tree depth of m=5 membership is `Ω(r^{3/2})`.

### Disproof track
A cone point / collapsible `Δ` ⇒ evasiveness fails ⇒ barrier dead.

### Reproduction artifact
Contract `experiment_contract_p1667_evasiveness_barrier_membership.md`; impl
`p1667_evasiveness_barrier.sage`; result/audit JSON; ledger `ECFG-P1667`.

---

## Candidate: HEREDITARY-DISCREPANCY-BARRIER-D2

### One-sentence mechanism
Use the **Beck–Fiala degree-2 discrepancy bound** on the two-large-prime incidence system (each relation
touches exactly 2 large primes ⇒ `herdisc = O(1)` *unconditionally*) to cap the achievable supply
enrichment at `δ ≤ 1/4`, a first combinatorial-discrepancy barrier on RT-1472.

### Status
HYPOTHESIS (barrier) — **sharpest new item this run**

### Novelty classification
LEDGER-NEW (Beck–Fiala / hereditary discrepancy barrier: 0 hits). Distinct from batch12 communication
`DISCREPANCY-CORRUPTION`, batch14 `LARGE-SIEVE-BARRIER-D1` (analytic `L^2`), batch8 `SHEARER-D3`
(entropy), batch5 `MATUNION-INDEP-D2` (matroid).

### Semantic fingerprint
As SPENCER-DISCREPANCY-A2 in barrier polarity: `herdisc(A)=O(1)` (Beck–Fiala, `t=2`) ⇒ enrichment
`o(√occupancy)` ⇒ `δ ≤ 1/4`.

### Nearest ledger entries
1. `LARGE-SIEVE-BARRIER-D1` (batch14) — analytic supply ceiling; **distinction:** `L^2` inequality vs
   combinatorial coloring.
2. `SHEARER-D3` (batch8) — entropy ceiling; **distinction:** count vs coloring balance.
3. `MATUNION-INDEP-D2` (batch5) — matroid non-independence; **distinction:** rank vs discrepancy.
4. `DISCREPANCY-CORRUPTION-A3` (batch12) — communication discrepancy; **distinction:** protocol vs set
   system.
5. `CUTTING-PLANES-RANK-BARRIER-D2` (batch13) — proof rank δ-ceiling; **distinction:** proof complexity
   vs Beck–Fiala.

### Nearest literature
- Beck–Fiala (1981): degree-`t` ⇒ `disc ≤ 2t−1`; here `t=2` ⇒ `disc ≤ 3`. Lovász–Spencer–Vesztergombi
   (1986): `herdisc` transference. Matoušek–Nikolov (2015): `γ_2`-`herdisc` equivalence. **Gap:** the
   translation from `herdisc` (a *signed*-coloring balance) to occupancy-supply `δ` (an *unsigned* count)
   is unproven.

### Target family
As §1.2; honest 2-LP incidence.

### Full algorithmic path
As SPENCER-DISCREPANCY-A2 in barrier mode.

### Cost model
If the translation holds, `δ ≤ 1/4` unconditionally for the honest 2-LP graph ⇒ RT-1472 cannot cross ⇒
closes the gate for all two-large-prime enrichment (the dominant open supply lane). Compare vs rho: the
RT-1472 optimum `L^{5/3}` never reaches below-`L^{1.25}`.

### Why the existing negative results do not already kill it
Prior δ-barriers bound counts or spectra; none bounds the *balanced-selection* operation the enrichment
literally performs. Beck–Fiala gives an *unconditional `O(1)`* discrepancy no prior meter delivered.

### Likely fatal obstruction (to the barrier)
The `herdisc → δ` translation: if enrichment gains come from *unsigned* pair multiplicity (many relations
per pair), discrepancy is silent and `δ` can exceed the coloring bound. Closing this gap is the whole
proof-track risk.

### Minimal falsifying experiment
Three sizes; confirm `herdisc(A)=O(1)` via `γ_2`/determinant bounds; measure honest `δ̂`; test whether
`δ̂ ≤ 1/4` and whether it tracks `herdisc/√occupancy`. Positive control: random degree-2 (Beck–Fiala
tight). Negative control: high-`herdisc` Hadamard system. Gate: `δ̂ ≤ 1/4`?

### Quantitative promotion gate (to accepted barrier)
Accept only if (a) `herdisc=O(1)` proven for the arithmetic 2-LP system AND (b) the `herdisc → δ`
translation lemma is proven, giving `δ ≤ 1/4` unconditionally.

### Proof track
Theorem: for the honest two-large-prime incidence matrix, maximal supply enrichment
`δ = O(herdisc·polylog/√occupancy) ⇒ δ ≤ 1/4`.

### Disproof track
Exhibit an arithmetic 2-LP family with `δ̂ > 1/4` and `O(1)` discrepancy ⇒ translation false ⇒ barrier
dead.

### Reproduction artifact
Contract `experiment_contract_p1668_hereditary_discrepancy_barrier.md`; impl
`p1668_hereditary_discrepancy_barrier.sage`; result/audit JSON; ledger `ECFG-P1668`.

---

## Candidate: SHARP-THRESHOLD-BARRIER-D3

### One-sentence mechanism
Use **Friedgut–Kalai symmetry** (the 2-LP supply property is invariant under prime relabeling ⇒ sharp
threshold) to prove the RT-1472 supply has **no intermediate `δ ∈ (1/4, ½)` plateau** — the supply jumps
from useless to saturated, a first threshold-geometry barrier.

### Status
HYPOTHESIS (barrier)

### Novelty classification
LEDGER-NEW (sharp-threshold barrier: 0 hits). Distinct from batch4 `CORRELATED-PEEL-A3` (Wormald DE 2-core
*location*) and batch4 `SOS-LB-D1` / all analytic-supply barriers.

### Semantic fingerprint
As SHARP-THRESHOLD-FRIEDGUT-A3, barrier polarity: symmetric monotone property ⇒ (Friedgut–Kalai) sharp
threshold width `o(B_c)` ⇒ no exploitable `δ`-window.

### Nearest ledger entries
1. `CORRELATED-PEEL-A3` (batch4) — 2-core threshold; **distinction:** width vs location.
2. `LARGE-SIEVE-BARRIER-D1` (batch14) — analytic; **distinction:** influences vs `L^2`.
3. `SIEVE-PARITY-BARRIER-D3` (batch14) — Selberg parity; **distinction:** parity vs threshold.
4. `MATUNION-INDEP-D2` (batch5) — matroid; **distinction:** rank vs threshold.
5. `HEREDITARY-DISCREPANCY-BARRIER-D2` (this batch) — discrepancy; **distinction:** balance vs threshold
   width (complementary, D2 bounds magnitude, D3 bounds window existence).

### Nearest literature
- Friedgut–Kalai (1996): symmetric monotone ⇒ sharp threshold. Bourgain–Friedgut (1999): coarse ⇒ junta.
   **Gap:** proving the *width* `o(B_c)` excludes the *specific* `δ∈(1/4,½)` band requires quantifying
   the threshold window against the exponent boundary, not just qualitative sharpness.

### Target family
As §1.2.

### Full algorithmic path
As SHARP-THRESHOLD-FRIEDGUT-A3, barrier mode.

### Cost model
If the threshold is sharp with width `o(B_c)`, there is no `B` giving `δ∈(1/4,½)` ⇒ RT-1472 window empty
⇒ closes the gate for honest symmetric supply. Compare vs rho as above.

### Why the existing negative results do not already kill it
No prior barrier addressed threshold *geometry*; it targets exactly the loophole (a coarse plateau) under
which `δ>1/4` could persist.

### Likely fatal obstruction (to the barrier)
Qualitative sharpness is near-certain (symmetry) but *quantitatively* excluding the `(1/4,½)` band needs
a width-vs-exponent estimate that Friedgut–Kalai does not directly give — the barrier may prove "sharp"
yet not pin the window below the boundary.

### Minimal falsifying experiment
As A3 but scored as barrier: measure width `ΔB`; test `ΔB = o(B_c)` and that no `B` yields `δ̂∈(1/4,½)`.
Positive control: sharp connectivity. Negative control: coarse biased-majority. Gate: empty `δ`-window?

### Quantitative promotion gate (to accepted barrier)
Accept only if a proof gives threshold width `o(B_c)` AND excludes `δ∈(1/4,½)` for all honest `B`.

### Proof track
Theorem: the symmetric 2-LP supply property has sharp threshold with width `o(B_c)` excluding the
`δ∈(1/4,½)` band.

### Disproof track
Measure a coarse threshold / an exploitable plateau ⇒ barrier dead, opens A3's positive branch.

### Reproduction artifact
Contract `experiment_contract_p1669_sharp_threshold_barrier.md`; impl `p1669_sharp_threshold_barrier.sage`;
result/audit JSON; ledger `ECFG-P1669`.

---

## 4. Ranking

Scores 0–5 on: (1) distance from prior ledger mechanisms; (2) plausibility of an exact verifier; (3)
chance of moving an *exponent* not a constant; (4) complete-path coverage; (5) falsifiability at toy
scale; (6) literature-novelty confidence; (7) low risk of hidden preprocessing/memory cost. Reject if
semantic novelty `< 3`, no complete descent, no rho comparison, or no precise distinction from the
nearest ledger entry.

| Candidate | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Verdict |
|---|---|---|---|---|---|---|---|---|
| EVASIVENESS-KSS-A1 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | **kept — conservative winner** |
| SPENCER-DISCREPANCY-A2 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | kept (feeds D2) |
| SHARP-THRESHOLD-FRIEDGUT-A3 | 4 | 3 | 2 | 4 | 4 | 4 | 4 | kept (feeds D3) |
| FI-MODULE-STABILITY-B1 | 5 | 3 | 3 | 4 | 3 | 4 | 3 | **kept — representation winner** |
| INCIDENCE-HOPF-ANTIPODE-B2 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | kept |
| COMBINATORIAL-SPECIES-B3 | 3 | 3 | 1 | 1 | 3 | 3 | 4 | **rejected — INCOMPLETE (no descent)** |
| HYPERCONTRACTIVITY-SSE-C1 | 4 | 3 | 3 | 4 | 4 | 4 | 3 | **kept — high-risk winner** |
| STREAMING-SKETCH-C2 | 4 | 4 | 1 | 4 | 4 | 4 | 3 | kept (self-defeating; feeds streaming LB) |
| UMBRAL-SHEFFER-C3 | 2 | 4 | 1 | 3 | 4 | 3 | 4 | **rejected — DEMOTED (dup of MAHLER)** |
| EVASIVENESS-BARRIER-D1 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | kept — barrier |
| HEREDITARY-DISCREPANCY-BARRIER-D2 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | **kept — highest-EV barrier** |
| SHARP-THRESHOLD-BARRIER-D3 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | kept — barrier |

Rejections: COMBINATORIAL-SPECIES-B3 (novelty 3 but no descent path, INCOMPLETE); UMBRAL-SHEFFER-C3
(novelty 2, duplicate of batch5 MAHLER by periodicity collapse).

**Selected winners:**
1. **Conservative:** EVASIVENESS-KSS-A1 (`ECFG-P1658`).
2. **Representation-changing:** FI-MODULE-STABILITY-B1 (`ECFG-P1661`).
3. **High-risk:** HYPERCONTRACTIVITY-SSE-C1 (`ECFG-P1664`).

Highest-EV item overall is **HEREDITARY-DISCREPANCY-BARRIER-D2** (`ECFG-P1668`): a Beck–Fiala `O(1)`
discrepancy is *unconditional*, and only the `herdisc → δ` translation lemma stands between it and an
unconditional `δ ≤ 1/4` closure of RT-1472's dominant supply lane.

---

## 5. Winner contracts + first executable commands

### 5.1 Contract — EVASIVENESS-KSS-A1 (`ECFG-P1658`)

- **Hypothesis:** the m=5 membership complex `Δ_r` is non-`Z_p`-collapsible (`χ̃(Δ_r)≠0`) for
  infinitely many `r`, and its field-op-weighted decision-tree depth scales as `r^{α}` with `α`
  *measurable* below 1.5.
- **Frozen protocol:** sizes `p ≈ {2^{20}, 2^{26}, 2^{32}}`; ≥3 random ordinary prime-order curves per
  size; seeds `{1,2,3}`; positive control = triangle-parity monotone property; negative control =
  cone-augmented (collapsible) property; metric = `χ̃(Δ)`, `H̃_*(Δ;Z_p)` where feasible, and
  field-op-weighted tree depth.
- **Promotion gate:** measured weighted `α < 1.5` with downward trend on all three sizes.
- **Kill condition:** cone point / `χ̃=0` / weighted `α ≥ 1.5`.
- **First command:**
```
sage p1658_evasiveness_kss_membership.sage --sizes 20,26,32 --curves 3 --seeds 1,2,3 \
  --pos-control triangle-parity --neg-control cone --emit p1658_evasiveness_kss_membership.json
```

### 5.2 Contract — FI-MODULE-STABILITY-B1 (`ECFG-P1661`)

- **Hypothesis:** the symmetrized summation ideal sequence `{I_m}` is a finitely generated FI-module (or
  `FI#`) whose stable generation degree gives a per-target m=5 membership exponent `c(d) < 1.5`.
- **Frozen protocol:** compute `S_m`-decompositions of `(I_m)_d` for `m = 2..8`, low `d`; test
  eventually-polynomial multiplicities (stability) and estimate generation degree; positive control =
  configuration-space FI-module; negative control = a non-f.g. ideal sequence; sizes as above for the
  instantiated m=5 cost.
- **Promotion gate:** measured representation stability AND measured per-target exponent `< 1.5`.
- **Kill condition:** transition maps not FI-morphisms / unbounded generation degree / cubic
  irreducibility blocks stabilization.
- **First command:**
```
sage p1661_fi_module_stability.sage --m-range 2:8 --deg-max 4 --stability-test poly-mult \
  --pos-control config-space --neg-control non-fg --emit p1661_fi_module_stability.json
```

### 5.3 Contract — HYPERCONTRACTIVITY-SSE-C1 (`ECFG-P1664`)

- **Hypothesis:** the m=5 membership indicator is small-set-expanding enough that a `T_ρ`-smoothed
  sampler emits genuine relations at `α_avg < 1.5` on a `1−o(1)` target fraction, giving a complete cost
  (smoothed + rho fallback) below `L^{2.5}`.
- **Frozen protocol:** sizes as above; estimate level-`k` Fourier weight and total influence of the
  `F_p` indicator; sweep noise `ρ`; measure smoothed hit-rate and *complete* cost including rho fallback;
  positive control = low-influence smooth indicator; negative control = a single linear equation
  (rigid high-influence).
- **Promotion gate:** fitted `α_avg < 1.5` with fallback fraction `o(1)` and complete cost trending
  below `L^{2.5}` on all three sizes.
- **Kill condition:** heavy influence along the constraint ⇒ no smoothing ⇒ `α_avg ≥ 1.5`.
- **First command:**
```
sage p1664_hypercontractivity_sse.sage --sizes 20,26,32 --rho-sweep 0.1:0.9:0.1 \
  --influence-est true --fallback rho --pos-control smooth --neg-control linear \
  --emit p1664_hypercontractivity_sse.json
```

---

## 6. Red-team — "all three winners are disguised repetitions or cost-negative"

- **EVASIVENESS-KSS-A1 ≈ a boundary meter, not a crossing.** Even a full evasiveness proof yields
  field-op-weighted `α = 1.5` (the gate value), not below it — the membership family lacks the
  prime-power transitive symmetry KSS needs, so the topological bound is only linear (`α≥1`). It is a
  *tighter articulation of the `L^{1.5}` floor*, matching the batch13 sensitivity verdict by a different
  route. **Verdict: near-certain scoped negative; converts to D1 (also boundary-only).**
- **FI-MODULE-STABILITY-B1 ≈ SYZYGY-REGULARITY-B2 (batch4) with an added functor, likely non-f.g.**
  The genuinely-new content is FI-functoriality; but "add a summand" is a group-law merge, not a free
  label injection, so the FI axioms almost certainly fail and the sequence is not finitely generated —
  in which case Church–Ellenberg Noetherianity gives nothing and the object reduces to the per-`m`
  Betti-table analysis already scoped-negative in batch4. Cubic irreducibility (P1513) further blocks
  stabilization. **Verdict: high-novelty but near-certain kill at the FI-functoriality step.**
- **HYPERCONTRACTIVITY-SSE-C1 ≈ RANDOM-RESTRICTION-C1 (batch13) on the noise axis, self-defeating.**
  Both are average-case backends with rho fallback; the noise operator can only concentrate a
  *small-set-expanding* indicator, and a codimension-1 algebraic variety has a heavy-influence junta
  along its defining constraint, so `T_ρ` gives no gain — the same "no shallow structure" kill batch13
  hit, re-expressed spectrally. **Verdict: near-certain self-defeating scoped negative.**

None of the three is a crossing. The **three D barriers are higher-EV** — each imports a lower-bound
technology no prior barrier used (topological evasiveness, Beck–Fiala discrepancy, Friedgut sharp
threshold), and **HEREDITARY-DISCREPANCY-BARRIER-D2** is the single most valuable item this run because
its `O(1)`-discrepancy input is *unconditional* (Beck–Fiala, degree 2), reducing the whole RT-1472
supply question to one translation lemma. **No break is claimed; RT-1472 and RT-1476 remain open.**

---

## 7. Claim discipline

- **Correctness ≠ performance:** every candidate's promotion gate requires a *measured exponent trend*,
  never mere correctness of a homology / representation / sampler computation.
- **Candidate relation ≠ verified ECDLP recovery:** all produced relations are Tier-0 re-checked by the
  wrapper; no evidence record would assert a solve above its certificate tier.
- **Toy-scale only:** all experiments are `p ≤ 2^{32}` synthetic ordinary curves; no crypto-scale claim
  is implied.
- **Barriers are conditional:** D1/D2/D3 are HYPOTHESIS-grade; each names the exact unproven step
  (transitive symmetry; `herdisc→δ` translation; width-vs-exponent estimate). A failed candidate is a
  **scoped negative**, not evidence that prime-field ECDLP cannot be improved.
- **This report is uncommitted:** it lives as a file; no ledger commit or status change is made unless
  the Coordinator requests it (AGENTS.md rule 1).

---

## 8. Ledger IDs minted this report

`ECFG-P1658` EVASIVENESS-KSS-A1 · `ECFG-P1659` SPENCER-DISCREPANCY-A2 · `ECFG-P1660`
SHARP-THRESHOLD-FRIEDGUT-A3 · `ECFG-P1661` FI-MODULE-STABILITY-B1 · `ECFG-P1662`
INCIDENCE-HOPF-ANTIPODE-B2 · `ECFG-P1663` COMBINATORIAL-SPECIES-B3 (rejected) · `ECFG-P1664`
HYPERCONTRACTIVITY-SSE-C1 · `ECFG-P1665` STREAMING-SKETCH-C2 · `ECFG-P1666` UMBRAL-SHEFFER-C3 (demoted)
· `ECFG-P1667` EVASIVENESS-BARRIER-D1 · `ECFG-P1668` HEREDITARY-DISCREPANCY-BARRIER-D2 · `ECFG-P1669`
SHARP-THRESHOLD-BARRIER-D3.

Range `ECFG-P1658–P1669`. Prior frontier `ECFG-P1657` (batch9/internal batch15). No IDs reused.
