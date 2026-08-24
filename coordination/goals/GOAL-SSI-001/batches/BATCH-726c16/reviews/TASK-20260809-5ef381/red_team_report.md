# Red-team report — `TASK-20260809-5ef381`

```yaml
red_team_report:
  id: RT-20260809-5ef381
  task_id: TASK-20260809-5ef381
  goal_id: GOAL-SSI-001
  batch_id: BATCH-726c16
  role: red-team
  claim_under_review: >-
    Whether EXP-SSI-16649 (SSI-CANONICAL-v8) is a single, byte-recomputable,
    physically charged design contract for the fixed-advice OneEnd frontier,
    including helper/index payloads, finite builder terminals, FOE and memory
    accounting, certificate/HNF/output production, replay/null/C-pair controls,
    synthetic rational aggregation, and the pending incumbent gate. This review
    makes no cryptanalytic, security, exponent, novelty, or execution claim.
  reviewed_snapshot:
    requested_commit: c19deb2202ad26f2f2198a77e0f83f841541bf59
    requested_commit_status: unavailable_in_this_worktree
    reviewed_commit: c19deb2206d548b2192cfe33d67ba56559f48d37
    reviewed_commit_status: >-
      Unique reachable commit whose message and tree contain the named
      BATCH-726c16 / EXP-SSI-16649 SSI v8 snapshot. It is not the requested
      object id; the discrepancy is recorded as an infrastructure/provenance
      blocker, not silently normalized.
    snapshot_parent: 6791c10eb92c3610ffe610e902f52a26ca74b44e
    queue_binding_head: b20401a241406224cd099ab68c73f7f54f207690
    evidence_boundary: >-
      Substantive design inspection used the reachable SSI v8 snapshot above,
      its pending INCUMBENT-FOE-v1 artifact, the BATCH-726c16 manifest/queue and
      snapshot receipt, EXP-SSI-e29417, and the declared BATCH-5a886c review
      inputs. No working-tree-only producer or ledger artifact was used as
      research evidence.
  verdict: DISSENT
  review_verdict: DISSENT_ON_BYTE_RECOMPUTABILITY_FREEZE_AND_EXECUTION_READINESS
  verdict_scope: >-
    Dissent from freeze, arithmetic-row production, break-even comparison, or
    execution readiness. Concur with the narrow design-only claim, the explicit
    no-execution state, and the deliberate pending incumbent gate. The findings
    below are static contract/provenance findings, not observations against an
    ECDLP or isogeny hypothesis.
  objections:
    - severity: infrastructure_blocking
      area: snapshot_identity
      finding: >-
        The exact requested commit c19deb2202ad26f2f2198a77e0f83f841541bf59 is
        absent from the local object database and no ref resolves it. The
        reachable matching snapshot is c19deb2206d548b2192cfe33d67ba56559f48d37,
        whose snapshot receipt still has commit_sha:null and
        verification.status:pending_post_commit. The review can therefore be
        retained only as a provisional review of the uniquely matching snapshot
        until the Coordinator resolves the hash binding.
      references:
        - c19deb2206d548b2192cfe33d67ba56559f48d37
        - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/archives/TASK-20260809-754c17/snapshot-receipt.json:8-20
        - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/batch_manifest.json:8-15
      falsification_route: >-
        Supply the exact requested commit object and show that its tree and
        parent match the reviewed snapshot. Until then, do not treat the two
        object ids as interchangeable archive identifiers.
      classification: infrastructure_provenance_not_research_evidence

    - severity: execution_blocking
      area: c_helper_slot_width_and_payload
      finding: >-
        C-HELPER-v3 declares a 96-byte occupied slot, but its own occupied
        record requires 1 + 32 + 70 + 70 + 70 + 70 + 32 + 32 = 377 bytes under
        the canonical encodings. The 64-byte payload width is not a factor
        payload: the record contains only a 32-byte middle_factor_digest and
        32 zero reserved bytes. Thus a query cannot decode the middle-factor
        list needed by HNF/saturation from the only helper bytes it is allowed
        to consume. The digest covers slots, but no factor-list digest preimage
        or factor-list bytes are bound.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:109-120
        - experiments/EXP-SSI-16649/specification.yaml:178-215
        - experiments/EXP-SSI-16649/specification.yaml:301-329
      falsification_route: >-
        Use the smallest occupied helper, A_C=1. Serializing one occupied slot
        according to the declared field inventory already exceeds slot_width;
        independently, hold the slot bytes fixed and vary the absent factor
        list. The query has no canonical bytes from which to choose the list or
        derive its matrix.
      classification: design_contract_not_research_evidence

    - severity: execution_blocking
      area: helper_capacity_bound
      finding: >-
        next_power_of_two(2*A_C) is not totalized by max_capacity=2^32-1.
        A_C=0 has no specified next power of two, and A_C=2^30+1 requires
        capacity 2^32, which exceeds the declared maximum. No admissible owner
        bound A_C<=2^30 or overflow/terminal precedence is stated.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:122-133
        - experiments/EXP-SSI-16649/specification.yaml:186-214
      falsification_route: >-
        Instantiate the capacity rule at A_C=0 and A_C=2^30+1. A conforming
        builder must either emit two different invalid representations or
        invent an unstated clamp, so helper capacity and digest bytes are not
        uniquely determined.
      classification: design_contract_not_research_evidence

    - severity: execution_blocking
      area: canonical_frame_precedence
      finding: >-
        The v8 lineage rule correctly says historical clauses are not inherited,
        but v8 still has an internal wire ambiguity. The universal frame is
        tag||version||payload_len||payload, while the manifest, helper, order,
        query-index, builder, matrix, output, and certificate layouts give local
        byte equations that omit payload_len. No v8 rule says whether the local
        equation is the complete payload or the complete object with the
        universal length inserted. The two choices yield different bytes and
        different digest preimages. In addition, HNF-RIGHT-ROW-v2 and
        SSJ-MANIFEST-v1 are named sub-contracts without their complete v8 wire
        definitions; the name is an external dependency, not a closed active
        namespace.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:41-55
        - experiments/EXP-SSI-16649/specification.yaml:84-121
        - experiments/EXP-SSI-16649/specification.yaml:164-175
        - experiments/EXP-SSI-16649/specification.yaml:301-350
      falsification_route: >-
        Encode one manifest or helper using the local equation and once using
        the universal frame. Both interpretations satisfy text in the same
        record, but header/body lengths and SHA256 inputs differ. A field-by-
        field supersession table is not enough; the active v8 grammar must pick
        one complete object encoding.
      classification: design_contract_not_research_evidence

    - severity: execution_blocking
      area: fixed_advice_quantifier
      finding: >-
        The scope states forall p exists fixed A_p forall E and forbids
        per-query advice regeneration, but the actual builder request contains
        a fresh request_id, seed, and requested_owner_count and only says it is
        immutable after hashing. There is no binding that the request seed is
        selected before E, is fixed per p, or equals the ORDER-MANIFEST seed.
        Query-generation seeds also contain an instance counter. A conforming
        implementation can therefore generate a target-dependent owner set
        while satisfying the request and manifest prose.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:57-76
        - experiments/EXP-SSI-16649/specification.yaml:216-234
        - experiments/EXP-SSI-16649/specification.yaml:266-299
        - experiments/EXP-SSI-16649/specification.yaml:454-458
      falsification_route: >-
        For fixed p choose two targets E0,E1, derive the builder seed from the
        target/instance, and emit two owner manifests. Unless the request is
        rejected because its seed was not precommitted in A_p, the stated
        universal quantifier is not enforced by the bytes.
      classification: quantifier_contract_not_research_evidence

    - severity: execution_blocking
      area: query_index_binding
      finding: >-
        The target-selection index charges a target/selection expansion, but it
        has no target-manifest digest, no exact record-width/header definition,
        no payload bytes beyond payload_digest, and no mapping from selection
        codes 0..3 to the branch/path semantics. The query-key generation uses
        target_curve_id, but the record does not retain it and the index digest
        does not bind the SSJ manifest digest. The named index therefore does
        not uniquely bind a target set, branch, or helper payload.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:164-176
        - experiments/EXP-SSI-16649/specification.yaml:235-259
        - experiments/EXP-SSI-16649/specification.yaml:403-408
      falsification_route: >-
        Keep target_count and owner_set_digest fixed while substituting a
        different target manifest or selection-to-branch map. The stated index
        fields do not force rejection because neither the manifest digest nor a
        branch map is in the index record/preimage.
      classification: design_contract_not_research_evidence

    - severity: execution_blocking
      area: biguint_and_signed_integer_coverage
      finding: >-
        The 70-byte bound is stated globally, but the contract is not
        byte-recomputable for signed matrix entries, HNF intermediates, factor
        lists/multiplicities, witnesses, or rational cells. signed_integers uses
        a minimally encoded magnitude while biguint uses a fixed 70-byte
        magnitude; MATRIX-v3 and OUTPUT-v3 do not give length-delimited record
        grammars for their signed-bigint sequences. Factor-list length prefixes,
        multiplicity fields, witness-record fields, and the output digest
        preimage are absent. Intermediate HNF values have no declared bound
        beyond eventual invalid_overflow.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:99-144
        - experiments/EXP-SSI-16649/specification.yaml:301-329
        - experiments/EXP-SSI-16649/specification.yaml:448-453
      falsification_route: >-
        Serialize two matrix rows with the same signed values but different
        minimal/fixed magnitude conventions, or two witness lists with adjacent
        values and no per-record length. Both parse under some text in v8, so a
        digest and HNF trace cannot be uniquely reconstructed.
      classification: design_contract_not_research_evidence

    - severity: execution_blocking
      area: finite_builder_terminals
      finding: >-
        The builder simultaneously requires one fixed-width record for every
        requested owner position, forbids partial rows, and permits
        CAP_EXHAUSTED, INVALID_RECORD, OVERFLOW, and infrastructure terminals.
        It does not define the record width, a finite maximum for
        requested_owner_count, how un-emitted positions are represented, or
        precedence when cap/invalid/overflow conditions coincide. The terminal
        frame also lacks request_id, seed/request digest, and requested-owner
        count, so its stream digest is not by itself a replay identity.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:122-133
        - experiments/EXP-SSI-16649/specification.yaml:266-299
        - experiments/EXP-SSI-16649/specification.yaml:460-470
      falsification_route: >-
        Submit a request with requested_owner_count greater than the allowed
        event/payload capacity, or make the first candidate both malformed and
        cap-exhausting. The contract has no unique terminal byte stream that
        satisfies both the all-positions and no-partial-row clauses.
      classification: finite_contract_not_research_evidence

    - severity: execution_blocking
      area: setup_access_memory_and_foe
      finding: >-
        Setup and access are named, but their accounting is not closed. The
        setup/query event lists are categories rather than a mapping from every
        helper, index, certificate, HNF, terminal, digest, source, and byte-read
        operation to an event_code and operation count. A 32-byte hash event is
        named without defining the cost of hashing arbitrary-length bodies.
        memory uses undefined header_bytes and a promised live-range table, and
        omits explicit provider receipts, generator/HNF source bytes, manifest
        construction temporaries, and certificate-field maxima. The statement
        that source files are not free conflicts with the closed M_advice list.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:122-133
        - experiments/EXP-SSI-16649/specification.yaml:260-264
        - experiments/EXP-SSI-16649/specification.yaml:388-408
        - experiments/EXP-SSI-16649/specification.yaml:331-351
      falsification_route: >-
        Produce two traces with the same named setup/query events but different
        counts of bytes hashed, terminal bytes, or source-buffer residency.
        Since no event payload table or live-range equation selects one count,
        both can report different FOE or memory while claiming conformance.
      classification: cost_contract_not_research_evidence

    - severity: execution_blocking
      area: foe_double_counting_and_success_semantics
      finding: >-
        query_cost defines W as the complete FOE event sum and T_q(E)=E[W]/q,
        while attempt_sum includes setup-access reads and T_setup is separately
        charged once per fixed A_p. T_q_run is then described as one attempt
        before inverse success probability, and break-even adds T_setup+Q*T_q_run.
        The contract never states whether W/T_q_run is query-only or includes
        setup. The same setup can consequently be charged once or once per
        attempted success. It also does not define the omega distribution,
        restart behavior after terminal/infrastructure outcomes, or the exact
        cap-conditioned expectation needed for E[W]/q.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:71-77
        - experiments/EXP-SSI-16649/specification.yaml:388-419
        - experiments/EXP-SSI-16649/specification.yaml:460-470
      falsification_route: >-
        Compare a one-time setup trace followed by Q queries with Q full traces
        each containing setup events. Both follow the prose definitions but
        produce different Q_break_even. A terminal or unavailable certificate
        further changes whether another attempt exists, with no declared rule.
      classification: cost_contract_not_research_evidence

    - severity: execution_blocking
      area: certificate_provider_mirror_boundary
      finding: >-
        EDGE-CERT-v3 requires provider_id, provider_receipt, mirror_path,
        mirror_sha256, and edge_stream, but provider_receipt has no grammar,
        signature/identity binding, source commitment, or relation to the
        mirror. mirror_path is only a path string; the contract does not say
        whether mirror_sha256 hashes the complete file or exactly edge_stream,
        nor require path_bytes=len(edge_stream). Transition digests have no
        preimage, and the certificate has no target/branch/start identity, so a
        certificate can be reused across query contexts unless an unstated
        external binding is assumed. Provider absence is correctly classified
        as infrastructure unavailability, but provider success is not defined
        strongly enough to establish certificate provenance.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:331-351
        - experiments/EXP-SSI-16649/specification.yaml:454-458
      falsification_route: >-
        Keep one edge_stream and mirror bytes fixed while changing provider
        receipt/path metadata, or reuse the same certificate for two target
        indices. The declared certificate digest can change without changing
        the transition semantics, and no target-binding field forces rejection.
      classification: availability_and_provenance_contract_not_research_evidence

    - severity: execution_blocking
      area: hnf_and_output_path
      finding: >-
        The positive path is asserted but not algorithmically closed. HNF-RIGHT-
        ROW-v2 is described as applying specified operations, although those
        operations, pivot/remainder rules, factor-to-matrix mapping, saturation
        procedure, intermediate bounds, and source bytes are not defined here.
        OUTPUT-v3 has no output-digest preimage, witness-record grammar, or
        enumerated branch/scalar classes. Consequently scalar/non-scalar status
        can be supplied as an under-specified label, and an implementation can
        bypass the intended transformation without violating a machine-checkable
        field rule.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:216-234
        - experiments/EXP-SSI-16649/specification.yaml:301-329
      falsification_route: >-
        Hold the helper slot, matrix bytes, and claimed HNF log fixed while
        changing the unnamed row-operation implementation or scalar_class. The
        v8 bytes do not contain enough algorithm/digest-preimage information to
        determine which output is admissible.
      classification: proof_and_output_contract_not_research_evidence

    - severity: execution_blocking
      area: replay_and_null_identity
      finding: >-
        Paired replay says the full event stream is identical and only a final
        identity bit is masked, but no identity-bit field, mask transform,
        separate post-gate record, or output-digest interaction is defined.
        branch_null similarly names an owner-specific null path without binding
        a distinct owner, certificate, factor payload, or path generator. With
        the helper payload absent and the output digest preimage absent, a
        label-only null can pass the prose while testing no nearby mathematical
        object. The query seed contains experiment/replicate/instance/attempt
        but not a declared branch or target field, and instance is not defined.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:320-329
        - experiments/EXP-SSI-16649/specification.yaml:433-458
      falsification_route: >-
        Replace only the final scalar/identity label and retain every preceding
        byte. If this is accepted as branch_null, the control cannot detect a
        hidden output classifier or target-independent helper/path artifact.
        Conversely, if output_digest changes, the promised pre-gate identity is
        not byte-identical because its digest preimage is unspecified.
      classification: control_contract_not_research_evidence

    - severity: execution_blocking
      area: c_pair_reference
      finding: >-
        The C-pair control refers to a declared finite null-replicate table with
        seed, replicate count, censoring rule, and digest, but no table path,
        bytes, descriptor grammar, endpoint/pair universe, duplicate policy,
        selection-code mapping, or finite reference values are present in the
        snapshot. The prose forbids iid substitution without defining the
        dependent law that replaces it. This is not a replayable control yet.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:235-259
        - experiments/EXP-SSI-16649/specification.yaml:433-447
        - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/batch_manifest.json:4-15
      falsification_route: >-
        Ask two conforming executors to materialize the finite C-pair reference
        from the current v8 text. They can choose different seed lists,
        replicate counts, or dependence structures while satisfying every
        sentence currently present.
      classification: control_contract_not_research_evidence

    - severity: execution_blocking_for_synthetic_control
      area: synthetic_rational_aggregation
      finding: >-
        Synthetic cells name exact rational fields and a maximum-over-targets
        rule, but do not define the cell wire grammar, target-set identity
        digest, graph/target/start generator, numerator/denominator bounds,
        denominator nonzero rule, reduction/canonicalization, or aggregation
        when one target row is censored. Saying that partial rows are censored
        but cannot be silently dropped does not determine whether a cell is
        invalid, censored, or computed over complete rows only.
      references:
        - experiments/EXP-SSI-16649/specification.yaml:134-144
        - experiments/EXP-SSI-16649/specification.yaml:448-453
        - experiments/EXP-SSI-16649/specification.yaml:479-491
      falsification_route: >-
        Give two target rows with the same complete rows but censor one target
        at the horizon. One executor can return a censored cell and another can
        take the maximum of complete rows; both follow the prose. Likewise,
        unreduced and reduced equivalent rationals have no canonical byte rule.
      classification: synthetic_control_contract_not_research_evidence

    - severity: provenance_and_memory_blocking
      area: incumbent_gate
      finding: >-
        The incumbent gate is correctly conservative: INCUMBENT-FOE-v1 is
        pending_external_measurement, has null FOE/memory/source fields, and
        explicitly disallows comparison or freeze. Therefore no numeric
        incumbent, break-even, or improvement row is admissible. The remaining
        issue is not a false result but that the single artifact-level source
        block does not yet carry per-parameter source bytes/receipts for both
        rows; any later measurement must be an additive, independently archived
        replacement and not an edit to this pending input.
      references:
        - experiments/EXP-SSI-16649/inputs/INCUMBENT-FOE-v1.yaml:1-45
        - experiments/EXP-SSI-16649/specification.yaml:409-431
      falsification_route: >-
        Supply exact, scope-matched SQISign-I and SQISign-V integer FOE and peak
        memory values with source command/commit/digest and independent receipt.
        Until then, any positive comparison is invalid_accounting rather than
        evidence of failure or gain.
      classification: design_gate_and_provenance_not_research_evidence

  required_controls:
    - >-
      Create an additive successor with a physically feasible C-HELPER slot:
      choose actual integer widths, serialize the complete factor list and
      multiplicities, bind its digest preimage, define A_C=0 and capacity
      overflow, and make the helper memory/lookup equations use that same body.
    - >-
      Replace the universal-frame/local-layout ambiguity with one complete
      grammar. Define payload_len placement for every object and all digest
      preimages, including factor, query-payload, transition, output, terminal,
      stream, and trace digests.
    - >-
      Bind one fixed A_p artifact per prime, including owner-set digest, seed,
      constructor source/commit, and target-manifest digest, and reject any
      builder request whose seed or owner set is chosen after E.
    - >-
      Add field-by-field signed-integer, factor/multiplicity, matrix, HNF,
      witness, branch/scalar/reason-code, and record-width grammars with all
      maxima and overflow behavior.
    - >-
      Define finite-builder record width, request binding, full/partial-stream
      terminal semantics, terminal precedence, and a unique identity for every
      terminal and null record.
    - >-
      Publish one event-code/phase/payload table and exact operation-count units;
      decide whether W and T_q_run are query-only or include setup, then make
      setup, access, terminal, source, hash, certificate, HNF, and output costs
      appear exactly once in the break-even equation.
    - >-
      Supply a closed memory live-range table and byte maxima covering all
      headers, source/provider/receipt bytes, mirrors, trace buffers, setup
      temporaries, output buffers, and index/helper products.
    - >-
      Define provider receipt authenticity and source scope, bind certificate
      bytes to target/branch/start identity, require exact mirror-content
      equality, and separate malformed proof from provider/mirror unavailability.
    - >-
      Define the actual HNF row operations, factor-to-matrix composition,
      saturation, scalar predicate, output digest preimage, and sole positive
      output grammar so HNF/output bypass is machine-detectable.
    - >-
      Define paired replay/null as separate typed records with an exact pre-gate
      trace, final-gate mask, continuation rule, branch/target seed binding,
      and owner-specific null certificate/path construction.
    - >-
      Commit one finite C-pair null-reference artifact with its seed list,
      replicate count, endpoint/pair universe, duplicate rule, descriptor and
      helper access, dependence law, censoring, and digest before any run.
    - >-
      Commit synthetic cell bytes and exact rational aggregation, including
      target-set identity, graph/start generation, reduced fraction grammar,
      denominator rules, horizon censoring, and max-over-targets behavior.
    - >-
      Resolve the requested-vs-reachable snapshot commit discrepancy and
      self-bind the snapshot receipt additively. Keep the incumbent measurement
      pending and execution unauthorized until both independent reviews and the
      independently verified incumbent source are archived.
  counterexample_or_mutation: >-
    The cheapest decisive static mutation is an A_C=1 helper. The declared
    occupied slot cannot fit in 96 bytes, and it contains no middle-factor bytes
    for the downstream HNF path. Independent mutations are: A_C=0 or
    A_C=2^30+1 for capacity; adding/removing universal payload_len for a
    manifest digest; choosing builder seed after target selection; reusing one
    certificate for two target indices; changing only scalar_class for the null;
    and censoring one target in a synthetic rational cell. These are contract
    ambiguities, not executed experiments.
  baseline_comparison:
    status: blocked_by_bound_pending_incumbent_and_unclosed_cost_path
    result: >-
      No Pollard-rho/BSGS/specialized-incumbent comparison is admissible from
      this snapshot. INCUMBENT-FOE-v1 has null exact values and explicitly sets
      comparison_allowed:false; the p^(1/3+o(1)) label is not a FOE or memory
      row. The candidate helper/output path and T_q_run are also not uniquely
      defined. This review therefore makes no claim that the proposed route is
      faster, slower, secure, or cryptanalytically useful.
  heuristic_challenges:
    - >-
      No heuristic result is present. The fixed-advice quantifier and the
      distribution of attempt randomness omega are not operationally bound,
      so a future q(E) measurement would need a declared sample space and
      pre-target advice artifact before it could be interpreted.
    - >-
      Finite vertex enumeration and HNF/factor generation are specified as
      named procedures, not as independently bound source/algorithm records;
      no random-model or scale claim can be inferred from them.
  cost_model_challenges:
    - >-
      The 377-byte-versus-96-byte slot contradiction invalidates helper memory,
      probe, payload, HNF, and every downstream FOE row before constants are
      considered.
    - >-
      Setup/access, hash-length, terminal, certificate, source-read, and
      live-memory accounting are not a unique functional; T_setup can be
      double-counted in T_q_run and E[W]/q lacks cap/restart semantics.
    - >-
      No exact incumbent or Q_break_even can be computed; a timeout,
      unavailable provider, malformed contract, or absent baseline must remain
      an infrastructure/design condition rather than negative evidence.
  reduction_and_scope_challenges:
    - >-
      The scope ceiling is appropriately narrow and excludes deployed
      security, SIDH/SIKE torsion-image recovery, all-advice lower bounds, and
      exponent claims. No reduction to SQIsign, CSIDH, EndRing, Isogeny, or a
      cryptographic security level is supported by this snapshot.
    - >-
      The certificate and output contracts do not yet bind a complete
      OneEnd/EndRing witness path, so even a future finite row would require a
      separate exact scope check before any scheme-level interpretation.
  proof_architecture_challenges:
    - >-
      The fixed-advice quantifier is stated but not enforced by the builder
      interface; this is a quantifier-order failure route.
    - >-
      The observation-fiber attack succeeds at the representation level: the
      same declared helper bytes can stand for different absent factor lists,
      and the same terminal/trace identity can be detached from different
      requests or target contexts.
    - >-
      The method ceiling is below the headline byte-recomputable contract: the
      helper cannot encode its payload and the HNF/output method is only named.
      No amount of finite arithmetic can establish a cost comparison until
      those structural ceilings are repaired.
    - >-
      Nearby-object/null controls are label-level or under-specified rather
      than complete owner/certificate/path mutations; they do not yet separate
      a mathematical signal from a classifier or provenance artifact.
  narrowest_supported_statement: >-
    At the reachable matching snapshot c19deb2206d..., EXP-SSI-16649 is an
    additive, design-only SSI v8 record that correctly withholds execution,
    evidence eligibility, freeze, and incumbent comparison. It is not yet a
    single byte-recomputable or physically cost-closed contract: the helper
    slot/payload contradiction alone blocks readiness, with additional
    unresolved precedence, quantifier, terminal, accounting, certificate,
    HNF/output, replay/null, C-pair, synthetic, and provenance defects. No
    scientific or cryptanalytic conclusion follows.
  next_concrete_action: >-
    The Coordinator should retain this DISSENT and create an additive successor
    that repairs the listed static contracts, resolves the snapshot object-id
    binding, and obtains the independently archived incumbent measurement.
    Re-snapshot and repeat independent review only after those repairs. Do not
    execute EXP-SSI-16649, promote a hypothesis, compute break-even, or change
    official status from this report.
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/reviews/TASK-20260809-5ef381/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-726c16/reviews/TASK-20260809-5ef381/runtime-session-receipt.json
```

