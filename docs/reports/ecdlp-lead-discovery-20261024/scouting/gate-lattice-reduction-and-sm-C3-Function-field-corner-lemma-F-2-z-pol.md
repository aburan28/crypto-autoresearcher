# Novelty gate N1-N4: C3 "Function-field corner lemma: F_2[z] polynomial-lattice (Popov-form) decomposition on ECC2K-130"

Field key: lattice reduction and small-root methods. Date 2026-10-24. Gate run by a subagent of the lead-discovery workflow.
Claim tier: gate analysis only. `sota_delta`: zero. No speedup is claimed or implied; rho stays the best known method.

Conventions used below. Every outcome labelled "produced here" was computed in this gate and its script and output are in section 6.
Everything labelled "prediction" or "conditional" is not an outcome. Every citation carries `provenance: recalled | retrieved`.

Housekeeping. (1) I wrote only under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`; no repo file was opened for writing. The final pasted runs of `lead_atlas.py` / `build_frontier_map.py` (Appendices A and B) used `python3 -B`; my earlier exploratory runs of the same tools did not. `tools/__pycache__` holds only cpython-312 files, the newest dated 22:35:22, which predates this gate (first run about 23:34), and no cpython-39 file exists (my interpreter was 3.9), so I have no evidence that any bytecode was written.
(2) The scout directory is shared with other concurrent gates: while I worked, files named `raw/n1_p*.txt`, `_c3_raw/atlas1..4.txt` and `_c3_raw/krmap1..4.txt` appeared that I did not create, and my first `raw/n1_a.txt` and `raw/n1_b.txt` do not match a fresh run of the same phrasings (n1_a's top hit was generic-table-oracle at score 10, a fresh run gives coppersmith-smallroot-semaev at 21; n1_b was empty when first counted and later held a different query's output), so both were clobbered by another process. The raw outputs pasted in Appendices A and B were therefore regenerated in one pass at assembly time (private directory `_c3_work/`), not copied from the shared files.
(3) The ledger index files `proposals.jsonl` / `hypotheses.jsonl` carry mtime 17:44-17:46 on 2026-10-24; ledger records filed after that are invisible to the N3 grep.

---

## 0. Verdict

**`duplicate_of_lead`, lead = `LEAD-ICP-coppersmith-smallroot-semaev` (open_next_step), with a scope note: the binary F_2[z] cell of that lead has never been run.**

Why not `advances_lead`: that verdict needs the candidate to be a sharper next step for the open lead, i.e. to change its `next_action` or `discriminates`. C3 does not: the lead's step is the optimal-shift-set computation on the prime-field S_3 polytope, (4,2) tree and rank-r GAP, and nothing in C3 touches it. Why not `new`: the engine is the lead's (Coppersmith/HG shift lattice on S_{m+1}, cost set by lattice reach), and the lead's `forecloses` phrases carry no ring qualifier.

One-paragraph reason. C3 uses the same engine class as the open lead: decomposition of a point as a multivariate small-root problem for S_{m+1} solved by a Coppersmith / Howgrave-Graham (HG) lattice, whose cost is set by lattice reach instead of solving degree. The lead's mechanism text and `forecloses` phrases ("Coppersmith small roots of summation polynomials", "small-x factor base solved by LLL") carry no ring qualifier. What the atlas, KR map and ledger do NOT contain is the transposition to the non-Archimedean ring F_2[z]/(F) with the polynomial-basis box (the known factor base V = span{1,...,z^{l-1}} of KR-IC-73db3f) as the window. Every row, evidence item, calculator (`tools/smallroot_reach.py`) and number of the lead is prime-field. So C3 is the same mechanism transposed to a ring the lead's rows do not cover, aimed at a different bottleneck (B4 writability, B5) than the lead's (B1). Under the strictness rule (same mechanism as an open lead, not a sharper step) that is `duplicate_of_lead`. The nuance that survives the verdict: the binary cell is unevaluated in the atlas, which is a scope gap in the lead (its foreclose phrases read broader than its prime-field evidence), not a new lead. I found no closed lead whose obstruction C3 fails to escape (section 1.2), and no KR row is the mechanism (section 2). Its own prediction is a closure, so its value is pre-emptive.

Three findings that change how the orchestrator should use it:

1. **Scope of the closure is narrower than the candidate's disposition text.** The corner lemma (as stated in the lattice scout's dossier, `scout-lattice-smallroot.md` section 0) does not cover addition trees with kept windowed internal nodes (w > 0). The candidate's "closed_obstructed(theorem) for the polynomial-lattice oracle class" would therefore have to be scoped to the single-equation (w = 0) family, or the tree cells must be computed. In characteristic 2 the tree blocks are much sparser than in the odd-characteristic polytopes behind the prime-field numbers: produced here, the x-monomial supports are S_3: 5 of 27, S_4: 24 of 625, S_5: 729 of 59,049 (prime-field supports recorded in `CLOSURE.md` section 3 and `LEAD-STR-special-j-ic-semaev`: S_3 13 of 27, S_4 439 of 625). So the prime-field (4,2) reach number does not transfer to F_2[z] by "the induction is characteristic-free"; that induction covers the corner coefficient only.
2. **The corner premise itself checks out in characteristic 2** (produced here, section 6): the corner coefficients of S_4 (x1^4 x2^4 x3^4) and S_5 ((x1 x2 x3 x4)^8) are the constant 1 in F_2[b, x_R]. This is step (i) of the candidate's first step, done.
3. **The univariate function-field Coppersmith theorem with exact lattice reduction is a published result** (Cohn-Heninger, arXiv:1008.1284 Theorem 1.2, `retrieved`), so the "external ingredient" is known literature; its multivariate form is only mentioned there, not developed.

Recommended disposition (a recommendation, not a status change): do not open C3 as a separate lead. File it as a binary scope note on `LEAD-ICP-coppersmith-smallroot-semaev` (the lead gains a binary F_2[z] cell: w = 0 closed by the corner argument if the F_2[z] probe confirms it, tree cells open with the 5 / 24 / 729-term supports), or, as the candidate proposes, as a pre-emptive closure under `LEAD-ICB-decomposition-encoding-and-sat` with the w = 0 scope qualifier.

---

## 1. N1. Atlas collision

Four runs: the candidate's 3 `match_phrasings` (A1, A2, A3, in the candidate's order) plus one of my own (A4: "polynomial lattice Coppersmith Howgrave-Graham F_2[z] Semaev summation polynomial decomposition polynomial basis"). Raw output: Appendix A.

### 1.1 Top 5 per run (all five were opened and read: YAML mechanism + obstruction + forecloses; KR rows read in KRMAP.md)

| run | rank: score id (disposition) |
|---|---|
| A1 | 1: 21 LEAD-ICP-coppersmith-smallroot-semaev (open_next_step); 2: 19 LEAD-ICB-cofactor-torsion-quotients (closed_obstructed); 3: 16 LEAD-ICB-kic-golden-base-exact-decomp (open_next_step); 4: 14 LEAD-ICB-frobenius-orbit-factor-base (closed_obstructed); 5: 12 KR-IC-73db3f (known_result) |
| A2 | 1: 12 LEAD-ICB-decomposition-encoding-and-sat (closed_obstructed); 2: 11 LEAD-ICP-coppersmith-smallroot-semaev; 3: 9 LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked); 4: 9 LEAD-ICE-sat-xor-pdp-oracle (open_next_step); 5: 8 LEAD-ICB-quasi-subfield-polynomials (closed_obstructed) |
| A3 | 1: 10 LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed); 2: 9 LEAD-ICP-icperf-writability-boundary (closed_obstructed); 3: 7 LEAD-ICE-rootfind-pairtable-oracle (open_blocked); 4: 6 LEAD-ICE-gpu-rootfind-oracle (open_blocked); 5: 6 LEAD-ICP-icperf-binary-pdp-solver (open_next_step) |
| A4 | 1: 19 LEAD-ICP-coppersmith-smallroot-semaev; 2: 17 KR-IC-5a43e5 (known_result); 3: 14 LEAD-ICE-boolean-f4-f5-f6-engines (closed_dominated); 4: 14 LEAD-STR-special-j-ic-semaev (open_next_step); 5: 13 LEAD-ICB-decomposition-encoding-and-sat |

Note on score ties/ranks: A3's lowest scores (6-7) show the "never writes the descended ANF" phrasing matches the atlas only through generic words; LEAD-ICP-icperf-writability-boundary is rank 2 there and is the lead the phrasing is really about. Additional leads read because the obstruction slot they hold is the one C3 claims to escape: `LEAD-ICB-generic-table-oracle`, `LEAD-ICE-descent-closure-degree-at-scale`, `LEAD-ICE-hybrid-guess-determine-l7`, `LEAD-ICE-curve-presentation-invariance`, `LEAD-ICB-cofactor-torsion-quotients`.

### 1.2 Reading, grouped by relation to C3

**(a) Same engine class: `LEAD-ICP-coppersmith-smallroot-semaev` (open_next_step), the only same-mechanism hit.**
- Mechanism (quoted): "A small-x or windowed factor base turns decomposition into a multivariate small-root problem for S_{m+1}, whose cost is set by lattice reach rather than solving degree. ... if reach exceeded the index-calculus demand the decomposition would cost polynomial time per attempt at a factor base large enough to beat rho."
- Forecloses (verbatim): Coppersmith small roots of summation polynomials; small-x factor base solved by LLL; windowed addition tree with lattice reduction; symmetric e1 e2 lattice for S_3; rank-r generalized arithmetic progression factor base; lattice-assisted meet-in-the-middle decomposition.
- Next action (summarised): provably optimal shift set (Ryan EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m,w) = (4,2) system and the rank-r >= 2 GAP; planted S_4/S_5 recovery only if the computed reach clears 8/9. Family `ic-prime`; evidence is `analysis/smallroot-reach/CLOSURE.md`, `tools/smallroot_reach.py`, prime-field ledger records. No obstruction block (open lead).
- Relation to C3: same engine (HG/JM shift lattice on S_{m+1}), same question (reach versus the index-calculus demand), different ring (F_2[z]/(F) with degree as the size function, exact lattice reduction) and different window (the polynomial-basis box). The lead's own source record (IDEA-20260808-486ae2, opened, section 3) frames the lattice as the substitute for the subfield's linear conditions over F_p ("Over F_p there is no subfield, so the classical substitute for 'linear condition' is 'archimedean smallness'"). In binary the same set V is both a linear subspace (where the descent/SAT/Groebner engines live) and a degree window (where a lattice engine can live); C3 is the second reading. The atlas records only the first.
- What C3 does that the forecloses phrases do not cover: nothing at the level of the phrases (they are unscoped and would cover it literally). What it adds is outside the lead's recorded scope: the ring, the exactness of the reduction, the characteristic-2 supports, the demand model with LA 2^{2l}, and the target (B4/B5). That is why the verdict is `duplicate_of_lead` with a scope note (same mechanism, unevaluated ring) and not `new`.
- What C3 does NOT do for the lead: it does not give a sharper next step on the lead's prime-field shift-polytope computation. The lead's `discriminates` is untouched by C3.

**(b) Closed binary leads whose obstruction premise C3 must escape. None is a duplicate; premise-by-premise (statements quoted verbatim in section 1.3):**
- `LEAD-ICP-icperf-writability-boundary` (cost_model; Scope: standardised binary curves with n <= 283, unchained descended ANF). Premise "descended ANF exceeds the per-decomposition rho budget by +40.8 bits at ECC2K-130": **escaped**, because a lattice on (S_{m+1}, F)^t over F_2[z] is built from S_{m+1} itself and never from a Weil-descended Boolean system. Not a claim that the lattice is free: its dimension and the size of S_{m+1} are separate costs (conditional: irrelevant if the reach ceiling binds first, which is C3's own prediction).
- `LEAD-ICB-decomposition-encoding-and-sat` (measured). Premise "SAT or enumeration, per-attempt UNSAT cost 2^{alpha l}, alpha ~ m": **escaped** (a lattice attempt costs polynomial time inside its reach, not 2^{alpha l}). Its `revisit_when` ("a solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3") is the slot C3 would occupy if its reach sufficed; C3 predicts it does not.
- `LEAD-ICB-generic-table-oracle` (theorem; Scope: all binary and Koblitz curves, one target, setup charged). Premise "oracle built from group operations and membership tests": **escaped** (the oracle reads x-coordinates algebraically). Its `revisit_when` ("an oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|)") names exactly this class and routes it to `LEAD-ICB-prime-degree-algebraic-decomposition`.
- `LEAD-ICE-generic-oracle-arity-cost-floor` (cost_model; Scope: oracles that do not read curve coordinates algebraically). **Escaped** by its own Scope clause. Its `revisit_when` ("an oracle that reads coordinates with per-query cost polynomial in n at fixed degree ... is measured") asks for a measurement; C3 as proposed is an analysis with a toy probe, not that measurement.
- `LEAD-ICB-frobenius-orbit-factor-base` (proof; Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure). **Not escaped, and C3 says so**: the deg < l box is not Frobenius-stable, so it gets no n-fold relation saving and no n^2 LA saving, while rho keeps its sqrt(2n). Also at n = 131 the usable stable dimensions are empty, so no stable box exists to switch to. The same row reports the per-attempt decomposition probability on polynomial bases equals the birthday value at matched |FB| (n = 11..23), which is the P(decomp) = 2^{ml-n}/m! that C3's demand model uses.
- `LEAD-ICB-cofactor-torsion-quotients`, `LEAD-ICB-quasi-subfield-polynomials`: C3 uses no quotient/filter and no QSP root set; not touched.

**(c) Same slot, different engine (open or blocked leads; not the same mechanism):**
`LEAD-ICB-prime-degree-algebraic-decomposition` (open_blocked: subspace base + algebraic solve of the descended system; engines F4/closure/SAT), `LEAD-ICE-descent-closure-degree-at-scale` (open_blocked: closure degree of the descended chain), `LEAD-ICE-hybrid-guess-determine-l7` (open_next_step: guess k variables then refute), `LEAD-ICE-sat-xor-pdp-oracle`, `LEAD-ICP-icperf-binary-pdp-solver`, `LEAD-ICB-kic-golden-base-exact-decomp` (co-designed binary bases with exact MITM), `LEAD-ICE-rootfind-pairtable-oracle` and `LEAD-ICE-gpu-rootfind-oracle` (exact enumerative root finding), `LEAD-ICE-boolean-f4-f5-f6-engines` (closed_dominated), `LEAD-STR-special-j-ic-semaev` (support reduction at special j; note it records S_3 support 9 / 10 / 13 and no cost gain under Groebner), `LEAD-ICE-curve-presentation-invariance`. Each solves the same decomposition problem by a different engine on the same or a descended system; none uses a shift lattice over a polynomial ring. All of them are descended-system or enumerative; C3 is the first row in the binary families whose engine is a non-descended algebraic oracle.

Relevant to the "beyond reach" case (conditional, not measured): C3's own ceiling is m*l < n/D. Past it, the only way to keep using the lattice is to guess g ~ m*l - n/D bits of the box per attempt, which is the hybrid of `LEAD-ICE-hybrid-guess-determine-l7` with a lattice in place of Groebner; with g ~ 71-77 bits at ECC2K-130, m = 4 (section 5) that is 2^g lattice calls per attempt, which exceeds the roughly m*l/2 = 44-47 bits of a meet-in-the-middle attempt over the same box, so it would sit in the SO-TABLE regime rather than below it. I did not run this; it is an argument (conditional on the ceiling m*l < n/D binding as predicted).

### 1.3 Standing obstructions the candidate claims to touch: verbatim statements (Scope clauses included)

SO-TABLE, SO-FROB and the writability wall, plus the other closed rows read, quoted by `yaml.safe_load` from the lead files:

- **LEAD-ICP-icperf-writability-boundary** (closed_obstructed, kind=cost_model): obstruction.statement: "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."
  - revisit_when: "n >= 409, or a representation (e.g. chained S_3 at m = 5, 6, ~2^31-2^33 monomials) whose written size plus solve fits under the rho budget with memory charged."

- **LEAD-ICB-decomposition-encoding-and-sat** (closed_obstructed, kind=measured): obstruction.statement: "Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. Ladders n = 11..31: no arm grows slower than the enumeration floor (m = 3 slopes 0.53-0.58 vs floor 0.21; m = 4 wide chain 0.805 vs 0.333). Encoding levers are constants: S_m symmetrisation saturates product spaces at m >= 5 at balanced l (H-BINSTD-770ec3 supported), closure outcomes are basis-invariant (Proposition B), reduction-polynomial weight is a constant confound, Nagao coset yield weakened vs chained S_3, trace replay is a constant at most."
  - revisit_when: "A solver or presentation whose UNSAT cost grows by fewer than m/2 - 1 bits per unit l at m >= 3 (then it becomes LEAD-ICB-prime-degree-algebraic-decomposition)."

- **LEAD-ICB-generic-table-oracle** (closed_obstructed, kind=theorem): obstruction.statement: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged."
  - revisit_when: "An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition; constant-factor engineering of this pipeline remains valid baseline work (LEAD-ICB-koblitz-setup-phase-cost)."

- **LEAD-ICB-frobenius-orbit-factor-base** (closed_obstructed, kind=proof): obstruction.statement: "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."
  - revisit_when: "A Frobenius-stable base whose per-attempt decomposition probability exceeds the birthday value at matched |FB| (a second gain in the decomposition step), or a stable non-subspace base with membership degree far below its size (see LEAD-ICB-nonlinear-frob-stable-bases)."

- **LEAD-ICE-generic-oracle-arity-cost-floor** (closed_obstructed, kind=cost_model): obstruction.statement: "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."
  - revisit_when: "An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds C(B+m-1,m)/N on average."

- **LEAD-ICB-quasi-subfield-polynomials** (closed_obstructed, kind=theorem): obstruction.statement: "Euler-Petit Theorem 1: every linearized QSP has beta >= 3/4, so under the HKPYY cost model the exponent is >= 0.93, i.e. >= 2^122 at n = 131 against rho 2^60.9; for F_2-coefficient lambda only X^2 + X (n0 = 1) and L_Phi131 (n0 = 130) exist at n = 131 (Prop. 2), and multiplicative QSPs give |V| = 264 or p + 1, beta >= 1.02. The crypto census also shows Lemma 4.1 tight (the n mod n0 term cannot be removed; witnesses at n = 7). Measured at toy n = 31, k = 15: QSP bases yield 0.214 against 0.204-0.230 for random subspaces (no gain)."
  - revisit_when: "A non-linearized or correspondence-defined QSP family (IDEA-20260916-a17f43) whose root count escapes the Frobenius-injection bound, or an exhaustive search past n = 47 finding log2(deg lambda) < n0^2/n at prime n."

- **LEAD-ICB-cofactor-torsion-quotients** (closed_obstructed, kind=proof): obstruction.statement: "On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; the corrected iota-stable classification (V_d = b^{1/4} F_{2^d}) empties the (subspace base, 2-torsion quotient) cell on every prime-degree standardized curve; the production 2-torsion census adds 0 relations. FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family)."
  - revisit_when: "A curve with a large smooth cofactor, or a non-homomorphic sum-compatible filter with more than log2(cofactor) bits."

### 1.4 Other standing obstructions (SO-GEN, SO-MULTI, SO-ENDO, ...)

C3 changes no group, no endomorphism action, no target set and no pairing, so SO-ENDO, SO-ISO, SO-PAIR, SO-PADIC, SO-XEDNI, SO-COVER, SO-MONO, SO-WALK, SO-DECK, SO-CHEON, SO-NET and SO-TORS are not engaged. SO-GEN (generic Omega(sqrt r), GGM-simulable oracles) is engaged only in the sense that an oracle that reads coordinates algebraically is outside the GGM model by construction; that is the property C3 relies on and does not by itself give a speedup. SO-MULTI (one target vs portfolio) is not engaged: C3's relation collection is per-target in the same way as the incumbent pipeline. SO-ALGFB (bounded-degree algebraic factor bases give O(d) points) is stated for F_p; over F_{2^n} the box is an F_2-subspace of 2^l points described by degree-1 conditions after Weil restriction, so it is not in that bound's scope, and the candidate's window is a size condition (see N4).

---

## 2. N2. Known results

Raw: Appendix B (four runs). Hits and relation to C3:

| KR row | what it says (KRMAP, read) | same as C3? |
|---|---|---|
| KR-IC-73db3f (score 12 in B1) | factor base {P : x(P) in V}, V an F_2-subspace; polynomial-basis V = span{1,z,...,z^{l-1}} lowers degree/variable count after Weil descent (FPPR, Petit-Quisquater, HPST 2013; Shantz-Teske experimental) | The FACTOR BASE of C3 is exactly this (R1 box). The SOLVER is not (those papers descend and use Groebner/SAT). Known: the base. New to the KR map: the lattice solver on it. |
| KR-IC-5a43e5 (B1 11, B4 17) | Semaev summation polynomials; "novelty must lie in representation, factor base, elimination or solver, never in 'use summation polynomials'" | C3's claimed novelty is in the solver, as this row requires. |
| KR-IC-5765d2, KR-IC-1fcdbc, KR-IC-889857, KR-IC-fbdb61, KR-IC-955fd6, KR-IC-8b9daa, KR-IC-46d822 | SAT/XOR (constant factors, same exponent as rho), char-2 summation algorithms far slower than rho (Galbraith-Gebregiyorgis, Shantz-Teske), first-fall-degree dispute, last fall degree bounds, symmetry/torsion speedups, Karabina, Gaudry | Different engines/results; not the lattice oracle. They are the background against which a reach-based oracle would be the only non-descended competitor. |
| KR-IC-b0fcda | Frobenius-invariant bases for subfield (Koblitz) curves | C3's base is not Frobenius-stable; no overlap. |
| KR-IC-5931ee | naive prime-field Semaev IC cannot beat generic methods | prime-field; context for the lead in 1.2(a). |

**No KR row is the Coppersmith/HG lattice mechanism on summation polynomials, in any ring.** The KR map has no lattice small-root row at all (grep of KRMAP.md for "coppersmith|howgrave|small-root|LLL|lattice" returns nothing). So N2 gives no `known_result` hit inside the program's map.

External literature (outside KRMAP), with provenance:

| item | what I verified | provenance |
|---|---|---|
| H. Cohn, N. Heninger, "Ideal forms of Coppersmith's theorem and Guruswami-Sudan list decoding", ICS 2011, arXiv:1008.1284 | Theorem 1.2 (polynomial ring): for f monic of degree d over F[z], modulus p(z) of degree n, finds every w(z) with deg w < beta^2 n / d and deg gcd(f(w), p) >= beta n; equivalent to Guruswami-Sudan when p splits; F[z]-lattices are measured by max coordinate degree (non-Archimedean), the shortest vector is found exactly in polynomial time (no LLL-type approximation loss); column-reduced bases in about m^(omega+o(1)) D operations; multivariate versions are only mentioned as corresponding to Parvaresh-Vardy / Guruswami-Rudra decoding, not developed. | **retrieved** (WebSearch + WebFetch of ar5iv.labs.arxiv.org/html/1008.1284; I read the first 100,000 of 125,500 characters) |
| Y. Aono, M. Agrawal, T. Satoh, O. Watanabe, "On the optimality of lattices for the Coppersmith technique", ACISP 2012 (ePrint 2012/108; journal AAECC 29(2), 169-195, year given as 2017 by the IAS repository and 2018 by DBLP) | Exists; shows (under a random-lattice heuristic) that the Coppersmith/May lattice already attains the best range for univariate modular equations, and optimality for the Boneh-Durfee bivariate equation. I did NOT verify the candidate's attribution "for the counting method" in detail. | **retrieved** (existence and content summary via WebSearch); the "counting method" attribution stays **recalled** |
| Mulders-Storjohann weak Popov form / Popov-form reduction over F[z] | not fetched; Cohn-Heninger's statement of exact reduction (above) is the retrieved support for the exactness claim | **recalled** |
| Guruswami-Sudan interpolation | equivalence to the F[z] Coppersmith theorem is stated in the Cohn-Heninger abstract | **retrieved** (through the Cohn-Heninger abstract) |
| Any prior use of a Coppersmith/lattice small-root method for binary-curve point decomposition | three standard WebSearch queries (including "Coppersmith lattice index calculus binary elliptic curve summation polynomial small root F_2[x] polynomial lattice point decomposition") returned only Groebner/SAT papers (FPPR, Petit-Quisquater line, Courtois ePrint 2016/003, Shishay-Gebregiyorgis thesis) | **retrieved, negative**: a failed search is not a proof of absence; 3 queries, standard mode only |

Net for N2: the load-bearing univariate function-field ingredient is a published theorem (`retrieved`); the program-specific composition (F_2[z] HG lattice on S_{m+1} with the polynomial-basis box, for ECC2K-130) is not a KR row and I found no source for it. The multivariate heuristic (extracting a common root from several short lattice vectors) is the same unproved algebraic-independence step as in the integer case.

---

## 3. N3. Ledger

Greps (exact, case-insensitive substring) of `ledger/.index/proposals.jsonl` (2,678 rows) and `hypotheses.jsonl` (2,131 rows) over title, claim/statement, mechanism: `F_2[z]`, `function field`, `function-field`, `Popov`, `polynomial lattice`, `polynomial-lattice`, `polynomial basis`, `F_2[x]`, `GF(2)[x]`, `F_q[x]`, `polynomial ring`, `Hermite`, `Guruswami`, `Pade`, `Mulders`, `Storjohann`, `Lenstra`, `lattice reduction`, `Coppersmith`, `small-root`, `small root`, `smallroot`, `Howgrave`, `Jochemsz`, `corner lemma`, `leading monomial`, and a cross-grep (binary/Koblitz/ECC2K/F_{2^/GF(2/Weil-descent terms AND lattice/Coppersmith/small-root/LLL/BKZ/Popov/function-field terms).

Result: **no record combines a lattice small-root method with a binary field or F_2[z].** `Popov`, `Guruswami`, `Pade`, `Mulders`, `Storjohann`, `polynomial lattice` return nothing; `corner lemma` / `leading monomial` return only a Groebner-context hypothesis (H-DREG-91be14). `function field` hits are all the xedni/elliptic-surface lane (different object).

Records that may be the same object (id, status, first 100 characters of claim):

| id | status | claim (100 chars) | same object as C3? |
|---|---|---|---|
| IDEA-20260808-486ae2 | proposed | (A) CLASSIFICATION. IDEA-20260801-021 / IDEA-20260803-e2f5bd bound any factor base cut out by a targ | Source record of the prime lead (opened): windowed tree, Z, Archimedean window. Same engine class, other ring. |
| IDEA-20260903-81a943 | unverified | For windowed (lattice-describable) prime-field factor bases attacked through a binary addition tree, | Prime closure note (CLOSURE.md). Not the object. |
| IDEA-20260904-39336c | proposed | The closure of IDEA-20260903-81a943 rests on one supply number, eps_available(S_3) = 0.8408, the Joc | Prime; says optimal-strategy runs never done. |
| IDEA-20260904-8dccc9 | proposed | Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t | Prime rank-r re-parametrisation (opened). Not the object. |
| IDEA-20260808-c31f1c | proposed | The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re | Prime rank-r GAP. |
| IDEA-20260808-e2315e | proposed | Every published Coppersmith-type analysis takes the shift lattice dimension to infinity at polynomia | Prime superpolynomial dimension. |
| IDEA-20261009-85062c | proposed | The empirical 50%-recovery threshold beta* for S_3 is well below 1/2 and degrades further for S_4. F | Prime planted threshold on S_3/S_4 (opened). Not binary. |
| H-PFDR-621852 | proposed | On the frozen direct-box S4/S5 planted law and actual modular JM/BKZ pipeline, test source beta thre | Prime planted S4/S5 JM/BKZ; the experiment C3's probe would mirror in F_2[z]. |
| H-PFDR-3c7d1e | proposed | The rank-1 closure of the lattice-describable factor-base family (IDEA-20260903-81a943, analysis/sma | Prime. |
| H-ECDLP-c3d48a | specified | Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham | Prime Stage 0 identities. |
| IDEA-20260923-9e4b71 | proposed | (A) THE MODEL SHIFT. RQ-ECDLP-78dbc5 asks for fewer stored entries at fixed online cost in a charged | Prime preprocessing re-reading of the closure. |
| IDEA-20260922-d11575 / H-BINSTD-490c76 | proposed / approved | Let E be any of c2pnb176v1, c2pnb208w1, c2pnb272w1, c2pnb304w1, c2pnb368w1, so (audit, analysis/bins | Binary, "descent lattice" = GHS descent; unrelated object. |
| IDEA-20261001-5628bc | proposed | SCOPE. ECC2K-130: E: y^2 + xy = x^3 + 1 (a = 0, b = 1) over F_2[z]/(z^131 + z^13 + z^2 + z + 1), #E | Cofactor as factor-base-size parameter; not lattice. |
| IDEA-20260916-3f7a1c | proposed | (A) THE REDUCTION, STATED IN FULL BECAUSE IT IS THREE LINES. Let lambda in F_2[X], d = deg lambda >= | QSP census; polynomial basis but no lattice solver. |
| IDEA-20261018-1aff90 | proposed | A GF(2) block Wiedemann (Coppersmith) consistency test on the Macaulay m | "Coppersmith" here is block Wiedemann, a different algorithm. |
| H-DREG-44d4b8 | approved | Let F be F_2[z]/(z^5 + z^2 + 1), V the F_2-span of {1, z}, R_X = z, and B = z + 1. Among lambda in F | Toy F_2[z] Semaev closing identity; no lattice. |

Three full records opened by exact path to decide (limit 3; the two rigidity records IDEA-20260806-c5d183 and IDEA-20260901-863e36 were opened separately for N4, which names them): `ledger/proposals/IDEA-20260808-486ae2.yaml`, `IDEA-20260904-8dccc9.yaml`, `IDEA-20261009-85062c.yaml` (first 3,500 characters each). All three are prime-field/Archimedean (windows in [0,B) subset F_p, integer small-root solvers, planted p of 40-80 bits). None mentions binary fields, F_2[z], non-Archimedean size, Popov form or function fields. Decision: no ledger record is the same object; the prime siblings are the object's twin, which is consistent with `duplicate_of_lead` on LEAD-ICP-coppersmith-smallroot-semaev (whose `ledger_refs` list these records).

Other relevant findings from the repo (read, not ledger-index hits): `docs/reports/ecdlp-lead-discovery-20261024/report.md` records (a) that the polynomial-basis V of KR-IC-73db3f "was never run" in the descent-closure lead (scope qualifier AUD-2), and (b) a staleness flag on the Coppersmith lead: its quoted numbers (0.8408, margin -0.0481 at (4,2)) are superseded by correction CORR-20261024-b2a799 (eps(S_3) = 0.2803, margin -0.6086 at (4,2)). I did not locate the CORR record or the `tools/smallroot_reach_hg.py` the lattice scout cites in this checkout (only `tools/smallroot_reach.py` exists), so I did not reproduce 0.2803.

---

## 4. N4. Notation change (IC / factor-base / representation candidate)

**The (representation, operation set) pair.** (R1 polynomial-basis coordinates x = sum_{j<l} c_j z^j in F_2[z]/(F), c_j in F_2, with the size function deg x(z) < l; Sigma = translation by factor-base elements, i.e. Class I partial-action of IDEA-20260806-c5d183). The oracle is an F_2[z]-lattice (HG/Popov) on (S_{m+1}, F)^t. Representation class R1 of RQ-ECDLP-623a32; attack stage changed: relation decomposition (solver), not membership.

**Is it a recorded rigidity result in new notation?**
- `IDEA-20260806-c5d183` (full translation => constant or injective; trichotomy). C3 has no lossy projection and does not claim propagation under full translation; it is Class I by construction (the relation vector propagates only under translation by factor-base elements, which is exactly index calculus). The rigidity theorem does not constrain it. Not a rigidity violation, and not a restatement of it.
- `IDEA-20260901-863e36` (propagation is a property of a projection paired with an operation set; lossy objects are block systems of <Sigma>; the cost law is the cost of canonicalising an orbit). C3 uses no quotient and no Gamma-orbit canonicalisation, so the "one open number" of that record does not exist for it. Not engaged.
- `KN-OPEN-020` (bounded-degree algebraic factor bases over generic prime-field subgroups are scoped out with charged costs; open class = high-degree, implicit-membership or target-dependent). Scope is F_p. C3's base is the F_2-subspace of KR-IC-73db3f (membership is F_2-linear after Weil restriction), described to the lattice by a size inequality deg x < l. In the record's vocabulary this is the implicit-membership / size-window class, the non-Archimedean twin of the Archimedean window of IDEA-20260808-486ae2; it is not the scoped-out bounded-degree algebraic class (whose Bezout bound |FB| <= 3d is an F_p statement). Charged costs C3 must still carry: description (trivial: the box), membership (a degree comparison), relation (lattice reduction per attempt), descent and linear algebra (2^{2l} for the unfolded base), memory.
- `KN-FIND-ffe1df` Theorem C (an exactly sum-compatible bucket index on E(F_p) is a surjective homomorphism onto a group of order dividing N, impossible for prime N, 1 < M < N). It is about Wagner-tree quotient indices; C3 has none. Not engaged.

**What the notation change does and does not hide.** The factor base and the operation set are the incumbent's; only the solver changes, and no recorded rigidity theorem constrains solvers. The demand side is the Class I mean-yield conservation identity of `KN-FIND-007` (opened: for any factor base of size B in a group of order N, the mean number of size-m multisets summing to a target is C(B+m-1, m)/N, whatever the base), i.e. P(decomp) = 2^{ml-n}/m! for B = 2^l; C3 re-derives it with p -> 2^n and does not escape it. `LEAD-ICE-generic-oracle-arity-cost-floor` records the matching product law (relations x targets x oracle = m 2^n). So the pair is not new arithmetic; the only new object is the oracle, and the oracle's supply side (reach) is the one number the prime lead also needs.

---

## 5. Quantitative cross-check of the candidate's arithmetic (produced here: arithmetic only)

n = 131, m = 4: D = 2^{m-1} = 8, ceiling m*l < 131/8 = 16.375 bits; demand (m-1) l > n/2 gives l > 131/6 = 21.83, i.e. m*l > 87.33; LA 2^{2l} < 2^{n/2} gives l < 32.75. Gap in m*l: 87.33 - 16.375 = 70.96 bits, matching the candidate's "about 71". Including the m! = 24 factor (4.58 bits) in the demand, l > 23.36 and m*l > 93.45, gap 77.07 bits; the candidate's figure is therefore slightly optimistic toward the attack, which is the right direction for a closure. These are model numbers (CLOSURE.md section 1 with p -> 2^n), not measurements.

---

## 6. Checks produced in this gate (scripts and outputs in `_c3_work/`)

1. `c3_s3_char2_check.py` -> `c3_s3_char2_check.out`: brute-force over GF(2^7) = F_2[z]/(z^7+z+1), curves y^2 + xy = x^3 + a x^2 + b (a in {0,1}, 6 random b each), random point pairs: S_3 = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + b vanishes on (x(P), x(Q), x(P+Q)) in every sampled triple (3,543 triples in the saved run, 0 failures; 3,544 / 0 in an earlier run). This fixes the binary S_3 used below.
2. `c3_corner_char2.py` -> `c3_corner_char2.out`: Semaev chain over Z lifted from that S_3 via exact Sylvester determinants, reduced mod 2 (resultant commutes with reduction at fixed formal degree). Output (verbatim):
```
S_4 (char 2): terms 24 per-var degrees [4, 4, 4, 4] t= 0.1
S_4 corner x1^4x2^4x3^4 (x4,b parameters): [((), 1)]
S_5 (char 2): terms 729 per-var degrees [8, 8, 8, 8, 8] t= 6.4
S_5 corner (x1x2x3x4)^8 coefficient list (x5,b parameters): [((), 1)]
```
(full file in the work directory; S_3 expands to the 5 monomials x1^2x2^2 + x1^2x3^2 + x2^2x3^2 + x1x2x3 + b.) The same file also prints the distinct x-monomial supports (verbatim): `distinct x-monomial supports (char 2): S_3 in x1,x2,x3 = 5 (of 27); S_4 in x1..x4 = 24 (of 625); S_5 in x1..x5 = 729 (of 59049)`.
Reading: the corner coefficient required by the candidate's Lemma B premise is the constant 1 for S_4 and S_5 in characteristic 2 (and for S_3, visible from the formula), independent of b and x_R. Per-variable degrees 2, 4, 8 = 2^{m-1} for S_{m+1}, as the candidate assumes. The supports are far sparser than the prime-field ones recorded in the repo (S_3 5 vs 13 of 27; S_4 24 vs 439 of 625); that does not affect a corner-based ceiling, but it does affect any tree cell (w > 0). Note the all-unknown corner of S_4 in four unknowns is absent (empty list), as expected for a block without a full corner.
3. Not run: the candidate's step (ii) (Popov-form planted-root probe at n = 31). Not part of the gate; no outcome of it is reported.

---

## 7. Structured conclusion

- verdict: `duplicate_of_lead` (lead: LEAD-ICP-coppersmith-smallroot-semaev), with the scope note that the binary F_2[z] cell is unevaluated
- N1: same engine class as one open lead (prime-field only); no closed lead's obstruction is left unanswered (the Frobenius-orbit obstruction is not escaped, as the candidate states).
- N2: no KR row is the mechanism; the factor base is KR-IC-73db3f; the univariate F[z] Coppersmith theorem is published (Cohn-Heninger, retrieved); no source for the composition found (3 searches).
- N3: no ledger record is the object; the prime twins are listed.
- N4: Class I pair; not a rigidity result in new notation; engages none of the four recorded results.
- Open items for the candidate (each is a scope, not a refutation): (1) tree cells (w > 0) are outside the corner lemma and binary supports are 5 / 24 / 729 terms, so state the closure as w = 0 only or compute the tree cells; (2) report the lattice dimension and size of S_{m+1} as costs even if the ceiling binds first; (3) the predicted closure (gap about 71-77 bits at ECC2K-130, m = 4) is a prediction until the F_2[z] probe is run.
- Prediction (labelled): closure of the w = 0 polynomial-lattice class at ECC2K-130; nothing in this gate measures it.


---

## Appendix A. Raw output, tools/lead_atlas.py --match (N1)

Run from /Volumes/SSD990-2/crypto-autoresearcher with the three LEAD_ATLAS_* variables set as instructed; python3 -B. Columns: score, lead id, disposition, title.

### A1. phrasing 1
```
$ python3 tools/lead_atlas.py --match "function-field corner lemma: F_2[z] Popov-form Coppersmith decomposition with polynomial-basis subspace factor base"
   21  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   19  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   14  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   12  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
   12  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
