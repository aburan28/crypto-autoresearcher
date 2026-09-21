# VAL-BATCH-011 — Validator review of RUN-SSIQ-a85692-h (EXP-SSIQ-a85692 v8, H-SSIQ-36e970, delta_E independent-RNG probe)

**Reviews the Coordinator-committed snapshot at commit `fcd9deacf8627360d6b69fd3b8ea2c1224175202`**
(receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/archives/TASK-20260806-edeb5a-receipt.yaml`,
parent `2c17b69ec52f636ce894881f9f52fd91d1bff25f`, the commit that froze
`specification_v8.yaml` after three pre-freeze Red Team rounds). Nothing in
this report edits `specification_v8.yaml`, any raw artifact, the frozen v8
implementation, or any ledger record. `specification_v8.yaml` (687 lines,
the frozen contract, including all three `pfN_summary` blocks PF-1–PF-13 and
all three pre-freeze round verdicts) was read in full;
`delta_e_independent_rng_probe_v8.py` (780 lines, the single new
implementation file) was read in full and checked line-by-line against the
frozen contract's exact-formula and exact-construction-step requirements,
not accepted from the run's own self-report; the complete
`RUN-SSIQ-a85692-h` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`,
`probe_delta_e_comparison.json`, `probe_permutation_null_control.json`) was
read directly. Every independently-computable claim below was
**re-executed or recomputed live**: a full, fresh re-run of the actual
committed script from a clean scratch directory (true C-REPRO, not a
self-report), a from-scratch key-by-key diff of the archived
RUN-SSIQ-a85692-b `delta_map` for p=2437 against this run's `new_delta_map`,
a from-scratch recomputation of every reported permutation-null summary
statistic directly from the raw 1000-trial list, and a from-scratch
cross-check of `real_n_structural_local_min=95` against
RUN-SSIQ-a85692-g's own archived `per_prime_summary` for p=2437.

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

- **Commit identity:** `git rev-parse HEAD` at the start of this review
  equals the task's cited commit `fcd9deacf8627360d6b69fd3b8ea2c1224175202`
  exactly; `git status --porcelain` is clean (the worktree is exactly this
  commit, no drift).
- **Parent:** `git log --pretty=%P -1 fcd9deac` = `2c17b69ec52f636ce894881f9f52fd91d1bff25f`,
  matching the receipt's declared `parent_sha` exactly, and that commit's
  own message/diff confirms it is the one that froze `specification_v8.yaml`
  (`git show --stat 2c17b69e`: only `specification_v8.yaml` and the round-3
  pre-freeze report change).
- **Path set:** `git diff --stat 2c17b69e fcd9deac --` returns exactly the
  11 declared artifacts (1 new implementation file + 10 run files) plus the
  receipt itself, all as pure additions (7353 insertions, 0 deletions, 0
  modifications to any pre-existing file). **Byte-for-byte set match, no
  extra file, nothing missing.**
- **Hashes:** recomputed `sha256sum` on all 11 declared artifacts directly
  from the working tree (which is exactly this commit) — **0 mismatches,
  all 11 exact matches** against the receipt's `path_sha256` block,
  including `stderr.log`'s canonical empty-file SHA-256
  (`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
- **`code.commit` binding:** `manifest.yaml.code.commit`
  (`2c17b69ec52f636ce894881f9f52fd91d1bff25f`) equals this snapshot's own
  `parent_sha` exactly — the run executed against the precise commit that
  froze `specification_v8.yaml`, with no intervening commit between freeze
  and execution start.

**Verdict: PASS.** The receipt is a genuine, content-verified record of the
exact bytes reviewed below, and this review reads the named commit directly
(not a working-tree-only artifact).

## 2. Contract-freeze verification

`specification_v8.yaml` is frozen at `2c17b69e` after **three** pre-freeze
Red Team rounds (`RT-PREFREEZE-EXP-SSIQ-a85692-v8.md`,
`-v8-round2.md`, `-v8-round3.md`, all present and non-empty in
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/`). Round 1 found
two blocking defects (PF-1: PART B would crash on any unresolved vertex;
PF-2: mis-citation of the original procedure as `compute_delta_e.py` instead
of `compute_delta_e_v2.py`). Round 2 found a new, independent blocking
defect (PF-9: the F_p-rational "resolve for free" wiring was never a
required construction step, reproducing PF-1's exact failure shape through a
different path). Round 3 re-verified PF-9's fix with a positive safety
argument and found no third blocking path, applying two narrow advisories
(PF-12, PF-13). All of PF-1, PF-2, and PF-9's fixes are independently
re-verified below by direct code read, not trusted from the freeze note's
own prose.

