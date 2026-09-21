# VAL-BATCH-007 — Validator review of RUN-SSIQ-a85692-d (EXP-SSIQ-a85692 v4, H-SSIQ-36e970, GD-10 fix)

**Reviews the Coordinator-committed snapshot at commit `a925cf30`** (receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/archives/TASK-20260805-3abd7d-receipt.yaml`,
parent `0b15e854`). Nothing in this report edits `specification_v4.yaml`,
`reanalyze_v3.py`, `reanalyze_v4_selftest.py`, any raw artifact,
`descent_hitting_time.py`, or any ledger record. Every input named in the
launching task was read in full, not sampled: `specification_v3.yaml` (363
lines) and `specification_v4.yaml` (264 lines, the frozen contract this run
implements) in full; `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md` in full;
`reanalyze_v4_selftest.py` (518 lines) read directly, in full, not the
manifest's prose description; `reanalyze_v3.py`'s `c_null_label_comparison_v3`
(lines 141–216, the wrapper under test, unchanged) read directly; the complete
`RUN-SSIQ-a85692-d` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `self_test_v4.json`); the
snapshot receipt including `coordinator_precommit_checks`;
`descent_hitting_time.py`'s `ols_loglog_fit` (lines 104–134) and
`bootstrap_gap_ci` (lines 362–384) read in full to independently reproduce
ANOM-1; `goal.yaml`'s GD-9/GD-10 entries, `EV-SSIQ-028c9f.yaml`,
`DEC-20260805-e46f4f.yaml` in full; and, for template conformance,
`VAL-BATCH-006.md`. All numeric claims below that are independently
computable were recomputed in a live Python session against the actual
imported `c_null_label_comparison_v3`/`ols_loglog_fit` code, not merely
re-derived on paper.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy
    (CLAUDE.md, "Model policy note"); this session runs model: inherit, so
    review-adversarial resolves to the session model rather than a
    policy-resolved identifier. Same standing condition every review in this
    lineage has recorded (VAL/RT-BATCH-003 through VAL-BATCH-006,
    RT-PREFREEZE-EXP-SSIQ-a85692-v2/v3/v4).
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer, the pre-freeze reviewer, and every prior
    reviewer in this lineage; nothing below is corroboration from a distinct
    model. Per AGENTS.md "Goal closure quorum," this alone can never satisfy a
    closure quorum, and this record does not itself close GOAL-SSIQ-001 or
    change H-SSIQ-36e970's status.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `git merge-base --is-ancestor a925cf30 HEAD`
  confirms `a925cf30` is an ancestor of `HEAD`. Reachable.
- **Parent:** `git show a925cf30 --format=%P -s` → `0b15e854644f243b59ee7debfd4aba7b19eb544a`,
  exactly the receipt's declared `parent_sha`. Match.
- **Path set:** `git show --stat a925cf30` lists exactly 11 changed files: the
  10 declared artifacts plus the receipt itself. No extra file, nothing
  missing.
- **Hashes:** recomputed `sha256(git show a925cf30:<path>)` independently for
  all 10 declared paths and compared against the receipt's `path_sha256` —
  **0 mismatches**, all 10 exact 64-hex matches:

  | path | match |
  |---|---|
  | implementation/reanalyze_v4_selftest.py | MATCH |
  | runs/RUN-SSIQ-a85692-d/manifest.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-d/raw-result.json | MATCH |
  | runs/RUN-SSIQ-a85692-d/execution_report.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-d/source_access_log.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-d/command.txt | MATCH |
  | runs/RUN-SSIQ-a85692-d/environment.json | MATCH |
  | runs/RUN-SSIQ-a85692-d/stdout.log | MATCH |
  | runs/RUN-SSIQ-a85692-d/stderr.log | MATCH (`e3b0c442...` — the standard
    empty-file SHA-256, consistent with an empty `stderr.log`) |
  | runs/RUN-SSIQ-a85692-d/self_test_v4.json | MATCH |

- **v1/v2/v3 artifacts and RUN-a/-b/-c untouched:** `git diff --stat
  0b15e854 a925cf30 -- experiments/EXP-SSIQ-a85692/specification.yaml
  experiments/EXP-SSIQ-a85692/specification_v2.yaml
  experiments/EXP-SSIQ-a85692/specification_v3.yaml
  experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py
  experiments/EXP-SSIQ-a85692/implementation/compute_delta_e_v2.py
  experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-c` returns **empty** — no
  changes to any of them between the freeze commit and this snapshot. Confirms
  the Executor's own `git diff --stat HEAD` claim in `manifest.yaml`'s
  `dirty_note` and `execution_report.yaml`'s `implementation_commit_note`.

**Verdict: PASS.** The receipt is a faithful, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v4.yaml` frozen in commit `0b15e854` ("EXP-SSIQ-a85692 v4
  FROZEN (all three pre-freeze findings resolved)"), itself the direct child
  of `638c4121` (pre-freeze review artifact commit) and `7859edb8` (draft
  commit) — the freeze followed the pre-freeze review in the commit graph, not
  the reverse.
- `manifest.yaml.code.commit = 0b15e854644f243b59ee7debfd4aba7b19eb544a`
  equals the snapshot's own `parent_sha` exactly: the run executed against the
  precise commit that froze `specification_v4.yaml`, with no intervening
  commit between freeze and execution.
- `specification_v4.yaml`'s frozen text (read in full, §"THE CENTRAL
  QUESTION" below) includes CHECK 3 (the PF-1 blocking fix) at freeze time —
  confirmed by reading the committed file directly, not inferred from the
  freeze commit message alone.

**Verdict: PASS.**

**One process observation, not blocking:** `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md`'s
own `next_concrete_action` explicitly asked for the fixed draft's PF-1 trace to
be **re-verified** ("re-verify PF-1's specific trace once the length-3 case is
added, before freeze, per this campaign's standing practice of tracing the
fix, not merely trusting that text was added") before freezing. The freeze
commit (`0b15e854`) message states the fix was applied but does not itself
record a distinct re-verification pass by the reviewer or Coordinator against
the edited text. This review supplies that missing re-verification
independently (§3 below, and the mutation trace in §4) and confirms the fix
holds, so this is not treated as blocking — but it is worth naming as a
process gap for a future amendment: a reviewer's own stated freeze
precondition should be checked off by name, not only inferred from the
committed diff matching the reviewer's suggested text.

## 3. THE CENTRAL QUESTION — do all three checks genuinely call the wrapper, and is CHECK 3 exactly length 3?

Read `reanalyze_v4_selftest.py` in full (518 lines), not the manifest's prose.

- **Import surface.** `import reanalyze_v3 as rv3` (line 75). Grep of the
  entire file for attribute accesses on `rv3` finds exactly four:
  `rv3.SEEDS`, `rv3.NULL_ARM_MIN_PRIMES`, `rv3.c_null_label_comparison_v3`,
  `rv3.git_state`. `rv3.main` never appears. `reanalyze_v3.py` is not edited
  (confirmed §1) and defines `run_synthetic_self_test_v3`
  (GD-10's own defective function) unchanged, but that function is never
  imported, referenced, or called anywhere in `reanalyze_v4_selftest.py`.
- **CHECK 1** (`_run_check1`, lines 118–162): calls
  `rv3.c_null_label_comparison_v3(real_per_prime, null_per_prime,
  null_survivors, rng_seed, min_primes=NULL_ARM_MIN_PRIMES, n_boot=n_boot)`
  directly (line 133) and asserts on `ret["evaluable"]` and
  `ret["c_null_label_control_failure"]` — the function's own returned dict,
  not a hand-computed prediction.
- **CHECK 2** (`_run_check2`, lines 165–243): calls the same function
  directly (line 179) with an unsorted `null_survivors = [7000, 2000, 5000,
  3000]` and asserts on eight fields of the returned dict
  (`evaluable`, `primes_used`, `N_list`, `gamma_null_greedy`,
  `gamma_null_random`, `m_gap_null_ci_lo/hi`,
  `c_null_label_control_failure`).
- **CHECK 3** (`_run_check3`, lines 246–358): calls the same function
  directly (line 275) with `null_survivors = [7000, 2000, 3000]` — **length
  exactly 3**, counted directly from the list literal, matching
  `NULL_ARM_MIN_PRIMES = 3`. No hand-written duplicate of
  `c_null_label_comparison_v3`'s internal cross-dict indexing, `min_primes`
  gate, or `sorted()` step exists anywhere in the file — the only `sorted()`
  calls in the file (lines 183, 279) compute `expected_primes_used` for the
  self-test's own **assertion targets**, not a parallel implementation of the
  function under test's decision logic. Grep for `ols_loglog_fit` and
  `bootstrap_gap_ci` inside `reanalyze_v4_selftest.py` finds them only in
  comments/docstrings — they are never called directly by this file; they are
  invoked exclusively inside `c_null_label_comparison_v3`'s own body, exactly
  as GD-10's repair requires.
- **Entry point.** `main()` (lines 429–517) defines only two `argparse`
  arguments, `--out` and `--self-test-out`. Grep for `open(` in the file finds
  exactly two calls (lines 449, 506), both mode `"w"`, both writing the two
  declared output paths. No `--run-b` flag exists on the parser; no code path
  opens any file for reading.

**Independent re-execution.** I imported `reanalyze_v3` directly in a live
Python session (same module the run imports) and re-called
`c_null_label_comparison_v3` with the exact inputs `reanalyze_v4_selftest.py`
constructs for CHECK 1/2/3 (`rng_seed=20260805`, `n_boot=2000`). Every
returned field reproduced **bit-exactly** what is recorded in
`self_test_v4.json` and `manifest.yaml.result.metrics`:

| field | recomputed (this review) | recorded (`self_test_v4.json`) | match |
|---|---|---|---|
| CHECK2 `gamma_null_greedy` | 0.30000000000000004 | 0.30000000000000004 | exact |
| CHECK2 `gamma_null_random` | 0.8000000000000004 | 0.8000000000000004 | exact |
| CHECK2 `m_gap_null_ci_lo` | 0.49999999999999917 | 0.49999999999999917 | exact |
| CHECK2 `m_gap_null_ci_hi` | 0.500000000000002 | 0.500000000000002 | exact |
| CHECK3 `evaluable` | True | true | exact |
| CHECK3 `gamma_null_greedy` | 0.30000000000000004 | 0.30000000000000004 | exact |
| CHECK3 `gamma_null_random` | 0.8000000000000005 | 0.8000000000000005 | exact |
| CHECK3 `m_gap_null_ci_lo` | 0.5000000000000002 | 0.5000000000000002 | exact |
| CHECK3 `m_gap_null_ci_hi` | 0.5000000000000011 | 0.5000000000000011 | exact |
| CHECK1 `evaluable` / `control_failure` | False / "NOT-EVALUABLE" | false / "NOT-EVALUABLE" | exact |

This is bit-for-bit reproduction against a freshly-imported copy of the
module, not a re-read of the run's own output — the numbers in this run
package are genuine products of actually calling `c_null_label_comparison_v3`,
not fabricated or copied from the CHECK 2 case.

**Analytic re-derivation (independent of the code's own output), per the
launching task's instruction:** for an exact power law `y = N**gamma` (`c=1`,
zero noise), `ols_loglog_fit`'s `gamma = sxy/sxx` reduces algebraically to
`gamma_fit = gamma_true` exactly (up to `float` rounding of `log`/`**`, order
`1e-16`), and any subset/resample of `>=2` distinct-N points on a noiseless
power law recovers the identical `gamma`, so the bootstrap CI must degenerate
to a point at `m_gap_expected = gamma_random - gamma_greedy = 0.5`. This
predicts CHECK 2's and CHECK 3's `gamma_null_greedy≈0.3`,
`gamma_null_random≈0.8`, and `m_gap_null_ci_lo≈m_gap_null_ci_hi≈0.5` — all
confirmed to match the reported/recomputed values to far better than the
`<1e-9` tolerance CHECK 2/3 require.

**Mutation trace, independently re-run against the actual, unchanged
`c_null_label_comparison_v3` code (not merely inherited from the pre-freeze
review):**

```
gate: len(null_survivors) < min_primes   (correct)   vs.   <= min_primes   (mutant), min_primes=3
L=2 (CHECK 1): original True  (NOT-EVALUABLE), mutant True  (NOT-EVALUABLE) -- IDENTICAL, does not distinguish
L=4 (CHECK 2): original False (evaluable),      mutant False (evaluable)     -- IDENTICAL, does not distinguish
L=3 (CHECK 3): original False (evaluable),      mutant True  (NOT-EVALUABLE) -- DIFFERS, distinguishes
```

This reproduces the pre-freeze review's own trace exactly and confirms the
`mutation_precondition_v4` fix genuinely closes the gap: CHECK 3, and only
CHECK 3, discriminates the named off-by-one mutation. The pre-freeze review's
required re-verification (§2 above) is satisfied by this independent trace.

**Verdict on the central question: PASS.** All three checks genuinely call
`c_null_label_comparison_v3` (imported, not duplicated); CHECK 3's
`null_survivors` list has length exactly 3, confirmed by direct count of the
list literal and by re-execution; the numbers reported are genuine,
reproducible outputs of the actual function, not hand-computed or fabricated.

## 4. Entry-point isolation — structural, not merely "not invoked this run"

Per the launching task's instruction to check the whole file, not merely
confirm the flag was unused this run:

- `argparse.ArgumentParser` (line 430) defines exactly two `add_argument`
  calls (`--out`, `--self-test-out`); no third argument, no `--run-b`, no
  other flag naming a file path anywhere on the parser.
- The only two `open()` calls in the entire 518-line file (lines 449, 506)
  are both mode `"w"`, targeting `args.self_test_out` and `args.out` — the two
  paths this run itself specifies as outputs. There is no `open()` call of any
  kind with mode `"r"`, `"rb"`, or default read mode anywhere in the file.
- `reanalyze_v3.main` (the function that requires `--run-b` and
  unconditionally `json.load`s it) is **defined** by the module import (a
  necessary side effect of `import reanalyze_v3 as rv3`) but is never
  **referenced or called** — confirmed by grep for `rv3.main` and for `main(`
  outside this file's own `def main():` definition, both returning zero
  matches.
- `source_access_log.yaml.files_read_this_run: [none]`, cross-checked against
  the code (not merely trusted): this matches the structural absence of any
  read-mode `open()` call.

This is a genuine structural guarantee, not an artifact of this particular
invocation's arguments — the script **cannot** be made to read
`RUN-SSIQ-a85692-b/raw-result.json` short of editing the file's source, since
no CLI surface exists that could name it and no code path opens any input
file. PF-3's fix is correctly and completely implemented.

**Verdict: PASS.**

## 5. ANOM-1 — independent reproduction and assessment of bearing on prior real-data results

### 5.1 Reproducing the artifact directly

I independently reproduced the disclosed floating-point artifact from first
principles, using the transcribed `ols_loglog_fit` formula (`sxx = sum((x -
xbar) ** 2 for x in xs)`, `xbar = sum(xs) / n`) against `x = log(500.0)`
repeated 3 times:

```
x      = 6.214608098422191
xbar   = 6.214608098422192      (x == xbar: False)
sxx    = 2.3665827156630354e-30 (sxx == 0.0: False)
```

This exactly matches `execution_report.yaml`'s ANOM-1 statement
(`sxx = 2.37e-30`, `xbar - log(500.0) ≈ 9.99e-16`). **Confirmed genuine, not
overstated.**

### 5.2 Confirming the artifact is specific to (N=500, repeat-count=3)

Brute-force enumeration (all `3**3 = 27` length-3 index-resample patterns over
`{200, 300, 700}`, and all `4**4 = 256` length-4 patterns over `{200, 300,
500, 700}`) finds **zero** anomalous degenerate-resample misses in either
case — matching `execution_report.yaml`'s own claimed enumeration exactly.
Extending the enumeration myself to every length-3 subset of `{200, 300, 500,
700}` that **includes** 500 confirms the artifact fires **only** for the
degenerate triple `(500, 500, 500)`, regardless of which other two values
accompany it in the subset, and **not** for the degenerate quadruple `(500,
500, 500, 500)` at `n=4`. The artifact is precisely as narrow as disclosed: a
single (value, repeat-count) coincidence in IEEE-754 rounding, not a general
defect in `ols_loglog_fit`.

### 5.3 Confirming the workaround actually avoids it

Re-running `c_null_label_comparison_v3` with `null_survivors = [7000, 2000,
5000]` (i.e. **including** prime 5000/N=500 in a length-3 set) reproduces the
failure mode described: `m_gap_null_ci_lo = 0.0` instead of the
analytically-expected `≈0.5` — an actual, reproducible wrong CI bound caused
by the undetected degenerate resample polluting the bootstrap distribution.
The frozen spec's CHECK 3 construction (`[7000, 2000, 3000]`, excluding
5000/N=500) avoids this and correctly recovers `ci_lo≈ci_hi≈0.5`, confirmed in
§3's table above. **The workaround is genuine and effective, not merely
claimed.**

### 5.4 Bearing on BATCH-004/005/006's real-data results

This is the material question. Two independent facts, both directly
verified against `RUN-SSIQ-a85692-b/raw-result.json` and against
`ols_loglog_fit`'s actual arithmetic, establish that ANOM-1 has **no bearing**
on any prior batch's real-data bootstrap CI:

1. **The real arm's N values are fixed and different from 500.** Read
   `descent_metrics.per_prime` directly: the only four N values that have
   **ever** been used in any real-arm `gamma_greedy`/`gamma_random` fit across
   BATCH-004/005/006 are `{203, 324, 478, 611}` (primes 2437/3889/5737/7333).
   500 never appears. The real arm's bootstrap always resamples with
   replacement at size `n = 4` (the fixed number of real-arm primes, both
   before and after `trapped_exclusion_filter_v3` — the filter, when it
   fires, either keeps all 4 or blocks the run entirely via
   `REAL_ARM_MIN_PRIMES`, never a partial 2-or-3 subset for the real arm).
   Brute-force enumeration of all 256 length-4 resample patterns over `{203,
   324, 478, 611}` (and, separately, over the synthetic `{200,300,500,700}`)
   finds **zero** degenerate-round-trip misses at `n=4` for any of these
   values, including 500 itself (quadrupled). The specific coincidence is
   `(value=500.0, repeat-count=3)` only; it does not recur at `repeat-count=4`
   for 500 or at any repeat-count for 203/324/478/611.
2. **The null arm's bootstrap was never invoked on real data in any prior
   batch.** Before v3, GD-9 documents that `c_null_label_control_failure` was
   a dead-code stub, never computed. In v3 (`RUN-SSIQ-a85692-c`), both arms
   lost all 4 primes to `trapped_exclusion_filter_v3`
   (0 survivors, independently reconfirmed by `VAL-BATCH-006.md` §3), so
   `c_null_label_comparison_v3` hit its `NOT-EVALUABLE` early-return
   (`len(null_survivors)=0 < 3`) and **returned before calling
   `dht.ols_loglog_fit` at all** — confirmed by the control-flow trace in
   `reanalyze_v3.py` lines 160–178 and independently re-verified by
   `VAL-BATCH-006.md` §5. So there is no null-arm real-data bootstrap CI from
   any prior batch that ANOM-1 could have silently corrupted, because none was
   ever computed.

**Conclusion: ANOM-1 is genuine, correctly characterized in scope and
mechanism, effectively worked around in this run, and has no bearing on
BATCH-004/005/006's real-data bootstrap CI results** — those results either
used a fixed real-arm N-set and resample size that never triggers this
coincidence, or (for the null arm) never reached a bootstrap call on real data
at all. This is independently re-derived from raw data and transcribed source
in this review, not accepted from the Executor's own disclosure.

**Verdict: PASS**, with the standing observation (already flagged by the
Executor, correctly not treated as this batch's problem to fix) that
`dht.ols_loglog_fit`'s `sxx == 0.0` degeneracy guard is fragile in principle —
an exact-equality float comparison guarding a mathematical exact-zero
condition — and should be hardened (e.g., an epsilon-relative comparison) in
a future, separately-scoped amendment, since a coincidence of this shape could
in principle recur at other (value, repeat-count) pairs not yet enumerated.

## 6. Diff-list cross-check against `required_artifacts_note`

Read `reanalyze_v4_selftest.py` directly against
`specification_v4.yaml`'s `required_artifacts_note` (not the module's own
docstring paraphrase, and not `execution_report.yaml`'s own claimed
cross-check, independently re-derived here):

- **CHANGED: `run_synthetic_self_test_v3` replaced (functionally) by
  `run_synthetic_self_test_v4`.** Confirmed: `reanalyze_v3.py` is
  byte-for-byte untouched (§1), so `run_synthetic_self_test_v3`'s source still
  exists there unchanged; `reanalyze_v4_selftest.py` defines an independent
  `run_synthetic_self_test_v4` (lines 361–420) that never calls
  `run_synthetic_self_test_v3` and instead calls `c_null_label_comparison_v3`
  directly in all three checks. `execution_report.yaml` discloses this
  precise "functional/dispatch replacement, not source edit" reading
  explicitly rather than silently reconciling the spec's "REPLACED"
  phrasing — an honest, non-blocking clarification, matching this campaign's
  standing discipline (cf. `VAL-BATCH-006.md` §8's identical style of
  cross-check).
- **NEW entry point/CLI mode, structurally cannot accept `--run-b`.**
  Confirmed §4 above.
- **Does not read `RUN-SSIQ-a85692-b`'s raw-result.json, does not re-call
  `trapped_exclusion_filter_v3` on real data, does not touch
  `RUN-SSIQ-a85692-c`'s archived outcome.** Confirmed: `files_read_this_run:
  [none]`; grep for `trapped_exclusion_filter_v3` inside
  `reanalyze_v4_selftest.py` finds zero occurrences (transitively importable
  via `rv3.trapped_exclusion_filter_v3` but never referenced); grep for
  `RUN-SSIQ-a85692-c` inside the file finds zero occurrences.
- **`c_null_label_comparison_v3` imported unchanged; `dht.ols_loglog_fit`/
  `dht.bootstrap_gap_ci` invoked only inside it; `v1c.apply_decision_rule`
  never invoked.** Confirmed §3 above (grep for `def
  c_null_label_comparison_v3`, `def ols_loglog_fit`, `def bootstrap_gap_ci`
  inside `reanalyze_v4_selftest.py` all return zero — none is redefined or
  shadowed).
- **`compute_delta_e_v2.py` never imported or invoked.** Confirmed: grep for
  `compute_delta_e_v2` inside `reanalyze_v4_selftest.py` returns zero matches.
- **New run id `RUN-SSIQ-a85692-d`; a/-b/-c and v1/v2/v3 spec files stay
  frozen.** Confirmed §1.

**Verdict: PASS.** No discrepancy found between the frozen diff list and the
code as actually written and run.

## 7. Executor's workaround — legitimate exercise of the spec's stated freedom?

`specification_v4.yaml`'s CHECK 3 text specifies only the **length** of
`null_survivors` ("EXACTLY `NULL_ARM_MIN_PRIMES=3`") and the general
construction ("as in CHECK 2" — two exact power laws, no `N` key in the null
arm). It does not name which 3 of the 4 CHECK-2 primes must be selected. The
Executor's choice to exclude prime 5000 (N=500) is therefore within the
spec's own stated freedom, not a narrowing of what the check tests: CHECK 3's
required assertions (`evaluable is True`, and (ii)–(iv) matching the known
analytic values to `<1e-9`) are unweakened, the boundary-length property
(`len(null_survivors)=3`, which is what actually discriminates the named
mutation, per §3's trace) is preserved exactly, and the substitution changes
nothing about *which gate* is being tested — only *which three synthetic
primes* populate it. `execution_report.yaml`'s own PD-2 entry states this was
"made BEFORE this run's own artifacts were produced... not selected post-hoc
to force a passing result on this run's own required-check data," and this is
consistent with the artifact timeline: ANOM-1 is disclosed as discovered
during implementation (via a separate brute-force script, not one of the
three required checks), and the *chosen* CHECK 3 construction is the one that
avoids the artifact, not one that happens to produce a passing number despite
it. §5.3 above independently confirms that including N=500 would have
produced a wrong CI bound (`ci_lo=0.0` instead of `≈0.5`), so this is not a
tolerance dodge — it is avoidance of a genuine numerical defect in a
dependency, disclosed rather than silently routed around.

**Verdict: PASS.** Legitimate exercise of stated freedom, not an undisclosed
narrowing.

## 8. Overclaim / premature-closure check

- `manifest.yaml.validity_reason` and `execution_report.yaml.executor_assessment.note`
  both state the scope explicitly and narrowly: "No conclusion is drawn here
  about whether `c_null_label_comparison_v3` is 'validated' or 'correct' in
  any sense beyond these three specific checks passing on this specific
  synthetic construction — that judgement, and any further action on ANOM-1,
  belongs to the Coordinator and independent reviewers." This is the correct
  scope: three passing synthetic checks establish that the wrapper's
  cross-dict indexing, min-primes gate, and sort step behave correctly on
  hand-constructed inputs with known analytic answers — they do **not**
  establish that the wrapper behaves correctly on real, non-degenerate
  descent data (no such data currently clears the `>=3`-null-arm-survivors
  floor; `RUN-SSIQ-a85692-c`'s `DATA-UNAVAILABLE-BLOCKED` outcome is
  unchanged and untouched by this run, confirmed §1/§6), nor do they say
  anything about whether a delta_E-gradient exists (`H-SSIQ-36e970`'s
  prediction remains untested by this batch, as by BATCH-006).
- Grep across every artifact in this run package for overclaiming language
  ("fully validated," "GD-9 is fixed," "validated on real data") finds zero
  matches. `real_data_source` is stated as the literal string `"NONE"` in
  both `raw-result.json` and `manifest.yaml.inputs.parameters`.
- `certificate.kind: none` is correctly declared, with a reason consistent
  with `docs/claims-and-verification.md`: no discrete log, no factor-base
  relation, no isogeny instance is claimed solved.
- The receipt's own commit message states the two flagged items are
  "Recorded VERBATIM AND NOT ENDORSED" — this review's independent checks
  (§3–§7 above) now upgrade both from "not endorsed" to "independently
  confirmed."

**Verdict: PASS.** No overclaim found. The distinction between "the wrapper's
own internal logic is now exercised by a genuine, discriminating test" and
"the wrapper is validated against real, non-degenerate data" (still absent)
is stated plainly and repeatedly, not buried.

## 9. Null-object-control framing (docs/inventor-protocol.md §3)

No statistical signal (correlation, bias, gamma estimate) is reported from
real data anywhere in this run — this is a pure code-validation self-test on
hand-constructed synthetic inputs, not a statistical measurement, so the
"does the quantity decay as the destroying parameter increases" check does
not apply to this run's own output in the way it would to a real-data claim.
The synthetic CHECK 2/3 `c_null_label_control_failure=True` outcomes are
stated, expected properties of the constructed examples (`m_gap_expected=0.5
> 0` by deliberate construction), not claims about any null object drawn from
real data, and the artifacts do not present them as such — consistent with
`VAL-BATCH-006.md` §10's identical finding for v3's synthetic self-test. No
artifact tell found; nothing to flag beyond what §5/§8 already establish.

## 10. Infrastructure / budget sanity

Total measured wall-clock `0.05396s` against a `60s` budget (`specification_v4.yaml
budget.wall_clock_seconds_per_run`), `ulimit -v 1048576` (1 GiB) never
approached (not instrumented, but the process completed in ~54ms performing
only in-memory arithmetic on ≤4-point data), single invocation, no
infrastructure failures, no prior attempts, exit code 0 (per `command.txt`).
`stdout.log`'s two printed lines match `raw-result.json`/`self_test_v4.json`
exactly; `stderr.log` is empty (confirmed both by content and by hash — the
canonical empty-file SHA-256). No anomaly beyond the disclosed ANOM-1, which
is a data-construction/dependency-arithmetic finding, not an infrastructure
failure.

**Verdict: PASS.**

---

## Findings

- **F-1 [confirmed, not blocking].** GD-10 is genuinely fixed: all three
  required checks in `run_synthetic_self_test_v4` call
  `c_null_label_comparison_v3` directly, read its own return value, and the
  new CHECK 3 (length exactly `NULL_ARM_MIN_PRIMES=3`) is independently
  confirmed, by re-running the actual mutation trace, to be the one and only
  case among the three that distinguishes the off-by-one `min_primes`
  mutation named in `mutation_precondition_v4`. This closes the exact gap
  GD-10 named, one layer recursively deeper than GD-9's own repair.
- **F-2 [confirmed, not blocking].** ANOM-1 is genuine, precisely
  characterized, and independently reproduced by this review from first
  principles (both the artifact itself and its narrow scope — `(N=500,
  repeat-count=3)` only). It has **no bearing** on any of BATCH-004/005/006's
  real-data bootstrap CI results, for two independently verified reasons: the
  real arm's N-set (`{203,324,478,611}`) and fixed resample size (`n=4`) never
  trigger it, and the null arm's bootstrap was never invoked on real data in
  any prior batch (dead code before v3; `NOT-EVALUABLE` early-return in v3).
- **F-3 [informational, non-blocking].** `dht.ols_loglog_fit`'s `sxx == 0.0`
  degeneracy guard is an exact float-equality check guarding a
  mathematical-exact-zero condition, and is therefore fragile in principle to
  recurrence at other (value, repeat-count) coincidences not yet enumerated.
  Already flagged by the Executor for a future, separately-scoped hardening
  (e.g. an epsilon-relative comparison); correctly not treated as in scope for
  this narrow, one-change amendment. Recorded here so it is not lost.
- **F-4 [informational, non-blocking, process note].** The pre-freeze
  review's own stated freeze precondition — an explicit re-verification of
  the length-3 fix's discriminating power before `frozen_at` — is not
  separately recorded as having been re-run between the draft-fix commit and
  the freeze commit; this review supplies that re-verification independently
  (§2–§3) and confirms it holds, so this is not blocking, but a future
  amendment's freeze commit should name the specific re-verification step by
  ID when a pre-freeze review makes one an explicit precondition.
- **F-5 [confirmed, not blocking, inherited limitation, unchanged from
  BATCH-006/EV-SSIQ-028c9f].** This batch, like BATCH-006, supplies **zero
  runtime evidence on real, non-degenerate data** that
  `c_null_label_comparison_v3`'s fit-and-bootstrap branch behaves correctly —
  only that the wrapper's own control flow is now genuinely exercised and
  correct against hand-constructed synthetic inputs with known analytic
  answers. Any future citation of this batch's outcome as "GD-9/GD-10 both
  fully resolved" must carry this qualifier: code-level and
  discriminating-synthetic-test correctness are now established; real-data
  runtime validation remains absent, unchanged since BATCH-006.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a run
executed exactly as its frozen v4 contract specifies. Every independently
checkable claim in this package was re-derived from the transcribed source of
the imported functions, from live re-execution against the actual
`c_null_label_comparison_v3`/`ols_loglog_fit` code, or from direct
control-flow/structural tracing — not accepted from the manifest's prose, the
Executor's own diff-list cross-check, or the pre-freeze review's own numbers —
and every one reproduced exactly or to far better than its stated tolerance:
the 10 declared path hashes (§1), the contract-freeze binding (§2), all three
checks' genuine wrapper calls and CHECK 3's exact length-3 construction (§3,
including bit-exact re-execution and an independently re-run mutation trace),
the entry point's structural (not merely incidental) inability to read real
data (§4), ANOM-1's genuineness, precise scope, and lack of bearing on any
prior real-data result (§5, independently re-derived by brute-force
enumeration and direct re-execution, not accepted from the Executor's
disclosure), the diff-list's function-level accuracy (§6), the legitimacy of
the CHECK 3 data-construction workaround (§7), and the absence of any
overclaim (§8).

It is admitted **with the condition**, carried forward and extended from
BATCH-006's own `ADMIT-WITH-CONDITIONS` (`EV-SSIQ-028c9f`), that any future
ledger evidence or decision record citing this batch's outcome must state
precisely what is now established and what is not: **GD-10 is fixed and
independently confirmed** — the required synthetic self-test now genuinely
exercises `c_null_label_comparison_v3`'s own cross-dict indexing, min-primes
gate (at the exact boundary that discriminates the named mutation), and sort
step, reading the function's own return value throughout, with no
hand-written duplicate logic anywhere in the test. **GD-9's wrapper remains
code-correct and now discriminating-synthetic-test-correct, but still
real-data-runtime-unvalidated** (F-5) — no citation of this batch may drop
that qualifier. **ANOM-1 is a genuine but narrowly-scoped floating-point
artifact in a frozen dependency, correctly worked around in this run, and
independently confirmed to have no bearing on any of BATCH-004/005/006's real
bootstrap CI results** (F-2) — this closes the specific concern the receipt's
`coordinator_precommit_checks` flagged for independent review.

This report establishes that `RUN-SSIQ-a85692-d` is admissible evidence of
exactly what it measured: `c_null_label_comparison_v3`'s own internal wiring
is correctly implemented and is now genuinely exercised by a test with real
discriminating power against the specific mutation class GD-10 named. It
establishes nothing about whether a delta_E-gradient exists, nothing about
`H-SSIQ-36e970`'s real-arm prediction, and nothing about
`c_null_label_comparison_v3`'s behavior on real, non-degenerate descent data —
those remain exactly as untested as `VAL-BATCH-006.md` found them.

```yaml
validation_report:
  id: VAL-BATCH-007
  task_id: TASK-20260805-aeb1ed
  run_ids: [RUN-SSIQ-a85692-d]
  reviewed_commit: a925cf30eadb65f636f06c95ee83cbc02073f857
  reviewed_commit_parent: 0b15e854644f243b59ee7debfd4aba7b19eb544a
  artifact_checks:
    - {check: path_sha256_recompute, scope: "all 10 declared paths", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "11 changed files = 10 declared artifacts + receipt itself"}
    - {check: v1_v2_v3_artifacts_and_runs_a_b_c_untouched, result: PASS, detail: "git diff --stat 0b15e854 a925cf30 against every v1/v2/v3 path and RUN-a/-b/-c returns empty"}
    - {check: contract_frozen_before_run, frozen_commit: 0b15e854, run_code_commit: 0b15e854, result: PASS, detail: "manifest.yaml.code.commit equals the freeze commit exactly, no intervening commit"}
    - {check: required_artifacts_present, result: PASS, detail: "all 10 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: check1_evaluable_and_control_failure, reported: "False / NOT-EVALUABLE", recomputed_by_reexecution: "False / NOT-EVALUABLE", result: "EXACT MATCH"}
    - {metric: check2_gamma_null_greedy, reported: 0.30000000000000004, recomputed_by_reexecution: 0.30000000000000004, expected_analytic: 0.3, result: "BIT-EXACT MATCH, |diff from analytic| ~4e-17 << 1e-9"}
    - {metric: check2_gamma_null_random, reported: 0.8000000000000004, recomputed_by_reexecution: 0.8000000000000004, expected_analytic: 0.8, result: "BIT-EXACT MATCH"}
    - {metric: check2_m_gap_null_ci_lo_hi, reported: "[0.49999999999999917, 0.500000000000002]", recomputed_by_reexecution: "[0.49999999999999917, 0.500000000000002]", expected_analytic: "degenerate point at 0.5", result: "BIT-EXACT MATCH"}
    - {metric: check3_evaluable, reported: true, recomputed_by_reexecution: true, result: "EXACT MATCH"}
    - {metric: check3_gamma_and_ci, reported: "gamma_greedy=0.30000000000000004, gamma_random=0.8000000000000005, ci=[0.5000000000000002,0.5000000000000011]", recomputed_by_reexecution: "identical", result: "BIT-EXACT MATCH"}
    - {metric: check3_null_survivors_length, reported: 3, recomputed_by_direct_count: 3, method: "counted [7000, 2000, 3000] literal directly in source", result: MATCH}
    - {metric: mutation_min_primes_offbyone_discrimination, method: "independently re-traced len(null_survivors)<min_primes vs <=min_primes at L=2,3,4 against the actual unchanged c_null_label_comparison_v3", result: "L=2 and L=4 identical under both rules (do not discriminate); L=3 differs (False vs True) -- CHECK 3 alone discriminates, reproducing the pre-freeze review's own trace independently"}
    - {metric: anom1_sxx_at_N500_repeat3, reported: 2.3665827156630354e-30, recomputed_from_first_principles: 2.3665827156630354e-30, method: "xbar=sum([log(500.0)]*3)/3; sxx=sum((x-xbar)**2 for x in xs), evaluated directly, independent of the run's own code", result: "EXACT MATCH, confirms sxx != 0.0"}
    - {metric: anom1_scope_specificity, method: "brute-force enumeration of all 27 length-3 and 256 length-4 index-resample patterns over {200,300,500,700} and over the real arm's actual N-set {203,324,478,611}", result: "artifact fires ONLY for the degenerate triple (500,500,500) at repeat-count exactly 3; zero anomalies at repeat-count 4 for any value including 500, and zero anomalies anywhere for {203,324,478,611}"}
    - {metric: anom1_workaround_effectiveness, method: "re-ran c_null_label_comparison_v3 with null_survivors=[7000,2000,5000] (including N=500 at length 3)", result: "reproduces the disclosed failure (ci_lo=0.0 instead of ~0.5); CHECK 3's actual construction [7000,2000,3000] avoids it and recovers ci_lo~ci_hi~0.5, confirming the workaround is genuine and necessary"}
  control_checks:
    - {control: all_three_checks_call_wrapper_directly, result: "CONFIRMED", detail: "grep + direct reading confirms rv3.c_null_label_comparison_v3 is called at lines 133, 179, 275; no hand-written duplicate of its cross-dict indexing, min-primes gate, or sorted() logic exists anywhere in the file; the only sorted() calls compute the self-test's own expected-value targets, not a parallel implementation"}
    - {control: check3_boundary_length_exactly_3, result: "CONFIRMED", detail: "null_survivors=[7000,2000,3000] counted directly; independently re-traced to be the unique length among the three checks that discriminates the min_primes off-by-one mutation"}
    - {control: entry_point_structural_isolation, result: "CONFIRMED", detail: "argparse defines only --out/--self-test-out; the only two open() calls in the file are both mode w targeting those two paths; reanalyze_v3.main (which requires --run-b) is imported-but-never-called, confirmed by grep for rv3.main and bare main( returning zero matches outside this file's own definition"}
    - {control: anom1_genuine_and_correctly_scoped, result: "CONFIRMED", detail: "independently reproduced sxx=2.3665827156630354e-30 from first principles; independently confirmed via brute-force enumeration that the artifact is specific to (N=500, repeat-count=3) and does not recur at repeat-count=4 for any value in either the synthetic or real N-sets"}
    - {control: anom1_no_bearing_on_prior_real_data, result: "CONFIRMED", detail: "real arm's fixed N-set {203,324,478,611} and fixed resample size n=4 never trigger the artifact (zero anomalies across all 256 length-4 patterns, independently enumerated); null arm's bootstrap was never invoked on real data in any prior batch (dead stub before v3; NOT-EVALUABLE early-return in v3, confirmed by VAL-BATCH-006.md sec5 and independently re-confirmed here)"}
    - {control: check3_data_construction_workaround_legitimate, result: "CONFIRMED", detail: "spec text specifies only the survivors-list LENGTH for CHECK 3, not which 3 of 4 primes; excluding N=500 preserves every required assertion and the boundary-length property unweakened; independently confirmed the alternative (including N=500) would produce a genuinely wrong CI bound, so this is defect-avoidance, not a tolerance dodge"}
    - {control: v3_v2_v1_and_prior_runs_untouched, result: PASS, detail: "git diff --stat 0b15e854 a925cf30 against every prior spec/impl/run path returns empty"}
    - {control: no_overclaim, result: PASS, detail: "grep across all run artifacts for overclaiming language ('fully validated', 'GD-9 is fixed', 'validated on real data') returns zero matches; real_data_source stated as literal NONE in both raw-result.json and manifest.yaml"}
  heuristic_validation_checks: []
  cost_model_checks:
    - {check: budget_realism, result: PASS, detail: "measured wall-clock 0.05396s against 60s budget, three orders of magnitude under budget, consistent with specification_v4.yaml's own estimate"}
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: confirmed-not-blocking, summary: "GD-10 is genuinely fixed: all three checks call c_null_label_comparison_v3 directly and CHECK 3 (length exactly 3) is independently confirmed to be the unique check that discriminates the named min_primes off-by-one mutation"}
    - {id: F-2, severity: confirmed-not-blocking, summary: "ANOM-1 is genuine, precisely scoped to (N=500, repeat-count=3), and independently confirmed to have no bearing on any of BATCH-004/005/006's real-data bootstrap CI results, for two independently verified reasons (real arm's fixed N-set/resample-size never triggers it; null arm's bootstrap was never invoked on real data before this synthetic self-test)"}
    - {id: F-3, severity: informational, summary: "dht.ols_loglog_fit's sxx==0.0 exact-equality degeneracy guard is fragile in principle to other unenumerated (value, repeat-count) coincidences; already flagged by the Executor for future hardening, correctly out of scope for this amendment"}
    - {id: F-4, severity: informational-process-note, summary: "The pre-freeze review's own stated freeze precondition (re-verify the length-3 fix's discriminating power before freeze) is not separately recorded as re-run before the freeze commit; this review supplies that re-verification independently and confirms it holds"}
    - {id: F-5, severity: confirmed-not-blocking-inherited-limitation, summary: "Unchanged from BATCH-006 (EV-SSIQ-028c9f): zero runtime evidence exists on real, non-degenerate data that c_null_label_comparison_v3's fit-and-bootstrap branch behaves correctly; only code-level and discriminating-synthetic-test correctness are established by this batch or any prior one"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, the pre-freeze reviewer, and every prior reviewer in this lineage; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "This report makes no claim about whether a delta_E-gradient exists, about lever L4's status, or about H-SSIQ-36e970's real-arm prediction; RUN-SSIQ-a85692-c's DATA-UNAVAILABLE-BLOCKED outcome is unchanged and untouched by this batch."
    - "Real-data runtime validation of c_null_label_comparison_v3's fit-and-bootstrap branch remains absent (F-5); any future citation of GD-9/GD-10 as fully resolved must carry this qualifier."
    - "Toy scale throughout, inherited unchanged from H-SSIQ-36e970.scope_ceiling: the synthetic CHECK 1/2/3 data uses hand-picked N values (200-700) unrelated to any real curve/prime scale; nothing here transfers to cryptographic scale or is claimed to."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-007/reviews/VAL-BATCH-007.md
```
