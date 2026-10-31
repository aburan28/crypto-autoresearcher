# Novelty gate N1-N4: C4 [out-of-field side finding] LMFDB census decides H-FROB-ff99bf

Date of gate: 2026-10-24. Scope: one candidate, read-only against the repositories; everything written lives under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

Candidate (as given): LMFDB `av_fq_isog` census, q = 2: g<=4 none with 131 | #A(F_2); g=5 24 of 14,325 classes (all simple, 11 with a
Jacobian, e.g. 5.2.b_d_e_h_n); g=6 617 of 164,937; claims H-FROB-ff99bf "refuted" and the census sub-step of
LEAD-ICB-nonlinear-frob-stable-bases "complete"; field_key = lattice reduction / small-root methods (the candidate is out of that field).

## 0. VERDICT (summary)

**verdict = advances_lead**, lead = `LEAD-ICB-nonlinear-frob-stable-bases` (disposition `open_next_step`).

The candidate is the lead's own named next-step arm ("finish the dimension-5/6 Weil-polynomial census over F_2 for 131 | #A") carried out
by lookup. It is **not** a new mechanism, it escapes no standing obstruction, and about half of its content is already in the ledger.

| piece of the candidate | status after this gate |
| --- | --- |
| g<=4: zero classes with 131 \| #A(F_2) | ALREADY RECORDED: KN-OPEN-095df5 (dims 1-4, exact, 2026-09-21); counts 5/35/215/1645 re-retrieved here |
| g=5: exactly 24 of 14,325 classes, all with 131 \| L(1) | ALREADY RECORDED, identical numbers: EV-BINSTD-2d41c3 (2026-10-01, strength preliminary: "24 sympy-agreed hits, LMFDB 14325, amb=0"). The refutation of H-FROB-ff99bf's universal claim is therefore already implied by that evidence ("Outcome A ... already ruled out by the g=5 hit list"). The lead's own next_action text already cites "H-BINSTD-944a66 has preliminary support". |
| g=6: 617 of 164,937 | NOT in the ledger. Ledger g=6 is `failed_infrastructure` under IMP-H1 (partial 99/164937 classes after ~5.6e6 tests, projected ~1377-1409 h; "must not be cited as exclusion"). The 617 is a retrieved external figure, not a count from the program's own instrument. |
| LMFDB Jacobian flag (11/24 at g=5; 173/617 at g=6) and explicit curve equations | NOT in the ledger. EV-BINSTD-2d41c3 left "Jacobian-or-not" as the follow-on for the 24 hits (a_r >= 0 only necessary; "none claimed as Jacobians"). Same retrieval gives `hyp_count`: 0 of 24 at g=5, 8 of 617 at g=6 (bears on H-FROB-f3d248, status approved, which I did not open). |
| point-count spectrum of the hits: g=5 only 131 or 262 (21 + 3); g=6 from 131 up to 1441 | NOT in the ledger. It is far below the Weil ceilings 6725 / 39201 used by H-FROB-66d9ae (approved, zero runs). What that implies for a base size and covering arity depends on how the Couveignes-Lercier base is counted, and that is UNVERIFIED here (section 6 gives both readings, labelled derived arithmetic; the primary source is unread). No inference about the candidate's usefulness is drawn from it. |
| "H-FROB-ff99bf: refuted" | Content right (g=5 hits falsify the universal claim), but already recorded in EV-BINSTD-2d41c3; the formal state transition is the Coordinator's. Not a new fact. |
| "census sub-step: complete" | OVERSTATED. g=5 complete (program's exact census, matched LMFDB 14325). g=6 hit list is LMFDB-asserted only; the program's own exact enumeration is infrastructure-incomplete, and LMFDB would be serving as both data and completeness control. |
| SO-FROB escape | NOT claimed and NOT achieved (candidate says so). The census supplies a group, no base, no membership degree, no cost. |

What is genuinely new and usable by the lead owner: the g=6 count, the Jacobian/explicit-curve information, and the observation that the
available groups have small |A(F_2)| (<=262 at g=5, <=1441 at g=6), far below the Weil ceilings. Nothing here moves any cost, exponent or leaderboard row. Plain statement of what is NOT new: the refutation of H-FROB-ff99bf and the g=5 list were already recorded (EV-BINSTD-2d41c3), and the lead's `discriminates` branch ("no dimension-5/6 abelian variety ... closes the route") was already decided against closing before this candidate; the candidate does not change the lead's state. The real increment is the g=6 LMFDB counts (externally sourced, not reproduced in-program because of IMP-H1) and the Jacobian-or-not answer that EV-BINSTD-2d41c3's `refine` decision named (11 of 24 at g=5, 173 of 617 at g=6, with LMFDB curve equations). No SO-FROB revisit condition is met.

## 1. N1 Atlas collision

Commands (from /Volumes/SSD990-2/crypto-autoresearcher, with LEAD_ATLAS_CRYPTO / LEAD_ATLAS_CRYPTANALYSIS / LEAD_ATLAS_ECC_CHALLENGES exported as instructed):
`python3 tools/lead_atlas.py --match "<phrase>"` for the three `match_phrasings` (runs 1-3), one phrasing of mine (run 4), and one further
phrasing on the Jacobian/explicit-model part (run 5). Raw outputs are pasted in section 8.

Per-run reading of the top hits (lead YAMLs opened for every non-KR hit; mechanism, obstruction, forecloses, next_action read):

**Run 1** ("LMFDB census ... dimension 5 and 6 with 131 dividing the point count")
1. LEAD-EXO-quantum-ecdlp-resources (open_next_step): Shor circuit resource reduction on secp256k1. Lexical hit only; different problem.
2. KR-RHO-6654ba: point halving as rho step. Unrelated.
3. LEAD-TRF-one-point-self-pairing (closed_obstructed): self-pairing/distortion from one point (Balasubramanian-Koblitz scalar-multiple theorem). Unrelated mechanism; no group over F_2 involved.
4. KR-IC-5765d2 (SAT/XOR PDP), 5. KR-IC-955fd6 (symmetries/torsion in PDP): context only.
6. **LEAD-ICB-nonlinear-frob-stable-bases (open_next_step, score 5)**: SAME OBJECT. (Ranked 6th by the lexical score, i.e. outside the top 5; found by reading all 8 rows, as the task requires a semantic read.) Its mechanism lists "F_2-rational points of low-dimensional algebraic groups or Jacobians"; its title names "algebraic-group (Couveignes-Lercier) points"; its next_action contains the census; its `discriminates` says "A census with no dimension-5/6 abelian variety having 131 | #A closes the Couveignes-Lercier route at g <= 6"; its forecloses include "Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131". The retrieved census returns the opposite branch (hits exist at g=5 and g=6), so the closing branch is unavailable and the route stays open (as the ledger already recorded at g=5).
7-8. LEAD-ICB-oakley-quintic-tower (open_next_step; n = 5 Gaudry-Diem on F_{2^155}, F_{2^185}, composite degree; unrelated), LEAD-RHO-cheon-deployed-applicability (open_blocked; r+-1 divisor census; unrelated).

**Run 2** ("is there an abelian variety over F_2 with a rational point of order 131")
1. **LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step, score 8)**: different object. It asks whether the 130-dimensional trace-zero part A of Res(E) is isogenous to an evaluable Jacobian of genus 130-300 (Torelli rarity heuristic, toy ladder n = 5, 7, 11, 13). The candidate's objects are 5- and 6-dimensional abelian varieties over F_2 with an order-131 rational point, used as a base group, not as a carrier of A. Shared ledger ref: H-FROB-f3d248 (Artin-Schreier genus 5/6 models with 131 | #Jac), which the LMFDB `hyp_count` column partly speaks to. Not a duplicate; adjacent.
2. LEAD-ICP-char0-lifting-xedni-smoothness (closed_known): xedni / Cheon lift; unrelated (characteristic 0 lifting).
3. LEAD-ICP-icperf-binary-pdp-solver (open_next_step): WDSat vs Groebner solver choice; unrelated to the census.
4. LEAD-TRF-one-point-self-pairing, 5. LEAD-TRF-second-torsion-direction (closed_obstructed; SO-PAIR, "Scope: ordinary and supersingular curves over F_p, prime N"): unrelated; the candidate is neither a pairing nor a transfer.
6-8. KR-IC-5765d2, KR-IC-955fd6, KR-RHO-6654ba: context.

