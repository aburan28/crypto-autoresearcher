# RT-BATCH-007 — Red Team review of RUN-SSIQ-a85692-d (EXP-SSIQ-a85692 v4,
# H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-007

**Reviews the Coordinator-committed snapshot at commit `a925cf30`** (parent
`0b15e854`), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/archives/TASK-20260805-3abd7d-receipt.yaml`,
covering `RUN-SSIQ-a85692-d` under `specification_v4.yaml`'s amendment
(frozen `0b15e854`) only. Independently confirmed by `git diff --stat
0b15e854 a925cf30`: only the 11 declared paths changed; `reanalyze_v3.py`,
`specification_v3.yaml`, `specification_v4.yaml`, and `RUN-SSIQ-a85692-a/-b/-c`
are byte-for-byte untouched. Nothing below is drawn from working-tree-only
state. This report changes nothing under `experiments/EXP-SSIQ-a85692/` or any
ledger record.

Read in full, per the launching task: `specification_v3.yaml`,
`specification_v4.yaml`, `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md`,
`RT-BATCH-006.md`, `implementation/reanalyze_v4_selftest.py`, the relevant
lines of `implementation/reanalyze_v3.py` (`c_null_label_comparison_v3`,
lines 141–216, unchanged), `implementation/compute_delta_e.py`,
`descent_hitting_time.py`'s `ols_loglog_fit`/`bootstrap_gap_ci`, the complete
`RUN-SSIQ-a85692-d` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `self_test_v4.json`, `source_access_log.yaml`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`), the archive
receipt, `goal.yaml`'s GD-9/GD-10 entries, `EV-SSIQ-028c9f.yaml`,
`DEC-20260805-e46f4f.yaml`. Independently executed (not merely read): the
actual `c_null_label_comparison_v3` function against synthetic inputs
matching CHECK 1/2/3 exactly, two hand-constructed mutations of it not
previously named by any prior review, and a direct reproduction of ANOM-1's
floating-point mechanism across a wider (N, resample-size) grid than the
Executor's own disclosure covers, including against the campaign's own real
prime N values.

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
    unprobeable (VAL/RT-BATCH-003 through 006, RT-PREFREEZE-EXP-SSIQ-a85692[-v2,-v3,-v4]),
    so this is recorded as the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with every producer and every prior reviewer in this
    lineage; it does not upgrade the campaign's evidence tier by itself. A
    Validator (TASK-20260805-aeb1ed) is reviewing the same run independently
    and in parallel; this report was produced without coordinating with it
    and stands alone.
