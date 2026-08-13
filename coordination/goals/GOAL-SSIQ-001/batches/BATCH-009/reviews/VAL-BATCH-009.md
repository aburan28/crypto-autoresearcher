# VAL-BATCH-009 — Validator review of RUN-SSIQ-a85692-f (EXP-SSIQ-a85692 v6, H-SSIQ-36e970, GD-12's fix + funnel-structure diagnostic)

**Reviews the Coordinator-committed snapshot at commit `302b580f`** (receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/archives/TASK-20260806-e3499d-receipt.yaml`,
parent `66753c92`). Nothing in this report edits `specification_v6.yaml`, any
raw artifact, `descent_hitting_time.py`, `trapping_diagnostic_v5.py`, or any
ledger record. `specification_v6.yaml` (636 lines, the frozen contract) was
read in full, including all `pfN_summary` blocks and the three-round freeze
note; `descent_hitting_time.py`'s `greedy_descent_hitting_time` (lines
179–222) and `descent_walk_hardened.py`'s `greedy_descent_hitting_time_v2`
were read directly, side by side, in full; `gd12_equivalence_regression_test.py`,
`funnel_structure_diagnostic_v6.py`, `trapping_diagnostic_v5.py`,
`run_batch009.py` (the actual executed code) read directly, in full; the
complete `RUN-SSIQ-a85692-f` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`,
`gd12_equivalence_regression_test.json`, `corrected_crosscheck.json`,
`funnel_structure_diagnostic.json`); and, for template conformance,
`VAL-BATCH-008.md`. Every independently-computable claim below was
**re-executed live**: a full fresh re-run of `run_batch009.py` end to end
from a clean output directory, plus a **from-scratch, independently-written**
walk/local-minimum implementation (not importing any of the three modules
under test) used to re-derive the crosscheck and ANOM-1 for all four primes,
not sampled to one.

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
    policy-resolved identifier. Same standing condition as VAL-BATCH-008 and
    every prior review in this lineage.
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

- **Commit reachability:** `git merge-base --is-ancestor 302b580f HEAD` →
  reachable (single parent `66753c92...`, matching `log --pretty=%P`).
- **Parent:** matches the receipt's declared `parent_sha` exactly.
- **Path set:** `git diff --name-only 66753c92 302b580f` returns exactly the
  15 declared artifacts plus the receipt itself (`commit_sha: null` /
  `commit_sha_note`, committed inside the commit it describes — same
  self-referential pattern as BATCH-008). Diffed programmatically against
  the receipt's own `declared_paths`: **byte-for-byte set match, no extra
  file, nothing missing.**
- **Hashes:** recomputed `sha256(git show 302b580f:<path>)` independently for
  a 6-file sample spanning both implementation code and run artifacts
  (`descent_walk_hardened.py`, `funnel_structure_diagnostic_v6.py`,
  `manifest.yaml`, `corrected_crosscheck.json`,
  `funnel_structure_diagnostic.json`, `stderr.log`) — **0 mismatches, all 6
  exact matches**, including `stderr.log`'s canonical empty-file SHA-256.
- **Untouched-files check, independently re-run:** `git diff --stat 66753c92
  302b580f --` against every v1–v5 spec file, every pre-BATCH-009
  implementation file named in the contract's `required_artifacts_note`
  UNCHANGED list (`compute_delta_e.py`, `compute_delta_e_v2.py`,
  `reanalyze_v3.py`, `reanalyze_v4_selftest.py`, `ols_hardened.py`,
  `trapping_diagnostic_v5.py`, `gd11_regression_test.py`,
  `run_batch008.py`), `EXP-SSIQ-58b642`'s `descent_hitting_time.py` /
  `build_isogeny_graph.py` / `calibration_synthetic.py`, and every prior run
  directory `RUN-SSIQ-a85692-{a,b,c,d,e}` — returns **empty**. `git status
  --porcelain` on the current worktree is also clean, so nothing here is a
  working-tree-only artifact.

