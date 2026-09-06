# TASK-20260905-b5a40f — idea-generator notes

GOAL-ECRANK-002 / BATCH-05103f / RQ-ECRANK-27dcc5. Deliverable:
`ledger/ideas/IDEA-20260905-d5608c.yaml` (the allocated identifier, used
exactly; nothing else minted). This file is the second deliverable: the
row-by-row frontier check behind `dominated_by: null`, the audit results,
the lightweight-run records, and inference provenance. WRITE-ONCE; the
record changes NO status, asserts NO evidence.

## 1. What was done

Read the binding contract (`ledger/handoffs/TASK-20260905-b5a40f.yaml`)
and the opening decision (`ledger/decisions/DEC-20260905-9e3e06.yaml`,
carrying the N2 mandate quoted verbatim from DEC-20260822-7d356e and the
five-point coordinator prior). Read the inputs: EV-ECRANK-6695dc
(obstruction block read FORWARD per the mandate), RT-20260904-de2fa2
(`closure_attack.the_reversal` — the exact form engaged),
EXP-ECRANK-e1e30e/analysis.md + source/twist_family.py,
TASK-20260822-a7a9e8/src/construct_highrank.py (the Mestre machinery as
implemented and certified), goal.yaml (C1/C2, next_action narrower
framing), templates/research-records.md (idea schema, citation
provenance, proof_search_map), docs/inventor-protocol.md, the five open
RQ-ECRANK ideas (located via `tools/ecc_priority.py --open-ideas`: they
live in `ledger/proposals/`, which the handoff's "grep ledger/ideas/"
pointer misses — IDEA-20260829-01cbc5, -173a32, -d53906, -c7472b,
IDEA-20260905-9f7bc1), and IDEA-20260905-9f7bc1 as format precedent.

kb `search_knowledge` was ATTEMPTED and FAILED: the index collection
`crypto_knowledge_lineage_20260813_626955` does not exist in this
session. Infrastructure fact, recorded per rule 3; no absence/novelty
inference is drawn from it. Novelty screen fell back to exact
question-ID filesystem search of `ledger/proposals/` and
`ledger/ideas/`, as the format precedent did.

## 2. Derivation summary (the record carries the full text)

- Forcing identity (M0): for model `E : v^2 = s(u)`, twist `E^(d)` is
  `d v^2 = s(u)`; any rational `(b, r)` with `s(b) = d r^2` is a point
  on `E^(d)` — substitution, no descent (internal precedent
  IDEA-20260829-01cbc5).
- δ-multiplier engine (M2): `δ` = Lagrange interpolant with
  `δ(b_i) = d_i` (degree ≤ n−1, unique, zero dof consumed);
  `s := δ g^2 mod p`, `p = ∏(x − b_i)`; then `s(b_i) = d_i g(b_i)^2`
  IDENTICALLY for every `g`; ellipticity (deg s ≤ 4) = n−5 quadratic
  vanishing conditions on the k_g+1 coefficients of g; family dimension
  `k_g + 6 − n` (≥ 0 iff k_g ≥ n − 6).
- Subspace form (M3): conditions ⟺ `(d_i r_i^2)_i ∈ W(b)` (the
  5-dimensional evaluation image of quartics) ⟺ `u = (r_i^2)` lies in
  the computable 5-dim subspace `W'(b)`. Multi-class forcing = finding
  SQUARE-PATTERN POINTS IN A 5-DIM RATIONAL SUBSPACE. Explicit count:
  b (n) + projective r (n−1) − conditions (n−5) = **n + 4 dimensional
  family for every n ≥ 6**; conditions degree-2 at every n (no degree
  multiplication), only their NUMBER grows.
- Density heuristic (HEUR-1): fixed generic b ⇒ expected square-pattern
  points of height ≤ H ~ `H^(5 − n/2)`: n=6 → H², n=8 → H¹ (abundant),
  n=10 → H⁰, n=12 → H⁻¹, n=32 → H⁻¹¹. n=6 = one diagonal quadratic form
  in 6 variables ⇒ Hasse–Minkowski makes existence ⟺ local solvability
  (recalled pointer, marked) — near-rigorous anchor P0.
