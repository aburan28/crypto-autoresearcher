# Gate N1-N4: C3 "Conflict-priced closure of the native-XOR SAT decomposition oracle"

Scout field: SAT/XOR solving and phase transitions of planted random systems (proof-complexity lower bounds and conflict pricing).
Bottleneck: B4 (LEAD-ICE-sat-xor-pdp-oracle). Gate run 2026-10-24, read-only on all repositories; only files under scratchpad/scout/ were written.
Provenance labels: retrieved = checked against a source this session; recalled = from memory, not checked; derived = arithmetic I did this session on recorded counters (not a measurement, no new run).

## VERDICT (summary)

advances_lead, lead = LEAD-ICE-sat-xor-pdp-oracle (open_next_step). Not a new mechanism, not an escape from any standing obstruction.
Candidate step (i) is the first clause of that lead's own next_action (reprice the native-XOR arm at 0, 0.1, 1 GAE per solver op) done by arithmetic instead of by ns calibration.
Five strict findings (details below):
 F1. The closure the candidate wants (closed_dominated / closed_obstructed(cost_model)) is NOT licensed by AGENTS.md 5a: SAT/rho = 0.854 at w=0 and 7.34 at w=0.1, so the order changes INSIDE the band (break-even w* = 0.00218). 5a says: "If the order of two arms changes inside the band, report them as unresolved at that boundary, never as a win for either side." Same for SAT vs Frobenius MITM (0.200 at w=0, 1.78 at w=0.1, break-even 0.0508). The candidate's sentence "the lead's first clause (above 1 across the band) is met" is false at w=0.
 F2. The (m-1)l conflict law is already in the ledger as IDEA-20260926-b11cb1 (L1: m=2 direct, "L_XG = 2^l exactly, the root-finding oracle A in disguise"; L2: chained, 2^{(m-1)l}) and IDEA-20260904-96c4f3 ((m-1)-fold enumeration dominates the SAT enumerator by 2^l/m; T_relations = m 2^n). The new content is one measured constant (3679.5 conflicts per call = 7.19 x 2^9 at m=2, l=9), which b11cb1 anticipated as an "E-PARTIAL at m = 2" realised fraction of about 0.1 (1/7.19 = 0.139, derived).
 F3. The law is stated for general m ("fixing m-1 blocks leaves S_3 affine in the last block"); that holds for m=2 direct and for chains only. For direct S_{m+1}, m>=3, b11cb1 L3 gives (m-1)l + u*(n) (residual nonlinear, Boolean degree <= m-1) and the closed lead measured alpha ~ m (WDSat 2.9985 at m=3). One cell (m=2, l=9) cannot identify an exponent: 3679.5 = 7.19 x 2^9 (exponent 1) or 1 x 2^{9 x 1.316} (constant 1). Also "per call" mixes 385 relation-yielding (SAT) calls with ~364 non-yielding ones (749 calls, 385 relations), while the lead and H-SATIC-5c526c fit per-attempt UNSAT medians, and H-SATIC records that WDSat "conf counts branch points, not CDCL conflicts"; the 2^-5.15 comparison to 2^{ml}/m! crosses solvers and units.
 F4. The proof-complexity ingredient supplies no price and no bound used in the arithmetic. Itsykson-Sokolov (retrieved) and Pipatsrisawat-Darwiche (retrieved) establish proof systems and simulations; "a conflict is a Res / Res(xor) line, therefore not priced at zero" is a modelling remark and is not in either abstract. The w=0 point of the band is a program convention (5a), which the proof-complexity remark cannot remove.
 F5. Escape of SO-TABLE is nominal: the candidate's own law says the SAT oracle behaves as (m-1)-fold enumeration with a GF(2)-linear membership test at a constant of 7.2 conflicts per leaf, i.e. inside "oracle built from group operations and membership tests". The closure is by cost, as the candidate says, but then SO-TABLE's theorem is not escaped by anything the candidate adds.
 What is new and checkable (all derived by me from count-qualified-main.resources.json; every candidate number reproduced): SAT/rho = 0.854 / 7.34 / 50.99 at w = 0 / 0.1 / 1; w* vs rho = 0.002183 (1/458.0, 2^-8.84; 0.002172 if rho's natives are left at 0); w vs Frobenius MITM = 0.05077; conflicts per call 3679.5; per run 68,899 = 1.0505 r (r = 65,587). I found no prior record of these band values or break-even for this session (grep of research/ecbench_sat_pdp_20261009, research/pdp_split_slots_20261012, ledger index).
 Recommended handling: record the band numbers on the lead as best_measured, status "unresolved at the boundary w in (0, 0.1), break-even 1/458"; do not close. Closure needs a 5a-compatible argument for excluding w=0 for conflicts (a rule decision, not a measurement) or an admitted calibration; native wall timings are currently not admitted (LEAD-RHO-native-step-cost: "no qualified Tier 0 host").

## Verification of the candidate's arithmetic (derived this session from count-qualified-main.resources.json, session ECBS1hb55a1bdabf18, host class L0)

| quantity | recorded / recomputed |
|---|---|
| ic-sat-xor total_gae_sum | 34,963.343; unpriced unit solver_conflicts_uncharged = relations.solver_ops = 2,755,966 in solver_calls 749; solver_budget_exceeded 0; propagations not recorded (confirmed: no such counter in phase_native_totals) |
| rho-strong total_gae_sum | 40,950.357 (setup 30,722.155 + search 10,228.202); unpriced natives 7,308 + 5,671 + 384 + 425 = 13,788 (confirmed) |
| ic-mitm-frob total_gae_sum | 174,894.135, unpriced_units empty, lower_bound false |
| SAT/rho at w = 0, 0.1, 1 | 0.8538, 7.337, 50.987 (w on conflicts and on rho natives alike) |
| break-even vs rho | w* = 0.002183 = 1/458.0 = 2^-8.839 |
| break-even vs Frobenius MITM | w = 0.05077 (MITM side has no unpriced counters) |
| conflicts per call | 3,679.53 = 7.187 x 2^9 = 0.02807 x (2^18/2) = 2^-5.155 x (2^18/2) |
| conflicts per run | 68,899 = 1.0505 x r, r = 65,587 (from the saved comparison file) |
| H6 extrapolation | w*(ECC2K-130) = 2^(-8.84 - 0.5 x (129 - 16)) = 2^-65.3 (arithmetic on an assumed slope 1.0, not a measurement) |
| descriptive L0 wall (not admissible under 5a) | online target_PDP 41.61 s over 749 calls = 55.6 ms per call = 15.1 us per conflict; sums over 40 runs SAT 41.62 s vs rho 1.22 ms (34,044x); saved comparison rho-strong__ic-sat-xor.json: wall median ratio 8272, 0 admitted pairs. With the rough 115.6 ns per GAE implied by rho solve_wall / total GAE this would put a conflict near 1.3e2 GAE, about 6e4 times the break-even; I treat this only as a sanity check. |

## N1 - Atlas collision

Raw outputs (atlas runs 1-4 are the 3 match_phrasings plus one of my own; runs 5-6 are two extra probes of the proof-complexity and break-even-price aspects) are pasted at the end.

Top hits read (lead YAML: mechanism + obstruction + forecloses):

1. LEAD-ICE-sat-xor-pdp-oracle (open_next_step; top hit of runs 1 and 2). SAME OBJECT. Title "SAT / native-XOR ... point-decomposition oracle with honest pricing". Its next_action.step: "Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per solver op, and fit alpha(m) of the conflict count at m in {3,4,5} (H-SATIC-5c526c)." Its discriminates: "Priced S/rho below 1 across the band would be a sub-rho toy row ...; above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant and closes the lead as dominated by the pair table." best_measured: "native-XOR SAT S/rho 0.854 lower bound, conflicts unpriced, n = 17 Koblitz, 40/40 verified". forecloses: SAT solver for point decomposition; CryptoMiniSat Gaussian elimination on Weil descent; WDSat XOR reasoning for summation polynomials; CNF-XOR encoding of the PDP; DPLL conflict law 2^(ml)/m!. No obstruction block (open). Candidate step (i) = the repricing clause of this next_action. Candidate step (ii) is a different fit (total conflicts vs r at m=2 on larger Koblitz curves) from the lead's alpha(m) at m=3,4,5, but H6 (slope 1.0) is the product law (relations x targets x oracle = m 2^n; KN-FIND-aa2efc; LEAD-ICE-generic-oracle-arity-cost-floor mechanism) restated for conflicts, and the closed lead's ladders (n = 11..31) already measure per-attempt slopes against the enumeration floor. A cross-size run of the native-XOR ecbench arm is not in the lead's evidence (single size, "not a cross-size claim" in the README), so that run would be new data, but a data point for the lead's own question.
2. KR-IC-5765d2 (known_result; N2).
3. LEAD-ICB-decomposition-encoding-and-sat (closed_obstructed; top hit of run 3, and its forecloses phrase "SAT or XOR solver for point decomposition beats rho" is verbatim the candidate's third match phrasing). obstruction.statement (kind measured, no Scope clause): "Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. ... Encoding levers are constants ..." revisit_when: "A solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3". The candidate does not answer this obstruction and does not try to: it re-derives the same non-win through the price axis, and its law (m-1)l at m=2 is consistent with it (alpha = m-1 = 1 at m=2, while the criterion alpha < m/2 - 1 equals alpha < 0 at m=2 and cannot be met there at all).
4. LEAD-ICP-icperf-binary-pdp-solver (open_next_step): solver choice (WDSat/CDCL+XOR vs Groebner); next_action H-ICPERF-c9380d, a Boolean-native Groebner column. Different action; same family (forecloses: WDSat conflict law for descended Semaev systems). Not the candidate's mechanism.
5. LEAD-ICE-rootfind-pairtable-oracle (open_blocked; runs 2 and 3). Mechanism: at m=2 the S_3 root in the last variable is x(R -/+ F_i), "one pair-sum lookup (binary)", exact and complete like enumeration. This is the object the candidate's own (m-1)l law identifies the SAT oracle with at m=2 (also b11cb1 L1). Its next_action prices the rootfind arm at 0, 0.1, 1 GAE: the same band applied to the rival oracle. Best measured cold complete IC about 1.54x strong rho (17-bit Koblitz, L0, natives unpriced). So the candidate's "SAT = enumeration at a constant" lands on this blocked lead.
6. LEAD-ICB-kic-golden-base-exact-decomp (open_next_step): "N7 pilot flat SAT / direct MITM median wall 1.70x [1.02, 2.69] (SAT slower)". Co-designed bases; different mechanism; its SAT-slower-than-MITM wall result is independent corroboration of the direction (descriptive).
7. LEAD-ICB-frobenius-search-symmetry (closed_obstructed; run 1): Frobenius as search symmetry inside one decomposition search; obstruction (proof): the absolute Frobenius is an equivariance between conjugate targets, not a per-instance symmetry. The candidate only compares against signed-Frobenius rho on the same orbit base; not touched.
8. LEAD-ICB-generic-table-oracle (closed_obstructed; run 3) and LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed; run 2): the SO-TABLE / free-oracle rows the candidate claims to escape; quotes below.
9. LEAD-ICP-icperf-writability-boundary (closed_obstructed, run 5): descended ANF exceeds the rho budget by +40.8 bits at ECC2K-130; independent of pricing; not touched by C3.
10. LEAD-RHO-native-step-cost (open_next_step, run 6): "GAE counts group additions; the native step also pays class canonicalisation ..." next_action prices canonicalisation (the rho-side natives the candidate prices at w); best_measured 718 instructions/step, ~57 field mults/step, 98.9 -> 68.2 ns/step. Relevant to the calibration the candidate says it can skip. LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked, run 6) is the B1 lead; not this mechanism.

