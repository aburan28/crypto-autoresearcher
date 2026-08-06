# VAL-BATCH-008 — Validator review of RUN-SSIQ-a85692-e (EXP-SSIQ-a85692 v5, H-SSIQ-36e970, GD-11's fix + trapping-mechanism diagnostic)

**Reviews the Coordinator-committed snapshot at commit `a686f170`** (receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/archives/TASK-20260806-bac693-receipt.yaml`,
parent `59cfaf39`). Nothing in this report edits `specification_v5.yaml`, any
raw artifact, `descent_hitting_time.py`, `build_isogeny_graph.py`, or any
ledger record. Everything named in the launching task was read in full, not
sampled: `specification_v5.yaml` (370 lines, the frozen contract) in full,
including both `pfN_summary` blocks; `RT-PREFREEZE-EXP-SSIQ-a85692-v5.md`
(round 1, DO-NOT-FREEZE) and `RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md`
(round 2, FREEZE-WITH-FIXES) in full, with particular attention to PF-6's
original reasoning; `descent_hitting_time.py`'s
`greedy_descent_hitting_time` (lines 179–222) read directly, in full;
`ols_hardened.py`, `gd11_regression_test.py`, `trapping_diagnostic_v5.py`,
`run_batch008.py` (the actual executed code) read directly, in full; the
complete `RUN-SSIQ-a85692-e` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`,
`gd11_regression_test.json`, `bootstrap_gap_ci_v2_regression_test.json`,
`trapping_diagnostic.json`, `trapped_vs_structural_crosscheck.json`);
`goal.yaml`'s GD-11 entry, `EV-SSIQ-87d21a.yaml`, `DEC-20260805-6aa5c2.yaml`
in full; and, for template conformance, `VAL-BATCH-007.md`. Every
independently-computable claim below was **re-executed live** against the
actual frozen code (not re-derived on paper, and not accepted from the
Executor's or reviewers' own numbers), including a full re-run of
`run_batch008.py` end to end and a from-scratch hand-trace of the disputed
counter-example using a fresh Python session that imports only the
frozen, unmodified `descent_hitting_time.py`/`build_isogeny_graph.py`.

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
    lineage has recorded (VAL/RT-BATCH-003 through VAL-BATCH-007,
    RT-PREFREEZE-EXP-SSIQ-a85692[-v2..-v5, -v5-round2]).
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer, both pre-freeze reviewers, and every
    prior reviewer in this lineage; nothing below is corroboration from a
    distinct model. Per AGENTS.md "Goal closure quorum," this alone can
    never satisfy a closure quorum, and this record does not itself close
    GOAL-SSIQ-001 or change H-SSIQ-36e970's status.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `git merge-base --is-ancestor a686f170 HEAD` →
  reachable.
- **Parent:** `git log --pretty=%P -n1 a686f170` → `59cfaf39ea72...`, exactly
  the receipt's declared `parent_sha`. Match.
- **Path set:** `git diff --name-only 59cfaf39 a686f170` returns exactly 17
  files: the 16 declared artifacts plus the receipt itself (which is
  committed inside the commit it describes, per the receipt's own
  `commit_sha: null` / `commit_sha_note`). No extra file, nothing missing.
- **Hashes:** recomputed `sha256(git show a686f170:<path>)` independently
  for all 16 declared paths and compared against the receipt's
  `path_sha256` — **0 mismatches, all 16 exact matches** (including
  `stderr.log`'s hash, the canonical empty-file SHA-256, consistent with an
  empty file, and `trapped_vs_structural_crosscheck.json`, a 6639-line
  file, matched in full, not truncated).
- **v1–v4 artifacts, all prior runs, and shared library code untouched:**
  `git diff --stat 59cfaf39 a686f170 -- experiments/EXP-SSIQ-a85692/specification.yaml
  experiments/EXP-SSIQ-a85692/specification_v2.yaml
  experiments/EXP-SSIQ-a85692/specification_v3.yaml
  experiments/EXP-SSIQ-a85692/specification_v4.yaml
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-c
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-d
  experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py
  experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py`
  returns **empty**. Confirms the Executor's own `git diff --stat HEAD`
  claim in `execution_report.yaml`'s `implementation_commit_note` and the
  receipt's `v1_v4_and_prior_runs_untouched` precommit check.

