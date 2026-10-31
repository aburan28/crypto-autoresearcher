# Scout dossier: polynomial method and Combinatorial Nullstellensatz, aimed at B1-B7 (round 2)

Field: the polynomial method in the broad sense. That covers Alon's Combinatorial Nullstellensatz,
Chevalley-Warning and Ax-Katz, Stepanov and Weil-type arguments, Dvir Kakeya, slice rank and Croot-Lev-Pach,
and the fewnomial theory of sparse polynomials over F_q. It also covers the algorithmic polynomial method
(Williams; Lokshtanov-Paturi-Tamaki-Williams-Yu; Bjorklund-Kaski-Williams; Dinur).

I applied these tools to two questions: whether decompositions exist and how many there are, and what
membership and refutation must cost.

Date 2026-10-24. Author: scout subagent. Every item is a proposal. Nothing here changes research state, and
nothing was written inside a repository. This file replaces the first-round draft, which is kept unchanged at
`scout/scout-polynomial-method.round1.md`. Section 1.3 says what changed and why.

**Provenance legend**
- **retrieved**: the source text was read in this session. Its file is under `scout/pm-refs/`.
- **recalled**: not read this session.
- **derived here**: an in-session derivation that nobody has reviewed.
- **PILOT**: my own toy computation. Scripts and outputs are in `scout/pmpilot/` and `scout/pilot/`. A
  pilot is not an evidence record.
- **PREDICTION**: a value that was not measured.

---------------------------------------------------------------------------------------------------------
## 0. Summary

Three candidates survive, and all three are prime field. B4-B7 got nothing from this field that a sibling
scout has not already covered or that survives arithmetic (section 5).

**C1 (B1). Measured input-size floor for G1. It decides the approved G1 oracle of
LEAD-ICE-charged-toy-ic-exponent-vs-rho without building it.**
- The lead is open_blocked only because the G1 backend of EXP-ICEX-153c34 has not been built and its S0
  smoke run was refused at the C-7 load gate.
- Any monomial-basis G1 path must hold, on every query, either the target-specialised f6 = S_6(., x_R) or
  its grid reduction fbar = f6 mod <g_V>. D-3 forbids the evaluation basis.
- I measured both:
  - fbar on the six frozen v4 fixtures is fully dense, |supp fbar| = L^5 on every target, and every
    coefficient depends on the target (U = |union_{i>=1} supp C_i| = L^5);
  - f6 itself has 99.99-100% of its 17^5 = 1,419,857 possible terms, on two fixture curves and one 22-bit
    curve.
- So for L <= 16 the per-query input is at least min(17^5, L^5) = L^5 terms, each needing at least one
  target-dependent multiplication, before Buchberger starts.
- On the spec's own arm-M metric (|U|·attempts_if_completed/(L+27) against T) that is **1,041x to 8,438x T**.
  These are exactly the numbers of the coordinator's design-time ceiling audit. That audit was conditional
  on density; C1 measures the density, so the audit's number becomes the exact floor.
- On 10 synthetic curves with the shape of the arm-X panel (L* = 5..13, 16-24 bits), fbar is dense on 40/40
  targets. The floor is 1.4e3x to 4.2e4x T. The per-success floor scales as q·L^5/|S5|, so the arm-X
  membership exponent is >= 1 (PREDICTION for the frozen panel).
- The hypothesis admits "a measured cost floor of G1 as implemented". C1 is a floor of every monomial-basis
  path. It becomes the "as implemented" form only after a counter check on the charged code (C1 step 3).
  - Read-only side flag: the S0 code g1_s0.py does not count the specialisation or reduction multiplications
    (SparsePoly arithmetic bypasses Field.mul).
  - Its root extraction evaluates the basis at all of V^5.
- The floor is scoped to L <= 16, which covers every fixture of EXP-ICEX-153c34.

