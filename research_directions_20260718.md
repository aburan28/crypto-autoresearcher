# Research Directions 2026-07-18 — Round 2

**Lab:** crypto-autoresearcher (empirical cryptanalysis, ECDLP over ordinary prime fields)
**Role:** Research Director
**Date anchor:** 2026-07-18 (local machine date, verified via `date` at session start)
**Status of this document:** speculation and hypothesis generation. Nothing here is a performance claim. Every candidate is a falsifiable probe; no candidate is asserted to beat Pollard rho.

---

## 1. Required input review

### 1.1 Files reviewed (staged copies in `inputs/`)

| File | Lines | Coverage |
|---|---|---|
| `inputs/research_ledger_main.md` (copy of `/Volumes/Volume/git/autolab/research_ledger.md`) | 2445 | full file, head and tail read directly; middle covered by machine parse |
| `inputs/research_ledger_ic.md` (copy of `/Volumes/Volume/git/autolab/ecdlp_index_calculus_state/research_ledger.md`) | 720 | full |
| `inputs/non_generic_transfer_search_20260610.md` | 389 | full (read end-to-end) |
| `inputs/bibliography.json` | 10 sources | full (read end-to-end) |
| Workspace prior-round records (`H-*.yaml`, `research_directions_20260717.md`, EXP-JET/BKK/TTN/NCP closures) | — | treated as ledger-adjacent input; all 12 candidates below were checked disjoint from them |

### 1.2 Machine-readable inventory

Tool: `tools/build_inventory_20260718.py`. Output: `inputs/ledger_inventory_20260718.json`, `inputs/ledger_added_20260718.json`.

- **2889 parsed rows, 2835 unique ledger IDs** across both ledgers.
- **256 IDs are new** relative to the 2026-07-17 snapshot (2707 entries) used for round 1.
- Section counts — main ledger: Active hypotheses 462, Negative results 640, Positive signals 1128, Open frontier questions 98, plus continuation/division-character/graph-index/control rows 14. IC ledger: Active 62, Baselines 87, Negative 98, OFQ 8, Positive 290. **761 explicit NEGATIVE RESULT rows** in total.
- **ID families covered:** ECFG (incl. ECFG-NR / ECFG-RT / ECFG-P / ECFG-MX), ISO, ISO-AR, TRANSFER-H / TRANSFER-NR / TRANSFER-P, OFQ-autolab, SHA1 (main ledger); ECFG, NR, OFQ-ic (IC ledger); PO-transfer-001..007 (transfer-search document).
- Extracted per entry (schema in the JSON): mechanism, representation, exploited structure, factor base, relation shape, relation-generation method, compression method, linear-algebra object, target-descent method, cost bottleneck, outcome, scoped negative boundary, next proposed branch. Fields absent in the source row are `null` (not fabricated).

### 1.3 Newest-ledger review highlights (the 256 new entries)

Read directly (tail sections) rather than sampled:

- P1473–P1513 closures: sparse subgroup-x decks, materialized serial-S3 backward states (closed), BKK/homotopy (NR-1492), output-sensitive resultant relation finding (NR-1493), Lattès/dynamical deck (NR-1495), tensor-train contraction of the Semaev tensor (NR-1488), IDEA-049..068 resolutions, Hasse-jet sections (P1509/P1510), linear-Chow atomizer (P1512).
- PO96A–PO96W transfer saga: hidden scalar square/power-map channels all closed (TRANSFER-NR-068..077); TRANSFER-H009..H035 open; ISO-AR orientation-division volcano work active.
- Round-1 workspace closures now on record: EXP-JET, EXP-BKK, EXP-TTN, EXP-NCP are scoped negatives. **Round-1 candidate mechanisms are excluded from round 2.**

### 1.4 Vocabulary collision check (both ledgers, grep)

`monodromy` 1 hit (unrelated context); `Chebotarev` 0; `Galois group` 0; `syndrome` 0; `Goppa` 0; `Edwards` 0; `elliptic surface` 0; `Mordell-Weil` 0; `Shtuka` 0; `Heegner` 0; `Buium` 0; `Manin kernel` 0; `quasirandom` 0; `sum-product` 0; `xedni` 0; `wreath` 0; `additive energy` 3 (P1447-family coordinate diagnostics — distinct sense from log-space energy used in D1); `Fourier` 10 (multiplicative Kummer channels — distinct); `resolvent` 12 (Tschirnhausen-cover context); `preprocess` 45 (incl. **OFQ-autolab-81**, open: fixed-curve preprocessing compiler vs the generic S·T² frontier).

## 2. External literature search (primary sources, documented)

Searches run 2026-07-18 via web search; claims below cite the located primary sources. Absence claims are documented-search absence, not proof of non-existence.

1. **Generic bounds:** Pollard (1978); Shoup generic-group lower bound Ω(√n) (EUROCRYPT 1997). Lab baseline: rho expected cost ≈ 0.886·√n group operations (van Oorschot–Wiener parallelization assumed for comparison).
2. **Summation polynomials:** Semaev, "Summation polynomials and the discrete logarithm problem on elliptic curves" (ePrint 2004/031); Faugère–Huot–Joux–Renault–Vitse symmetrized/variant analyses; Huot thesis (Edwards and Jacobi-intersection summation polynomials exist — **Edwards-variant candidate dropped as literature-covered**); Wroński 2024 quantum-annealing on twisted Edwards prime-field instances.
3. **Coding-theory direction:** AG-code/ECP cryptanalysis literature exists (Minder thesis; Faure–Minder; Márquez-Corbella–Pellikaan) — it attacks curve-based *codes*, not ECDLP. **No "ECDLP-as-syndrome-decoding / relation-enumeration via dual-code weight enumerators" work found** (documented search; novelty remains UNVERIFIED).
4. **Xedni:** Silverman, "The xedni calculus and the elliptic curve discrete logarithm problem", Des. Codes Cryptogr. 20 (2000) 5–40; Jacobson–Koblitz–Silverman–Stein–Teske, "Analysis of the xedni calculus attack", DCC 20 (2000) 41–64 (shows the global-lift success probability collapses). No function-field-surface variant located.
5. **Non-uniform generic bounds:** Corrigan-Gibbs & Kogan, EUROCRYPT 2018 (ePrint 2017/1113): preprocessing DLP with advice S·T² = Ω̃(n); Coretti–Dodis–Guo, CRYPTO 2018 (AI-GGM).
6. **Arithmetic jets:** Buium, Invent. Math. 122 (1995) 309–340: an order-2 arithmetic δ-character exists iff good reduction and the curve is **not** a canonical/Serre–Tate lift. No ECDLP application located (UNVERIFIED).
7. **Small-root lattices:** Coppersmith bivariate small-root methods appear in isogeny norm-equation solving; **not** found applied to summation-polynomial relation finding.
8. **Pseudorandomness:** Liu–Gao, "Quasirandom subsets of Z_p from elliptic curves", Acta Math. Sinica (2009); Shkredov and Schoen–Shkredov energy/additive-combinatorics methods for elliptic sequences.
9. **Function-field arithmetic:** Mason–Stothers (Stothers 1981; Mason 1984); Evertse S-unit equation bounds; Beukers–Schlickewei bound 2^{8r+8}. Yun–Zhang, Annals 186 (2017) 767–911 & 189 (2019) 393–526 (higher Gross–Zagier over function fields); Howard–Shnidman (arXiv:1707.00213); Shnidman, Manin–Drinfeld over function fields (2024).
10. **Monodromy of summation covers:** **no work computing or exploiting the Galois/monodromy group of Semaev summation-polynomial covers located** (documented search; classification POSSIBLY NOVEL as a mechanism, not as mathematics — monodromy computations are standard algebraic geometry).
11. Round-1 areas (Hasse jets of the addition law, tropical/BKK decomposition, tensor-network contraction, transfer operators, path algebras, output-sensitive incidence reporting, equivariant sieves) — now closed in-ledger or covered by round-1 records; not re-proposed except where D-group barriers reference them.

## 3. Novelty standard and closed territory

The brief's novelty bar and closed-territory list are applied verbatim. Duplicate test: semantic fingerprint F(C) = (algebraic object, available public operations, hidden structure exploited, information discarded, information retained, relation-generation primitive, compression primitive, rank mechanism, descent mechanism, dominant cost exponent), compared against all 2835 inventoried entries plus round-1 workspace records. Six of twelve candidates begin outside the ledger's dominant vocabulary (B1, B2, C1, C2, C3, D3; A1/D1/D2 use Chebotarev/monodromy/pseudorandomness vocabulary that has 0–1 collisions).

**Novelty labels used:** LEDGER-NEW (absent from all reviewed records) combined with a literature label (LITERATURE-ADJACENT / NOVELTY-UNVERIFIED / POSSIBLY NOVEL with documented search). No candidate is called globally novel.

---

# 4. Candidates

---

## Candidate A1: Chebotarev census of the decomposition cover — relation-rate audit and exceptional-Galois sieve

### One-sentence mechanism
Exploit the Galois/monodromy structure S of the m-th Semaev summation cover to replace the *assumed* relation probability (uniform/quasirandom) with a measured Chebotarev density, reducing the cost C of index-calculus budget planning (subproblem P: relation-finding success prediction and exceptional-curve detection) below the uncalibrated baseline B.

### Status
HYPOTHESIS (measurement candidate; the attack content is conditional on finding exceptional curves)

### Novelty classification
LEDGER-NEW + POSSIBLY NOVEL (documented search §2.10 found no monodromy/Galois-group treatment of summation covers; monodromy computation itself is standard mathematics)

### Semantic fingerprint
- algebraic object: Galois closure of the m-th summation cover over the (x₁,…,x_{m-1})-parameter space
- available public operations: polynomial factorization over F_p, Frobenius cycle types, exact point enumeration at toy scale
- hidden structure exploited: possible non-full (imprimitive or exceptional) monodromy for special curve families
- information discarded: y-coordinates, group-law labels, all linear-algebra structure
- information retained: Frobenius cycle-type histograms of S_m(x₁,…,T) factorizations
- relation-generation primitive: none new — this is a census, not a generator
- compression primitive: Chebotarev density tables replacing per-instance rate measurements
- rank mechanism: none (not a linear-algebra proposal)
- descent mechanism: none of its own — calibrates and gates existing descent routes
- dominant cost exponent: measurement cost Õ(p) per curve at fixed m (same order as one rho run at toy scale; the *claim* is about removing wasted budget, not about a new attack exponent)

### Nearest ledger entries
1. **NR-1492** (BKK/homotopy relation finding, closed): also studies the summation *polynomial system*, but counts solutions via mixed volume; distinction: A1 never solves the system — it computes Frobenius cycle statistics of the cover's Galois closure, a different invariant (group-theoretic, not enumerative).
2. **NR-1486** (closed): resultant-style relation surface; distinction: A1 retains factorization *cycle types*, discards resultants entirely.
3. **RT-1476** (relation-trace audit): also audits relation rates; distinction: RT-1476 audits generated relations post-hoc; A1 predicts rates a priori from cycle-type census without generating any relation.
4. **NR-1473** (sparse subgroup-x decks, closed): shares the subgroup-x substrate; distinction: A1's object is the Galois group of a cover, not a deck of x-coordinates.
5. **NR-1447** (coordinate diagnostics / additive-energy family): shares statistical x-distribution auditing; distinction: energy of coordinate sets vs Frobenius cycle types of a defining polynomial — different statistic, different theorem (Weil vs Chebotarev).

