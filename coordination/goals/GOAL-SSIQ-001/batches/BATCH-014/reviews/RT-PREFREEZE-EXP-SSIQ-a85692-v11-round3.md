# RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3 — Round 3 pre-freeze Red Team
# review of the DRAFT amendment `specification_v11.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-014, task `TASK-20260807-43d16f-r3`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v11.yaml` at
`status: draft`, `approved_by: null`, `frozen_at: null`,
`pre_freeze_review.status: ROUND_2_COMPLETE_ROUND_3_PENDING`, committed at
`5d6caed4320ccdf24bf202150421ed50b16e4e24` (confirmed: that commit is this
file's most recent touching commit AND is the checked-out `HEAD`; working
tree clean, 0 modified paths; 1756 lines, up from round 2's reviewed 1184).**
This is the round-3 revision applying PF-17 (repair A) and PF-18…PF-25.

This is a focused third round. Rounds 1 and 2 are treated as settled: their
verified-clean conclusions (seed isolation, function existence and
signatures, PF-2/PF-7/PF-8/PF-9/PF-10 pre-application, scope discipline, the
untruncated-archived-reference premise, the completed-table RNG-independence
premise) are cited as still holding and are not re-derived, except where
round 3's own changes put weight on them. What is re-derived from scratch
here: the entire new upper arm of the prediction curve, the orphan-constant
sweep, the gate's ordering and well-definedness, PF-18 against the real
function body, PF-19/PF-20's exhaustiveness, and the budget. Then one fresh
adversarial pass with the draft's own `round3_scope_requested` deliberately
set aside — a draft that nominates its own review scope is nominating what
it is confident about.

**No implementation file for v11 exists** (confirmed: no `*v11*` file under
`experiments/EXP-SSIQ-a85692/implementation/`). This remains a plan audit.
This review is advisory pre-freeze input on a draft and changes nothing under
`experiments/` or `ledger/`.

Read in full: `specification_v11.yaml` (1756 lines, in full, not from diff);
`RT-PREFREEZE-EXP-SSIQ-a85692-v11.md` (round 1); its round-2 successor;
`COORD-VERIFY-PREFREEZE-v11.md`. Read directly in source, never trusted from
prose: `delta_e_truncation_probe_v9.py` in full (665 lines), with
`run_truncation_probe_v9` at 147–211 traced statement by statement;
`compute_delta_e.py` 100–210 (`build_smooth_table`, `two_sided_search`);
`delta_e_independent_rng_probe_v8.derive_per_vertex_seed` by execution.

Directly recomputed against the committed tree (read-only, non-durable): the
full 194-entry `per_vertex_records` of `RUN-SSIQ-a85692-h`; the CDF of
archived `wall_seconds` in the neighbourhood of 1.45 s; all 194
`derive_per_vertex_seed(20260811, v)` values against the archived
`seed_used` field; `RUN-SSIQ-a85692-h/environment.json`,
`manifest.yaml`, `execution_report.yaml`, `raw-result.json`; and the
`environment.json` of every run `-a` … `-j` in this lineage.

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
    SESSION-independent only, NEVER model-independent. This session shares a
    model family with the Coordinator who drafted v11 and wrote
    COORD-VERIFY-PREFREEZE-v11, with the round-1 and round-2 reviewers whose
    findings it is auditing, with the Executor, and with RT-BATCH-013, whose
    own falsifiable prediction this amendment exists to test. Four
    recomputations of the prediction curve now agree; that is agreement among
    four sessions of one model against one committed artifact, not four
    independent measurements. It does not upgrade the campaign's evidence
    tier and does not satisfy or advance a closure quorum. It is also the
    reason the two blocking findings below matter: both are premises that
    three prior sessions of the same model carried forward without checking,
    which is the characteristic failure mode of correlated review.
```

---

## Bottom line up front

**DO-NOT-FREEZE — on two findings, neither of which is in the round-3 scope
the draft nominated for itself, and both of which are cheap text repairs.**

Everything the task asked me to verify, verified clean. I want that on the
record before the objections, because it is the larger part of the result:

- **PF-17's repair is arithmetically complete and correct.** Every figure of
  the new upper arm reproduced exactly on an independent recomputation from
  the committed artifact: `115`, `36`, `20`, `{5:20, 6:4, 7:6, 8:6}`,
  `{2:28, 3:43, 4:8}` summing to `79`, the `115/79` split, the `0.725 s`
  source-side cap, and `0` at `b = 1.10 s`. So did the whole rest of the
  inclusion-rule block: `{2:34, 3:70, 4:10, 5:42, 6:10, 7:16, 8:12}` summing
  to 194, the 80-vertex `delta_E >= 5` population, the 1.20/1.30/1.40/1.70
  rows, both extrema, and `1.3924050331115723`. I confirm the Coordinator's
  reproduction rather than contradict it (§1). Notably the
  `{2:28, 3:43, 4:8}` split, which the draft flags as the one figure it did
  *not* itself recompute, is correct.
- **No orphan `1.4`-derived operative constant survives.** I swept all 76
  occurrences of the string `1.4` in the file myself. Every one is either
  `1.45`, `1.4x`/`1.4x-2.5x` (a load ratio), `+1.4%` (an overshoot figure),
  `1.40`/`1.4` in the historical comparison table or the PF-17 narrative, or
  the `1.4531…`-style float tails of archived times. The only operative
  thresholds are `1.45` (G-1), `1.32242279052734375` (G-2), `15.0` (G-0/CAL-1)
  and `2.0` (G-0b/CAL-2), and I verified independently that
  `1.15 × 1.149932861328125 = 1.32242279052734375` exactly as a rational, so
  G-2 is genuinely archived-floor-derived and correctly unmoved (§2).
- **PF-18's shallow copy is correct against the real function body.**
  `run_truncation_probe_v9` reads exactly `graph["field"]`, `graph["q"]`,
  `graph["vertices"]` (lines 156–158) and nothing else, ever. The claimed
  8-vertex consequences all hold, and I confirmed by execution that
  `derive_per_vertex_seed(20260811, v)` reproduces **all 194** of RUN-h's
  archived `seed_used` values, so CAL-1's like-for-like RNG claim is true and
  is order-independent (§3). This fix is strictly better than the duplicate
  it replaces.
- **The gate is well-defined and correctly ordered, including G-0b.** F_cal
  cannot be made undefined; the branches reduce to an unambiguous
  `defer-or-(stamp = G-2 OR G-2b)` decision; I could construct no bypass and
  no conflicting pair (§4).
- **The budget reproduces to the digit.** `194 × 2.55 = 494.7`;
  `213.4 / 281.3`; `+120.0 + 16.0 + 2.0 = 632.7`; `630.7 × 1.042 = 657.19`;
  `1000/632.7 = 1.5805`; `1000/657.2 = 1.5216`; `657/3600 = 0.1825` CPU-h =
  `55.3%` of 0.33; round 2's `485.0 → 1.55x` also reproduces (§6). RUN-h's
  own artifacts independently support the `~2 s` non-search allowance: its
  total wall was `278.496 s` against `277.832 s` of summed per-vertex search,
  i.e. `0.66 s` for graph build, verification, both comparisons and all JSON
  I/O.
- **PF-19, PF-20, PF-21, PF-22, PF-24 and PF-25 are correctly applied.**
  M-1/M-2 do partition `new != archived` over integers; Q-LOAD is keyed to a
  field that is defined and always present; P-3's branch set is better
  ordered and P-3a's factual basis is **true** — I checked RUN-h's
  `environment.json`, `manifest.yaml` and `execution_report.yaml` directly and
  there is no load average, no `getloadavg`, no `hw.ncpu`, nothing (§5).
  PF-25's derivation is sound and I re-derived it independently.

**The two blocking findings are premises nobody checked, not arithmetic:**

**PF-26 [BLOCKING] — the amendment's central instrument is a
measured-versus-archived timing comparison, and the committed evidence says
the measuring machine and the archived machine are not the same machine. The
frozen text asserts they are, by name, and never looks.** Every run in this
lineage — `-a` through `-j`, including `RUN-SSIQ-a85692-h` itself, the source
of every archived time the prediction curve, `A`, `F_cal`, G-0, G-1, G-2 and
G-2b are built on — executed on `Linux-6.18.5-fc-v18-x86_64-with-glibc2.39`,
Python `3.11.15 … [GCC 13.3.0]`, `cpus_available: 4`. Every load observation
frozen into this specification was taken with `sysctl -n hw.ncpu` on a
**14-core arm64 Darwin host** (I re-measured: `Darwin … RELEASE_ARM64_T6041`,
`hw.ncpu` 14, load `36.09 / 56.77 / 63.22` at the time of writing, `75.85 /
89.14 / 73.54` twenty minutes earlier). Different core count, different ISA,
different OS, different Python build. The specification calls its own caveat
the **"SAME-HARDWARE CONTENTION CAVEAT"** and derives an operational
prediction from those host figures ("at ~2.4x, F_cal would land near 2.8 s
and the gate would fire G-1"); it requires `hw.ncpu` as an
`environment.json` field, on a platform where that command does not exist;
and in 1756 lines it never records RUN-h's platform, never cites RUN-h's
`environment.json`, and never requires the Executor to check that RUN-k runs
where RUN-h ran. The fix is about five lines and costs no compute (§7.1).

**PF-27 [BLOCKING] — `115` is not an upper bound, and the stated reason it
survives as one is directionally backwards. The error is inherited from
round 2, and PF-17's own move from 1.4 to 1.45 is what made it
quantitatively load-bearing.** The draft says the one-heap-pop qualification
is "an error in the PERMISSIVE direction for the only use made of it here (an
upper bound on `n_naturally_completed`)". A premise *stricter* than the code
means the code admits **more** natural completions than the premise, which
attacks an upper bound rather than protecting it. Round 2 rescued this by
saying the bound "actually rests on" the necessary condition `t_total < b` —
but `t_total < b` is not necessary either, by the *identical* mechanism
applied to the target half: `remaining = b − t_source` is checked at the top
of the target loop too, so a target build whose final pop straddles the
deadline still returns `to_t = False` with `t_total = b + (one pop)`. The
archived distribution is extremely dense exactly there: **18** records lie in
`[1.45, 1.46)`, **30** in `[1.45, 1.47)`, **71** in `[1.45, 1.50)`. Using the
overshoot RT-BATCH-013 actually measured on this lineage, the honest count
runs `124` at 5 ms of slack, `135` at 11 ms, `157` at 25 ms — against a
frozen "upper bound" of `115` and a P-3 trigger of "above 115" that
pre-commits the run to reading a contention or hardware or
premise-falsification story for an outcome the code produces on its own. At
`b = 1.4` the same slack moved the count `45 → 56 → 67`; the move to 1.45
landed the reference point in the mode of the distribution, which is where
the defect bites (§7.2).

Three advisories follow, PF-28…PF-30. None blocks.

On the two questions the task asked me to weigh rather than wave through:
**PF-25's reclassification is correct and I would not soften it — but it does
reduce the amendment to roughly one integer of empirical content, and I say
so plainly in §8.** **PF-23's stamping form is acceptable in kind, but its
threshold of 10 is not aligned with the draft's own P-2 artifact boundary of
58, which leaves a wide band where the specification's reading rule calls an
outcome an environment artifact while the artifact's own `load_confounded`
reads `false` (PF-29).**

---

## §1 — PF-17's repair, recomputed from the artifact [task item 1]

Recomputed directly from
`runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json` under the draft's own
R-1…R-4, with no reference to the draft's prose except to compare afterwards.
Census first: 194 records, `resolved` true on all 194, `timed_out` false on
all 194, `per_vertex_budget_seconds` 15.0, `base_seed` 20260811. So every
`wall_seconds` is a genuine unbudgeted natural time, exactly as the lineage
has claimed since BATCH-013.

Full value histogram: `{2:34, 3:70, 4:10, 5:42, 6:10, 7:16, 8:12}`, sum 194,
no value outside 2…8. `delta_E >= 5` population `42+10+16+12 = 80`.

| b | total | `>=5` | `=5` | `>=5` histogram | `{2,3,4}` split | remainder |
|---|---|---|---|---|---|---|
| 1.10 | 0 | 0 | 0 | `{}` | `{}` | 0 |
| 1.20 | 2 | 0 | 0 | `{}` | `{2:2}` | 2 |
| 1.30 | 7 | 0 | 0 | `{}` | `{2:4, 3:3}` | 7 |
| 1.40 | 45 | 4 | 0 | `{6:1, 7:1, 8:2}` | `{2:19, 3:19, 4:3}` | 41 |
| **1.45** | **115** | **36** | **20** | **`{5:20, 6:4, 7:6, 8:6}`** | **`{2:28, 3:43, 4:8}`** | **79** |
| 1.70 | 194 | 80 | 42 | `{5:42, 6:10, 7:16, 8:12}` | `{2:34, 3:70, 4:10}` | 114 |

**Every claimed figure of the new upper arm reproduces exactly.**
`n_naturally_completed <= 115`; `delta_E >= 5 <= 36`; the `>=5` histogram
`{5:20, 6:4, 7:6, 8:6}` (sums to 36); `delta_E = 5 <= 20`; remainder `79` in
`{2:28, 3:43, 4:8}` (sums to 79, and `36 + 79 = 115`); split `115/79`;
source-side cap `1.45/2 = 0.725` s. The `b = 1.10` arm is **exactly 0** — the
smallest archived time is `1.149932861328125`, so no record is below 1.1, and
the "EXACT, not merely an upper bound" labelling of that arm is right for the
reason given (contention is monotone in the safe direction), subject only to
PF-26's cross-platform caveat.

I **confirm** the Coordinator's independent reproduction of `115 / 36 / 79 /
{5:20,6:4,7:6,8:6} / {2:28,3:43,4:8} / 20`. I also independently recomputed
the `{2:28, 3:43, 4:8}` split that the draft's provenance note honestly flags
as taken from round 1's table rather than recomputed by the Coordinator: it
is **correct**. That note can now be updated to say two independent
recomputations obtained it.

Extrema: min `1.149932861328125` at `[749, 1684]`, `delta_E 2`; min over
`delta_E >= 5` is `1.3924050331115723`; max `1.6985499858856201`. The eight
smallest by coordinate are exactly the eight named in
`floor_calibration_set_v11`, in the listed order, to full float precision, and
the ninth (`[2154, 1467]`, `1.3176441192626953`) and tenth (`[2405, 1364]`,
`1.3180382251739502`) are as PF-24(a) states, with the gap being 2.98 ms and
then a further 0.39 ms. The draft's replacement of "comfortably separated"
with "NOT COMFORTABLE; MERELY UNAMBIGUOUS" is accurate.

On the comparative table at lines 249–255: `45 vs 115`, `4 vs 36`, `0 vs 20`,
`{6:1,7:1,8:2} vs {5:20,6:4,7:6,8:6}`, `45/149 vs 115/79`, `485.0 vs 494.7` —
all six rows check. The `45/149` and `115/79` splits are correct against
`194`. The comparative argument replacing the withdrawn necessity claim is a
genuine argument: it names the constraint, states what the constraint does and
does not decide, names the alternative, prices it, and makes a trade. I
searched for residual necessity language and found none — the surviving
"ONLY [1.1, 1.4]" strings are all inside quotation marks attributing the claim
to the round-2 draft. Task item (b) is **clean**.

## §2 — Orphan `1.4`-derived constants: full-text sweep [task item 2]

I did not accept the draft's assertion at line 922 that "a full-text sweep
for surviving 1.4-derived constants was performed"; I performed my own,
listing every one of the 76 lines containing the substring `1.4` and
classifying each.

Result: **no orphan operative constant.** The classification is:

- `1.45` in an operative position — `SWEEP_BUDGETS`, G-1's threshold, the
  source-side cap derivation, P-1's `0.5 × 115 = 57.5`, G-0b's and G-2b's
  references, the budget terms. Correct.
- `1.4` / `1.40` as **historical or comparative** — the round-2 draft's
  choice recorded by name (lines 218–230, 731–758, 891–939), the prediction
  table's `b = 1.40` row (1189), the "1.4 vs 1.45" comparison header (249).
  All correctly historical.
- `1.4x`, `1.4x-2.5x`, `1.4x-1.7x` — load ratios, dimensionless, unrelated.
- `+1.4%` — the b=0.8 overshoot figure from RT-BATCH-013.
- float tails inside archived times.

Both non-sweep-derived thresholds check independently:

- **G-2, `1.32242279052734375`.** With `A = 1.149932861328125`, exact rational
  arithmetic gives `1.15 × A = 1.32242279052734375` — the draft's digits are
  the exact real value, and it is archived-floor-derived, so PF-17's budget
  change correctly does not move it. The draft's claim here is true.
  *One implementation caution, not a PF:* the IEEE-754 double nearest to the
  literal `1.32242279052734375` is `1.3224227905273438`, while evaluating
  `1.15 * A` in floating point yields `1.3224227905273436` — one ULP apart.
  Round 2's phrase "exact to the last digit" is true of the real number, not
  of the float. The specification already requires the frozen literal and
  forbids runtime recomputation, so this cannot bite; it is worth one line in
  the Executor's instructions so nobody writes `1.15 * A`.
- **G-0's 15.0 s and CAL-2's 2.0 s** contain no sweep-derived quantity, and
  `F_cal`'s own definition (minimum measured CAL-1 wall_seconds over
  non-timed-out members of a coordinate-pinned set) contains none either.

Task item (a)'s constant half is **clean**.

## §3 — PF-18's shallow-copy CAL-1, against the real function body [task item 4]

I read `run_truncation_probe_v9` (lines 147–211) statement by statement, not
its docstring.

```
156    field = graph["field"]
157    q = graph["q"]
158    vertices = graph["vertices"]
```

Those are the **only three subscripts of `graph` in the function**. There is
no other `graph[` anywhere in the body, no `.get(`, no iteration over
`graph.items()`, no adjacency table, no neighbour map, no precomputed
structure. Everything downstream flows through `field` (`field.is_in_fp`,
`field.frobenius`), `q`, `vertices`, the imported
`v8probe.derive_per_vertex_seed`, and `compute_delta_e.two_sided_search`.
**The precondition the Executor is told to check is satisfied**, and the
shallow copy `{**graph, "vertices": THE_EIGHT}` therefore changes exactly one
thing and silently changes nothing.

The claimed 8-vertex consequences all follow directly from lines 159–160 and
198–200:

- `fp_rational = [v for v in vertices if field.is_in_fp(v)]` — all eight
  calibration vertices are drawn from the 194 non-`F_p`-rational records, so
  over `cal_graph` this list is **empty**, hence
  `n_fp_rational_wired_unconditionally = 0` and `new_delta_map` starts empty.
- `non_fp_rational` is exactly the eight, so `n_attempted = 8` (incremented
  once per loop iteration at 171–172) and `n_non_fp_rational = 8`.
- `coverage_fraction = n_resolved / float(n_non_fp_rational)` = `n_resolved/8`
  — **a different denominator from the sweep's /194**, exactly as the draft
  says, and the draft's requirement that the artifact label this explicitly is
  the right control.

**The RNG claim is true, and I verified it by execution rather than by
reading.** `derive_per_vertex_seed(base_seed, vertex)` is
`sha256("SSIQ-v8-probe:%d:%r" % (base_seed, tuple(int(c) for c in vertex)))`
truncated to 8 bytes — a pure function of `(base_seed, vertex)` with **no
dependence on position in the list, on the size of the list, or on any prior
call**. I computed it for all 194 archived vertices at `base_seed = 20260811`
and compared against the archived `seed_used` field: **194 of 194 match.**
So CAL-1 on the restricted graph reproduces exactly the per-vertex RNG streams
RUN-h used for those eight vertices, restriction and reordering are both
harmless, and the measured/archived ratio is a like-for-like timing comparison
of identical work. `random.Random(seed_v)` is constructed fresh inside the
loop (176), never shared or advanced across vertices.

One residual, non-blocking: `THE_EIGHT` must be a list/tuple of **tuples of
ints** to match the in-process vertex representation (the archived records
store `list(v)` at line 190, so the in-process objects are tuples). The draft
says "as tuples", which is right; worth the Executor asserting
`set(THE_EIGHT) <= set(graph["vertices"])` before the call so a
representation mismatch fails loudly instead of producing an empty
`non_fp_rational` and a vacuous `8 → 0` calibration. I list this under
required controls.

Task item (d) is **clean**, and PF-18 is, as the draft concedes, better than
what it replaced: after it the amendment contains no authorized duplicate of
any search loop.

## §4 — G-0 / G-0b / G-1 / G-2 / G-2b / G-3: ordering and well-definedness [task item 3]

**Are all gates evaluated before any sweep point runs?** Yes, and it is
stated three times in mutually consistent language: `amendment_scope`
("evaluated before the sweep loop begins, NOT a narrative caveat"),
`load_defer_gate_v11` ("evaluated immediately after step (0b)'s calibration
and BEFORE the sweep loop begins"), and the step-(0b)-outside-per-sweep-point-
isolation clause at lines 197–199. The calibration itself is ordered
CAL-1 → CAL-2 by data dependency (CAL-2's `measured_source_fraction` divides
by "CAL-1's measured total for the same vertex"), which is consistent with
G-0 (CAL-1) preceding G-0b (CAL-2).

**Is the relative order unambiguous?** Yes, once G-2b's "Independently of
G-2" is read against G-3's "and G-2b did not fire". The branch set reduces,
without residue, to:

```
if  (any CAL-1 timed_out) or (fewer than 8 CAL-1 records):   DEFER  [G-0]
elif (any CAL-2 timed_out at 2.0s):                          DEFER  [G-0b]
elif F_cal >= 1.45:                                          DEFER  [G-1]
else: PROCEED;  load_confounded = (F_cal > 1.32242279052734375)   [G-2]
                                  or (LAC(1.45) < 10)             [G-2b]
```

That is total, exclusive on the defer side, and monotone on the stamp side.
**No pair can conflict**: G-2 and G-2b both set the same boolean to the same
value, so simultaneous firing is idempotent, and G-3 is definitionally the
complement. I could construct no state in which the run proceeds on a
corrupted premise that the gate was written to catch.

**Is `F_cal` well-defined?** Yes, and for the reason the draft gives: G-0
fires first on any CAL-1 timeout or short record set, so by the time G-1
evaluates, all eight are non-timed-out and the "counting only non-timed-out"
qualifier in `F_cal`'s definition is vacuous rather than potentially
empty-set. G-0b sits between G-0 and G-1 but concerns CAL-2 only and cannot
disturb this. `F_cal` is in seconds and both thresholds it meets are absolute
second values; the units are consistent.

**Is G-2b's median ratio computable from what CAL-1 actually collects?**
Yes. CAL-1 is required to record, per vertex, `measured wall_seconds` and
"the archived wall_seconds above" and "the ratio measured/archived", plus
their median as `measured_load_inflation_ratio`. The archived denominators are
pinned in the frozen text to full precision. The product-and-count step needs
RUN-h's 194 archived `wall_seconds`, which `required_artifacts_note` already
lists as a read-only input. Computable, at zero extra compute, exactly as
claimed.

**Is G-2b inert?** No — and I checked, because a stamping clause that never
fires is worse than none. Counting `#{archived × r < 1.45}` as a function of
the median ratio `r`: `r = 1.00 → 115`, `1.05 → 31`, `1.10 → 10`,
`1.105 → 7`, `1.15 → 3`, `1.30 → 0`. So G-2b (`< 10`) fires at
`r ≳ 1.107`, while G-2 fires at a floor-vertex ratio `> 1.15`. **G-2b is
strictly more sensitive than G-2 in ratio terms** and is a genuine addition,
not decoration. Credit where due.

**Is the disclosed PF-23 weakening honest about what G-2b does and does not
catch?** Partly. It is honest that stamping is weaker than deferring and
honest about why (n = 8, extremity-selected, applied uniformly). It is *not*
explicit that the chosen threshold of 10 sits far below the draft's own P-2
artifact boundary of 58, which leaves a band where the two instruments
disagree about the same run. See **PF-29**.

Task item (c) is **clean on well-definedness and ordering**; the residual is
the threshold-coherence advisory, not a definedness defect.

## §5 — PF-19 and PF-20, checked for genuine exhaustiveness [task item 5]

**PF-19 / the M-1/M-2 partition.** `delta_e_upper_bound` values are integers,
so `new > archived` and `new < archived` do exhaust `new != archived`.
`Q-LOAD` is keyed to the run-level top-level `load_confounded`, which
`load_defer_gate_v11` makes a "REQUIRED, ALWAYS-PRESENT top-level boolean …
never omitted and never defaulted silently" — so the qualifier's referent is
defined in every branch that writes the file. The round-2 defect (a per-vertex
flag defined nowhere) is genuinely repaired, and repaired without inventing a
new flag, which was the right move. The one uncovered case is a
naturally-completed vertex **absent from the archived map** — it would be
neither M-1 nor M-2 and would fall into `compare_against_archived`'s
`n_this_run_resolved_not_in_archived` counter (line 286). At p=2437 the
archived map covers all 203 vertices, so this is empty in fact; it is worth
one clause, not a PF.

But see **PF-28**: the *content* of Q-LOAD is wrong even though its
definition is now clean.

**PF-20 / P-3's ordering.** I checked the factual claim the new P-3a rests on,
because the draft puts it first on the strength of it: *"RUN-h recorded no
load figures at all"*. **True.** `RUN-SSIQ-a85692-h/environment.json` records
`python_version`, `platform`, `os`, `architecture`, `cpus_available: 4`,
`memory_total_gb_approx: 15`, dependencies, resource caps and detached-
execution notes — and no load average of any window. `manifest.yaml` and
`execution_report.yaml` contain no `loadavg`, `load_average`, `getloadavg` or
`hw.ncpu` string. So P-3a's premise holds and the observation that "RUN-h's
side of that comparison DOES NOT EXIST" is literally correct **for load**.

Is putting P-3a *first* justified? Under the draft's own picture of the world
— one heavily and variably loaded machine — yes, it is the right prior
ordering, and it repairs a real false dichotomy. But that picture is the one
PF-26 breaks: RUN-h's `environment.json` does record `cpus_available: 4` and a
Linux x86_64 platform, so the *hardware* side of the comparison does exist,
was never consulted, and makes P-3b (cross-hardware) at least as likely as
P-3a rather than clearly second. The ordering is conditional on an unchecked
premise; the branch set is also not exhaustive, per PF-27. Both are folded
into those findings rather than counted again here.

## §6 — Budget [task item 6]

Every term re-derived independently:

| term | draft | recomputed |
|---|---|---|
| sweep worst case | `194 × 2.55 = 494.7` | `494.7` ✓ |
| lower arm | `194 × 1.1 = 213.4` | `213.4` ✓ |
| upper arm | `194 × 1.45 = 281.3` | `281.3` ✓ |
| CAL-1 | `8 × 15.0 = 120.0` | `120.0` ✓ |
| CAL-2 | `8 × 2.0 = 16.0` | `16.0` ✓ |
| subtotal | `632.7` | `494.7+120+16+2 = 632.7` ✓ |
| with overshoot | `630.7 × 1.042 = 657.2` | `657.189` ✓ |
| margins | `1.58x`, `1.52x` | `1.5805`, `1.5216` ✓ |
| CPU-hours | `0.183`, `55.3%` | `657/3600 = 0.1825`, `55.30%` ✓ |
| PF-17 delta | `+9.7 s`, `1.55x → 1.52x` | `485.0 → 494.7`; `621×1.042+2 → 1.5406` ✓ |

The `630.7` base for the overshoot factor (subtotal minus the 2 s graph
build) is the right base, since the overshoot mechanism lives in
`build_smooth_table`'s loop and does not apply to graph construction. Applying
`+4.2%` to CAL-1/CAL-2, which are expected to complete naturally, is
conservative in the stated direction and the draft says so.

The `~2 s` graph-build allowance is independently supported by the committed
artifacts: RUN-h's `wall_clock_seconds` is `278.49618768692017` against a sum
of per-vertex `wall_seconds` of `277.831778…`, leaving `0.664 s` for the
graph build, identity verification, two comparisons and all JSON I/O. `2 s`
is roughly 3x that. Task item (f) is **clean**.

One honest note on the budget's own load-invariance argument. "A TRUNCATED
vertex consumes ~b wall seconds regardless of contention" is correct as to
`build_smooth_table`'s gating, but a truncated vertex still pays the final
straddling pop, and under contention that pop takes longer in wall time. This
is exactly the `+4.2%` term, and it is already in the arithmetic, so the
argument is fine; I flag it only because the same mechanism is PF-27's, and
the specification currently treats it as a budget nuisance in one place and
denies its existence in another.

---

## §7 — Fresh pass: what round 3 introduced, and what nobody checked

### 7.1 PF-26 [BLOCKING] — the archived machine and the measuring machine are not the same machine, and the frozen text asserts they are

**The finding.** The amendment's entire instrument is a comparison of RUN-k's
measured wall times against RUN-h's archived wall times: `F_cal` versus `A`,
G-0's "15.0 s implies an ~8.8x slowdown", G-1's `1.45`, G-2's `1.15 × A`,
G-2b's median measured/archived ratio, and the whole prediction curve. That
comparison is only meaningful between comparable machines. The specification
asserts comparability by name — the caveat block at line 585 is titled
**"SAME-HARDWARE CONTENTION CAVEAT"** — and nowhere checks it.

I checked it. From the committed artifacts:

| | archived runs `-a` … `-j` (incl. **RUN-h**) | the machine every load figure in the spec came from |
|---|---|---|
| platform | `Linux-6.18.5-fc-v18-x86_64-with-glibc2.39` | `Darwin … RELEASE_ARM64_T6041` |
| cores | `cpus_available: 4` | `sysctl -n hw.ncpu` = **14** |
| ISA | x86_64 | arm64 |
| Python | `3.11.15 … [GCC 13.3.0]` | not recorded in the spec |

All three observers whose figures the spec freezes (this Coordinator on
2026-08-06, the round-1 reviewer, the round-2 reviewer) obtained their core
count with `sysctl -n hw.ncpu`, a BSD/Darwin command that does not exist on
the Linux platform every run in this lineage actually used. Their load
averages are therefore host figures. I re-measured this session and got the
same host: 14 cores, load `36.09 / 56.77 / 63.22`, and `75.85 / 89.14 /
73.54` twenty minutes earlier — figures further outside the spec's stated
"roughly 1.4x to 2.5x" range than round 2's were, and on the wrong
denominator besides.

**Why this is blocking rather than pedantic.** Exactly one of two things is
true, and the specification addresses neither:

- **(a) RUN-k executes where RUN-a…-j executed** (a 4-CPU Linux environment).
  Then every load figure frozen in this document describes a machine that
  will not run the experiment; the "14 cores" arithmetic uses a denominator
  3.5x too large; the prominently placed operational prediction — "at ~2.4x,
  F_cal would land near 2.8 s and the gate would fire G-1, so executing today
  most likely buys ~140 s of calibration and a deferral" — is unfounded, and
  it is precisely the kind of statement that causes a Coordinator to defer a
  dispatch or to discount a real result; and PF-14(d)'s required
  `environment.json` field `hw.ncpu` is specified by a command that will fail
  there. (Prior runs record `cpus_available`, presumably `os.cpu_count()`,
  which is a different quantity from `hw.ncpu` and which the spec never
  names.)
- **(b) RUN-k executes on the Darwin arm64 host.** Then the comparison
  against RUN-h is cross-ISA, cross-OS, cross-libc and cross-Python-build,
  the caveat is misnamed, and the **cross-hardware branch stops being an
  aside and becomes the live case**. Two consequences the draft treats as
  remote become primary: the b = 1.10 s arm's "guaranteed-truncated"
  monotone-safety rests explicitly on the execution machine not being *faster*
  than RUN-h's — a modern arm64 core against a 4-vCPU x86_64 sandbox is a
  plausible speedup, and the archived floor is only `1.1499 s` against a
  `1.10 s` budget, a **4.3% margin**; and P-3b overtakes P-3a in prior
  likelihood, inverting the ordering PF-20 just installed.

Under (b) the phrase "THE GUARANTEED-TRUNCATED CONTROL ARM", which is
load-bearing for PF-17's entire comparative argument, is not guaranteed.

**This is the same defect class as PF-17, one level deeper:** a claim asserted
in frozen text as settled ("SAME-HARDWARE") that was never checked, where the
committed evidence needed to check it was sitting in `environment.json` in the
same run directory the prediction curve was computed from. Three prior
sessions of the same model read that directory and none opened that file. I
note, per my own `independence_cap`, that this is what correlated review looks
like from the inside.

**The repair is cheap and costs no compute.** (i) Record RUN-h's platform,
`cpus_available` and Python build in the frozen text, next to the archived
figures they qualify. (ii) Rename the "SAME-HARDWARE CONTENTION CAVEAT" to
something the document can support, and state which machine the frozen load
observations were taken on and by what command. (iii) Add a gate branch —
call it **G-0c**, ordered with the other infrastructure branches — that reads
RUN-k's own `platform` / `cpus_available` and compares them with RUN-h's
committed values, and **DEFERs on mismatch**, on the same AGENTS.md rule 3
footing as G-0 and G-0b. This is three lines of Executor code and turns an
asserted premise into a measured one, which is what PF-14 did for load and is
the identical argument. (iv) Replace `hw.ncpu` with a portable requirement
(`os.cpu_count()` plus `os.getloadavg()`, both of which exist on both
platforms) so PF-14(d) is satisfiable wherever the run lands. (v) If the
answer is (b), state that the `b = 1.10 s` arm's truncation guarantee is
conditional on the measured `F_cal` exceeding 1.10 s and let the gate say so,
rather than asserting it in prose.

### 7.2 PF-27 [BLOCKING] — `115` is not an upper bound, and the argument that it survives as one has the sign backwards

**The finding.** Lines 312–320 state, and `pf12_summary` repeats:

> because the budget test sits at the TOP of `build_smooth_table`'s heap
> loop … `to_s` is False iff the source heap EXHAUSTS, so `to_s == False`
> actually implies `t_source <= b/2 + (one heap pop)`. The restated premise
> is therefore very slightly STRICTER than the code — **an error in the
> PERMISSIVE direction for the only use made of it here (an upper bound on
> `n_naturally_completed`), which is why the upper-bound labelling survives
> unchanged.**

That inference is backwards. If the frozen premise is *stricter* than what
the code will actually accept, the code produces **more** natural completions
than the premise admits, which is an attack on an upper bound, not a defence
of one. Round 2 (§3.2) reached the same conclusion by a different route —
that the bound "actually rests on" the necessary condition `t_total < b` — and
that route fails too, because `t_total < b` is **not** a necessary condition,
by the identical mechanism applied to the other half:

```
compute_delta_e.py:189-192   remaining = max(0.0, b - (t_mid - t0))
compute_delta_e.py:155-159   while heap:  if time.time() - t0 > remaining: timed_out=True; break
```

The target build's loop-top check is against `remaining` measured from
`t_mid`, i.e. against total elapsed `> b`. A target expansion whose **final**
pop begins just under the deadline and finishes just over it exits the
`while heap:` loop *normally*, with `to_t = False`. So `timed_out == False`
implies `t_total <= b + (one heap pop)`, not `t_total < b`. The necessary
condition the whole prediction curve rests on is off by exactly the quantity
RT-BATCH-013 already measured on this lineage.

**Why it is quantitatively load-bearing here, and was much less so at 1.4.**
The archived distribution is at its densest immediately above 1.45:

| slack ε | count `< 1.45 + ε` | count `< 1.40 + ε` |
|---|---|---|
| 0 | **115** | 45 |
| 5 ms | 124 | — |
| 7.2 ms (0.5% of b) | 127 | 56 |
| 11 ms | 135 | — |
| 20.3 ms (1.4% of b) | 147 | 67 |
| 60.9 ms (4.2% of b) | 187 | 130 |

18 archived records lie in `[1.45, 1.46)`, 30 in `[1.45, 1.47)`, 71 in
`[1.45, 1.50)`. RT-BATCH-013's measured overshoots correspond to absolute
slacks of about 25 / 11 / 5 ms at b = 0.6 / 0.8 / 1.0. At any of those, the
honest bound is between **124 and 157**, not 115.

**What breaks.**

1. The label "UPPER BOUND", applied to `115` in `pre_registered_prediction_
   curve_v11`, in `amendment_scope`, and in the pre-committed `strength_note`
   clause that every future citation must quote, is unsupported as a one-sided
   bound. The true statement is that `115` is a **reference count with
   unquantified corrections in both directions**: the `b/2 = 0.725 s`
   source-side cap can only push the realised count *down* by an amount the
   archive cannot evidence, and the final-pop slack can only push it *up* by
   an amount the archive can bound only crudely. That is a weaker and more
   honest object, and the amendment should freeze that one.
2. **P-3's branch set is not exhaustive**, despite saying "THE BRANCH SET HERE
   IS EXHAUSTIVE". A measured count in roughly `(115, 155]` is fully
   consistent with identical hardware, identical load, and every premise of
   this amendment intact — it is the code's own documented behaviour. As
   written, P-3 pre-commits the run to reporting such an outcome as a
   scheduling difference (P-3a), a hardware difference (P-3b), or a premise
   falsification (P-3c). This is the *same shape* PF-20 was raised to fix, one
   layer down: an "exhaustive" branch set that omits the most mechanical
   explanation available.
3. **P-1/P-2's numeric boundary inherits the error.** `0.5 × 115 = 57.5` is a
   convention and survives as one, but its anchor is not the quantity the
   draft says it is.

**The repair, again text-only.** (i) Withdraw the "PERMISSIVE direction"
sentence and replace it with the correct two-sided statement. (ii) Add a
**P-3d**, ordered *first* among the over-bound branches because it is the
cheapest explanation: the measured count exceeds the archived-derived
reference by an amount consistent with final-pop overshoot, with a
pre-registered magnitude — e.g. treat `115 < measured <= #{archived < 1.45 +
0.042 × 1.45} = 187` as the "within the instrument's own overshoot tolerance"
band, or pick a tighter ε and justify it. (iii) Keep `115` as the headline
reference count with both correction directions named wherever it is quoted.
(iv) One free improvement: CAL-1 already measures eight vertices at 15.0 s
with no truncation, so the run can *measure* nothing about the final-pop
slack — but the **sweep's own truncated vertices** at b = 1.10 s give
`measured wall_seconds − 1.10` for up to 194 vertices, a direct, free
measurement of the overshoot distribution on the actual machine. Requiring
that distribution to be reported would let a future amendment set ε
empirically instead of by inheritance.

### 7.3 PF-28 [ADVISORY] — Q-LOAD stamps the one outcome PF-25 says is informative, on a mechanism that provably cannot cause it

`Q-LOAD` says: if the run's `load_confounded` is true, then **every** mismatch
it reports, M-1 or M-2, "is additionally stamped as arising from a
load-confounded run and is not mathematical evidence under AGENTS.md rule 3
until re-measured on an unloaded machine."

But the mismatches in question are on **naturally-completed** vertices, and
the draft's own PF-25 derivation establishes that such a vertex's value
cannot depend on anything but the vertex: `timed_out == False` means both
heaps exhausted, a completed table's contents are RNG-independent, and
`best_deg` is a minimum over a multiset. **Machine load determines *which*
vertices complete naturally; it cannot alter the *value* returned by one that
did.** So Q-LOAD, as applied to the equality cross-check, discounts on a
mechanism that is incapable of producing the observation.

This matters because PF-25 has just reclassified the equality half as a
control "whose only informative outcome is FAILURE". Under G-2 — which fires
at a floor inflation of only 15%, entirely plausible on any loaded machine —
the single informative outcome this amendment can produce would be born
pre-stamped "not mathematical evidence until re-measured". That is the
amendment disarming its own instrument.

**Repair:** restrict Q-LOAD to the quantities load actually reaches —
`n_naturally_completed`, the naturally-completed histogram, the P-1/P-2/P-3
reading, the composition of the naturally-completed set — and state
explicitly that a **value** mismatch on a naturally-completed vertex is
*not* discountable by load, for the reason PF-25 gives, and must be surfaced
loudly regardless of the stamp. This strengthens the amendment at zero cost.

### 7.4 PF-29 [ADVISORY] — G-2b's threshold of 10 is not aligned with the draft's own artifact boundary of 58, and the load-adjusted count is undefined on the branch that must report it

Two parts, both in round-3's new G-2b.

**(a) Threshold coherence.** P-2 pre-registers that a measured
`n_naturally_completed` below `58` at b = 1.45 s reads "in the first instance
an EXECUTION-ENVIRONMENT ARTIFACT under AGENTS.md rule 3". G-2b stamps
`load_confounded: true` only when the *predicted* count falls below `10`. From
§4's table, a median inflation ratio of `1.05` — a 5% slowdown, entirely
ordinary — yields a load-adjusted predicted count of `31`. Such a run is not
stamped by G-2b, and if `F_cal <= 1.32242279052734375` it is not stamped by
G-2 either, so it is written with `load_confounded: false` while the
specification's own reading rule calls its likely outcome an environment
artifact. The band of disagreement is wide: predicted counts from about 10 to
57.

The draft's stated reason for the *stamping* form (n = 8, extremity-selected,
cruder than the floor measurement) is a good reason and I accept it — that is
my answer to the question the draft poses to this reviewer. The reason does
**not** justify the *value* 10, which is nowhere derived. Aligning G-2b's
threshold with P-2's own boundary (58, i.e. `0.5 ×` the reference count) would
make the artifact's top-level boolean agree with the specification's own
reading rule, at no compute cost and with no change in kind. If 10 is
deliberately conservative, the frozen text should say why it is two rules
apart from P-2 and not merely that stamping is weaker than deferring.

Mitigating, and worth recording in the draft's favour: line 1602 already
requires the applicable P-1/P-2/P-3 reading to be reported **in-band** per
sweep point, so a reader opening only the JSON does see the artifact reading
even when `load_confounded` is `false`. That converts this from a BATCH-010
propagation failure into an internal-coherence defect.

**(b) Definedness on the defer branches.** The G-0/G-0b/G-1 artifact's
**closed** required list includes "the load-adjusted predicted counts". But
G-0 fires precisely when some CAL-1 vertex timed out *or fewer than 8 records
were produced* — and the median ratio is defined over CAL-1's eight
measured/archived ratios with, unlike `F_cal`, **no** stated exclusion of
timed-out vertices and no stated behaviour when zero records exist. On G-0 the
required field is therefore either meaningless (a median over ratios of ~13,
giving a predicted count of 0) or undefined (empty record set), while the
closed list — whose closedness round 2 correctly identified as the clause that
makes the branch airtight — requires it to be present. **Repair:** state
whether the G-2b median excludes timed-out CAL-1 vertices (it should, for
symmetry with `F_cal`), and state that on G-0 the load-adjusted counts are
reported as `null` with a reason string rather than as a number, so the closed
list stays satisfiable without a fabricated zero. This is the same
"ABSENT, not zero" discipline PF-14 already established, applied to the field
PF-23 newly added.

### 7.5 PF-30 [ADVISORY] — the file's own motivation is not reconciled with P-4 and PF-25

Lines 4–8, the provenance header, still state that this amendment exists on
the ranked resume action `DEC-20260806-520ca4` item (1) — RT-BATCH-013's own
falsifiable prediction "that one more sweep point straddling the observed
1.14993 s natural-completion floor would test whether `delta_E>=5`
convergence begins appearing there while `delta_E=2/3` remain exactly
converged."

By the amendment's own later text it cannot test that. P-4 says **no outcome
at any budget** licenses a statement about whether `delta_E >= 5` convergence
begins at the floor. PF-25 says the equality half confirms nothing new in the
positive direction at any `k`. So the document opens by naming a question and
closes by pre-committing that it cannot answer it. The `PURPOSE (RESTATED
AFTER PF-11/PF-13/PF-17/PF-25)` paragraph at lines 35–57 is honest and does
the restating, but it sits *below* the motivation it supersedes and does not
say that the originating prediction is out of reach.

**Repair:** one sentence in the header — that PF-11/PF-13/PF-25 and reading
rule P-4 have narrowed the originating question out of this amendment's reach,
that what remains testable is the `n_naturally_completed(b)` curve, and that
RT-BATCH-013's prediction remains open and is forwarded to the successor
amendment. Per `docs/inventor-protocol.md` §4, forwarding an unanswerable
question with named forward guidance is required; silently leaving the old
motivation at the top of a frozen file is how a question gets treated as
retired without ever being closed.

### 7.6 What I checked in the fresh pass and found clean

- **PF-25's derivation, re-derived independently.** `run_truncation_probe_v9`
  shares across loop iterations only `field`, `q`, `new_delta_map` (written,
  never read, per vertex) and the counters. `rng_v` is constructed fresh at
  176 from a seed that is a pure function of `(base_seed, vertex)`. `target =
  field.frobenius(v)` is deterministic. `rng` reaches
  `build_smooth_table` only via `neighbors_ell_isogenous →
  find_roots_with_multiplicity`, i.e. root *order*, not the root *set*, and
  `best_deg = min` over a multiset. **A naturally-completed vertex's value
  cannot depend on what happened to other vertices in the same pass.** PF-25
  is right. The only shared mutable state I could posit is memoisation inside
  the field or modular-polynomial modules, which would affect timing and not
  values, and premise (i) already covers it.
- **The equality half's prior evidence state**, read verbatim from the
  artifact: `n_both_resolved 203`, `n_value_matches 203`, `n_value_differs 0`,
  `value_differs_triples []`, `non_fp_rational_only {194, 194, 0}`. The
  disclosure at lines 404–413 is accurate.
- **The `remaining == 0.0` degradation path** is as described: `0.0` is a real
  zero budget, `heap = [(1, start_j)]` is non-empty on entry, so the first
  loop-top check fires, the table is empty, `common` is empty, `resolved` is
  `False`, `timed_out` is `True` — landing exactly in
  `n_unresolved_and_timed_out`. The PF-12 and PF-16 fixes are consistent with
  each other, as the draft claims.
- **The I-1/I-2/I-3 identities** are correct against the counter semantics at
  lines 168–196 and 202–211: `n_timed_out` and `n_attempted` are over all
  attempted, `n_resolved` over attempted, and the four sub-counts partition as
  stated.
- **`resolved_non_fp_set` plumbing.** Correct: the returned dict (202–211) has
  no such key, so the caller must reconstruct it from `per_vertex_records`,
  exactly as the plumbing note says, and the naturally-completed variant
  filter `resolved is True and timed_out is False` matches the record shape at
  189–196.
- **No necessity language survives** about the sweep-point choice outside
  attributed quotation.
- **Scope discipline.** `OBJECTIVE_BOUNDARY` is, if anything, more restrictive
  than round 2's. No scope inflation; p=2437 only; toy scale stated; no
  cryptographic transfer claimed; no PERSISTS/WEAKENS label; the
  RT-BATCH-011 question explicitly disclaimed.
- **No implementation file yet**, so nothing to diff against the frozen
  function-level diff list; the list itself is consistent with the real
  modules' contents.

---

## §8 — The two judgement calls the task asked for

**(a) Is PF-25's reclassification right, and is what remains worth ~657 s?**

The reclassification is **right** and I would not soften it; I re-derived it
above from source. But the task is correct that it quietly reduces the
amendment's contribution, and the honest accounting is worth stating in the
frozen text rather than leaving to a reader:

- The `b = 1.10 s` arm's result is **pre-registered as exactly 0** and the
  draft itself says it "is NOT presented as a new observation".
- The equality half at both arms is, by PF-25, a control whose expected
  outcome is a null and whose only informative outcome is a failure the
  derivation says cannot occur.
- The naturally-completed value histogram at `b = 1.45 s` is speed-selected,
  and the draft's own BATCH-012 clause forbids citing it as informative about
  the `delta_E` population.
- What is left is **one integer** — the measured `n_naturally_completed` at
  `b = 1.45 s` — read against a reference count that PF-27 shows is not the
  one-sided bound the draft says it is, on a machine PF-26 shows may not be
  the machine the reference came from, with the reading rule P-2 declaring any
  value below 58 an environment artifact carrying no mathematical content.

So: the empirical yield is one number, and roughly half its possible range is
pre-committed to be uninformative. Against that: the cost is genuinely small
(worst case `~657 s`, `0.183` CPU-h, and realistically far less since 115 of
194 vertices are expected to finish early), the campaign is under no budget
cap, and an instrument-integrity control that has never been run in the mixed
regime is a legitimate thing to spend a tenth of a CPU-hour on. **My judgement
is that it is worth running — but only with PF-26 and PF-27 repaired, because
without them the one number it produces is not interpretable against the
reference it is being compared to.** I would also record in the frozen text
that the amendment's expected yield is one integer plus two controls, so no
later citation can inflate it.

I additionally endorse, rather than dispute, the draft's decision to **defer**
round 2's optional null-object control (re-running the upper arm under the
same seed, or the eight calibration vertices at the sweep budget). The
reasoning given — a third measurement configuration on a third pre-freeze
round raises specification risk more than it raises yield — is sound. But I
would attach a condition: the successor amendment that extends above 1.45 s
must carry it, because the `n_naturally_completed(b)` curve is precisely the
kind of reported quantity that needs a null object of the same shape, and this
amendment measures it at two points without one.

**(b) Is PF-23's "stamping form only" adoption acceptable?**

**Acceptable in kind, defective in threshold.** The stated reason for
preferring a stamp to a defer is a real epistemic reason (n = 8,
extremity-selected, applied uniformly to a 194-vertex distribution) and not a
convenience, and I verified in §4 that G-2b is not inert — it fires at a median
inflation of about 1.107 where G-2 needs 1.15 at the floor vertex, so it
genuinely tightens the gate. I do not ask for it to be upgraded to a defer.

What defeats part of the purpose is the **value 10**, which is undefended and
sits two rules apart from the draft's own P-2 boundary of 58. That is PF-29(a)
and it is an alignment fix, not a redesign.

---

## Objections

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3
  task_id: TASK-20260807-43d16f-r3
  claim_under_review: >-
    That specification_v11.yaml, in its round-3 revision at commit 5d6caed43,
    has correctly applied PF-17 (repair A, SWEEP_BUDGETS = [1.1, 1.45]) and
    the eight advisory findings PF-18..PF-25, and is ready to be frozen as a
    pre-registered protocol amendment authorizing RUN-SSIQ-a85692-k.
  objections:
    - id: PF-26
      severity: BLOCKING
      title: >-
        The archived machine and the measuring machine are not the same
        machine, and the frozen text asserts by name that they are.
      finding: >-
        Every run in this lineage, RUN-SSIQ-a85692-a through -j including
        RUN-SSIQ-a85692-h itself -- the sole source of every archived time
        that A, F_cal, G-0, G-1, G-2, G-2b and the entire prediction curve
        are built on -- executed on Linux-6.18.5-fc-v18-x86_64-with-glibc2.39,
        Python 3.11.15 [GCC 13.3.0], cpus_available 4 (verified directly in
        each run's environment.json). Every load observation frozen into this
        specification was taken with sysctl -n hw.ncpu on a 14-core arm64
        Darwin host (re-measured this session: hw.ncpu 14, load 36.09/56.77/
        63.22, and 75.85/89.14/73.54 twenty minutes earlier) -- a BSD command
        that does not exist on the platform every archived run used. The
        specification titles its caveat block "SAME-HARDWARE CONTENTION
        CAVEAT", derives a prominent operational prediction from those host
        figures ("at ~2.4x, F_cal would land near 2.8 s and G-1 would fire"),
        and requires hw.ncpu as an environment.json field -- while in 1756
        lines it never records RUN-h's platform, never cites RUN-h's
        environment.json, and never requires the Executor to check that RUN-k
        runs where RUN-h ran. Either RUN-k runs on the 4-CPU Linux runner, in
        which case the frozen load narrative and the hw.ncpu requirement
        describe the wrong machine and the deferral prediction is unfounded;
        or it runs on the Darwin arm64 host, in which case the comparison is
        cross-ISA/cross-OS/cross-libc, "SAME-HARDWARE" is false, the b=1.10 s
        arm's truncation guarantee (4.3% margin against the 1.1499 s archived
        floor) is no longer monotone-safe, and P-3b overtakes the P-3a
        ordering PF-20 just installed. This is PF-17's defect class one level
        deeper: a premise asserted as settled in frozen text, checkable from a
        file in the same run directory the prediction curve was computed from,
        that four sessions of one model did not open.
      repair: >-
        Text plus three lines of Executor code, zero compute. (i) Record
        RUN-h's platform, cpus_available and Python build in the frozen text
        beside the archived figures. (ii) Rename the SAME-HARDWARE caveat and
        state which machine the frozen load observations came from and by what
        command. (iii) Add gate branch G-0c, ordered with G-0/G-0b: read
        RUN-k's own platform and cpus_available, compare against RUN-h's
        committed values, DEFER on mismatch under AGENTS.md rule 3 -- the same
        argument PF-14 made for load, applied to hardware. (iv) Replace
        hw.ncpu with os.cpu_count() + os.getloadavg(), portable to both
        platforms, so PF-14(d) is satisfiable wherever the run lands. (v) If
        the runner is the Darwin host, make the b=1.10 s truncation guarantee
        conditional on measured F_cal > 1.10 s rather than asserted in prose.
    - id: PF-27
      severity: BLOCKING
      title: >-
        115 is not an upper bound, and the stated reason it survives as one
        has the sign backwards; PF-17's move to 1.45 is what made this
        load-bearing.
      finding: >-
        The draft (lines 312-320, repeated in pf12_summary) says the
        one-heap-pop qualification is "an error in the PERMISSIVE direction
        for the only use made of it here (an upper bound on
        n_naturally_completed)". A premise stricter than the code means the
        code admits MORE natural completions than the premise, which attacks
        an upper bound rather than defending it. Round 2's rescue -- that the
        bound rests on the necessary condition t_total < b -- fails by the
        identical mechanism applied to the target half: remaining =
        max(0.0, b - t_source) is checked at the TOP of the target loop
        (compute_delta_e.py:155-159, 189-192), so a target expansion whose
        final pop straddles the deadline exits the while-heap loop normally
        with to_t False and t_total = b + (one pop). Hence timed_out == False
        implies t_total <= b + (one pop), and t_total < b is not necessary.
        The archived distribution is densest exactly there: 18 records in
        [1.45, 1.46), 30 in [1.45, 1.47), 71 in [1.45, 1.50). At the
        overshoots RT-BATCH-013 measured on this lineage (5/11/25 ms absolute
        at b=1.0/0.8/0.6) the honest count is 124/135/157, not 115. Three
        things break: the "UPPER BOUND" label that the pre-committed
        strength_note requires every future citation to quote; P-3's claim
        that its branch set is EXHAUSTIVE, since a measured 116-155 is fully
        consistent with identical hardware, identical load and every premise
        intact -- the same false-exhaustiveness shape PF-20 was raised to fix;
        and P-1/P-2's 57.5 anchor. At b = 1.4 the same slack moved 45 to
        56/67/130, so PF-17's own repair is what placed the reference point in
        the mode of the distribution.
      repair: >-
        Text-only. (i) Withdraw the "PERMISSIVE direction" sentence; state
        that 115 is a reference count with unquantified corrections in BOTH
        directions -- the 0.725 s source-side cap pushes down, the final-pop
        slack pushes up. (ii) Add P-3d, ORDERED FIRST among the over-bound
        branches: measured in (115, N_eps] is within the instrument's own
        overshoot tolerance, with eps pre-registered now. (iii) Quote the two
        correction directions wherever 115 appears, including the
        strength_note clause. (iv) Free improvement: require the b = 1.10 s
        arm's truncated vertices to report measured wall_seconds - 1.10, which
        measures the final-pop overshoot distribution on the actual machine
        for up to 194 vertices at zero extra cost, so a successor amendment
        can set eps empirically instead of by inheritance.
    - id: PF-28
      severity: ADVISORY
      title: >-
        Q-LOAD stamps the one outcome PF-25 identifies as informative, on a
        mechanism that provably cannot cause it.
      finding: >-
        Q-LOAD pre-commits that if run-level load_confounded is true, EVERY
        mismatch reported -- M-1 or M-2 -- "is not mathematical evidence under
        AGENTS.md rule 3 until re-measured". But those mismatches are on
        NATURALLY-COMPLETED vertices, and the draft's own PF-25 derivation
        (which I re-derived independently from source: fresh per-vertex RNG
        from a vertex-only seed, no cross-iteration state, completed-table
        determinism, best_deg a unique minimum over a multiset) establishes
        that load determines WHICH vertices complete, never the VALUE returned
        by one that did. Since PF-25 has just reclassified the equality half
        as a control whose only informative outcome is FAILURE, and G-2 fires
        at a mere 15% floor inflation, the amendment's single informative
        possible outcome would be born pre-stamped as not-mathematical-
        evidence. The amendment disarms its own instrument.
      repair: >-
        Restrict Q-LOAD to the quantities load actually reaches
        (n_naturally_completed, the naturally-completed histogram and its
        composition, the P-1/P-2/P-3 reading) and state explicitly that a
        VALUE mismatch on a naturally-completed vertex is NOT discountable by
        load, for the reason PF-25 gives, and must be surfaced loudly
        regardless of the stamp.
    - id: PF-29
      severity: ADVISORY
      title: >-
        G-2b's threshold of 10 is unaligned with the draft's own P-2 artifact
        boundary of 58, and the load-adjusted count is undefined on the branch
        required to report it.
      finding: >-
        (a) P-2 pre-registers that a measured count below 58 at b = 1.45 s
        reads as an execution-environment artifact under rule 3. G-2b stamps
        load_confounded only when the PREDICTED count is below 10. I computed
        the correspondence: median inflation 1.05 gives a predicted count of
        31, 1.10 gives 10, 1.15 gives 3. So a 5% slowdown yields a run written
        with load_confounded: false whose own reading rule calls its likely
        outcome an artifact; the band of disagreement is predicted counts from
        about 10 to 57. The stated reason for stamping rather than deferring
        is sound and I accept it, but it does not defend the VALUE 10, which
        is nowhere derived. Mitigating: line 1602 already requires the
        applicable P-1/P-2/P-3 reading in-band, so this is an internal
        coherence defect and not a BATCH-010 propagation failure. (b) The
        G-0/G-0b/G-1 deferral artifact's CLOSED required list includes "the
        load-adjusted predicted counts", but G-0 fires exactly when CAL-1
        records timed out or fewer than 8 exist, and unlike F_cal the G-2b
        median states no exclusion of timed-out vertices and no behaviour on
        an empty record set -- so a required field of a closed list is
        meaningless or undefined precisely on the branch that writes it.
      repair: >-
        (a) Align G-2b's threshold with P-2's own boundary (0.5x the reference
        count) or state in frozen text why it is deliberately two rules apart.
        (b) State that the G-2b median excludes timed-out CAL-1 vertices, for
        symmetry with F_cal, and that on G-0 the load-adjusted counts are
        reported as null with a reason string rather than as a fabricated
        zero -- the same "ABSENT, not zero" discipline PF-14 established.
    - id: PF-30
      severity: ADVISORY
      title: >-
        The file's own motivation is not reconciled with P-4 and PF-25, so an
        open question is left looking retired.
      finding: >-
        Lines 4-8 still state that this amendment exists to test RT-BATCH-013's
        prediction that a sweep point straddling the 1.14993 s floor "would
        test whether delta_E>=5 convergence begins appearing there". P-4
        pre-commits that NO outcome at any budget licenses a statement about
        that, and PF-25 establishes the equality half confirms nothing new in
        the positive direction at any k. The document opens by naming a
        question it closes by pre-committing it cannot answer. The restated
        PURPOSE paragraph is honest but sits below the motivation it
        supersedes and does not say the originating prediction is out of
        reach.
      repair: >-
        One sentence in the header: that PF-11/PF-13/PF-25 and P-4 have
        narrowed the originating question out of this amendment's reach, that
        what remains testable is the n_naturally_completed(b) curve, and that
        RT-BATCH-013's prediction REMAINS OPEN and is forwarded to the
        successor amendment. Per docs/inventor-protocol.md section 4, an
        unanswerable question is forwarded with named guidance, not left
        silently at the top of a frozen file.
  required_controls:
    - >-
      G-0c, a hardware-identity precondition: RUN-k's own platform and CPU
      count read at run start and compared against RUN-h's committed
      environment.json values, DEFER on mismatch, on the same rule-3 footing
      as G-0/G-0b. This is the control PF-26 needs and it costs nothing.
    - >-
      Portable environment capture: os.cpu_count() and os.getloadavg() at run
      start and run end, replacing the Darwin-only hw.ncpu that PF-14(d)
      currently requires, so the required field is obtainable on whichever
      platform executes.
    - >-
      Final-pop overshoot measurement: report the distribution of
      (measured wall_seconds - 1.10) over the b = 1.10 s arm's truncated
      vertices. Free, up to 194 samples, measures on the actual machine the
      exact quantity PF-27 shows the prediction curve is uncertain by, and
      lets a successor set eps empirically.
    - >-
      Executor assertion before CAL-1: set(THE_EIGHT) <= set(graph["vertices"])
      and len(THE_EIGHT) == 8, so a tuple/list representation mismatch fails
      loudly instead of silently producing an empty non_fp_rational list and a
      vacuous 8-vertex calibration that resolves 0 of 0.
    - >-
      Use the frozen literal 1.32242279052734375 for G-2, never the expression
      1.15 * A: the literal's nearest double is 1.3224227905273438 while
      1.15 * A evaluates to 1.3224227905273436, one ULP apart. Immaterial
      against a wall-clock measurement, but the spec already forbids runtime
      recomputation and the Executor should be told why.
    - >-
      Carried from round 2 and still owed by the successor amendment, not this
      one: a null-object control for the n_naturally_completed(b) curve. This
      amendment measures that curve at two points with no null of the same
      shape; the draft's reason for deferring it is accepted, but the deferral
      should be recorded as a debt against the successor rather than as a
      disposal.
  counterexample_or_mutation: >-
    The cheapest discriminating measurement for PF-27, requiring no new run:
    the b = 1.10 s arm is 100% truncated by construction, so every one of its
    194 per-vertex wall_seconds minus 1.10 is a direct sample of the final-pop
    overshoot on the executing machine. If that distribution has a 95th
    percentile below about 3 ms, only ~9 archived vertices sit inside the
    slack and the 115 reference is nearly one-sided after all; if it reaches
    10-25 ms, 20 to 42 vertices do and P-3's trigger is simply in the wrong
    place. The measurement is already inside the run and costs nothing to
    report. For PF-26 the discriminating control is even cheaper: print
    platform.platform() and os.cpu_count() at run start and diff them against
    RUN-h's environment.json before the gate evaluates. Two lines decide which
    of the two branches in PF-26 the amendment is actually in.
  baseline_comparison: >-
    Not applicable in the algorithmic sense and correctly not claimed. This
    amendment is a descriptive diagnostic control on a p=2437 toy instance; it
    asserts no algorithm, no complexity exponent, and no comparison against
    Pollard-rho, BSGS, or any specialized isogeny baseline. OBJECTIVE_BOUNDARY
    disclaims all of that explicitly and the disclaimer is stronger in round 3
    than in round 2. The only comparison-of-alternatives in the document is the
    sweep-point choice, and after PF-17 it is a genuine Pareto argument with
    both axes priced (115 vs 45 naturally completed, 36 vs 4 at delta_E >= 5,
    20 vs 0 at delta_E = 5, against 494.7 s vs 485.0 s) rather than a claimed
    necessity. That part of the draft is now correct. What is NOT priced on
    every axis is the comparison of this amendment against doing nothing: with
    PF-25 applied, the marginal empirical yield is one integer, and the draft
    does not say so in those terms.
  heuristic_challenges:
    - >-
      The load-adjusted predicted count applies an n = 8 median ratio,
      measured on the extreme fastest tail of the population (delta_E in {2,3}
      only, by the draft's own selection-bias disclosure), uniformly to a
      194-vertex distribution. The draft discloses this and downgrades the
      clause accordingly, which is the right response. But the same
      extremity-selection objection applies with more force to F_cal, which is
      the MINIMUM of that same eight and gates the whole run -- and there the
      draft does not disclose it. F_cal is defended as "the measured analogue
      of exactly the same quantity" as A, which is true and is the right
      defence for a floor; it is worth saying that it is a floor statistic and
      therefore says nothing about the body of the distribution the b = 1.45 s
      arm actually depends on.
    - >-
      The prediction curve's transfer assumption -- that RUN-h's per-vertex
      timings predict RUN-k's -- is the amendment's load-bearing heuristic and
      is nowhere numbered or stated as one. It is discussed under two caveats
      (contention, cross-hardware) but never given the status of an explicit
      assumption with a falsification condition. PF-26 and PF-27 are both
      failures of exactly that unstated heuristic. Numbering it, stating it,
      and pairing it with the G-0c hardware check and the overshoot
      measurement would bring this amendment into line with the explicit-
      conditional-rigor discipline the program's own target profile requires.
  cost_model_challenges:
    - >-
      Every budget term reproduces exactly (494.7 / 213.4 / 281.3 / 120.0 /
      16.0 / 632.7 / 657.19 / 1.5805 / 1.5216 / 0.1825 CPU-h / 55.3%), and the
      ~2 s non-search allowance is independently supported by RUN-h's own
      0.664 s of non-search wall time. No objection to the arithmetic.
    - >-
      The worst case is correctly sized on zero natural completions and relies
      on the expected early completions for nothing, which is the right
      discipline for a run whose object of study is exactly that expectation.
    - >-
      One incoherence worth naming: the budget block treats the final-pop
      overshoot as a real, measured, quantified cost (+4.2%, applied to
      630.7 s), while the natural-completion semantics block denies that the
      same mechanism can push a vertex past its budget without timing out.
      The document cannot have it both ways; PF-27 is that contradiction.
  reduction_and_scope_challenges:
    - >-
      No reduction is cited and none is needed. Scope discipline is clean and
      is stricter in round 3 than round 2: p=2437 only, toy scale stated, no
      transfer to cryptographic scale, no PERSISTS/WEAKENS label, no gating of
      any decision rule, the RT-BATCH-011 question explicitly disclaimed, and
      P-4 forbidding the one conclusion a reader would most want to draw. I
      found no scope inflation anywhere.
    - >-
      The narrowing is now severe enough that it becomes a different kind of
      problem: an amendment that has correctly disclaimed everything is at
      risk of being cited later for the one thing it did not disclaim. The
      pre-committed strength_note clause is the right instrument for that, and
      it should carry PF-27's two-sided correction so the 115 figure is never
      quoted as a bound.
  proof_architecture_challenges:
    - >-
      Compositional-invariant attack, and it is where PF-27 came from: the
      invariant "timed_out == False implies the archived total time was below
      the budget" was checked on the SOURCE half and then assumed for the
      TOTAL. Deleting that assumption and re-deriving the target half from
      compute_delta_e.py:189-192 breaks it at the first step. The strong
      invariant the amendment actually needs is
      "max(2*t_source, t_total) <= b + (one pop)", which does not imply the
      clean upper bound the document freezes.
    - >-
      Quantifier-order attack on the gate: the thresholds are chosen before
      the run (correct) but the machine they are calibrated against is chosen
      -- implicitly, by wherever the Executor happens to run -- after the
      thresholds were frozen. That is PF-26. The repair is to make the machine
      a checked precondition rather than a free variable.
    - >-
      Observation-fiber attack on the equality cross-check: holding
      "naturally-completed value equals archived value" fixed and varying the
      underlying run cannot separate any two hypotheses, because PF-25 shows
      the fiber is a single point a priori. The draft reaches this conclusion
      itself and states it. That is the right call and I confirm it.
  narrowest_supported_statement: >-
    If frozen as drafted and executed past the gate, the results would support
    only: at p=2437 alone, at per-vertex budgets 1.10 s and 1.45 s under
    BASE_SEED 20260811 and the frozen (L, X=23, B_SMOOTH=23) search class, on
    whatever machine the Executor happened to use, the measured count of
    non-F_p-rational vertices whose two_sided_search returned timed_out False
    stood in the reported relation to a reference count of 0 and 115 derived
    from RUN-SSIQ-a85692-h's archived totals -- a reference that is neither an
    upper nor a lower bound, being reduced by the unmeasured 0.725 s
    source-side cap and increased by the unmeasured final-pop overshoot -- and
    that on all k of those vertices the returned delta_E equalled
    RUN-SSIQ-a85692-b's archived value, k being the reported
    n_naturally_completed, under the recorded environment figures and the
    load_confounded stamp. It would NOT support: any independent confirmation
    of the equality proposition (already n = 194 with zero exceptions, and
    determinate a priori under PF-25, so a k/k match is a passed control and
    not a finding); any statement about whether delta_E >= 5 convergence
    begins at the floor (P-4); any inference from the speed-selected
    naturally-completed histogram to the delta_E population; any transfer of
    RUN-h's timing distribution to a different machine, which the committed
    environment.json files show is the live question and not a remote one; or
    anything whatever about the other three primes, about H-SSIQ-36e970's
    real-arm prediction, or about any cryptographic scale.
  next_concrete_action: >-
    Coordinator: apply PF-26 and PF-27 in one textual pass -- add gate branch
    G-0c (read RUN-k's platform and CPU count, compare against RUN-h's
    committed environment.json, DEFER on mismatch), replace hw.ncpu with
    os.cpu_count() + os.getloadavg(), record RUN-h's actual platform beside
    the archived figures, rename the SAME-HARDWARE caveat, withdraw the
    "PERMISSIVE direction" sentence and relabel 115 as a two-sided reference
    count, add P-3d ordered first among the over-bound branches, and require
    the b = 1.10 s arm's overshoot distribution to be reported -- then fold in
    PF-28, PF-29 and PF-30, all of which are single-clause text edits. Zero
    new compute; no budget amendment; no design change; SWEEP_BUDGETS stays
    [1.1, 1.45]. Given that this is the third round and that every item in
    rounds 1 and 2 now verifies clean, a fourth full red-team round is
    disproportionate: a Coordinator self-verification note in the style of
    COORD-VERIFY-PREFREEZE-v11.md, recording RUN-h's environment.json figures
    verbatim and the recomputed over-bound band, is the right closing step,
    then freeze. Before dispatching the Executor, read the load on the machine
    that will ACTUALLY run it -- not the review host -- because that is the
    distinction PF-26 exists to force.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no module from this lineage's
    implementation directory executed as an experiment -- this is a
    specification and real-code trace against a draft with no implementation
    file yet (confirmed: no *v11* file under
    experiments/EXP-SSIQ-a85692/implementation/), not an execution audit.
    Non-durable, read-only local computations run against the committed tree
    at HEAD 5d6caed43: (a) full independent recomputation over
    RUN-SSIQ-a85692-h's 194 per_vertex_records under R-1..R-4 -- census,
    full value histogram, delta_E>=5 population, below-budget counts with
    >=5 sub-histograms and {2,3,4} splits at 1.10/1.20/1.30/1.40/1.45/1.70,
    extrema, min over delta_E>=5, and the ten smallest by coordinate to full
    float precision; (b) the CDF of archived wall_seconds in [1.45, 1.50) and
    at 1.45+eps for eps in {5, 7.2, 11, 20.3, 25, 60.9} ms, and the same at
    1.40, for PF-27; (c) execution of
    delta_e_independent_rng_probe_v8.derive_per_vertex_seed(20260811, v) for
    all 194 vertices, compared against the archived seed_used field (194/194
    match); (d) direct source read of delta_e_truncation_probe_v9.py in full
    and compute_delta_e.py 100-210, with every line citation in the draft
    verified; (e) direct read of environment.json for all ten runs -a..-j and
    of RUN-h's manifest.yaml, execution_report.yaml and raw-result.json for
    load and hardware figures; (f) exact-rational verification of
    1.15 * 1.149932861328125 and the corresponding IEEE-754 doubles;
    (g) the G-2b ratio-to-predicted-count correspondence over median ratios
    1.00-1.30; (h) independent re-derivation of every budget term for both the
    round-2 and round-3 sweep-point lists; (i) uname, sysctl -n hw.ncpu (14),
    uptime (36.09/56.77/63.22, and 75.85/89.14/73.54 earlier); (j) git
    rev-parse/log/status to confirm the reviewed commit is HEAD, is this
    file's most recent touching commit, and the tree is clean. No file was
    written or edited by any of these computations other than this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task wrote only
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11-round3.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v11.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```

---

## Overall verdict

**DO-NOT-FREEZE.**

Not because the round-3 revision is weak — it is the strongest draft this
lineage has produced, and every item in the scope it was given verifies
clean. PF-17's repair reproduces figure for figure on a fourth independent
recomputation. PF-18 is genuinely better than what it replaced and is correct
against the real function body, which I traced statement by statement rather
than trusting. The gate is well-defined, correctly ordered, non-bypassable,
and G-2b is a real tightening rather than decoration. The budget is exact.
PF-19, PF-20, PF-21, PF-22, PF-24 and PF-25 are all correctly applied, and
PF-25's reclassification is right — the draft argued itself out of its own
headline and that is the behaviour the process is for.

It does not freeze because two premises underneath all of that were never
checked, and both are checkable for free. The amendment compares measured
times against archived times without ever verifying they come from comparable
machines, while the committed `environment.json` files say they probably do
not (PF-26). And it freezes a number as a one-sided upper bound on an argument
whose sign is inverted, at a budget its own PF-17 repair moved into the
densest part of the distribution, where the instrument's own documented
overshoot covers 18 to 71 vertices (PF-27). Both are exactly the defect class
PF-17 identified — an assertion in frozen text that nobody tested — and both
are repaired by text plus a handful of lines, with no design change, no new
compute, and no budget amendment.

Third rounds should not be manufactured, and I did not manufacture this one:
neither finding appears in the six items the draft nominated for itself, both
were found by ignoring that nomination, and both are demonstrated against
committed artifacts and the real frozen code rather than argued. Equally,
neither is a reason to redesign anything. `SWEEP_BUDGETS = [1.1, 1.45]` is the
right choice, the calibration and gate architecture is sound, and I would
freeze this document the moment PF-26 and PF-27 are written in.

**Disclosed accepted limitations** — real, and correctly disclosed by the
draft, not grounds to withhold a freeze once the two blocking items are fixed:
the naturally-completed subset is speed-selected and biased toward small
`delta_E` at every arm; 36 of an 80-vertex `delta_E >= 5` population is a
partial view and 1.45 s is below the 1.6985 s archived maximum, so the slowest
vertices are unobservable; the equality half is a control whose expected
outcome is a null; the `b = 1.10 s` arm's result is pre-registered as exactly
0 and is not a new observation; CAL-2 does not close PF-12's sufficiency gap;
`F_cal` and the load-adjusted ratio are `n = 8` extremity-selected statistics;
a G-1 deferral discards the monotone-safe lower arm along with everything
else; and the whole result is a toy-scale, single-prime, descriptive
diagnostic that transfers to nothing.