```

---

## Bottom line up front

**GD-10 is genuinely closed for the mutation classes this campaign has
already named, and PF-1's specific gap is genuinely fixed.** All three
checks in `reanalyze_v4_selftest.py` call `c_null_label_comparison_v3`
directly — confirmed by grep (exactly three call sites, one per check
function) and by reading every assertion (all read `ret[...]` fields, none
hand-computes a duplicate of the wrapper's cross-dict indexing, gate, or
sort). CHECK 3's `null_survivors` list is confirmed, by direct read of the
executed code and the archived `self_test_v4.json`, to have length **exactly
3** (`[7000, 2000, 3000]`), and I independently re-executed the min_primes
off-by-one mutation the pre-freeze review found undetected: CHECK 3 now
correctly distinguishes `< min_primes` from `<= min_primes` (original:
`evaluable=True`; mutant: `evaluable=False` → `check3["pass"]` flips to
`False`). Entry-point isolation is real, not merely claimed: I traced the
full transitive import chain (`reanalyze_v3` → `compute_delta_e` →
`build_isogeny_graph`/`calibration_synthetic`/`descent_hitting_time`/
`modular_polynomials`/`velu_verify`) at the AST level and found zero
module-level file I/O anywhere in it; `reanalyze_v3.main()` requires no
default arguments and is never called.

**But I found one new mutation this self-test does not catch, and ANOM-1 is
materially more serious than the Executor's own framing states.** A mutation
that silently drops `rng_seed` threading into `bootstrap_gap_ci` (replacing
`random.Random(rng_seed)` with an unseeded `random.Random()`) passes all
three checks' assertions, on every run, because CHECK 2/3's noiseless
exact-power-law construction makes every valid bootstrap resample recover
the *same* gamma regardless of which points are drawn or in what order —
executed and confirmed: two live runs of the mutant against CHECK 2's exact
inputs produced bit-identical CIs (`0.49999999999999917`,
`0.5000000000000019`) both times, so no assertion this self-test specifies,
run once or compared across runs, would ever distinguish seeded from
unseeded resampling. Separately, I reproduced ANOM-1 directly and found it
is **not** an N=500-specific curiosity: at the exact resample size (n=3)
CHECK 3 exists to exercise, N=324 — one of this campaign's own four real
primes (3889) already used in every prior batch's real-arm bootstrap — *also*
triggers the same silent degeneracy-guard failure. The Executor's own
disclosure undersells this by describing it as isolated to "N=500 with a
3-point resample." I confirmed the anomaly can, for the right (N,
resample-size, y-value) combination, produce a genuinely wrong nonzero
`gamma` (not just a harmless `0.0`) — e.g. `gamma=0.5` from a fully-degenerate
all-identical-points design at N=611, n=6 — which is a materially more
serious failure mode (a silently wrong number entering the bootstrap
distribution) than a crash. This is real, reproducible, and affects a shared
library function two experiments (`EXP-SSIQ-58b642`, `EXP-SSIQ-a85692`)
import by reference; it warrants a named defect, **GD-11**, independent of
GD-9/GD-10's wrapper-level scope. It is good news, independently confirmed,
that this campaign's *already-archived* real bootstrap CIs (all computed at
resample size n=4 on N∈{203,324,478,611}) are not contaminated, since the
fully-degenerate case correctly raises at n=4 for all four of those specific
values — but that is a coincidence of this particular N-set and resample
size, not a structural guarantee, and the very n=3 boundary this batch's own
CHECK 3 newly exercises is exactly where the guard is least reliable.

---

## Front 1 — Do all three checks genuinely call `c_null_label_comparison_v3`?

**Yes, confirmed independently, not merely re-read from the Executor's
claim.** `grep -n "c_null_label_comparison_v3" reanalyze_v4_selftest.py`
shows exactly three call sites at the top level of `_run_check1` (line 133),
`_run_check2` (line 179), and `_run_check3` (line 275), each of the form
`ret = rv3.c_null_label_comparison_v3(real_per_prime, null_per_prime,
null_survivors, rng_seed, min_primes=NULL_ARM_MIN_PRIMES, n_boot=n_boot)`.
Every assertion dict in all three checks reads a key off `ret` (e.g.
`ret["evaluable"] is False`, `ret["primes_used"] == expected_primes_used`,
`ret["gamma_null_greedy"]`), never a value computed by a second,
independent, hand-written implementation of the wrapper's logic — the exact
GD-10 failure mode. The only place `sorted(...)` or `_CHECK23_N_MAP[...]`
appear outside the function call is in building the *expected/analytic*
reference values the returned dict is compared against (e.g.
`expected_primes_used = sorted(null_survivors)`), which is legitimate test
oracle construction, not a duplicate implementation feeding the pass/fail
verdict from an independent code path — this is qualitatively different
from GD-10's actual bug, where the self-test never touched
`c_null_label_comparison_v3` at all. **No trace of GD-10's bug recurring
inside its own fix.**

## Front 2 — Re-tracing the pre-freeze review's mutations against the actual executed data, plus new mutations

### 2a. Re-verify PF-1's fix (min_primes off-by-one) — genuinely closed

Independently executed (not just hand-traced) against CHECK 1/2/3's actual
`null_survivors` lengths (2, 4, 3):

| Check | length | original gate (`<`) | mutant gate (`<=`) | distinguishes? |
|---|---|---|---|---|
| CHECK 1 | 2 | NOT-EVALUABLE | NOT-EVALUABLE | No (as before) |
| CHECK 2 | 4 | evaluable | evaluable | No (as before) |
| CHECK 3 | 3 | evaluable | **NOT-EVALUABLE** | **Yes** |

CHECK 3's `null_survivors=[7000, 2000, 3000]` (length exactly 3, confirmed
directly against both the executed code and the archived
`self_test_v4.json`'s `check3.inputs.null_survivors`) is the boundary PF-1
required. Under the mutant, `evaluable` flips from `True` to `False`,
`check3["pass"]` becomes `False` (since `evaluable_is_True` is a required,
non-extra assertion), and `all_checks_pass` becomes `False`. **PF-1's
blocking finding is genuinely fixed, re-verified by direct execution rather
than trusting the added text.**

### 2b. New mutation 1 — swapped-source median desync (executed)

Constructed and executed the mutant `greedy_medians = [null_per_prime[p]["greedy_median"]
for p in null_survivors]` / `random_medians = [... for p in null_survivors]`
(pulling medians via the *unsorted* `null_survivors` argument instead of the
correct sorted `ordered` list — a plausible copy-paste variant of the exact
desync class this campaign's own schema-forcing design targets) against
CHECK 2's real inputs (`null_survivors=[7000,2000,5000,3000]`). Result:
`gamma_null_greedy=-0.1013` (expected `0.3`), `gamma_null_random=-0.2702`
(expected `0.8`), CI `[-1.545, 0.897]` (expected point `[0.5,0.5]`) — every
one of assertions (i)–(iv) fails decisively. **CAUGHT, and caught hard: not
merely by the sort-order assertion (i), but by the numeric fit checks
(ii)–(iv) as well**, since a permutation mismatch of an exact power law
generically does not itself lie on any power law.

### 2c. New mutation 2 — `rng_seed` silently not threaded (executed) — **NOT CAUGHT**

Constructed and executed the mutant `rng = random.Random()` (dropping the
`rng_seed` argument entirely, replacing seeded reproducibility with
wall-clock/OS entropy) inside `bootstrap_gap_ci`'s caller, against CHECK 2's
exact inputs, run twice independently:

```
run1: gamma_null_greedy=0.3, gamma_null_random=0.8, CI=[0.49999999999999917, 0.5000000000000019]
run2: gamma_null_greedy=0.3, gamma_null_random=0.8, CI=[0.49999999999999917, 0.5000000000000019]
```

All four numeric assertions (ii)–(iv) and both order assertions (i) pass,
identically, on both runs. This is not a fluke of one random draw: for
CHECK 2/3's deliberately noiseless exact-power-law construction, *every*
valid (non-degenerate) bootstrap resample recovers the exact same `gamma`
regardless of which points are drawn, in what order, or how many valid
draws occur — the identical degeneracy `VAL-BATCH-006.md` and
`RT-PREFREEZE-EXP-SSIQ-a85692-v4.md` PF-2 already established for the
missing-`sorted()` mutation, now shown to extend to a strictly larger
mutation class: **anything that only perturbs *which* points a bootstrap
resample draws, including breaking `rng_seed` reproducibility (C-REPRO)
entirely, is invisible to this self-test's assertions.** Since the self-test
also never re-invokes itself twice and diffs the output (no determinism/
reproducibility check exists anywhere in `synthetic_self_test_v4`), this gap
cannot be closed by re-running the existing checks — it needs an assertion
that was never specified: run `c_null_label_comparison_v3` twice with the
same `rng_seed` and assert bit-identical output, which the exact-power-law
construction's own degeneracy could still mask (since two seeded-*or*
unseeded runs would likely match anyway) — the cheapest discriminator would
instead need a **noisy** (non-exact) synthetic construction, where different
bootstrap draws produce genuinely different `gamma` values, so that
`rng_seed` threading is observably load-bearing. This is lower severity than
PF-1 (C-REPRO for this specific new wrapper function has no other test
coverage in this campaign either, so this is a pre-existing gap the v3→v4
lineage never claimed to close, not a regression), but it is a real,
newly-identified, currently-uncaught mutation class and should be recorded
as advisory required work, not silently absorbed into "all checks pass."

### 2d. Re-confirm Mutation 1 from the pre-freeze review (swap N dict source) — still caught

`null_per_prime` dicts in all three checks (confirmed directly in the
executed code and `self_test_v4.json`) carry only `greedy_median`/
`random_median`, never `N` — matching `c_null_label.per_prime`'s real schema
(re-confirmed against `RUN-SSIQ-a85692-b/raw-result.json` in this review's
own earlier sessions in this lineage). A mutant reading `N` from
`null_per_prime` instead of `real_per_prime` still raises `KeyError`
immediately, unchanged from the pre-freeze trace. **CAUGHT (via crash, same
caveat as before: whether an uncaught exception is required to be recorded
as an explicit FAIL row is still unstated by the spec — carried forward as
non-blocking, per PF-3's already-advisory status on this point).**

## Front 3 — Is entry-point isolation actually complete?

**Yes, verified by tracing the full import chain, not merely trusting "main()
not called."** `reanalyze_v4_selftest.py`'s `import reanalyze_v3 as rv3`
transitively imports `compute_delta_e` (`v1c`) and `descent_hitting_time`
(`dht`); `compute_delta_e` itself imports `build_isogeny_graph`,
`calibration_synthetic`, `descent_hitting_time`, `modular_polynomials`, and
`velu_verify`. I parsed every one of these six files' module-level AST
(top-level statements outside `def`/`class`/import) directly: none contains
a file-read call — `modular_polynomials.py`'s `MODPOLY_DIR` is a path
*string* built with `os.path.join`, never opened at import time;
`calibration_synthetic.py` and `descent_hitting_time.py`'s only executable
top-level statements besides constant/regex assignments are
`sys.path.insert` and an `if __name__ == "__main__":` guard, which does not
fire on import. Both `reanalyze_v3.main()` and `compute_delta_e.main()` take
**zero** parameters (`def main():`), so there are no eagerly-evaluated
default-argument file paths either. `source_access_log.yaml`'s
`files_read_this_run: [none]` and the two `open()` calls in
`reanalyze_v4_selftest.py` (both mode `"w"`, both to `--out`/
`--self-test-out`) are independently confirmed, not merely re-stated.
**The "imported but main() not called" claim genuinely holds all the way
down the transitive chain — a real result, not an unchecked assumption,
answering the task's specific concern.**

## Front 4 — ANOM-1: independent investigation and severity verdict

Reproduced the mechanism directly (not merely re-derived from the Executor's
narrative): `ols_loglog_fit`'s degeneracy guard is `if sxx == 0.0: raise
ValueError`, where `sxx = sum((x - xbar)**2 for x in xs)` and `xbar =
sum(xs)/n`. For `n` repeated copies of `x = log(N)`, IEEE-754 summation of
`n` identical floats followed by division by `n` does not always round-trip
to bit-identical `x` — whether it does depends on the specific mantissa bits
of `log(N)`, which is unrelated to any property of the *data*, purely an
artifact of which floating-point value `log(N)` happens to be.

**Reproduced across a grid, not just at the Executor's one reported point:**

```
N=203  n=3,4,5,6,7,8: guard fires correctly (OK) at every n tested
N=324  n=3: ANOMALY (sxx=2.4e-30, silent)   n=4,5: OK   n=6,7,8: ANOMALY
N=478  n=3,4,5,6,7,8: guard fires correctly at every n tested
N=500  n=3: ANOMALY (the Executor's own reported case)
N=611  n=3,4: OK   n=5,6,7,8: ANOMALY
```

**Materially stronger finding than the Executor's own framing:** N=324 is
not a synthetic value — it is **prime 3889's real N value**, already used in
every real-arm bootstrap this campaign has run to date, and it triggers the
identical silent-degeneracy failure at **n=3**, the exact resample size
CHECK 3 exists to exercise for the first time in this campaign's history.
The Executor's disclosure states the anomaly is specific to "N=500 with a
3-point bootstrap resample" and frames the fix as excluding one prime from
one check's construction; it does not report that a real campaign prime is
equally exposed at the same boundary.

**Confirmed the failure mode is not merely cosmetic (not always `gamma=0.0`):**
constructing a fully-degenerate all-identical-points design at N=611, n=6
(a repeat-count that is realistic for a null-arm survivor count once this
campaign widens past its current 4–5 primes) with `y=36.0` (prime 7333's
real `random_median`, which I independently found does *not* round-trip
under 3-way summation either: `log(36.0)*3/3 != log(36.0)`) produces
`gamma=0.5` — a plausible-looking but entirely spurious slope from a design
that should have raised `ValueError` and been discarded. This confirms the
Executor's own "spurious non-degenerate fit" language is not hypothetical:
a wrong, non-obviously-wrong number can silently enter
`bootstrap_gap_ci`'s `gaps` list.

**Bearing on prior batches' real results — checked directly, not assumed:**
`RUN-SSIQ-a85692-b`'s own already-archived real-arm bootstrap
(`descent_metrics.gamma_greedy=0.2335`, `m_gap_ci_lo=-0.408`,
`m_gap_ci_hi=1.326`, `n_primes_used=4`) resamples at **n=4** over
N∈{203,324,478,611}. I confirmed the fully-degenerate (all-4-draws-identical)
case correctly raises `ValueError` for **all four** of these specific N
values at n=4 — so this specific already-archived number is not contaminated
by ANOM-1. **This is a fact about this particular 4-value set at this
particular resample size, not a structural guarantee**: N=324 is anomalous
at n=3, n=6, n=7, n=8 (just not n=4, by what the arithmetic above shows is
coincidence of that value's specific mantissa bits), and N=611 is anomalous
at every n≥5 tested. `c_null_label_comparison_v3`'s null-arm fit-and-bootstrap
branch has **never yet run on real data** (confirmed by `RT-PREFREEZE-v3`/
`RT-BATCH-006`: real null-arm survivor count was 0, below the n≥3 floor,
every batch to date), so there is no already-computed *null-arm* bootstrap
CI to check — but the very next time it does run for real, if the survivor
count lands at exactly 3 (this campaign's own stated floor,
`NULL_ARM_MIN_PRIMES=3`) and includes prime 3889 (N=324), the guard is
confirmed silently unreliable at that exact combination.

**Verdict: this is a genuine, reproducible, silently-wrong-output defect in
a shared library function (`dht.ols_loglog_fit`'s degeneracy check),
imported by reference into two experiments (`EXP-SSIQ-58b642`,
`EXP-SSIQ-a85692`), and it should be named as a new defect, GD-11,
independent of and lower in the stack than GD-9/GD-10's wrapper-level
concerns.** It does not currently invalidate any archived number (checked,
not assumed), and this batch's workaround for CHECK 3 specifically was
reasonable (see Front 5) — but the underlying guard (`sxx == 0.0` as an
exact float comparison after summation) is not a robust way to detect
degenerate designs, and the next real dispatch that reaches the null arm's
fit-and-bootstrap branch at a small survivor count is at genuine,
non-hypothetical risk. Recommended fix direction (not itself required by
this review): replace `sxx == 0.0` with `max(xs) == min(xs)` (checks the
*inputs* for exact equality directly, independent of summation rounding) or
an epsilon-relative tolerance keyed to `xbar`'s magnitude.

## Front 5 — Was excluding N=500 from CHECK 3 legitimate?

**For:** CHECK 3's stated purpose (per `specification_v4.yaml` and PF-1) is
narrowly to distinguish `len(null_survivors) < min_primes` from `<=
min_primes` at the boundary length 3 — a control-flow/gate test, not a
numerical-robustness test of `ols_loglog_fit`/`bootstrap_gap_ci`, which are
explicitly named "imported unchanged, by reference" and out of scope for
this amendment. The spec's own text constrains only the survivors-list
*length* ("EXACTLY NULL_ARM_MIN_PRIMES=3"), not which 3 of the 4 constructed
primes are chosen, so selecting `{200,300,700}` over `{200,300,500}` is
within the spec's own stated freedom. The choice was disclosed in three
places (a code comment, `execution_report.yaml`'s ANOM-1 entry, and
`manifest.yaml`'s `check3.note`), all *before* being cited as evidence, and
the Coordinator's own precommit check flagged it `FLAGGED_FOR_INDEPENDENT_REVIEW`
rather than silently endorsing it — good practice.

**Against:** CHECK 3 is the *first* test in this campaign's history to
exercise `bootstrap_gap_ci` at n=3, and its `all_checks_pass: true` /
`self_test_verdict: PASS` framing (`self_test_v4.json`, `raw-result.json`)
will be read by future records as "the fit-and-bootstrap branch is validated
at the boundary." Per Front 4, that PASS is true only for the specific
N-values chosen *because* they are known not to trigger ANOM-1 — a
different, equally spec-compliant choice of survivors (e.g. one including
prime 3889/N=324, which is exactly as likely to arise from real
`trapped_exclusion_filter_v3` output as any other prime) would have failed
CHECK 3's own <1e-9 tolerance assertions outright. This is not the same
class of gap as GD-9/GD-10 (this self-test does call the right function, and
the "PASS" is not fabricated for the data it actually used), but the
self-test's own claimed scope ("demonstrates the fit-and-bootstrap branch
executes end-to-end") is not fully earned: it demonstrates the branch
executes end-to-end *for numerically well-behaved inputs*, which real
`trapped_exclusion_filter_v3` output is not guaranteed to be.

**Verdict: legitimate and narrow for CHECK 3's own stated purpose (the
min_primes gate), but not orthogonal to `c_null_label_comparison_v3`'s
real-world reliability at n=3, and the run package's framing should say so.**
Recommend a text-only addition to a successor record (not a re-run): state
explicitly that CHECK 3's `all_checks_pass=true` validates the min_primes
gate and the exact-power-law fit/CI arithmetic *for the specific N values
tested*, and does **not** establish that `dht.ols_loglog_fit`/
`bootstrap_gap_ci` are numerically robust at n=3 for arbitrary real N —
that question is open and is exactly what ANOM-1/GD-11 names.

## Front 6 — BATCH-008 ranking

`DEC-20260805-e46f4f`'s `next_actions` named the trapping-mechanism
diagnostic (already-collected graph/vertex/`delta_map` data from
`RUN-SSIQ-a85692-b`, zero new search) as item (2), deferred behind GD-10's
fix (item (1), now closed by this batch). Given this batch's own findings:

1. **[HIGHEST, ZERO NEW COMPUTE] Record GD-11** (name the defect, state the
   obstruction — `sxx == 0.0` as an exact-float degeneracy check is
   unreliable — and the forward guidance: harden the guard, e.g.
   `max(xs)==min(xs)`, before the null arm's fit-and-bootstrap branch first
   runs on real data). This is a documentation/defect-naming action, not a
   code change, and costs nothing. It must land before any future run cites
   a null-arm `c_null_label_control_failure` computed from a small (n=3–5)
   real survivor set as trustworthy without this caveat.
2. **[HIGH, CHEAP, RECOMMENDED BEFORE (3)] Harden `dht.ols_loglog_fit`'s
   degeneracy guard** (`max(xs)==min(xs)` or an epsilon-relative check) and
   re-run CHECK 2/3 plus a targeted regression test at N=324/n=3 and
   N=611/n=6 to confirm the fix. This is a genuine code change to a shared,
   frozen library, so it needs its own scoped amendment and pre-freeze
   review (not silently folded into the trapping diagnostic), but it is
   small, targeted, and zero new search. I do **not** rank this above the
   trapping-mechanism diagnostic outright, because — per the already-checked
   fact in Front 4 — no currently-archived real number is contaminated, so
   there is no live incorrect conclusion to correct; but it should land
   *before*, not after, the campaign's next real null-arm fit-and-bootstrap
   execution, whichever action produces that first.
3. **[HIGH, ZERO NEW COMPUTE] The trapping-mechanism diagnostic**
   (`DEC-20260805-e46f4f`'s item (2)), unchanged in substance from prior
   batches' ranking: is trapping concentrated on specific low-degree
   vertices, correlated with a graph-structural property independent of N,
   or an artifact of the greedy tie-break rule. Nothing in this batch's
   findings changes this diagnostic's priority or method; it remains
   zero-new-search and does not depend on GD-11 being fixed first (it reads
   already-collected graph data, not `ols_loglog_fit` output).
4. **[ADVISORY, TEXT-ONLY] Add a determinism/reproducibility check for
   `c_null_label_comparison_v3`'s `rng_seed` threading** using a *noisy*
   (non-exact-power-law) synthetic construction, per Front 2c. Lower
   priority than 1–3: no currently-archived result depends on this property
   being tested, and it is cheap to add whenever `synthetic_self_test_v4` is
   next touched, but should not be silently dropped from the campaign's
   backlog.

**Ranked: 1 (GD-11 naming) > 2 (harden the guard) ≈ 3 (trapping diagnostic,
can run in parallel with 2, independent data) > 4 (rng-seed determinism
check).** Do not let 2 block 3 — they use disjoint data and code paths.

---

## Objections

1. **[Front 2c, MEDIUM, NEW FINDING] A mutation that silently drops
   `rng_seed` threading (unseeded `random.Random()` replacing
   `random.Random(rng_seed)`) is not caught by any of `synthetic_self_test_v4`'s
   three checks, on any run.** Executed directly against CHECK 2's exact
   inputs, twice: both runs produced bit-identical, fully-passing output
   (`gamma_null_greedy=0.3`, CI=`[0.49999999999999917, 0.5000000000000019]`
   both times). This holds because the noiseless exact-power-law
   construction makes every valid bootstrap resample recover the identical
   `gamma`, the same structural degeneracy `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md`
   PF-2 already found for the missing-`sorted()` mutation, now shown to
   extend to the reproducibility (C-REPRO) property specifically. No
   currently-specified assertion, including a hypothetical re-run-and-compare
   check, would catch this without a noisy (non-exact) construction.
2. **[Front 4, HIGH, NEW FINDING] ANOM-1 is broader and more serious than
   the Executor's own disclosure states, and warrants a new defect (GD-11)
   against the shared `dht.ols_loglog_fit`.** Independently reproduced
   across a wider (N, resample-size) grid than the Executor tested: N=324
   (a real campaign prime, 3889) is *also* anomalous at n=3 — the exact
   resample size CHECK 3 newly exercises — not only the synthetic N=500 the
   disclosure names. Independently confirmed the anomaly can produce a
   genuinely wrong nonzero `gamma` (e.g. `0.5` from a fully-degenerate
   design at N=611/n=6 with prime 7333's real `random_median`), not only a
   harmless `gamma=0.0`. Independently confirmed this campaign's
   already-archived real bootstrap CI (`RUN-SSIQ-a85692-b`, n=4,
   N∈{203,324,478,611}) is *not* currently contaminated (the guard correctly
   fires for all four values at n=4), but this is a coincidence of that
   specific value set and resample size, not a structural guarantee — the
   null arm's own fit-and-bootstrap branch has never yet run on real data,
   and the next time it does, at the campaign's own stated floor
   (`NULL_ARM_MIN_PRIMES=3`), it is exposed if prime 3889 is among the
   survivors.
3. **[Front 5, ADVISORY] CHECK 3's `all_checks_pass=true` is read too
   broadly by the run package's own framing.** "Demonstrates the
   fit-and-bootstrap branch executes end-to-end" is true only for the
   specific, ANOM-1-avoiding N values CHECK 3 was constructed with; a
   different, equally spec-compliant choice of survivors would have failed
   CHECK 3's own tolerance assertions. Not a defect in CHECK 3's design
   (its own narrow purpose — the min_primes gate — is genuinely served), but
   the successor record should state this scope limit explicitly rather than
   let "PASS" imply general numerical robustness at n=3.

## Required controls

- Record GD-11 against `dht.ols_loglog_fit`'s degeneracy guard
  (`sxx == 0.0` as an exact-float comparison), naming the obstruction (guard
  reliability depends on floating-point summation coincidence, not on any
  property of the data), independently reproduced at N=324/n=3 and
  N=611/n=6, before the null arm's fit-and-bootstrap branch first executes
  on real data (OBJ-2).
- A text-only scope caveat on any successor record citing this batch's
  `all_checks_pass=true`: CHECK 3 validates the min_primes gate and the
  fit/CI arithmetic for the specific N values it was constructed with, not
  general numerical robustness of `ols_loglog_fit`/`bootstrap_gap_ci` at
  n=3 for arbitrary real N (OBJ-3).
- A determinism/reproducibility check for `c_null_label_comparison_v3`'s
  `rng_seed` threading, using a noisy (non-exact-power-law) synthetic
  construction so that seeded vs. unseeded resampling is observably
  distinguishable — lower priority, recorded as backlog, not blocking this
  batch's closure of GD-10 (OBJ-1).

## Counterexample or mutation

Two mutations executed directly against the real, unchanged
`c_null_label_comparison_v3` and CHECK 2's exact inputs:
(1) desynchronized medians (`greedy_medians`/`random_medians` pulled via
unsorted `null_survivors` instead of `ordered`) — **caught decisively**,
`gamma_null_greedy=-0.1013` vs. expected `0.3`; (2) `rng_seed` silently
dropped (`random.Random()` instead of `random.Random(rng_seed)`) — **not
caught**, both runs of the mutant reproduce bit-identical, fully-passing
output (`gamma_null_greedy=0.3`, CI=`[0.49999999999999917,
0.5000000000000019]`), because the noiseless exact-power-law construction
makes the bootstrap distribution's every valid draw identical regardless of
which points are resampled or with what randomness. This is a direct
falsifier of "synthetic_self_test_v4, as specified and executed, would catch
any subtle wrong implementation of `c_null_label_comparison_v3`" for the
specific mutation class of broken reproducibility.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale gradient-existence screen, `asymptotic_claim: null` throughout,
correctly inherited unchanged. The relevant baseline is this campaign's own
instrument- and fix-scrutiny discipline (GD-4 through GD-10): this batch
clears that bar for the specific gap GD-10 named (the wrapper is genuinely
exercised, PF-1's boundary case is genuinely closed, re-verified by direct
execution rather than trusting added text) and materially exceeds it by
surfacing a defect (ANOM-1/GD-11) in a *different, lower* layer of the stack
that no prior review in this lineage traced past the Executor's own
disclosure — the Executor named ANOM-1 honestly (AGENTS rule 8, not silently
discarded) but characterized its scope more narrowly than an independent
reproduction across a wider grid supports.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
finding here implicates a numbered heuristic; every finding is a
control-validation and shared-library-correctness gap.

## Cost model challenges

No asymptotic-cost claim is made (`asymptotic_claim: null`, correctly); the
per-attempt × inverse-success-probability review does not apply. The
`60s`/`0.02` CPU-hour budget is realistic and generously oversized (measured
`0.054s`) — no resource-bookkeeping defect. The live concern is again
evidentiary: GD-11 (Front 4) means a future real dispatch's bootstrap CI at
small resample sizes could silently include a spurious point-estimate
without any budget or timing signal indicating something is wrong — the
defect is invisible to every cost/timing control this campaign has, by
construction, since it produces a plausible-looking finite number, not a
crash or timeout.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears
anywhere in this amendment or its inherited hypothesis.
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) is correctly stated and not
exceeded. No scope-inflation found. This amendment correctly narrows to
exactly one change (`run_synthetic_self_test_v3` → `v4`) and correctly does
not reopen `RUN-SSIQ-a85692-c`'s archived `DATA-UNAVAILABLE-BLOCKED` outcome
or the deferred trapping-mechanism diagnostic — independently confirmed:
`grep -c "RUN-SSIQ-a85692-c\|trapped_exclusion_filter_v3(" reanalyze_v4_selftest.py`
shows no invocation of either.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level
gradient-existence screen, not a proof-oriented proposal. Attacked and held,
same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-d` as committed at `a925cf30`: GD-10 is genuinely
closed for every mutation class this campaign has so far named
(swapped-N-source, off-by-one `min_primes` — re-verified by direct
execution at the exact boundary length, missing-`sorted()`) — all three
checks in `reanalyze_v4_selftest.py` call `c_null_label_comparison_v3`
directly, confirmed by grep and by reading every assertion. Entry-point
isolation (PF-3) is genuinely complete, verified by tracing the full
transitive import chain's module-level AST, not merely trusting
"main() not called." One new mutation (silently dropped `rng_seed`
threading) is **not** caught by any check as specified, executed and
confirmed directly — lower severity, recorded as backlog. `ANOM-1` is real,
independently reproduced, and **broader** than the Executor's own framing:
it affects a real campaign prime (N=324, prime 3889) at the exact n=3
boundary this batch newly exercises, and can produce a genuinely wrong
nonzero `gamma`, not only a harmless `0.0` — this should be named as a new
defect, GD-11, against the shared `dht.ols_loglog_fit`, independent of
GD-9/GD-10's wrapper-level scope. No currently-archived real result is
contaminated by GD-11 (checked directly: all four real N values correctly
trigger the guard at the n=4 resample size those results actually used),
but this is a coincidence of that specific value set, not a structural
guarantee, and the null arm's fit-and-bootstrap branch has never yet run on
real data. CHECK 3's exclusion of N=500 was a legitimate, narrow exercise of
the spec's own stated freedom for its own stated purpose (the min_primes
gate), but its `all_checks_pass=true` should not be read as general
numerical robustness of `ols_loglog_fit`/`bootstrap_gap_ci` at n=3 for
arbitrary real N — that question is exactly what GD-11 leaves open.