### Nearest literature
Semaev 2004/031 (summation polynomials); Chebotarev density theorem (standard); monodromy computations for covers (standard algebraic geometry, e.g. Harris's Galois-group methods). Gap: no source applies monodromy of summation covers to ECDLP relation probabilities — claim is UNVERIFIED beyond the documented search.

### Target family
Ordinary prime-field curves E/F_p, prime-order subgroup (cofactor-1 toys), excluding: anomalous (#E=p), supersingular, j=0/1728 extra-automorphism cases (those are *targets of opportunity* for the exceptional sieve, analyzed separately, never silently mixed with random controls).

### Full algorithmic path
1. factor-base construction: none new — audit applies to whatever factor base the calibrated attack uses;
2. relation generation: none new;
3. witness extraction and verification: Frobenius cycle type from exact factorization of S_m over F_p (verifiable, deterministic);
4. relation probability: **the object of study** — measured split densities vs Chebotarev predictions for full S_{m-1}-monodromy vs quasirandom;
5. matrix dimensions, density, rank: not applicable (no matrix);
6. factor-log calibration: improved rate estimates feed existing calibration;
7. individual logarithm / target descent: INCOMPLETE as an attack — no descent route of its own (it gates/calibrates others);
8. offline/online separation: census is fully offline per curve family;
9. memory and parallelism: embarrassingly parallel over (x₁,…) samples and curves; memory O(m·log p) per sample.

### Cost model
Census: O(S · m · log²p) per curve for S samples; at toy scale S=3·10⁴, p≤10³ this is <1 s (measured: 0.285 s for 3 curves, §9.2). Scaling to m=3, p≈2²⁰: Õ(S·polylog p), far below one rho run O(√p) — measurement is cheap. Attack-relevant comparison: rho 0.886·√n, BSGS 2·√n memory-heavy; A1 changes no exponent — its value is (a) killing attack branches whose assumed relation rates are wrong by more than the Weil floor 2/√p, (b) flagging exceptional curves where rates deviate (potential constant or sub-exponential relation-finding gains *on those curves only*).

### Why the existing negative results do not already kill it
Every closed relation-finding branch (NR-1486, NR-1492, NR-1493, P1488) assumed or measured rates per-instance; none computed the cover's monodromy. New mathematical operation: Chebotarev census of Frobenius cycle types. The obstruction avoided: post-hoc rate fitting (post-hoc filters are closed territory) — A1 is a priori and theorem-backed.

### Likely fatal obstruction
Generic curves almost certainly have full symmetric monodromy (this is exactly D2's barrier prediction), so the census yields only the quasirandom rate and the exceptional sieve finds nothing; the candidate then reduces to a calibration tool with no attack value.

### Minimal falsifying experiment
Toy primes p ∈ {101, 211, 431, 809, 1601, 4099}, seeds 20260718+x, prime-order cofactor-1 controls; positive control: planted relation (x from the factor-base orbit window) must register with rate 1; negative controls: uniform-x and shuffled-window censuses must match exact predictions. Phase 1 (m=2, harness validation) executed — §9.2. Phase 2 (m=3 Semaev S₃ factorization census) is the substantive gate.

### Quantitative promotion gate
Phase-2 gate: at ≥3 toy sizes, measured m=3 split-rate deviation from the full-monodromy Chebotarev prediction must exceed 3× the Weil floor on a *non-excluded* curve family, OR an exceptional family with imprimitive monodromy must be found at rate ≥1/20 over random curves; otherwise the attack content is closed and only the calibration record is archived.

### Proof track
Theorem to establish: the geometric monodromy group of the m-th Semaev cover over F̄_p is the full symmetric (resp. wreath) group for all ordinary E outside an explicit exceptional locus — or conversely, exhibit an exceptional locus with strictly smaller monodromy and compute its Chebotarev densities.

### Disproof track
A full-monodromy proof (or census agreement within Weil error across ≥3 sizes and ≥2 m values) kills the attack content and promotes D2. A counterexample family (e.g., CM curves with monodromy forced into a proper subgroup) would narrow the claim to that family.

### Reproduction artifact
- contract: `experiments/EXP-MONO-001/contract.md`
- implementation: `experiments/EXP-MONO-001/mono_census.py`
- results: `experiments/EXP-MONO-001/smoke_results.json` (phase 1, executed)
- audit script: `experiments/EXP-MONO-001/audit_mono.py` (recomputes rates from the JSON + fixed seed)
- ledger ID: ECFG-RT-1514 (proposed)

---

## Candidate A2: Isogeny-class-amortized non-uniform preprocessing — one advice string per class

### One-sentence mechanism
Exploit Vélu-computable isogeny structure S to amortize a Corrigan-Gibbs–Kogan-style preprocessing advice string across an entire isogeny class, reducing the amortized complete cost C of the multiple-target DLP subproblem P below the per-curve advice baseline B = CK frontier S·T² = Ω̃(n).

### Status
HYPOTHESIS (weakened at first probe — see §9.1: no cross-curve advice transfer observed at toy scale)

### Novelty classification
LEDGER-NEW + NOVELTY-UNVERIFIED (CK/CDG give *generic* advice lower bounds; isogeny-class-amortized advice for ECDLP not located in the documented search)

### Semantic fingerprint
- algebraic object: ordinary isogeny class (volcano) over F_p + CK advice string
- available public operations: Vélu formulas, class enumeration at toy scale, oracle-free advice evaluation
- hidden structure exploited: shared ℓ-isogeny connective tissue between class members
- information discarded: per-curve optimizations
- information retained: one advice table serving all class members + transfer maps
- relation-generation primitive: generic walks seeded from advice
- compression primitive: advice amortization (one S for the whole class)
- rank mechanism: none
- descent mechanism: target reduction via isogeny transfer to the advice-friendly classmate, then CK walk
- dominant cost exponent: still Θ(√n) online; the claim is *amortization*: per-target cost → (S + T + Vélu-transfer)/k for k targets in the class, vs k independent CK instances

### Nearest ledger entries
1. **OFQ-autolab-81** (open: fixed-curve preprocessing compiler vs S·T² frontier): closest. Distinction: OFQ-81 is *fixed-curve* advice; A2's new operation is cross-curve advice transport through explicit Vélu maps — that transport step is exactly what failed at first probe (§9.1), so the distinction is now a measured obstruction, not a wording difference.
2. **ECFG-003 / ECFG-P002** (early fixed-curve preprocessing signals): same fixed-vs-class distinction as above.
3. **PO67/PO68** (same-field isogeny-invariant closures): those closed *invariants*; A2 does not use invariants — it transfers *advice*, and the closed invariant channels never carried log information anyway.
4. **PO69–PO71** (linear-algebra/descent-dominance closures): set the context that relation finding isn't always the bottleneck; A2's advice targets the walk phase, so these bound its value but don't close it.
5. **NR-1504** (closed): same-family scheduling variant; distinction: A2 has an honest hit generator (the CK walk), not a source selector.

### Nearest literature
Corrigan-Gibbs & Kogan EUROCRYPT 2018 (ePrint 2017/1113): preprocessing DLP advice with S·T² = Ω̃(n); Coretti–Dodis–Guo CRYPTO 2018 (AI-GGM lower bounds); Bernstein–Lange non-uniform DLP analyses. Gap: none of these considers isogeny-class structure; the lower bounds are per-group, so class amortization is not ruled out — but the transfer step must carry discrete-log-useful advice, which §9.1 fails to observe at toy scale.

### Target family
Ordinary prime-field curves in isogeny classes of size ≥2 over F_p, prime-order subgroup; excluded: anomalous, supersingular classes, classes with only j=0/1728 members.

### Full algorithmic path
1. factor-base construction: advice table built on one class member E₀;
2. relation generation: CK walk on E₀ for offline phase;
3. witness extraction and verification: discrete logs verified by scalar multiplication on the target curve after Vélu transfer (transfer of the *target*, not of logs — logs are isogeny-invariant under the pullback only up to known kernel corrections, which must be charged);
4. relation probability: generic walk rates;
5. matrix: none (advice-table walk);
6. factor-log calibration: standard;
7. individual logarithm: map target P ∈ E_i to E₀ via composed Vélu isogeny (cost Õ(ℓ) per step, charged), solve on E₀ with advice, pull back;
8. offline/online separation: one offline S per class, online T per target;
9. memory and parallelism: S advice cells shared; parallelism standard.

### Cost model
Per-target amortized: (S + k·T + k·C_velu)/k with S·T² = Ω̃(n) per CK, C_velu = Õ(ℓ_max·log²p) transfer. To beat k independent rho runs (0.886·k·√n), need T + C_velu < 0.886·√n with S spread over k — promising only if advice transfers. §9.1 toy probe (executed; classes of 6 prime-order curves at p ∈ {101, 211, 431}, 372 samples/curve): within-curve transfer matched the exact combinatorial prediction 2W/n (0.180 vs 0.147 at p=101; 0.075 vs 0.080 at p=211; 0.038 vs 0.036 at p=431); cross-curve transfer deltas vs baseline were mixed, −0.031 to +0.035 (≈ sampling noise at 372 samples), with no systematic positive transfer — **no amortization observed**. Honest status: weakened, not closed (toy scale, one advice policy).

### Why the existing negative results do not already kill it
Same-field isogeny-invariant closures (PO67/PO68) killed *invariant* channels; A2's operation is advice *transport*, which was never measured until §9.1. The new mathematical operation: Vélu-explicit advice transport with charged kernel corrections. (Note: the first probe now provides its own scoped negative; the candidate survives only as a refined question — which advice *representations*, if any, are transportable?)

### Likely fatal obstruction
Advice strings encode per-curve walk structure; isogenies scramble walk tables faster than they preserve logs (consistent with §9.1), making transport lossy at all scales.

### Minimal falsifying experiment
Toy primes p ∈ {101, 211, 431}, full isogeny classes enumerated (3–6 curves each), seeds 20260718+x; positive control: advice used on its own curve must hit ≥5× baseline; negative controls: relabeled-target (honest transfer) and random-table controls must not exceed baseline + Weil floor. Executed — §9.1.

### Quantitative promotion gate
Across ≥3 toy sizes and ≥3 advice policies, cross-curve transferred hit rate must exceed the relabeled negative control by >3σ in a majority of classmates, with transferred complete cost (walk + transfer) < 0.9 × per-curve CK. Currently: gate not met at phase 1.

### Proof track
Theorem: for ordinary classes, there exists an advice representation of size S with S·T² = õ(n) per class (not per curve) and an explicit transport map with o(√n) loss. Strongest plausible version: transportable advice = isogeny-covariant walk tables.

### Disproof track
A covariant-transport impossibility theorem (advice as a section of a non-flat bundle over the class) or repeated §9.1-style nulls across policies/sizes closes the candidate.

### Reproduction artifact
- contract: `experiments/EXP-ISADV-001/contract.md`
- implementation: `experiments/EXP-ISADV-001/advice_transfer.py` (smoke version executed, §9.1)
- results: `experiments/EXP-ISADV-001/smoke_results.json`
- audit script: `experiments/EXP-ISADV-001/audit_isadv.py`
- ledger ID: ECFG-NR-1515 (proposed, if phase-2 confirms the null) / ECFG-P-1515 (if a policy passes the gate)

---

## Candidate A3: Mason–Stothers/Evertse certified relation budgeting — S-unit bounds as a relation law

### One-sentence mechanism
Exploit function-field S-unit count bounds S (Mason–Stothers, Evertse, Beukers–Schlickewei 2^{8r+8}) to give *certified a priori upper bounds* on the number of smooth relations of a given shape, reducing the cost C of relation-search budget allocation P below the heuristic-estimate baseline B by replacing heuristics with theorems.

### Status
CONJECTURE (bounds are theorems; their tightness/applicability to summation-relation shapes is not)

### Novelty classification
LEDGER-NEW + LITERATURE-ADJACENT (the bounds exist; their use as ECDLP relation laws not located)

### Semantic fingerprint
- algebraic object: S-unit equation solutions over F_p(t) (function-field analog of smooth relations)
- available public operations: polynomial arithmetic, exact enumeration at toy degrees
- hidden structure exploited: radical-vs-degree (Mason–Stothers) control of solution counts
- information discarded: which specific relations occur
- information retained: certified upper bounds on relation counts per shape
- relation-generation primitive: none new
- compression primitive: theorem-gated budgeting (stop rules from bounds, not from heuristics)
- rank mechanism: none
- descent mechanism: none of its own — budgets existing descents
- dominant cost exponent: no exponent claim; constant-factor budget savings only, bounded by the gap between heuristic and certified counts

### Nearest ledger entries
1. **RT-1476** (relation-trace audit): audits measured counts; distinction: A3 replaces measurement with certified bounds — theorem vs statistics.
2. **PO-transfer-007** (transfer-search document): budgeted transfers heuristically; distinction: same as above.
3. **NR-1477** (closed): heuristic budget failure; distinction: A3's bounds cannot silently over-promise (they are theorems), avoiding the exact recorded obstruction.
4. **NR-1489** (closed): adjacent budgeting assumption; distinction: certified vs assumed.
5. **PO96M2** (secondary-operation closure): unrelated mechanism; listed because its closure record shows the lab's budget-blowup pattern A3 would gate.

### Nearest literature
Stothers (1981), Mason (1984) (polynomial abc); Evertse (S-unit bounds); Beukers–Schlickewei (2^{8r+8} bound). Claims: finite, computable upper bounds on S-unit solutions of bounded degree/rank. Gap: bounds are worst-case and likely loose by large factors for the specific summation-relation shape — the certified budget may exceed the measured need by more than rho's constant, killing the advantage.

### Target family
Ordinary prime-field curves; relations modeled over F_p(t); excluded: anomalous, supersingular, genus>1 lift models (out of scope).

### Full algorithmic path
1. factor-base: mapped to the S-unit/rank-r setting;
2. relation generation: unchanged (existing generators);
3. witness extraction/verification: unchanged;
4. relation probability: **object of study** — certified upper bounds per shape vs measured;
5. matrix: unchanged;
6. calibration: budgets set from bounds;
7. descent: INCOMPLETE of its own (budget layer only);
8. offline/online: bound computation offline;
9. memory/parallelism: trivial.

### Cost model
Value = (heuristic-budget cost) − (certified-budget cost) ≥ 0 only when the certified bound is within a constant factor of the true count. Beukers–Schlickewei 2^{8r+8} is doubly exponential in rank r — for r ≥ 2 the certified budget likely *exceeds* rho's total cost, making the candidate cost-negative unless tighter shape-specific bounds (Mason–Stothers direct) apply. Honest expectation: useful as a *disproof instrument* (certified impossibility of budgets) more than as a budgeting tool.

### Why the existing negative results do not already kill it
No ledger entry used certified arithmetic-geometry bounds; all budget closures were heuristic. New operation: theorem-gated stop rules.

### Likely fatal obstruction
Worst-case bounds are astronomically loose for relation-shaped equations; certified budgets lose to heuristic ones, which already lose to rho in the closed branches.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}, enumerate all S-unit-style relation instances of bounded degree, seeds 20260718+x; positive control: a synthetic S-unit family with known count must be bounded correctly (bound ≥ truth, within predicted factor); negative control: random equations (non-S-unit) must not satisfy the bound shape.

### Quantitative promotion gate
Certified bound within factor ≤ 4 of measured relation count at ≥3 toy sizes and ≥2 relation shapes; otherwise closed as "certified but useless" (scoped negative).

### Proof track
Theorem: a shape-specific Mason–Stothers-type bound for summation-relation equations with degree/radical ratio tight enough to bound counts within poly(r) of truth.

### Disproof track
Exhibit a relation shape where every S-unit-type bound exceeds the true count by >2^{r}; or measurement showing the ratio bound/truth grows with p at toy scale.

### Reproduction artifact
- contract: `experiments/EXP-SUNIT-001/contract.md`
- implementation: `experiments/EXP-SUNIT-001/sunit_budget.py`
- results: `experiments/EXP-SUNIT-001/smoke_results.json`
- audit script: `experiments/EXP-SUNIT-001/audit_sunit.py`
- ledger ID: ECFG-RT-1516 (proposed)

---

## Candidate B1: Relation-enumerator representation — relations as code words, MacWilliams as exact relation-count calculus

### One-sentence mechanism
Re-represent the relation-search space S as an evaluation (algebraic-geometry) code over F_q so that relation counts become code weight enumerators, reducing the cost C of relation-count prediction and factor-base sizing P below the sample-and-fit baseline B by making counts exactly computable via dual-code (MacWilliams) transforms.

### Status
CONJECTURE (the representation is exact; whether the enumerators are *cheaper to compute than the counts themselves* is open)

### Novelty classification
LEDGER-NEW + NOVELTY-UNVERIFIED (AG-code cryptanalysis exists — Minder, Faure–Minder, Márquez-Corbella–Pellikaan — but attacks curve codes; the reverse direction, ECDLP relation enumeration *via* code duality, not located in the documented search)

### Semantic fingerprint
- algebraic object: AG evaluation code C_L(D,G) built from the relation locus; its dual
- available public operations: evaluation at rational points, syndrome computation, MacWilliams transform at toy lengths
- hidden structure exploited: duality — counts in C become coefficients in C⊥'s enumerator
- information discarded: relation identities (only counts retained)
- information retained: full weight distribution of the relation-indicator code
- relation-generation primitive: evaluation map (unchanged substrate, new reading)
- compression primitive: MacWilliams identity (enumerator of C from enumerator of C⊥)
- rank mechanism: code dimension k = ℓ(G) via Riemann–Roch (exact, theorem-backed)
- descent mechanism: none new; enumerators calibrate factor-base size and stopping rules
- dominant cost exponent: enumerator computation is exponential in the *dual* dimension in the worst case — the open question is whether the dual is small for relation-shaped codes

### Nearest ledger entries
1. **PO-transfer-004** (transfer document): a representation change that preserved cost; distinction: B1's compression is an exact duality identity (theorem), not a relabeling.
2. **NR-1447** (coordinate diagnostics): statistic-of-coordinates family; distinction: weight enumerators are complete invariants of the code, not post-hoc features.
3. **NR-1504** (closed scheduling variant): no honest generator; B1 keeps the standard generator and only re-reads its output distribution.
4. **P1488** (tensor-train closure): also a compression-of-counting attempt; distinction: P1488 compressed the *tensor*; B1 compresses the *count function* via duality — different object.
5. **NR-1493** (output-sensitive resultant, closed): same goal (count before generating); distinction: resultants vs code duality, algebraically disjoint mechanisms.

### Nearest literature
Semaev 2004/031 (relation substrate); AG-code literature (Goppa; Minder thesis; Faure–Minder; Márquez-Corbella–Pellikaan — code-side attacks); MacWilliams identity (standard). Gap: no source computes ECDLP relation counts as weight enumerators. Claims and assumptions: Riemann–Roch gives dimensions; duality gives transforms — but enumerator *computation* cost is the whole question.

### Target family
Ordinary prime-field curves, prime-order subgroup; codes over F_q built from the curve itself; excluded: anomalous, supersingular (code structure degenerates there — analyzed separately if used).

### Full algorithmic path
1. factor-base: divisor G = factor-base formal sum; D = evaluation points;
2. relation generation: evaluation (unchanged);
3. witness extraction/verification: any enumerated relation still verified by group law (no change);
4. relation probability: **object of study** — exact enumerator coefficients vs sampled rates;
5. matrix: generator/parity-check matrices of C and C⊥, dimensions from Riemann–Roch, density low (evaluation structure);
6. factor-log calibration: from exact counts if the gate is met;
7. descent: INCOMPLETE of its own (enumeration layer only);
8. offline/online: enumerator computation offline per (E, factor base);
9. memory/parallelism: enumerator via MacWilliams needs O(q^{k⊥}) naive — the candidate dies here unless structure (automorphisms, folded codes) cuts k⊥.

### Cost model
Honest: naive enumerator cost Θ(q^{min(k,k⊥)}) is *worse* than generating all relations. The candidate has value only if relation-shaped codes have k⊥ = O(log q) or admit group-algebra-factored transforms. Compared to rho (0.886·√n) and BSGS: B1 is not an attack; it is an exact-calculus proposal whose best case removes sampling error from every budget decision; worst case it is an expensive restatement (then closed as scoped negative).

### Why the existing negative results do not already kill it
P1488 closed tensor compression; NR-1493 closed resultant counting; neither touched code duality. New operation: MacWilliams transform on the relation-indicator code. Obstruction avoided: "compression must materialize the object" — duality never materializes relations.

### Likely fatal obstruction
k⊥ is large (≈ q − ℓ(G)) for relation-shaped codes, making the dual transform exponentially expensive — the enumerator is harder than the enumeration.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}, full enumeration of relations at tiny sizes gives ground-truth enumerators; compute via duality; seeds 20260718+x; positive control: Reed–Solomon sanity case (known enumerator via MDS theorem) must match; negative control: scrambled evaluation order must destroy the predicted enumerator.

### Quantitative promotion gate
Dual-transform cost ≤ (ground-truth enumeration cost)/4 at ≥3 increasing sizes *with a falling trend*, and dimension ratio k⊥/log q bounded; otherwise closed.

### Proof track
Theorem: relation-indicator codes from summation loci have dual distance/dimension structure permitting a sub-enumeration-cost enumerator algorithm (e.g., via code automorphisms = curve isomorphisms).

### Disproof track
Riemann–Roch computation showing k⊥ = Θ(q) for all relation-shaped G, or measured transform cost scaling ≥ enumeration at 3 sizes.

### Reproduction artifact
- contract: `experiments/EXP-AGC-001/contract.md`
- implementation: `experiments/EXP-AGC-001/enumerator.py`
- results: `experiments/EXP-AGC-001/smoke_results.json`
- audit script: `experiments/EXP-AGC-001/audit_agc.py`
- ledger ID: ECFG-RT-1517 (proposed)

---

## Candidate B2: Function-field xedni — rank-1 elliptic-surface Mordell–Weil lattices over F_p(t)

### One-sentence mechanism
Lift the ECDLP to a rank-1 elliptic surface S over F_p(t) whose Mordell–Weil lattice is exactly computable, so that discrete-log relations become section-specialization identities, reducing the cost C of relation generation P below the summation-polynomial baseline B by replacing solving with linear algebra in the Mordell–Weil lattice.

### Status
HYPOTHESIS (classical xedni is known-fatal at scale — the function-field variant inherits that risk; toy-scale rank behavior is unmeasured)

### Novelty classification
LEDGER-NEW + LITERATURE-ADJACENT (xedni: Silverman DCC 20:5–40, 2000; fatal analysis: Jacobson–Koblitz–Silverman–Stein–Teske DCC 20:41–64, 2000. The function-field-surface variant with exact Mordell–Weil lattice computation — Shioda–Tate — was not located; UNVERIFIED beyond the documented search)

### Semantic fingerprint
- algebraic object: elliptic surface ℰ → P¹ over F_p, Mordell–Weil group ℰ(F_p(t)), height pairing lattice
- available public operations: section arithmetic, specialization homomorphisms ℰ(F_p(t)) → E_t(F_p), Shioda–Tate rank formula
- hidden structure exploited: global relations among sections specialize to local ECDLP relations
- information discarded: individual summation-polynomial systems
- information retained: the height-pairing Gram matrix (exact lattice)
- relation-generation primitive: section specialization at deg-1 places
- compression primitive: Mordell–Weil lattice (rank r replaces exponential search)
- rank mechanism: Shioda–Tate: ρ = r + 2 + Σ(m_v − 1)
- descent mechanism: target descent = expressing the target's lift in the lattice basis, then specializing
- dominant cost exponent: unknown — governed by the probability that a random curve is a *specialization* of a rank-≥1 surface with the right sections; xedni analysis says this probability collapses as p grows (the inherited fatal obstruction)

### Nearest ledger entries
1. **TRANSFER-P075** (Lang fiber: exact DLP-free transport from scalar multiplication to Frobenius translation): also a global-lift transport; distinction: Lang transport moves *points along Frobenius orbits* with Θ(q) table state (correctness-only, explicitly not an algorithmic gain); B2 moves *relations through section specialization* — different morphism (specialization vs translation), and B2 is honest about needing a sub-rho evaluator where P075 explicitly disclaims one.
2. **TRANSFER-H010/H012** (open transfer hypotheses): same family of global-to-local moves; distinction: those transfer scalar/hidden maps; B2 transfers group-law relations via a surface.
3. **PO96V** (transfer saga closure): closed a hidden-map channel; distinction: B2's channel is a *rank* condition (Shioda–Tate), not a hidden map.
4. **NR-1501** (closed): adjacent lift attempt; distinction: B2's lift is to a *surface with computable lattice*, not to a scalar cover.
5. **NR-1492** (BKK closure): both count solutions of polynomial systems; distinction: B2 never solves the summation system — it replaces it with lattice membership.

### Nearest literature
Silverman 2000 (xedni proposal, claims: lift ECDLP to global field, use height functions); Jacobson–Koblitz–Silverman–Stein–Teske 2000 (claim: probability that lifted points are dependent/independent kills the attack as p → ∞); Shioda–Tate formula (standard); Yun–Zhang 2017/2019 (function-field arithmetic uses the same surfaces, different purpose). Gap: no function-field toy measurement of the xedni obstruction; assumption inherited: specialization density behaves like the classical case.

### Target family
Ordinary prime-field curves that are specializations ℰ_{t₀} of rank-≥1 elliptic surfaces over F_p(t); excluded: constant/iso-trivial surfaces, anomalous or supersingular specializations, j=0/1728 (extra sections may confound controls).

### Full algorithmic path
1. factor-base: sections {s₁..s_r} spanning ℰ(F_p(t)), specialized at t₀;
2. relation generation: specialize random lattice combinations at deg-1 places;
3. witness extraction/verification: specialization identity verified by point addition on E_{t₀} (exact);
4. relation probability: **the open quantity** — fraction of t-specializations landing in the factor base, measured at toy scale;
5. matrix: height-pairing Gram matrix, r×r, dense but tiny (r ≤ 8 at toy scale); the ECDLP-sized matrix is unchanged;
6. factor-log calibration: from lattice coefficients;
7. descent: express lifted target in the section lattice (lattice reduction, exact if rank small) then specialize — **this is the xedni step whose failure probability the 2000 analysis bounds**;
8. offline/online: surface + lattice offline per curve family; specialization online;
9. memory/parallelism: lattice is tiny; parallelizable over specializations.

### Cost model
Setup: Õ(d²·p²) toy surface/section enumeration (d = section degree bound). Attack cost if rank-1 lift exists: O(poly(r)·log²p) per relation — exponentially better than solving S_m *per relation* — multiplied by the probability P_lift that the target admits the needed lift. JKSST 2000: P_lift → 0 like (log p)^{-Θ(1)} or worse in the classical case; unless the function-field variant changes P_lift's scaling, complete cost stays ≫ rho 0.886·√n. The toy gate measures P_lift's *trend*; toy correctness alone is not evidence (per AGENTS.md rule 7).

### Why the existing negative results do not already kill it
The ledger closed lift/transfer channels that were *maps*; the xedni obstruction (lift-probability collapse) was never measured in-ledger, and the function-field variant (exact lattice via Shioda–Tate instead of uncomputable Mordell–Weil over Q) changes the substrate: ranks over F_p(t) are *larger and computable* (Tate conjecture regime for surfaces), which is precisely the ingredient classical xedni lacked. New operation: exact Mordell–Weil lattice computation replacing uncomputable global descent.

### Likely fatal obstruction
P_lift collapses exactly as in JKSST 2000; larger function-field ranks do not repair the specialization-density exponent.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}, enumerate degree-≤1 sections x(t) = x₀+x₁t of toy surfaces y² = x³ + a(t)x + b(t), build section lattices, seeds 20260718+x; positive control: a planted section (constructed surface) must be recovered by the lattice; negative controls: random cubic polynomials (non-square) must not appear; iso-trivial surfaces must be flagged and excluded. Measure rank-1 frequency vs the xedni-independence prediction.

