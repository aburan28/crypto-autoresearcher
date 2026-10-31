# Scout dossier: query and communication complexity, generic-group and structured-generic-group lower bounds

Field: query and communication complexity; generic-group lower bounds and their time-space,
structured and non-adaptive refinements (Shoup 1997; Corrigan-Gibbs-Kogan 2018; Corrigan-Gibbs-
Henzinger-Wu SGGM, ePrint 2026/384; Dinur-Keller-Marmor, arXiv 2505.00894; function inversion and
3SUM-indexing time-space bounds), plus two neighbouring query-complexity tools: uniqueness and
sparsity of multilinear representations (Nisan-Szegedy), and heavy-Fourier-coefficient learning and
statistical-query (SQ) lower bounds.

Status of everything below. These are proposals and derivations. No experiment was run on any
curve of cryptographic size, and no repository was touched. This session I ran small scripts under
`scout/qc/`.
- The region check, the digit-writability models and the full-sumset model are cost models. Their
  outputs are model numbers, i.e. predictions.
- The H4 check and the invariant census are exact toy computations (p <= 2^61, N about 2^10). Their
  outputs are measured toy results, labelled as such. Heuristics are numbered H1..H9 in section 0.3.
Expected values are predictions.

This file replaces an earlier draft at the same path, written by a previous run of this workflow step.
I treated that draft as unverified input. Every number kept from it was re-derived or re-run here.
Section 6 lists what changed and why.