## Next concrete action

Coordinator: (1) record GD-11 in `goal.yaml`, naming the obstruction
(`sxx == 0.0` as an exact-float degeneracy check is unreliable, independently
reproduced at N=324/n=3 and N=611/n=6, N=324 being a real campaign prime)
and forward guidance (harden the guard before the null arm's
fit-and-bootstrap branch first runs on real data at a small survivor count);
(2) open BATCH-008 with, in parallel where independent: the trapping-mechanism
diagnostic (`DEC-20260805-e46f4f` item (2), zero new search, unaffected by
GD-11) and a small, separately-scoped amendment hardening
`dht.ols_loglog_fit`'s degeneracy guard (e.g. `max(xs)==min(xs)`), each
through its own pre-freeze review; (3) add the `rng_seed`-threading
determinism check to backlog (OBJ-1), non-blocking. Do not cite this batch's
`all_checks_pass=true` as validating `ols_loglog_fit`/`bootstrap_gap_ci`'s
numerical robustness at n=3 generally — only GD-10's specific wrapper-wiring
concern, and only for the N values CHECK 2/3 actually used.

## Overall verdict

**CHALLENGE, NARROW.** GD-10 is genuinely fixed and this batch's own
required mutation-precondition (PF-1) is genuinely re-verified by direct
execution, not merely re-read — this is a real, well-targeted advance,
materially better than v3's own self-test. The challenge is that this
batch's own disclosed anomaly (ANOM-1) is broader and more consequential
than its own framing states, and one additional mutation class (`rng_seed`
threading) is not caught by any check as specified — neither finding
overturns GD-10's closure or `RUN-SSIQ-a85692-d`'s `completed_valid` status,
but ANOM-1 should be named as its own defect (GD-11) rather than left as an
anomaly note inside a run package whose own headline claim is about a
different function entirely.

