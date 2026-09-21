# Research-Director Idea Generation — 2026-07-18 (batch 3)

**Role:** Research Director, empirical ECDLP cryptanalysis lab.
**Mission:** propose *mechanism-new*, falsifiable directions whose **complete** cost could
eventually beat the single-target Pollard-rho `0.886·sqrt(n)` baseline for ECDLP over
**ordinary prime fields**. Toy correctness, a new coordinate system, a relation certificate,
faster preprocessing, or a solver swap is explicitly **not** a breakthrough.

Autonomous scheduled run (no user present); implementation choices noted inline.

## Why a third report today

Two complete reports already exist for 2026-07-18: `research/idea_generation_20260718.md`
(batch1: A1 sparse-interpolation, A2 Sidon/B_h, A3 list-decoding, B1 Serre–Tate [rej], B2
Cartier–Manin [rej], B3 group-dual DFT, B4 Semaev border-rank, C1 approximate-homomorphism,
C2 Kloosterman [rej], C3 CM ideal-factorization, D1–D3 barriers) and
`research/idea_generation_20260718_batch2.md` (A1 subresultant-PRS, A2 cycle-matroid, A3
amortization meter, B1 modular/Hecke, B2 Drinfeld, B3 Ritt/Dickson, C1 isogeny-expander walk,
C2 Pink–Zilber, C3 p-adic-height, D1–D3 barriers). Together with the two 2026-07-17 reports
(batch1 + batch2), **four prior reports and ~48 prior candidates** now exist. Every search seed
named in this task's brief (Hasse-jet/dual-number, tropical/Newton-polytope, output-sensitive
incidence, arithmetic-dynamical transfer operators, noncommutative correspondence/path algebras,
tensor-network/separator-rank) was consumed by batch1 of 07-17. This report is therefore held to
a **stricter** bar: each candidate must be mechanism-new against the ledger **and all four**
prior reports, and each is fingerprinted against that combined catalogue (§1). Five external
literature scouts (documented, primary-source) back the novelty labels (§5).

Because the mined lanes are exhausted, this report deliberately enters **six families that
appear nowhere in the four prior reports or the ledger**: (i) *displacement-structured / superfast
elimination* (Toeplitz-like Bézoutian, half-GCD, composed-resultant power-sum), (ii) *spectral
graph theory* (effective-resistance sparsification, Matrix-Tree enrichment), (iii)
*representation-theoretic operators* (Heisenberg/theta-group Schrödinger–Weil), (iv)
*non-archimedean skeleton / Weil–Châtelet descent* collapses, (v) *holographic / matchgate
counting* (Valiant, Cai–Lu Holant dichotomy), and (vi) *sum-product / additive-energy* relation-
supply barriers (Rudnev, BGKS, Shkredov). Nine of the twelve candidates begin outside the
ledger's dominant vocabulary (Semaev/Gröbner, cover/Prym, isogeny/CM, large-prime, database-join).

---

## 0. Review scope and inventory census

**Required inputs read (all four), plus derived corpus and all four prior reports:**

1. `research_ledger.md` — 2478 lines. Sections: open-frontier questions (~113 checkboxes),
   active hypotheses, negative results, positive signals, baselines, literature map, graph-index
   frontier, negative controls, the 07-17 division-character routing rows (ECFG-NR-1484,
   ECFG-RT-1485), and the newest **2026-07-18 oriented-norm Kani block** (ISO-NR/OBS/RT-ONK-001..003,
   IKD-004..014). The only rho-relevant conditional theorems on the board remain **RT-1472**
   (2-large-prime enrichment `δ>1/4`), **RT-1476** (m-ary membership `α<3/2`), and **RT-1485**
   (Kummer companion-state, a *storage* result, not a query backend).
2. `ecdlp_index_calculus_state/research_ledger.md` — 720 lines; ECFG functional-graph +
   direct-source packet track (ECFG-001.. hypotheses, public-selector chain). This is the
   dominant "coordinate index calculus + Evans functional graph" lane; every selector/scout
   micro-optimization is a **negative control** (post-hoc wins, prospective failures).
3. `research/non_generic_transfer_search_20260610.md` — 390 lines; transfer/decomposition channel
   search + PO-transfer-001..006 appendix. Load-bearing: **twist positive control** (P-224 twist
   `53.28` bits below base rho, but adjacent invalid-curve channel, not an original-subgroup
   break) and the **trace-fiber lemma** (PO-005: for a group hom `τ:H→G`, full kernel fibers
   multiply successes and trials equally → no relation-probability or rank gain).
4. `ecdlp_index_calculus_state/research_sources/bibliography.json` — 10 primary IC entries
   (Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske 2013; FHJRV 2014; Kousidis–Wiemers 2015;
   Karabina 2015; Amadori–Pintore–Sala 2017; McGuire–Mueller 2017; Trimoska–Ionica–Dequen 2020).
5. Derived corpus: 1100+ files in `research/` (178 `PO_transfer` contracts, 169 ISO-AR atlas
   entries, PAPER_* barrier notes, p14xx theorems), plus the four idea reports (inputs 13–16).

**Census (machine-readable, exact `grep -oE | sort -u | wc -l` counts, this run; supersedes the
older 2248-line-ledger numbers quoted in the 07-17 reports):**

