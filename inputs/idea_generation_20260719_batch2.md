# ECDLP Idea Generation — Report batch8 (2026-07-19, second run)

Research Director, empirical cryptanalysis lab. Target: a non-generic
single-target ordinary-prime-field ECDLP algorithm whose **complete** cost beats
Pollard-rho `O(sqrt(n))`. Toy correctness, a new coordinate system, a relation
certificate, faster preprocessing, or an isolated solver win is **not** a
breakthrough.

This is the **10th** idea report (prior nine: `20260717`, `20260717_batch2`,
`20260718{,_batch2..6}`, `20260719`). Ledger ID block used through
`ECFG-P1561` (batch7). This report allocates **`ECFG-P1562..P1573`**.

---

## 0. Input review and ledger inventory

### 0.1 Sources read

1. `/Volumes/Volume/git/autolab/research_ledger.md` (2478 records, ~2.8 MB;
   read via its own machine-readable ID-family index line plus targeted greps —
   the file's records are single very-long-line YAML-ish blocks, so a full
   linear re-read of every record is neither tractable nor necessary given the
   consolidated fingerprint catalogue below).
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md`
   (720 records; frontier `P1509–P1513` confirmed).
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md`
   (389 lines; PO-transfer program runs through **PO96z** = Hom-PPAV /
   finite-Kummer-Cheon).
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json`
   (113 lines).
5. The nine prior idea reports (their internal anti-duplication catalogues
   fingerprint the full ledger; used as the primary de-dup surface).

### 0.2 Inventory (machine-readable ID families and counts)

| Family | Range / count | Meaning |
|---|---|---|
| `P-series` | `P001..P1486` (ledger), report `P1514..P1561` | main experiment/negative records |
| `ECFG-` | `ECFG-001..043`, `NR-1500..1508`, `P1509..P1513` | IC-state frontier (Hasse-jet source chain, marked-resultant/DB-join LBs) |
| `RT-series` | `RT-1471`, **`RT-1472`**, **`RT-1476`**, `RT-1485` | conditional rho-crossing gates + Kummer companion-state note |
| `PO-series` | `PO71..PO96z` | non-generic transfer program (isogeny/Prym/Kummer/Hom-PPAV) |
| `RQ/IDEA/H/EXP/RUN/EV/DEC/TASK/KN-*` | lifecycle records | question→decision chain |

**Number of distinct mechanism lanes reviewed: 48+** (spanning reports 1–9;
enumerated in §0.3). **Number of prior candidate IDs fingerprinted: `P1514..P1561`
(48 report candidates) + the `ECFG`/`RT`/`PO` frontier.**

For every extracted lane I hold: mechanism, representation, exploited structure,
factor base, relation shape, relation-generation method, compression method,
linear-algebra object, target-descent method, cost bottleneck, outcome, scoped
negative boundary, next branch. The consolidated fingerprint table is §0.3.

### 0.3 Consolidated anti-duplication catalogue (mechanism lanes already spent)

- **2-large-prime δ enrichment (RT-1472):** graphic-matroid cycle basis
  (`RT-1472-CYCLEMAT`), matroid-union (`MATUNION-A2`), effective-resistance
  sparsifier (`EFFRES-A2`), 2-core/Wormald DE (`CORRELATED-PEEL-A3`), graph-limit
  cut-norm (`GRAPHON-CUTNORM-B3`), HDX cosystolic/coboundary expansion
  (`HDX-COBOUNDARY-A2`), Lang–Weil point-count supply (`LANGWEIL-SUPPLY-D2`),
  matroid-union non-independence (`MATUNION-INDEP-D2`), VC-dim/Sauer–Shelah
  (`VCDIM-D3`), Guruswami–Sudan decoding radius (`LISTDECODE-B2`), additive-energy
  ceiling (`ENERGY-D1`).
- **m=5 membership backend α (RT-1476):** subresultant/eliminant degree
  (`RT-1476-SUBRES-A1`, batch2-A1), transposed power-projection/Bostan–Schost
  (`POWERPROJ-A1`), Ben-Or–Tiwari/Prony sparse-interp evaluation (`BENORTIWARI-A1`),
  apolarity/catalecticant marked-resultant compiler (`APOLARITY-ATOMIZER-A2`),
  moment-SOS certificate (`SOS-LASSERRE-A1`), Polynomial-Calculus/IPS degree
  (`POLYCALC-D2`), SOS degree LB (`SOS-LB-D1`), query-to-communication lifting
  (`LIFTING-D1`), γ2/sign-rank (`SIGNRANK-GAMMA2-B3`), OV/3SUM fine-grained
  (`FINEGRAINED-OV-D1`), τ-conjecture/Shub–Smale circuit (`CIRCUIT-TAU-D3`),
  border-rank/asymptotic-spectrum (`ASYMPSPEC-D1`, `BORDER-B4`, `TT-B2`),
  Cohn–Umans triple-product convolution (`COHNUMANS-B1`), slice-rank
  (`SLICE-RANK-1-D2`), Schur/plethysm (`SCHURPLETHYSM-B3`), Baur–Strassen witness
  opener (`BAURSTRASSEN-A1`), Lang–Weil/Adolphson–Sperber supply meters
  (`LANGWEIL-METER-A3`, `ADOLPHSPERBER-A2`), Guth–Katz polynomial partitioning
  (`POLYPART-A3`).
- **Representation lanes:** displacement/Toeplitz–Bézoutian (`DISP-A1`),
  power-sum composed-resultant (`PWRSUM-A3`), Heisenberg/theta-Weil (`HEIS-B1`),
  Fourier–Mukai Poincaré kernel (`FOURIERMUKAI-B2`), generalized Jacobian
  (`GENJAC-MODULUS-B1`), Picard–Fuchs/Gauss–Manin (`PICARDFUCHS-B2`), syzygy/Betti
  (`SYZYGY-REGULARITY-B2`), Weil–Châtelet/Lang descent (`WCDESC-B2`), Berkovich
  skeleton (`SKEL-B3`), Ronkin/coamoeba Monge–Ampère (`RONKIN-B1`), Newton
  polytope/tropical (`POLY-A1`, `TROP-B3`), jet-scheme/Hasse-jet (`JET-B1`,
  IC `P1509`), quiver/path-algebra (`QUIV-C1`), motivic/arc-space (`MOTIVIC-B3`),
  Mahler/automatic (`MAHLER-B1`).
- **Arithmetic-dynamics lanes:** transfer operator (`SPEC-C2`), Ritt (`RITT-B3`),
  isogeny-walk (`ISOWALK-C1`), Dynamical Mordell–Lang (`DML-ORBIT-C1`), arboreal
  Galois (`ARBOREAL-C1`/`-MAX-D3`), ACFA difference variety (`ACFA-C1`), Stange
  elliptic net / EDS (`ELLNET-C2`), Cohen–Lenstra volcano (`COHENLENSTRA-C2`).
- **Speculative/other:** growth/SL2 product theorem (`GROWTH-SL2-C1`), Pila–Wilkie
  o-minimal (`PILA-WILKIE-C2`), sandpile/critical group (`SANDPILE-JACOBIAN-C3`),
  higher-order Fourier/nilsequence (`NILSEQ-C2`), orthogonal lattice (`OLAT-C3`),
  holographic/matchgate Holant (`HOLANT-C1`/`HOLDICH-D3`), free probability
  (`FREEPROB-C3`), Croot–Sisask almost-periodicity (`CROOTSISASK-C3`),
  bootstrap-spectral SDP (`BOOTSTRAP-SPECTRAL-C2`, rejected), Weil-explicit-formula
  density (`EXPLICIT-FORMULA-C3`, rejected).
- **Finite-field/collapse controls:** `COLLAPSE-D2` trichotomy, `LINLABEL-UNIFIED-D3`
  (only nonlinear labels escape), `SPARSEBND-D3`.

### 0.4 Standing frontier facts carried into batch8

- **P1512-R1** closes the **scalar-linear Chow/Tate atomizer** at `Ω(r^5)`; only
  the **nonlinear-circuit exception** survives.
- **P1511-R2** closes the **materialized product-circuit factorized semijoin**
  (input degree `r^3`).
- **P1510-R1** marked-resultant per-target compiler evaluates at `Θ(r^2)`/eval;
  `BENORTIWARI-A1` (batch7) recovers `r` relations in `O(r)` evals ⇒ `Θ(r^3)`,
  **"identical exponent to P1511-R2 unless a batched multipoint evaluation shares
  the per-target work."** ← this is the one **open escape hatch** in the backend
  lane. `HANKEL-BLOCK-A3` below attacks it directly.
- **P1513** leaves the **shared-common-norm / both-norms-cubic** boundary open.
- **PO-transfer** program: all transfer routes run through `PO96z`
  (Hom-PPAV / finite-Kummer-Cheon); no ordinary-prime transfer beats rho.
- **Only two live rho-crossing surfaces:** `RT-1472` (`δ>1/4`) and `RT-1476`
  (`α<3/2`). The sparse-LA stage (`n^{2/5}`) is **not** binding. **No ledger entry
  shows a complete-cost single-target rho speedup**; every "below rho" is
  amortized-many-target or setup-uncharged.

**All six task-brief search seeds were declared exhausted in batch4**, and the
one never-used seed (elliptic divisibility sequences) was consumed by
`ELLNET-C2` in batch7. batch8 therefore imports **lower-bound and representation
technologies that no prior report or barrier used**: matrix rigidity, coding-LP
(Delsarte) duality, information-theoretic Shearer submodularity, approximate
degree / dual polynomials, multiparty number-on-forehead communication,
A-hypergeometric (GKZ) D-modules, Honda formal-group logarithms, cluster-algebra
mutation, RKHS kernel-mean embeddings, probabilistic polynomials, and persistent
homology. Each is checked against §0.3 for mechanism-identity, not wording.

---

## 1. Candidates

Twelve candidates in four groups. **Eight begin outside the ledger's dominant
vocabulary** (RIGIDITY, DELSARTE-LP, FORMALGROUP, GKZ, RKHS, PROBABILISTIC-POLY,
APPROXDEG, NOF-COMM). The remaining four extend named frontier objects with a new
operation.

---

### Group A — Conservative extensions of known work

---

## Candidate: RIGIDITY-A1 — Valiant rigidity of the P1510 marked-resultant evaluation matrix

### One-sentence mechanism
Exploit the **structured-matrix form** S of the P1510 per-target compiler to
lower-bound (via Valiant rigidity) the cost C of any depth-2 / linear-circuit
evaluation backend for subproblem P = single-target membership evaluation below
baseline B = the `Θ(r^2)`/eval floor.

### Status
HYPOTHESIS (meter/barrier).

### Novelty classification
POSSIBLY NOVEL (rigidity has never been applied to an ECDLP index-calculus
backend; documented absence in §0.3 and the backend-LB lane).

### Semantic fingerprint
F = (algebraic object: the P1510 marked-resultant coefficient matrix `M_r`;
public ops: field arithmetic on `M_r` entries; hidden structure: displacement/
Sylvester structure of the resultant; info discarded: entries below the rigidity
threshold; info retained: rank profile of `M_r`; relation-gen primitive: none
(this is a cost meter on the *evaluation*); compression primitive: none; rank
mechanism: **Valiant rigidity `R_{M}(r/2)`** = min entries changed to drop rank
below `r/2`; descent mechanism: n/a; dominant cost exponent: the exponent `γ`
such that a linear circuit of size `O(r^{1+γ})` and depth `O(log r)` could
evaluate `M_r`).

### Nearest ledger entries
1. `P1511-R2` (product-circuit semijoin, input degree `r^3`) — measures the
   *materialized product circuit*; RIGIDITY measures the **evaluation matrix's
   rigidity → circuit-depth trade-off**, a different complexity object.
2. `P1512-R1` (scalar-linear Chow atomizer, `Ω(r^5)`, determinantal) — bounds the
   *atomizer*; RIGIDITY bounds the *evaluator*. Distinct matrices, distinct
   measures (determinantal complexity vs rigidity).
3. `POWERPROJ-A1` (transposed power-projection α-meter) — dual-side *algorithm*;
   RIGIDITY is a *lower bound* on the same evaluation.
4. `ASYMPSPEC-D1` (asymptotic spectrum/border rank) — bounds *bilinear* rank;
   rigidity bounds *linear-circuit size at fixed depth*, a stronger/orthogonal
   regime (Valiant's depth-reduction is the bridge, not border rank).
5. `SIGNRANK-GAMMA2-B3` (γ2 factorization norm) — a *communication/matrix-norm*
   bound; rigidity is a *combinatorial rank-robustness* bound. No identity.

### Nearest literature
Valiant 1977 (rigidity → superlinear circuit LB); Alman–Williams 2017
(Walsh–Hadamard is **not** rigid enough — a cautionary result). Gap: no known
explicit family meets Valiant's threshold, and resultant matrices are Toeplitz-like,
hence *plausibly non-rigid* — which is itself the informative outcome.

### Target family
Ordinary `E/F_p`, prime order `n`, `p` a random 160–256-bit prime; exclude
`j∈{0,1728}`, anomalous (`#E=p`), and low-embedding-degree curves. Toy scale
`p ∈ {~10^3, ~10^4, ~10^5}`, factor base `B=p^{1/5}`, `m=5`, `r=|B|`.

