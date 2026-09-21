# Independent Validator Report — BATCH-121 committed analyses and DEC-20260805-364e9e

**Task:** TASK-20260806-39f832 (validator, independent session)
**Batch:** BATCH-e0ccb2 (review-only)
**Goal:** GOAL-ECDLP-001
**Reviewed (committed, read-only):**
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/tasks/TASK-20260805-004/oracle_hpseudo_analysis.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/tasks/TASK-20260805-005/closure_and_multi_target.md`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-121/archives/TASK-20260805-006/snapshot_receipt.md`
- `ledger/decisions/DEC-20260805-364e9e.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-e0ccb2/batch.yaml`

**Method.** All stated quantities were independently recomputed (curve orders, multiplicative
orders, the duplication formula, L[1/2] values, and every K* table cell) with a fresh
verification script; git provenance was checked against the commit graph. No research
experiment was run; the arithmetic checks are pure verification computations.

---

## Check 1 — Snapshot binding and provenance

**VERDICT: revise**

- The two analysis files, the DEC, and the snapshot receipt were committed together in a
  single commit `32a0d119e7550279dedbf47e8b16c94d8df51c9b` ("research: BATCH-121
  DEC-20260805-364e9e oracle/multi-target analyses"), which changed exactly the four
  declared paths (685 insertions). The commit is reachable from `HEAD` and is an ancestor
  of `origin/main` (the batch's claim that the content is "already committed on main"
  holds for `origin/main`; local `main` is 528 commits behind — a worktree fetch state,
  not a defect in the reviewed documents).
- On-disk blob hashes match the committed blobs exactly:
  - `oracle_hpseudo_analysis.md` → `0d884f17f2dd8756e0f818b8eb39901a6078e5c8`
  - `closure_and_multi_target.md` → `7a8fdd596cdfd1da86cc675e19926e33c4ebe900`
  - `DEC-20260805-364e9e.yaml` → `e9b72a1b6c99e9de1b3d5d1443d07e3848edc67e`
  - `snapshot_receipt.md` → `e1a3a5a184ef05ff6800bb72f07e68423c16ec34`
  Working tree is clean for these paths. The receipt records no per-file hashes (only
  paths/tasks/producers), so the binding rests on the commit; that binding is verified.
- **Defect (provenance):** the receipt's "Parent: `b72cf155` (BATCH-120 content
  committed, pushed as `cursor/ecdlp-batch-120-continue`)" names a commit that **does not
  exist** in the repository (`git cat-file -t b72cf155` → invalid object). The actual
  parent of the snapshot commit is `61db44b660c5f21217e4390d9c674011e50f874e` (an
  events-digest commit). The "Base commit checked: `b72cfab78`" line is plausible
  (`b72cfab78` exists, is the BATCH-120 content commit, and is an ancestor of the
  snapshot), but the parent line is wrong as recorded. The receipt's "No external main
  changes to merge" is not independently verifiable and the history between `b72cfab78`
  and the snapshot contains main merges.

## Check 2 — L[1/2, sqrt(2)] exponent (oracle doc Q1; DEC)

**VERDICT: pass**

- `ln N = 256·ln 2 = 177.4457`, `ln ln N = 5.1787`, `sqrt(ln N · ln ln N) = 30.3139`.
- `L[1/2, sqrt(2)] = exp(sqrt(2)·30.3139) = exp(42.870) = 2^61.85`. The doc's
  "≈ exp(42.8) ≈ 2^61.7" is a rounding of 2^61.85 down to 2^61.7 — acceptable within
  "≈" (0.15 bits).
- `N^{1/2} = 2^128 = exp(88.72)`; doc's "exp(88.7)" ✓. `2^61.85 << 2^128` ✓.
- The claim "sub-rho means cost < O(sqrt(N))" is loosely worded (should be
  `o(sqrt(N))`/`< sqrt(N)` asymptotically) but the intent and the comparison are correct.

