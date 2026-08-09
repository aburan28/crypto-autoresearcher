# Red-team report — `TASK-20260809-9e3c34`

```yaml
red_team_report:
  id: RT-20260809-9e3c34
  task_id: TASK-20260809-9e3c34
  goal_id: GOAL-SSI-001
  batch_id: BATCH-5a886c
  role: red-team
  reviewed_snapshot:
    snapshot_commit: 88e25821911863fe52e46980a0bd8ef40d552876
    snapshot_parent: 411cb5f5ac14546a2b6475b7cfa901fb879aa137
    queue_binding_commit: 81ad78fd3
    successor_experiment: EXP-SSI-e29417
    direct_predecessor_experiment: EXP-SSI-8fbe66
    predecessor_review_batch: BATCH-b47cd5
    evidence_boundary: >-
      Substantive design inputs were read from the requested committed snapshot
      and its queue-binding descendant. The producer refinement, producer
      duplication audit, snapshot receipt, EXP-SSI-8fbe66, and both BATCH-b47cd5
      review reports were used as the declared comparison boundary. No
      working-tree-only input was used as scientific or design evidence.
  claim_under_review: >-
    Whether the EXP-SSI-e29417 v7 additive design-only successor is a single,
    byte-recomputable and physically charged contract for C-HELPER-v2,
    ORDER-MANIFEST-v2, the target-domain query index, large integers, finite
    builder and break-even accounting, certificate availability and transition
    roots, HNF/output, full replay identity, permutation/null controls,
    dependent C-pair calibration, and the synthetic reference. This review
    makes no experiment, attack, security, exponent, novelty, hypothesis,
    completion, or scientific-result claim.
  verdict: DISSENT
  review_verdict: DISSENT_ON_FREEZE_AND_EXECUTION_READINESS
  verdict_scope: >-
    Dissent from treating v7 as freeze-ready, arithmetic-row-ready, or
    execution-ready as an exact physical contract. Concur that it is an
    additive design-only refinement, that the direct predecessor and prior
    BATCH-b47cd5 review paths are named, that the claim ceiling remains narrow,
    and that execution remains unauthorized. The dissent is based on static
    representation, scope, cost, control, and provenance contradictions only;
    it is not a scientific observation.
  objections:
    - id: RT-9E3C34-V1-V2-SUPERSESSION
      severity: execution_blocking
      finding: >-
        contract_repair_v7 is appended after a still-present contract_repair_v6
        and does not state a field-by-field precedence rule that removes the
        earlier clauses from the contract. The top-level record still uses
        SSI-BYTES-v1, ORDER-MANIFEST-v1, C-HELPER-v1, the common record hash
        index, the old EDGE-STREAM count and output grammar, and the eight-way
        C-pair/iid control. The v7 block introduces SSI-BYTES-v1.1,
        ORDER-MANIFEST-v2, C-HELPER-v2, a target/selection index, a v2
        certificate, a u32 output length, and a 256-replicate empirical
        reference. These are not a single canonical byte stream. A future
        executor can satisfy the v1 clauses or the v2 clauses and still claim
        conformance to the same YAML. The producer's statement that all v7
        contracts are explicit therefore exceeds what the combined record
        fixes.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:114-123
        - experiments/EXP-SSI-e29417/specification.yaml:181-220
        - experiments/EXP-SSI-e29417/specification.yaml:236-250
        - experiments/EXP-SSI-e29417/specification.yaml:351-370
        - experiments/EXP-SSI-e29417/specification.yaml:441-582
        - experiments/EXP-SSI-e29417/specification.yaml:707-877
        - experiments/EXP-SSI-e29417/specification.yaml:895-1149
        - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/tasks/TASK-20260809-b1b31a/refinement_report.yaml:27-71

    - id: RT-9E3C34-C-HELPER-PAYLOAD
      severity: execution_blocking
      finding: >-
        C-HELPER-v2 improves the predecessor by naming a slot array, empty
        bytes, a probe order, and two digest passes, but its placement and
        payload semantics are still not closed. The record declares an
        endpoint table and a canonical pair-record array without defining
        either physical table or its record grammar. It says that each
        distinct endpoint/pair record is inserted once while the logical count
        is A_C, but does not say whether A_C counts endpoints, pairs, or
        endpoint/pair occurrences. Consequently endpoint_slot has no defined
        uniqueness or target array, and payload_ptr has no fully typed target
        or payload length. pair_record_bytes and header_bytes in the memory
        equation are undefined. The legacy C entry and middle descriptor use
        b_slot, while v2 uses b_slot_C; no compatibility rule says which width
        the descriptor stores or how a descriptor's slots map to the helper
        slots. A physically materialized helper can therefore have multiple
        admissible payload layouts and pointer interpretations.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:284-301
        - experiments/EXP-SSI-e29417/specification.yaml:952-977
        - experiments/EXP-SSI-e29417/specification.yaml:1074-1097
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:45-68
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-ed64bf/validation_report.yaml:291-302

    - id: RT-9E3C34-C-HELPER-DIGEST-KEY
      severity: execution_blocking
      finding: >-
        The v2 digest names are closer to a two-pass construction, but they do
        not freeze the preimages. `header_without_endpoint_body_sha256_and_
        helper_digest` does not define whether fields are removed, zeroed, or
        replaced by typed placeholders, and header_bytes has no expansion for
        the variable generator/source fields. The body digest is called an
        endpoint body digest while the helper digest is over the same slot
        bytes, with no explicit stored-body framing or digest field order.
        The pair-key frame uses the undeclared domain c_helper_key and omits
        the v1.1 version, generator version, and field-tag grammar required by
        the v7 wire envelope. The top-level v1 helper still calls its digest a
        framed binary body digest. Thus placement, key derivation, and digest
        verification are not independently byte-recomputable.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:188-220
        - experiments/EXP-SSI-e29417/specification.yaml:951-981
        - experiments/EXP-SSI-e29417/specification.yaml:895-906
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:45-68

    - id: RT-9E3C34-ORDER-OWNER-ORACLE
      severity: execution_blocking
      finding: >-
        ORDER-MANIFEST-v2 narrows the owner-set idea but does not make the
        owner field unambiguous for A_tagged and B_tagged. Their branch records
        contain lookup_curve_id and an order_tag whose embedded owner may be a
        different field; no invariant equates them and v2 does not say which
        one is collected into owner_set. C_pair still names C-HELPER-v1 in the
        owner-set definition and branch sources even though the proposed
        physical helper is v2. The v2 header says a generator source digest is
        recorded, but no source-digest field or exact generator-version length
        is in the header, and header_bytes is not defined. The body record
        digest preimage is not defined either. A committed manifest can
        therefore still be a shared larger order universe or a differently
        bound subset while appearing to satisfy the prose owner-set rule. The
        sentence forbidding a full-order oracle is not a resource-bound
        construction.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:256-283
        - experiments/EXP-SSI-e29417/specification.yaml:927-949
        - experiments/EXP-SSI-e29417/specification.yaml:1092-1097
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:69-93

    - id: RT-9E3C34-TARGET-INDEX-WIRING
      severity: execution_blocking
      finding: >-
        Charging the target-domain expansion is directionally correct, but the
        query index is not wired to a unique query. b_selection and
        index_header_bytes are undefined, H_Q is not assigned an exact header
        encoding, and no duplicate/empty-slot/payload-array serialization is
        given for the target index. More importantly, the record's earlier
        query sampling derives a vertex index from the old target-derived key,
        while v2 introduces a selection_index but never defines how an attempt
        obtains that selection index or maps it to a retained branch record.
        The statement that a query derives both values from bytes it possesses
        is a scope assertion, not an algorithm. The selection frame also omits
        the generator identity and version required by the v1.1 frame rule,
        and index_selection has no literal domain code. The old record-hash
        initial-slot rule remains active. A scan, a second index, or a hidden
        target/selection oracle is therefore not excluded by a single
        canonical lookup path, and the target expansion cost is not
        recomputable.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:111-123
        - experiments/EXP-SSI-e29417/specification.yaml:236-250
        - experiments/EXP-SSI-e29417/specification.yaml:982-1009
        - experiments/EXP-SSI-e29417/specification.yaml:895-925
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:69-93

    - id: RT-9E3C34-LARGE-INTEGER-COVERAGE
      severity: execution_blocking
      finding: >-
        The 70-byte v1.1 magnitude bound repairs the specific four-byte
        counter defect for the named builder and saturation caps, but it does
        not cover every declared integer-bearing object. No mathematical or
        wire bound is supplied for degree_product, its prime factors and
        multiplicities, the 4x4 U_edge matrix, intermediate HNF entries,
        output witnesses, total FOE, or exact rational synthetic numerators and
        denominators. H_Q may require a b_slot_Q wider than the 70-byte
        variable-integer envelope, yet no fixed-width capacity/storage limit
        or header encoding is stated. The old v1 grammar simultaneously
        permits u64 replicate/instance/attempt fields and raw u32 fields while
        v1.1 requires tagged large integers. The claim that 560 bits exceeds
        every declared cap is therefore not established for all declared
        objects, and two wire representations remain possible.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:181-220
        - experiments/EXP-SSI-e29417/specification.yaml:720-736
        - experiments/EXP-SSI-e29417/specification.yaml:907-925
        - experiments/EXP-SSI-e29417/specification.yaml:982-1009
        - experiments/EXP-SSI-e29417/specification.yaml:1074-1091
        - experiments/EXP-SSI-e29417/specification.yaml:1130-1141
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:121-146

    - id: RT-9E3C34-FINITE-SATURATION
      severity: execution_blocking
      finding: >-
        The v7 builder still has no terminal class for exhaustion of the finite
        manifest at S_eff=|V_p|<S_req. It stops at S_req retained records or
        the candidate cap, so a finite universe can be treated either as a
        cap exhaustion or as an unstated padding event. The proposed partial
        padding rule does not define a canonical null record, whether padding
        counts toward S_eff, how padded records are indexed, or how their
        bytes and accesses are charged. It also conflicts with the physical
        table/index dimensions being based on S_eff. `max(1,2^20*S_req)`
        conflicts with the earlier exact cap and S=0 control. These choices
        change terminal class, table capacity, query domain, and cost without
        changing the declared inputs.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:153-155
        - experiments/EXP-SSI-e29417/specification.yaml:222-224
        - experiments/EXP-SSI-e29417/specification.yaml:334-350
        - experiments/EXP-SSI-e29417/specification.yaml:495-505
        - experiments/EXP-SSI-e29417/specification.yaml:1010-1033
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:147-166

    - id: RT-9E3C34-FINITE-ACCOUNTING
      severity: execution_blocking
      finding: >-
        The finite cost section names useful operands but does not provide a
        closed accounting functional. T_attempt includes setup accesses while
        T_total adds T_setup, with no event classification that separates
        construction from per-attempt reads. No branch-specific equation says
        when C-helper, certificate, order, and target-index setup are charged,
        and the top-level setup equation omits the v2 C-helper and certificate
        terms. INCUMBENT-FOE-v1 is described but no committed input path,
        canonical bytes, or actual exact FOE record is supplied. Terminal and
        reason code literals, event-to-FOE mappings, restart independence, and
        cap-conditioned expected-cost semantics remain absent. Consequently
        q_run is only a finite statistic schema; T_q, T_q_run, and
        Q_break_even cannot be jointly recomputed from this snapshot. This is
        an accounting incompleteness, not a negative result.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:52-62
        - experiments/EXP-SSI-e29417/specification.yaml:158-187
        - experiments/EXP-SSI-e29417/specification.yaml:590-617
        - experiments/EXP-SSI-e29417/specification.yaml:778-805
        - experiments/EXP-SSI-e29417/specification.yaml:1034-1049
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:167-190

    - id: RT-9E3C34-CERTIFICATE-ROOT-AVAILABILITY
      severity: execution_blocking_for_end_to_end_claims
      finding: >-
        EDGE-CERT-v2 adds horizon and provider/receipt fields, but the wire
        schema still does not bind the local mirror path or its receipt to a
        named immutable artifact. Its u16 provider/receipt lengths conflict
        with the v1.1 variable-field u32 rule and no per-field maxima are
        provided. The outer certificate edge_count uses b_count while the
        retained EDGE-STREAM-v1 body uses uint32_le, with no exact equality
        encoding rule. The root frames use undeclared edge_root and
        edge_transition domains and omit the v1.1 version, field tags, and
        generator fields required by the generic frame rule. `transition_id`
        and U_edge are introduced in the HNF section but do not appear in the
        certificate header or edge-body grammar. Degree class to transition
        matrix mapping is consequently not bound. The dependency-unavailable
        classification correctly remains operational, but a certificate
        digest and an availability code still do not provide an end-to-end
        physically reproducible path cost.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:352-370
        - experiments/EXP-SSI-e29417/specification.yaml:824-836
        - experiments/EXP-SSI-e29417/specification.yaml:1050-1073
        - experiments/EXP-SSI-e29417/specification.yaml:1074-1085
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:214-237

    - id: RT-9E3C34-HNF-OUTPUT
      severity: execution_blocking
      finding: >-
        HNF/output remains a predicate sketch rather than a unique algorithm.
        v2 says to use a named row-reduction procedure but does not name or
        define it, its pivot/remainder conventions, scalar normalization, or
        intermediate bounds. U_edge has no integer matrix encoding, and the
        degree-factor list has no factor/multiplicity byte grammar or
        derivation from degree_class and the edge certificate. The scalar
        predicate is improved but its sign/magnitude encoding and witness
        digest preimage are not fixed. The older output gate uses a u16
        witness_len and scalar-sign/magnitude fields; v2 uses a u32 normalized
        HNF length and scalar_code without explicitly superseding the old
        record. Construction C still has no operation that maps
        middle_factor_code and the two endpoint orders into one pullback.
        Thus an output-producing C path and full replay witness are not
        byte-recomputable.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:225-235
        - experiments/EXP-SSI-e29417/specification.yaml:366-371
        - experiments/EXP-SSI-e29417/specification.yaml:806-823
        - experiments/EXP-SSI-e29417/specification.yaml:1074-1097
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:191-237

    - id: RT-9E3C34-REPLAY-IDENTITY
      severity: execution_blocking
      finding: >-
        v2 correctly says that treatment and replay should consume a full
        attempt stream, but it does not freeze the stream. Event tags,
        canonical event payloads, FOE field widths, optional fields, and the
        hash preimage for event_bytes_sha256/pre_gate_trace_sha256 remain
        unspecified. The v1 paired_trace_fields still has one generic
        witness_bytes field, a u64 delta_path with no signed difference or
        aggregation formula, and no separate treatment/replay containers;
        v2 does not replace these fields with a complete record. It also does
        not define whether attempts after a treatment success continue in the
        32768-attempt control or how their terminal continuation is serialized.
        “Only would_stop and the final identity predicate may differ” is not
        enough to establish byte identity when certificate bytes, output
        bytes, and post-gate witness containers are not typed.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:454-493
        - experiments/EXP-SSI-e29417/specification.yaml:837-848
        - experiments/EXP-SSI-e29417/specification.yaml:1098-1112
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:238-280

    - id: RT-9E3C34-NULL-PERMUTATION
      severity: execution_blocking
      finding: >-
        The v2 null clauses do not bind the controls that still use the old
        formulas. CTRL-SHUFFLED-FIBER applies a modulo-S_eff permutation but
        declares applicability using |V_p|<2; S_eff=0 and S_eff=1 therefore
        remain undefined. Its SHAKE-modulo rule is not explicitly replaced by
        the later Fisher-Yates/rejection rule. The v2 next_distinct frame uses
        the undeclared next_distinct domain and omits p_code, branch_code, and
        the required generator/version fields. For N>=2 it labels exhaustion
        after N draws owner_mismatch_not_applicable, even though the universe is
        not a singleton and a null generator has simply failed to produce a
        distinct value. No literal terminal code is supplied. Finally, the
        owner-mutated nulls still do not bind an owner-specific certificate or
        construction proving the same edge/HNF event path as treatment, so the
        claimed trace identity and forced-zero gate are not entailed.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:197-220
        - experiments/EXP-SSI-e29417/specification.yaml:506-547
        - experiments/EXP-SSI-e29417/specification.yaml:1098-1122
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:258-280

    - id: RT-9E3C34-C-PAIR-DEPENDENCE
      severity: execution_blocking
      finding: >-
        The v2 C-pair null correctly acknowledges a dependent finite reference
        rather than relying only on C_iid, but the record still has two
        incompatible gates: the top-level control has eight replicates and
        exact C_iid/tolerance thresholds, while v2 requests 256 null
        replicates, a seed-list digest, and an empirical quantile gate without
        defining the seed list, quantile level, or quantile serialization.
        “Same left/right marginals” still has no histogram byte schema, exact
        index-to-endpoint mapping, duplicate policy, or treatment generator
        binding. The helper endpoint universe and the permutation universe are
        not connected, and the helper/descriptor references still name v1 in
        the older clauses. Therefore the dependent null's reference law and
        acceptance gate are not one declared finite object; C_iid cannot be
        silently retained as the gate or silently discarded.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:548-563
        - experiments/EXP-SSI-e29417/specification.yaml:859-866
        - experiments/EXP-SSI-e29417/specification.yaml:1119-1129
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:281-302

    - id: RT-9E3C34-SYNTHETIC-REFERENCE
      severity: execution_blocking_for_diagnostic_only
      finding: >-
        The non-SSI boundary survives and is correctly non-gating for the
        universal fixed-advice claim, but the synthetic reference remains
        mismatched to its observation cells. The top-level control compares an
        empirical CDF per target set against F_N,S while aggregating cells by
        N,S,replicate. v2 defines its reference as a rational mean over the
        declared U and x pairs and still reports only N,S,replicate cells; it
        does not include a target-set digest in the cell or pool the observed
        samples consistently. The graph version, target-set/start derivation,
        and exact seed-to-counter mapping are named but not assigned literal
        generator bytes. Numerator/denominator storage for every time through
        the declared horizon has no rational field grammar or bound. This
        control can remain synthetic-only, but it is not yet a single
        replayable reference test.
      references:
        - experiments/EXP-SSI-e29417/specification.yaml:564-582
        - experiments/EXP-SSI-e29417/specification.yaml:867-876
        - experiments/EXP-SSI-e29417/specification.yaml:1130-1141
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-c96ef6/red_team_report.md:303-323

    - id: RT-9E3C34-PROVENANCE-SCHEMA
      severity: provenance_caveat
      finding: >-
        The v7 direct predecessor binding is now consistent with the batch
        manifest and producer artifacts: EXP-SSI-8fbe66 and the BATCH-b47cd5
        reports are named. The immutable snapshot receipt itself nevertheless
        retains commit_sha:null and verification.status:pending_post_commit,
        while the queue-binding commit records 88e258219 as the snapshot
        archive commit. That is a surviving self-binding caveat, not evidence
        that the snapshot was changed. The prior BATCH-b47cd5 Validator also
        recorded legacy experiment-schema drift for the predecessor/successor
        record shape; no additive schema-supersession artifact is present in
        this batch, and this review did not run a schema diagnostic. Treat the
        issue as unresolved provenance/schema debt, not as a scientific
        observation.
      references:
        - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/dispatch_queue.json:26-37
        - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/archives/TASK-20260809-2eea70/snapshot-receipt.json:1-20
        - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/tasks/TASK-20260809-b1b31a/refinement_report.yaml:13-19
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b47cd5/reviews/TASK-20260809-ed64bf/validation_report.yaml:82-120

  required_controls:
    - >-
      Add an explicit v7 supersession table: every v1/v6 field, seed, domain,
      control, count, digest, output, and cost equation must be marked
      superseded or retained, with one canonical SSI-BYTES-v1.1 grammar and
      literal code table. Do not leave v1 and v2 clauses co-normative.
    - >-
      Define C-HELPER-v2's endpoint table, canonical pair-record array,
      endpoint/pair cardinalities, duplicate/uniqueness rule, payload record
      bytes, endpoint_slot and payload_ptr ranges, descriptor slot widths, and
      exact body/header serialization. Freeze both digest preimages including
      field omission/placeholder rules and the c_helper_key frame.
    - >-
      Define ORDER-MANIFEST-v2's owner extraction for each branch, generator
      source digest and version bytes, record digest preimage, all header
      lengths, body duplicate/capacity rules, and setup artifact path. State
      explicitly whether any full-vertex order table is permitted and charge
      its exact owner set and storage if it is.
    - >-
      Define the target-index selection-index generator, branch-record mapping,
      target/index header, b_selection, H_Q encoding, empty/duplicate rules,
      query-key domain and frame literals, and exact probe/payload path. Tie
      every attempt to one selection index without a scan or secondary oracle.
    - >-
      Provide a field-by-field integer envelope for all counters, H_Q/H_C slot
      widths, degree products/factors, edge matrices, HNF intermediates,
      witnesses, FOE, rational references, and Q. Remove the simultaneous v1
      u64/raw-field grammar or define explicit v1.1 exceptions.
    - >-
      Add a finite-manifest-exhaustion terminal and canonical null/padding
      record, including whether padding contributes to S_eff, how it is
      indexed, and all bytes/costs. Resolve the S_req=0 cap rule and assign
      literal terminal/reason codes and counter scopes.
    - >-
      Supply a committed INCUMBENT-FOE-v1 input and branch-specific setup,
      attempt, memory, and certificate equations. Separate setup construction
      from per-attempt access, define restart/cap conditioning, map every event
      to FOE, and leave Q_break_even undefined unless all operands are bound.
    - >-
      Freeze one certificate grammar with one edge-count encoding, all
      provider/mirror/receipt fields and maxima, literal root frames and root_0,
      transition IDs, degree-to-matrix mapping, and certificate/header/output
      memory. Preserve unavailable bytes as operational unavailability.
    - >-
      Define the actual HNF row-reduction and saturation algorithms, matrix and
      factor encodings/bounds, middle-factor composition, scalar predicate,
      normalized witness bytes, and every digest preimage. Make the v2 output
      record the sole output grammar.
    - >-
      Freeze event tag/payload tables, FOE encodings, trace hash preimages,
      separate treatment/replay records, witness lengths, delta_path formula,
      and the exact continuation/attempt set after early success. Require
      certificate bytes and all post-gate data needed for replay identity.
    - >-
      Bind S_eff-specific applicability, null domains/frames, draw width and
      rejection encoding, exhaustion terminal classes, and owner-specific
      certificate/path construction for every permutation and owner-mismatch
      control.
    - >-
      Choose one C-pair reference: either fully define the eight-replicate
      C_iid gate or replace it with the 256-replicate dependent reference.
      Serialize histogram inputs, seed list, quantile rule, endpoint universe,
      treatment/null generators, duplicate policy, and descriptor/helper access.
    - >-
      Make synthetic observations and references use the same unit: include
      target-set identity in each cell or pool observations over the exact U/x
      population. Freeze graph version, target/start derivation, rational field
      bounds, and reference digest while retaining the non-SSI boundary.
    - >-
      Preserve the pending snapshot receipt and have the Coordinator record any
      separate post-commit verification and schema-supersession decision
      additively; do not edit this snapshot, its producer files, predecessors,
      queue, or prior review reports.

  counterexample_or_mutation: >-
    Static mutations only; none were executed. (1) Give an A_tagged record a
    lookup_curve_id different from the owner embedded in its order_tag: the
    v2 owner-set rule has no unique answer. (2) Give one endpoint two distinct
    pair records: A_C, endpoint_slot, payload_ptr, and the undefined endpoint
    table admit multiple helper layouts. (3) Select S_req=0: the top-level
    exact-zero cap and v2 max(1,...) cap disagree. (4) Apply the top-level
    eight-replicate C_iid gate and the v2 256-replicate empirical gate to the
    same null: both cannot be the frozen acceptance rule. (5) Compare one
    target-set synthetic CDF against the v2 mixture reference without a U
    digest: the cell unit is not the same. (6) Select an edge certificate with
    v2 b_count edge_count and a v1 uint32 edge body: the count equality bytes
    are unspecified. These are text-level representation and quantifier
    attacks, not experiments, diagnostics, cryptographic computations, or
    scientific observations.

  baseline_comparison: >-
    No Pollard-rho, BSGS/MITM, specialized baseline, arithmetic row, timing,
    physical table, cost measurement, or scientific control was executed or
    observed. S=0, the B sigma mapping, and the incumbent p^(1/3+o(1)) label
    remain declarations; T_inc_foe is an unbound future input. No gain,
    break-even point, security effect, exponent movement, or comparison with a
    baseline follows from the snapshot.

  heuristic_challenges:
    - >-
      The fixed-advice quantifier forall p exists fixed A_p forall E in V_p
      and the non-transfer status of H-ADV-1-R survive as claim boundaries;
      neither is validated by this review or by the design text.
    - >-
      H-ADV-2 remains load-bearing for order generation, membership output,
      certificate availability, HNF pullback, and C composition. The missing
      generator/source, path, and output schemas prevent a closed conditional
      cost row.
    - >-
      H-ADV-3 remains restricted to named typed branches and cannot become an
      all-advice statement through the target index. H-ADV-4 remains
      unverified because the dependent null/reference gate is inconsistent.
    - >-
      The synthetic graph arm remains a model-only diagnostic and cannot
      validate H-ADV-1-W or an SSI curve claim, even after its reference schema
      is repaired.

  cost_model_challenges:
    - >-
      The target-domain expansion is an important surviving cost obligation,
      but undefined b_selection, index header/payload storage, and selection
      wiring prevent its byte and FOE total from being evaluated.
    - >-
      C-helper, order, certificate, path, HNF, output, replay, and rational
      reference storage are named as cost axes but not given a single complete
      physical byte/event equation.
    - >-
      The finite q_run formula is explicitly finite-only and must not replace
      symbolic worst-case q(A_p,E). Because the cap probability, setup/access
      split, and incumbent input remain unbound, this review does not infer a
      negative or positive cost result.

  reduction_and_scope_challenges:
    - >-
      The claim ceiling correctly excludes all-advice lower bounds, an attack,
      security claims, exponent movement, EndRing/Isogeny transfer, SQIsign or
      CSIDH parameter claims, and deployed-scheme conclusions.
    - >-
      An external EDGE-CERT remains an explicit dependency rather than a free
      cryptanalytic construction. Even with provider bytes available, the v2
      certificate and output defects prevent an end-to-end cost claim.
    - >-
      No affected-versus-safe scheme conclusion is made. Any future closure
      must keep the named OneEnd/EndRing boundary and the out-of-scope
      SIDH/SIKE torsion-image boundary intact.

  proof_architecture_challenges:
    - >-
      The fixed-A_p quantifier, union-before-counting fiber rule, typed branch
      ceiling, and non-SSI nearby diagnostic boundary survive as proof-map
      obligations only. They do not prove that the physically bound advice
      object has the claimed fiber or that an external path is generated.
    - >-
      The observation-collision split between B-tagged and B-membership is
      useful, but owner-set extraction, order setup, target-index expansion,
      and shared payload costs are not unified, so no Pareto comparison or
      monotonicity result is available.
    - >-
      The controls remain pre-registered gates, not completed controls. No
      failed control, heuristic value, arithmetic row, or scientific
      observation is recorded here.

  narrowest_supported_statement: >-
    The committed 88e258219 snapshot, as bound by the 81ad78fd3 queue
    descendant, is an additive, execution-unauthorized design refinement of
    EXP-SSI-8fbe66. It preserves the narrow fixed-advice, typed-branch,
    design-only claim ceiling and materially names more physical components,
    including a target-domain expansion and an unavailable-certificate
    boundary. It is not yet a single byte-exact, cryptographic-scale,
    physically charged, output-producing, replay-reproducible, branch-complete
    contract. No mathematical, cryptanalytic, security, exponent, novelty,
    hypothesis-transition, completion, negative, or baseline result follows.
    Design repair is not an observation; execution and diagnostics remain
    unauthorized.

  next_concrete_action: >-
    The Coordinator should create an additive successor that first declares
    v7 precedence over v1/v6 clauses, then closes the helper/order/index wire
    schemas, all integer envelopes, finite padding/accounting, certificate and
    HNF/output bytes, replay continuation, null/C-pair gates, and synthetic
    cell semantics. Preserve all predecessor, producer, snapshot, queue, and
    prior-review bytes; retain execution_authorized=false; and obtain fresh
    independent Validator and Red Team review from the new committed snapshot.

  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/reviews/TASK-20260809-9e3c34/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-5a886c/reviews/TASK-20260809-9e3c34/runtime-session-receipt.json
```

## Verdict and no-execution boundary

**`DISSENT` on freeze, arithmetic-row production, and execution readiness; `CONCUR` on the additive design-only scope, the narrow claim ceiling, the external-certificate dependency boundary, the synthetic non-SSI boundary, and the unauthorized execution state.**

This is a static red-team review of the committed v7 contract. The surviving blockers are representation and accounting defects, not observations that the SSI route succeeds or fails. No experiment, diagnostic, cryptographic computation, arithmetic-row generator, network retrieval, timing, or scientific control was executed. No predecessor, producer artifact, queue, ledger, or prior review report was edited; the only intended writes are the two declared artifacts listed above.
