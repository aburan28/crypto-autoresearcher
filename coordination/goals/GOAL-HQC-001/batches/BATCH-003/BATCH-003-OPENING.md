# GOAL-HQC-001 — BATCH-003 opening

- **Goal**: `GOAL-HQC-001` (status `active`)
- **Question**: `RQ-HQC-001`
- **Opened**: 2026-08-02
- **Prior batch**: BATCH-002, closed `refine`, `DEC-20260802-9664c6`,
  `EV-HQC-6fd5b1`, `CORR-20260802-3ae664`, verified ledger commit `306ea7aa`
- **Base merged from `main`**: `72d8aafe`
- **Owner**: coordinator

## 1. Mandate, and why this batch is different

BATCH-003 executes `DEC-20260802-9664c6`'s single `next_action`: **design the
measurement**. It is the first batch in this campaign permitted to do so —
`RQ-HQC-001.constraints[0]` blocked experiment design until the primary sources
were filed as `KN-LIT` entries, and BATCH-002 filed them.

It is also the first batch that will create a **hypothesis** (`H-HQC-18d1b4`)
and a **frozen experiment contract** (`EXP-HQC-982268`). Both are Coordinator
acts performed only in the ledger archive, after independent review.

**BATCH-003 still runs no confirmatory measurement.** It designs one, and it
builds a correctness oracle for one. The distinction is enforced by task
scoping, not by good intentions — see §4.

## 2. What is being measured, and why that object

The target is **not** the decoding failure rate directly, and **not** pairwise
correlation. It is the **joint moment `μ_{δ_e+1}`** of the inner-decoder failure
indicators, **on the true space (T)**.

That target is forced by `EV-HQC-6fd5b1` O-6, the strongest result this campaign
has produced:

- A17 — the assumption that inner-decoder block failures are i.i.d., so their
  sum is Binomial — is stated and proved nowhere in either primary source, and
  neither SPEC Theorem 6.1 nor RMRS Theorem 4.3 is proved at all.
- A17 is load-bearing: Theorem 6.1 depends on it entirely, and Table 5's DFR
  column and the IND-CCA2 join depend transitively.
- Its failure direction **cannot be signed from the page**. Two mechanisms of
  opposite sign are both present, the distortion reduces to `μ_{δ_e+1}` rather
  than to pairwise correlation, and because `μ_m` is not determined by `μ_2`,
  **second-moment data is structurally incapable of signing it** — and all
  published evidence is second-moment.

So the question cannot be closed by more reading, and a design that measured
pairwise correlation would answer the wrong question with real compute. That is
the specific error this opening exists to prevent.

**Space (T), not space (M).** `DEC-20260802-9664c6` D-5 records that the
A5 ⟹ A17 implication holds only on the model space (M); on the true space (T)
A5's antecedent is false, so the implication is vacuous exactly where it would
matter. Sampling must use true fixed-weight `x, y, r₁, r₂, e`. A design that
samples on (M) would be measuring its own assumption.

## 3. What this batch does not claim

No decoding trial at standardized parameters. No statement about whether HQC's
DFR model is correct. No security claim in either direction. The claim-tier
ceiling stays **toy**, and `RQ-HQC-001` makes that ceiling *more* binding for a
standardized algorithm, not less. Nothing here is admissible toward the
AGENTS.md rule 13 closure quorum.

## 4. Batch composition

| Task | Role | Purpose |
|---|---|---|
| `TASK-20260802-853bad` | executor | Design the measurement: proposed hypothesis, frozen protocol, **null object**, numbered heuristics, and a feasibility/power analysis saying at which reduced parameters `μ_{δ_e+1}` is actually estimable within budget. |
| `TASK-20260802-ecba30` | executor | Build a **correctness oracle**: an exact small-case computation of the joint moment, plus an i.i.d.-by-construction null generator, with tests. Independent of the design. |
| `TASK-20260802-506c73` | coordinator | Snapshot archive. Runs alone. |
| `TASK-20260802-addcdd` | validator | Protocol completeness, oracle correctness, heuristic numbering, no-confirmatory-run gate. |
| `TASK-20260802-e5ebe9` | red-team | Attack the design before it costs compute. |
| `TASK-20260802-1758c3` | coordinator | Ledger archive: `EV-HQC-0e9116`, `DEC-20260802-d94a64`, `H-HQC-18d1b4`, `EXP-HQC-982268`, goal checkpoint. Runs alone. |

**Why an oracle is the second producer, and why it is independent.** A
joint-moment estimator is exactly the kind of code whose bugs look like
signal: an estimator that over-counts coincidences produces precisely the
"positive correlation" this campaign is looking for. An exact computation at a
parameter small enough to enumerate gives any later estimator a ground truth to
be checked against, and the same machinery supplies the null object. It does not
depend on the protocol's final shape, so it runs concurrently.

**`runs_authorized: 0` for both producers.** The oracle may execute its own
exact computations and tests — that is what it is for — but neither task may run
the confirmatory measurement. That is BATCH-004's, against a contract that has
been reviewed and frozen.

## 5. Two gates carried forward from BATCH-002's failures

**The null-object gate.** `docs/inventor-protocol.md` requires controls before
belief, and this campaign has already had a control fire on the wrong space
(BATCH-002 D-5). The protocol must specify the identical measurement on an
i.i.d.-by-construction ensemble of matched shape. A joint-moment excess that
does not vanish on the null is an artifact, and the design must say so before
any number exists to be tempted by.

**The flag-without-resolution gate**, added per `DEC-20260802-9664c6` D-7.
BATCH-002 froze into the immutable corpus an entry that flagged the
Prop 6.1.3/6.1.4 inconsistency and never derived its resolution — verbatim the
failure mode that batch was correcting. Both reviewers are directed to check
this batch's deliverables for the *class*, not the instance: any flagged
discrepancy must be resolved, or explicitly recorded as open with a named
successor.

## 6. Standing limitations

Both reviews are independent **sessions** on one model; no policy alias in
`orchestration/model-policies.yaml` resolves under this harness. Closing this
goal will require three genuinely distinct backends, and no attestation may
ever be synthesized from same-model reviews.

`validate_ledger.py` at open: **64** errors above the grandfathered baseline
(down from 67 as `main` continued schema cleanup). None names a
`GOAL-HQC-001` record. BATCH-003 must keep that zero.