- **Distinct negatives:** ECFG-NR **501** (span `238..1484`), TRANSFER-NR **92** (`001..093`),
  ISO-AR-NR **82** (`001..082`), ISO-NR-ONK/IKD/OBS/RT **~14** (grew this run), SHA1-N **9**
  (`003..011`), core `NR-` ~13. (TRANSFER-NR is ~92, notably higher than the 07-17 reports' ~53.)
- **Active hypotheses:** ECFG-H **382** (`303..687`), ISO-AR base **37** + ISO-SP/RM/CW ~9,
  TRANSFER-H **36** (`001..036`), SHA1-H 4.
- **Positive signals:** ECFG-P **937** (root ledger, `238..1470`) + **339** (IC-state ledger,
  `001..1513`), TRANSFER-P **95** / PO **79** (same records, two notations), ISO-AR-POS **50**.
- **Restricted-model rows (rho-relevant): 3** — ECFG-RT-1472, RT-1476, RT-1485. **`ECFG-MX-1478`
  is the sole dense-resultant record.**
- **IC-state frontier: P1509–P1513** — the "source-coded / marked-resultant compiler" chain on
  IDEA-068/115/117. **P1509 verifies IDEA-068 Hasse-jet source-sections as an EXACT local positive
  (all 900 nonreturn endpoints Hasse order 1 or 2), but no global compiler** (⇒ the brief's
  Hasse-jet seed is consumed). P1510-R1 exact degree-2 marked resultant is per-row `O(r²)` but
  `Θ(r³)` repeated; P1511-R2 / P1512-R1 close the FD/factorized-semijoin and scalar-linear Chow
  atomizers (`Ω(r⁵)` universal-atom matrix), **preserving only the nonlinear-circuit exception**;
  P1513 leaves an output-sensitive common-norm recurrence open.
- **ID families:** ECFG (coordinate IC + Evans graph — dominant, with the P1509–P1513 marked-
  resultant/DB-join sub-lane), TRANSFER/PO (cover/Prym/Jacobian correspondence), ISO-AR/SP/ONK/IKD
  (oriented-CM isogeny + self-pairing + oriented-ideal Kani recovery), SHA-1 bounty (off-ECDLP),
  core `NR-`.

**Extracted fingerprint fields per family** (mechanism / representation / exploited structure /
factor base / relation shape / relation-generation / compression / linear-algebra object /
target-descent / cost bottleneck / outcome / scoped negative boundary / next branch) are in §1.
**Load-bearing bottom line, re-confirmed:** *no ledger entry and no prior-report candidate
demonstrates a complete-cost single-target speedup over Pollard rho on prime-field ECDLP.* Every
empirical "below rho" is amortized-many-target and/or setup-uncharged. The sparse-LA stage
(`B²=n^{2/5} < n^{1/2}`) is **not** binding; the **relation/membership-generation stage** is. The
only rho-crossing paths on record are the two unrealized conditional theorems **RT-1472**
(`δ>1/4`) and **RT-1476** (`α<3/2`). These, plus the standing barriers, are the constraints every
candidate must respect.

---

## 1. Fingerprint inventory by mechanism family (compressed)

`F(entry) = (object, ops, hidden-structure, discarded, retained, relation-primitive,
compression-primitive, rank-mechanism, descent-mechanism, dominant-cost-exponent)`.

| Fam | Object | Structure exploited | Relation / compression primitive | Rank mechanism | Descent | Dominant cost | Outcome / scoped boundary |
|---|---|---|---|---|---|---|---|
| **M1 ECFG coordinate IC** | `E/F_p`, `B≈n^{1/5}` | recursive `S1,S2,S3` five-term `A+C=R`; bases interval_x, x_mod4, rational-map, `x^L=1` subgroup, autos | pair-compiler, shared-x buckets, CRT/product trees, preimage DAG | weighted factor-log matrix, sparse | one-factor online descent | membership/generator cost | **TOY, no single-target win.** end-to-end `22..66× rho`. |
| **M1b ECFG join-query** (P1510–P1513) | 5-term provenance query as DB join | acyclic join tree, FD width, factorized semijoin, linear-Chow atomizer | WCOJ, subresultant/gcd semijoin | determinantal / Chow cycle length | shared | input-iterator `r^3=q^{3/5}` | **NEGATIVE (verified):** every atomizer provably cubic; input floor unbroken. |
| **M2 large-prime graph** | 1-LP / 2-LP endpoint graph | residual-column occupancy; endpoint-incidence cycles | pair table, signless nullity | graph cycle rank | LP-log propagation | 1-LP `0.6`; 2-LP setup `Θ(L²)` | **RT-1472:** crosses `1/2` iff enrichment `δ>1/4`; explicit decks give `δ≤1/4`. |
| **M3 implicit membership backend** | m-ary Semaev pair/5-term membership | `x^L=1` sparse S3, char buckets, CM orbit, serial-S3 state, resultants | implicit predicate eval | sparse full-rank | shared backend | query exponent `α` | **RT-1476:** backend with `α<3/2` (m=5), setup `≤L²`, random support → conditionally beats rho. All tried backends miss it. |
| **M4 cover/Prym/Jacobian transfer** | genus-2/3 covers, Pryms, `Z[π]` lattices | hidden E-isotypic block, C3/deck projectors, norm labels | source principal-divisor / ternary constant-sum, LP closure | C3-module kernels, Rosati Gram | calibrated logs → point lookup | Prym cert + cover setup | **RESTRICTED THMs:** deck/Prym maps scalar-or-zero on visible E; best recovery `~3376× rho`. |
| **M5 oriented-CM isogeny + Kani** | oriented `O_K`, volcano, θ, Kani, oriented ideals | target-free kernel construction, oriented-ideal norm floor, `n²=d+Norm(a)` | — | — | — | torsion-field degree | **OBS/RESTR-THM, TOY.** isogeny-finding + oriented-ideal-Kani planting; does not attack rho. |
| **M6 ECFG public selectors** | Evans graph `k→x(kB)` | depth/component/indegree as leaf selectors | frozen gates route relation leaves | selected-event yield vs uniform | shift-lookup | full graph = N edges | **NEGATIVE chain:** every selector wins post-hoc, fails prospective. |

**Standing barriers / restricted theorems (frontier constraints every candidate must respect):**

- **B-Dreg** — degree-of-regularity conservation over `F_p`; naive Semaev/Gröbner, coordinate
  reparametrization, scalar Weil-restriction/abelian-surface, crossbred `m=3`, multi-target rho —
  none lowers the exploitable solving degree.
- **B-trace-fiber (PO-005)** — full kernel fibers multiply successes and trials equally → no gain.
- **B-permutation (TRANSFER-NR-001, ISO-CW-NR-001)** — measure-preserving correspondence preserves
  multiplicities → no rank gain.
- **B-preproc (Corrigan-Gibbs/Kogan; CHW)** — generic frontier `S·T² = Ω̃(εq)`.
- **B-explicit-edge (P1434)** — explicit terminal source-edge circuits admit no compressed exact
  promoting rule. Loophole: *generative/sketch-based* witness recovery.
- **B-n=1 collapse (Gaudry/Diem)** — prime-field `n=1` has no proper base field to Weil-restrict.
- **B-cubic-join (P1510–P1513)** — the source-labelled 5-term provenance query has input floor
  `r^3=q^{3/5}`; join planning, factorized semijoin, and scalar-linear Chow atomizers are all `≥`
  cubic. Loophole: a *target-specialized nonlinear* circuit (unrealized).

**Prior-report mechanism catalogue (all four reports — must not be re-proposed).** Semaev-Gröbner
(baseline); BKK/mixed-volume; elliptic-net/EDS smoothness; incidence-reporting range DS;
dual-number/jet lift; tensor-train separator rank; Semaev border/CP rank; tropical/p-adic
valuation descent; noncommutative CM-correspondence (quiver); Lattès transfer-operator spectrum;
Xedni global height-lattice lift; 3-large-prime hypergraph homology; NFS two-sided coincidence;
Kedlaya–Umans membership evaluation; Kani genus-2 RM Jacobian glue; Serre–Tate canonical lift;
level-≥3 theta-bilinear membership; representation-technique MITM; p-curvature/holonomy descent;
character-sum/Kloosterman bias sampling; sparse interpolation (Prony/BOT); Sidon/B_h additive
designs; list-decoding (GS) membership; group-dual DFT indicator; Bogolyubov–Ruzsa
approximate-homomorphism stability; CM ideal-factorization class-group IC; subresultant-PRS
backward state (RT-1476 meter); graphic-matroid cycle-basis enrichment (RT-1472 meter);
amortization crossover meter; modular/Hecke factor base; Drinfeld/FF transport; Ritt/Dickson
map-decomposition; isogeny-expander walk; Pink–Zilber unlikely-intersection; p-adic-height lift.
Barriers already stated: nilpotent no-rank-gain; correspondence-permutation no-gain;
separator-rank LB; generic-model MITM; crystalline order-only; Gaudry fixed-genus IC;
class-function no-leakage; addition-law scrambling; transform-sparsity/border-rank LB;
Ritt-indecomposability; Drinfeld transport-impossibility; expander-mixing ≠ sub-birthday.

**Everything below is fingerprinted against that catalogue.** The six lanes entered here appear
nowhere in it.

---

## 2. Known-closed / control-only territory (this run)

A candidate is a **duplicate** unless it breaks a measured obstruction with a *new mathematical
operation*. Beyond the standing list (ordinary same-field isogeny invariants; scalar Weil/theta
pullbacks; explicit 2-LP advice graphs; joint factor/LP block-Krylov; pair-residual character
buckets; non-invariant CM decks; materialized serial-S3 state; dense composed resultants; DB
join planning; source selectors without an honest generator; relation-validity without recovery;
preprocessing wins that lose on advice/memory/target-count; twist/extension channels; oriented-
ideal Kani planting), this run adds as **negative controls / covered**:

1. **All ~48 prior-report candidate mechanisms** (the catalogue in §1).
2. **Single-variable Õ(d) fast elimination as folklore** — half-GCD, superfast Toeplitz, and
   composed-resultant power-sum methods already give Õ(d) per *bivariate* elimination
   (Kailath–Sayed; Bini–Pan; Moenck; Bostan–Flajolet–Salvy–Schost 2006). A candidate reusing
   these is a *duplicate of folklore* unless it exploits the **iterated/multivariate Semaev**
   structure and beats the F4/F5 Gröbner cost — the single-variable bound alone is not novel
   (Literature Agent, load-bearing caveat).
3. **Descent over `F_p`** — Weil–Châtelet `H^1(F_q,E)=0` (Lang): no nontrivial torsor/covering
   exists over a finite field, so any "m-descent / covering" representation collapses unless it
   leaves `F_p` (→ global-lift/xedni wall, covered).

High-numbered ECFG-NR provenance rows, SHA1-N, and the ISO-AR V-chain are instrumentation
negatives, **not** mathematical dead-ends.

---

## 3. Twelve candidates

Notation: `q≈n` prime subgroup order; `B≈n^{1/5}` factor base; `L≈B`; rho `≈0.886·n^{1/2}`;
IC total `≈ B·(cost/relation) + B²(sparse LA) + descent`; the **relation/membership stage** is
binding. The two named gates are **RT-1476** (`α<3/2`, m=5) and **RT-1472** (`δ>1/4`).

### Group A — conservative extensions of known IC work

---

## Candidate: A1 — Displacement-structured (Toeplitz-like) Bézoutian membership backend

### One-sentence mechanism
Exploit that the Sylvester/Bézout matrix of the serial-S3 backward-3-sum eliminant has **O(1)
displacement rank** (it is Toeplitz-/Hankel-like) to compute the shared-`u` membership certificate
by a **superfast generalized-Schur (GKO) structured solve in `Õ(d)`** field ops per query rather
than the dense `Θ(d²)` resultant, driving the RT-1476 query exponent `α` toward the sub-rho `<3/2`.

### Status
HYPOTHESIS (α is a measurable exponent; the theorem it feeds, RT-1476, is proven).

### Novelty classification
POSSIBLY NOVEL (displacement-structured elimination is mature in computer algebra but, per the
Literature Agent's explicit absence check, has **never** been applied to Semaev summation
polynomials or ECDLP index calculus; distinct from batch2-A1 subresultant-PRS, batch1-B2
tensor-train, batch2(0718)-A3 Kedlaya–Umans). See §5 for the load-bearing "single-variable is
folklore" caveat that constrains the claim to the iterated/structured setting.)

### Semantic fingerprint F(A1)
- object: 5th Semaev `S5`, serial-split into forward `S3(x1,x2,u)` and backward `S4(u,x3,x4,x5)`;
  the Sylvester/Bézout matrix `Syl_u` of the two in the shared variable `u`.
- ops: field ops in `F_p`; FFT polynomial arithmetic; GKO generalized-Schur / Cauchy-like solve.
- hidden structure: **`Syl_u` has displacement rank O(1)** under the `∇ = Z_1·M − M·Z_2` operator
  (Kailath–Sayed), because Sylvester/Bézout matrices are Toeplitz-like; the summation-polynomial
  coefficients are themselves C-finite in the symmetric functions (an extra structure layer).
- discarded: the dense composed resultant (never formed — the batch1 07-18 §2 negative control).
- retained: the generator pair `(G,B)` of displacement rank O(1) that encodes `Syl_u`.
- relation primitive: five-term `A+C=R`; a vanishing structured Schur complement certifies shared `u`.
- compression primitive: **displacement-structured superfast solve** (GKO + FFT), *not* elimination.
- rank mechanism: unchanged `Θ(L)` sparse factor-log matrix over `Z/n`.
- descent: same backend on `T+[r]P` decompositions (RT-1476 uses the backend for descent too).
- dominant cost exponent: `α := log_L(per-query cost) = log_L(displacement-rank × d)` — **measured**.

### Nearest ledger entries
1. **RT-1476** — the theorem A1 feeds; A1 is a concrete backend candidate for its free `α`.
   Distinction: candidate vs gate.
2. **ECFG-MX-1478 (dense composed resultant `4L²`, zero held-out prediction)** — MX-1478
   *materializes* the resultant and its second-order recurrence `U_n=-B·U_{n-1}-AC·U_{n-2}`; A1
   never forms it, solving the *structured* Sylvester system instead. Distinction:
   displacement-structured solve vs dense materialization.
3. **batch2-A1 (subresultant-PRS β-meter)** — subresultant PRS is a `Θ(d²)` fraction-free scheme
   that measures the eliminant *degree* `β`; A1 attacks the *arithmetic* cost at fixed degree via
   O(1)-displacement superfast solve. Distinction: structured-matrix arithmetic vs PRS degree.
4. **batch1-B2 (tensor-train / separator rank)** — bond-dimension compression of the S3 tensor;
   A1 uses Toeplitz displacement structure, a different rank notion, different failure mode
   (displacement rank vs bond dimension).
5. **ECFG-RT-1485 (Kummer companion state, constant fibers, quadratic support)** — a *storage*
   result hinting the backward state is compressible; A1 turns the hint into a *query* cost.
   Distinction: storage vs structured query.

### Nearest literature
Kailath–Sayed, *Displacement Structure* (SIAM Review 1995); Bini–Pan, *Polynomial and Matrix
Computations* (1994); Gohberg–Olshevsky (GKO generalized-Schur, superfast Cauchy-like
`O(d log² d)`); Villard et al., *Elimination ideal and bivariate resultant over finite fields*
(arXiv:2302.08891). Kudo–Yokoyama (*Complexity bounds on Semaev's naive IC*, J. Math. Crypt.
2020) note the PDP Gröbner computation "is regarded as an extension of the extended Euclidean
algorithm" — but invoke this to derive a **lower bound**, never a speedup. **Gap (Literature
Agent):** no source applies displacement-rank/structured elimination to Semaev; the single-variable
`Õ(d)` bound is folklore, so novelty must rest on the iterated Semaev structure and must beat F4/F5.

### Target family
Random ordinary prime-order short-Weierstrass `E/F_p`, `p` prime, `n=#E` prime, `j∉{0,1728}`,
non-anomalous, large embedding degree, no small-CM-discriminant. Excluded: supersingular,
binary/extension fields.

### Full algorithmic path
1. **Factor base:** `L=q^{1/5}` x-coordinates on the line (RT-1476 m=5 model), `O(L)` group ops.
2. **Relation generation:** forward table of `S3(x1,x2,u)` roots for all `(x1,x2)`; for each
   backward `(x3,x4,x5)`, build the O(1)-displacement generator of `Syl_u(S3,S4)`; run the GKO
   superfast structured solve; a vanishing structured Schur complement certifies shared `u`.
3. **Witness/verify:** the certified `u` gives the shared point; verify `S5=0` by exact evaluation.
4. **Relation probability:** `min(1, L^5/q)` per 5-tuple (unchanged from RT-1476).
5. **Matrix:** `Θ(L)` rows, ≤5 nonzeros/row, over `Z/n`, density `O(1/L)`.
6. **Factor-log calibration:** standard.
7. **Descent:** same structured backend on the target decomposition.
8. **Offline/online:** symbolic split + generator template offline per curve; solve online.
9. **Memory/parallel:** forward table `O(L²)` (or streamed with distinguished-`u`); solves are
   embarrassingly parallel across the backward base.

### Cost model
Per RT-1476: total exponent `2/(m+1−α)` for `α≤1`; at m=5, sub-rho requires `α<3/2`. A1's
per-query cost is `displacement-rank(Syl_u) × Õ(d)` where `d` is the `u`-degree. If displacement
rank is O(1) *and* `d=Õ(L^{α})` with `α<3/2`, relation-gen is `L·Õ(L^{α}) = n^{(1+α)/5} ≪ n^{1/2}`.
Compare rho `n^{0.5}`; explicit-join IC `n^{0.6}`; dense resultant MX-1478 `n^{2/5}`-per-query.

### Why existing negatives do not already kill it
Avoids **dense composed resultant / MX-1478** (never materialized) and **B-Dreg** (no Gröbner
solving degree). New operation: **superfast displacement-structured solve of the Semaev backward
Sylvester system.**

