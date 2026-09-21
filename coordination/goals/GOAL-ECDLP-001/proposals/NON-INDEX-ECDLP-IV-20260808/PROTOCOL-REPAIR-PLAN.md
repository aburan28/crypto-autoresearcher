# Versioned protocol repair plan — Arm-A/Arm-B redirect

Status: draft, not approved, not dispatched
Date: 2026-08-09
Goal: `GOAL-ECDLP-001`
Frozen proposal: `NON-INDEX-ECDLP-IV-20260808`
Coordinator decision placeholder: `DEC-20260809-b097bc`
Successor batch placeholder: `BATCH-f0b644`

This package preserves the frozen version-1 experiment files. It adds two
version-2 protocol amendments and an independent review task because the
original queue is structurally valid but not protocol-ready: both experiments
are still `review_required`, neither has `approved_by`, neither binds an exact
implementation/command, and the existing Arm-A driver does not expose an
ordinary-rho baseline. The independent read-only audit recommends
`REVISE_REQUIRED`; its findings are operational protocol defects, not
mathematical evidence.

## Dispatch order

```text
TASK-20260809-c08f7b (materialize protocol package)
        |
        v
TASK-20260809-0a3d8c (pre-review snapshot)
        |
        v
TASK-20260809-1e6c8c (independent protocol review)
        |
        v
TASK-20260809-c74a28 (Coordinator snapshot of review before decision)
        |
        v
Coordinator approval decision + successor queue amendment
        |
        v
Arm-A implementation/freeze gate
        |
        v
Arm-A producer -> TASK-20260809-819996 snapshot -> Validator/Red Team
        |
        v
Arm-B producer -> snapshot -> Validator/Red Team
```

The post-producer review edges are machine-readable in the successor task
cards: Arm A's snapshot fans out to `TASK-20260809-a1c288` (Validator) and
`TASK-20260809-902a67` (Red Team), which converge on the Coordinator ledger
archive `TASK-20260809-10a04a`; Arm B's snapshot similarly fans out to
`TASK-20260809-4b0599` and `TASK-20260809-9f6cb6`, which converge on
`TASK-20260809-88d0dd`. These are future cards only. They cannot run until the
successor queue is admitted, the relevant producer has a verified snapshot,
and the backend/model provenance gates pass.

No executor card is eligible until the independent review is complete, the
Coordinator has approved the frozen v2 protocol, the implementation hashes
match the amendment, and the harness backend preflight passes (or the exact
native-session fallback is explicitly admitted by policy).

## Machine-dispatch integration blockers

The checked-in `dispatch_queue.json` is the immutable version-1 queue and
contains no `TASK-20260809-*` entry. It must not be edited in place to make the
repair appear live. Its dispatcher rendering still exposes the old
`TASK-20260808-6b7ca0` executor as ready because queue validation does not
enforce the experiment's `approved_by` field; that is precisely why the old
executor must be blocked/superseded before any successor queue is admitted.
Before any v2 task is dispatched, the Coordinator must
create a successor queue (with a fresh queue/batch identifier) that:

- includes `TASK-20260809-c08f7b`, `TASK-20260809-0a3d8c`, `TASK-20260809-1e6c8c`, and
  `TASK-20260809-c74a28` with machine-readable `depends_on`, `read_scope`,
  `write_scope`, `artifact_paths`, archive declarations, and inference policy;
- marks the old `TASK-20260808-6b7ca0` and `TASK-20260808-dd5e91` executor
  entries blocked/superseded so the dispatcher cannot select version 1 while
  the v2 amendments are pending;
- adds a fresh Arm-A executor and the Coordinator archive task
  `TASK-20260809-819996`, with the exact Arm-A paths listed in amendment A5;
- adds a fresh Arm-B executor whose direct dependency is the verified
  `TASK-20260809-819996` snapshot receipt and whose exact paths are listed in
  amendment B3--B5; and
- assigns every producer, review, and archive artifact to exactly one archive
  task without giving an archive task write ownership of another worker's
  source directory.

Until that successor queue is committed and validated, the prose ordering above
is informative only and no Executor dispatch is authorized.

The draft pre-review queue is
`dispatch_queue_v2.json`. It contains only the materialization, pre-review
snapshot, independent protocol review, and review-snapshot tasks, all marked
`blocked` with the current backend/approval gates. It intentionally does not
replace the immutable v1 queue and does not admit either executor. A later
Coordinator queue amendment must add the Arm-A/Arm-B producer, post-snapshot
Validator/Red-Team, and ledger-archive cards after the v2 protocol is approved
and the backend preflight passes.

