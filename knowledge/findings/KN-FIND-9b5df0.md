---
id: KN-FIND-9b5df0
type: internal_finding
title: "A pre-registration naming a source an 'independent route' before auditing its code provenance can make bit-identical agreement indistinguishable from same-code cross-environment reproducibility"
tags: [independence, route-provenance, code-lineage, pre-registration, environment-diversity, instrument-design, cross-validation, c3-lane, ml-kem, negative-result, toy-scale]
confidence: derivation_plus_two_independent_reviews_via_different_methods_on_one_model
evidence_level: derivation_plus_toy_scale_measurement
source_refs: [BATCH-fbb639, TASK-20260813-0eb5a3, TASK-20260813-7b3039, TASK-20260813-451a6d, TASK-20260813-6ab893]
internal_refs: [EV-MLKEM-965a37, DEC-20260813-28d7b2, DEC-20260813-c60bba]
sibling_findings_narrowed: []
sibling_findings_note: "This entry does not narrow any prior finding in this goal; it is a distinct instrument-design lesson about pre-registration methodology, not a further measurement of A-1 or the fibre-constancy criterion KN-FIND-9d44b4 and KN-FIND-7d098b address. `internal_refs` carries LEDGER records only, matching the shape those entries use."
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-451a6d/probes/probe_shared_code_provenance.sh
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-451a6d/probes/probe_shared_code_provenance_output.txt
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_route_independence.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_route_independence_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-451a6d/validation_report.yaml
review_refs:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-451a6d/validation_report.yaml
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/red_team_report.md
added: '2026-08-13'
superseded_by: null
---

## What this says, and what it does NOT say

**Claim tier: TOY, unconditionally.** Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Measured on this
campaign's own frozen lattice/basis grid, no reduction above `d = 40`.

**THIS ENTRY MAKES NO CLAIM THAT ANY MEASUREMENT IN `BATCH-fbb639` IS WRONG.** Every
number and the fired termination branch are independently re-derived by both reviews
from the frozen pre-registration with zero mismatches, and are robust under two
different, independently-constructed stricter coverage readings. This entry is about
what the agreement between two named "routes" is entitled to be read as **evidence
of** — not about whether the reported dispersion values are correct.

The finding, in one sentence:

> When a pre-registration names two data sources "independent routes" without
> auditing their code lineage, bit-identical agreement between them can be **entirely
> explained by shared code re-executed in a different environment**, and is
> indistinguishable at the level of the raw number from genuine
> algorithmically-independent cross-validation.

## 1. What was measured, and how the defect was found

`BATCH-fbb639`'s pre-registration (`PREREG-3`) named a route pair — `ROUTE-P`
(`results_relvar.json`) and `ROUTE-I` (`results_l7l8.json` for `L7`,
`results_am4.json` for `L9`/`L11`) — and froze a comparison: at every cell where both
routes exist, compute `D_route`, the disagreement between them, and compare it to
the observable's own fibre dispersion. At all 18 covered cells, `D_route = 0.0`
exactly while the observable's own fibre dispersion was strictly positive, so every
covered cell verdicted `EXCEEDS`.

Two independent reviews — the Validator and the Red Team, working blind to each
other and using different methods — each **diffed the actual source code** rather
than trusting the pre-registration's characterization, and both found the same
thing: `make_A`, `build_basis`, and `hkz_profile` — the numerical kernel that
produces every `lam1n`/`hkz` value at every covered cell — are shared **verbatim**
across all three named sources (`measure_am4.py` → `measure_relvar.py` →
`replicate_l7l8.py`), each downstream file's own docstring stating so explicitly:
"CARRIED VERBATIM from ...". For `L7`, the two "routes" additionally ran on the
**same host** — `results_l7l8.json`'s own environment block records
`ENVIRONMENTS_DIFFER: false`, every field matching the producer's run.

## 2. Why environment diversity alone did not catch this

For `L9`/`L11`, `results_am4.json` genuinely ran on a **different host** (macOS vs.
Linux) — real cross-machine execution, not the same-host `L7` case. But it runs the
**same carried-verbatim code**. So the two facts must be kept separate: a match
across genuinely different environments is consistent with either independent
implementations that happen to agree, or one implementation re-executed elsewhere.
Environment diversity by itself distinguishes neither. This is precisely the
distinction this goal's own binding carry — "'genuinely cross-platform' is NOT
citable" — already exists to police *after the fact*; this finding shows the same
discipline is needed **before** a pre-registration freezes a source as
"independent," not only when interpreting its result afterward.

`report_c3lane.md`'s own characterization of the `L9`/`L11` contribution — "This is
a genuinely independent computation ... executed in a different environment" —
**overstates what it establishes**. The "different environment" clause is narrowly
true and is not disclosed alongside the shared-kernel fact.

## 3. The control that neither confirms nor refutes, reported honestly

The Red Team built, rather than merely proposed, a control to test whether the
code-sharing artifact could be masking a false `EXCEEDS`: `D_route(rdet)` at `L11`,
comparing `results_relvar.json` (Linux) against `results_am4.json`'s
`probe_L_supplementary` block (a genuinely different host, macOS) — real
cross-machine data, using the same carried-verbatim `rdet_of`/`build_basis` code.
Result: `D_route(rdet) = 0.0` exactly, confirming the code-sharing mechanism
generalizes beyond `lam1n`/`hkz` to a candidate nobody in this goal disputes.