Read in full this session:
- ATLAS.md, all seven families.
- KRMAP.md.
- object-frame-ideation.md, sections 1-3.
- idea-generator.md, "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md, Part A.
- LEADERBOARD.md, Tables A-B and the phase table.
- The prime rows of FRONTIER.md.
- The lead YAMLs for every obstruction quoted below.
- H-ICEX-6ca21f, H-EWALK-29cb90, H-CLGP-63f471 and H-PFDR-2765d2.
- EV-PFDR-1394a4, EV-PFDR-99c699, EV-PFDR-f71d7f and EV-SDEG-4a1c3d (relevant fields).
- analysis/smallroot-reach/CLOSURE.md.
- crypto `research/lit2026_w3_ggm_audit_20261011/README.md` (the program's SGGM audit).
- crypto `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` section 2.
- crypto `RESEARCH_PRIME_FAST_ECDLP.md` sections 3-5.
- crypto `research/ic_planner_validation_20261020/README.md`.
- The fp24 row of `docs/ic/runs/ic-boundary-ledger-round5-2026-09-22.json`.

Ledger index: grepped only. The proposals directory was not opened.

---------------------------------------------------------------------------------------------------

## 0. Frame

### 0.1 What my field says about B1-B3, in one paragraph

The SGGM is the generic group model plus a free "star" operation, which factors labels over a
structured set. Its bound Omega(min(sqrt q, 1/delta)) is vacuous once the factor base's m-sums cover
the group. The program's own audit found that "122 of 208 rows have delta_upper = 1", and that "for
these configurations the cost lies entirely in *finding* a decomposition. The SGGM treats that
search as a free star evaluation" (crypto audit README, read this session).

So the generic-model literature has said all it can about dense index calculus. What remains of B1,
B2 and B4 is one number per oracle: its charged per-attempt cost and its reusable memory, measured
as exponents of the factor-base size.

- QC1 turns this into an exact admission region with two oracle semantics. It places every oracle
  the program has built.
- QC2 is a scoped rule-out for the reduced binary-digit system, the presentation the open digit
  lead solves. It is rigorous given H2 at low arity, and needs H4w at high arity.
- QC3 is the one B3 move my field supplies. It moves to the time-space-optimal vertex of the generic
  table frontier, which Table B has never used. It is tier I only, because it stays inside SO-TABLE.
- QC4 (B6) and QC5 (B7 plus three exotic leads) are the same kind of tool for rho and transfer:
  - a query bound for the generic half (proved for QC4; SQ-scoped for QC5);
  - one cheap exact census or spectrum for the coordinate-dependent half.

### 0.2 Units and notation

N (also r, q) is the prime group order. B = N^beta is the number of factor-base abscissae; signed
points number 2B. m is the arity. The per-attempt oracle cost is T_dec = B^tau, in group-operation
equivalents and charged. A reusable table of B^mu entries costs at least its size to build. Relations
needed are about B. The per-attempt decomposition probability is pi.

### 0.3 Numbered heuristics (each with its validation route)

- **H1 (yield).** pi ~ C(2B+m-1, m)/N, and the mean is exact by KN-FIND-007 ("mean per-target yield
  is binomial(B+m-1, m)/N for every base of size B").
  - Validation: the yield/ceiling fields of the boundary ledger. At fp24, m = 2,
    yield_over_ceiling = 1.0014.
- **H2 (linear algebra).** Sparse linear algebra on weight-m rows costs at least c*m*B^2. No
  sub-quadratic solver is known for these random sparse systems over F_N; Wiedemann gives m*B^2 as an
  upper bound.
  - Validation: none possible by measurement. It is a standing assumption of every IC cost model in
    the program (the arity table of RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md section 2.4).
- **H3 (Groebner tracks the grid).** F4/msolve on <S_{m+1}, g_V(x_1),...,g_V(x_m)> costs at least
  the dimension of the grid quotient up to polynomial factors. This is HEUR-ICEX-6ca21f-1 restated.
  - Validation: EXP-ICEX-153c34 arm M.
- **H4 (no cancellation).** In the reduced (multilinear, d = 2) digit expansion of S_{m+1}, every
  monomial of block degree <= 2^{m-1} has a nonzero coefficient mod p, except on a Schwartz-Zippel
  fraction of order 1/p.
  - Validation: section 2 below. The toy check (K <= 4) was run this session.
  - H4w, its weak form, is what the closure actually needs in the s ~ 2^{m-1} band. It asks only
    that at least a 2^{-80}..2^{-302} fraction of those monomials be nonzero (section 2).
- **H5 (generic position of invariants).** The smallest pole order of a non-constant function on E
  that is invariant under H <= (Z/N)^* on G \ {O} is (N-1)(1 - |H cap Aut|/h) + O(1).
  - Validation: section 4. The toy census was run this session.
- **H6 (random-level spectra).** For coordinate statistics s on G, sqrt(N)*max_{alpha != 0} |g_s^(alpha)|
  and sqrt(N)*max_{d != 0} |A_s(d)| are at the level of the maximum of N Gaussians.
  - Validation: section 5.
- **H7 (QC3 relations).** The relations needed under the early-stop rule are rho_rel*B, with
  rho_rel in [0.667, 1.0] for m = 3..5. The value 0.667 = 74/111 is measured at m = 2, fp24.
- **H8 (QC3 hits).** The per-trial hit probability is 2*keys/r for a full m-fold signed sumset, as
  measured at m = 2.
- **H9 (QC3 constants).** These carry over from m = 2:
  - c_tab = 1 GAE per table key (12,432 adds for 12,432 keys at fp24);
  - c_w = 1.096 GAE per walked trial (35,787 GAE over 32,642 trials).

---------------------------------------------------------------------------------------------------

## 1. QC1 (B1 first; also B2, B4, B5). The (tau, mu) admission region for decomposition oracles, with oracle semantics fixed

**Bottleneck.** B1. The approved non-enumerative oracle is unbuilt
(LEAD-ICE-charged-toy-ic-exponent-vs-rho, open_blocked). Audits found the four-size IC exponent
unidentifiable. Behind B1 sit B2 (the 0.30 gate), B4 (alpha of the SAT/XOR arm) and B5 (hybrid
guess-and-determine). The program prices each of them in its own normalisation.

**External ingredients.**
- Shoup, "Lower bounds for discrete logarithms and related problems", EUROCRYPT 1997, LNCS 1233,
  256-266, doi 10.1007/3-540-69053-0_18.
  - Retrieved this session: bibliographic data and the Omega(sqrt p) headline, from secondary records.
- Corrigan-Gibbs, Kogan, "The Discrete-Logarithm Problem with Preprocessing", ePrint 2017/1113
  (EUROCRYPT 2018).
  - Retrieved this session (abstract page): S*T^2 = Omega~(eps N) for generic algorithms with S bits
    of advice, tight up to logarithmic factors.
- Corrigan-Gibbs, Henzinger, Wu, "The Structured Generic-Group Model", ePrint 2026/384, a major
  revision of the EUROCRYPT 2026 paper.
  - Retrieved this session (abstract page): exploiting structure on at most a delta fraction costs
    Omega(min(sqrt q, 1/delta)). The abstract claims "similar lower bounds" for elliptic-curve points.
  - Theorem numbers below (Def 3.1, Thm 3.2 `DLAdv <= delta(3T+2) + (3T+1)^2/q + 1/q`, Thm B.1
    `O~(S T^2/q + delta T)`, Thm 4.2 free factoring `O(k log^2 k log n / gamma)`) are as quoted by the
    crypto audit README, which I read.
  - The PDF fetch failed twice this session (the tool's safety check returned no verdict), so I did
    not read the theorem text. The audit records the EC section as missing from the copy it read.
- De, Trevisan, Tulsiani, "Time space tradeoffs for attacks against one-way functions and PRGs",
  CRYPTO 2010.
  - Retrieved via search: inverting random functions needs S*T >= Omega~(eps N), which Hellman-type
    attacks attain up to the Fiat-Naor range.
- Golovnev, Guo, Horel, Park, Vaikuntanathan, "Data structures meet cryptography: 3SUM with
  preprocessing", STOC 2020, arXiv 1907.08355.
  - Retrieved via search (abstract level): Fiat-Naor upper bounds for 3SUM-indexing, and lower bounds
    that are conditional or model-restricted.

Provenance for the candidate is "retrieved". The load-bearing facts are the CGK and SGGM abstracts,
both fetched.

**Mechanism (derivation; I re-derived it and checked it numerically in `qc/qc1_region_check.py`).**

Total cost: C = (relations) + B^mu + B^2.

- Find-one oracle: at most one decomposition per attempt, so relations = B * B^tau / min(1, pi).
- List-all oracle: it returns all decompositions of the target and pays at least their number, so
  relations = B * B^tau / pi, under the constraint B^tau >= max(1, pi).

Writing pi = B^m/N, the exponent of C must drop below 1/2 for some beta.

*Region lemma.* For tau >= 0:

    R_m^find = { tau < min(m/2 - 1, m - 3),  tau + mu < m - 1 }
    R_m^list = { tau < m - 3,                tau + mu < m - 1 }

Both are empty for m <= 3. At m = 3 there is a tie at tau = 0 with mu <= 2.

Proof sketch:
- The relation term needs beta(m - 1 - tau) > 1/2.
- Linear algebra needs beta < 1/4 (H2).
- The table needs mu*beta < 1/2.
- A find-one oracle in the unsaturated branch also needs beta <= 1/m.
- For list-all, beta may exceed 1/m, but the output constraint gives tau*beta >= m*beta - 1, which is
  compatible.
- Eliminating beta gives the stated inequalities.

The script's bisection reproduces the boundaries at m = 4..8. Find-one: tau = 1.000, 1.500, 2.000,
2.499, 2.999. List-all: tau = 1, 2, 3, 4, 5.

*Generic corollary (a free k-SUM-indexing bound).* An oracle built from group operations, equality
and membership tests, with (tau, mu) inside R_m, would give a generic DLP algorithm in o(sqrt N). Its
upper bound would use only H1's exact mean yield and Wiedemann's upper bound on linear algebra. That
contradicts Shoup and CGK.

So every generic oracle has tau >= min(m/2 - 1, m - 3) or tau + mu >= m - 1. The known generic splits
(a j-sum table plus enumeration of m - j summands) have (tau, mu) = (m - j, j), so tau + mu = m. They
miss the region by one full power of B.

The script's generic-split exponents (find-one, best beta) match the program's finite-size fitted
mitm exponents at the engine's default table arity j = (m+1)//2 (H-PFDR-2765d2). The fitted values
carry their own intervals, so "match" means agreement to the quoted precision:

| m | j | predicted exponent | measured |
|--:|--:|--:|--:|
| 3 | 2 | 0.667 | 0.67 |
| 4 | 2 | 0.750 | 0.75 |
| 5 | 3 | 0.600 | 0.60 |
| 7 | 4 | 0.571 | 4/7 |

The tau = 0 vertex j = m gives m/(2m-1): 0.600, 0.571 and 0.556 at m = 3, 4, 5. It has never been
run on Table B (see QC3).

*The exact requirement on a non-generic oracle.* It must do both of the following.
- (a) Decide one m-sum decomposition per attempt in B^tau with tau below min(m/2 - 1, m - 3), or
  below m - 3 if it lists all solutions.
- (b) Beat every generic split by at least B^{1+eps} in the combined time-memory exponent.

At m = 4 the oracle must be sub-linear in |F| per attempt (tau < 1) with mu < 3 - tau. At m = 5 it
needs tau < 1.5 (find-one) or tau < 2 (list-all).

In words: the representation-dependent operation must invert the addition map F^m -> G restricted to
the factor base by a factor of B better than Yao/De-Trevisan-Tulsiani random-function inversion
allows (S*T ~ |domain|).

*Reconciliation with the program's own normalisations.* Each pair below states the same condition in
two forms, so these are consistency checks, not corrections:

- SDEG gate, B2. EV-SDEG-4a1c3d has m = 5, L = q^{0.2} and "0.30 sub-rho threshold" on beta_work in
  q. Here 0.30/0.2 = tau 1.5, which is R_5^find at beta = 1/5. B1's measured 0.797 is tau = 3.99.
  The subgroup base's 0.647 is tau = 3.24.
- ICEX threshold, B1. H-ICEX-6ca21f sets T = 13*0.886*sqrt(q)/(L+27) units per success, with
  B = L = q^{1/5} and m = 5. That is T_dec ~ q^{0.3} = B^{1.5}, the same find-one boundary.
- Small-root demand. CLOSURE.md condition (I), "(m-1)beta - Sum_v (1 - gamma_v) > 1/2", is the
  find-one region at tau = 0. The 8/9 is reach per equation for the windowed full tree (w = 2). The
  earlier draft's "could not reconcile" is withdrawn.
- RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md section 2.4.
  - The m = 4 row, "yes iff T_dec << p^{1/4}", is tau < 1 at the re-optimised B = (pT)^{1/5}. It is
    correct under both semantics, so the earlier draft's flag on the revisit_when wording is withdrawn.
  - The m = 5 row, "yes iff T_dec << p^{1/2}", holds only for a list-all oracle. Its optimum
    B = (pT)^{1/6} = p^{1/4} has pi > 1. A find-one oracle needs T_dec << p^{3/10} (side flag F2).
- Binary threshold, B4. LEAD-ICB-decomposition-encoding-and-sat records "beating rho needs
  alpha < m/2 - 1". That omits the linear-algebra cap. At m = 3 the threshold is alpha < 0 (R_3 is
  empty), consistent with "on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's
  2^60.81" (KN-FIND-aa2efc). Frobenius orbit folding changes polylog factors only (side flag F1).

**Placement of every built oracle (derived from committed records; no new measurement).**

| oracle (record) | m | tau | mu | needs | verdict |
|:--|--:|--:|--:|:--|:--|
| Table B folded/walked pair table (LEADERBOARD Table B) | 2 | 0 | 2 | R_2 empty | outside for any oracle |
| prime mitm, default arity (H-PFDR-2765d2) | 3-7 | m - j | j = (m+1)//2 | tau + mu < m - 1 | outside by exactly 1 |
| SDEG serial split + subresultant PRS, interval/random (EV-SDEG-4a1c3d) | 5 | 3.99 | ~2 | < 1.5 | outside by 2.5 |
| same, subgroup base | 5 | 3.24 | ~2 | < 1.5 | outside by 1.7 |
| G1 Groebner on the grid indicator ideal (EXP-ICEX-153c34 design; quotient is F_p^(V^5) by CRT, H-ICEX-6ca21f) | 5 | >= 5 (theorem for Macaulay/XL; H3 for F4); symmetrised C(L+4,5): still 5 | 0 | < 1.5 (find-one), < 2 (list-all) | outside by >= 3 |
| WDSat / CMS-XOR binary PDP (LEAD-ICB-decomposition-encoding-and-sat) | 3 | 3.0 | ~0 | R_3 empty | outside for any oracle, at any conflict price |
| same | 4 | 4.09-4.33 | ~0 | < 1 | outside by >= 3.1 |
| hybrid guess-and-determine (3,7) (LEAD-ICE-hybrid-guess-determine-l7) | 3 | k* + closure | 0 | R_3 empty | outside for any oracle |
| Coppersmith/JM small roots, small-x base (LEAD-ICP-coppersmith-smallroot-semaev) | m | ~0 within reach | 0 | per-variable reach > 1/(2(m-1)); JM direct box 1/(m(m+1)2^{m-2}) | the only built family inside R_m in (tau, mu); blocked by reach (1/80 vs 1/6 at m = 4) |

**Representation-operation pair.** The representation is the x-coordinate label in F_p of the
factor-base points, with any presentation of F (R1). Sigma is translation by factor-base elements.
The oracle is the partial inverse of the m-fold addition map F^m -> G.
**Trichotomy:** partial-action. This is index calculus Class I: the relation vector propagates only
under translation by F.

**SO codes touched (quoted).** QC1 does not escape these premises itself. It is the test that
certifies a candidate has left them.

- SO-TABLE, LEAD-ICP-generic-table-decomposition (closed_obstructed, theorem): "Any decomposition
  oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off
  and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included
  the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1).
  [...] Scope: any generic (enumeration/table) decomposition over F_p."
  - Premise: "enumerates or table-looks-up factor-base elements". By the generic corollary, being
    inside R_m is impossible within this premise.
- SO-TABLE, LEAD-ICB-generic-table-oracle: "Every oracle built from group operations and membership
  tests makes IC a generic-group algorithm with advice [...] Scope: all binary and Koblitz curves, one
  target, setup charged."
  - Premise: "built from group operations and membership tests". The same role, for B4 and B5.
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound: "Shoup/Nechaev generic-group lower bound: any generic
  algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). [...]
  Scope: all generic algorithms, any field, any r."
  - Premise: "generic algorithm". R_m is its quantitative complement, stated in IC coordinates.
- SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base: "A target-independent algebraic locus of
  degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and
  membership polynomial prod(x - v) of degree B [...] Scope: prime-order E/F_p, any base of size B."
  - QC1 converts "description degree B" into its consequence for algebraic oracles on the grid ideal:
    tau >= m by the CRT quotient (the G1 row).
- Nearest closed lead, LEAD-ICE-generic-oracle-arity-cost-floor (cost_model): "[...] in-model,
  structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783)
  give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE
  control does have sub-VOW cells, so the obstruction is the oracle class, not IC."
  - R_m is the exact shape of the "FREE control" sub-VOW cells, charged.

**First discriminating step (zero compute, advancing the blocked step rather than replacing it).**

1. File the region lemma, the two oracle semantics, the generic corollary and the placement table as
   one derivation record.
2. For LEAD-ICE-charged-toy-ic-exponent-vs-rho: G1's placement already exists. It is the
   coordinator's design-time ceiling audit in H-ICEX-6ca21f ("Grid floor A*L^5 is 0.13-4.4 times
   B0's measured units per success and 1,041-8,438 times T on the v4 fixtures").
   - The region shows that T = 13*0.886*sqrt(q)/(L+27) is exactly the find-one boundary tau = 1.5 at
     m = 5 and B = q^{1/5}.
   - So the audit's verdict follows from R_5 plus the CRT dimension count (tau_G1 = 5), without a run.
   - Neither arm of EXP-ICEX-153c34 varies L at fixed q: arm M fixes L = ceil(p^{1/5}) per fixture,
     and arm X freezes L across q. So the contract cannot itself identify tau. I do not propose it as
     a tau measurement.
   - What QC1 adds for this lead is the record: the arm-M verdict is derivable. Running arm M is then
     a test of H3 (F4 tracking the grid) only, not of the exponent question.
3. For LEAD-ICE-sat-xor-pdp-oracle: drop m = 3 from "fit alpha(m) at m in {3,4,5}", because R_3 is
   empty at any conflict price. Keep alpha(4) < 1 and alpha(5) < 1.5 / 2 as the only live thresholds.

**Outcomes -> dispositions.**
- The coordinator accepts the derivation together with the existing ceiling audit.
  - The G1 arm is decided before any build: closed_obstructed(cost_model) for Groebner-on-grid-
    indicator oracles, for every base of size B (interval, random, subgroup), scoped by H3 for F4.
  - LEAD-ICE-charged-toy-ic-exponent-vs-rho keeps open_blocked, with its next step changed to: admit a
    backend only with a derived (tau, mu) inside R_m. The one family with that property is small-root
    lattices, routed to LEAD-ICP-coppersmith-smallroot-semaev.
  - The SAT/XOR lead's m = 3 cell closes: closed_obstructed(cost_model).
- EXP-ICEX-153c34 runs anyway (as an H3 check), and G1 membership units per success fall below T on
  every 20-bit fixture with the agreement check intact.
  - H3 is refuted at those fixtures: open_next_step. best_measured = G1 units per success over T,
    with a tau reading requiring a new fixed-q, varied-L ladder.
- Any future oracle measured inside R_m at m >= 4, on at least 3 admissible sizes, with a size-matched
  null: open_next_step, best_measured = (tau, mu, m).

**Tier.** X: it decides exponent routes. **Predicted gain.** 0 bits; it is an instrument.
Prediction (H3): every non-lattice oracle the program has built sits at least 1.7 tau-units outside
R_m (table above).

**Cost.** Implementation: half a day to a day (derivation plus a table from committed records).
Compute: none.

**Self-kill risk.** Medium-high on novelty.
- R_m restates CGK/Shoup in IC coordinates. The program already has the arity table (section 2.4),
  the small-root demand (CLOSURE.md) and the ICEX threshold, each in its own normalisation.
- What is new:
  - the find-one versus list-all split, which corrects the m >= 5 rows (F2);
  - the m = 3 correction to the binary SAT threshold (F1);
  - the generic corollary, whose predictions match the measured mitm exponents;
  - dropping m = 3 from the SAT alpha fit;
  - recording that the ceiling audit's G1 verdict follows from R_5.

**--match phrasings** (log: `scout/qc/match_log_query_communication.txt`):
- Own: "per-attempt oracle exponent tau and table exponent mu escape region for an index-calculus
  decomposition oracle".
  - lead_atlas top: LEAD-ICE-rootfind-pairtable-oracle (17), LEAD-ICB-generic-table-oracle (12).
  - frontier top: KR-RHO-cd0049.
- Plain: "how fast must a point decomposition oracle be per attempt to beat Pollard rho".
  - Top: LEAD-ICE-generic-oracle-arity-cost-floor (18), LEAD-ICE-rootfind-pairtable-oracle (18).
- Obstruction vocabulary: "decomposition oracle that is not a generic time/memory trade-off obeying
  S*T^2 >~ N".
  - Top: LEAD-ICE-generic-oracle-arity-cost-floor (14), LEAD-ICE-rootfind-pairtable-oracle (12),
    LEAD-EXO-augmented-oracle-ggm (11), LEAD-ICP-generic-table-decomposition (11).

---------------------------------------------------------------------------------------------------

## 2. QC2 (B2 residual). Writability floor for the reduced digit presentation, through the uniqueness of multilinear representations

**Bottleneck.** B2 is closed only as closed_known, through KR-IC-5931ee, "under stated statistical
assumptions". Its revisit_when names the digit map: "A prime-field factor base whose membership
equation has bounded degree independent of p (the base-d digit-map / PFDR descent, IDEA-20260830-84cdb7)
produces a measured solving degree that stays flat across >= 3 field sizes."

The open lead carrying it is LEAD-ICP-digit-presentation-solving-degree (open_next_step). Its
discriminator ("d_lf growing ... closes; bounded in s ... reopens") makes the closure depend on a
solving-degree law the instrument cannot measure past s = 5.

QC2 is a floor that does not depend on d_lf. It is **scoped** to the presentation that lead's
instrument actually solves: rows mu*S~ of the digit-substituted generator in the squarefree Boolean
ring. EV-PFDR-1394a4 records "the Boolean-evaluation identity at all 64 digit assignments" and "rows
mu S~ in B". QC2 does not decide B2's revisit_when in general.

The program already holds part of this ground:
- EV-PFDR-f71d7f counts the top form ("binom(s, 2^{m-1})^m = 2^221.3 nonzero terms at (256, m 5,
  ...)").
- EV-PFDR-1394a4 records an exponent closure "not reaching m >= 10 at 256-bit p".

What QC2 adds:
- one floor for every m and s;
- four field sizes;
- W-ary digits;
- an explicit statement of which cells rest on which assumption.

**External ingredient.** Nisan, Szegedy, "On the degree of Boolean functions as real polynomials",
Computational Complexity 4 (1994) 301-313.
- Retrieved this session: bibliographic data and the uniqueness of the multilinear representation,
  via secondary sources.
- Over F_p the same uniqueness is the elementary Moebius-inversion fact. Functions {0,1}^n -> F_p
  correspond one-to-one to multilinear polynomials over F_p, and the coefficient at J is
  Sum_{I subset J} (-1)^{|J \ I|} f(1_I).
- So the support of S~ is an invariant of the function d -> S_{m+1}(x(d), x_R) on the cube. No
  rewriting of the same reduced system is sparser.
- Restriction is monotone. Setting digits to 0 keeps exactly the monomials that avoid them, with
  unchanged coefficients, so the support of a restriction to a subcube is a certified lower bound.

Provenance: retrieved. Combined with the input-size bound that every solver consuming the generator
in the monomial basis pays at least its support. This is the polynomial-method view of a writability
wall.

**Mechanism.**

Setup: x_i = Sum_j W^j d_ij, with block degree K = 2^{m-1}. The top form of S_{m+1} is prod_i x_i^K
(EV-PFDR-f71d7f: "reduced total degree is m 2^{m-1}").

- Floor A, rigorous for p > K and p not dividing W. Reduced monomials of block degree exactly K come
  only from the top form, with coefficient prod multinomial * W^(...) != 0, giving
  #{e in [0,W-1]^s : |e| = K}^m terms.
