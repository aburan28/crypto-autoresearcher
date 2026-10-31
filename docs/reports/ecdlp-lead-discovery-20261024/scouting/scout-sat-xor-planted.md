# Scout dossier: SAT/XOR solving, planted systems and proof complexity, applied to the ECDLP index-calculus bottlenecks

Field: SAT/XOR solving and phase transitions of planted random systems; proof-complexity lower bounds
(resolution, Res(⊕), polynomial calculus, cutting planes) and what they imply for CDCL+XOR and algebraic
decomposition oracles, including conflict pricing.

Scout run 2026-10-24 (second pass; it supersedes the earlier draft of this file from the same day). Read-only on
every repository. Everything written lives under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.
No candidate below moves an exponent below rho. Each is a decision: a proof that closes a branch, a computation
that decides a lead's own discriminator, or an instrument with outcomes mapped to dispositions.
The words "promising" and "breakthrough" are not used.

## 0. Status words and provenance

- **reproduced (this session)**: re-run in this session with the scripts in `scout/repro/`, which import the
  earlier run's exact-arithmetic engine `scout/pcdeg/pcdeg.py` / `pcmix.py` unchanged. Outputs are in
  `scout/repro/*.out`.
- **earlier-run output (on disk, not re-run)**: produced by the earlier pass of this scout. The files are
  `scout/pcdeg/*.out`. I did not produce these numbers. I report them as recorded and cite the file each time.
- **derived (this session)**: a written proof (§4), or arithmetic on counters that someone else recorded (§3.1 R5).
  Neither is a new measurement.
- **model**: a dense-Macaulay cost computation. It is never a measurement, and it is never a lower bound on all algorithms.
- **predicted**: an expectation. Each one carries a numbered heuristic (H1..H6) and a probability.
- Every citation is marked **retrieved** (I read the source text or abstract in this session) or **recalled**.

## 1. What was read