### Full algorithmic path
1. **Factor-base construction:** standard `x`-coordinate base of size `r=p^{1/5}`.
2. **Relation generation:** unchanged (Semaev `S_5` membership).
3. **Witness extraction/verification:** re-verify each solved relation by direct
   EC addition (certificate re-check, per `docs/claims-and-verification.md`).
4. **Relation probability:** unchanged; not the object of study.
5. **Matrix dimensions/density/rank:** form `M_r` = the P1510 evaluation matrix;
   compute exact rigidity `R_{M_r}(r/2)` by ILP/exhaustive small-`r` search;
   record rank profile under `t`-entry perturbations for `t=0..r`.
6. **Factor-log calibration:** n/a (meter).
7. **Individual logarithm / descent:** n/a.
8. **Offline/online separation:** the rigidity value is *offline* per curve
   family; report whether it certifies an online-evaluation lower bound.
9. **Memory/parallelism:** rigidity computation is offline, `O(r^2)` memory.

### Cost model
Meter output is the exponent `γ`. Interpretation: if `R_{M_r}(r/2) = Ω(r^2 /
log r · log(r/…))` (Valiant regime), then **no** linear circuit of size
`o(r^2)`/depth `O(log r)` evaluates `M_r`, so any backend factoring through
`M_r` costs `Ω(r^2)`/eval → with `r` targets, `Ω(r^3)` total = **matches
P1511-R2, no rho crossing** via this route. Compare: rho `= n^{1/2} = p^{1/2}`;
IC backend baseline `Θ(r^3)=Θ(p^{3/5})` (already worse than rho at single
target — the α<3/2 hope is exactly to beat this).

### Why the existing negative results do not already kill it
`P1511-R2`/`P1512-R1` bound *specific circuits* (product circuit, scalar-linear
atomizer). Rigidity is a **circuit-independent** structural obstruction: it would
close the "some clever unstructured linear circuit evaluates the backend cheaply"
gap that the two determinantal/product bounds leave open. New operation:
rank-robustness under sparse perturbation.

### Likely fatal obstruction
Resultant/Sylvester matrices are **displacement-structured (Toeplitz-like)**, and
all known structured matrices are **non-rigid** (Alman–Williams-style). So the
meter most likely returns "low rigidity" ⇒ **cannot** rule out a fast backend —
i.e. it fails to *close* the gate but also gives no speedup. Honest expected
outcome: **inconclusive-toward-open**, not a crossing.

### Minimal falsifying experiment
Three sizes `p∈{1009, 10007, 100003}`, 5 seeds each, ordinary prime-order
controls; positive control = a known-rigid matrix (random ±1, expect high
rigidity); negative control = a Toeplitz matrix (expect low rigidity). Measure
`R_{M_r}(r/2)` exactly for `r≤12`, extrapolate the exponent.

### Quantitative promotion gate
Promote only if measured `R_{M_r}(r/2)` **grows faster** than any Toeplitz
control AND the implied evaluation lower bound is *sub*-`r^2` is refuted (i.e. it
would confirm the floor, closing RT-1476 from below — a scoped negative, not a
crossing). A crossing is impossible from a lower-bound meter; the gate is a
**gate-closing** threshold, not a speed threshold.

### Proof track
Theorem: the marked-resultant matrix family `{M_r}` has displacement rank `O(1)`,
hence rigidity `R(r/2) = O(r · polylog)` (non-rigid), formally proving no
rigidity-based backend LB exists — which *redirects* effort to the nonlinear
exception.

### Disproof track
Exhibit `r` and a target family where `R_{M_r}(r/2) = ω(r·polylog)`, reopening a
rigidity LB.

### Reproduction artifact
Contract `experiment_contract_p1562_rigidity_marked_resultant.md`; impl
`tasks/ecdlp_index_calculus/p1562_rigidity_eval_matrix.py`; result
`p1562_rigidity_marked_resultant_probe.json`; audit
`p1562_rigidity_audit.py`; ledger `ECFG-P1562`.

---

## Candidate: DELSARTE-LP-A2 — Delsarte linear-programming supply ceiling on the 2-large-prime relation code

### One-sentence mechanism
Exploit the **coding structure** S of the achievable 2-large-prime relation set
to cap (via the Delsarte LP bound on its dual distance) the number C of
**linearly independent** relations per large-prime block, testing whether the
enrichment exponent `δ` can exceed `1/4` for subproblem P = relation supply,
baseline B = `δ=1/4`.

### Status
HYPOTHESIS (δ-ceiling meter/barrier for RT-1472).

### Novelty classification
POSSIBLY NOVEL (Delsarte/LP duality never applied as an ECDLP relation-supply
ceiling; distinct from every §0.3 δ-lane).

