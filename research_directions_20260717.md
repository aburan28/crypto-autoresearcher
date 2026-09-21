# Research Director Submission: New Falsifiable Directions for Non-Generic ECDLP over Ordinary Prime Fields

Date: 2026-07-17
Role: Coordinator / Research Director (per AGENTS.md contract)
Scope: generated toy curves, public benchmark instances, synthetic data only. No wallets, production keys, accounts, or unauthorized systems are targeted by any proposal below.
Baseline convention: Pollard rho with negation, `0.886·sqrt(n)` group operations, single-target, small memory. `n` = prime subgroup order, `q = p` = field size, `n ≈ q`. All costs below are fully charged (setup + failed attempts + verification + sparse linear algebra + memory traffic + advice + descent).

---

## 0. Required input review — what was read

Staged copies in `/Volumes/Volume/crypto-autoresearcher/inputs/` (originals under `/Volumes/Volume/git/autolab/`):

1. `autolab_research_ledger.md` (2,250 long lines, 9 sections)
2. `ecdlp_ic_research_ledger.md` (648 lines, 6 sections)
3. `non_generic_transfer_search_20260610.md` (389 lines, read in full by the Director)
4. `bibliography.json` (10 primary-source records, read in full)
5. Referenced frontier artifacts: experiment contracts `p1471`–`p1480` (two-large-prime cycle diagnostic, 2LP occupancy exponent boundary, sparse-subgroup FFE/log compression, CM-endomorphism stable deck, residual-character support concentration, m-ary sparse-deck exponent boundary, serial-S3 state compression, S3 subgroup norm composition, factor-log feature compression, bitvector serial-S3 membership), plus the ledger-internal negative-result tables, open-frontier lists, baselines, and literature maps.

Machine-readable inventory built: `inputs/ledger_inventory.json` — **2,707 records**, validated by `json.load`. One record per ledger entry, with fields {mechanism, representation, exploited structure, factor base, relation shape, relation generation, compression, linear algebra, descent, bottleneck, outcome, negative boundary, next branch}. No sampling by recency: every section (open frontier, active hypotheses, negative results, positive signals, baselines, literature map, graph-index frontier, negative controls, dated continuations) of both ledgers was parsed in full.

**ID families covered:** ECFG-H (382 hypotheses), ECFG-P (1,273 positive-signal rows), ECFG-NR (504 negative results), ECFG-N (101), ECFG-0## (62), ECFG-IR/RT/MX (5); ISO-AR (122), ISO-SP (4), ISO-CW (3), ISO-RM (2), ISO-PK (1); TRANSFER-H (8), TRANSFER-NR (53), TRANSFER-P (64); SHA1-H/N/P (17, off-ECDLP sibling program); PO## probes (21 records / 20 distinct, PO45–PO96 + PO-transfer-001..007); H325–H329; bare P#### (P1085, P1385, P1399, P1434, P1449); NR-1078/1079/1086; 37 frontier-question records; 17 baseline-convention rows; 8 literature-map rows; 10 experiment-contract records (P1471–P1480).

### 0.1 Ledger mechanism map (40 clusters, condensed)

Dominant clusters by size and recency: rank-packet column closure (370 rows); low-term/top-k leaf selectors (269); quadratic-root public-factor surfaces (209); factor-substitution holdout descent (198); genus-2/Prym/cover transfer (159); carrier-quotient residual frontiers (145); branch-diversity multiplicity (145); direct-source certificates (144); volcano orientation/kernel reconstruction (123); source-form motif generation (104); strict-bridge certificates (84); public-feature support prediction (74); exact-FFE product-tree batching (56); width amortization (42); summation-polynomial point decomposition (37, negative); CM-endomorphism stable decks (14, negative); self-pairing volcano torsion (11); two-large-prime occupancy (5, negative: floor exponent 2/3); m-ary summation exponent boundary (RT-1476: m≤3 no sub-rho α; m=4 needs α<1; m=5 needs α<3/2); serial-S3 state compression (negative: forward L^1.112, backward L^1.675); S3 subgroup norm composition (negative: resultant exponent 1.979); factor-log features (negative); bitvector SMT membership (negative: timeout at L=4).

### 0.2 Dominant vocabulary (must-be-escaped set)

rho/below-rho · public selector/guard/gate/scout · source-form/source-cost · top-k · salt/phase corridors · leaf · window/holdout · low-term total2/total10 · certificate/direct-source/bridge · rank packet/deficiency/free columns · support motif ([8,11]… vs [2,4]) · carrier-quotient residual class · transfer (10472 etc.) · factor substitution/family-holdout · charge cap/stop-rule/root-saved · prefix/width amortization · target/blind descent · factor base/deck/anchor · ECFG functional graph/reverse index · Semaev S3/S5 · large prime/2LP occupancy · x^L=1 sparse deck · Berlekamp–Massey · resultant row-norm · residual character · CM endomorphism j=0 · bitvector/Z3 · Prym/Kummer/Hesse · volcano/self-pairing/torsion · negation symmetry · streaming/10x gate/amortization.

**Vocabulary-compliance check: 11 of the 12 candidates below open with a primitive outside this set** (jets, incidence reporting, displacement rank, elliptic nets, Newton polytopes, isotypic idempotents, transfer operators, tensor networks, path algebras, and three barrier theorems). A3 (structured matrices) partially reuses "factor base / relation matrix" but its new object (displacement rank of AP-support matrices) is absent from the ledger.

### 0.3 Closed/control-only territory honored

Treated as negative controls unless the measured obstruction is explicitly broken: same-field isogeny invariants; scalar Weil pullback; explicit 2LP advice graphs (ECFG-NR-1471, ~107x of 11·rho); joint factor/LP Krylov; pair-residual character buckets (ECFG-NR-1475, δ ≈ 0.02 « 1/4); non-invariant CM endpoint decks (ECFG-NR-1474, zero invariant cosets); materialized serial-S3 backward states (L^1.675); dense composed resultants (ECFG-MX-1478, exponent 1.979); source selectors/post-hoc scheduling without an honest hit generator; relation validity without ECDLP recovery; preprocessing wins losing to rho after charging. Each candidate below names the obstruction it avoids and the new operation responsible.

---

## 1. External literature search log (documented, primary sources)

Searched 2026-07-17 via web search; findings below distinguish *found* (with source) from *not found after documented search*.

