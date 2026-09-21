# Idea Generation — Research Director report (batch10)

- **Date:** 2026-07-19
- **Role:** Research Director, empirical cryptanalysis lab
- **Mission:** genuinely mechanism-new, falsifiable directions for a non-generic
  prime-field ECDLP algorithm whose **complete** single-target cost could beat the
  Pollard-rho `O(sqrt(n))` baseline.
- **Report family:** 12th idea-generation report (batch10). Prior reports:
  `20260717`, `20260717_batch2`, `20260718{,_batch2..6}`, `20260719{,_batch2,_batch3}`.
- **Proposed ledger IDs this batch:** `ECFG-P1586 … ECFG-P1597`.
- **Claim discipline up front:** No ECDLP break is claimed. Every candidate below is a
  CONJECTURE/HYPOTHESIS/HEURISTIC/OPEN at toy scale. The two live rho-crossing gates
  **RT-1472** and **RT-1476** remain open. A failed candidate here is a *scoped* negative
  result, never evidence that prime-field ECDLP is unimprovable.

---

## 0. Required input review + machine-readable inventory

All five required inputs read in full:

1. `/Volumes/Volume/git/autolab/research_ledger.md` — 2478 lines.
2. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md` — 720 lines.
3. `/Volumes/Volume/git/autolab/research/non_generic_transfer_search_20260610.md` — 389 lines.
4. `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_sources/bibliography.json` — 10 primary sources.
5. Current experiment contracts, negative-result tables, open-frontier questions, and the
   literature map referenced by the above (P1509–P1513 IC-state frontier; RT-1472/RT-1476/RT-1485
   conditional theorems; PO-transfer program in the transfer-search doc).

### Inventory (not a recent-entry sample; full grep census)

| Source | Unique record IDs | Families covered |
|---|---:|---|
| Main ledger | **1826** ECFG record IDs | `ECFG-{P,NR,RT,MX,H}`; RT set = `{RT-1472, RT-1476, RT-1485}` |
| IC-state ledger | **82** P-series records | `P1405…P1513`, `IDEA-0xx…-1xx`, `PO*` transfer program |
| Transfer-search doc | PO-transfer program | Hom-PPAV / finite-Kummer-Cheon chain through `PO96*` |
| Bibliography | 10 primary sources | Semaev'04, Gaudry'09, FPPR'12, Shantz–Teske'13, FHJRV'14, Kousidis–Wiemers'15, Karabina'15, Amadori–Pintore–Sala'17, McGuire–Mueller'17, Trimoska–Ionica–Dequen'20 |
| Prior idea reports | 11 reports | ~60 mechanism lanes (memory catalogue) |

Per-record extraction (mechanism / representation / exploited structure / factor base /
relation shape / relation-generation method / compression method / linear-algebra object /
target-descent method / cost bottleneck / outcome / scoped negative boundary / next branch)
was performed by reading the P1471–P1486 main-ledger negative table and the P1509–P1513
IC-state frontier record-by-record. The **binding facts** that constrain every candidate below:

- **RT-1476 (m-ary membership gate).** For `m=5`, a complete implicit membership backend needs
  query exponent **`alpha < 3/2`** with setup `<= L^2`, random-like support, sparse full-rank
  relations. `m<=3` has no sub-rho `alpha`; `m=4` needs `alpha<1`. Sparse LA (`q^{2/5}`) and
  descent (`q^{1/5}`) are **not** binding — the membership/relation-generation stage is.
- **RT-1472 (2-large-prime enrichment gate).** Cost exponent `max(2l, 1-l, 6/5-2l)` minimized at
  `l=1/3` giving `2/3 > 1/2`; crossing rho requires pair-support **enrichment `delta > 1/4`**.
  The honest summation graph is a.a.s. subcritical (`delta=0`) in every measured deck (P1471–P1475).
- **The cubic input floor (P1510–P1513).** The source-marked resultant compiler P1510-R1 is an
  exact output-sensitive FFE primitive, but every downstream attempt to turn it into `Theta(r)`
  sub-rho rows re-materializes a **`Theta(r^3) = q^{3/5}`** object: product-circuit semijoin
  (P1511-R2, input degree `r^3`), scalar-linear Chow atomizer (P1512-R1, `Omega(r^5)` cycle
  payload forces cubic matrix dimension via `deg(det M) <= dim M`), and shared common-norm
  (P1513, both norms cubic). **The only preserved exception is a target-specialized NONLINEAR
  circuit that never materializes the `r^2` pair-resultant leaves.**

**This is the fact batch10 attacks.** RT-1476's `alpha` is exactly the question *"is there a small
arithmetic circuit for five-term membership that never materializes the `r^2` leaves?"* Every prior
report metered or barriered *specific* representations (subresultant degree, border rank, VC,
Nullstellensatz degree, communication lifting, approximate degree, entropy). **No prior report
imported the arithmetic-circuit-complexity lower-bound family** — the measure-based methods
(dimension of shifted partial derivatives, Nisan's exact noncommutative-ABP rank, geometric
complexity theory occurrence obstructions, Raz elusive functions, the depth-reduction chasm, and
the algebraic-natural-proofs meta-barrier) that lower-bound the size of **any** circuit for a
given polynomial. That family is the organizing theme of this batch and the source of its novelty.

---

## Anti-duplication guard (consumed lanes this batch must clear)

From the memory catalogue, prior reports have consumed (non-exhaustive): subresultant/eliminant
degree; cycle-matroid & graphic-matroid homology; Ritt/Lattès decomposition; isogeny/Ramanujan
walk; displacement/Toeplitz-Bézoutian; effective-resistance sparsifier; power-sum & composed
resultant; Heisenberg/theta Schrödinger–Weil; Weil–Châtelet/Lang descent; Berkovich skeleton;
holographic/matchgate + Holant; higher-order Fourier/nilsequence; orthogonal-lattice relation
finder; sum-product energy; SOS/Lasserre & Positivstellensatz; apolarity/Waring catalecticant;
Wormald 2-core DE; generalized-Jacobian modulus; syzygy/Betti resolution; **sign-rank/γ2
factorization norm**; SL2 growth/product theorem; Pila–Wilkie o-minimal; transposed
power-projection; Nash-Williams matroid union; Mahler/automatic sequences; Fourier–Mukai kernel;
arc-space/**motivic measure**; arboreal/iterated-preimage Galois; Baur–Strassen reverse mode;
HDX cosystolic expansion; **Lang–Weil / Adolphson–Sperber / zeta-monodromy** point counts;
Cohn–Umans triple product & **Strassen asymptotic spectrum / border rank**; Picard–Fuchs Gauss–Manin;
graphon cut-norm; dynamical Mordell–Lang; **Ben-Or–Tiwari/Prony sparse interp**; Guth–Katz polynomial
partitioning; Guruswami–Sudan list decoding; Schur/plethysm; ACFA difference variety; Stange
elliptic nets; Croot–Sisask; **Valiant rigidity**; Delsarte LP; **block-Hankel multipoint
sharing**; Honda formal group/Coleman; **GKZ D-module holonomic rank**; cluster mutation;
persistent homology; RKHS kernel-mean; **probabilistic polynomial**; effective Nullstellensatz
*feasibility* certificate; Ax–Katz p-adic supply; hypergraph container; matching-vector codes;
Elekes–Szabó; Newton–Okounkov; method of multiplicities; polynomial Freiman–Ruzsa; and barriers
**τ-conjecture/Shub–Smale (roots), fine-grained OV/3SUM, VC-dimension, query-to-communication
lifting, polynomial-calculus/IPS degree, approximate-degree/dual-polynomial, number-on-forehead
BNS, Shearer entropy, restriction/Kakeya, combinatorial-NSS/Alon, Ax–Katz congruence**.

**Not yet used by any prior report or barrier** (the batch10 imports): dimension of **shifted
partial derivatives** (Kayal–Saha–Saptharishi depth-4); **Nisan exact noncommutative-ABP rank**
(distinct from block-Hankel multipoint sharing — that shares an evaluation grid across a target
bank; Nisan's matrix is the *coefficient* Hankel giving intrinsic ordered ABP width); **GCT
occurrence/multiplicity obstructions** (representation-theoretic, distinct from border rank and
GKZ holonomic rank); **Raz elusive functions**; **Agrawal–Vinay/Tavenas depth-reduction chasm**;
**Barvinok/Godsil–Štefankovič polynomial interpolation** counting; **Coppersmith–Howgrave-Graham
small-roots coefficient lattice** (distinct from OLAT, which reduced the log-vector lattice);
**Brandt-matrix/Eichler-order** quaternionic Hecke; **dequantized sample-and-query** linear
algebra; **numerical homotopy/monodromy continuation**; **Moser–Tardos entropy compression**;
and the **algebraic-natural-proofs** meta-barrier (Forbes–Shpilka–Volk / Grochow–Kumar–Saks–Saraf).

Every candidate is fingerprinted against the catalogue below; any candidate whose semantic
fingerprint matched an existing lane was rejected before writing.

---

## Group A — Conservative extensions of known work

### Candidate: SHIFTED-PARTIALS-A1  `ECFG-P1586`

#### One-sentence mechanism
Exploit the *dimension of the linear span of shifted partial derivatives* `Gamma_{k,l}` of the
serial-S3 backward membership polynomial to reduce the open question in RT-1476 — the query
exponent `alpha` of any depth-4 (`SigmaPiSigmaPi`) membership backend — to an **exactly measured
complexity lower bound**, testing whether `Gamma` forces `alpha >= 3/2`.

#### Status
HYPOTHESIS (measurable exact meter; strong prior that it closes the gate).

#### Novelty classification
POSSIBLY NOVEL (arithmetic-circuit shifted-partial method absent from all 11 reports and every
prior barrier; documented search below found no ECDLP application).

#### Semantic fingerprint F(C)
- algebraic object: backward-3-sum membership polynomial `B_r(x; T)` over `F_p`, `q=Theta(r^5)`
- available public operations: coefficient access, monomial shifts, linear algebra over `F_p`
- hidden structure exploited: sparsity/monomial support of `B_r` limits `dim` of `x^{<=l}·∂^{=k}B_r`
- information discarded: exact solution values (this measures circuit size, not solutions)
- information retained: full monomial-derivative span (the complexity certificate)
- relation-generation primitive: *none directly* — this is a lower-bound meter on the backend
- compression primitive: n/a (measures whether any depth-4 compression can exist)
- rank mechanism: rank of the shifted-partial-derivative matrix `M_{k,l}(B_r)`
- descent mechanism: same backend is reused for descent, so the bound transfers to stage 7
- dominant cost exponent: the meter *outputs* the floor on `alpha`; target is the crossing `3/2`

#### Nearest ledger entries
1. **P1477-R2** (materialized serial-S3 backward state, fit `L^1.675`): measured *density* of the
   backward polynomial; A1 measures the *representation-independent depth-4 circuit floor*, which
   density alone does not certify (a dense polynomial can still have a small circuit). Distinction:
   `dim(shifted partials)` is a lower bound on circuit size; degree/density is not.
2. **P1512-R1** (scalar-linear Chow atomizer, `Omega(r^5)`): closed one *linear* representation via
   `deg(det M) <= dim M`. A1 generalizes to *all depth-4* circuits (products of linear-in-shift
   forms), a strictly larger class than determinantal/linear.
3. **P1511-R2** (product-circuit semijoin, input `r^3`): closed the *specific* product circuit; A1
   asks whether *any* `SigmaPiSigmaPi` avoids the floor, subsuming the product-circuit as one leaf.
4. **batch7 POLYCALC-D2** (Polynomial-Calculus/IPS refutation degree): bounds *refutation* proof
   size; A1 bounds *evaluation* circuit size — a different object (Nullstellensatz refutation of
   non-membership ≠ circuit for the membership state).
5. **batch4 SIGNRANK-GAMMA2-B3** (γ2 factorization-norm matrix): a *communication/matrix-norm*
   measure on a 0/1 membership matrix; A1 is an *arithmetic-circuit* measure on the polynomial.
   Distinct measures on distinct objects (matrix vs polynomial).

#### Nearest literature
- Kayal, Saha, Saptharishi, *A super-polynomial lower bound for regular arithmetic formulas*
  (STOC 2014) — shifted-partial dimension gives `n^{Omega(sqrt d)}` depth-4 lower bounds.
- Nisan, Wigderson, *Lower bounds on arithmetic circuits via partial derivatives* (1996) — the
  partial-derivative dimension measure. Gap: neither treats a Semaev/summation membership form.

#### Target family
Ordinary `E/F_p`, prime order `n`, non-CM generic `j`, `q=Theta(r^5)`, sparse subgroup domain
`x^L=1` (as in P1473/P1477). Excluded: supersingular; small embedding degree; CM `j in {0,1728}`;
anomalous `#E=p`.

