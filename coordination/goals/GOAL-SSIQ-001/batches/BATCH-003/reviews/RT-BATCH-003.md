# RT-BATCH-003 — Red Team review of GOAL-SSIQ-001 BATCH-003 (EXP-SSIQ-58b642, RUN-SSIQ-58b642-a, VOID)

**Task:** `TASK-20260805-5dba23` · **Goal:** `GOAL-SSIQ-001` · **Batch:** `BATCH-003`
**Role:** red-team · **Attacks interpretation and scope, not the Validator's arithmetic.**
The independent re-derivation of C-CAL-GAP's recovered-gap numbers and the independent
check of the WISDE data-gap claim (re-fetching, re-parsing `results<p>.sage`) belong to the
Validator (`TASK-20260805-2c086d`) and are not duplicated here. I read the Validator's
subject matter (what WISDE's file actually contains) but did not re-fetch it myself; every
number below is copied from committed artifacts and labelled as such.

**Artifacts read, all confirmed byte-identical between the frozen snapshot commit
`3c117cbc` and the working tree (`git diff 3c117cbc -- experiments/EXP-SSIQ-58b642` empty
at review time):**

| package | contents |
|---|---|
| `experiments/EXP-SSIQ-58b642/specification.yaml` | frozen contract, `frozen_at: 2026-08-05` |
| `experiments/EXP-SSIQ-58b642/implementation/*.py` | `build_isogeny_graph.py`, `descent_hitting_time.py`, `calibration_synthetic.py` |
| `experiments/EXP-SSIQ-58b642/runs/RUN-SSIQ-58b642-a/*` | `manifest.yaml`, `raw-result.json`, `execution_report.yaml`, `source_access_log.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log` |
| `coordination/.../BATCH-003/reviews/RT-PREFREEZE-EXP-SSIQ-58b642.md` | predecessor's seven pre-freeze findings (PF-1..PF-7), verdict FREEZE-WITH-FIXES |
| `coordination/.../BATCH-003/tasks/PF5-research/pf5_degenerate_vertex_convention.md` | PF-5 zero-compute research task |
| `experiments/EXP-SSIQ-4de240/{specification.yaml,runs/RUN-SSIQ-4de240-a/*}` | BATCH-002's prior run, its `M_GRAD` arm (`NOT_MEASURED`, deviation D4) |
| `ledger/goals/GOAL-SSIQ-001/goal.yaml`, `ledger/hypotheses/H-SSIQ-18dc91.yaml` | levers L1-L5/N5, GD-1..GD-5, standing conditions |

Compute performed: none beyond `grep`/`git diff`/`git log` over already-committed text;
every quoted number is copied, not recomputed.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified (orchestration.adapter doctor --probe not run)
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. The xhigh
    reasoning-effort component of review-adversarial is neither settable nor
    verifiable from inside a subagent.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    Per ledger/goals/GOAL-SSIQ-001/goal.yaml runtime.runtime_note: under this
    harness every policy alias falls back to the session model, so producer
    (Executor TASK-EXP-SSIQ-58b642-executor), predecessor Red Team
    (RT-PREFREEZE-EXP-SSIQ-58b642), and this review are SESSION-independent
    only, never model-independent. Nothing below should be read as
    corroboration from a distinct model.
```

---

## Bottom line up front

Phase 0 and the graph-construction phase of this run are genuinely good, checked work —
better instrumented than either of the two prior batches this campaign has run. The VOID
outcome is the right report of what happened, and the refusal to fabricate a real-label arm
is correct reasoning, not merely a defensible one. But the run exists because of a defect
that was not merely "hard to see in advance" — it was **already written down, in a
Coordinator-committed, ledger-archived record that this very contract cites by name**, and
neither the contract's author nor the pre-freeze Red Team pass connected the two documents.
That is a new, distinct contract defect in the GD-4/GD-5 family, and I name it GD-6 below.
Separately, this run surfaced a real structural finding (PD-2) that undermines part of
PF-5's own resolution, and it leaves on the table an unexplored, plausibly cheaper
unblocking route than the one the Executor's escalation note offers.

---

## FRONT 1 — Could this have been caught before freeze, and by whom?

**Yes. This was not merely checkable — it was already checked, written down, and committed
to the ledger a batch earlier, and the frozen contract cites the exact document that says
so, without anyone reading past the citation.**

The frozen contract's `inputs.graph_construction.delta_E_cross_reference` clause reads: *"cross-reference delta_E from the WISDE released data used in EXP-SSIQ-4de240 (same source, same acquisition route)."* This assumes WISDE's per-prime release supplies a **per-j-invariant** `delta_E` label, in exactly the shape GD-4 describes: an instrument's capability asserted without the cheap check that would have refuted it.

The cheap check existed and had already been performed. `experiments/EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/execution_report.yaml`, committed at `41a4aebd` (2026-08-05 04:11:42Z) and superseded (not retracted) at `3fee6655` (04:48:31Z) — **both more than an hour before** the BATCH-003 draft contract was authored at `c3a94f56` (05:52:37Z) — records, under the `M_GRAD` secondary metric:

> "The released dataset gives, per prime, a Z-basis of each maximal order type and its successive minima -- but NOT the 2-isogeny adjacency of the supersingular graph. Recovering it means enumerating the norm-2 left ideals of each order, computing their right orders, rebuilding each right order's Gross lattice and Eisenstein-reducing it: reimplementing the authors' pipeline and GENERATING the neighbour delta values in session."

and the WISDE README, already quoted verbatim in that same committed package: *"resultsp.sage contains a list containing a basis for each maximal order... as well as the tuple (N1,N2,N3)."* Neither passage mentions a j-invariant field, a curve identifier, or anything that links an order/basis row to a specific computed vertex. A five-minute re-read of the one document `EXP-SSIQ-58b642` names as its own data source — the document its own PD-1 later cites verbatim ("EXP-SSIQ-4de240's M_GRAD arm already identified, for the identical reason, as 'reimplementing the authors' pipeline'") — would have surfaced this before a single line of the BATCH-003 contract's `delta_E_cross_reference` section was written. This is a **cheaper** check than any GD-4/GD-5 repair required: not a calculation to perform, but a citation to actually read.

The pre-freeze Red Team pass (`RT-PREFREEZE-EXP-SSIQ-58b642.md`) also missed it, and its own text shows the gap: Section 9 ("Attacked and held") credits "the correctness oracle against WISDE released δ_E (assumption 2 / C-CONNECTIVITY)" as "a real, checkable invalidation trigger, not an assertion" — but that is the **vertex-count** check (which does work, and did pass for all 12 primes), not the **per-vertex label** mechanism the contract's confirmatory metric actually depends on. The seven PF findings interrogate the M-GAP *estimator* (calibration, censoring, tie-breaking) exhaustively but never interrogate whether the *label* the estimator consumes is obtainable at all. That is the same shape as GD-4 and GD-5 — checking that a machine computes correctly without checking that it has the material to compute on.

**This is a new named Coordinator contract defect: propose GD-6.**

> **GD-6 (proposed).** A frozen contract's `delta_E_cross_reference` clause assumed a
> per-vertex (per-j-invariant) `delta_E` linkage exists in the WISDE release "same source,
> same acquisition route" as `EXP-SSIQ-4de240`, without re-reading `EXP-SSIQ-4de240`'s own
> already-committed `M_GRAD` finding (`execution_report.yaml`, deviation D4, frozen at
> `41a4aebd`/`3fee6655`, over an hour before this contract was drafted) that the release is
> indexed by abstract maximal-order type, not by curve or j-invariant, and that recovering
> that linkage needs the Deuring correspondence's hard ("curve → ideal") direction. The
> pre-freeze Red Team pass (`RT-PREFREEZE-EXP-SSIQ-58b642.md`) audited the M-GAP estimator's
> seven failure modes exhaustively but never audited whether its input label was obtainable,
> and its own "attacked and held" section conflates the vertex-*count* check (which works)
> with the per-vertex *label* mechanism (which does not). Distinct from GD-4/GD-5 in kind:
> those needed a fresh cheap calculation nobody ran; this needed a fresh cheap *re-read* of a
> document already sitting in the repository and already cited by name in the very clause
> that turned out to be false. Mitigation for BATCH-004 onward: before a contract names an
> external dataset as ground truth at a stated granularity ("per-vertex," "per-j-invariant"),
> the pre-freeze Red Team pass explicitly checks that granularity against the literal
> file-format evidence already on record for that dataset (a prior `source_access_log.yaml`
> or execution report), not merely against the estimator built on top of it.

This does **not** repeat GD-4/GD-5's shape exactly, so it should be recorded as its own
item rather than folded into GD-4/GD-5: those were about an obstruction/estimator that
could not do arithmetic asked of it; this is about a contract's *input* that could not
supply the granularity asked of it, discoverable by reading rather than computing, and
discoverable from a document the contract itself already pointed at.

---

## FRONT 2 — Is VOID the right call, or was there a legitimate path to a real result?

**VOID is the right call for the route attempted. The refusal to fabricate a random label
is correct, non-negotiable reasoning, not merely defensible caution. But "full Deuring
correspondence is the only route" overstates the search the Executor actually ran, and a
cheaper, more directly relevant alternative was left unexamined.**

### 2.1 The refusal to fabricate is correct, and provably so, not just prudent

If the only information available is the **aggregate** `delta_E` multiset for a prime (which
WISDE does supply, and which the graph's own `delta1_locus_cross_check` and
`normalisation_check` independently confirm matches), then assigning that multiset's values
to BFS-discovered vertices **without any structural linkage** is not an approximation of a
real-label arm — it is, up to relabelling, *exactly* what `C-NULL-LABEL` already computes: a
uniformly random permutation of the same value multiset onto the same graph. Running it and
calling it "real" would not weaken the evidence, it would duplicate a control under a
different name and let a reviewer mistake a second null for a signal. The Executor's
reasoning here is airtight given the premise (no linkage available), and I did not find a
way to break it.

### 2.2 What the Executor's escalation options leave out

PD-1's `escalation` field offers three options: (a) narrow to a binary `delta_E=1`-vs-not
label; (b) a dedicated successor task implementing the full Deuring-correspondence
computation; (c) a different ground-truth source. A fourth, cheaper option is not named:

**Compute `delta_E` directly, in-session, for a handful of small primes, by the same route
AOV themselves used to build WISDE — a bounded search over `B`-smooth isogeny degrees from
`E` to `E^{(p)}` — rather than reconstructing WISDE's order-type index.** This is materially
different from, and cheaper than, "reimplementing the authors' pipeline" in the sense PD-1
means: PD-1's blocked route requires solving the *curve → ideal* direction of the Deuring
correspondence (computing `End(E)` from `E`), which is the heuristically hard direction —
the same direction the `OneEnd`/`EndRing` problems this entire campaign studies are built
on. Computing `delta_E` by exhaustive smooth-degree search, by contrast, never touches the
endomorphism ring at all; it is a direct search over isogeny *degrees*, exactly the object
`F1`/`F3` of `exponent_budget` already describe, bounded by the same
`(p/2)^{1/3}`-scale degree this campaign already treats as tractable to reason about. At the
toy primes tested here (`delta_E <= ~22`, graphs up to `~1800` vertices), such a search is
plausibly bounded well inside this run's own budget, since it is asymptotically the same
search AOV performed exhaustively for every prime `p <= 22000` to produce the WISDE release
in the first place. **This should have been named as a fourth escalation option, and its
absence is itself a gap in PD-1's own accounting**, not a fatal flaw in the VOID call.

There is a second, sharper version of this same point: PD-1's stated blocker conflates two
different directions of the correspondence. "KLPT-style connecting-ideal search plus
ideal-to-isogeny translation" is the *efficient* `ideal → isogeny` direction (this is what
KLPT is *for*); the actually-hard direction is `curve → ideal` (computing `End(E)`), which
is not what KLPT accelerates. The PD-1 text should be read as pointing at the hard
direction's cost, but the wording as written could mislead a future reader into thinking
"KLPT" names the bottleneck, when the bottleneck is the endomorphism-ring computation KLPT
presupposes as already known. This is worth a wording correction in any successor task, not
a re-run of this one.

### 2.3 Did Phase 0 test the right risk?

Phase 0 (C-CAL-GAP) is a genuinely validated instrument-bias gate (see Front 3a) but it
tests exactly one failure mode: whether the M-GAP *estimator* recovers a known true gap
under a stated finite-size bias mechanism. It says nothing about whether the *inputs* to
that estimator (the real-label arm's per-vertex data) exist. **C-CAL-GAP is necessary but
was never sufficient, and the frozen contract's structure treated it as if clearing Phase 0
cleared the whole risk surface.** The gate that would have caught this — a data-availability
pre-check on the named external source, at the stated granularity, before any estimator
work is designed around it — does not exist anywhere in this campaign's contract template.
I recommend the Coordinator add it as a standing **Phase -1** gate, distinct from and prior
to C-CAL-GAP: *"fetch and inspect (or re-cite a prior committed inspection of) the exact
external file the contract's `inputs` section names, at the exact granularity the contract's
metrics require, before designing an estimator around it."* This is the direct structural
fix GD-6 calls for, stated as a process requirement rather than a one-off correction.

---

## FRONT 3 — What did this run actually buy the campaign?

VOID is not zero information here. Four separable products:

### 3a. C-CAL-GAP is now a validated, reusable instrument

Recovered gap errors of `0.022`, `0.008`, `0.025` against a `+-0.10` tolerance on three
synthetic pairs, including a saturating/capped variant that genuinely exercised the
sentinel/censoring code path (`trapped_fraction` `0.16`-`0.25`, not trivially zero) without
corrupting the recovered gap. This is exactly the standing practice GD-4 adopted ("run the
frozen estimator on an object with the target exponent before freezing the contract"),
executed rather than merely stated, and it is **independent of whether this run's real arm
ever completes** — any future contract in this campaign that needs to sign-test a difference
of two fitted exponents through a shared estimator now has a working template to copy rather
than design from scratch, with a passing precedent rather than an assertion.

### 3b. The graph-construction pipeline is now a validated, reusable tool

`C-CONNECTIVITY` (exact match to `floor(p/12)+e` for all 12 primes), `M-DEGSEQ` (every
vertex multiset-degree exactly 3, all 12 primes), `C-EDGELIST` (0 mismatches at `p=2437`,
203 vertices, against an independent computation), and the `delta_E=1`-locus cross-check
(exact match to WISDE's `N(1,p)` for all 12 primes) all passed. This is real, checked
infrastructure — `Phi_2` root-finding over `F_{p^2}`, BFS enumeration, multiset-adjacency
bookkeeping — independent of the labelling problem that blocked the confirmatory metric, and
it is exactly the tool a successor task implementing the direct-computation route (§2.2)
would build on rather than re-derive.

### 3c. PD-2 is a real finding, not bookkeeping, and it weakens part of PF-5's own resolution

PF-5's resolution rests on CGL's stated reason for restricting to `p = 1 (mod 12)`: "the
elliptic curves have no automorphisms other than `+-1`" at that residue, which the frozen
contract's `degenerate_j_handling` reads as sufficient for "a genuine SIMPLE undirected
3-regular graph with no multiplicity bookkeeping at all." PD-2 found, empirically and by two
independent methods (squarefree-part degree via `gcd(Phi_2(X,v), X^{p^2}-X)`, and
`gcd(Phi_2, d/dX Phi_2)`), that 0-3 vertices per prime (out of 203-1800) have a genuine
double edge to their own Frobenius conjugate `v^p`, at `p = 1 (mod 12)` — exactly the residue
class PF-5 chose *because* it should have no automorphism-driven multiplicity.

This matters beyond bookkeeping: `Aut(E) = {+-1}` rules out multiplicity that arises from
**automorphisms of the curve itself**, but PD-2's mechanism is different — a vertex's own
three 2-isogenies landing on the same target curve up to isomorphism looks like a
**Galois-action-on-`E[2]`** phenomenon (the Frobenius action on the three order-2 subgroups
of `E[2]` fixing more than one subgroup as a set), not a vertex-automorphism phenomenon.
CGL's cited reason is therefore **necessary but not sufficient** for the "genuine simple
graph" claim the contract asserted, and the general degenerate-vertex/multiplicity question
Sutherland's Remark 8 and CGL both leave unresolved (PF-5's own finding) may be entangled
with this second mechanism even in the "easy" `p ≡ 1 (mod 12)` residue class the campaign
picked specifically to avoid the automorphism-driven version. Forward guidance: any successor
task computing the deferred `p != 1 (mod 12)` multiplicity table (PF-5's option (a)) should
budget for **two** mechanisms, not one — automorphism-driven multiplicity at `j=0`/`1728`
*and* Galois-action-driven multiplicity at ordinary vertices including at `p ≡ 1 (mod 12)` —
and should not treat `Aut(E) = {+-1}` as closing the question even for the residue class
where it holds.

### 3d. The cheaper unblocking route is the direct in-session smooth-degree computation, not full Deuring reconstruction

As argued in §2.2: extending the already-validated graph-construction tool (§3b) with a
bounded, disclosed smooth-degree isogeny search for `delta_E`, run at the same toy primes
already fetched, is plausibly the cheapest unblocking step — cheaper than reconstructing
WISDE's order-type index (which requires the hard direction of Deuring) and cheaper than a
new external dataset search. It should go through the same discipline this campaign now
applies to everything else: a cheap pre-compute feasibility estimate (cost of the
smooth-degree search at the smallest pre-registered prime) before a full contract is frozen
around it, exactly the lesson GD-4 already states.

One candidate the Executor's own escalation list offers — option (a), the binary
`delta_E=1`-vs-not label — deserves a caution before BATCH-004 treats it as a cheap win. With
only a binary label, "greedy descent on delta_E" degrades to "biased walk toward a known
target set using full graph knowledge," which is not obviously a test of a `delta_E`
gradient at all: a BFS-informed shortest-path-to-target policy would beat an undirected
random walk *by construction*, regardless of whether `delta_E` carries any exploitable
structure, because full knowledge of the target set plus the already-built graph is enough
on its own. A naive binary-label redesign risks testing "does having a map help" rather than
"does `delta_E` predict distance," which is not what L4 asks. If pursued, it needs its own
design pass, not an assumption of viability.

---

## Numbered objections

1. **[HIGH — new contract defect, GD-6]** The frozen contract's `delta_E_cross_reference`
   clause assumed WISDE supplies a per-vertex `delta_E` label without re-reading
   `EXP-SSIQ-4de240`'s own already-committed `M_GRAD` finding that WISDE is indexed by
   abstract order type, not j-invariant — a finding available over an hour before this
   contract was drafted and cited by the contract itself as its data source. Resolution
   route: adopt GD-6 as written above; add a "Phase -1" data-availability pre-check to the
   Red Team pre-freeze standing practice (GD-4's mitigation), scoped to checking a named
   external source's granularity against its own prior committed inspection before any
   estimator is designed around it.
2. **[MEDIUM]** The pre-freeze Red Team pass's "attacked and held" section credited the
   WISDE correctness oracle generally, without separating the vertex-*count* check (which
   works) from the per-vertex *label* mechanism (which did not) — a conflation that let the
   load-bearing assumption pass unexamined. Resolution route: future pre-freeze passes state
   explicitly, for every external-data dependency, which specific field/granularity is
   checked and which is merely assumed.
3. **[MEDIUM]** PD-1's escalation options omit a fourth, likely cheaper route: direct
   in-session computation of `delta_E` by bounded smooth-degree isogeny search (AOV's own
   method), which does not require solving the hard "curve → ideal" direction of the Deuring
   correspondence at all. Resolution route: any successor task scopes and costs this option
   explicitly before defaulting to the full-Deuring-correspondence route PD-1 names.
4. **[LOW-MEDIUM, wording only]** PD-1's stated blocker ("KLPT-style connecting-ideal search
   plus ideal-to-isogeny translation") names the efficient `ideal → isogeny` direction as the
   cost driver when the actual bottleneck is the hard `curve → ideal` direction (computing
   `End(E)`) that KLPT presupposes as already solved. Resolution route: correct the wording
   in any successor task's problem statement so a future reader does not budget for the wrong
   sub-problem.
5. **[MEDIUM — genuine finding, not a defect]** PD-2 (double edges to the Frobenius
   conjugate at `p = 1 mod 12`) shows PF-5's resolution — "`Aut(E) = {+-1}` ⇒ genuine simple
   graph" — is necessary but not sufficient; a second, Galois-action-driven multiplicity
   mechanism operates even at the "easy" residue class. Resolution route: record this as a
   knowledge finding (candidate `KN-FIND`) with forward guidance to the deferred `p != 1 (mod
   12)` multiplicity successor, per §3c; do not let the contract's superseded
   "genuine SIMPLE ... graph" language stand uncorrected in any future citation of it.
6. **[LOW]** The binary `delta_E=1`-vs-not label option (PD-1 escalation (a)) risks
   collapsing into a trivial "does full graph knowledge beat blind random walk" comparison
   rather than a test of a `delta_E` gradient specifically, unless redesigned. Resolution
   route: any successor task using this option must show its comparison cannot be won by
   graph-distance-to-target-set knowledge alone, before being treated as answering L4's
   question.

## Required controls (for any successor task)

- A "Phase -1" data-granularity check: fetch or re-cite a prior committed inspection of the
  named external source's literal per-record fields, at the exact granularity a contract's
  metrics require, before designing an estimator around it (objection 1).
- A bounded feasibility estimate (cost at the smallest pre-registered prime) for the direct
  smooth-degree `delta_E` computation, run and reported before a full successor contract is
  frozen around it — the same discipline C-CAL-GAP now applies to estimator bias, applied
  here to a compute-cost claim (objection 3).
- If the binary-label route is pursued, a null-object control showing the comparison is not
  won by graph-distance-to-target-set knowledge alone, independent of any `delta_E`
  structure (objection 6).

## Counterexample or mutation

None required against a mathematical claim — this run makes none (`asymptotic_claim: null`,
correctly held). The relevant mutation is a **document mutation**, already performed by this
review: re-reading `EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/execution_report.yaml`'s `M_GRAD`
section, already committed at `41a4aebd` before the BATCH-003 contract was drafted, would
have surfaced the exact defect this run discovered at run time. That the same information
was available and unread is the counterexample to any claim that this failure mode was
undiscoverable before freeze.

## Baseline comparison

Not applicable in the algorithm-comparison sense — `H-SSIQ-18dc91` claims no algorithm and
`asymptotic_claim` is correctly null; there is no Pollard-rho/BSGS/specialized-baseline
comparison for a gradient-existence screen. The relevant baseline for this review is the
campaign's own prior instrument discipline: BATCH-002's `EXP-SSIQ-4de240` (uncalibrated
estimator, GD-4) and BATCH-003's own pre-freeze pass (seven estimator-level findings, all
resolved) both improved the estimator machinery; this run shows the campaign has not yet
extended the same scrutiny to its *data-source* assumptions, which is exactly what GD-6
names.

## Heuristic challenges

`H-SSIQ-18dc91.heuristic_assumptions` is correctly empty (this is a gradient-existence
screen, not a proof-oriented claim, per its own `proof_search_map.not_applicable_reason`) —
attacked and held, no defect found here. The implicit premise of the whole experiment design
— "WISDE's released data can supply per-vertex ground truth at this granularity" — is not a
mathematical heuristic but an **empirical availability assumption**, and it is the one this
review's Front 1 shows should have been checked, not stated as a heuristic requiring a
random-model justification.

## Cost model challenges

Phase 0 and graph construction are within budget by wide margins (construction: 0.4-4.5s per
prime against a 900s per-smallest-prime stopping rule). No cost-model defect found in what
was executed. The cost model NOT stated anywhere in this package is the one that matters for
BATCH-004: neither PD-1's escalation options nor this review can yet bound the cost of full
Deuring-correspondence reconstruction or of the direct smooth-degree search named in §2.2 —
both need their own pre-compute feasibility pass before a successor contract is frozen,
exactly the discipline GD-4 already requires and this run's own C-CAL-GAP precedent
demonstrates is cheap to apply.

## Reduction and scope challenges

No scheme from the source's affected-vs-safe lists appears anywhere in this contract or run;
no scope widening found. `H-SSIQ-18dc91.scope_ceiling` (toy, up to ~2000 vertices) is
correctly stated and nothing in this run's artifacts exceeds it — the VOID outcome, if
anything, under-claims relative to what a careless reading might extract from the passing
Phase-0/graph-construction results.

## Proof architecture challenges

`proof_search_map.not_applicable_reason` is correctly reasoned (gradient-existence screen,
not a proof-oriented proposal) and this review found no place section 8's audits would have
caught something this reasoning missed — attacked and held, same verdict as the pre-freeze
pass.

---

## BATCH-004 recommendation, ranked

1. **Highest priority: unblock L4's real-arm labelling problem via the direct in-session
   smooth-degree `delta_E` computation (§2.2, §3d), NOT full Deuring-correspondence
   reconstruction.** This remains the only lever whose ceiling meets the goal's `p^{1/4}`
   target, and this run neither closed it nor showed the direct-computation route
   infeasible — it showed only that the *WISDE-order-type-matching* route is blocked. Gate
   it on a cheap pre-compute feasibility estimate (cost of the smooth-degree search at the
   smallest pre-registered prime) before freezing a successor contract, per GD-4's standing
   practice. This is a genuinely different, cheaper task than the one PD-1's escalation
   option (b) describes.
2. **Formally retire REC-1b.** This run independently confirms `EXP-SSIQ-4de240`'s `M_GRAD`
   finding: the same WISDE order-type-vs-j-invariant gap blocks both. REC-1b is dead by the
   same mechanism twice over; close it with a citation to both runs rather than leaving it
   open on a technicality.
3. **N5 scoping pass** (structurally different auxiliary targets — oriented curves,
   prescribed-torsion, higher-dimensional) remains zero-compute and was already raised in
   priority by the goal record's `next_action` item (ii); nothing in this batch changes that
   ranking, so it stays above the deferred `p != 1 (mod 12)` successor.
4. **Deferred `p != 1 (mod 12)` multiplicity successor** stays lowest of the four named
   items. PD-2 (§3c) raises its cost estimate rather than lowering it: the multiplicity
   question is now known to be entangled with a Galois-action mechanism even in the "easy"
   residue class, so a future attempt should budget for two mechanisms, not one, before
   committing compute.
5. **The binary-label redesign (PD-1 option (a))** is not ranked above item 1: it is cheap
   but risks being uninformative (§3d, objection 6) unless redesigned with its own null
   control first.

The campaign should **not pivot away from L4**. Nothing in this run's VOID outcome is
evidence against a computable `delta_E`-gradient existing — it is evidence only that one
specific data-linkage route to testing it is closed. The direct-computation alternative is
untested, plausible, and reuses infrastructure this run already validated (§3a, §3b).

---

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-58b642/` as frozen at `3c117cbc`: Phase 0 (C-CAL-GAP) and
the graph-construction/correctness-gate machinery (`C-CONNECTIVITY`, `M-DEGSEQ`,
`C-EDGELIST`, the `delta_E=1`-locus cross-check) are genuinely validated, reusable
instruments, checked by independent methods where checked at all. The confirmatory metric
(`M-GAP` on real labels) could not be computed because WISDE's released data lacks the
per-vertex linkage the contract's own `delta_E_cross_reference` clause assumed — an
assumption that was checkable, and in substance already checked and recorded, in a
Coordinator-committed sibling record over an hour before this contract was drafted (GD-6).
VOID is the correct report of this outcome; it is neither a detection, an
unresolved-by-this-test result, nor evidence against L4's obstruction in either direction.
PD-2 shows PF-5's "no automorphism ⇒ genuine simple graph" resolution is incomplete even in
the residue class it chose to avoid the problem. Nothing here licenses closing lever L4 or
pausing this goal; the cheapest next step is a direct, in-session, bounded `delta_E`
computation, not the full Deuring-correspondence route the run's own escalation note leads
with.

## Next concrete action

Coordinator: (1) record GD-6 in `ledger/goals/GOAL-SSIQ-001/goal.yaml`'s
`known_defects_of_this_record`, alongside GD-4/GD-5, with the mitigation stated above as a
standing "Phase -1" pre-freeze practice; (2) route PD-2 to a `KN-FIND` candidate with the
forward guidance in §3c, not left implicit inside a VOID run's execution report; (3) task a
bounded, zero-compute feasibility estimate (cost of a smooth-degree `delta_E` search at the
smallest pre-registered prime, extending `build_isogeny_graph.py`) as the pre-freeze
prerequisite for a BATCH-004 successor to `H-SSIQ-18dc91`, before committing to either PD-1's
named escalation routes.

## Overall verdict

**CONFIRM-SCOPED.** The VOID outcome, the refusal to fabricate a label, and the
graph-construction/Phase-0 machinery are confirmed as reported and as sound within their
stated scope. The interpretation is NOT fully endorsed as complete: a new contract defect
(GD-6) should be named, PD-1's escalation options are incomplete (a cheaper route exists and
was not scoped), and PD-2's implication for PF-5's own resolution should be carried forward
explicitly rather than left as a footnote inside an execution report.

