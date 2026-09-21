# Red-team report — `TASK-20260809-467402`

```yaml
red_team_report:
  id: RT-20260809-467402
  task_id: TASK-20260809-467402
  goal_id: GOAL-SSI-001
  batch_id: BATCH-1ab3b0
  role: red-team
  independent_session: true
  claim_under_review: >-
    Whether the exact SSI-CANONICAL-v9 design in EXP-SSI-9d821a is a single,
    byte-recomputable, physically charged contract for the fixed-advice
    classical OneEnd frontier, including the helper/index/builder path,
    terminal and FOE rules, memory accounting, certificate/provider/HNF/output
    path, paired replay/null identity, finite C-pair and synthetic controls,
    and incumbent admission. This review makes no execution, observation,
    attack, security, exponent, novelty, hypothesis-transition, or completion
    claim.
  reviewed_snapshot:
    requested_commit: 2adffc5faff11904a1fb4a6450a56ffa555b5335
    requested_commit_status: resolved_exactly
    snapshot_parent: e227a49ae56319f1e8c83949d99ef48d937ac167
    experiment_path: experiments/EXP-SSI-9d821a/
    producer_report: coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml
    producer_audit: coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/duplication_knowledge_audit.md
    v8_review_context:
      - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/reviews/TASK-20260809-5ef381/red_team_report.md
      - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/reviews/TASK-20260809-d2b66e/validation_report.yaml
      - ledger/decisions/DEC-20260809-f5eca6.yaml
      - ledger/evidence/EV-SSI-a5f9a7.yaml
    snapshot_receipt_status: >-
      The exact commit is resolvable and was the review boundary. Its immutable
      snapshot receipt still records commit_sha:null and
      verification.status:pending_post_commit. That is an archival provenance
      caveat, not a reason to substitute another commit and not scientific
      evidence.
  objections:
    - id: RT9-001
      category: universal_framing_and_digest_preimages
      severity: freeze_blocking
      finding: >-
        The universal outer-frame rule is a useful v8 repair, but the v9
        contract does not instantiate it for every object or every digest.
        Vertex-manifest hashing appends an undefined body_frames term;
        C-HELPER-v4 commits payload_blob_digest without defining the bytes it
        hashes; restart seeds use a raw tag||version||fields expression rather
        than the declared framed encoding; and the synthetic cell digest is a
        raw concatenation. Several named formats have no numeric tag, byte
        encoding for textual bytestring contents, or complete preimage grammar.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:96-151
        - experiments/EXP-SSI-9d821a/specification.yaml:194-229
        - experiments/EXP-SSI-9d821a/specification.yaml:238-264
        - experiments/EXP-SSI-9d821a/specification.yaml:297-300
        - experiments/EXP-SSI-9d821a/specification.yaml:418-428
        - experiments/EXP-SSI-9d821a/specification.yaml:608-612
      falsification_route: >-
        Ask two conforming serializers to materialize the vertex manifest,
        payload blob digest, restart seed, and synthetic cell digest from the
        stated text. Any difference in body-frame inclusion, tag assignment,
        payload-length inclusion, or bytestring encoding demonstrates that the
        claimed canonical bytes are not determined by the snapshot.
      exact_repair: >-
        Add a sole tag/version registry and a complete frame grammar for every
        named object. Define the exact bytestring encoding and length for every
        textual/source/path field; define each digest preimage as an ordered
        list of complete frames; give payload_blob_digest and all trace,
        identity, cell, and stream digests explicit framed preimages; and
        reject any raw concatenation that is not a declared frame.
      classification: design_contract_not_research_evidence

    - id: RT9-002
      category: fixed_advice_quantifier
      severity: freeze_blocking
      finding: >-
        The scoped formula forall p exists fixed A_p forall E is stated, and
        ADVICE-COMMIT-v4 excludes explicit target fields, but the operational
        witness for A_p is incomplete. The owner generator source/algorithm is
        represented only by ids/digests and an undefined fixed generator
        digest; the role-resolution function is only called deterministic; and
        target_manifest_digest is used throughout v9 without a separately
        defined target-manifest object or an explicit equality to the vertex
        manifest. A digest commitment alone does not show that every owner,
        endpoint, helper, and index byte was generated before E was read.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:72-95
        - experiments/EXP-SSI-9d821a/specification.yaml:244-256
        - experiments/EXP-SSI-9d821a/specification.yaml:257-265
        - experiments/EXP-SSI-9d821a/specification.yaml:325-332
        - experiments/EXP-SSI-9d821a/specification.yaml:353-360
        - experiments/EXP-SSI-9d821a/specification.yaml:362-368
        - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml:20-31
      falsification_route: >-
        Hold p and advice_seed fixed while supplying two implementations with
        different owner-generator source bytes or different deterministic role
        maps, or let target_manifest_digest denote either the full vertex list
        or a target-specific subset. Both choices satisfy the prose while
        yielding different A_p/query wiring. A pre-target transcript and
        source-bound replay would expose the ambiguity.
      exact_repair: >-
        Bind canonical generator source bytes, algorithm version, source commit,
        and source digest into the advice receipt; define the owner-set and
        role-resolution functions byte-for-byte; define target_manifest as a
        concrete object or explicitly equate it to vertex_manifest; and require
        a pre-target advice artifact whose input transcript contains no E,
        instance, attempt, or selection field. Report the target-wise q(E)
        scope separately from the fixed-advice construction.
      classification: quantifier_order_not_research_evidence

    - id: RT9-003
      category: helper_payload_binding
      severity: execution_blocking
      finding: >-
        The v9 96-byte metadata slot repairs the v8 arithmetic impossibility,
        but it does not close the semantic interface. The slot repeats
        owner_index and endpoint_index that also occur in HELPER-PAYLOAD-v4,
        yet no equality check is specified. payload_blob_digest has no
        preimage rule, payload_flags have no domain, factor signs/multiplicity
        and the relation middle_degree = product(factors) are not constrained,
        and the matrix bytes are not tied to the endpoint or factor list.
        Range digests prove byte integrity of a selected range, not that the
        range is the intended helper for the slot's pair key.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:267-320
        - experiments/EXP-SSI-9d821a/specification.yaml:430-451
        - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml:21-27
      falsification_route: >-
        Construct a structurally framed occupied slot whose pair_key and range
        digest point to a valid payload, but whose repeated owner/endpoint
        fields, factor list, and matrix describe a different semantic edge.
        Recomputing all declared local digests leaves no stated cross-field
        rejection. This is a static observation-fiber mutation; it was not
        executed.
      exact_repair: >-
        Define payload_blob_digest, factor ordering/multiplicity/sign domains,
        the degree/factor equation, matrix construction, and a verifier rule
        equating slot, endpoint-record, payload, and pair-key identities.
        Include the source blob identity/base in every pointer-bearing record
        and make helper construction reject any repeated-field mismatch before
        the helper digest is accepted.
      classification: representation_and_method_boundary_not_research_evidence

    - id: RT9-004
      category: target_index_and_pointer_namespace
      severity: execution_blocking
      finding: >-
        TARGET-SELECTION-INDEX-v4 fixes a visible 128-byte record width and
        reuses the C-helper pair-key expression, but its role-to-index function
        is not defined. A record's payload_offset/payload_length/payload_digest
        has no explicit blob namespace or equality rule to the helper slot and
        HELPER-PAYLOAD-v4 range. The index header commits advice and target
        digests but does not independently commit the helper digest, order
        manifest, or the selected owner/endpoint tuple as canonical fields.
        Binary-search order is not semantic wiring.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:321-360
        - experiments/EXP-SSI-9d821a/specification.yaml:194-211
      falsification_route: >-
        Use two valid helper ranges with different endpoint semantics or two
        role maps that produce different owner/endpoint indices. Both can be
        placed behind a 128-byte index record while preserving its local
        lengths and digests because the source namespace and role function are
        not fixed by the text.
      exact_repair: >-
        Define the target-manifest object and role function, add explicit
        helper-frame/order-manifest identity to the index header or query-key
        domain, and require every record to carry and verify a named blob id,
        slot offset/length, pair-key equality, owner/endpoint equality, and
        payload-digest equality. Add mutation cases for each pointer and
        identity field.
      classification: query_wiring_not_research_evidence

    - id: RT9-005
      category: finite_builder_and_terminal_totalization
      severity: freeze_blocking
      finding: >-
        The fixed 4096-byte owner stride and numeric terminal codes are progress,
        but null records are not a grammar of that stride. owner_record defines
        owner_index, endpoint_count, endpoint records, record_digest, and
        padding; null_record additionally introduces record_tag and null_reason,
        says numeric fields are zero, and assigns SHA256(empty) without defining
        how that digest covers the owner-record payload. ZERO_REQUEST is outside
        the terminal precedence table, REPLAY_IDENTITY_FAILURE has no condition,
        and FINITE_OWNER_EXHAUSTED refers to a committed finite owner manifest
        that is not an input object in the request grammar.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:362-428
        - experiments/EXP-SSI-9d821a/specification.yaml:141-144
      falsification_route: >-
        Request one retained owner followed by an early terminal, then compare
        the proposed null stride with the owner_record payload grammar. Also
        present a zero request with an invalid digest and a finite-manifest
        exhaustion at the same position. The text permits different terminal
        bytes and precedence choices.
      exact_repair: >-
        Define NULL-OWNER-RECORD-v4 as its own exact framed 4096-byte grammar,
        including null reason, digest preimage, and padding. Add all terminal
        conditions, including replay failure, to one total precedence relation;
        bind finite-owner exhaustion to a named manifest and request; and
        specify whether malformed request fields are rejected before the
        ZERO_REQUEST rule.
      classification: finite_control_contract_not_research_evidence

    - id: RT9-006
      category: foe_event_mapping_and_byte_charging
      severity: freeze_blocking
      finding: >-
        The primitive table assigns unit FOE values to numeric codes, while
        setup_events and query_events are names with no numeric mapping or
        event population. Codes 1, 2, 3, 8, and 9 charge input_bytes=0 even
        when field, matrix, or transition data are consumed; no exact rule
        derives operation_count from a graph step, certificate read, HNF
        operation, terminal, provider receipt, or replay event. Hash and byte
        events have formulas, but the actual byte ranges and hash inputs are
        not enumerated. The producer's claim of complete event equations is
        therefore not enough to recompute total_foe.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:430-468
        - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml:33-44
      falsification_route: >-
        Encode one graph step that reads a 64-byte transition and one HNF row
        operation over a full matrix. The snapshot provides no unique numeric
        event sequence or operation count, so two traces with different byte
        work can both satisfy the event table. This is an accounting ambiguity,
        not a measured cost difference.
      exact_repair: >-
        Add a numeric event-code/phase table with one row per named event,
        operand byte ranges, operation-count derivation, hash-block rule,
        terminal/provider/certificate/HNF/output costs, and a canonical event
        population for every control-flow branch. Define whether primitive FOE
        units are normalized or calibrated and prohibit an incumbent comparison
        until both sides use the same unit.
      classification: cost_model_not_research_evidence

    - id: RT9-007
      category: restart_probability_and_total_expected_cost
      severity: freeze_blocking
      finding: >-
        q_cap is called the probability that an independently seeded attempt
        succeeds, but the finite attempt distribution is not declared. Seeds
        are deterministic functions of attempt indices, A_MAX is finite, and
        T_q is nevertheless defined as E[W]/q_cap. That identity requires an
        explicit independent-restart law and a stopping model; with a finite
        cap, success-correlated attempt cost, and retained censored traces, the
        expected cost to a successful output is not determined by the stated
        fields. It is also unclear whether q_cap/T_q are per target, worst-case,
        or averaged over a target distribution.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:72-95
        - experiments/EXP-SSI-9d821a/specification.yaml:424-428
        - experiments/EXP-SSI-9d821a/specification.yaml:462-478
      falsification_route: >-
        Consider two attempt laws with the same marginal q_cap and E[W] but
        different correlation between success and W, or a finite A_MAX with no
        successful attempt. The snapshot gives no unique total cost or failure
        probability for those cases.
      exact_repair: >-
        Define the seed sample space and target quantifier, record the joint
        distribution of success and attempt cost, and use a truncated-geometric
        stopping equation with explicit failure probability after A_MAX. If no
        infinite-restart interpretation is intended, report only bounded
        per-attempt/per-run costs and do not publish E[W]/q_cap.
      classification: expected_cost_not_research_evidence

    - id: RT9-008
      category: hidden_memory_and_source_bytes
      severity: execution_blocking
      finding: >-
        The memory table is labelled live_ranges but supplies only phase,
        ordinal, and size; it does not supply allocation and release intervals
        from which overlap can be recomputed. Several exact operands are also
        absent: source_generator_payload_bytes is undefined, helper/index
        headers and outer digests are not represented as separate live buffers,
        provider receipt and mirror-path/source buffers are not bounded as
        objects, and HNF operation-log/factor/scratch buffers are not listed.
        certificate_bytes_max bounds path_bytes, not the complete certificate
        frame. A max of candidate/sort/digest workspace is an assertion of
        non-overlap, not a demonstrated lifetime schedule.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:194-229
        - experiments/EXP-SSI-9d821a/specification.yaml:479-501
        - experiments/EXP-SSI-9d821a/specification.yaml:503-534
      falsification_route: >-
        Retain the source bytes, helper payload, candidate buffer, sort buffer,
        provider receipt, matrix workspace, operation log, and trace while
        serializing one query. The snapshot contains no start/end intervals or
        exact buffer rules that determine whether these objects overlap or are
        charged.
      exact_repair: >-
        Replace ordinal rows with an explicit allocation/lifetime table and
        include every serialized header, digest, source, provider receipt,
        mirror, factor, matrix, HNF, operation-log, trace, and output buffer.
        Define the complete certificate object bound and derive M_advice/M_work
        from the same byte frames used by the verifier.
      classification: resource_accounting_not_research_evidence

    - id: RT9-009
      category: certificate_provider_and_path_binding
      severity: execution_blocking
      finding: >-
        EDGE-CERT-v4 has substantially more fields than v8, but provider
        authenticity is not closed. The outer Ed25519 signature message
        explicitly excludes provider_receipt_frame, so provider_id,
        artifact_digest, and receipt metadata are protected only by an
        internally recomputed receipt_digest, not by a trusted signature. The
        provider public key is carried in the receipt and its digest is carried
        in the certificate, but no external trust anchor pins the key. No rule
        binds artifact_digest to the transition frames, enforces source-to-next
        destination continuity, or proves graph adjacency/final endpoint.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:503-534
        - experiments/EXP-SSI-9d821a/specification.yaml:650-654
      falsification_route: >-
        Change provider_id or artifact_digest and recompute receipt_digest while
        keeping the certificate fields covered by the stated signature message
        unchanged. The stated rules do not force the outer signature to reject
        that provenance mutation. Independently permute transition endpoints
        while preserving frame counts and local hashes; no path-continuity rule
        is supplied.
      exact_repair: >-
        Pin provider identity and public key in a separately archived trusted
        manifest, include the complete canonical provider receipt (or its
        digest plus all identity fields) in the signed message, bind
        artifact/mirror bytes to the same transition-frame digest, and define
        path start, adjacency, endpoint, horizon, and factor/transition
        validity checks.
      classification: certificate_provenance_not_research_evidence

    - id: RT9-010
      category: hnf_saturation_and_output_path
      severity: execution_blocking
      finding: >-
        MATRIX-v4, OP-LOG-v4, SATURATION-v4, and OUTPUT-v4 are framed more
        explicitly than their v8 names, but the positive mathematical path is
        still not algorithmically closed. op_code semantics, pivot/remainder
        rules, factor_index bounds, initial/final digest chaining, factor-to-
        matrix composition, saturation predicate, scalar predicate, and
        witness correctness are not defined. Each operation/saturation digest
        can therefore certify its own bytes without certifying that the bytes
        are the deterministic result of the certificate. scalar_class 0 is a
        label, not a machine-checkable conclusion.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:503-563
        - experiments/EXP-SSI-9d821a/specification.yaml:430-451
      falsification_route: >-
        Hold the framed matrix and certificate fixed, then choose a different
        locally self-digested operation log and scalar_class. Because the
        semantic operation table and digest chain are absent, the text does not
        identify the first mandatory rejection. This is a proof-architecture
        collision, not an executed HNF result.
      exact_repair: >-
        Define every op_code and deterministic row operation, bind the initial
        matrix digest and each next digest, consume certificate factors with
        explicit bounds and equations, chain saturation frames, and define a
        verifiable scalar predicate and witness relation. Make OUTPUT-v4 valid
        only when those checks succeed.
      classification: proof_and_output_contract_not_research_evidence

    - id: RT9-011
      category: paired_replay_and_branch_null_identity
      severity: control_contract_blocking
      finding: >-
        Paired replay says treatment and null share an identical request and
        pre-classification trace, while branch_null says null_owner,
        null_mutation_digest, and branch-map identity are serialized in a
        shared request. Those fields are absent from BUILDER-REQUEST-v4 and
        from the attempt-seed grammar. TRACE-SHARED-v4 and FINAL-IDENTITY-v4
        also have no declared outer tags, target/attempt binding, or exact
        treatment/replay container. The owner mutation itself is only a hash-
        selection rule; its changed certificate, helper payload, or path is not
        defined. The control can therefore collapse to a label-only null or
        permit unequal traces while claiming identity masking.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:362-368
        - experiments/EXP-SSI-9d821a/specification.yaml:565-592
        - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml:45-50
      falsification_route: >-
        Replace only the final identity bit, change only the null owner, and
        then change only the target index. The snapshot does not define which
        resulting bytes must remain equal, which must differ, or which digest
        must reject the mutation. A valid paired control must distinguish these
        three cases before any measurement.
      exact_repair: >-
        Define typed REQUEST, REPLAY, TRACE-SHARED, and FINAL-IDENTITY frames
        containing target, branch, attempt, owner mutation, and advice identity.
        Specify exact shared pre-gate events, continuation after success,
        final-mask semantics, and a concrete owner-specific certificate/path
        mutation. Add mutation controls for identity-bit, target, branch, and
        trace changes.
      classification: control_contract_not_research_evidence

    - id: RT9-012
      category: finite_c_pair_control
      severity: control_contract_blocking
      finding: >-
        C-PAIR-REF-v4 improves v8 by fixing 32 seed indices and a row schema,
        but it remains a design manifest, not a finite reference artifact. No
        row bytes, finite_table_digest field, generator_source_digest, endpoint
        or pair universe, endpoint ordering, dependent reference law, or
        treatment/reference acceptance statistic is present. The row schema
        names endpoint_set_digest and shared_trace_digest without defining their
        source byte sets. measured_rows_present:false and
        independent_verification_receipt:null correctly make the control
        invalid for admission; they do not provide a null result.
      references:
        - experiments/EXP-SSI-9d821a/controls/C-PAIR-REF-v4.yaml:1-43
        - experiments/EXP-SSI-9d821a/specification.yaml:593-604
        - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/tasks/TASK-20260809-0fe8c5/refinement_report.yaml:51-61
      falsification_route: >-
        Have two conforming executors materialize the endpoint/pair universe and
        reference rows. The manifest leaves enough generator and acceptance
        choices that their finite tables need not match while all visible fields
        remain satisfied. No run was performed to resolve this.
      exact_repair: >-
        Commit the exact 32 row frames and finite-table digest, generator source
        bytes/digest, endpoint/pair universe and order, dependence law,
        duplicate/rejection semantics, censoring rule, and a pre-registered
        comparison statistic with its invalid-control threshold. Archive an
        independent replay receipt before any treatment result is interpreted.
      classification: control_manifest_not_research_evidence

    - id: RT9-013
      category: finite_synthetic_control
      severity: control_contract_blocking
      finding: >-
        SYNTHETIC-REF-v4 fixes finite cell and target indices and states a
        maximum over all complete rows, but it does not define the synthetic
        graph/start state, per-target success and attempt generation, initial
        rational values, rational reduction/canonicalization, or a per-target
        row frame. The cell digest is again an unframed concatenation and does
        not include an explicit cell index/list digest. Partial cells are
        invalid, but the required complete cell bytes and acceptance rule are
        absent. This is a control specification, not observed control data.
      references:
        - experiments/EXP-SSI-9d821a/controls/SYNTHETIC-REF-v4.yaml:1-45
        - experiments/EXP-SSI-9d821a/specification.yaml:605-617
      falsification_route: >-
        Supply two cells with the same complete target rows but different
        rational encodings or one censored target row. The text does not define
        a unique canonical fraction or a machine-readable invalid/censored
        aggregation record beyond the prose gate.
      exact_repair: >-
        Define typed cell and target-row frames, graph/start/success generators,
        initial values, reduced positive-rational encoding, cell-index binding,
        denominator and overflow behavior, and the exact invalid/censored/max
        aggregation transition. Materialize all eight cells and archive an
        independent verification receipt.
      classification: control_manifest_not_research_evidence

    - id: RT9-014
      category: incumbent_admission_and_baseline
      severity: admission_blocking_by_design
      finding: >-
        The incumbent gate remains honest and correctly blocks freeze,
        comparison, and break-even: both SQISign rows have null FOE and memory,
        the source fields are null, and comparison_allowed:false. It is not
        evidence that SSI loses. The future baseline is also labelled
        no_fixed_advice while the candidate amortizes fixed advice through
        T_setup+Q*T_q; without a matched Q/advice/setup convention, even a
        later exact FOE row would not by itself be comparable.
      references:
        - experiments/EXP-SSI-16649a/inputs/INCUMBENT-FOE-v1.yaml:1-45
        - experiments/EXP-SSI-9d821a/specification.yaml:222-224
        - experiments/EXP-SSI-9d821a/specification.yaml:474-501
      falsification_route: >-
        Provide exact SQISign-I and SQISign-V source measurements with the
        required command, commit, bytes, generator version, memory, and
        independent receipt, then compare under an explicitly common advice
        and Q accounting. Until that exists, any break-even or improvement row
        is invalid accounting, not a negative scientific result.
      exact_repair: >-
        Add a superseding, independently archived incumbent record with exact
        per-prime FOE/memory and source bytes, then define whether baseline and
        candidate are compared per target, at fixed Q, or under a common
        preprocessing model. Bind the incumbent measurement to the v9 event
        and memory grammar before enabling freeze.
      classification: admission_gate_not_research_evidence

    - id: RT9-015
      category: scope_and_reduction_boundary
      severity: limitation
      finding: >-
        The v9 claim ceiling appropriately excludes all-advice lower bounds,
        deployed security, positive SIDH/SIKE torsion-image claims, and
        transfers to EndRing, Isogeny, SQIsign, or CSIDH. However, the
        certificate/output defects leave no closed reduction from the framed
        bytes to a valid OneEnd endpoint or endomorphism witness. The correct
        scope is therefore the design of an intended finite contract only; no
        baseline comparison, hardness statement, or scheme-level conclusion is
        available.
      references:
        - experiments/EXP-SSI-9d821a/specification.yaml:20-53
        - experiments/EXP-SSI-9d821a/specification.yaml:503-563
        - ledger/decisions/DEC-20260809-f5eca6.yaml:15-20
      falsification_route: >-
        A future implementation would need an exact path-to-output witness and
        a separately reviewed reduction before any OneEnd/EndRing or scheme
        statement could be admitted. No such artifact is in this snapshot.
      exact_repair: >-
        Keep the current claim ceiling, add the complete path/witness reduction
        as a separately reviewed proof contract, and require an independent
        review-breakthrough decision for any later claim that exceeds the
        design-only boundary.
      classification: scope_ceiling_preserved

  required_controls:
    - >-
      Add a canonical frame/tag registry and byte-level digest-preimage table;
      cover all v9 object, source, trace, identity, stream, cell, and table
      digests, including textual encoding and payload lengths.
    - >-
      Bind the fixed-advice generator source and role map, define target-manifest
      identity, and archive a pre-target advice construction receipt.
    - >-
      Add cross-object mutations for helper slot/payload/endpoint/index owner,
      endpoint, pair-key, offset, length, and digest mismatches.
    - >-
      Give null records and all terminal outcomes exact fixed-stride grammars,
      one precedence table, malformed-request ordering, finite exhaustion, and
      stream identity rules.
    - >-
      Supply numeric event-code/phase/population rules, operand byte ranges,
      operation-count equations, and an independent reconciliation of setup,
      attempt, restart, and terminal FOE.
    - >-
      Replace the ordinal memory table with allocation/lifetime intervals and
      include every header, source, provider, mirror, factor, matrix, HNF,
      operation-log, trace, and output buffer.
    - >-
      Pin the provider key, sign the complete receipt identity, bind mirror and
      artifact bytes to the transition stream, and verify path continuity and
      endpoint semantics.
    - >-
      Define deterministic HNF/saturation operations, digest chaining, factor
      consumption, scalar predicate, and witness validity.
    - >-
      Materialize typed paired replay/null frames and finite C-pair/synthetic
      artifacts with exact seeds, rows/cells, digests, acceptance, and
      independent replay receipts.
    - >-
      Supply the matched independent incumbent source measurement and a common
      fixed-advice/Q accounting convention before freeze or comparison.
  counterexample_or_mutation: >-
    No mutation was executed. The cheapest decisive static mutations are:
    (1) make the repeated owner/endpoint fields in a helper payload disagree
    with its slot while recomputing local digests; (2) replace provider_id or
    artifact_digest and recompute only receipt_digest, which the stated outer
    signature message excludes; (3) retain the same matrix and certificate but
    choose another self-digested HNF log/scalar label; (4) change only the
    branch-null owner or target index in paired replay; and (5) vary the
    unmaterialized finite C-pair or synthetic reference table. These are
    contract mutations and observation-fiber tests, not experiments.
  baseline_comparison:
    status: blocked_by_pending_incumbent_and_unclosed_cost_path
    result: >-
      No Pollard-rho, BSGS, or specialized-incumbent comparison is admissible.
      The incumbent has null exact values and comparison_allowed:false, while
      q_cap, T_q, event FOE, memory, certificate cost, and the fixed-advice
      amortization convention are not uniquely defined. This review makes no
      claim that the candidate is faster, slower, secure, or cryptanalytically
      useful.
  heuristic_challenges:
    - >-
      No heuristic result or run is present. The fixed-advice quantifier is a
      declaration whose generator/source and target-manifest witness are not
      bound, and the attempt sample space for q_cap is not specified.
    - >-
      The finite controls are not materialized and there is no distributional
      observation from which a random-model transfer, scale claim, or null
      rejection could be inferred.
  cost_model_challenges:
    - >-
      v9 removes the v8 occupied-slot arithmetic contradiction, but pointer
      namespace, payload digest, event-code, source-byte, provider-byte, and
      live-range semantics still prevent exact FOE/memory recomputation.
    - >-
      The E[W]/q_cap formula lacks a declared restart law and finite-cap
      treatment; setup/index/target scope and baseline advice amortization are
      not aligned.
  reduction_and_scope_challenges:
    - >-
      The design-only claim ceiling is correctly narrow. The certificate and
      output grammar does not yet establish a valid OneEnd endpoint or an
      EndRing/Isogeny witness, so no scheme or security statement follows.
    - >-
      The pending incumbent is an admission condition, not a negative result;
      any future comparison must use exact matched source and Q/preprocessing
      scope.
  proof_architecture_challenges:
    - >-
      Observation-fiber attack: local digests do not imply semantic equality
      among helper, index, certificate, HNF, and output objects.
    - >-
      Quantifier-order attack: target-manifest identity and the source-bound
      owner/role generator are missing from the fixed-advice witness.
    - >-
      Method-ceiling attack: self-consistent frames can be serialized without
      proving that they are the deterministic OneEnd/HNF/output path; the
      contract ceiling therefore stops below byte-recomputable semantics.
    - >-
      Nearby-object attack: paired null, finite C-pair, and synthetic controls
      are not yet concrete objects that distinguish a method signal from a
      classifier, provenance, or reference-construction artifact.
  narrowest_supported_statement: >-
    At the exact commit 2adffc5faff11904a1fb4a6450a56ffa555b5335,
    EXP-SSI-9d821a is an additive design-only v9 successor. It appears to
    remove v8's specific 96-byte occupied-slot versus 377-byte field-layout
    contradiction and it correctly keeps execution_authorized:false,
    evidence_eligible:false, and frozen:false. It is not yet a complete
    byte-recomputable or physically cost-closed contract: universal framing,
    fixed-advice enforcement, helper/index semantics, finite terminals, FOE,
    memory, provider/path authenticity, HNF/output semantics, paired replay,
    C-pair, and synthetic controls retain execution- or freeze-blocking gaps.
    The incumbent is intentionally pending. No scientific, cryptanalytic,
    security, exponent, novelty, negative, or completion conclusion follows.
  next_concrete_action: >-
    Retain this DISSENT and create an additive v10 repair for the listed
    byte-level and semantic interfaces, materialize and independently verify
    the finite controls, obtain the matched incumbent measurement, re-snapshot,
    and repeat independent review. Do not execute EXP-SSI-9d821a, promote a
    hypothesis, compute break-even, or change official status from this report.
  verdict: DISSENT
  review_verdict: DISSENT_ON_V9_BYTE_RECOMPUTABILITY_COST_CLOSURE_AND_EXECUTION_READINESS
  verdict_scope: >-
    Independent read-only static Red Team review of the exact v9 snapshot and
    named v8 context. The verdict is on design readiness and admission only,
    not on the SSI mechanism or any cryptographic hypothesis.
  execution_authorization: false
  scientific_claim_made: false
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/reviews/TASK-20260809-467402/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-1ab3b0/reviews/TASK-20260809-467402/runtime-session-receipt.json
```

