# RT-PREFREEZE-EXP-SSIQ-a85692-v10 — Round 1 pre-freeze Red Team review of
# the DRAFT amendment `specification_v10.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001
# BATCH-013, task `TASK-20260806-99bd03`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v10.yaml` at
`status: draft`, `pre_freeze_review.status: pending`, committed at `6edd3ce1`
(a Coordinator-committed snapshot of the draft, not a frozen spec) — a
three-point intermediate-budget truncation sweep (0.6s/0.8s/1.0s) amending
`specification_v9.yaml` (v9, frozen `d729af05328f7e40fe466f4e4d473298e246db8f`,
retained unedited), implementing RT-BATCH-012's own named "Required controls"
and "Counterexample or mutation" recommendation.** Per this task's operating
rules, only Coordinator-committed snapshots are treated as durable evidence;
this review is advisory pre-freeze input on a draft, and changes nothing
under `experiments/EXP-SSIQ-a85692/` or any other path outside this report.
**No implementation file for v10 exists yet** (confirmed:
`experiments/EXP-SSIQ-a85692/implementation/` has no `*v10*` file as of
`6edd3ce1`) — this review audits the plan an Executor would have to turn into
code, not code that already runs.

Read in full: `specification_v10.yaml` (277 lines); `specification_v9.yaml`
(498 lines, all PF-1 through PF-5 fix text and both freeze-round verdicts);
`RT-BATCH-012.md` (full, including its exact power bounds, conjugate-pair
trace, and "Required controls"/"Counterexample or mutation" sections this
amendment implements); `delta_e_truncation_probe_v9.py` (full, 665 lines, the
actual frozen v9 implementation, read directly rather than trusted from spec
prose); `delta_e_independent_rng_probe_v8.py` lines 145–176
(`derive_per_vertex_seed`, `verify_graph_identity`); `compute_delta_e.py`
lines 144–211 (`build_smooth_table`, `two_sided_search`);
`build_isogeny_graph.py` (`EXP-SSIQ-58b642/implementation/`) lines 63–125
(`Fp2Field` class, `frobenius`, `is_in_fp`); `trapping_diagnostic_v5.py`
lines 102–130 (`load_archived_prime_data`). Directly executed, not trusted
from prose (all reproducible against the committed tree):
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`'s full 194-entry
`per_vertex_records` (`wall_seconds` min/max independently recomputed);
`build_isogeny_graph.py`'s module-level namespace (confirmed no top-level
`frobenius` function exists, only `Fp2Field.frobenius`); a modular-arithmetic
check of self-conjugate-vertex impossibility over the 194-vertex
non-F_p-rational domain at p=2437.

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
    lineage (including RT-BATCH-012, whose own recommendation this amendment
    implements). Does not upgrade the campaign's evidence tier and does not
    itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**DO-NOT-FREEZE.** The core statistical/experimental design is sound and a
genuine improvement over v9 — the three budgets are correctly bounded below
the independently re-verified 1.14993s natural-completion floor (I
re-derived this directly from `RUN-SSIQ-a85692-h`'s own 194 `wall_seconds`
records: min `1.149932861328125`, matching the spec's cited figure to
displayed precision, with zero vertices below any of 0.6/0.8/1.0s), the
budget arithmetic (`194*2.4=465.6s` worst case, `1200/465.6≈2.58x` margin) is
independently re-verified correct, and the self-conjugate edge case the
conjugate-pair reporting logic implicitly assumes away is in fact
impossible at p=2437 (proven below, not merely assumed). But four defects,
all directly demonstrable against the committed spec text and the real
underlying code (not merely hypothesized), would let an Executor implement
this incorrectly or inefficiently:

1. **PF-1 [BLOCKING] — the draft directly contradicts itself on whether the
   graph is rebuilt/re-verified once or three times.** `amendment_scope`'s
   own numbered PROCEDURE list nests graph rebuild and identity
   re-verification as step (1) **inside** the "PER SWEEP POINT b in [0.6,
   0.8, 1.0]" loop ("... BEFORE any delta_E search begins for **that** sweep
   point"), while `inputs.truncation_sweep_search_v10` explicitly states "The
   graph is rebuilt ONCE and its identity re-verified ONCE at the start
   (**not once per sweep point**...)". These are not reconcilable readings
   of the same text — see §1.
2. **PF-2 [BLOCKING] — the write-order/failure-isolation discipline only
   covers Comparison 2, not PART A, not the new histogram/conjugate-pair
   code, and not the single combined artifact write, leaving the stated
   intent ("a failure at one budget must never affect the other two")
   unenforced by the specified mechanism.** See §2.
3. **PF-3 [BLOCKING] — `required_artifacts_note`'s central justification for
   writing a new module is factually wrong on direct code read.** v9's own
   `run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds)`
   already takes budget as an explicit function parameter and never
   references the module-level `PER_VERTEX_BUDGET_SECONDS` constant inside
   its body — it is **already** genuinely reusable across all three budgets,
   unchanged. See §3.
4. **PF-4 [BLOCKING] — `build_isogeny_graph.frobenius` is not a real,
   importable name.** `frobenius` is `Fp2Field.frobenius(self, x)`, an
   instance method reachable only via `graph["field"].frobenius(v)` (exactly
   how v9's own code and RT-BATCH-012's own trace use it); no module-level
   `frobenius` function exists in `build_isogeny_graph.py` (confirmed by
   direct namespace check). See §4.

Four further advisory findings (PF-5 through PF-8) tighten reuse-ambiguity
resolution, a reproducibility caveat, a counting-convention gap, and a
statistical-power framing gap for the new cross-sweep reporting; none blocks
freeze independently. All four are fixable in one textual pass with **zero**
new compute, exactly as v9's own PF-1 was.

---

## §1 — Graph rebuild/re-verify: once, or per sweep point? [task item 1 /
## item 7]

**A genuine, directly demonstrable internal contradiction, not a stylistic
ambiguity.** Quoting both passages exactly as committed:

`amendment_scope` (lines 55–60): *"PER SWEEP POINT b in [0.6, 0.8, 1.0]
(seconds): (1) rebuild the graph (IMPORTED UNCHANGED); re-run the two-part
graph-identity verification via
delta_e_independent_rng_probe_v8.verify_graph_identity (GENUINELY IMPORTED,
UNCHANGED, exactly as v9 did) BEFORE any delta_E search begins for **that
sweep point**; ..."*

`inputs.truncation_sweep_search_v10` (lines 156–162): *"The graph is rebuilt
**ONCE** and its identity re-verified **ONCE** at the start (**not once per
sweep point** -- IDENTICAL graph object reused across all three sweep
points, since it does not depend on the budget and rebuilding it three times
would add cost with no diagnostic value); the identity re-verification
result is reported **once** and applies to all three sweep points."*

The first passage is the authoritative, numbered PROCEDURE description
(the section this campaign's own conventions treat as the binding contract
text, per v9's own `amendment_scope`/`inputs` split); the second directly
negates it. This is not merely a wording nit: it changes (a) how many times
`build_graph_for_prime`/`verify_graph_identity` actually run (1 vs. 3, a
~2–4s difference — negligible against the 1200s budget, so not a *safety*
issue), (b) the output schema — is `graph_identity_verification` a single
top-level field (as `inputs` implies) or nested once per sweep point (as
`amendment_scope`'s per-point framing implies)? — and (c), most importantly,
which of two different Executors following the two different passages in
good faith would produce **structurally different, mutually incompatible
`truncation_sweep_comparison.json` artifacts**, exactly the "Executor could
resolve wrong" risk this task asked me to hunt for. I have no basis to
prefer one interpretation as "what was meant"; both are stated as
requirements in the same frozen-to-be document.

The "ONCE" design (`inputs`) is the more defensible one on its own stated
grounds (the graph doesn't depend on budget, so rebuilding is pure overhead)
and is also the one the budget note's own arithmetic implicitly assumes
("Graph reconstruction runs three times... and is negligible" — wait, this
line in `amendment_scope`'s own BUDGET JUSTIFICATION paragraph says **three
times**, directly contradicting `inputs`' "ONCE" a *third* time in the same
document). Quoting exactly: *"Graph reconstruction runs three times (once
per sweep point, ~1-2s each per every prior amendment's own measured
figures) and is negligible against this bound."* So the document asserts
"three times" in two places (`amendment_scope`'s PROCEDURE list and its own
BUDGET JUSTIFICATION paragraph) and "ONCE" in a third (`inputs`). This is a
real defect, not a single slip.

**Required fix:** pick one design (I recommend "ONCE," per `inputs`' own
correct efficiency argument) and make `amendment_scope`'s PROCEDURE list and
its BUDGET JUSTIFICATION paragraph consistent with it — moving graph
rebuild/re-verify outside the "PER SWEEP POINT" loop, and stating explicitly
whether `graph_identity_verification` is a single top-level field or
repeated per sweep point in the required artifact schema.

## §2 — Crash paths across three independent sweep points [task item 1]

**The stated intent is broader than the specified mechanism, and the gap is
concretely worse here than in v9 because v10 introduces new, previously
unexercised code and combines three formerly-independent runs into one
artifact-writing lifecycle.**

`amendment_scope` point (8) states: *"each sweep point's own PART A result
and Comparison 1 result MUST be captured before that sweep point's
Comparison 2 is attempted, and each sweep point's Comparison 2 code MUST be
wrapped so any exception becomes a recorded `comparison_2_error` field for
THAT sweep point only... the three sweep points are fully independent in
both computation and failure isolation, so a failure at one budget must
never affect the other two."* This is **explicitly** "IDENTICAL to v9's own
PF-5 fix" — i.e., it only extends v9's Comparison-2-only exception wrapping,
sweep-point by sweep-point. I read v9's actual `main()`
(`delta_e_truncation_probe_v9.py:411–660`) directly: PART A itself (the
`run_truncation_probe_v9` call) and the new value would-be
histogram/conjugate-pair logic (which does not exist in v9 at all — it is
genuinely new to v10) are **not** wrapped in any try/except anywhere in this
lineage's precedent. If PART A raises an unanticipated exception for one
budget (plausible: different budgets exercise different timing-dependent
code paths inside `build_smooth_table`'s soft-cap check, an untested regime
for this specific per-vertex-budget/vertex-count combination), or if the
**new** histogram/conjugate-pair code (never previously exercised in this
lineage, so has no track record the way Comparisons 1/2 do) raises anywhere,
nothing in the specified failure-isolation discipline protects an
**already-successfully-completed earlier sweep point's** results from being
discarded.

This is concretely reinforced, not merely hypothesized, by the
`required_artifacts` list itself: it names exactly **one** combined output,
`runs/RUN-SSIQ-a85692-j/truncation_sweep_comparison.json` — no
per-sweep-point artifact file, no incremental-write requirement. An
Executor modeling this on v9's own `main()` (confirmed: v9 accumulates
everything into local variables and writes `comp_path`/`raw_result_path`
in single `json.dump` calls **once, at the very end**, after every prior
step) would naturally accumulate all three sweep points' results into one
in-memory structure and write it once at the end — precisely the shape that
lets sweep point 3's failure (in *either* PART A or the new
histogram/conjugate-pair code, neither of which is protected) silently
erase sweep points 1 and 2's already-valid, real-compute-backed results, in
direct contradiction of the design's own stated intent. This would be
**worse** than the outcome v9's own PF-5 flagged (dormant there, since v9
had only one sweep point and nothing to lose by a downstream crash beyond
what a single run always risks): here it converts a partial success (2 of 3
budgets' worth of real search) into a total loss.

**Required fix:** wrap **each** sweep point's **entire** per-budget bundle
(graph-identity dependency permitting, PART A + Comparison 1 + Comparison 2
+ the new histogram/conjugate-pair analysis) in its own outer try/except at
the sweep-loop level, catching *any* exception and recording a
`sweep_point_error` field for that budget alone; accumulate each sweep
point's result (success or a documented `sweep_point_error`) into a list
incrementally, and make the final artifact write unconditional on how many
of the three sweep points actually succeeded — not merely require that
Comparison 2 within an already-successful sweep point fail gracefully.

**Cheapest discriminating control:** before dispatch, have the Executor
inject a deliberate fault (e.g., a forced `raise` inside the histogram
computation for the b=0.8 sweep point) after b=0.6 completes, and confirm
the written `truncation_sweep_comparison.json` still contains b=0.6's full
result and a `sweep_point_error` for b=0.8 — the same kind of directly-
reproduced check RT-BATCH-012's own Front 5 used to confirm v9's PF-5 was
genuinely, not just claimedly, implemented.

## §3 — Is the new `run_truncation_probe_for_budget` module genuinely
## necessary? [task items 5, 7 — required_artifacts_note accuracy]

**No — the stated justification is false on direct code read, and the
"necessary" new module duplicates a function that is already reusable
unchanged.** `required_artifacts_note` states: *"the ONE genuine code-level
generalization this amendment makes relative to v9: v9's own
`PER_VERTEX_BUDGET_SECONDS` was a fixed module-level constant, not reusable
across multiple budget values in one run without either three separate
frozen amendments or this generalization -- disclosed here explicitly, not
silently introduced."*

I read `delta_e_truncation_probe_v9.py:147` directly:

```python
def run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds):
    ...
    r = compute_delta_e.two_sided_search(
        field, v, target, rng_v, q,
        L=compute_delta_e.L_PRIMES, X=compute_delta_e.X_LIST_BOUND,
        time_budget_seconds=per_vertex_budget_seconds)