**C2 (B1, SO-TABLE's "test sub-linear in |F|"). Coset-partition ceiling on every sparse-polynomial
prefilter.**
- Ingredient: Bi-Cheng-Rojas, Theorem 1.1 (retrieved). The nonzero roots of a t-nomial over F_q are a union
  of at most 2·sqrt(t-1)·q^{(t-2)/(t-1)} cosets of two nested subgroups.
- I derive (Lemma C2-R) that any t-nomial prefilter on x(R) has net per-success gain at most
  rho(s)/(1 - 2·eta·kappa(s)/(phi|S|)). This holds for every precision and every recall.
- kappa(s) and rho(s) are coset-coverage numbers of the decomposable set S, and they are measurable.
- Under coset regularity the bound tends to 1 + o(1) whenever log|S|/log q > (t-2)/(t-1).
- PILOT at mu ≈ 0.8, t = 3: the bound falls 8.5 → 6.5 → 5.0 at 20/22/24 bits. Interval, random and
  subgroup bases all sit on the random null. A planted coset-union control is detected.
- This closes the high-yield regime for sparse prefilters. The residual is decomposable sets smaller than
  q^{(t-2)/(t-1)}.

**C3 (B2's open non-enumerative class; supporting instrument). Static-certificate support floor.**
- By CN Theorem 1.1 (retrieved), every Nullstellensatz, quotient-basis or dense-Macaulay refutation over a
  univariately presented factor base must carry NF(1/f), which has full support.
- The pilot shows support fraction 1.0000 in all of these:
  - m = 2, 3: 36 cells, re-run here and identical;
  - m = 5: 87 non-member targets;
  - L = 17, 19, 21: the regime where the input f has stopped growing (17^5 terms) but the certificate still
    has L^5.
- So static algebraic oracles cost at least (m!/2^m)·q per success, which is exponent 1.
- It covers what C1 cannot (L > 16, any static solver). It does not cover dynamic Buchberger/PC.
- Nearest siblings: query-communication C2 (a degree floor) and H-PCD-03be5a (PC-degree measurement). C3's
  separate quantity is size, not degree.

---------------------------------------------------------------------------------------------------------
## 1. Inputs, reproduction, and what changed from round 1

### 1.1 Read this session

- ATLAS.md (all families) and KRMAP.md (both areas).
- object-frame-ideation.md sections 1-3, plus sections 4-6.
- idea-generator.md "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md part A, LEADERBOARD tables A-D and phase shares, FRONTIER.md head.
- Lead YAMLs:
  - charged-toy-ic-exponent-vs-rho, prime-field-semaev-solving-degree, prime-ic-constant-engineering;
  - generic-table-decomposition, algebraic-membership-factor-base, digit-presentation-solving-degree;
  - the obstruction statement and revisit_when of all 20 SO-code leads (extracted verbatim to
    `scout/_so_quotes_pm.txt`).
- Ledger:
  - H-ICEX-6ca21f (statement, coordinator prior, HEUR-ICEX-6ca21f-1);
  - EXP-ICEX-153c34/specification.yaml (G1 definition D-1..D-6, arms M/N/X, panel rule, cost accounting);
  - EXP-ICEX-153c34/implementation/s0_gates_report.yaml (refused at C-7) and g1_s0.py (head);
  - TASK-20261001-768475/ceiling_audit_output.json;
  - EV-SDEG-4a1c3d (scope clause and resource check), EV-PFDR-1394a4 (head), H-PCD-03be5a.
- The sibling scout dossiers, for deduplication: additive-comb, algebraic-geometry-covers,
  algorithmic-nt-smoothness, arithmetic-statistics, coding-isd, commutative-algebra, hpc-constants,
  lattice-smallroot, padic-tropical, query-communication, sat-xor-planted.

### 1.2 Reproduction of round-1 pilots

All four round-1 pilot scripts were re-run this session (outputs in `scout/pilot/rerun/`).
- grid_ns_support, controls and member_targets are byte-identical to round 1.
- coset_coverage differs only by six import-time print lines from coset_concentration.py. Every data row is
  identical.

So the round-1 numbers quoted below are now reproduced by me.

### 1.3 What changed, and why

- **Round-1 C3 (Bezout-on-translates agreement bound) is killed as a duplicate** (K-D1).
  - scout-additive-comb AC-2 proves the same bound, |S| <= 2·sqrt(d_E·N) + 3 with d_E = 2d, which is
    sqrt(8dN) + 3. It also measured A(1).
  - scout-coding-isd C2 targets the same lead.
  - The B6 corollary is covered by query-communication C4. The B7 corollary is covered by additive-comb
    AC-1, arithmetic-statistics C1 and padic-tropical C1.
- **Round-1 C2 (Kelley, high precision only) is replaced.**
  - Kelley's scope, "false positives < C_min/2", excludes almost every useful prefilter.
  - The binding ingredient is the Bi-Cheng-Rojas partition, which I re-read in the PDF. The abstract
    rendering mangles the exponent: it prints (t-2)(t-1) where the paper means (t-2)/(t-1).
  - Lemma C2-R covers all precisions and recalls.
- **Round-1 C1 is split.** The G1 decision became C1, with a new measurement. The static-class
  Nullstellensatz floor became C3, with new m = 5 and L > 16 data and its priors named.
- **The IPS knapsack degree bound for digit presentations is not proposed.** It is covered by
  commutative-algebra C1 and sat-xor-planted P1 (K-D2).

---------------------------------------------------------------------------------------------------------
## 2. Field scan (result, authors, year → use here → disposition)

| result | could do | disposition |
|:--|:--|:--|
| Combinatorial Nullstellensatz Thm 1.1, Lemma 2.1 (Alon 1999) [retrieved] | normal form mod <g_A(x_i)> is unique and degree-respecting; it fixes what a static certificate must contain | **C1, C3** |
| Fewnomial root structure: Bi-Cheng-Rojas Thm 1.1 (arXiv 1204.1113v2) [retrieved]; Kelley (arXiv 1602.00208) [retrieved, abstract] | roots of a t-nomial are a few cosets, so a sparse target test forces coset structure in S | **C2** (BCR binding; Kelley superseded) |
| BCR sub-linear root detection as an oracle [retrieved] | decide "f has a root" in q^{(t-2)/(t-1)+o(1)} | killed K2 |
| Chevalley-Warning, Warning, restricted-variable CW (Brink; Clark-Forrow-Schmitt) [recalled] | existence of decompositions | killed K3 |
| Ax-Katz [recalled] | divisibility of decomposition counts | killed K4 |
| Croot-Lev-Pach, Ellenberg-Gijswijt, slice rank (Tao) [recalled] | compress the decomposition tensor | killed K5 |
| Dvir Kakeya; method of multiplicities [recalled] | no Kakeya structure | empty K6 |
| CN Thm 1.2, Alon-Furedi [retrieved for Thm 1.2] | existence of decompositions via non-vanishing | killed K7 |
| Stepanov (Heath-Brown-Konyagin; Corvaja-Zannier; Shkredov-Vyugin) [recalled] | subgroup and coset coincidence caps | killed K8, K16 |
| Determinant method (Bombieri-Pila; Heath-Brown; Walsh) [recalled] | small-box point counts | killed K9 (dominated by the lattice scout and the Coppersmith lead) |
| Polynomial-method incidences (Guth-Katz, Rudnev, Stevens-de Zeeuw); Elekes-Szabo (2012); Tao (2015) [recalled] | caps on S_3 solutions on grids; coincidence harvest | killed K11 |
| Algorithmic polynomial method (Williams 2014; LPTWY SODA 2017; BKW ICALP 2019; Dinur EUROCRYPT 2021) [recalled] | batch or restricted-domain solving | killed K1, K13, K14 |
| Kedlaya-Umans fast multipoint evaluation / modular composition (SICOMP 2011) [recalled] | evaluate S_{m+1} on grid × targets; evaluation data structures | killed K12, K15 |
| Impagliazzo-Pudlak-Sgall knapsack PC degree (1999) [recalled; retrieved by siblings] | digit-presentation degree floor | duplicate of siblings (K-D2) |
| Lange-Winterhof (COCOON 2002) interpolation degree [recalled] | log-agreement bound | duplicate of siblings (K-D1) |

---------------------------------------------------------------------------------------------------------
## 3. Standing obstructions quoted (obstruction.statement, Scope clause included, verbatim from the lead YAMLs)

- **SO-TABLE**, LEAD-ICP-generic-table-decomposition [theorem]:
  - Statement: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a
    generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup);
    with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho
    even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99
    (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48,
    0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic
    (enumeration/table) decomposition over F_p."
  - revisit_when: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at
    arity m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|."
- **SO-TABLE** (binary), LEAD-ICB-generic-table-oracle [theorem]: "Every oracle built from group operations
  and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and
  Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat
  sqrt(r/2n) in total work; ... Scope: all binary and Koblitz curves, one target, setup charged."
- **SO-ALGFB**, LEAD-ICP-algebraic-membership-factor-base [theorem]: "A target-independent algebraic locus of
  degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and
  membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean
  per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain
  <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact
  mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows
  deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
- **SO-GEN**:
  - LEAD-RHO-generic-sqrt-lower-bound [theorem]: "Shoup/Nechaev generic-group lower bound: any generic
    algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in
    this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope:
    all generic algorithms, any field, any r."
  - LEAD-EXO-augmented-oracle-ggm [theorem]: "Each named oracle is GGM-simulable (jet, endomorphism O(1);
    incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate
    family at exponent 1/2 ... Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
- **B2**, LEAD-ICE-prime-field-semaev-solving-degree [literature]:
  - Statement: "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program
    reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and
    random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM
    checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field
    Groebner arm." It has no Scope clause.
  - The evidence record's scope_statement ends: "Nothing here is claimed at other m, factor-base sizes,
    extension fields, for non-enumerative (Groebner/algebraic) decomposition solvers, or at cryptographic
    size."
  - Its resource_check reads: "The open class left by the data is non-enumerative algebraic decomposition
    (EXP-ICEX-fa2b37, Groebner)."

Object-frame constraints applied throughout:
- A new arithmetic is a (representation, operation set) pair.
- IC is Class I, partial-action.
- Bounded-degree algebraic bases are scoped out (KN-OPEN-020). The open class is high-degree,
  implicit-membership, or target-dependent descriptions.

---------------------------------------------------------------------------------------------------------
## 4. Live candidates

### C1. Measured input-size floor of the G1 oracle: decides EXP-ICEX-153c34's arms M and X without building G1

**Bottleneck:** B1. "The approved non-enumerative oracle is unbuilt (LEAD-ICE-charged-toy-ic-exponent-vs-rho,
open_blocked)." The lead's next step is "Build the EXP-ICEX-153c34 backend (G1 membership, O5 oracle, ...)
and pass S0 gates". The S0 run of 2026-10-10 was "refused_infrastructure" (C-7 machine protection,
s0_gates_report.yaml), and no G1 query has ever run.

