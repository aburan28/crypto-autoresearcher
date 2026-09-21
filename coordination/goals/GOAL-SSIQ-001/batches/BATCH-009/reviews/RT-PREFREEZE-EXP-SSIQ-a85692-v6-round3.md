# RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3 — Third pre-freeze Red Team review
# of the REVISED DRAFT amendment `specification_v6.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-009

**Reviews `experiments/EXP-SSIQ-a85692/specification_v6.yaml` at
`status: draft`, `pre_freeze_review.findings_applied: [PF-1, PF-2, PF-3,
PF-4, PF-5, PF-6, PF-7, PF-8, PF-10, PF-11]`, as read directly from the
working tree under task `TASK-20260806-32fb8b`.** Per this task's own
operating rules, only a Coordinator-committed snapshot is treated as durable
evidence; this report is advisory input to the Coordinator's own freeze
decision and changes nothing under `experiments/EXP-SSIQ-a85692/` (including
`specification_v5.yaml`, still frozen unedited) or any ledger record.

Read in full per the launching task: `AGENTS.md`, `CLAUDE.md`,
`agents/red-team.md`; `RT-PREFREEZE-EXP-SSIQ-a85692-v6.md` (round 1,
DO-NOT-FREEZE, PF-1/PF-2/PF-3 blocking) and
`RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2.md` (round 2, DO-NOT-FREEZE,
PF-7/PF-8 blocking-NEW) in full; `RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md`
(the format/caliber and "advisory-vs-blocking, applied-between-rounds"
precedent) in full; the current `specification_v6.yaml` in full, in
particular the entire `pre_freeze_review` block (all ten `pfN_summary`
entries), `inputs.gd12_fix_v6`, and `inputs.funnel_structure_diagnostic_v6`;
the frozen, unchanged `descent_hitting_time.py` (`greedy_descent_hitting_time`,
lines 179–222) and `trapping_diagnostic_v5.py` (`build_graph_for_prime`,
lines 133–148, `SEED = 20260805`, line 90) directly; `compute_delta_e.py`
(`SEEDS = [20260805, 11, 977]`, line 101; `build_all_graphs(PRIMES, SEEDS[0])`,
line 661; the `descent_metrics` block, lines 820–860) directly, specifically
to re-confirm the seed/graph provenance PF-8's numbers depend on, not merely
to re-read round 2's claim about it. **Programmatically queried, not sampled
from prose or from either prior report's own numbers**:
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json`'s
`descent_metrics.per_prime[p].greedy_trapped_fraction` and
`phase_minus1_real_search[p].n_vertices` for all four primes (2437, 3889,
5737, 7333), independently recomputing `n_trapped_false = round((1 -
greedy_trapped_fraction) * n_vertices)` and `sum(basin) = n_vertices -
n_trapped_false` for each, from a fresh Python process, not by re-deriving
round 2's arithmetic by hand.

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
    found unprobeable in this campaign's prior reviews; recorded as the
    standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This
    review shares a model family with every producer and every prior
    reviewer in this lineage, including rounds 1 and 2 of this same draft;
    it does not upgrade the campaign's evidence tier by itself.
```

---

## Bottom line up front

**PF-7 and PF-8 are both CONFIRMED HOLDING at the level that matters — the
required Executor-facing BEHAVIOR is now unambiguous (PF-7) and the
illustrative numbers are now independently, exactly correct (PF-8), verified
here from a fresh query, not by re-deriving round 2's arithmetic.** PF-10 and
PF-11 are confirmed applied with no gap. **No new BLOCKING defect survives
this round.** This draft can be frozen once two small, non-blocking text
additions are made (PF-12, PF-13) — the same "advisory, non-blocking,
zero-search-cost" category PF-4/PF-5/PF-6/PF-10/PF-11 already occupy in this
lineage, not a fourth DO-NOT-FREEZE cycle.

Two new advisory-only findings, both surfaced by reading this round's own new
text with the same skepticism that found PF-7/PF-8 as byproducts of round 1's
fix text:

1. **PF-12 [ADVISORY, NEW]: PF-7's fix closes the required BEHAVIOR
   unambiguously, but its own justifying parenthetical — "the SAME per-prime
   isolation mechanism crosscheck_pass gating already requires... the
   identical wrapping, not a second, different mechanism" — never names a
   concrete implementation (no try/except, no pseudocode, no code-level
   description anywhere in the document), and the claim that crosscheck_pass
   gating "necessarily" requires the same wrapping the accounting assertion
   needs is not actually true as a matter of necessity: crosscheck_pass is a
   precomputed boolean that gates entry into PART B's per-prime block via a
   plain conditional skip, which raises nothing and therefore needs no
   exception-catching wrapper at all, whereas the accounting assertion's own
   "halt with an explicit error" is a mid-computation raise that DOES need
   one to stay scoped to one prime.** This does not leave the required
   OUTPUT ambiguous (both requirements — skip-and-report on
   `crosscheck_pass=False`; halt-and-report-only-that-prime on an accounting
   mismatch — are independently pinned down precisely enough that any
   Executor converges on the same observable artifact), so it is not a PF-3/
   PF-7-style operational ambiguity; it is a confidently-stated, unverified
   implementation-necessity claim in a fix's own connective prose, one rung
   below PF-8's shape (a false numeric illustration) rather than PF-7's
   (an operationally ambiguous scope).
