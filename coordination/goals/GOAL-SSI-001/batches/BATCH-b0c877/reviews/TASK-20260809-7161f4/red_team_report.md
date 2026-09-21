# Red-team report — `TASK-20260809-7161f4`

```yaml
red_team_report:
  id: RT-20260809-7161f4
  task_id: TASK-20260809-7161f4
  goal_id: GOAL-SSI-001
  batch_id: BATCH-b0c877
  role: red-team
  independent_session: true
  claim_under_review: >-
    Whether the exact SSI-CANONICAL-v11 design in EXP-SSI-bf10ef is a
    universal, byte-recomputable, target-free-advice, finite, semantically
    edge-verifiable, physically charged contract for the named classical
    OneEnd boundary, with identifiable paired replay and comparable controls
    and incumbent admission. This review makes no SSI, OneEnd, EndRing,
    security, exponent, novelty, performance, or scientific claim.
  reviewed_snapshot:
    requested_snapshot_commit: 1f68ed0cd235fec08ee9abe86cd43316cb63b170
    requested_commit_status: resolved_exactly
    snapshot_parent: fff4e24145e486b35de73e2ad56326b143936db6
    worktree_head_at_start: 5338b8caa4e4cd80f5eb4c9a67ee8b9a312511ff
    experiment_path: experiments/EXP-SSI-bf10ef/
    predecessor_experiment: EXP-SSI-7b1469
    predecessor_v10_review_context:
      - coordination/goals/GOAL-SSI-001/batches/BATCH-cdcf50/reviews/TASK-20260809-68dca1/red_team_report.md
      - coordination/goals/GOAL-SSI-001/batches/BATCH-cdcf50/reviews/TASK-20260809-80c7d5/validation_report.yaml
    snapshot_receipt: coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/archives/TASK-20260809-6dfe00/snapshot-receipt.json
    snapshot_receipt_status: >-
      The requested commit is the review boundary and is reachable exactly.
      Its immutable snapshot receipt retains commit_sha:null and
      verification.status:pending_post_commit. That is an archival provenance
      caveat; it is not a reason to substitute the later worktree HEAD and is
      not scientific evidence.
  objections:
    - id: RT11-001
      category: universal_framing_and_registry_parity
      status: partial_pass_with_freeze_blocker
      severity: freeze_blocking
      finding: >-
        V11 makes the outer frame, widths, 29 symbolic registry rows, and the
        top-level/subrecord distinction much more explicit. The symbolic
        tag/name/final-field rows in FRAME-REGISTRY-v6 match the specification
        table. That parity is not a materialized registry: every schema_digest
        and registry_digest is null, so the hard gate cannot be satisfied. More
        seriously, the subrecord rule says a subrecord has no independent digest,
        while ENDPOINT-v6 has endpoint_digest as a final field, PAYLOAD-v6 has
        payload_digest, and the C-PAIR, synthetic, EVENT, OP, SATURATION-ROW,
        and replay subrecords also carry digest fields. V11 never defines the
        distinction between an allowed local digest and the prohibited
        independent digest, nor the preimage for several of those local fields.
        The NULL-RECORD description says the total object is 4096 bytes but does
        not state whether its listed fields are the payload or the complete
        outer frame, unlike the owner description. Two conforming serializers
        can therefore still disagree about local-digest status and the null
        frame prefix/length.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:92-135
        - experiments/EXP-SSI-bf10ef/specification.yaml:137-173
        - experiments/EXP-SSI-bf10ef/specification.yaml:261-271
        - experiments/EXP-SSI-bf10ef/specification.yaml:292-309
        - experiments/EXP-SSI-bf10ef/specification.yaml:352-377
        - experiments/EXP-SSI-bf10ef/inputs/FRAME-REGISTRY-v6.yaml:7-42
      falsification_route: >-
        Hold all semantic values fixed and materialize one serializer that
        treats endpoint_digest and row_digest as raw subrecord fields and a
        second that applies the subrecord prohibition or includes a framed
        prefix in NULL-RECORD-v6. Both satisfy the present prose but produce
        different bytes. This is a static observation-fiber mutation; it was
        not executed.
      exact_repair: >-
        Choose one rule for local subrecord digests, publish a field-level
        preimage and participation rule for every such digest, and either
        register the local schemas or explicitly mark them as non-digesting
        raw fields. Give NULL-RECORD-v6 an exact payload grammar, outer prefix,
        payload length, padding equation, and empty case. Materialize the
        registry and all non-null schema digests before freeze.
      classification: design_contract_not_research_evidence

    - id: RT11-002
      category: digest_preimages_and_dependency_breaking
      status: incomplete
      severity: byte_recomputability_blocking
      finding: >-
        The terminal stream cycle is repaired in principle: stream_digest
        excludes both terminal digests, and terminal_digest depends on the
        resulting stream_digest. That attack therefore does not establish a
        direct cycle under the intended interpretation. It remains ambiguous
        how the shortened terminal preimage serializes its outer payload_len.
        Other preimages remain absent or only named: manifest has no declared
        curve-id-table digest even though source_domain_frame requires one;
        source_algorithm_digest, source_blob_digest, map_digest, endpoint_digest,
        event_digest, op_digest, row_digest, arm_input_digest,
        normalized_digest, shared_prefix_digest, shared_digest,
        null_mutation_digest, artifact_digest, and mirror_digest have no sole
        byte-level preimage in the active contract. The provider sign rule also
        does not say whether Ed25519 signs the complete tag-18 preimage, the
        sign_digest bytes, or another domain-separated message. A final-digest
        rule for top-level frames does not resolve these embedded and signature
        message choices.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:203-215
        - experiments/EXP-SSI-bf10ef/specification.yaml:216-246
        - experiments/EXP-SSI-bf10ef/specification.yaml:272-280
        - experiments/EXP-SSI-bf10ef/specification.yaml:292-377
        - experiments/EXP-SSI-bf10ef/specification.yaml:394-409
        - experiments/EXP-SSI-bf10ef/specification.yaml:323-351
      falsification_route: >-
        Ask two serializers to compute curve_id_table_digest, one local event
        digest, and sign_digest while holding all visible field values fixed;
        allow one to hash raw fields and the other to hash complete nested
        frames. Ask the terminal serializers whether the shortened frame carries
        the original or shortened payload_len. The snapshot supplies no
        rejection rule selecting one answer. No digest was computed.
      exact_repair: >-
        Add an acyclic digest dependency table naming ordered bytes, complete
        versus shortened outer frames, lengths, domain codes, and omitted
        fields for every digest field. Define the manifest curve-table digest,
        source and map identities, artifact/mirror byte domains, and the exact
        signed message. Give each special digest a concrete type rather than
        relying on the universal top-level rule.
      classification: byte_contract_not_research_evidence

    - id: RT11-003
      category: source_advice_quantifier_and_hidden_oracle
      status: partial_pass_with_unclosed_source_boundary
      severity: execution_blocking
      finding: >-
        Moving TARGET-MANIFEST and TARGET-INDEX construction to phase 1 is a
        real repair: the stated A_p no longer contains an explicit target,
        attempt, selection, or target-index field, and the owner ranking itself
        is target-free. The universal quantifier is not yet operationally
        closed. A_p contains a source_domain_frame and a helper payload blob,
        but the source algorithm and source bytes are represented only by
        digest identifiers; no source tree/path/commit binding, finite source
        grammar, or target-free source transcript is included. The required
        source reads are a future charge promise, not a current definition of
        the source object. The undefined curve-id-table digest and undefined
        matrix/payload relations further prevent a verifier from reconstructing
        the same A_p from p alone. The contract therefore narrows the
        quantifier correctly but does not prove that two admissible producers
        must build the same fixed advice.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:73-90
        - experiments/EXP-SSI-bf10ef/specification.yaml:203-246
        - experiments/EXP-SSI-bf10ef/specification.yaml:379-403
        - experiments/EXP-SSI-bf10ef/inputs/EDGE-ALGORITHM-v6.yaml:6-23
        - experiments/EXP-SSI-bf10ef/inputs/EDGE-ALGORITHM-v6.yaml:24-41
      falsification_route: >-
        Hold p, manifest_digest, advice_seed, and all visible source digests
        fixed at the interface level, then supply two source interpreters with
        different path/commit or matrix-generation semantics. If both satisfy
        the visible digest and source-domain fields, they yield different
        helper bytes or edge relations without a stated first rejection. This
        is a proposed static mutation, not an executed source test.
      exact_repair: >-
        Bind source bytes, source-tree commit, canonical path namespace,
        algorithm version, source digest preimage, and a finite target-free
        transcript into the advice artifact. Define curve-id-table and
        payload/matrix construction byte-for-byte, and state explicitly which
        source material belongs to A_p and which is charged phase-1 input.
      classification: quantifier_order_and_method_boundary_not_research_evidence

    - id: RT11-004
      category: finite_seeds_terminal_totalization_and_cycle
      status: partial_pass
      severity: freeze_blocking
      finding: >-
        V11 correctly rejects a prose finite-list uniformity assertion, binds
        attempt indices to unique DOMAIN-v6 seed frames, and gives an intended
        acyclic stream/terminal digest order. The finite builder is still not a
        total construction. The request has attempt_count but no explicit
        attempt-index-to-owner emission function, no named finite owner manifest
        input for exhaustion, and no candidate-cap input or exact
        CANDIDATE_CAP predicate. The terminal equations count asserted strides
        and records, but do not bind terminal_position to a stride index,
        requested_count to a bounded seed-list object, or each emitted
        owner_index to the committed order. REPLAY_IDENTITY_FAILURE has a code
        but no terminal predicate or precedence relation. The seed-list and
        pair/null transcript bounds are also not stated as field-level
        admission inequalities. Thus the cycle repair holds conditionally,
        while terminal totalization and finite-stream identity remain open.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:175-201
        - experiments/EXP-SSI-bf10ef/specification.yaml:247-284
        - experiments/EXP-SSI-bf10ef/specification.yaml:454-461
        - experiments/EXP-SSI-bf10ef/specification.yaml:511-516
      falsification_route: >-
        Keep request_digest and seed_list_digest fixed, vary the mapping from
        attempt indices to owner records, and emit a self-consistent count
        vector with a different terminal_position or candidate set. Also emit
        the same stream with CANDIDATE_CAP and REPLAY_IDENTITY_FAILURE. The
        active text does not force one owner schedule or precedence outcome.
        No stream was generated.
      exact_repair: >-
        Add an explicit finite owner/order input and deterministic attempt to
        owner schedule, require attempt_count <= attempts_max, define every
        candidate-cap and replay-failure predicate, bind terminal_position and
        reason to the exact stream prefix, and publish one total terminal
        precedence table. Give pair/null rejected draws a complete bounded
        transcript grammar and make the terminal shortened-frame length rule
        explicit.
      classification: finite_contract_not_research_evidence

    - id: RT11-005
      category: semantic_edge_and_provider_boundary
      status: admission_boundary_holds_but_semantics_are_pending
      severity: admission_blocking
      finding: >-
        The provider boundary is correctly conservative: PROVIDER-TRUST-v6 has
        null identity/key fields, EDGE-ALGORITHM-v6 has null implementation and
        independent replay receipts, provider work is transport-only, and the
        specification declares every certificate invalid until the typed
        semantic implementation and replay exist. This prevents the current
        design from treating a provider signature as a mathematical edge or as
        evidence. It does not close the future boundary. The edge manifest's
        opcode operand_schema and witness_schema are bytestring names, not the
        actual finite-field equations, and artifact/mirror digest preimages and
        mirror-path namespace are absent. The receipt relation does not fully
        specify the signed-message bytes. A trusted provider could therefore
        still be an oracle in any future materialization unless the independent
        edge verifier and byte/path relations are made concrete.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:285-351
        - experiments/EXP-SSI-bf10ef/specification.yaml:410-417
        - experiments/EXP-SSI-bf10ef/inputs/EDGE-ALGORITHM-v6.yaml:6-41
        - experiments/EXP-SSI-bf10ef/inputs/PROVIDER-TRUST-v6.yaml:5-17
      falsification_route: >-
        Supply a byte-valid provider receipt and continuous transition frames
        whose transition witnesses are not recomputable by a uniquely specified
        edge program; ask whether the contract rejects them before provider
        trust is consulted. Separately vary mirror bytes or path namespace while
        preserving the visible artifact/mirror fields. These are future static
        mutations only; no provider was contacted.
      exact_repair: >-
        Materialize the EDGE-ALGORITHM-v6 program, all opcode equations,
        transcript and witness schemas, source/destination/factor relation, and
        independent replay receipt. Define artifact and mirror hash domains,
        canonical path policy, receipt-to-certificate field equality, and the
        exact Ed25519 signed message. Retain provider work as transport-only.
      classification: semantic_admission_gate_not_research_evidence

    - id: RT11-006
      category: event_foe_and_memory_cost_accounting
      status: incomplete
      severity: cost_recomputation_blocking
      finding: >-
        V11 improves the event width, numeric code list, primitive table, and
        buffer inventory. The event schedule still omits a unique population for
        seed derivation/list reads, request and owner/null record processing,
        stream digest construction, provider/certificate root work, and several
        serialization and terminal paths. No rule maps event_code multiplicity
        to the number of field operations in an edge check, HNF step, signature
        check, or replay arm. Primitive codes 9 (serialization) and 10
        (buffer allocation/release) have no FOE or byte equation. EVENT-v6's
        event_digest and operand_digest preimages are also undefined, and the
        single input_bytes field cannot by itself distinguish input, output,
        hash, mirror, serialization, and memory byte populations. On memory,
        BUFFER-v6 has no class separating M_advice from M_work, no explicit
        strict allocation/release ordering, and no field-level binding of every
        external source/mirror lifetime to an interval. The global maxima are
        listed but not tied to explicit count inequalities. Exact total_foe,
        total_bytes, M_advice, and M_work are therefore not recomputable from
        the contract alone.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:192-201
        - experiments/EXP-SSI-bf10ef/specification.yaml:352-361
        - experiments/EXP-SSI-bf10ef/specification.yaml:432-469
        - experiments/EXP-SSI-bf10ef/specification.yaml:511-521
      falsification_route: >-
        Hold the visible event list fixed while varying the number of field
        operations inside one edge check, the mirror bytes retained during a
        signature, or the serialization staging lifetime. Also assign the same
        BUFFER-v6 rows to advice and work in opposite ways. The present fields
        permit equal-looking traces with different work or category peaks. No
        cost trace or memory table was produced.
      exact_repair: >-
        Publish a complete phase/event population table and primitive equations,
        including all hash/signature/provider/mirror/read/write/output bytes and
        multiplicities. Add preimages for event-local digests, explicit input
        and output byte accounting, buffer class, strict interval and sentinel
        rules, count inequalities, and one reconciliation equation for all
        reported totals.
      classification: cost_model_not_research_evidence

    - id: RT11-007
      category: deterministic_hnf_saturation_and_output
      status: not_closed
      severity: semantic_execution_blocking
      finding: >-
        The v11 HNF text is materially more specific but is not a unique
        algorithm. It says to choose the lowest-index nonzero pivot row and then
        breaks ties by smallest absolute entry; among distinct rows the first
        rule already decides, so the second rule has no defined trigger. It
        combines a Euclidean quotient with a quotient truncated toward zero,
        without a quotient/remainder equation. For example, with an entry 3 and
        pivot 5, truncation toward zero gives quotient 0 and remainder 3,
        outside [-2.5,2.5); choosing quotient 1 gives remainder -2 but is not
        the stated truncation rule. The text does not specify zero-pivot/rank
        termination, sign-normalization ordering, factor-to-matrix construction,
        or exact empty/overflow behavior. SATURATION-v6 lacks first/next
        pre/post digest chaining equations, and OUTPUT-v6 still delegates the
        non-scalar predicate and witness equations to unspecified typed rules.
        A self-consistent operation log can therefore remain distinct from the
        deterministic HNF/output path.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:292-315
        - experiments/EXP-SSI-bf10ef/specification.yaml:298-309
        - experiments/EXP-SSI-bf10ef/specification.yaml:418-431
        - experiments/EXP-SSI-bf10ef/inputs/EDGE-ALGORITHM-v6.yaml:24-35
      falsification_route: >-
        Use a matrix containing two eligible pivot rows and a signed entry whose
        nearest canonical remainder differs from truncation toward zero. Hold
        factors and all local digest fields fixed while choosing either legal
        interpretation. Then choose two saturation sequences with the same
        initial matrix digest but different pre/post chaining. These are static
        observation-fiber mutations, not HNF executions.
      exact_repair: >-
        Replace the prose with a total pseudocode-level algorithm: pivot
        ordering, signed division and remainder equation, normalization order,
        zero/rank termination, factor consumption, overflow, and empty cases.
        Define matrix construction and all saturation chain equalities, then
        state the exact scalar/non-scalar predicate and typed witness equations
        that output verification recomputes.
      classification: proof_and_output_contract_not_research_evidence

    - id: RT11-008
      category: paired_replay_null_identity
      status: incomplete
      severity: control_contract_blocking
      finding: >-
        The typed PAIR-REQUEST, ARM-TRACE, SHARED-TRACE, and FINAL-IDENTITY
        frames repair the v10 absence of widths. They do not define the
        semantics that make the pair identifiable. shared_prefix_digest,
        normalized_digest, arm_input_digest, and null_mutation_digest have no
        preimages or normalization function. The phrase "canonical prefix
        through pair_request_digest" is especially unsafe because the pair
        request itself contains branch, treatment_owner, null_owner,
        draw_count, and null-mutation fields; the contract does not state which
        of those are pair-shared and which are arm-specific. There is no rule
        that null_owner differs from treatment_owner, no deterministic null
        draw/mutation relation, and no equation requiring identity_bit to equal
        equality of normalized shared material. A pair can consequently assert
        an identity bit with arbitrary arm traces while satisfying local widths
        and final digests.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:362-377
        - experiments/EXP-SSI-bf10ef/specification.yaml:404-409
        - experiments/EXP-SSI-bf10ef/specification.yaml:471-481
      falsification_route: >-
        Keep target, advice, attempt, and query_key fixed; set null_owner equal
        to treatment_owner, change only null_mutation_digest, and flip
        identity_bit while recomputing local final digests. Ask which field or
        semantic predicate rejects each mutation. Also make the two arms differ
        only after the claimed shared prefix and compare the resulting shared
        digest. No pair replay was materialized.
      exact_repair: >-
        Define the null-owner draw law and rejection of the treatment owner,
        exact pair-shared and arm-specific field sets, a canonical normalization
        function, all digest preimages, continuation/censoring behavior, and
        identity_bit as a recomputed equality predicate. Serialize every
        rejected draw and bind the pair to a typed control receipt.
      classification: control_contract_not_research_evidence

    - id: RT11-009
      category: control_materialization_and_comparability
      status: admission_gate_holds_but_control_contract_is_not_comparable
      severity: control_admission_blocking
      finding: >-
        The conservative admission boundary holds: both C-PAIR-REF-v6 and
        SYNTHETIC-REF-v6 explicitly have no measured rows/cells and no
        independent receipts, and the specification correctly classifies them
        as INVALID_CONTROL rather than negative evidence. The manifests do not
        yet force comparable future tables. C-PAIR does not state the endpoint
        universe, exact endpoint_count rule, or success/acceptance relation, and
        its local row_digest conflicts with the global subrecord digest rule.
        SYNTHETIC claims an exact rational initial state in the specification,
        but the input manifest gives no initial numerator/denominator or
        success/attempt generator; a censored target rule alone cannot recreate
        the rows. The cell/row table digest relation is described as raw
        concatenation without a complete control-frame preimage. Eight cells
        and sixteen rows per cell are counts, not a matched null identity.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:316-322
        - experiments/EXP-SSI-bf10ef/specification.yaml:471-481
        - experiments/EXP-SSI-bf10ef/controls/C-PAIR-REF-v6.yaml:7-34
        - experiments/EXP-SSI-bf10ef/controls/SYNTHETIC-REF-v6.yaml:6-28
      falsification_route: >-
        Materialize two control producers using the visible seeds and counts,
        but choose different endpoint universes or synthetic initial states.
        Both can preserve the listed row widths and local fields because the
        missing generator/state relations do not select one table. This is a
        proposed control mutation; no control rows or cells were generated.
      exact_repair: >-
        Bind the endpoint universe, selection/rejection/acceptance law, and
        exact C-pair target relation. Publish synthetic initial values and the
        success/attempt recurrence generator. Define all control subrecord
        preimages and the complete tag-28/tag-29 table frames, then obtain
        independent replay receipts before any control result is used.
      classification: control_manifest_not_research_evidence

    - id: RT11-010
      category: incumbent_admission_and_cost_comparability
      status: gate_holds_but_comparison_is_blocked
      severity: comparison_blocking
      finding: >-
        The incumbent gate is correctly conservative. INCUMBENT-FOE-v1 has
        null FOE, memory, source, and independent-receipt fields and explicitly
        sets comparison_allowed:false and freeze_allowed:false. V11 therefore
        makes no baseline, break-even, or advantage claim. A second comparison
        defect remains even after those nulls are populated: the incumbent's
        advice_model is no_fixed_advice, while the successor's scoped
        construction is fixed-advice with potentially large preprocessing and
        memory. The V11 text asks for a common setup/Q convention but gives no
        equation that includes advice construction, source/provider work,
        per-query cost, finite success probability, or the number of queries
        q. break_even_q is a required metric without a definition. A measured
        no-advice incumbent cannot be compared to fixed advice by matching only
        per-prime FOE and peak memory.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:36-47
        - experiments/EXP-SSI-bf10ef/specification.yaml:471-493
        - experiments/EXP-SSI-16649/inputs/INCUMBENT-FOE-v1.yaml:5-45
      falsification_route: >-
        Hold a future incumbent's query FOE fixed while charging or omitting
        the one-time A_p construction and source/helper memory. The two choices
        produce different break-even q values while satisfying the current
        required incumbent fields. This is a cost-scope mutation only; no
        incumbent measurement was used or created.
      exact_repair: >-
        Obtain independently archived per-prime incumbent source bytes,
        command, commit, exact FOE, memory, and replay receipt. Define a common
        advice/preprocessing/Q scope and an explicit total-cost equation that
        includes setup, A_p, source/edge/provider work, finite success/failure,
        query cost, and memory. Define break_even_q only from those matched
        quantities, and preserve comparison_allowed:false until all are bound.
      classification: baseline_admission_not_research_evidence

    - id: RT11-011
      category: backend_execution_and_claim_boundary
      status: holds
      severity: operational_boundary_preserved
      finding: >-
        The execution boundary holds in the requested snapshot. The experiment
        is review_required, frozen:false, execution_authorized:false,
        evidence_eligible:false, and maximum_runs:0; the batch manifest also
        sets execution_authorized:false and a design-only claim ceiling. Missing
        provider, edge, controls, incumbent, and backend material is not
        treated as research evidence. No backend was selected or probed in this
        review, so the native session model label remains operationally
        unverified. The snapshot receipt's pending post-commit verification is
        a provenance caveat only. There is no basis for fallback, execution, or
        a scientific interpretation.
      references:
        - experiments/EXP-SSI-bf10ef/specification.yaml:1-52
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/batch_manifest.json:1-27
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/dispatch_queue.json:75-157
        - coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/archives/TASK-20260809-6dfe00/snapshot-receipt.json:1-26
      falsification_route: >-
        A future execution attempt would violate the present hard boundary
        before it could yield evidence. This review performed no such attempt,
        probe, parser, arithmetic check, network request, or experiment.
      exact_repair: >-
        None is required for the current boundary. Preserve the current
        design-only flags and add no backend receipt until a Coordinator
        separately authorizes a materialization task after the contract and
        admission gates pass.
      classification: execution_boundary_not_research_evidence

  required_controls:
    - >-
      Resolve the outer/subrecord distinction, local digest policy, all local
      digest preimages, NULL-RECORD framing, registry serialization, and
      non-null schema/registry digests.
    - >-
      Bind the source algorithm and source bytes to a canonical path, commit,
      finite grammar, and target-free transcript; define curve-table,
      payload/matrix, and map identities.
    - >-
      Publish the finite seed-list inequalities, deterministic attempt-to-owner
      schedule, owner exhaustion input, candidate-cap predicate, complete
      terminal precedence, and shortened-terminal length rule.
    - >-
      Materialize the edge implementation and independent replay, with typed
      field equations, witness relations, transcript rules, provider receipt
      equality, signature preimage, mirror/artifact domains, and path policy.
    - >-
      Freeze a complete event population and primitive-charge table, including
      local event preimages, provider/hash/signature/read/write/output bytes,
      and explicit total-FOE/total-bytes reconciliation.
    - >-
      Add buffer class, exact allocation/release and external-lifetime rules,
      count inequalities, and recomputable M_advice/M_work peaks.
    - >-
      Replace HNF prose with total deterministic pseudocode and equations for
      signed division, pivot/tie order, zero/rank termination, factor mapping,
      saturation chaining, overflow, empty cases, scalar predicates, and
      witness verification.
    - >-
      Define paired replay's shared/arm-specific bytes, null-owner mutation
      law, normalization, all preimages, continuation/censor semantics, and
      identity-bit equality predicate.
    - >-
      Materialize C-pair and synthetic generators/states, complete control
      frames, rows/cells, and independent replay receipts before treating them
      as controls.
    - >-
      Materialize and independently verify the incumbent under an advice and
      preprocessing scope matched to A_p, then define the total-cost and
      break_even_q equations before comparison or freeze.

  counterexample_or_mutation: >-
    No mutation was executed. The cheapest decisive static mutations are:
    (1) serialize a local digest-bearing subrecord under the allowed-local and
    prohibited-independent interpretations; (2) include versus omit the
    shortened NULL/terminal outer prefix and payload length; (3) choose two
    source interpreters or helper matrix relations behind the same visible
    source identifiers; (4) vary attempt-to-owner mapping and terminal reason
    while preserving counts; (5) use signed entry 3 with pivot 5 to expose the
    truncating-versus-canonical remainder ambiguity; (6) choose two saturation
    chains with the same initial matrix digest; (7) set null_owner equal to
    treatment_owner and flip identity_bit; (8) choose different C-pair endpoint
    universes or synthetic initial states; and (9) include versus omit fixed
    advice construction in a prospective break-even calculation. These are
    contract mutations, not observations or experiments.

  baseline_comparison:
    status: blocked_by_pending_incumbent_and_unclosed_cost_scope
    result: >-
      No Pollard-rho, BSGS, specialized-baseline, break-even, speed, memory,
      security, or cryptanalytic comparison is admissible. The incumbent is
      explicitly pending, its advice model is no_fixed_advice while the
      successor is fixed-advice, and V11 defines no total break_even_q equation.

  heuristic_challenges:
    - >-
      No heuristic, sample, success probability, empirical distribution, FOE
      measurement, or cryptographic-scale observation is present or claimed.
      The finite seed list is explicitly not asserted uniform; its existence
      cannot supply a success model.
    - >-
      The fixed-advice quantifier is narrowed to target-free visible fields,
      but source bytes, source semantics, and helper/matrix reconstruction are
      not yet a fully bound A_p. This is a design uncertainty, not a negative
      result about the quantifier or SSI.

  cost_model_challenges:
    - >-
      Event populations, primitive equations, local digest preimages,
      serialization/output accounting, and provider/mirror work are not yet
      sufficient to recompute total_foe or total_bytes.
    - >-
      Buffer intervals do not classify advice versus work or bind every external
      source/mirror and staging lifetime, so M_advice and M_work are not closed.
    - >-
      The incumbent comparison omits an explicit matched advice/preprocessing
      scope and a total break_even_q equation.

  reduction_and_scope_challenges:
    - >-
      A provider signature, path continuity, transition root, or HNF digest
      does not establish a valid OneEnd edge without the missing independent
      EDGE-ALGORITHM-v6 relation and witness replay.
    - >-
      Nothing in this design supports an EndRing, Isogeny, SQIsign, CSIDH,
      SIDH, deployed-security, lower-bound, exponent, or all-advice claim.
      The current claim ceiling correctly excludes all of them.
    - >-
      The finite controls and incumbent are admission conditions, not null or
      negative evidence. Missing rows, cells, measurements, and receipts must
      remain blockers.

  proof_architecture_challenges:
    - >-
      Observation-fiber attack: local digest fields, pointer fields, event
      fields, HNF logs, and replay identity bits admit alternative visible
      interpretations unless the missing cross-field equations are added.
    - >-
      Quantifier-order attack: phase-1 target indexing is correctly separated,
      but the source/helper bytes are not a complete source-bound target-free
      transcript.
    - >-
      Boundary/strictness attack: the provider and execution boundaries hold as
      refusal gates, but the semantic edge algorithm and matched incumbent do
      not yet exist, so no strict improvement or method comparison follows.
    - >-
      Method-ceiling attack: under ideal future implementation, the present
      contract can support at most a future finite serialization/accounting
      construction; it cannot yet support a verified OneEnd path or advantage.
    - >-
      Nearby-object attack: a continuous but mathematically unrelated provider
      path, an alternate HNF log, a same-owner null arm, or a different synthetic
      state is not yet separated by a complete typed predicate.
    - >-
      Compositional-invariant attack: the declared frame digests and pointer
      checks do not by themselves imply the edge relation, deterministic HNF,
      candidate predicate, or replay identity. Each implication needs its own
      recomputed witness.

  narrowest_supported_statement: >-
    EXP-SSI-bf10ef is a genuine additive SSI-CANONICAL-v11 design successor.
    It improves the v10 contract by aligning the symbolic registry rows,
    separating target-bound phase-1 material from A_p, binding finite unique
    seed derivations, stating a dependency-breaking terminal construction,
    listing typed edge/provider/replay/cost fields, and preserving explicit
    INVALID_CONTROL, INVALID_CERTIFICATE, incumbent, backend, and execution
    gates. Static review does not establish that the successor is universally
    byte-recomputable, source/advice-closed, finite-stream total, semantically
    path-verifiable, cost/memory recomputable, HNF/output deterministic,
    replay-identifiable, control-comparable, or incumbent-comparable. No
    scientific, cryptanalytic, security, exponent, novelty, negative, status,
    or completion conclusion follows.

  next_concrete_action: >-
    Keep the successor review_required, frozen:false, execution_authorized:false,
    evidence_eligible:false, and maximum_runs:0. Treat this as a contract-level
    DISSENT, not a mathematical rejection. Create an additive successor that
    answers RT11-001 through RT11-010, re-snapshot the exact declared paths, and
    obtain fresh independent Validator and Red Team reviews before any freeze,
    control materialization, incumbent comparison, backend probe, or execution
    handoff. Do not edit v10 artifacts, the v11 inputs, ledgers, or queue as a
    repair and do not convert any missing artifact into negative evidence.

  verdict: DISSENT
  review_verdict: DISSENT_ON_V11_BYTE_RECOMPUTABILITY_SEMANTIC_COST_REPLAY_CONTROL_AND_COMPARISON_READINESS
  verdict_scope: >-
    Independent read-only static Red Team review of the exact v11 snapshot
    commit 1f68ed0cd235fec08ee9abe86cd43316cb63b170, the named EXP-SSI-bf10ef
    files, the immutable predecessor v10 review artifacts, and the named
    incumbent gate. No experiment, parser/schema diagnostic, arithmetic check,
    provider request, backend probe, network retrieval, control run, timing,
    memory measurement, scientific observation, status transition, or ledger
    edit was performed.
  execution_authorization: false
  scientific_claim_made: false
  cryptanalytic_claim_made: false
  security_claim_made: false
  exponent_claim_made: false
  novelty_claim_made: false
  hypothesis_transition_made: false
  goal_completion_claim_made: false
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/reviews/TASK-20260809-7161f4/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-b0c877/reviews/TASK-20260809-7161f4/runtime-session-receipt.json
```