### Likely fatal obstruction
Superfast Toeplitz methods reduce *arithmetic at fixed degree* but do **not** reduce the eliminant
*degree* `d`. If `d=Θ(q)` (generic Bézout bound for three summation constraints — exactly what
batch2-A1's degree meter is likely to find, `β≈1`), then even `Õ(d)` arithmetic is `Õ(q) ≫ √n`.
Structured elimination is decisive **only** if the `u`-eliminant degree is subquadratic — the same
degree wall that constrains all RT-1476 backends. A1's honest content is: *given* a subquadratic
degree, the arithmetic is quasi-linear, so the degree meter (batch2-A1) is the true gate and A1
is its complementary fast backend.

### Minimal falsifying experiment
Toy `p ∈ {1009, 65521, 16769023}`, 3 seeds each, ordinary prime-order curves. (i) Build the
serial-S3 split; (ii) measure the displacement rank of `Syl_u` under `∇` at three sizes; (iii)
time the GKO structured solve vs dense resultant vs batch2-A1 subresultant PRS. **Positive
control:** a contrived Toeplitz system of known O(1) displacement rank (GKO must win). **Negative
control:** a random dense matrix of matched size (GKO gives no gain). Fit `α = log_L(query cost)`
and the displacement-rank trend.

### Quantitative promotion gate
Measured displacement rank O(1) (flat in `L`) **and** query exponent `α<3/2` across all three
sizes, **with** relations reaching sparse rank `≥L−1`. Correctness alone is not the gate.

### Proof track
Theorem: `Syl_u(S3,S4)` has displacement rank `O(1)` under the Sylvester operator, **and** the
`u`-eliminant degree is `O(q^{β})` with `β<3/10` (would follow from a Newton-polytope/mixed-volume
bound on the `u`-elimination ideal, using mixed volume as an *analysis* tool, not the batch1-A1
algorithm).

### Disproof track
Measured `d=Θ(q)` (`β≈1`) at all sizes ⇒ scoped negative "structured elimination gives no RT-1476
backend because the Semaev backward eliminant is Bézout-dense in `u`," sharpening MX-1478 from
*materialization cost* to *degree floor*.

### Reproduction artifact
- contract: `research/experiment_contract_a1_displacement_bezout_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/a1_displacement_bezout_solver.sage`
- result/audit: `.../a1_displacement_result.json`, `.../a1_displacement_verify.sage`
- ledger id: **DISP-A1**

---

## Candidate: A2 — Effective-resistance spectral-sparsifier enrichment meter (RT-1472 δ-meter)

### One-sentence mechanism
Exploit the **electrical/spectral structure of the two-large-prime graph** — sampling partial
relations by **effective resistance** (Spielman–Srivastava) to store an `O(L)`-edge spectral
sparsifier instead of `Θ(L²)` pair-advice, and reading the enrichment `δ` off the Laplacian
spectrum (`λ₂`, Matrix-Tree `τ=∏λ_i/n`) — targeting the `δ>1/4` threshold RT-1472 proves crosses rho.

### Status
HYPOTHESIS (δ is a measurable exponent; RT-1472 is proven).

### Novelty classification
POSSIBLY NOVEL (per the Literature Agent, spectral sparsification / effective resistance has
**never** been applied to index-calculus large-prime graphs — the sparsification and IC
literatures are disjoint; index-calculus cycle yield is always analyzed *combinatorially*,
Lenstra–Manasse / Gaudry–Thomé–Thériault–Diem / Nagao). Distinct from batch2-A2 (min cycle basis /
graphic matroid) and from 07-17/07-18 3-uniform-hypergraph homology.

### Semantic fingerprint F(A2)
- object: graph `G`, vertices = large primes, edges = partial relations with ≤2 large primes;
  its Laplacian `L_G` and effective-resistance metric.
- ops: partial-relation generation; Laplacian solves; effective-resistance leverage scores.
- hidden structure: **effective resistance = probability an edge lies in a random spanning tree =
  edge's irreplaceability in the relation (cycle) space**; low-resistance edges are redundant
  (parallel paths = independent cycles), high-resistance edges are near-bridges.
- discarded: the `Θ(L²)` explicit pair advice.
- retained: an `O(L/ε²)`-edge spectral sparsifier preserving the quadratic form (all cycles,
  cuts, spanning-tree count to `1±ε`).
- relation primitive: partial relations with 2 large primes (birthday on the controlled part).
- compression primitive: **effective-resistance sampling** (`O(L log L)` edges) / BSS (`O(L)`).
- rank mechanism: cycle-space dimension `|E|−|V|+c`; spectral quality via `λ₂`, `τ`.
- descent: special-q on a target large prime (standard).
- dominant cost exponent: `max(2ℓ,1−ℓ,1+1/5−2ℓ)` (RT-1472), with advice term replaced by `O(L)`.

### Nearest ledger entries
1. **RT-1472** — the theorem A2 feeds; A2 measures `δ`. Distinction: candidate vs gate.
2. **ECFG-NR-1471 (explicit 2-LP deck, `~107× rho`, every signal gate fails)** — NR-1471 stores
   the explicit matrix; A2 **never stores pairs**, only the `O(L)` sparsifier, so the advice term
   `2ℓ` in RT-1472 is replaced by the sparsifier cost. Distinction: spectral proxy vs explicit deck.
3. **batch2-A2 (graphic-matroid min cycle basis)** — same "store `O(L)` not `Θ(L²)`" goal, but a
   *combinatorial* cycle basis; A2 uses the *Laplacian spectrum / effective resistance*, a
   different functional with a different enrichment measure (`λ₂`, `τ` vs Horton cycle weight).
4. **07-18(batch2)-A1 (3-uniform hypergraph homology)** — counts independent 2-cycles via boundary
   rank; A2 counts via the graph Laplacian null-space multiplicity and spectral gap. Distinct object.
5. **ECFG-NR-304/308 (source-scheduling negatives)** — A2 must carry an honest 2-LP generator, not
   a selector. Distinction: honest generator + spectral sparsifier vs selector.

### Nearest literature
Spielman–Srivastava, *Graph Sparsification by Effective Resistances* (SICOMP 2011, arXiv:0803.0929);
Batson–Spielman–Srivastava, *Twice-Ramanujan Sparsifiers* (arXiv:0808.0163); Kirchhoff / Matrix-Tree;
Lenstra–Manasse (two large primes, 1994); Gaudry–Thomé–Thériault–Diem (double-LP, eprint 2004/153);
Nagao (arXiv:math/0606607). **Gap:** no spectral treatment of IC large-prime yield exists.

### Target family
As A1; plus the honest 2-LP generator at `L=q^{1/5}` (RT-1472 optimum).

### Full algorithmic path
1. FB `L=q^{1/5}`. 2. Generate partial relations with ≤2 large primes (birthday on controlled
coords). 3. Build `G`; compute effective-resistance leverage scores; keep an `O(L/ε²)`-edge
spectral sparsifier; read `δ = log_L(#independent cycles / advice)`, `λ₂`, `τ=∏λ_i/n`.
4. Cycles → full relations. 5. Sparse `Z/n` matrix. 6. Calibration. 7. Special-q descent.
8. Offline: graph + sparsifier; online: descent. 9. Memory `O(L)`.

### Cost model
RT-1472: without enrichment, exponent `2/3` at `ℓ=1/3`; `δ>1/4` needed to cross `1/2`. The
sparsifier makes the *advice* term `O(L)` instead of `Θ(L²)`, but the **exact enrichment is still
`|E|−|V|+c`** — spectra give the *rate/quality* (`λ₂`, `τ`), not a larger cycle count. So A2 wins
only if the honest 2-LP graph genuinely has `Ω(L^{1+δ})` cycles with `δ>1/4` **and** the sparsifier
faithfully preserves them.

### Why existing negatives do not already kill it
NR-1471 killed the *explicit stored deck*; A2's new operation is to never store the deck, only its
`O(L)` spectral sparsifier, and to measure `δ` spectrally. Obstruction avoided: `Θ(L²)` advice
blow-up. Responsible operation: effective-resistance sparsification.

### Likely fatal obstruction
The cycle-space dimension of a random sparse graph with `|E|≈|V|` is `Θ(|V|)`, giving `δ≤1/4` (no
crossing) — the same subcritical-random-graph wall that constrains batch2-A2. Sparsification and the
spectral quality measure change *storage and diagnostics*, not the *number* of independent cycles;
if the honest generator is subcritical, no spectral trick manufactures cycles.

### Minimal falsifying experiment
Toy `p ∈ {65521, 1000003, 16769023}`. Build the honest 2-LP graph; compute effective-resistance
sparsifier, `λ₂`, `τ`, and `|E|−|V|+c`; fit `δ`. **Positive control:** a planted-dense-graph regime
with known `δ>1/4`. **Negative control:** Erdős–Rényi `G(L, L^{-1})` (`δ→0`, subcritical).

### Quantitative promotion gate
Measured `δ>1/4` with flat/increasing trend across three sizes **and** the sparsifier preserving
≥`(1−ε)` of the independent relations. Else scoped NEGATIVE for spectral enrichment of RT-1472.

### Proof track
Theorem: the honest 2-LP summation graph at `L=q^{1/5}` has cycle-space dimension `Ω(L^{1+δ})`,
`δ>1/4`; equivalently `λ₂` bounded below by a size-independent constant.

### Disproof track
Show the graph is a.a.s. subcritical (forest + `O(1)` cycles, `δ=0`) via the random-graph threshold.

### Reproduction artifact
- contract: `research/experiment_contract_a2_effres_sparsifier_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/a2_effres_delta_meter.py`
- result/audit: `.../a2_effres_result.json`, `.../a2_effres_audit.py`
- ledger id: **EFFRES-A2**

---

## Candidate: A3 — Composed-resultant power-sum common-root backend (Prony-pencil on the MX-1478 recurrence)

### One-sentence mechanism
Exploit that the MX-1478 one-transition oracle expresses the S3 state as a **second-order C-finite
recurrence** (`U_n=−B·U_{n−1}−AC·U_{n−2}`, `K_L=A^L+C^L−U_L`), so the two-transition common-root
problem is a **composed resultant of C-finite sequences** computable by **power-sum / Newton-identity
generating series in `Õ(d)`** (Bostan–Flajolet–Salvy–Schost "special resultants") — never forming
the dense `4L²` object MX-1478 measured.

### Status
HYPOTHESIS (feeds RT-1476; complements A1 with a different fast-elimination primitive).

### Novelty classification
LITERATURE-ADJACENT (composed-product/composed-sum "special resultants" are classical for C-finite
sequences, but per the Literature Agent have **never** been applied to Semaev; the new operation is
recognizing the MX-1478 backward state as a C-finite composed resultant and using power-sum series
instead of the Sylvester determinant). Distinct from batch2-A1 (subresultant PRS, `Θ(d²)`) and A1
(displacement solve): A3 uses the **generating-function / power-sum** representation.

### Semantic fingerprint F(A3)
- object: the composed resultant `Res_u(S3(·,u), S4(u,·))` viewed via the power sums of its roots,
  built from the C-finite MX-1478 transition oracle.
- ops: field ops; Newton–Girard identities; generating-series (Graeffe/diamond-product) arithmetic.
- hidden structure: **C-finiteness of the S3 state** (constant-coefficient linear recurrence) makes
  the power sums of the eliminant roots themselves C-finite/holonomic and computable in `Õ(d)`.
- discarded: the dense `4L²` two-transition resultant (MX-1478).
- retained: the first `O(d)` power sums, sufficient to recover the eliminant / detect a shared root.
- relation primitive: five-term `A+C=R`; a shared root of the composed pair = a valid decomposition.
- compression primitive: **power-sum / composed-resultant generating series** (BFSS diamond product).
- rank mechanism: unchanged sparse factor-log matrix.
- descent: same backend on the target.
- dominant cost exponent: `α := log_L(#power-sums × recurrence-order arithmetic)` — measured.

### Nearest ledger entries
1. **ECFG-MX-1478** — the exact object A3 builds on: MX-1478 found the logarithmic C-finite
   transition oracle **and** that its first composition is a dense quadratic `4L²` state with BM
   order `~half` the sequence. A3's new content: compute the composed resultant via power sums
   *without* materializing that `4L²` object. Distinction: generating-series elimination vs dense
   materialization. **This directly executes MX-1478's own next-action** ("a concrete black-box
   common-root/source algorithm below `L^{1.5}` that emits no dense `L²` object").
2. **RT-1476** — gate A3 feeds. 3. **batch2-A1 (subresultant PRS)** — measures degree `β`; A3
   attacks the *arithmetic* via power sums. 4. **A1 (displacement solve)** — sibling fast primitive
   (structured matrix vs generating series). 5. **ECFG-NR-1479 (factor-log feature spaces `≤L^{1/2}`
   fail)** — A3 does not interpolate logs; it eliminates `u`. Distinction: elimination vs feature fit.

### Nearest literature
Bostan–Flajolet–Salvy–Schost, *Fast computation of special resultants* (J. Symb. Comput. 2006 —
composed products/sums / "diamond products" via power-sum generating series, `Õ(d)`);
Bostan–Chyzak–Salvy (holonomic/∂-finite sequences, creative telescoping); von zur Gathen–Gerhard
Ch. 11 (fast Euclidean). **Gap:** never applied to summation polynomials; the MX-1478 C-finite
structure is exactly the input BFSS needs but this connection is unmade.

### Target family
As A1.

### Full algorithmic path
1. FB `L=q^{1/5}`. 2. For each backward tuple, form the two C-finite transition streams
   (MX-1478 oracle); compute the first `O(d)` power sums of the composed-resultant roots via the
   diamond-product generating series; detect a shared root (a zero power-sum pattern / a common
   factor via the recovered eliminant). 3. Verify `S5=0` exactly. 4. `min(1,L^5/q)`. 5. Sparse
   `Z/n`. 6. Calibration. 7. Descent via the same series backend. 8. Offline template; online
   series. 9. Memory `O(d)` per query, streamed.

### Cost model
If the composed-resultant degree is `d=Õ(L^{α})` and power sums cost `Õ(d)` (C-finite), relation-gen
`= L·Õ(L^{α})`; sub-rho iff `α<3/2`. But MX-1478 already measured the two-transition resultant
degree `~2L²+1` with fitted exponent `1.979` and BM order `~half` — **strong evidence `d=Θ(L²)`**,
i.e. `α≈2`, above the gate. A3's bet is that the *power-sum* representation is cheaper than the
*coefficient* representation even at `d=Θ(L²)` — which only helps if a shared root is detectable
from `o(d)` power sums.

### Why existing negatives do not already kill it
MX-1478 closed the *materialized* `4L²` object and *dense BM* on the full coefficient vector; it did
**not** test whether `o(d)` power sums suffice to detect a shared root. New operation: composed-
resultant power-sum root detection on the C-finite oracle.

### Likely fatal obstruction
MX-1478's evidence (`4L²` degree, BM order `~half`, zero held-out recurrence prediction) predicts the
composed state is *generic* — its power sums carry no early-terminating structure, so detecting a
shared root needs `Θ(d)=Θ(L²)` power sums, giving `α≈2` and no sub-rho window. Power-sum
representation is a change of basis, not a degree reduction.

### Minimal falsifying experiment
Toy `p ∈ {1009, 65521, 16769023}`, 3 seeds. Build the MX-1478 oracle; compute power sums of the
composed resultant; measure the *minimum number of power sums* needed to certify presence/absence of
a shared root, as a function of `q`. **Positive control:** two polynomials with a planted common
factor (few power sums suffice). **Negative control:** MX-1478's own dense two-transition object
(expect `Θ(L²)`). Fit `α`.

### Quantitative promotion gate
Shared-root certification from `o(L^{3/2})` power sums across three sizes, with sparse rank `≥L−1`.
Else scoped NEGATIVE closing the power-sum backend for RT-1476 (refining MX-1478 from *coefficient*
density to *power-sum* density).

### Proof track
Theorem: the composed resultant of the two MX-1478 C-finite streams has a shared root iff a length-
`o(L^{3/2})` power-sum pattern vanishes. Would follow from a low-order holonomic relation among the
composed power sums.

### Disproof track
Exhibit the `Θ(L²)` power-sum requirement (generic composed state) — the expected outcome, a clean
statement that the C-finite structure does not compress the *composition*.

### Reproduction artifact
- contract: `research/experiment_contract_a3_powersum_composed_resultant_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/a3_powersum_common_root.sage`
- result/audit: `.../a3_powersum_result.json`, `.../a3_powersum_verify.sage`
- ledger id: **PWRSUM-A3**

### Group B — representation changes

---

## Candidate: B1 — Heisenberg / theta-group Schrödinger–Weil operator representation

### One-sentence mechanism
Represent each point of `E[n]` as an element of the finite **Heisenberg (theta) group** `G(L)` and
the target `Q=[k]P` as a **shift operator** in the `n`-dimensional Schrödinger model, then attempt to
recover the scalar `k` from the **Weil/metaplectic action** of `Sp(E[n])` — a representation change of
the algebraic *object* (point → operator on an `n`-dim space), not the coordinates.

### Status
CONJECTURE (expected computational-negative; the sharp reason is the deliverable — pairs D2).

### Novelty classification
POSSIBLY NOVEL as a *DLP-recovery* mechanism (theta groups/Weil representation are classical —
Mumford, Weil — and the Literature Agent found **no** primary source giving a *classical* DLP
speedup from them). **Critical distinction from batch2(07-17)-B3 `THETA-BILIN-B3`** (which also
invokes a Heisenberg action): `THETA-BILIN-B3` uses level-≥3 theta *coordinates* to build a
*degree-2 bilinear membership predicate* replacing the degree-`2^{m−2}` Semaev relation — it stays
in the *index-calculus relation-generation* lane. B1 instead uses the Heisenberg group's *unique
irreducible operator representation* (Schrödinger model) to attempt *direct scalar recovery* (a
hidden-shift extraction), abandoning relations/factor-base entirely. Different object (operator vs
theta coordinate), different goal (recovery vs membership), different failure mode (hidden-shift
hardness vs Semaev degree). Also distinct from the group-dual DFT (linear characters). **Quantum
caveat, explicit:** this hidden-shift framing is exactly where Shor/Kuperberg bite — B1 is expected
classically negative but is not a quantum-hardness claim.

### Semantic fingerprint F(B1)
- object: theta group `1→F_p^*→G(L)→E[n]→0`; its unique irrep (finite Stone–von Neumann); the
  Schrödinger–Weil representation of `Sp(E[n])`.
- ops: line-bundle / theta-null arithmetic; Heisenberg commutator; Weil-representation intertwiners.
- hidden structure: whether the **shift operator `ρ(Q)`** exposes `k` more cheaply than walking `⟨P⟩`.
- discarded: the coordinate/curve presentation.
- retained: an operator per point; the metaplectic action.
- relation primitive: an operator identity `ρ(P)^k = ρ(Q)` (a hidden shift in the Schrödinger model).
- compression primitive: `n`-dimensional representation theory (Stone–von Neumann uniqueness).
- rank mechanism: (speculative) intertwiner/eigenstructure of the shift.
- descent: recover the shift `k` from `ρ(Q)`.
- dominant cost exponent: cost of extracting the shift — **the object of test**.

### Nearest ledger entries
1. **batch2(07-17)-B3 `THETA-BILIN-B3` (level-≥3 theta-bilinear membership)** — the closest prior
   candidate: it uses theta *coordinates* + Heisenberg action to build a degree-2 *membership
   predicate* (relation lane); B1 uses the Heisenberg *operator representation* (Schrödinger model)
   for *scalar recovery* (no factor base). Distinction: operator/representation + recovery vs
   coordinate + membership.
2. **07-18(batch1)-B3 (group-dual DFT indicator)** — linear (order-1) characters of `Z/n`; B1 is the
   *non-abelian* Heisenberg representation of `E[n]`, strictly richer. Distinction: Heisenberg irrep
   vs abelian character.
3. **B-class-function no-leakage** — the recurring wall (Frobenius/cohomology see only order/trace);
   B1's bet is that the *torsor/shift* structure (not a class function) is visible in the Schrödinger
   model. Distinction: shift operator vs invariant.
4. **M5 self-pairing (Galbraith–Gilchrist–Robert)** — uses the Weil pairing for isogeny/torsion
   recovery; B1 uses the *representation* the pairing generates, for DLP. Distinction: DLP recovery
   vs isogeny finding.
5. **B-preproc** — any operator precompute must beat `S·T²=Ω̃(εq)`.

### Nearest literature
Mumford, *On the equations defining abelian varieties I* (Invent. Math. 1966, theta groups) and
*Tata Lectures on Theta III*; Weil, *Sur certains groupes d'opérateurs unitaires* (Acta Math. 1964,
metaplectic representation); finite Stone–von Neumann; survey *Heisenberg Groups, Theta Functions
and the Weil Representation* (arXiv:0905.1865); Shor (quant-ph/0301141, the quantum caveat).
**Gap:** no classical DLP algorithm from theta groups; the "as hard as BSGS" claim is folklore, not a
cited theorem — B1's value is to force it to a clean statement.

