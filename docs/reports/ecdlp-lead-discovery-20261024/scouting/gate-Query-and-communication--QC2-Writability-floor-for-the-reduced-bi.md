# Gate record: QC2 Writability floor for the reduced binary-digit presentation (Query and communication field)

Run date: 2026-10-25. Raw --match outputs pasted verbatim below.

## N1 raw lead_atlas --match outputs

### python3 tools/lead_atlas.py --match "multilinear support of the base-2 digit presentation of the prime-field Semaev system as a writability floor"
```
   25  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   11  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   11  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   10  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    9  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    8  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    8  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    8  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
```

### python3 tools/lead_atlas.py --match "writing down the binary-digit Semaev polynomial over a prime field costs more than rho"
```
   16  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   13  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   13  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
   11  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
   10  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   10  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
   10  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
```

### python3 tools/lead_atlas.py --match "digit presentation ANF exceeds the whole per-decomposition rho budget before any solver runs"
```
   10  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    9  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    8  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
    8  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    7  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    7  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    7  LEAD-RHO-kangaroo-interval                   closed_dominated   Kangaroo / lambda (van Oorschot-Wiener, Gaudry-Schost) as a full-group ECDLP solver
```

### python3 tools/lead_atlas.py --match "digit presentation solving degree"
```
   17  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   14  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   12  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   11  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   10  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    8  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    7  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
```
## N2 raw build_frontier_map --match outputs
### python3 tools/build_frontier_map.py --match "multilinear support of the base-2 digit presentation of the prime-field Semaev system as a writability floor"
```
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-1c2928  score=3  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-33f837  score=3  [record/reported]  Prime-field ECDLP records
    sources: KN-LIT-095, KN-LIT-a714d3, KN-LIT-24b9c7, KN-LIT-ff80da
KR-RHO-cd0049  score=3  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-8b9daa  score=1  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-9e610d  score=1  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
```
### python3 tools/build_frontier_map.py --match "writing down the binary-digit Semaev polynomial over a prime field costs more than rho"
```
KR-IC-5931ee  score=16  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-9e610d  score=10  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-cd0049  score=10  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=9  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-791cb7  score=9  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-889857  score=9  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-a4dd54  score=8  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
```
### python3 tools/build_frontier_map.py --match "digit presentation ANF exceeds the whole per-decomposition rho budget before any solver runs"
```
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-93979e  score=6  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
KR-RHO-e7f98e  score=6  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```
### python3 tools/build_frontier_map.py --match "multilinear representation uniqueness Nisan-Szegedy degree of Boolean functions"
```
KR-IC-e847d1  score=6  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=6  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-5b1c0a  score=5  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
KR-IC-0d2021  score=4  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
```

## N1 reading of the top-5 hits of every run (lead YAMLs opened; mechanism + obstruction + forecloses)

Run 1 (multilinear support / writability floor): LEAD-ICP-digit-presentation-solving-degree (25), LEAD-ICE-chained-semaev-dreg-vs-semiregular (11), LEAD-ICE-curve-presentation-invariance (11), LEAD-ICP-icperf-writability-boundary (10), LEAD-ICE-prime-field-semaev-solving-degree (9).
Run 2 (writing down the binary-digit Semaev polynomial > rho): KR-IC-5931ee (16), LEAD-ICB-quasi-subfield-polynomials (13), LEAD-ICP-digit-presentation-solving-degree (13), LEAD-RHO-matched-rho-calibration (13), LEAD-STR-special-j-ic-semaev (11).
Run 3 (ANF exceeds the per-decomposition rho budget): LEAD-ICE-generic-oracle-arity-cost-floor (10), LEAD-ICP-digit-presentation-solving-degree (10), LEAD-ICP-icperf-writability-boundary (9), LEAD-STR-automorphism-quotient-rho (8), LEAD-STR-isogeny-class-generic-invariance (8).
Run 4 (own phrasing, "digit presentation solving degree"): LEAD-ICP-digit-presentation-solving-degree (17), LEAD-ICE-curve-presentation-invariance (14), KR-IC-fbdb61 (12), LEAD-ICE-prime-field-semaev-solving-degree (11), LEAD-ICE-descent-closure-degree-at-scale (10).

