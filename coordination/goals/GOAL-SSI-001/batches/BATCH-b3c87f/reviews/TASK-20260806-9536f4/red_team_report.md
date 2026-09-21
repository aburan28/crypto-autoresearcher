# Red-team report — TASK-20260806-9536f4 (BATCH-b3c87f, GOAL-SSI-001)

Independent session. I did not produce any artifact under review and I repair none.
I change no status, edit no raw artifact, and commit nothing.

## 0. Snapshot binding, independently verified

Receipt: `coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/archives/TASK-20260806-274d8a/snapshot-receipt.json`.
It carries `commit_sha: null`, `parent_sha: null`, `verification.status: pending_post_commit`.
I recomputed five of the eleven declared hashes against the tree at `69441f1a`
(`git show 69441f1a:<path> | sha256sum`):

| path | recomputed sha256 | matches receipt |
|---|---|---|
| `ledger/proposals/IDEA-20260806-62ba9d.yaml` | `f813b21f…0204b34` | yes |
| `experiments/EXP-SSI-697354/specification.yaml` | `957192f2…da2da4fdc` | yes |
| `ledger/hypotheses/H-SSI-7fe2bf.yaml` | `46b76b1d…1f601c95` | yes |
| `…/TASK-20260806-fd3518/duplication_audit.md` | `17abcd7f…22044ca7` | yes |
| `ledger/proposals/IDEA-20260806-b60c35.yaml` | `b08894b5…89a200c0` | yes |

**Content-verified.** One process observation, recorded not acted on: commit `69441f1a`
changes exactly one file (the receipt itself). The eleven declared artifacts entered the
tree in `6ccaa446` and `c546a0bc`. Under AGENTS.md "Durable research commits" the verifier
expects the snapshot commit to *change exactly the declared artifacts*; here it changes
none of them. Per CLAUDE.md the archive binds to content first, and the content binds, so
this is not an evidence-integrity failure — but the receipt's `commit_sha: null` should be
filled by the Coordinator's post-commit verifier before any ledger transition cites it.

---

## 1. THE HEADLINE ADJUDICATION — `IDEA-20260806-62ba9d` against the primary source

The proposal makes three separable claims. **One is right, one is wrong, and one is
already-committed prior art the proposal's own novelty screen missed.** The net effect is
that `EV-SSI-59f7a2` *does* need a superseding correction, but not the one 62ba9d asks for
and not for the reason it gives, and the "32–43 % of the committed gap" figure must not be
carried anywhere.

### 1a. "§4.1 prices OneEnd, not Isogeny" — **UPHELD** at source