### Semantic fingerprint
F = (object: the binary/`F_r` code whose codewords are the incidence vectors of
honest 2-large-prime relations; public ops: relation sampling + linear algebra;
hidden structure: MacWilliams duality of the relation code; info discarded: the
metric geometry beyond pairwise distances; info retained: the distance
distribution; relation-gen primitive: honest hit generator (no post-hoc
scheduling); compression primitive: none; rank mechanism: **Delsarte LP bound
`A(r,d)` on dual distance** ⇒ independent-relation count; descent: n/a; dominant
exponent: `δ` s.t. #independent relations `= r^{1/2+δ}`).

### Nearest ledger entries
1. `VCDIM-D3` (Sauer–Shelah shatter ceiling on δ) — a **combinatorial**
   shatter-function bound; Delsarte is a **spectral/LP-duality** bound on the same
   δ. Different certificate, potentially tighter where the relation code has
   structured distance distribution.
2. `LISTDECODE-B2` (Guruswami–Sudan decoding radius) — uses the code to
   *generate*; Delsarte uses the code to **bound supply from above**. Opposite
   direction.
3. `LANGWEIL-SUPPLY-D2` (Lang–Weil point count ⇒ `δ≤1/4`) — an **algebraic**
   count of the relation variety; Delsarte is a **coding-theoretic** count.
   Honest risk: both may land at `δ≤1/4`; the value is an *independent* proof.
4. `MATUNION-INDEP-D2` (two honest LP graphs non-independent) — matroid rank;
   Delsarte is code rank. Related but distinct duality.
5. `ENERGY-D1` (additive-energy supply ceiling) — additive-combinatorial;
   Delsarte is code-distributional.

### Nearest literature
Delsarte 1973 (LP bound); McEliece–Rodemich–Rumsey–Welch 1977 (asymptotic LP);
MacWilliams–Sloane. Gap: applying LP duality to the *specific* relation code of
a 2-large-prime graph at `B=q^{1/5}` is unstudied; the dual distance of that code
is uncharacterized.

### Target family
As RIGIDITY-A1; additionally require prime order and honest (unscheduled) hit
generation so the code is not artificially inflated.

### Full algorithmic path
1. **Factor base:** `r=q^{1/5}` primes + two large-prime alphabets of size
   `L=q^{1/5}`.
2. **Relation generation:** honest hit generator producing 2-large-prime
   relations; record incidence vectors → codewords.
3. **Witness verification:** certificate re-check per relation.
4. **Relation probability:** measured empirically (input to the LP).
5. **Matrix/rank:** build the code's distance distribution; solve the Delsarte LP
   for the max independent-set/dual-distance bound `A`.
6. **Factor-log calibration:** the LP output caps the solvable-system size.
7. **Descent:** n/a (supply meter).
8. **Offline/online:** LP is offline per family.
9. **Memory/parallelism:** LP is small; `O(r)` constraints.

### Cost model
Output = `δ` upper bound. If Delsarte LP forces #independent relations
`≤ r^{1/2+1/4}`, then RT-1472 is **closed** (`δ≤1/4`), matching LANGWEIL-SUPPLY by
a different route; if LP *permits* `δ>1/4`, that is a (weak) necessary condition
to keep RT-1472 alive — not a crossing, but a green light. Compare rho `q^{1/2}`.

### Why the existing negative results do not already kill it
`LANGWEIL-SUPPLY-D2` bounds the *variety point count*; a code can have fewer
independent codewords than points (dependencies), so Delsarte can be **strictly
tighter** and close δ even where Lang–Weil is loose. New operation: LP duality on
the distance distribution.

### Likely fatal obstruction
The relation code may have **no useful distance concentration** (random-like),
making the Delsarte LP vacuous (returns the trivial `δ` bound) — reproducing
LANGWEIL-SUPPLY without improvement.

### Minimal falsifying experiment
Three sizes, 5 seeds; positive control = a structured code with known LP bound
(Hamming/BCH — expect tight); negative control = a random code (expect vacuous);
ordinary prime-order curves. Solve the LP, compare `δ` bound across controls.

### Quantitative promotion gate
Close-the-gate threshold: `δ ≤ 1/4` certified ⇒ RT-1472 closed (scoped negative).
Keep-alive: LP permits `δ ≥ 1/4 + ε` for `ε>0` measured stably across sizes.

### Proof track
Theorem: the 2-large-prime relation code has dual distance `d^⊥ = Θ(r)` ⇒ Delsarte
LP forces `δ≤1/4`.

### Disproof track
A curve family whose relation code has a low-dual-distance structured component
admitting `δ>1/4`.

### Reproduction artifact
Contract `experiment_contract_p1563_delsarte_relation_code.md`; impl
`p1563_delsarte_lp_supply.py`; result `p1563_delsarte_lp_probe.json`; audit
`p1563_delsarte_audit.py`; ledger `ECFG-P1563`.

---

## Candidate: HANKEL-BLOCK-A3 — Block-Hankel shared multipoint evaluation of the P1510 compiler across targets

### One-sentence mechanism
Exploit the **shared coefficient structure** S of the P1510 marked-resultant
compiler across all `r` targets to reduce the total backend cost C of subproblem
P = recovering all `r` relations, via a **block-Hankel / matrix-Padé (matrix
Berlekamp–Massey) batched multipoint evaluation**, below baseline B = the
`Θ(r^3)` per-target floor of P1511-R2 / BENORTIWARI-A1.

### Status
HYPOTHESIS (directly resolves the one open escape hatch from batch7).

### Novelty classification
LITERATURE-ADJACENT (batched multipoint evaluation / Bostan–Schost is standard;
its application to *share the P1510 compiler across the target bank* is the new,
untested operation — the exact hatch batch7 flagged unresolved).

### Semantic fingerprint
F = (object: the family `{f_t(z)}` of P1510 compilers, one per target `t`; public
ops: multipoint polynomial evaluation, matrix Padé; hidden structure: whether
`{f_t}` share a common evaluation grid / low-rank coefficient tensor; info
discarded: per-target–specific coefficients if a shared basis exists; info
retained: the shared block-Hankel factor; relation-gen primitive: **batched
shared evaluation** (new); compression primitive: matrix Berlekamp–Massey;
rank mechanism: block-Hankel rank across targets; descent: n/a; dominant
exponent: total-cost exponent `θ` in `Θ(r^θ)`).

### Nearest ledger entries
1. `BENORTIWARI-A1` (Prony per-target, `Θ(r^3)`) — evaluates `f_t` **per target
   independently**; HANKEL-BLOCK tests whether a **single block-structured pass**
   shares the evaluations. This is precisely the "unless multipoint sharing wins"
   clause batch7 left open.
2. `P1511-R2` (materialized product circuit, `r^3` leaves) — a single-target
   lower bound; HANKEL-BLOCK is a **cross-target amortization**, outside the
   single-target model P1511-R2 bounds.
3. `POWERPROJ-A1` (transposed power projection) — dual-side single evaluation;
   HANKEL-BLOCK is a **multi-instance** batching of it.
4. `P1510-R1` (the compiler being evaluated) — the black box.
5. `DISP-A1` (displacement/Toeplitz–Bézoutian elimination) — structured LA on
   *one* system; HANKEL-BLOCK is structured LA **across the target bank**.

### Nearest literature
Bostan–Schost 2005 (multipoint eval / Tellegen); Beckermann–Labahn (matrix
Padé); Kaltofen block-Wiedemann. Gap: no result shares a *marked-resultant target
bank* through one block-Hankel solve; the sharing hinges on a common evaluation
locus that has never been checked for `S_5`.

### Target family
As above; ordinary prime order, `m=5`, `r=p^{1/5}`, full target bank of size `r`.

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}`.
2. **Relation generation:** for the whole target bank, assemble `{f_t(z)}` from
   P1510; attempt a shared multipoint grid `{z_1..z_k}` common to all `t`.
3. **Witness verification:** certificate re-check on every recovered relation.
4. **Relation probability:** unchanged.
5. **Matrix/rank:** form the block-Hankel matrix `H` of stacked evaluations; run
   matrix Berlekamp–Massey; measure its block rank and the solve cost.
6. **Factor-log calibration:** solve the shared linear system for all relations
   at once.
7. **Descent:** individual log uses the same shared backend (report its exponent).
8. **Offline/online:** the shared grid construction is offline; per-target solve
   is online.
9. **Memory/parallelism:** `H` is `O(r·k)`; block ops parallelize.

### Cost model
If a **common evaluation grid of size `O(r)`** exists and the block-Hankel solve
costs `O(M(r) log r)` amortized, total `= Õ(r^2)` ⇒ `θ≈2` ⇒ **α≈1**, which would
**cross RT-1476** (`α<3/2`). If the grids are target-specific (expected), each
target needs its own `Θ(r^2)` evaluation ⇒ `Θ(r^3)` = **reproduces P1511-R2**.
Compare rho `p^{1/2}=p^{0.5}` vs `Õ(r^2)=Õ(p^{2/5})=p^{0.4}` — **a crossing if
`θ=2` holds** (this is the rare candidate with a real positive exponent path).

### Why the existing negative results do not already kill it
`P1511-R2` and `BENORTIWARI-A1` are both **single-target / per-target** bounds.
Neither prices **cross-target sharing**. The new operation (shared block-Hankel
multipoint evaluation) is exactly the unpriced amortization; if it exists it
escapes both bounds.

### Likely fatal obstruction
The P1510 compiler `f_t` depends on the **target-specific source tag** in its
evaluation variable, so the natural evaluation locus is target-specific and **no
common grid exists** ⇒ sharing fails ⇒ `θ=3`. This is the near-certain outcome,
and it would **close the last open sub-question** in the P1510/P1511 backend lane
as a clean scoped negative.

### Minimal falsifying experiment
Three sizes `p∈{1009,10007,100003}`, 5 seeds; measure whether a common
evaluation grid of size `O(r)` reproduces all `r` targets' compilers; positive
control = a synthetic bank with a *planted* shared grid (must give `θ=2`);
negative control = a bank with random per-target tags (must give `θ=3`); ordinary
prime-order curves. Fit `θ` from total solve time vs `r`.

### Quantitative promotion gate
**Crossing threshold:** measured total-cost exponent `θ ≤ 2 + o(1)` (⇒ `α<3/2`)
stable across all three sizes with certificate re-verification. Anything `θ≥2.5`
closes the hatch (scoped negative). Correctness of recovered relations alone is
**not** sufficient — the exponent must be measured.

### Proof track
Theorem: the marked-resultant target bank `{f_t}` admits a rank-`O(r)` block-Hankel
factorization over a shared grid ⇒ `Õ(r^2)` total ⇒ `α<3/2`.

### Disproof track
Show the source-tag dependence forces `Ω(r)` distinct evaluation loci with pairwise
incompatible supports ⇒ no shared grid ⇒ `θ=3` (expected).

### Reproduction artifact
Contract `experiment_contract_p1564_block_hankel_shared_eval.md`; impl
`p1564_block_hankel_target_bank.py`; result `p1564_block_hankel_probe.json`;
audit `p1564_block_hankel_audit.py`; ledger `ECFG-P1564`. **[Conservative
winner — full contract in §3.]**

---

### Group B — Genuine representation changes

---

## Candidate: FORMALGROUP-B1 — Honda formal-group logarithm linearization of the addition relation

### One-sentence mechanism
Exploit the **formal group law** S of `E/F_p` to linearize the `m`-point Semaev
membership (turning `⊕` into `+` under the formal log) and reduce the cost C of
subproblem P = relation membership, below baseline B = the degree-`2m-2` Semaev
solve — **if** the formal log carried `F_p` information.

### Status
CONJECTURE (near-certain negative; value = closing the p-adic-linearization hope).

### Novelty classification
LITERATURE-ADJACENT (formal groups are textbook (Silverman AEC IV); their use as
an ECDLP *relation linearizer* is unstudied but the obstruction is classical).

### Semantic fingerprint
F = (object: the formal group `Ê/Z_p` and its logarithm `log_Ê`; public ops:
formal-power-series arithmetic mod `p^k`; hidden structure: additivity of
`log_Ê(P⊕Q)=log_Ê P+log_Ê Q`; info discarded: everything coprime-to-`p`; info
retained: the `p`-adic parameter `t=-x/y`; relation-gen primitive: linear
membership in log-coordinates; compression: linearization; rank mechanism: linear
system over `Z_p/p^k`; descent: solve linear congruence; dominant exponent: would
be `1` **if** it worked).

### Nearest ledger entries
1. `HEIS-B1` (Heisenberg/theta-Weil operator) — stays in `F_p`, uses theta
   structure; FORMALGROUP moves to the **`p`-adic formal parameter**. Different
   representation, different field.
2. `PICARDFUCHS-B2` (Gauss–Manin/`p`-curvature) — `p`-curvature is the *obstruction*
   to `p`-adic algebraic solutions; FORMALGROUP is the naive `p`-adic linearizer
   `p`-curvature already warns against.
3. `MAHLER-B1` (automatic sequences of `x([k]P)`) — `p`-power structure but in
   `F_p` state complexity; FORMALGROUP is `p`-adic-analytic.
4. `ADOLPHSPERBER-A2` (`p`-adic Newton polygon supply meter) — valuation side;
   FORMALGROUP is the *value* (log) side of the same `p`-adic object.
5. `WCDESC-B2` (Weil–Châtelet/Lang descent) — a different linearization
   (`H^1`), also collapses.

### Nearest literature
Silverman, *AEC* IV (formal groups, `log_Ê`); Coleman integration (the log is the
Coleman integral of the invariant differential); Satoh 2000 (canonical lift point
counting — same `p`-adic machinery). Gap: none of these leak the scalar `k` mod
the group order `n` (coprime to `p`).

### Target family
Ordinary `E/F_p`; canonical lift exists (ordinary ⇒ Serre–Tate). Exclude
supersingular.

### Full algorithmic path
1. **Factor base:** points reducing into the formal group's domain of convergence
   (kernel of reduction) — **empty over `F_p`** except `O`. *(Stage fails here.)*
2–9. **INCOMPLETE:** the formal log converges only on `ker(reduction)`, which over
   the residue field `F_p` is trivial; there is no `F_p`-point (other than `O`)
   whose canonical lift lies in the convergence disk with computable log giving
   `F_p` data. Marked **INCOMPLETE** by design — this candidate is a
   **negative-theory probe**, not a complete attack.

### Cost model
The linear-system exponent would be `1` in log-coordinates, but the map
`P ↦ log_Ê(P)` lands in `Z_p` and is **constant mod `n`** (no dependence on `k`
mod `n`), so zero information about the DLP is recovered. Effective cost to solve
the DLP: **unbounded** (no leakage). Compare rho: rho wins trivially.

### Why the existing negative results do not already kill it
No prior report tested the **formal-group / Coleman-log** representation
explicitly; readers repeatedly propose "`p`-adically linearize the group law."
This candidate **closes that lane by name**, complementing `PICARDFUCHS-B2`'s
`p`-curvature obstruction with the direct convergence/coprimality obstruction.

### Likely fatal obstruction
`gcd(p, n)=1` ⇒ the `p`-adic formal log is orthogonal to the mod-`n` scalar; the
log leaks only the (useless) reduction-kernel coordinate. Classical, decisive.

### Minimal falsifying experiment
Three sizes; compute `log_Ê` of `[k]P` mod `p^k` for random `k`, correlate with
`k mod n`; positive control = the multiplicative group `F_p^*` where the `p`-adic
log **does** leak (baseline that it *can* work when field and order share `p`);
negative control = ordinary EC (expect zero correlation). Ordinary prime order.

### Quantitative promotion gate
Any statistically significant recovery of `k mod n` bits from `log_Ê` (expected:
none). Correctness of the formal arithmetic alone is not a gate.

### Proof track
Theorem (expected): for ordinary `E/F_p`, `log_Ê∘(canonical lift)` factors through
`ker(reduction)` and is independent of the mod-`n` component ⇒ no leakage.

### Disproof track
A curve/parameter where the canonical-lift log correlates with `k mod n` (would
be a major surprise contradicting Serre–Tate).

### Reproduction artifact
Contract `experiment_contract_p1565_formal_group_log_leakage.md`; impl
`p1565_formal_group_log.py`; result `p1565_formal_group_probe.json`; audit
`p1565_formal_group_audit.py`; ledger `ECFG-P1565`.

---

## Candidate: GKZ-DMODULE-B2 — A-hypergeometric (GKZ) D-module of the Semaev toric membership

### One-sentence mechanism
Exploit the **toric (sparse) structure** S of the `m`-th Semaev polynomial by
representing membership solutions as solutions of its **A-hypergeometric (GKZ)
D-module**, whose **holonomic rank** exactly counts the membership branches, to
meter the descent cost C of subproblem P = individual-log branching, against
baseline B = the naive `(2m-2)`-per-variable degree bound.

### Status
HYPOTHESIS (representation + exact α-meter).

### Novelty classification
POSSIBLY NOVEL — **documented search** (WebSearch 2026-07-19) found GKZ applied to
Feynman integrals, mirror symmetry, toric geometry, but **no** application to
Semaev summation polynomials or ECDLP index calculus.

### Semantic fingerprint
F = (object: the GKZ ideal `H_A(β)` of the Semaev Newton polytope `A=Newton(S_m)`;
public ops: Weyl-algebra Gröbner / normal-volume computation; hidden structure:
**toric symmetry of `S_m`**; info discarded: coefficient values (only the support
`A` matters); info retained: the polytope `A` and homogeneity `β`; relation-gen
primitive: n/a (descent meter); compression: toric residue; rank mechanism:
**holonomic rank = normalized volume `vol(A)`** (Adolphson); descent mechanism:
branch-count = number of D-module solutions; dominant exponent: `α` implied by
`vol(A)` growth in `m`).

### Nearest ledger entries
1. `PICARDFUCHS-B2` (Gauss–Manin of a *family of curves*) — D-module of the
   **period family**; GKZ is the D-module of the **summation polynomial itself**
   (a toric object, not a curve family). Different connection, different base.
2. `RONKIN-B1` (amoeba/Monge–Ampère density) — the **archimedean** amoeba of `S_m`;
   GKZ is the **algebraic D-module** on the same polytope. Ronkin measures density;
   GKZ counts holonomic rank.
3. `POLY-A1`/`TROP-B3` (Newton polytope / tropical of `S_m`) — the polytope as a
   **combinatorial** object; GKZ endows it with a **differential-system** structure
   whose rank is a new invariant (normalized volume, not tropical variety).
4. `RT-1476-SUBRES-A1` (eliminant/subresultant degree) — the *resultant* degree;
   GKZ gives the **branch count via holonomic rank**, a distinct (and exactly
   computable) descent meter.
5. `ADOLPHSPERBER-A2` (Newton polygon / exponential sums) — Adolphson–Sperber is
   literally the theory that computes GKZ holonomic rank = volume; ADOLPHSPERBER
   used it as a **supply** valuation, GKZ uses it as a **descent-branch** count.
   Closest neighbor; distinction = supply meter vs descent meter, and D-module vs
   `L`-function.

### Nearest literature
GKZ 1989–1990 (A-hypergeometric systems); Adolphson 1994 (holonomic rank =
normalized volume for non-resonant `β`); Saito–Sturmfels–Takayama (Gröbner
deformations of GKZ). Macaulay2 `Dmodules::gkz` computes it. Gap: `vol(Newton(S_m))`
for symmetrized Semaev is uncomputed in the literature; its growth in `m` is the
open number.

### Target family
Ordinary `E/F_p`; `m∈{3,4,5}`; the meter is characteristic-independent (polytope
only), but relation validity is checked over `F_p`, prime order.

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}`.
2. **Relation generation:** Semaev `S_m` membership (unchanged); the GKZ system
   describes how solutions move with target coefficients.