## Verdict and evidence boundary

The verdict is **DISSENT on v11 contract closure**, not a rejection of SSI or
of the underlying research direction. V11 is genuine design progress over the
v10 snapshot. In particular, the target-bound index is explicitly phase 1, the
seed list has a finite indexed representation, the terminal dependency is
intended to be acyclic, provider work is excluded until independent semantic
edge replay exists, and missing controls/incumbent data remain admission
blockers.

The dissent is driven by the remaining observation fibers. The subrecord rule
and the digest-bearing subrecords do not agree on whether local digests are
allowed; several digest preimages and the signature message are not named; the
source digest identifiers do not constitute a complete source-bound A_p; and
the builder has no explicit attempt-to-owner emission or total terminal
predicate. The event schedule and primitive table do not account uniquely for
all work, and the buffer rows do not separate advice from work. The HNF rule
contains an ordering/quotient ambiguity, while saturation, output, and replay
fields lack the equations that turn local consistency into the claimed
semantic predicate. Finally, the control manifests and the no-fixed-advice
incumbent are correctly pending but are not yet comparable inputs.

All counterexamples above are proposed static mutations. None was executed.
No parser, arithmetic, cryptographic, network, provider, backend, experiment,
control, timing, memory, or scientific diagnostic was run. Missing inputs and
unclosed gates are blockers, never negative evidence, and the Coordinator alone
may decide the next research-state transition.
