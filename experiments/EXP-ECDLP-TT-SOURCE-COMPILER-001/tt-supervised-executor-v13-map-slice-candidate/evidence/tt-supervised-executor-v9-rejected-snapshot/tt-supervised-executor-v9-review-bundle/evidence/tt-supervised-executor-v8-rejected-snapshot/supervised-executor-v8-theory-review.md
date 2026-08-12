# Handoff: V8 Frozen-Bundle Theory Review

## Claim or task

Decision: **NO-GO.**

Schema implementation is not justified. The frozen model contains concrete
information-flow, Git-chain, resource-binding, and record-closure
counterexamples.

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

This is harness/schema research, not an ECDLP result.

## Assumptions

- Review scope was limited to the exact frozen V8 review bundle.
- No builder, verifier, control suite, or campaign was executed by the reviewer.
- `local-verification-v8.json` and `supervised-executor-v8-own-audit.md` were
  excluded as evidence.
- The 18 obligation IDs were interpreted through the V8 contract because the
  referenced `supervised-executor-repair-handoff-v7.yaml` is absent.
- Runtime OS isolation, lock semantics, process identity, filesystem durability,
  and Git ref atomicity remain outside the finite model.

## Evidence

### Hash and immutability boundary

`shasum -a 256 -c SHA256SUMS` succeeded for all eight listed payloads. The eight
payloads and `SHA256SUMS` have `uchg`. The bundle directory and AppleDouble
sidecars do not. The listed payload bytes are hash-stable; the entire directory
tree is not an immutable boundary.

### Findings, ordered by severity

1. **CRITICAL: composed traces reseed semantic source state.**
   `makeComposedTraceControl` creates every next source with `sourceFor` and
   carries forward only the record universe. The verifier checks record-universe
   equality but never reconstructs `next.pre_state` from `previous.post_state`.
   The A2 trace jumps from D004's `recovery_reconstruction` handoff to a freshly
   seeded M002 meter source.
2. **CRITICAL: the Git parent chain is not the committed chain.**
   Tree and parent OIDs are hashes of descriptive strings, not derived from tree
   bytes or the preceding committed object. Frozen controls give P0 commit OID
   `eeafe9a08c81c278c285b8192a561dc680e60a1e`, while P1 uses parent
   `9864eb7259ec027a8ea05b3c224ab2e94e629a1e`. No Git tree-object bytes or
   tree-object receipt exists. CAS therefore proves consistency with a fabricated
   observation, not continuity from the preceding committed phase.
3. **CRITICAL: A2 binds an A0/A1-only resource measurement.**
   The A2 receipt points to a measurement containing only attempts A0 and A1.
   Receipt validation compares hashes and totals but never requires the receipt
   ordinal to occur in the measurement. Resource validation also does not require
   memory vertices to equal the attempt/closure domain.
4. **HIGH: the complete durable universe is not closed.**
   Both validators accept an unknown `record_type`, arbitrary path, and arbitrary
   payload whenever canonical bytes and digest agree. Such a record falls through
   every linkage check and is classified as a noncounter record. The builder also
   accepts recovery admission A33 through its regex while the verifier rejects it
   against A0-A32.
5. **HIGH: capability validation is not bound to launch.**
   The durable capability receipt contains only a schema label and
   `valid_current`; it has no descriptor digest, executable digest, ordinal,
   phase, or launch identity. Any launch can reuse the singleton receipt.
6. **HIGH: event symbols remain an inherited oracle.**
   Source evidence compilation derives only Git fields. Spawn, runtime, and
   validation failures all resolve to a `phase_terminal` with
   `TERMINAL_HARNESS_FAILURE`; the record does not derive which event occurred.
7. **HIGH: exact postcondition reconstruction is local, not compositional.**
   The verifier reconstructs each fixture's append-only union, but `post_state`
   is metadata plus a partial patch, not a complete next-schema source. No total
   reconstruction function from post-state and record universe to the next closed
   source exists.
