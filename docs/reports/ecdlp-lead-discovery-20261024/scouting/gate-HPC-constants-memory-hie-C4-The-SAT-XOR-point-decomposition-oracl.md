# Gate N1-N4: C4 "The SAT/XOR point-decomposition oracle decided by the break-even conflict price from sealed counters"

Field: HPC constants (round 2). Bottleneck B4 (LEAD-ICE-sat-xor-pdp-oracle). Gate run 2026-10-25, read-only on all repositories; only files under scratchpad/scout/ were written (this file and raw-C4/).
Provenance labels: retrieved = checked against a source this session; recalled = from memory, not checked; derived = arithmetic I did this session on recorded counters (no new run, no measurement).

## VERDICT (summary)

duplicate_of_lead, lead = LEAD-ICE-sat-xor-pdp-oracle (open_next_step). Not a new mechanism, not an escape from any standing obstruction, and the closure it proposes is not licensed by AGENTS.md 5a.
Why duplicate and not advances_lead (the "sharper next step" bar): (a) the candidate's core (reprice the native-XOR arm over a weight band, plus the crossing price) is a strict subset of the lead's recorded next_action: it drops the propagation clause and the alpha(m) fit; (b) its decision rule (floor argument H1/H2 to exclude w = 0) is unlicensed under 5a (F2), so it is not a sharper discriminator; (c) the same arithmetic was done this round by sibling C3 (F7), and C3's advances_lead rested on content C4 lacks (the measured m = 2 constant, 7.19 x 2^((m-1)l) conflicts per call, and the 2^-5.15 gap to 2^(ml)/m!); matching C3's verdict is not a reason in itself; (d) the only element that is not already in the lead is the optional callgrind Ir-per-conflict run, which is the lead's own calibration clause ("Calibrate ns per conflict ... against ns per group addition") done with an existing tool and without a PMU, and per 5a a calibration is only a further point and never closes the band, so it does not change any disposition.
Strict findings:
 F1. Same object as the open lead's own next_action. The lead's step is: "Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per solver op, and fit alpha(m)". The candidate's mechanism is the repricing clause (adds a 0.01 point and the closed-form crossing price, which is linear algebra on the same counters) plus a physical-floor argument that replaces the calibration clause. It omits the propagation clause (propagations are not recorded in the sealed vector: no such counter in phase_native_totals) and the alpha(m) fit at m in {3,4,5}.
 F2. The candidate's closure is NOT licensed by AGENTS.md 5a (crypto repo, "Rank only where the conclusion holds at every weight in the band. If the order of two arms changes inside the band, report them as unresolved at that boundary, never as a win for either side"; "Pinned calibrations may be added as a further point, but they never replace the band"). w = 0 is a mandatory band point for conflicts, and SAT/rho = 0.854 there, > 1 from w ~ 0.0022 up, so the order changes inside the band [0, 0.1]. The candidate's H1 (conflict >= 10 ns) is a physical argument to exclude w = 0; 5a makes the band a program convention that such an argument, or any calibration (callgrind Ir, an L2 wall), cannot remove. Consequence: no calibration can close this lead through the band at this cell. The only closure routes are the alpha(m) scaling (H-SATIC-5c526c, or the measured alpha ~ m of the closed sibling LEAD-ICB-decomposition-encoding-and-sat) or an owner rule decision on w = 0 for solver conflicts. The candidate's reopen condition ("only a measured conflict price < 0.0022 GAE could reopen it") is therefore moot: the lead is already unresolved at that boundary at w = 0. Rule 6 additionally says wall clock is never the headline and an extrapolation is not a measurement: the 15.1 us per conflict is an L0 macOS wall (README: "L0 wall median is descriptive only"; none met the L2 wall gate).
 F3. Candidate arithmetic reproduces, with one 5a deviation. I recomputed every quoted number from count-qualified-main.resources.json (table below). The candidate's 7.58 (w = 0.1) and 68.2 (w = 1) leave rho's 344.7 unpriced native ops per run (canonicalisations 7,308 + partition hashes 5,671 + table inserts 384 + table queries 425, over 40 runs) at zero; 5a says apply the weight "the same way to every arm, references included". Applied to both sides: 7.34 and 50.99; crossing price 0.0021833 (not 0.00217); PREDICTION P (floor 10 ns, using the rho-arm L0 conversion 115.6 ns/GAE, so w = 0.0865): S/rho 6.48 with rho natives at w, 6.67 with rho natives at 0. The candidate's prediction "S/rho >= 6.6" therefore holds only with rho natives at zero.
 F4. The 0.25 ns figure uses the rho-strong arm's L0 conversion (solve_wall / total GAE = 115.6 ns per GAE). Other arms at L0: ic-mitm 175, ic-mitm-frob 341, rho-aa 443 ns per GAE, so the conversion is not calibrated (spread 3.8x) and the SAT arm's own ratio (1.19e6 ns per GAE) is dominated by solver wall. "That arm's L0 wall" is ambiguous. The H2 margin (about 10^4) survives any of these conversions, but it is a statement about an unadmitted conversion.
 F5. Single-size, toy datum. n = 17 Koblitz (log2 r = 16.00), where strong rho's charged set-up is 75% of its GAE (30,722 of 40,950; README: "the panel cannot support a scaling inference"). The crossing price is a toy-size number; the lead's real discriminator (does conflict count track 2^(ml)/m!, i.e. alpha ~ m) is carried by the closed sibling LEAD-ICB-decomposition-encoding-and-sat and by the pending H-SATIC-5c526c, not by this arithmetic. The candidate's outcome rule is a conjunction (priced S/rho > 1 AND alpha ~ m (cited)), and only the second conjunct closes anything.
 F6. The escape of SO-TABLE is nominal. The candidate's own premise says the oracle reads descended coordinates (true), but the recorded derived identity (IDEA-20260904-3c7a91, quoted in the lead mechanism: "the pdp CNF-XOR model is a complete enumerator of V^m mod S_m with no above-leaf pruning") puts it back in the enumeration class. The candidate does not need the escape for its decision, and it does not answer LEAD-ICB-decomposition-encoding-and-sat's obstruction (it relies on it: "Caught by").
 F7. Overlap the candidate under-states. It says the sibling scout-sat-xor-planted.md kill 6 "predicts the same direction without the computed price". In this round that kill was promoted to a candidate and scout-sat-xor-planted.md section R5 (repro/c3_band.py) computes the same band (0.854 / 7.34 / 50.99), the crossing prices 0.002183 (vs rho) and 0.0508 (vs Frobenius MITM) and the 15.1 us per conflict (descriptive only). Gate file gate-SAT-XOR-solving-and-phas-C3-Conflict-priced-closure-of-the-native.md (same round, sibling) reached advances_lead on the same lead. C4 is a duplicate of that sibling candidate (not of an atlas or ledger record) and should be merged with it, not filed separately.
 What is new and checkable: nothing beyond arithmetic on one sealed vector. The lead's best_measured line ("conflicts unpriced") does not yet record the band values; recording them is bookkeeping on the lead, not a new lead.