## Verdict and evidence boundary

The explicit verdict is **DISSENT on byte-recomputability, freeze, arithmetic-row, and execution readiness**. I **CONCUR** only with the experiment’s narrow design-only ceiling, its `frozen: false`, `execution_authorized: false`, and `evidence_eligible: false` state, and its refusal to fabricate an incumbent baseline.

The most decisive static falsification is the C-helper slot: the declared 96-byte slot cannot encode the fields that v8 itself declares as four 70-byte integers plus the key, digest, occupancy byte, and reserved bytes. Even if that width were repaired, the only purported payload is a digest and 32 zero bytes, so the HNF/output path has no factor bytes to consume. This is a design contradiction, not a failed experiment.

The FOE and memory model is also not closed. `T_attempt` includes setup-access reads while `T_setup` is separately added to break-even, and no rule identifies whether `W`/`T_q_run` includes setup. Event categories do not define payloads or operation-count units, and the memory equations defer exact headers/live ranges while claiming source bytes are charged. Any resulting arithmetic row would be non-reproducible.

The incumbent artifact is properly conservative, not defective in the sense of fabricating evidence: it is explicitly `pending_external_measurement`, all values are null, and comparison/freeze are disallowed. That means the correct current conclusion is “no admissible comparison,” not “the candidate loses.”

## Design/infrastructure conditions versus research evidence

Design and infrastructure conditions identified here are the missing requested commit object, pending snapshot self-binding, helper-layout impossibility, unresolved framing and field grammars, advice-seed quantifier gap, terminal and FOE ambiguity, missing provider/certificate semantics, incomplete HNF/output method, and unmaterialized C-pair/synthetic controls. They must be repaired as additive records and reviewed again.

There is no research evidence in this review. No experiment, diagnostic, cryptographic computation, synthetic measurement, baseline measurement, security evaluation, or hypothesis/status transition was performed or inferred. The report does not claim an ECDLP result, a OneEnd result, a SQIsign/CSIDH/SIDH/SIKE security result, a lower bound, an exponent change, or a negative result against the proposed mechanism.