**Verdict: PASS.**

## 3. Claim: the implementation genuinely follows the frozen contract, not merely reports doing so

Read `delta_e_independent_rng_probe_v8.py` function-by-function against
`specification_v8.yaml`'s exact requirements:

- **`derive_per_vertex_seed` formula (exact match required).** Spec:
  `int.from_bytes(hashlib.sha256(("SSIQ-v8-probe:%d:%r" % (base_seed,
  tuple(int(c) for c in vertex))).encode("utf-8")).digest()[:8], "big")`.
  Implementation (lines 151–154):
  `payload = "SSIQ-v8-probe:%d:%r" % (base_seed, tuple(int(c) for c in
  vertex)); digest = hashlib.sha256(payload.encode("utf-8")).digest();
  return int.from_bytes(digest[:8], "big")`. **Byte-for-byte identical.**
  Independently confirmed collision-free over the actual 194-vertex run:
  194 `seed_used` values in `probe_delta_e_comparison.json`, **194 distinct
  values, 0 collisions.**
- **`PER_VERTEX_BUDGET_SECONDS=15.0` as a genuinely fixed constant.** Module
  constant at line 126, passed directly as
  `time_budget_seconds=per_vertex_budget_seconds` to
  `compute_delta_e.two_sided_search` inside the per-vertex loop (lines
  205–208) with no arithmetic on elapsed/remaining time anywhere in the
  call. Read `two_sided_search` itself (`compute_delta_e.py` lines
  177–210): it takes its own local `t0 = time.time()` **at the start of
  each call** and its internal source/target-table time split is derived
  from its own `time_budget_seconds` argument only — no global or
  cross-call state. **Confirmed: every vertex genuinely receives an
  independent, non-shrinking 15.0s budget**, the exact property PF-6's
  falsification design requires. Independently confirmed empirically: 0 of
  194 `per_vertex_records` report `timed_out: true`, and the average
  measured `wall_seconds` (~1.43s/vertex) is far below the 15.0s cap with no
  systematic drift across the loop (spot-checked the first 30 records: no
  vertex-order-dependent trend).
- **PF-9 required construction step.** Lines 192–194: `new_delta_map = {};
  for v in fp_rational: new_delta_map[v] = 1` runs **before** the
  non-F_p-rational search loop begins. Matches `compute_delta_e_v2.py`'s own
  construction exactly, as the frozen spec requires.
- **PF-1/PF-9 gate, checked before PART B runs.** `check_coverage_gate`
  (lines 314–334) computes `gate_pass = bool(actual == expected ==
  ARCHIVED_N_VERTICES)` i.e. `len(new_delta_map) == len(graph["vertices"])
  == 203`, and `main()` (line 621) only calls
  `run_probe_permutation_null_control_v8` `if gate["gate_pass"]:` —
  otherwise it writes the distinct `COVERAGE-SHORTFALL` record and skips
  PART B entirely. Confirmed in the actual artifact:
  `coverage_gate.gate_pass == true`,
  `len_new_delta_map == len_graph_vertices == archived_n_vertices == 203`.
- **PF-12 permutation-trial construction.** `run_probe_permutation_null_control_v8`
  (lines 344–363): a **single** `rng = random.Random(permutation_seed)` is
  constructed once, `base_values = list(new_delta_map.values())` is
  snapshotted once before the trial loop, and each of the 1000 trials takes
  `values = list(base_values)` (a fresh copy of the *same* base multiset),
  calls `rng.shuffle(values)` on the **one persistent** `rng` instance
  (never re-seeded per trial), and builds `permuted_map = dict(zip(vertices,
  values))`. **Matches the frozen contract exactly.**
- **PF-13 JSON-safety convention.** `delta_map_json_safe` (lines 237–240)
  returns `{str(list(k)): v for k, v in delta_map.items()}`, used
  everywhere `new_delta_map` is written to JSON (line 662); every
  vertex-identity-bearing record elsewhere (`per_vertex_records`,
  `value_differs_triples`, `missing_vertices`) nests the vertex as
  `list(v)` inside a dict **value**, never as a raw tuple dict key.
  Confirmed by direct inspection of the actual `probe_delta_e_comparison.json`
  (`new_delta_map` keys are strings like `"[1031, 1095]"`) — no `TypeError`
  risk, no violation found.

