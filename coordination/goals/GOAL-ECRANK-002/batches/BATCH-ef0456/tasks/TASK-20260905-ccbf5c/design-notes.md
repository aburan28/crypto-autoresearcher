# TASK-20260905-ccbf5c — design coordinator notes

GOAL-ECRANK-002 / BATCH-ef0456 / RQ-ECRANK-27dcc5. Design step of
/design-experiment on IDEA-20260905-d5608c. Deliverables (exactly three
files, all written; nothing else minted, no git state mutated):

1. `ledger/hypotheses/H-ECRANK-ee6e0e.yaml` — the `specified` hypothesis.
2. `experiments/EXP-ECRANK-76a70d/specification.yaml` — the FROZEN
   contract, `status: review_required`, `approved_by: null`.
3. This file.

WRITE-ONCE task report. This batch designs; it does NOT approve and does
NOT execute. The approval gate (user confirmation + committed Coordinator
decision) is a later batch, per DEC-20260905-eba685's
`approval_gate_note`.

## 1. What was read (binding inputs)

- `ledger/handoffs/TASK-20260905-ccbf5c.yaml` (full contract: objective,
  constraints, deliverables, completion gate).
- `ledger/decisions/DEC-20260905-eba685.yaml` (opening decision:
  heuristic-validation class note; the SIX-POINT COORDINATOR PRIOR;
  approval gate; batch budget).
- `ledger/ideas/IDEA-20260905-d5608c.yaml` (all 994 lines: mechanism
  M0-M6, parameter count, P0-P4, HEUR-1/HEUR-2, four controls, F1-F6,
  wall H1, frontier/domination blocks, sota_delta, proof_search_map,
  citations with provenance marks).
- `coordination/goals/GOAL-ECRANK-002/batches/BATCH-05103f/tasks/TASK-20260905-b5a40f/notes.md`
  (derivation notes: parameter-count arithmetic run 1, 8-row frontier
  table, four audits, the constant-4096 degeneracy lesson).
- `.claude/skills/design-experiment/SKILL.md` (binding workflow;
  heuristic-validation pattern requirements; rules on freezing and
  decidable success criteria).
- `templates/research-records.md` (hypothesis + experiment schemas,
  citation provenance, budget-floor note).
- `experiments/EXP-ECRANK-e1e30e/specification.yaml` (structure
  precedent) + `analysis.md` section headers + `source/` listing (the
  committed machinery: verify_certificate.py, twist_family.py,
  quartic_reduction path; certified-13 baseline on the single class
  d = 1).
- `ledger/evidence/EV-ECRANK-6695dc.yaml` (obstruction block read
  forward: `others` spans 6-17 units, conditional means
  9.4945/10.6954/13.0667 over the 651 sum_mult-objective k = 3
  sub-cosets; run-id schema facts; certificate refs; D4 remedy rule).
- `tools/validate_ledger.py` (required fields for hypothesis/experiment;
  the `approved`-status-only enforcement of `approved_by`; citation and
  obstruction checks) — so the records are written to the validator, not
  to taste.

kb `search_knowledge` was ATTEMPTED and FAILED in this session
identically to the idea-filing session: the index collection
`crypto_knowledge_lineage_20260813_626955` does not exist. Infrastructure
fact recorded per rule 3; no novelty or absence inference is drawn;
`novelty_status: unverified` is inherited from the idea and noted on the
hypothesis.

