# Novelty gate N1-N4: C3 (binary) block-multilinear (multigraded) truncated closure for chained descended S_3 cells

Candidate field_key: commutative algebra. Date of gate: 2026-10-24. Read-only inputs; nothing inside the repositories was edited, created, added or committed. Everything below was written under `.../scratchpad/scout/`.

## VERDICT: advances_lead (lead = LEAD-ICE-descent-closure-degree-at-scale, open_blocked)

C3 is a sharper, memory-feasible variant of the open lead's own blocked next step (the lead's `next_action.step` says "on a host with >= 250 GB RAM (or a sparse closure)"; `dreg_closure_m4l6_20261018/RESULTS.md` says "Q3 needs a host above about 250 GB, or a sparser closure"). It is not `new`, for three reasons that the candidate text does not carry:

1. The exact monomial restriction (cap the number of internal-node (u) bits per monomial, drop a product as a whole when any monomial leaves the column set, so every row stays in the ideal) was already built and run at toy scale in `analysis/ecdlp2m-iteration-20261009/leads-pilot4/` (`myclosure4.c`, kind `cap`, variants `fullu2`, `fullu3`, `L1u2`, `L2u2`, `L2u3`). I reproduced its column counts with the candidate's own counting formula, digit for digit: (x bits, u bits, cap, D) = (9,9,2,4) -> 3,082; (12,11,2,4) -> 8,428; (9,9,3,4) -> 3,922; (12,11,3,4) -> 10,573, which are the pilot's `fullu2`/`fullu3` column counts for m = 3, (n,k) = (9,3), (11,4). It is an exploratory pilot ("Not program evidence"), it is not cited by any atlas lead row, and its own ranked-lead row 6 reads "Not a lead: u-bit caps (result 2) ... closed at m >= 5 for the toy cells measured". So the atlas does not show this collision; the repository does.
2. The "derived fact" that every chain equation is multi-affine in the blocks (c_1, c_2, c_3, u), affine in u, is already recorded: `crypto:research/pdp_literature_leads_20261022/leads/LEAD-01.md` section 1, "What survives descent", item 1 (toy desk check at n = 11, l = 3: f_1 has block profile (c_1,c_2,u) = (1,1,1), f_2 has (c_3,u) = (1,1)). The same note (section 8) says "Field equations break the multigrading, so applicability is unclear."
3. The B4 writability escape does not work as stated (N1, collision 3 below), and the (3,7) cell is an m = 3 cell, whose ECC2K-130 row is above rho "even with a free oracle" (`crypto:research/notes/ecc2k130/RESEARCH_ECC2K130_DESCENT_DEGREE.md` lines 43-44: 2^68.58 against 2^60.81, re-read this session), so the cell's only row-relevant use is as a proxy for the m = 4 degree bracket (+7.62 / +10.32 bits), as the candidate itself says (board gain 0).

