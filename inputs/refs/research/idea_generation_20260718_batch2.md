# Research-Director Idea Generation — 2026-07-18 (batch 2)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Mission:** propose *mechanism-new*, falsifiable directions whose **complete** cost could
eventually beat the single-target Pollard-rho `0.886·sqrt(n)` baseline for ECDLP over
**ordinary prime fields**. Toy correctness, a new coordinate system, a relation certificate,
faster preprocessing, or a solver swap is explicitly **not** a breakthrough.

Autonomous scheduled run (no user present); implementation choices noted inline.

## Why a second report today

A complete first report already exists for today: `research/idea_generation_20260718.md`
(1744 lines; candidates A1 sparse-interpolation, A2 Sidon/B_h, A3 list-decoding, B1 Serre–Tate
[rejected dup], B2 Cartier–Manin [rejected dup], B3 group-dual DFT, B4 Semaev border-rank,
C1 approximate-homomorphism stability, C2 Kloosterman importance-sampling, C3 CM ideal
factorization, D1–D3 barriers). Re-running the same brief would only re-derive it. Following the
07-17 precedent (batch1 + batch2), this is a **batch 2** held to a **strictly harder** novelty bar:
each candidate must be mechanism-new against the ledger **and all three** prior reports
(`idea_generation_20260717.md`, `..._20260717_batch2.md`, `..._20260718.md` — 36 candidates in
total). The three prior runs, between them, consumed essentially every seed named in the task brief
plus a large penumbra. This report therefore deliberately leaves the mined lanes and reaches into
five families that **none** of the three prior reports touched: **modular-parametrization / Hecke**,
**Drinfeld / function-field transport**, **arithmetic-dynamical map-decomposition (Ritt/Dickson)**,
**isogeny-graph expander walks**, and **unlikely-intersection (Pink–Zilber)**, plus two conservative
probes aimed directly at the two open conditional theorems.

---

## 0. Review scope and inventory census

**Required inputs read (all four), plus derived corpus and all three prior reports:**

1. `research_ledger.md` — 2465 lines. Sections: open-frontier questions (~103), active hypotheses
   (ECFG-H303..H687, ISO-AR/SP, TRANSFER-H, SHA1-H ≈ 427), negative results (ECFG-NR span
   303..1484 ≈ 501, plus TRANSFER-NR ≈ 53, ISO-AR/SP/CW-NR ≈ 59, ISO-NR-ONK/IKD, core NR-, SHA1-N;
   **total distinct negatives ≈ 638**), positive signals (ECFG-P..P1513, TRANSFER/PO, ISO-AR-POS
   ≈ 1068), baselines, literature map, and the three restricted-model rows **RT-1472, RT-1476,
   RT-1485** — the only rho-relevant conditional theorems on the board.
2. `ecdlp_index_calculus_state/research_ledger.md` — 720 lines; ECFG functional-graph + provenance
   direct-source track, now at P1510–P1513 (worst-case-optimal-join / factorized-semijoin /
   linear-Chow atomizer on the 5-term provenance query).