- `atlas/ATLAS.md`: all 267 lines, every family (open next steps, generic, ic-binary, ic-engine, ic-prime, transfer,
  structure, exotic). `atlas/KRMAP.md`: generic-rho and index-calculus rows.
  `docs/object-frame-ideation.md` §1–3, `agents/idea-generator.md` ("Search heuristics", "Obstructions as generative
  material"), and `docs/target-result-profile.md` Part A.
- `crypto-main/docs/ic/LEADERBOARD.md`: Tables A and B and the phase shares.
  `crypto-main/docs/bounds/FRONTIER.md`: the Koblitz and prime toy domains.
- Lead YAMLs, read in full: LEAD-ICE-sat-xor-pdp-oracle, LEAD-ICP-digit-presentation-solving-degree,
  LEAD-ICE-prime-field-semaev-solving-degree, LEAD-ICP-generic-table-decomposition,
  LEAD-ICP-algebraic-membership-factor-base, LEAD-ICE-charged-toy-ic-exponent-vs-rho,
  LEAD-ICP-prime-ic-constant-engineering, LEAD-ICB-decomposition-encoding-and-sat,
  LEAD-ICP-icperf-writability-boundary, LEAD-ICE-hybrid-guess-determine-l7, LEAD-ICE-generic-oracle-arity-cost-floor,
  LEAD-ICP-icperf-binary-pdp-solver, LEAD-ICE-descent-closure-degree-at-scale,
  LEAD-ICB-prime-degree-algebraic-decomposition, LEAD-ICP-coppersmith-smallroot-semaev,
  LEAD-ICE-relation-graph-rank-large-prime. Every other SO code's statement comes from its ATLAS row, which
  reproduces the YAML's obstruction.statement.
- Primary data for C3: `crypto-main/research/ecbench_sat_pdp_20261009/{README.md, count-qualified-main.table.md,
  count-qualified-main.resources.json, specs/count-qualified-main.json}`. Also `src/bin/ic/bench.rs`, for the
  meaning of the `koblitz-orbit` factor-base parameter.
- Ledger dedup: I grepped `ledger/.index/{proposals,hypotheses}.jsonl` only, never the directory. Terms: XORSAT, overlap gap,
  OGP, planted, proof complexity, polynomial calculus, Impagliazzo, subset sum, knapsack, binary value, Res(, parity
  decision, cutting plane, Nullstellensatz, resolution width, conflict pric, ns per conflict, backdoor, Tseitin,
  Grigoriev, degree lower bound.
  - No record cites Impagliazzo–Pudlák–Sgall, a characteristic-p subset-sum bound for polynomial calculus, Res(⊕),
    parity decision trees, or conflict pricing.
  - **Closest in-program precedent for T1: IDEA-20260903-e1e38b** (status proposed, novelty unverified; read this
    session). It uses the same Wilson inclusion-matrix rank theorem on a different object. It derives the **first fall
    degree** of the **direct** digit top form, d_ff = m2^{m−1} + ⌊(s − 2^{m−1})/2⌋ + 1. That result is conditional on
    Wilson (snippet-retrieved there) and on H-TOP at m ≥ 3, and the record names "the solving degree, where the curve
    and the target first enter" as the residual open object. T1 differs in four ways:
    - it bounds the PC **refutation** degree, which lower-bounds every PC-simulable solver on UNSAT instances;
    - it covers the **chained** presentation, which e1e38b does not;
    - it needs no H-TOP and no top-form analysis;
    - its floor ⌈s/2⌉+1 is weaker than e1e38b's d_ff for the direct system.

    T1's novelty is **unverified**: the characteristic-p transfer is short enough to be folklore.
  - The PC-degree **instrument** exists as H-PCD-03be5a / H-ECDLP-29f047 (specified or proposed, never run).
  - The (m−1)l "ideal-XG" enumeration law exists as IDEA-20260926-b11cb1 and IDEA-20260904-96c4f3.
  - 2-core stopping exists as IDEA-20260814-a67a1d and H-ICEX-760fd5.
- `tools/lead_atlas.py --match` and `tools/build_frontier_map.py --match` were run on every phrasing in §6, and the
  hits are recorded there.

## 2. External ingredients and provenance

| ingredient | statement used | provenance |
|---|---|---|
| Impagliazzo, Pudlák, Sgall, "Lower bounds for the polynomial calculus and the Groebner basis algorithm", ECCC TR97-042 (1997); Comput. Complexity 8 (1999) | Thm 4.1: for nonzero reals c_i, m − Σ c_i x_i has no PC refutation of degree ⌈n/2⌉. Lemma 4.2: for multilinear p of degree k < ⌈n/2⌉, the multilinear reduction of (m − Σ c_i x_i)·p has degree k+1. The proof uses full row rank of the k-set vs (k+1)-set inclusion matrix, citing Gottlieb 1966. §5: degree bounds give monomial-count bounds for Gröbner implementations. | **retrieved**: full text read this session (pp. 1–2, 7–9, 11–12) from the ECCC download |
| D. H. Gottlieb, "A certain class of incidence matrices", Proc. AMS 17 (1966) | the inclusion matrix D_k^n has full rank over the reals | **retrieved as the citation in IPS97, ref. [4]**; content not read |
| R. M. Wilson, "A diagonal form for the incidence matrices of t-subsets vs. k-subsets", European J. Combin. 11 (1990) | rank over F_p of W_{t,k}(n) = Σ_{i ≤ t, p ∤ C(k−i, t−i)} (C(n,i) − C(n,i−1)) for t ≤ min(k, n−k). At k = t+1: full row rank iff p > t+1 | **recalled**. The specialisation was checked numerically this session at 174 (n, k, p) cells, n ≤ 10, p ≤ 13, with 0 mismatches (`repro/wilson.out`) |
| Clegg, Edmonds, Impagliazzo, STOC 1996 | a Gröbner computation that refutes within degree D is a degree-D PC refutation | citation **retrieved** (IPS97 ref. [3], used in Def. 1.1); the simulation's content is **recalled** |
| Behera, Limaye, Ramanathan, Srinivasan, arXiv 2506.16397 (2025) | Lemma 2.2: for β in a proper extension field and random α, the multilinear inverse of Σ α_i x_i − β has full degree n w.h.p. This is a functional/IPS degree bound, not a PC bound. It is the nearest published positive-characteristic subset-sum degree result I found. | **retrieved** (abstract and Lemma 2.2 statement) |
| Itsykson, Sokolov, "Resolution over linear equations modulo two", APAL 171(1) 2020; "Lower bounds for splittings by linear combinations", MFCS 2014 | tree-like Res(⊕) = DPLL that splits on F_2-linear forms; exponential lower bounds on Tseitin and PHP formulas | **retrieved** (bibliographic record and summary) |
| Gryaznov, Ovcharov, Riazanov, arXiv 2404.08370 (2024) | Prover–Delayer games give tree-like Res(⊕) size lower bounds; applied to "extensible" formulas | **retrieved** (abstract) |
| Efremenko, Garlík, Itsykson, STOC 2024 | superpolynomial lower bounds for regular (DAG-like) Res(⊕) | earlier-run retrieval (search summary); **recalled** this session |
| Alekseev, Grigoriev, Hirsch, Tzameret, STOC 2020 (binary value principle) | BVP: Σ 2^{i−1} x_i = −1; semi-algebraic systems refute it in low degree | earlier-run retrieval (abstract); **recalled** this session |
| Williams, Gomes, Selman, IJCAI 2003 (backdoors) | strong backdoor B for a subsolver ⇒ DPLL cost ≤ 2^{\|B\|}·poly | **recalled** |
| Pipatsrisawat, Darwiche, AIJ 2011 | CDCL with restarts p-simulates resolution, so conflicts are proof lines | **recalled** |
| Caminata, Gorla (solving degree vs last fall degree) | solv.deg = max(d_F, max GB degree); for an inconsistent system GB = {1}, so d_F = Macaulay solving degree | **recalled** |
| Faugère, Safey El Din, Spaenlehauer 2011 (bilinear systems) | regularity bounds for affine bilinear systems | **recalled** (used only in kill K8) |
| Dinur, EUROCRYPT 2021; Lokshtanov–Paturi–Tamaki–Williams–Yu, SODA 2017 | polynomial-method solvers for degree-d systems over GF(2) in about 2^{(1−1/(2.7d))n} | **recalled** (used only in kill K9) |

## 3. Measurements and derivations

### 3.1 Produced in this session

**R1. Subset-sum PC degree in characteristic p** (reproduces and extends the earlier run's M1; `repro/repro_m1_m2.py` →
`repro/m1.out`, 84 s). Convention: PC over F_P with Boolean axioms in the multilinear quotient. V_D is the least
subspace of degree-≤D multilinear polynomials that contains the axioms and is closed under x_j·(·) on its degree-≤D−1
elements. PC degree = least D with 1 ∈ V_D.

| family | p | s | targets ρ | PC degree measured |
|---|---|---|---|---|
| binary weights 2^j | 65521 | 2..9 | 2^s, and −1 (the BVP) | ⌈s/2⌉+1 in all 16 instances |
| same, SAT control ρ = 3 | 65521 | 2..9 | — | no refutation (correct) in all 8 |
| all-ones weights | 65521 | 2..9 | s+1 | ⌈s/2⌉+1 in all 8 |
| random weights, seed 2026 (the earlier run used seed 11) | 65521 | 3..8 | random non-subset-sums, 3 per s | ⌈s/2⌉+1 in all 18 |
| binary weights, **every** out-of-range ρ | 17, 37, 41, 67, 97, 131, 257, 521 | 4, 5, 5, 6, 6, 7, 8, 9 | all 1+5+9+3+33+3+1+9 = 64 | ⌈s/2⌉+1 in all 64 (p = 41, 97, 521 are new) |

**R2. Chained digit system** {S_3(x_1,x_2,u_1), S_3(u_{k−1},x_{k+1},u_k), S_3(u_{m−2},x_m,x_R)}. Here x_k = Σ 2^j d_{k,j}
uses Boolean digits, u are field variables, and the curve is y² = x³+3x+11 over F_65521. This reproduces the earlier run's
M5 with a fresh seed, 4242 (`repro/repro_chain.py` → `repro/chain_repro.out`). A returned degree certifies that the
draw is UNSAT, because a refutation exists. Planted SAT controls must return no refutation.

| (m, s) | (3,1) | (4,1) | (5,1) | (3,2) | (4,2) | (3,3) | (5,2) |
|---|---|---|---|---|---|---|---|
| PC degree, 2 UNSAT draws | 5, 5 | 5, 5 | 5, 5 | 6, 6 | 6, 6 | 7, 7 | launched (seed 777), not completed in this session; `repro/chain_52.out` empty |
| planted SAT control | none (ok) | none (ok) | none (ok) | none (ok) | none (ok) | none (ok) | |

Every reproduced cell equals the earlier run's value.

**R3. Wilson rank condition** (`repro/wilson_check.py` → `repro/wilson.out`). The k-set vs (k+1)-set inclusion matrix of
[n] has full row rank over F_p **iff p > k+1**. Checked at n ≤ 10, k ≤ (n−1)/2, p ∈ {2,3,5,7,11,13}: 174 cells, 0 mismatches.

**R4. Model thresholds** (I re-ran `pcdeg/scan_kappa.py`, unchanged). This is the dense-Macaulay MODEL
IC = B·max(1, m!p/B^m)·cols(ms bits, m−2 field vars, D)^ω + mB², with B = 2^s and rho = √(πp/4), for the chained field-u
presentation with D = 4 + κs flat in m. Model sub-rho cells exist iff:
- ω = 2: κ < 0.444 (256-bit), 0.800 (384-bit), 1.083 (521-bit);
- ω = 2.81: κ < 0.111, 0.400, 0.583.

At κ = 1 the margins are +53.7 (256), +16.4 (384) and −20.7 (521, at (m,s,D) = (73,12,16)) bits. At κ = 0.5 they are
+5.5 / −44.5 / −94.2. All of these reproduce the earlier run.

**R5. Conflict pricing of the recorded SAT arm** (`repro/c3_band.py` → `repro/c3_band.out`). This is arithmetic on the recorded
resource vector of session ECBS1hb55a1bdabf18 (crypto `research/ecbench_sat_pdp_20261009`, PROTOCOL-3, 40 measured runs
per arm, curve icv1-f2m17-tm101-00378d4e, log₂ r = 16.00, oracle `descent-algebraic:m=2`, CryptoMiniSat native XOR,
base `koblitz-orbit:divisor=0;1`).
- **The base has dim V = l = 9.** X^17 − 1 = (X+1)·f_1·f_2 over F_2 with deg f_i = ord_17(2) = 8, and indices 0 and 1 select
  1 + 8 dimensions. The run records 512 = 2^9 abscissae scanned per run, which confirms this.
- **Recorded counts.**
  - SAT arm: 34,963.343 GAE, plus 2,755,966 conflicts (unpriced) in 749 solver calls.
  - Strong signed-Frobenius rho: 40,950.357 GAE, plus 13,788 unpriced native ops (7,308 canonicalisations, 5,671 hashes,
    384 inserts, 425 queries).
  - Frobenius MITM: 174,894.135 GAE. Plain MITM: 3,967,256.501 GAE.
  - Propagations are not recorded at all. Pricing conflicts alone therefore understates SAT cost, so every number below
    errs toward SAT.
- **Pricing.** Every unpriced op on both sides is priced at w GAE.

| w (GAE per unpriced op) | 0 | 0.001 | 0.01 | 0.1 | 1 |
|---|---|---|---|---|---|
| SAT / matched strong rho | 0.854 | 0.921 | 1.52 | **7.34** | **51.0** |
| SAT / Frobenius MITM | 0.200 | 0.216 | 0.358 | 1.78 | 16.0 |

- **Crossing prices.** SAT and rho are equal at w* = 0.002183 = 1/458 ≈ 2^−8.84 GAE per conflict. SAT and Frobenius MITM
  are equal at 0.0508; SAT and plain MITM at 1.43.
- **Conflict law at this cell.** 3,679.5 conflicts per call is 2^11.85. That equals **7.19·2^{(m−1)l}**, and is 2^−5.15 of
  2^{ml}/m!. The SAT success rate is 385/749 = 0.514.
- **Totals.** Conflicts per run are 68,899 = 1.05·r.
- **L0 wall (descriptive only).** The recorded L0 walls read about 15.1 µs per conflict against about 120 ns per rho
  search GAE. That is an L0 reading on one macOS host, not admitted. **No disposition below uses it.**

### 3.2 Earlier-run outputs on disk (not re-run in this session)

- M2 (`pcdeg/run_s3_check.py`; the earlier draft records it): the m = 2 direct digit system S_3(L(d_1),L(d_2),x_R) gives PC degree
  5, 5, 6, 6 at s = 2..5. That equals the program's d_lf = 4 + ⌊s/2⌋ (EV-PFDR-99c699) cell for cell. The s = 6 cell timed out.
- M3 (`pcdeg/s3u.out`): unequal blocks (s_1, s_2) fit max(⌈s_max/2⌉+2, 4+⌊s_min/2⌋), on 12 cells × 3 draws.
- M4 (`pcdeg/chain.out`): the fixed-abscissa chain gives 2, 4, 4, 5, 5, 5 for m = 3..8.
- M5 (`pcdeg/chain_full.out`, `pcdeg/chain_full2.out`): the chained system at s = 1 gives 5, 5, 5, 6 for m = 3..6, from 2 draws
  each with planted controls. **m = 7 gives 6 from ONE draw with no planted control (806 s).** At s = 2: 6, 6 (m = 3, 4).
  At s = 3: 7 (m = 3).
  **The (3, 4) cell never completed** (`pcdeg/chain_s4.out` is empty). It was not relaunched.
- M6 (`pcdeg/scan_*.py`): model scans. The κ thresholds are reproduced in R4. The direct-presentation margins are
  +79 (256), +117 (384) and +157 (521) bits at ω = 1 with no Wilson term. With D = 5+⌊s/2⌋+δ(m−2), sub-rho cells exist
  iff δ < 0.000 / 0.048 / 0.131 at 256 / 384 / 521, ω = 2.

## 4. Theorem T1: the characteristic-p subset-sum degree barrier for Boolean-affine (digit) presentations

**Lemma K_p (IPS Thm 4.1 transferred to characteristic p).** Let F be a field of characteristic 0 or p. Let
c_1..c_n ∈ F^× and ρ ∈ F, and suppose char F = 0 or p > ⌈n/2⌉. Then {ρ − Σ c_i x_i} ∪ {x_i² − x_i} has no PC_F refutation of
degree ≤ ⌈n/2⌉.

*Proof.* IPS's proof (pp. 8–9) uses the field in exactly two places.
1. Row and column scaling of the inclusion matrix D_k^n by products of the c_i. This needs only c_i ≠ 0.
2. Full row rank of D_k^n for k ≤ ⌈n/2⌉ − 1, which IPS cite from Gottlieb over the reals. Over characteristic p,
   Wilson's theorem at (t, k) = (k, k+1) has binomials C(k+1−i, k−i) = k+1−i ∈ {1..k+1}. So the rank is full iff p > k+1,
   and for all k ≤ ⌈n/2⌉ − 1 this is p > ⌈n/2⌉ (checked numerically in R3).

Lemma 4.2 then holds verbatim. The coefficient vector of the degree-(k+1) part of ML((ρ − Σc_i x_i)·p) is
(top part of p)ᵀ·C, which is nonzero. The induction is field-free: every line of a degree-≤⌈n/2⌉ derivation reduces to
ML(p·(ρ − Σ c_i x_i)) with deg p ≤ ⌈n/2⌉ − 1, and 1 is not of that form. Neither the proof nor the statement needs
ρ ∈ F_p; ρ may lie in any extension field of characteristic p. ∎

Two remarks on the hypothesis:
- (a) If ρ ∈ F_p and the instance is UNSAT, Cauchy–Davenport (each {0, c_i} has two elements) gives n ≤ p − 2. So the
  hypothesis p > ⌈n/2⌉ is automatic, and it matters only for ρ in an extension field.
- (b) It cannot be dropped. Take characteristic 3, c_i = 1 and ρ ∈ F_9 ∖ F_3. Then
  (Σx_i − ρ)³ = Σx_i³ − ρ³ ≡ Σx_i − ρ³ mod the Boolean ideal, so a degree-3 derivation gives the constant ρ − ρ³ ≠ 0.
  That is a degree-3 refutation for every n (hand derivation).
  In general, the Frobenius gives degree-p refutations whenever the c_i ∈ F_p and ρ ∉ F_p. This is the "nearby object
  on which the conclusion fails" that the proof-architecture rule asks for. It is also the characteristic-2 story:
  Weil-descended F_2 systems are the p = 2 case, where membership is F_2-linear and the barrier is absent.

**Theorem T1.** Let p be prime with p > ⌈s/2⌉ (every cryptographic p), E/F_p nonsingular, m ≥ 2, and target x_R.
Present each leg as x_k = L_k(d_k) := a_k + Σ_{j<s} c_{k,j} d_{k,j}, with Boolean digits and nonzero weights. This covers
base-2 digits, windows [a, a+2^s), and binary-coefficient GAPs. Consider either system for an UNSAT target:
- (a) the direct system {S_{m+1}(L_1,…,L_m, x_R)} ∪ Bool;
- (b) the chained system {S_3(L_1, L_2, u_1), S_3(u_{i−1}, L_{i+1}, u_i), S_3(u_{m−2}, L_m, x_R)} ∪ Bool, where the u_i are
  field variables (no field equation).

Here **UNSAT means no solution over F̄_p with Boolean digits**, which is the only case in which a PC refutation exists.

Then every PC refutation over F_p, or over any finite extension of F_p, has degree ≥ ⌈s/2⌉ + 1, in two cases:
- for the chained system (b), at every s;
- for the direct system (a), whenever 2^{m−1} ≤ ⌈s/2⌉.

With unequal blocks the bound is ≥ ⌈s_max/2⌉ + 1. In the remaining direct regime, 2^{m−1} > ⌈s/2⌉, step 2 below does not
apply. There the relevant floors are the generator degree m·min(2^{m−1}, s) (EV-PFDR-f71d7f) and e1e38b's d_ff
(conditional), both far above ⌈s/2⌉+1.

*Proof.*
1. **Restriction.** Keep one leg k₀ free. Assign Boolean values to every other leg's digits. Choose the chain abscissae
   forwards from leg 1 and backwards from x_R, so that every chain equation not containing L_{k₀} holds. These values lie
   in a **finite extension of F_p**: each step solves a quadratic over the previous field, so the degree can double at
   each step.
   Substituting constants maps a degree-D refutation to a degree-≤D refutation of the residual {g(L_{k₀}(d))} ∪ Bool over
   that extension. A multiplication by a substituted variable becomes a scalar multiple.
   Here g is univariate of degree e (e = 2 in the chained case, e = 2^{m−1} in the direct case). No root of g is a value
   of L_{k₀} on the cube, since otherwise the full system would have an F̄_p solution.
   The restriction is chosen so that g is non-constant. In the chained case the x² coefficient of S_3(X, a, u) is
   (u − a)², and when u = a the X coefficient is −4(a³ + Aa + B). So g degenerates only if the chain value meets a
   rational 2-torsion abscissa, which is impossible when #E(F_p) is odd. A single non-degenerate restriction suffices,
   because the full system's PC degree is at least that of any restriction.
2. **Linear core.** Let ρ be a root of g, in a further extension of characteristic p. From ρ − L, derive
   g(L) = h(L)(L − ρ) in multilinear degree ≤ e: multiply by the monomials of h and multilinearise, as in IPS Lemma 3.1.
   Then apply the residual refutation. This gives a refutation of {ρ − L} of degree max(D, e). When e ≤ ⌈s/2⌉, Lemma K_p
   (which allows any extension field of characteristic p) forces D ≥ ⌈s/2⌉+1.
   - In the chained case e = 2. For s ≥ 3 that is ≤ ⌈s/2⌉. For s ≤ 2 the bound ⌈s/2⌉+1 ≤ 2 holds trivially, because every
     S_3 axiom has degree ≥ 2 (its u² coefficient is (L − L′)²).
   - In the direct case this is exactly the stated condition 2^{m−1} ≤ ⌈s/2⌉. ∎

**Scope line (twist decompositions).** Some targets have no F_p-decomposition but do have an F̄_p solution: twist
abscissae in the box, or intermediate sums over an extension. They have **no** algebraic refutation at all, and a
Gröbner solver returns spurious solutions on them instead of refuting. T1 says nothing about them. This is the prime-field
analogue of the quadratic-twist decompositions recorded in EV-ICPERF-390707. Every R2 draw that returned a degree is
certified F̄_p-UNSAT by that refutation.

**Corollaries.**
- **C-a (solver independence).** By the Clegg–Edmonds–Impagliazzo simulation (recalled), the following all reach degree
  ≥ ⌈s/2⌉+1 on every UNSAT instance, for every curve, target and monomial order:
  - Macaulay or XL at degree D, which realises the NS degree, and NS degree ≥ PC degree;
  - every F4, F5, MutantXL and Buchberger run, each of which is a PC derivation.

  With Caminata–Gorla (recalled), the last fall degree of an inconsistent system equals its Macaulay solving degree,
  so d_lf ≥ ⌈s/2⌉+1 too. At the IC operating point B ≈ (m!p)^{1/m}, this is ≥ (log₂ p)/(2m) + 1.
  **"d_lf bounded in s" is therefore impossible.** That is the reopening branch of
  LEAD-ICP-digit-presentation-solving-degree. Measured equality: subset sum = ⌈s/2⌉+1 at every tested cell (R1);
  the m = 2 direct system sits at +3 above the floor (M2).
- **C-b (scope).** T1 covers every PC-simulable solver on F_p-affine Boolean presentations. It does **not** cover:
  - lattice reduction (the Coppersmith lead);
  - cutting planes, SoS or pseudo-Boolean solvers (AGHT 2020: the BVP is easy for semi-algebraic systems);
  - carry-circuit encodings with auxiliary Boolean carry variables (the residual is then a circuit, not {g(L)});
  - enumeration.
- **C-c (cost consequence, MODEL).**
  - Direct presentation: already closed by the generator degree m·min(2^{m−1}, s) (EV-PFDR-f71d7f; M6 margins
    +79 to +157 bits).
  - Chained presentation: T1 alone does **not** close it. With the floor max(⌈s/2⌉+1, 4) the earlier run's scan reads
    −29.9 bits at 256-bit (model). That residual cell is candidate C2.
  - If the m = 2 residual floor 4 + ⌊s/2⌋ (M2, measured, not proven) were proven, restriction would lift the chained
    floor to 4 + s/2. That closes 256-bit in the model (threshold κ 0.444) but leaves 384 and 521 open.
- **C-d (characteristic contrast).** Over F_2, the one-block restriction of a Weil-descended system is F_2-affine and
  refutes at degree 1. T1's hypothesis is exactly what fails there. This explains, at theorem level, why "F_p digits as
  a Weil-descent analogue" cannot inherit the binary first-fall behaviour.

## 5. Candidates (ranked; prime field first)

### C1 (prime; B2 → B1). Theorem T1 decides the digit-presentation lead's reopening branch

- **Bottleneck.** B2: the prime-field S_3/S_4 solving degree, with beta_work 0.797 / 0.647 against the 0.30 gate. Its only live
  escape, the digit presentation, is B1's only non-enumerative oracle route. The digit lead's discriminator reads
  "a d_lf bounded in s strictly below the null is the first elliptic early fall over F_p and reopens the conditional
  cost table". EV-PFDR-99c699 could not support any growth statement.
- **Ingredient.** IPS 1999 Thm 4.1 / Lemma 4.2 (retrieved), transferred to characteristic p by Wilson 1990 (recalled;
  numerically checked, R3).
  The closest in-program precedent is IDEA-20260903-e1e38b (§1): same rank theorem, but it treats the first fall of the
  direct top form, conditionally. Novelty is unverified.
- **Mechanism.** §4. Restriction to one free leg turns any Gröbner-type refutation into a subset-sum refutation, which
  needs degree ⌈s/2⌉+1 in characteristic p > ⌈s/2⌉.
- **(Representation, operation set).** R1: x_k = L_k(d_k), Boolean digits with nonzero F_p weights. Σ_IC = translation by
  factor-base points (index calculus is Class I). Inside the oracle, Σ_PC = {multiplication by a variable, linear
  combination, restriction}.
  **Trichotomy: partial-action**, because the relation vector propagates only under translation by factor-base points
  (IDEA-20260806-c5d183). T1 is a statement about the oracle's refutation cost.
  **KN-OPEN-020 class:** implicit membership. T1 settles the Boolean-affine subclass for PC-simulable solvers.
- **SO codes touched (statements quoted with Scope) and the premise escaped.**
  - SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base: "A target-independent algebraic locus of degree d yields O(d)
    usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of
    degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for
    every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). … Scope: prime-order E/F_p,
    any base of size B."
    Escaped premise: "membership polynomial prod(x − v) of degree B". Digit membership costs degree 2 per digit.
    T1 is the matching obstruction for that escape: the price reappears as solver degree (log₂ B)/2 + 1.
  - SO-TABLE, LEAD-ICP-generic-table-decomposition: "Any decomposition oracle that enumerates or table-looks-up
    factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and
    T >~ sqrt(N) (Shoup); … Scope: any generic (enumeration/table) decomposition over F_p."
    Escaped premise: "enumerates or table-looks-up". The oracle is algebraic.
  - SO-GEN, LEAD-RHO-generic-sqrt-lower-bound: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs
    Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). … Scope: all generic algorithms, any field,
    any r."
    Escaped premise: "generic". The oracle reads coordinates. Likewise LEAD-ICE-generic-oracle-arity-cost-floor:
    "Scope: oracles that do not read curve coordinates algebraically".
  - Closed-known neighbour, LEAD-ICE-prime-field-semaev-solving-degree: "Naive Semaev IC over prime fields cannot beat
    generic methods (KR-IC-5931ee). The program reproduced it: … beta_work(B1) = 0.797 on interval and random bases and
    0.647 on subgroup bases against the 0.30 sub-rho threshold …". Its revisit_when ("membership equation has bounded
    degree independent of p … measured solving degree that stays flat across >= 3 field sizes") cannot fire at the IC
    operating point, because s grows with log p and the degree grows at least as s/2.