**Verdict: PASS.** The implementation is a faithful, exact realization of
the frozen contract on every checked point.

## 4. Independent re-execution (true C-REPRO)

The run only took ~278s, so this was affordable and was actually done, not
skipped. From a clean scratch directory
(`/tmp/.../scratchpad/val_batch011_repro`, outside the repository tree),
ran the exact committed command:

```
ulimit -v 2097152
timeout 3600 python3 experiments/EXP-SSIQ-a85692/implementation/delta_e_independent_rng_probe_v8.py \
  --run-dir <scratch-dir>
```

The re-run completed in 279.51s (vs. the archived 278.50s) with `EXITCODE=0`
and printed `OUTCOME PERSISTS`. A full recursive structural diff of the
re-executed JSON against the archived `RUN-SSIQ-a85692-h` artifacts found:

- **`raw-result.json`**: 5 diffs, all in expected non-deterministic fields
  (`started_utc`, `finished_utc`, `wall_clock_seconds`, and `git.commit`
  /`git.dirty`, which differ only because this re-execution ran from the
  later, now-clean `HEAD` rather than the exact historical dirty-tree state
  at original execution time — an artifact of *when* the re-run was
  launched, not of the computation). **Zero numeric-result differences.**
- **`probe_delta_e_comparison.json`**: 194 diffs, **every single one** is a
  per-vertex `wall_seconds` timing field (confirmed programmatically: 0 of
  194 diffs touch any field other than `wall_seconds`). `new_delta_map`,
  `coverage_gate`, and `comparison_against_archived` are **dict-equal,
  byte-for-byte**, between the two runs.
- **`probe_permutation_null_control.json`**: **0 diffs** — this file,
  containing `real_depth0_fraction`, all 1000 `null_depth0_fractions`, every
  summary statistic, and the `PERSISTS` outcome, is **exactly, bit-for-bit
  identical** between the original run and this independent re-execution.

This is exactly the pattern the task instructions anticipate: genuinely
nondeterministic OS-level timing fields differ, numeric research results do
not. **The run reproduces exactly**, including the full 194-vertex
independently-seeded search outcome and the entire permutation-null
computation.

**Verdict: PASS — true, independent C-REPRO achieved, not merely claimed.**

## 5. Independent re-verification of headline numeric claims

All three recomputed directly from raw JSON, not from any prose summary.

**(a) Archived-vs-new delta_map comparison.** Loaded
`RUN-SSIQ-a85692-b/raw-result.json`'s own
`phase_minus1_real_search["2437"].delta_map` (203 keys) directly, and this
run's own `new_delta_map` (203 keys, from `probe_delta_e_comparison.json`)
directly. `new_keys == archived_keys` (both length 203, symmetric
difference empty), and a key-by-key value diff over the full intersection
found **`n_value_differs = 0`** — confirming the reported
`n_value_differs=0`, `n_value_matches=203` exactly. This includes 194
independently-RNG-searched non-F_p-rational values and 9 trivial
F_p-rational identities (both maps wire these to `1` unconditionally).

**(b) Permutation-null statistics.** Loaded the full 1000-element
`null_depth0_fractions` list from `probe_permutation_null_control.json`
directly. `max(null_depth0_fractions) = 0.7471264367816092` (exact match to
the reported `null_max`). `margin = (1.0 - 0.7471264367816092) * 100 =
25.287356321839084` percentage points (exact match to the reported
`margin_percentage_points`). Checked the pre-registered PERSISTS threshold
from the frozen contract directly against these recomputed numbers:
`1.0 >= 0.95` **and** `25.287... >= 13.1` — both true, so **PERSISTS is the
correct, independently-re-derivable mechanical output of the pre-registered
rule**, not merely a self-reported label. (Independently recomputed
`mean`/`median`/`min`/population-`sd` also match to the reported precision,
modulo negligible last-digit float-summation-order noise in `mean`/`sd`
— not a discrepancy in the underlying data.)