**External ingredient:** Alon, "Combinatorial Nullstellensatz", Theorem 1.1 and Lemma 2.1 [retrieved: author
PDF https://web.math.princeton.edu/~nalon/PDFS/null2.pdf, pp. 1-2 read this session; journal data CPC 8
(1999) 7-29 recalled].
- Theorem 1.1 (paraphrase): if f vanishes on S_1 × ... × S_n, then f = Σ h_i g_i with g_i = Π_{s∈S_i}(x_i - s)
  and deg h_i <= deg f - deg g_i.
- The proof reduces f by g_i and shows the reduced polynomial is 0 by Lemma 2.1.
- Lemma 2.1: "If P(x_1, x_2, ..., x_n) = 0 for all n-tuples ... then P ≡ 0", for P with x_i-degree <= t_i
  on grids with |S_i| >= t_i + 1.
- Consequence used here: the reduced representative fbar of f modulo <g_V(x_i)> is the unique polynomial with
  every deg_{x_i} < L that agrees with f on V^m. So its support is a property of f's values on the grid, not
  of the algorithm, and it can be computed by interpolation.

**Representation and operation pair.**
- Representation: abscissas as elements of the grid quotient R5 = F_p[x1..x5]/<g_V(x_i)> in the monomial
  basis. This is G1's own representation (D-2).
- Operation set: R5-module operations plus target specialisation x_R. The relation vector propagates under
  translation by factor-base elements only.
- Trichotomy: **partial-action** (IC Class I). G1 decides the branching event "R ∈ S5" that the meter
  prices.

**Lemma C1-a (input-size floor of monomial-basis paths; derived here, unreviewed).**
- Path independence:
  - A monomial-basis G1 must hold either f6(., x_R) (the S0 code does: f6_specialised_poly, then
    reduce_indicator_poly) or fbar_R. D-3 excludes the evaluation basis.
  - Measured on the fixture curves: |supp f6(., x_R)| = 1,419,737 to 1,419,857 of 17^5
    (`pmpilot/f6_unreduced_on_fixture_curves.out`) and |supp fbar| = L^5.
  - So the per-query input is >= min(|supp f6|, |supp fbar|) = L^5 for L <= 16.
- The rest of this lemma prices the fbar path, which is the cheaper of the two.
- In G1 as specified, every query R yields fbar_R = NF_{g_V}(f6(x1..x5, x_R)) ∈ R5 in the monomial basis.
  D-2: "then the normal form modulo g_V". D-3: "Arithmetic in R5 must stay in the monomial basis.
  Converting to evaluations at grid points ... is not G1".
- Write fbar_R = Σ_{i=0}^{16} x_R^i·C_i, where the C_i ∈ R5 are fixed per fixture (C_i is the normal form of
  the x_6^i coefficient of S_6).
- Each monomial in U := ∪_{i>=1} supp C_i carries a coefficient that is a non-constant polynomial in x_R.
  Producing it needs at least one F_p multiplication involving target-dependent data, unless one scales by
  repeated addition, which no implementation does.
- Under v4 C-3 (F_p multiplication 1 unit, additions free), the per-query S_specialise cost is therefore
  >= |U| units.
- On arm M's replayed stream: M_s >= |U|·attempts_if_completed/(L+27). attempts_if_completed is
  {12165, 1943, 547, 3341, 475, 19917}, from the spec.
- In expectation: >= |U|/y_exact per success, where y_exact = |S5|/q (O5).
- Scope: the lemma holds while deg_{x_i} S_6 = 16 >= L. For L >= 17, f6 is already reduced. Then
  |supp fbar| <= 17^5 stops growing with L, and only C3's certificate floor (static classes) remains.

**PILOT 1, the six frozen v4 fixtures** (`pmpilot/g1_fixture_floor.py`; input:
`experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json`, EXP-ICEX-aaccfc rows).
- Method:
  - V = {x in [0, B) : x^3 + ax + b a nonzero square}, with B the least integer such that B^5 >= p. L matches
    the spec's L_by_fixture at 6/6.
  - f6 is evaluated on V^5 through the exact Semaev resultant recursion (closed-form Res_{n,2}), then
    tensor-interpolated. The meter is allowed to do this; D-3 forbids it only inside G1's charged path.
  - C_i come from 17 x_R samples outside V.
  - |S5| is from exhaustive enumeration of signed 5-multisets, as O5 does.
  - Sanity: S_6 vanishes at a planted 5-sum on 5/5 fixtures where the planted sum was usable (b20-s21's draw
    hit V or O), and on 10/10 panel-shape curves.

| fixture | q | L | supp fbar (8 targets) | U | attempts (spec) | **arm-M floor M_s/T** | expected floor/T (y_exact) | |S5| | y_exact | f6-path floor/T (17^5 input) | audit B0/T | supp NF(1/f) |
|:--|--:|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|:--|
| b16-s21 | 60821 | 3 | 243 every target | 243 | 12165 | **1,040.7** | 1,069 | 146 | 0.00240 | 6.1e6 | 8,062.5 | L^5 on 7/7 non-members |
| b16-s22 | 63703 | 5 | 3125 every target | 3125 | 1943 | **2,088.7** | 1,854 | 1182 | 0.01855 | 9.5e5 | 3,516.2 | L^5 on 8/8 |
| b16-s23 | 47059 | 6 | 7776 every target | 7776 | 547 | **1,702.3** | 1,838 | 2630 | 0.05589 | 3.1e5 | 1,738.6 | L^5 on 8/8 |
| b20-s21 | 562333 | 7 | 16807 every target | 16807 | 3341 | **6,501.2** | 6,867 | 5418 | 0.00963 | 5.5e5 | 4,477.5 | L^5 on 8/8 |
| b20-s22 | 619537 | 11 | 161051 every target | 161051 | 475 | **8,438.1** | 9,162 | 45648 | 0.07368 | 7.4e4 | 1,902.1 | L^5 on 8/8 |
| b20-s23 | 909289 | 5 | 3125 every target | 3125 | 19917 | **5,666.9** | 7,004 | 1182 | 0.00130 | 2.6e6 | 9,789.0 | L^5 on 8/8 |

- T = 13·0.886·sqrt(q)/(L+27), the spec's own threshold. L^5 = 243, 3125, 7776, 16807, 161051, 3125.
- The arm-M column, |U|·attempts/(L+27)/T, reproduces the ceiling audit's grid_floor/T to the decimal
  (TASK-20261001-768475/ceiling_audit_output.json).
- The expected column uses 1/y_exact in place of realised attempts.
- The "f6-path" column prices the path the S0 code actually takes: hold the unreduced f6, at about 17^5
  terms per query.
- audit B0/T is the enumerative backend's measured cost, from the same audit.
- Of the C_i, the i <= 9 coefficients have L^5 - 1 terms at b16-s22, b20-s21 and b20-s22; the union U is L^5
  everywhere.

**PILOT 2, panel shape for arm X** (`pmpilot/g1_panel_density.py`).
- Synthetic curves with the frozen arm-X rule's shape: p window, B* = 9..26, L* = 5, 6, 8, 10, 13, two curves
  per size, four targets each.
- These are NOT the SHA-labelled frozen panel, which needs the Sage generator. Order was not checked, so
  q ≈ p.

