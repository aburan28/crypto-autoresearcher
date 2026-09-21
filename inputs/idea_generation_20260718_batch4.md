# Idea Generation — ECDLP non-generic mechanisms (2026-07-18 batch4)

Research Director scheduled run. Target: a non-generic algorithm whose
*complete* cost could beat the single-target Pollard-rho baseline
`0.886*sqrt(n)` group operations on ordinary prime-field elliptic curves.
Toy correctness, a new coordinate, a relation certificate, faster
preprocessing, or a solver-only improvement is explicitly **not** a
breakthrough.

This is the sixth report. It must be mechanism-new against the ledger **and**
against reports `20260717`, `20260717_batch2`, `20260718`,
`20260718_batch2`, `20260718_batch3`. The dominant finding of the input review
(below) is that the prior five reports have **exhausted every search seed named
in the task brief** and 48 distinct mechanism lanes. This report therefore
deliberately proposes twelve mechanisms that are **absent from that catalogue**,
labels each honestly, and — where the honest label is "adjacent to a known
theorem that probably kills it" — says so.

---

## 1. Input review and machine-readable inventory

### 1.1 Sources read

- `research_ledger.md` (2,478 records; ID families **RT** ×3 live theorems,
  **P** positive/negative signals, **H** hypotheses, **MX** ×1, plus the
  `ISO-*`, `PO-*/PO96*`, `ECFG-*`, `SHA1-*`, `TRANSFER-H*` families).
- `ecdlp_index_calculus_state/research_ledger.md` (720 records; **P1071–P1513**,
  **IDEA-049…068**, **NR/ECFG-N** ×~100, **ECFG-P** ×~50, baselines,
  literature map).
- `research/non_generic_transfer_search_20260610.md` (transfer-channel sieve,
  BNIT/TCD, PO-transfer-001…006 handoffs).
- `ecdlp_index_calculus_state/research_sources/bibliography.json` (11 primary
  index-calculus sources: Semaev 2004; Gaudry 2009; FPPR 2012; Shantz–Teske
  2013; FHJRV 2014; Kousidis–Wiemers 2015; Karabina 2015; Amadori–Pintore–Sala
  2017; McGuire–Mueller 2017; Trimoska–Ionica–Dequen 2020).
- The five prior idea-generation reports (full catalogue extracted; see §1.3).

### 1.2 Ledger fingerprint inventory (families and mechanisms)

| Family | Count (approx) | Mechanism / representation | Exploited structure | Relation-generation | Compression | LA object | Descent | Bottleneck | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| `ISO-AR/SP/CW/PK`, `ISO-*-IKD/ONK` | ~70 | Ordinary ascending-isogeny + oriented-ideal Kani recovery | CM/Frobenius orientation, self-pairing, `n^2=d+Norm(a)` | none (isogeny finding) | theta/BHLS split | `(2,2)` gluing graph | — | torsion-field degree; not a DLP channel | recovery/plumbing positives; **no DLP speedup** |
| `PO-transfer-001…006`, `PO9…PO96*` | ~120 | Cover/Prym/Jacobian correspondence factor base | split genus-2, cyclic covers `z^d=h`, Hesse/Kummer, Lang torsor, augmentation-graded `k^D` | native function-field/principal-divisor rows, trace/deck projectors | large-prime, aggregate completion | incidence nullity, Hom-lattice | blind target descent | rank arrives late; matched controls reproduce signal; charged `>10^2..10^3x` rho | **scoped negatives**; scalar-linear labels closed (PO96D) |
| `P1436…P1479`, `RT-1472/1476`, `MX-1478`, `RT-1485` | ~45 | Sparse multiplicative-subgroup `x^L=1` deck + 2-large-prime graph + implicit S3/S5 membership | sparse predicate, C-finite S3 norm `K_L=A^L+C^L-U_L` | implicit membership queries; 2-LP graph edges | pair advice `Θ(L^2)` | sparse graph `~q^{1/5}`; sparse LA `L^2` | same backend | **membership query exponent `α`** and **pair enrichment `δ`** | two live conditional theorems (RT-1472, RT-1476) |
| `IDEA-049…068`, `P1490…P1513` | ~30 | Source-marked eliminant / Hasse-jet source-section compiler | two-transition endpoint algebra; Hasse order 1–2 | source-coded Hasse-jet FFE reporter | truncated marked resultant | Chow/Tate atomizer matrix | per-key output | **global compiler exponent** (`Θ(r^3)` now; want `<r^{5/2}`) | P1509 local positive; scalar-linear atomizer closed `Ω(r^5)` (P1512-R1); **nonlinear-circuit exception preserved** |
| `ECFG-P/N`, `SHA1-H*`, `ECFG-H303…309` | ~160 | Functional-graph selector / source-scheduling; SHA-1 basin allocation | graph shape features; public route stats | post-hoc feature filter | — | route-conditional stumps | — | no stable promotion | **control-only**; NR series |

### 1.3 Prior-report candidate catalogue (48 mechanisms; anti-dup)

All five reports read in full. The five reports proposed **60 candidate slots =
48 distinct mechanisms (groups A/B/C) + 15 barrier candidates (group D)** (some
repeat). The complete flat list and the mechanism-lane grouping are archived in
the running memory index; the **consumed lanes** that this report must NOT
re-propose are:

- **Fast membership backend (RT-1476 `α`):** polyhedral/BKK homotopy
  (POLY-A1), tensor-train/separator-rank of the S2|S3 operator (TT-B2),
  border-rank of `T_{S_m}` (BORDER-B4), Prony/Ben-Or–Tiwari sparse
  interpolation (SPARSE-A1), subresultant-PRS early-abort (RT-1476-SUBRES-A1),
  Kedlaya–Umans batched multipoint eval (KU-BATCH-A3), displacement/Toeplitz-
  Bézoutian GKO solve (DISP-A1), composed-resultant power-sum on the C-finite
  oracle (PWRSUM-A3), Guruswami–Sudan list-decode (LDEC-A3), polynomial-
  partitioning incidence reporting (INC-A3), holographic/matchgate counting
  (HOLANT-C1).
- **Large-prime graph enrichment (RT-1472 `δ`):** 3-uniform simplicial `H_1`
  homology (KLP-HOM-A1), graphic-matroid Horton cycle basis (RT-1472-CYCLEMAT-
  A2), effective-resistance spectral sparsifier (EFFRES-A2), NFS-style two-
  sided coincidence (NFS2S-A2).
- **Char-0 / p-adic lift:** global MW height-lattice xedni (XEDNI-C3), tropical/
  `Q_p` valuation lift of the Semaev variety (TROP-B3), Serre–Tate canonical-
  lift formal-group log (STATE-B2/CANLIFT-B1), Cartier–Manin/p-curvature
  cohomology descent (COHO-B2/PCURV-C2), Coleman–Gross p-adic height lattice
  (PADICHT-C3), Berkovich skeleton (SKEL-B3).
- **Representation change:** nilpotent Hasse-jet dual-number filter (JET-B1),
  Kani `(N,N)` RM genus-2 glue (KANI-RM-B1), level-≥3 theta bilinear membership
  (THETA-BILIN-B3), Heisenberg/Schrödinger–Weil metaplectic shift (HEIS-B1),
  modular/Hecke `X_0(N)` factor base (MODHECKE-B1), Drinfeld-module transport
  (DRINFELD-B2), Weil–Châtelet `m`-torsor (WCDESC-B2), group-dual DFT indicator
  (DFT-B3), Gowers/nilsequence predictor (NILSEQ-C2), orthogonal-lattice
  Nguyen–Stern (OLAT-C3).
- **Isogeny/CM/dynamics:** `Cl(O)`-correspondence quiver composition (QUIV-C1),
  Lattès transfer-operator spectrum (SPEC-C2), Ritt/Dickson functional
  decomposition (RITT-B3), non-backtracking Ramanujan isogeny walk (ISOWALK-C1),
  CM ideal-factorization IC (CMIDEAL-C3).
- **Additive/analytic:** elliptic-net/EDS smoothness (EDS-A2), Sidon/`B_h`
  base (SIDON-A2), small-doubling/Bogolyubov–Ruzsa stability (STAB-C1),
  character-sum decomposition-count bias + Kloosterman sampling (CHARBIAS-C3,
  KLOOS-C2), representation-technique subset-sum MITM (REPMITM-C1), Pink–Zilber
  anomalous subvariety (ZILBERPINK-C2), many-target amortization (AMORT-A3).

**All six task-brief search seeds are consumed:** Hasse-jet/dual-number
(JET-B1 + ledger P1509), tropical/Newton-polytope (POLY-A1, TROP-B3), output-
sensitive incidence (INC-A3), arithmetic-dynamical transfer operator (SPEC-C2,
RITT-B3, ISOWALK-C1), noncommutative correspondence/path algebra (QUIV-C1),
tensor-network/separator-rank (TT-B2, BORDER-B4). This report goes **outside the
seed set entirely.**

### 1.4 The only two live rho-crossing surfaces (binding constraints)

Confirmed verbatim from `research_ledger.md`:

- **RT-1472** — explicit hash-like 2-large-prime graph at `B=n^{1/5}`. Cost
  exponent `max(2ℓ, 1−ℓ, 1+1/5−2ℓ)`, minimized at `ℓ=1/3` → `2/3`. Crossing
  rho needs pair-support **enrichment `δ>1/4`**; without it an implicit deck
  needs setup `o(L)` and query `o(sqrt(L))`. Prior measurement: honest
  summation graph is a.a.s. subcritical (`δ≈0`).
- **RT-1476** — five-term implicit membership backend. With `L=q^ℓ`, support
  probability `min(1, L^m/q)`, query `L^α`, `Θ(L)` rows, sparse LA `L^2`:
  optimum total exponent `2/(m+1−α)` for `α≤1`, else `(1+α)/m`. **`m≤3` has no
  sub-rho `α`; `m=4` needs `α<1`; `m=5` needs `α<3/2`.**
- **IDEA-068 compiler** (IC-state frontier): P1509 gives an exact local Hasse-
  jet source section (all 900 non-return endpoints have Hasse order 1–2); the
  global source-blind marked-resultant compiler (P1510) is `Θ(r^3)`, target
  `<r^{5/2}` for `q=Θ(r^5)`. **P1512-R1 closed the scalar-linear Chow/Tate
  atomizer at `Ω(r^5)`; only a target-specialized _nonlinear_ circuit survives.**

Every ledger "below rho" is amortized-many-target or setup-uncharged. No
single-target complete-cost speedup exists anywhere in either ledger.

---

## 2. Novelty method