```

### A2. phrasing 2
```
$ python3 tools/lead_atlas.py --match "lattice reduction over binary polynomials as a point-decomposition solver for ECC2K-130"
   12  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   11  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    8  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
    8  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    8  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
```

### A3. phrasing 3
```
$ python3 tools/lead_atlas.py --match "an oracle that never writes the descended ANF escapes the writability boundary but its reach is below n/2^{m-1}"
   10  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    9  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    7  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
    6  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
    6  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
    5  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    5  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
    5  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
```

### A4. phrasing 4 (my own additional phrasing)
```
$ python3 tools/lead_atlas.py --match "polynomial lattice Coppersmith Howgrave-Graham F_2[z] Semaev summation polynomial decomposition polynomial basis"
   19  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   17  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   14  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
   14  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
   13  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
   12  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   12  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
   12  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
```

## Appendix B. Raw output, tools/build_frontier_map.py --match (N2)

### B1. phrasing 1
```
$ python3 tools/build_frontier_map.py --match "function-field corner lemma: F_2[z] Popov-form Coppersmith decomposition with polynomial-basis subspace factor base"
KR-IC-73db3f  score=12  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
```

### B2. phrasing 2
```
$ python3 tools/build_frontier_map.py --match "lattice reduction over binary polynomials as a point-decomposition solver for ECC2K-130"
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5765d2  score=6  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-889857  score=6  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-18cc42  score=6  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-IC-791cb7  score=5  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=4  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-955fd6  score=4  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

### B3. phrasing 3
```
$ python3 tools/build_frontier_map.py --match "an oracle that never writes the descended ANF escapes the writability boundary but its reach is below n/2^{m-1}"
KR-RHO-13bf67  score=3  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-791cb7  score=2  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-fbdb61  score=2  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-RHO-fb88e6  score=2  [known_mechanism/proven]  Negation map: sqrt(2) gain and fruitless cycles
    sources: KN-LIT-074c32, KN-LIT-c8e485, KN-LIT-5b238b, KN-LIT-a5c59c
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5a43e5  score=1  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-0528e7  score=1  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
```

### B4. phrasing 4
```
$ python3 tools/build_frontier_map.py --match "polynomial lattice Coppersmith Howgrave-Graham F_2[z] Semaev summation polynomial decomposition polynomial basis"
KR-IC-5a43e5  score=17  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-1fcdbc  score=12  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-955fd6  score=12  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5931ee  score=9  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5765d2  score=8  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-889857  score=8  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
```
