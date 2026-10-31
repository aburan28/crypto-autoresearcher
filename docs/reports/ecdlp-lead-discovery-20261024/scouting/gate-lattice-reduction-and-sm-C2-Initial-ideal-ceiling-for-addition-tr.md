# Novelty gate N1-N4: C2 "Initial-ideal ceiling for addition-tree (kept-window) systems, plus HG-admissibility gate (prime field)"

Field: lattice reduction and small-root methods. Date 2026-10-24. Claim tier: gate report, no computation of the
candidate itself was run here. `sota_delta`: zero. Pollard rho remains the best known method. Every number below that
is a prediction is labelled as one. Everything quoted from `origin/...` branches was read with `git show`/`git grep`
(read-only) and is **unmerged to the branch this gate ran on** (`lead-discovery/20261024-mythos-ecdlp`, HEAD `7a05c759a7`);
the atlas and the tools below were built from the working tree and do NOT see it.

## 0. Verdict

**`advances_lead`** on **LEAD-ICP-coppersmith-smallroot-semaev** (`open_next_step`, ic-prime). Not `duplicate_of_lead`, not
`known_result`, not `new`.

Reasons, in order of weight.

1. Same mechanism as the lead (Coppersmith/HG small-root decomposition on a windowed binary addition tree with kept
   internal windows, the (m,w) = (4,2) cell). The lead's `forecloses` includes "windowed addition tree with lattice
   reduction" and "Coppersmith small roots of summation polynomials". The candidate is not outside those phrases.
2. It is a sharper next step for the lead's own `discriminates` clause ("optimal reach < 0.8889 everywhere turns the
   current heuristic ... closure into a strategy-independent one"). The lead's `next_action` is a supply computation
   (Ryan optimal shifts, Feng-Luo-Chen-Nitaj-Pan sumset bounds). The lead-discovery audit (AUD-4 for this lead, file
   `docs/reports/ecdlp-lead-discovery-20261024/AUDIT.md`, section "LEAD-ICP-coppersmith-smallroot-semaev") states: "No
   strategy-independent upper bound on Coppersmith-type reach is known. Reach depends on the shift polytope." C2 proposes
   exactly such an upper bound (a ceiling uniform over every monomial support M and every multiplicity t) for the w > 0
   cells. That is the part none of the lead's forecloses phrases, next_action, or ledger refs covers.
3. Strict reading of what is NOT new (section 7): the machinery is Ryan's (his optimal shift set is computed from a Groebner basis of
   the corresponding ideal), the demand inequality is already derived in the unmerged readiness report, the achievability/cuso arm
   duplicates an in-flight task, and the per-block ceiling is the unreviewed Lemma A of the sibling candidate C1. The only
   novel content is the uniformity over (M, t) via order-averaged initial ideals, applied to the joint ideal, conditional on H4.

Lead field for the structured output: LEAD-ICP-coppersmith-smallroot-semaev. Secondary leads the same ceiling would bound:
LEAD-ICP-lattice-ic-relation-construction (Newton-shift lane, IDEA-20261015-9defe9). The "HG-admissibility gate" half
lands on LEAD-ICP-construction-normal-form (`open_unexamined`).

## 1. Program state the atlas does not show (found while reading the ledger; decides N1 and N3)

Reading `git branch -a` for "smallroot" turned up in-flight work on exactly this cell. All items are read-only `git show`.

| item | ref / commit (all unmerged to HEAD `7a05c759a7`) | what it contains |
|---|---|---|
| Joint small-root finite accounting audit | `origin/research/joint-smallroot-reach-audit-20261024`, report added in `6a9f400e0f` (2026-10-24), head `c10660ccef` | exact HG determinant accounting `sum_i beta_i s_i < t*N - q`; the legacy calculator puts `q` on the right-hand side; finite joint union-support candidates (31, 382, 2591 columns at t = 1, 2, 3); "optimality of the tested shift families" explicitly NOT established |
| Weighted reach and readiness report | same branch, `readiness-20261025/report.md`, added in `3417ab1c40` (2026-10-25) | weighted region `4*sL*beta + 2*sI*gamma < K`; the conditional cost model `C(beta,gamma,tau) = max(3-3beta-2gamma+tau, 2beta)`; the rho-reference conditions `beta < 1/4` and `3beta+2gamma > 5/2 + tau`; pinned cuso 0.4.0 (commit `fb2747d2`) univariate calibration delta* = 1/3; cuso `optimal.py` calls `J.groebner_basis()` |
| Named open problem | same branch, `problems/joint-smallroot-reach-baseline-and-oracle-unverified.md`, added in `fefa0dd26c` | status `investigating`; lists "reconcile the optimized joint weighted-bound normalization" and "a real optimized joint construction" as open; says the old 0.8408 versus 8/9 margin is unreconciled |
| Correction to CLOSURE.md | `origin/fix/smallroot-reach-rhs-convention-pr`, `analysis/smallroot-reach/CORRECTION.md`, added in `f624a7dd5e` (2026-10-24) | `eps_HG = eps_TOOL / n`; 0.8408 -> 0.2803, margin -0.0481 -> -0.6086 at (4,2); "Nothing here shows the optimal-shift question is formally closed: Jochemsz-May extended is one strategy"; not independently reviewed |
| Coordinator decision and zero-run task | `origin/lane/smallroot-3cfef2`, `DEC-20261025-fe4f22` and `TASK-20261025-b7e32e`, both added in `dcfbd2b3a4` (2026-10-25) | decision `revise` on IDEA-20260904-39336c; task constraint "Do not reuse 0.8408, 8/9 or the quoted gap as a validated joint bound" and "No claim of optimality outside a specified shift and monomial domain"; zero executions |

Consequence for how this gate states things: **no comparison number from 0.8408, 0.2803 or 8/9 is used as a verdict
input.** The gate for C2 is stated in weighted (beta, gamma1, gamma2) form (section 2.6). The candidate's own line
"eps_avail(4,2) <= 1/2 vs eps_req 8/9, margin <= -0.39" compares a per-block volume ceiling with a per-equation demand
after a conversion the candidate does not write out; I re-derived the conversion (section 2.6) and it holds only under
C1's Lemma A plus H4, so I treat "-0.39" as a prediction, not a result.

Operational notes (disclosure). (a) The scout directory is shared with concurrent runs. My first four `--match` outputs went
to `scout/raw/` and were clobbered or mixed with another run's files (an `n1_p1.txt` of 0 bytes that I did not create was
removed by me with `rm -f` before I realised the directory was shared; it may have been another run's in-progress
output). I discarded those outputs and re-ran everything into `scout/_c2lat_own/`, which is private to this gate. Only
`_c2lat_own/` outputs are pasted below. (b) The Ryan PDF returned HTTP 403; see section 6.

