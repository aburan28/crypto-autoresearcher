---
id: KN-TECH-a810e4
type: technique
title: A coverage or positive-control clause satisfied at its stated numeric floor is not the same as satisfying its stated intent — check the intent separately, every time
tags: [positive-control, coverage-gap, design-review, review-discipline, nearby-object-control, sensitivity-vs-specificity, methodology, statistics]
confidence: reported
complexity: >-
  not an arithmetic check like KN-TECH-95a42b — a design-review discipline:
  when a successor contract "fixes" a review-flagged gap, verify the fix
  restores the INTENT of the original requirement, not merely a numeric
  threshold the requirement happened to state
applicability: >-
  every successor experiment contract that closes a gap a prior review
  identified — especially validation-coverage clauses ("check a sample of
  size >= N") and positive-control clauses ("confirm the instrument can
  detect a known case before trusting a null reading on an unknown one")
source_refs: [EV-MONO-849355, EXP-MONO-670aa6, EV-MONO-04d447, EXP-MONO-b19c6b, H-MONO-663fb4]
added: '2026-08-31'
superseded_by: null
---

## Method

Across three consecutive experiments in this lane (EXP-MONO-c819ba,
EXP-MONO-670aa6, EXP-MONO-b19c6b), a recurring pattern emerged that is
distinct from the arithmetic failures KN-TECH-7745e6 and KN-TECH-95a42b
document: **a validation-coverage or positive-control requirement a prior
review flagged as too narrow gets satisfied by the next contract via the
cheapest literal reading that clears a stated numeric floor, while the
underlying intent of the check is left unrestored.** Three concrete
instances:

1. **The dual-path control.** EXP-MONO-670aa6's Red Team flagged that its
   dual-path (route-1-vs-route-2) check covered only the 100 real-arm
   cells, leaving the >20,000-draw null population entirely unchecked by
   the independent computation route. EXP-MONO-b19c6b's own fix (an
   "extended dual-path sample") clears the declared `>=200 samples` floor
   — but does so by sampling only TWO fixed within-curve positions
   (draw_index 0 and 100) repeated across ~97 curves, leaving over 99% of
   any SINGLE curve's null-draw index range (200-19999) completely
   unswept. The floor is met; the coverage the floor was meant to
   approximate — "the independent route was spot-checked across the
   range the p-value machinery actually depends on" — is not.

2. **The nearby-object positive control.** H-MONO-663fb4's own
   `proof_search_map.method_ceiling.nearby_object_control` requires: "any
   instrument that cannot reproduce the forced value exactly cannot
   detect an exceptional factor base at all." EXP-MONO-b19c6b's frozen
   text discharges this by explicitly relying on EXP-MONO-c819ba's own
   already-reviewed subgroup/coset-union result — valid for the REUSED
   computation (`conv.py`, byte-identical, twice independently reviewed)
   this control actually exercises. But EXP-MONO-b19c6b ALSO introduces a
   brand-new co-equal primary metric (a Fisher-combined panel-level
   statistic) specifically to catch effects too small for the per-curve
   test — and no experiment in this three-run lane has EVER applied that
   NEW statistic to a known-exceptional case. The letter of "the control
   is satisfied by relying on a prior result" is honoured; the intent
   ("every metric that could render a verdict has a demonstrated ability
   to detect a genuine positive") is not, for the metric that was added
   specifically to widen detection.

3. **The undisclosed partial-collision rate.** EXP-MONO-670aa6's
   independence check was fully absent; EXP-MONO-b19c6b's fix reports a
   `full_triple_collision` count of zero — correct and load-bearing — but
   never surfaces the (benign, but real) prime-only partial-collision
   rate (3/46, 3/48) that a reviewer had to re-derive from the raw
   comparison array. The headline number the fix was built around is
   reported; a narrower diagnostic that would let a future reader judge
   "how close" the panels came to colliding is not.

## The rule this establishes

**When a successor contract closes a review-flagged gap, ask two separate
questions, not one:** (a) does the fix clear the stated numeric
threshold? and (b) does the fix restore the reason the threshold was
stated in the first place? A "yes" to (a) is cheap to verify — it is
often a single number comparison — and is exactly the kind of check
KN-TECH-95a42b already automates. A "yes" to (b) requires re-reading the
ORIGINAL review finding's own stated concern (not just its stated
remedy) and checking the new design against that concern directly, which
is a design-review step, not an arithmetic one, and does not get easier
by being run more carefully at the numeric level.

**A specific, high-value instance of question (b): a new primary metric
introduced to widen detection inherits every existing positive-control
obligation the metric it supplements already discharged — it does not
inherit the discharge itself.** Reusing a prior experiment's positive
control result is valid ONLY for the exact computation that control
result was measured against; a new statistic sharing a Stage number or a
gating role with an old, validated one is not thereby validated.
Confirming a statistic's SPECIFICITY (it does not fire on a null-vs-null
comparison) is a distinct fact from confirming its SENSITIVITY (it does
fire on a genuine positive) — a null-object gate passing establishes only
the former.

## What this technique is not

This is not a claim that any of the three instances above invalidates its
own experiment's disposition — in each case the underlying reading
(controlled null, no enrichment, genuine independence) is independently
supported by other lines of evidence, and each gap is disclosed as an
open qualification rather than a refutation. It is a narrow, recurring
design-review failure mode — distinct from KN-TECH-7745e6's calibration
check and KN-TECH-95a42b's floor-vs-threshold arithmetic — worth checking
explicitly every time a contract claims to have closed a prior review's
finding, even in a contract that got every arithmetic check right.
