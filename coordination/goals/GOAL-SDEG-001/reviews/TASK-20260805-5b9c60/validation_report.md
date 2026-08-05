# Independent Validation Report — EXP-SDEG-f7faa8 / H-SDEG-0dd021 / CORR-20260805-9d2e17

- **Task:** TASK-20260805-5b9c60
- **Role:** Validator (independent; did not produce any artifact under review)
- **Reviewed state:** snapshot commit `07c43118` on branch `claude/ssi-ecdlp-experiments-4cwbrq`
- **Reviewed at:** 2026-08-05
- **Scope:** receipt / artifact / control integrity and internal consistency. **NOT** mathematical
  interpretation. **NOT** approval — `approved_by` is and remains the Coordinator's field.

## VERDICT: REVISE

The three artifacts are arithmetically sound and unusually forthcoming: **every one of the
twelve baseline-reproduction values I independently recomputed matched**, and every number I
traced back to EV-SIG-008, EV-SIG-006, EV-DREG-008 and `TASK-20260731-016/results.json` is
present in those records with the meaning the contract assigns it. CORR-20260805-9d2e17's
load-bearing defect finding (D1) is correct at source. Nothing is fabricated; no receipt is
overstated in a way I could detect.

`REVISE` rather than `ADMIT_WITH_QUALIFICATIONS` rests on exactly **three** defects (F-1, F-2,
F-4). Each is a *frozen-parameter or gate-integrity* defect, and CTRL-4 / IR7 make all three
unrepairable after any Stage-1 number is observed. They must therefore be resolved *before*
Stage 1 runs, not after. Everything else in this report is a qualification, not a blocker.

I do not approve or reject. I return a validity verdict on the artifacts.

---

## Part 1 — Baseline-reproduction audit, recomputed independently

I recomputed all of these from the contract's own stated series and nothing else:

> `H_n(z) = (1+z)^nb(n) · (1+z²)^−n · (1+z³)^−n`, `nb(n) = n + 3⌈n/3⌉`,
> `h_k = [z^k] H_n` untruncated, `h_k⁺` = truncate-positive, `φ_full = min{k : h_k ≤ 0}`,
> `N(nb,D) = Σ_{j≤D} C(nb,j)`, `sr_pred(n,D) = N(nb,D) − Σ_{k≤D} h_k⁺`,
> `nrows(n,D) = n·N(nb,D−2) + n·N(nb,D−3)`.

Exact integer arithmetic (Python `fractions`-free integer convolution; formal power-series
inversion of `(1+z²)` and `(1+z³)`, no truncation of the denominator).

| # | Value claimed by the contract's audit | Recomputed | Match |
|---|---|---|---|
| 1 | `sr_pred(9,3..6) = 180 / 1,674 / 9,504 / 28,068` | 180 / 1,674 / 9,504 / 28,068 | **YES** |
| 2 | `sr_pred(12,3..6) = 312 / 3,834 / 29,418 / 156,520` | 312 / 3,834 / 29,418 / 156,520 | **YES** |
| 3 | `HF(9) = [1, 18, 144, 645, 1566, 738, 0]` | `h⁺` = [1, 18, 144, 645, 1566, 738, 0] | **YES** (see note A) |
| 4 | frozen quotient `3,112` | `Σ_{k≤6} h_k⁺ (n=9) = 3,112` | **YES** |
| 5 | `φ_full(9) = 6` | 6 | **YES** |
| 6 | `φ_full(12) = 7` (EV-SIG-008 "freeze degree 7") | 7 | **YES** |
| 7 | `N(24,6) = 190,051` | 190,051 | **YES** |
| 8 | `nrows(9,6) = 45,324` | 45,324 | **YES** |
| 9 | `nrows(12,6) = 183,312` | 183,312 | **YES** |
| 10 | `nrows(12,5) = 31,512` | 31,512 | **YES** |
| 11 | CTRL-B bracket **lower** endpoint `140,504` = `A − Σ_{k≤6} h_k` | 174,035 − 33,531 = **140,504** | **YES** |
| 12 | CTRL-B bracket **upper** endpoint `156,520` = `sr_pred` (arm-P rule) | 156,520 | **YES** |

Additional structural values quoted in the contract, also recomputed and matching:

- `nb = 18 / 22 / 23 / 24 / 28 / 29` at `n = 9/10/11/12/13/14` — **matches** (and confirms the
  contract's and CORR D5's point that this is *not* the `nb = 2n` family off-lattice).
- `N(18,6) = 31,180` (CELL-C `ncols`) — **matches**.
- Stage-2 ladder column counts `31,180 / 110,056 / 145,499 / 190,051 / 499,178 / 621,616` —
  **all six match**.
- `nrows(13,6) = 361,933` — **matches**.
- `rankK6 = nrows − sr_pred = 183,312 − 156,520 = 26,792` — **matches** EV-SIG-008.
- `C(24,6) = 134,596`; `156,520 − 29,418 = 127,102`; `134,596 − 127,102 = 7,494` — the
  contract's claim that `h_6(12)` is *forced* by the two committed `sr_pred` values is correct.

**NO baseline value failed to reproduce.** CTRL-6 as written is satisfiable and SR5 will not
fire on any of the values it names.

> **Note A (not a mismatch, but state it precisely).** The `0` in `HF(9)` is the *truncation
> convention* `h_6⁺ = 0`, not the series coefficient. The untruncated `h_6(n=9) = −8,097`. The
> contract is internally consistent here — clause (4) defines `h⁺` and EV-SIG-006 records
> `HF at n=9: [1, 18, 144, 645, 1566, 738, 0, ...]` in exactly that convention — but since the
> whole hypothesis is that *the truncation is the suspect*, a reader must not read `HF(9)`'s
> final `0` as a reproduced property of the system. It is the convention under test reproducing
> itself.

### Corroboration the contract did not claim, found during recomputation

Two committed numbers in `coordination/goals/GOAL-DREG-001/batches/BATCH-003/reviews/RT-CTRLB.md`
("sem quotient 35462 vs 17515, 2.02x") land exactly on the frozen form's own quantities at
CELL-B: `Σ_{k≤6} s_k = 26,037 + (7,494 − 16,016) = 17,515`, and `174,035 − 138,573 = 35,462`.
Neither is cited by the contract. This is independent arithmetic support for the skeleton and
is recorded here as a finding *for* the artifacts, not against them.

---

## Part 2 — Numbered findings

### F-1 (BLOCKING). CELL-C's declared arm contradicts its own gate threshold G3, and the choice between the two readings is a live free parameter.

`specification.yaml` declares `CELL-C: arm: P (full support, u_6 = 0)`. The frozen arm-P rule
is `rank_P = sr_pred − max(0, sr_pred + u_D − N(nb,D))`. At CELL-C, `u_6 = 0`, so the projection
loss is zero and **the arm-P rule returns `sr_pred(9,6) = 28,068`, identically, for every
candidate**. G3 demands *exactly* `31,179`. Under the declared arm, **G3 is unsatisfiable by
construction** — not failed by the model, but excluded by the cell's own label.

Under an arm-R reading of the same cell (`A = 31,180`, `s_6 = h_6 − 0 = −8,097`, `φ_F = 6`,
`|V| = 1`) the three frozen candidates give:

| | Q | predicted rank | G3 (target 31,179) |
|---|---|---|---|
| C1 HARD_FREEZE | `Σ_{k<6} s_k = 3,112` | 28,068 | FAIL |
| C2 SIGNED_CARRY | `max(1, −4,985) = 1` | **31,179** | PASS |
| C3 VARIETY_COLLAPSE | `|V| = 1` (D ≥ φ_F) | **31,179** | PASS |

So the arm label of CELL-C flips G3 from `FAIL, FAIL, FAIL` to `FAIL, PASS, PASS`. The contract
never states which rule applies at CELL-C; CTRL-2 states only the target. This is precisely the
class of choice CTRL-4 and IR7 exist to forbid: it is resolvable after the cell is seen, and it
materially changes the per-candidate table that the mandatory BRANCH NEGATIVE deliverable (a)
must publish. It must be fixed in the frozen text before Stage 1.

Substantively, N0 also does not fit the arm-P *definition* — arm P is "a full-support SYSTEM
whose Macaulay columns are deleted afterwards", and no columns were deleted from N0; its
up-closure is simply complete at D6. On the contract's own CTRL-9 test (arm from construction
artifacts) N0 reads as arm R with `u_6 = 0`, not arm P. That is the Coordinator's call to make
and record, not mine — but it must be made *in the frozen file*.

