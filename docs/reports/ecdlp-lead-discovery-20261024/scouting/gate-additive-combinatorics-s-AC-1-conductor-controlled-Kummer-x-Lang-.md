# Gate record: AC-1, conductor-controlled (Kummer x Lang) Weil bound for the Miller primitive U = f_{N,P}^{1/N}

Candidate: "AC-1: conductor-controlled (Kummer x Lang) Weil bound for the Miller primitive U = f_{N,P}^{1/N} (overlaps scout-arithmetic-statistics C1; independent re-derivation)". Bottleneck B7 (transfer, prime field). Field: additive combinatorics. Tier X, predicted gain 0 (a closure).

Gate session: 2026-10-25. Read-only on every repository. Everything written by this gate is under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/` (raw copies in `_ac1_raw/`). Tools were run from `/Volumes/SSD990-2/crypto-autoresearcher` with the three `LEAD_ATLAS_*` variables exported as instructed.

## 0. What this gate produced and what it did not

Produced here (and pasted raw below): six `lead_atlas.py --match` runs (3 candidate phrasings plus 3 of my own), six `build_frontier_map.py --match` runs (same strings), ledger-index greps, readings of the lead YAMLs, and a literature retrieval log.

NOT produced here: any measurement of the theorem, of K1, or of K2. The candidate's figures (max|S|/(2 sqrt p) = 0.9974-1.0000 on 15/15 curves, K2 exact on 9/9, max|sum chi(r_k) e(ak/N)| = 27.7-122.4) are the candidate's own. The sibling dossier `scout-arithmetic-statistics.md` (its section C2) reports its own toy table. I reran none of these. Every correctness statement below is therefore a statement about derivations and sources I read, not a result I measured. Expected values are labelled predictions.

## 1. Verdict in one paragraph

Verdict: `advances_lead`, lead `LEAD-TRF-miller-cocycle-nonhom-transfer` (open_unexamined), with `LEAD-EXO-miller-pairing-cocycle` (open_next_step, K1/K2 cell) as the secondary home.

- N1: the candidate's object (U = f_{N,P}^{1/N}, its correlation with characters of Z/N) is the object of that open lead and of `IDEA-20261017-e3a6f1` H1. The lead's next step is to measure H1. AC-1 instead derives the character clause of H1 and supplies the constant. That is a sharper next step on an open lead, not a duplicate: no recorded record contains the bound.
- Not `duplicate_of_lead`: no closed lead's obstruction covers how U correlates with characters of G. The closed hits (SO-PADIC, SO-PAIR, SO-NET, SO-TORS, SO-DECK, SO-ISO, SO-GEN) are consistent with AC-1 and AC-1 escapes none of them. The candidate says so itself (gain 0).
- Not `known_result` through N2: no KRMAP row covers character sums on elliptic-curve points (the only literature-term hits in KRMAP.md are "Weil descent" and "Weil restriction"). KR-RHO-53c89f is adjacent only. Outside KRMAP, the inequality is known in substance (section N2 below): Shparlinski-Stange 2012 Lemma 4 gives the Kummer x group-character bound with constant 2 deg f, and Castro-Moreno 2000 gives a support-count constant. AC-1 is a standard combination of the two applied to a function of degree N, not new mathematics. What is new is the application and what it does to the lead's disposition.
- The lead's own discriminator asks for equidistribution at the 1/p rate. AC-1 derives p^{-1/2} (a derivation I read but did not verify). AC-1 therefore cannot close the whole lead. The ratio clause (Smart-ratio success 1/p), nonlinear use of U, the zeta-defect cell and the generalized-Jacobian cell stay open.
- One piece may be new relative to the literature: C1c (flatness of r_k = psi_{k-1}/psi_k against characters). It is conditional on K2 (unreviewed) and it appears to bear on an open question posed in Bhakta-Shparlinski 2025. That calls for independent review before anyone cites it, not for enthusiasm. Details in section N2.
- Merge: scout-arithmetic-statistics C2 (the candidate calls it C1; in that file C1 is the occupancy calculator) states the same theorem. `gate-p-adic-and-tropical-geom-C1` covers the K2/C1d EDS-ratio material (its analysis section was still empty when I looked, so there is no verdict of theirs to compare). Treat the three as one item.


## N1. Atlas collision: raw `tools/lead_atlas.py --match` outputs, verbatim

Run from /Volumes/SSD990-2/crypto-autoresearcher with LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS and LEAD_ATLAS_ECC_CHALLENGES exported as instructed. Runs a-c are the candidate's three match_phrasings; d-f are my own. The tool prints 8 rows per run; the first 5 of every run were read (reading follows the raw blocks).

### N1 run a (candidate phrasing)

```
$ python3 tools/lead_atlas.py --match "conductor-controlled Weil bound for the Miller primitive U and the Kummer sheaf of f_{N,P}"
    7  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    6  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    6  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    6  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    5  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    5  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
    4  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
```

### N1 run b (candidate phrasing)

```
$ python3 tools/lead_atlas.py --match "character sums of Miller function values are square-root small regardless of degree"
   20  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   12  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
   10  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
    9  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    8  LEAD-STR-isogeny-walk-weak-neighbour         closed_known       Walk or construct isogenies from a deployed curve to find a weak neighbour
    7  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    6  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
```

### N1 run c (candidate phrasing)

```
$ python3 tools/lead_atlas.py --match "non-homomorphic section recovers k only at the random rate"
    5  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    5  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
    4  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    4  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    3  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    3  LEAD-EXO-methodology-instruments             open_next_step     Program methodology: instrument calibration, nulls, findings promotion (not a cost mechanism)
```

### N1 run d (own phrasing)

```
$ python3 tools/lead_atlas.py --match "Weil bound Kummer sheaf Lang torsor character sum Miller function equidistribution"
   12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    7  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    6  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    6  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    6  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    5  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
```

### N1 run e (own phrasing)

```
$ python3 tools/lead_atlas.py --match "elliptic divisibility sequence ratio psi_{k-1}/psi_k character sum flatness"
    8  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    7  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    4  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    4  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    3  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    3  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    3  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
```

### N1 run f (own phrasing)

```
$ python3 tools/lead_atlas.py --match "Lang torsor character of E(F_p) Kummer sheaf Euler-Poincare conductor square-root cancellation"
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    6  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    5  LEAD-EXO-torsor-deck-period                  closed_obstructed  Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent
    4  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    4  LEAD-STR-koblitz-volcano-descendants         closed_obstructed  Curves below a binary Koblitz curve in its volcano (ECC2K-130, K-163, K-283, m=37..83)
    4  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
    3  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