3. **Witness verification:** certificate re-check.
4. **Relation probability:** unchanged.
5. **Matrix/rank:** compute `A=Newton(S_m)`, its normalized volume `vol(A)` =
   holonomic rank = **exact membership branch count**.
6. **Factor-log calibration:** branch count feeds the descent-tree accounting.
7. **Individual logarithm / descent:** descent branching factor `= vol(A)`;
   exponent `α` from `vol(A)` growth in `m`.
8. **Offline/online:** `vol(A)` is offline per `m`.
9. **Memory/parallelism:** volume computation is offline, small.

### Cost model
If `vol(Newton(S_5))` grows like the **BKK/mixed-volume** bound
`(2m-2)^{m-1}/(m-1)!` (Kushnirenko-style), the descent branching **matches** the
known summation-polynomial degree growth ⇒ **no exponent gain**, `α≥3/2`
reproduced. A crossing requires `vol(A)` to be **strictly sub-BKK** due to a toric
degeneration — the open question. Compare rho `p^{1/2}` vs backend `p^{(1/2)·α}`.

### Why the existing negative results do not already kill it
No prior lane computed the **exact holonomic rank / normalized volume** of the
Semaev polytope; `RT-1476-SUBRES-A1` measured *resultant* degree (an upper bound
that can be loose). The GKZ volume is an **exact, tighter** branch count that could
reveal a toric cancellation the resultant degree hides. New operation:
D-module holonomic-rank computation.

### Likely fatal obstruction
`vol(Newton(S_m))` almost certainly equals the mixed-volume bound (Semaev
polynomials are "generic enough" on their support), so GKZ **reproduces** the
known degree growth exactly — an *exact* negative rather than a crossing.
Resonance of `β` may also break the rank-volume identity, requiring the harder
resonant analysis.

### Minimal falsifying experiment
`m∈{3,4,5}`, exact `vol(Newton(S_m))` via Macaulay2/`polymake`; positive control =
a *dense* degree-`2m-2` polytope (volume = the BKK bound, no gain); negative
control = a *degenerate* toric example with known sub-BKK volume (meter must detect
the drop); ordinary prime-order curves for relation validity. Fit `α` from
`vol(A)` in `m`.

### Quantitative promotion gate
**Crossing signal:** `vol(Newton(S_m))^{1/(m-1)}` grows **strictly slower** than the
resultant-degree baseline, extrapolating to a descent exponent `α<3/2` at `m=5`.
Exact-volume-matches-BKK ⇒ scoped negative (closes the toric-cancellation hope).

### Proof track
Theorem: `Newton(S_m)` is normally-generic ⇒ `vol=` mixed volume `⇒ α=` the known
degree exponent (a clean negative), OR a toric degeneration lemma giving strict
inequality (the positive).

### Disproof track
Exhibit `m` where `vol(Newton(S_m))` < mixed-volume bound, reopening a descent
speedup.

### Reproduction artifact
Contract `experiment_contract_p1566_gkz_semaev_holonomic_rank.md`; impl
`p1566_gkz_semaev_volume.py` (+ Macaulay2 script); result
`p1566_gkz_holonomic_probe.json`; audit `p1566_gkz_audit.py`; ledger
`ECFG-P1566`. **[Representation winner — full contract in §3.]**

---

## Candidate: CLUSTER-MUTATION-B3 — Cluster-algebra mutation as a relation-generation primitive

### One-sentence mechanism
Exploit the **cluster-algebra structure** S underlying the EC addition/EDS
coordinates to generate new relations from old by **subtraction-free mutation**
(no polynomial-system solve), reducing the cost C of subproblem P = relation
generation below baseline B = per-relation Semaev solving.

### Status
HEURISTIC (representation; high overlap risk with ELLNET — flagged).

### Novelty classification
NOVELTY-UNVERIFIED (cluster/Somos structure of EC is known; its use as a
*generation dynamics* distinct from the ELLNET *evaluation oracle* is the claim).

### Semantic fingerprint
F = (object: the cluster algebra with Somos-4/EDS exchange relations attached to
`E`; public ops: cluster mutation (Laurent-positive exchange); hidden structure:
the exchange matrix `B` of the seed; info discarded: absolute point coordinates;
info retained: the **exchange lattice**; relation-gen primitive: **mutation**
(new); compression: Laurent phenomenon; rank mechanism: rank of the exchange
matrix = independent-relation analog; descent: mutation path to target;
dominant exponent: relations produced per mutation).

### Nearest ledger entries
1. `ELLNET-C2` (Stange elliptic net bilinear-recurrence **oracle**) — **reads**
   `W(k)` values to test membership; CLUSTER **produces** the relation lattice via
   mutation. **Exact distinction:** ELLNET evaluates a fixed net; CLUSTER studies
   the *exchange-matrix rank* as a supply object. Thin margin — the exchange
   relations are the EDS recurrence ELLNET already hits.
2. `MAHLER-B1` (automatic-sequence state) — infinite-state `x([k]P)`; CLUSTER is a
   finite-seed mutation graph.
3. `RITT-B3` (Ritt decomposition of iteration) — polynomial decomposition; CLUSTER
   is exchange dynamics.
4. `SANDPILE-JACOBIAN-C3` (critical group) — a different combinatorial group on a
   graph; CLUSTER is the cluster mutation group.
5. `SYZYGY-REGULARITY-B2` (free resolution) — algebraic relations among generators;
   CLUSTER is exchange relations, a different relation source.

### Nearest literature
Fomin–Zelevinsky 2002 (cluster algebras); Fordy–Hone (Somos sequences and
cluster mutation); Stange 2011 (elliptic nets = EDS = Somos-like). Gap: whether
mutation produces *linearly independent* relations faster than solving; likely no,
because exchange relations reproduce the three-term EDS recurrence.

