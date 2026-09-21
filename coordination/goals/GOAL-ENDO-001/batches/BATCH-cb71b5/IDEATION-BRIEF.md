# BATCH-cb71b5 ideation brief — shared by every lane

Campaign: `GOAL-ENDO-001`. Read
`analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md` first; it is the
frozen decomposition and your lane is one of its fourteen. Read your lane's
`RQ-*` record in `ledger/questions/`. You are the **idea-generator** role
(`agents/idea-generator.md`); you file proposals and change no status.

## Non-negotiables (AGENTS.md, docs/inventor-protocol.md)

1. **Name the resource.** Every proposal must state which of R1–R8 (see
   DECOMPOSITION.md §2) it consumes. A proposal whose only use of `phi` is to
   apply it to points of `G` is **inadmissible**: `G` has prime order, so every
   endomorphism acts on it as multiplication by a scalar (`H-ENDO-001`), and
   incidence and endomorphism-image oracles are generic-group simulable and hence
   closed at exponent 1/2 (`KN-FIND-b7e091`). If your proposal is inadmissible,
   **say so in `novelty_screen.verdict` and file it anyway** as a recorded
   closure with its obstruction named — that is a legitimate deliverable here.
2. **Null object before belief.** `null_object_control` is mandatory and must
   name a matched object of the same shape and the parameter whose increase must
   destroy the signal. A quantity that fails to decay when that parameter grows
   is the canonical artifact tell.
3. **Pareto honesty.** `dominated_by` must be filled by actually checking the
   frontier (parallel Pollard rho with distinguished points at `0.886 sqrt(N)`
   group operations and `O(1)` memory, `KN-TECH-001`/`KN-TECH-006`; the
   automorphism-discounted variant on CM curves, `KN-TECH-018`; BSGS at
   `sqrt(N)` time and memory). `null` is a fabrication unless you checked every
   row across time, memory, and data/queries. `sota_delta` must be quantitative;
   "zero speedup against any attack baseline" is the correct and expected answer
   for most proposals and is not a defect.
4. **No fabrication.** Never invent a citation, a run, a timing, or a number.
   Cite only `KN-*`, `EXP-*`, `EV-*`, `DEC-*`, `H-*`, `IDEA-*` ids you have
   actually read, or named public theorems you can state precisely. If you are
   unsure a paper says what you want it to say, write the claim as `[open]` and
   put the uncertainty in `assumptions`.
5. **Toy scale.** Everything runnable here is `p` up to ~32 bits, pure Python
   (`sympy`, `numpy`, no Sage). `estimated_cost.compute` must be honest about
   that. The existing instrument is `harness/toycurve.py`, `harness/semaev.py`,
   `harness/rho.py`, `harness/endomorphism_la.py`, `harness/runner.py`.
6. **Premature closure is a failure mode.** Do not decline to generate because
   the area looks mined. "This space is exhausted" is a hypothesis about the
   search, not a fact about the space.

## Novelty screen — run it, record it

Before filing, grep the repository for your mechanism:

```sh
grep -ril "<your key phrase>" ledger/ knowledge/ docs/ analysis/ | head -20
```

Record the exact commands, the hit counts, and a verdict in `novelty_screen`:
`novel` | `adaptation` | `duplicate` | `known_negative`. A `duplicate` is filed
with the id it duplicates and is still useful — it maps the corpus.

## ID allocation

```sh
python3 tools/allocate_id.py --next idea --date 20260807   # mint
python3 tools/allocate_id.py --check IDEA-20260807-xxxxxx  # verify before use
```

Never grep for "the next free number". Record the command you ran in
`id_allocation_provenance`.

## Output

One file per idea at `ledger/proposals/IDEA-20260807-<tok>.yaml`, top-level key
`idea`. Required fields (copy the shape from
`ledger/proposals/IDEA-20260806-e4f96e.yaml`, which is a good exemplar):

```yaml
idea:
  id: IDEA-20260807-<tok>
  question_id: <your RQ id>
  added: '2026-08-07'
  title: <one specific sentence; no marketing>
  class: mechanism | algorithm | representation | measurement | control | tooling | composition
  claim: <what is being asserted, in full, with the mechanism's logic>
  resource_label: <R1..R8, or "audit: consumes no resource">   # campaign-specific, required
  admissibility: admissible | inadmissible_generic_group       # campaign-specific, required
  admissibility_argument: <why the resource escapes, or why it does not>
  discriminated_from: [<what this is NOT, with ids>]
  object_first_candidate:
    tracked_object: <the object, not the technique>
    lossiness: <what it forgets>
    propagation: <how it moves under the operations>
    survival_score: <what changes kill it>
  mechanism: <step by step, concrete enough to implement>
  novelty_status: novel | adaptation | duplicate | known_negative
  novelty_screen: {method: ..., results: ..., verdict: ...}
  null_object_control: <matched null + the decay parameter; MANDATORY>
  assumptions: []
  predictions: [{metric: ..., direction: higher|lower|different, minimum_effect: ...}]
  minimal_test:
    design: <the cheapest experiment that could kill it>
    controls: []
    required_metrics: []
  falsification_conditions: []
  confounders: []
  interpretation_limits: []
  reachability_gate: <T5: is a good object reachable, and at what cost? REQUIRED
                      for any lane proposing to move between curves>
  target_complexity:
    time_exponent: ...
    memory_exponent: ...
    best_known: ...
    hidden_overhead: ...
    tradeoff_note: ...
  dominated_by: <checked, never a bare null>
  sota_delta: <quantitative>
  estimated_cost: {implementation: low|medium|high, compute: low|medium|high}
  recommended_priority: low | medium | high
  honest_prior_of_survival: <a number and a one-line reason>
  id_allocation_provenance: <the exact command>
  status: proposed
  proposed_by: idea-generator
  proposed_at: '2026-08-07'
  source_refs: [<ids you actually read>]
```

Include `proof_search_map` (see `templates/research-records.md` §Hypothesis and
`KN-TECH-080`) on any proposal that is proof-oriented — a theorem, an asymptotic
bound, a certificate family, a reduction, or a closure argument. Purely empirical
proposals set `proof_search_map: {not_applicable_reason: ...}`.

## Quality bar

Eight to nine proposals per lane. They must be **different mechanisms**, not
eight parameterisations of one. At least one per lane must be a proposal whose
expected outcome is a **negative with a named obstruction**, and at least one
must be a **control or instrument** proposal. Spread `recommended_priority`
honestly — if everything is `high`, the ranking carries no information.