## Verdict and evidence boundary

The verdict is **DISSENT on v9 byte-recomputability, semantic path closure,
FOE/memory accounting, control readiness, freeze readiness, and execution
readiness**. I concur with the narrower design-only boundary: the experiment is
explicitly unfrozen, execution-unauthorized, and evidence-ineligible, and the
incumbent gate correctly refuses to fabricate a baseline.

The v8 occupied-slot contradiction is repaired at the layout level: v9 moves
factor and matrix material into a framed payload blob and leaves the 96-byte
slot as metadata. That repair is real design progress, but it does not by
itself bind the repeated identities, index pointers, certificate semantics,
HNF operations, or output predicate. A digest of a frame establishes integrity
of those bytes; it does not establish that the bytes are the intended object or
the result of the intended OneEnd path.

The strongest independent objections are the unbound universal digest grammar,
the missing operational witness for the fixed-advice quantifier, the absent
numeric event schedule and lifetime intervals, the provider signature's
exclusion of its receipt identity, and the replay/null contradiction between
identical requests and branch-specific fields. The C-pair and synthetic files
are honest design manifests with no measurements, so they block admission
rather than support or refute the mechanism.

No experiment, diagnostic, parser/schema check, arithmetic-row generation,
cryptographic computation, baseline measurement, control outcome, or scientific
observation was performed. Existing producer, predecessor, queue, ledger, and
snapshot files were not modified; only the two declared task artifacts were
written.