Branch state (read-only git only): branch
`ecrank-d5608c-design-20260905`, HEAD `25926971282111894da83dbd88bf13982867672e`,
working tree clean before writing. PROCEDURE DEVIATION, recorded not
absorbed: the skill's "merge origin/main before designing" step was NOT
performed because the handoff constraint "no git state mutated
(read-only git fine)" governs this task; `git fetch`/merge and the PR are
the archive task's (TASK-20260905-81ec59) and the lane coordinator's
responsibility per DEC-20260905-eba685's `lane_note` and
`approval_gate_note` ("this batch publishes the PR before reporting the
design complete"). The records were drafted against the current worktree
state, which already carries the BATCH-ef0456 opening commit.

Skill step 3's empty `amendments/` and `runs/` directories were NOT
created: the handoff binds this task to exactly three FILES, and git
tracks no empty directories — the executor/archival task creates them at
first use. The amendment PATH is declared in the contract
(`experiments/EXP-ECRANK-76a70d/amendments/`) so the frozen-prediction
rule is checkable.

## 2. Sample-size derivation and budget arithmetic (prior point 2 — done, not skipped)

Executed pre-run as design run 1 (exact commands in §6; pure arithmetic,
zero scans, zero descent, zero experiment execution).

### 2.1 The H^(5 − n/2) arithmetic, explicitly, at the chosen n

HEUR-1: expected square-pattern points of height ≤ H in the fixed
5-dimensional subspace W′(b) ~ C(b,d)·H^(5 − n/2), C(b,d) > 0 iff locally
solvable everywhere. Exponents (run 1, §1 of output):

| n | exponent 5 − n/2 | conditions n − 5 | family dim n + 4 | Mestre closed-form deg s = n/2 − 1 | elliptic (deg s ≤ 4) |
|---|---|---|---|---|---|
| 6 | **+2** | 1 | 10 | 2 | yes |
| 8 | **+1** | 3 | 12 | 3 | yes |
| 10 | **0** | 5 | 14 | 4 | yes |
| 12 | −1 | 7 | 16 | 5 | **no — WALL** |
| 32 | −11 | 27 | 36 | 15 | no |

At n = 8, r-height H = 10⁴ (u-height X = H² = 10⁸): per-point
square-pattern probability X^(−n/2) = 10⁻³²; subspace lattice points
~X⁵ = 10⁴⁰; expected count X^(5 − n/2) = 10⁸ in u-height, i.e. ~C·H¹ =
C·10⁴ in box height H as HEUR-1 states the law. Predicted **abundant** at
n = 8; finite-expected-nonzero at n = 10.

### 2.2 Sample count from the smallest predicted probability to resolve

- **Smallest probability to resolve:** q = 10⁻³ := per-b-tuple
  probability that a seeded b-tuple yields ≥ 1 certified instance within
  the bounded search. **DECLARED, NOT THEOREM-DERIVED — flagged:**
  HEUR-1 predicts neither the locally-solvable fraction f_loc nor the
  constant C(b,d), so no theorem in hand yields q. q = 10⁻³ is the
  SMALLEST floor resolvable inside the idea's own budget: resolving
  q = 10⁻⁴ at the same tail multiple needs N_b = 10⁵ ⇒ 10⁵ × 10⁴ = 10⁹
  counted ops = the idea's ≤ 10⁹/arm cap EXACTLY, zero headroom, wall
  risk at conservative throughput. q = 10⁻³ keeps 10× op headroom.
- **Derived sample count:** N_b = tail_multiple / q = 10 / 10⁻³ =
  **10⁴ seeded b-tuples per arm** (arms B and C). Arm A (n = 6, exponent
  +2, expected counts ~C·10⁸ at H = 10⁴) takes 10³ — ample.
- **Expected tail multiple:** N_b·q = **10** (10× — "meaningfully larger
  than 1" per the skill). Consequence: if the true rate ≥ q, P(zero
  instances) = (1 − q)^N_b ≈ e⁻¹⁰ ≈ **4.5 × 10⁻⁵**, so a null result is a
  MEASUREMENT against HEUR-1 on the declared scope (fires F1 there), not
  bad luck. This is what makes the success criterion's negative branch a
  real outcome.
- **F1 scope honesty:** 10⁴ of ~1.67 × 10⁹ affine normal-form tuples
  (b₁ = 0, b₂ = 1; b₃..b₈ distinct in [−20,20]\{0,1}) ≈ 6 × 10⁻⁶ of the
  box. Full exhaustion would cost ~2 × 10¹³ ops (~10⁵× the arm cap) and
  is NOT promised; F1 fires at the DECLARED SAMPLE scope only (rule 6).
  The idea's P1 is budget-scoped in the idea itself (≤ 10⁹ ops, ≤ 2 h),
  so this FIXES scope rather than narrowing a promise (prior point 4's
  demanded resolution).

### 2.3 Budget arithmetic (prior point 4)

- Per-b declared cap **10⁴ exact ops**: Vandermonde left kernel O(n³)
  = 512 + δ Lagrange interpolation O(n²) = 64 + ≤ 8 fibration draws ×
  ~824 (3 diagonal-conic assemblies ~24 + Bézout ≤ 8 candidates × ~100
  exact rationality ops) ≈ 7.2 × 10³, rounded up. (The "~10³ ops per b"
  in the idea's cost model is the idea's own ESTIMATE; the contract
  declares the rounded cap and counts actual ops — estimates are never
  presented as measurements.)
- Per-arm: 10⁴ b × 10⁴ ops = **10⁸ counted exact ops** — inside the
  idea's ~10⁸–10¹⁰ estimate and 10× inside its ≤ 10⁹/arm cap. Counted
  and checkpointed every 10⁷.
- Wall: at a conservative ≥ 2 × 10⁴ exact-ops/s (Python Fractions floor)
  → 5000 s < 7200 s cap; at the idea's implied 1.4 × 10⁶ ops/s → 71 s.
  Stopping rule: counted ops 10⁸ OR wall 7200 s, whichever first;
  exhaustion is INERT (rules 3/5), never re-scored.
- Scan stage: box |num| ≤ 10³, den ≤ 20 → 4 × 10⁴ points/class; per
  (quartic, class) cell 8 × 10⁵ ops; constructed instance 8 cells =
  6.4 × 10⁶; null objects 8 random quartics × 8 classes = 64 cells =
  5.1 × 10⁷; stage total 5.8 × 10⁷ ops → ≤ 2900 s at the conservative
  floor. The box WIDENS the committed extra_quartic_points box
  (|n| ≤ 400, d ≤ 12) — "the untouched knob" — and is declared frozen.
- Known-false control: expects total **7 at n = 8** and **9 at n = 10**
  (g − y relation eats 1; committed ceilings attained exactly per
  EV-ECRANK-6695dc); total = n there ⇒ ALL runs void (IV-1).
- Height-sweep predicted relative counts (nested H = 10², 10³, 10⁴):
  n = 6 → 10⁴ : 10⁶ : 10⁸; n = 8 → 10² : 10³ : 10⁴ (~10× per decade);
  n = 10 → 1 : 1 : 1. The three n's give three DIFFERENT predicted
  slopes — the different-scale control (C7) is scale-specific by
  construction.
- Contract budget fields: wall_clock_seconds_per_run 7200 (≥ 600 floor);
  maximum_memory_gb 8 (≥ 8 floor; expected actual < 4 GB — headroom
  disclosed, peak_rss_bytes reconciled per run); total_cpu_hours 16
  (worst case 8 runs × 2 h; expected ~6–7 h); maximum_runs 8
  (enumerated in the contract); maximum_workers 1; descent_calls 0;
  pari_ellrank_calls 0; network none.

## 3. The six-point coordinator prior, engaged one by one

1. **DECIDABILITY.** The success criterion binds exactly the falsifiable
   target the prior named: a certified k = 3 total contribution ≥ 8 from
   the forced classes (≥ 4 exact eigenspace + ≥ 4 exact F_l units, kind
   split carried, zero verifier errors) at an arm-B instance found within
   the frozen box, the 10⁴ seeded sample, and the 10⁸ counted-op cap —
   tied to P1. The unfalsifiable phrasing ("construct any curve with
   forced points on four classes", which succeeds given enough solver
   time) is EXCLUDED by the counted-ops cap, the frozen sample, and the
   explicit negative branches: sample exhausted with no instance = F1 on
   the declared scope (P(zero | rate ≥ q) ≈ 4.5 × 10⁻⁵ makes it a real
   possible outcome); contribution < 8 or c_e ≥ 2 = negative on P2 (F3);
   control failure = invalidation, not a result. A
   `success_criterion_decidability_note` in the contract records that
   every clause is machine-checkable from the predefined metrics. The
   pull the prior predicted (toward the unfalsifiable phrasing) was
   resisted by deriving the negative branch FIRST (the 4.5 × 10⁻⁵
   arithmetic) and writing the positive branch around it.
2. **SAMPLE-SIZE DERIVATION.** §2 above and the contract's
   `sample_size_derivation` block: the H^(5 − n/2) arithmetic done
   explicitly at n = 6/8/10 (table), the smallest probability to resolve
   named (q = 10⁻³, declared-not-derived and FLAGGED as such — the honest
   status, since HEUR-1 predicts neither f_loc nor C(b,d)), N_b = 10⁴
   derived as tail_multiple/q, expected tail count 10 (10× multiple
   stated), and the q = 10⁻⁴ alternative priced out against the idea's
   own op cap. Not skipped, not hand-waved.
3. **CONTROL BINDING.** All four idea controls are in the contract's
   `controls` AND bound to consequences: known-false d = (1..1) →
   invalidation rule **IV-1** ("its failure voids the run", verbatim
   discipline: ALL runs VOID, at both n = 8 → 7 and n = 10 → 9);
   null-object scan → C2 with the frozen Fisher test (α = 0.05) feeding
   F6; blind kernel re-derivation → C3 with blind_from naming the solver
   module and the producer's notes/report, bound to **IV-3**; degeneracy
   filter → C4 with the constant-4096 lesson, bound to **IV-4** (struck
   from all counts; success instance failing it voids the success claim).
   The skill's minimum controls are added: planted synthetic uniform
   control of matched shape (C5 → IV-2, validates sampler AND metric),
   independence of instances and seeds (C6 → IV-7 determinism), second
   parameter set at a different scale (C7: n = 6/8/10, three different
   predicted slopes).
4. **BUDGET CONSISTENCY.** §2.3: 10⁸ counted ops/arm inside the idea's
   ~10⁸–10¹⁰ estimate and 10× inside its ≤ 10⁹ cap; wall 7200 s = the
   idea's ≤ 2 h/arm; memory ceiling 8 GB (floor-respecting headroom over
   the idea's 4 GB estimate, disclosed as headroom); descent 0, PARI 0,
   network none. The n = 8 (4 × 2) vs bounded-budget tension is resolved
   BY FIXING SCOPE — the seeded 10⁴ sample with F1 scoped to it (rule 6)
   — not by an unbounded run and not by a fudged number.
5. **WALL DISCIPLINE.** Contract scope is n ≤ 10 EVERYWHERE (objective's
   SCOPE WALL clause; hypothesis `test_boundary.scope_wall` and wall H1's
   `contract_effect`). No budget line, stopping rule, metric, or
   criterion references n ≥ 12, the k = 4 nearby object (n = 16), or the
   M6 scale route to total ≥ 32. P4 is carried IN THE HYPOTHESIS in full
   (flagged optimistic/unpriced, idea's own flag) with an explicit
   `excuse_reason` for its exclusion from the contract; the idea's P3
   n = 12 sub-step is likewise explicitly excused with a reason. Nothing
   silently promises the unpriced wall-crossing route.
6. **STATUS DISCIPLINE.** Hypothesis `status: specified`; experiment
   `status: review_required`; `approved_by: null` with an
   `approval_note` stating that null is by design and by rule, and that
   self-approval in this batch is a violation. No approval, no handoff to
   executor, no compute authorized. (Validator note: `approved_by` is
   enforced non-null only on `status: approved`; `review_required` with
   null is the pre-approval state the skill's step 2 mandates.)

## 4. Carry-or-excuse index (nothing silently dropped)

| Idea element | Where it lives | Status |
|---|---|---|
| Mechanism M0-M6 | hypothesis `mechanism` (M6 marked out-of-contract-scope, named not promised) | carried |
| Parameter count n+4, n ≥ 6; conditions degree 2, count linear | hypothesis mechanism M2/M3; contract inputs.engine | carried |
| P0 (n = 6 anchor) | hypothesis numbered_predictions + contract arm A; Hasse-Minkowski rigor_note (recalled pointer, verification pending) | carried |
| P1 (n = 8 main) | hypothesis + contract success criterion; scope_note fixes the sample scope | carried |
| P2 (c_e bookkeeping) | hypothesis + contract metrics/F3/IV rules | carried |
| P3 (scale step + scan) | hypothesis + contract arm C + scan stage; n = 12 sub-step EXCUSED with reason (wall discipline, no price, no solver) | carried with explicit partial excuse |
| P4 (total ≥ 32, optimistic) | hypothesis, full text with the three unpriced steps; EXCUSED from contract with reason (wall discipline, prior point 5) | carried + explicit excuse |
| HEUR-1 / HEUR-2 | hypothesis `heuristic_assumptions`; contract `heuristics_stated_exactly` + `preregistered_prediction`; supporting_results EMPTY BY RULE 9 with notes (recalled pointers cannot discharge it) | carried |
| Four controls | contract C1-C4 bound to IV-1/IV-3/IV-4 and F6 | carried + bound |
| F1-F6 | hypothesis `falsification_conditions`; contract `falsification_criterion` with per-condition scope | carried |
| Wall H1 (ellipticity wall) | hypothesis `walls` + `contract_effect` | carried |
| Certificate-kind split (O-06) | hypothesis mechanism M4; contract metrics + success criterion + IV-6 | carried |
| by_construction_not_by_descent | hypothesis mechanism M0/M5 + statement + contract objective (ZERO descent) + IV-6 | carried |
| Confounders (O-09 selection, post-hoc widening, O-08 pseudo-replication) | hypothesis `confounders`; contract C6, stopping rules (no adaptive widening), comparison metric (d) | carried + bound |
| Interpretation limits (toy scale, no ECDLP, pointers-not-support, obstruction-not-verdict) | hypothesis `interpretation_limits`; contract `scale_relevance` | carried |
| sota_delta (axis A negative −12..−8; axes B/C the claim) | hypothesis `interpretation_limits` last entry, quantitative | carried |
| dominated_by null + 8-row frontier table | carry-BY-REFERENCE to the immutable idea record and its notes (ranking artifact; hypothesis references, does not re-assert) — explicit, not silent | carried by reference |
| proof_search_map + four audits | hypothesis `proof_search_map`, full, with k = 4 nearby object marked out-of-contract | carried |
| novelty_status unverified + novelty screen | hypothesis `novelty_status` + note (kb attempt failed again this session) | carried |
| Assumptions (5) | hypothesis `assumptions` verbatim | carried |
| Citations with provenance marks | hypothesis `citations` + `structural_ingredients` (recalled entries hedged, verified_by null; internal entries name the reading task) | carried |
| Degeneracy lesson (constant 4096) | contract C4 + hypothesis proof_search_map reproduction_check + tail check (reverse artifact tell) | carried |

## 5. Schema and validator evidence

- Written to the validator's actual requirements (read from
  `tools/validate_ledger.py`): hypothesis REQUIRED = id, question_id,
  statement, mechanism, status — all present; question_id
  RQ-ECRANK-27dcc5 resolves (`ledger/questions/RQ-ECRANK-27dcc5.yaml`
  exists). Experiment REQUIRED = id, hypothesis_id, version, status,
  metrics, budget, success_criterion — all present; hypothesis_id
  resolves to the hypothesis written in the same task; ID patterns
  (`^H-[A-Z]+-<6hex>$`, `^EXP-[A-Z]+-<6hex>$`) match; the file path
  matches the validator's discovery regex
  `^experiments/[^/]+/specification\.yaml$`.
- Citation/structural_ingredients validation: every entry carries
  `provenance` ∈ {recalled, internal}; every `internal` entry carries
  `verified_by` (TASK-20260905-ccbf5c for records read in THIS session;
  TASK-20260905-b5a40f for records read by the idea's producer and
  carried through its citation — honestly attributed); every `recalled`
  entry has verified_by null and is hedged.
- `python3 tools/validate_ledger.py` run after writing both YAML
  records. Tail: `OK: validated 9014 records, no new violations` (plus
  the standing baseline notes: 1210 grandfathered legacy errors
  suppressed, 979 legacy schema issues read-only). **Zero new violations
  attributable to H-ECRANK-ee6e0e or EXP-ECRANK-76a70d.**
- No-null discipline (refuse-style): every field group named in the
  completion gate (inputs / controls / independent variables / metrics /
  seeds / budget / stopping / invalidation / success / falsification /
  artifacts) is fully filled. The only nulls in either record are
  DELIBERATE documented nulls: `rerandomization: null`,
  `asymptotic_claim: null`, `correspondence: null`,
  `not_applicable_reason: null` — each with an adjacent `*_note` stating
  why null rather than absent (the EXP-YIELD-003 distinction the
  validator's own comment enforces), and `approved_by: null` which is the
  mandated pre-approval state. `heuristic_assumptions[].supporting_results: []`
  is empty BY RULE 9 with notes, not overlooked.

## 6. Lightweight runs (maximum_runs 2; 2 used; ZERO scans, ZERO descent, ZERO experiment execution)

- **Run 1** — sample-size derivation + budget arithmetic (the numbers in
  §2, machine-executed, not hand-waved).
  - path: `/Volumes/SSD990/llm/tmp/opencode/task_ccbf5c_design_arithmetic.py`
  - command: `python3 /Volumes/SSD990/llm/tmp/opencode/task_ccbf5c_design_arithmetic.py 2>&1 | tee /Volumes/SSD990/llm/tmp/opencode/task_ccbf5c_design_arithmetic.out`
  - result: exponent table (§2.1); per-point probability 10⁻³² at n = 8,
    H = 10⁴; q = 10⁻³ ⇒ N_b = 10⁴, tail count 10, P(zero) = 4.517 × 10⁻⁵;
    per-b 7168 → declared 10⁴ ops; per-arm 10⁸ ops, inside 10⁸–10¹⁰ and
    ≤ 10⁹ cap; wall 5000 s at 2 × 10⁴ ops/s floor; box capacity
    1,673,844,480 tuples, sample fraction 5.97 × 10⁻⁶; height-sweep
    ratios; scan stage 5.76 × 10⁷ ops ≤ 2880 s; known-false expectations
    7/9; arm budgets A 5 × 10⁶, B 10⁸, C 10⁸.
- **Run 2** — YAML parse + sha256 of all three deliverables
  (bookkeeping; exact invocation and hashes in the task log and the
  return message).
- Mandated completion-gate tool (not counted as an experiment run,
  precedent TASK-20260905-b5a40f §5): `python3 tools/validate_ledger.py`
  — tail recorded in §5.

No Mestre scans, no descent, no experiment arms, no network requests, no
identifier minted, no git state mutated (read-only `git rev-parse` /
`git status` / `git branch` only).

## 7. Inference provenance

- requested_policy: `coordinator-orchestration-code` (design authority
  per the design-experiment skill step 2; handoff `inference.policy`).
- reasoning_effort: `null` (policy default; no per-task calibration
  issued, no cap announced to this session).
- fallback_used: `true` — dispatched as a general agent carrying the
  full design contract; the opencode coordinator role binding
  (balance-dead) is dead in this deployment; `fallback_allowed: true` in
  the handoff. `degraded_allowed` was false and NO requirement was
  degraded (`degraded_requirements: []`).
- model_verified: `false` (no `orchestration.adapter doctor --probe`
  confirmation exists for this identifier in this session).
- resolved_model_id: `fireworks-ai/accounts/fireworks/models/qwen3p8-max`
  (self-reported runtime identity, stated exactly).
- independent_session: `true`.
- backend: not Amazon Bedrock; no provider, endpoint, or identifier
  containing `bedrock` was selected, requested, or probed; zero network
  requests (the kb attempt hit a local absent index).

## 8. Findings and verdict

**Verdict: design-with-findings.** All contract fields are filled, the
success criterion is decidable with a frozen negative branch, and the
budget is consistent with the idea's own estimate — no gap forced a
fudged budget or an unfalsifiable criterion. Disclosed findings (none
hidden, none smoothing):

1. **q = 10⁻³ is declared, not theorem-derived.** HEUR-1 predicts
   neither f_loc nor C(b,d); the resolution floor is a pre-registered
   design constant justified by pricing the finer floor (q = 10⁻⁴) out
   of the idea's own op cap. It is frozen and cannot be moved afterward
   except by amendment.
2. **Throughput assumption.** The wall budget assumes ≥ 2 × 10⁴ exact
   Fraction ops/s; the idea's own cost model implies up to 1.4 × 10⁶.
   Mitigation: the COUNTED-ops cap is the binding budget, checkpointing
   every 10⁷ ops, and exhaustion is inert — a slow machine yields a
   completed prefix plus an exhaustion report, never a fake result.
3. **Per-b cost (~7.2 × 10³ ops) rests on the idea's cost-model
   estimate** ("~10³ ops per b" plus enumerated components), not on a
   measurement of this engine. The contract counts actual ops; if the
   real per-b cost exceeds the declared 10⁴ cap per b, the arm completes
   a smaller sample prefix and reports it as such (F1 scope narrows to
   the completed prefix — rule 6 again).
4. **F6 statistical power is limited** at the declared scan box (4
   constructed non-forced cells vs 32 null cells): it can fire
   decisively only on large effects. Disclosed in the contract (C2) and
   in P3's honest_power_note.
5. **Arm C (n = 10) is borderline** (exponent 0): finding nothing there
   is a P3-relevant measurement, not an invalidation — stated in the
   hypothesis so a null arm C cannot be misread either way.
6. **Hasse-Minkowski and Mazur are recalled pointers** (Serre Ch. IV;
   Mazur IHES 1977): pointers, never support (rule 9). The pipeline
   relies on the COMMITTED verifier implementations, and P0's
   "near-rigorous" label carries a rigor_note asking the approval-gate
   reviewer to confirm the statement from a read source before any
   conclusion leans on the label.
7. **kb index absent** in this session (second occurrence): novelty
   stays `unverified`; no absence inference drawn.

Next step is NOT execution: per the skill step 4 and the opening
decision, the frozen contract is presented to the USER for confirmation,
and approval (plus the executor handoff) is a separate committed
Coordinator decision in a later batch. Until then `approved_by` stays
null and no compute is spent.