What is not covered anywhere that I could find: the truncated closure at D = 5 on the (3,19,7) cell (the lead's blocked C1 cell), and the u <= 1 cap at any m. That is an operational gap, not a new object.

## Citation provenance (what I actually retrieved)

- Faugere, Safey El Din, Spaenlehauer, arXiv 1001.4004 (JSC 2011). **retrieved**: abstract via WebFetch of arxiv.org/abs/1001.4004, and the theorem text via the arXiv PDF (WebFetch saved the PDF; `pdftotext` on it). Theorem 6.1 (section 6.4, p. 25): "If the system F is generic, then the degree of regularity of theta(I) is upper bounded by d_reg <= min(n_x + 1, n_y + 1)." Hypotheses as written: affine bilinear system with m = n_x + n_y equations in n_x + n_y variables, "the characteristic of k is 0 (although the results remain true when the characteristic is large enough)". The candidate's "recalled" min(n_x,n_y)+1 bound is therefore upgraded to retrieved; the hypotheses (generic, square, bilinear, characteristic 0 or large, no field equations) are NOT those of the Boolean chained S_3 system. LEAD-01 section 1 reads it as min(3l, n)+1 = 16 at (15,5), 20 at (19,7), 132 at (131,44), "4x to 33x above measured F4": the bound says nothing about D = 5 at (3,19,7). The candidate's mechanism does not rely on it, so it is context only.
- Bender, Faugere, Tsigaridas, "Towards Mixed Gröbner Basis Algorithms: the Multihomogeneous and Sparse Case", arXiv 1805.03577, ISSAC 2018. **retrieved** (abstract via WebFetch): mixed, square, zero-dimensional multihomogeneous systems; explicit degree bound. Same hypothesis gap (square, zero-dimensional, homogeneous). Ning-Ran-Samardjiska "Multi-homogeneous XL" (ePrint 2025/2060): **recalled** (the repo's LEAD-01 lists it abstract-only; I did not fetch it).
- Repository facts quoted below were read this session from the files named.

## N1 Atlas collision

Raw outputs are pasted in the appendix (runs 1-4 are the three `match_phrasings` plus one of my own; runs X1-X3 are extra probes). The tool prints the top 8 hits per run; I read the lead YAML (mechanism, obstruction, next_action, forecloses) of every top-5 lead hit of every run (the union is 11 leads), LEAD-ICE-syzygy-cascade-signatures (rank 8 of run 1), and LEAD-ICE-hybrid-guess-determine-l7 and LEAD-ICE-sat-xor-pdp-oracle from the candidate text. KR rows in the lists were read in KRMAP.md.

Top-5 per run (score, id, disposition):
- Run 1 (phrasing 1): 11 LEAD-ICE-descent-closure-degree-at-scale (open_blocked); 8 LEAD-ICE-boolean-f4-f5-f6-engines (closed_dominated); 7 KR-IC-fbdb61; 7 LEAD-ICE-chained-semaev-dreg-vs-semiregular (open_next_step); 7 LEAD-ICP-icperf-writability-boundary (closed_obstructed).
- Run 2 (phrasing 2): 19 LEAD-ICE-descent-closure-degree-at-scale; 16 LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked); 11 KR-IC-889857; 11 LEAD-ICE-prime-field-semaev-solving-degree (closed_known); 10 LEAD-ICE-curve-presentation-invariance (open_next_step).
- Run 3 (phrasing 3): 35 LEAD-ICP-icperf-writability-boundary; 18 LEAD-ICE-chained-semaev-dreg-vs-semiregular; 10 LEAD-ICB-decomposition-encoding-and-sat (closed_obstructed); 10 LEAD-ICE-semaev-chain-cost-model (closed_obstructed); 10 LEAD-ICP-digit-presentation-solving-degree (open_next_step).
- Run 4 (own phrasing: multidegree truncated Macaulay closure mutants degree in internal node variables bihomogeneous Hilbert series descended Semaev): 22 LEAD-ICE-chained-semaev-dreg-vs-semiregular; 15 LEAD-ICE-descent-closure-degree-at-scale; 13 LEAD-ICB-prime-degree-algebraic-decomposition; 13 LEAD-ICP-digit-presentation-solving-degree; 10 LEAD-ICE-first-fall-degree-assumptions (open_blocked).

Hit-by-hit reading (mechanism + obstruction + forecloses):

1. **LEAD-ICE-descent-closure-degree-at-scale (open_blocked). Same cell, same question. advances_lead.** Mechanism: MutantXL/F4 closure degree of descended S_3/S_4 chains vs l and n; "the degree rises at l = 7 at m = 3". Next action: run the frozen C1 cell (m,n,l) = (3,19,7) at degree 5 "on a host with >= 250 GB RAM (or a sparse closure)", then (4,7). blocked_by: "memory (C1 capped at 169 GB of 184 GB; projection 217 GB)". No obstruction block (open lead). Forecloses: "solving degree of Weil descent stays 4", "first fall degree assumption makes binary ECDLP subexponential", "MutantXL closure degree on summation polynomial systems", "degree-capped certified decomposition", "arity axis of bounded-degree refutation". None of these phrases covers a u-degree-restricted closure at D = 5; the lead itself invites "a sparse closure". C3 is exactly one such sparse closure, so it is inside the lead, not past it.
2. **LEAD-ICE-hybrid-guess-determine-l7 (open_next_step). Measured alternative unblock of the same cell.** Registered result (`crypto:research/dreg_hybrid_guess_20261024/RESULTS.md`, read in full): on 10 of 10 UNSAT (3,7) draws all 2^k branches refute at degree 4 with k* <= 2, at 2.7-6.2 GB RSS, at 1/116 to 1/260 of the projected degree-5 closure (e = 3); unspecialised degree 4 "saturates without refuting on all 10 draws". The m = 4 row stays >= +7.62 and is +8.43 (S_const) or +30.7 to +58.3 (S_lin); what separates them is stretch cell E8 (3,22,8), which did not run. C3 does not run E8. So C3 would add the unspecialised degree-5 reading at (3,7) that the hybrid bypassed; it does not touch the open discriminator of that lead. Forecloses of this lead ("hybrid guess and determine descent", "fix one variable then Groebner", "specialisation lowers closure degree") are not claimed by C3.
3. **LEAD-ICP-icperf-writability-boundary (closed_obstructed). The candidate's B4 escape premise does not hold.** Obstruction (kind cost_model), quoted: "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]." revisit_when: "n >= 409, or a representation (e.g. chained S_3 at m = 5, 6, ~2^31-2^33 monomials) whose written size plus solve fits under the rho budget with memory charged." The candidate says it escapes "unchained descended ANF" because a chained S_3 is block-multilinear with O(l^2 n) terms. But (a) every closure and hybrid cell in the program is already chained S_3, and the lead already names chained S_3 as the representation whose written size plus solve must fit under the rho budget; C3 supplies no new written-size or solve-cost number, only a smaller Macaulay column count at toy-adjacent cells; (b) the lead's forecloses include "chained Semaev system at m = 5 or 6 on ECC2K-130" and "memory column for block Wiedemann at the cap locus", which is the same Macaulay-memory column; (c) a u-degree cap changes columns by a bounded factor (candidate's own numbers: 3.0x memory at the (3,7) D = 5 cell), and the writability gap at ECC2K-130 is +40.8 bits. Conclusion: the B4 claim should be dropped, not escaped.
4. **LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked).** The pipeline lead for "the only non-generic oracle on binary curves". The candidate's SO-TABLE/SO-GEN "escape" (algebraic oracle) is this lead's own premise (`LEAD-ICB-generic-table-oracle` revisit_when points to it). Evidence list already contains `block-local-closure-pilot` ("locality-2 closure refutes m = 5, |V| = 8 (5/5)"), i.e. restricted-support closures are an existing line. Forecloses: "mutant or degree-4 closure as a sub-rho decomposition oracle", "solving degree stays bounded for Weil descent at m = 4 on ECC2K-130". C3 does not claim to avoid these; it claims a memory constant.
5. **LEAD-ICE-boolean-f4-f5-f6-engines (closed_dominated).** Obstruction (measured): dominated by LEAD-ICE-rootfind-pairtable-oracle on n <= 31, m in {2,3,4}; revisit_when: "A descended cell where the pair table is infeasible (m >= 4 at large n) and the algebraic degree stays bounded (LEAD-ICE-descent-closure-degree-at-scale)". C3 is a restricted-support closure, not an engine speedup, so it is not this lead's mechanism, but it lives under that revisit clause: any cost claim depends on the degree question C3 is meant to feed.
6. **LEAD-ICE-chained-semaev-dreg-vs-semiregular (open_next_step).** Shares the same block structure (`IDEA-20260828-d91efa`: chained t = 3 system as I_A on (U,X3) and I_B on (U,X1,X2) sharing only U) but asks whether d_reg departs from a semi-regular null, via exact Macaulay ranks. Not the same mechanism. A truncated closure would be an instrument there (the lead's n = 15 D = 6 runs failed at 11.7-12.2 GiB), not a duplicate.
7. **LEAD-ICB-decomposition-encoding-and-sat (closed_obstructed).** Obstruction (measured): SAT and enumeration arms have per-attempt UNSAT cost 2^(alpha l), alpha ~ m, versus alpha < m/2 - 1 needed; "closure outcomes are basis-invariant (Proposition B)". Forecloses "direct S_4 instead of chained S_3". Not C3's mechanism; C3's candidate text itself notes unchained S_4 is not block-multilinear.
8. Read and not the same mechanism: LEAD-ICE-semaev-chain-cost-model (closed_obstructed; obstruction: t* = m* under Semaev's cost model and N invariant over merge topologies; revisit only if a solver's degree depends on topology), LEAD-ICE-first-fall-degree-assumptions (open_blocked; Lean bridge on the S_3 degree-2 fall), LEAD-ICE-prime-field-semaev-solving-degree (closed_known; prime field, beta_work 0.797 / 0.647 vs 0.30; forecloses prime-field Groebner solving-degree laws, not binary closures), LEAD-ICP-digit-presentation-solving-degree (open_next_step; prime-field digit presentation), LEAD-ICE-curve-presentation-invariance (open_next_step; isogeny and model transport), LEAD-ICE-syzygy-cascade-signatures (open_next_step; F5 signature cascade). Their forecloses phrases do not mention a degree-filtered or memory-reduced closure.
9. LEAD-ICE-sat-xor-pdp-oracle (B4 lead named in the candidate): SAT/XOR enumeration pricing, open_next_step; C3 does not touch SAT conflicts. No collision.

Standing obstructions, quoted with Scope:
- SO-TABLE binary, LEAD-ICB-generic-table-oracle (closed_obstructed, theorem): "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply ... Scope: all binary and Koblitz curves, one target, setup charged." revisit_when: "An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition". C3 is a solver-side constant inside that non-generic oracle; it does not change which side of the obstruction the oracle is on.
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed, theorem): "any generic algorithm needs Omega(sqrt r) group operations ... Scope: all generic algorithms, any field, any r." revisit_when: "only a method that reads the representation (index calculus, transfer) can change the exponent." C3 reads the representation but claims no exponent.
- Writability (above).

What C3 does that the forecloses phrases do not cover (the only thing): a closure-semantics-preserving column restriction by internal-node degree evaluated at D = 5 on (3,19,7). It is a memory instrument for an open measurement, with the repository's own pilot already in the neighbourhood (next section).

### Same-mechanism prior art that the atlas does not show

`analysis/ecdlp2m-iteration-20261009/leads-pilot4/` (README.md, PREDICTIONS.md, aggregate.md, myclosure4.c; exploratory, "No contract, no run record, no ledger write"). Read this session.

- Object and rule identical to C3: chained S_3, t = m; `myclosure4.c` adds "a u-degree cap on the allowed monomials" to `myclosure_local.c`, whose rule is "a product x_j * g is dropped as a whole whenever any of its monomials falls outside the column set. Nothing is ever truncated term-wise, so every row ... is a genuine element of the ideal" (pilot #3 README). That is C3's "keep closure semantics".
- D = 4 results (UNSAT refuted / SAT false refutations; columns vs full W_4):

| cell (m; n,k) | variant | columns (full) | UNSAT refuted | SAT false |
|---|---|---|---|---|
| 3; 9,3 | fullu2 | 3,082 (4,048) | 20/20 | 0/8 |
| 3; 11,4 | fullu2 | 8,428 (10,903) | 10/10 | 0/5 |
| 4; 7,2 | fullu2 | 4,832 (9,109) | 25/25 | 0/4 |
| 4; 7,2 | L2u2 | 3,450 | 25/25 | 0/4 |
| 4; 9,3 | L2u2 | 12,590 (31,931) | 0/10 | 0/4 |
| 4; 9,3 | L2u3 | 23,198 | 10/10 | 0/4 |
| 4; 9,3 | L1u2 | 2,690 | 0/10 | 0/4 |
| 4; 11,3 | L1u2 | 3,877 | 0/10 | 0/2 |
| 5; 9,3 | L2u2 / L2u3 | 20,280 / 48,099 | 0/5 / 0/5 | 0/3 |

  Pilot summary row: "smallest u-bit cap that refutes": <= 2 (m = 3), 2 (m = 4, n = 7), 3 (m = 4, n = 9), "4 = no cap" (m = 5). Its stated conclusion: "A u-bit cap gives nothing on top of locality from m = 5 on. At m = 5 the refutation already uses monomials of full degree 4 in the u-bits." Pre-registered P-M6 (locality 2, m = 6) refuted only 1/5.
- Consequences for C3's stated hypotheses (my reading, labelled as such):
  - Supports the m = 3 leg: u <= 2 preserved 30/30 degree-4 refutations at m = 3 toy cells (n <= 11), at 76-77% of the columns. u <= 1 was never run at any m.
  - Goes against H3-b for the proposed calibration cell: at m = 4 the cap needed rose from 2 (n = 7) to 3 (n = 9). `L2u2` at (4,9,3) refutes 0/10, but `fullu2` (no locality restriction, a superset) was not run there, so H3-b is not settled by this data. PREDICTION (extrapolation from three cells, low confidence): u <= 2 is more likely to lose than to keep the (4,15,6) refutations. The candidate's own kill rule ("Truncation loses the (4,6) refutations: C3 is killed") already covers that outcome.
  - Column counts: at toy cells the cap saves 23-24% of columns; the candidate's 42% (3.0x memory) at (3,19,7) D = 5 is arithmetic I re-derived exactly (see "Arithmetic check"), but is not a measured saving.
- Neighbouring record: pilot #3 (`block-local-closure-pilot`): locality restrictions L1/L2 on the same closure, with the same whole-product dropping; L1 loses refutations at m = 4, n = 9 (9/10) and m = 5 (0/10); L2 keeps m = 5 (5/5). Cited by LEAD-ICB-prime-degree-algebraic-decomposition.

Arithmetic check (re-derived, not measured): (3,19,7): N = 21 x-bits + 19 u-bits = 40; D = 5 full C(40,<=5) = 760,099 (216.7 GB by 3*cols^2/8, matches RESULTS "projection 217 GB"); u <= 2: 438,391 (72.1 GB); u <= 1: 171,289 (11.0 GB). (4,15,6): N = 24 + 30 = 54; D = 4 full 342,541 (RESULTS reports 342,537 columns, 44 GB projected, 25.8 GB measured); u <= 2: 213,636 (17.1 GB); u <= 1: 82,701 (2.6 GB). All of the candidate's column and GB figures reproduce.

### N1 verdict

advances_lead. The nearest thing to a duplicate is the pilot #4 `cap` arm, which is not an atlas lead and was closed there only for toy cells; it is evidence the curator should attach to LEAD-ICE-descent-closure-degree-at-scale before C3 is ranked (I did not edit anything). Not `duplicate_of_lead` because the lead is open, names a sparse closure as an allowed step, and the D = 5 (3,19,7) application is unmeasured.

## N2 Known results

Raw outputs of `build_frontier_map.py --match` for the three phrasings, my own phrasing, and one extra probe are pasted in the appendix.

- Hits: KR-IC-fbdb61 (known_bound/proven, "Last fall degree and solving degree of Weil descent systems": last fall degree bounded under stated conditions; "Semi-regular (Bardet-Faugere-Salvy) predictions do not describe descended summation systems"), KR-IC-e847d1 (Crossbred: Macaulay preprocessing plus exhaustive search), KR-IC-0d2021 (modern Groebner refinements), KR-IC-f3da82 (F4 trace reuse), KR-IC-889857 (disputed: subexponential binary ECDLP under first-fall assumption), KR-IC-1fcdbc (known_negative/measured: char-2 summation algorithms far slower than rho), KR-IC-955fd6, KR-IC-f5c584.
- None records a multigraded or u-degree-truncated closure, the Faugere-Safey El Din-Spaenlehauer bilinear bound, or Bender-Faugere-Tsigaridas. A lexical miss proves nothing, so I checked the semantics: KR-IC-fbdb61 and KR-IC-889857 concern the degree question that C3 only measures; they are the context for the lead, not for C3's mechanism. KR-IC-e847d1 (hybrid Macaulay plus enumeration) is the known relative of the hybrid guess lead, not of C3.
- External literature: multihomogeneous and bilinear Groebner theory exists (FSS 2011, BFT 2018, retrieved above) but its theorems need exact (multi)homogeneity, square zero-dimensional input and characteristic 0 or large; the Boolean ring's field equations x^2 = x are inhomogeneous in every grading, so the Macaulay matrix is filtered by u-degree, not block-diagonal. No published result that I know of gives a degree or memory theorem for u-degree-filtered Macaulay closures of Boolean Weil-descended Semaev systems, and I make no claim that none exists (search by two repository notes, LEAD-01 and LEAD-14, found none).

N2 verdict: no KR hit is the same mechanism; no `known_result`. The literature supplies motivation (block structure) and no usable bound.

## N3 Ledger

Greps (python, case-insensitive substring over whole index lines) on `proposals.jsonl` and `hypotheses.jsonl`; raw hit lists are in the appendix. Terms: multigraded, multihomogeneous, multi-homogeneous, bihomogeneous, bilinear, multilinear, truncated macaulay, truncat, internal node, per-block, mixed degree, block-local, sparse closure, u-degree, block degree, weighted degree, multidegree.

Hits that may be the same object (id | status | 100 chars of claim):
- IDEA-20260808-ec2128 | proposed | "PRECISELY WHICH SYSTEMS ARE BIGRADED ... (A) The k-tuple intersection system ... IS multi-homogeneous" (UOV, not ECDLP; opened in full).
- IDEA-20260916-e6540d | proposed | "(A) THE RESTRUCTURING. Semaev's characteristic-2 index calculus ... costs stage 1 at about m! * 2^{n/m} ..." (DEGREE-CAPPED CERTIFIED DECOMPOSITION; opened in full; it is a ledger_ref of the open lead).
- IDEA-20260828-d91efa | proposed | "The full system's freeze degree / column-count sequence ... predicted ... by H_full(t) =? H_A(t)*H_B(t)/H_{k[U]}(t)" (amalgam over the shared U block; opened in full).
- H-PFDR-f7161e | proposed | "(A) THE OBJECT. In the boolean chained Semaev system at t = 3 over GF(2), IDEA-20260828-d91efa asserts a block decomposition ..." (index row only).
- IDEA-20261016-7a138a | proposed | "Nagao's chain passes information from R through m-2 n-bit variables U_i. A transfer-matrix variant keeps after link i only a degree-<=d description M_i ..." (cut-describability gate; index row only).
- IDEA-20260828-770aa4 | proposed | "The 11.73-12.22 GiB peak RSS measured ... during the n=15 D=6 Macaulay prepare phase ..." (streaming builder for the dreg lead; index row only).
- IDEA-20261018-1aff90 | proposed | "A GF(2) block Wiedemann (Coppersmith) consistency test on the sparse Macaulay matrix decides, for the (4,6) cell at degree 5 ..." (the adjacent record named in the candidate; it loses closure semantics; index row only).
- IDEA-20260731-009 | unverified | "The first-fall degree d_ff and Macaulay-bound degree d_reg of Semaev-shaped multihomogeneous systems at parameter sizes ... estimated by sampling random systems" (index row only).
- IDEA-20260903-cf63ad / H-PFDR-9aadc0 / H-PFDR-c88f14 (prime-field digit twin; "multilinear" in the claim; different field), H-DREG-44d4b8 (trace-multiplier identity on a toy S_3; the word 'bilinear' only), H-MGD-001 (Cummings-Hauenstein multigraded dual space, generic prime ECDLP): not the same object.

Opened (3, as allowed): IDEA-20260808-ec2128, IDEA-20260916-e6540d, IDEA-20260828-d91efa.
- ec2128: derives exact multigrading and block-diagonalisation of the Macaulay matrix for a UOV system, with the FSS bilinear results "RECALLED ... deliberately not used". Its own caveat is the one that bites C3: "Standard F4/F5 with degrevlex does not respect the grading". Different object (multivariate signature scheme, exactly homogeneous system, no Boolean ring). It does show the program already has a record of the multigraded-Macaulay idea in another family; it is not C3.
- e6540d: caps the total Macaulay degree at D_0 with a three-way verdict; the truncation is by total degree, the matrix is dense; no multidegree filtration, no memory column. Its pair is the same R1-class truncated Macaulay presentation C3 uses (see N4).
- d91efa: Hilbert-series factorisation over the shared U-block as a predictor of rank deficits at n = 9, 12; no truncation of the closure, no memory reduction beyond predicting without gluing.

No ledger proposal or hypothesis records a u-degree (or block-degree) restricted closure. The same-mechanism artefact is non-ledger: `analysis/.../leads-pilot4` and `.../block-local-closure-pilot` (N1).

N3 verdict: no ledger duplicate; nearest are ec2128 (other family, same grading idea), e6540d (total-degree cap), d91efa/H-PFDR-f7161e (block decomposition predictor), 7a138a (cut at the internal nodes).

## N4 Notation change

The candidate is an instrument over an existing representation, not a new IC object, but the gate is run because it states a pair.
- Pair: (R3 = Weil restriction to F_2 of x_i in an F_2-subspace V (l bits per x block) plus chained internal nodes u in F_{2^n} (n bits each), Sigma = translation by factor-base elements (the S_3 chain composition) together with the Macaulay step set restricted to the u-degree filtration: multiplication by Boolean monomials staying in the column set, F_2-linear combination). Tracked object: the row space of the filtered Macaulay matrix, a subspace of the degree-D closure, projected to the verdict {refuted, not refuted}.
- This is the same pair as `IDEA-20260916-e6540d` ("R1-class representation ... truncated Macaulay presentation", Class I partial-action) with a finer truncation; no new arithmetic and no new factor base (V is the existing degree-1-membership F_2-subspace).
- Not a recorded rigidity result in new notation:
  - IDEA-20260806-c5d183 (no lossy object propagates deterministically under the FULL translation action): C3's Sigma is the partial action (translation by factor-base elements only) and the tracked object is an ideal-state projection, not a quotient of E(F_p).
  - IDEA-20260901-863e36 (propagation belongs to a projection paired with an operation group): C3 states the pair; nothing in it asserts a projection that would be constant or injective.
  - KN-FIND-ffe1df Theorem C (quasigroup combining rule forces a surjective homomorphism E(F_p) -> ([M], f), impossible for N prime and M < N): applies to Wagner k-tree filters h on E(F_p) with a combining rule; C3 has no filter, bucket or combining rule, and works over F_{2^n} coordinates.
  - KN-OPEN-020 (bounded-degree algebraic factor bases over F_p scoped out): prime-field statement; C3 is binary and changes no factor base.
- Caveat: C3's SO-TABLE/SO-GEN escape is the premise of LEAD-ICB-prime-degree-algebraic-decomposition, so it inherits that lead's open_blocked status and its forecloses; it adds no new escape.

N4 verdict: pair stated; not a rigidity result in new notation; nothing to escape because nothing new is asserted.

## What would make this worth running (conditions, not a recommendation to approve)

1. Attach pilot #4 (and pilot #3) as prior art to LEAD-ICE-descent-closure-degree-at-scale before ranking; C3 is then "the sparse-closure option of that lead, at its blocked cell", cost about a day of code (the column-set predicate already exists in `myclosure4.c` for D = 4 and a dense bit-packed eliminator; a D = 5, 440k-column dense build at u <= 2 is 72 GB by the 3 cols^2/8 model, 0.59x of that if the (4,6) ratio carries over, labelled prediction).
2. Run the calibration (4,15,6) D = 4 at u <= 1, u <= 2 and also `fullu` vs `L2u` at (4,9,3) to settle H3-b with the existing instruments first; pilot #4 makes failure of u <= 2 at m = 4 a live outcome.
3. Treat any (3,7) D = 5 truncated refutation as a certificate (valid by construction); treat failure to refute as inconclusive for the lead, as the candidate says.
4. Drop the B4 writability claim and the "SO-TABLE escape" claim from the framing.
5. Do not credit the FSS/BFT bounds: their hypotheses fail.
6. Replace the (4,6) calibration by an m = 3, l = 6 matched calibration, add the D = 4 negative control at (3,7), and drop the "(3,7) refutes at 4" outcome (see the defects section).


## Defects in the candidate's outcome table and calibration (found during the gate)

1. **The branch "(3,7) refutes at degree 4 -> open_next_step, +7.6 row restored" cannot occur.** A u-truncated closure keeps only rows that are genuine elements of the degree-D closure (products leaving the column set are dropped whole), so it is a subspace of the full W_D. The full degree-4 closure is already known not to refute at (3,7): `RESEARCH_ECC2K130_DESCENT_DEGREE.md` line 88 ("At l = 7 (N = 40, 42), on 8 of 8 draws, it does not refute at 4") and `dreg_hybrid_guess_20261024/RESULTS.md` ("Unspecialised degree 4 saturates without refuting on all 10 draws"). So C3 can only read "refutes at 5" (valid certificate; combined with the degree-4 failure it fixes the closure degree of that draw at exactly 5) or "inconclusive" (truncation is one-sided). It cannot restore the +7.6 row. This also gives a zero-cost negative control: the same truncation at D = 4 on the same draws must not refute; a refutation there would be an instrument bug.
2. **The calibration cell is mismatched to the target.** The first step calibrates on (4,15,6), an m = 4 cell, and kills C3 if truncation loses those refutations. Pilot #4 shows the needed u-cap rises with m and n at m = 4 (2 at n = 7, 3 at n = 9) while u <= 2 held 30/30 at m = 3 toy cells. A (4,6) failure could therefore kill an instrument that would still work at (3,19,7). A matched calibration is an m = 3, l = 6 cell that refutes at degree 4 (e.g. a (3,19,6) UNSAT draw), run at u <= 1 and u <= 2 against the full degree-4 closure, plus the D = 4 negative control above.
3. **Only one of the candidate's outcome-to-disposition rows is live:** "refutes at 5 -> best_measured '(3,7) refutes at 5 (degree rises at l = 7)', confirming the +10.32-bit bracket input". The "(4,7) at u <= 1" follow-up is infeasible on the host by the hybrid study's table ("an unsatisfiable system needs N = 84 and 1.4-1.5 TB of dense basis even at k = 8"); u-truncation is not shown to rescue it.

## Appendix: raw tool output (verbatim)

Environment: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as in the task; run from /Volumes/SSD990-2/crypto-autoresearcher. Each block is the unedited stdout+stderr of the command shown.

### N1 run 1: python3 tools/lead_atlas.py --match "multigraded block-multilinear truncated closure for chained descended S_3 systems"
```
   11  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    8  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    7  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    7  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    7  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    6  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
    6  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    6  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

### N1 run 2: python3 tools/lead_atlas.py --match "shrink the memory of the binary decomposition refutation by limiting degree in the internal-node variables"
```
   19  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   16  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   11  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
   11  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   10  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    9  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    9  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
```

### N1 run 3: python3 tools/lead_atlas.py --match "descended ANF too large to write inside the rho budget chained Semaev system memory column"
```
   35  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
   18  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   10  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   10  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    9  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    8  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    8  KR-RHO-fbd7b1                                known_result       Grumpy giants and better-than-rho generic ordering
```

### N1 run 4: python3 tools/lead_atlas.py --match "multidegree truncated Macaulay closure mutants degree in internal node variables bihomogeneous Hilbert series descended Semaev"
```
   22  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   15  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   13  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   13  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   10  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    9  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    9  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    8  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
```

### N1 extra X1: python3 tools/lead_atlas.py --match "block-local locality restricted degree-4 closure u-bit cap fewer columns"
```
    7  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    6  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    5  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
    4  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    3  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    3  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    3  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    1  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
```

### N1 extra X2: python3 tools/lead_atlas.py --match "structured Groebner on multihomogeneous systems block-aware selection bilinear core XL"
```
   11  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   10  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    8  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    7  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    6  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
    6  KR-IC-f3da82                                 known_result       F4 trace reuse across many similar systems
    6  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
```

### N1 extra X3: python3 tools/lead_atlas.py --match "sparse closure larger memory host degree-5 closure cell"
```
    6  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    6  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    6  LEAD-RHO-cheon-toy-reproduction              open_next_step     Toy reproduction of Cheon's algorithm with memory charged and supplied-input CRT composition
    6  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    6  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged
    5  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    4  KR-RHO-fbd7b1                                known_result       Grumpy giants and better-than-rho generic ordering
    4  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
```

### N2 run 1: python3 tools/build_frontier_map.py --match "multigraded block-multilinear truncated closure for chained descended S_3 systems"
```
KR-IC-fbdb61  score=7  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-e847d1  score=6  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-IC-0d2021  score=3  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-f3da82  score=3  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-955fd6  score=1  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-b0fcda  score=1  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-f5c584  score=1  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
```

### N2 run 2: python3 tools/build_frontier_map.py --match "shrink the memory of the binary decomposition refutation by limiting degree in the internal-node variables"
```
KR-IC-889857  score=11  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-46d822  score=9  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-955fd6  score=9  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-f5c584  score=7  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-fbdb61  score=6  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
```

### N2 run 3: python3 tools/build_frontier_map.py --match "descended ANF too large to write inside the rho budget chained Semaev system memory column"
```
KR-IC-a4dd54  score=8  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-fbd7b1  score=8  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
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

### N2 run 4: python3 tools/build_frontier_map.py --match "multidegree truncated Macaulay closure mutants degree in internal node variables bihomogeneous Hilbert series descended Semaev"
```
KR-IC-889857  score=9  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-0d2021  score=4  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

### N2 extra X1: python3 tools/build_frontier_map.py --match "bilinear bihomogeneous Groebner multi-homogeneous XL Hilbert series degree of regularity"
```
KR-IC-fbdb61  score=10  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=9  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-0d2021  score=8  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-f5c584  score=7  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-e2d81b  score=3  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
```

### N3 ledger greps (python substring match over ledger/.index/{proposals,hypotheses}.jsonl; format: id | status | matched terms | title[:70] | claim[:100]; script: scout/lgrep.py)
```
#### proposals.jsonl term: multigraded
#### hypotheses.jsonl term: multigraded
H-MGD-001 | specified | ['multigraded'] |  | For generic-prime ECDLP, a Cummings--Hauenstein homogeneous multigraded dual-space route can support
#### proposals.jsonl term: multihomogeneous
IDEA-20260731-009 | unverified | ['multihomogeneous'] | Crypto-size first-fall-degree correspondence — sample Semaev-shaped sy | The first-fall degree d_ff and Macaulay-bound degree d_reg of Semaev-shaped multihomogeneous systems
#### hypotheses.jsonl term: multihomogeneous
#### proposals.jsonl term: multi-homogeneous
IDEA-20260808-ec2128 | proposed | ['multi-homogeneous'] | The k-tuple intersection system is MULTI-HOMOGENEOUS with multidegrees | PRECISELY WHICH SYSTEMS ARE BIGRADED, derived this session. (A) The k-tuple intersection system -- f
#### hypotheses.jsonl term: multi-homogeneous
#### proposals.jsonl term: truncated macaulay
IDEA-20260916-e6540d | proposed | ['truncated macaulay'] | DEGREE-CAPPED CERTIFIED DECOMPOSITION: cap the Macaulay degree at D_0, | (A) THE RESTRUCTURING. Semaev's characteristic-2 index calculus (KN-LIT-fa346d) costs stage 1 at abo
#### hypotheses.jsonl term: truncated macaulay
#### proposals.jsonl term: internal node
IDEA-20260808-d6d973 | proposed | ['internal node'] | Elimination-yield duality: for prime-field point decomposition, keepin | Let a decomposition R = P_1 + ... + P_m be organised by a binary addition tree with internal nodes I
IDEA-20260904-8dccc9 | proposed | ['internal node'] | THE WINDOW DOES NOT HAVE TO BE ONE UNKNOWN: re-parametrizing the SAME  | Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
IDEA-20260904-e9675e | proposed | ['internal node'] | THE TREE HYPOTHESIS IS NOT LOAD-BEARING ON THE DEMAND SIDE: eps_requir | (A) THE AUXILIARY-COUNT LAW. Let a decomposition test for "P_1 + ... + P_m = R with x(P_k) in a wind
IDEA-20260913-c94e52 | proposed | ['internal node'] | Chaining topology is a four-fold invariant with one bounded variant: e | GOAL-SEMBIN-cbf422 sub-objective 3 asserts that "a balanced tree is another presentation of the same
#### hypotheses.jsonl term: internal node
H-PFDR-a79efd | proposed | ['internal node'] |  | DEGREE AND YIELD ARE TWO ENDS OF ONE BUDGET IN THE WINDOWED ADDITION-TREE FAMILY, AND THE YIELD HALF
#### proposals.jsonl term: per-block
IDEA-20260807-394cf4 | proposed | ['per-block'] | EV-EQJ-001 measured a relation module collapsing to 11-15 DISTINCT coe | EV-EQJ-001 rejected the isotypic linear-algebra mechanism cleanly -- exactly 4 of 10 isotypes carry 
IDEA-20260816-1e36fa | proposed | ['per-block'] | Treat the near-collision block chain as a counted object: define N(k), | (A) The published chosen-prefix cost for a Merkle-Damgard hash is a single headline number, but stru
IDEA-20260816-7fe6c0 | proposed | ['per-block'] | Measure what whipping buys before pricing what it costs: the rank dist | (A) MAYO's whipping factor k exists for one stated reason: the underlying UOV map has an oil space t
IDEA-20260816-ade53e | proposed | ['per-block'] | Charge the restarts: measure the distribution of abort depth in near-c | (A) A near-collision block search proceeds by satisfying a chain of conditions and restarting when o
IDEA-20260901-8e3a59 | proposed | ['per-block'] | THE EFFECTIVE PER-BLOCK COST EXPONENT IS c MINUS f, AND f IS BOUNDED B | FIVE SEPARABLE CLAIMS. (A) THE EXPONENT. The expected cost of one near-collision block is 2^{c-f} co
IDEA-20260922-1f9967 | proposed | ['per-block'] | Per-block new_falls on symmetry sectors, crater automorphism versus fl | Representation class R1 of RQ-ECDLP-623a32 (summation coordinates, split into isotypic blocks), atta
#### hypotheses.jsonl term: per-block
H-PFDR-f7161e | proposed | ['per-block'] | The amalgam Hilbert-series identity H_full = H_A * H_B / H_{k[U]} is a | (A) THE OBJECT. In the boolean chained Semaev system at t = 3 over GF(2), IDEA-20260828-d91efa asser
H-SHAONE-fd1a54 | specified | ['per-block'] | Stage 0 effective per-block cost exponent minus bounded identities — n | Fix the exact count identity of IDEA-20260901-8e3a59 before any later-stage claim. Stage 0 asserts o
#### proposals.jsonl term: mixed degree
#### hypotheses.jsonl term: mixed degree
H-DREG-662920 | specified | ['mixed degree'] |  | For K=F_(2^n), absolute trace Tr to F2, independently coordinatized u in K and x in an F2-subspace V
#### proposals.jsonl term: multilinear
IDEA-20260903-cf63ad | proposed | ['multilinear'] | THE PRIME-FIELD DIGIT TWIN OF THE BINARY CHAINED SEMAEV SYSTEM HAS NEI | Setting. E/F_p short Weierstrass y^2 = f(x), p > 3, arity m = 3, chained t = 3 tree as in GOAL-DREG-
IDEA-20260924-8b28ea | proposed | ['multilinear'] | N-CONV. Keep S_3's exact quadratic part phi_{x_R}(Q) (the rank-16 imag | CEILING FIRST. No cost claim of any kind. At m = 2, oracle A (2^9 root-findings per attempt) decides
#### hypotheses.jsonl term: multilinear
H-PFDR-9aadc0 | specified | ['multilinear'] | The prime-field digit twin of the binary chained Semaev system has nei | SETTING. E/F_p short Weierstrass, p > 3, arity m = 3, chained t = 3 tree over F_p with no Weil desce
H-PFDR-c88f14 | specified | ['multilinear'] | No bounded-last-fall-degree theorem transfers to the prime-field digit | (A) TRANSFER, DERIVED. arXiv:2103.07282 (retrieved at abstract and ar5iv level by the proposing sess
#### proposals.jsonl term: block-local
#### hypotheses.jsonl term: block-local
#### proposals.jsonl term: sparse closure
#### hypotheses.jsonl term: sparse closure
#### proposals.jsonl term: u-degree
IDEA-20261006-8d97d3 | proposed | ['u-degree'] | Leading coefficient of the composition square against the leading coef | For Phi_T = g tau + Delta tau^2 the composition Phi_T composed with itself has tau-degree 4 and lead
#### hypotheses.jsonl term: u-degree
```

### Earlier N3 greps in this session (same script) that returned only unrelated or the same rows: terms bihomogeneous (no hits), bilinear (UOV/MAYO/pairing records and H-DREG-44d4b8, H-NISTBIN-1803fe), multilinear (IDEA-20260903-cf63ad, IDEA-20260924-8b28ea, H-PFDR-9aadc0, H-PFDR-c88f14), block degree / weighted degree / partial degree / multidegree variants (only IDEA-20260808-ec2128 for 'multidegree').

### Repository greps for the mechanism outside the ledger index (grep -rIl, case-insensitive; u-degree|block-multilinear|bihomogeneous|multigraded|multihomogeneous)
```
crypto-autoresearcher: analysis/ecdlp2m-iteration-20261009/leads-pilot4/{PREDICTIONS.md,README.md,myclosure4.c} (u-degree cap), docs/reports/ecdlp-lead-discovery-20261024/FOLD.md (multigraded Bezout, sparse elimination folded: no new exponent), knowledge/literature/{KN-LIT-3247,KN-LIT-023}.md, knowledge/findings/KN-FIND-017.md, knowledge/techniques/KN-TECH-007.md, ideas/* (older ECDLP-IDEA records)
crypto: research/pdp_literature_leads_20261022/leads/{LEAD-01,LEAD-14,LEAD-12,LEAD-03,LEAD-02,LEAD-08}.md, research/xl_bilinear_core_20261006/README.md, research/xl_trilinear_t_unknown_20261006/README.md, research/ic_tree_split_cutout_20260930/RESULTS.md, research/sat_factor_base_review_20260908/autolab/runs_manual/binary_s4_ffd_l8_20260920/ANALYSIS.md
```

### Raw: key lines read from pilot #4 and FSS
```
leads-pilot4/README.md result 2 (verbatim table rows): '| 3, 9, 3 | <= 2 | 3,082 / 4,048 |', '| 3, 11, 4 | <= 2 | 8,428 / 10,903 |', '| 4, 7, 2 | 2 (with L2) | 3,450 / 9,109 |', '| 4, 9, 3 | 3 (with L2; L2u2 refutes 0/10) | 23,198 / 31,931 |', '| 5, 9, 3 | 4 = no cap (L2u3 refutes 0/5) | 65,649 / 124,314 |'
leads-pilot4/README.md ranked lead 6: 'Not a lead: u-bit caps (result 2) | closed at m >= 5 for the toy cells measured'
FSS 1001.4004 Theorem 6.1 (pdftotext of arXiv PDF): 'If the system F is generic, then the degree of regularity of theta(I) is upper bounded by dreg <= min(nx + 1, ny + 1).' Section 6.4: 'we suppose without loss of generality that nx <= ny. We also assume in this part of the paper that the characteristic of k is 0 (although the results remain true when the characteristic is large enough).'
```