**Verdict: PASS.** The receipt is a genuine, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v6.yaml` is frozen at commit `66753c92` ("EXP-SSIQ-a85692
  v6 FROZEN (three pre-freeze review rounds)"), a direct descendant of
  `79c7d098` (round-2 revised draft), `6ae7847f` (round-1 revised draft),
  `e78309b4` (original draft) — three review rounds precede the freeze in
  the commit graph, matching `pre_freeze_review.status: REVIEWED` and the
  round1/round2/round3 report paths, all present.
- `manifest.yaml.code.commit = 66753c92...` equals the snapshot's own
  `parent_sha` exactly: the run executed against the precise commit that
  froze `specification_v6.yaml`, no intervening commit.
- **Minor, pre-existing, non-blocking textual inconsistency (not introduced
  by this batch):** `specification_v6.yaml`'s own header comment (line 1)
  still reads "DRAFT PROTOCOL AMENDMENT, NOT YET FROZEN," unchanged since
  the freeze commit itself (`git show 66753c92:...specification_v6.yaml |
  head -1` confirms this is baked into the frozen blob, not a working-tree
  drift). The file's `frozen_at`, `status: approved`, and `freeze_note`
  fields are unambiguous, and this batch's execution correctly treats the
  file as frozen — this is a documentation hygiene defect in a file this
  snapshot did not touch (out of `declared_paths`), flagged for a future
  spec-authoring cleanup, not a validity finding against this batch.

**Verdict: PASS**, with the header note above recorded as a non-blocking
observation.

## 3. Claim 1 — `greedy_descent_hitting_time_v2` is a genuine bit-identical superset

Read `descent_hitting_time.greedy_descent_hitting_time` (lines 179–222) and
`descent_walk_hardened.greedy_descent_hitting_time_v2` (lines 71–106)
side by side, not from `gd12_equivalence_regression_test.json`'s own report.
Line-by-line: identical variable initialization, identical top-level
`delta_map[start]==1` short-circuit, identical non-backtracking neighbour
filter (`[v for v in adjacency[current] if v != prev]` with the same
empty-fallback), identical candidate filtering and tie-break dispatch (v2
calls `dht.tie_break_choice`, the frozen function's own unchanged symbol,
never a reimplementation), identical step/tie-event bookkeeping. The **only**
difference at any of the three return statements is the added
`"terminal_vertex": current` key. **Confirmed: a genuine, bit-identical
superset**, independently of the regression test's own self-report.

`gd12_equivalence_regression_test.json` was also independently re-executed
(§5) rather than merely read, and every field it reports (bit-identical
non-terminal fields on 3/3 cases spanning all 3 return branches; `(1617,
1793)` terminal vertex for the named `(148,37)` case) reproduces exactly.

**Verdict: PASS.**

## 4. Claim 2 — the corrected cross-check, independently re-derived from scratch

Wrote a fresh, standalone script importing **only**
`trapping_diagnostic_v5.build_graph_for_prime` /
`load_archived_prime_data` (the contract's own authorized reuse mechanism)
and `descent_hitting_time.tie_break_choice` (the frozen, content-derived
tie rule) — **not** `descent_walk_hardened.py`,
`gd12_equivalence_regression_test.py`, or `funnel_structure_diagnostic_v6.py`,
the three modules under test. Independently reimplemented the walk/terminal-
vertex logic and `is_structural_local_min` from the docstring/formula, and
ran it against all four primes (not a sample):

| p | n_vertices | n_trapped_true | n_trapped_false | disagreements (my code) | matches corrected_crosscheck.json |
|---|---|---|---|---|---|
| 2437 | 203 | 170 | 33 | 0 | yes (170/33, 0 disagreements) |
| 3889 | 324 | 234 | 90 | 0 | yes (234/90, 0 disagreements) |
| 5737 | 478 | 392 | 86 | 0 | yes (392/86, 0 disagreements) |
| 7333 | 611 | 520 | 91 | 0 | yes (520/91, 0 disagreements) |

Zero disagreements on all 1316 trapped=True walks, independently confirming
that every trapped=True walk's terminal vertex genuinely is a structural
local minimum, exactly matching `corrected_crosscheck.json`'s own
`crosscheck_pass: true` / `n_disagreements: 0` for all four primes. This is
a **from-scratch, independently-written confirmation**, not a re-read of the
Executor's or Coordinator's own numbers.

**Verdict: PASS. GD-12 is genuinely fixed**, independently confirmed at the
same standard `VAL-BATCH-008.md` used to falsify v5's uncorrected version.

## 5. Claim 3 — ANOM-1 (depth(m)==0 universally), independently re-derived a fourth time

Extending the same from-scratch script (§4), computed `is_structural_local_min`
over **every** vertex (not just basin-eligible ones) and `depth(m) =
min(neighbour deltas) - delta_map[m]` for every basin-eligible local minimum
(`delta_map[m] > 1`) on all four primes:

| p | n_structural_local_min (all) | n_basin_eligible | distinct depth values observed |
|---|---|---|---|
| 2437 | 95 | 86 | {0} |
| 3889 | 132 | 114 | {0} |
| 5737 | 194 | 176 | {0} |
| 7333 | 287 | 270 | {0} |

**depth(m) == 0 for every one of 646 basin-eligible local minima across all
four primes, zero exceptions** — independently re-derived a **fourth** time
(Executor ×2, Coordinator ×1, this Validator ×1 now), each time from a fresh
query using code outside the run's own new modules. The `n_structural_local_min`
figures (95/132/194/287) exactly match the Coordinator's own precommit
figure in the receipt, and the basin-eligible counts (86/114/176/270) match
`funnel_structure_diagnostic.json` exactly. This is a genuine, real-data
degeneracy, not a coding artifact of any one implementation.

**Verdict: PASS, ANOM-1 independently confirmed.**

## 6. Null-object-control framing (docs/inventor-protocol.md §3)

ANOM-1 is not a reported correlation, bias, or excess — it is the opposite:
the REQUIRED CORRELATION (Pearson, depth vs. basin_size / depth vs.
log(basin_size)) is mathematically **undefined** (zero variance in depth),
and is reported honestly as `null` with an explicit "zero variance" note in
every artifact, never fabricated as `0.0`. No signal is claimed against
which a null-object control (random function, random bijection) would be
required by §3's rule. That said, this review flags — as `execution_report.yaml`'s
own ANOM-1 text already does, not adding a new finding — that a plausible,
undisclosed explanation for the universal depth==0 is a coarse `delta_E`
label range (only 8–11 distinct integer values observed per prime against
203–611 vertices), which would make ties a near-certain pigeonhole
consequence rather than a property specific to this graph's structure. The
frozen spec's own `funnel_structure_diagnostic_v6.py` correctly does **not**
draw this or any other mechanistic conclusion (`OBJECTIVE_BOUNDARY` is
restated and followed throughout), so no §3 gap exists here: nothing claims
depth has explanatory power, so nothing needs a destroying-parameter control
to substantiate a claim that was never made. Recorded as a limitation (§10
below) for whichever future amendment does attempt to interpret ANOM-1.

**Verdict: N/A — no signal is claimed, so §3 does not gate this batch.**

## 7. Claim 4 — PART B's twelve stated "matches frozen spec" values, checked directly

Read `funnel_structure_diagnostic.json`'s `comparison_to_frozen_illustrative_values`
block for all four primes directly (not `manifest.yaml`'s summary of it) and
cross-checked against `specification_v6.yaml`'s own stated
`ILLUSTRATIVE VALUES` text (PF-8 fix, lines 468–490):

| p | n_vertices (spec / measured) | n_trapped_false (spec / measured) | sum_basin (spec / measured) |
|---|---|---|---|
| 2437 | 203 / 203 | 33 / 33 | 170 / 170 |
| 3889 | 324 / 324 | 90 / 90 | 234 / 234 |
| 5737 | 478 / 478 | 86 / 86 | 392 / 392 |
| 7333 | 611 / 611 | 91 / 91 | 520 / 520 |

All twelve numbers match exactly, and `n_vertices_match` /
`n_trapped_false_match` / `sum_basin_match` are all `true` in the JSON
itself for every prime. `sum_basin` also independently reproduces as
exactly `n_trapped_true` in my own from-scratch script (§4), confirming the
partition is exhaustive as the accounting assertion requires.

**Verdict: PASS.**

## 8. Claim 5 — "untouched" files, independently re-checked

`git diff --stat 66753c92 302b580f --` against the full untouched-files list
named in `required_artifacts_note` (specification.yaml through
specification_v5.yaml; `compute_delta_e.py`, `compute_delta_e_v2.py`,
`reanalyze_v3.py`, `reanalyze_v4_selftest.py`, `ols_hardened.py`,
`trapping_diagnostic_v5.py`, `gd11_regression_test.py`, `run_batch008.py`;
`descent_hitting_time.py`, `build_isogeny_graph.py`,
`calibration_synthetic.py`; `RUN-SSIQ-a85692-a` through `-e`) — **empty
diff**, confirmed directly by this review, not merely re-read from the
Executor's or Coordinator's own `git diff --stat HEAD` claim.

**Verdict: PASS.**

## 9. Claim 6 — C-REPRO, reproducibility from a fresh execution

`manifest.yaml.code.commit` (`66753c92`) equals `parent_sha` exactly (§2).
Beyond that binding check, re-ran the **actual recorded command**
(`run_batch009.py --run-dir <clean scratch dir> --raw-result-b
RUN-SSIQ-a85692-b/raw-result.json`) end to end from a clean output
directory. Exit code 0. Every JSON artifact this produced
(`corrected_crosscheck.json`, `funnel_structure_diagnostic.json`,
`gd12_equivalence_regression_test.json`) diffed field-by-field (sorted-key
JSON comparison) against the committed run package — **byte-for-byte
identical**. `raw-result.json` matches after excluding only the
self-evidently time-varying fields (`started_utc`, `finished_utc`,
`wall_clock_seconds`, `git`). This is genuine reproducibility from a fresh
process, not merely internal self-consistency within the one archived run.

**Verdict: PASS.**

## 10. Overclaim / premature-closure check

- `manifest.yaml`'s `validity_reason`, `execution_report.yaml`'s
  `executor_assessment`, and the receipt's `coordinator_precommit_checks`
  all state ANOM-1 and its consequence (the REQUIRED CORRELATION being
  undefined) plainly, in machine-readable fields, without softening or
  omission, and explicitly decline to draw any conclusion about
  `H-SSIQ-36e970` or lever L4 — correctly deferring that judgement to the
  Coordinator and independent reviewers, per `funnel_structure_diagnostic_v6`'s
  own `OBJECTIVE_BOUNDARY`.
- `certificate.kind: none` is correctly declared with a reason consistent
  with `docs/claims-and-verification.md`.
- Grep across the full run package for claim-adjacent overreach ("detects a
  gradient," "confirms L4," "validated the mechanism," "GD-12 proves")
  returns zero matches beyond the disclosed, scoped "GD-12 is genuinely
  fixed" statement, which this review independently confirms (§4).
- `scale_qualifier`/toy-scale framing is inherited unchanged from prior
  batches (graph sizes 203–611 vertices); nothing here is presented as
  crypto-scale.

**Verdict: PASS.** No overclaim found.

## 11. Infrastructure / budget sanity

Measured wall-clock `3.17s` against a `900s` budget, roughly two orders of
magnitude under budget; `ulimit -v 2097152` (2 GiB) never approached. PD-2
(a `SyntaxError` in the Executor's own first draft of
`gd12_equivalence_regression_test.py`, fixed before any artifact was
produced) is disclosed in `execution_report.yaml`/`command.txt`, correctly
classified as an `implementation_error` in the Executor's own first attempt,
not a specification defect, and not treated as evidence — independently
confirmed non-consequential: no output from the failed attempt exists or
was reported. This review's own re-execution (§9) reproduced `3.17s`–`3.19s`
wall-clock across two runs, consistent.

**Verdict: PASS.**

---

## Findings

- **F-1 [confirmed, not blocking].** `greedy_descent_hitting_time_v2` is
  independently confirmed a genuine, bit-identical superset of the frozen
  `greedy_descent_hitting_time` by direct side-by-side line comparison, not
  by trusting the regression test's own report — the required equivalence
  regression is also independently re-executed and reproduces exactly.
- **F-2 [central finding, confirmed, not blocking].** GD-12's corrected
  cross-check is independently re-derived from scratch, using code outside
  all three modules under test, against all four primes (not sampled): zero
  disagreements on 1316/1316 trapped=True walks. **GD-12 is genuinely
  fixed**, in direct, independently-confirmed contrast to v5's uncorrected
  cross-check, which `VAL-BATCH-008.md` independently confirmed failed on
  every prime for a different, specification-level reason.
- **F-3 [confirmed, not blocking, disclosed anomaly].** ANOM-1 (depth(m)==0
  for all 646 basin-eligible local minima across all four primes) is
  independently re-derived a fourth time by this review, from a fresh
  from-scratch query, matching the Executor's (×2) and Coordinator's (×1)
  own independent re-derivations exactly. The REQUIRED CORRELATION is
  correctly reported as mathematically undefined (`null`, zero-variance
  note), never fabricated as `0.0`. No §3 null-object-control gap exists,
  since no correlation/bias/excess is actually claimed — the finding is the
  absence of variance to correlate, honestly reported and left
  uninterpreted, correctly deferred to future review.
- **F-4 [confirmed, not blocking].** All twelve of PART B's
  "matches-frozen-spec" numbers (n_vertices/n_trapped_false/sum_basin × 4
  primes) independently verified to match `specification_v6.yaml`'s own
  stated illustrative values exactly, cross-checked directly against the run
  JSON's own comparison block, not merely against the manifest's summary.
- **F-5 [confirmed, not blocking].** Every file the contract requires
  untouched (`descent_hitting_time.py`, `build_isogeny_graph.py`,
  `calibration_synthetic.py`, `trapping_diagnostic_v5.py`, `ols_hardened.py`,
  every prior spec version, every prior run directory) is independently
  confirmed byte-for-byte unchanged by this review's own `git diff --stat`,
  and the worktree itself is clean.
- **F-6 [confirmed, not blocking].** Full reproducibility independently
  confirmed: a fresh re-execution of the actual recorded command, from a
  clean directory, produces byte-for-byte identical JSON artifacts
  (excluding only inherently time-varying fields) — genuine reproducibility,
  not self-consistency within one archived run.
- **F-7 [informational, non-blocking].** `specification_v6.yaml`'s own
  header comment is stale ("DRAFT... NOT YET FROZEN," unchanged since the
  freeze commit itself) despite `frozen_at`/`status: approved`/`freeze_note`
  being unambiguous. Pre-existing in the parent commit, not introduced by
  this batch, and did not cause any operational ambiguity in this run.
  Flagged for a future spec-authoring hygiene pass.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run executed exactly as its frozen v6 contract (after three pre-freeze
review rounds) specifies. Every independently checkable claim in this
package was re-derived from a from-scratch, independently-written
implementation (not importing any of the three modules under test), from a
full fresh re-execution of `run_batch009.py` against the actual committed
code (byte-for-byte reproduction of every JSON artifact), or from direct
side-by-side source comparison — not accepted from the manifest's prose, the
Executor's own diff-list cross-check, or the Coordinator's own precommit
numbers. All sampled path hashes match and the full declared-path set is
exact (§1); the contract-freeze binding is correct and followed three
review rounds (§2); `greedy_descent_hitting_time_v2` is a genuine
bit-identical superset (§3); **GD-12 is genuinely fixed**, independently
confirmed by a fourth, independently-written re-derivation against all four
primes with zero disagreements (§4); **ANOM-1 is independently confirmed**
a fourth time (§5), correctly reported as an undefined correlation rather
than fabricated, with no null-object-control gap since no signal is claimed
(§6); all twelve of PART B's stated expected values are independently
verified exact (§7); every file required untouched is confirmed untouched
(§8); and the run is confirmed reproducible from a clean re-execution, not
merely self-consistent (§9).

It is admitted **with the condition**, extending this lineage's standing
practice (`VAL-BATCH-008.md`'s own condition), that any future ledger
evidence or decision record citing this batch's outcome must state
precisely what is now established and what is not: **GD-12 is genuinely
fixed** (independently confirmed, not merely asserted) — the corrected
cross-check is a real, code-verified confirmation of `corrected_equivalence_proof`
against real archived data. **PART B is a diagnostic only**, per its own
repeatedly-restated `OBJECTIVE_BOUNDARY`: it does not test
`H-SSIQ-36e970`'s real-arm prediction, does not gate any decision rule, and
does not itself constitute evidence for or against a computable
`delta_E`-gradient. **ANOM-1 (universal depth==0) is a genuine, real,
unexplained empirical property of this batch's four primes' `delta_E`
labelling**, independently confirmed four times by four different
code paths — it is not evidence of any kind for or against L4's revisit
condition, and any future amendment that investigates *why* it holds
(the coarse `delta_E` cardinality is a plausible but untested candidate
explanation) should itself be treated as new research, not a restatement of
this batch's result.

```yaml
validation_report:
  id: VAL-BATCH-009
  task_id: TASK-20260806-ff3023
  run_ids: [RUN-SSIQ-a85692-f]
  reviewed_commit: 302b580f196afd25ddd40f89502c38aaa5acde8f
  reviewed_commit_parent: 66753c92fede639ab30e1b28dc1382b08a25167f
  artifact_checks:
    - {check: path_sha256_recompute, scope: "6-file sample of 15 declared paths (implementation + run artifacts)", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "16 changed files = 15 declared artifacts + receipt itself; diffed programmatically against declared_paths, exact set match"}
    - {check: v1_v5_artifacts_prior_runs_and_shared_library_code_untouched, result: PASS, detail: "git diff --stat 66753c92 302b580f against every v1-v5 spec, every named UNCHANGED implementation file, EXP-SSIQ-58b642's three frozen modules, and RUN-SSIQ-a85692-a/-b/-c/-d/-e returns empty; worktree also clean"}
    - {check: contract_frozen_before_run, frozen_commit: 66753c92, run_code_commit: 66753c92, result: PASS, detail: "manifest.yaml.code.commit equals the freeze commit exactly, no intervening commit; freeze followed three pre-freeze review rounds in the commit graph"}
    - {check: required_artifacts_present, result: PASS, detail: "all 15 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: greedy_descent_hitting_time_v2_superset_property, method: "direct side-by-side source comparison, not the regression test's own self-report", result: "confirmed bit-identical superset: only difference is the added terminal_vertex key at each of the three return statements"}
    - {metric: gd12_equivalence_regression_test_full_rerun, method: "byte-for-byte JSON diff of a fresh re-execution against the committed gd12_equivalence_regression_test.json", result: "IDENTICAL"}
    - {metric: corrected_crosscheck_p2437_p3889_p5737_p7333, method: "from-scratch, independently-written walk + is_structural_local_min implementation, importing only trapping_diagnostic_v5's authorized reuse functions and dht.tie_break_choice -- not any of the three modules under test", reported: "0 disagreements on 170/234/392/520 trapped=True walks respectively", recomputed: "0 disagreements on 170/234/392/520 trapped=True walks respectively, all four primes", result: "EXACT MATCH, independently reproduced"}
    - {metric: anom1_depth_zero_universal, method: "same from-scratch script, extended to compute depth(m) for every basin-eligible and every structural local minimum on all four primes", reported: "depth==0 for 86/114/176/270 basin-eligible minima (646 total), 95/132/194/287 structural minima (all)", recomputed: "identical: depth distinct-values set == {0} for every prime, both scopes", result: "EXACT MATCH, independently reproduced a fourth time (Executor x2, Coordinator x1, this Validator x1)"}
    - {metric: part_b_twelve_illustrative_values, method: "direct read of funnel_structure_diagnostic.json's own comparison_to_frozen_illustrative_values block for all four primes, cross-checked against specification_v6.yaml's own stated text", result: "all twelve values (n_vertices/n_trapped_false/sum_basin x 4 primes) match exactly"}
    - {metric: full_run_batch009_reexecution, method: "re-ran the exact recorded command against the committed code from a clean directory", result: "exit code 0; every output JSON (gd12_equivalence_regression_test.json, corrected_crosscheck.json, funnel_structure_diagnostic.json) byte-for-byte identical to the committed run package; raw-result.json matches after excluding only inherently time-varying fields"}
    - {metric: wall_clock_sanity, reported: 3.1727652549743652, recomputed_by_reexecution: "3.17s-3.19s across repeated runs", result: "consistent, two orders of magnitude under the 900s budget"}
  control_checks:
    - {control: v2_bit_identical_superset_of_frozen_dht_function, result: CONFIRMED, detail: "direct side-by-side source read, lines 179-222 vs 71-106, not the regression test's own report"}
    - {control: gd12_corrected_crosscheck_independently_reproduced, result: CONFIRMED, detail: "from-scratch implementation, all four primes, zero disagreements on 1316/1316 trapped=True walks"}
    - {control: anom1_depth_zero_independently_reproduced_4th_time, result: CONFIRMED, detail: "fresh query, code outside all three modules under test, matches Executor's and Coordinator's own independent re-derivations exactly"}
    - {control: part_b_illustrative_values_match_frozen_spec_text, result: CONFIRMED, detail: "all twelve values checked directly against both the JSON artifact and the frozen spec's own stated text"}
    - {control: v1_v5_and_prior_runs_and_shared_library_untouched, result: PASS, detail: "git diff --stat 66753c92 302b580f against every prior spec/run path and all three EXP-SSIQ-58b642 frozen modules returns empty"}
    - {control: c_repro_fresh_reexecution, result: PASS, detail: "byte-for-byte identical JSON artifacts from a clean re-run, not merely self-consistency within the archived run"}
    - {control: no_overclaim, result: PASS, detail: "grep across all run artifacts for claim-adjacent overreach returns zero matches beyond the disclosed, independently-confirmed 'GD-12 is genuinely fixed' statement; OBJECTIVE_BOUNDARY correctly followed throughout for PART B"}
    - {control: null_object_control_applicability, result: NOT_APPLICABLE, detail: "ANOM-1 is an undefined correlation (zero variance), not a claimed correlation/bias/excess; no signal is asserted that would require a destroying-parameter/null-object control under inventor-protocol.md section 3"}
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: confirmed-not-blocking, summary: "greedy_descent_hitting_time_v2 independently confirmed a genuine bit-identical superset of the frozen function by direct source comparison, not by trusting the regression test's own report"}
    - {id: F-2, severity: confirmed-central-finding-not-blocking, summary: "GD-12's corrected cross-check independently re-derived from scratch against all four primes: zero disagreements on 1316/1316 trapped=True walks. GD-12 is genuinely fixed."}
    - {id: F-3, severity: confirmed-not-blocking-disclosed-anomaly, summary: "ANOM-1 (depth(m)==0 for all 646 basin-eligible local minima, all four primes) independently reproduced a fourth time from a fresh from-scratch query; correctly reported as an undefined correlation, not fabricated; no null-object-control gap since no signal is claimed"}
    - {id: F-4, severity: confirmed-not-blocking, summary: "All twelve of PART B's stated expected values independently verified exact against both the run JSON and the frozen spec text"}
    - {id: F-5, severity: confirmed-not-blocking, summary: "Every file required untouched is independently confirmed byte-for-byte unchanged; worktree clean"}
    - {id: F-6, severity: confirmed-not-blocking, summary: "Full reproducibility independently confirmed via a fresh, clean re-execution producing byte-for-byte identical artifacts"}
    - {id: F-7, severity: informational-non-blocking, summary: "specification_v6.yaml's own header comment is stale ('DRAFT... NOT YET FROZEN'), pre-existing in the parent commit, not introduced by this batch, no operational consequence"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, the pre-freeze reviewers, and the Coordinator's own precommit re-derivation; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "PART B is a diagnostic only, per its own repeatedly-restated objective_boundary; this report makes no claim about H-SSIQ-36e970's real-arm prediction, lever L4's status, or whether a computable delta_E-gradient exists."
    - "ANOM-1 (universal depth==0) is independently confirmed as a real, unexplained property of these four primes' delta_E labelling under this construction; a plausible but untested candidate explanation (coarse delta_E cardinality: only 8-11 distinct values per prime against 203-611 vertices) is noted but not investigated by this review or by the run itself -- any future amendment addressing it is new research, not a restatement of this result."
    - "Toy scale throughout, inherited unchanged from H-SSIQ-36e970.scope_ceiling: graph sizes 203-611 vertices; nothing here transfers to cryptographic scale or is claimed to."
    - "This review's own recomputation was exhaustive (all four primes, not sampled) for the corrected cross-check and ANOM-1, and used a full byte-for-byte re-execution (not a second independent implementation) for the remaining twelve PART B values and every hash/diff check -- the exhaustive from-scratch re-derivation targeted the two claims this task explicitly named as most important."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/VAL-BATCH-009.md
```