For each candidate `C` the semantic fingerprint
`F(C) = (object, public ops, hidden structure, info discarded, info retained,
relation-gen primitive, compression primitive, rank mechanism, descent
mechanism, dominant cost exponent)` is compared against the §1.3 catalogue and
the §1.2 ledger families. A candidate is a duplicate if an existing entry shares
the essential fingerprint even under renaming. External primary-source searches
were run for the four load-bearing new lanes (SOS/Lasserre for Semaev;
generalized Jacobians for DLP; `γ2`/sign-rank membership; slice-rank three-term
relations); results are cited per candidate.

Claim tiers: `CONJECTURE | HYPOTHESIS | HEURISTIC | OPEN`. Novelty:
`LEDGER-NEW | LITERATURE-ADJACENT | NOVELTY-UNVERIFIED | POSSIBLY NOVEL`.

---

## GROUP A — Conservative extensions (attack a live gate with a genuinely new operation)

## Candidate: SOS-LASSERRE-A1

### One-sentence mechanism
Exploit the moment/sum-of-squares (Lasserre) semidefinite hierarchy to certify
five-point Semaev membership `S`, reducing the membership-query cost `C` of the
`m=5` decomposition subproblem `P` below the Gröbner/border-rank baseline `B` at
which every prior backend saturated.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (documented empty literature search: no work connects SOS/Lasserre
to Semaev/ECDLP; the general SOS-for-polynomial-systems machinery is standard).

### Semantic fingerprint
`F` = (moment matrix / SOS cone over the `S5` ideal; public field ops + SDP
solve; the successful-membership subvariety geometry; the dense monomial basis;
the low-degree SOS certificate if one exists; relation-gen = SDP feasibility
witness; compression = rank of the moment matrix truncation; rank = SDP
pseudo-moment matrix; descent = same SDP with target substituted; dominant
exponent = SOS degree `d_SOS` in `L`).

