# RT-PREFREEZE-EXP-SSIQ-a85692 — Pre-freeze Red Team review of the draft contract
# EXP-SSIQ-a85692 (H-SSIQ-9e2c71), GOAL-SSIQ-001 BATCH-004

**Task:** `TASK-20260805-40ad8c` (minted this session; no prior task id existed for
this review — `coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/` did not exist
before this task) · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-004`
**Role:** red-team, pre-freeze. **Reviews a `status: draft` contract. Nothing in
this report changes `experiments/EXP-SSIQ-a85692/specification.yaml`,
`experiments/EXP-SSIQ-58b642/` (frozen), or any ledger record — those are the
Coordinator's, not this task's, to touch.**

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. No
    orchestration.adapter doctor --probe was run this session; per
    VAL-BATCH-003 and RT-BATCH-003 (BATCH-003, this environment), every
    credentialed backend was previously found unprobeable here, so this is
    recorded as the standing condition, not re-verified as newly discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    ledger/goals/GOAL-SSIQ-001/goal.yaml runtime.runtime_note. Nothing below
    should be read as corroboration from a distinct model.
```

---

## GD-6 re-read confirmation (mandatory, checked first)

Per `ledger/goals/GOAL-SSIQ-001/goal.yaml`'s GD-6 entry and this draft's own
`gd6_standing_repair_applied.reread_requirement`, the following were read **in
full**, not sampled by headline field, before any opinion below was formed:

- `experiments/EXP-SSIQ-58b642/specification.yaml` — the frozen predecessor
  contract, all ~571 lines, including the seven PF findings it applied and the
  PF-5 scope-narrowing resolution text.
- `experiments/EXP-SSIQ-58b642/runs/RUN-SSIQ-58b642-a/execution_report.yaml` —
  full, including both protocol deviations (PD-1: the WISDE-linkage blocker;
  PD-2: the Frobenius-conjugate double-edge finding), all three anomalies, and
  the executor's own assessment.
- `experiments/EXP-SSIQ-58b642/runs/RUN-SSIQ-58b642-a/raw-result.json` — full
  (both halves; the file exceeds one read window), including
  `delta_e_cross_reference_report` for all 12 primes, `null_arm` for all three
  seeds, `phase0_calibration`, `diameters`, and `wisde_records_summary`.
- `coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/RT-BATCH-003.md`
  — full, including the GD-6 proposal text and the §2.2/§3d recommendation of
  the direct-computation route as the cheaper unblocking option.
- `coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/VAL-BATCH-003.md`
  — full, including finding 7 (the VOID-taxonomy gap) and finding 8
  (`command.txt` non-reproducibility).
- `ledger/evidence/EV-SSIQ-9a0396.yaml` and `ledger/decisions/DEC-20260805-cd8bcd.yaml`
  — full.
- `ledger/goals/GOAL-SSIQ-001/goal.yaml` — full, including the exponent budget,
  lever table, all six `known_defects_of_this_record` entries (GD-1 through
  GD-6), and `next_action`.
- `ledger/hypotheses/H-SSIQ-18dc91.yaml` and `H-SSIQ-9e2c71.yaml` — full.
- `experiments/EXP-SSIQ-a85692/specification.yaml` — the draft under review,
  full.