## Frozen input and cost contracts

Arm A's command expands to 24 instance cells (three field sizes crossed with
eight seeds), with 12 walks per cell and all declared modes/controls present in
the same receipt family. The version-2 manifest must contain exactly those 24
rows in lexicographic `(field_bits, seed)` order; a mismatch fails before the
first walk. Its comparison table retains a vector of integer operation/event
counts, bytes, and memory/timing fields, with each work component normalized by
`sqrt(N_subgroup)` and no unapproved scalar weighting.

Arm B consumes exactly the 24 source-instance rows in the Arm-A instance
manifest; degree, seed, candidate, control, and target-count entries are
nested receipts rather than hidden extra runs. It freezes all candidate,
rejection, random-map, non-special, identity, and unsupported rows before the
first target-side solve. Candidate order is the
bytewise tuple `(source_instance_id, degree, target_j,
target_coefficients_digest, kernel_digest, map_digest)` and exactly the first
12 constructible rows per degree are selected; all later rows remain recorded
as truncated. `C-RANDMAP` is a representation/evaluation null unless a
homomorphism certificate proves scalar preservation. Its one-shot vector is
the complete construction-to-replay sum; its amortized vectors are frozen for
target counts 1, 8, and 64. `ell` denotes isogeny degree, while
`N_subgroup` is the sole DLP normalization denominator.

The earlier `EXP-ECDLP-3c1bc0` audit is explicitly provenance, not a second
Arm-B experiment: it covers structural odd-degree special-
`j` closure but has no source (P,Q,N_{\text{subgroup}},k) replay fixture and
does not measure end-to-end transfer cost. Arm B must therefore spend its
primary rows on fresh scalar-replay certificates and complete construction-to-
replay vectors; structural-only rows are retained as provenance or refusal.

## Required future artifact paths

The future executor and archive cards must declare these paths exactly (the
amendment `artifact_paths` lists are the source of truth):

Arm A:

```text
protocol_inputs/implementation_boundary.yaml
protocol_inputs/automorphism_census/instance_manifest.yaml
protocol_inputs/automorphism_census/control_manifest.yaml
protocol_inputs/automorphism_census/cost_schema.yaml
artifacts/automorphism_census/instance_manifest.yaml
artifacts/automorphism_census/source_manifest.json
artifacts/automorphism_census/raw_receipts.jsonl
artifacts/automorphism_census/automorphism_certificates.jsonl
artifacts/automorphism_census/refusal_table.jsonl
artifacts/automorphism_census/comparison_table.csv
validation/automorphism_census_report.yaml
```

Arm B:

```text
protocol_inputs/implementation_boundary.yaml
protocol_inputs/isogeny_transfer/candidate_manifest.yaml
protocol_inputs/isogeny_transfer/control_manifest.yaml
protocol_inputs/isogeny_transfer/cost_schema.yaml
artifacts/isogeny_transfer/candidate_manifest.yaml
artifacts/isogeny_transfer/candidate_manifest.sha256
artifacts/isogeny_transfer/source_manifest.json
artifacts/isogeny_transfer/raw_receipts.jsonl
artifacts/isogeny_transfer/transfer_certificates.jsonl
artifacts/isogeny_transfer/refusal_table.jsonl
artifacts/isogeny_transfer/cost_table.csv
validation/isogeny_transfer_report.yaml
```

The required post-snapshot review and ledger paths are also frozen in the
proposed cards:

```text
reviews/TASK-20260809-a1c288/validator_report.yaml
reviews/TASK-20260809-902a67/red_team_report.yaml
ledger/evidence/EV-ECDLP-b28834.yaml
ledger/decisions/DEC-20260809-6a360d.yaml
archives/TASK-20260809-10a04a/ledger-receipt.json
reviews/TASK-20260809-4b0599/validator_report.yaml
reviews/TASK-20260809-9f6cb6/red_team_report.yaml
ledger/evidence/EV-ECDLP-b367d7.yaml
ledger/decisions/DEC-20260809-7ef364.yaml
archives/TASK-20260809-88d0dd/ledger-receipt.json
```

The ledger records above are reserved artifact paths, not prewritten findings;
their contents may be authored only from actual independent reports.