| bits | L* | L^5 | supp fbar | U | L^5/|S5| | floor/T (q≈p) |
|--:|--:|--:|:--|--:|--:|--:|
| 16 | 5 | 3125 | 3125 ×4, ×4 | 3125 | 3.05, 2.64 | 1,588; 1,420 |
| 18 | 6 | 7776 | 7776 ×4, ×4 | 7776 | 2.91, 2.91 | 4,046; 3,827 |
| 20 | 8 | 32768 | 32768 ×4, ×4 | 32768 | 3.24, 3.24 | 7,835; 7,383 |
| 22 | 10 | 100000 | 100000 ×4, ×4 | 100000 | 3.44, 3.43 | 18,706; 19,612 |
| 24 | 13 | 371293 | 371293 ×4, ×4 | 371293 | 3.58, 3.55 | 41,581; 38,821 |

Per success, the floor is (L^5/|S5|)·q, where L^5/|S5| rises toward 5!/2^5 = 3.75. So the fitted exponent of
expected units per success along the panel is >= 1 plus a small positive term from that rise. PREDICTION
under H1.

**Relation to existing records (novelty: adaptation).**
- The coordinator prior of H-ICEX-6ca21f already expects failure. The arithmetic sits in its ceiling audit:
  "the floor is 1,041-8,438 times T on the six v4 fixtures; a symmetrised variant would still be 55-229 times
  T".
- That floor charged one unit per grid point under HEUR-ICEX-6ca21f-1, "Stated as a heuristic, not a lower
  bound for algorithms that skip the certificate". The heuristic is about the certificate h = 1/f6 being
  random-like.
- C1 removes the heuristic:
  - fbar and U are exactly L^5, and f6 is about 17^5, on every measured target.
  - So the per-query input of every monomial-basis path is >= L^5. The certificate does not enter.
  - The audit's numbers are now exact floors, not heuristic ones.
- The hypothesis admits "A charged-work lower bound that already exceeds a threshold is a measured cost floor
  of G1 as implemented, scoped to that implementation."
  - C1 is that kind of floor for every monomial-basis implementation.
  - It is "as implemented" only once the charged code is shown to count the specialisation (step 3).
- C1 also prices arm X. The prior gives arm X 0.60 "incomplete_or_inconclusive"; the panel-shape density
  removes that mass by arithmetic.
- The symmetrised variant (C(L+4, 5) quotient) was not measured here. The audit's 55-229x T for it stands as
  the design-time figure.

**SO codes touched.**
- SO-TABLE: premise "oracle that enumerates or table-looks-up factor-base elements". G1 does neither, so it
  is outside the premise. C1 shows it is still far above the rho threshold T and at membership exponent >= 1.
  This is a closure by a different, cost-model argument, not an escape.
  - Against the enumerative B0, the floor is comparable rather than dominant. The audit's grid_floor/B0 is
    0.13, 0.59 and 0.98 at L = 3, 5, 6, and 1.45 and 4.44 at L = 7, 11. So C1 does NOT claim that G1 loses to
    B0 at small L; it claims G1 cannot reach T.
- SO-GEN: premise "any generic algorithm". G1 reads coordinates, so the premise is escaped. C1 supplies its
  floor.
- SO-ALGFB: premise "mean per-target yield is binomial(B+m-1, m)/N for every base of size B". Not escaped.
  C1 uses the conserved yield (y_exact) as the denominator.

**Tier:** X. It decides an exponent route: the G1 membership exponent is >= 1.

**Predicted gain:** 0. This is a closure.
- Measured arm-M floor M_s/T >= 1,040.7 at the six fixtures.
- PREDICTION under **H1**: floor/T of 1.4e3-4.2e4 and membership exponent >= 1.0 on the frozen panel.

**First discriminating step** (about half a day; minutes of CPU):
1. Record Lemma C1-a and the six-fixture table. Done here, unreviewed.
2. Run the existing Sage generator `experiments/EXP-ICEX-153c34/implementation/panel_fixtures.py` to produce
   the frozen 20-fixture panel, byte-reproduce it (gate G0-1), and apply `pmpilot/g1_fixture_floor.py`'s
   meter: fbar, U, |S5|, floor/T.
3. Consistency check, only when C-7 admits it. It is needed for the "as implemented" form.
   - First route the specialisation and reduction through the counted Field.mul. In the current S0 code
     (g1_s0.py) SparsePoly.mul/add use raw Python arithmetic and Counters records only s_pairs and
     reductions.
   - Then run on b16-s21/s22 and check S_specialise >= |U| per query.

**Outcome to disposition:**
- |U| = L^5 on all 20 panel fixtures (predicted):
  - The G1 arm of LEAD-ICE-charged-toy-ic-exponent-vs-rho is **closed_obstructed(cost_model)**. Statement:
    "every monomial-basis G1 path holds >= L^5 terms per query; arm-M M_s >= 1.04e3·T on the six v4 fixtures;
    panel membership exponent >= 1".
  - The lead's next_action is no longer "build G1". By the lead's own discriminates clause ("an empty
    crossover across the reachable range turns the lane into an exhausted_at_scale record"), the lead
    becomes a candidate for **exhausted_at_scale** at 16-24 bits. B0/T is already 1.7e3-9.8e3 (audit).
    The coordinator decides.
  - Any successor non-enumerative oracle must avoid materialising a grid-dense polynomial and must meet
    query-communication C1's region (tau < m/2 - 1).
- Some panel fixture has |U| << L^5: **open_next_step**, with best_measured = min |U|/L^5 and the recomputed
  floor/T.
- The counted S_specialise is below |U| on some query: Lemma C1-a's reading of D-2 is wrong. **No
  disposition change** (instrument void).

**Cost:** implementation about 0.5 day (the meter exists); compute minutes.

**Self-kill risk:**
- Low on correctness. The density is measured directly and is exact on 88 targets (48 fixture + 40
  panel-shape).
- High on novelty. The coordinator's ceiling audit already had the arm-M number, conditional on density.
  C1's contribution is three things: the measured density, which makes it exact; the path-independent
  input floor; and the arm-X decision without a build.
- Scope is L <= 16 only.

**--match** (env exported; full output in `scout/match-polynomial-method-r2.txt`):
- own: "input normal form of the target-specialised summation polynomial modulo the factor-base polynomials
  is dense, so the Groebner membership oracle costs L^5 per query before Buchberger starts". Top hits:
  LEAD-ICP-construction-normal-form 21, KR-IC-5a43e5 15, LEAD-ICE-rootfind-pairtable-oracle 11.
- plain: "the approved algebraic membership oracle has to write down a polynomial as large as brute-force
  enumeration for every target, so it cannot beat rho at the toy fixtures". Top hits:
  LEAD-ICE-generic-oracle-arity-cost-floor 18, LEAD-ICP-algebraic-membership-factor-base 14,
  LEAD-ICE-charged-toy-ic-exponent-vs-rho 12.
- obstruction vocabulary: "non-enumerative decomposition oracle that is not a generic time/memory trade-off
  but whose per-attempt cost T_dec exceeds the enumeration of factor-base elements". Top hits:
  LEAD-ICE-generic-oracle-arity-cost-floor 17, LEAD-ICP-generic-table-decomposition 16.
- No row forecloses "dense normal form of the target-specialised S_6 modulo g_V".

---------------------------------------------------------------------------------------------------------
### C2. Bi-Cheng-Rojas coset-partition ceiling on every sparse-polynomial prefilter of the decomposition test

**Bottleneck:** B1 through SO-TABLE's revisit_when, "a decomposition test sub-linear in |F|". In
query-communication C1's region, a cheap prefilter is the only way a non-generic test could lower the
per-trial exponent tau.

**External ingredient:** J. Bi, Q. Cheng, J. M. Rojas, "Sub-linear root detection, and new hardness results,
for sparse polynomials over finite fields", arXiv:1204.1113v2 (2012), **Theorem 1.1** [retrieved: PDF read
this session, `pm-refs/bcr/`; ISSAC 2013 venue recalled]. For f = c_1 + c_2 x^{a_2} + ... + c_t x^{a_t} of
degree < q:
- "letting δ := gcd(q - 1, a_2, ..., a_t) and η := sqrt(t-1)·((q-1)/δ)^{(t-2)/(t-1)}, the entire set of
  nonzero roots of f in F_q is a union of at most 2η cosets of two proper subgroups S_1 ⊆ S_2 of F_q^*,
  where |S_1| = δ".
