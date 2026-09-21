# RT-PREFREEZE-EXP-SSIQ-a85692-v4 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v4.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-007

**Reviews `experiments/EXP-SSIQ-a85692/specification_v4.yaml` at `status: draft`
(this task's working-tree read; the amendment is not yet snapshot-committed by
the Coordinator, and this report changes nothing under
`experiments/EXP-SSIQ-a85692/` — including the already-frozen `specification_v3.yaml`
at commit `7f40426b` — or any ledger record; those remain the Coordinator's
alone to touch.** `specification_v4.yaml` was read in full, not sampled, and
so was `specification_v3.yaml` (363 lines, frozen `7f40426b`), as the diff
base. Read in full per the launching task: `coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/RT-BATCH-006.md`
(the report that found GD-10) and `VAL-BATCH-006.md` (the independent
confirmation that the *arithmetic* of v3's dead-end self-test was correct —
the defect was never the arithmetic, only which function it exercised);
`experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py` in full, with
`c_null_label_comparison_v3` (lines 141–216, UNCHANGED by this amendment —
this is the exact code this review traces mutations against) and the
now-superseded `run_synthetic_self_test_v3` (lines 223–356) read line by
line; `experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json`,
specifically `descent_metrics.per_prime` and `c_null_label.per_prime`, to
verify the no-`N`-in-null-arm schema claim directly rather than take it on
the draft's word; `experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py`'s
`ols_loglog_fit` (lines 104–134) and `bootstrap_gap_ci` (lines 362–384) read
in full, needed for check (d) and PF-2 below, which requires tracing the
*actual arithmetic* of a resampling function, not merely trusting the
draft's own worked-check framing; `ledger/goals/GOAL-SSIQ-001/goal.yaml`'s
GD-9 and GD-10 entries and `next_action` (goal is sharded:
`ledger/goals/GOAL-SSIQ-001/goal.yaml` plus `checkpoints/BATCH-*.yaml`, per
CLAUDE.md's sharding convention); `ledger/evidence/EV-SSIQ-028c9f.yaml`,
`ledger/decisions/DEC-20260805-e46f4f.yaml`, `ledger/hypotheses/H-SSIQ-36e970.yaml`.
`RT-PREFREEZE-EXP-SSIQ-a85692-v3.md` read in full as the structural template
this report follows, per the launching task's instruction.

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
    unprobeable (VAL/RT-BATCH-003 through 006, RT-PREFREEZE-EXP-SSIQ-a85692[-v2,-v3]),
    so this is recorded as the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    shares a model family with every producer and every prior reviewer in this
    lineage; it is not corroboration from a distinct model and does not
    upgrade the campaign's evidence tier by itself, and it does not itself
    satisfy or advance a closure quorum.
```

---

## Bottom line up front

Checks (a), (c), (d) [in the corrected form derived below], and (e) all pass,
several with a materially more useful conclusion than the draft's own text
anticipates. **But item (b) — the mutation-precondition itself, the single
most important new requirement this amendment adds — fails for one of its
own three named example mutations.** Hand-tracing the actual, unchanged
`c_null_label_comparison_v3` code (`reanalyze_v3.py` lines 160–178) against
`synthetic_self_test_v4`'s specified inputs shows that an off-by-one mutation
of the `min_primes` gate (the draft's own worked example: "requiring `>3`
instead of `>=3`") produces **byte-identical output** from both CHECK 1
(`null_survivors` length 2) and CHECK 2 (length 4), because neither check
constructs a case at the boundary — length exactly `NULL_ARM_MIN_PRIMES=3`,
the one value that distinguishes `< 3` from `<= 3`. This is not a hypothetical
concern: it is the literal, named worked example in `mutation_precondition_v4`'s
own text, traced for real per the launching task's instruction, and it fails.

Separately (check (d), item PF-2 below), tracing `bootstrap_gap_ci` and
`ols_loglog_fit`'s actual arithmetic against CHECK 2's exact-power-law,
zero-noise construction shows that the missing-`sorted()` mutation — the
draft's other named example — is **not** caught by any of the four numeric
checks (ii)–(iv); its entire detection depends on check (i) alone (the
assertion that the returned `N_list` is ascending). This is not a defect —
check (i) as specified does catch it — but the draft's framing of four
roughly-parallel assertions obscures that one of them is doing all the work
for this mutation class, which is worth stating explicitly before freeze so a
future edit does not treat check (i) as redundant.

Neither finding requires redesigning the amendment's mechanism. Both are
fixable with a small, cheap addition (one more boundary-length synthetic
case) plus text-only clarification — zero new search cost, consistent with
the amendment's own budget.

---

## (a) Does the spec text genuinely call `c_null_label_comparison_v3` in both branches, precisely enough that an Executor could not reproduce GD-10's mistake?

**Yes, materially more precisely than v3's text ever was for its own
self-test, and precisely enough to close the specific gap GD-10 named.**

Traced against the actual, unchanged function (`reanalyze_v3.py` lines
141–216, whose signature is
`c_null_label_comparison_v3(real_per_prime, null_per_prime, null_survivors, rng_seed, min_primes=NULL_ARM_MIN_PRIMES, n_boot=2000)`
and whose return dict carries `evaluable`, `c_null_label_control_failure`,
`N_list`, `gamma_null_greedy`, `gamma_null_random`, `m_gap_null_ci_lo/hi`,
`primes_used`):

- **CHECK 1** calls `c_null_label_comparison_v3(real_per_prime, null_per_prime,
  null_survivors, rng_seed, ...)` directly and asserts on its **returned**
  `c_null_label_control_failure` and `evaluable` fields — the spec text is
  explicit: "via the function's own return value, not a hand-computed
  prediction of what it should return." This is the exact discipline GD-10's
  own repair requires and v3's `run_synthetic_self_test_v3` never applied.
- **CHECK 2** likewise calls the function directly with an unsorted
  `null_survivors`, and every one of its four assertions (i)–(iv) is phrased
  against "the returned" value — `N_list`, `gamma_null_greedy`/`gamma_null_random`,
  `m_gap_null_ci_lo/hi`, `c_null_label_control_failure` — all of which are
  literal keys in the function's own existing return dict, so there is no
  ambiguity about what "the returned X" refers to once an Executor reads the
  already-existing function.
- The closing sentence — "BOTH CHECKS CALL `c_null_label_comparison_v3`
  DIRECTLY — no duplicate, hand-written re-implementation of its internal
  logic anywhere in the self-test code, per GD-10's standing repair" — states
  the constraint GD-10 exists to enforce as an explicit prohibition, not
  merely a design intention, materially stronger than anything in v3's prose.
- A design detail worth confirming (traced, not merely noted): CHECK 1's
  `null_per_prime`/`real_per_prime` are specified with `>=4` entries but
  `null_survivors` is a length-2 **subset** of those keys. This incidentally
  also guards against a plausible alternate bug — a mutant that gates on
  `len(null_per_prime)` (4, the dict) instead of `len(null_survivors)` (2,
  the argument) would incorrectly proceed past the `NOT-EVALUABLE` branch and
  fail CHECK 1's assertion. Good, if incidental, discriminating power.

**One residual ambiguity, not blocking but worth tightening (see PF-3
below):** the spec does not say whether `RUN-SSIQ-a85692-d`'s script entry
point is a new function/CLI mode that never touches `--run-b`, or a modified
`main()` that still requires and reads `RUN-SSIQ-a85692-b/raw-result.json`
(as the current, unchanged `main()` unconditionally does at line 388) while
simply not acting on it. The draft's prose ("does NOT re-analyze
`RUN-SSIQ-a85692-b`'s real data again... does not read
`RUN-SSIQ-a85692-b`'s raw-result.json") is a factual claim about the
*artifact*, but `required_artifacts_note` never states the mechanism that
makes it true, unlike v3's precedent where the module docstring's own diff
list named every function/call-site precisely. This is a specification gap
of the same *class* PF-2 in `RT-PREFREEZE-EXP-SSIQ-a85692-v3.md` treated as
blocking (a diff list accurate as far as it goes, but silent on an
implementation detail the amendment's own claim depends on) — but unlike
that PF-2, nothing here is foreseeably reachable in a way that could produce
a wrong *result*; at worst an Executor keeps `--run-b` required and reads the
file without using it, which contradicts the "does not read" sentence
literally but changes no computed number. Rated advisory, not blocking; see
PF-3.

## (b) THE MUTATION PRECONDITION — traced for real, against the actual code

Per the launching task, I hand-constructed and traced three mutations of
`c_null_label_comparison_v3` (all three of the draft's own named examples)
against `synthetic_self_test_v4`'s specified inputs, using the actual,
unmodified function body (`reanalyze_v3.py` lines 141–216) as ground truth —
not executed, traced by hand per the spec's own instruction that this is a
review step applied to code precisely enough described to be traced without
running it.

### Mutation 1 — swap the `N` dict source (`real_per_prime` → `null_per_prime`)

Line 181: `N_list = [real_per_prime[p]["N"] for p in ordered]` →
`N_list = [null_per_prime[p]["N"] for p in ordered]`.

Both CHECK 1 and CHECK 2 construct `null_per_prime` dicts that **explicitly
omit** the `N` key (matching `c_null_label.per_prime`'s real schema, verified
directly below in check (c)). The first list-comprehension access,
`null_per_prime[p]["N"]`, therefore raises `KeyError` immediately, before any
return value exists. **CAUGHT** — a crash is observably different from the
draft's expected clean `PASS` verdict in both checks. (Not explicitly
addressed by the spec: whether the self-test harness is required to catch
this exception and record it as an explicit `FAIL` row, or whether an
uncaught exception terminating the run counts as "caught." Either behavior
distinguishes this mutant from correct code, so this does not block freeze,
but the spec should say which is expected so `execution_report.yaml`'s
format is not left to Executor discretion — a minor, non-blocking
precision gap, folded into PF-3.)

### Mutation 2 — off-by-one in `min_primes` (the draft's own named example: "requiring `>3` instead of `>=3`")

Line 160: `if len(null_survivors) < min_primes:` → `if len(null_survivors) <= min_primes:`
(with `min_primes=NULL_ARM_MIN_PRIMES=3` unchanged) — i.e., the mutant
requires strictly **more than 3** survivors (`>= 4`) to reach the
fit-and-bootstrap branch, instead of the correct `>= 3`.

Traced against **CHECK 1**'s `null_survivors` (length 2, per the spec text):
- Original: `2 < 3` → `True` → `NOT-EVALUABLE`.
- Mutant: `2 <= 3` → `True` → `NOT-EVALUABLE`.
- **Identical output. CHECK 1 does not distinguish.**

Traced against **CHECK 2**'s `null_survivors` (`[7000, 2000, 5000, 3000]`,
length 4, per the spec text):
- Original: `4 < 3` → `False` → proceeds to fit-and-bootstrap (the expected,
  substantive branch).
- Mutant: `4 <= 3` → `False` → proceeds to fit-and-bootstrap.
- **Identical output. CHECK 2 does not distinguish either.**

**Neither check constructs a `null_survivors` list of length exactly
`NULL_ARM_MIN_PRIMES = 3`, the one length at which `< 3` and `<= 3` disagree.**
This mutation therefore passes `synthetic_self_test_v4` as specified,
completely undetected, on both of its required checks. This is not a
contrived worst-case mutation — it is the literal example the draft's own
`mutation_precondition_v4` text names ("an off-by-one in `min_primes`, e.g.
requiring `>3` instead of `>=3`"). **NOT CAUGHT.**

This is a rigorous falsifier of the precondition's own implicit assumption:
the draft asks the reviewer to confirm "at least one" mutation changes
CHECK 2's outputs (a bar Mutations 1 and 3 both clear, so the *letter* of
`mutation_precondition_v4` is technically satisfiable), but the launching
task explicitly asks for "which mutation(s) you tried and whether each would
be caught" — and this campaign's own standing practice (`RT-BATCH-006.md`'s
verdict on v3: "clears the *letter*... but not the *substance*") is to treat
a named, plausible mutation that slips through as a real gap, not a
technicality to wave past because a different mutation happened to be
caught. See **PF-1**, blocking.

### Mutation 3 — remove the `sorted()` step (`ordered = sorted(null_survivors)` → `ordered = null_survivors`)

Traced against CHECK 2's construction (unsorted `[7000, 2000, 5000, 3000]`),
using `ols_loglog_fit` and `bootstrap_gap_ci`'s actual, transcribed
arithmetic (`descent_hitting_time.py` lines 104–134, 362–384):

- `ols_loglog_fit` computes `gamma = sxy/sxx`, a **sum over the point set**
  (lines 115–121) — order-invariant by construction. Reordering `ordered`
  reorders `N_list`, `greedy_medians`, and `random_medians`
  **consistently** (all three list comprehensions iterate over the same
  `ordered` list and index by prime key `p`), so the (N, median) pairing per
  point is unaffected by the mutation — only the *reported order* of the
  three output lists changes.
- Because CHECK 2 uses an **exact power law with zero noise** (deliberately,
  for hand-checkability — the same construction `VAL-BATCH-006.md` §4.1–4.2
  independently confirmed makes `gamma_fit = gamma_true` exactly for *any*
  subset of `>=2` distinct-N points), `gamma_null_greedy`, `gamma_null_random`,
  and `m_gap_null` are **identical** whether `ordered` is sorted or not.
- `bootstrap_gap_ci` (lines 368–378) draws `idx = [rng.randrange(n) for _ in
  range(n)]` — a sequence of **positional indices**, independent of list
  content — then resamples `Nb`/`gb`/`rb` at those indices. Reordering the
  input lists changes which *specific* points a given index sequence selects,
  but (i) the degenerate-resample test (`sxx==0`, i.e. all sampled points
  share one N) fires exactly when the drawn indices are all identical,
  regardless of what value that index maps to — so the **set of dropped
  resamples is identical** either way — and (ii) for every valid resample,
  the exact-power-law degeneracy above means the recovered gamma is the
  **same true value regardless of which points were drawn**. So
  `m_gap_null_ci_lo`, `m_gap_null_ci_hi`, `gaps`, and `n_boot_valid_draws`
  are **all bit-for-bit identical** between sorted and unsorted `ordered`,
  for this specific construction.
- **The only observable difference is the raw `N_list` (and `primes_used`)
  fields' reported order**: `[200, 300, 500, 700]` (sorted) vs. `[700, 200,
  500, 300]` (unsorted, mirroring the literal `[7000, 2000, 5000, 3000]`
  order). Check (i) — "the function's own internal sort produces the correct
  ascending `N_list`" — directly asserts this. **CAUGHT, but *only* by check
  (i)**, not by checks (ii)–(iv).

This is a materially sharper conclusion than the launching task's own item
(d) presupposes ("confirm... they'd differ in a way that changes the
computed gamma") — **the computed gamma does *not* change**, by the exact
mathematics of this specific test construction, and the mutation's entire
detectability rests on one assertion (check (i)) reading the raw `N_list`
field, not on any of the numeric fit/CI checks. See **PF-2**, advisory
(not blocking, since check (i) as specified does the job) but the spec
should say this explicitly so a future edit does not treat check (i) as
optional or redundant relative to (ii)–(iv).

### Summary of item (b)

| Mutation | Caught by CHECK 1? | Caught by CHECK 2? | Verdict |
|---|---|---|---|
| 1. Swap `N` source (real→null dict) | crashes (KeyError) | crashes (KeyError) | CAUGHT (via crash) |
| 2. Off-by-one `min_primes` (`<=` for `<`) | NO — identical output | NO — identical output | **NOT CAUGHT** |
| 3. Missing `sorted()` | n/a (early-return branch, `ordered` unused) | CAUGHT, but *only* via check (i)'s `N_list` assertion | CAUGHT (fragile) |

**The mutation precondition, applied honestly to all three of the draft's
own named examples, fails for one of them (Mutation 2) and succeeds
fragile-ly for another (Mutation 3).** This blocks freeze until fixed. The
fix is cheap: add one more synthetic case with `null_survivors` of length
**exactly `NULL_ARM_MIN_PRIMES = 3`** (the stated floor), asserting
`evaluable is True` (the fit-and-bootstrap branch fires *at* the floor, not
only strictly above it) — this single addition closes Mutation 2 and is
consistent in spirit and cost with the two checks already specified. See
**PF-1**.

## (c) Does `c_null_label.per_prime`'s real schema genuinely lack an `N` key?

**Yes, confirmed directly against `RUN-SSIQ-a85692-b/raw-result.json`,
independent of the draft's own claim.** `c_null_label.per_prime["2437"]` =
`{"greedy_median": 10.0, "greedy_trapped_fraction": 0.8078817733990148,
"random_median": 17.0}` — three keys, no `N`. Checked for all four
contributing primes (2437, 3889, 5737, 7333); the pattern holds for each.
By contrast `descent_metrics.per_prime["2437"]` carries `N: 203` alongside
`greedy_median`/`random_median`/`greedy_trapped_fraction`/`is_extension_prime`.
This independently reconfirms `RT-BATCH-006.md`'s own Objection 1 finding
(same schema check, same conclusion) on the same underlying file. **The
draft's claim that pulling `N` from `null_per_prime` in Mutation 1 forces a
`KeyError` is correct and independently reverified, not merely inherited.**

## (d) Does CHECK 2's unsorted-`null_survivors` design actually detect a missing/wrong `sorted()` step?

**Yes, but not for the reason the launching task's framing assumes — see the
full trace under Mutation 3 above.** The computed `gamma`/`m_gap`/CI values
are analytically **invariant** to the sort, by the same exact-power-law
degeneracy `VAL-BATCH-006.md` §4.1–4.2 already established; only the raw
`N_list`/`primes_used` output fields differ in reported order, and check (i)
is the sole mechanism that reads that difference. The example chosen
(`[7000, 2000, 5000, 3000]`) is **not** "accidentally identical" in the
numeric sense the task worried about — it is **necessarily** identical in
`gamma`/CI for *any* choice of unsorted order, given the deliberately
noiseless power-law construction the draft (correctly) uses for
hand-checkability. This is not a defect in the draft's design — check (i) as
specified does catch it — but the draft's own text should say plainly that
check (i) carries the entire discriminating burden for a missing-sort defect,
not present it as one of four roughly-equal, mutually-reinforcing assertions.
See PF-2.

## (e) Does this amendment silently touch, re-run, or restate `RUN-SSIQ-a85692-c`'s archived outcome?

**No.** `required_artifacts` names only `runs/RUN-SSIQ-a85692-d/*` (a new run
id); nothing in `required_artifacts`, `inputs.synthetic_self_test_v4`, or
`required_artifacts_note` references `RUN-SSIQ-a85692-c`'s `raw-result.json`,
`synthetic_self_test.json`, or `decision` fields, or re-invokes
`trapped_exclusion_filter_v3`/`c_null_label_comparison_v3` against real data.
`required_artifacts_note` states explicitly: "this amendment does not read
`RUN-SSIQ-a85692-b`'s raw-result.json, does not re-call
`trapped_exclusion_filter_v3` on real data, and does not touch
`RUN-SSIQ-a85692-c`'s already-archived outcome." Confirmed consistent with
`amendment_scope`'s own text and with the budget note ("no file I/O beyond
reading nothing... and writing the required artifacts"). **Pass, cleanly** —
modulo the entry-point-mechanism ambiguity noted in (a)/PF-3, which is about
*how* this is enforced in code, not *whether* the spec intends it.

## (f) Other issues found

### Required-artifacts-note diff-list precision

The note's claim — "`trapped_exclusion_filter_v3` is imported but this
amendment does not call it on any real data" — is accurate **given** the
(unstated, see PF-3) assumption that v4's implementation continues to edit
`reanalyze_v3.py` in place (keeping `trapped_exclusion_filter_v3` defined in
the same module, simply unused by the new self-test) rather than moving to a
wholly separate script. Under that assumption the sentence is correct: the
function stays defined, is never invoked by `run_synthetic_self_test_v4`,
and the synthetic `null_survivors` lists are hand-constructed directly, never
derived by running the filter. This is precise **as far as it goes**; PF-3
below is about the gap in what it does not state (the entry-point
mechanism), not an error in what it does state.

### Budget

`60s`/`0.02` CPU-hours for two function calls against `<=4`-point synthetic
dicts is generous by at least two further orders of magnitude beyond v3's
own already-generous `300s` (which itself completed in `0.035s` measured —
`VAL-BATCH-006.md` §11). No concern.

### "Zero new search cost" framing

Accurate. Nothing in `synthetic_self_test_v4` or `mutation_precondition_v4`
requires a graph, a `delta_map`, or any Phase −1 machinery; all inputs are
hand-constructed dict literals. Consistent with the amendment's own claim.

---

## Findings

### PF-1 — [BLOCKING] `mutation_precondition_v4`'s own named off-by-one example is not caught by `synthetic_self_test_v4` as specified

Traced directly against the actual, unchanged `c_null_label_comparison_v3`
(`reanalyze_v3.py` lines 160–178): mutating the `min_primes` gate from
`len(null_survivors) < min_primes` to `len(null_survivors) <= min_primes`
(the draft's own worked example, "requiring `>3` instead of `>=3`") produces
**identical output** from both CHECK 1 (`null_survivors` length 2: `NOT-EVALUABLE`
under both original and mutant) and CHECK 2 (`null_survivors` length 4:
evaluable under both). The one length that would distinguish the rules — 3,
the stated floor `NULL_ARM_MIN_PRIMES` — is never constructed by either
check. This directly falsifies the precondition's implicit premise for this
specific, named mutation, and per this campaign's own standing practice
(`RT-BATCH-006.md`: "clears the letter... but not the substance"), a
required control that passes on a technicality (a *different* named mutation
happens to be caught) while a named example silently slips through is the
exact failure shape GD-9→GD-10 exist to catch, one layer further in.

**Fix, concrete, zero new search cost:** add a third synthetic case (or
extend CHECK 1/2) with a `null_survivors` list of length **exactly
`NULL_ARM_MIN_PRIMES = 3`** — matching keys constructed the same way as
CHECK 2 (exact power laws so the expected `gamma`/`m_gap` are
hand-computable) — and assert `evaluable is True` (the fit-and-bootstrap
branch fires *at* the floor, not only strictly above it). This closes
Mutation 2 and gives the boundary its own explicit test, symmetric with how
CHECK 1 already tests the boundary from below (length 2, one below the
floor).

### PF-2 — [ADVISORY, not blocking] The missing-`sorted()` mutation's entire detectability rests on check (i) alone, not on checks (ii)–(iv), and the spec does not say so

Per the full trace under Mutation 3 above: `ols_loglog_fit`'s sum-based
`gamma` and `bootstrap_gap_ci`'s resampling are both invariant, for CHECK 2's
deliberately noiseless exact-power-law construction, to whether
`null_survivors` is sorted before use — every valid subset/resample recovers
the *same* true `gamma` regardless of point order. So `gamma_null_greedy`,
`gamma_null_random`, `m_gap_null_ci_lo/hi`, and `c_null_label_control_failure`
(checks (ii)–(iv)) would be **numerically identical** with or without the
`sorted()` call; only the raw `N_list`/`primes_used` output order differs,
which check (i) alone catches. This is not a defect — check (i) as specified
does the job — but the draft's presentation of (i)–(iv) as four
assertions invites a future reader (or a future amendment trimming
"redundant" checks) to treat them as interchangeable evidence for the same
class of bug, which they are not for this mutation. **Fix, text-only:** state
explicitly, next to check (i), that it is the load-bearing assertion for a
missing/incorrect `sorted()` defect specifically, given the exact-power-law
construction's order-invariance of the fit/CI outputs, and must not be
dropped or weakened independent of (ii)–(iv).

### PF-3 — [ADVISORY, not blocking] The entry-point mechanism for `RUN-SSIQ-a85692-d` is unstated, leaving `required_artifacts_note`'s "does not read `RUN-SSIQ-a85692-b`'s raw-result.json" claim structurally unenforced

The current, unchanged `main()` (`reanalyze_v3.py` lines 376–384) takes
`--run-b` as a **required** CLI argument and unconditionally opens and
`json.load`s it (line 388–389) before doing anything else.
`required_artifacts_note` asserts this amendment's run "does not read
`RUN-SSIQ-a85692-b`'s raw-result.json," but neither `amendment_scope` nor
`required_artifacts_note` states whether v4 introduces a new entry point
(a new function/CLI mode that never accepts `--run-b`) or modifies `main()`
to make the argument optional/unused for this dispatch — as against v3's own
precedent, whose diff list named every new/changed/imported function and
call site precisely enough to be checked by `grep`. This does not threaten
correctness of the self-test's numeric outputs (nothing in
`synthetic_self_test_v4` depends on `RUN-SSIQ-a85692-b`'s content either
way), but it leaves open a path where an Executor keeps `--run-b` required
and reads the file (satisfying the CLI, changing nothing computed) while
the artifact's own `required_artifacts_note` claims it was never read — a
factual mismatch of the same *shape*, though far lower stakes, as the
diff-list gaps `RT-PREFREEZE-EXP-SSIQ-a85692-v2.md` and `-v3.md` both rated
blocking. **Fix, text-only:** state explicitly whether `RUN-SSIQ-a85692-d`'s
script is invoked via a new function/mode that structurally cannot read
`--run-b`, or via a modified `main()` with a stated new flag, so
`source_access_log.yaml`'s "no real data read" claim (inherited pattern from
v3's own synthetic self-test, `VAL-BATCH-006.md` §4.3) is enforced by the
interface, not by Executor discretion.

---

## Required controls / checks before dispatch

- A third synthetic case in `synthetic_self_test_v4` with `null_survivors` of
  length exactly `NULL_ARM_MIN_PRIMES = 3`, asserting `evaluable is True`,
  closing the boundary gap that lets the draft's own named `min_primes`
  off-by-one mutation pass undetected (PF-1, **blocking**).
- Explicit text stating that check (i) (the `N_list`-ascending assertion) is
  the sole discriminator for a missing/incorrect `sorted()` defect, given
  the exact-power-law construction's invariance of `gamma`/CI to point order
  (PF-2, advisory).
- Explicit statement of the entry-point mechanism (new function/mode vs.
  modified `main()`) that makes `RUN-SSIQ-a85692-d` genuinely never read
  `RUN-SSIQ-a85692-b`'s raw-result.json, so `required_artifacts_note`'s claim
  is interface-enforced rather than Executor-discretionary (PF-3, advisory).

## Counterexample or mutation

The cheapest discriminating check for PF-1 is exactly the one performed
above at zero new compute: hand-trace `if len(null_survivors) < min_primes:`
vs. the mutant `if len(null_survivors) <= min_primes:` (`min_primes=3`
unchanged) against `null_survivors` of length 2 (CHECK 1: `NOT-EVALUABLE`
under both) and length 4 (CHECK 2: evaluable under both) — both checks
produce byte-identical verdicts under the original code and the mutant, a
direct falsifier of "the mutation precondition is satisfied by this draft's
design for all three of its own named example mutations." Concrete fix
already stated in PF-1: add a `null_survivors` length-3 case.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
gradient-existence screen, `asymptotic_claim: null` throughout, correctly
inherited unchanged. The relevant baseline is this campaign's own
instrument- and fix-scrutiny discipline (GD-4 through GD-10): this draft's
call-site precision (check (a)) is a genuine, material improvement over v3's
prose, and two of its three worked-example mutations are correctly caught.
What this review adds is the discipline GD-10's own standing repair calls
for applied recursively: verifying a validation artifact's discriminating
power is not itself validated by declaring "at least one mutation would be
caught" — it requires tracing every named candidate mutation, honestly, the
same way `RT-BATCH-006.md` traced the wrapper-bypass gap rather than
accepting that the self-test "ran" and reported `PASS`.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
numbered heuristic requiring a random-model justification is implicated by
any finding here; every finding is a control-validation discriminating-power
gap in new self-test code, not a claim about the underlying arithmetic
object.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly); the per-attempt-cost × inverse-success-probability review does
not apply. The `60s`/`0.02` CPU-hour budget is realistic and generously
oversized relative to two function calls on `<=4`-point synthetic data — no
resource-bookkeeping concern. The live concern remains evidentiary, not
resource cost: PF-1 means the amendment's validation artifact, as specified,
would not detect one of its own three named target-mutation classes, so a
future run's `c_null_label_control_failure` output, if it were ever produced
by a `min_primes`-off-by-one-mutated implementation, would be certified by
a self-test that cannot tell the difference.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis. `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) is correctly stated and not exceeded. No scope-inflation
found. This amendment correctly narrows its own scope to exactly one change
(`run_synthetic_self_test_v3` → `v4`) and correctly does not reopen
`RUN-SSIQ-a85692-c`'s archived `DATA-UNAVAILABLE-BLOCKED` outcome or the
deferred trapping-mechanism diagnostic (per (e) above) — both correctly
deferred to a later, separately-scoped amendment rather than folded in here.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level
gradient-existence screen, not a proof-oriented proposal. Attacked and held,
same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v4.yaml` as read at
draft status: the amendment's design correctly closes GD-10's core defect —
both of `synthetic_self_test_v4`'s checks genuinely call
`c_null_label_comparison_v3` and read its own return value, not a
hand-written duplicate of its logic (check (a)), and the synthetic
`null_per_prime` schema's omission of `N` is independently confirmed against
`RUN-SSIQ-a85692-b/raw-result.json` to force correct dict-source wiring
(check (c)); the amendment is correctly self-contained and does not touch
`RUN-SSIQ-a85692-c`'s archived outcome (check (e)). It should **not** be
frozen as currently written: `mutation_precondition_v4`'s own required
freeze precondition — that a hand-traced mutation of
`c_null_label_comparison_v3` would change the self-test's output — fails for
one of the draft's own three named example mutations (an off-by-one in
`min_primes`), because neither of the two specified checks constructs a
`null_survivors` list at the stated floor length of exactly 3 (PF-1,
blocking). Separately, the missing-`sorted()` mutation is caught only
through check (i) — not through the numeric fit/CI checks (ii)–(iv), which
are analytically invariant to point order for the deliberately noiseless
power-law construction this draft uses — and the spec should say so
explicitly rather than presenting four checks as roughly interchangeable
evidence (PF-2, advisory). The entry-point mechanism that is supposed to
make "does not read `RUN-SSIQ-a85692-b`'s raw-result.json" true is unstated
(PF-3, advisory). None of these findings require redesigning the
amendment's mechanism, which is otherwise a genuine, well-targeted fix for
GD-10.

## Next concrete action

Coordinator: before moving this draft to `status: approved` / setting
`frozen_at`, require the amendment text to add a third `synthetic_self_test_v4`
case with `null_survivors` of length exactly `NULL_ARM_MIN_PRIMES = 3`,
asserting `evaluable is True` (PF-1, blocking) — this is the single change
that makes the mutation precondition's own worked example pass. While
editing, also add (PF-2, advisory) an explicit note that check (i) alone
carries the discriminating power for a missing/incorrect `sorted()` defect,
and (PF-3, advisory) a one-line statement of the entry-point mechanism that
keeps `RUN-SSIQ-a85692-d` from reading `RUN-SSIQ-a85692-b`'s raw-result.json.
None of the three requires new search or touches `RUN-SSIQ-a85692-c`'s
archived outcome. Once fixed, re-verify PF-1's specific trace (length-3 case
now distinguishes the `min_primes` off-by-one) before freeze, per this
campaign's standing practice of tracing the fix, not merely trusting that
text was added.

## Overall verdict

**FREEZE-WITH-FIXES.** Blocking, in priority order:

1. **[BLOCKING]** PF-1 — `mutation_precondition_v4`'s own named `min_primes`
   off-by-one example is not caught by `synthetic_self_test_v4` as
   specified; add a `null_survivors` length-3 boundary case before freeze.

PF-2 and PF-3 are advisory (text-only clarifications, no design change) and
do not block this dispatch.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v4
  task_id: NOT SUPPLIED IN THE LAUNCHING HANDOFF; recorded as unsupplied rather than fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v4.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970): a versioned amendment to the frozen v3
    contract (specification_v3.yaml, frozen 7f40426b) that replaces v3's
    run_synthetic_self_test_v3 (found in BATCH-006/RT-BATCH-006.md, GD-10,
    to never call c_null_label_comparison_v3) with
    run_synthetic_self_test_v4, specified to call c_null_label_comparison_v3
    itself through both its NOT-EVALUABLE and fit-and-bootstrap branches,
    plus a new pre-freeze precondition (mutation_precondition_v4) requiring
    the reviewer to hand-trace at least one mutation of
    c_null_label_comparison_v3 against the self-test's specified inputs
    before freeze.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: mutation_precondition_v4's own named example mutation (an off-by-one in min_primes, 'requiring >3 instead of >=3') is NOT caught by synthetic_self_test_v4 as specified. Hand-traced against the actual, unchanged c_null_label_comparison_v3 (reanalyze_v3.py lines 160-178): mutating `len(null_survivors) < min_primes` to `len(null_survivors) <= min_primes` produces IDENTICAL output from CHECK 1 (null_survivors length 2: NOT-EVALUABLE under both original and mutant, since 2<3 and 2<=3 are both True) and from CHECK 2 (null_survivors length 4: evaluable under both, since 4<3 and 4<=3 are both False). Neither check constructs a null_survivors list of length exactly NULL_ARM_MIN_PRIMES=3, the one value that distinguishes the two rules. A required precondition that passes only because a DIFFERENT named mutation (dict-source swap) happens to be caught, while this specific named example silently slips through, is the same letter-vs-substance gap RT-BATCH-006.md found in v3's own self-test, recurring one layer further in."
    - "OBJ-2 [PF-2, ADVISORY]: the missing-sorted() mutation (the draft's other named example) is caught ONLY via check (i)'s N_list-ascending assertion, not via checks (ii)-(iv). Traced against ols_loglog_fit's sum-based gamma formula and bootstrap_gap_ci's index-based resampling (descent_hitting_time.py lines 104-134, 362-384): for CHECK 2's deliberately noiseless exact-power-law construction, gamma_null_greedy, gamma_null_random, m_gap_null, and m_gap_null_ci_lo/hi are analytically IDENTICAL whether null_survivors is sorted before use or not (every valid subset/resample of an exact power law recovers the true gamma exactly, the same degeneracy VAL-BATCH-006.md Section 4.2 already established for the CI). Only the raw N_list/primes_used output ORDER differs, which only check (i) reads. This is not a defect (check (i) as specified does catch it) but the spec presents (i)-(iv) as four roughly-equal assertions when only one carries weight for this mutation class, and should say so explicitly."
    - "OBJ-3 [PF-3, ADVISORY]: the entry-point mechanism for RUN-SSIQ-a85692-d is unstated. main() (reanalyze_v3.py lines 376-389, unchanged) currently requires --run-b and unconditionally reads RUN-SSIQ-a85692-b's raw-result.json before doing anything else, but required_artifacts_note asserts this amendment's run 'does not read' that file without stating whether v4 introduces a new entry point that structurally cannot accept --run-b, or modifies main() with a new flag. Does not threaten correctness of any computed number, but leaves the 'does not read real data' claim Executor-discretionary rather than interface-enforced, the same class of gap (though far lower stakes) RT-PREFREEZE-EXP-SSIQ-a85692-v2.md and -v3.md both rated blocking for diff-list omissions."
  required_controls:
    - "A third synthetic case in synthetic_self_test_v4 with null_survivors of length exactly NULL_ARM_MIN_PRIMES=3, asserting evaluable is True -- closes the boundary gap that lets the draft's own named min_primes off-by-one mutation pass undetected (OBJ-1, blocking)."
    - "Explicit text stating check (i) (N_list-ascending) is the sole discriminator for a missing/incorrect sorted() defect given the exact-power-law construction's order-invariance of gamma/CI (OBJ-2, advisory)."
    - "Explicit statement of the entry-point mechanism (new function/mode vs. modified main()) making RUN-SSIQ-a85692-d genuinely never read RUN-SSIQ-a85692-b's raw-result.json (OBJ-3, advisory)."
  counterexample_or_mutation: >-
    Hand-trace `if len(null_survivors) < min_primes:` (original,
    min_primes=3) vs. the mutant `if len(null_survivors) <= min_primes:`
    against synthetic_self_test_v4's two specified null_survivors lengths:
    length 2 (CHECK 1) gives NOT-EVALUABLE under both original and mutant
    (2<3 and 2<=3 both True); length 4 (CHECK 2) gives evaluable under both
    (4<3 and 4<=3 both False). Byte-identical verdicts under correct code and
    the mutant on both required checks -- a direct falsifier of
    "synthetic_self_test_v4, as specified, would catch this draft's own
    named min_primes off-by-one mutation." Concrete fix: add a
    null_survivors length-3 case (the stated floor), asserting evaluable is
    True, which correct code passes (3<3 False -> evaluable) and the mutant
    fails (3<=3 True -> NOT-EVALUABLE) -- the one length that distinguishes
    the two rules.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-10): this
    draft's call-site precision is a genuine improvement over v3's prose
    (check (a)), and two of its three named example mutations are correctly
    caught. What this review adds, per GD-10's own standing repair applied
    recursively, is that "at least one mutation would be caught" is not the
    same bar as "every named candidate mutation was actually traced" -- the
    same letter-vs-substance distinction RT-BATCH-006.md drew against v3's
    own self-test.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; every finding is a control-validation discriminating-power gap in new self-test code."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 60s/0.02 CPU-hour budget is realistic and generously oversized for two function calls on <=4-point synthetic data -- no resource-bookkeeping defect."
    - "The live concern is evidentiary, not resource cost: PF-1 means the amendment's validation artifact, as specified, would not detect one of its own three named target-mutation classes, so a future min_primes-off-by-one-mutated implementation would be certified passing by a self-test that cannot tell the difference."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "This amendment correctly narrows to exactly one change and correctly does not reopen RUN-SSIQ-a85692-c's archived DATA-UNAVAILABLE-BLOCKED outcome or the deferred trapping-mechanism diagnostic, both correctly left to a later, separately-scoped amendment (check (e))."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v4.yaml as read at
    draft status: the amendment's design correctly closes GD-10's core
    defect -- both checks genuinely call c_null_label_comparison_v3 and read
    its own return value (check (a)), and the null_per_prime schema's
    omission of N is independently confirmed against
    RUN-SSIQ-a85692-b/raw-result.json (check (c)); the amendment is
    correctly self-contained and does not touch RUN-SSIQ-a85692-c's archived
    outcome (check (e)). It should NOT be frozen as currently written:
    mutation_precondition_v4's own required freeze precondition fails for
    one of the draft's own three named example mutations (an off-by-one in
    min_primes), because neither specified check constructs a
    null_survivors list at the stated floor length of exactly 3 (PF-1,
    blocking). The missing-sorted() mutation is caught only through check
    (i), not through checks (ii)-(iv), which are analytically invariant to
    point order for this specific noiseless power-law construction (PF-2,
    advisory). The entry-point mechanism enforcing "does not read
    RUN-SSIQ-a85692-b's raw-result.json" is unstated (PF-3, advisory). None
    require redesigning the amendment's mechanism, which is otherwise a
    genuine, well-targeted fix for GD-10.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text to add a third synthetic_self_test_v4 case with null_survivors of
    length exactly NULL_ARM_MIN_PRIMES=3, asserting evaluable is True (PF-1,
    blocking) -- the single change that makes the mutation precondition's
    own worked example pass. While editing, also add an explicit note that
    check (i) alone carries the discriminating power for a missing-sorted()
    defect (PF-2, advisory) and a one-line statement of the entry-point
    mechanism that keeps RUN-SSIQ-a85692-d from reading
    RUN-SSIQ-a85692-b's raw-result.json (PF-3, advisory). Re-verify PF-1's
    specific trace once the length-3 case is added, before freeze.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v4.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No code executed. Hand-tracing only: (1) the actual, unmodified
    c_null_label_comparison_v3 (reanalyze_v3.py lines 141-216) against
    synthetic_self_test_v4's specified inputs for three named mutations; (2)
    the actual ols_loglog_fit and bootstrap_gap_ci implementations
    (descent_hitting_time.py lines 104-134, 362-384) to derive the
    order-invariance argument for the missing-sorted() mutation; (3) direct
    read of RUN-SSIQ-a85692-b/raw-result.json's descent_metrics.per_prime
    and c_null_label.per_prime to independently confirm the no-N-in-null-arm
    schema claim. No graph built, no search run, no file written outside
    this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v4.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v4.yaml itself)
    and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