## Check 3 — ord_q(2) = Ω(sqrt(q)) bound and toy checks (closure doc A.2/A.3)

**VERDICT: PASS (toy arithmetic); the bound is a heuristic with a loose citation**

- Test curve `y² = x³ + 3x + 7` over F_1009: independently recomputed `#E = 952 =
  2³·7·17` ✓, `q = 17` ✓, `ord_17(2) = 8` ✓, `sqrt(17) = 4.123` ✓, ratio `1.940` ✓.
- All five random curves (654,114), (25,759), (281,250), (228,142), (754,104) reproduce
  exactly: N = 1064/1008/994/1070/1044, q = 19/7/71/107/29, ord_q(2) = 18/3/35/106/28,
  ratios 4.129/1.134/4.154/10.247/5.199 — every cell matches. All five satisfy
  `ord_q(2) ≥ sqrt(q)` ✓. The doc correctly labels this toy-scale and flags q=7 as a
  borderline outlier.
- The generic claim "ord_q(2) = Ω(sqrt(q)) generically" is a heuristic (the doc says
  so). The citation is loose: Hooley's conditional proof of Artin's conjecture concerns
  `ord_q(2) = q−1` (primitive root), which is far stronger than `ord ≥ sqrt(q)`, and
  "the minimum is bounded away from sqrt(q) for all but a vanishingly small fraction of
  primes" is not established by the cited results as stated. The toy check is honest
  evidence but weak (5 curves at one prime).
- **Scope note:** the ord_q(2) analysis is *irrelevant* to the oracle's power — see
  Check 6. The bound's correctness does not rescue the closure.

## Check 4 — K*(BKK) crossover formula and tables (closure doc B)

**VERDICT: PASS (formula and derivation); REVISE (two table cells, floating-point artifacts)**

- `K*(std) = ⌈s/(1−t)⌉` and `K*(BKK) = ⌈s·β/(1−t·β)⌉` with `β = 2/(m+1)` are correctly
  derived; the ratio `β(1−t)/(1−t·β)` is correct; the rescue condition `t·β < 1 ⟺
  t < (m+1)/2` and the B.5 table `[1,2.00)/[1,2.50)/[1,3.00)` are correct; B.7's
  `K*(BKK) ≈ K*(std)·2/(m+1)` for small t is correct.
- 34 of 36 table cells verified exactly. Two cells are off by one due to binary
  floating-point `ceil` artifacts:
  - `K*(std)` at `s=200, t=0.9`: doc says **2001**, exact value is **2000**
    (`200/0.1 = 2000` exactly; FP gives `2000.0000000000005`). Appears in all three
    tables and is inherited by the DEC's "K* drops 2001 → 96" (correct: 2000 → 96).
  - `K*(BKK)` at `m=4, s=200, t=0.9`: doc says **126**, exact value is **125**
    (`80/0.64 = 125` exactly).
  - The stated ratios (0.091, 0.063, 0.048) round to the same values under the
    corrected cells, so no downstream conclusion changes.
- **Minor internal inconsistency (B.6):** "the per-target speedup 1/(t·β) … achieved
  only when t < 1" — the correct condition is `t·β < 1`, i.e. `t < (m+1)/2` (the
  parenthetical "(i.e., T_desc(BKK) < sqrt(N))" itself implies this, and B.5's rescue
  regime claims exactly `t ∈ [1, (m+1)/2)`). "t < 1" contradicts the doc's own B.5.
- B.8's "T_desc(BKK) < sqrt(N)" is stated without the `t·β < 1` qualification (minor).

## Check 5 — Doubling formula and its claimed verification (closure doc A.1/A.2)

**VERDICT: REJECT**

- The doc's formula `f(x) = ((3x²+a)² − 8b·x)/(4(x³+ax+b))` is **wrong**. The correct
  duplication formula is `f(x) = (x⁴ − 2ax² + a² − 8bx)/(4(x³+ax+b))` (from
  `x(2P) = (3x²+a)²/(4y²) − 2x` with `y² = x³+ax+b`; the doc drops the `−8x⁴ − 8ax²`
  terms).
