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
| LEAD-ICP-lattice-ic-relation-construction | AUD-4 | two of three routes reduce to standing obstructions | refuted |
| 13 further rows (LEAD-ICP-gfp5-odd-char-cover, LEAD-ICP-xline-symmetry-special-j, LEAD-ICP-construction-normal-form, LEAD-TRF-global-lift-small-height, LEAD-TRF-padic-canonical-section x3, LEAD-TRF-cover-catalog-jacobian-transfer, LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-TRF-teske-secret-isogeny-trapdoor, LEAD-TRF-small-genus-cover-general, LEAD-EXO-augmented-oracle-ggm, LEAD-EXO-miller-pairing-cocycle) | mixed | see `AUDIT.md` | verification **pending** (the first verify run hit the session limit; resumed) |

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

(filled from the scouting workflow; see `GRAVEYARD.md`)

## d. Survivors, ranked

(filled from the scouting workflow)

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
2. (survivors' first steps, filled from the scouting workflow)

## h. Blockers (problems/ records)

- `problems/formal-lean-external-volume-eintr.md` (new): Lake/`lean` reads on
  the external volume fail intermittently with EINTR; the Lean gate could not be
  run to completion; the theorems compile under plain `lean` with retries.
- `problems/README.md` is held by Conductor task T-5065 (another session), so
  the index line for the new problem record is **not** added here; proposed line:
  `- [Lean/Lake file reads on the external APFS volume fail intermittently with EINTR, blocking the formal gate](formal-lean-external-volume-eintr.md) - open`.
- `gh auth status`: the keyring token for github.com is invalid on this host
  and `api.github.com` is outside the sandbox allowlist; the PR for this branch
  is opened only if `gh` works at delivery time, otherwise the pushed branch is
  reported (propose-ideas skill, "Branch and PR hygiene").
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

(filled at the end)

## Checks

| check | result |
|---|---|
| `python3 tools/validate_ledger.py` | FAIL, 104 pre-existing errors on origin/main; 0 errors name RQ-ECDLP-361f3a, IDEA-20261024-a2b05d or the new targets (full log in `checks/validate_ledger_full.log`) |
| `python3 tools/lead_atlas.py --check --strict-paths` | FAIL, 2 pre-existing errors (LEAD-RHO-pool-class-quotient evidence[4], [5]); 0 attributable to this session; without `--strict-paths` these are warnings and the check passes |
| `python3 tools/build_frontier_map.py --check` | PASS: `known-results map OK: 52 rows` |
| `lake build` / `AxiomAudit.lean` / `verify_formal_targets.py` | NOT RUN TO COMPLETION (EINTR on this host); plain `lean` compile of both new files: PASS (logs in `checks/`) |
