# Scout dossier: algebraic geometry of curves and covers (final lead-discovery round, run 2)

Field: Riemann-Hurwitz; Kummer and Artin-Schreier covers of E over F_p; split Jacobians; isogeny graphs and modular curves as carriers; trigonal and tetragonal constructions; Weil restriction in odd characteristic; decompositions of Jac(C) with E as a factor.

Author: scout subagent, 2026-10-24, run 2.

Nothing inside any repository was edited, created, added or committed. All files written are under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

## Provenance

- **Prior draft.** An earlier, unreviewed run of this same task left a dossier at this path. I preserved it unchanged as `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/scout-algebraic-geometry-covers.prior-run.md` (sha256 418d8da9...3a250e).
  - Every number below that came from that draft has been re-run or re-fetched in this session.
  - Anything I did not reproduce is marked "carried from prior draft, not reproduced".
  - Where this run contradicts the prior draft, I say so. See F4 and F5.
- **Tags.**
  - COMPUTED: produced in this session by a script under `scout/agc/`, listed in section 6.
  - RETRIEVED: fetched in this session from the web or from the LMFDB mirror.
  - READ: a local record or source file read in this session.
  - PREDICTION: an expected value, with a numbered heuristic.
- No result is labelled "promising".

## 0. Bottom line

1. **CA, prime field (B3; decides three open leads).** This is the main result of this run.
   - Under the ecbench factor-base and oracle definitions, the m = 2 relation yield on the 24-bit volcano fixtures is an exact count. It counts the signed pair sums of the realized base that land in the prime-order subgroup G, including the doubling sums 2P_i.
   - On a cofactor curve, E(F_p) = G x H. The doubling term depends on |E(F_p)[2]|, and on an l = 2 volcano that group drops from 4 (crater and intermediate levels) to 2 (floor). So floor/crater = (B-1+2)/(B-1+4) = 33/35 = 0.943 at B = 32.
   - COMPUTED over all 7,760 measured curve-models of crypto's isogeny-volcano-cost v2.1 study, from the realized bases:

     | quantity | predicted (exact count) | measured |
     |:--|--:|--:|
     | l = 2 floor/crater | 0.9429 | 0.9417 (README H1: 0.942 [0.931, 0.953]) |
     | per-class correlation, 14 l = 2 classes | 0.785 | |
     | l = 2 intermediate/crater | 0.999 | 0.993 |
     | l = 3 floor/crater | 1.002 | 1.006 |
     | within-vertex model spread (median) | CV 6.2% | tau 7.0% |

     The 3-torsion contrast class (l3-s1011) is predicted at 1.019 and measured at 1.025.
   - The study recorded the l = 2 deficit as having an unknown mechanism. This count explains it: 2-torsion through doubling relations, a finite-size constant of order 2/(B+1).
   - On prime-order curves every such lever is 0. That covers all 8 prime Table B rows: COMPUTED, each has #E = r.
   - On the cofactor fixtures the levers are positive (+6.1% level, about +11% best-of-16 model) but predicted dominated, about 11x, by projecting the base into G. One ecbench session is recommended to decide that.
   - The same count with H = 1 predicts the blocked arity-3 panel EXP-ECTD-0cf008 exactly. At P29, the exact useful occupancies of crater and floor are 0.06673 and 0.06673 (ratio 1.0001). The two validated P29 arms are predicted at 2,185.8 and 2,187.0 hits per 32,768 targets, against 2,204 and 2,191 measured (z = +0.40 and +0.09). The panel's success criterion is unreachable.
2. **CB, prime field (B1).** A three-line Galois-invisibility lemma.
   - Splitting-type ("fully split fibre") factor bases cannot be supplied to the approved Groebner oracle G1 (EXP-ICEX-153c34 reduces modulo g_V) except as their Zariski closure g_V = prod(x - v). That closure is SO-ALGFB.
   - The S_d fully-split family is a non-tower cover base with polylogarithmic membership. Its density p/d! is COMPUTED: ratio 0.949-1.042 for d = 3..7 at p of about 2^18 and 2^20.
   - This is a cheap proof that closes a cell. It moves no exponent.
3. **CC, Koblitz (B5).** Howe's principal-polarisation criterion for the trace-zero variety A_n reduces to the sign and prime factors of one Lucas number U_n(t_1, 2).
   - COMPUTED for every prime n < 140 and for n = 163.
   - Validated, RETRIEVED, against LMFDB `has_principal_polarization` on all 38 simple trace-zero classes A_3 over q in {2, 3, 4, 5, 7, 8, 9} and A_5 over q = 2. All 38 agree, and every branch of the criterion is exercised.
   - Consequences:
     - The genus-12 cell at n = 13 of LEAD-ICB-ecc2k130-jacobian-carrier is empty by theorem.
     - n = 131 is not excluded.
     - The only enumerable faithful rung that has a PPAV, n = 11, has a different Howe type from n = 131. So the toy ladder cannot sample 131's type at any enumerable genus.
4. **CD, transfer (B7).** For LEAD-TRF-teske-trapdoor-fp6-weak-class (open_unexamined), crypto's own weak-curve database already contains the per-class count of Joux-Vitse-weak representatives over F_{p^6}.
   - COMPUTED from it: about 2% of positive classes have the minimum count (12). A proxy for "class size per weak curve" has a scale-stable upper tail, with 99th percentile about 0.5 x 2p^3 at p = 41 and 47.
   - The open number is the torsor size of the weak curves, which ISO-1 records as "Bounded, not individually measured". The first step is to measure it from data in hand.
   - PREDICTION: a hidden-weakness class exists in about 1% of positive classes.
5. **No prime-field exponent candidate from this field survives.**
   - Same-field covers re-describe E-side bases (IDEA-20260902-a0ed78 (R)) or inflate the group (SO-COVER).
   - Over F_p there is no Frobenius to multiply equations, so the only algebraic factor-base inputs are Zariski-closed sets of degree at least |F| (SO-ALGFB) or towers, which are measured with no plateau.
   - Killed candidates, including the prior draft's C3 and C5, are listed in section 5.

## 1. Inputs read

- **ATLAS.md**, all 147 leads, read in full.
- **KRMAP.md**, read in full.
- **object-frame-ideation.md**, sections 1-3 (and 4-6).
- **idea-generator.md**: "Search heuristics" and "Obstructions as generative material".
- **target-result-profile.md**, part A.
- **Lead YAMLs (READ):**
  - LEAD-ICP-algebraic-membership-factor-base
  - LEAD-ICE-charged-toy-ic-exponent-vs-rho
  - LEAD-ICE-prime-field-semaev-solving-degree
  - LEAD-ICP-prime-ic-constant-engineering
  - LEAD-ICP-generic-table-decomposition
  - LEAD-TRF-same-field-genus-g-embedding
  - LEAD-TRF-small-genus-cover-general
  - LEAD-TRF-odd-char-descent-smith-quartic
  - LEAD-TRF-cover-catalog-jacobian-transfer
  - LEAD-EXO-split-jacobian-projection
  - LEAD-ICB-ecc2k130-jacobian-carrier
  - LEAD-TRF-teske-secret-isogeny-trapdoor
  - LEAD-TRF-teske-trapdoor-fp6-weak-class
  - LEAD-STR-class-representative-ic-selection
  - LEAD-ICP-isogeny-transported-relation-yield
  - Obstruction statements of 21 further rows, extracted verbatim by script; see section 7.
- **Ledger:** grep of `.index/{proposals,hypotheses}.jsonl`, plus these individual records:
  - EV-SDEG-4a1c3d
  - IDEA-20260805-4243e6
  - IDEA-20260902-a0ed78, lines 1-110
  - The index entries for IDEA-20261022-727676, IDEA-20261018-e0857e and IDEA-20260902-701458.
- **Experiments:** EXP-ICEX-153c34 specification (G1/O5 definitions); EXP-ECTD-0cf008 specification (P29/P37 inputs); `problems/prime-field-arity3-relation-oracle.md`.
- **crypto (read-only snapshot):**
  - `research/isogeny-volcano-cost-v2_20261017/`: README, specs, curves.jsonl, analysis JSON.
  - `src/cryptanalysis/ic_boundary.rs`: `prime_factor_base`, `build_negation_folded`.
  - `src/cryptanalysis/ic_framework/plugins.rs`: PrimeAbscissaBase, MitmOracle.
  - `src/cryptanalysis/f4_fp_tower.rs`: module header.
  - `research/weak_curve_database_20261012/`: README, REPORT, THEOREMS_AND_HEURISTICS, theorems.json, and weak_curves.sqlite opened read-only.
  - `research/iso1_weak_classes_20261007/REPORT.md`, header.