- **Parameter-count bottom line:** multi-class forcing SURVIVES the
  degrees-of-freedom arithmetic — YES abundantly at n = 8 (4 classes ×
  2 points), BORDERLINE at n = 10 (5 classes × 2, exponent 0),
  OPEN-AND-UNPRICED for n ≥ 12 (ellipticity wall H1: Mestre's own
  closed form gives deg s = n/2−1, elliptic only for n ≤ 10; for
  n ≥ 12 the vanishing system is strictly stronger even at d = 1).
  The route past the wall is M6 (construction seeds 4–5 classes; the
  committed exact-square-test augmentation scan, generalized per class,
  fills) — yield unmeasured, falsifiable (P3/F6). P4 (total ≥ 32) is
  flagged optimistic with three named unpriced steps.
- By construction, not by descent: points are evaluations of the
  identity once (b, r) is in hand; class membership is an INPUT; r_low
  is never computed (the min(r_low, #pts) convention that made every
  committed k=3 number descent-dependent is bypassed); independence is
  eigenspace-exact across classes + F_l-exact within; [K:Q]=8 is 7
  exact square tests. The only search is the quadratic-system solve
  and the exact-square-test scan — categorically not descents. If
  HEUR-1 fails, the COST objection grows; the descent-infeasibility
  obstacle is still not inherited.

## 3. Frontier table — every row checked (basis of `dominated_by: null`)

Axes: time, memory, data/queries (descents/oracle calls), certificate
kind. "Dominates the proposal?" = weakly better on ALL axes.

| # | Frontier row | Time | Memory | Data/queries | Certificate kind | Dominates? |
|---|---|---|---|---|---|---|
| 1 | Committed k=3 fixture, total 20 (EV-ECRANK-6695dc level A/B; base [0,-1,1,8,-50], 3+3+2+2+3+3+2+2) | ~25 min descent (128 descents × ~1.5 s × 5 certs) + 1218 s + 24 s producers | <1–4 GB (never costed by producers — disclosed) | 640 PARI ellrank descents; r_low PARI's, re-derived by nobody | 8 exact + 12 floating-regulator units; maximality UNVERIFIED | NO — beats the first-experiment target on raw total only (axis A); loses on data (640 descents vs 0) and certificate kind; does not transfer to constructed curves (31/31 timeouts, O-07) |
| 2 | Per-class single-twist Mestre baseline, 4–5 runs (the prior's dominator candidate) | ~9.4 ms/curve ⇒ ~50 ms total | trivial | 0 descents for its ONE forced class per curve; the other 7 classes of each produced curve need per-class descent — measured-blocked (31/31 ellrank timeouts at \|a_i\|~1e25; no rank ≥ 5 in 364,756 at small scale) ⇒ cost on the target axis is not lower, it is INFINITE/blocked | per curve: one populated class, regulator independence | NO — produces m DIFFERENT curves with one populated class each; the k=3 total is a per-curve quantity, so it cannot produce the object at any price. Dominates only on the single-class-over-Q axis, where the proposal claims nothing |
| 3 | Mestre single-class over Q, certified 13 (numerical independence) | 1218 s search | <4 GB | 0 descents (construction) + PARI heights | regulator-dependent | NO — disjoint axis (single class over Q); proposal makes no single-class claim |
| 4 | Degree-32 eigenspace certificate, 32 exact, no numerics | committed | small | 128 descents (small-conductor base) | 100% exact | NO — different field degree (32 vs C1's ≤ 8); unreachable-from row for the degree-8 rung |
| 5 | Degree-64, 64 exact | committed | small | as row 4 | 100% exact | NO — same reason, degree axis |
| 6 | Twist-search ceiling (no rank ≥ 5 in 364,756 candidates; 2 of rank 4 in 49,692) | committed scan | small | 364,756 twist descents/screenings | measured ceiling | NO — dominated by rows 1–5 on totals; dominates nothing here |
| 7 | IDEA-20260829-01cbc5 ladder (rank ≥ 32 over degree-2 field; 31+k over degree-2^k) | minutes (verification) once points in hand | small | 0 descents; but CONSUMES AN EXTERNAL WITNESS (ICARM no. 302) | exact (F_l) | NO — different object: external input this construction line does not take; fills k of 2^k classes (logarithmic); its own text names the product-class gap this engine attacks |
| 8 | External degree-1 witness, rank ≥ 31 over Q accepted by the committed verifiers (EV-ECRANK-2f1e65; C1 candidate UNPROMOTED under IMP-2) | minutes | small | 0 (verification of fetched points) | exact + non-singular regulator | NO — external input, not a construction; answers "is C1 satisfiable", not the goal's committed narrower framing "what does THIS construction reach" |

Verdict: NO row is weakly better on all axes ⇒ `dominated_by: null`.
Honest converse recorded in the record: row 1 DOES dominate the
first-experiment target on axis A alone (20 > 8–12); the null asserts
non-domination on the proposal's claimed contribution (axes B and C),
and the axis-A deficit is carried in `sota_delta`, not hidden.

`sota_delta` (quantitative, all arithmetic in run 1): axis A (k=3
total, any means) committed 20 = 8 + 12 → first-experiment delta
−12..−8, P4 delta +12 (unpriced); axis B (descent-free k=3 total)
committed 0 → target ≥ 8, delta +8 (new axis value); axis C (classes
populated by construction on one curve) committed 1 → target 4, delta
+3; axis D (single-class rank over Q) committed 13, delta 0, not
contested.

## 4. proof_search_map — the four desk audits (all carried, none excused)

1. **Exact baseline reproduction — CARRIED.** Slice d=(1..1), δ≡1:
   the vanishing system contains Mestre's trunc√p whenever n ≤ 10.
   Confirmed by ONE deterministic evaluation (run 1, Fractions, no
   trials): A = (±1,±3,±5,±7), deg p = 8, deg g = 4, `s(a_i) =
   g(a_i)^2` TRUE for all 8 points. Instructive detail: this symmetric
   A gives the CONSTANT s = 4096 — identity holds perfectly, instance
   degenerate (not elliptic) — so the nondegeneracy filter is a real
   condition (the committed machine enforces exactly this). Committed
   scale: the same assertion runs inside mestre_polys on every build
   (2,985 + 39,876 constructions; re-derived on all 1206 pool curves
   by EV-ECRANK-6695dc). Delta recorded: at n ≥ 12 the closed form
   overshoots deg s ≤ 4, so the engine is strictly stronger even at
   d = 1 — the slice reproduces the baseline exactly where the
   baseline is elliptic.
2. **Observation-collision search — CARRIED.** Observable =
   (populated class set, certificate-kind-split total). Distinct
   preimages (equal totals, different class distributions) are the
   exact equal-max/different-total phenomenon of EV-ECRANK-6695dc; the
   separator missing in that batch's fits exists here BY CONSTRUCTION
   (the d_i are inputs). The 2-design blindness (O-01) cannot apply —
   no relation is fitted to any enumeration. Residual collision
   (isomorphic curves from distinct solutions) deduped by minimal
   model.
3. **Quantifier-order statement — CARRIED.** Pure existence: EXISTS s,
   b, r explicit rationals, FOR ALL i: s(b_i) = d_i r_i², nonsingular,
   non-torsion, certified independent. No universal-over-cosets claim,
   no mean-relation-to-extreme-instance transfer (the PA-02 swap is
   excluded by form). HEUR-1 is a search heuristic, never a premise of
   a certificate.
4. **Method ceiling + nearby-object control — CARRIED.** Ceiling: ≤ 8
   exact eigenspace units at k=3 (PA-03, saturated everywhere); above
   8 = multiplicity units, weaker kind; the split is carried in every
   total (O-06 guardrail; "degree 8 beats degree 32" forbidden without
   it). Nearby object: k=4 coset (committed-support k4 optimum 32 at
   level A) — same engine, tests the H^(5−n/2) degradation. Known-
   false control (proves-too-much): d=(1..1), where "total = n" is
   KNOWN FALSE (ceilings 7/9) — built into the test boundary.

## 5. Lightweight runs (maximum_runs 2; 2 used; ZERO scans/descent/search compute)

- **Run 1** — parameter counts + baseline-reproduction arithmetic +
  frontier arithmetic.
  - path: `/Volumes/SSD990/llm/tmp/opencode/task_b5a40f_param_counts.py`
  - command: `python3 /Volumes/SSD990/llm/tmp/opencode/task_b5a40f_param_counts.py 2>&1 | tee /Volumes/SSD990/llm/tmp/opencode/task_b5a40f_param_counts.out`
  - result: table (n | n−5 conditions | δg family dim k_g+6−n | subspace
    family dim n+4 | density exponent 5−n/2 | Mestre closed-form deg
    n/2−1 | elliptic only n ≤ 10) for n = 6,8,10,12,16,32; Mestre
    identity TRUE on the deterministic n=8 instance (s constant 4096 —
    degenerate, noted above); 20 = 8+12; 32−20 = 12; 8−20..12−20 =
    −12..−8; 8−0 = 8; 4−1 = 3; 11811×16 = 188,976; 2³−1 = 7; even-parity
    neighbours of 31 are 30 and 32 ⇒ C1 needs 32 under the O-12 reading.
- **Run 2** — YAML parse check of both deliverables + sha256 (bookkeeping).
  - command: `python3 -c "import yaml,sys; [yaml.safe_load(open(p)) and print('parses:',p) for p in sys.argv[1:]]" ledger/ideas/IDEA-20260905-d5608c.yaml coordination/goals/GOAL-ECRANK-002/batches/BATCH-05103f/tasks/TASK-20260905-b5a40f/notes.md && shasum -a 256 <both paths>` (exact invocation in the task log).
- Mandated completion-gate tool (not an experiment run):
  `python3 tools/validate_ledger.py` — tail inspected; result recorded
  in §7.

No Mestre scans, no descent, no experiment arms, no network requests.

## 6. Inference provenance

- requested_policy: `research-deep` (handoff `inference.policy`).
- reasoning_effort: `null` (policy default; no per-task calibration, no
  cap announced to this session).
- fallback_used: `true` — dispatched as a general agent carrying the
  full idea-generator contract; the opencode idea-generator binding
  (balance-dead) is dead in this deployment; `fallback_allowed: true`
  in the handoff. degraded_allowed was false and NO requirement was
  degraded (`degraded_requirements: []`).
- model_verified: `false` (no `orchestration.adapter doctor --probe`
  confirmation exists for this identifier in this session).
- resolved_model_id: `fireworks-ai/accounts/fireworks/models/qwen3p8-max`
  (self-reported runtime identity).
- independent_session: `true`.
- backend: not Amazon Bedrock; no identifier containing `bedrock` was
  selected, requested or probed; zero network requests (the kb search
  attempt hit a local absent index).

## 7. Validator + deliverable confirmation

- `python3 tools/validate_ledger.py` run after writing the record; tail
  result: **no new violations attributable to
  IDEA-20260905-d5608c** (exact tail in the task log; note the
  validator's discovery globs cover `ledger/proposals/`, not
  `ledger/ideas/` — the handoff's write_scope binds this record to
  `ledger/ideas/`, which `tools/ecc_priority.py` reads via
  `PROPOSAL_DIRS = ("proposals", "ideas")`, so the record is visible to
  the open-ideas worklist regardless).
- Both deliverables written, YAML-parsed (run 2), sha256 recorded in
  the task log and the return message. Exactly two files written; no
  git state mutated; nothing minted beyond the allocated identifier.

## 8. Prior engagement index (where the record answers (a)–(e))

- (a) domination objection → `domination_objection` block: premise
  check (no degree multiplication — conditions stay degree 2, count
  grows linearly), what the baseline actually produces (m different
  curves, one class each; per-curve totals need blocked descents),
  cost model at certified parameters (~10^8–10^10 exact ops vs ~50 ms
  for a different object). Cost model GIVEN ⇒ `dominated_by` argued
  null with the row table above.
- (b) parameter count → `mechanism` M2/M3 + `walls` H1 + run-1 table:
  survives YES at n = 8, borderline n = 10, wall named past n = 10.
- (c) frontier rows → §3 table (8 rows × time/memory/data/certificate
  kind); `sota_delta` quantitative in the record.
- (d) by construction → `by_construction_not_by_descent` block, with
  the honest inheritance note (cost objection ≠ descent inheritance).
- (e) fatigue-report guard → the record carries mechanism with
  explicit counts, 5 numbered predictions each with its own
  falsifier, a frozen test boundary with controls (known-false,
  null-object, blind re-derivation, degeneracy filter), 6
  falsification conditions, 2 numbered heuristics with random-model
  justification, and the four audits — not a restatement.
