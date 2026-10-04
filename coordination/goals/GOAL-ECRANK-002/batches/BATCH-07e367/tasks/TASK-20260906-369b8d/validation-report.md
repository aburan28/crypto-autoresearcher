# Validation report — TASK-20260906-369b8d (Validator, joints J1 + J2)

- goal: GOAL-ECRANK-002 / RQ-ECRANK-27dcc5 / BATCH-07e367
- experiment under review: EXP-ECRANK-76a70d v1 (frozen contract
  `experiments/EXP-ECRANK-76a70d/specification.yaml`, protocol sha256
  bcff5ced4c31468e3e09b49b7197b793888775f4df0d63074bad6c3905044b8f per
  DEC-20260905-2d466e)
- snapshot commit read: `a20a49b6adbcce51893c1221dbd69cdcd486ad9d` (binds the
  executor's run package byte-for-byte, 214 paths; worktree branch
  `ecrank-76a70d-exec2-20260906`, HEAD f164d4d63 at dispatch)
- authoritative review plan: DEC-20260906-69749a.review_plan (pre-recorded
  before any reviewer ran); queue copy records ONE procedure deviation
  (J2 re-scope, ratified per the deviation text by DEC-20260906-7448cf)
- role: Validator. Independent fresh session; did NOT produce any artifact
  under review. Joints owned: J1 (run-record integrity and determinism),
  J2 (blind re-derivation). J3/J4 belong to TASK-20260906-a2eb0c and were
  NOT performed; the red-team's task directory was NOT opened (blindness
  within round; attested below).
- scope discipline: this round reviews RUN RECORDS only. No status change,
  no promotion, no interpretation beyond J1/J2. Nothing here touches the
  UNPROMOTED closure candidate of DEC-20260905-7adca0.

## Inference manifest (this session)

```yaml
inference:
  requested_policy: review-adversarial
  reasoning_effort: xhigh
  fallback_used: true
  fallback_reason: "role-bound validator binding balance-dead (DECLARED FALLBACK dispatch; handoff TASK-20260906-369b8d sets fallback_allowed: true)"
  degraded_allowed: false
  degraded_requirements: []          # none accepted; independence and effort requirements met in-session
  resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  model_verified: false              # no `orchestration.adapter doctor --probe` run in this session; identifier is unverified configuration per AGENTS.md
  independent_session: true          # fresh session; not a continuation of the producer; produced none of the artifacts under review
  runtime: opencode CLI (api-direct); no Bedrock provider, backend, or model identifier selected at any point (rule 16)
```

## Attestation: what was read, and in what order

Phase 1 — pre-blind reads (governance + frozen contract + permitted blind inputs only):

1. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-07e367/tasks/TASK-20260906-369b8d/task_card.yaml`
2. `ledger/handoffs/TASK-20260906-369b8d.yaml` (handoff envelope + review_plan)
3. `ledger/decisions/DEC-20260906-69749a.yaml` (authoritative pre-recorded plan + Coordinator prior)
4. `coordination/goals/GOAL-ECRANK-002/batches/BATCH-07e367/dispatch_queue.json` — my task entry only, including `review_plan.procedure_deviations` (the J2 re-scope)
5. `experiments/EXP-ECRANK-76a70d/specification.yaml` (frozen contract)
6. Directory NAMES only under `experiments/EXP-ECRANK-76a70d/` and `experiments/EXP-ECRANK-76a70d/runs/` (no file contents)
7. ONLY the `blind_rederivation_inputs_C3` key of
   `runs/RUN-ECRANK-76a70d-R2-armA/raw-result.json`,
   `runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json`,
   `runs/RUN-ECRANK-76a70d-R5-armC/raw-result.json`
   (extracted programmatically by key; no other content of these files was
   read at this phase — these blocks are the deviation's explicitly
   permitted J2 inputs)

Phase 2 — J2 blind re-derivation computed from the statements of the
quantities and the parameters alone (Section J2 below), and THIS SECTION OF
THE REPORT WAS WRITTEN TO DISK before any blind_from source was opened.

Phase 3 — post-blind reads (appended below after the J2 derivation was
committed to this file): executor recorded solver outputs for the comparison
step, the eight run manifests and raw artifacts for J1, the repair-task
handoff, and git history for the repair-diff check. Each Phase-3 read is
listed in the J1/comparison sections with its purpose.

blind_from attestation: before the J2 derivation in Section J2 was computed
and written, I did NOT open any of:

- `experiments/EXP-ECRANK-76a70d/source/` (any file)
- `experiments/EXP-ECRANK-76a70d/execution-report.yaml`
- the executor's run report bodies (including all content of
  `runs/*/raw-result.json` outside the permitted
  `blind_rederivation_inputs_C3` blocks, `runs/*/stdout.log`,
  `runs/*/stderr.log`, `runs/*/manifest.yaml`, `runs/*/checkpoints/`,
  `runs/*/command.txt`, `runs/*/environment.json`)
- `certificates/` contents

Sibling-report attestation: `coordination/goals/GOAL-ECRANK-002/batches/BATCH-07e367/tasks/TASK-20260906-a2eb0c/` was NOT read at any point (red-team report; within-round blindness, `blindness.lifted_for: []`).

---

# J2 — Blind re-derivation (re-scoped per the recorded procedure deviation)

## J2.0 Re-scope and status of the pre-recorded object

The pre-recorded J2 object (DEC-20260906-69749a) was "ONE arm-B certified
instance (first by seed order)" and its certified k=3 total. Per the
procedure deviation recorded in the dispatch queue's
`review_plan.procedure_deviations` (recorded before the reviewers ran;
ratified by DEC-20260906-7448cf per its text), that object DOES NOT EXIST:
the executor's terminal receipt records zero constructed instances in every
arm (arm-B funnel 80000 draws / 80000 solves_ok / 0 square_ok / 0 found), so
no certified k=3 total exists to re-derive. J2 is therefore RE-SCOPED, not
dropped, to control C3 / invalidation rule IV-3 of the frozen contract:

> C3 BLIND KERNEL RE-DERIVATION: an independent agent re-derives, from the
> STATEMENT of the quantities and the parameters alone, (a) the left kernel
> of W(b) (the n − 5 linear relations from the 5 × n Vandermonde) and
> (b) the delta interpolant, at ≥ 3 seeded b-tuples per arm, and NEVER reads
> the solver's implementation, the producer's notes, or its report.

I adopt the re-scope as dispatched. This section IS the contract's required
C3 artifact (`required_artifacts`: "blind re-derivation report (C3): the
re-deriver's declared sources_read, blind_from attestation, and the compared
quantities"), placed inside this single declared deliverable so the ledger
archive's path set is unchanged.

## J2.1 Permitted inputs actually used (sources_read for the derivation)

- The frozen contract's statement of the quantities:
  `experiments/EXP-ECRANK-76a70d/specification.yaml` —
  `inputs.engine` (delta = Lagrange interpolant with delta(b_i) = d_i;
  W'(b) = D^-1 W(b), left kernel of the 5 × n Vandermonde at b),
  `inputs.b_tuples` (affine normal form b_1 = 0, b_2 = 1; b_3..b_n distinct
  integers in [-20, 20] \ {0,1}), `controls` C3, `invalidation_rules` IV-3.
- The executor's exported `blind_rederivation_inputs_C3` blocks in the three
  arm raw-result files (permitted by the deviation; "exported by the
  contract for exactly this purpose"). Each block entry carries: `b`
(integer strings), `d_pattern` (integers), `stream`, `b_index`, and
  `quantity_statements`:
  - "left kernel of W(b): all c in Q^n with sum_i c_i b_i^t = 0 for t = 0..4 (reduced basis)"
  - "delta interpolant: delta(b_i) = d_i, degree <= n-1"

The block's quantity statements agree with the frozen contract's statement
of C3 (same object, same defining equations). No other input was used for
the derivation.

## J2.2 Quantities as I state them from the contract alone (before any comparison)

For a b-tuple b = (b_1..b_n) of distinct rationals and a pattern d = (d_1..d_n):

(a) **Left kernel of W(b)** — the solution space
K(b) = { c ∈ Q^n : Σ_i c_i · b_i^t = 0 for t = 0, 1, 2, 3, 4 },
i.e. the kernel of the 5 × n Vandermonde map V with V[t][i] = b_i^t. For
distinct b_i every 5 columns of V are independent (Vandermonde
determinant ≠ 0), so rank V = 5 and dim K(b) = n − 5 exactly. These are the
"n − 5 linear relations" of the contract; each y ∈ K(b) yields the quadratic
vanishing condition Σ_i y_i d_i g(b_i)^2 = 0 on g's coefficients (the
engine's ellipticity conditions), and W(b) := K(b)^⊥ is the 5-dimensional
subspace whose D^-1-image W'(b) carries the square-pattern points.

(b) **Delta interpolant** — the unique polynomial delta ∈ Q[x] with
deg ≤ n − 1 and delta(b_i) = d_i for all i (Lagrange interpolation;
uniqueness is standard since the b_i are distinct).

Canonical forms I fixed for my side BEFORE seeing any executor value:

- Kernel: the RREF kernel basis — pivots at columns 0..4 (guaranteed by
  distinctness), free coordinates 5..n−1; for each free coordinate f, the
  basis vector v^(f) with v^(f)_f = 1, v^(f)_(other free) = 0, and pivot
  entries read from the RREF of V. This basis is unique (canonical), so
  equality of "reduced bases" is well-defined; in addition I compare the
  kernel as a SUBSPACE (the basis-independent invariant).
- Delta: the full coefficient vector in ASCENDING order (entry t =
  coefficient of x^t), as exact Fractions in lowest terms.

## J2.3 My independent implementation (named: "re-deriver", this session)

Written in this session from J2.2 alone; exact `fractions.Fraction`
arithmetic only; no floating point; no reuse of any executor code (none was
read). Two independent internal methods per quantity:

- Kernel: exact Gaussian elimination to RREF of the 5 × n integer
  Vandermonde; basis read off free columns. Self-check per basis vector:
  all five moment equations Σ c_i b_i^t = 0 verified exactly, t = 0..4.
- Delta: (i) explicit Lagrange construction Σ_i d_i Π_{j≠i} (x − b_j)/(b_i − b_j)
  by exact polynomial multiplication; (ii) INDEPENDENTLY, solving the n × n
  Vandermonde linear system Σ_t c_t b_i^t = d_i by exact elimination. The
  two methods must agree coefficient-wise; the interpolant is additionally
  verified by exact evaluation delta(b_i) = d_i at every i.

**Controls before belief — known-answer controls on my own instrument, run
BEFORE trusting any comparison (all PASS):**

1. Kernel dimension/rank control: at b = (0,1,2,3,4,5), dim K = 1 and
   rank V = 5, as theory requires.
2. Closed-form relation-vector control (independent of my elimination):
   the classical vector c_i = 1 / Π_{j≠i}(b_i − b_j) kills all moments
   t = 0..n−2 (hence t = 0..4). Verified exactly at n = 6, 8, 10 on test
   tuples, AND verified to lie in the span of my RREF basis for EVERY one
   of the 27 exported tuples (membership by exact reduction against the
   RREF basis; residual zero in all 27 cases). A kernel implementation that
   missed this canonical vector would fail here.
3. Known delta answers: d = (1..1) → delta = 1; d = (b_i) → delta = x;
   d = (b_i^2) → delta = x^2 — verified exactly on test tuples at n = 6 and
   n = 8. (Note d = (1..1) → delta = 1 is also the degenerate-Mestre slice
   of the contract's known-false control; my instrument returns the
   known-correct constant there.)
4. Lagrange vs Vandermonde-solve agreement on every exported tuple (27/27).

Input-domain checks against the frozen contract (all 27 tuples PASS):
b_1 = 0, b_2 = 1; b_3..b_n distinct integers in [-20, 20] \ {0, 1}; all b_i
distinct; arm A n = 6, arm B n = 8, arm C n = 10.

## J2.4 Coverage

Frozen requirement: ≥ 3 seeded b-tuples PER ARM. The exported blocks give
9 per arm (3 coset streams × b_index 0..2, the first three seeded b-tuples
of each stream). I re-derived ALL 27. Coverage: 9 ≥ 3 per arm — SATISFIED.

## J2.5 Re-derived values (my side of the comparison; fixed before any executor output was read)

Conventions: kernel basis vectors listed in free-coordinate order f = 5..n−1,
entries ascending by coordinate index, exact rationals (integers written
bare); delta coefficients ASCENDING (x^0 first), exact rationals.

### Arm A — RUN-ECRANK-76a70d-R2-armA (n = 6, seed 760706; kernel dim 1)

A/s0/b0: b = (0, 1, 5, 11, −17, −14); d = (−21, 3003, −21, 3003, −77, −77)
- kernel basis (f=5): (−4275/187, 665/24, −525/88, 57/88, −2375/4488, 1)
- delta (deg 5): (−21, 1761814933/479655, −954985037/1598850, −270730001/4796550, 14687/3366, 1374007/4796550)

A/s0/b1: b = (0, 1, −18, −7, 19, −13); d = (3003, −77, 77, 3003, 77, −77)
- kernel basis (f=5): (320/57, −260/57, −5824/23199, −20/11, 35/2109, 1)
- delta (deg 5): (3003, −474922221/18720, −75070037/142272, −799897/47424, 10703/7488, 47453/711360)

A/s0/b2: b = (0, 1, 14, 11, −10, 12); d = (91, −91, 21, −91, 21, 91)
- kernel basis (f=5): (−11/35, 24/65, −121/546, −88/105, 1/210, 1)
- delta (deg 5): (91, −71242/429, −546737/28314, 45629/14157, 4793/28314, −245/14157)

A/s1/b0: b = (0, 1, −5, 3, 17, 10); d = (−143, −210, −143, 110, −210, 110)
- kernel basis (f=5): (−441/17, 1225/32, 147/176, −225/16, −675/5984, 1)
- delta (deg 5): (−143, −947351329/6597360, 14158489921/197920800, 1408186559/197920800, −424369609/197920800, 17539399/197920800)

A/s1/b1: b = (0, 1, 11, −17, 9, −1); d = (−143, −210, −143, 143, 143, −210)
- kernel basis (f=5): (−1280/561, 4/3, 4/77, −5/4641, −4/39, 1)
- delta (deg 5): (−143, −15365933/1370880, −22986947/342720, 1102309/97920, 24707/342720, −7377/152320)

A/s1/b2: b = (0, 1, 12, −15, 5, 16); d = (−110, 143, 273, 143, 273, −110)
- kernel basis (f=5): (341/15, −31, −620/189, −11/135, 372/35, 1)
- delta (deg 5): (−110, 1312969/4185, −697048669/11048400, 4612889/2209680, 3161677/11048400, −170413/11048400)

A/s2/b0: b = (0, 1, 4, 7, −13, −15); d = (−5, 26, 390, 390, 26, −5)
- kernel basis (f=5): (3344/91, −1045/21, 880/51, −76/21, −2508/1547, 1)
- delta (deg 5): (−5, 16491697/15519504, 27806114353/931170240, 445898501/931170240, −357632593/931170240, −17604641/931170240)

A/s2/b1: b = (0, 1, 6, 13, −18, −14); d = (5, 5, −5, −26, −5, −26)
- kernel basis (f=5): (−300/13, 504/19, −9/2, 200/403, −525/1178, 1)
- delta (deg 5): (5, 34630003/96478200, −103279403/289434600, −402887/128637600, 195953/192956400, 7841/1157738400)

A/s2/b2: b = (0, 1, −8, 7, 14, −10); d = (26, 26, 390, −3, −3, 390)
- kernel basis (f=5): (561/49, −1360/117, −17/9, 176/147, −85/637, 1)
- delta (deg 5): (26, −9001523/2297295, 390826351/85765680, −312938383/514594080, −2951731/85765680, 406363/102918816)

### Arm B — RUN-ECRANK-76a70d-R3-armB (n = 8, seed 760708; kernel dim 3, free coords 5,6,7)

B/s0/b0: b = (0, 1, 4, −9, 15, 11, −4, 8); d = (−546, −330, 330, 546, −330, −546, 330, 546)
- kernel basis:
  - f=5: (−280/27, 44/3, −200/39, 77/702, −5/18, 1, 0, 0)
  - f=6: (−190/27, 152/21, −475/429, −38/351, 10/693, 0, 1, 0)
  - f=7: (−833/135, 136/15, −1666/429, 98/1755, −34/495, 0, 0, 1)
- delta (deg 7): (−546, 332959957/1815450, 346327183/7780500, −5609211547/435708000, 97523813/108927000, 17006473/217854000, −347819/21785400, 275801/435708000)

B/s0/b1: b = (0, 1, −20, −1, 12, 3, 11, −11); d = (1365, −546, −330, −546, 1365, −330, −1365, −1365)
- kernel basis:
  - f=5: (69/10, −414/77, 9/10640, −621/247, −23/2288, 1, 0, 0)
  - f=6: (31/2, −62/7, 11/2128, −1705/247, −155/208, 0, 1, 0)
  - f=7: (207/2, −345/7, −253/2128, −13662/247, 45/208, 0, 0, 1)
- delta (deg 7): (1365, −6501526273/9103584, −126402116941171/66092019840, 217144868515/300418272, 840908209/600836544, −28614185473/3304600992, 7767123941/66092019840, 74668907/3304600992)

B/s0/b2: b = (0, 1, −12, −3, 7, 2, 12, −17); d = (−1365, −546, −33, −33, −546, −1365, 1365, 1365)
- kernel basis:
  - f=5: (25/18, −175/78, 25/13338, −7/54, −1/57, 1, 0, 0)
  - f=6: (−550/7, 900/13, −275/741, 44/3, −792/133, 0, 1, 0)
  - f=7: (−120, 1190/13, −952/247, 34, −51/19, 0, 0, 1)
- delta (deg 7): (−1365, 30604929071/23094500, −77766818123/277134000, −590689392877/2327925600, 31715007637/1293292000, 6310767919/1662804000, −55053247/352716000, −5290039/363738375)

B/s1/b0: b = (0, 1, −3, 7, 15, 6, −8, 12); d = (−858, 5005, 5005, −1, −858, 210, −1, 210)
- kernel basis:
  - f=5: (9/7, −81/56, −1/8, −81/112, 1/112, 1, 0, 0)
  - f=6: (345/7, −575/14, −23/2, 69/28, −5/28, 0, 1, 0)
  - f=7: (−55/7, 225/28, 11/12, −99/56, −55/168, 0, 0, 1)
- delta (deg 7): (−858, 58133502709/9563400, 216242887349/573804000, −326186340037/491832000, 14621846357/224532000, 140783501/21517650, −118487443/107588250, 383360401/10328472000)

B/s1/b1: b = (0, 1, 17, −5, −3, 8, 13, −9); d = (−858, 5005, −858, −210, 5005, −210, 858, 858)
- kernel basis:
  - f=5: (3003/85, −429/16, −91/1360, 21/5, −273/20, 1, 0, 0)
  - f=6: (4608/85, −39, −351/935, 416/55, −117/5, 0, 1, 0)
  - f=7: (−416/17, 117/8, −27/1496, −117/11, 39/2, 0, 0, 1)
- delta (deg 7): (−858, 36320149/10560, 197434751/78336, −19029277/1436160, −37035793/430848, 1303453/718080, 567469/861696, −3823/130560)

B/s1/b2: b = (0, 1, 9, −6, −10, −9, −17, −15); d = (−210, −1, 210, −1, 858, 858, 210, −210)
- kernel basis:
  - f=5: (1, −243/308, 1/76, −9/14, −243/418, 1, 0, 0)
  - f=6: (−1001/15, 221/4, −1309/1140, 221/10, −1989/190, 0, 1, 0)
  - f=7: (−32, 2025/77, −10/19, 80/7, −1296/209, 0, 0, 1)
- delta (deg 7): (−210, 4186503219/15917440, −817542659/28274400, −207423908093/8595417600, −181441346/151091325, 8225347727/38679379200, 99756961/4834922400, 37911443/77358758400)

B/s2/b0: b = (0, 1, −6, 3, 12, −4, 5, −8); d = (−165, 165, −42, 42, 42, 165, −42, −165)
- kernel basis:
  - f=5: (−140/27, 64/11, −80/243, −320/243, 35/2673, 1, 0, 0)
  - f=6: (−77/27, 5, 10/243, −770/243, −5/243, 0, 1, 0)
  - f=7: (55/3, −160/7, −440/189, 160/27, −2/27, 0, 0, 1)
- delta (deg 7): (−165, 18872663/51480, 96926437/8648640, −5045547977/103783680, −10936333/13837824, 326850479/207567360, 779323/23063040, −2306341/207567360)

B/s2/b1: b = (0, 1, 17, 9, 3, 4, −16, −12); d = (42, −165, 15, 15, 462, 42, 462, −165)
- kernel basis:
  - f=5: (−65/153, 65/64, 15/7616, −13/288, −65/42, 1, 0, 0)
  - f=6: (−5225/9, 15675/16, −475/112, 3553/72, −9350/21, 0, 1, 0)
  - f=7: (−13195/51, 27405/64, −1755/1088, 1885/96, −377/2, 0, 0, 1)
- delta (deg 7): (42, −47701843197/61686625, 1181971088917/1691976000, −2596734494567/20303712000, −46704989/7779200, 4076838533/2537964000, 270463/18096000, −588994391/142125984000)

B/s2/b2: b = (0, 1, 14, 17, 4, −2, −18, −3); d = (165, −42, 15, 462, 15, −42, 462, 165)
- kernel basis:
  - f=5: (−684/119, 76/13, 57/455, −12/221, −76/65, 1, 0, 0)
  - f=6: (−8360/17, 9240/13, 627/13, −5016/221, −3192/13, 0, 1, 0)
  - f=7: (−10, 595/52, 4/13, −7/52, −34/13, 0, 0, 1)
- delta (deg 7): (165, −4693034769/54454400, −7361527961/53747200, 66028372741/12415603200, 2276795011/194754560, −41141776187/49662412800, −566799447/16554137600, 126051451/49662412800)

### Arm C — RUN-ECRANK-76a70d-R5-armC (n = 10, seed 760710; kernel dim 5, free coords 5..9)

C/s0/b0: b = (0, 1, −14, −13, −9, 16, 9, −10, −1, 11); d = (2730, −42, −1430, −22, −2730, −2730, −1430, −22, 2730, −42)
- kernel basis:
  - f=5: (18125/91, −1160/7, −1160/7, 22500/91, −116, 1, 0, 0, 0, 0)
  - f=6: (4048/91, −6831/175, −4752/175, 3726/91, −506/25, 0, 1, 0, 0, 0)
  - f=7: (22/273, −2/35, 11/35, −55/91, −11/15, 0, 0, 1, 0, 0)
  - f=8: (−32/21, 104/175, −32/175, 2/7, −13/75, 0, 0, 0, 1, 0)
  - f=9: (20000/273, −440/7, −352/7, 6875/91, −110/3, 0, 0, 0, 0, 1)
- delta (deg 9): (2730, −26108203819357/19178932500, −53839161578370061/37974286350000, −1037923577293/39972933000, 324108091140263/10126476360000, 5858604009079/4602943800000, −5748611991953/25316190900000, −282930716449/25316190900000, 349731713/726780600000, 3970619927/151897145400000)

C/s0/b1: b = (0, 1, 4, −14, 16, 7, −11, 12, 2, 18); d = (1430, −1430, 22, −22, −22, 22, −1430, 42, 1430, 42)
- kernel basis:
  - f=5: (−243/64, 147/25, −49/16, 1/100, −49/1600, 1, 0, 0, 0, 0)
  - f=6: (−3645/224, 99/5, −33/8, −33/70, 11/160, 0, 1, 0, 0, 0)
  - f=7: (−143/14, 3328/225, −143/27, 176/4725, −143/450, 0, 0, 1, 0, 0)
  - f=8: (1/2, −896/675, −14/81, −1/2025, 1/1350, 0, 0, 0, 1, 0)
  - f=9: (17, −1792/75, 68/9, −17/225, −119/75, 0, 0, 0, 0, 1)
- delta (deg 9): (1430, −2122210433167/218034180, 28198556149401101/3021953734800, −13712432521926143/5180492116800, 23798881266490727/145053779270400, 375301837172959/13186707206400, −222401991536113/64468346342400, −2930560597859/580215117081600, 58867183643/4875757286400, −18889572371/52746828825600)

C/s0/b2: b = (0, 1, 16, 5, −13, 13, −16, 19, 17, 15); d = (−2730, 42, 2730, 42, −42, 2730, 1430, 1430, −42, −2730)
- kernel basis:
  - f=5: (−36/5, 338/35, −676/1595, −169/55, 8/203, 1, 0, 0, 0, 0)
  - f=6: (2142/65, −192/5, −357/1595, 1088/165, −2176/1131, 0, 1, 0, 0, 0)
  - f=7: (1512/65, −152/5, −3192/1595, 456/55, −57/377, 0, 0, 1, 0, 0)
  - f=8: (72/13, −51/7, −408/319, 68/33, −272/7917, 0, 0, 0, 1, 0)
  - f=9: (−49/13, 5, −245/319, −49/33, 25/1131, 0, 0, 0, 0, 1)
- delta (deg 9): (−2730, 4044400733527627/199767760920, −155693895211697865521/6856029554774400, 13692831698266936547/2493101656281600, −492804202751693953/2285343184924800, −410648831801562649/9141372739699200, 8653977510957187/2285343184924800, 86219746553467/3047124246566400, −3661434490999/360843660777600, 6660116936567/27424118219097600)

C/s1/b0: b = (0, 1, 16, 6, 11, −11, −6, −1, 5, 8); d = (−33, 14, 110, −110, −14, −110, −33, −14, 14, 110)
- kernel basis:
  - f=5: (−459/4, 18513/125, −2057/500, −6534/125, 2754/125, 1, 0, 0, 0, 0)
  - f=6: (−119/4, 4488/125, −357/500, −1309/125, 504/125, 0, 1, 0, 0, 0)
  - f=7: (−119/44, 238/125, −7/500, −34/125, 119/1375, 0, 0, 1, 0, 0)
  - f=8: (1/4, −11/25, −1/100, −22/25, 2/25, 0, 0, 0, 1, 0)
  - f=9: (−7/22, 64/125, 7/250, −112/125, −448/1375, 0, 0, 0, 0, 1)
- delta (deg 9): (−33, 1172151371/89535600, 1417045961417/39395664000, 309750740129/354560976000, −615740958583/202606272000, 7657539371/202606272000, 643732619/9209376000, −2049124151/709121952000, −553892257/1418243904000, 9817183/472747968000)

C/s1/b1: b = (0, 1, −17, 14, 3, −5, −15, 7, 6, −6); d = (33, −33, −110, −33, 105, 33, −105, −105, 105, −110)
- kernel basis:
  - f=5: (−1824/119, 760/39, −38/1581, 1440/31031, −57/11, 1, 0, 0, 0, 0)
  - f=6: (−2784/119, 435/13, −348/527, 4320/31031, −116/11, 0, 1, 0, 0, 0)
  - f=7: (−96/17, 392/39, 49/7905, −288/4433, −294/55, 0, 0, 1, 0, 0)
  - f=8: (−460/119, 92/13, 2/527, −1035/31031, −46/11, 0, 0, 0, 1, 0)
  - f=9: (−330/17, 330/13, −21/527, 27/403, −7, 0, 0, 0, 0, 1)
- delta (deg 9): (33, −6160249396294579/57761421157440, 55660232501196241/1732842634723200, 108578729697857753/10397055808339200, −104186940267561961/62382334850035200, −5613729105006461/20794111616678400, 23907207774677/1006166691129600, 1585017479921/678068857065600, −1682858889563/20794111616678400, −392665321747/62382334850035200)

C/s1/b2: b = (0, 1, −12, −9, −20, −14, −17, −19, 18, −4); d = (110, 110, 33, −110, 105, −14, 105, −110, 33, −14)
- kernel basis:
  - f=5: (−5/12, 4/13, −175/104, 28/33, −5/88, 1, 0, 0, 0, 0)
  - f=6: (−1, 68/91, −51/26, 17/11, −51/154, 0, 1, 0, 0, 0)
  - f=7: (−35/54, 19/39, −475/468, 266/297, −95/132, 0, 0, 1, 0, 0)
  - f=8: (969/4, −18468/91, 8721/104, −1292/11, −4131/616, 0, 0, 0, 1, 0)
  - f=9: (−40/27, 256/273, 50/117, −256/297, −5/231, 0, 0, 0, 0, 1)
- delta (deg 9): (110, −195600636669623/1291998708000, 3685112376682817/58139941860000, 39634124506989433/558143441856000, 43770771151657337/2790717209280000, 854577319292813/656639343360000, 49228265840219/2790717209280000, −20021651735209/5581434418560000, −20504269447/99668471760000, −37953666367/11162868837120000)

C/s2/b0: b = (0, 1, −12, 17, −7, −16, 6, 7, −17, 12); d = (15015, 15015, 462, 13, 13, −462, 10, 10, −462, 462)
- kernel basis:
  - f=5: (−99/7, 297/26, −6732/1885, −3/58, 187/35, 1, 0, 0, 0, 0)
  - f=6: (2145/238, −297/32, 11/58, −585/15776, −99/112, 0, 1, 0, 0, 0)
  - f=7: (190/17, −4655/416, 98/377, −931/15776, −19/16, 0, 0, 1, 0, 0)
  - f=8: (−150/7, 7225/416, −1734/377, −75/928, 867/112, 0, 0, 0, 1, 0)
  - f=9: (2090/119, −855/52, 209/377, −627/1972, −33/14, 0, 0, 0, 0, 1)
- delta (deg 9): (15015, 7813050933483703/8539995063600, −198418025645730971/225835425015200, −602451691237809869/11257027339219200, 75961361436252023/4645757314598400, 22806386530471/22885504012800, −244385980906919/2322878657299200, −11346264319/1763318818800, 6585027992849/32520301202188800, 145422156631/11707308432787968)

C/s2/b1: b = (0, 1, 18, −2, −7, 3, −16, −6, −1, −4); d = (10, −462, 15015, −13, −462, −10, 15015, −13, 10, −10)
- kernel basis:
  - f=5: (125/21, −375/68, −1/510, −3/2, 9/140, 1, 0, 0, 0, 0)
  - f=6: (−289, 168, −28/125, 3468/25, −2312/125, 0, 1, 0, 0, 0)
  - f=7: (8/3, −24/17, 7/6375, −42/25, −72/125, 0, 0, 1, 0, 0)
  - f=8: (−19/21, 19/68, −1/12750, −19/50, 19/3500, 0, 0, 0, 1, 0)
  - f=9: (55/21, −22/17, 1/1275, −11/5, −22/175, 0, 0, 0, 0, 1)
- delta (deg 9): (10, −5648481231847/38052630000, −22412050203047/91326312000, −38959425019433/391398480000, 38996638409593/5479578720000, 11823796680319/996287040000, 3145823894761/1369894680000, 86335568917/782796960000, −37499725817/5479578720000, −5121972287/10959157440000)

C/s2/b2: b = (0, 1, −4, −11, −3, −12, 4, −1, −20, 18); d = (13, 10, 15015, 15015, −10, −13, −10, 10, −13, 13)
- kernel basis:
  - f=5: (78/11, −18/5, 351/35, −117/77, −13, 1, 0, 0, 0, 0)
  - f=6: (210/11, −14, 9, −1/11, −15, 0, 1, 0, 0, 0)
  - f=7: (−10/11, 1/4, 2/7, −1/616, −5/8, 0, 0, 1, 0, 0)
  - f=8: (4284/11, −204, 459, −170/11, −630, 0, 0, 0, 1, 0)
  - f=9: (3451/2, −20097/20, 13311/10, −153/8, −16269/8, 0, 0, 0, 0, 1)
- delta (deg 9): (13, −357369289994989/399058179520, −3261857642070067/14366094462720, 164533750305441149/172393133552640, 489642791705836963/2068717602631680, −8352817514337133/142670179491840, −26218523819110067/2068717602631680, −344965357881299/1034358801315840, 1204371304183/32323712541120, 6360684760429/4137435205263360)

## J2.6 Comparison against the executor's recorded solver output

STATUS AT TIME OF WRITING THE DERIVATION: PENDING — the comparison step had
not yet been performed, because every location where the executor's solver
values could be recorded lies inside blind_from. The derivation above was
computed and written to this file FIRST. The comparison (and its outcome,
per quantity, with exact arithmetic on any disagreement) is appended below
in Section J2.7 after the blind phase was lifted.

## J2.7 Comparison outcome (appended post-blind; read order attested above)

Phase-3 sources opened for the comparison (after J2.5 was on disk):
`runs/*/raw-result.json` full contents (search for recorded per-b solver
values), `experiments/EXP-ECRANK-76a70d/source/ecrank_engine.py`
(`vandermonde_kernel` at line 695, `lagrange_interp` at line 494), and the
three arm raw-result files in full.

**Where the executor's values live.** The executor's raw results record NO
per-b kernel bases or delta coefficient vectors — the
`blind_rederivation_inputs_C3` blocks export only the quantity statements
and the parameters (b, d_pattern, stream, b_index). The recorded solver
side of IV-3 is therefore its committed implementation itself, bound
byte-for-byte at the snapshot commit
(`source/ecrank_engine.py` sha256
483ade5887b23d3014438676a883c75fab8167d057ac19ed7b62cb35e548707d; verified
below in J1 to equal both the snapshot blob and the run-time hash recorded
in every manifest). Comparison procedure, disclosed: I loaded that committed
module (post-derivation) and ran `vandermonde_kernel(b)` and
`lagrange_interp(b, d)` on exactly the 27 exported (b, d_pattern) tuples,
and compared against my blind values of J2.5. Reading the solver's code
ONLY identifies the defining equations (they match the statements verbatim:
kernel = {c : Σ_i c_i b_i^j = 0, j = 0..4}, RREF reduced basis on free
columns; delta = exact Lagrange interpolant); the compared numbers on my
side were fixed and written before the module was opened, and three anchor
literals transcribed back from J2.5 (arm A s0/b0 kernel+delta, arm B s0/b0
kernel first vector+delta, arm C s0/b0 kernel first vector+delta) were
asserted equal to my implementation's output inside the comparison script,
tying the comparison to the written blind values.

**Result: 27 / 27 tuples EXACT MATCH.** For every tuple in every arm:

- kernel: the executor's reduced basis equals my RREF basis vector-by-vector,
  entry-by-entry, as exact Fractions (arm A: 1 vector × 9 tuples; arm B:
  3 vectors × 9; arm C: 5 vectors × 9);
- delta: the executor's coefficient vector equals mine coefficient-by-
  coefficient as exact Fractions (degrees 5/7/9 at n = 6/8/10, all 27).

No disagreement exists, so IV-3 is UNTRIGGERED and nothing localises to
either implementation. Falsification route for this verdict: any later
re-run of the comparison script against a different
`ecrank_engine.py` byte-set (different sha256) or different exported
`blind_rederivation_inputs_C3` blocks that produces a mismatch would
overturn it; the values in J2.5 are reproducible from the statements and
parameters alone by any third implementation.

**Coverage and discharge.** 9 seeded b-tuples per arm (≥ 3 required); the
first three b-indices of each of the 3 coset streams per arm. This section
discharges BOTH the review-architecture blind re-derivation obligation
(J2 as re-scoped) and the contract's C3 control artifact
(`required_artifacts`: re-deriver's declared sources_read — J2.1;
blind_from attestation — header attestation; compared quantities — J2.5 +
J2.7), per the recorded procedure deviation.

## J2.8 J2 verdict

**J2: PASS.** The blind re-derivation was computed and written before any
blind_from source was opened (order attested; file committed to disk in
Phase 2); the two named implementations — the executor's snapshot-bound
`ecrank_engine.py` and this session's independent re-derivation — agree
exactly on all 27 exported tuples for both C3 quantities; instrument
controls passed on known-answer objects before the comparison; IV-3 is
untriggered. No BLOCK item.

---

# J1 — Run-record integrity and determinism

Performed in Phase 3, after the J2 derivation was committed to this file.
All eight runs under `experiments/EXP-ECRANK-76a70d/runs/` were re-parsed
from the snapshot-bound bytes.

## J1.1 Artifact-policy re-parse (all 8 manifests)

Per-run check against the AGENTS.md artifact policy; every item located by
path + field (`runs/RUN-*/manifest.yaml`, nested `run:` record):

| policy item | field | present in all 8 |
|---|---|---|
| exact command | `code.command`, `code.argv`, companion `command.txt` | YES |
| git commit + dirty state | `code.commit` (903b55b93bbb... in all 8), `code.dirty: true`, `code.dirty_files` (untracked runs/ + source/; honest — workers never commit) | YES |
| environment + dependency versions | `environment` block + companion `environment.json` (CPython 3.12.8, macOS-26.6-arm64, pyyaml 6.0.3 serialization-only, stdlib_only_pipeline true, pari_in_pipeline false, cypari absent, network none) | YES |
| input parameters and seeds | `inputs.parameters` (arm, arm_seed, n, n_b_declared, draws_per_b, H_schedule_per_draw, S/T indices, IC list; scan box+alpha; known-false expected totals; planted levels) + `inputs.seeds_note` | YES |
| inference manifest | `inference` block in all 8: requested_policy executor-implementation, backend opencode api_direct (fireworks), resolved_model_id fireworks-ai/accounts/fireworks/models/qwen3p8-max with source note, model_verified false + note, reasoning effort fields, fallback_used true + reason, degraded_allowed false, degraded_requirements [], bedrock guard recorded | YES |
| stdout/stderr complete | `runs/*/stdout.log` (82–518 B JSON summaries, well-formed, consistent with manifests), `runs/*/stderr.log` (0 bytes in all 8 — consistent with clean completions; no truncation markers) | YES |
| raw machine-readable results | `runs/*/raw-result.json` (per-stream funnels, cosets, op counters, blind blocks; scan parameters; known-false per-b totals + anchors + IV1 flag; planted records + certificates + IV2 flag) | YES |
| validity status and reason | `status` + `result.validity_reason` in all 8 (7 × completed, 1 × completed_not_evaluable for R6) | YES |
| timestamps + resources | `timing.started_at/finished_at/wall_seconds`; `resources.peak_rss_bytes/peak_rss_gb`; `cpu_seconds: null` with explicit never-guessed note (rule 9 compliant); counted ops in `result.metrics.counted_exact_ops` with cap/memory flags | YES |
| run-time source hashes | `code.source_sha256` for all 8 driver/engine files in every manifest | YES |

Seed verification against the frozen `replication.seeds`
[760706, 760708, 760710, 760711, 760712]: arm A 760706 ✓, arm B 760708 ✓,
replay 760708 with `replay_of` naming R3's raw-result ✓, arm C 760710 ✓,
scan 760711 ✓, known-false 760712 ✓, planted derives from 760708 only ✓.
No seed adjustment anywhere. See OBS-2 for the R1 smoke seed.

## J1.2 Snapshot and code-integrity binding

- All 8 `code.source_sha256` maps were compared against (a) the current
  tree and (b) the blobs at snapshot commit
  `a20a49b6adbcce51893c1221dbd69cdcd486ad9d`: all equal, all 8 files
  (certify76.py 9be509b1…, ecrank_engine.py 483ade58…, run_arm.py
  8f58cf2c…, run_common.py 704d2f9d…, run_known_false.py 63c8d48e…,
  run_planted.py 7bf05c38…, run_r1_smoke.py eb8863ab…, run_scan.py
  e32405ee…). The engine that produced arms A/B/C is byte-identical in
  every manifest and at the snapshot.
- run_planted.py differs between the R1–R7 manifests (e56a3ed0…,
  then-current) and R8 (7bf05c38…, post-revision): disclosed per-run
  provenance in `execution-report.yaml: procedural_notes`, consistent with
  the preserved R8 attempt history; not an inconsistency.
- Snapshot receipt (`archives/TASK-20260906-cf7fcf/snapshot-receipt.json`):
  213 path hashes + the receipt itself = the declared 214 paths; spot-check
  of 5 paths (R3 manifest, R3 raw-result, R4 determinism-diff.txt, R5
  ckpt-014, execution-report.yaml) — recorded sha256 == actual bytes, all
  True. `commit_sha`/`parent_sha` null by construction (receipt is
  committed inside the snapshot commit; backfilled in the verified
  follow-up 268756be0, which states all 214 hashes verified).
- The committed certifier pin was checked: `exact_certify.py` at the path
  named in every manifest hashes to the pinned
  1bc7c05954fdf9531c41eb942e91f918e401098971b2211501a9628ae011ea8e ✓.

## J1.3 Checkpoint cadence and op counters

- The contract cadence ("checkpoint every 10^7 counted ops") is implemented
  in `source/ecrank_engine.py:1185` (`Checkpointer(every_ops=10**7)`,
  docstring cites the contract floor) plus finer b-interval flushes every
  500 b-tuples (`run_arm.py:259-261`) — a superset of the required cadence.
- It APPEARS IN THE RAW OUTPUTS: arm C crossed 10^7 ops and flushed
  `runs/RUN-ECRANK-76a70d-R5-armC/checkpoints/ckpt-014-ops_10000069.json`
  (ops-boundary tag). Arms A/B/replay never reached 10^7 ops (5.3e5 /
  8.68e6 / 8.68e6), so no ops-boundary checkpoint was due there; R7 (1.8e6)
  and R8 (5.0e6) likewise; R6 counted 0 ops.
- Per-run checkpoint verification: op counters monotone in every checkpoint
  series; every inter-checkpoint delta ≤ 10^7 (max observed 1,162,380,
  arm C); final checkpoint ops == raw-result `ops_counted_total` ==
  manifest `result.metrics.counted_exact_ops` in all four arm runs
  (531,610 / 8,683,560 / 8,683,560 / 13,940,808). Checkpoint state carries
  `found`, `level_counts`, `exhaustion`, `streams_completed` — the
  completed-prefix data the stopping rules require.
- All totals sit far inside the frozen 1.0e8 cap and the recorded wall
  times inside 7200 s; `ops_cap_respected`/`memory_ceiling_respected` true
  in all 8 (max peak 0.049 GB vs 8 GB ceiling).

## J1.4 Arm-B determinism (R3 vs R4) — from recorded artifacts AND an independent scratch replay

From the recorded artifacts:

- `runs/RUN-ECRANK-76a70d-R4-armB-replay/determinism-diff.txt`:
  IV7_fired false, bit_for_bit_match true, first_divergence null,
  orig_n = rerun_n = 0, orig/rerun sha256 both
  4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945.
  I verified this digest is exactly sha256("[]") — the canonical
  serialization of the EMPTY instance list. The recorded bit-for-bit claim
  is therefore TRUE but trivially satisfied: both sides compare an empty
  list. Noted, not a defect — but it makes the broader comparison below
  the load-bearing evidence.
- Counted-op totals identical: R3 == R4 == 8,683,560 (manifests, raw
  results, final checkpoints, stdout).
- Full raw-result comparison R3 vs R4: every shared top-level field is
  exactly equal (streams with all per-stream funnel counters, arm_cosets,
  blind_rederivation_inputs_C3 blocks, level/cumulative counts, dedup_C6)
  EXCEPT `parameters`, whose ONLY differing subkeys are `run_kind`
  (arm_B vs arm_B_determinism_rerun) and `replay_of` (null vs R3's
  raw-result path) — the identity fields a replay must carry. R4 adds only
  `determinism_IV7`. Checkpoint op series identical (19 checkpoints, same
  ops at every index).

Independent scratch replay (this session; my ONE permitted run; nothing
written inside `experiments/`):

- Setup: scratch root `/Volumes/SSD990/llm/tmp/opencode/validator-369b8d-scratch`
  with copies of the 8 snapshot-bound source files (hashes re-verified),
  R3's raw-result as the replay input, and the committed `exact_certify.py`
  (hash == pin). Interpreter: CPython 3.12.8 — the recorded version.
- Command (recorded verbatim): `ECRANK_REPO_ROOT=<scratch> PYTHONHASHSEED=0
  python3 experiments/EXP-ECRANK-76a70d/source/run_arm.py --arm B --run-id
  RUN-ECRANK-76a70d-RVAL-scratch --replay-of
  experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json`
  run with cwd = scratch root (the driver's `ECRANK_REPO_ROOT` env knob,
  `run_common.py:28`, confines ALL writes to the scratch tree; exit 0,
  wall ~25 s; the driver's git_info recorded a non-fatal "not a git
  repository" error inside the scratch manifest, as designed).
- Result: status completed, "determinism re-run: instance list bit-for-bit
  MATCH", ops 8,683,560. My replay's raw-result equals R3's on EVERY
  shared field (streams, arm_cosets, blind blocks, counts, dedup) except
  the same two identity parameters (run_kind, replay_of) and the added
  determinism block; its 19-checkpoint op series is identical to R3's
  entry-by-entry. The driver recomputed the sha256 comparison against the
  committed R3 list: match, IV7 not fired.
- Conclusion: the arm-B pipeline reproduces the recorded run from the
  committed bytes + frozen seed alone, in a fresh process on a disjoint
  write root — determinism verified INDEPENDENTLY, not merely from the
  executor's own diff artifact. IV-7 untriggered.

## J1.5 Exhaustion is never reported as a result

- `exhaustion: null` in all four arm raw-results (R2/R3/R4/R5) and in
  every arm checkpoint file; key absent in R1/R6/R7/R8 (run kinds the
  field does not apply to). No run's stdout/manifest/raw-result contains
  an exhaustion report; all three arms record "full pre-registered sample
  executed" (1000/10000/10000 b-tuples; final-checkpoint
  streams_completed [334,333,333] arm A, [3334,3333,3333] arms B/C), and
  the execution report's budget block records
  `exhaustion_events: none`. The dispatch note says the receipt reports
  none — CONFIRMED against the raw records.
- The one non-completed status, R6 `completed_not_evaluable`, is inertness
  (zero constructed instances ⇒ no matched-shape scan input), classified
  as not-evaluable with 0 counted ops and explicitly "not upgraded to a
  result" (manifest verifier string; execution report). This is the
  honest-classification behavior the stopping rules require, not an
  exhaustion re-scored as anything.
- Preserved failed attempts (R1: attempt-1-crashed, attempt-2-S10-coset-
  closure-bug; R8: attempt-1-height-bug, attempt-2-wrong-cwd,
  attempt-3-accounting-key-bug) exist on disk with NOTE.txt causes and are
  classified as implementation failures, never as evidence (rule 5
  compliance visible in the records; attempt-3's collided certificates are
  quarantined and marked non-citable).

## J1.6 Pre-archive repair TASK-20260906-546d17 — moved without altering?

Boundary (per `ledger/handoffs/TASK-20260906-546d17.yaml`): re-shape the
eight FLAT worker manifests into the nested `run:` schema of
`tools/validate_ledger.py` and derive the companions `command.txt` (from
`code.command`) and `environment.json` (from the `environment` block),
"WITHOUT altering one recorded value"; same snapshot commit binds the
repaired bytes.

- Pre/post byte diff: NOT PERFORMED — the pre-repair flat manifests were
  never committed (git history shows exactly ONE commit touching
  `runs/*/manifest.yaml`: the snapshot a20a49b6a), so no pre-repair bytes
  exist to diff against. Recorded as not performed with this reason; the
  following direct checks substitute.
- Companion derivation parity: for all 8 runs, `command.txt` ==
  `run.code.command` exactly, and `environment.json` == the
  `run.environment` block key-for-key, value-for-value (programmatic
  check, 8/8 True both). The derived files introduce nothing.
- Cross-file value parity: the repaired manifests were compared against
  the executor's `execution-report.yaml` (a DIFFERENT file, outside the
  repair's write_scope `runs/`, so untouched by it) on status,
  validity_reason, counted ops, wall_seconds, peak_rss_gb, started_at,
  finished_at, and command for all 8 runs: 7/8 ALL MATCH; the single
  divergence (R6 validity_reason: manifest carries the short text, the
  report's run_inventory carries an expanded prose) was RESOLVED against
  the driver source: `run_scan.py:95-98` records the short string verbatim
  ("arm-B found zero constructed instances: no matched-shape source; F6
  not evaluable (honest report, inert)"), so the manifest preserves the
  driver's recorded value and the report field is the report's own prose —
  a pre-existing wording divergence, NOT a repair alteration (OBS-4).
- Schema-conformance side effects: fields the runs never recorded appear
  as explicit nulls with sibling notes (`cpu_seconds`), and
  `result.certificate.kind: "none"` with a verifier string naming the
  actual descent-free stack — consistent with the repair handoff's
  constraints (no overclaim, no backfill).
- Gap: the manifests' `schema_repair.note` points to "the repair task's
  output record" for the per-run field mapping; no such record exists in
  the tree (task directory TASK-20260906-546d17 contains only
  task_card.yaml; no receipt file elsewhere located). Flagged as OBS-5;
  the direct checks above cover what the mapping would evidence.
- Verdict on the repair: within what is checkable from committed bytes,
  the repair MOVED fields without altering, inventing, or dropping a
  recorded value.

## J1.7 Timer-field semantics (OBS-1, resolved from code)

`wall_seconds` is systematically smaller than finished_at − started_at
(by ~1.3–1.55 s in R1–R5/R7/R8; 1.552 s vs 0.001 in R6). Cause located in
`run_common.py:93-160`: `started_at` is stamped at the TOP of `open_run`,
before its own bookkeeping (two `git` subprocess calls, env probe, 8
source-file sha256 hashes); `t0 = time.monotonic()` is taken at the END of
`open_run`; `wall_seconds` measures from that t0. So the two fields
measure different, adjacent intervals by construction — the gap is
open_run's own setup, roughly constant per run. R6's 0.001 s is the
not-evaluable path finalizing ~1 ms after its t0 (a fast json.load of
R3's raw-result between them). No fabricated or impossible values; noted
so no later reader mistakes the gap for inconsistency.

## J1.8 Further observations (no adjudication beyond J1)

- OBS-2: R1 smoke records seed `rng_s5_s6: 760701`, which is NOT in the
  frozen `replication.seeds` list; the boilerplate `seeds_note` ("all
  seeds derive from replication.seeds") is literally inaccurate for R1.
  The smoke run is a self-test on committed fixtures, not a measurement;
  all measurement-run seeds match the frozen list exactly. Falsification
  route if this were load-bearing: any measurement run whose seed is not
  in the frozen list — none exists.
- OBS-3 (REFERRED TO J4, not owned here): measured counted ops per b-tuple
  (~868 arm B; ~1394 arm C) run ~an order of magnitude below the design's
  ~7.2×10^3 ops/b estimate and the `per_b_declared_ops: 10000` parameter.
  The cap was never approached (max arm total 1.39×10^7 vs 1.0×10^8), so
  no silent cap breach exists in these records; whether the IC-1 counting
  convention measures what the cost model assumes is the J4 owner's
  question (Coordinator prior point iii). I verified the COUNTERS are
  internally consistent (J1.3); I did NOT validate the cost model.
- OBS-6 (facts recorded; adjudication belongs to J3/Coordinator): R7's
  raw-result records `IV1_fired: true`. The void-trigger condition of
  IV-1 ("pipeline reports certified total = n at d = (1..1)") occurred
  ZERO times in the raw record (`any_total_equals_n: false`; histograms
  {5:5, 6:6, 7:9} at n=8 and {7:2, 8:3, 9:15} at n=10 over b_per_n=20);
  the committed fixture anchors reproduced exactly (7 at n=8, 9 at n=10,
  `matches_expected: true`); 40 certificates present, and the
  post-finalization diagnostics file exists with the recorded sha256
  ea6c172c… (verified). The executor recorded two readings of the frozen
  wording (strict expectation vs void trigger) for the Coordinator, and
  the run records are internally consistent under both. My J1 verdict on
  record integrity does not depend on that adjudication; likewise R8's
  `certified_aggregates_observed` {2,3,4,5} are recorded as observations
  with their note. Nothing here promotes or demotes any control outcome.
- OBS-7: `source/__pycache__/*.pyc` and an EMPTY stray directory skeleton
  `source/experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R8-planted/`
  (0 files; the attempt-2 wrong-cwd artifact of `open_run`'s makedirs)
  exist in the tree but are OUTSIDE the snapshot's 213-hash binding
  (excluded per `excluded_paths_note` and the
  `artifact_inventory_amendment`, which inventoried via
  `git ls-files --others --exclude-standard`). Harmless, but the stray
  directory should be swept by whoever owns source/ next.
- R8 raw/report reconciliation (checked because the counts differ by 9):
  `planted_records` holds 1170 entries = 1161 plant records + 9
  background-draw summary records (`kind: background_draws`, hits 0 ==
  the report's `background_draw_hits: 0`); per-instance plant counts
  [52,52,62,67,102,136,136,232,322] sum to 1161 == report
  `plants_total`; and `cumulative_counts_per_level` {100:18, 1000:214,
  10000:1161} equals EXACTLY the count of plant records whose realized
  `planted_height` ≤ H (recomputed: 18/214/1161); max realized height
  9999 ≤ 10^4 (family cut respected). No discrepancy.
- Run-count/budget: 8 finalized run records == frozen `maximum_runs` 8;
  the slot-(8) wording tension (planted control executed under the
  repair-margin slot) is disclosed by the executor in
  `inventory_accounting_note` and left to the Coordinator — recorded, not
  adjudicated here.
- R2 arm-A local-solvability diagnostic: 1000/1000 b-tuples carry
  `local_solvability_list` entries in the raw streams, matching the
  execution report's aggregates source statement. Content interpretation
  is outside J1.

## J1.9 J1 verdict

**J1: PASS with observations OBS-1..OBS-7 (none blocking).** The eight run
records are complete against the artifact policy, bound byte-for-byte at
the snapshot commit, internally consistent across manifest ↔ raw-result ↔
checkpoint ↔ stdout ↔ execution-report, deterministic under both the
recorded artifacts and an independent scratch replay from the committed
bytes, cadence-conformant, within every frozen cap, and free of any
exhaustion-as-result misreporting; the pre-archive repair preserved every
checkable recorded value. No BLOCK item. Falsification routes: OBS items
carry theirs inline; the determinism verdict would be overturned by any
future replay from the snapshot bytes + seed 760708 diverging on any
shared field (script and scratch recipe recorded in J1.4 for repetition).

---

# Completion-gate self-check and budget accounting

- Per-joint verdicts with evidence pointers: J2.8 (PASS), J1.9 (PASS with
  observations) — pointers inline throughout.
- Blind re-derivation written before any blind_from source was opened,
  values compared: J2.5 (written in Phase 2, file on disk before Phase 3)
  + J2.7 (comparison, 27/27 exact match); read order attested in the
  header.
- BLOCK items: NONE. Observations OBS-1..OBS-7 carry falsification routes
  where applicable; OBS-3 is referred to the J4 owner; OBS-6 records facts
  for the J3 owner and the Coordinator without adjudication.
- Budget: 1 run consumed of maximum_runs 1 (the scratch arm-B replay);
  wall well inside 7200 s; memory trivial; no Bedrock provider touched.
- write_scope compliance: the ONLY repository write is this file. The
  scratch replay wrote solely under
  /Volumes/SSD990/llm/tmp/opencode/validator-369b8d-scratch (the
  dispatch-sanctioned scratch area, chosen precisely because re-running
  the driver in place would write inside `experiments/`, outside my
  write_scope). Nothing committed (workers never commit).
- Status changes / promotions: NONE made. This report touches no
  hypothesis, experiment, or goal state, promotes no claim (C1 untouched),
  closes nothing, and does not touch the UNPROMOTED closure candidate of
  DEC-20260905-7adca0. IV-1 adjudication, slot-(8) accounting, F-label
  mapping, and round composition are Coordinator work.

# Full attestation of reads (final)

In order: (1) task_card.yaml; (2) ledger/handoffs/TASK-20260906-369b8d.yaml;
(3) ledger/decisions/DEC-20260906-69749a.yaml; (4) dispatch_queue.json (my
task entry + procedure_deviations; later the 546d17/908f6b entries and the
archive receipt); (5) specification.yaml; (6) directory listings (names
only) of the experiment tree; (7) ONLY the blind_rederivation_inputs_C3
blocks of the three arm raw-results; [J2 derivation computed and WRITTEN
HERE]; (8) post-blind, in service of J2.7/J1: full raw-result.json of all
eight runs, execution-report.yaml, all eight manifest.yaml, all eight
command.txt/environment.json/stdout.log/stderr.log (sizes+contents), the
checkpoint directories and files of R2/R3/R4/R5, determinism-diff.txt,
source/ecrank_engine.py (kernel/delta/checkpointer sections),
source/run_common.py (open_run/finalize_run/git_info/env_info),
source/run_arm.py and source/run_scan.py (control-flow sections cited),
certificates/ directory listings (counts only), the R7 diagnostics file
(hash), ledger/handoffs/TASK-20260906-546d17.yaml,
archives/TASK-20260906-cf7fcf/snapshot-receipt.json, and git history/blob
queries on the snapshot commit. NOT read at any point:
coordination/goals/GOAL-ECRANK-002/batches/BATCH-07e367/tasks/TASK-20260906-a2eb0c/
(the red-team's task directory — within-round blindness held); no bus
messages were sent or relied on; no approval, status change, or
attestation is claimed by this report.