```

### N1 reading of the top 5 hits of every run

Lead YAMLs were opened under `knowledge/leads/ecdlp/<family>/` and mechanism, disposition, obstruction.statement and forecloses were read for every non-KR hit. KR hits are logged in N2. "Same mechanism" below means same object and same test, not shared vocabulary.

Run a (candidate phrasing 1, "conductor-controlled Weil bound for the Miller primitive U and the Kummer sheaf of f_{N,P}"):
1. LEAD-EXO-miller-pairing-cocycle (open_next_step, score 7): SAME OBJECT (U(R) = f(R)^(1/N), "if U(kP) exposed k through a cheap closed form"). No obstruction recorded. Its next_action (verify K1, K2, then ask whether k is recoverable from U(kP) in fewer than sqrt N operations once r_k is charged) is the cell AC-1's C1b/C1c/C1d talk about.
2. KR-IC-5ea2f8 (known_result, 6): lexical hit on "Weil" (GHS Weil descent). Orthogonal.
3. LEAD-EXO-curve-model-representation (closed_obstructed, 6): lexical hit on "Kummer" (Kummer line, x-only models; obstruction is invariance of solving degree). AC-1's Kummer is a Kummer sheaf (a mu_e-cover of E minus {P,O}), not a coordinate change. Orthogonal.
4. LEAD-TRF-ghs-binary-composite (closed_known, 6): lexical hit on "Weil". Orthogonal.
5. LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined, 6): SAME OBJECT AND SAME MECHANISM (see below).

Run b (phrasing 2, "character sums of Miller function values are square-root small regardless of degree"):
1. LEAD-EXO-miller-pairing-cocycle (20): as above.
2. LEAD-TRF-mov-small-embedding-degree (closed_known, 12): the reduced pairing when N | p^k - 1. AC-1 is the complementary regime gcd(N, p-1) = 1, where the pairing is trivial; its N | p-1 control cell is exactly the MOV/Frey-Rueck boundary of this lead. No overlap.
3. LEAD-STR-small-cm-disc-nonunit-endo (closed_obstructed, 10): lexical ("degree"). Orthogonal.
4. LEAD-TRF-miller-cocycle-nonhom-transfer (9): same.
5. KR-RHO-53c89f (8): adjacent, see N2.

Run c (phrasing 3, "non-homomorphic section recovers k only at the random rate"):
1. LEAD-ICP-coincidence-harvest-structured-base (open_next_step, 5): lexical ("random"). Orthogonal.
2. LEAD-STR-jmv-random-self-reduction (closed_known, 5): random self-reduction by isogeny walks within one endomorphism-ring level; a hardness equivalence, moves no cost. AC-1's C1b is a different random self-reduction (re-randomising the target through U), not covered by this lead's forecloses phrases ("JMV random self-reduction gives an attack", "expander isogeny walk re-randomises ECDLP"). It is not covered, and it is also not an attack: the candidate's own C1b says the self-reduction rate is rho-level.
3. KR-RHO-13bf67 (4): Shoup/Nechaev generic lower bound. Consistent with AC-1 (U is computed from the coordinates of the point, so it is not a GGM oracle; AC-1 claims no sub-sqrt-N algorithm).
4. LEAD-ICE-semaev-cover-monodromy (closed_obstructed, 4): monodromy of the Semaev summation cover (SO-MONO). A different cover and a different question. Orthogonal.
5. LEAD-TRF-function-field-xedni-lift (closed_obstructed, 4): sections of elliptic surfaces over F_p(t) (SO-XEDNI). Orthogonal.

Run d (my own, "Weil bound Kummer sheaf Lang torsor character sum Miller function equidistribution"):
1. LEAD-EXO-miller-pairing-cocycle (12), 2. LEAD-TRF-miller-cocycle-nonhom-transfer (8): as above.
3. LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale, 7): same KIND of statement (Fourier/character correlation of a function of the point with characters of the discrete log), different OBJECT: the indicator of the small-x set, which is not an algebraic function of the point. Its recorded obstruction says the Weil route fails because DL_G(P) is not algebraic (KN-FIND-e7a3b1, "wrong functional form"). AC-1 does not contradict that finding and does not reopen H-PSEUDO: in AC-1 the discrete-log character is the trace function of a lisse Lang-torsor sheaf on E, and the other factor is a Kummer sheaf of a rational function, so the sum is a genuine curve sum. The family AC-1 handles is "algebraic statistic times a group character"; H-PSEUDO's family is not in it.
4. KR-IC-5ea2f8 (6): lexical.
5. LEAD-EXO-curve-model-representation (6): lexical.

Run e (my own, "elliptic divisibility sequence ratio psi_{k-1}/psi_k character sum flatness"):
1. LEAD-EXO-elliptic-net-eds (closed_obstructed, 8, SO-NET): the home of C1c/C1d. Not the same mechanism: that lead uses net identities as a relation supply; C1c is a character-sum statement about one derived sequence. Consistent with its measured conclusion (collision statistics random-oracle-equivalent). AC-1 supplies none of its "revisit_when" objects (a target-specific nonlinear locator, or a rank >= 2 net with k-specific relations).
2. LEAD-EXO-dl-character-sum-pseudorandom (7): as in run d.
3. LEAD-RHO-correlated-walks-shared-sums (closed_obstructed, 6): lexical. Orthogonal.
4. KR-IC-5a43e5 (4): Semaev summation polynomials, lexical.
5. LEAD-STR-torsion-module-leak (closed_obstructed, 4, SO-TORS): forecloses "Legendre symbol of psi_l at x(kP)" and "division polynomial statistics leak k". C1c is a character statistic of division-polynomial ratios with the INDEX k varying (psi_{k-1}(P)/psi_k(P)), not psi_l for a fixed l. The nearest forecloses phrase is "division polynomial statistics leak k". AC-1 does not claim leakage; it bounds a family of such statistics (rigorously, if K2 holds), which is the quantitative form of that closed lead's own conclusion.
(Also in this run: LEAD-EXO-miller-pairing-cocycle (3), LEAD-ICP-algebraic-membership-factor-base (3, SO-ALGFB, lexical via "character"), LEAD-STR-class-group-ecdlp-bridge (3).)

Run f (my own, "Lang torsor character of E(F_p) Kummer sheaf Euler-Poincare conductor square-root cancellation"):
1. LEAD-EXO-curve-model-representation (6), 2. LEAD-EXO-dl-character-sum-pseudorandom (6): as above.
3. LEAD-STR-class-group-ecdlp-bridge (open_next_step, 6): Cl(O)-vectorization and CM self-pairings as a bridge to ECDLP. Different mechanism (class-group torsor, not a G_m-extension class of a point of order N). Orthogonal.
4. LEAD-EXO-torsor-deck-period (closed_obstructed, 5, SO-DECK): torsor/deck-orbit descent on G_m/G_a-torsors. U is a section of a G_m-extension, so the lead's family is adjacent. Its obstruction (a rational deck-invariant factors through the quotient; a connected nontrivial cover has no rational section, so a rational selector is a missing section) concerns using the cover to route a target to a small fibre. AC-1 proposes no label, selector or routing; it only bounds a character sum. Outside the premise, and not an escape. (This lead was not in the candidate's SO list; I added it.)
5. LEAD-STR-isogeny-class-generic-invariance (closed_obstructed, 4, SO-ISO): rho and BSGS depend only on group order and Aut. AC-1 makes no cost claim about a generic algorithm; its bound is uniform in the isogeny class by construction. Outside the premise, no overlap. (Opened as requested; also not in the candidate's SO list.)
Further hit seen: LEAD-EXO-coordinate-statistic-leakage (open_next_step, run f rank 8; forecloses "trace-function sheaf pulled back through addition"). It is an open lead on cheap coordinate statistics. AC-1's theorem for general f (not only the Miller function) says that the Kummer family chi(f(R)) is uncorrelated with every group character to within s(f) sqrt p, which is relevant to that lead's "multiplicative statistics sit at the random level" census (EV-ECDLP-81f4d4). The general-f form is Shparlinski-Stange Lemma 4/5 in degree form, so it is known technique. Suggest filing the general-f statement as evidence for that lead and keeping the Miller-specific consequence under LEAD-TRF-miller-cocycle-nonhom-transfer.

#### The same-mechanism hit, read closely

LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined). Mechanism: with gcd(N, p-1) = 1 the Tate pairing is trivial but f_{N,P} gives U(R) = f(R)^{1/N} whose coboundary is the line-function cocycle; "if log U(kP) carried structure in k ... it would be a cheap non-homomorphic transfer into F_p^*". Next step: test H1 of IDEA-20261017-e3a6f1 at toy size (equidistribution of ell(k) = log_g U(kP) in Z/(p-1), Smart-ratio success, correlation with characters of Z/N, with a planted-structure positive control). Discriminator: "Equidistribution at the 1/p rate closes the lead ... any character correlation would be the first one-point transfer signal". Forecloses phrases: Miller function transfer; generalized Jacobian transfer; unreduced Tate pairing value; Miller S-unit descent; zeta defect quasi-homomorphism. No obstruction block (it is open).

IDEA-20261017-e3a6f1 H1, opened in full (record 1 of 3): "ell(k)=log_g U(kP) is uniform on Z/(p-1) jointly with characters of Z/N". Its `rigorous_support` reads: "character sums of such terms are bounded in the recalled literature (unread)". Its minimal test already specifies the spectrum measurement (256 multipliers a, all j, threshold ln(256 N)+12, positive control N | p-1). So the proposal anticipated that a character-sum bound exists and did not derive it. AC-1 derives it. That makes AC-1 a sharper next step: it turns the character half of H1 from "heuristic with unread support" into a theorem with an explicit constant, and it predicts the maximum the lead's spectrum test can show (2 sqrt p per (chi, a), against the proposal's null threshold). It does not replace the lead's toy test, which still has to fix the K1/K2 conventions, run the positive control and measure the ratio clause.

Escape clause. Hits' forecloses phrases that AC-1 does NOT cover: (a) "equidistribution at the 1/p rate" and the Smart-ratio success rate (AC-1 gives only p^{-1/2}); (b) nonlinear statistics of U and multi-query use; (c) "zeta defect quasi-homomorphism" (AC-1's H-AC1 cell, see conflict note in section 6); (d) "generalized Jacobian transfer". Phrases AC-1 DOES touch: "Miller function transfer", "unreduced Tate pairing value" (character level), "division polynomial statistics leak k" (C1c), "elliptic net relations for discrete log" (C1d, only as a negative bound).

### N1 standing obstructions the candidate touches, quoted from the lead rows (Scope clauses included)

SO-PADIC, LEAD-TRF-padic-canonical-section (closed_obstructed, theorem): "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E." AC-1: not escaped, and not an extension of this obstruction's proof. The objects differ (sections into E(Q_p) versus F_p^*-valued sections of a G_m-extension). AC-1's rate p^{-1/2} is weaker than the 1/p stated here. The candidate's word "extends" should read "is the F_p^*-valued analogue at a weaker rate".

SO-PAIR, LEAD-TRF-second-torsion-direction (closed_obstructed, theorem): "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N." AC-1: the premise is homomorphic or graph-type transfers; U is non-homomorphic, so it is outside the premise, and AC-1 asserts no transfer. Not escaped.

SO-NET, LEAD-EXO-elliptic-net-eds (closed_obstructed, proof; the YAML has no Scope clause, confirmed): "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing (24x -> 135x)." AC-1: C1c adds a character-level flatness statement for one EDS-derived sequence; C1d's circularity claim is the Lauter-Stange EDS-association equivalence (recalled; bibliographic record retrieved, see N2). Not escaped.

SO-TORS, LEAD-STR-torsion-module-leak (closed_obstructed, proof): "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N." AC-1: consistent. AC-1 is a rigorous instance of "a non-homomorphic point statistic" with correlation bounded by 2 sqrt p / N per (chi, a) pair; the candidate writes 2/sqrt(N), which agrees when p ~ N. Not escaped.

Added by this gate (not in the candidate's list):

SO-DECK, LEAD-EXO-torsor-deck-period (closed_obstructed, proof; no Scope clause): "For a generically Galois cover every rational deck-invariant factors through the quotient; a transitive fibre-orbit label is base data; a connected nontrivial cover has no rational section, so a rational target-compatible selector is a missing section or trivialization (IDEA-010 gate, independently verified). The cubical/biextension lift lands on the invertible side of the recognizable/invertible duality, i.e. computing its label costs the log (IDEA-20260920-376b00)." AC-1 proposes no label or selector. Outside the premise.

SO-ISO, LEAD-STR-isogeny-class-generic-invariance (closed_obstructed, theorem; no Scope clause): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (+-5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve." AC-1 makes no generic-cost claim. Outside the premise.

SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed, theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r." And LEAD-EXO-augmented-oracle-ggm (closed_obstructed, theorem): "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 ... Scope: oracles, not resources (see IDEA-20260808-ea3b4f)." AC-1 claims no sub-sqrt-r algorithm, so it is inside both Scopes by default.

Also true for the object-frame results: AC-1 is not a factor base (KN-OPEN-020 does not apply), and it adds no new arithmetic (section N4).

## N2. Known results: raw `tools/build_frontier_map.py --match` outputs, verbatim

### N2 run a (candidate phrasing)

```
$ python3 tools/build_frontier_map.py --match "conductor-controlled Weil bound for the Miller primitive U and the Kummer sheaf of f_{N,P}"
KR-IC-5ea2f8  score=6  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-fbdb61  score=5  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-e2d81b  score=3  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
```

### N2 run b (candidate phrasing)

```
$ python3 tools/build_frontier_map.py --match "character sums of Miller function values are square-root small regardless of degree"
KR-RHO-53c89f  score=8  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=6  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-0d2021  score=4  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-49c882  score=4  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5931ee  score=4  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
```

### N2 run c (candidate phrasing)

```
$ python3 tools/build_frontier_map.py --match "non-homomorphic section recovers k only at the random rate"
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-53c89f  score=2  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5ea2f8  score=1  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=1  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
```

### N2 run d (own phrasing)

```
$ python3 tools/build_frontier_map.py --match "Weil bound Kummer sheaf Lang torsor character sum Miller function equidistribution"
KR-IC-5ea2f8  score=6  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-fbdb61  score=5  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-8b9daa  score=4  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
```

### N2 run e (own phrasing)

```
$ python3 tools/build_frontier_map.py --match "elliptic divisibility sequence ratio psi_{k-1}/psi_k character sum flatness"
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
```

### N2 run f (own phrasing)

```
$ python3 tools/build_frontier_map.py --match "Lang torsor character of E(F_p) Kummer sheaf Euler-Poincare conductor square-root cancellation"
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