- The exponent is (t-2)/(t-1). The proof of Lemma 3.1 gives δ' <= sqrt(t-1)·N^{(t-2)/(t-1)}, and the
  abstract states the method is "sub-linear in q when t is fixed".
- Kelley (arXiv 1602.00208) [retrieved, abstract]: "2 (q-1)^{1-ε} C^ε" root bound. Superseded here.

**Lemma C2-R (net-gain ceiling; derived here, unreviewed).**
- Setup:
  - S ⊂ F_q^* is the set of decomposable target abscissas, with density δ_S = |S|/(q-1).
  - f is a nonzero t-nomial used as a prefilter: run the exact test only when f(x(R)) = 0.
  - S' = S ∩ Z(f), with recall φ = |S'|/|S|.
- Definitions:
  - κ(s) := max |S ∩ K| over cosets K of subgroups of order < s;
  - ρ(s) := max |S ∩ K|/(δ_S |K|) over cosets of order >= s.
- By BCR, Z(f) ∩ F_q^* = K_1 ⊔ ... ⊔ K_n with n <= 2η, each K_i a coset. For every s:
  φ|S| <= n·κ(s) + ρ(s)·δ_S·Σ|K_i| <= 2η·κ(s) + ρ(s)·δ_S·|Z(f)|.
- So the net per-success saving G := φ(q-1)/|Z(f)| satisfies **G <= ρ(s)/(1 - 2η κ(s)/(φ|S|))** for every s
  with 2ηκ(s) < φ|S|.
- Any precision and any recall are covered. η <= sqrt(t-1)·q^{θ_t}, with θ_t := (t-2)/(t-1).

**Corollary (under H2, coset regularity).**
- H2: κ(s_0) = O(log q) and ρ(s_0) = 1 + o(1) at s_0 = C·log q/δ_S.
- Then G <= 1 + o(1) whenever φ|S| >> q^{θ_t}·log q, i.e. whenever μ := log|S|/log q > θ_t.
- In IC terms (query-communication C1 region, j-sum split):
  - A prefilter can help only at parameters with m·β <= θ_t, where the decomposable set is smaller than the
    t-nomial's isolated-root capacity. There the required gain is still >= q^{1/2 - (j-1)θ_t/m}.
  - Table B's m = 2 (β = 1/3, μ = 2/3 > 1/2): trinomial prefilters cannot help.
  - Balanced m = 4 (β = 1/5, μ = 0.8): t <= 5 is excluded, t = 6 ties.
  - At m = 4, trinomials would need gain >= q^{1/4} on a set of size <= q^{1/2}. That residual is open.

**Representation and operation pair.**
- Representation: R1, x(R) ∈ F_p.
- Operation set: power maps x → x^e and F_p-linear combination, i.e. sparse evaluation at O(t log q) cost.
  Translation is not used.
- Trichotomy: **coordinate-dependent**. The test is a function of the representation of R. IC remains Class
  I around it.

**PILOT** (`pmpilot/bcr_coverage.py`; outputs bcr_coverage_smooth.out and bcr_coverage_refined.out).
- Primes: chosen with the most divisors of p-1 among about 4000 random primes per size, to stress-test.
- S = x(A ± A) with |A| = L, so that μ ≈ 0.795-0.798.
- Bases: interval, random-x and multiplicative-subgroup bases.
- Exact discrete-log table, and every subgroup of F_p^*.
- 24 equal-size random nulls per cell.

| bits | p | |S| | refined bound t=3, φ=1 (interval / random / subgroup) | null mean (same order) | t=3, φ=1/2 | t=4 |
|--:|--:|--:|:--|:--|:--|:--|
| 20 | 991201 | 56.7-58.8k | 8.47 / 7.75 / 10.15 | 8.02 / 8.12 / 8.60 | 15.1-18.7 (nulls 17.3-18.0) | vacuous (41-45, ≈ trivial) |
| 22 | 4125421 | 187k | 6.48 / 6.03 / 5.61 | 5.99 / 5.92 / 6.11 | 11.6-11.9 (nulls 11.7-12.0) | vacuous (42) |
| 24 | 14562241 | 518k | 4.97 / 4.85 / 5.10 | 5.17 / 5.05 / 5.02 | 8.7-8.8 (nulls 9.2-9.3) | vacuous (47) |

- Planted positive control: half of S replaced by 4 full cosets of a subgroup of order 7080 / 22919 / 63040.
  The instrument reports c_max = 1.0 at every size, so ρ = 1/δ_S and the bound becomes trivial, as it must.
- Large-coset coverage (D >= sqrt p) relative to density: 1.30-1.55 for S, against nulls of 1.33-1.46.
- Every structured base sits on its null. The bound falls about 25% per 2 bits.
- t = 4 is vacuous at toy size because η ≈ 1.7·q^{2/3} exceeds |S|/κ. That matches the condition μ > θ_4 =
  2/3 only asymptotically.

**SO codes touched.**
- SO-TABLE: premise "enumerates or table-looks-up factor-base elements". **Escaped**: one sparse evaluation
  of x(R), with no enumeration or lookup. This is exactly the revisit_when's "test sub-linear in |F|", and
  C2 closes its sparse sub-class in the μ > θ_t regime.
- SO-GEN / augmented-oracle-GGM: premise "Each named oracle is GGM-simulable". **Escaped**: a sparse
  predicate on the field coordinate is not one of the named group-theoretic oracles.
- SO-ALGFB: premise "A target-independent algebraic locus of degree d yields O(d) usable points ...;
  mean per-target yield is binomial(B+m-1, m)/N". Yield is **not escaped**; C2 moves only per-attempt
  cost. The description-degree premise is not touched, because Z(f) is a high-degree locus on the target
  side. That is the KN-OPEN-020 "high-degree" class transported from base to target.

**Tier:** X (scoped closure of an exponent route).

**Predicted gain:** 0 (closure).
- Measured toy, t = 3, μ ≈ 0.8: the bound falls 8.5/7.7/10.1 → 6.5/6.0/5.6 → 5.0/4.9/5.1 at 20/22/24 bits.
  The null means are 8.0-8.6 → 5.9-6.1 → 5.0-5.2.
- PREDICTION under H2: it keeps decreasing toward 1 as q grows, for every t with μ > θ_t.
- No specific large-q value is claimed. The random-model constants were not derived to that precision.

**First discriminating step** (about 1 day; hours of CPU):
- Ladder from 20 to 28 bits with highly composite p-1. Use a log table up to 2^26, or index calculus in F_p^*
  above that.
- Sets: S = x(Σ_m(F)) for m = 2, 3, 4, at the region-optimal β of each j-split and at β = θ_t/m, the boundary.
- t ∈ {3, 4, 5}, φ ∈ {1, 1/2, 1/4}. At least 100 nulls per cell, plus the planted coset-union control.
- Bases: interval, random, subgroup, coset, Dickson images.