- **Tier X** (a statement about how the oracle's degree grows). **Predicted gain: 0.** This is a closure.
  - H1: Wilson's theorem as recalled (p = 0.98; 174/174 numerical cells agree).
  - H2: the Caminata–Gorla identity, needed only for the d_lf wording (p = 0.9).
- **First discriminating step** (zero compute, 1–2 days): an independent review of §4. In parallel:
  - (a) retrieve Wilson 1990 to move H1 to retrieved;
  - (b) optionally, state the characteristic-p Lemma 4.2 as a Lean target for fixed small n (formal lane).
- **Outcomes → dispositions.**
  - Review confirms → LEAD-ICP-digit-presentation-solving-degree: the bounded-d_lf branch is
    **closed_obstructed(theorem)**, scope "PC-simulable solvers, F_p-affine Boolean presentations, F̄_p-UNSAT
    targets, every curve, p > ⌈s/2⌉". The scope covers the chained presentation at all s and the direct presentation at
    2^{m−1} ≤ ⌈s/2⌉; the remaining direct cells sit under the generator-degree floor of EV-PFDR-f71d7f.
    The lead stays **open_next_step** only for the chained cost cell (C2). best_measured: "T1 floor ⌈s/2⌉+1 proven;
    measured subset sum = ⌈s/2⌉+1 (0 exceptions), m = 2 direct = 4+⌊s/2⌋, chained m = 3 = 4+s (s ≤ 3)".
    LEAD-ICE-prime-field-semaev-solving-degree stays **closed_known**, with T1 appended to its revisit_when.
  - Review finds a gap → **open_next_step**. best_measured is R1 (equality at every tested (p, s), ρ ∈ F_p), and the
    F_{p²}-target case needs an F_{p²} engine.
- **Cost.** Implementation: review 1 day (Lean optional, 3–5 days). Compute: none; R1 took 84 s.
- **Self-kill risk.** Low for the theorem, which is a two-place transfer of a published proof. It is medium for its
  reach: T1 alone does not close the chained presentation in the cost model, and says nothing about lattice, CP/SoS or
  carry-circuit solvers.

### C2 (prime; B1). Chained-arity degree law D(m, s): the one digit cell that T1 leaves open

- **Bottleneck.** B1. Under T1's floor, the chained digit presentation is the only presentation whose dense-Macaulay
  model still has sub-rho cells at deployed sizes (R4/M6). Measured so far:
  - D(3, s) = 5, 6, 7 for s = 1, 2, 3. That is slope κ(3) = 1, twice the m = 2 slope.
  - D(m, 1) = 5, 5, 5, 6 (m = 3..6), and 6 at m = 7 (one draw).
  - D(m, 2) = 6, 6 (m = 3, 4).
  - Reproduced this session: every cell with m ≤ 5, s ≤ 3 (R2).
- **Ingredient.** Solver-independent PC degree (CEI 1996 simulation, recalled) as the meter, with T1 as the proven floor.
  The reason to ask whether D depends on m at all is Alekhnovich–Razborov (recalled): for structured CNFs, refutation
  complexity follows branch-width, not constraint count, and the chain has a path-shaped constraint graph.
  The obstruction to bounded degree is the u-variables: their F_p domain carries the whole group state.
- **(Representation, operation set).** R1 digits for the legs, plus the auxiliary Semaev-chain abscissae u_i (field
  variables). Σ_IC is translation by factor-base points; the oracle's operations are the PC rules.
  **Trichotomy: partial-action** (Class I relation object). **KN-OPEN-020:** implicit membership.
- **SO codes.**
  - SO-ALGFB, SO-TABLE and SO-GEN: as in C1, quoted there, with the same escaped premises (degree-B membership,
    enumeration/table, generic).
  - Binary-arm vocabulary, LEAD-ICP-icperf-writability-boundary: "At the best viable arity the descended ANF exceeds the
    whole per-decomposition rho budget by … +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs.
    Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."
    The chained presentation escapes "unchained". A flat-in-m law would also be the writability lead's revisit
    condition ("chained S_3 at m = 5, 6").
- **Heuristics (predicted, all about a MODEL).**
  - H3 (p = 0.75): D keeps growing in m, at least +1 per doubling of m, or κ(m) > 1.08 for some m ≥ 4.
    Basis: the +1 step at m = 6 and κ(3) = 1. Under H3 every chained cell closes at ≤ 521 bits for ω ≥ 2. The earlier-run
    scan with κ = 1 and δ = 0.1 reads +52 bits at 521; logarithmic growth adds about 11 bits per extra degree at the
    m ≈ 73 optimum.
  - H3′ (p = 0.20): κ ≤ 1 and D flat for m ≥ 6. The m = 7 single draw (6 = D(6)) is why H3′ is raised from the earlier
    draft's 0.15. The model then keeps a 521-bit cell at −20.7 bits (m ≈ 73, s ≈ 12, D ≈ 16, ω = 2). The 256- and 384-bit
    cells close.
  - H3″ (p = 0.05): κ ≤ 0.8 and flat. This opens 384-bit as well, in the model.
- **Tier X. Predicted gain.** Most likely 0 (H3). Under H3′ only, a model-only 2^20.7 below rho at 521 bits (ω = 2);
  0 at ω ≥ 2.81 under every heuristic. Not a measurement.
- **First discriminating step.** Build a sparse F_p PC/Macaulay closure engine (or an msolve driver with Boolean digit
  equations and an RSS watchdog). Measure:
  - D(m, 1) for m = 8..12;
  - D(m, 2) for m = 5, 6;
  - D(4, 3) and the (3, 4) cell that never completed.

  Use ≥ 3 UNSAT draws plus a planted SAT control per cell, and a matched-shape random chained null (random bags of the same
  bidegree support). The dense engine here caps near 1.5·10^4 columns; m = 7 at s = 1 took 806 s per draw in the earlier run.
  This session's (5, 2) run was launched but did not complete in this session (R2).
- **Outcomes → dispositions.**
  - D(m, 1) ≥ 7 by m ≤ 12 and κ(4) ≥ 1 → chained digit presentation **closed_obstructed(cost_model)** at every deployed
    size. With C1, LEAD-ICP-digit-presentation-solving-degree closes as closed_obstructed(theorem + cost_model).
  - D(m, 1) = 6 flat through m = 12 and κ(4), κ(5) ≤ 1 → **open_next_step**. best_measured: "D = 4 + s at m = 3, flat at 6 for
    m = 6..12 (s = 1)". The next step is the SAT-regime (planted-target) solving degree, then an end-to-end toy IC at
    40–64 bits against matched rho, measuring F4 work rather than cols^ω.
  - The random null shows the same D → the law depends only on system shape. Record it, and keep the cost disposition
    as above.
  - The engine cannot reach m ≥ 10 at 128 GB → **exhausted_at_scale**, with the reached (m, s).
- **Cost.** Implementation: 3–5 days. Compute: hours per cell at m ≤ 6, s ≤ 3; the m ≥ 10 or s = 4 cells need 32–128 GB.
- **Self-kill risk.** High. Toy s ≤ 3 is far from the s ≈ 12 the model needs, and the chained cell survives only under H3′.
  It is kept because it is the last open digit cell after T1, and one sparse-engine ladder decides it.

### C3 (binary; B4). The recorded SAT counters decide the lead's own repricing discriminator

- **Bottleneck.** B4: "S/rho lower bound 0.854 with conflicts unpriced". The lead's next_action is to "reprice the
  native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per solver op". Its discriminator: "Priced S/rho below 1
  across the band would be a sub-rho toy row …; above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration
  at a constant and closes the lead as dominated by the pair table."
- **Ingredient.**
  - Conflicts are lines of the solver's refutation: CDCL p-simulates resolution (Pipatsrisawat–Darwiche, recalled), and
    Gauss-XOR conflicts are Res(⊕) lines (Itsykson–Sokolov, retrieved). So conflicts are work that cannot be priced at
    zero, and the §5a band applies to them.
  - The per-call law is a strong-backdoor count (Williams–Gomes–Selman 2003, recalled). In characteristic 2, x ↦ x² is
    F_2-linear, so fixing m−1 blocks leaves the descended S_3 F_2-affine in the last block. That gives the program's own
    ideal-XG (m−1)l law, IDEA-20260926-b11cb1.
- **Mechanism (derived, R5).** Using only recorded counters, at n = 17, m = 2, l = 9:
  - S_SAT/S_rho = 0.854 at w = 0, **7.34 at w = 0.1** and **51.0 at w = 1**;
  - crossing price w* = 2^−8.84 GAE per conflict (1/458);
  - SAT also loses to Frobenius MITM above w = 0.051;
  - propagations are uncounted, so these are closure-direction bounds.

  The lead's first clause (above 1 across the band) is met at w = 0.1 and w = 1. The second clause ("conflicts tracking
  2^(ml)/m!") is **not met as written**: the count is 2^−5.15 of that law. It is 7.2·2^{(m−1)l}, the (m−1)l-bit backdoor
  law. Total conflicts per run are 1.05·r, which is consistent with the product law (KN-FIND-aa2efc) at one size only.
- **(Representation, operation set).** R1: x ∈ the F_2-subspace V of F_{2^17}, Weil-descended to 9 bits per leg. Σ_IC is
  translation by factor-base points. The solver's operations are unit propagation, Gauss–Jordan on XOR rows, and
  conflict analysis (Res(⊕) inference). **Trichotomy: partial-action.**
- **SO codes.**
  - LEAD-ICB-decomposition-encoding-and-sat (measured): "Every SAT or enumeration method measured has per-attempt UNSAT
    cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; …) while beating rho
    needs alpha < m/2 - 1". This statement has no Scope clause. C3 adds the price axis that the measured statement
    leaves out. At m = 2 the native-XOR arm sits at alpha = m − 1 = 1 bit per unit l, below "alpha ~ m" but not below
    m/2 − 1 = 0.
  - SO-TABLE (binary), LEAD-ICB-generic-table-oracle: "Every oracle built from group operations and membership tests
    makes IC a generic-group algorithm with advice … Scope: all binary and Koblitz curves, one target, setup charged."
    Escaped premise: the SAT oracle reads descended coordinates algebraically. The closure here therefore comes from
    cost, not from that theorem.
  - SO-GEN: as quoted in C1, with the same escaped premise (the oracle is not generic).
  - LEAD-ICE-generic-oracle-arity-cost-floor: "Scope: oracles that do not read curve coordinates algebraically". This is
    escaped, and C3 is the priced analogue for the algebraic SAT oracle.
  - SO-FROB, LEAD-ICB-frobenius-orbit-factor-base: "… Rho gets the matching sqrt(2n) from the same automorphisms, so the
    matched gap is unchanged. … Scope: Koblitz/subfield curves over F_{2^n}, n prime …". This is respected rather than
    escaped: the SAT arm uses the Frobenius-stable orbit base and is compared with signed-Frobenius rho.