**Verdict: PASS.** The receipt is a genuine, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v5.yaml` is frozen at commit `59cfaf39`
  ("EXP-SSIQ-a85692 v5 FROZEN (two pre-freeze review rounds)"), itself the
  direct descendant of `203c3e8d` (round-2 review artifact commit),
  `d82be3b4` (revised draft), `62193861` (round-1 review artifact commit)
  — the freeze followed **two** pre-freeze review rounds in the commit
  graph, not the reverse, matching `pre_freeze_review.status: REVIEWED`.
- `manifest.yaml.code.commit = 59cfaf39ea721780b4cddf3d7ac5968a70872b15`
  equals the snapshot's own `parent_sha` exactly: the run executed against
  the precise commit that froze `specification_v5.yaml`, with no
  intervening commit between freeze and execution.
- Round 1 (`RT-PREFREEZE-EXP-SSIQ-a85692-v5.md`) returned **DO-NOT-FREEZE**
  on PF-1/PF-4/PF-5 (bootstrap wiring hollow-fix risk; unspecified
  `delta_map` key-format bridge; vertex-count-only graph-rebuild check).
  Round 2 (`RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md`), independently
  re-tracing all three by direct execution, confirmed them genuinely fixed
  and found one **new** blocking defect, **PF-9** (the coverage
  assertion's required-fix text, inherited verbatim from round 1's own
  prose, named `n_resolved`/`n_vertices` as interchangeable when they are
  different archived quantities — 194/306/460/594 vs 203/324/478/611).
  The frozen `specification_v5.yaml` (read directly) states the corrected
  text: "NAME ONLY n_vertices, NEVER n_resolved" — confirming PF-9 was
  actually applied before freeze, not merely claimed applied.

**Verdict: PASS.**

## 3. PART A — independent reproduction of both required regression tests

### 3.1 `ols_loglog_fit_v2` is genuinely byte-identical except the guard

Diffed the extracted function bodies of `dht.ols_loglog_fit` (lines
104–134) and `ols_hardened.ols_loglog_fit_v2` programmatically (Python
`difflib`, not eyeballed): the only substantive differences are the
function name, an added docstring paragraph, and the single guard line
(`if sxx == 0.0:` → `if max(xs) == min(xs):`). Every other line —
arithmetic, return dict, docstring's first paragraph — is character-for-
character identical. **Confirmed.**

### 3.2 `bootstrap_gap_ci_v2` is a genuinely new function, not an alias

Read `ols_hardened.py` directly: `bootstrap_gap_ci_v2` is a full,
independent `def`, `__all__ = ["ols_loglog_fit_v2", "bootstrap_gap_ci_v2"]`
names exactly two functions, and its resampling loop calls
`ols_loglog_fit_v2(Nb, gb)` / `ols_loglog_fit_v2(Nb, rb)` — this module's
own hardened function, never `dht.ols_loglog_fit` or `dht.bootstrap_gap_ci`
— for **both** per-resample fits (`fg`, `fr`). No `bootstrap_gap_ci_v2 =
dht.bootstrap_gap_ci` alias form exists anywhere (grep-confirmed).
**Confirmed genuinely new, threading the hardened fit through both call
sites, resolving PF-1 as claimed.**

### 3.3 Full re-execution of the actual run

Re-ran the exact recorded command (`ulimit -v 2097152; timeout 900 python3
run_batch008.py --run-dir ./rerun-out --raw-result-b
RUN-SSIQ-a85692-b/raw-result.json`) against the committed code, from a
clean directory. Exit code 0. Every JSON artifact this produced
(`gd11_regression_test.json`, `bootstrap_gap_ci_v2_regression_test.json`,
`trapping_diagnostic.json`, `trapped_vs_structural_crosscheck.json`)
compared field-by-field against the committed run package —
**bit-identical**, including the full 93/138/234/267-entry disagreement
lists in `trapped_vs_structural_crosscheck.json` (compared as Python
objects, `==` True for every prime).

### 3.4 The contrastive claim, independently reproduced from scratch

Constructed the two named anomaly cases directly (not by importing the
Executor's test file) and called the **frozen, unmodified**
`dht.ols_loglog_fit` and the hardened `ols_hardened.ols_loglog_fit_v2` on
identical inputs:

| case | original `dht.ols_loglog_fit` | hardened `ols_loglog_fit_v2` |
|---|---|---|
| N=324, n=3, y=[10,20,30] | did **not** raise; `gamma=-0.5` | raised `ValueError("degenerate design: all N equal")` |
| N=611, n=6, y=[36.0]*6 | did **not** raise; `gamma=0.5` | raised `ValueError` |

Exact match to `gd11_regression_test.json`'s reported values
(`spurious_gamma_if_not_raised: -0.5` and `0.5` respectively). This
independently confirms the headline contrastive claim: the original
guard's `sxx == 0.0` check is a post-summation float-equality test that
does not fire on these genuinely degenerate designs (IEEE-754 rounding
leaves `sxx` a tiny nonzero float), while the hardened guard's direct
input comparison (`max(xs)==min(xs)`) fires correctly on both.

### 3.5 Bootstrap wiring — the fix reaches the actual resampling loop

The full re-execution (§3.3) reproduces
`bootstrap_gap_ci_v2_regression_test.json` exactly:
`bootstrap_gap_ci_v2(N_list=[324]*3, ...)` → `lo=None, hi=None,
n_valid_draws=0/2000` (every one of 2000 degenerate resamples correctly
discarded), while `dht.bootstrap_gap_ci` on the **identical inputs and RNG
seed/state** → `lo=-0.5, hi=0.5, n_valid_draws=2000/2000` (every resample
silently accepted a spurious gap). The `N=611/n=6` case (constructed with
distinct `median_greedy_list=[24.0]*6` / `median_random_list=[36.0]*6` so
the spurious per-resample gap is a genuinely nonzero `0.5`, not a
coincidental cancellation to `0.0`) reproduces identically:
`bootstrap_gap_ci_v2` discards all 2000; the frozen original accepts
`gap=0.5` on all 2000. **This is the direct, code-verified evidence that
the fix reaches `bootstrap_gap_ci_v2`'s own resampling loop, not merely
the standalone function in isolation — the exact call path GD-11 named as
the live risk, and the exact gap PF-1 (round 1) found the original draft's
text left hollow.**

**Verdict on PART A: PASS.** Both required regression tests genuinely hold
up under independent re-execution. The contrastive design is real, not
asserted: the frozen, unmodified original silently produces materially
wrong nonzero gammas on both named anomaly cases, at both the standalone-
function and bootstrap-resampling-loop levels, while the hardened
functions correctly reject them in every case tested.

## 4. PART B, THE CENTRAL QUESTION — independent determination of what `greedy_descent_hitting_time`'s "trapped" flag actually reflects

### 4.1 Reading the frozen function directly

`descent_hitting_time.greedy_descent_hitting_time` (lines 179–222, read
directly, not from any summary): it walks from `start`, taking a
non-backtracking strict-descent step whenever a strictly-smaller-delta
neighbour exists, and returns `trapped: True` (with the sentinel hitting
time) at the **first vertex reached along that walk** — call it `w` — that
has no strictly-smaller-delta neighbour among its (non-backtracking)
candidates. `w` is in general **not** `start`: it is wherever the walk
happens to halt, which can be zero, one, or many steps away from `start`.
The function's return dict (`hitting_time`, `trapped`, `steps`,
`tie_events`, `steps_with_choice`) does **not** include `w` itself — the
walk's terminal vertex is computed internally and discarded.

The function's own docstring invariant ("a strict-descent walk's
predecessor always has strictly greater delta... so it can never be
excluded from a smaller-delta candidate set by the non-backtracking rule")
is a true, mechanically checkable fact about the code (`candidates`
requires `delta_map[v] < cur_delta`; `prev`'s delta is always `>=
cur_delta` by construction, so excluding `prev` from `nbrs` never removes
a genuine candidate). This proves exactly one thing: **"the walk halts at
w" is logically equivalent to "w is a structural local minimum," for `w`
= the walk's own terminal vertex.** It says nothing at all about
`is_structural_local_min(start)` unless `start` happens to equal `w`.

### 4.2 Where PF-6's reasoning (round 1) elides start vs. terminal

Read `RT-PREFREEZE-EXP-SSIQ-a85692-v5.md` §(g) and PF-6 directly. The
review's own trace is the correct mathematical argument, and it states the
conclusion as "the walk is trapped at vertex w ... is exactly equivalent
to 'w is a structural local minimum'" — using `w`, not `start`, in its own
prose. But the review's **required fix**, carried into the frozen
`specification_v5.yaml` text verbatim (`inputs.trapping_mechanism_diagnostic_v5`,
REQUIRED CROSS-CHECK), operationalizes this as: "confirm its own 'trapped'
flag agrees with `is_structural_local_min(start)` for every single vertex
tested." This substitutes `start` for `w` in the operational instruction,
silently treating them as the same vertex — which they are not whenever
the walk takes one or more steps before halting. Round 2's review
independently re-confirmed PF-6 "cost-wise and design-wise" but did not
re-examine this specific substitution; both reviews' compute-performed
logs (checked directly) show neither ever ran `greedy_descent_hitting_time`
against real `delta_map` data during pre-freeze review — the elision was
never exercised until this run.

### 4.3 Independent, from-scratch reproduction of the Executor's counter-example

In a fresh Python session, importing only the frozen, unmodified
`build_isogeny_graph.py` and `descent_hitting_time.py` (not the
Executor's `trapping_diagnostic_v5.py`), I rebuilt prime 2437's graph
(`SEEDS[0]=20260805`) and loaded `RUN-SSIQ-a85692-b`'s archived
`delta_map`:

```
delta_map[(148, 37)] = 5
adjacency[(148, 37)] = [(1617, 1793), (1849, 2359), (1944, 484)]
neighbour deltas = [2, 5, 5]
is_structural_local_min((148, 37)) = False        # 2 < 5
greedy_descent_hitting_time(..., start=(148,37), ...)
  = {'trapped': True, 'steps': 1, 'hitting_time': 10, ...}