**Outcome to disposition:**
- The refined bound is at the null level and decreasing with q in every cell with μ > θ_t:
  **closed_obstructed(theorem, scoped)** for t-nomial prefilters at μ > (t-2)/(t-1). Residuals: smaller
  decomposable sets, non-sparse short straight-line-program tests, and sparse tests in a changed coordinate
  outside the tested Moebius/Dickson families.
- The bound exceeds the null by a margin that grows with q for some base: **open_next_step**, with
  best_measured = the excess. Then build that t-nomial and price it end to end.
- The planted control is missed: **no disposition change** (instrument void).

**Cost:** implementation about 1 day; compute CPU-hours.

**Self-kill risk:** high.
- The closure is partial. It leaves the regime μ <= θ_t, where a filter would need gain >= q^{1/4} at m = 4.
- The prior for a positive outcome is about zero. The program's census reads: "every stable multiplicative
  coset statistic sits at the random level" (EV-ECDLP-81f4d4).
- Its value is to convert an exponentially large family (all t-nomials, about q^{2t}) into a finite,
  measurable coset census.

**Nearest priors:**
- IDEA-20260928-4e2be7 (coset and Dickson BASES with O(log d) membership) is the base side.
- IDEA-20261002-3722ca models B^θ attempt cost.
- The ledger has no hits for "fewnomial", "Kelley", "Bi-Cheng-Rojas" or "sparse prefilter".
- No sibling scout uses fewnomial theory.

**--match:**
- own: "Bi-Cheng-Rojas coset partition of roots of a t-nomial bounds the net gain of any sparse polynomial
  prefilter on the decomposable target set". Top hits: LEAD-EXO-invertible-hint-subset 8,
  LEAD-ICP-algebraic-membership-factor-base 8.
- plain: "a cheap sparse polynomial test on x(R) cannot tell which targets decompose unless the decomposable
  x-coordinates bunch up in multiplicative cosets". Top hits: KR-IC-5a43e5 8,
  LEAD-ICP-algebraic-membership-factor-base 8.
- obstruction vocabulary: "decomposition test sub-linear in |F| that does not enumerate or table-look-up
  factor-base elements". Top hits: LEAD-ICE-curve-presentation-invariance 9,
  LEAD-ICE-decomposition-probability-audit 8, LEAD-ICP-generic-table-decomposition 8.
  - The decomposition-probability-audit lead's "learned decomposability predictors" are prefilters. C2
    covers their sparse-polynomial sub-class only.
- All scores are low. No KR row forecloses a coset-partition argument.

---------------------------------------------------------------------------------------------------------
### C3. Static-certificate support floor on univariately presented factor bases (supporting instrument for B2's open class)

**Bottleneck:** B2.
- The open class left by EV-SDEG-4a1c3d is "non-enumerative algebraic decomposition (EXP-ICEX-fa2b37,
  Groebner)". Its scope clause excludes those solvers.
- C1 covers G1 only for L <= 16. C3 covers every static solver at every L.

**External ingredient:** Alon CN Theorem 1.1 and Lemma 2.1 [retrieved, as in C1].

**Lemmas (derived here, unreviewed; from round 1, re-checked).** A is the base's x-set, |A| = L, and
J = <g_A(x_1), ..., g_A(x_m)>. For a non-member target f = f_R, set μ* := NF_J(1/f).
- **N1 (exact static degree).** Division by J never raises degree (CN Thm 1.1). So every certificate
  1 = μf + Σλ_i g_A(x_i) has NF_J(μ) = μ*. The minimal Nullstellensatz degree is exactly
  deg f + deg μ*, because deg(μf) = deg μ + deg f and deg μ >= deg μ*.
- **N2 (quotient-basis linear algebra).** The coefficient vector expressing 1 in the rows {x^a·f mod J}, over
  the L^m standard monomials, is unique and equals μ*. So such a refutation touches >= |supp μ*| rows.
  Scope: standard-monomial multiples only.
- **N3 (sparse presentations).** For A = μ_k, monomials are characters. Exponent folding cannot create
  support, so every certificate has |supp| >= |supp μ*|.
- **N4 (dense Macaulay/XL).** The degree is >= L. That gives >= C(L+m, m) columns. This is the same floor as
  query-communication C2's degree argument.
- **N5 (members).** The cofactor of the eliminant certificate is forced at the L^m - |Z| non-zeros, so finding
  a decomposition costs as much as refuting one.

**Assembly.**
- Per success: >= s·L^m/y = s·(m!/2^m)·q, where s := |supp μ*|/L^m.
- Total: >= s·(m!/2^m)·q·L.
- That is exponent 1 + β for the static classes, against exhaustive search at 1.

**PILOT (mine; toy).**
- m = 2, 3 (round 1, re-run here and identical): 36 cells, p ∈ {10007, 20011}, interval, random and full
  subgroup bases. Support fraction 1.0000 and degree fraction 1.000 in every cell.
- Planted controls recovered exactly: f = x_1 gives 0.0333 = 1/30; f = x_1x_2 on μ_10 gives 0.0100.
- Members: 15/16 cells at or above the generic floor (L^m - |Z|)/L^m. The 16th is a tiny-L degeneracy where
  |proj Z| = L.
- m = 5 (new): |supp NF(1/f)| = L^5 on all 47 non-member targets of the six v4 fixtures, and on all 40 of the
  panel-shape curves.
- m = 5 in the unreduced regime (new; `pmpilot/static_floor_unreduced.py`, p = 4194319, an interval-type
  base):

  | L | input |supp f| | input/L^5 | |supp NF(1/f)| | certificate/L^5 |
  |--:|--:|--:|--:|--:|
  | 17 | 1,419,857 | 1.0000 | 1,419,857 | 1.0000 |
  | 19 | 1,419,857 | 0.5734 | 2,476,099 | 1.0000 |
  | 21 | 1,419,857 | 0.3477 | 4,084,101 | 1.0000 |

  - Six targets; one at L = 19 was a member and is skipped.
  - Above L = 16 the input stops growing at 17^5, but the static certificate keeps growing as L^5. This is
    the regime C1 cannot reach.

**Representation and operation pair.** As in C1: R_m in the monomial basis with module operations.
Trichotomy: **partial-action**.

**SO codes touched.**
- SO-TABLE: premise "enumerates or table-looks-up". Escaped, since an algebraic certificate is neither.
  C3 shows the static certificate is as large as enumeration, so it extends the closure to static algebraic
  classes.
- SO-ALGFB: premise "a size-B algebraic base has ... membership polynomial prod(x - v) of degree B". Not
  escaped. C3 is the cost statement for exactly that membership polynomial on every univariate grid, sparse
  ones included (N3).
- B2's scope clause: it covers the static part of "non-enumerative (Groebner/algebraic) decomposition
  solvers".

**Tier:** X (class closure). **Predicted gain:** 0. Static classes are at exponent >= 1 per success under
**H3** (s >= 0.99 on every univariate grid).

**First discriminating step** (1-2 days; CPU hours):
1. Extend the meter to m = 4 (S_5) and to coset and Dickson D_k(u, a) images, with L up to 64/24/12 for
   m = 2/3/4, three primes from 2^14 to 2^24, and at least 32 targets per cell (members included), keeping
   the planted controls.