- Floor B, under H4. Every reduced monomial of block degree <= K appears:
  (Sum_{t<=K} #{|e| = t})^m. For s <= K this is the full grid 2^{ms}, so in that regime the digit
  system is as large as the grid that QC1's CRT row prices.

Cost model (`qc/qc2_digit_writability_v2.py`). It is favourable to the attack in every term:
- the yield uses 2W^s signed points, an upper bound on the valid abscissae;
- the relations are W^s/2 and the linear-algebra columns W^s/2, both lower bounds;
- linear algebra is charged m*(W^s/2)^2 (H2);
- the solver is free, and each attempt pays only the writing of S~.

The margin is log2(total) - log2(sqrt(pi N/4)), minimised over m <= 14 and all s. Cells within +-2
bits are marked undecided. These are model numbers. An earlier pass counting 2W^s linear-algebra
columns (`qc2_digit_writability.out`) shifted margins by about 1-2 bits.

**Which cells rest on which assumption (W = 2, `qc/qc2_floorA_by_m.out`).** Under floor A + H2 alone,
which is rigorous given H2, W = 2 closes:

| log2 p | arities closed | margins | arities needing H4w |
|--:|:--|:--|:--|
| 128 | m <= 4 (m = 5 undecided) | +34.4, +28.9, +39.8 (m = 5: +1.1) | m >= 6 |
| 256 | m <= 5 | +58.2, +31.1, +63.9, +65.1 | m >= 6 |
| 384 | m <= 6 | +81.0 ... +34.7 | m >= 7 |
| 521 | m <= 6 | +105.0 ... +103.2 | m >= 7 |

The higher-arity cells all lie in the band s ~ 2^{m-1}, where the top form is nearly a single
monomial. There the closure needs only a weak form of H4:

- **H4w.** At least a 2^{-80} (128 bits), 2^{-155} (256), 2^{-226} (384) or 2^{-302} (521) fraction
  of the block-degree-<=K monomials is nonzero.
- For example, at 256 bits the band needs at most 2^{108.8} monomials, while floor B gives at least
  2^{155} more than required (`qc2_digit_writability_v2.out`).
- For m >= 15 (K > s always), floor B is the full grid, and the total is at least
  B*m!*N/2^{m+1} > rho under H4.

| log2 p | W = 2 (floor B, needs H4w for m >= 6/7) | W = 4 | W = 8 | W = 16 | W = 64 | W = 256 |
|--:|--:|--:|--:|--:|--:|--:|
| 128 | +29.4 closed | +20.7 | +18.5 | +15.9 | +13.9 | +3.7 |
| 256 | +31.2 closed | +25.6 | +22.2 | +13.7 | +4.5 | +0.2 undecided |
| 384 | +34.3 closed | +25.3 | +8.5 | +0.3 undecided | -2.6 open | -7.4 open |
| 521 | +32.7 closed | +4.9 | -2.3 open | -8.2 open | -13.5 open | -24.3 open |

Two cautions:
- Without H2 the W = 2 closure fails at 521 bits (-10.8), where s = 174 saturates pi.
- For W >= 4 I did not split cells into those resting on floor A and those resting on H4.

**H4 toy check (run this session; exact, `qc/qc2_h4_check.py`, output `qc/qc2_h4_check.out`).**

Method: exact Moebius transform of d -> S_{m+1}(x(d), x_R) over {0,1}^{ms}.
- S_3 explicit; S_4 = Res_X(S_3, S_3) via the quadratic-resultant formula.
- Random a, b, x_R; p in {2^61 - 1, 2^31 - 1, 65537}.
- Cells: m = 2, s = 2..8 and m = 3, s = 2..6. That is 36 (cell, prime) pairs, 5 draws per pair when
  ms <= 14 and 2 draws otherwise.

Results:
- Every monomial with a block degree above K has coefficient exactly 0 in every draw. This is the
  structural sanity check.
- Every monomial with block degree <= K is nonzero in every draw at p = 2^61 - 1 and p = 2^31 - 1:
  - m = 3, s <= 4: the full grids of 64, 512 and 4,096 terms;
  - m = 3, s = 6: 185,193 of 185,193.
- The one exception is a single draw at p = 65537, m = 3, s = 6, where 6 of 185,193 coefficients
  vanished. That matches the 1/p accidental-zero rate: 185,193/65,537 = 2.8 expected per draw, and the
  two draws gave 6 and 0.

**This says little about the band that needs H4w.** That band has K = 32-64 at m = 6-7, and the toy
check stops at K <= 4.

**Representation-operation pair.** Base-W digits of the x-coordinate as ms auxiliary F_p-variables,
with field equations of degree W (R1). Sigma is translation by F. **Trichotomy:** partial-action.

**SO codes touched (quoted).**
- SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base (quoted under QC1, Scope "prime-order E/F_p, any
  base of size B").
  - Premise escaped by the digit presentation: "a target-independent algebraic locus of degree d" in
    the single coordinate x. The digit base is described by ms auxiliary variables, each with a
    degree-W membership equation. That is exactly KN-OPEN-020's "implicit-membership" class.
  - QC2 closes this escape for the expanded, reduced presentation, using a different quantity:
    support rather than degree.
- Nearest closed lead, LEAD-ICP-icperf-writability-boundary (cost_model): "At the best viable arity
  the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283),
  +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver
  runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is
  inside (283, 409]."
  - QC2 is its prime-field counterpart, with the matching scope: expanded and reduced. A presentation
    that keeps x_i as unknowns with linear digit constraints, or a chained digit system with free F_p
    intermediates, has a small input and escapes the floor. Those stay open.
- B2 closure source, KR-IC-5931ee: "Yokoyama-Yasuda-Takahashi-Kogure prove, under stated statistical
  assumptions, that Semaev's naive index calculus over F_p costs at least as much as generic
  algorithms".
  - For the reduced digit presentation at low arity, QC2 replaces those assumptions by H2 alone. At
    high arity it uses H2 plus H4w.

**First discriminating step.** Certify H4w in the band where it carries the closure, using sampled
coefficients and no symbolic S_{m+1}.

- The coefficient at J costs 2^{|J|} point evaluations of S_{m+1}. Each evaluation is the product
  over the 2^{m-1} sign patterns of (x_R - x(P_1 +- ... +- P_m)), computed in F_{p^2}.
- Sample monomials of low block degree (<= 3 per block) at the band's cells: m = 6, 7, 8 with s near
  2^{m-1}, 20 (curve, target) draws, p near 2^127 and 2^255. That is 2^{3m} evaluations per
  coefficient, so 2^{18}-2^{24}.
- The count of block-degree-<=3 monomials exceeds the 128- and 256-bit requirement. For example
  C(63, <=3)^7 = 2^{107} against a need of 2^{90.8} at (m = 7, 256 bits).
- At 384 and 521 bits the requirement (up to 2^{163.5} and 2^{222.3}) exceeds what monomials of block
  degree <= 3 or 4 can certify at feasible cost. Those bands stay conditional on H4w.

**Outcomes -> dispositions.**
- Sampled zero fraction <= ~2^{m-1}/p at every sampled cell (predicted).
  - LEAD-ICP-digit-presentation-solving-degree: closed_obstructed(cost_model) for the d = 2 reduced
    presentation its instrument solves:
    - at 128 and 256 bits, all m, conditional on H2 (and on the sampled H4w for m >= 6);
    - at 384 and 521 bits, m <= 6 conditional on H2. For m >= 7 it rests on unverified H4w and is
      recorded as such.
  - The residual cells stay open_next_step:
    - W-ary digits (W = 256 at 256 bits and W = 16 at 384 bits undecided; W >= 64 at 384 bits and
      W >= 8 at 521 bits open);
    - all unexpanded and chained digit presentations.
  - Next step for the residual: a solver-side floor, i.e. the W-ary first-fall law from the
    tensor-product top form.
- A material zero fraction at any sampled cell.
  - H4w is in doubt there, and the closure at that arity reverts to floor A.
  - The lead stays open_next_step, with best_measured = the cancellation fraction and pattern. That
    pattern would be a new object: structured vanishing of a digit-expanded summation polynomial.

**Tier.** X: it closes an exponent route at deployed sizes. **Predicted gain.** 0 bits; this is a
closure. Predicted W = 2 margins: +29.4, +31.2, +34.3 and +32.7 bits above rho at 128, 256, 384 and
521 bits (floor B + H2, model).

**Cost.** Implementation: about one day (point-evaluation sampler). Compute: hours.

**Self-kill risk.** Medium.
- The scope is the expanded presentation only.
- Every closure needs H2.
- At high arity the closure needs H4w, which is certifiable by sampling only at 128 and 256 bits.
- Low-arity overlap: the floor-A part repeats the program's top-form count and its m < 10 closure at
  256 bits.

**--match phrasings.**
- Own (revised): "multilinear support of the base-2 digit presentation of the prime-field Semaev
  system as a writability floor".
  - Top: LEAD-ICP-digit-presentation-solving-degree (25).
  - The first-pass own phrasing missed it; both are in the log.
- Plain: "writing down the binary-digit Semaev polynomial over a prime field costs more than rho".
  - Top: KR-IC-5931ee (16); LEAD-ICP-digit-presentation-solving-degree (13, third).
- Obstruction vocabulary: "digit presentation ANF exceeds the whole per-decomposition rho budget
  before any solver runs".
  - Top: LEAD-ICE-generic-oracle-arity-cost-floor (10), LEAD-ICP-digit-presentation-solving-degree
    (10), LEAD-ICP-icperf-writability-boundary (9).

---------------------------------------------------------------------------------------------------

## 3. QC3 (B3, tier I). Move Table B to the tau = 0 vertex of the generic time-space frontier: a full m-fold signed sumset, one lookup per walked target, small B, m = 3-5

**Bottleneck.** B3: LEAD-ICP-prime-ic-constant-engineering, whose Table B gap widens from 5.47x to
13.5x. The lead's success criterion is constant improvement: "Each verified gain is an improvement
over the current IC baseline under the owner's success criterion even though the exponent is fixed."

**External ingredient.** The CGK time-space frontier S*T^2 = Omega~(eps N), applied to one-target IC
with an unknown-log factor base (Corrigan-Gibbs-Kogan 2018, abstract retrieved this session). Read
in QC1 coordinates: among generic splits (tau, mu) = (m - j, j), the best exponent at fixed m is the
j = m vertex, m/(2m-1) (QC1 script). Table B sits at (m, j) = (2, 2), the worst arity, with exponent
2/3. Provenance: retrieved.

**Why it is not already done (checked).**
- ic.pipeline's mitm oracle takes "summands, 2 or 3", built on a pair table: `src/bin/ic/bench.rs`
  plugin listing.
- Its m = 3 mode subtracts one factor-base point per target, so j = 2.
- The 2026-10-13 arity benchmark ("pair-table arity two versus three summands at 64 abscissae",
  m3/m2 = 1.431) is j = 2 at a fixed B = 64, not re-optimised.
- The planner validation's alternatives were base size, oracle, stop rule and targets, never arity
  or table depth.
- The autoresearcher mitm engine's default table arity is (m+1)//2 (H-PFDR-2765d2).
- No ledger proposal or hypothesis uses a full m-fold sumset with zero per-target subtractions. The
  index grep for "triple-sum", "h-fold" and "sumset" found only occupancy and coincidence studies
  (IDEA-20260930-4ebd85, IDEA-20261006-5bfbcf, IDEA-20261018-5fa71b).

**Mechanism and model (`qc/qc3_fullsumset_model.py`, output `qc/qc3_fullsumset_model.out`;
predictions).**

- Table: every <= m-fold signed sum of B abscissae with no cancelling pair, x-keyed up to global
  sign. The number of keys at level j is Sum_k C(B,k) C(j-1,k-1) 2^k / 2. It is built incrementally
  at c_tab GAE per key (H9).
- Targets: R <- R + G walked, one x-lookup per trial at c_w GAE, with hit probability 2*keys/r (H8).
- Relations: rho_rel*B, with weight-m rows and negligible linear algebra at B <= 64 (H7).
- Factor-base construction: the measured fp24 per-abscissa cost of the square-root phase.

Calibration check: the model with the fp24 constants gives S = 14.71 at m = 2, B = 111, against the
measured 14.79. The same constants give the m = 2 optima at fp20 and fp22 below, 7% under the
measured rows.
- Caveat: that comparison sets the model's optimum B against measured recipes at their own B (the
  family optimum), so it is a consistency check, not an independent validation.