Standing-obstruction quotes (rows read):
- SO-TABLE, LEAD-ICB-generic-table-oracle: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup charged." The candidate claims to escape the premise "built from group operations and membership tests" because the SAT oracle reads descended coordinates. Strict reading: its own measured law (7.2 conflicts per 2^l at m=2) and b11cb1 L1 / 96c4f3 say the oracle's work IS (m-1)-fold enumeration with a GF(2)-linear membership test, so the escape is nominal. The candidate's actual claim (closure by priced cost) does not depend on the escape, and escaping SO-TABLE is not needed for a closure.
- LEAD-ICE-generic-oracle-arity-cost-floor: "Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC." The SAT oracle does read coordinates algebraically, so this Scope clause is technically escaped; the candidate's "priced analogue" is a fair description but the product law T_relations = m 2^n (96c4f3, KN-FIND-aa2efc) already gives the closure at ECC2K-130 for any oracle whose per-attempt work is the (m-1)-fold enumeration.
- SO-GEN and SO-FROB: respected, not escaped (candidate says so).
- LEAD-ICB-decomposition-encoding-and-sat: quoted above; candidate consistent, not an answer.

What the candidate does that the hits' forecloses phrases do NOT cover: (a) the three band values and two break-even prices for the recorded cell; (b) the measured m=2 constant 7.19 (conflicts per 2^l) for the CryptoMiniSat native-XOR arm; (c) the explicit observation that the lead's "2^{ml}/m!" clause fails at this cell by 2^5.15. Everything else (conflict law, enumeration domination, closure at ECC2K-130) is covered by foreclosed phrases ("DPLL conflict law 2^(ml)/m!", "SAT or XOR solver for point decomposition beats rho", "pair-sum table meet-in-the-middle decomposition oracle") and by ledger records below.