### Nearest ledger entries
1. **RT-1476** — same target gate (`α<3/2` at `m=5`); distinct because SOS is a
   convex certificate, not an eliminant. 2. **RT-1476-SUBRES-A1** — subresultant
   degree; SOS degree is a different, potentially smaller, complexity measure.
   3. **BORDER-B4 / TT-B2** — bound the multiplicative/tensor rank; the stated
   barrier `SPARSEBND-D3` ("`Ψ_R` basis-invariant dense, `T_{S_m}` near-maximal
   border rank") **does not bound SOS degree** — a dense system can have a
   low-degree SOS certificate. 4. **IDEA-058** (quadratic-phase decomposition) —
   a specific algebraic factorization, not a convex relaxation. 5. **MX-1478** —
   C-finite S3 norm; SOS would act on the assembled `S5`, not the recurrence.
   Exact distinction: SOS/Lasserre is the first proposed backend whose cost is
   governed by Positivstellensatz degree rather than elimination/rank degree.

### Nearest literature
Lasserre (2001) moment-SOS hierarchy; Laurent (2009) survey; Amadori–Pintore–Sala
(2017) prime-field Semaev baseline; Kousidis–Wiemers (2015) first-fall degree.
Claim: SOS refutation/extraction degree can be strictly below the Gröbner
solving degree for structured systems. Assumption: the `S5` system's SOS degree
scales sub-`(3/2)·log_L`. Gap: no Semaev SOS-degree measurement exists.

### Target family
Ordinary `E/F_p`, `#E` prime, `j∉{0,1728}`, non-anomalous, embedding degree
large; sparse subgroup deck `x^L=1` as in P1473 (`L=q^{1/5}`). Excluded:
supersingular, CM-tiny-discriminant, anomalous.

### Full algorithmic path
1. **Factor base:** sparse `x^L=1` deck, size `L=q^{1/5}` (reuse P1473 fixtures).
2. **Relation generation:** for a random point `R`, form the `S5(x1..x5,x(R))`
   membership ideal restricted to the deck; solve the degree-`d` Lasserre SDP;
   a rank-drop / flat-extension certificate yields the decomposition witness.
3. **Witness extraction/verification:** extract points from the flat moment
   matrix (Henrion–Lasserre extraction); re-verify `P1+..+P5=R` on the curve.
4. **Relation probability:** `min(1, L^5/q)=Θ(1)` at `L=q^{1/5}`.
5. **Matrix:** `Θ(L)` rows, `Θ(L)` columns, sparse; nullity ≥1 target.
6. **Factor-log calibration:** standard sparse-LA over `Z/n`.
7. **Descent:** substitute the public target `Q` for `R`; same SDP.
8. **Offline/online:** SDP structure (monomial basis, constraint matrices) is
   target-independent → precompute; only the localizing vector is online.
9. **Memory/parallelism:** moment matrix `O(L^{2d})`; SDP columns independent.

### Cost model
Per-query SDP: interior-point cost `~ (moment-matrix size)^{3.5} = L^{7d}`
naively, but with the chordal/structured-sparsity exploitation `~ L^{c·d}` for
small `c`. Membership query exponent `α = c·d_SOS`. Setup `L^2`; failed
attempts `Θ(1)` at `L=q^{1/5}`; sparse LA `L^2`; descent same backend. Total
`2/(6−α)` (m=5). **Crosses rho iff `α<3/2`, i.e. `c·d_SOS<3/2`.** Compare: rho
`n^{1/2}`; BSGS `n^{1/2}`; Amadori–Pintore–Sala Gröbner `>rho`.

### Why existing negatives do not kill it
`SPARSEBND-D3` and the border-rank/separator-rank barriers are statements about
sparsity and multiplicative rank of the eliminant/tensor — SOS degree is
neither. The IDEA-058 quadratic-phase negative was about a specific
factorization, not a convex certificate. No prior candidate measured SOS degree.

### Likely fatal obstruction
SOS lower bounds (Grigoriev; Barak–Steurer pseudo-calibration) commonly force
`d_SOS=Ω(L)` for random-like algebraic systems, giving `α=Θ(L)` — far above
`3/2`. If the Semaev `S5` behaves pseudo-random for SOS, the candidate dies (this
is candidate SOS-LB-D1).

### Minimal falsifying experiment
Toy sizes `L∈{8,16,32}` (three), seeds `{20260718..20260722}`, on ordinary
prime-order deck fixtures; positive control = a planted decomposable target
(must certify at low `d`); negative control = a random non-decomposable target
(must stay infeasible). Measure `d_SOS` and the SDP wall time; fit `d_SOS(L)`.

### Quantitative promotion gate
Measured `c·d_SOS < 1.5` with a monotone or flat trend across the three `L`
(equivalently, membership-query exponent `α<3/2` extrapolated), AND exact
extraction verified on ≥95% of planted controls. Correctness alone fails the
gate; the exponent must trend below `3/2`.

### Proof track
Theorem to establish: the truncated `S5`-membership ideal admits a degree-`d`
SOS/Positivstellensatz certificate with `d=O(1)` (independent of `L`), via a
flat-extension argument on the deck's finite variety.

### Disproof track
An SOS lower bound `d_SOS=Ω(L^{ε})` for the `S5` system (pseudo-calibration over
the random target distribution), or a measured super-`3/2` `α` trend.

### Reproduction artifact
Contract `experiment_contract_sos_lasserre_s5_membership.md`; implementation
`sos_lasserre_s5.sage` (Sage + a Python SDP interface, e.g. an interior-point
moment solver); result `sos_lasserre_s5_result.json`; audit
`sos_lasserre_s5_audit.py`; ledger `P1514`.

---

## Candidate: APOLARITY-ATOMIZER-A2

### One-sentence mechanism
Exploit the apolarity / catalecticant (Waring) decomposition of the two-
transition marked resultant to realize the *target-specialized nonlinear
circuit* that P1512-R1 preserved, reducing the IDEA-068 global compiler cost `C`
of the source-blind endpoint-polynomial subproblem below the scalar-linear
`Ω(r^5)` Chow barrier `B`.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW (the nonlinear-circuit exception is explicitly open in P1512-R1/P1513);
LITERATURE-ADJACENT (apolarity/catalecticant symmetric-tensor decomposition is
classical — Iarrobino–Kanev; Landsberg–Ottaviani).

### Semantic fingerprint
`F` = (marked resultant of the two-transition S3 pair as a symmetric tensor;
public field ops; the Hasse-order-1/2 source-section structure P1509 exposes;
the dense scalar-linear coefficient layout; the low Waring/border-Waring rank if
one exists; relation-gen = per-target eliminant evaluation via a bilinear/
quadratic-gate circuit; compression = apolar ideal / catalecticant kernel; rank
= catalecticant matrix rank; descent = per-key output specialization; dominant
exponent = compiler cost in `r`).

### Nearest ledger entries
1. **P1512-R1** — closed the *scalar-linear* atomizer at `Ω(r^5)`, explicitly
   preserving the nonlinear exception this candidate builds. 2. **P1510** — the
   `Θ(r^3)` global compiler this would replace. 3. **BORDER-B4** — border rank of
   `T_{S_m}` (batched membership tensor); distinct object (that is the summation
   tensor; this is the marked-resultant compiler) and distinct tool (Bini
   bilinear vs. symmetric apolarity/catalecticant). 4. **PWRSUM-A3** — power-sum
   composed resultant; a linear-algebra-of-Newton-sums route, not a Waring
   decomposition. 5. **P1509** — the Hasse-jet local section this consumes as
   input. Exact distinction: apolarity targets the *symmetric* structure of the
   resultant polynomial (its Waring rank), a complexity axis no prior compiler
   candidate used.

### Nearest literature
Iarrobino–Kanev (1999) catalecticants; Landsberg (2012) tensor complexity;
Bostan–Flajolet–Salvy–Schost (2006) fast resultants. Claim: symmetric tensors of
bounded Waring/border-Waring rank admit evaluation circuits far below their
dense size. Gap: the marked-resultant's Waring rank is unmeasured.

### Target family
As IDEA-068: two-transition endpoint algebra on ordinary prime-order deck
fixtures, `q=Θ(r^5)`. Excluded: return-endpoints of Hasse order `≥3` (P1509
shows these do not occur on the tested fixtures — must re-check at scale).

### Full algorithmic path
1. **Factor base:** P1490 two-transition endpoints (reuse).
2. **Relation generation:** build the source-marked resultant as a symmetric
   tensor `T_r`; compute its apolar ideal / catalecticant rank; if `rank=r^{o(1)}`
   assemble the Waring evaluation circuit.
3. **Witness/verify:** the circuit outputs the source-blind endpoint polynomial;
   independent replay of P1509 Hasse-section roots.
4. **Probability:** deterministic per target (compiler, not sampler).
5. **Matrix:** the catalecticant is `~r×r`; sparse LA `r^2`.
6. **Calibration:** as IDEA-068.
7. **Descent:** per-key specialization of the circuit.
8. **Offline/online:** the Waring decomposition is target-independent (offline);
   only specialization is online.
9. **Memory/parallelism:** `O(r^2)` state; circuit gates parallel.

### Cost model
If Waring/border-Waring rank of `T_r` is `w(r)`, the compiler evaluates in
`w(r)·polylog` per target and `w(r)·r` for `Θ(r)` targets. Crosses the barrier
iff total `< r^{5/2}`, i.e. `w(r)=o(r^{3/2})`. Setup = one Waring decomposition
`~r^3` (amortized). Compare: current P1510 `Θ(r^3)`; scalar-linear closed
`Ω(r^5)`.

### Why existing negatives do not kill it
P1512-R1 is a lower bound **only for scalar-linear** atomizers; it is not a lower
bound against nonlinear (bilinear/quadratic-gate) circuits, which it names as the
open exception. Waring evaluation is exactly such a nonlinear circuit.

### Likely fatal obstruction
Generic symmetric tensors have near-maximal Waring rank (`w(r)=Θ(r^{?})` close to
the Alexander–Hirschowitz bound); if `T_r` is Waring-generic, `w=Ω(r^{3/2})` and
the barrier holds nonlinearly too (candidate LINLABEL-UNIFIED-D3 formalizes this).

### Minimal falsifying experiment
`r∈{8,12,16}` (three), seeds `{20260718..}`, ordinary prime-order fixtures;
positive control = a synthetically low-Waring-rank marked resultant (must
compile fast); negative control = a Waring-generic tensor of the same shape.
Measure `w(r)` via catalecticant ranks.

### Quantitative promotion gate
`w(r)=o(r^{3/2})` (fit exponent `<1.5`) across the three `r`, with exact
compiler output matching P1509 Hasse roots on ≥95% of endpoints.

### Proof track
Theorem: the two-transition marked resultant has border-Waring rank `O(r·polylog)`
by exhibiting an explicit apolar scheme of that length.

### Disproof track
Catalecticant rank `Ω(r^{3/2})` (a Waring lower bound), which promotes P1512-R1
to a *nonlinear* barrier (feeds D3).

### Reproduction artifact
Contract `experiment_contract_apolarity_atomizer.md`; impl
`apolarity_atomizer.sage`; result JSON; audit `apolarity_atomizer_audit.py`;
ledger `P1515`.

---

## Candidate: CORRELATED-PEEL-A3

### One-sentence mechanism
Exploit the differential-equation-method (Wormald) 2-core emergence threshold of
the *dependent* summation graph — whose edges `x_i+x_j` are correlated through
shared endpoints — to test whether the honest 2-large-prime graph supplies
pair-support enrichment `δ>1/4` (the RT-1472 gate) with **no** stored advice.

### Status
HYPOTHESIS

### Novelty classification
NOVELTY-UNVERIFIED (random-graph peeling thresholds are standard; their
application to the correlated Semaev sum-graph is unrecorded and the RT-1472
lane used only static algebraic invariants).

### Semantic fingerprint
`F` = (the 2-LP summation multigraph with dependent edges; public sum/collision
ops; the correlation structure of shared endpoints; the exact edge multiplicities;
the emergent 2-core; relation-gen = cycles in the 2-core; compression = the core
is `o(L^2)`; rank = cycle-space dimension of the core; descent = target edge into
the core; dominant exponent = `δ` from the core-size scaling).

### Nearest ledger entries
1. **RT-1472** — the gate; prior work took the graph as an i.i.d. random graph
   (subcritical, `δ≈0`). 2. **RT-1472-CYCLEMAT-A2** — static min-cycle basis;
   this is a dynamic peeling *process* threshold. 3. **EFFRES-A2** — Laplacian
   spectrum (static); distinct. 4. **KLP-HOM-A1** — simplicial homology (static
   topology). 5. **NR-1471** — measured coordinate vs hash deck edges/rank; this
   proposes the correlated-random-graph model those measurements lacked. Exact
   distinction: the operation is Wormald DE-method analysis of a peeling Markov
   process on a graph with *dependent* edges, not any static algebraic invariant.

### Nearest literature
Wormald (1995) DE method; Molloy (2005) cores of random hypergraphs; Aronson–
Frieze–Pittel Karp–Sipser matching. Claim: correlated random graphs can have
core thresholds shifted from the i.i.d. value. Gap: the Semaev sum-graph's exact
degree/correlation law is not in the random-graph literature.

### Target family
Ordinary prime-order `E/F_p`; factor base `B=n^{1/5}`; 2-LP window `L`. Excluded:
structured/advice-bearing bases (those are the disallowed-preprocessing regime).

### Full algorithmic path
1. **Factor base:** `B=n^{1/5}` factor primes + `L` large-prime slots.
2. **Relation generation:** collect honest pair relations; build the large-prime
   multigraph; run peeling to the 2-core.
3. **Witness/verify:** each core cycle → a full relation; re-verify on curve.
4. **Probability:** governed by the pair-support law `Θ(L^2)`.
5. **Matrix:** cycle-space of the 2-core; rank = its dimension.
6. **Calibration:** sparse LA `L^2`.
7. **Descent:** insert the target as an edge; find its core cycle.
8. **Offline/online:** graph construction offline; target cycle online.
9. **Memory/parallelism:** store only the 2-core (`o(L^2)` if `δ>0`).

### Cost model
Enrichment `δ` = exponent of the surviving core size `L^{1+δ}` above the naive
`L`. RT-1472: crosses rho iff `δ>1/4`. Setup `L^2`; peeling linear in edges;
sparse LA `L^2`. Total exponent `max(2ℓ,1−ℓ,1+1/5−2ℓ)` refined by the measured
`δ`.

### Why existing negatives do not kill it
The a.a.s.-subcritical claim was made for the i.i.d. model; the dependent-edge
peeling threshold has not been computed. If correlation lifts the core threshold,
`δ>0` arises without advice.

### Likely fatal obstruction
The dependence is likely *anti*-concentrating (shared endpoints reduce, not
raise, core density), so the corrected threshold gives `δ=0` — confirming the
subcritical barrier (this is candidate SLICE-RANK-1-D2's neighbor).

### Minimal falsifying experiment
`L∈{2^10,2^12,2^14}` (three), seeds `{20260718..}`, ordinary prime-order
fixtures; positive control = an i.i.d. graph at matched density (known
threshold); negative control = the honest correlated graph. Measure 2-core size
vs `L`; fit `δ`.

### Quantitative promotion gate
Fitted `δ>1/4` on the honest correlated graph across the three `L`, with the
i.i.d. control reproducing its textbook threshold (sanity).

### Proof track
Theorem: the Semaev 2-LP sum-graph's peeling process has core-emergence density
`c*<` (or `>`) the i.i.d. value, via a Wormald ODE for the residual degree
sequence.

### Disproof track
The ODE fixed point gives an empty 2-core (`δ=0`) a.a.s., closing RT-1472's
no-advice branch.

### Reproduction artifact
Contract `experiment_contract_correlated_peel_2core.md`; impl
`correlated_peel_2core.sage`; result JSON; audit; ledger `P1516`.

---

## GROUP B — Genuine representation changes

## Candidate: GENJAC-MODULUS-B1

### One-sentence mechanism
Exploit a **non-split** generalized Jacobian `J_m` of `E` with a chosen modulus
`m` (a semiabelian extension `0→T→J_m→E→0` by a torus `T`) so that the extension
cocycle couples `T`-smoothness to the `E`-target, exposing a relation channel `C`
for the original subplem `P` that the split reduction (Déchène) misses.

### Status
OPEN

### Novelty classification
LITERATURE-ADJACENT (Déchène 2006 studied `J_m` DLP and proved the security
reduces to the `E`- and `T`-components when the sequence effectively splits;
the *non-split coupling as an index-calculus channel* is not treated).

### Semantic fingerprint
`F` = (generalized Jacobian `J_m`, a semiabelian group; public `J_m` arithmetic
via functions with prescribed behaviour along `m`; the extension class in
`Ext^1(E,T)=` the modulus data; the discarded torus coordinate in the split
case; the retained cocycle in the non-split case; relation-gen = smooth
factorizations of `T`-parts of divisors supported on `m`; compression = the
torus DLP is easy (`G_m`); rank = coupled `(E,T)` relation matrix; descent =
push the target through the cocycle; dominant exponent = torus-relation yield).

### Nearest ledger entries
1. **WCDESC-B2** — Weil–Châtelet torsor (`H^1`), collapses by Lang; `J_m` is a
   *group extension*, not a torsor, and does not vanish. 2. **SKEL-B3** —
   Berkovich skeleton; distinct (archimedean-analytic vs algebraic semiabelian).
   3. **PO-transfer** cover/Prym family — abelian-variety covers, not semiabelian
   extensions by a torus. 4. **TRANSFER-H004** — non-homomorphic cyclic-cover
   label; `J_m` is homomorphic but semiabelian. 5. **CMIDEAL-C3** — `End(E)`
   ideals; unrelated. Exact distinction: the semiabelian torus direction with a
   nontrivial extension cocycle is a group object absent from both ledgers.

### Nearest literature
Serre *Groupes algébriques et corps de classes*; Déchène (2006) "Arithmetic of
Generalized Jacobians" (eprint 2006/033) and "Discrete Logarithms in Generalized
Jacobians"; Déchène "Security of Generalized Jacobian Cryptosystems." Claim: the
`J_m` DLP reduces to `E` and `G_m` DLPs. **This is the central obstruction, not a
help** — the reduction says `J_m` is *at most as hard* as `E`, never easier,
*when the components decouple*. The untreated gap: a modulus whose extension does
not decouple and whose torus factor is over an extension field with smoother
order.

### Target family
Ordinary `E/F_p`, `#E` prime; modulus `m = ` a degree-`d` effective divisor
whose support field `F_{p^d}` gives `T=Res(G_m)` with smooth order
`p^d−1`-cofactor. Excluded: split moduli (Déchène-easy either way), trivial `m`.

### Full algorithmic path
1. **Factor base:** `E`-points (small height) × `T`-smooth torus elements.
2. **Relation generation:** functions with divisor supported on `m` give
   `J_m`-relations coupling an `E`-relation to a `T`-cofactor; factor the `T`-part
   over the smooth torus base.
3. **Witness/verify:** reconstruct the `J_m`-principal divisor; check both the
   `E` push-forward and the `T` component.
4. **Probability:** `T`-smoothness probability over `F_{p^d}` (subexponential-
   friendly) times the `E`-incidence.
5. **Matrix:** block `[E | cocycle | T]`; the target enters the `E`-block, the
   cocycle couples it to the easy `T`-block.
6. **Calibration:** solve the `T`-block first (easy), back-substitute via cocycle.
7. **Descent:** lift `Q` to `J_m`, factor its `T`-shadow.
8. **Offline/online:** torus factor base offline; target lift online.
9. **Memory/parallelism:** `T`-factor base standard subexponential size.

### Cost model
If the cocycle transfers `Θ(log)` bits of the `E`-target per `T`-relation, and
`T`-relations cost `L_{p^d}` (torus subexponential), the coupled solve costs
`~ (E-relations)·(torus-relation cost)`. Crosses rho only if the coupling yields
`ω(1)` independent `E`-constraints per unit torus work — the make-or-break
quantity. Compare rho `sqrt(n)`; Déchène split baseline `= E`-cost.

### Why existing negatives do not kill it
Déchène's reduction is proved for the *split/decoupled* case. Lang's theorem
kills torsors (`H^1=0`), not group extensions (`Ext^1≠0`). The non-split coupling
is untested.

### Likely fatal obstruction
The extension `0→T→J_m→E→0` over a *finite* field is very often split (`Ext^1`
frequently trivial for the relevant `T`), and even when non-split the induced map
on relations is `F_p`-linear in the target → bounded rank (this is exactly
LINLABEL-UNIFIED-D3). Then it collapses to Déchène-easy = no gain.

### Minimal falsifying experiment
Toy primes `p∈{101,211,431}` (three), `d=2`, seeds `{20260718..}`; positive
control = a curve with an intentionally non-split `m` and smooth `p^2−1`;
negative control = a split `m`. Measure independent `E`-constraints extracted per
torus relation; compare to the split baseline and to rho.

### Quantitative promotion gate
The coupled channel yields marginal `E`-rank growing faster than the direct
`E`-factor base at matched cost, extrapolating to online exponent `<1/2` — not
merely `≤ E`-cost.

### Proof track
Theorem: for a non-split `J_m`, the cocycle map on relation classes is *not*
`F_p`-linear in the target coordinate, hence can exceed the PO96D scalar-linear
rank bound.

### Disproof track
`Ext^1(E,T)=0` for the admissible moduli, or the cocycle map is `F_p`-linear
(then D3 applies and the lane closes).

### Reproduction artifact
Contract `experiment_contract_genjac_nonsplit_modulus.md`; impl
`genjac_modulus_channel.sage`; result JSON; audit; ledger `P1517`.

---

## Candidate: SYZYGY-REGULARITY-B2

### One-sentence mechanism
Exploit the **minimal free resolution** (graded Betti table / Castelnuovo–Mumford
regularity) of the factor-base ideal `I_B⊂F_p[E]`, representing relations as
first syzygies, so that a low-regularity (near-linear) resolution supplies a
linear-size generating set of relations at cost `C` below random relation
harvesting `B`.

### Status
HYPOTHESIS

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Castelnuovo–Mumford regularity and Boij–
Söderberg theory are standard commutative algebra; the *degree of regularity of
solving* — Dreg — appears in the ledger as a barrier, but the **minimal free
resolution / syzygy module of the factor-base ideal** is a distinct object never
proposed).

### Semantic fingerprint
`F` = (the graded ideal `I_B` of factor-base points and its syzygy module; public
Gröbner/linear-algebra ops on the coordinate ring; the geometry of `B` as a
point configuration; the discarded higher syzygies; the retained first-syzygy
generators = relations; relation-gen = first syzygies of `I_B`; compression =
Betti numbers `β_{1,j}`; rank = the syzygy matrix rank; descent = express `Q` as
a syzygy; dominant exponent = regularity `reg(I_B)`).

### Nearest ledger entries
1. **Dreg conservation barrier (B-Dreg)** — bounds the *solving* degree of the
   Semaev system; `reg(I_B)` is the resolution regularity of the *factor-base
   ideal*, a different graded invariant. 2. **PO96K / incidence nullity** —
   measures rank of a fixed relation matrix; this proposes generating the matrix
   from syzygies. 3. **BORDER-B4** — tensor rank; unrelated graded object.
   4. **SIDON-A2** — additive base design; a syzygy resolution is not a design.
   5. **P1479** — feature-space dimension of factor logs; a linear-algebra probe,
   not a free resolution. Exact distinction: no prior candidate uses the minimal
   free resolution / Betti table / Boij–Söderberg cone of `I_B` as the relation
   source.

### Nearest literature
Eisenbud *The Geometry of Syzygies*; Boij–Söderberg (2008); Castelnuovo–Mumford
regularity bounds for points in `P^n`. Claim: points in "general position" have
predictable, often near-linear, resolutions; special configurations have lower
regularity. Gap: the factor-base point configuration on `E` is neither generic
nor studied resolution-theoretically.

### Target family
Ordinary `E/F_p` prime order; factor base = small-`x` points or a rational-map
image, size `B=q^{1/5}`, embedded in `P^N` via a chosen very-ample linear system.
Excluded: degenerate/collinear factor bases (trivially low regularity but no DLP
content).

### Full algorithmic path
1. **Factor base:** `B` points on `E` under a degree-`k` embedding.
2. **Relation generation:** compute the minimal free resolution of `I_B`; read
   first syzygies `β_{1,·}` as relations.
3. **Witness/verify:** each syzygy is an explicit polynomial combination → an
   effective principal divisor relation; verify on `E`.
4. **Probability:** deterministic (resolution is computed, not sampled).
5. **Matrix:** the first-syzygy matrix; rank from `β_{1,j}`.
6. **Calibration:** sparse LA on the syzygy matrix.
7. **Descent:** add `Q` to `B`; the new first syzygies involving `Q` give its
   log.
8. **Offline/online:** resolution of the fixed base offline; `Q`-augmented
   syzygies online.
9. **Memory/parallelism:** resolution is the memory driver (`reg`-dependent).

### Cost model
Resolution cost `~ B^{ω·reg}` (Gröbner of the point ideal). Useful iff
`reg(I_B)=O(1)` and the number of independent first syzygies is `≥B−1` (full
rank). Then relations are produced deterministically at `poly(B)` rather than by
`~B` random trials each `Θ(1)` — a *constant-factor to low-poly* change, so the
honest hope is an exponent change only if the syzygies are *denser in relations*
than random harvesting. Compare: random harvesting `B` trials; rho `sqrt(n)`.

### Why existing negatives do not kill it
The Dreg barrier bounds solving, not the resolution of `I_B`; PO96K measured a
*fixed* matrix's rank, not a syzygy-generated one; no negative addresses the
Betti table.

### Likely fatal obstruction
Generic points have maximal (Minimal-Resolution-Conjecture) Betti numbers → the
first syzygies are exactly the `~B` obvious linear relations with rank `<B−1`
(reproducing PO96K's rank deficit), giving no enrichment. Regularity may also be
`Θ(B^{1/N})`, too large.

### Minimal falsifying experiment
`B∈{16,32,64}` (three) on ordinary prime-order toys `p∈{101,431,1601}`; positive
control = a special (e.g., complete-intersection) sub-configuration with known
low resolution; negative control = generic `B` points. Compute `reg(I_B)` and the
first-syzygy rank; compare to `B−1`.

### Quantitative promotion gate
First-syzygy rank `≥B−1` with `reg(I_B)=O(1)` across the three `B`, and syzygy
relations verified on `E` — extrapolating to a relation-yield exponent beating
random harvesting *and* a complete descent below rho.

### Proof track
Theorem: the factor-base point ideal has `reg=O(1)` and `β_{1}≥B−1` under the
chosen embedding, via a Boij–Söderberg pure-diagram decomposition.

### Disproof track
MRC-generic Betti numbers with first-syzygy rank `<B−1` (reproduces the PO96K
deficit), closing the lane.

### Reproduction artifact
Contract `experiment_contract_syzygy_regularity_factorbase.md`; impl
`syzygy_regularity.sage` (Sage/Macaulay2 resolution); result JSON; audit
`syzygy_audit.m2`; ledger `P1518`.

### **[Representation-changing winner — full contract in §5.2]**

---

## Candidate: SIGNRANK-GAMMA2-B3

### One-sentence mechanism
Represent five-term membership as a Boolean incidence matrix `M` over
(factor-base tuple) × (target) and exploit a small **`γ2` factorization norm /
sign-rank** of `M` to build a low-dimensional membership evaluator whose query
cost `C` is polylogarithmic, giving `α<3/2`.

### Status
HYPOTHESIS

### Novelty classification
POSSIBLY NOVEL (the `γ2`/sign-rank machinery — Linial–Shraibman; Hambardzumyan–
Hatami–Hatami 2025 factorization-norm/Zarankiewicz — is active but has never been
applied to a Semaev membership matrix).

### Semantic fingerprint
`F` = (the membership Boolean matrix `M`; public evaluation as inner products of
low-dim sign vectors; the geometric near-low-complexity of the decomposition
relation; the discarded exact values; the retained sign pattern; relation-gen =
positive cells of `M`; compression = `γ2(M)`; rank = sign-rank; descent = the
target column's sign vector; dominant exponent = `α` from `γ2`).

### Nearest ledger entries
1. **RANK-D3** (report barrier) — separator/Schmidt rank of the S3 operator;
   `γ2` is a *different, non-multiplicative, approximate* complexity measure.
   2. **RT-1476** — the gate. 3. **BORDER-B4/TT-B2** — multiplicative/tensor
   rank; `γ2` is not a tensor rank. 4. **INC-A3** — incidence *reporting*; this
   is incidence *matrix complexity*. 5. **P1479** — linear feature-space of
   factor logs (exact rank); `γ2` is a margin/factorization norm. Exact
   distinction: `γ2`/sign-rank is a communication-complexity measure of the
   incidence matrix, orthogonal to every algebraic-rank barrier stated.

### Nearest literature
Linial–Shraibman (2009) `γ2` and communication; Hambardzumyan–Hatami–Hatami
(2025) "Factorization norms and Zarankiewicz problems" (bounded `γ2` ⇒
degree-bounded, `O(m+n)` ones); Alon–Moran–Yehudayoff sign-rank. Claim: bounded
`γ2` gives efficient (`P^{EQ}`) protocols. **Dual edge:** the same theorem says a
bounded-`γ2` incidence graph has *few* ones — i.e., few relations — so small
`γ2` may bound *supply* rather than speed queries.

### Target family
Ordinary prime-order deck fixtures (P1473), `m=5`. Excluded: as RT-1476.

### Full algorithmic path
1. **Factor base:** sparse `x^L=1` deck.
2. **Relation generation:** membership queries answered by the low-dim sign
   evaluator (if `γ2` small).
3. **Witness/verify:** on a positive sign, extract and verify the 5-tuple.
4. **Probability:** `Θ(1)` at `L=q^{1/5}`.
5. **Matrix:** `Θ(L)` rows; sparse LA `L^2`.
6. **Calibration:** standard.
7. **Descent:** target column's sign vector.
8. **Offline/online:** the factorization `M=BC` offline; online = one inner
   product.
9. **Memory/parallelism:** `γ2·L` storage.

### Cost model
Query `α = log_L γ2(M)`. Crosses rho iff `γ2(M)=L^{o(3/2)}`. Setup = the
factorization (offline, `~L^ω`). But the Zarankiewicz theorem warns: if
`γ2=L^{o(1)}`, `M` has `O(L)` ones total → too few relations. The viable window
is `γ2` small enough for cheap queries yet large enough for `≥L` relations —
which may be empty.

### Why existing negatives do not kill it
No stated barrier bounds `γ2`/sign-rank of the membership matrix; RANK-D3 is
about a different (exact, multiplicative) rank.

### Likely fatal obstruction
The membership matrix is likely *sign-rank-maximal* (pseudo-random), giving
`γ2=Θ(sqrt(L))` and no query saving — or, if `γ2` is small, the supply collapses
by Zarankiewicz. A pincer.

### Minimal falsifying experiment
`L∈{8,16,32}` (three), seeds `{20260718..}`, ordinary prime-order fixtures;
positive control = a planted low-`γ2` structured membership matrix; negative
control = the honest membership matrix. Estimate `γ2` (SDP) and count relations.

### Quantitative promotion gate
`γ2(M)=o(L^{3/2})` **and** relation count `≥L−1` simultaneously across the three
`L` (both sides of the pincer cleared).

### Proof track
Theorem: `γ2` of the `S5` deck membership matrix is `L^{o(1)}` while its density
stays `Ω(L)` — an explicit factorization from the deck's multiplicative structure.

### Disproof track
`γ2=Θ(sqrt(L))` (sign-rank-maximal) or the Zarankiewicz supply collapse — either
closes the lane and strengthens RANK-D3.

### Reproduction artifact
Contract `experiment_contract_gamma2_membership.md`; impl `gamma2_membership.py`
(SDP `γ2` estimator + Sage deck); result JSON; audit; ledger `P1519`.

---

## GROUP C — High-risk speculative mechanisms

## Candidate: GROWTH-SL2-C1

### One-sentence mechanism
Represent scalar multiplication as the action of a small generating set inside
the affine/`SL2`-type transformation group on the Kummer line and exploit a
Bourgain–Gamburd/Helfgott **product-theorem** growth rate to make target-orbit
spreading fast enough that a meet-in-the-middle collision costs `C=n^{1/2−c}`
below the birthday baseline `B=n^{1/2}`.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (growth-in-groups / product theorems are established; their use as
a sub-birthday DLP collision accelerator on the EC Kummer transformation group is
absent from ledger and reports; distinct from ISOWALK's isogeny-graph spectral
gap and STAB's additive small-doubling).

### Semantic fingerprint
`F` = (the transformation semigroup generated by `x↦x([a]·)` maps on `P^1`;
public Kummer differential-addition; the nonabelian growth of the generated set;
the discarded exact scalars; the retained orbit-expansion rate; relation-gen =
collisions in rapidly spreading orbits; compression = expander mixing of the
Cayley graph of generators; rank = n/a; descent = the target's collision;
dominant exponent = birthday exponent modified by growth).

### Nearest ledger entries
1. **ISOWALK-C1** — spectral gap of the *isogeny* graph (moves between curves);
   this is growth in the *transformation group on one curve's* Kummer line.
   2. **STAB-C1** — additive small-doubling of the x-addition graph (abelian);
   product theorems are nonabelian/multiplicative growth. 3. **PO96P Lattès
   orbit** — a single map's orbit; this uses a generating *set*. 4. **NILSEQ-C2**
   — higher-order Fourier of the abelian sequence; distinct. 5. **rho baseline**
   — random walk; this is a structured (expander) walk. Exact distinction:
   Helfgott-type product growth in the generated transformation group is the
   mechanism, not an isogeny-graph gap or an additive-energy statement.

### Nearest literature
Helfgott (2008) growth in `SL2(F_p)`; Bourgain–Gamburd (2008) expansion; Tao
*Expansion in finite simple groups of Lie type*. Claim: bounded generating sets
of `SL2(F_p)` grow at a fixed positive rate → diameter `O(log p)`. Gap: the EC
scalar action does **not** obviously generate an `SL2`-type group; the relevant
semigroup may be abelian (then no product-theorem gain).

### Target family
Ordinary prime-order `E/F_p`; Kummer line `x`-coordinate model. Excluded: curves
whose scalar action is provably abelian on `P^1` (the generic case — the central
risk).

### Full algorithmic path
1. **Factor base:** none; this is a collision method.
2. **Relation generation:** iterate a small generating set of transformation
   maps to spread two orbit clouds (baby/giant) faster than random.
3. **Witness/verify:** an orbit collision `x([a]G)=x([b]Q)` gives the log.
4. **Probability:** birthday, but on a faster-mixing structured walk.
5. **Matrix:** none.
6. **Calibration:** none.
7. **Descent:** the collision *is* the descent.
8. **Offline/online:** generator set offline; walk online.
9. **Memory/parallelism:** distinguished-point / VW parallel collision.

### Cost model
If the transformation group is genuinely nonabelian with product-theorem growth,
diameter `O(log)` and near-uniform mixing could shave the *constant* — but the
birthday exponent `1/2` is information-theoretic for a generic-order group and
growth changes constants, not the exponent, **unless** the growth exposes an
`o(n)` invariant subset. Compare rho `0.886 sqrt(n)`.

### Why existing negatives do not kill it
No ledger negative addresses nonabelian growth of the scalar transformation
group; the generic-group bound is about *encodings*, not about a structured walk
that might expose a non-generic invariant.

### Likely fatal obstruction
The scalar action on the Kummer line is **abelian** (`[a][b]=[ab]`), so no
`SL2`-style product theorem applies; growth is linear and the birthday exponent
is untouched — a near-certain kill unless a genuinely nonabelian companion action
(e.g., including the hyperelliptic involution + a twist map) is found that still
carries the log.

### Minimal falsifying experiment
`p∈{1009,4099,16411}` (three), seeds `{20260718..}`; positive control = an
`SL2(F_p)` toy with known logarithmic diameter (sanity of the growth code);
negative control = the pure abelian scalar walk (must show no exponent gain).
Measure orbit-cover exponent vs step count.

### Quantitative promotion gate
Measured collision exponent `<1/2−c` (`c>0`) on the EC transformation walk across
the three sizes — not merely a constant-factor improvement.

### Proof track
Theorem: an explicit bounded generating set of transformation maps on `E`'s
Kummer line generates a nonabelian group of product-theorem type whose orbit of
`G` covers an `n^{1/2−c}` subset carrying `Q`.

### Disproof track
The generated group is abelian / linearly growing (the expected outcome),
confirming the birthday exponent is untouched.

### Reproduction artifact
Contract `experiment_contract_growth_sl2_walk.md`; impl `growth_sl2_walk.sage`;
result JSON; audit; ledger `P1520`.

---

## Candidate: PILA-WILKIE-C2

### One-sentence mechanism
Exploit the Pila–Wilkie o-minimal **point-counting** theorem — algebraic points
on a transcendental (definable) family are sparse except on a genuine algebraic
part — to predict, from the counting-density excess, where the `{x([k]G)}`
configuration carries an *algebraic* relation surplus that concentrates the
factor-base search.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (Pila–Wilkie counting and its transcendence applications are
established; using the counting-density as a relation-yield predictor for ECDLP
is absent; distinct from ZILBERPINK-C2's unlikely-intersection existence claim).

### Semantic fingerprint
`F` = (a definable family in an o-minimal structure whose algebraic points encode
relations; public evaluation of `x([k]·)`; the transcendental-vs-algebraic
dichotomy of the point set; the discarded transcendental bulk; the retained
algebraic part; relation-gen = algebraic-part points; compression = the counting
bound `O(H^ε)`; rank = of the algebraic part; descent = target in the algebraic
part; dominant exponent = density of the algebraic part).

### Nearest ledger entries
1. **ZILBERPINK-C2** — anomalous subvariety *existence* in `E^k`; Pila–Wilkie
   gives a *counting density*, a quantitatively different tool. 2. **NILSEQ-C2** —
   higher-order Fourier; not o-minimal counting. 3. **STAB-C1** — additive
   stability; distinct. 4. **P1449 ancestry invariance** — a permutation-
   invariance obstruction Pila–Wilkie counting is designed to see past. 5. **rho**
   — random baseline. Exact distinction: the counting-theorem *density estimate*
   (not existence) as a search-concentration predictor is new.

### Nearest literature
Pila–Wilkie (2006) "The rational points of a definable set"; Pila (2011)
André–Oort; Habegger–Pila. Claim: `≤ c H^ε` algebraic points of height `≤H` off
the algebraic part. Gap: the ECDLP relation set may lie *entirely* in the
algebraic part (then the theorem is vacuous) — the central risk.

### Target family
Ordinary prime-order `E/F_p` lifted to a definable family over `R`/`Q_p`.
Excluded: cases where relations are all algebraic (theorem vacuous).

### Full algorithmic path
1. **Factor base:** points whose defining data sits in a definable family.
2. **Relation generation:** locate the algebraic part of the family; its points
   are candidate relations.
3. **Witness/verify:** reduce candidates mod `p`, verify on `E`.
4. **Probability:** governed by algebraic-part density.
5. **Matrix:** algebraic-part relations.
6. **Calibration:** sparse LA.
7. **Descent:** place `Q` in the family; find its algebraic-part fiber.
8. **Offline/online:** family/algebraic-part offline; target fiber online.
9. **Memory/parallelism:** algebraic-part enumeration.

### Cost model
Only useful if the algebraic part is `o(n^{1/2})` yet carries `≥B` relations —
i.e., a *concentration*. The counting theorem gives an upper bound on the
transcendental part, not a constructive locator of the algebraic part; the
constructive step is the hard, possibly-superpolynomial, gap. Compare rho.

### Why existing negatives do not kill it
No ledger negative uses o-minimal counting; ZILBERPINK addressed existence, not
density-based concentration.

### Likely fatal obstruction
Over a *finite* field there is no height/transcendence to exploit — Pila–Wilkie
lives in characteristic 0; the reduction `mod p` may erase exactly the algebraic-
part distinction, making the whole channel a characteristic-0 artifact (like the
closed xedni/height-lift lane).

### Minimal falsifying experiment
Toy lifts of `p∈{101,211,431}` (three) to a definable family; positive control =
a family with a known nontrivial algebraic part; negative control = a family
whose relations are all algebraic (vacuous). Count algebraic-part points vs
height; check whether reduction preserves the surplus.

### Quantitative promotion gate
A definable family for `E` whose algebraic part has size `o(n^{1/2})`, carries
`≥B` reduce-and-verify relations, and whose extraction is `poly` — extrapolating
below rho.

### Proof track
Theorem: an explicit definable family whose algebraic part is provably small yet
relation-complete for `E`'s subgroup.

### Disproof track
The algebraic part is all of the relation set (theorem vacuous) or is erased by
reduction mod `p` (characteristic-0 artifact) — closing the lane.

### Reproduction artifact
Contract `experiment_contract_pila_wilkie_density.md`; impl
`pila_wilkie_density.sage`; result JSON; audit; ledger `P1521`.

---

## Candidate: SANDPILE-JACOBIAN-C3

### One-sentence mechanism
Represent the target subgroup via the **critical group (sandpile / graph
Jacobian)** of an explicitly constructed graph and exploit fast chip-firing +
the Matrix-Tree structure to solve the DLP in the combinatorial-Jacobian
representation at cost `C` below rho `B`.

### Status
CONJECTURE

### Novelty classification
POSSIBLY NOVEL (sandpile/critical groups of isogeny and Cayley graphs are
studied — Ribet component groups, Cayley-graph critical groups — but never as an
ECDLP solving representation; distinct from OLAT's relation lattice, which is not
a graph Jacobian).

### Semantic fingerprint
`F` = (the critical group `K(Γ)=Z^V_0/im(Laplacian)`; public chip-firing /
Laplacian reduction; the isomorphism `K(Γ)≅E(F_p)` if one exists; the discarded
graph geometry; the retained group structure; relation-gen = spanning-tree /
chip-firing equivalences; compression = Matrix-Tree; rank = Laplacian
Smith-normal-form; descent = target's chip configuration; dominant exponent =
chip-firing mixing/stabilization time).

### Nearest ledger entries
1. **OLAT-C3** — a relation lattice `Λ⊂Z^B` with SVP; the critical group is the
   *cokernel* of a graph Laplacian, a specific structured lattice with chip-
   firing dynamics, not a generic SVP instance. 2. **EFFRES-A2** — effective
   resistance (same Laplacian world) but for *enrichment*, not as the DLP group
   itself. 3. **PO-transfer** Jacobians — abelian-variety Jacobians, not graph
   Jacobians. 4. **ECFG** functional graph — a dynamics graph, not its critical
   group. 5. **rho**. Exact distinction: the *combinatorial* (graph) Jacobian and
   its chip-firing dynamics as the DLP carrier is new.

### Nearest literature
Baker–Norine (2007) Riemann–Roch for graphs; Lorenzini critical groups; Ribet
component-group/isogeny-graph work. Claim: a graph's critical group is a
computable finite abelian group with rich structure. Gap: producing a graph with
`K(Γ)≅E(F_p)` **and a computable isomorphism** is exactly the circular obstacle.

### Target family
Ordinary prime-order `E/F_p`. Excluded: any construction whose `K(Γ)≅E(F_p)`
isomorphism itself requires a DLP oracle (the trap).

### Full algorithmic path
1. **Factor base:** vertices of `Γ` (e.g., an isogeny/Cayley graph attached to
   `E`).
2. **Relation generation:** chip-firing equivalences (spanning-tree relations).
3. **Witness/verify:** reduce chip configs to canonical form; map back to `E`.
4. **Probability:** deterministic (Laplacian reduction).
5. **Matrix:** the graph Laplacian; Smith normal form gives the group.
6. **Calibration:** solve in `K(Γ)` where the structure is explicit.
7. **Descent:** target `Q` as a chip configuration; canonicalize.
8. **Offline/online:** graph + Laplacian SNF offline; target reduction online.
9. **Memory/parallelism:** sparse Laplacian; parallel chip-firing.

### Cost model
Chip-firing stabilization is polynomial in `|V|`, but the payoff requires a
*natural* `Γ` with a *computable* `K(Γ)→E(F_p)` map whose fibers are cheap; if
`|V|=poly(log p)` and the map is efficient the DLP would be poly — implausibly
strong, flagging the circularity. Compare rho.

### Why existing negatives do not kill it
No ledger negative treats graph critical groups; OLAT is a different lattice
object.

### Likely fatal obstruction
Circularity: any efficiently-computable isomorphism `K(Γ)≅E(F_p)` transports the
DLP both ways, so either the isomorphism is as hard as the DLP (no gain) or `Γ`
is exponentially large. Near-certain kill absent a natural, small, computable
`Γ`.

### Minimal falsifying experiment
`p∈{101,211,431}` (three), candidate graphs = isogeny graph, a Cayley graph of
`E(F_p)`, a Schreier graph; positive control = a graph with known small critical
group and computable iso; negative control = a random regular graph (must show no
usable `E`-iso). Compute `K(Γ)` SNF; test for a cheap `E`-iso.

### Quantitative promotion gate
A polynomial-size `Γ` with a `poly`-computable `K(Γ)→E(F_p)` map and target
canonicalization below rho — a genuine, non-circular reduction.

### Proof track
Theorem: an explicit natural graph attached to `E` has `K(Γ)≅E(F_p)` with a
`poly`-time isomorphism.

### Disproof track
Every natural `Γ` either has the wrong critical group or a DLP-hard isomorphism
(the expected circularity), closing the lane.

### Reproduction artifact
Contract `experiment_contract_sandpile_jacobian.md`; impl
`sandpile_jacobian.sage`; result JSON; audit; ledger `P1522`.

---

## GROUP D — Negative-theory candidates (expose a precise loophole or barrier)

## Candidate: SOS-LB-D1

### One-sentence mechanism
Prove a **degree lower bound** `d_SOS=Ω(L^{ε})` for any sum-of-squares/
Positivstellensatz certificate of `S5` deck membership (via Grigoriev/pseudo-
calibration), which would kill SOS-LASSERRE-A1 and quantify exactly which convex
relaxations remain.

### Status
OPEN (barrier candidate)

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (SOS lower bounds are a mature area — Grigoriev
2001; Barak–Steurer pseudo-calibration).

### Semantic fingerprint
Object = the `S5` membership pseudo-distribution; retained info = the moment
constraints a degree-`d` liar can satisfy; mechanism = a degree-`d`
pseudo-expectation fooling SOS; exponent = the refutation degree.

### Nearest ledger entries
1. **SPARSEBND-D3** (report) — border-rank/sparsity barrier; SOS-LB covers the
   convex-certificate axis it misses. 2. **B-Dreg** — Gröbner solving degree;
   related but SOS ≠ Gröbner. 3. **RT-1476** — the gate this would help close.
   4. **RANK-D3** — separator rank; different measure. 5. **P1512-R1** — Chow
   atomizer `Ω(r^5)` (a different object). Exact distinction: an SOS-degree lower
   bound is a new barrier axis.

### Nearest literature
Grigoriev (2001) linear-Positivstellensatz LBs; Barak–Steurer (2014) SOS survey;
Kothari et al. planted-clique SOS. Claim: pseudo-calibration yields `Ω(L^ε)`
degree LBs for random-like systems. Gap: the `S5` deck is structured (deck +
curve), not fully random.

### Target family / path / cost
Applies to the SOS-LASSERRE-A1 setting. The "algorithmic path" is a proof: build
a degree-`d` pseudo-expectation over the target distribution consistent with the
`S5` constraints; show it fools SOS up to `d=Ω(L^ε)`. Cost model: the barrier
asserts `α_SOS=Ω(L^ε)`, above `3/2`.

### Why existing negatives do not already establish it
No stated barrier addresses SOS degree; this fills the gap.

### Likely fatal obstruction (to the barrier)
The deck's algebraic structure may admit a genuine low-degree certificate
(then A1 wins and this barrier is false) — that is precisely the useful outcome.

### Minimal falsifying experiment
Same fixtures as A1; if A1 measures `d_SOS=O(1)`, this barrier is refuted. The
barrier's own "experiment" is a pseudo-calibration construction checked on
`L∈{8,16,32}`.

### Quantitative promotion gate
A proved `d_SOS=Ω(L^ε)` with `ε>0`, or empirical `d_SOS` growth on the three `L`.

### Proof / disproof track
Proof = pseudo-calibration. Disproof = an explicit `O(1)`-degree certificate.

### Reproduction artifact
Note `sos_lower_bound_s5.md`; impl `sos_lb_pseudocalibration.py`; ledger `P1523`.

---

## Candidate: SLICE-RANK-1-D2

### One-sentence mechanism
Prove that the slice-rank/Croot–Lev–Pach polynomial method gives **no** relation-
supply enrichment for the rank-1 cyclic group `E(F_p)` — the tool only bites in
high-rank `F_p^n` objects — so any additive-combinatorial enrichment hope
(including RT-1472's `δ` and the additive C-side ideas) must pass through a
Weil-restricted high-rank object.

### Status
OPEN (barrier candidate)

### Novelty classification
LEDGER-NEW as a *stated* barrier; LITERATURE-ADJACENT (CLP/slice-rank is a
high-rank phenomenon; cyclic `Z/N` caps are governed by Behrend/Bloom–Sisask, not
slice rank).

### Semantic fingerprint
Object = the 3-term relation set `{P+Q+R=O}` in the cyclic group; mechanism =
slice-rank bound on relation-free sets; the barrier = in rank 1 the bound is
near-trivial; loophole retained = high-rank Weil restriction `E(F_{p^n})`.

### Nearest ledger entries
1. **ENERGY-D1** (report) — 2-term additive-energy ceiling; this is the 3-term
   slice-rank analogue and its rank-1 collapse. 2. **RT-1472** — the enrichment
   gate. 3. **SIDON-A2 / STAB-C1** — additive designs/stability; bounded by the
   same rank-1 collapse. 4. **SCRAMBLE-D2** — addition-law energy defect; kindred.
   5. **GAUDRY-BAR-D3** — fixed-genus Weil-descent cost (the high-rank loophole's
   own barrier). Exact distinction: the precise statement that slice rank is
   *vacuous in rank 1*, pointing the only additive enrichment at the Weil-
   restricted setting (already Gaudry-barriered).

### Nearest literature
Croot–Lev–Pach (2017); Ellenberg–Gijswijt (2017); Tao slice-rank notes (2016);
Bloom–Sisask (2020) cyclic caps. Claim: slice rank yields `4^{γn}` caps in
`Z_4^n` but nothing comparable in `Z/N`. Gap: a fully explicit rank-1
non-enrichment statement for the EC relation set.

### Target family / path / cost
Cyclic `E(F_p)` (rank 1). Proof: slice rank of the `Z/N` three-term tensor is
`Θ(N)` (full), so no `o(N)` relation-free-set bound and no super-linear supply
enrichment; the only escape is `E(F_{p^n})` with `n` large, where GAUDRY-BAR-D3
already charges `Ω̃(q^{2−2/g})`.

### Why existing negatives do not already establish it
ENERGY-D1 covered 2-term energy; the 3-term slice-rank collapse in rank 1 is a
distinct statement that also bounds the C-side additive ideas.

### Likely fatal obstruction (to the barrier)
A clever high-rank embedding of `E(F_p)` (not the naive Weil restriction) that
escapes both slice-rank triviality and the Gaudry cost — the useful loophole to
hunt.

### Minimal falsifying experiment
`p∈{101,211,431}` (three); compute the slice rank of the 3-term relation tensor;
confirm it is full (`Θ(N)`); positive control = `F_2^n` (known `<3^n` slice
rank); negative control = cyclic (must be full).

### Quantitative promotion gate
Slice rank `=Θ(N)` confirmed across the three sizes (barrier holds), or a genuine
`o(N)` bound found (barrier refuted → real enrichment).

### Proof / disproof track
Proof = full slice rank of the cyclic three-term tensor. Disproof = a sub-full
bound via a nontrivial embedding.

### Reproduction artifact
Note `slice_rank_rank1_barrier.md`; impl `slice_rank_cyclic.sage`; ledger `P1524`.

---

## Candidate: LINLABEL-UNIFIED-D3

### One-sentence mechanism
Unify the PO96D scalar-linear factor-base negative (main ledger) and the P1512-R1
scalar-linear Chow-atomizer `Ω(r^5)` closure (IC-state ledger) into **one
theorem**: any target-label that is an `F_p`-linear functional of the
pushforward/endpoint data has marginal rank `o(B)` or compiler cost `Ω(r^5)`;
only genuinely **nonlinear** labels (the preserved exception, which APOLARITY-
ATOMIZER-A2 and GENJAC-MODULUS-B1 attack) can escape.

### Status
OPEN (barrier candidate)

### Novelty classification
LEDGER-NEW (unifies two separately-proved scalar-linear negatives across both
ledgers into a single model-level statement and pins the exact surviving
loophole).

### Semantic fingerprint
Object = the space of target-labels on a transfer/compiler object; mechanism =
`F_p`-linearity in the target forces bounded rank / high compiler degree; the
loophole = nonlinear (bilinear/quadratic/Waring) labels.

### Nearest ledger entries
1. **PO96D-R1** — exhausted scalar-linear labels `q2−[k]φ·q1`, all worse.
   2. **P1512-R1** — scalar-linear Chow atomizer `Ω(r^5)`. 3. **PO96AB-R1-F2/F3**
   — typed objects that collapse to `[3]Γ(P)` (linear). 4. **TRANSFER-H013…H024**
   — the `k^D`/hidden-square program, all defeated by linearity/target-DLP.
   5. **BAR-TRANSPORT-D1** (report) — transport injections. Exact distinction:
   both ledgers' scalar-linear negatives become corollaries of one linearity-
   rank/degree theorem, isolating the nonlinear exception as the *only* frontier.

### Nearest literature
Generic-group model (Shoup 1997); Nechaev; algebraic-computation-tree lower
bounds. Claim: linear functionals over a group carry bounded independent
information. Gap: a clean cross-object statement covering both the transfer
factor base and the marked-eliminant compiler.

### Target family / path / cost
Applies to every transfer/compiler object in both ledgers. Proof: any label
`L(P)=Σ c_i·f_i(P)` linear over `F_p` in the endpoint coordinates has image in a
fixed `O(1)`-dimensional space per target → marginal rank `o(B)`; and a
scalar-linear atomizer inherits the Chow `Ω(r^5)`. Cost model: the barrier
asserts scalar-linear transfer cannot beat rho; nonlinear is unbarriered.

### Why existing negatives do not already establish it
They are two *separate* scoped negatives; unifying them yields a reusable barrier
and a precise loophole spec that directs A2/B1.

### Likely fatal obstruction (to the barrier)
A nonlinear label (Waring circuit, non-split cocycle) that provably exceeds the
linear rank bound — the intended positive escape (A2/B1). The barrier is
*designed* to be escaped only there.

### Minimal falsifying experiment
Re-run PO96D scalar-linear sweep + P1510 scalar-linear atomizer on three fixtures
`p∈{271,499,787}`; confirm both hit the linear bound; then test one nonlinear
label (a Waring/quadratic-gate atomizer) for rank/degree escape.

### Quantitative promotion gate
All scalar-linear labels reproduce `rank o(B)` / `Ω(r^5)` across three fixtures,
AND a nonlinear label demonstrably exceeds the bound on at least one — sharply
locating the loophole.

### Proof / disproof track
Proof = linearity ⇒ bounded rank/degree (both ledgers). Disproof = a scalar-
linear label with rank `≥B−1` and sub-`r^{5/2}` cost (would reopen the linear
lane).

### Reproduction artifact
Note `linlabel_unified_barrier.md`; impl `linlabel_probe.sage`; ledger `P1525`.

---

## 3. Ranking

Scores 0–5 per axis: **D** = distance from prior ledger/report mechanisms;
**V** = plausibility of an exact verifier; **E** = chance of changing an exponent
(not a constant); **P** = complete-path coverage; **F** = falsifiability at toy
scale; **L** = literature-novelty confidence; **R** = *low* hidden preprocessing/
memory risk (5 = low risk). Reject if semantic novelty `D<3`, no complete descent
path, no rho comparison, or no precise distinction from the closest entry.

| Cand | Group | D | V | E | P | F | L | R | Σ | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **SOS-LASSERRE-A1** | A | 4 | 5 | 4 | 5 | 5 | 4 | 3 | **30** | **WINNER (conservative)** |
| APOLARITY-ATOMIZER-A2 | A | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 25 | keep |
| CORRELATED-PEEL-A3 | A | 4 | 5 | 3 | 4 | 5 | 3 | 4 | 28 | keep |
| GENJAC-MODULUS-B1 | B | 4 | 4 | 3 | 4 | 4 | 3 | 3 | 25 | keep |
| **SYZYGY-REGULARITY-B2** | B | 5 | 5 | 4 | 5 | 5 | 4 | 3 | **31** | **WINNER (representation)** |
| SIGNRANK-GAMMA2-B3 | B | 4 | 4 | 3 | 4 | 4 | 4 | 3 | 26 | keep |
| **GROWTH-SL2-C1** | C | 4 | 5 | 3 | 4 | 5 | 4 | 4 | **29** | **WINNER (high-risk)** |
| PILA-WILKIE-C2 | C | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 23 | keep (weak) |
| SANDPILE-JACOBIAN-C3 | C | 4 | 4 | 2 | 3 | 4 | 4 | 3 | 24 | keep (circularity risk) |
| SOS-LB-D1 | D | 4 | 4 | — | 4 | 4 | 4 | 4 | 24 | barrier |
| SLICE-RANK-1-D2 | D | 4 | 5 | — | 4 | 5 | 4 | 5 | 27 | barrier |
| LINLABEL-UNIFIED-D3 | D | 5 | 4 | — | 4 | 4 | 4 | 4 | 25 | barrier |

All twelve satisfy `D≥3`, have a complete (if speculative) descent path, compare
to rho, and carry a precise distinction from their nearest entry. **Winners:**
SOS-LASSERRE-A1 (conservative), SYZYGY-REGULARITY-B2 (representation),
GROWTH-SL2-C1 (high-risk).

---

## 4. Experiment contracts (three winners)

### 4.1 SOS-LASSERRE-A1

```yaml
id: EXP-SOS-LASSERRE-001            # ledger P1514
hypothesis: >
  The degree-d Lasserre/SOS certificate for m=5 Semaev deck membership has
  d_SOS = O(1), giving membership-query exponent alpha < 3/2 and, via the
  RT-1476 accounting, a complete-cost single-target ECDLP below rho.
null_hypothesis: >
  d_SOS grows with L (alpha = Omega(L^eps) > 3/2); SOS is no cheaper than the
  Gröbner/border-rank backends already at the wall.
target_family: ordinary prime-order E/F_p, j != 0,1728, non-anomalous, deck x^L=1
sizes: {L: [8, 16, 32]}            # three toy sizes, q ~ L^5
seeds: [20260718, 20260719, 20260720, 20260721, 20260722]
controls:
  positive: planted decomposable target (must certify at small d)
  negative: random non-decomposable target (must remain infeasible)
  ordinary_prime_order: required for all fixtures
metrics: [d_SOS, sdp_wall_time, extraction_success_rate, alpha_fit,
          total_exponent_estimate_2_over_6_minus_alpha]
promotion_gate:
  condition: "c * d_SOS < 1.5 with flat/monotone trend across L, AND
              exact 5-tuple extraction verified on >= 95% of planted controls"
  note: "correctness alone fails; the measured/extrapolated alpha must trend < 3/2"
falsification: "d_SOS(L) fit exponent > 0 (grows with L) OR alpha_fit >= 3/2"
baselines: [rho_0.886_sqrt_n, bsgs_sqrt_n, amadori_pintore_sala_grobner]
artifacts:
  contract: research/experiment_contract_sos_lasserre_s5_membership.md
  impl: experiments/ecdlp_index_calculus/sos_lasserre_s5.sage
  result: experiments/ecdlp_index_calculus/sos_lasserre_s5_result.json
  audit: experiments/ecdlp_index_calculus/sos_lasserre_s5_audit.py
```

First executable command:

```bash
sage experiments/ecdlp_index_calculus/sos_lasserre_s5.sage --L 8 \
  --seed 20260718 --fixture ordinary_prime_order --degrees 2,3,4 \
  --controls planted,random --out sos_lasserre_s5_result.json
```

### 4.2 SYZYGY-REGULARITY-B2

```yaml
id: EXP-SYZYGY-REG-001             # ledger P1518
hypothesis: >
  Under a chosen degree-k embedding, the factor-base point ideal I_B on an
  ordinary prime-order E has reg(I_B) = O(1) and first-syzygy rank >= B-1,
  yielding a deterministic, full-rank relation set with a complete blind
  descent below rho.
null_hypothesis: >
  I_B has MRC-generic (near-maximal) Betti numbers; first-syzygy rank < B-1
  (reproducing the PO96K rank deficit) and/or reg(I_B) grows with B.
target_family: ordinary prime-order E/F_p; factor base = small-x or rational-map image
sizes: {B: [16, 32, 64], p: [101, 431, 1601]}
seeds: [20260718, 20260719, 20260720]
controls:
  positive: complete-intersection sub-configuration (known low resolution)
  negative: B generic points (MRC-generic Betti numbers)
  matched: equal-B random harvesting relation count
metrics: [reg_I_B, betti_table, first_syzygy_rank, relation_verify_rate,
          blind_descent_rate, charged_cost_vs_rho]
promotion_gate:
  condition: "first_syzygy_rank >= B-1 AND reg(I_B)=O(1) across all B, with
              syzygy relations verified on E, extrapolating relation-yield
              exponent below random harvesting AND complete descent below rho"
falsification: "first_syzygy_rank < B-1 on the honest base (matches PO96K) OR
                reg(I_B) fit exponent > 0"
baselines: [rho_0.886_sqrt_n, random_relation_harvesting, po96k_incidence_nullity]
artifacts:
  contract: research/experiment_contract_syzygy_regularity_factorbase.md
  impl: experiments/ecdlp_index_calculus/syzygy_regularity.sage
  result: experiments/ecdlp_index_calculus/syzygy_regularity_result.json
  audit: experiments/ecdlp_index_calculus/syzygy_audit.m2
```

First executable command:

```bash
sage experiments/ecdlp_index_calculus/syzygy_regularity.sage --B 16 \
  --p 101 --embed-degree 3 --seed 20260718 \
  --controls complete_intersection,generic --emit-betti \
  --out syzygy_regularity_result.json
```

### 4.3 GROWTH-SL2-C1

```yaml
id: EXP-GROWTH-SL2-001             # ledger P1520
hypothesis: >
  A bounded generating set of transformation maps on E's Kummer line generates
  a nonabelian group of product-theorem (Helfgott/Bourgain-Gamburd) type whose
  structured walk covers an n^{1/2 - c} (c>0) subset carrying the target,
  giving a sub-birthday single-target collision below rho.
null_hypothesis: >
  The scalar transformation action is abelian ([a][b]=[ab]); growth is linear,
  diameter Theta(n), and the birthday exponent 1/2 is untouched (constant-only
  change at best).
target_family: ordinary prime-order E/F_p, Kummer-line model
sizes: {p: [1009, 4099, 16411]}
seeds: [20260718, 20260719, 20260720]
controls:
  positive: SL2(F_p) toy with known O(log p) diameter (growth-code sanity)
  negative: pure abelian scalar walk (must show no exponent gain)
  vw_parallel: distinguished-point collision harness for fair rho comparison
metrics: [orbit_cover_exponent, collision_exponent, diameter_fit,
          group_commutativity_test, charged_ops_vs_0.886_sqrt_n]
promotion_gate:
  condition: "measured collision_exponent < 0.5 - c (c>0) on the EC walk across
              all three p, not merely a constant-factor speedup"
falsification: "generated group is abelian / linearly growing; collision
                exponent = 0.5 within noise"
baselines: [rho_0.886_sqrt_n, bsgs_sqrt_n]
artifacts:
  contract: research/experiment_contract_growth_sl2_walk.md
  impl: experiments/ecdlp_isogeny/growth_sl2_walk.sage
  result: experiments/ecdlp_isogeny/growth_sl2_walk_result.json
  audit: experiments/ecdlp_isogeny/growth_sl2_audit.py
```

First executable command:

```bash
sage experiments/ecdlp_isogeny/growth_sl2_walk.sage --p 1009 \
  --generators kummer_scalar_set --seed 20260718 \
  --controls sl2_sanity,abelian_walk --steps-log2 6,8,10 \
  --out growth_sl2_walk_result.json
```

---

## 5. Red-team: are the three winners disguised repetitions or cost-negative?

**SOS-LASSERRE-A1.** *Disguised repetition?* The membership-backend meta-lane has
11 prior variants (POLY/TT/BORDER/SPARSE/SUBRES/KU/DISP/PWRSUM/LDEC/INC/HOLANT),
all barriered by border-rank/sparsity/separator-rank/Holant-dichotomy. A skeptic
says: "SOS is just another backend on the same dense system; SPARSEBND-D3 already
implies it is expensive." Rebuttal: SPARSEBND-D3 bounds *sparsity and border
rank*, which do **not** bound SOS degree — a dense, high-border-rank polynomial
system can have a constant-degree SOS certificate (this is why SOS is studied
*because* it can beat elimination). The distinction is real, but the honest risk
is high: SOS **lower bounds** (candidate SOS-LB-D1) frequently force `d_SOS=Ω(L^ε)`
for random-like systems, in which case A1 is cost-negative (`α≫3/2`). *Verdict:*
not a repetition (new complexity axis), but its make-or-break is an unmeasured
SOS degree that the literature's default expectation says will be large. The
experiment is cheap and decisive — which is why it is the conservative winner.

**SYZYGY-REGULARITY-B2.** *Disguised repetition?* PO96K already measured a fixed
relation matrix's rank deficit; a skeptic says the first-syzygy module *is* that
same matrix. Rebuttal: PO96K took a *given* incidence matrix; B2 asks whether the
*minimal free resolution* supplies a **different, deterministic, potentially
denser** generating set with `reg=O(1)` — a graded invariant PO96K never
computed. But the honest fatal risk is that generic points obey the Minimal
Resolution Conjecture, so `β_1` gives exactly the `~B` obvious relations with
rank `<B−1` — i.e., B2 *reproduces* the PO96K deficit and is cost-negative. The
only escape is a *special* (non-generic) factor-base configuration with low
resolution, and any such configuration risks being DLP-content-free (collinear/
degenerate). *Verdict:* genuinely new object and exact verifier, but plausibly
converges to a known negative; its value is that it would *explain* the PO96K
deficit resolution-theoretically even if it fails as a speedup.

**GROWTH-SL2-C1.** *Disguised repetition?* ISOWALK-C1 already used expander walks;
a skeptic says C1 is ISOWALK with different words. Rebuttal: ISOWALK walks the
*isogeny graph between curves* (spectral gap → collision constant); C1 walks the
*transformation group on one curve's Kummer line* and invokes a *product theorem*,
not a spectral gap. The distinction is real. But the near-certain fatal
obstruction is that the scalar action is **abelian** (`[a][b]=[ab]`), so no
`SL2`-type product theorem applies and, worse, the birthday exponent `1/2` is
information-theoretic for a generic-order cyclic group — growth changes constants,
not the exponent, *unless* a genuinely nonabelian companion action carrying the
log is found (unlikely on the Kummer line). *Verdict:* not a repetition, but the
most likely to be cost-neutral (constant-factor only); it is the high-risk winner
precisely because its falsification is crisp and it forces the abelian-growth
question to be settled on record.

**Cross-cutting red-team.** All three winners, and indeed all nine mechanism
candidates, live under the standing barriers: generic-group encoding bounds
(constant-only for structured walks), the RT-1472/RT-1476 accounting (nothing
below rho without `δ>1/4` or `α<3/2`), and LINLABEL-UNIFIED-D3 (scalar-linear
transfer is bounded — every candidate must show a *nonlinear* mechanism). None of
the twelve is yet demonstrated to cross exponent `1/2`; each is a scoped,
falsifiable hypothesis with an exact toy verifier and an honest most-likely-fatal
obstruction. A failed candidate here is a scoped negative result that narrows the
non-generic frontier — it is **not** evidence that prime-field ECDLP cannot be
improved.

---

## Claim discipline

Every "below rho" in this report is a *conditional* target contingent on an
unmeasured quantity (`d_SOS`, `reg(I_B)`, growth exponent, `δ`, `α`, `w(r)`,
`γ2`). No verified single-target complete-cost speedup is claimed; none exists in
either ledger. All fixtures are generated toy curves or public parameters; no
wallets, production keys, or unauthorized systems are targeted. Correctness of a
membership certificate, a syzygy, a critical group, or a collision is
distinguished throughout from a performance claim and from verified ECDLP
recovery. Toy evidence, heuristics, restricted models, and untested assumptions
are labeled as such.

---

### Sources (external literature search)

- Semaev, *Summation polynomials and the DLP on elliptic curves*, ePrint 2004/031.
- Amadori, Pintore, Sala, *On the DLP for prime-field elliptic curves*, ePrint 2017/609.
- Kousidis, Wiemers, *On the first fall degree of summation polynomials*, ePrint 2015/1121.
- Lasserre (2001) moment-SOS hierarchy; Laurent (2009) survey — [SOS optimization](https://en.wikipedia.org/wiki/Sum-of-squares_optimization); no Semaev/SOS connection found in search.
- Grigoriev (2001) Positivstellensatz lower bounds; Barak–Steurer SOS survey.
- Déchène, *Arithmetic of Generalized Jacobians*, [ePrint 2006/033](https://eprint.iacr.org/2006/033.pdf); *Discrete Logarithms in Generalized Jacobians*, [arXiv:math/0610073](https://arxiv.org/pdf/math/0610073); *Security of Generalized Jacobian Cryptosystems*.
- Iarrobino–Kanev (1999) *Power Sums, Gorenstein Algebras, and Determinantal Loci* (apolarity/catalecticants); Landsberg (2012) *Tensors*.
- Eisenbud, *The Geometry of Syzygies*; Boij–Söderberg (2008).
- Linial–Shraibman (2009) `γ2` and communication; Hambardzumyan–Hatami–Hatami (2025) [*Factorization norms and Zarankiewicz problems*](https://arxiv.org/abs/2502.18429).
- Croot–Lev–Pach (2017); Ellenberg–Gijswijt (2017); Tao (2016) [*Notes on the slice rank of tensors*](https://terrytao.wordpress.com/2016/08/24/notes-on-the-slice-rank-of-tensors/); Bloom–Sisask (2020).
- Helfgott (2008) *Growth and generation in SL2(Z/pZ)*; Bourgain–Gamburd (2008); Tao, *Expansion in finite simple groups of Lie type*.
- Pila–Wilkie (2006) *The rational points of a definable set*; Pila (2011) André–Oort.
- Baker–Norine (2007) *Riemann–Roch and Abel–Jacobi theory on a finite graph*; Lorenzini critical groups.
- Wormald (1995) differential-equation method; Molloy (2005) cores of random hypergraphs.
```