## 2. N1 Atlas collision

Run from /Volumes/SSD990-2/crypto-autoresearcher with LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as specified.
Phrasings 1-3 are the candidate's match_phrasings; phrasing 4 is mine. Raw output follows, unedited.

### 2.1 Raw `python3 tools/lead_atlas.py --match` output

**Phrasing 1**: `averaged initial-ideal ceiling for Howgrave-Graham lattices on chained S_3 trees with kept windowed internal nodes`
```
    8  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    3  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
    3  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    3  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    1  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    1  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

**Phrasing 2**: `can a lattice solve the tree of small S_3 equations used for windowed decompositions`
```
   14  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    9  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    6  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
    6  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    5  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    5  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    4  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    4  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
```

**Phrasing 3**: `kept internal windows welded to block degree: demanded reach 8/9 at (m,w)=(4,2) vs strategy-independent per-block ceiling 1/2`
```
    6  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    6  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    6  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    6  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    6  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    6  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    6  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    6  LEAD-TRF-curve-parameter-transfer-audits     closed_known       Transfer-safety audits of deployed curves: embedding degree, anomaly, twist, subfield/descent, seed provenance
```

**Phrasing 4 (mine)**: `Coppersmith small root Semaev summation polynomial lattice initial ideal Howgrave-Graham admissibility gate`
```
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
   12  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
   11  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   11  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