| Family | Result |
|---|---|
| Pollard rho / generic bounds | Foundational: Pollard 1978; Shoup EUROCRYPT 1997 generic-group Ω(√n). Baseline barrier, not a non-generic impossibility theorem (ledger literature map agrees). |
| Semaev / symmetrized summation | bibliography.json: Semaev 2004/031; Faugère–Huot–Joux–Renault–Vitse EUROCRYPT 2014; Amadori–Pintore–Sala 2017/609; Kousidis–Wiemers 2015/1121 (first fall degree). |
| Rational-map / cover factor bases | bibliography.json + transfer doc: Gaudry 2009; Joux–Vitse 2012; Petit–Kosters–Messeng 2016 (per ledger litmap); Tian cover attack (per transfer doc). |
| Weil descent / trace-zero | GHS family and scalar-pullback negatives per transfer doc and ledger (NR-022, PO-004). |
| Gröbner / SAT / crossbred / resultant / non-Gröbner | bibliography.json: FPPR EUROCRYPT 2012; Shantz–Teske 2013/596; Karabina 2015; McGuire–Mueller 2017/1262 (Gröbner-free, still worse than rho per authors); Trimoska–Ionica–Dequen AFRICACRYPT 2020 (SAT). |
| Isogeny / correspondence / Prym / Kummer / Jacobian transfer | Smith genus-3 transfer, Tian genus-3 cover, Lange–Ortega, Lombardo–Lorenzo García–Ritzenthaler–Sijsling, Howe gluing, Eid explicit isogenies (ledger litmap). |
| Endomorphism / Frobenius | GLV/GLS and automorphism-accelerated rho (recollection, standard); ledger CM-deck negatives P1474. |
| Arithmetic dynamics / EDS | Shipsey thesis 2000; Stange "The Tate pairing via elliptic nets" (Pairing 2007) (recollection). No sub-rho EDS-DLOG mechanism found. |
| Hasse-derivative / jet-scheme lifting of EC addition | **No ECDLP application found.** Adjacent: Silverman, "The xedni calculus and the ECDLP" (Designs, Codes and Cryptography; confirmed via search) and Jacobson–Koblitz–Silverman–Stein–Teske, "Analysis of the xedni calculus attack" (CACR Waterloo 1999; confirmed) — that is lift-to-characteristic-0, not nilpotent jets. Smart / Satoh–Araki anomalous attacks use p-adic lifting but are predicate-based (#E = p). Buium arithmetic differential equations (recollection): existence theory, no algorithm. |
| Tropical / Newton polytope of summation systems | **No ECDLP application found.** Adjacent: tropical elliptic curves as combinatorial objects (arXiv:2507.21958); Castryck–Denef–Vercauteren use Newton polytopes for zeta functions (ePrint-listed). Sparse elimination theory: Bernstein–Kushnirenko–Khovanskii; Canny–Emiris 1993/2000; Huber–Sturmfels 1995 (recollection). |
| Output-sensitive finite-field incidence reporting | Counting bounds found: Stevens–de Zeeuw, Bull. LMS 49 (2017) 842–858, arXiv:1609.06284, I ≲ |P|^{11/15}|L|^{11/15}; Rudnev, Combinatorica 38 (2018); Iosevich et al., arXiv:2303.00330; Vinh 2011; Bourgain–Katz–Tao 2004. **No algorithmic output-sensitive reporting primitive over F_p, and no ECDLP relation-harvesting use, found.** |
| Arithmetic-dynamical transfer operators / spectral invariants | Transfer-operator literature is pure dynamics (Ruelle; Baladi; Mayer–Mühlenbruch–Strömberg 2012, Hecke triangle groups — all confirmed via search). **No ECDLP/DLOG application found.** Adjacent: Teske's random-walk analyses of Pollard rho (recollection: Teske 1998/2001). |
| Noncommutative correspondence / path algebras | Path-algebra Gröbner theory found: Waweru–Maingi, arXiv:2306.06457 (2023); Farkas–Feustel–Green framework (via VT thesis). **No cryptographic/ECDLP application found.** Adjacent: Charles–Goren–Lauter isogeny-graph path hashing (J. Cryptology 2009, recollection). |
| Tensor-network / separator-rank contraction of Semaev-type tensors | Search returned no direct ECDLP/Gröbner application. Recollection: tensor-network #CSP counting (Kourtis–Chamon–Ruckenstein–Mucciolo, SciPost Phys. 7, 060 (2019)); Markov–Shi treewidth contraction. NOVELTY-UNVERIFIED. |

Novelty labels used below: LEDGER-NEW (absent from the 2,707-record inventory); LITERATURE-ADJACENT; NOVELTY-UNVERIFIED; POSSIBLY NOVEL (no equivalent mechanism after the documented search above). No candidate is claimed globally novel without this evidence.

---

## 2. Novelty method

Each candidate C carries a semantic fingerprint F(C) = (algebraic object; public operations; hidden structure exploited; information discarded; information retained; relation-generation primitive; compression primitive; rank mechanism; descent mechanism; dominant cost exponent). C is rejected as duplicate if any ledger entry shares the essential fingerprint under terminology change. Five nearest ledger IDs are listed per candidate with the exact mathematical distinction (wording distinctions insufficient).

---

## 3. Candidate set A — conservative extensions of known work

## Candidate: A1 — Tangent-split summation (first-jet / dual-number decomposition of the addition relation)

### One-sentence mechanism
Exploit the linearity of the EC addition law in nilpotent directions over F_p[ε]/ε² to split m-point relation generation into a cheap exactly-linear tangent screen plus a nonlinear residual, reducing per-relation solving cost C below the serial-S3 state-growth cost measured at L^1.675 (NR-1477), with B = rho-exponent 1/2 as the bar.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (xedni calculus lifts to char 0 — different operation; anomalous p-adic lifts are predicate-based; Buium delta characters are non-algorithmic).

### Semantic fingerprint
F(A1) = (jet scheme J¹ of the summation variety over F_p[ε]/ε²; dual-number EC arithmetic and F_p-linear solves; tangent-bundle linearity of the group law; jets of order ≥ 2 discarded; zeroth-order equation + first-order variational equation retained; relation generation = linear ε-consistency screen then exact residual test; compression = replacing nonlinear state recursion by linear algebra; rank = more low-degree equations per candidate; descent = standard large-prime descent on surviving relations; dominant exponent = 1/2 unless the screen's cost/survival trade measurably beats it).

### Nearest ledger entries
- ECFG-NR-1477 (serial-S3 state compression): same relation family; distinction — they materialize polynomial states serially and measured density blow-up; A1 never builds serial states, it splits each candidate a priori into linear + nonlinear parts. Different solving order, not different encoding.
- P1480 (bitvector SMT membership): same membership question; distinction — SMT is a backend swap on the same equations (timed out at L=4); A1 changes the equation set itself (adds exact linear equations from the tangent direction).
- ECFG-NR-1399/1400 (x-only S3 quotient certificates): same S3 object; distinction — quotienting removes information; A1 adds an infinitesimal direction (more equations, more unknowns, but linear ones).
- ECFG-H639/640 (summation-polynomial hypotheses): parent relation family; distinction identical to NR-1477 point.
- PO-004 / NR-022 (scalar Weil pullback): also "adds variables"; distinction — Weil variables are new field scalars with nonlinear coupling; ε-directions are nilpotent and the ε-block is exactly linear in the jet coordinates (formal-group linearization).

### Nearest literature
Silverman, xedni calculus (Designs, Codes and Cryptography; confirmed in search) and Jacobson–Koblitz–Silverman–Stein–Teske analysis (CACR 1999): they lift points to Q and impose global dependence — assumptions failed asymptotically; A1 never leaves F_p and makes no independence heuristic. Smart / Satoh–Araki anomalous attacks (confirmed references in search): p-adic lift works only when #E = p, excluded here. Buium, arithmetic differential equations (recollection): proves δ-characters exist on abelian varieties; gives no relation-generation algorithm. Gap: nobody has tested whether the tangent screen buys a cost/survival trade for point decomposition.

### Target family
Ordinary prime-field curves, prime-order subgroup, p ≥ 2^7 toy sizes up; exclude anomalous (#E = p, already polynomial-time), singular, supersingular (embedding-degree channel), char 2/3.

### Full algorithmic path
1. Factor base: standard x-interval FB of size B. 2. Relation generation: for each candidate (m−1)-tuple, form the dual-number addition chain; the ε-block is an F_p-linear system in the jet coordinates — solve it exactly (cheap); survivors get the exact zeroth-order S_m test. 3. Witness extraction/verification: tuple + tangent vector; verification is ordinary EC arithmetic (exact, verifier-independent). 4. Relation probability: p_m · σ, σ = tangent-survival rate (measured, not assumed). 5. Matrix: standard sparse relation matrix, dimensions B × #relations, weight m-ish. 6. Factor-log calibration: standard. 7. Descent: standard LP descent. 8. Offline/online: FB and tangent-screen precomputation offline; target tests online. 9. Memory/parallelism: standard sparse; screen is embarrassingly parallel. The only new claim is the per-candidate cost vs survival trade; if no measured edge appears, the attack is INCOMPLETE but the experiment is complete and decisive.

### Cost model
Classical Semaev route: need ≈ B relations, per-candidate cost C_nonlin, hit probability p_m ≈ B^{m−1}/((m−1)!·n); total ≈ (B/p_m)·C_nonlin + LA(B) + descent. Tangent-split: total ≈ (B/p_m)·(C_lin + σ·C_nonlin) + LA(B) + descent. Win requires C_lin < (1−σ)·C_nonlin at equal p_m, sustained with exponent margin vs 0.886·√n. All three quantities measurable at toy scale.

### Why the existing negative results do not already kill it
NR-1477 measured serial polynomial-state growth; P1480 measured an SMT backend; both keep the equation set fixed. A1's new mathematical operation is the a priori linearization (jet split), which neither tried. The measured obstructions (state density, solver timeout) are stage-specific, not relation-family-specific.

### Likely fatal obstruction
Information conservation: at F_p-points, the tangent space of the summation variety may be *determined by* the zeroth-order solution set (the ε-system is then implied, σ ≈ 1, zero gain); or requiring ε-consistency is generically stronger than the base relation (σ collapses, probability dies). Either extreme kills the trade. D1 formalizes this as a model question.

### Minimal falsifying experiment
Toy primes p ∈ {101, 211, 431} (plus 1009 stress), seeds 20260717..20260722, freshly generated ordinary prime-order curves. Measure σ, C_lin, C_nonlin, p_m, and end-to-end relation yield per F_p-op vs a serial-S3 harvester at identical FB. Positive control: the standard S3 harvester must reproduce ledger relation counts. Negative control: random non-relation tuples must be rejected by the tangent screen at the measured σ (no leakage).

### Quantitative promotion gate
Complete charged cost (relations + LA + descent) fits exponent ≤ 0.49 across the three sizes with the 1/2 crossing excluded at 95% confidence; OR a ≥ 4x per-relation cost ratio at equal hit rate sustained across all sizes (flagged necessary-not-sufficient).

### Proof track
Lemma: over F_p[ε]/ε² the ε-component of the addition law is an F_p-linear form in the jet coordinates (true by formal-group linearization). Theorem needed: asymptotic law for σ(m, B, n).

### Disproof track
Prove the ε-system's solution set equals the Zariski tangent space at zeroth-order solutions (σ ≡ 1), or measure C_lin + σ·C_nonlin ≥ C_nonlin across all sizes — kills A1 as scoped negative.

### Reproduction artifact
Contract `research/EXP_JET1_contract.md`; implementation `experiments/ecdlp_jet/jet1_tangent_split.sage`; result `experiments/ecdlp_jet/jet1_tangent_split_result.json`; audit `experiments/ecdlp_jet/jet1_verify.sage`; ledger ID JET-H-001.

---

## Candidate: A2 — Output-sensitive finite-field incidence reporting for chord harvesting

### One-sentence mechanism
Replace B²-candidate enumeration by an output-sensitive incidence-reporting primitive over F_p² (dual transform + algebraic partition/range searching) that lists only the s-rich lines of the factor-base chord arrangement, reducing relation-discovery cost C of the harvesting subproblem P below the ledger's own measured floors (RT-1472: 2LP exponent floor 2/3; frontier A39: pair-output exponent α₂ < 3/2 required at B ≈ q^{1/5}), with B = rho 1/2.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (incidence *counting bounds* exist — Stevens–de Zeeuw, Rudnev, Iosevich; no algorithmic output-sensitive *reporting* primitive over finite fields found after documented search, and no ECDLP harvesting use found).

### Semantic fingerprint
F(A2) = (incidence graph between FB points and chord/target-shifted lines in F_p²; duality + partition/range queries; EC chords are a non-generic, algebraically structured line family (each line determined by two curve points); incidences below richness s discarded; s-rich lines and their witness tuples retained; relation generation = output-proportional reporting (cost ∝ output, not candidate space); compression = dual-space partition tree, never materialize the pair surface; rank = unchanged relation matrix, harvested cheaper; descent = standard 2LP descent; dominant exponent = reporting cost Õ(B + I) target vs measured enumeration floors).

### Nearest ledger entries
- ECFG-RT-1472 (2LP occupancy exponent boundary): measured floor 2/3 and names the loophole verbatim — "implicit deck with setup o(L), query o(√L)". A2 is the first candidate proposing a concrete primitive for exactly that loophole; distinction — they enumerate/hash decks; A2 reports via duality.
- ECFG-NR-1471 (explicit 2LP deck, ~107x of 11·rho): distinction — explicit advice graphs vs implicit reporting; A2 stores no pair table.
- ECFG-NR-1434 / P1434 (B⁴ explicit terminal-witness boundary): closed *only in the explicit-edge model* by the ledger's own scope statement; A2's distinction is precisely never materializing edges.
- Frontier A39 (α₂ < 3/2 with output-sensitive source opening): A2 is that question instantiated with a named primitive and a barrier companion (D3).
- ECFG-NR-1404/1405/1407 (predicate factor bases): distinction — those are post-hoc selectors of FB membership; A2 changes the enumeration algorithm, not the FB predicate.

### Nearest literature
Stevens–de Zeeuw, arXiv:1609.06284 (Bull. LMS 2017): I ≲ |P|^{11/15}|L|^{11/15}; Rudnev, Combinatorica 38 (2018) point-plane incidences; Iosevich et al., arXiv:2303.00330; Vinh 2011 universal bound I ≤ |A||L|/p + (|A||L|p)^{1/2}; Bourgain–Katz–Tao 2004. Ahmadi–Shparlinski sum-product estimates on elliptic curves (per ledger A39; exact venue unverified). Over ℝ, output-sensitive reporting exists (Chan; partition trees — recollection). Gap: no finite-field reporting algorithm with subquadratic setup and output-proportional marginal cost is known to the Director; D3 tests whether EC chord families are even rich enough for it to matter.

### Target family
Ordinary prime-field curves, prime-order subgroup; B grid tied to n^{1/4}, n^{1/3}, n^{2/5}; exclude tiny FB (B < 8) and non-prime fields.

### Full algorithmic path
1. FB: x-set of size B. 2. Relation generation: dualize FB points and chord lines; report s-rich incidences (m=3: third curve intersection in FB; m=4/5: target-coupled lines through −R with remaining intersections in FB). 3. Witness: explicit collinear tuple, verified by EC addition (exact). 4. Relation probability: measured incidence statistics vs Vinh-type prediction. 5. Matrix: standard sparse relation matrix filled from reported incidences only. 6. Calibration: standard. 7. Descent: standard 2LP descent (RT-1476 thresholds: m=4 needs α < 1, m=5 needs α < 3/2). 8. Offline: FB dual structure (must be o(B²) — the crux); online: reporting + descent. 9. Memory: partition structure target O(B·polylog B), streaming reporting.

### Cost model
Enumeration baseline: Θ(B^{m−1}) candidate tests. Target reporting cost: S(B) setup + I·T_rep, with I = #reported incidences ≈ B^{m}/(c·n^{m−2}) under random-model statistics. Fully charged total = S(B) + I·T_rep + LA(B) + descent. Win requires this < 0.886·√n with the m=4/5 relation-supply regime of RT-1476. At m=3 the supply arithmetic (I ≈ B³/(3n), forcing B toward n^{1/2}) is already adverse — stated honestly; A2 lives in the m=4/5 regime or dies.

### Why the existing negative results do not already kill it
Every measured floor (NR-1471, RT-1472, NR-1434) assumed enumeration or explicit materialization. The new mathematical operation is output sensitivity with subquadratic setup — the exact loophole RT-1472 left open. Nothing in the ledger measures reporting primitives.

### Likely fatal obstruction
The primitive may not exist: partition trees rely on order/continuity unavailable over F_p; algebraic partitioning (Guth–Katz style) is a counting/existence tool, and converting it to listing likely reintroduces Ω(candidate) factors or constants that lose to B² enumeration at every toy size. Second kill: EC chord richness may be at the generic ceiling (D3), so I is too small at useful B.

### Minimal falsifying experiment
p ∈ {211, 1009, 4099}; B ∈ {n^{1/4}, n^{1/3}, n^{2/5}}; seeds 20260717..20260722. Implement (i) exact enumerator (baseline), (ii) dual range-searching reporter (grid-bucketing + algebraic partition variant). Measure setup cost, marginal per-incidence cost, and the full charged total vs the 2/3 and α₂ < 3/2 thresholds. Positive control: reporter output multiset must equal enumerator output exactly. Negative control: random non-EC line sets must not be reported more cheaply (guards against claiming generic bucket-sort as an EC mechanism).

### Quantitative promotion gate
Measured pair/tuple-output exponent α₂ < 3/2 at B ≈ q^{1/5} (the ledger's own A39 threshold) with setup o(B²) confirmed, and the complete-cost trend across three sizes pointing below 0.49; correctness alone is not the gate.

### Proof track
A finite-field reporting theorem: for algebraic line families of bounded degree in F_p², runtime O(B^{1+ε} + I·polylog B) with subquadratic setup — an algorithmic analogue of Pach–Sharir/Chan over F_p.

### Disproof track
D3 barrier: richness distribution of EC chord arrangements at the generic Stevens–de Zeeuw ceiling, plus a worst-case Ω(B²/I) reporting lower bound on grid-like families — would close A2 with a theorem.

### Reproduction artifact
Contract `research/EXP_INC1_contract.md`; implementation `experiments/ecdlp_incidence/inc1_report.sage`; result `experiments/ecdlp_incidence/inc1_report_result.json`; audit `experiments/ecdlp_incidence/inc1_verify.sage`; ledger ID INC-H-001.

---

## Candidate: A3 — Displacement-rank relation matrices from arithmetic-progression supports

### One-sentence mechanism
Constrain relation harvesting to supports forming short arithmetic progressions {x, x+d, …, x+(m−1)d} so the relation matrix has O(1) displacement rank (Toeplitz/Hankel-like), then solve with superfast structured algorithms, reducing the linear-algebra stage below generic sparse Wiedemann while paying a measured relation-probability penalty, B = rho 1/2.

### Status
CONJECTURE.

### Novelty classification
LEDGER-NEW; NOVELTY-UNVERIFIED (structured Gaussian elimination and block Wiedemann are standard; Toeplitz-by-design relation harvesting not found in the documented search).

### Semantic fingerprint
F(A3) = (relation matrix as a low-displacement-rank operator; AP-constrained harvesting; translation symmetry of support sets; non-AP relations discarded; AP relation families retained; relation generation = AP-tuple sieve (honest hit generator, not post-hoc filter); compression = displacement generator of size O(α(m+B)) instead of nnz entries; rank = full rank by choice of shift set D; descent = standard; dominant exponent = LA constant reduction, exponent unchanged unless it composes with m=5 supply).

### Nearest ledger entries
- PO63–PO73 anchor relation matrices: same object class; distinction — they schedule rows; A3 constrains the *support geometry* so the operator itself is structured.
- ECFG-P1440/1442–1444 (exact-FFE product-tree batching): distinction — they accelerate evaluation of fixed polynomials; A3 changes the matrix class, not the evaluator.
- ECFG-NR-1479 (factor-log feature compression): distinction — post-hoc low-dimensional structure in log vectors failed; A3 imposes structure a priori on supports and measures the penalty.
- PO72 (rank-many Krylov): distinction — solver-side residual budget; A3 changes what is solved.
- NR-1078/1079/1086 (remaining columns [6,7]): distinction — not a column-targeting selector; the support constraint is generator-level.

### Nearest literature
Kaltofen–Saunders 1991 (Wiedemann); Coppersmith block Wiedemann 1994; LaMacchia–Odlyzko structured Gaussian elimination 1991; displacement-rank complexity (Kaltofen; recollection); Bostan–Lecerf–Schost Tellegen transposition 2003. Gap: no one has *designed* relation supports to force operator structure in EC index calculus.

### Target family
Ordinary prime-field, prime-order subgroup, all m ≥ 3, standard exclusions.

### Full algorithmic path
1. FB: x-interval. 2. Relation generation: for shifts d ∈ D and base points, test AP-tuple membership against target-coupled summation (honest generator). 3. Witness: standard, exactly verified. 4. Relation probability: AP-conditional hit rate, measured vs random-support baseline. 5. Matrix: AP-induced Toeplitz/Hankel blocks; displacement rank α measured numerically. 6. Calibration: standard. 7. Descent: standard. 8. Offline: shift-set selection; online: AP sieve + structured solve. 9. Memory: displacement generator only.

### Cost model
Sparse Wiedemann: O(B·w) field ops, w = row weight. Structured solve: O(α²·B·polylog B). Win requires α = O(1) and AP penalty factor (probability drop) small enough that B does not inflate past the point where LA savings are swamped by relation supply cost. Both quantities measured.

### Why the existing negative results do not already kill it
The ledger's closed LA territory is solver-side (joint Krylov) or post-hoc (log features). No entry measures *designed* support geometry. The new operation is the support constraint creating an exactly structured operator.

### Likely fatal obstruction
AP conditioning is an extra algebraic constraint ≈ one more curve-point condition: hit probability collapses by a factor that grows with m, inflating B until the LA win is irrelevant; or the matrix is not exactly low-displacement because negation/quadratic twists break translation invariance of supports.

### Minimal falsifying experiment
p ∈ {211, 1009, 4099}; D = {1..64}; m ∈ {3,4}; seeds as above. Measure AP hit rate vs random-support baseline, numerical displacement rank α, structured-solve time vs Wiedemann at equal matrix. Positive control: standard harvesting reproduced at D = {0}. Negative control: random x-sets show no AP enrichment (guards against measuring coincidences of small fields).

### Quantitative promotion gate
LA share of fully charged total cost falls below 10% while the relation-stage penalty stays < 1.5x vs the best ledger baseline at equal toy size, sustained across three sizes; ultimate bar remains a complete-cost exponent trend < 0.49.

### Proof track
Theorem: AP-family harvesting yields displacement rank α ≤ f(m); plus the AP hit-probability asymptotic.

### Disproof track
Measured α growing like √B, or AP penalty ≥ n/B — either kills A3 as scoped negative.

### Reproduction artifact
Contract `research/EXP_STR1_contract.md`; implementation `experiments/ecdlp_structured/str1_ap_matrix.sage`; result `experiments/ecdlp_structured/str1_ap_matrix_result.json`; audit `experiments/ecdlp_structured/str1_verify.sage`; ledger ID STR-H-001.

---

## 4. Candidate set B — genuine representation changes

## Candidate: B1 — Elliptic-net (EDS) representation of the logarithm group

### One-sentence mechanism
Re-encode the ECDLP in the elliptic divisibility net (Shipsey/Stange), where Somos-type quadratic identities supply a two-parameter family of exact multiplicative relations among net terms, and test whether this non-generic relation supply reduces discrete-log recovery below the birthday bound that limits every generic walk, B = rho 1/2.

### Status
CONJECTURE.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Shipsey 2000; Stange, Pairing 2007 — nets compute pairings; no sub-rho EDS-DLOG mechanism found after documented search).

### Semantic fingerprint
F(B1) = (elliptic divisibility net over F_p; net double/add recurrence; Somos quadratic identities = free exact relations; sign/y-information discarded (net is an x-line-like quotient); full scalar divisibility structure retained; relation generation = recurrence collision sieve; compression = net terms as single field elements; rank = relation-module rank of Somos identities restricted to k-fibers; descent = index-calculus on net exponents; dominant exponent = 1/2 unless collisions beat birthday).

### Nearest ledger entries
- PO63–PO73 anchor relation matrices: distinction — ledger relations are harvested by membership tests; net relations come from a global algebraic recurrence (relation supply without per-relation search).
- ECFG Berlekamp–Massey recurrence log-compression rows: distinction — they compress logs *after* recovery; B1 generates relations *before* recovery; direction reversed.
- ECFG-NR-1473 (x^L = 1 sparse subgroup membership): distinction — one multiplicative identity; Somos gives a two-parameter family indexed by (i, j, k).
- PO92/PO93 (module rank 731/758; zero map-span surplus): distinction — their module is a point-label kernel; the net module is a one-dimensional recurrence module — different module, different invariant.
- NR-022 / PO-004 (scalar Weil): distinction — no field extension, no new scalars.

### Nearest literature
Shipsey, thesis 2000; Stange, "The Tate pairing via elliptic nets", Pairing 2007; Miller–Stange; division polynomials (standard). Gap: net-domain relation *supply* for DLOG was never measured; nets were used to *compute*, not to *relate*.

### Target family
Ordinary prime-field, prime-order subgroup, char ≥ 5; exclude singular curves and small embedding degree (pairing channel).

### Full algorithmic path
1. FB: small-index net terms {W_i(P), i ≤ B}. 2. Relation generation: enumerate Somos-identity collisions among FB terms and target-shifted terms W_i(Q)·W_j(Q) cross-terms. 3. Witness: index quadruple + net recomputation (exact). 4. Relation probability: collision rate vs birthday prediction (measured). 5. Matrix: exponent relations over Z/n. 6. Calibration: standard log calibration on net indices. 7. Descent: index descent in the net domain. 8. Offline: FB net table O(B); online: collision sieve. 9. Memory: O(B) net terms.

### Cost model
Net terms are deterministic algebraic functions of x(kP) (division polynomials), so a generic-model equivalence argument applies unless Somos collisions arrive sub-birthday. Total = FB table O(B) + collision search O(B²) or sorted O(B log B) + LA + descent. Win requires measured collision enrichment over the birthday model at equal budget — the exact measurable.

### Why the existing negative results do not already kill it
No ledger entry tests net-domain relation supply. The new mathematical operation is the two-parameter Somos identity family; all ledger recurrences were one-parameter (BM) or membership predicates.

### Likely fatal obstruction
Somos identities are universal (hold for every k): restricted to a k-fiber they may yield only tautologies — relations that encode the group law itself, not k. Then the net is a relabeling inside the generic model and Shoup's bound closes it. This is the strongest kill argument and B1's experiment is designed to detect it directly.

### Minimal falsifying experiment
p ∈ {101, 431, 1601}; seeds as above; compute nets of P and random Q = kP; enumerate Somos collisions among FB-index terms; test k-recovery vs BSGS at equal op budget. Positive control: net-based pairing recomputation matches Weil pairing (Stange). Negative control: nets of random non-related points must show no collision enrichment.

### Quantitative promotion gate
k-recovery charged exponent trend < 0.49 across sizes; secondary (necessary-not-sufficient): net-relation rank per field op ≥ 2x BSGS-equivalent.

### Proof track
Theorem characterizing the relation module of Somos identities restricted to k-fibers — if it is generated by universal identities, B1 is dead by theorem.

### Disproof track
Measured collision statistics equal to random-oracle birthday statistics across sizes → representation is generic, scoped negative.

### Reproduction artifact
Contract `research/EXP_NET1_contract.md`; implementation `experiments/ecdlp_net/net1_somos_sieve.sage`; result `experiments/ecdlp_net/net1_somos_sieve_result.json`; audit `experiments/ecdlp_net/net1_verify.sage`; ledger ID NET-H-001.

---

## Candidate: B2 — Tropical/Newton-polytope (BKK) decomposition of five-point membership

### One-sentence mechanism
Replace Bézout-degree solving of the m-summation system by support-aware sparse elimination (mixed volume / polyhedral homotopy over the Newton polytopes of the Semaev family), so that the complexity driver becomes the mixed volume MV rather than the dense Bézout bound, reducing solving cost C of point decomposition below dense-resultant growth (measured exponent 1.979, MX-1478), B = rho 1/2.

### Status
HYPOTHESIS.

### Novelty classification
LEDGER-NEW (every ledger resultant is dense); LITERATURE-ADJACENT (sparse elimination theory exists — BKK, Canny–Emiris, Huber–Sturmfels; no application to Semaev/ECDLP found after documented search).

### Semantic fingerprint
F(B2) = (Newton polytopes Δ_i of the target-sectioned summation system; polytope computation, regular subdivision, toric resultants; monomial-support sparsity of S_m; zero-coefficient monomials discarded — exactly what dense methods pay for; supports and structure constants retained; relation generation = sparse resultant / polyhedral homotopy membership solving; compression = support sets instead of dense coefficient tensors; rank = unchanged relation matrix; descent = standard; dominant exponent = MV-driven vs Bézout-driven).

### Nearest ledger entries
- ECFG-MX-1478 (dense composed resultants, exponent 1.979): distinction — sparse/mixed elimination replaces dense composition; the complexity invariant changes from degree to mixed volume. Not a wording distinction.
- ECFG-RT-1476 (m-ary exponent boundary): distinction — they bound membership exponents; B2 changes the solver's complexity driver; the two compose (RT-1476's α gates B2's total).
- ECFG-NR-1447 (additive expansion/permutation floors): distinction — polytope supports are exact combinatorial objects, not energy heuristics.
- P1480 (bitvector membership): distinction — support-aware algebraic solving vs bit-blasting.
- ECFG-H639/640 (summation hypotheses): parent family.

### Nearest literature
Bernstein–Kushnirenko–Khovanskii (BKK bound); Canny–Emiris sparse resultants (1993/2000); Huber–Sturmfels polyhedral homotopy (1995); Kousidis–Wiemers first-fall-degree (bibliography.json) as adjacent Semaev complexity analysis; Castryck–Denef–Vercauteren (Newton polytopes in curve arithmetic, adjacent). Gap: the Newton polytope of the Semaev family has apparently never been computed; its growth law is an open, decidable-at-small-m question.

### Target family
Ordinary prime-field, prime-order subgroup, m ∈ {4,5,6}, char ≥ 5, standard exclusions.

### Full algorithmic path
0. (Stage zero, one-time, offline): compute exact monomial supports and Newton polytopes of S_m(x_1..x_{m−1}; x_R) for m = 3..7; compute MV vs Bézout. 1. FB: standard. 2. Relation generation: polyhedral homotopy / sparse-resultant membership solving. 3. Witness: exact tuple verification by direct evaluation. 4. Relation probability: unchanged from classical Semaev (same solution set — this is a solver replacement; stated plainly). 5. Matrix: standard. 6. Calibration: standard. 7. Descent: standard. 8. Offline/online: stage 0 offline; solving online. 9. Memory: support-sized, not dense-tensor-sized.

### Cost model
Dense elimination ∼ D^{O(m)} with D ∼ 2^{m−2}-ish (consistent with the measured 1.979 fit). Sparse ∼ MV^{O(1)}·poly(#support). Win requires log MV / log Bézout < 1 strictly and persisting as m grows, AND the solver stage being a non-negligible share of the RT-1476 total — otherwise B2 is a banned "solver improvement alone"; the promotion gate therefore charges the full relation + LA + descent path.

### Why the existing negative results do not already kill it
MX-1478 measured dense composition. The new mathematical operation is support-aware elimination with a different complexity invariant. If the polytopes are saturated, D2 proves it and B2 dies in stage 0 at trivial cost — decisive in both directions.

### Likely fatal obstruction
Semaev polynomials may be Newton-saturated (full simplex support in each variable block): then MV = Bézout, sparse ≡ dense, and B2 is MX-1478 re-skinned. Symmetrization reduces degree but fills support.

### Minimal falsifying experiment
p ∈ {101, 431, 1009}; m ∈ {3,4,5}; compute exact supports, polytopes, MV (mixed-subdivision enumeration at these sizes); then solve real systems via sparse vs dense routes, counting F_p-ops. Positive control: solution sets identical to the ledger S3 harvester. Negative control: random same-support systems must show the same MV (if they solve equally fast, any win is generic sparse-system machinery, not EC structure — scope narrows accordingly).

### Quantitative promotion gate
MV/Bézout ratio ≤ 0.85 at m = 5 and measured solve-exponent ratio < 0.9 across sizes, trending down in m; plus the combined charged exponent (with RT-1476 supply) trending below 0.49.

### Proof track
Computation of the Semaev family Newton polytopes (itself a publishable theorem); theorem MV(S_m) ∼ c^m with c < 2.

### Disproof track
A Newton-saturation theorem for S_m ⇒ MV = Bézout ⇒ dead; or measured ratio ≥ 0.95 at m = 5.

### Reproduction artifact
Contract `research/EXP_BKK1_contract.md`; implementation `experiments/ecdlp_bkk/bkk1_newton_mv.sage`; result `experiments/ecdlp_bkk/bkk1_newton_mv_result.json`; audit `experiments/ecdlp_bkk/bkk1_verify.sage`; ledger ID BKK-H-001.

---

## Candidate: B3 — Equivariant index calculus on the Semaev fiber-product curve (isotypic rank mechanism)

### One-sentence mechanism
Decompose the relation space of the summation fiber-product curve into isotypic components under G = S_{m−1} ⋉ (Z/2)^{m−1} using exact group-algebra idempotents, harvest and solve per block, and test whether block-restricted rank arrival and orbit-compressed storage reduce the charged total below the symmetrized baseline, B = rho 1/2.

### Status
CONJECTURE.

### Novelty classification
LEDGER-NEW (ledger Prym/deck work uses single involutions; full S_{m−1} ⋉ 2^{m−1} idempotent splitting of the relation operator is absent); LITERATURE-ADJACENT (Gaudry AV index calculus; FHJRV torsion symmetrization uses the S_m action on *polynomials* — B3 decomposes the *relation operator/module*, a different object).

### Semantic fingerprint
F(B3) = (G-module structure of the relation space; character projectors / group averaging; orbit structure of solution tuples; non-trivial isotypes discarded (measurable per block); trivial/sign blocks retained; relation generation = block-restricted symmetrized predicates; compression = orbit representatives (factor |G|); rank = per-block rank arrival vs full-matrix rank; descent = blockwise LP descent; dominant exponent = constant-factor unless block-rank arrival differs asymptotically — the measured question).

### Nearest ledger entries
- ECFG-NR-1399–1402 (x-only S3 quotient certificates): distinction — quotient predicates; B3 keeps the full operator and splits it exactly by idempotents.
- PO74–PO78 (Prym/deck cluster): distinction — Prym = ±1 eigenspaces of one involution; B3 uses the full group algebra (new composability law: idempotent splitting of the operator).
- PO-transfer-006 (cofiber ranks 6/34/74): distinction — combinatorial hypergraph rank vs representation-theoretic block rank.
- PO92 (module rank 731/758): distinction — new module (isotypic decomposition), new invariant (block multiplicities).
- ECFG-NR-1475 (residual character buckets, δ ≈ 0.02): distinction — buckets were statistical filters with tiny measured gain; idempotent projection is exact, not a density heuristic — the measured obstruction does not transfer (see below).

### Nearest literature
Gaudry 2009 (bibliography.json); FHJRV EUROCRYPT 2014 (bibliography.json); Maschke/Wedderburn (standard). Gap: equivariant decomposition of the *relation matrix* (rather than the defining polynomials) appears unmeasured everywhere.

### Target family
Ordinary prime-field, prime-order subgroup, m ∈ {4,5}, p ∤ |G| (true at our sizes), standard exclusions.

### Full algorithmic path
1. FB: G-orbit representatives of x-sets. 2. Relation generation: symmetrized predicates with block tags. 3. Witness: orbit + block id + exact verification. 4. Relation probability: block-conditional hit rates (measured per isotype). 5. Matrix: block-diagonal by construction; dimensions /|G|-ish per block. 6. Calibration: per-block. 7. Descent: blockwise LP descent. 8. Offline: idempotent precomputation (cheap, exact). 9. Memory: orbit storage, 1/|G| factor.

### Cost model
Total = (B/p_m)·C_eval (unchanged) + Σ_blocks LA(B_b) + descent. LA is superlinear in dimension, so Σ LA(B/|G|) < LA(B); storage drops by |G|. Risk: block-rank imbalance (empty blocks waste; trivial block may carry all relations, in which case B3 ≡ FHJRV symmetrization with bookkeeping — stated as the red-team line).

### Why the existing negative results do not already kill it
NR-1475's measured δ ≈ 0.02 applies to statistical character *buckets*; B3's new operation is exact idempotent projection of the operator — a decomposition, not a filter. The obstruction (density gain too small) does not apply to exact splittings; what remains to measure is block-rank arrival, which no ledger entry records.

### Likely fatal obstruction
Solution tuples come in G-orbits, so the trivial isotype provably carries a large fraction of relations — that fraction is *already* what symmetrization exploits. If block multiplicities are |G|-symmetric, B3 reduces to FHJRV with extra accounting (disguised-repetition kill).

### Minimal falsifying experiment
p ∈ {211, 1009, 4099}; m = 4; build the G-action, idempotents, block matrices; measure per-block relation counts, ranks, and blind-descent success. Positive control: total relations equal the symmetrized baseline exactly. Negative control: random G-actions on random hypergraphs must show the same block distribution (if they do, block structure is not EC-specific and any asymptotic hope dies).

### Quantitative promotion gate
Fully charged exponent trend < 0.49; or ≥ 4x LA+storage reduction at equal recovered targets sustained across three sizes (necessary-not-sufficient).

### Proof track
Theorem computing isotypic multiplicities of the permutation module on relation tuples; corollary: non-trivial blocks carry an asymptotically vanishing or non-vanishing share.

### Disproof track
Measured multiplicities exactly |G|-symmetric with all harvested relations in trivial+sign blocks → equivalence to symmetrization, scoped negative.

### Reproduction artifact
Contract `research/EXP_EQJ1_contract.md`; implementation `experiments/ecdlp_equivariant/eqj1_isotypic.sage`; result `experiments/ecdlp_equivariant/eqj1_isotypic_result.json`; audit `experiments/ecdlp_equivariant/eqj1_verify.sage`; ledger ID EQJ-H-001.

---

## 5. Candidate set C — high-risk speculative mechanisms

## Candidate: C1 — Transfer-operator (Ruelle/Koopman) spectral channel on the translation walk

### One-sentence mechanism
Coarse-grain the translation-by-P map on E(F_p) into a finite Markov operator, estimate its leading spectrum from sub-birthday trajectory samples, and test whether spectral phase information localizes k into an interval shrinkable below √n total cost, B = rho 1/2.

### Status
CONJECTURE (expected to become a barrier measurement; stated honestly).

### Novelty classification
POSSIBLY NOVEL as an ECDLP mechanism (no transfer-operator use for DLOG found after documented search); LITERATURE-ADJACENT on the dynamics side (Ruelle; Mayer–Mühlenbruch–Strömberg 2012 confirmed in search; Teske's rho random-walk analyses, recollection).

### Semantic fingerprint
F(C1) = (transfer/Koopman operator of group translation; Markov partitions, spectral estimation; spectral gap and resonances of the walk; fine orbit information discarded; leading eigenpairs retained; relation generation = spectral estimation (no factor base — direct-solver candidate); compression = coarse-graining to C cells; rank = N/A; descent = interval localization + BSGS finish; dominant exponent = unknown, likely 1/2 by character orthogonality).

### Nearest ledger entries
- ECFG-010–013 graph-shape selectors: distinction — local walk statistics vs a global spectral object (leading eigenpairs of the coarse operator).
- ECFG-N001 (direct graph inversion, 7/320): distinction — orbit-following vs operator inversion.
- Frontier E5/E7/E8 (ECFG reverse index): distinction — C1 never materializes a full index; only the leading spectrum at C ≪ n cells.
- TRANSFER-NR-018 (PO45 functional transfer): distinction — different operator and different observable.
- SHA1 basin coarse-graining rows: adjacent spirit, different problem (off-ECDLP sibling program).

### Nearest literature
Ruelle transfer operators (confirmed); Mayer–Mühlenbruch–Strömberg, Discrete Contin. Dyn. Syst. 32 (2012) (confirmed); Teske, random walks for Pollard rho (recollection); Koopman spectral methods in data science (recollection). Gap: nobody has tried spectral estimation of *group translations* as a DLOG channel — likely because of the orthogonality argument below, but that argument has never been written as a theorem with toy measurements.

### Target family
Ordinary prime-field, prime-order subgroup; standard exclusions.

### Full algorithmic path
No factor base (direct solver; FB/LA stages are N/A by design, not missing). 1. Partition E(F_p) into C cells by x-intervals. 2. Build the empirical C×C transition matrix of the +P walk from sampled trajectories of total length S. 3. Compute leading eigenpairs; map eigenvalue phases to a k-interval via character identification. 4. Witness: interval membership certificate by point multiplication (exact). 5. Localization probability measured. 6–7. Descent: BSGS inside the localized interval. 8. Offline: none beyond sampling; online: everything. 9. Memory: C² matrix.

### Cost model
Cost ≈ S·C² (sampling + spectral) + √(n/L) (finish), L = localization factor. Win requires L super-constant at S = o(√n). Character orthogonality predicts L = O(1): translation eigenfunctions are characters, and coarse-graining mixes exactly the phase information that encodes k. The experiment measures L(S, C) directly; any L growing like n^δ with δ > 0 at S ≤ n^{0.3} would be a genuine surprise and a promotion signal.

### Why the existing negative results do not already kill it
No ledger entry touches operator spectra. The new mathematical operation is Markov coarse-grained spectral inversion — not orbit following, not shape selection, not an index.

### Likely fatal obstruction
The coarse-grained translation operator is asymptotically character-diagonal: its eigenvalues at full resolution are exactly χ(P) (which *are* the logarithm data — circular at C ≈ n), and at C ≪ n coarse-graining kills the phase. Expect the clean barrier outcome L = O(1); the candidate's real deliverable is then the barrier theorem plus measurements (D-flavored value).

### Minimal falsifying experiment
p ∈ {211, 1009, 4099}; C ∈ {8, 32, 128}; S ∈ {n^{1/4}, n^{3/8}}; seeds as above. Measure L vs charged cost. Positive control: at C = n (full resolution) the spectrum does recover k — sanity that the channel exists in principle. Negative control: random permutation operators must not localize (guards against estimator artifacts).

### Quantitative promotion gate
L ≥ n^{0.05} at S ≤ n^{0.3} sustained across three sizes (far below break-even, but a directional signal); otherwise archive as a barrier measurement with the fitted L(S, C) law.

### Proof track
Theorem: coarse-grained character mixing bound L = O(1) for translation operators on cyclic groups — or a counterexample family.

### Disproof track
Character orthogonality essentially *is* the disproof; deliver it as a proved barrier if measurements agree.

### Reproduction artifact
Contract `research/EXP_TRA1_contract.md`; implementation `experiments/ecdlp_transfer_op/tra1_koopman.sage`; result `experiments/ecdlp_transfer_op/tra1_koopman_result.json`; audit `experiments/ecdlp_transfer_op/tra1_verify.sage`; ledger ID TRA-H-001.

---

## Candidate: C2 — Tensor-network (tree) contraction of the recursive Semaev tensor with rank truncation

### One-sentence mechanism
Read the recursive definition S_m = Res_y(S_k(…, y), S_{m−k+2}(y, …)) as a tree tensor network whose bonds are the eliminated variables, and contract it with rank-χ-truncated factorizations — never materializing dense composed resultants (measured exponent 1.979, MX-1478) — so relation counting/enumeration costs poly(χ)·tree-size, B = rho 1/2.

### Status
CONJECTURE.

### Novelty classification
LEDGER-NEW; NOVELTY-UNVERIFIED (tensor-network #CSP counting exists — Kourtis et al., SciPost Phys. 7, 060 (2019), recollection; no Gröbner/summation-polynomial tensor-network application found after documented search).

### Semantic fingerprint
F(C2) = (Semaev recursion as a tree tensor network over F_p; tensor contraction and exact rank-revealing factorization; unknown-but-measurable low-rank structure of intermediate bonds; sub-χ singular directions discarded (recall loss only); χ-dimensional bond spaces retained; relation generation = contraction-based counting + conditional-contraction enumeration; compression = TTN factorization (the S_m polynomial is never materialized); rank = bond ranks as the new complexity invariant; descent = standard on enumerated solutions; dominant exponent = poly(χ) vs the 1.979 dense fit — win iff χ grows sub-exponentially).

### Nearest ledger entries
- ECFG-MX-1478 (dense composed resultants): distinction — C2 never composes densely; the invariant is bond rank, not degree. Exact (untruncated) contraction admittedly ≡ dense resultant — the candidate lives or dies on measured truncated recall, stated plainly.
- ECFG-NR-1477 (serial-S3 states): distinction — their state is a polynomial; C2's state is a low-rank tensor factor.
- Frontier A37 (transposed factor-membership matrix without B⁴ materialization): C2 is a candidate answer with a named contraction law; the ledger question names no primitive.
- P1480 (bitvector backend): distinction — exact algebraic contraction vs SMT encoding.
- ECFG-NR-1419 (symmetric-square materialized products): distinction — structured contraction ≠ materialized product.

### Nearest literature
Kourtis–Chamon–Ruckenstein–Mucciolo, SciPost Phys. 7, 060 (2019) (recollection): tensor-network counting for #CSP; Markov–Shi treewidth contraction (recollection). Over finite fields: contraction is field-agnostic algebra, but SVD-style truncation needs a norm absent over F_p — honest sub-question; C2 therefore uses exact rank-revealing truncation over F_p (border-rank viewpoint) with empirical recall measurement. Gap: nobody has measured bond ranks of resultant recursion tensors, generic or Semaev.

### Target family
Ordinary prime-field, prime-order subgroup, m ∈ {4,5,6}, char ≥ 5, standard exclusions.

### Full algorithmic path
1. FB: standard. 2. Relation generation: build the TTN from the recursion tree; contract to *count* solutions at target sections; enumerate solutions by conditional contraction (slice-and-dice over variables). 3. Witness: every emitted tuple is verified exactly by direct Semaev evaluation — truncation can only lose recall, never precision (by construction). 4. Relation probability: measured recall vs exact counts from the ledger harvester. 5. Matrix: standard, filled from enumerated solutions. 6. Calibration: standard. 7. Descent: standard. 8. Offline: network construction (one-time, symbolic). 9. Memory: O(tree·χ²·d) instead of dense polynomial states.

### Cost model
Exact contraction = dense resultant cost (the measured 1.979 obstruction). Rank-χ contraction ≈ O(tree·χ³·d²). Fully charged total = contraction + enumeration + LA + descent. Win requires the χ needed for recall ≥ 0.99 to grow polynomially where dense degree grows exponentially — measurable directly as χ(m, log q) growth exponent vs 1.979.

### Why the existing negative results do not already kill it
MX-1478 measured *dense composition*; C2's new mathematical operation is rank-truncated contraction with exact output verification. The closed obstruction (dense resultant blow-up) is precisely the object bypassed — not renamed, since the cost driver changes from degree to measured bond rank.

### Likely fatal obstruction
Bond ranks are generically full: resultant tensors likely have maximal border rank, χ explodes like d^{Θ(m)}, and C2 becomes dense resultant with overhead. If so, the experiment converts MX-1478's degree statement into a measured rank-growth law — a genuine negative-theory contribution, archived as scoped negative.

### Minimal falsifying experiment
p ∈ {101, 431, 1009}; m ∈ {3,4,5}; implement the TTN with exact F_p arithmetic and rank-revealing factorizations; measure bond ranks vs size and recall at capped χ; compare against MX-1478 dense timings. Positive control: exact contraction (χ unbounded) reproduces exact solution counts matching the ledger S3 harvester. Negative control: random tensors of identical shape (expected full rank — if Semaev tensors are also full rank, that is the scoped negative).

### Quantitative promotion gate
Measured bond-rank growth exponent < 1 (polynomial χ at recall ≥ 0.99) across three sizes, beating the 1.979 dense exponent with margin; correctness alone is not the gate.

### Proof track
Theorem bounding the border rank of the Semaev recursion tensor; or a genericity theorem showing full rank (which kills it — equally valuable).

### Disproof track
Exhibit one full-rank bond slice family; or measured χ(m) fit with exponent ≥ 1.9.

### Reproduction artifact
Contract `research/EXP_TTN1_contract.md`; implementation `experiments/ecdlp_ttn/ttn1_semaev_contraction.sage`; result `experiments/ecdlp_ttn/ttn1_semaev_contraction_result.json`; audit `experiments/ecdlp_ttn/ttn1_verify.sage`; ledger ID TTN-H-001.

---

## Candidate: C3 — Noncommutative path-algebra syzygy search on the correspondence quiver

### One-sentence mechanism
Model translations, negation, and small correspondences as arrows of a quiver, let its (noncommutative) path algebra act on formal point-sums, and search with noncommutative Gröbner/syzygy methods (Bergman overlaps) for word-level relations between the target word and factor-base words that commutative summation relations miss, B = rho 1/2.

### Status
CONJECTURE (high circularity risk; included because the seed list mandates investigating it and the falsification is cheap and sharp).

### Novelty classification
POSSIBLY NOVEL as an ECDLP mechanism (path-algebra Gröbner theory confirmed — Waweru–Maingi, arXiv:2306.06457; Farkas–Feustel–Green; no cryptographic application found); LITERATURE-ADJACENT: Charles–Goren–Lauter isogeny-graph path finding (recollection).

### Semantic fingerprint
F(C3) = (path algebra KQ of the correspondence quiver; noncommutative arithmetic, overlap/syzygy computation; word-order (noncommuting) structure among translations and correspondences; the commutative quotient discarded; word-level relations retained; relation generation = NC-GB overlap reductions; compression = quiver presentation; rank = syzygy module rank; descent = word evaluation yields the scalar directly; dominant exponent = unknown, likely ≥ birthday via the commutative-shadow argument).

### Nearest ledger entries
- ISO-AR volcano orientation rows: distinction — they reconstruct specific maps; C3 searches a free-associative syzygy space (different algebraic object).
- PO-transfer-002 (target-coupled MITM): distinction — divisor-list meet-in-the-middle vs word relations.
- ECFG motif-generation rows: distinction — motifs are commutative support sets; words retain order (this is also the red-team kill line: see below).
- PO63 anchor matrices: distinction — linear algebra over Z/n vs free-associative algebra.
- PO-004 (scalar Weil): distinction — no restriction of scalars.

### Nearest literature
Bergman, diamond lemma (Adv. Math. 1978, recollection); Waweru–Maingi 2023 (confirmed); Farkas–Feustel–Green (confirmed via thesis source); Charles–Goren–Lauter 2009 (recollection). Gap: NC-GB has never been pointed at ECDLP; the commutator-collapse theorem below may explain why.

### Target family
Ordinary prime-field, prime-order subgroup. Honesty note: over F_p, Frobenius acts trivially on points, so noncommutativity must come from word order of translations/negations and any isogeny arrows — isogeny arrows lead toward closed same-field territory and are excluded from the base experiment.

### Full algorithmic path
1. FB: translation arrows {T_{P_i}} plus negation. 2. Relation generation: truncated NC-GB to degree ≤ 6; collect reductions whose evaluation collapses to scalar multiples. 3. Witness: word + evaluation transcript (exactly verifiable). 4. Relation probability: syzygy-hit rate (measured). 5. Matrix: overlap incidence (if needed). 6. Calibration: N/A (word evaluation gives k directly). 7. Descent: word evaluation. 8. Offline: quiver setup; online: NC-GB search. 9. Memory: GB growth (the risk).

### Cost model
If the evaluation map factors through the commutative group algebra Z[E(F_p)] — expected — then every NC relation descends to a subset-sum relation, and cost per relation ≥ birthday cost. Win requires a word-order constraint with no commutative shadow; existence of such constraints is the measurable question.

### Why the existing negative results do not already kill it
No ledger entry uses free-associative structures; the overlap/syzygy calculus is a genuinely absent primitive. The candidate survives the fingerprint test narrowly: its distinction from motif generation (word order) is real even if likely vacuous.

### Likely fatal obstruction
The commutator-collapse theorem: if the evaluation kernel is generated by commutators, NC relations ≡ commutative relations and C3 is motif generation with noncommutative bookkeeping (disguised repetition). Over F_p there is no Frobenius arrow to break commutativity.

### Minimal falsifying experiment
p ∈ {101, 431}; quiver = {T_{P_i}, i ≤ B} ∪ {neg}; truncated NC-GB to degree 6; count Q-reaching relations vs a commutative subset-sum baseline at equal op budget. Positive control: word-evaluation engine verified on known k. Negative control: the commutative quotient must reproduce all found relations — if it does, C3 is bookkeeping (scoped negative).

### Quantitative promotion gate
A relation class with NC-GB cost per relation < commutative harvest cost at equal size, with charged exponent trend < 0.49; expected to fail — archival as scoped negative is the likely outcome and is acceptable.

### Proof track
Theorem: the evaluation kernel KQ → Z/n is generated by commutators (kills C3); or exhibit a noncommuting invariant with kernel strictly smaller (promotes C3).

### Disproof track
The commutator-generation theorem (likely provable; would close the whole noncommutative-correspondence direction for prime fields).

### Reproduction artifact
Contract `research/EXP_NCP1_contract.md`; implementation `experiments/ecdlp_ncpath/ncp1_quiver_gb.sage`; result `experiments/ecdlp_ncpath/ncp1_quiver_gb_result.json`; audit `experiments/ecdlp_ncpath/ncp1_verify.sage`; ledger ID NCP-H-001.

---

## 6. Candidate set D — negative-theory candidates (barrier / loophole theorems)

These three are theory-track candidates: their deliverable is a theorem or decisive certificate plus toy computational certification, not an attack. The "route to descent" rejection rule is applied to algorithmic candidates only; for D candidates the analog is a *decisive scope statement* (what exactly is closed, or what exact loophole is exposed).

## Candidate: D1 — Generic-model barrier for jet-augmented relation channels

### One-sentence mechanism
Define an augmented generic-group model whose queries include first-order jet (dual-number) data of the addition law, and attempt a Shoup-style simulation theorem: if jet algorithms are simulable generically with O(1) overhead, then all dual-number candidates (A1) are closed at exponent 1/2; if simulation fails, the exact non-simulable operation is the loophole A1 must exploit.

### Status
OPEN.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (Shoup EUROCRYPT 1997; Maurer abstract models — no jet-augmented generic model found).

### Semantic fingerprint
(model-theoretic; object = augmented generic group with tangent oracle; operations = group op + ε-linear solves; structure = formal-group linearity; discarded = higher jets; retained = order ≤ 1; relation generation = model query; compression = simulation overhead bound; rank/descent = N/A; dominant exponent = 1/2 if barrier holds).

### Nearest ledger entries
ECDLP negative controls (ECFG-NR-238 family) — distinction: empirical vs model-level; ECFG-NR-1447 (additive-expansion diagnosis) — distinction: empirical expansion diagnosis vs a simulation theorem; frontier A38 (structured-generic model request) — D1 is a direct answer attempt; Shoup baseline rows; A1 (sibling candidate).

### Nearest literature
Shoup 1997; Maurer 2005 (recollection); Jager–Schwenk generic-model refinements (recollection). Gap: no augmented model with nilpotent structure constants has been analyzed.

### Target family
Model-level; validated on ordinary prime-field toy curves.

### Full algorithmic path
Theory program: (1) formalize the model; (2) prove simulability or exhibit the non-simulable query; (3) toy-check: A1's measured σ must match the model's prediction. Stages 1–9 of the attack template are N/A by design.

### Cost model
N/A (theory). If the barrier holds: exponent 1/2 certified for the whole jet family — a high-value closure.

### Why existing negatives do not kill it
It is a barrier candidate; barriers are not killed by empirical negatives, only by counterexamples.

### Likely fatal obstruction
The model may be unformalizable without leaking the encoding (tangent data may be inherently encoding-dependent), making the question ill-posed — itself a reportable outcome.

### Minimal falsifying experiment
Toy certification on p ∈ {101, 211, 431}: compare A1-measured σ against the model's predicted σ under simulability; mismatch = candidate loophole, match = barrier evidence.

### Quantitative promotion gate
Proved simulation theorem, or an explicit non-simulable operation validated at all three toy sizes.

### Proof track
The simulation theorem itself (or the counterexample construction).

### Disproof track
A1 experiment violating model predictions with exact verification.

### Reproduction artifact
Note `research/THM_JETBARRIER1.md`; check script `experiments/ecdlp_jet/jetbarrier1_model_check.sage`; result `jetbarrier1_model_check.json`; audit `jetbarrier1_verify.sage`; ledger ID JETB-TH-001.

---

## Candidate: D2 — Mixed-volume growth-law certificate for the Semaev family

### One-sentence mechanism
Compute exactly (and certify computationally) the Newton polytopes and mixed volumes of the Semaev summation family for m = 3..7, fit the growth law, and deliver either a barrier theorem (MV = Bézout order → B2-class methods dead) or a quantified opening (MV/Bézout → c < 1 with a rate → B2 promoted with exact targets).

### Status
OPEN.

### Novelty classification
LEDGER-NEW; LITERATURE-ADJACENT (BKK theory; Kousidis–Wiemers first-fall-degree as adjacent Semaev complexity analysis).

### Semantic fingerprint
(complexity-geometry certificate; object = Newton polytope sequence of S_m; operations = support enumeration + mixed-subdivision volume; structure = monomial support sparsity; discarded = coefficients; retained = supports; relation generation = N/A; compression = support sets; rank = N/A; descent = N/A; dominant exponent = the MV growth rate itself).

### Nearest ledger entries
ECFG-MX-1478 (dense resultant exponent) — distinction: D2 measures the *sparse* invariant the ledger never computed; ECFG-RT-1476 — distinction: membership exponent vs solving-complexity driver; ECFG-H639/640 — parent family; frontier A43 (non-Gröbner batched sieve request) — D2 supplies its complexity ground truth; B2 (sibling candidate).

### Nearest literature
BKK; Canny–Emiris; Sturmfels (recollection); Kousidis–Wiemers (bibliography.json). Gap: the Semaev polytope sequence is uncomputed in the literature as far as the documented search reached.

### Target family
Model-level; ordinary prime-field toy curves for certification.

### Full algorithmic path
Theory program with exact computation at m ≤ 7 (tractable): supports → polytopes → mixed volumes → growth-law fit → theorem attempt (saturation or sparsity).

### Cost model
Computation is exponential in m but tiny at m ≤ 7; deliverable is the asymptotic law, not the instances.

### Why existing negatives do not kill it
Nothing in the ledger measures polytope volumes; MX-1478's 1.979 is a *dense* measurement and logically compatible with either MV outcome.

### Likely fatal obstruction
Support enumeration at m = 7 may exceed budget (mitigation: exploit S_m's recursive structure to compute polytopes fiberwise — itself part of the theorem track).

### Minimal falsifying experiment
Exact MV computation at m ∈ {3,4,5} on three seeds/curves; cross-check MV against actual solution counts over F_p (BKK says MV bounds the count — any violation is a computation bug; agreement certifies the pipeline).

### Quantitative promotion gate
A proved or 3-point-certified growth law with an exponent statement; ambiguous fits (CI spanning the Bézout rate) do not count.

### Proof track
Newton-saturation theorem (barrier) or sparsity theorem with c < 2 (opening).

### Disproof track
The opposite theorem.

### Reproduction artifact
Note `research/THM_BKKMV1.md`; certificate `experiments/ecdlp_bkk/bkkmv1_cert.sage`; result `bkkmv1_cert.json`; audit `bkkmv1_verify.sage`; ledger ID BKKMV-TH-001.

---

## Candidate: D3 — Incidence-richness ceiling for EC chord arrangements

### One-sentence mechanism
Prove or computationally certify whether factor-base chord arrangements on E(F_p) attain the generic Szemerédi–Trotter-type richness ceiling: if yes, relation supply for A2-class harvesting is capped and that direction closes at exponent ≥ 1/2; if EC chords show a curve-specific *excess* of rich lines, that excess is a quantified opening and A2 is promoted with exact targets.

### Status
OPEN.

### Novelty classification
LEDGER-NEW as a formal barrier target; LITERATURE-ADJACENT (Stevens–de Zeeuw; Vinh; Ahmadi–Shparlinski EC sum-product estimates per ledger A39).

### Semantic fingerprint
(incidence-combinatorics barrier; object = richness distribution of the chord-line arrangement; operations = exact enumeration + character-sum estimation; structure = algebraic non-genericity of chord lines; discarded = lines below richness s; retained = the s-profile; relation generation = N/A; compression = N/A; rank = N/A; descent = N/A; dominant exponent = the richness exponent itself).

### Nearest ledger entries
Frontier A39 (pair-output exponent question) — D3 supplies its ground truth; ECFG-RT-1472 (2LP floor) — distinction: D3 explains *why* the floor is where it is; ECFG-NR-1471 — same; ECFG-NR-1404/1405/1407 (predicate FBs) — distinction: D3 is FB-agnostic (arrangement-level); A2 (sibling candidate).

### Nearest literature
Stevens–de Zeeuw 2017 (confirmed); Rudnev 2018; Iosevich et al. 2023 (confirmed); Vinh 2011; Bourgain–Katz–Tao 2004; Ahmadi–Shparlinski (per ledger A39; venue unverified). Gap: richness *profiles* of EC chord arrangements, as opposed to worst-case bounds, appear unmeasured.

### Target family
Model-level; ordinary prime-field toy curves, B grid as in A2.

### Full algorithmic path
Exact toy enumeration of the richness distribution → comparison against random line sets and against Vinh/SdZ predictions → character-sum theorem attempt.

### Cost model
Enumeration at toy sizes is cheap; the theorem is the deliverable.

### Why existing negatives do not kill it
It converts folklore ("chords are generic") into a measured/proved statement; no ledger entry measures richness profiles.

### Likely fatal obstruction
Character-sum error terms may swamp the signal at provable scales, leaving only toy evidence (model-bound, stated as such).

### Minimal falsifying experiment
p ∈ {211, 1009, 4099}; B grid; enumerate the full richness profile; controls: random line sets (negative) and deliberately grid-structured sets (positive control for the measurement's sensitivity).

### Quantitative promotion gate
A fitted richness exponent separated from the random-line control by > 3 standard errors at all three sizes, or a proved bound.

### Proof track
EC-chord richness ceiling theorem (barrier) or excess theorem (opening).

### Disproof track
The opposite result.

### Reproduction artifact
Note `research/THM_INCBARRIER1.md`; script `experiments/ecdlp_incidence/incbarrier1_richness.sage`; result `incbarrier1_richness.json`; audit `incbarrier1_verify.sage`; ledger ID INCB-TH-001.
