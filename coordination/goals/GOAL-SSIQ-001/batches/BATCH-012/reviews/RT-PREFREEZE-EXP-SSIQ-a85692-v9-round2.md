# RT-PREFREEZE-EXP-SSIQ-a85692-v9-round2 — Round 2 pre-freeze Red Team
# review of the DRAFT amendment `specification_v9.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-012, task `TASK-20260806-b1380b`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v9.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED` (round 1 verdict
recorded), committed at `15172d65c0bfc8ba27c42691f41d786cf429df85` —
confirmed by direct diff that the working tree exactly matches this commit
(`git show 15172d65:...specification_v9.yaml | diff - <working tree>` empty).
This is the Coordinator's revision applying all four round-1 findings
(PF-1 blocking, PF-2/PF-3/PF-4 advisory) from
`RT-PREFREEZE-EXP-SSIQ-a85692-v9.md`. Per this task's operating rules, only
Coordinator-committed snapshots are treated as durable evidence; this review
is advisory pre-freeze input on a still-unfrozen draft (`frozen_at: null`).**

Round 1's findings and their full basis are taken as read and cited, not
re-derived, except where this round found reason to revisit them: the
seed-isolation mechanism trace, the core `194 * 0.5 = 97.0` / `600/97.0 ≈
6.19x` budget arithmetic, and the `OBJECTIVE_BOUNDARY` scope discipline all
still hold (round 1 §2, §3, §5) and were spot-checked, not re-derived, below.

Read/executed this round, directly against the committed tree, not trusted
from prose: `git diff f400803d 15172d65 -- specification_v9.yaml` (the exact
textual delta the Coordinator applied — confirmed to touch *only* the four
PF-1–PF-4 locations round 1 named, nothing else); `specification_v9.yaml` in
full (403 lines, current); `trapping_diagnostic_v5.py:90-130`
(`load_archived_prime_data`'s real source, including its actual collision
check `len(delta_map) != len(raw_delta_map)`); `delta_e_independent_rng_probe_v8.py:517-775`
(`main()`'s actual write-order architecture — where PART A/PART B results
are held in memory and all artifacts written only at the very end); direct
Python execution against the real committed files:
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`'s `new_delta_map` (all 203
keys, full `tuple(json.loads(key))` round-trip, collision check, coverage
fields) and `RUN-SSIQ-a85692-b/raw-result.json`'s `delta_map` for p=2437
(same round-trip check); `git log`/`git show` on `specification_v6.yaml`'s
own prior round-1→round-2 transition, to check whether `pre_freeze_review.status: REVIEWED`
mid-process (before round 2 has run) is this lineage's established
convention or a new anomaly.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified this session.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. Standing condition
    for this lineage, not re-discovered here.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Shares a model family
    with the Executor, the Coordinator, and every prior reviewer in this
    lineage (including this amendment's own round-1 reviewer). Does not
    upgrade the campaign's evidence tier and does not itself satisfy or
    advance a closure quorum.
```

---

## Bottom line up front