- `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, Sections 1.4–3 (Algorithm
  1–3, Lemmas 3.2–3.5, Theorem 1.5, proof of Theorem 1.1) and Section 4.1
  (rough concrete-cost estimate) — read directly, not from memory, per the
  draft's own instruction.
- `tools/validate_ledger.py`, the `RUN_REQUIRED_TOP` list and the companion-
  artifact check (the code that produced GD-5), to check finding 7 below
  against the actual validator rather than the contract's claim about it.

**What mattered from this re-read, concretely, not just "everything was read":**

1. RT-BATCH-003 §2.2/§3d and its `BATCH-004 recommendation, ranked` item 1 do
   not merely suggest the direct-computation route — they explicitly say it
   must be **"gate[d] on a cheap pre-compute feasibility estimate (cost of the
   smooth-degree search at the smallest pre-registered prime) before freezing
   a successor contract, per GD-4's standing practice."** The draft contains
   no such estimate anywhere; `smoothness_parameters_pinned_before_data`
   defers both the number and the estimate to the Executor's runtime
   discretion. This is the single fact that reading RT-BATCH-003 in full
   (rather than trusting the goal record's one-line summary of it) surfaced,
   and it is the basis of Finding 1 below.
2. VAL-BATCH-003 finding 7's precise wording — "a downstream reader filtering
   by `decision_branch` cannot distinguish 'signal contaminated by structure'
   from 'no data existed to test either direction'" — is what let me notice
   that the draft's own new `M-COVERAGE` per-prime exclusion clause (Finding 4
   below) reintroduces exactly this ambiguity one level down, even though the
   draft's *top-level* branch vocabulary fix is real and correctly applied.
   Skimming the draft's `gd6_standing_repair_applied` claim would not have
   caught this; only holding VAL-BATCH-003's own sentence against every use of
   the word "VOID" in the new text did.
3. `raw-result.json`'s per-prime `delta_e_cross_reference_report.<p>.delta_gt_1_blocked.n_vertices_needing_a_label`
   values (194, 306, 460, 594, 718, 864, 1014, 1172, 1304, 1462, 1614, 1760 —
   summing to 11,462) and `execution_report.yaml`'s
   `development_verification_commands` note ("full graph construction and
   timing for all 12 primes (fast: 0.4-4.5s each")) are the two numbers the
   feasibility arithmetic in Finding 1 is built from. Neither is quoted
   anywhere in RT-BATCH-003, VAL-BATCH-003, EV-SSIQ-9a0396, or the goal
   record's summaries of BATCH-003 — they exist only in the raw run artifact,
   which is exactly why the re-read mandate names it explicitly rather than
   the reviews that cite it.
4. Reading `paper_fulltext.md` directly (not trusting the draft's paraphrase)
   confirmed the draft's mechanism correctly avoids the hard `curve → ideal`
   Deuring direction (RT-BATCH-003 objection 4's wording correction is
   respected: nowhere does this draft cite KLPT as the cost driver) — this is
   a point in the draft's favor, not a defect, and it would have been unfair
   to omit it.

---

## Bottom line up front

The draft correctly implements RT-BATCH-003's own top recommendation (direct
in-session smooth-degree search, not full Deuring reconstruction) and
correctly applies most of GD-6's standing repair at the top level: the
`DATA-UNAVAILABLE/BLOCKED` branch is genuinely distinct from
`CONTROL-FAILURE-VOID` in the decision rule text, and `required_artifacts`
is, on independent check against `tools/validate_ledger.py`, actually correct
this time. But the draft has three defects serious enough to block freeze,
one of them large: (1) the single most expensive, least-checked step in the
whole contract — building B-smooth isogeny tables for ~11,462 vertices across
12 primes — has no feasibility estimate at all, and the arithmetic below
suggests the naive per-vertex reading of the method, at any B large enough to
give useful coverage, overshoots the stated budget by roughly one to two
orders of magnitude; (2) the modular polynomials Φ_ℓ needed for ℓ > 2 (the
whole point of the "smooth-degree" search, since ℓ=2 alone is nearly useless
here — see Finding 1) have no named, verified source, unlike Φ_2, which
BATCH-003 explicitly required to be sourced correctly and not approximated;
(3) `C-NULL-LABEL`, the control the draft relies on (unchanged) to rule out a
structure-correlated artifact, cannot detect the one new artifact mechanism
this draft's own new instrument introduces — a search-order bias correlated
with 2-isogeny-graph position — because that mechanism produces exactly the
signature (`real arm has a gap, shuffled arm does not`) the control reads as
`DETECTED`. A fourth defect, smaller but concrete, is that the M-COVERAGE
per-prime exclusion clause reuses the bare word "VOID" the contract otherwise
worked to retire — the same shape of leak VAL-BATCH-003 caught at the
top level, one level further down, in text this draft itself introduces.

None of these require redesigning the experiment. All four have a concrete,
statable fix below.

---

## Findings

### Finding 1 — [BLOCKING] No feasibility estimate exists, and a first-principles estimate suggests the naive reading overshoots budget by roughly 1–2 orders of magnitude

**The arithmetic RT-BATCH-003 asked for and the draft still doesn't do.**

Theorem 1.5 (paper, line 81) bounds delta_E ≤ (p/2)^{1/3} for *every*
supersingular curve. At this campaign's own pre-registered prime set that
bound is tiny:

| p | (p/2)^{1/3} |
|---|---|
| 2437 (smallest) | ≈ 10.68 |
| 21601 (largest) | ≈ 22.14 |

This has two consequences the draft doesn't draw out.

**(a) A search restricted to ℓ=2 only is nearly useless here.** Reusing
BATCH-003's diameter measurements (`raw-result.json.diameters`: 10 at p=2437,
14 at p=21601) — the *cheapest possible* "delta_E upper bound," a pure
2-isogeny BFS distance from E to E^{(p)} in the graph already built, giving
delta_E ≤ 2^{diameter} — would report bounds of 2^10=1024 to 2^14=16384,
which is 2–3 orders of magnitude *looser* than the true ceiling of ~11–22.
For the search to be informative at all (i.e., for `M-BOUND-TIGHTNESS` and
`M-COVERAGE` to mean anything beyond "found *some* huge composite degree"),
B must include primes well beyond 2 — this is not an optional refinement of
the method, it is required by the object's own scale.

**(b) But covering primes beyond 2 requires modular polynomials Φ_ℓ the
campaign has never sourced, at a combinatorial cost the draft never
estimates.** Using the draft's own worked example set L={2,3,5,7,11,13}: to
guarantee coverage of the *entire* possible degree range up to 22 (the
largest pre-registered prime's ceiling), B must be at least 19 (a degree can
literally *be* the prime 19), so a genuinely useful pinning needs B≈19–23,
not the draft's example set (which stops at 13 and would already miss
prime-17 and prime-19 degrees — a second, smaller gap in the draft's own
worked example).

Using Lemma 3.2's own bound, #L(E,X,B) ≤ Ψ(X,B)·X·(ln X + 2), and noting that
at B≈23 essentially every integer ≤ X=23 is B-smooth (Ψ(X,B)≈X):

```
#L(E,X,B) ≈ X² (ln X + 2) ≈ 23² × (ln 23 + 2) ≈ 529 × 5.13 ≈ 2714 entries (one side)
```

Two tables per vertex (from E and from E^{(p)}) ≈ 5400 entries. Summed over
the 11,462 non-F_p-rational vertices needing a search across all 12 primes
(`raw-result.json.delta_e_cross_reference_report.*.delta_gt_1_blocked.n_vertices_needing_a_label`,
summing to 194+306+460+594+718+864+1014+1172+1304+1462+1614+1760 = **11,462**):

```
11,462 × 5400 ≈ 6.19 × 10^7 table entries to construct, run-wide
```

Per-entry cost floor, from `execution_report.yaml`'s own measured Φ_2
graph-construction timing (0.4–4.5s for a whole ~1800-vertex graph, i.e. ≈
2.5ms per Φ_2 root-finding call at the largest prime — and this is for the
*cheapest* polynomial in the needed set, Φ_2's fixed nine-term form; Φ_ℓ for
ℓ up to 19–23 has degree ℓ+1 and classical-modular-polynomial coefficients
that grow enormously with ℓ, so 2.5ms/entry is a floor, not an average):

```
6.19×10^7 entries × 2.5ms/entry ≈ 154,750s ≈ 43 hours ≈ 21.5× the 7200s wall-clock budget
```

— using the *most optimistic* available per-entry cost figure, before
accounting for the (real, larger) cost of evaluating Φ_ℓ for ℓ>2. This is an
order-of-magnitude sanity check, not a certified measurement, but it is built
entirely from numbers already in the committed BATCH-003 artifacts (Theorem
1.5's own bound, Lemma 3.2's own cardinality bound, and the Executor's own
measured Φ_2 timing) — exactly the standard the task asks for, and exactly
what RT-BATCH-003 asked the Coordinator to obtain before freezing this
contract.

**A second, sharper problem: the one budget safeguard the draft does have
only checks the smallest prime.** `stopping_rules`' "PHASE -1 BUDGET CAP"
requires the sub-budget check only "on the smallest pre-registered graph."
But table size scales with X ∝ (p/2)^{1/6}, which grows across the
pre-registered set (X≈3.2·B^{1/2} at p=2437 vs. X≈4.7·B^{1/2} at p=21601) —
so a smoke test passing cheaply at p=2437 (203 vertices, 194 needing search,
smaller X) provides no assurance about p=21601 (1800 vertices, 1760 needing
search, the largest X), where the arithmetic above shows the real cost is
concentrated. A run could clear the stated stopping-rule check, proceed
through several primes, and only then discover the overshoot deep into the
budget — the opposite of "fail fast."

**Fix (concrete, does not redesign the experiment):**

1. Pin B=23, X=23 (derivation: B must exceed the largest prime that can
   divide any integer ≤ ⌈(p_max/2)^{1/3}⌉ = 22 at p=21601, i.e. B≥19,
   rounded to the next prime 23 for margin; X via the paper's own formula
   X=B^{1/2}(p_max/2)^{1/6} ≈ √23×4.68 ≈ 22.4, rounded to 23) — this replaces
   the unpinned "e.g. {2,3,5,7,11,13}" example, which under-covers primes 17
   and 19 that the largest pre-registered prime's own ceiling requires.
2. Before Phase -1 runs against the full prime set, require an **executed,
   reported smoke test**: build one vertex's two-sided table at the
   **largest** pre-registered prime (21601), not the smallest, using the
   pinned B=23, and report the measured wall-clock and entry count. Compare
   against the arithmetic above and against the 7200s budget explicitly in
   `execution_report.yaml` before Phase -1 proceeds past the smallest prime.
3. If the smoke test confirms an overshoot anywhere near the estimate above,
   the contract needs an explicit scope reduction stated *before* freeze —
   e.g., a stated per-prime vertex sample cap (with the sampling rule
   pre-registered, not chosen after seeing results) — rather than
   discovering this at run time and improvising one. This is the same
   discipline `selection_rule_pf3_corrected` already applies to prime
   selection; it is currently missing for vertex selection within a prime.

### Finding 2 — [BLOCKING] Φ_ℓ for ℓ > 2 has no named, verified source

BATCH-003's contract required, for Φ_2 alone: "a published, fixed nine-term
polynomial; DO NOT approximate or truncate it" — and the Validator
independently re-verified those nine coefficients via a third, from-scratch
route (exact rational Vélu-formula arithmetic) before trusting them
(`VAL-BATCH-003.md` §5). This draft's method requires Φ_ℓ for every prime in
L up to B (per Finding 1, realistically B≈19–23: Φ_3, Φ_5, Φ_7, Φ_11, Φ_13,
Φ_17, Φ_19), and says nothing about where those coefficients come from. This
matters because the classical modular polynomials grow fast — by ℓ=13–19 the
coefficients are large integers, not a small fixed table an implementer can
safely "recall" the way Φ_2's nine terms can be quoted from a paper appendix.
An Executor asked to "mirror Algorithm 1–3" without a cited source risks
either (a) silently generating Φ_ℓ incorrectly (a correctness bug that would
not be caught by any control in this contract — `C-BOUND-CHECK`'s
cross-check only validates *degrees found*, not the polynomial used to find
them, against an independent Φ_ℓ), or (b) attempting to derive Φ_ℓ from
scratch in-session (a nontrivial symbolic-computation sub-task with its own
correctness risk, silently absorbing part of the compute budget Finding 1
already shows is tight).

**Fix:** name a specific, cited, verifiable source for Φ_ℓ (ℓ ∈ L, ℓ>2)
before implementation begins — e.g. a published table (Sutherland's modular
polynomial database, or the classical tables in a cited reference) — and
require the same independent-verification standard BATCH-003 applied to Φ_2
(a from-scratch cross-check via an independent method, e.g. the
j(q)-expansion identity or exact Vélu-formula arithmetic on a handful of test
curves, for at least the largest ℓ actually used) before any real-vertex
search runs against it.

### Finding 3 — [BLOCKING] `C-NULL-LABEL` cannot detect the one new artifact mechanism this draft's own instrument introduces

This directly answers the task's points 3 and 4 together, since the
mechanism is the same and the reasoning `C-BOUND-CHECK`'s non-gating design
relies on is the reasoning this finding breaks.

**Concrete mechanism.** Algorithm 1/2 as specified (and as this draft
inherits it, `paper_fulltext.md` lines 137–176) builds the table L(E,X,B) by
iterating primes ℓ ≤ B in increasing order (line 2: "for ℓ ≤ B do"), and for
each ℓ extends every existing entry before moving to the next prime.
Algorithm 2 then returns on the *first* matching entry found in this
construction order (line 4–6: "for (E′,ψ) ∈ L do ... return"). This order
systematically favours degree combinations built from small primes,
especially ℓ=2 — the *same* prime that defines the 2-isogeny graph the
descent experiment measures gradient over. A vertex whose true minimal
isogeny (or *some* small-degree isogeny reaching a matchable target) is
reachable via a short run of 2-steps will be assigned a small reported
delta_E quickly; a vertex whose only matchable path runs through several
distinct larger primes gets a larger reported value even if its *true*
delta_E is comparable — a labelling bias correlated with each vertex's own
2-isogeny-graph proximity structure, driven by the search algorithm, not by
arithmetic.

**Why `C-NULL-LABEL`, unchanged, does not catch this.** `C-NULL-LABEL`
shuffles the *already-computed* delta_E value multiset uniformly at random
across vertices. This destroys *any* correlation between the reported label
and graph position — including a genuine delta_E-gradient correlation *and*
this search-order artifact, indistinguishably. If the search-order bias is
real, the real-label arm shows a gap (small-2-step-distance vertices get
systematically smaller labels, correlated with the very adjacency greedy
descent walks), the shuffled arm shows none (shuffling destroys the
correlation regardless of its source), and the decision rule reports
`DETECTED` — a false positive for "a computable delta_E-gradient exists,"
when what was actually detected is a property of the labelling *instrument*.
This is the same shape as BATCH-003's PF-1 (shared bias does not
automatically cancel) and PF-4 (tie-break rule could be structure-correlated)
findings, applied to the one genuinely new mechanism this draft introduces.

**Why this breaks `C-BOUND-CHECK`'s stated non-gating reasoning.** The
draft's justification for not gating on `M-BOUND-TIGHTNESS` — "an upper
bound remains a valid, disclosed label ... as long as M-COVERAGE and the
label distribution are honestly reported" — implicitly assumes the
*looseness* of an upper bound is uncorrelated with graph position. That
assumption is never argued and, per the mechanism above, is plausibly false:
the search's own construction order makes looseness (or tightness) a
function of a vertex's position relative to small-prime paths, which is
exactly the axis under test. Honest reporting of `M-BOUND-TIGHTNESS` as a
*passive* diagnostic does not protect against this, because the artifact
would show up as a `DETECTED` M-GAP, not as a bound-tightness anomaly.

**Fix (a genuinely new, cheap control, not a redesign):** Add a required
control distinct from `C-NULL-LABEL` that holds the search's algorithmic
structure fixed while breaking its correlation with the true arithmetic. Two
concrete, cheap options, either is sufficient:

- **Random-target null:** run the identical `compute_delta_e.py` search, at
  the identical (B,X), but with each vertex's "target" replaced by a
  uniformly random *other* vertex on the same graph instead of the true
  Frobenius conjugate E^{(p)}. If the resulting collision-degree label still
  correlates with 2-isogeny-graph distance-to-target (predicted by the
  mechanism above), the real-arm signal is contaminated regardless of what
  C-NULL-LABEL shows.
- **B-stability check:** run the full pipeline at two materially different
  smoothness bounds (e.g. B=2 alone, restricted to power-of-2 degrees, versus
  the pinned B=23) and require M-GAP's sign to be stable across them. Per
  the artifact-tell framing this review is asked to apply: the parameter that
  should destroy a search-order artifact as it increases is the search's
  *resolving power* (B, X) — a genuine delta_E-gradient signal should be
  stable or strengthen as bound tightness improves; an instrument artifact
  has no reason to track B in a consistent direction. A flat or unstable
  M-GAP across very different B is the artifact tell; this is currently
  neither run nor reported.

This is required, not merely advisory, because — per Finding 3's mechanism —
the existing null control is structurally blind to exactly the risk this new
instrument introduces, and the draft's own stated reasoning for not gating
`M-BOUND-TIGHTNESS` depends on an assumption this finding shows is
unjustified.

### Finding 4 — [BLOCKING] The per-prime `M-COVERAGE` exclusion clause reuses the bare word "VOID" the contract otherwise worked to retire

Checked every branch and every control's `failure_consequence` text against
VAL-BATCH-003 finding 7's exact standard, per the task's instruction, not
just the top-level decision rule this draft explicitly rewrote.

The top-level fix is real: `decision_rule_frozen_before_data` and
`invalidation_rules` consistently use `DATA-UNAVAILABLE/BLOCKED` (Phase -1
gate, M-COVERAGE<0.5 on 4+ primes) and `CONTROL-FAILURE-VOID`
(`C-NULL-LABEL`/`C-CONNECTIVITY` failure) as distinct, explicitly
disambiguated labels at the *run* level — no leak found there.

But `metrics.secondary.M-COVERAGE`'s own text, introduced fresh by this
draft (not inherited from EXP-SSIQ-58b642, since M-COVERAGE is the one
genuinely new metric), reads: *"if M-COVERAGE(N) falls below 0.5 for any
prime, that prime's contribution to M-GAP is **VOID** (mirrors the
trapped_fraction gate...)"* — bare "VOID," the exact word the run-level fix
was built to keep away from a data-availability shortfall. A downstream
reader filtering *per-prime* records by outcome label — exactly the failure
mode VAL-BATCH-003 finding 7 named at the run level — would now conflate
"this prime's coverage was too low" (a data-availability shortfall, the
*same underlying mechanism* the run-level gate calls `DATA-UNAVAILABLE`)
with "this prime's signal is contaminated" (the run-level meaning of `VOID`
proper), one level of granularity below where the fix was applied. This is
not hypothetical: the *same* per-prime pattern already exists for
`trapped_fraction` ("that prime's gamma_greedy contribution is VOID",
inherited unchanged from EXP-SSIQ-58b642, itself never disambiguated from a
run-level VOID either) — so this draft now has *three* distinct concepts
(run-level `CONTROL-FAILURE-VOID`, run-level `DATA-UNAVAILABLE/BLOCKED`,
and now two separate per-prime exclusion mechanisms) sharing one bare word
in at least two places.

**Fix:** rename the M-COVERAGE per-prime exclusion label to something
distinct from both run-level branches and from the trapped_fraction
exclusion — e.g. `PER-PRIME-COVERAGE-SHORTFALL` — and add one explicit
sentence in the contract (near `fitting_window` or the decision rule)
enumerating all outcome-scope labels now in play (2 run-level branches + 2
per-prime exclusion labels) so a downstream reader cannot conflate any pair
of them. This is a wording fix, not a redesign, and it completes rather than
contradicts the taxonomy work this draft otherwise did correctly.

### Finding 5 — [ADVISORY] Phase ordering (Phase 0 before Phase -1) has no material hidden cost, but the smoke-test gap in Finding 1 is the real missing pre-check

Point 5's question directly: no, running Phase 0 (pure synthetic, seconds)
before Phase -1 wastes negligible budget even in the worst case, since graph
reuse itself is near-zero cost (cached from BATCH-003, or rebuildable in
0.4–4.5s per prime per `execution_report.yaml`). The cheaper pre-check that
*should* run even before Phase 0 is not a reordering of Phase 0 and Phase -1
— it is the single-vertex-single-prime smoke test named in Finding 1, which
this draft omits entirely (it defers to "the pinned (B,X) must be fixed
before any graph's computation begins," never to "a smoke test must be run
and reported before the pin is trusted"). Folded into Finding 1's fix rather
than treated as a separate blocking item, since the fix is identical.

### Finding 6 — [ADVISORY, not blocking] `required_artifacts` verified correct against `tools/validate_ledger.py`, not merely trusted

Checked `RUN_REQUIRED_TOP = ["id", "experiment_id", "status", "code",
"environment", "inputs", "timing", "result"]` (validate_ledger.py line 155)
and the companion-artifact check (lines 391–395: `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`) against
the draft's `required_artifacts` list directly, rather than accepting the
draft's own claim that it "inherits EXP-SSIQ-58b642's PF-6 fix." All five
companion filenames are present under `runs/RUN-SSIQ-a85692-a/`; `manifest.yaml`
is listed (its body-level `RUN_REQUIRED_TOP` satisfaction is a runtime
obligation, correctly noted as separate from the artifact list itself in
`required_artifacts_note`). **Confirmed correct, not a repeat of GD-5.** No
action needed.

### Finding 7 — [ADVISORY] Section 4.1's own optimism caveat is relevant to this draft's B/X-fitting approach, and the connection is not drawn

The task names this explicitly, so it is answered even though it does not
rise to blocking on its own (Finding 1 already blocks on the underlying
arithmetic). Section 4.1's caveat ("these numbers are obtained via a rough
UNDERestimation of the size of the table and the cost of its generation ...
we are assuming here that the bound of Lemma 3.5 is tight") concerns the
paper's *own* concrete-cost estimate for Algorithm 3's random-walk-until-
success loop at cryptographic scale — a different quantity from what this
draft measures (this draft applies Algorithm 2 once per fixed vertex, no
retry loop, so the "1/P0" factor from Section 4.1 does not directly transfer,
correctly). But the *mechanism* of the optimism — "assume constructing a
table costs a single F_{p^2}-operation per entry" (paper, line 230) —
is exactly what Finding 1's cost floor also assumes for lack of a better
figure, and this campaign has *already measured*, in the sibling goal
GOAL-P13-001 (per `goal.yaml`'s `related_goals_note`: EV-PEC-2e67ff,
EV-PEC-857664, "the measured per-entry overhead refuting the paper's Section
4.1 convention"), that this convention understates real per-entry cost. This
draft's "fit B,X to the run's wall-clock budget" instruction gives the
Executor no warning that the naive per-entry-cost assumption it will
naturally reach for has already been shown, elsewhere in this campaign, to
be optimistic. **Fix (folds into Finding 1's smoke-test requirement):** the
required smoke test should explicitly measure per-entry cost rather than
assume the paper's Section 4.1 convention, and the contract should cite
GOAL-P13-001's finding as the reason a measured, not assumed, per-entry cost
is required.

### Finding 8 — [ADVISORY] `smoothness_parameters_pinned_before_data`'s worked example under-covers the largest prime's own ceiling

Noted in passing under Finding 1 but worth its own line: the draft's example
set `L = {2,3,5,7,11,13}` (`inputs.delta_e_computation.method`) omits primes
17 and 19, both of which are ≤ the largest pre-registered prime's ceiling of
⌈(21601/2)^{1/3}⌉ = 22 and so can appear as single-step degrees of the
minimal isogeny at that prime. If the contract freezes with this example
literally adopted as the pin, coverage at the largest primes would be
mechanically capped below what Theorem 1.5 guarantees is possible — not a
bug in the search, but a self-inflicted, avoidable coverage ceiling. Folded
into Finding 1's fix (B=23 supersedes this example).

---

## Required controls (for the successor contract, before freeze)

- An executed, reported smoke test at the **largest** pre-registered prime
  (not just the smallest), measuring real per-entry table-construction cost
  including at least one ℓ>2 modular-polynomial evaluation, checked against
  the 7200s budget before Phase -1 proceeds past the first prime (Finding 1).
- A cited, verified source for Φ_ℓ (ℓ ∈ L, ℓ>2), with an independent
  cross-check for at least the largest ℓ used, matching the standard already
  applied to Φ_2 (Finding 2).
- A search-algorithm-bias null control distinct from `C-NULL-LABEL` — either
  a random-target null or a B-stability check — required and reported
  alongside `C-NULL-LABEL`, not optional (Finding 3).
- Disambiguated labels for the two per-prime exclusion mechanisms
  (`trapped_fraction`, `M-COVERAGE`) so neither reuses the bare word "VOID"
  now reserved for the run-level `CONTROL-FAILURE-VOID` branch (Finding 4).

## Counterexample or mutation

The cheapest discriminating mutation for Finding 3 is the random-target null
described there: re-run `compute_delta_e.py` unchanged except for substituting
a uniformly random other graph vertex for the true Frobenius conjugate
E^{(p)} as the search target, for a handful of vertices at the smallest
prime. If the reported collision degree still correlates with 2-isogeny-graph
distance-to-(random)-target at a magnitude comparable to what the real
experiment would report against the true target, the search-order artifact
is confirmed live and the real arm's M-GAP cannot be trusted as evidence of a
delta_E-gradient without this control run and reported first.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this is a
toy-scale, gradient-existence screen with `asymptotic_claim: null` throughout
(`H-SSIQ-9e2c71.asymptotic_claim_note`), inherited correctly unchanged from
`H-SSIQ-18dc91`. The relevant baseline for this review is the campaign's own
instrument-scrutiny discipline (GD-4/GD-5/GD-6): this draft correctly applies
two of the three prior lessons (an actually-checked `required_artifacts` list,
a genuinely distinct decision-rule branch at the top level) but repeats a
narrower version of GD-4's shape at Finding 1 — an instrument (the delta_E
search) whose feasibility at the stated scale is asserted by omission (no
estimate given) rather than checked, the exact pattern GD-4 was adopted to
stop.

## Heuristic challenges

`H-SSIQ-9e2c71.heuristic_assumptions` is correctly empty (inherited from
H-SSIQ-18dc91; this remains a gradient-existence screen, not a proof-oriented
or heuristic-conditional claim, so `docs/target-result-profile.md`'s
heuristic-inventory checklist does not bind it) — attacked and held, same
verdict as both BATCH-003 reviews reached for the predecessor. The implicit,
unstated assumption this review challenges is *not* a numbered heuristic
requiring a random-model justification; it is the algorithmic-bias
independence assumption underlying `C-BOUND-CHECK`'s non-gating design
(Finding 3), which is an instrument-design claim, not a heuristic about the
arithmetic object.

## Cost model challenges

No concrete asymptotic-cost claim is made anywhere in this draft
(`asymptotic_claim: null`, correctly), so `docs/target-result-profile.md`'s
per-attempt-cost × inverse-success-probability review does not apply in the
complexity-claim sense. What *does* apply, and is the substance of Finding 1,
is ordinary resource bookkeeping: the draft's own `budget` section requires
the Executor to "state explicitly ... how the 7200s is split," but supplies
no pre-freeze estimate against which that split can be judged reasonable
before the run is attempted — exactly the gap RT-BATCH-003 asked the
Coordinator to close before this contract froze.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this draft or its inherited hypothesis; no scope widening found.
`H-SSIQ-9e2c71.scope_ceiling` (toy, inherited from BATCH-003's pinned prime
set) is correctly stated and nothing in the draft's design exceeds it.

## Proof architecture challenges

`proof_search_map.not_applicable_reason` is correctly reasoned and inherited
unchanged (gradient-existence screen, not a proposed complexity reduction) —
attacked and held, same verdict both BATCH-003 reviews reached for the
predecessor hypothesis; nothing in this draft's changes (the new labelling
instrument) converts it into a proof-oriented proposal, since the instrument
labels a fixed toy graph rather than claiming anything about the archived
source's own Heuristic 1 or asymptotic result.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification.yaml` as read at draft
status (not yet frozen): the contract correctly reuses BATCH-003's validated
graph-construction and calibration infrastructure by reference, correctly
implements RT-BATCH-003's own top-ranked recommendation (direct in-session
smooth-degree search rather than full Deuring reconstruction), and correctly
applies GD-6's run-level decision-rule taxonomy fix. It should not be frozen
as currently written: the new instrument's own feasibility at the stated
scale is unestimated and a first-principles calculation from numbers already
in the BATCH-003 artifacts suggests it plausibly overshoots the stated budget
by an order of magnitude or more at any smoothness bound wide enough to be
useful; the modular polynomials the method needs beyond Φ_2 have no named
source; the one null control the draft carries forward cannot detect the one
genuinely new artifact mechanism this draft's own search algorithm
introduces; and the new per-prime coverage-exclusion label reuses the exact
word the contract's own taxonomy fix exists to retire.