```

### 2.2 Top-5 hits of every run: what each is, and whether it collides with C2

I opened the YAML of every lead below (mechanism, obstruction, forecloses) and the KRMAP row of every KR hit.

| run | hit (score) | disposition | relation to C2 |
|---|---|---|---|
| 1,2,4 | **LEAD-ICP-coppersmith-smallroot-semaev** (8, 14, 16) | open_next_step | **Same mechanism. The collision.** Section 2.3. |
| 1,2 | LEAD-ICP-lattice-ic-relation-construction (3, 9) | open_blocked | Adjacent. Mechanism: ideal/quaternion lattices, isogeny-adjoint witnesses, "Newton shift certificates for small-window decompositions" (ledger IDEA-20261015-9defe9, which compares dense and Newton-target shifted lattices; the lead's next step names F43/F97/F101 fixtures). Its next_action is a certified-relation pipeline; it asks whether short vectors give relations, not for an upper bound on every lattice. C2's ceiling, if it holds, would bound the Newton-shift sub-lane for the same polynomial family. Does not cover C2. |
| 1 | LEAD-ICB-decomposition-encoding-and-sat (6) | closed_obstructed | Binary PDP via SAT/XOR/enumeration; per-attempt UNSAT cost 2^{alpha l}, alpha ~ m. Different field (F_2^n), different solver. No collision. |
| 1,3 | LEAD-ICE-chained-semaev-dreg-vs-semiregular (6) | open_next_step | Boolean (GF(2)) chained S_3, m = 3, t = 3: Macaulay-rank deficit against a semi-regular null; forecloses include "Hilbert series of chained summation ideal". C2 also uses Hilbert-function data of an ideal of the chained system, but the ideal is J^k over F_p (powers of the S_3 ideal, order-averaged leading ideals), the purpose is the Howgrave-Graham determinant, and the field is F_p. Shares vocabulary only. No collision. |
| 1 | LEAD-ICB-oakley-quintic-tower (3) | open_next_step | Binary n = 5 Gaudry-Diem. No collision. |
| 1 | LEAD-ICP-icperf-writability-boundary (3) | closed_obstructed | Binary ANF writability, +40.8 bits at ECC2K-130 (B4). C2 is prime-field and lattice; it does not touch the ANF. Note the candidate's `bottleneck` text lists B1 only, so no collision. |
| 2 | LEAD-STR-small-cm-disc-nonunit-endo (6), LEAD-TRF-mov-small-embedding-degree (6), KR-RHO-53c89f (5) | closed_obstructed / closed_known / known | Structure and transfer leads; lexical hits on "small". No collision. |
| 3 | KR-IC-f5c584 (6), KR-IC-fbdb61 (6) | known_result | First/last fall degree of Weil descent over F_{2^n}. C2 is not a Groebner solving-degree claim over F_p; the lattice family "never pays that cost" (CLOSURE.md section 0). One caveat in section 7: cuso's optimal-shift routine does a Groebner computation, so C2's own instrument does pay a Groebner preprocessing cost at toy scale. No collision on the mechanism. |
| 3 | LEAD-ICB-prime-degree-algebraic-decomposition (6), LEAD-ICE-descent-closure-degree-at-scale (6) | open_blocked | Binary prime-degree curves, bounded solving degree (B4/B5). No collision. Also in the same score band in run 3: LEAD-ICE-prime-field-semaev-solving-degree (closed_known, B2: beta_work 0.797 / 0.647 against the 0.30 gate) and LEAD-ICP-digit-presentation-solving-degree (open_next_step, digit presentation as a Weil-descent analogue). Both are Groebner-degree routes; C2 is the small-root route, which is the family the program's own CLOSURE.md separates from them. |
| 4 | LEAD-ICE-syzygy-cascade-signatures (12) | open_next_step | F5-signature cascade of chained Semaev systems: are there more non-rewritable low-degree syzygies than generic? C2's Lemma A needs (f_1..f_s, p) to be a regular sequence, i.e. no syzygies beyond Koszul at the p-adic and F_p levels; that is a premise the syzygy lead's own evidence (digit lead: "no syzygy beyond Koszul", EV-PFDR-e67f06) speaks to, but it is not the same question. Adjacent premise, no collision. |
| 4 | LEAD-STR-special-j-ic-semaev (12) | open_next_step | j = 0 / 1728 lose monomials (S_3 support 9 / 10 against 13). Scope note for C2: the ceiling's premise needs the corner monomials x_i^2 x_j^2 of S_3 to survive. In the standard form S_3 = (x1-x2)^2 x3^2 - 2[(x1+x2)(x1x2+a)+2b] x3 + (x1x2-a)^2 - 4b(x1+x2) (recalled formula, and the sibling dossier's sympy check `corner_probe.py`), the three corner coefficients equal 1 for every (a, b), so the premise should survive at special j; I did not recheck by machine. |
| 4 | KR-IC-5a43e5 (14), KR-IC-5931ee (13) | known_result | Semaev summation polynomials (framework); naive Semaev IC over F_p cannot beat generic methods. KR-IC-5a43e5 says novelty "must lie in representation, factor base, elimination or solver". C2's novelty claim lies in the solver-capability bound. KR-IC-5931ee is a negative result about the algorithm class C2 is trying to close further; C2 is consistent with it and does not contradict it. |

### 2.3 The collision: LEAD-ICP-coppersmith-smallroot-semaev (verbatim fields from the YAML)

- `title`: "Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases"
- `mechanism`: "A small-x or windowed factor base turns decomposition into a multivariate small-root problem for S_{m+1}, whose cost is set by lattice reach rather than solving degree. With binary addition trees and kept windowed internal nodes, all-S_3 degree-2 blocks have the largest reach; if reach exceeded the index-calculus demand the decomposition would cost polynomial time per attempt at a factor base large enough to beat rho."
- `next_action.step`: "Compute the provably optimal shift set (Ryan, EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m, w) = (4, 2) system, and the rank-r >= 2 GAP substitution of H-PFDR-3c7d1e, with tools/smallroot_reach.py as the calibrated calculator; then a planted direct-box S_4/S_5 recovery (H-PFDR-621852) at 40-56 bits only if the computed reach clears 8/9."
- `next_action.discriminates`: "Optimal reach >= 0.8889 at (4,2) (or any rank-r GAP cell with positive margin) reopens a concrete lattice decomposition oracle to be measured; optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one and closes the family."
- `best_measured`: "S_3 reach rigorous delta <= 0.10, heuristic 0.12-0.16 (needs 1/2), Probes B/C at 40/56 bits; epsilon margin -0.0481 at (m,w) = (4,2) (JM extended 0.8408 vs demand 8/9)". (This figure is the superseded normalization; see section 1.)
- `forecloses`: Coppersmith small roots of summation polynomials; small-x factor base solved by LLL; windowed addition tree with lattice reduction; symmetric e1 e2 lattice for S_3; rank-r generalized arithmetic progression factor base; lattice-assisted meet-in-the-middle decomposition.
- The row has no `obstruction` block (open lead). Its in-repo closure note `analysis/smallroot-reach/CLOSURE.md` section 5 is scoped to "binary addition trees, m <= 32, any w, any window sizes, any rank-1 GAP factor base ... heuristic JM reach", "claimed nowhere else", and says the rank-r >= 2 GAPs and non-tree strategies are outside scope.

Why this is `advances_lead` and not `duplicate_of_lead`:

1. The candidate's object (the tree with w > 0 kept windowed internal nodes, cell (4,2), the S_3 blocks, the joint ideal) is the lead's object, and its decision (close the cell strategy-independently, or open it) is the lead's `discriminates` clause. So it cannot be called new.
2. The lead's step is a **supply lower-bound computation** for one shift family (the optimum within the Ryan/Feng paradigm). The audit (AUD-4) notes no theorem is known that bounds reach for every strategy. C2's Lemma A route is an **upper bound over every support M and multiplicity t**, derived from Hilbert-function data of the initial ideals of J^k, plus an admissibility test. That is a different kind of statement from "run the optimal-shift tool", and it is the missing half of the discriminator. This is the "sharper next step" case.
3. The lead's `forecloses` phrases cover the mechanism but none of them covers a ceiling uniform over all monomial supports and all multiplicities; the nearest ledger record (IDEA-20260904-39336c) is a supply-side computation (section 4), and the nearest in-flight task (TASK-20261025-b7e32e) explicitly makes "No claim of optimality outside a specified shift and monomial domain".

### 2.4 Secondary leads the candidate touches

- LEAD-ICP-lattice-ic-relation-construction (open_blocked): the Newton-shift sub-lane (IDEA-20261015-9defe9, "certificate-filtered Newton shifts for valid small-window point decompositions") would inherit the same upper bound for small-window S_3/S_4 families. The lead's blocker is `problems/lattice-index-calculus-relation-construction-not-demonstrated.md`.
- LEAD-ICP-construction-normal-form (open_unexamined; mechanism: "A decidable normal form (base, nvars, degree sequence, Groebner signature, oracle) quotients the many proposed prime-field systems into distinct constructions, and instruments ... must show unbiasedness and dynamic range before their nulls count"). The "HG-admissibility gate" half of C2 is an instrument of that kind (a zero-compute filter on proposed small-root systems); it is a natural extra column for that lead's normal form, not a separate lead. Note the gate is only as good as Lemma A, which is unreviewed.

### 2.5 Standing obstructions: verbatim `obstruction.statement` (Scope clause included) and the escape check

**SO-TABLE** (LEAD-ICP-generic-table-decomposition, closed_obstructed, kind theorem):
"Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."
Escape: the premise is "enumerates or table-looks-up factor-base elements". A lattice oracle reads x as an integer in an archimedean window and enumerates nothing; the premise is escaped. The revisit_when ("A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5})") is the condition the lattice route would have to meet, and C2's predicted outcome is that it is not met.

**SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound, closed_obstructed, kind theorem):
"Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." revisit_when: "Never for generic algorithms; only a method that reads the representation (index calculus, transfer) can change the exponent."
Escape: the premise "generic" is escaped because the oracle reads the representation (integer window of x(P)). Not a free escape: C2 itself predicts that the representation-reading oracle is bounded by Lemma A.

**SO-ALGFB** (LEAD-ICP-algebraic-membership-factor-base, closed_obstructed, kind theorem):
"A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
Escape: the "algebraic locus of degree d" premise is escaped (the windows are archimedean inequalities: the implicit-membership class of KN-OPEN-020). **The conservation clause is NOT escaped**; it pins the demand side, as the candidate itself says. SO-ALGFB therefore bounds what C2 may hope for: even a perfect lattice oracle must still meet the conservation-fixed demand, which is the demand inequality of section 2.6.

### 2.6 The gate, stated in weighted (beta, gamma1, gamma2) form (no 0.8408 / 0.2803 / 8/9 input)

Notation: four leaf windows X_i = p^beta, two kept internal nodes u1 = x(P1+P2), u2 = x(P3+P4) with windows p^gamma1, p^gamma2, root x_R known. Three blocks: A = S_3(x1,x2,u1), B = S_3(x3,x4,u2), R = S_3(u1,u2; x_R).

- Demand, sub-rho reference (conditional model; credit: `analysis/smallroot-reach/CLOSURE.md` section 1 for (I) and (II); `readiness-20261025/report.md` (commit `3417ab1c40`, unmerged) for the rho-reference form with tau = 0 and gamma1 = gamma2 = gamma): linear algebra `beta < 1/4`; relation collection `3*beta + gamma1 + gamma2 > 5/2`. The same inequality is also derived in IDEA-20260904-e9675e (eps_required depends only on the number A of bounded auxiliaries).
- Supply ceiling claimed by C2 (conditional on C1's Lemma A, unreviewed; and on H4): `gamma1 + gamma2 < 1/2` from block R alone (two-unknown S_3 with corner u1^2 u2^2), and `2*beta + gamma1 < 1/2`, `2*beta + gamma2 < 1/2` from blocks A and B (three-unknown S_3, order-averaged over the three lex leading monomials x_i^2 x_j^2).
- Compatibility check (my arithmetic, a derivation not a measurement): demand with beta < 1/4 forces `gamma1 + gamma2 > 5/2 - 3*beta > 7/4`; the root-block ceiling forces `gamma1 + gamma2 < 1/2`. The regions are disjoint by at least 5/4 in the coordinate gamma1 + gamma2 (strictly more for beta < 1/4), with no reliance on 0.8408 or 8/9. Under C1's Lemma A and H4 only.
- Conversion to the candidate's epsilon (so its "<= 1/2" can be compared): summing the three block ceilings gives `4*beta + 2*gamma1 + 2*gamma2 < 3/2`, hence `4*beta + gamma1 + gamma2 < 3/2`, i.e. epsilon < 1/2 with E = 3 equations. This conversion holds only under Lemma A and H4. The candidate's "margin <= -0.39" equals 1/2 - 8/9 and is a **prediction under H4**, not an established value.
- **H4 is a real hypothesis.** The joint ideal J = (f_A, f_B, f_R) contains each block's principal ideal, so J^k contains f_R^k and the leading ideal of J^k contains that of f_R^k. The per-block ceiling derived from in(f_R)^k therefore does not transfer to J automatically; a ceiling for J needs in_sigma(J^k) itself (the sibling dossier says as much: Lemma B "needs in_sigma(J^k), which can exceed in_sigma(J)^k when the leading monomials share variables"). Eliminating x1..x4 from f_A, f_B gives a different polynomial in (u1,u2) with different support, which is exactly the lever the joint lattice might exploit. So "closure" is a prediction; the outcome "ratio >= 1 in some direction" is live.

## 3. N2 Known results

### 3.1 Raw `python3 tools/build_frontier_map.py --match` output (same four phrasings, same environment)

**Phrasing 1**
```
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