**FREEZE-WITH-FIXES.** PF-1's fix is correct and complete on direct trace
against the real committed files, not merely on the corrected prose being
internally consistent: the new text cites only
`probe_delta_e_comparison.json`; the specified `tuple(json.loads(key))`
round-trip is precise (not the ambiguous "just `json.loads`" a careless
Executor might implement) and I independently re-ran it against all 203 real
keys in that file — zero collisions, zero parse failures, exact match to the
spec's own worked example; the specified collision/injectivity check is
verbatim the same check `load_archived_prime_data` itself performs, verified
by reading that function's real source. PF-2's corrected arithmetic
(`277.85/97.0 = 2.864`, `278.5/97.0 = 2.871`) is independently re-verified
exactly correct in both places it appears. PF-3 and PF-4's disclosures are
accurate, narrowly scoped, and introduce no new claim beyond what round 1
asked for. One genuine, round-1-adjacent finding (PF-5, advisory, not
blocking): the spec still does not require that PART A's own core
measurement be written to disk independent of Comparison 2's outcome — the
exact *architectural* shape that produced v8's PF-1/PF-9, now narrowed rather
than eliminated. I traced this concretely and found the specific triggering
conditions are closed for *this* run (the source file is fixed, read-only,
and I directly verified it parses cleanly with zero collisions; v8's own
`new_delta_map` has full 203/203 coverage, so no vertex lookup from this
run's own graph can miss), so this is not a live crash risk for this
specific dispatch — but the spec still lacks the general write-order/failure-
isolation discipline this lineage's own standing repair exists to enforce,
and it is a zero-cost textual fix worth making explicit before or shortly
after freeze.

1. **PF-1 fix: CONFIRMED CORRECT AND COMPLETE**, by direct execution against
   the real files, not by re-reading corrected prose. See §1.
2. **PF-5 [NEW, ADVISORY, not blocking]: the fix closes the specific PF-1
   defect but leaves the general architectural pattern that produced it
   (a downstream comparison's failure can discard PART A's own already-valid
   core result) unaddressed in spec text.** The concrete trigger is verified
   closed for this run; the general discipline gap is real and cheap to fix.
   See §1.4.
3. **PF-2 fix: CONFIRMED CORRECT.** `277.85/97.0 = 2.864`, `278.5/97.0 =
   2.871`, both exactly matching the spec's own corrected figures. See §2.
4. **PF-3 and PF-4 disclosures: accurate, narrowly worded, no new claims.**
   See §3.
5. **Fresh pass: no other defect found.** The diff is confirmed surgical —
   touches only the four PF-1–PF-4 locations round 1 named, nothing else —
   and `pre_freeze_review.status: REVIEWED` mid-process (before round 2 has
   run) is this lineage's own established convention (confirmed against
   `specification_v6.yaml`'s identical round-1→round-2 checkpoint), not a
   new anomaly. See §4.

---

## (1) Re-verifying PF-1's fix against the real committed files

### 1.1 Source-file citation

Confirmed by direct read of the current draft (lines 234–253): the text now
reads "CITED, CORRECTED: load ONLY
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`
... — NOT raw-result.json, which lacks this field entirely." No remaining
reference anywhere in the current draft cites `raw-result.json` as a source
for `new_delta_map` (grep-equivalent read of the full file confirms this is
the only place the field is discussed, and it is stated unambiguously).
`required_artifacts_note` (lines 350–356) independently repeats the same
corrected citation. **Confirmed fixed.**

### 1.2 Does the specified round-trip actually work?

The spec's worked example is precise, not ambiguous:

> "for every key, apply `tuple(json.loads(key))` to recover the vertex
> tuple — e.g. `json.loads("[1031, 1095]") == [1031, 1095]`, then
> `tuple(...) == (1031, 1095)`."

This is the *correct* two-step construction (parse to `list`, then wrap in
`tuple`), not the common ambiguous shortcut a careless Executor might
mis-implement as `json.loads(key)` alone (which returns a `list`, not
hashable, and would raise `TypeError: unhashable type: 'list'` the first
time it was used as a dict key) or `tuple(key)` (which would iterate the
*string* `"[1031, 1095]"` character-by-character, producing garbage). The
spec text is explicit about both steps, in the correct order, with a
concrete worked example the Executor can literally test against.

I independently re-ran this exact construction against all 203 real keys in
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`'s `new_delta_map`:

```
$ python3 -c "
import json
d = json.load(open('experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json'))
ndm = d['new_delta_map']
parsed = {}
collisions = 0
for k, v in ndm.items():
    t = tuple(json.loads(k))
    if t in parsed: collisions += 1
    parsed[t] = v
print(len(ndm), len(parsed), collisions)"
203 203 0
```

Zero parse failures, zero collisions, 203-in/203-out. The spec's own worked
example (`"[1031, 1095]" -> (1031, 1095)`) matches the real first key in the
file exactly. **Confirmed: the round-trip works on all 203 real keys, as
specified, with no collisions.**

### 1.3 Is the disclosed collision check well-specified and accurate?

The spec text (lines 263–267) says: "Perform the SAME collision/injectivity
check `load_archived_prime_data` itself performs (assert the parsed-tuple
keyset has the same cardinality as the raw string keyset, i.e. no two
distinct string keys parse to the same tuple; raise loudly if not)."

I read `load_archived_prime_data`'s real source
(`trapping_diagnostic_v5.py:102–130`) directly, not from any prior review's
paraphrase:

```python
for key_str, delta_val in raw_delta_map.items():
    vertex = tuple(json.loads(key_str))
    delta_map[vertex] = delta_val
if len(delta_map) != len(raw_delta_map):
    raise TrappingDiagnosticError(
        "PF-4 key round-trip produced %d distinct vertex tuples from "
        "%d raw delta_map keys for p=%d -- a collision in the "
        "tuple(json.loads(key)) round-trip, which should be injective" ...)
```

This is *exactly* "assert the parsed-tuple keyset has the same cardinality
as the raw string keyset... raise loudly if not" — a cardinality comparison
(`len(delta_map) != len(raw_delta_map)`) after a dict-comprehension-style
build, not a per-key duplicate check during the loop, but functionally
identical (a dict silently drops a colliding key on overwrite, so the final
`len()` mismatch catches exactly the same condition). The spec's description
matches the real check precisely, not just gesturally. **Confirmed accurate.**

### 1.4 Hunting for a new, PF-1-adjacent crash path (PF-5)

This is the question round 1 could not have asked, since it never got past
the schema mismatch to consider what happens *after* a correct parse.
Applying this campaign's own recurring lesson (v8's PF-1/PF-9: a required
step whose failure discards an unrelated, already-valid, more important
result) to the *fixed* Comparison 2 code specifically:

I read `delta_e_independent_rng_probe_v8.py`'s actual `main()`
(`.py:517–775`) — the one existing, frozen, committed implementation in this
lineage that this amendment's own new module is explicitly modeled on (same
PROCEDURE numbering, same "rebuild graph → PART A search → comparison(s) →
write" shape). Its real architecture: PART A's result
(`part_a_result`), the archived comparison, and (when the coverage gate
passes) PART B's result are all computed and held **in memory**; *every*
artifact write (`probe_delta_e_comparison.json`, `probe_permutation_null_control.json`,
`raw-result.json`) happens only at the very end (lines 643–766), after all
computation has completed with no exception. There is no
try/except anywhere in `main()` isolating an earlier step's already-computed,
valid result from a later step's failure — this is precisely the shape that
made PF-1/PF-9 catastrophic in the first place (an unresolved-vertex
KeyError inside PART B, computed *after* PART A, discarded PART A's own
valid result because nothing had been written to disk yet).

`specification_v9.yaml`'s current text (round 1's fixed version) still does
not instruct the Executor to write PART A's own core measurement
(`n_resolved`, `n_timed_out`, `coverage_fraction`, `new_delta_map`) to disk,
or otherwise protect it, independently of whether Comparison 2's new parsing
step (`parse_v8_new_delta_map`) succeeds. If an Executor follows this
lineage's own established `main()` pattern (compute everything, write once
at the end — the only pattern this lineage has ever used), then **any**
exception raised inside Comparison 2's code — not just the specific
KeyError PF-1 named, which is now closed, but *any* future failure (e.g. an
`IOError` if the file path is wrong, a `json.JSONDecodeError`, or the
collision check's own deliberately-required `raise` on a future schema
drift) — would still propagate uncaught and discard PART A's own
already-computed, more important result, exactly mirroring PF-1/PF-9's
shape, just with the specific trigger changed from "wrong schema" to
"anything else that could go wrong in Comparison 2."

**However, I traced whether this is a *live* risk for *this specific*
dispatch, not merely a hypothetical residual concern, and found it is not:**

- The source file (`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`) is
  fixed, already committed, and I directly re-verified it parses with zero
  collisions and zero malformed keys (§1.2) — the collision-check `raise`
  branch is deterministically dead for this exact input.
- `RUN-SSIQ-a85692-h`'s own `new_delta_map` has **full 203/203 coverage**
  (directly confirmed: `n_resolved=194, n_non_fp_rational=194,
  coverage_fraction=1.0, len(new_delta_map)=203` — v8's 15.0s budget never
  truncated), and it is built from the *identical* rebuilt graph/vertex set
  v9 will use (same seed, same `build_graph_for_prime` call). So every
  vertex v9's own run could possibly resolve is guaranteed to be a key in
  the parsed map — the KeyError-on-lookup failure mode that made v8's PART B
  crash-prone (missing keys for *some* vertices under partial coverage) is
  structurally impossible here, because the comparison target has full
  coverage by construction.
- A file-not-found/IOError is essentially ruled out since the file is
  already committed, read-only, and its path is a literal string in the
  spec, not derived at runtime.

So this is an **advisory, not blocking**, finding: the general discipline
gap is real, cheap to close, and consistent with the campaign's own stated
value of not repeating a failure *shape* even when the specific trigger is
gone — but I found no live path by which it would fire for this run's real
inputs.

