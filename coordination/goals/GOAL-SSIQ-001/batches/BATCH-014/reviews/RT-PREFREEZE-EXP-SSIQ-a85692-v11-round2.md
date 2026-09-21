# RT-PREFREEZE-EXP-SSIQ-a85692-v11-round2 — Round 2 pre-freeze Red Team
# review of the DRAFT amendment `specification_v11.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-014, task `TASK-20260807-43d16f-r2`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v11.yaml` at
`status: draft`, `approved_by: null`, `frozen_at: null`,
`pre_freeze_review.status: ROUND_1_COMPLETE_ROUND_2_PENDING`, committed at
`2256c925b6c8676b520ab6821a3a1be35c102afe` (confirmed: that commit is this
file's most recent touching commit AND is the checked-out `HEAD`; working
tree clean; 1184 lines, up from round 1's reviewed 329-line snapshot at
`6b6703ee2`) — the Coordinator's round-2 revision applying all six round-1
findings (PF-11…PF-14 blocking, PF-15/PF-16 advisory).** This is a targeted,
scoped round 2 per this task's own instructions: independently recompute the
pre-registered prediction curve from the committed artifact rather than
check it against the draft's prose; test whether the defer gate is a genuine
hard precondition; re-verify PF-12's restated semantics against the real
frozen code; check CAL-1/CAL-2 implementability and the duplicate
classification; check the budget arithmetic; and do one fresh pass for
defects the revision itself introduced. Round 1's own confirmed-sound
findings (seed isolation, function existence/signatures, scope discipline,
PF-2/PF-7/PF-8/PF-9/PF-10 pre-application) are cited as still holding, not
re-derived. **No implementation file for v11 exists yet** (confirmed: no
`*v11*` file under `experiments/EXP-SSIQ-a85692/implementation/`) — this
remains a plan audit, not an execution audit. This review is advisory
pre-freeze input on a draft and changes nothing under `experiments/` or
`ledger/`.

Read in full: `specification_v11.yaml` (1184 lines, in full, not from diff);
`RT-PREFREEZE-EXP-SSIQ-a85692-v11.md` (round 1, PF-11…PF-16, in full);
`COORD-VERIFY-PREFREEZE-v11.md`; `specification_v10.yaml` (frozen
predecessor); `RT-PREFREEZE-EXP-SSIQ-a85692-v10-round2.md` (format and
severity-calibration precedent). Read directly in source, never trusted from
spec prose: `compute_delta_e.py` lines 144–210 (`build_smooth_table`,
`two_sided_search`) and 360–420 (`run_phase_minus1_on_confirmatory_set`);
`delta_e_truncation_probe_v9.py` lines 147–211 (`run_truncation_probe_v9`);
`delta_e_truncation_sweep_v10.py` lines 164–219
(`value_histogram_and_conjugate_pairs`); `trapping_diagnostic_v5.py`
(`build_graph_for_prime` 133, `load_archived_prime_data` 102).

Directly recomputed against the committed tree (read-only, non-durable):
the full 194-entry `per_vertex_records` of `RUN-SSIQ-a85692-h` — full value
histogram, `delta_E >= 5` population, below-budget counts at 1.10/1.20/1.30/
1.40/1.45/1.70 with their `delta_E >= 5` sub-histograms, global min/max, min
over `delta_E >= 5`, the eight and nine smallest records by coordinate, and
the `resolved`/`timed_out` census; `RUN-SSIQ-a85692-b`'s `raw-result.json`
`phase_minus1_real_search` record for p=2437; and this machine's core count
and current load averages.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
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
    SESSION-independent only, NEVER model-independent. Shares a model family
    with the Coordinator who drafted v11 and wrote COORD-VERIFY-PREFREEZE-v11,
    with round 1's own reviewer, with the Executor, and with every prior
    reviewer in this lineage -- including RT-BATCH-013, whose own falsifiable
    prediction this amendment exists to test, so the prediction and its
    adversarial review are not drawn from independent populations. The
    agreement between this review's recomputation and the Coordinator's is
    therefore agreement between two sessions of one model against one
    artifact, not two independent measurements. Does not upgrade the
    campaign's evidence tier and does not itself satisfy or advance a closure
    quorum.