- **The prior-run dossier**, in full.

## 2. Findings that matter to the orchestrator (not candidates)

**F1. The B2 numbers are an enumerative-backend measurement, not a Groebner solving degree.** I read this myself in this session.
- EV-SDEG-4a1c3d's scope_statement says: "Semaev m=5 serial split (RT-1476 A1) with per-triple subresultant PRS ... Nothing here is claimed at other m, factor-base sizes, extension fields, for non-enumerative (Groebner/algebraic) decomposition solvers, or at cryptographic size."
- Its inference says: "The binding support is the serial split's own floor -- backward-triple count".
- LEAD-ICE-prime-field-semaev-solving-degree's title ("Groebner solving degree / eliminants ...") reads that 0.797 / 0.647 as an algebraic result.
- The approved algebraic oracle G1 (EXP-ICEX-153c34) reduces modulo g_V, the factor-base polynomial of degree |V|. It is therefore in the SO-ALGFB regime by construction.

**F2. LEAD-TRF-teske-secret-isogeny-trapdoor misstates the proof obligation it merged.**
- The lead's next_action says: "Enumerating or walking the class costs about sqrt(N), so the trapdoor holder's advantage over public rho is capped at zero exponent."
- The source record IDEA-20260805-4243e6 (READ) claims something different: "Total cost is about H * (c_test + c_step) ... Hence the security margin of ANY ordinary-F_p secret-isogeny trapdoor over matched rho is exactly log2(c_test + c_step) - 1.33 bits and is ZERO IN THE EXPONENT. The claim is therefore NOT that such trapdoors are impossible."
- The record bounds the public attacker's cost of exploiting the trapdoor, at rho-scale. It does not bound the holder's advantage.
- The holder's advantage is min(C_rho, H(c_test + c_step) + T_A) / T_A, an exponent whenever a non-class-invariant sub-rho weakness T_A exists.
- Over F_p no such weakness is known (KN-OPEN-cc1988). So the counting argument cannot close the lead as worded. The lead closes only through its IC-meter half, which CA decides.

**F3. KR-IC-46d822 pairs the 2004 preprint exponents with "double large primes".**
- KR-IC-46d822 says: "F_{q^3}: O(q^{10/7}) and F_{q^4}: O(q^{14/9}) with double large primes".
- RETRIEVED this session:
  - The ePrint 2004/073 abstract states O(q^{10/7}) for GF(q^3) and O(q^{14/9}) for GF(q^4) and genus 2 over GF(p^2). It names no large-prime variation.
  - The published version, J. Symbolic Comput. 2009 (DOI 10.1016/j.jsc.2008.08.005; MaRDI/zbMATH review), states heuristic O~(q^{2-2/n}), that is q^{4/3} at n = 3 and q^{3/2} at n = 4.
- Any comparator built on this KR row should use q^{2-2/n}.

**F4. Correction to the prior draft's K4.**
- The prior draft cited IDEA-20261022-727676 as a "Kummer vs isogeny tower" arm.
- That record is "Replay lever in the PKM tower F4: measure the target-independent share of cost" (READ, index).
- Velu-type towers are covered by the f4_fp_tower engine itself. Its header (READ) lists three tower step families: "Kummer: `y_j² = y_{j+1}`; Dickson: `y_j² = y_{j+1} + 2`; a 2-isogeny step: `y_j² = y_j·y_{j+1} − ξ·y_{j+1} + ξ·y_j − τ`". The last is the Velu x-map of a 2-isogeny.

**F5. Correction to the prior draft's C2 (heuristic H2.2, "size effect").**
- The volcano IC base is `prime-abscissa:size=32` (spec READ). That is a fixed count of 32 abscissae, not a fixed bound L.
- The study's planted control ("factor base 33 against 32 ... predicted 1.063") confirms the fixed count.
- So the 5.8% floor deficit is not a base-size artefact. CA gives the actual mechanism and reproduces it.

**F6. Correction to the prior draft's count model (old C4).**
- log2 h^-(K) for K = Q(zeta_131, sqrt(-7)) was given as about 545.
- The analytic class number formula for CM fields carries a factor (2 pi)^{-[K+:Q]} = 2^{-344.7}. With w = 262 the estimate is about 2^{208} (PREDICTION; the product of L(1, chi) values is ignored).
- The expected genus-130 carrier count moves from about 2^{-7583} to about 2^{-7920}. No conclusion changes. This count model adds nothing beyond the lead's own codimension 8128 (= 8515 - 387), so it is no longer offered as a candidate (K4 in section 5).

**F7. Ledger state.** The ledger index files (modified 17:44) predate the prior draft (19:04). No Howe/PPAV, fully-split, trigonal, volcano-ball or torsion-cancellation record exists in them (COMPUTED grep).

## 3. Why this field yields no prime-field exponent candidate (reasoning, not a measurement)

Over F_{q^n}, Weil restriction does two things:
- It makes the factor-base condition x in F_q a Zariski-closed linear condition.
- It turns one decomposition equation into n equations, because Frobenius is a field automorphism.

Over F_p, Aut(F_p) = 1, and no cover multiplies equations:
- A cover C -> E only re-describes an E-side base (IDEA-20260902-a0ed78 (R), READ title: "F3 HAS NO OBJECT OF ITS OWN").
- A same-field Jacobian inflates the group (SO-COVER).
- A positive-dimensional algebraic subset of the x-line has about p points.