- **Tier I** (end-to-end priced, one size). It extends to X under H6.
- **Predicted gain: 0** (closure). The band numbers are derived, not predicted.
  - H6 (p = 0.8): total conflicts ∝ r^{1.0±0.15} across sizes, from the product law with the (m−1)l backdoor at balanced l.
    Then w*(r) ≈ 2^−8.84·(r/2^16)^{−1/2}, which is about 2^−65 GAE per conflict at ECC2K-130 size. Any positive conflict
    price keeps SAT-oracle IC above matched rho beyond toy size.
- **First discriminating step.**
  - (i) Zero compute: file R5 as the repricing that the lead's next_action asks for. The ns-per-conflict calibration
    becomes unnecessary unless a CDCL+XOR conflict could cost less than 1/458 of a group addition.
  - (ii) Re-run the frozen PROTOCOL-3 arms (rho-strong, ic-sat-xor, ic-mitm-frob) on the two larger toy Koblitz curves of
    the frontier set (log₂ r ≈ 17 and 21). Fit total conflicts against r.
- **Outcomes → dispositions.**
  - (i) alone → LEAD-ICE-sat-xor-pdp-oracle **closed_obstructed(cost_model)**. In the atlas's own vocabulary this is
    closed_dominated: by strong rho above w = 0.0022 and by Frobenius MITM above w = 0.051. Scope: n = 17 Koblitz, m = 2,
    conflicts counted, propagations uncounted. Record that the 2^(ml)/m! clause is replaced by the measured
    7.2·2^{(m−1)l}.
  - (ii) Slope ≥ 0.75 → upgrade the scope to an exponent statement: SAT-oracle IC total-work exponent ≥ 0.75 > 0.5 at
    every positive price.
  - (ii) Slope ≤ 0.6 → **open_next_step**, best_measured = the slope. That would be a sub-enumeration CDCL effect, to be
    fitted as alpha(m) at m = 3, 4, 5 per H-SATIC-5c526c.
