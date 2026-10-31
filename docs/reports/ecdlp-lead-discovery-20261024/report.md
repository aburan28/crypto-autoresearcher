# ECDLP lead discovery, 2026-10-24: prime-field index calculus first

Session report for RQ-ECDLP-361f3a (propose-ideas, lead-discovery round).
Every statement below is labelled proposed, derived, measured (by whom) or
independently verified. Nothing in this report was approved, dispatched or run
as an experiment by this session (hard rule 3).

## a. Orientation

- **Atlas brief (live tools, run from the CAR root at the commits below):**
  `ECDLP lead atlas (knowledge/leads/ecdlp/, reviewed 2026-10-24): 147 leads, 72
  closed with a named obstruction, 51 open with a decided next step, 16 blocked,
  8 unexamined. 2049/2078 ECDLP ledger records mapped to a lead. Changed since
  the review: crypto-autoresearcher: 146 paths; crypto: 16 paths; cryptanalysis:
  32 paths; ecc-challenges: 3 paths.`
- **Delta status:** `--delta` lists 201 watched paths (54 decisions
  DEC-20261018..24, 19 CZLIFT/ICPERF/PEXT/SEMAEV hypotheses and evidence, 29
  ideas IDEA-20261018..24, 12 findings/open problems, 19 problem records in CAR;
  16 crypto paths; 32 cryptanalysis paths; 3 ecc-challenges paths). They were
  folded as **proposed row diffs** (section b and `FOLD.md`), not applied, and
  the review stamp was left alone (hard rule 3; AUD passes ask for diffs).
- **Commits worked at:** crypto-autoresearcher `ab0609ebee` (origin/main at
  17:13 PDT; branch `lead-discovery/20261024-mythos-ecdlp`); crypto
  `5cb553810e` (origin/main, detached worktree); cryptanalysis `c5aa7b39b`
  (origin/main, detached worktree); ecc-challenges `df8cd52` at the first fetch,
  `86f8a57` by the end of the session; crypto-lean: **not checked out** on this
  host (no Lean imports were taken from it).
- **Research question:** RQ-ECDLP-361f3a (new; minted with
  `tools/allocate_id.py`, `--check` OK).
- **Tools:** live (`lead_atlas.py --brief/--delta/--coverage/--check
  --strict-paths/--render/--match`, `build_frontier_map.py --out/--match/--check`,
  `obstruction_registry.py --unexamined/--debt`, `build_ledger_index.py`,
  `validate_ledger.py`, `allocate_id.py`), not a snapshot.
- **Baseline read (crypto, origin/main, read by a delegated reader and
  spot-checked):** Table B prime ladder fp10..fp24 at S_IC/S_rho 5.47x (log2 r
  11.9) to 13.5x (23.4), validated 13/13, no sealed bound on any Table B row;
  sealed prime toy IC bounds `ECBND1h93b7a9d5c187` (ic.pipeline
  mitm:negation_folded, alpha 0.8407 [0.6459, 0.9528]) and `ECBND1h9879c0aa348f`
  (subtract, alpha 1.0054 [0.8805, 1.0769]) against `rho.negation`
  `ECBND1h9896c8176a62` (alpha 0.4545 [0.3876, 0.5927]); "Prime curves have no
  algebraic oracle in ecbench"; Koblitz Table A at rule v8: rho 4.67-18.07x
  faster cold at n = 41..61, no sealed Koblitz IC bound (all six inadmissible);
  no end-to-end IC row on the m = 83 gate curve.

## b. Audit table