**Required control (PF-5, advisory, zero cost, recommended before or
promptly after freeze):** add one sentence to `required_artifacts_note` or
`amendment_scope` requiring that PART A's own core measurement
(`n_resolved`, `n_timed_out`, `coverage_fraction`, `new_delta_map`) be
captured into the run's written artifacts (or otherwise protected, e.g. via
a try/except around Comparison 2 that records a `comparison_2_error` field
rather than propagating) independent of whether Comparison 1 or Comparison 2
succeed — matching this lineage's own coverage-gate discipline (v8's PF-1/
PF-9 fix gated PART B's *execution* on a coverage check; this amendment
should equivalently gate Comparison 2's *ability to erase* PART A's result,
not merely fix the one input schema that made it crash this round).

## (2) PF-2 arithmetic re-verification

```
$ python3 -c "print(277.85/97.0); print(278.5/97.0)"
2.8644329896907217
2.8711340206185567
```

The current draft states `277.85/97.0 = 2.864` (amendment_scope, line 109)
and `278.5/97.0 = 2.871` (budget.note, line 374) — both exact matches to
independent recomputation, correctly rounded to three decimal places.
**Confirmed correct**, both instances.

## (3) PF-3 / PF-4 disclosure sanity check

**PF-3** (lines 378–389): states exact per-vertex resolved/timed-out counts
under the 0.5s budget are not bit-for-bit reproducible across hardware,
since where the wall-clock cutoff lands (not the pinned seed) depends on
machine speed/load — this is exactly round 1's own finding (§2 there),
restated accurately, with no broader or narrower claim added.