## Derived arithmetic (c4_verify.py, run -I; output pasted in section RAW)

| quantity | candidate | recomputed (derived) |
|---|---|---|
| SAT GAE per run | 874.08 | 874.0836 (34,963.343 / 40; lower_bound true; unpriced_units = solver_conflicts_uncharged) |
| rho-strong GAE per run | 1,023.76 | 1,023.7589 (40,950.357 / 40; lower_bound true; 4 unpriced native counters) |
| Frobenius MITM GAE per run | 4,372.35 | 4,372.3534 (unpriced_units empty) |
| conflicts per run | 68,899.15 | 68,899.15 (2,755,966 = relations.solver_ops, 749 solver_calls; 3,679.5 per call) |
| crossing price vs rho | 0.00217 | 0.002172 (rho natives at 0), 0.002183 (5a) |
| crossing price vs Frobenius MITM | 0.0508 | 0.05077 |
| SAT/rho at w = 0 / 0.01 / 0.1 / 1 | 0.854 / 1.53 / 7.58 / 68.2 | 0.854 / 1.527 / 7.584 / 68.154 (rho natives at 0); 0.854 / 1.522 / 7.337 / 50.987 (5a) |
| SAT/Frobenius MITM at 0 / 0.01 / 0.1 / 1 | not stated | 0.200 / 0.357 / 1.776 / 15.96 |
| L0 ns per conflict | 15.1 us | 15,099 ns (target_PDP wall / solver_ops), 15,108 ns (solve wall / solver_ops); descriptive L0 only |
| ns per GAE (rho arm, L0) | 115.6 implied | 115.65; other arms 175 / 341 / 443 |
| 15.1 us in GAE at 115.6 ns/GAE | not stated | 130.6 GAE per conflict (above the band's top point 1 by 130x) |
| H2: rho natives doubling S, c* <= 0.017 GAE (about 2 ns) | c* <= 0.017 | reproduces: rho 1,023.76 + 344.7 natives at w = 1 is 1,368 < 2 x 1,023.76, so the doubling bound c* = (2 x 1,023.76 - 874.08) / 68,899.15 = 0.01703 GAE (1.97 ns at 115.6 ns/GAE) is a ceiling; the 5a-priced crossing is 0.002183 |

## N1 - Atlas collision (4 runs: the 3 match_phrasings + my own "CDCL conflict price lower bound clause-database traversal watched literals SAT solver cost per conflict versus rho GAE")

Raw outputs pasted verbatim in RAW below. Top hits per run, all opened (lead YAML: mechanism + obstruction + forecloses):

Run 1 (break-even price phrasing): LEAD-ICE-sat-xor-pdp-oracle (15), LEAD-ICE-generic-oracle-arity-cost-floor (8), LEAD-ICP-icperf-binary-pdp-solver (8), LEAD-ICE-gpu-rootfind-oracle (7), KR-IC-5765d2 (6).
Run 2 (conflicts cost too much): LEAD-ICE-generic-oracle-arity-cost-floor (19), LEAD-ICE-rootfind-pairtable-oracle (15), LEAD-ICB-decomposition-encoding-and-sat (13), LEAD-ICE-sat-xor-pdp-oracle (13), KR-IC-1fcdbc (12).
Run 3 (alpha ~ m phrasing): LEAD-ICB-decomposition-encoding-and-sat (31), KR-IC-5765d2 (25), LEAD-ICE-sat-xor-pdp-oracle (22), LEAD-ICP-icperf-binary-pdp-solver (21), LEAD-ICE-rootfind-pairtable-oracle (18).
Run 4 (own phrasing): LEAD-ICP-icperf-binary-pdp-solver (18), LEAD-ICB-decomposition-encoding-and-sat (16), LEAD-ICE-sat-xor-pdp-oracle (15), KR-RHO-1c2928 (12), LEAD-ICE-charged-toy-ic-exponent-vs-rho (12).

1. LEAD-ICE-sat-xor-pdp-oracle (open_next_step). SAME MECHANISM. Mechanism: encode descended S_3/S_4 as CNF-XOR, CDCL with Gaussian elimination; "SAT conflicts and propagations are unpriced, and a derived identity says the pdp CNF-XOR model is a complete enumerator of V^m mod S_m with no above-leaf pruning". next_action.step (quoted above in F1). discriminates: "Priced S/rho below 1 across the band would be a sub-rho toy row to send through the validation gate; above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant and closes the lead as dominated by the pair table." best_measured: "native-XOR SAT S/rho 0.854 lower bound, conflicts unpriced, n = 17 Koblitz, 40/40 verified". forecloses: SAT solver for point decomposition; CryptoMiniSat Gaussian elimination on Weil descent; WDSat XOR reasoning for summation polynomials; CNF-XOR encoding of the PDP; DPLL conflict law 2^(ml)/m!. No obstruction field (open). The candidate's name, bottleneck and rule quote are this row.
2. LEAD-ICB-decomposition-encoding-and-sat (closed_obstructed). obstruction.statement (kind measured, no Scope clause): "Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. ... Encoding levers are constants: ..." forecloses includes "SAT or XOR solver for point decomposition beats rho" (verbatim the candidate's third phrasing). The candidate's conclusion (SAT oracle does not beat rho) is this foreclosed statement reached through a price axis; it does not answer or try to answer the obstruction (it cites it).
3. LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed). obstruction.statement (cost_model): "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc) ... Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC." The candidate's reading that the SAT oracle is outside this Scope is correct; the product law (relations x targets x oracle = m 2^n) still applies to any oracle whose per-attempt work is the enumeration.
4. LEAD-ICB-generic-table-oracle (SO-TABLE; closed_obstructed, from the candidate's own citation and the standing list). obstruction.statement (theorem), read in the YAML: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; ... Scope: all binary and Koblitz curves, one target, setup charged." revisit_when: "An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition". Candidate quote is accurate (elisions marked). Its claimed escape is nominal (F6).
4b. SO-GEN rows (the candidate lists SO-GEN in so_codes_touched; opened this session).
   LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed; theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." revisit_when: "Never for generic algorithms; only a method that reads the representation (index calculus, transfer) can change the exponent."
   LEAD-EXO-augmented-oracle-ggm (closed_obstructed; theorem): "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 ... Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
   SO-GEN is RESPECTED, not escaped: the candidate does not claim a sub-sqrt(r) generic algorithm and does not rely on an extra public oracle; its rho arm is the generic reference and its SAT arm reads the representation (the one route the first row leaves open), where the decision is made on cost, not on an exponent. Nothing in SO-GEN is answered or needed.
5. LEAD-ICP-icperf-binary-pdp-solver (open_next_step). Solver choice SAT vs Groebner (H-ICPERF-c9380d, BRiAl column); different action and different axis (solver family, not conflict price). forecloses: "WDSat conflict law for descended Semaev systems". Not the candidate's step.
6. LEAD-ICE-rootfind-pairtable-oracle (open_blocked). Same pricing template on the rival oracle: "Price every native primitive ... at 0, 0.1 and 1 GAE/op"; best_measured about 1.54x strong rho (17-bit Koblitz, L0, natives unpriced). The program already applies the 0/0.1/1 band to each oracle lead; the candidate is the SAT instance of that template.
7. LEAD-ICE-gpu-rootfind-oracle (open_blocked): CUDA root-finding; unrelated mechanism (hardware throughput of a different oracle).
8. LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked; B1): charged toy exponent vs matched rho, needs the unbuilt non-enumerative oracle; context only.
9. LEAD-RHO-native-step-cost (open_next_step): prices rho's canonicalisation (the rho-side natives that the candidate leaves at zero); best_measured 718 instructions per step. Relevant to F3.
10. LEAD-ICB-kic-golden-base-exact-decomp (open_next_step; N7 pilot "flat SAT / direct MITM median wall 1.70x [1.02, 2.69] (SAT slower)"): independent descriptive corroboration of direction; different mechanism (co-designed bases). LEAD-ICB-frobenius-search-symmetry and LEAD-ICP-icperf-writability-boundary (B4 wall, +40.8 bits) are untouched by the candidate.

What the candidate does that the hits' forecloses phrases do not cover: the crossing price per conflict as a number (0.00217 to 0.00218 GAE) and the band values for this one sealed cell; the lead does not record them. The floor argument (a conflict cannot cost about 0.25 ns) is also not in the lead, but it is a remark, not a cost model, and 5a does not let it replace the band.
Semantic sweep of ATLAS.md for conflict/break-even/per-solver-op terms (raw-C4/semantic_sweep.txt, pasted below) finds no further lead pricing conflicts.

## N2 - Known results

build_frontier_map.py --match, 4 phrasings, raw below. KR-IC-5765d2 tops runs 1 and 3 (score 6 and 25) and is in the top 3 of run 4; KR-IC-1fcdbc tops run 2.
- KR-IC-5765d2 (known_mechanism, measured): "SAT solvers (CryptoMiniSat) and the XOR-aware WDSat solve binary-curve PDP instances faster than Magma F4 (up to 300x on the PDP step, Trimoska-Ionica-Dequen 2020), without changing the exponent relative to rho." The candidate's object (SAT/XOR PDP oracle) is this KR. The KR is about SAT vs F4 and exponent, not a priced SAT-vs-rho break-even; the priced comparison is the lead's, not a literature result.
- KR-IC-1fcdbc (known_negative, measured): characteristic-2 summation algorithms stay far slower than rho (Galbraith-Gebregiyorgis, Shantz-Teske); experiments only at small n and l. The direction the candidate predicts.
- KR-RHO-1c2928 (rho constant; set-up 71% of the strong reference at toy sizes): relevant to F5.
- No KR contains a CDCL cost-per-conflict statement. External ingredient: Moskewicz, Madigan, Zhao, Zhang, Malik, "Chaff: Engineering an Efficient SAT Solver", DAC 2001, pp. 530-535. Provenance: bibliographic record RETRIEVED (WebSearch this session; https://collaborate.princeton.edu/en/publications/chaff-engineering-an-efficient-sat-solver/ and PDF copy https://cs357.stanford.edu/MMZZM01.pdf: authors, venue, year and pages confirmed; abstract is about efficient Boolean constraint propagation and a decision strategy). The load-bearing remark ("a conflict costs at least one clause-database traversal, so more than about one cycle") is NOT shown in the abstract and I did not verify it in the full text; keep it recalled, and note that it is the candidate's modelling remark, not a Chaff result. The decision does not need Chaff: the arithmetic uses only the sealed counters.
Verdict for N2: no KR states the result; KR-IC-5765d2 and KR-IC-1fcdbc cover the object and the direction. Not known_result as a number, because the break-even is arithmetic on a program-internal counter set.

## N3 - Ledger

grep of ledger/.index/{proposals,hypotheses}.jsonl by: conflict; break-even; SATIC|ecbench_sat_pdp|sat_pdp; per solver op / GAE per conflict / solver_ops; native-XOR|CryptoMiniSat|WDSat; priced/pricing near conflict/solver (raw below). Hits that may be the same object (id + claim head):
- H-SATIC-5c526c [proposed] "alpha(m) of DPLL point decomposition at m in {3,4,5}: the per-attempt UNSAT conflict law 2^(ml)/m! persists on chained S_3 and direct S_(m+1), and no cell reaches alpha < m/2 - 1" (opened in full). Its object frame is the candidate's pair verbatim: "Representation R1 ... Sigma = S_m permutations ... (plus translation by factor-base points: Class I, partial-action, IDEA-20260806-c5d183) ... No new object; an existing one is priced." It measures conflict COUNT scaling (alpha), not conflict PRICE; records "WDSat conf counts branch points, not CDCL conflicts" (a solver-unit caveat the candidate does not carry: the sealed vector is CryptoMiniSat native-XOR conflicts). Linked to the lead's next_action ("fit alpha(m) ... (H-SATIC-5c526c)").
- IDEA-20261017-4b1672 [proposed] same claim as H-SATIC-5c526c (source idea; not opened in full, the hypothesis quotes its mechanism verbatim).
- IDEA-20260915-0d8e90 / H-ICPERF-81de5c "WDSat UNSAT conflict count equals c * 2^{ml}, c in [0.9, 1.0] (an exhaustive core)": the conflict-count law, not a price.
- IDEA-20260904-3c7a91 "The pdp CNF-XOR model admits no above-leaf pruning: the SAT solver is a complete enumerator of V^m modulo S_m"; IDEA-20260904-e12b5a (Gaussian elimination inert on the pdp CNF-XOR model); IDEA-20260926-b11cb1 (ideal-XG ceiling: XOR-Gaussian elimination in DPLL cannot beat the (m-1)-fold enumeration oracle). These are the "SAT = enumeration" side; the candidate's priced version has no record of its own.
- IDEA-20261007-ece173 "Fully charged yield metrology ... timeouts at a fixed conflict cap": a charging protocol (metrology), different object; IDEA-20261018-f2cd4d (tau-Horner m! vs symmetry-breaking m! at matched core size): conflict counts again.
No index row contains a conflict price, a break-even price, or "GAE per solver op" applied to the sealed ecbench session (term 4 returned 0 hits in both indexes; "break-even" hits in proposals are unrelated cost-model proposals (e.g. IDEA-20261017-bbc53e, IDEA-20261018-a0830c, coincidence harvest)). Full records opened: H-SATIC-5c526c only (2 more allowed, not needed; the other hits are summarised from their index claims).
Verdict for N3: the object is recorded (lead + H-SATIC-5c526c + the enumeration-identity ideas); the priced band is not recorded in the ledger index, but it is the lead's own step and has been computed in the same round by the sibling C3 (F7).

## N4 - Notation change

The candidate is an IC/representation candidate, so N4 applies. Pair: (R1 = F_2 coordinates of the Weil-descended chained S_3 over a subspace factor base, written as CNF-XOR; Sigma = translation by factor-base elements together with S_m on the summand slots). This is the same pair as the object frame of H-SATIC-5c526c / IDEA-20261017-4b1672 (Class I, partial-action). Against the recorded rigidity results:
- IDEA-20260806-c5d183: on a cyclic group of prime order every projection that propagates deterministically under the FULL translation action is constant or injective. Sigma here is a partial action (translation by factor-base points only), outside the theorem's hypothesis, and the candidate asserts no propagating projection. The candidate claims no new object.
- IDEA-20260901-863e36: propagation is a property of a projection paired with an operation group; the pair above is the one already filed, so no new pair is introduced.
- KN-OPEN-020: scoped to prime-field generic subgroups and bounded-degree algebraic factor bases; the candidate is a binary/Koblitz subspace base, so the open class is not entered and not closed.
- KN-FIND-ffe1df Theorem C: exact sum-compatible filters / combining rules on E(F_p) of prime order are impossible (a surjective homomorphism onto a smaller set); the candidate has no filter or combining rule.
Result: the pair is not new notation for a recorded rigidity result (it is not a rigidity result at all, since the candidate proposes no representation change). No N4 collision, and no N4 novelty either.

## Disposition recommendation (strict)

Do not file C4 as a separate lead and do not log it as an advance. It duplicates LEAD-ICE-sat-xor-pdp-oracle's repricing clause and sibling C3. For the lead, the only bookkeeping worth doing is to record the derived band on best_measured: SAT/rho 0.854 / 7.34 / 50.99 at w = 0 / 0.1 / 1 with the same weight on both sides (rho natives 344.7 per run), crossing 1/458 GAE per conflict vs rho and 0.0508 vs Frobenius MITM, propagations unrecorded; and state the cell as "unresolved at the boundary" per 5a (not closed_dominated). Per 5a, no calibration (the candidate's optional callgrind Ir run, an L2 wall, or LEAD-RHO-native-step-cost's canonicalisation pricing) can close it through the band, because w = 0 is a mandatory point and SAT/rho = 0.854 there. The lead can close only by the alpha(m) fit (H-SATIC-5c526c; conflicts tracking 2^(ml)/m!) read together with LEAD-ICB-decomposition-encoding-and-sat's measured alpha ~ m, or by an owner rule decision on w = 0 for solver conflicts. A callgrind Ir-per-conflict run is still a legitimate further band point (the lead's calibration clause, PMU-free), but it moves no disposition.

## RAW

### lead_atlas.py --match run atlas1 (python3 tools/lead_atlas.py --match "...")
phrase: break-even price per SAT conflict from sealed counters decides the native-XOR SAT point-decomposition oracle
   15  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    8  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    8  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    7  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    5  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    5  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571

### lead_atlas.py --match run atlas2 (python3 tools/lead_atlas.py --match "...")
phrase: SAT conflicts cost too much for the SAT decomposition oracle to beat rho
   19  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   15  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   13  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   13  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   12  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   12  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   12  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   12  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)

### lead_atlas.py --match run atlas3 (python3 tools/lead_atlas.py --match "...")
phrase: per-attempt UNSAT cost 2^{alpha l} with alpha ~ m; SAT or XOR solver for point decomposition beats rho; conflicts unpriced
   31  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   25  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   22  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   21  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   18  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   15  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   14  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   14  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination

### lead_atlas.py --match run atlas4 (python3 tools/lead_atlas.py --match "...")
phrase: CDCL conflict price lower bound clause-database traversal watched literals SAT solver cost per conflict versus rho GAE
   18  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   16  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   15  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   12  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
   12  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
   12  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   12  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels

### build_frontier_map.py --match run frontier1 (same phrase order as atlas1-4)
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-e7f98e  score=3  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-1c2928  score=2  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-cd0049  score=2  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-2480c6  score=1  [record/reported]  Binary-curve ECDLP records (FPGA)
    sources: KN-LIT-097, KN-LIT-fc4c4d, KN-LIT-f663db
KR-RHO-cb1c58  score=1  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-RHO-ea34b8  score=1  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964

### build_frontier_map.py --match run frontier2 (same phrase order as atlas1-4)
KR-IC-1fcdbc  score=12  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5765d2  score=12  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-1c2928  score=12  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-a4dd54  score=8  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-5b1c0a  score=8  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
KR-IC-081a58  score=7  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=7  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006

### build_frontier_map.py --match run frontier3 (same phrase order as atlas1-4)
KR-IC-5765d2  score=25  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-1c2928  score=15  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=14  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-955fd6  score=12  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-6654ba  score=12  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-a4dd54  score=11  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-cd0049  score=9  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa

### build_frontier_map.py --match run frontier4 (same phrase order as atlas1-4)
KR-RHO-1c2928  score=12  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-5765d2  score=10  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-e7f98e  score=9  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-RHO-13bf67  score=8  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=8  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-1fcdbc  score=7  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-93979e  score=7  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2

### ledger grep (proposals/hypotheses index)
##### proposals.jsonl 2678
--- term /conflict/ : 7 hits
  IDEA-20260915-0d8e90 [proposed] On the Trimoska S_4 Weil-descent instances with V = {deg x < l} and m = 3 factor-base points, WDSat 
  IDEA-20260920-b9f0c5 [proposed] On E/F_2 Koblitz curves over F_{2^n}, build Weil-descent PDP instances whose factor base is a Froben
  IDEA-20260926-b11cb1 [proposed] CEILING FIRST. No row moves. The law says XOR-Gaussian elimination inside a DPLL search on the desce
  IDEA-20261007-ece173 [proposed] With every cost charged (attempts, failures, timeouts at a fixed conflict cap, preprocessing, symmet
  IDEA-20261017-4b1672 [proposed] For WDSat on Weil-descended Semaev systems over F_{2^n} (prime n 13..31, Koblitz and ordinary, V = p
  IDEA-20261017-fd3924 [proposed] On toy Koblitz curves y^2+xy=x^3+ax^2+1 over F_2^n (n in 11,13,17,19,23; m in 2,3; k in k0,k0+1; k0=
  IDEA-20261018-f2cd4d [proposed] In the exhaustive-core regime (conflicts per refutation c 2^(ml), expected solutions per target lam 
--- term /break-?even/ : 7 hits
  IDEA-20260805-6253cf [unverified] GOAL-CRYPTO-001 admits a candidate if it shows "a fully charged wall-clock or operation-count advant
  IDEA-20260809-217be0 [proposed] Published estimates are dominated by the precomputation phases, with the individual-logarithm descen
  IDEA-20260815-38a1cc [proposed] Preprocessing gives per-target cost below sqrt(N) after an offline phase, which is the one classical
  IDEA-20260901-cc08db [proposed] FIVE SEPARABLE CLAIMS, ALL ABOUT COST MODELS. (A) THE OBJECT. For a balanced n-bit modulus with p of
  IDEA-20261016-0bacee [proposed] O = any cheap procedure outputting one candidate for dlog_P(R) (the lane's Smart ratio), success rat
  IDEA-20261017-bbc53e [proposed] Stage: relation decomposition by coincidence harvest. Relations needed are c*U (c in 0.92..1.0; U = 
  IDEA-20261018-a0830c [proposed] BRIDGE of IDEA-20261017-bbc53e (law), EXP-PFDR-ca5e01 (design) and nine leads' stated bounds. (i) An
--- term /SATIC|ecbench_sat_pdp|sat[_ -]pdp/ : 8 hits
  IDEA-20260904-3c7a91 [proposed] SCOPE: symmetrized S_{m+1} pdp over F_{2^n}, Weil-descended to F_2, in the CNF-XOR model of SRC-SATI
  IDEA-20260904-e12b5a [proposed] SCOPE: symmetrized S_{m+1} pdp over F_{2^n} descended to F_2, CNF-XOR model of SRC-SATIC-TRIMOSKA-20
  IDEA-20260905-24d827 [proposed] SCOPE: ordinary prime-field short-Weierstrass curves, p in 2^12..2^32, decomposition arity m in {2,3
  IDEA-20260905-a6f98e [proposed] SCOPE: symmetrized binary pdp of SRC-SATIC-TRIMOSKA-2019 (m = 3, l in 3..8, n in {3l-1, 4l}) in its 
  IDEA-20260909-fe3e07 [proposed] A fully charged non-Groebner batched m in {5,6,8} point-decomposition sieve, together with held-out 
  IDEA-20260922-9d12bd [proposed] SCOPE: the CNF-XOR descended point-decomposition (pdp) model of SRC-SATIC-TRIMOSKA-2019 and the dire
  IDEA-20260930-b26bbc [proposed] OUTCOME CLASS (a), A SEARCH EXPONENT, with the escape from the SATIC ceiling named: the ceiling ml -
  IDEA-20260930-ba8184 [proposed] OUTCOME CLASS (a), A SEARCH EXPONENT, aimed at and honestly expected to be NEGATIVE: the record test
--- term /per (solver|SAT)[ -]?(op|conflict|propagation)|GAE per (solver|conflict|op)|solver[_ ]ops/ : 0 hits
--- term /native[- ]XOR|CryptoMiniSat|WDSat/ : 11 hits
  IDEA-20260915-0d8e90 [proposed] On the Trimoska S_4 Weil-descent instances with V = {deg x < l} and m = 3 factor-base points, WDSat 
  IDEA-20260915-7ef636 [proposed] P3b and P6 of H-ICPERF-cc4847 are measured on objects that differ in TWO ways at once, and as measur
  IDEA-20260920-18dc28 [proposed] Trimoska-Ionica-Dequen list as future work testing WDSat on the simplified system obtained from the 
  IDEA-20260920-b9f0c5 [proposed] On E/F_2 Koblitz curves over F_{2^n}, build Weil-descent PDP instances whose factor base is a Froben
  IDEA-20260922-793fd8 [proposed] (A) THE STRUCTURAL FACT THAT MAKES A PORTFOLIO EVEN WORTH ASKING ABOUT. Every decomposition attempt 
  IDEA-20260930-4406e0 [proposed] On one frozen explicit base of the n=7 Koblitz subgroup and one frozen explicit base of the n=11 Kob
  IDEA-20261001-3f2d06 [proposed] KR-IC-e847d1 reports Crossbred as a hybrid Boolean MQ method; KR-IC-5765d2 records XOR-SAT (WDSat / 
  IDEA-20261001-5c936b [proposed] KR-IC-8b9daa reports Karabina's symmetric-function reformulation of binary-curve PDP as a constant/p
  IDEA-20261017-4b1672 [proposed] For WDSat on Weil-descended Semaev systems over F_{2^n} (prime n 13..31, Koblitz and ordinary, V = p
  IDEA-20261017-fd3924 [proposed] On toy Koblitz curves y^2+xy=x^3+ax^2+1 over F_2^n (n in 11,13,17,19,23; m in 2,3; k in k0,k0+1; k0=
  IDEA-20261018-b4bc61 [proposed] Crossbred with the improved preprocessing of ePrint 2026/360 solves the Weil-descended PDP cells at 
--- term /price[ds]? .*(conflict|solver)|(conflict|solver).*(price|priced|pricing|unpriced)/ : 2 hits
  IDEA-20260808-812554 [proposed] Write T_solve = B^{(m-1)sigma} for the cost of finding all m-decompositions of one target over a siz
  IDEA-20261015-1e8145 [proposed] R1/R2 membership/relation/LA comparison: price identical auxiliary finite-coset bases as list, expan
##### hypotheses.jsonl 2131
--- term /conflict/ : 6 hits
  H-BINSTD-85e778 [analyzed] CLAIM (control / measurement; HOLD-I; NO ATTACK). Setting: polynomial-basis F_2-multiplication tenso
  H-BINSTD-e241a8 [approved] CLAIM (null-object protocol + differential measurement). RQ-BINSTD-b6f698 mandates the prime-degree 
  H-FROB-a5bf86 [approved] On Koblitz E/F_2 over F_{2^{41}} (primary) and F_{2^{43}} (decisive, capacity-gated), for Frobenius-
  H-FROB-ad36e7 [proposed] (From the IDEA-20261017-fd3924 claim.) On toy Koblitz curves y^2+xy=x^3+ax^2+1 over F_2^n (n in 11,1
  H-ICPERF-81de5c [specified] (L1, THE CONFLICT LAW.) On Weil-descended S_4 instances over V = {deg x < l} with m = 3 factor-base 
  H-SATIC-5c526c [proposed] (From the IDEA-20261017-4b1672 claim.) For WDSat on Weil-descended Semaev systems over F_{2^n} (prim
--- term /break-?even/ : 0 hits
--- term /SATIC|ecbench_sat_pdp|sat[_ -]pdp/ : 0 hits
--- term /per (solver|SAT)[ -]?(op|conflict|propagation)|GAE per (solver|conflict|op)|solver[_ ]ops/ : 0 hits
--- term /native[- ]XOR|CryptoMiniSat|WDSat/ : 12 hits
  H-ALBIN-007 [analyzed] Autolab package `bin_exp007` (binary-field ECDLP) produces a scoped empirical measurement that can b
  H-BINSTD-e241a8 [approved] CLAIM (null-object protocol + differential measurement). RQ-BINSTD-b6f698 mandates the prime-degree 
  H-FROB-a5bf86 [approved] On Koblitz E/F_2 over F_{2^{41}} (primary) and F_{2^{43}} (decisive, capacity-gated), for Frobenius-
  H-FROB-ad36e7 [proposed] (From the IDEA-20261017-fd3924 claim.) On toy Koblitz curves y^2+xy=x^3+ax^2+1 over F_2^n (n in 11,1
  H-ICPERF-195806 [inconclusive] On the certified ordinary curve y^2+xy=x^3+31 over GF(2^61), with prime subgroup order 5764607525572
  H-ICPERF-2c57cc [specified] For the 60 shipped instances of SRC-ICPERF-TRIMOSKA-ECICB-2024 (cells (15,5), (17,6), (19,6); 10 S +
  H-ICPERF-71a809 [analyzed] CLAIM (measurement / constant-factor mechanism; DX-04 survivor of DEC-20260928-63addc; NO ATTACK; NO
  H-ICPERF-81de5c [specified] (L1, THE CONFLICT LAW.) On Weil-descended S_4 instances over V = {deg x < l} with m = 3 factor-base 
  H-ICPERF-c9380d [approved] CLAIM (measurement / tooling; NO ATTACK). Setting: the ICPERF PDP boundary cells (15,5), (17,6), (19
  H-ICPERF-cc4847 [weakened] For the 60 shipped instances of SRC-ICPERF-TRIMOSKA-ECICB-2024 (cells (15,5), (17,6), (19,6); 10 S +
  H-KIC-9416d9 [proposed] Under normative completion SHA256=1419bc2107601476c4fd44f90d67475ec15e98eef68a35888df9abfaed0aa3e5, 
  H-SATIC-5c526c [proposed] (From the IDEA-20261017-4b1672 claim.) For WDSat on Weil-descended Semaev systems over F_{2^n} (prim
--- term /price[ds]? .*(conflict|solver)|(conflict|solver).*(price|priced|pricing|unpriced)/ : 2 hits
  H-CERTBIN-3e547f [approved] With rho exponent 60.81, the m = 4 ceiling exponent is exactly 5881/200, strictly above 29.40 and st
  H-OAKLEY-c2e7b7 [approved] 4! = 24 and 5! = 120, so their ratio is 5. The inequality 2^{4p} > 24 * 2^{40} fails at p = 11 and f

### semantic sweep
### grep ATLAS.md (semantic sweep)
18:| `LEAD-EXO-ml-learned-models` Machine learning / neural and RL approaches to ECDLP and its subroutines | open_next_step | Run a learnability control on toy prime-order groups: train a model to predict a log bit from coordinates, with a planted-structure positive control (a known homomorphic leak) and a random-relabelling nul
26:| `LEAD-ICB-nonlinear-frob-stable-bases` Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points | open_next_step | Run the approved matched-\|F\| per-attempt cost comparison: trace-spectrum V_E (H-CERTBIN-5a81ca) and n
34:| `LEAD-ICE-sat-xor-pdp-oracle` SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing | open_next_step | Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per s
37:| `LEAD-ICP-coincidence-harvest-structured-base` Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | open_next_step | Run the break-even growth ladder (IDEA-20261018-a0830c): measure kappa_rel for the best FAM-1 geometry at 3+ rungs from 
69:| `LEAD-ICE-rootfind-pairtable-oracle` Root-finding / pair-table decomposition oracle in place of a Groebner solve | open_blocked | Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op, replay on a second host (L2+), and re-run the
139:| `LEAD-ICB-nonlinear-frob-stable-bases` Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points | open_next_step | Run the approved matched-\|F\| per-attempt cost comparison: trace-spectrum V_E (H-CERTBIN-5a81ca) and 
158:| `LEAD-ICE-sat-xor-pdp-oracle` SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing | open_next_step | Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per 
165:| `LEAD-ICE-rootfind-pairtable-oracle` Root-finding / pair-table decomposition oracle in place of a Groebner solve | open_blocked | Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op, replay on a second host (L2+), and re-run th
182:| `LEAD-ICP-coincidence-harvest-structured-base` Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection | open_next_step | Run the break-even growth ladder (IDEA-20261018-a0830c): measure kappa_rel for the best FAM-1 geometry at 3+ rungs from

### grep KRMAP.md

### c4_verify.py output
SAT GAE/run 874.0835750749999 rho GAE/run 1023.7589189717568 FrobMITM GAE/run 4372.353367275
conflicts/run 68899.15 total 2755966 calls 749 conf/call 3679.5273698264355
rho unpriced natives/run 344.7
sat unpriced_units ['solver_conflicts_uncharged'] rho unpriced_units ['canonicalisations_uncharged', 'partition_hashes_uncharged', 'table_inserts_uncharged', 'table_queries_uncharged'] fm unpriced []
c* vs rho (rho natives at 0): 0.0021723830249975058
c* vs rho (rho natives at w, 5a): 0.0021833060274972214
c* vs FrobMITM: 0.050773772857865454
w=0: SAT/rho natives-at-0 0.854 | SAT/rho natives-at-w (5a) 0.854 | SAT/FrobMITM 0.200
w=0.001: SAT/rho natives-at-0 0.921 | SAT/rho natives-at-w (5a) 0.921 | SAT/FrobMITM 0.216
w=0.01: SAT/rho natives-at-0 1.527 | SAT/rho natives-at-w (5a) 1.522 | SAT/FrobMITM 0.357
w=0.1: SAT/rho natives-at-0 7.584 | SAT/rho natives-at-w (5a) 7.337 | SAT/FrobMITM 1.776
w=1: SAT/rho natives-at-0 68.154 | SAT/rho natives-at-w (5a) 50.987 | SAT/FrobMITM 15.958
L0 ns/conflict (target_PDP/solver_ops): 15099.108714693868
L0 ns/conflict (solve_wall/solver_ops): 15108.429704865735
L0 ns per GAE, rho solve_wall/GAE: 115.64822323493357
  ns/GAE solve_wall ic-mitm 175.46778355622098
  ns/GAE solve_wall ic-mitm-frob 340.81546019431687
  ns/GAE solve_wall ic-sat-xor 1190913.5398301948
  ns/GAE solve_wall rho-aa 443.19105952767495
  ns/GAE solve_wall rho-strong 115.64822323493357
c* in ns at rho-arm L0 ns/GAE: 0.25123223702669184 ns
floor 10ns -> w= 0.08646911919853278  SAT/rho (natives at 0): 6.673184733730327  (natives at w): 6.484396812750373
measured 15.1us -> GAE per conflict: 130.56066312424693
setup share of rho GAE: 0.750229233212048
per-call wall ms: 55.557583775700934

### c4_verify.py source
import json
J=json.load(open("/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/ecbench_sat_pdp_20261009/count-qualified-main.resources.json"))
A={a["arm"]:a for a in J["arms"]}
N=40
sat=A["ic-sat-xor"]; rho=A["rho-strong"]; fm=A["ic-mitm-frob"]
S0=sat["total_gae_sum"]/N; R0=rho["total_gae_sum"]/N; F0=fm["total_gae_sum"]/N
conf=sat["phase_native_totals"]["relations.solver_ops"]/N
calls=sat["phase_native_totals"]["relations.solver_calls"]
nat=sum(rho["method_counter_totals"][k] for k in ("canonicalisations_uncharged","partition_hashes_uncharged","table_inserts_uncharged","table_queries_uncharged"))/N
print("SAT GAE/run",S0,"rho GAE/run",R0,"FrobMITM GAE/run",F0)
print("conflicts/run",conf,"total",sat["phase_native_totals"]["relations.solver_ops"],"calls",calls,"conf/call",sat["phase_native_totals"]["relations.solver_ops"]/calls)
print("rho unpriced natives/run",nat)
print("sat unpriced_units",sat["unpriced_units"],"rho unpriced_units",rho["unpriced_units"],"fm unpriced",fm["unpriced_units"])
print("c* vs rho (rho natives at 0):",(R0-S0)/conf)
print("c* vs rho (rho natives at w, 5a):",(R0-S0)/(conf-nat))
print("c* vs FrobMITM:",(F0-S0)/conf)
for w in (0,0.001,0.01,0.1,1):
    print(f"w={w}: SAT/rho natives-at-0 {(S0+w*conf)/R0:.3f} | SAT/rho natives-at-w (5a) {(S0+w*conf)/(R0+w*nat):.3f} | SAT/FrobMITM {(S0+w*conf)/F0:.3f}")
# ns conversions (L0 descriptive only)
print("L0 ns/conflict (target_PDP/solver_ops):",sat["online_phase_ns_totals"]["target_PDP"]/sat["phase_native_totals"]["relations.solver_ops"])
print("L0 ns/conflict (solve_wall/solver_ops):",sat["solve_wall_ns_sum"]/sat["phase_native_totals"]["relations.solver_ops"])
print("L0 ns per GAE, rho solve_wall/GAE:",rho["solve_wall_ns_sum"]/rho["total_gae_sum"])
for nm,a in A.items():
    print("  ns/GAE solve_wall",nm,a["solve_wall_ns_sum"]/a["total_gae_sum"])
g=rho["solve_wall_ns_sum"]/rho["total_gae_sum"]
cs=(R0-S0)/conf
print("c* in ns at rho-arm L0 ns/GAE:",cs*g,"ns")
print("floor 10ns -> w=",10/g," SAT/rho (natives at 0):",(S0+10/g*conf)/R0," (natives at w):",(S0+10/g*conf)/(R0+10/g*nat))
print("measured 15.1us -> GAE per conflict:",sat["online_phase_ns_totals"]["target_PDP"]/sat["phase_native_totals"]["relations.solver_ops"]/g)
print("setup share of rho GAE:",rho["phase_gae_totals"]["setup"]/rho["total_gae_sum"])
print("per-call wall ms:",sat["online_phase_ns_totals"]["target_PDP"]/calls/1e6)