#### Full algorithmic path
1. **factor-base construction:** the `2r`-point oriented subgroup deck (as P1477).
2. **relation generation:** n/a — A1 is a meter; the backend under test is the P1510 compiler.
3. **witness extraction/verification:** each measured `Gamma` value re-verified by an independent
   rank recomputation over a second prime.
4. **relation probability:** inherited from RT-1476 model (`min(1, L^5/q)`).
5. **matrix dimensions/density/rank:** `M_{k,l}` has `binom(vars+k-1,k)` rows, `binom(vars+l,l)`
   monomial-shift columns; rank computed exactly over `F_p`.
6. **factor-log calibration:** n/a (meter).
7. **individual log / descent:** the backend is reused; the `alpha` floor transfers to stage 7.
8. **offline/online separation:** meter is fully offline; it certifies the *online* backend floor.
9. **memory/parallelism:** rank of `M_{k,l}` dominates; embarrassingly parallel across `(k,l)`.

#### Cost model
The **meter** cost is `poly(r)` rank computations (offline, one-time). Its **output** is the floor
`alpha >= alpha_*(Gamma)`. Depth-4 arithmetic complexity of `B_r` is `>= Gamma_{k,l} / (top-fan-in
shift dimension)`. If `Gamma` scales as `r^{c}` with `c` such that any depth-4 backend costs
`L^{3/2+eps}`, then RT-1476's `alpha<3/2` is **impossible for depth-4**, i.e. every non-materializing
depth-4 hope is closed. Compare: rho `q^{1/2}`; the P1510 product-circuit `q^{3/5}`; the RT-1476
crossing target `q^{2/5}` at `alpha=1`.

#### Why the existing negative results do not already kill it
P1511-R2/P1512-R1 close *named* circuits (product, scalar-linear). None rules out a clever depth-4
`SigmaPiSigmaPi` that never materializes leaves. A1 is the *first representation-independent*
statement over the whole depth-4 class — the exact class the "nonlinear-circuit exception" lives in.

#### Likely fatal obstruction
The membership form may have *low* shifted-partial dimension (it is highly structured/symmetric),
in which case `Gamma` gives no super-`3/2` floor and the meter is inconclusive rather than a barrier
— a genuinely small depth-4 circuit might then exist and A1 would have *helped* rather than closed.

#### Minimal falsifying experiment
Compute `Gamma_{k,l}(B_r)` exactly for `r in {4,8,16}` (three toy sizes), seeds `s in {1,2,3}`,
over two primes (F65537, F1000003) as replication. **Positive control:** the iterated-matrix-mult
polynomial `IMM_{w,r}` (known `Gamma`-large). **Negative control:** a genuinely small-circuit dense
polynomial (e.g. `prod (x_i + c)`) with known-low `Gamma`. Fit `log Gamma / log r`.

#### Quantitative promotion gate
Promote to a barrier iff the measured `Gamma`-slope certifies a depth-4 `alpha`-floor `>= 3/2` at
`>= 2` of 3 sizes with LOO-consistent slope; **correctness alone is insufficient** — the gate is the
measured exponent crossing `3/2`. If the floor is `< 3/2`, downgrade to "depth-4 not excluded" and
promote the *constructive* search instead.

#### Proof track
Theorem to establish: `dim Gamma_{k,l}(B_r) >= r^{c}` with `c` forcing depth-4 size `L^{3/2}`, via
a monomial-support/leading-form argument on the serial-S3 recurrence `U_n=-B U_{n-1}-AC U_{n-2}`
(P1478).

#### Disproof track
Exhibit an explicit depth-4 circuit of size `L^{<3/2}` for `B_r` at some `r` (would refute the floor
and, if it also solves membership, be a genuine advance — the productive failure mode).

#### Reproduction artifact
- contract: `ecdlp_index_calculus_state/experiment_contract_p1586_shifted_partials_depth4_floor.md`
- implementation: `tasks/ecdlp_index_calculus/p1586_shifted_partial_dimension_meter.py`
- result: `p1586_shifted_partials_result.json`
- audit: `p1586_shifted_partials_audit.py`
- ledger ID: `ECFG-P1586`

---

### Candidate: NISAN-NC-RANK-A2  `ECFG-P1587`

#### One-sentence mechanism
Exploit **Nisan's exact characterization** — the width of the smallest noncommutative algebraic
branching program computing the *ordered* serial-S3 backward state equals the rank of the Nisan
coefficient-Hankel matrix `N_k` at each order cut `k` — to reduce the "non-materializing streaming
backend" question to an exact rank measurement of `N_k`.