Full per-lead record: `AUDIT.md` (seven family audits, every finding quoting
the row's obstruction.statement or next_action and an evidence path). Fold of
the 201 changed paths: `FOLD.md`. Counts (findings that propose a change; "no
change" rows stay in the files):

| family | leads | findings | Lean target statements (AUD-3/4) |
|---|---|---|---|
| generic | 26 | 25 | 7 |
| ic-binary | 21 | 21 | 8 |
| ic-engine | 19 | 23 | 4 |
| ic-prime | 24 | 28 | 7 |
| transfer | 21 | 30 | 4 |
| structure | 17 | 17 | 9 |
| exotic | 19 | 16 | 7 |
| **total** | **147** | **160** (AUD-1 21, AUD-2 52, AUD-3 21, AUD-4 55, AUD-5 9, AUD-6 2) | **46** |

**Fold (section a):** 197 of 201 paths read; 182 advance an existing lead (row
edits proposed in `FOLD.md`), 15 are not about ECDLP (coverage `NONE`), 4
unclear; **6 new mechanisms** no lead covers, proposed as new rows for the
Coordinator (not filed here because each needs its own `--match` and criteria
block): `LEAD-ICP-fp4-gaudry-d4-ladder` (IDEA-20261018-2c37f5),
`LEAD-TRF-cubic-ghs-genus3-hyperelliptic-2lp` (IDEA-20261018-670088),
`LEAD-ICP-pkm-tower-algebraic-oracle` (14 `research/pkm_*` directories cited by
no lead), `LEAD-TRF-prime-degree-ghs-genus-floor` (GOAL-PEXT-4a1d6b),
`LEAD-EXO-koopman-transfer-operator` (KN-OPEN-010), and
`LEAD-TRF-torsion-section-digit-fourier` (KN-OPEN-d3a6f0, split from
LEAD-TRF-padic-canonical-section). Two fold rows propose disposition changes
on LEAD-TRF-padic-canonical-section (DEC-20261023-2e7447 conditional reopen;
DEC-20261023-36b4f0 confirmation).

**Disposition changes proposed (21) and their adversarial verification (3
skeptics each, majority rule):**

| lead | pass | proposed | verification |
|---|---|---|---|
| LEAD-RHO-non-automorphism-equivalence | AUD-5 | the queued proof target is too weak to close the lead; sharpen the first step | **survives** (3 votes) |
| LEAD-ICE-chained-semaev-dreg-vs-semiregular | AUD-4 | KR-IC-fbdb61 already says semi-regular predictions do not describe descended systems, so only the block/topology-matched null is a valid co-arm; rewrite the step | **survives** (3 votes) |
| LEAD-RHO-cheon-deployed-applicability | AUD-4 | a bound without factorisation decides the discriminator | refuted |
| LEAD-ICB-factor-base-subspace-choice | AUD-1 | revisit trigger fired for the product-profile property | refuted |
| LEAD-ICB-tau-horner-chain | AUD-4 | a counting identity decides the m! accounting before the run | refuted |
| LEAD-ICE-sat-xor-pdp-oracle | AUD-4 | recorded counts already exclude "priced S/rho below 1 across the band" | refuted |
| LEAD-ICE-first-fall-degree-assumptions | AUD-4 | the counterexample branch is realised on a finite model (Lean certificates) | refuted |
| LEAD-ICP-lattice-ic-relation-construction | AUD-4 | two of three routes reduce to standing obstructions | refuted (the evidence path is a proposal report, not a deciding record) |
| LEAD-TRF-padic-canonical-section | AUD-1 | the clause "any non-homomorphic section recovers d only at the random 1/p rate" is recorded false by DEC-20261024-23d64d; split the row, keep the homomorphic/formal-log clause closed (kind theorem via KN-FIND-7e2b94) and open the digit-character channel | **survives** (3 votes; all three skeptics give the same split, see PROPOSED-DIFFS.md 7) |
| LEAD-TRF-padic-canonical-section | FOLD | closed_obstructed -> open_next_step on DEC-20261023-2e7447 (NA-4 successor) | **survives** (3 votes; corrected: add the next_action the validator requires, cite DEC-20261024-23d64d N-3(1)) |
| LEAD-TRF-padic-canonical-section | FOLD | DEC-20261023-36b4f0 confirms the closure for the formal-log clause | **survives** (2 of 3; corrected: keep closed, narrow the statement to EV-CZLIFT-ad28f5's scope, kind proof not theorem) |
| LEAD-TRF-small-genus-cover-general | AUD-5 | the title scope "other configurations over F_{q^3}" exceeds the x-line proof; narrow the title and split the non-x-line degree-2-function / Jacobian-existence routes into an open row | **survives** (3 votes; corrected: frame as narrowing to the proof's scope, which the row's own revisit_when already names) |
| LEAD-EXO-augmented-oracle-ggm | AUD-2 | the theorem closure (Shoup via GGM simulability) forecloses coordinate-reading oracles it does not reach; split: keep closed for oracles whose answers are computable by group operations and equality, open the coordinate-reading group | **survives** (3 votes; same split from all three) |
| LEAD-EXO-miller-pairing-cocycle | AUD-4 | a derivation (T-KUMMER, in `AUDIT.md`) decides the correlation part of the queued step; commit it as a reviewable record first, then run the K1/K2 identity check | **survives** (2 of 3; corrected: keep open_next_step, anchor the Weil/Deligne input on a KN-LIT row) |
| LEAD-ICP-gfp5-odd-char-cover | AUD-4 | paper theorems already in crypto (genus floor g >= 33 at n = 5) decide the blocked step | refuted (2 of 3: the census is committed but does not price the non-x-line routes the row names) |
| LEAD-ICP-xline-symmetry-special-j | AUD-5 | dominated by LEAD-STR-special-j-ic-semaev | refuted (that row is itself open; nothing decided) |
| LEAD-ICP-construction-normal-form | AUD-5 | methodology row; dominate it by LEAD-EXO-methodology-instruments | refuted (no committed record decides it) |
| LEAD-TRF-global-lift-small-height | AUD-1 | both load-bearing clauses revised by CZLIFT records; closed_known -> closed_obstructed (proof for coverage) | refuted (2 of 3: DEC-20261024-23d64d still has `archived_by: null`; wait for the archive) |
| LEAD-TRF-cover-catalog-jacobian-transfer | AUD-4 | every catalogued map is same-field, so SO-COVER decides it | refuted (the assessment README classifies, it does not decide) |
| LEAD-TRF-miller-cocycle-nonhom-transfer | AUD-5 | duplicate of LEAD-EXO-miller-pairing-cocycle | refuted (no committed record; propose `related`, not closed_dominated) |
| LEAD-TRF-teske-secret-isogeny-trapdoor | AUD-4 | a pigeonhole bound caps the occupancy meter at e/(e-1) | refuted (H-ECTD-e88346 is an approved hypothesis, not a result; the bound is a Lean target, not a closure) |

Net: **8 of 21 proposed disposition changes survive** three skeptics each; 13
are refuted, in every case because the cited record is a plan, a proposal, a
classification or an un-archived decision rather than a deciding record. The
8 survivors are written as proposed diffs with the skeptics' corrected wording
(`PROPOSED-DIFFS.md`, items 7-12); none is applied.

**Prime-field findings that change what to do next (ic-prime, ic-engine; the
proposer's wording, with the evidence path in `AUDIT.md`):**

- AUD-3, `LEAD-ICP-extension-field-embedding`: a structural lemma replaces the
  cost model: for odd n, `{P in E(F_{p^n}) : x(P) in F_p}` **is** `E(F_p)`
  (y^2 in F_p forces y in F_p), and for even n it is `E(F_p)` plus the twist;
  the subfield base is the original group, so the embedding buys nothing by
  construction. This is stronger than the exponent inequality proved in
  `ExtensionFieldEmbedding.lean` and is the better Lean target (statement in
  `AUDIT.md`; not written this session).
- AUD-3, `LEAD-ICP-generic-table-decomposition` and
  `LEAD-ICE-generic-oracle-arity-cost-floor`: the m <= 3 part of the "theorem"
  is a two-term cost model; the audit states the exact (constant-level) AM-GM
  form `a/B^(m-1) + B^2 >= ((m+1)/(m-1))((m-1)a/2)^(2/(m+1))` with
  `a = m! N T`, sub-rho only if `T = O(N^((m-3)/4))`. The exponent form is
  proved in `ArityOracleThreshold.lean`; the AM-GM form with constants is the
  natural follow-up target.
- AUD-1, `LEAD-ICE-generic-oracle-arity-cost-floor`: revisit clause (b), "a
  non-generic yield exceeds C(B+m-1,m)/N on average", **cannot fire** because
  KN-FIND-007 proves the mean is exactly that for every base of size B; rewrite
  it as a target-sampling rule with O(1) GAE per sampled target and a
  conditional yield above the mean (this is the H1 escape in the threshold
  theorem's own terms).
- AUD-2, `LEAD-ICP-generic-table-decomposition`: three forecloses phrases cover
  coordinate-reading oracles the generic bound does not reach; qualify them
  ("with a generic oracle, or at m <= 3 with any oracle under the AUD-3 lemma").
- AUD-2, `LEAD-ICP-representation-subset-sum`: scope "any representation/filter
  variant" contradicts the row's own revisit_when; restrict to filters that use
  only group operations and equality of encodings.
- AUD-2, `LEAD-ICP-algebraic-membership-factor-base`: the prime-field theorem
  is cited by unqualified phrases ("multiplicative subgroup factor base x^B = 1")
  that block the binary variant IDEA-20261018-329d0a; qualify "over F_p".
- AUD-2, family misfilings: `LEAD-ICP-icperf-writability-boundary` (binary
  scope, filed in ic-prime; and its chained-Semaev phrase blocks the very
  representation its revisit_when names), `LEAD-ICP-icperf-binary-pdp-solver`
  (overlaps LEAD-ICE-sat-xor-pdp-oracle), `LEAD-ICP-retained-setup-online`
  (Koblitz n61/n83 rows duplicating LEAD-ICB-retained-setup-online; no
  prime-field row exists).
- AUD-4, `LEAD-ICP-residual-partial-relations`: the exponent is already derived
  (H-PFDR-cb9606): work ~ N^((1+beta)/2), LA balance at beta = 1/3 gives 2/3
  against the fitted 0.841 [0.646, 0.953]; add "fit against 2/3" to
  discriminates (this is the k = 1/2 point of the threshold theorem: an oracle
  of order 1/2 at m = 2 gives 2/(m+1-k) = 2/2.5 = 0.8, so the derived 2/3 needs
  the large-prime accounting the model does not have; both numbers stay above
  rho).
- AUD-4, `LEAD-ICP-prime-ic-constant-engineering`: the validation-gate half of
  the next step is done (LEADERBOARD lines 49-56 mark Table B validated;
  DEC-20261023-122e32 accepted EXP-ICPERF-6c546e); compute the counted batching
  gain from calibration.json and run the paired arm against both the incumbent
  recipe and a batched-rho reference.
- AUD-4, `LEAD-ICP-coincidence-harvest-structured-base`: EXP-PFDR-bb0d26 has run
  (DEC-20261022-9aec2b: O-NULL on 44 of 45 powered cells, max |kappa-1| =
  0.0414, planted kappa >= 1.2885 detected); drop the "run it" clause, add its
  independent review and the a0830c rungs at 32/36 bits.
- AUD-4, `LEAD-ICP-coppersmith-smallroot-semaev`: no strategy-independent reach
  bound is known, so the queued shift-polytope computation is the decider; absorb
  IDEA-20261015-9defe9 (Newton-target shifts) into it. The lattice scout
  (section c) adds the staleness flag that the row quotes numbers superseded by
  CORR-20261024-b2a799 (eps(S_3) = 0.2803, margin -0.6086 at (4,2)).
- AUD-4, `LEAD-ICE-charged-toy-ic-exponent-vs-rho`: measure the O5 oracle's
  per-query cost slope before building the pipeline; slope >= (m-3)/4 at every
  arity closes the lane on exponents (the same conclusion as PROPOSED-DIFFS.md
  section 2, reached independently by the audit agent from KN-FIND-007).
- AUD-4, `LEAD-ICE-gpu-rootfind-oracle`: an Amdahl floor from the validated
  Table B phase shares puts the matched GPU ratio at >= 1 at fp12, fp16, fp18,
  fp20 even with a free relation phase; restrict the session to fp10, fp14,
  f2m18, f2m21 and map kernel efficiency below h_min to closed_obstructed
  (cost_model).
- AUD-4, `LEAD-ICE-relation-graph-rank-large-prime` and
  `LEAD-ICE-semaev-yield-model-coset-typing`: KN-FIND-007 forces the gain to
  come from the oracle side (LA is < 0.5% of Table B S); the typed-base gain is
  (m-1)!, not m!, at matched per-variable dimension and loses m^m at matched
  total base.
- AUD-4, `LEAD-ICE-hybrid-guess-determine-l7`: both E8 outcomes stay above rho
  in column touches (+8.43 bits constant k; +30.7 to +58.3 growing k); gate E8
  on the unmeasured touch-to-GAE conversion K.
- AUD-2, scope qualifiers needed on `LEAD-ICE-semaev-cover-monodromy` (F_p, p >
  3 only), `LEAD-ICE-boolean-f4-f5-f6-engines` and
  `LEAD-ICE-semaev-chain-cost-model` (binary, Semaev 2015 cost model), and
  `LEAD-ICE-descent-closure-degree-at-scale` (random subspaces only; the
  polynomial-basis V of KR-IC-73db3f was never run).

**Binary / Koblitz (ic-binary, 21 findings; `AUDIT.md`):** the family audit
found eight short-proof candidates (the conservation lemma LT-1 used by three
rows, the tau-Horner bijection LT-7, the cofactor-filter lemma LT-6, the
writability/alpha inequality LT-2 "there exists l with n + l(1 + alpha - m) <
n/2 iff alpha < m/2 - 1", the affine-invariance of degree-d spans LT-3, the
scalar-fixed-point lemma LT-4, the LA-share bound LT-5); its only proposed
disposition changes (factor-base-subspace trigger, tau-Horner counting) were
refuted by the skeptics, so the binary rows stand as they are.

**Cross-session input, not verified here:** a parallel desk review on this
host (memory note `ecdlp-factor-base-arity-review-2026-10`, 2026-10-24) reports
four gaps the repos do not record: no algebraic solving degree exists at m >= 5
in any repo (first chained cells (5,2,11), (5,3,13), (6,2,11) fit the 64-variable
engine); the literature's degree-4 flat was measured at large overdetermination
Delta = n - m*l while the repo's rise at l = 7 is at Delta about 0 (a Delta-sweep
at fixed (m, l) is its top-ranked experiment); Galbraith-Gebregiyorgis 2014
Experiment 2 (m = 4, l = 4 binary Edwards invariants) was never built; the
symmetric e_k presentation above the l = 6 crossover was never run. These are
recalled from the note, not from a committed record, and belong to the
ic-binary and ic-engine next_actions once checked.

## c. Graveyard

Full record: `GRAVEYARD.md`; dossiers and raw gate output: `scouting/`.
Twelve outside fields were scouted (coding theory and ISD, lattice small-root
methods, SAT/XOR and planted systems, additive combinatorics, commutative
algebra, p-adic and tropical geometry, arithmetic statistics, query and
communication complexity, HPC constants, algebraic geometry of covers, the
polynomial method, algorithmic number theory). Screened count: **47 candidates
proposed after 152 scout-level kills** (every kill with its reason in
`GRAVEYARD.md` section D). Gate outcome for the 36 candidates that received a
verdict: **8 killed (7 N1 duplicates of a lead, 1 N2 known result), 28 judged
`advances_lead` (a sharper step on an existing open lead), 0 new mechanisms.**
Eleven candidates have no gate verdict (the gate agents hit the session limit
twice) and are listed as unexamined. No skeptic votes were obtained (every
refutation agent failed on the limit), so nothing below is independently
refuted or confirmed; the lead author's own reading is marked as such.

| candidate | killed by | obstruction kind | forecloses phrases | record needed |
|---|---|---|---|---|
| Riemann-Roch excess lemma: no AG-code decoder or ISD algorithm is a point-decomposition oracle | N1 (duplicate of LEAD-EXO-ideas-corpus-algebraic-transforms; FINDING-PF-IC-001 P1539, rejected ideas 013/014/130/...) | proof (the lead's) | AG code decoding as decomposition; list decoding the elliptic code; syndrome decoding for ECDLP | none new; the lead's record |
| Function-field corner lemma: F_2[z] Popov-form lattice decomposition on ECC2K-130 | N1 (same mechanism as LEAD-ICP-coppersmith-smallroot-semaev, binary arm) | cost_model | polynomial-lattice small roots of S_m over F_2[z]; Popov form decomposition; function-field Coppersmith | that lead's reach record |
| Exact tree-like Res(xor) optimum of UNSAT descended PDP instances | N1 (LEAD-ICB-decomposition-encoding-and-sat, closed; candidate does not escape its measured alpha ~ m) | measured | parity decision tree for PDP; tree-like Res(xor) refutation size; UNSAT core size of descended S_m | the lead's EV records |
| Popcount-filtered exact refutation-degree meter for squaring and Chebyshev towers | N1 (LEAD-ICP-algebraic-membership-factor-base; residual item is IDEA-20261018-e0857e) | theorem | refutation degree of tower bases; Chebyshev tower factor base; squaring tower membership | KN-FIND-007 / the lead's record |
| Valuation-triviality lemma: p-adic tropical initial-form decoder for a Semaev system | N2 (KR-IC-5931ee consequence; frontier delta 0) | literature | p-adic valuation decoder for Semaev; tropical initial forms of S_m; Newton polygon decomposition | KR-IC-5931ee |
| (tau, mu) admission region for IC decomposition oracles, find-one vs list-all | N1 (quantitative complement of LEAD-ICE-generic-oracle-arity-cost-floor; now covered by IDEA-20261024-a2b05d's theorem) | proof (model) | oracle admission region; find-one versus list-all oracle; tau-mu exponent plane | TASK-20261024-9fbb0f |
| One FFT per statistic: heavy Fourier coefficient and autocorrelation for the Miller cocycle | N1 (LEAD-TRF-miller-cocycle-nonhom-transfer already holds both halves) | n/a (open lead) | heavy Fourier coefficient of a non-homomorphic transfer; Goldreich-Levin on the Miller primitive; autocorrelation of U(kP) | the lead's first step |
| SAT/XOR oracle decided by the break-even conflict price (HPC scout's version) | N1 (the repricing clause of LEAD-ICE-sat-xor-pdp-oracle's own next_action; merged into IDEA-20261024-741c49) | cost_model | conflict pricing of the SAT oracle; ns per conflict versus ns per group addition; break-even conflict weight | IDEA-20261024-741c49 |

Scout-level kills worth recording because they close routes a future session
would otherwise retry (all in `GRAVEYARD.md` D, with the scout's argument):
every list-decoding, ISD, folded-code, interleaved and quasi-cyclic decoding
route (agreement equals the dimension; collisions reduce to the group-law MITM;
no small-order translation on a prime-order group); every Coppersmith variant
beyond the corner lemma (Jochemsz-May, Herrmann-May, Bauer-Joux, Kannan
embedding, BKZ at any dimension, rank-r GAP lattices, Farey bases,
Bombieri-Pila); sum-product, incidence, Kloosterman/Weil/Burgess and
Balog-Szemeredi-Gowers routes (vacuous below sqrt(p) or above the break-even);
overlap-gap, low-degree, k-XORSAT threshold, cutting-planes and lifted Res(xor)
bounds (wrong model or gadget-composed formulas); Mordell-Weil CVP, Weil
polynomial enumeration for Jacobian carriers and EDS ratio stripping; and every
binary/Koblitz coding-theory route (reduce to SO-QSP, rank-metric K7 or
SO-FROB).

## d. Survivors, ranked

No candidate opens a new lead; the six carried forward are sharper first steps
for existing open leads, filed as IDEA records with `prior_art.lead` set,
criteria blocks and draft protocols in their notes (section g). Ranking by
P(first step rules it in) x gain / cost, with each factor the lead author's
estimate (unverified by a skeptic; the dossier's own self-kill risk is quoted):

| idea (advances lead) | tier | claim type | P(rule-in) | gain if it does | cost of the step | first step |
|---|---|---|---|---|---|---|
| IDEA-20261024-741c49 conflict-priced 5a band for the native-XOR SAT oracle from the recorded ecbench counters (LEAD-ICE-sat-xor-pdp-oracle; ECC2K-130 family, n = 17, m = 2) | I | exact_computation + measured | the arithmetic stands (every number traced to `research/ecbench_sat_pdp_20261009/`); the ORDER is **unresolved** under crypto/AGENTS.md 5a: SAT/strong-rho is 0.854 [0.825, 0.883] at w = 0 but 7.34 at w = 0.1 and 51.0 at w = 1, break-even w* = 1/458 = 2^-8.84, so the lead's sub-rho branch holds only if a CDCL+XOR conflict costs under 1/458 of a group addition; 0.3 that a qualified-host calibration lands below that | decides the one binary row with a sub-1 unpriced ratio; removes a planned ns-per-conflict calibration only if the calibration itself is the deciding step | zero for step (i); step (ii) needs a re-freeze (PROTOCOL-4: n = 17 and 23, l-ladder 8-12, conflict budget 300,000, since n = 19 and 29 degenerate and n = 23 trips the frozen 20,000 budget) | file the band computation as the repricing; an admitted ns-per-conflict calibration on a qualified host; the PROTOCOL-4 re-freeze |
| IDEA-20261024-1b76a4 corner lemma: strategy-independent Howgrave-Graham ceiling for single-equation lattice decomposition, plus the addition-tree initial-ideal ceiling and the tropical corollary (LEAD-ICP-coppersmith-smallroot-semaev) | X (rule-out) | theorem (conditional on H1: no structurally short vector without a determinant reason) | 0.7 for the single-equation closure; 0.4 that the addition-tree cells also close | closes the last open prime-field small-root lead by proof instead of a reach computation; a Lean target | about 1 day review, minutes of probes | independent review of the lemma; extend the corner probe to the rank-2 GAP form; cuso on S_3 |
| IDEA-20261024-e65d46 characteristic-p IPS subset-sum degree floor and the polynomial-calculus degree bound for digit/box presentations (LEAD-ICP-digit-presentation-solving-degree) | X (rule-out) | theorem (conditional on H1: Wilson's rank theorem transfers to F_{p^d}, p > s) | 0.7 for the direct digit branch; the chained cell stays open | closes the digit-presentation escape of the Semaev solving-degree closure; a Lean target | 1-2 days (proof + exact PC-degree checker), minutes of compute | review the five-lemma proof; retrieve Wilson 1990; run the exact checker at s = 6..14 |
| IDEA-20261024-5bbcda writability floor for the expanded reduced binary-digit presentation via uniqueness of multilinear representations (LEAD-ICP-digit-presentation-solving-degree) | X (rule-out) | theorem (rigorous at m <= 4) + exact_computation (H-TOP at m >= 5; H4w certified by sampling at m = 6-8 only) | 0.5 (the floor needs H2; m = 5 at 128 bits is undecided at +1.1 bits; m = 9-14 rests on unverified H3) | a cost floor on one presentation, independent of any solver; it does not close the SO-ALGFB escape | about 1 day for the sampler; medium compute (one coefficient costs about 2^(4m-1) point additions: 2.4-24 core-hours per m = 8 cell) | certify H4w by sampled coefficients at m = 6-8, 128/256 bits, 40 monomials per cell |
| IDEA-20261024-06f16f move Table B to the tau = 0 vertex: full m-fold signed sumset, one lookup per walked target (LEAD-ICP-prime-ic-constant-engineering) | I | measured | 0.35 (constants extrapolated from one m = 2 row; early-stop rank at m >= 3 unmeasured; "BSGS relabelling" reading must be excluded) | predicted 1.9-2.4x (m = 3) to 2.7-3.5x (m = 4) fewer GAE at fp24, i.e. the Table B distance 13.5x -> 5.6-7.1x, a Tier I end-to-end move if the paired ratio's lower CI bound is above 1 at every band weight | 1-2 days Rust, under an hour of compute per panel | implement `mitm-full:m=3` in ic.pipeline; paired arm vs the incumbent at fp20/22/24/28 with matched rho and A/A |
| IDEA-20261024-892d61 exact occupancy calculator: conservation, Markov ceiling, Paley-Zygmund floor (LEAD-ICP-isogeny-transported-relation-yield; also LEAD-TRF-teske-secret-isogeny-trapdoor, LEAD-ICE-decomposition-probability-audit) | I (instrument) | exact_computation | 0.8 that the exact tables reproduce the two run arms within noise | replaces 17 missing arms of EXP-ECTD-0cf008 by exact population quantities; a Lean target for the three inequalities | done (about 200 lines of C++); 6 s to 2 h per base | file popcov and the P29 exact table as a pre-registered prediction in the recovery amendment |

Four more gate-passed candidates are proposed as next_action sharpenings without
an IDEA record (section b's proposed diffs or `GRAVEYARD.md` B): the exact
all-target decomposition census from the log-domain spectrum
(LEAD-ICE-decomposition-probability-audit), the cofactor-coset counting law that
makes the volcano l = 2 yield effect 2-torsion bookkeeping
(LEAD-STR-class-representative-ic-selection), the Table B "rho denominator"
decomposition with a falsifiable 28/32-bit projection
(LEAD-RHO-matched-rho-calibration), and the Kummer-conductor / Weil-Deligne
bound for the Miller primitive (LEAD-TRF-miller-cocycle-nonhom-transfer).

Two corrections the record writers made to the lead author's first reading,
kept here because they change how the ideas are read: (1) the full-sumset arm
(IDEA-20261024-06f16f) is a **k = 0 oracle** (one lookup per walked target),
not a k = ceil(m/2) one; its exponent stays at m/(2m-1) > 1/2 only because the
B^m table build is charged, which is the arity-2 memory-coupling theorem of
`MemoryCouplingArityTwo.lean` generalised to arity m (proposed as that idea's
Lean target); and (2) the occupancy calculator (IDEA-20261024-892d61) settles
only the two occupancy contrasts of EXP-ECTD-0cf008, not all 17 missing arms;
its rank-prefix, interval, replay and transported-base-equality exit criteria
stay owed. The writers also found two crypto study directories cited by no lead
(`research/ic_triple_table_20260923`, `research/ic_triple_counted_20260923`),
an atlas gap for the next fold.

**What the round says about the prime-field path forward.** Every candidate
that survived the gates is either a closure (corner lemma, IPS degree floor,
writability floor, occupancy calculator) or a constant-level engineering step
(the tau = 0 sumset arm). Together with the threshold theorem (section f) the
prime-field picture is: the exponent question is open only for a decomposition
oracle of enumeration order k < (m-1)/2, every lattice, Groebner-on-digits, SAT
and enumeration route proposed in this round sits at or above the line by its
own dossier, and the measurable work is (1) the oracle-order census, (2) the
tau = 0 sumset arm against Table B, and (3) sealing the three closures as Lean
targets.

## e. Obstruction matrix and raw `--match` output

For IDEA-20261024-a2b05d (which advances a closed lead rather than opening one),
the raw gate output is in `gates/gates-arity-threshold.txt`; the top hits were
`LEAD-ICE-generic-oracle-arity-cost-floor` (24, 14, 24 on the three phrasings),
`LEAD-ICP-generic-table-decomposition` (20), `LEAD-ICE-rootfind-pairtable-oracle`
(20), `LEAD-ICP-coppersmith-smallroot-semaev` (17); frontier hits `KR-IC-5931ee`
(19), `KR-RHO-13bf67` (15); ledger hits IDEA-20260803-fa9839,
IDEA-20260808-2ef5c8, IDEA-20260829-b5a2c8, IDEA-20260830-3c0861,
IDEA-20260830-4ab603 (the two-term model lineage). Verdict: same mechanism as the
first hit; the idea upgrades its closure (AUD-3) and does not file a new lead.

## f. Lean status

![Arity / oracle-order threshold: cost exponent E*(m, k) against the generic 1/2 for both oracle semantics, with the sealed prime toy IC bounds and the atlas mitm exponents placed at their model order (editable source: render.py; nothing in the figure is a measurement produced by this session).](threshold-line.svg)

| theorem (file) | file or attempt dir | role | status | open bridges |
|---|---|---|---|---|
| `CryptoResearch.IC.ArityOracleThreshold` (19 theorems: `costAll_ge_small`, `costAll_ge_large`, `costAll_ge_one`, attainment x2, `small_threshold`, `large_threshold`, `free_oracle`, `linear_oracle`, `quadratic_oracle`, `mitm_never_sub_generic`, `exhaustive_ge_one`, `attemptsAll_le_attemptsOne`, `costAll_le_costOne`, `costOne_ge_small`, `costOne_small_attained`, `costOne_ge_enum`, `costOne_enum_attained`, `main_hyps_satisfiable`; controls `needs_H1..H4`) | `formal/CryptoResearch/IC/ArityOracleThreshold.lean`; target `formal/targets/ic-arity-oracle-threshold-20261024.yaml` (TASK-20261024-9fbb0f) | cost-model algebra (rule-out within the model H1-H4) | compiles under plain `lean` v4.35.0-rc1 / Mathlib 7fa22735: 0 errors, 0 `sorry`, every `#print axioms` = propext, Classical.choice, Quot.sound; **repository gate not run to completion** (problems/formal-lean-external-volume-eintr.md); `needs_semantic_review = true` | H1-H4 are hypotheses; no bridge to curve points, counts or finite sizes; the one-decomposition semantics for 1 < k is not interpolated (only k <= 1 and k >= 1 bounds) |
| `CryptoResearch.IC.MemoryCouplingArityTwo` (7 theorems + control) | `formal/CryptoResearch/IC/MemoryCouplingArityTwo.lean`; target `formal/targets/ic-memory-coupling-arity-two-20261024.yaml` (TASK-20261024-2be6ac) | cost-model algebra (IDEA-20260830-4ab603's correction) | same: compiles under plain `lean`, 0 errors, 0 `sorry`, standard axioms; gate not run | H5 (B^2 table) is a hypothesis; unstructured bases only |

| `CryptoResearch.IC.ExtensionFieldEmbedding` (AUD-3 upgrade for `LEAD-ICP-extension-field-embedding`, kind cost_model) | `formal/CryptoResearch/IC/ExtensionFieldEmbedding.lean`; target `formal/targets/ic-extension-field-embedding-20261024.yaml` (TASK-20261024-551bd9) | cost-model algebra | compiles under plain `lean` (see `checks/`); gate not run | H6 (Gaudry's heuristic cost p^(2-2/n+o(1)) on E(F_{p^n}), KR-IC-46d822) is a hypothesis |

**Derivation for the third target (source of its claim).** Embedding the
prime-field problem on E(F_p) (order about p) into E(F_{p^n}) and running
Gaudry's decomposition with the subfield base {x in F_p} costs, under H6,
p^(2-2/n+o(1)) for every fixed n >= 2 (KR-IC-46d822: q^(2-2/n) with q = p). The
reference is rho on the original group at p^(1/2). Claim: for every real
n >= 2, 1/2 < 2 - 2/n; equivalently there is no n >= 2 with 2 - 2/n <= 1/2, so
the embedding enlarges the problem faster than the subfield base helps, at every
extension degree. Control: without the hypothesis n >= 2 the statement fails at
n = 1 (2 - 2 = 0), which is the trivial extension and not an embedding, so the
degree hypothesis is load-bearing. Non-vacuity: n = 2 gives the exponent 1,
which is the LEAD row's own "p at n = 2". Proved in the file as
`gaudry_exponent_gt_half`, `embedding_never_helps`, `needs_degree_two`,
`main_hyps_satisfiable`.

Fidelity items (sheriff B3 a-e), all files: (a) statement paired with the
informal claim clause by clause in the file header and in
`IDEA-20261024-a2b05d.notes.md` sections 3 and 8, forall/exists order written out
in the IDEA's `quantifier_order`; (b) `main_hyps_satisfiable` in each file; (c)
no new computable definitions (the definitions are real-valued `max`
expressions; no `#eval` differential test applies); (d) no data enters; (e)
scope: real m >= 2, k >= 0, beta > 0, exponents only; never cited at any finite
size.

## g. Experiment specs awaiting approval (approved_by: null)

1. `specs/EXP-SPEC-oracle-order-census.md` - prime-field decomposition-oracle
   order census (fitted k per implemented oracle against the threshold line;
   positive controls with k = 1 by construction; matched rho.negation; A/A).
2. Draft PROTOCOL for each carried-forward idea's first step, in section 4 of
   its notes file (`ledger/proposals/<IDEA-ID>.notes.md`), with the criteria
   block in section 3: IDEA-20261024-1b76a4 (corner-lemma review, rank-2 GAP
   probe, cuso on S_3), IDEA-20261024-e65d46 (five-lemma proof review, exact
   polynomial-calculus degree checker at s = 6..14, three toy primes),
   IDEA-20261024-5bbcda (sampled-coefficient certification of H4w at 128/256
   bits), IDEA-20261024-741c49 (band computation from the recorded counters;
   PROTOCOL-3 re-run with the 0 / 0.1 / 1 GAE band), IDEA-20261024-06f16f
   (paired `mitm-full:m=3` arm against the Table B incumbent at fp20/22/24/28
   with matched rho.negation and A/A), IDEA-20261024-892d61 (pre-registered
   exact occupancy tables for the EXP-ECTD-0cf008 recovery amendment). All
   carry `approved_by: null`; none was compiled, relayed or run.

## h. Blockers (problems/ records)

- `problems/formal-lean-external-volume-eintr.md` (new): Lake/`lean` reads on
  the external volume fail intermittently with EINTR; the Lean gate could not be
  run to completion; the theorems compile under plain `lean` with retries.
- `problems/README.md` is held by Conductor task T-5065 (another session), so
  the index line for the new problem record is **not** added here; proposed line:
  `- [Lean/Lake file reads on the external APFS volume fail intermittently with EINTR, blocking the formal gate](formal-lean-external-volume-eintr.md) - open`.
- PR creation: the keyring token for github.com is invalid on this host; a
  fine-grained token supplied in chat authenticates (`gh api user` ->
  aburan28) but `gh pr create` returns "Resource not accessible by personal
  access token (createPullRequest)" (no pull-request write permission). The
  branch `lead-discovery/20261024-mythos-ecdlp` is pushed; the PR is opened by
  the user with `gh pr create` after `gh auth login -h github.com`, or from the
  compare page, with the body in the session summary.
- Conductor: task T-5083 holds the touched paths (epoch 7); further lease
  renewals were refused ("retry budget exhausted (4/4)").
- Pre-existing: `tools/validate_ledger.py` reports `FAIL: 104 new validation
  error(s)` on origin/main records (IDEA-20261003-*, IDEA-20261016-*,
  experiments/EXP-AES-14352a, EXP-ICPERF-*, ...), none naming this session's
  records (tracked by `problems/full-ledger-validation-errors.md`);
  `lead_atlas.py --check --strict-paths` reports 2 errors on
  `LEAD-RHO-pool-class-quotient` (ecc-challenges evidence paths that exist only
  on branch `claude/ecdlp-leads-analysis-l7f87y`, commit 1f49962; proposed diff:
  add `ref: claude/ecdlp-leads-analysis-l7f87y` to those two evidence entries, or
  merge that branch).

## i. Verdict lines

- LEAD-ICE-generic-oracle-arity-cost-floor (IDEA-20261024-a2b05d): advance | needs the repository Lean gate on a host without the EINTR fault, then a separate sheriff review, to decide the proof upgrade.
- LEAD-ICE-charged-toy-ic-exponent-vs-rho: needs the measured enumeration order k of the O5 oracle (oracle-order census spec) to decide.
- LEAD-ICP-generic-table-decomposition: advance (revisit_when sharpened to the threshold line); no disposition change.
- LEAD-ICP-extension-field-embedding (TASK-20261024-551bd9): needs the Lean gate to decide the kind upgrade; the audit's structural lemma is the stronger target.
- LEAD-ICE-sat-xor-pdp-oracle (IDEA-20261024-741c49): needs an admitted ns-per-conflict calibration on a qualified host (break-even 1/458 of a group addition) and the PROTOCOL-4 re-freeze to decide; the band is unresolved inside w in (0, 0.1), so neither branch is met today.
- LEAD-ICP-coppersmith-smallroot-semaev (IDEA-20261024-1b76a4): needs the independent review of the corner lemma and the rank-2 GAP probe to decide; predicted close (proof, conditional on H1).
- LEAD-ICP-digit-presentation-solving-degree (IDEA-20261024-e65d46, IDEA-20261024-5bbcda): needs the five-lemma proof review plus the exact PC-degree checker (direct branch, odd-order curves) and the H4w coefficient sampling at m = 6-8 (expanded presentation, rigorous at m <= 4) to decide; the chained cell and m = 5 at 128 bits stay open.
- LEAD-ICP-prime-ic-constant-engineering (IDEA-20261024-06f16f): needs the paired `mitm-full:m=3` arm against the incumbent at fp20-fp28 with matched rho, A/A and the band to decide; Tier I only.
- LEAD-ICP-isogeny-transported-relation-yield (IDEA-20261024-892d61): advance | needs the pre-registered exact occupancy tables filed in the EXP-ECTD-0cf008 amendment to decide.
- LEAD-TRF-padic-canonical-section, LEAD-TRF-small-genus-cover-general, LEAD-EXO-augmented-oracle-ggm, LEAD-EXO-miller-pairing-cocycle, LEAD-RHO-non-automorphism-equivalence, LEAD-ICE-chained-semaev-dreg-vs-semiregular: advance (row splits or sharper next steps proposed in PROPOSED-DIFFS.md 7-12, each verified by three skeptics); the Coordinator decides.
- Six proposed new rows from the fold (section b): needs their own `--match` runs and criteria blocks to decide; not filed here.

## Checks

| check | result |
|---|---|
| `python3 tools/validate_ledger.py` | FAIL, 104 pre-existing errors on origin/main (re-run after merging origin/main e5f46a5951 and again after filing the six scouted ideas: the same 104); 0 errors and 0 advisories name RQ-ECDLP-361f3a or any IDEA-20261024-* record of this session (every error line in `checks/validate_ledger_excerpt.txt`) |
| `python3 tools/lead_atlas.py --check` (plain) | PASS: `lead atlas OK: 147 leads ...; coverage 2056/2089 (33 unmapped)`; the 7 new ideas are mapped in `coverage.tsv` |
| `python3 tools/check_merge_hygiene.py --base origin/main` | PASS on the 27 touched paths (no conflict markers, no unparseable records, no identifier collisions) |
| `python3 tools/lead_atlas.py --check --strict-paths` | FAIL, 2 pre-existing errors (LEAD-RHO-pool-class-quotient evidence[4], [5]); 0 attributable to this session; without `--strict-paths` these are warnings and the check passes |
| `python3 tools/build_frontier_map.py --check` | PASS: `known-results map OK: 52 rows` |
| `lake build` / `AxiomAudit.lean` / `verify_formal_targets.py` | NOT RUN TO COMPLETION. `lake build` fails on `.trace` reads with EINTR; `verify_formal_targets.py` was run once (22:26-22:40 PDT) and stopped after 5 of about 90 targets because every receipt, including previously machine-verified Endosweep/Binstd targets, read `formalization_blocked` / `lake build failed` with EINTR in the build log, i.e. the gate measures the host fault here. Plain `lean` compile of all three new files: PASS (logs in `checks/`). The three new targets stay undischarged. |
