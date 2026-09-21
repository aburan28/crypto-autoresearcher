# TASK-20260719-044 multigraded dual independent audit

## Record boundary

- Role: reviewer
- Target reviewed:
  `coordination/tasks/TASK-20260719-041/multigraded_dual_theorem_gate.md` as frozen at
  970addbd (and its declared upstream declarations and handoffs).
- Independent scope: review only; no experiment, run, solver, fixture, compute, or
  policy transition.
- Evidence files: `coordination/tasks/TASK-20260719-039/primary_multigraded_dual_extraction.md`,
  `coordination/tasks/TASK-20260719-040/semantic_cost_preflight.md`,
  `coordination/tasks/TASK-20260719-041/multigraded_dual_theorem_gate.md`,
  `coordination/tasks/TASK-20260719-042/checkpoint_preparation.yaml`,
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-008/source_reconciliation.md`,
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-008/prerequisite_manifest.yaml`,
  and `coordination/goals/GOAL-ECDLP-001/batches/BATCH-008/dispatch_queue.json`.
- Inference policy context:
  `review-xhigh` was required by AGENTS.md.

## 1. Gate audit summary

The producer correction in `TASK-20260719-041` is materially stronger than the original
direct-atomization claim and is structurally coherent with `TASK-20260719-039` and
`TASK-20260719-040`:

- The source does state exact operations for homogeneous multigraded dual spaces at a supplied
  grading and homogeneous centre (Cummings--Hauenstein, Theorem 3.2, Corollary 3.6).
- `TASK-20260719-040` correctly distinguishes between local affine duals `D_y(I)` and
  homogeneous centered pieces `D_0^a(I)`.
- The route to an exact existence bit is correctly reframed as: prove the input ideal is
  Cox-irrelevant-saturated and all strata/fiber edge cases are controlled, then use
  Maican plus Cummings--Hauenstein to turn a Hilbert component zero test into nonemptiness.

## 2. What is confirmed as sound

### 2.1 Source-level positives

- **Cummings--Hauenstein recursion is sound as stated**: the `DualSpace`-type
  recursion computes `dim D_0^a(I)` (equivalently `H_I(a)`) from supplied homogeneous
  generators plus finite grading data.
- **Right inverse/colon direction is correctly typed**: `Phi_g`/`Psi_g` is a right inverse on
  differential spaces, and Theorem 4.8 is correctly read as a colon transfer.
- **`TASK-20260719-040` cost framing is still useful**: the natural homogeneous representation
  costs `Theta(B^5)` ambient/component traffic in the literal five-deck realization, and that
  is a strong scoped complexity bound.
- **No experimental claim is introduced by this producer**: no new run, solver, fixture, or
  campaign is implied by `TASK-20260719-041`.

### 2.2 Why this does not yet prove an immediate ECDLP constructor

Three explicit obligations remain open and were already identified by the source package:

1. **Finite-field construction of the exact dual recursion**  
   The source is proved over `C`; a bounded, prime-field/divided-power replacement with
   explicit field-compatibility assumptions is still missing.
2. **Exact saturated-fiber and all-strata semantics**  
   The producer still depends on Cox-irrelevant saturation plus all-strata handling for
   restricted-fiber emptiness. The current files have no closure theorem that an unsaturated
   presentation cannot create false nonempties.
3. **Restriction replay under all gate operations**  
   The review still sees missing binding for costed updates under every recursive/auxiliary
   restriction step (including recursive-S3 and exceptional charts), and no compact reuse proof.

## 3. Exact verdict check

The `terminal_verdict` is:

`REVISE_AND_DEFER_THE_EXISTENCE_BIT_ROUTE__CUMMINGS_HAUENSTEIN_PLUS_MAICAN_GIVE_A_CONDITIONAL_COEFFICIENT_TO_NONEMPTINESS_PATH__NO_SATURATED_ALL_STRATA_FP_CONSTRUCTOR_OR_SUBRHO_COST_THEOREM_IS_PROVED__PRESERVE_SPARSE_ADAPTIVE_EXCEPTIONS`

This is an acceptable non-official review outcome (scoped revision/defer), because the core
correctness direction is acknowledged and the missing proofs are exactly scoped to
finite-field constructor semantics and saturation/restriction completeness.

## 4. Exact scopes and boundaries preserved

- **Scope preserved:** only an existence-bit route is reviewed; the stronger `IDEA-133`
  faithful-functional/source-inverse branch remains optional.
- **No universal lower bound asserted:** all `B^5` and `B^6` counts are representation-scoped
  to the literal homogeneous implementation and do not close every sparse or adaptive backend.
- **No compute authorization added:** this path remains compute-free review.
- **One next action (scope-preserving):** independently prove the exact finite-field,
  all-strata Cox-irrelevant saturation closure for the restricted-fiber ideal and provide a
  charged replay rule for each dyadic restriction update in the five-sparse/fixed-rank complete
  path.

## 5. Final audit closure

`TASK-20260719-044` is complete as reviewer scope. No official status transition is made here.