### Target family
Ordinary prime-order `E/F_p`, `j∉{0,1728}`; excluded specials as A1.

### Full algorithmic path (INCOMPLETE unless the shift is sub-BSGS-recoverable)
1. Build `G(L)` and the Schrödinger model for `E[n]` (`n`-dim, so this is toy-`n` only).
2. Realize `ρ(P)` and `ρ(Q)`; **test whether `k` is extractable from `ρ(Q)` faster than `√n`.**
3. Stages 3–9 depend on step 2: if extraction is `Θ(√n)` (a monomial/permutation shift whose orbit
   is exactly `⟨P⟩` — the expected case) the candidate is a **class-function-analogue negative**;
   only a genuine sub-`√n` intertwiner shortcut makes relation/descent stages definable.

### Cost model
The Schrödinger shift operator is monomial/permutation-type with orbit `⟨P⟩`; extracting the shift
classically walks that orbit → `Θ(√n)` (BSGS), no exponent change. B1 wins only if the metaplectic
action provides an eigen-shortcut. Compare rho `n^{0.5}`.

### Why existing negatives do not already kill it
Orthogonal to every measured lane; the class-function wall addresses *invariants*, and B1 uses a
*non-invariant torsor/shift*. But its honest role is a **negative-theory probe**: does the richest
non-abelian representation of `E[n]` expose the shift?

### Likely fatal obstruction (pairs D2)
**Hidden-shift hardness.** In the Schrödinger model, translation-by-`Q` is a shift whose orbit is
literally `⟨P⟩`; recovering the shift is the abelian hidden-shift/HSP that is classically `Θ(√n)`
(BSGS) and only *quantumly* easy (Shor). The representation reshuffles the group but adds no
classical shortcut — the same reason Kuperberg/Regev results are quantum.

### Minimal falsifying experiment
Toy `n ∈ {7,11,13,101}` (Schrödinger model is `n`-dimensional — small `n` only): build `ρ(P),ρ(Q)`;
measure the cost of extracting `k` from the metaplectic action vs BSGS `√n`. **Positive control:** a
setting with a genuine eigen-shortcut (e.g. a smooth-order shift where Pohlig–Hellman-type
diagonalization applies). **Negative control:** prime-order BSGS (exponent `1/2`).

### Quantitative promotion gate
A classical shift-extraction with exponent `<1/2−ε` across three toy `n`. (Expected `=1/2` — a clean
statement that the Heisenberg/Weil representation is classically shift-hard, a barrier the ledger
lacks.)

### Proof track
Theorem: classical shift-extraction from the Schrödinger model of `E[n]` is `Θ(√n)` (reduces to
abelian HSP with no classical speedup).

### Disproof track
Exhibit a sub-`√n` metaplectic shortcut (a genuine surprise; would be revolutionary).

### Reproduction artifact
- note: `research/b1_heisenberg_weil_formalization_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/b1_theta_group_shift.sage`
- result/audit: `.../b1_theta_result.json`, `.../b1_theta_verify.sage`
- ledger id: **HEIS-B1**

---

## Candidate: B2 — Weil–Châtelet / m-descent torsor representation (collapse barrier)

### One-sentence mechanism
Represent the target via a nontrivial **`m`-covering torsor** of `E` (classical descent: lift the
DLP into a principal homogeneous space where the log becomes a covering coordinate), testing whether
any torsor handle survives over `F_p` — a representation change of the *object* (point → torsor point).

### Status
CONJECTURE (expected clean collapse; the sharp barrier is the deliverable — pairs D2).

### Novelty classification
LEDGER-NEW vocabulary; **the collapse is a citable barrier not stated in the ledger.** The transfer
track closes *same-field isogeny* and *scalar Weil restriction*; it never states the
Weil–Châtelet/Lang triviality of *descent* over finite fields.

### Semantic fingerprint F(B2)
- object: `WC(E/F_p) ≅ H^1(F_p, E)`; `m`-covering torsors; the descent exact sequence
  `0→E(F_p)/mE(F_p)→H^1(F_p,E[m])→H^1(F_p,E)[m]→0`.
- ops: torsor construction; covering maps; Galois cohomology.
- hidden structure exploited (hoped): a nontrivial torsor coordinate encoding `k mod m`.
- discarded: the affine curve presentation.
- retained: (hoped) the covering coordinate.
- relation primitive: `k mod m` from the covering; CRT over many `m`.
- compression primitive: descent/covering.
- rank mechanism: — (collapses first).
- descent mechanism: literally covering descent.
- dominant cost exponent: — (undefined; collapses).

### Nearest ledger entries
1. **Transfer track same-field-isogeny closure** — closes order-based transfer; B2 asks the
   *cohomological descent* question. Distinction: torsor vs isogeny.
2. **07-17(batch1)-C3 / 07-18(batch2)-C3 (xedni / p-adic-height global lift)** — global-field descent
   over `Q` (MW-rank/height wall); B2 asks the *finite-field* version. Distinction: `F_p` vs `Q`.
3. **B-n=1 collapse** — B2 is the cohomological sibling: no proper base field ⇒ no nontrivial torsor.
4. **NR-022 scalar Weil restriction** — restriction within char `p`; B2 uses torsors, also over `F_p`.
5. **B-class-function** — related no-leakage principle.

### Nearest literature
Lang, *Algebraic groups over finite fields* (Amer. J. Math. 1956: `H^1(k,G)=1` for connected `G`
over finite `k`); Lang–Tate (WC ≅ H^1); Serre, *Galois Cohomology*; Milne, *Elliptic Curves*.
**Decisive (Literature Agent):** `WC(E/F_q)=0` — every `E`-torsor over `F_q` is trivial (has a
rational point), so classical `m`-descent has **no nontrivial covering** to lift the DLP into.

### Target family
Ordinary prime-order `E/F_p`.

### Full algorithmic path (INCOMPLETE by design — locates the collapse)
1. Attempt to construct a nontrivial `m`-covering torsor of `E/F_p`. **Step 1 fails: `H^1(F_p,E)=0`
   ⇒ every torsor is trivial.** Only the *arithmetic* handle `H^1(F_p,E[m])≅E(F_p)/mE(F_p)` survives
   — and that is exactly `k mod m`, recoverable only by solving the DLP mod `m` (BSGS-hard). Stages
   2–9 are undefined.

### Cost model
Undefined — the geometric torsor handle is empty; the surviving `E[m]`-handle is BSGS-hard. A
rejection criterion.

### Why existing negatives do not already kill it
No ledger entry states the finite-field descent collapse; B2 supplies it. New operation: the
Weil–Châtelet/Lang triviality as an explicit ECDLP representation barrier.

### Likely fatal obstruction
**`H^1(F_p,E)=0` (Lang).** No nontrivial torsor exists over a finite field; descent needs a global
field (nontrivial Ш/H^1). The only surviving handle is `E(F_p)/mE(F_p)` = the DLP mod `m` itself.

### Minimal falsifying experiment
Formal + toy: for small `E/F_p`, attempt to enumerate nontrivial `E`-torsors (confirm all are
trivial); confirm the `E[m]`-descent sequence recovers only `E(F_p)/mE(F_p)`. **Positive control:**
an elliptic curve over `Q` with nontrivial Ш (torsors exist globally). **Negative control:** the same
curve mod `p` (torsors vanish).

### Quantitative promotion gate
A nontrivial `F_p`-torsor coordinate encoding `k mod m` recoverable in `o(√m)`. (Provably empty —
promotion gate is a challenge to contradict Lang.)

### Proof track (=D2 component)
Theorem: `H^1(F_p,E)=0` ⇒ no ECDLP descent handle over `F_p` beyond `E(F_p)/mE(F_p)`.

### Disproof track
Exhibit a nontrivial `F_p`-torsor (contradicts Lang — impossible).

