# QM-STOPPING obstruction analysis (begun) — BATCH-040 / TASK-20260730-131

- Goal: GOAL-SSI-001
- Idea: IDEA-20260729-001 (CSIDH-COLLIMATION-FC0-R2)
- Decision ref: DEC-20260730-037 · Evidence input: EV-SSI-039 · Red-team input: RT-20260730-129
- Role: executor (observations only; no state transition)
- Git revision at execution: 912e45f90b1a7c77ef9d8c1c7318cba6e7e827dd

<!-- MACHINE-READABLE STATUS (harness-checked) -->
```yaml
OBSTRUCTION_ANALYSIS_STATUS: unverified
named_obstruction: false
meets_inventor_protocol_s4: false
is_closure_claim: false
fatigue_report_acknowledged: true
qm_stopping_control_result: FAIL
tau_invented: false
joint_finiteness_established: false
```

## 0. What this document is, and is not

This **begins** the QM-STOPPING obstruction analysis demanded by DEC-20260730-037
and framed by RT-20260730-129. Per inventor-protocol §4, a **closure** requires a
*named obstruction + an argument + forward guidance*, and a mere count of
screened-and-rejected mechanisms is a **fatigue report** whose honest status is
`unverified`.

**Honest disposition of this document: `unverified`.** No obstruction meeting the
§4 standard can yet be named. Below I (a) state precisely what QM-STOPPING is, (b)
record the fatigue fact honestly, (c) articulate a *candidate* obstruction as an
explicit hypothesis and show why it does **not** yet meet the §4 standard, and (d)
give forward guidance naming what a real obstruction argument would have to
establish. This is a beginning, not a closure. It asserts no clearance, no
breakthrough, no completion, and invents no τ.

## 1. What QM-STOPPING is

QM-STOPPING is the open sub-question of QUERY_MEMORY concerning the **stopping
rule** of the FC0 collimation-sieve lifetime: whether there exists a
**source-compatible, Verify-relative stopping time τ** bounding the number of
sieve attempts before acceptance, together with **joint finiteness** of the
resource vector (queries Q, space S, P, C, and +H). The negative control has
returned `control_result: FAIL` and has been **retained across BATCH-018, 031,
032, 033, 034, 035, 036, 037** (per EV-SSI-039 / DEC-20260730-037) and again
through **BATCH-039** (gate-A toy instantiation left it FAIL). τ has never been
invented; joint finiteness has never been established.

## 2. The fatigue fact, stated honestly (inventor-protocol §4)

QM-STOPPING FAIL has now been *merely retained* across ≥8 batches without a named
obstruction plus argument. Under §4 this retention is a **statement about the
search, not about the problem**. It is **not** evidence that τ cannot exist, and
per AGENTS.md rule 3/5 the repeated non-clearance — much of which traces to an
absent host and absent Verify body — is closer to an *infrastructure/host gap*
than to a proven mathematical obstruction. Recording the count as if it were a
closure would be exactly the failure mode §4 warns against. It is therefore
recorded as `unverified`.

## 3. Candidate obstruction (hypothesis — NOT yet a §4 closure)

**Candidate name:** *Verify-relativity of the stopping time.*

**Sketch.** The stopping rule that bounds sieve attempts is defined relative to
the acceptance predicate `Verify(x, k')`. In the current program state:

- the real `Verify` body (curve/isogeny evaluation) is **absent** — the BATCH-022
  scaffold `verify.py` is a total no-crypto predicate with a synthetic accept
  token, explicitly `deferred_to_implementation_spike`;
- the host that would supply it (CollimationSieve@6f9188e4) is
  **host-gap-certified / `no_admissible_pin`** (BATCH-020, retained);
- τ's finiteness depends on the per-attempt success probability, which depends on
  the collision/acceptance distribution induced by that absent `Verify` body.

So a bound on τ appears to **require** the host acceptance semantics, which are
unavailable.

**Why this does NOT meet the §4 standard (the honest part).** §4's model
obstruction (the S-box `L ∘ Inv` argument) is a statement about the *object*: a
proof that a whole *class* of lenses dies against the object's structure. The
candidate above is instead a statement about the *current program state* — a
missing host and a missing predicate body. That is an availability gap, not a
demonstrated mathematical barrier. Concretely it fails §4 on three counts:

1. **No proof of impossibility within a stated scope.** It shows τ is *currently
   unsourced*, not that a source-compatible τ *cannot* exist. An availability gap
   is not an obstruction (AGENTS.md rule 5).
2. **No argument that the dependence is essential.** It has not been shown that
   τ's finiteness genuinely cannot be reduced to a host-independent property
   (e.g. a mixing-time / collision-distribution bound) that could be established
   without the full `Verify` body. The reduction has not been attempted.
3. **No forward-guidance-grade class map.** §4 closures name the classes that
   remain open after the obstruction. Here the obstruction itself is unproven, so
   no class map is earned.

Therefore the candidate is retained as an **open hypothesis**, and QM-STOPPING
status remains `unverified` (not `closed`, not an obstruction claim).

## 4. Proof-search audit (inventor-protocol §8, applied to the candidate)

- **Baseline reproduction.** The "baseline" is the retained FAIL control. It is
  reproduced (still FAIL), but a FAIL control is not a bottleneck slice of a
  best-known result — there is no positive baseline to embed against. *Audit
  status: non-applicable, recorded.*
- **Observation collision.** Observable = "τ bound exists." Two ground-truth
  objects with the same observable-absence (host present vs host absent) would
  separate an availability gap from a real obstruction; we cannot construct the
  host-present object (no admissible pin), so the collision test **cannot yet be
  run** — which is itself why the obstruction is unverified.
- **Quantifier order.** The claim needing proof is `∀ admissible host semantics,
  ¬∃ finite source-compatible τ`. The candidate only supports `(current state) ⇒
  τ unsourced`. The universal-over-hosts quantifier is untouched. *This gap is the
  core reason for `unverified`.*
- **Method ceiling / nearby-object control.** A method that concludes "no τ" from
  "host absent" would equally conclude "no τ" for a *solvable* nearby instance
  whose host merely happens to be unpinned. It cannot distinguish the pair, so it
  has not identified load-bearing structure. *Audit fails; candidate rejected as a
  closure.*

## 5. Controls-before-belief note (inventor-protocol §3)

The relevant null object for a future τ signal is a **random/permuted acceptance
distribution of the same shape**: any purported τ bound must be shown to *decay
appropriately* as the parameter meant to destroy structure increases, and must be
run against the null before belief. No τ signal is claimed here, so no control is
owed yet; this is registered so a future τ attempt cannot skip it.

## 6. Forward guidance (what a real §4 obstruction — or its refutation — requires)

To convert the candidate into a §4-standard closure **or** to refute it, a future
bounded step (still zero-compute where possible) should:

1. **Attempt the host-independence reduction.** Determine whether τ's finiteness
   reduces to a host-*independent* property — a mixing-time / re-randomization
   bound or a collision-distribution property of the sieve — that can be stated
   without the full `Verify` body. If yes, the Verify-relativity candidate is
   **refuted** and QM-STOPPING moves to that property's analysis.
2. **If the dependence is essential, prove it.** Show, within a stated scope, that
   *every* admissible host acceptance semantics compatible with FC0 fails to admit
   a finite source-compatible τ — i.e. discharge the `∀ hosts` quantifier. Only
   then is a named obstruction earned.
3. **Then, and only then, write the class map** of stopping-rule families that
   remain open (e.g. amortized/average-case τ, τ relative to a relaxed acceptance
   predicate, τ under an explicit heuristic) as §4 forward guidance.
4. **Do not** substitute an invented or toy τ (the fake-τ / controlled-null
   trap), and **do not** launch EXP-SSI-001 to force the issue.

## 7. Enumerated status

- **Object studied:** the FC0 collimation-sieve stopping rule / τ and joint
  Q/S/P/C(+H) finiteness (QM-STOPPING).
- **Depth of verified structure:** none beyond retaining the FAIL control and
  articulating a candidate obstruction hypothesis that fails the §8 audits.
- **`dominated_by`:** the actual GOAL-SSI-001 cryptanalytic frontier (supersingular
  isogeny / QUERY_MEMORY reconciliation) fully dominates; this document adds no
  row to any time/memory/data frontier for the hard problem. It is internal
  analysis, not an attack.
- **`sota_delta`:** no attack; conceptual/analysis contribution only — begins the
  obstruction analysis and records it honestly as `unverified`.
- **Enumerated closures:** none at the §4 standard.
- **Open directions:** §6 items 1–3 above; the host-integration width contract
  (companion deliverable) remains the other binding blocker.
