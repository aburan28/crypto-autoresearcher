# RT-PREFREEZE-EXP-SSIQ-a85692-v8-ROUND2 — Round 2 pre-freeze Red Team
# review of the DRAFT amendment `specification_v8.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-011, task `TASK-20260806-c1c8ef`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v8.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED` (round 1, DO-NOT-FREEZE),
a working-tree draft not yet frozen.** Per this task's operating rules, only a
Coordinator-committed snapshot of a *frozen* artifact is treated as durable
research evidence; this is advisory pre-freeze input. It changes nothing under
`experiments/EXP-SSIQ-a85692/` and commits nothing.

**This is a genuinely independent re-trace, not a rubber-stamp of round 1's
report or the draft's own "FIX APPLIED" annotations.** Every blocking finding
below was re-derived directly from the current v8 text and the actual code it
imports; round 1's report (`RT-PREFREEZE-EXP-SSIQ-a85692-v8.md`) was read only
to know what round 1 claimed, never trusted as already-correct.

Read in full: `AGENTS.md`, `agents/red-team.md`, `RT-PREFREEZE-EXP-SSIQ-a85692-v8.md`
(round 1); `specification_v8.yaml` (current, 452 lines) in full, twice —
once for the round-1-fix re-trace, once fresh for new defects. Directly read
(not trusted from prose): `RUN-SSIQ-a85692-b/manifest.yaml`, `command.txt`
(both in full, this session, independent of round 1's own citations of them);
`compute_delta_e.py`'s `run_phase_minus1_on_confirmatory_set`,
`two_sided_search`, `build_smooth_table` (lines 130–419, in full);
`compute_delta_e_v2.py` in full (`real_execution_budget_v2` =
`run_phase_minus1_on_confirmatory_set`, `estimate_per_prime_cost_v2`,
`apply_truncation_fallback`, `main`); `delta_e_permutation_null_control_v7.py`
in full (`local_min_and_depth`, `depth0_fraction`, `rebuild_and_verify`,
`run_for_prime`); `build_isogeny_graph.py`'s `Fp2Field.is_in_fp`.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified this session.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. Every credentialed
    backend under this environment has previously been found unprobeable in
    this campaign's prior reviews, recorded as the standing condition, not
    re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Shares a model family
    with the Executor, the Coordinator, round 1's own reviewer, and every
    prior reviewer in this lineage. Does not upgrade the campaign's evidence
    tier and does not itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**This draft should STILL NOT be frozen as written.** Round 1's two blocking
findings are genuinely, correctly fixed — PF-1's coverage gate and PF-2's
citation correction both hold up under independent re-trace against the
actual code and the actual archived manifest/command.txt. PF-3 and PF-6's
advisory fixes are also sound. But fixing PF-1 introduced a **new, unguarded
crash path of the identical shape and severity**: the coverage gate PF-1
added checks coverage **only over the 194 non-F_p-rational vertices**, while
`depth0_fraction` (PART B's very first call, imported unchanged) iterates
over the **full 203-vertex domain** for p=2437 — the 9 F_p-rational vertices
included. The draft never states, as an explicit construction step, that
PART A's new `delta_map` actually contains entries for those 9 vertices; it
only asserts, in a parenthetical aside, that they "resolve for free... IDENTICAL
to the original procedure," without wiring that claim into code the way this
draft precisely wires every other formula (the seed-derivation formula, the
budget arithmetic, the PERSISTS/WEAKENS thresholds). If an Executor
implements PART A literally as scoped — a loop over `is_in_fp(v) False`
vertices only, recording results only for those — the resulting `delta_map`
is missing 9 entries even at `coverage_fraction == 1.0`, and `depth0_fraction`
crashes on the very first of those 9 vertices with an uncaught `KeyError`,
exactly reproducing round 1's PF-1 failure mode through a path the new gate
does not check at all.

1. **PF-9 [NEW, BLOCKING, compute-loss risk].** See full trace below. The
   coverage gate's sole criterion, `coverage_fraction (== n_resolved /
   n_non_fp_rational)`, is by definition blind to the F_p-rational subset of
   `graph["vertices"]`. `depth0_fraction`'s domain (`vertices`, passed as
   `g["vertices"]`, confirmed by v7's own `rebuild_and_verify` returning the
   *full* rebuilt vertex set, and by the draft's own text reusing "the SAME
   p=2437 graph... not rebuilt twice") is the full 203-vertex set, not the
   194-vertex non-F_p-rational subset. p=2437's own archived data
   (`ARCHIVED_N_VERTICES[2437] = 203`, `non_fp_rational_vertex_counts_by_prime[2437]
   = 194`, both confirmed directly against `RUN-SSIQ-a85692-b/manifest.yaml`)
   has exactly 9 F_p-rational vertices. These are not a marginal corner of
   the metric either: every `delta_e=1` vertex is *trivially* a structural
   local minimum at depth 0 (no value can be smaller than 1 given the
   search's own upper-bound semantics), so the F_p-rational vertices are a
   substantial, structurally-guaranteed contributor to `n_local_min` and
   `n_depth0` in both the real and archived REAL_DEPTH0_FRACTION figures
   (consistent with `EXPECTED_REAL_N_LOCAL_MIN[2437] = 95` in
   `delta_e_permutation_null_control_v7.py`, well above the 9 identity
   vertices alone, meaning several non-F_p-rational vertices also resolve to
   1 — but the 9 are unconditionally always present). **Required fix**
   (two parts, both zero additional search cost, matching this lineage's own
   PF-1/PF-2 standard of a precise code-level fix, not a prose reassurance):
   (a) state explicitly, as a numbered construction step (not a parenthetical
   aside), that `run_probe_delta_e_search_v8` builds `new_delta_map` by first
   setting `new_delta_map[v] = 1` for every `v` with `field.is_in_fp(v)`
   True — the identical step `compute_delta_e_v2.run_phase_minus1_on_confirmatory_set`
   itself performs (confirmed at `compute_delta_e_v2.py:259-261`,
   `for v in g["vertices"]: if field.is_in_fp(v): delta_map[v] = 1`) — before
   or alongside the non-F_p-rational search loop; (b) strengthen the gate
   itself so it does not rely solely on `coverage_fraction` (a non-F_p-only
   quantity that cannot detect a missing F_p-rational entry): require
   `len(new_delta_map) == len(g["vertices"])` (203 for p=2437) as an
   additional, explicit precondition for PART B to proceed — mirroring v7's
   own `rebuild_and_verify` coverage assertion, which checks key-membership
   against the *full* rebuilt vertex set, not a subset. Without (b), a latent
   bug in the F_p-rational construction step would still slip past a gate
   that only counts non-F_p resolutions.

Two further findings are advisory (do not block freeze by themselves but
should be applied given real compute is at stake):

2. **PF-10 [ADVISORY].** The "margin" that gates PERSISTS/WEAKENS (0.95
   fraction floor, 13.1pp margin floor) is never restated as an explicit
   formula in v8 itself (contrast: the seed-derivation formula, the 10x/12.6x
   budget arithmetic, and the exact PERSISTS/WEAKENS boolean conditions are
   all spelled out precisely). The draft relies on the reader inferring
   "margin" = `(new REAL_DEPTH0_FRACTION − max(new NULL_DEPTH0_FRACTIONS)) ×
   100`, by analogy to how v7's own archived 23.1pp figure was derived (per
   `EV-SSIQ-a64d92 O-2`) and by the fact that `summary_stats` (imported
   unchanged) returns a `max` field. This is very likely the intended
   reading and is not itself ambiguous once traced, but it is a lower
   standard of explicitness than the rest of this draft holds itself to, and
   this exact class of gap (an intended-but-unstated construction/formula)
   is what produced PF-9 above. Low-cost fix: state the formula once,
   explicitly, next to the 0.95/13.1 thresholds.

3. **PF-11 [ADVISORY].** The COVERAGE-SHORTFALL branch text states it is
   "NOT one of PF-6's three interpretive outcomes" but does not explicitly
   restate PF-4's own disclosure (that a completed test's discriminating
   power concentrates in the RNG-sharing half of PF-6's confound, since the
   budget-shrinking half was very likely non-binding in the archived
   baseline). This omission does not create ambiguity — COVERAGE-SHORTFALL
   already excludes PERSISTS/WEAKENS by construction, so no reader could
   mistake a shortfall for a test of either confound-half — but for a
   record that will be read on its own, one sentence noting "under
   COVERAGE-SHORTFALL, neither half of PF-6's confound was tested this run"
   would remove any need for a future reader to re-derive that from context.

4. **PF-1 [round 1, BLOCKING] — RE-VERIFIED, CONFIRMED HOLDING for the case
   it addresses.** Direct re-trace: the gate text
   (`inputs.probe_permutation_null_control_v8`, "REQUIRED GATE: if PART A's
   coverage_fraction < 1.0... PART B DOES NOT RUN AT ALL") correctly and
   unambiguously prevents PART B from running when any of the 194
   non-F_p-rational vertices is unresolved, and `required_artifacts_note`'s
   own "REQUIRED_ARTIFACTS SCOPE UNDER PF-1's COVERAGE GATE" paragraph is
   airtight on what gets written in that case — "ONLY the COVERAGE-SHORTFALL
   record... never omitted, never a partial or silently-truncated PART B
   result" leaves no room for an Executor to read the "ALWAYS written"
   instruction as license to write a partial PART B result; the two
   sentences are explicitly conjoined ("if the gate does NOT pass, it
   contains ONLY... never a partial..."). This closes the *specific* crash
   PF-1 named (an unresolved non-F_p-rational vertex under the fixed-15s
   search). It does **not** close PF-9's crash (a missing F_p-rational
   entry), which is a distinct vertex subset the gate's own criterion cannot
   see — see PF-9 above; this is why PF-1's fix is correct as far as it
   goes but the overall gate is not yet airtight.

5. **PF-2 [round 1, BLOCKING] — RE-VERIFIED, CONFIRMED HOLDING,
   INDEPENDENTLY.** I read `RUN-SSIQ-a85692-b/manifest.yaml` and
   `command.txt` directly this session (not via round 1's citations) and
   confirm: the command actually run was `python3
   experiments/EXP-SSIQ-a85692/implementation/compute_delta_e_v2.py --out
   .../RUN-SSIQ-a85692-b/raw-result.json`, and the manifest's own
   `validity_reason` names `real_execution_budget_v2` as the mechanism that
   produced the p=2437 delta_map. I additionally read
   `compute_delta_e_v2.py`'s `run_phase_minus1_on_confirmatory_set` in full
   (lines 212–296) and confirmed it is `real_execution_budget_v2`: a single
   aggregate cross-prime `remaining` counter threaded across primes in
   ascending order, no `t_prime`/`min()` per-prime cap anywhere — materially
   different from v1's `compute_delta_e.py:370-419`
   (`per_vertex_cap = min(remaining, t_prime)`, a fixed per-prime sub-budget,
   confirmed present verbatim). I then greped every live occurrence of
   "ORIGINAL procedure" / `compute_delta_e.py` / `compute_delta_e_v2.py` in
   the current `specification_v8.yaml` (lines 34, 39–49, 76, 96,
   155–157/176–184 inside the `pre_freeze_review` history block, 399–411 in
   `required_artifacts_note`): every operative citation (i.e. everywhere
   except the `pre_freeze_review.verdict`/`*_summary` fields, which are
   correctly recounting round 1's *history*, not making a fresh claim)
   correctly names `compute_delta_e_v2.py`'s `real_execution_budget_v2` as
   the actual originating procedure, and the budget-margin arithmetic
   (line 96) is derived against it. No stale citation to v1's
   `compute_delta_e.py` as "the ORIGINAL procedure" survives anywhere in the
   live spec text. PF-2 is fixed consistently throughout, not merely at the
   first occurrence.

6. **PF-3 [round 1, ADVISORY] — RE-VERIFIED, ADEQUATE.** The draft now
   requires "the Executor MUST launch this run's command detached via the
   identical setsid/nohup/disown pattern RUN-SSIQ-a85692-b's own
   `command.txt` documents, proactively." This is actionable, not merely
   vague reassurance: it names the exact precedent artifact
   (`RUN-SSIQ-a85692-b/command.txt`), which I read directly and confirms it
   contains a complete, literal, copy-pasteable shell template (`setsid
   nohup bash -c '...' < /dev/null > /dev/null 2>&1 & disown -a`) an
   Executor unfamiliar with the workaround can follow exactly. This matches
   the convention this draft already uses elsewhere for reused code (point
   at the exact artifact rather than re-transcribe it). Minor,
   non-blocking suggestion: inlining the literal command in v8 itself would
   remove one hop of indirection, but pointing at a real, already-verified
   artifact is an acceptable and consistent level of precision for an
   operational (not mathematical) instruction.

7. **PF-6 [round 1, ADVISORY] — RE-VERIFIED, CLEAN BINARY PARTITION,
   CONFIRMED.** PERSISTS := `fraction >= 0.95 AND margin >= 13.1`; WEAKENS
   := `fraction < 0.95 OR margin < 13.1`. This is the exact De Morgan
   negation of PERSISTS's condition, so PERSISTS and WEAKENS partition every
   `(fraction, margin)` pair with no gap and no double-coverage by
   construction — re-derived independently, not merely re-read. Boundary
   values checked explicitly: `fraction = 0.95` alone is on the PERSISTS
   side of its own condition (`>=`); `margin = 13.1` alone is likewise on the
   PERSISTS side; the pair `(0.95, 13.1)` exactly satisfies PERSISTS; the
   pair `(0.95, 13.099...)` falls to WEAKENS (margin `< 13.1`); the pair
   `(0.9499..., 20)` falls to WEAKENS (fraction `< 0.95`). AMBIGUOUS is
   correctly retained only as a disclosed non-branch for a genuinely
   unanticipated numeric anomaly (e.g. a NaN or undefined fraction), not as
   a reachable branch of the ordinary partition. This closes round 1's named
   gap (a stronger-than-archived margin defaulting to AMBIGUOUS) cleanly.

---

## (1) Is PF-1's coverage gate airtight end-to-end, or does it leave a path
for PART B to run on incomplete data? [task question 1]

**No — see PF-9.** The gate is airtight for the *specific* incompleteness it
was written to catch (an unresolved non-F_p-rational vertex under the new
fixed-15s search) but not for a structurally distinct and unconditionally
present incompleteness: the 9 F_p-rational vertices at p=2437, which the
`coverage_fraction` criterion cannot see by construction (its own denominator
is `n_non_fp_rational`), but which `depth0_fraction`'s domain (the full
`g["vertices"]`) requires. The `required_artifacts_note`'s "ALWAYS written"
instruction is not itself ambiguous or exploitable as a license to write a
partial PART B result (traced above, PF-1 re-verification) — the actual risk
is upstream of that instruction, in whether `new_delta_map` is complete at
all when the gate reports `coverage_fraction == 1.0`.

## (2) Is PF-2's citation fix accurate and applied consistently everywhere?
[task question 2]

**Yes, independently re-verified against the primary sources, not round 1's
report.** See finding 5 above: direct read of `RUN-SSIQ-a85692-b/manifest.yaml`
and `command.txt`, direct read of `compute_delta_e_v2.py`'s
`real_execution_budget_v2` function body, and a full grep of every "ORIGINAL
procedure" occurrence in the current spec text, all confirm the citation is
now correct and applied uniformly.

## (3) Is PF-3's detached-launch instruction actionable? [task question 3]

**Yes.** See finding 6. It names an exact, directly-verified precedent
artifact containing a complete literal command template.

## (4) Is PF-6's PERSISTS/WEAKENS partition clean, exhaustive, and
non-overlapping, including at the stated boundary values? [task question 4]

**Yes.** See finding 7. Independently re-derived as an exact De Morgan
negation; boundary values at fraction=0.95 and margin=13.1 checked
explicitly and land correctly on the PERSISTS side.

## (5) Any new defect from this round's revision, and do the accumulated
fixes compose cleanly? [task question 5]

**One new blocking defect (PF-9), one minor precision gap (PF-10), one minor
disclosure-completeness gap (PF-11).** PF-9 is a direct, mechanical
consequence of PF-1's fix: narrowing the crash-prevention gate to exactly the
incompleteness PF-1's counterexample named (a partial non-F_p-rational
search) left the adjacent, always-present F_p-rational subset unguarded,
because that subset was never part of what `coverage_fraction` measures. This
is exactly the composition risk the task asked about: PF-1's fix is locally
correct but was not re-checked against the *full* domain `depth0_fraction`
actually operates over. PF-4's own disclosure (COVERAGE-SHORTFALL means
neither confound-half was tested) composes correctly with PF-1's gate in
substance (PF-11 notes only a missing restatement, not a logical gap).

## (6) Final sanity pass: any remaining path to wasting the real compute
budget? [task question 6]

**Yes — PF-9 is exactly such a path, and it is the only one found beyond what
PF-1/PF-2/PF-3 already close.** As specified, if `run_probe_delta_e_search_v8`
is implemented literally as scoped (loop and record only over
`is_in_fp(v) False` vertices), PART A can spend up to its full worst-case
2910s of search time, resolve all 194 non-F_p-rational vertices
(`coverage_fraction == 1.0`), pass PF-1's gate, and then crash on PART B's
very first `depth0_fraction` call on one of the 9 unrecorded F_p-rational
vertices — discarding the entire real-compute spend for zero interpretable
result, the identical failure mode PF-1 was written to prevent. No other new
path to wasting the budget was found: the delta_E search instrument itself
(`two_sided_search`/`build_smooth_table`) is confirmed bounded and
non-raising (checks `time_budget_seconds` every heap-pop, returns
`resolved: False` on timeout rather than raising); the 2910s worst-case
search bound is correctly derived and cannot itself exceed the 3600s cap; the
infrastructure kill-window risk (PF-3) is now covered by an actionable
instruction; and the graph-identity check (PF-8, re-verified present) runs
before any search compute is spent, so a graph-rebuild mismatch would abort
cheaply rather than after the expensive search.

---

## Objections

- **OBJ-9 [PF-9, NEW, BLOCKING]:** PF-1's coverage gate checks
  `coverage_fraction`, defined only over the 194 non-F_p-rational vertices,
  but `depth0_fraction` (PART B's first call) iterates the full 203-vertex
  domain for p=2437. The draft never states, as a wired construction step,
  that PART A's `new_delta_map` includes the 9 F_p-rational identity
  entries (`delta_e=1`) — only a parenthetical aside claims this "IDENTICAL
  to the original procedure," unlike every other precisely-wired formula in
  this draft. A literal implementation of PART A's stated scope (loop only
  over `is_in_fp(v) False`) produces a `new_delta_map` missing those 9
  entries even at `coverage_fraction == 1.0`, and `depth0_fraction` crashes
  with an uncaught `KeyError` on the first such vertex — the same
  catastrophic zero-result failure PF-1 was written to prevent, via a path
  PF-1's gate cannot detect.
- **OBJ-10 [PF-10, ADVISORY]:** The "margin" used in the PERSISTS/WEAKENS
  test is never restated as an explicit formula in v8, unlike every other
  quantity this draft precisely specifies; the intended reading (REAL minus
  the new run's own null-distribution max) is inferable but not stated.
- **OBJ-11 [PF-11, ADVISORY]:** The COVERAGE-SHORTFALL branch does not
  explicitly restate that neither half of PF-6's named confound (RNG-sharing,
  budget-shrinking) is resolved by a shortfall outcome; not ambiguous given
  COVERAGE-SHORTFALL's exclusion from PERSISTS/WEAKENS, but a one-sentence
  restatement would remove any need to re-derive this.
- **OBJ-1 [PF-1, round 1] — RE-CONFIRMED HOLDING** for the specific
  incompleteness it addresses (see finding 4).
- **OBJ-2 [PF-2, round 1] — RE-CONFIRMED HOLDING**, verified independently
  against primary sources this round (see finding 5).
- **OBJ-3 [PF-3, round 1] — RE-CONFIRMED ADEQUATE** (see finding 6).
- **OBJ-6 [PF-6, round 1] — RE-CONFIRMED CLEAN PARTITION** (see finding 7).

## Required controls

- Before freeze: PF-9 must be resolved — (a) state explicitly, as a
  construction step, that `new_delta_map[v] = 1` for every F_p-rational `v`
  is set before or alongside the non-F_p-rational search loop; (b) add
  `len(new_delta_map) == len(g["vertices"])` as an explicit, additional
  precondition for PART B to proceed, not merely `coverage_fraction == 1.0`.
- Strongly recommended before freeze (PF-10): state the margin formula
  explicitly next to the 0.95/13.1 thresholds.
- Recommended, zero cost (PF-11): add one sentence to the COVERAGE-SHORTFALL
  branch noting neither confound-half was tested under that outcome.

## Counterexample or mutation

**PF-9's counterexample, concretely constructible, no adversarial input
needed:** implement `run_probe_delta_e_search_v8` exactly as PART A's text
scopes it — `for v in graph["vertices"]: if not field.is_in_fp(v): ...
search...` — recording results (and hence populating `new_delta_map`) only
inside that conditional body. Run it: all 194 non-F_p-rational vertices at
p=2437 resolve within their fixed 15s budgets (plausible given the 10x
margin over the measured average), so `coverage_fraction = 194/194 = 1.0`
and PF-1's gate reports PASS. PART B's driver then calls
`depth0_fraction(new_delta_map, g["vertices"], g["adjacency"])`. The loop
`for v in vertices` reaches the first of the 9 F_p-rational vertices (not in
`new_delta_map`, since the loop that populated it explicitly excluded
`is_in_fp(v) True`), and `local_min_and_depth`'s `delta_map[v] <= m`
evaluation raises an uncaught `KeyError` on the vertex itself — the same
failure PF-1's counterexample described, now surviving PF-1's own gate.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
statistical-control work, `asymptotic_claim: null` throughout, unchanged.
The relevant baseline is this lineage's own established specification
discipline (v6/v7's PF-1/PF-2/PF-3/PF-7 standard, and round 1's own
code-verified-crash-path standard for this very amendment): PF-9 is found by
applying that identical standard one level deeper — tracing not just whether
the fix as written is internally consistent, but whether it actually covers
every vertex `depth0_fraction`'s own signature requires, not only the subset
the original counterexample happened to name.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, unchanged from round 1. No numbered heuristic is
implicated; `asymptotic_claim: null` throughout.

## Cost model challenges

The budget arithmetic re-verified in round 1 (10x/12.6x margins, 2910s
worst-case search bound) is unaffected by PF-9 — PF-9 is a correctness/crash
risk, not a cost-model error, and does not change any figure in the budget
note. What PF-9 changes is the probability that the *entire* budget is spent
for zero interpretable result: PF-1's fix was specifically supposed to drive
that probability to zero for any coverage outcome, and it does not yet do so
for the F_p-rational subset. Total expected cost, accounting honestly for
this risk, is not simply the 3600s cap × 1 attempt — it is (probability the
implementation happens to include F_p-rational entries correctly despite the
spec's own silence on the point) × 3600s, plus (probability it does not) ×
(time-to-crash, likely small, but zero interpretable result either way).
This is exactly the "total expected cost, never per-attempt cost alone"
discipline this campaign requires, and it is currently undefined because the
draft does not pin down which of the two behaviors an Executor will
implement.

## Reduction and scope challenges

No scheme from any affected-vs-safe list appears anywhere in this amendment;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated and not
exceeded, unchanged from round 1. `OBJECTIVE_BOUNDARY` still correctly scopes
a PERSISTS result to "THIS ONE PRIME ONLY." No scope inflation found this
round either.

## Proof architecture challenges

Not applicable — direct instrument-level statistical/search-procedure
control, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited unchanged,
attacked and held, unchanged from round 1).

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v8.yaml` as it currently
stands (draft, not yet frozen, post-round-1-revision): round 1's two
blocking findings (PF-1, PF-2) are correctly and consistently fixed, verified
here independently against the actual code and the actual archived
manifest/command.txt rather than trusted from round 1's own report; round
1's advisory findings PF-3 and PF-6 are also correctly and adequately
applied. However, PF-1's fix, while correct for the exact incompleteness its
own counterexample named, does not extend to a structurally adjacent and
unconditionally-present incompleteness — the 9 F_p-rational vertices at
p=2437, which `coverage_fraction` cannot detect and which the draft never
wires into `new_delta_map`'s construction as an explicit step. This
reproduces PF-1's original catastrophic failure mode (an uncaught crash on
PART B's first call, discarding the entire real-compute spend for zero
result) through a path PF-1's own gate does not check. This is a
specification/wiring fix at zero additional search cost, exactly like PF-1
and PF-2 were, and should be applied with the same priority.