```

`per_vertex_budget_seconds` is the function's **third parameter**, used
directly at the only call site inside the function body. The module-level
constant `PER_VERTEX_BUDGET_SECONDS = 0.5` (line 125) is referenced **only**
at the `main()` call site (`run_truncation_probe_v9(g, BASE_SEED,
PER_VERTEX_BUDGET_SECONDS)`), never inside the function itself. This means
`run_truncation_probe_v9` is **already** a genuinely budget-parameterized,
reusable function — it can be genuinely imported and called three times
unchanged (`v9probe.run_truncation_probe_v9(g, BASE_SEED, b)` for `b` in
`[0.6, 0.8, 1.0]`), with zero new duplicate code for the per-vertex search
loop. `required_artifacts_note`'s claim that this "was not reusable... 
without either three separate frozen amendments or this generalization" is
incorrect, and the premise motivating a brand-new module
(`delta_e_truncation_sweep_v10.py`) with a new, parallel function
(`run_truncation_probe_for_budget`) does not hold.

This matters beyond bookkeeping precision, per this campaign's own GD-9/
GD-10 standing repair that `required_artifacts_note` explicitly invokes as
its own governing standard ("EXPLICIT, CODE-VERIFIED FUNCTION-LEVEL DIFF,
per GD-9/GD-10's standing repair") — a diff note claiming to be
code-verified is not, on direct check, here. It also creates unnecessary
duplicate-code drift risk: a hand-written "generalized" reimplementation of
`run_truncation_probe_v9`'s loop is one more place the `IDENTICAL BASE_SEED`
/ fresh-`random.Random`-per-vertex / F_p-rational-unconditional-wiring
guarantees this spec repeatedly cites as load-bearing could subtly diverge
from the already-audited original, for no behavioral benefit.

**Required fix:** either (a) genuinely import and reuse `run_truncation_probe_v9`
directly for the per-vertex search loop across all three sweep points
(recommended — removes duplicate-code risk and shrinks the new-code surface
§2's failure-isolation fix needs to cover), layering the genuinely new
histogram/conjugate-pair/cross-sweep-comparison logic on top of its
existing return value; or (b) if a new function is retained for some other,
real reason (e.g., restructuring the return shape for §2's incremental-write
fix), state that actual reason in `required_artifacts_note` instead of the
disproven "budget wasn't parameterized" justification.

## §4 — `build_isogeny_graph.frobenius`: is it actually importable as
## stated? [task item 5]

**No.** `required_artifacts_note` lists, among its "GENUINELY IMPORTS,
UNCHANGED" targets: *"build_isogeny_graph.frobenius, build_isogeny_graph.
degree_sequence_check (the latter via verify_graph_identity's own
import)"* — phrasing that treats `frobenius` as a standalone, directly
importable module-level name, parallel to `degree_sequence_check`. I
checked `build_isogeny_graph.py`'s module namespace directly:

```
$ grep -n "^def frobenius\|^frobenius\s*=" experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py
(no matches)
$ grep -n "def frobenius" experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py
119:    def frobenius(self, x):
```

`frobenius` exists **only** as `Fp2Field.frobenius(self, x)`, an instance
method on the field class, reachable only as `graph["field"].frobenius(v)`
— exactly the form v9's own code already uses (`delta_e_truncation_probe_v9.py:177`,
`target = field.frobenius(v)`) and exactly the form RT-BATCH-012's own trace
used when it actually computed conjugate pairs. There is no module-level
`build_isogeny_graph.frobenius` callable an Executor could literally
`import`. An Executor following `required_artifacts_note`'s literal wording
(e.g., `from build_isogeny_graph import frobenius`, or `big.frobenius(v)`
after `import build_isogeny_graph as big`) would hit an immediate
`ImportError`/`AttributeError` — a live, directly-reproducible defect of the
same shape as v9's own PF-1 (a citation naming something that does not
exist in the claimed form), just smaller in blast radius since it would
only affect the new conjugate-pair reporting step, not the whole run.

**Required fix:** correct both `amendment_scope`'s and `required_artifacts_note`'s
phrasing to `graph["field"].frobenius` (`Fp2Field.frobenius` instance
method, reached via the already-imported graph object, not a standalone
module import).

## §5 — Value-histogram/conjugate-pair well-definedness [task item 4]

**Verified sound — no defect, but worth documenting the proof rather than
assuming it.** Self-conjugacy (`frobenius(v) == v`) requires `x[1] ==
(-x[1]) % p`, i.e. `2*x[1] ≡ 0 (mod p)`. Since `p = 2437` is an odd prime,
this forces `x[1] ≡ 0 (mod p)` — but `is_in_fp(x)` is defined as exactly
`x[1] % p == 0` (`build_isogeny_graph.py:94-95`), so any vertex with
`x[1] ≡ 0` **is** F_p-rational and is, by construction, excluded from the
194-vertex non-F_p-rational domain the histogram/conjugate-pair reporting
operates over. So no self-conjugate vertex can appear in the population
this reporting logic examines, and `n_resolved_without_a_paired_partner_in_resolved_set`
is well-defined with no silent edge case. `frobenius` is also confirmed (by
the same argument, applied to `frobenius(x)[1] = (-x[1])%p`) to map the
non-F_p-rational domain to itself, consistent with RT-BATCH-012's own
empirical trace of 4 exact pairs among 8 resolved vertices in `RUN-SSIQ-a85692-i`.
No fix needed here; flagged only because the task specifically asked and
because "silently assumed correct" is exactly the failure mode this
lineage's own history (PF-1 in both v8 and v9) has repeatedly punished.

## §6 — Reuse-ambiguity that is resolvable now, not genuinely open [task
## item 5/6, advisory]

`inputs.truncation_sweep_search_v10` leaves `parse_v8_new_delta_map`'s reuse
as a disjunction: *"either genuinely imported from
delta_e_truncation_probe_v9.py if its function signature permits reuse
without modification, or restated as an authorized disclosed duplicate...
the Executor's own execution_report.yaml must state which approach was
taken and why."* I checked `parse_v8_new_delta_map(path)`
(`delta_e_truncation_probe_v9.py:302`) directly: its signature takes only a
`path` argument and its body references no module-level constant
(`PER_VERTEX_BUDGET_SECONDS`, `BASE_SEED`, etc.) at all — it is
unconditionally, genuinely reusable, importable as-is, and callable three
times with the identical fixed `path` argument (Comparison 2's source file
does not change per sweep point). This is not a live ambiguity; it can be
pre-resolved now. **PF-5 [ADVISORY]:** recommend the Coordinator instruct
the Executor to genuinely import this function (removing one more
unnecessary potential duplicate, and one more disjunctive judgment call an
Executor could resolve toward unnecessary duplication, compounding §3's
concern) rather than leave it open.

## §7 — Cross-run hardware-reproducibility caveat not re-inherited
## [advisory]

The core premise "every one of the three budgets stays below the observed
1.14993s floor, so every vertex is guaranteed truncated at every sweep
point" is independently re-verified true against `RUN-SSIQ-a85692-h`'s
actual committed data (min `wall_seconds` = `1.149932861328125` across all
194 records; zero records below 0.6, 0.8, or 1.0s). But this guarantee rests
on comparing **this** run's (RUN-SSIQ-a85692-j's) wall-clock behavior
against a **different** run's (RUN-SSIQ-a85692-h's) measured floor, produced
on whatever hardware executed that run. v9's own PF-3 finding explicitly
disclosed that exact per-vertex wall-clock cutoff behavior is not
bit-for-bit reproducible across hardware. **PF-6 [ADVISORY]:** v10 should
explicitly restate/inherit this caveat — on sufficiently different hardware,
even the direction of the "every vertex is truncated at b=1.0" guarantee
could in principle weaken (though this is very unlikely given the ~13-70%
margin between 1.0s and the observed 1.15-1.70s range) — rather than
silently treating RUN-SSIQ-a85692-h's specific hardware-measured floor as a
portable constant.

## §8 — Budget arithmetic [task item 3]

**Independently re-verified, all correct.** `0.6+0.8+1.0 = 2.4`; `194*2.4 =
465.6`; `194*1.0 = 194.0` (b=1.0 alone); `1200/465.6 = 2.5773...` ≈ "~2.58x"
as stated. `total_cpu_hours: 0.4` against `wall_clock_seconds_per_run: 1200`
(`1200/3600 = 0.333`) is consistent with a generous, not tight, single-
threaded rounding, matching the identical pattern in v9's own budget note
(`600s`/`0.2` CPU-hours, `600/3600=0.167`). No objection.

## §9 — Scope discipline [task item 6]

**Clean.** Grepped the full spec for `PERSISTS`, `WEAKENS`, `lever L4`, and
`H-SSIQ-36e970`: the hypothesis ID appears only as standard experiment
metadata and in `OBJECTIVE_BOUNDARY`'s own explicit disclaimer ("does not
test H-SSIQ-36e970's real-arm prediction... does not produce a
PERSISTS/WEAKENS label"). No affected/safe cryptographic scheme list
anywhere. `OBJECTIVE_BOUNDARY` correctly and explicitly states that even
b=1.0 remains below the 1.14993s floor and so "still forces truncation on
every vertex" — correctly declining to let this amendment alone answer
RT-BATCH-011's original boundary question, framing it instead, correctly,
as a test of whether the **selection-effect artifact** RT-BATCH-012 traced
weakens. No scope inflation found.

## §10 — Statistical-power framing for the new cross-sweep reporting
## [advisory, item 4]

RT-BATCH-012's own central finding about v9's `0/8` result was not "the
sample was too small" in a generic sense but that a specific, mechanism-
traced selection effect (extreme-value, correlated-pair bias) made the
result close to uninformative regardless of nominal sample size. The
REQUIRED CROSS-SWEEP REPORTING text requires reporting `n_resolved` per
sweep point (via REQUIRED REPORTING item (5), inherited) and the full value
histogram, but does **not** require framing any observed "shift toward the
true population mix" with the same statistical-power discipline
RT-BATCH-012 applied (Clopper-Pearson bounds, conjugate-pair
double-counting correction). Given b=0.6 is likely to resolve a similarly
small population as v9's 0.5s point (only modestly larger), a future
citation of "the histogram shifted at b=0.6/0.8" without that context risks
exactly the interpretive overreach RT-BATCH-012 corrected for v9. **PF-7
[ADVISORY]:** recommend adding one sentence to `OBJECTIVE_BOUNDARY` or the
REQUIRED CROSS-SWEEP REPORTING text pre-committing that any future citation
of a histogram shift report `n_resolved` and the conjugate-pair-corrected
effective sample size alongside it, not a bare percentage comparison.

## §11 — Edge case: n_resolved = 0 (or very small) at a sweep point
## [advisory, item 4/7]

Unlike v9 (a single point whose actual `n_resolved=8` outcome was known
*after* the run, when RT-BATCH-012 reviewed it), v10 is being drafted
*before* any of the three outcomes are known. If `n_resolved = 0` at b=0.6
(plausible, since 0.6 is only modestly above v9's 0.5s, which produced 8),
the histogram/conjugate-pair reporting logic must produce a well-defined
empty result (empty histogram dict, `n_conjugate_pairs_among_resolved = 0`)
rather than divide by `n_resolved` or otherwise assume a non-empty resolved
set. **PF-8 [ADVISORY]:** recommend the Coordinator require the Executor's
`execution_report.yaml` explicitly confirm this guard was exercised or
found unnecessary for whatever `n_resolved` values actually occur, matching
this lineage's own "trace it, don't trust it" discipline rather than
assuming it away.

## §12 — RNG identity across sweep points [task item 2]

**Sound, on direct trace, consistent with v9's own round-1-verified
argument.** `derive_per_vertex_seed(base_seed, vertex)`
(`delta_e_independent_rng_probe_v8.py:151-154`) is a pure function of
`(base_seed, vertex)` alone — confirmed by direct read, no reference to
budget anywhere. `two_sided_search` reuses the **same** `rng` object across
its own source- and target-table builds *within* one call (existing,
unchanged v8/v9 behavior, not new to v10), but v9's own
`run_truncation_probe_v9` constructs a **fresh** `random.Random(seed_v)`
object per vertex, inline, inside its per-vertex loop (line 176:
`rng_v = random.Random(seed_v)`) — never shared or advanced across
vertices, and (since it is a fresh local object constructed on every call)
never carrying state across separate invocations of the function either.
Given `amendment_scope`'s explicit requirement that v10 "construct a FRESH
random.Random instance" per vertex **per sweep point**, and given (per §3)
the cleanest implementation is direct reuse of `run_truncation_probe_v9`
itself (which already does this correctly), there is no live RNG-state-
leakage risk **provided** §3's fix is applied — reusing the already-audited
function rather than a hand-written duplicate removes any risk that a
"generalized" reimplementation accidentally hoists `rng_v`'s construction
out of the per-vertex loop. No objection to the design; recommend the
Executor's `execution_report.yaml` explicitly confirm fresh instantiation
was preserved (cheap, and matches this campaign's own "verify the fix, not
the prose" precedent).

---

## Objections

- **OBJ-1 [PF-1, BLOCKING]**: the spec directly contradicts itself on
  whether the graph is rebuilt/re-verified once (`inputs`, stated twice
  including "not once per sweep point") or three times (`amendment_scope`'s
  numbered PROCEDURE list, and its own BUDGET JUSTIFICATION paragraph's
  "Graph reconstruction runs three times"). Two different good-faith
  Executors could produce structurally incompatible artifacts.
- **OBJ-2 [PF-2, BLOCKING]**: the write-order/failure-isolation discipline
  is stated to cover Comparison 2 only, per sweep point (mirroring v9's own
  PF-5 scope exactly), but the closing intent clause ("a failure at one
  budget must never affect the other two") is broader than that mechanism.
  PART A itself, and the genuinely new histogram/conjugate-pair reporting
  code (no precedent in this lineage), are unprotected; the single combined
  `required_artifacts` entry (no per-sweep-point file) implies a
  write-once-at-the-end architecture matching v9's own `main()` precedent,
  under which an uncaught exception in sweep point 3 would discard sweep
  points 1 and 2's already-valid results — a worse outcome than any single
  prior amendment's failure mode, since three formerly-independent runs are
  now one artifact-writing lifecycle.
- **OBJ-3 [PF-3, BLOCKING]**: `required_artifacts_note`'s stated
  justification for a new module — that v9's `PER_VERTEX_BUDGET_SECONDS`
  "was a fixed module-level constant, not reusable... without... this
  generalization" — is false on direct code read. `run_truncation_probe_v9`
  already takes `per_vertex_budget_seconds` as its third parameter and
  never references the module constant internally; it is already genuinely
  reusable, unchanged, across all three budgets. `required_artifacts_note`
  claims to be "CODE-VERIFIED" per this campaign's own GD-9/GD-10 standard
  and is not, on this point.
- **OBJ-4 [PF-4, BLOCKING]**: `build_isogeny_graph.frobenius` is cited as a
  "GENUINELY IMPORTED, UNCHANGED" module-level name in both
  `amendment_scope` and `required_artifacts_note`; no such name exists.
  `frobenius` is `Fp2Field.frobenius`, an instance method reachable only via
  `graph["field"].frobenius(v)`. A literal implementation of the cited
  import raises `ImportError`/`AttributeError`.
- **OBJ-5 [PF-5, advisory]**: the disjunctive `parse_v8_new_delta_map` reuse
  plan is resolvable now, not a genuinely open judgment call — direct code
  read confirms it takes only a `path` argument with zero budget-dependent
  state, so it is unconditionally, genuinely importable.
- **OBJ-6 [PF-6, advisory]**: v9's own PF-3 cross-hardware wall-clock
  reproducibility caveat is not explicitly re-inherited, even though the
  entire "every vertex guaranteed truncated at every sweep point" property
  rests on comparing this run's wall-clock behavior against a different
  run's (`RUN-SSIQ-a85692-h`'s) hardware-measured floor.
- **OBJ-7 [PF-7, advisory]**: no requirement that a future citation of a
  cross-sweep histogram shift report `n_resolved`/conjugate-pair-corrected
  sample size alongside it, risking the same interpretive overreach
  RT-BATCH-012 corrected for v9's `0/8`.
- **OBJ-8 [PF-8, advisory]**: no explicit requirement that the histogram/
  conjugate-pair reporting logic be confirmed robust to `n_resolved = 0` (or
  very small `n_resolved`) at a sweep point, an outcome not yet known and
  plausible at b=0.6.

## Required controls

- **[PF-1, BLOCKING]**: resolve the graph-rebuild-count contradiction; make
  `amendment_scope`'s PROCEDURE list and BUDGET JUSTIFICATION paragraph
  consistent with `inputs`' "ONCE" design (recommended, on efficiency
  grounds already stated correctly in `inputs`), and state explicitly
  whether `graph_identity_verification` is a single top-level artifact field
  or repeated per sweep point.
- **[PF-2, BLOCKING]**: require each sweep point's entire per-budget bundle
  (not just Comparison 2) be wrapped in its own exception handler recording
  a `sweep_point_error` field, with results accumulated incrementally so a
  later sweep point's failure cannot discard an earlier one's already-valid
  results; require this be independently verified (not merely asserted) via
  a deliberate injected-fault test before or immediately after dispatch.
- **[PF-3, BLOCKING]**: either genuinely reuse `run_truncation_probe_v9`
  directly for the per-vertex search loop (recommended) or correct
  `required_artifacts_note`'s justification to state the real reason (if
  any) a new function is needed.
- **[PF-4, BLOCKING]**: correct the `frobenius` citation in both
  `amendment_scope` and `required_artifacts_note` to `graph["field"].frobenius`
  (an `Fp2Field` instance method reached via the graph object), not a
  standalone module import.
- **[PF-5, advisory]**: pre-resolve `parse_v8_new_delta_map` reuse toward
  genuine import (confirmed safe), removing an unnecessary disjunction.
- **[PF-6, advisory]**: restate v9's own PF-3 cross-hardware
  reproducibility caveat for v10's "every vertex guaranteed truncated"
  premise.
- **[PF-7, advisory]**: require `n_resolved` and conjugate-pair-corrected
  sample size accompany any future citation of a cross-sweep histogram
  shift.
- **[PF-8, advisory]**: require `execution_report.yaml` confirm the
  histogram/conjugate-pair logic's behavior on an `n_resolved = 0` (or
  small) sweep point, whether exercised in practice or not.
- None of PF-5 through PF-8 blocks freeze independently; PF-1 through PF-4
  do, collectively — each is a separate, directly-demonstrated defect, not
  redundant restatements of one issue.

## Counterexample or mutation

The cheapest concrete demonstration that PF-2 (§2) is a live, not merely
theoretical, risk: once implemented, have the Executor deliberately inject
a fault into the b=0.8 (middle) sweep point's histogram/conjugate-pair code
after b=0.6 has completed successfully, and confirm the written
`truncation_sweep_comparison.json` still contains b=0.6's full result plus a
recorded `sweep_point_error` for b=0.8 and b=1.0 does not silently also
disappear. If it does not — if the fault at b=0.8 discards b=0.6's
already-valid result too — that directly confirms PF-2 as specified (not
merely as feared) and blocks dispatch until fixed; if it correctly
preserves b=0.6, that is the cheapest possible positive confirmation the
Coordinator can request before spending the real 465.6s worst-case compute
this amendment is sized for.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale, single-prime search-procedure diagnostic work,
`H-SSIQ-36e970.asymptotic_claim: null` throughout, correctly inherited and
unchanged. The relevant baseline is this lineage's own code-verified-
crash-path and GD-9/GD-10 required-artifacts-accuracy standard, which
`required_artifacts_note` itself explicitly invokes as its governing
repair — PF-3 and PF-4 are exactly the shape that repair exists to catch (a
prose claim about what is genuinely importable/reusable that does not
survive direct code read), applied here to the two things genuinely new in
this amendment relative to v9 (the "generalized" search function and the
new conjugate-pair reporting), not to the parts (Comparisons 1/2's core
logic) v9's own two review rounds already audited and this amendment
correctly proposes to keep unchanged.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty — unchanged,
a search-procedure diagnostic, not a heuristic-conditional asymptotic
claim. `asymptotic_claim: null` throughout. No numbered heuristic is
implicated by this amendment.

## Cost model challenges

No asymptotic-cost claim anywhere. The safety-critical arithmetic (worst
case `194*(0.6+0.8+1.0)=465.6s`; `1200/465.6≈2.58x` margin) is independently
re-verified correct (§8). No `total expected cost = per-attempt cost ×
inverse success probability` computation is needed — this remains a
bounded, single-run, non-probabilistic-success diagnostic, consistent with
v8's and v9's own cost-model framing at this scale. The one cost-adjacent
gap is PF-1 (§1): whether graph reconstruction genuinely runs once or three
times changes the *measured* wall-clock this amendment reports by roughly
2-4 seconds, immaterial to the 1200s cap but material to whether the run's
own self-reported "graph reconstruction runs three times... negligible" text
is itself internally consistent.

## Reduction and scope challenges

No affected/safe cryptographic scheme list anywhere in this amendment;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated and not
exceeded. `OBJECTIVE_BOUNDARY` explicitly excludes `H-SSIQ-36e970`'s
real-arm prediction, any PERSISTS/WEAKENS label, and lever L4, and is
explicitly scoped to p=2437 alone — verified by direct grep of the full
spec text (§9), not merely trusted from prose. It also correctly and
explicitly declines to let this amendment alone answer RT-BATCH-011's
original truncation-boundary question, framing itself instead, correctly
narrowly, as a test of whether v9's own selection-effect artifact weakens.
No scope inflation found.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; a direct instrument-
level search-procedure diagnostic, not a proof-oriented proposal. Attacked
and held, unchanged from v8's and v9's own review history.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v10.yaml` as committed
at `6edd3ce1` (draft, `pre_freeze_review.status: pending`, no implementation
file yet written): the underlying experimental design — three intermediate
budgets, all independently re-verified strictly below the observed
1.14993s natural-completion floor, correctly isolating budget as the sole
manipulated variable via v8/v9's already-audited seed formula, correctly
scoped and honestly bounded on cost — is sound and directly responsive to
RT-BATCH-012's own named recommendation. It is **not** yet safe to freeze:
four directly-demonstrated defects (an internal self-contradiction on graph
rebuild count, PF-1; an incompletely-specified failure-isolation mechanism
whose gap is concretely worse than any prior amendment's because it spans
three formerly-independent runs writing to one combined artifact, PF-2; a
false "code-verified" justification for a new, unnecessary duplicate
function, PF-3; and a citation of a non-existent module-level import that
would crash on literal implementation, PF-4) must be corrected before an
Executor can implement this plan without a real risk of resolving at least
one of them incorrectly. All four fixes are textual, require zero new
compute, and do not touch the sound underlying design (the budget choice,
the seed-reuse argument, and the scope boundary all survive this review
unchanged).