**(c) `real_n_structural_local_min=95` cross-check against RUN-SSIQ-a85692-g.**
Loaded `RUN-SSIQ-a85692-g/raw-result.json`'s own
`delta_e_permutation_null_control_v7.per_prime_summary["2437"]` directly:
`n_structural_local_min: 95` — exact match to this run's own
`real_n_structural_local_min=95`. RUN-g's own artifacts do not additionally
store *which* 203 vertices were local minima (only the aggregate count and
`null_depth0_fractions`), so a literal vertex-identity diff against RUN-g's
own stored data is not possible from its artifacts alone. However, a
**stronger** and directly re-derivable argument is available and was
checked: `depth0_fraction`/`local_min_and_depth`
(`delta_e_permutation_null_control_v7.py` lines 133–178) are **pure
functions of `(delta_map, vertices, adjacency)`** only — confirmed by direct
read of their signatures and bodies, no other state consulted. Since (i)
this run's `new_delta_map` is byte-for-byte identical to
RUN-SSIQ-a85692-b's own archived `delta_map` for p=2437 (0/203 value
differences, per (a) above), and (ii) this run's rebuilt graph
(`vertices`+`adjacency`) is confirmed identical to the archived graph via
the PF-8 graph-identity re-verification (§6 below, same pinned seed, same
degree sequence, same vertex count), the structural-local-minimum **vertex
set** computed on this run's data is mathematically forced to be identical
to the vertex set computed on the archived data — not merely matching by
coincidence of aggregate count.

**Verdict: PASS on all three.**

## 6. Graph-identity re-verification (PF-8)

`probe_delta_e_comparison.json.graph_identity_verification`:
`n_built_vertices=203`, `degree_sequence_check.pass=true`
(`n_degree_ne_3=0`), `vertex_count_match=true`, overall `pass=true`.
Independently cross-checked `n_built_vertices=203` against
`RUN-SSIQ-a85692-b/raw-result.json`'s own
`phase_minus1_real_search["2437"].n_vertices` field directly: **203, exact
match.** The check itself (`verify_graph_identity`, lines 164–175) calls
`big.degree_sequence_check(g)` — genuinely imported, unchanged, from
`build_isogeny_graph.py` (confirmed unmodified via `git diff --stat 2c17b69e
fcd9deac -- .../build_isogeny_graph.py`, empty) — plus a direct
`n_built == archived_n_vertices` comparison, both against the graph rebuilt
from the same pinned `GRAPH_SEED=20260805` every amendment since v5 has
used. This is the full strength of PF-8's own check as the frozen contract
defines it (degree-sequence + vertex-count, relying on the pinned seed's
determinism for genuine structural identity, not a full adjacency-list
diff) — a scope inherited unchanged from v5/v6/v7, not narrowed by v8.

**Verdict: PASS**, both as reported and independently re-derived from the
archived cross-reference.

## 7. PD-1 (required_artifacts_note vs. amendment_scope discrepancy)

`specification_v8.yaml`'s `amendment_scope` PROCEDURE step (1) explicitly
requires re-running the two-part graph-identity verification
(`degree_sequence_check` + vertex-count match) — citing PF-8's own named
fix from round 1 — but `required_artifacts_note`'s shorter "GENUINELY
IMPORTS, UNCHANGED" function list omits `build_isogeny_graph.degree_sequence_check`.
This is a genuine internal inconsistency **within the frozen contract
itself**, introduced by the same freeze process that added the PF-8 fix to
`amendment_scope`'s prose without correspondingly updating
`required_artifacts_note`'s own summary list.

The Executor's resolution — follow `amendment_scope`'s explicit,
more-specific, PF-8-cited instruction and import
`build_isogeny_graph.degree_sequence_check` — is **correct**: both readings
agree on *what to do* (re-run the check), and `amendment_scope` carries a
named, round-1 blocking-adjacent fix while `required_artifacts_note` is a
supporting summary list, not an independent procedural requirement.
Confirmed the import is genuinely present and used
(`import build_isogeny_graph as big`; `big.degree_sequence_check(g)` called
before any search begins), and confirmed `build_isogeny_graph.py` itself is
unmodified. The disclosure is **adequate**: both `manifest.yaml`'s
`validity_reason` and `execution_report.yaml`'s `protocol_deviations[PD-1]`
state the discrepancy, the exact contract text on both sides, and the
resolution rationale in full, rather than silently reconciling it or
picking one reading without note. This does not hide anything — if
anything, surfacing an inconsistency in the frozen contract's own text
(rather than silently working around it) is the correct HONESTY RULE
behavior this campaign has repeatedly required of Executors.