## Next concrete action

Coordinator: return this draft for one further revision round applying PF-9
(state the F_p-rational identity-vertex construction step explicitly, and
strengthen the gate to check `len(new_delta_map) == len(g["vertices"])`, not
only `coverage_fraction`), plus PF-10 (state the margin formula explicitly)
and PF-11 (one-sentence COVERAGE-SHORTFALL disclosure) in the same pass. Do
not dispatch the Executor until PF-9 is resolved: as specified, there is
still a directly constructible input (a literal, spec-compliant
implementation of PART A's own stated scope) that spends up to the full
3600s real-compute budget and crashes before writing any interpretable PART B
result — the exact outcome round 1's PF-1 finding was raised to prevent.

## Overall verdict

**DO-NOT-FREEZE.** Round 1's two blocking findings (PF-1, PF-2) are
correctly and consistently fixed, independently re-verified against primary
sources this round; PF-3 and PF-6's advisory fixes are also sound. But one
new blocking finding (PF-9) was found by this round's independent re-trace:
PF-1's coverage gate, though airtight for the specific vertex subset its own
counterexample named, does not cover the F_p-rational vertex subset that
`depth0_fraction`'s actual domain requires, and the draft never wires the
construction of those entries into `new_delta_map` as an explicit step. This
reproduces the identical catastrophic failure mode (up to 3600s of real
compute spent for zero interpretable result) PF-1 was written to close, via
an adjacent, unguarded path. Given this remains the first amendment since v4
to spend real, non-recoverable compute, PF-9 should be treated as
dispatch-blocking with the same priority PF-1 received in round 1. Two
further advisory findings (PF-10, PF-11) should be applied in the same
revision pass.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v8-round2
  task_id: TASK-20260806-c1c8ef
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v8.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: REVIEWED, round 1
    verdict DO-NOT-FREEZE with PF-1/PF-2 blocking, both marked FIX APPLIED in
    the current draft text) -- round 2 independent re-trace of round 1's
    seven applied findings (PF-1 through PF-8) plus a fresh, skeptical
    full-document pass for new defects, given this remains the first
    amendment since specification_v4.yaml to spend real, non-recoverable
    delta_E search compute (up to 1 CPU-hour).
  objections:
    - "OBJ-9 [PF-9, NEW, BLOCKING]: PF-1's coverage gate checks coverage_fraction, defined only over the 194 non-F_p-rational vertices at p=2437, but depth0_fraction (PART B's first call, imported unchanged) iterates the FULL 203-vertex domain (g['vertices'], the same graph PART A rebuilt, reused not rebuilt twice). The draft never states, as a wired construction step, that PART A's new_delta_map includes the 9 F_p-rational identity entries (delta_e=1) -- only a parenthetical aside claims this is 'IDENTICAL to the original procedure', unlike every other precisely-wired formula in this draft (the seed-derivation formula, the budget arithmetic, the PERSISTS/WEAKENS thresholds). Direct read of compute_delta_e_v2.py:259-261 confirms the ORIGINAL procedure performs this as an explicit code step (for v in g['vertices']: if field.is_in_fp(v): delta_map[v] = 1) that this draft's prose never restates as a requirement. A literal implementation of PART A's own stated scope (loop only over is_in_fp(v) False) produces a new_delta_map missing those 9 entries even at coverage_fraction == 1.0, and depth0_fraction crashes with an uncaught KeyError on the first such vertex -- the identical catastrophic zero-result failure PF-1 was written to prevent, via a path PF-1's own gate cannot detect. These 9 vertices are not a marginal edge case: delta_e=1 vertices are unconditionally structural local minima at depth 0 (no value can be smaller than 1), and are a substantial contributor to REAL_DEPTH0_FRACTION's own n_local_min/n_depth0 counts (consistent with EXPECTED_REAL_N_LOCAL_MIN[2437]=95 in delta_e_permutation_null_control_v7.py, well above 9 alone)."
    - "OBJ-10 [PF-10, ADVISORY]: The 'margin' used in the PERSISTS (>=13.1pp)/WEAKENS (<13.1pp) test is never restated as an explicit formula anywhere in v8, unlike every other precisely-specified quantity in this draft. The intended reading (new REAL_DEPTH0_FRACTION minus the new run's own 1000-trial null distribution's max, by analogy to how v7's own archived 23.1pp figure was derived per EV-SSIQ-a64d92 O-2, and using the max field summary_stats already returns) is inferable but not stated as a formula."
    - "OBJ-11 [PF-11, ADVISORY]: The COVERAGE-SHORTFALL branch does not explicitly restate that neither half of PF-6's named confound (RNG-sharing, budget-shrinking) is resolved by a shortfall outcome. Not ambiguous, since COVERAGE-SHORTFALL is already explicitly excluded from PERSISTS/WEAKENS/AMBIGUOUS, but a one-sentence restatement would remove any need for a future reader to re-derive this from context."
    - "OBJ-1 [PF-1, round 1, RE-CONFIRMED HOLDING for the specific incompleteness it addresses]: Direct re-trace of the current draft's gate text and required_artifacts_note's 'REQUIRED_ARTIFACTS SCOPE UNDER PF-1's COVERAGE GATE' paragraph confirms it is airtight against an Executor reading the 'ALWAYS written' instruction as license to write a partial PART B result -- the two clauses are explicitly conjoined ('if the gate does NOT pass, it contains ONLY... never a partial...'). This closes the exact crash PF-1's own counterexample named. It does not close PF-9's distinct crash path (see OBJ-9)."
    - "OBJ-2 [PF-2, round 1, RE-CONFIRMED HOLDING, independently]: This round directly read RUN-SSIQ-a85692-b/manifest.yaml and command.txt (not via round 1's citations) and confirmed the archived p=2437 data was produced by compute_delta_e_v2.py's real_execution_budget_v2 (compute_delta_e_v2.py:212-296, a single aggregate cross-prime counter, no t_prime), materially different from v1's compute_delta_e.py:370-419 (per_vertex_cap = min(remaining, t_prime), confirmed present verbatim). A full grep of every live 'ORIGINAL procedure'/compute_delta_e.py/compute_delta_e_v2.py occurrence in the current specification_v8.yaml (lines 34, 39-49, 76, 96, 399-411) confirms every operative citation now correctly names compute_delta_e_v2.py throughout, with no stale v1 citation surviving anywhere outside the pre_freeze_review history block (which correctly recounts round 1's history, not a fresh claim)."
    - "OBJ-3 [PF-3, round 1, RE-CONFIRMED ADEQUATE]: The detached-launch requirement names the exact precedent artifact (RUN-SSIQ-a85692-b/command.txt), read directly this round and confirmed to contain a complete, literal, copy-pasteable setsid/nohup/disown shell template an Executor unfamiliar with the workaround can follow exactly."
    - "OBJ-6 [PF-6, round 1, RE-CONFIRMED CLEAN BINARY PARTITION]: PERSISTS (fraction>=0.95 AND margin>=13.1) and WEAKENS (fraction<0.95 OR margin<13.1) are the exact De Morgan negation of each other, independently re-derived (not merely re-read) to partition every (fraction, margin) pair with no gap and no double-coverage. Boundary values explicitly checked: fraction=0.95 alone and margin=13.1 alone both land on PERSISTS's own >= side; the pair (0.95, 13.1) exactly satisfies PERSISTS; (0.95, 13.099...) and (0.9499..., 20) both correctly fall to WEAKENS."
  required_controls:
    - "PF-9 [BLOCKING]: (a) state explicitly, as a numbered construction step (not a parenthetical aside), that run_probe_delta_e_search_v8 sets new_delta_map[v] = 1 for every F_p-rational vertex v before or alongside the non-F_p-rational search loop -- the identical step compute_delta_e_v2.py's real_execution_budget_v2 itself performs (confirmed at compute_delta_e_v2.py:259-261); (b) strengthen PART B's gate to additionally require len(new_delta_map) == len(g['vertices']) (203 for p=2437), not solely coverage_fraction (which is defined only over the 194-vertex non-F_p-rational subset and cannot detect a missing F_p-rational entry), mirroring v7's own rebuild_and_verify coverage assertion which checks key-membership against the FULL rebuilt vertex set."
    - "PF-10 [ADVISORY, strongly recommended before freeze]: state the margin formula (new REAL_DEPTH0_FRACTION minus the new run's own null-distribution max, times 100) explicitly next to the 0.95/13.1 thresholds, rather than leaving it to be inferred by analogy to v7's archived figure."
    - "PF-11 [ADVISORY, zero cost]: add one sentence to the COVERAGE-SHORTFALL branch stating that neither half of PF-6's named confound is resolved by that outcome."
  counterexample_or_mutation: >-
    PF-9's counterexample, directly constructible from the draft's own
    stated scope, not an adversarial input: implement run_probe_delta_e_search_v8
    exactly as PART A's text scopes it -- "for v in graph['vertices']: if not
    field.is_in_fp(v): ...search..." -- recording results, and hence
    populating new_delta_map, only inside that conditional body. Run it: all
    194 non-F_p-rational vertices at p=2437 resolve within their fixed 15s
    budgets (plausible given the 10x margin over the measured 1.47s/vertex
    average), so coverage_fraction = 194/194 = 1.0 and PF-1's gate reports
    PASS. PART B's driver then calls depth0_fraction(new_delta_map,
    g["vertices"], g["adjacency"]). The loop for v in vertices reaches the
    first of the 9 F_p-rational vertices (never inserted into new_delta_map,
    since the loop that populated it explicitly excluded is_in_fp(v) True),
    and local_min_and_depth's delta_map[v] <= m evaluation raises an
    uncaught KeyError on the vertex itself, before any of the 1000 null
    trials run.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale statistical/search-procedure control work, asymptotic_claim
    null throughout, unchanged from round 1. The relevant baseline is this
    lineage's own code-verified-crash-path standard, applied here one level
    deeper than round 1 applied it: tracing not only whether PF-1's fix is
    internally consistent with its own stated counterexample, but whether it
    actually covers every vertex depth0_fraction's own signature requires.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional complexity claim) -- attacked and held, unchanged from round 1. asymptotic_claim: null throughout."
  cost_model_challenges:
    - "PF-9 does not change any figure in the round-1-verified budget arithmetic (10x/12.6x margins, 2910s worst-case search bound), which remains correct. What it changes is the probability the ENTIRE 3600s budget is spent for zero interpretable result: PF-1's fix was meant to drive that probability to zero for any coverage outcome, and as specified it does not, for the F_p-rational vertex subset. Total expected cost -- per-attempt cost times inverse success probability, never per-attempt cost alone -- is currently undefined by the draft, because the draft's own silence on whether new_delta_map's construction includes F_p-rational entries leaves the implementation's crash probability unpinned."
  reduction_and_scope_challenges:
    - "No scheme from any affected-vs-safe list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded, unchanged from round 1."
    - "OBJECTIVE_BOUNDARY still correctly scopes a PERSISTS result to THIS ONE PRIME ONLY; no scope inflation found this round."
  proof_architecture_challenges:
    - "Not applicable -- direct instrument-level statistical/search-procedure control, not a proof-oriented proposal (H-SSIQ-36e970.proof_search_map.not_applicable_reason, inherited unchanged, attacked and held, unchanged from round 1)."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v8.yaml as it
    currently stands (draft, not yet frozen, post-round-1-revision): round
    1's two blocking findings (PF-1, PF-2) are correctly and consistently
    fixed, independently re-verified against the actual code and the actual
    archived manifest.yaml/command.txt rather than trusted from round 1's own
    report; round 1's advisory findings PF-3 and PF-6 are also correctly and
    adequately applied. However, PF-1's fix, while correct for the exact
    incompleteness its own counterexample named, does not extend to a
    structurally adjacent and unconditionally-present incompleteness -- the
    9 F_p-rational vertices at p=2437, which coverage_fraction cannot detect
    and which the draft never wires into new_delta_map's construction as an
    explicit step. This reproduces PF-1's original catastrophic failure mode
    through a path PF-1's own gate does not check. This is a
    specification/wiring fix at zero additional search cost, exactly like
    PF-1 and PF-2 were, and should be applied with the same priority before
    this draft is frozen or dispatched.
  next_concrete_action: >-
    Coordinator: return this draft for one further revision round applying
    PF-9 (state the F_p-rational identity-vertex construction step
    explicitly, and strengthen the gate to check len(new_delta_map) ==
    len(g["vertices"]), not only coverage_fraction), plus PF-10 (state the
    margin formula explicitly) and PF-11 (one-sentence COVERAGE-SHORTFALL
    disclosure) in the same pass. Do not dispatch the Executor until PF-9 is
    resolved: as specified, there is still a directly constructible input (a
    literal, spec-compliant implementation of PART A's own stated scope)
    that spends up to the full 3600s real-compute budget and crashes before
    writing any interpretable PART B result.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no permutation trial executed --
    this review is a specification and implementation trace, not an
    execution. Directly read this session (not trusted from round 1's
    report): specification_v8.yaml in full (twice, once per fix, once fresh
    for new defects); RUN-SSIQ-a85692-b/manifest.yaml and command.txt in
    full; compute_delta_e.py lines 130-419 (two_sided_search,
    build_smooth_table, run_phase_minus1_on_confirmatory_set) in full;
    compute_delta_e_v2.py in full (real_execution_budget_v2,
    estimate_per_prime_cost_v2, apply_truncation_fallback, main);
    delta_e_permutation_null_control_v7.py in full (local_min_and_depth,
    depth0_fraction, rebuild_and_verify, run_for_prime); build_isogeny_graph.py's
    Fp2Field.is_in_fp. Independently re-derived the PERSISTS/WEAKENS boolean
    partition as an exact De Morgan negation and checked its boundary values
    by hand. No file written outside this report; no run artifact,
    specification file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v8.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