8. **MEDIUM: preservation and publication are not self-contained.**
   The contract references an absent repair handoff. V7 preservation consists of
   asserted hashes while builder and verifier read an external sibling directory.
   The in-memory publication snapshot binds only builder and transition bytes.

## Obligation audit

| Obligation | Result | Theory finding |
|---|---|---|
| `V8-ORDINAL-01` | Failed | Pointwise A0-A32 domains do not establish cross-context identity flow. |
| `V8-ORDINAL-02` | Failed | Approval maximum is not reconstructed; builder/verifier disagree on A33. |
| `V8-PHASE-01` | Failed | Presence checks do not prove predecessor-chain continuity. |
| `V8-TRACE-01` | Failed | Every trace step reseeds its source object. |
| `V8-EVENT-01` | Failed | Event name is not derived uniquely from the cited record. |
| `V8-RECOVERY-01` | Failed | A2 skips reconstructed recovery state before meter finalization. |
| `V8-EVIDENCE-01` | Failed | Unknown records, paths, and payload schemas are accepted. |
| `V8-IDENTITY-01` | Failed | Capability and resource receipts lack end-to-end identity binding. |
| `V8-POST-01` | Failed | Local append-only reconstruction exists; next-source reconstruction does not. |
| `V8-UNIQUE-01` | Failed | Uniqueness is checked only for recognized, partially interpreted classes. |
| `V8-GIT-01` | Failed | Tree OID lacks tree bytes/object derivation. |
| `V8-GIT-02` | Failed | Later parent OID is not the prior committed OID. |
| `V8-CONTEXT-01` | Partial | Local contexts are fixed; context handoff is not proved. |
| `V8-OVERLAP-01` | Model-local only | Static selector partitioning does not establish reachable composition. |
| `V8-CAPABILITY-01` | Failed | Descriptor checks are isolated from the launch receipt. |
| `V8-RESOURCE-01` | Failed | Numeric domains are checked; attempt/memory membership is unbound. |
| `V8-RESOURCE-02` | Failed | A2 receipt is accepted against an A0/A1 measurement. |
| `V8-PUBLISH-01` | Partial | Listed bytes are bound; the full snapshot and V7 bytes are not. |

## Proof track

A restricted local theorem remains plausible: if declared finite domains are
complete and every source product matches at most one rule, `selectRule` is total
into rule, default, or schema rejection. That theorem concerns only local
selection.

For the stated invariants, V9 needs lemmas for:

- deterministic next-source reconstruction;
- closed record-type, path, and payload schemas;
- current ordinal and approval-budget derivation from the universe;
- event-origin derivation;
- descriptor-to-receipt-to-launch binding;
- measurement-domain-to-receipt binding;
- actual Git tree, parent, ref, and CAS continuity.

## Disproof track

The source-reseeding construction, P0/P1 OID inequality, frozen A2 mismatch,
unknown-record construction, A33 validator divergence, event aliasing, and
capability-receipt replay are formal or directly executable counterexamples in
the frozen model.

## Failure modes

- Finite Cartesian products cover declared values, not omitted runtime statuses
  or reachable traces.
- Correct arithmetic cannot repair incorrectly bound resource domains.
- Exact hashes establish byte identity, not semantic sufficiency.
- OS capability enforcement, private-map isolation, kernel identity, filesystem
  synchronization, and Git atomicity remain unmodeled implementation obligations.
- None of these findings supports a cryptanalytic or performance claim.

## Next concrete action

Create a versioned V9 bundle with a total next-source reconstruction function,
closed durable-record schemas and canonical paths, actual Git tree/parent/ref
derivation, descriptor-bound capability receipts, ordinal-complete resource
measurements, and frozen regression counterexamples for source reseeding, unknown
records, A33, Git-parent mismatch, A2 resource mismatch, event aliasing, and
capability replay. Include the authoritative 18-obligation handoff and rejected
V7 bytes in the new immutable manifest.

## Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/SHA256SUMS`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-contract-v8.md`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/build_v8_design_artifacts.mjs`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/verify_v8_design_artifacts.mjs`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-transition-matrix-v7.json`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-control-matrix-v7.json`
