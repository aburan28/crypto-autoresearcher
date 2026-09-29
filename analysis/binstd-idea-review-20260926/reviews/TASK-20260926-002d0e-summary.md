# TASK-20260926-002d0e — lane R1 summary (queued_for_design BINSTD proposals)

Reviewer lane: TASK-20260926-002d0e, 2026-09-26. Adversarial re-read in full of
the seven `queued_for_design` proposals under `RQ-BINSTD-b6f698` (HOLD-B..G of
`DEC-20260924-99ce20`). Advisory only: no record edited, no status moved, no run.
Every number below was re-derived in this session by short Python arithmetic
(no solver, no experiment) unless marked `unchecked`. Per-idea reviews are in
`reviews/<IDEA id>.yaml` in the BRIEF section 6 schema.

## Summary table

| idea | verdict | agrees with hold? | one-line concrete experiment | successor seam |
| --- | --- | --- | --- | --- |
| IDEA-20260922-1a081a | sound_with_corrections | agrees (HOLD-B) | Zero-compute script reproducing the 13 rho rows (+ ECC2K-130 / ECC2-131 pair) under sqrt(pi r/(4k)), the (227, 55) gate, Delta_rho and the threshold G = sqrt(2m); C1 census; toy yield parity at n = 17 (Koblitz a = 1 vs RC-1 curve, V = {deg < 9}, m = 2, exhaustive) | Measure the realised Frobenius relation gain G (rank of tau-shifted relations) on a tau-stable n = 17/23 base against sqrt(2m) — the number C3's sign depends on |
| IDEA-20260922-c07598 | sound_with_corrections | agrees (HOLD-B, fold into 1a081a) | Five-row integer certificate (h = q+1-t, Weil recursion, gcd, t odd) + toy E/F_16 (A = 0, B = t^3+1, #E = 12) over F_{2^20} (r = 87421) and F_{2^28}: least j with pi_16^j P = P, predicted 5 and 7; pi_2 fails E's equation | none (A3 closes on j = 1/b ≠ 0 ⇒ Aut = Z/2 for every ordinary binary curve; provenance to upgrade from recalled) |
| IDEA-20260922-6cf862 | sound_with_corrections | agrees (HOLD-D) | Part 1 certificate file (identities, ord_k(2^16) lattice, corrected rho rows, product-law floor per row with the lattice rounding cost); Part 2 on the same E/F_16 cell over F_{2^20}: exhaustive m = 2, 3 census of G-targets over E(F_16) (predicted 0) with cofactor-target positive control, stable vs size-matched non-stable W, ordinary-curve null | THE COARSE-LATTICE PRICE: per-row floor at optimal l vs nearest phi-stable F_q-dimension vs orbit-union set, with/without the order-k gain (c2pnb208w1 and c2pnb272w1 informative) |
| IDEA-20260922-29b1c5 | defective | disagrees (HOLD-E) | Stage 1': census of iota-stable subspaces at composite n ≤ 12 (predicted one per divisor of n, V_d = b^{1/4} F_{2^d}); Stage 2': n = 17 Koblitz (a = 1) and RC-1 curve, W dim 8, exhaustive m = 2 — multiplicity per covered target (predicted 2.00 on V_W vs ≈1 random), coverage per operation (ratio 0.5), relation-phase total ratio (0.5) | THE SCALED-SUBFIELD FACTOR BASE b^{1/4} F_{2^d} on the five c2pnb rows (d ∈ {k, 2k, 4k, 8k}): iota- and phi-stable, not a subfield, not emptied by the cofactor lemma; price yield, descended degree and composition of the E/2E bit with the phi-orbit quotient at m = 4 against the per-row floor |
| IDEA-20260922-6028ed | sound_with_corrections | agrees (HOLD-F) | Per-cell write-once records under analysis/binstd-curve-audit/reachability/ with unit, m, floor_bits, budget_bits, rho_convention, provenance_tier; validator in the validate_ledger check_* pattern; six-case synthetic battery on a scratch copy; seed only re-derived cells (13 rho rows, GHS/stable-subspace/subfield-rational columns, ECC2K-130 floors at m = 2..8) | none |
| IDEA-20260922-818b73 | dominated | agrees (HOLD-F, as a column of 6028ed) | Zero-compute budget column budget_bits(m) = 60.81 − floor_bits(m) for ECC2K-130 and the toy analogue at RC-1; then count field multiplications per group op and per W_4 refutation on RC-1's 144 archived instances to produce the first same-unit gamma_meas | A CERTBIN proposal for the first same-unit exchange rate (mults per group op vs per W_4 refutation on RC-1), the missing conversion between KN-FIND-5a8d3e's refutation costs and KN-FIND-aa2efc's budget column |
| IDEA-20260922-77bf31 | sound_with_corrections | agrees (HOLD-G) | Cell (n = 17, Koblitz a = 1, r = 65587, m = 2, l = 9) with V_stable (ideal of a degree-8 factor of Phi_17) and V_poly = {deg < 9}, RC-1 curve as null: tau-orbit concordance (1.000 on V_stable), W-walk lag-1 autocorrelation with block bootstrap, NEW tau-walk autocorrelation on V_poly, fresh-scalar anchor; Stage 2 descent/relation ratio vs g/B = 17/512 | TAU AS THE FREE ATTEMPT GENERATOR on ECC2K-130 for non-stable V: 131 conjugate targets at one squaring each, systems related by the a77711 equivariance; measure indicator independence and shareable elimination work across the 131 images (owner CERTBIN; discriminated from IDEA-20260923-5d0b8e) |

## Ranked: which of these are worth designing next, and why

1. **6cf862 Part 1 (+ the floor column)** — seconds of arithmetic, already
   re-derived here; fills five structurally-empty cells with certificates and,
   with the product-law floor per row added, turns them into priced cells. Its
   quoted rho rows are ALREADY at the corrected convention (only the label was
   wrong); the net movement becomes sqrt(k), not sqrt(k/2). c2pnb208w1 is the
   row of the whole population with the most product-law headroom (13–31 bits
   at m = 4–5 versus 4.4–12.4 on ECC2K-130), which is the one thing in this
   lane that changes where a future oracle measurement should be pointed.
2. **1a081a after S2** — the baseline column is right to 0.01 bit; add the
   Certicom pair row (Delta_rho = 4.02 bits, a Frobenius-blind line reaches
   ECC2-131 first), the threshold form of C3 (sign flips iff realised relation
   gain G > sqrt(2m); measured G so far is 1), and the trace-parity exception
   pre-registered. c07598 folds in as the symmetry-ledger section with A3 closed.
3. **77bf31 Stage 0 with the two corrections** — the grid must be re-chosen
   ((17,2,9) on a = 1, (23,2,12), (31,3,11), (41,2,21) are the only cells with a
   tau-stable V at l = ceil(n/m); n = 19, 29, 37 host none — the HOLD-T defect
   again), and limb (E) must be scoped to tau-stable SETS: on ECC2K-130 no
   useful tau-stable subspace exists, so for a subspace base tau is the
   cheapest NON-trivial re-randomiser (131 conjugate attempts at one squaring
   each). That inversion is the most interesting ECC2K-130 statement in the lane
   and is minutes of pure Python at n = 17.
4. **6028ed as the carrier** — but sharded one write-once file per cell (the
   repository's own concurrency rule) and with unit / m / floor / budget /
   convention / provenance-tier fields, seeded only from re-derived numbers.
   818b73's gamma* is its budget column, defined from the product-law floor and
   citing KN-FIND-aa2efc (which 818b73 does not cite and which already carries
   the per-m budget); 818b73's worked example must be restated same-cell (the
   133-bit figure is at (n' = 66, m = 2), not (n' = 33, m = 4); the same-cell
   gap is ≥ 49 bits via 3f7a1c's attempts column).
5. **29b1c5: return for revision, not design.** Its lemma is false as stated
   (the proof drops a factor sqrt(b); the iota-stable subspaces are exactly
   b^{1/4} F_{2^d}, one per divisor d of n — verified by brute-force census at
   n = 6), its composite-row verdict is wrong in the direction that hides a live
   object, and its "exact 2^{m-1}" is an accounting artifact (decompositions
   over V_W cluster in even-parity T-flip classes of size 2^{m-1}, so coverage
   per target falls by the same factor; net gain is one bit — the index of 2E —
   at any m; on Koblitz rows V_W = tau-bar^{-1}(F_W) exactly). The prime-row
   emptiness cell survives with a corrected certificate and can be filed at
   zero compute. The scaled-subfield base on the c2pnb rows is the one
   genuinely new object this lane surfaced and deserves its own proposal.

Nothing in the lane moves an exponent or an ECC2K-130 floor; every idea here is
indexing, certification, accounting or infrastructure, and each says so. The
product-law reading of the brief stands under every correction made here:
m ≤ 3 closed at the floor, m ≥ 4 open by the tabulated budgets, orbit-aware
floors lower by 9–13 bits but unrealised by any measured oracle.

## Arithmetic checks performed, by record

Convention throughout: rho = sqrt(pi r/(4k)), k = Frobenius class order
(CORR-20260922-81aeab as applied in DEC-20260924-99ce20); orders and cofactors
parsed as integers from `analysis/binstd-curve-audit/binary-curve-params.txt`.

**Shared**
- Product-law floor table of BRIEF §2 / KN-FIND-aa2efc reproduced EXACTLY as
  min over l of [m!·2^(131−(m−1)l) + m·2^(2l)]: 89.25, 68.58, 56.40, 48.44,
  42.85, 35.61 at m = 2, 3, 4, 5, 6, 8 (optimal l = 43.3, 33.0, 26.8, 22.8,
  19.9, 16.1 bits); budgets vs 60.81: none, none, 4.41, 12.37, 17.96, 25.2.
  Frobenius-aware variant (relations/131, LA/131²): 79.87, 58.03, 45.15, 36.71,
  30.79, 23.10. Same minimisation at N = 160/192/256 for c2pnb176v1/208w1/272w1:
  m = 4: 68.0/80.8/106.4 (blind), 62.5/74.9/99.9 (orbit-aware); m = 5:
  58.1/68.8/90.1 and 52.3/62.6/83.3; rho rows 78.10/93.98/125.78.
- ECC2K-130: #E(F_2) = 4 (points (0,1),(1,0),(1,1),O), t = −1; Weil recursion
  gives 2^131 + 1 − s_131 = 4l with l = 680564733841876926932320129493409985129
  (130 bits, Miller-Rabin probable prime); rho = 2^60.8090; negation-only
  2^64.326; ECC2-131 stand-in sect131r1 (h = 2, 130.0-bit r) rho_neg 64.83;
  Delta_rho = 4.02 = 0.5·log2(131) + 0.5.
- ord_n(2): 17→8, 19→18, 23→11, 29→28, 31→5, 37→36, 41→20, 131→130, 163→162,
  193→96, 233→29, 239→119, 283→94, 409→204, 571→114; stable-dimension sets
  {0,1} + ord·{0..(n−1)/ord}.
- Reduction polynomials t^17+t^3+1, t^19+t^5+t^2+t+1, t^23+t^5+1, t^29+t^2+1,
  t^31+t^3+1, t^37+t^6+t^4+t+1, t^41+t^3+1 irreducible (Rabin test).
- Koblitz toy orders (Weil recursion): n = 17 a = 0: 4·137·239; a = 1: 2·65587;
  n = 19: 4·130873 / 2·262543; n = 23: 4·2095853 / 2·4196903; n = 29:
  4·8353·16067 / 2·6323·42457; n = 31: 4·373·1439393 / 2·26041·41231; n = 37:
  4·149·230603167 / 2·260999·263293; n = 41: 4·549756390943 / 2·739·2543·585071.
- Instrument availability: every module of experiments/EXP-CERTBIN-e94b27/impl/
  except make_trial_plan.py and stats_exact.py imports numpy; numpy is NOT
  installed in this container (`missing: numpy`); no WDSat/CaDiCaL/msolve/M2/
  Singular/Sage/Magma binary.

**IDEA-20260922-1a081a**
- Twelve rho rows: K-163 77.15/B-163 80.83; K-233 111.39/115.83; K-283
  136.25/140.83; K-409 198.99/203.83; K-571 279.75/284.83; sect193r1/r2 95.83;
  sect239k1 114.38 — record agrees to 0.01 bit. log2 r = 162.000, 231.000,
  232.000, 281, 282, 407, 408, 569, 570; h = 2/2 at 163, 4/2 above.
- Delta_rho(m) = 3.674, 4.432, 4.572, 4.838, 5.079 (record 3.67…5.08 ✓);
  aware branch −3.67, −3.43, −3.57, −3.84, −4.08; 227/55 = 4.127 vs sqrt 17 =
  4.123 ✓; threshold G = sqrt(2m) derived. C1 census: `unchecked`.

**IDEA-20260922-c07598**
- Cofactor identities 5/5; Weil order = h·r 5/5; gcd(h,r) = 1 5/5; t odd 5/5
  (ordinary ⇒ j = 1/b ≠ 0 ⇒ Aut = Z/2, recalled classification).
- Record's rows 77.85, 93.73, 125.53, 141.45, 173.31 reproduced under its own
  sqrt(2k), r = 2^(s−0.5); corrected rows 78.10, 93.98, 125.78, 141.71,
  173.57 (net +0.25 bit: +0.5 convention, −0.25 half-bit r).
- Toy cell E/F_16 (A = 0, B = t^3+1): #E(F_16) = 12, t = 5; F_{2^20}: 12·87421;
  F_{2^28}: 12·22366891; F_{2^24}: largest prime 181 (composite control needs a
  curve search).

**IDEA-20260922-6cf862**
- ord_k(2^16) = 5, 3, 1, 9, 11; factor counts 3, 5, 17, 3, 3; subspace counts
  8, 32, 2^17, 8, 8; dimension sets as the record lists; q = 2, k = 131 returns
  {0,1,130,131}.
- Quoted rows 78.1, 94.0, 125.8, 141.7, 173.6 = sqrt(pi r/(4k)) with actual r
  (label sqrt(2k) would give 77.60 … 173.07); net movement sqrt(k) = 2^1.73,
  1.85, 2.04, 2.12, 2.26 (record sqrt(k/2)).
- Smallest stable l = 5, 4, 5, 9, 11 → 2^80, 2^64, 2^80, 2^144, 2^176;
  c2pnb208w1 LA dim 2^60.3; per-row floors as above.

**IDEA-20260922-29b1c5**
- x(P+T) = sqrt(b)/x re-derived and confirmed on all 75 affine points of
  y²+xy = x³+b over F_64. x(2P) = x² + b/x² re-derived, hence u = sqrt(x(2P)) =
  x(tau-bar P) on Koblitz curves.
- Lemma census at n = 6, b ∈ F_4∖F_2: 3 iota-stable subspaces of dim ≤ 3
  (dims 1, 2, 3), each = b^{1/4}·F_{2^d}; record predicts 1. Corrected lemma
  V_d = b^{1/4} F_{2^d}, one per divisor.
- Clustering check at n = 11, m = 2 (#E = 2112, W dim 5, |V_W| = 29, |F_W| =
  22 vs random subspace |F_R| = 25): mean multiplicity 2.00 (u-line) vs 1.08
  (random); coverage per pair-sum ratio 0.54 (predicted 0.5). Relation-phase
  totals m!N vs m!N/2 ⇒ one bit at any m.
- rho expression 0.886·sqrt(pi l/4): 64.151 vs 64.326, 0.175 bit low (A5 ✓).

**IDEA-20260922-6028ed**
- No reachability-table artifact in the repository (find); validate_ledger.py
  has check_cross_refs (843), check_schema_supersessions (1143),
  check_knowledge_entries (1665); 31 dumped curves (ECC2K-130 absent from the
  dump). No arithmetic in the record to check.

**IDEA-20260922-818b73**
- 2^0.3 = 1.231; 2^(60.9−133) = 2^−72.1 ✓ as arithmetic; but 133 is at
  (n' = 66, m = 2) per RQ-QSP-f9bbdb item (5) — cross-cell. Same-cell gap via
  3f7a1c: 110 − 60.9 = 49.1 bits (d = 3), 90.6 − 60.9 = 29.7 (d = 7).
- KN-FIND-aa2efc budget = 2^(60.81 − floor): m = 4 → 2^4.41, m = 5 → 2^12.37
  (gamma* at family level, uncited by the record).

**IDEA-20260922-77bf31**
- Descent shares with l = ceil(n/m): ECC2K-130 m = 4: l = 33, g = 2^7.03,
  2^−25.97; m = 5: l = 27, 2^−19.97; K-163: l = 41, 2^−33.65; K-571: l = 143,
  2^−133.84; c2pnb368w1: l = 92, g = 23 = 2^4.52, 2^−87.48 — all ✓.
- Toy grid: tau-stable V at l = ceil(n/m) exists only at (17,2,9), (23,2,12),
  (31,2,16), (31,3,11), (41,2,21); none at n = 19, 29, 37; none for m = 4 at any
  listed n. TNAF scalar multiplication ≈ n/3 additions, not 1.5n (recalled).

## Files written by this lane

- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-1a081a.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-c07598.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6cf862.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-29b1c5.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6028ed.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-818b73.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-77bf31.yaml
- analysis/binstd-idea-review-20260926/reviews/TASK-20260926-002d0e-summary.md

No existing record was edited. Scratch arithmetic scripts live only in the
session scratchpad outside the repository.