```

---

## Bottom line up front

**DO-NOT-FREEZE — on one finding, with a one-number repair.**

All six round-1 findings are genuinely fixed, and I verified each against
the artifact or the real code rather than against the corrected prose:

- **PF-11 fix holds.** Every figure in the pre-registered prediction curve
  reproduces exactly on my independent recomputation — all seven histogram
  buckets, the 194 sum, the 80-vertex `delta_E >= 5` population, all six
  below-budget counts, all sub-histograms, both extrema, and the
  1.3924050331115723 s `delta_E >= 5` minimum (§1). The inclusion rule
  R-1…R-4 is well-defined and reproducible. On the 80/78 and 36/30
  discrepancy: **80 and 36 are correct** under the stated rule, the round-1
  review's own tables agree, and its prose figures are the errors. The
  draft's handling — state the rule, recompute under it, refuse to edit an
  immutable review — is correct and is the right precedent.
- **PF-14 fix holds.** The defer gate is a genuine hard precondition, not
  bypassable in any branch I can construct, and `F_cal` is well-defined
  because G-0 fires first and makes the "non-timed-out only" qualifier
  vacuous (§2). The "ABSENT not zero" requirement is airtight — but only
  because of the `containing ONLY:` closed list, not because of the ABSENT
  sentence itself, which under-enumerates.
- **PF-12 fix holds.** All three line citations are correct
  (`compute_delta_e.py:185-192`, `:208`, `delta_e_truncation_probe_v9.py:183`
  — note 183 is the *corrected* citation; round 1 cited 186, which is
  `n_resolved += 1`). `max(2*t_source, t_total) <= b` is the right restated
  premise up to one-heap-pop overshoot, which errs in the permissive
  direction and so cannot break the upper-bound labelling. M-2's `new <
  archived` signature is right (§3).
- **PF-13/PF-15/PF-16 fixes hold.** Both inherited premises (i) completed-
  table RNG-independence and (ii) the archived reference being itself
  untruncated are re-derived here from source and both **confirm** (§3.3):
  RUN-b's p=2437 record is 194/194 with 284.88 s of a 300 s pool, so the
  smallest `per_vertex_cap = min(remaining, t_prime)` was ~16.5 s against a
  1.6985 s maximum natural time.
- **CAL-1/CAL-2 are implementable and the budget arithmetic is exact.** Every
  term reproduces: 485.0, 120.0, 16.0, 623.0, 621.0 → ~647, 1.61x, 1.55x,
  0.180 CPU-h (§4, §5). The eight named coordinate vertices **are** exactly
  the eight smallest archived times, and the ninth is 1.3176441192626953 s.

**The blocking finding is new and is in the fix itself:**

**PF-17 [BLOCKING] — the "forced, not preferred" choice of `b = 1.4` is a
false necessity, and the draft pays 9x its own headline power for it.** The
frozen text asserts: *"ONLY [1.1, 1.4] PRESERVES A GUARANTEED-TRUNCATED ARM
… That constraint decides the choice; it is not a preference."* The
constraint does no such thing. It excludes **1.2 as the lower point** — it
says nothing whatsoever about 1.4 versus 1.45 as the *upper* point.
**`[1.1, 1.45]` preserves the guaranteed-truncated arm in full and is never
considered anywhere in the 1184 lines.** Its cost is `194 * 2.55 = 494.7 s`
against 485.0 s — **+9.7 s, 2%, inside a 353 s margin**. Its benefit, on the
draft's own recomputed curve which I independently confirm: the
naturally-completed `delta_E >= 5` subset goes from **4 to 36**, and the
`delta_E = 5` class — which has **zero** members below 1.4 s and **20** below
1.45 s — appears at all. The draft's stated reason for declining 1.45
("because pairing it with 1.2 s would forfeit the guaranteed-truncated arm")
is a non sequitur: nothing requires 1.45 to be paired with 1.2. The pairing
is an artifact of round 1 having offered exactly two example lists, and the
revision converted that two-element menu into a claimed logical necessity.

This is the failure mode this round exists to catch: a round-2 draft that
fixes round 1's findings while introducing a new one. It matters more, not
less, because §6 shows the mixed-regime equality prediction is *a priori
determinate* — which leaves `n_naturally_completed(b)` and the
naturally-completed value histogram as the run's only genuinely empirical
content, i.e. exactly the quantity 1.45 improves 9x.

Seven further findings (PF-18…PF-24) are **ADVISORY**, including two that the
revision itself introduced: P-3 reproduces the very false-dichotomy defect
PF-12 just fixed (§7.2), and M-3 classifies mismatches by a per-vertex
`load_confounded` flag that is defined nowhere (§7.1).

**One live environmental datapoint the Coordinator should have before
scheduling anything.** `sysctl -n hw.ncpu` = **14**; `uptime` in this session
reports load averages **33.78 / 34.45 / 31.50**. That is **~2.4x**
oversubscription — materially worse than the "~1.4x-1.7x" the frozen text
records as this machine's condition. At 2.4x inflation, `F_cal` would land
near 2.8 s and the gate would fire **G-1 DEFER**. That is the gate working
exactly as designed and is not a defect; but freezing today most likely buys
a ~140 s calibration and a deferral, and the frozen text should not state the
oversubscription factor as a fixed property of the machine (§7.6).

---

## §1 — PF-11's fix: the prediction curve, recomputed independently
## [task item 1]

I recomputed everything directly from
`runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`, in a fresh session,
without reading the draft's figures into the computation. `per_vertex_records`
has 194 entries; `per_vertex_budget_seconds: 15.0`; `resolved == true` on
194/194; `timed_out == true` on **0**. So every `wall_seconds` is a genuine
unbudgeted natural completion, exactly as the draft states, and R-2's
resolved filter is indeed vacuous here.

| quantity | draft's frozen figure | my independent recomputation | agrees |
|---|---|---|---|
| full histogram | `{2:34, 3:70, 4:10, 5:42, 6:10, 7:16, 8:12}` | `{2:34, 3:70, 4:10, 5:42, 6:10, 7:16, 8:12}` | yes |
| sums to | 194 | 194 | yes |
| total `delta_E >= 5` | 80 | **80** | yes |
| b=1.10 | 0 total, 0 `>=5` | 0, 0 | yes |
| b=1.20 | 2 total, 0 `>=5`, both `delta_E=2` | 2, 0, both `delta_E=2` | yes |
| b=1.30 | 7 total, 0 `>=5` | 7, 0 | yes |
| b=1.40 | 45 total, 4 `>=5`, `{6:1, 7:1, 8:2}` | 45, 4, `{6:1, 7:1, 8:2}` | yes |
| b=1.45 | 115 total, **36** `>=5`, `{5:20, 6:4, 7:6, 8:6}` | 115, **36**, `{5:20, 6:4, 7:6, 8:6}` | yes |
| b=1.70 | 194 total, 80 `>=5` | 194, 80 | yes |
| min over all | 1.149932861328125 s, `[749, 1684]`, `delta_E=2` | identical | yes |
| min over `>=5` | 1.3924050331115723 s, `delta_E=8` | identical | yes |
| max over all | 1.6985499858856201 s | identical | yes |

**Every figure reproduces exactly.** The `<= 41` remainder at b=1.40 also
checks (45 − 4 = 41, in `{2,3,4}`).

**Is the inclusion rule well-defined and reproducible?** Yes, on all four
clauses, and I can state precisely why each is needed:
- **R-1** fixes the population as the 194 `per_vertex_records` and excludes
  the 9 F_p-rational vertices. Unambiguous, and it correctly explains the
  203-vs-194 split in the run's own `comparison_against_archived`
  (`n_both_resolved: 203`, `non_fp_rational_only.n_both_resolved: 194` —
  both confirmed by direct read).
- **R-2** is vacuous here (194 resolved, 0 timed out — I confirm the draft's
  "zero occurrences" claim by census, not by string search). Stating it
  anyway is correct: it is the clause that makes the rule transfer to
  RUN-k, where it will *not* be vacuous.
- **R-3** (inclusive `>= 5`) and **R-4** (strict `< b`) are both stated and
  both matter in principle. R-4's own escape clause is true: no archived
  `wall_seconds` equals any quoted budget, so strict-vs-inclusive changes no
  count here.

One residual ambiguity worth naming, not blocking: the rule fixes the
threshold convention for the *archived-derived* counts but does not say
which `delta_E` value labels a vertex in the *measured* naturally-completed
histogram at run time (the new run's own value, or the archived one). They
must agree by the exactness argument, but the artifact should say which
field it histogrammed. That is a one-clause addition, listed under required
controls.

**On the 80/78 and 36/30 discrepancy.** Under R-1…R-4 the correct figures
are **80 and 36**. I obtain them independently; `COORD-VERIFY-PREFREEZE-v11.md`
obtained them independently; and round 1's own §1 tables give
`42+10+16+12 = 80` and `{5:20, 6:4, 7:6, 8:6} = 36`. Round 1's **prose**
figures ("a floor over 78 vertices", "of which 30 have `delta_E >= 5`") are
the errors, and they disagree with that same review's own tables. **The
draft's handling is correct on all three counts**: it states the rule rather
than asserting an outcome; it recomputes under the rule so any reader can
reproduce it; and it declines to edit or "reconcile" an immutable review
record, leaving the discrepancy on the record and asking the round-2 reviewer
to recompute. That is the right disposition and I would not want it changed.
The draft is also right that nothing load-bearing turns on it: PF-11's
argument runs on 1.392405 s and on the two sub-1.2 s vertices, which every
party agrees on.

## §2 — PF-14's fix: is the defer gate bypassable? [task item 2]

**Evaluated before any sweep point: yes, unambiguously.** Three independent
statements in the frozen text pin this down — `amendment_scope` step (0b)(c)
("a HARD PRECONDITION evaluated before the sweep loop begins, NOT a
narrative caveat"), `load_defer_gate_v11`'s opening ("evaluated immediately
after step (0b)'s calibration and BEFORE the sweep loop begins, and its
branches are exhaustive"), and the closing anti-relaxation clause ("evaluated
ONCE, on the frozen thresholds above, and MAY NOT be recomputed, relaxed, or
re-run after seeing any sweep result … changing a pre-registered
success/validity criterion after observing outcomes requires a versioned
protocol_amendment record"). The last is the clause that actually closes the
loophole, and it is the one most drafts omit.

**Can a run proceed and write results if calibration fails or throws?** I
could not construct a path. G-0 covers both the semantic failure ("ANY of the
eight CAL-1 calls returns `timed_out True` at a 15.0 s budget") **and** the
structural one ("or if fewer than 8 CAL-1 records were produced"), which is
the clause that catches a caught-and-skipped exception. An *uncaught*
exception in calibration terminates the run with no artifact, which is the
correct infra outcome and matches step (0)'s own PF-10 discipline. The
calibration is explicitly placed **outside** the per-sweep-point try/except
isolation, so a sweep-point handler cannot swallow a calibration failure.
Good.

**Is `F_cal` well-defined?** Yes — and note it is **not a ratio**. It is the
*minimum measured CAL-1 wall_seconds in seconds* over the eight calibration
vertices, compared against two absolute second-valued thresholds. The
"counting only vertices whose CAL-1 `timed_out` is False" qualifier looks
like it could leave `F_cal` undefined over an empty set, but it cannot: G-0
is evaluated **first** and defers if *any* of the eight timed out, so by the
time G-1 is reached all eight are non-timed-out and the qualifier is vacuous.
Branch ordering is what makes this well-defined, and the draft states the
ordering explicitly ("evaluated IN ORDER"). It is computable from exactly
what CAL-1 collects (the draft requires `measured wall_seconds, timed_out,
resolved, delta_e_upper_bound` per vertex). The separate
`measured_load_inflation_ratio` (median of eight ratios) is honestly labelled
"a DIAGNOSTIC, n = 8, never a model" and correctly plays **no** role in the
gate.

**Threshold check.** `1.15 * 1.149932861328125 = 1.32242279052734375` —
exact, to the last digit. `A` is attained by `[749, 1684]`, which is a member
of the calibration set, so `F_cal` is the measured analogue of the same
quantity. Coherent.

**Is "ABSENT not zero" unambiguous?** Yes — but the load-bearing clause is
not the one the draft points at. The sentence *"n_naturally_completed,
n_resolved and every histogram field are ABSENT (not zero, not {})"*
under-enumerates: it omits `n_attempted`, `n_timed_out`, `n_still_truncated`,
`coverage_fraction`, `n_naturally_completed_matching_archived`, and the
identity outcomes I-1/I-2/I-3. What makes the branch airtight is the
preceding closed list — *"writes truncation_sweep_comparison.json containing
**ONLY**: deferred, deferral_branch, load_confounded, the full CAL-1/CAL-2
records, hw.ncpu and start/end load averages, the pre-registered prediction
curve, and an explicit statement that NO SWEEP WAS EXECUTED"*. Because that
list is closed, every sweep field is excluded whether or not the ABSENT
sentence names it. The requirement therefore **holds**, and I flag the
under-enumeration only so a future edit does not weaken the `ONLY` to an
`including` and silently reopen the hole.

**Two gaps in the gate, both advisory** (PF-22, PF-23 below): the PROCEED-
stamped band `[1.32242…, 1.4)` admits states in which the b=1.4 arm is
predictably near-empty (at `F_cal = 1.35`, i.e. ~17% inflation, only ~2
vertices satisfy even the necessary condition), so the gate gates on a proxy
(the floor) rather than on the quantity the amendment actually cares about
(the count) — cheaply fixable, since CAL-1's own eight ratios permit a
load-adjusted predicted count; and CAL-2 has **no** gate role at all despite
the draft calling a CAL-2 timeout at 2.0 s "by itself a strong contention
signal". Neither is blocking, because P-2 plus the `load_confounded` stamp
keep the honesty guarantee intact in both cases.

**One deliberate over-conservatism, correctly chosen, worth recording as an
accepted limitation:** on G-1 the *entire* run defers, including the b=1.1
arm — even though the draft itself proves that arm is monotone-safe under
load and therefore still valid. Deferring it too is conservative rather than
wrong, and I would not require a change; but the Coordinator should know a
G-1 deferral discards a measurement that would have remained sound.

## §3 — PF-12's fix, checked against the real control flow [task item 3]

### 3.1 Line citations

All three are correct in the current tree:
- `compute_delta_e.py:185-187` is `half_budget = … time_budget_seconds / 2.0`
  and the source `build_smooth_table` call; `:188-192` is `t_mid`,
  `remaining = … max(0.0, time_budget_seconds - (t_mid - t0))`, and the
  target call. The draft's "185-192" spans exactly this.
- `compute_delta_e.py:208` is `"timed_out": bool(to_s or to_t),`. Exact.
- `delta_e_truncation_probe_v9.py:183` is `timed_out = bool(r["timed_out"])`.
  Exact — and this is a **correction** of round 1, which cited 186 (that line
  is `n_resolved += 1`). The revision fixed a citation error it was not asked
  to fix. Noted in its favour.
- The PF-14(b) correction's citations `:160` (`non_fp_rational = [...]`) and
  `:172` (`for v in non_fp_rational:`) are also exact.

### 3.2 Is `max(2*t_source, t_total) <= b` the right premise?

Substantially yes, with one qualification the draft does not make and does
not need to.

`to_s` is False iff the source heap **exhausts**, not iff `t_source <= b/2`:
the budget test sits at the *top* of the loop (`compute_delta_e.py:155-159`),
so a build whose final pop carries it past `b/2` still returns
`timed_out=False`. So `to_s == False` implies `t_source <= b/2 + (one pop)`,
i.e. the restated premise is very slightly *stricter* than the code. That
error is in the **permissive** direction for the draft's use: the archived-
derived counts are used only as **upper bounds** on `n_naturally_completed`,
and a premise slightly stricter than reality can only make the true count
larger than the source-side reasoning suggests — never larger than the
`t_total < b` necessary condition, which is what the bound actually rests on.
The upper-bound labelling therefore survives. I verified the same overshoot
mechanism is the one RT-BATCH-013 measured at +4.2%/+1.4%/+0.5%, so it is
already characterized in this lineage.

The `remaining = max(0.0, …)` behaviour is correctly described ("the TARGET
table only `remaining`"). One consequence the draft does not state and which
is harmless but worth a reader knowing: `remaining` is clamped at `0.0`, and
`0.0` is a *real* zero budget, not `None`. Since `heap = [(1, start_j)]` is
never empty on entry, a target build with `remaining == 0.0` times out on its
very first loop-top check with an empty table, hence `common == {}`,
`resolved == False`, `timed_out == True`. So a source-side overrun degrades
to a clean unresolved-and-timed-out record rather than an exception — which
is exactly the `n_unresolved_and_timed_out` population PF-16's fix newly
names. The two fixes are consistent with each other.

`timed_out == False` ⇒ "exact within the frozen `(L, X=23, B=23)` class" is
correct and is now stated correctly throughout; `two_sided_search`'s own
docstring (`compute_delta_e.py:181-183`) says "an UPPER BOUND was searched,
not the exact minimal degree". The round-1 phrase "the confirmed true
minimum" is gone; I grepped and found no survivor.

### 3.3 The two inherited premises, re-derived here rather than accepted

The draft explicitly asks the round-2 reviewer to re-check these rather than
take them from its text. Both **confirm**:

- **(i) A completed smooth table is RNG-independent.** Read directly:
  `build_smooth_table` returns `table[j] = d` over the Dijkstra closure under
  the `nd > X` cap; `rng` enters only through
  `neighbors_ell_isogenous → find_roots_with_multiplicity`, i.e. root-finding
  *order*, not the root *set*. On exhaustion the table's contents are
  determined. And `best_deg = table_s[c] * table_t[c]` minimized over
  `common` is a minimum of a multiset, so it is unique even if the
  arg-minimum is not. `delta_e_upper_bound` is therefore RNG-independent for
  a completed search. Confirmed.
- **(ii) The archived reference is itself untruncated.** Read
  `run_phase_minus1_on_confirmatory_set` (`compute_delta_e.py:368-400`):
  `per_vertex_cap = min(remaining, t_prime)` with `remaining = t_prime -
  elapsed`, `t_prime = 300`. RUN-b's `phase_minus1_real_search["2437"]` reads
  `n_attempted: 194, n_resolved: 194, wall_seconds_used: 284.88387155532837`.
  The *last* vertex therefore started at ~283.5 s with a cap of ~16.5 s —
  the **smallest** cap in the run — against a 1.6985 s archived maximum
  natural time, a ~10x margin. No vertex in RUN-b was truncated. Confirmed.
  (Incidental, not a defect: RUN-b uses a **shared** `rng_search` across
  vertices while v8–v11 use a fresh per-vertex `random.Random`. Premise (i)
  is exactly what makes that difference irrelevant to the comparison, which
  is why premise (i) needs to be stated — the draft is right to state it.)

### 3.4 The three-way mismatch branch

**M-2's signature is right.** If both sides completed within the same
`(L, X=23, B=23)` class, their values are forced equal by §3.3(i); so a
mismatch means one side did not complete. `new < archived` means the new
(completed) search found a smaller in-class minimum than the archived one
recorded — i.e. the archived value is the non-minimal one. That is the
archived-side/class-artifact branch, correctly signed.

**But M-1/M-2/M-3 are not a partition, and M-3 is not evaluable as written**
(PF-19 below): M-1 ∪ M-2 already exhausts `new ≠ archived`, and M-3 —
"any mismatch on a vertex flagged `load_confounded`" — is a *cross-cutting*
qualifier, not a third case. Worse, `load_confounded` is defined in
`load_defer_gate_v11` as a **run-level top-level boolean** set by the gate;
there is no per-vertex `load_confounded` flag anywhere in the 1184 lines. So
a required reporting classification refers to an undefined term. The fix is
one sentence and the finding is advisory, not blocking, because no
good-faith Executor could be led into a *wrong* artifact by it — only into
an ambiguous label.

## §4 — CAL-1/CAL-2: implementability, and the duplicate classification
## [task item 4]

**The draft's correction of round 1 is correct on the facts.**
`run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds)`
(`:147`) takes no vertex-subset argument, derives
`non_fp_rational = [v for v in vertices if not field.is_in_fp(v)]` at `:160`,
and iterates all of them at `:172`. Calling it as round 1 literally
prescribed would search all 194 at 15.0 s — worst case 2910 s, nearly 3x the
entire 1000 s cap. Round 1's prescription was, as written, not implementable
inside the budget, and recording that rather than silently deviating is the
right behaviour under this program's own rules.

**The substitute is genuinely implementable and genuinely uses unchanged
imports.** I checked each callable against source:
`v8probe.derive_per_vertex_seed(base_seed, vertex)` exists
(`delta_e_independent_rng_probe_v8.py:151`); `field.frobenius(v)` is a real
method; `compute_delta_e.two_sided_search(field, v, target, rng_v, q, L=…,
X=…, time_budget_seconds=15.0)` matches `:177-178` exactly; and CAL-2's
`build_smooth_table(field, v, rng_v2, q, L_PRIMES, X_LIST_BOUND, 2.0, None)`
maps positionally onto `(field, start_j, rng, q, L, X, time_budget_seconds,
t0)` at `:144-145`, with `t0=None` correctly triggering the internal
`t0 = time.time()`. All eight positional slots are right. CAL-1's specified
body is a faithful restriction of `delta_e_truncation_probe_v9.py:174-181`.

**The PF-3/PF-9 duplicate classification is legitimate, not a loophole** —
the disclosure is specific (names the function, the reason, the cost figure,
and the required `execution_report.yaml` disclosure), the duplicated code is
four lines of glue around imported callables, and no frozen file is touched.
It clears this lineage's own standard.

**However, the conclusion that a duplicate is *necessary* is wrong, and the
alternative is strictly better** (PF-18 below). `run_truncation_probe_v9`
consumes only three keys of `graph` — `field`, `q`, `vertices`. A **shallow
copy with the vertex list restricted**, `{**graph, "vertices": THE_EIGHT}`,
makes round 1's prescription literally implementable: `fp_rational` becomes
empty, `non_fp_rational` becomes the eight, and the **frozen function itself
runs, unchanged**, at `8 * 15.0 = 120 s` worst case — the same cost, with
**zero** duplicated code and zero divergence risk. That is a genuine
improvement in exactly the direction PF-3/PF-9 point, and it is cheaper to
specify than the duplicate is to audit. (CAL-2 must remain a direct
`build_smooth_table` call regardless; that part is unavoidable and fine.)

**The eight named vertices are exactly the eight smallest, verified by
coordinate and to full float precision:**

| # | coordinate | delta_E | archived wall_seconds | matches draft |
|---|---|---|---|---|
| 1 | `[749, 1684]` | 2 | 1.149932861328125 | yes |
| 2 | `[749, 753]` | 2 | 1.1633622646331787 | yes |
| 3 | `[360, 1897]` | 3 | 1.257300853729248 | yes |
| 4 | `[360, 540]` | 3 | 1.2623295783996582 | yes |
| 5 | `[817, 445]` | 2 | 1.2640187740325928 | yes |
| 6 | `[2154, 970]` | 2 | 1.2711119651794434 | yes |
| 7 | `[697, 105]` | 3 | 1.2978770732879639 | yes |
| 8 | `[2405, 1073]` | 2 | 1.314664602279663 | yes |
| **9** | `[2154, 1467]` | 2 | **1.3176441192626953** | yes |

The 9th is the claimed 1.3176441192626953 s. **The boundary is unambiguous —
there is no tie — but the draft's word "comfortably separated" is false**
(PF-24): the 8th-to-9th gap is **2.98 ms**, 0.23%, and the 10th
(`[2405, 1364]`, 1.3180382251739502) sits 0.4 ms beyond the 9th. Since the
set is fixed by explicit coordinate in frozen text, nothing depends on the
gap, so this is a wording defect rather than a design one — but a frozen
document should not assert a separation it does not have.

The selection-bias disclosure attached to the calibration set (fastest tail,
`delta_E ∈ {2,3}` only, "a TIMING instrument only") is correct and correctly
placed, and discharges BATCH-012's obligation against the instrument itself
— which round 1 did not ask for.

## §5 — Budget [task item 5]

Every term reproduces:

| term | draft | recomputed | agrees |
|---|---|---|---|
| sweep worst case | `194 * (1.1 + 1.4) = 485.0` | `194 * 2.5 = 485.0` | yes |
| CAL-1 | `8 * 15.0 = 120.0` | 120.0 | yes |
| CAL-2 | `8 * 2.0 = 16.0` | 16.0 | yes |
| graph build | ~2 | ~2 | yes |
| subtotal | 623.0 | `485+120+16+2 = 623.0` | yes |
| search terms | 621.0 | `485+120+16 = 621.0` | yes |
| +4.2% overshoot | ~647 | `621.0 * 1.042 = 647.08` | yes |
| margin | 1.61x / 1.55x | `1000/623 = 1.605`, `1000/647 = 1.546` | yes |
| CPU-hours | 0.180 vs 0.33 (55%) | `647/3600 = 0.1797`; `0.180/0.33 = 54.5%` | yes |
| b=1.4 pass | 271.6 s | `194 * 1.4 = 271.6` | yes |

The **CPU-hour conversion is sound and conservative in the right
direction**: the run is single-threaded, so wall-seconds are an upper bound
on CPU-seconds, and under contention CPU-hours consumed will be *below*
0.180. Applying the +4.2% truncation overshoot to the CAL-1/CAL-2 terms
(which are expected to complete *naturally*, not truncate) is also
conservative. The load-invariance argument for the dominant 485.0 s term is
correct: `build_smooth_table` gates on wall clock, so a truncated vertex
consumes ~`b` wall seconds regardless of contention — it simply does less
work. **No budget amendment is required, and the draft is right not to
request one.**

**Under PF-17's repair the budget still holds**, which is the point of
recommending it: `194 * (1.1 + 1.45) = 494.7`; `+120 +16 +2 = 632.7`
subtotal; search terms `630.7 * 1.042 = 657.2`; margins `1000/632.7 = 1.58x`
and `1000/657.2 = 1.52x`; `657/3600 = 0.183` CPU-hours against 0.33 (55.3%).
The b=1.45 pass worst case is `194 * 1.45 = 281.3 s`.

## §6 — PF-17 [BLOCKING, NEW]: the forced choice is not forced, and it costs
## the run its only genuinely empirical content

The frozen text, twice (`amendment_scope` and `pf11_summary`):

> ONLY [1.1, 1.4] PRESERVES A GUARANTEED-TRUNCATED ARM: 1.1 s is strictly
> below the archived minimum 1.149932861328125 s (0 of 194 archived records
> below it), whereas 1.2 s already admits 2 natural completions, so a
> [1.2, 1.45] sweep would have NO arm at which "every vertex is genuinely
> truncated" still holds … **That constraint decides the choice; it is not a
> preference.**

Every factual clause is true and I verified each. The **inference** is not.
The constraint is about the *lower* point: it excludes 1.2 and mandates
something below 1.149932861328125. It is silent on the upper point. The
draft's own honest-limitation paragraph then compounds the error:

> The larger delta_E >= 5 subset lives at b = 1.45 s (predicted upper bound
> 36), which this amendment DELIBERATELY DOES NOT take, **because pairing it
> with 1.2 s would forfeit the guaranteed-truncated arm.**

Nothing requires 1.45 to be paired with 1.2. `[1.1, 1.45]` satisfies the
constraint completely. It is never named, costed, or rejected anywhere in
1184 lines. The two-element menu was an *example list* in round 1's §7
("`[1.1, 1.4]` or `[1.2, 1.45]` are both defensible"), and round 1 explicitly
recommended "retaining a sub-floor point as the guaranteed-truncated control"
— not "choose one of these two literal lists."

**What the omission costs, on figures I recomputed myself:**

| | b = 1.40 | b = 1.45 |
|---|---|---|
| naturally-completed (upper bound) | 45 | 115 |
| of which `delta_E >= 5` | **4** | **36** |
| of which `delta_E = 5` | **0** | **20** |
| histogram of the `>=5` subset | `{6:1, 7:1, 8:2}` | `{5:20, 6:4, 7:6, 8:6}` |
| mixed-regime split | 45 / 149 | 115 / 79 |
| sweep cost | 485.0 s | 494.7 s (**+2%**) |

A **9x** loss on the `delta_E >= 5` subset, and total absence of the
`delta_E = 5` class — the *largest* single value class at `>= 5` (42 of 80) —
for **9.7 seconds** inside a 353-second margin. Both budgets give a genuinely
mixed pass (45/149 vs 115/79); "mixedness" does not favour 1.4.

**Why this is blocking rather than a preference I happen to disagree with:**

1. **A false necessity claim is being frozen.** "That constraint decides the
   choice; it is not a preference" is a statement about the logical structure
   of the design space, and it is wrong. Frozen text is what future readers
   and future amendments cite; a fabricated necessity is not a small defect
   in a document whose entire value is that it was fixed before the run.
2. **It defeats the amendment's own remaining empirical content.** The
   PF-13 re-scoping makes "mixed-regime equality" the headline contribution
   — but that prediction is **a priori determinate** (PF-21 below): each
   vertex in `run_truncation_probe_v9`'s loop gets a fresh
   `random.Random(derive_per_vertex_seed(base_seed, v))`, its own
   `two_sided_search` call, and shares nothing across iterations but the
   immutable `field`/`q`/`vertices`; combined with §3.3(i)'s completed-table
   determinism, a naturally-completed vertex's value **cannot** depend on
   what happened to other vertices in the same pass. So the equality
   cross-check is an *instrument-integrity control* whose only informative
   outcome is failure. That leaves `n_naturally_completed(b)` and the
   naturally-completed value histogram as the run's genuine empirical
   output — exactly what 1.45 improves 9x.
3. **The draft itself concedes the cost** ("a very small effective sample
   for any statement about the delta_E >= 5 class specifically") and then
   binds a `strength_note` clause around it. Disclosing a self-inflicted and
   avoidable limitation is better than hiding it, but disclosure is not a
   substitute for not inflicting it at 2% cost.
4. **It repeats round 1's own defect shape at reduced amplitude.** PF-11 was
   "the chosen budget cannot observe the named phenomenon." PF-17 is "the
   chosen budget observes it at 1/9 the resolution available for +2% cost,
   on a stated reason that does not hold."

**Two acceptable repairs; either clears this finding.**

- **(A), preferred — adopt `SWEEP_BUDGETS = [1.1, 1.45]`.** Requires exactly
  four edits, all of which I have already computed so round 3 is arithmetic
  only: (i) the budget list; (ii) `load_defer_gate_v11` G-1's threshold,
  which is defined as "the largest sweep budget" and must become
  `F_cal >= 1.45`; (iii) the `pre_registered_prediction_curve_v11` entry for
  the upper arm — `n_naturally_completed <= 115`, `delta_E >= 5 <= 36`,
  predicted `>=5` histogram `{5:20, 6:4, 7:6, 8:6}`, remainder `<= 79` in
  `{2,3,4}` (specifically `{2:28, 3:43, 4:8}`), predicted mixed-regime split
  ~115 natural against ~79 truncated; (iv) the budget block — 494.7 / 632.7 /
  ~657 / 1.58x / 1.52x / 0.183 CPU-h / 281.3 s for the upper pass.
- **(B), minimal — keep 1.4, withdraw the necessity claim.** Delete "That
  constraint decides the choice; it is not a preference," delete the "because
  pairing it with 1.2 s" clause, explicitly name `[1.1, 1.45]` as the
  considered-and-rejected alternative, and give the **actual** reason for
  preferring 1.4. I could not construct such a reason and the draft offers
  none; if the Coordinator can, stating it is a full repair.

I record explicitly that repair (B) is sufficient. I am not requiring the
Coordinator to adopt my preferred design — only to stop asserting that the
design was forced when it was chosen.

## §7 — Fresh pass: what else the revision introduced

### 7.1 PF-19 [ADVISORY] — M-3 classifies on a flag that does not exist
Covered in §3.4. M-3 requires labelling "any mismatch on a vertex flagged
`load_confounded`", but `load_confounded` is defined only as a run-level
top-level boolean. Either define a per-vertex flag or restate M-3 as a
run-level qualifier co-applied with M-1/M-2, and state that M-1/M-2 are the
partition.

### 7.2 PF-20 [ADVISORY] — P-3 reproduces the exact false dichotomy PF-12
### just finished fixing
P-3 reads: a measured `n_naturally_completed` **above** the upper bound
"would falsify one of this amendment's stated premises (either the archived
timings, or the b/2 cap reading of `two_sided_search`)". That is a two-way
dichotomy that omits the a priori most likely third cause: **RUN-SSIQ-a85692-h
was itself measured under unrecorded load.** The whole premise of PF-14 is
that this machine carries heavy, variable contention and that RUN-h recorded
no load figures — so RUN-h's archived times may already be inflated, and a
RUN-k executed under *lighter* contention would legitimately exceed the
archived-derived bound with every premise intact. The draft's own
CROSS-HARDWARE caveat says as much ("it could fail only if the execution
machine were FASTER"). As written, P-3 pre-commits the run to "surface
loudly … never reconciled" a premise falsification for what is most likely a
scheduling difference. Add the third branch. This is the same defect shape
the revision just correctly repaired for mismatch classification, reappearing
one section later in the reading rules.

### 7.3 PF-21 [ADVISORY] — P-1/P-2 leave an undefined middle band
P-1 covers "at or slightly below its upper bound"; P-2 covers "FAR below …
and specifically a measured 0". Nothing covers, say, 20 of 45 — which is a
plausible outcome and the one where post-hoc discretion is most tempting.
A pre-committed reading rule with an undefined middle does not do the job a
pre-committed reading rule exists to do. Fix: pre-register a numeric split
(e.g. `>= 0.5 x` upper bound reads as P-1; `< 0.5 x` reads as P-2), chosen
now, before any measurement.

Otherwise, **do P-1..P-4 prevent a null being read as a finding? Largely
yes.** P-2 assigns a measured 0 to the environment "in the first instance"
and names it "a fatigue report about the instrument, not a statement about
the object", which is the right language. P-4 is the strongest clause in the
document: *no* outcome licenses "delta_E >= 5 convergence does not begin at
the floor", with both reasons given (unpowered, and confounded with load by
construction). `OBJECTIVE_BOUNDARY` restates it. Together with the G-0/G-1
absent-fields discipline, the silent-null path PF-14 identified is closed.

### 7.4 PF-22 [ADVISORY] — CAL-2 is named a strong contention signal and then
### given no gate role
The draft says a CAL-2 source-side timeout at 2.0 s against archived totals
of at most 1.32 s "is by itself a strong contention signal", then defines
G-0/G-1 exclusively over CAL-1. A scenario passes cleanly: seven vertices
fine, one CAL-2 timeout at 2.0 s, `F_cal` = 1.2, run proceeds unstamped. A
named strong signal with no consequence is not an instrument. Either give
CAL-2 a G-0 clause or state explicitly that CAL-2 is diagnostic-only and
deliberately non-gating.

Relatedly, `pf12_summary`'s "so the missing quantity is supplied by
measurement rather than assumed" is the loosest sentence in the revision.
CAL-2 supplies `t_source` for **8 extremity-selected vertices** with
`delta_E ∈ {2,3}`, at a 2.0 s cap, on a **fresh RNG** (so, as the draft
itself correctly discloses, an independent measurement and not a
decomposition of CAL-1). It supplies nothing about the 194 sweep vertices,
so the prediction curve remains an upper bound with no sufficiency check —
which is what the main text correctly says. Align the summary with the main
text.

### 7.5 PF-23 [ADVISORY] — the gate gates on a proxy, not on the quantity
Covered in §2. `[1.32242…, 1.4)` admits states where the b=1.4 arm is
predictably near-empty. CAL-1 already measures eight
`measured/archived` ratios; a load-adjusted predicted count
(apply the median ratio to the archived times and recount below `b`) costs
zero extra compute and would let the gate defer on the quantity that
matters. Advisory because G-2's `load_confounded: true` stamp plus P-2 keep
the artifact honest in that band.

### 7.6 PF-24 [ADVISORY] — two overstated factual assertions in frozen text
(a) "the ninth smallest is 1.3176441192626953 s, **comfortably separated**"
— the gap is 2.98 ms (0.23%); §4. The boundary is unambiguous; the adjective
is wrong. (b) The machine's oversubscription is stated as a settled property
("~1.4x-1.7x", "14 cores against 1-minute load averages measured at
19.45-24.15"). I measure **33.78 / 34.45 / 31.50** on 14 cores right now —
~2.4x, well outside the frozen range, and the 5- and 15-minute figures show
it is not a spike. Frozen text should record those observations as
timestamped measurements, not as a standing characterization, precisely
because the gate exists to re-measure it at run time. **Operationally: at
~2.4x, `F_cal` would land near 2.8 s and G-1 would fire — freezing today most
likely buys ~140 s of calibration and a DEFER.** That is the gate working as
designed, not a defect; but it is worth scheduling around, and it is a
reason not to treat a G-1 deferral, if it comes, as anything but an infra
outcome.

### 7.7 What I checked and found clean
- The seven PF-16 counts each name their population; the three identities
  I-1/I-2/I-3 are each correct given those populations and are required to be
  *asserted and reported*, not assumed. `n_unresolved_and_not_timed_out` is
  a genuinely new and genuinely interesting residual, correctly flagged as
  never-observed.
- The `resolved_non_fp_set` plumbing note is now stated explicitly, with the
  exact reconstruction expression, and separately for the naturally-completed
  subset — the advisory round 1 raised without a PF number.
- All four standing obligations (BATCH-010/011/012/013) are carried by name,
  with BATCH-012's extremity check extended to both the naturally-completed
  subset and the calibration set. The BATCH-011 self-admission ("discharging
  this obligation at drafting time would have caught both PF-11 and PF-12")
  is unusually candid and is the right precedent.
- The PF-13 prior-evidence disclosure is verbatim-accurate: I re-read
  `comparison_against_archived` and confirm `n_both_resolved: 203`,
  `n_value_matches: 203`, `n_value_differs: 0`, `value_differs_triples: []`,
  `non_fp_rational_only: {194, 194, 0}` at `per_vertex_budget_seconds: 15.0`
  with zero `timed_out`.
- The withdrawal of the "robust to modest cross-run timing variation"
  assurance is complete and is explicitly not replaced by a weaker one.
- `value_histogram_and_conjugate_pairs` remains pure with no module state and
  an explicit `n_resolved == 0` case; calling it twice per sweep point with
  different `resolved_non_fp_set` arguments is safe.
- Scope discipline: `OBJECTIVE_BOUNDARY` is *stronger* than v10's, correctly
  excludes the H-SSIQ-36e970 real-arm prediction, any PERSISTS/WEAKENS label,
  RT-BATCH-011's original question (citing DEC-20260806-520ca4 D-3), and adds
  an explicit non-establishment clause for the `delta_E >= 5` question. No
  affected/safe scheme list. **No scope inflation found.**

## Objections

- **OBJ-1 [PF-17, BLOCKING]**: the frozen text asserts that the
  guaranteed-truncated-arm constraint *decides* `[1.1, 1.4]` over
  `[1.2, 1.45]` and that the choice "is not a preference". The constraint
  decides only the *lower* point. `[1.1, 1.45]` satisfies it completely, is
  never named or costed anywhere in 1184 lines, costs `194 * 2.55 = 494.7 s`
  against 485.0 s (**+9.7 s, 2%**, inside a 353 s margin), and takes the
  naturally-completed `delta_E >= 5` subset from **4 to 36** while making the
  `delta_E = 5` class (0 vertices below 1.4 s, 20 below 1.45 s) observable at
  all. The stated reason for declining 1.45 — "because pairing it with 1.2 s
  would forfeit the guaranteed-truncated arm" — is a non sequitur.
- **OBJ-2 [PF-18, advisory]**: the draft concludes that CAL-1 *must* be an
  authorized duplicate of `run_truncation_probe_v9`'s inner loop. It need not
  be. That function consumes only `graph["field"]`, `graph["q"]` and
  `graph["vertices"]`, so `{**graph, "vertices": THE_EIGHT}` makes round 1's
  prescription literally implementable at the same 120 s worst case, running
  the **frozen function unchanged** with zero duplicated code.
- **OBJ-3 [PF-19, advisory]**: M-3 classifies mismatches "on a vertex flagged
  `load_confounded`", but `load_confounded` is defined only as a run-level
  top-level boolean; no per-vertex flag exists. M-1/M-2/M-3 are also not a
  partition (M-1 ∪ M-2 already exhausts `new != archived`).
- **OBJ-4 [PF-20, advisory]**: reading rule P-3 offers a two-way explanation
  for an over-bound measurement and omits the a priori most likely third —
  that RUN-SSIQ-a85692-h itself ran under unrecorded contention, so RUN-k on
  a less-loaded machine legitimately exceeds the bound. This is the same
  false-dichotomy shape PF-12 just repaired for mismatch classification.
- **OBJ-5 [PF-21, advisory]**: P-1 ("at or slightly below") and P-2 ("FAR
  below") leave an undefined middle band, restoring exactly the post-hoc
  discretion a pre-committed reading rule exists to remove.
- **OBJ-6 [PF-22, advisory]**: CAL-2 is called "by itself a strong contention
  signal" and then given no role in G-0..G-3 and no completeness requirement
  on the PROCEED branches; and `pf12_summary` overstates it as supplying
  PF-12's missing quantity, when it supplies `t_source` for 8
  extremity-selected `delta_E in {2,3}` vertices under a fresh RNG and
  nothing about the 194 sweep vertices.
- **OBJ-7 [PF-23, advisory]**: the gate's PROCEED-stamped band
  `[1.32242279052734375, 1.4)` admits states in which the b=1.4 arm is
  predictably near-empty; the gate uses the measured floor as a proxy for the
  measured count, when CAL-1's own eight ratios permit gating on a
  load-adjusted predicted count at zero extra compute.
- **OBJ-8 [PF-24, advisory]**: two overstated assertions in frozen text —
  the 8th/9th calibration boundary is "comfortably separated" when the gap is
  2.98 ms (0.23%), and the machine's oversubscription is stated as a standing
  ~1.4x-1.7x property when I measure ~2.4x (33.78/34.45/31.50 on 14 cores)
  this session.
- **Not an objection, recorded for completeness [PF-25, observation]**: the
  mixed-regime equality prediction is *a priori determinate* from per-vertex
  isolation in `run_truncation_probe_v9`'s loop plus completed-table
  determinism; it is an instrument-integrity control whose only informative
  outcome is failure, not a measurement that can confirm anything. The draft's
  pre-committed restriction and `strength_note` clause already prevent
  mis-citation, so this is a framing correction, not a defect — but
  "the genuinely new thing this amendment can measure" overstates it.

## Required controls

- **[PF-17, BLOCKING]**: either **(A)** adopt `SWEEP_BUDGETS = [1.1, 1.45]`,
  updating in the same pass G-1's threshold to `F_cal >= 1.45` (it is defined
  as "the largest sweep budget"), the prediction curve's upper arm to
  `<= 115` total / `<= 36` with `delta_E >= 5` / predicted `>=5` histogram
  `{5:20, 6:4, 7:6, 8:6}` / remainder `<= 79` in `{2,3,4}` (`{2:28, 3:43,
  4:8}`) / split ~115 natural against ~79 truncated, and the budget block to
  494.7 / 632.7 / ~657 s / 1.58x / 1.52x / 0.183 CPU-h / 281.3 s upper pass;
  **or (B)** keep 1.4 and delete both necessity claims, naming `[1.1, 1.45]`
  as considered-and-rejected with the actual reason stated. Either clears the
  finding. Zero new compute for either.
- **[PF-18, advisory]**: specify CAL-1 as
  `run_truncation_probe_v9({**graph, "vertices": THE_EIGHT}, BASE_SEED, 15.0)`
  — the frozen function, unchanged, on a vertex-restricted shallow copy —
  and drop the authorized-duplicate classification for CAL-1 entirely. If the
  Coordinator prefers to keep the duplicate, then require the Executor to
  assert in `execution_report.yaml` that CAL-1's call arguments and record
  shape match `delta_e_truncation_probe_v9.py:174-196` line by line, and to
  report any divergence.
- **[PF-19, advisory]**: state that M-1/M-2 partition `new != archived` and
  that M-3 is a run-level qualifier applied *in addition*; or define a
  per-vertex `load_confounded` flag and say how it is set.
- **[PF-20, advisory]**: add a third branch to P-3 — RUN-h's own load was
  never recorded, so an over-bound measurement is first attributable to RUN-k
  executing under lighter contention than RUN-h did, and only then to premise
  falsification.
- **[PF-21, advisory]**: pre-register a numeric boundary between P-1 and P-2
  now, before any measurement.
- **[PF-22, advisory]**: either give CAL-2 a G-0 clause (a 2.0 s source-side
  timeout defers) or state explicitly that CAL-2 is diagnostic-only and
  deliberately non-gating; and align `pf12_summary` with the main text's own
  (correct) statement that the archive supports the necessary condition only.
- **[PF-23, advisory]**: gate on a load-adjusted predicted count derived from
  CAL-1's eight measured ratios, in addition to the floor.
- **[PF-24, advisory]**: replace "comfortably separated" with the actual
  2.98 ms figure and the accurate statement (no tie, so no tie-break rule is
  needed); and timestamp the load observations rather than stating an
  oversubscription range as a property of the machine.
- **[PF-25, advisory]**: state that the mixed-regime equality is derivable a
  priori from per-vertex isolation plus completed-table determinism, so the
  cross-check is an instrument-integrity control whose informative outcome is
  a failure; a `k/k` match confirms nothing new even at `k = 45`.
- **[minor, no PF number]**: state which `delta_E` field labels the *measured*
  naturally-completed histogram (the new run's value or the archived one).
- **PF-18 through PF-25 do not block freeze individually or collectively.
  PF-17 does.**

## Counterexample or mutation

**The cheapest discriminating check against PF-17 costs nothing and is
already run.** The archived per-value time table shows `min(wall_seconds |
delta_E = 5) = 1.406 s` and `min(wall_seconds | delta_E >= 5) = 1.392405 s`.
At `b = 1.4` the naturally-completed `>= 5` subset is `{6:1, 7:1, 8:2}` — 4
vertices, no `delta_E = 5` at all, a sliver of the value classes it purports
to sample. At `b = 1.45` it is `{5:20, 6:4, 7:6, 8:6}` — 36 vertices spanning
every class. That table *is* the counterexample to "the constraint decides
the choice"; it can be reproduced in ten lines of Python against a committed
artifact, and it is the same computation that produced PF-11.

**The cheapest discriminating control on the mixed-regime claim (PF-25)**, if
the Coordinator wants the cross-check to be a real control rather than a
foregone confirmation: run the b=1.4 (or 1.45) pass **twice** with the same
`BASE_SEED` and confirm both passes agree vertex-by-vertex, or run the eight
calibration vertices *alone* (via the PF-18 shallow-copy graph) at the sweep
budget and confirm their naturally-completed values match the same vertices'
values inside the full 194-vertex pass. That is the null-object control for
"does the composition of the pass affect a per-vertex result", it costs ~10 s,
and it tests the proposition directly rather than inferring it from a
`k/k` match that determinism already guarantees.

**The cheapest environmental control** is the one already specified and it is
good: CAL-1 at the 15.0 s reference budget on the eight coordinate-named
vertices, compared against their archived times. Its expected reading today,
at 33.78/34.45/31.50 on 14 cores, is a G-1 deferral.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
unchanged from BATCH-013 and from round 1: toy-scale, single-prime
search-procedure diagnostic work, `H-SSIQ-36e970.asymptotic_claim: null`,
`heuristic_assumptions` empty, correctly inherited, no `dominated_by` field
in play and no cryptanalytic cost claim anywhere. The operative baseline
remains **the archived evidence this amendment must beat to be worth
running**, and the revision now discloses it correctly: `RUN-SSIQ-a85692-h`
already establishes the equality at n=194 with zero exceptions and zero
timeouts. Against that baseline the amendment's *disclosed* increment is the
mixed-regime conditioning (which §6/PF-25 shows is a priori determinate) plus
the empirical `n_naturally_completed(b)` curve — and PF-17 is precisely the
finding that the second, which is the real increment, was needlessly cut to
1/9 resolution on its most-discussed sub-question.

## Heuristic challenges

No heuristic in the `docs/target-result-profile.md` sense: no exponent-first
claim, no random-model transfer, no `o(1)`/polylog overhead, no
van Oorschot–Wiener interpolation, no reduction corollary, no affected/safe
scheme scope. The nearest analogue is the **archived-timings-transfer
assumption** — that RUN-h's per-vertex wall times predict RUN-k's on the same
machine — and the revision handles it correctly: it is labelled an upper
bound, its sufficiency gap (`t_source <= b/2`) is stated, its environmental
confound has a pre-registered gate and a recorded measurement, and its
cross-hardware assurance has been withdrawn without replacement. That is the
right treatment. The one remaining asymmetry is PF-20: the transfer
assumption's *downward* failure is fully instrumented; its *upward* failure
(RUN-h itself loaded) is mis-attributed by P-3.

## Cost model challenges

None outstanding. Every budget term reproduces exactly (§5), the CPU-hour
conversion is conservative in the correct direction, the load-invariance
argument for the dominant truncated-sweep term is right on the mechanism
(wall-clock gating means a truncated vertex costs ~`b` regardless of
contention), and the +4.2% overshoot figure is this lineage's own measured
value applied conservatively to terms that will mostly not truncate. PF-17's
repair (A) costs +9.7 s of search and +34 s of headroom consumption, leaving
1.52x margin — checked, not asserted.

## Reduction and scope challenges

None. `OBJECTIVE_BOUNDARY` is stronger than v10's and correctly refuses:
H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label, lever L4,
any claim beyond p=2437, RT-BATCH-011's original question (citing
DEC-20260806-520ca4 D-3's confound constraint), and — new in round 2 — any
establishment or refutation of "delta_E >= 5 convergence begins at the
floor", with both reasons stated. No scope inflation found. No closure or
negative result is asserted anywhere, so the closure-burden rules do not
bite.

## Proof architecture challenges

The one derivation-shaped argument in the amendment is the natural-completion
exactness chain, and it now holds end to end on my independent read:
completed table ⇒ RNG-independent contents (`build_smooth_table`, rng enters
only root-finding order) ⇒ `best_deg` a unique minimum over a multiset ⇒
value determined; plus the archived reference itself untruncated (RUN-b:
194/194, smallest `per_vertex_cap` ~16.5 s against 1.6985 s max natural).
Both premises are correctly labelled as inherited and both were re-checked
here rather than accepted. The one architectural note is PF-25: this same
chain makes the mixed-regime prediction determinate, so the cross-check
should be framed as a control, not a measurement.

## Narrowest supported statement

If this amendment were frozen exactly as drafted and executed successfully
past the gate, the narrowest statement its results would support is:

> At p=2437 only, at per-vertex budgets 1.1 s and 1.4 s under
> `BASE_SEED = 20260811` and the frozen `(L, X=23, B=23)` search class, the
> subset of the 194 non-F_p-rational vertices whose `two_sided_search`
> returned `timed_out = False` in a pass where other vertices were
> simultaneously truncated returned `delta_E` values identical to
> `RUN-SSIQ-a85692-b`'s archived map on all `k` of them, where `k` is the
> reported `n_naturally_completed` for that budget (predicted upper bound 45
> at 1.4 s, of which at most 4 carry `delta_E >= 5` and none carries
> `delta_E = 5`); and the measured `n_naturally_completed` at each budget
> stood in the reported relation to the archived-derived upper bound, under
> the recorded load averages and `load_confounded` stamp.

It would **not** support: any statement about `delta_E = 5` vertices (none is
observable at 1.4 s); any statement about whether `delta_E >= 5` convergence
begins at the floor (P-4); any statement about the `delta_E` population from
the naturally-completed histogram (speed-selected); any independent
confirmation of the equality proposition itself (already at n=194, and
determinate a priori); or anything about the other three primes or any
cryptographic scale.

## Next concrete action

Coordinator: apply PF-17 in one textual pass — repair (A), `[1.1, 1.45]`,
with the four dependent edits and all replacement figures given in §5/§6, or
repair (B), keep 1.4 and withdraw the necessity claims with an actual reason
— and fold in as many of PF-18…PF-25 as are cheap (all are text-only; PF-18
and PF-20 are the two with real downstream consequence). Zero new compute.
Given that every round-1 fix verified clean and the remaining defect is a
single design number plus wording, **no third dedicated red-team round is
required**: a Coordinator self-verification note recording the recomputed
prediction-curve line for the new upper budget, in the style of
`COORD-VERIFY-PREFREEZE-v11.md`, is proportionate. Then freeze. **Before
dispatching the Executor, re-read `uptime`**: at the 33.78/34.45/31.50 I
measure now, the run's most likely outcome is a G-1 deferral, and the
calibration is cheap enough that spending it to learn that is acceptable —
but scheduling it against a quieter machine is cheaper still.

## Overall verdict

**DO-NOT-FREEZE**, on **PF-17** alone. Every one of round 1's six findings is
genuinely and verifiably fixed against the artifact and the real code, not
merely against corrected prose; the prediction curve reproduces to the last
digit; the defer gate is a real hard precondition I could not bypass; the
PF-12 semantics are correct against the control flow; CAL-1/CAL-2 are
implementable; and the budget arithmetic is exact. The blocking finding is
one the revision itself introduced: a false necessity claim frozen into the
text, which costs the amendment's own headline quantity a factor of 9 for a
2% budget increase, on a reason that does not survive inspection. The repair
is one number, or one deleted sentence. This lineage froze v10 after two
rounds; v11 should freeze after a short third pass, and there is nothing in
the design as a whole that needs re-litigating to get there.

---

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v11-round2
  task_id: TASK-20260807-43d16f-r2
  claim_under_review: >-
    The ROUND-2 draft amendment specification_v11.yaml (EXP-SSIQ-a85692
    version 11, status draft, approved_by null, frozen_at null,
    pre_freeze_review.status ROUND_1_COMPLETE_ROUND_2_PENDING, committed at
    2256c925b6c8676b520ab6821a3a1be35c102afe, HEAD, working tree clean),
    which revises the round-1 draft in response to
    RT-PREFREEZE-EXP-SSIQ-a85692-v11.md's four BLOCKING (PF-11..PF-14) and
    two ADVISORY (PF-15, PF-16) findings: a two-point mixed-regime
    truncation sweep at SWEEP_BUDGETS = [1.1, 1.4] over p=2437, preceded by
    a mandatory 8-vertex floor calibration (CAL-1/CAL-2) and a
    pre-registered defer gate (G-0..G-3), with a pre-registered prediction
    curve and pre-committed reading rules P-1..P-4. Scoped round-2 review:
    independent recomputation of the prediction curve, gate-bypassability,
    PF-12 semantics against the real code, CAL-1/CAL-2 implementability and
    duplicate classification, budget arithmetic, and a fresh pass for
    defects the revision itself introduced.
  objections:
    - "OBJ-1 [PF-17, BLOCKING]: the frozen text asserts the guaranteed-truncated-arm constraint DECIDES [1.1, 1.4] over [1.2, 1.45] and that the choice 'is not a preference'. The constraint decides only the LOWER point. [1.1, 1.45] satisfies it completely, is never named or costed anywhere in 1184 lines, costs 194*2.55 = 494.7s against 485.0s (+9.7s, 2%, inside a 353s margin), and takes the naturally-completed delta_E>=5 subset from 4 to 36 while making the delta_E=5 class (0 vertices below 1.4s, 20 below 1.45s) observable at all. The stated reason for declining 1.45 -- 'because pairing it with 1.2 s would forfeit the guaranteed-truncated arm' -- is a non sequitur; nothing requires 1.45 to be paired with 1.2."
    - "OBJ-2 [PF-18, advisory]: the draft concludes CAL-1 MUST be an authorized duplicate of run_truncation_probe_v9's inner loop. run_truncation_probe_v9 consumes only graph['field'], graph['q'], graph['vertices'], so {**graph, 'vertices': THE_EIGHT} makes round 1's prescription literally implementable at the same 120s worst case, running the frozen function unchanged with zero duplicated code."
    - "OBJ-3 [PF-19, advisory]: M-3 classifies mismatches 'on a vertex flagged load_confounded', but load_confounded is defined only as a run-level top-level boolean; no per-vertex flag exists anywhere. M-1/M-2/M-3 are also not a partition (M-1 union M-2 already exhausts new != archived)."
    - "OBJ-4 [PF-20, advisory]: reading rule P-3 gives a two-way explanation for an over-bound measurement and omits the a priori most likely third -- that RUN-SSIQ-a85692-h itself ran under unrecorded contention (PF-14's own premise is that this machine's load is heavy and was never recorded), so RUN-k on a less-loaded machine legitimately exceeds the bound. This is the same false-dichotomy shape PF-12 just repaired for mismatch classification, reappearing one section later."
    - "OBJ-5 [PF-21, advisory]: P-1 ('at or slightly below') and P-2 ('FAR below') leave an undefined middle band (e.g. 20 of 45), restoring exactly the post-hoc discretion a pre-committed reading rule exists to remove."
    - "OBJ-6 [PF-22, advisory]: CAL-2 is called 'by itself a strong contention signal' and then given no role in G-0..G-3 and no completeness requirement on PROCEED branches; and pf12_summary's 'the missing quantity is supplied by measurement rather than assumed' overstates a measurement of t_source on 8 extremity-selected delta_E in {2,3} vertices under a fresh RNG that says nothing about the 194 sweep vertices."
    - "OBJ-7 [PF-23, advisory]: the gate's PROCEED-stamped band [1.32242279052734375, 1.4) admits states in which the b=1.4 arm is predictably near-empty (at F_cal=1.35, ~2 vertices satisfy even the necessary condition); the gate uses the measured floor as a proxy for the measured count when CAL-1's own eight ratios permit gating on a load-adjusted predicted count at zero extra compute."
    - "OBJ-8 [PF-24, advisory]: two overstated frozen assertions -- the 8th/9th calibration boundary is 'comfortably separated' when the gap is 2.98ms (0.23%, 1.314664602279663 vs 1.3176441192626953), and the machine's oversubscription is stated as a standing ~1.4x-1.7x property when this session measures ~2.4x (33.78/34.45/31.50 on 14 cores)."
    - "OBJ-9 [PF-25, observation, not a defect]: the mixed-regime equality prediction is a priori determinate -- run_truncation_probe_v9's loop gives each vertex a fresh random.Random and its own two_sided_search call and shares nothing across iterations but immutable field/q/vertices, which with completed-table determinism makes a naturally-completed vertex's value independent of the pass it sits in. The cross-check is an instrument-integrity control whose only informative outcome is failure; 'the genuinely new thing this amendment can measure' overstates it. The draft's own pre-committed restriction and strength_note clause already prevent mis-citation."
  required_controls:
    - "[PF-17, BLOCKING] Either (A) adopt SWEEP_BUDGETS = [1.1, 1.45], updating in the same pass: G-1's threshold to F_cal >= 1.45 (it is defined as 'the largest sweep budget'); the prediction curve's upper arm to <=115 total, <=36 with delta_E>=5, predicted >=5 histogram {5:20, 6:4, 7:6, 8:6}, remainder <=79 in {2,3,4} (= {2:28, 3:43, 4:8}), split ~115 natural against ~79 truncated; and the budget block to 494.7 / 632.7 / ~657s / 1.58x / 1.52x / 0.183 CPU-h / 281.3s upper pass. Or (B) keep 1.4 and delete both necessity claims, naming [1.1, 1.45] as considered-and-rejected with the actual reason stated. Either clears the finding; zero new compute for either."
    - "[PF-18, advisory] Specify CAL-1 as run_truncation_probe_v9({**graph, 'vertices': THE_EIGHT}, BASE_SEED, 15.0) -- the frozen function unchanged on a vertex-restricted shallow copy -- and drop CAL-1's authorized-duplicate classification. If the duplicate is kept, require the Executor to assert in execution_report.yaml that CAL-1's call arguments and record shape match delta_e_truncation_probe_v9.py:174-196 line by line."
    - "[PF-19, advisory] State that M-1/M-2 partition new != archived and that M-3 is a run-level qualifier applied in addition; or define a per-vertex load_confounded flag and how it is set."
    - "[PF-20, advisory] Add a third branch to P-3: RUN-h's own load was never recorded, so an over-bound measurement is first attributable to RUN-k running under lighter contention, and only then to premise falsification."
    - "[PF-21, advisory] Pre-register a numeric boundary between P-1 and P-2 now, before any measurement (e.g. >= 0.5x upper bound reads as P-1)."
    - "[PF-22, advisory] Either give CAL-2 a G-0 clause (a 2.0s source-side timeout defers) or state explicitly that CAL-2 is diagnostic-only and deliberately non-gating; align pf12_summary with the main text's own correct statement that the archive supports the necessary condition only."
    - "[PF-23, advisory] Gate additionally on a load-adjusted predicted count derived from CAL-1's eight measured ratios, not on the floor alone."
    - "[PF-24, advisory] Replace 'comfortably separated' with the actual 2.98ms figure plus the accurate statement (no tie, so no tie-break rule needed); timestamp the load observations rather than stating an oversubscription range as a property of the machine."
    - "[PF-25, advisory] State that the mixed-regime equality is derivable a priori from per-vertex isolation plus completed-table determinism, so a k/k match confirms nothing new even at k=45."
    - "[minor, no PF number] State which delta_E field labels the measured naturally-completed histogram (the new run's value or the archived one)."
    - "PF-18 through PF-25 do not block freeze individually or collectively. PF-17 does."
  counterexample_or_mutation: >-
    Against PF-17, at zero compute: the archived per-value time table gives
    min(wall_seconds | delta_E = 5) = 1.406s and min(wall_seconds |
    delta_E >= 5) = 1.3924050331115723s, so at b=1.4 the naturally-completed
    delta_E>=5 subset is {6:1, 7:1, 8:2} -- 4 vertices, no delta_E=5 class at
    all -- while at b=1.45 it is {5:20, 6:4, 7:6, 8:6}, 36 vertices spanning
    every class. That table is the counterexample to 'the constraint decides
    the choice', reproducible in ten lines of Python against a committed
    artifact. Against PF-25, the cheapest real control on the mixed-regime
    proposition is to run the eight calibration vertices ALONE (via PF-18's
    shallow-copy graph) at the sweep budget and confirm their
    naturally-completed values match the same vertices' values inside the full
    194-vertex pass -- ~10s, and it tests pass-composition-independence
    directly rather than inferring it from a k/k match determinism already
    guarantees. The environmental control (CAL-1 against the eight archived
    times) is already specified and is good; its expected reading today, at
    33.78/34.45/31.50 on 14 cores, is a G-1 deferral.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense, and no
    dominated_by field is in play: toy-scale single-prime search-procedure
    diagnostic work, H-SSIQ-36e970.asymptotic_claim null, heuristic_assumptions
    empty, no cryptanalytic cost claim, no affected/safe scheme list. The
    operative baseline is the archived evidence the amendment must beat to be
    worth running, and the revision now discloses it correctly and verbatim:
    RUN-SSIQ-a85692-h already establishes the equality at n=194 with zero
    exceptions and zero timeouts (n_both_resolved 203, n_value_matches 203,
    n_value_differs 0, non_fp_rational_only 194/194/0, at
    per_vertex_budget_seconds 15.0). Against that baseline the disclosed
    increment is the mixed-regime conditioning (a priori determinate, PF-25)
    plus the empirical n_naturally_completed(b) curve -- and PF-17 is the
    finding that the second, the real increment, was cut to 1/9 resolution on
    its most-discussed sub-question for a 2% budget saving.
  heuristic_challenges:
    - "No exponent-first or heuristic-conditional claim is made anywhere; the target-result-profile challenge set does not apply. The nearest analogue is the archived-timings-transfer assumption, which the revision now handles correctly: labelled an upper bound, sufficiency gap (t_source <= b/2) stated, environmental confound gated and measured, cross-hardware assurance withdrawn without replacement. The one remaining asymmetry is PF-20: the transfer assumption's downward failure is fully instrumented, its upward failure (RUN-h itself loaded) is mis-attributed by P-3."
  cost_model_challenges:
    - "None outstanding. Every term reproduces: 194*2.5=485.0, 8*15.0=120.0, 8*2.0=16.0, +2 graph = 623.0 subtotal, 621.0 search terms, 621.0*1.042=647.08 ~ 647s, 1000/623=1.605 ~ 1.61x, 1000/647=1.546 ~ 1.55x, 647/3600=0.1797 ~ 0.180 CPU-h against 0.33 (54.5% ~ 55%), 194*1.4=271.6s upper pass. The CPU-hour conversion is conservative (single-threaded, so wall >= CPU, and more so under contention). Applying the +4.2% truncation overshoot to CAL-1/CAL-2 -- terms expected to complete naturally, not truncate -- is also conservative. The load-invariance argument for the dominant 485.0s term is right on the mechanism (wall-clock gating means a truncated vertex costs ~b regardless of contention). PF-17's repair (A) costs +9.7s search and leaves 1.52x margin -- checked, not asserted."
  reduction_and_scope_challenges:
    - "None. OBJECTIVE_BOUNDARY is stronger than v10's and correctly refuses H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label, lever L4, any claim beyond p=2437, RT-BATCH-011's original question (citing DEC-20260806-520ca4 D-3), and -- new in round 2 -- any establishment or refutation of 'delta_E>=5 convergence begins at the floor', with both reasons stated. No scope inflation found. No closure or negative result is asserted, so the closure-burden rules do not bite."
  proof_architecture_challenges:
    - "The natural-completion exactness chain holds end to end on independent read: completed table => RNG-independent contents (rng enters only find_roots_with_multiplicity ordering, not the root set) => best_deg a unique minimum over a multiset => value determined; plus the archived reference itself untruncated (RUN-b p=2437: 194/194, wall_seconds_used 284.88387155532837 of a 300s pool, so the smallest per_vertex_cap = min(remaining, t_prime) was ~16.5s against a 1.6985499858856201s maximum natural time). Both premises were re-checked here from source rather than accepted from the draft, as the draft itself requested. The one architectural note is PF-25: the same chain makes the mixed-regime prediction determinate, so the cross-check is a control, not a measurement."
  narrowest_supported_statement: >-
    If frozen as drafted and executed past the gate, the results would support
    only: at p=2437 alone, at per-vertex budgets 1.1s and 1.4s under
    BASE_SEED 20260811 and the frozen (L, X=23, B=23) search class, the subset
    of the 194 non-F_p-rational vertices whose two_sided_search returned
    timed_out False in a pass where other vertices were simultaneously
    truncated returned delta_E values identical to RUN-SSIQ-a85692-b's
    archived map on all k of them, k being the reported n_naturally_completed
    for that budget (predicted upper bound 45 at 1.4s, of which at most 4
    carry delta_E>=5 and none carries delta_E=5); and the measured
    n_naturally_completed stood in the reported relation to the
    archived-derived upper bound, under the recorded load averages and
    load_confounded stamp. It would NOT support any statement about delta_E=5
    vertices (none observable at 1.4s), about whether delta_E>=5 convergence
    begins at the floor (P-4), about the delta_E population from the
    speed-selected naturally-completed histogram, any independent confirmation
    of the equality proposition itself (already n=194, and determinate a
    priori), or anything about the other three primes or any cryptographic
    scale.
  next_concrete_action: >-
    Coordinator: apply PF-17 in one textual pass -- repair (A), adopt
    [1.1, 1.45] with the four dependent edits and all replacement figures
    given in this review's sections 5 and 6, or repair (B), keep 1.4 and
    withdraw both necessity claims with an actual reason stated -- and fold in
    as many of PF-18..PF-25 as are cheap (all text-only; PF-18 and PF-20 have
    the most downstream consequence). Zero new compute. Given that every
    round-1 fix verified clean and the remaining defect is one design number
    plus wording, no third dedicated red-team round is required: a Coordinator
    self-verification note recording the recomputed prediction-curve line for
    the new upper budget, in the style of COORD-VERIFY-PREFREEZE-v11.md, is
    proportionate. Then freeze. Before dispatching the Executor, re-read
    uptime: at 33.78/34.45/31.50 on 14 cores the run's most likely outcome is
    a G-1 deferral.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no module from this lineage's
    implementation directory executed -- this review is a specification and
    real-code trace against a draft with no implementation file yet (confirmed:
    no *v11* file under experiments/EXP-SSIQ-a85692/implementation/), not an
    execution audit. Non-durable, read-only local computations run directly
    against the committed tree at HEAD 2256c925b: (a) full independent
    recomputation over RUN-SSIQ-a85692-h's 194 per_vertex_records under the
    draft's own R-1..R-4 -- resolved/timed_out census (194/0), full value
    histogram, delta_E>=5 population, below-budget counts and >=5
    sub-histograms at 1.10/1.20/1.30/1.40/1.45/1.70, global min/max, min over
    delta_E>=5, and the ten smallest records by coordinate to full float
    precision; (b) direct read of comparison_against_archived in the same
    artifact; (c) direct read of RUN-SSIQ-a85692-b's raw-result.json
    phase_minus1_real_search record for p=2437; (d) direct source read of
    compute_delta_e.py lines 144-210 and 360-420,
    delta_e_truncation_probe_v9.py lines 147-211,
    delta_e_truncation_sweep_v10.py lines 164-219, and
    trapping_diagnostic_v5.py function definitions, with line numbers verified
    against the draft's citations; (e) sysctl -n hw.ncpu (14) and uptime
    (33.78/34.45/31.50); (f) git log/rev-parse/status to confirm the reviewed
    commit is HEAD, is this file's most recent touching commit, and the tree
    is clean. Independent arithmetic re-derivation of every budget term for
    both the drafted [1.1, 1.4] and the proposed [1.1, 1.45]. No file was
    written or edited by any of these computations other than this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task wrote only
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v11.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