Per-hit reading (what the hit's mechanism is, and whether the candidate's mechanism is covered by its forecloses):

1. LEAD-ICP-digit-presentation-solving-degree, open_next_step (the lead the candidate names; top hit in 3 of 4 runs). Mechanism: write each unknown in s bounded digits as an F_p analogue of Weil descent and ask whether the Semaev system's solving degree is bounded in p (first/last fall, staircase, carry circuits). No obstruction field (open). Its forecloses are all about fall degrees, staircases, semigroup presentations and carry circuits; none says "support/size of the written generator" or "writability". Its evidence list does carry EV-PFDR-f71d7f (note: "deg S_{m+1} = m 2^{m-1} voids the bounded-LFD conditional cost claim") and EV-PFDR-1394a4, but the lead row's best_measured and next_action never mention the writability observation O-3 that sits inside EV-PFDR-f71d7f (see N3). Disposition for QC2: same presentation, same lane, different closure kind (cost model of the written generator, solver-independent) -> candidate is a next step for this OPEN lead, not a new lead.
2. LEAD-ICP-icperf-writability-boundary, closed_obstructed, kind cost_model. Mechanism: the descended (Weil-restricted) binary system, unchained or chained, must be written; its ANF exceeds the whole per-decomposition rho budget (+40.8 bits at ECC2K-130). Obstruction Scope: "standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]". QC2 is the same obstruction KIND on a different object (prime-field digit presentation); the lead's Scope clause excludes prime fields, so QC2 neither falls under it nor answers it. Revisit_when ("a representation whose written size plus solve fits under the rho budget") is the opposite direction of QC2 (QC2 predicts no such fit). Not a duplicate by scope; it is the precedent for the cost-model closure form QC2 proposes.
3. LEAD-ICE-prime-field-semaev-solving-degree, closed_known (KR-IC-5931ee), kind literature: beta_work 0.797 / 0.647 vs 0.30 gate on the x-coordinate (interval/random/subgroup) presentations. Its revisit_when names exactly the digit-map presentation ("a prime-field factor base whose membership equation has bounded degree independent of p (the base-d digit-map / PFDR descent, IDEA-20260830-84cdb7) produces a measured solving degree that stays flat across >= 3 field sizes"). QC2 does not measure a solving degree, so it does not trigger or answer that revisit condition; it is a different route to the same closure.
4. LEAD-ICE-chained-semaev-dreg-vs-semiregular, open_next_step: Boolean chained S_3 (binary) d_reg vs semi-regular null. Different field (binary), different invariant (degree of regularity). Forecloses do not cover writability. No collision.
5. LEAD-ICE-curve-presentation-invariance, open_next_step: transport by Velu isogeny / model change / special j to an easier Semaev presentation (fall degree, yield). Different presentation axis. No collision.
6. LEAD-ICB-quasi-subfield-polynomials, closed_obstructed (theorem, Euler-Petit beta >= 3/4): binary QSP bases. Different object. No collision.
7. LEAD-RHO-matched-rho-calibration, open_next_step: denominator calibration of the rho reference. QC2 uses rho as the comparison scale (0.5*(log2 N + log2(pi/4))); the calibration lead does not touch writability. No collision, only a shared denominator.
8. LEAD-STR-special-j-ic-semaev, open_next_step: j = 0/1728 sparser S_3 (support 9/10 vs 13). Relevant to the support of the generic generator only at special j; QC2 is stated for generic curves. No collision; note QC2's support floor would need a separate special-j statement (special j has fewer monomials in S_3, so a sparse-S_3 effect could in principle lower the floor at special j; QC2 does not claim anything there).
9. LEAD-ICE-generic-oracle-arity-cost-floor, closed_obstructed, cost_model: enumerative/MITM/free decomposition oracles cannot reach rho at any arity; "the store any sub-rho cell needs costs as much as rho's whole walk". Scope: "oracles that do not read curve coordinates algebraically". QC2's object reads coordinates algebraically, so it is outside that Scope. Observation (heuristic H-a, not established): in the high-arity band where only H4w carries the closure, the written support is a fixed fraction (>= 2^-80 .. 2^-302) of the digit cube of size B^m = N^{m/(m+1)}; that is a table of the size SO-TABLE / this lead already price, reached by a dense expansion rather than an oracle. This is why the high-arity part of QC2 carries little information beyond "a dense polynomial in the digit cube is as large as the cube".
10. LEAD-STR-automorphism-quotient-rho, LEAD-STR-isogeny-class-generic-invariance (closed): rho-side constants and isogeny invariance. Different object. No collision.
11. LEAD-ICE-descent-closure-degree-at-scale, open_blocked: binary closure degree at scale. Different field and invariant. No collision.
12. LEAD-ICP-algebraic-membership-factor-base (the SO-ALGFB row, not a top-5 hit but the standing obstruction QC2 claims to touch), closed_obstructed, theorem. Statement (verbatim): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: ... Scope: prime-order E/F_p, any base of size B." QC2 is not an escape from this row (it predicts 0 bits and a closure), and the row's revisit_when (KN-OPEN-020 answered positively) is not triggered by a cost floor on one presentation. QC2's sentence "QC2 closes that escape for the expanded reduced presentation using support rather than degree" overstates: it is a cost-model floor (conditional on H2 and H4w), not a theorem about the implicit-membership class, and it is scoped to the expanded presentation.