2. The dynamic arm (the class C3 does not cover): run msolve/F4 on three cells per m and record its
   operation counts against L^m.

**Outcome to disposition:**
- s >= 0.99 everywhere: **closed_obstructed(theorem)** for static classes over univariate grids. It is
  recorded as a scope extension of B2's closed_known row.
- Dynamic counts >= c·L^m: **closed_obstructed(cost_model)** for those engines.
- Dynamic counts << L^m: **open_next_step**, with best_measured = the count slope in log L. This is the R1
  shortcut. For A = μ_k, PC can derive x^{2^j} - c^{2^j} in log k lines, so the static floor is not a
  theorem for dynamic proofs.
- Some family with s ~ L^{-γ}: **open_next_step**, with best_measured = γ. The predicted exponent is
  1 + β - γβ.
- A planted sparse-inverse control is missed: **no disposition change** (instrument void).

**Cost:** implementation 1-2 days; compute CPU-hours.

**Self-kill risk:** high (low marginal value).
- It closes static classes inside a lead that is already closed_known.
- Nearest priors and the delta from each, one line apiece:
  - query-communication C2: PC soundness gives degree >= membership degree. C3 gives SIZE, and it gives size
    for sparse presentations where a degree-based column count does not bind (N2, N3).
  - H-PCD-03be5a: a specified PC-DEGREE measurement. C3 is a closed-form static size floor, and it adds
    member targets (N5).
  - HEUR-ICEX-6ca21f-1: the same intuition, stated as a heuristic. C3 is a theorem for the static classes
    plus measured s.

**--match:**
- own: "Combinatorial Nullstellensatz normal form of 1/f on the factor-base grid has full support, so every
  static Nullstellensatz or quotient-basis certificate costs |A|^m". Top hits:
  LEAD-ICP-construction-normal-form 12, LEAD-ICP-full-width-arity-grid 9.
- plain: "any linear-algebra certificate that a target does not decompose over the factor base is as large
  as listing all m-tuples of the base". Top hits: LEAD-STR-class-representative-ic-selection 13,
  KR-IC-5a43e5 12.
- obstruction vocabulary: "eliminant degree and solving degree of non-enumerative Groebner algebraic
  decomposition solvers over F_p beyond the serial S_3 split". Top hits:
  LEAD-ICE-prime-field-semaev-solving-degree 28, LEAD-ICE-curve-presentation-invariance 17,
  LEAD-ICP-digit-presentation-solving-degree 13.
- No row forecloses "support of NF(1/f) on the grid".

---------------------------------------------------------------------------------------------------------
## 4b. Side flags for the coordinator (read-only observations, no action taken)

These come from reading `experiments/EXP-ICEX-153c34/implementation/g1_s0.py`, the S0-only code whose header
says "The charged protocol driver is deliberately absent".
- `f6_specialised_poly` builds the full target-specialised f6 by a Sylvester subset-DP over SparsePoly
  entries, and `reduce_indicator_poly` then reduces it.
  - SparsePoly.mul/add use raw Python arithmetic, not the counted Field.mul.
  - Counters records only s_pairs and reductions inside Buchberger.
  - If a charged driver reused these functions, S_specialise would be uncharged.
- `g1_membership` extracts roots by evaluating the basis at every point of itertools.product(V, repeat=5).
  That is an L^5 grid scan, which D-3 rules out of the charged path ("literally enumeration of V^5").
- Neither observation changes C1's floor, which holds for every monomial-basis path. Both matter for step 3
  and for any future charged run.

---------------------------------------------------------------------------------------------------------
## 5. Killed candidates (own kills first; duplicates second)

**Duplicates of sibling scouts.**
- **K-D1. Bezout-on-translates agreement bound (round-1 C3).**
  - It is the same theorem as scout-additive-comb AC-2: "|S| <= 2 sqrt(d_E N) + 3", with d_E = 2d giving
    sqrt(8dN) + 3. AC-2 also has A(1) measured.
  - scout-coding-isd C2 targets the same lead (LEAD-EXO-invertible-hint-subset).
  - The B6 corollary is covered by query-communication C4. The B7 corollary is covered by additive-comb
    AC-1, arithmetic-statistics C1 and padic-tropical C1.
- **K-D2. IPS knapsack PC-degree floor for digit presentations.** Covered by commutative-algebra C1 and
  sat-xor-planted P1, both with IPS retrieved. The digit d_ff's floor((s - 2^{m-1})/2) term is
  Wilson-inclusion-rank driven, as those dossiers show.

**Own kills, with arithmetic.**
- **K0. Round-1 C2 (Kelley high-precision scope).** Kelley gives a full coset of size
  C >= q^{1-(1-μ)(t-1)}/2^{t-1} inside Z(f). It is useful only when false positives are below C/2, which at
  μ = 0.8, t = 3 is q^{0.6}/8 against |S| = q^{0.8}. Superseded by Lemma C2-R.
- **K1. GF(2) polynomial-method solvers for the descended PDP (BKW 2019, Dinur 2021) (B4/B5).**
  - With N bits a solver costs 2^{cN} with c >= 0.69 (quadratic) or 1 - 1/(2.7d).
  - Beating rho needs alpha = c·m < m/2 - 1, i.e. c < 1/2 - 1/m. Dead at every m.
  - ECC2K-130 at m = 4 (chained): N ≈ 394, so 2^{273} against 2^{60.9}.
- **K2. BCR root detection as the oracle.** It costs q^{(t-2)/(t-1)+o(1)} per query, which is >= q^{1/2} at
  t = 3, above any per-attempt gate.
- **K3. Chevalley-Warning family for existence of decompositions.**
  - With x_i ∈ A the condition (p-1)·deg f < Σ(|A_i| - 1) fails by a factor of about p/(mL).
  - Unrestricted, it is trivial.
  - CW on target-dependent bases: the equation degrees exceed the variable count.
- **K4. Ax-Katz.** It needs #vars - Σdeg > 0. For the Semaev hypersurface, m - total degree < 0, so it is
  vacuous.
- **K5. Slice rank / Croot-Lev-Pach.**
  - The addition tensor of Z/N has slice rank N.
  - The binary descended indicator has degree >= 2n, against the < 3l/2 a bound needs.
- **K6. Dvir Kakeya / multiplicities.** There is no high-dimensional line structure.
- **K7. CN Theorem 1.2 for existence.** Going through 1 - f^{p-1} needs |A| > (p-1)·deg f/m.
- **K8. Stepanov coset caps.** The cap is about |H|^{5/3} against the random |H|^3/p, a ratio p^{1-4β/3} >=
  p^{2/3} at β = 1/4. Vacuous.
- **K9. Determinant method as a small-box enumerator.** It gives upper bounds only. The algorithmic form is
  Coppersmith (LEAD-ICP-coppersmith-smallroot-semaev; lattice scout).
- **K11. Incidence bounds and Elekes-Szabo for coincidence harvesting.**
  - Caps on S_3 solutions on A^3 are about n^{3/2} (Stevens-de Zeeuw / Rudnev type) or n^{2-η}
    (Elekes-Szabo). Both exceed the random rate n^3/p for n < p^{2/3}, so they cannot certify absence of
    excess (LEAD-ICP-coincidence-harvest-structured-base).
  - S_3 is in any case the group-law exception of Elekes-Szabo.
  - Over F_p, Tao's regularity versions need dense sets.
- **K12. Decomposable-target polynomial Φ_A plus fast evaluation or a Kedlaya-Umans evaluation data
  structure.** Space |S|^{1+ε} with polylog query is the folded table again: generic with advice.
