# RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2 — Second pre-freeze Red Team review
# of the REVISED DRAFT amendment `specification_v5.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-008

**Reviews `experiments/EXP-SSIQ-a85692/specification_v5.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED`,
`pre_freeze_review.verdict: FREEZE-WITH-FIXES (this revised text, pending a
second review pass)`, as committed at snapshot `d82be3b4` ("GOAL-SSIQ-001
BATCH-008: EXP-SSIQ-a85692 v5 draft revised after DO-NOT-FREEZE (round 1)"),
parented on `c445c171` (the round-1-reviewed draft).** Working tree confirmed
clean against this commit (`git status --short` on the file: empty). Per this
task's operating rules, only this Coordinator-committed snapshot is treated as
durable input. This report changes nothing under `experiments/EXP-SSIQ-a85692/`
or any ledger record.

Read in full per the launching task: `RT-PREFREEZE-EXP-SSIQ-a85692-v5.md` (the
round-1 report, DO-NOT-FREEZE, PF-1/PF-4/PF-5 blocking, PF-6/PF-7/PF-8
advisory) in full; the current `specification_v5.yaml` in full, in particular
`amendment_scope`, `pre_freeze_review` (with its six `pfN_summary` entries),
`inputs.gd11_fix_v5`, `inputs.trapping_mechanism_diagnostic_v5`, and
`required_artifacts_note`; `descent_hitting_time.py`'s `ols_loglog_fit` (lines
104–134) and `bootstrap_gap_ci` (lines 362–384) read directly; confirmed by
`git log`/`git status` that this file has exactly one commit
(`3c117cbc`) and no working-tree changes, so "stays frozen and byte-for-byte
untouched" is not merely asserted but independently confirmed;
`build_isogeny_graph.py`'s `degree_sequence_check`, `build_graph_bfs`, and
`neighbors_2isogenous` read directly; `RUN-SSIQ-a85692-b/raw-result.json`
loaded and inspected **programmatically**, not sampled — specifically every
field of `phase_minus1_real_search[prime]` for all five primes, including
`n_vertices`, `n_resolved`, `n_attempted`, `len(delta_map)`, and
`m_coverage_all_vertices_fraction`; `compute_delta_e.py`'s
`run_phase_minus1_on_confirmatory_set` (lines 368–419) read directly to
determine what `n_resolved` actually counts; `ledger/goals/GOAL-SSIQ-001/goal.yaml`'s
GD-11 entry and `next_action` in full. A concrete `tuple(json.loads(key))`
round-trip was executed directly in Python against the archived key format
(not derived from memory), per item (2) of the launching task.

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
    Subagent frontmatter under this runtime cannot express a policy
    (CLAUDE.md, "Model policy note"); this session runs `model: inherit`.
    Every credentialed backend under this environment has previously been
    found unprobeable (VAL/RT-BATCH-003 through 007,
    RT-PREFREEZE-EXP-SSIQ-a85692[-v2,-v3,-v4,-v5]), so this is recorded as
    the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This
    review shares a model family with every producer and every prior
    reviewer in this lineage, including the round-1 review of this same
    draft; it does not upgrade the campaign's evidence tier by itself and
    does not itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**PF-1, PF-4, PF-5, and PF-6's fixes genuinely hold up under independent,
direct tracing — round 1's blocking findings are correctly resolved in this
revision, not merely re-worded.** PF-7 and PF-8's advisory text is applied
correctly. But **one new, blocking, precisely-locatable defect (PF-9)** was
found by tracing the revised Part B text against the *actual* archived JSON
fields, not the round-1 report's own prose: the required PF-4 coverage
assertion tells the Executor to check the matched-`delta_map`-key count
against "that prime's already-archived `n_resolved`/`n_vertices` count" as if
these were the same number — **they are not.** `n_resolved` (194, 306, 460,
594 for primes 2437/3889/5737/7333) is a strictly smaller, different
statistic than `n_vertices`/`len(delta_map)` (203, 324, 478, 611, the numbers
actually written in parentheses next to the ambiguous field name). This
conflation was **not introduced by this revision** — it was present verbatim
in round 1's own required-fix text (`RT-PREFREEZE-EXP-SSIQ-a85692-v5.md`,
PF-4's "Required fix" paragraph and its `required_controls` YAML entry) and
the Coordinator's revision correctly implemented round 1's instructions to
the letter, propagating round 1's own unverified error forward. This is
exactly the shape this task's brief warns about: a fix that "looked right in
prose" — in this case, the *prior review's* prose — but does not hold up
under direct tracing against the real data. See PF-9.

None of the four items this affects requires redesign. All are fixable at
zero new search cost, and the concrete correct numbers are already sitting
inline in the spec text — only the field-name label needs correcting.

---

## (1) PF-1's fix: bootstrap wiring, traced step by step

### Design precision

Traced the revised `inputs.gd11_fix_v5` text against `bootstrap_gap_ci`'s
actual code (quoted above from lines 362–384) line by line:

| Original `bootstrap_gap_ci` element | Revised `bootstrap_gap_ci_v2` spec text | Verdict |
|---|---|---|
| Signature `(N_list, median_greedy_list, median_random_list, rng, n_boot=2000)` | States the identical signature verbatim | Unambiguous |
| `idx = [rng.randrange(n) for _ in range(n)]` per resample (PRIMES-as-unit) | "ports ... the resampling loop structure verbatim (same PRIMES-as-resampling-unit design...)" | Unambiguous — no redesign of the resampling unit |
| `fg = ols_loglog_fit(Nb, gb)` | "calls `ols_loglog_fit_v2` ... for BOTH per-resample fits (`fg`, `fr`)" | **Explicitly names both call sites** |
| `fr = ols_loglog_fit(Nb, rb)` | same sentence, "BOTH" | **Explicitly names both call sites** |
| `except ValueError: continue` | "catches the SAME ValueError the hardened guard now raises more reliably, discarding that resample exactly as the original does for a caught ValueError" | Unambiguous |
| `lo = gaps[int(0.025*len(gaps))]; hi = ...` / `if not gaps: return None, None, []` | "same percentile-based CI extraction" | Adequate by the same "ports X verbatim" standard round 1 already accepted for `ols_loglog_fit_v2`'s "BYTE-IDENTICAL except the guard" framing |

**Unlike the original draft's text (`= dht.bootstrap_gap_ci`, then an
unresolved "OR"), this revision states exactly one binding, at both call
sites, with no open alternative.** There is no remaining "OR" for an Executor
to resolve either way. This closes round 1's PF-1 (c) finding as specified.
**PF-1's fix is CONFIRMED ADEQUATE.**

### Regression test design — is it exercisable as a "technically passes" gap?

I built and ran the concrete construction a competent Executor would most
naturally use to satisfy "resample data constructed so that at least one
resample draw reproduces the N=324/n=3 ... anomaly pattern": `N_list =
[324, 324, 324]` (all three entries identical, i.e. the *population itself*
is degenerate, not merely one lucky resample draw). Under this construction:

- **Every** resample (`idx = [rng.randrange(3) for _ in range(3)]`) produces
  `Nb = [324, 324, 324]` regardless of which specific indices are drawn,
  since all three source values are identical. This guarantees, deterministically
  and independent of `rng` state or seed, that the anomaly fires on every one
  of the `n_boot` iterations — a strictly stronger and *more* reproducible
  test than "at least one."
- I confirmed directly (same computation as round 1's (b)) that
  `max(xs) == min(xs)` is `True` for `xs = [math.log(324)]*3` (trivially,
  since it is the same float computed three times), so `ols_loglog_fit_v2`
  correctly raises on every resample, `gaps` stays empty, and
  `bootstrap_gap_ci_v2` correctly returns `(None, None, [])`.
- This construction is also a genuine discriminator against the *original*
  PF-1 hollow-fix pattern, not merely a check that looks busy: if
  `bootstrap_gap_ci_v2` were (despite the spec text) still secretly wired to
  the unhardened `ols_loglog_fit`, this exact input would reproduce round 1's
  own finding — `sxx = 2.3665...e-30` (not exactly `0.0`) — so the *old*
  guard does **not** fire, `gamma = sxy/sxx` is computed from a near-zero
  denominator, and a spurious, non-`None` gap value would enter the returned
  CI. So a test built this way both (a) exercises the anomaly and (b) would
  fail loudly if the wiring bug from round 1's original draft recurred.

**This is a real, working test, not a placeholder** — unlike v4's PF-1 gap
(where neither of the two *specified* checks constructed the boundary case
the mutation needed, so the gap was in what the spec explicitly enumerated),
here the spec names the target values explicitly and the cheapest, most
natural construction that satisfies the literal text also happens to be the
strongest available construction. **Residual, non-blocking precision note:**
the spec text does not itself state *how* to construct "resample data ...
so that at least one draw reproduces" the pattern — it leaves the mechanism
implicit. A less careful Executor could instead pass `N_list` with four
*distinct* real values (mirroring `RUN-SSIQ-a85692-b`'s actual archived set)
and rely on `rng` chance to occasionally draw a degenerate resample within
`n_boot=2000` iterations — a weaker, seed-dependent, non-guaranteed
construction that could pass or fail depending on unstated seed choice. I do
not classify this as blocking: the natural reading (a repeated-value
population) is both simpler to implement and stated directly enough ("N=324/n=3") that an Executor most likely arrives at it, and, unlike v4's PF-1,
there is no evidence in this codebase's history of an Executor choosing the
weaker chance-dependent construction when a deterministic one is this cheap.
Recommend the spec add one clause naming the repeated-value construction
explicitly, to remove the last bit of interpretive freedom — advisory,
**PF-10**.

## (2) PF-4's fix: `tuple(json.loads(key))` round-trip, executed directly

```python
>>> v = (1031, 1095)
>>> key = str(list(v))
>>> key
'[1031, 1095]'
>>> back = tuple(json.loads(key))
>>> back, type(back[0]), back == v
((1031, 1095), <class 'int'>, True)
```

Confirmed directly against the archived file: `delta_map["[1031, 1095]"]`
exists in `RUN-SSIQ-a85692-b`'s `phase_minus1_real_search["2437"]` (round 1's
own counterexample). The round-trip recovers the **exact original tuple**,
including element type (`int`, not `float`, `str`, or a numeric type that
would fail Python's `==`/hash-based dict-key equality against the rebuilt
graph's own `(int, int)` vertex tuples — confirmed by direct reading of
`build_isogeny_graph.py`: `Fp2Field` elements are always plain `(a, b)`
tuples of Python `int` in `[0, p)`, e.g. `build_graph_bfs`'s
`seed = (seed_int % p, 0)` and `neighbors_2isogenous`'s returned roots, both
built from `%`/field arithmetic that always yields `int`). **`json.loads`
parses arbitrary-precision integers as Python `int` with no floating-point
detour**, so there is no precision-loss failure mode here even for large
field elements. `tuple(json.loads(key))` is confirmed the correct, exact
round-trip. **PF-4's key-conversion fix is CONFIRMED ADEQUATE** — but see
PF-9 below: the conversion procedure is correct, the *downstream coverage
comparison target* it feeds is not.

## (3) PF-5's fix: is M-DEGSEQ + archived vertex count a meaningful correctness check?

Confirmed the revised spec text no longer claims "byte-identical to what was
already validated" — it now reads "report the rebuild as 'independently
verified correct' only if both [M-DEGSEQ and the archived per-prime vertex
count] pass," matching round 1's required reframing exactly. This is honest
framing. On the substance (round 1's own question, restated for this pass):
**yes, residual risk remains, and it is acceptable, for the reason round 1
already gave** — no adjacency was ever archived, so no stronger check is
achievable from data that exists. A root-finding bug that swaps which of two
degree-matching curves is adjacent to a third, while preserving vertex count
and every vertex's degree-3 property, would still pass both M-DEGSEQ and the
count check. I looked for whether a stronger check is available and was not
proposed: **one exists and is, in fact, latently present in this same
revision** — PF-4's own coverage assertion, once corrected per PF-9, is
**more discriminating than PF-5's own stated pair of checks**, because
`delta_map`'s archived key set is an implicit archived snapshot of the
*exact vertex set* (not just its count or its per-vertex degree) from a
*prior, already-validated* build. A rebuild that produces vertex `v'`
where the original build had `v` (same count, same degree-3 property, but
`v' != v`) would fail to find a `delta_map` entry for `v'` and would be
short one match — the coverage assertion would catch it. This does not
recover adjacency-level verification (two different vertex sets could still
coincidentally produce the same count of matches through a compensating
double-error, which is a residual, accepted risk), but it is a real,
free, additional layer of vertex-set fidelity beyond what PF-5's own text
names, worth stating explicitly rather than leaving implicit. Recommend
adding one sentence cross-referencing PF-4's coverage assertion as a second,
independent vertex-set check alongside M-DEGSEQ — advisory, **PF-11**.
**PF-5's fix is CONFIRMED ADEQUATE** as specified; the residual risk is
honestly bounded, not hidden, and is the correct "best available check"
verdict, matching round 1's own honest weighing.