3. `research/non_generic_transfer_search_20260610.md` — 390 lines; transfer/decomposition channel
   search + PO-transfer-001..006 appendix (twist positive control, trace-fiber lemma).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` — 10 primary IC entries (Semaev
   2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013; FHJRV 2014; Kousidis–Wiemers 2015; Karabina
   2015; Amadori–Pintore–Sala 2017; McGuire–Mueller 2017; Trimoska–Ionica–Dequen 2020).
5. Derived corpus: 1100+ files in `research/` (178 PO_transfer contracts, 169 ISO-AR atlas entries,
   PAPER_* barrier notes, p14xx theorems), plus the three idea reports (inputs 13–15).

**ID families and their fingerprints (mechanism / representation / structure / factor base /
relation shape / relation-gen / compression / linear-algebra object / descent / bottleneck /
outcome):**

| Family | Mechanism core | Representation | Bottleneck | Outcome envelope |
|---|---|---|---|---|
| **ECFG** (dominant) | coordinate index calculus + Evans functional-graph provenance; now DB-join sub-lane | x-line / 5-term summation deck | five-term implicit membership; final-column rank; below-rho generation | all coordinate/selector/scout micro-optimizations are **negative controls**; the honest wall is RT-1476 (α<3/2) |
| **TRANSFER/PO** | cover / Prym / Jacobian correspondence over F_p; incidence-cover; oriented-ideal Kani | genus-2/3 Jacobian, trigonal cover | calibration deficit; missing nonlinear packet; composition law absent | same-field cover **cannot beat** IC (Diem); genus-2 RM escape only via Kani glue (batch2 B1) |
| **ISO-AR / SP / ONK / IKD** | oriented-CM isogeny walks; self-pairing; oriented-ideal Kani recovery | CM order / class group | finding an *isogenous weak curve* | NR-033/T-ISO-4: no weak isogenous B for NIST curves; FLAT volcano, class-wide End |
| **SHA1** | seed-preimage bounty | — | off-ECDLP | negative |
| **RT frontier** | 2-LP occupancy (RT-1472); m-ary membership (RT-1476); Kummer state (RT-1485) | restricted cost models | enrichment δ>1/4 (RT-1472); backward-3-sum α<3/2 (RT-1476) | **two open conditional theorems** — the entire live surface |

**Prior-report mechanism catalogue (must all be treated as covered):** Semaev-Gröbner (baseline),
BKK/mixed-volume, elliptic-net/EDS smoothness, incidence-reporting range DS, dual-number/jet lift,
tensor-train separator rank, Semaev border/CP rank, tropical/p-adic valuation descent,
noncommutative CM-correspondence (quiver), Lattès transfer-operator spectrum, Xedni global
height-lattice lift, 3-large-prime hypergraph homology, NFS two-sided coincidence, Kedlaya–Umans
membership evaluation, Kani genus-2 RM Jacobian glue, Serre–Tate canonical lift, level-≥3
theta-bilinear membership, representation-technique MITM, p-curvature/holonomy descent,
character-sum/Kloosterman bias sampling, sparse interpolation (Prony/Ben-Or–Tiwari), Sidon/B_h
additive designs, list-decoding (Guruswami–Sudan) membership, group-dual DFT indicator,
Bogolyubov–Ruzsa approximate-homomorphism stability, CM ideal-factorization class-group IC.
Barriers already stated: nilpotent no-rank-gain, correspondence-permutation no-gain, separator-rank
LB, generic-model MITM, crystalline order-only, Gaudry fixed-genus IC, class-function no-leakage,
addition-law scrambling, transform-sparsity/border-rank LB.

**Everything in this report is fingerprinted against that catalogue.** The five lanes I enter
(modular/Hecke, Drinfeld/FF-transport, Ritt/Dickson dynamics, isogeny-expander walk,
Pink–Zilber) appear **nowhere** in the catalogue above and nowhere in the 638 negatives.

**Claim discipline.** Everything below is `CONJECTURE`/`HYPOTHESIS`/`OPEN`. No toy correctness is
claimed. Novelty labels: `LEDGER-NEW` (absent from reviewed ledger), `LITERATURE-ADJACENT`
(nearby prior art), `NOVELTY-UNVERIFIED` (literature coverage incomplete), `POSSIBLY NOVEL`
(no equivalent mechanism found after a documented search — see §5 for the literature grounding).

---

# Group A — Conservative extensions (attack the two open theorems directly)

## Candidate: A1 — Subresultant-PRS non-materializing backward-state backend (RT-1476 α-meter)

### One-sentence mechanism
Exploit the **serial S3 factorization** of five-point membership to compute the backward 3-sum
state with a **subresultant polynomial-remainder-sequence with modular early-abort**, reducing the
membership-query exponent `α` of subproblem P (implicit 5-term membership) below the dense-eliminant
cost, toward the `α<3/2` threshold that RT-1476 proves would beat rho.

### Status
HYPOTHESIS (α is a measurable exponent; the theorem it feeds is already proven).

### Novelty classification
LITERATURE-ADJACENT (subresultant PRS is classical; its use as the *non-materializing backward-state
representation* the ledger's P1477 gate explicitly asks for, versus the batch1 tensor-train and
batch2 Kedlaya–Umans backends, is the new operation).

### Semantic fingerprint F(A1)
- algebraic object: 5th Semaev polynomial `S5(x1..x5)`, serial-split into forward `S3(x1,x2,u)` and
  backward `S4(u,x3,x4,x5)` sharing the intermediate x-coordinate `u`.
- available public operations: field ops in F_p; polynomial arithmetic; resultant/subresultant.
- hidden structure exploited: the **elimination ideal of the backward 3-sum is low-degree in `u`**
  even though the composed eliminant is dense (the ledger's own RT-1485 shows the Kummer companion
  state has *constant* fibers and quadratic support — a hint the backward state may be compressible).
- information discarded: the explicit composed resultant (never formed).
- information retained: a subresultant coefficient stream sufficient to certify `u`-membership.
- relation-generation primitive: for each candidate `(x3,x4,x5)` in the factor base, run PRS in `u`
  against the forward table; early-abort on the first vanishing subresultant.
- compression primitive: subresultant PRS = structured Gaussian elimination on the Sylvester matrix
  without forming the eliminant (Bareiss/Collins).
- rank mechanism: `Θ(L)` relations, sparse, over `Z/n`; standard sparse LA.
- descent mechanism: same backend on the target's decomposition (RT-1476 uses the backend for
  descent too).
- dominant cost exponent: **the object of measurement** — backward-state degree `d(u)` and its
  scaling exponent `α := log_L(query cost)`.

### Nearest ledger entries
1. **RT-1476** — the theorem this feeds; A1 is the executable meter for its free parameter `α`.
2. **P1477** (RT-1476 next action) — *"non-materializing backward representation with measured
   exponent <1.5"*; A1 is one concrete instantiation. Distinction from the ledger's own suggestion:
   the ledger leaves the representation unspecified; A1 commits to subresultant PRS and gives a
   falsifiable degree measurement.
3. **RT-1485** — Kummer companion state (constant fibers, quadratic support); evidence the backward
   state *may* be low-degree, but RT-1485 is a *storage* result, not a *query* backend. A1 turns the
   structural hint into a query cost.
4. **batch1 B2 tensor-train** — also a non-materializing S3 backend, but by low-rank tensor
   contraction; A1 is elimination-theoretic (subresultant), not a tensor factorization — different
   compression primitive, different failure mode (degree growth vs bond dimension).
5. **batch2 A3 Kedlaya–Umans** — black-box fast multivariate evaluation; A1 exploits the *structured
   bivariate* backward eliminant rather than treating membership as an opaque evaluation. The exact
   distinction: KU bounds evaluation cost; A1 bounds the **degree of the eliminant** — a different
   quantity that could be small even when KU is not decisive.

### Nearest literature
Collins 1967 (subresultant PRS); Bareiss 1968; von zur Gathen–Lücking 2003 (subresultants,
complexity). Semaev 2004 / Gaudry 2009 (summation-polynomial IC). None measures the backward
serial-S3 degree exponent for the m=5 prime-field system. Gap: no primary source has computed
whether the backward 3-sum eliminant degree in `u` grows sub-`q^{3/2}`.

### Target family
Ordinary prime-field `E/F_p`, prime order `n`, `j∉{0,1728}`, no CM special-order, non-anomalous,
large embedding degree. Excluded: binary/extension fields, singular/supersingular/anomalous.

### Full algorithmic path
1. **Factor base:** `L = q^ℓ` x-coordinates on the line (the ledger's m=5 model).
2. **Relation generation:** forward table of `S3(x1,x2,u)` roots `u` for all `(x1,x2)` pairs;
   backward PRS test each `(x3,x4,x5)` for a shared `u`.
3. **Witness extraction/verification:** the vanishing subresultant yields the shared `u`; verify the
   full `S5=0` by direct evaluation (exact, O(1) field ops).
4. **Relation probability:** `min(1, L^5/q)` per 5-tuple (unchanged from RT-1476 model).
5. **Matrix:** `Θ(L)` rows, sparse (≤5 nonzeros/row), over `Z/n`; density `O(1/L)`.
6. **Factor-log calibration:** standard IC calibration on the factor-base logs.
7. **Descent:** same subresultant backend on `T + [r]P` decompositions.
8. **Offline/online:** relation collection + LA offline per curve; descent online per target.
9. **Memory/parallelism:** forward table `O(L^2)` entries (or streamed with distinguished-`u`);
   PRS is embarrassingly parallel across the backward factor base.

### Cost model
Per RT-1476: total exponent `2/(m+1−α)` for `α≤1`, else `(1+α)/m`; at m=5, sub-rho requires
`α<3/2`. A1's job is to measure `α`. If the backward eliminant degree in `u` is `Θ(q^β)`, then
naive root-finding gives `α≈β·(cost-of-degree-d-root-find exponent)`. **Concrete falsifiable
prediction:** if `β≥3/10` the whole scheme lands at exponent `≥1/2` (tie/worse) — measure `β`.
Compare vs rho `0.886 q^{1/2}`, BSGS `q^{1/2}` time+memory, Gaudry-Diem prime-field IC (no sub-rho
known).

### Why existing negatives do not already kill it
The closed-territory list names **"dense composed resultants"** as a negative control. A1's new
operation is **not forming the composed resultant**: subresultant PRS with early-abort reads off the
degree of the *smallest* nonzero subresultant, which can be far below the product degree. The
obstruction avoided is eliminant materialization; the responsible operation is the Bareiss-style
fraction-free PRS that exposes intermediate degree without the final expansion.

### Likely fatal obstruction
The backward 3-sum eliminant in `u` almost certainly has degree `Θ(q)` (the generic Bezout bound for
three summation constraints), giving `β=1`, `α≥1`, and no sub-rho window at m=5. RT-1485's constant
fibers are for the *Kummer companion*, not the general backward state — the compressibility may not
transfer.

### Minimal falsifying experiment
Toy p ∈ {1009, 65521, 16769023}. For random ordinary prime-order curves (3 seeds each), build the
serial-S3 split symbolically, run subresultant PRS, and **measure the degree of the first nonzero
subresultant in `u`** as a function of `q`. Positive control: a contrived curve where the backward
state is known low-degree. Negative control: a random dense trivariate system of the same total
degree (should show `β≈1`). Fit `β = d log(deg)/d log(q)`.

### Quantitative promotion gate
Measured `β < 0.3` across all three sizes with a downward or flat trend ⇒ `α<3/2` plausible ⇒
promote to a costed collector. `β ≥ 0.3` ⇒ scoped NEGATIVE RESULT closing the subresultant backend
for RT-1476.

### Proof track
Theorem to establish: *the backward 3-sum elimination ideal `⟨S3(x1,x2,u), S4(u,x3,x4,x5)⟩ ∩ F_p[u]`
has generator degree `O(q^{β})` with `β<3/10`.* Would follow from a Newton-polytope / mixed-volume
bound on the u-eliminant (note: uses mixed volume as an *analysis* tool, not as the batch1-A1
*algorithm*).

### Disproof track
Exhibit a family where the u-eliminant degree grows linearly in q (generic Bezout), i.e. `β=1`.

### Reproduction artifact
Contract `research/PO_batch2_A1_subresultant_backward_state_contract.md`; implementation
`experiments/ecdlp_prime_field/a1_subresultant_prs_degree_meter.sage`; result
`a1_backward_state_degree.json`; audit `a1_audit.py`; ledger ID **RT-1476-SUBRES-A1**.

---

## Candidate: A2 — Graphic-matroid cycle-basis large-prime enrichment (RT-1472 δ-meter)

### One-sentence mechanism
Exploit the **cycle space of the large-prime graph** as a graphic matroid, using a sparse cycle
basis (Horton/min-weight) to convert `Θ(L^2)` two-large-prime pair-advice into effective enrichment
`δ`, targeting the `δ>1/4` threshold RT-1472 proves would cross rho.

### Status
HYPOTHESIS.

### Novelty classification
LITERATURE-ADJACENT (two-large-prime graphs are classical, Fouque et al.; the **matroid cycle-basis
sparsifier as the enrichment operator** — vs batch2 A1's simplicial *homology* of a 3-uniform
hypergraph — is the new operation).

### Semantic fingerprint F(A2)
- algebraic object: graph `G` whose vertices are large primes, edges are partial relations carrying
  two large primes; matroid = cycle space of `G`.
- available public operations: relation generation with ≤2 uncontrolled large primes; graph algs.
- hidden structure exploited: **cycles in `G` = full relations**; a min-weight cycle basis packs the
  most relations per unit advice.
- information discarded: pair-advice not on any short cycle.
- information retained: a sparse cycle basis spanning the relation lattice.
- relation-generation primitive: partial relations with 2 large primes (birthday on the controlled
  part).
- compression primitive: **graphic-matroid cycle-basis extraction** (Horton set + Gaussian
  elimination over GF(2) then lift).
- rank mechanism: cycle-space dimension `|E|−|V|+c` is the effective relation count; this is the `δ`.
- descent mechanism: special-q on a target large prime (standard).
- dominant cost exponent: `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)` (RT-1472), improved iff enrichment `δ>1/4`.

### Nearest ledger entries
1. **RT-1472** — the theorem this feeds; A2 measures `δ`.
2. **P1473** (RT-1472 next action, costed FFE/summation implicit-membership preflight) — A2 supplies
   the *combinatorial* half (enrichment) the ledger requested alongside the membership half.
3. **batch2 A1 3-large-prime hypergraph homology** — same goal (RT-1472), **different object**:
   batch2 A1 uses `H_1` of a 3-uniform simplicial complex (3 large primes); A2 uses the cycle
   *matroid* of a 2-uniform graph (2 large primes). The precise distinction: homology counts
   independent 2-cycles in a hypergraph via boundary-map rank; matroid cycle basis counts
   independent circuits in a graph via graphic-matroid rank. These are different enrichment
   functionals with different `δ` scaling; batch2 A1's own gate is δ from 3-way coincidences, A2's
   is δ from 2-way cycle packing.
4. **ECFG-NR-308 / NR-304** (source-scheduling negatives) — confirm that *scheduling without an
   honest hit generator* is a negative control; A2 must carry an honest 2-large-prime generator, not
   a selector.
5. **batch2 A2 NFS two-sided** — also multi-factor-base relations; NFS builds two *independent*
   bases and matches; A2 stays single-base and enriches via cycles. Distinct compression.

### Nearest literature
Fouque–Joux–… two-large-prime variants; Horton 1987 (minimum cycle basis); Gaudry–Thomé–Thériault
(large-prime IC for curves). Gap: the enrichment exponent `δ` for the 2-LP cycle matroid on the
prime-field summation graph has not been measured against the RT-1472 threshold.

### Target family
As A1.

### Full algorithmic path
1. FB `L=q^{1/5}` (RT-1472 optimum region).
2. Generate partial relations carrying ≤2 large primes (birthday on controlled coords).
3. Build `G`; extract Horton min-weight cycle basis; each cycle → full relation via XOR/lift.
4. Relation probability: pair-support `Θ(L^2)`, edges `Θ(L+B)`.
5. Matrix: cycle-basis relations over `Z/n`, sparse.
6. Calibration: standard.
7. Descent: special-q.
8. Offline: graph build + cycle basis; Online: descent.
9. Memory: `O(|E|)`; cycle basis is near-linear.

### Cost model
RT-1472: without enrichment, exponent `2/3` at `ℓ=1/3`; enrichment `δ>1/4` needed to cross `1/2`.
A2 measures the realized `δ = log_L(#independent cycles / #edges advice)`. Compare vs rho, and vs the
implicit-deck alternative (setup `o(L)`, query `o(√L)`).

### Why existing negatives do not already kill it
The closed list names **"explicit two-large-prime advice graphs"** as a negative control — but that
control stores *explicit pair advice* `Θ(L^2)`; A2's new operation is to **never store the pairs**,
only the sparse cycle basis (`O(L)`), so the advice-cost term `2ℓ` in RT-1472 is replaced by the
cycle-basis cost. The obstruction avoided is the `Θ(L^2)` advice blow-up; the responsible operation
is min-cycle-basis sparsification.

### Likely fatal obstruction
The cycle-space dimension of a random sparse graph with `|E|≈|V|` is `Θ(|V|)`, giving `δ` no better
than the trivial single-large-prime yield — i.e. `δ≤1/4` and no crossing. Enrichment from cycles is
a constant-factor, not an exponent, in the birthday regime.

### Minimal falsifying experiment
Toy p ∈ {65521, 1000003, 16769023}. Build the 2-LP graph from an honest FFE/summation generator;
compute the min-cycle-basis dimension vs edge count; fit `δ`. Positive control: a planted-dense-graph
regime where δ is known >1/4. Negative control: Erdős–Rényi `G(n, n^{-1})` (δ→0 exponentially).

### Quantitative promotion gate
Measured `δ > 1/4` with flat/increasing trend across three sizes ⇒ promote. `δ ≤ 1/4` ⇒ scoped
NEGATIVE RESULT for the cycle-matroid enrichment of RT-1472.

### Proof track
Theorem: *the honest 2-LP summation graph at `L=q^{1/5}` has cycle-space dimension `Ω(L^{1+δ})` with
`δ>1/4`.* Requires a lower bound on short cycles in the summation incidence graph.

### Disproof track
Show the graph is a.a.s. a forest-plus-`O(1)`-cycles (δ=0) via the subcritical random-graph regime.

### Reproduction artifact
Contract `research/PO_batch2_A2_cycle_matroid_enrichment_contract.md`; impl
`experiments/ecdlp_prime_field/a2_cycle_basis_delta_meter.sage`; result `a2_cycle_delta.json`;
audit `a2_audit.py`; ledger ID **RT-1472-CYCLEMAT-A2**.

---

## Candidate: A3 — Many-target amortization crossover meter (offline/online separation)

### One-sentence mechanism
Exploit **factor-base reuse across `T` simultaneous targets** to amortize the offline relation-and-LA
cost, measuring whether the per-target online exponent can drop below rho's `1/2` for a
sub-exponential target count `T`.

### Status
HYPOTHESIS (meta-candidate: conditional on a working online descent such as A1/RT-1476).

### Novelty classification
LEDGER-NEW (the ledger repeatedly *warns* about amortization as a control — "preprocessing wins
whose target count loses to rho" — but never **costs the crossover** as a first-class experiment;
no idea report proposes an amortization meter).

### Semantic fingerprint F(A3)
- algebraic object: shared factor base + a batch of `T` targets `{T_i = [k_i]P}`.
- available public operations: EC ops; relation generation; sparse LA.
- hidden structure exploited: **offline cost is target-independent**; only descent is per-target.
- information discarded: nothing (accounting candidate).
- information retained: the full relation lattice and factor-base logs, reused `T` times.
- relation-generation primitive: whatever the online channel is (A1/A2 backend, or even the
  ledger's coordinate IC) — A3 is channel-agnostic.
- compression primitive: none new; amortization is a *cost-accounting* transform.
- rank mechanism: one shared sparse solve.
- descent mechanism: per-target special-q / backend descent.
- dominant cost exponent: `(offline)/T + (online per target)`; crossover when `offline/T < rho − online`.

### Nearest ledger entries
1. **ECFG-H533** (*"explicit many-target setup model"* named as the next viable move) — A3 is that
   model, made quantitative.
2. **RT-1476** — supplies the online descent exponent A3 needs as input.
3. **ECFG-NR-347 / NR-304** — "full-artifact source generation" negatives that show naive
   amortization *loses*; A3 must beat exactly these by separating offline from online honestly.
4. **batch1 A3 / batch2 A3** (backends) — A3 consumes a backend; it is not itself a backend.
5. Closed-territory bullet *"preprocessing wins whose offline cost, memory, advice, or target count
   loses to rho"* — A3's entire purpose is to find the exact `T` where this flips, if ever.

### Nearest literature
Hitchcock–Montague–Carter–Dawson (batch DLP amortization); Kuhn–Struik 2001 (rho for multiple
targets: `√(Tn)` for `T` targets, i.e. `√(T/n)` per target *worse* for large T — the baseline A3
must beat); Bernstein–Lange (batch discrete log). Gap: no prime-field IC amortization crossover has
been computed because no working online IC exists — A3 is conditional.

### Target family
As A1; plus the batch model with `T=q^τ` targets on the same curve/subgroup.

### Full algorithmic path
1–6. Offline (shared): factor base, relations, calibration — cost `C_off = q^{c_off}`.
7. Online: per-target descent, cost `q^{c_on}` each (from the chosen backend).
8. Separation: total `C_off + T·q^{c_on}`; per-target `C_off/T + q^{c_on}`.
9. Memory: store factor-base logs `O(L)` once.

### Cost model
Multi-target rho (Kuhn–Struik): `√(Tn)` total ⇒ per-target `√(n/T)` — *decreasing* in T, so rho
**already amortizes**. **This is the honest bar A3 must clear.** IC amortization beats rho only if
`C_off/T + q^{c_on} < √(n/T)`, i.e. needs `c_on < 1/2` (a genuine sub-rho *online* exponent, which
only RT-1476 could supply) AND `C_off/T` subdominant. So A3 is *strictly downstream* of A1/A2: with
no sub-rho online exponent, amortization cannot help (rho amortizes equally well).

### Why existing negatives do not already kill it
The negatives (NR-347, NR-304) killed amortization *with an over-rho online channel*. A3's new
content is the explicit statement+meter that amortization is **only** decisive when paired with
`c_on<1/2` — which reframes A1/A2 as the real prize and A3 as the multiplier. This is a scoping/
accounting contribution, not a standalone break.

### Likely fatal obstruction
Rho already amortizes to `√(n/T)` per target, so unless the IC online exponent is genuinely `<1/2`,
A3 provably cannot cross. A3 is dead the moment A1 and A2 both fail.

### Minimal falsifying experiment
Analytic + toy: plug measured `c_on` from A1/A2 into `C_off/T + q^{c_on}` vs `√(n/T)`; sweep `τ∈[0,1]`.
Toy p∈{65521,1000003}; verify the Kuhn–Struik multi-target rho constant empirically as the control.

### Quantitative promotion gate
Exists `τ<1` with `C_off/T + q^{c_on} < 0.886√(n/T)` using a *measured* `c_on<1/2` ⇒ promote. Else
scoped NEGATIVE RESULT (amortization is not an independent lever).

### Proof track
Theorem: *if the online IC descent exponent is `c_on<1/2`, then there is `τ*<1` such that batch IC
beats multi-target rho for `T≥q^{τ*}`.* (Elementary once `c_on` is a hypothesis.)

### Disproof track
Show `c_on≥1/2` for all known channels ⇒ A3 vacuous (the current state of the world).

### Reproduction artifact
Contract `research/PO_batch2_A3_amortization_crossover_contract.md`; impl
`experiments/ecdlp_prime_field/a3_amortization_meter.py`; result `a3_crossover.json`; ledger ID
**AMORT-A3**.

---

# Group B — Genuine representation changes

## Candidate: B1 — Modular-parametrization / Hecke factor base

### One-sentence mechanism
Exploit the **modular parametrization `φ: X_0(N) → E`** to represent points of `E(F_p)` as points on
the modular curve and generate relations from the **Hecke-operator action**, hoping the Hecke module
gives many cheap linear relations among factor-base logs.

### Status
CONJECTURE.

### Novelty classification
POSSIBLY NOVEL (see §5 literature grounding — no primary source uses modular parametrization or
Hecke action as an ECDLP index-calculus factor base).

### Semantic fingerprint F(B1)
- algebraic object: modular curve `X_0(N)`, Hecke algebra `T`, parametrization `φ` with conductor
  `N = cond(E)`.
- available public operations: `φ` and its dual `φ^`; Hecke correspondences `T_ℓ`.
- hidden structure exploited: **Hecke correspondences give many degree-`(ℓ+1)` self-maps** that act
  linearly on divisor classes — a potential source of relations unavailable on `E` alone.
- information discarded: the archimedean uniformization; keep only the mod-p reduction.
- information retained: the Hecke module structure of `J_0(N)`.
- relation-generation primitive: `T_ℓ`-orbits of factor-base points under `φ`-pullback.
- compression primitive: Hecke eigenform decomposition (block-diagonalizes the relation matrix).
- rank mechanism: Eichler–Shimura relation `T_ℓ = Frob_ℓ + ℓ Frob_ℓ^{-1}` on `J_0(N)`.
- descent mechanism: pull the target back through `φ` and Hecke-reduce.
- dominant cost exponent: dominated by the **cost of computing `φ^{-1}` mod p** and `N`'s size.

### Nearest ledger entries
1. **ISO-AR / ONK** (oriented-CM isogeny + Kani) — closest existing "auxiliary modular object" line,
   but ISO uses isogeny *volcanoes* to find weak curves; B1 uses the *modular curve* and Hecke
   *correspondences* to make relations. Distinction: isogeny graph vs Hecke graph; weak-curve-finding
   vs relation-generation.
2. **TRANSFER-NR-080 / PO-096ab** (trigonal cover, Prym) — B1 is an auxiliary *curve* too, but
   `X_0(N)` is not a cover *of `E` over `F_p`* (it covers via `φ` a degree-`deg φ` map with huge
   conductor); the mechanism is the Hecke action, absent from the cover track.
3. **batch2 B1 Kani genus-2 RM** — both use modular/RM structure; Kani glues torsion into a genus-2
   Jacobian to invoke Gaudry–Diem; B1 stays genus-1 on `E` and uses `X_0(N)`'s Hecke module. Distinct
   objects (genus-2 abelian surface vs `J_0(N)`) and distinct exploited structure (RM vs Hecke).
4. **batch1 C1 noncommutative CM-correspondence** — quiver of CM isogenies; B1's correspondences are
   Hecke, defined for *all* `E` (not just CM), which is the point.
5. **CM ideal factorization (0718 C3)** — class-group of `End(E)`; B1 uses `T`, the Hecke algebra of
   `J_0(N)`, a different (much larger) ring. Distinct algebraic object.

### Nearest literature
See §5 (literature agent). Eichler–Shimura; Wiles/BCDT modularity (guarantees `φ` exists for all
`E/Q`, but B1 needs it for `E/F_p` — reduction of a lift). Gap: no ECDLP use.

### Target family
Ordinary `E/F_p` that is the reduction of an `E/Q` with **small conductor `N`** (chosen/known lift).
Excluded: curves with no small-conductor lift (generic case — a likely fatal restriction).

### Full algorithmic path
1. **Factor base:** images `φ(Q_i)` of CM/Heegner points `Q_i ∈ X_0(N)(F_p)`.
2. **Relation generation:** apply `T_ℓ` to factor-base points; Eichler–Shimura gives a linear
   relation among `Frob`-images.
3. **Witness/verify:** check the relation on `E(F_p)` directly (exact).
4. **Relation probability:** governed by Hecke-orbit collisions.
5. **Matrix:** Hecke-eigenform block structure; potentially structured (Toeplitz-like per eigenform).
6. **Calibration:** factor-base logs.
7. **Descent:** `φ`-pullback of target + Hecke reduction.
8. **Offline/online:** compute `φ`, `T_ℓ` offline (needs `N`); descend online.
9. **Memory/parallel:** `J_0(N)` has dimension `~N/12` — **memory `Ω(N)` is the killer if `N` large.**

### Cost model
Setup dominated by `φ^{-1}` mod p and `dim J_0(N) ~ N`. If `N` is polynomial in `log p`, relations
are cheap; if `N ~ p` (generic), setup is `≥ p`, catastrophically worse than rho. Compare vs rho
`0.886√n`.

### Why existing negatives do not already kill it
No ledger negative touches Hecke correspondences; the transfer track's "same-field cover" negative
(Diem) does not apply because `X_0(N) → E` is not a cover *of `E`* in the Weil-descent sense (it is a
parametrization with the Hecke module attached). The new operation is the Hecke action as a relation
source.

### Likely fatal obstruction
**Conductor size.** For a random ordinary `E/F_p`, the smallest lift has conductor `N` polynomial in
`p` (often `Θ(p)`), so `dim J_0(N) = Θ(p)` and every step costs `≥ p ≫ √n`. Also `φ^{-1}` is a full
fiber of degree `deg φ`. B1 can only ever apply to the measure-zero family of small-conductor curves
(a negative control for *deployed* curves).

### Minimal falsifying experiment
Pick tiny-conductor curves `N∈{11,14,15,17}` reduced mod small primes `p`; build `φ` and `T_ℓ`
explicitly (Sage `ModularSymbols`); measure how many independent `E(F_p)`-relations the Hecke action
yields per unit cost, and how the yield scales as `N` grows across a family. Positive control: a CM
curve with small `N`. Negative control: force `N ~ p` and confirm blow-up.

### Quantitative promotion gate
Independent relations per point `> 1` at cost `< √n` **with a construction that does not require
`N=o(p)`** across three sizes. (Almost certainly fails the `N`-condition — but the experiment
precisely maps *which* structure the conductor destroys.)

### Proof track
Theorem needed: *there is an efficiently computable `φ`-pullback and Hecke relation generator with
setup `o(√n)` for a positive-density family of ordinary `E/F_p`.* (Expected to be **false** — the
value is the sharp negative.)

### Disproof track
Show `dim J_0(N) = Θ(N)` and `N = Ω(p^{1−ε})` for a.a. ordinary `E/F_p` ⇒ setup `Ω(p^{1−ε}) ≫ √n`.

### Reproduction artifact
Contract `research/PO_batch2_B1_modular_hecke_contract.md`; impl
`experiments/ecdlp_prime_field/b1_hecke_relation_yield.sage`; result `b1_hecke_yield.json`; ledger ID
**MODHECKE-B1**.

---

## Candidate: B2 — Drinfeld-module / function-field transport

### One-sentence mechanism
Exploit the **function-field analogy** by seeking an efficiently computable homomorphism from the
order-`n` subgroup of `E(F_p)` into a **rank-2 Drinfeld-module discrete log over `F_p[t]`**, where
function-field index calculus is subexponential, thereby transporting ECDLP to an easier category.

### Status
CONJECTURE (expected negative; value is a precise transport-impossibility boundary — pairs D1).

### Novelty classification
POSSIBLY NOVEL (no known algebraic map E(F_p)→Drinfeld-DLP; see §5).

### Semantic fingerprint F(B2)
- algebraic object: rank-2 Drinfeld `F_p[t]`-module `Φ`, its DLP in `Φ(K)` for `K/F_p(t)`.
- available public operations: EC group law; (hypothetical) transport map `ψ`.
- hidden structure exploited: **subexponential IC exists for Drinfeld-module DLP** (Carlitz-style
  smoothness in `F_p[t]`).
- information discarded: none intended (must be injective on the n-subgroup).
- information retained: the full order-n structure, re-encoded in `F_p[t]`.
- relation-generation primitive: function-field smoothness of divisors (in the target category).
- compression primitive: FF-IC linear algebra.
- rank mechanism: FF-IC relation matrix.
- descent mechanism: FF individual log.
- dominant cost exponent: subexponential `L_?(1/2)` **if** the transport `ψ` exists and is cheap.

### Nearest ledger entries
1. **PO-transfer track** (transfer/decomposition) — the *closest philosophy* (move ECDLP to an easier
   object), but all transfer entries stay in the elliptic/Jacobian/cover world over `F_p`; none maps
   to a Drinfeld module. Distinct target category.
2. **ISO track** (isogeny transport) — transports within the isogeny class (same category); B2 leaves
   the category entirely.
3. **batch2 B1 Kani genus-2** — transports to a genus-2 Jacobian (still an abelian variety over
   `F_p`); B2 transports to an `F_p[t]`-module (function-field object). Different category.
4. **NR-033 / T-ISO-4** (no weak isogenous B) — a transport-*within*-category negative; B2 asks the
   orthogonal question of transport *across* categories.
5. **MOV/Frey–Rück** (known special case in AGENTS.md) — the only successful transport (to `F_{p^k}^*`
   via pairing); B2 asks whether a Drinfeld analogue of the pairing exists. Distinction: MOV needs
   small embedding degree; B2 needs a Drinfeld transport that is the object of the search.

### Nearest literature
See §5. Scanlon; Papikian (Drinfeld modules); function-field DLP subexponential (Adleman–Huang,
Enge–Gaudry). Gap: no map from an elliptic-curve group over `F_p` to a Drinfeld-module DLP is known;
the analogy is structural, not functorial.

### Target family
Ordinary `E/F_p`, prime `n`. Excluded special cases: anomalous, supersingular (those have their own
transports).

### Full algorithmic path
1. **Transport `ψ`:** *(the missing stage)* — construct/search for an efficiently computable
   `ψ: ⟨P⟩ → Φ(K)` respecting the group law. **If `ψ` does not exist, candidate is INCOMPLETE by
   design** (this is the point: locate the obstruction).
2–9. Conditional on `ψ`: standard FF-IC (factor base of low-degree places, relation smoothness,
   sparse LA, FF individual log).

### Cost model
Conditional subexponential `L_p(1/2)` in the *target* category — but the **transport cost is
unbounded/unknown**, and if `ψ` requires solving ECDLP to define, the whole thing is circular.
Compare vs rho.

### Why existing negatives do not already kill it
No ledger negative addresses cross-category transport to function-field modules. The new operation is
the *search for a functor*, which no prior entry attempts.

### Likely fatal obstruction
**No functorial map exists.** `E(F_p)` is a *fixed finite abelian group* with no natural `F_p[t]`-
module structure; any injection into a Drinfeld-module DLP that respects `+` would itself be a group
isomorphism onto a cyclic subgroup, computable only by *already solving* the DLP (the "embed into an
easier group" fallacy — the same reason MOV needs the pairing, an *external* bilinear map, not an
embedding). B2 will almost surely reduce to: *the only cross-category transports are pairings, and
pairings land in `F_{p^k}^*` (MOV), not Drinfeld modules.*

### Minimal falsifying experiment
Formal/structural, with a tiny toy check: enumerate all `F_p`-algebra maps and additive maps between
a small `E(F_p)` (n∈{7,11,13}) and small rank-2 Drinfeld modules; confirm the only group
homomorphisms are the trivial/DLP-solving ones. Positive control: MOV pairing into `F_{p^k}^*`
(exists, uses a bilinear map, not an embedding). Negative control: random finite group pair (no
structured map).

### Quantitative promotion gate
An efficiently computable, injective, group-law-respecting `ψ` with construction cost `o(√n)`. (Almost
certainly non-existent — promotion gate is effectively a challenge to produce the map.)

### Proof track
Theorem (the prize even if `ψ` doesn't exist): *any group homomorphism `⟨P⟩ → Φ(K)` computable in
time `o(√n)` implies an `o(√n)` DLP solver* (self-referential impossibility) — pairs D1.

### Disproof track
Exhibit `ψ` (would be a genuine break — extremely unlikely). More realistically, prove D1.

### Reproduction artifact
Contract `research/PO_batch2_B2_drinfeld_transport_contract.md`; impl
`experiments/ecdlp_prime_field/b2_transport_functor_search.sage`; result `b2_transport.json`; ledger
ID **DRINFELD-B2**.

---

## Candidate: B3 — Ritt/Dickson map-decomposition factor base on the Kummer line

### One-sentence mechanism
Exploit a hypothetical **Ritt decomposition of the multiplication-by-`m` Lattès map** on the Kummer
x-line into commuting low-degree factors, defining a **Dickson-smooth factor base** in which scalar
multiplication becomes a composition of cheap dynamical maps yielding relations.

### Status
CONJECTURE (expected negative via Ritt-indecomposability — pairs D3).

### Novelty classification
LITERATURE-ADJACENT to batch1 C2 (Lattès *transfer-operator spectrum*), but the mechanism —
**Ritt/functional decomposition of the map itself**, not the spectrum of its transfer operator — is
POSSIBLY NOVEL (see §5).

### Semantic fingerprint F(B3)
- algebraic object: the Lattès map `f_m(x) = x([m]P)` on `P^1` (Kummer line); division polynomials.
- available public operations: x-only ladder `x([m]P) = f_m(x)`; polynomial composition.
- hidden structure exploited: **if `f_m = g ∘ h` with `g,h` low-degree**, smoothness in the
  decomposition monoid gives relations.
- information discarded: the y-coordinate/sign (Kummer quotient).
- information retained: the x-line dynamical structure.
- relation-generation primitive: factor a factor-base x-coordinate through the commuting-map
  decomposition (Ritt second theorem structure).
- compression primitive: functional decomposition (Ritt/Zannier normal form).
- rank mechanism: relations among "Dickson-smooth" x-values.
- descent mechanism: express `x(T)` via the same decomposition.
- dominant cost exponent: governed by whether nontrivial low-degree factors exist.

### Nearest ledger entries
1. **batch1 C2 Lattès transfer-operator spectral descent** — same map `f_m`, **different invariant**:
   transfer-operator *spectrum* (analysis) vs *functional decomposition* (algebra). Different failure
   mode: spectral gap vs indecomposability.
2. **RT-1485 Kummer companion state** — same x-line/Kummer object; RT-1485 studies the *pair state*
   `(x(A+B),x(A−B))`, B3 studies the *iterate* decomposition of `[m]`. Distinct.
3. **ECFG** coordinate IC — uses x-line coordinates as a factor base; B3 adds a *dynamical
   composition law* on them, which ECFG lacks.
4. **batch1 A2 EDS smoothness** — also an x-line/division-polynomial "smoothness," but EDS factors
   *net values*; B3 factors the *map* into commuting components. Distinct smoothness monoid.
5. **batch1 B3 tropical** — also a Kummer/valuation object; B3 is a functional-decomposition, not a
   valuation, mechanism.

### Nearest literature
Ritt 1922 (functional decomposition); Zannier; Pakovich (Lattès decomposition); Ghioca–Tucker–Zieve
(commuting maps / arithmetic dynamics). Known: Lattès maps are generically **indecomposable** except
via the isogeny/CM structure. Gap: whether *any* deployed-curve `f_m` decomposes usefully.

### Target family
Ordinary `E/F_p`, `j∉{0,1728}` (no extra automorphisms), non-CM (CM would allow endomorphism
decomposition — but that's the covered CM lane).

### Full algorithmic path
1. **Factor base:** x-values that are "Dickson-smooth" (factor through the decomposition).
2. **Relation gen:** compose cheap factors to hit factor-base elements.
3. **Verify:** exact x-ladder check.
4. **Probability:** smoothness density in the decomposition monoid.
5. **Matrix:** relations over `Z/n`.
6. **Calibration:** factor-base logs.
7. **Descent:** decompose `x(T)`.
8. **Offline/online:** decomposition offline; descent online.
9. **Memory/parallel:** small.

### Cost model
If `f_m` decomposed into `O(log m)` degree-`O(1)` maps, relations would be near-free — a genuine
exponent change. But Ritt theory says Lattès maps of a non-CM curve are **indecomposable** beyond the
trivial `[m]=[m1]∘[m2]` (which just re-encodes the scalar and gives nothing). Compare vs rho.

### Why existing negatives do not already kill it
The Lattès transfer-operator negative (batch1 C2, folded into a class-function barrier) addresses the
*spectrum*; it does not address *functional decomposition*. The new operation is Ritt normal-form
factoring of `f_m`.

### Likely fatal obstruction
**Ritt indecomposability.** `[m] = [m1]∘[m2]` is the *only* decomposition, and it recurses to the same
DLP — no smoothness gain (Pakovich: Lattès decompositions come only from the multiplicative structure
of `m`, i.e. from isogenies already known). D3 formalizes this.

### Minimal falsifying experiment
Toy p∈{1009,65521,1000003}, several ordinary non-CM curves; symbolically factor `f_m` (division
polynomial ratios) for small `m` via Sage `pari` functional decomposition; count nontrivial
decompositions beyond `m=m1·m2`. Positive control: a CM curve (should show endomorphism-induced
extra factors — the covered lane). Negative control: `j` generic (expect none).

### Quantitative promotion gate
A nontrivial low-degree decomposition of `f_m` **not** coming from `m=m1·m2`, giving smoothness
density `> q^{-1/2}` in the decomposition monoid. (Expected zero — the value is the sharp
indecomposability negative D3.)

### Proof track
Theorem (=D3): *for ordinary non-CM `E/F_p`, `f_m` is indecomposable in `F_p(x)` up to `[m]=[m1]∘[m2]`.*

### Disproof track
Exhibit one curve with an extra decomposition ⇒ opens a new smoothness lane.

### Reproduction artifact
Contract `research/PO_batch2_B3_ritt_dickson_contract.md`; impl
`experiments/ecdlp_prime_field/b3_lattes_decomposition.sage`; result `b3_ritt.json`; ledger ID
**RITT-B3**.

---

# Group C — High-risk speculative mechanisms

## Candidate: C1 — Non-backtracking isogeny-expander walk relation harvester

### One-sentence mechanism
Exploit the **Ramanujan spectral gap of the `ℓ`-isogeny graph** (Pizer) to run a non-backtracking
random walk that mixes in `O(log q)` steps, hoping the fast mixing yields distinguished-point
relations at a rate that beats the birthday bound.

### Status
HYPOTHESIS (expected: mixing speed does not beat birthday — a precise, valuable negative).

### Novelty classification
POSSIBLY NOVEL as a *relation/collision* mechanism (isogeny graphs are used for hashing/CSIDH and for
weak-curve finding in the ISO track, **not** for beating birthday-bound DLP collision search; see §5).

### Semantic fingerprint F(C1)
- algebraic object: the `ℓ`-isogeny graph `G_ℓ(F_p)` (Ramanujan, degree `ℓ+1`).
- available public operations: apply an `ℓ`-isogeny; evaluate on points.
- hidden structure exploited: **spectral gap `1 − 2√ℓ/(ℓ+1)`** ⇒ `O(log)` mixing.
- information discarded: the specific isogeny path.
- information retained: endpoint curve + transported point.
- relation-generation primitive: non-backtracking walk to distinguished nodes; match transported
  point coordinates.
- compression primitive: distinguished-point collision.
- rank mechanism: collisions → relations in `⟨P⟩`.
- descent mechanism: walk from the target.
- dominant cost exponent: the object of test — does fast mixing change the collision exponent from
  `1/2`?

### Nearest ledger entries
1. **ISO-AR / ONK / IKD** — uses the isogeny graph, but to **find a weak curve** (structural), not to
   **harvest collisions** (dynamical). Distinct goal; NR-033 says no weak curve exists, which C1
   sidesteps because C1 doesn't need a weak endpoint — it needs a collision.
2. **batch1 C2 Lattès transfer operator** — also a "spectral gap on a dynamical graph," but on the
   *Lattès* self-map, not the *isogeny* graph. Different graph, different walk.
3. **batch1 C1 noncommutative CM-correspondence** — isogeny *composition algebra*; C1 is a *random
   walk*, not an algebra. Distinct.
4. **rho baseline** — rho is itself a random walk on `⟨P⟩`; C1 asks whether an isogeny-graph walk
   mixes "more usefully." The exact distinction: rho's walk is on the group (mixing is irrelevant —
   collisions are birthday); C1's walk is on curves, and the question is whether curve-mixing
   *transports* to faster point-collisions.
5. **VW parallel collision** — the baseline C1 must beat; C1 adds isogeny structure to the walk.

### Nearest literature
Pizer 1990 (Ramanujan isogeny graphs); Charles–Goren–Lauter 2009 (CGL hash — uses non-backtracking
walk, but for *hashing/one-wayness*, explicitly NOT for DLP speedup). Gap: no claim that expander
mixing beats birthday for DLP.

### Target family
Ordinary `E/F_p` (its isogeny volcano is flat per the CM-structure memo — a possible obstruction).

### Full algorithmic path
1. Factor base: distinguished endpoint curves.
2. Relation gen: non-backtracking `ℓ`-walk transporting `[a]P+[b]Q`; record at distinguished nodes.
3. Verify: transported point equality (exact).
4. Probability: collision at distinguished nodes.
5–7. relations / LA / descent as in rho-IC hybrid.
8–9. offline walks; online target walk; memory = distinguished-point table.

### Cost model
Mixing gives *uniform* endpoints in `O(log)` steps, but the number of *distinct* endpoint states is
`O(p/ℓ)` (class number of the order), and collisions among transported points remain birthday
`√(#states)`. **Prediction:** exponent stays `1/2`; the spectral gap changes constants, not the
exponent — because expander mixing bounds *distribution distance*, not *collision count below
birthday*. Compare vs rho, VW.

### Why existing negatives do not already kill it
The ISO negatives (no weak curve) target *structure*; C1 targets *collision rate* and does not need a
weak curve. No ledger entry tests whether the isogeny-graph spectral gap beats birthday.

### Likely fatal obstruction
**Expander mixing ≠ sub-birthday collisions.** Faster mixing to uniform does not reduce the number of
samples needed for a collision below `√(state space)`; the birthday exponent `1/2` is
mixing-independent. Also the flat ordinary volcano gives few horizontal isogenies.

### Minimal falsifying experiment
Toy p∈{1009,65521,1000003}; build `G_ℓ`, run non-backtracking walks, measure distinguished-point
collision count vs steps; fit the exponent. Positive control: a graph where a planted short cycle
gives sub-birthday collisions. Negative control: rho on `⟨P⟩` (exponent `1/2` exactly).

### Quantitative promotion gate
Measured collision exponent `< 1/2 − ε` across three sizes. (Expected `=1/2` — precise negative that
spectral gap is a constant-factor lever, closing an intuitive but wrong hope.)

### Proof track
Theorem: *non-backtracking walk collision time on `G_ℓ` is `Θ(√{#vertices})` regardless of spectral
gap* (birthday is gap-independent).

### Disproof track
Exhibit a walk with sub-birthday collisions (would be a genuine surprise).

### Reproduction artifact
Contract `research/PO_batch2_C1_isogeny_expander_walk_contract.md`; impl
`experiments/ecdlp_prime_field/c1_isogeny_walk_collision.sage`; result `c1_walk.json`; ledger ID
**ISOWALK-C1**.

---

## Candidate: C2 — Pink–Zilber unlikely-intersection anomalous-relation search

### One-sentence mechanism
Exploit **unlikely-intersection theory** (Mordell–Lang / bounded-height) to test whether
x-coordinates of small multiples `{x([i]P)}` lie in an anomalous subvariety of a power `E^k`,
yielding **algebraic relations cheaper than random** among factor-base logs.

### Status
CONJECTURE (expected negative; sharpens why no anomalous structure exists — pairs the barrier menu).

### Novelty classification
POSSIBLY NOVEL (no cryptographic use of unlikely-intersection theory for ECDLP relations; see §5).

### Semantic fingerprint F(C2)
- algebraic object: powers `E^k`, subvarieties, torsion/small-height points.
- available public operations: EC ops; height/coordinate evaluation.
- hidden structure exploited: **anomalous subvarieties** (dimension higher than expected in a
  torsion-coset intersection) would host many relations.
- information discarded: generic points off the subvariety.
- information retained: points on the anomalous locus.
- relation-generation primitive: detect coplanarity/algebraic dependence among `{[i]P}` images.
- compression primitive: the defining equations of the anomalous locus.
- rank mechanism: relations from the subvariety's linear structure.
- descent mechanism: locate the target's image on the locus.
- dominant cost exponent: governed by whether anomalous loci exist at useful density.

### Nearest ledger entries
1. **batch1 A1 BKK / batch1 A3 incidence** — both about algebraic coincidences among point-images;
   C2 asks whether *unlikely* (higher-than-expected) coincidences exist by arithmetic-geometry
   theory, not by counting/incidence. Distinct: existence theorem vs counting algorithm.
2. **0718 C1 approximate-homomorphism stability** — both about "structure among small-multiple
   images"; stability is additive-combinatorial (Bogolyubov), C2 is arithmetic-geometric (Zilber–
   Pink). Distinct machinery.
3. **ECFG coordinate coincidences** — the whole ECFG lane finds coordinate coincidences empirically;
   C2 asks whether theory *predicts* a dense anomalous family. Distinct: empirical vs theoretical.
4. **Xedni (batch1 C3)** — global height lattice; C2 uses bounded-height/unlikely-intersection,
   related but Xedni *lifts to a height lattice over Q* while C2 works with torsion cosets in `E^k`
   over `F_p`'s lift. Distinct object.
5. **Manin–Mumford** (torsion points on subvarieties) — the closest theorem; C2 asks the
   *DLP-relation* analogue.

### Nearest literature
Zilber; Pink; Bombieri–Masser–Zannier (anomalous subvarieties); Habegger–Pila. Gap: all results are
*finiteness* theorems (few anomalous points) — which **predicts the mechanism fails** but has never
been stated as an ECDLP-relation obstruction.

### Target family
Ordinary `E/F_p`, prime order.

### Full algorithmic path
1. Factor base: `{x([i]P)}` for small `i`.
2. Relation gen: test membership of the tuple in candidate anomalous subvarieties of `E^k`.
3–9. If a dense anomalous family existed: relations, LA, descent. **If not (expected), the candidate
   is a structured negative.**

### Cost model
Unlikely-intersection theorems say anomalous points are **finite/sparse** ⇒ relation yield
`o(1)` ⇒ no exponent gain. Compare vs rho.

### Why existing negatives do not already kill it
No ledger entry invokes Zilber–Pink; the new operation is testing an arithmetic-geometry existence
theorem as a relation source.

### Likely fatal obstruction
**Finiteness of anomalous intersections** (Bombieri–Masser–Zannier): exactly the theorems that make
the mechanism fail — anomalous loci are too sparse to seed a factor base. This is the sharp negative.

### Minimal falsifying experiment
Toy: for small `E(F_p)` and small `k`, exhaustively search for algebraic dependencies among
`{x([i]P)}` beyond the trivial ones; measure density vs the random baseline. Positive control: CM
curve (extra endomorphism relations — the covered lane). Negative control: generic `j` (expect
random-baseline density).

### Quantitative promotion gate
Anomalous-relation density `> q^{-1/2}` and non-CM. (Expected below — precise negative.)

### Proof track
Theorem: *the number of non-trivial algebraic dependencies among `{x([i]P)}_{i≤B}` is `O(B^{ε})` for
non-CM `E`* (a Zilber–Pink-flavored bound).

### Disproof track
Find a non-CM curve with `Ω(B)` anomalous dependencies (would be revolutionary).

### Reproduction artifact
Contract `research/PO_batch2_C2_unlikely_intersection_contract.md`; impl
`experiments/ecdlp_prime_field/c2_anomalous_locus_search.sage`; result `c2_anomalous.json`; ledger ID
**ZILBERPINK-C2**.

---

## Candidate: C3 — Coleman–Gross p-adic height-pairing relation lattice

### One-sentence mechanism
Exploit the **Coleman–Gross p-adic height pairing** at an auxiliary prime as a computable bilinear
form that partially *linearizes* the group law, generating a **p-adic relation lattice** whose short
vectors are ECDLP relations.

### Status
CONJECTURE (high-risk; expected negative bounded by height-regulator size).

### Novelty classification
LITERATURE-ADJACENT to batch2 C2 (p-curvature/holonomy) and batch1 C3 (archimedean height lattice /
Xedni), but the **p-adic *height pairing*** as a bilinear relation source is a distinct object
(POSSIBLY NOVEL — see §5).

### Semantic fingerprint F(C3)
- algebraic object: `E/Q_ℓ` (a lift), Coleman–Gross height pairing `⟨·,·⟩_p: E(Q_ℓ)×E(Q_ℓ)→Q_p`.
- available public operations: EC ops; Coleman integration; height evaluation.
- hidden structure exploited: **bilinearity** of the height pairing gives *linear* relations among
  logs (a partial homomorphism to `(Q_p,+)`).
- information discarded: the non-linear part of the group law.
- information retained: the p-adic linear image.
- relation-generation primitive: LLL on the lattice of height vectors of factor-base points.
- compression primitive: lattice reduction.
- rank mechanism: rank of the height-vector lattice (bounded by the Mordell–Weil rank of the lift —
  the likely killer).
- descent mechanism: express target's height vector in the reduced basis.
- dominant cost exponent: governed by the p-adic precision / regulator size.

### Nearest ledger entries
1. **batch2 C2 p-curvature/holonomy** — both p-adic/arithmetic-differential; p-curvature is a
   *connection* invariant, Coleman–Gross is a *height pairing*. Distinct bilinear objects.
2. **batch1 C3 Xedni height lattice** — both "height lattice"; Xedni is *archimedean/global* over Q,
   C3 is *p-adic local*. Distinct valuation.
3. **Smart/anomalous attack** (AGENTS.md special case) — the *only* case where a p-adic log linearizes
   ECDLP (when `p∣#E`); C3 asks whether the *height pairing* (not the formal log) gives partial
   linearization for *non*-anomalous curves. The distinction is the crux and the likely wall.
4. **MOV/Frey–Rück** — pairing-based transport; the height pairing is a different (p-adic, symmetric)
   pairing.
5. **batch1 B1 dual-number jet** — also a "linearization" idea; jets are infinitesimal, the height
   pairing is global-p-adic. Distinct.

### Nearest literature
Coleman–Gross 1989 (p-adic heights); Mazur–Stein–Tate (computation); Balakrishnan (Coleman
integration). Gap: never used for ECDLP relations; the pairing is `Q_p`-valued with rank bounded by
MW rank.

### Target family
Ordinary `E/F_p` with a lift `E/Q` of controllable MW rank; ordinary reduction at the auxiliary
prime.

### Full algorithmic path
1. Factor base: points with computable p-adic heights.
2. Relation gen: LLL on height vectors → integer relations.
3. Verify: exact on `E(F_p)`.
4. Probability: governed by height-lattice density.
5. Matrix: reduced lattice.
6–9. calibration/descent/offline/memory standard.

### Cost model
The height pairing maps into `Q_p^r` with `r = ` MW rank of the lift, which is `O(1)` (generically
0–1) — so the linear image is **too low-dimensional** to encode the order-`n` DLP; relations collapse
to the trivial. Compare vs rho.

### Why existing negatives do not already kill it
Neither the p-curvature nor the archimedean-height entries use the *p-adic height pairing*; the new
operation is LLL on Coleman–Gross height vectors.

### Likely fatal obstruction
**Mordell–Weil rank bound.** The height pairing's image has dimension = MW rank `= O(1)`, far too
small to separate the `n` group elements; the pairing does not injectively linearize `⟨P⟩` (same
reason MOV needs a *full* bilinear pairing into a big field). For anomalous curves the formal log
already works (known); for ordinary non-anomalous, the height image is rank-bounded and useless.

### Minimal falsifying experiment
Toy: small `E/Q` of known rank, reduce mod small `p`; compute p-adic heights of factor-base points;
LLL; count non-trivial relations vs random. Positive control: anomalous curve (formal log works).
Negative control: rank-0 lift (height pairing trivial).

### Quantitative promotion gate
Non-trivial relation yield `> q^{-1/2}` for a *non-anomalous, bounded-rank* family. (Expected
below — precise negative tying the failure to the MW-rank bound.)

### Proof track
Theorem: *the Coleman–Gross height map `⟨P⟩ → Q_p^r` with `r=O(1)` cannot inject the order-n subgroup,
so its relation lattice has rank `O(1)`.*

### Disproof track
A non-anomalous family where the height lattice has rank `Ω(log n)` (unexpected).

### Reproduction artifact
Contract `research/PO_batch2_C3_padic_height_lattice_contract.md`; impl
`experiments/ecdlp_prime_field/c3_coleman_gross_lattice.sage`; result `c3_height.json`; ledger ID
**PADICHT-C3**.

---

# Group D — Negative-theory candidates (expose precise loopholes/barriers)

## Candidate: D1 — Cross-category transport-injection barrier (↔ B1, B2)

### One-sentence mechanism
Prove that **any efficiently computable, group-law-respecting injection** of `⟨P⟩` into a group `G`
with subexponential DLP would itself yield a sub-`√n` DLP solver — so no transport (modular, Drinfeld,
function-field) can help *unless* it is an external bilinear pairing (MOV-type).

### Status
CONJECTURE (a restricted-model theorem is the target).

### Novelty classification
LEDGER-NEW (the ledger has scoped transfer negatives — NR-033, TRANSFER-NR-080 — but no general
transport-injection lower bound; batch2 D-barriers cover crystalline order-only and Gaudry
fixed-genus, not cross-category injection).

### Semantic fingerprint F(D1)
- algebraic object: abstract cyclic group `⟨P⟩` of order `n`; a candidate target group `G`.
- exploited structure (to *forbid*): any injective homomorphism `ψ`.
- key distinction from prior barriers: batch2 D1 (generic-model MITM) forbids *representation-MITM*;
  D1 forbids *cross-category embeddings*. Different model, different forbidden object.
- dominant statement: `ψ` computable in `o(√n)` ⇒ DLP in `o(√n)` (self-reduction).

### Nearest ledger entries
1. **NR-033 / T-ISO-4** — "no weak isogenous curve": transport *within* the isogeny class fails; D1
   generalizes to *any* category.
2. **batch2 D2 crystalline order-only barrier** — forbids linear/spectral order-only representations;
   D1 forbids *injective transports*. Complementary, distinct.
3. **class-function no-leakage (0718 D1)** — forbids *class-function* representations; D1 forbids
   *homomorphic embeddings*. Distinct forbidden class.
4. **MOV/Frey–Rück** — the *exception* D1 must carve out (pairings are bilinear maps, not
   embeddings): D1 must precisely separate "embedding" (forbidden) from "pairing" (the known
   exception).
5. **generic-group lower bound (Shoup)** — D1 is a *non-generic* companion: it forbids a *specific
   representation-level* transport, complementing Shoup's generic bound.

### Nearest literature
Shoup 1997; Maurer–Wolf (DLP self-reductions); Boneh–Lipton (black-box fields). Gap: no theorem
distinguishing embedding-transports (forbidden) from pairing-transports (MOV) for prime-field ECDLP.

### Target family / path / cost
Model-bound theorem; no algorithmic stages (barrier). The "experiment" is a proof + a toy check that
all small-group embeddings into easier groups require solving the DLP.

### Why existing negatives do not already kill it (i.e., why prove it)
Because B1/B2 keep tempting the transport idea; D1 closes it precisely and identifies the *only*
loophole (external bilinear pairings with small embedding degree — already the MOV special case).

### Likely obstruction to the *proof*
Carving out the pairing exception cleanly (a pairing is a bilinear map `⟨P⟩×⟨P⟩→G`, not an injection
`⟨P⟩→G`); the theorem must be stated for injections/homomorphisms only.

### Minimal falsifying experiment / disproof track
A cross-category efficiently-computable injection with `o(√n)` construction that is *not* a pairing
(would refute D1 and be a real break).

### Proof track
Reduce: given `ψ` and a subexp DLP oracle in `G`, solve DLP in `⟨P⟩`; bound construction+query.

### Reproduction artifact
`research/PO_batch2_D1_transport_injection_barrier_theory.md`; ledger ID **BAR-TRANSPORT-D1**.

---

## Candidate: D2 — Amortization / preprocessing lower bound (↔ A3)

### One-sentence mechanism
Prove that in the structured-generic + advice model, **single-target prime-field ECDLP cannot beat
multi-target rho's `√(n/T)`** via preprocessing/many-target amortization **unless** the online IC
descent exponent is genuinely `<1/2` — i.e. amortization is not an independent lever.

### Status
CONJECTURE.

### Novelty classification
LEDGER-NEW (the closed-territory list *warns* about preprocessing loopholes but states no theorem;
A3 is the meter, D2 is the bound).

### Semantic fingerprint F(D2)
- algebraic object: batch of `T` targets, shared advice string of bounded length.
- exploited structure (to bound): offline/online tradeoff.
- distinction from prior barriers: D2 bounds *amortization*, not *representation* — a new axis.
- dominant statement: online exponent `≥1/2` ⇒ batch IC `≥` multi-target rho for all `T`.

### Nearest ledger entries
1. **ECFG-H533** (many-target model) — D2 bounds exactly this.
2. **ECFG-NR-347 / NR-304** — empirical amortization failures; D2 explains them as a theorem.
3. **RT-1476 / RT-1472** — the conditional theorems; D2 shows amortization is downstream of them.
4. **batch2 D-barriers** — representation barriers; D2 is a *resource* (advice/preprocessing) barrier.
5. Kuhn–Struik multi-target rho — the baseline D2 formalizes as unbeatable-by-amortization-alone.

### Nearest literature
Corrigan-Gibbs–Kogan (preprocessing DLP lower bounds!); Mihalcik; Bernstein–Lange (batch DL). Gap:
those bound *generic* preprocessing; D2 targets the *non-generic IC* amortization crossover
specifically, tied to the online exponent.

### Path / cost
Barrier; the "experiment" is the A3 meter plus a proof in the advice model.

### Why prove it
To stop amortization from being mistaken for an independent breakthrough lane; it channels effort back
to the online exponent (RT-1476).

### Likely obstruction to proof
Corrigan-Gibbs–Kogan-style bounds are generic; extending to the structured-generic IC model requires
care about what advice the factor base constitutes.

### Disproof track
A preprocessing scheme with over-`1/2` online exponent that still beats multi-target rho (would refute
D2).

### Proof track
Show any advice of length `S` with online time `T_on` obeys `S·T_on ≥ n` (CGK-style), then combine
with the multi-target rho bound.

### Reproduction artifact
`research/PO_batch2_D2_amortization_lower_bound_theory.md`; ledger ID **BAR-AMORT-D2**.

---

## Candidate: D3 — Lattès Ritt-indecomposability barrier (↔ B3)

### One-sentence mechanism
Prove that for ordinary **non-CM** `E/F_p`, the multiplication-by-`m` Lattès map `f_m` is
**functionally indecomposable** over `F_p(x)` beyond `[m]=[m1]∘[m2]`, so no Dickson-smooth factor
base can exist.

### Status
CONJECTURE (largely follows from Pakovich's classification — a matter of stating it in the ECDLP
model).

### Novelty classification
LEDGER-NEW (no ledger entry states a functional-decomposition barrier; batch1 C2's Lattès entry is a
spectral, not decomposition, statement).

### Semantic fingerprint F(D3)
- algebraic object: Lattès map `f_m ∈ F_p(x)`.
- exploited structure (to forbid): nontrivial commuting decomposition.
- distinction: forbids *functional decomposition* (B3's mechanism), a new forbidden operation.
- dominant statement: `f_m = g∘h` ⇒ the decomposition comes from `m=m1·m2` (no smoothness gain).

### Nearest ledger entries
1. **batch1 C2 Lattès spectral** — same map, spectral barrier; D3 is the decomposition barrier.
2. **RT-1485 Kummer state** — same x-line object; D3 is about iterates, RT-1485 about pair states.
3. **CM ideal factorization (0718 C3)** — the CM case is where decompositions *do* come from
   endomorphisms; D3 excludes non-CM precisely to separate the covered CM lane.
4. **batch1 A2 EDS** — division-polynomial structure; D3 bounds what that structure can decompose.
5. **B3** — the candidate D3 kills.

### Nearest literature
Ritt 1922; Pakovich (Lattès decomposition classification); Ghioca–Tucker–Zieve. These essentially
prove D3; the contribution is the ECDLP-model statement + toy confirmation.

### Path / cost
Barrier; "experiment" = B3's decomposition meter over a curve family, expected to return zero
nontrivial decompositions for non-CM `j`.

### Why prove it
Closes the Dickson-smoothness hope precisely, and sharpens *why* CM is the only place map-decomposition
helps (re-deriving the covered CM lane as the unique exception).

### Likely obstruction to proof
None major (Pakovich handles the geometry); the work is the arithmetic (`F_p` vs `C`) transfer and CM
carve-out.

### Disproof track
A non-CM `f_m` with an extra low-degree decomposition (would refute D3 and open B3).

### Proof track
Invoke Pakovich's classification of decompositions of Lattès maps; specialize to `F_p`, non-CM.

### Reproduction artifact
`research/PO_batch2_D3_ritt_indecomposability_theory.md`; ledger ID **BAR-RITT-D3**.

---

# 4. Ranking

Scores 0–5 per axis: **Dist** (distance from prior ledger+report mechanisms), **Verif** (plausibility
of an exact verifier), **Exp** (chance of changing an *exponent* not a constant), **Path** (complete-
path coverage), **Fals** (falsifiability at toy scale), **Lit** (literature-novelty confidence),
**Risk⁻** (freedom from hidden preprocessing/memory cost; higher = safer). Reject if Dist<3, no route
to descent, no rho comparison, or no precise distinction from the nearest ledger entry.

| Cand | Dist | Verif | Exp | Path | Fals | Lit | Risk⁻ | Notes |
|---|---|---|---|---|---|---|---|---|
| **A1** subresultant backend | 3 | 5 | 4 | 5 | 5 | 3 | 4 | attacks RT-1476 directly; α is a clean meter |
| A2 cycle-matroid enrich | 3 | 4 | 3 | 5 | 5 | 3 | 3 | attacks RT-1472; δ likely ≤1/4 |
| A3 amortization meter | 3 | 4 | 2 | 4 | 4 | 4 | 3 | downstream of A1/A2; scoping value |
| **B1** modular/Hecke | 4 | 4 | 4 | 4 | 4 | 5 | 2 | conductor-size killer, but maps a real structure |
| B2 Drinfeld transport | 5 | 3 | 5 | 2 | 3 | 5 | 3 | INCOMPLETE by design; value is D1 |
| **B3** Ritt/Dickson | 4 | 5 | 4 | 4 | 5 | 4 | 4 | clean meter; D3 likely kills, but sharp |
| C1 isogeny-expander walk | 4 | 4 | 2 | 4 | 5 | 4 | 4 | precise "gap≠sub-birthday" negative |
| C2 Zilber–Pink | 5 | 3 | 3 | 3 | 3 | 5 | 4 | finiteness likely kills; exotic |
| C3 Coleman–Gross height | 4 | 4 | 3 | 4 | 4 | 4 | 3 | MW-rank bound likely kills |
| D1 transport barrier | 4 | 5 | — | — | 4 | 4 | 5 | pairs B1/B2 |
| D2 amortization bound | 4 | 5 | — | — | 4 | 4 | 5 | pairs A3; CGK-adjacent |
| D3 Ritt-indecomp | 3 | 5 | — | — | 5 | 3 | 5 | pairs B3; near-corollary of Pakovich |

**Rejections/demotions:** none reach auto-reject, but **B2** is flagged INCOMPLETE (missing the
transport stage by design — kept only because its *disproof* is D1, a first-class deliverable). **A3**
is explicitly downstream (no independent exponent lever) — kept as a scoping meter, not a break.

**Selected winners (one per positive group):**
1. **Best conservative: A1** — subresultant-PRS backward-state backend. It is the only candidate that
   is (a) an exact verifier, (b) a clean scalar meter (`β`/`α`), and (c) aimed at the *single open
   theorem whose hypothesis is a measurable exponent* (RT-1476). Highest expected information per
   compute.
2. **Best representation-changing: B3** — Ritt/Dickson decomposition. Cleaner verifier and
   falsifiability than B1 (no conductor dependence) and B2 (no missing stage); pass or fail it
   produces the sharp indecomposability map D3 and re-derives why CM is the unique decomposition lane.
3. **Best high-risk: C1** — isogeny-expander walk. The most *executable* speculative candidate with a
   crisp exponent measurement; its expected negative ("spectral gap is constant-factor, not
   exponent") closes a genuinely intuitive-but-untested hope that recurs whenever someone sees the
   Ramanujan property.

---

# 5. Literature grounding (from parallel Literature-Agent search, primary sources)

**Baseline confirmed.** Shoup (EUROCRYPT 1997) and Nechaev (1994) prove `Ω(√p)` only in the
**generic-group model** (elements as random encodings, group-op oracle); rho with distinguished
points matches the `~0.886√n` constant (van Oorschot–Wiener 1999). These say nothing about
representation-level (index-calculus/summation/endomorphism) algorithms — the correct open framing
for all nine positive candidates.

**Per-mechanism nearest prior art and gap:**

- **B1 modular/Hecke — OPEN, no negative result exists.** Heegner points and Hecke operators are used
  for rational-point construction (Gross–Zagier), point counting, and modular polynomials (Elkies/SEA)
  — **never** as an IC factor base for ECDLP. A folklore Wikipedia remark that "Heegner points" were
  considered and judged unlikely to beat `O(√p)` has **no locatable primary source**
  (NOVELTY-UNVERIFIED for that specific claim). No decomposition-cost analysis exists ⇒ B1 is a
  genuinely open positive-track direction, not a refuted one. **Correct next step: Theory-Agent
  formalization (factor base, membership cost, relation probability) *before* experiment.**
- **B2 Drinfeld transport — discouraging precedent (strengthens the expected negative).** Scanlon,
  *"Public key cryptosystems based on Drinfeld modules are insecure,"* J. Cryptology 2001, proves the
  **Drinfeld-module DLP analogue is EASY (polynomial time)**. This is decisive for B2: the receiving
  problem is *weaker*, not a subexponential-strength engine — so even if a transport `ψ` existed it
  would not import hardness-beating structure; and no functor `E(F_p) → `Drinfeld-DLP is known
  (NOVELTY-UNVERIFIED). **Updates B2:** its value is purely the impossibility statement D1; the
  Scanlon result also means a *successful* B2 transport would be a self-defeating "transport into an
  easy problem," which is fine (we want easy) but underscores there is no map.
- **B3 Ritt/Dickson — likely negative, sharpened to the prime-order case.** Ritt (1922);
  Zieve–Müller (arXiv:0807.3578); Pakovich (generalized Lattès, arXiv:0710.3860). Mult-by-`m` on the
  x-line is a Lattès map that decomposes **only along divisors of `m`** — exactly the Pohlig–Hellman
  structure. **For prime group order this is vacuous** (the *scalar* `m` still factors, but the
  decomposition gives no new smoothness beyond what Pohlig–Hellman already extracts from `ord(P)`).
  This *sharpens* D3: the barrier is not merely Pakovich indecomposability but that the decompositions
  which *do* exist are Pohlig–Hellman-trivial for prime order. This is a clean scoped
  `RESTRICTED THEOREM` target for the Theory Agent.
- **C1 isogeny-expander walk — helps constants, not the exponent (OPEN for exponent).** Pizer 1990
  (Ramanujan graphs); Charles–Goren–Lauter, J. Cryptology 2009 (eprint 2006/021) use the spectral gap
  for **hashing**, and isogeny-graph collision search is itself only `√p` — matching, not beating,
  rho. No source proposes expander mixing to beat birthday for any DLP. **The repo already contains
  `phase20_isogeny_walk.sage.py` / `phase20_isogeny_walk_small.sage.py`** — the honest C1 experiment
  is to instrument these to measure whether non-backtracking + spectral gap reduces the *constant* in
  front of `√p`, a legitimate constant-factor study with no expected exponent win.
- **C2 unlikely intersections — OPEN, needs an effective finite-field analogue first.** Zilber–Pink /
  Manin–Mumford / Mordell–Lang and recent Drinfeld/Shimura extensions are **pure arithmetic geometry**
  with **no cryptographic application anywhere** (NOVELTY-UNVERIFIED as a crypto tool). The theorems
  are *qualitative finiteness* (often ineffective) — the opposite of an enumerable factor base. Theory
  Agent must first state a precise finite-height/finite-field analogue; none exists to compare against.

**Cross-cutting:** none of the nine has been benchmarked against Semaev/summation
(McGuire–Mueller 2017, `2017-1262.pdf` in-repo), Gaudry/Diem degree-of-regularity, Petit rational-map
factor bases, or GLV/Frobenius speedups; the benchmark harness must add these before any promotion.
**Novelty verdicts:** B1 (POSSIBLY NOVEL, no refutation), B2 (POSSIBLY NOVEL map / discouraging
precedent), B3 (LITERATURE-ADJACENT, prime-order negative), C1 (LITERATURE-ADJACENT, constant-only),
C2 (POSSIBLY NOVEL, no crypto prior art). A1/A2/A3 remain LITERATURE-ADJACENT (classical tools aimed
at the two open theorems); D1/D2/D3 LEDGER-NEW as formal statements (D2 adjacent to
Corrigan-Gibbs–Kogan preprocessing bounds; D3 near-corollary of Pakovich + Pohlig–Hellman).

---

# 6. Experiment contracts for the three winners

## Contract A1 — Subresultant-PRS backward-state degree meter

```markdown
# Experiment Contract: A1 subresultant backward-state (RT-1476 alpha meter)
## Hypothesis
The backward 3-sum eliminant of the serial-S3 split of S5 has degree Theta(q^beta) in the shared
Kummer coordinate u with beta < 0.3, giving membership-query exponent alpha < 3/2 (RT-1476 sub-rho).
## Null hypothesis
beta >= 0.3 (generic Bezout-like growth) => alpha >= 3/2 => no sub-rho window at m=5.
## Parameters
- curves: random ordinary prime-order E/F_p, j not in {0,1728}, non-anomalous
- p in {1009, 65521, 16769023}; 3 seeds each
- factor base: x-line, L=q^{1/5}
## Metrics
- degree of first nonzero subresultant in u; coefficient bit-size (Collins/Brown bound check);
  PRS step count; wall-clock; **field-op count on the SUCCESSFUL-membership subset only** (relations
  found) — per the red-team, abort speedups on the non-relation fraction must be excluded; fitted
  beta = d log(ops_success)/d log(q)
## Positive control
contrived curve with a known low-degree backward state (verify meter reports small beta)
## Negative control
random dense trivariate system of equal total degree (expect beta ~ 3/2 on successes)
## Success criterion
beta < 3/2 (ideally < 0.3) on the SUCCESS subset across all three sizes with flat/decreasing trend
[strong prior per red-team: beta -> 3/2 from above]
## Falsification criterion
beta >= 0.3 at any size, or increasing trend
## Reproduction command
sage experiments/ecdlp_prime_field/a1_subresultant_prs_degree_meter.sage --p 1009,65521,16769023 --seeds 3 --out a1_backward_state_degree.json
## Expected failure modes
generic Bezout degree Theta(q); coefficient blow-up dominating even if degree small
```
**First executable command:**
`sage experiments/ecdlp_prime_field/a1_subresultant_prs_degree_meter.sage --p 1009 --seeds 3 --dry-run`

## Contract B3 — Lattès Ritt-decomposition census

```markdown
# Experiment Contract: B3 Ritt/Dickson decomposition census
## Hypothesis
For some ordinary non-CM E/F_p there is a nontrivial functional decomposition f_m = g o h (g,h low
degree) not arising from m=m1*m2, giving a Dickson-smooth factor base with density > q^{-1/2}.
## Null hypothesis
Every decomposition of f_m reduces to divisors of m (Ritt/Pakovich), and for PRIME group order these
are Pohlig-Hellman-trivial => no new smoothness => no gain (D3, prime-order-scoped).
## Parameters
- p in {1009, 65521, 1000003}; several non-CM curves (j generic) + CM controls; m up to 64
## Metrics
- count of nontrivial functional decompositions of f_m; degrees of factors; smoothness density in
  the decomposition monoid
## Positive control
CM curve (expect endomorphism-induced extra decompositions)
## Negative control
generic j non-CM (expect only m=m1*m2)
## Success criterion
>=1 nontrivial non-multiplicative decomposition with smoothness density > q^{-1/2}
## Falsification criterion
zero nontrivial decompositions across all non-CM curves (=> D3)
## Reproduction command
sage experiments/ecdlp_prime_field/b3_lattes_decomposition.sage --p 1009,65521,1000003 --mmax 64 --out b3_ritt.json
## Expected failure modes
Pakovich indecomposability => zero non-CM decompositions
```
**First executable command:**
`sage experiments/ecdlp_prime_field/b3_lattes_decomposition.sage --p 1009 --mmax 16 --dry-run`

## Contract C1 — Isogeny-expander walk collision exponent

```markdown
# Experiment Contract: C1 isogeny-expander walk collision exponent
## Hypothesis
Non-backtracking walks on the ell-isogeny graph produce distinguished-point ECDLP-relation
collisions at exponent < 1/2 - eps (sub-birthday), exploiting the Ramanujan spectral gap.
## Null hypothesis
Collision exponent = 1/2 (birthday, gap-independent) => constant-factor only.
## Parameters
- p in {1009, 65521, 1000003}; ell in {2,3}; distinguished-point rate tuned; 3 seeds each
## Metrics
- collision count vs number of walk steps; fitted collision exponent; mixing time; comparison to rho
  on <P>
## Positive control
graph with a planted short cycle (expect sub-birthday)
## Negative control
rho random walk on <P> (exponent exactly 1/2)
## Success criterion
collision exponent < 1/2 - eps across all three sizes
## Falsification criterion
collision exponent >= 1/2 at any size
## Reproduction command
sage experiments/ecdlp_prime_field/c1_isogeny_walk_collision.sage --p 1009,65521,1000003 --ell 2,3 --seeds 3 --out c1_walk.json
## Expected failure modes
expander mixing bounds distribution distance, not collision count => exponent stays 1/2
```
**First executable command:**
`sage experiments/ecdlp_prime_field/c1_isogeny_walk_collision.sage --p 1009 --ell 2 --seeds 3 --dry-run`

---

# 7. Red-team: are the three winners disguised repetitions or cost-negative?

**Red-Team-Agent verdicts (parallel adversarial pass):**

- **A1 — cost-negative unless the success-subset exponent is measured.** The agent's strongest
  objection: subresultant PRS changes *how* you avoid storing the eliminant, not *what* it costs. The
  backward 3-sum eliminant has degree `~q` in the surviving variable, and PRS on a degree-`q` object
  is `Ω(q^{3/2})` field ops even with early abort — because **early abort only helps the non-relation
  fraction** (`≈` constant), *not* the relation-producing fraction, which is exactly where RT-1476's
  `α<3/2` must hold. Prediction: the exponent `β→3/2` from above. **This forces a contract change:**
  A1 must fit `β` on the **successful-membership subset only** (relations found), not the aggregate —
  otherwise the abort speedup masquerades as a win. *(Folded into Contract A1's Metrics/Success below —
  see the updated "success subset" instrumentation.)* The objection does not kill A1 as a **meter**
  (measuring `β` is the deliverable), but it makes the null hypothesis `β≥3/2` the strong prior.
- **B1 — missing stage (preimage not efficiently computable).** `deg φ ~ N^{1+o(1)}` and the relevant
  conductor `N ≈ p` for a random ordinary reduction; `φ^{-1}(P)` is a degree-`~N` fiber costing
  `Ω(p) ≫ √n`, and Hecke relations live in `J_0(N)/Q` — reduced mod `p` they give `0=0` or the
  order relation, **not** independent `F_n`-relations in `⟨P⟩`. Confirming measurement: fiber degree
  `≈ N` and reduced-relation rank `= 0` at `p≈2^20`. Confirms B1's own stated conductor-size fatal
  obstruction.
- **B2 — structural: no functor.** `E(F_p)` and rank-2 Drinfeld modules live over incompatible base
  categories; the only DL-respecting maps are isomorphisms onto `⟨P⟩` (computable only by solving the
  DLP — circular), exactly the MOV situation minus a pairing. Confirms B2's INCOMPLETE-by-design status
  and D1.

**Director's standing red-team (independent of the agent):**

- **A1 vs "dense composed resultants" (negative control).** The only thing separating A1 from the
  banned control is the *claim* that subresultant PRS reads off a small intermediate degree. If the
  backward eliminant degree is `Θ(q)` (the generic Bezout expectation), A1 **is** the dense-resultant
  control with lazy evaluation — same exponent, no win. A1 is therefore honest *only as a meter*: its
  deliverable is the number `β`, and the most likely value (`β≈1`) makes it a scoped negative that
  *closes* the subresultant backend for RT-1476. That is still net-positive (it removes one of the few
  natural P1477 instantiations), but A1 must not be sold as a probable break.
- **B3 vs Pakovich (near-certain negative).** B3's success requires contradicting a published
  classification (Lattès maps decompose only via their multiplicative/endomorphism structure). The
  honest posture: B3 is *expected* to fail, and its value **is** D3 — a precise ECDLP-model statement
  of an existing theorem, plus the CM carve-out that re-explains why the covered CM lane is the unique
  exception. Do not run B3 expecting a positive; run it to *certify* D3 at toy scale.
- **C1 vs birthday-bound (near-certain negative).** Expander mixing controls *distribution distance*,
  which is orthogonal to *collision count*; the birthday exponent `1/2` is mixing-independent. C1 will
  almost certainly measure exactly `1/2`. Its value is closing a recurring intuition ("the graph is
  Ramanujan, surely the walk mixes into a speedup") with a crisp measurement. Not a break.
- **Shared risk — all three winners are "meters," not breaks.** This is deliberate and correct given
  the state of the frontier: the only rho-relevant surface is the two conditional theorems, and the
  fastest way to advance is to *measure the exponents those theorems leave free* (A1 → RT-1476 α) or
  to *certify the barriers* that channel effort back to them (B3→D3, C1→spectral-gap-is-constant). A
  batch that promised a probable break here would be overclaiming. The mandate ("could eventually
  cross 1/2") is met by A1, whose meter directly targets the free exponent of an *already-proven*
  conditional sub-rho theorem.

---

## Director's summary (default template)

**Current claim** — `OPEN`: the prime-field ECDLP frontier is still exactly the two conditional
theorems RT-1472 (needs enrichment δ>1/4) and RT-1476 (needs backward-state α<3/2); this batch adds
three executable *meters* (A1 for RT-1476's α, A2 for RT-1472's δ, C1 for the isogeny-gap intuition)
and three barrier theorems (D1 transport, D2 amortization, D3 Ritt) that channel effort back to those
exponents.

**What we tested/proved** — nothing empirically yet; this is idea generation. All 12 candidates are
fingerprinted mechanism-new vs the ledger and all three prior reports; six begin outside the ledger
vocabulary (B1,B2,B3,C1,C2,C3).

**What failed** — B2 is INCOMPLETE by design (no transport map); A3 is downstream (no independent
exponent lever); B1 is conductor-bounded to a measure-zero curve family.

**What remains open** — RT-1476 α (A1), RT-1472 δ (A2), the amortization crossover conditional on a
sub-rho online exponent (A3/D2).

**Why this matters** — A1 is the first proposal to instantiate the ledger's own P1477 gate with a
concrete, falsifiable degree measurement; the barriers precisely delimit three tempting but likely-
dead lanes (transport, amortization, map-decomposition).

**Next three pushes** —
1. Conservative: run Contract A1 (subresultant backward-state degree meter → RT-1476 α).
2. Representation-changing: run Contract B3 (Lattès decomposition census → certify D3).
3. High-risk: run Contract C1 (isogeny-expander collision exponent → certify spectral-gap-is-constant).

**Artifacts** — this report; 12 candidate specs; 3 experiment contracts + first commands; 3 barrier
theory notes; proposed ledger IDs RT-1476-SUBRES-A1, RT-1472-CYCLEMAT-A2, AMORT-A3, MODHECKE-B1,
DRINFELD-B2, RITT-B3, ISOWALK-C1, ZILBERPINK-C2, PADICHT-C3, BAR-TRANSPORT-D1, BAR-AMORT-D2,
BAR-RITT-D3.

*End of report body — literature (§5) and red-team (§7) agent findings folded in below when the
parallel agents return.*
