# RT-PREFREEZE-EXP-SSIQ-a85692-v2 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v2.yaml` (H-SSIQ-137200), GOAL-SSIQ-001 BATCH-005

**Reviews `experiments/EXP-SSIQ-a85692/specification_v2.yaml` at `status: draft`
(this task's working-tree read; the amendment is not yet snapshot-committed by
the Coordinator, and this report changes nothing under
`experiments/EXP-SSIQ-a85692/`, including its already-frozen v1
`specification.yaml` at commit `96ad45de`, and no ledger record — those
remain the Coordinator's alone to touch.** Every other input named in the
launching task was read in full, not sampled, per GD-6's standing repair as
formalized by GD-7's standing repair for prefix-truncation formulas
(`ledger/goals/GOAL-SSIQ-001/goal.yaml` GD-6 and GD-7 entries): v1
`specification.yaml` (614 lines), `RUN-SSIQ-a85692-a/raw-result.json` (full,
including the complete `truncation_fallback.per_prime_estimate` array) and
`execution_report.yaml` (full), `RT-BATCH-004.md` and `VAL-BATCH-004.md`
(full), `EV-SSIQ-94de20.yaml` and `DEC-20260805-a4e04e.yaml` (full),
`goal.yaml`'s GD-7 entry and `next_action`, `H-SSIQ-137200.yaml` (full), and
— beyond what the task named — the actual implementation code at
`experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py`
(`apply_truncation_fallback`, `run_phase_minus1_on_confirmatory_set`, and
`main()`'s call sites), because the amendment's own claim about which
functions change is a checkable, code-level fact, not a prose assertion to
take on faith — this is the same discipline `VAL-BATCH-004.md` §3.2 applied
to v1's fallback text and it is what surfaces this review's central finding.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: >-
    self-reported by this Claude Code subagent session; not probe-verified
    this session (no `orchestration.adapter doctor --probe` run here).
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs `model: inherit`. Every
    credentialed backend under this environment has previously been found
    unprobeable (VAL-BATCH-003, RT-BATCH-003, RT-PREFREEZE-EXP-SSIQ-a85692,
    RT-BATCH-004, VAL-BATCH-004), so this is recorded as the standing
    condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    is not corroboration from a distinct model, and it does not upgrade the
    campaign's evidence tier by itself.
```

---

## Bottom line up front

Checks (a) and (b) — the two things GD-7's standing repair exists specifically
to force — both **pass cleanly**. The draft's `scope_reduction_fallback_v2`
text is unambiguous cumulative-prefix language, and its own WORKED CHECK
arithmetic (3041.7s at the 4th prime, 6138.3s at the 6th) is independently
re-derivable byte-for-byte from `raw-result.json`'s own
`truncation_fallback.per_prime_estimate` array with zero new compute (see
below). **But the amendment does not actually deliver what it claims to
deliver, and the reason is not in the text the draft's own pre-freeze
checklist asks the reviewer to scrutinize — it is in code the draft's
`required_artifacts_note` claims is untouched.** `compute_delta_e.py`
contains a **second, independent instance of the exact GD-7-defective formula**
(`T_PRIME = 0.5 * WALL_CLOCK_BUDGET_SECONDS / len(PRIMES)`, i.e. the same
`0.5×7200/12 = 300s`), used not for admission but as a **hard per-prime real
wall-clock cap during the actual Phase -1 search**
(`run_phase_minus1_on_confirmatory_set`, called from `main()` with `T_PRIME`
unchanged). This amendment corrects the admission-side reading of that
formula but never touches the execution-side instance of the identical
constant. The consequence, quantified below from numbers already on disk: at
most 1–2 of the 4 admitted primes will likely clear `M-COVERAGE >= 0.5` in
real execution, so the amendment as drafted will most likely still return
`DATA-UNAVAILABLE-BLOCKED` — reproducing GD-7's practical outcome under a
different, unaddressed mechanism, while burning real compute this time. This
is **PF-1, BLOCKING**, and it is exactly the shape GD-4 through GD-7 all
share: a frozen (or, here, about-to-be-frozen) element nobody stress-tested
because the reviewer's attention was correctly, but not completely, drawn to
the one formula everybody already knew to look at.

Three further findings (PF-2 through PF-4) are also required before freeze,
each a genuine specification gap that would otherwise leave an Executor to
improvise mid-run — exactly what this campaign's invalidation-rules
discipline exists to prevent. One (PF-5) is advisory.

---

## (a) Independent re-derivation of the individual-cap vs. cumulative-prefix readings

Re-read `scope_reduction_fallback_v2` cold, without reference to
`EV-SSIQ-94de20`/`DEC-20260805-a4e04e`'s own arithmetic, to check whether the
text supports two readings the way v1's did.

**It does not — this is the one place the draft is unambiguous, and it says
so explicitly.** The operative sentence: *"Using
per_prime_cost_estimate_v2's per-prime estimates, ascending by prime size,
compute the RUNNING CUMULATIVE SUM of estimated costs. TRUNCATE the
confirmatory prime set to the largest ascending PREFIX whose CUMULATIVE sum
is <= T_reserved (3600s) — this is the fix: the budget check is against the
prefix's TOTAL estimated cost, not against each prime's estimate compared to
a fixed 1/12 equal share of the reserved budget."* There is no dangling
"per-prime" comparison left anywhere in the prose an Executor could
mistakenly implement as an individual cap; the text explicitly names and
rejects the wrong (v1) reading in the same sentence that states the right
one. An **individual-cap reading is not constructible from this text at
all** — unlike v1's `scope_reduction_fallback_pinned_before_data`, which
never used the word "cumulative" and left "estimate each pre-registered
prime's full-coverage cost" genuinely open to either check. **Check (a)
passes: the admission-side wording is unambiguous.**

(What is *not* covered by this unambiguous wording — the real per-prime
execution-time cap applied once a prime is admitted — is a completely
separate mechanism the text never mentions at all. See PF-1.)

## (b) Independent re-verification of BATCH-004's own numbers under the cumulative reading

Recomputed the running cumulative sum directly from
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a/raw-result.json`'s
`truncation_fallback.per_prime_estimate` array (already committed, zero new
compute), independent of the draft's own WORKED CHECK text and independent
of `EV-SSIQ-94de20`/`DEC-20260805-a4e04e`:

| # | prime | `estimated_full_coverage_seconds` (as committed) | running cumulative sum |
|---|---|---|---|
| 1 | 2437 | 379.72598012288415 | 379.726 |
| 2 | 3889 | 598.9492263793945 | 978.675 |
| 3 | 5737 | 900.3811899820964 | 1879.056 |
| 4 | 7333 | 1162.666145324707 | **3041.722** |
| 5 | 8893 | 1405.3775965372722 | 4447.100 |
| 6 | 10657 | 1691.1507568359375 | **6138.251** |
| 7 | 12541 | 1984.753318786621 | 8123.004 |

Cumulative sum crosses `T_reserved = 3600s` between primes 4 and 5 (3041.722
≤ 3600 < 4447.100) and crosses the full `7200s` between primes 6 and 7
(6138.251 ≤ 7200 < 8123.004). **This exactly reproduces the Coordinator's
cited figures (3041.7s at the 4th prime / 6138.3s at the 6th) to the digits
stated**, independently re-derived from the raw array rather than trusted
from the ledger synthesis. **Check (b) passes**: a cumulative reading of the
identical, already-committed numbers admits exactly 4 primes
(`{2437, 3889, 5737, 7333}`) under the reserved half-budget, which is the
operative `T_reserved=3600s` cutoff the draft's own formula uses — the
"6 primes within 7200s" figure is context for `coverage_widening_note`
(see PF-2), not itself the admission rule.

---

## (c) Two-point smoke test / linear interpolation soundness

**The interpolation is not load-bearing for the primary fix (correctly
disclosed as such: "the two-point smoke test is a secondary accuracy
improvement, not load-bearing for reaching >=4 primes"), so it does not
block on that basis alone. But it has a real, undisclosed failure mode
distinct from the one `invalidation_rules_v2_additions` checks for.**

The STOP condition catches only gross non-monotonicity (`c_max < c_min`). It
does **not** catch the more physically plausible failure mode: **the true
cost-vs-prime relationship is concave** (sub-linear in `p`), in which case a
straight-line chord between two endpoints **underestimates** cost at every
interior prime, even while remaining monotonically increasing and passing
the STOP check cleanly. This is not a hypothetical concern for this specific
instrument: the search terminates on the *first* collision found, and
Theorem 1.5's own ceiling `(p/2)^{1/3}` is itself concave in `p` (10.68 at
p=2437 vs. 22.10 at p=21601, a much smaller ratio than `p` itself, 8.9×) —
so if search-termination cost tracks anything like the true minimal-degree
ceiling (as `VAL-BATCH-004.md` §3.3's own three independent correction
models, all built from this same contract's data, already suggested), the
two true endpoints understate a linear model's fit and a linear chord
between them plausibly *underestimates* cost at every prime in between. This
is the opposite failure direction from v1's flat single-point model, which
was a genuine worst-case upper bound (using the most expensive, largest
prime's cost for everyone) precisely because of this same directionality —
v2's chord gives up that guarantee without saying so. **Not blocking on the
admission side** (the >=4-prime floor is independently validated using v1's
still-conservative flat estimate per check (b) above, with zero reliance on
the interpolation), **but blocking if any fix to PF-1 below sizes real
per-prime execution sub-budgets from `per_prime_cost_estimate_v2`'s
(possibly underestimated) values without a stated margin.**

## (d) `coverage_widening_note` specification precision

Underspecified in a way that invites exactly the mid-run improvisation this
campaign's invalidation-rules discipline exists to prevent. The note permits
the Executor to *"additionally attempt the NEXT ascending prime beyond the
cumulative-prefix cutoff"* (singular) but then separately cites the WORKED
CHECK's "6 primes within the full 7200s" figure as the reason "ample
headroom is expected." **These two statements are in tension and the text
never resolves it**: does "the next ascending prime" mean exactly one
additional prime (5th, i.e. 8893) may be attempted once, or does it license
an *iterative* widening (attempt the 5th; if budget remains, attempt the
6th; ...) up to whatever the actually-remaining wall clock allows? Nothing
in the note states a loop-termination condition, a maximum count, or whether
"remaining budget" is checked against the admitted prefix's *estimated* cost
or its *actual measured* cost from the just-completed real search. Given
this note explicitly authorizes the Executor to spend real compute based on
a judgment call ("MAY additionally attempt"), the amendment's own
non-improvisation standard (GD-4's discipline, reaffirmed by GD-7: *"cannot
be tuned after seeing which primes are convenient"*) requires this to be a
mechanical, pre-registered rule, not an option left to Executor discretion
mid-run. **Required before freeze**: state explicitly whether widening is a
single one-off attempt or an iterative process, and if iterative, the exact
stopping condition (e.g. "continue admitting the next ascending prime,
one at a time, as long as [X] holds, with no other stopping criterion").

## (e) Provenance / version-control precision of the code reuse

**This is where check (f)'s search for "a frozen element nobody
stress-tested" actually lands, and it is severe.** `required_artifacts_note`
states: *"implementation/compute_delta_e.py is REUSED... with ONLY the
apply_truncation_fallback function replaced... (and the smoke-test driver
extended to run at both endpoints)... every other function... is REUSED
UNCHANGED."* This claim is **checkable against the actual v1 code and does
not hold.** Reading `compute_delta_e.py` directly:

```
# compute_delta_e.py, lines 111-112
WALL_CLOCK_BUDGET_SECONDS = 7200
T_PRIME = 0.5 * WALL_CLOCK_BUDGET_SECONDS / len(PRIMES)   # 300.0s, PF-1 fix
```

`T_PRIME` (300s) is used in **two structurally independent places**:

1. `apply_truncation_fallback` (lines 331-361) — the ADMISSION check this
   amendment correctly replaces.
2. `run_phase_minus1_on_confirmatory_set` (lines 368-419), called from
   `main()` at line 717-718 as
   `run_phase_minus1_on_confirmatory_set(graphs, truncation["confirmatory_prime_set"], SEEDS, T_PRIME)`
   — a **completely separate mechanism**: once a prime is admitted, this
   function caps the *actual real-time search* for that prime's entire
   non-F_p-rational vertex set at `t_prime` seconds (line 391-393:
   `if remaining <= 0: break`), stopping the search early and reporting
   whatever fraction of vertices got resolved in that window as
   `m_coverage_non_fp_fraction`. `main()`'s own log line states this
   explicitly: *"Running REAL delta_E search on the %d confirmatory
   prime(s) (each capped at its own T_prime=%.1fs sub-budget)."*

The amendment's `scope_reduction_fallback_v2` fixes mechanism (1). Nothing in
the draft — not the amendment text, not `required_artifacts_note`, not
`coverage_widening_note` — mentions, touches, or even acknowledges mechanism
(2). `required_artifacts_note`'s claim that "every other function... is
REUSED UNCHANGED" is therefore **not an accurate specification of what a
correct implementation of this amendment's own stated purpose requires** —
it under-names the diff by at least one more function/call-site
(`run_phase_minus1_on_confirmatory_set`'s `t_prime` argument, or its call
site in `main()`). This is not a hypothetical ambiguity risk the way (d) is;
it is a **concrete, quantifiable, code-verified defect**, worked out fully in
PF-1 below.

(A smaller, secondary imprecision in the same note: `run_feasibility_smoke_test`
(lines 294-330) already takes an arbitrary prime argument and computes a
prime-agnostic theoretical ceiling — calling it a second time at `PRIMES[0]`
plausibly requires **no change to the function itself**, only an additional
call site in `main()`. "The smoke-test driver extended" overstates what's
needed there. Minor on its own, but the same pattern of imprecision that
hides the much larger PF-1 gap.)

## (f) Other defects found

Covered as PF-1 (the headline finding), PF-4 (STOP-condition label gap), and
the scope-creep question below.

**Is the amendment's own "one change plus one small optional change" framing
accurate?** Not quite, once PF-1 is accounted for: making the amendment's
*stated intent* (actually execute Phase -1 on the cumulatively-admitted
prefix and obtain real M-COVERAGE) achievable requires a **third** change —
correcting or removing the mismatched real-execution sub-budget — that the
draft does not currently name as in scope at all. This does not rise to "the
mechanism needs a redesign" (the delta_E instrument, the decision-rule
ordering, every control, and the admission-side formula are all sound and
correctly scoped); it is a **specification completeness gap in an amendment
that believes it is smaller than it actually needs to be to work**. That is
squarely within a pre-freeze reviewer's job and does not require broadening
this into a fuller review — it requires one more paragraph in the same
amendment.

---

## Findings

### PF-1 — [BLOCKING] The real per-prime execution cap is a second, unaddressed instance of GD-7's exact defective formula, and will likely still fail the Phase -1 gate

**Quantified from numbers already on disk plus the code's own logged
behavior, zero new compute:**

`run_phase_minus1_on_confirmatory_set` caps each admitted prime's ENTIRE
non-F_p-rational vertex search at `T_PRIME = 300s` wall-clock,
**independent of whether 1, 4, or 12 primes are in the confirmatory set,**
and independent of `scope_reduction_fallback_v2`'s own `T_reserved=3600s`.
Using the smoke test's own measured per-vertex cost (1.9574s/vertex,
`raw-result.json.feasibility_smoke_test.avg_wall_seconds_per_vertex`), at
most `floor(300 / 1.9574) ≈ 153` vertices can be resolved per admitted
prime within its unchanged sub-budget. Using the disclosed A-1 informal
smaller-prime figure (1.43s/vertex) instead, at most `floor(300/1.43) ≈ 209`.
Applied to the 4 primes this amendment's own check (b) admits:

| prime | non-F_p vertices | max resolvable @1.9574s/v | coverage | max resolvable @1.43s/v (optimistic) | coverage |
|---|---|---|---|---|---|
| 2437 | 194 | 153 | 78.9% (pass) | 209 (capped at 194) | 100% (pass) |
| 3889 | 306 | 153 | 50.0% (borderline) | 209 | 68.6% (pass) |
| 5737 | 460 | 153 | 33.3% (**fail**) | 209 | 45.6% (**fail**) |
| 7333 | 594 | 153 | 25.8% (**fail**) | 209 | 35.3% (**fail**) |

Under either the measured or the most optimistic disclosed cost figure, **at
most 2 of the 4 admitted primes clear `M-COVERAGE >= 0.5`** — and the
code's own terminal gate check (`main()`, lines 743-746:
`n_primes_coverage_pass = sum(1 for p, r in phase_minus1_results.items() if
r["m_coverage_non_fp_fraction"] >= 0.5); phase_minus1_gate_pass =
n_primes_coverage_pass >= 4`) requires **>=4 primes to actually clear
coverage post-search**, not merely to be admitted into the confirmatory set.
The amendment's admission-side fix is real and correct (checks (a), (b)
above), but it feeds into an execution-side mechanism that was never updated
to match it. **The most likely outcome of dispatching this draft as written
is that the run still returns `DATA-UNAVAILABLE-BLOCKED`** — not because the
cumulative-prefix admission logic failed (it will have correctly admitted 4
primes), but because a *second*, textually invisible instance of the exact
formula GD-7 named defective (`T_PRIME = 0.5×7200/12`) silently truncates
each admitted prime's real search before it can resolve enough vertices —
while this time consuming real compute (an estimated `4 × 300s ≈ 1200s`,
not the `90.57s` BATCH-004 spent) to arrive at what could again read as
"genuine infeasibility," exactly the misreading `RT-BATCH-004.md` warned
against for a different mechanism.

**This is the same shape as GD-4 through GD-7, one further layer down**: the
pre-freeze process (this review) was explicitly directed to scrutinize the
admission-side formula because that is the formula everyone already knew to
distrust; the sibling formula living in a function `required_artifacts_note`
asserted was untouched went unexamined by the same discipline that caught
GD-7 itself.

**Fix, concrete, does not redesign the amendment:** specify, in the
amendment text (not left to Executor discretion), how each admitted prime's
real per-prime execution sub-budget is computed. Two options, either
sufficient: (i) give admitted prime `p_i` a real sub-budget at least equal
to its own `per_prime_cost_estimate_v2` value, with the *sum* of sub-budgets
bounded by `T_reserved` (this is the natural reading of "the budget check is
against the prefix's TOTAL cost" applied consistently to execution, not only
admission); or (ii) remove the per-prime real-time cap entirely for admitted
primes and instead cap the *aggregate* real Phase -1 wall clock at
`T_reserved`, stopping the whole phase (not each prime individually) once
that aggregate is exhausted, with any partially-searched prime's partial
`M-COVERAGE` reported honestly. Either requires updating
`run_phase_minus1_on_confirmatory_set`'s call site (or its default
argument) — `required_artifacts_note` must name this function/call site as
also changing, not just `apply_truncation_fallback` and the smoke-test
driver.

### PF-2 — [BLOCKING] `coverage_widening_note`'s widening rule is underspecified (see check (d) above)

State explicitly whether post-cutoff widening is a single next-prime attempt
or an iterative process, and if iterative, the exact, mechanical stopping
condition. As written, an Executor has discretion over how much additional
real compute to spend and on how many primes, which is exactly the kind of
mid-run judgment call this campaign's non-improvisation standard exists to
foreclose.

### PF-3 — [BLOCKING] Linear interpolation's failure mode is only partly covered by the STOP condition (see check (c) above)

The `c_max < c_min` STOP condition catches gross non-monotonicity but not
the more plausible failure mode of a concave true cost-vs-`p` relationship,
under which a linear chord *underestimates* intermediate-prime costs even
while remaining monotonic. Not blocking for the admission-side >=4-prime
floor (independently validated in check (b) using v1's conservative flat
estimate, with zero reliance on interpolation) — **but blocking if PF-1's
fix ties real per-prime execution sub-budgets to
`per_prime_cost_estimate_v2` values**, since an underestimate there would
recreate PF-1's coverage-shortfall risk through the accuracy improvement
meant to help. Recommend either a documented safety margin (e.g.
`sub_budget(p) = 1.5 × interpolated_estimate(p)`) wherever the interpolated
model is used to gate real execution time, or restricting the interpolated
model to reporting/diagnostics only and keeping any execution-time
allocation tied to the (conservative) flat single-point figure.

### PF-4 — [BLOCKING] The new STOP condition does not name which outcome-scope label applies

`invalidation_rules_v2_additions`' non-monotonicity STOP condition says
"STOP and report per per_prime_cost_estimate_v2" but never names which of
the four labels in `outcome_scope_label_glossary`
(`CONTROL-FAILURE-VOID` / `DATA-UNAVAILABLE/BLOCKED` / the two per-prime
labels) the resulting outcome carries. This is exactly the ambiguity GD-6's
standing repair (and `VAL-BATCH-003.md` finding 7) was adopted to close at
the run level, and PF-4 finds it reopened, undocumented, at this new branch.
Most natural mapping is `DATA-UNAVAILABLE/BLOCKED` (no confirmatory set can
even be computed), but the amendment must say so rather than leave an
Executor to infer it.

### PF-5 — [ADVISORY, not blocking] `required_artifacts_note`'s function-diff description is imprecise beyond PF-1's specific gap

`run_feasibility_smoke_test` already takes an arbitrary prime argument and a
prime-agnostic ceiling formula; running it a second time at `PRIMES[0]`
plausibly needs no change to the function itself, only an added call site in
`main()` — "the smoke-test driver extended" overstates what changes there.
Separately, whether the new two-point interpolation logic
(`per_prime_cost_estimate_v2`) lives inside a rewritten
`apply_truncation_fallback` or a new helper function is unspecified.
Recommend the amendment (or its dispatch instructions to the Executor)
include an explicit, code-verified function-level diff list before
implementation begins, the same standard this review applied to check the
draft's own claim.

---

## Required controls / checks for BATCH-005 dispatch

- A stated, mechanical rule for each admitted prime's real Phase -1
  execution sub-budget (PF-1), verified before dispatch to actually admit
  enough real search time for at least 4 primes to plausibly clear
  `M-COVERAGE >= 0.5`, using the same conservative arithmetic this review
  used (worst case: the measured 1.9574s/vertex figure, not an
  as-yet-unmeasured, possibly-optimistic interpolated one).
- A mechanical, pre-registered stopping rule for `coverage_widening_note`
  (PF-2).
- A documented margin, or a restriction to non-execution-gating use, for
  `per_prime_cost_estimate_v2`'s linear interpolation wherever it feeds a
  real time allocation (PF-3).
- An explicit outcome-scope label for the non-monotonicity STOP condition
  (PF-4).
- A code-verified (not merely asserted) function-level diff list against v1's
  `compute_delta_e.py` before the Executor begins implementation (PF-5).

## Counterexample or mutation

The cheapest discriminating check for PF-1 is exactly the one performed
above: read `run_phase_minus1_on_confirmatory_set`'s call site in `main()`
(`compute_delta_e.py` line 717-718) and observe it still passes the module
constant `T_PRIME` (300s) as the per-prime real-execution sub-budget,
unconditional on how many primes the corrected admission rule selects.
Combined with the smoke test's own already-measured 1.9574s/vertex cost and
the already-committed per-prime non-F_p-rational vertex counts (both in
`raw-result.json`), this shows at most ~2 of the 4 admitted primes can clear
`M-COVERAGE >= 0.5` under the current code — a direct falsifier of "the
cumulative-prefix fix alone unblocks Phase -1," using zero new compute and
zero re-measurement, exactly the standard GD-4/GD-7 established.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this
remains a toy-scale, gradient-existence screen with `asymptotic_claim: null`
throughout (`H-SSIQ-137200.asymptotic_claim_note`), correctly inherited
unchanged. The relevant baseline is this campaign's own instrument- and
fix-scrutiny discipline (GD-4 through GD-7): this amendment correctly
diagnoses and fixes the ADMISSION-side instance of the defect the prior
batch named, and does so with independently-reproducible arithmetic (checks
(a), (b) above pass cleanly) — but it repeats GD-4/GD-7's exact failure
pattern one function further away: a sibling instance of the same numeric
constant, used for a structurally different purpose, was not itself
stress-tested before this draft was presented for freeze.

## Heuristic challenges

`H-SSIQ-137200.heuristic_assumptions` correctly remains empty (gradient-
existence screen, not a heuristic-conditional complexity claim) — attacked
and held, consistent with every prior review in this lineage. No numbered
heuristic requiring a random-model justification is implicated by any
finding in this review; every finding here is a budget-allocation /
specification-precision defect, not a claim about the underlying arithmetic
object.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly), so the per-attempt-cost × inverse-success-probability review
does not apply in the complexity-claim sense. What does apply, and is the
substance of PF-1, is ordinary resource bookkeeping carried inconsistently
across two mechanisms in the same reused code: the admission-side budget
model is now internally consistent (`T_reserved=3600s`, cumulative), but the
execution-side model was left at its old, GD-7-defective value
(`T_PRIME=300s`, an individual 1/12 share), and nothing in the draft
reconciles the two. A corrected amendment must state one consistent budget
model that governs both which primes are admitted and how much real time
each admitted prime actually gets.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis. `H-SSIQ-137200.scope_ceiling`
(toy, inherited from H-SSIQ-9e2c71) is correctly stated and not exceeded by
anything in the draft's design. No scope-inflation concern found in the
amendment's *content*; the concern found (PF-1/PF-5) is that its own
described scope ("ONLY apply_truncation_fallback... replaced") is narrower
than what its stated purpose actually requires, which is a completeness gap,
not scope creep.