### Target family
Ordinary `E/F_p`, prime order; EDS coordinates well-defined (`P` non-torsion).

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}`.
2. **Relation generation:** seed a cluster from a factor-base relation; mutate to
   generate candidate relations without solving `S_5`.
3. **Witness verification:** certificate re-check each mutated relation.
4. **Relation probability:** measure fraction of mutations giving *new independent*
   relations.
5. **Matrix/rank:** exchange-matrix rank vs number of mutations.
6. **Factor-log calibration:** standard once relations collected.
7. **Descent:** mutation path from target seed.
8. **Offline/online:** seed offline; mutation online.
9. **Memory/parallelism:** mutation is local, parallel over seeds.

### Cost model
If each mutation yields an independent relation in `O(1)` field ops, generation
cost drops from `Θ(r^2)`/relation (Semaev solve) to `Õ(1)`/relation — a **massive
constant/low-order win** but **not an exponent change** unless the independent
count also grows, which the EDS periodicity forbids. Compare rho: no crossing
expected (periodicity ⇒ single period-`n` family = BSGS).

### Why the existing negative results do not already kill it
`ELLNET-C2` bounded the *oracle-evaluation* route; it did not price *mutation-based
generation*. The new operation (subtraction-free exchange) generates relations
without a solve — untested as a *supply* mechanism.

### Likely fatal obstruction
Cluster mutations for EC seeds reproduce the **EDS three-term recurrence**, whose
values are period-`n`; the generated relations collapse to one `AP` of length `n`
⇒ **periodicity ⇒ BSGS**, exactly the ELLNET kill. The exchange-matrix rank is
`O(1)` (rank-2 for Somos-4).

### Minimal falsifying experiment
Three sizes; count linearly-independent relations vs mutation depth; positive
control = a cluster algebra of *infinite* mutation type (rank grows); negative
control = the EC/Somos-4 seed (rank saturates fast); ordinary prime order.

### Quantitative promotion gate
Independent-relation count grows as `r^{1/2+δ}` with `δ>1/4` from mutation alone
(expected: saturates at `O(1)`). Correctness of mutated relations is not a gate.

### Proof track
Theorem: the EC Somos exchange matrix has rank `2` ⇒ mutation supply is `O(1)`
independent relations (clean negative).

### Disproof track
An EC-derived cluster of unbounded mutation type producing growing independent
supply.

### Reproduction artifact
Contract `experiment_contract_p1567_cluster_mutation_supply.md`; impl
`p1567_cluster_mutation.py`; result `p1567_cluster_probe.json`; audit
`p1567_cluster_audit.py`; ledger `ECFG-P1567`.

---

### Group C — High-risk speculative mechanisms

---

## Candidate: PERSISTENT-HOMOLOGY-C1 — Persistent-homology barcode as a high-δ relation-cluster detector

### One-sentence mechanism
Exploit the **multiscale topology** S of the relation point-cloud (persistent
`H_1` barcode) to detect enrichable dense 1-cycle clusters and steer 2-large-prime
selection to raise C = independent-relation count for subproblem P = δ enrichment,
above baseline B = `δ=1/4`.

### Status
HEURISTIC (high-risk; thin vs cycle-rank — flagged).

### Novelty classification
NOVELTY-UNVERIFIED (TDA/persistent homology never applied to ECDLP relations;
but its `H_1` likely reduces to graph cycle rank = a spent quantity).

### Semantic fingerprint
F = (object: Vietoris–Rips/relation complex filtered by relation weight; public
ops: persistence computation; hidden structure: multiscale `H_1` bars; info
discarded: single-scale data; info retained: bar lifetimes; relation-gen: none
(selector); compression: barcode; rank mechanism: persistent Betti `b_1`;
descent: n/a; dominant exponent: δ from long-bar count).

### Nearest ledger entries
1. `HDX-COBOUNDARY-A2` (cosystolic/coboundary expansion) — **single-scale
   spectral** cohomology; PERSISTENT is **multiscale** homology. Distinct
   invariant, likely correlated.
2. `RT-1472-CYCLEMAT` (graphic-matroid cycle basis) — the algebraic cycle space;
   persistent `H_1` at threshold ∞ **equals** cycle rank ⇒ **overlap risk**.
3. `GRAPHON-CUTNORM-B3` (cut-norm) — a different graph-limit metric.
4. `EFFRES-A2` (effective resistance) — spectral edge importance; persistence is
   topological bar lifetime.
5. `CORRELATED-PEEL-A3` (2-core threshold) — the 2-core is a persistence-like
   filtration; overlap on the filtration idea.

### Nearest literature
Edelsbrunner–Harer (persistent homology); Carlsson (TDA). Gap: over a random
bipartite relation graph, `H_1` is determined by first Betti number
`|E|-|V|+c` — no new information beyond cycle rank.

### Target family
Ordinary `E/F_p`, prime order, honest hit generator.

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}` + two large-prime alphabets.
2. **Relation generation:** honest hits → weighted relation complex.
3. **Witness verification:** certificate re-check.
4. **Relation probability:** empirical.
5. **Matrix/rank:** compute persistent `H_1`; correlate long bars with
   independent-relation gains.
6. **Factor-log calibration:** selected relations feed the solve.
7. **Descent:** n/a.
8. **Offline/online:** persistence offline.
9. **Memory/parallelism:** persistence is `O(|E| α(|E|))`.

### Cost model
If long bars mark clusters yielding `r^{1/2+δ}` independent relations with
`δ>1/4`, crossing; expected `b_1 = |E|-|V|+c` gives exactly the CYCLEMAT δ (no
gain). Compare rho `q^{1/2}`.

### Why the existing negative results do not already kill it
`HDX-COBOUNDARY` and `CYCLEMAT` are single-scale; persistence adds a filtration
that *could* (heuristically) separate enrichable substructure. New operation:
multiscale bar-lifetime thresholding.

### Likely fatal obstruction
For sparse random bipartite relation graphs, persistent `H_1` collapses to the
cycle rank ⇒ **reproduces CYCLEMAT δ**, no gain. Near-certain rebrand.

### Minimal falsifying experiment
Three sizes; compare δ from bar-guided selection vs cycle-basis selection;
positive control = a planted high-persistence cluster (must be detected); negative
control = random graph (bars ≡ cycle rank); ordinary prime order.

### Quantitative promotion gate
Bar-guided δ **exceeds** cycle-basis δ by a stable margin `>1/4` (expected: equal).

### Proof track
Theorem: for the relation complex, persistent `H_1 =` cycle rank (clean negative),
or a separation lemma (positive).

### Disproof track
A relation family where bar lifetimes strictly refine cycle rank into a higher δ.

### Reproduction artifact
Contract `experiment_contract_p1568_persistent_homology_delta.md`; impl
`p1568_persistent_homology.py`; result `p1568_persistence_probe.json`; audit
`p1568_persistence_audit.py`; ledger `ECFG-P1568`.

---

## Candidate: RKHS-KERNEL-C2 — Reproducing-kernel Hilbert space embedding of the membership indicator

### One-sentence mechanism
Exploit a **group-invariant kernel** S so that the membership indicator has a
**low-rank Gram factorization**, reducing the cost C of subproblem P = 5-point
membership decision to a cheap inner product, below baseline B = the degree-`2m-2`
solve.

### Status
HEURISTIC (high-risk).

### Novelty classification
POSSIBLY NOVEL (RKHS/kernel-mean embedding never applied to Semaev membership;
distinct from sign-rank/γ2).

### Semantic fingerprint
F = (object: RKHS `H_k` with group-invariant kernel `k`; public ops: kernel
evaluation; hidden structure: character/orbit decomposition of `k`; info
discarded: high-frequency spectrum; info retained: low-rank kernel features; rel-gen:
membership by thresholded inner product; compression: **kernel low-rank**; rank
mechanism: Gram rank; descent: nearest-feature; dominant exponent: Gram rank vs
`r`).

### Nearest ledger entries
1. `SIGNRANK-GAMMA2-B3` (γ2/sign-rank of the membership matrix) — the **optimal**
   low-rank sign representation; RKHS fixes a **specific group-invariant kernel**
   and studies its spectral decay. Distinction: chosen kernel vs optimal norm.
2. `FOURIERMUKAI-B2` (Poincaré-kernel label) — an algebraic kernel on `E×E`; RKHS
   is a positive-definite analytic kernel for classification.
3. `HEIS-B1` (theta/Weil operator) — representation-theoretic; RKHS uses
   Peter–Weyl only implicitly.
4. `SOS-LASSERRE-A1` (moment/SOS) — moment matrices are kernel Gram matrices;
   overlap on the moment-matrix idea, distinct in using a fixed kernel.
5. `NILSEQ-C2` (nilsequence predictor) — a different structured predictor.

### Nearest literature
Smola–Gretton (kernel mean embedding); Schölkopf–Smola (RKHS). Gap: a
group-invariant kernel's Gram matrix over the group has rank = #characters used =
`Θ(n)` for full separation (Peter–Weyl) — no low-rank shortcut.