### Quantitative promotion gate
Measured P_lift(p) at ≥3 toy sizes must decay strictly slower than the JKSST-type prediction fitted at the same sizes, with the gap growing; equivalently a fitted exponent α in P_lift ~ p^{-α} with α < 1/2 and 95% CI excluding the classical prediction. Otherwise closed as scoped negative.

### Proof track
Theorem: for an explicit family of non-isotrivial elliptic surfaces over F_p(t), the specialization map ℰ(F_p(t)) → E_{t₀}(F_p) is surjective onto the prime-order subgroup with density bounded below by p^{-α}, α < 1/2 (a function-field analog of a *quantitative* xedni-density statement; likely false — hence falsifiable).

### Disproof track
A specialization-density upper bound (large-sieve over t) matching JKSST; or measured α ≥ 1/2 at 3 sizes.

### Reproduction artifact
- contract: `experiments/EXP-XEDN-001/contract.md`
- implementation: `experiments/EXP-XEDN-001/xedni_sections.py`
- results: `experiments/EXP-XEDN-001/smoke_results.json`
- audit script: `experiments/EXP-XEDN-001/audit_xedn.py`
- ledger ID: ECFG-P1518 / ECFG-NR-1518 (proposed, outcome-dependent)

---

## Candidate B3: Coppersmith small-root lattices for windowed relation finding