## Next concrete action

Coordinator: before moving this draft to `status: approved` / `frozen_at`,
require the Executor (or a bounded, zero-compute-adjacent research task) to
(1) run and report the smoke test named in Finding 1 at the *largest*
pre-registered prime with the pinned B=23, X=23; (2) name and cite a verified
source for Φ_ℓ, ℓ>2 (Finding 2); (3) add the search-algorithm-bias null
control (Finding 3) as a required, not optional, control alongside
C-NULL-LABEL; (4) rename the M-COVERAGE per-prime exclusion label away from
bare "VOID" (Finding 4). None of these require redesigning the experiment's
mechanism, which is otherwise sound and correctly targets lever L4 per this
goal's `next_action`.

## Overall verdict

**FREEZE-WITH-FIXES.** Required before freeze, in priority order:

1. **[BLOCKING]** Pin B=23, X=23 (or an equivalent derivation reaching the
   same coverage), and require an executed, reported feasibility smoke test
   at the **largest** pre-registered prime (not only the smallest) before
   Phase -1 is allowed to proceed across the full prime set — Finding 1.
2. **[BLOCKING]** Name and cite a verified source for Φ_ℓ, ℓ ∈ L \ {2}, with
   an independent cross-check for at least the largest ℓ used, before any
   implementation work on `compute_delta_e.py` begins — Finding 2.