### N2 reading

KR rows hit, with their KRMAP statements (from `atlas/KRMAP.md`, 51 KR rows in total):

- KR-RHO-53c89f (textbook_fact/proven; score 8 in run b, 2 in run c, absent from runs a, d, e, f): "Transfer attacks apply only to special curves." MOV/Frey-Rueck need a small embedding degree; Semaev/Satoh-Araki/Smart need trace one; generic curves have neither, so these are curve checks and not ECDLP algorithms. ADJACENT: it is the only semantic hit and the row cited as `known_results` by both Miller leads. It says nothing about non-homomorphic F_p^*-valued maps or character sums, so it does not make AC-1 a known result.
- KR-RHO-13bf67 (textbook_fact/proven): Shoup/Nechaev generic lower bound, Omega(sqrt p) group operations. Consistent with AC-1; AC-1 claims no algorithm.
- KR-IC-5a43e5 (known_mechanism/proven): Semaev summation polynomials; row says novelty must lie in representation, factor base, elimination or solver. Lexical for AC-1 (it is not an IC mechanism).
- All other KR hits (KR-IC-5ea2f8, -fbdb61, -73db3f, -f5c584, -46d822, -5765d2, -791cb7, -e2d81b, -8b9daa, -889857, -0d2021, -49c882, -5931ee, -081a58, -1fcdbc, KR-RHO-6239aa): lexical, matching "Weil" (Weil descent), "degree", "random" or "rate". None concerns character sums, Kummer coverings, Lang torsors, division polynomials or elliptic nets.