The independent Arm-B verifier is a planned separate entrypoint,
`harness/verify_isogeny_transfer_v2.py`; the current `verify_transport` helper
is not accepted as the independent certificate guard because it reuses the
forward implementation and does not establish the complete field/twist/gcd/
kernel/inverse/replay contract.

The audit also records two narrower refusal conditions in the implementation
boundary: `verify_transport` only checks that the declared `N` annihilates the
mapped point, not that the point has exact order `N`, and it infers the target
degree from the supplied kernel-list length. `velu_image` likewise assumes a
complete full-point kernel while using an x-coordinate membership shortcut.
The v2 verifier must independently establish exact subgroup order, kernel
closure/completeness, target trace/order, and the declared degree before any
transfer or cost row is admitted.

## Implementation boundary

The proposed Arm-A entrypoint is `harness/run_ecdlp_endo_census_v2.py`. It must
reuse the public-instance baseline and the corrected eigenvalue bookkeeping,
but it must make the ordinary/negation/full policy distinction explicit rather
than treating both existing `run_ewalk2.py` modes as quotient modes.

The existing `harness.rho.solve` helper is not itself an Arm-A implementation:
its `RhoResult` has generic group-operation totals but no canonicalizer hook,
verified eigenvalue/stabilizer transport, fruitless-cycle counter, or field-
operation/canonicalization/memory vector. A future v2 entrypoint may reuse its
generic arithmetic semantics for a separately identified baseline check, but
it must emit the frozen per-mode cost vector and deterministic restart/scalar-
replay fields itself; relabeling `total_group_operations` as quotient work is a
protocol refusal.

The proposed Arm-B entrypoint is `harness/run_ecdlp_isogeny_transfer_v2.py`.
The existing odd-degree Velu code is usable only for degrees 3, 5, 7, and 11.
Degrees 2 and 4 remain a named implementation gate: a dedicated, independently
tested formula is required before those degrees can be counted. Routing them
through `velu_odd`, returning the identity, or silently dropping them is
invalid.

The exact implementation boundary is frozen in
`protocol_inputs/implementation_boundary.yaml`. It records that
`harness/run_ecdlp_endo_census_v2.py`,
`harness/run_ecdlp_isogeny_transfer_v2.py`, and
`harness/verify_isogeny_transfer_v2.py` are `planned_not_yet_built`. It also
records why the existing `verify_transport` helper is not an independent
certificate verifier: it reuses the forward path, assumes an odd degree from
the kernel-list length, and does not establish the complete field/twist/gcd/
kernel/inverse/replay contract. The source-hash manifest and certificate
fields in that input are mandatory pre-execution gates; a missing file,
hash mismatch, or unsupported degree is a refusal/implementation boundary,
not a negative result.

The same input now carries a ten-case verifier fixture contract. One
odd-degree row from the committed `EXP-ECDLP-3c1bc0` structural audit is used
only as provenance for fresh fixture materialization; that run has no complete
kernel bytes or ECDLP P/Q/N/k fixture. Target-trace mutation, x-coordinate-only
kernel input, even-degree requests, subgroup-gcd failure, incomplete kernels,
scalar-replay failure, kernel-containing P/Q, twist mismatch, and structural-
only inputs must all be rejected or refused before a target-side solve. The
prior audit is not treated as an Arm-B transport certificate or an ECDLP
result, and the v2 fixture suite itself is `planned_not_yet_built`.
The verifier must not call `velu_odd`, `velu_image`, or the forward driver to
derive target coefficients or images; those outputs are untrusted inputs to a
separate exact path, with an independently hashed dual/inverse/alternate-map
replay.

## Claim boundary

This repair changes no hypothesis status, creates no evidence record, and
authorizes no mathematical inference. Any eventual result remains toy-scale
unless a later, separately approved validation plan establishes a broader
correspondence. Backend failure, missing formulas, timeouts, and failed
certificates are operational or validity outcomes, not evidence against either
hypothesis.

## Subproblem decomposition and decision gates

The redirect is intentionally split into separate questions. A curve feature
must clear the earlier gates before it is allowed to influence a later one; in
particular, a `j`-invariant association is not a solve-cost result.