**Run 3** ("Couveignes-Lercier algebraic-group points for non-subspace Frobenius-stable bases at n = 131")
1. **LEAD-ICB-nonlinear-frob-stable-bases (score 27)**: the lead (above).
2. LEAD-ICB-large-prime-variants (open_next_step): 1LP/2LP relation collection; orthogonal.
3-4. KR-IC-b0fcda (GGMP Frobenius-invariant bases), KR-RHO-6239aa: context.
5. **LEAD-ICB-frobenius-orbit-factor-base (closed_obstructed)** = SO-FROB. Obstruction text read in full (quoted in section 5).
6. LEAD-ICP-coincidence-harvest-structured-base (open_next_step): pair-sum coincidences of structured bases; orthogonal.
7-8. KR-IC-5a43e5, KR-RHO-46c2c6: context.

**Run 4** ("Weil polynomial census Jacobian rational point of order 131 over F_2 Frobenius-stable factor base")
1. LEAD-ICB-nonlinear-frob-stable-bases (19): the lead.
2-3. KR-IC-73db3f, KR-IC-b0fcda: context (stable subspace bases; GGMP).
4. KR-IC-5a43e5: context.
5. LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale; character-sum bias of DL on small-x bases): not the same mechanism.
6. LEAD-ICB-frobenius-orbit-factor-base (SO-FROB, as above).
7-8. LEAD-ICB-quasi-subfield-polynomials (closed_obstructed; Euler-Petit beta >= 3/4, SO-QSP) and LEAD-ICP-algebraic-membership-factor-base (closed_obstructed; SO-ALGFB, "Scope: prime-order E/F_p"): neighbours, not the same object. SO-ALGFB is a prime-field theorem; the candidate is over F_2 / F_{2^131}, outside its scope.

**Run 5** ("genus 5 curve over F_2 whose Jacobian has 131 points explicit model Artin-Schreier")
1. LEAD-TRF-same-field-genus-g-embedding (closed_obstructed; SO-COVER, Scope: prime-field source curves, same-field covers): unrelated (Jac(C) ~ E x A for E/F_p).
2. KR-IC-791cb7 (weak binary fields under GHS): context. 3. LEAD-ICB-ecc2k130-jacobian-carrier: adjacent as above.
4. KR-IC-5ea2f8 (GHS/cover attacks): context. 5-6. LEAD-ICE-curve-presentation-invariance, LEAD-STR-class-representative-ic-selection (open_next_step; model/isogeny presentation choice): different question.
7. LEAD-ICB-nonlinear-frob-stable-bases (score 7): the lead. 8. KR-IC-a4dd54 (hyperelliptic IC and the genus threshold): context.

N1 conclusion: exactly one lead carries the candidate's mechanism and it is open. The candidate is a sharper/partial execution of that lead's census arm, hence `advances_lead`, not `duplicate_of_lead`. What the candidate does that the lead's `forecloses` phrases do not cover: it adds retrieved g=6 counts and Jacobian/explicit-curve data; it does NOT add any factor base, membership description, relation mechanism, or cost, so it does not touch the foreclosed phrase "Couveignes-Lercier elliptic periods or algebraic-group factor base at n = 131" (that phrase is about a base, and none is built).

## 2. N2 Known results

Commands: `python3 tools/build_frontier_map.py --match "<phrase>"` for the same five phrasings (raw in section 8).
Hits across runs: KR-RHO-6654ba, KR-IC-5765d2, KR-IC-955fd6, KR-IC-5a43e5, KR-IC-73db3f, KR-IC-b0fcda, KR-IC-5ea2f8, KR-IC-49c882, KR-IC-791cb7, KR-IC-a4dd54, KR-IC-5931ee, KR-IC-cd159a, KR-RHO-755e35, KR-RHO-6239aa, KR-RHO-46c2c6, KR-RHO-482ed3 and others.
Relevant rows read in KRMAP.md: **KR-IC-b0fcda** ("Frobenius-invariant factor bases for subfield (Koblitz) curves ... reduce the number of systems to solve by up to 1/n ... speed linear algebra by n^2", GGMP, KN-LIT-0d9d28, abstract_read), **KR-IC-73db3f** (choosing the factor-base vector space V), **KR-IC-a4dd54**, **KR-IC-5ea2f8** (GHS/cover attacks).
A grep of KRMAP.md for `couveignes|honda|LMFDB|weil polynomial|abelian variet` returns no row. No KR row states or settles whether an abelian variety over F_2 of dimension 5 or 6 has 131 | #A(F_2). The KR hits describe the Frobenius-invariant-base concept (the thing the Couveignes-Lercier route would extend) and not the census.
N2 conclusion: not `known_result`. Exactly what is new relative to the KR map: a database fact (existence of such classes at g=5,6), which is a data point about an input, not a method. It is also not new relative to the ledger (section 3).

## 3. N3 Ledger collision

Index greps (raw in section 8): `.index/hypotheses.jsonl` and `.index/proposals.jsonl` with terms: 131 + (abelian|Jacobian|Weil); Couveignes|Lercier; LMFDB|av_fq; Weil-polynomial / isogeny class over F_2; algebraic group + Frobenius/stable; the ids H-FROB-ff99bf, H-BINSTD-944a66, EV-BINSTD-2d41c3, EV-FROB-a85eaf; "point of order 131"; IMP-H1 / 164937 / has_jacobian / Jacobian-or-not.