So an algebraic oracle's factor base is either:
1. Zariski-closed of degree at least |F| (SO-ALGFB);
2. a tower of low-degree steps (the PKM cell, measured in f4_fp_tower with "about one degree per eight unknowns ... no degree plateau", IDEA-20261018-e0857e); or
3. invisible to the oracle (CB's lemma).

Archimedean presentations (digits, Coppersmith) lie outside this field.

## 4. Candidates

### CA. Exact torsion-cancellation and sum-set count law for native factor bases across volcano levels (prime field; instrument plus proof; B3; decides three open leads)

**Bottleneck.**
- B3, prime IC constant engineering: is there a curve, model or volcano-level constant to harvest?
- LEAD-STR-class-representative-ic-selection (open_next_step): yield arms (a)-(c); "l=2 IC yield floor/crater 0.942"; H4 "model tau 7.2%".
- LEAD-ICP-isogeny-transported-relation-yield (open_blocked on `problems/prime-field-arity3-relation-oracle.md`).
- The IC-meter half of LEAD-TRF-teske-secret-isogeny-trapdoor ("Both floor/crater ratios beyond 20% with 99% intervals excluding one would be the first non-invariant meter").

**External ingredients.**
- **(i) Volcano level determines the l-primary group structure** (Kohel 1996; Miret et al. 2005-2008; Ionica-Joux, "Pairing the Volcano", ANTS IX 2010 / Math. Comp. 2013, arXiv:1110.3602). Overall provenance: recalled. A web search this session found the Ionica-Joux paper but could not confirm the general level theorem.
  - The fact used here was COMPUTED directly from the fixtures, so the argument does not rest on the citation. In curves.jsonl, every crater and intermediate curve of the 14 l = 2 classes has E(F_p) = Z/n1 x Z/2 (|E(F_p)[2]| = 4), and every floor curve is cyclic in its 2-part (|E(F_p)[2]| = 2).
- **(ii) An isogeny of degree coprime to n induces a Galois-module isomorphism E[n] -> E'[n]** (standard; recalled). So odd-l volcanoes keep |E(F_p)[2]| constant across levels. COMPUTED: the l = 3 classes show h2 equal at crater and floor in all 14.
- **(iii) The ecbench definitions (READ in crypto source).**
  - `prime_factor_base`: "the `size` smallest abscissae that are on the curve, both signs", taken in the full group E(F_p), not projected to G.
  - `build_negation_folded`: "for group in groups.iter().skip(ai)". The pair table includes the diagonal sum P_i + P_i = 2P_i and skips only the identity. Keys are folded by negation.

**Mechanism (derived here; a counting identity).**
- Write E(F_p) = G x H with |G| = r prime and gcd(r, |H|) = 1. Let h_i be the H-component of base point P_i.
- For a target R uniform in G, the expected number of table hits is exactly 2 * #{distinct x-classes of sums P_i + eps P_j (j >= i) lying in G} / r.
- The G-part of each H-cancelling sum is a fixed point of G, so no independence assumption is needed.
- A sum lies in G iff its H-components cancel:
  - Off-diagonal pairs: eps h_i + h_j = 0, expected 2C(B,2)/|H|, whatever H's structure.
  - Diagonal terms: 2h_i = 0, i.e. h_i in H[2] = E(F_p)[2], expected B |E(F_p)[2]| / |H|.
- Between two curves with the same |H| (isogenous, same #E), the yield ratio is therefore (B - 1 + |E_1(F_p)[2]|) / (B - 1 + |E_2(F_p)[2]|).
- Within one curve, isomorphic models change which 32 abscissae are smallest. The realized cancellation count then fluctuates with relative SD of order sqrt(|H| / (2C(B,2))). That fluctuation is the "coordinate effect".

**COMPUTED test against the study** (scripts `agc/volcano_exact_yield.py` and `agc/volcano_compare.py`, `agc/volcano_tau.py`; 7,760 curve-models; about 8 minutes on CPU):

| quantity | exact count from realized bases | measured (crypto analysis JSON / README) |
|:--|--:|--:|
| l = 2 floor/crater, geometric mean over 14 classes | 0.9429 | 0.9417; README H1 0.942 [0.931, 0.953] |
| closed form 33/35 | 0.9429 | |
| per-class correlation, l = 2 (n = 14) | 0.785 | |
| most extreme class l2-s1001 | 0.904 | 0.893 |
| l = 2 intermediate levels / crater | 0.9992 | 0.9926 |
| l = 3 floor/crater (14 classes) | 1.0017 | 1.0062; README H2 1.006 |
| l3-s1011 (the README's 3-torsion contrast) | 1.0186 | 1.0246 (README: "deficit: not seen") |
| model effect, median over 28 classes | CV 6.2% | tau_rel 7.0% (README: 7.2%) |
| horizontal effect, median | CV 2.5% | tau_rel 1.75% (README: 1.9%) |

- The l = 2 deficit is exactly the loss of the doubling relations R = +-2P_i when the floor loses its full rational 2-torsion. It does not depend on l-torsion in general, which is why l3-s1011 shows none.
- In classes whose cofactor has odd 2-part (h2 = 1), the predicted model CV is close to 0 while the measured tau is 3-4%. That is consistent with a measurement noise floor; I infer this from the medians and did not test it separately.

**COMPUTED test against the blocked arity-3 panel** (`agc/p29_arity3_occupancy.py`; about 3 minutes):
- P29 has r = #E = 320091991, so H = 1 and no torsion effect is possible.
- "Useful" triples are three distinct abscissae with signs. The exact useful occupancy is |{distinct signed 3-sums}| / (r - 1), computed from 256 discrete logs per curve.

| endpoint | exact occupancy | expected hits / 32,768 | measured (data.json via problems/ file) | z |
|:--|--:|--:|--:|--:|
| P29-crater | 0.06673 | 2,186.5 | not run | |
| P29-floor | 0.06673 | 2,186.7 | not run | |
| P29-E2 | 0.06671 | 2,185.8 | 2,204 | +0.40 |
| P29-E3 | 0.06674 | 2,187.0 | 2,191 | +0.09 |
| P37-floor-u2 (Poisson approximation only, not exact) | 0.06459 | 2,116.6 | 2,178 | +1.38 |

- Predicted P29 floor/crater ratio: 1.0001, with target-sampling SE about 2.9%.
- The panel's success criterion ("both observed ratios at least 20 percent from 1") is unreachable.
- Realized-base variation of the distinct-sum count is +-0.03% (21,351,946 to 21,363,462 distinct sums out of 22,108,160).

**Representation-operation pair.**
- Representation: the x-coordinate of P in a chosen model (u-scaling) of a chosen vertex curve of the volcano. The base is the 32 smallest abscissae of that presentation, taken in the full group E(F_p).
- Sigma: translation by base elements (the IC partial action), with presentation changes by Velu isogenies and isomorphisms.

**Trichotomy: coordinate-dependent.** The native base is a function of the presentation. The law shows the presentation enters only through (a) the H-components of the base and (b) additive coincidences of its logs.

**SO codes touched (quoted statements in section 7).**
- **SO-ALGFB.** The premise is "mean per-target yield is binomial(B+m-1, m)/N for every base of size B", with "Scope: prime-order E/F_p, any base of size B".
  - The volcano fixtures are cofactor curves (#E = 12r in l2-s1001), which is outside that scope. The law extends conservation to them: yield depends on |E(F_p)[2]| through the doubling term, an O(1/B) effect.
  - Inside the scope (P29, H = 1) it confirms conservation, including coverage, which is the observable the statement leaves open.
- **SO-ISO.** The premise "rho and BSGS depend only on the group order and the automorphism group" binds generic algorithms; this native-base IC is not generic, so it escapes. The row has no Scope clause.
  - The law shows IC yield depends on the full group structure E(F_p) (not only on G), which changes along 2-volcanoes. The dependence is O(1/B).
- **SO-TORS.** "Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial ... Scope: prime-order G, any l != N."
  - The H-components are data of the curve, not of the log k. The law is k-independent and is consistent with the statement; nothing is escaped.
- **SO-TABLE(p).** "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off ... Scope: any generic (enumeration/table) decomposition over F_p." Not escaped: the pair table is enumerative, and CA moves constants only.

**Tier: I** (constants; an instrument and proof).

**Predicted gain.**
- **0 on prime-order curves**, which covers Table B and every deployed prime curve.
  - COMPUTED check: all 8 prime Table B rows are prime-order. For each, p = r + t - 1 (trace read from the ICV1 id) is prime with log2 p equal to the row's size. crypto's RESEARCH_IC_BOUNDARY_LEDGER.md line 115 (READ) says "prime order (roster curves to 20 bits, generated prime-order curves at 22 and 24)". PREDICTION by H-A1: the distinct-sum count of a native base equals the Poisson value 1 - exp(-lambda) to within 1e-3 relative.
  - Measured at P29: 0.06671-0.06674 against 0.06674.
  - Holds unless the base has additive structure in log space, as an AP or GAP of logs would.
- **On cofactor curves, the levers are real but small and dominated.**
  - Level selection, arm (b), floor to crater: +6.1% m = 2 yield at B = 32. This is consistent with the measured +4.5% S (H5).
  - Model selection, arm (c), H-A2: the per-model count is deterministic, so a best-of-K choice transfers from calibration to held-out targets. Its size is about sigma * E[max of K normals], about +11% for K = 16 and sigma = 6.2%. It vanishes as 1/B and is exactly 0 on cofactor-1 curves.
  - Both levers are dominated by projecting the base into G (H-A3, below).
- **Corollary, H-A3, arithmetic only and not measured.** On a cofactor-12 curve, a base projected into G has every signed pair sum in G (2C(32,2) + 32 = 1024 entries), against (992 + 128)/12 = 93.3 for the full-group base. That is a 10.97x m = 2 yield handicap in the volcano studies' IC rows ("IC/matched rho 17-170x").
  - crypto already has the projected base (`PrimeProjectedAbscissaBase`, READ).
  - This does not touch B3's prime-order Table B.

**First discriminating step.**
- Steps (a) and (b) were done in this session: the m = 2 law against 28 classes, and the P29 arity-3 exact occupancy against the two validated P29 arms.
- (c) Implement the same exact count in compiled code for P37 (r of about 2^36, B = 1600: 1600 BSGS logs, then 5.45e9 signed triples deduplicated in sorted chunks). Compare with the validated P37 arm and predict the other 17 arms.
- (d) Recommendations to the coordinator: decide the panel from the exact counts instead of reviving the blocked collector, and run the projected-base session described under the outcomes.

**Outcomes and dispositions.**
- If the P37 exact counts give floor/crater = 1 +- 0.01 and the validated P37 arm lies within 2 sigma of its exact prediction:
  - LEAD-ICP-isogeny-transported-relation-yield becomes closed_obstructed(proof). best_measured: predicted P29 ratio 1.0001; validated arms within z <= 1.4.
  - LEAD-STR-class-representative-ic-selection, prime-order scope: every representative lever is identically 0 by the law. Record closed_obstructed(proof): the doubling-term law, 0.9429 predicted against 0.942 measured.
  - The IC-meter half of LEAD-TRF-teske-secret-isogeny-trapdoor becomes closed_obstructed(proof) at toy scale.
- LEAD-STR-class-representative-ic-selection, cofactor curves. The levers (+6.1% level, about +11% best-of-16 model) are positive constants but predicted dominated by projecting the base into G.
  - Discriminating step, recommended to the coordinator and not run here: one ecbench session on the v2.1 fixtures with `PrimeProjectedAbscissaBase` against `prime-abscissa`, same B and recipe, measuring relation yield and S.
  - If the projected base reaches about 11x yield (H-A3; 10.97x at the crater, 11.6x at the floor) with the implied S drop: closed_dominated, best_measured = the measured yield and S ratio.
  - If it falls well short: open_next_step, best_measured = the measured ratio.
- If a validated arm deviates from its exact prediction by more than 3 sigma: that is a procedure or instrument defect in the panel or in this law. Record it as open_next_step, best_measured = the deviation.
- If a native base shows a coverage deficit beyond the Poisson value that grows with N (additive log structure): open_next_step, best_measured = the excess and its slope. This is the only outcome that would matter, as the lead itself says.

**Cost.** Steps (a) and (b) are done (about 12 CPU-minutes, pure Python). Step (c): about 1 day of implementation; minutes to an hour of compute.

**Self-kill risk.** Low on the law, which is a count identity verified against 7,760 curve-models and two panel arms. Medium on whether the coordinator accepts deciding a frozen panel from exact counts.

**--match phrasings and top hits (`agc/match_log.txt`):**

| phrasing | lead_atlas top hits | build_frontier_map top hit |
|:--|:--|:--|
| Own: "exact cofactor torsion cancellation yield law for prime-abscissa base across volcano levels" | LEAD-ICB-cofactor-torsion-quotients (12); LEAD-ICP-isogeny-transported-relation-yield (12) | KR-IC-955fd6 (6) |
| Plain: "why floor curves of a 2-isogeny volcano give fewer index calculus relations than crater curves" | LEAD-ICP-isogeny-transported-relation-yield (22) | KR-IC-5931ee (15) |
| Obstruction vocabulary: "isogenous curves F_p-isomorphic prime-order subgroups mean per-target yield for every base of size B coverage or variance excess that grows with N" | LEAD-ICE-decomposition-probability-audit (14) | KR-IC-5931ee / KR-IC-b0fcda / KR-RHO-755e35 (6) |

### CB. Galois-invisibility lemma for the approved G1 oracle, and the S_d fully-split base (prime field; cheap proof; B1)

**Bottleneck.**
- B1: which non-enumerative oracle inputs can exist?
- G1 (EXP-ICEX-153c34, READ) reduces modulo g_V and charges "reduction of f5 modulo g_V".
- KN-OPEN-020's "implicit-membership" open class.
- A result-class axis for LEAD-ICP-construction-normal-form (open_unexamined).

**External ingredients.**
- The Chebotarev density theorem for function fields with Weil-type error, applied to the Galois closure of a degree-d cover P^1_t -> P^1_x (Fried-Jarden, *Field Arithmetic*, Prop. 6.4.8; Murty-Scherk; recalled, not opened this session).
- Galois descent: a reduced F_p-scheme's ideal is defined by its F_p-bar-points.

**Construction.**
- Take g in F_p[t] monic of degree d with Galois group S_d, and F_g = {P in G : g(t) - x(P) splits completely over F_p}.
- Membership is one degree-d factorisation, O~(d^2 log p). The size is about p/d!, so d of about log p / log log p gives any |F| = p^beta.
- COMPUTED (`agc/splitcount_rerun.py`, a byte-identical rerun of the prior draft's script with seed 20261024): ratio of fully split count to p/d! for d = 3..7 is
  - 1.000, 1.001, 1.004, 0.995, 0.949 at p = 200003;
  - 1.000, 1.000, 0.995, 1.011, 1.042 at p = 1000003.
- IDEA-20260902-a0ed78 lines 73-74 (READ) say: "The cover-image bases with polylog membership known to this session are exactly two families, and both are TOWERS". Line 80 adds that the sibling IDEA-20260902-701458 exhibits a base outside them. F_g is a further non-tower family.

**Lemma G (derived here; unreviewed).**
- Setup: let Sigma be any polynomial system over F_p, in the x-variables and any auxiliary fibre variables, built from S_{m+1} and cover equations. Assume it contains no polynomial vanishing on F_p but not on F_p-bar, i.e. no t^p - t and no prod(x - v).
- Claim: the projection of V_{F_p-bar}(Sigma) to x-space then contains the whole decomposition variety, of dimension m - 1.
- Reason: over F_p-bar every fibre splits, and splitting type is Galois data.
- Corollary: a Groebner, F4, XL or G1 oracle that isolates F_g-decompositions must either
  - adjoin field equations of degree at least p, or
  - replace F_g by its Zariski closure g_V of degree |F_g|, which is SO-ALGFB, or the tower cell when a low-width tower description exists.
  - Every other oracle for F_g uses membership tests, so SO-TABLE applies.
- This is the oracle-side form of SO-MONO's "cycle-type census is a no-go".

**Representation-operation pair.** Representation: x(P) with the auxiliary fibre polynomial g(t) - x. Sigma: translation by base elements.

**Trichotomy: partial-action** (IC Class I).

**SO codes touched.**
- **SO-ALGFB.** The premise "A target-independent algebraic locus of degree d yields O(d) usable points" covers Zariski-closed loci. F_g is not Zariski-closed, so it escapes the premise. Lemma G then shows the escape is unusable by algebraic oracles. This is a closure that extends SO-ALGFB, not a way around it.
- **SO-TABLE(p).** The premise "Any decomposition oracle that enumerates or table-looks-up factor-base elements" is not escaped by non-algebraic oracles.
- **SO-MONO.** Consistent with it. The row has no Scope clause.

**Tier: X** (classification of B1's input space).

**Predicted gain: 0.** PREDICTION:
- H-B1: the fully-split density is (1 + o(1))/d! uniformly for d <= log p. Measured for d <= 7, p <= 2^20.
- H-B2: no non-enumerative, non-algebraic oracle reads splitting type. Lattice methods read archimedean size, not splitting type.

**First discriminating step (about half a day).**
- (a) Write Lemma G and its corollary as a reviewed derivation.
- (b) Optional sanity control only; it cannot discriminate. One equation in three unknowns has Hilbert dimension 2 regardless. The control records the solving degree of the same base given as g_V = prod(x - v).
- This is a closure by proof with no open empirical branch. A zero-dimensional splitting-type system of degree < |F| is excluded by the same Nullstellensatz argument behind SO-ALGFB.
- (c) Recommend to the coordinator an amendment note to IDEA-20260902-a0ed78 (M) recording the third family.

**Outcomes and dispositions.**
- Derivation accepted on review: closed_obstructed(theorem) for the splitting-type cell of KN-OPEN-020, recorded as a result class in LEAD-ICP-construction-normal-form.
- A reviewer finds a flaw in Lemma G: the cell stays open (unverified). No empirical branch exists.

**Cost.** About half a day of implementation; minutes of compute.

**Self-kill risk.** High that a reviewer calls it folklore. It is kept because it is the cheapest decider of what G1 can take as input, and it corrects (M).

**--match phrasings and top hits:**

| phrasing | lead_atlas top hit | build_frontier_map top hit |
|:--|:--|:--|
| Own: "Galois-type fibre splitting factor base invisible to Groebner membership oracle" | LEAD-ICP-algebraic-membership-factor-base (15) | KR-IC-49c882 (9) |
| Plain: "factor base of x values where a polynomial cover splits completely, membership by factoring" | LEAD-ICP-algebraic-membership-factor-base (18) | KR-IC-73db3f (12) |
| Obstruction vocabulary: "target-independent algebraic locus of degree d yields O(d) usable points membership polynomial prod(x - v) of degree B" | LEAD-ICP-algebraic-membership-factor-base (15) | KR-IC-f5c584 (11) |

### CC. Howe's polarisation invariant of the trace-zero variety A_n: theorem-level rung exclusions for ECC2K-130 carriers (Koblitz; B5)

**Bottleneck.** B5, LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step). Its closure "rests on a codimension heuristic (8,128), not a theorem". Its next step samples n = 11 and n = 13 "(2 primitive mod n, A simple, no small magic number)".

**External ingredients.**
- **(i) Howe's theorem** (Howe 1995, 1996), RETRIEVED this session from Howe's VaNTAGe slides, "Deducing information about a curve over a finite field from its Weil polynomial", 1 March 2022 (corrected slides), p. 10 of 38. PDF sha256 3476b013...7b2576429f7b, text extracted with pdftotext.
  - "2 Suppose K is CM, with real subfield K+. If K/K+ is ramified at a finite prime, or if π − π̄ is divisible by a prime of K inert in K/K+, then C contains a PPAV."
  - "3 Suppose the middle coefficient c of f is coprime to q, and that C does not satisfy the conditions in (2). Then there is an integer s > 0 with N_{K/Q}(π − π̄) = s², and C contains a PPAV if and only if c ≡ s mod m, where m is the prime divisor of q if q is odd, and m = 4 if q is even."
  - Also from the slides (p. 11): "Every simple odd-dimensional isogeny class over a finite field contains a PPAV."
- **(ii) LMFDB av_fq_isog** (RETRIEVED via the LMFDB SQL mirror).
- **(iii)** The Weil-restriction adjunction Hom_{F_2}(J, Res E_K) = Hom_K(J_K, E_K) (recalled).

**Derivation (here; unreviewed in general, validated below).** For E/F_2 with trace t_1 = -1 (ECC2K-130: y^2 + xy = x^3 + 1, #E(F_2) = 4):
- f_A(T) = (T^{2n} - t_n T^n + 2^n)/(T^2 - t_1 T + 2).
- The middle coefficient c equals U_n(t_1, 2). COMPUTED: verified by polynomial division for n in {3, 5, 11, 13}.
- K = Q(zeta_n, sqrt(-7)) has degree 2(n-1) for n != 7, so A_n is simple for every prime n != 7.
- Complex conjugation (-1, eps) lies in neither inertia group, so K/K+ is unramified at all finite primes.
- N_{K/Q}(π - π̄) = U_n^2.
- Every prime l | U_n satisfies l ≡ (-7/l) mod n, so Frob_l is either complex conjugation itself (inert) or trivial (split).
- Hence: **A_n has a PPAV iff U_n has a prime factor l with (-7/l) = -1, or U_n > 0.**

**General-q rule, COMPUTED and RETRIEVED** (`agc/howe_rule_validate.py`).
- I implemented Howe's criterion in full for the trace-zero variety A_n of any ordinary E/F_q:
  - Ramification of K/K+ at n when n | disc(Q(sqrt D)) and n ≡ 3 mod 4.
  - The inert-prime test, including l = 2.
  - The mod-m clause.
- Checked against LMFDB `has_principal_polarization` for all simple A_3 over q in {2, 3, 4, 5, 7, 8, 9} and A_5 over q = 2: **38 of 38 agree.**
- Branches exercised: ramified at n (2.4.ab_ad, 2.7.ac_ad), inert prime (2.3.ab_ac via l = 2, 2.4.ad_f, 2.5.ae_l, 2.8.af_r, 2.9.ac_af), mod-4 clause with c ≡ s (2.8.ad_b), mod-4 clause with c not ≡ s (2.2.ab_ab, 2.8.ab_ah, 4.2.ab_ab_d_ab), mod-p clause (2.3.ac_b, 2.5.ac_ab, 2.9.ae_h).
- A first naive version of the rule (no l = 2, no ramification test) failed at q = 3 and q = 4. That failure is why the full rule was implemented.

**COMPUTED Howe types at q = 2, t_1 = -1** (`agc/howe_lucas.py`; sympy factorint; apparition law checked for every factor):

| n | 2 primitive mod n | sign of U_n | type |
|--:|:--:|:--:|:--|
| 3, 5, 13 | yes | U = -1 | NO PPAV (n = 3, 5 match LMFDB) |
| 11 | yes | + (U = 23 ≡ 1 mod 11) | PPAV (sign only) |
| 19 | yes | - (457 ≡ 1) | NO PPAV |
| 29 | yes | - (8641 ≡ -1, inert) | PPAV (inert) |
| 31 | no | - | NO PPAV |
| 37 | yes | + and inert (73, 2663 ≡ -1) | PPAV (inert and sign), the first faithful rung of 131's type |
| 131 | yes | + (263 ≡ 1; 146505763881528721 ≡ -1, inert) | PPAV (inert and sign) |
| 139 | yes | - (all factors ≡ 1) | NO PPAV |
| 163 | yes | + and inert | PPAV |

Totals over 33 primes: 22 inert-type, 5 sign-only, 6 with no PPAV.

**LMFDB rows at q = 2 (RETRIEVED; my queries):**
- A_5 (4.2.ab_ab_d_ab): no PPAV and no Jacobian.
- A_5 x B: all classes have PPAVs and 0 have Jacobians: 5 of 5 at g = 5 and 35 of 35 at g = 6.
- A_3 x B Jacobians: 2/5 (g = 3), 1/35 (g = 4), 11/215 (g = 5), 133/1644 (g = 6).
- Simple ordinary classes, Jacobians per PPAV where the PPAV count is known: 5/7, 34/55, 183/611, 1181/20380 at g = 2..5.

**Consequences.**
1. The n = 13 rung's genus-12 cell (B = 0) is empty by theorem, as are the genus-dim-A cells at n = 19, 31 and 139. The genus 13-14 cells at n = 13 remain testable, since products A x B can carry PPAVs (cf. A_5 x B).
2. n = 131 is not excluded by any polarisation obstruction.
3. The only faithful rung with a PPAV at enumerable genus is n = 11, and it is of sign-only type. 131's type (2 primitive, inert prime and positive) first appears at n = 37 (dim 36). So no enumerable toy rung samples 131's Howe type.
   - Inference, heuristic H-C2 (not a consequence of Howe's theorem): carrier density depends on the Howe type through the PPAV count in the class. A null on the n <= 13 ladder is therefore weaker evidence about n = 131 than the lead's discriminates field implies.

**Representation-operation pair.** Representation: divisor classes on a carrier curve C/F_2 whose Jacobian contains A as an isogeny factor. Sigma: Frobenius together with the F_2-rational Z/n twist structure of Res E (A as the sum of constant-field twists E ⊗ psi).

**Trichotomy: coordinate-dependent** (Jacobian IC reads Mumford coordinates).

**SO codes touched.**
- **SO-TABLE(b).** The premise "Every oracle built from group operations and membership tests" is escaped: divisor smoothness means factoring u(x). The Scope clause "all binary and Koblitz curves, one target, setup charged" covers the target, not the carrier route.
- **SO-GEN.** The premise "any generic algorithm" is escaped (coordinate access).
- **SO-FROB.** "At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty ... Scope: Koblitz/subfield curves over F_{2^n}". This is not a factor-base route on E, so the premise "the base {x(P) in V} is pi-stable" is escaped.
- **SO-COVER.** "Scope: prime-field source curves", which excludes this setting.

**Tier: X.** Conditional on a carrier, the lead's route costs 2^37.2 against rho's 2^60.9.

**Predicted gain: 0 (cell closures).**
- The genus-dim-A cells at n = 3, 5, 13, 19, 31, 139 are closed by theorem.
- PREDICTION, H-C1: the expected genus-130 carrier count is about 2^{208} x 2^{-8128}, using H-C1a (Brauer-Siegel-size h^- including the (2 pi)^{-130} factor) and H-C1b (Jacobian fraction among a class's PPAVs is about 2^{(3g-3) - g(g+1)/2}). H-C1b is supported only to within about 2x at g = 4, 5 by the calibration rows above.

**First discriminating step (about 1 day).**
- (a) Freeze the derivation, the general-q rule and the 38-class LMFDB cross-check as a reviewed record.
- (b) Recommend to the coordinator that the ladder:
  - drop the genus-12 cell at n = 13 (vacuous);
  - run n = 11 at genus 10-12 and n = 13 at genus 13-14;
  - filter early on prescribed place counts (for B = 0: #C(F_{2^k}) = 2^k + 1 + t_k for n not dividing k);
  - record explicitly that no enumerable rung samples 131's type.
- (c) Run PARI bnfinit on K_11 = Q(zeta_11, sqrt(-7)) for h^- and Howe's PPAV count, to predict the n = 11 genus-10 carrier count.

**Outcomes and dispositions.**
- Derivation accepted: closed_obstructed(theorem) for the genus-dim-A cells at n in {3, 5, 13, 19, 31, 139}. The lead stays open_next_step.
- n = 11 genus 10-12 sampled with no carrier at the predicted density: exhausted_at_scale for the ladder at n <= 13. Record that the n = 131 closure still rests on the codimension heuristic, because no sampled rung shares 131's type.
- A carrier is found at n = 11 or n = 13: open_next_step, best_measured = carrier count and genus.

**Cost.** About 1 day of implementation; minutes to hours of compute.

**Self-kill risk.** Low on the theorem part (validated on 38 of 38 classes across every branch). Medium on H-C1b. The candidate does not close n = 131.

**--match phrasings and top hits:**

| phrasing | lead_atlas top hit | build_frontier_map top hit |
|:--|:--|:--|
| Own: "Howe principal polarization obstruction for the trace-zero variety Jacobian carrier" | LEAD-ICB-ecc2k130-jacobian-carrier (17) | KR-IC-5ea2f8 (4) |
| Plain: "can the ECC2K-130 trace-zero abelian variety be the Jacobian of a curve" | LEAD-ICB-ecc2k130-jacobian-carrier (24) | KR-IC-5ea2f8 (9) |
| Obstruction vocabulary: "codimension heuristic Torelli rarity genus 130 to 300 curve carrying A evaluable Jacobian" | LEAD-ICB-ecc2k130-jacobian-carrier (38) | KR-IC-791cb7 (9) |

### CD. Weak-representative torsor census: does any F_{p^6} isogeny class hide its Joux-Vitse-weak curve beyond a public walk? (transfer; B7)

**Bottleneck.** B7, LEAD-TRF-teske-trapdoor-fp6-weak-class (open_unexamined). Its question: "ask whether any class places its weak curve beyond a public walk".

**External ingredients.**
- **Deuring's correspondence:** an ordinary F_Q-isogeny class with trace t is the disjoint union, over orders O with Z[pi] ⊆ O ⊆ O_K, of Cl(O)-torsors of size h(O). Its weighted size is the Hurwitz-Kronecker class number H(4Q - t^2) (Deuring 1941; Schoof 1987; Waterhouse 1969; recalled).
- **Volcano navigation:** vertical steps cost O(depth) isogenies (Kohel 1996; Fouquet-Morain 2002; Sutherland 2013, "Isogeny volcanoes"; recalled).
- **Teske's trapdoor** (Teske, J. Cryptology 2006, recalled).
- **The JV weak class** (Joux-Vitse, EUROCRYPT 2012, recalled).
- **ISO-1 theorem (READ):** "every ordinary weak class has v₂(f_pi) ≥ 2", and weak curves sit "at least one level above the deepest possible level". Its own table says: "Actual endomorphism-ring 2-volcano levels | Bounded, not individually measured".

**Mechanism.**
- Weakness is cheap to test: a Legendre model whose parameter lies in the cubic norm-one torus.
- The public's best route to some weak curve in E_pub's class is a horizontal search over the torsor(s) holding weak curves, after O(depth) vertical steps. Its cost is S_pub of about min over weak orders O_w of h(O_w)/#weak(O_w), times (c_step + c_test).
- The holder's advantage is min(C_rho, S_pub + T_JV) / T_JV.
- A hidden-weakness construction exists exactly when some classes have S_pub of order C_rho.

**COMPUTED from crypto's weak_curves.sqlite** (read-only; cubic norm-one rows at p = 41, 43, 47; curves over F_{p^6}; DB grade "probabilistic_diagnostic", though the ISO-1 update says a certifying counter reproduced p = 37-59 byte for byte):
- **Weak representatives per class** come in multiples of 6, almost always 12.
- **Minimum positive count is 12** (except two rows of 6 at p = 41). The fraction of positive classes at the minimum is 732/33,224 (2.2%), 792/38,452 (2.1%) and 898/50,382 (1.8%). The mean positive count is 170-194.
- **Class support by Frobenius 2-depth** (p = 41): depth 1 has 0 of 33,620 classes positive; depth 2 has 16,578 of 16,812; depth >= 3 has 12,446/12,606, 3,148/3,150 and then all.
- **Proxy S_pub ≈ sqrt(|t^2 - 4p^6|) / (count/12)**, standing in for H(Δ)/#weak:
  - median 10,391 (p = 41) and 13,712 (p = 47);
  - 99th percentile 68,706 and 94,709, which is 0.50 and 0.46 x 2p^3;
  - maximum about 2p^3 at both primes.
  - Matched rho on E(F_{p^6}) is about 1.25 p^3 (86,000 at p = 41).
- **Single-weak-curve classes** are biased toward small |Δ| (median sqrt|Δ| 58,697 against 119,806 overall at p = 41), but 10% of them have sqrt|Δ| > 120,972.

**Representation-operation pair.** Representation: the vertex of E in the F_{p^6} isogeny graph (its endomorphism order and Cl(O)-torsor position). Sigma: horizontal and vertical isogeny steps plus the weak-test predicate. Weakness itself is the genus-3 cover over F_{p^2}.

**Trichotomy: coordinate-dependent.** JV weakness is a property of the curve model (a cover exists) and is not a class invariant.

**SO codes touched.**
- **NEAR-TRF-isogeny-to-weak / SO-ISO.** LEAD-TRF-prime-field-isogeny-to-weak: "prime fields admit no GHS descent, so the special set inside a generic class is empty at every size (EV-IT-511f3d). Scope: prime fields, ordinary or supersingular classes. Over composite-degree binary fields descent weakness is NOT class-invariant". F_{p^6} escapes the "prime fields" scope.
  - SO-ISO's T1 still holds: rho is invariant across the class.
- **SO-COVER.** "Scope: prime-field source curves", which excludes this setting.
- **SO-GEN.** The weakness is coordinate-dependent, which escapes the premise "generic algorithm".

**Tier: X.** A structural existence question; the advantage is rho/T_JV when S_pub is of order rho.

**Predicted gain.** PREDICTION: in at least 1% of positive classes at every p from 37 to 113, S_pub >= C_rho/4. In those classes a Teske-style trapdoor gives an advantage of about C_rho/T_JV.
- H-D1: H(Δ) is about c sqrt|Δ| with c in [0.3, 1].
- H-D2: weak curves are not concentrated on small-h orders; ISO-1's bound places them one level or more above the floor, where torsors are large.
- At the jv-sieve lead's historical, unvalidated ratio T_JV/C_rho = 0.0042 (p = 1823), the advantage would be about 60-240x.

**First discriminating step (1-2 days).**
- (a) For every positive class at p = 37..113 (the certified census), compute exact H(Δ) with PARI qfbhclassno, and the number of weak isomorphism classes. Verify the 12-per-curve multiplicity by enumerating one class at p = 37.
- (b) For the top-1% tail, compute End(E_w) of each weak representative by volcano climbing, and h(End(E_w)).
- (c) Compute S_pub, and compare it with C_rho and with the measured T_JV of LEAD-TRF-jv-sieve-fp6-weak-class at the same p.

**Outcomes and dispositions.**
- The tail fraction with S_pub >= C_rho/4 stays >= 0.5% across p = 37..113: open_next_step. A hidden-weakness construction exists and needs a security definition, as the lead itself says. best_measured = tail fraction and S_pub/T_JV.
- Weak representatives sit on small-h orders (S_pub << T_JV in every class), or the tail decays with p: closed_obstructed(cost_model). The public walk is always cheap, and the trapdoor hides nothing.

**Cost.** 1-2 days of implementation; CPU-hours of compute (PARI class numbers for about 1e6 classes, plus point counting for End in the tail).

**Self-kill risk.**
- Medium-high: the proxy may overstate S_pub if weak curves cluster at the crater. The ISO-1 statement bounds them only from below.
- The p of about 40-50 data are toy-sized.
- Novelty unverified: Teske-type trapdoors in odd characteristic were not searched in the web literature this session.

**--match phrasings and top hits:**

| phrasing | lead_atlas top hit | build_frontier_map top hit |
|:--|:--|:--|
| Own: "weak-representative torsor size census Joux-Vitse weak class F_p^6 trapdoor" | LEAD-TRF-teske-trapdoor-fp6-weak-class (29) | KR-IC-791cb7 (10) |
| Plain: "how far is the nearest Joux-Vitse weak curve inside an isogeny class over F_p^6" | LEAD-TRF-jv-sieve-fp6-weak-class (29); LEAD-TRF-teske-trapdoor-fp6-weak-class (27) | KR-IC-791cb7 (20) |
| Obstruction vocabulary: "secret isogeny to a weak endpoint hidden weak curve class walk costs c_test weakness not publicly recognisable" | LEAD-TRF-teske-secret-isogeny-trapdoor (41) | KR-IC-791cb7 (28) |

## 5. Killed candidates (killed by me before proposing)

- **K1. Volcano-ball (Phi_l correspondence) tower base** (the prior draft's C3).
  - A Phi_2 step has leading monomial y_j^2 y_{j+1}^2. f4_fp_tower requires one quadratic rule with leading monomial y_j^2 per tower variable ("these relations are a Gröbner basis with leading monomials `y_j²`", READ). So it is not a 1-2 day arm.
  - Its own prediction (H3.1) was domination by the Kummer slope.
  - The Velu x-map step that would be its cheap analogue already exists as the engine's "2-isogeny step".
- **K2. Cubic-Kummer (trigonal) GHS covers in odd characteristic** (the prior draft's C5).
  - Predicted outcome: a tie at n = 3. Genus 4 gives q^{4/3}, the same as Gaudry's published O~(q^{2-2/n}) (RETRIEVED, JSC 2009). At k = 6 it sits above the Kummer floor of 9.
  - Novelty is doubtful: crypto's weak-curve SOURCE_AUDIT lists Iijima-Momose-Chao (2013, more (2,...,2) covers) and "Tian supplies an odd-prime polarized cubic-restriction mechanism" (READ in its README). Cubic constructions are therefore at least partly published.
  - No gain is possible.
- **K3. Projected cofactor base as a separate B3 candidate.** Folded into CA as corollary H-A3. It applies only to cofactor curves, while Table B rows are prime-order.
- **K4. Count model for the genus-130 carrier** (the prior draft's C4 count-model half). It adds h^- (about 2^{208} after F6's correction) to the lead's own codimension 8128 and changes no conclusion.
- **K5. Unramified Z/131 Prym carriers** (new this run).
  - An unramified Z/n cover D -> D_0 over F_2 needs n | #Pic^0(D_0)(F_2) <= (1 + sqrt 2)^{2 g_0}, which forces g_0 >= 3 and genus(D) >= 263.
  - The Prym's L-function factors over geometric characters chi. It contains the constant-field twists L(E, zeta T) that make up A only by coincidence.
  - This agrees with the prior draft's K12.
- **K6. Degeneracy-locus scan of the model x isogeny-class family** (prior K1). Carried as a duplicate of IDEA-20260811-c05798; not re-verified this run.
- **K7. Same-field covers as relation sources** (prior K2). Duplicate of IDEA-20260902-a0ed78 (R) (title READ).
- **K8. S_d fully-split base as an exponent candidate** (prior K3). Lemma G (CB) leaves it enumeration-only (SO-TABLE).
- **K9. Elliptic-torsion / Lattes / Velu x-map towers** (prior K4, re-attributed). Covered by f4_fp_tower's 2-isogeny step family (F4).
- **K10. Generalized-Jacobian splitting for the Miller cocycle** (prior K5). LEAD-EXO-miller-pairing-cocycle already carries IDEA-20261017-e3a6f1 K1/K2 as its next step.
- **K11. Bielliptic small-square base; small-integer-coefficient curves; Res of a non-F_p-rational isogenous E''; conic quotient at m = 2; target-dependent window base; Hess Moebius-twisted x on ECC2K-130** (prior K6-K11). Carried with the prior reasons (xedni, extension embedding, m = 2 floor, known-log pool H-BINSTD-1447cf named in SO-TABLE(b), branch-orbit genus of about 2^{n-1}). Not re-verified beyond the quoted obstruction rows.

## 6. Session computations (reproducible; all under `scout/agc/`)

All scripts run with `python3 -I` except where noted.

| script | input | output | time |
|:--|:--|:--|:--|
| `howe_lucas.py -1` | none | Lucas U_n and Howe type for prime n < 140 and n = 163; middle-coefficient identity checked | about 10 s |
| `tracezero_polys.py`, `howe_rule_validate.py`, `lmfdb_rows.txt`, `lmfdb_hpp.json` | 44 trace-zero L-polynomials; LMFDB rows transcribed from this session's SQL results | 38/38 agreement | seconds |
| `volcano_exact_yield.py <crypto>/research/isogeny-volcano-cost-v2_20261017` | every curve-model in classes/*/curves.jsonl | `volcano_exact_yield.json` | 7.6 min |
| `volcano_compare.py` | the above plus analysis/class-*.json | `volcano_compare.json` | seconds |
| `volcano_tau.py` | as above | model and horizontal spreads against tau_rel | seconds |
| `p29_arity3_occupancy.py 0` (numpy; run without -I) | the P29 inputs of EXP-ECTD-0cf008 | exact occupancies | 3.2 min |
| `splitcount_rerun.py` | none | byte-identical copy of the prior draft's script, same seed, same output | 85 s |

Other artefacts:
- `howe_lucas.py` uses sympy factorint and checks the apparition law for every factor.
- `p29_arity3_occupancy.py`: base from abscissa 0 upward, as in the spec's base_rule ("first B distinct rational abscissae in increasing integer order").
- Weak-curve database queries: sqlite3 -readonly on `<crypto>/research/weak_curve_database_20261012/weak_curves.sqlite`; tail statistics from `cubic_p41.txt` and `cubic_p47.txt`.
- `match_log.txt`: lead_atlas and build_frontier_map output for all 12 phrasings.
- `quoted_obstructions.txt`: verbatim obstruction statements of 21 rows, extracted by script from the YAMLs.
- `dl_howe/howe_slides.pdf` and `howe_slides.txt`: Howe slides fetched this session (sha256 3476b01360aaa0158d05e0274c5298235cd7cfab1b84f773e70b9b2576429f7b).
- The LMFDB SQL queries are listed in this session's tool log: trace-zero labels; product classes at q = 2, g = 2..6; Jacobian/PPAV calibration for simple ordinary classes at q = 2.

## 7. Quoted obstruction statements (verbatim, extracted from the lead YAMLs by script)

Rows marked "(no Scope clause in row)" have none in the YAML.

- **SO-GEN** = LEAD-RHO-generic-sqrt-lower-bound [theorem]: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."
- **SO-GGM** = LEAD-EXO-augmented-oracle-ggm [theorem]: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong). Measured: the x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong) and the m=3 MITM split saving is attributable to the split, not the oracle (EV-ECDLP-7367e2). Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
- **SO-TABLE(b)** = LEAD-ICB-generic-table-oracle [theorem]: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged."
- **SO-TABLE(p)** = LEAD-ICP-generic-table-decomposition [theorem]: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."
- **SO-ISO** = LEAD-STR-isogeny-class-generic-invariance [theorem] (no Scope clause in row): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (±5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve."
- **SO-COVER** = LEAD-TRF-same-field-genus-g-embedding [theorem]: "Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd)."
- **SO-ALGFB** = LEAD-ICP-algebraic-membership-factor-base [theorem]: "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
- **SO-MONO** = LEAD-ICE-semaev-cover-monodromy [proof] (no Scope clause in row): "For every p > 3 and nonsingular E/F_p, the generic monodromy is (Z/2)^{m-2} (ordered base) and (Z/2)^{m-2} x| S_{m-1} (symmetric base, m >= 4) with an exact Frobenius rule on unramified fibres (KN-FIND-bdcd60, two blind re-derivations); on the factor-base locus S_m splits completely with an exact root multiset, so the generic-fibre cycle-type census is a no-go as a relation-rate probe at every m >= 3 (KN-FIND-4f0d84). GOAL-MONO-001 completed under DEC-20261022-a0f165."
- **SO-FROB** = LEAD-ICB-frobenius-orbit-factor-base [proof]: "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."
- **SO-TORS** = LEAD-STR-torsion-module-leak [proof]: "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N."
- **SO-DECK** = LEAD-EXO-torsor-deck-period [proof] (no Scope clause in row): "For a generically Galois cover every rational deck-invariant factors through the quotient; a transitive fibre-orbit label is base data; a connected nontrivial cover has no rational section, so a rational target-compatible selector is a missing section or trivialization (IDEA-010 gate, independently verified). The cubical/biextension lift lands on the invertible side of the recognizable/invertible duality, i.e. computing its label costs the log (IDEA-20260920-376b00)."
- **SO-ENDO** = LEAD-STR-endo-scalar-action-generic [theorem]: "For G of prime order N, End(G) = Z/N, so every endomorphism-image oracle is simulable by group operations and Shoup's bound applies (KN-FIND-b7e091, EV-GGM-79e710, DEC-20260804-3b4258). ... Scope: any prime-field or binary curve, any size, prime-order subgroup."
- **SO-PAIR** = LEAD-TRF-second-torsion-direction [theorem]: "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N."
- **SO-MULTI** = LEAD-ICB-multi-target-and-portfolio [theorem] (no Scope clause in row): "The multi-instance generic bound (L logarithms cost >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up, and batch rho (Kuhn-Struik) attains it; ..."
- **NEAR (CA)** = LEAD-ICB-cofactor-torsion-quotients [proof] (no Scope clause in row; binary curves): "On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); ... the production 2-torsion census adds 0 relations."
  - CA concerns the prime-field cofactor case and yield, not quotients.
- **NEAR (CA)** = LEAD-STR-isogeny-transport-preprocessing [proof] (no Scope clause in row): "Transporting each target to the table's curve costs O(1) isogeny evaluations and reduces 'M targets on M isogenous curves' exactly to M targets on one curve. ..."
- **NEAR (CD)** = LEAD-TRF-prime-field-isogeny-to-weak [theorem]: "Tate: ordinary curves over F_p are F_p-isogenous iff they have the same #E(F_p); trace one and k = ord_N(p) are functions of #E and p, and prime fields admit no GHS descent, so the special set inside a generic class is empty at every size (EV-IT-511f3d). Scope: prime fields, ordinary or supersingular classes. Over composite-degree binary fields descent weakness is NOT class-invariant (see LEAD-TRF-ghs-binary-composite)."
- **NEAR (K2)** = LEAD-TRF-small-genus-cover-general [proof]: "Riemann-Hurwitz census g = 1 - 2^m + 2^{m-2} R: among 2-torsion Kummer covers of E/F_{q^3} only the JV configuration gives g <= 3 (others g in {1, 7, 9, 13}); for E/GF(p^k) with F_p(j) = GF(p^k) every GHS cover has genus >= 9, 49, 41 at k = 6, 10, 14, which repriced 247 of 846 cover_descent rows down to marginal/boundary. Scope: Kummer/GHS covers of the x-line in odd characteristic."
- **NEAR (CC, K7)** = LEAD-ICP-extension-field-embedding [cost_model]: "Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n}) against the original sqrt(p): p at n = 2 and p^{4/3} at n = 3; the embedding enlarges the problem faster than the subfield helps. Scope: any fixed n."
- **NEAR (F1)** = LEAD-ICE-prime-field-semaev-solving-degree [literature] (no Scope clause in row): "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field Groebner arm."

## 8. Citations and provenance

| citation | provenance |
|:--|:--|
| Howe 1995/1996 PPAV theorem, quoted from Howe, "Deducing information about a curve over a finite field from its Weil polynomial", VaNTAGe Seminar, 1 March 2022 (corrected slides), https://math.mit.edu/~drew/vantage/HoweSlides.pdf, pp. 10-11 | RETRIEVED (PDF fetched and text extracted this session); the Trans. AMS primary was not opened |
| LMFDB av_fq_isog (q <= 9 trace-zero rows; q = 2, g <= 6 product and calibration rows) | RETRIEVED (LMFDB SQL mirror, this session) |
| Gaudry, ePrint 2004/073 abstract (q^{10/7}, q^{14/9}) | RETRIEVED |
| Gaudry, J. Symbolic Comput. 2009, DOI 10.1016/j.jsc.2008.08.005 (O~(q^{2-2/n}), via the MaRDI/zbMATH entry) | RETRIEVED; HAL returned 403 |
| Ionica-Joux, "Pairing the Volcano", ANTS IX 2010 / Math. Comp. 2013, arXiv:1110.3602 | RETRIEVED (search abstract level). CA's load-bearing torsion-by-level fact was COMPUTED from the fixtures instead |
| Miret, Moreno, Sadornil, Tena, Valls on l-torsion structure along volcanoes; Kohel 1996 thesis; Fouquet-Morain 2002; Sutherland, "Isogeny volcanoes" (ANTS X, 2013) | recalled |
| Chebotarev density theorem for function fields (Fried-Jarden, *Field Arithmetic*, Prop. 6.4.8; Murty-Scherk) | recalled (the prior draft's secondary retrieval was not repeated) |
| Deuring (1941); Waterhouse (1969); Schoof (1987) class-number counts; Teske, J. Cryptology 2006 (trapdoor); Joux-Vitse, EUROCRYPT 2012 | recalled |
| Iijima-Momose-Chao (ePrint 2013/487); Tian (arXiv:2012.07173) | READ only as cited in crypto's weak-curve README; not opened |

Internal records, READ: EV-SDEG-4a1c3d, IDEA-20260805-4243e6, IDEA-20260902-a0ed78, EXP-ICEX-153c34, EXP-ECTD-0cf008, problems/prime-field-arity3-relation-oracle.md, crypto `ic_boundary.rs`, `plugins.rs`, `f4_fp_tower.rs`, isogeny-volcano-cost-v2 data, weak_curve_database and ISO-1 report.

## 9. Sub-areas of this field searched with no candidate

- **X_0(N) and X_1(N) as carriers for prime-field E.** Genus about N^2/24. The diamond-operator reformulation is already in the ledger (prior draft: IDEA-20260806-0c9de1; not re-verified).
- **Artin-Schreier covers of E over F_p.** Degenerate: z^p - z = f(P) has a rational fibre point only when f(P) = 0, since the trace over F_p is the identity.
- **Kummer covers of E over F_p.** These give character-constant sets, which SO-ALGFB lists ("character-constant sets").
- **Tetragonal / Recillas / Donagi constructions for prime-field E.** These re-describe E-side bases (IDEA-20260902-a0ed78 (R)) or inflate the group (SO-COVER).
- **Weil restriction in odd characteristic from prime-field sources.** No subfield exists, so the extension-embedding cost model applies.
- **Split Jacobians E x E' and Richelot/Kani gluings over F_p.** Covered by SO-COVER, SO-PAIR and LEAD-EXO-split-jacobian-projection.
- **Same-field Jacobians with factor E^k.** Relations project to E-side bases (IDEA-20260902-a0ed78 (R)). Smoothness probability is set by the full Jacobian, so SO-COVER's q^{2-2/g} binds.
- **Isogeny-class or model selection for solving degree.** Carried as a duplicate of IDEA-20260811-c05798 (O-semicontinuity); not re-verified.
- **Quotients by H <= (Z/N)^* beyond Aut** (B6, LEAD-RHO-non-automorphism-equivalence).
  - A Bezout argument for algebraic H-invariants is vacuous: every lambda in (Z/N)^* has a representation a ≡ lambda b with a^2 + b^2 of order N.
  - Frobenius acts trivially on G, so End(E) acts through a + b and offers no cheap non-scalar.
  - No in-field ingredient was found.
- **Generalized Jacobians as a transfer** (B7, Miller cocycle). Covered by IDEA-20261017-e3a6f1 and IDEA-20261009-c8433d (prior draft; atlas next step READ).
