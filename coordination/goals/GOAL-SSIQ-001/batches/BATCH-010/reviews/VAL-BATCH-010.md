# VAL-BATCH-010 — Validator review of RUN-SSIQ-a85692-g (EXP-SSIQ-a85692 v7, H-SSIQ-36e970, delta_E label-permutation null control, formalized)

**Reviews the Coordinator-committed snapshot at commit `4fd1425a`**
(receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/archives/TASK-20260806-9ad6b5-receipt.yaml`,
parent `6bdaecb8dc2851126744a6608e14b003e7dc4916`). Nothing in this report
edits `specification_v7.yaml`, any raw artifact,
`delta_e_permutation_null_control_v7.py`, or any ledger record.
`specification_v7.yaml` (424 lines, the frozen contract) was read in full,
including both `pfN_summary` blocks (PF-1 through PF-10) and both
pre-freeze review rounds' verdict text; `delta_e_permutation_null_control_v7.py`
(601 lines, the single new implementation file) was read in full and
compared directly, function by function, against `trapping_diagnostic_v5.py`'s
own inline coverage-assertion / graph-rebuild / `is_structural_local_min`
logic (lines 161–244), not accepted from the run's own self-report; the
complete `RUN-SSIQ-a85692-g` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`,
`permutation_null_control.json`) was read directly; and, for template
conformance, `VAL-BATCH-009.md`. Every independently-computable claim below
was **re-executed live**: two independent fresh re-runs of the actual
committed script from a clean scratch directory (not the archived run
directory), a from-scratch recomputation of every reported summary
statistic directly from the raw 1000-trial lists for all four primes (not
sampled to one), an empirical RNG-determinism differentiator (persistent
instance vs. fresh-seed-per-trial), and a direct monkeypatch test forcing
the "materially disagrees" branch to fire to confirm it does not gate
null-trial computation.

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
    policy-resolved identifier. Same standing condition as every prior
    review in this lineage.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer, the pre-freeze reviewers, and the
    Coordinator's own precommit re-derivation. Per AGENTS.md "Goal closure
    quorum," this alone can never satisfy a closure quorum, and this record
    does not itself close GOAL-SSIQ-001 or change H-SSIQ-36e970's status.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `git merge-base --is-ancestor 4fd1425a HEAD` →
  reachable (single parent `6bdaecb8...`, matching `log --pretty=%P`).
- **Parent:** matches the receipt's declared `parent_sha` exactly.
- **Path set:** `git diff --stat 6bdaecb8 4fd1425a --` returns exactly the
  10 declared artifacts (1 new implementation file + 9 run files) plus the
  receipt itself (`commit_sha: null` / `commit_sha_note`, committed inside
  the commit it describes — same self-referential pattern as prior
  batches), all as pure additions (13819 insertions, 0 deletions, 0
  modifications to any pre-existing file). **Byte-for-byte set match, no
  extra file, nothing missing.**
- **Hashes:** recomputed `sha256(git show 4fd1425a:<path>)` independently
  for a 5-file sample spanning implementation code and run artifacts
  (`delta_e_permutation_null_control_v7.py`, `manifest.yaml`,
  `permutation_null_control.json`, `raw-result.json`, `stderr.log`) —
  **0 mismatches, all 5 exact matches**, including `stderr.log`'s canonical
  empty-file SHA-256.
- **Untouched-files check, independently re-run:** `git diff --stat 6bdaecb8
  4fd1425a --` against every file named in `required_artifacts_note`'s
  UNCHANGED list (`descent_hitting_time.py`, `ols_hardened.py`,
  `trapping_diagnostic_v5.py`, `descent_walk_hardened.py`,
  `funnel_structure_diagnostic_v6.py`, `run_batch009.py`,
  `compute_delta_e.py`, `compute_delta_e_v2.py`, `reanalyze_v3.py`,
  `reanalyze_v4_selftest.py`, `build_isogeny_graph.py`),
  `EXP-SSIQ-58b642`'s three frozen modules
  (`descent_hitting_time.py`, `build_isogeny_graph.py`,
  `calibration_synthetic.py`), and every prior run directory
  `RUN-SSIQ-a85692-{a,b,c,d,e,f}` — returns **empty**. `git status
  --porcelain` on the current worktree is also clean.