Hits that may be the same object (id, status, claim to 100 chars):
- **H-FROB-ff99bf** [analyzed] "For every abelian variety A of dimension g in {5, 6} over F_2, the point count #A(F_2) is NOT divisible by 131." The candidate's target hypothesis itself. Analyzed by DEC-20261007-0c298a: dims 1-4 reproduced, dims 5-6 feasibility-gated impediment (2,200,952,677 and 132,339,478,495,234 candidates vs 50M limit); "v2 pruned enumeration is the successor".
- **H-BINSTD-944a66** [analyzed] "Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completeness control". The successor census. Its evidence EV-BINSTD-2d41c3 reports g=5 outcome B.
- **H-BINSTD-6feaa2** [approved] "An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completeness-controlled against LMFDB class counts" (IDEA-20260926-5c26f9 is its source proposal [proposed]: "THE DIMENSION-5 AND DIMENSION-6 WEIL-POLYNOMIAL CENSUS OVER F_2 FOR 131 DIVIDING THE POINT COUNT"). Same census, third formulation.
- **H-FROB-f3d248** [approved] "Artin-Schreier normal forms of genus 5 and 6 over F_2 either contain a model with 131 | #Jac(F_2)=P(1) (explicit equation) or contain none" (source IDEA-20261002-8f26ce). The explicit-model/Jacobian column; LMFDB `hyp_count` and `curves` speak to it (not opened; status approved only).
- **H-FROB-66d9ae** [approved] "Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimension g <= 6 has m=3 sumset image fraction below 2^-80 at n=131, and the least covering arity is 11 (g=5) or 9 (g=6)" (source IDEA-20261002-cad44c). Relevance pricing of exactly the groups the candidate supplies.
- H-BINSTD-41d8b2 [supported] torus-row certificate at n=131 ({k : 131 | Phi_k(2)} = {130, 17030}); IDEA-20261002-711e84 (genus-2 Jacobian with a point of order 19, toy), IDEA-20261006-83c197 (dimension-2 quotient at the first prime failing the dimension-1 conditions), IDEA-20260926-80209d (toy control ladder): neighbours, not the same object.
- IDEA-20261009-791518 matched the LMFDB term but is about rank ladders of elliptic curves over Q; unrelated.

Records opened in full (3, by exact path):
1. `ledger/hypotheses/H-FROB-ff99bf.yaml`: confirms the candidate's hypothesis is the ledger's own, "falsifiable either way; both outcomes are results"; a hit "reopen[s] the Frobenius-invariant factor-base route (KN-OPEN-095df5 existence half)" but "does NOT by itself give a factor base: the degree half ... remains open and is OUT OF SCOPE". The candidate's own caveat repeats this.
2. `ledger/evidence/EV-BINSTD-2d41c3.yaml`: g=5 "Filtered hit_count=24 at modulus 131; ambiguous_count=0", "Unfiltered class count 14325 matches LMFDB", "Sympy re-verification: 24/24 hits agree"; g=6 `failed_infrastructure` (IMP-H1), "NOT outcome A"; decision `refine`: "Jacobian-or-not / non-linear-base follow-on for the 24 hits"; boundaries: "a_r>=0 is necessary-only; several hits fail it; none claimed as Jacobians" and "Transfer assumption if anyone later cites these hits toward a factor base ... UNVALIDATED". This record is the collision: the candidate's g=5 numbers are identical.
3. `ledger/hypotheses/H-FROB-66d9ae.yaml` (read to the predictions block): ceilings 6725 / 39201 from KN-OPEN-095df5, m* = 11 / 9, Semaev degrees 512 / 128, image-fraction < 2^-80 at m = 3, zero runs. This is the relevance question the candidate defers to "the coordinator".

Also read (knowledge, not ledger records): `knowledge/open-problems/KN-OPEN-095df5.md` (written 2026-09-21; still says the enumeration "stops at dimension 4"; not updated with EV-BINSTD-2d41c3, i.e. the knowledge entry lags the ledger).

N3 conclusion: the candidate's g=5 content duplicates recorded evidence; its g=6 and Jacobian content is an increment over the ledger. No ledger record contains LMFDB-sourced g=6 counts or LMFDB Jacobian flags (grep for `has_jacobian`, `164937`, `Jacobian-or-not` returns only the records above and unrelated ones).

## 4. N4 Notation change

The candidate is factor-base-adjacent, so N4 applies.

Candidate's pair, as stated: (representation = algebraic group A = Jac(C)/F_2 with a rational point of order 131, i.e. the F_2-rational points of a commutative algebraic group, used to describe a subset of F_{2^131} through the Couveignes-Lercier quotient isogeny; operation set Sigma = Frobenius (the Galois action of Gal(F_{2^131}/F_2) of prime order 131) acting on the factor base). Trichotomy class stated: partial-action.

Comparison with the recorded rigidity results, in the new notation:
- IDEA-20260806-c5d183 (prime-order group, projection propagating under the FULL translation action is constant or injective): requires a lossy projection pi of the ECDLP group G = <P> of order r ~ 2^131, with Sigma containing all of G's translations. The candidate has no projection of G and Sigma is not translation of G; the translation group involved is A(F_2) of order 131 (or 262), a different and tiny group, and the Galois action is by group automorphisms of E(F_{2^131}) (Frobenius), not translations. The theorem is not engaged. Candidate's own class "partial-action" is consistent.
- IDEA-20260901-863e36 (propagation = projection paired with operation set; block systems of <Sigma>; Gamma <= (Z/n)^* quotients): the Frobenius half of the candidate's pair IS this recorded pair (Gamma = <2> of order 131 acting on G; quotient = Gamma-orbit; the program's measured value for it is "orbit-union buys exactly log2(n) bits (7.03 at n = 131)" in the lead's best_measured, and the gain-exactly-n statement H-FROB-6774fb in LEAD-ICB-frobenius-orbit-factor-base). In new notation the candidate adds one thing to that pair: the base is described as the image of A(F_2) under a quotient isogeny, rather than as a subspace or orbit union. That is a change in the MEMBERSHIP DESCRIPTION of the base, which is the KN-OPEN-020 axis, not a new Sigma.
- KN-OPEN-020 (bounded-degree algebraic factor bases over a generic prime-field subgroup are scoped out; the open class is high-degree, implicit-membership or target-dependent descriptions): the candidate's description would be an implicit-membership description (periods of a quotient isogeny), so it falls in the OPEN class, not the scoped-out class; but KN-OPEN-020 is stated for prime-field subgroups and the candidate lives over F_{2^131}. The charged-cost obligations of the FACTOR-BASE ESCAPE constraint (description, membership, relation, descent, time, memory) are all unpaid by the candidate; the ledger's H-FROB-66d9ae and GGMP example 5.1 (about 280x solve cost for fraction-shaped bases, quoted in KN-OPEN-095df5) are the nearest priced neighbours.
- KN-FIND-ffe1df Theorem C (exactly sum-compatible bucket index is a surjective homomorphism onto a group of order dividing N): not engaged; no bucket index, no combining rule.
Representation class (RQ-ECDLP-623a32): R3-adjacent (Weil restriction / algebraic-group coordinates), attack stage: factor-base membership. The candidate names no stage whose charged cost it changes.
N4 conclusion: after the change of notation the candidate is neither one of the recorded rigidity results nor an escape from them. It is an input census with no tracked object, so the rigidity results simply do not apply to it, and it also does not evade them.

## 5. Standing obstruction (SO-FROB) quoted

`LEAD-ICB-frobenius-orbit-factor-base` (closed_obstructed, kind proof), obstruction.statement, including its Scope clause:

> "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."

revisit_when: "A Frobenius-stable base whose per-attempt decomposition probability exceeds the birthday value at matched |FB| (a second gain in the decomposition step), or a stable non-subspace base with membership degree far below its size (see LEAD-ICB-nonlinear-frob-stable-bases)."

The candidate escapes the "usable stable dimensions are empty" premise only in the trivial sense that a non-subspace base is not a subspace (a premise the open lead already states). It supplies no base, no membership degree and no per-attempt probability, so neither revisit condition is met, and the obstruction's scope (Koblitz/subfield curves, n prime, ECC2K-130 by structure) still covers the use the candidate points at. The other standing obstructions it could touch (SO-QSP beta >= 3/4; SO-ALGFB prime-field scope; SO-COVER prime-field scope) are not engaged.