**PF-4** (lines 390–400): states the 0.5s budget is a soft cap (checked only
between heap-pop iterations, never mid-call), consistent with round 1's
finding, correctly cites the same code location
(`compute_delta_e.py`'s `build_smooth_table` loop), and correctly notes the
600s/97.0s (~6.19x) margin makes this unlikely to matter — no new numeric
claim, no overclaim. **Both confirmed accurate, no new claim beyond round
1's own ask.**

## (4) Fresh pass for anything else

`git diff f400803d 15172d65 -- specification_v9.yaml` (reproduced above)
confirms the applied fix is **surgical**: it touches exactly four locations
(the two "Nx smaller" arithmetic spots, the `pre_freeze_review` metadata
block, and REQUIRED COMPARISON 2's text plus its `required_artifacts_note`
mirror) — nothing else in the 403-line file changed. This rules out an
edit-introduced regression anywhere outside the four named findings.

One process question worth resolving explicitly rather than silently
assuming: `pre_freeze_review.status: REVIEWED` while `experiment.status:
draft` and `frozen_at: null` — does "REVIEWED" mid-process (before round 2
has actually run) misrepresent this draft as review-complete? I checked
this lineage's own prior precedent rather than guessing: `specification_v6.yaml`
went through an identical three-round pre-freeze history (round 1 → fix →
round 2 → fix → round 3 → freeze). At the exact analogous checkpoint in its
own git history (commit `6ae7847f`, "v6 draft revised after DO-NOT-FREEZE
(round 1)," i.e. round-1-fixed-pending-round-2), its `pre_freeze_review.status`
was **also** `REVIEWED`, with `experiment.status: draft` unchanged. This is
this lineage's own established, consistent convention across at least two
prior multi-round amendments (v6, and v8 itself used the identical pattern
at its own final freeze), not a new or ambiguous labeling choice introduced
by this fix. No objection.

No other inconsistency, wrong claim, or newly-introduced defect found on a
fresh line-by-line read of the current 403-line draft.

---

## Objections

- **OBJ-1 [informational, not a defect]**: PF-1's fix is confirmed correct
  and complete on direct execution against the real committed files: the
  source-file citation now names only `probe_delta_e_comparison.json`; the
  `tuple(json.loads(key))` round-trip is precisely specified (not the
  ambiguous shortcut a careless implementation might use) and independently
  re-verified to work on all 203 real keys with zero collisions; the
  disclosed collision check is verbatim the same check
  `load_archived_prime_data` itself performs, confirmed by reading its real
  source. No remaining objection to PF-1's fix itself.
- **OBJ-2 [PF-5, NEW, advisory, not blocking]**: the fix closes the specific
  KeyError/schema-mismatch defect PF-1 named but leaves the general
  architectural pattern that produced it — a downstream comparison step's
  failure, of any kind, can discard PART A's own already-computed, more
  important result, because this lineage's own established `main()`
  architecture (`delta_e_independent_rng_probe_v8.py:517-775`, confirmed by
  direct read) writes all artifacts only at the very end with no
  try/except isolating earlier results — unaddressed in spec text. Traced
  concretely: the specific triggering conditions (a missing key, a
  malformed source file, a real collision) are all verified closed for this
  run's actual inputs (`RUN-SSIQ-a85692-h`'s `new_delta_map` has full
  203/203 coverage and zero collisions on direct re-verification), so this
  is not a live crash risk for this dispatch, but the general discipline gap
  is real and cheap to close.
- **OBJ-3 [informational]**: PF-2's corrected arithmetic (`277.85/97.0 =
  2.864`, `278.5/97.0 = 2.871`) is independently re-verified exactly
  correct in both places it appears.
- **OBJ-4 [informational]**: PF-3 and PF-4's disclosures are accurate,
  narrowly worded, and add no claim beyond what round 1 asked for.

## Required controls

- **[PF-5, advisory, recommended before or promptly after freeze, zero
  cost]**: add one sentence requiring PART A's own core measurement
  (`n_resolved`, `n_timed_out`, `coverage_fraction`, `new_delta_map`) be
  captured/written independent of whether Comparison 1 or Comparison 2
  succeed (e.g. a try/except around Comparison 2 recording a
  `comparison_2_error` field on failure, rather than an uncaught exception
  that discards everything computed so far) — matching this lineage's own
  coverage-gate discipline from v8's PF-1/PF-9 fix, extended to cover any
  failure mode in Comparison 2, not only the one PF-1 named. Does not block
  this freeze given the concrete trigger is verified closed for this run's
  real, fixed, already-verified inputs.
- None of the round-1 findings (PF-1 through PF-4) require further action;
  all four are confirmed correctly and completely applied.

## Counterexample or mutation

No live counterexample found against the fixed PF-1 text — directly
demonstrated by re-running the specified round-trip against all 203 real
keys in the actual committed file (§1.2): zero parse failures, zero
collisions. For PF-5, the counterexample is hypothetical-but-real-shaped,
not live for this dispatch: *if* `probe_delta_e_comparison.json` were ever
replaced, corrupted, or moved (it will not be, for this run — it is
read-only and already committed), or if a future amendment reused this
amendment's `parse_v8_new_delta_map` against a differently-shaped file the
way v9's original draft mistakenly pointed `load_archived_prime_data` at the
wrong file, the resulting exception would (per the same `main()`-style
architecture) still discard PART A's own valid result with no isolation —
this is the concrete mutation that would expose the gap, and it is the same
class of mutation (source-file substitution) that produced PF-1 itself.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
search-procedure diagnostic work, `H-SSIQ-36e970.asymptotic_claim: null`
throughout, unchanged by this fix. The relevant baseline remains this
lineage's own code-verified-crash-path and GD-9/GD-10 required-artifacts-
accuracy standard, now additionally including the standing PF-1/PF-9
write-order lesson (round 1's own §1 already named both failure modes;
this round confirms the narrower one is closed and the broader
architectural one is not, though currently dormant for this run's real
inputs).

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains empty; `asymptotic_claim: null`
throughout; unchanged by this round's fix. No numbered heuristic implicated.

## Cost model challenges

No asymptotic-cost claim anywhere in this amendment. Both of PF-2's
corrected decorative comparisons (`~2.864x`, `~2.871x`) are independently
re-verified exactly correct; the safety-critical `194*0.5=97.0` /
`600/97.0≈6.19x` budget arithmetic, already re-verified in round 1, was
spot-checked again and still holds (unchanged by this round's diff, per
`git diff f400803d 15172d65`). No total-expected-cost computation is needed
or attempted — this remains a bounded, single-run, non-probabilistic-success
diagnostic.

## Reduction and scope challenges

No affected/safe cryptographic scheme list appears anywhere in this
amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) unchanged and not
exceeded. `OBJECTIVE_BOUNDARY` text (lines 292-304) is unchanged by this
round's diff (confirmed via `git diff f400803d 15172d65`, which does not
touch this block) — round 1's own clean finding here still holds without
re-derivation. No scope inflation found.

## Proof architecture challenges

Not applicable — unchanged from round 1's finding; this remains a direct
instrument-level search-procedure diagnostic, not a proof-oriented proposal.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v9.yaml` as committed
at `15172d65c0bfc8ba27c42691f41d786cf429df85` (draft, `pre_freeze_review.status:
REVIEWED`, round-1 findings applied): PF-1's fix is confirmed correct and
complete by direct execution against the real committed `RUN-SSIQ-a85692-h`
artifacts, not merely by re-reading the corrected prose — the round-trip
works on all 203 real keys with zero collisions, and the disclosed collision
check matches `load_archived_prime_data`'s real source exactly. PF-2's
corrected arithmetic is independently re-verified exactly correct in both
places. PF-3 and PF-4's disclosures are accurate and add no new claim. One
new, advisory (not blocking) finding: the fix closes the specific schema
mismatch but not the general architectural pattern (an unprotected
downstream-comparison failure discarding PART A's own valid, already-
computed result) that produced it — verified dormant, not live, for this
specific dispatch's actual fixed, already-verified inputs. This draft is
**safe to freeze**; PF-5 should be applied in the same or a prompt follow-up
pass but does not block this freeze.

## Next concrete action

Coordinator: this draft is ready to freeze. Optionally fold PF-5's one-
sentence write-order/failure-isolation requirement into the frozen text in
the same pass (zero cost, textual only, matching this lineage's own
coverage-gate discipline); if deferred, record it as a named, open advisory
item in the frozen spec's `freeze_note` so it is not silently dropped.
Dispatch `RUN-SSIQ-a85692-i` (confirmed: this run ID does not yet exist
under `experiments/EXP-SSIQ-a85692/runs/`) per the frozen budget (600s wall
clock, 97.0s worst-case bound, ~6.19x margin, independently re-verified
correct this round and in round 1).

## Overall verdict

**FREEZE-WITH-FIXES.** PF-1 (blocking, round 1) is confirmed correctly and
completely fixed by direct execution against the real committed files.
PF-2/PF-3/PF-4 (advisory, round 1) are all confirmed correctly applied. One
new advisory finding this round, PF-5 (not blocking): the fix closes the
specific defect but not the general architectural pattern behind it; the
concrete trigger is verified closed for this run's real inputs, so it does
not block freeze, but should be applied in the same or a prompt follow-up
pass as a zero-cost textual addition, consistent with this lineage's own
standing discipline against this exact failure shape.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v9-round2
  task_id: TASK-20260806-b1380b
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v9.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: REVIEWED,
    findings_applied: [PF-1, PF-2, PF-3, PF-4]), committed at
    15172d65c0bfc8ba27c42691f41d786cf429df85 -- the Coordinator's revision of
    the round-1-reviewed draft applying round 1's one blocking finding
    (PF-1: wrong source-file citation and unhandled key-format mismatch in
    REQUIRED COMPARISON 2) and three advisory findings (PF-2: arithmetic
    error; PF-3: reproducibility caveat; PF-4: soft-cap disclosure). Round 2
    pre-freeze review, second and (per this round's finding) likely final
    round for this amendment before freeze.
  objections:
    - "OBJ-1 [informational]: PF-1's fix is confirmed correct and complete on direct execution against the real committed files, not merely on re-reading corrected prose. The source-file citation now names only probe_delta_e_comparison.json (raw-result.json is no longer cited anywhere for new_delta_map, confirmed by full-file read). The specified tuple(json.loads(key)) round-trip is precise (parse-to-list then wrap-in-tuple, in the correct order, with a concrete worked example matching the file's real first key exactly) and I independently re-ran it against all 203 real keys in RUN-SSIQ-a85692-h/probe_delta_e_comparison.json's new_delta_map: 203 keys in, 203 distinct tuples out, zero parse failures, zero collisions. The disclosed collision/injectivity check ('assert the parsed-tuple keyset has the same cardinality as the raw string keyset... raise loudly if not') is verbatim the same check load_archived_prime_data itself performs (trapping_diagnostic_v5.py:117-122: len(delta_map) != len(raw_delta_map) -> raise TrappingDiagnosticError), confirmed by reading that function's actual source this round, not merely trusting a prior paraphrase."
    - "OBJ-2 [PF-5, NEW, advisory, not blocking]: the applied fix closes the specific KeyError/schema-mismatch defect PF-1 named but leaves the general architectural pattern that produced it unaddressed in spec text -- a downstream comparison step's failure, of any kind, can still discard PART A's own already-computed, more important result, because this lineage's own established main() architecture (delta_e_independent_rng_probe_v8.py:517-775, confirmed by direct read) computes everything in memory and writes all artifacts only at the very end, with no try/except isolating an earlier step's valid result from a later step's exception -- the identical shape that made v8's own PF-1/PF-9 catastrophic. Traced concretely for THIS dispatch's real inputs: RUN-SSIQ-a85692-h's new_delta_map has full 203/203 coverage (n_resolved=194/194, coverage_fraction=1.0, directly re-confirmed), so no vertex v9's own run could resolve can be missing from it, ruling out the KeyError-on-lookup failure mode; the source file is fixed, committed, read-only, and directly re-verified to parse with zero collisions, ruling out the collision-check raise branch. So this is not a live crash risk for this specific dispatch, but the general discipline gap -- that Comparison 2's ANY future failure mode, not just the one PF-1 named, is still architecturally capable of discarding PART A's own valid result -- is real and cheap to close."
    - "OBJ-3 [informational]: PF-2's corrected arithmetic is independently re-verified exactly correct in both places it appears: 277.85/97.0 = 2.8644... (spec states 2.864, matches) and 278.5/97.0 = 2.8711... (spec states 2.871, matches)."
    - "OBJ-4 [informational]: PF-3 (hardware-reproducibility caveat on per-vertex truncation timing) and PF-4 (soft, not hard, per-vertex budget cap) are both accurately worded, correctly cite the same code locations round 1 identified, and introduce no claim beyond what round 1 asked for."
  required_controls:
    - "[PF-5, advisory, recommended before or promptly after freeze, zero cost]: add one sentence requiring PART A's own core measurement (n_resolved, n_timed_out, coverage_fraction, new_delta_map) be captured/written independent of whether Comparison 1 or Comparison 2 succeed (e.g. a try/except around Comparison 2 recording a comparison_2_error field on failure rather than an uncaught exception that discards everything computed so far) -- extending this lineage's own v8 PF-1/PF-9 coverage-gate discipline to cover any Comparison-2 failure mode, not only the specific schema mismatch PF-1 named. Does not block this freeze: the concrete trigger is verified closed for this run's real, fixed, already re-verified inputs (full 203/203 coverage in the comparison target, zero collisions in the source file)."
    - "None of round 1's PF-1 through PF-4 require further action -- all four independently re-verified correctly and completely applied this round."
  counterexample_or_mutation: >-
    No live counterexample against the fixed PF-1 text: independently
    re-running the specified tuple(json.loads(key)) round-trip against all
    203 real keys in the actual committed RUN-SSIQ-a85692-h/probe_delta_e_
    comparison.json produces zero parse failures and zero collisions. For
    PF-5, the concrete (non-live-for-this-run) mutation that would expose
    the gap: substitute a differently-shaped or malformed source file for
    probe_delta_e_comparison.json (the same class of mutation that produced
    PF-1 itself) -- given this lineage's own established write-everything-
    at-the-end main() architecture (confirmed by direct read of
    delta_e_independent_rng_probe_v8.py:517-775), the resulting exception
    would still discard PART A's own valid, already-computed result, since
    no write-order or exception-isolation discipline protects it.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale search-procedure diagnostic work, H-SSIQ-36e970.asymptotic_claim
    null throughout, unchanged. The relevant baseline remains this lineage's
    own code-verified-crash-path and GD-9/GD-10 required-artifacts-accuracy
    standard, now including the standing PF-1/PF-9 write-order lesson: round
    1 already named both failure modes (crash-before-write and
    silent-vacuous-result); this round confirms the narrower, specific one
    (wrong schema) is closed by direct re-verification, and the broader
    architectural one (any Comparison-2 failure can still erase PART A) is
    not textually addressed, though it is currently dormant given this run's
    real, fixed, already-verified inputs.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions remains empty; asymptotic_claim: null throughout; unchanged by this round's fix. No numbered heuristic implicated."
  cost_model_challenges:
    - "No asymptotic-cost claim anywhere in this amendment. PF-2's corrected decorative comparisons (277.85/97.0 = 2.864, 278.5/97.0 = 2.871) are both independently re-verified exactly correct. The safety-critical 194*0.5=97.0s / 600/97.0~=6.19x budget arithmetic, already re-verified in round 1 and unchanged by this round's diff (confirmed via git diff f400803d 15172d65, which does not touch this text), still holds. No total-expected-cost computation is needed or attempted -- this remains a bounded, single-run, non-probabilistic-success diagnostic."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) unchanged and not exceeded."
    - "OBJECTIVE_BOUNDARY text is unchanged by this round's diff (confirmed via git diff f400803d 15172d65, which does not touch this block) -- round 1's own clean finding here still holds without re-derivation. No scope inflation found."
  proof_architecture_challenges:
    - "Not applicable -- unchanged from round 1's finding; this remains a direct instrument-level search-procedure diagnostic, not a proof-oriented proposal."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v9.yaml as committed
    at 15172d65c0bfc8ba27c42691f41d786cf429df85 (draft,
    pre_freeze_review.status: REVIEWED, findings_applied: [PF-1, PF-2, PF-3,
    PF-4]): PF-1's fix is confirmed correct and complete by direct execution
    against the real committed RUN-SSIQ-a85692-h artifacts, not merely by
    re-reading corrected prose -- the round-trip works on all 203 real keys
    with zero collisions, and the disclosed collision check matches
    load_archived_prime_data's real source exactly. PF-2's corrected
    arithmetic is independently re-verified exactly correct in both places.
    PF-3 and PF-4's disclosures are accurate and add no new claim beyond
    round 1's ask. One new, advisory (not blocking) finding (PF-5): the fix
    closes the specific schema mismatch but not the general architectural
    pattern (an unprotected downstream-comparison failure discarding PART
    A's own valid, already-computed result) that produced it -- verified
    dormant, not live, for this specific dispatch's actual fixed,
    already-verified inputs (full 203/203 coverage in the comparison
    target, zero collisions in the source file). This draft is safe to
    freeze; PF-5 should be applied in the same or a prompt follow-up pass
    but does not block this freeze.
  next_concrete_action: >-
    Coordinator: this draft is ready to freeze. Optionally fold PF-5's
    one-sentence write-order/failure-isolation requirement into the frozen
    text in the same pass (zero cost, textual only, matching this lineage's
    own coverage-gate discipline from v8's PF-1/PF-9 fix); if deferred,
    record it as a named, open advisory item in the frozen spec's
    freeze_note so it is not silently dropped. Dispatch RUN-SSIQ-a85692-i
    (confirmed this run ID does not yet exist under
    experiments/EXP-SSIQ-a85692/runs/) per the frozen budget (600s wall
    clock, 97.0s worst-case bound, ~6.19x margin, independently re-verified
    correct this round and in round 1).
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v9-round2.md
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v9.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run -- this review is a specification
    and artifact-schema trace, not an execution. Non-durable, read-only
    local Python computations run directly against the committed tree to
    confirm (a) tuple(json.loads(key)) applied to all 203 real keys in
    RUN-SSIQ-a85692-h/probe_delta_e_comparison.json's new_delta_map produces
    203 distinct tuples, zero collisions; (b) the identical round-trip
    against RUN-SSIQ-a85692-b/raw-result.json's delta_map for p=2437
    produces 203 distinct tuples, zero collisions; (c) 277.85/97.0 =
    2.8644..., 278.5/97.0 = 2.8711...; (d) RUN-SSIQ-a85692-h's own
    coverage_fraction=1.0, n_resolved=194/194, len(new_delta_map)=203. Also
    read, directly: trapping_diagnostic_v5.py:90-130 (load_archived_prime_
    data's real source and real collision check);
    delta_e_independent_rng_probe_v8.py:517-775 (main()'s real write-order
    architecture); git diff f400803d 15172d65 -- specification_v9.yaml (the
    exact applied textual delta, confirmed surgical -- touches only the
    four PF-1-PF-4 locations); git show 6ae7847f:specification_v6.yaml (to
    confirm pre_freeze_review.status: REVIEWED mid-process is this
    lineage's established convention, not a new anomaly); full current
    specification_v9.yaml (403 lines); round 1's full report
    (RT-PREFREEZE-EXP-SSIQ-a85692-v9.md). No file was written or modified
    by these computations beyond this report; no run artifact, specification
    file, or ledger record was written or edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v9-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v9.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