- **`code.commit` binding:** `manifest.yaml.code.commit`
  (`6bdaecb8dc2851126744a6608e14b003e7dc4916`) equals this snapshot's own
  `parent_sha` exactly — the run executed against the precise commit that
  froze `specification_v7.yaml`, with no intervening commit between freeze
  and execution start.

**Verdict: PASS.** The receipt is a genuine, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v7.yaml` is frozen at commit `6bdaecb8` ("EXP-SSIQ-a85692
  v7 FROZEN (two pre-freeze review rounds)"), a direct descendant of
  `cebbc300` (round-1 revised draft) and `6d9f7e55` (original amendment
  draft) — two review rounds precede the freeze in the commit graph,
  matching `pre_freeze_review.status: REVIEWED` and both `round1`/`round2`
  report paths, both present and non-empty
  (`RT-PREFREEZE-EXP-SSIQ-a85692-v7.md`, 49721 bytes;
  `RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md`, 60574 bytes).
- Round 1's two blocking findings (PF-1: the coverage assertion had been
  silently narrowed to a bare cardinality count; PF-2: the "materially
  disagrees" branch's failure-handling scope was unstated) are both
  confirmed fixed by direct code read (§3, §5 below), independently of the
  freeze note's own claim.

**Verdict: PASS.**

## 3. Claim: the two-part coverage/graph-rebuild check is genuinely restored, not merely reported passing

Read `delta_e_permutation_null_control_v7.py`'s `rebuild_and_verify`
(lines 186–266) side by side with `trapping_diagnostic_v5.py`'s own inline
procedure in `run_diagnostic_for_prime` (lines 161–208), not from
`permutation_null_control.json`'s own report. The two are line-for-line
structurally identical: same `archived_n_vertices`/`archived_n_resolved`
pinned-value guard; same `g, seed_info = build_graph_for_prime(p, seed)`
call; same `degseq = big.degree_sequence_check(g)` / `vertex_count_match =
bool(n_built == archived_n_vertices)` graph-rebuild half; same
`vertex_set = set(vertices)` / `matched_vertices = [v for v in delta_map if
v in vertex_set]` / `coverage_assertion_pass = bool(n_matched ==
archived_n_vertices)` coverage half (**never** `archived_n_resolved`, per
PF-1's own explicit prohibition); same
`graph_rebuild_independently_verified_correct = bool(degseq_pass and
vertex_count_match and coverage_assertion_pass)` combination formula. This
is a genuine, code-verified restoration of v6's own two-part check, not a
re-derivation that merely produces the same JSON fields.

**Verdict: PASS — independently confirmed by direct source comparison, not
by trusting the JSON's own `coverage_assertion_pass`/`graph_rebuild_verification` fields.**

## 4. Claim: `is_structural_local_min`/`depth(v)` formulas match the frozen text exactly, with the disclosed PF-4 broadening

`local_min_and_depth` (lines 133–156) computes `is_min = bool(delta_map[v]
<= m)` and `depth = m - delta_map[v]` where `m = min(delta_map[u] for u in
adjacency[v])` — identical to `trapping_diagnostic_v5.py`'s own inline
formula at line 234 (`is_min = bool(delta_map[v] <= min(nbr_deltas))`).
Grep confirms no `delta_map[v] > 1` (basin-eligibility) restriction appears
anywhere in the v7 module, matching PF-4's disclosed broadening to every
structural local minimum, not only the basin-eligible subset v6 used.

**Verdict: PASS.**

## 5. Independent C-REPRO: two fresh re-executions from clean scratch directories

Re-ran the actual committed script (`delta_e_permutation_null_control_v7.py`,
unmodified, at its committed content) **twice**, each into a fresh scratch
directory outside the run's own artifact tree, using the same recorded
command and the same read-only input
(`RUN-SSIQ-a85692-b/raw-result.json`). Both re-executions exited 0 in
~4.2s. Comparison against the archived `permutation_null_control.json`:

| check | result |
|---|---|
| `archived == repro1` (full dict-equal, Python `==`) | **True** |
| `archived == repro2` (full dict-equal) | **True** |
| `repro1 == repro2` | **True** |
| `sha256(archived permutation_null_control.json)` | `6e4f6ddc...600e035` |
| `sha256(repro1 permutation_null_control.json)` | `6e4f6ddc...600e035` — **identical** |
| `sha256(repro2 permutation_null_control.json)` | `6e4f6ddc...600e035` — **identical** |

`permutation_null_control.json` contains no time-varying fields, so this is
a **byte-for-byte identical file**, not merely a value-level match — the
strongest form of C-REPRO confirmation available. Spot-checked all four
primes' full 1000-element `null_depth0_fractions` lists element-by-element
(not merely the summary statistics): **all four lists dict-equal, exact,
first-5-elements shown and matched in the raw computation log.**
`raw-result.json`'s non-time-varying fields (all metrics, seeds, per-prime
summaries) also match exactly; only `started_utc`/`finished_utc`/
`wall_clock_seconds`/`git.commit`(during re-execution the tree carries this
snapshot's own additional history, expected) differ, as expected for any
fresh invocation.

**Verdict: PASS. C-REPRO independently confirmed** — not merely accepted
from the Executor's own self-reported second invocation (which this report
also independently reproduces the outcome of), by two fully independent
fresh executions of this validator's own.

## 6. RNG-determinism claim, verified directly in code and empirically differentiated

Read the actual permutation loop (lines 344–360): `rng =
random.Random(permutation_seed)` is constructed **once**, immediately
before the `for _trial in range(n_trials):` loop, and `rng.shuffle(values)`
is called on this **same** `rng` object inside the loop body on every
iteration — never reconstructed or reseeded mid-prime. This matches the
frozen contract's text exactly: "a SINGLE, FRESHLY-CONSTRUCTED
random.Random(20260806) instance, constructed once per prime... advanced
sequentially across all 1000 trials for that prime via repeated
.shuffle() calls on the SAME instance, never re-seeded or reconstructed
mid-prime."

To confirm this distinction has empirical teeth (not just that the code
reads correctly), wrote a standalone script reproducing the graph rebuild
and the first 5 trials for p=2437 two ways: (a) the spec-compliant
persistent-instance pattern, and (b) a spec-violating alternative that
reconstructs `random.Random(20260806)` fresh inside the loop before each
`.shuffle()` call (the exact failure mode the task named as
"still deterministic but would NOT match the contract"). Result:

- **Persistent-instance first 5 trials:** `[0.5405405405405406,
  0.5432098765432098, 0.5, 0.6363636363636364, 0.4805194805194805]` —
  **exactly matches** the archived `permutation_null_control.json`'s own
  first 5 values for p=2437.
- **Fresh-seed-per-trial first 5 trials:** `[0.5405405405405406,
  0.5405405405405406, 0.5405405405405406, 0.5405405405405406,
  0.5405405405405406]` (degenerate, constant — the same permutation drawn
  every time) — **does not match** the archived data past the first
  element.

This is a positive empirical confirmation, not merely a code-reading
inference: the archived data is consistent with the persistent-RNG
implementation and inconsistent with the alternative the frozen contract
explicitly rules out.

**Verdict: PASS — RNG determinism claim independently confirmed, both by
direct code read and by empirical differentiation against the ruled-out
alternative.**

## 7. Summary statistics recomputed from raw values, all four primes (not sampled to one)

Recomputed mean, median, min, max, and population standard deviation
(divide by `N_TRIALS`, per PF-3/PF-10) directly from
`permutation_null_control.json`'s own raw 1000-element
`null_depth0_fractions` lists, independently of `summary_stats()`'s own
code:

| p | mean (reported / recomputed) | median | min | max | population SD |
|---|---|---|---|---|---|
| 2437 | 0.5820914702 / 0.5820914702 | 0.5844155844 / 0.5844155844 | 0.3835616438 / 0.3835616438 | 0.7692307692 / 0.7692307692 | 0.0613823117 / 0.0613823117 |
| 3889 | 0.3743707586 / 0.3743707586 | 0.3725490196 / 0.3725490196 | 0.1818181818 / 0.1818181818 | 0.5412844037 / 0.5412844037 | 0.0586885052 / 0.0586885052 |
| 5737 | 0.3634890236 / 0.3634890236 | 0.3648648649 / 0.3648648649 | 0.2127659574 / 0.2127659574 | 0.5131578947 / 0.5131578947 | 0.0483932937 / 0.0483932937 |
| 7333 | 0.4547406666 / 0.4547406666 | 0.4559585492 / 0.4559585492 | 0.3144329897 / 0.3144329897 | 0.5906976744 / 0.5906976744 | 0.0392298155 / 0.0392298155 |

All values match to full float precision (exact `==` in Python, not
"in the right ballpark") for all four primes. Also independently
recomputed `null_exceeds_or_equals_real_count` directly from the raw list
(`sum(1 for v in null_depth0_fractions if v >= real_depth0_fraction)`):
**0 for all four primes**, matching the archived and reported figure
exactly.

**Verdict: PASS.**

## 8. REAL_DEPTH0_FRACTION, independently reproduced

Both fresh re-executions (§5) reproduce `real_depth0_fraction == 1.0` on
all four primes with `n_structural_local_min` = 95/132/194/287 — exactly
matching `RUN-SSIQ-a85692-f`'s own already-archived ANOM-1 figures, as the
frozen contract's EXPECTED RESULT states, and as the Coordinator's own
precommit check independently verified. `materially_disagrees_with_expectation`
is `False` on every prime in this reproduction, consistent with the
archived record.

**Verdict: PASS.**

## 9. PF-2 fix ("materially disagrees" branch does not gate null-trial computation) — confirmed by forced-failure test, not only by code read

This did not occur on the real four primes (§8), so the frozen contract's
own failure-handling branch for this case was never exercised by the
archived run. Read the code path directly first: after computing
`materially_disagrees` and constructing the `anomaly` dict, `run_for_prime`
proceeds **unconditionally** into the `# ---- (4) NULL_DEPTH0_FRACTIONS`
section — there is no `if materially_disagrees: continue/return/skip`
anywhere in the function. To confirm this structurally rather than by
inference alone, imported the actual committed module and monkeypatched
`EXPECTED_REAL_DEPTH0_FRACTION` to `0.42` (guaranteed to never match the
measured 1.0), forcing `materially_disagrees_with_expectation = True` for
p=2437, then called `run_for_prime` directly:

```
materially_disagrees: True
anomaly is not None: True
n null trials computed: 25          # (n_trials=25 used for speed)
null_summary_statistics present: True
```

The forced mismatch produces the disclosed anomaly **and** the full,
complete null-trial computation and summary statistics — exactly as PF-2
requires ("this DOES NOT HALT OR SKIP that prime's NULL_DEPTH0_FRACTIONS
computation").

**Verdict: PASS — PF-2's fix independently confirmed via a forced-failure
unit test against the actual committed code, not only by reading that no
skip branch exists.**

## 10. Overclaim / premature-closure check

- `manifest.yaml.validity_reason`, `execution_report.yaml.executor_assessment`,
  and the receipt's `coordinator_precommit_checks` all state the results
  plainly, correctly restate `OBJECTIVE_BOUNDARY` (this is a control, not a
  test of `H-SSIQ-36e970`'s real-arm prediction, gates no decision rule),
  and explicitly decline to draw a mechanism conclusion about ANOM-1.
- `certificate.kind: none` is correctly declared with a reason consistent
  with `docs/claims-and-verification.md`.
- Grep across the full run package, the implementation file, and the
  receipt for claim-adjacent overreach ("detects a gradient," "confirms
  L4," "validated the mechanism," "proves H-SSIQ," "discrete log
  found/solved") returns **zero matches**.
- `scale_qualifier: "toy; N (graph size) in [203, 611]"` is present in both
  `raw-result.json` and `permutation_null_control.json`; nothing here is
  presented as crypto-scale.

**Verdict: PASS. No overclaim found.**

## 11. Null-object-control framing (docs/inventor-protocol.md §3)

This run's own reported quantity — the null distribution's summary
statistics (mean 36.3%–58.2% across the four primes) — **is itself the
null-object control** for the real data's own 100%-depth0 anomaly (ANOM-1,
independently confirmed in `VAL-BATCH-009.md` §5). No further null-object
control is owed by this run: the "destroying parameter" here is exactly
the label permutation itself, and the frozen contract's own reported
statistic (`null_exceeds_or_equals_real_count = 0/1000` on every prime)
is the correct form of decay check — the real data's 100% figure sits
**above every one of the 4000 permuted trials**, i.e., permutation (the
parameter meant to destroy any genuine spatial structure) does destroy the
100% figure, driving it down to a 36–58% mean, consistently on every
prime. This is the canonical "decays when it should" pattern the protocol
requires, correctly measured and archived here (not merely asserted).
This amendment's own text (PF-6, the "next required control" for a
*different*, deferred question — whether ANOM-1 reflects genuine
graph-spatial structure vs. a `delta_E`-search-procedure RNG confound) is
correctly scoped as future work, out of this amendment's own zero-new-
search-cost boundary, and is not conflated with this control's own,
already-satisfied null-object requirement.

**Verdict: PASS — the required null-object control is present, and its
governing statistic (permuted-null means well below the real 100%, on
every prime) is independently reproduced in §5–§8 above.**

## 12. Infrastructure / budget sanity

Measured wall-clock `4.114069700241089s` against a `900s` budget, roughly
two orders of magnitude under budget; `ulimit -v 2097152` (2 GiB) never
approached. This review's own two re-executions measured `~4.2s`–`4.25s`,
consistent with the archived figure. `environment.json`'s recorded
`python_version` (`3.11.15`) matches this review's own interpreter exactly.
No infrastructure failure occurred on this batch (unlike RUN-SSIQ-a85692-f's
disclosed PD-2, which was a first-attempt implementation error, correctly
not treated as evidence).

**Verdict: PASS.**

---

## Findings

- **F-1 [confirmed, not blocking].** The two-part coverage assertion /
  graph-rebuild verification (PF-1's restoration) is independently
  confirmed a genuine, line-for-line structural duplicate of
  `trapping_diagnostic_v5.py`'s own inline procedure by direct source
  comparison, not by trusting the run's own reported
  `coverage_assertion_pass`/`graph_rebuild_verification` fields.
- **F-2 [confirmed, not blocking].** `is_structural_local_min`/`depth(v)`
  independently confirmed identical to the frozen formula, with the
  disclosed PF-4 broadening (no basin-eligibility restriction) verified by
  direct grep of the actual module, not only by the module's own
  docstring claim.
- **F-3 [central finding, confirmed, not blocking].** C-REPRO is
  independently confirmed by **two** fully independent fresh
  re-executions of the actual committed script (not the Executor's own
  self-reported second invocation), producing a byte-for-byte identical
  `permutation_null_control.json` (matching sha256) on both occasions,
  including all four primes' full 1000-element raw trial lists.
- **F-4 [confirmed, not blocking].** The RNG-determinism claim (single,
  persistent `random.Random(20260806)` instance per prime, never
  reseeded mid-prime) is independently confirmed both by direct code read
  and by an empirical differentiator against the ruled-out
  fresh-seed-per-trial alternative, which this review confirms produces a
  materially different (degenerate) trial sequence that does **not**
  match the archived data.
- **F-5 [confirmed, not blocking].** All four primes' reported summary
  statistics (mean, median, min, max, population SD) and
  `null_exceeds_or_equals_real_count` independently recomputed directly
  from the raw 1000-element lists — exact match (Python `==`, full float
  precision), all four primes, not sampled to one.
- **F-6 [confirmed, not blocking].** `REAL_DEPTH0_FRACTION == 1.0` on all
  four primes, matching `RUN-SSIQ-a85692-f`'s own archived ANOM-1 figures
  exactly, independently reproduced by this review's own re-execution.
- **F-7 [confirmed, not blocking].** PF-2's fix (the "materially
  disagrees" branch never gates or skips null-trial computation) is
  independently confirmed by a forced-failure unit test against the
  actual committed code (not merely by reading that no skip branch
  exists): forcing the mismatch condition still produced the full,
  complete null-trial computation and summary statistics.
- **F-8 [confirmed, not blocking].** Every file required untouched is
  independently confirmed byte-for-byte unchanged by this review's own
  `git diff --stat`, and the worktree itself is clean.
- **F-9 [informational, non-blocking].** This control's own governing
  statistic (permuted-null means well below the real 100% figure, on
  every prime, `null_exceeds_or_equals_real_count = 0/1000` throughout) is
  itself the null-object-control decay pattern `docs/inventor-protocol.md`
  §3 requires and is correctly reported and archived — flagged here
  explicitly since the task instructions asked this be checked directly
  rather than assumed.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run executed exactly as its frozen v7 contract (after two pre-freeze
review rounds) specifies. Every independently checkable claim in this
package was re-derived from two fully independent fresh re-executions of
the actual committed code (byte-for-byte reproduction of the archived
`permutation_null_control.json`, confirmed by sha256), from direct
side-by-side source comparison against `trapping_diagnostic_v5.py`'s own
inline logic, from an empirical RNG differentiator against the ruled-out
alternative, and from a forced-failure unit test of PF-2's fix — not
accepted from the manifest's prose, the Executor's own self-reported
second invocation, or the Coordinator's own precommit numbers. All sampled
path hashes match and the full declared-path set is exact (§1); the
contract-freeze binding is correct, following two review rounds (§2); the
two-part coverage/graph-rebuild check and the local-min/depth formulas are
genuine, code-verified duplicates of the frozen text (§3–4); **C-REPRO is
independently confirmed**, not merely accepted from the Executor's own
self-report (§5); the RNG-determinism claim is independently confirmed
both by code read and by empirical differentiation (§6); all summary
statistics recompute exactly from raw data, all four primes (§7);
REAL_DEPTH0_FRACTION reproduces exactly (§8); PF-2's failure-handling fix
is independently confirmed via a forced-failure test, not only inferred
from the absence of a skip branch (§9); no overclaim was found (§10); the
required null-object-control decay pattern is present and correctly
reported (§11); and infrastructure/budget figures are sane and reproduced
(§12).

It is admitted **with the condition**, extending this lineage's standing
practice, that any future ledger evidence or decision record citing this
batch's outcome must state precisely what is now established and what is
not: **this run formally archives, as an immutable, independently
re-executable record, the delta_E label-permutation null control first
informally run in BATCH-009** — REAL_DEPTH0_FRACTION is 1.0 on every prime
(matching RUN-SSIQ-a85692-f's own ANOM-1 exactly), and the null
distribution's means (36.3%–58.2%) sit well below the real figure on every
one of 4000 trials (`null_exceeds_or_equals_real_count = 0/1000`
throughout). Per this amendment's own repeatedly-restated
`OBJECTIVE_BOUNDARY`, this is a **control, not a test of H-SSIQ-36e970's
real-arm prediction**, does not gate any decision rule, and does not
resolve the funnel-structure mechanism question (DEC-20260806-498531 item
(2), explicitly deferred). It also, by the frozen contract's own
admission (PF-6, named and deferred, not attempted here), **cannot
distinguish genuine graph-spatial structure from a `delta_E`-computation
procedure confound** (the shared, sequentially-advancing per-vertex RNG in
`compute_delta_e.py`'s search) — any future amendment crediting ANOM-1's
persistence under permutation to genuine mathematical structure, rather
than this narrower "coarse alphabet + graph regularity vs. destroyed
spatial structure" distinction, needs that separately-named, not-yet-run
control.

```yaml
validation_report:
  id: VAL-BATCH-010
  task_id: TASK-20260806-08f905
  run_ids: [RUN-SSIQ-a85692-g]
  reviewed_commit: 4fd1425aeaf1bef7624eff78893a6d5de3bd9dd5
  reviewed_commit_parent: 6bdaecb8dc2851126744a6608e14b003e7dc4916
  artifact_checks:
    - {check: path_sha256_recompute, scope: "5-file sample of 10 declared paths (implementation + run artifacts)", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "11 changed files = 10 declared artifacts + receipt itself; all pure additions (13819 insertions, 0 deletions); diffed programmatically against declared_paths, exact set match"}
    - {check: v1_v6_and_prior_runs_untouched, result: PASS, detail: "git diff --stat 6bdaecb8 4fd1425a against every UNCHANGED-listed implementation file, EXP-SSIQ-58b642's three frozen modules, and RUN-SSIQ-a85692-a through -f returns empty; worktree also clean"}
    - {check: contract_frozen_before_run, frozen_commit: 6bdaecb8, run_code_commit: 6bdaecb8, result: PASS, detail: "manifest.yaml.code.commit equals the freeze commit exactly, no intervening commit; freeze followed two pre-freeze review rounds in the commit graph, both report files present and non-empty"}
    - {check: required_artifacts_present, result: PASS, detail: "all 10 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: c_repro_fresh_reexecution_x2, method: "two independent fresh re-executions of the actual committed delta_e_permutation_null_control_v7.py into clean scratch directories, not the Executor's own self-reported second invocation", reported: "Executor's own dict-equal self-report, not independently re-executed prior to this review", recomputed: "byte-for-byte identical permutation_null_control.json (sha256 6e4f6ddc...600e035) on both fresh re-executions, including all four primes' full 1000-element raw trial lists", result: "EXACT MATCH, independently reproduced from scratch"}
    - {metric: rng_determinism_persistent_instance_vs_fresh_seed_per_trial, method: "direct code read (single random.Random constructed once per prime, outside the trial loop) plus an empirical differentiator implementation of the ruled-out fresh-seed-per-trial alternative", result: "persistent-instance reproduction exactly matches archived first-5 trial values for p=2437; fresh-seed-per-trial alternative produces a degenerate, non-matching sequence -- confirms the archived data is consistent only with the contract-specified RNG usage"}
    - {metric: null_summary_statistics_all_four_primes, method: "recomputed mean/median/min/max/population_sd directly from the raw null_depth0_fractions lists in permutation_null_control.json, independent of summary_stats()'s own code", reported: "p2437 mean=0.582091 median=0.584416 min=0.383562 max=0.769231 sd=0.061382; p3889 mean=0.374371 median=0.372549 min=0.181818 max=0.541284 sd=0.058689; p5737 mean=0.363489 median=0.364865 min=0.212766 max=0.513158 sd=0.048393; p7333 mean=0.454741 median=0.455959 min=0.314433 max=0.590698 sd=0.039230", recomputed: "identical to full float precision (Python ==) for all four primes", result: "EXACT MATCH, independently reproduced, all four primes, not sampled"}
    - {metric: null_exceeds_or_equals_real_count_all_four_primes, method: "recomputed directly from raw null_depth0_fractions list against real_depth0_fraction, all four primes", reported: "0/1000 on every prime", recomputed: "0/1000 on every prime", result: "EXACT MATCH"}
    - {metric: real_depth0_fraction_all_four_primes, method: "reproduced by two independent fresh re-executions", reported: "1.0 on all four primes (95/95, 132/132, 194/194, 287/287)", recomputed: "identical, both re-executions", result: "EXACT MATCH, matches RUN-SSIQ-a85692-f's own archived ANOM-1 figures"}
    - {metric: pf2_materially_disagrees_branch_does_not_gate_null_trials, method: "forced-failure unit test: monkeypatched EXPECTED_REAL_DEPTH0_FRACTION to 0.42 (guaranteed mismatch) and called run_for_prime directly against the actual committed module", result: "materially_disagrees_with_expectation=True, anomaly populated, AND all 25/25 requested null trials computed with full summary statistics -- PF-2's fix confirmed structurally, not only by absence-of-skip-branch inference"}
    - {metric: coverage_and_graph_rebuild_formula_identity, method: "direct side-by-side source comparison of rebuild_and_verify (v7 module, lines 186-266) against trapping_diagnostic_v5.py's own inline run_diagnostic_for_prime procedure (lines 161-208)", result: "line-for-line structurally identical: same guard, same degree_sequence_check/vertex_count_match half, same vertex_set/matched_vertices/coverage_assertion_pass half (never archived_n_resolved), same combination formula"}
    - {metric: wall_clock_sanity, reported: 4.114069700241089, recomputed_by_reexecution: "~4.2s-4.25s across two independent re-runs", result: "consistent, two orders of magnitude under the 900s budget"}
  control_checks:
    - {control: two_part_coverage_graph_rebuild_check_genuine_restoration, result: CONFIRMED, detail: "direct side-by-side source read against trapping_diagnostic_v5.py's own inline logic, not the run's own self-report"}
    - {control: is_structural_local_min_depth_formula_and_pf4_broadening, result: CONFIRMED, detail: "identical formula confirmed by direct read; PF-4 broadening (no basin-eligibility restriction) confirmed by grep of the actual module"}
    - {control: c_repro_independently_reexecuted, result: CONFIRMED, detail: "two fresh, independent re-executions produce a byte-for-byte identical permutation_null_control.json (sha256 match), not merely value-level agreement"}
    - {control: rng_single_persistent_instance_not_fresh_seed_per_trial, result: CONFIRMED, detail: "direct code read plus empirical differentiator against the ruled-out alternative implementation"}
    - {control: pf2_failure_handling_does_not_gate_null_trials, result: CONFIRMED, detail: "forced-failure unit test against the actual committed module, not inference from source alone"}
    - {control: null_object_control_present_and_reported, result: CONFIRMED, detail: "the null distribution (36.3%-58.2% mean across primes) is itself the required decay-under-destroying-parameter check against the real data's 100% figure; null_exceeds_or_equals_real_count=0/1000 on every prime independently reproduced"}
    - {control: v1_v6_and_prior_runs_and_shared_library_untouched, result: PASS, detail: "git diff --stat 6bdaecb8 4fd1425a against every named UNCHANGED path and all prior run directories returns empty"}
    - {control: no_overclaim, result: PASS, detail: "grep across all run artifacts, the implementation file, and the receipt for claim-adjacent overreach returns zero matches; OBJECTIVE_BOUNDARY correctly restated throughout"}
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: confirmed-not-blocking, summary: "Two-part coverage/graph-rebuild check independently confirmed a genuine, line-for-line structural duplicate of trapping_diagnostic_v5.py's own inline logic"}
    - {id: F-2, severity: confirmed-not-blocking, summary: "is_structural_local_min/depth(v) formulas and PF-4's disclosed domain broadening independently confirmed by direct code read and grep"}
    - {id: F-3, severity: confirmed-central-finding-not-blocking, summary: "C-REPRO independently confirmed by two fresh re-executions producing a byte-for-byte identical permutation_null_control.json, not accepted from the Executor's own self-report"}
    - {id: F-4, severity: confirmed-not-blocking, summary: "RNG-determinism claim (single persistent instance per prime) independently confirmed by code read and by empirical differentiation against the ruled-out fresh-seed-per-trial alternative"}
    - {id: F-5, severity: confirmed-not-blocking, summary: "All four primes' summary statistics and null_exceeds_or_equals_real_count recomputed exactly from raw trial lists"}
    - {id: F-6, severity: confirmed-not-blocking, summary: "REAL_DEPTH0_FRACTION=1.0 on all four primes independently reproduced, matching RUN-SSIQ-a85692-f's own archived ANOM-1 figures"}
    - {id: F-7, severity: confirmed-not-blocking, summary: "PF-2's fix (materially-disagrees branch never gates null-trial computation) confirmed by a forced-failure unit test against the actual committed code"}
    - {id: F-8, severity: confirmed-not-blocking, summary: "Every file required untouched is independently confirmed byte-for-byte unchanged; worktree clean"}
    - {id: F-9, severity: informational-non-blocking, summary: "The null distribution's own decay pattern (means well below the real 100% figure on every prime) is itself the null-object-control docs/inventor-protocol.md section 3 requires, correctly reported"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, the pre-freeze reviewers, and the Coordinator's own precommit re-derivation; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "This is a CONTROL per its own repeatedly-restated OBJECTIVE_BOUNDARY: it does not test H-SSIQ-36e970's real-arm prediction, does not gate any decision rule, and does not resolve the funnel-structure mechanism question (DEC-20260806-498531 item (2), explicitly deferred)."
    - "By the frozen contract's own admission (PF-6, named and explicitly deferred, not attempted by this amendment), this control cannot distinguish genuine graph-spatial structure from a delta_E-computation-procedure RNG confound (compute_delta_e.py's shared, sequentially-advancing per-vertex RNG). Any future amendment crediting ANOM-1's persistence under permutation to genuine mathematical structure needs that separately-named, not-yet-run control."
    - "Toy scale throughout, inherited unchanged from H-SSIQ-36e970.scope_ceiling: graph sizes 203-611 vertices; nothing here transfers to cryptographic scale or is claimed to."
    - "This review's recomputation was exhaustive (all four primes, not sampled) for summary statistics, C-REPRO, and the RNG-determinism differentiator, and used targeted forced-failure unit tests (not a full independent from-scratch reimplementation of the entire module) for the PF-2 branch check -- the exhaustive treatment targeted the claims this task explicitly named as most important (C-REPRO, RNG determinism, summary-statistic exactness, PF-2's failure-handling scope)."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/VAL-BATCH-010.md
```