| Table B row | measured IC S (x matched rho) | model m = 2 | **m = 3, j = 3** | m = 4, j = 4 | m = 5, j = 5 |
|:--|:--|:--|:--|:--|:--|
| fp20 (log2 r 20.0, rho 1.29) | 10.7 (8.3x) | 9.95-13.0 | **4.6-5.9 (3.6-4.6x), B* = 13-15** | 3.5-4.3 (2.7-3.3x), B* = 8 | 3.0-3.7 (2.4-2.8x) |
| fp22 (21.7, rho 1.22) | 12.8 (10.5x) | 12.0-15.7 | **5.2-6.6 (4.2-5.4x), B* = 17-19** | 3.7-4.7 (3.0-3.9x) | 3.2-3.9 (2.6-3.2x) |
| fp24 (23.4, rho 1.04) | 14.0 (13.5x) | 14.5-19.0 | **5.8-7.4 (5.6-7.1x), B* = 22-24; 7.6k-9.8k table keys** | 4.1-5.2 (3.9-4.9x), B* = 11-12 | 3.5-4.2 (3.3-4.0x), B* = 7-8 |
| fp28 | (planner rows only) | 24.6-32.2 | 8.1-10.3 | 5.2-6.5 | 4.1-5.1 |

Each range spans rho_rel = 0.667 to 1.0 (H7). Memory at the m = 3 optimum is 7.6k-9.8k keys at fp24,
below the incumbent's 12.4k.

How the shape behaves:
- The ratio to rho stops growing. At fixed m the exponent is m/(2m-1) against 1/2, so the gap grows
  like N^{1/(2(2m-1))}: N^{1/6} at m = 2, N^{1/10} at m = 3, N^{1/14} at m = 4.
- In the m -> infinity, B -> 1 limit the recipe degenerates to baby-step giant-step with a structured
  baby-step set of unknown logs. Under H7-H9 the model total is at least
  2*sqrt(c_tab*c_w*rho_rel*B*r/2), about 1.48*sqrt(rho_rel*B*r).
- So, in the model, no member of this family reaches matched rho at these sizes. This is a model
  statement under H7-H9, not a consequence of SO-GEN. BSGS itself beats rho on operations at toy
  sizes (KR-RHO-cd0049: bsgs.negation 1.160 x floor = about 1.03 GAE per sqrt r, with a 0.50 sqrt(r)
  table), and BSGS is this family's limit.
- Every new row should therefore be reported against bsgs.negation as well as matched rho. A row near
  rho would otherwise read as a BSGS relabelling, under closed_known
  LEAD-RHO-bsgs-family-memory.

**Pricing band (AGENTS.md section 5a).** The new recipe adds no new unpriced counter. It makes one
lookup per trial, as the incumbent does, and needs fewer square-root solves because B is smaller. At
w = 1 GAE per lookup both arms gain about one GAE per trial, so the ordering is predicted to hold
across the band.

**Representation-operation pair.** The representation is the x-key of the full m-fold signed sumset
of a small factor base (R1). Sigma is translation by factor-base elements, with walked targets.
**Trichotomy:** partial-action.