### Target family
Ordinary `E/F_p`, prime order, `m=5`.

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}`.
2. **Relation generation:** classify 5-tuples as member/non-member by kernel score.
3. **Witness verification:** certificate re-check on positives.
4. **Relation probability:** measured (with false-positive control per closed
   territory rule — no post-hoc filter credit).
5. **Matrix/rank:** Gram-matrix rank of the invariant kernel on samples.
6. **Factor-log calibration:** standard.
7. **Descent:** nearest-member retrieval.
8. **Offline/online:** kernel features offline.
9. **Memory/parallelism:** Gram `O(r^2)`.

### Cost model
If Gram rank `= o(r)`, membership costs `o(r)`/query ⇒ `α<3/2`, crossing;
expected Gram rank `= Θ(n)` (character basis) ⇒ no shortcut. Compare rho `p^{1/2}`.

### Why the existing negative results do not already kill it
`SIGNRANK-GAMMA2-B3` bounds the *optimal* sign-rank (a Zarankiewicz pincer); a
**fixed group-invariant kernel** could in principle have faster spectral decay
than the worst-case sign-rank — untested. New operation: invariant-kernel spectral
truncation.

### Likely fatal obstruction
Peter–Weyl: separating membership needs `Θ(n)` characters ⇒ Gram rank `Θ(n)` ⇒
reproduces the SIGNRANK Zarankiewicz barrier. Also risks illegitimate post-hoc
classifier credit — must charge full verification.

### Minimal falsifying experiment
Three sizes; measure Gram-rank vs `r` and membership accuracy with certificate
re-check; positive control = a synthetic low-rank-kernel problem; negative control
= the true `S_5` indicator; ordinary prime order.

### Quantitative promotion gate
Gram rank `= o(r)` **and** certificate-verified membership α exponent `<3/2`
stable across sizes (expected: rank `Θ(n)`).

### Proof track
Theorem: any group-invariant kernel separating `S_5` membership has Gram rank
`Ω(n)` (Peter–Weyl) — clean negative.

### Disproof track
An invariant kernel with `o(r)` Gram rank and verified membership.

### Reproduction artifact
Contract `experiment_contract_p1569_rkhs_membership.md`; impl
`p1569_rkhs_kernel.py`; result `p1569_rkhs_probe.json`; audit
`p1569_rkhs_audit.py`; ledger `ECFG-P1569`.

---

## Candidate: PROBABILISTIC-POLY-C3 — Probabilistic-polynomial randomized membership backend

### One-sentence mechanism
Exploit **randomized low-degree approximation** S (a probabilistic polynomial
correct w.h.p.) of the Semaev membership indicator to reduce the cost C of
subproblem P = membership evaluation below baseline B = the exact degree-`2m-2`
eliminant, giving a randomized backend with `α<3/2`.

### Status
HYPOTHESIS (high-risk; cleanly paired with its own killing barrier APPROXDEG-D1).

### Novelty classification
POSSIBLY NOVEL (probabilistic polynomials never applied to Semaev membership;
distinct from exact SOS/PC/subresultant degree).

### Semantic fingerprint
F = (object: a random polynomial `P̃` with `Pr[P̃(x)≠[x∈member]]≤1/3`; public ops:
evaluate `P̃`; hidden structure: low **probabilistic degree** of the indicator;
info discarded: exactness on a `1/3` fraction; info retained: majority-vote
correctness; rel-gen: membership by `O(1)` randomized evaluations; compression:
degree reduction via randomness; rank mechanism: probabilistic degree
`deg~(S_5)`; descent: randomized backend; dominant exponent: `α` from
probabilistic degree).

### Nearest ledger entries
1. `SOS-LASSERRE-A1` (exact moment-SOS certificate) — an **exact** certificate;
   PROBABILISTIC-POLY trades exactness for degree. Different regime.
2. `POLYCALC-D2` (PC/IPS proof degree) — proof-system degree LB; probabilistic
   degree is an **approximation** notion, upper-bounding a *randomized algorithm*.
3. `RT-1476-SUBRES-A1` (exact eliminant degree) — exact; PROBABILISTIC is
   approximate.
4. `FINEGRAINED-OV-D1` (OV/3SUM conditional LB) — a different lower-bound model.
5. `SIGNRANK-GAMMA2-B3` — sign-rank relates to threshold degree, adjacent to
   probabilistic degree but distinct (threshold vs probabilistic).

### Nearest literature
Razborov 1987, Smolensky 1987 (probabilistic polynomials over `F_p`); Alman–Williams
2015 (probabilistic-polynomial algorithms). Gap: the probabilistic degree of the
Semaev `S_5` indicator over `F_p` is uncharacterized; approximate-degree lower
bounds (see D1) likely force it high.

### Target family
Ordinary `E/F_p`, prime order, `m=5`.

### Full algorithmic path
1. **Factor base:** `r=p^{1/5}`.
2. **Relation generation:** construct `P̃` (random restriction / Razborov–Smolensky)
   approximating membership; evaluate on candidate 5-tuples.
3. **Witness verification:** **certificate re-check on every claimed member** (no
   probabilistic credit without re-verification — closed-territory rule).
4. **Relation probability:** measure true/false-positive under re-verification.
5. **Matrix/rank:** probabilistic degree vs `m`.
6. **Factor-log calibration:** standard on verified relations.
7. **Descent:** randomized backend re-run for individual log.
8. **Offline/online:** `P̃` construction offline; evaluation online.
9. **Memory/parallelism:** `P̃` evaluation parallelizes trivially.

### Cost model
If probabilistic degree `d̃(S_5)=o(2m-2)^{?}` giving evaluation `o(r^{3/2})`/query,
then randomized backend `α<3/2` ⇒ **crossing** (after full re-verification of the
`O(1)`-vote positives). If `d̃` matches the exact degree (D1 barrier), no gain.
Compare rho `p^{1/2}`; backend `p^{α/2}`.

### Why the existing negative results do not already kill it
All prior degree bounds (`SUBRES`, `SOS-LB`, `POLYCALC`) are **exact / proof**
degrees; **probabilistic degree can be strictly smaller** than exact degree for
many functions (e.g. OR). No lane tested whether the Semaev indicator is one of
them. New operation: randomized degree reduction.

### Likely fatal obstruction
The membership indicator is a **high-sensitivity, near-full-degree** Boolean-ish
function over `F_p`; approximate-degree lower bounds (APPROXDEG-D1) very likely
force `d̃ = Ω(exact degree)` ⇒ no gain. This is the paired-barrier kill.

### Minimal falsifying experiment
Three sizes `p∈{1009,10007,100003}`, 5 seeds; empirically fit probabilistic
degree of `S_5` membership (min degree for `≤1/3` error), with **full certificate
re-verification** of positives; positive control = OR/threshold function (known
low `d̃`); negative control = a full-degree function (inner product; `d̃=Ω(n)`);
ordinary prime order. Report α from fitted `d̃`.

### Quantitative promotion gate
Fitted probabilistic degree yields certificate-verified membership evaluation with
`α ≤ 3/2 − ε`, stable across all three sizes. **Correctness of `P̃` alone is not a
gate; the re-verified exponent is.**

### Proof track
Theorem: `d̃(S_5) = o(\text{exact deg})` (positive) — would need a random-restriction
argument exploiting Semaev structure.

### Disproof track
APPROXDEG-D1's dual polynomial shows `d̃(S_5)=Ω(\text{exact deg})` (expected) ⇒
close the randomized-backend hope.

### Reproduction artifact
Contract `experiment_contract_p1570_probabilistic_poly_membership.md`; impl
`p1570_probabilistic_poly.py`; result `p1570_probpoly_probe.json`; audit
`p1570_probpoly_audit.py`; ledger `ECFG-P1570`. **[High-risk winner — full
contract in §3.]**

---

### Group D — Negative-theory / barrier candidates

Each imports a lower-bound technology **no prior barrier used** (§0.3 confirms
LIFTING=2-party query-to-comm, POLYCALC=PC/IPS, SOS-LB=SOS, ASYMPSPEC=asymptotic
spectrum, CIRCUIT-TAU=τ-conjecture, FINEGRAINED-OV=OV/3SUM, VCDIM=Sauer–Shelah,
LANGWEIL-SUPPLY=point count, MATUNION-INDEP=matroid). None used approximate
degree, NOF multiparty, or Shearer entropy.

---

## Candidate: APPROXDEG-D1 — Approximate-degree / dual-polynomial lower bound on m=5 membership

### One-sentence mechanism
Any polynomial `ε`-approximating the 5-point membership indicator has degree
`≥ d̃`; a **dual polynomial** certifies `d̃ = Ω(\text{exact Semaev degree})`, so
**no low-degree (hence no sub-`r^{3/2}`-evaluated) backend** exists → lower-bounds
RT-1476 `α`.

### Status
OPEN (barrier).

### Novelty classification
POSSIBLY NOVEL — **documented search** (2026-07-19): no approximate-degree /
dual-polynomial barrier for Semaev/ECDLP exists; closest prior art is *first-fall
degree* (Petit–Quisquater, arXiv 1906.05594 / 1503.08001), which bounds Gröbner
regularity, **not** approximate degree.

### Semantic fingerprint
F = (object: the membership indicator `f_mem:(F_p)^5→{0,1}`; public ops: n/a
(lower bound); hidden structure: symmetry of `S_5`; info discarded: n/a; info
retained: approximate degree `d̃_ε(f_mem)`; rel-gen: n/a; compression: n/a; rank
mechanism: **dual polynomial `ψ` with high pure degree and `⟨ψ,f⟩` large**;
descent: n/a; dominant exponent: lower bound on `α`).

### Nearest ledger entries
1. `SOS-LB-D1` (SOS degree via pseudo-calibration) — **SOS/positivity** degree;
   approximate degree is `ℓ_∞`-approximation degree. Different; often incomparable.
2. `POLYCALC-D2` (PC/IPS Nullstellensatz degree) — **refutation** degree;
   approximate degree is **approximation** degree.
3. `LIFTING-D1` (query-to-communication lifting) — lifts *decision-tree* to
   communication; approximate degree lower-bounds *polynomial* representations.
   Complementary; the dual polynomial is the object lifting often needs.
4. `RT-1476-SUBRES-A1` (exact eliminant degree) — exact degree is `≥` approximate
   degree; APPROXDEG gives a **robust** lower bound surviving approximation
   (kills PROBABILISTIC-POLY-C3 and RKHS-C2).
5. `SIGNRANK-GAMMA2-B3` (sign-rank / threshold degree) — threshold degree `≤`
   approximate degree; related dual-witness technology, distinct quantity.

### Nearest literature
Nisan–Szegedy 1994 (approximate degree); Sherstov (pattern-matrix, dual
polynomials); Bun–Thaler (approximate-degree surveys). Gap: the dual polynomial
for the *Semaev* membership indicator is unconstructed; its pure degree is the
open number.

### Target family
Ordinary `E/F_p`, prime order, `m=5`. Characteristic-sensitive: the indicator is
over `F_p`, so use `F_p`-approximate degree (not Boolean).

### Full algorithmic path (as a barrier)
1. **Factor base / relation gen / … :** n/a — this is a lower bound on any backend
   factoring through a low-degree membership predictor.
2. **Certificate:** construct (empirically at toy `p`, then argue asymptotically) a
   dual polynomial `ψ` orthogonal to all low-degree polynomials with `⟨ψ,f_mem⟩`
   large ⇒ `d̃` lower bound.
3. **Implication:** `d̃=Ω(D)` ⇒ any polynomial-predictor backend costs `Ω(r^{D/…})`
   ⇒ `α≥3/2` from this route.

### Cost model
The barrier output is a lower bound on `α`. If `d̃(f_mem)=Ω(\text{exact deg})`,
then RT-1476's `α<3/2` is **unreachable by any low-degree-predictor backend** ⇒
partial gate closure (scoped to predictor-factoring backends). Rho stays the
single-target champion.

### Why the existing negative results do not already kill it
`SOS-LB`, `POLYCALC`, `SUBRES` bound **exact / proof** degrees; a backend could
sidestep them via **approximation** (PROBABILISTIC-POLY, RKHS). Approximate degree
is the **robust** obstruction closing that approximation loophole — a genuinely new
barrier axis.

### Likely fatal obstruction (to the *barrier's* usefulness)
Approximate degree bounds **polynomial representation** cost, not arbitrary
arithmetic circuits; a backend not factoring through a global low-degree predictor
(e.g. an iterated/structured evaluator) escapes it. So the barrier is **partial**
(covers the predictor class, which PROBABILISTIC-POLY/RKHS inhabit).

### Minimal falsifying experiment
Toy `p∈{1009,10007,100003}`, `m∈{3,4,5}`; via LP, compute the exact
`ε`-approximate degree of `f_mem` for small supports and fit growth; positive
control = OR (low `d̃`); negative control = inner-product/`mod-p` (high `d̃`);
ordinary prime order.

### Quantitative promotion gate
Fitted `d̃(f_mem)` grows to force `α≥3/2` for predictor backends (⇒ closes the
PROBABILISTIC-POLY/RKHS lane). If `d̃` is *small*, that **reopens** a randomized
backend — a positive surprise.

### Proof track
Theorem: a symmetric dual polynomial on `S_5`'s support certifies
`d̃_ε(f_mem)=Ω(2m-2)^{Θ(1)}`.

### Disproof track
An explicit low-degree `ε`-approximant to `f_mem` (would enable PROBABILISTIC-POLY).

### Reproduction artifact
Contract `experiment_contract_p1571_approx_degree_membership.md`; impl
`p1571_approx_degree_lp.py`; result `p1571_approxdeg_probe.json`; audit
`p1571_approxdeg_audit.py`; ledger `ECFG-P1571`.

---

## Candidate: NOF-COMM-D2 — Multiparty number-on-forehead communication lower bound on 5-point membership

### One-sentence mechanism
View 5-point membership as a **5-party number-on-forehead** problem (party `i`
sees all points but its own); a Babai–Nisan–Szegedy / discrepancy bound on its NOF
communication lower-bounds any backend that decomposes membership into ≤5 partial
evaluators with bounded cross-talk → lower-bounds RT-1476 `α`.

### Status
OPEN (barrier).

### Novelty classification
POSSIBLY NOVEL (multiparty NOF never applied to ECDLP; distinct from 2-party
lifting).

### Semantic fingerprint
F = (object: the 5-argument membership predicate as an NOF communication problem;
public ops: n/a; hidden structure: cylinder-intersection / discrepancy of `f_mem`;
info retained: NOF communication complexity `C_5(f_mem)`; rank mechanism:
**discrepancy / BNS cube norm**; descent: n/a; dominant exponent: LB on `α`).

### Nearest ledger entries
1. `LIFTING-D1` (query-to-communication lifting, **2-party**) — NOF is the
   **`k≥3`-party** regime, where cylinder-intersection (not rank) is the measure.
   Genuinely different technology.
2. `FINEGRAINED-OV-D1` (OV/3SUM) — fine-grained conditional; NOF is
   unconditional communication.
3. `SIGNRANK-GAMMA2-B3` (γ2, 2-party) — 2-party matrix norm; NOF cube norm is the
   multiparty analog.
4. `APPROXDEG-D1` — polynomial degree; NOF is communication. Complementary axes.
5. `RT-1476-SUBRES-A1` — the quantity being bounded (`α`).

### Nearest literature
Babai–Nisan–Szegedy 1992 (multiparty NOF, cube norm); Chattopadhyay–Ada 2008;
Sherstov (multiparty discrepancy). Gap: the cube-norm / discrepancy of the Semaev
membership predicate is uncomputed; and the reduction from *arithmetic backend* to
*NOF protocol* must be justified (not every backend yields a 5-party protocol).

### Target family
Ordinary `E/F_p`, prime order, `m=5` (naturally 5 parties).

### Full algorithmic path (as a barrier)
1. n/a (lower bound). 2. Bound `disc(f_mem)` via the BNS cube norm at toy `p`;
   extrapolate. 3. Argue any ≤5-part factored backend with bounded cross-talk is a
   NOF protocol ⇒ its cost `≥ 2^{C_5}` ⇒ `α` lower bound.

### Cost model
If `C_5(f_mem)=Ω(\log r)` (super-constant discrepancy), factored backends cost
`Ω(r^{c})` blocking `α<3/2` for that class. Rho unaffected.

### Why the existing negative results do not already kill it
`LIFTING-D1` is 2-party and cannot bound a genuinely 5-way factored backend; the
5-point membership is intrinsically multiparty. New tech: multiparty cube norm.

### Likely fatal obstruction (to the barrier)
The reduction "arithmetic backend ⇒ NOF protocol" holds only for backends that
**partition the 5 inputs across ≤5 processors with limited communication**; a
monolithic backend is not covered. Partial barrier, class-scoped.

### Minimal falsifying experiment
Toy `p`, `m=5`; estimate the cube norm / discrepancy of `f_mem` on small supports;
positive control = generalized inner product (known high NOF); negative control =
a low-NOF predicate; ordinary prime order.

### Quantitative promotion gate
Estimated `C_5(f_mem)` grows to block `α<3/2` for factored backends; low `C_5`
would (surprisingly) *permit* a communication-efficient backend.

### Proof track
Theorem: `disc(f_mem)` under the BNS cube norm is `2^{-Ω(\log r)}` ⇒ NOF LB.

### Disproof track
A low-discrepancy structure in `f_mem` enabling a cheap 5-party protocol.

### Reproduction artifact
Contract `experiment_contract_p1572_nof_membership.md`; impl `p1572_nof_cube_norm.py`;
result `p1572_nof_probe.json`; audit `p1572_nof_audit.py`; ledger `ECFG-P1572`.

---

## Candidate: SHEARER-D3 — Shearer entropy / submodular supply ceiling on independent 2-large-prime relations

### One-sentence mechanism
The **Shearer entropy inequality** over the factor-incidence hypergraph of honest
2-large-prime relations caps the **entropy (hence count) of linearly independent
relations** per prime block ⇒ `δ ≤ 1/4`, closing RT-1472 by an information-theoretic
route.

### Status
OPEN (barrier).

### Novelty classification
POSSIBLY NOVEL (Shearer/submodular entropy never applied to ECDLP relation supply;
distinct from Lang–Weil count, matroid rank, VC-dim, Delsarte LP).

### Semantic fingerprint
F = (object: the relation ensemble's joint distribution over factor slots; public
ops: n/a; hidden structure: **submodularity of entropy** under the incidence
covering; info retained: `H(\text{relations})`; rank mechanism: **Shearer /
Chung–Frankl–Graham–Shearer covering bound**; descent: n/a; dominant exponent:
upper bound on `δ`).

### Nearest ledger entries
1. `LANGWEIL-SUPPLY-D2` (point count ⇒ `δ≤1/4`) — **algebraic** count; Shearer is
   **information-theoretic**. Honest risk: both land at `δ≤1/4`; value = independent
   proof + tightness where the variety is reducible.
2. `MATUNION-INDEP-D2` (matroid non-independence) — rank submodularity; Shearer is
   **entropy** submodularity (a different submodular function on the same incidence).
3. `VCDIM-D3` (Sauer–Shelah) — shatter function; Shearer is entropy covering.
4. `DELSARTE-LP-A2` (this report) — coding-LP; pairs with Shearer as a second
   information ceiling.
5. `ENERGY-D1` (additive energy) — a second-moment count; Shearer is an entropy
   count.

### Nearest literature
Chung–Frankl–Graham–Shearer 1986 (entropy covering); Radhakrishnan (entropy method);
Bregman–Minc (permanent bound). Gap: the incidence-cover structure of the specific
2-large-prime graph at `B=q^{1/5}` is uncharacterized; the resulting Shearer
constant is the open number.

### Target family
Ordinary `E/F_p`, prime order, honest hit generator (no source scheduling).

### Full algorithmic path (as a barrier)
1. Build the factor-incidence hypergraph of honest relations. 2. Choose a fractional
cover; apply Shearer to bound `H(\text{relation vector})`. 3. Convert entropy bound
to an independent-relation count ⇒ `δ` ceiling.

### Cost model
If Shearer forces #independent `≤ r^{3/4}` (⇒ `δ≤1/4`), RT-1472 closes by
information theory (scoped negative). Rho stays champion.

### Why the existing negative results do not already kill it
`LANGWEIL-SUPPLY` counts variety **points**; entropy counts **independent
information**, which can be **strictly less** when relations share factor structure
(dependencies) — potentially closing δ where Lang–Weil is loose. New tech: entropy
submodularity.

### Likely fatal obstruction (to the barrier's tightness)
If relations are near-independent (high-entropy, random-like), Shearer gives only
the trivial bound = reproduces LANGWEIL-SUPPLY without improvement.

### Minimal falsifying experiment
Three sizes; empirically estimate relation-ensemble entropy and the Shearer cover
bound; positive control = a highly-dependent relation set (entropy `≪` count,
tight); negative control = independent relations (entropy `≈` count, vacuous);
ordinary prime order.

### Quantitative promotion gate
Shearer bound certifies `δ≤1/4` (closes RT-1472) or is provably vacuous (defer to
Lang–Weil).

### Proof track
Theorem: the incidence hypergraph admits a fractional cover giving Shearer entropy
`≤ (3/4)\log r` ⇒ `δ≤1/4`.

### Disproof track
A relation family with entropy exceeding the `δ=1/4` ceiling.

### Reproduction artifact
Contract `experiment_contract_p1573_shearer_supply_ceiling.md`; impl
`p1573_shearer_entropy.py`; result `p1573_shearer_probe.json`; audit
`p1573_shearer_audit.py`; ledger `ECFG-P1573`.

---

## 2. Ranking

Scores 0–5 on: (1) distance from prior ledger mechanisms; (2) plausibility of an
exact verifier; (3) chance of changing an exponent (not a constant); (4)
complete-path coverage; (5) falsifiability at toy scale; (6) literature-novelty
confidence; (7) **low** hidden preprocessing/memory risk (5 = low risk).

| Candidate | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| RIGIDITY-A1 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | 26 | keep |
| DELSARTE-LP-A2 | 4 | 4 | 2 | 5 | 5 | 4 | 4 | 28 | keep |
| **HANKEL-BLOCK-A3** | 3 | 5 | 4 | 5 | 5 | 3 | 4 | 29 | **keep (conservative winner)** |
| FORMALGROUP-B1 | 4 | 5 | 1 | 2 | 5 | 3 | 5 | 25 | keep (negative-theory) |
| **GKZ-DMODULE-B2** | 5 | 5 | 3 | 5 | 4 | 5 | 4 | 31 | **keep (representation winner)** |
| CLUSTER-MUTATION-B3 | 3 | 4 | 2 | 4 | 4 | 3 | 4 | 24 | keep (flagged vs ELLNET) |
| PERSISTENT-HOMOLOGY-C1 | 3 | 3 | 2 | 4 | 4 | 3 | 3 | 22 | keep (flagged vs cycle-rank) |
| RKHS-KERNEL-C2 | 4 | 4 | 2 | 4 | 4 | 4 | 3 | 25 | keep |
| **PROBABILISTIC-POLY-C3** | 4 | 4 | 3 | 5 | 5 | 4 | 4 | 29 | **keep (high-risk winner)** |
| APPROXDEG-D1 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | 31 | keep (highest-EV barrier) |
| NOF-COMM-D2 | 5 | 3 | 4 | 4 | 3 | 5 | 5 | 29 | keep |
| SHEARER-D3 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 29 | keep |

**Rejections:** none scored semantic novelty (col 1) below 3; all have complete
paths (barriers labeled path-as-barrier), quantitative rho comparisons, and a
precise distinction from the closest ledger entry. CLUSTER-MUTATION-B3 and
PERSISTENT-HOMOLOGY-C1 are **kept but flagged** as thin-margin (ELLNET / cycle-rank
respectively) — their value is *closing* those plausible lanes by name, not a
crossing.

### Selected winners

1. **Best conservative — HANKEL-BLOCK-A3 (`ECFG-P1564`).** It resolves the *single
   open sub-question* batch7 left in the entire P1510/P1511 backend lane
   ("identical exponent unless a batched multipoint evaluation shares the
   per-target work"). It is the rare candidate with a **real positive exponent
   path** (`θ=2 ⇒ α≈1`) and a **decisive** experiment either way.
2. **Best representation — GKZ-DMODULE-B2 (`ECFG-P1566`).** Highest total; a genuine
   new algebraic object (A-hypergeometric D-module of the Semaev polytope) with an
   **exact** verifier (holonomic rank = normalized volume, computable in
   Macaulay2/polymake) and documented literature novelty.
3. **Best high-risk — PROBABILISTIC-POLY-C3 (`ECFG-P1570`).** A real exponent-changing
   mechanism (randomized low-degree backend) cleanly **paired with its own killing
   barrier** APPROXDEG-D1, so one toy experiment resolves it decisively.

*(Note for the Coordinator: the three **barriers** APPROXDEG-D1 / NOF-COMM-D2 /
SHEARER-D3 are the highest-expected-value items overall — each, if it reaches
threshold, **closes a live gate** (D1/D2 → `α≥3/2` for RT-1476; D3 → `δ≤1/4` for
RT-1472). Consistent with batch5–7's finding that barriers dominate attacks in EV
on this saturated frontier. They are not selected as the three "winners" only
because the task fixes the winner slots to conservative/representation/high-risk
attack archetypes.)*

---

## 3. Experiment contracts and first executable commands (three winners)

### Contract W1 — HANKEL-BLOCK-A3 (`ECFG-P1564`)

```yaml
id: ECFG-P1564
title: Block-Hankel shared multipoint evaluation of the P1510 compiler across the target bank
hypothesis: >
  The r per-target marked-resultant compilers {f_t} admit a common O(r)-size
  evaluation grid enabling a single block-Hankel / matrix-Pade solve that recovers
  all r relations at total cost Theta(r^theta) with theta <= 2 (=> alpha < 3/2),
  escaping the per-target Theta(r^3) floor of P1511-R2 / BENORTIWARI-A1.