3. **[BLOCKING]** Add a search-algorithm-bias null control (random-target
   null or B-stability check) as a required control distinct from
   `C-NULL-LABEL`, and report it alongside `C-NULL-LABEL` in the decision
   rule's evidentiary basis — Finding 3.
4. **[BLOCKING]** Rename the `M-COVERAGE` per-prime exclusion label away from
   bare "VOID," and add one sentence disambiguating all four outcome-scope
   labels (2 run-level, 2 per-prime) now in the contract — Finding 4.

Findings 5, 6, 7, 8 are advisory and either fold into the above fixes or
require no action (Finding 6: confirmed correct as written).

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692
  task_id: TASK-20260805-40ad8c
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification.yaml (status: draft,
    hypothesis_id H-SSIQ-9e2c71): a successor contract to the frozen, VOID
    EXP-SSIQ-58b642, reusing its graph-construction and calibration code by
    reference and replacing the blocked WISDE delta_E cross-reference with a
    direct in-session bidirectional meet-in-the-middle smooth-degree isogeny
    search per the archived source's Algorithm 1-3, gated by a new Phase -1
    M-COVERAGE >= 0.5 check, with a decision rule naming
    DATA-UNAVAILABLE/BLOCKED as distinct from CONTROL-FAILURE-VOID.
  objections:
    - "OBJ-1 [BLOCKING]: no feasibility estimate exists for the new delta_E-search instrument. A first-principles estimate from Theorem 1.5's own bound, Lemma 3.2's own cardinality bound, and EXP-SSIQ-58b642's own measured Phi_2 timing gives ~6.19x10^7 table entries run-wide and ~154,750s (~43h) at an optimistic 2.5ms/entry floor, ~21.5x the 7200s budget -- before accounting for the larger real cost of Phi_ell, ell>2. The only stated budget safeguard (Phase -1 smoke check) tests only the smallest prime, where cost is lowest, not the largest, where the arithmetic shows cost concentrates."
    - "OBJ-2 [BLOCKING]: the modular polynomials Phi_ell needed for ell>2 (required because ell=2 alone gives useless ~2^10-2^14 bounds against a true ceiling of ~11-22) have no named, verified source, unlike Phi_2 which BATCH-003 required to be sourced correctly and independently cross-checked."
    - "OBJ-3 [BLOCKING]: C-NULL-LABEL, reused unchanged, cannot detect the one new artifact mechanism this draft's own search introduces -- a search-construction-order bias favouring small primes (especially ell=2, the graph's own defining prime), which would produce exactly the 'real arm has a gap, shuffled arm does not' signature the decision rule reads as DETECTED. This also breaks the stated justification for not gating M-BOUND-TIGHTNESS, which assumes bound-looseness is graph-position-independent, an assumption never argued."
    - "OBJ-4 [BLOCKING]: the new M-COVERAGE per-prime exclusion clause reuses the bare word VOID -- the exact word the contract's run-level decision-rule fix (DATA-UNAVAILABLE/BLOCKED vs CONTROL-FAILURE-VOID) exists to retire -- one level of granularity below where GD-6's fix was applied, and alongside the pre-existing (inherited, likewise undisambiguated) per-prime trapped_fraction VOID."
    - "OBJ-5 [ADVISORY]: Phase-0-before-Phase-(-1) ordering has no material hidden cost; the real missing pre-check is the smoke test named in OBJ-1, not a reordering."
    - "OBJ-6 [ADVISORY, resolved]: required_artifacts independently checked against tools/validate_ledger.py's RUN_REQUIRED_TOP and companion-file list -- confirmed correct, not a repeat of GD-5."
    - "OBJ-7 [ADVISORY]: this campaign's own GOAL-P13-001 evidence (EV-PEC-2e67ff, EV-PEC-857664) already shows the paper's Section 4.1 per-entry-cost convention is optimistic; the draft's fit-B/X-to-budget instruction risks the same optimism unless the required smoke test measures, rather than assumes, per-entry cost."
    - "OBJ-8 [ADVISORY]: the draft's own worked example L={2,3,5,7,11,13} under-covers the largest pre-registered prime's own ceiling (misses primes 17, 19, both <= 22); superseded by the concrete B=23 pin in OBJ-1's fix."
  required_controls:
    - "Executed, reported feasibility smoke test at the LARGEST pre-registered prime (not only the smallest), measuring real per-entry table-construction cost including at least one ell>2 modular-polynomial evaluation, before Phase -1 proceeds past the first prime."
    - "A cited, verified source for Phi_ell (ell in L, ell>2), independently cross-checked for at least the largest ell used, matching the standard already applied to Phi_2."
    - "A search-algorithm-bias null control distinct from C-NULL-LABEL (random-target null, or a B-stability check across at least two materially different smoothness bounds), required and reported, not optional."
    - "Disambiguated labels for the two per-prime exclusion mechanisms (trapped_fraction, M-COVERAGE) so neither reuses the bare word VOID reserved for the run-level CONTROL-FAILURE-VOID branch."
  counterexample_or_mutation: >-
    Random-target null: re-run compute_delta_e.py unchanged except for
    substituting a uniformly random other graph vertex for the true
    Frobenius conjugate E^{(p)} as the search target, for a handful of
    vertices at the smallest pre-registered prime. If the reported collision
    degree still correlates with 2-isogeny-graph distance-to-(random)-target
    at a magnitude comparable to what the real experiment would report
    against the true target, the search-order artifact named in OBJ-3 is
    confirmed live and the real arm's M-GAP cannot be trusted as evidence of
    a delta_E-gradient without this control run and reported first.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    inherited correctly from H-SSIQ-18dc91). The relevant baseline is the
    campaign's own instrument-scrutiny discipline (GD-4/GD-5/GD-6): this
    draft correctly applies the required_artifacts and top-level
    decision-rule-taxonomy lessons but repeats a narrower version of GD-4's
    shape at OBJ-1 -- an instrument's feasibility at the stated scale
    asserted by omission rather than checked.
  heuristic_challenges:
    - "H-SSIQ-9e2c71.heuristic_assumptions is correctly empty, inherited unchanged from H-SSIQ-18dc91 (gradient-existence screen, not a proof-oriented claim) -- attacked and held. The unstated assumption this review challenges (OBJ-3) is an instrument-design independence assumption behind C-BOUND-CHECK's non-gating choice, not a numbered heuristic requiring a random-model justification."
  cost_model_challenges:
    - "No concrete asymptotic-cost claim is made anywhere (asymptotic_claim: null, correctly); the per-attempt-cost x inverse-success-probability review does not apply in the complexity-claim sense."
    - "Ordinary resource bookkeeping is the live issue: the draft requires the Executor to state how the 7200s budget is split but supplies no pre-freeze estimate against which that split can be judged reasonable, despite RT-BATCH-003 explicitly asking for exactly this before freeze (OBJ-1)."
    - "This campaign's own GOAL-P13-001 evidence already shows the paper's Section 4.1 per-entry-cost convention is optimistic; the draft inherits the same optimism risk unless the required smoke test measures rather than assumes per-entry cost (OBJ-7)."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this draft or its inherited hypothesis; no scope widening found."
    - "scope_ceiling (toy, inherited from BATCH-003's pinned prime set) is correctly stated and not exceeded by anything in the draft's design."
  proof_architecture_challenges:
    - "proof_search_map.not_applicable_reason is correctly reasoned and inherited unchanged; the new labelling instrument does not convert this into a proof-oriented proposal, since it labels a fixed toy graph rather than claiming anything about the archived source's Heuristic 1 or asymptotic result -- attacked and held, same verdict as both BATCH-003 reviews reached for the predecessor."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification.yaml as read at draft
    status: the contract correctly reuses BATCH-003's validated
    infrastructure by reference, correctly implements RT-BATCH-003's own
    top-ranked recommendation, and correctly applies GD-6's run-level
    decision-rule taxonomy fix. It should not be frozen as written: the new
    instrument's feasibility at the stated scale is unestimated and a
    first-principles calculation from already-committed BATCH-003 numbers
    suggests a plausible order-of-magnitude budget overshoot at any
    smoothness bound wide enough to be useful; Phi_ell for ell>2 has no named
    source; C-NULL-LABEL cannot detect the new search-order artifact
    mechanism; and the new per-prime M-COVERAGE exclusion label reuses the
    word the contract's own taxonomy fix exists to retire.
  next_concrete_action: >-
    Coordinator requires, before status: approved / frozen_at: (1) an
    executed, reported feasibility smoke test at the largest pre-registered
    prime with B=23, X=23 pinned; (2) a cited, verified source for Phi_ell,
    ell>2; (3) a search-algorithm-bias null control (random-target null or
    B-stability check) added as required alongside C-NULL-LABEL; (4) the
    M-COVERAGE per-prime exclusion label renamed away from bare VOID. None
    require redesigning the experiment's mechanism.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/reviews/RT-PREFREEZE-EXP-SSIQ-a85692.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic only (Theorem 1.5's stated bound, Lemma 3.2's stated
    cardinality bound, and arithmetic combining already-committed
    BATCH-003 measured timings and per-prime vertex counts from
    raw-result.json); no code executed, no graph built, no search run.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/reviews/RT-PREFREEZE-EXP-SSIQ-a85692.md
    -- experiments/EXP-SSIQ-a85692/specification.yaml, experiments/EXP-SSIQ-58b642/,
    and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