- **Cost.** Implementation: none for (i); about 0.5 day to re-spec (ii). Compute: (i) none; (ii) about 1–3 hours, since the
  n = 17 SAT arm used 42 s of solve wall over 40 runs at L0.
- **Self-kill risk.** Low for (i): it is arithmetic on audited counters (the replay receipt lists 200/200 identical
  runs). The only escape is a conflict that costs under 1/458 GAE. Medium for (ii), since m = 2 is the most favourable
  SAT cell.

### C4 (binary; B4/B5 instrument). Exact tree-like Res(⊕) optimum of the UNSAT PDP: one number bounds every branching policy

- **Bottleneck.** B4/B5. Three open leads ask, each in its own vocabulary, whether some branching strategy beats the
  enumeration law:
  - LEAD-ICP-icperf-binary-pdp-solver: "branching order versus structure effect in DPLL";
  - LEAD-EXO-ml-learned-models: a learned WDSat branching policy at 16,097 conflicts against a default of 3,092;
  - LEAD-ICE-sat-xor-pdp-oracle: the tree-like part of the conflict law.
- **Ingredient.**
  - Tree-like Res(⊕) is exactly DPLL with linear splitting (parity decision trees) (Itsykson–Sokolov 2014/2020, retrieved).
  - Prover–Delayer games characterise tree-like Res(⊕) size (Gryaznov–Ovcharov–Riazanov 2024, retrieved). This is the
    proof route if the toy optimum is to become a theorem.
  - Strong backdoors (recalled).