**Phrasing 2**
```
KR-RHO-53c89f  score=5  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-5931ee  score=4  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-73db3f  score=3  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-cb1c58  score=3  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

**Phrasing 3**
```
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=6  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-0d2021  score=4  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-RHO-1c2928  score=4  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

**Phrasing 4 (mine)**
```
KR-IC-5a43e5  score=14  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=13  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-1fcdbc  score=9  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-889857  score=8  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-73db3f  score=7  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-53c89f  score=5  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
```

### 3.2 Reading of the N2 output

No frontier-map row speaks to lattice or small-root methods. The 15 distinct rows returned across the four runs are Semaev framework and naive-IC negatives (KR-IC-5a43e5, KR-IC-5931ee, KR-IC-1fcdbc), Weil-descent degree results (KR-IC-f5c584, KR-IC-fbdb61, KR-IC-889857, KR-IC-0d2021), factor-base-space rows (KR-IC-73db3f, KR-IC-955fd6, KR-IC-49c882 quasi-subfield polynomials, KR-IC-46d822, KR-IC-791cb7), transfer (KR-RHO-53c89f) and two rho rows (KR-RHO-cb1c58, KR-RHO-1c2928). Phrasing 1 returned "no row shares a term with the query -- this is NOT evidence of novelty" and I do not read it as such. A direct grep of KRMAP.md for Coppersmith, small-root, Howgrave-Graham, lattice, Jochemsz, Ryan, Aono, capacity, initial ideal returned nothing (section 3.3).

What the KR hits do and do not say about C2:

- **KR-IC-5931ee** ("Naive Semaev index calculus over prime fields cannot beat generic methods"; Yokoyama-Yasuda-Takahashi-Kogure under stated statistical assumptions; algebraic factor bases work only at small parameters; McGuire-Mueller Groebner-free variant still worse than rho). This is the negative C2 sits next to. It concerns Groebner/algebraic decomposition cost and does not mention a small-root oracle, so it does not settle C2; it supplies the prior that C2's predicted outcome (closure) is the expected one.
- **KR-IC-5a43e5**: "novelty must lie in representation, factor base, elimination or solver, never in 'use summation polynomials'". C2 does not claim novelty in using summation polynomials.
- **KR-IC-49c882** (quasi-subfield polynomials, SO-QSP) concerns a different representation.

Literature outside KRMAP (this is where the "exactly what is new" statement has to be made; provenance in section 6):

1. For a **fixed** monomial set M and multiplicity t, Ryan's optimal-shift algorithm (EUROCRYPT 2025) already computes the Groebner basis of the ideal and a lattice that "contains all small Howgrave-Graham polynomials" in the integer span (cuso README, retrieved). Hence the determinant of the full lattice I_t ∩ Z[M] is computable exactly by an existing tool; no new mathematics is needed for "what does the best lattice for this (M,t) reach".
2. Leading-term counting as a proof of lattice optimality is in the literature for univariate and Boneh-Durfee-type problems (Aono-Agrawal-Satoh-Watanabe, ePrint 2012/108, retrieved by search; journal version AAECC 29(2) 2017; the optimality there is described by a later paper as holding under a random-lattice heuristic) and, for the univariate case, via capacity theory (Chinburg-Hemenway-Heninger-Scherr, arXiv 1605.08065; KB note KN-LIT-3299, title level). I did not find, in the abstracts and README retrieved, a ceiling uniform over all (M, t) for **systems** of modular polynomials. I could not read the Ryan PDF (HTTP 403), so I cannot rule out that such a statement is in the paper body.
3. Therefore the honest N2 statement is: **the technique is an adaptation of known leading-term/initial-ideal optimality arguments; what is not found in the retrieved sources is its application as a uniform ceiling to the joint ideal of the chained S_3 system.** Novelty status for the mathematics: `unverified`, adaptation. That is enough for `advances_lead` (a next step for a lead), and not enough for `new`.

### 3.3 Raw grep of KRMAP.md for lattice and small-root terms

`grep -n -i -E "coppersmith|small-root|smallroot|howgrave|lattice|jochemsz|ryan|aono|capacity|initial ideal|groebner basis of|hidden number" KRMAP.md` returned **no lines** (exit 1, no output).
The same grep on ATLAS.md returns only lead rows (LEAD-ICP-coppersmith-smallroot-semaev at lines 38 and 183, LEAD-ICP-lattice-ic-relation-construction at 73 and 193, LEAD-RHO-lhw-preprocessing-frontier, LEAD-ICP-representation-subset-sum, LEAD-STR-endo-scalar-action-generic, etc.).