2. **PF-13 [ADVISORY, NEW]: the draft now assigns different failure-handling
   SEVERITY to two structurally analogous, both-tautological partition
   checks, without ever explaining the asymmetry.** PART A's
   `n_trapped_true + n_trapped_false == n_vertices` assertion is stated to be
   "a global, run-aborting check... a bug independent of any prime-specific
   data question." PART B's `sum(basin) + n_trapped_false == n_vertices`
   assertion — the *identical shape* of check, "every vertex accounted for
   exactly once," now proven (round 2, independently re-derived and
   reconfirmed here) to hold unconditionally by construction for the same
   underlying reason — is, per PF-7's fix, PER-PRIME. Both checks are
   guaranteed to pass on correct code, so this is inert in practice, but the
   draft gives no reason why a violation of one implies a systemic code bug
   (global abort) while a violation of the structurally identical other
   implies only a prime-specific anomaly (per-prime halt). This is a
   documentation/rationale coherence gap, not an operational one — visible
   only when the two assertions, patched separately across rounds 1/2/3, are
   read side by side.

Neither finding requires redesigning either part's mechanism, and both are
fixable at zero new search cost with a sentence each, matching this
lineage's established advisory category.

---

## (1) PF-7's fix: is the halt-scope behavior actually unambiguous now, and is the named mechanism pinned down?

### Required behavior: CONFIRMED UNAMBIGUOUS

Re-read `funnel_structure_diagnostic_v6` item 2's FAILURE-HANDLING SCOPE
paragraph against the exact two-reading counterexample round 2's report
constructed (a per-prime `try/except` catching the accounting assertion vs. a
literal "GLOBAL" reading that aborts everything). The current text states:
"a mismatch for prime P halts ONLY prime P's PART B computation for that
prime... The other three primes' PART B results are computed and written to
the output artifacts normally, unaffected by one prime's accounting
mismatch." This is a complete, unconditional behavioral specification: for
any prime P with a mismatch, that prime's own output must record an explicit
error naming the mismatch amount, and every other prime's output must be
computed and written normally regardless of P's outcome. Round 2's own
counterexample (an Executor who reads "GLOBAL" literally and discards all
four primes' output) is now explicitly foreclosed by name — the sentence "this
assertion is NEVER global/run-aborting, correcting the original text's
self-contradiction" directly rules out that reading. **PF-7's core, blocking
defect (an unreconciled two-scope contradiction) does not survive**: there is
now exactly one required behavior, stated without a competing reading
anywhere in the document.

### PF-12 [ADVISORY, NEW]: the "same mechanism" justification is asserted, not pinned down, and is not necessarily accurate

The fix earns its unambiguous behavior through a parenthetical that makes a
stronger, additional claim than the behavior itself requires: "the SAME
per-prime isolation mechanism `gd12_fix_v6`'s `crosscheck_pass` gating
already requires (an Executor implementing that gating necessarily wraps
each prime's PART B block separately; this assertion's halt uses the
identical wrapping, not a second, different mechanism)."

Tracing `crosscheck_pass`'s own required behavior (`gd12_fix_v6`'s
FAILURE-HANDLING MODEL paragraph) against what it actually needs at the
implementation level: `crosscheck_pass` is computed and recorded as a
**precomputed per-prime boolean field**, and PART B's own precondition is "if
`crosscheck_pass` is False for a given prime, PART B MUST NOT run for that
prime." Satisfying this requires nothing more than a plain conditional
(`if crosscheck_pass[p]: ... else: skip`) inside a per-prime loop — it never
raises, so there is nothing for any wrapper to catch. By contrast, the
accounting assertion's own "halting with an explicit error on any mismatch"
is a mid-computation raise, which — to satisfy "halts ONLY prime P's
computation" — genuinely does require an exception-catching construct
(a `try/except` or equivalent) scoped to that one prime's block, so that the
raise does not propagate out of the per-prime loop and abort iteration for
the remaining primes.