```

I then independently hand-simulated the walk's own step logic (not
calling any Executor code) to recover the terminal vertex the frozen
function's return value does not expose:

```
step 1: current=(148,37), delta=5, candidates (delta<5) among non-backtracking
        neighbours = [(1617,1793) delta=2]  ->  move to (1617,1793)
delta_map[(1617,1793)] = 2
adjacency[(1617,1793)] = [(148,37), (1617,644), (1733,789)]
neighbour deltas = [5, 2, 8]
is_structural_local_min((1617,1793)) = True        # 2 <= min(5,2,8)
=> walk halts here (no strictly-smaller-delta neighbour) -- TRAPPED at (1617,1793)
```

This **exactly reproduces** the Executor's disclosed trace, using
independently-written code, a fresh graph rebuild, and no dependency on
`trapping_diagnostic_v5.py`. It directly falsifies the frozen spec's own
"any disagreement is conclusively a bug in this amendment's own code"
framing: `is_structural_local_min(start)` is `False`, the walk's `trapped`
flag is `True`, and both are individually correct — the walk genuinely
halts at `(1617,1793)`, which genuinely is a structural local minimum,
confirming PF-6's actual mathematical claim (about the **terminal**
vertex) while falsifying its **operationalization** (comparison against
the **start** vertex).

### 4.4 Aggregate confirmation — the gap is systematic, not an isolated example

Independently recomputed, for prime 2437, `fraction_structural_local_min`
directly from a from-scratch graph rebuild and the archived `delta_map`:
`95/203 = 0.467980`, exact match to the committed
`trapping_diagnostic.json`. Independently recomputed the rebuilt
per-vertex `greedy_trapped_fraction` for the same prime: `0.837438...`,
**bit-identical** to `RUN-SSIQ-a85692-b`'s archived
`descent_metrics.per_prime["2437"].greedy_trapped_fraction` — independent
confirmation that the graph rebuild reproduces the *original* run's exact
adjacency, not merely a graph of the right size (this rules out an
adjacency-reconstruction bug as an alternative explanation for the
crosscheck failures: the two runs' graphs are identical, verified by a
downstream statistic that is sensitive to any adjacency difference). Since
`0.837 > 0.468`, most walks that end up trapped somewhere do **not** start
at a vertex that is itself a local minimum — this is exactly the
"many-to-one funnelling" PF-8 already anticipated, and it is exactly what
makes the start/terminal substitution fail on the *majority* of vertices,
not a rare edge case. Full re-execution (§3.3) confirms the disagreement
counts (93/203, 138/324, 234/478, 267/611) reproduce bit-exactly.

### 4.5 Conclusion on the central question

**I independently confirm the Executor's PD-SPEC-1 diagnosis.** The frozen
contract's REQUIRED CROSS-CHECK, as literally operationalized, compares
`greedy_descent_hitting_time`'s `trapped` flag against
`is_structural_local_min(start)`. `greedy_descent_hitting_time`'s `trapped`
flag is a property of the walk's **terminal** vertex, which the frozen,
unmodified function's return value does not expose and which differs from
`start` whenever the walk takes at least one step (the common case: only
41–47% of vertices are themselves local minima, per this run's own,
independently-reproduced measurement, while 72–85% of walks end up trapped
somewhere). PF-6's underlying mathematical claim ("trapped at `w`" ⟺ "`w`
is a structural local minimum") is correct and is not what the disagreement
counts refute; what is refuted is the frozen spec's substitution of
`start` for `w` in the cross-check's operational text, and the frozen
spec's own "any disagreement is conclusively a bug in this amendment's own
code" assertion, which does not survive a single hand-traced
counter-example using only unmodified, imported functions. **This is a
specification defect, not an Executor implementation defect and not a
mechanism finding about the descent process itself.**

**A residual question this review flags for the Coordinator, beyond
confirming the diagnosis itself:** this defect passed through **two**
pre-freeze review rounds (round 1 minted PF-6; round 2 re-confirmed "PF-6's
fix... cost-wise and design-wise... unchanged," per its own §(4)) without
either round executing `greedy_descent_hitting_time` against real
`delta_map` data to check the claimed equivalence empirically before
freeze — both rounds accepted the code-identity argument as sufficient and
did not test it, unlike PF-1/PF-4's fixes, which both rounds *did*
independently execute. Whether this warrants a new named defect (GD-12)
against the campaign's specification-authoring/review process — a
pre-freeze review accepting a mathematically-true argument without
checking that its stated operationalization matches the argument's own
variable — is a Coordinator judgement this report does not make, but the
underlying fact pattern (a proof accepted correctly, an operationalization
of it accepted without re-deriving which vertex the proof is actually
about) is independently confirmed here.

## 5. Coverage assertion, graph-rebuild verification, and structural-local-minimum recomputation

- **Coverage assertion (PF-9-corrected):** independently recomputed for
  prime 2437 by loading `RUN-SSIQ-a85692-b/raw-result.json` directly and
  matching `tuple(json.loads(key))`-converted `delta_map` keys against a
  from-scratch graph rebuild's vertex set: `203/203` matched, equal to the
  archived `n_vertices` (203), **not** to `n_resolved` (194) — confirming
  PF-9's fix is genuinely implemented in the executed code, not merely
  stated in the spec text. All four primes pass per the full re-execution
  (§3.3).
- **Graph-rebuild verification:** `degree_sequence_check` passes and
  rebuilt vertex count exactly matches archived `n_vertices` for all four
  primes (independently re-verified for 2437 in §4.4's rebuild). The
  additional, unrequested bit-identical `greedy_trapped_fraction` match
  (§4.4) is a stronger, independent confirmation of adjacency fidelity
  than either M-DEGSEQ or the coverage assertion alone provide.
- **Structural local-minimum fractions:** independently recomputed for
  prime 2437 directly from `delta_map` + rebuilt adjacency (§4.4):
  `95/203 = 0.467980`, exact match. The full re-execution (§3.3)
  reproduces all four primes' fractions
  (0.467980/0.407407/0.405858/0.469722) bit-identically.
- **Neighbour-delta distribution (OBS-B5):** spot-checked prime 2437's
  reported summary (`local_min_vertices`: n=285, mean=3.933,
  `non_local_min_vertices`: n=324, mean=3.994) against the raw
  `trapping_diagnostic.json` payload directly — both distributions present
  in full, summary statistics consistent with the raw per-vertex data
  inspected.

**Verdict: PASS on all four.** Every quantity in this section that this
review recomputed independently reproduced the committed value exactly.

## 6. Diff-list cross-check against `required_artifacts_note`

Checked `required_artifacts_note`'s diff list against the actual code
directly (not `execution_report.yaml`'s own cross-check, independently
re-derived here):

- **NEW: `ols_hardened.py`, two functions.** Confirmed §3.1–3.2:
  `ols_loglog_fit_v2` byte-identical except the guard;
  `bootstrap_gap_ci_v2` a genuinely new function, not an alias, calling
  `ols_loglog_fit_v2` for both fits.
- **NEW: a diagnostic script implementing `trapping_mechanism_diagnostic_v5`,
  importing `build_isogeny_graph.build_graph_bfs`, `degree_sequence_check`,
  and `descent_hitting_time.greedy_descent_hitting_time` unchanged, by
  reference.** Confirmed: `trapping_diagnostic_v5.py`'s import block reads
  `import build_isogeny_graph as big` / `import descent_hitting_time as
  dht`, both unmodified (confirmed §1's untouched-files diff). The PF-4
  key round-trip (`tuple(json.loads(key))`), the PF-9-corrected coverage
  assertion (`n_matched == archived_n_vertices`, grep-confirmed
  `n_resolved` appears only in reporting fields, never in the comparison
  condition), the PF-5/PF-11 graph-rebuild verification, and the PF-6
  exhaustive (full-`for v in vertices:` loop, no sampling) cross-check are
  all present exactly as the spec requires. **One disclosed deviation**
  (not a diff-list gap): PF-6's literal "halt with an explicit error...
  never a silently-reported disagreement count" instruction is not
  honored — the run records the full disagreement list as data instead of
  raising an uncaught exception on the first prime. Disclosed explicitly
  as PD-SPEC-1, not silently reconciled; see §4 and §7 below for this
  review's assessment of that choice.
- **UNCHANGED, NOT MODIFIED list** (`descent_hitting_time.py`,
  `compute_delta_e.py`, `compute_delta_e_v2.py`, `reanalyze_v3.py`,
  `reanalyze_v4_selftest.py`, `build_isogeny_graph.py`): confirmed empty
  diff, §1.
- **NOT RE-RUN** (`RUN-SSIQ-a85692-a/-b/-c/-d`): confirmed empty diff, §1;
  `RUN-SSIQ-a85692-b/raw-result.json` opened read-only only (grep-confirmed
  no `"w"`-mode `open()` targets it anywhere in this batch's code).
- **Two undisclosed-by-`required_artifacts_note`-but-necessary files**
  (`gd11_regression_test.py`, `run_batch008.py`): both disclosed explicitly
  in `execution_report.yaml`'s `new_files_written`, with the same
  disclosure discipline `RUN-SSIQ-a85692-d`'s `reanalyze_v4_selftest.py`
  used (per `VAL-BATCH-007.md` §6, an established pattern in this
  lineage). Not treated as a discrepancy: both fulfil requirements
  `inputs.gd11_fix_v5`/`inputs.trapping_mechanism_diagnostic_v5` state
  explicitly, and neither introduces any numerical logic of its own beyond
  the two implementation modules the note does name.

**Verdict: PASS**, with the one disclosed protocol deviation (PD-SPEC-1's
halt behavior) carried forward to §7/§8, not silently absorbed here.

## 7. The disclosed protocol deviation — was not halting the right call?

PF-6's frozen text requires halting with an explicit, uncaught error on
the **first** disagreement. Executed literally, this would have halted the
process on prime 2437's first checked vertex (very likely — 93/203 of
2437's vertices disagree), destroying the run's ability to produce *any*
of PART B's required artifacts (coverage assertion results, graph-rebuild
verification, structural-local-minimum fractions, neighbour-delta
distributions) on **any** of the four primes, not just the crosscheck
itself.

This review's independent trace (§4.3) establishes that the frozen
instruction's own stated justification for the halt ("any disagreement is
conclusively a bug in this amendment's own code") is false, verified
directly, not merely disputed. Given that, halting the process would not
have surfaced a genuine defect faster or more safely — it would have
destroyed evidence (the coverage assertion, graph-rebuild verification,
and structural statistics, all independently confirmed correct in §5,
have no dependency on PF-6's cross-check outcome and would have been lost
entirely). The Executor's choice — run the check exactly as specified,
record the full per-vertex disagreement list (not merely a count, so a
future re-analysis has everything the halted-run would have lacked),
report `crosscheck_pass=False` honestly, and classify the outcome as a
specification defect requiring Coordinator action rather than either
silently redefining "start" to mean "terminal vertex" or suppressing the
disagreement — is the correct application of AGENTS rule 8 ("unexpected
observations must be recorded, not silently discarded") and is consistent
with this campaign's own standing discipline (GD-6's repair: re-read what
is actually being tested before accepting a decision-rule label).

**Verdict: PASS.** The deviation from PF-6's literal halt instruction is
correctly disclosed, independently justified by this review's own
verification that the instruction's stated reason for existing is false,
and strictly more informative than compliance would have been (a halted
run on prime 2437 alone would have told the Coordinator nothing about
primes 3889/5737/7333, nothing about the structural-local-minimum
statistics, and nothing about which specific vertices disagree).

## 8. Overclaim / premature-closure check

- Every artifact in this run package states the crosscheck failure and its
  classification without softening it: `manifest.yaml.validity_reason`
  states `PART_B_all_primes_crosscheck_pass: false` as a `metrics` field
  (not buried in prose), `executor_assessment.protocol_complete: false`,
  `data_quality: "limited"` (not `"valid"` or `"invalid"` — a deliberate,
  correctly-reasoned middle category, since the *measured* structural
  statistics are independently corroborated correct (§5) while the
  *required* cross-check did not pass).
- The structural local-minimum fractions and the archived
  `greedy_trapped_fraction` are stated explicitly, in every artifact that
  reports both (`trapping_diagnostic.json`'s
  `statistic_distinction_note`, `raw-result.json`'s
  `statistic_distinction_note`, `manifest.yaml`'s `validity_reason`), as
  **different, non-corroborating statistics** — never presented as two
  measurements of the same quantity. This is the correct claim boundary:
  independently confirmed in §4.4, the gap between them (0.47 vs 0.84 for
  prime 2437) is the expected signature of many-to-one funnelling, not a
  discrepancy to be reconciled.
- `objective_boundary` (restated verbatim in every artifact) correctly
  states PART B is a diagnostic, not a claim: it does not test
  `H-SSIQ-36e970`'s real-arm prediction, does not gate any decision rule,
  and does not constitute evidence for or against a computable
  `delta_E`-gradient. No artifact in this package contradicts this
  anywhere — grep across the full run package for claim-adjacent language
  ("detects a gradient," "confirms L4," "validated the mechanism") returns
  zero matches.
- `certificate.kind: none` is correctly declared with a reason consistent
  with `docs/claims-and-verification.md`: no discrete log, no factor-base
  relation, no isogeny instance is claimed solved by either PART A or
  PART B.
- The receipt's own `part_b_exhaustive_crosscheck_reported_FAILING` check
  is labelled `FAIL_HONESTLY_DISCLOSED`, not silently marked `PASS` or
  omitted — the Coordinator's own precommit check correctly did not
  pre-judge this review's finding, framing it as the single most important
  item for independent review, which this report has now supplied.

**Verdict: PASS.** No overclaim found in either part. The single most
consequential finding of this run (PF-6's operational text tests the wrong
vertex) is stated as plainly and prominently as the passing findings, not
minimized.

## 9. Null-object-control framing (docs/inventor-protocol.md §3)

PART A's regression tests are code-correctness checks on hand-constructed
synthetic data with known analytic answers, not statistical measurements
against a null object — the §3 framing does not apply to them in the way
it would to a real-data statistical claim, consistent with
`VAL-BATCH-007.md` §9's identical finding for the prior batch's synthetic
self-test.

PART B's structural-local-minimum fractions (0.41–0.47) are a genuine
statistical measurement on real graph/`delta_map` data, but
`inputs.trapping_mechanism_diagnostic_v5`'s own `OBJECTIVE_BOUNDARY`
explicitly disclaims that this diagnostic tests or bears on
`H-SSIQ-36e970`'s real-arm prediction — no correlation, bias, or excess is
claimed against any destroying parameter here, so no null-object control
is required by the protocol for this specific measurement, and none is
missing that the diagnostic's own stated scope would need. This review
does not treat the fraction-of-local-minima measurement as evidence for or
against a delta_E-gradient, consistent with the run's own framing.

## 10. Infrastructure / budget sanity

Total measured wall-clock `3.086s` against a `900s` budget
(`specification_v5.yaml budget.wall_clock_seconds_per_run`), roughly two
orders of magnitude under budget; `ulimit -v 2097152` (2 GiB) never
approached; this review's own independent re-execution reproduced
`3.17s`–`3.50s` wall-clock across two separate runs, consistent with the
committed `3.086s` and with normal process-to-process variance for
identical, purely-CPU-bound work. Single invocation, no infrastructure
failures, no prior attempts, exit code 0 (`command.txt`). `stdout.log`'s
eleven lines match `raw-result.json`/`manifest.yaml` exactly; `stderr.log`
is empty (confirmed by content and by the canonical empty-file SHA-256).

**Verdict: PASS.**

---

## Findings

- **F-1 [confirmed, not blocking].** PART A's contrastive regression tests
  genuinely hold up: independently re-executed from scratch, both the
  standalone-function claim (original silently returns spurious gammas
  `-0.5`/`0.5` on the two named anomaly cases; hardened version correctly
  raises) and the bootstrap-wiring claim (the hardened
  `bootstrap_gap_ci_v2` discards every degenerate resample; the frozen,
  unmodified original accepts a spurious gap on every one of 2000
  resamples on identical inputs/RNG state) reproduce exactly.
  `ols_loglog_fit_v2` is confirmed byte-identical to the original except
  the single guard line; `bootstrap_gap_ci_v2` is confirmed a genuinely
  new function, not an alias, threading the hardened fit through both
  per-resample calls — GD-11 is genuinely closed by this run.
- **F-2 [central finding, confirmed, classified specification_error, not
  blocking PART A or the diagnostic content].** PART B's REQUIRED
  exhaustive cross-check fails on all four primes
  (93/203, 138/324, 234/478, 267/611), and this review **independently
  confirms** the Executor's PD-SPEC-1 diagnosis: `greedy_descent_hitting_time`'s
  `trapped` flag reflects the walk's **terminal** vertex, which the
  frozen function's return value does not expose, not the **start**
  vertex the frozen spec's operational text compares against.
  Independently reproduced the disclosed counter-example (p=2437, vertex
  (148,37)) from scratch, using only the imported, unmodified functions,
  and independently confirmed via a bit-identical rebuilt-adjacency check
  that the disagreement is not an artifact of graph-rebuild divergence.
  PF-6's underlying mathematical claim (trapped-at-`w` ⟺ `w` is a
  structural local minimum, for `w` = the walk's terminal vertex) is
  correct and not refuted by this finding; what is refuted is the frozen
  spec's substitution of `start` for `w` in the cross-check's operational
  text and its "any disagreement is conclusively a bug" framing.
- **F-3 [informational, non-blocking, process observation].** This defect
  passed through two pre-freeze review rounds without either round
  executing `greedy_descent_hitting_time` against real data to test the
  claimed equivalence empirically — unlike PF-1/PF-4, which both rounds
  did independently execute. Recorded here as a fact pattern; whether it
  warrants a new named defect (GD-12) against the specification-authoring/
  review process is left to the Coordinator, per this task's own framing.
- **F-4 [confirmed, not blocking].** The structural local-minimum
  fractions (0.41–0.47 per prime) are independently recomputed correctly
  from the actual `delta_map` and a from-scratch rebuilt graph for prime
  2437, and the full run's four-prime figures reproduce bit-identically
  under independent re-execution. They are correctly and consistently
  stated, in every artifact that reports both, as a different statistic
  from the archived `greedy_trapped_fraction` (0.72–0.85), not as a
  corroborating measurement — confirmed by this review's own independent
  recomputation of the gap's direction and rough magnitude.
- **F-5 [confirmed, not blocking].** The disclosed protocol deviation
  (not halting on the first disagreement, as PF-6's literal text
  instructs) is the correct choice, independently justified by this
  review's own verification that the halt instruction's stated reason is
  false: halting would have destroyed the coverage-assertion,
  graph-rebuild-verification, and structural-statistic results for all
  four primes, none of which depend on the crosscheck's outcome and all of
  which are independently confirmed correct in this report.
- **F-6 [confirmed, not blocking, inherited limitation].** Consistent with
  `EV-SSIQ-87d21a`'s own `hypothesis_id: null` framing for infrastructure
  work, neither PART A nor PART B bears on `H-SSIQ-36e970`'s real-arm
  prediction, on lever L4's status, or on whether a computable
  `delta_E`-gradient exists. PART B's `objective_boundary` language is
  followed consistently throughout the package, confirmed by this review's
  own grep for claim-adjacent overreach (§8), which found none.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run executed exactly as its frozen v5 contract (after two pre-freeze
review rounds) specifies. Every independently checkable claim in this
package was re-derived from the transcribed source of the imported
functions, from a full live re-execution of `run_batch008.py` against the
actual committed code (bit-identical reproduction of every JSON artifact,
including the full 93/138/234/267-entry disagreement lists), or from an
independent, from-scratch hand-trace using only unmodified imported
functions — not accepted from the manifest's prose, the Executor's own
diff-list cross-check, or either pre-freeze review's own numbers. All 16
declared path hashes match (§1); the contract-freeze binding is correct
and followed two review rounds (§2); PART A's contrastive claim
genuinely holds at both the standalone-function and bootstrap-resampling-
loop levels (§3); and, **most importantly**, this review **independently
confirms the Executor's PD-SPEC-1 diagnosis**: the frozen contract's
required exhaustive cross-check tests the wrong vertex (`start` instead of
the walk's unexposed terminal vertex), a specification defect in the
contract's own operational text (inherited from PF-6's round-1 prose,
re-confirmed but not re-derived in round 2), not a bug in this run's code
and not a negative finding about the descent mechanism itself (§4,
including an independent from-scratch reproduction of the disclosed
counter-example and a bit-identical adjacency-fidelity check ruling out
graph-rebuild divergence as an alternative explanation). The structural
local-minimum statistics themselves are independently recomputed and
correct (§5), and the disclosed decision not to halt on PF-6's literal
instruction is the correct call given that instruction's stated
justification is independently verified false (§7).

It is admitted **with the condition**, extending this lineage's standing
practice (`VAL-BATCH-007.md`'s own condition on GD-11's scope), that any
future ledger evidence or decision record citing this batch's outcome must
state precisely what is now established and what is not: **GD-11 is
genuinely fixed**, independently confirmed at both the standalone and
bootstrap-resampling-loop levels. **PART B's structural local-minimum
measurements (0.41–0.47 per prime) are independently confirmed correct**
and are a diagnostic only, bearing on no hypothesis. **The frozen
contract's own REQUIRED cross-check (PF-6, as operationalized in
`specification_v5.yaml`) is defective**, independently confirmed by this
review through a from-scratch reproduction of the disclosed
counter-example — any successor record must not read the
`crosscheck_pass: false` result as a finding about
`greedy_descent_hitting_time`'s correctness, about the descent mechanism,
or about `H-SSIQ-36e970`; it is a specification-authoring defect requiring
a Coordinator decision on remedy (rescope, drop, or supersede the
cross-check with one that exposes and compares the walk's actual terminal
vertex).

```yaml
validation_report:
  id: VAL-BATCH-008
  task_id: TASK-20260806-3c6363
  run_ids: [RUN-SSIQ-a85692-e]
  reviewed_commit: a686f17026a4e0b5656cd4ed154a16e9c1c0e9bb
  reviewed_commit_parent: 59cfaf39ea721780b4cddf3d7ac5968a70872b15
  artifact_checks:
    - {check: path_sha256_recompute, scope: "all 16 declared paths", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "17 changed files = 16 declared artifacts + receipt itself"}
    - {check: v1_v4_artifacts_prior_runs_and_shared_library_code_untouched, result: PASS, detail: "git diff --stat 59cfaf39 a686f170 against every v1-v4 spec, RUN-a/-b/-c/-d, and descent_hitting_time.py/build_isogeny_graph.py returns empty"}
    - {check: contract_frozen_before_run, frozen_commit: 59cfaf39, run_code_commit: 59cfaf39, result: PASS, detail: "manifest.yaml.code.commit equals the freeze commit exactly, no intervening commit; freeze followed two pre-freeze review rounds in the commit graph"}
    - {check: required_artifacts_present, result: PASS, detail: "all 16 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: ols_loglog_fit_v2_byte_diff_vs_original, method: "programmatic difflib diff of extracted function bodies", result: "only name, added docstring, and the single guard line differ; every other line identical"}
    - {metric: gd11_anomaly_N324_n3, reported: "original gamma=-0.5 (no raise), v2 raises", recomputed_by_reexecution: "identical, from a fresh Python session not importing the Executor's test file", result: "EXACT MATCH"}
    - {metric: gd11_anomaly_N611_n6, reported: "original gamma=0.5 (no raise), v2 raises", recomputed_by_reexecution: "identical", result: "EXACT MATCH"}
    - {metric: bootstrap_gap_ci_v2_vs_original_N324_n3, reported: "v2: lo=hi=None, 0/2000 valid; original: lo=-0.5,hi=0.5, 2000/2000 valid", recomputed_by_full_rerun: "identical", result: "BIT-EXACT MATCH"}
    - {metric: bootstrap_gap_ci_v2_vs_original_N611_n6, reported: "v2: lo=hi=None, 0/2000 valid; original: lo=hi=0.5, 2000/2000 valid", recomputed_by_full_rerun: "identical", result: "BIT-EXACT MATCH"}
    - {metric: full_run_batch008_reexecution, method: "re-ran the exact recorded command against the committed code from a clean directory", result: "exit code 0; every output JSON (gd11_regression_test.json, bootstrap_gap_ci_v2_regression_test.json, trapping_diagnostic.json, trapped_vs_structural_crosscheck.json) bit-identical to the committed run package, including the full 93/138/234/267-entry disagreement lists compared as Python objects"}
    - {metric: counterexample_p2437_vertex_148_37, method: "from-scratch trace using only the imported, unmodified descent_hitting_time.py/build_isogeny_graph.py, independent of trapping_diagnostic_v5.py", reported: "delta_map=5, neighbour deltas [2,5,5], is_structural_local_min(start)=False, walk trapped=True steps=1, terminal vertex (1617,1793) delta=2 is a genuine local min (neighbours [5,2,8])", recomputed: "identical in every field", result: "EXACT MATCH, independently reproduced"}
    - {metric: fraction_structural_local_min_p2437, reported: 0.467980, recomputed_from_scratch: 0.467980, method: "direct computation from a from-scratch graph rebuild and the archived delta_map, independent of trapping_diagnostic_v5.py", result: "EXACT MATCH (95/203)"}
    - {metric: rebuilt_greedy_trapped_fraction_p2437_vs_archived, recomputed: 0.8374384236453202, archived_RUN_a85692_b: 0.8374384236453202, result: "BIT-IDENTICAL, independently confirms adjacency-rebuild fidelity, ruling out graph-divergence as an alternative explanation for the crosscheck disagreements"}
    - {metric: coverage_assertion_p2437, reported: "203/203 matched vs archived n_vertices=203 (never n_resolved=194)", recomputed: "203/203, tuple(json.loads(key)) round-trip independently re-executed", result: "EXACT MATCH, confirms PF-9's fix is genuinely implemented in code, not only stated in spec text"}
    - {metric: wall_clock_sanity, reported: 3.085620880126953, recomputed_by_reexecution: "3.17s and 3.50s across two independent runs", result: "consistent, both roughly two orders of magnitude under the 900s budget"}
  control_checks:
    - {control: ols_loglog_fit_v2_byte_identical_except_guard, result: CONFIRMED, detail: "diffed programmatically; only name, docstring, and the single guard line differ"}
    - {control: bootstrap_gap_ci_v2_genuinely_new_not_alias, result: CONFIRMED, detail: "grep confirms no alias form; independent function calling ols_loglog_fit_v2 for both fg/fr"}
    - {control: contrastive_original_silently_accepts_spurious_gamma, result: CONFIRMED, detail: "independently reproduced -0.5/0.5 spurious gammas from the frozen, unmodified dht.ols_loglog_fit on both named anomaly cases, at both standalone and bootstrap-resampling-loop levels"}
    - {control: PD_SPEC_1_diagnosis_independently_confirmed, result: CONFIRMED, detail: "the walk's 'trapped' flag reflects the TERMINAL vertex reached by the walk, not the START vertex; the frozen spec's REQUIRED CROSS-CHECK compares against is_structural_local_min(START), a different vertex whenever the walk takes >=1 step; independently reproduced via a from-scratch hand-trace of the disclosed counter-example (p=2437, vertex (148,37)) using only unmodified imported functions, and via a bit-identical rebuilt-adjacency check ruling out graph divergence as an alternative explanation"}
    - {control: PF6_underlying_math_claim_correct_operationalization_wrong, result: CONFIRMED, detail: "'trapped at w <=> w is a structural local minimum' is true and mechanically verified for w = the walk's own terminal vertex; the frozen spec's operational text substitutes start for w, which this review traces to round 1's own prose (PF-6 discussion), carried into the frozen contract and re-confirmed but not re-derived by round 2"}
    - {control: coverage_assertion_and_graph_rebuild_pass_all_four_primes, result: CONFIRMED, detail: "independently recomputed for prime 2437 from scratch (203/203 matched against n_vertices, never n_resolved); full re-execution reproduces all four primes' pass status bit-identically"}
    - {control: structural_local_min_fractions_correctly_computed, result: CONFIRMED, detail: "independently recomputed 95/203=0.467980 for prime 2437 from a from-scratch graph rebuild and the archived delta_map; full re-execution reproduces all four primes' fractions bit-identically"}
    - {control: v1_v4_and_prior_runs_and_shared_library_untouched, result: PASS, detail: "git diff --stat 59cfaf39 a686f170 against every prior spec/run path and descent_hitting_time.py/build_isogeny_graph.py returns empty"}
    - {control: no_overclaim, result: PASS, detail: "grep across all run artifacts for claim-adjacent overreach ('detects a gradient', 'confirms L4', 'validated the mechanism') returns zero matches; the crosscheck failure and its classification are stated plainly in machine-readable metrics fields, not buried in prose"}
    - {control: halt_deviation_justified, result: PASS, detail: "PF-6's literal halt-on-first-disagreement instruction's stated justification ('conclusively a bug') is independently verified false; not halting preserved the coverage-assertion, graph-rebuild, and structural-statistic results for all four primes, none of which depend on the crosscheck outcome"}
  heuristic_validation_checks: []
  cost_model_checks:
    - {check: budget_realism, result: PASS, detail: "measured wall-clock 3.086s against 900s budget, two orders of magnitude under budget; independent re-execution reproduced 3.17s-3.50s across two runs, consistent"}
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: confirmed-not-blocking, summary: "PART A's contrastive regression tests genuinely hold up under independent re-execution at both the standalone-function and bootstrap-resampling-loop levels; GD-11 is genuinely closed"}
    - {id: F-2, severity: confirmed-central-finding-not-blocking, summary: "Independently confirmed the Executor's PD-SPEC-1 diagnosis: the frozen contract's REQUIRED cross-check compares the walk's trapped flag against is_structural_local_min(START) when the flag is actually a property of the walk's unexposed TERMINAL vertex; PF-6's underlying math is correct, its operationalization in the frozen spec text is not; classified as a specification defect, not a code bug or mechanism finding"}
    - {id: F-3, severity: informational-process-note, summary: "This defect passed through two pre-freeze review rounds without either round executing greedy_descent_hitting_time against real data to test the claimed equivalence empirically, unlike PF-1/PF-4 which both rounds did execute; whether this warrants a new named defect (GD-12) is left to the Coordinator"}
    - {id: F-4, severity: confirmed-not-blocking, summary: "Structural local-minimum fractions (0.41-0.47) independently recomputed correct from scratch for prime 2437 and bit-identically reproduced for all four primes; correctly and consistently distinguished from the archived greedy_trapped_fraction as a different statistic in every artifact"}
    - {id: F-5, severity: confirmed-not-blocking, summary: "The disclosed decision not to halt on PF-6's literal instruction is correct and independently justified: the halt instruction's own stated reason is verified false, and halting would have destroyed otherwise-independently-confirmed-correct results for all four primes"}
    - {id: F-6, severity: confirmed-not-blocking-inherited-limitation, summary: "Neither part bears on H-SSIQ-36e970's real-arm prediction, lever L4's status, or delta_E-gradient existence; objective_boundary language followed consistently, no overreach found by grep"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, both pre-freeze reviewers, and every prior reviewer in this lineage; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "This report makes no claim about whether a delta_E-gradient exists, about lever L4's status, or about H-SSIQ-36e970's real-arm prediction; PART B is a diagnostic only, per its own objective_boundary, confirmed followed throughout the package."
    - "The frozen contract's REQUIRED cross-check (PF-6, as operationalized) is confirmed defective by this review; any successor citation of this batch's crosscheck_pass:false result must read it as a specification defect, not as a finding about greedy_descent_hitting_time's correctness or about the descent mechanism."
    - "Toy scale throughout, inherited unchanged from H-SSIQ-36e970.scope_ceiling: graph sizes 203-611 vertices; nothing here transfers to cryptographic scale or is claimed to."
    - "This review's own recomputation was exhaustive for prime 2437 (the counter-example prime) and relied on bit-identical full-pipeline re-execution (not independent re-derivation) for primes 3889/5737/7333's specific numeric values; the re-execution used the exact committed code against the exact committed inputs, so it confirms internal consistency and reproducibility but is not a second, independently-written implementation for those three primes."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/VAL-BATCH-008.md
```
