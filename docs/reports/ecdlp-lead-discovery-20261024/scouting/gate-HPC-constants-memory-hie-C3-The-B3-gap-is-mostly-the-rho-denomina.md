# Gate record: C3 (B3 gap is mostly the rho denominator)

Date: 2026-10-25. Read-only gates N1-N4. Raw --match outputs pasted verbatim below (limit 10).

## N1 run 1: lead_atlas --match "times-floor decomposition of the Table B prime gap into matched rho finite-size bias and IC growth"

```
   29  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   17  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   16  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   15  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   14  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   11  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   11  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   11  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   10  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```

## N1 run 2: lead_atlas --match "the prime index calculus gap to rho widens because the rho reference converges to its floor"

```
   19  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   18  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   17  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   16  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   15  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   15  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   13  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   13  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   13  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```

## N1 run 3: lead_atlas --match "Table B gap to matched rho widens from 5.47x to 13.5x; rho finite-size bias law; medium-tier prime rho bound"

```
   50  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   18  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   17  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   10  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   10  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   10  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    9  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    9  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    9  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    9  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
```

## N1 run 4: lead_atlas --match "distinguished point set-up amortisation matched rho calibration extrapolation of prime index calculus to cryptographic sizes"

```
   19  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   19  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   18  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   18  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   18  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
   17  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   16  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   16  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
   15  LEAD-ICB-koblitz-rho-reference               open_next_step     The matched Koblitz rho reference for binary IC rows: step pricing, signed-Frobenius canonicalisation, a 131-bit walk
   15  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
```

## N2 run: build_frontier_map --match "times-floor decomposition of the Table B prime gap into matched rho finite-size bias and IC growth"

```
KR-RHO-cd0049  score=16  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-a4dd54  score=11  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-1fcdbc  score=10  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-46d822  score=7  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=7  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-38be82  score=7  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
KR-RHO-ea34b8  score=7  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
```

## N2 run: build_frontier_map --match "the prime index calculus gap to rho widens because the rho reference converges to its floor"

```
KR-IC-a4dd54  score=19  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-5931ee  score=18  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-1c2928  score=17  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-9e610d  score=15  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-cd0049  score=13  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=12  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-46d822  score=9  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-ae532f  score=9  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-64659b  score=7  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-RHO-825bca  score=7  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
```

## N2 run: build_frontier_map --match "Table B gap to matched rho widens from 5.47x to 13.5x; rho finite-size bias law; medium-tier prime rho bound"

```
KR-RHO-cd0049  score=18  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-1c2928  score=9  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-ea34b8  score=9  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-9e610d  score=7  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-a4dd54  score=7  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-13bf67  score=7  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-38be82  score=7  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
KR-RHO-93979e  score=7  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
```

## N2 run: build_frontier_map --match "distinguished point set-up amortisation matched rho calibration extrapolation of prime index calculus to cryptographic sizes"

```
KR-IC-a4dd54  score=19  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-5931ee  score=18  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-1c2928  score=18  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-9e610d  score=16  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-1fcdbc  score=12  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-6654ba  score=12  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-cd0049  score=11  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-6239aa  score=10  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-ea34b8  score=10  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-46d822  score=9  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
```


## N1 reading of the top-5 hits (YAML opened: mechanism, obstruction, forecloses)

Opened and read: LEAD-RHO-matched-rho-calibration, LEAD-ICB-koblitz-rho-reference, LEAD-ICP-generic-table-decomposition, LEAD-ICE-rootfind-pairtable-oracle, LEAD-ICP-full-width-arity-grid, LEAD-ICE-charged-toy-ic-exponent-vs-rho (top-5 of runs 1-4), plus lower-ranked LEAD-ICB-generic-table-oracle, LEAD-ICE-generic-oracle-arity-cost-floor, LEAD-ICP-retained-setup-online, LEAD-ICB-multi-target-and-portfolio, LEAD-ICP-prime-ic-constant-engineering (the B3 lead itself), LEAD-RHO-negation-map-fruitless-cycles, LEAD-RHO-generic-sqrt-lower-bound. KR rows (KR-RHO-cd0049, KR-RHO-1c2928, KR-RHO-6239aa, KR-IC-5931ee) read in KRMAP.md.