```yaml
red_team_report:
  id: RT-BATCH-003
  task_id: TASK-20260805-5dba23
  claim_under_review: >-
    EXP-SSIQ-58b642 / RUN-SSIQ-58b642-a (frozen snapshot 3c117cbc): Phase 0 (C-CAL-GAP)
    passed on all three synthetic pairs; graph construction and all correctness gates
    (C-CONNECTIVITY, M-DEGSEQ, C-EDGELIST, delta_E=1-locus cross-check) passed for all 12
    pre-registered primes; the confirmatory real-label M-GAP metric could not be computed
    because WISDE's released data lacks a per-vertex delta_E linkage; the run terminates
    VOID per the frozen decision rule's underspecification clause, not DETECTED, not
    UNRESOLVED-BY-THIS-TEST, and not FALSIFIED/REFUTED.
  objections:
    - "OBJ-1 [HIGH, new defect GD-6]: the delta_E_cross_reference clause assumed a per-vertex WISDE linkage without re-reading EXP-SSIQ-4de240's own already-committed M_GRAD finding (frozen at 41a4aebd, over an hour before this contract was drafted at c3a94f56) that WISDE is indexed by abstract order type, not j-invariant. Checkable, and in substance already checked, before freeze."
    - "OBJ-2 [MEDIUM]: RT-PREFREEZE's 'attacked and held' section conflated the WISDE vertex-count check (which works) with the per-vertex label mechanism (which did not), letting the load-bearing assumption pass seven findings unexamined."
    - "OBJ-3 [MEDIUM]: PD-1's escalation options omit a fourth, likely cheaper route -- direct in-session bounded smooth-degree delta_E computation (AOV's own method), which avoids the hard curve-to-ideal direction of Deuring entirely."
    - "OBJ-4 [LOW-MEDIUM, wording]: PD-1 names 'KLPT-style ... translation' as the cost driver when the actual bottleneck is the hard curve-to-ideal direction KLPT presupposes as already solved."
    - "OBJ-5 [MEDIUM, genuine finding]: PD-2 (double edges to the Frobenius conjugate at p=1 mod 12) shows PF-5's 'Aut(E)={+-1} implies genuine simple graph' resolution is necessary but not sufficient -- a Galois-action-on-E[2] mechanism produces multiplicity even in the residue class chosen to avoid the automorphism-driven version."
    - "OBJ-6 [LOW]: the binary delta_E=1-vs-not escalation option risks testing 'does full graph knowledge beat blind random walk' rather than a delta_E gradient specifically, unless redesigned with its own null control."
  required_controls:
    - "Phase -1 data-granularity check: verify a named external source's literal per-record fields against a stated metric's required granularity, using any prior committed inspection already on record, before designing an estimator around it."
    - "Bounded feasibility estimate for the direct smooth-degree delta_E computation at the smallest pre-registered prime, before freezing a successor contract around it."
    - "If pursued, a null-object control for the binary-label redesign showing the comparison is not won by graph-distance-to-target-set knowledge alone."
  counterexample_or_mutation: >-
    Document mutation, not a code mutation: re-reading
    experiments/EXP-SSIQ-4de240/runs/RUN-SSIQ-4de240-a/execution_report.yaml's M_GRAD
    section -- committed at 41a4aebd, over an hour before the BATCH-003 draft contract
    (c3a94f56) was authored, and explicitly named as this contract's own data source --
    would have surfaced the exact data-availability gap this run discovered only at
    execution time. The information's prior existence and its being unread is the
    counterexample to any claim this was undiscoverable before freeze.
  baseline_comparison: >-
    Not applicable in the algorithm-comparison sense (asymptotic_claim is correctly null,
    no Pollard-rho/BSGS/specialized-baseline comparison exists for a gradient-existence
    screen). Relevant baseline is the campaign's own prior instrument discipline: BATCH-002
    (GD-4, uncalibrated estimator) and BATCH-003's own pre-freeze pass (seven estimator-level
    findings, resolved) both improved estimator scrutiny; this run shows the same scrutiny
    has not yet been extended to data-source assumptions, which GD-6 names.
  heuristic_challenges:
    - "H-SSIQ-18dc91's empty heuristic_assumptions is correctly reasoned (gradient-existence screen, not a proof-oriented claim) -- attacked and held. The unstated premise this review challenges is an empirical data-availability assumption, not a heuristic requiring a random-model justification."
  cost_model_challenges:
    - "Phase 0 and graph construction are within budget by wide margins (0.4-4.5s/prime against a 900s stopping-rule cap); no defect found in what was executed."
    - "Neither PD-1's Deuring-reconstruction option nor this review's proposed direct smooth-degree-search alternative has a stated cost estimate; both need a pre-compute feasibility pass before a successor contract is frozen, per GD-4's own standing practice."
  reduction_and_scope_challenges:
    - "No scheme from the source's affected-vs-safe lists appears anywhere in this contract or run; no scope widening found."
    - "scope_ceiling (toy, up to ~2000 vertices) is correctly stated and not exceeded by anything reported."
  proof_architecture_challenges:
    - "proof_search_map.not_applicable_reason is correctly reasoned; no place found where section 8's audits would have caught something this reasoning missed -- attacked and held, same verdict as the pre-freeze pass."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-58b642/ as frozen at 3c117cbc: Phase 0 and the
    graph-construction/correctness-gate machinery are genuinely validated, reusable
    instruments. The confirmatory M-GAP metric could not be computed because WISDE lacks the
    per-vertex linkage the contract assumed -- an assumption that was checkable, and in
    substance already checked and recorded, in a Coordinator-committed sibling record over
    an hour before this contract was drafted (GD-6). VOID is the correct report; it is
    neither a detection nor evidence against L4's obstruction in either direction. PD-2 shows
    PF-5's resolution is incomplete even in the residue class it chose to avoid the problem.
    Nothing here licenses closing L4 or pausing the goal.
  next_concrete_action: >-
    Coordinator records GD-6 in ledger/goals/GOAL-SSIQ-001/goal.yaml's
    known_defects_of_this_record with the "Phase -1" data-granularity mitigation; routes
    PD-2 to a KN-FIND candidate with forward guidance to the deferred p != 1 (mod 12)
    successor; and tasks a bounded, zero-compute feasibility estimate for a direct
    smooth-degree delta_E computation (extending build_isogeny_graph.py) as the pre-freeze
    prerequisite for BATCH-004's successor to H-SSIQ-18dc91, before committing to either of
    PD-1's named escalation routes.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-003/reviews/RT-BATCH-003.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: "none beyond grep/git diff/git log over already-committed text; every quoted number copied, not recomputed"
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the Coordinator's
    ledger/snapshot archive task commits this report; it is not durable until that archive
    exists. Per write_scope, this task did not modify experiments/EXP-SSIQ-58b642/ or any
    ledger record.
  verdict: CONFIRM-SCOPED
```