**Verdict: PASS** — correct resolution, adequately disclosed, not a defect
in this run's result.

## 8. Scope, controls, and objective-boundary check

- **Write scope respected.** `git diff --stat 2c17b69e fcd9deac --` shows
  exactly one new implementation file and one new run directory; every
  prior specification (`specification.yaml` through `specification_v7.yaml`),
  every prior implementation module, and every prior run directory
  (`RUN-SSIQ-a85692-a` through `-g`) is untouched (confirmed by the same
  diff, empty for those paths).
- **Certificate discipline.** `certificate.kind: "none"` is stated
  explicitly with a correct reason (pure measurement/probe, no discrete-log
  solve, no factor-base relation, no isogeny instance solved) — consistent
  with `docs/claims-and-verification.md`.
- **Scale honesty.** `scale_qualifier: "toy; N (graph size) = 203; single
  prime p=2437"` and `objective_boundary` are stated in every artifact that
  carries the result, including explicit statements that this is a
  DIAGNOSTIC CONTROL for one prime only, licenses no claim about
  H-SSIQ-36e970, lever L4, or the other three untested primes, and
  transfers no result to cryptographic scale. This matches AGENTS.md rule 7
  and the toy-scale limitation this review records below.
- **Null-object control / decay-under-manipulation check
  (inventor-protocol §3).** This amendment's entire design *is* a
  decay-under-manipulation check applied to PF-6's own confound hypothesis:
  ANOM-1's label-permutation null (PART B, `delta_e_permutation_null_control_v7`,
  genuinely imported unchanged) is the null object; the manipulation meant
  to test whether the real-vs-null margin is an artifact of the *search
  procedure's own* shared, sequentially-advancing RNG is the replacement of
  that RNG with independent, freshly-seeded, fixed-budget draws. If the
  ANOM-1 signal were an artifact of the shared-RNG search procedure, the
  margin should have decayed (or the delta_map itself should have changed)
  under this manipulation. Measured result: the delta_map is byte-identical
  (§5a) and the margin did not decay (25.29pp vs. the archived 23.1pp for
  the same prime) under the manipulation designed to remove the suspected
  confound. This is the correct diagnostic direction and the correct
  measurement for PF-6's own falsification design; **what this single data
  point means for H-SSIQ-36e970 is explicitly out of this Validator's scope
  and is left to the Coordinator and Red Team**, per this task's own
  instruction.

**Verdict: PASS.**

## 9. Limitations (recorded, not treated as defects)

- **Toy scale.** p=2437, N=203 vertices, single prime. No result here
  transfers to cryptographic scale; this is explicitly disclosed in every
  carrying artifact and is restated here per AGENTS.md rule 7.
- **Single prime, single amendment.** This probe deliberately tests only
  p=2437 (the same prime/graph RUN-SSIQ-a85692-b already searched); the
  other three primes (3889, 5737, 7333) remain untested by this probe, per
  the frozen contract's own explicit deferral.
- **Graph-identity check scope.** PF-8's re-verification (degree-sequence +
  vertex-count match against a pinned seed) is not a full adjacency-list
  diff against the archived graph; this is the scope the frozen contract
  (inherited from v5/v6/v7) defines, not a gap this run introduced.