scope:
  curves: ordinary E/F_p, prime order, j not in {0,1728}, non-anomalous, high embedding degree
  sizes: [p=1009, p=10007, p=100003]
  seeds: [1,2,3,4,5]
  m: 5
  factor_base: r = round(p**(1/5))
controls:
  positive: synthetic target bank with a PLANTED shared O(r) grid (must yield theta≈2)
  negative: target bank with random per-target source tags (must yield theta≈3)
  ordinary_prime_order_control: required each size
measure:
  primary: total-solve-cost exponent theta fitted from wall/op-count vs r
  secondary: existence and size of a shared evaluation grid; block-Hankel rank
verification:
  every recovered relation re-verified by direct EC addition (certificate re-check)
  no relation counted without certificate; timeouts are NOT negative evidence
promotion_gate:
  crossing: theta <= 2 + o(1) (=> alpha < 3/2) stable across all 3 sizes, certificates pass
  gate_closed_negative: theta >= 2.5 across sizes (closes the batch7 escape hatch)
inference:
  requested_policy: <from handoff>
  resolved_model: <record actual>
  fallback_used: <bool>
artifacts:
  contract: experiment_contract_p1564_block_hankel_shared_eval.md
  impl: tasks/ecdlp_index_calculus/p1564_block_hankel_target_bank.py
  result: p1564_block_hankel_probe.json
  audit: p1564_block_hankel_audit.py