These are two different code shapes (a conditional skip vs. an
exception-catching wrapper), and the parenthetical's claim that an Executor
implementing `crosscheck_pass` gating "necessarily" produces the wrapping the
accounting assertion needs is not established anywhere in the document — no
`try/except`, no pseudocode, no code-level description of "the wrapping"
appears at any point in `specification_v6.yaml`. This matches the task's own
framing precisely: the draft **asserts that a shared mechanism exists rather
than naming what it concretely is**. An Executor could satisfy both required
BEHAVIORS (which are independently, correctly pinned down) via, for example,
(a) a single `try/except` per prime that also contains the plain
`crosscheck_pass` conditional inside it, (b) a `try/except` added
specifically and only around the accounting-assertion step, separate from an
un-wrapped `crosscheck_pass` conditional earlier in the same per-prime
iteration, or (c) a helper function per prime returning a status/error object
instead of raising at all. All three produce the same *observable output
artifact* the contract requires, so this does not reopen PF-7's operational
ambiguity — but it does mean the parenthetical's own confidently-stated
implementation-necessity claim ("the identical wrapping, not a second,
different mechanism") is unverified prose asserted into contract text without
a trace, the same category of defect (though narrower in consequence) PF-8
was for numeric illustrations. Recommend either removing the parenthetical's
implementation-necessity claim (state only the required behavior, which is
already sufficient and correct) or naming the mechanism concretely (e.g.,
"an Executor should structure this as one `try/except AssertionError` block
per prime, covering both the `crosscheck_pass` skip and the accounting
check"). Non-blocking: the required behavior an Executor must deliver is
already unambiguous without this parenthetical.

## (2) PF-8's fix: independently re-verified from a fresh query, not by re-deriving round 2's arithmetic

Directly queried `RUN-SSIQ-a85692-b/raw-result.json` in a fresh Python
process:

| prime | `n_vertices` (`phase_minus1_real_search[p]`) | `greedy_trapped_fraction` (`descent_metrics.per_prime[p]`) | `n_trapped_false = round((1-frac)*n)` | `sum(basin) = n - n_trapped_false` | draft's stated values |
|---|---|---|---|---|---|
| 2437 | 203 | 0.8374384236453202 | **33** | **170** | 33/170 |
| 3889 | 324 | 0.7222222222222222 | **90** | **234** | 90/234 |
| 5737 | 478 | 0.8200836820083682 | **86** | **392** | 86/392 |
| 7333 | 611 | 0.851063829787234  | **91** | **520** | 91/520 |

All four pairs match the draft's `funnel_structure_diagnostic_v6` item 2
"ILLUSTRATIVE VALUES, CORRECTED" section exactly, with no rounding
discrepancy (each `(1-frac)*n` lands within `1e-10` of an exact integer, not
merely close). **PF-8's numeric fix is CONFIRMED CORRECT, independently
computed from a fresh query in this round, not by re-checking round 2's
arithmetic by hand.**

**Provenance re-verified, not merely re-read from round 2's claim:** the
`greedy_trapped_fraction` values above come from `RUN-SSIQ-a85692-b`'s
`descent_metrics` block, computed by `compute_delta_e.py`'s
`dht.run_population(g["adjacency"], vertices, delta_map, "greedy", ...)`
(lines 838–839) on graphs built by `build_all_graphs(PRIMES, SEEDS[0])`
(line 661) where `SEEDS[0] = 20260805` (line 101). Directly read
`trapping_diagnostic_v5.py`'s `build_graph_for_prime` (lines 133–148) and its
module-level `SEED = 20260805` (line 90, docstring: "same pinned convention
as `build_all_graphs()`") and confirmed both call the identical sequence
(`random.Random(seed)` → `seed_j_invariant` → `verify_seed_supersingular` →
`build_graph_bfs`) with the same seed value — so the graph PART A/B's reuse
mechanism will rebuild is deterministically identical to the one
`greedy_trapped_fraction` was already computed on, and the `delta_map` PART
A/B loads (`load_archived_prime_data`, reading this same
`RUN-SSIQ-a85692-b/raw-result.json`) is the identical dict. The draft's claim
that these are "the identical quantity this amendment's own reuse mechanism
will reproduce byte-for-byte once `greedy_descent_hitting_time_v2` exists" is
therefore justified, not merely asserted, and PF-8's illustrative values are
genuine predictions, not guesses that happen to be checkable.

## (3) PF-10 and PF-11: confirmed applied, no new gap

**PF-10 [ADVISORY, round 2] — CONFIRMED APPLIED.** The `is_structural_local_min`
disclosed duplicate now restates the source formula's missing-neighbour
"RAISE LOUDLY" guard (`gd12_fix_v6`, "PF-10 FIX APPLIED... raise loudly if
any u in adjacency[v] has no delta_map entry, for the identical reason that
file's own PF-7 fix already gives"). Re-checked this guard's scope claim
against the rest of the control-flow text (per the launching task's specific
direction to check consistency, not merely presence): the guard is described
as "structurally unreachable given this amendment's own required coverage
assertion" — i.e. it presupposes the coverage assertion (delta_map keys
matched against the rebuilt vertex set == `archived_n_vertices`) runs and
passes *before* `is_structural_local_min` is ever invoked, for both PART A's
cross-check and PART B's basin computation, which share the same reuse
mechanism. This is a reasonable, load-bearing precondition, but its own
failure-handling scope (global vs. per-prime, if the coverage assertion
itself ever failed) is nowhere stated — a real but pre-existing gap (present
since round 1's PF-2 fix introduced the coverage assertion, not introduced by
this round's PF-10 text), noted here for completeness but not counted as a
new-this-round finding, since PF-10's own restated guard is itself internally
consistent with what it claims (unreachable given the coverage assertion,
whatever that assertion's own scope turns out to be).

**PF-11 [ADVISORY, round 2] — CONFIRMED APPLIED.** The top-decile
concentration formula now specifies `top_decile_concentration: null` with an
explicit note for the theoretical `n_basin_eligible == 0` case, "never a
division by zero," and states this is "not reached by any of this
amendment's four primes, whose real basin-eligible counts are
86/114/176/270." Independently re-confirmed these four counts are unchanged
from round 2's own table (derived from `RUN-SSIQ-a85692-e`'s archived
`n_structural_local_min` minus `RUN-SSIQ-58b642-a`'s archived F_p-rational
locus sizes); no boundary case is triggered for the primes actually in scope.

## (4) Fresh read for new defects, beyond the four patches

Re-read the entire draft with the same discipline that surfaced PF-7/PF-8 as
byproducts of round 1's fix text (not merely diffing against round 2's
version), specifically for the two things this task named: (a) whether
PF-7's newly-added "same mechanism" language is precise enough for an
Executor to implement without ambiguity (covered above: behaviorally yes,
implementation-detail no — PF-12), and (b) whether the PF-10 restatement is
consistent with the rest of the control flow (covered above: consistent,
modulo a pre-existing, not-new-this-round gap around the coverage
assertion's own failure scope).

**PF-13 [ADVISORY, NEW]**, surfaced by comparing PART A's and PART B's two
accounting assertions side by side rather than reading either in isolation:
see bottom-line-up-front above for the finding. Concretely, quoting both:

- PART A (`gd12_fix_v6`, REQUIRED CORRECTED CROSS-CHECK): "`n_trapped_true +
  n_trapped_false` MUST equal that prime's archived `n_vertices` exactly,
  halting with an explicit error on any mismatch (this specific assertion is
  a **global, run-aborting check** -- a violation here means the walk was not
  run on every vertex exactly once, **a bug independent of any prime-specific
  data question**)."
- PART B (`funnel_structure_diagnostic_v6`, item 2): "`sum(len(basin[m])
  ...) + n_trapped_false` MUST equal that prime's `n_vertices` exactly... a
  mismatch for prime P halts **ONLY prime P's PART B computation**... Every
  vertex's walk is either trapped=True (falls into exactly one basin-eligible
  m's basin...) or trapped=False (counted in `n_trapped_false`), so this
  assertion is a genuine, exhaustive, non-overlapping partition check, not
  vacuous, and **holds unconditionally by construction**."

Both are, by the draft's own words, "every vertex accounted for exactly
once" tautologies that "hold unconditionally by construction" given correct
code — PART A's own rationale for treating a violation as evidence of "a bug
independent of any prime-specific data question" applies with exactly the
same force to PART B's assertion (a bug in the basin-assignment loop that
mis-assigns or double-counts a walk is no more "prime-specific" a priori than
a bug in the walk-dispatch loop that skips a vertex). The draft never states
why one violation category should be treated as strong enough evidence of a
systemic defect to abort the whole run before any prime's output is written,
while the other, structurally identical category, should be treated as
isolated to one prime. Since both checks are proven (independently
re-derived in round 2, re-confirmed above) to hold unconditionally given
correct code, this asymmetry has no live consequence for `RUN-SSIQ-a85692-f`
as currently scoped — but per this campaign's own GD-4/GD-12/PF-3/PF-7
standard ("unlikely to matter in practice" is not itself a justification a
reviewer should accept without an explicit rationale), the asymmetric
severity assignment deserves either (a) a one-clause justification for why
the two checks warrant different scopes, or (b) unifying them to the same
scope (most naturally: also making PART A's `n_trapped_true + n_trapped_false
== n_vertices` check per-prime, matching PART B's now-corrected model, since
nothing in PART A's own text argues that a per-prime data anomaly could not
also be the actual cause of that specific violation).

No other new defect was found. The `required_artifacts`, `budget`, and
`required_artifacts_note` sections are unchanged since round 2 and remain
internally consistent with the corrected text above.

## (5) Whole-draft coherence pass, PART A and PART B together, after three rounds of patches

Specifically checked for a recurrence of v5's own PF-9 shape (a field-name
conflation feeding a hard-fail assertion, inherited silently across rounds)
inside v6: grepped every occurrence of `n_resolved`/`n_vertices` in the
current draft. **v6 explicitly and correctly avoids the PF-9 trap**: its one
mention of `n_resolved` reads "vertex set == `archived_n_vertices`, **never
`n_resolved`, per PF-9**" (line 279) — the coverage assertion is stated
correctly and cites the exact lesson from the sibling amendment's own
round-2 finding, rather than repeating it. No other `n_resolved`/`n_vertices`
conflation exists anywhere in v6.

Beyond that specific check, the accumulated PART A/PART B text remains
readable and internally traceable end-to-end: `amendment_scope` states the
high-level claim once; `gd12_fix_v6` and `funnel_structure_diagnostic_v6`
restate and formalize it with explicit fix-provenance annotations
(`PF-N FIX APPLIED`) at every edited clause, which — while verbose (ten
`pfN_summary` entries plus inline annotations repeating much of the same
content across `pre_freeze_review`, `gd12_fix_v6`, and
`funnel_structure_diagnostic_v6`) — has not introduced a contradiction
between the summary and the operative text anywhere checked in this pass
(each `pfN_summary` was cross-read against its corresponding operative clause
above and found to match). The one place where three rounds of patches
produced a genuine side-effect inconsistency is PF-13 (above): PART A's and
PART B's accounting-assertion severities were fixed independently, in
different rounds (PF-3 fixed PART A's cross-check scope in round 1; PF-7
fixed PART B's accounting-assertion scope in round 2), and nothing in either
round's fix ever compared the two resulting scopes against each other.

---

## Findings summary

| ID | Status this round | Location | One-line |
|---|---|---|---|
| PF-7 | **CONFIRMED HOLDING (behavior)** | PART B accounting-assertion scope | Required behavior (mismatch halts only that prime; others proceed and are written) is now unambiguous; see PF-12 for the fix's own unverified "same mechanism" implementation claim |
| PF-8 | **CONFIRMED HOLDING** | PART B illustrative values | Independently re-verified from a fresh query: 33/170, 90/234, 86/392, 91/520 for p=2437/3889/5737/7333 respectively, exact matches, graph/seed provenance re-traced and confirmed identical |
| PF-10 | CONFIRMED APPLIED | PART B is_structural_local_min duplicate | Missing-neighbour guard restated; consistent with the coverage-assertion precondition it depends on |
| PF-11 | CONFIRMED APPLIED | PART B top-decile | null-with-note for n_basin_eligible==0, not reachable by the four in-scope primes |
| PF-12 | **ADVISORY, NEW** | PART B accounting-assertion FAILURE-HANDLING SCOPE parenthetical | "Same mechanism...identical wrapping" is asserted, not pinned down as concrete code, and is not strictly necessary (crosscheck_pass gating needs no exception wrapper at all; the accounting halt does) — non-blocking, required OUTPUT behavior is unaffected |
| PF-13 | **ADVISORY, NEW** | PART A vs PART B accounting-assertion severity | Two structurally identical, both-tautological "every vertex accounted for once" checks are assigned different failure scopes (global vs. per-prime) with no stated justification for the asymmetry — inert in practice since both provably hold by construction, but unreconciled |

---

## Required controls / checks before dispatch

- PF-7, PF-8, PF-10, PF-11: no further action required; all CONFIRMED
  HOLDING/APPLIED this round, independently re-derived and re-queried, not
  merely re-read.
- **PF-12 [ADVISORY]:** either remove the "necessarily wraps... the identical
  wrapping, not a second, different mechanism" implementation-necessity
  claim from the accounting-assertion's FAILURE-HANDLING SCOPE text (the
  required behavior stands on its own without it), or name the mechanism
  concretely (e.g., a single `try/except` per prime covering both the
  `crosscheck_pass` skip and the accounting check).
- **PF-13 [ADVISORY]:** add one clause justifying why PART A's accounting
  assertion is global/run-aborting while PART B's structurally analogous one
  is per-prime, or unify both to the same scope.
- Neither PF-12 nor PF-13 requires a fourth full review round before freeze;
  both are text-only, zero-search-cost additions in the same category as
  PF-4/PF-5/PF-6/PF-10/PF-11 in this lineage.

## Counterexample or mutation

**PF-8's counterexample, re-executed from a fresh query this round (not
copied from round 2's report):**

```
p=2437: n_vertices=203, greedy_trapped_fraction=0.8374384236453202
        (1-0.8374384236453202)*203 = 33.00000000000001 -> n_trapped_false=33
        sum(basin) = 203-33 = 170
p=3889: n_vertices=324, greedy_trapped_fraction=0.7222222222222222
        (1-0.7222222222222222)*324 = 90.0 -> n_trapped_false=90
        sum(basin) = 324-90 = 234
p=5737: n_vertices=478, greedy_trapped_fraction=0.8200836820083682
        (1-0.8200836820083682)*478 = 85.99999999999999 -> n_trapped_false=86
        sum(basin) = 478-86 = 392
p=7333: n_vertices=611, greedy_trapped_fraction=0.851063829787234
        (1-0.851063829787234)*611 = 91.0 -> n_trapped_false=91
        sum(basin) = 611-91 = 520
```

All four exactly match the draft's stated ILLUSTRATIVE VALUES with no
discrepancy — this round finds no falsifier, unlike round 2's original
9/18/18/17 counterexample against the pre-fix text.

**PF-12's illustration (not a falsifier of the required output, only of the
"same mechanism" narrative claim):** an Executor who implements
`crosscheck_pass` gating as a bare `if crosscheck_pass[p]: compute(p) else:
skip(p)` inside a `for p in primes` loop (a fully compliant, natural
implementation of PART A's own stated requirement, needing no exception
handling at all) has, at that point, built no "wrapping" for the accounting
assertion's own raise to reuse — they must still add a `try/except`
specifically for that assertion. This does not violate any requirement in
the contract (the final artifact is identical either way), but it directly
falsifies the parenthetical's claim that such an Executor's `crosscheck_pass`
implementation "necessarily" already provides "the identical wrapping" the
accounting assertion needs.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
(toy-scale infrastructure and a graph-structural diagnostic,
`asymptotic_claim: null` throughout, correctly inherited). The relevant
baseline remains this campaign's own instrument- and spec-scrutiny
discipline (GD-4 through GD-12, v5's PF-9, v6's own PF-7/PF-8): this round
confirms that discipline converges — three successive rounds of "trace it,
don't trust it" applied to the same two paragraphs (the accounting
assertion's scope and its illustrative numbers) have now exhausted their
BLOCKING findings, leaving only prose-precision gaps (PF-12) and an
unreconciled-but-inert severity asymmetry (PF-13) — the same terminal shape
v5's own lineage reached at its round 2 (one small blocking item, then
freeze-with-fixes), here reached one round later and with no blocking item
at all.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains empty (gradient-existence
screen, not a heuristic-conditional complexity claim) — attacked and held,
consistent with every prior review in this lineage. No finding here
implicates a numbered heuristic; PF-12/PF-13 are prose-precision and
rationale-consistency gaps in diagnostic contract text, not claims about the
underlying ECDLP-adjacent problem.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly, inherited); the per-attempt-cost × inverse-success-probability
review does not apply. The `900s`/`0.3` CPU-hour budget is unchanged from
round 1 and remains realistic; PF-12 and PF-13 are both text-only,
zero-cost. No live evidentiary concern remains from PF-7/PF-8 (both
confirmed correct this round); PF-12/PF-13, being inert-in-practice
(neither assertion is expected to fire, and the required output behavior for
both is already unambiguous), carry no evidentiary risk beyond documentation
clarity for a future reader or amendment.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis; `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) correctly stated and not exceeded. No scope-inflation
found. `funnel_structure_diagnostic_v6`'s `OBJECTIVE_BOUNDARY` correctly
restates PART B as a diagnostic, not a claim, unchanged since round 1. This
amendment still correctly implements exactly the two resume actions
`DEC-20260806-357b30`'s `next_actions`/`resume_action` named, on the same
four primes, at zero new search cost — reconfirmed here, unaffected by
PF-12/PF-13, both purely inside PART B's own diagnostic text and both inert
given the underlying assertions provably hold.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` (inherited unchanged)
remains correctly reasoned — a direct instrument-level gradient-existence
screen and a graph-structural diagnostic, not a proof-oriented proposal.
Attacked and held, same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v6.yaml` as read in the
working tree, `status: draft`: rounds 1 and 2's five blocking findings
(PF-1, PF-2, PF-3, PF-7, PF-8) are all genuinely resolved on their own
stated terms. This round independently re-verifies PF-7's required behavior
is unambiguous (a mismatch for prime P halts only P's PART B computation;
all other primes are computed and written normally) and PF-8's illustrative
values are exactly correct (33/170, 90/234, 86/392, 91/520 for
p=2437/3889/5737/7333), both from fresh queries against the archived
`RUN-SSIQ-a85692-b/raw-result.json` and fresh reads of the frozen code, not
by re-deriving either prior report's own numbers. PF-10 and PF-11 are
confirmed applied with no gap. **No blocking defect survives this round.**
Two new advisory findings round out this pass: PF-12 (the accounting
assertion's "same mechanism" justification is asserted, not pinned down as
concrete code, and is not strictly necessary as stated, though the required
Executor-facing behavior is unaffected) and PF-13 (PART A's and PART B's two
structurally analogous, both-provably-tautological accounting assertions are
assigned different failure-handling severities with no stated
justification, inert in practice but unreconciled in the contract's own
prose). Neither requires redesigning either part's mechanism or a further
review round; both are fixable at zero new search cost.

## Next concrete action

Coordinator: this draft may proceed to `status: approved` / `frozen_at` once
PF-12 and PF-13 are applied as text-only additions (removing or concretizing
the accounting assertion's "same mechanism" implementation-necessity claim;
adding a one-clause justification, or unification, for the PART A/PART B
accounting-severity asymmetry) — consistent with this lineage's own
established practice of applying advisory-only findings without a dedicated
re-verification round (v5's PF-10/PF-11, v6's own PF-4/PF-5/PF-6/PF-10/PF-11
were all applied this way). If the Coordinator prefers a fourth pass to
re-confirm PF-12/PF-13's specific text, that is available but not, on this
review's own findings, required before freeze.

## Overall verdict

**FREEZE-WITH-FIXES.** No blocking item remains. Required before
`status: approved` / `frozen_at`:

1. **[ADVISORY]** PF-12 — remove or concretize the accounting assertion's
   "same mechanism... identical wrapping" implementation-necessity claim,
   which is asserted rather than pinned down and is not strictly accurate as
   stated (the required Executor-facing behavior itself is unaffected and
   already unambiguous).
2. **[ADVISORY]** PF-13 — add a one-clause justification for, or unify, the
   differing failure-handling severities PART A and PART B assign to their
   two structurally analogous, both-tautological accounting assertions.

PF-7 and PF-8 (round 2's blocking findings) are both **CONFIRMED HOLDING**,
independently re-derived and re-queried in this round rather than trusted
from round 2's own report. PF-10 and PF-11 are **CONFIRMED APPLIED**. Rounds
1 and 2's five blocking findings (PF-1, PF-2, PF-3, PF-7, PF-8) are, in
total, all resolved as of this snapshot of the draft.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3
  task_id: TASK-20260806-32fb8b
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v6.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), read directly from the working tree,
    pre_freeze_review.findings_applied = [PF-1, PF-2, PF-3, PF-4, PF-5, PF-6,
    PF-7, PF-8, PF-10, PF-11] -- the third revision in this draft's own
    lineage, applying round 2's two new blocking findings (PF-7: PART B's own
    accounting-assertion failure-handling scope was self-contradictory;
    PF-8: PART B's "traced by hand" illustrative numbers were false) plus
    round 2's two advisory findings (PF-10, PF-11), on top of round 1's three
    blocking fixes (PF-1, PF-2, PF-3) and three advisory fixes (PF-4, PF-5,
    PF-6), all previously confirmed holding.
  objections:
    - "PF-12 [ADVISORY, NEW]: PF-7's fix correctly and unambiguously specifies the REQUIRED BEHAVIOR of PART B's accounting-assertion halt (a mismatch for prime P halts only P's PART B computation; the other three primes' results are computed and written normally) -- this closes PF-7's own blocking defect. But the fix's own justifying parenthetical, 'the SAME per-prime isolation mechanism gd12_fix_v6's crosscheck_pass gating already requires (an Executor implementing that gating necessarily wraps each prime's PART B block separately; this assertion's halt uses the identical wrapping, not a second, different mechanism)', never names a concrete mechanism anywhere in the document (no try/except, no pseudocode) and its claim of necessity is not actually true: crosscheck_pass gating is satisfiable by a plain per-prime conditional skip that never raises and therefore needs no exception-catching wrapper at all, while the accounting assertion's own 'halt with an explicit error' is a mid-computation raise that DOES require one to stay scoped to a single prime. This does not reopen operational ambiguity in the required OUTPUT (multiple different implementations of the underlying mechanism all produce the identical required artifact), but it is a confidently-stated, unverified implementation-necessity claim left in contract text, the same species of defect PF-8 was for numeric illustrations, one rung narrower in consequence."
    - "PF-13 [ADVISORY, NEW]: PART A's REQUIRED CORRECTED CROSS-CHECK accounting assertion (n_trapped_true + n_trapped_false == n_vertices) is explicitly stated to be 'a global, run-aborting check... a bug independent of any prime-specific data question', while PART B's accounting assertion (sum(basin) + n_trapped_false == n_vertices) -- proven, independently re-derived in round 2 and reconfirmed here, to be a structurally identical 'every vertex accounted for exactly once' tautology that 'holds unconditionally by construction' -- is, per PF-7's own fix, per-prime. The draft never explains why a violation of one structurally identical check implies a systemic code bug warranting a full-run abort while a violation of the other implies only a prime-specific issue. Inert in practice (both checks are proven to always hold given correct code), but an unreconciled asymmetry in the contract's own stated rationale, visible only when the two assertions -- fixed independently in different rounds (PF-3 in round 1 for PART A's scope, PF-7 in round 2 for PART B's scope) -- are read side by side."
    - "PF-7 [round 2's finding, CONFIRMED HOLDING (behavior)]: the required halt-scope behavior for PART B's accounting assertion is now unambiguous and fully forecloses round 2's own two-reading counterexample (a per-prime try/except vs. a literal global-abort reading) -- the current text states unconditionally that a mismatch for prime P halts only P's computation and that the other three primes' results are computed and written normally regardless, with the original self-contradictory 'GLOBAL... for that prime's computation' phrasing removed entirely. See PF-12 above for the fix's own separate, narrower, non-blocking gap."
    - "PF-8 [round 2's finding, CONFIRMED HOLDING]: independently re-verified in this round from a fresh query against RUN-SSIQ-a85692-b/raw-result.json (not by re-deriving round 2's own arithmetic): n_trapped_false = round((1-greedy_trapped_fraction)*n_vertices) computed fresh gives exactly 33/90/86/91 for p=2437/3889/5737/7333 respectively, and sum(basin) = n_vertices - n_trapped_false gives exactly 170/234/392/520 -- all four pairs match the draft's stated ILLUSTRATIVE VALUES exactly, with no rounding discrepancy. Graph/seed provenance independently re-traced: compute_delta_e.py's build_all_graphs(PRIMES, SEEDS[0]) (SEEDS[0]=20260805) and trapping_diagnostic_v5.py's build_graph_for_prime(p, SEED) (SEED=20260805, same docstring-declared convention) call the identical rng/seed_j_invariant/verify_seed_supersingular/build_graph_bfs sequence with the same seed value, confirming the graph and delta_map the draft's own reuse mechanism will load are deterministically identical to the ones greedy_trapped_fraction was already computed on."
    - "PF-10 [round 2's finding, CONFIRMED APPLIED]: the is_structural_local_min disclosed duplicate now restates the missing-neighbour RAISE LOUDLY guard from trapping_diagnostic_v5.py's own inline formula; re-checked for consistency with the rest of the control flow as this task specifically directed -- the guard's claimed unreachability presupposes the coverage assertion runs and passes before is_structural_local_min is ever invoked, which is a reasonable, load-bearing precondition; that precondition's own failure-handling scope is nowhere stated, but this is a pre-existing gap from round 1's PF-2 fix, not introduced by PF-10's own text, and PF-10's restated guard is itself internally consistent with what it claims."
    - "PF-11 [round 2's finding, CONFIRMED APPLIED]: the top-decile concentration formula specifies null-with-an-explicit-note for the theoretical n_basin_eligible==0 case; independently re-confirmed the four in-scope primes' real basin-eligible counts (86/114/176/270, unchanged from round 2's own table) never trigger this boundary."
  required_controls:
    - "PF-12: remove the accounting-assertion FAILURE-HANDLING SCOPE parenthetical's implementation-necessity claim ('necessarily wraps... the identical wrapping, not a second, different mechanism'), or replace it with a concrete, named mechanism (e.g., a single try/except per prime covering both the crosscheck_pass skip and the accounting check) -- ADVISORY, non-blocking, zero new search cost."
    - "PF-13: add a one-clause justification for why PART A's and PART B's structurally analogous accounting assertions warrant different failure-handling scopes, or unify both to the same scope -- ADVISORY, non-blocking, zero new search cost."
  counterexample_or_mutation: >-
    PF-8: fresh, independent query against RUN-SSIQ-a85692-b/raw-result.json
    in this round's own Python process: n_vertices/greedy_trapped_fraction
    pairs (203, 0.8374384236453202), (324, 0.7222222222222222),
    (478, 0.8200836820083682), (611, 0.851063829787234) for
    p=2437/3889/5737/7333 give n_trapped_false = 33/90/86/91 and
    sum(basin) = 170/234/392/520 exactly, matching the draft's stated
    ILLUSTRATIVE VALUES with no discrepancy -- no falsifier found this round,
    unlike round 2's original 9/18/18/17 counterexample against the pre-fix
    text.
    PF-12 (illustrative, not a falsifier of required output): an Executor
    who implements crosscheck_pass gating as a bare per-prime
    if/else-skip (fully compliant with PART A's own stated requirement,
    needing no exception handling) has, at that point, built no wrapping the
    accounting assertion's own raise could reuse -- directly falsifying the
    parenthetical's claim that such an Executor's crosscheck_pass
    implementation "necessarily" already provides "the identical wrapping"
    the accounting assertion needs, though the final required artifact is
    unaffected either way.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline remains this
    campaign's own instrument- and spec-scrutiny discipline (GD-4 through
    GD-12, v5's PF-9, v6's own PF-7/PF-8): three successive rounds of
    "trace it, don't trust it" applied to the same two paragraphs (the
    accounting assertion's scope and its illustrative numbers) have now
    exhausted their blocking findings, leaving only a prose-precision gap
    (PF-12) and an unreconciled-but-inert severity asymmetry (PF-13) -- the
    same terminal shape v5's own lineage reached at its round 2 (one small
    blocking item, then freeze-with-fixes), reached here one round later
    with no blocking item at all.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; PF-12/PF-13 are prose-precision and rationale-consistency gaps in diagnostic contract text."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is unchanged and remains realistic; PF-12/PF-13 are both text-only, zero-cost."
    - "No live evidentiary concern remains from PF-7/PF-8 (both confirmed correct this round, independently); PF-12/PF-13 are inert in practice since neither assertion is expected to fire and the required output behavior for both is already unambiguous -- their cost is documentation clarity for a future reader or amendment, not run risk."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded. No scope-inflation found."
    - "funnel_structure_diagnostic_v6's OBJECTIVE_BOUNDARY correctly restates PART B as a diagnostic, not a claim, unchanged since round 1."
    - "This amendment still correctly implements exactly the two resume actions DEC-20260806-357b30's next_actions/resume_action named, on the same four primes, at zero new search cost -- reconfirmed here, unaffected by PF-12/PF-13."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen and a graph-structural diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v6.yaml as read in
    the working tree, status: draft: rounds 1 and 2's five blocking findings
    (PF-1, PF-2, PF-3, PF-7, PF-8) are all genuinely resolved on their own
    stated terms. This round independently re-verifies PF-7's required
    behavior is unambiguous and PF-8's illustrative values are exactly
    correct (33/170, 90/234, 86/392, 91/520 for p=2437/3889/5737/7333), both
    from fresh queries against archived data and fresh code reads, not by
    trusting either prior report's own numbers. PF-10/PF-11 are confirmed
    applied with no gap. No blocking defect survives this round. Two new
    advisory findings (PF-12: the accounting assertion's "same mechanism"
    justification is asserted, not pinned down as concrete code, and is not
    strictly necessary as stated, though required Executor-facing behavior
    is unaffected; PF-13: PART A's and PART B's two structurally analogous,
    both-provably-tautological accounting assertions are assigned different
    failure-handling severities with no stated justification, inert in
    practice but unreconciled) round out this pass. Neither requires
    redesigning either part's mechanism or a further review round; both are
    fixable at zero new search cost.
  next_concrete_action: >-
    Coordinator: this draft may proceed to status: approved / frozen_at once
    PF-12 and PF-13 are applied as text-only additions (removing or
    concretizing the accounting assertion's "same mechanism"
    implementation-necessity claim; adding a one-clause justification, or
    unification, for the PART A/PART B accounting-severity asymmetry) --
    consistent with this lineage's own established practice of applying
    advisory-only findings without a dedicated re-verification round. A
    fourth pass to re-confirm PF-12/PF-13's specific text is available at the
    Coordinator's discretion but is not, on this review's own findings,
    required before freeze.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Programmatically queried RUN-SSIQ-a85692-b/raw-result.json in a fresh
    Python process (not reusing round 2's arithmetic): loaded
    descent_metrics.per_prime[p].greedy_trapped_fraction and
    phase_minus1_real_search[p].n_vertices for all four primes, computed
    n_trapped_false = round((1 - greedy_trapped_fraction) * n_vertices) and
    sum(basin) = n_vertices - n_trapped_false for each, confirming exact
    matches to the draft's stated ILLUSTRATIVE VALUES (33/170, 90/234,
    86/392, 91/520). Read compute_delta_e.py's build_all_graphs (line 242)
    and its call site (line 661, SEEDS[0]=20260805) and
    trapping_diagnostic_v5.py's build_graph_for_prime (lines 133-148) and
    module-level SEED=20260805 (line 90) directly to re-confirm the graph
    and delta_map provenance PF-8's numbers depend on. Traced
    greedy_descent_hitting_time's signature and control flow
    (descent_hitting_time.py lines 179-222) directly against the draft's
    gd12_fix_v6 description for continued consistency. Grepped the entire
    current specification_v6.yaml for n_resolved/n_vertices to confirm no
    recurrence of v5's own PF-9 field-conflation defect. Cross-read every
    pfN_summary entry against its corresponding operative clause in
    gd12_fix_v6/funnel_structure_diagnostic_v6 for consistency. No graph
    built, no delta_E search run, no file written outside this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml
    itself), the round-1 and round-2 reports, and every ledger record are
    untouched.
  verdict: FREEZE-WITH-FIXES
```