- **Mechanism.** At toy cells, compute the exact minimum number of leaves over parity decision trees whose leaves close by
  the XG rule (degree-1 linearisation of the restricted descended system is inconsistent). Three query families:
  - (Q1) single bits: subcube DP over 3^N states, N ≤ 15;
  - (Q2) Q1 plus pairwise XORs within a block and across blocks at equal bit index. These are the splits that
    symmetric coordinates would exploit;
  - (Q3) all linear forms: DP over affine subspaces at N ≤ 8.

  Cells: m = 2 with l ∈ {5, 6, 7}, and m = 3 with l ∈ {3, 4, 5}; n ∈ {ml−1, ml, ml+1}; Koblitz and ordinary toy curves;
  20 UNSAT draws each. Include a planted positive control: a descended system with a hidden low-dimensional linear
  subvariety, where the optimum must be small. Compare with 2^{(m−1)l} and with the WDSat/CMS conflict counts on the same
  instances.
- **(Representation, operation set).** R1 descended bits. Σ = restriction by F_2-affine parity queries.
  **Trichotomy: partial-action.**
- **SO codes.**
  - LEAD-ICB-decomposition-encoding-and-sat, quoted in C3. "Every … method measured" is replaced by an optimum over a
    defined proof-system class.
  - SO-TABLE (binary) and SO-GEN: quoted in C1/C3. The premise escaped is the same as in C3 (the oracle reads
    coordinates algebraically).
