# Novelty gate N1-N4: C5 "census instrument for Couveignes-Lercier abelian periods (g = 6 over F_2, J(F_2) = Z/131)"

Gate agent run 2026-10-24/25. Read-only on the repositories; every file written by this gate is under
/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/ (this file, the raw match dumps raw1/raw1b/raw2/raw2b/raw3, and c5_curve_check.py).
Candidate field_key: p-adic and tropical geometry. Note: C5 uses no p-adic, tropical or Newton-polygon structure (it is a Honda-Tate/Weil-polynomial census plus Cantor arithmetic over F_2), so the field_key is a loose fit; nothing below depends on it.

## VERDICT (summary first)

verdict: advances_lead. Lead: LEAD-ICB-nonlinear-frob-stable-bases (open_next_step).

* As an ECDLP mechanism C5 is not new: its (representation, operation set) pair, its torsor-fibre construction and its toy rung already exist in the ledger (IDEA-20261002-711e84 / H-FROB-772c0b / EXP-FROB-7d51ae at genus 2, n = 19; IDEA-20260926-6f2601 / H-BINSTD-41d8b2 for the torsor description; H-FROB-66d9ae / IDEA-20261002-cad44c for the g <= 6 size cap). The standing closure SO-FROB (LEAD-ICB-frobenius-orbit-factor-base) is not escaped: C5 itself predicts gain 0 and accepts the orbit cap.
* As an instrument it supplies three items around one named sub-step of the open lead (the dimension-5/6 census). It does NOT change which branch of the lead's discriminator holds: the 24 g = 5 hits (EV-BINSTD-2d41c3: independent exact enumeration, 14325 classes, 24 hits, agreeing with LMFDB) had already made the closing branch ("no dim-5/6 abelian variety has 131 | #A closes the route at g <= 6") impossible, as EV-BINSTD-2d41c3 and C5's own outcomes_to_dispositions say. What it adds: (a) an LMFDB lookup replaces the infeasible g = 6 Rolle enumeration (IMP-H1, ~1.4e3 h projected, failed_infrastructure), giving 617 classes and the cross-check that H-BINSTD-6feaa2 asks for once hits exceed ~100. Its completeness at g = 6 rests on the LMFDB paper's statement that the database holds complete sets of isogeny classes (p.2 and Table 1 of arXiv:2003.05380, retrieved by me) and is NOT independently re-derived: the 164937 control figure is LMFDB's own number, so only g = 5 has an independent enumeration. (b) Jacobian status of the hits: C5 reports 173 of 617 with a known Jacobian (reproduced); the g = 5 status (11 of 24, none hyperelliptic) was found by this gate, not by C5. (c) a named explicit curve, which is LMFDB's own entry.
* What is genuinely not in the ledger (grep of proposals/hypotheses/experiments indexes for 617, has_jacobian, hyp_count, jacobian_count, the curve string, the LMFDB label: 0 hits): the g = 6 filtered count (617), the LMFDB Jacobian status of the hits, and an explicit curve. Two of these are retrievals, not constructions (the curve is LMFDB's own entry, see below).
* Duplication, stated plainly: C5's first step (toy rung comparing a torsor base with a random subspace and a size-matched null) is EXP-FROB-7d51ae (hypothesis H-FROB-772c0b, from IDEA-20261002-711e84) at other rungs. That experiment is approved and has not run, and neither it nor 711e84 is in the lead's ledger_refs. The right action is to run or extend it and add it to the lead's refs, not to file C5 as a new idea. Pricing at n = 131 is already capped by H-FROB-66d9ae (which is in the lead's refs); see G1-G3.
* Strict reading: the new content is retrieval of known tables plus hygiene, worth one line on the lead (g = 6 count; Jacobian status of the g = 5 hits), not a new lead.

## Verification of C5's retrieved/produced claims (done by this gate; provenance retrieved unless noted)