### One-sentence mechanism
Replace resultant elimination S with Coppersmith-type bivariate small-root lattices so that summation-polynomial relations are found only inside a small window XY < W^{1/2}, reducing the cost C of relation generation P below the full-solve baseline B when relations are only needed in a corner of the search box.

### Status
CONJECTURE (the window bound XY < W^{1/2} is the named obstruction; no reason yet to believe relation distribution concentrates in the window)

### Novelty classification
LEDGER-NEW + LITERATURE-ADJACENT (Coppersmith methods are standard and appear in isogeny norm equations; application to summation-polynomial relation finding not located in the documented search)

### Semantic fingerprint
- algebraic object: bivariate summation polynomial S₃(x₁, x₂) restricted to a window [0,X]×[0,Y]
- available public operations: lattice reduction (LLL, exact at toy dimension), polynomial shifts
- hidden structure exploited: small roots of modular/bivariate equations below the Coppersmith bound
- information discarded: all roots outside the window
- information retained: certified complete root list inside the window (lattice methods are complete within their bound)
- relation-generation primitive: small-root lattice solving
- compression primitive: windowing (search-space truncation with completeness certificate)
- rank mechanism: lattice determinant vs shift-monomial count (Howgrave-Graham)
- descent mechanism: unchanged (standard factor-base descent fed by windowed relations)
- dominant cost exponent: unchanged 1/2 unless relation density is window-concentrated (measured, not assumed)

### Nearest ledger entries
1. **NR-1493** (output-sensitive resultant, closed): same goal (generate only what you need); distinction: resultants vs lattices — and NR-1493's recorded obstruction (output-sensitive enumeration still costs like the full solve) is exactly what the window bound must beat.
2. **NR-1486** (closed resultant surface): distinction: elimination vs approximate-common-divisor/lattice methods.
3. **NR-1490** (closed): adjacent solver variant; distinction: certified window completeness vs solver swap (solver swaps alone are excluded by the novelty standard — the window certificate is the claimed new operation).
4. **P1494** (adjacent active line): shares the "restrict the box" intuition; distinction: P1494 restricts via algebraic constraints; B3 restricts via archimedean window + completeness certificate.
5. **RT-1476** (rate audit): provides the density baseline B3's window rates compare against.