Scan of KRMAP.md for the literature vocabulary of this candidate (Shparlinski, Kohel, Perel'muter, Perret, Castro, Moreno, Lauter, Stange, character sum, exponential sum, Bombieri, Deligne, Katz, Kummer, Lang torsor, sheaf, Hasse): the only matches are "Weil descent" and "Weil restriction" in index-calculus rows. The program's known-results map therefore has no row for the analytic technique AC-1 rests on. A lexical or KRMAP miss proves nothing about the literature, so I retrieved it (next table).

### Literature retrieval log (WebSearch and WebFetch were available; PDFs were saved, copied into `_ac1_raw/dl_*` and read with pdftotext)

| source | what I read | provenance |
|---|---|---|
| Shparlinski, Stange, Character sums with division polynomials, Canad. Math. Bull. 55 (2012) 850-857, arXiv:0912.5246 | abstract; full preprint text. Lemma 4: for a non-principal multiplicative character eta of F_q^*, f in F_q(E) of degree d that is not an m-th power (m | q-1), and ANY character omega of E(F_q), the sum over the points with f(P) finite of omega(P) eta(f(P)) is at most 2 d sqrt q. Lemma 5: the same over a subgroup H, by orthogonality over the characters trivial on H. The authors attribute Lemma 4 to Chen, Monatsh. Math. 154 (2008) 1-10 (Prop. 1), which they trace to Perret, Multiplicative character sums and Kummer coverings, Acta Arith. 59 (1991) 279-290. Their theorems are for quadratic characters. | retrieved (primary preprint text) |
| Bhakta, Shparlinski, arXiv:2507.09271 (correlations of character sums of division polynomials under shifts) | abstract/intro and PDF text. Lemma 2.3 (from the Shparlinski-Stange lemma): for a non-principal multiplicative character chi, Psi in F_p(E) not a nontrivial power, the sum over n of chi(Psi(nP)) e_R(an) is bounded by deg Psi times sqrt p. Question 1.1 asks when the correlation of chi(psi_n(P)) with chi(psi_{n+h}(P)) is o(N); the authors say they cannot answer it and prove only bounds on an average over h <= H, nontrivial for H in two ranges with a gap between them that they call an open question. They treat any chi of order d. | retrieved (primary preprint text) |
| Castro, Moreno, Mixed exponential sums over finite fields, Proc. AMS 128 (2000) 2529-2537 | NOT read. The statement as quoted in Wu-Ni, arXiv:2608.12758v3, Theorem 2.1 (PDF text read): the sum over X(F_p) of chi(f(P)) psi(g(P)) is at most (2 g_X - 2 + s + l + deg(g)_inf - r) sqrt p, s = number of distinct points in the support of div f, with f not an m-th power and g not of Artin-Schreier form; they say it improves Perel'muter. With g = 0 this is the pure Kummer bound (2 g_X - 2 + s) sqrt p. The additive twist there is psi(g(P)) with psi additive on F_p, not a character of the group E(F_p). | retrieved, secondary (primary unread) |
| Perel'muter, Estimation of a sum along an algebraic curve, Mat. Zametki 5 (1969) 373-380 | bibliographic record and an abstract-level summary (sums of e(phi(P)) chi(psi(P)) over rational points of a curve, bound c sqrt q with c depending on degrees) from search snippets | retrieved (bibliographic only), content unread |
| Kohel, Shparlinski, Exponential sums and group generators for elliptic curves over finite fields, ANTS-IV, LNCS 1838 (2000) 395-404 | bibliographic record. The author's PDF was unreachable (connection refused). The statement as quoted in Ahmadi-Shparlinski, arXiv:1302.4210, Lemma 1 (text read): for ordinary E, a point G of order T and any group character chi of E(F_q), the sum over n in Z_T of psi(x(nG)) chi(nG) (printed chi(G)) is O(q^{1/2}). Additive character of x only. The candidate's "Cor. 1" label was not checked. | retrieved, secondary |
| Lauter, Stange, SAC 2008 (LNCS 5381 (2009) 309-327) | search record only. Correct title: The elliptic curve discrete logarithm problem and equivalent hard problems for elliptic divisibility sequences. EDS Association, EDS Residue and EDS Discrete Log are each solvable in subexponential time iff ECDLP is. The candidate's citation gave no title. | retrieved (bibliographic only) |
| Weil II; Deligne, SGA 4 1/2 "Sommes trig."; Grothendieck-Ogg-Shafarevich | not retrieved | recalled |

The load-bearing citation for the constant 2 (rather than 2N) is therefore recalled, with two retrieved neighbours: Shparlinski-Stange Lemma 4 gives the right shape (Kummer x any group character, genus 1) with the degree constant, and Castro-Moreno (secondary) gives a support-count constant for a Kummer sum twisted by an Artin-Schreier character. The Kummer x Lang statement with the support-count constant is not in anything I retrieved. I checked the Euler-Poincare count by reasoning (rank-1 tame sheaf on E minus {P,O}, chi_c = -2, H^0_c = H^2_c = 0, weights at most 1, so dim H^1_c = 2) and the orthogonality step for a cofactor h > 1 (average of h characters, each at most 2 sqrt p). That is reading, not a verification, and the primary sources for the support-count form are still owed.

Repo context for the same ingredient. KN-LIT-7639 and KN-LIT-f6de4b record that the program's own hypothesis (H1) (multiplicative Weil/Bombieri on a genus-g curve with constant (2g-2+2m) sqrt p, m = distinct zeros and poles) is only partly traced: the explicit constant and general character order on curves are listed as owed, and Perel'muter was not retrieved. KN-FIND-ffe1df (the O2 line) already uses (H1) as an input. The two retrievals above bear on those owed items (Lemma 4 for general eta on genus 1, degree form; Castro-Moreno as quoted for the support form). I did not edit any KN file. KN-LIT-018 (Stange, The Tate pairing via elliptic nets, in the KB) is the literature for expressing Miller/Tate values through net values; K2 is of that family but is itself unreviewed.

### Exactly what is new relative to that literature

1. AC-1's inequality is the Shparlinski-Stange Lemma 4 sum with the degree d replaced by the support count s. For f = f_{N,P}, d = N so Lemma 4 yields 2N sqrt p (vacuous, N ~ p), while s = 2 yields 2 sqrt p. I found no retrieved source that states this for the Miller function. My search was a handful of queries and four PDFs read (a fifth, Mak-Zaharescu arXiv:1309.1726, was extracted and only searched for the keywords; it adds nothing), so this is a weak negative.
2. The N-th root device: chi o U = (chi^u) o f with u = N^{-1} mod (p-1), and the local monodromy of the Kummer sheaf at P and O is chi^{+-1}, nontrivial. Elementary.
3. The bookkeeping: what it does to the two leads.
Everything else is standard. Call it a standard combination (Lemma 4 plus a support-count refinement plus the Lang-torsor twist), not a new theorem.

### C1c against the literature

The candidate says C1c extends Shparlinski-Stange "beyond quadratic chi". That wording is not supported: Lemma 4 is already stated for any non-principal eta, and Bhakta-Shparlinski treat any chi of order d, so generality in chi is not the new thing. What is not in either paper:

- The sum in C1c is the complete, unaveraged sum of chi(r_k) e(ak/N) with r_k = psi_{k-1}(P)/psi_k(P), i.e. the shift-1 correlation of chi(psi_{k-1}) with the conjugate chi-bar(psi_k). Bhakta-Shparlinski's Question 1.1 is about chi(psi_n) chi(psi_{n+h}) with the same chi, for individual h; they prove only bounds on an average over h and state the individual case is open. For quadratic chi (chi-bar = chi, psi_k(P) != 0) the two coincide at h = 1: chi(r_k) = chi(psi_{k-1}) chi(psi_k). For chi of order above 2 they differ and C1c does not answer Question 1.1.
- If K2 holds (U(kP) = c r_k C^{k/N}), the drift C^{k/N} gives chi(C)^{ku}, a phase that is not a character of Z/N; expanding it over characters of Z/N on the window costs a factor O(log N), which matches the candidate's 2 sqrt(p) log N. That is my reading of the candidate's route. I did not run or re-derive the completion step.
- Consequence if all of that is right: for P of prime order N with gcd(N, p-1) = 1 and quadratic chi, the shift-1 sum over one period of P is O(sqrt p log N), which would settle one case of a question the authors describe as out of reach of their techniques. A short argument that settles a published open case is a reason to ask for independent review of K2 and of the completion step before anyone cites it. Also unchecked: Bhakta-Shparlinski's window is up to R = d ord P, so for quadratic chi the full window sums (1 + chi(C)) times one period, which vanishes if chi(C) = -1; the relation to their stated ranges needs a look.
- C1c does not cover the single-sequence sums S_{chi,P}(N) = sum chi(psi_n(P)) of Shparlinski-Stange, nor same-chi correlations for chi of order above 2.

Status of C1c: possibly new, conditional on K2 (unreviewed) and on gcd(N, p-1) = 1, unreviewed, not rerun here. The lead-level verdict does not depend on it.

## N3 and N4 and verdict

### N3 ledger dedup

Method: grep of `ledger/.index/proposals.jsonl` (2678 rows) and `ledger/.index/hypotheses.jsonl` (2131 rows) with `_ac1_raw/ledger_grep_ac1.py` (OR-score) and `_ac1_raw/ledger_and_ac1.py` (AND-groups), run with `python3 -I`. Terms: miller, kummer, weil, lang torsor, conductor, f_{n,p}, character sum, psi_{k-1}, division polynomial, e3a6f1, n-th root, quasi-homomorphism, zeta-defect, unreduced, kummer sheaf, pairing-free, non-homomorphic, elliptic divisibility, shparlinski, kohel, perel, sheaf, deligne, katz, lauter, stange, castro, bombieri, equidistribut, square-root cancellation. The index covers proposals and hypotheses only; evidence, decision and experiment records were not searched. Raw outputs are in the appendix at the end of this file.

Hits that may be the same object or a near neighbour (id [status] first 100 characters of the claim):

```
IDEA-20261017-e3a6f1 [proposed] E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
IDEA-20261016-09fd08 [proposed] y^2=x^3+ax+b/F_p, G=<P> odd order n prime to p, chord slope lam(R,S)=(y_R-y_S)/(x_R-x_S) (tangent at
IDEA-20261009-9f89ae [proposed] The linear-complexity profile of (W_n mod p) for n <= L grows as L/2 (random profile) for L up to 10
IDEA-20261009-c8433d [proposed] The connecting homomorphism agrees with Miller's algorithm up to a fixed convention on 100% of insta
IDEA-20261009-8d09c0 [proposed] (i) the zero set of W mod p in a box is exactly a lattice of index |<P_1..P_r>| (Lauter-Stange); (ii
H-ECDLP-f8cea6 [proposed] A public reduced-Tate character can be evaluated and decoded without hidden scalar input on the fini
IDEA-20260807-569c82 [proposed] (A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^
IDEA-20260930-8e3b75 [proposed] REPRESENTATION CLASS AND STAGE (RQ-ECDLP-623a32 vocabulary, filed under RQ-ECDLP-c1b7b1 because the
H-CRYPTO-fde1f1 [analyzed] For the two fixed normalized sheaf families on the declared generic base curve locus, the addition-p
H-PSEUDO-83817b [specified] For any prime p, prime-order elliptic curve E/F_p with group order N, generator G, and factor base F
H-PFDR-8a4f44 [proposed] THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
IDEA-20260829-4b34c5 [proposed] TWO-SIDED CLAIM, both sides informative. POSITIVE SIDE. The accepted set D_chi, defined as the set o
```

Full records opened (exactly three, the cap), by exact path:

1. `ledger/proposals/IDEA-20261017-e3a6f1.yaml`. SAME OBJECT: the canonical primitive U = T^(1/N) of the Miller cocycle, claims K1 (Weil-reciprocity cocycle, U unique primitive), K2 (U(kP) = c r_k C^(k/N), r_k = psi_{k-1}(P)/psi_k(P)), K3/H1 (ell(k) uniform in Z/(p-1) jointly with characters of Z/N). Status proposed, novelty unverified. No Weil, Kummer or Lang-torsor bound anywhere in it; H1's `rigorous_support` says character sums of such terms are bounded "in the recalled literature (unread)". The proposals/hypotheses index shows no hypothesis referencing it (a grep for the id returns only the proposal itself); evidence, decision and experiment records were not searched, so I cannot say whether its minimal test was run anywhere. AC-1 is the derivation H1 was waiting for. Its recorded PAIR and TRICHOTOMY are the same as AC-1's (section N4).
2. `ledger/proposals/IDEA-20261016-09fd08.yaml` (zeta-defect Z, the additive analogue). Its H1 `rigorous_support` is "Weil-type equidistribution plausible, unread". This is the cell the candidate's H-AC1 addresses. Not the same object as U (F_p-valued, Artin-Schreier side). See the conflict note in section 6.
3. `ledger/proposals/IDEA-20261009-9f89ae.yaml` (period-finding on EDS mod p). A control predicting a random linear-complexity profile for W_n mod p, citing Lauter-Stange (recalled) for the ECDLP-equivalence. Adjacent to C1c/C1d (SO-NET), but the statistic differs (linear complexity versus character sums), so not the same object.

Decision on the other hits, from their index rows only (not opened): IDEA-20261009-c8433d (generalized-Jacobian extension class equals the Tate pairing; trivial on l-parts with l not dividing p^k - 1) and H-ECDLP-f8cea6 / IDEA-20260807-569c82 (reduced Tate character and the pairing oracle) are siblings in the same transfer family, on the pairing-alive side or the control side of AC-1, not the same object. IDEA-20260930-8e3b75 (deformation defect digit) is a non-homomorphic local-section sibling of the zeta-defect. IDEA-20261009-8d09c0 (hidden kernel lattice via elliptic nets) is the Lauter-Stange/SO-NET neighbour. H-CRYPTO-fde1f1 (trace sheaves pulled back through addition, correlation complex) uses the same machinery (Weil-Deligne on sheaf trace functions) for coordinate statistics under P+Q; its object is different. H-PFDR-8a4f44 and IDEA-20260829-4b34c5 use character-sum bounds on E for multiplicative-subgroup accepted sets and x(R) in H; different objects. H-PSEUDO-83817b is the additive-DL-character sum on a small-x base; different object (section N1, run d).

Finding for the dedup question: nothing in the proposals/hypotheses index contains the Kummer x Lang bound, the conductor argument, or a Weil-type bound for Miller-function values. The only record of the same object is IDEA-20261017-e3a6f1, which leaves the bound as an unread literature pointer.

### N4 notation check

AC-1 states the pair as: representation R2, the F_p^*-valued canonical section U of the G_m-extension of class [P] (and, for the zeta-defect cell, the G_a analogue); operation set Sigma = translation by S, acting on U only through the explicit defect g_{R,S}(P); trichotomy class coordinate-dependent.

This is the pair already recorded in IDEA-20261017-e3a6f1 (its `mechanism`): "PAIR: representation = F_p^*-valued canonical quasi-homomorphism U (R2, transfer); Sigma = translation by S, acting on U only through the explicit defect g_{R,S}(P). TRICHOTOMY: coordinate-dependent. LOSSY TEST: the graph R->(R,U(R)) is a subgroup isomorphic to E(F_p)[N], a change of coordinates and not proposed; U alone is lossy by collisions." So AC-1 introduces no new (representation, operation set) pair. It bounds a statistic of an existing one.

Is it a recorded rigidity result in new notation? No, and the relation is as follows.
- IDEA-20260806-c5d183: a projection that propagates deterministically under the full translation action of a prime-order group is constant or injective. Qualitative and exact.
- IDEA-20260901-863e36: propagation is a property of a projection paired with an operation set; the propagating lossy objects are the block systems of the group generated by Sigma. Structural.
- KN-FIND-ffe1df Theorem C: exact sum-compatibility plus associativity forces a homomorphism onto a group of order dividing N, impossible for prime N and 1 < M < N. The finding itself says it covers the exact case only; the approximate case is where it uses the Weil/Bombieri input (H1).
- KN-OPEN-020: bounded-degree algebraic factor bases. Not applicable: AC-1 is not a factor base, so the factor-base-escape clause of the constraint block does not arise.
None of these states a bound on a complex correlation sum. AC-1's statement is of the form |sum_R chi(U(R)) psi(R)| <= 2 sqrt p over characters psi of G, and the rigidity results neither imply nor follow from it: they are statements about exact propagation and contain no Fourier quantity, so they cannot bound a correlation sum, and a correlation bound for one coordinate-dependent object says nothing about the exact-propagation classes. (The N | p-1 control cell, the reduced Tate pairing t(P,kP) = t(P,P)^k, is an injective homomorphism into mu_N, i.e. the injective case of c5d183, not a coordinate-dependent object; it is the positive control where the characters peak, not an example for this argument.) The connection: with Sigma the full translation action, the characters of G are exactly the covariant functions, so correlation with them is the quantitative form of "does U propagate under Sigma". AC-1 says no, to within 2 sqrt p / N, for one object and only for linear statistics. That is a quantitative companion of the coordinate-dependent class, proved with the same analytic input the O2 line used, and not a new rigidity theorem. It does not touch KN-OPEN-020.

### 6. Verdict, residual cells, conflicts, review owed

Verdict: `advances_lead`; lead `LEAD-TRF-miller-cocycle-nonhom-transfer`.

Why not the other three values:
- `duplicate_of_lead`: the lead and IDEA-20261017-e3a6f1 contain no bound; AC-1 changes H1's character clause from heuristic to derived. A closed lead whose obstruction AC-1 fails to answer would make it a duplicate; the closed hits are consistent with AC-1 and AC-1 claims to escape none, so that rule does not fire.
- `known_result`: no KRMAP row. The literature has the inequality in substance (Shparlinski-Stange Lemma 4 degree form; Castro-Moreno support form, secondary), so the novelty is application only; I state exactly what is new in N2. If the program's convention treats "standard technique applied to a new function" as known, the downgrade would be to `known_result` for the theorem and `advances_lead` for the bookkeeping. I chose `advances_lead` because the lead is open and its H1 is still waiting for exactly this support.
- `new`: no. The object is the open lead's object.

Mismatch with the lead's discriminator (do not read this as closing the lead): the lead asks for equidistribution at the 1/p rate. AC-1 proves p^{-1/2}. The ratio clause (Smart-ratio success 1/p, which the candidate's C1b bounds only at p^{-1/2}), nonlinear statistics and multi-query use of U, the zeta-defect cell and the generalized-Jacobian cell stay `open_unexamined`. At most the character-level cell, in the scope "linear (Fourier) statistics of U and of Kummer characters of U, prime-order N, gcd(N, p-1) = 1", could move to closed_obstructed(theorem), after independent review and after the lead's own toy replay (K1/K2 conventions, the N | p-1 positive control). Proposed, not applied; I changed no record.

