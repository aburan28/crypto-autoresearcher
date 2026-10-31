# Novelty gate N1-N4: C4 [MERGE into scout-lattice-smallroot C1] unconditional strong-Groebner corner ceiling (prime field, B1)

Date 2026-10-25. Gate run by a scout subagent. Claim tier of everything below: analysis and toy check. No speedup is claimed. Repository-write check (run at 00:07 on 2026-10-25 with `find -newer` against my first raw output _c4gate_raw/atlas1.txt, 23:52): under /Volumes/SSD990-2/crypto-autoresearcher, excluding ledger/.index (other sessions update it), the only entry newer than my first output is the directory mtime of .git/worktrees/icperf-prime63-postrun-20261019 (00:07:51; every file inside it is dated Oct 19). I ran no git command and attribute it to another session, but I cannot prove that. tools/__pycache__ is dated Oct 24 22:35, before my first command. One Sage invocation was made once (`sage _c4gate_sgb.sage` from the scout directory): it failed at startup with PermissionError on a cache file. Its launcher /Volumes/SSD990/cryptanalysis/sage sets TMPDIR and DOT_SAGE under /Volumes/SSD990/cryptanalysis/.sage-build-tmp (a symlink to /private/tmp/cryptanalysis-sage-build-cache-20261019) and runs mkdir -p and runtime_check.py there. I checked afterwards: nothing under /Volumes/SSD990/cryptanalysis (depth 3, excluding third_party and .git) and nothing under the symlink target is newer than that attempt or than atlas1.txt. I did not retry Sage. All scratch files are under the scout directory (the `_c4gate_*` files). Env LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as instructed. Predictions are labelled as predictions; "derived" means by hand in this gate, "computed" means a script output pasted below.

## 0. Verdict (details in sections 1-8)

**advances_lead.** Lead: LEAD-ICP-coppersmith-smallroot-semaev (open_next_step). It is also, by the candidate's own label, a duplicate of the sibling scout's C1 (corner lemma); the sibling's gate file for C1 (gate-lattice-reduction-and-sm-C1-...md) reached the same verdict, and I agree with it. What C4 adds to C1 is narrow and is an epistemic upgrade, not a new ceiling:

- The ceiling D * log_p(vol) < 1 is the sibling's C1 ceiling, unchanged.
- C4 supplies an H1-free (non-Gaussian-heuristic) proof route for the sub-case where ONE corner monomial has weight >= 1: then (p,f)^t contains no nonzero polynomial g with ||g(Xx)||_inf < p^t, so there is nothing for any HG-type lattice to find (strong Groebner basis over Z_(p); proof in section 5.1). That answers the sibling's own scope item 1 ("unconditional version would extend capacity theory") for the single-corner cells (all w = 0 rank-1 boxes, GAP rank up to a bound corrected in 5.3, and each block of the (4,2) tree under CLOSURE's demand, 5.6).
- It is strictly WEAKER than the sibling's order-averaged determinant lemma wherever several corners compete (rank-r GAP beyond the bound, 3-unknown S_3 blocks): section 5.2.
- At the lead's discriminating cell (m,w) = (4,2) it decides CLOSURE.md's per-block construction rigorously, and by a wide margin (section 5.6): under CLOSURE's own demand (I)+(II), the root block S_3(y1,y2;x_R) has a unit corner of weight > 7/2 and each leaf block a unit corner of weight > 11/6, all >= 1. It also shows the recorded supply 0.8408 for the 3-unknown S_3 block is not attainable by any shift set inside (p,S_3)^t when epsilon is read in CLOSURE's stated sum-of-exponents convention (block volume < 3/4). What stays open at (4,2) is only a genuinely joint lattice over (p, f1, f2, f3)^t (sibling C2, or the joint arm of IDEA-20260904-39336c). So the lead stays open_next_step. No KR row covers it (KRMAP has no Coppersmith or lattice row). No ledger record states it; the nearest, IDEA-20260904-39336c, asserts the opposite premise (slack to the information ceiling, F1) for cells the lemma bounds.
- Recommendation: do not file as an independent candidate. Fold into C1 as a corollary "C1-U (rigorous single-corner form)" and fix the two misstatements in 5.3 and 5.4 before it is scored.

## 1. N1 raw output: python3 tools/lead_atlas.py --match (3 match_phrasings + 1 of my own)

### lead_atlas run 1: strong Groebner basis of (p,f)^t: no lattice polynomial is short once the corner monomial of the summation polynomial exceeds p on the box
```
   13  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
   10  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    8  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    8  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    8  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    8  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    7  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
```

### lead_atlas run 2: no Coppersmith lattice built from the modulus and the summation polynomial can find small decompositions
```
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   10  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    9  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    7  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    7  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
```

### lead_atlas run 3: small-root Coppersmith Jochemsz-May decomposition with lattice-describable window AP GAP factor bases reach below demand
```
   32  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   13  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   12  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   11  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   11  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```

### lead_atlas run 4: (own) strong Groebner basis over Z leading coefficient valuation tropical Newton polytope ideal power (p,f)^t short polynomial Howgrave-Graham
```
   10  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   10  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    8  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    6  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    6  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    5  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    5  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
```

### N1 reading notes (top 5 hits of every run; YAML mechanism + obstruction + forecloses read)

| hit | disposition | same mechanism? | what C4 does that its forecloses phrases do not cover |
|---|---|---|---|
| LEAD-ICP-coppersmith-smallroot-semaev (top-1 in runs 2 and 3; rank 7 of 8 in run 1; not in the printed top 8 of run 4; YAML read) | open_next_step | **Same family.** Its forecloses list "Coppersmith small roots of summation polynomials", "small-x factor base solved by LLL", "windowed addition tree with lattice reduction", "rank-r generalized arithmetic progression factor base", "lattice-assisted meet-in-the-middle decomposition". The lead is OPEN: its next_action asks for the provably optimal shift set (Ryan EUROCRYPT 2025) and says "optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one". | C4 is a zero-compute, rigorous, strategy-independent ceiling for the single-corner cells. That is a sharper next step for the w = 0 part of the lead's discriminator, hence **advances_lead**. It says nothing for (4,2): the lead's best_measured margin -0.0481 is a w = 2 cell, outside C4's claim by its own text. |
| LEAD-ICP-lattice-ic-relation-construction (run 2) | open_blocked | No. Ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors. Its forecloses include "Newton shift certificates for small-window decompositions", which is the same lattice shape, but the lead is blocked on a certified pipeline that does not exist. | C4 bounds what any shift-lattice (including "Newton shift" ones built on the ideal (p,f)^t) can find for a single S_{m+1}; it does not address the ideal/quaternion lattices. The sibling lists the polynomial lane (IDEA-20261015-9defe9) as covered; I did not open that record. |
| LEAD-ICE-boolean-f4-f5-f6-engines (run 1, 4) | closed_dominated | No. Boolean Groebner engines on the Weil-descended chain. Shares only the word "Groebner". C4's Groebner basis is over Z for the ideal power (p,f)^t, used as a proof device, not a solver. | Different object. |
| LEAD-ICB-decomposition-encoding-and-sat (run 1, 4) | closed_obstructed | No. SAT/XOR/enumeration encodings for binary PDP; obstruction is the 2^(alpha l) UNSAT cost with alpha ~ m. | Different field (char 2) and solver class. The sibling's C3 is the function-field analogue; C4 does not claim it. |
| LEAD-ICB-kic-golden-base-exact-decomp, LEAD-ICP-coincidence-harvest-structured-base, LEAD-ICB-frobenius-orbit-factor-base, LEAD-ICB-factor-base-subspace-choice, LEAD-ICE-prime-field-semaev-solving-degree (run 3, 4 and read for SO checks) | open / closed | No. Structured-base design, coincidence harvesting, Frobenius orbits, subspace choice, and Groebner solving degree. None uses an integer-size (archimedean) box or HG lattices. | Not covered; not overlapped. The solving-degree row (KR-IC-5931ee, beta_work 0.797 / 0.647 vs 0.30) is the algebraic-solver counterpart that C4's lattice-solver ceiling complements; it does not state a lattice ceiling. |
| KR-IC-5a43e5, KR-IC-5931ee, KR-IC-1fcdbc, KR-IC-73db3f, KR-IC-955fd6, KR-IC-fbdb61, KR-IC-b0fcda (KRMAP rows, runs 1-3) | known_* | No. Summation polynomials as framework, naive prime-field IC cannot beat generic, char-2 summation slower than rho, small product spaces, symmetries, last fall degree, Frobenius bases. | None mentions Coppersmith, Howgrave-Graham or lattice reach (`grep -i -E "coppersmith|howgrave|lattice|small-root|jochemsz"` on KRMAP.md returned no line). |