N1 conclusion. No lead's forecloses phrase covers the candidate as a whole, so it is not a pure duplicate of a closed lead. But the part of the candidate that is rigorous (Floor A) is a recorded internal finding (N3), and the lead it targets is open, so the candidate is a sharper/alternative next step for an open lead rather than a new lead.

## N2 known results (literature map)

Rows returned (raw output above). Read the relevant KRMAP rows:
- KR-IC-5931ee known_negative/proven, "Naive Semaev index calculus over prime fields cannot beat generic methods" (Yokoyama-Yasuda-Takahashi-Kogure under stated statistical assumptions; algebraic factor bases work only at small parameters; McGuire-Mueller Gröbner-free variant still worse than rho). The match is on the direction of the conclusion (prime-field Semaev IC does not beat generic), not on the object. The KR proof concerns naive x-coordinate Semaev systems under statistical assumptions; the digit presentation of IDEA-20260830-84cdb7 is not among the KR's cited constructions. So the KR does not by itself settle QC2's object. What QC2 would add relative to the KR is only a presentation-specific cost floor whose predicted outcome (no gain) agrees with the KR's direction.
- KR-IC-5a43e5 known_mechanism/proven, Semaev summation polynomials; degree 2^{m-2} per variable; the row says "novelty must lie in representation, factor base, elimination or solver, never in 'use summation polynomials'". QC2's novelty claim would have to sit in "representation" (the digit presentation), which is the program's own construct, so this row neither covers nor excludes QC2.
- KR-IC-fbdb61, KR-IC-f5c584, KR-IC-889857 (last/first fall degree, binary Weil descent): solver-side invariants, not the written size. KR-IC-1fcdbc (char-2 summation algorithms far slower than rho). No KR row states a support/ANF-size floor for any presentation, and no KR row mentions multilinear-representation uniqueness.
- Literature for the external ingredient. Nisan, Szegedy, "On the degree of Boolean functions as real polynomials", Computational Complexity 4 (1994) 301-313: bibliographic record RETRIEVED this session (WebSearch confirmed title, journal, volume, pages). The specific statement the candidate uses (uniqueness of the multilinear representation) was NOT located: the PDF copy found (web.vu.lt/mif/s.jukna/boolean/Nisan-Szegedy.pdf) is image/Flate-compressed and WebFetch could not read it. So "the uniqueness lemma is in this paper" stays recalled. Mathematically it is only Moebius inversion on the cube (over F_p as over R), a textbook fact; nothing in the cited paper is used beyond it. The program already uses this fact: KN-FIND-0618ab states the block-multigrading was "checked directly at (m, s) = (2,2), (2,3), (2,5), (3,4) by Moebius inversion over the Boolean cube", and H-PFDR-4148b8 works in the function ring B = F_p[a]/(a^2 - a). So the external ingredient is not new to the program.
- Recalled (not verified, not load-bearing): the practical infeasibility of writing out S_n for n >= 6 symbolically is folklore in the Semaev/Gaudry/Faugere literature; I did not look it up.
N2 conclusion: no KR row is the same object; the nearest (KR-IC-5931ee) agrees with QC2's predicted direction. Not known_result as a whole; the Floor-A content is an internal finding, not a literature result.