For LEAD-EXO-miller-pairing-cocycle: its K1/K2 verification step is not discharged by AC-1 (K2 unreviewed). The candidate's own caveat (recovery cell moves only after review of C1d) is right.

Conflict with the candidate's H-AC1 ("Swan conductor <= 2 at O, so |sum| <= (1 + Swan) sqrt p" for the zeta-defect cell): the sibling dossier says the zeta-defect sum is Artin-Schreier with a degree-dependent conductor, so the bound is vacuous. From the K1 formula in IDEA-20261016-09fd08, Z(R) = -(1/n^2)[y f_n''(x)/f_n'(x) + (3x^2+a)/(2y)], the function has poles at the zeros of f_n' (about n^2/2 of them) and at y = 0, not only at O. If K1 is as printed, counting only O undercounts and the sibling's reading is the safer one. I did not derive the conductor myself. H-AC1 is not endorsed, and the cell stays open_unexamined either way. The verdict does not depend on it.

Numbering and merge: the candidate names the overlap "scout-arithmetic-statistics C1"; in `scout/scout-arithmetic-statistics.md` the Kummer-conductor theorem is C2 (C1 there is an occupancy calculator). C2 there states the same theorem for general f with s_e(f) sqrt p, the same U corollary, and reports a toy table with maximum |S|/sqrt p at 2.014-2.020 against 2 + 2/sqrt p; I did not rerun it. `gate-p-adic-and-tropical-geom-C1-the-Miller-primitive-U-is-the-Lauter-.md` covers U as the Lauter-Stange EDS ratio (K2, C1d) and has no analysis section yet. Merge all three into one item filed against the same lead.

Review owed before any disposition change (none done by this gate): (1) independent derivation of the Kummer x Lang bound with the support constant, including a primary read of Castro-Moreno or Perret and the cofactor case; (2) K2 on independent code; (3) the O(log N) completion in C1c; (4) the N | p-1 control cell; (5) whether C1c touches Bhakta-Shparlinski Question 1.1 for quadratic chi, which is the only piece I could not place as known.