### Reproduction artifact
- note: `research/b2_weil_chatelet_descent_barrier_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/b2_torsor_triviality_check.sage`
- ledger id: **WCDESC-B2**

---

## Candidate: B3 — Berkovich-skeleton / non-archimedean tropical-of-the-curve representation (collapse barrier)

### One-sentence mechanism
Represent `E` by the **Berkovich skeleton** of a `Q_p`-lift and read the discrete log off a **tropical
Jacobian / cycle-length** coordinate (the Tate-uniformization circle), testing whether any skeleton
handle exists for an ordinary good-reduction curve — a representation change of the *object* (curve →
non-archimedean analytification), distinct from tropicalizing the Semaev *variety* (consumed).

### Status
CONJECTURE (expected clean collapse; the barrier is the deliverable — pairs D2).

### Novelty classification
LEDGER-NEW; **distinct from batch1(07-17)-B3 tropical/p-adic valuation descent**, which tropicalizes
the *Semaev variety* over the residue field. B3 tropicalizes the *curve* (skeleton of `E^{an}`). The
collapse is a citable barrier the ledger lacks.

### Semantic fingerprint F(B3)
- object: `E^{an}` over `Q_p` (or `C_p`); its minimal skeleton.
- ops: reduction; Tate uniformization (if it existed); tropical Jacobian.
- hidden structure exploited (hoped): a cycle-length coordinate `−val(j)` encoding the log.
- discarded: the algebraic curve presentation.
- retained: (hoped) the skeleton metric graph.
- relation primitive: tropical-Jacobian linear structure.
- compression primitive: metric-graph / tropical linear algebra.
- rank mechanism: — (collapses).
- descent: tropical descent.
- dominant cost exponent: — (undefined; collapses).

### Nearest ledger entries
1. **batch1(07-17)-B3 (tropical/p-adic valuation descent on the Semaev variety)** — tropicalizes the
   *relation variety*; B3 tropicalizes the *curve*. Distinct object.
2. **07-18(batch1)-B1 / Serre–Tate canonical lift (rejected)** — lifts to `Z_p` for a formal-log
   channel; B3 lifts for a *skeleton*. Distinction: formal group vs analytification.
3. **B-n=1 collapse** — sibling: good ordinary reduction has no non-archimedean handle.
4. **M5 (Satoh canonical lift for counting)** — same lift used for order/trace; B3 asks for a DLP
   skeleton coordinate. Distinction: counting vs DLP.
5. **B-class-function** — related no-leakage.

### Nearest literature
Berkovich, *Spectral Theory and Analytic Geometry over Non-Archimedean Fields* (1990);
Baker–Payne–Rabinoff, *Nonarchimedean geometry, tropicalization, and metrics on curves*
(arXiv:1104.0320). **Decisive (Literature Agent):** the minimal skeleton of `E^{an}` is a **single
point** for good reduction and a **circle** (circumference `−val(j)=val(q_{Tate})`) only for
*multiplicative/bad* reduction (Tate uniformization). Good ordinary reduction ⇒ contractible skeleton.

### Target family
Ordinary good-reduction `E/F_p` (and any `Q_p`-lift, which stays good-reduction).

### Full algorithmic path (INCOMPLETE by design)
1. Lift `E/F_p` to `E/Q_p`; form the skeleton. **Step 1 collapses: good reduction ⇒ the skeleton is
   a point, no cycle, no tropical-Jacobian coordinate.** A bad-reduction lift would give a circle but
   is a *different curve*. Stages 2–9 undefined.

### Cost model
Undefined — no skeleton handle. A rejection criterion.

### Why existing negatives do not already kill it
No ledger entry states the good-reduction skeleton triviality; B3 supplies it, distinct from the
Semaev-variety tropicalization already tried.

### Likely fatal obstruction
**Good reduction ⇒ trivial skeleton.** The tropical/skeleton handle appears only under multiplicative
(bad) reduction, which the target curve does not have; any `Q_p`-lift of a good-reduction curve stays
good-reduction. Clean, unconditional collapse.

### Minimal falsifying experiment
Formal + toy: confirm the skeleton of a good-reduction `E/Q_p` is a point; confirm a bad-reduction
(Tate) curve gives a circle. **Positive control:** a split-multiplicative curve (`E^{an}=G_m/q^Z`,
circle skeleton). **Negative control:** any good-reduction lift (point).

### Quantitative promotion gate
A skeleton/tropical coordinate of an ordinary good-reduction curve encoding the log. (Provably empty.)

### Proof track (=D2 component)
Theorem: the Berkovich skeleton of an ordinary good-reduction `E` is a point ⇒ no tropical-Jacobian
DLP handle.

### Disproof track
Exhibit a nontrivial good-reduction skeleton (contradicts Berkovich — impossible).

### Reproduction artifact
- note: `research/b3_berkovich_skeleton_barrier_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/b3_skeleton_triviality_check.sage`
- ledger id: **SKEL-B3**

### Group C — high-risk speculative mechanisms

---

## Candidate: C1 — Holographic / matchgate reduction of the m-term decomposition count

### One-sentence mechanism
Represent the **count of m-term factor-base decompositions** (`A+…=R` solutions) as a **Holant / #CSP
instance** and test whether a **holographic basis change** makes its constraint signatures
matchgate-realizable on a planar graph, so **FKT/Pfaffian** computes relation supply in polynomial
time — an output-sensitive relation harvester bypassing Gröbner/resultant elimination.

