# Red-team report — `TASK-20260809-bcd3d9`

```yaml
red_team_report:
  id: RT-20260809-bcd3d9
  task_id: TASK-20260809-bcd3d9
  goal_id: GOAL-SSI-001
  batch_id: BATCH-c057fd
  role: red-team
  reviewed_snapshot:
    commit: d2e1cb4eed78b798682b779db3d86ee17c60d024
    parent: 0d31d0f134ba4c5450892f815f3efc43df6174e4
    worktree_head_at_start: d798e45b716b116b32bd81893f4951fe2af4b806
    evidence_boundary: >-
      All substantive campaign evidence was read from the immutable snapshot
      commit named above with git show. The later worktree HEAD was not used as
      evidence. The snapshot receipt itself remains pending post-commit
      verification and is treated only as an archival provenance caveat.
  claim_under_review: >-
    Whether the additive, design-only EXP-SSI-357363 successor closes the exact
    physical byte equations, SSI-BYTES-v1 grammar, cryptographic-scale counts,
    manifest/setup/index charges, output-producing A/B/C paths, hard restart and
    FOE accounting, paired replay identity, semantic nulls, C-pair calibration,
    and synthetic diagnostic boundary inherited from EXP-SSI-8e589d. This review
    makes no experiment, attack, security, exponent, novelty, hypothesis-status,
    or completion claim.
  verdict: DISSENT
  verdict_scope: >-
    Dissent from freeze and execution readiness as an exact, finite,
    independently reproducible physical contract. Concur that the successor is
    additive and design-only, that the direct predecessor b_order and b_index
    undercounts are repaired in their stated formulas, that the external
    edge-stream boundary and non-SSI diagnostic ceiling are explicit, and that
    execution remains unauthorized.
  objections:
    - id: RT-BCD3D9-HELPER-WIDTHS
      severity: execution_blocking
      finding: >-
        The corrected order-tag width is internally consistent: the scalar
        declaration and b_order now include one sign byte per scalar, giving
        1186 and 2274 bytes. The index header is also included in the stated
        b_index formula. However C-HELPER-v1 is still not physically exact. It
        stores endpoint_curve_id, endpoint_slot, pair_key, and
        middle_factor_code, while helper_entry is only b_curve+b_slot+16 and
        omits the declared uint32 middle-factor field. Its header, occupancy,
        capacity, digest, payload mapping, and helper-specific slot width are
        also absent. Since A_C can exceed S_C, the common pair-table b_slot is
        not automatically wide enough for helper slots. M_order_helper_bytes
        and the C-helper portion of M_total_bytes therefore remain undefined.
      reference: experiments/EXP-SSI-357363/specification.yaml:223-250,286-295,330-345
    - id: RT-BCD3D9-GRAMMAR-SEEDS
      severity: execution_blocking
      finding: >-
        SSI-BYTES-v1 gives useful literal codes and integer conventions but does
        not close the byte grammar. The committed build_seed is not present in
        the builder frame, and the committed query_seed is not present in the
        query seed derivation. The graph protocol names a graph_seed although
        only graph_null_seed is committed. ORDER-GEN-v1, SSJ-ENUM-v1, and the
        manifest generator version have no literal byte schema or digest input.
        The generic frame rule does not enumerate the exact fields, null
        encodings, or length-prefix treatment for every hash and trace event;
        integer(SHAKE256(...)) has no explicit byte interpretation. The 16-byte
        hash_domain in shared_header is not assigned a literal value. Thus the
        same prose still admits multiple seed and hash byte streams.
      reference: experiments/EXP-SSI-357363/specification.yaml:97-117,172-216,223-231,330-340,437-480,560-578
    - id: RT-BCD3D9-SCALE-COUNTS
      severity: execution_blocking
      finding: >-
        The b_count and b_attempt formulas repair stored H and builder-count
        widths, but not all cryptographic-scale counters. The builder explicitly
        uses counter_u64 while its declared cap is 2^20*S_req; at the named
        cryptographic rows that cap can require more than 64 bits. The same
        issue applies to any unbounded advice-index/permutation or
        next-distinct counter, while their frame widths are not specified. A
        biguint uses a uint16 length prefix without a declared bound proving that
        the exact degree product or output intermediate fits 65535 bytes. Trace
        counts such as completed_attempt_count and witness_count have no field
        widths or canonical serialized representation. The contract therefore
        still contains overflow paths at precisely the scale it claims to cover.
      reference: experiments/EXP-SSI-357363/specification.yaml:52-60,109,172-184,188-216,330-338,477-489
    - id: RT-BCD3D9-MANIFEST-SETUP
      severity: execution_blocking
      finding: >-
        Naming T_manifest and T_order_helper does not make setup chargeable. The
        SSJ manifest has no frozen Deuring-polynomial bytes or digest source,
        root multiplicity/normalization rule, exact generator version, or
        manifest-generation trace. ORDER-MANIFEST-v1 and C-HELPER-v1 have no
        complete header/body widths, cardinality binding, sorting algorithm, or
        setup FOE equation. In addition, ORDER-MANIFEST-v1 is described as an
        owner-to-order table but its cardinality and branch ownership are not
        fixed. If it contains orders for all V_p vertices, it is a full external
        order oracle shared by otherwise small advice rows; if it contains only a
        helper subset, that subset is not bound. Either interpretation prevents
        a comparable A/B/C advice frontier until the helper scope and all bytes
        are fixed.
      reference: experiments/EXP-SSI-357363/specification.yaml:92-117,276-290,330-345
    - id: RT-BCD3D9-INDEX-LOOKUP
      severity: execution_blocking
      finding: >-
        The static table layout is more explicit, but its query path is not. A
        retained record's hash_key is derived from the entire branch-specific
        record_bytes, whereas a query starts with target_curve_id and does not
        yet possess an order tag, pair descriptor, or membership payload. No
        target-key hash, equality predicate, or mapping from target ID to the
        selected initial slot is specified. The one-selected-slot cost claim can
        therefore hide a scan, a second index, or an oracle. Failed-build peak
        storage, candidate-byte lengths, and the payload-array construction are
        also asserted as charges without a builder trace or exact equations.
      reference: experiments/EXP-SSI-357363/specification.yaml:232-250,252-302,330-345,374-380
    - id: RT-BCD3D9-HNF-OUTPUT
      severity: execution_blocking
      finding: >-
        HNF-RIGHT-ROW-v1 names a useful canonical predicate, but it does not
        supply the exact pivot/zero-row convention, admissible scalar envelope,
        saturation algorithm, degree-class meaning, or output witness byte
        encoding. b_mag is a width, not a bound proving that every pulled-back
        and saturated output fits it. Output_encode is a unit primitive, and
        M_work_bytes is only a name; output HNF bytes, digest bytes, certificate
        framing, peak intermediate memory, and bigint costs are not charged.
        Construction C stores target and endpoints plus a middle descriptor but
        no endpoint order. Its output path names two edge streams and a
        pullback, without saying where the terminal HNF order comes from or how
        the two paths and middle factor compose. B-membership can appeal to the
        global order helper, but C has no equivalent closed source.
      reference: experiments/EXP-SSI-357363/specification.yaml:223-231,286-295,347-366,374-380
    - id: RT-BCD3D9-EDGE-BOUNDARY
      severity: execution_blocking_for_end_to_end_claims
      finding: >-
        The explicit external EDGE-STREAM-v1 boundary is a surviving scope
        improvement: the record does not pretend to generate an SSI path. It
        also means no end-to-end ECDLP or OneEnd cost is established. The
        certificate source, target/owner binding, degree-class transition map,
        next-step digest field, and path termination certificate are absent. A
        SHA256 digest and digest verification are charged in prose, but the
        digest bytes and certificate header are absent from path_bytes, and
        certificate generation, storage, and availability are outside T_setup
        and T_q. A supplied certificate can consequently be an uncharged
        path oracle unless the Coordinator keeps the claim ceiling exactly at
        conditional accounting with that input already available.
      reference: experiments/EXP-SSI-357363/specification.yaml:347-366,437-480,584-613
    - id: RT-BCD3D9-RESTART-FOE
      severity: execution_blocking
      finding: >-
        T_q remains a symbolic E[W]/q functional, not a finite protocol cost.
        Seeds are deterministic expressions and no probability law for omega or
        independent restart stream is defined, so q is not an instantiable
        per-attempt probability for a fixed target. The formula uses an
        unbounded inverse-success expectation while A_max=32768 is a hard
        terminal cap; the expected cost and failure probability of the capped
        process are not specified. T_manifest, T_order_helper, and
        T_index_build have no primitive counter equations, and the trace has no
        mapping from event_code to byte reads, hash/SHAKE blocks, manifest
        comparisons, table probes, serialization, or output work. T_inc_foe is
        still an external placeholder. Q_break_even has a clear non-strict
        rational inequality, but no defined value can be produced until those
        inputs and capped semantics exist.
      reference: experiments/EXP-SSI-357363/specification.yaml:52-60,154-184,330-345,441-480,584-599
    - id: RT-BCD3D9-REPLAY
      severity: execution_blocking
      finding: >-
        The successor correctly removes the predecessor's alternate replay seed
        and requires a same pre-gate hash. The identity claim is still not
        independently recomputable: event_code literals, optional/null field
        encodings, event-frame serialization, and the bytes hashed by
        pre_gate_trace_sha256 are not frozen; primitive work counters are absent
        from the event schema; and the normalized witness/owner bytes needed to
        recompute the final predicate are absent. Treatment stops after success
        while null gates require 32768 completed attempts, but the paired row and
        completed-attempt scope do not say which attempts are paired in that
        case. A hash field plus aggregate counts is not a complete trace identity
        contract.
      reference: experiments/EXP-SSI-357363/specification.yaml:172-184,437-489,490-555
    - id: RT-BCD3D9-NULL-SHUFFLE
      severity: execution_blocking
      finding: >-
        The next-distinct owner and rejection-based permutation are named but
        not algorithmically serialized: candidate derivation, rejection
        counters, modulo-bias handling, and a concrete permutation algorithm are
        missing. CTRL-SHUFFLED-FIBER is undefined for S_eff=0 because its
        permutation reduces modulo S_eff; its not_applicable condition checks
        only |V_p|<2. Tagged shuffles regenerate a new owner order, which changes
        record bytes, path selection, and possibly FOE, so the stated same-path
        claim is not entailed by the path-rule sentence. Membership shuffles
        change the treatment owner-equals-lookup invariant without declaring the
        corresponding null exception. Owner-mismatch paths also need a fresh
        owner-specific edge certificate, so they cannot be assumed to share the
        treatment path merely because their parser and final gate names match.
      reference: experiments/EXP-SSI-357363/specification.yaml:437-480,506-555
    - id: RT-BCD3D9-C-PAIR
      severity: execution_blocking
      finding: >-
        PAIR-DESCRIPTOR-v1 is required to recompute fields, but its actual
        recomputation algorithm and middle-factor mapping are not supplied.
        Treatment-matched endpoint-pair generation is still only a phrase; the
        null's hard rejection cap has no numeric value or terminal classification.
        The endpoint permutation does not by itself establish an iid pair-key
        law after fixed marginals, endpoint ordering, slot reconstruction, and
        descriptor recomputation. Consequently C_iid and the per-replicate
        collision gates are declared thresholds, not calibrated controls. The
        missing four-byte helper field further prevents C's physical and
        statistical paths from being the same declared table.
      reference: experiments/EXP-SSI-357363/specification.yaml:286-302,535-555,579-582
    - id: RT-BCD3D9-SYNTHETIC
      severity: execution_blocking_for_diagnostic_only
      finding: >-
        The non-SSI boundary is explicit and survives: G_N cannot validate
        H-ADV-1-W or an SSI-curve claim. The diagnostic is nevertheless not
        replayable from the frozen bytes. It names a fixed graph kernel and
        first-hit-at-zero convention, but graph_seed is not committed, target
        set and start derivations are unspecified, and the promised exact
        recurrence/rational aggregation is deferred to future diagnostic output.
        More importantly, comparing every sampled target set to a reference CDF
        averaged over all target sets can confound target-set geometry with the
        walk kernel; a conditional reference for the sampled set or a declared
        random-set statistic is needed. Any result from this arm would remain
        synthetic-only even after repair.
      reference: experiments/EXP-SSI-357363/specification.yaml:437-450,560-582
    - id: RT-BCD3D9-PROVENANCE
      severity: provenance_caveat
      finding: >-
        The requested snapshot commit and parent are correct and its diff adds
        exactly the four snapshot paths. The immutable snapshot receipt still
        has commit_sha: null and verification.status: pending_post_commit, so
        post-commit self-binding is not present in that receipt. This is an
        archival caveat, not mathematical evidence. The preflight also found no
        configured usable API backend; native Codex provenance is independent
        and non-Bedrock but the model label is not adapter-probe verified.
      reference: coordination/goals/GOAL-SSI-001/batches/BATCH-c057fd/archives/TASK-20260809-9a76c7/snapshot-receipt.json:1-21
  required_controls:
    - >-
      Freeze field-by-field SSI-BYTES-v1 frames, literal generator/domain
      versions, seed inclusion, null markers, event serialization, trace hash
      bytes, and a query-key lookup hash distinct from the full-record build
      hash.
    - >-
      Replace every cryptographic-scale u64 candidate/permutation counter with a
      proved sufficient representation, bound biguint length and output/HNF
      envelopes, and specify widths for all trace and completion counters.
    - >-
      Define SSJ, ORDER, and C-helper headers, bodies, capacities, digests,
      generator algorithms, cardinalities, helper slot widths, and explicit
      T_setup/M_setup/build traces; bind any order helper to the exact branch
      rather than leaving a full order table as a hidden oracle.
    - >-
      Close every A/B/C output path, including terminal HNF sources, C middle
      composition, transition semantics for external edge certificates,
      output witness bytes, digest/certificate storage, and peak workspace.
    - >-
      Define the query probability space, iid/restart semantics, capped-cost
      functional, cap-exhaustion status, complete primitive counter equations,
      supplied T_inc_foe, and exact branch-specific Q_break_even inputs.
    - >-
      Make owner-mismatch and shuffled controls use fully specified valid
      records and certificates, mark S_eff<2 cases not_applicable, and either
      prove event/path identity or stop calling regenerated payloads same-path.
    - >-
      Supply a finite treatment-matched C-pair generator, numeric rejection cap,
      descriptor reconstruction and null reference/calibration, and freeze the
      synthetic graph seed/derivation/reference statistic while preserving its
      non-SSI ceiling.
  counterexample_or_mutation: >-
    Static contract mutations only, none executed: (1) at a named sigma=1
    builder row, counter_u64 cannot enumerate the declared 2^20*S_req cap once
    the cap exceeds 2^64; (2) a C-helper record with all four declared fields is
    four bytes longer than helper_entry; (3) a query holding only target_curve_id
    cannot evaluate the specified full-record hash_key without an unstated
    payload or a second lookup oracle; (4) CTRL-SHUFFLED-FIBER with S_eff=0
    reaches modulo zero; (5) changing an owner requires a different endpoint
    path certificate, so regenerated owner orders do not establish a byte-
    identical path; and (6) a C pair has no declared terminal order bytes from
    which to emit the required witness. These are static schema/logic attacks,
    not arithmetic-row generation, experiments, diagnostics, or observations.
  baseline_comparison: >-
    No Pollard-rho, BSGS/MITM, specialized baseline, arithmetic row, cost table,
    timing, or physical table was executed. S=0 and the sigma=1/2 B mapping are
    named controls only. T_inc_foe remains an unsupplied input and the setup,
    query, certificate, and helper costs are not fully computable. No gain over
    any baseline follows from this snapshot.
  heuristic_challenges:
    - >-
      H-ADV-1-W remains correctly separated as a fixed-A_p,
      worst-case-over-E conditional statement, and H-ADV-1-R remains explicitly
      weaker and non-SSI. Neither has a defined query probability law, complete
      output path, or validated control in this snapshot.
    - >-
      H-ADV-2 is load-bearing for order construction, B-membership output, and
      any C endpoint output, but ORDER-GEN and terminal order sources are not
      reproducibly supplied. H-ADV-3 remains a named closed-list ceiling, not a
      proof about arbitrary advice. H-ADV-4 remains unverified and its null
      statistic is not calibrated by the declared permutation alone.
    - >-
      The explicit synthetic boundary is a surviving protection against scope
      inflation. It cannot validate H-ADV-1-W, and its own unresolved
      conditional-reference issue prevents even a clean synthetic diagnostic
      interpretation.
  cost_model_challenges:
    - >-
      Direct b_order and b_index arithmetic repairs survive, but C-helper bytes,
      helper capacities, order-helper storage, candidate bytes, path digest and
      certificate bytes, output witness bytes, and peak workspace remain
      uncharged or undefined.
    - >-
      T_setup is an additive label without stage traces; T_q uses an unbounded
      inverse-success expression with a hard cap; FOE primitive weights have no
      event decomposition; and Q_break_even cannot be evaluated without
      T_inc_foe and the missing setup/query values.
    - >-
      The external edge-stream input is an explicit boundary, not a free
      cryptanalytic result. Any future claim must state that certificate
      generation/availability is excluded and must not present the resulting
      accounting as an end-to-end attack cost.
  reduction_and_scope_challenges:
    - >-
      The claim ceiling correctly excludes EndRing, Isogeny, SQIsign, CSIDH,
      security, and all-advice conclusions. The C branch still has no explicit
      terminal order/output source, and the external certificate boundary
      prevents a complete reduction or attack path.
    - >-
      No affected-vs-safe scheme conclusion is established. The named
      cryptographic labels are parameter labels only; they do not transfer the
      closed-list accounting to deployed schemes or security levels.
  proof_architecture_challenges:
    - >-
      The fixed-advice quantifier, union-before-counting fiber rule, named-branch
      method ceiling, and nearby non-SSI warning are useful surviving repairs.
      They do not supply the missing observation-fiber separator for external
      path certificates or the missing output witness in C.
    - >-
      The observation-collision split between B-tagged and B-membership is
      preserved, but a shared/possibly full ORDER-MANIFEST changes the resource
      model unless its cardinality and branch binding are frozen.
    - >-
      The proof-map and control entries are obligations and gates, not passes.
      No failed control, heuristic, arithmetic row, or scientific observation
      was recorded here.
  narrowest_supported_statement: >-
    The immutable d2e1cb4 snapshot contains an additive, execution-unauthorized
    design refinement that fixes the predecessor's direct b_order and b_index
    undercounts, adds literal code names and finite query caps, improves the
    fixed-advice quantifier, and states an explicit external edge-stream and
    non-SSI diagnostic boundary. It is not yet a byte-exact,
    cryptographic-scale, physically charged, output-producing,
    replay-reproducible, branch-complete execution contract. No mathematical,
    cryptanalytic, security, exponent, novelty, hypothesis-transition,
    completion, or negative result follows. Design repair is not an observation,
    and execution and diagnostics remain unauthorized.
  next_concrete_action: >-
    The Coordinator should create an additive successor that closes the helper
    and manifest schemas, lookup hashing, scale-safe counters and biguint/output
    bounds, HNF/C output sources, external certificate semantics, finite FOE and
    capped-restart definitions, paired trace bytes, valid owner/shuffle nulls,
    C-pair generation/calibration, and synthetic seed/reference semantics.
    Preserve all predecessor bytes, re-review a new immutable snapshot
    independently, and keep execution_authorized=false until every declared
    gate is actually satisfied.
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-c057fd/reviews/TASK-20260809-bcd3d9/red_team_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-c057fd/reviews/TASK-20260809-bcd3d9/runtime-session-receipt.json
```

## Verdict and review boundary

**`DISSENT` on freeze and execution readiness; `CONCUR` on the additive design-only scope, explicit external-path boundary, non-SSI diagnostic ceiling, and unauthorized execution state.**

The successor is materially better than `EXP-SSI-8e589d`: the sign-byte
correction gives the stated 1186/2274 order widths, the index header is now in
the b_index equation, fixed-A_p quantifiers are explicit, and the prior
alternate replay seed was removed. Those repairs are real design changes, not
observations. The remaining defects above prevent a reproducible physical
cost/frontier contract and block any execution or scientific interpretation.

No experiment, diagnostic, arithmetic-row generator, cryptographic computation,
parser-based scientific check, or cost measurement was executed. The listed
mutations are static counterexamples to the frozen specification only. No queue,
ledger, predecessor artifact, or specification was edited.