Provenance summary: every citation above carries its status in the N2 table (retrieved primary preprint text: Shparlinski-Stange, Bhakta-Shparlinski; retrieved secondary: Castro-Moreno via Wu-Ni, Kohel-Shparlinski via Ahmadi-Shparlinski; retrieved bibliographic only: Perel'muter, Lauter-Stange; recalled: Weil II, Deligne SGA 4 1/2, GOS). Predictions in the candidate (bound 2 sqrt p, flatness) are the candidate's and are not outcomes of this gate.

## Appendix. Raw N3 ledger-index grep outputs, verbatim

### A1. OR-score grep (`python3 -I ledger_grep_ac1.py miller kummer weil "lang torsor" conductor "f_{n,p}" "character sum" "psi_{k-1}" "division polynomial" e3a6f1`), top 25 per file

```
##### proposals.jsonl count 182
4|IDEA-20261017-e3a6f1|proposed|miller,weil,f_{n,p},e3a6f1|The Miller cocycle has a canonical primitive U: E(F_p)[N] -> F_p^* exactly when |E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
2|IDEA-20260807-e7eb5d|proposed|miller,weil|THE SELF-PAIRING INSTRUMENT AND ITS NULL - a pure-Python Miller-loop calculator |(A) WHY THIS EXISTS. This lane's three closure records (IDEA-20260807-464ff8, IDEA-20260807-30868b, 
2|IDEA-20261002-8f26ce|proposed|weil,character sum|Artin-Schreier curves of genus 5 and 6 over F_2 as the explicit-model column of |The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve
2|IDEA-20261006-237ce0|proposed|miller,weil|The Weil pairing of one order-5 point with itself is 1 on y^2 = x^3 + 2x + 3|Let E be y^2 = x^3 + 2x + 3. Let p be the smallest prime with p > 20 and p < 120 such that E is nons
2|IDEA-20261006-24268f|proposed|kummer,division polynomial|Affine exact-order-3 counts differ on y^2=x^3+4x+6 and y^2=x^3+5x+8 over F_41|REPRESENTATION. The objects are affine points of exact order 3, read as pairs (x, y) in F_41^2, not 
2|IDEA-20261006-42b03f|proposed|kummer,division polynomial|Sum of F_31-rational roots of psi_3 on y^2=x^3+1 is not zero|REPRESENTATION. The object is the monic 3-division polynomial of y^2=x^3+1 over F_31, in the affine 
1|IDEA-20260726-011|unverified|kummer|Twist-blind Kummer walk — does the shared x-line carry cross-twist information a|E and its quadratic twist E' share the Kummer line P^1 = E/±1, and the differential-addition law the
1|IDEA-20260727-006|adaptation|weil|Equidistribution-resolution gap - the factor-base size at which Weil error terms|For prime-field Semaev index calculus with an interval (or any Fourier-accessible) factor base F = {
1|IDEA-20260731-008|unverified|weil|Isogeny-transfer cost gate — when a short ordinary isogeny to a special-curve fa|Let E/F_p be a prime-field curve with prime-order subgroup G of order N. Suppose there exists a publ
1|IDEA-20260731-017|unverified|conductor|Large-conductor vertical barrier — measure ECDLP-meter discontinuity across a pr|Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
1|IDEA-20260801-004|unverified|conductor|Large-conductor vertical barrier: isogeny-chain degrees and the cost of forcing |For ordinary curves over generic prime fields, forcing a Semaev/Gröbner heavy tail by choosing a sec
1|IDEA-20260805-0d2a21|unverified|weil|The goal says prime-field decomposition cost and every measurement is a boolean |GOAL-SIG-001's objective is written in terms of "prime-field decomposition cost" and RQ-SIG-001's sc
1|IDEA-20260805-128f35|unverified|conductor|The involution budget of a cyclotomic conductor: an exact census of every order-|The engine of the disclosed HAWK attack (KN-LIT-7592) is stated by its own entry as "the object hidi
1|IDEA-20260805-4ed1b1|unverified|weil|Two p-independent forced constants for the chi=1 xedni window: an absolute ceili|TWO constants, both derived before any run, both independent of p, and both absent from every record
1|IDEA-20260805-5a9d2c|unverified|weil|The XEDN relation-coefficient bound is Hermite's constant, not geometry: max_|co|Every one of the fourteen Mordell-Weil relations ever recorded by GOAL-XEDN-003 has support 3 or 4 (
1|IDEA-20260805-5bf632|unverified|weil|The XEDN coefficient metric is anti-monotone in its own data: replace "shortest |H-XEDN-005 and its four predecessors measure "the infinity-norm of the shortest nonzero Mordell-Weil
1|IDEA-20260805-bd61c3|unverified|weil|max_|coeff| = 1 is a theorem about norm-2 lattice vectors at support 3, not a me|The primary metric of EXP-XEDN-004 -- the infinity-norm of the shortest group-law-verified Mordell-W
1|IDEA-20260805-cf2d5a|proposed|kummer|The Semaev summation cover is a 2-Kummer cover, not a generic one: its geometric|THE STATEMENT. Let E : y^2 = f(x) = x^3 + Ax + B be non-singular over a field k of characteristic > 
1|IDEA-20260805-e5dd09|unverified|weil|The rank budget, not the section density: exact forced values Pr[rank = 8] = 1 -|For the frozen GOAL-ICLIFT-001 family y^2 = x^3 + b(t) over F_p with deg b = 6 exactly, the geometri
1|IDEA-20260807-15f103|known_in_substance|conductor|CLOSURE with named obstruction: smooth-conductor descent within an isogeny class|Within an ordinary isogeny class (fixed trace t, fixed group order N), the CM conductor f varies fro
1|IDEA-20260807-3f5545|proposed|conductor|COMPLETE-CLASS LEVEL-VECTOR STRATIFICATION: enumerate an entire toy F_p-isogeny |(A) THE OBJECT IS A VECTOR, NOT A NUMBER, AND THIS LANE HAS BEEN TREATING IT AS A NUMBER. A curve's 
1|IDEA-20260807-44ba75|proposed|weil|CM SUPPLIES THE RANK CONTROL XEDNI HAD TO BUY WITH MESTRE'S CONDITIONS, BUT IN T|(A) WHAT XEDNI PAID FOR AND WHAT CM GIVES FREE. Silverman's construction (KN-LIT-020) needs the glob
1|IDEA-20260807-4fc635|proposed|kummer|THE NULL OBJECT FOR "MODEL MATTERS" IS THE SAME MODEL UNDER A RANDOM CHANGE OF C|(A) THE CONTROL THIS LANE CANNOT DO WITHOUT, STATED AS AN OBJECT RATHER THAN AS A CAVEAT. Every L11 
1|IDEA-20260807-569c82|proposed|weil|THE PAIRING ORACLE IS THE CONSTANT ORACLE ON A PRIME-ORDER SUBGROUP, AND NO CM E|(A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^
1|IDEA-20260807-5f24d7|proposed|miller|THE MOV COST FUNCTIONAL IS A MINIMUM OVER THREE BRANCHES, NOT ONE, AND ITS BINDI|(A) THE DEFECT BEING REPAIRED, AND ITS TWIN. This campaign has a recorded cost-model failure - accor
##### hypotheses.jsonl count 115
2|H-ICEX-652b0d|proposed|kummer,division polynomial||For a declared, frozen panel of cheap projections of E(F_p) that contains no division polynomial - t
2|H-JMV-001|approved|miller,conductor||Figure 1 of Jao-Miller-Venkatesan 2005 (arXiv:math/0411378v3) misreports the Frobenius conductor c_p
1|H-ALBIN-001|analyzed|weil||Autolab package `bin_exp001` (binary-field ECDLP) produces a scoped empirical measurement that can b
1|H-ALBIN-913542|proposed|weil||SCOPE: the primary texts recorded in this corpus as the sources for the last-fall-degree bound on We
1|H-ALPF-023|analyzed|kummer||Autolab package `round012_exp028_theta_kummer_surface` (prime-field ECDLP) produces a scoped empiric
1|H-BINSTD-3b1f2d|analyzed|weil|On binary toys (n,ℓ)∈{17}×{3,4} with frozen V and shared XOR-SAT pin, charged co|SETTING. Semaev S_m via resultant recursion (KR-IC-5a43e5) on x-coordinates with factor base {P : x(
1|H-BINSTD-61dad7|approved|weil|Weil-bound vacuity of subspace abscissa density at every index-calculus dimensio|CLAIM (control / structural certificate; HOLD-X4). On E_a : y^2 + xy = x^3 + a x^2 + b over F_{2^n} 
1|H-BINSTD-6feaa2|approved|weil|An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completenes|CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f
1|H-BINSTD-85e778|analyzed|weil|Reduction-polynomial Hamming weight w is a constant-factor confound on descended|CLAIM (control / measurement; HOLD-I; NO ATTACK). Setting: polynomial-basis F_2-multiplication tenso
1|H-BINSTD-880e8b|analyzed|weil|At fixed dim(V)=ℓ on toy binary cells, Spearman ρ between dim(V·V) and remaining|CLAIM (heuristic_validation / encoding-size instrument; NO ATTACK; NO EXPONENT). Let V ⊂ F_{2^n} be 
1|H-BINSTD-944a66|analyzed|weil|Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen|SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of 
1|H-BINSTD-a177b6|analyzed|weil|HOLD-T: affordability table WITHOUT /mu (orbit cancelation); Koblitz vs ordinary|SETTING. Binary curves over F_{2^n}, CNF-XOR / S_{m+1} descended point- decomposition cost at toy sc
1|H-BINSTD-af1faf|analyzed|weil|After EV-BINSTD-f1d8e2, raised dimVV/N_var floors make the legacy 0.70 Spearman |CLAIM (heuristic_validation / encoding-size INSTRUMENT; NO ATTACK; NO EXPONENT). Successor to H-BINS
1|H-BINSTD-b102b7|analyzed|weil|At fixed dim(V)=ℓ on toy binary cells, Spearman ρ(r_Tr, N_nl) ≤ −0.70 across a f|CLAIM (heuristic_validation / encoding-structure instrument; NO ATTACK; NO EXPONENT). Let V ⊂ F_{2^n
1|H-BINSTD-ce918e|analyzed|weil|At fixed dim(V)=ℓ on toy binary cells, peak RSS of S_3 encode+one-shot solve und|CLAIM (heuristic_validation / memory instrument; NO ATTACK; NO EXPONENT). Let V ⊂ F_{2^n} be an F_2-
1|H-BINSTD-d460e5|supported|weil|After Karabina auxiliary symmetrisation on toy binary S_3 cells, median residual|CLAIM (heuristic_validation / encoding-residue instrument; NO ATTACK; NO EXPONENT). For each Stage-1
1|H-CANL-2d15e2|approved|weil||TEST BOUNDARY. Let p=19. Let C_cm be y^2 = x^3 + 1 over Q with P_cm = (2, 3), C_n1 be y^2 = x^3 + x 
1|H-CLGP-a9ce97|specified|conductor|Stage 0 ray-class torsor bridge ordinary conductor-1 curve identities — n=2 — be|Fix the exact count identity of IDEA-20260812-a3720a before any later-stage claim. Stage 0 asserts o
1|H-CZLIFT-9a32e9|weakened|weil|Small rational points on E/Q (and on E(K) for a quadratic K) grow like (log H)^{|For E/Q of rank r the number N_E(H) of rational points of naive height H(x) <= H grows like c_E (log
1|H-DREG-152cff|proposed|weil||SCOPE: boolean chained Semaev built by src/semaev_tree.py at t = 3, ti = 0 (m = 3), Weil-descended t
1|H-DREG-1d0e5d|approved|weil|One F_4 Vélu edge does not move the degree-filtration rank profile of the chaine|On the single certified ordinary degree-2 edge frozen in EXP-DREG-dd668d, the full-column boolean Ma
1|H-DREG-2b51fb|approved|weil|One F_5 S_3 first-fall gap against a support-matched null|On the first short-Weierstrass curve y^2 = x^3 + A x + B over F_5, in lexicographic order of (A, B),
1|H-DREG-91be14|proposed|weil||SCOPE. The boolean chained Semaev system at m = 3, t = 3 as built by src/semaev_tree.py and Weil-des
1|H-DREG-c44a0d|approved|kummer|The eliminated graph of one certified Vélu edge does not lower last-fall degree |On the certified edge produced by EXP-DREG-dd668d, at rung n=1, let I_native be the codomain chained
1|H-DREG-dafc39|proposed|weil||SCOPE. The boolean chained Semaev system at m = 3, t = 3, ti = 0 built by src/semaev_tree.py and Wei
```

### A2. AND-group grep round 1 (`python3 -I ledger_and_ac1.py ...`)

```
IDEA-20260805-2acde5 | prop | unverified | unreduced | Where the confidence actually rests: audit the two sentences in SQIsign's own Section 10 t | If the audit of IDEA-20260805-c4ae3d holds, the headline claim about SQIsign is TRUE: no torsion ima
IDEA-20260808-c4b462 | prop | proposed | non-homomorphic | Signed-y approximate-quotient four-list cascade: test whether a public non-homomorphic coo | CONDITIONAL THEOREM TARGET, NOT A RESULT. Let G=<P> have prime order N and Q=[k]P. Put M=L=floor(N^(
IDEA-20260816-ec9a47 | prop | proposed | n-th root | The step from a noise variance to a noise infinity-norm assumes the N coefficients of the  | (A) Every parameter derivation that starts from a variance and ends at a decryption-correctness cond
IDEA-20260818-f8dc30 | prop | unverified | n-th root | TRANSFORM-DOMAIN (CYCLOTOMIC-COSET) AUDIT OF QC-SD: the Berlekamp-Massey weight threshold  | Quasi-cyclic syndrome decoding at HQC's shape (R = 1/2, secret (x,y) with wt(x) = wt(y) = w, ring R 
IDEA-20260909-4c5ee9 | prop | proposed | non-homomorphic | Import PO96M / PO96AB*: residual/nonlinear factor bases for non-homomorphic IC | An exact DLP-free residual label space of size O(q^{1/2-epsilon}), or a nonlinear gauge-invariant pr
IDEA-20260911-2dd68d | prop | proposed | non-homomorphic | Resolution-matched, degeneracy-screened re-test of the Teichmuller non-homomorphic contras | After (i) excluding the m=1 entry as a mathematical tautology (never entering any agreement statisti
IDEA-20260930-39ad61 | prop | proposed | lang&torsor | THE TRANSPORT STEP HAS ITS OWN PREPROCESSING FRONTIER: a Bernstein-Lange distinguished-poi | CEILING FIRST. No per-target exponent moves. The per-target online cost of the one-table-per-class a
IDEA-20260930-8e3b75 | prop | proposed | non-homomorphic | THE DEFORMATION DEFECT DIGIT: on a prime-order ordinary curve the unique n-torsion lift of | REPRESENTATION CLASS AND STAGE (RQ-ECDLP-623a32 vocabulary, filed under RQ-ECDLP-c1b7b1 because the 
IDEA-20261009-9e4a40 | prop | proposed | non-homomorphic | Teichmueller lifts are useless for index calculus in F_p^* - size, not canonicity, is what | Pr[omega(a) mod p^k is B-smooth] is about rho(k log p / log B), far below Pr[a in [0, p) is B-smooth
IDEA-20261009-9f89ae | prop | proposed | elliptic divisibility | Period-finding on elliptic divisibility sequences mod p has no linear-recurrence shortcut | The linear-complexity profile of (W_n mod p) for n <= L grows as L/2 (random profile) for L up to 10
IDEA-20261016-09fd08 | prop | proposed | quasi-homomorphism | The zeta-defect Z: a lift-free canonical quasi-homomorphism on E(F_p)[n] whose carry is a  | y^2=x^3+ax+b/F_p, G=<P> odd order n prime to p, chord slope lam(R,S)=(y_R-y_S)/(x_R-x_S) (tangent at
IDEA-20261016-53ec5d | prop | proposed | unreduced | Carry law and height window: why the NAIVE section of F_p^* works exactly below p, and its | (M) F_p^*, naive section s(a)=a in [1,p), q(a)=(a^(p-1)-1)/p, integer generator g, d in [2,n-2], k_d
IDEA-20261017-e3a6f1 | prop | proposed | n-th root | The Miller cocycle has a canonical primitive U: E(F_p)[N] -> F_p^* exactly when N does not | E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
IDEA-20261024-5f08bd | prop | proposed | n-th root | General-prime floor lemma: single-orbit genus floor 2^(n-3-e(n)) (n-4) + 1, e(n) from 4-te | For prime n >= 5 and branch quadruples on one sigma-orbit (r = n), m = #{zeta in mu_n : s_S(zeta) !=
H-ECDLP-69301c | hypo | specified | miller&character | Stage 0 cubic-residue identities — p=7, (p-1)/3=2, chi_3(1)=1 — before any doubling charac | Fix the exact cubic-residue exponent identity of IDEA-20260913-1eb65c before any doubling map, any 3
H-ECDLP-c48f2a | hypo | proposed | non-homomorphic |  | THIS IS A NEW, SEPARATELY SCOPED SIBLING OF H-ECDLP-09125b, NOT AN EXTENSION OF ITS ALREADY-DECIDED 
H-ECDLP-f8cea6 | hypo | proposed | miller&character |  | A public reduced-Tate character can be evaluated and decoded without hidden scalar input on the fini
H-ISOU-d1a4a5 | hypo | approved | unreduced |  | The pinned native command may construct and independently verify the selected compact known-CM M8191
H-ISOU-ffa8b0 | hypo | supported | unreduced |  | The pinned native command may construct and independently verify the selected compact known-CM M4449
H-JINV-f20ba3 | hypo | approved | division polynomial&character | Orbit-normalised doubling-slope character gap between j=1728 and a matched-trace ordinary  | Over F_29, let trace mean #E(F_29)-(29+1), computed by enumerating points. Let the orbit-normalised 
H-SEMBIN-ce9e29 | hypo | specified | unreduced |  | On the single summation polynomial S_3 over F_2[z]/(z^3+z+1), with B = 1, the shift x1 -> x1+1 keeps
TOTAL 21
```

### A3. AND-group grep round 2 (the term h-ecdlp-bd1572 over-matches source_refs of a 2026-10-09 batch and is noise)

```
IDEA-20260802-006 | prop | unverified | square-root cancellation | The scalar index set as a tracked object - does multiplicative structure in the INDEX surv | THE TRACKED OBJECT IS THE INDEX SET, NOT THE POINT. For n prime and K a subset of (Z/n)*, define pi(
IDEA-20260805-787c8b | prop | unverified | shparlinski | The HNP success region is a WINDOW in signature count, not a threshold: a pre-derived (m,  | For the standard Boneh-Venkatesan / Nguyen-Shparlinski lattice embedding of ECDSA partial-nonce leak
IDEA-20260829-4b34c5 | prop | proposed | character sum&elliptic | Replace the order-theoretic accepted set by a multiplicative subgroup of F_p*, and use bil | TWO-SIDED CLAIM, both sides informative. POSITIVE SIDE. The accepted set D_chi, defined as the set o
IDEA-20260903-fc1355 | prop | proposed | perel | THE NESTED DIGIT LADDER IS PROFILE-BLIND UNDER THE SEMI-REGULAR NULL: for any ladder profi | Setting as in IDEA-20260830-84cdb7: base d >= 2, nested windows V_s = {x in [0, d^s) : f(x) a square
IDEA-20260926-cafcf1 | prop | proposed | weil bound | THE ABSCISSA DENSITY OF A SUBSPACE FACTOR BASE IS NOT CONTROLLED BY THE WEIL BOUND AT ANY  | Representation class R1 of RQ-ECDLP-623a32 (the abscissa in any F_2-basis); the attack stage whose c
IDEA-20261001-9d8520 | prop | proposed | perel | DOES DOUBLING THE LARGE-PRIME BOUND ABSORB ≥α OF ORPHANED SEMI-SMOOTH RELATION CANDIDATES  | Double-large-prime variants are standard in hyperelliptic / extension-field IC (KR-IC-a4dd54 / KR-IC
IDEA-20261002-711e84 | prop | proposed | perel | Mumford u-coefficient eliminant of a genus-2 Jacobian fibre over F_2, as the membership po | On a genus-2 curve C/F_2 whose Jacobian has a rational point of order 19, the Couveignes fibre of tr
IDEA-20261002-8f26ce | prop | proposed | character sum&point | Artin-Schreier curves of genus 5 and 6 over F_2 as the explicit-model column of the order- | The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve
IDEA-20261006-5db10b | prop | proposed | character sum&point | Doubling-sum character sum on one prime-field curve exceeds one quarter of its support | Let E be y^2 = x^3 + x + 3 over F_47, let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
IDEA-20261009-00514a | prop | proposed | katz | Compute the Serre-Tate parameter q(E^) directly and compare with the j-distance rule | For the lifts of EXP-CZLIFT-17b7eb, v_p(q(E^) - 1) computed from the unit-root splitting (Katz) equa
IDEA-20261009-0bb2cf | prop | proposed | h-ecdlp-bd1572 | Rank required for a Q-lift index calculus - measured N(H) vs the coverage requirement | On every available curve with certified generators (rank 5-29 from the literature plus the rank-30/3
IDEA-20261009-0f3a09 | prop | proposed | h-ecdlp-bd1572 | Summation polynomials are insensitive to the form of p | For fixed (a,b), S_3 and S_4 over F_p have identical monomial support and coefficient identities whe
IDEA-20261009-275a14 | prop | proposed | h-ecdlp-bd1572 | Genus-g covers of E over F_p cost p^(2 - 2/g) >= p (worse than rho) | Measured index-calculus cost for recovering logs in the E-part of Jac(C)(F_p), g in {2, 3}, fits an 
IDEA-20261009-29706a | prop | proposed | h-ecdlp-bd1572 | Lifting a fixed E/F_p to Q - rank and generator heights across the (s, t) lift family | Over 10^4 lifts with |s|, |t| <= 100 of a fixed E/F_p (p about 2^20 and 2^30), the rank distribution
IDEA-20261009-2abd32 | prop | proposed | h-ecdlp-bd1572 | The only existing SNFS for ECDLP is pairing transfer; special p helps only the multiplicat | (a) the embedding-degree distribution of random curves over pseudo-Mersenne p is indistinguishable f
IDEA-20261009-321a1d | prop | proposed | h-ecdlp-bd1572 | Xedni control - dependence probability of fitted lifts | At p about 2^20 and k in {2, 3, 4}, the fraction of dependent k-tuples is <= 10^-3 and every depende
IDEA-20261009-354b14 | prop | proposed | h-ecdlp-bd1572 | Rotation-class factor base control - multiplication by 2 is a bit rotation for Mersenne p  | Pr[P + Q in D_rot | P, Q in D_rot] = |D_rot| / p within sampling error for m in {1, 2, 4, 8}, and th
IDEA-20261009-443717 | prop | proposed | h-ecdlp-bd1572 | Digit-grading factor base under Z[x]/(x^d - c) -> F_p | D = {P : x(P) < 2^(n-k)} has no closure: Pr[P + Q in D | P, Q in D] equals |D|/p within sampling err
IDEA-20261009-4635cf | prop | proposed | h-ecdlp-bd1572 | The computable canonical point lift to E(Q_p) carries no DLP information | The section is independent of the chosen lift, is a homomorphism, satisfies [N] section(P) = O to pr
IDEA-20261009-4b1724 | prop | proposed | h-ecdlp-bd1572 | Lifting to the SNFS number field K = Q(c^(1/d)) leaves the rank/height obstruction unchang | For small analogues p = 2^n - c (n <= 40, d in {2, 3}; d = 5 only for n <= 24), rank E(K) - rank E(Q
IDEA-20261009-57140c | prop | proposed | h-ecdlp-bd1572 | Cyclotomic lift with complete splitting - one K-point gives phi(c) residues and a free Gal | (i) the relation yield ratio R(H) = #trace relations from K-points of height <= H divided by #distin
IDEA-20261009-581f5d | prop | proposed | h-ecdlp-bd1572 | Bounded-height section through a prescribed fibre point - the decomposition step of a func | T_section(d, chi, p) at the Gaussian-heuristic d from E4 exceeds p^(1/2) poly(log p) for every solve
IDEA-20261009-61fc7f | prop | proposed | h-ecdlp-bd1572 | Chevalley classification of homomorphic transfers over F_p (finite control) | No generalized Jacobian of E over F_p with modulus of degree <= 4 (reduced gives tori, non-reduced g
IDEA-20261009-64a1c0 | prop | proposed | h-ecdlp-bd1572 | Embedding degree over a Mersenne prime - k = 2 is impossible and k in {1, 3, 4} are Cunnin | (a) over random prime-order curves over Mersenne p the distribution of k equals the Balasubramanian-
IDEA-20261009-85062c | prop | proposed | h-ecdlp-bd1572 | Small-root threshold for size-constrained decomposition (Coppersmith on S_3, S_4) | The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F
IDEA-20261009-8d09c0 | prop | proposed | lauter&stange | Hidden kernel lattice via elliptic nets, and the elliptic-sieve null test | (i) the zero set of W mod p in a box is exactly a lattice of index |<P_1..P_r>| (Lauter-Stange); (ii
IDEA-20261009-9e4a40 | prop | proposed | h-ecdlp-bd1572 | Teichmueller lifts are useless for index calculus in F_p^* - size, not canonicity, is what | Pr[omega(a) mod p^k is B-smooth] is about rho(k log p / log B), far below Pr[a in [0, p) is B-smooth
IDEA-20261009-9f89ae | prop | proposed | lauter&stange | Period-finding on elliptic divisibility sequences mod p has no linear-recurrence shortcut | The linear-complexity profile of (W_n mod p) for n <= L grows as L/2 (random profile) for L up to 10
IDEA-20261009-a7733f | prop | proposed | h-ecdlp-bd1572 | Algebraic factor bases over F_p have about p points (dimension obstruction) | For every tested algebraic factor base (x in the image of a degree-d map P^1 -> P^1; curves in E x E
IDEA-20261009-b01e42 | prop | proposed | h-ecdlp-bd1572 | Can a prescribed ordinary E/F_p be a fibre of a high-rank elliptic surface over F_p(t)? | (a) random A, B of degrees <= 4 chi, 6 chi constrained through E at t_0 have rank 0 or 1 with probab
IDEA-20261009-b6d31b | prop | proposed | h-ecdlp-bd1572 | Solinas number fields - does small root discriminant of K_f = Q[t]/(f) give E(K_f) anythin | Over toy analogues p = f(2^k) prime with the four NIST f shapes and random low-weight f, rank E(K_f)
IDEA-20261009-bec077 | prop | proposed | h-ecdlp-bd1572 | The Serre-Tate canonical lift is a CM curve over a class field of degree about sqrt(p) | For random ordinary curves at p in 2^20 .. 2^48, h(D) fits c * sqrt(p) times a slowly varying factor
IDEA-20261009-c8433d | prop | proposed | h-ecdlp-bd1572 | Generalized-Jacobian extension class equals the Tate pairing | The connecting homomorphism agrees with Miller's algorithm up to a fixed convention on 100% of insta
IDEA-20261009-c88658 | prop | proposed | h-ecdlp-bd1572 | Function-field generator heights are O(chi), independent of p | On E1 surfaces across p in {2^8, 2^12, 2^16, 2^20}, lambda_1 of the MW lattice lies in [chi/2, 2 chi
IDEA-20261009-d94525 | prop | proposed | h-ecdlp-bd1572 | Smart's attack succeeds on random lifts and fails on the Serre-Tate canonical lift | success rate >= 1 - 2/p on random lifts; 0 on the canonical lift.
IDEA-20261009-f24f8a | prop | proposed | h-ecdlp-bd1572 | Point-decomposition cost scaling vs factor-base size for size-based factor bases (SAT / Gr | T_decomp(p, beta, m) is proportional to |F_beta|^(1 +/- 0.05) for m in {2, 3} across all solvers, i.
IDEA-20261009-fb9bae | prop | proposed | h-ecdlp-bd1572 | Required section height H(p, r) from the lattice-count heuristic | Measured N(H) on E1 lattices matches the heuristic within 2x for H >= 3 lambda_1^2; the required deg
IDEA-20261010-478721 | prop | proposed | h-ecdlp-bd1572 | Solinas number fields - does small root discriminant of K_f = Q[t]/(f) give E(K_f) anythin | Over toy analogues p = f(2^k) prime with the four NIST f shapes and random low-weight f, rank E(K_f)
IDEA-20261017-2f80c9 | prop | proposed | h-ecdlp-bd1572 | Operation sets on the SNFS digit lattice, priced: rotation quotient, implicit norm-smooth  | p=m^d-c, pi=alpha-m, digit box D_H (unique Babai lifts). (A) Sigma_rot={x->m*x} is coordinate-depend
IDEA-20261017-5c1d2a | prop | proposed | h-ecdlp-bd1572 | Ring-homomorphic digit section of the SNFS ring: the defect is a carry polynomial confined | p=m^d-c prime; pi=alpha-m generates the degree-1 prime of Z[alpha]=Z[X]/(X^d-c), N(pi)=+-p; psi2: Z[
IDEA-20261017-9b7e04 | prop | proposed | h-ecdlp-bd1572 | Names that are not logarithms: CM-volcano points of a modular E_0 reduced at p. Supply The | K=Q(sqrt(-D0)) small, p=pi*pibar split, 4p=t^2+D0 f^2. (1) The F_p-curves of trace t number H(t^2-4p
IDEA-20261017-e3a6f1 | prop | proposed | h-ecdlp-bd1572 | The Miller cocycle has a canonical primitive U: E(F_p)[N] -> F_p^* exactly when N does not | E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
H-CRYPTO-fde1f1 | hypo | analyzed | sheaf |  | For the two fixed normalized sheaf families on the declared generic base curve locus, the addition-p
H-ECDLP-281dd6 | hypo | specified | h-ecdlp-bd1572 |  | Let p = 2^c - 1 be a Mersenne prime with c prime and let l be an odd prime dividing #E(F_p) for a cu
H-ECDLP-2f1033 | hypo | specified | h-ecdlp-bd1572 |  | Let p = 2^c - 1 be a Mersenne prime with c prime, so ord_p(2) = c, p = 1 mod c, and p splits complet
H-ECDLP-4da36f | hypo | specified | h-ecdlp-bd1572 |  | Let f be a monic low-weight polynomial with coefficients in {-1, 0, 1} and p = f(2^k) prime, and let
H-ECDLP-954cae | hypo | approved | character sum&point | The cleared numerators 3 and 2 differ by 1 | The proposal writes the window endpoints 3/4 and 1/2. Clearing the common denominator 4 gives the nu
H-ECDLP-986bab | hypo | specified | h-ecdlp-bd1572 |  | Let p = 2^c - 1 be a Mersenne prime, write every x in F_p as its c-bit string (x = p is identified w
H-ECDLP-bd1572 | hypo | specified | h-ecdlp-bd1572 |  | For a prime p of special polynomial form p = P(m) with deg P = d small and P of small coefficients (
H-ECDLP-e6772e | hypo | specified | character sum&point | Doubling-sum character sum on y^2 = x^3 + x + 3 over F_47 | Let E be y^2 = x^3 + x + 3 over F_47. Let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
H-ECDSA-7ccd4b | hypo | proposed | shparlinski |  | SCOPE: the Boneh-Venkatesan / Nguyen-Shparlinski lattice embedding of ECDSA partial-nonce leakage, a
H-PFDR-8a4f44 | hypo | proposed | deligne |  | THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
H-PSEUDO-83817b | hypo | specified | character sum&elliptic |  | For any prime p, prime-order elliptic curve E/F_p with group order N, generator G, and factor base F
TOTAL 53
```

### A4. First-100-character claims of the listed hits

```
IDEA-20261017-e3a6f1 [proposed] E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
IDEA-20261016-09fd08 [proposed] y^2=x^3+ax+b/F_p, G=<P> odd order n prime to p, chord slope lam(R,S)=(y_R-y_S)/(x_R-x_S) (tangent at
IDEA-20261009-9f89ae [proposed] The linear-complexity profile of (W_n mod p) for n <= L grows as L/2 (random profile) for L up to 10
IDEA-20261009-c8433d [proposed] The connecting homomorphism agrees with Miller's algorithm up to a fixed convention on 100% of insta
IDEA-20261009-8d09c0 [proposed] (i) the zero set of W mod p in a box is exactly a lattice of index |<P_1..P_r>| (Lauter-Stange); (ii
H-ECDLP-f8cea6 [proposed] A public reduced-Tate character can be evaluated and decoded without hidden scalar input on the fini
IDEA-20260807-569c82 [proposed] (A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^
IDEA-20260930-8e3b75 [proposed] REPRESENTATION CLASS AND STAGE (RQ-ECDLP-623a32 vocabulary, filed under RQ-ECDLP-c1b7b1 because the 
H-CRYPTO-fde1f1 [analyzed] For the two fixed normalized sheaf families on the declared generic base curve locus, the addition-p
H-PSEUDO-83817b [specified] For any prime p, prime-order elliptic curve E/F_p with group order N, generator G, and factor base F
H-PFDR-8a4f44 [proposed] THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
IDEA-20260829-4b34c5 [proposed] TWO-SIDED CLAIM, both sides informative. POSITIVE SIDE. The accepted set D_chi, defined as the set o
```