## (4) PF-6's fix: is the full-vertex cross-check actually cheap?

Confirmed unchanged from round 1's assessment: `greedy_descent_hitting_time`
is O(diameter) per start vertex (a strict-descent walk that terminates in at
most `diameter` steps, since delta strictly decreases and the walk cannot
revisit — confirmed by direct reading of the function, lines 179–222).
Graphs here are ≤ 611 vertices (`n_vertices` for the four primes used, per
the table below), 3-regular, with diameters that scale like O(log p) for
supersingular 2-isogeny (Ramanujan-graph) expansion — negligibly small
relative to `n_vertices` itself. Running the walk from all 611 (or fewer)
vertices costs at most a small constant factor over running it from a
sample, and the stated budget (`900s`/`0.3` CPU-hours) already accounted for
this generously in round 1 relative to `EXP-SSIQ-58b642`'s own measured
graph-build figures (12–120s total). No new cost concern. **PF-6's fix is
CONFIRMED ADEQUATE**, cost-wise and design-wise (the exact
walk-trapped/structural-local-minimum equivalence argument in round 1's (g)
is unchanged and still correct, since `greedy_descent_hitting_time` remains
byte-for-byte frozen — independently reconfirmed via `git log`/`git status`
above).

## (5) New gap search: does the revision change anything beyond the fit-function substitution, and is the diff list complete?