**SO codes touched (quoted).**
- SO-TABLE, LEAD-ICP-generic-table-decomposition (quoted under QC1; "Scope: any generic
  (enumeration/table) decomposition over F_p").
  - **QC3 does not escape this premise.** It "table-looks-up factor-base elements", so it stays a
    generic time/memory trade-off, bounded by S*T^2 >~ N. That is why it is tier I only.
  - Its forecloses list includes "choose the factor-base size B optimally to cross rho" and
    "pair-table meet-in-the-middle decomposition beats rho at higher arity". QC3 claims neither. It
    claims only the constant at one-target toy sizes.
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (quoted under QC1, "Scope: all generic algorithms, any
  field, any r"). It is inside the premise, so the floor is BSGS-like.
- SO-MULTI, LEAD-ICB-multi-target-and-portfolio: "The multi-instance generic bound (L logarithms
  cost >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up [...]".
  - Not touched: the board is one target.

**First discriminating step.**
1. Implement a `mitm-full:m=3` oracle in ic.pipeline: a level-3 signed sumset built from the
   negation-folded pair table, one x-lookup per walked target, no per-target subtraction. Estimated
   1-2 days in Rust; the Python engine already builds h-fold sumsets.
2. Run a paired ecbench arm against the incumbent folded/walked m = 2 recipe at fp20, fp22, fp24 and
   fp28:
   - B at the model optimum (m = 3: 13/17/22/42; m = 4: 8/9/11/18);
   - 24 paired targets per size, A/A, cluster intervals and the section 5a band;
   - table entries and memory reported beside S.
3. Add the m = 4 arm second.

**Outcomes -> dispositions.**
- Paired ratio interval below 1 at every size, with S inside the predicted band.
  - open_next_step, best_measured = the new Table B rows, each with its ratio to matched rho and to
    bsgs.negation, and its table entries. The recipe planner gains an arity dimension.
  - The ratio's growth rate across sizes is reported against N^{1/10}.
  - The predicted ratio to bsgs.negation at fp24 is 3.4-7.2x (m = 3-5).
- Ratio below 1 but S above the band by more than 1.5x.
  - H7, H8 or H9 fails at m = 3; most likely rank deficits or degenerate sums at small B.
  - open_next_step, with the failing constant named.
- Interval spanning 1 or above 1 at every size.
  - The arity item is exhausted_at_scale (fp20-fp28) for full-sumset recipes. B3 then rests only on
    the lead's own batching arm.

**Tier.** I (constant, end-to-end in Table B's GAE unit). **Predicted gain** at fp24, H7-H9:
- m = 3: 1.9-2.4x fewer GAE, ratio 13.5x -> 5.6-7.1x;
- m = 4: 2.7-3.5x fewer GAE, ratio -> 3.9-4.9x.

The lead's two-level batching arm lowers c_w and would compound with this.

**Cost.** Implementation: 1-2 days. Compute: seconds per solve at fp20-fp28.

**Self-kill risk.** Medium.
- The constants at small B (8-24 abscissae) are extrapolated from one m = 2 row, and rank behaviour
  under early stop at m >= 3 is unmeasured.
- A reviewer may call the m >= 4 rows "BSGS with unknown-log baby steps". They are index calculus by
  the board's definition (factor base, relations, linear algebra), but the limit should be stated.

**--match phrasings.**
- Own: "full m-fold signed sumset table with one lookup per walked target for prime-field index
  calculus at m = 3 to 5".
  - Top: LEAD-ICP-retained-setup-online (20), LEAD-RHO-correlated-walks-shared-sums (16).
  - Revised own: "prime-field index calculus with a full triple-sum table and walked targets at the
    generic time-space vertex" puts LEAD-ICP-prime-ic-constant-engineering fifth (12).
- Plain: "use a table of all triple sums of factor-base points instead of pair sums to cut prime
  index calculus cost".
  - Top: LEAD-RHO-correlated-walks-shared-sums (20), KR-IC-5931ee (17),
    LEAD-ICP-prime-ic-constant-engineering (16).
- Obstruction vocabulary: "meet-in-the-middle table decomposition at higher arity as a generic
  time/memory trade-off for the prime ladder".
  - Top: LEAD-ICP-generic-table-decomposition (28), LEAD-ICB-generic-table-oracle (21).

---------------------------------------------------------------------------------------------------

## 4. QC4 (B6). Shoup's bound with the unknown multiplier restricted to H: generic canonicalisation of H-orbits costs Omega(sqrt h) per call, plus an exact census of algebraic H-invariants

**Bottleneck.** B6: LEAD-RHO-non-automorphism-equivalence (open_unexamined). Its next step: "Prove or
refute H-EWALK-29cb90's per-step canonicalisation bound: show that for h = |H| > 6 on ordinary
prime-field curves any canonicaliser costs Omega(log h) group operations per step (charged gain <= 1),
and search the encoding for a non-constant H-invariant at h ~ N^{1/3} on toy curves (exhaustive at
N < 2^20)."

In the object frame this is the one open number of a quotient object, "the cost of canonicalising a
Gamma-orbit" (IDEA-20260901-863e36).

**External ingredient.** Shoup's random-encoding collision argument (Shoup 1997; bibliographic data
and headline retrieved; the proof technique is recalled, and I did not re-read the full text). It is
applied with the unknown multiplier drawn from H instead of from Z/N. Provenance: retrieved.

**Theorem (my derivation).** Let C be a generic algorithm. Given sigma(P), sigma(Q) and a point R with
its known representation R = aP + bQ, it outputs sigma(c(R)) with c(R) in H*R and c(lambda*R) = c(R)
for every lambda in H. Suppose it makes q group queries per call and is consistent with probability
>= 1 - eps on a pair (R, lambda*R), where:
- lambda is uniform in H;
- the second call is given an independent representation (a', b') of lambda*R.

Then q >= sqrt(h(1 - 2eps - O(1/h))/2) - O(1).

Proof sketch.
- From the joint view (a, b, a', b'), k is uniform on h values: one value for each lambda.
- Every label is a linear form in K. Two distinct forms, from within one call or across the two calls,
  coincide at the true k with probability <= 1/h. So all (2q+O(1))^2/2 pairs together collide with
  probability <= (2q+O(1))^2/(2h).
- With no collision, the real game equals the ideal game.
  - Correctness of each call alone forces its output to be the known multiple mu_i of its input, with
    mu_i in H a function of that call's view (otherwise the probability is <= h/N).
  - Consistency then needs mu_1 = mu_2*lambda, which has probability 1/h.

The cross-call collisions this counts are the ones a real canonicaliser exploits (for example the
minimum-label rule over the orbit). That is why the bound is sqrt(h) and not 1.

**Corollary (constant level).** A rho walk on G/H takes about sqrt(pi N/(2h)) steps. If every step
calls an unadvised, unbatched generic canonicaliser, the walk costs >= sqrt(h/2)*sqrt(pi N/(2h)) =
sqrt(pi N/4) times (1 - O(h^{-1/2})). That is the negation walk's count: charged gain <= 1 + O(h^{-1/2})
over negation rho. This proves the lead's "charged gain <= 1" for every generic canonicaliser, not
only for enumeration (H-EWALK-29cb90 priced enumeration at h per step).

**What it does not cover.**
- The exponent half is already closed globally by SO-GEN: a walk with a generic canonicaliser is a
  generic algorithm, so the N^{1/3} rung needs a non-generic canonicaliser in any case.
- Canonicalisations batched across L parallel walks, or using advice, are not covered by the per-call
  bound. Multi-instance arguments suggest sqrt(L*h) rather than L*sqrt(h) for batched collision
  finding. The constant claim is therefore stated for unbatched, unadvised canonicalisers only.

**The residual is coordinate-dependent.** A canonicaliser through a rational invariant f in F_p(E),
with f([g]R) = f(R) on G \ {O}, has fibres that are unions of free H-orbits, so deg f >= h. That gives
only Omega(log h) field operations, which cannot bound the charged gain.

The live question is the smallest degree of such an f. H5 predicts generic position,
d_min = (N-1)(1 - |H cap Aut|/h) + O(1). The reason: the image of L(dO) in functions on G \ {O} is
d-dimensional, and the invariant subspace has dimension (N-1)/h.

**Toy census (run this session; exact; `qc/qc4_invariant_census.py`, output
`qc/qc4_invariant_census.out`).**

Method: for each H = <g>, Gaussian elimination over F_p of the columns f([g]R) - f(R), R in
G \ {O}, for the basis 1, x, y, x^2, xy, ... in pole order. The first dependent column of positive
pole order gives d_min.

Sample: 21 cells.
- Ordinary prime-order curves with (p, N) = (1009, 997), (1021, 1013), (1213, 1259), and every h | N-1
  up to 64 that the script reached: 15 cells.
- A j = 0 curve (p = 1009, N = 967): 6 cells.

Results:
- Positive controls were detected. On every curve h = 2 gives pole 2 (x, the negation map). On j = 0,
  h = 3 gives pole 3 (y) and h = 6 gives pole 6 (x^3).
- Every other cell equals the generic-position count within one:
  - odd h: (N-1)(1 - 1/h) + 1 (h = 3, 11, 17, 23, 37 and, on j = 0, h = 7);
  - even h: (N-1)(1 - 2/h) + 2, because -1 is in H (h = 4, 6, 12, 22, 34, 44 ordinary; h = 14 on
    j = 0);
  - h = 21 on j = 0, which contains the order-3 automorphism: (N-1)(1 - 3/h) + 3.

So at N about 2^10, no non-automorphism invariant exists below generic position. Automorphisms
contribute exactly their factor and nothing more.

**Representation-operation pair.** The affine (x, y) encoding (R1). Sigma is multiplication by
H <= (Z/N)^*. **Trichotomy:** partial-action. The H-orbit partition is a block system of the
multiplicative action of <H>, not of translation. The residual invariant search is
coordinate-dependent.

**SO codes touched (quoted).**
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (quoted under QC1, "Scope: all generic algorithms, any
  field, any r").
  - Inside the premise for the generic half. QC4 adds the constant-level accounting the exponent
    statement lacks.
- SO-ENDO, LEAD-STR-endo-scalar-action-generic: "For G of prime order N, End(G) = Z/N, so every
  endomorphism-image oracle is simulable by group operations and Shoup's bound applies [...] Scope:
  any prime-field or binary curve, any size, prime-order subgroup."
  - Premise: "endomorphism-image oracle". For h > 6, applying H is not a cheap endomorphism. A
    canonicaliser is a different object, an orbit selector, and its cost is what QC4 bounds.
- Nearest closed lead, LEAD-STR-small-cm-disc-nonunit-endo: "[...] A rho class of size h costs about h
  evaluations of alpha to canonicalise, so the net factor is at most sqrt(h)/kappa with kappa about h
  times c(alpha) [...] Scope: ordinary prime-field curves, prime-order G."
  - QC4 replaces "about h evaluations" (enumeration) by a lower bound for every generic canonicaliser
    (sqrt(h/2)), and by a measured degree floor for algebraic ones.

**First discriminating step.**
1. Zero compute: file the theorem and corollary, scoped to unbatched, unadvised generic
   canonicalisers.
2. Extend the census:
   - N up to 2^13-2^14 (dense elimination, hours);
   - h near N^{1/3}, at least 3 curves per N, plus one j = 0 and one j = 1728 curve as positive
     controls;
   - a random-relabelling control: a random permutation of G \ {O} with the same orbit structure as H.
     It must give the same d_min, since generic position is a property of the counting.

The lead asks for "exhaustive at N < 2^20". Dense elimination at that size needs about 10^{12}-byte
matrices. I propose 2^14 as the reachable rung and say so.

**Outcomes -> dispositions.**
- Generic position at every cell (predicted, H5; holds on all 21 toy cells).
  - LEAD-RHO-non-automorphism-equivalence: closed_obstructed(theorem), scoped to generic unbatched
    canonicalisers.
  - best_measured: "no non-automorphism H-invariant below (N-1)(1 - |H cap Aut|/h) + O(1), at
    N <= 2^14".
  - Batched and advised canonicalisers are recorded as the stated open residue.
- A non-automorphism invariant at least N^{c} below generic position, at any cell, with the
  relabelling control at generic position.
  - open_next_step: price its straight-line evaluation cost against sqrt(h). This would be the first
    non-generic quotient structure on an ordinary prime-order curve.

**Tier.** X. The lead's open rung (N^{1/3} with free canonicalisation) is exponent-level, and QC4
decides it in both halves. **Predicted gain.** 0 bits. Constant gain is at most 1 + O(h^{-1/2}) over
negation rho for unbatched generic canonicalisers (theorem).

**Cost.** Proof: half a day. Census extension: one day, with hours of compute.

**Self-kill risk.** Low on correctness of the per-call theorem. Medium on value: SO-GEN already closes
the exponent, and the batched case stays open.

**--match phrasings.**
- Own: "restricted-multiplier Shoup bound for generic canonicalisation of multiplier-subgroup orbits".
  - Top: LEAD-RHO-generic-sqrt-lower-bound (9), LEAD-RHO-automorphism-class-walks (7),
    LEAD-STR-endo-scalar-action-generic (7).
- Plain: "canonicalising orbits of a subgroup of scalar multipliers costs the square root of the orbit
  size".
  - LEAD-RHO-non-automorphism-equivalence at rank 5 (7).
- Obstruction vocabulary: "every endomorphism-image oracle is simulable by group operations so
  quotient rho by a multiplier subgroup gains nothing".
  - Top: LEAD-RHO-non-automorphism-equivalence (16), then LEAD-RHO-automorphism-class-walks (13).

---------------------------------------------------------------------------------------------------

## 5. QC5 (B7 and three exotic leads). One FFT per statistic: heavy Fourier coefficient (upper bound) and autocorrelation (SQ lower bound)

**Bottleneck.** B7: LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined). Its next step tests H1
of IDEA-20261017-e3a6f1, including "correlation with characters of Z/N". The same instrument decides:
- LEAD-EXO-ml-learned-models (its learnability control);
- the digit-character family of LEAD-EXO-coordinate-statistic-leakage;
- the unblock threshold of LEAD-EXO-hnp-advice-leakage ("exponent 2*beta vs 1/2").

**External ingredients.**
- Akavia, Goldwasser, Safra, "Proving hard-core predicates using list decoding", FOCS 2003, 146-157.
  - Retrieved via search: the list-decoding framework and a new heavy-Fourier-coefficient learning
    algorithm over Z_N. I did not read the theorem text.
- Blum, Furst, Jackson, Kearns, Mansour, Rudich, STOC 1994 (SQ dimension via pairwise correlations),
  and Yang, COLT 2002 (Omega(d/log d) for SQ dimension d).
  - Retrieved via search, abstract level.
- Feldman-Guzman-Vempala (2017), SQ simulation of bounded-precision gradient methods: recalled.

Provenance: retrieved.

**Mechanism.** For a bounded statistic s on E(F_p), put g_s(k) = s(kP) on Z/N.
- tau_s = max_{alpha != 0} |g_s^(alpha)|.
- gamma_s = max_{d != 0} |A_s(d)|, the centred autocorrelation (the inverse transform of |g_s^|^2).

Upper bound. The queries s(cQ + aP) = g_s(ck* + a) are computable from the target.
- A heavy coefficient is found offline in poly(log N, 1/tau) evaluations.
- O(1/tau^2) samples estimate one phase, and O(log N) scalings c recover k*.
- Total O~(log N/tau_s^2), which is sub-rho iff tau_s >= N^{-1/4+eps}. This is the HNP lead's own
  threshold.

Lower bound, SQ scope. If gamma_s is at the random level (about N^{-1/2}), the shifted family has
SQ dimension d = N^{Omega(1)}. Pairwise correlations at most gamma_s give d of order 1/gamma_s or
gamma_s^{-1/3}, depending on the convention. SQ algorithms, including bounded-precision gradient
training on these features, then need d^{Omega(1)} queries at constant tolerance.
- I have not read the exact theorem, so the exponent (for example Yang's Omega(d/log d)) is not
  claimed. The ML disposition below is conditional on it.

Both numbers come from one length-N FFT per statistic per curve.

**Representation-operation pair.** Coordinates, or the Miller value U(Q) in F_p^* (R1/R3). Sigma is
the affine maps k -> ck + a on the logarithm, realised by known multiples. **Trichotomy:**
coordinate-dependent.

**SO codes touched (quoted).**
- SO-TORS, LEAD-STR-torsion-module-leak: "[...] A non-homomorphic point statistic is a function of the
  encoding of Q. Using it is index calculus or a generic query, and partial information about k on the
  point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). [...] Scope: prime-order G, any
  l != N."
  - Premise escaped: the sqrt(M) penalty assumes the M consistent candidates are enumerated. List
    decoding of a heavy coefficient avoids that, so the price is O~(1/tau^2), and QC5 measures tau.
- SO-PAIR, LEAD-TRF-second-torsion-direction: "Balasubramanian-Koblitz: [...] an F_p-rational
  graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and
  supersingular curves over F_p, prime N."
  - Premise: a homomorphic or bilinear transfer. U is non-homomorphic and outside it.
- SO-NET, LEAD-EXO-elliptic-net-eds. The statement has no Scope clause; the premise part reads:
  "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k
  (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead) [...]".
  - U(Q), evaluated from Q's coordinates alone, is not a net query. The factorisation
    U(kP) = c*r_k*C^{k/N} of K2, with r_k = psi_{k-1}/psi_k, reintroduces an integer-k net value that
    is not computable from kP without k. So K2 adds nothing beyond U itself (killed as a transfer,
    K12). What remains is exactly QC5's spectral test on k -> chi(U(kP)).

**First discriminating step.**
- Exact FFT over Z/N of g_s for a frozen registry:
  - chi(U(kP)) for characters chi of F_p^* of order 2, 3, 4, on special and matched random p;
  - the digit characters of x;
  - the census statistics;
  - the ML lead's feature map.
- Sizes: N in {2^16, 2^20, 2^24}, 3 curves each; computing all kP costs N additions.
- Controls: a planted-homomorphism positive control and a random-relabelling null.
- Report sqrt(N)*tau_s and sqrt(N)*gamma_s against the maximum of N Gaussians.

**Outcomes -> dispositions.**
- All statistics at the random level (predicted, H6).
  - Miller H1 closed (U is a hash at the Fourier level): LEAD-TRF-miller-cocycle-nonhom-transfer
    closed_obstructed(measured).
  - Digit-character family closed.
  - LEAD-EXO-ml-learned-models closed_obstructed(theorem, SQ scope) for these features. This is
    conditional on fixing the SQ-dimension statement used; with only the d^{Omega(1)} form it reads
    "no SQ learner below N^{c}" for an explicit c to be read from the source.
  - The HNP lead stays open_blocked, with the unblock threshold made precise: tau >= N^{-1/4}.
- Any statistic whose sqrt(N)*tau_s grows with N: open_next_step, priced at O~(log N/tau^2) against
  matched rho.

**Tier.** X: a heavy coefficient would be an exponent move. **Predicted gain.** 0 bits (H6). My prior
for a heavy coefficient at N >= 2^20 is under 5 percent.

**Cost.** One day. Compute: seconds to minutes per cell.

**Self-kill risk.** High overlap.
- LEAD-EXO-dl-character-sum-pseudorandom already measured log-domain character sums of factor-base
  indicators at 2^20-2^26 ("R = C_EC/C_null is flat at about 1.28-1.34").
- The HNP lead's conversion has the same threshold.
- New here: the SQ (autocorrelation) direction, and applying the test to chi(U) and to learned
  features. Ranked last.

**--match phrasings.**
- Own (revised): "Fourier transform over Z/N of a character of the Miller cocycle value U(kP) as a
  list-decoding test".
  - Top: LEAD-EXO-miller-pairing-cocycle (13), LEAD-TRF-miller-cocycle-nonhom-transfer (8).
  - The first-pass own phrasing reached only LEAD-EXO-coordinate-statistic-leakage (5).
- Plain: "does any function of the point coordinates correlate with a character of the discrete log".
  - Top: LEAD-EXO-dl-character-sum-pseudorandom (13), LEAD-EXO-ml-learned-models (10).
- Obstruction vocabulary: "non-homomorphic point statistic gives partial information about k at less
  than sqrt(M) cost".
  - Top: LEAD-STR-torsion-module-leak (10), LEAD-TRF-one-point-self-pairing (10).

---------------------------------------------------------------------------------------------------

## 6. Killed candidates (my own) and what changed from the earlier draft

Killed:

- **K1. The membership-degree floor (the earlier draft's C2).**
  - Its PC-degree lemma is trivial: the generators already have degree B.
  - Its Macaulay-rank corollary is the CRT grid ceiling already in H-ICEX-6ca21f ("F_p[x1..x5]/<g_V(x_i)>
    is isomorphic to functions on the grid V^5"), with the coordinator's prior of 0.95.
  - The degree statement is also in EV-PFDR-f71d7f.
  - Kept only as the G1 row of QC1.
- **K2. Fiat-Naor / Hellman inversion of the m-sum map** (3SUM-indexing upper bounds, GGHPV 2020;
  Kopelowitz-Porat 2019, recalled).
  - In QC1 coordinates it gives tau + 2mu >= 2m or tau + 3mu >= 3m, strictly worse than table splits.
- **K3. Kane-Lovett-Moran near-linear linear decision trees for k-SUM** (JACM 2019, recalled).
  - They need an order compatible with addition, which Z/N lacks.
- **K4. SGGM Theorem 4.2 as an algorithm.**
  - Free factoring with free linear algebra gives (m! N)^{1/m}; charging linear algebra gives R_m.
    It is the frame of QC1, not a lead.
- **K5. DKM non-adaptive bounds on relation collection.**
  - IC is not generic. The crypto audit already placed the non-adaptive arms on the DKM line
    (canonical-entries*T/(r/A) = 0.739-1.432). Nothing is left to decide.
- **K6. Yun multi-instance bounds for Table B.**
  - The board is one target, and SO-MULTI already covers batches.
- **K7. Sub-quadratic sparse linear algebra.**
  - It would change only m = 3 in R_m.
  - Known finite-field sparse solvers (Casacuberta-Kyng 2022, recalled) stay above exponent 2 for
    these shapes, so H2 stands.
- **K8. Res(xor) / parity-decision-tree lower bounds for SAT-PDP (B4).**
  - General Res(xor) lower bounds are open.
  - The measured alpha ~ m already decides through QC1. Deferred.
- **K9. Unconditional closure of KN-OPEN-020.**
  - It implies circuit lower bounds for an NP search problem. Closures must stay scoped by solver
    class and presentation, as QC1, QC2 and QC4 are.
- **K10. A curve-aware GGM with point transport, for LEAD-STR-class-group-ecdlp-bridge.**
  - H-CLGP-63f471 already specifies the simulator (S1).
  - My increment is small and is recorded as side flag F6:
    - point maps between isogenous copies of G are known-scalar maps up to a computable eigenvalue,
      so they are simulable with O(log N) overhead;
    - the simulation fails exactly at a ray-class Cl_n(O) vectorization oracle, which is ECDLP
      itself.
- **K11. A generic-graph hitting-time bound Omega(h/w) for the Teske F_{p^6} trapdoor (B7).**
  - The weak set is reached by the structured ISO-1 walk at 1e5-1e8 F_p multiplications, so the
    random-placement lower bound does not apply. The lead's own measurement decides it.
- **K12. Miller K2 as a transfer.**
  - r_k is an integer-k elliptic-net value, so U(kP) = c*r_k*C^{k/N} carries no information beyond
    U(kP) (SO-NET premise). Folded into QC5.
- **K13. Batched or advised canonicalisation as a way around QC4.**
  - Not killed: it is recorded as QC4's open residue.

What changed from the earlier draft at this path:

1. The region lemma now fixes oracle semantics.
   - The draft's "R_m = {tau < m/2 - 1, tau + mu < m - 1}" is the find-one region without the
     linear-algebra cap. It mis-states m = 3 (it needs tau < 0, not < 0.5) and the list-all region at
     m >= 5 (tau < m - 3).
   - Its WDSat row said "needs tau < 0.5" at m = 3, which contradicted its own region.
2. Two draft flags are withdrawn:
   - the revisit_when wording, which is correct at the re-optimised B;
   - the small-root normalisation, which reconciles.
3. My first-pass model reproduced the draft's W = 2 digit margins within a bit (+30.4, +32.7, +36.0,
   +33.7). The uniformly favourable recount gives +29.4, +31.2, +34.3 and +32.7. There are four
   differences:
   - The closure needs H2. Without linear algebra charged, the 521-bit cell fails (-10.8), and the
     draft did not say so.
   - H4 carries the closure only at m >= 6 (128 and 256 bits) and m >= 7 (384 and 521 bits), in the
     s ~ 2^{m-1} band. There a weak form, H4w, suffices. Floor A + H2 alone closes the lower
     arities.
   - The W-ary residual is larger here: W >= 64 at 384 bits is open (-2.6 at W = 64), where the
     draft had +2.2. Cells within 2 bits are now marked undecided.
   - The draft's "scope: unchained" is sharpened to "expanded reduced presentation". Unexpanded
     presentations with x_i kept as unknowns escape the floor.
4. The H4 toy check and the invariant census are new outcomes, produced this session.
5. QC3 is new. The draft had no live B3 candidate.
6. The draft's citations marked "retrieved" were re-checked this session. The labels above are only
   for what I fetched or searched now.

## 7. Side flags for the coordinator (no action taken)

- **F1. Binary SAT threshold missing its linear-algebra cap at m = 3.**
  LEAD-ICB-decomposition-encoding-and-sat's obstruction says "beating rho needs alpha < m/2 - 1". With
  the B^2 linear-algebra cap it is alpha < min(m/2 - 1, m - 3), or alpha < m - 3 for list-all oracles.
  At m = 3 that is alpha < 0, so no oracle can cross. This is consistent with KN-FIND-aa2efc (a free
  m = 3 oracle costs 2^68.58 against 2^60.81).
- **F2. The m = 5 arity row assumes a list-all oracle.** In RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md
  section 2.4 the m = 5 row ("T_dec << p^{1/2}") holds only for list-all oracles. For a find-one oracle
  it is T_dec << p^{3/10}. The EXP-ICEX-153c34 threshold already uses the find-one value.
- **F3. Measured mitm exponents match the generic-split predictions.** The finite-size fitted mitm
  exponents 0.67/0.75/0.60/0.571 match the generic-split predictions at the engine's default table
  arity (m+1)//2. The j = m vertex was never run; that is QC3.
- **F4. The G1 verdict already follows from the region.** The coordinator's ceiling audit in
  H-ICEX-6ca21f (A*L^5 floor, 1,041-8,438 times T) is QC1's G1 placement: T is the find-one boundary
  tau = 1.5 at m = 5. Neither 153c34 arm varies L at fixed q, so the contract does not identify tau.
  Running arm M tests H3 only.
- **F5. The CHW EC section is still unread.** The PDF fetch failed twice this session (the tool's
  safety check returned no verdict). The crypto audit's stated gap ("The EC statement could not be
  extracted") stands.
- **F6. Increment to H-CLGP-63f471.**
  - Add point-transport oracles between isogenous copies to CAGG. They are simulable with O(log N)
    overhead by eigenvalue computation.
  - The simulation fails exactly at a ray-class Cl_n(O) vectorization oracle, and that oracle is
    ECDLP. This is the "one bridge" the lead's discriminator asks to be named.

## 8. Files (all written this session under scout/)

- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc1_region_check.py and qc1_region_check.out
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc2_digit_writability.py and qc2_digit_writability.out (first pass: linear algebra free, then H2 charged with 2W^s columns)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc2_digit_writability_v2.py and qc2_digit_writability_v2.out (uniformly favourable recount, undecided band, H4-dependent cells with required support)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc2_floorA_by_m.py and qc2_floorA_by_m.out (floor A + H2 margins per arity, W = 2)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc2_h4_check.py and qc2_h4_check.out (exact toy H4 check)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc3_fullsumset_model.py and qc3_fullsumset_model.out
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/qc4_invariant_census.py and qc4_invariant_census.out (exact toy census)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/match_log_query_communication.txt (both match tools, 15 + 3 phrasings)
- /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/qc/obstruction_quotes.txt (verbatim obstruction statements extracted from the lead YAMLs)

Older scripts in scout/ (digit_floor*.py, digit_asym.py, split_out.txt, W384_out.txt, match_log.txt)
belong to the earlier draft. Nothing above relies on them.