### Standing obstructions: quoted obstruction.statement (Scope clause included) and how C4 stands

C4 proposes a closure, not an escape. The candidate's `escape_premises` field claims the lattice "escapes" SO-TABLE/SO-ALGFB/SO-GEN; the lemma then shuts that escape for single-corner cells. The quotes, from the lead YAMLs:

- SO-TABLE, LEAD-ICP-generic-table-decomposition: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p." A lattice oracle reads integer sizes, so it is not an enumeration or table. The premise is escaped. Escape is of no use for the cells C4 closes.
- SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base: "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B." An interval or AP box is not a low-degree algebraic locus, so the locus premise is escaped (KN-OPEN-020's implicit-membership class). The yield-conservation clause is NOT escaped and C4 does not try to: the lemma bounds oracle success, not yield.
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." The method reads the representation, so it is non-generic; premise escaped, irrelevant to the closure.
- Lead row for B2 context, LEAD-ICE-prime-field-semaev-solving-degree (closed_known): "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). ... beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold". C4 is an additional, solver-class-specific ceiling for the lattice branch; it adds no sub-rho path.

## 2. N2 raw output: python3 tools/build_frontier_map.py --match (same 4 phrasings)

### build_frontier_map run 1: strong Groebner basis of (p,f)^t: no lattice polynomial is short once the corner monomial of the summation polynomial exceeds p on the box
```
KR-IC-5a43e5  score=9  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-fbdb61  score=7  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
```

### build_frontier_map run 2: no Coppersmith lattice built from the modulus and the summation polynomial can find small decompositions
```
KR-IC-5931ee  score=10  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-1fcdbc  score=9  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5a43e5  score=9  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=7  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-fbdb61  score=7  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-53c89f  score=5  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
```

### build_frontier_map run 3: small-root Coppersmith Jochemsz-May decomposition with lattice-describable window AP GAP factor bases reach below demand
```
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=5  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-5931ee  score=5  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
```

### build_frontier_map run 4: (own) strong Groebner basis over Z leading coefficient valuation tropical Newton polytope ideal power (p,f)^t short polynomial Howgrave-Graham
```
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-1fcdbc  score=3  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5a43e5  score=3  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
```

N2 reading: 16 distinct KR rows appear across the four runs (KR-IC-5a43e5, -5931ee, -1fcdbc, -73db3f, -955fd6, -fbdb61, -889857, -b0fcda, -8b9daa, -46d822, -081a58, -5765d2, -f5c584, -49c882; KR-RHO-1c2928, KR-RHO-53c89f). None states a lattice or small-root ceiling; their scores come from the words "summation polynomial", "Semaev", "Groebner", "factor base". KR-IC-5931ee is the nearest in spirit (prime-field Semaev IC cannot beat generic, algebraic bases only at small parameters) but concerns Groebner/statistical models, not HG lattices. So no KR row is "known_result" for C4. That is "not found in the map", not "absent from the literature" (section 6 lists literature-adjacent work).

## 3. N3 ledger grep (grep only; /Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl; helper `_c4gate_ledger.py` matches title|claim|mechanism|statement|id, case-insensitive)

Terms used (22): coppersmith, howgrave, jochemsz, small-root, smallroot, "groebner basis over z", "strong gr", corner, "initial ideal", "leading monomial", "leading coefficient", "leading-monomial", "newton polytope", "ideal power", tropical, valuation, gröbner, "determinant criterion", unconditional, "lattice reach", "reach ceiling", "p-adic".

### Raw grep output, batch 1
```
######## TERM: coppersmith
## proposals.jsonl
IDEA-20260807-0f49b6	[proposed]	coppersmith	KN-OPEN-018 states the lattice/ECDLP boundary precisely: lattice reduction enters ECDLP work only vi
IDEA-20260808-e2315e	[proposed]	coppersmith	Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia
IDEA-20260816-b4e5b7	[proposed]	coppersmith	(A) The quantity this program actually needs from Coppersmith-style partial-information recovery is 
IDEA-20260816-b5b822	[proposed]	coppersmith	(A) A Coppersmith-style small-root pipeline is a composition of five separable stages, and the progr
IDEA-20260901-cc08db	[proposed]	coppersmith	FIVE SEPARABLE CLAIMS, ALL ABOUT COST MODELS. (A) THE OBJECT. For a balanced n-bit modulus with p of
IDEA-20261009-85062c	[proposed]	coppersmith	The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
IDEA-20261017-2f80c9	[proposed]	coppersmith	p=m^d-c, pi=alpha-m, digit box D_H (unique Babai lifts). (A) Sigma_rot={x->m*x} is coordinate-depend
IDEA-20261018-1aff90	[proposed]	coppersmith	A GF(2) block Wiedemann (Coppersmith) consistency test on the sparse Macaulay matrix decides, for th
count 8
## hypotheses.jsonl
H-ECDLP-15d016	[specified]	coppersmith	Fix the one-step next-feature split of a parity feature on a prime-order additive group before any p
H-ECDLP-78337d	[specified]	coppersmith	Fix the prime-order / twist-order split of one Weierstrass toy before any Weil-restriction index cal
H-ECDLP-7b7398	[specified]	coppersmith	Fix the multiplicative N^2-th-root uniqueness on F_p^* before any cubical point, division polynomial
H-ECDLP-c3d48a	[specified]	coppersmith	Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
H-ECDLP-cacf58	[specified]	coppersmith	Fix the ring Z[i] before any Coppersmith small-root solve, Semaev polynomial, Velu map, yield ratio,
H-RSA-564644	[specified]	coppersmith	Fix the exact count identity of IDEA-20260901-cc08db before any later-stage claim. Stage 0 asserts o
count 6
######## TERM: howgrave
## proposals.jsonl
IDEA-20260808-24c61b	[proposed]	howgrave	Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is 
IDEA-20260808-e2315e	[proposed]	howgrave	Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia
IDEA-20260816-a321ac	[proposed]	howgrave	(A) Every small-root construction pays for reach with two coupled costs: the lattice dimension D, wh
IDEA-20260901-c5e859	[proposed]	howgrave	FIVE SEPARABLE CLAIMS. (A) THE OBJECT. Fix a univariate small-root instance with known answer x0 -- 
IDEA-20261009-85062c	[proposed]	howgrave	The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
count 5
## hypotheses.jsonl
H-ECDLP-c3d48a	[specified]	howgrave	Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
count 1
######## TERM: jochemsz
## proposals.jsonl
IDEA-20260903-81a943	[unverified]	jochemsz	For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree,
IDEA-20260904-39336c	[proposed]	jochemsz	The closure of IDEA-20260903-81a943 rests on one supply number, eps_available(S_3) = 0.8408, the Joc
count 2
## hypotheses.jsonl
H-ECDLP-c3d48a	[specified]	jochemsz	Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
H-PFDR-621852	[proposed]	jochemsz	On the frozen direct-box S4/S5 planted law and actual modular JM/BKZ pipeline, test source beta thre
count 2
######## TERM: small-root
## proposals.jsonl
IDEA-20260802-003	[unverified]	small-root	TWO CLAIMS, ONE NEGATIVE AND ONE MEASURED, AND THEY ARE STATED SEPARATELY BECAUSE THEY HAVE DIFFEREN
IDEA-20260808-c31f1c	[proposed]	small-root	The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re
IDEA-20260808-e2315e	[proposed]	small-root	Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia
IDEA-20260816-7d1ed0	[proposed]	small-root	(A) The distinctive property of a small-root method, as this repository records it in KN-TECH-015, i
IDEA-20260816-a321ac	[proposed]	small-root	(A) Every small-root construction pays for reach with two coupled costs: the lattice dimension D, wh
IDEA-20260816-b4e5b7	[proposed]	small-root	(A) The quantity this program actually needs from Coppersmith-style partial-information recovery is 
IDEA-20260816-b5b822	[proposed]	small-root	(A) A Coppersmith-style small-root pipeline is a composition of five separable stages, and the progr
IDEA-20260901-c5e859	[proposed]	small-root	FIVE SEPARABLE CLAIMS. (A) THE OBJECT. Fix a univariate small-root instance with known answer x0 -- 
IDEA-20260901-c75e81	[proposed]	small-root	FIVE SEPARABLE CLAIMS. (A) THE OBJECT. For a small-root construction C with asymptotic reach exponen
IDEA-20260901-c7d8f6	[proposed]	small-root	FIVE SEPARABLE CLAIMS. (A) THE PREMISE BEING TESTED. RQ-RSA-d46f02 and GOAL-RSA-002 state that ECDSA
IDEA-20260901-cc08db	[proposed]	small-root	FIVE SEPARABLE CLAIMS, ALL ABOUT COST MODELS. (A) THE OBJECT. For a balanced n-bit modulus with p of
IDEA-20260903-81a943	[unverified]	small-root	For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree,
IDEA-20260904-8dccc9	[proposed]	small-root	Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
IDEA-20260913-c5f90d	[proposed]	small-root	OBJECT FRAME. Representation: the height-minimal rational representative of the x-coordinate -- for 
IDEA-20260923-9e4b71	[proposed]	small-root	(A) THE MODEL SHIFT. RQ-ECDLP-78dbc5 asks for fewer stored entries at fixed online cost in a charged
IDEA-20261009-85062c	[proposed]	small-root	The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
count 16
## hypotheses.jsonl
H-ECDLP-4b54a2	[approved]	small-root	SETTING AND CODOMAINS. p is a prime, E/F_p is an ordinary curve of prime order N (N = p up to O(sqrt
H-ECDLP-c3d48a	[specified]	small-root	Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
H-ECDLP-cacf58	[specified]	small-root	Fix the ring Z[i] before any Coppersmith small-root solve, Semaev polynomial, Velu map, yield ratio,
H-RSA-c1c5b2	[specified]	small-root	Fix the exact count identity of IDEA-20260901-c75e81 before any later-stage claim. Stage 0 asserts o
count 4
######## TERM: smallroot
## proposals.jsonl
IDEA-20260904-8dccc9	[proposed]	smallroot	Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
count 1
## hypotheses.jsonl
H-PFDR-3c7d1e	[proposed]	smallroot	The rank-1 closure of the lattice-describable factor-base family (IDEA-20260903-81a943, analysis/sma
count 1
######## TERM: groebner basis over z
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: strong gr
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: corner
## proposals.jsonl
IDEA-20260723-006	[speculative]	corner	For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)
IDEA-20260805-f9e801	[unverified]	corner	TWO SEPARABLE CLAIMS, THE FIRST OF WHICH IS A PURE ARITHMETIC CHECK COSTING SECONDS AND WHICH THIS P
IDEA-20260806-3b91c7	[unverified]	corner	THIS IS AN EXPONENT CORRECTION TO A COMPARATOR, NOT AN ATTACK. It makes every positive claim in this
IDEA-20260829-bb336b	[proposed]	corner	(A) WHAT THE PUBLISHED NUMBER ACTUALLY IS. FIPS 204's category claim, and every RQ-MLDSA-001 record 
IDEA-20260901-69912d	[proposed]	corner	Three statements. G is the gate, T is the table, R is the reading rule. (G) THE AFFINE GATE. For eve
IDEA-20260930-79abd9	[proposed]	corner	SETTING. Generic prime-order group, Q = [x]P with x in W(m, w), 2^m < n, alpha = w/m, H the binary e
count 6
## hypotheses.jsonl
H-ECDLP-6c52c0	[proposed]	corner	Source proposal IDEA-20260806-3b91c7 (RQ-ECDLP-002, class cost-model). THE SOURCE PROPOSAL IS NOT ED
H-SEMAEV-002	[supported]	corner	For every tested m in {3, 4}, every tested small prime p >= 5, and every tested nonsingular short-We
H-SEMBIN-c59e50	[weakened]	corner	The exponent constant c = 1.6986 in Semaev 2015's bound 2^{1.6986 sqrt(n ln n)} is carried ENTIRELY 
count 3
```

### Raw grep output, batch 2
```
######## TERM: initial ideal
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: leading monomial
## proposals.jsonl
count 0
## hypotheses.jsonl
H-DREG-91be14	[proposed]	leading monomial	SCOPE. The boolean chained Semaev system at m = 3, t = 3 as built by src/semaev_tree.py and Weil-des
count 1
######## TERM: leading coefficient
## proposals.jsonl
IDEA-20260818-ec1740	[proposed]	leading coefficient	The deployment cost model for class groups of imaginary quadratic orders is a SINGLE subexponential 
IDEA-20260825-823de4	[proposed]	leading coefficient	A dyadic interval can expose its exact unit-product state as an element of a typed quotient ring, co
IDEA-20261006-8d97d3	[proposed]	leading coefficient	For Phi_T = g tau + Delta tau^2 the composition Phi_T composed with itself has tau-degree 4 and lead
IDEA-20261006-f6419e	[proposed]	leading coefficient	Use the reduction convention for positive-definite binary quadratic forms: |b| <= a <= c, and if |b|
count 4
## hypotheses.jsonl
H-XEDN-876f24	[approved]	leading coefficient	TEST BOUNDARY. Prime p=5. Curve family y^2 = x^3 + b(t) with a(t)=0. Two slot spaces: coefficient ve
count 1
######## TERM: leading-monomial
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: newton polytope
## proposals.jsonl
IDEA-20260723-006	[speculative]	newton polytope	For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)
IDEA-20260808-c31f1c	[proposed]	newton polytope	The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re
IDEA-20260811-97e244	[proposed]	newton polytope	(A) THE PRECISE REASON SUPPORT IS THE WRONG FUNCTIONAL. The campaign's standing puzzle is committed:
IDEA-20260904-8dccc9	[proposed]	newton polytope	Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
count 4
## hypotheses.jsonl
H-ECDLP-30a2a1	[proposed]	newton polytope	Source proposal IDEA-20260808-2e14f7 (RQ-ECDLP-002, class representation). For E/F_p ordinary with p
H-ECDLP-c3d48a	[specified]	newton polytope	Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
H-JINV-28621d	[specified]	newton polytope	Fix the exact count identity of IDEA-20260811-97e244 before any later-stage claim. Stage 0 asserts o
count 3
######## TERM: ideal power
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: tropical
## proposals.jsonl
IDEA-20260814-c3af09	[proposed]	tropical	CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
count 1
## hypotheses.jsonl
count 0
######## TERM: valuation
## proposals.jsonl
IDEA-20260726-008	[methodological]	valuation	Ledger barriers that charge "evaluating a degree-d isogeny costs ~O(d)" predate the sqrt-elu evaluat
IDEA-20260731-002	[adaptation]	valuation	There exists a fully charged cost model of FAEST multi-round forgery — charging every hash evaluatio
IDEA-20260801-006	[adaptation]	valuation	Wesolowski 2026's concrete van Oorschot–Wiener middle-memory cost for the supersingular isogeny prob
IDEA-20260805-db5afa	[unverified]	valuation	For every HQC instance, the Hamming weight of the error vector e' = x.r2 - r1.y + e, taken over the 
IDEA-20260807-06cc5d	[proposed]	valuation	(A) THE EXTERNAL INGREDIENT, VERIFIED AT ABSTRACT LEVEL AND CITED WITH ITS LIMITS. Chung, Diaconis a
IDEA-20260807-bbdcf3	[proposed]	valuation	(A) THE TWO NUMBERS, AND WHY THE GAP CUTS BOTH WAYS. For an ordinary E/F_p with Frobenius trace t, d
IDEA-20260808-bfee7e	[proposed]	valuation	GOAL-AES-003 records an r=5 yoyo hit count of 59 for AES against a null expectation of 4.0 (BATCH-00
IDEA-20260809-313546	[proposed]	valuation	For AES-GCM the authentication tag is a polynomial evaluation in a key-derived point, and the equali
IDEA-20260809-666d3d	[proposed]	valuation	Every quantum cost estimate for CSIDH multiplies an oracle-query count by the cost of evaluating the
IDEA-20260809-758a6a	[proposed]	valuation	A reversible implementation of the group action cannot be cheaper than a good classical constant-tim
IDEA-20260809-78f3c4	[proposed]	valuation	The chief risk in this goal is drift from "locating the disagreement" to "settling it". The claim is
IDEA-20260809-c059a7	[proposed]	valuation	Every parameter choice in password hashing is an attempt to maximize the attacker's cost per guess s
IDEA-20260814-c3af09	[proposed]	valuation	CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
IDEA-20260815-621eea	[proposed]	valuation	Every CSIDH quantum estimate multiplies a query count by an oracle cost. The query count is disputed
IDEA-20260816-1128f8	[proposed]	valuation	(A) In a t-pass Argon2 evaluation the dependency graph has roughly t*m nodes, one per (pass, index) 
IDEA-20260816-25269a	[proposed]	valuation	(A) THE ASYMMETRY. Every factor-base geometry measurement recorded in this program reports what the 
IDEA-20260816-28a7fb	[proposed]	valuation	(A) A concrete-security number attached to an FHE parameter set is the output of a cost model evalua
IDEA-20260816-2c1f20	[proposed]	valuation	(A) The security argument for Argon2 is a cost argument, and the cost currency is area-time: memory 
IDEA-20260816-389b1b	[proposed]	valuation	(A) A cost quoted as device-hours converts to evaluations by multiplying by a device's throughput, a
IDEA-20260816-398c6b	[proposed]	valuation	(A) Section 4 of docs/inventor-protocol.md requires that a measured obstruction be read twice: once 
IDEA-20260816-3fc7b2	[proposed]	valuation	(A) Sparse secrets exist in FHE parameter sets because they make bootstrapping affordable, so any pr
IDEA-20260816-4b35b0	[proposed]	valuation	(A) Every forgery in a polynomial-evaluation MAC succeeds exactly when the authentication key is a r
IDEA-20260816-5a8d47	[proposed]	valuation	(A) Repeating a nonce in a polynomial-evaluation MAC yields an equation whose unknown is the authent
IDEA-20260816-5c040d	[proposed]	valuation	(A) The frozen gate declares OBSTRUCTED when a reduced Delta has an odd valuation at a finite irredu
IDEA-20260816-72e5e5	[proposed]	valuation	(A) OBJECT. An FO-bound evaluator is a function from a term list plus an input vector to a bit-secur
IDEA-20260816-79aec0	[proposed]	valuation	(A) Merkle-Damgard strengthening pins bits in the last block: a one bit, zeros, and a 64-bit length 
IDEA-20260816-7d1ed0	[proposed]	valuation	(A) The distinctive property of a small-root method, as this repository records it in KN-TECH-015, i
IDEA-20260816-8596af	[proposed]	valuation	(A) OBJECT. A chain of reductions is written as a sequence of steps, each of which replaces one expr
IDEA-20260816-ade53e	[proposed]	valuation	(A) A near-collision block search proceeds by satisfying a chain of conditions and restarting when o
IDEA-20260818-17300c	[proposed]	valuation	Every exTNFS cost model turns norm sizes into relation counts through one substitution: "a norm of N
IDEA-20260820-53aa2d	[proposed]	valuation	A prequential e-value process evaluated under a frozen adaptive policy may test simulator calibratio
IDEA-20260820-9dc01a	[proposed]	valuation	Given a fixed finite candidate set and candidate-wise test martingales that are valid under each can
IDEA-20260823-38f214	[unverified]	valuation	Conditional research proposal only; the exact possible bound and every unproved dependency remain so
IDEA-20260823-6284e8	[unverified]	valuation	Conditional research proposal only; the exact possible bound and every unproved dependency remain so
IDEA-20260823-850562	[unverified]	valuation	Conditional research proposal only; the exact possible bound and every unproved dependency remain so
IDEA-20260828-18f49b	[proposed]	valuation	BATCH-002's yoyo/boomerang quartet construction (mode A1) measures an r=5 hit count of 59 against a 
IDEA-20260829-512415	[proposed]	valuation	E-521 is x^2 + y^2 = 1 - 376014 x^2 y^2 over p = 2^521 - 1. Four separable sub-claims. C1 and C2 are
IDEA-20260829-70258e	[proposed]	valuation	(A) WHAT THE FAMILY ACTUALLY DOES. Kani-style embeddings need an auxiliary endomorphism of norm S = 
IDEA-20260829-b130bb	[proposed]	valuation	Curve41417 is x^2 + y^2 = 1 + 3617 x^2 y^2 over p = 2^414 - 17. Four separable sub-claims. (C1) THE 
######## TERM: gröbner
## proposals.jsonl
IDEA-20260731-016	[unverified]	gröbner	In ordinary prime-field isogeny classes at toy sizes (bitlength of N in [40,60]), the per-curve dist
IDEA-20260731-017	[unverified]	gröbner	Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
IDEA-20260801-002	[adaptation]	gröbner	The boolean chained Semaev (m=3, t=3) system's graded pivot-degree Hilbert function, computed by exa
IDEA-20260801-004	[unverified]	gröbner	For ordinary curves over generic prime fields, forcing a Semaev/Gröbner heavy tail by choosing a sec
IDEA-20260828-661a28	[proposed]	gröbner	Steiner (arXiv 2402.07852 / ePrint 2024/313), retrieved this session at abstract level only, develop
IDEA-20260828-faca4f	[proposed]	gröbner	(A) THE UNEXAMINED THIRD FAMILY. Twelve-plus batches of GOAL-MLKEM-003/004 and all 25 filed RQ-MLKEM
IDEA-20260922-881df9	[proposed]	gröbner	Representation class R3 of RQ-ECDLP-623a32 (Weil restriction of the chained summation coordinates), 
IDEA-20260922-9d808c	[proposed]	gröbner	Representation class R3 of RQ-ECDLP-623a32 (Weil restriction coordinates), attack stage relation-dec
IDEA-20260922-f1e5b7	[proposed]	gröbner	Representation class R3 of RQ-ECDLP-623a32 (Weil restriction to F_2 of the affine x-coordinates and 
IDEA-20261001-556cea	[proposed]	gröbner	KR-IC-f5c584 states the trace morphism forces a linear equation (first fall degree 2 for S_3); KR-IC
IDEA-20261006-9475a4	[proposed]	gröbner	Representation R1, attack stage relation decomposition, as an elimination-degree proxy rather than a
count 11
## hypotheses.jsonl
H-MLKEM-677f84	[specified]	gröbner	Fix the exact count identity of IDEA-20260828-661a28 before any later-stage claim. Stage 0 asserts o
H-MLKEM-fef84f	[specified]	gröbner	Fix the exact count identity of IDEA-20260828-faca4f before any later-stage claim. Stage 0 asserts o
H-PFDR-d5f90f	[specified]	gröbner	A finite increasing-s ladder with retained producers, separate degree conventions, and two-sided las
count 3
######## TERM: determinant criterion
## proposals.jsonl
IDEA-20260901-c75e81	[proposed]	determinant criterion	FIVE SEPARABLE CLAIMS. (A) THE OBJECT. For a small-root construction C with asymptotic reach exponen
count 1
## hypotheses.jsonl
count 0
######## TERM: unconditional
## proposals.jsonl
IDEA-20260805-19990a	[unverified]	unconditional	FILED EXPLICITLY AS AN IMPLEMENTATION-CLASS PROPOSAL, per GOAL-MAYO-001's next_action: 'proposals th
IDEA-20260805-4243e6	[unverified]	unconditional	For an ordinary curve E/F_p with #E(F_p) = N = p + 1 - t, the set of curves that a Teske-style desig
IDEA-20260806-9d47e2	[unverified]	unconditional	(A) THE COST IDENTITY, WHICH IS A COROLLARY THE FINDING STATES AND DOES NOT CASH. KN-FIND-c41ea9 est
IDEA-20260807-90479e	[proposed]	unconditional	KN-LIT-7592 (Straznickas-Weis, citation_verified: read) gives an UNCONDITIONAL, heuristic-free reduc
IDEA-20260808-0e9fa1	[proposed]	unconditional	The windowed decomposition count for a target R is the number of F_p-points of the hypersurface S_{m
IDEA-20260808-51e40f	[proposed]	unconditional	Every algebraic attack in this slice terminates in a DETERMINED quadratic solve. For q = 2^e the Fro
IDEA-20260808-e2315e	[proposed]	unconditional	Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia
IDEA-20260813-878855	[proposed]	unconditional	After primary sources fix the real signer and genuine simulator, test whether their unconditional si
IDEA-20260828-606247	[proposed]	unconditional	Formalizes catalogue entry A2-8 (ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/A2.md, lines 685-753), 
IDEA-20260829-512415	[proposed]	unconditional	E-521 is x^2 + y^2 = 1 - 376014 x^2 y^2 over p = 2^521 - 1. Four separable sub-claims. C1 and C2 are
IDEA-20260829-7169d6	[proposed]	unconditional	THREE LINKED STATEMENTS. STATEMENT 1, BOOTSTRAP. The log-interval key that IDEA-20260829-390ccc argu
IDEA-20260829-8cbb9b	[proposed]	unconditional	This program's upper-bound instrument is PARI ellrank, and two facts about it are committed. FIRST, 
IDEA-20260829-c705b4	[proposed]	unconditional	THE OBSERVATION FIRST, BECAUSE IT IS A FACT ABOUT COMMITTED RECORDS AND NOT A HYPOTHESIS. Every unco
IDEA-20261016-397ac9	[proposed]	unconditional	At bit length n = 256, the factor 2^{80} n^4 = 2^{112} quoted from Delgado’s Theorem 4.4 (arXiv:2609
count 14
## hypotheses.jsonl
H-AES-93d0ca	[specified]	unconditional	Fix the exact count identity of IDEA-20260828-606247 before any later-stage claim. Stage 0 asserts o
H-BINSTD-b6eca7	[approved]	unconditional	CLAIM (representation / heuristic-validation at toy scale). Let E: y^2+xy=x^3+a x^2+b over F_{2^n}, 
H-ECDLP-a6d66b	[proposed]	unconditional	FIELD CORRECTION, RECORDED FIRST BECAUSE IT CHANGES WHAT THIS RECORD IS. The dispatching handoff TAS
H-ECRANK-28dba7	[supported]	unconditional	There is an explicit elliptic curve E/Q and an explicit multiquadratic field K with [K:Q] <= 32 such
H-HAWK-e783e5	[specified]	unconditional	Fix the exact count identity of IDEA-20260807-90479e before any later-stage claim. Stage 0 asserts o
H-MAYO-c0ddab	[proposed]	unconditional	IMPLEMENTATION CLASS, FILED SEPARATELY FROM THE MAP-CLASS HYPOTHESIS H-MAYO-2c6c34, per GOAL-MAYO-00
H-PCD-03be5a	[specified]	unconditional	The polynomial-calculus refutation degree PC(F) of the Semaev decomposition system for an undecompos
H-SDEG-489b76	[rejected]	unconditional	At balanced L=q^{1/5} on ordinary prime-field toys, the serial-S3 backward-3-sum eliminant degree ex
count 8
######## TERM: lattice reach
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: reach ceiling
## proposals.jsonl
count 0
## hypotheses.jsonl
count 0
######## TERM: p-adic
## proposals.jsonl
IDEA-20260807-dbb250	[proposed]	p-adic	(A) WHY THIS ROUTE IS TEMPTING AND MUST BE ADDRESSED. The Serre-Tate canonical lift of an ORDINARY c
IDEA-20260811-dc6ece	[proposed]	p-adic	(A) THE CANONICAL ARM, CLOSED BY IDENTITY AND NOT BY MEASUREMENT. For an ordinary E/F_p the Frobeniu
IDEA-20260901-b4e6eb	[proposed]	p-adic	Frozen setting, inherited verbatim from the repaired hypotheses of the 2026-08-31 ECDLP-IDEA-436 err
IDEA-20260905-3a30d5	[proposed]	p-adic	(A) THE THREE FUNCTIONS. E/F_p ordinary, cofactor 1, n = #E coprime to p, E^ the naive lift with the
IDEA-20260905-848b77	[proposed]	p-adic	(A) THE SETTING AND THE SPLITTING. E/F_p with good reduction, p >= 3, E^/Q_p any lift (the naive one
IDEA-20260905-dacf4f	[proposed]	p-adic	(A) THE GAP. harness/toycurve.py provides exact F_p arithmetic and point counting only. The only ano
IDEA-20261009-843cfd	[proposed]	p-adic	In Z_p^* the Teichmuller character gives the unique homomorphic section of Z_p^* -> F_p^* with image
IDEA-20261009-bec077	[proposed]	p-adic	For random ordinary curves at p in 2^20 .. 2^48, h(D) fits c * sqrt(p) times a slowly varying factor
IDEA-20261009-d2412c	[proposed]	p-adic	For E/F_p with a prime-order subgroup <P>, n != p, let s_tor be the torsion section (the unique n-to
IDEA-20261017-5c1d2a	[proposed]	p-adic	p=m^d-c prime; pi=alpha-m generates the degree-1 prime of Z[alpha]=Z[X]/(X^d-c), N(pi)=+-p; psi2: Z[
count 10
## hypotheses.jsonl
H-CANL-613cfc	[specified]	p-adic	Fix the exact count identity of IDEA-20260807-dbb250 before any later-stage claim. Stage 0 asserts o
H-CANL-b77100	[specified]	p-adic	Fix the exact count identity of IDEA-20260811-dc6ece before any later-stage claim. Stage 0 asserts o
H-CZLIFT-fba874	[analyzed]	p-adic	Let E/F_p have a prime-order subgroup <P>, n != p, and let s_tor be the torsion section on a lift E^
count 3
```

### Hits that may be the same object (id, status, first 100 chars of claim from the index row)
- IDEA-20260904-39336c [proposed] The closure of IDEA-20260903-81a943 rests on one supply number, eps_available(S_3) = 0.8408, the Joc
- IDEA-20260808-e2315e [proposed] Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia
- IDEA-20260723-006 [speculative] For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)
- H-PFDR-3c7d1e [proposed] The rank-1 closure of the lattice-describable factor-base family (IDEA-20260903-81a943, analysis/sma
- IDEA-20260903-81a943 [unverified] For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree,
- IDEA-20260904-8dccc9 [proposed] Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
- IDEA-20260808-486ae2 [proposed] (A) CLASSIFICATION. IDEA-20260801-021 / IDEA-20260803-e2f5bd bound any factor base cut out by a targ
- H-ECDLP-c3d48a [specified] Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
- IDEA-20260808-c31f1c [proposed] The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re
- IDEA-20261009-85062c [proposed] The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
- IDEA-20260816-a321ac [proposed] (A) Every small-root construction pays for reach with two coupled costs: the lattice dimension D, wh
- IDEA-20260901-c75e81 [proposed] FIVE SEPARABLE CLAIMS. (A) THE OBJECT. For a small-root construction C with asymptotic reach exponen
- IDEA-20260814-c3af09 [proposed] CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
- H-PFDR-621852 [proposed] On the frozen direct-box S4/S5 planted law and actual modular JM/BKZ pipeline, test source beta thre

Full records opened (exact paths; 3 of 3 allowed):
1. ledger/proposals/IDEA-20260904-39336c.yaml. Same lead step (run Ryan's optimal shifts on the S_3 polytope and the joint (4,2) system). Its F1 states "The information ceiling for this normalization is eps = 1, so the unexploited slack on the S_3 polytope is 0.1592". For full-corner blocks C4/C1 shows the binding ceiling is the corner weight 1/D, not 1. So C4 does not duplicate it; it undercuts one of its premises for the single-corner cells and leaves its joint (4,2) arm untouched. Its "SECOND ARM" (charge dimension as N^delta) is the IDEA-20260808-e2315e arm.
2. ledger/proposals/IDEA-20260808-e2315e.yaml. Superpolynomial shift dimension; mechanism sentence "Howgrave-Graham's lemma is unconditional at every dimension". C4's lemma answers its question for single-corner cells at every t and every dimension (the floor p^t is dimension-free), within the (p,f)^t ideal. For multi-corner cells it stays open at the strong-GB level. Not a duplicate: e2315e proposes an empirical eps(D) sweep, C4 a proof.
3. ledger/proposals/IDEA-20260723-006.yaml. Corner-coefficient induction for the Semaev Newton polytope: the premise "corner coefficient is a unit" is recorded here, but as a BKK/mixed-volume negative gate, never connected to HG lattices. Premise precedent, not the same object.

Judged from index rows only (not opened): H-PFDR-3c7d1e (rank-1 closure, rank-r substitution; the sibling read it), IDEA-20260903-81a943 / IDEA-20260904-8dccc9 / IDEA-20260808-486ae2 / H-ECDLP-c3d48a / IDEA-20260808-c31f1c (JM-based closure, digits, GAP invariance lemma, threshold identities: all JM-strategy-specific), IDEA-20260901-c75e81 / IDEA-20260816-a321ac (reach vs dimension cost), H-PFDR-621852 (planted recovery). IDEA-20260814-c3af09 is the only "tropical" hit ("Lift-stable tropical initial-form decoder": a valuation-branch decoder that must return exact factor-base points). It is a solver proposal, not a reach ceiling, so not the same object. IDEA-20261009-85062c ("empirical 50%-recovery threshold beta* for S_3 ... falsified if beta* >= 1/2 for S_3") has a consequence worth recording: if its beta is per variable (x(P) < p^beta, as its mechanism says), the lemma gives beta* < 1/4 for HG on (p,S_3)^t, so that falsifier can never fire (derived; I did not open the record).

No hit in 22 terms states a strong-Groebner, leading-coefficient-valuation or initial-ideal ceiling for (p,f)^t. "groebner basis over z", "strong gr", "initial ideal", "ideal power", "leading monomial" (HG context), "lattice reach", "reach ceiling" returned zero relevant rows.

## 4. N4 notation check

- Pair: (representation, operation set Sigma) = (R1: integer representative of x(P) in [0,p) with an archimedean box, or the GAP/AP/digit coordinates u of x = a_0 + sum a_j u_j with |u_j| <= X_j; Sigma = {monomial shifts, multiplication within the ideal (p,f)^t, integer linear combinations} acting on polynomials in u, not on points of G).
- Trichotomy: coordinate-dependent (the box is a function of the representation); the index-calculus context is partial-action (translation by factor-base elements), as in the sibling.
- Is it a recorded rigidity result in new notation? **No.** IDEA-20260806-c5d183 and KN-FIND-ffe1df Theorem C are about projections of G propagating under full translation; Sigma here is not a group action on G and the lemma is a statement about an ideal's leading coefficients, so neither covers it. IDEA-20260901-863e36 (projection paired with an operation set; block systems of <Sigma>) concerns lossy quotients of G; C4 tracks no lossy object of G. KN-OPEN-020 (bounded-degree algebraic factor bases scoped out; open class = high-degree, implicit-membership or target-dependent descriptions): a box is an implicit-membership description, so C4 is a result INSIDE the open class: it bounds one solver family (HG lattices over (p,f)^t) for it. It neither re-derives the bounded-degree theorem nor changes the open status of the class (other solvers for implicit membership remain unexamined).
- What N4 does NOT show: the box is also "bounded degree in u" after substitution, but the size bounds are archimedean, so SO-ALGFB's O(d) locus argument does not apply; the mean-yield conservation clause still does. The closure is a statement about the oracle, not about yield.

## 5. Gate-side checks (my own; analysis and toy)

### 5.1 The lemma, re-derived by hand (derived, not computed)
Let f in Z[u] have coefficient c_0 with p not dividing c_0 at a monomial u^{a0} that is LM(f) for some monomial order sigma, and let the box weight w(a) = sum_i omega_i a_i (X_i = p^{omega_i}). I_t = (p,f)^t = sum_k p^{t-k} f^k Z[u]. Work over Z_(p) so f/c_0 is monic. G = {g_k = p^{t-k} f^k : 0 <= k <= t} is a strong Groebner basis: for k < l, the S-polynomial is p^{t-k} f^k (M^{l-k} - f^{l-k}) = h*g_k with LM(h*g_k) = LM(S), a standard representation, and the G-polynomial is g_l itself because v_p(p^{t-l}) < v_p(p^{t-k}). Hence for every nonzero g in I_t with leading monomial u^a, the leading coefficient c lies in p^{t-kappa(a)} Z, where kappa(a) = min(t, max{k : LM(f)^k | u^a}). Since k*a0 <= a, w(a) >= kappa(a) * w(a0). So ||g(Xx)||_inf >= |c| X^a >= p^{t-kappa} p^{w(a)} >= p^{t - kappa + kappa*w(a0)} >= p^t whenever w(a0) >= 1. Howgrave-Graham needs ||g(Xx)||_2 < p^t / sqrt(dim). So no HG-useful polynomial exists at any t and any M. This is "Lemma U". The sibling's statement D*log_p(vol) < 1 is the same threshold. For S_{m+1} with one unit corner prod c_i^D (D = 2^{m-1}), Lemma U gives: HG-type lattices over (p,S)^t find nothing once D * sum_i omega_i >= 1.
Scope kept: only the ideal (p,f)^t (not the full vanishing ideal of the root mod p^t; sibling scope item 2); one equation (sibling scope item 3 = C2).

### 5.2 Lemma U is weaker than the sibling's order-averaged determinant lemma on multi-corner cells (derived)
For the 3-unknown block S_3(x_a,x_b,u) there are three monic corners x_i^2 x_j^2. Lemma U closes the block if SOME pair has omega_i + omega_j >= 1/2; the feasible region is therefore all three pair sums < 1/2, i.e. block volume < 3/4 (at equal weights omega < 1/4 each). The sibling's averaged determinant argument gives vol_block < 1/2 (section 2.6 of the sibling dossier), which is stronger but Gaussian-heuristic level. For rank-r GAP slots with spread weights the same relation holds. So Lemma U is the weaker, unconditional statement on multi-corner blocks; it cannot replace C1/C2's sharper ceiling, but it is enough for section 5.6.

### 5.3 Misstatement in the candidate: "IC demand is >= 1" and "covers GAP rank r <= 2^{m-1}" (derived from CLOSURE.md)
CLOSURE.md DEMAND at w = 0 is epsilon_req = m/(2(m-1)) (equivalently sum_i beta_i >= m/(2(m-1)): 1.0 at m=2, 0.75 at m=3, 0.667 at m=4, 0.571 at m=8; tends to 1/2). The candidate's "demand >= 1" holds only at m = 2. The closure conclusion survives: the ceiling 2^{1-m} <= 1/2 < m/(2(m-1)). The rank claim does not: closure needs max over generator choices of D * sum_i omega_{i,c_i} >= 1; with slot volume spread evenly over r generators and beta at the minimum demand 1/(2(m-1)), this holds iff r <= D*m*beta = 2^{m-2} * m/(m-1) (m=3: r <= 3; m=4: r <= 5.33; for the 2^{m-1} claimed: m=4 would be 8). So the unconditional form covers GAP rank up to 2^{m-2} m/(m-1) at minimum demand (and r <= D m beta for larger beta), and "digits" are rank s, not rank 1, so they fall under the same bound. (Even-spread weights are the worst case for Lemma U; uneven spreads help it.)

### 5.4 Misdirected outcome mapping in the candidate (derived)
"Certified reach <= 1/2 -> single-equation cells closed_obstructed(theorem)". A finite-t cuso reach <= 1/2 is IMPLIED by Lemma U, it does not imply it; running cuso can only refute (reach > 1/2 -> lemma wrong). The closed_obstructed(theorem) status comes from the proof in 5.1 plus independent review of it, not from the cuso run. The H4 prediction interval [0.28, 0.50] (sum-beta units) is consistent with the sibling's probe (0.294 at L=16, JM 1/3 for the 2-unknown S_3) but is a prediction; I did not run cuso. Unit caution: the sibling's gate flagged that tools/smallroot_reach.py may use a different unit convention (sum versus per variable); C4's "sum-beta" has the same exposure.

### 5.5 Toy check of Lemma U (computed; sublattice only; NOT proof)
Script `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/_c4gate_svp2.py` (PARI 2.17.3 via gp: matkerint for the intersection with Z[M], then LLL, then qfminim). p = 101; f = S_3(x,y;xR) over Z with random integers a, b, xR (seeds 11, 12); corner x^2 y^2 has coefficient 1. Lattice = Z-span of p^(t-k) x^i y^j f^k with support inside M' intersected with Z[M], M = [0,L]^2 (M' = [0,L+t]^2), coordinates scaled by X^(i+j) with X1 = X2 = X (rational). "corner_weight" = log_p(X^4). Output = whether any lattice vector has L2 norm below p^t (qfminim with threshold p^(2t)(1 - 1e-6)); trivial vector p^t excluded by the tolerance. The generated lattice is a sublattice of (p,f)^t intersect Z[M], so this checks consistency with Lemma U, not the lemma. Positive control: X <= 3/2 (weight <= 0.35) does produce shorter vectors, so the test can fail.

t=2, L=4:
```
seed=11 p=101 t=2 L=4 M'=[0,6]^2 X=1/1 corner_weight=0.000 dim=25 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.14955806608646513 
seed=11 p=101 t=2 L=4 M'=[0,6]^2 X=3/2 corner_weight=0.351 dim=25 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.5787648410577364 
seed=11 p=101 t=2 L=4 M'=[0,6]^2 X=2/1 corner_weight=0.601 dim=25 n_vectors_with_norm<p^t=0 min_among_found/p^t=None 
seed=11 p=101 t=2 L=4 M'=[0,6]^2 X=4/1 corner_weight=1.202 dim=25 n_vectors_with_norm<p^t=0 min_among_found/p^t=None 
seed=12 p=101 t=2 L=4 M'=[0,6]^2 X=1/1 corner_weight=0.000 dim=25 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.26247554408179613 
seed=12 p=101 t=2 L=4 M'=[0,6]^2 X=3/2 corner_weight=0.351 dim=25 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.7741023221790991 
seed=12 p=101 t=2 L=4 M'=[0,6]^2 X=2/1 corner_weight=0.601 dim=25 n_vectors_with_norm<p^t=0 min_among_found/p^t=None 
seed=12 p=101 t=2 L=4 M'=[0,6]^2 X=4/1 corner_weight=1.202 dim=25 n_vectors_with_norm<p^t=0 min_among_found/p^t=None 
python3 _c4gate_svp2.py 2 4 6 1,3/2,2,4 2>&1  0.21s user 0.09s system 47% cpu 0.623 total
```
t=3, L=6:
```
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=1/1 corner_weight=0.000 dim=49 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.07228516686196941
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=3/2 corner_weight=0.351 dim=49 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.6636750512419497
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=2/1 corner_weight=0.601 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=5/2 corner_weight=0.794 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=3/1 corner_weight=0.952 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=7/2 corner_weight=1.086 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=3 L=6 M'=[0,9]^2 X=4/1 corner_weight=1.202 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=1/1 corner_weight=0.000 dim=49 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.05280110716227888
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=3/2 corner_weight=0.351 dim=49 n_vectors_with_norm<p^t=2 min_among_found/p^t=0.6505514637333235
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=2/1 corner_weight=0.601 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=5/2 corner_weight=0.794 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=3/1 corner_weight=0.952 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=7/2 corner_weight=1.086 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=3 L=6 M'=[0,9]^2 X=4/1 corner_weight=1.202 dim=49 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
python3 _c4gate_svp2.py 3 6 9 1,3/2,2,5/2,3,7/2,4 2>&1  3.38s user 0.20s system 77% cpu 4.639 total
```
t=4, L=8 (X in {2, 5/2, 3, 7/2, 4}; X < 2 not run):
```
seed=11 p=101 t=4 L=8 M'=[0,12]^2 X=2/1 corner_weight=0.601 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=4 L=8 M'=[0,12]^2 X=5/2 corner_weight=0.794 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=4 L=8 M'=[0,12]^2 X=3/1 corner_weight=0.952 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=4 L=8 M'=[0,12]^2 X=7/2 corner_weight=1.086 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=11 p=101 t=4 L=8 M'=[0,12]^2 X=4/1 corner_weight=1.202 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=4 L=8 M'=[0,12]^2 X=2/1 corner_weight=0.601 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=4 L=8 M'=[0,12]^2 X=5/2 corner_weight=0.794 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=4 L=8 M'=[0,12]^2 X=3/1 corner_weight=0.952 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=4 L=8 M'=[0,12]^2 X=7/2 corner_weight=1.086 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
seed=12 p=101 t=4 L=8 M'=[0,12]^2 X=4/1 corner_weight=1.202 dim=81 n_vectors_with_norm<p^t=0 min_among_found/p^t=None
timeout 900 python3 _c4gate_svp2.py 4 8 12 2,5/2,3,7/2,4 2>&1  45.55s user 0.59s system 90% cpu 50.923 total
sed 's/ ERR:\*\*\* matkerint: Warning: increasing stack size to [0-9]*\.//'  0.00s user 0.00s system 0% cpu 50.921 total
```
Reading: at corner weight >= 1 (X >= 7/2 at p = 101) no vector shorter than p^t exists at t = 2, 3, 4 (consistent with Lemma U). At weights 0.60-0.95 no short vector appears either at these sizes, so the toy does not probe how tight the ceiling is (the sibling's JM numbers suggest reach stays near corner weight 2/3 for this object, below 1). The toy neither confirms nor refutes the multi-corner or w > 0 claims.

### 5.6 Consequence for CLOSURE.md at (m,w) = (4,2) (derived; conditional on CLOSURE's demand model, which I did not re-derive)
CLOSURE.md sets the demand (I) (m-1)beta - sum_v(1 - gamma_v) > 1/2, (II) 2 beta < 1/2, (III) m beta + sum_v gamma_v <= epsilon (w+1). At (4,2): (I) gives gamma1 + gamma2 > 5/2 - 3 beta, and (II) gives beta < 1/4, so gamma1 + gamma2 > 7/4. With gamma_v <= 1 each gamma_v > 3/4, and (I) forces beta > 1/(2(m-1)) = 1/6.
- Root block S_3(y1, y2; x_R): two unknowns, unit corner y1^2 y2^2, a monomial divisible by every monomial of the block and so LM in every order. Corner weight 2(gamma1 + gamma2) > 7/2 >= 1. Lemma U: (p, S_3)^t holds no HG-useful polynomial at any t.
- Leaf blocks S_3(x1, x2, y1) and S_3(x3, x4, y2): the pair corner x1^2 y1^2 (coefficient 1, LM in the lex order x1 > y1 > x2) has weight 2(beta + gamma1) > 2(1/6 + 3/4) = 11/6 >= 1. Closed likewise.
So CLOSURE's per-block construction at (4,2) (each S_3 block solved by its own HG lattice over its own (p, S_3)^t) is closed unconditionally. The sibling's C2 reaches the root-block half at determinant level (its H4 prediction); Lemma U makes it rigorous for the per-block form.
Second consequence: CLOSURE's convention is "epsilon when the solver returns the roots whenever prod(bounds) <= p^(epsilon * #equations)". For a single 3-unknown block (#equations = 1) epsilon is the SUM of the three exponents. By 5.2 Lemma U allows block volume < 3/4, so the recorded supply epsilon(S_3, extended) = 0.8408 > 3/4 cannot be attained by any shift set inside (p, S_3)^t, and JM-extended shifts are such a set. So either CLOSURE's 0.8408 is not a sum-convention number or the JM value is above a ceiling. The sibling gate's observation fits the first reading: 0.8408/3 = 0.2803, the value the repo HG tool quotes for the same block, and the calculator's closed form 2n/(d(n+1)) for the full box [0,d]^n is twice the n=2, d=2 value 1/3 that I recall as the Jochemsz-May bivariate bound XY < W^(2/(3 delta)) for bidegree (delta, delta) (recalled, not retrieved). I did not read tools/smallroot_reach.py and did not adjudicate the cause. The direction is over-credit toward the attack: with Lemma U alone the per-equation supply is < 3/4 against demand 8/9, margin < -0.139 instead of -0.0481; if 0.2803 is the sum-reach, about -0.61 (the latter is the sibling's observation, not mine).
Still open at (4,2): a joint lattice over the ideal (p, f1, f2, f3)^t sharing y1, y2 (sibling C2; the joint arm of IDEA-20260904-39336c). Lemma U does not cover it: the leading monomials of the three equations share y1 and y2, so in_sigma(J^k) can exceed in_sigma(J)^k, as the sibling's scope item 3 says.

### 5.7 Toy check, 3-unknown S_3 block (computed; sublattice only; NOT proof)
Script `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/_c4gate_svp3var.py`: same construction as 5.5 for f = S_3(x,y,z;a,b) with all 13 monomials (the corners x^2y^2, x^2z^2, y^2z^2 each have coefficient 1), M = [0,L]^3, M' = [0,L+t]^3, X1 = X2 = X3 = X, "pair_corner_weight" = log_p(X^4), seeds 21, 22. X = 7/2 (101^0.2714 per variable) is close to the per-variable value 0.2803 that corresponds to CLOSURE's 0.8408 as a sum.
t=2, L=3:
```
seed=21 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=1/1 pair_corner_weight=0.000 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.48007041276834284 
seed=21 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=3/2 pair_corner_weight=0.351 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.9576833115713299 
seed=21 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=2/1 pair_corner_weight=0.601 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=21 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=7/2 pair_corner_weight=1.086 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=21 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=4/1 pair_corner_weight=1.202 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=1/1 pair_corner_weight=0.000 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.49860112126788797 
seed=22 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=3/2 pair_corner_weight=0.351 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=2/1 pair_corner_weight=0.601 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=7/2 pair_corner_weight=1.086 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=2 L=3 M'=[0,5]^3 gens=288 X=4/1 pair_corner_weight=1.202 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
python3 _c4gate_svp3var.py 2 3 1,3/2,2,7/2,4  4.37s user 0.21s system 59% cpu 7.695 total
```
t=3, L=3:
```
seed=21 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=1/1 pair_corner_weight=0.000 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.5388540524430804 
seed=21 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=3/2 pair_corner_weight=0.351 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.95768331157133 
seed=21 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=7/2 pair_corner_weight=1.086 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=21 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=4/1 pair_corner_weight=1.202 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=1/1 pair_corner_weight=0.000 dim=64 n_vec_below_p^t=2 found_norm/p^t=0.498601121267888 
seed=22 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=3/2 pair_corner_weight=0.351 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=7/2 pair_corner_weight=1.086 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
seed=22 p=101 t=3 L=3 M'=[0,6]^3 gens=496 X=4/1 pair_corner_weight=1.202 dim=64 n_vec_below_p^t=0 found_norm/p^t=None 
python3 _c4gate_svp3var.py 3 3 1,3/2,7/2,4  47.57s user 0.54s system 87% cpu 54.987 total
```
Reading: no vector shorter than p^t at pair-corner weight >= 1 (X = 7/2, 4), including X = 7/2, the nearest integer-friendly point to the per-variable 0.2803; the positive control (X = 1, and X = 3/2 in some seeds) shows shorter vectors. Sublattice of (p,f)^t intersect Z[M] at small t only; consistent with Lemma U and with 5.6, not a proof of it.

## 6. Citations with provenance

| citation | role | provenance |
|---|---|---|
| Ryan, "Solving Multivariate Coppersmith Problems with Known Moduli", EUROCRYPT 2025, ePrint 2024/1577 | Groebner-basis theory yields a provably optimal shift-polynomial set; implies C4's strong-GB lens is the machinery of the lead's own next_action tool (cuso). Abstract: the strategies "remain heuristic" for asymptotic bounds. | **retrieved** (WebFetch eprint.iacr.org/2024/1577 and WebSearch this session; abstract level only; a second WebFetch of the PDF eprint.iacr.org/2024/1577.pdf returned HTTP 403, so the paper's theorems, and whether it already contains a closed-form monic-corner bound or characterises the optimal lattice's determinant by strong-GB leading coefficients, were NOT read) |
| Adams-Loustaunau, An Introduction to Groebner Bases, AMS GSM 3 (1994), ch. 4 | strong Groebner bases over rings | **recalled** for the section-level content. Retrieved only: chapter 4 is titled "Groebner bases over rings" (AMS listing via WebSearch snippet); the AMS page itself returned 403. The definition of a strong GB over Z (every lead term of the ideal is divisible by some basis lead term, coefficient included) was **retrieved** from Macaulay2/OSCAR documentation snippets. I rely on neither: section 5.1 proves the needed fact directly. |
| Howgrave-Graham, "Finding small roots of univariate modular equations revisited", Cryptography and Coding 1997 (IMA), LNCS 1355, DOI 10.1007/BFb0024458 | the HG short-vector condition | **retrieved** at listing level (WebSearch this session: title, venue, LNCS volume, DOI; the lemma's text was not read, I use the standard statement from memory) |
| Aono, Agrawal, Satoh, Watanabe, ACISP 2012; Chinburg-Hemenway-Heninger-Scherr 2016 | related optimality for univariate and Boneh-Durfee-type lattices | **recalled** here; the sibling retrieved them at abstract level. A multivariate monic-corner form in their full texts, or in Ryan's, is not excluded: if it exists, the verdict moves toward known_result for the unconditional lemma (the sibling's H3). |
| Jochemsz-May 2006; Herrmann-May; Bauer-Joux | context | **recalled** |

Load-bearing citation status: Ryan 2025 (retrieved, abstract); everything else the lemma needs is proved in 5.1. A strong-GB argument is textbook-level, so I rate the lemma's novelty as `unverified`, an adaptation, and would not call it new mathematics.

## 7. Numbered heuristics and conditions

H1. Lemma U is rigorous inside its scope (single equation, ideal (p,f)^t, one unit corner of weight >= 1; proof 5.1, toy-consistent). It says nothing about structurally short polynomials in the larger vanishing ideal, nor about systems of several equations.
H2. The corner premise (S_{m+1} corner coefficient 1, LM in every order) is the sibling's induction plus numeric checks for m <= 4 (S_5 at one prime); IDEA-20260723-006 records the premise for the Newton polytope. I re-derived only the S_3 corner coefficient by hand (it is 1; the (x1x2 - a)^2 term) and did not recompute S_4 or S_5.
H3. If Ryan 2025 (or Aono et al.) states a multivariate monic-corner ceiling, the unconditional lemma is known and C4 reduces to a citation.
H4. At (4,2), Lemma U closes the per-block construction (5.6) but not a joint multi-equation lattice over (p, f1, f2, f3)^t; any statement about the lead as a whole needs C2.
H5. Direction of the unit question flagged in the sibling gate (tools/smallroot_reach.py, sum versus per variable): Lemma U plus CLOSURE's stated sum-of-exponents convention puts any attainable 3-unknown block volume below 3/4, so CLOSURE's 0.8408 is over-credited toward the attack (5.6). The cause inside the calculator I did not examine (I did not read tools/smallroot_reach.py). C4's own "sum-beta" numbers are sums of exponents.

## 8. Verdict

advances_lead. Lead: LEAD-ICP-coppersmith-smallroot-semaev (open_next_step). Merge into the sibling's C1 as a rigorous single-corner corollary (Lemma U). It closes CLOSURE.md's per-block (4,2) construction and makes the recorded supply 0.8408 unattainable in CLOSURE's own convention (5.6); correct "demand >= 1" and "rank <= 2^(m-1)" first (5.3); read the cuso run as a falsifier only (5.4). The lead stays open_next_step because a joint multi-equation lattice over (p, f1, f2, f3)^t at (4,2) is not covered (C2).