- **K13. Williams-style polynomial method (probabilistic polynomials plus rectangular matrix
  multiplication).**
  - The predicate [f = 0] over F_p has degree p - 1.
  - Equality joins (MITM) are already linear by hashing.
- **K14. LPTWY/BKW restricted-domain solving over F_p.** These give q^{(1 - 1/O(d))·n}-type bounds whose
  savings need small q relative to the degree (recalled). For the restricted grid A^m inside F_p with
  q ~ 2^64 the predicate [x_i ∈ A] has degree L or q - 1, and nothing beats the L^m grid.
- **K15. Kedlaya-Umans multipoint evaluation of S_{m+1} over grid × targets.** Output-size bound = enumeration.
- **K16. Stepanov auxiliary polynomial as a sub-|H| algorithm.** Its degree is >= |H|.
- **K17. H-invariant degree bound for B6.**
  - ψ∘[a] - ψ∘[b] vanishes on G, so δ·(a^2 + b^2) >= N - 1. Pigeonhole on a subgroup H gives
    |a|, |b| <= sqrt(N/h), so δ >= ~h/2.
  - Straight-line cost is only >= log δ, so this does not close the lead. QC-C4 covers generic
    canonicalisers.
- **K18. CN floor transported to binary (writability).** The grid quotient mod a linearised L_V is the
  descended ANF basis up to a weight-triangular change. So the floor equals the already-measured
  writability wall (+40.8 bits on ECC2K-130). No new number.
- **K19. Special-j support reduction.** x → ζx also moves x_R, so per-target NF support is unchanged. The
  only gain is target-orbit folding, a constant matching rho's sqrt|Aut|.
- **K20. B3 from this field.** The Table B relation phase is (point addition + O(1) probe) per walked target.
  A prefilter or algebraic test cannot shrink an O(1) probe, and C2 already excludes trinomials at m = 2.
  No candidate.

---------------------------------------------------------------------------------------------------------
## 6. Fields searched but empty

- Slice rank, Croot-Lev-Pach, cap sets.
- Dvir Kakeya and the method of multiplicities.
- Chevalley-Warning, Ax-Katz, and restricted-variable CW, for existence and counting.
- Incidence geometry and Elekes-Szabo over F_p for the m = 2 join.
- GF(2) parity-counting solvers, and Williams/LPTWY algorithmic polynomial methods.
- Stepanov caps in the IC regime.
- The determinant method.
- Kedlaya-Umans fast evaluation.
- The polynomial method on B5 (Jacobian carriers, hybrid guess-and-determine), B6 step primitives, and B7
  Teske/F_{p^6}.

---------------------------------------------------------------------------------------------------------
## 7. Numbered heuristics

- **H1** (C1): for the Semaev S_6 specialisation and an interval-type or random-x base with L <= 16, fbar and
  U are dense (= L^5) on every target. Measured on 48 + 40 targets.
  - Rigorous bound paired with it: Lemma 2.1 makes fbar unique.
  - Distribution statement imitated: L^5 random values have a fully supported interpolant except with
    probability about L^5/p.
  - Validation: the frozen panel meter (C1 step 2).
- **H2** (C2): decomposable abscissa sets are coset-regular. For s_0 = C·log q/δ_S, κ(s_0) = O(log q) and
  ρ(s_0) = 1 + O(C^{-1/2}).
  - Rigorous bound: BCR Theorem 1.1.
  - Distribution statement imitated: a random set of density δ meets every coset of order >= s_0 in
    δ|K|(1 ± o(1)) points, with O(log q) points in smaller cosets.
  - Validation: the C2 ladder against at least 100 nulls. The toy data agrees with H2 at 20-24 bits.
- **H3** (C3): s = |supp NF(1/f)|/L^m >= 0.99 for every univariate grid presentation.
  - Rigorous bound: CN Thm 1.1 uniqueness.
  - Distribution statement imitated: the same random-interpolant argument as H1.
  - Validation: the C3 ladder. Measured s = 1.0000 on every non-degenerate cell so far.

---------------------------------------------------------------------------------------------------------
## 8. Citations

- N. Alon, "Combinatorial Nullstellensatz", Combin. Probab. Comput. 8 (1999) 7-29. Thm 1.1, Thm 1.2 and
  Lemma 2.1 **retrieved** (author PDF https://web.math.princeton.edu/~nalon/PDFS/null2.pdf, text extracted
  to `pm-refs/alon/null2.txt`). Journal data **recalled**.
- J. Bi, Q. Cheng, J. M. Rojas, arXiv:1204.1113v2, Thm 1.1 and Lemma 3.1 **retrieved** (PDF; text in
  `pm-refs/bcr/bcr.txt`). ISSAC 2013 venue **recalled**.
- Z. Kelley, arXiv:1602.00208, root bound **retrieved** (abstract page).
- Shoup (EUROCRYPT 1997); Corrigan-Gibbs and Kogan (EUROCRYPT 2018): **recalled** (cited through KR rows).
- Impagliazzo, Pudlak, Sgall, Comput. Complexity 8 (1999): **recalled** here (retrieved by sibling scouts).
- Elekes and Szabo, JAMS 2012; Tao, "Expanding polynomials over finite fields of large characteristic"
  (2015); Stevens and de Zeeuw (2017); Rudnev (2018): **recalled**.
- Williams (2014); Lokshtanov, Paturi, Tamaki, Williams, Yu (SODA 2017); Bjorklund, Kaski, Williams (ICALP
  2019); Dinur (EUROCRYPT 2021); Kedlaya and Umans (SICOMP 2011): **recalled**.
- Lange and Winterhof (COCOON 2002): **recalled**. Duplicate kill only.
- In-program: H-ICEX-6ca21f, EXP-ICEX-153c34 spec and implementation report,
  TASK-20261001-768475/ceiling_audit_output.json, EV-SDEG-4a1c3d, EV-PFDR-1394a4, H-PCD-03be5a,
  EV-ECDLP-81f4d4 (as quoted in the atlas). All **read this session**.

---------------------------------------------------------------------------------------------------------
## 9. Files

All paths are under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

- `scout-polynomial-method.md`: this dossier. `scout-polynomial-method.round1.md`: the round-1 draft.
- `pmpilot/g1_fixture_floor.py`, `.out`, `.json`: C1, six v4 fixtures.
- `pmpilot/g1_panel_density.py`, `.out`, `.json`: C1, panel-shape curves.
- `pmpilot/bcr_coverage.py`, `bcr_coverage_smooth.out`, `bcr_coverage_refined.out`: C2.
  `bcr_coverage.out` is the first run, on primes with few divisors, kept for transparency.
- `pmpilot/static_floor_unreduced.py`, `.out`, `_L21.out`: C3, the L > 16 regime.
- `pmpilot/f6_unreduced_on_fixture_curves.out`, `.json`: the unreduced f6 density on fixture curves b16-s21 and
  b20-s22 (C1, path independence).
- `pilot/` and `pilot/rerun/`: round-1 pilots and their reproductions.
- `pm-refs/alon/`, `pm-refs/bcr/`: fetched PDFs and extracted text (untrusted data, kept separate from the
  scripts).
- `match-polynomial-method-r2.txt`: lead_atlas and build_frontier_map --match output for the 9 phrasings.
- `_so_quotes_pm.txt`: verbatim obstruction statements and revisit_when for the 20 SO leads.