## Next concrete action

Coordinator: apply PF-1 through PF-4 in one pass (resolve the graph-rebuild
contradiction toward the "ONCE" design; require per-sweep-point exception
wrapping around each budget's entire bundle, not just Comparison 2; correct
`required_artifacts_note`'s justification to reuse `run_truncation_probe_v9`
directly rather than duplicate it; correct the `frobenius` citation to
`graph["field"].frobenius`), apply PF-5 through PF-8 in the same pass
(pre-resolve the `parse_v8_new_delta_map` disjunction toward genuine
import; restate the PF-3-style hardware-reproducibility caveat; require
`n_resolved`/conjugate-pair-corrected sample size alongside any future
histogram-shift citation; require confirmation the reporting logic handles
`n_resolved=0`), then request a second, focused pre-freeze round scoped
specifically to (a) re-verifying the corrected text is now internally
consistent (no remaining "once" vs. "three times" contradiction), and (b)
confirming, once an implementation exists, that the deliberate-fault
failure-isolation test named in "Counterexample or mutation" above actually
passes — before freezing and dispatching the real 465.6s worst-case
compute this amendment is sized for.

## Overall verdict

**DO-NOT-FREEZE.** Four blocking findings, each directly demonstrated
against the committed spec text and the real underlying code (not merely
inferred from prose): a self-contradictory graph-rebuild-count requirement
(PF-1); a failure-isolation discipline that is narrower than its own stated
intent and concretely riskier than any prior single-point amendment because
it spans three formerly-independent runs sharing one artifact (PF-2); a
false "code-verified" justification for an unnecessary new duplicate
function (PF-3); and a citation of a non-existent module-level import that
would crash on literal implementation (PF-4). Four further advisory findings
(PF-5 through PF-8) should be applied in the same pass. The underlying
experimental design — the three budgets, the seed-reuse argument, the
budget arithmetic, the scope boundary — is sound and correctly implements
RT-BATCH-012's own recommendation; every required fix here is textual, with
zero new compute, so I expect this to be a short second round, proportionate
to v9's own two-round precedent for a smaller amendment.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v10
  task_id: TASK-20260806-99bd03
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v10.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: pending),
    committed at 6edd3ce1 -- a three-point intermediate-budget truncation
    sweep (0.6s/0.8s/1.0s, all strictly below the observed 1.14993s
    natural-completion floor) amending the frozen specification_v9.yaml
    (frozen d729af05328f7e40fe466f4e4d473298e246db8f), implementing
    RT-BATCH-012's own named "Required controls"/"Counterexample or
    mutation" recommendation: rerun v9's per-vertex-independent-RNG
    delta_E search design at p=2437 across three budgets in one run
    (RUN-SSIQ-a85692-j), testing whether the resolved-value distribution
    shifts toward the true population mix as budget grows, and whether
    v9's own Frobenius-conjugate-pairing degeneracy weakens. No
    implementation file exists yet as of the reviewed commit -- this
    review audits the plan, not executing code. Round 1 pre-freeze review,
    first round for this amendment.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: the spec directly contradicts itself on whether the graph is rebuilt/re-verified once or three times. amendment_scope's own numbered PROCEDURE list nests graph rebuild + identity re-verification as step (1) inside the 'PER SWEEP POINT b in [0.6, 0.8, 1.0]' loop, explicitly 'BEFORE any delta_E search begins for that sweep point,' and amendment_scope's own BUDGET JUSTIFICATION paragraph states 'Graph reconstruction runs three times (once per sweep point...)' -- while inputs.truncation_sweep_search_v10 explicitly states 'The graph is rebuilt ONCE and its identity re-verified ONCE at the start (not once per sweep point...)'. Two good-faith Executors following the two different passages would produce structurally incompatible artifacts (differing in whether graph_identity_verification is a single top-level field or repeated per sweep point, and in actual rebuild count)."
    - "OBJ-2 [PF-2, BLOCKING]: the write-order/failure-isolation discipline in amendment_scope point (8) is explicitly scoped to Comparison 2 only, per sweep point, mirroring v9's own PF-5 fix exactly -- but its own closing intent clause ('a failure at one budget must never affect the other two') is broader than that mechanism. Direct read of v9's actual main() (delta_e_truncation_probe_v9.py:411-660) confirms PART A itself is never wrapped in any try/except in this lineage's precedent, and the new histogram/conjugate-pair reporting code (genuinely new to v10, no precedent) is unaddressed by any exception-handling requirement. The required_artifacts list names exactly one combined output file (no per-sweep-point artifact), implying a write-once-at-the-end architecture matching v9's own main() precedent -- under which an uncaught exception anywhere in sweep point 3's processing would discard sweep points 1 and 2's already-valid, real-compute-backed results, contrary to the design's own stated intent, and a worse outcome than any prior single-point amendment's failure mode since three formerly-independent runs now share one artifact-writing lifecycle."
    - "OBJ-3 [PF-3, BLOCKING]: required_artifacts_note's stated justification for writing a new module (delta_e_truncation_sweep_v10.py with a new function run_truncation_probe_for_budget) is factually wrong on direct code read. It claims v9's PER_VERTEX_BUDGET_SECONDS 'was a fixed module-level constant, not reusable across multiple budget values in one run without either three separate frozen amendments or this generalization.' Direct read of delta_e_truncation_probe_v9.py:147 confirms run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds) already takes budget as an explicit third parameter, used directly at its only internal call site (line 181, time_budget_seconds=per_vertex_budget_seconds); the module-level PER_VERTEX_BUDGET_SECONDS constant is referenced only at the main() call site, never inside the function body. The function is already genuinely reusable, unchanged, across all three sweep-point budgets, with zero code change needed. required_artifacts_note explicitly claims to satisfy this campaign's own GD-9/GD-10 'CODE-VERIFIED FUNCTION-LEVEL DIFF' standard and does not, on this specific point."
    - "OBJ-4 [PF-4, BLOCKING]: 'build_isogeny_graph.frobenius, GENUINELY IMPORTED, UNCHANGED' is cited in both amendment_scope and required_artifacts_note as a directly-importable module-level name. Direct namespace check of build_isogeny_graph.py (experiments/EXP-SSIQ-58b642/implementation/) confirms no module-level frobenius function exists -- only Fp2Field.frobenius(self, x), an instance method reachable exclusively via graph['field'].frobenius(v), exactly the form v9's own code (delta_e_truncation_probe_v9.py:177, target = field.frobenius(v)) and RT-BATCH-012's own trace already used. A literal implementation of the cited import (e.g. from build_isogeny_graph import frobenius) raises ImportError/AttributeError immediately -- a live, directly-reproducible defect of the same shape as v9's own PF-1, scoped to the new conjugate-pair reporting step."
    - "OBJ-5 [PF-5, advisory]: the disjunctive parse_v8_new_delta_map reuse plan ('genuinely imported... if its function signature permits... or restated as an authorized disclosed duplicate') is resolvable now, not genuinely open. Direct code read confirms parse_v8_new_delta_map(path) takes only a path argument, references no budget-dependent module constant, and is unconditionally, genuinely importable and reusable across all three sweep points with an identical fixed path argument each call."
    - "OBJ-6 [PF-6, advisory]: v9's own PF-3 cross-hardware wall-clock reproducibility caveat is not explicitly re-inherited in v10, even though the core premise 'every budget stays below the observed 1.14993s floor, so every vertex is guaranteed truncated at every sweep point' -- independently re-verified true against RUN-SSIQ-a85692-h's actual committed 194 per_vertex_records (min wall_seconds=1.149932861328125, zero records below 0.6/0.8/1.0s) -- rests on comparing this run's wall-clock behavior against a different run's hardware-measured floor."
    - "OBJ-7 [PF-7, advisory]: no requirement that n_resolved and conjugate-pair-corrected effective sample size accompany any future citation of a cross-sweep histogram shift, risking the same interpretive overreach RT-BATCH-012 corrected for v9's 0/8 result (Clopper-Pearson bounds up to 31-53% true divergence rate at that sample size/structure) recurring at a similarly small n_resolved sweep point (plausibly b=0.6)."
    - "OBJ-8 [PF-8, advisory]: no explicit requirement that the new histogram/conjugate-pair reporting logic's behavior on an n_resolved=0 (or very small) sweep point be confirmed -- unlike v9, whose actual n_resolved=8 outcome was known before RT-BATCH-012 reviewed it, v10 is drafted before any of the three outcomes are known, and b=0.6 (only modestly above v9's 0.5s, which produced n_resolved=8) could plausibly resolve very few or zero vertices."
  required_controls:
    - "[PF-1, BLOCKING]: resolve the graph-rebuild-count self-contradiction; make amendment_scope's PROCEDURE list and BUDGET JUSTIFICATION paragraph consistent with inputs' 'rebuilt ONCE' design (recommended, on inputs' own correctly-stated efficiency grounds), and state explicitly whether graph_identity_verification is a single top-level artifact field or repeated per sweep point."
    - "[PF-2, BLOCKING]: require each sweep point's entire per-budget bundle (PART A + Comparison 1 + Comparison 2 + histogram/conjugate-pair analysis), not merely Comparison 2, be wrapped in its own exception handler recording a sweep_point_error field for that budget alone; require results be accumulated incrementally so a later sweep point's failure cannot discard an earlier one's already-valid results; require this be verified via a deliberate injected-fault test (see Counterexample or mutation) before treating the design as safe to dispatch."
    - "[PF-3, BLOCKING]: either genuinely reuse run_truncation_probe_v9 directly for the per-vertex search loop across all three budgets (recommended -- zero new code, removes duplicate-code drift risk) or correct required_artifacts_note's justification to state the real reason (if any) a new function is needed, since the stated reason is false on direct code read."
    - "[PF-4, BLOCKING]: correct the frobenius citation in both amendment_scope and required_artifacts_note to graph['field'].frobenius (an Fp2Field instance method reached via the already-imported graph object), not a standalone module-level import."
    - "[PF-5, advisory]: pre-resolve parse_v8_new_delta_map reuse toward genuine import (confirmed unconditionally safe), removing an unnecessary open disjunction."
    - "[PF-6, advisory]: restate v9's own PF-3 cross-hardware wall-clock reproducibility caveat for v10's 'every vertex guaranteed truncated at every sweep point' premise."
    - "[PF-7, advisory]: require n_resolved and conjugate-pair-corrected effective sample size accompany any future citation of a cross-sweep histogram-shift finding, not a bare percentage comparison."
    - "[PF-8, advisory]: require execution_report.yaml explicitly confirm the histogram/conjugate-pair reporting logic's behavior at n_resolved=0 or small n_resolved, whether exercised in practice or not."
    - "None of PF-5 through PF-8 blocks freeze independently; PF-1 through PF-4 do, collectively, as four separate, directly-demonstrated defects."
  counterexample_or_mutation: >-
    The cheapest concrete demonstration that PF-2's failure-isolation gap is
    live, not merely theoretical: once implemented, deliberately inject a
    fault into the b=0.8 (middle) sweep point's histogram/conjugate-pair
    code after b=0.6 has completed successfully, and confirm the written
    truncation_sweep_comparison.json still contains b=0.6's full result plus
    a recorded sweep_point_error for b=0.8, with b=1.0 either completing
    normally or also recording its own independent error -- never silently
    discarding b=0.6's already-valid result. If it does not preserve b=0.6,
    that directly confirms PF-2 as specified, not merely as feared, and
    blocks dispatch until fixed; if it does, that is the cheapest possible
    positive confirmation before spending the real 465.6s worst-case compute
    this amendment is sized for.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale, single-prime search-procedure diagnostic work,
    H-SSIQ-36e970.asymptotic_claim null throughout, correctly inherited and
    unchanged. The relevant baseline is this lineage's own code-verified-
    crash-path and GD-9/GD-10 required-artifacts-accuracy standard, which
    required_artifacts_note itself explicitly invokes as its governing
    repair -- PF-3 and PF-4 are exactly the shape that repair exists to
    catch, applied here to the two things genuinely new relative to v9 (the
    claimed-necessary "generalized" search function and the new
    conjugate-pair reporting's import), not to the parts (Comparisons 1/2's
    core logic) v9's own two review rounds already audited and this
    amendment correctly proposes to keep unchanged.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty -- unchanged, a search-procedure diagnostic, not a heuristic-conditional asymptotic-complexity claim. asymptotic_claim: null throughout. No numbered heuristic implicated by this amendment."
  cost_model_challenges:
    - "No asymptotic-cost claim anywhere. Worst-case total search time across all three sweep points (194*(0.6+0.8+1.0)=465.6s) and the 1200s/~2.58x total budget margin are independently re-verified correct. No total-expected-cost = per-attempt-cost x inverse-success-probability computation is needed -- bounded, single-run, non-probabilistic-success diagnostic, consistent with v8's/v9's own cost-model framing. The one cost-adjacent gap is PF-1: whether graph reconstruction genuinely runs once or three times changes the measured wall-clock this amendment reports by roughly 2-4 seconds -- immaterial to the 1200s cap but material to the spec's own internal consistency, since it asserts both counts in different places of the same document."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "OBJECTIVE_BOUNDARY explicitly excludes H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label, and lever L4, and is explicitly scoped to p=2437 alone -- verified by direct grep of the full spec text for these terms, not merely trusted from prose. It correctly and explicitly declines to let this amendment alone answer RT-BATCH-011's original truncation-boundary question ('even the b=1.0 sweep point remains below the 1.14993s full-completion floor'), framing itself narrowly and correctly as a test of whether v9's own selection-effect artifact weakens. No scope inflation found."
  proof_architecture_challenges:
    - "Not applicable -- H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged; direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held, unchanged from v8's and v9's own review history."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v10.yaml as
    committed at 6edd3ce1 (draft, pre_freeze_review.status: pending, no
    implementation file yet written): the underlying experimental design --
    three intermediate budgets, all independently re-verified strictly below
    the observed 1.14993s natural-completion floor (min wall_seconds
    re-derived directly from RUN-SSIQ-a85692-h's real per_vertex_records:
    1.149932861328125, zero of 194 records below any of 0.6/0.8/1.0s),
    correctly isolating budget as the sole manipulated variable via v8/v9's
    already-audited seed formula, correctly bounded and honestly justified
    on cost (194*2.4=465.6s worst case, ~2.58x margin, independently
    re-verified) -- is sound and directly responsive to RT-BATCH-012's own
    named recommendation. It is not yet safe to freeze: four
    directly-demonstrated defects (a self-contradictory graph-rebuild-count
    requirement, PF-1; a failure-isolation mechanism narrower than its own
    stated intent and concretely riskier than any prior amendment's because
    it spans three formerly-independent runs sharing one combined artifact,
    PF-2; a false code-verified justification for an unnecessary new
    duplicate function, PF-3; and a citation of a non-existent module-level
    import that would crash on literal implementation, PF-4) must be
    corrected before an Executor can implement this plan without material
    risk of resolving at least one of them incorrectly. All four required
    fixes are textual, zero new compute, and do not touch the sound
    underlying budget/seed-reuse/scope design.
  next_concrete_action: >-
    Coordinator: apply PF-1 through PF-4 in one pass (resolve the
    graph-rebuild-count contradiction toward the "rebuilt ONCE" design;
    require per-sweep-point exception wrapping around each budget's entire
    bundle, not just Comparison 2, with incremental result accumulation;
    correct required_artifacts_note to reuse run_truncation_probe_v9
    directly rather than duplicate it; correct the frobenius citation to
    graph['field'].frobenius) -- textual only, zero new compute -- then
    apply PF-5 through PF-8 in the same pass, and request a second, focused
    pre-freeze round scoped specifically to (a) confirming the corrected
    text is now internally consistent with no remaining "once" vs. "three
    times" contradiction, and (b) once an implementation exists, confirming
    the deliberate-fault failure-isolation test named in "Counterexample or
    mutation" actually passes -- before freezing and dispatching the real
    465.6s worst-case compute this amendment is sized for.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v10.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no code executed from this
    lineage's implementation modules -- this review is a specification and
    artifact-schema trace against a draft with no implementation file yet,
    not an execution. Non-durable, read-only local Python computations were
    run directly against the committed tree: (a) extracted and computed
    min/max wall_seconds across all 194 per_vertex_records in
    RUN-SSIQ-a85692-h/probe_delta_e_comparison.json, and counted records
    below 0.6/0.8/1.0/1.14993s thresholds (all zero, confirming the "every
    vertex guaranteed truncated" premise against real data); (b) grepped
    build_isogeny_graph.py's full module namespace for a top-level
    frobenius definition (none found; only Fp2Field.frobenius, an instance
    method); (c) verified self-conjugate-vertex impossibility over the
    194-vertex non-F_p-rational domain at p=2437 via modular arithmetic
    (2*x[1] ≡ 0 mod odd prime p forces x[1] ≡ 0, i.e. F_p-rational,
    excluded from the domain by construction); (d) grepped the full
    specification_v10.yaml text for PERSISTS/WEAKENS/lever L4/H-SSIQ-36e970
    mentions to confirm scope-discipline claims; (e) independently
    recomputed the budget arithmetic (194*2.4=465.6, 1200/465.6≈2.58x) and
    confirmed run_truncation_probe_v9's function signature and internal
    body (delta_e_truncation_probe_v9.py, full 665 lines) make no reference
    to the module-level PER_VERTEX_BUDGET_SECONDS constant. No file was
    written or edited by any of these computations. Read in full:
    specification_v10.yaml (277 lines); specification_v9.yaml (498 lines,
    all PF-1 through PF-5 fix text, both freeze-round verdicts);
    RT-BATCH-012.md (full); delta_e_truncation_probe_v9.py (full, 665
    lines, the real frozen v9 implementation); delta_e_independent_rng_probe_v8.py
    lines 145-176; compute_delta_e.py lines 144-211; build_isogeny_graph.py
    (EXP-SSIQ-58b642/implementation/) lines 54-125; trapping_diagnostic_v5.py
    lines 102-130.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task wrote
    only coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v10.md
    (creating the batch's reviews/ directory, which did not previously
    exist, as part of writing that single file) -- experiments/EXP-SSIQ-a85692/
    (including specification_v10.yaml and every prior run package) and
    every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