- **Tier X** (decides the per-attempt exponent within tree-like DPLL(⊕)). **Predicted gain: 0.**
  - H4 (p = 0.75): the optimum lies within [1/2, 2] of 2^{(m−1)l} at every cell.
  - H4′ (p = 0.1): some cell is ≤ 2^{−l}·2^{(m−1)l}. Even then alpha ≥ m − 2 per unit l, which stays ≥ m/2 − 1 for every
    m ≥ 2. So no rho crossing follows under any outcome.
- **Outcomes → dispositions.**
  - Optimum ≥ 0.5·law everywhere (Q1 and Q2, and Q3 at N ≤ 8) → three sub-questions become **exhausted_at_scale** (N ≤ 15):
    the branching-order question in LEAD-ICP-icperf-binary-pdp-solver, the learned-branching sub-question in
    LEAD-EXO-ml-learned-models (any policy's count becomes a distance to the optimum), and the tree-like part of
    LEAD-ICE-sat-xor-pdp-oracle. DAG-like CDCL stays stated as open, since only regular Res(⊕) has lower bounds (EGI 2024).
  - Optimum ≤ 2^{−l}·law at some cell → **open_next_step** on all three: port the optimal split rule into WDSat and refit
    alpha(m).
- **Cost.** Implementation: 2–3 days (bitset Gauss with a subcube or affine-subspace DP). Compute: under a day for N ≤ 15.
- **Self-kill risk.** Medium–high. The result is tree-like only, and its families are restricted beyond N ≈ 8.
  IDEA-20260926-b11cb1 already predicts the outcome for block-order DPLL; C4 tests it over the whole tree-like class.

## 6. --match phrasings (hits from `tools/lead_atlas.py --match`, run this session)

| cand | own | plain-language | nearest closed lead's vocabulary |
|---|---|---|---|
| C1 | "characteristic-p subset-sum polynomial calculus degree floor for digit-presented decomposition" → ICB-prime-degree-algebraic-decomposition 14, ICE-descent-closure 14, digit lead 12 | "can a Groebner solver ever reach a bounded degree when the factor base is written in binary digits over a prime field" → ICB-quasi-subfield-polynomials 22, digit lead 21 | "prime-field Semaev Groebner solving degree law with a bounded-degree membership factor base" → ICE-prime-field-semaev-solving-degree 35, digit lead 21, ICP-algebraic-membership 19 |
| C2 | "chained Semaev digit system degree flat in arity" → ICE-chained-semaev-dreg-vs-semiregular 23, digit lead 21 | "does adding more summands raise the Groebner degree of chained decomposition over a prime field" → digit lead 18 | "chained Semaev system at m = 5 or 6 on ECC2K-130" → ICP-icperf-writability-boundary 20 |
| C3 | "price SAT conflicts in group-addition equivalents crossing price" → ICE-sat-xor-pdp-oracle 7, KR-IC-5765d2 6 | "how much would each SAT solver conflict have to cost before the SAT oracle loses to rho" → ICE-sat-xor-pdp-oracle 16, ICP-icperf-binary-pdp-solver 14 | "SAT or XOR solver for point decomposition beats rho" → ICB-decomposition-encoding-and-sat 26, KR-IC-5765d2 25 |
| C4 | "optimal parity decision tree DPLL XOR branching lower bound point decomposition" → KR-IC-5765d2 15, ICP-icperf-binary-pdp-solver 14 | "is there any branching rule for a SAT solver that beats brute force on point decomposition" → ICP-icperf-binary-pdp-solver 21 | "every SAT or enumeration method has per-attempt UNSAT cost with alpha about m" → ICB-decomposition-encoding-and-sat 9 |

`build_frontier_map.py --match` gave these top known-result rows:
- C1: KR-IC-5931ee (17);
- C3: KR-IC-5765d2 (6);
- C4: KR-IC-5765d2 (15);
- C2: KR-IC-fbdb61 (13).

None of these rows states a characteristic-p PC bound, conflict pricing or a Res(⊕) optimum.

## 7. Killed candidates (own kills, with reason)

- **K1. Overlap-gap / low-degree hardness of decomposition search** (Gamarnik; Hopkins; Kunisky–Wein–Bandeira; recalled).
  These obstruct stable or low-degree algorithms only. Gaussian elimination solves planted XORSAT inside the OGP regime.
  For generic oracles, SO-GEN already binds. No new bound on any named bottleneck.
- **K2. Planted-XORSAT 2-core / balanced-cycle stopping of the relation stage.** Duplicate: IDEA-20260814-a67a1d and
  H-ICEX-760fd5. The pipeline already stops when the target column is pinned. Linear algebra is 0.0–0.4% of Table B S.
- **K3. Factor-base sizing at the decomposability phase transition.** KN-FIND-007 conservation fixes the mean yield at
  binom(B+m−1, m)/N (SO-ALGFB). No lever.
- **K4. Semi-algebraic (cutting planes / SoS / pseudo-Boolean) oracle on the integer lift.** It escapes T1, since AGHT
  shows the BVP is easy for semi-algebraic systems. But the residual problem is a modular knapsack; its best known
  treatment is lattice small-roots (the Coppersmith lead, margin −0.048), and no cutting-planes advantage on modular
  knapsacks is known to me. Dominated, and duplicate.
- **K5. A univariate-membership PC bound for interval/random/subgroup bases.** Trivial: the membership axiom already has
  degree B. Closed_known (KR-IC-5931ee).
- **K6. Proof-complexity generators (ABRW 2004).** These need sparse, expanding, local generators, and the descended
  PDP is dense. Inapplicable.
- **K7. The 2-leg residual as corank-1 MinRank (support minors).** About n ≈ 3l ≪ l² equations, so linearisation fails;
  dominated by enumeration.
- **K8. The earlier draft's "restriction-branching sandwich" (its candidate B2).**
  - In characteristic 2, the descended S_3 is F_2-affine in each block separately, so the 2-leg residual is an
    overdetermined bilinear system: about 3l equations in 2l bits.
  - Its expected refutation degree at l ≤ 10 is ≤ 4 (FSS 2011 bilinear regularity, recalled; the earlier draft's own H5,
    p = 0.7). The lower arm therefore most likely certifies nothing.
  - Its other arm, k*, is already LEAD-ICE-hybrid-guess-determine-l7's own discriminator.
  - Killed as the weakest candidate.
- **K9. MQ polynomial-method solvers** (Lokshtanov et al. 2017; Dinur 2021; recalled) on the descended PDP. Per attempt
  they cost about 2^{(1−1/(2.7d))ml} = 2^{0.877ml} at d = 3. For m ≤ 7 that is worse than the char-2 (m−1)l backdoor, and
  above m/2 − 1 for every m. Dominated.
- **K10. A degree-p Frobenius refutation (Remark (b) in §4) as an attack primitive.** Its degree is p, which is larger than B.
  Useless.
- **K11. Low-degree "decomposability filter" on targets.** An exact filter must vanish on the ~p/m! decomposable
  abscissae, which forces degree ≥ p/m! (SO-ALGFB applied to the target set). Approximate filters are bounded by
  the character-sum flatness of LEAD-EXO-dl-character-sum-pseudorandom, which is exhausted. Duplicate.
- **(Promoted, not killed.)** The earlier draft's kill #6 ("closing B4 by the product law alone") becomes C3. With the
  recorded counters it decides the lead's own discriminator.

## 8. Fields searched with nothing usable for B1–B7

- Overlap-gap property and algorithmic thresholds of planted CSPs (Gamarnik 2021; Gamarnik–Sudan).
- The low-degree likelihood-ratio method (Hopkins 2018; Kunisky–Wein–Bandeira 2019). It is for noisy detection, and the
  decomposition problem is noiseless and algebraic.
- Random k-XORSAT satisfiability and 2-core thresholds (Dubois–Mandler 2002; Pittel–Sorkin 2016). Already implemented as
  pinned-column stopping.
- Cutting-planes lower bounds for random CNF (Fleming–Pankratov–Pitassi–Robere 2017; Hrubeš–Pudlák 2017). They have no
  modular-knapsack analogue for S(x) ≡ 0 (mod p).
- Bounded-depth / lifted Res(⊕) lower bounds (Efremenko–Itsykson; Bhattacharya–Chattopadhyay–Dvořák). These need
  gadget-composed formulas, which the PDP is not.
- MQ polynomial-method and crossbred solvers (K9; KR-IC-e847d1).
- B3 (prime IC constants), B6 (rho step cost, non-automorphism classes, GPU/FPGA) and B7 (transfers): no ingredient in this
  field.

## 9. Proof obligations and caveats

- §4 relies on Wilson 1990 as recalled (174/174 numerical agreement), and on CEI 1996 and Caminata–Gorla as recalled.
  The proof was transferred by me from the retrieved IPS text. It has not been independently reviewed.
- T1's scope excludes lattice, CP/SoS, carry-circuit encodings and enumeration (C-b). Every cost line is the dense-Macaulay
  model with ω ∈ {1, 2, 2.81}. The proven PC size bound at these degrees (IPS §5, exp(Ω(D²/N))) is negligible.
- C2's data rest on one curve, one prime and s ≤ 3. m = 7 is a single draw with no control. (3, 4) never completed.
  (5, 2) was launched in this session and did not complete.
- C3 rests on one curve and one host class (L0). Propagations are unpriced, and rho's canonicalisations are priced at the
  same w as conflicts. The L0 wall figures are descriptive and unused.