**However**, `rdet`'s own fibre dispersion is *also* exactly `0.0` at every cell
checked, because `|det B| = q^(d-k)` is algebraically independent of the random
matrix draw — the same "forced by algebra" phenomenon this goal's own `G-VAR`/`AM-11`
machinery already documents for `X_null`. So `rdet` **ties out** (`DOES NOT EXCEED`
under the frozen tie rule) rather than demonstrating a false-positive `EXCEEDS`. The
Red Team searched for a non-target candidate with genuine, non-algebraically-forced
fibre dispersion and found none available in the corpus. **Recorded plainly: whether
the 18 (or 16) `EXCEEDS` verdicts would still fire under genuine algorithmic
independence remains open.** This entry does not resolve that question in either
direction, and neither does the batch it comes from.

## 4. What this changes, and what it does not

**It changes no number and not the fired termination branch.** Both reviews
independently confirm `T-C3LANE-OPEN-PARTIAL` fires and is robust under stricter
coverage readings, with or without this finding.

**It changes what the agreement is entitled to support.** The batch shows the
observables' fibre dispersion is nonzero and detectable through this pipeline, and
exceeds this specific corpus's own same-code reproducibility floor. It does **not**
show that two algorithmically independent implementations agree the dispersion is
real. Any citation of this batch's `EXCEEDS` verdicts must carry that qualification
in the same sentence — worth stating "on the covered cells, under code-shared
cross-environment reproducibility, not under independent verification."

## 5. What a successor must do, and what it must not

1. **Audit code lineage before a pre-registration names a source an "independent
   route."** A grep for shared function names, or better, a diff of the actual
   files, costs seconds and would have caught this before any number was measured.
2. **A cheap fix exists and does not require a new measurement of this batch's
   result.** A genuinely non-code-shared re-implementation of `ROUTE-I` for
   `lam1n`/`hkz` at `L7`/`L9`/`L11` (`d ≤ 40`, no new reduction), re-run against the
   same archived `ROUTE-P` values under the identical frozen comparison, would let
   a future batch cite `EXCEEDS` without this qualification. This campaign has built
   independent re-implementations from frozen prose four times already; the pattern
   is established and the cost is known.
3. **This is not a claim that shared code is disqualifying in general** — a
   carried-verbatim kernel re-executed elsewhere can be a legitimate
   reproducibility check. It is a claim that a pre-registration must **say which
   kind of check it is** before the numbers exist, because the two are
   indistinguishable after the fact from the raw agreement alone.

## 6. Scope and limits — read before citing

1. **THE FINDING IS REACHED BY TWO INDEPENDENT REVIEWS VIA DIFFERENT METHODS.** The
   Validator found it through git-plumbing and code-provenance probes; the Red Team
   found it through direct source diffing and a built cross-host control. Neither
   saw the other's write scope. Each is otherwise a single session and must be cited
   as such.
2. **INDEPENDENCE IS PROCEDURAL — NEVER MODEL-LEVEL, AND HERE NOT ENVIRONMENTAL
   EITHER.** AGENTS.md rule 12 is **UNMET AND UNWAIVED**. Both reviews ran on the
   SAME model and the SAME host as the producer. The irony is not lost and is stated
   directly: this batch's own reviews share the exact property this finding
   criticizes in the producer's pre-registration. This entry does not exempt itself
   from the standard it states.
3. **IT DOES NOT SAY WHETHER THE 18 (OR 16) `EXCEEDS` VERDICTS ARE TRUE UNDER
   GENUINE INDEPENDENCE.** That question is explicitly left open (§3). This is an
   instrument-design and disclosure finding, not a verdict on any observable's
   dispersion.
4. **NOTHING HERE IS AN IMPOSSIBILITY RESULT.** §5 names the cheap fix; it is
   untested, not unavailable.
5. **DERIVATIONS AND CONSTRUCTIONS, NOT THEOREMS.** That three files sharing a
   docstring-declared verbatim kernel produce bit-identical output is elementary;
   the built cross-host control on `rdet` is a construction, reported with its
   result exactly as measured, including that it fails to resolve the open question.
6. **IT ESTABLISHES NOTHING ABOUT ANY LATTICE.** `BATCH-fbb639` adjudicates no
   proposition about a lattice, revalidates no prior batch, retires no prior
   amendment, and closes, pauses and completes nothing.

## Identifier provenance

`KN-FIND-9b5df0` was drawn **without scanning state** (AGENTS.md rule 14) and then
confirmed in **two scopes** by the dispatching session at the Coordinator's request:
worktree `tools/allocate_id.py --check` (well-formed, 0 occurrences across 6,611
identifier-bearing paths) **and** a cross-ref sweep of the 25 most-recently-updated
remote branches (0 hits), plus confirmation that it is not tracked under
`knowledge/findings/` on `origin/main`. Recorded as two-scope confirmed and **never**
as `--check` alone — `--check` answers from the working tree only, which is how the
same tool once reported two identifiers "free" while both were already bound on a
pushed branch. The Coordinator that specified this entry's content held no shell and
claimed neither check as its own; both were performed by the dispatching harness
session.

## Superseding relationship

This entry does not narrow any prior finding in this goal. **No prior entry is
edited and no `superseded_by` is set** on any of them. It stands as an independent
instrument-design lesson, cross-referenced from `DEC-20260813-28d7b2`'s
`knowledge_promotion` field.