`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 226 opens §4.1 with *"Let us estimate
a lower bound on the concrete cost of the algorithm"* — singular, and the algorithm in
scope is Algorithm 3 (Theorem 1.1, OneEnd: *"finds a non-scalar endomorphism
α ∈ End(E) \ Z"*, line 19). Every quantity in the derivation is Algorithm 2's table
`M = Ψ(X,B)·X` and Algorithm 3's `P0`. **No step of §4.1 crosses Corollary 1.2.** The row
labels "SQIsign NIST-I/III/V" are parameter-set labels for `log2 p`, not a claim that the
figure is a SQIsign key-recovery cost, and the paper never asserts otherwise.

`EV-SSI-59f7a2.inference` nevertheless says the finding *"tightens the security estimate …
at SQIsign NIST-I"*, and `DEC-20260805-596d71.decision_scope` states *"The theoretical
security of SQIsign NIST-I under Wesolowski's algorithm is 2^{120-123} AES-equivalent"*.
Both are class-(c) sentences resting on a class-(a) computation, exactly as 62ba9d
describes. **The scope elision is real and it is committed.**

Two further defects in the same direction, which 62ba9d does not name:

- The paper's own comparison column, `previous methods ≈ 2^{P/2}`, is a **memoryless
  Isogeny/EndRing figure** (Delfs–Galbraith), set against a **OneEnd** figure. The
  campaign's `T_B = P/2` baseline in `EXP-SSI-697354` inherits that asymmetry unchanged.
- `EXP-SSI-697354` line 792 scopes its affected set as *"Constructions resting on the
  supersingular Isogeny / EndRing / OneEnd problem"* — all three, undifferentiated. `GRH`
  appears **zero times** in `EXP-SSI-697354/specification.yaml`, `H-SSI-7fe2bf.yaml` and
  `EV-SSI-59f7a2.yaml` (grep counts: 1 hit total across all three files, and it is line
  792's problem list, not a conditionality statement).

### 1b. "The bridge is uncharged anywhere in the corpus" — **REFUTED**

62ba9d's novelty screen reports *"A grep of ledger/ for `Corollary 1.2|OneEnd.*EndRing.*
reduction|reduction.*cost.*OneEnd` returned 15 files; none charges the reduction."* The
discriminating string is `Proposition 8.5`, and it was not searched. It returns committed
records that charge and condition the bridge already:

| record | what it already records |
|---|---|
| `ledger/goals/GOAL-SSIQ-001/goal.yaml` **GD-1** (l. 478-495) | verbatim 62ba9d's complaint — *"reachable only through the uninspected reductions [35, Theorem 1] and [35, Proposition 8.5] … No exponent is assigned to those reductions anywhere"* — raised 2026-08-05 by `TASK-20260805-fb72f1`, then **DISCHARGED** by BATCH-002 (`EV-SSIQ-29fcbb` O-9, O-10): *"The cascade was costed … both are `(log p)^{O(1)} = p^{o(1)}`, and NEITHER is `p^ε`"* |
| `ledger/goals/GOAL-SSIQ-001/checkpoints/BATCH-002.yaml` **SC-1** | *"GRH enters at the Isogeny arrow via [35, Proposition 8.5] … 'Conditional on Heuristic 1 alone' is now WRONG for the isogeny problem (right for OneEnd and EndRing)"* |
| same, **SC-2** | ***"Theorem 7.2 reduces EndRing to OneEnd_λ"*** — singular oracle call, with a `log deg α = (log p)^{O(1)}` rider |
| `ledger/goals/GOAL-SSIQ-001/goal.yaml` l. 115-125 | `heuristic_conditional_correction_20260805`: *"This campaign had been quoting it the wrong way throughout."* |
| `H-SSIQ-90e07b.yaml` l. 525-540 | `corollaries.reduction_ref` … **SC-3: "concrete cost NOT inheritable"** |
| `H-WESO-001.yaml` l. 80, `H-P13-001.yaml` l. 79 | *"Corollary 1.2 cites a nonexistent Proposition 8.5 of [35] and silently imports GRH for the isogeny direction"* |

So the bridge is charged **at the exponent level**, its GRH conditionality is recorded, and
its **concrete-cost non-inheritability is explicitly flagged (SC-3)**. What is genuinely
missing is not a charge but a **propagation**: none of SC-1, SC-2, SC-3 was carried across
from `GOAL-SSIQ-001` into `GOAL-SSI-001`'s `EV-SSI-59f7a2`, `DEC-20260805-596d71`,
`H-SSI-7fe2bf` or `EXP-SSI-697354`.

### 1c. The rank argument — **UNSOUND, and it falsifies the proposal by its own criterion**

62ba9d STEP 2 (R1): *"One OneEnd call yields one non-scalar α, so `Z[α]` has rank 2. Rank 4
therefore needs at least 2 further independent outputs, so `k ≥ 3` on pure rank grounds."*

This conflates the **Z-module span of the outputs** with the **order they generate**.
`End(E)` is a ring. Let `α ∈ End(E)\Z` and `β ∈ End(E)\Q(α)`. In `B_{p,∞}` every subfield
`L ⊇ Q` satisfies `[L:Q] | 2`, so a proper Q-subalgebra of a quaternion **division** algebra
is `Q` or a quadratic field, and dimension 3 is impossible. Hence the Q-algebra generated by
`α, β` is all of `B_{p,∞}`, and `Z⟨α,β⟩ = Z + Zα + Zβ + Zαβ` is a **rank-4 order**.

**The rank floor is `k ≥ 2`, not `k ≥ 3`.** `62ba9d.falsification_conditions[5]` reads:
*"The rank argument gives `k < 3`. The record's only unconditional derived number is wrong
and the premise fails."* **It is triggered.**

Worse for the proposal, `k = 2` is itself not the operative number. `[35]` is identified in
the frozen source's own bibliography at **line 328** of the file 62ba9d declares READ:
*Aurel Page and Benjamin Wesolowski, "The Supersingular Endomorphism Ring and **One
Endomorphism** Problems are Equivalent", EUROCRYPT 2024.* The title is singular; corpus
`SC-2` records `Theorem 7.2` as reducing EndRing to `OneEnd_λ`. Both point at `k = 1`.

**Consequences, arithmetic:**

| quantity | 62ba9d claims | correct black-box floor | with `k = 1` per [35]'s title / SC-2 |
|---|---|---|---|
| EndRing over OneEnd | `log2 3 = 1.585` bits | `log2 2 = 1` bit | 0 bits |
| Isogeny over OneEnd | `log2 6 = 2.585` bits | `log2 4 = 2` bits | `log2 2 = 1` bit |
| `gap_consumed_fraction` (of 6–8 bits) | **0.32–0.43** | 0.25–0.33 | 0.125–0.167 |

The proposal's `sota_delta` field asserts the 1.585/2.585/32–43 % numbers as *derived*.
**They are not derived; they are wrong, and `sota_delta` must not be quoted.** Note also
that R4's `2 × EndRing` doubling is a *call* doubling, so its contribution is `log2 2 = 1`
bit and not the `+1 bit on top of EndRing` compounding the record implies.

### 1d. Verdict on item 1

- `EV-SSI-59f7a2` and `DEC-20260805-596d71` **do need a superseding correction**, on the
  narrow and fully supported ground that a **OneEnd** concrete cost is stated as a
  **SQIsign (Isogeny)** security figure without carrying `SC-1` (GRH at the Isogeny arrow)
  or `SC-3` (concrete cost not inheritable across the reduction), both of which are
  committed elsewhere in the corpus.
- The correction is **qualitative (conditionality and problem label), not quantitative**.
  No bit count changes. The program has not been "overstating a number"; it has been
  **understating a conditionality and mislabelling a problem**.
- `IDEA-20260806-62ba9d` may not be dispatched in its present form. Its STEP 3 scope
  partition (classes (a)/(b)/(c)) is the surviving, useful half and is worth an hour. Its
  STEP 2 derived floors must be withdrawn by a superseding record before any of them
  reaches a checkpoint, a synthesis, or another proposal's `discriminated_from` block.

---

## 2. DUPLICATION — per-proposal verdict

I enumerated **267** files under `ledger/proposals/*.yaml` with `ls` (the producer's audit
saw 100 of 257; the count grew by the two 2026-08-06 batches). Full-corpus greps run over
`ledger/proposals/` **and** `ideas/`: `Corollary 1.2`, `Proposition 8.5`, `preprocessing|
non-uniform|advice`, `query model|query complexity|query lower bound|oracle model`. The
producer's disclosed recall limit (§5 of `duplication_audit.md`) is real and it **did cost
one finding**: the `Proposition 8.5` cluster in §1b above. That is the single duplication
miss in this batch and it is confined to `62ba9d`.

| proposal | named nearest | I also opened | verdict |
|---|---|---|---|
| `62ba9d` | `IDEA-20260805-d66193` | `IDEA-20260805-332316`, `IDEA-20260805-bc8246`, `IDEA-20260805-f9e801`, `GOAL-SSIQ-001/goal.yaml` GD-1, `BATCH-002.yaml` SC-1/2/3, `H-SSIQ-90e07b` | **PARTIAL DUPLICATE.** The discrimination against `d66193` and `332316` (quantifier prefix vs charged resources) holds. The discrimination against **GD-1 / SC-1 / SC-2 / SC-3** does not exist, because the record never found them. GD-1 states 62ba9d's premise verbatim and was discharged 2026-08-05. What survives as new is only the *concrete-bit* framing and the class-(a)/(b)/(c) partition. |
| `e4c719` | `IDEA-20260805-e7ee4a` | `IDEA-20260805-250e50`, `IDEA-20260805-062bee`, `IDEA-20260805-2d2c41` | **NOT A DUPLICATE.** `e7ee4a`'s criterion is literally `log_p(det)/rank`; adding the degree-count exponent `c` is a real third parameter, and `250e50`'s `E(θ,s,γ)` has no `(rank, det)` variable. One correction to the record's framing: `e7ee4a` **leaves the oriented cell OPEN** ("oriented curves … are exactly N5"), so `e4c719`'s title claim that `e7ee4a` "returns the wrong number" on a decided cell overstates — it returns the wrong number on a cell `e7ee4a` declined to decide. |
| `9c2f80` | `IDEA-20260805-250e50` | `IDEA-20260805-bc8246`, `IDEA-20260803-48e258`, `ideas/catalogue-20260805/B1-9` | **NOT A DUPLICATE** in this corpus. `250e50`'s `γ` is a per-query *time* exponent with no memory variable (its own record says so); `bc8246`'s `w` is per-execution working memory. The advice axis is genuinely unplotted here. |
| `d5a34e` | `IDEA-20260805-c60813` | `IDEA-20260805-250e50`, `IDEA-20260805-e7ee4a`, `IDEA-20260805-062bee` | **NOT A DUPLICATE.** `c60813` is a three-prong kill of one architecture; `d5a34e` quantifies over a model class and measures query count. Distinct observables. |
| `b60c35` | `IDEA-20260805-2d2c41` | `IDEA-20260805-062bee`, `IDEA-20260805-93ee20`, paper §4.2 (l. 246-256) | **NOT A DUPLICATE.** `2d2c41` varies conditioning on `E` at one `p`; `062bee` fits `γ` across four *toy* primes; `b60c35` varies `p` at fixed cryptographic size. Orthogonal. I independently verified every quotation: 100,000 samples at `5·2^248−1`, 10,000 at `27·2^500−1`, `ρ ≈ 1/69232` and `1/3312`, no control prime — all correct at source. I also re-derived its congruence arithmetic: `5·2^248−1 ≡ 1 (mod 3)`, `27·2^500−1 ≡ 2 (mod 3)`, both `≡ 3 (mod 4)`. Correct. |

**On the producer's audit itself:** it disclosed its own recall limit in §5 and named the
red team as the party who should attack it. That disclosure is worth crediting and it is
*not* a substitute for coverage — the sibling task reached 262/262 with `Grep`
`head_limit: 0`, and one real collision (§1b) lived in exactly the unread region.

---

## 3. CONTROL-CANNOT-FAIL (`KN-TECH-1a5b7e`) — explicit verdicts

### 3a. `EXP-SSI-697354`

I evaluated every assertion numerically from the committed inputs before writing this
section. Reproduction script inputs: `…/BATCH-046/tasks/TASK-20260804-55952a/implementation/
cost_measurements.json` `$.scaling_summary` (8 rows, verified present and matching the
frozen literals) and the T2 literals in the contract.

Fits I recomputed independently: `a1 = 15.576908`, `a3 = 16.925485`, `b3 = −36.279644`
(contract says `−36.279641`; 3e-6 drift, harmless), `a4 = 16.27692061`.
`T_A(256, S=0, A=0)` = `118.4613 / 118.5179 / 118.5690 / 118.5248` for L1–L4.

| control | capable of returning a negative? | evidence |
|---|---|---|
| **RG-1** | **YES on the Executor's code — but as literally specified it FAILS.** The gate's declared configuration is *"unbounded memory, memoryless baseline"*, which is `MC_P13`. Under `MC_P13` the formula subtracts `0.5·min(log2 w, L_mem)`, so at unbounded memory `T_A(256) = 118.4613 − 46.25 = ` **`72.2113`**, against an assertion window `[118.25, 118.75]`. The frozen reference block (`T_A_256_S0_A0`) and `preregistered_prediction.Q1` both omit the memory term entirely. **The contract contradicts itself on its own blocking gate.** | see §4 |
| **RG-2** | **NO.** `S_struct = 3.0` is a *declared input* (the contract's own `honesty_flag` says it is not re-derived). RG-2 = RG-1 + 3.0. It carries no information RG-1 does not. |
| **RG-3** | **Effectively NO.** RG-3 = RG-1 + 1.584963. RG-1's window maps to `[119.835, 120.335]`; RG-3 asserts `[119.9, 120.4]`. A 0.065-bit sliver of RG-1's window would fail RG-3 — no expected input lies there (design-time image `[120.046, 120.154]`). |
| **RG-4** | **NO, about the world.** The contract states it: *"Neither outcome fails the gate; failing to report which one holds DOES fail it."* This is a disclosure obligation formatted as a gate. |
| **RG-5** | **NO. Computed: min gap = 2.5241, max gap = 11.2756** over the declared `4 laws × 2 S × 4 A` grid at `P = 256, c = 0`. Requirement is `min ≤ 6.5` and `max ≥ 10.5`. Both clear by ~4 and ~0.8 bits, and both are forced by the *declared* extreme values of `S` (0/3) and `A` (−1.737/+3.907), fixed at freeze time. The gate cannot fail. Additionally the "coverage of `[6,11]`" is achieved by an ASIC corner (`S=3, A=3.907`) that `EV-SSI-59f7a2` never used, so it is a coincidence of the corner set, not a reproduction. |
| **NULL-OBJECT arm N0** | **NO.** `D_null0(P) ≡ E(P)` identically, because `N0` sets `E ≡ 0`. Computed range over `{L1..L4} × {256, 768}`: **`11.9613 … 13.6621`**, inside the pre-registered `[11.9, 14.2]`. Falsifier **F4** (`min D_null0 < 1.0`) requires `log2(a·256) < 1`, i.e. `a < 0.0039`. **Algebraically unreachable.** The "pre-registered prediction" is an identity of the contract's own formulas. |
| **NULL-OBJECT arm N1** | **NO.** `D_null1 = |E − 9.8|`; computed range `2.1613 … 3.8621`. Falsifier **F6** (`D_null1 ≥ D_null0`) requires `|E − 9.8| ≥ E`, i.e. `E ≤ 4.9`. I checked every integer `P ∈ [256, 768]` for all four laws: **never**. Unreachable. |
| **MONO-1** | **YES, on Executor wiring only.** It is the symbolic derivative of the contract's own formula. It cannot detect a level error (see §4). |
| **MONO-2** | **YES, on Executor wiring only** (a dropped `min()`), as the contract itself says. Same blindness to level. |
| **MONO-3** | **NO, except on a bug.** Under `MC_P13`, `dΔ/dlog2 w ≡ +0.5` below the kink, so a direction reversal is algebraically impossible. Its `NOT_EVALUABLE(n=…)` escape is correct practice and I credit it. |
| **MONO-4** | **NO. Computed:** the two conventions differ by `0.5·min(lw, L_mem) + 0.5·lw ≥ 10.0` bits at `lw = 10`, against a `≥ 0.5` bit bar. Forced. |
| **MONO-5** | **NO at run time.** It is a data check whose data is *transcribed into the contract*. I ran it: `L_paper` ↑, `L_mem` ↑, `L_paper − P/3 = [21.1667, 29.5, 33.5333, 38.9, 46.4]` strictly ↑ and inside `[21.0, 47.0]`, `L_mem − P/3 = [7.1667, 10.6, 10.6333, 14.0, 16.2]` non-decreasing. **All pass.** The contract froze both the assertion and the numbers it asserts about. |
| **FITTED-WINDOW-GUARD** | **YES, on Executor omission only.** A missing stamp or an empty `undefined_segments.json`. Process check, not a measurement. |
| **ADVERSARIAL-CORNER** | **Vacuous as written.** It withdraws "any pre-registered lower bound" that does not survive the corner; the contract pre-registers no such headline lower bound, so there is nothing for it to withdraw. |
| **SANITY-1** | **NO.** The sign of `dT_A/dlog2 w` is fixed by the committed formula at `−0.5` below the kink. The `MODEL_PATHOLOGY: memory_discount_direction` branch fires only if "cost falls as memory falls", which the formula makes algebraically impossible — as the control's own `preregistered_expectation` already spells out. It also audits the **wrong quantity**: the sign, not the anchor (§4). |
| **XCHK-1** | **YES, on an evaluator bug.** But it recomputes the *same expression*, so it cannot detect a wrong formula. |
| **XCHK-2** | **NO.** The tolerance is widened from the script's own `0.75` to the **3.51 bits previously observed as the discrepancy**. A check whose tolerance is set to the size of the deviation it once found cannot find that deviation again. |

**Summary: of fourteen assertions, exactly zero can return a negative about the
mathematical object.** Five (RG-1 under one reading, MONO-1, MONO-2, XCHK-1,
FITTED-WINDOW-GUARD) can return a negative about the Executor's code; the rest are
identities of the contract's own algebra or of numbers the contract itself froze. **I can
state in advance, without the run, that this contract will report a 100 % control pass**,
and I have computed every value above to show why. This is batch 34 of the pattern the
handoff named. The contract's control section is unusually well-*written* — each control
carries a `can_this_control_fail` block naming a concrete defect — but the named defects
are all implementation defects, and the object under study is arithmetic on frozen numbers,
so there is no object left for a control to be wrong about.

### 3b. Null objects in the five proposals

| proposal | null | capable of failing? |
|---|---|---|
| `62ba9d` | trivial-reduction null (`EndRing → OneEnd` must charge 0) | **NO in substance.** The record itself calls it *"free by inspection"* and assigns prior **0.97**. A null whose correct answer is written in the record and whose pass probability the record puts at 0.97 is a self-consistency check on the accountant, not a discriminator. |
| `62ba9d` | identity-reduction gate (`OneEnd → OneEnd` = 1 call, 1 table) | **NO.** Same structure. |
| `62ba9d` | can-the-ledger-say-superpolynomial | **YES.** The single genuinely discriminating control in the record, and the one worth keeping when the rest is withdrawn. |
| `62ba9d` | source-blocked-cell discipline (`≥ 1` blocked cell) | **YES, on process.** Note it is now partly moot: `SC-2` supplies the answer the record marked SOURCE-BLOCKED. |
| `62ba9d` | `k = 1` known-answer gate vs `EV-SSI-59f7a2` bracket | **YES, on arithmetic.** |
| `e4c719` | `c`-blind arm (hard-wire `c = 2`, require disagreement on the oriented cell) | **NO.** The disagreement is *defined* by the record (`c = 1` vs `c = 2` on that cell is asserted, not measured). Agreement is impossible by construction. |
| `e4c719` | forced-value gate `c_measured = 2.00` at toy scale | **YES.** A real enumeration against a counting theorem. Keep it; it is the record's only genuine measurement. |
| `e4c719` | NOT-APPLICABLE control on prime-field ECDLP | **Weak.** Depends on the analyst declining to apply a formula, not on data. |
| `9c2f80` | random-advice null (must return `p^{1/3}`) | **NO as scheduled.** Stage 0 evaluates it *symbolically*, by the same analyst who wrote the four constructions. It cannot fail until an implementation exists that could charge set membership. |
| `9c2f80` | shuffled-fiber control | **YES in principle**, same blocker: no implementation at Stage 0. |
| `9c2f80` | `S = 0` and `S = p` known-answer gates | **NO.** Symbolic, forced by the definitions. |
| `d5a34e` | δ-oracle null (adding `Q4` must drop the bound to `≤ 1/5`) | **YES — the strongest null in the batch**, because `1/5` comes from `250e50`'s independently derived identity, not from `d5a34e`. |
| `d5a34e` | Frobenius-free and no-planted-path nulls (must return `1/2`) | **YES.** Both are genuine. |
| `d5a34e` | graded control at `θ ∈ {1/6, 1/4, 1/3, 1/2}` | **YES** — and this is the "what should the quantity have done" control the inventor protocol §3 asks for: the bound must *track* the planted degree. Good. |
| `b60c35` | ARM M (size- and class-matched random primes) | **YES — the only control in this batch capable of returning a negative about the mathematical object.** Pre-committed statistic, hash-committed before ARM T is read, within-arm spread across three primes, and a declared underpowered branch. It is also the only one that is *blocked on a sampler that does not exist* (`compute_budget_note` says so plainly). |
| `b60c35` | ARM C (cross-class null) | **NO, quantitatively.** See objection OBJ-8 below. |
| `b60c35` | ρ known-answer gate at the two published `(p, B)` pairs | **YES, and it is runnable today.** I verified both target values at source (paper l. 250, 252: `1/69232`, `1/3312`). |

---

## 4. THE vOW CONVENTION CONFLICT — the corpus **can** decide it, and **neither committed convention is right**

The designer reports two committed, incompatible chargings. I checked both at source. The
correct answer is that they are two halves of **one** law, and each committed artifact
mangles it in a different way.

**The law (paper §1.1, l. 39, verbatim):** *"The time-memory tradeoff of van
Oorschot–Wiener [43] solves a claw-finding problem of this size in time essentially
`√(N³/w) = p^{1/2+o(1)}/w^{1/2}` with memory `w`. This allows one to interpolate between
the `p^{1/3+o(1)}` high-memory algorithm presented here and the classic `p^{1/2+o(1)}`
algorithms with polynomial memory like [21]."*

The law is a **single curve for the assessed method**, ranging from `p^{1/3}` at
`w = N` down to `p^{1/2}` at polynomial `w`. Instantiating at NIST-I with `N = M = 2^{92.5}`
and `1/P0 = 2^{14}`:

```
T(w) = (1/P0) · sqrt(M^3 / w)          log2 T(w) = log2 T_full + 0.5·(L_mem − log2 w),  w ≤ M
                                       log2 T(M) = 106.5   ✓ recovers the paper's own row
                                       log2 T(poly) = 152.75
```

Now the two committed chargings:

**`MC_P13` / `EXP-P13VOW-001`** — `cost_model.py` l. 236: `"T_w_vOW = T_full / sqrt(min(w, M))"`,
and `EXP-SSI-697354` inherits it as `− 0.5·min(log2 w, L_mem)`.
The `sqrt` argument is a **memory count, not a ratio** — the expression is dimensionally
inconsistent, which is the cheapest tell. Numerically it equals the correct law **minus
`0.5·L_mem` uniformly**:

| P | correct `log2 T` at `w = M` | `MC_P13` at `w = M` | error, attacker-favourable |
|---|---|---|---|
| 256 | 118.4613 | **72.2113** | **46.25 bits** |
| 384 | 170.0463 | 100.7463 | 69.30 bits |
| 512 | 217.1613 | 126.5113 | 90.65 bits |

The *shape* is right (monotone decreasing in `w`, kink at `L_mem`); the *anchor* is wrong.
`MC_P13` **is not a convention. It is an arithmetic error.**

Its committed consequence in `EV-WESO-001` — *"with zero hidden overhead the vOW middle
regime beats Delfs-Galbraith at every tested budget `w = 2^30..2^80` for all five sizes"* —
is a direct product of that error. Under the correct law at NIST-I, `w = 2^30` gives
`106.5 + 0.5(92.5 − 30) = 137.75 > 128`: the method **loses** to Delfs–Galbraith there. The
correct crossover is at `log2 w ≈ 49.5` entries, not at every tested budget.

**`MC_VOW`** — the paper's law attached to the **baseline**: `T_B = P/2 + log2 k_DG + A −
0.5·log2 w`. This misattributes the law. `p^{1/2+o(1)}/w^{1/2}` **is** the memory-reduced
form of the assessed method; the previous-methods column is stated by the paper itself as
*"≈ 2^128 F_{p^2}-operations and **negligible memory**"* (l. 234). Giving Delfs–Galbraith a
`w^{-1/2}` speedup both misassigns the curve and double-counts it. At `w = 2^{92.5}` it
would make the baseline `2^{81.75}` — faster than `p^{1/3}` — which is the sign flip the
designer observed. That flip is an **artifact of misattribution, not a genuine convention
ambiguity.**

**Verdict on item 4.** The corpus decides it, from two sentences of the frozen source. The
correct charging is:

```
T_A(P, w) = L_paper(P) + E(P) + S + c·√P + A + 0.5·max(0, L_mem(P) − log2 w)
T_B(P, w) = P/2 + log2 k_DG + A            (memoryless; the paper's own column)
```

Consequently:

- `H-SSI-7fe2bf` **HEUR-XO-3** ("exactly one of the two committed conventions describes the
  physically correct comparison") is a **false dichotomy**: neither does.
- `H-SSI-7fe2bf` l. 327-330 states the alleged `MC_P13` pathology as *"it makes the assessed
  method CHEAPER as memory shrinks"*. The specification's own `SANITY-1` says the opposite
  and is right (*"smaller w gives a smaller subtraction and a LARGER cost"*). **The frozen
  hypothesis and the frozen specification contradict each other on the sign**, and both are
  in the same snapshot.
- **`SANITY-1` audits the sign and cannot see the anchor.** `MONO-1`–`MONO-4` are all
  differential (slope, kink, ordering) and are **invariant under a constant offset**, so
  none of them can see a 46/69/91-bit level error either. `RG-1`–`RG-5` are evaluated with
  the memory term absent. `XCHK-1` recomputes the same expression. **The contract has no
  control that can detect its single largest defect.**
- The contract's stated *"secondary and equally binding"* objective — *"determine whether
  the sign of the comparison is controlled by the corrected estimator or by an unstated
  memory-charging convention"* — is built on that false dichotomy, and `H-SSI-7fe2bf` H2 /
  falsifier `F5` inherit it.

---

## 5. THE SYNTHESIS SENTENCE — the designer is right, and the defect is one level upstream

`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` l. 171: *"NIST-III/V retain comfortable margins
under every tested overhead scenario."* I recomputed the committed table from `T1` + `T2`
under `L1`, `S = A = c = 0`:

| level | `T_A` | gap below the level's own target (`2^128/2^192/2^256`) | advantage over the matched baseline (`P/2`) | table bytes @ 64 B/entry |
|---|---|---|---|---|
| NIST-I  | 118.4613 | **9.5387** | **9.5387** | `2^{98.5}` |
| NIST-III | 170.0463 | **21.9537** | **21.9537** | `2^{144.6}` |
| NIST-V  | 217.1613 | **38.8387** | **38.8387** | `2^{187.3}` |

**The designer's `≈ 9.5 / 22 / 39` is correct.** Both gaps **grow** with level: at NIST-III
and NIST-V the assessed method sits *further* below the level's own target and gains *more*
over the matched baseline than at NIST-I. The sentence is false on both those axes and true
only on memory feasibility, where the excess over `2^{73.08}` bytes is `25.4 / 71.5 / 114.2`
bits and does widen with level.

**Two corrections to the designer's own account, both in the direction of a larger problem:**

1. **The defect originates in `EV-WESO-001`, not in the synthesis.** That record's
   `observations` block carries the red team's actual wording: *"a defensible calibration
   `c ~ 1.8` shrinks the NIST-I **margin** to ~2.3 bits …; NIST-III/V **margins survive**
   all tested scenarios."* There "margin" is the **attack's advantage** — the same record
   says the method *"beats Delfs-Galbraith at every tested budget"*. `EV-WESO-001`'s own
   `inference` field then rewrites it as *"NIST-III/V **retain comfortable margins** under
   every tested overhead scenario"*, which in a security document reads as scheme safety.
   **The subject is inverted between the `observations` and `inference` blocks of a single
   committed evidence record**, and the synthesis copies the `inference` wording verbatim.
   A superseding correction must therefore supersede `EV-WESO-001`'s inference sentence,
   not only the synthesis line.
2. **`SCOPE-A` and `SCOPE-B` are the same number.** Because `L_prev = P/2` and each NIST
   level's target is also `2^{P/2}`, the advantage-over-baseline and gap-below-target
   columns coincide identically at `log2 k_DG = 0` under the memoryless baseline (see table:
   9.5387 / 21.9537 / 38.8387 in both). `EXP-SSI-697354` presents them as two independent
   pre-registered orderings (`Q5`) and requires them *"reported separately with the axis
   named"*. **They are one observation counted twice.** The contract should disclose the
   degeneracy and state that `SCOPE-A` and `SCOPE-B` separate only when `log2 k_DG ≠ 0` or
   under `MC_VOW`.

Credit where due: the contract's `claim_ceiling.forbidden_sentences` already forbids *"the
unqualified sentence 'NIST-III/V retain margin'"* and requires the axis be named. That is
exactly right, and it is the batch's best single piece of work.

---

## 6. RUNNABILITY ON THE DECLARED STDLIB-ONLY PATH — **QUALIFIED YES, with two gaps**

- Interpreter and inputs: `T1` exists at the declared path, `$.scaling_summary` is a list of
  8 rows, and `log2_p` / `avg_mults_per_entry` match `frozen_values_x` / `frozen_values_y`
  exactly. Every computation the contract requires (OLS, proportional fit, `log2`, a
  513-point scan, bisection, SHA-256, JSON I/O, `importlib.util.find_spec`) is stdlib.
  I reproduced all five frozen fit constants and all four `T_A(256)` values in pure stdlib
  `math` in under a second. **The primary path does not need numpy.**
- **Gap 1 — `stdlib_modules_permitted` is a closed list that omits `re` and `ast`.** Two
  mandatory steps need one of them in practice: parsing the five bullets at
  `paper_fulltext.md` lines 234-238, and extracting `PAPER_PAIRS` from lines 60-66 of a
  `.py` source file. Both are achievable with `str.split`, but an Executor reaching for `re`
  is technically outside the frozen dependency contract while `invalidation_rules` only
  invalidates on the *forbidden* list. Ambiguous, not fatal — but it is a design-time defect
  and it should be closed by amendment rather than by Executor discretion.
- **Gap 2 — the contract is not self-contained.** `independent_variables` names *"log2 w
  (the deliverable's free axis, 14 declared values)"* and `invalidation_rules` forbids *"any
  post-hoc change to … the w grid"*, but the grid appears nowhere in
  `specification.yaml`. It is at `H-SSI-7fe2bf.yaml` l. 500
  (`[20, 25, 30, 35, 40, 50, 60, 70, 80, 92.5, 138.6, 181.3, 206.0, 272.2]`). The freeze
  should name that field path explicitly.
- Consequence of that grid worth flagging: under `MC_VOW`, `9` of the `14` `w` values
  (`20 … 80`) make the feasible `P` set **empty at every `P`**, so those cells all emit
  `INFEASIBLE_AT_MEMORY`; at `log2 w = 92.5` the feasible set is the **single point**
  `P = 256`, so step 4's *"value of `g` at BOTH feasible endpoints"* is degenerate. The
  `p_star_band` and falsifier `F2` will therefore be computed over a small and unstated
  `n_numeric`. The contract's requirement to report the categorical counts alongside the
  band is what saves this from being unreadable, and it should be enforced at review.

**"Vacuously satisfied" wording — PRESENT, mechanism convention-specific.**
`escalation_rules` states: *"A pre-registered bound satisfied only because the assessed
method is memory-infeasible at that `w` is reported with the words VACUOUSLY SATISFIED …
IDEA-20260803-48e258's F3 is expected to be satisfied vacuously across its entire `w` range
for exactly this reason, and saying so is the point."* The required words are used and the
prediction is stated in them. **But the stated reason holds only under `MC_VOW`**: under
`MC_P13` the contract explicitly masks nothing (*"Under MC_P13 no P is masked"*), so no cell
is ever memory-infeasible and the label is undefined on half the grid. There, `F3`
non-triggering has a different cause (`L_mem(256) = 92.5 > 40`, so no `log2 w ≤ 40` cell can
be feasible at all). The contract should say *which convention* the vacuity applies to.

---

## 7. Objections, consolidated by severity

**BLOCKING (must be resolved before dispatch or before any ledger transition)**

- **OBJ-1.** `EXP-SSI-697354` `RG-1` is self-contradictory. Under the gate's own declared
  configuration (`MC_P13`, unbounded memory) `T_A(256) = 72.2113`, outside the asserted
  `[118.25, 118.75]`. The contract's own `invalidation_rules` then void the run. An Executor
  who instead silently drops the memory term is making an undeclared protocol choice, which
  `invalidation_rules` also forbids. **The contract cannot be run as frozen without one or
  the other violation.** Requires a versioned `protocol_amendment` and a new experiment
  version, not an Executor decision.
- **OBJ-2.** `MC_P13` is off by `0.5·L_mem` — **46.25 / 69.30 / 90.65 bits at NIST-I/III/V,
  all attacker-favourable** — because `T_full / sqrt(min(w, M))` takes the square root of a
  memory count rather than a ratio and does not reduce to the paper's own `2^{106.5}` at
  `w = M`. The defect is inherited from `EXP-P13VOW-001` `cost_model.py` l. 236 and is the
  source of `EV-WESO-001`'s committed *"beats Delfs-Galbraith at every tested budget"*. No
  control in `EXP-SSI-697354` can detect it (§4).
- **OBJ-3.** `IDEA-20260806-62ba9d`'s `k ≥ 3` rank floor is unsound, triggering the record's
  own falsification condition 5; the derived `1.585 / 2.585` bits and the
  `32–43 %` `gap_consumed_fraction` in `sota_delta` must be withdrawn and must not be
  carried into any checkpoint, synthesis, or downstream `discriminated_from` block (§1c).

**HIGH**

- **OBJ-4.** `EV-SSI-59f7a2` and `DEC-20260805-596d71` state a **OneEnd** concrete cost as a
  **SQIsign (Isogeny)** security figure without `SC-1` (GRH at the Isogeny arrow) or `SC-3`
  (concrete cost not inheritable). `GRH` appears zero times in `EV-SSI-59f7a2`,
  `H-SSI-7fe2bf` and `EXP-SSI-697354`. A superseding correction is warranted — qualitative,
  not numeric (§1d).
- **OBJ-5.** `EV-WESO-001` inverts the subject of "margin" between its `observations` and
  `inference` blocks; `analysis/SSI-ECDLP-SYNTHESIS-20260803.md` l. 171 propagates the
  inverted form. Correction should supersede both (§5).
- **OBJ-6.** Every substantive control in `EXP-SSI-697354` — `RG-2`, `RG-3`, `RG-4`, `RG-5`,
  both `NULL-OBJECT` arms, `MONO-3`, `MONO-4`, `MONO-5`, `SANITY-1`, `XCHK-2` — is
  algebraically or arithmetically forced by numbers already inside the contract. I computed
  all of them and they all pass (§3a). The run will report a 100 % control pass and that
  result will carry no information.
- **OBJ-7.** `H-SSI-7fe2bf` l. 327-330 and `EXP-SSI-697354` `SANITY-1` **contradict each
  other on the sign** of the alleged `MC_P13` pathology, inside one frozen snapshot.

**MEDIUM**

- **OBJ-8.** `b60c35`'s ARM C is quantitatively void as motivated. Its stated
  congruence-class mechanism (supersingularity of `j = 0` and `j = 1728`) touches `O(1)`
  curves out of `≈ p/12 ≈ 2^{244}` classes, and the Eichler mass-formula corrections for
  `p mod 12` are `O(1)` against a mass of `(p−1)/24`. **The effect ARM C is designed to
  detect has weight `O(1/p)` and cannot register at 100,000 samples.** Either name a
  different channel by which `p mod 12` reaches the minima of the trace-zero ternary form,
  or drop ARM C and spend the samples on ARM M's within-arm spread.
- **OBJ-9.** `b60c35` names no mechanism by which the *additive* shape `c·2^k − 1` (as
  distinct from the congruence class) could bias the minima of the ternary form, and
  pre-registers no power calculation. Without both, `ARM T ≠ ARM M` is unfalsifiable in
  practice: any observed difference is as likely a sampler artifact. Require a stated
  minimum detectable effect and the `n` that reaches it, before Stage 2.
- **OBJ-10.** `9c2f80`'s null and its prediction are the same object. It predicts a flat
  frontier `T(S) = min(p^{1/3}, p/S)`, and the way that prediction "fails" is that someone
  invents a better advice construction. **A null result confirms the hypothesis** — the
  `KN-TECH-1a5b7e` structure at proposal level. It also never compares against the DLP-with-
  preprocessing literature, where `ST² = Õ(N)` frontiers and generic-group lower bounds are
  the specialized baseline; `dominated_by` lists five isogeny rows and no preprocessing row,
  so the `advice` axis of that field is unchecked against the actual frontier for the axis
  it introduces. Under the inventor protocol §5 that is an unchecked entry, not a `null`.
- **OBJ-11.** `d5a34e` sequences its nulls before the object they control. Stages 1–2 run
  *"the identical lower-bound argument"* on null models; the argument is Stage 3's
  deliverable and does not exist. Either the nulls are run on a *sketch* — in which case
  they audit a sketch — or they cannot run first as specified.
- **OBJ-12.** `d5a34e`'s `sota_delta` says it *"replaces twelve separately-argued mechanism
  closures by ONE conditional statement"*. An IGQ query bound lower-bounds **time** only for
  algorithms whose sole primitive is neighbour expansion. The corpus's twelve closures
  include quaternion-side avenues (`c60813`'s relation collection lives there, and so does
  the paper's own §4.2). **One IGQ theorem does not replace twelve closures**; it replaces
  the subset that lives inside the model, and the record should count that subset explicitly
  rather than asserting the replacement. That is scope inflation in a closure claim, which
  the inventor protocol §4 treats as symmetric with overclaiming.
- **OBJ-13.** `e4c719` calls `E = c·log_p(D)/(2·rank)` an *identity* that *"returns 1/3, 1/2
  and 1/4 exactly"*. It rests on `m = Θ̃(D^{1/r})`, but **Hermite gives an upper bound**
  `m ≤ γ_r D^{1/r}`, not a two-sided estimate. `E` is therefore an *upper bound on the
  exponent under a genericity assumption*, not an identity. As an admissibility screen it
  errs safely, so the criterion survives — but the word "identity" must go, and the
  genericity assumption must be numbered as a heuristic with a falsification condition.
- **OBJ-14.** `e4c719`'s title claims `e7ee4a` *"returns the wrong number"* on a cell.
  `e7ee4a` explicitly leaves the oriented cell **open** (*"oriented curves … are exactly
  N5"*). The correct statement is that `e7ee4a`'s criterion, *if applied* to a cell it
  declined to decide, returns `1/2` where the class-group argument gives `1/4`. Overstated
  as written.

**LOW / process**

- **OBJ-15.** Snapshot receipt carries `commit_sha: null` and the snapshot commit changes
  none of the eleven declared artifacts (§0).
- **OBJ-16.** `stdlib_modules_permitted` omits `re` and `ast`, both of which two mandatory
  parsing steps naturally require (§6).
- **OBJ-17.** The `w` grid is invalidation-protected but lives outside the frozen
  specification (§6).
- **OBJ-18.** `SCOPE-A` and `SCOPE-B` are numerically identical under the committed inputs
  at `log2 k_DG = 0`; the contract presents them as two independent orderings (§5).
- **OBJ-19.** `global_storage_log2_bytes = 73.08` is a 2023 deployed-storage figure. Calling
  the resulting excess a "margin" imports an economic constant into a security statement;
  `EV-SSI-59f7a2`'s *"physically impossible"* and `DEC-20260805-596d71`'s repetition of it
  overstate. The supportable form is *"exceeds 2023 global deployed storage by `2^{25.4}`"*.
- **OBJ-20.** The producer's duplication audit enumerated 100 of 257 proposal files and
  head-read 12 of 19 targets. Its sibling task reached full coverage with `Grep`
  `head_limit: 0`. The disclosure is honest and it does not substitute for coverage: one
  real collision (§1b) lived in the unread region.

---

## 8. Baseline comparison

Nothing in this batch proposes an attack, so `sota_delta` is zero on every attack axis in
all five proposals — I checked each `dominated_by` block against the five-row frontier
(Wesolowski `p^{1/3+o(1)}` time and memory; Delfs–Galbraith `p^{1/2}(log p)^{O(1)}` at
polynomial memory; vOW `p^{1/2+o(1)}/w^{1/2}` at memory `w`; MITM `p^{1/2}` at `p^{1/2}`;
Kohel `p·(log p)^{O(1)}` at polynomial memory) and the rows are correctly stated in all
five. **One `dominated_by` is nevertheless unchecked on its own new axis:** `9c2f80`
introduces an advice axis and lists no preprocessing-literature row on it (OBJ-10).

The contract's baseline treatment carries a second, larger problem in the same place as
OBJ-2: with `MC_P13` corrected, the assessed method **loses** to Delfs–Galbraith at every
`w ≤ 2^{49.5}` entries at NIST-I, which reverses `EV-WESO-001`'s committed
*"beats Delfs-Galbraith at every tested budget `w = 2^{30}..2^{80}`"*. Any statement in this
goal that the assessed method dominates the matched baseline at a *feasible* memory budget
currently rests on the arithmetic error in OBJ-2.

---

## 9. The two cheapest observations requested

**Cheapest observation that falsifies the top-ranked new proposal (`IDEA-20260806-62ba9d`,
ranked first by `ideation_report.md` §2).**
Not the trivial-reduction null the producer names — the record itself calls that null *"free
by inspection"* and puts its pass probability at **0.97**, so it discriminates nothing.
Instead: **read line 328 of the file the record declares READ.** It is the bibliography
entry for `[35]`: *Page and Wesolowski, "The Supersingular Endomorphism Ring and **One
Endomorphism** Problems are Equivalent", EUROCRYPT 2024* — singular. Cross-check
`ledger/goals/GOAL-SSIQ-001/checkpoints/BATCH-002.yaml` **SC-2**: *"Theorem 7.2 reduces
EndRing to OneEnd_λ."* Both give `k = 1`. **Under two minutes, zero compute, no external
source, and it fires the record's own falsification condition 5.**

**Cheapest observation that invalidates the contract's output.**
**Evaluate `MC_P13` at `(P = 256, log2 w = L_mem(256) = 92.5)` and compare it to the
committed anchor `2^{118.5}`.** It returns **`118.4613 − 46.25 = 72.2113`**. One line of
arithmetic. It simultaneously (a) shows `MC_P13` does not reduce to the paper's own §4.1 row
at full memory, and (b) shows `RG-1`, evaluated in the configuration the gate itself
declares, fails by 46 bits.

---

## 10. Narrowest supported statement

> Under the snapshot at `69441f1a`: `EXP-SSI-697354` is a well-documented, honestly
> claim-ceilinged, stdlib-runnable arithmetic contract whose fourteen control assertions are
> all determined at freeze time by numbers the contract itself carries — I computed every
> one and every one passes — and whose two memory-charging conventions are, respectively, an
> arithmetic error of 46/69/91 bits in the attacker's favour and a misattribution of the
> paper's own interpolation law to the wrong side of the comparison. It should not be
> dispatched as frozen: its blocking gate `RG-1` fails under the configuration the gate
> declares.
>
> Of the five new proposals, four (`e4c719`, `9c2f80`, `d5a34e`, `b60c35`) are not
> duplicates of the corpus I checked and each carries at least one genuinely falsifiable
> control; `b60c35`'s ARM M is the only control in the entire batch capable of returning a
> negative about the mathematical object, and it is blocked on a sampler that does not
> exist. `62ba9d` is a partial duplicate of committed `GOAL-SSIQ-001` state (GD-1, SC-1,
> SC-2, SC-3), and its one unconditional derived number is wrong.
>
> `EV-SSI-59f7a2` requires a superseding correction, on the ground that it labels a OneEnd
> concrete cost as a SQIsign security figure without carrying SC-1 (GRH at the Isogeny
> arrow) or SC-3 (concrete cost not inheritable) — **not** on the ground that the reduction
> carries an uncharged 1.585–2.585 bits, which it does not.
> `EV-WESO-001`'s `inference` sentence and `analysis/SSI-ECDLP-SYNTHESIS-20260803.md` l. 171
> require a superseding correction: the gaps below target and the advantages over the
> matched baseline are `9.5387 / 21.9537 / 38.8387` bits at NIST-I/III/V and **grow** with
> level; "NIST-III/V retain comfortable margins" is true only on the memory-feasibility axis.
>
> No statement here closes any lane. Nothing here is a security claim about SQIsign in
> either direction, and nothing here bears on Heuristic 1, on Theorem 1.1, on Corollary 1.2,
> or on the correctness of `[35]`.

---

## 11. Machine-readable report

```yaml
red_team_report:
  id: RT-20260806-9536f4
  task_id: TASK-20260806-9536f4
  snapshot_commit: 69441f1a
  snapshot_verification: content_verified_5_of_11_paths_recomputed
  claim_under_review: >-
    (i) that the five BATCH-b3c87f proposals are new and falsifiable;
    (ii) that EXP-SSI-697354 can produce a result surviving its own controls;
    (iii) that IDEA-20260806-62ba9d's reduction charge consumes 32-43% of the
    committed 6-8 bit gap below 128 at SQIsign NIST-I.
  objections:
    - {id: OBJ-1,  severity: blocking, target: EXP-SSI-697354, summary: "RG-1 self-contradictory; under its own declared MC_P13/unbounded-memory configuration T_A(256)=72.2113, outside [118.25,118.75]"}
    - {id: OBJ-2,  severity: blocking, target: "EXP-SSI-697354 / EXP-P13VOW-001 / EV-WESO-001", summary: "MC_P13 = T_full/sqrt(min(w,M)) takes sqrt of a memory count not a ratio; off by 0.5*L_mem = 46.25/69.30/90.65 bits attacker-favourable; does not reduce to 2^106.5 at w=M"}
    - {id: OBJ-3,  severity: blocking, target: IDEA-20260806-62ba9d, summary: "k>=3 rank floor unsound (two non-commuting non-scalar endomorphisms generate a rank-4 order); floor is k>=2, and [35]'s title plus SC-2 give k=1; fires the record's own falsification condition 5"}
    - {id: OBJ-4,  severity: high, target: "EV-SSI-59f7a2 / DEC-20260805-596d71", summary: "OneEnd concrete cost stated as SQIsign/Isogeny security figure; SC-1 (GRH) and SC-3 (concrete cost not inheritable) never propagated; GRH appears 0 times in the SSI records"}
    - {id: OBJ-5,  severity: high, target: "EV-WESO-001 / analysis/SSI-ECDLP-SYNTHESIS-20260803.md:171", summary: "'margin' subject inverted between observations and inference blocks; gaps are 9.5387/21.9537/38.8387 and grow with level"}
    - {id: OBJ-6,  severity: high, target: EXP-SSI-697354, summary: "RG-2..RG-5, both null arms, MONO-3..MONO-5, SANITY-1, XCHK-2 are all forced at freeze time; all computed and all pass; run will report 100% control pass carrying no information"}
    - {id: OBJ-7,  severity: high, target: "H-SSI-7fe2bf:327-330 vs EXP-SSI-697354 SANITY-1", summary: "frozen hypothesis and frozen specification contradict each other on the sign of the alleged MC_P13 pathology"}
    - {id: OBJ-8,  severity: medium, target: IDEA-20260806-b60c35, summary: "ARM C's stated congruence mechanism (j=0/j=1728) has weight O(1/p) against ~2^244 classes and cannot register at 100k samples"}
    - {id: OBJ-9,  severity: medium, target: IDEA-20260806-b60c35, summary: "no mechanism named for the additive shape c*2^k-1 and no power calculation; ARM T vs ARM M unfalsifiable in practice as specified"}
    - {id: OBJ-10, severity: medium, target: IDEA-20260806-9c2f80, summary: "null and prediction coincide (flat frontier); dominated_by lists no preprocessing-literature row on the advice axis the record introduces"}
    - {id: OBJ-11, severity: medium, target: IDEA-20260806-d5a34e, summary: "nulls sequenced before the lower-bound argument they control, which is the Stage-3 deliverable"}
    - {id: OBJ-12, severity: medium, target: IDEA-20260806-d5a34e, summary: "an IGQ bound replaces only the subset of the twelve closures inside the model; quaternion-side closures are outside it; scope inflation in a closure claim"}
    - {id: OBJ-13, severity: medium, target: IDEA-20260806-e4c719, summary: "E = c*log_p(D)/(2r) is an upper bound under genericity, not an identity; Hermite is one-sided; the genericity assumption is unnumbered"}
    - {id: OBJ-14, severity: medium, target: IDEA-20260806-e4c719, summary: "e7ee4a leaves the oriented cell OPEN; 'returns the wrong number' on a decided cell is overstated"}
    - {id: OBJ-15, severity: low, target: snapshot-receipt.json, summary: "commit_sha null; 69441f1a changes none of the eleven declared artifacts"}
    - {id: OBJ-16, severity: low, target: EXP-SSI-697354, summary: "stdlib_modules_permitted omits re and ast, both needed by two mandatory parsing steps"}
    - {id: OBJ-17, severity: low, target: EXP-SSI-697354, summary: "the invalidation-protected w grid lives in H-SSI-7fe2bf:500, not in the frozen specification"}
    - {id: OBJ-18, severity: low, target: EXP-SSI-697354, summary: "SCOPE-A and SCOPE-B are numerically identical under the committed inputs at log2 k_DG = 0"}
    - {id: OBJ-19, severity: low, target: "EV-SSI-59f7a2 / DEC-20260805-596d71", summary: "2^73.08 is 2023 deployed storage; 'physically impossible' overstates an economic constant as a mathematical margin"}
    - {id: OBJ-20, severity: low, target: TASK-20260806-fd3518, summary: "duplication audit covered 100/257 files and 12/19 head-reads; one real collision lived in the unread region"}
  duplication_verdicts:
    IDEA-20260806-62ba9d: {verdict: partial_duplicate, collides_with: ["GOAL-SSIQ-001/goal.yaml GD-1", "BATCH-002.yaml SC-1", "BATCH-002.yaml SC-2", "H-SSIQ-90e07b SC-3", "H-WESO-001:80", "H-P13-001:79"], survives_as_new: "the class (a)/(b)/(c) scope partition only"}
    IDEA-20260806-e4c719: {verdict: not_a_duplicate, checked: [IDEA-20260805-e7ee4a, IDEA-20260805-250e50, IDEA-20260805-062bee, IDEA-20260805-2d2c41]}
    IDEA-20260806-9c2f80: {verdict: not_a_duplicate, checked: [IDEA-20260805-250e50, IDEA-20260805-bc8246, IDEA-20260803-48e258, "ideas/catalogue-20260805 B1-9"]}
    IDEA-20260806-d5a34e: {verdict: not_a_duplicate, checked: [IDEA-20260805-c60813, IDEA-20260805-250e50, IDEA-20260805-e7ee4a, IDEA-20260805-062bee]}
    IDEA-20260806-b60c35: {verdict: not_a_duplicate, checked: [IDEA-20260805-2d2c41, IDEA-20260805-062bee, IDEA-20260805-93ee20, "paper_fulltext.md 4.2"]}
  control_can_fail_verdicts:
    EXP-SSI-697354:
      RG-1: {can_fail: code_only, note: "as specified it FAILS: 72.2113 vs [118.25,118.75]"}
      RG-2: {can_fail: false, note: "= RG-1 + declared S=3.0"}
      RG-3: {can_fail: effectively_false, note: "= RG-1 + 1.584963; 0.065-bit sliver only"}
      RG-4: {can_fail: false, note: "disclosure obligation; contract states neither outcome fails"}
      RG-5: {can_fail: false, note: "computed min gap 2.5241, max gap 11.2756 vs required <=6.5 / >=10.5; forced by declared S and A"}
      NULL-OBJECT-N0: {can_fail: false, note: "D_null0 == E(P) identically; computed 11.9613..13.6621; F4 requires a < 0.0039"}
      NULL-OBJECT-N1: {can_fail: false, note: "D_null1 = |E-9.8|; F6 requires E <= 4.9; checked all P in [256,768], never"}
      MONO-1: {can_fail: code_only}
      MONO-2: {can_fail: code_only}
      MONO-3: {can_fail: false, note: "slope is +0.5 identically under MC_P13; NOT_EVALUABLE escape is correct practice"}
      MONO-4: {can_fail: false, note: "computed >= 10.0 bits at lw=10 against a 0.5-bit bar"}
      MONO-5: {can_fail: false, note: "data check whose data is transcribed into the contract; I ran it, all four limbs pass"}
      FITTED-WINDOW-GUARD: {can_fail: omission_only}
      ADVERSARIAL-CORNER: {can_fail: vacuous, note: "no headline lower bound is pre-registered for it to withdraw"}
      SANITY-1: {can_fail: false, note: "MODEL_PATHOLOGY branch algebraically unreachable; audits the sign, cannot see the anchor error of OBJ-2"}
      XCHK-1: {can_fail: code_only, note: "same formula, second expression path"}
      XCHK-2: {can_fail: false, note: "tolerance widened to the 3.51-bit deviation it previously found"}
    proposals:
      IDEA-20260806-62ba9d: {trivial_reduction_null: false, identity_gate: false, superpolynomial_control: true, source_blocked_discipline: process_only, k1_known_answer_gate: true}
      IDEA-20260806-e4c719: {c_blind_arm: false, forced_value_gate_on_c: true, not_applicable_control: weak}
      IDEA-20260806-9c2f80: {random_advice_null: false_as_scheduled, shuffled_fiber: blocked_no_implementation, S0_and_Sp_gates: false}
      IDEA-20260806-d5a34e: {delta_oracle_null: true, frobenius_free_null: true, no_planted_path_null: true, graded_control: true, sequencing: defective}
      IDEA-20260806-b60c35: {arm_M: true, arm_C: false, rho_known_answer_gate: true, within_arm_spread: true, blocked_on: quaternion_sampler_does_not_exist}
  required_controls:
    - "Before dispatch: evaluate MC_P13 at (P=256, log2 w=92.5) against 118.4613 and record the 46.25-bit residual."
    - "Re-anchor the vOW law as log2 T_A = L_paper + E + S + c*sqrt(P) + A + 0.5*max(0, L_mem - log2 w) with a memoryless baseline, and re-derive EV-WESO-001's 'beats Delfs-Galbraith at every tested budget' under it."
    - "Add one control to EXP-SSI-697354 that can fail on the OBJECT rather than the code: assert T_A(P, log2 w = L_mem(P)) == T_A(P, unbounded) under every convention, which is a level check no MONO limb performs."
    - "For b60c35: state a minimum detectable KS effect size and the n reaching it, before Stage 2; drop or re-motivate ARM C."
    - "For 9c2f80: add a preprocessing-frontier row (ST^2-type) to dominated_by before the advice axis is claimed unplotted."
  counterexample_or_mutation: >-
    Rank counterexample to IDEA-20260806-62ba9d R1: let alpha in End(E)\Z and
    beta in End(E)\Q(alpha). Every subfield L of B_{p,infinity} satisfies
    [L:Q] | 2, so a proper Q-subalgebra of a quaternion division algebra is Q or
    a quadratic field and dimension 3 is impossible. Hence Q<alpha,beta> =
    B_{p,infinity} and Z + Z*alpha + Z*beta + Z*alpha*beta is a rank-4 order.
    Two OneEnd outputs suffice for rank 4; the claimed k >= 3 floor is false.
  baseline_comparison: >-
    All five proposals state the five-row frontier correctly (Wesolowski
    p^{1/3+o(1)} time and memory; Delfs-Galbraith p^{1/2}(log p)^{O(1)} at poly
    memory; vOW p^{1/2+o(1)}/w^{1/2} at memory w; MITM p^{1/2} at p^{1/2}; Kohel
    p*(log p)^{O(1)} at poly memory) and none adds an attack row. One unchecked
    axis: 9c2f80 introduces advice and lists no preprocessing row on it. Separately,
    with MC_P13 corrected per OBJ-2 the assessed method LOSES to Delfs-Galbraith at
    every w <= 2^{49.5} entries at NIST-I, reversing EV-WESO-001's committed
    'beats Delfs-Galbraith at every tested budget w = 2^30..2^80'.
  heuristic_challenges:
    - "EXP-SSI-697354 correctly states heuristic_under_test: NONE and validates nothing. Accepted; this is not an objection."
    - "HEUR-XO-3 is a false dichotomy: neither committed convention is the paper's law (Sec. 4)."
    - "e4c719's genericity assumption m = Theta~(D^{1/r}) is unnumbered and unstated; Hermite is one-sided (OBJ-13)."
    - "62ba9d H-RED-1 asserts three outputs are needed for finite index; two suffice, so the heuristic is stated at the wrong arity."
    - "b60c35 correctly identifies that Heuristic 1's only experimental support has a theory comparison and no matched null. Upheld at source (paper l. 246-256)."
  cost_model_challenges:
    - "OBJ-2: MC_P13 anchor error, 46.25/69.30/90.65 bits, attacker-favourable, undetectable by every control in the contract."
    - "MC_VOW misattributes the paper's own interpolation law to a baseline the paper states has negligible memory; double-counts."
    - "SCOPE-A == SCOPE-B under the committed inputs at log2 k_DG = 0 (9.5387/21.9537/38.8387); one observation counted twice."
    - "62ba9d confuses per-call with total cost in the correct direction but with the wrong multiplier; the Isogeny charge is <= 1 bit, not 2.585."
    - "2^73.08 global storage is an economic constant of 2023 presented as a physical margin."
  reduction_and_scope_challenges:
    - "Section 4.1 prices OneEnd (Algorithm 3), not Isogeny. Upheld at source, paper l. 226-234."
    - "The paper's 'previous methods' column is a memoryless Isogeny figure set against a OneEnd figure; EXP-SSI-697354 inherits the asymmetry in T_B = P/2."
    - "[35] = Page-Wesolowski EUROCRYPT 2024, 'One Endomorphism' (paper l. 328). Corpus SC-2 records Theorem 7.2 reducing EndRing to OneEnd_lambda. k = 1."
    - "SC-1 (GRH at the Isogeny arrow) and SC-3 (concrete cost not inheritable) are committed in GOAL-SSIQ-001 and appear nowhere in GOAL-SSI-001's records; GRH count is 0 in EV-SSI-59f7a2, H-SSI-7fe2bf and EXP-SSI-697354."
    - "EXP-SSI-697354's affected list lumps Isogeny/EndRing/OneEnd undifferentiated at l. 792."
    - "d5a34e inflates an IGQ bound into a replacement for twelve closures that include quaternion-side avenues outside the model."
  proof_architecture_challenges:
    - "Observation-fiber: 62ba9d's resource vector cannot distinguish k=1 from k=3 without [35]; it correctly reports the collision, but then fills the cell with an unsound rank derivation instead of leaving it SOURCE-BLOCKED."
    - "Quantifier-order: 62ba9d's own quantifier_order block is correct and is the record's best content; it is undermined by STEP 2 filling the existential it identifies."
    - "Method-ceiling: EXP-SSI-697354's ceiling is 'a locus computed under two wrong laws'; with either law corrected the deliverable changes sign in part of the grid, so the ceiling does not reach the stated objective."
    - "Nearby-object: d5a34e's no-planted-path null is the correct nearby-object control and is genuinely capable of failing; e4c719's ECDLP NOT-APPLICABLE control is not (it is an analyst judgement)."
    - "Boundary/strictness: MC_P13 does not embed the paper's own w=M row as its boundary (OBJ-2); the old method is not correctly embedded."
  narrowest_supported_statement: >-
    See Section 10. In one line: the batch added four non-duplicate directions and
    one contract that cannot be run as frozen; its single genuinely object-level
    control (b60c35 ARM M) is blocked on an unbuilt sampler; the campaign's
    headline number is correctly identified as a OneEnd number but the proposed
    1.585-2.585 bit correction to it is wrong and must be withdrawn.
  next_concrete_action: >-
    Coordinator: open a scoped correction task that (1) recomputes MC_P13 at
    (P=256, log2 w=92.5) against 118.4613, records the 46.25-bit residual, and
    issues a versioned protocol_amendment or a new experiment version for
    EXP-SSI-697354 before any Executor dispatch; and (2) files one superseding
    record carrying SC-1 and SC-3 into EV-SSI-59f7a2/DEC-20260805-596d71 and
    correcting EV-WESO-001's inference sentence and
    analysis/SSI-ECDLP-SYNTHESIS-20260803.md line 171 to name the axis.
    Do NOT dispatch IDEA-20260806-62ba9d until its STEP 2 derived floors are
    withdrawn by a superseding record.
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/reviews/TASK-20260806-9536f4/red_team_report.md
  reviewed_records:
    - ledger/proposals/IDEA-20260806-62ba9d.yaml
    - ledger/proposals/IDEA-20260806-e4c719.yaml
    - ledger/proposals/IDEA-20260806-9c2f80.yaml
    - ledger/proposals/IDEA-20260806-d5a34e.yaml
    - ledger/proposals/IDEA-20260806-b60c35.yaml
    - experiments/EXP-SSI-697354/specification.yaml
    - ledger/hypotheses/H-SSI-7fe2bf.yaml
    - ledger/evidence/EV-SSI-59f7a2.yaml
    - ledger/evidence/EV-WESO-001.yaml
    - ledger/decisions/DEC-20260805-596d71.yaml
    - analysis/SSI-ECDLP-SYNTHESIS-20260803.md
    - inputs/P13-WESOLOWSKI-2026/paper_fulltext.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-fd3518/{duplication_audit.md,ideation_report.md}
    - coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-976fd5/{design_report.md,approval_decision.yaml}
    - coordination/tasks/TASK-20260724-P13-VAL/repro/experiments/EXP-P13VOW-001/cost_model.py
    - coordination/goals/GOAL-SSI-001/batches/BATCH-046/tasks/TASK-20260804-55952a/{red_team_concrete_cost.yaml,implementation/cost_measurements.json}
    - ledger/goals/GOAL-SSIQ-001/{goal.yaml,checkpoints/BATCH-002.yaml}
    - ledger/hypotheses/{H-SSIQ-90e07b.yaml,H-WESO-001.yaml,H-P13-001.yaml}
  inference:
    requested_policy: review-adversarial
    reasoning_effort: xhigh
    resolved_model_id: claude-opus-5
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness resolves every policy alias in
      orchestration/model-policies.yaml to one model. Recorded, never silently
      substituted (AGENTS.md rule 11).
    degraded_allowed: false
    independent_session: true
    model_verified: false
    model_verified_reason: No adapter probe receipt exists for this session.
```