```

First executable command:
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1564_block_hankel_target_bank.py \
  --p 1009 --m 5 --seeds 1,2,3,4,5 \
  --mode shared_grid --controls planted_shared,random_tags \
  --verify-certificates --emit p1564_block_hankel_probe.json
```

### Contract W2 — GKZ-DMODULE-B2 (`ECFG-P1566`)

```yaml
id: ECFG-P1566
title: A-hypergeometric (GKZ) holonomic rank of the Semaev toric membership as an exact descent-branch meter
hypothesis: >
  The normalized volume vol(Newton(S_m)) = holonomic rank of the GKZ system H_A(beta)
  equals the exact membership branch count; if vol grows strictly slower than the
  resultant-degree baseline, the m=5 descent exponent alpha drops below 3/2.
scope:
  m: [3, 4, 5]
  curves: ordinary E/F_p prime order (for relation-validity checks); meter itself is char-independent
  sizes: [p=1009, p=10007, p=100003]
  seeds: [1,2,3,4,5]
controls:
  positive: dense degree-(2m-2) polytope (vol = BKK mixed volume, no gain)
  negative: degenerate toric example with known sub-BKK volume (meter must detect drop)
  ordinary_prime_order_control: required
measure:
  primary: vol(Newton(S_m)) exact (Macaulay2 Dmodules::gkz / polymake), and alpha = growth exponent in m
  secondary: resonance status of beta (rank=volume validity)
verification:
  cross-check holonomic rank via two independent tools (Macaulay2 and polymake normalized volume)
  relation validity spot-checked over F_p with certificate re-check
promotion_gate:
  crossing: vol^{1/(m-1)} grows strictly slower than resultant-degree baseline => extrapolated alpha<3/2 at m=5
  gate_closed_negative: vol = BKK mixed volume exactly (closes the toric-cancellation hope)
inference: { requested_policy: <handoff>, resolved_model: <actual>, fallback_used: <bool> }
artifacts:
  contract: experiment_contract_p1566_gkz_semaev_holonomic_rank.md
  impl: tasks/ecdlp_index_calculus/p1566_gkz_semaev_volume.py
  result: p1566_gkz_holonomic_probe.json
  audit: p1566_gkz_audit.py
```

First executable command:
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1566_gkz_semaev_volume.py \
  --m 3,4,5 --backend both --controls dense_polytope,degenerate_toric \
  --cross-check --emit p1566_gkz_holonomic_probe.json
```

### Contract W3 — PROBABILISTIC-POLY-C3 (`ECFG-P1570`)

```yaml
id: ECFG-P1570
title: Probabilistic-polynomial randomized backend for m=5 Semaev membership
hypothesis: >
  The probabilistic degree d~(f_mem) of the 5-point membership indicator over F_p is
  strictly below its exact degree, enabling a randomized backend that decides
  membership in o(r^{3/2}) per query (alpha<3/2) AFTER full certificate re-verification.
scope:
  m: 5
  curves: ordinary E/F_p prime order
  sizes: [p=1009, p=10007, p=100003]
  seeds: [1,2,3,4,5]
controls:
  positive: OR / threshold function (known low probabilistic degree)
  negative: inner-product / mod-p function (probabilistic degree Omega(n))
  ordinary_prime_order_control: required
measure:
  primary: fitted probabilistic degree d~ (min degree for <=1/3 error) and implied alpha
  secondary: true/false-positive rate under certificate re-verification
verification:
  EVERY claimed member re-verified by direct EC addition; probabilistic positives get
  NO credit without re-check; report re-verified alpha only
paired_barrier: ECFG-P1571 (APPROXDEG-D1) — its dual polynomial predicts the outcome
promotion_gate:
  crossing: re-verified membership evaluation alpha <= 3/2 - eps stable across 3 sizes
  gate_closed_negative: d~ = Omega(exact degree) (closes randomized-backend hope; consistent with D1)
inference: { requested_policy: <handoff>, resolved_model: <actual>, fallback_used: <bool> }
artifacts:
  contract: experiment_contract_p1570_probabilistic_poly_membership.md
  impl: tasks/ecdlp_index_calculus/p1570_probabilistic_poly.py
  result: p1570_probpoly_probe.json
  audit: p1570_probpoly_audit.py
```

First executable command:
```bash
cd /Volumes/Volume/git/autolab/ecdlp_index_calculus_state && \
python3 tasks/ecdlp_index_calculus/p1570_probabilistic_poly.py \
  --p 1009 --m 5 --seeds 1,2,3,4,5 \
  --controls or_threshold,inner_product --verify-certificates \
  --emit p1570_probpoly_probe.json
```

---

## 4. Red-team: are the three winners disguised repetitions or cost-negative?

**HANKEL-BLOCK-A3 — is it just BENORTIWARI/POWERPROJ/P1511-R2 renamed?**
Attack: batched multipoint evaluation is standard and P1511-R2 already lower-bounded
the product circuit. Rebuttal: P1511-R2 and BENORTIWARI are **single-target /
per-target**; neither prices **cross-target grid sharing**, which is a distinct
model (the exponent lives in `r` = #targets, not per-target degree). Verdict: **not
a rename** — but **near-certain cost-negative**: the P1510 compiler's evaluation
variable carries a target-specific source tag ⇒ no common grid ⇒ `θ=3`. Honest
expected outcome: **closes the escape hatch** as a scoped negative. It is *not* a
disguised repetition; it is the disproof of the last open sub-question in that lane.

**GKZ-DMODULE-B2 — is it PICARDFUCHS/RONKIN/SUBRES in new words?**
Attack: it's "another Newton-polytope / another resultant-degree" candidate.
Rebuttal: the holonomic rank = normalized volume is an **exact branch count**,
strictly different from PICARDFUCHS (D-module of a *curve family*, not the summation
polynomial), RONKIN (archimedean density), and SUBRES (resultant *upper bound*).
Documented literature search found **no** GKZ↔Semaev crossover. Verdict: **not a
rename**. **Cost-risk:** near-certain that `vol(Newton(S_m))` = the BKK mixed volume
(Semaev is generic on its support) ⇒ **exact negative**, reproducing the known
degree growth — but as an *exact tight* count, upgrading the SUBRES *upper bound* to
an equality (real ledger value).

**PROBABILISTIC-POLY-C3 — is it SOS/POLYCALC/SUBRES with randomness bolted on?**
Attack: all prior degree bounds already cover it. Rebuttal: those are **exact/proof**
degrees; **probabilistic degree can be strictly smaller** (OR is the canonical
example), a regime no lane tested. Verdict: **not a rename**. **Cost-risk:**
near-certain the membership indicator is high-sensitivity ⇒ APPROXDEG-D1's dual
polynomial forces `d̃=Ω(exact)` ⇒ **no gain**. The pairing with D1 makes the negative
*decisive* rather than merely likely.

**Cross-cutting red-team.** All three winners are, in expectation, **scoped
negatives / exact tightenings**, not crossings — consistent with the standing
frontier fact that **no complete-cost single-target rho speedup exists in the ledger
or any prior report**, and that on this saturated frontier the **barriers**
(APPROXDEG-D1, NOF-COMM-D2, SHEARER-D3) carry the higher expected value because each
threshold-reaching barrier *closes a live gate*. The three winners were selected to
(a) resolve the one genuinely open backend sub-question (W1), (b) convert a loose
upper bound into an exact count (W2), and (c) test the last untested degree regime
with a decisive paired barrier (W3). **No break is claimed. RT-1472 and RT-1476
remain open.**

---

## Claim discipline

- **Correctness ≠ performance.** Every "crossing" gate above requires a *measured
  exponent or complete-cost trend*, never correctness of a certificate alone.
- **Candidate relations ≠ verified ECDLP recovery.** All contracts re-verify every
  claimed relation by direct EC addition; probabilistic/kernel positives get **no**
  credit without re-check (closed-territory rule on post-hoc selectors).
- **Toy scale is labeled.** All experiments are `p ≤ 10^5`; no toy result is
  presented as crypto-scale.
- **Timeouts/crashes are not negative mathematical evidence.**
- **A failed candidate is a scoped negative**, not evidence that prime-field ECDLP
  cannot be improved.
- **Novelty labels are honest:** POSSIBLY NOVEL (RIGIDITY, DELSARTE-LP, GKZ, RKHS,
  PROBABILISTIC-POLY, APPROXDEG, NOF-COMM, SHEARER — with the two documented
  searches for GKZ and approximate-degree), LITERATURE-ADJACENT (HANKEL-BLOCK,
  FORMALGROUP), NOVELTY-UNVERIFIED (CLUSTER-MUTATION, PERSISTENT-HOMOLOGY — both
  flagged thin-margin).

**Sources (documented external search, 2026-07-19):**
- [Semaev summation polynomials / degree 2m−2 and first-fall degree (arXiv:1503.08001)](https://arxiv.org/pdf/1503.08001)
- [First fall degree of summation polynomials (arXiv:1906.05594)](https://arxiv.org/pdf/1906.05594)
- [Semaev, new algorithm for ECDLP (eprint 2015/310)](https://eprint.iacr.org/2015/310.pdf)
- [GKZ A-hypergeometric ideal (Macaulay2 Dmodules)](https://macaulay2.com/doc/Macaulay2/share/doc/Macaulay2/HolonomicSystems/html/_gkz.html)