Verdict for N1: advances_lead (sharper, zero-compute execution of the open lead's own repricing step). Not duplicate_of_lead only because step (i) produces numbers the lead does not yet record and step (ii) is a cross-size run the lead does not list; but the candidate offers no mechanism beyond the lead's.

## N2 - Known results (frontier map)

Raw outputs pasted at the end. Hits:
- KR-IC-5765d2 (known_mechanism / measured; top hit of runs 1, 3, 5): "SAT solvers (CryptoMiniSat) and the XOR-aware WDSat solve binary-curve PDP instances faster than Magma F4 (up to 300x on the PDP step, Trimoska-Ionica-Dequen 2020), without changing the exponent relative to rho." Internal: EV-ICPERF-390707, WDSat's advantage comes from static branching order, XOR-GE 4-7x slower. forecloses: SAT solver for point decomposition; XOR clauses for Weil descent; CryptoMiniSat for summation polynomials; Gaussian elimination in SAT for PDP. dominated_by null.
- KR-IC-1fcdbc (known_negative / measured): characteristic-2 summation algorithms stay far slower than rho; internal KN-FIND-aa2efc (ECC2K-130 free oracle at m=3 costs 2^68.58 vs rho 2^60.81).
- KR-RHO-1c2928 (known_bound / measured): lean signed-Frobenius rho at 4.996x the generic floor (the matched reference family); KR-RHO-482ed3 (signed-Frobenius rho, sqrt(m)); KR-RHO-18cc42 (ECC2K-130 rates); KR-RHO-6654ba (point halving).
- KR-IC-955fd6, KR-IC-8b9daa (Karabina symmetric formulation), KR-IC-a4dd54, KR-IC-5a43e5 (Semaev), KR-IC-889857 (first-fall-degree dispute), KR-IC-fbdb61: adjacent, not this object.
Reading: the qualitative result "SAT/XOR PDP does not change the exponent and stays far slower than rho" is a known result (KR-IC-5765d2 + KR-IC-1fcdbc). What is not in any KR row is the GAE-priced band with break-even for the count-qualified-main cell. That is a measured-data accounting item of this program, not a literature result. I found nothing in the frontier map on proof-complexity lower bounds for CDCL+XOR on Semaev systems (run 5 returned only the SAT row and Semaev/fall-degree rows).
Literature check of the candidate's citations: Itsykson-Sokolov, Annals of Pure and Applied Logic 171(1), art. 102722, 2020, DOI 10.1016/j.apal.2019.102722: retrieved (WebSearch, abstract: Res(xor), exponential lower bounds for tree-like Res(xor), incomparable with resolution, implicational completeness). Pipatsrisawat-Darwiche, Artificial Intelligence 175(2):512-525 (2011): retrieved (abstract: CDCL solvers p-simulate general resolution). Williams-Gomes-Selman, IJCAI 2003 (strong backdoors): recalled, not checked (not load-bearing for the arithmetic). Not verified by the retrieved abstracts: the specific claim "Gauss-XOR conflicts are Res(xor) lines" (modelling step; plausible, not checked). Neither paper gives a per-conflict price or a size bound for Semaev/PDP systems.

## N3 - Ledger

Greps run (output pasted at the end): terms conflict / native-xor / solver_ops / unpriced / break-even; backdoor; ideal-XG; Itsykson / Res(xor) / Pipatsrisawat / Williams-Gomes / proof complexity; 5c526c / 4b1672; 96c4f3. No proposal or hypothesis matches the priced-conflict break-even object ("price per conflict", "GAE per conflict", "crossing price" return only unrelated break-even records: IDEA-20260805-6253cf, -20261017-bbc53e, -20261018-a0830c about other leads). No hit for Itsykson, Pipatsrisawat, Williams-Gomes. "backdoor" hits: IDEA-20260904-3c7a91 and -b40e6d.
Possible same-object records (id, status, 100-char claim):
- IDEA-20260926-b11cb1 [proposed, unverified] "CEILING FIRST. No row moves. The law says XOR-Gaussian elimination inside a DPLL search on the descended point-decomposition system can never do better than the (m-1)-fold enumeration oracle ..." (OPENED, record 1 of 3). L1: m=2 direct, "ideal-XG closes every depth-l node: L_XG = 2^l exactly, the root-finding oracle A of EXP-CERTBIN-e94b27 in disguise"; L2: chains, 2^{(m-1)l}; L3: direct S_{m+1}, m>=3, 2^{(m-1)l + u*(n)}, u* about sqrt(2n); predicts "E-PARTIAL at m = 2 and E-INERT at m = 3"; realised fraction about 0.1 at m=2 from KN-FIND-47da4e. Dated 2026-09-26, before the 2026-10-09 data. = the candidate's "(m-1)l law" (the candidate cites it). Covers F2 and F3.
- IDEA-20260904-96c4f3 [proposed, unverified] "Charge the pdp honestly - a subspace factor base makes membership a GF(2) linear test, so an (m-1)-fold loop solves the pdp in 2^{(m-1)l}/(m-1)! group operations ..." (OPENED, record 2 of 3). States the SAT enumerator is dominated by 2^l/m, and "T_relations = m * 2^n, independent of both l and m", dominated by rho. Its own interpretation_limits: the loop is "almost certainly folklore".
- H-SATIC-5c526c [proposed] / IDEA-20261017-4b1672 [proposed] "alpha(m) of DPLL point decomposition at m in {3,4,5}: the per-attempt UNSAT conflict law 2^(ml)/m! persists ..." (H-SATIC OPENED, record 3 of 3). Mechanism text: "No new object; an existing one is priced." Readings H_enum alpha=m (3c7a91), H_ideal alpha->m-1 (b11cb1), H_sub alpha<m-1. Tested by EXP-SATIC-f50f16 with WDSat (branch points, not CDCL conflicts) and CryptoMiniSat as control; no approval decision yet. Covers the alpha(m) fit the lead names; the candidate's step (ii) is not a substitute.
- IDEA-20260904-3c7a91 [proposed] "The pdp CNF-XOR model admits no above-leaf pruning: the SAT solver is a complete enumerator of V^m modulo S_m ..." (not opened; index entry: strong backdoor w.r.t. unit propagation, dominated_by the (m-1)-fold enumeration). Source of the lead's 2^{ml}/m! clause.
- IDEA-20260904-e12b5a, -20260915-0d8e90, -20260922-af7396 (priced "before it is run", conflict count c 2^{kp} on the Oakley ladder; H-OAKLEY-602f93 [approved]), -20260926-89886c (SAT/UNSAT asymmetry law), -20260905-a6f98e (proof-size dichotomy: LRAT refutation length = leaf count; a clausal-proof-size record, nearest to the proof-complexity ingredient; index entry only), -20260930-b26bbc (CDCL(T) inner theory): same SAT lane, none prices conflicts in GAE.
Decision: no record holds the break-even computation; the (m-1)l law and the SAT-dominated-by-enumeration statement are recorded as proposals (status proposed, novelty_status unverified), so the candidate's law component is a duplicate of b11cb1/96c4f3; the data point and pricing are new relative to the ledger.

Corpus items outside the ledger index that bear on the decision (read-only, crypto-main):
- AGENTS.md 5a (quoted in F1) and docs/bounds/README.md ("The page shows the break-even price per uncharged operation at which the two mean ops figures cross: the dominance flips there, inside the band or beyond it"). The break-even price is a standard output of the program's `ecbench band` tooling, so w* is not a new instrument.
- research/notes/index-calculus/RESEARCH_SAT_SEMAEV.md (the program's own CDCL+parity engine, m=3): conflicts per triple 0.97-1.02 ("The solver never prunes"), cost per conflict 35, 65, 140, 512 us across n = 15..24, SAT reject 5x to 62x slower than brute force and widening. Earlier, independent record that the SAT route is "a strictly worse way to enumerate".

## N4 - Notation check

Pair stated by the candidate: (R1, UP + Gauss-Jordan on XOR rows + CDCL), R1 = x in the F_2-subspace V of F_{2^17} Weil-descended to 9 bits per leg, Sigma_IC = translation by factor-base points. This is the pair already filed as "Representation R1 (x in F_2-subspace V; descent gives ml core bits). Sigma = S_m permutations ... (plus translation by factor-base points: Class I, partial-action, IDEA-20260806-c5d183)" in H-SATIC-5c526c / IDEA-20261017-4b1672. The tracked object is a work counter (conflicts), not a projection of a group element, so there is no new representation or quotient in the candidate.
Rigidity results, checked:
- IDEA-20260806-c5d183 (every lossy ECDLP object propagating deterministically under FULL translation on a prime-order group is constant or injective): the candidate's Sigma is translation by factor-base points only, a partial action (Class I), and its object is a cost counter, so the theorem is neither contradicted nor re-derived.
- IDEA-20260901-863e36 (propagation is a property of a projection paired with an operation group): the Frobenius orbit appears only in the comparator (signed-Frobenius rho on the same orbit base), unchanged.
- KN-OPEN-020 (bounded-degree algebraic factor bases over F_p scoped out; open class is high-degree / implicit-membership / target-dependent): the candidate's V is an F_2-linear subspace, the scoped-out linear class (b11cb1 says the same: "nothing escapes it"); no claim of escape is made, and none is available.
- KN-FIND-ffe1df Theorem C (exact sum-compatible tree combining rule is a quasigroup, hence a group, hence no proper quotient of prime-order E(F_p)): about Wagner-tree filters; not engaged.
Conclusion: C3 is not a rigidity result in new notation, and not an object-frame escape either: it prices an existing object.

## Appendix - raw outputs (verbatim)

### lead_atlas.py --match "price SAT conflicts in group-addition equivalents crossing price"
```
    7  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    6  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    5  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    4  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    3  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    3  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    3  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    2  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
```

### build_frontier_map.py --match "price SAT conflicts in group-addition equivalents crossing price"
```
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-cd0049  score=2  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
```

### lead_atlas.py --match "how much would each SAT solver conflict have to cost before the SAT oracle loses to rho"
```
   16  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   14  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   13  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   13  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   11  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
   11  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
```

### build_frontier_map.py --match "how much would each SAT solver conflict have to cost before the SAT oracle loses to rho"
```
KR-RHO-825bca  score=11  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-5765d2  score=10  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-1c2928  score=9  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-18cc42  score=6  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-93979e  score=6  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
```

### lead_atlas.py --match "SAT or XOR solver for point decomposition beats rho"
```
   26  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   25  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
   20  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
   19  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
   18  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   14  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   14  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   12  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
```

### build_frontier_map.py --match "SAT or XOR solver for point decomposition beats rho"
```
KR-IC-5765d2  score=25  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-1fcdbc  score=14  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-6654ba  score=12  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-a4dd54  score=11  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-1c2928  score=11  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-955fd6  score=10  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-8b9daa  score=8  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-cd0049  score=8  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

### lead_atlas.py --match "conflict count per call scaling 2^{(m-1)l} strong backdoor Gauss-XOR CDCL cost model (own phrasing)"
```
   14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    6  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    6  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    6  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
    6  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
    6  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
```

### build_frontier_map.py --match "conflict count per call scaling 2^{(m-1)l} strong backdoor Gauss-XOR CDCL cost model (own phrasing)"
```
KR-RHO-1c2928  score=10  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-825bca  score=5  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-18cc42  score=3  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-RHO-e7f98e  score=3  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-IC-081a58  score=2  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-791cb7  score=2  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-955fd6  score=2  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-46d822  score=1  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
```

### lead_atlas.py --match "resolution proof complexity lower bound for CDCL with XOR Gauss on descended Semaev system (extra probe)"
```
   13  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   11  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    8  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    8  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    8  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    7  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

### build_frontier_map.py --match "resolution proof complexity lower bound for CDCL with XOR Gauss on descended Semaev system (extra probe)"
```
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-0d2021  score=3  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-fbdb61  score=2  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
```

### lead_atlas.py --match "break-even price per unpriced native operation SAT conflicts versus rho band (extra probe)"
```
   12  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    9  KR-RHO-e7f98e                                known_result       GPU Pollard rho: academic state of the art is thin
    9  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    9  LEAD-ICE-charged-toy-ic-exponent-vs-rho      open_blocked       One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
    9  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    8  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    7  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    7  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
```

### build_frontier_map.py --match "break-even price per unpriced native operation SAT conflicts versus rho band (extra probe)"
```
KR-RHO-e7f98e  score=9  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-IC-1fcdbc  score=7  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5765d2  score=7  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-93979e  score=6  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
```

### ledger index greps (proposals.jsonl, hypotheses.jsonl; script scout/_c3_raw/ledger_grep.py, case-insensitive substring over the whole index row)
```
### G1 terms(any>=2 of): conflict, native-xor, solver_ops, unpriced, break-even
##### proposals.jsonl minhits 2 ['conflict', 'native-xor', 'solver_ops', 'unpriced', 'break-even', 'breakeven']
##### hypotheses.jsonl minhits 2 ['conflict', 'native-xor', 'solver_ops', 'unpriced', 'break-even', 'breakeven']

### G2 any of: break-even, breakeven, crossing price, price per conflict
##### proposals.jsonl minhits 1 ['break-even', 'breakeven', 'crossing price', 'price per conflict', 'gae per conflict', 'gae per solver']
1 IDEA-20260805-6253cf [unverified] Charging the baseline instead of the candidate: the Wiener AT^2 break-even surface for GOA | GOAL-CRYPTO-001 admits a candidate if it shows "a fully charged wall-clock or operation-count advant
1 IDEA-20260809-217be0 [proposed] The descent phase is asymptotically negligible and concretely expensive — measure it, beca | Published estimates are dominated by the precomputation phases, with the individual-logarithm descen
1 IDEA-20260815-38a1cc [proposed] PREPROCESSING ATTACKS CHANGE THE PER-TARGET EXPONENT AND ARE THE ONLY CLASSICAL ROUTE THAT | Preprocessing gives per-target cost below sqrt(N) after an offline phase, which is the one classical
1 IDEA-20260901-cc08db [proposed] WHERE DOES KNOWING SOMETHING START TO MATTER: the operative leakage threshold is not the C | FIVE SEPARABLE CLAIMS, ALL ABOUT COST MODELS. (A) THE OBJECT. For a balanced n-bit modulus with p of
1 IDEA-20261016-0bacee [proposed] Break-even line for full-value section predictors: Smart-ratio success rate rho beats the  | O = any cheap procedure outputting one candidate for dlog_P(R) (the lane's Smart ratio), success rat
1 IDEA-20261017-bbc53e [proposed] Break-even excess for coincidence-harvested relations: kappa must reach the unknown count  | Stage: relation decomposition by coincidence harvest. Relations needed are c*U (c in 0.92..1.0; U = 
1 IDEA-20261018-a0830c [proposed] The break-even growth ladder: a lead matters only if its excess grows 2^(8 delta*) across  | BRIDGE of IDEA-20261017-bbc53e (law), EXP-PFDR-ca5e01 (design) and nine leads' stated bounds. (i) An
##### hypotheses.jsonl minhits 1 ['break-even', 'breakeven', 'crossing price', 'price per conflict', 'gae per conflict', 'gae per solver']

### G3 any of: backdoor
##### proposals.jsonl minhits 1 ['backdoor']
1 IDEA-20260904-3c7a91 [proposed] The pdp CNF-XOR model admits no above-leaf pruning: the "SAT solver" is a complete enumera | SCOPE: symmetrized S_{m+1} pdp over F_{2^n}, Weil-descended to F_2, in the CNF-XOR model of SRC-SATI
1 IDEA-20260904-b40e6d [proposed] A four-tier null ladder for the CNF-XOR pdp model - if a shape-matched random Boolean syst | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} Weil-descended to F_2 and its non-symmetrized counterpar
##### hypotheses.jsonl minhits 1 ['backdoor']

### G4 any of: ideal-xg
##### proposals.jsonl minhits 1 ['ideal-xg']
1 IDEA-20260926-b11cb1 [proposed] GAUSSIAN ELIMINATION IN SAT HAS A SOLVER-FREE CEILING, THE IDEAL-XG LAW: linearising the r | CEILING FIRST. No row moves. The law says XOR-Gaussian elimination inside a DPLL search on the desce
##### hypotheses.jsonl minhits 1 ['ideal-xg']

### G5 any of: itsykson, res(⊕), pipatsrisawat, williams-gomes, proof complexity
##### proposals.jsonl minhits 1 ['itsykson', 'res(⊕)', 'pipatsrisawat', 'williams-gomes', 'proof complexity', 'proof-complexity']
##### hypotheses.jsonl minhits 1 ['itsykson', 'res(⊕)', 'pipatsrisawat', 'williams-gomes', 'proof complexity', 'proof-complexity']
1 H-ECDLP-29f047 [proposed]  | SCOPE: the frozen toy Semaev point-decomposition systems already used in this program's DREG lane, a

### G6 both: SAT and rho and priced
##### proposals.jsonl minhits 3 ['sat', 'rho', 'priced', 'conflict']
3 IDEA-20260901-e4184f [proposed] THE ENDOMORPHISM CLAW, PRICED BY A COVOLUME IDENTITY. Small |D_0| supplies about sqrt(p/|D | Five statements. A is the construction, B is the covolume identity that is the whole content, C is t
3 IDEA-20260915-0d8e90 [proposed] The PDP cost law the boundary table should test: WDSat's UNSAT conflict count equals c * 2 | On the Trimoska S_4 Weil-descent instances with V = {deg x < l} and m = 3 factor-base points, WDSat 
3 IDEA-20260922-af7396 [proposed] THE SAT ARM OF THE OAKLEY n = 5 LADDER IS PRICED BEFORE IT IS RUN, AND THE PRICE IS q^4: o | Let E/F_{2^{5p}}: y^2 + xy = x^3 + b with b not in F_{2^p} (the Oakley shape; both RFC 2409 curves s
3 IDEA-20260926-89886c [proposed] THE SAT/UNSAT ASYMMETRY LAW AT m = 3: a sound early-abort mutant-closure filter (W_3, then | CEILING FIRST. This bears on arity m = 3 and on the chained regime. On ECC2K-130 the product law (KN
##### hypotheses.jsonl minhits 3 ['sat', 'rho', 'priced', 'conflict']

### G7 any of: 5c526c, 4b1672
##### proposals.jsonl minhits 1 ['5c526c', '4b1672']
1 IDEA-20261017-4b1672 [proposed] alpha(m) of DPLL point decomposition at m in {3,4,5}: does 2^(ml)/m! persist on chained S_ | For WDSat on Weil-descended Semaev systems over F_{2^n} (prime n 13..31, Koblitz and ordinary, V = p
##### hypotheses.jsonl minhits 1 ['5c526c', '4b1672']
2 H-SATIC-5c526c [proposed] alpha(m) of DPLL point decomposition at m in {3,4,5}: the per-attempt UNSAT conflict law 2 | (From the IDEA-20261017-4b1672 claim.) For WDSat on Weil-descended Semaev systems over F_{2^n} (prim

### G8 any of: 96c4f3
##### proposals.jsonl minhits 1 ['96c4f3']
1 IDEA-20260904-3c7a91 [proposed] The pdp CNF-XOR model admits no above-leaf pruning: the "SAT solver" is a complete enumera | SCOPE: symmetrized S_{m+1} pdp over F_{2^n}, Weil-descended to F_2, in th
1 IDEA-20260904-7fd218 [proposed] Two-axis factor attribution for the pdp - every toggleable ingredient moves EITHER the lea | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} descended to F_2, and the dir
1 IDEA-20260904-96c4f3 [proposed] Charge the pdp honestly - a subspace factor base makes membership a GF(2) linear test, so  | SCOPE: binary elliptic curves over F_{2^n}, n prime, factor base B = {(x,
1 IDEA-20260904-b40e6d [proposed] A four-tier null ladder for the CNF-XOR pdp model - if a shape-matched random Boolean syst | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} Weil-descended to F_2 and its
1 IDEA-20260904-e12b5a [proposed] Gaussian elimination is inert on the pdp CNF-XOR model for a derivable reason - under the  | SCOPE: symmetrized S_{m+1} pdp over F_{2^n} descended to F_2, CNF-XOR mod
1 IDEA-20260905-24d827 [proposed] The prime-field analogue of the SATIC ceiling - a bit-blasted or Groebner-theory CDCL(T) s | SCOPE: ordinary prime-field short-Weierstrass curves, p in 2^12..2^32, de
1 IDEA-20260905-79112a [proposed] Incremental assumption-based solving across targets amortises nothing - with the target's  | SCOPE: binary symmetrized pdp, m = 3, l in 4..8, plain CNF model with the
1 IDEA-20260922-29b1c5 [proposed] THE 2-TORSION TRANSLATION QUOTIENT IS NOT AVAILABLE TO A SUBSPACE FACTOR BASE ON ANY STAND | SETTING. E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, b != 0, ordinar
1 IDEA-20260922-493606 [proposed] A CHEAP m=4 CELL THAT ONLY A KOBLITZ-SHAPED STANDARDIZED CURVE MAKES REACHABLE: closing th | SCOPE: toy Koblitz-shaped (a,b in F_2) and pseudorandom-shaped (mu=1, mat
1 IDEA-20260922-7ab503 [proposed] THE ABSOLUTE FROBENIUS x -> x^2 IS A GENUINE COORDINATE-SHIFT SYMMETRY OF THE DESCENDED PO | SETTING. For E: y^2+xy=x^3+ax^2+b over F_{2^m} in a NORMAL basis {alpha,a
1 IDEA-20260922-845a77 [proposed] A MEET-IN-THE-MIDDLE CLAW DECOMPOSITION OF THE POINT-DECOMPOSITION STEP ITSELF: split an m | Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck se
1 IDEA-20260922-9d12bd [proposed] REDUCTION-POLYNOMIAL SPARSITY (PENTANOMIAL vs TRINOMIAL) AS A c_leaf-AXIS- ONLY LEVER FOR  | SCOPE: the CNF-XOR descended point-decomposition (pdp) model of SRC-SATIC
1 IDEA-20260922-af7396 [proposed] THE SAT ARM OF THE OAKLEY n = 5 LADDER IS PRICED BEFORE IT IS RUN, AND THE PRICE IS q^4: o | Let E/F_{2^{5p}}: y^2 + xy = x^3 + b with b not in F_{2^p} (the Oakley sh
1 IDEA-20260922-faa8d2 [proposed] A SOLVER-QUERY MEET-IN-THE-MIDDLE POINT DECOMPOSITION IS PROVABLY DOMINATED BY STRAIGHT EN | SCOPE: symmetrized descended pdp over F_{2^n}, n prime, factor base a sub
```