- Independent check on the test curve: the doc's formula matches the true `x([2]P)`
  (computed via `λ = (3x²+a)/(2y)`, `x(2P) = λ² − 2x`) at only **3 of 475** affine
  points (x = 0 and two others where the missing terms vanish mod 1009); the correct
  formula matches **all 475**. The doc's claim that the formula "was evaluated at all
  affine points … and confirmed to match x([2]P) … for every non-2-torsion point
  checked" is **false as stated**.
- The y-sign-cancellation conclusion (O_D is a rational function of x(P) alone) is
  nevertheless correct — the correct formula also contains no y. The error originates
  in IDEA-58b638's own text, which carries two wrong formulas (the "corrected" one
  matches the closure doc's wrong one).
- The "5 curves at p=1009 (seed 42)" provenance is unverifiable (no RNG/generation
  procedure stated), though all stated values are arithmetically correct.

## Check 6 — Doubling-oracle closure argument (IDEA-58b638) and its disposition

**VERDICT: REJECT — the closure argument is invalid and the conclusion contradicts the companion document**

- The closure's central claim (B): "The only non-trivial strategy for extracting x(Q)
  from O_D queries … is the doubling chain", requiring `ord_q(2)` queries. This is
  **false**: the adversary can query the oracle at the halved point —
  `O_D([2^{-1}]Q) = x([2]·[2^{-1}]Q) = x(Q)` — **one query**, since `[2^{-1}]Q` is a
  group-law scalar multiple available in the GGM. The doubling chain never needs to
  wrap; `ord_q(2)` is irrelevant to the oracle's power.
- Consequently `O_D` is **equivalent** to the x-coordinate (encoding) oracle, not weaker:
  `O_D(P) = f(x(P))` (x-oracle ⊇ O_D) and `x(Q) = O_D([2^{-1}]Q)` (O_D ⊇ x-oracle).
- The companion document (TASK-20260805-004, Q1/Q3) itself classifies the encoding
  oracle (P → x(P)) as NON-SIMULABLE (BATCH-060 control), classifies C_t as Tier 3,
  and states Semaev IC is **sub-rho unconditionally** (`L[1/2, sqrt(2)] ≈ 2^61.7 <<
  2^128`) with exactly this oracle. Therefore `O_D` enables sub-rho IC — the closure's
  conclusion "O_D gives no sub-rho ECDLP attack" and the DEC's "No sub-rho path"
  **contradict the companion document's own Q1**.
- The two committed documents are internally inconsistent on this point, and the
  closure's "no advantage beyond standard GGM" is false: O_D is non-simulable in the
  GGM (it leaks x-coordinates), exactly like the encoding oracle.
- The DEC's disposition "IDEA-58b638 CLOSED as rejected (barrier confirmed)" is
  **not supported** by the validated artifacts. The correct statement is that O_D is
  equivalent to the encoding oracle — the same oracle the program's own sub-rho IC
  track is built on. (Whether the *idea* "doubling oracle" is novel is a separate
  question; the closure as argued is invalid.)

## Check 7 — H-PSEUDO orientation correction (oracle doc Q4, DEC)

**VERDICT: PASS (with two ledger gaps)**