## 4. N3 Ledger

Searched `/Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl` by plain substring match over title, claim, mechanism and statement. Terms: howgrave, leading monomial, corner, ryan, smallroot, small-root, coppersmith, jochemsz, addition tree, regular sequence, sumset, admissib, "initial ideal", "optimal shift", cuso, "associated graded", "kept window". Zero hits for: "initial ideal", "ryan", "optimal shift", "cuso", "hg-admiss", "kept window", "associated graded". Raw output of the filtered run (127 raw ids, 48 after requiring Semaev/decomposition/index-calculus/factor-base/ECDLP vocabulary):

```
127 raw ids; 48 after ECDLP-relevance filter
H-DREG-91be14 proposed ['leading monomial'] | SCOPE. The boolean chained Semaev system at m = 3, t = 3 as built by src/semaev_tree.py and Weil-des
H-ECDLP-1288e1 proposed ['admissib'] | GOAL-ENDO-001 labels every lane by the non-generic resource it must consume, drawing on the R1-R8 ta
H-ECDLP-3165ff proposed ['sumset'] | SCOPE: EXPLICIT reusable precomputations for the target-independent part of a chained point-decompos
H-ECDLP-4b54a2 approved ['small-root'] | SETTING AND CODOMAINS. p is a prime, E/F_p is an ordinary curve of prime order N (N = p up to O(sqrt
H-ECDLP-6c52c0 proposed ['corner'] | Source proposal IDEA-20260806-3b91c7 (RQ-ECDLP-002, class cost-model). THE SOURCE PROPOSAL IS NOT ED
H-ECDLP-78337d specified ['coppersmith'] | Fix the prime-order / twist-order split of one Weierstrass toy before any Weil-restriction index cal
H-ECDLP-7b7398 specified ['coppersmith'] | Fix the multiplicative N^2-th-root uniqueness on F_p^* before any cubical point, division polynomial
H-ECDLP-c3d48a specified ['admissib', 'coppersmith', 'howgrave', 'jochemsz', 'small-root'] | Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
H-ECDLP-cacf58 specified ['coppersmith', 'small-root'] | Fix the ring Z[i] before any Coppersmith small-root solve, Semaev polynomial, Velu map, yield ratio,
H-FROB-66d9ae approved ['sumset'] | CLAIM (structural certificate / column pricing; NO ATTACK). Setting: any Couveignes factor base F wh
H-ICEX-3bccf3 proposed ['regular sequence'] | On frozen Semaev S_3 decomposition systems at toy prime-field scale, the three degree quantities tha
H-ICEX-c273c2 proposed ['sumset'] | THE DECOMPOSITION PROBABILITY IS NOT A PROBABILITY TO BE ESTIMATED. For a factor base V of size B, i
H-PFDR-1b2386 proposed ['sumset'] | (A) WHAT IS ALREADY CLOSED, SO THIS IS NOT MISTAKEN FOR IT. The mean per-target decomposition yield 
H-PFDR-3c7d1e proposed ['smallroot'] | The rank-1 closure of the lattice-describable factor-base family (IDEA-20260903-81a943, analysis/sma
H-SEMAEV-002 supported ['corner'] | For every tested m in {3, 4}, every tested small prime p >= 5, and every tested nonsingular short-We
H-SEMBIN-c59e50 weakened ['corner'] | The exponent constant c = 1.6986 in Semaev 2015's bound 2^{1.6986 sqrt(n ln n)} is carried ENTIRELY 
IDEA-20260723-003 unverified ['admissib'] | After excluding the failed compact z_R constructor and the inconclusive hyperplane-signature cost cl
IDEA-20260723-006 speculative ['corner'] | For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)
IDEA-20260727-003 known ['admissib'] | For prime-field Semaev index calculus with factor base size B = N^beta and decomposition arity m, th
IDEA-20260731-012 adaptation ['sumset'] | Let E/F_p carry a prime-order subgroup G of order N, let F be a factor base of size B = N^beta, and 
IDEA-20260802-003 unverified ['small-root'] | TWO CLAIMS, ONE NEGATIVE AND ONE MEASURED, AND THEY ARE STATED SEPARATELY BECAUSE THEY HAVE DIFFEREN
IDEA-20260806-20f6ab unverified ['admissib'] | THIS RECORD'S HEADLINE IS A NEGATIVE WITH A PRICE TAG. It is filed under the admissibility clause fo
IDEA-20260807-0f49b6 proposed ['coppersmith'] | KN-OPEN-018 states the lattice/ECDLP boundary precisely: lattice reduction enters ECDLP work only vi
IDEA-20260807-6eb96b proposed ['admissib'] | (A) THE DEFECT IN THE OBVIOUS DESIGN. RQ-ICINV-475b5e and DECOMPOSITION.md L1 prescribe comparing wi
IDEA-20260807-7c00e6 proposed ['admissib'] | (A) THE ATTRACTIVE-LOOKING IDEA, STATED AT ITS STRONGEST BEFORE IT IS CLOSED. By T1, an F_p-isogeny 
IDEA-20260808-24c61b proposed ['howgrave'] | Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is 
IDEA-20260808-c31f1c proposed ['small-root'] | The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re
IDEA-20260808-d6d973 proposed ['addition tree'] | Let a decomposition R = P_1 + ... + P_m be organised by a binary addition tree with internal nodes I
IDEA-20260808-fc5e3e proposed ['admissib'] | The published binary-ECDLP Weil-descent complexity is derived by charging a Groebner basis computati
IDEA-20260815-47638d proposed ['admissib'] | GOAL-ICEX-001 is non-executing pending charged SDEG, MONO and RELN packages, and those are each defe
IDEA-20260830-c5c614 proposed ['sumset'] | (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
IDEA-20260903-81a943 unverified ['addition tree', 'jochemsz', 'small-root'] | For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree,
IDEA-20260904-8dccc9 proposed ['small-root', 'smallroot'] | Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
IDEA-20260905-5a1ea2 proposed ['sumset'] | (A) THE OBJECT. For a factor base F of size m inside a prime-order subgroup G of E(F_p), let H_F(x) 
IDEA-20260905-64397d proposed ['admissib'] | For a factor base consisting of complete automorphism orbits, the mean raw tuple count is insufficie
IDEA-20260905-bf8898 proposed ['admissib'] | A divisor-based projective representation may reveal useful structure in a relation locus that survi
IDEA-20260906-f5fc87 proposed ['admissib'] | R3 representation at the decomposition/relation stage. An intermediate resolvent can reduce arithmet
IDEA-20260913-c5f90d proposed ['small-root'] | OBJECT FRAME. Representation: the height-minimal rational representative of the x-coordinate -- for 
IDEA-20260921-457a46 unverified ['admissib'] | A factor base chosen in the quotient coordinate u=x+1/x, together with an exact two-torsion lift rul
IDEA-20260922-f7de2a proposed ['admissib'] | A scalar gap in new_falls is not a mechanism. An off-locus outlier nominated by IDEA-20260922-805a59
IDEA-20260923-9e4b71 proposed ['small-root'] | (A) THE MODEL SHIFT. RQ-ECDLP-78dbc5 asks for fewer stored entries at fixed online cost in a charged
IDEA-20260930-14c753 proposed ['sumset'] | Representation class R1 of RQ-ECDLP-623a32 (x-coordinate). The attack stage is relation collection's
IDEA-20261002-5abffe proposed ['regular sequence'] | KR-IC-0d2021 refines degree-of-regularity / solving-degree predictions for affine semi-regular seque
IDEA-20261002-cad44c proposed ['sumset'] | Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimens
IDEA-20261006-5bfbcf proposed ['sumset'] | Representation R1, attack stage relation yield. On E: y^2 = x^3 + x + 4 over F_61, let F be the four
IDEA-20261006-9e0efb proposed ['admissib'] | Let p be the smallest prime with 11 <= p <= 40 such that F_{p^3} is built on the first monic irreduc
IDEA-20261009-85062c proposed ['coppersmith', 'howgrave', 'small-root'] | The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
IDEA-20261017-2f80c9 proposed ['coppersmith'] | p=m^d-c, pi=alpha-m, digit box D_H (unique Babai lifts). (A) Sigma_rot={x->m*x} is coordinate-depend
```