## Proof architecture challenges

`proof_search_map.not_applicable_reason` remains correctly reasoned and
inherited unchanged — this is a direct instrument-level gradient-existence
screen, not a proof-oriented proposal, and nothing in this amendment converts
it into one. Attacked and held, same verdict as every prior review in this
lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v2.yaml` as read at
draft status: the amendment correctly diagnoses and fixes GD-7's
admission-side defect (the cumulative-prefix reading is unambiguous in the
text and its own worked arithmetic is independently reproducible to the
digit from already-committed BATCH-004 numbers, checks (a) and (b) above).
It should not be frozen as currently written: a second, textually
unacknowledged instance of the identical defective formula
(`T_PRIME=0.5×7200/12=300s`) governs the real per-prime execution time once
a prime is admitted, independent of and inconsistent with the corrected
admission-side budget, and — quantified from already-committed numbers —
will most likely still prevent >=4 primes from clearing `M-COVERAGE >= 0.5`
in real execution, reproducing `DATA-UNAVAILABLE-BLOCKED` under an
unaddressed mechanism while consuming real compute this time. Three further
specification gaps (the widening rule's stopping condition, the
interpolation model's unchecked concavity risk where it could feed real time
allocation, and the new STOP condition's missing outcome label) must also be
closed before dispatch. None of these require redesigning the amendment's
mechanism, which is otherwise sound and correctly targets the same,
already-validated delta_E instrument.

## Next concrete action

Coordinator: before moving this draft to `status: approved` / setting
`frozen_at`, require the amendment text (not the Executor, at run time) to
state (1) the real per-prime execution sub-budget rule for admitted primes,
consistent with the corrected admission-side cumulative budget, updating
`required_artifacts_note` to name `run_phase_minus1_on_confirmatory_set`'s
call site as also changing (PF-1, the blocking finding); (2) a mechanical
stopping condition for `coverage_widening_note`'s post-cutoff widening
(PF-2); (3) a documented margin or a non-execution-gating restriction on
`per_prime_cost_estimate_v2`'s linear interpolation (PF-3); (4) the outcome
label for the non-monotonicity STOP condition (PF-4). PF-5 is advisory and
can be closed with a one-line diff-list addition. None require redesigning
the experiment's mechanism, which is otherwise sound.

## Overall verdict

**FREEZE-WITH-FIXES.** Blocking, in priority order:

1. **[BLOCKING]** PF-1 — reconcile the real per-prime execution sub-budget
   with the corrected cumulative admission budget; name the changed
   call site/function explicitly.
2. **[BLOCKING]** PF-2 — mechanical stopping condition for
   `coverage_widening_note`.
3. **[BLOCKING]** PF-3 — margin or scope restriction on the linear
   interpolation wherever it could gate real execution time.
4. **[BLOCKING]** PF-4 — name the outcome-scope label for the
   non-monotonicity STOP condition.

PF-5 is advisory and can be folded into the fix for PF-1's
`required_artifacts_note` correction.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v2
  task_id: NOT SUPPLIED IN THE LAUNCHING HANDOFF; recorded as unsupplied rather than fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v2.yaml (status: draft,
    hypothesis_id H-SSIQ-137200): a versioned amendment to the frozen v1
    contract (specification.yaml, frozen 96ad45de) that replaces
    scope_reduction_fallback_pinned_before_data's individual per-prime budget
    cap with a cumulative-ascending-prefix check (GD-7's fix), plus an
    optional two-point (smallest+largest prime) smoke test / linear
    interpolation refinement, plus a disclosed, bounded post-hoc coverage
    -widening allowance.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: compute_delta_e.py contains a second, independent instance of GD-7's exact defective formula (T_PRIME = 0.5*7200/12 = 300s), used not for admission (which this amendment correctly fixes) but as a hard per-prime real-execution wall-clock cap inside run_phase_minus1_on_confirmatory_set, called from main() with T_PRIME unchanged. required_artifacts_note's claim that only apply_truncation_fallback and the smoke-test driver change is checked against the code and does not hold. Quantified from already-committed raw-result.json numbers (1.9574s/vertex measured cost, or 1.43s/vertex disclosed-optimistic): at most 2 of the 4 admitted primes (2437, 3889, 5737, 7333) can clear M-COVERAGE>=0.5 within the unchanged 300s per-prime real cap, so the code's own terminal gate (n_primes_coverage_pass >= 4) will most likely still fail, reproducing DATA-UNAVAILABLE-BLOCKED under an unaddressed mechanism while consuming real compute this time."
    - "OBJ-2 [PF-2, BLOCKING]: coverage_widening_note permits attempting 'the NEXT ascending prime' (singular) while also citing a 6-primes-within-7200s figure as headroom, without stating whether widening is a single attempt or an iterative process, or any mechanical stopping condition -- leaves a real, budget-consuming judgment call to the Executor mid-run, contrary to this campaign's non-improvisation standard."
    - "OBJ-3 [PF-3, BLOCKING]: per_prime_cost_estimate_v2's two-point linear interpolation is checked only for gross non-monotonicity (c_max < c_min), not for the more plausible failure mode of a concave true cost-vs-p relationship (physically motivated by the search's first-collision termination and Theorem 1.5's own concave (p/2)^(1/3) ceiling), under which a linear chord underestimates intermediate-prime cost while remaining monotonic and passing the stated check. Not blocking for the admission-side >=4-prime floor (independently re-verified using v1's conservative flat estimate, check (b)), but blocking if any fix to OBJ-1 ties real execution sub-budgets to this interpolated, possibly-underestimated model without a stated margin."
    - "OBJ-4 [PF-4, BLOCKING]: the new non-monotonicity STOP condition (invalidation_rules_v2_additions) does not name which of the four outcome_scope_label_glossary labels applies to the resulting outcome, reopening exactly the ambiguity GD-6's standing repair and VAL-BATCH-003 finding 7 closed at the run level."
    - "OBJ-5 [PF-5, ADVISORY]: required_artifacts_note additionally overstates what changes in run_feasibility_smoke_test (already prime-agnostic; likely needs only an added call site, not a function change) and leaves unspecified whether the interpolation logic lives inside a rewritten apply_truncation_fallback or a new helper -- recommend an explicit, code-verified function-level diff list before implementation."
  required_controls:
    - "A stated, mechanical rule reconciling each admitted prime's real Phase -1 execution sub-budget with the corrected cumulative admission budget (T_reserved=3600s), with the changed function/call-site named explicitly in required_artifacts_note (PF-1)."
    - "A mechanical, pre-registered stopping condition for coverage_widening_note's post-cutoff widening (PF-2)."
    - "A documented safety margin, or a restriction to non-execution-gating (reporting-only) use, for per_prime_cost_estimate_v2's linear interpolation wherever it could feed a real time allocation (PF-3)."
    - "An explicit outcome-scope label named for the non-monotonicity STOP condition (PF-4)."
  counterexample_or_mutation: >-
    Read run_phase_minus1_on_confirmatory_set's call site in main()
    (compute_delta_e.py line ~717-718): it still passes the module constant
    T_PRIME (300s) as each admitted prime's real-execution sub-budget,
    unconditional on the corrected admission rule's prime count. Combined
    with raw-result.json's already-measured 1.9574s/vertex cost and
    already-committed per-prime non-F_p-rational vertex counts (194, 306,
    460, 594 for the 4 admitted primes), at most ~2 of 4 can clear
    M-COVERAGE>=0.5 within that unchanged cap -- a direct falsifier of "the
    cumulative-prefix admission fix alone unblocks Phase -1," using zero new
    compute and zero re-measurement.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-7): this
    amendment correctly diagnoses and fixes the admission-side instance of
    the prior batch's defect, with independently-reproducible arithmetic, but
    repeats the identical failure pattern one function further away -- a
    sibling instance of the same numeric constant, serving a different
    purpose, went unexamined.
  heuristic_challenges:
    - "H-SSIQ-137200.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. Every finding in this review is a budget-allocation / specification-precision defect, not a claim about the underlying arithmetic object."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply in the complexity-claim sense."
    - "Ordinary resource bookkeeping is the live issue: the admission-side budget model is now internally consistent (T_reserved=3600s cumulative) but the execution-side per-prime cap was left at the old GD-7-defective value (T_PRIME=300s individual share), and nothing in the draft reconciles the two (PF-1)."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; no scope widening found in content."
    - "H-SSIQ-137200.scope_ceiling (toy, inherited from H-SSIQ-9e2c71) correctly stated and not exceeded."
    - "The amendment's own described scope ('ONLY apply_truncation_fallback... replaced') is narrower than what its stated purpose actually requires (PF-1, PF-5) -- a completeness gap in the specification, not scope creep in the mechanism."
  proof_architecture_challenges:
    - "proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal; nothing in this amendment converts it into one. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v2.yaml as read at
    draft status: the amendment correctly diagnoses and fixes GD-7's
    admission-side defect (checks (a) and (b) both pass, independently
    reproduced to the digit from already-committed numbers). It should NOT be
    frozen as currently written: a second, textually unacknowledged instance
    of the identical defective formula governs real per-prime execution time
    once a prime is admitted, and -- quantified from already-committed
    numbers, zero new compute -- will most likely still prevent >=4 primes
    from clearing M-COVERAGE>=0.5 in real execution, reproducing
    DATA-UNAVAILABLE-BLOCKED under an unaddressed mechanism while consuming
    real compute this time. Three further specification gaps (widening
    stopping condition, interpolation concavity risk where execution-gating,
    missing STOP-condition label) must also close before dispatch. None
    require redesigning the amendment's mechanism.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text itself (not Executor discretion at run time) to state (1) the real
    per-prime execution sub-budget rule for admitted primes, consistent with
    the corrected cumulative admission budget, naming
    run_phase_minus1_on_confirmatory_set's call site as also changing in
    required_artifacts_note (PF-1, blocking); (2) a mechanical stopping
    condition for coverage_widening_note (PF-2, blocking); (3) a documented
    margin or non-execution-gating restriction on the linear interpolation
    (PF-3, blocking); (4) the outcome label for the non-monotonicity STOP
    condition (PF-4, blocking). PF-5 folds into PF-1's required diff-list
    correction.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic only, entirely on numbers already committed in
    experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a/raw-result.json
    (cumulative summation of truncation_fallback.per_prime_estimate;
    coverage-fraction arithmetic from avg_wall_seconds_per_vertex and
    non_fp_rational_counts_by_prime) plus reading (not executing)
    experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py to verify
    the draft's required_artifacts_note claim against the actual v1 code. No
    code executed, no graph built, no search run, no new measurement taken.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v2.yaml itself)
    and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