### Nearest literature
Coppersmith (small roots, bivariate); Howgrave-Graham (modular reformulation); Coron (bivariate bounds); used in isogeny norm equations (e.g., PQCrypto-era norm solving). Gap: no application to summation polynomials located; assumption needed: relation x-coordinates are not equidistributed (contradicts D2's quasirandomness — tension acknowledged).

### Target family
Ordinary prime-field curves, prime-order subgroup; excluded: anomalous, supersingular; windows defined modulo p (wraparound handled by shift).

### Full algorithmic path
1. factor-base: standard small-x or subgroup-x base;
2. relation generation: LLL on the shift lattice of S₃(x₁,x₂) mod p inside window;
3. witness extraction/verification: each lattice root verified by direct substitution + group-law relation check (exact);
4. relation probability: **object of study** — windowed density vs global density;
5. matrix: lattice basis (dim (d+1)²-ish for degree d shifts, dense integers, bit-size ~ log p); ECDLP matrix unchanged;
6. calibration: windowed rate feeds existing calibration;
7. descent: standard once relations exist;
8. offline/online: lattice construction per (curve, window) offline;
9. memory/parallelism: lattice memory polynomial in shift degree; parallel over windows.

### Cost model
LLL on dimension-D lattice with B-bit entries: Õ(D⁶·B³) classical, D≈(d+1)². To be useful: windowed hit rate ρ_W must satisfy ρ_W > (XY/p²)·(1+ε) (window concentration) AND total lattice cost over all windows < full-solve cost. If relations equidistribute (D2's prediction), ρ_W = XY/p² and B3 loses to NR-1493's recorded baseline by the lattice overhead — cost-negative. Gate measures ε directly.

### Why the existing negative results do not already kill it
NR-1493 closed output-sensitive *enumeration*; it never measured windowed density concentration, and lattice small-root methods give *completeness within the bound*, a property resultants lack. New operation: Howgrave-Graham shift lattice on the summation polynomial.

### Likely fatal obstruction
Equidistribution (D2): windows are fair game, so windowing buys nothing and lattice overhead loses to the closed resultant baseline.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431, 809}, enumerate all S₃ relations exactly, measure windowed density ε across a grid of windows, seeds 20260718+x; positive control: planted small-root instance must be recovered by the lattice within bound; negative control: random bivariate polynomial must yield no spurious roots.

### Quantitative promotion gate
Measured window concentration ε > 0 beyond 3× sampling error at ≥3 sizes, with per-window lattice cost < (enumerated-window cost)/2; otherwise closed.

### Proof track
Theorem: summation-polynomial root distribution in boxes has a bilinear/discrepancy bound (Burgess-type) strong enough to certify ε > 0 for XY ≫ p^{3/2+δ} — or the negative theorem that no such bound can beat equidistribution.

### Disproof track
Discrepancy upper bound at equidistribution level (likely, via Weil bounds on the cover — ties to D2); or measured ε ≈ 0 at 3 sizes.

### Reproduction artifact
- contract: `experiments/EXP-COPP-001/contract.md`
- implementation: `experiments/EXP-COPP-001/window_lattice.py`
- results: `experiments/EXP-COPP-001/smoke_results.json`
- audit script: `experiments/EXP-COPP-001/audit_copp.py`
- ledger ID: ECFG-RT-1519 (proposed)

---

## Candidate C1: Buium arithmetic δ-characters — the Manin-kernel channel

### One-sentence mechanism
Exploit arithmetic differential-algebra structure S (Buium's order-2 δ-character, which exists exactly for ordinary non-canonical-lift curves) to define a new character-like channel on E(F_p), reducing the cost C of target identification P below the generic baseline B — speculatively by making the discrete log visible to a δ-character evaluation.

### Status
CONJECTURE (high risk: lift-dependence and the mod-p shadow of δ-characters are the named obstructions)

### Novelty classification
LEDGER-NEW + NOVELTY-UNVERIFIED (Buium, Invent. Math. 122 (1995) 309–340 gives existence of the order-2 character precisely on ordinary non-Serre–Tate curves; no ECDLP application located in the documented search)

### Semantic fingerprint
- algebraic object: p-derivation δ and the arithmetic jet space J²(E); the δ-character ψ: E(Z_p) → Z_p
- available public operations: p-adic lifting, δ evaluation (polynomial in coordinates + lifted Frobenius)
- hidden structure exploited: existence of ψ is equivalent to the *failure* of the canonical lift — the curve's ordinary-but-not-special position
- information discarded: the group structure's prime-to-p parts
- information retained: ψ-values (a genuine character — a *homomorphic* invariant, unlike any x-coordinate statistic)
- relation-generation primitive: δ-character evaluation on multiples (speculative)
- compression primitive: character linearity: ψ(nP) = n·ψ(P) — log linearity *in the p-adic character group*, which is NOT the ECDLP group; the gap is the candidate
- rank mechanism: none
- descent mechanism: none yet — INCOMPLETE (no route from ψ-values to F_p-logs identified; that identification is the research question)
- dominant cost exponent: undefined (no complete path); evaluation cost Õ(log²p) per point

### Nearest ledger entries
1. **JET-001 (workspace prior-round record, EXP-JET closures)**: Hasse-jet lifting of the addition law, closed scoped-negative; distinction: Hasse jets are *characteristic-p* derivatives of the group law; Buium δ is a *mixed-characteristic* p-derivation with Frobenius — different operator, different existence theorem. The EXP-JET obstruction (jets collapse mod p) is precisely why C1 uses mixed characteristic — and also why C1's own obstruction is lift-dependence.
2. **PO96R / PO96U** (transfer saga closures): hidden-map channels; distinction: ψ is a *publicly computable* character, not a hidden map — it avoids the hidden-map obstruction but buys its own (triviality of the mod-p shadow).
3. **PO96V**: same distinction.
4. **NR-1501** (closed lift attempt): scalar-cover lift; distinction: jet-space lift with an existence theorem tied to the curve's arithmetic type.
5. **TRANSFER-P075** (Lang fiber): exact Frobenius transport; distinction: Lang uses geometric Frobenius on covers; C1 uses arithmetic Frobenius inside the p-derivation.

### Nearest literature
Buium 1995 (existence iff good reduction and not canonical lift); Buium–Poonen (Manin-kernel arithmetic analogs); anomalous-curve attacks (Smart; Satoh–Araki; Semaev 1998 — p-adic lifts DO break anomalous curves, the encouraging precedent). Claims/assumptions: ψ is computable; its kernel is the arithmetic Manin kernel. Gap: anomalous attacks work because #E = p; for prime-order subgroups of ordinary curves the mod-p reduction of ψ may be identically zero — no published statement either way located.

### Target family
Ordinary prime-field curves, explicitly **excluding canonical/Serre–Tate lifts** (no order-2 character exists there — Buium's theorem makes the exclusion precise) and anomalous curves (already broken; excluded as targets but used as positive controls).

### Full algorithmic path
1. factor-base: undefined — INCOMPLETE;
2. relation generation: speculative ψ-evaluations;
3. witness extraction/verification: ψ computed two ways (definition vs linearity prediction) — self-verifying;
4. relation probability: not defined yet;
5. matrix: none;
6. calibration: none;
7. descent: INCOMPLETE — the missing stage is a theorem linking ψ(P), ψ(Q) and log(Q base P);
8. offline/online: p-adic setup offline per curve;
9. memory/parallelism: trivial.

### Cost model
No complete path — no rho comparison possible yet (this alone keeps C1 out of the winners). Evaluation: Õ(log²p) per ψ. IF a log-visibility theorem existed with character overhead O(polylog), the exponent question would reduce to D3-style cohomological obstructions; as stated, the candidate is a probe for the theorem, not an attack.

### Why the existing negative results do not already kill it
EXP-JET closed characteristic-p jets; no ledger entry touched mixed-characteristic characters. New operation: Buium's p-derivation character with its exact existence dichotomy.

### Likely fatal obstruction
ψ(P) mod p is identically 0 on E(F_p) (the character lives one p-adic digit above the visible one), making the channel invisible at the ECDLP layer — the p-adic analog of the EXP-JET collapse.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}, implement p-derivation δ on lifts of toy curves, compute ψ on all points, seeds 20260718+x; positive control: anomalous curve (p-adic attack must recover a planted log — literature-backed); negative controls: canonical-lift curve (ψ must NOT exist — Buium dichotomy) and random non-character function (must fail linearity).

### Quantitative promotion gate
ψ mod p nonzero on ≥1% of points AND ψ(nP) ≡ n·ψ(P) exactly at ≥3 toy sizes; if ψ ≡ 0 mod p everywhere at 2 sizes, closed.

### Proof track
Theorem: for ordinary non-canonical E/F_p, the reduction of ψ mod p is a nonzero F_p-valued function on E(F_p) (or its vanishing — the disproof).

### Disproof track
Direct computation showing ψ(E(Z_p)) ⊂ pZ_p always; or a Manin-kernel argument that the F_p-points lie in the kernel.

### Reproduction artifact
- contract: `experiments/EXP-DCHAR-001/contract.md`
- implementation: `experiments/EXP-DCHAR-001/dchar.py`
- results: `experiments/EXP-DCHAR-001/smoke_results.json`
- audit script: `experiments/EXP-DCHAR-001/audit_dchar.py`
- ledger ID: ECFG-RT-1520 (proposed)

---

## Candidate C2: Imprimitive-monodromy resolvent decomposition of the summation cover

### One-sentence mechanism
Test whether the Galois monodromy S of the m-th summation cover is genuinely the full (wreath) group, and where it is imprimitive, exploit the block system via resolvents to split relation finding into smaller covers, reducing the cost C of relation generation P below the full-cover baseline B by a divide-and-conquer the full group forbids.

### Status
HYPOTHESIS (attack value conditional on discovering imprimitive families; the census itself is certain to produce *some* verdict — this is D2's two-sided experiment)

### Novelty classification
LEDGER-NEW + POSSIBLY NOVEL (documented search §2.10: no Galois/monodromy treatment of summation covers located; resolvent methods are classical)

### Semantic fingerprint
- algebraic object: Galois closure of the m-th Semaev cover; its block systems; Lagrange resolvents
- available public operations: exact factorization, cycle-type census, resolvent construction at toy degree
- hidden structure exploited: imprimitivity blocks = hidden product/fiber structure of the relation space
- information discarded: individual relations during the census
- information retained: block system + decomposition law (Frobenius cycle types per block)
- relation-generation primitive: resolvent-split sub-cover solving (only if imprimitivity found)
- compression primitive: block decomposition (degree d = b·e splits into covers of degree b and e)
- rank mechanism: none directly
- descent mechanism: blockwise descent mirrors target descent (structured, smaller systems)
- dominant cost exponent: IF imprimitive with block size shrinking with m, relation cost drops from O(p^{2−2/m})-style toward the sub-cover exponent — a genuine exponent claim, hence high-risk

### Nearest ledger entries
1. **NR-1492** (BKK closure): counted solutions without structure; distinction: C2 seeks *group-theoretic* structure (block systems), invisible to mixed-volume counting.
2. **NR-1480/1481** (closed): cover-manipulation variants; distinction: those manipulated the cover's equations; C2 computes its Galois group — an invariant the equations-only closures never touched.
3. **P1510/P1511** (Hasse-jet sections): local structure of the same cover; distinction: jets are infinitesimal; monodromy is global — complementary, and P1510's closures do not bound C2.
4. **TRANSFER-NR-079/080** (closed transfer channels): hidden scalar maps; distinction: block systems are *provable from public factorizations*, not hidden.
5. **RT-1476** (rate audit): quasirandom baseline; distinction: C2 explains (or kills) rate deviations via group structure rather than recording them.

### Nearest literature
Semaev 2004/031; Faugère–Huot–Joux–Renault–Vitse (symmetrized variants — they use the *known* S_{m-1} symmetry, which is the generic wreath structure; nothing finer); Harris-style monodromy computation methods. Gap: whether special families (CM, small-discriminant, special endomorphism structure) force proper subgroups is uncomputed. Assumption: at toy degrees the census is exact (it is — brute factorization).

### Target family
Ordinary prime-field curves, prime-order subgroup; special families (CM j-invariants, excluding j=0/1728 from random controls but analyzed as target families) are the prime suspects for imprimitivity; excluded: anomalous, supersingular.

### Full algorithmic path
1. factor-base: standard;
2. relation generation: resolvent-split solving IF imprimitive; else the candidate is a measurement (with D2 archiving the barrier);
3. witness extraction/verification: block membership + factorization certificates, exact;
4. relation probability: Chebotarev on the true group (replaces quasirandom assumption);
5. matrix: unchanged downstream; possibly smaller effective systems per block;
6. calibration: from measured group-specific densities;
7. descent: blockwise — INCOMPLETE until an imprimitive family is exhibited;
8. offline/online: census + resolvents offline per family;
9. memory/parallelism: census embarrassingly parallel; resolvent construction memory-heavy only at large degree (out of scope).

### Cost model
Census: Õ(S·m·log²p) (as A1). IF imprimitive with blocks of size e = d/b: relation solve cost drops by factor ~ (d/e)^{ω−1}-ish per system at fixed field — at cryptographic sizes a constant-to-subexponential gain depending on how b scales with m; the exponent claim is conditional and flagged as such. Against rho 0.886·√n: even a 2× relation-finding gain does not beat rho alone (PO68/PO71: linear algebra and descent dominate) — the gate therefore demands a *scaling* effect in m, not a constant.

### Why the existing negative results do not already kill it
All closed cover branches manipulated equations or counted solutions; none computed the Galois group. New operation: cycle-type census + resolvent block test. Obstruction avoided: "another cover manipulation" — C2 is an invariant computation, falsifiable either way.

### Likely fatal obstruction
The group is the full wreath product for all ordinary curves (generic expectation; D2); no resolvent exists; candidate closes as the strongest-yet form of the quasirandomness barrier.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431, 809}, exact cycle-type census of the decomposition cover at m=2,3 (degrees small enough for exact group computation by factorization), seeds 20260718+x; positive control: an intentionally imprimitive constructed cover (product polynomial) must be detected with its block system; negative control: random polynomials (full S_d by Hilbert) must test primitive/full.

### Quantitative promotion gate
Detection of a non-full group on a non-excluded ordinary curve family with Chebotarev-consistent densities at ≥3 sizes AND a measured block structure whose resolvent solve cost beats the full-cover solve by a factor growing with m; the null result (full group everywhere within Weil error at ≥3 sizes, ≥2 m) promotes D2 and closes C2.

### Proof track
Theorem: geometric monodromy of the m-th Semaev cover = wreath product for all ordinary E (barrier theorem), OR exhibition of an exceptional locus with proper monodromy + density bounds.

### Disproof track
The barrier theorem itself; or census agreement with the full group at all tested sizes.

### Reproduction artifact
- contract: `experiments/EXP-IMON-001/contract.md`
- implementation: `experiments/EXP-IMON-001/imon_group.py`
- results: `experiments/EXP-IMON-001/smoke_results.json`
- audit script: `experiments/EXP-IMON-001/audit_imon.py`
- ledger ID: ECFG-RT-1521 (proposed)

---

## Candidate C3: Function-field Heegner/Drinfeld special-cycle height channel

### One-sentence mechanism
Exploit special-cycle structure S on Drinfeld modular surfaces (Yun–Zhang higher Gross–Zagier territory) so that target discrete logs become intersection multiplicities/height pairings of special cycles, reducing the cost C of individual-log extraction P below the descent baseline B by reading logs from heights instead of solving systems.

### Status
CONJECTURE (highest risk in the set; shares its surface substrate with B2 — see red team §7)

### Novelty classification
LEDGER-NEW + NOVELTY-UNVERIFIED (Yun–Zhang Annals 2017/2019, Howard–Shnidman arXiv:1707.00213, Shnidman 2024 exist as mathematics; any computational-ECDLP reading not located)

### Semantic fingerprint
- algebraic object: Drinfeld modular surfaces / elliptic surfaces with special cycles (Heegner-type points)
- available public operations: cycle construction, intersection pairing, specialization (toy scale)
- hidden structure exploited: height pairings of special cycles encode arithmetic data (L-values in the literature; here: speculatively, logs)
- information discarded: the ECDLP group's cyclic structure (kept only inside cycle coordinates)
- information retained: intersection numbers (exact integers)
- relation-generation primitive: special-cycle construction
- compression primitive: height pairing (bilinear, lattice-valued)
- rank mechanism: rank of the special-cycle lattice (Manin–Drinfeld-type finiteness)
- descent mechanism: height-to-log reading — INCOMPLETE, no such map is known; constructing it is the candidate
- dominant cost exponent: undefined

### Nearest ledger entries
1. **TRANSFER-P075** (Lang fiber): exact transport channel; distinction: heights are *quadratic-form* invariants, not fiber transports.
2. **TRANSFER-H010/H012** (open transfer hypotheses): same global-to-local family; distinction: cycle intersections vs scalar maps.
3. **PO96M2** (secondary-operation closure): also a higher-structure channel; distinction: PO96M2's obstruction (cohomological vanishing, cf. D3) does not apply to *geometric* cycle classes with Frobenius descent — that loophole is C3's only breathing room and D3's stated exception.
4. **NR-1501**: lift closure; distinction as in B2.
5. **B2 (this document)**: shares the elliptic-surface substrate; the red team (§7) attempts the collapse; the distinction maintained: B2 uses the *group* of sections (additive structure), C3 uses *intersection numbers of cycles* (quadratic structure) — different pairings, different read-outs.

### Nearest literature
Yun–Zhang 2017/2019 (higher Gross–Zagier: heights of special cycles = derivatives of L-functions over function fields); Howard–Shnidman (special cycles); Shnidman 2024 (Manin–Drinfeld function field). Claims in literature: height/L-value identities. Gap: no identity links heights to discrete logs; assumption needed: a Gross–Zagier-style formula with the log in the "L-value" slot — pure speculation, flagged.

### Target family
Elliptic surfaces over F_p(t) with Drinfeld-modular structure; ordinary specializations; excluded: isotrivial surfaces, anomalous/supersingular fibers, j=0/1728.

### Full algorithmic path
1. factor-base: special cycles above factor-base places;
2. relation generation: cycle intersections;
3. witness/verification: intersection numbers independently recomputed (exact);
4. relation probability: undefined — INCOMPLETE;
5. matrix: intersection matrix of cycles (toy: small);
6. calibration: none yet;
7. descent: INCOMPLETE (the height→log map is the missing theorem);
8. offline/online: cycle construction offline;
9. memory/parallelism: standard.

### Cost model
No complete path; no rho comparison possible (barred from winning). Toy cycle computation Õ(poly(d)·p²). Speculative best case inherits B2's P_lift obstruction plus its own missing-map obstruction — strictly worse positioned than B2.

### Why the existing negative results do not already kill it
The ledger has no cycle/height vocabulary at all (0 collisions). New operation: intersection-theoretic read-out.

### Likely fatal obstruction
No height→log map exists; heights see norms/traces (Frobenius-invariant data) and logs are exactly the non-invariant part — the same wall that closed every trace/norm channel in the ledger.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}, construct special cycles on toy Drinfeld-type surfaces, compute intersection matrices, seeds 20260718+x; positive control: a planted cycle with known intersection must be recovered; negative control: random divisors must not satisfy the special-cycle height identities; test: correlation of any height functional with planted logs must be 0 within error (predicted) — a nonzero correlation would be the (unlikely) promotion signal.

### Quantitative promotion gate
A height functional correlating with planted logs beyond 3σ at ≥3 sizes, with an explicit conjectured identity; absence at 2 sizes closes the candidate.

### Proof track
Theorem (would-be): a Gross–Zagier-type identity whose special-value side contains the discrete log. Almost certainly false — hence a clean disproof target.

### Disproof track
Proof that heights factor through the norm (killing log visibility); or the toy correlation null.

### Reproduction artifact
- contract: `experiments/EXP-HEEG-001/contract.md`
- implementation: `experiments/EXP-HEEG-001/special_cycles.py`
- results: `experiments/EXP-HEEG-001/smoke_results.json`
- audit script: `experiments/EXP-HEEG-001/audit_heeg.py`
- ledger ID: ECFG-RT-1522 (proposed)

---

## Candidate D1: Log-space pseudorandomness barrier — anomalous factor bases force GAP structure

### One-sentence mechanism
Prove (or refute at toy scale) that any factor base S with anomalously high relation rate must have additive-combinatorial GAP structure in log space, which contradicts the quasirandomness of elliptic-curve log maps — a barrier explaining *why* every relation-boosting branch closed, and exposing the precise loophole (structured-but-invisible bases) if the argument has a gap.

### Status
HYPOTHESIS (negative theory; the reduction is the deliverable)

### Novelty classification
LEDGER-NEW + LITERATURE-ADJACENT (quasirandomness of EC-derived sets: Liu–Gao 2009; energy methods: Shkredov, Schoen–Shkredov; BSG + Freiman are standard tools — their assembly into an ECDLP barrier statement not located)

### Semantic fingerprint
- algebraic object: the log map log_G: E(F_p) → Z/nZ as a pseudorandom function; additive energy of factor-base images
- available public operations: energy computation, BSG/Freiman at toy scale
- hidden structure exploited: none (barrier); the *absence* of structure is the claim
- information discarded: all geometry
- information retained: energy/GAP statistics of log-space images
- relation-generation primitive: n/a
- compression primitive: n/a
- rank mechanism: n/a
- descent mechanism: n/a (barrier candidate — exempt from descent-route rejection, scored on barrier value)
- dominant cost exponent: n/a — bounds other candidates' exponents

### Nearest ledger entries
1. **NR-1447** (coordinate additive-energy diagnostics): closest vocabulary; distinction: NR-1447 measured energy of *coordinate* sets; D1 works in *log space* and aims at an implication (anomaly ⇒ GAP ⇒ contradiction), not a diagnostic.
2. **ECFG-NR-1484** (division-character quotient characters give no rank advantage): a concrete instance D1 would explain; distinction: D1 is the meta-theorem, not a family result.
3. **ECFG-RT-1485** (Kummer differential state, constant fibers, quadratic support): another instance; same distinction.
4. **NR-1475 / NR-1479** (closed boosting branches): the pattern D1 claims to unify; distinction: unification + loophole statement vs individual closures.
5. **PO96M2** (secondary-operation closure): instance; distinction as above.

### Nearest literature
Liu–Gao 2009 (quasirandom subsets of Z_p from elliptic curves); Schoen–Shkredov (energy bounds); Balog–Szemerédi–Gowers + Freiman (standard). Gap: the assembled barrier theorem. Circularity acknowledged and priced (red team §7): quasirandomness of the log map *is* morally ECDLP-hardness; D1's value is making the bootstrap precise and toy-auditable, not proving it.

### Target family
Ordinary prime-field curves, prime-order subgroup; excluded: anomalous, supersingular (pseudorandomness fails differently there — separate analysis).

### Full algorithmic path
Barrier candidate — path stages 1–9 not applicable as an attack; the *audit* path: sample factor-base proposals from closed ledger branches, compute log-space energy/GAP statistics at toy sizes, compare against random-set controls.

### Cost model
Audit cost Õ(S²) energy computations per proposed base at toy scale. The barrier's content: any attack needing a relation-rate boost of factor p^δ needs a base with energy defect ≥ δ, which quasirandomness bounds to δ ≤ O(1/log p) — strangling exponent gains while permitting constant-factor ones (consistent with all ledger closures being constant-level).

### Why the existing negative results do not already kill it
Negative theory is not attacked by negative results; it organizes them. The new operation: log-space BSG/Freiman audit with random-set controls.

### Likely fatal obstruction
The reduction is circular at cryptographic sizes (quasirandomness unprovable without solving ECDLP), and at toy sizes everything is pseudorandom — the barrier may be unfalsifiable-in-both-directions, in which case it is philosophy, not science, and should be rejected.

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431, 809, 1601}, seeds 20260718+x: (i) verify random curve factor bases have energy within Weil-type error of random sets; (ii) *adversarially search* small bases for energy defects (the loophole probe); positive control: an arithmetic-progression base must be flagged GAP; negative control: random sets must not be flagged.