### Same mechanism: LEAD-RHO-matched-rho-calibration (open_next_step, family generic)

Its mechanism text: "Toy rho bounds carry fixed set-up costs (fitted alpha 0.31-0.45 below 0.5), and the sealed frontier has a medium-tier domain for Koblitz curves only. A calibrated prime medium-tier rho bound would fix the denominator of every prime-field gap."
Its next_action: "fit R(N) = 1 + c/N^beta to the toy-to-medium ratio (H-ECDLP-ff38dc)"; discriminates: "If medium-tier rho.negation lands within 1.10x of sqrt(pi/4) the toy excess is set-up and every prime gap shrinks by the toy factor; a persistent 1.3-1.5x would point to a real walk shortfall (reopen LEAD-RHO-negation-map-fruitless-cycles)."
forecloses: "calibrate the charged rho baseline"; "rho finite-size bias law"; "medium-tier prime rho bound"; "coefficient of variation of matched rho".

Candidate C3 vs this lead, element by element:
- Fit form rho/floor = 1 + c N^-beta: identical to the lead's R(N) = 1 + c/N^beta.
- Threshold 1.10 for rho/floor: the candidate's "rho/floor 1.10 (28 bits)" and "<= 1.15" mirror the lead's "within 1.10x".
- "rho/floor > 1.3 at 32 bits: reopen LEAD-RHO-negation-map-fruitless-cycles": the lead's "persistent 1.3-1.5x ... reopen LEAD-RHO-negation-map-fruitless-cycles". Same disposition mapping.
- First step: the candidate's own words, "the prime medium-tier rho bounds that LEAD-RHO-matched-rho-calibration already specifies". Adopted, not new.
- "the gap shrinks by the toy factor" (lead) = "the gap is mostly the rho denominator" (candidate): same claim, same direction.
What the candidate adds that the lead's text does not state: (a) an IC-side factor IC/floor = (IC/rho) x (rho/floor), with a leave-one-out slope 0.138 (0.11-0.17) against the m=2 model's 1/6; (b) a fit already done on the 8 existing Table B reprice rows (beta 0.275, log2 c 4.32, sd 0.056) instead of waiting for the 32-48 bit ladder; (c) numerical IC/rho and IC/floor projections at 28 and 32 bits with three disposition branches; (d) sizes 28 and 32 bits (the lead asks 32-48).
The IC-side factorisation is an identity (IC/rho = IC/floor x floor/rho) applied to leaderboard numbers; its content is the fitted slope, which the lead's disposition rules do not forbid but also do not require.

### Other top-5 hits

- LEAD-ICP-generic-table-decomposition (closed_obstructed, SO-TABLE): the candidate is a re-attribution of the measured clause "Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4" inside this lead's obstruction. It does not touch the theorem part; it escapes no premise (candidate says so itself). Obstruction.statement, verbatim: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p." Its evidence already lists "native u64 enumeration PDP ... gap > 40x from 32 bits" (RESEARCH_PRIME_FAST_ECDLP.md) and "FRONTIER fitted exponent 0.841 [0.500, 1.024] for folded mitm m = 2": IC-side exponent fits exist at 12-32 bits.
- LEAD-ICP-prime-ic-constant-engineering (open_next_step, the B3 lead): next_action is to put the eight Table B prime rows through the validation gate (replay certificate, matched rho with the section 5a band, VALIDATION.json). Its best_measured and phase table are the inputs the candidate re-reads. The candidate's "seal fp26, fp28, fp32 rows" falls under this step plus LEAD-RHO-matched-rho-calibration; it adds no new engineering mechanism.
- LEAD-ICB-koblitz-rho-reference (open_next_step): same denominator-accounting theme for the Koblitz Table A ("Strengthening the reference is accounting, not an IC improvement, but it fixes the distance remaining"), where the correction runs the other way (the as-built rho is too slow, gap understated 1.67-1.96x). Different family (binary); not the same measurement; confirms the program already treats "fix the rho denominator" as a registered lead class.
- LEAD-ICE-rootfind-pairtable-oracle (open_blocked), LEAD-ICB-generic-table-oracle (closed_obstructed, "ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r", binary analogue of the IC-side slope), LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed), LEAD-ICP-full-width-arity-grid (open_blocked, "the distance to matched rho is known at the sizes the leaderboard extrapolates to"), LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked; "the four-size exponent unidentifiable and the 1/2 comparison mis-specified"): all generic-oracle or measurement-programme leads; none escaped, none is the same mechanism. LEAD-ICE-charged-toy-ic-exponent-vs-rho and IDEA-20260805-4d31bc (crossover order) cover the IC-vs-rho extrapolation-estimator theme.
- SO-GEN (LEAD-RHO-generic-sqrt-lower-bound, closed_obstructed). Obstruction.statement, verbatim: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." The candidate moves no exponent and no algorithm; not escaped.
- Other SO codes in the standing list are untouched by an instrument that proposes no placement.