## 6. Independent verification performed by this gate (retrieved, not recalled)

Source: LMFDB table `av_fq_isog`, queried via the LMFDB MCP read-only SQL tool on 2026-10-24, plus one public page fetched with WebFetch. Results (raw SQL results pasted in section 8):

| g | classes (q=2) | 131 \| #A(F_2) | simple | has_jacobian = 1 | has_jacobian = -1 | other flag values | hyp_count > 0 among hits |
| - | - | - | - | - | - | - | - |
| 1 | 5 | 0 | | | | | |
| 2 | 35 | 0 | | | | | |
| 3 | 215 | 0 | | | | | |
| 4 | 1645 | 0 | | | | | |
| 5 | 14325 | 24 | 24 | 11 | 13 | 0 | 0 |
| 6 | 164937 | 617 | 497 | 173 | 444 | 0 | 8 |

- Reproduces every number the candidate gave (24 / 14,325; all simple; 11 with Jacobian; 617 / 164,937). The only addition is the simple-count at g=6 (497 of 617) and the other columns.
- `has_jacobian` takes only the values 1 and -1 for all 180,907 classes with g in {4,5,6} (no unknowns), and `has_jacobian = 1` coincides with `jacobian_count > 0` in every row. The positive flags come with explicit curve equations in the `curves` column; I did not verify the equations independently.
- Point counts of the hits: g=5: #A = 131 for 21 classes and 262 for 3; g=6: 131 (375), 262 (106), 393 (51), 524 (37), 655 (26), 786 (11), 917 (2), 1048 (4), 1179 (1), 1310 (3), 1441 (1). For prime 131 the rational group is cyclic (Z/131) exactly when #A = 131; LMFDB `is_cyclic` is true for all 24 at g=5 and 602 of 617 at g=6.
- Spot check of the cited example: WebFetch of `https://www.lmfdb.org/Variety/Abelian/Fq/5/2/b_d_e_h_n` returns L-polynomial 1 + x + 3x^2 + 4x^3 + 7x^4 + 13x^5 + 14x^6 + 16x^7 + 24x^8 + 16x^9 + 32x^10, 131 points over F_2, simple and geometrically simple, contains the Jacobian of one non-hyperelliptic curve with a degree-5 plane model. L(1) = 131 recomputed by hand.
- Independent numerical re-check by this gate (`raw/check_hits.py`, output `raw/check_hits_output.txt`; float root-finding, NOT a rigorous Sturm test): all 24 g=5 L-polynomials satisfy the functional equation a_{2g-i} = 2^{g-i} a_i, have all roots at modulus sqrt(2) to within 5e-15, and L(1) in {131, 262}. By Honda-Tate (recalled, classical) each such polynomial is realised by an isogeny class over F_2.
- Derived arithmetic, two readings of the base size (NOT experimental outcomes; no run exists; both are predictions that inherit unverified assumptions). Covering arity m = least integer with |F|^m >= 2^131; Semaev degree 2^(m-2) as in H-FROB-66d9ae.
  (a) H-FROB-66d9ae's assumption |F| <= #A(F_2) (factor base = images of F_2-rational points). The same script reproduces that hypothesis's own figures (ceiling 6725 -> m = 11, degree 2^9 = 512; ceiling 39201 -> m = 9, degree 2^7 = 128). For the actual hits: #A = 131 -> m = 19; #A = 262 -> m = 17; g=6 maximum #A = 1441 -> m = 13.
  (b) Reading of the Couveignes-Lercier construction as relayed in KN-OPEN-095df5 (a rational subgroup T of order n = 131 and the quotient isogeny A -> A/T): the candidate set {P : sigma(P) - P in T} is the preimage of (A/T)(F_2), of size n * #A(F_2) = 131 * #A(F_2) points, all defined over F_{2^131}, in #A(F_2) Frobenius orbits of length 131. This count is my own derivation from the construction as relayed, not a retrieved statement; the primary source (Couveignes-Lercier) is not read here and the real base may be a sub-selection of these points. Under (b): #A = 131 -> |F| = 17161 (2^14.07), m = 10; #A = 262 -> m = 9; #A = 1441 -> m = 8; (b) applied to the ceilings 6725 / 39201 would give m = 7 / 6 rather than 11 / 9 (so reading (a) in H-FROB-66d9ae may be mis-scoped by a factor n; flagged for the lead owner, not adjudicated).
  Neither reading is used in the verdict; neither claims any cost. Arity alone does not price the descended system (GGMP example 5.1: about 280x solve cost for fraction-shaped bases, quoted in KN-OPEN-095df5).