### Quantitative promotion gate
Barrier "confirmed" (as toy science): no adversarial base of size ≥ p^{1/4} with energy defect beyond 3σ at ≥3 sizes. Loophole "exposed": any such base found — immediately promoting the corresponding attack branch.

### Proof track
Theorem: quasirandomness (energy bound) for log-map images of subgroup-x sets under explicit Weil-type error terms.

### Disproof track
Exhibiting one anomalous base (kills the barrier, opens an attack) or showing the energy bound can never be certified below the needed threshold (kills the barrier's teeth).

### Reproduction artifact
- contract: `experiments/EXP-QRAND-001/contract.md`
- implementation: `experiments/EXP-QRAND-001/energy_audit.py`
- results: `experiments/EXP-QRAND-001/smoke_results.json`
- audit script: `experiments/EXP-QRAND-001/audit_qrand.py`
- ledger ID: ECFG-RT-1523 (proposed)

---

## Candidate D2: Full-monodromy rigidity barrier — Chebotarev forces quasirandom relation rates

### One-sentence mechanism
Establish that the summation cover has full (wreath) monodromy for all ordinary curves, so that Chebotarev forces relation rates to their quasirandom values up to Weil error — a theorem-grade barrier that closes every exceptional-rate sieve (including A1/C2 attack content) in one stroke, with the loophole being any certified exceptional locus.

### Status
HYPOTHESIS (negative theory; two-sided with A1/C2 — same census, opposite reading)

### Novelty classification
LEDGER-NEW + POSSIBLY NOVEL (same documented search as A1; the *barrier statement* for ECDLP relation rates not located)

### Semantic fingerprint
- algebraic object: same Galois closure as C2, read as a rigidity statement
- available public operations: cycle-type census, Weil-error bookkeeping
- hidden structure exploited: fullness of monodromy = absence of exploitable structure
- information discarded/retained: as C2
- relation-generation primitive: n/a
- compression primitive: n/a
- rank mechanism: n/a
- descent mechanism: n/a (barrier)
- dominant cost exponent: n/a — bounds others'

### Nearest ledger entries
1. **RT-1476** (rate audit): measured quasirandom-looking rates; distinction: D2 would *explain* them as a theorem (Chebotarev), not a coincidence of fixtures.
2. **NR-1477** (closed): heuristic rate assumption failure; distinction: D2 replaces assumptions with density theorems.
3. **PO-transfer-006** (transfer document): assumed-rate transfer failure; same distinction.
4. **NR-1489** (closed): adjacent; same distinction.
5. **NR-1492** (BKK closure): counting without structure; distinction: D2 supplies the missing structural reason the counting could not be beaten.

### Nearest literature
Chebotarev density theorem; Hilbert irreducibility (generic full monodromy); Weil bounds. Gap: the monodromy group of Semaev covers is uncomputed in the literature (documented search) — so the barrier is conjectural, not yet theorem.

### Target family
All ordinary prime-field curves (the barrier's strength is its generality); exclusions only for the exceptional-locus analysis.

### Full algorithmic path
Barrier — no attack path. Audit path = A1/C2 census read for fullness.

### Cost model
Census cost as A1. Content: any relation-rate-dependent attack's success probability is pinned within 2/√p of quasirandom, converting all "exceptional curve" hopes into an explicit exceptional-locus existence question.

### Why the existing negative results do not already kill it
They *support* it; nothing in the ledger states or tests the monodromy-fullness mechanism. New operation: monodromy census as barrier evidence.

### Likely fatal obstruction
The barrier is only as strong as its census/theory coverage; a single certified exceptional family breaks it — which is exactly C2's win condition (the two candidates are complementary by design).

### Minimal falsifying experiment
Shared with A1/C2: toy p ∈ {101, 211, 431, 809, 1601, 4099}, m=2,3, seeds 20260718+x; positive control: a planted imprimitive cover must be detected as non-full; negative control: random polynomials must read full.

### Quantitative promotion gate
Barrier "established at toy scale": cycle-type histograms match the full group within Weil error at ≥3 sizes and ≥2 m, on ≥20 random ordinary curves per size, zero exceptions beyond excluded families.

### Proof track
Theorem: geometric monodromy of the m-th Semaev cover is the full wreath product for ordinary E (Hilbert-irreducibility-style argument over the universal elliptic curve).

### Disproof track
Any certified exceptional locus (C2's gate) or census deviation beyond 3× Weil error.

### Reproduction artifact
- contract: shared with `experiments/EXP-IMON-001/contract.md` (two-sided experiment)
- implementation: `experiments/EXP-IMON-001/imon_group.py`
- results: `experiments/EXP-IMON-001/smoke_results.json`
- audit script: `experiments/EXP-IMON-001/audit_imon.py`
- ledger ID: ECFG-RT-1524 (proposed)

---

## Candidate D3: Cohomological-dimension barrier — cd(F_p)=1 kills secondary operations, and its geometric loophole is precise

### One-sentence mechanism
Unify the PO96M2-family closures (secondary/higher operations returning nothing) as a theorem: over F_p, cohomological dimension 1 forces all higher Massey-type operations on the relevant Galois modules to vanish, so no secondary channel can carry log information — with the loophole exactly identified as *geometric* classes (over F̄_p) with Frobenius descent data.

### Status
HYPOTHESIS (negative theory; the loophole clause is the falsifiable part)

### Novelty classification
LEDGER-NEW + NOVELTY-UNVERIFIED (cd(F_p)=1 is standard — Serre, Galois Cohomology; its use as an ECDLP secondary-operation barrier not located)

### Semantic fingerprint
- algebraic object: Galois cohomology H^i(G_{F_p}, −), i ≥ 2; Massey products
- available public operations: toy Brauer/cup-product computations
- hidden structure exploited: vanishing of H^{≥2}
- information discarded: all primary structure (already exploited everywhere)
- information retained: the exact obstruction certificate
- relation-generation primitive: n/a
- compression primitive: n/a
- rank mechanism: n/a
- descent mechanism: n/a (barrier)
- dominant cost exponent: n/a

### Nearest ledger entries
1. **PO96M2 / TRANSFER-NR-063** (secondary-operation closure): the chief instance D3 explains; distinction: instance vs theorem.
2. **TRANSFER-H017** (open): a would-be higher channel; distinction: D3 predicts its closure unless it uses geometric classes.
3. **PO96P-R1A** (adjacent closure): instance.
4. **TRANSFER-NR-076/078** (closed): instances.
5. **NR-1489** (closed): instance-adjacent.

### Nearest literature
Serre, Galois Cohomology (cd(F_p)=1); Milne, Étale Cohomology (geometric classes over F̄_p with Frobenius descent — the stated loophole, e.g. Tate conjecture regime, cf. B2's lattice). Gap: nobody has phrased the lab's repeated secondary-operation failures as this theorem (documented search).

### Target family
All ordinary prime-field curves; the loophole clause concerns geometric-cycle constructions (B2/C3 territory — cross-linked).

### Full algorithmic path
Barrier — no attack path. Audit: enumerate the closed secondary-operation branches, verify each one's channel factors through an H^{≥2} or fails the Frobenius-descent condition.

### Cost model
No attack cost. Audit cost trivial. Content: future secondary-operation proposals are rejected on sight unless they exhibit a geometric class with explicit Frobenius descent — a sharp, checkable gate.

### Why the existing negative results do not already kill it
They are its evidence base; the new operation is the unification + the precise loophole clause (which also keeps B2/C3-style geometric channels legally open — and thus falsifiable rather than vibes).

### Likely fatal obstruction
The unification may be wrong in detail: some closed channel may not factor through H^{≥2}, breaking the theorem's cover story; or the loophole clause may be vacuous (no geometric class ever descends at ECDLP-relevant sizes).

### Minimal falsifying experiment
Toy p ∈ {101, 211, 431}: (i) verify cup-product/Massey vanishings on the relevant modules by direct computation; (ii) attempt to construct one geometric class with Frobenius descent at toy scale (the loophole probe); positive control: a known H¹ class must be detected nonzero; negative control: a synthetic H² candidate over F_p must vanish.

### Quantitative promotion gate
Barrier "established": all ≥4 audited closures fit the pattern + toy vanishings confirmed at ≥3 sizes. Loophole "exposed": one descending geometric class found — immediately cross-promotes B2/C3-style channels.

### Proof track
Theorem: every secondary-operation channel of the PO96M2 type factors through H^{≥2}(G_{F_p}, M) = 0 for the relevant M — plus the descent criterion for the geometric exception.

### Disproof track
One audited closure that does not fit, or a descending class that carries no log information either (loophole vacuous).

### Reproduction artifact
- contract: `experiments/EXP-CDONE-001/contract.md`
- implementation: `experiments/EXP-CDONE-001/cup_vanishing.py`
- results: `experiments/EXP-CDONE-001/smoke_results.json`
- audit script: `experiments/EXP-CDONE-001/audit_cdone.py`
- ledger ID: ECFG-RT-1525 (proposed)

---

# 5. Ranking

Scores 0–5 per criterion. Hidden-cost risk is scored 5 = low risk. Attack candidates must pass all four rejection rules; D-group barrier candidates are exempt from the descent-route rule by design (their deliverable is a barrier theorem + toy audit, not an attack) and are marked †.

| Cand. | Distance | Verifier | Exponent chance | Path coverage | Toy falsif. | Lit. novelty | Hidden-cost risk (5=low) | Total | Rejection check |
|---|---|---|---|---|---|---|---|---|---|
| A1 mono census | 4 | 5 | 2 | 3 | 5 | 4 | 4 | **27** | passes (measurement candidate; descent-by-calibration declared INCOMPLETE openly) |
| A2 isogeny advice | 3 | 4 | 2 | 4 | 5 | 3 | 2 | 23 | passes; weakened by §9.1 |
| A3 S-unit budget | 4 | 4 | 2 | 3 | 4 | 4 | 4 | **25** | passes |
| B1 AG-code enumerator | 4 | 4 | 2 | 3 | 4 | 3 | 3 | 23 | passes |
| B2 function-field xedni | 4 | 3 | 2 | 4 | 4 | 4 | 3 | **24** | passes (specialization = descent route; rho comparison present; distinction from TRANSFER-P075 is mathematical: specialization morphism vs Frobenius-translation fiber) |
| B3 Coppersmith window | 3 | 4 | 2 | 3 | 4 | 3 | 3 | 22 | passes |
| C1 Buium δ-character | 5 | 2 | 2 | 2 | 3 | 4 | 2 | 20 | **rejected as winner**: stages 1,7 INCOMPLETE → no complete route to target descent; no rho comparison possible |
| C2 imprimitive monodromy | 4 | 4 | 3 | 3 | 5 | 4 | 3 | **26** | passes (conditional exponent claim flagged; descent blockwise, conditional on discovery) |
| C3 Heegner cycles | 5 | 2 | 2 | 2 | 3 | 3 | 2 | 19 | **rejected as winner**: stages 4,7 INCOMPLETE; no rho comparison possible |
| D1 log-space barrier † | 4 | 4 | — | — | 4 | 4 | 4 | (barrier) | exempt; falsifiable both directions |
| D2 full-monodromy barrier † | 4 | 4 | — | — | 5 | 4 | 4 | (barrier) | exempt; two-sided with A1/C2 |
| D3 cd(F_p)=1 barrier † | 4 | 3 | — | — | 3 | 3 | 4 | (barrier) | exempt; unification could break |

No candidate scores 3+ on "exponent chance": honest reflection of the ledger state — 761 negative rows have closed every constant-level channel tested, and no proposed mechanism here has a proved exponent. C2 is the only candidate with a *conditional* exponent mechanism (block decomposition shrinking with m), hence its 3.

## Winners

1. **Best conservative: A1** (EXP-MONO-001) — 27. Exact verifier, cheapest census, immediate archival value either way, and it is the shared harness for D2.
2. **Best representation-changing: B2** (EXP-XEDN-001) — 24. The only representation candidate with a complete (if probably doomed) descent route and a literature-named fatal obstruction that has never been *measured* in-ledger.
3. **Best high-risk: C2** (EXP-IMON-001) — 26. The only candidate carrying a conditional exponent mechanism, two-sided with D2 so the experiment cannot be wasted.

Contracts: §8. First commands: §8 and §9.

# 6. Red team — attempts to kill the three winners

## 6.1 Are A1/C2/D2 one object with three stances?
**Yes, partially — disclosed, not hidden.** All three share the decomposition-cover monodromy object. Defense: the *experiments* differ in what they must output. A1's deliverable is calibrated rate tables + an exceptional-curve sieve (it succeeds even if monodromy is full, by archiving certified rates). C2 succeeds only if a non-full group with exploitable block system is found (attack content). D2 succeeds only if fullness is established at theorem or strong-census level (barrier content). Running one census supports all three readings; we count that as efficiency, not duplication. The fingerprint components "relation-generation primitive" and "descent mechanism" genuinely differ across the three (none / resolvent-split / n/a).

## 6.2 B2 vs C3 collapse attempt
Both live on elliptic surfaces over F_p(t). Collapse argument: a section's height pairing is expressible via intersection numbers, so B2's lattice IS C3's intersection matrix. Partially true mathematically (Shioda's height = intersection-theoretic). The maintained distinction: B2 uses the **additive group structure** of sections (specialization is a homomorphism — logs could survive); C3 uses **quadratic height data** (Frobenius-invariant — logs provably die, same wall as closed trace/norm channels). So the collapse actually *strengthens* the red team: C3 is B2 with the log-carrying structure quotiented out. Verdict: C3 kept as a separate candidate only because its literature anchor (Yun–Zhang) is independent; its score (19) already reflects near-fatal status. B2 survives the collapse attempt.

## 6.3 D1 circularity
Quasirandomness of the EC log map is morally equivalent to ECDLP hardness, so D1 "assumes its conclusion." Acknowledged. D1's non-circular content: (i) the *reduction* — any relation boost ⇒ log-space GAP structure — is a theorem candidate independent of whether quasirandomness holds; (ii) toy audits can *find* anomalous bases (loophole) without proving quasirandomness. What D1 cannot do: prove the barrier at cryptographic sizes. It is priced accordingly (barrier candidate, not winner).

## 6.4 The A-group fails if relation finding is not the bottleneck
PO68/PO71 closures show linear algebra and descent dominate complete cost in the closed branches. A1/A3 only calibrate relation budgets; A2 only amortizes walks. If relation finding is not the bottleneck, all A-group value collapses to bookkeeping. Defense: A1/C2's census also certifies when relation finding *cannot* be improved (feeds D2), which redirects budget to the true bottleneck — archival value, not attack value. Attack value of A2 is directly gated by §9.1-style transfer, currently negative.

## 6.5 Cost-negative analysis of the three winners
- **A1**: census Õ(S·m·log²p) ≪ one rho run; cannot be cost-negative as a *measurement*. Attack content: zero until the §4-A1 gate is met. No hidden memory. Clean.
- **B2**: setup Õ(d²·p²) toy; the fatal term is P_lift (JKSST 2000 collapse). Complete cost = per-relation cost / P_lift ≫ rho unless the gate (α < 1/2 trend) is met. Expectation: cost-negative; the experiment's job is to *measure* the negativity precisely and archive it. No hidden advice/memory beyond the lattice (tiny).
- **C2**: census cheap; resolvent machinery only activates on discovery (never at toy scale expected). Cannot be silently cost-negative because the attack path does not exist until the gate is met.
All three: worst case is a scoped negative result with exact numbers — acceptable under AGENTS.md rules 5–6.

## 6.6 Disguised-repetition check against the novelty bar
- A1 is not "another post-hoc feature filter": it computes an a priori group-theoretic invariant (Chebotarev census), the opposite of post-hoc.
- B2 is not "another same-field isogeny neighbor" and not a Weil-descent variant: the lift goes to a *surface over F_p(t)*, not to a scalar extension; the ledger has zero elliptic-surface entries.
- C2 is not "another Semaev parameter sweep": parameters are untouched; the Galois group of the cover is a new object in-ledger (0 collisions for `monodromy`/`Galois group`/`wreath` in the census vocabulary grep).

# 7. (reserved)

# 8. Winner experiment contracts

Full contracts are files:
- `experiments/EXP-MONO-001/contract.md` — first command: `python3 experiments/EXP-MONO-001/mono_census.py --primes 101 211 431 --seed 20260718 --samples 30000 --window 4` (executed, §9.2)
- `experiments/EXP-XEDN-001/contract.md` — first command: `python3 experiments/EXP-XEDN-001/xedni_sections.py --p 101 --seed 20260718 --samples 200000` (executed, §9.3)
- `experiments/EXP-IMON-001/contract.md` — first command: `python3 experiments/EXP-IMON-001/imon_group.py --p 101 --seed 20260718 --samples 20000` (executed, §9.4)

Each contract states: objective, inputs, constraints, deliverables, budget, completion gate, controls, validity criteria, and the ledger-ID proposal.

# 9. Executed smoke results (2026-07-18, this session)

All four runs used only generated toy curves (ordinary, prime-order group, cofactor 1), fixed seeds, planted positive controls, and relabeled/uniform negative controls. Nothing below is evidence of attack capability; these are harness validations plus first measurements.

## 9.1 EXP-ISADV-001 (A2 probe) — `experiments/EXP-ISADV-001/smoke_results.json`
Classes of 6 prime-order curves per prime, samples=372, window W=8, seed 20260718. Controls pass (exit 0).
- p=101 (class order 109): within-curve transfer 0.180 (exact prediction 2W/n = 0.147); cross-curve transfer deltas vs baseline 0.079: {+0.018, +0.012, −0.031, −0.007, −0.009}.
- p=211 (order 199): within-curve 0.075 (pred. 0.080); deltas {+0.035, −0.003, −0.003, +0.013, −0.022}.
- p=431 (order 443): within-curve 0.038 (pred. 0.036); deltas {−0.008, +0.003, −0.010, −0.010, −0.008}.
**Reading:** within-curve advice behaves exactly as combinatorics predicts; cross-curve transfer is statistically indistinguishable from baseline at all three sizes. A2 weakened (phase-1 scoped negative on transfer).

## 9.2 EXP-MONO-001 (A1, phase 1) — `experiments/EXP-MONO-001/smoke_results.json`
Prime-order curves (orders 83, 199, 443) at p ∈ {101, 211, 431}, samples=30000, window=4, seed 20260718, runtime 0.285 s. Controls pass (exit 0): positive 1.0 everywhere; uniform and shuffled negatives match predictions within 0.001.
- Measured toy relation rates: 0.0408 / 0.0196 / 0.0087 vs exact toy predictions W/p = 0.0396 / 0.0190 / 0.0093 (deltas +0.0012 / +0.0007 / −0.0006, far inside Weil floors 0.199 / 0.138 / 0.096).
- Recorded artifact lesson: the naive independence prediction P(split)·W/n is *wrong* for this toy event (orbit membership implies split); the harness now carries both predictions, demonstrating it can distinguish prediction artifacts from signal. The substantive Chebotarev gate is phase 2 (m=3 Semaev census) — not yet run.

## 9.3 EXP-XEDN-001 (B2 harness) — `experiments/EXP-XEDN-001/smoke_results.json`
p=101, seed 20260718, runtime 1.6 s. Controls pass (exit 0).
- Constant-section census: 637/1296 surfaces (0.4915) vs prediction 0.5 (delta −0.008).
- Planted degree-2 section recovered exactly (unique section found on the planted surface).
- Scarcity measurement: 0 sections in 5760 random slots on 40 random surfaces; 0 squares in 200 000 random sextics (naive prediction ≈ 9.7·10⁻⁷/slot) — the xedni rarity obstruction is already visible at toy scale, consistent with JKSST 2000.
**Reading:** harness validated; the promotion gate (P_lift trend vs classical prediction over ≥3 sizes) is the full experiment, not this smoke.

## 9.4 EXP-IMON-001 (C2/D2 harness) — `experiments/EXP-IMON-001/smoke_results.json`
p=101, seed 20260718, runtime 162 s (brute-force quadratic-factor scan; optimization needed before larger sizes — recorded as a budget note).
- Curve cover (E: y²=x³+6x+9, order 83 prime): split rate 0.4059 vs S₂ Chebotarev 0.5, delta −0.094 within Weil floor 0.199 — consistent with quasirandomness (D2-ward). The coded joint-split census is deterministic given the marginal (recorded as a harness limitation; the nontrivial joint test requires the m=3 cover, phase 2).
- Positive control (product covers g₂·g₃, 400 samples): only block-respecting cycle types observed; flagged non-full ✓.
- Negative control (20 000 random deg-5 polynomials): 5-cycle rate 0.2034 (Chebotarev S₅: 0.2), 4+1 rate 0.2494 (0.25) — full-consistent ✓.
**Reading:** the census correctly separates full from non-full covers on controls; the curve cover shows no deviation beyond Weil error at this size.

# 10. Claim discipline

- All executed results are **toy-scale** (p ≤ 431) and labeled as such; per lab rule 7 they are not crypto-scale validation of anything.
- Correctness (controls passing) is separated from performance throughout; no candidate claims a measured exponent.
- A2's phase-1 null is a scoped negative on cross-curve advice transfer at toy scale with one advice policy — it closes exactly that scope, nothing more (lab rule 6).
- The monodromy novelty classifications (A1, C2, D2: POSSIBLY NOVEL) rest on a documented search (§2.10); they are not claims of global novelty. B1, C1, C3 remain NOVELTY-UNVERIFIED where marked.
- The two-sided design (A1/C2 vs D2; D1 barrier vs loophole probe; D3 barrier vs descent criterion) means every experiment archives a usable record on either outcome.
- Failed candidates are scoped negative results, not disproofs of the underlying mathematics.