### F-2 (BLOCKING). G2 as specified in `metrics.primary` cannot fail, and is mislabelled as HEUR-BF-3's falsifier.

At CELL-B the arm-P projection loss is `max(0, 156,520 + 16,016 − 190,051) = max(0, −17,515) = 0`.
The slack is 17,515 — the rule would return `156,520` for **any** `u_6 ≤ 33,531`, for **all three**
candidates (the arm-P rule contains no `Q` and no `|V|`, so it is candidate-independent). G2 is
therefore a **constant PASS** with a wide margin: no possible candidate, and no plausible
perturbation of the committed inputs, could make it fail.

The contract states "G2 is HEUR-BF-3's own falsifier" and the hypothesis's HEUR-BF-3
`falsification_condition` is a **disjunction** — (i) arm P does not return 0, *or* (ii) a
candidate returns the same value for both arms while the committed ranks differ by 7,110. Half
(i) is the tautology above. Half (ii) is genuinely discriminating and **C2 triggers it**: C2
returns `156,520` at CELL-A (arm R) *and* `156,520` at CELL-B (arm P), while the committed ranks
are `149,410` and `156,520`. But half (ii) lives only in CTRL-3 prose and in the hypothesis
record — it is **not part of the `GATE VERDICT` computation**, which is defined as `G1 ∧ G2 ∧ G3
∧ G5`. As frozen, one of the four conjuncts is vacuous and the live arm-rule falsifier is
outside the verdict. Add the CTRL-3 cross-arm condition to the gate metrics, or restate G2's
claimed role honestly. Both are text changes and both are forbidden after Stage 1 by IR7.

### F-3 (QUALIFICATION, and the answer to the disclosure question). The `coordinator_prior_disclosure` does not leak a way to pre-select a *winner* — there is none. It does determine the entire gate outcome at freeze time, which the disclosure's own wording understates.

**Recomputed, from the frozen series and nothing else:**

- `h_6(n=12) = 7,494` — **matches** the disclosure (and is independently forced by the two
  committed `sr_pred` values, as the disclosure says).
- `u_6 = 16,018` at CELL-A — **confirmed** by two independent derivations from EV-SIG-008's own
  committed data: `190,051 − 174,033 = 16,018` and `C(24,6) − 118,578 = 16,018`.
- `s_6 = h_6 − u_6 = 7,494 − 16,018 = **−8,524**` — **matches** the disclosure exactly.
- `φ_F(12, D=6) = 6 < φ_full(12) = 7` — **confirmed**. The disclosed "effective freeze pulled
  7 → 6" is arithmetically correct.

Carrying that forward against the frozen candidate list at CELL-A (`A = 174,033`, `|V| = 2`,
`Σ_{k<6} s_k = 26,037`, `Σ_{k≤6} s_k = 17,513`):

| | Q | predicted rank | predicted deficit | \|d − 7,110\|/7,110 | G1 (< 0.05) |
|---|---|---|---|---|---|
| C1 | 26,037 | 147,996 | **8,524** | 0.1989 | FAIL |
| C2 | 17,513 | 156,520 | **0** | 1.0000 | FAIL |
| C3 | 2 | 174,031 | **−17,511** | 3.4629 | FAIL |