### What the hits' forecloses phrases do NOT cover
The forecloses lists of LEAD-RHO-matched-rho-calibration do not name an IC-side slope, a per-size IC/floor series or a pre-registered IC/rho projection at 28 and 32 bits. That is the whole delta. It is a derived summary statistic plus a prediction, not a mechanism.

## Measured facts found while reading, which bear on the candidate (derived by this gate from recorded rows; read-only; script scout/hpc-r2/gate_c3_check.py, output gate_c3_check.out)

Source: research/ic_planner_validation_20261020/analysis/summary.json (crypto-main; PROTOCOL frozen before the sessions; 24 paired runs per curve; 12 of 256 records replayed per session and all reproduced, per its README), planner constants in src/cryptanalysis/ic_framework/planner.rs (PRIME_RHO_POINTS), docs/ic/LEADERBOARD.md ("Planner validation, outside tables A-C" and "Pair-table set-up" sections). These are not Table B rows and carry no VALIDATION.json; the unit is ecbench GAE at w = 0, Table B uses ledger GAE with calibration.json ratios (at 23.4-24.0 bits Table B reads 13.5x, the planner study 14.4x, so the unit offset is of the order 7 percent).

| curve | log2 r | measured S(plan)/S(rho.negation) [95%] | planner prediction | rho/floor (rho-neg S / 0.886) | candidate-fit rho/floor | derived IC/floor |
|:--|--:|:--|--:|--:|--:|--:|
| c24 | 23.47 | 12.56 [9.7, 16.5] | 11.5 | 1.181 | 1.228 | 14.83 |
| r24 (fp24) | 24.00 | 14.39 [11.6, 18.4] | 12.2 | 1.076 | 1.206 | 15.49 |
| r26 (fp26) | 25.35 | 14.56 [11.2, 19.6] | 14.5 | 1.180 | 1.159 | 17.18 |
| c28 | 27.69 | 21.85 [17.0, 29.8] | 19.3 | 1.045 | 1.102 | 22.83 |
| r28 (fp28) | 28.00 | 21.68 [17.0, 28.3] | 20.1 | 1.064 | 1.096 | 23.06 |
| c30 | 29.62 | 25.78 [19.9, 35.2] | 24.5 | 1.058 | 1.070 | 27.26 |