- **PF-4's own disclosure.** The frozen contract itself discloses that the
  archived baseline's budget-shrinking confound component was very likely
  never binding (100% coverage used only ~7.9% of a fresh 3600s aggregate
  pool at the time p=2437 was processed), so this probe's discriminating
  power is concentrated in the RNG-sharing half of PF-6's confound, not the
  budget-shape half. This Validator did not independently re-derive that
  claim (it rests on RUN-SSIQ-a85692-b's own already-validated archived
  data, outside this task's re-verification scope) but notes it is stated
  explicitly in the frozen contract, not hidden.
- **Model independence.** This review is session-independent only, per the
  `inference` block above; it shares a model family with the producer, the
  three pre-freeze reviewers, and the Coordinator's own precommit
  re-derivation.

---

## Summary

Every check performed independently — receipt content-hash verification,
frozen-contract-vs-implementation line-by-line comparison, a full clean-room
re-execution (true C-REPRO), and from-scratch recomputation of every
headline statistic directly from raw JSON — **passed**. The run is a
faithful, reproducible execution of `specification_v8.yaml` exactly as
frozen. No artifact was found stale, inconsistent, fabricated, or
out-of-scope. The one disclosed discrepancy (PD-1) is a genuine internal
inconsistency in the frozen contract's own text, correctly resolved and
adequately disclosed, not a defect in this run's data.

This validation establishes that **the receipt is admissible evidence**. It
does not itself determine what a PERSISTS outcome means for H-SSIQ-36e970,
PF-6's confound resolution, or lever L4 — that interpretive judgment belongs
to the Coordinator, informed by this report and the Red Team's parallel,
independent review.

```yaml
validation_report:
  id: VAL-BATCH-011
  task_id: TASK-20260806-ae09c6
  run_ids:
    - RUN-SSIQ-a85692-h
  artifact_checks:
    - check: receipt_commit_and_parent_identity
      result: PASS
      detail: >-
        HEAD == fcd9deacf8627360d6b69fd3b8ea2c1224175202 (the cited commit),
        parent == 2c17b69ec52f636ce894881f9f52fd91d1bff25f (matches receipt
        parent_sha and specification_v8.yaml's own freeze commit exactly).
        Worktree clean.
    - check: declared_path_set_and_diff_shape
      result: PASS
      detail: >-
        git diff --stat 2c17b69e fcd9deac -- returns exactly the 11 declared
        artifacts plus the receipt itself, all pure additions (7353
        insertions, 0 deletions, 0 modifications to any pre-existing file).
    - check: path_sha256_recomputation
      result: PASS
      detail: >-
        sha256sum recomputed on all 11 declared artifacts directly from the
        working tree; 0 mismatches against the receipt's path_sha256 block,
        including stderr.log's canonical empty-file hash.
    - check: code_commit_binding
      result: PASS
      detail: manifest.yaml code.commit == this snapshot's parent_sha exactly.
    - check: write_scope_and_prior_runs_untouched
      result: PASS
      detail: >-
        Only 1 new implementation file and 1 new run directory exist;
        specification.yaml through specification_v7.yaml and
        RUN-SSIQ-a85692-a through -g are byte-for-byte untouched.
  metric_recomputations:
    - check: derive_per_vertex_seed_formula_exact_match
      result: PASS
      detail: >-
        Implementation formula is byte-for-byte identical to the frozen
        spec text; 194/194 seed_used values distinct, 0 collisions.
    - check: per_vertex_budget_genuinely_fixed
      result: PASS
      detail: >-
        PER_VERTEX_BUDGET_SECONDS=15.0 passed unmodified per call;
        two_sided_search's own t0 is local to each call, no cross-vertex
        state; 0/194 vertices timed_out.
    - check: pf9_construction_step_order
      result: PASS
      detail: >-
        new_delta_map[v]=1 for all 9 F_p-rational vertices wired before the
        non-F_p-rational search loop begins (line order confirmed by direct
        read).
    - check: pf1_pf9_gate_checked_before_part_b
      result: PASS
      detail: >-
        gate_pass computed from len(new_delta_map)==len(vertices)==203
        before run_probe_permutation_null_control_v8 is called; gate_pass
        true, PART B ran.
    - check: pf12_permutation_construction
      result: PASS
      detail: >-
        Single random.Random(PERMUTATION_SEED), base_values snapshotted
        once, per-trial fresh copy + shuffle on the persistent rng + zip;
        never re-seeded.
    - check: pf13_json_safety
      result: PASS
      detail: >-
        delta_map_json_safe uses str(list(k))-keying throughout; no raw
        tuple used as a JSON dict key anywhere in the artifacts.
    - check: c_repro_independent_re_execution
      result: PASS
      detail: >-
        Fresh clean-room re-run (279.51s, EXITCODE=0, OUTCOME PERSISTS).
        raw-result.json: 5 diffs, all expected non-deterministic fields
        (timestamps, wall_clock_seconds, git.commit/dirty). Comparison
        JSON: 194 diffs, all per-vertex wall_seconds timing, 0 diffs in
        new_delta_map/coverage_gate/comparison_against_archived.
        Permutation-null JSON: 0 diffs, bit-for-bit identical.
    - check: archived_vs_new_delta_map_diff
      result: PASS
      detail: >-
        Independently loaded RUN-SSIQ-a85692-b's archived delta_map (203
        keys) and this run's new_delta_map (203 keys) and diffed key-by-key:
        n_value_differs=0, confirming the reported figure exactly.
    - check: permutation_null_statistics_recomputation
      result: PASS
      detail: >-
        max(null_depth0_fractions)=0.7471264367816092 and margin=
        25.287356321839084 recomputed directly from the raw 1000-trial
        list, exact match to reported values; PERSISTS threshold check
        (>=0.95 and >=13.1) independently confirmed true.
    - check: real_n_structural_local_min_cross_check
      result: PASS
      detail: >-
        95 matches RUN-SSIQ-a85692-g's own archived per_prime_summary for
        p=2437 exactly. Vertex-identity match (not merely count) is
        established by a stronger structural argument: depth0_fraction/
        local_min_and_depth are pure functions of (delta_map, vertices,
        adjacency); delta_map is byte-identical (0/203 differ) and the
        graph is confirmed identical via PF-8, so the local-minimum vertex
        set is mathematically forced to be identical, not merely
        coincidentally equal in count. RUN-g's own artifacts do not store
        per-vertex identities, so a raw diff against RUN-g's own stored
        data was not directly possible; the structural argument is offered
        instead and is at least as strong.
  control_checks:
    - check: graph_identity_reverification_pf8
      result: PASS
      detail: >-
        n_built_vertices=203, degree_sequence_check.pass=true
        (n_degree_ne_3=0), vertex_count_match=true; independently
        cross-checked n_built=203 against RUN-SSIQ-a85692-b's own archived
        n_vertices=203 for p=2437.
    - check: pd1_disclosed_discrepancy_resolution
      result: PASS
      detail: >-
        amendment_scope vs. required_artifacts_note internal contract
        inconsistency over build_isogeny_graph.degree_sequence_check;
        Executor's resolution (follow amendment_scope's more specific,
        PF-8-cited instruction) is correct and adequately disclosed in both
        manifest.yaml and execution_report.yaml, not silently reconciled.
    - check: null_object_decay_under_manipulation
      result: PASS
      detail: >-
        This amendment's design is itself a decay-under-manipulation check
        of PF-6's confound: the manipulation (independent per-vertex RNG,
        fixed budget) should decay the ANOM-1 margin if the RNG-sharing
        procedure were the cause. Measured: delta_map unchanged, margin did
        not decay (25.29pp vs. archived 23.1pp). Interpretation for
        H-SSIQ-36e970 is explicitly out of this Validator's scope.
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: passed
  limitations:
    - Toy scale only (p=2437, N=203 vertices); no result transfers to
      cryptographic scale.
    - Single prime, single amendment; the other three primes (3889, 5737,
      7333) remain untested by this probe, per the frozen contract's own
      explicit deferral.
    - PF-8's graph-identity check is degree-sequence + vertex-count against
      a pinned seed, not a full adjacency-list diff against the archived
      graph; this scope is inherited unchanged from v5/v6/v7, not narrowed
      by v8.
    - PF-4's own disclosure that the archived baseline's budget-shrinking
      confound component was likely never binding was not independently
      re-derived by this Validator (it rests on already-archived
      RUN-SSIQ-a85692-b data outside this task's re-verification scope) but
      is stated explicitly in the frozen contract, not hidden.
    - This review is session-independent only; it shares a model family
      with the producer, all three pre-freeze reviewers, and the
      Coordinator's own precommit re-derivation.
  artifact_paths:
    - experiments/EXP-SSIQ-a85692/specification_v8.yaml
    - experiments/EXP-SSIQ-a85692/implementation/delta_e_independent_rng_probe_v8.py
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/manifest.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/raw-result.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/execution_report.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/source_access_log.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/command.txt
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/environment.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/stdout.log
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/stderr.log
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_permutation_null_control.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-g/raw-result.json
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/archives/TASK-20260806-edeb5a-receipt.yaml
```

**Verdict: ADMIT.** The receipt is a valid, content-verified, independently
reproducible research artifact whose reported numbers recompute exactly
from raw data. This does not itself support any claim about H-SSIQ-36e970,
demonstrate a speedup, or authorize promotion — that judgment is the
Coordinator's, informed by this report and the Red Team's parallel review.