## N3 ledger and repository dedup

Index greps (proposals.jsonl 2678 rows, hypotheses.jsonl 2131 rows) on: writab, multilinear, top.form, Nisan|Szegedy, Moebius, support size/floor, monomial count, digit+(support|size|write), "descended ANF|ANF size|ANF exceeds", "block.degree", "rho budget" within PFDR/ICPERF. No row matches "Nisan|Szegedy" in the IC lane and no row matches "descended ANF|ANF size|block.degree". Hits that may be the same or adjacent object (id + first 100 chars of title):
- IDEA-20260903-e1e38b | THE p-ARY ALGEBRAIC IMMUNITY OF THE DIGIT-SUBSTITUTED SEMAEV TOP FORM IS 1/m OF THE GENERIC VALUE AN
- H-PFDR-4148b8 | The first fall degree of the d = 2 digit-presented Semaev system is a closed form in (m, s) alone --  [OPENED IN FULL]
- IDEA-20260903-751062 | THE ONE RECORDED PRIME-FIELD EARLY FALL IS A CLOSED-FORM MEMBERSHIP ARTIFACT AND ITS OWN ARCHIVE ALR
- H-PFDR-e02f3b | The one recorded prime-field early fall (EXP-ALPF-011 e-ring, quoted by EV-ALPF-001 and RQ-PFDR-ae2f
- IDEA-20260903-cf63ad / H-PFDR-9aadc0 | THE PRIME-FIELD DIGIT TWIN OF THE BINARY CHAINED SEMAEV SYSTEM HAS NEITHER INGREDIENT OF THE EXHIBIT...
- H-PFDR-c88f14 | No bounded-last-fall-degree theorem transfers to the prime-field digit presentation (the Frobenius c
- IDEA-20260830-84cdb7 | PRIME FIELDS DO HAVE THE MISSING INGREDIENT AND IT IS THE BASE-d DIGIT MAP - writing x = a_0 + a_1 d (the presentation itself)
- IDEA-20260808-afe4ce | The prime-field mirror of the last-fall-degree theorem is a FLOOR, not a ceiling - for any factor ba (d_lf >= B for set-theoretic descriptions)
- IDEA-20260926-1ddce2 | THE CHAINED-S_3 ORACLE AT m = 5, 6 IS WRITABLE ON ECC2K-130 WHERE THE UNCHAINED S_{m+1} IS NOT: the (binary writability, chained)

Records opened in full (budget 3): H-PFDR-4148b8 (hypothesis), EV-PFDR-f71d7f (evidence; sections O-1..O-9 and the findings block, lines 1-60, 150-215, 380-445). The third slot was not used. Disclosure: I also opened non-ledger artifacts that those records point to, which are not "ledger/proposals" records: knowledge/findings/KN-FIND-0618ab.md, knowledge/open-problems/KN-OPEN-02200b.md, knowledge/open-problems/KN-OPEN-020.md, knowledge/findings/KN-FIND-ffe1df.md (Theorem C section), and coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/rt_support_size.py. Process slip, disclosed: once I ran `ls ledger/proposals | grep -E "<two ids>"` to locate two IDEA files; it printed only the two matching filenames, and I did not list or read the directory otherwise.

DECISIVE FINDING (same object, already recorded). The candidate's Floor A is the red team's derivation R4 of TASK-20260904-6681da, recorded as:
- rt_support_size.py: "#terms(S~) >= binom(s, 2^(m-1))^m, a lower bound on the cost of WRITING DOWN the generator, hence on the cost of building one row of the degree-D_0 Macaulay matrix"; the argument is the candidate's own ("no two terms share a monomial" is the uniqueness of the reduced form).
- EV-PFDR-f71d7f observation O-3 (R4, "unconditional on HEUR-001, on D_0 and on omega"): "The generator cannot be written down at the cells that carry the claim. Its top-degree part alone has binom(s, 2^{m-1})^m nonzero terms = 2^221.3 at (256, m 5, D_0 4, omega 2), exceeding that cell's entire claimed total of 2^108.76 by 2^112.5 ... marginal at m = 4 (-0.57)".
- KN-FIND-0618ab bullet 4: "Independently of all of the above, the generator cannot be written down at large m. Its top-degree part alone has binom(s, 2^(m-1))^m nonzero terms = 2^221.3 at a 256-bit, m = 5 parameter set", and the same finding states the floor "applies to every presentation keeping S_{m+1} as a generator, at every base d".
I recomputed 5*log2(C(54,16)) = 221.3, matching. The candidate's own self_kill_risk concedes the repeat.

What the candidate adds beyond that record (and only this):
(i) comparison against rho for every (m, s, W, log2 N) instead of against one cost-table cell's claimed total (qc2_floorA_by_m.out / qc2_digit_writability_v2.out; I re-ran both; the floor-A table reproduces byte-for-byte and the headline margins +29.4/+31.2/+34.3/+32.7 at W = 2 reproduce);
(ii) Floor B (H4) and H4w: a conjecture that most reduced monomials of block degree <= K are present, needed for every cell with m >= 6 at 128/256 bits and m >= 7 at 384/521 bits (at 128 bits even m = 5 closes under floor A + H2 by only +1.1 bits), with a toy exact check (qc2_h4_check.out, m <= 3, K <= 4) and a proposed sampling protocol for m = 6..8;
(iii) the W-ary table (W = 4..256), where several cells are undecided or open.
All of (i)-(iii) are conditional on H2 (an attack-favourable but modelled LA cost) and (ii)-(iii) on H4w.

CORRECTION to the candidate's strength label. The candidate calls Floor A "rigorous for p > K, p not dividing W". Floor A needs the coefficient of prod_k x_k^{2^{m-1}} in S_{m+1} to be nonzero mod p (H-TOP). The program records H-TOP as holding at m = 2, 3, 4 and OPEN at m >= 5 (KN-OPEN-02200b: "the argument offered ... is a generic statement, and the degenerate specialisations a reviewer actually hit are exactly where genericity fails"). Every Floor-A-only closure at m >= 5 in the candidate's table (e.g. 256 bits: m = 5 margin +65.1) therefore inherits H-TOP at m = 5. Floor A is rigorous at m <= 4 given the program's own checks, conditional at m >= 5.

## N4 notation check

(representation, operation set) pair of QC2: representation = base-W digits of the factor-base x-coordinates as m*s auxiliary F_p variables with degree-W field equations (squarefree/reduced normal form for W = 2), i.e. the presentation of IDEA-20260830-84cdb7 (R1 in the RQ-ECDLP-623a32 sense); operation set Sigma = translation by factor-base elements (Class I, partial-action, index calculus as in IDEA-20260806-c5d183). QC2 introduces no new tracked object and no new projection of the group; the tracked quantity (support of the reduced generator S~) is a size invariant of the recorded pair.
Against the recorded rigidity results:
- IDEA-20260806-c5d183 (on a prime-order group a projection that propagates under the FULL translation action is constant or injective) and KN-FIND-ffe1df Theorem C (an exactly sum-compatible bucket index is a surjective homomorphism onto a group of order dividing N): both concern lossy projections propagating under full translation. QC2 has Sigma = factor-base translation only, and states no propagation claim, so it is neither an instance of nor a re-derivation of these results. It does not claim to escape them either.
- IDEA-20260901-863e36 (propagation is a property of a projection paired with an operation set; objects that propagate under Sigma are block systems of <Sigma>): QC2 tracks no projection, so the block-system classification does not apply to it.
- KN-OPEN-020 (bounded-degree algebraic factor bases scoped out; open class = high-degree, implicit-membership, target-dependent descriptions): the digit presentation is in the open class (degree-W membership per digit variable, implicit in the x-line). QC2 supplies a cost floor for the EXPANDED form of that presentation only. It does not answer KN-OPEN-020's universal question, and unexpanded or chained presentations, straight-line/implicit evaluation of S_{m+1}(l_1..l_m, x_R), stay open (the candidate says this itself). It is also not a "bounded-degree" result in new notation: it measures support, not degree.
Conclusion: QC2 is not a recorded rigidity result in new notation. It is also not a new arithmetic: it is the recorded Class-I digit pair with a cost-model floor attached, so it adds a constraint on one presentation and no new object.

## Verdict

advances_lead, lead = LEAD-ICP-digit-presentation-solving-degree (open_next_step).

Reason in short: the lane's open lead has a solver-side next step; QC2 proposes a solver-independent cost closure for the same presentation. Its rigorous core (Floor A, the top-degree support binom(s, 2^{m-1})^m) is already recorded by the red team (rt_support_size.py, EV-PFDR-f71d7f O-3, KN-FIND-0618ab) and is conditional on H-TOP at m >= 5 (KN-OPEN-02200b, open), contrary to the candidate's "rigorous" label. The external ingredient (uniqueness of multilinear representation) is the Moebius-inversion fact the program already uses. What is not recorded: the all-(m, s, W, N) rho comparison, Floor B / H4w, and the sampled-coefficient certification plan. Those increments are conditional (H2, H4w), are predicted to move no attack axis (0 bits), and in the high-arity band reduce to "a dense expansion in the digit cube is as large as the cube" (heuristic H-a above). Therefore: fold into the open lead as an alternative closure step (a certify-H4w-by-sampling task plus a rho-referenced extension of the O-3 count), do not register as a new lead, and do not upgrade Floor A to rigorous at m >= 5 until KN-OPEN-02200b is settled (the S_6 symbolic check it names is the cheaper prerequisite and is also the first thing QC2 needs).

Predictions (labelled as predictions, none produced here): if H4w holds in the sampled band and H-TOP holds at m = 5..8, the d = 2 expanded presentation closes by cost model at 128/256 bits for all m under H2; at 384/521 bits the m <= 6 closure also needs H-TOP at m = 5, 6. If H4w fails materially (large zero fraction), the affected arities revert to Floor A (open at m >= 6 at 128/256 bits per qc2_floorA_by_m.out).

## Addendum (after second read of the R4 derivation; supersedes any weaker wording above)

A1. The R4 derivation note itself was read in full (coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/derivation-R4-cost-honesty.md, section B3, plus rt_support_size.out). B3 compares the written top-part support binom(s, 2^{m-1})^m with each cost-table cell's OWN total claimed cost T, for eight cells (256 bits: m = 3, 4, 5 at several (D_0, omega); 128 and 64 bits at m = 5): excess -97.19 (m 3), -0.57 (m 4), +112.55 .. +115.66 (m 5, 256 bits), +81.77 (128 bits, m 5), +20.27 (64 bits, m 5). B3 states "this finding is specific to the m = 5 rows". It compares against T, not against rho for all (m, s), not at m >= 6, not for W > 2, and has no analogue of Floor B. So increment (i) (rho comparison over the full (m, s, W, log2 N) grid) is new relative to B3, but it is an extension of B3's table with the same object and the same counting argument, not a new argument.

A2. UNVERIFIED reference in the candidate: its self_kill_risk says the floor-A part repeats "the program's m < 10 closure at 256 bits". I searched for it and did not find it: grep for m < 10 / m <= 9 / m = 9 / arity 10 in EV-PFDR-1394a4, EV-PFDR-f71d7f, knowledge/findings, knowledge/open-problems, ledger/evidence (PFDR/digit/256 filter), the R4 note and its .out files, red-team-report.yaml, docs/ic/LEADERBOARD.md and docs/bounds/FRONTIER.md (crypto-main copies), and the candidate's own qc/ scripts and outputs. The candidate's own table (qc/qc2_floorA_by_m.out) shows floor A + H2 leaving m = 6..14 open at 256 bits (margins -29.3 .. -88.0), so floor A alone cannot be the source of an m < 10 closure at 256 bits. I record the reference as not located and unverified; nothing in this gate relies on it.

A3. Provenance upgrade for the external ingredient (page images read this session from the fetched PDF): Nisan and Szegedy, Computational Complexity 4 (1994) 301-313, p. 302, Section 1.1: the multilinear polynomials over a field form a 2^n-dimensional space with the generalized-AND functions as a basis, "so ... there is a unique multi-linear polynomial representing any given Boolean function"; Definition 1.1 (p. 303) defines deg(f) as the degree of that unique representation. Citation provenance: retrieved (page 302). The same paragraph notes that the polynomial under the 0/1 encoding and under the +-1 encoding "may look very different" and one "can be very sparse ... while the other is dense", while the degree is invariant. Consequence for QC2 (stated as my derivation, not computed): the support floor is a property of the fixed 0/1-digit monomial basis; the candidate's wording "the support of S~ is an invariant that every monomial-basis solver must read" holds for that basis only. Floor A (the top block-multidegree part) is unchanged in support under a per-variable affine re-encoding d = a + b*u (the top part is mapped to itself times a nonzero scalar, derivation sketch), so Floor A is basis-robust; Floor B / H4w is a statement about the 0/1 basis and would need a separate argument for another basis.

A4. H4 toy check: I READ qc/qc2_h4_check.out (m = 2, s = 2..8; m = 3, s = 2..6; primes 2^61-1, 2^31-1, 65537) and did not re-run it. The output shows full support at the two large primes and at p = 65537, m = 3, s = 6, one draw with 185,187 of 185,193 allowed coefficients nonzero (6 zeros), which matches the candidate's "6/185,193" statement; I did not verify the instrument (exact Moebius inversion of S_{m+1} at the sampled points) or the claim of zero coefficients above block degree K beyond reading the printed counts. The check covers K <= 4 only, as the candidate states. What I did re-run: qc2_floorA_by_m.py (reproduces its .out byte for byte), the first four lines of qc2_digit_writability_v2.py (headline W = 2 margins +29.4, +31.2, +34.3, +32.7 reproduce), and the single number 5*log2(C(54,16)) = 221.3.

A5. Standing-obstruction statements the candidate must stay consistent with (verbatim from the lead rows):
- SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base, closed_obstructed, theorem): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). ... Scope: prime-order E/F_p, any base of size B."
- ICPERF writability (LEAD-ICP-icperf-writability-boundary, closed_obstructed, cost_model): "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."
QC2 is consistent with both (it predicts a closure) and is outside the second one's Scope (prime-field, not binary).

A6. Rigor label, restated: Floor A is rigorous at m <= 4 given the program's own checks of H-TOP (KN-OPEN-02200b: holds m = 2, 3, 4, open at m >= 5). At m >= 5 it is conditional on H-TOP, including the 128-bit m = 5 closure that holds by only +1.1 bits under floor A + H2 (qc2_floorA_by_m.out). The first prerequisite named by KN-OPEN-02200b (the S_6 symbolic check at m = 5, by the one-variable specialisation used at m = 4) is also the cheapest first step for QC2 and would settle the m = 5 cells before any sampling is needed.