Hits that may be the same object as C2 (id, status, first 100 characters of claim or statement, as stored in the index):

| id | status | claim (100 chars) |
|---|---|---|
| IDEA-20260904-39336c | proposed | The closure of IDEA-20260903-81a943 rests on one supply number, eps_available(S_3) = 0.8408, the Joc |
| IDEA-20260904-8dccc9 | proposed | Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t |
| IDEA-20260903-81a943 | unverified | For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree, |
| IDEA-20260808-486ae2 | proposed | (A) CLASSIFICATION. IDEA-20260801-021 / IDEA-20260803-e2f5bd bound any factor base cut out by a targ |
| IDEA-20260808-d6d973 | proposed | Let a decomposition R = P_1 + ... + P_m be organised by a binary addition tree with internal nodes I |
| IDEA-20260904-e9675e | proposed | (A) THE AUXILIARY-COUNT LAW. Let a decomposition test for "P_1 + ... + P_m = R with x(P_k) in a wind |
| H-PFDR-3c7d1e | proposed | The rank-1 closure of the lattice-describable factor-base family (IDEA-20260903-81a943, analysis/sma |
| H-ECDLP-c3d48a | specified | Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham  |
| H-PFDR-621852 | proposed | On the frozen direct-box S4/S5 planted law and actual modular JM/BKZ pipeline, test source beta thre |
| H-PFDR-6b8c0f | specified | Fix the exact window-shape identities of IDEA-20260904-8dccc9 before any re-parametrization. Stage 0 |
| H-ECDLP-4b54a2 | approved | SETTING AND CODOMAINS. p is a prime, E/F_p is an ordinary curve of prime order N (N = p up to O(sqrt |
| IDEA-20260723-006 | speculative | For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m) |
| IDEA-20261009-85062c | proposed | The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F |
| IDEA-20261015-9defe9 | proposed | R1 relation-solving comparison: dense versus Newton-target shifted lattices must yield achieved norm |
| IDEA-20260808-c31f1c | proposed | The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re |
| IDEA-20260807-0f49b6 | proposed | KN-OPEN-018 states the lattice/ECDLP boundary precisely: lattice reduction enters ECDLP work only vi |

I opened exactly three full records by exact path (proposals only; never listed `ledger/proposals/`): IDEA-20260904-39336c, IDEA-20260808-d6d973, IDEA-20260904-e9675e. The other rows above are index-level reads only (so statements about them are limited to what the index fields say).

Decisions:

- **IDEA-20260904-39336c (proposed; recommended_priority high; "revise" per DEC-20261025-fe4f22 on the unmerged lane branch).** Closest ledger object. Its claim: run Ryan's optimal shifts and the Feng et al. sumset algorithm on the S_3 polytope **and on the joint three-equation system at (m,w) = (4,2)**; falsification: "eps_opt(S_3) and eps_opt(joint) are both <= 0.8889. The closure survives ... upgraded from 'one strategy's value' to 'the paradigm's optimum for this polytope'"; it also pre-registers "eps_opt(joint) equals eps_opt(per-block) within 1e-3 ... the per-block shortcut is tight". Overlap with C2: (i) the same cell and the same joint-versus-per-block question (its F3 is C2's H4); (ii) C2's "cuso/HNF cross-check" arm is its Stage 1. Difference: it is a **supply-side computation within the optimal-shift paradigm**, with a heuristic root-extraction assumption H1; it contains no ceiling uniform in (M,t) and no initial-ideal argument (the record states no citation of any upper-bound result). Its own limit: "'Provably optimal shift polynomials' is optimality within a paradigm". C2 would supply the analytic counterpart. Its own honest prior: ~0.12 that eps_opt clears the demand.
- **IDEA-20260808-d6d973 (proposed).** Elimination-yield duality: keeping an internal sum as a windowed variable costs (B'/p) in yield, eliminating it doubles the degree; "A solver insensitive to degree would escape it entirely; none is known." This is the "weld" that C2's title calls "kept internal windows welded to block degree". Already recorded; credit to this record and to CLOSURE.md section 2.
- **IDEA-20260904-e9675e (proposed).** Proves that eps_required depends only on the number A of bounded auxiliaries: eps_required = (A + 1/2 + beta)/E, reproducing the closure's `(w + 1/2 + 1/(2(m-1)))/(w+1)` at A = w, E = w+1. So C2's "conservation clause ... fixes eps_req(m,w)" is already derived there; not new.
- **IDEA-20260723-006 (speculative; index-level only).** "Corner-coefficient induction and exceptional-target saturation theorem": the Semaev Newton polytope is the full box outside an O(m)-sized exceptional target set. This is the ledger precursor of C1/C2's premise that the corner monomials appear with coefficient 1; credit it. It says nothing about HG lattices.
- **IDEA-20260903-81a943 / analysis/smallroot-reach/CLOSURE.md, IDEA-20260904-8dccc9, IDEA-20260808-486ae2, IDEA-20260808-c31f1c, H-PFDR-3c7d1e, H-ECDLP-c3d48a, H-PFDR-6b8c0f**: the closure, its (m,w) = (4,2) setting, the rank-r digit re-parametrization, the Stage-0 identity records. All supply/demand bookkeeping for the same cell; none contains an upper bound uniform in (M,t).
- **H-ECDLP-4b54a2 (approved; index-level only; not opened because of the three-record cap).** "Preprocessing re-reading of the windowed small-root family at (m = 3, w = 1): does the JOINT small-root region of the coupled summation system {S_3(x1, x2, y), ...". Same family and the same supply object (the joint small-root region of coupled S_3 equations) at the (3,1) tree, which is the tree C2's `first_step` uses for its cuso/HNF achievability check; the demand model differs (preprocessing). Its experiment EXP-ECDLP-64fa3d has no run yet (per CORRECTION.md). **C2's (3,1) arm may therefore duplicate an approved, unrun experiment.** I could not open the record because of the three-record cap, so I cannot say what ceiling statements it contains; its pre-registered predictions (per CORRECTION.md) calibrate the epsilon convention, not a ceiling. Unresolved: the Coordinator must reconcile it before any C2 contract.
- **IDEA-20261015-9defe9, IDEA-20261009-85062c**: Newton-shift certificates and an empirical S_3 recovery threshold; achievability-side objects.
- **H-PFDR-621852**: planted S4/S5 recovery with actual JM/BKZ pipeline; the follow-up the lead's `next_action` gates on the computed reach.

N3 conclusion: no ledger record states an upper bound on reach that is uniform in the monomial set and multiplicity, or an initial-ideal/Hilbert-function argument for the joint ideal. IDEA-20260904-39336c is the same decision with a different instrument, and the unmerged lane (DEC-20261025-fe4f22, TASK-20261025-b7e32e) is already working its applicability design with zero executions. So: a sharper next step on an open lead, with a duplicate sub-arm.

## 5. N4 Notation change (C2 is an IC / factor-base / representation candidate)

**The (representation, operation set) pair.** Representation R1: the integer representative of x(P) in [0,p), with a window p^beta on each of the four leaves and p^gamma_v on each kept internal partial sum, plus the known root x_R. Operation set Sigma: translation by factor-base elements, i.e. determinism only under translation by H = {P : x(P) in the window}, a proper subset of G (a partial action). Oracle: the joint Howgrave-Graham lattice on the ideal (f_A, f_B, f_R, p)^t. This is the same pair as the lead's and C1's; C2 adds no new representation or operation. Its contribution would be an instrument on the oracle component.

Against each recorded rigidity result:

- **IDEA-20260806-c5d183** (projection that propagates deterministically under the FULL translation action is constant or injective; every non-trivial object is Class I partial-action, Class II branching, or Class III coordinate-dependent). C2's pair is Class I (translation by H only) and Class III (it reads the integer representative, not the group element). The theorem constrains projections of G; C2 constrains a class of algorithms operating on a window representation. C2 neither restates the theorem in new symbols nor contradicts it, and the theorem has no consequence for an archimedean-window lattice oracle. Placement in Class I means C2 is not an escape from the trichotomy: its cost axis is the coverage/collision split already fixed by KN-FIND-007, which is exactly the conservation clause the candidate says it does not escape.
- **IDEA-20260901-863e36** (propagation is a property of a projection paired with an operation group; block systems of Gamma, Gamma a subgroup of (Z/n)^*). C2's operation set is translation by H, not a multiplicative Gamma-action; there is no orbit or quotient being canonicalised. The classification (C1) of that record has nothing to say about the window pair. Not the same object.
- **KN-OPEN-020** (universal algebraic-factor-base no-go; the bounded-degree theorem is a "scoped negative"; open class = "high-degree interpolation descriptions, multiple constructible predicates, target-dependent descriptions, and implicit membership or source-recovery algorithms"). The window is implicit, archimedean membership, so C2 lives in the open class. If Lemma A plus H4 held, C2 would be one more scoped negative inside that open class (lattice-describable windows with polynomial-dimension HG lattices). It does not claim the universal statement.
- **KN-FIND-ffe1df** (Wagner k-tree, "sum-compatible filters"; Theorem A', Theorem C: a tree must invert its combining rule in each argument, so the rule is a quasigroup, and an exact sum-compatible quasigroup is a group, impossible for prime order). Table row "A, B -- `x`-based intervals and bit windows only: closed at level 1, conditional on (H1')". Kept windowed internal nodes are exactly x-interval filters on partial sums, so the finding is adjacent. C2 does not use Theorem C and does not contradict Theorem A'. It **depends on** the uniform-window yield assumption (B'/p)^{|S|} of IDEA-20260808-d6d973, i.e. on there being no filtering gain; ffe1df supports that at level 1 only, conditional on (H1') (which KN-LIT-f6de4b finds largely untraced to a primary source), and says the bound "does not transfer as stated" to levels >= 2. At (m,w) = (4,2) the kept nodes are level 1 and the root merge is level 2, so the independence assumption at the root is not covered by ffe1df. This affects the demand side (conservation), not the supply ceiling.

Conclusion: C2's pair is not a recorded rigidity result in new notation. It is a recorded pair (the lead's) with a new instrument aimed at its oracle component. The "partial-action" trichotomy class stated in the candidate is correct.

## 6. Citations and provenance

| citation | provenance | what was actually read this session |
|---|---|---|
| K. Ryan, "Solving Multivariate Coppersmith Problems with Known Moduli", EUROCRYPT 2025, ePrint 2024/1577 | **retrieved** (abstract page and cuso README) | eprint.iacr.org/2024/1577 abstract fetched (title, sole author, three strategies; Groebner-basis strategy "provably computes an optimal set of shift polynomials"; improved asymptotic bounds on three problems; methods "heuristic"). github.com/keeganryan/cuso README fetched: shift polynomials have "integer linear spans that contain all small Howgrave-Graham polynomials"; symbolic strategies "heuristically compute asymptotic bounds"; dependencies SageMath, flatter, msolve. The PDF returned HTTP 403, so **no theorem statement, bound, or applicability condition was read from the paper body**. The abstract states no upper bound on the achievable Coppersmith bound. |
| Aono, Agrawal, Satoh, Watanabe, "On the optimality of lattices for the Coppersmith technique" | ePrint 2012/108 and journal version AAECC 29(2), 2017, pp. 169-195, DOI 10.1007/s00200-017-0336-9: **retrieved by search** (listing and snippets, not the paper). **ACISP 2012 venue: recalled, not confirmed** (the search did not confirm it). | Optimality for univariate and Boneh-Durfee; a 2016 follow-up describes it as optimal under a random-lattice heuristic. |
| Chinburg, Hemenway, Heninger, Scherr, capacity theory, arXiv 1605.08065 | **retrieved by search** (listing) and in the KB at title level (KN-LIT-3299) | univariate only |
| Matsumura, Commutative Ring Theory, Th. 16.2 (regular sequence gives gr_I(A) = (A/I)[X_1..X_r]) | **recalled** | not checked here; Lemma A also needs (p, f_1, f_2, f_3) to be a regular sequence in Z[u], which is a per-prime premise for the actual S_3 system and is **not verified** by anything I ran |
| Feng, Luo, Chen, Nitaj, Pan, ePrint 2024/1330 (sumset bounds) | **recalled** from the lead row and IDEA-20260904-39336c | not retrieved in this gate |
| Lemma A, Lemma B, corner lemma (C1), and "3-unknown S_3 block needs vol < 1/2" | internal, from the sibling scout dossier `scout/scout-lattice-smallroot.md` | I re-derived the order-averaging step for the 3-unknown block (minimum of an average, q_ij proportional to omega_i + omega_j) and it gives vol < 1/2 as stated; I did **not** independently review the proof of Lemma A (the index-count step) or the regular-sequence step. Unreviewed; no machine check of the dossier's numerical probes was repeated here |

The load-bearing citation for the candidate is Ryan 2024/1577. It is marked retrieved at abstract and README depth only.

## 7. What is new, what is not, and what the verdict does not say

Not new (credit where it belongs):

1. The mechanism, the (4,2) cell and the discriminator: the lead and CLOSURE.md.
2. "Kept internal windows welded to block degree": CLOSURE.md section 2 and IDEA-20260808-d6d973.
3. eps_req(m,w) = (w + 1/2 + 1/(2(m-1)))/(w+1): CLOSURE.md section 1, re-derived in IDEA-20260904-e9675e.
4. The demand inequality `3beta + gamma1 + gamma2 > 5/2` with `beta < 1/4`: the readiness report (`3417ab1c40`, unmerged) states the rho-reference conditions with gamma1 = gamma2 and tau = 0. That report also says its finite regions' disjointness from the sub-rho region is "not an impossibility claim about improved shifts"; C2 is the attempt at that impossibility claim, so credit the report and do not present the inequality as C2's.
5. The cuso/HNF achievability cross-check: IDEA-20260904-39336c Stage 1 and TASK-20261025-b7e32e (zero-run applicability, same joint weighted system). Recommend C2 drop this arm or share that harness.
6. The machinery: Ryan's optimal shift set is computed from a Groebner basis of the corresponding ideal (abstract and cuso README), and cuso's `optimal.py` calls `J.groebner_basis()` (readiness report, source inspection). So for a fixed (M,t) the exact determinant of I_t ∩ Z[M] is already obtainable. C2's own first step (Groebner bases of J^k on the (3,1) and (4,2) trees at p ~ 2^16) is the same kind of preprocessing, so the lattice route does pay a Groebner cost at toy scale; "the lattice family never pays that cost" in CLOSURE.md refers to solving degree over F_p, not to this preprocessing.
7. Lemma A and the corner premise: from the sibling candidate C1 (unreviewed); the corner-coefficient fact has a ledger precursor in IDEA-20260723-006.

New, narrowly: a ceiling **uniform over every support M and every multiplicity t**, obtained from order-averaged initial ideals of J^k for the joint ideal J of the chained S_3 system, which would turn the lane's task (optimum within a specified shift and monomial domain) into a domain-free statement within polynomial-dimension HG lattices of the form I_t ∩ Z[M]; plus a zero-compute admissibility filter for proposed small-root systems.

Conditionals the verdict leaves intact:

- **Lemma A is unreviewed.** C2 inherits C1's status. Per AGENTS rule 12 (as cited by CORRECTION.md) a result contradicting a closure needs independent review; a result that strengthens one is still a theorem-shaped claim and should be reviewed before any lead is closed on it.
- **H4** (per-block ceilings stay binding in the joint ideal) is not implied by anything proved; section 2.6 explains why a joint lattice can only do at least as well as a per-block one.
- **H1** (determinant-level, Gaussian-heuristic statement; structurally short vectors with no determinant reason are not excluded). The lemma bounds the determinant criterion, not every conceivable short-vector structure. Auxiliary ideals larger than (J,p)^t (elements of degree >= p) and lattices of superpolynomial dimension are outside the lemma's scope as the dossier itself states.
- **Regularity** of (p, f_A, f_B, f_R) in Z[u] is a per-prime premise.
- **"Predicted gain 0 / closure"** is a prediction under H4. The opposite outcome (ratio >= 1 in some direction) is live and is what the candidate says it would pursue.
- A closure on this route would be scoped to polynomial-dimension HG lattices of the stated form and to binary addition trees; it would not touch non-tree presentations (IDEA-20260904-e9675e's divisor presentation), non-lattice solvers, or the atlas's other standing obstructions.
- Decision value: if the lane's cuso symbolic bound for the joint system lands far below the demand, C2's contribution shrinks to "strategy-independent proof of a result the computation already shows"; if it lands near the demand, C2's ceiling is the discriminator. Nothing is lost by sequencing C2 after that computation.

## 8. Recommended narrowing (for whoever drafts the C2 contract)

1. Treat C2 as the upper-bound half of LEAD-ICP-coppersmith-smallroot-semaev's discriminator and file it as a next-step refinement of that lead and of IDEA-20260904-39336c (not as a new lead).
2. Review Lemma A first (C1 dependency): exact dim V_k against the averaged leading-monomial count on the single S_3 block at t <= 3, reproduced independently.
3. Primary measurement: dim V_k(J) = dim (J^k mod p) ∩ F_p[M] for the joint ideal on the finite union-support fixtures of the unmerged audit (31 / 382 / 2591 columns), against the order-averaged bound. This is the direct test of H4 and of IDEA-20260904-39336c's F3.
4. Drop the cuso/HNF achievability arm, or reuse the pinned cuso adapter of TASK-20261025-b7e32e. The (3,1)-tree part of that arm may also duplicate the approved, unrun H-ECDLP-4b54a2 / EXP-ECDLP-64fa3d (not opened here); reconcile with it first.
5. State every outcome in the weighted (beta, gamma1, gamma2) region of section 2.6. Do not quote 0.8408, 0.2803 or 8/9 as comparison values.
6. Add the admissibility gate as a column to LEAD-ICP-construction-normal-form only after item 2 passes.