- The fp26 and fp28 registered curves, which the candidate lists as its "first step", have already been measured against rho.negation, 24 pairs each, on 2026-10-20 (not as Table B rows).
- 28-bit leg of the candidate's projection: candidate band IC/rho 23.2-24.5 (derive_b3.out) and 23-25 (tier text); measured 21.68 [17.0, 28.3] and 21.85 [17.0, 29.8]. The point estimates are below the band, the intervals contain it. Candidate IC/floor projection at 28 bits 25.4 (fit) / 26.9 (1/6 model); derived 23.06 is lower than both. The existing planner cost model (ic-planner/1, a two-point log-linear interpolation, PRIME_RHO_POINTS = (19.10, 6.6671), (32.0, 32.955)) predicted 20.1 and 19.3 at those sizes and was "within 18 percent" at all six; so an IC/rho extrapolation with a log-linear slope of 0.179 per log2 r between 19.1 and 32 bits already exists in the code and has been checked at six sizes.
- 32-bit leg: LEADERBOARD "Pair-table set-up" section and planner.rs E_BLOCKED32 record "smallest gap 33.0x rho at 1,024 abscissae" on icv1-fp32-t7319-90da43e9 (PRIME_RHO_POINTS carries 32.955). Candidate band 35.7-40.8 (derive_b3.out), "36-41" (tier text): 33.0 lies below it. IC/floor equals 33.0 times rho/floor, i.e. 33-36 for rho/floor in [1.00, 1.10], inside the candidate's pass window [30, 48]. The 33.0 comes from one session at one abscissa count (N = 1,024), which the README describes as target-pinned at about 0.5 relations per column; whether this is the family optimum is not established by what I read.
- IC-side slope: OLS slope of log2(derived IC/floor) on log2 r over the six rows is 0.146 per log2 r (23.5-29.6 bits). Candidate: 0.138 (leave-one-out 0.11-0.17) on four Table B rows from 18 bits. They agree. The IC-side slope claim is therefore corroborated by rows that exist, and the candidate did not cite them.
- rho-side: the six measured rho/floor values scatter 1.045-1.181 between 23.5 and 29.6 bits, as much as the candidate's predicted drop from 28 to 32 bits (1.096 to 1.045). A rho/floor test at 28 or 32 bits needs the 24-runs-per-size design (standard error of the order 0.027 per rung in H-ECDLP-ff38dc's accounting with sd(log T) = 0.6413 and 576 runs) and cannot be settled by single-session means. The candidate's fit exponent beta = 0.275 lies outside the band 0.30-0.70 that H-ECDLP-ff38dc (status proposed, never executed) pre-registers for the same law (its HEUR-001: R(N) = 1 + c N^(-1/2), falsified if the fitted exponent leaves 0.30-0.70 or the nested comparison prefers log N); the walk_over_own_floor column of the reprice ledger as printed in derive_b3.out (definition not checked here) reads 1.21-1.24 at 16-22 bits and 1.03 at 23.4, so part of the toy excess may not be set-up and a pure set-up law may not describe it.

## N2 Known results (build_frontier_map --match, four phrasings; raw output above)

- KR-RHO-6239aa (known_mechanism / proven), "Parallel collision search with distinguished points": this is the candidate's own external ingredient; its text already states "the DP density trades storage against the in-flight tail at collision time". Fixed set-up amortising against sqrt(r) is textbook and is a restatement of that row, not new.
- KR-RHO-cd0049 (known_bound / measured): negation-map BSGS at 1.160 [1.068, 1.248] x floor, fitted alpha 0.460 [0.377, 0.502], log2 r 17.70-23.97, prime. KR-RHO-1c2928 (known_bound / measured): Koblitz toy, "fixed-cost signature, not a law", "the reference set-up is 71 % of its total at these sizes" and "it says nothing about medium scale". Both are measured, program-internal statements that the toy excess over the floor is a fixed-cost effect; they cover rho variants other than prime rho.negation and do not decompose an IC gap.
- KR-IC-5931ee (known_negative / proven): naive Semaev IC over prime fields cannot beat generic methods; KR-IC-9e610d: no prime-field attack better than rho. Both are the exponent-level statements the candidate confirms and cannot move.
- No KR row states an IC/floor growth law for prime fields. No KR row is the IC-side decomposition. The attribution (IC/rho = IC/floor x floor/rho on Table B) is not a literature result; it is an identity applied to program data.
- Citation provenance: van Oorschot and Wiener, "Parallel Collision Search with Cryptanalytic Applications", J. Cryptology 12(1):1-28 (1999), DOI 10.1007/PL00003816: bibliographic existence and abstract content RETRIEVED this session (WebSearch, Springer record link.springer.com/doi/10.1007/PL00003816 and the author preprint on people.scs.carleton.ca); the specific reading "set-up and DP tail amortise as N^-beta against sqrt(r)" is RECALLED, taken from the KR-RHO-6239aa paraphrase, and I did not open the paper text to check the section.

