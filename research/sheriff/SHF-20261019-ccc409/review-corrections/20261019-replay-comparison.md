# Replay comparison correction — 2026-10-19

This correction applies to sheriff case `SHF-20261019-ccc409`, first reviewed at
`5a29e76baa91941e599be28bbb6405ee6692bf93` and reconciled with the concurrent
author updates `bafe4ed12926282ab30bd1874396808c30f07070` and
`6cf6c48d0d6de3202e2faa0a683e3537a5206c18`. This correction preserves the retained
records and repairs two executable comparator/test files. The 44 original-head,
67 first-update and 80 later-update path hashes are bound separately in the
[machine-readable correction](20261019-replay-comparison.json); the original
versions remain available at the first commit.

The archived `scripts/replay.py` uses an unanchored regular expression to remove
keys containing `date`, `dir`, and other strings. It therefore removes
`candidate_scalar`, `candidate_point`, and `direction`. It also rounds all
floating-point values to nine decimal places. Two distinct results,
`{candidate_scalar: 7, candidate_point: [1, 2], direction: above, value: 1e-10}`
and `{candidate_scalar: 19, candidate_point: [3, 4], direction: below, value: 2e-10}`,
both become `{value: 0.0}`. The fixed regression reproduces that false equality
by importing the historical comparator without invoking its command launcher.

The original case records six replay passes: three from the comparator and
three from manual re-diff statements. The comparator defect does not disprove
those manual comparisons or demonstrate a changed scientific result.

While this correction was under review, the author supplied a strict comparator
and committed/regenerated output pairs in `bafe4ed129`. A read-only review of
those retained bytes found nine pairs equal after excluding the exact metadata
leaves listed in [the retained-pair review](20261019-retained-pairs.json). Each
committed side matches its artifact at audited base `d0f70c0a0905`. Every
excluded path was inspected with its before/after values; no key-name heuristic
or wildcard is used in this comparison. Timing, memory, execution identity,
platform and timestamp agreement are outside that result.

The pairs cover all files listed by the author's comparison output for five
records. For `EV-MONO-d90e9c`, only three of five listed pairs were retained:
`replay_strict.py` stores `PAIRS/evidence_id/basename`, so `p211` overwrote the
`p101/preregistration.json` and `p101/timings.json` pairs. The retained committed
hashes match `p211`, not `p101`. The missing exact pairs must be recovered from
the author's existing replay scratch area and independently compared, or that
record's complete comparison must remain unknown. The JSON records the expected
and retained hashes. A new run cannot substitute for the missing original pair
without a new receipt.

The author then supplied a separate MONO rerun and receipt in `6cf6c48d0d`,
explicitly stating that the first scratch worktree was removed and the original
missing pair cannot be recovered. Its five new pairs use full artifact paths.
This review checked all five committed sides against the audited base and
compared both sides with concrete, inspected clock/timing/RSS exclusions. All
five agree within that scope. They are recorded as `later_author_record` in the
same retained-pair JSON, separately from the nine first-run pairs. They do not
repair the missing original bytes. The new author's receipt names worktree
commit `bafe4ed129`; this review has not certified its execution/source parity.

These are comparisons of retained artifacts, not verification of replay
execution identity, exact source parity, the complete expected output set,
performance, preregistration chronology or underlying science. The original
six historical replay statuses remain unresolved at that broader level; the
artifact-level results are recorded separately. This review launched no
recorded experiment command and does not authorize one.

The author's new comparator fixes the original rounding/key-filter defect.
This patch additionally escapes `/` and `~` inside JSON-pointer object keys,
requires every excluded path to resolve to a scalar leaf on both sides, and
refuses nonfinite or unsupported values. Fixed regressions cover aliasing,
container loss, missing metadata and unsupported values. The launcher now
emits `artifact_comparison_pass` with `execution_certified: false`, because it
selects only modified JSON/YAML files and has no complete expected output
inventory. Historical output rows retain their original statuses. These code
repairs do not alter the retained-pair results, which use the independent exact
tuple-path helper and concrete leaf paths.

[`exact_comparison.py`](exact_comparison.py) preserves every field and numeric
value by default. An optional allowlist identifies exact object-key/list-index
paths to individual metadata leaves. Missing paths, container exclusions,
nonfinite numbers, and unsupported JSON values are refused. The comparison
retains types and list order and reports every detected difference. Callers must
separately bind the original and replay output bytes, expected artifact set, and
the reason each excluded path is metadata. This helper supplies no archival or
scientific certificate by itself. The old replay launcher remains historical source. A future certified replay
needs an explicitly bound output inventory and execution provenance in addition
to a comparison helper.

The remaining verdict fields also retain the scope stated in the archived
report: most records received mechanical citation checks, and only a small
subset was read substantively. `independence_ok: true` records a heuristic path
or task-resolution signal; it does not establish author, session, instrument,
or model independence. Two run/experiment IDs and an existing reviewer path do
not establish a second reproduction. In particular, the archived C1 phrase
“reproduced on disk for 71 of 88” must be read as **71 labels retained by the
composer's heuristic**, not 71 verified reproductions. Recommended strengths
remain unverified proposals for a separately supported Coordinator decision.
The report's `validated_with_caveats` category can coexist with failed digests,
missing citations, or an unchecked claim; it establishes neither that all
citations resolve nor that every attempted check passed.

Validation for this correction uses fixed in-memory cases only:

```sh
python3 -m unittest discover -s research/sheriff/SHF-20261019-ccc409/review-corrections -p 'test_exact_comparison.py' -v
```

A future audit must receive its own authorization and preserve the original
case, failed attempts, and receipts. This correction changes no evidence record,
strength label, hypothesis, experiment status, or goal state.