#### Status
HYPOTHESIS (exact meter; Nisan's theorem is tight, so the measurement is a proof, not a heuristic).

#### Novelty classification
POSSIBLY NOVEL (noncommutative-ABP rank absent from all reports; explicitly distinct from batch8
block-Hankel).

#### Semantic fingerprint F(C)
- algebraic object: ordered word-series of the S3 backward transition (noncommutative in the
  transition-variable order)
- available public operations: coefficient-of-word access, matrix rank over `F_p`
- hidden structure exploited: order-`n` linear recurrence `U_n=-B U_{n-1}-AC U_{n-2}` (P1478)
- information discarded: commutative collapses (this keeps word order)
- information retained: full Hankel-of-words coefficient matrix
- relation-generation primitive: n/a (meter on the backend)
- compression primitive: measures whether a width-`w` ABP (the cheapest streaming backend) exists
- rank mechanism: `rank(N_k)` = exact minimal ABP width at cut `k`
- descent mechanism: streaming backend reused for descent
- dominant cost exponent: `alpha >= (1/ell)·log_L(max_k rank N_k)`

#### Nearest ledger entries
1. **batch8 HANKEL-BLOCK-A3** (block-Hankel multipoint sharing across the target bank): shares an
   *evaluation grid* across many targets. A2's Nisan matrix is the *coefficient* Hankel of one
   ordered series — an intrinsic ABP-width measure, not a cross-target sharing scheme. Different
   matrix, different theorem (Nisan exact characterization vs multipoint evaluation).
2. **P1478 (MX-1478)** (sparse subgroup norm recurrence `U_n`): A2 measures the *ABP width* implied
   by that recurrence, which the ledger never metered (P1478 measured resultant degree `~L^2`).
3. **P1477-R2** (dense backward polynomial, BM order ~1/3 of length): BM measures the *commutative
   linear-recurrence* order; A2 measures the *noncommutative* width — strictly finer, and the P1477
   "held-out prediction fails" note is exactly a symptom of high noncommutative rank.
4. **batch5 POWERPROJ-A1** (transposed power projection): a dual-side commutative membership meter;
   A2 is noncommutative and word-ordered.
5. **batch7 BENORTIWARI-A1** (Prony sparse interpolation, cubic-eval floor): both are "streaming
   backend" tests, but Prony recovers *sparse support* while Nisan bounds *ordered ABP width* — the
   distinction is exactly whether order matters (it does for serial-S3).

#### Nearest literature
- Nisan, *Lower bounds for non-commutative computation* (STOC 1991) — width = Hankel rank, exact.
- Gap: no application to Semaev/S3 recurrences; the sparse-recurrence structure is untested.

#### Target family
Same as A1.

#### Full algorithmic path
1–2. factor base / relation: as A1 (meter). 3. verify: recompute `rank(N_k)` over a second prime.
4. probability: RT-1476 model. 5. matrix: `N_k` has `L^{k}` × `L^{n-k}` structure, computed exactly
via the recurrence (no dense materialization). 6. calibration: n/a. 7. descent: bound transfers.
8. offline/online: fully offline meter. 9. memory: `rank(N_k)` dominates, parallel over `k`.

#### Cost model
Meter cost `poly(r)`. Output: the minimal noncommutative streaming backend costs
`Theta(L · max_k rank N_k)`. If `max_k rank N_k = Theta(L)` then any ordered backend is `Theta(L^2)`
per target, i.e. `alpha = 2 > 3/2` — closes the streaming hope. Compare rho `q^{1/2}`, RT-1476
target `q^{2/5}`.

#### Why the existing negative results do not already kill it
The ledger only measured *commutative* recurrence order (BM/P1477) and *specific* circuits. Nisan's
noncommutative rank is the exact width of the cheapest *streaming* (bounded-memory) backend — the
literal "non-materializing backward representation" RT-1476/P1477 asks for.

#### Likely fatal obstruction
If the serial-S3 order can be *symmetrized* away (the summation polynomials are symmetric!), the
noncommutative bound may not apply to the *symmetrized* backend, which is the one actually used
(FHJRV symmetrization). Then A2 bounds the wrong (unsymmetrized) object.

#### Minimal falsifying experiment
Exact `rank(N_k)` for `r in {4,8,16}`, all cuts `k`, two primes, seeds `{1,2,3}`. **Positive
control:** palindrome/word-Hankel with known-full rank. **Negative control:** a width-2 ABP series
(low rank). Fit `log(max_k rank) / log r`.

#### Quantitative promotion gate
Barrier iff `max_k rank N_k` slope `>= 1` (⇒ `alpha >= 2`) on `>=2/3` sizes, LOO-consistent. If the
*symmetrized* series has low rank, that is a **constructive lead**, not a barrier — promote it.

#### Proof track
Show `rank(N_{n/2}) = Theta(L)` from linear independence of the `U_j` recurrence coefficients.

#### Disproof track
Exhibit a low-rank cut for the symmetrized series (⇒ a genuine small streaming backend).

#### Reproduction artifact
- contract: `experiment_contract_p1587_nisan_noncommutative_rank.md`
- impl: `tasks/ecdlp_index_calculus/p1587_nisan_nc_rank_meter.py`
- result: `p1587_nisan_nc_rank_result.json`; audit: `p1587_nisan_nc_rank_audit.py`; ID `ECFG-P1587`.

---

### Candidate: BARVINOK-INTERP-A3  `ECFG-P1588`

#### One-sentence mechanism
Exploit **Barvinok/Godsil–Štefankovič polynomial interpolation** (truncated Taylor expansion of the
log-partition of the honest 2-large-prime relation graph) to compute the exact relation *supply*
exponent `delta` of RT-1472 as an analytic cluster-expansion count rather than a spectral or
point-count estimate.

#### Status
HEURISTIC (supply meter; likely `delta=0` kill but a LEDGER-NEW counting method).

#### Novelty classification
LEDGER-NEW (Barvinok interpolation absent; distinct from Lang–Weil point count and Shearer entropy).

#### Semantic fingerprint F(C)
- algebraic object: partition function `Z(z) = sum over 2-LP relation configs z^{|config|}`
- available public operations: enumerate low-order cluster coefficients of `Z`
- hidden structure exploited: cluster/Mayer expansion locality of the honest summation graph
- information discarded: individual relation identities (only the count matters)
- information retained: the truncated Taylor coefficients of `log Z`
- relation-generation primitive: n/a (supply meter for RT-1472)
- compression primitive: n/a
- rank mechanism: n/a
- descent mechanism: n/a
- dominant cost exponent: outputs `delta` directly

#### Nearest ledger entries
1. **RT-1472** (2-LP occupancy exponent `2/3`, needs `delta>1/4`): A3 is a *different estimator* of
   the same `delta` — analytic interpolation vs the direct occupancy count of P1472.
2. **batch6 LANGWEIL-SUPPLY-D2** (Deligne/Lang–Weil point count pins `delta<=1/4`): a *variety
   point-count*; A3 is a *graph partition-function* count. Different objects (algebraic variety vs
   relation hypergraph), potentially different tightness.
3. **batch8 SHEARER-D3** (Shearer entropy submodular ceiling): a *static* entropy bound; A3 is an
   *analytic* cluster expansion — the difference is convergence radius vs submodularity.
4. **batch4 CORRELATED-PEEL-A3** (Wormald DE 2-core threshold): a differential-equation peeling of
   the dependent sum-graph; A3 replaces DE with a partition-function Taylor series.
5. **batch3 ENERGY-D1** (sum-product additive-energy ceiling): energy bounds pair collisions; A3
   bounds full-configuration supply.

#### Nearest literature
- Barvinok, *Combinatorics and Complexity of Partition Functions* (2016).
- Patel, Regts, *Deterministic polynomial-time approximation algorithms for partition functions*
  (2017). Gap: neither treats a summation-polynomial relation graph.

#### Target family
Ordinary prime-order `E/F_p`, `B=n^{1/5}` large-prime bound, honest hash-frozen 2-LP graph as in
RT-1472/P1471. Excluded: planted/advice graphs (those are the disallowed `Theta(L^2)` advice case).

#### Full algorithmic path
1. factor base: `B=n^{1/5}` primes. 2. relation generation: the honest 2-LP summation graph.
3. verify: re-derive `delta` from an independent occupancy simulation. 4. probability: from `Z`.
5. matrix: the cycle-space nullity vs targets (as P1471). 6. calibration: n/a. 7. descent: n/a.
8. offline/online: offline supply audit. 9. memory: cluster-coefficient storage `poly(B)`.

#### Cost model
Meter `poly(B)`. Output `delta`. RT-1472 crosses rho iff `delta>1/4`; prior P1471–P1475 all measured
`delta<=0.02`. Compare rho `q^{1/2}`, the enrichment floor `1/4`.

#### Why the existing negative results do not already kill it
P1471–P1475 measured `delta` by *occupancy* and *character buckets*; they never applied an analytic
partition-function estimator that could reveal a *convergence-radius* enrichment invisible to
occupancy sampling. Low probability of a positive, but a distinct estimator.

#### Likely fatal obstruction
The honest graph is a.a.s. subcritical (RT-1472), so `Z` has trivial cluster expansion and `delta=0`
— A3 most likely re-confirms the subcritical kill with a new method (still a useful independent
barrier confirmation).

#### Minimal falsifying experiment
`delta` via truncated `log Z` for `B=n^{1/5}` at three `n` sizes (`~2^30, 2^36, 2^42` toy), seeds
`{1,2,3}`. **Positive control:** a planted super-critical graph (should show `delta>0`). **Negative
control:** an Erdős–Rényi graph at the same density (subcritical). **Prime-order control:** matched
random-x deck.

#### Quantitative promotion gate
Promote iff `delta>1/4` on the honest graph at `>=2/3` sizes; **any** `delta<=1/4` is a scoped
negative confirming RT-1472's subcriticality by an independent estimator.

#### Proof track
Show the honest 2-LP graph's independence polynomial has all roots outside the Barvinok disk ⇒
`delta=0`.

#### Disproof track
A planted-advice graph with `delta>1/4` and offline advice `o(L)` (would reopen RT-1472).

#### Reproduction artifact
- contract: `experiment_contract_p1588_barvinok_supply_delta.md`
- impl: `tasks/ecdlp_index_calculus/p1588_barvinok_interpolation_supply.py`
- result: `p1588_barvinok_result.json`; audit: `p1588_barvinok_audit.py`; ID `ECFG-P1588`.

---

## Group B — Genuine representation changes

### Candidate: COPPERSMITH-LATTICE-B1  `ECFG-P1589`

#### One-sentence mechanism
Exploit **Coppersmith/Howgrave-Graham coefficient-lattice small-roots** — recast five-term Semaev
membership on the sparse subgroup as "find the bounded-support root of `S5` modulo the subgroup
relation `x^L=1`" and solve it by LLL on the shift-polynomial lattice, replacing resultant/Gröbner
elimination with lattice reduction.

#### Status
HYPOTHESIS (clean representation change with a near-certain smallness kill).

#### Novelty classification
LITERATURE-ADJACENT (Coppersmith is standard; its application to Semaev membership on a subgroup is
absent; distinct from OLAT orthogonal-lattice log-finder).

#### Semantic fingerprint F(C)
- algebraic object: `S5(x1..x5)` restricted to `x_i^L=1`, sought root as a lattice vector
- available public operations: build shift-polynomial coefficient lattice, LLL
- hidden structure exploited: subgroup relation as a modulus with structured support
- information discarded: high-norm roots (Coppersmith keeps only bounded ones)
- information retained: the bounded-support root region
- relation-generation primitive: LLL-short-vector = a membership witness
- compression primitive: lattice basis (dim = number of shifts)
- rank mechanism: lattice determinant vs bound (Howgrave-Graham condition)
- descent mechanism: same lattice with target-shifted `S5`
- dominant cost exponent: LLL cost `poly(dim)`; the question is whether the bound admits sub-rho `L`

#### Nearest ledger entries
1. **batch3 OLAT-C3** (orthogonal-lattice relation finder): reduces the *log-vector* lattice to find
   relations; B1 reduces the *coefficient* lattice of *one polynomial* to find bounded roots — a
   different lattice (coefficients vs logs) and a different output (root vs relation).
2. **P1479** (no exact log lies in a `<=L^{1/2}` public linear feature space): B1 is nonlinear
   (small-root, not linear-span); the P1479 negative on linear features does not cover it.
3. **P1473/P1478** (sparse `x^L=1` subgroup membership): B1 uses the same modulus but a lattice, not
   a norm recurrence.
4. **batch4 SOS-LASSERRE-A1** (moment-SOS certificate): both are "certificate" backends, but SOS is
   a PSD-moment relaxation; B1 is an integer-lattice small-root method.
5. **RT-1476** (m=5 needs `alpha<3/2`): B1 is a candidate backend whose `alpha` = lattice dimension
   exponent.

#### Nearest literature
- Coppersmith (1996); Howgrave-Graham (1997); May, *Using LLL-reduction for solving RSA and
  factorization problems* (2010 survey). Gap: all require the unknown *small* relative to the
  modulus.

#### Target family
Ordinary prime-order `E/F_p`, sparse subgroup domain `x^L=1`. Excluded: full-range x targets (no
smallness).

#### Full algorithmic path
1. factor base: subgroup x-coordinates. 2. relation generation: LLL-short vectors of the shift
lattice. 3. verify: substitute the recovered root into `S5` and check `x_i^L=1`. 4. probability:
Howgrave-Graham bound. 5. matrix: lattice of dimension `d`, LLL. 6. calibration: n/a. 7. descent:
target-shifted `S5`. 8. offline/online: lattice built offline, LLL online per target. 9. memory:
`d^2` basis.

#### Cost model
LLL is `poly(d)`; the crossing question is whether the Howgrave-Graham bound `X < q^{1/deg}` admits
`X = L` with sub-rho `d`. Compare rho `q^{1/2}`.

#### Why the existing negative results do not already kill it
No ledger entry applied a *coefficient* lattice / small-root method to `S5`; the OLAT and P1479
negatives are about log-vectors and linear feature spaces, not polynomial small roots.

#### Likely fatal obstruction
**Smallness fails.** Subgroup x-coordinates are uniformly distributed in `F_p` (not small); the
Howgrave-Graham condition `X^{something} < det(lattice)` cannot be met with `X = Theta(q)`, so LLL
returns the zero relation or a spurious short vector. Near-certain kill — this is the honest disproof.

#### Minimal falsifying experiment
Build the shift lattice for `S5` on `x^L=1` at `r in {4,8,16}`, LLL, two primes, seeds `{1,2,3}`.
**Positive control:** a planted small-root instance (`X` genuinely small) — LLL must recover it.
**Negative control:** full-range x (LLL must fail). **Prime-order control:** matched random-x.

#### Quantitative promotion gate
Promote iff LLL recovers genuine subgroup roots with lattice dimension exponent `< 3/2` in `L` on
`>=2/3` sizes. Any failure at full x-support is the expected scoped negative.

#### Proof track
Show the Howgrave-Graham bound for `S5` on the subgroup requires `X = o(q^{1/2})`, impossible for
subgroup coords ⇒ formal no-go.

#### Disproof track
A curve/subgroup family whose x-coordinates *are* small (e.g. GLV-structured) where LLL wins — would
be a genuine (but non-generic, scope-limited) speedup.

#### Reproduction artifact
- contract: `experiment_contract_p1589_coppersmith_smallroot_membership.md`
- impl: `tasks/ecdlp_index_calculus/p1589_coppersmith_lattice_membership.py`
- result: `p1589_coppersmith_result.json`; audit: `p1589_coppersmith_audit.py`; ID `ECFG-P1589`.

---

### Candidate: GCT-OCCURRENCE-B2  `ECFG-P1590`  ★ representation winner

#### One-sentence mechanism
Exploit a **geometric-complexity-theory occurrence obstruction** — a partition `lambda` whose
irreducible-multiplicity in the coordinate ring of the *orbit closure* of the padded backward-S3
membership form differs from its multiplicity for the small iterated-matrix-multiplication
(VBP-complete) polynomial — to prove, representation-theoretically, that **no small algebraic
branching program** computes five-term membership, closing RT-1476's `alpha` for the whole ABP class.

#### Status
CONJECTURE (representation-theoretic; strongest possible barrier if an occurrence obstruction exists,
but subject to a known GCT no-go).

#### Novelty classification
POSSIBLY NOVEL (GCT occurrence/multiplicity obstructions absent from all reports; explicitly
distinct from GKZ holonomic rank and border rank).

#### Semantic fingerprint F(C)
- algebraic object: `GL`-orbit closure of the padded membership form `x_0^{d-deg}·B_r`
- available public operations: plethysm/Kronecker coefficient computation, representation theory
- hidden structure exploited: `GL`-symmetry of the summation polynomial (it is symmetric)
- information discarded: the actual solutions (this is a pure lower bound)
- information retained: the multiplicity function `lambda -> mult`
- relation-generation primitive: n/a (barrier)
- compression primitive: measures whether membership sits in the small-ABP orbit closure
- rank mechanism: irreducible multiplicities (occurrence obstruction)
- descent mechanism: transfers (same backend)
- dominant cost exponent: outputs `alpha`-floor for the ABP class

#### Nearest ledger entries
1. **batch8 GKZ-DMODULE-B2** (A-hypergeometric holonomic rank = normalized volume): a *D-module*
   invariant counting branches; GCT multiplicities are `GL`-representation numbers of an orbit
   closure — a different invariant (holonomic rank vs plethysm multiplicity).
2. **batch6 COHNUMANS-B1 / batch5 ASYMPSPEC-D1** (triple-product / asymptotic spectrum / border
   rank): tensor-rank invariants; GCT occurrence obstructions are *not* rank — they are multiplicity
   comparisons (Bürgisser–Ikenmeyer–Panova show these can differ).
3. **P1512-R1** (scalar-linear Chow atomizer, `Omega(r^5)`): B2 targets the *ABP* (VBP) class that
   strictly contains the linear atomizer.
4. **batch4 SYZYGY-REGULARITY-B2** (Betti table / free resolution): a *commutative-algebra*
   resolution invariant; GCT is a *representation-theoretic* orbit-closure invariant.
5. **RT-1476** (the `alpha` gate itself): B2 is the representation-theoretic route to closing it.

#### Nearest literature
- Mulmuley, Sohoni, *Geometric Complexity Theory I/II* (2001/2008).
- Bürgisser, Ikenmeyer, Panova, *No occurrence obstructions in geometric complexity theory*
  (JAMS 2019) — the crucial no-go: occurrence obstructions alone cannot separate VBP from VP.

#### Target family
Same as A1 (padded membership form).

#### Full algorithmic path
1–2. n/a (barrier). 3. verify: recompute multiplicities via a second plethysm algorithm.
4. probability: RT-1476 model. 5. matrix: character-table / Kronecker computations. 6. n/a.
7. descent: transfers. 8. offline. 9. memory: partition enumeration `poly` at fixed small `d`.

#### Cost model
Meter is exponential in general but tractable at toy `d` (`r in {2,3}` padded). Output: if an
occurrence obstruction exists, ABP size `> L^{3/2}` ⇒ RT-1476 closed for ABPs. Compare rho.

#### Why the existing negative results do not already kill it
No prior barrier used representation-theoretic multiplicities; border-rank (asymptotic spectrum) and
GKZ holonomic rank are provably different invariants that can miss what GCT sees.

#### Likely fatal obstruction
**Bürgisser–Ikenmeyer–Panova**: occurrence obstructions *provably do not exist* between VBP and VP.
So B2's most likely honest outcome is that the multiplicity comparison is vacuous — B2 becomes a
scoped confirmation that *this* representation-theoretic route is closed (itself a valuable negative,
matching the batch-9 discipline of importing a technology that closes a lane by name).

#### Minimal falsifying experiment
Compute low-order plethysm/Kronecker multiplicities of the padded `B_r` orbit vs `IMM` at `r in
{2,3}` (necessarily tiny — the honest limitation, `log`-ged), two independent plethysm codes.
**Positive control:** a form with a *known* occurrence obstruction (if any small example exists).
**Negative control:** `IMM` itself (multiplicities must match itself).

#### Quantitative promotion gate
Promote iff a genuine occurrence obstruction (multiplicity mismatch) is found at a computable `d` —
extremely unlikely given the no-go; the realistic gate is documenting the *vacuity* precisely (which
lane it closes). **Correctness alone is not the gate; the multiplicity mismatch is.**

#### Proof track
Find `lambda` with `mult_lambda(orbit B_r) > 0` but `mult_lambda(IMM) = 0` (occurrence obstruction).

#### Disproof track
Bürgisser–Ikenmeyer–Panova already supplies the disproof for occurrence obstructions ⇒ B2's honest
role is to test whether the *multiplicity* (not occurrence) obstruction survives, and if not, close
the GCT lane.

#### Reproduction artifact
- contract: `experiment_contract_p1590_gct_occurrence_obstruction.md`
- impl: `tasks/ecdlp_index_calculus/p1590_gct_multiplicity_meter.py`
- result: `p1590_gct_result.json`; audit: `p1590_gct_audit.py`; ID `ECFG-P1590`.

---

### Candidate: QUATERNION-BRANDT-B3  `ECFG-P1591`

#### One-sentence mechanism
Exploit **Brandt-matrix / Eichler-order** structure — route the factor base through the
endomorphism-order module and use Brandt matrices (Hecke action on the ideal class set) as the
relation generator — to test whether quaternionic Hecke arithmetic compresses the relation system.

#### Status
HEURISTIC (near-certain commutative-collapse kill for ordinary curves; flagged thin).

#### Novelty classification
LITERATURE-ADJACENT (distinct object from MODHECKE-B1 modular Hecke and isogeny-walk, but adjacent
to the CM class-group action already barriered in P1474).

#### Semantic fingerprint F(C)
- algebraic object: ideal class set of the endomorphism order `O` with Brandt/Hecke action
- available public operations: Brandt matrix construction, class-set enumeration
- hidden structure exploited: `O`-module structure of the factor base
- information discarded: non-`O`-stable relations
- information retained: the Hecke-eigenspace decomposition
- relation-generation primitive: Brandt-matrix rows as relations
- compression primitive: Hecke-eigenspace basis
- rank mechanism: rank of the Brandt/Hecke module
- descent mechanism: Hecke-orbit descent
- dominant cost exponent: class-number `h(O)` ~ `q^{1/2}` (the likely kill)

#### Nearest ledger entries
1. **P1474 (NR-1474)** (large CM known-scalar orbit does not compress the sparse deck): B3's Hecke
   action on an ordinary (imaginary-quadratic) order *is* the class-group action P1474 already
   barriered — near-certain duplication unless the *quaternionic* (supersingular) structure is used,
   which is out of scope. This is the honest reason B3 is thin.
2. **MODHECKE-B1** (modular-form Hecke, unformalized): B1 uses modular eigenforms; B3 uses Brandt
   matrices — dual under Jacquet–Langlands but a different explicit object. Distinction is real but
   both reduce to the same eigenvalue arithmetic.
3. **batch3 HEIS-B1** (theta-group Schrödinger–Weil): a Heisenberg operator, not a Hecke module.
4. **RT gates**: B3 is a candidate relation generator.
5. **PO-transfer program** (Hom-PPAV/Kummer–Cheon): B3's class-set is the CM-endpoint deck the
   transfer program already routes.

#### Nearest literature
- Eichler; Pizer, *An algorithm for computing modular forms on `Gamma_0(N)`* (Brandt matrices).
- Gap: ordinary curves have *commutative* endomorphism rings — no genuine quaternion order at an
  ordinary prime.

#### Target family
Ordinary prime-order `E/F_p` (imaginary-quadratic `O`). **This is the fatal scope point:** ordinary
⇒ commutative `O` ⇒ no true Brandt/quaternion structure.

#### Full algorithmic path
1. factor base: ideal classes of `O`. 2. relation generation: Brandt-matrix rows. 3. verify:
class-set closure. 4. probability: Hecke-orbit density. 5. matrix: Brandt matrix `h×h`. 6.
calibration: Hecke eigenvalues. 7. descent: Hecke orbit. 8. offline: class-set precompute. 9.
memory: `h^2`.

#### Cost model
Class number `h(O) ~ sqrt(|disc|) ~ q^{1/2}`, so the Brandt matrix is `q^{1/2}×q^{1/2}` — the factor
base itself is rho-sized. No sub-rho gain visible. Compare rho `q^{1/2}` directly.

#### Why the existing negative results do not already kill it
P1474 barriered the *scalar* CM orbit's non-compression; B3 asks whether the *full Hecke module*
(not a single orbit) compresses. Marginally distinct, but the class-number obstruction is the same.

#### Likely fatal obstruction
Commutativity: ordinary `O` is imaginary quadratic; "Brandt matrices" degenerate to the class-group
regular representation, whose size is `h(O) ~ q^{1/2}` — rho-sized factor base, no gain.

#### Minimal falsifying experiment
Build the class-set Hecke action for three small-`disc` ordinary curves, seeds `{1,2,3}`, measure
relation-matrix rank vs `h`. **Positive control:** a supersingular curve (genuine quaternion order —
out of scope but validates the code). **Negative control:** the same ordinary curve's plain
class-group action (P1474).

#### Quantitative promotion gate
Promote iff the Hecke module compresses the factor base to size `o(q^{1/2})` on `>=2/3` fixtures.
Near-certain failure ⇒ scoped negative confirming P1474 at module level.

#### Proof track
Show the ordinary Brandt matrix equals the class-group regular representation (size `h ~ q^{1/2}`).

#### Disproof track
An ordinary family with anomalously small `h(O)` and a compressing Hecke eigenspace.

#### Reproduction artifact
- contract: `experiment_contract_p1591_brandt_eichler_relations.md`
- impl: `tasks/ecdlp_index_calculus/p1591_brandt_matrix_relations.py`
- result: `p1591_brandt_result.json`; audit: `p1591_brandt_audit.py`; ID `ECFG-P1591`.

---

## Group C — High-risk speculative mechanisms

### Candidate: DEQUANTIZED-SAMPLING-C1  `ECFG-P1592`  ★ high-risk winner

#### One-sentence mechanism
Exploit **quantum-inspired sample-and-query dequantized linear algebra** (Tang / Chia–Gilyén–Li–
Lin–Wang) to solve the P1512 membership/atomizer linear system with cost polylogarithmic in the
matrix *dimension* — depending only on stable rank and condition number — potentially bypassing the
`Theta(r^3)` dense-solve input floor if the atomizer matrix has low stable rank.

#### Status
HYPOTHESIS (genuinely new backend class; clean stable-rank kill expected).

#### Novelty classification
POSSIBLY NOVEL (dequantized sample-and-query absent from all reports; distinct from RKHS Gram and
probabilistic-polynomial randomized backends).

#### Semantic fingerprint F(C)
- algebraic object: the P1512 atomizer / membership linear system `M x = b`
- available public operations: `ell^2`-norm sample-and-query access to `M`'s rows
- hidden structure exploited: (hoped) low stable rank / spectral decay of `M`
- information discarded: exact dense entries (replaced by importance samples)
- information retained: the top singular subspace
- relation-generation primitive: sampled low-rank projection = approximate membership solve
- compression primitive: low-rank sketch of `M`
- rank mechanism: stable rank `||M||_F^2 / ||M||^2`
- descent mechanism: same sketch reused per target
- dominant cost exponent: `poly(stable rank, kappa, 1/eps)` — independent of dimension `r`

#### Nearest ledger entries
1. **batch8 RKHS-KERNEL-C2** (kernel-mean Gram backend, killed by Peter–Weyl rank `Theta(n)`): both
   are "sketch the linear system," but RKHS uses an *exact* Gram; C1 uses *randomized sampling
   access* with a stable-rank (not full-rank) dependence — the distinction is whether spectral decay
   helps (RKHS ignored decay; C1 exploits it).
2. **batch8 PROBABILISTIC-POLY-C3** (randomized-polynomial backend): a *degree* randomization; C1 is
   a *linear-algebra* randomization (sampling access).
3. **P1512-R1** (dense solve forces `deg(det) <= dim` ⇒ cubic): C1 asks whether a *sub-dimensional*
   approximate solve dodges the exact-degree argument (it may — approximate ≠ exact).
4. **batch5 POWERPROJ-A1** (exact transposed power projection): C1 is approximate/sampled.
5. **RT-1476**: C1 is a candidate backend with `alpha` = polylog if stable rank is `O(1)`.

#### Nearest literature
- Tang, *A quantum-inspired classical algorithm for recommendation systems* (STOC 2019).
- Chia, Gilyén, Li, Lin, Wang, Woodruff (STOC 2020) — dequantized framework and its stable-rank /
  condition-number dependence. Gap: no application to a summation-polynomial system; and exactness
  requirements of ECDLP recovery vs approximate solves.

#### Target family
Same as A1.

#### Full algorithmic path
1. factor base: P1477 deck. 2. relation generation: sampled approximate membership solves. 3.
verify: **exact** re-substitution (the crucial catch — ECDLP needs exact witnesses, approximate
solves must round to exact). 4. probability: RT-1476 model. 5. matrix: sampled sketch of `M`
(dimension `r^?`, stable rank `s`). 6. calibration: from sketch. 7. descent: reuse sketch. 8.
offline: build sampling data structure. 9. memory: `O(s^2)` sketch.

#### Cost model
Dequantized solve costs `poly(s, kappa, 1/eps)`; **dimension-free**. If stable rank `s = O(1)` and
`kappa = poly(r)`, cost is `poly-log` in `r` ⇒ `alpha -> 0`. If `s = Theta(r)` (full rank, no decay)
cost is `Theta(r^2)` or worse ⇒ no gain. Compare rho `q^{1/2}`, dense solve `q^{3/5}`.

#### Why the existing negative results do not already kill it
P1512-R1's `deg(det) <= dim` argument is about the *exact* determinant; a sampled approximate solve
is not a determinant computation, so the exact-degree floor does not directly apply. RKHS was killed
by *full* Gram rank; C1 depends on *stable* rank (which can be small even when the full rank is
large, if singular values decay).

#### Likely fatal obstruction
**No spectral decay.** The P1512 atomizer is engineered to have rank `Theta(r)` with `Omega(r^5)`
cycle payload — a flat singular spectrum ⇒ stable rank `Theta(r)` ⇒ dequantized cost `Theta(r^2)`,
no gain. Plus: approximate solves may never round to the *exact* witnesses ECDLP requires (claim
discipline: approximate membership ≠ verified ECDLP recovery).

#### Minimal falsifying experiment
Measure the singular-value spectrum and stable rank of the P1512 atomizer matrix at `r in {4,8,16}`,
two primes, seeds `{1,2,3}`; run a dequantized solve and check exact-witness recovery rate.
**Positive control:** a planted low-stable-rank system (dequantized must win). **Negative control:**
a flat-spectrum random matrix (dequantized must lose). **Prime-order control:** matched deck.

#### Quantitative promotion gate
Promote iff stable rank `s = o(r)` **and** exact-witness recovery `>= 99%` on `>=2/3` sizes, giving
`alpha < 3/2`. Any flat spectrum or sub-exact recovery is the expected scoped negative.

#### Proof track
Bound the stable rank of the P1512 atomizer from its singular-value decay; if `s=O(1)`, dequantized
gives `alpha=o(1)`.

#### Disproof track
Prove the atomizer has flat spectrum (`s = Theta(r)`) ⇒ dequantized is `Theta(r^2)`, matching the
"engineered full-cycle payload" of P1512-R1.

#### Reproduction artifact
- contract: `experiment_contract_p1592_dequantized_membership_solve.md`
- impl: `tasks/ecdlp_index_calculus/p1592_dequantized_sample_query.py`
- result: `p1592_dequantized_result.json`; audit: `p1592_dequantized_audit.py`; ID `ECFG-P1592`.

---

### Candidate: HOMOTOPY-MONODROMY-C2  `ECFG-P1593`

#### One-sentence mechanism
Exploit **numerical polynomial-homotopy continuation with `ell`-adic monodromy tracking** — track
only the subgroup-fiber solutions of the Semaev system along a homotopy from a solved start system,
bounding path count by the monodromy group order — as an output-sensitive membership solver.

#### Status
HEURISTIC (high-risk; no archimedean continuation over `F_p`, likely reject-tier).

#### Novelty classification
LITERATURE-ADJACENT (homotopy continuation is standard in numerical AG; `ell`-adic/finite-field
tracking is exotic and absent from the ledger).

#### Semantic fingerprint F(C)
- algebraic object: Semaev system as a parametrized family with a homotopy parameter `t`
- available public operations: predictor–corrector path tracking, monodromy permutations
- hidden structure exploited: monodromy group acting on the solution set
- information discarded: solutions outside the subgroup fiber
- information retained: the subgroup-fiber paths
- relation-generation primitive: endpoint of a tracked path = a membership witness
- compression primitive: monodromy-orbit representatives
- rank mechanism: monodromy group order
- descent mechanism: homotopy to the target system
- dominant cost exponent: number of tracked paths ~ solution count `q^{2/5}` (likely no gain)

#### Nearest ledger entries
1. **batch4 SPEC-C2 / batch5 ARBOREAL-C1 / batch6 DML-ORBIT-C1** (transfer-operator / iterated-map
   dynamics): C2 is *path continuation*, not orbit dynamics — distinct operation, but shares the
   "F_p has no continuum" fatal issue that killed the dynamical family.
2. **batch7 ACFA-C1** (killed by Frobenius = id on `F_p`): C2 shares the finite-field pathology (no
   archimedean path).
3. **P1510-R1** (exact output-sensitive FFE compiler): C2 wants output-sensitivity by tracking only
   subgroup paths — but `ell`-adic path count = total solution count.
4. **batch2 PICARDFUCHS-B2** (Gauss–Manin constructive descent): both are "continuation," but
   Picard–Fuchs is a differential system; C2 is numerical predictor–corrector.
5. **RT-1476**: candidate backend.

#### Nearest literature
- Sommese, Wampler, *The Numerical Solution of Systems of Polynomials* (2005).
- Gap: numerical continuation is archimedean; `ell`-adic continuation lacks a convergent metric for
  tracking.

#### Target family
Same as A1.

#### Full algorithmic path
1. factor base: subgroup deck. 2. relation: tracked-path endpoints. 3. verify: exact substitution.
4. probability: fraction of paths landing in the fiber. 5. matrix: n/a (solver). 6. n/a. 7. descent:
homotopy to target. 8. offline: start-system solve. 9. memory: path storage.

#### Cost model
Number of paths = mixed volume ~ total Semaev solution count `q^{2/5}`; tracking only the subgroup
fiber requires knowing it in advance (circular). No output sensitivity ⇒ `q^{2/5}` paths, at best
matching the sparse-LA stage, not the membership stage. Compare rho `q^{1/2}`.

#### Why the existing negative results do not already kill it
No ledger entry used numerical continuation; the dynamical negatives are about *iteration*, not
*path tracking* — a distinct (if likely equally doomed) mechanism.

#### Likely fatal obstruction
Over `F_p` (or `Z_ell`) there is no archimedean path to continue along; `ell`-adic homotopy has no
convergent corrector, and the path count equals the full solution count — no output sensitivity.

#### Minimal falsifying experiment
Implement an `ell`-adic predictor–corrector for a toy Semaev system at `r in {4,8,16}`, count paths
vs subgroup solutions, seeds `{1,2,3}`. **Positive control:** an archimedean (over `C`) continuation
that recovers all solutions. **Negative control:** the `ell`-adic version (expected to fail to
track). **Prime-order control:** matched deck.

#### Quantitative promotion gate
Promote iff tracked path count is `o(q^{2/5})` (output-sensitive to the subgroup fiber) on `>=2/3`
sizes. Near-certain failure ⇒ scoped negative on numerical continuation over finite fields.

#### Proof track
Show a convergent `ell`-adic homotopy corrector exists with path count = subgroup-fiber size (would
be a genuine advance).

#### Disproof track
Show `ell`-adic corrector diverges / path count = mixed volume `q^{2/5}` regardless of fiber.

#### Reproduction artifact
- contract: `experiment_contract_p1593_ladic_homotopy_membership.md`
- impl: `tasks/ecdlp_index_calculus/p1593_homotopy_monodromy.py`
- result: `p1593_homotopy_result.json`; audit: `p1593_homotopy_audit.py`; ID `ECFG-P1593`.

---

### Candidate: MOSER-ENTROPY-COMPRESSION-C3  `ECFG-P1594`

#### One-sentence mechanism
Exploit the **Moser–Tardos entropy-compression / algorithmic-LLL** argument — model honest 2-LP
relation search as a resampling process and test whether its witness log is incompressible below
`Theta(L^2)` advice — as a *constructive* supply lower bound for RT-1472's `delta`.

#### Status
HEURISTIC (barrier-flavored supply meter; high-risk that it only re-confirms subcriticality).

#### Novelty classification
LEDGER-NEW (Moser–Tardos entropy compression absent; distinct from Shearer *static* entropy).

#### Semantic fingerprint F(C)
- algebraic object: the resampling execution log of the 2-LP relation search
- available public operations: run the search, record the resampling witness
- hidden structure exploited: locality of the LLL dependency graph
- information discarded: non-witness randomness
- information retained: the compressed witness log
- relation-generation primitive: n/a (barrier)
- compression primitive: entropy-compression coding of the witness
- rank mechanism: n/a
- descent mechanism: n/a
- dominant cost exponent: outputs `delta` via witness-log incompressibility

#### Nearest ledger entries
1. **batch8 SHEARER-D3** (Shearer submodular entropy ceiling): a *static* entropy bound on
   configuration count; C3 is the *algorithmic/constructive* Moser–Tardos compression — a different
   theorem (Kolmogorov-flavored incompressibility of an execution log).
2. **RT-1472** (needs `delta>1/4`): C3 is an alternative supply estimator.
3. **batch4 CORRELATED-PEEL-A3** (Wormald DE 2-core): C3 replaces the DE with a resampling log.
4. **A3 (this batch, BARVINOK-INTERP)**: both estimate `delta`; Barvinok is analytic, C3 is
   algorithmic-information.
5. **P1471–P1475** (occupancy / character buckets, `delta<=0.02`): C3 is a distinct estimator.

#### Nearest literature
- Moser, Tardos, *A constructive proof of the general Lovász Local Lemma* (JACM 2010).
- Gap: no application to relation-supply lower bounds in index calculus.

#### Target family
Ordinary prime-order `E/F_p`, `B=n^{1/5}`, honest 2-LP graph.

#### Full algorithmic path
1. factor base: `B` primes. 2. relation: run the resampling search, log witnesses. 3. verify:
re-run with a second seed. 4. probability: witness-log length. 5–7. n/a. 8. offline supply audit.
9. memory: log storage.

#### Cost model
If the witness log is incompressible below `Theta(L^2)`, the honest supply needs `Theta(L^2)` advice
⇒ `delta=0` (matching RT-1472). If it compresses to `o(L^2)`, `delta>0`. Compare the `1/4` floor.

#### Why the existing negative results do not already kill it
Shearer is static; the *algorithmic* incompressibility of the resampling log is a distinct
certificate that could, in principle, reveal a compressible (enriched) supply invisible to static
entropy — though most likely it re-confirms `delta=0`.

#### Likely fatal obstruction
The honest search is subcritical (RT-1472), so its resampling log is essentially incompressible ⇒
`delta=0`; C3 re-confirms the kill with a new certificate.

#### Minimal falsifying experiment
Run the 2-LP resampling search at `B=n^{1/5}` for three `n`, compress the witness log (e.g.
Lempel–Ziv proxy), seeds `{1,2,3}`. **Positive control:** a planted enriched graph (compressible
log). **Negative control:** Erdős–Rényi (incompressible). **Prime-order control:** matched deck.

#### Quantitative promotion gate
Promote iff the witness log compresses to `o(L^2)` giving `delta>1/4` on `>=2/3` sizes. Any
`delta<=1/4` is the expected scoped negative.

#### Proof track
Show the honest 2-LP resampling log has Kolmogorov complexity `Theta(L^2)` ⇒ `delta=0`.

#### Disproof track
An enriched deck with `o(L^2)`-compressible witness log and offline advice `o(L)`.

#### Reproduction artifact
- contract: `experiment_contract_p1594_moser_entropy_compression_supply.md`
- impl: `tasks/ecdlp_index_calculus/p1594_moser_tardos_supply.py`
- result: `p1594_moser_result.json`; audit: `p1594_moser_audit.py`; ID `ECFG-P1594`.

---

## Group D — Negative-theory candidates (each imports a NEW lower-bound technology)

### Candidate: ELUSIVE-FUNCTIONS-D1  `ECFG-P1595`

#### One-sentence mechanism
Import **Raz's elusive-functions** lower-bound method — treat the membership map `F^s -> F^N` as a
polynomial map and prove its image is *elusive* (not contained in any low-degree, low-dimensional
variety) — to force a super-linear arithmetic-circuit lower bound on any membership backend,
bounding RT-1476's `alpha`.

#### Status
CONJECTURE (barrier; import of an unused LB technology).

#### Novelty classification
POSSIBLY NOVEL (Raz elusive functions absent from all reports and barriers; distinct from
τ-conjecture roots, border rank, partial derivatives).

#### Semantic fingerprint F(C)
- algebraic object: the membership polynomial map `Gamma_r: F^s -> F^N`
- available public operations: dimension/degree of images under low-degree maps
- hidden structure exploited: the moment-curve-like structure of the S3 recurrence image
- information discarded: n/a (barrier)
- information retained: image-variety dimension/degree
- relation-generation primitive: n/a
- compression primitive: measures whether a small circuit's image can contain `Gamma_r`'s
- rank mechanism: image dimension vs degree (elusiveness)
- descent mechanism: transfers
- dominant cost exponent: outputs `alpha`-floor

#### Nearest ledger entries
1. **batch6 CIRCUIT-TAU-D3** (τ-conjecture/Shub–Smale root bound): bounds circuits via *real root
   count*; D1 bounds via *image elusiveness* — a different circuit-lower-bound route (Raz proved
   elusive functions ⇒ circuit lower bounds, orthogonal to the τ program).
2. **A1 (this batch, shifted partials)**: A1 is a *measure on the polynomial*; D1 is a *geometric
   property of the map's image*. Complementary, distinct.
3. **P1512-R1** (`deg(det) <= dim`): D1 generalizes the dimension argument to nonlinear maps via
   elusiveness.
4. **batch4 PILA-WILKIE-C2** (o-minimal counting): a *transcendental* counting bound; D1 is
   algebraic image dimension.
5. **RT-1476**: the gate D1 attacks.

#### Nearest literature
- Raz, *Elusive functions and lower bounds for arithmetic circuits* (STOC 2008 / ToC 2010).
- Gap: no ECDLP/Semaev instantiation; requires an explicit elusive witness.

#### Target family
Same as A1.

#### Full algorithmic path
1–2. n/a (barrier). 3. verify: recompute image dimension via a second Gröbner basis. 4. RT-1476
model. 5. Jacobian rank / image dimension computation. 6. n/a. 7. transfers. 8. offline. 9.
`poly(r)` memory at toy `r`.

#### Cost model
Meter `poly(r)`. Output: if `Gamma_r` is elusive with the Raz parameters, any circuit has size
`> L^{3/2}` ⇒ RT-1476 closed. Compare rho.

#### Why the existing negative results do not already kill it
No prior barrier used image-elusiveness; τ-conjecture (roots) and border rank are provably different
obstructions.

#### Likely fatal obstruction
Raz's method famously requires an *explicit* elusive function and only yields lower bounds *at
specific dimension/degree tradeoffs*; the membership map may fail the elusiveness threshold (its
image may be low-degree because summation polynomials are structured), giving no bound.

#### Minimal falsifying experiment
Compute image dimension and degree of `Gamma_r` at `r in {4,8,16}` (Jacobian rank + degree bound),
two primes, seeds `{1,2,3}`. **Positive control:** the moment curve (known elusive). **Negative
control:** a linear map (non-elusive). Fit against Raz's threshold.

#### Quantitative promotion gate
Barrier iff the measured (dimension, degree) crosses Raz's elusiveness threshold implying `alpha >=
3/2` on `>=2/3` sizes. Otherwise "not elusive at this scale" (inconclusive).

#### Proof track
Prove `Gamma_r` is `(s, delta)`-elusive for the Raz parameters that yield super-linear circuit size.

#### Disproof track
Exhibit a low-degree low-dimension variety containing the image (non-elusive) ⇒ possible small
circuit.

#### Reproduction artifact
- contract: `experiment_contract_p1595_elusive_function_barrier.md`
- impl: `tasks/ecdlp_index_calculus/p1595_elusive_image_meter.py`
- result: `p1595_elusive_result.json`; audit: `p1595_elusive_audit.py`; ID `ECFG-P1595`.

---

### Candidate: DEPTH-REDUCTION-CHASM-D2  `ECFG-P1596`

#### One-sentence mechanism
Import the **Agrawal–Vinay / Koiran / Tavenas depth-reduction "chasm at depth 4"** — any
polynomial-size arithmetic circuit for membership reduces to a `SigmaPiSigmaPi` of size
`2^{O(sqrt(d) log)}` — to convert A1's *depth-4* shifted-partial floor into a lower bound against
**general** (any-depth) membership circuits, closing RT-1476's `alpha` unconditionally within
arithmetic complexity.

#### Status
CONJECTURE (barrier amplifier; imports the depth-reduction theorem, unused by any prior barrier).

#### Novelty classification
POSSIBLY NOVEL (depth-reduction chasm absent from all reports; the mechanism that makes A1 bite
generally).

#### Semantic fingerprint F(C)
- algebraic object: general arithmetic circuit for `B_r`
- available public operations: depth-reduction transformation, then A1's shifted-partial measure
- hidden structure exploited: bounded degree `d = O(r)` of membership ⇒ tight chasm parameters
- information discarded: n/a (barrier)
- information retained: the depth-4 image of any small circuit
- relation-generation primitive: n/a
- compression primitive: measures general-circuit size via its depth-4 shadow
- rank mechanism: shifted-partial dimension of the depth-reduced form
- descent mechanism: transfers
- dominant cost exponent: outputs general-circuit `alpha`-floor

#### Nearest ledger entries
1. **A1 (this batch, shifted partials)**: A1 gives a *depth-4* floor; D2 supplies the *reduction*
   that promotes it to a general-circuit floor. Distinct theorems (measure vs depth reduction),
   deliberately paired (as batch8 paired PROBABILISTIC-POLY with APPROXDEG).
2. **batch6 CIRCUIT-TAU-D3** (τ-conjecture): a different general-circuit bound (roots vs
   depth-reduced measure).
3. **batch7 LIFTING-D1** (query-to-communication lifting): a communication amplifier; D2 is an
   arithmetic-depth amplifier.
4. **P1511-R2 / P1512-R1**: D2 subsumes these specific-circuit closures under a general statement.
5. **RT-1476**: the gate.

#### Nearest literature
- Agrawal, Vinay (FOCS 2008); Koiran (2012); Tavenas (2015) — depth reduction to depth 4.
- Gap: the reduction's `2^{O(sqrt d)}` overhead must be reconciled with the small `d=O(r)` regime;
  whether it yields a *useful* (super-`3/2`) floor at toy `d` is the open question.

#### Target family
Same as A1.

#### Full algorithmic path
1–2. n/a. 3. verify: cross-check the reduced-form measure vs A1 directly. 4. RT-1476 model. 5.
shifted-partial rank of the depth-reduced form. 6. n/a. 7. transfers. 8. offline. 9. `poly(r)`.

#### Cost model
The chasm overhead is `2^{O(sqrt d)}`; with `d = O(r)` this is `2^{O(sqrt r)}` — sub-polynomial in
`L=q^{ell}` for `q=Theta(r^5)`, so a depth-4 floor `L^{3/2}` survives the reduction up to
`2^{O(sqrt r)}` slack. If the slack is dominated, RT-1476 closes for general circuits. Compare rho.

#### Why the existing negative results do not already kill it
No prior barrier promoted a depth-limited bound to a general-circuit bound; this is the standard
"chasm" amplifier, never applied here.

#### Likely fatal obstruction
The `2^{O(sqrt r)}` reduction overhead may *swamp* the `L^{3/2}` depth-4 floor at the relevant
`ell`, leaving the general-circuit bound weaker than `3/2` — the reduction is famously lossy at
small degree.

#### Minimal falsifying experiment
Analytically and empirically compare the depth-4 floor (from A1) against the chasm overhead at `r in
{4,8,16}`; determine whether the net general-circuit floor exceeds `3/2`. Seeds `{1,2,3}`.
**Positive control:** a polynomial with a known general-circuit lower bound surviving the chasm.
**Negative control:** a polynomial where the chasm overhead swamps the depth-4 bound.

#### Quantitative promotion gate
Barrier iff the net general-circuit floor `>= 3/2` after subtracting chasm overhead, on `>=2/3`
sizes. Otherwise the bound is depth-4-only (A1's scope stands, D2 inconclusive).

#### Proof track
Show `L^{3/2} / 2^{O(sqrt r)} = L^{>1}` at the RT-1476-optimal `ell` ⇒ general floor `>3/2`.

#### Disproof track
Show the chasm overhead dominates ⇒ no general bound (only depth-4).

#### Reproduction artifact
- contract: `experiment_contract_p1596_depth_reduction_chasm.md`
- impl: `tasks/ecdlp_index_calculus/p1596_chasm_amplifier.py`
- result: `p1596_chasm_result.json`; audit: `p1596_chasm_audit.py`; ID `ECFG-P1596`.

---

### Candidate: ALGEBRAIC-NATURAL-PROOFS-D3  `ECFG-P1597`

#### One-sentence mechanism
Import the **algebraic-natural-proofs barrier** (Forbes–Shpilka–Volk / Grochow–Kumar–Saks–Saraf) —
if the membership polynomial is "pseudorandom" (indistinguishable from a random low-degree form by
any efficiently computable algebraic property), then *no efficiently constructible algebraic lower-
bound proof* can certify RT-1476's `alpha`-floor — exposing precisely *why* every prior algebraic
barrier (subresultant, border rank, Nullstellensatz, GKZ, this batch's A1/A2/B2/D1/D2) stalls.

#### Status
OPEN (meta-negative-theory; exposes a loophole/barrier-to-barriers).

#### Novelty classification
POSSIBLY NOVEL (algebraic natural proofs absent from all reports; a meta-barrier not previously
considered).

#### Semantic fingerprint F(C)
- algebraic object: the membership form vs a random low-degree form
- available public operations: efficiently computable (VP-natural) distinguishing properties
- hidden structure exploited: (absence of) an efficiently computable distinguisher ⇒ pseudorandomness
- information discarded: n/a
- information retained: the distinguishing-property complexity
- relation-generation primitive: n/a
- compression primitive: n/a
- rank mechanism: succinct-hitting-set / distinguisher existence
- descent mechanism: n/a
- dominant cost exponent: outputs *whether an efficient α-barrier can exist at all*

#### Nearest ledger entries
1. **All algebraic barriers to date** (subresultant, border rank, Nullstellensatz, GKZ, A1, A2, B2,
   D1, D2): D3 is the *meta*-statement about whether any of these can succeed — a genuinely new
   category (barrier-to-barriers), not another algebraic barrier.
2. **batch7 POLYCALC-D2** (IPS/Nullstellensatz degree): D3 asks whether IPS-style algebraic proofs
   are *themselves* blocked by pseudorandomness.
3. **batch5 ASYMPSPEC-D1** (asymptotic spectrum): D3 subsumes the question of whether spectrum-based
   barriers can work.
4. **RT-1476**: D3 characterizes the *provability* of the gate, not the gate value.
5. **P1512-R1's "nonlinear-circuit exception"**: D3 asks whether that exception is
   pseudorandom-hard-to-close.

#### Nearest literature
- Forbes, Shpilka, Volk, *Succinct hitting sets and barriers to proving algebraic circuit lower
  bounds* (STOC 2017).
- Grochow, Kumar, Saks, Saraf, *Towards an algebraic natural proofs barrier via polynomial identity
  testing* (2017). Gap: no instantiation for a summation-polynomial family.

#### Target family
Same as A1 (the membership form as the candidate hard polynomial).

#### Full algorithmic path
1–2. n/a (meta-barrier). 3. verify: cross-check distinguisher-complexity via a second construction.
4. RT-1476 model. 5. succinct-hitting-set / distinguisher-rank computation. 6–7. n/a. 8. offline.
9. `poly(r)`.

#### Cost model
Meter `poly(r)`. Output: if no efficiently computable property separates `B_r` from random, then any
efficient `alpha`-barrier (including A1/A2/B2/D1/D2) is *provably blocked*, and the honest research
implication is that RT-1476 must be attacked *constructively* (find a backend) rather than by
barrier. Compare: this reframes the entire IC-state program's barrier arm.

#### Why the existing negative results do not already kill it
It is a category no prior report occupies: not a barrier on the algorithm, but a barrier on the
barriers. Its value is *diagnostic* — it tells the lab whether to keep importing algebraic barriers
(this batch's A/D arm) or pivot fully to constructive backends.

#### Likely fatal obstruction
The natural-proofs barrier may be *inapplicable* if the membership form is *not* pseudorandom (it is
highly structured), in which case efficient barriers *can* work and D3's meta-warning is void — which
would be *good news* for the barrier program.

#### Minimal falsifying experiment
Test whether a small set of efficiently computable algebraic properties (partial-derivative rank,
evaluation-dimension, A1/A2 measures) distinguish `B_r` from a random low-degree form at `r in
{4,8,16}`, seeds `{1,2,3}`. **Positive control:** a form known to be distinguishable (structured).
**Negative control:** a random form (indistinguishable by construction).

#### Quantitative promotion gate
Actionable finding iff either (a) `B_r` is efficiently distinguishable ⇒ barrier program is viable
(keep A/D arm), or (b) `B_r` is pseudorandom ⇒ pivot to constructive backends. Both are decision-
relevant; there is no rho-crossing gate here (this is a meta-diagnostic, labeled as such).

#### Proof track
Either exhibit an efficient distinguisher (barrier viable) or a succinct hitting set implying
pseudorandomness (barrier blocked).

#### Disproof track
Show `B_r` has an obvious efficient distinguisher ⇒ D3 is void and barriers proceed.

#### Reproduction artifact
- contract: `experiment_contract_p1597_algebraic_natural_proofs_barrier.md`
- impl: `tasks/ecdlp_index_calculus/p1597_natural_proofs_diagnostic.py`
- result: `p1597_natural_proofs_result.json`; audit: `p1597_natural_proofs_audit.py`; ID `ECFG-P1597`.

---

## Ranking

Scores 0–5 per axis: **DIST** = distance from prior ledger mechanisms; **VER** = plausibility of an
exact verifier; **EXP** = chance of moving an exponent (not a constant); **PATH** = complete-path
coverage; **FALS** = toy-scale falsifiability; **LIT** = literature-novelty confidence; **RISK** =
risk of hidden preprocessing/memory cost (**5 = low risk**).

| Cand | DIST | VER | EXP | PATH | FALS | LIT | RISK | Notes |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| **A1 SHIFTED-PARTIALS** | 5 | 5 | 4 | 5 | 5 | 4 | 5 | exact depth-4 α-meter; closes a live gate for depth-4 |
| A2 NISAN-NC-RANK | 5 | 5 | 4 | 5 | 5 | 4 | 5 | exact ABP-width meter; symmetrization caveat |
| A3 BARVINOK-INTERP | 4 | 4 | 3 | 4 | 4 | 4 | 4 | δ supply meter; likely re-confirms subcritical |
| B1 COPPERSMITH-LATTICE | 3 | 4 | 2 | 4 | 5 | 3 | 4 | clean smallness kill |
| **B2 GCT-OCCURRENCE** | 5 | 3 | 4 | 4 | 3 | 5 | 3 | representation-theoretic; BIP no-go caveat |
| B3 QUATERNION-BRANDT | 2 | 4 | 1 | 4 | 4 | 3 | 3 | thin; commutative collapse |
| **C1 DEQUANTIZED-SAMPLING** | 5 | 3 | 4 | 4 | 4 | 5 | 2 | dimension-free if stable-rank low; flat-spectrum kill |
| C2 HOMOTOPY-MONODROMY | 3 | 2 | 2 | 4 | 3 | 3 | 2 | no F_p continuum; reject-tier |
| C3 MOSER-ENTROPY | 4 | 4 | 3 | 3 | 4 | 4 | 4 | constructive δ meter |
| **D1 ELUSIVE-FUNCTIONS** | 5 | 4 | 5 | 4 | 4 | 5 | 4 | image-elusiveness α-barrier |
| **D2 DEPTH-REDUCTION-CHASM** | 5 | 4 | 5 | 4 | 4 | 5 | 4 | promotes A1 to general circuits |
| D3 ALGEBRAIC-NATURAL-PROOFS | 5 | 3 | 3 | 4 | 4 | 5 | 4 | meta-diagnostic; no rho gate |

Rejections (semantic novelty < 3, or no complete descent path, or no rho comparison, or no precise
distinction): **B3 QUATERNION-BRANDT** (DIST 2, commutative collapse duplicates P1474 at module
level) and **C2 HOMOTOPY-MONODROMY** (VER 2 / EXP 2, no exact finite-field verifier, no output
sensitivity) are retained only as documented negative controls, not promoted.

### Selected winners

1. **Best conservative:** **SHIFTED-PARTIALS-A1** (`ECFG-P1586`). Exact, representation-independent
   depth-4 α-meter that directly addresses RT-1476's open "non-materializing backend" question — the
   first bound over the *whole* depth-4 class (the class the P1512 nonlinear-circuit exception lives
   in). Near-certain to move an exponent (close the gate for depth-4) or produce a genuine
   constructive lead.
2. **Best representation-changing:** **GCT-OCCURRENCE-B2** (`ECFG-P1590`). A representation-
   theoretic invariant (orbit-closure multiplicities) provably distinct from border rank and GKZ
   holonomic rank; either finds an occurrence obstruction (closes RT-1476 for all ABPs) or precisely
   documents the BIP no-go lane closure.
3. **Best high-risk:** **DEQUANTIZED-SAMPLING-C1** (`ECFG-P1592`). The only candidate whose backend
   is *dimension-free* and could in principle dodge the exact `deg(det) <= dim` cubic floor via
   stable rank — a genuinely new escape hatch, paired with its own flat-spectrum kill.

**Higher-EV note (per batch7–9 discipline):** the three **D barriers** (ELUSIVE-D1, CHASM-D2,
NATURAL-PROOFS-D3) are collectively higher expected value than the winners, because each imports a
lower-bound technology no prior barrier used and each threshold, if reached, **closes a live gate**
(D1/D2 → `alpha >= 3/2` ⇒ RT-1476 shut for elusive/general circuits; D3 → decides whether the
barrier program is even viable). A1 is promoted as the conservative winner because it is the *exact
measurable* core that D2 amplifies.

---

## Experiment contracts + first executable command (three winners)

### Contract — `ECFG-P1586` SHIFTED-PARTIALS-A1

- **Hypothesis:** the shifted-partial-derivative dimension `Gamma_{k,l}` of the serial-S3 backward
  membership polynomial `B_r` grows with an exponent forcing every depth-4 (`SigmaPiSigmaPi`)
  membership backend to cost `>= L^{3/2}`, i.e. RT-1476's `alpha < 3/2` is impossible for depth-4.
- **Frozen protocol:** `r in {4,8,16}`; primes `{65537, 1000003}`; seeds `{1,2,3}`; compute exact
  `rank(M_{k,l}(B_r))` over `F_p` for all `(k,l)` with `k+l <= deg B_r`; positive control `IMM_{2,r}`;
  negative control `prod_i (x_i + c_i)`; fit `log(max Gamma)/log r` with leave-one-out.
- **Promotion gate:** depth-4 α-floor `>= 3/2` at `>= 2/3` sizes, LOO-consistent slope.
- **Immutable outputs:** result JSON + SHA-256, independent audit re-ranking over the second prime.
- **First command:**
  ```bash
  python3 tasks/ecdlp_index_calculus/p1586_shifted_partial_dimension_meter.py \
    --r 4,8,16 --primes 65537,1000003 --seeds 1,2,3 \
    --controls imm,linear-product \
    --out ecdlp_index_calculus_state/results/p1586_shifted_partials_result.json
  ```

### Contract — `ECFG-P1590` GCT-OCCURRENCE-B2

- **Hypothesis:** the `GL`-orbit-closure of the padded membership form `x_0^{d-deg}B_r` admits an
  occurrence obstruction against the iterated-matrix-multiplication (VBP-complete) polynomial,
  proving no small ABP computes five-term membership.
- **Frozen protocol:** `r in {2,3}` (tractable `d`); compute low-order plethysm/Kronecker
  multiplicities of the orbit vs `IMM`; two independent plethysm implementations for cross-check;
  positive control = any known small occurrence-obstruction example; negative control = `IMM` vs
  itself (multiplicities must match). Explicitly log the `d`-range limitation.
- **Promotion gate:** a genuine multiplicity mismatch (occurrence obstruction) at a computable `d`;
  else document precisely which GCT lane the Bürgisser–Ikenmeyer–Panova no-go closes.
- **First command:**
  ```bash
  python3 tasks/ecdlp_index_calculus/p1590_gct_multiplicity_meter.py \
    --r 2,3 --max-partition-degree 8 \
    --compare imm --backends sage-plethysm,lie-plethysm \
    --out ecdlp_index_calculus_state/results/p1590_gct_result.json
  ```

### Contract — `ECFG-P1592` DEQUANTIZED-SAMPLING-C1

- **Hypothesis:** the P1512 atomizer matrix has stable rank `s = o(r)` with `poly(r)` condition
  number, so a dequantized sample-and-query solve recovers exact membership witnesses with query
  exponent `alpha < 3/2`, dodging the `deg(det) <= dim` cubic floor.
- **Frozen protocol:** `r in {4,8,16}`; primes `{65537,1000003}`; seeds `{1,2,3}`; measure the exact
  singular-value spectrum and stable rank of the atomizer; run the dequantized solve; record
  exact-witness recovery rate; positive control = planted low-stable-rank system; negative control =
  flat-spectrum random matrix; prime-order control = matched random-x deck.
- **Promotion gate:** stable rank `s = o(r)` **and** exact-witness recovery `>= 99%` at `>= 2/3`
  sizes ⇒ `alpha < 3/2`.
- **First command:**
  ```bash
  python3 tasks/ecdlp_index_calculus/p1592_dequantized_sample_query.py \
    --r 4,8,16 --primes 65537,1000003 --seeds 1,2,3 \
    --measure stable-rank,condition-number,exact-recovery \
    --controls low-stable-rank,flat-spectrum,random-x \
    --out ecdlp_index_calculus_state/results/p1592_dequantized_result.json
  ```

---

## Red-team — are the three winners disguised repetitions or cost-negative?

**A1 SHIFTED-PARTIALS-A1.** *Repetition charge:* is this just P1477-R2's "backward polynomial is
dense" restated, or batch8's block-Hankel? *Rebuttal:* P1477-R2 measured *degree/density*, which is
**not** a circuit lower bound — a dense polynomial can have a tiny circuit (e.g. `prod(x_i+c)` is
dense degree-`r` with an `O(r)` circuit). The shifted-partial dimension is a genuine *lower bound on
depth-4 size* that density cannot supply; block-Hankel (batch8) measured multipoint-evaluation
sharing across a target bank, a different matrix. *Cost-negative charge:* the meter itself is offline
`poly(r)`, so it cannot be "cost-negative" — but its **honest limitation** is that it only closes the
*depth-4* class; without D2 (chasm) it says nothing about deeper circuits, and if `Gamma` is small
(structured symmetric polynomial), it is *inconclusive*, not a barrier. **Verdict: not a repetition;
scoped to depth-4; not a crossing, an exact tightening — exactly as claimed.**

**B2 GCT-OCCURRENCE-B2.** *Repetition charge:* is this batch8's GKZ D-module or batch5/6 border-rank
under a new name? *Rebuttal:* GKZ holonomic rank = normalized volume (a `D`-module invariant);
border rank = tensor rank; GCT occurrence obstructions = `GL`-irrep multiplicities of an orbit
closure — Bürgisser–Ikenmeyer–Panova prove these are *provably different* invariants (occurrence
obstructions can vanish where the polynomials differ). *Cost-negative / dead-on-arrival charge:* the
BIP no-go says occurrence obstructions **cannot** separate VBP from VP — so B2's most likely outcome
is *vacuity*. *Rebuttal:* this is honestly disclosed; B2's promoted value is precisely to **close the
GCT-occurrence lane by name** (the batch-9 discipline: import a technology whose threshold, even
when it fails, retires a live lane) and to test the *multiplicity* (not merely occurrence)
obstruction, which BIP does not rule out. **Verdict: not a repetition; realistic role is a scoped
lane-closure, not a crossing.**

**C1 DEQUANTIZED-SAMPLING-C1.** *Repetition charge:* is this batch8's RKHS-KERNEL-C2 or
PROBABILISTIC-POLY-C3? *Rebuttal:* RKHS was killed by *full* Peter–Weyl Gram rank `Theta(n)`;
dequantized cost depends on **stable** rank `||M||_F^2/||M||^2`, which can be `O(1)` even when full
rank is `Theta(r)` if singular values decay — a genuinely different dependence. Probabilistic-poly
randomized the *degree*, not the linear-algebra access. *Cost-negative charge (the strong one):* the
P1512 atomizer was **engineered** in P1512-R1 to carry an `Omega(r^5)` cycle payload with rank
`Theta(r)` — a *flat* spectrum ⇒ stable rank `Theta(r)` ⇒ dequantized cost `Theta(r^2)`, **no gain**;
and approximate solves may never round to the *exact* witnesses ECDLP requires (approximate
membership ≠ verified recovery). *Rebuttal:* both are real risks, disclosed as the likely fatal
obstruction; C1's value is that it is the *only* winner whose backend is dimension-free and therefore
the only one not automatically bound by `deg(det) <= dim`. If the spectrum is flat (expected), C1 is a
scoped negative that **independently re-confirms the P1512 full-cycle-payload design** via a spectral
route. **Verdict: not a repetition; most likely cost-negative via flat spectrum, honestly the
highest-variance winner.**

**Overall red-team conclusion.** None of the three winners is claimed to cross rho. A1 is an exact
depth-4 tightening; B2 is a representation-theoretic lane-closure; C1 is a high-variance spectral
probe. The three **D barriers** remain higher-EV because each threshold, if reached, closes a live
gate (RT-1472 or RT-1476). **No break claimed. RT-1472 and RT-1476 remain open.** Every negative
above is scoped to the tested curves, parameters, solver, and toy budget (`r in {2..16}`,
`q=Theta(r^5)`); none is evidence that prime-field ECDLP cannot be improved.

---

## Provenance note

This report is an uncommitted file under `research/`, per the standing convention (reports live as
uncommitted files; do not commit unless the Coordinator asks). Proposed IDs `ECFG-P1586..P1597` are
reserved by this document and are not yet ledger-official; they become official only through the
Coordinator's ledger-commit + verifier path defined in `AGENTS.md`/`CLAUDE.md`. Committed main-ledger
frontier remains ~`P1486`; IC-state frontier `P1509–P1513`.