## N3 Ledger (grep of ledger/.index/proposals.jsonl and hypotheses.jsonl; index claim fields are truncated, so a lexical miss proves nothing)

Terms tried: finite-size, medium tier, matched rho, rho/floor, set-up share/cost, R(N), Table B, distance to rho, denominator, IDEA-20260829-34f3ed, fixed set-up, toy rho, rho.negation, IC/rho, gap to rho, prime ladder, extrapolat. Scripts: scout/hpc-r2/gate_c3_ledger.py and gate_c3_ledger2.py. Most terms returned 0 hits (the index stores about 200 characters of claim text).
Hits that may be the same object:
- H-ECDLP-ff38dc (proposed): "No cell of this census is comparable to any other until the charged rho instrument's own finite-size bias is calibrated; the bias law is R(N) = 1 + c N^(-1/2) ..." SAME OBJECT on the rho side. Opened in full.
- IDEA-20260829-34f3ed (unverified): its source proposal ("THE GAP, STATED AS A FACT ABOUT THIS PROGRAM'S RECORDS"; RQ-ECDLP-165d4b declares bit_sizes 16-36 and five of six rows are empty). Not opened separately; content relayed in the hypothesis.
- H-ICEX-835c4f (proposed): "The program has no measured Pollard-rho baseline ... step-count constant c ... 0.8862 within 10 percent ... four-size toy ladder". Opened (first 60 lines). Measures the rho constant itself; no IC side.
- H-ECDLP-f3d2fd (proposed): "A charged measurement of the incumbent baseline, Pollard rho with distinguished points, on toy prime-order subgroups at 16, 20, 24 and 28 bits. NO NEW ALGORITHM". Not opened; header read in the index only.
- H-CRYPTO-a405d4 (proposed): coefficient of variation of the matched rho cost, cv = sqrt(4/pi - 1) = 0.5227; not the same object.
- IDEA-20260805-4d31bc (unverified, opened first 70 lines): "Report the crossover order, not the exponent"; an IC-vs-rho extrapolation estimator (Fieller set for log ell*), no rho finite-size bias and no times-floor factorisation. Adjacent instrument, not the same.
- IDEA-20260922-2e2a58 ("THE SCALAR CROSSOVER IS UNDER-DETERMINED") and H-BINSTD-a9d430 ("measurement instrument", what quantity an IC-vs-rho comparison reports): adjacent, binary side, not opened.
Decision on the 3 opened records: H-ECDLP-ff38dc is the same rho-side object with the same fit form; its bias law fixes beta = 1/2 and refuses extrapolation past 26 bits (N must be exactly known), the candidate fits beta freely and extrapolates to 28 and 32. IDEA-20260805-4d31bc and H-ICEX-835c4f are adjacent, not the same.

## N4 Notation change

Not applicable in the sense of the gate (the candidate is an instrument/derivation with no factor base, representation, quotient or coordinate). Stated anyway: (representation, operation set) pair = none; the objects are two scalar series (IC/floor and rho/floor) over log2 r. It is not a rigidity result in new notation and does not touch IDEA-20260806-c5d183, IDEA-20260901-863e36, KN-OPEN-020 or KN-FIND-ffe1df Theorem C; those were not re-opened because nothing in the candidate is a projection or algebraic factor base over F_p.

## Verdict (draft before advisor review)

advances_lead, lead = LEAD-RHO-matched-rho-calibration. Not new: the rho half is the lead's text and H-ECDLP-ff38dc's law; the IC half is an identity plus a slope that planner-validation rows (23.5-29.6 bits, derived slope 0.146) already corroborate; the fp26/fp28/fp32 sizes already have measured IC/rho on file (outside Table B, unvalidated by the gate).