- Verified against the hypothesis text `H-PSEUDO-83817b`: the hypothesis bounds
  `max_k |hat{1_F}(k)| ≤ C·sqrt(B)`, i.e. bounded Fourier coefficients = pseudorandom
  DLs = yield **at** the heuristic level; above-heuristic yield for aligned targets
  requires a large coefficient, i.e. H-PSEUDO **failing**. The oracle doc's "Defect 1"
  (the IDEA's Direction A was inverted) is consistent with the hypothesis text, and the
  corrected biconditional (chain-complex sub-rho ↔ H-PSEUDO fails) is coherent.
- **Gap 1:** `KN-FIND-9d2f56.md` still contains the old wording ("This is exactly
  H-PSEUDO (yield above heuristic = structured additive density of S)") — the DEC's
  claim "KN-FIND-9d2f56 Corollary restated accordingly" is not reflected in the
  knowledge record (the file was not updated). The corpus retains an unresolved
  usage conflict between the hypothesis text and the finding.
- **Gap 2:** the DEC references `DEC-20260804-384a4a` ("only the interpretation
  direction used in DEC-20260804-384a4a") — **no such record exists** in the ledger
  (dangling reference; KN-FIND-9d2f56's actual source decision is
  `DEC-20260804-425827`).
- The "sub-rho" conflation (Defect 2) is coherent and internally consistent.

## Check 8 — DEC-20260805-364e9e dispositions

- **IDEA-58b638 rejected: NOT SUPPORTED** (Check 6). The disposition rests on an
  invalid argument and contradicts the companion document.
- **IDEA-62ef74 dispatched: SUPPORTED in substance** — the two defects are real and
  the corrected biconditional is coherent; the C_t non-simulability witness and the
  O(1) membership claim are consistent with BATCH-060's taxonomy (Tier 3) and the
  hypothesis text. Caveats: the KN-FIND-9d2f56 wording was not updated and the DEC's
  `DEC-20260804-384a4a` reference is dangling (Check 7).
- **IDEA-0cd03f approved for experiment design: SUPPORTED** — the K* formula is
  correct, the rescue regime is correctly derived, and `EV-SEMAEV-7f7d22` is reserved
  and bound by the BATCH-122 experiment contract (TASK-20260805-007) using the same
  formulas. The two FP table artifacts and the B.6 wording do not change the
  disposition.
- The DEC's "K* drops 2001 → 96" inherits the 2001 FP artifact (correct: 2000 → 96).
- The DEC's `ord_N(2)` vs the closure doc's `ord_q(2)` is a notation difference only.
- The IDEA-58b638 record in `new_ideas_batch120.yaml` still carries `status: proposed`;
  the "CLOSED as rejected" disposition exists only in the DEC (the DEC's
  decision_scope says the closure is idea-level, but the idea record itself was not
  updated). Minor ledger-consistency gap.

## Other notes

- The oracle doc's header source list ("BATCH-060/TASK-20260804-051") and footer
  ("BATCH-060/ggm_analysis.md") name the same file; cosmetic inconsistency only.
- The closure doc's Q2 arithmetic (`S_m = B^3/N = sqrt(N)`, `B/S_m = 1`,
  `B^ω ≥ N`, `(log N)^{3m}/N`) is correct under the reading "B/S_m = targets needed to
  collect B relations".
- The oracle doc's Q2 "maximal failure → factor base generates the index-k* subgroup,
  fraction 1/k* of targets" is a consistent heuristic (a maximal Fourier coefficient
  forces F's DLs onto a coset of the k*-kernel).
- No fabricated runs, timings, or statistics were found in the reviewed documents
  beyond the false formula-verification claim in Check 5 (which is a mathematical
  error in the stated verification, not a fabricated run record).

## Overall verdict

**VERDICT: revise**

The snapshot content is genuinely committed and byte-identical on disk; the L[1/2]
arithmetic, the toy-curve arithmetic, the H-PSEUDO orientation correction, and the
K*(BKK) formula are all sound. But the batch's headline closure — IDEA-58b638
"rejected, no sub-rho path" — is invalid: the halving query `O_D([2^{-1}]Q) = x(Q)`
makes O_D equivalent to the x-coordinate oracle, which the companion document itself
classifies as non-simulable and sub-rho-enabling. The doubling formula is wrong and
its claimed verification is false; the snapshot receipt names a non-existent parent
commit; two K* cells carry floating-point artifacts; and the DEC carries a dangling
record reference. The DEC's dispositions for IDEA-62ef74 and IDEA-0cd03f survive
scrutiny; the IDEA-58b638 rejection does not.