### Status
CONJECTURE (expected #P-hard by the Cai–Lu dichotomy; the either-way result is the deliverable).

### Novelty classification
POSSIBLY NOVEL (the Literature Agent found the holographic-algorithm and ECDLP-decomposition
literatures **entirely disjoint** — no matchgate/Holant framing of Semaev exists; distinct from all
consumed tensor mechanisms, which are *rank* notions, not *matchgate/planar-Pfaffian* tractability).

### Semantic fingerprint F(C1)
- object: the Semaev decomposition constraint as a bipartite Holant signature graph
  (factor-base variables × summation constraints).
- ops: field/tensor ops; holographic basis change; FKT on a planar realization.
- hidden structure exploited (hoped): a basis in which the `S_m` constraint signature is
  matchgate-realizable (satisfies the matchgate/Grassmann–Plücker identities) and planar.
- discarded: the algebraic elimination view.
- retained: the constraint signature tensor.
- relation primitive: a decomposition = a term in the Holant sum.
- compression primitive: **holographic transform + FKT Pfaffian** (poly-time counting).
- rank mechanism: relation *supply* from the count; standard sparse LA downstream.
- descent: count/enumerate decompositions of the target constraint.
- dominant cost exponent: poly-time if matchgate-realizable; else `#P`-hard (no polynomial cost).

### Nearest ledger entries
1. **batch1(07-17)-B2 (tensor-train / separator rank)** & **07-18(batch1)-B4 (Semaev border rank)** —
   both are *rank* compressions of the S3 tensor; C1 asks a *tractability-class* question (matchgate/
   planar), decided by the Holant dichotomy, not a rank bound. Distinct invariant.
2. **RT-1476 / M3 membership** — C1 is a *counting/harvesting* route, not a per-query membership
   backend; if the count is holographically tractable, relations are output-sensitive. Distinction:
   count-all vs decide-one.
3. **M1b DB-join (P1510–P1513)** — the join lower bound is *combinatorial* (input floor `r^3`); C1
   asks whether an *algebraic* holographic circuit evades it. Distinction: WCOJ vs Holant.
4. **B-explicit-edge (P1434)** — C1 lives in the generative regime P1434 leaves open.
5. **B-Dreg** — C1 abandons polynomial-system *solving* for constraint *counting*.

### Nearest literature
Valiant, *Holographic Algorithms* (SICOMP 2008); Cai–Choudhary (Holant/matchgate tensors);
Cai–Lu–Xia (Holant* dichotomy, STOC 2009); Cai–Chen (#CSP complex-weight dichotomy, JACM 2017);
Cai–Guo–Williams (STOC 2013 dichotomy); R. Williams, *Counting Solutions to Polynomial Systems*
(SOSA 2018); Cheng–Hu, *Counting Value Sets* (arXiv:1111.1224). **Verdict (Literature Agent):**
polynomial-system solution counting over `F_q` is #P-complete in general (already quadratics over
`F_2`); the tractable islands are affine / product / matchgate signatures — a measure-zero set; the
symmetric, per-variable degree-`2^{m−2}` Semaev constraint has no planar interaction structure, so
#P-hardness is predicted. **Gap:** no explicit #P-hardness proof for the *specific* Semaev count, and
no impossibility ruling out a clever gadget — both directions are open and either would be novel.

### Target family
Random ordinary prime-order `E/F_p`; excluded specials as A1.

### Full algorithmic path
1. Encode the m-term decomposition constraint (factor-base indicator × summation) as a Holant
   signature graph. 2. Search for a holographic basis making all signatures matchgate-realizable;
   test planarity. 3. If realizable, FKT counts decompositions in poly time → output-sensitive
   relation supply; else classify via the dichotomy (→ #P-hard, barrier D3). 4–9. Standard IC
   downstream if a count route exists.

### Cost model
If matchgate-realizable and planar: FKT is `O(V^3)` per query — poly, a genuine exponent change vs
birthday `B²`. If not (predicted): #P-hard, no polynomial route. Compare rho `n^{0.5}`.

### Why existing negatives do not already kill it
Attacks the P1434 generative loophole via a *tractability class*, not a rank bound or explicit edge
circuit. New operation: holographic transform + FKT of the Semaev constraint.

### Likely fatal obstruction (pairs D3)
**Cai–Lu dichotomy predicts #P-hardness.** The Semaev signature is symmetric with per-variable
exponential degree and no planar structure, so it almost surely lies outside all three tractable
classes → #P-hard, no holographic shortcut. Matchgate signatures have bounded arity/parity that the
Semaev constraint violates.

### Minimal falsifying experiment
Symbolic + toy: for `m∈{3,4}`, write the decomposition constraint as a Holant instance; test each of
the three tractability classes (affine, product, matchgate-after-basis-change); check planarity.
**Positive control:** a known matchgate-realizable constraint (FKT counts it). **Negative control:** a
generic non-matchgate signature (dichotomy → #P-hard). Report the class membership per `m`.

### Quantitative promotion gate
The Semaev constraint (some `m`) is matchgate-realizable on a planar Holant instance ⇒ poly-time
relation counting ⇒ promote. Else scoped NEGATIVE = barrier D3 (Semaev decomposition counting is
#P-hard / non-holographic).

### Proof track
Theorem: the m-term Semaev decomposition-counting signature is matchgate-realizable after a
holographic basis change (would be revolutionary), OR (=D3) provably #P-hard / outside all three
tractable classes.

### Disproof track
The dichotomy classification places the signature outside affine/product/matchgate — the expected,
citable barrier.

### Reproduction artifact
- contract: `research/experiment_contract_c1_holographic_semaev_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/c1_holant_signature_classify.sage`
- result/audit: `.../c1_holant_result.json`, `.../c1_holant_verify.sage`
- ledger id: **HOLANT-C1**

---

## Candidate: C2 — Higher-order-Fourier / nilsequence relation predictor

### One-sentence mechanism
Test whether the sequence `k ↦ x([k]P)` carries **higher-order (quadratic/nilsequence) Fourier
structure** (a Gowers-`U^s` correlation with a nilsequence) that a **degree-`s` inverse-theorem
detector** could use to predict relation-bearing `k` more cheaply than random — a representation
change to the *higher-order dual*, strictly beyond the (consumed) linear group-dual DFT.

### Status
CONJECTURE (expected negative: the sequence is Gowers-uniform / pseudorandom; the precise
uniformity statement is the deliverable).

### Novelty classification
POSSIBLY NOVEL (higher-order Fourier / inverse theorems are mature in additive combinatorics but,
per no prior report and no ledger entry, never applied to ECDLP; strictly distinct from
07-18(batch1)-B3 group-dual DFT, which uses order-1 linear characters only, and from
07-18(batch1)-C1 Bogolyubov approximate-homomorphism, which is a `U^2`/Freiman statement).

### Semantic fingerprint F(C2)
- object: the map `f:Z/n→F_p`, `f(k)=x([k]P)`, and its Gowers `U^s` norms / nilsequence correlations.
- ops: EC arithmetic; box/Gowers-norm estimation; nilsequence correlation.
- hidden structure exploited (hoped): a large `U^{s}` correlation ⇒ a degree-`(s−1)` polynomial-phase
  structure among `{x([k]P)}` ⇒ predictable relations.
- discarded: the linear (order-1) spectrum (known structureless).
- retained: the higher-order phase.
- relation primitive: a nilsequence-predicted `k` with `A+C=R` support.
- compression primitive: degree-`s` inverse theorem (Green–Tao–Ziegler).
- rank mechanism: relations from the predicted structured set.
- descent: locate the target's `k` via the higher-order phase.
- dominant cost exponent: cost of estimating a large `U^s` correlation without logs — the crux.

### Nearest ledger entries
1. **07-18(batch1)-B3 (group-dual DFT)** — order-1 characters; C2 is order-`≥2`. Distinction:
   higher-order vs linear Fourier.
2. **07-18(batch1)-C1 (Bogolyubov approximate-homomorphism)** — a `U^2`/energy statement; C2 uses the
   full `U^s` inverse theory (nilsequences). Distinction: `U^2` vs `U^{≥3}`.
3. **ECFG selector chain** — empirical combinatorial statistics of `k→x(kB)`; C2 asks whether the
   *higher-order Fourier dual* has structure. Distinction: nilsequence vs graph statistic.
4. **character-sum/Kloosterman bias (rejected, prior)** — linear exponential-sum bias; C2 is
   higher-order. Distinction: `U^2` bias vs `U^s`.
5. **B-preproc** — a higher-order precompute must beat `S·T²`.

### Nearest literature
Gowers (`U^s` norms); Green–Tao–Ziegler (inverse theorem for the Gowers norms, nilsequences); Green–
Tao (nilsequences and the primes); Bourgain–Garaev–Konyagin–Shparlinski (exponential sums on curves,
the *linear* case — already equidistributed). **Gap:** no higher-order-Fourier analysis of
`x([k]P)`; the linear case is known structureless (equidistribution), which *predicts* higher-order
uniformity but has never been checked.

### Target family
Ordinary prime-order `E/F_p`, prime `n`.

### Full algorithmic path (INCOMPLETE unless a large `U^s` correlation exists)
1. Sample `f(k)=x([k]P)`; estimate `U^2, U^3` norms. 2. **If `U^s` is small (Gowers-uniform,
   expected) there is no higher-order structure and the candidate is a negative/barrier;** only a
   large `U^s` correlation makes relation/descent stages definable. 3–9. Conditional on structure.

### Cost model
If a nilsequence correlation of magnitude `δ` exists and is estimable in `Õ(1/δ^{O(1)})`, structured
relations follow; but equidistribution of `x([k]P)` predicts `U^s`-uniformity (`δ=n^{−Ω(1)}`),
requiring `Θ(√n)` samples to detect — no gain. Compare rho `n^{0.5}`.

### Why existing negatives do not already kill it
The linear-character negatives (DFT, Kloosterman) address order-1; C2 asks the strictly-higher-order
question no entry tested.

### Likely fatal obstruction
**Higher-order uniformity.** `x([k]P)` is heuristically Gowers-uniform (the map is "algebraically
pseudorandom"), so all `U^s` norms are `n^{−Ω(1)}` and no nilsequence predicts relations; detecting
any residual correlation costs `Θ(√n)`. A precise, valuable negative.

### Minimal falsifying experiment
Toy `p∈{1009,65521,1000003}`: estimate `U^2,U^3` norms of `x([k]P)` and search for a correlated
degree-2 nilsequence. **Positive control:** a genuine quadratic phase `e(αk²/n)` (large `U^3`).
**Negative control:** a random function (uniform). Fit the `U^s` norm vs `n`.

### Quantitative promotion gate
A `U^s` correlation `δ=n^{−o(1)}` yielding relation prediction at cost `<√n`. (Expected `δ=n^{−Ω(1)}`
— a clean "elliptic scalar map is higher-order-uniform" barrier.)

### Proof track
Theorem: `‖x([·]P)‖_{U^s} = n^{−Ω(1)}` for ordinary `E/F_p` (higher-order equidistribution). Would
follow from bounds on complete exponential sums with nilsequence weights on curves.

### Disproof track
Exhibit a large `U^s` correlation (a genuine surprise, opening a higher-order relation lane).

### Reproduction artifact
- contract: `research/experiment_contract_c2_higher_order_fourier_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/c2_gowers_nilsequence.sage`
- result/audit: `.../c2_gowers_result.json`, `.../c2_gowers_verify.sage`
- ledger id: **NILSEQ-C2**

---

## Candidate: C3 — Orthogonal-lattice (Nguyen–Stern) hidden-relation finder

### One-sentence mechanism
Encode the factor base as an integer lattice whose **short vectors are exactly the low-weight
relations** `Σ a_i F_i = O`, and use **LLL/BKZ orthogonal-lattice (Nguyen–Stern) reduction** to
detect a hidden relation from *public coordinate data alone* (without knowing the logs) — a
representation change to a lattice whose geometry (hoped) exposes the relation shortness.

### Status
CONJECTURE (expected negative: logs are pseudorandom mod `n`, so relations have no short integer
representative; the precise obstruction is the deliverable).

### Novelty classification
POSSIBLY NOVEL (orthogonal-lattice / Nguyen–Stern is standard for hidden-subset-sum and
hidden-linear-structure, but never applied to EC relation harvesting; distinct from all consumed
mechanisms — the ledger uses no lattice-reduction relation finder). NOVELTY-UNVERIFIED pending a
deeper hidden-number-problem cross-check.

### Semantic fingerprint F(C3)
- object: the lattice `Λ = {a∈Z^B : Σ a_i·log(F_i) ≡ 0 (mod n)}` and its orthogonal complement.
- ops: EC arithmetic (to build public rows); LLL/BKZ.
- hidden structure exploited (hoped): low-weight relations are *short* in `Λ`.
- discarded: the group presentation.
- retained: the lattice geometry.
- relation primitive: a short vector of `Λ` = a relation.
- compression primitive: lattice reduction.
- rank mechanism: independent short vectors → relation matrix.
- descent: express the target as a short combination.
- dominant cost exponent: the gap between `λ_1(Λ)` and the low-weight relation norm — the crux.

### Nearest ledger entries
1. **07-17(batch1)-C3 / 07-18(batch2)-C3 (xedni / p-adic-height lattice lift)** — those lift to a
   *Mordell–Weil height lattice over `Q`*; C3 builds a *relation lattice over `Z` from `F_p` data*.
   Distinct object (relation lattice vs MW lattice).
2. **M1 five-term relations** — same relations, different finder (lattice vs decomposition search).
3. **B-explicit-edge (P1434)** — C3 is a generative/sketch route (LLL detects without enumerating).
4. **07-18(batch1)-B3 (group-dual DFT)** — both seek hidden additive structure; C3 uses lattice
   geometry, DFT uses the spectrum. Distinction: SVP vs Fourier.
5. **B-preproc** — the reduced basis must beat `S·T²`.

### Nearest literature
Lenstra–Lenstra–Lovász (LLL 1982); Nguyen–Stern (orthogonal lattice, the hidden-subset-sum attack);
Coppersmith (small roots); Boneh–Venkatesan (hidden number problem). **Gap:** no lattice-reduction
relation finder for EC factor bases; the hidden-number-problem line attacks *nonce leakage*, not
relation harvesting.

### Target family
Ordinary prime-order `E/F_p`, prime `n`.

### Full algorithmic path (INCOMPLETE unless relations are short)
1. Build public rows encoding factor-base coordinate constraints; form `Λ`. 2. **Reduce; test whether
   a low-weight relation is the shortest vector.** If logs are pseudorandom, `λ_1(Λ) = Θ(n^{1/B})`
   (Minkowski) with the relation vector *not* short — no gap, LLL returns noise; the candidate is a
   negative. Stages 3–9 conditional on a shortness gap.

### Cost model
LLL is poly in `B` and `log n`; the question is the *gap* `‖relation‖ / λ_1(Λ)`. Pseudorandom logs ⇒
no gap ⇒ no detection. If (contrary to expectation) low-weight relations are `n^{−Ω(1)}`-shorter than
generic vectors, LLL finds them in poly time — an exponent change. Compare rho `n^{0.5}`.

### Why existing negatives do not already kill it
No ledger entry tries lattice reduction on the relation lattice. New operation: orthogonal-lattice
detection of hidden low-weight EC relations.

### Likely fatal obstruction
**Pseudorandom logs ⇒ no lattice shortness.** The map `F_i ↦ log(F_i) mod n` is heuristically
uniform, so the relation lattice is a random `Z/n`-kernel lattice whose low-weight relations are *not*
shorter than generic vectors (no exploitable gap); LLL returns Minkowski-length noise. The DLP is
precisely the statement that this map has no efficiently-detectable structure.

### Minimal falsifying experiment
Toy `p∈{1009,65521,1000003}`: build `Λ`, LLL-reduce, measure `‖shortest found‖` vs the true
low-weight relation norm. **Positive control:** a planted short relation (LLL must find it).
**Negative control:** a random `Z/n`-kernel lattice (no gap). Fit the gap vs `n`.

### Quantitative promotion gate
LLL/BKZ recovers a low-weight relation with a shortness gap growing across three sizes, at cost
`<√n`. (Expected no gap — a clean "EC relation lattice has no exploitable shortness" barrier.)

### Proof track
Theorem: the relation lattice of a random EC factor base has `λ_1 = Θ(`Minkowski`)` with low-weight
relations non-short (no LLL detectability). Would follow from log-uniformity.

### Disproof track
Exhibit a shortness gap on a real (non-planted) factor base (a genuine surprise).

### Reproduction artifact
- contract: `research/experiment_contract_c3_orthogonal_lattice_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/c3_orthogonal_lattice_relations.sage`
- result/audit: `.../c3_lattice_result.json`, `.../c3_lattice_verify.sage`
- ledger id: **OLAT-C3**

### Group D — negative-theory / barrier candidates

---

## Candidate: D1 — Sum-product / additive-energy ceiling on low-weight relation supply

### One-sentence mechanism
Prove (via the **sum-product / additive-energy** bounds for elliptic-curve x-coordinates —
Bourgain–Garaev–Konyagin–Shparlinski, Rudnev, Shkredov) an **upper bound** on the number of
independent low-weight additive relations a factor base of `B` curve x-coordinates can supply,
locating exactly why coordinate IC stalls — a barrier, not an algorithm.

### Status
HYPOTHESIS / OPEN (a provable ceiling; expected to bound 2-term relation supply below the naive
`B²`).

### Novelty classification
POSSIBLY NOVEL as an ECDLP barrier (per the Literature Agent, sum-product on EC x-coordinates is
established, but has **never** been stated as a relation-supply ceiling for index calculus; slice-rank
/ CLP is structurally mismatched to a 1-dimensional `F_p` factor base and is *not* the right tool —
this is the honest correction). Distinct from 07-18(batch1)-A2 Sidon (an additive *design* proposal)
and from the border-rank barrier (a *tensor-rank* notion).

### Semantic fingerprint F(D1)
- object: `A = {x(F_i)}`, a set of `B` curve x-coordinates; its additive energy `E^+(A)`.
- ops: incidence/character-sum estimates (Rudnev point-plane; BGKS).
- hidden structure exploited: **a curve's x-set cannot be simultaneously additively and
  multiplicatively structured** — `E^+(A)` is bounded away from `|A|^3`.
- discarded: — (analysis, not algorithm).
- retained: the energy bound.
- relation primitive: a 2-term relation `x(F_i)+x(F_j)=x(F_k)+x(F_l)` (an additive quadruple).
- compression primitive: — .
- rank mechanism: the count of independent additive quadruples bounds low-weight relation supply.
- descent: — .
- dominant cost exponent: the relation-supply exponent (upper-bounded).

### Nearest ledger entries
1. **07-18(batch1)-A2 (Sidon/B_h additive design)** — proposes to *design* a low-energy base; D1
   *proves* an unconditional energy ceiling for *any* curve x-set. Distinction: design vs bound
   (D1 is A2's promised "design ceiling," now sourced).
2. **B-addition-law scrambling (prior barrier)** — qualitative; D1 makes it quantitative via
   sum-product. Distinction: quantitative energy bound.
3. **07-17(batch1)-B2 border-rank LB** — a *tensor-rank* barrier on the S3 tensor; D1 is an
   *additive-energy* barrier on the x-set. Different invariant (energy vs rank).
4. **ECFG-NR-1475 (pair-residual buckets fail)** — empirical; D1 explains the ceiling.
5. **RT-1476** — D1 bounds the *2-term* supply; RT-1476 concerns *m=5* membership — D1 does **not**
   close m=5 (the higher-arity supply is larger), which is the precise scope boundary.

### Nearest literature
Bourgain–Garaev–Konyagin–Shparlinski, *sum-product on elliptic curves* (arXiv:0806.0640): for
`A=x(E)` with `|A|≤p^{3/4}`, `max(|A+A|,|A·A|) ≫ min(p,|A|^{4/3})`; Ahmadi–Shparlinski;
Murphy–Petridis–Roche-Newton–Rudnev–Shkredov (Mathematika, arXiv:1702.01003); Rudnev point-plane
(arXiv:1612.02719). **These bound `E^+(A)` from above — a curve-specific ceiling on low-weight
additive relations.** Slice-rank/CLP (Croot–Lev–Pach; Ellenberg–Gijswijt; Tao) is *not* applicable
(mismatched to a 1-dim factor base) — an honest scope correction.

### Target family
`A =` x-coordinates of a factor base on ordinary `E/F_p`, `|A|=B≈n^{1/5}` (well within `p^{3/4}`).

### Full algorithmic path (barrier — analysis)
1. Bound `E^+(A)` via BGKS/Rudnev. 2. Convert the energy bound to an upper bound on the number of
   independent 2-term relations. 3. Compare to the `B²` naive supply and to the rank needed
   (`≥B−1`). 4. State the scope: bounds `m=2`; higher `m` supply is separate.

### Cost model
No cost — a supply ceiling. If independent 2-term relations are `o(B)`, the 2-term coordinate lane
cannot reach full rank without large-prime repair (the observed M1/M4 failure mode).

### Why existing negatives do not already kill it
No ledger entry sources the addition-law scrambling wall to a *quantitative* sum-product ceiling; D1
does, and corrects the tempting-but-wrong slice-rank framing.

### Likely fatal obstruction (to the barrier itself)
The bound is for `m=2`; the actual IC uses `m=5`, where supply is `Θ(B^5/q·…)` and the ceiling is
weaker. D1 is a *sharp barrier for the 2-term lane*, an *explanation* (not a closure) for higher `m`.

### Minimal falsifying experiment
Toy `p∈{65521,1000003,16769023}`: measure `E^+(A)` for factor-base x-sets vs the BGKS bound; count
independent 2-term relations vs `B`. **Positive control:** a random set (energy `≈|A|^3/p`).
**Negative control:** an arithmetic progression (energy `≈|A|^3`, but *not* realizable as a curve
x-set — the point). Fit the energy exponent.

### Quantitative promotion gate
A proven `E^+(A)=o(B^3)` ceiling matching the measured energy across three sizes, converted to an
independent-relation bound `o(B)`. (This *is* the barrier; "promotion" = a clean theorem.)

### Proof track
Theorem: for `A=x(`factor base`)`, `E^+(A) ≤ B^{3−ε}` (from BGKS/Rudnev), hence independent 2-term
relations `= O(B^{1−ε})`.

### Disproof track
Exhibit a curve x-set with `E^+(A)=Ω(B^3)` (would contradict BGKS — impossible for `|A|≤p^{3/4}`).

### Reproduction artifact
- note: `research/d1_additive_energy_relation_ceiling_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/d1_additive_energy_meter.sage`
- ledger id: **ENERGY-D1**

---

## Candidate: D2 — Finite-field structure-collapse barrier (Lang / class-function / skeleton unification)

### One-sentence mechanism
Unify the three collapses located by B1/B2/B3 into a single **finite-field structure-collapse
principle**: every "richer object" attached to `E/F_p` (torsor, skeleton, cohomology, non-abelian
representation) either is a **class function** of Frobenius (order/trace only), **vanishes** by Lang
(`H^1=0`, trivial skeleton), or reduces to a **hidden shift** (BSGS-hard) — so no representation
change over `F_p` yields a sub-`√n` DLP handle without leaving the field.

### Status
HYPOTHESIS (a unifying restricted theorem consolidating scattered no-leakage walls).

### Novelty classification
LEDGER-NEW as a *unified* statement (the ledger has piecemeal class-function and same-field-closure
rows; the Lang/skeleton/hidden-shift trichotomy is not consolidated).

### Semantic fingerprint F(D2)
- object: the category of `F_p`-structures on `E` (torsors, `H^i`, skeleta, `E[n]`-representations).
- ops: — (meta-analysis).
- hidden structure exploited: the trichotomy (class function / Lang-vanishing / hidden-shift).
- relation primitive / compression / rank / descent: — (barrier).
- dominant cost exponent: none survives below `√n` without leaving `F_p`.

### Nearest ledger entries
1. **B-class-function no-leakage (prior barrier)** — the invariant branch of the trichotomy.
2. **Transfer-track same-field closure** — the isogeny-invariant branch.
3. **07-18(batch1)-B1/B2 (Serre–Tate/Cartier–Manin, rejected)** — instances of the class-function
   branch; D2 adds the Lang-vanishing and hidden-shift branches.
4. **B2/B3 (this run)** — the Lang and skeleton instances.
5. **B1 (this run)** — the hidden-shift instance.

### Nearest literature
Lang 1956 (`H^1(F_q,G)=1`); Berkovich / Baker–Payne–Rabinoff (good-reduction skeleton trivial);
Mumford/Weil (theta-group hidden shift); Achter et al. (crystalline order-only, prior). **Together:
every `F_p` handle is order/trace, empty, or BSGS-hard.**

### Target family
Ordinary `E/F_p`.

### Full algorithmic path (barrier — proof program)
1. Class-function branch: Frobenius-invariant data = char poly `X²−tX+p` (order/trace). 2.
Lang-vanishing branch: `H^1(F_p,E)=0`, trivial skeleton. 3. Hidden-shift branch: `E[n]`-arithmetic
and Heisenberg/Weil representations reduce to `E(F_p)/mE` / a shift, BSGS-hard. 4. Conclude: any
sub-`√n` handle must leave `F_p` (→ global-lift/xedni wall).

### Cost model
No cost — a barrier. Its consequence: representation-change candidates over `F_p` are dead unless
they (a) leave the field or (b) exhibit a genuine hidden-shift shortcut (B1's gate).

### Why existing negatives do not already kill it
The ledger states the branches separately; D2's contribution is the exhaustive trichotomy and the
"must leave `F_p`" corollary, which reframes the entire representation-change group.

### Likely fatal obstruction (to the barrier)
The trichotomy might be non-exhaustive — a fourth kind of `F_p`-structure (e.g. a motivic/`t`-motive
object) could exist; D2 must argue exhaustiveness or scope to the enumerated categories.

### Minimal falsifying experiment
Formal: verify the three branches on toy curves (Frobenius char poly; torsor triviality; shift
BSGS-cost). **Positive control:** the multiplicative group `(Z/p)^*` where the `p`-adic log *does*
linearize (a structure that *left* the finite field via `Z_p`). **Negative control:** `E(F_p)` itself.

### Quantitative promotion gate
A proof that the three branches exhaust the efficiently-constructible `F_p`-structures ⇒ a unified
barrier. (A representation-change candidate that escapes all three would *disprove* D2 — that is the
value.)

### Proof track
Theorem: every efficiently-constructible `F_p`-structure on `E` is a Frobenius class function,
Lang-trivial, or hidden-shift-hard.

### Disproof track
Exhibit an `F_p`-structure outside the trichotomy with a sub-`√n` DLP handle (a genuine break).

### Reproduction artifact
- note: `research/d2_finite_field_collapse_trichotomy_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/d2_collapse_branch_checks.sage`
- ledger id: **COLLAPSE-D2**

---

## Candidate: D3 — Cai–Lu Holant dichotomy barrier for Semaev decomposition counting

### One-sentence mechanism
Prove (via the **Cai–Lu / Cai–Chen #CSP–Holant dichotomy**) that the m-term Semaev
decomposition-counting signature lies **outside all three tractable classes** (affine, product,
matchgate), hence relation counting is **#P-hard** and admits no holographic/planar-Pfaffian
shortcut — closing the C1 lane and, more broadly, the "count relations in poly time by structural
tractability" hope.

### Status
HYPOTHESIS / OPEN (a dichotomy-based hardness barrier; the specific #P-hardness proof is unmade).

### Novelty classification
POSSIBLY NOVEL (no prior source classifies the Semaev decomposition count in the Holant framework;
distinct from the border-rank/separator-rank barriers, which are rank statements, not complexity-
class dichotomies).

### Semantic fingerprint F(D3)
- object: the Semaev decomposition-counting signature as a Holant instance.
- ops: — (complexity classification).
- hidden structure exploited: the dichotomy criterion (three tractable classes vs #P-hard).
- relation primitive / compression / rank / descent: — (barrier).
- dominant cost exponent: #P-hard (no polynomial counting route).

### Nearest ledger entries
1. **C1 (this run)** — D3 is C1's expected negative, made a theorem.
2. **07-17(batch1)-B2 border-rank LB / 07-18(batch1)-B4** — rank barriers; D3 is a *tractability-
   class* barrier. Distinct invariant.
3. **M1b DB-join cubic floor (P1510–P1513)** — a *combinatorial* lower bound; D3 is an *algebraic-
   counting* hardness. Complementary.
4. **B-explicit-edge (P1434)** — D3 closes the *counting* form of the generative loophole C1 opened.
5. **B-Dreg** — D3 concerns *counting* hardness, not solving degree.

### Nearest literature
Cai–Lu–Xia (Holant* dichotomy); Cai–Chen (#CSP complex-weight dichotomy, JACM 2017); Cai–Guo–Williams
(STOC 2013); R. Williams (*Counting Solutions to Polynomial Systems*, SOSA 2018 — polynomial-system
counting #P-complete); Cheng–Hu (*Counting Value Sets*). **The dichotomy's tractable islands are
measure-zero; the symmetric, exponential-per-variable-degree Semaev signature falls outside them.**

### Target family
The m-term Semaev decomposition-counting problem over `F_p`.

### Full algorithmic path (barrier — proof program)
1. Encode the Semaev count as a Holant signature. 2. Show it is not affine (nonlinear support). 3.
Show it is not product-type (non-tensor-decomposable, from summation coupling). 4. Show it is not
matchgate-realizable (violates matchgate identities / parity; non-planar; exponential arity/degree).
5. Conclude #P-hard by the dichotomy.

### Cost model
No cost — a hardness barrier. Consequence: no holographic relation-counting shortcut exists; C1 is
closed and the "structural-tractability" counting hope is bounded.

### Why existing negatives do not already kill it
The ledger has no complexity-class classification of the Semaev count; D3 supplies it, distinct from
rank and join barriers.

### Likely fatal obstruction (to the barrier)
The dichotomy applies to *fixed finite* signature sets; the Semaev signature is *parameterized* by `m`
and `p` (a family), so a uniform dichotomy conclusion needs the classification to hold across the
family — a nontrivial technical step (the honest scope caveat), and no *specific* #P-hardness proof
for Semaev exists yet (only the general polynomial-counting hardness).

### Minimal falsifying experiment
Symbolic: for `m∈{3,4,5}`, classify the signature against the three tractable classes. **Positive
control:** a matchgate-realizable signature (tractable). **Negative control:** a generic symmetric
signature (#P-hard). Report class membership.

### Quantitative promotion gate
A proof that the Semaev signature is outside all three classes for some `m` ⇒ #P-hard barrier. (A
signature *inside* a class would instead *promote C1* — the dichotomy makes this decidable.)

### Proof track
Theorem: the m-term Semaev decomposition-counting signature is #P-hard (outside affine/product/
matchgate) — via the Cai–Chen/Cai–Lu dichotomy.

### Disproof track
Exhibit a holographic realization (would promote C1 to a poly-time relation counter — revolutionary).

### Reproduction artifact
- note: `research/d3_holant_dichotomy_barrier_20260718b3.md`
- impl: `experiments/ecdlp_prime_field/d3_semaev_signature_classify.sage`
- ledger id: **HOLDICH-D3**

---

## 4. Ranking

Scored 0–5 on: (a) distance from prior ledger/report mechanisms; (b) plausibility of an exact
verifier; (c) chance of changing an exponent (not a constant); (d) complete-path coverage; (e)
falsifiability at toy scale; (f) literature-novelty confidence; (g) low risk of hidden
preprocessing/memory cost. Rejected: semantic novelty `<3`, no route to descent, no rho comparison,
or no precise distinction from the closest entry.

| Cand | (a) | (b) | (c) | (d) | (e) | (f) | (g) | Verdict |
|---|---|---|---|---|---|---|---|---|
| **A1** displacement-Bézoutian | 4 | 5 | 3 | 5 | 5 | 4 | 4 | **SURVIVES** (conservative winner) |
| **A2** eff-resistance sparsifier | 4 | 5 | 3 | 5 | 5 | 4 | 4 | SURVIVES (alt conservative) |
| **A3** power-sum composed resultant | 3 | 5 | 2 | 5 | 5 | 3 | 4 | survives (weakest: MX-1478 predicts `α≈2`) |
| **B1** Heisenberg/Weil operator | 5 | 4 | 3 | 3 | 3 | 4 | 3 | **SURVIVES** (representation winner) |
| **B2** Weil–Châtelet descent | 5 | 5 | 1 | 2 | 5 | 5 | 5 | survives as **barrier** (D2 component) |
| **B3** Berkovich skeleton | 5 | 5 | 1 | 2 | 5 | 5 | 5 | survives as **barrier** (D2 component) |
| **C1** holographic/matchgate | 5 | 4 | 4 | 4 | 4 | 5 | 3 | **SURVIVES** (high-risk winner) |
| **C2** higher-order Fourier | 5 | 3 | 2 | 3 | 3 | 4 | 3 | survives (expected uniformity negative) |
| **C3** orthogonal lattice | 4 | 4 | 2 | 3 | 4 | 3 | 4 | survives (expected no-gap negative) |
| **D1** additive-energy ceiling | 4 | 5 | 3 | 5 | 5 | 5 | 5 | **SURVIVES** (best barrier — sourced) |
| **D2** collapse trichotomy | 4 | 4 | 2 | 4 | 4 | 4 | 5 | survives (unifying barrier) |
| **D3** Holant dichotomy | 4 | 4 | 3 | 4 | 4 | 5 | 5 | survives (closes C1) |

**Selected winners:**

1. **Best conservative — A1 (displacement-structured Bézoutian backend, `DISP-A1`).** Directly on
   the binding stage (RT-1476 membership `α`), a genuinely distinct fast-elimination primitive
   (Toeplitz displacement rank, never applied to Semaev), an exact verifier, full path coverage,
   toy-falsifiable. Honest risk: shares the eliminant-*degree* wall with all RT-1476 backends —
   which is why it is paired with the degree meter, not proposed alone.
2. **Best representation — B1 (Heisenberg/theta-group Schrödinger–Weil operator, `HEIS-B1`).** The
   only representation candidate whose obstruction is *computational* (hidden-shift hardness) rather
   than a structural annihilation — so it is the most "alive," and even its negative is a clean,
   citable "theta-group is classically shift-hard" barrier the ledger lacks (with an explicit quantum
   caveat).
3. **Best high-risk — C1 (holographic/matchgate decomposition counting, `HOLANT-C1`).** Sharp and
   *decidable* via the Cai–Lu dichotomy, genuinely un-consumed (the two literatures are disjoint), a
   real exponent-changing prize if realizable, and a citable #P-hardness barrier (D3) if not.

Full experiment contracts and first executable commands for the three winners are in §6; a red-team
attempt to prove all three are disguised repetitions or cost-negative is in §7.

---

## 5. Literature grounding (documented external search, primary sources)

Five scouts, primary sources only. Verdicts folded into each candidate's novelty label; the
load-bearing findings:

- **Structured elimination (A1/A3):** displacement-rank Sylvester/Bézout solves are `Õ(d)`
  (Kailath–Sayed; Bini–Pan; GKO), half-GCD is `Õ(d)` (Moenck/Schönhage), composed resultants of
  C-finite sequences are `Õ(d)` via power sums (Bostan–Flajolet–Salvy–Schost 2006). **None applied
  to Semaev.** Kudo–Yokoyama (JMC 2020) note the PDP Gröbner ≈ extended-Euclid but use it for a
  *lower* bound. **Caveat:** single-variable `Õ(d)` is folklore — novelty rests on the iterated
  Semaev structure and must beat F4/F5, and the binding wall is the eliminant *degree*, not the
  arithmetic.
- **Holographic (C1/D3):** Cai–Lu/Cai–Chen dichotomy — tractable islands (affine/product/matchgate)
  are measure-zero; polynomial-system counting over `F_q` is #P-complete (Williams SOSA 2018). **No
  connection to Semaev/EC exists** — either direction is novel.
- **Sum-product / additive energy (D1):** BGKS (arXiv:0806.0640), Murphy–Petridis–Roche-Newton–
  Rudnev–Shkredov (arXiv:1702.01003), Rudnev point-plane (arXiv:1612.02719) bound `E^+(x(E))` from
  above — a curve-specific low-weight-relation ceiling. **Slice-rank/CLP is structurally mismatched**
  to a 1-dim `F_p` factor base (honest correction). Never applied to EC IC.
- **Descent/Heisenberg/skeleton (B1/B2/B3):** Lang 1956 `H^1(F_q,E)=0` (torsor descent trivial over
  `F_p`); Mumford/Weil theta-group hidden-shift = BSGS-hard classically (folklore; quantum caveat via
  Shor); Berkovich good-reduction skeleton is a point (circle needs bad reduction). All three
  collapses confirmed against primary sources.
- **Spectral sparsification (A2):** Spielman–Srivastava (arXiv:0803.0929), BSS (arXiv:0808.0163),
  Matrix-Tree; IC cycle yield is analyzed *combinatorially* only (Lenstra–Manasse; Gaudry–Thomé–
  Thériault–Diem, eprint 2004/153; Nagao). **No spectral treatment exists.** Caveat: the exact
  enrichment is `|E|−|V|+c`; spectra give storage (`O(L)`) and a yield-quality measure, not a larger
  cycle count.

---

## 6. Winner experiment contracts + first commands

*(Contracts follow `templates/research-records.md` shape: hypothesis, null, parameters, metrics,
positive/negative controls, success/falsification criteria, reproduction command. Each experiment is
a **meter** — it measures the promotion-gate exponent, and its own success criterion is a measured
exponent/trend, never toy correctness.)*

### 6.1 A1 — `DISP-A1` displacement-structured Bézoutian backend

- **Hypothesis.** The serial-S3 backward Sylvester matrix `Syl_u(S3,S4)` has displacement rank
  `O(1)` and the GKO superfast solve gives per-query membership at exponent `α<3/2` (RT-1476, m=5).
- **Null.** Displacement rank grows with `L`, or the `u`-eliminant degree is `Θ(q)` (`β≈1`), so
  `α≥3/2`; structured elimination gives no RT-1476 backend.
- **Parameters.** `p∈{1009,65521,16769023}`; 3 seeds each (`20260718..20260720`); ordinary
  prime-order `j∉{0,1728}`; `m=5`; `L=⌈q^{1/5}⌉`.
- **Metrics.** displacement rank of `Syl_u` vs `L`; GKO solve time vs dense resultant vs subresultant
  PRS; fitted `α=log_L(query cost)`; sparse relation rank; peak memory; all vs rho `0.886√n`.
- **Positive control.** A synthetic O(1)-displacement Toeplitz system (GKO must beat dense).
- **Negative control.** A random dense matrix of matched size (GKO gives no gain); and batch2-A1's
  degree meter (must reproduce `β`).
- **Success.** displacement rank flat **and** `α<3/2` across all three sizes with rank `≥L−1`.
- **Falsification.** displacement rank grows, or `β≈1`/`α≥3/2` at any size ⇒ scoped NEGATIVE.
- **Reproduction command (first executable step — degree/structure preflight):**

```bash
sage experiments/ecdlp_prime_field/a1_displacement_bezout_solver.sage \
  --primes 1009,65521,16769023 --seeds 20260718,20260719,20260720 --m 5 \
  --measure displacement_rank,u_degree,solve_time --out a1_displacement_result.json
```

### 6.2 B1 — `HEIS-B1` Heisenberg/theta-group shift extraction

- **Hypothesis.** In the Schrödinger model of `E[n]`, the scalar `k` in `Q=[k]P` is classically
  extractable from the metaplectic action at cost `<√n`.
- **Null.** Shift extraction is `Θ(√n)` (BSGS) — the Heisenberg/Weil representation adds no classical
  shortcut.
- **Parameters.** toy `n∈{7,11,13,101}` (Schrödinger model is `n`-dimensional); 3 seeds; ordinary
  prime-order.
- **Metrics.** cost of classical shift extraction vs BSGS `√n`; whether the metaplectic action
  diagonalizes the shift; mutual information of any operator invariant with `k`.
- **Positive control.** a smooth-order shift where Pohlig–Hellman-type diagonalization applies (full
  leakage). **Negative control.** prime-order BSGS (exponent `1/2`).
- **Success.** extraction exponent `<1/2−ε` across three toy `n`.
- **Falsification.** extraction `=Θ(√n)` ⇒ scoped NEGATIVE = "theta-group classically shift-hard"
  barrier (with quantum caveat).
- **Reproduction command:**

```bash
sage experiments/ecdlp_prime_field/b1_theta_group_shift.sage \
  --orders 7,11,13,101 --seeds 20260718,20260719,20260720 \
  --measure shift_extract_cost,metaplectic_diag,mutual_info --out b1_theta_result.json
```

### 6.3 C1 — `HOLANT-C1` holographic classification of the decomposition count

- **Hypothesis.** For some `m∈{3,4,5}`, the Semaev decomposition-counting signature is
  matchgate-realizable on a planar Holant instance ⇒ FKT counts relations in poly time.
- **Null.** For all `m`, the signature is outside affine/product/matchgate ⇒ #P-hard (barrier D3).
- **Parameters.** symbolic `m∈{3,4,5}`; representative ordinary curves at `p∈{1009,65521}` for the
  concrete signature entries; 3 seeds.
- **Metrics.** signature membership in each of the three tractable classes; planarity of the
  interaction graph; (if realizable) FKT count time vs birthday `B²`.
- **Positive control.** a known matchgate-realizable signature (FKT counts it). **Negative control.**
  a generic symmetric signature (dichotomy → #P-hard).
- **Success.** matchgate-realizable + planar for some `m` ⇒ promote to a costed counter.
- **Falsification.** outside all three classes for every `m` ⇒ scoped NEGATIVE = barrier D3.
- **Reproduction command:**

```bash
sage experiments/ecdlp_prime_field/c1_holant_signature_classify.sage \
  --m 3,4,5 --primes 1009,65521 --seeds 20260718,20260719,20260720 \
  --classify affine,product,matchgate --check-planarity --out c1_holant_result.json
```

---

## 7. Red team — are the three winners disguised repetitions or cost-negative?

**A1 (`DISP-A1`) — is it a solver swap / duplicate of batch2-A1?**
Partly exposed. The task forbids "replacing one solver." A1's defense: it does not swap the
*relation-matrix* solver (forbidden); it changes the *membership-backend* cost exponent `α`, which
RT-1476 identifies as *the* binding gate — and displacement structure is a genuinely distinct
primitive from subresultant PRS (batch2-A1, `Θ(d²)` fraction-free) and tensor-train (batch1-B2).
**But the fatal honesty:** all three primitives (A1, A3, batch2-A1) die to the same eliminant-*degree*
wall — if `β≈1` (the expected Bézout-generic outcome), no fast arithmetic saves `α`. A1 is therefore
**not an independent break**; it is the correct fast backend *conditional* on a subquadratic degree
that no evidence yet supports. Its true value is sharpening "the bottleneck is degree, not
arithmetic" — a scoping contribution, honestly labeled. **Cost-negative risk: high** unless the
degree meter (batch2-A1) first returns `β<3/10`.

**B1 (`HEIS-B1`) — is it a disguised class-function / group-dual DFT repeat?**
Survives as distinct but expected-negative. The group-dual DFT (07-18-batch1-B3) uses order-1
characters; B1 uses the *non-abelian* Heisenberg representation — strictly richer, and its
obstruction is *computational* (hidden shift) not *structural* (class function), so it is not the
same wall. **But:** the hidden-shift reduction to BSGS is folklore, not a cited theorem, and the
honest outcome is `α=1/2` (no classical gain) — the representation reshuffles `⟨P⟩` without a
shortcut. B1 is **cost-negative in expectation**; its deliverable is the clean barrier + the quantum
caveat (this is exactly where Shor bites), not a speedup. Scope: toy-`n` only (the model is
`n`-dimensional), so it can never scale to a crypto-size *attack* even if it surprised.

**C1 (`HOLANT-C1`) — is it a disguised tensor-rank repeat, and is #P-hardness a foregone conclusion?**
Survives as genuinely novel but predicted-negative. C1 is *not* a rank barrier (batch1-B2 border
rank / batch1-07-18-B4): the Holant dichotomy is a *tractability-class* question, orthogonal to rank.
The Literature Agent confirms the two literatures are disjoint. **But:** the dichotomy almost
certainly places the symmetric, exponential-degree Semaev signature in #P-hard territory (no planar/
matchgate structure), so C1's *positive* branch is a long shot; its realistic yield is barrier D3.
**Cost-negative risk for the positive branch: very high**; the value is a *decidable* either-way
result — the dichotomy makes the classification a finite check, so unlike most high-risk candidates
C1 *terminates* with a definite verdict.

**Cross-cutting red-team verdict.** None of the three is a *verbatim* repeat, and each has a precise
mathematical distinction from its nearest ledger/report entry (documented above). **But all three are
honestly expected-negative or conditional:** A1 on the degree wall, B1 on hidden-shift hardness, C1 on
the dichotomy. That is consistent with the program's load-bearing finding — *no complete-cost
single-target rho speedup exists on record* — and the winners' real contributions are (i) A1/A3:
localizing the RT-1476 bottleneck to eliminant *degree* (not arithmetic) with two new fast backends
that would win *given* a subquadratic degree; (ii) B1: the first classically-alive representation
candidate + a citable hidden-shift barrier; (iii) C1/D3: a decidable holographic-tractability verdict
on relation counting. **No toy correctness is claimed as a break; every "below rho" remains
unproven; each expected negative is a scoped result, not evidence that prime-field ECDLP is
unimprovable.**

---

## 8. Claim discipline

Everything above is `CONJECTURE`/`HYPOTHESIS`/`OPEN`. Novelty labels are `LEDGER-NEW`,
`LITERATURE-ADJACENT`, `NOVELTY-UNVERIFIED`, or `POSSIBLY NOVEL` per the documented §5 search;
where absence of prior art is the basis, it is labeled provisional. Correctness is distinguished from
performance, and candidate relations from verified ECDLP recovery, throughout. Toy evidence,
heuristics, restricted models, and untested assumptions are labeled. A failed candidate is a scoped
negative result, **not** evidence that prime-field ECDLP cannot be improved. The two open conditional
theorems (RT-1472 `δ>1/4`, RT-1476 `α<3/2`) remain the only rho-relevant live surface; A1/A2/A3 feed
them directly, and the barriers (D1–D3) sharpen the surrounding walls.