```yaml
red_team_report:
  id: RT-BATCH-007
  task_id: TASK-20260805-b73a2e
  claim_under_review: >-
    RUN-SSIQ-a85692-d (experiments/EXP-SSIQ-a85692, specification_v4.yaml,
    hypothesis H-SSIQ-36e970): a stand-alone synthetic self-test
    (reanalyze_v4_selftest.py) that fixes GD-10 by calling
    c_null_label_comparison_v3 (GD-9's wrapper, unchanged) directly through
    three checks -- NOT-EVALUABLE branch, unsorted fit-and-bootstrap branch,
    and the exact NULL_ARM_MIN_PRIMES=3 boundary (PF-1's blocking fix) --
    with a new, isolated entry point that structurally cannot read real
    data, plus a disclosed floating-point anomaly (ANOM-1) in the frozen,
    unchanged dht.ols_loglog_fit worked around in CHECK 3's construction.
  objections:
    - "OBJ-1 [Front 2c, MEDIUM, NEW FINDING]: a mutation silently dropping rng_seed threading (random.Random() replacing random.Random(rng_seed) inside c_null_label_comparison_v3's bootstrap call) is NOT caught by any of synthetic_self_test_v4's three checks, on any run. Executed directly against CHECK 2's exact inputs twice: both runs produced bit-identical, fully-passing output (gamma_null_greedy=0.3, CI=[0.49999999999999917, 0.5000000000000019]) because the noiseless exact-power-law construction makes every valid bootstrap resample recover the identical gamma regardless of which points are drawn or in what order -- the same structural degeneracy RT-PREFREEZE-EXP-SSIQ-a85692-v4.md PF-2 found for the missing-sorted() mutation, now shown to extend to C-REPRO/reproducibility specifically. No currently-specified assertion would catch this without a noisy (non-exact-power-law) construction."
    - "OBJ-2 [Front 4, HIGH, NEW FINDING]: ANOM-1 is broader and more serious than the Executor's own disclosure states and warrants a new defect (GD-11) against the shared dht.ols_loglog_fit, independent of GD-9/GD-10's wrapper-level scope. Independently reproduced across a wider (N, resample-size) grid: N=324 (this campaign's own real prime 3889, already used in every prior real-arm bootstrap) is ALSO anomalous at n=3 -- the exact resample size CHECK 3 newly exercises -- not only the synthetic N=500 the disclosure names; N=611 is anomalous at n>=5. Independently confirmed the anomaly can produce a genuinely wrong NONZERO gamma (0.5, from a fully-degenerate design at N=611/n=6 using prime 7333's real random_median=36.0), not only the harmless gamma=0.0 the disclosed example happened to show. Independently confirmed this campaign's already-archived real bootstrap CI (RUN-SSIQ-a85692-b, n=4, N in {203,324,478,611}) is NOT currently contaminated -- the guard correctly fires for all four values at n=4 -- but this is a coincidence of that specific value set and resample size, not a structural guarantee, and the null arm's own fit-and-bootstrap branch has never yet run on real data; the next time it does, at this campaign's own stated floor NULL_ARM_MIN_PRIMES=3, it is exposed if prime 3889 is among the survivors."
    - "OBJ-3 [Front 5, ADVISORY]: CHECK 3's all_checks_pass=true is read too broadly by the run package's own framing (\"demonstrates the fit-and-bootstrap branch executes end-to-end\"). This is true only for the specific, ANOM-1-avoiding N values CHECK 3 was constructed with (per PD-2's disclosed choice); a different, equally spec-compliant selection of survivors (e.g. including prime 3889/N=324) would have failed CHECK 3's own <1e-9 tolerance assertions outright. Not a defect in CHECK 3's design (its narrow purpose, the min_primes gate, is genuinely served and independently re-verified by direct execution), but the successor record should state this scope limit explicitly rather than let PASS imply general numerical robustness at n=3."
  required_controls:
    - "Record GD-11 against dht.ols_loglog_fit's degeneracy guard (sxx==0.0 as an exact-float comparison), naming the obstruction and forward guidance (harden the guard, e.g. max(xs)==min(xs), before the null arm's fit-and-bootstrap branch first runs on real data at a small survivor count) -- OBJ-2."
    - "Text-only scope caveat on any successor record citing this batch's all_checks_pass=true: validates the min_primes gate and fit/CI arithmetic for the specific N values tested, not general numerical robustness of ols_loglog_fit/bootstrap_gap_ci at n=3 for arbitrary real N -- OBJ-3."
    - "A determinism/reproducibility check for c_null_label_comparison_v3's rng_seed threading using a noisy (non-exact-power-law) synthetic construction -- lower priority, backlog, non-blocking -- OBJ-1."
  counterexample_or_mutation: >-
    Two mutations executed directly against the real, unchanged
    c_null_label_comparison_v3 and CHECK 2's exact inputs: (1) desynchronized
    medians (greedy_medians/random_medians pulled via unsorted
    null_survivors instead of ordered) -- CAUGHT decisively,
    gamma_null_greedy=-0.1013 vs expected 0.3; (2) rng_seed silently dropped
    (random.Random() instead of random.Random(rng_seed)) -- NOT CAUGHT, both
    runs of the mutant reproduce bit-identical, fully-passing output
    (gamma_null_greedy=0.3, CI=[0.49999999999999917, 0.5000000000000019]),
    because the noiseless exact-power-law construction makes the bootstrap
    distribution's every valid draw identical regardless of which points are
    resampled or with what randomness. Direct falsifier of
    "synthetic_self_test_v4, as specified and executed, would catch any
    subtly wrong implementation of c_null_label_comparison_v3" for the
    specific mutation class of broken reproducibility.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-10): this batch
    clears that bar for the specific gap GD-10 named (re-verified by direct
    execution, not by trusting added text) and materially exceeds it by
    surfacing a defect in a different, lower layer of the stack (ANOM-1/GD-11)
    that no prior review traced past the Executor's own, narrower disclosure.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; every finding is a control-validation or shared-library-correctness gap."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 60s/0.02 CPU-hour budget is realistic and generously oversized (measured 0.054s) -- no resource-bookkeeping defect."
    - "The live concern is evidentiary: GD-11 means a future real dispatch's bootstrap CI at small resample sizes could silently include a spurious point-estimate with no budget/timing signal indicating a problem -- the defect produces a plausible-looking finite number, not a crash or timeout, so it is invisible to every cost/timing control this campaign has."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "This amendment correctly narrows to exactly one change and correctly does not reopen RUN-SSIQ-a85692-c's archived DATA-UNAVAILABLE-BLOCKED outcome or the deferred trapping-mechanism diagnostic -- independently confirmed by grep, neither is invoked anywhere in reanalyze_v4_selftest.py."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-d as committed at a925cf30: GD-10 is genuinely
    closed for every mutation class this campaign has so far named --
    confirmed by grep (exactly three call sites, all reading the function's
    own return value) and by direct re-execution of the min_primes off-by-one
    mutation at CHECK 3's exact boundary length (evaluable flips True->False
    under the mutant, as required). Entry-point isolation (PF-3) is
    genuinely complete, verified by AST-level tracing of the full transitive
    import chain, not merely trusting "main() not called." One new mutation
    (silently dropped rng_seed threading) is NOT caught by any check as
    specified, executed and confirmed directly -- lower severity, backlog.
    ANOM-1 is real, independently reproduced, and broader than the
    Executor's own framing: it affects a real campaign prime (N=324, prime
    3889) at the exact n=3 boundary this batch newly exercises, and can
    produce a genuinely wrong nonzero gamma, not only gamma=0.0 -- should be
    named as a new defect, GD-11, against the shared dht.ols_loglog_fit,
    independent of GD-9/GD-10's scope. No currently-archived real result is
    contaminated (checked directly: the guard correctly fires for all four
    real N values at the n=4 resample size those results actually used),
    but this is a coincidence of that value set, not a guarantee, and the
    null arm's fit-and-bootstrap branch has never yet run on real data.
    CHECK 3's exclusion of N=500 was legitimate and narrow for its own
    stated purpose (the min_primes gate), but its all_checks_pass=true
    should not be read as general numerical robustness at n=3 -- that
    question is exactly what GD-11 leaves open.
  next_concrete_action: >-
    Coordinator: (1) record GD-11 in goal.yaml, naming the obstruction
    (sxx==0.0 as an exact-float degeneracy check is unreliable, reproduced
    at N=324/n=3 and N=611/n=6, N=324 being a real campaign prime) and
    forward guidance (harden the guard before the null arm's
    fit-and-bootstrap branch first runs on real data at a small survivor
    count); (2) open BATCH-008 with, in parallel where independent: the
    trapping-mechanism diagnostic (DEC-20260805-e46f4f item (2), zero new
    search, unaffected by GD-11) and a small, separately-scoped amendment
    hardening dht.ols_loglog_fit's degeneracy guard, each through its own
    pre-freeze review; (3) add the rng_seed-threading determinism check to
    backlog, non-blocking. Do not cite this batch's all_checks_pass=true as
    validating ols_loglog_fit/bootstrap_gap_ci's numerical robustness at n=3
    generally -- only GD-10's specific wrapper-wiring concern, and only for
    the N values CHECK 2/3 actually used.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/reviews/RT-BATCH-007.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Executed (not merely traced): the actual, unchanged
    c_null_label_comparison_v3 against CHECK 1/2/3's exact synthetic inputs,
    reproducing self_test_v4.json's own reported values exactly; two
    hand-constructed mutations of c_null_label_comparison_v3 (desynchronized
    medians, dropped rng_seed threading) executed against CHECK 2's inputs;
    the min_primes off-by-one mutation re-executed at CHECK 1/2/3's actual
    lengths (2, 4, 3) to confirm PF-1's fix; ols_loglog_fit's sxx degeneracy
    guard reproduced directly across a grid of (N, resample-size) pairs
    including this campaign's own real prime N values (203, 324, 478, 611,
    2437, 3889, 5737, 7333, 8893) and n in [2,8]; AST-level parse of six
    transitively-imported modules' module-level statements to verify no
    file I/O occurs at import time. git diff --stat confirmed only the 11
    declared paths changed between commits 0b15e854 and a925cf30. No graph
    built, no delta_E search run, no real prior run's raw-result.json read
    at any point in this review.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/reviews/RT-BATCH-007.md
    -- experiments/EXP-SSIQ-a85692/ and every ledger record are untouched.
  verdict: CHALLENGE
```