**Assessment, stated plainly as instructed.** The disclosure could **not** have been used to
pre-select a winning candidate, because **no candidate wins**. The gate is not compromised in
the direction of a false positive; that direction is closed. What the disclosure does establish
is stronger than what it claims: `s_6 = −8,524` *is* C1's G1 prediction (`deficit = −s_6 =
8,524`), so the disclosed quantity hands the reader C1's miss directly, and C2/C3 follow in one
line each. Combined with `G2 ≡ PASS` (F-2) and `G5 ≡ PASS` (Part 3), **the whole Stage-1 verdict
is determined at freeze time from committed inputs: F1, gate FAIL, under either reading of
F-1.** The contract's "the Coordinator holds a NON-TRIVIAL PRIOR THAT G1 WILL NOT PASS"
therefore understates its own epistemic position: this is a determined outcome, not a prior.
Two consequences the Coordinator should see stated:

1. **BRANCH POSITIVE is unreachable through this contract**, so the Stage-2 ladder — the
   substantive research — can never be authorized via this route. The negative disposition is
   not one of two branches; it is *the* deliverable.
2. Under CLAUDE.md rule 9 this needs its successor named, which the contract does supply
   (BRANCH NEGATIVE (d): the 7,110 residual mechanism stays OPEN; `IDEA-20260803-fa9839`
   consumes the boundary). That obligation is met.

**Evidence *against* band-fitting, which I looked for and did not find.** The 5 % G1 band is not
a post-disclosure choice: it is inherited verbatim from `IDEA-20260803-202a15`
(`two_number_point_prediction`: "within 5 per cent of 7,110"), filed 2026-08-03, two days before
the conversion in which `s_6` was computed. And C1's miss is 19.9 %, so no band in `(0.05,
0.199)` would have changed the verdict. I find no sign the threshold was selected to force
either outcome.

I record explicitly: **this arithmetic is not a Stage-1 execution and is not a gate outcome.**
It has no run receipts, satisfies none of `required_artifacts`, and does not discharge CTRL-7. It
is offered solely as the integrity assessment this task asked for.

### F-4 (BLOCKING, narrow). "VERIFIED PER CELL, never assumed" is not dischargeable at CELL-D from committed data, and the blanket claim behind it is contradicted by a committed record.

Clause (6)'s identity `s_k = h_k (k<D)`, `s_D = h_D − u_D` is conditioned on `u_k = 0 for k < D`,
which the contract twice insists is verified per cell. Checking each gate cell:

| cell | can `u_k = 0 (k<D)` be verified from committed data? |
|---|---|
| CELL-A | **YES** — EV-SIG-008 commits the full degree histogram `1/24/276/2,024/10,626/42,504/118,578`; degrees 0–5 are complete against `C(24,k)`, deficiency 16,018 sits entirely in degree 6. |
| CELL-B | **YES** — `results.json` admission metric `deleted_degree_histogram_equals_6_16016: true`. |
| CELL-C | **YES** — forced arithmetically: `ncols = 31,180 = N(18,6)`, so every slice is complete. |
| CELL-D | **NO** — no degree histogram for the n=12 D5 column set is committed anywhere I could find. |

The hypothesis's own enumeration of verified cells (`mechanism`, ingredient (ii)) lists n=9 D5/D6
and n=12 D6 at both seeds — **and omits n=12 D5**, i.e. omits CELL-D, a *gate* cell.

Worse, the nearest committed reading of that object contradicts the blanket claim.
`coordination/goals/GOAL-DREG-001/batches/BATCH-003/reviews/RT-CTRLB.md` records, for the
seed-2026 n=12 D5 restriction:
`columns: {kept: 46717, deleted: 8738, full: 55455, deleted_degree_histogram: {5: 8736, 4: 2}}`
— i.e. **`u_4 = 2 ≠ 0`**. The hypothesis's "Every committed cell has `u_k = 0` for `k < D`" is
false as written against committed state.

**Severity is limited, and I verified why.** I recomputed CELL-D under both histograms:

- seed-2 figures (`A = 46,709`, `u_5 = 8,746`): `φ_F = 6`, `Σ_{k≤5} s_k = 17,291`,
  C1 = C2 = C3 = **29,418**, deficit **0** → G5 PASS for all three.
- seed-2026 figures (`A = 46,717`, `u_4 = 2`, `u_5 = 8,736`): `Σ_{k≤5} s_k = 17,299`,
  C1 = C2 = C3 = **29,418**, deficit **0** → G5 PASS for all three.

G5's outcome is invariant, because the contract's own support-independence corollary
(`A − Σ_{k≤D} s_k = N(nb,D) − Σ_{k≤D} h_k`, which I verified holds exactly at all four gate
cells) makes it so. So this is **not** an evaluability blocker for the gate's verdict. It is
blocking for a narrower reason: the contract asserts a per-cell verification it cannot perform
at CELL-D, and asserts a universal that a committed record falsifies. Under IR5/CTRL-6 that
assertion is load-bearing text and cannot be corrected after Stage 1. Restrict the claim to the
three cells where it holds, and mark CELL-D's precondition as assumed-with-invariance-argument.

**Related, and unreported by the contract:** `46,709 / 8,746` (seed 2) vs `46,717 / 8,738`
(seed 2026) is a **third** unreconciled n=12 pair, of the same shape and the same 8-column size
as the D6 pair (`174,033/16,018` vs `174,035/16,016`) that the contract *does* surface as a live
HEUR-BF-1 datum. The contract surfaces one and not the other. The same builder-identity question
applies. (Also noted: RT-CTRLB uses sem D5 rank `28,096` where EV-SIG-008 commits `28,097` — a
further one-off in the same lineage.)

### F-5 (QUALIFICATION). The support-independence corollary's stated gloss is false at one gate cell.

The identity `A − Σ_{k≤D} s_k = N(nb,D) − Σ_{k≤D} h_k` is **true**; I verified it at all four
gate cells. Its stated consequence — "an untruncated restricted prediction equals the untruncated
full one, *i.e.* `sr_pred` is SUPPORT-INDEPENDENT" — is a non-sequitur wherever `D ≥ φ_full`,
because `sr_pred` is built from `h⁺`, not `h`. At CELL-A (n=12, D=6, `φ_full = 7`) both sides
equal `156,520 = sr_pred` ✓. At **CELL-C** (n=9, D=6, `φ_full = 6`) both sides equal **36,165**,
while `sr_pred(9,6) = 28,068`. The corollary is fine as an identity; the sentence that reads it
as a statement about `sr_pred` is out of scope at CELL-C, which is a gate cell. Text fix.

### F-6 (QUALIFICATION). Citation and "committed" labelling defects.

1. **CELL-G is sourced to the wrong record.** `specification.yaml` gives
   `{id: CELL-G, ..., source: EV-SIG-008}` with `rank 27,292 / deficit_6 776 / extra_6 8,897 /
   variety_size 6`. Those four numbers are in **EV-SIG-006** (`sem D6 rank 27,292, deficit 776,
   ... extra_6 8,897`; `|V_sem| = 6`). EV-SIG-008 carries only `residual_6 = 2,615`, and
   attributes it to EV-SIG-006. Verified present in EV-SIG-006; **mis-cited**, not fabricated.
2. **CELL-F attributes the sem's columns to N1 — UNVERIFIED.** `{CELL-F, N1, ncols: 11032,
   u_5: 1584, ...}`. EV-SIG-006 records `11,032` as the **sem's** D5 `ncols` (`ncols sem/null:
   ... D5 11,032/12,615`) and `1,584` as the **sem's** D5 top-slice miss. N1's D6 column set is
   committed as equal to the sem's (29,332); **its D5 column set is nowhere committed**, and the
   old null's D5 `ncols` is committed as `12,615` (missing 1), not 11,032. N1's *rank* `9,135`
   and *extra* `369` at D5 **are** committed and correct. CELL-F is non-gating, so this does not
   touch the gate; the attribution should be marked UNVERIFIED rather than committed.
3. **Derived values presented under `committed:` blocks.** All arithmetically correct — I checked
   each — but none is quoted from its source record: `u_6 = 16,018` (CELL-A), `u_5 = 8,746`
   (CELL-D), `nrows = 45,324` (CELL-C), `deficit_of_this_null = 0` (CELL-B), `ncols_minus_V`
   values. Recommend a `derived:` sub-block so a reader is never asked to infer which is which.

### F-7 (QUALIFICATION). IR1–IR13: present and each decidable, but the non-overlap claim fails for one pair and IR7 has no named artifact.

All thirteen are present. Each is decidable from a named or clearly implied artifact, with two
exceptions:

- **IR3 ∩ IR5 overlap with conflicting remedies.** A rebuilt `ncols` disagreeing with a committed
  cell fires IR3 (*that cell* is invalid — instrument drift) **and** IR5 (*the whole run set* is
  invalidated and SR5 halts). Same trigger, two different consequences, no precedence rule.
- **IR7 names no decidable artifact.** It forbids post-hoc change to the frozen text, but the
  contract's own `blocking_nulls` records `execution_plan.protocol_hashes` as absent (correctly —
  the producing session had no shell and refused to fabricate a hash). In practice IR7 *is*
  decidable, against snapshot commit `07c43118`, which I verified touches only
  `experiments/EXP-SDEG-f7faa8/{specification.yaml,amendments/.gitkeep,runs/.gitkeep}`,
  `ledger/hypotheses/H-SDEG-0dd021.yaml`, `ledger/corrections/CORR-20260805-9d2e17.yaml`. Naming
  that commit in the contract closes IR7 at zero cost and without fabricating anything.

### F-8 (MINOR). CTRL-4 and IR7 freeze "all seven predictions"; the hypothesis lists eight.

`H-SDEG-0dd021.predictions` has 8 entries (G1, G2, G3, G5, ladder error, saturation shape,
crossing, HEUR-BF-1 spread). A frozen-parameter clause that miscounts the set it freezes is a
small hole in exactly the clause that must not have holes.

---

## Part 3 — Direct answers to the four checks

### Check 3 — Gate evaluability from committed inputs alone. **CONFIRMED, with F-1 and F-4 attached.**

The `blocking_nulls` entry on `variety_sizes_missing` is **correct**: the missing `|V|` values
(n=12 sem, n=12 arm-P null) are genuinely not needed. I confirmed cell by cell that the gate uses
only `|V_N0(9)| = 1` (CELL-C, EV-SIG-006) and `|V_N1(12)| = 2` (CELL-A and CELL-D, EV-SIG-008
"`|V_N1| = 2`"), both committed; and that CELL-B is arm P, whose rule contains no `|V|` term at
all. **No gate cell requires an uncommitted `|V|`. Stage 1 is not unrunnable for that reason.**

Per-gate inputs, all traced to committed records:

- **G1** — `A = 174,033` ✓, `u_6 = 16,018` (derived, doubly confirmed) ✓, `|V| = 2` ✓,
  `sr_pred = 156,520` ✓. **Evaluable.**
- **G2** — `sr_pred = 156,520` ✓, `u_6 = 16,016` ✓ (`ncols_deleted`), `N(24,6) = 190,051` ✓
  (`ncols_null_full`). **Evaluable** (and constant — F-2).
- **G3** — `A = 31,180` ✓, `u_6 = 0` ✓ (forced), `|V| = 1` ✓. **Evaluable only once F-1 is
  resolved**; as frozen, which rule applies is undetermined.
- **G5** — `A = 46,709` ✓ (EV-SIG-008 "ncols 46,709"), `u_5 = 8,746` (derived) ✓, `|V| = 2` ✓;
  `φ_F` additionally requires the D5 per-degree `a_k`, which is uncommitted (F-4). **Evaluable in
  outcome** (invariant under both committed histograms, verified), **not in its declared
  verification obligation.**

### Check 4 — Decidability and a reachable negative. **CONFIRMED.**

The success criterion is decidable purely from the predefined metrics: `PASS iff ∃ one candidate
satisfying G1 ∧ G2 ∧ G3 ∧ G5`, each a comparison of an integer against a committed integer (three
exact, one banded at 5 %). No outcome depends on a judgement call. A negative is reachable and
named (`F1`, BRANCH NEGATIVE), with a mandatory deliverable of five enumerated parts and `F7`
making an incomplete negative a non-finish. There is no third branch and no outcome that
escapes classification. **The contract cannot report "no result".**

The symmetric concern is live and is F-3: the *positive* branch, not the negative, is the
unreachable one.

### Check 5 — Frozen-parameter integrity. **CONFIRMED for the candidates; FAILED for the CELL-C arm assignment.**

- C1 / C2 / C3 are each fully specified, single-valued and parameter-free, and the list is closed
  at three before evaluation. I evaluated all three at all four gate cells without needing to
  choose anything. ✓
- The arm rule for P is fully specified. ✓
- Arm assignment is required to precede evaluation (CTRL-9) and to come from construction
  artifacts (IR6), and CELL-A / CELL-B / CELL-D each carry an `arm_evidence` block that I checked
  against source: CELL-B's classification is directly supported by `results.json`
  (`arm: null_restricted_to_sem_support`, `deleted_set_equals_null_minus_sem: true`,
  `null_system_hash_equals_ctrl_a_pin: true`, `restriction_sha256_kept_idx` present). ✓
- **CELL-C's assignment is the failure** (F-1): the declared arm makes its own gate threshold
  unreachable, so the assignment is de facto open and can be settled after the cell is seen. That
  is a free parameter, and it is the only one I found.
- Two smaller specification gaps of the same kind: `φ_F` is under-specified whenever `φ_F > D`
  (clause (6)'s shortcut stops at `s_D`; the primary definition via `A_F(z)` is fine but needs
  per-degree `a_k`) — this bites at CELL-D; and the `s_k` for `k > D` are never stated.

### Check 6 — IR1–IR13. **Present: YES. Each decidable: YES (2 caveats). Non-overlapping: NO.** See F-7.

---

## Part 4 — What I verified against source and found correct

Recorded because a validation report that lists only defects misrepresents the artifact.

**Every number in the task's verification list traced to source and confirmed:**

- EV-SIG-008: `7,110` ✓ (GATE 1 FINAL, "deficit_6 = 7,110"), `rank 149,410` ✓, `156,520` ✓,
  `ncols − |V| = 174,031` ✓ (stated verbatim in the Unexpected/rule-8 block), `ncols 174,033` ✓,
  `nrows 183,312` ✓, `rankK6 26,792` ✓, `|V_N1| = 2` ✓, and the whole CELL-D block
  (`46,709 / 31,512 / 29,418 / extra 0 / sem 28,097 / 1,321 / 1,322 / 0.0 %`) ✓.
- EV-DREG-008 + `TASK-20260731-016/results.json`: `sr_pred = 156,520` ✓ (`anchors`),
  `rank_null_restricted = 156,520` ✓, `rank_sem = 138,573` ✓, `ncols_restricted = 174,035` ✓,
  `ncols_deleted = 16,016` ✓, `ncols_null_full = 190,051` ✓, `deficit_genuine = 17,947` with
  `deficit_genuine_formula = "rank(null|sem_support) - 138573"` ✓ **verbatim**,
  `rank_sem_anchor_138573_unchanged: true` ✓, preregistered bracket `[140504, 156520]` ✓.
- EV-SIG-006: frozen quotient `3,112` ✓, `HF at n=9: [1, 18, 144, 645, 1566, 738, 0, ...]` ✓,
  N0 `rank 31,179 = ncols − |V| = 31,180 − 1` ✓ with `extra 4,986` ✓ and `|V_null_old| = 1` ✓,
  N1 `rank 28,939 / sr_pred 28,068 / deficit −871 / extra 7,226 / |V| = 0 / ncols 29,332` ✓.
- **`31,179` for G3** ✓ (EV-SIG-006, machine-confirmed, determinism rerun).
  **`29,418` for G5** ✓ (EV-SIG-008 GATE 3 FINAL, "N1 null D3/D4/D5 ranks == sr_pred
  (312/3,834/29,418), extra 0").

**CORR-20260805-9d2e17 D1 is correct at source, and it is the load-bearing finding.** I checked
the proposal rather than the correction's quotation of it: `IDEA-20260803-202a15` does assert
"RETURNS 7,110 FOR THE COLUMN-MATCHED NULL **AND 17,947 FOR THE SUPPORT-RESTRICTED NULL** AT
n = 12, D = 6" and "THEY ARE DIFFERENT NULLS". The committed `results.json` records
`rank_null_restricted = 156,520 = anchors.sr_pred` — the support-restricted null's own defect is
exactly **0**, and 17,947 is `rank(null|sem_support) − 138,573`, the **sem's** deficit against it.
The proposal's central design device is wrong as written; the correction states this without
editing the proposal (AGENTS.md rule 4 respected — I confirmed `IDEA-20260803-202a15` is
untouched by commit `07c43118`); and the contract does not inherit the error — it gates on 7,110
and 0, and IR13 makes the misattribution an invalidation condition. **D2–D6 also check out
against source.**

**Other integrity checks that passed:**

- `approved_by: null`, `status: review_required`, no `stage2_authorization_decision_id`.
  **Nothing is authorized by these artifacts**, exactly as the commit message states.
- `GOAL-SDEG-001.next_action` is quoted **verbatim** in the contract ("Protocol design PASS.
  Defer activation/executor until ECDLP verifier-hash and precommit residuals clear under a
  separate ledger authorization; no runs now."). SR1 and the Stage-2 block are consistent with it.
- Snapshot `07c43118` touches only the four declared paths plus two `.gitkeep` files. No ledger
  record was overwritten. Working tree clean at review time.
- `tools/validate_ledger.py` reports **1** error
  (`experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/manifest.yaml: run.code.command
  missing`). I confirmed that file exists unchanged at parent `9e12ad3d`: **pre-existing and
  unrelated to these artifacts**, as the commit message claims. Note that it is a *different* run
  from the CELL-B lineage — EV-DREG-008 explicitly routes CELL-B's receipt to the coordination
  task artifacts, not to that manifest.
- The G1 band arithmetic is self-consistent: `7,110 ± 5 % = [6,754.5, 7,465.5]` ✓ and the stated
  rank window `[149,054.5, 149,765.5]` ✓. The G2 rationale (`156,520 × 5 % = 7,826 >` the entire
  G1 effect) ✓. Nine cells (CELL-A..I), four gates, three candidates — all counts consistent
  except F-8.
- The provenance asymmetry is disclosed rather than hidden, and I confirmed it at source:
  EV-SIG-008's `artifact_absence_statement` does say "no claim in this record is bound to a frozen
  protocol or to a reproducible run receipt through the ledger". IR11 correctly forbids citing
  those receipts as a reproduction. **The 7,110 anchor is UNVERIFIED as a live receipt** — it
  survives only via transcript and branch `exp-sig-008-artifacts` commit `d1d36dd`, which I did
  not attempt to fetch and therefore cannot confirm. The contract already says exactly this.

---

## Part 5 — Minimal repair list to clear REVISE

Three text changes to `experiments/EXP-SDEG-f7faa8/specification.yaml` (and the mirrored clauses
in `H-SDEG-0dd021`), all before any Stage-1 number is observed, all forbidden afterwards by IR7:

1. **F-1** — State which rule applies at CELL-C, with its CTRL-9 construction evidence, and make
   G3's satisfiability consistent with that choice. (If N0 is arm P, G3 is unreachable and must
   say so; if arm R with `u_6 = 0`, say that and cite the construction.)
2. **F-2** — Either add the CTRL-3 cross-arm condition to the `GATE VERDICT` computation, or drop
   the claim that G2 is HEUR-BF-3's falsifier and record that G2 is a constant PASS with slack
   17,515.
3. **F-4** — Restrict "every committed cell has `u_k = 0` for `k < D`" to CELL-A/B/C; mark CELL-D's
   precondition as assumed, with the invariance argument (verified above, G5 = 0 under both
   committed histograms); and surface the `46,709/8,746` vs `46,717/8,738` pair alongside the D6
   pair already surfaced.

Recommended but non-blocking: F-3 (restate the disclosure as a determined outcome, not a prior),
F-5, F-6 (fix CELL-G's source to EV-SIG-006; mark CELL-F's `ncols`/`u_5` UNVERIFIED; separate
`derived:` from `committed:`), F-7 (name commit `07c43118` as IR7's decidable artifact; give
IR3/IR5 a precedence rule), F-8 (seven → eight).

---

## Statement of limits on this report

- I did not execute Stage 1, produce any run receipt, or satisfy CTRL-7. The arithmetic in F-1,
  F-3 and F-4 is integrity assessment, not a gate outcome, and no part of it may be cited as one.
- I did not fetch branch `exp-sig-008-artifacts` `d1d36dd`; the 7,110 anchor's underlying receipt
  is **UNVERIFIED** by me, as the contract itself already records.
- I verified no rank measurement and re-ran no solver. Every committed rank in this report is
  taken as recorded; only the *closed-form* values were recomputed.
- Claim tier of everything reviewed is **toy**. Nothing here bears on ECDLP hardness, moves any
  exponent, or narrows KN-OPEN-002. `sota_delta` zero.
- Write scope honored: this file only. No ledger record, contract, hypothesis, correction or
  proposal was edited.

---

**Validator verdict: REVISE** — arithmetically sound and honestly disclosed; three
frozen-parameter/gate-integrity defects (F-1, F-2, F-4) must be closed in the frozen text before
Stage 1, because IR7 makes them uncloseable after. Approval or rejection is the Coordinator's
decision, not mine.