V1 (retrieved, LMFDB av_fq_isog, q = 2, SQL via the lmfdb connector this session):
  class counts g = 1..6: 5, 35, 215, 1645, 14325, 164937 (matches the LMFDB control used in EV-BINSTD-2d41c3 / H-BINSTD-6feaa2).
  classes with 131 | abvar_count: 0, 0, 0, 0, 24, 617 for g = 1..6. Matches C5.
  g = 5: 24 classes (21 with #A = 131, 3 with #A = 262), all simple. Matches EV-BINSTD-2d41c3 (24 hits).
  g = 6: 617 classes; 375 with #A = 131 exactly; 497 simple; has_jacobian = 1 for 173 (and -1 for 444); hyp_count > 0 for 8. Matches C5 exactly.
V2 (retrieved, same table; NOT stated by C5, found by this gate): at g = 5, has_jacobian = 1 for 11 of the 24 hits (10 of the 21 with #A = 131 exactly), all with hyp_count = 0, i.e. non-hyperelliptic genus-5 curves (plane quintics with a node / canonical models in P^4). EV-BINSTD-2d41c3 left the Jacobian status of the 24 hits open ("does NOT upgrade a_r >= 0 to is a Jacobian"; some hits fail a_r >= 0); the LMFDB lookup answers it for 11 of them. Consequence: the minimal genus carrying J(F_2) = Z/131 is <= 5 (not 6); the genus-6 hyperelliptic curve is a convenient choice (Cantor arithmetic), not the minimal one. Semantics of has_jacobian: the knowl says only "whether this isogeny class contains a Jacobian". Across the whole q = 2 table the column takes only -1 and 1 (no 0): g=1: 0/5; g=2: 15/20; g=3: 107/108; g=4: 1025/620; g=5: 9986/4339; g=6: 126610/38327 (counts of -1 / 1). The paper (2020 version, retrieved) says LMFDB "does not implement positive Jacobian testing in genus 4 and higher" (section 3.7, p.18) and "does not identify any isogeny class of dimension at least 4 as containing a Jacobian" (section 6.2, p.43); the live table has since acquired has_jacobian = 1 rows at g >= 4, by a route I did not identify. So for g >= 4 I read -1 as "no Jacobian known" (a lower-bound reading: 173 at g = 6 and 11 at g = 5 are lower bounds). For g <= 3 the -1 rows are probably decided negatives (e.g. 15 of 35 classes at g = 2), which is an inference I did not verify.
V3 (produced by this gate, c5_curve_check.py, pure stdlib): curve y^2 + (x^7+x+1) y = x^6+x^3+x^2 over F_2. Brute-force N_k for k = 1..12 = 4, 6, 4, 26, 44, 102, 123, 258, 490, 1066, 2116, 4154. L(T) coefficients from k <= 6 (genus 6, two rational points at infinity since h is monic of degree 7): 1, 1, 1, -1, 1, 3, 11, 6, 4, -8, 16, 32, 64. L(1) = 131. L(T) predicts N_7..N_12 exactly (match True). Middle coefficient 11 is odd, so ordinary (p-rank 6). gcd(h, f'^2 + h'^2 f) = 1, so the affine part is smooth; the points at infinity are smooth. Hasse-Weil holds. All of C5's curve claims reproduce.
V4 (retrieved): the LMFDB class 6.2.b_b_ab_b_d_l has abvar_count 131, has_jacobian 1, jacobian_count 2, hyp_count 1, p_rank 6, and its first listed curve "x^7 y + x^6 + x^3 + x^2 + x y + y^2 + y" is the same curve as C5's (y^2 + (x^7+x+1)y = x^6+x^3+x^2, after moving terms). So the "explicit genus-6 hyperelliptic Jacobian" is an LMFDB entry; C5's contribution there is selection, not construction.
V5 (retrieved, g = 2, 3 rungs): q = 2 classes with has_jacobian = 1 and abvar_count 11, 13, 19 exist at g = 2 (2.2.b_d, 2.2.c_c, 2.2.d_f) and 17 at g = 3 (3.2.a_c_c, 3.2.a_d_ab); consistent with C5's "g = 2 at n = 11, 13, 19" and "n = 17 at g = 3". The full min-g table to n <= 293 was not re-run.
V6 (citation, retrieved): Dupuy-Kedlaya-Roe-Vincent, arXiv:2003.05380 (v2, 24 Sep 2020), title, authors, abstract (WebFetch) and PDF pages 1-8, 18-19, 42-43 (Read). Retrieved statements: p.2 "searchable lists of complete sets of isogeny classes of abelian varieties" for the (g, q) range of Table 1 (dimension 6: bound q = 2, 164937 classes; dimension 5: q <= 3, 281790); p.2 and section 3.7/6.2 the Jacobian caveat for dimension >= 4 (quoted in V2). Both of C5's load-bearing sentences are therefore confirmed as retrieved. Caveat: the 2020 text says no dimension >= 4 class was identified as containing a Jacobian, which is stale against the live table (V2). Couveignes-Lercier, FFA 15 (2009): recalled; KN-OPEN-095df5 records that CL itself was never read by the program, only GGMP section 4.2's reproduction.


## N1 Atlas collision: reading of the top hits (raw outputs are pasted in the RAW section at the end)

Runs: R1-R3 = the 3 match_phrasings in order; R4 = my own phrasing (Couveignes-Lercier elliptic periods normal basis Lang torsor Weil polynomial census); R5 = extra (Jacobian of a genus-g curve over F_2 with a rational point of order n, Mumford coordinates of the Lang fibre); R6 = extra (Honda-Tate Weil polynomial census over F_2 with 131 | point count, LMFDB). Rank in parentheses. For every run I opened the lead YAML (or KRMAP row) of the top 5 hits and read mechanism, obstruction, forecloses.

| run | hit (rank) | disposition | read result |
|---|---|---|---|
| R1(1) R2(3) R3(1) R4(1) | LEAD-ICB-nonlinear-frob-stable-bases | open_next_step | SAME LANE. Mechanism lists "F_2-rational points of low-dimensional algebraic groups or Jacobians"; forecloses "Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131"; next_action includes "finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A ... and read the Couveignes-Lercier primary source"; evidence cites EV-BINSTD-2d41c3 (g = 5, 6 census, preliminary support). C5 = a sharper step for this open lead. |
| R1(2) | LEAD-ICB-ecc2k130-jacobian-carrier | open_next_step | ADJACENT, different object: asks whether the 130-dim trace-zero part A of Res(E) is a Jacobian (genus 130-300, toy n = 5, 7, ladder n = 11, 13). C5's abelian variety is over F_2 with 131 | #A, not Res_{F_{2^131}/F_2}E. Shares the "Jacobian-or-not" question and the toy-ladder style. Not the same mechanism. |
| R2(1) R5(1) | LEAD-TRF-same-field-genus-g-embedding | closed_obstructed | Different: embeds E as an isogeny factor of Jac(C) (Tate multiplicativity, #Jac = N * #A). C5's Jacobian is auxiliary and carries no copy of E. Its obstruction statement does not apply; Scope there is prime-field source curves. |
| R1(3), R2(4) | LEAD-ICP-char0-lifting-xedni-smoothness, LEAD-TRF-global-lift-small-height | closed_known | Unrelated (characteristic-0 lifts, xedni). |
| R2(5) | LEAD-STR-class-representative-ic-selection | open_next_step | Unrelated (isogeny-class representative, small-abscissa base). |
| R3(2) R5(7) | LEAD-ICB-frobenius-orbit-factor-base | closed_obstructed | SAME STRUCTURE, standing obstruction SO-FROB, NOT answered by C5 (quoted below). Its revisit_when names the open lead as the only door. |
| R3(4) | LEAD-ICB-quasi-subfield-polynomials | closed_obstructed | SO-QSP; C5's sets are not linearized QSPs, so beta >= 3/4 (Euler-Petit Theorem 1) does not apply as stated; not an escape that does work, because the base is tiny (see size cap). |
| R4(2) | LEAD-ICB-decomposition-encoding-and-sat | closed_obstructed | The C5 first_step prices per-attempt cost in D <= 5 closure work and WDSat conflicts; this lead's measured obstruction (alpha ~ m per unit l, extrapolated 50-150 bits above budget at n = 131) governs any cost reading from that instrument. |
| R4(4), R6(7) | LEAD-ICP-construction-normal-form | open_unexamined | Prime-field normal-form dedup; unrelated object. |
| R5(2,3,4,8), R3(6) | LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale), LEAD-EXO-split-jacobian-projection (closed_obstructed), LEAD-ICB-cofactor-torsion-quotients (closed_obstructed; also R3), LEAD-ICB-kic-golden-base-exact-decomp (open_next_step) | | Adjacent only. split-Jacobian: embeds E in a genus-2 Jacobian (Poincare factor); C5 does not. cofactor-torsion: 2-torsion/cofactor quotients (gcd(4, l) = 1), unrelated to a Lang torsor. dl-character-sum: bias of DL on small-x bases; no torsor structure. kic-golden: affine 2-flat / orbit-canonical lookup bases, different base family. |
| R6(1,2,6) | LEAD-TRF-ghs-binary-composite (closed_known), LEAD-TRF-odd-char-descent-smith-quartic (open_blocked), LEAD-ICE-boolean-f4-f5-f6-engines (closed_dominated) | | Unrelated or constant-factor engines (composite N GHS; odd-characteristic genus-3 descent; Boolean F4/F5). |
| all | KR-IC-b0fcda, KR-IC-73db3f, KR-IC-5a43e5, KR-IC-5ea2f8, KR-IC-791cb7, KR-IC-5931ee, KR-IC-f5c584 | known_result | See N2. |

Quoted standing obstruction the candidate must escape (SO-FROB, LEAD-ICB-frobenius-orbit-factor-base, obstruction.statement, verbatim, Scope included):
"For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."
Its revisit_when: "A Frobenius-stable base whose per-attempt decomposition probability exceeds the birthday value at matched |FB| (a second gain in the decomposition step), or a stable non-subspace base with membership degree far below its size (see LEAD-ICB-nonlinear-frob-stable-bases)."
C5 does not answer it: C5's own predicted gain is 0 (H5: orbit cap <= log2(131) = 7.03 bits, matched by rho's sqrt(2n); H6: per-attempt probability equals the birthday value). C5 therefore sits exactly at the revisit_when door and predicts the door stays shut.

SO-TABLE (LEAD-ICB-generic-table-oracle, obstruction.statement, quoted in part, Scope included): "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup charged." Its revisit_when: "An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|)". C5's first_step measures exactly that number (membership cost) and therefore is an instrument for the revisit condition, not an escape.

SO-QSP (LEAD-ICB-quasi-subfield-polynomials): "Euler-Petit Theorem 1: every linearized QSP has beta >= 3/4". C5's sets are not linearized, so the theorem is not applicable, which is a scope observation, not progress.

What C5 does that the forecloses phrases do not cover: the lead's forecloses are "Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131" (covers the construction), and "trace-spectrum / Hamming ball / multiplicative subgroup / tau-adic" (siblings). Not covered by any forecloses phrase and not in the ledger index: (i) the filtered g = 6 count and its simple/Jacobian/hyperelliptic breakdown from the LMFDB; (ii) the LMFDB Jacobian status of the 24 g = 5 hits (found by this gate, V2); (iii) a named explicit curve. These are census facts about the existence half of KN-OPEN-095df5, not about the degree half.

## Size cap that C5 does not address (derivation by this gate; ledger already holds the general version)

Heuristic G1 (conditional on the fibre being 0-dimensional with #J(F_2) = 131 points): the Lang fibre has exactly 131 points; every coordinate function f defined over F_2 takes at most 131 values on it, and the value set is one Frobenius orbit. A base built from d-variate low-degree functions of the 12 Mumford coordinates has |F| <= 131 * C(12+d, d). d = 1: 1,572 (2^10.6); d = 3: 59,605 (2^15.9).
G2 (arithmetic, successive multiplication as in H-FROB-66d9ae Arm A, no m! factor): least m with |F|^m >= 2^131 is 13 at |F| = 1,572 and 9 at |F| = 59,605 (9 is also the value H-FROB-66d9ae derives from the Weil ceiling 39,201 at g = 6). With the m! factor the least m is 17 and 10. Semaev degree 2^(m-2) is then >= 2^8 = 256 (m = 10) up to 2^15 (m = 17). These are predictions by derivation, not measurements, and they are the same order as the ledger's H-FROB-66d9ae figures (m* = 9, degree 128 at g = 6).
G3 (field theory, conditional on f(R_0) not in F_2): since 131 is prime, the F_2-minimal polynomial of a single coordinate value has degree exactly 131 = the size of its orbit, so the eliminated one-variable membership predicate has degree equal to |B_f|, not far below it. The lead's revisit_when needs "membership degree far below its size"; that can only come from keeping the description implicit (12 unknowns plus the Cantor/Frobenius equations), which is the KN-OPEN-020 implicit-membership class and exactly what IDEA-20261002-711e84 charges. G3 is my derivation and I did not find it recorded in the ledger.
G1 note: C5 names only the fibre over T (131 points). The natural Lang-torsor base would also use the fibres over kT, k = 1..130 (points R with (Frob - 1)R in <T>, all in J(F_{2^131}) because 131T = 0), i.e. about 130 * 131 = 17,030 points, 2^14.06 per coordinate function. This is inside the |F| range used in G2 (up to 59,605), so the arity conclusion (m >= 9..10 at the generous end) is unchanged; nobody should read G1's 131 as the base size.
Consequence (conditional on G1-G3): C5's own outcome mapping "Per-attempt cost in [0.5, 2] of the subspace arm -> price n = 131 on this J" would price a base whose forced arity m >= 9..17 dominates any per-attempt ratio; the n = 131 price is therefore decided by the size cap before it is decided by membership cost. This agrees with C5's own self_kill_risk "high".


## N2 Known results (KRMAP rows read; raw build_frontier_map output in the RAW section)

* KR-IC-b0fcda (known_mechanism / heuristic; top hit for the SO-FROB phrasing, score 17, matched phrase "Frobenius-stable factor base"): Galbraith-Granger-Merz-Petit: Frobenius-invariant factor bases cut the number of systems by up to 1/n and linear algebra by n^2. C5's orbit-cap premise is this result. KR hit => known_result for the "gain is n on relations" part. C5 does not claim more.
* KR-IC-73db3f (choose the factor-base vector space V; GGMP section 4.1-4.2, Shantz-Teske): the Couveignes-Lercier group-based bases are reproduced there (GGMP section 4.2, as recorded in KN-OPEN-095df5). The program has never read Couveignes-Lercier itself. The existence half (is there a commutative group over F_2 with a rational point of order 131) is a ledger/knowledge question (KN-OPEN-095df5), not a KR row. GGMP table 3 prices fractions at about 280x the vector-space Groebner time at n = 131 (not Galois-invariant; shape benchmark only), recorded in KN-OPEN-095df5.
* KR-IC-5ea2f8 / KR-IC-791cb7 (GHS, Menezes-Teske-Weng): prime degree is not weak; C5's Jacobian is not a cover of E, same observation as IDEA-20261002-711e84.
* KR-IC-a4dd54 (hyperelliptic IC, q^{2-2/g}): attacks the Jacobian discrete log itself; C5 never does that (orthogonal, same finding as 711e84).
* KR-IC-5a43e5 (Semaev summation polynomials): "novelty must lie in representation, factor base, elimination or solver, never in 'use summation polynomials'". C5 is a representation-of-the-factor-base candidate.
* KR-IC-5931ee, KR-IC-f5c584, KR-IC-fbdb61, KR-IC-49c882, KR-IC-955fd6, KR-IC-5765d2: prime-field negative result, trace linear equation / first fall degree, last fall degree, QSP, torsion symmetries, SAT. None is the census; all constrain the pricing step.
* The census object itself (Weil polynomials / isogeny classes of abelian varieties over F_2 with a prescribed divisor of #A): Honda-Tate plus the LMFDB tables (Dupuy-Kedlaya-Roe-Vincent) is standard literature infrastructure; a KR hit would be too strong, but the novelty of "tabulate it" is nil. C5 itself calls the census an instrument.
Verdict from N2: KR hit on the orbit-cap premise (KR-IC-b0fcda) => the gain claim is known. Nothing in KRMAP records the g = 6 count or a Jacobian existence statement at n = 131, so those are new to the program but are retrievals from a public database, not results.

## N3 Ledger (grep of /Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses,experiments}.jsonl; raw hit list in the RAW section)

Terms used: Couveignes, Lercier, "131 | #A / 131 divides / 131 | h", Weil polynomial, genus 6 / g = 5 / dimension 5-6, Lang torsor / torsor, abelian variety, Jacobian, LMFDB, Frobenius-stable, algebraic group, Hamming ball / trace-spectrum, plus the literal strings 617, has_jacobian, hyp_count, jacobian_count, the curve string x^7+x+1 and the LMFDB label 6.2.b_b_ab_b_d_l (the last group: 0 hits in all three indexes).

Hits that may be the same object (id [status] claim, 100 chars):
* IDEA-20261002-711e84 [proposed] "On a genus-2 curve C/F_2 whose Jacobian has a rational point of order 19, the Couveignes fibre of tr..." OPENED. Same (representation, operation set) pair as C5: Mumford (u, v) coordinates of the Couveignes fibre of translation by an order-n class on Jac(C)/F_2, Sigma = translation on Jac(C) plus translation on E by points whose abscissa is in the image. Genus 2, n = 19, eliminant onto u_0, toy degree comparison against vector-space (GGMP degree 6), random-subset, null-curve and Z/19 controls. Its own assumption: genus 2 gives a rational-point cap of 33, so "a toy invariant" with the rho exponent unchanged at n = 131. => C5's first_step is this record at other rungs (n = 11, 13 at g = 2; n = 17 at g = 3). Same object.
* H-FROB-772c0b [approved] (EXP-FROB-7d51ae approved) "On a genus-2 curve over F_2 with 19 | #Jac(F_2), the Mumford u_0 eliminant degree of the order-19 Couveignes fibre ..." Index row only. The executable form of 711e84.
* IDEA-20260926-6f2601 [proposed] / H-BINSTD-41d8b2 [supported] "THE TORUS ROW OF KN-OPEN-095df5 PRICED AS A CERTIFICATE ...": elements of F_{2^131} as values f(b) of F_2-rational functions on a torsor fibre of a commutative group over F_2 (a KN-OPEN-020 implicit-membership description). Index rows only. Same description class as C5's "low-degree functions of Mumford coordinates".
* IDEA-20260926-5c26f9 [proposed] / H-BINSTD-944a66 [analyzed] / EV-BINSTD-2d41c3 / H-BINSTD-6feaa2 [approved, EXP-BINSTD-7d37fc approved] / H-FROB-ff99bf [analyzed] / EV-FROB-a85eaf: the dimension-5/6 census. H-BINSTD-6feaa2 OPENED: it plans the same g = 5, 6 census with LMFDB unfiltered counts (1645, 14325, 164937) as a completeness control and a Rolle-pruned enumerator; its prediction for filtered_hits is "No direction pre-committed ... >~100 hits at g=6 triggers re-check before belief" (the retrieved 617 is in that regime and is a LMFDB filter, not an enumeration, so it also supplies the cross-check the hypothesis wants). EV-BINSTD-2d41c3 and EV-FROB-a85eaf (both cited in the lead YAML evidence list, read under N1) confirm: g = 5 24 hits; g = 6 failed_infrastructure; no filtered g = 6 count anywhere. C5's census claim "no g = 6 filtered count was found" is correct for EV-BINSTD-2d41c3, H-BINSTD-6feaa2 (opened) and census.json (g <= 4 only; checked).
* IDEA-20261002-cad44c [proposed] / H-FROB-66d9ae [approved, EXP-FROB-8451c7 approved, zero runs] "Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimension g <= 6 has cardinality at most the Weil ceiling, 6725 at g=5 and 39201 at g=6": OPENED (H-FROB-66d9ae). For all factor bases with |F| <= 39201 the m = 3 sumset image is below 2^-80 of 2^131 and the least covering arity is 9 (g = 6), Semaev degree 128. Listed in the lead's ledger_refs. C5's J(F_2) = Z/131 is inside this forall (fibre of size 131). Open window stated there: "Extension families of positive-dimensional parameters are OUTSIDE the forall".
* IDEA-20261002-8f26ce [proposed] / H-FROB-f3d248 [approved, EXP-FROB-f495ea approved] Artin-Schreier genus 5/6 over F_2 (y^2 + y = f(x), f of odd degree 11 or 13) as explicit models of the order-131 question. C5's curve is not Artin-Schreier (h = x^7+x+1 is not constant), so it is not covered by that search; the LMFDB entry is outside it. Related explicit-model column, different family.
* IDEA-20261006-83c197 [proposed] / H-FROB-be16c9 [specified, EXP-FROB-05cbda review_required]: dimension-2 Weil class count and one S_3 degree at the smallest prime excluded by both dimension-1 conditions. Same (R3 auxiliary group over F_2, Frobenius/translation) pair at the first excluded prime.
* IDEA-20261018-329d0a [proposed] multiplicative-subgroup (x^d = 1) stable lane: sibling inside the same lead.
* IDEA-20261024-a29e53 [proposed, dated today] Weil restriction / "is the cover floor the genus floor": adjacent (Res_{K/F_q}E, not an auxiliary Jacobian).
Records opened in full (exact paths): ledger/proposals/IDEA-20261002-711e84.yaml, ledger/hypotheses/H-FROB-66d9ae.yaml, ledger/hypotheses/H-BINSTD-6feaa2.yaml (three). Additionally read, not proposals/hypotheses: ledger/evidence/EV-BINSTD-2d41c3.yaml and ledger/evidence/EV-FROB-a85eaf.yaml (cited in the lead's evidence list, read under N1 to check C5's statement about the g = 6 status), knowledge/open-problems/KN-OPEN-095df5.md and KN-OPEN-020.md, knowledge/findings/KN-FIND-ffe1df.md, docs/object-frame-ideation.md.
Verdict from N3: the mechanism and the toy rung duplicate 711e84 / H-FROB-772c0b; the census duplicates H-BINSTD-6feaa2 / EXP-BINSTD-7d37fc in intent; the g <= 6 size cap is H-FROB-66d9ae. The delta is the retrieval route (LMFDB lookup instead of the infeasible Rolle enumeration at g = 6) and the Jacobian status.

## N4 Notation check

Pair stated by C5: (R3 Lang-torsor Mumford coordinates on a genus-6 Jacobian over F_2 with J(F_2) = Z/131; Sigma = Frobenius acting as translation by T on the torsor). Trichotomy class claimed: partial-action.
Against the recorded results:
* IDEA-20260806-c5d183 (full-translation propagation is constant or injective on a prime-order group) and KN-FIND-ffe1df Theorem C (exact sum-compatibility forces a homomorphism): not triggered, because Sigma is the Galois group Z/131, not the full translation action on E(F_{2^131}). Partial-action (Class I) is correct. No new rigidity argument is needed or given.
* IDEA-20260901-863e36 (propagation = block systems of <Sigma>): the set {f(R)} is by construction a union of <Frobenius>-orbits of F_{2^131}, i.e. a union of blocks. Equivariance f(Frob R) = Frob f(R) holds because f is defined over F_2, and Frob R = R + T. Hence the base is an ORBIT-UNION base. Orbit-union and normal-basis bases are already measured: LEAD-ICB-frobenius-orbit-factor-base (per-attempt probability equals the birthday value, n = 11..23), KN-FIND-47da4e (orbit-union parameterisation cost-neutral), tau-factor-base pilot (exactly log2(n) bits). In new notation, C5's base is a recorded object (orbit-union, SO-FROB) given a different description (implicit membership through a torsor). The only quantity C5 adds is the price of that description (membership degree), which is the number named in the lead's revisit_when and the one IDEA-20261002-711e84 already prices at genus 2.
* KN-OPEN-020 (bounded-degree algebraic factor bases scoped out; open class = high-degree, implicit, target-dependent): C5's fibre is 0-dimensional with 131 points, so by G3 the eliminated univariate description has degree 131 = |orbit|, the equality case of the Bezout-type bound |F| <= Delta; it is inside the scoped-out class unless the description stays implicit. C5 must (and the ledger's 711e84 does) declare the implicit-membership class and charge description, membership, relation, descent, time and memory.
* Object-frame constraint block (docs/object-frame-ideation.md section 3): C5 names the pair and the class; it does not give the lossy-projection test against Sigma (what is discarded, branching bound) that 711e84 gives for u_0 (L, b); that gap would have to be filled before it could be filed as a separate idea. The R3 class is "torsor coordinates" of RQ-ECDLP-623a32; the attack stage claimed is factor-base membership.
Result: the pair is not a new rigidity statement and is not escaped from a recorded one in new notation; it is the recorded orbit-union base (SO-FROB) plus the recorded torsor description (6f2601 / 711e84). No new object.

## Hard-rule compliance and caveats

* Nothing was created, edited, git-added or committed inside the repositories. Files written by this gate: this file, raw1.txt, raw1b.txt, raw2.txt, raw2b.txt, raw3.txt, c5_curve_check.py, and the part_*.md assembly files, all under the scout/ directory.
* Predictions are labelled: G1-G3 and the arity numbers are derivations/predictions by this gate. V1-V5 are retrieved/produced by this gate. V6's two load-bearing sentences are retrieved (PDF pages read); the g = 6 completeness remains the paper's claim, not independently re-derived by this gate.
* No outcome is reported for the candidate's toy rung: it was not run by this gate.
* Heuristics are numbered G1-G3; H5/H6 are C5's own.
* This verdict does not rate C5 as promising or not. C5 predicts no exponent move (gain 0); by docs/target-result-profile.md A1 (a target-class result changes an exponent or an equally central structural barrier) it is an instrument/census step, not a target-class result.


## RAW OUTPUTS (verbatim)

### RAW N1: python3 tools/lead_atlas.py --match (R1-R4; env LEAD_ATLAS_* as specified)
```
=== LEAD_ATLAS --match: abelian variety over F_2 with a rational point of order 131: genus-6 hyperelliptic Jacobian with exactly 131 points for Couveignes-Lercier periods ===
   15  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   13  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    8  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    8  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    8  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    8  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    6  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs

=== LEAD_ATLAS --match: a small curve over F_2 whose Jacobian has 131 points gives a Frobenius-stable model of the 131-bit field ===
   16  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   14  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   13  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   12  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
   10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    9  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
    9  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    8  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks

=== LEAD_ATLAS --match: Frobenius-stable factor base gain is exactly n on relations and never more; stable subspaces empty at prime n ===
   23  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   18  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   17  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   17  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
   11  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)

=== LEAD_ATLAS --match: Couveignes-Lercier elliptic periods normal basis Lang torsor Weil polynomial census ===
   16  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   14  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   12  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    9  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    9  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    8  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    8  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    7  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?

```
### RAW N1 extra: lead_atlas --match (R5, R6)
```
=== LEAD_ATLAS --match: Jacobian of a genus-g curve over F_2 with a rational point of order n yields a Galois-invariant factor base via Mumford coordinates of the Lang fibre ===
   14  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   11  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   11  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)

=== LEAD_ATLAS --match: Honda-Tate Weil polynomial census of isogeny classes over F_2 with 131 dividing the point count, LMFDB ===
   12  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
   11  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   10  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    9  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    9  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    9  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    9  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*

```
### RAW N2: python3 tools/build_frontier_map.py --match (R1-R4)
```
=== build_frontier_map --match: abelian variety over F_2 with a rational point of order 131: genus-6 hyperelliptic Jacobian with exactly 131 points for Couveignes-Lercier periods ===
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5ea2f8  score=8  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-a4dd54  score=5  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde

=== build_frontier_map --match: a small curve over F_2 whose Jacobian has 131 points gives a Frobenius-stable model of the 131-bit field ===
KR-IC-791cb7  score=14  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5ea2f8  score=8  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-53c89f  score=8  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-755e35  score=7  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c

=== build_frontier_map --match: Frobenius-stable factor base gain is exactly n on relations and never more; stable subspaces empty at prime n ===
KR-IC-b0fcda  score=17  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    matched phrase(s): Frobenius-stable factor base
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5a43e5  score=10  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-49c882  score=9  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-cd0049  score=6  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-0528e7  score=4  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-IC-9e610d  score=3  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006

=== build_frontier_map --match: Couveignes-Lercier elliptic periods normal basis Lang torsor Weil polynomial census ===
KR-IC-73db3f  score=12  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-f5c584  score=8  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5ea2f8  score=6  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-1fcdbc  score=3  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2

```
### RAW N2 extra: build_frontier_map --match (R5, R6)
```
=== build_frontier_map --match: Jacobian of a genus-g curve over F_2 with a rational point of order n yields a Galois-invariant factor base via Mumford coordinates of the Lang fibre ===
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-955fd6  score=11  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5ea2f8  score=8  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=8  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-755e35  score=8  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea

=== build_frontier_map --match: Honda-Tate Weil polynomial census of isogeny classes over F_2 with 131 dividing the point count, LMFDB ===
KR-IC-73db3f  score=10  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-791cb7  score=10  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5ea2f8  score=9  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-5765d2  score=8  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-f5c584  score=8  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006

```
### RAW N3: ledger index grep (proposals.jsonl, hypotheses.jsonl; python regex over claim/statement/title/mechanism; first 40 hits per term)
```
=== LEAD_ATLAS --match (own phrasing): Kohel Shparlinski exponential sums over a subgroup of E(F_p) twisted by group characters Lang isogeny Bombieri ===
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    9  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    9  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    9  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
    8  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    6  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
=== BUILD_FRONTIER_MAP --match (own phrasing): Kohel Shparlinski exponential sums over a subgroup of E(F_p) twisted by group characters Lang isogeny Bombieri ===
KR-IC-791cb7  score=10  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-755e35  score=7  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-5ea2f8  score=3  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-955fd6  score=1  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-ae532f  score=1  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-e2d81b  score=1  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
=== LEAD_ATLAS --match (own phrasing): Fourier spectrum of a canonical non-homomorphic quasi-homomorphism onto F_p^* is white ===
    7  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    5  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    4  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    3  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    3  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    2  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    2  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
=== BUILD_FRONTIER_MAP --match (own phrasing): Fourier spectrum of a canonical non-homomorphic quasi-homomorphism onto F_p^* is white ===
KR-IC-cd159a  score=3  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-5b1c0a  score=1  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
```
### RAW N3 extra: the index-row dump of the 16 candidate-duplicate records (ids, claim, mechanism, refs) was printed to the session and is summarised in the N3 section. Literal-string greps for 617 / has_jacobian / hyp_count / jacobian_count / x^7+x+1 / 6.2.b_b_ab_b_d_l returned 0 hits in proposals, hypotheses and experiments indexes.
### RAW V1-V6: LMFDB queries, curve check, paper pages
```
SELECT g, COUNT(*), SUM(abvar_count%131=0), SUM(abvar_count=131), SUM(131|A and is_simple), SUM(131|A and has_jacobian=1), SUM(131|A and hyp_count>0) FROM av_fq_isog WHERE q=2 AND g<=6 GROUP BY g  ->
g=1: 5, 0, 0, 0, 0, 0 | g=2: 35, 0,0,0,0,0 | g=3: 215, 0,0,0,0,0 | g=4: 1645, 0,0,0,0,0 | g=5: 14325, 24, 21, 24, 11, 0 | g=6: 164937, 617, 375, 497, 173, 8
has_jacobian split among 131|A: g=5: -1 -> 13, 1 -> 11 ; g=6: -1 -> 444, 1 -> 173
SELECT g, has_jacobian, COUNT(*) FROM av_fq_isog WHERE q=2 GROUP BY g, has_jacobian -> (g, value, n): (1,1,5) (2,-1,15) (2,1,20) (3,-1,107) (3,1,108) (4,-1,1025) (4,1,620) (5,-1,9986) (5,1,4339) (6,-1,126610) (6,1,38327)
knowl columns.av_fq_isog.has_jacobian: 'Whether this isogeny class contains a Jacobian' (no definition of -1)
6.2.b_b_ab_b_d_l: abvar_count 131, has_jacobian 1, jacobian_count 2, hyp_count 1, is_simple true, p_rank 6, curves[0] = x^{7} y + x^{6} + x^{3} + x^{2} + x y + y^{2} + y
g=5 hits with has_jacobian=1: 5.2.b_d_e_h_n, 5.2.b_d_e_i_k, 5.2.b_d_e_j_h, 5.2.b_e_c_k_f, 5.2.c_c_d_h_k, 5.2.c_c_f_g_d, 5.2.c_d_c_g_j, 5.2.c_d_d_f_h, 5.2.c_d_e_e_f, 5.2.c_e_e_c_c (all abvar_count 131), 5.2.d_g_l_q_v (262)
arXiv:2003.05380v2 p.2: 'searchable lists of complete sets of isogeny classes of abelian varieties'; Table 1 (dimension, bound on q, class count): (1,499,6184) (2,211,1253897) (3,25,1055307) (4,5,183607) (5,3,281790) (6,2,164937)
arXiv:2003.05380v2 section 3.7 (p.18): 'currently the LMFDB does not implement positive Jacobian testing in genus 4 and higher.'  section 6.2 (p.43): 'Currently the LMFDB does not identify any isogeny class of abelian varieties of dimension at least 4 as containing a Jacobian.'

--- python3 -I c5_curve_check.py ---
N_k, k=1..12 : [4, 6, 4, 26, 44, 102, 123, 258, 490, 1066, 2116, 4154]
L coeffs c_0..c_12: [1, 1, 1, -1, 1, 3, 11, 6, 4, -8, 16, 32, 64]
L(1) = #J(F_2) = 131
predicted N_k 1..12: [4, 6, 4, 26, 44, 102, 123, 258, 490, 1066, 2116, 4154]
match k=7..12 : True match k=1..6: True
a_g (middle coeff) = 11 ordinary iff odd: True
Hasse-Weil ok: True
gcd(h, f'^2+h'^2 f) = 0b1 (1 => smooth affine part)
```