- **`rng` handling:** unchanged — `bootstrap_gap_ci_v2` states the identical
  `rng` parameter position and role ("ports ... the resampling loop structure
  verbatim"). No redesign found.
- **`n_boot` handling:** unchanged — the signature explicitly restates
  `n_boot=2000` as the default, matching the original exactly.
- **Percentile extraction:** stated as "same percentile-based CI extraction,"
  which I accept by the same standard round 1 already applied to
  `ols_loglog_fit_v2`'s "BYTE-IDENTICAL except the guard" claim — a
  mechanically verifiable, line-diffable assertion once the code exists, not
  a design ambiguity now.
- **`required_artifacts_note`'s diff list:** re-checked against the revised
  design. It now correctly lists **two** new functions inside
  `ols_hardened.py` (`ols_loglog_fit_v2` and, explicitly, `bootstrap_gap_ci_v2`
  as "a GENUINELY NEW function with its own resampling loop, NOT an alias"),
  matches `required_artifacts` now listing **two separate** regression-test
  artifacts (`gd11_regression_test.json` for the standalone-function test and
  `bootstrap_gap_ci_v2_regression_test.json` for the wiring test) — this is a
  real structural improvement over the round-1 draft (which had only one
  regression-test artifact, part of why PF-1's own required validation could
  not have caught the hollow-fix pattern even if intended to). The
  UNCHANGED and NOT-RE-RUN lists are unchanged from round 1 and remain
  accurate on direct check (confirmed no prior run's file is read for
  anything but `delta_map`, per (6) below). **This item is adequately
  addressed** — no new gap found here beyond PF-9 (below), which is a
  data-value defect, not a diff-list omission.
- **THE ONE NEW GAP FOUND: PF-9**, detailed next.

### PF-9 [BLOCKING, NEW] — Part B's coverage assertion names two different, unequal archived quantities as interchangeable, and the field name it leads with is the wrong one

Directly queried `RUN-SSIQ-a85692-b/raw-result.json`'s
`phase_minus1_real_search` for all four primes this amendment uses:

| prime | `n_vertices` | `n_resolved` | `len(delta_map)` |
|---|---|---|---|
| 2437 | 203 | **194** | 203 |
| 3889 | 324 | **306** | 324 |
| 5737 | 478 | **460** | 478 |
| 7333 | 611 | **594** | 611 |

`n_vertices` and `len(delta_map)` agree exactly for all four primes
(consistent with `m_coverage_all_vertices_fraction == 1.0`, already confirmed
by round 1's PF-7 finding). `n_resolved` is a **different, strictly smaller**
quantity for every one of them. Reading `compute_delta_e.py`'s
`run_phase_minus1_on_confirmatory_set` directly (lines 368–419) explains why:
`n_resolved` counts only the **non-`F_p`-rational vertices resolved via the
real `two_sided_search`** (`n_resolved += 1` inside the `for v in non_fp:`
loop at line 402); `delta_map` additionally contains every `F_p`-rational
vertex, which "resolve[s] for free (delta_E = 1 identity)" (line 382–385,
never incrementing `n_resolved`). So `len(delta_map) = n_resolved + (#
F_p-rational vertices)`, and `n_resolved < n_vertices` structurally, for any
prime with at least one `F_p`-rational vertex (which every tested prime has).

The revised spec's Part B text states:

> "the number of `delta_map` keys successfully matched against the rebuilt
> graph's vertex set MUST equal that prime's already-archived
> **`n_resolved`/`n_vertices` count** (203/324/478/611 respectively per
> prime, already sitting in the same `raw-result.json` this diagnostic
> reads)"

This treats `n_resolved` and `n_vertices` as one interchangeable quantity
and gives one set of numbers — but those numbers (203/324/478/611) are the
`n_vertices` values, **not** the `n_resolved` values (194/306/460/594). If an
Executor implements this literally by reading the archived JSON's
`n_resolved` field (the first-named alternative, and a field that genuinely
exists at that exact path, making the mistake easy to make and hard to
notice without cross-checking, exactly as PF-4's own counterexample
demonstrated for the key-format question), the coverage assertion — which
the spec itself requires to "halt with an explicit error... if it does not
match exactly" — will **fail on every single one of the four primes,
unconditionally, even when the key-conversion, graph rebuild, and vertex
matching are all completely correct.** This defeats Part B's diagnostic
before it can report anything, on a self-inflicted false-positive halt, not
a real correctness problem.

**This defect was not introduced by the Coordinator's revision.** It is
present verbatim in round 1's own required-fix language
(`RT-PREFREEZE-EXP-SSIQ-a85692-v5.md`, PF-4's "Required fix" paragraph:
"the number of `delta_map` keys successfully matched ... must equal the
already-archived `n_resolved`/`n_vertices` count for that prime (2437: 203,
3889: 324, 5737: 478, 7333: 611)" — and repeated identically in that report's
`required_controls` YAML block and `next_concrete_action`). Round 1's own
review, in the same pass that correctly identified `n_resolved`,
`n_vertices`, `delta_map` entries, and coverage as *separate columns* in its
own inspection table (`(e)`, lines 271–277 of that report — which lists
`n_vertices` and "`delta_map` entries" as equal, and never lists `n_resolved`
in that table at all), nonetheless wrote its **required fix** using
`n_resolved` as an alias for the value it had only actually verified as
`n_vertices`. The Coordinator's `specification_v5.yaml` revision then
correctly and faithfully implemented round 1's instruction to the letter —
this is exactly the situation this task's brief anticipates: a "fix" that
looked right in prose (round 1's own prose) but does not hold up under
direct tracing against the underlying data. It took querying the real
`raw-result.json` and `compute_delta_e.py` fields directly, not re-reading
either report's own text, to surface it.

**Required fix:** remove `n_resolved` from the coverage-assertion sentence
entirely. State only: "must equal that prime's already-archived
**`n_vertices`** count (equivalently `len(delta_map)`, since
`m_coverage_all_vertices_fraction == 1.0` for all four primes) — 203/324/478/611
respectively — **never `n_resolved`, which is a different, strictly smaller
quantity counting only the non-`F_p`-rational vertices resolved by real
search, excluding the `F_p`-rational vertices that resolve for free.**" This
is a one-sentence, zero-new-search text correction; the correct numeric
values are already present in the spec text and need no recomputation.

**Severity note:** this is not a silent-corruption risk — the assertion, as
literally specified, would halt loudly with an explicit error (per the
spec's own "halt... not a silent partial result" requirement), so it would
not produce a wrong published number. But it would permanently block Part
B's diagnostic from ever completing on any of the four primes, which is a
real defeat of this amendment's stated purpose, and — per this campaign's
own precision discipline (GD-9 through GD-11, all "a control/fix that names
the right thing but doesn't do the right thing at the call site that
matters") — a field-name ambiguity feeding a hard-fail assertion belongs in
the same blocking category as PF-1/PF-4/PF-5 were in round 1, even though,
like round 1's PF-1, it is fixable in one sentence.

## (6) Does the amendment retroactively alter any already-archived gamma/CI value?

**No, reconfirmed.** `required_artifacts_note`'s "NOT RE-RUN" list is
unchanged from round 1 and remains accurate: `RUN-SSIQ-a85692-a/-b/-c/-d`
and every archived `gamma`/CI value are untouched; this amendment reads only
`RUN-SSIQ-a85692-b`'s `delta_map` field and performs no new `delta_E` search.
Consistent with `EV-SSIQ-87d21a.yaml` O-4's finding (GD-11 does not
contaminate any archived number) and with the goal ledger's GD-11 entry,
which states the null-arm fit-and-bootstrap branch "has never yet executed on
real data." **Confirmed, no issue.**

---

## Findings

### Round-1 findings — disposition on this pass

- **PF-1 [was BLOCKING] — CONFIRMED FIXED.** See (1) above: the wiring is now
  stated unambiguously at both call sites, with no open "OR," and the
  required two-part validation (standalone + wired-through) is genuinely
  capable of catching the exact hollow-fix pattern round 1 found, confirmed
  by direct construction and execution of the natural regression-test input.
- **PF-4 [was BLOCKING] — CONFIRMED FIXED on the conversion procedure**; see
  PF-9 for a new, distinct defect in what the conversion's *result* is
  checked against. The `tuple(json.loads(key))` round-trip itself is
  independently verified correct, including type fidelity, by direct
  execution in (2) above.
- **PF-5 [was BLOCKING] — CONFIRMED FIXED**; reframed language is accurate
  and the residual risk (no archived adjacency) is honestly bounded, not
  hidden. See PF-11 (advisory) for an available strengthening not yet stated.
- **PF-6 [was ADVISORY] — CONFIRMED APPLIED AND ADEQUATE**, cost and design
  both reconfirmed negligible/correct.
- **PF-7 [was ADVISORY] — CONFIRMED APPLIED.** The spec now states the
  branch is untestable on this batch's data and specifies loud-raise
  behavior if unexpectedly reached.
- **PF-8 [was ADVISORY] — CONFIRMED APPLIED.** The spec now states explicitly
  that the two fractions are related-but-different statistics.

### PF-9 — [BLOCKING, NEW] Part B's required coverage assertion names `n_resolved` and `n_vertices` as interchangeable; they are not, and the archived `n_resolved` values (194/306/460/594) do not match the numbers written next to them (203/324/478/611, which are actually `n_vertices`)

See the full trace in (5) above. This defect originates in round 1's own
required-fix text and was faithfully, correctly implemented by the
Coordinator's revision — a defect in the *prior review's* prose, not in this
revision's execution of it. Directly confirmed against
`RUN-SSIQ-a85692-b/raw-result.json` and `compute_delta_e.py`'s
`run_phase_minus1_on_confirmatory_set`. As specified, this coverage assertion
will halt with an error on every one of the four primes if implemented by
reading the `n_resolved` field, defeating Part B's diagnostic entirely,
regardless of whether the key-conversion, graph rebuild, and vertex matching
are otherwise fully correct.

**Required fix:** name only `n_vertices` (equivalently `len(delta_map)`,
given confirmed full coverage) as the coverage assertion's comparison target;
state explicitly that `n_resolved` is a different, smaller quantity that must
not be used here, with a one-clause explanation of what it actually counts
(non-`F_p`-rational vertices resolved by real search only).

### PF-10 — [ADVISORY] Part A's required `bootstrap_gap_ci_v2` regression test does not state its construction mechanism explicitly, though the natural reading is correct and was independently verified to work

See (1) above. The natural, cheapest, most robust construction
(`N_list = [N, N, ..., N]`, `n` copies of the single anomalous value) both
satisfies the letter of "at least one resample draw reproduces the anomaly"
and is a genuine discriminator against the original hollow-fix pattern,
independently confirmed by direct execution. Recommend stating this
construction explicitly in the spec text to remove the (currently
unexercised, low-probability) alternative reading of relying on `rng` chance
with distinct `N` values.

### PF-11 — [ADVISORY] PF-5's stated verification does not credit the additional vertex-set fidelity PF-4's own (corrected) coverage assertion provides

See (3) above. Once PF-9 is fixed, PF-4's coverage assertion checks the
rebuilt graph's vertex set against `delta_map`'s archived key set — a
stronger check than M-DEGSEQ + count alone, since it can detect a rebuild
that swaps which specific vertices appear (same count, same per-vertex
degree, different identity) as long as the swap changes which vertices have
a `delta_map` entry. Recommend one cross-referencing sentence in the PF-5
fix text.

---

## Required controls / checks before dispatch

- **PF-9 [BLOCKING]:** correct the coverage-assertion sentence in
  `inputs.trapping_mechanism_diagnostic_v5` to name only `n_vertices`
  (never `n_resolved`) as the comparison target for matched `delta_map`
  keys, with the one-clause explanation of why `n_resolved` is a different,
  smaller quantity. Zero new search cost; the correct numbers are already in
  the spec text.
- **PF-10 [ADVISORY]:** state the `N_list = [N]*n` repeated-value
  construction explicitly for the `bootstrap_gap_ci_v2` regression test.
- **PF-11 [ADVISORY]:** cross-reference PF-4's coverage assertion as an
  additional vertex-set-fidelity check alongside M-DEGSEQ in the PF-5 fix
  text.

## Counterexample or mutation

**PF-9's counterexample, executed directly against the archived data:** for
prime 2437, `raw-result.json`'s `phase_minus1_real_search["2437"]["n_resolved"]
== 194` while `["n_vertices"] == 203` and `len(["delta_map"]) == 203`. A
literal implementation of the spec's coverage assertion using the
`n_resolved` field compares a correctly-computed matched-key count of `203`
against an expected value of `194` and halts with an error on a completely
correct run — a direct falsifier of "the coverage assertion, as specified,
verifies what it claims to verify" for the field name the spec text leads
with.

**PF-1's counterexample, constructed and executed directly:** `N_list =
[324, 324, 324]` fed to a hand-simulated `bootstrap_gap_ci_v2` loop produces
`xs = [math.log(324)]*3` on every resample; `max(xs) == min(xs)` is `True`
(guard fires) under the hardened `ols_loglog_fit_v2`; under the *original*
`ols_loglog_fit`, `sxx = 2.3665...e-30 != 0.0` (guard does not fire), so this
input is a genuine discriminator that the specified regression test, if
implemented as the natural reading suggests, would correctly exercise and
would correctly fail if the PF-1 wiring bug recurred.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
(toy-scale infrastructure and diagnostic work, `asymptotic_claim: null`
throughout, correctly inherited and unchanged from round 1). The relevant
baseline remains this campaign's own instrument- and fix-scrutiny discipline
(GD-4 through GD-11), now extended one layer further: PF-9 shows that
discipline must apply not only to the Executor's implementation and the
Coordinator's amendment text, but to a **prior red-team review's own
required-fix prose**, which is not exempt from the "trace it, don't trust
it" standard just because it is itself a review artifact.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
finding here implicates a numbered heuristic; PF-9/PF-10/PF-11 are all
control/instrument-fidelity or specification-precision gaps.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly). The `900s`/`0.3` CPU-hour budget is unchanged from round 1 and
remains realistic and generously sized; PF-9's fix (a text correction) and
PF-10/PF-11 (text additions) have zero cost impact. The live concern remains
evidentiary: as specified, PF-9 would cause Part B's diagnostic to halt with
an error on its very first real invocation, on all four primes
simultaneously — a loud, not silent, failure, but one that would consume the
run's budget and require a re-dispatch cycle to discover and fix if not
caught before freeze.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis; `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) correctly stated and not exceeded. No scope-inflation found.
`objective_boundary`'s scoping of Part B as a diagnostic, not a claim, is
unchanged and correctly stated. This amendment still correctly bundles
exactly the two actions `DEC-20260805-6aa5c2`'s `next_action` named, on
disjoint data and code paths — reconfirmed, unaffected by PF-9 (which is
purely inside Part B's own diagnostic text).

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level
gradient-existence screen, not a proof-oriented proposal. Attacked and held,
same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v5.yaml` as committed
at `d82be3b4`, `status: draft`: round 1's three blocking findings (PF-1,
PF-4, PF-5) and its advisory finding on cross-check scope (PF-6) are all
genuinely, adequately resolved in this revision, confirmed by independent
direct tracing against the actual code and archived data, not by re-reading
either report's prose — `bootstrap_gap_ci_v2` is a genuinely new function
that unambiguously threads `ols_loglog_fit_v2` through both per-resample fit
calls (PF-1); the `tuple(json.loads(key))` round-trip correctly and exactly
recovers the archived vertex tuples, type included (PF-4's conversion
procedure); the M-DEGSEQ-plus-archived-vertex-count graph-rebuild
verification is the best available check given no adjacency was ever
archived, honestly framed (PF-5); and the exhaustive trapped-vs-structural
cross-check is confirmed computationally negligible for graphs of this size
(PF-6). PF-7 and PF-8's advisory text is applied correctly. **One new
blocking defect was found**: the coverage assertion PF-4's fix requires
names `n_resolved` and `n_vertices` as an interchangeable pair, but they are
different, unequal archived quantities (194/306/460/594 vs.
203/324/478/611) — inherited verbatim from round 1's own required-fix
language and faithfully implemented by this revision, so the defect is in a
prior review's prose, not in the Coordinator's execution of it (PF-9,
blocking, one-sentence fix). Two further advisory precision items (PF-10:
state the regression test's construction mechanism explicitly; PF-11: credit
PF-4's coverage assertion as additional vertex-set-fidelity evidence beyond
PF-5's own stated pair of checks) round out this pass. None require
redesign; all are fixable at zero new search cost, and PF-9's correct
numeric values are already present in the spec text.

## Next concrete action

Coordinator: before `status: approved` / setting `frozen_at`, require the
amendment text to (1) fix PF-9 by naming only `n_vertices` (never
`n_resolved`) as the coverage-assertion's comparison target, with a one-clause
note distinguishing the two archived fields; (2) apply PF-10/PF-11 as
text-only additions. Re-verify PF-9's specific trace once fixed — confirm
the corrected sentence reads `n_vertices` only and that no other place in the
spec (or a future Executor's `execution_report.yaml`) reintroduces
`n_resolved` as a stand-in for it — before freeze, per this campaign's
standing practice of tracing the fix, not merely trusting that text was
added. None of PF-9/PF-10/PF-11 requires new search or touches any
already-archived run's data. Given PF-9 is a single, precisely-located
sentence-level correction with the correct values already present in the
text, and every other round-1 finding is now confirmed genuinely resolved,
this does not warrant a third full DO-NOT-FREEZE cycle — but freeze must not
occur before PF-9's text is corrected and re-checked.

## Overall verdict

**FREEZE-WITH-FIXES.** One blocking item remains, at a much narrower scope
than round 1's three:

1. **[BLOCKING, NEW]** PF-9 — the Part B coverage assertion's stated
   comparison target (`n_resolved`/`n_vertices`, treated as interchangeable)
   is wrong for the `n_resolved` half: `n_resolved` (194/306/460/594) is a
   different, smaller archived quantity than `n_vertices`/`len(delta_map)`
   (203/324/478/611, the numbers actually written in the spec). Fix: name
   only `n_vertices`. One sentence, zero new search cost, correct values
   already stated.

PF-1, PF-4, PF-5, PF-6, PF-7, PF-8 are all confirmed genuinely fixed on this
pass, by direct tracing against the actual code and data, not by trusting
either this revision's or round 1's own prose. PF-10 and PF-11 are advisory
and do not block freeze on their own.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2
  task_id: NOT SUPPLIED IN THE LAUNCHING HANDOFF; recorded as unsupplied rather than fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v5.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at snapshot d82be3b4, parented on
    c445c171 (the round-1-reviewed draft) -- a revision applying all six
    findings (PF-1, PF-4, PF-5, PF-6, PF-7, PF-8) of
    RT-PREFREEZE-EXP-SSIQ-a85692-v5.md's DO-NOT-FREEZE verdict: PART A adds a
    genuinely new bootstrap_gap_ci_v2 (not an alias) threading
    ols_loglog_fit_v2 through both per-resample fits; PART B states the
    delta_map key<->vertex-tuple conversion procedure explicitly, adds a
    hard-fail coverage assertion, reframes the graph-rebuild verification as
    "independently verified correct" via M-DEGSEQ plus the archived
    per-prime vertex count, and runs the trapped-vs-structural cross-check on
    every resolved vertex.
  objections:
    - "PF-9 [BLOCKING, NEW]: Part B's required coverage assertion (inputs.trapping_mechanism_diagnostic_v5) states the matched-delta_map-key count must equal that prime's archived 'n_resolved/n_vertices count (203/324/478/611...)', treating the two field names as interchangeable. Directly queried against RUN-SSIQ-a85692-b/raw-result.json: n_vertices/len(delta_map) equal 203/324/478/611 for the four primes used, but n_resolved equals 194/306/460/594 -- a different, strictly smaller quantity (confirmed by direct reading of compute_delta_e.py's run_phase_minus1_on_confirmatory_set: n_resolved counts only non-F_p-rational vertices resolved via real search, excluding F_p-rational vertices that resolve for free via delta_E=1 identity and are never counted in n_resolved but are included in delta_map and n_vertices). If an Executor implements the assertion by reading the n_resolved field (the first-named alternative, and a real field at that exact JSON path), the assertion halts with an error on all four primes unconditionally, even when key-conversion, graph rebuild, and vertex matching are all fully correct -- defeating Part B's diagnostic before it can report anything. This defect was not introduced by the Coordinator's revision: it is present verbatim in round 1's own required-fix text and required_controls YAML entry for PF-4, which the revision correctly and faithfully implemented to the letter, propagating round 1's own unverified error forward."
    - "PF-10 [ADVISORY]: Part A's required bootstrap_gap_ci_v2 regression test spec ('resample data constructed so that at least one resample draw reproduces the N=324/n=3 or N=611/n=6 anomaly pattern') does not state its construction mechanism explicitly. The natural, cheapest construction (N_list = [N]*n, n copies of the single anomalous value, guaranteeing every resample is degenerate regardless of rng state) is independently confirmed correct and is also a genuine discriminator against the original PF-1 hollow-fix pattern -- but the spec leaves this implicit rather than stated, unlike its otherwise-precise wiring language elsewhere."
    - "PF-11 [ADVISORY]: PF-5's stated graph-rebuild verification (M-DEGSEQ plus archived vertex count) does not credit that PF-4's own (once PF-9 is fixed) coverage assertion provides additional vertex-set fidelity beyond a plain count -- delta_map's archived key set functions as an implicit archived vertex-set snapshot, catching a same-count, same-degree vertex swap that M-DEGSEQ + count alone would miss. Not stated as a second, independent check in the spec text."
  required_controls:
    - "PF-9: correct the coverage-assertion sentence in inputs.trapping_mechanism_diagnostic_v5 to name only n_vertices (never n_resolved) as the comparison target for matched delta_map keys, with a one-clause note distinguishing the two archived fields (n_resolved counts only non-F_p-rational vertices resolved by real search; n_vertices/len(delta_map) includes the F_p-rational vertices too) -- BLOCKING, zero new search cost, correct numeric values already present in the spec text."
    - "PF-10: state the N_list = [N]*n repeated-value construction explicitly for the bootstrap_gap_ci_v2 regression test -- advisory."
    - "PF-11: cross-reference PF-4's (corrected) coverage assertion as an additional vertex-set-fidelity check alongside M-DEGSEQ in the PF-5 fix text -- advisory."
  counterexample_or_mutation: >-
    PF-9: raw-result.json's phase_minus1_real_search["2437"]["n_resolved"] ==
    194 while ["n_vertices"] == 203 and len(["delta_map"]) == 203, confirmed
    by direct programmatic query. A literal implementation of the coverage
    assertion using the n_resolved field compares a correctly-computed
    matched-key count of 203 against an expected value of 194 and halts with
    an error on a completely correct run -- a direct falsifier of "the
    coverage assertion, as specified, verifies what it claims to verify" for
    the field name the spec text leads with.
    PF-1 (confirming, not falsifying): N_list = [324, 324, 324] fed to a
    hand-simulated bootstrap_gap_ci_v2 loop produces xs = [math.log(324)]*3
    on every resample; max(xs)==min(xs) is True (guard fires) under
    ols_loglog_fit_v2; under the original ols_loglog_fit, sxx =
    2.3665e-30 != 0.0 (guard does not fire) -- confirming this input is a
    genuine discriminator the specified regression test's natural
    construction would correctly exercise.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline remains this
    campaign's own instrument- and fix-scrutiny discipline (GD-4 through
    GD-11), extended one layer further by PF-9: the "trace it, don't trust
    it" standard applies to a prior red-team review's own required-fix
    prose, not only to the Executor's implementation or the Coordinator's
    amendment text.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; PF-9/PF-10/PF-11 are all control/instrument-fidelity or specification-precision gaps."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is unchanged from round 1 and remains realistic and generously sized; PF-9's fix (text correction) and PF-10/PF-11 (text additions) have zero cost impact."
    - "The live concern is evidentiary: as specified, PF-9 would cause Part B's diagnostic to halt with an error on its very first real invocation, on all four primes simultaneously -- a loud, not silent, failure, but one that would consume a dispatch cycle to discover and fix if not caught before freeze."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded. No scope-inflation found."
    - "objective_boundary's scoping of Part B as a diagnostic, not a claim, is unchanged and correctly stated."
    - "This amendment still correctly bundles exactly the two actions DEC-20260805-6aa5c2's next_action named, on disjoint data and code paths -- reconfirmed, unaffected by PF-9 (purely inside Part B's own diagnostic text)."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v5.yaml as committed
    at d82be3b4, status: draft: round 1's three blocking findings (PF-1,
    PF-4, PF-5) and its advisory cross-check-scope finding (PF-6) are all
    genuinely, adequately resolved in this revision, confirmed by
    independent direct tracing against the actual code and archived data --
    bootstrap_gap_ci_v2 unambiguously threads ols_loglog_fit_v2 through both
    per-resample fit calls (PF-1); tuple(json.loads(key)) correctly and
    exactly recovers the archived vertex tuples, type included (PF-4's
    conversion procedure); M-DEGSEQ plus archived vertex count is the best
    available graph-rebuild check given no adjacency was ever archived,
    honestly framed (PF-5); the exhaustive cross-check is computationally
    negligible (PF-6). PF-7/PF-8 advisory text is applied correctly. One new
    blocking defect was found: the coverage assertion PF-4's fix requires
    names n_resolved and n_vertices as interchangeable, but they are
    different, unequal archived quantities (194/306/460/594 vs
    203/324/478/611) -- inherited verbatim from round 1's own required-fix
    language and faithfully implemented by this revision, so the defect is
    in a prior review's prose, not in the Coordinator's execution of it
    (PF-9, blocking, one-sentence fix, correct values already present in the
    text). PF-10/PF-11 are advisory precision notes. None require redesign.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text to (1) fix PF-9 by naming only n_vertices (never n_resolved) as the
    coverage-assertion's comparison target, with a one-clause note
    distinguishing the two archived fields; (2) apply PF-10/PF-11 as
    text-only additions. Re-verify PF-9's specific trace once fixed before
    freeze, per this campaign's standing practice. None of PF-9/PF-10/PF-11
    requires new search or touches any already-archived run's data. Given
    PF-9 is a single, precisely-located sentence-level correction with the
    correct values already present in the text, and every other round-1
    finding is confirmed genuinely resolved, this does not warrant a third
    full DO-NOT-FREEZE cycle -- but freeze must not occur before PF-9's text
    is corrected and re-checked.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Executed directly (not merely traced): tuple(json.loads(str(list(v))))
    round-trip for v=(1031,1095), confirming exact tuple and int-type
    recovery, cross-checked against a plausible-wrong str(v) alternative
    that fails json.loads outright. Loaded RUN-SSIQ-a85692-b/raw-result.json
    programmatically and queried n_vertices, n_resolved, len(delta_map), and
    m_coverage_all_vertices_fraction for all five primes directly (not from
    any prose description), which is what surfaced PF-9. Hand-simulated
    max(xs)==min(xs) and the original sxx computation for N_list=[324,324,324]
    to confirm PF-1's regression-test construction actually discriminates
    between the hardened and unhardened guard. Direct source reads (not
    summaries) of dht.bootstrap_gap_ci/ols_loglog_fit,
    build_isogeny_graph.py's degree_sequence_check/build_graph_bfs/
    neighbors_2isogenous, and compute_delta_e.py's
    run_phase_minus1_on_confirmatory_set (to determine what n_resolved
    actually counts). git log/git status confirmed descent_hitting_time.py
    has exactly one commit and no working-tree changes, and confirmed
    specification_v5.yaml's current committed state (d82be3b4) and clean
    working tree. No graph built, no delta_E search run, no file written
    outside this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v5.yaml itself),
    the round-1 report, and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