| Subproblem | What is being tested | Required certificate or control | Decision it can inform |
| --- | --- | --- | --- |
| S0: public-instance validity | The source curve, prime subgroup, `P`, `Q`, twist, and scalar replay are well-defined | independent order/subgroup and `kP=Q` certificates; refusal table | whether a row is valid input or infrastructure-invalid |
| S1: automorphism quotient | A verified `F_p`-defined unit automorphism changes rho orbit handling beyond ordinary and negation baselines | field-of-definition, automorphism order, eigenvalue, stabilizer, and collision certificates; `C-RAND` and `C-RELABEL` | whether a special unit action is worth carrying into transfer search |
| S2: non-unit CM endomorphism action | A verified endomorphism on a selected `j`/CM stratum supplies a usable subgroup eigenvalue or decomposition, rather than merely correlating with a curve label | explicit endomorphism construction, subgroup action/eigenvalue certificate, degree/kernel checks, and a nearby same-order `j` control | whether to author a separate CM-action experiment; S2 is not dispatched by the current Arm-A/Arm-B queue |
| S3: isogeny transfer | Moving the instance to a bounded-degree target preserves the scalar and changes complete charged cost | independent forward/inverse or dual replay certificate, deterministic candidate manifest, even-degree refusal receipts | whether any target survives end-to-end cost accounting |
| S4: cost and scale | Any observed difference survives setup, retries, serialization, memory, and multi-target amortization | vector cost schema, one-shot and `k={1,8,64}` tables, null controls, finite-size limits | whether the result is observation-only, inconclusive, or eligible for further review |

The current Arm-A amendment covers S0/S1. Arm B covers S0/S3/S4 after the
Arm-A snapshot. S2 is deliberately a gated successor rather than being
smuggled into either arm: non-unit CM endomorphisms are not automatically
automorphisms, and an eigenvalue equation alone does not prove a cheaper DLP
algorithm. The existing committed `NON-INDEX-ECDLP-III-20260807` corpus may
seed candidate strata and matched controls, but its `expected_rho_*` fields are
synthetic scaffolding and cannot be used as S1--S4 evidence.

### `j`/CM target strata

The candidate policy must label every target before solving as one of:

```text
unit-special: j=0 or j=1728 with a verified F_p-defined automorphism;
cm-nonunit: verified non-unit CM endomorphism with a subgroup eigenvalue;
ordinary-other: ordinary target with no admitted special action;
control-nonspecial: same-order non-special neighbor;
excluded-positive: anomalous or small-embedding calibration.
```

`unit-special` can enter S1. `cm-nonunit` can only enter S2 after the separate
certificate gate. `ordinary-other` and `control-nonspecial` provide the nearby
object controls. `excluded-positive` rows are retained in refusal or calibration
artifacts and never counted as primary ECDLP evidence.

### S2 follow-on gate: non-unit CM endomorphisms

If S1 produces a valid unit-special census, the next endomorphism-specific
question is not “does this `j` look good?” It is:

```text
For a predeclared ordinary CM stratum, can a publicly constructed non-unit
endomorphism be certified on the measured prime subgroup, with a usable
eigenvalue/decomposition and a complete charged implementation whose control
does not receive that endomorphism?
```

The cheapest discriminating protocol would freeze, before any solve outcome:

1. a finite list of CM discriminant/`j` strata and a nearby same-order
   ordinary-other stratum;
2. the endomorphism construction and its degree/kernel or rational-function
   certificate;
3. the subgroup action and eigenvalue certificate, including the exact
   quantifier order for the admitted subgroup and the failure/refusal case;
4. a method ceiling stating whether the endomorphism can only change a constant
   or whether it could change the rho/search exponent; and
5. a matched small-integer null for any curve-derived eigenvalue or
   kernel-field-order signal, so a size/order artifact is not attributed to CM;
6. a charged control that pays construction, evaluation, decomposition,
   retries, and verification even when the eigenvalue is unusable.

This is a proposed successor gate, not an approved experiment. Before it can
be implemented or dispatched it needs its own `proof_search_map`, exact
baseline/collision/quantifier/ceiling audits, source-hash-bound code, and an
independent review. The current Arm-A/Arm-B package records S2 refusals rather
than silently treating non-unit CM structure as an Arm-A automorphism.

The draft map is frozen at
`proof_search_map/S2-CM-ENDO-20260809.yaml`. Its version-2 `not_dispatchable` gate is
intentional: the map records pending audits and the unresolved historical
EXP-ENDO-001 lineage conflict, and it does not convert either item into
mathematical evidence. It also carries the matched small-integer null required
to distinguish CM structure from the open integer-size confound recorded in
`KN-OPEN-2c095b`. The map's Pareto fields are likewise unmeasured until a
fresh, source-hash-bound implementation produces immutable receipts.