- Prediction (labelled; conditional on LMFDB's curve enumeration being complete): Artin-Schreier curves y^2 + y = f(x) are hyperelliptic, and `hyp_count` = 0 for all 24 g=5 hit classes, so H-FROB-f3d248's genus-5 arm ("contains a model with 131 | #Jac ... or contains none") is predicted to come out "none"; at g=6 only 8 of the 617 hit classes have a hyperelliptic Jacobian (which of them, if any, are Artin-Schreier is not determined here). No run exists; H-FROB-f3d248 was not opened.

## 7. Numbered heuristics and caveats

1. LMFDB's q = 2, g <= 6 isogeny-class list is complete. Support: class counts 5/35/215/1645/14325/164937 equal the ledger's controls (IDEA-20260926-5c26f9), and the program's own exact g=5 enumeration matched 14325 independently (EV-BINSTD-2d41c3). At g=6 there is no independent reproduction (IMP-H1). The refutation of H-FROB-ff99bf does not depend on g=6 completeness.
2. Each class with a Weil polynomial of the required form is realised by an abelian variety over F_2 (Honda-Tate). Provenance: recalled (classical).
3. The `has_jacobian = -1` flag is an exhaustive negative. Provenance: unverified; the knowl text only says "Whether this isogeny class contains a Jacobian". Nothing in the verdict depends on it.
4. A positive-flag class gives a curve C/F_2 whose Jac(C)(F_2) has a point of order 131 (cyclic when #A = 131). True by the group-order statement for a class with L(1) = 131 (prime).
5. Usefulness to a factor base is conditional on the Couveignes-Lercier construction extending to such an A with explicit translation formulae and a descended-system degree bound: unverified, the primary source is not read here (it is known only through GGMP section 4.2, KN-OPEN-095df5). Provenance of Couveignes-Lercier and GGMP: recalled via the ledger/knowledge records; no retrieval attempted for them.
6. Citation provenance: LMFDB av_fq_isog = retrieved (SQL tool + WebFetch, 2026-10-24). Honda-Tate = recalled. GGMP / Couveignes-Lercier = recalled (second hand). Dupuy et al., LMFDB abelian varieties over finite fields paper = recalled (not cited as load-bearing).

## 8. RAW OUTPUTS (verbatim)

### 8.1 N1 raw: `python3 tools/lead_atlas.py --match "<phrase>"`

#### atlas run 1: "LMFDB census of abelian varieties over F_2 of dimension 5 and 6 with 131 dividing the point count"
```
    7  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    6  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    5  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    5  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    5  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
    5  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
    5  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply
```

#### atlas run 2: "is there an abelian variety over F_2 with a rational point of order 131"
```
    8  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    6  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    6  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    6  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    6  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    6  LEAD-TRF-second-torsion-direction            closed_obstructed  Reach a second N-torsion direction: nonequivariant trace-zero transfer, Kani/Robert graph kernels, Richelot gluing of E with E'
    5  KR-IC-5765d2                                 known_result       SAT and XOR reasoning for point decomposition
    5  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
```

#### atlas run 3: "Couveignes-Lercier algebraic-group points for non-subspace Frobenius-stable bases at n = 131"
```
   27  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
    7  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    6  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    5  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
    5  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    4  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    4  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
```

#### atlas run 4: "Weil polynomial census Jacobian rational point of order 131 over F_2 Frobenius-stable factor base  (own phrasing)"
```
   19  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   17  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   17  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   14  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   13  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   13  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
   13  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
```

#### atlas run 5: "genus 5 curve over F_2 whose Jacobian has 131 points explicit model Artin-Schreier  (own phrasing 2)"
```
   13  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
   11  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
   10  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    8  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    8  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    8  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    7  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
    6  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
```

### 8.2 N2 raw: `python3 tools/build_frontier_map.py --match "<phrase>"`

#### frontier run 1 (same phrasing as atlas run 1)
```
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5a43e5  score=3  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=3  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-ea34b8  score=3  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-fbd582  score=3  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
KR-IC-8b9daa  score=2  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
```

#### frontier run 2 (same phrasing as atlas run 2)
```
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-755e35  score=4  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-5a43e5  score=3  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-ea34b8  score=3  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-fbd582  score=3  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
```

#### frontier run 3 (same phrasing as atlas run 3)
```
KR-IC-b0fcda  score=6  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-46c2c6  score=4  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-7d93f6  score=3  [known_bound/proven]  Time–space bounds for many collisions and DP memory
    sources: KN-LIT-fe066e, KN-LIT-b19b9b
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-cd159a  score=1  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```

#### frontier run 4 (same phrasing as atlas run 4)
```
KR-IC-73db3f  score=17  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=17  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    matched phrase(s): Frobenius-stable factor base
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=14  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=10  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5ea2f8  score=10  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-49c882  score=9  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5765d2  score=8  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

#### frontier run 5 (same phrasing as atlas run 5)
```
KR-IC-791cb7  score=11  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5ea2f8  score=8  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-a4dd54  score=6  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-755e35  score=5  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-cd159a  score=4  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```

### 8.3 N3 raw: ledger index greps (python json scan of .index/hypotheses.jsonl and .index/proposals.jsonl)
```
### hypotheses.jsonl :: 131 AND (abelian|Jacobian|Weil) :: 8 hits
  H-BINSTD-61dad7 [approved] CLAIM (control / structural certificate; HOLD-X4). On E_a : y^2 + xy = x^3 + a x^2 + b over F_{2^n}  | title=Weil-bound vacuity of subspace abscissa density at every index-calculus dimensio
  H-BINSTD-6feaa2 [approved] CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f | title=An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completenes
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
  H-FROB-f3d248 [approved] CLAIM (arithmetic-table / structural measurement; NO ATTACK; NO EXPONENT). Let C_f : y^2 + y = f(x)  | title=Artin-Schreier normal forms of genus 5 and 6 over F_2 either contain a model wit
  H-FROB-ff99bf [analyzed] CLAIM (falsifiable either way; both outcomes are results). For every abelian variety A of dimension  | title=No abelian variety over F_2 of dimension 5 or 6 has 131 dividing its point count
  H-PFDR-14ca22 [proposed] Let E over F_p be ordinary, P a point of PRIME order N, G the group generated by P, and H any abelia | title=On a cyclic group of prime order N every bilinear map into H is determined by th
  H-SEMBIN-8e8bef [approved] CLAIM (control / measurement; NO ATTACK). Scope: Semaev 2015 Assumption 1 ONLY (KN-LIT-fa346d Sectio | title=Four Semaev/DREG degree quantities are separated by construction on the Weil-des
  H-SEMBIN-d895d9 [approved] CLAIM (measurement; NO ATTACK; NO EXPONENT). Scope: Semaev 2015 Assumption 1 and the published Semae | title=The Assumption 1 solving-degree boundary is a surface in (n, k) measurable by on
### hypotheses.jsonl :: Couveignes :: 6 hits
  H-BINSTD-41d8b2 [supported] SETTING. KN-OPEN-095df5 leaves the Couveignes–Lercier torus row without a degree bound. IDEA-2026092 | title=Torus-row certificate at n=131: {k: 131|Phi_k(2)} = {130,17030} for k<=20000; Ph
  H-BINSTD-6feaa2 [approved] CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f | title=An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completenes
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
  H-FROB-66d9ae [approved] CLAIM (structural certificate / column pricing; NO ATTACK). Setting: any Couveignes factor base F wh | title=Any Couveignes factor base built from F_2-rational points of a commutative algeb
  H-FROB-772c0b [approved] CLAIM (toy structural / degree measurement; NO ATTACK; NO EXPONENT). Setting: genus-2 models C: y^2  | title=On a genus-2 curve over F_2 with 19 | #Jac(F_2), the Mumford u_0 eliminant degre
  H-FROB-ff99bf [analyzed] CLAIM (falsifiable either way; both outcomes are results). For every abelian variety A of dimension  | title=No abelian variety over F_2 of dimension 5 or 6 has 131 dividing its point count
### hypotheses.jsonl :: LMFDB :: 2 hits
  H-BINSTD-6feaa2 [approved] CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f | title=An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completenes
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
### hypotheses.jsonl :: Weil-polynomial census :: 4 hits
  H-BINSTD-6feaa2 [approved] CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f | title=An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, completenes
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
  H-ECTD-2570d9 [approved] TEST BOUNDARY. One curve, E: y^2 = x^3 + x + 1, reduced at the single prime p = 13. The instrument e | title=
  H-FROB-cd38a5 [approved] TEST BOUNDARY. One isogeny class of abelian surfaces over F_2. The Frobenius polynomial is P(T) = T^ | title=
### hypotheses.jsonl :: algebraic group AND Frobenius-stable :: 0 hits
### hypotheses.jsonl :: H-FROB / H-BINSTD ids :: 2 hits
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
  H-FROB-ff99bf [analyzed] CLAIM (falsifiable either way; both outcomes are results). For every abelian variety A of dimension  | title=No abelian variety over F_2 of dimension 5 or 6 has 131 dividing its point count
### hypotheses.jsonl :: rational point of order 131 :: 2 hits
  H-BINSTD-944a66 [analyzed] SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of  | title=Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB completen
  H-FROB-f3d248 [approved] CLAIM (arithmetic-table / structural measurement; NO ATTACK; NO EXPONENT). Let C_f : y^2 + y = f(x)  | title=Artin-Schreier normal forms of genus 5 and 6 over F_2 either contain a model wit
### proposals.jsonl :: 131 AND (abelian|Jacobian|Weil) :: 17 hits
  IDEA-20260807-569c82 [proposed] (A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^ | title=THE PAIRING ORACLE IS THE CONSTANT ORACLE ON A PRIME-ORDER SUBGROUP, AND NO CM E
  IDEA-20260807-e7eb5d [proposed] (A) WHY THIS EXISTS. This lane's three closure records (IDEA-20260807-464ff8, IDEA-20260807-30868b,  | title=THE SELF-PAIRING INSTRUMENT AND ITS NULL - a pure-Python Miller-loop calculator 
  IDEA-20260808-40aab9 [proposed] (A) WHAT THE MACHINERY NEEDS. The SIDH-breaking machinery (Castryck-Decru; Maino-Martindale; Robert) | title=The Kani / Robert higher-dimensional embedding - the single largest recent struc
  IDEA-20260808-bba3dc [proposed] The 2022-2026 higher-dimensional isogeny toolbox (Kani's lemma, the SIDH-attack machinery, Clapoti,  | title=Torsion-rationality budget for the higher-dimensional isogeny toolbox on ordinar
  IDEA-20260808-fa1d80 [proposed] Let G = <P> of prime order N, Q = [k]P, and consider the abelian surface A = E x E with its product  | title=Tracked object: the split-quotient certificate. ECDLP is exactly the problem of 
  IDEA-20260829-70258e [proposed] (A) WHAT THE FAMILY ACTUALLY DOES. Kani-style embeddings need an auxiliary endomorphism of norm S =  | title=The Autolab p1243 auxiliary-discriminant Kani family tracks a polarization type,
  IDEA-20260901-2d3f07 [proposed] Let E/F_p be an ordinary curve, P a point of PRIME order N, G = <P>, and H any abelian group written | title=THE SELF-PAIRING HALF OF THE LANE IS CIRCULAR, BY A DIMENSION COUNT - on a cycli
  IDEA-20260913-449d2b [proposed] SCOPE. Semaev 2015 (KN-LIT-fa346d, frozen at inputs/SEMAEV-2015-310/) Assumption 1 ONLY. Nothing her | title=Four quantities, one name -- separate Semaev's d_F4 from the first fall degree, 
  IDEA-20260916-a17f43 [proposed] (A) THE SHAPE, AND WHY IT IS THE COMPLEMENT OF WHAT IS CLOSED. The bound of IDEA-20260916-5c9d6e (A) | title=THE SUCCESSOR OBJECT THE INJECTION BOUND LEAVES ROOM FOR: factor bases V_R = {x 
  IDEA-20260922-99294c [proposed] RQ-BINSTD-b6f698's own audit (analysis/binstd-curve-audit/) establishes that 131 (and every other m  | title=IS THE "FULLY DETERMINED" WEIL-DESCENT SHAPE BASIS-INVARIANT? n=131 prime forecl
  IDEA-20260926-5c26f9 [proposed] CEILING FIRST. This is a structural-emptiness certificate for one column of RQ-BINSTD-b6f698's table | title=THE DIMENSION-5 AND DIMENSION-6 WEIL-POLYNOMIAL CENSUS OVER F_2 FOR 131 DIVIDING
  IDEA-20260926-80209d [proposed] CEILING FIRST. A control fixture for RQ-BINSTD-b6f698's table (owner by the R2 rule); no arity, no o | title=THE TOY CONTROL LADDER FOR ALGEBRAIC-GROUP FACTOR BASES, at primes n in {17, 23,
  IDEA-20261002-8f26ce [proposed] The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve | title=Artin-Schreier curves of genus 5 and 6 over F_2 as the explicit-model column of 
  IDEA-20261002-cad44c [proposed] Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimens | title=Weil-cap arity ledger for a rational-point Couveignes factor base: at genus at m
  IDEA-20261006-237ce0 [proposed] Let E be y^2 = x^3 + 2x + 3. Let p be the smallest prime with p > 20 and p < 120 such that E is nons | title=The Weil pairing of one order-5 point with itself is 1 on y^2 = x^3 + 2x + 3
  IDEA-20261007-6c65b7 [proposed] Let E be y^2 = x^3 + x over F_73. If the discriminant is 0 the model is singular and the run is an i | title=Weil pairing of a point with its j=1728 image on y^2 = x^3 + x over F_73 is not 
  IDEA-20261007-ee2836 [proposed] Let E be y^2 = x^3 + 1 over F_19. If the discriminant is 0 the model is singular and the run is an i | title=Weil pairing of a point with itself on y^2 = x^3 + 1 over F_19 equals 1
### proposals.jsonl :: Couveignes :: 5 hits
  IDEA-20260813-a33bee [proposed] At log2(p) <= 32, test a Couveignes--Rostovtsev--Stolbunov ordinary class-group action after restric | title=Toy character-kernel ordinary class-group KEX with a certified-flat full-orbit g
  IDEA-20260901-dedcea [proposed] FOUR SEPARABLE CLAIMS. (A) THE MATCHED PAIR. Integer factorisation and prime-field discrete logarith | title=RUN THE CONTROL THE LITERATURE SET UP, AT A SIZE THIS PROGRAM CAN REACH. Matched
  IDEA-20261002-711e84 [proposed] On a genus-2 curve C/F_2 whose Jacobian has a rational point of order 19, the Couveignes fibre of tr | title=Mumford u-coefficient eliminant of a genus-2 Jacobian fibre over F_2, as the mem
  IDEA-20261002-cad44c [proposed] Any Couveignes factor base built from F_2-rational points of a commutative algebraic group of dimens | title=Weil-cap arity ledger for a rational-point Couveignes factor base: at genus at m
  IDEA-20261006-83c197 [proposed] Let n be the smallest prime that fails both dimension-1 conditions recorded in KN-OPEN-095df5 over F | title=Degree of one descended system from a dimension-2 quotient at the first prime th
### proposals.jsonl :: LMFDB :: 1 hits
  IDEA-20261009-791518 [proposed] With retrieved (LMFDB) equations for the minimal-conductor curves of rank 8 to 11, the growth slope  | title=Retrieve, not recall, the rank ladder: extend the small-point census to ranks 8-
### proposals.jsonl :: Weil-polynomial census :: 3 hits
  IDEA-20260926-5c26f9 [proposed] CEILING FIRST. This is a structural-emptiness certificate for one column of RQ-BINSTD-b6f698's table | title=THE DIMENSION-5 AND DIMENSION-6 WEIL-POLYNOMIAL CENSUS OVER F_2 FOR 131 DIVIDING
  IDEA-20260926-80209d [proposed] CEILING FIRST. A control fixture for RQ-BINSTD-b6f698's table (owner by the R2 rule); no arity, no o | title=THE TOY CONTROL LADDER FOR ALGEBRAIC-GROUP FACTOR BASES, at primes n in {17, 23,
  IDEA-20261005-1e54b5 [proposed] Let A be an abelian surface over F_2 in the isogeny class with Frobenius polynomial P(T) = T^4 + 3T^ | title=Field of definition of the etale 2-torsion on the order-19 abelian surface over 
### proposals.jsonl :: algebraic group AND Frobenius-stable :: 0 hits
### proposals.jsonl :: H-FROB / H-BINSTD ids :: 0 hits
### proposals.jsonl :: rational point of order 131 :: 1 hits
  IDEA-20261002-8f26ce [proposed] The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve | title=Artin-Schreier curves of genus 5 and 6 over F_2 as the explicit-model column of 
```

Additional index scan for g=6 follow-ups / Jacobian flags (terms IMP-H1|164937|has_jacobian|Jacobian-or-not|g=6 census|617 together with BINSTD|FROB|Weil|131), output verbatim:
```
H-CERTBIN-405f4d | approved | Degree 131 has 65 quadratic classes and 2795 cubic classes.
H-MLKEM-0c0a6e | proposed | 
H-QSP-411d8f | supported | Heuristic H1 of H-QSP-645a07, restated as a falsifiable claim on the engine-independent eliminant degree of th
H-QSP-645a07 | analyzed | 
IDEA-20260805-5a4409 | unverified | Parseval energy budget of the dual-FFT distinguisher: an exact conservation law that forces the across-candida
IDEA-20260918-6c07e1 | proposed | A FROBENIUS-ORBIT CONGRUENCE CLOSES THE F_2-COEFFICIENT QUASI-SUBFIELD SHAPE AT n = 131 FOR EVERY n' IN [2, 12
IDEA-20260922-818b73 | proposed | THE EXCHANGE RATE AGAINST RHO: gamma*(cell) = 2^(60.9 - floor_bits), the single scalar any ECC2K-130 relation-
IDEA-20260926-0d1d74 | proposed | ROOT-FINDING IN A SUBSPACE OR ORBIT-UNION FACTOR BASE BY MODULAR COMPOSITION: gcd(h, L_V) costs O(l deg(h)^2) 
IDEA-20260926-bbf2ed | proposed | THE TRACE-SPECTRUM FACTOR BASE AT n = 131: V_E = {x : Tr(x^e) = 0 for e in E}, E a set of 98 cyclotomic classe
IDEA-20260926-bc1cab | proposed | THE TWISTED-COEFFICIENT CENSUS AT n = 131: K-coefficient quasi-subfield lambda (n' = 33, deg <= 7), where the
```

Records opened in full (exact paths): ledger/hypotheses/H-FROB-ff99bf.yaml ; ledger/evidence/EV-BINSTD-2d41c3.yaml ; ledger/hypotheses/H-FROB-66d9ae.yaml (first 140 lines).
Index rows (not full records) printed for: H-FROB-ff99bf, H-BINSTD-944a66, H-BINSTD-6feaa2, H-FROB-f3d248, H-FROB-66d9ae, H-BINSTD-41d8b2, IDEA-20260926-5c26f9, IDEA-20260806-c5d183, IDEA-20260901-863e36.

### 8.4 LMFDB retrieval (this gate, 2026-10-24)
```
LMFDB MCP (read-only SQL), table av_fq_isog, queried 2026-10-24. Results verbatim as returned.

--- Q1 counts by g (q=2, g<=7) ---
SELECT g, COUNT(*) AS n_classes, SUM(CASE WHEN abvar_count % 131 = 0 THEN 1 ELSE 0 END) AS n_131, SUM(... AND is_simple ...) AS n_131_simple, SUM(... AND has_jacobian = 1 ...) AS n_131_jac1, SUM(... AND has_jacobian = -1 ...) AS n_131_jacm1, SUM(... AND has_jacobian = 0 ...) AS n_131_jac0, SUM(... AND has_jacobian IS NULL ...) AS n_131_jacnull FROM av_fq_isog WHERE q = 2 AND g <= 7 GROUP BY g ORDER BY g
{"columns": ["g","n_classes","n_131","n_131_simple","n_131_jac1","n_131_jacm1","n_131_jac0","n_131_jacnull"], "row_count": 6, "rows": [
 {"g":1,"n_classes":5,"n_131":0,"n_131_simple":0,"n_131_jac1":0,"n_131_jacm1":0,"n_131_jac0":0,"n_131_jacnull":0},
 {"g":2,"n_classes":35,"n_131":0,"n_131_simple":0,"n_131_jac1":0,"n_131_jacm1":0,"n_131_jac0":0,"n_131_jacnull":0},
 {"g":3,"n_classes":215,"n_131":0,"n_131_simple":0,"n_131_jac1":0,"n_131_jacm1":0,"n_131_jac0":0,"n_131_jacnull":0},
 {"g":4,"n_classes":1645,"n_131":0,"n_131_simple":0,"n_131_jac1":0,"n_131_jacm1":0,"n_131_jac0":0,"n_131_jacnull":0},
 {"g":5,"n_classes":14325,"n_131":24,"n_131_simple":24,"n_131_jac1":11,"n_131_jacm1":13,"n_131_jac0":0,"n_131_jacnull":0},
 {"g":6,"n_classes":164937,"n_131":617,"n_131_simple":497,"n_131_jac1":173,"n_131_jacm1":444,"n_131_jac0":0,"n_131_jacnull":0}]}
(no g=7 rows: the q=2 table stops at g=6)

--- Q2 the 24 g=5 hits ---
SELECT label, abvar_count, has_jacobian, jacobian_count, hyp_count, is_cyclic, group_structure_count, is_simple, array_length(curves,1) AS ncurves, poly_str FROM av_fq_isog WHERE q = 2 AND g = 5 AND abvar_count % 131 = 0 ORDER BY has_jacobian DESC, label
label | abvar_count | has_jacobian | jacobian_count | hyp_count | is_cyclic | group_structure_count | is_simple | ncurves | poly_str (L-polynomial coefficients a_0..a_10)
5.2.b_d_e_h_n | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 1 3 4 7 13 14 16 24 16 32
5.2.b_d_e_i_k | 131 | 1 | 3 | 0 | true | 1 | true | 3 | 1 1 3 4 8 10 16 16 24 16 32
5.2.b_d_e_j_h | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 1 3 4 9 7 18 16 24 16 32
5.2.b_e_c_k_f | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 1 4 2 10 5 20 8 32 16 32
5.2.c_c_d_h_k | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 2 2 3 7 10 14 12 16 32 32
5.2.c_c_f_g_d | 131 | 1 | 2 | 0 | true | 1 | true | 2 | 1 2 2 5 6 3 12 20 16 32 32
5.2.c_d_c_g_j | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 2 3 2 6 9 12 8 24 32 32
5.2.c_d_d_f_h | 131 | 1 | 2 | 0 | true | 1 | true | 2 | 1 2 3 3 5 7 10 12 24 32 32
5.2.c_d_e_e_f | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 2 3 4 4 5 8 16 24 32 32
5.2.c_e_e_c_c | 131 | 1 | 1 | 0 | true | 1 | true | 1 | 1 2 4 4 2 2 4 16 32 32 32
5.2.d_g_l_q_v | 262 | 1 | 1 | 0 | true | 1 | true | 1 | 1 3 6 11 16 21 32 44 48 48 32
5.2.a_f_b_p_d | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 0 5 1 15 3 30 4 40 0 32
5.2.b_c_g_i_j | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 1 2 6 8 9 16 24 16 16 32
5.2.b_d_d_k_j | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 1 3 3 10 9 20 12 24 16 32
5.2.b_d_f_f_o | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 1 3 5 5 14 10 20 24 16 32
5.2.b_d_f_g_l | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 1 3 5 6 11 12 20 24 16 32
5.2.b_e_d_i_g | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 1 4 3 8 6 16 12 32 16 32
5.2.c_c_c_h_p | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 2 2 2 7 15 14 8 16 32 32
5.2.c_e_d_e_b | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 2 4 3 4 1 8 12 32 32 32
5.2.c_f_d_d_af | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 2 5 3 3 -5 6 12 40 32 32
5.2.c_g_l_t_bd | 262 | -1 | 0 | 0 | true | 1 | true | 1 | 1 2 6 11 19 29 38 44 48 32 32
5.2.d_e_d_a_ae | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 3 4 3 0 -4 0 12 32 48 32
5.2.d_f_e_ad_aj | 131 | -1 | 0 | 0 | true | 1 | true | 1 | 1 3 5 4 -3 -9 -6 16 40 48 32
5.2.d_g_k_q_ba | 262 | -1 | 0 | 0 | true | 1 | true | 1 | 1 3 6 10 16 26 32 40 48 48 32
(24 rows)

--- Q3 point-count spectrum of the hits ---
SELECT g, abvar_count, COUNT(*) AS n, SUM(CASE WHEN has_jacobian=1 THEN 1 ELSE 0 END) AS jac1 FROM av_fq_isog WHERE q = 2 AND g IN (5,6) AND abvar_count % 131 = 0 GROUP BY g, abvar_count ORDER BY g, abvar_count
g=5: 131 -> n=21 jac1=10 ; 262 -> n=3 jac1=1
g=6: 131 -> 375/87 ; 262 -> 106/40 ; 393 -> 51/22 ; 524 -> 37/12 ; 655 -> 26/5 ; 786 -> 11/3 ; 917 -> 2/1 ; 1048 -> 4/1 ; 1179 -> 1/0 ; 1310 -> 3/1 ; 1441 -> 1/1

--- Q4 curves column for the 11 g=5 hits with has_jacobian = 1 (plane-model equations pasted as returned; the multi-equation P^4 complete-intersection models are SUMMARISED here, not pasted) ---
5.2.b_d_e_h_n [131]: x^5 + x^4*z + x^3*z^2 + x^2*y^3 + x*y^3*z + x*y*z^3 + y^4*z
5.2.b_d_e_i_k [131]: x^5 + x^3*z^2 + x^2*y*z^2 + x*y^4 + y^4*z + y^3*z^2 + y^2*z^3 ; (2 further complete-intersection models in P^4)
5.2.b_d_e_j_h [131]: x^5 + x^4*y + x^3*y*z + x^3*z^2 + x^2*y^3 + x^2*y^2*z + x*y^3*z + x*y*z^3 + y^5 + y^3*z^2 + y^2*z^3
5.2.b_e_c_k_f [131]: one complete-intersection model in P^4 (three equations in x,y,z,t,u)
5.2.c_c_d_h_k [131]: x^4*y + x^3*y*z + x^2*y^2*z + x^2*y*z^2 + x^2*z^3 + x*y^4 + x*y^3*z + x*y*z^3 + y^5 + y^3*z^2
5.2.c_c_f_g_d [131]: 2 plane quintic models
5.2.c_d_c_g_j [131]: one complete-intersection model in P^4
5.2.c_d_d_f_h [131]: 1 plane model + 1 complete-intersection model in P^4
5.2.c_d_e_e_f [131]: x^5 + x^4*y + x^3*y^2 + x^3*y*z + x^2*y^2*z + x^2*y*z^2 + x^2*z^3 + x*y^3*z + x*y*z^3 + y^5
5.2.c_e_e_c_c [131]: one complete-intersection model in P^4
5.2.d_g_l_q_v [262]: x^4*z + x^3*y*z + x^3*z^2 + x^2*y^2*z + x*y^4 + x*y^3*z + y^5 + y^2*z^3
(P^4 models summarised; none of the equations was independently checked for smoothness or genus by this gate)

--- Q5 hyp_count / g=6 aggregate for hits ---
SELECT COUNT(*) AS n131, SUM(has_jacobian=1) AS jac1, SUM(hyp_count>0) AS hyp_pos, SUM(hyp_count IS NULL) AS hyp_null, SUM(abvar_count=131 AND has_jacobian=1) AS jac1_exactly131, SUM(is_cyclic) AS cyc FROM av_fq_isog WHERE q=2 AND g=6 AND abvar_count % 131 = 0
{"n131": 617, "jac1": 173, "hyp_pos": 8, "hyp_null": 0, "jac1_exactly131": 87, "cyc": 602}

--- Q6 has_jacobian value domain, g in (4,5,6) ---
{"g":4,"n_total":1645,"jac1":620,"jacm1":1025,"jac0":0,"jacnull":0}
{"g":5,"n_total":14325,"jac1":4339,"jacm1":9986,"jac0":0,"jacnull":0}
{"g":6,"n_total":164937,"jac1":38327,"jacm1":126610,"jac0":0,"jacnull":0}

--- Q7 consistency of jacobian_count / hyp_count ---
{"g":4,"n":1645,"hyp_null":0,"hyp_pos":217,"jc_null":0,"jc_pos":620,"jac1_but_count0":0}
{"g":5,"n":14325,"hyp_null":0,"hyp_pos":841,"jc_null":0,"jc_pos":4339,"jac1_but_count0":0}
{"g":6,"n":164937,"hyp_null":0,"hyp_pos":3341,"jc_null":0,"jc_pos":38327,"jac1_but_count0":0}

--- WebFetch https://www.lmfdb.org/Variety/Abelian/Fq/5/2/b_d_e_h_n (retrieved 2026-10-24) ---
L-polynomial: 1 + x + 3x^2 + 4x^3 + 7x^4 + 13x^5 + 14x^6 + 16x^7 + 24x^8 + 16x^9 + 32x^10
Number of points over F_2 (abvar_count): 131
Simple: yes ("simple and geometrically simple")
Contains a Jacobian: yes, of one curve, stated to be non-hyperelliptic; listed equation x^5 + x^4 z + x^3 z^2 + x^2 y^3 + x y^3 z + x y z^3 + y^4 z = 0
```

### 8.5 Numerical re-check script output (raw/check_hits.py; float, not rigorous)
```
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.66e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.00e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.33e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.00e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.55e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.55e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.66e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=8.88e-16  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=4.44e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=8.88e-16  weil_numeric=True
L(1)= 262  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.11e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=3.33e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.78e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.00e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.11e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.33e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.33e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.00e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.44e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.89e-15  weil_numeric=True
L(1)= 262  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=2.00e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.55e-15  weil_numeric=True
L(1)= 131  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=3.33e-15  weil_numeric=True
L(1)= 262  131|L(1)=True  funct.eq=True  max|mod-sqrt2|=1.11e-15  weil_numeric=True
ALL OK: 24 / 24 (numerical float check, NOT a rigorous Sturm test)
g5 |A|=131: least m with N^m >= 2^131 is 19; Semaev degree 2^(m-2)=2^17
g5 |A|=262: least m with N^m >= 2^131 is 17; Semaev degree 2^(m-2)=2^15
g6 max |A|=1441: least m with N^m >= 2^131 is 13; Semaev degree 2^(m-2)=2^11
H-FROB-66d9ae g5 ceiling 6725: least m with N^m >= 2^131 is 11; Semaev degree 2^(m-2)=2^9
H-FROB-66d9ae g6 ceiling 39201: least m with N^m >= 2^131 is 9; Semaev degree 2^(m-2)=2^7
```

### 8.6 Reading (b) arithmetic, |F| = 131 * #A(F_2) (second python call, output verbatim; derived, see section 6)
```
n*131 17161 14.07 m= 10 Semaev deg 2^(m-2)=2^8
n*262 34322 15.07 m= 9 Semaev deg 2^(m-2)=2^7
n*1441 188771 17.53 m= 8 Semaev deg 2^(m-2)=2^6
n*6725 880975 19.75 m= 7 Semaev deg 2^(m-2)=2^5
n*39201 5135331 22.29 m= 6 Semaev deg 2^(m-2)=2^4
```
(The 8.5 output above is reading (a), |F| <= #A(F_2), and reproduces H-FROB-66d9ae's own m* = 11 / 9.)
