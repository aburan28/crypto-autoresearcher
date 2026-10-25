# Novelty gate N1-N4: C4, exact tree-like Res(⊕) (parity decision tree) optimum of UNSAT descended PDP instances

Field key: SAT/XOR solving and phase transitions of planted random systems; proof-complexity lower bounds ...
Gate run 2026-10-24. Read-only on every repository; this file and `scout/_c4_raw/` are the only things written.
Tools run from /Volumes/SSD990-2/crypto-autoresearcher with LEAD_ATLAS_CRYPTO / LEAD_ATLAS_CRYPTANALYSIS / LEAD_ATLAS_ECC_CHALLENGES exported.
Raw `--match` outputs below are pasted verbatim (default limit, 8 rows each). Status words: **retrieved** = I read the source text or
abstract in this session; **recalled** = from memory, not re-read; **derived** = arithmetic or a written argument in this session
(not a measurement); **predicted** = an expectation, not an outcome. Nothing here is a measurement of C4 itself.

## Verdict (one paragraph, details below)

**duplicate_of_lead**, lead = **LEAD-ICB-decomposition-encoding-and-sat** (closed_obstructed, obstruction.kind measured). The candidate's own
escape premise quotes that lead's obstruction sentence ("Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with
alpha ~ m ... while beating rho needs alpha < m/2 - 1") and offers to replace "every method measured" by an optimum over a proof-system class.
Same object (DPLL/XOR search on the descended PDP), same figure of merit (per-attempt UNSAT exponent alpha against the enumeration law).
The obstruction is not answered: the candidate's own H4' arithmetic says no outcome reaches alpha < m/2 - 1, so the lead's revisit_when can
never fire. Under the gate's strict rule (semantic match with a closed lead whose obstruction the candidate does not answer) this is a duplicate.
It is not "advances_lead": the open leads that carry the same question in their forecloses phrases (LEAD-ICE-sat-xor-pdp-oracle,
LEAD-ICP-icperf-binary-pdp-solver, LEAD-EXO-ml-learned-models) have next actions C4 does not run (conflict pricing; BRiAl column; toy
prime-order learnability control), so C4 is not their next step. It is not "new" (leaf test, solver-free exact instrument, reference law and
predicted outcome are in IDEA-20260926-b11cb1, -96c4f3, -3c7a91; the outcome equals the program's default oracle LEAD-ICE-rootfind-pairtable-oracle)
and not "known_result" (no KR row states a class optimum, though the p = 0.75 branch restates KR-IC-5765d2).

Residual increment, stated so it is not lost: the minimum over adaptive decision trees (Q1) and over F_2-linear splits (Q2, Q3) of the leaf count
of IDEA-20260926-b11cb1's ideal-XG node test. Route it as an extension of b11cb1 (which sits under the open LEAD-ICE-sat-xor-pdp-oracle), not as a
new lead, and only after fixing defects D1-D4 (section 6). It is a closure instrument with predicted gain 0.

## N1. Atlas collision: raw outputs of python3 tools/lead_atlas.py --match (runs 1-3 are the mandated match_phrasings; 4-6 are my own)

=== N1 lead_atlas --match [run 1]: optimal parity decision tree DPLL XOR branching lower bound point decomposition ===
```
   15  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   14  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   12  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   11  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
   10  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    9  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    9  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
```

=== N1 lead_atlas --match [run 2]: is there any branching rule for a SAT solver that beats brute force on point decomposition ===
```
   21  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   19  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   16  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   15  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   15  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   14  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
   12  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
   12  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
```

=== N1 lead_atlas --match [run 3]: every SAT or enumeration method has per-attempt UNSAT cost with alpha about m ===
```
    9  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    6  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    6  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    6  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    6  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    6  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
```

=== N1 lead_atlas --match [run 4]: tree-like resolution over linear equations Res(xor) proof complexity SAT solver ===
```
   14  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   13  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   10  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    9  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    5  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    5  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    4  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
```

=== N1 lead_atlas --match [run 5]: guess a subset of descended bits then Gauss elimination decides UNSAT: minimum number of guessed bits strong backdoor for Semaev system ===
```
   12  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   11  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    9  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    7  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    7  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    7  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    7  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

=== N1 lead_atlas --match [run 6]: learned or optimal split rule for CDCL branching lower bound on conflicts for descended Semaev S_3 ===
```
   10  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    7  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    7  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    7  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    7  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    6  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
```


### N1 reading (top 5 of every run opened: lead YAML mechanism + obstruction + forecloses)

YAMLs read in full: LEAD-ICP-icperf-binary-pdp-solver, LEAD-ICE-sat-xor-pdp-oracle, LEAD-ICB-decomposition-encoding-and-sat,
LEAD-EXO-ml-learned-models, LEAD-ICB-frobenius-search-symmetry, LEAD-ICB-kic-golden-base-exact-decomp, LEAD-ICB-generic-table-oracle,
LEAD-ICE-hybrid-guess-determine-l7, LEAD-ICE-descent-closure-degree-at-scale, LEAD-ICE-chained-semaev-dreg-vs-semiregular,
LEAD-ICP-icperf-writability-boundary; mechanism/obstruction/forecloses of LEAD-ICB-oakley-quintic-tower, LEAD-ICE-rootfind-pairtable-oracle,
LEAD-ICP-gfp5-rho-reference-audit, LEAD-ICE-boolean-f4-f5-f6-engines, LEAD-ICP-digit-presentation-solving-degree,
LEAD-ICE-first-fall-degree-assumptions, LEAD-ICE-semaev-chain-cost-model, LEAD-STR-class-representative-ic-selection.
KR rows read in KRMAP.md: KR-IC-5765d2, KR-IC-955fd6, KR-IC-e847d1, KR-IC-1fcdbc, KR-IC-f5c584.

| hit | disposition | what it covers | does C4 differ? |
|---|---|---|---|
| LEAD-ICP-icperf-binary-pdp-solver | open_next_step | Solver choice for the descended binary PDP. forecloses: "branching order versus structure effect in DPLL", "WDSat conflict law for descended Semaev systems". Next action is a BRiAl Groebner column with d_solv. Best measured: m=3 F4/F6/SAT slopes 0.53-0.58 vs MITM floor 0.207. | The QUESTION (does branching order matter) is already foreclosed by this lead's phrase; its next action is a different instrument. C4 would supply a solver-free answer for one leaf rule. Sharper sub-instrument, not the lead's next step. |
| LEAD-ICE-sat-xor-pdp-oracle | open_next_step | Native-XOR SAT oracle, honest pricing. forecloses "DPLL conflict law 2^(ml)/m!". Mechanism text already says: "a derived identity says the pdp CNF-XOR model is a complete enumerator of V^m mod S_m with no above-leaf pruning" (= IDEA-20260904-3c7a91). Ledger refs carry IDEA-20260926-b11cb1. Next action: calibrate ns per conflict and refit alpha(m) (H-SATIC-5c526c). Discriminator: "conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant". | Closest open lead. C4's H4 is the 'confirms SAT is enumeration at a constant' branch, stated as a class bound instead of a fitted slope. C4 does not run the lead's next action and does not price conflicts. |
| LEAD-ICB-decomposition-encoding-and-sat | closed_obstructed (measured) | obstruction.statement: "Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m ... while beating rho needs alpha < m/2 - 1". No Scope clause. revisit_when: "A solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3". forecloses "SAT or XOR solver for point decomposition beats rho". | C4 cannot meet revisit_when: its own H4' says that even a 2^-l win leaves alpha >= m-2 >= m/2-1. So the obstruction is NOT answered. C4 replaces "every method measured" by "optimum over a class" - a tightening of the same closure, not an escape. This is why the verdict is duplicate_of_lead against this closed lead. |
| LEAD-EXO-ml-learned-models | open_next_step | forecloses "learned SAT branching for point decomposition"; best_measured: learned WDSat branching 16,097 conflicts vs default 3,092 on 8 held-out targets (worse). Next action is a toy prime-order learnability control, unrelated to C4. | C4 would give any policy's conflict count a distance to an optimum (for the XG-leaf tree-like class). The lead's next action is not touched. |
| KR-IC-5765d2 | known_result | SAT/XOR reasoning for PDP (Trimoska-Ionica-Dequen 2020), measured, "without changing the exponent relative to rho". | C4's expected outcome (H4, p = 0.75) is this KR restated as a class bound. |
| KR-IC-955fd6 | known_result | symmetries/torsion speed up PDP. | not related to the proof-system question. |
| LEAD-ICB-oakley-quintic-tower | open_next_step | n = 5 Gaudry-Diem on F_{2^155}, SAT arm priced q^4. | lexical hit only (point decomposition). |
| LEAD-ICB-frobenius-search-symmetry | closed_obstructed (proof) | Frobenius is an equivariance, not a per-instance search symmetry; orbit CNF encodings cost >= 0.95x plain. | C4 is not a symmetry lever. Relevant only because a tree optimum under a Frobenius-symmetrised V would hit the same obstruction. |
| LEAD-ICB-kic-golden-base-exact-decomp | open_next_step | co-designed binary factor bases, SAT vs exact MITM; flat SAT / direct MITM wall 1.70x (SAT slower). | different object (factor-base design). |
| LEAD-ICE-rootfind-pairtable-oracle | open_blocked | the S_3 root in the last variable is x(R -/+ F_i): m = 2 decomposition is one batched inversion plus table probes, m = 3 is |F| lookups; "exact and complete like enumeration", default oracle in every Table A/B row, moves the constant, never the exponent. | This IS the (m-1)-fold enumeration with a linear last step, i.e. the strategy that gives C4's reference law 2^{(m-1)l}. C4's H4 therefore predicts that the best tree-like SAT policy equals an oracle the program already runs. |
| LEAD-ICB-generic-table-oracle (SO-TABLE) | closed_obstructed (theorem) | "Scope: all binary and Koblitz curves, one target, setup charged." | C4 is silent-from-outside (it reads descended coordinates) but constructs no oracle and, by H4, lands above the pair-table line (2^{ml/2} vs 2^{(m-1)l} for m >= 3). Not escaped in effect. |
| LEAD-ICE-hybrid-guess-determine-l7 | open_next_step | Fix k variables then close at degree 4 (MutantXL): k* <= 2 at (m,l) = (3,7), hybrid cost 1/116 to 1/3,400 of the degree-5 closure. | A policy with a higher-degree leaf test needs far fewer guessed bits than 2^{(m-1)l}: a direct counter-example to "one number bounds every branching policy" unless the number is indexed by leaf strength. C4 fixes the leaf test at degree 1. |
| LEAD-ICE-descent-closure-degree-at-scale, -chained-semaev-dreg-vs-semiregular, LEAD-ICP-icperf-writability-boundary, LEAD-ICE-boolean-f4-f5-f6-engines, LEAD-ICP-digit-presentation-solving-degree, LEAD-ICE-first-fall-degree-assumptions, LEAD-ICE-semaev-chain-cost-model, LEAD-STR-class-representative-ic-selection, LEAD-ICP-gfp5-rho-reference-audit | various | closure-degree / d_reg / writability / engines / prime-field digit / chain cost / class selection / rho audit. | lexical neighbours (descended system, point decomposition). None carries a proof-system or exact-tree object. |

What C4 does that the hits' forecloses phrases do not cover: an exact minimum-leaf computation over adaptive decision trees (Q1) and over
F_2-linear splits (Q2, Q3) under a stated leaf test. What it does not cover: any solver that uses a leaf test stronger than degree-1
linearisation (LEAD-ICE-hybrid-guess-determine-l7, IDEA-20260906-412391), DAG-like clause learning, or any priced quantity.

## N2. Known results: raw outputs of python3 tools/build_frontier_map.py --match (same six phrasings)

=== N2 build_frontier_map --match [run 1]: optimal parity decision tree DPLL XOR branching lower bound point decomposition ===
```
KR-IC-5765d2  score=15  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=10  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-8b9daa  score=8  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-ea34b8  score=7  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
```

=== N2 build_frontier_map --match [run 2]: is there any branching rule for a SAT solver that beats brute force on point decomposition ===
```
KR-IC-5765d2  score=19  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=10  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-8b9daa  score=8  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-a4dd54  score=7  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
```

=== N2 build_frontier_map --match [run 3]: every SAT or enumeration method has per-attempt UNSAT cost with alpha about m ===
```
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-18cc42  score=5  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-RHO-1c2928  score=5  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-825bca  score=5  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-e847d1  score=3  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-IC-955fd6  score=2  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-ae532f  score=2  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
```

=== N2 build_frontier_map --match [run 4]: tree-like resolution over linear equations Res(xor) proof complexity SAT solver ===
```
KR-IC-5765d2  score=14  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-73db3f  score=3  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-0d2021  score=2  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-5a43e5  score=2  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-b0fcda  score=1  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

=== N2 build_frontier_map --match [run 5]: guess a subset of descended bits then Gauss elimination decides UNSAT: minimum number of guessed bits strong backdoor for Semaev system ===
```
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-cd86f5  score=3  [known_mechanism/measured]  r-adding walks and the walk constant
    sources: KN-LIT-49d5cd, KN-LIT-3849b1, KN-LIT-a5c59c
```

=== N2 build_frontier_map --match [run 6]: learned or optimal split rule for CDCL branching lower bound on conflicts for descended Semaev S_3 ===
```
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-fbdb61  score=2  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-0d2021  score=1  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```


### N2 reading

Top rows for all four mandated/own phrasings: KR-IC-5765d2 (scores 15, 19, 6, 14). Other rows are lexical (KR-IC-955fd6, KR-IC-8b9daa,
KR-IC-1fcdbc, KR-IC-f5c584, KR-IC-e847d1, KR-RHO rows). KRMAP.md and ATLAS.md contain no occurrence of: proof complexity, Res(, resolution
(as a proof system), parity decision, Itsykson, tree-like, Prover, Delayer, backdoor, DPLL, branching (the single "branching" hit in ATLAS.md
is the LEAD-EXO-ml-learned-models row). So no KR row states a Res(⊕) or parity-decision-tree optimum for any algebraic-cryptanalysis system.

KR-IC-5765d2 (known_mechanism/measured) says SAT/XOR solving of PDP is faster than Magma F4 by up to 300x on the PDP step "without changing
the exponent relative to rho". C4's H4 outcome (optimum within [1/2, 2] of 2^{(m-1)l}, p = 0.75) is that sentence with a class bound
attached. So: the likely result is a known_result in content; the only part not already known is the class bound itself.

Literature check of the load-bearing citation (WebFetch / WebSearch available and used):
- Gryaznov, Ovcharov, Riazanov, arXiv 2404.08370: **retrieved** (arXiv abstract page fetched). Abstract: Res(⊕) is the proof system of
  Itsykson-Sokolov (clauses are disjunctions of F_2-linear equations); the paper characterises tree-like SIZE and SPACE of Res(⊕)
  refutations by combinatorial games, proves tree-like size lower bounds by Prover-Delayer games for a class of "extensible formulas"
  (pigeonhole, ordering principle, dense linear ordering principle), and gives a width-space relation. The abstract names no algebraic or
  cryptographic family, and I did not read the definition of "extensible". So the candidate's statement "they are the proof route if the toy
  optimum is to become a theorem" is conditional on the descended-PDP CNF being extensible or on a new game argument; neither is shown.
- Itsykson, Sokolov, "Resolution over linear equations modulo two", APAL 171(1), 102722 (2020): **retrieved** (abstract via search result).
  Tree-like Res(⊕) proofs correspond to DPLL with splits on arbitrary F_2-linear combinations of variables; exponential tree-like lower
  bounds; Res and tree-like Res(⊕) do not simulate each other. The MFCS 2014 preprint "Lower bounds for splittings by linear combinations"
  is **retrieved** at the same level (Tseitin and PHP-type formulas).
- Efremenko, Garlik, Itsykson, STOC 2024 (regular Res(⊕) lower bounds): still **recalled**, not re-read.
- Beame, Sun, "Extending CDCL to Disjunctions of Parity Equations", SAT 2026 (LIPIcs 10.4230/LIPIcs.SAT.2026.5; full version arXiv
  2605.15002): **retrieved** (abstract read from the PDF). CDCL(⊕) produces Res(⊕) proofs and polynomially simulates Res(⊕) given
  nondeterministic decisions and restarts; solver Xorcle. Relevance: it confirms that DAG-like CDCL(⊕) is not bounded by a tree-like
  optimum, and it gives a solver that branches on arbitrary parity equations, which is the natural comparator for Q3. The paper is not about
  algebraic-cryptanalysis instances as far as the abstract shows.
- Williams, Gomes, Selman (strong backdoors, 2003): **recalled**.
- Exact minimum-size decision tree by dynamic programming over subcubes is classical for ordinary trees (the search surfaced
  "totally optimal decision trees for Boolean functions" at snippet level; Hyafil-Rivest NP-completeness, **recalled**). Exact PDT
  complexity of small functions is known (Chistopolskaya-Podolskii, ECCC 2018/174: majority n - B(n) + 1, **retrieved** at snippet
  level). The technique is therefore not new; the application to a descended Semaev system with an XG leaf is, as far as this
  search shows. The search was one query per item and is not exhaustive: a lexical miss proves nothing.

N2 conclusion: not a KR hit on mechanism (no row states a class optimum), but the expected outcome coincides with KR-IC-5765d2.
Rating: known in content (p = 0.75 branch), unknown only in its class-bound form.

## N3. Ledger dedup (greps over ledger/.index/{proposals,hypotheses}.jsonl only)

Terms and hit counts (proposals / hypotheses, case-insensitive substring over the whole index row):
parity decision 0/0; "res(⊕" 0/0; "res(xor" 0/0; tree-like 0/0; itsykson 0/0; delayer 0/0; "split rule" 0/0; "proof complexity" 0/1
(H-ECDLP-29f047); ideal-xg 1/0; backdoor 2/0; dpll 5/3; branching 28/3; "conflict law" 0/2; "decision tree" 3/0 (unrelated: endo oracle
classes, FN-DSA sampler, IDEA-20260906-69b3fc); "(m-1)l" 2/0; "block-order" 1/0. No record uses the words Res(⊕), parity decision tree
or tree-like. The semantic cluster is nonetheless dense. Hits that may be the same object (id | status | first 100 chars of claim):

| id | status | claim (first 100 chars) |
|---|---|---|
| IDEA-20260926-b11cb1 | unverified | CEILING FIRST. No row moves. The law says XOR-Gaussian elimination inside a DPLL search on the desce |
| IDEA-20260904-96c4f3 | unverified | SCOPE: binary elliptic curves over F_{2^n}, n prime, factor base B = {(x,y) in E(F_{2^n}) : x in V}  |
| IDEA-20260904-3c7a91 | unverified | SCOPE: symmetrized S_{m+1} pdp over F_{2^n}, Weil-descended to F_2, in the CNF-XOR model of SRC-SATI |
| IDEA-20260904-e12b5a | unverified | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} descended to F_2, CNF-XOR model of SRC-SATIC-TRIMOSKA-20 |
| IDEA-20260904-b40e6d | unverified | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} Weil-descended to F_2 and its non-symmetrized counterpar |
| IDEA-20260904-7fd218 | unverified | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} descended to F_2, and the direct model of src/semaev_tre |
| IDEA-20260915-7ef636 | unverified | P3b and P6 of H-ICPERF-cc4847 are measured on objects that differ in TWO ways at once, and as measur |
| IDEA-20260915-eee7e4 | unverified | Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, and V = {deg x < l} the Trimoska factor-base su |
| IDEA-20260915-0d8e90 | adaptation | On the Trimoska S_4 Weil-descent instances with V = {deg x < l} and m = 3 factor-base points, WDSat  |
| IDEA-20261017-4b1672 | adaptation | For WDSat on Weil-descended Semaev systems over F_{2^n} (prime n 13..31, Koblitz and ordinary, V = p |
| IDEA-20260906-412391 | unverified | R3 representation at the decomposition/relation stage. Bounded-degree nonlinear consequences can red |
| IDEA-20260906-9f56ad | unverified | R3 representation at the decomposition/relation stage. On standalone binary pdp instances, a continu |
| IDEA-20260922-af7396 | unverified | Let E/F_{2^{5p}}: y^2 + xy = x^3 + b with b not in F_{2^p} (the Oakley shape; both RFC 2409 curves s |
| H-ICPERF-81de5c | specified | (L1, THE CONFLICT LAW.) On Weil-descended S_4 instances over V = {deg x < l} with m = 3 factor-base  |
| H-ICPERF-cc4847 | weakened | For the 60 shipped instances of SRC-ICPERF-TRIMOSKA-ECICB-2024 (cells (15,5), (17,6), (19,6); 10 S + |
| H-ICPERF-71a809 | analyzed | CLAIM (measurement / constant-factor mechanism; DX-04 survivor of DEC-20260928-63addc; NO ATTACK; NO |
| H-SATIC-5c526c | proposed | (From the IDEA-20261017-4b1672 claim.) For WDSat on Weil-descended Semaev systems over F_{2^n} (prim |
| H-ECDLP-29f047 | proposed | SCOPE: the frozen toy Semaev point-decomposition systems already used in this program's DREG lane, a |

One-line gloss of each (from the index title/mechanism, which I read; the first three were opened in full):
- **IDEA-20260926-b11cb1** (opened in full, proposed): "ideal-XG ceiling". Defines the node test "substitute fixed bits into the descended Boolean
  system, treat every remaining monomial as an unknown, Gaussian-eliminate; conflict iff 1 is in the row space" and the leaf count L_XG,
  "computable exactly by a rank simulation with no SAT solver". Proposition C: for every solver whose node refutation is a linear
  consequence of the restricted parity rows, L_real >= L_XG. Proposition L: L1 (m = 2) L_XG = 2^l exactly; L2 (chain) 2^{(m-1)l};
  L3 (direct S_{m+1}, m >= 3) 2^{(m-1)l + u*(n)}, u* = max{u : sum_{i<=m-1} C(u,i) <= n}. Fixed block core order. The candidate's
  "XG rule" is this node test word for word.
- **IDEA-20260904-96c4f3**: (m-1)-fold enumeration with a linear last-point membership test, 2^{(m-1)l}/(m-1)! group operations (C4's reference law).
- **IDEA-20260904-3c7a91** (opened in full, proposed): "no above-leaf pruning: the SAT solver is a complete enumerator of V^m modulo S_m";
  conflicts occur only within O(1) levels of leaf depth ml; Ceiling (C): "not reachable by better search"; B5: two solvers branching on the ml core
  variables report conflict counts within a few percent whatever their XOR module. Attached to LEAD-ICE-sat-xor-pdp-oracle's mechanism text.
- **IDEA-20260904-e12b5a**: GE is inert before depth (m-1)l on the CNF-XOR model; single collapse in the last block.
- **IDEA-20260915-7ef636** (opened, proposed): 2x2 {structured, random content} x {core-first, random order} plus planted-core null:
  "separate the branching-order effect from the structure effect". This is the origin of the ICPERF lead's forecloses phrase.
- **IDEA-20260915-0d8e90, H-ICPERF-81de5c**: exhaustive-core conflict law c * 2^{3l} on direct S_4 (specified, not an outcome).
- **IDEA-20261017-4b1672 / H-SATIC-5c526c** (proposed): alpha(m) of DPLL PDP at m in {3,4,5}; "does any cell reach alpha < m/2 - 1". C4 is the
  optimal-policy version of the same question.
- **IDEA-20260906-412391**: certified nonlinear-to-affine consequences before depth (m-1)l; a degree-D Macaulay pass per node (b11cb1 says
  ideal-XG is its D = input-degree case). This is the leaf-strength axis that C4 holds fixed.
- **IDEA-20260906-9f56ad**: DAG of residual fibres (shared decision graph), the DAG-like counterpart C4 excludes.
- **H-ECDLP-29f047** (proposed): polynomial-calculus degree instrument on prime-field Semaev toy systems, "adapted from proof complexity".
  Different proof system and field, but a precedent for a proof-complexity instrument in this program.
- H-ICPERF-cc4847 (weakened), H-ICPERF-71a809 (analyzed), IDEA-20260915-eee7e4, IDEA-20260904-b40e6d, -7fd218, IDEA-20260922-af7396:
  measurement-side neighbours (static order effect, E-membership per block, null ladder, two-axis attribution, chain affine in the new argument).

Opened in full (3 of 3): IDEA-20260926-b11cb1 (all), IDEA-20260915-7ef636 (first 75 lines), IDEA-20260904-3c7a91 (first 70 lines).

N3 decision. Same object? Partly. C4 = b11cb1's instrument (same node test, same exact solver-free leaf count, same toy regime) with the
fixed block order replaced by a minimum over adaptive trees (Q1), over F_2-linear splits (Q2, Q3), plus a planted positive control (b11cb1 has
a regression check at m = 2 and a chain check instead). b11cb1's Proposition C already holds node by node for any decision order, so it
bounds L_real(order) below by L_XG(order) for every fixed order; C4's extra number is min over orders and splits of L_XG. Overlap review
of b11cb1 itself says it grepped "Gaussian elimination", "XOR", "linearis" and did not find a Res(⊕) or tree-optimum record, consistent with
my grep. Verdict for N3: not a duplicate record; an extension of an un-run proposal (b11cb1, status proposed, no run found in the index).

Later grep on the id "b11cb1" across all three indices (hypotheses, experiments, proposals) found three more rows:
- **H-SATIC-b1ff02** (approved) and **EXP-SATIC-11e236** (approved), "Free-bit cutoff arithmetic": checks b11cb1's degree-2 monomial bound
  1 + u + C(u,2) on the written field degrees; the hypothesis text states "It does not run a rank simulation and it does not run a solve".
  So the b11cb1 rank simulation, i.e. the instrument that C4 generalises, is specified/approved only at the arithmetic level and has not been run
  (as far as the index shows; I did not open the experiment's amendments directory).
- **IDEA-20260930-b26bbc** (proposed, unverified), index claim: "OUTCOME CLASS (a), A SEARCH EXPONENT, with the escape from the SATIC ceiling
  named: the ceiling ml - log2|G| of IDEA-20260904-3c7a91 and the enumeration law (m-1) l of IDEA-20260904-96c4f3 ..." and title "the certified
  m = 2 object as the inner theory of a CDCL(T)-style decomposition search: enumerate m - 2 legs by group arithmetic, decide the residual two-leg
  instance ...". I read only the index row, not the record. Consequence: the ledger already holds a proposal that claims to go below the (m-1)l law
  by changing the LEAF test (a certified m = 2 decider) rather than the split rule. C4's class (degree-1 XG leaf) does not contain that policy, which
  is the same point as LEAD-ICE-hybrid-guess-determine-l7 and IDEA-20260906-412391: the number C4 computes is indexed by leaf strength.
- Neighbouring measured datum in crypto-main (not a ledger hit): research/hamming_ideal_pdp_20260930/RESULT.md measures the depth at which a Groebner
  oracle resolves (mean tame depth 7.4-10.4 of 13 coordinates at n = 13) for a weight-constrained factor base: a different V, same "how deep must
  you branch" question, measured rather than bounded.

## N4. Notation check (C4 is a representation/operation-set candidate)

**Pair as the candidate states it.** R1: Weil-descended bits of x in an F_2-subspace V (V = {deg x < l} in the polynomial basis, the Trimoska
factor base). Sigma: restriction by F_2-affine parity queries on those bits, with the Gauss-XOR leaf rule (node closed iff the constant 1 lies in
the F_2-span of the restricted equations, monomials collapsed by multilinear reduction). Tracked object: the restricted system at a node (its
span / rank), and the minimum leaf count over trees. This is the object of IDEA-20260926-b11cb1 ("linearisation state of the RESTRICTED algebraic
system at a node"), with the order freed.

**Is it a recorded rigidity result in new notation?** No, for these reasons.
1. IDEA-20260806-c5d183 (prime-order group: a projection that propagates under the FULL translation action is constant or injective) concerns
   lossy projections of a group element. C4 tracks no projection of the target point. Sigma is restriction of the unknown coordinates of a
   decomposition, not translation of the target. The relation vector is untouched (b11cb1 says the same: "Class I"). Sigma does not contain the
   full translation action, so the constraint block's first clause is satisfied.
2. IDEA-20260901-863e36 (propagation = projection paired with an operation set; block systems of <Sigma>): C4's "projection" (node -> rank/closure
   flag) is a function of the assignment, and the quantity of interest (minimum leaves) is a property of the system, not of a block system on a
   prime-order subgroup. Nothing in 863e36 speaks to F_2-affine restriction of unknowns.
3. KN-FIND-ffe1df Theorem C (exactly sum-compatible bucket index on E(F_p) is a surjective homomorphism, impossible for prime N): about bucket
   indices for Wagner-style k-trees over a prime-order group; C4 has no group-valued index. Unrelated.
4. KN-OPEN-020 (bounded-degree algebraic factor bases over generic prime-field subgroups are scoped out; open class = high-degree, implicit,
   target-dependent): C4 is binary, not prime-field, so the scoped-out result does not literally apply. But the constraint block asks every candidate
   with a factor base to name its KN-OPEN-020 class or declare itself inside the scoped-out class and stop. V = {deg x < l} has linear (degree-1)
   membership, which is a bounded-degree description. C4 carries no such declaration; b11cb1 did ("V = {deg < l} inside KN-OPEN-020's scoped-out
   class; nothing escapes it"). Same declaration applies here, and with it the F2 off-limits-lens flag (factor-base decomposition is the lens).
5. Closed rigidity neighbours in the atlas do apply to the SAT lane: Proposition B in LEAD-ICB-decomposition-encoding-and-sat ("closure outcomes
   are basis-invariant") means Q3 (all affine subspaces) cannot depend on the basis of V, so basis/reduction-polynomial choice cannot be a lever
   there; Q1 and Q2 are basis-dependent by construction and are the only families where it could matter.

**Trichotomy label.** The candidate says "partial-action: a Class I relation object". b11cb1 labels the same object "COORDINATE-DEPENDENT ... and
BRANCHING under re-targeting". The instrument's value in Q1/Q2 depends on the descended-bit coordinates; only Q3 is coordinate-free. The label
should read coordinate-dependent for Q1/Q2, with partial-action applying to the relation search around it, not to the instrument.

**N4 result.** Not a recorded rigidity result in new notation. It is a refinement of b11cb1's object (order freed, linear splits added), inside
the scoped-out factor-base class, and the pair adds no escape from SO-TABLE / SO-GEN: it constructs no oracle and, by its own H4, lands above the
pair-table line.

## 5. Standing obstructions touched, quoted in full (obstruction.statement from the lead YAMLs, read this session)

- **LEAD-ICB-decomposition-encoding-and-sat** (closed_obstructed, kind measured; no Scope clause): "Every SAT or enumeration method measured has
  per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l =
  3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. Ladders
  n = 11..31: no arm grows slower than the enumeration floor (m = 3 slopes 0.53-0.58 vs floor 0.21; m = 4 wide chain 0.805 vs 0.333). Encoding
  levers are constants: S_m symmetrisation saturates product spaces at m >= 5 at balanced l (H-BINSTD-770ec3 supported), closure outcomes are
  basis-invariant (Proposition B), reduction-polynomial weight is a constant confound, Nagao coset yield weakened vs chained S_3, trace replay is a
  constant at most." revisit_when: "A solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3 (then it becomes
  LEAD-ICB-prime-degree-algebraic-decomposition)." C4 does not answer it: H4' caps the best case at alpha >= m-2 >= m/2-1. C4's Q2 (pairwise XOR
  splits, the splits symmetric coordinates would use) falls under "encoding levers are constants" and Q3 under "closure outcomes are basis-invariant".
- **SO-TABLE, LEAD-ICB-generic-table-oracle** (closed_obstructed, kind theorem): "Every oracle built from group operations and membership tests makes
  IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or
  6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27
  above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools
  (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup
  charged." The escaped premise is "built from group operations and membership tests". C4 reads descended coordinates, so the theorem is silent on
  it, but C4 constructs no oracle and by its own H4 lands at 2^{(m-1)l}, above the pair-table line 2^{ml/2} for m >= 3. revisit_when of that lead
  points to an oracle with "algebraic restriction on the unknowns with membership degree far below |F|"; V = {deg x < l} has degree-1 membership,
  and the measured SAT ladders in the lead above are exactly that case.
- **SO-GEN, LEAD-RHO-generic-sqrt-lower-bound** (closed_obstructed, kind theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm
  needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism
  classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." revisit_when: "Never for generic algorithms;
  only a method that reads the representation (index calculus, transfer) can change the exponent." C4 reads the representation, so the premise
  "generic" is escaped in form; C4 itself claims no exponent change, so nothing is gained from the escape.

## 6. Defects of the candidate as written (strictness items; each changes what C4 can claim)

D1. **Q3 never runs on a declared cell.** Declared cells: m = 2, l in {5,6,7} gives N = ml = 10, 12, 14; m = 3, l in {3,4,5} gives N = 9, 12, 15.
    Q3 is specified "at N <= 8". Every declared cell has N >= 9. So the only family that is basis-free and covers all F_2-linear forms is not
    evaluated anywhere the grid says it will be (derived arithmetic). The title's "one number that bounds every branching policy" then holds, at
    most, for Q1 (single bits) and Q2 (the sparse XOR families), not for "all linear splits". Fix: Q3 on m = 2, l <= 4 (outside the grid) or shrink n.
    Also, Q2's state space is not the 3^N subcube lattice (states are affine subspaces generated by XOR queries), so the stated "3^N, N <= 15" cost
    bound applies to Q1 only.
D2. **The reference law is the wrong comparator for the direct model.** b11cb1 Proposition L: 2^{(m-1)l} is the exact ideal-XG leaf count only for
    m = 2 and for chained presentations (L1, L2). For direct S_{m+1} at m = 3 it predicts 2^{(m-1)l + u*(n)}, u*(n) = max{u : 1 + u + C(u,2) <= n}.
    On the candidate's m = 3 cells (n = 8..16) integer arithmetic gives u* = 3,3,3 (l = 3), 4,4,4 (l = 4), 4,4,5 (l = 5), i.e. 2^{u*} = 8 to 32, as
    large as 2^l itself. If b11cb1's generic step holds (its H1, conditional), H4 "within [1/2, 2] of 2^{(m-1)l}" fails on the direct model for a
    reason already in the ledger, and the m = 3 cells sit at the 2^{ml} end (no gain from XG). The candidate does not say whether it uses chained
    or direct S_{m+1}. It must, because H4 is a different statement in each.
D3. **"Tree-like Res(⊕)" is not the class computed.** The computed class is parity decision trees whose queries are F_2-linear forms in the
    descended bits and whose leaves close by "1 in the span of the restricted equations" (function-span test, degree-1 linearisation). Res(⊕)
    leaves are falsified linear clauses of a CNF over all variables (including auxiliary monomial / AND-gate variables). The Itsykson-Sokolov
    equivalence (tree-like Res(⊕) = DPLL splitting on linear forms, **retrieved**) and the Gryaznov-Ovcharov-Riazanov games apply to that CNF class.
    The equivalence between the two classes is not shown, so neither the label nor the "proof route to a theorem" is established. And DAG-like
    CDCL(⊕) (Beame-Sun 2026, **retrieved**) p-simulates Res(⊕) given nondeterministic decisions and restarts, so the tree-like number does not bound
    CDCL+XOR conflict counts, which are the quantities in LEAD-EXO-ml-learned-models (16,097 vs 3,092) and LEAD-ICE-sat-xor-pdp-oracle.
D4. **The number is indexed by leaf strength.** LEAD-ICE-hybrid-guess-determine-l7 (k* <= 2 fixed variables at degree-4 closure, (m,l) = (3,7), vs
    (m-1)l = 14) and IDEA-20260930-b26bbc (certified m = 2 decider as leaf) are policies whose leaf test is stronger than degree-1 linearisation.
    A degree-1-leaf optimum does not bound them. "Bounds every branching policy" should read "bounds every branching policy under the degree-1 XG leaf".
D5. (minor) H4': a ratio of 2^{-l} at one cell is not a slope; "alpha >= m-2 per unit l" needs the ratio to persist across l, which three l values
    per m only roughly test. And H4 (p = 0.75) is, with the u* correction, close to a restatement of recorded predictions (b11cb1 L1-L3,
    3c7a91 ceiling), so the expected information gain over the ledger is concentrated in the p = 0.1 branch.

## 7. Verdict reasoning

- **duplicate_of_lead (LEAD-ICB-decomposition-encoding-and-sat).** Semantic match on object and figure of merit; the lead is closed on a
  measured obstruction (section 5) that C4 explicitly targets and cannot answer, because C4's own H4' arithmetic caps its best case at
  alpha >= m-2 >= m/2-1. The gate's strict rule is about a semantic match, not an identical mechanism, so the bounding-versus-solving difference
  does not change the label: C4 tightens the closure inside a class, it does not reopen the lead.
- Not **advances_lead.** That label needs a sharper next step for an OPEN lead. The open leads that carry the question in their forecloses phrases
  ("branching order versus structure effect in DPLL"; "DPLL conflict law 2^(ml)/m!"; "learned SAT branching for point decomposition") have next
  actions that C4 does not run (BRiAl column with d_solv; ns-per-conflict calibration and alpha(m) refit; toy prime-order learnability control).
- Not **new:** node test, solver-free exact leaf count, reference law and predicted outcome are in IDEA-20260926-b11cb1, IDEA-20260904-96c4f3,
  IDEA-20260904-3c7a91; the oracle realising the reference law is the program's default (LEAD-ICE-rootfind-pairtable-oracle); the b11cb1
  arithmetic is already an approved experiment (EXP-SATIC-11e236 / H-SATIC-b1ff02).
- Not **known_result:** no KR row states a Res(⊕)/PDT optimum (N2), though the p = 0.75 outcome restates KR-IC-5765d2.
- **Residual increment (kept for the record).** Minimum over adaptive trees and F_2-linear splits of b11cb1's ideal-XG leaf count, with a planted
  positive control. Route it as an extension of IDEA-20260926-b11cb1 under the open LEAD-ICE-sat-xor-pdp-oracle, after fixing D1-D4: run b11cb1's
  rank simulation first at m = 2 and on the chain, where L1 and L2 are exact. If H4 held, the tree-like XG-leaf sub-question would move toward
  exhausted_at_scale (Q1, N <= 15); LEAD-ICB-decomposition-encoding-and-sat would stay closed_obstructed; DAG-like CDCL(⊕) and stronger leaf tests
  (LEAD-ICE-hybrid-guess-determine-l7, IDEA-20260906-412391, IDEA-20260930-b26bbc) would stay open.
- Not a rho-crossing lead; SO-TABLE and SO-GEN are not escaped in effect. Heuristics used: none beyond those stated (the u* correction in D2 is
  conditional on b11cb1's own generic-step heuristic H1).
