# Supervised Executor V9 Own Audit

## Status

`OBSERVATION` | `MODEL-BOUND` | `ZERO-RUN`

This is a local design audit, not independent acceptance. It does not authorize
runtime implementation, control execution, the 29-mutation campaign, or an ECDLP
claim.

## Authoritative Draft Hashes

```text
5b63cfe63c1c4634bfcbe0e39b022dc9e3aabc3079e83cb6fcce1d3b21ee1848  build_v9_closed_kernel.mjs
e651f2c42c2ccc555ce33ada4e64aabd717bdc85e06c94a3e5d97fcae9e8a35c  supervised-executor-closed-kernel-v9.json
e050b19ebd36858e42581f8fac0b17c80867a0f34b994b7876d8bddaa2d85c12  verify_v9_closed_kernel.mjs
49f5c78846f840762ac021eede24d7a5329fe3c391a6c4e09e36fe3ba15b7939  local-verification-v9.json
ec5ebc1cd66bd80945478b6acfc2d849d3dbba5ee74cb4ecb5cedeca2c1d58d3  supervised-executor-contract-v9.md
ae832d8ab6185e7eeab78736e042e29762e62c38b135db419cc793eb1a628b56  supervised-executor-topology-decision-v8.md
2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383  selector-rules-v8.json
2aec7a2a64d8bb060f4224ae109a2fd13a535e8d97810ff895662f21b048e55d  evidence/tt-supervised-executor-v8-rejected-snapshot.sha256
```

The own-audit hash is intentionally absent from this list because this file was
written after the deterministic gate. The review-bundle manifest must bind it.

## Determinism

Two consecutive complete builder runs returned the same:

- builder SHA-256: `5b63cfe6...1848`;
- generated artifact SHA-256: `e651f2c4...a35c`;
- A0 final universe: `40cc1133...528b`;
- A2 final universe: `6bf7a3b7...c001`.

Two independent-verifier runs returned the same receipt SHA-256:
`49f5c788...7939`.

## Local Results

- 37 closed record types with exact payload key sets, canonical paths, and one
  authorized producer each.
- 20 V9 repair obligations named in the generated artifact.
- 2 complete traces.
- 211 journaled steps: 105 for normal A0 and 106 for recovery A2.
- 241 final records in A0 and 254 in A2.
- 26 builder-executed regressions, all rejected as preregistered.
- 26 independently re-executed regressions, all rejected as preregistered.
- 132 independent verifier checks, including the portable V8 rejection root and
  every member of its nested evidence manifest.

## Former Criticals

### A2 resource domain

The A2 measurement contains exactly:

```text
attempts: A0, A1, A2
memory vertices: A0, A1, A2, closure-A2
receipt ordinal: A2
```

The validly rehashed A0/A1-only measurement mutation rejects with
`RESOURCE_MEASUREMENT_DOMAIN_MISMATCH`.

### Git continuity

Every P1-through-E0 commit object has `parent_oid` equal to the preceding
`committed_phase.commit_oid`. Blob and binary tree bytes are literal Git object
inputs. CAS names the intended ref and authorized producer, and a post-CAS
observation must still equal the new OID.

### Source reseeding

No trace contains a source snapshot. Each action receipt binds the pre-universe,
independently reconstructed source digest, selected rule/action, next context,
and exact domain delta. Reversing input record order reconstructs the same
universe and journal cursor. Context relabeling, receipt deletion, sequence-zero
injection, and consumed-observation replay all reject.

### Closed evidence

Unknown record types, extra payload keys, unauthorized producers, normalized
path aliases, and unreferenced private-copy records reject before selection.
Sequence zero admits only root records and the exact typed prior-attempt history
used by the recovery control.

The generated artifact contains only canonical bundle-relative evidence paths.
The verifier rejects aliases, escapes, non-regular files, and absolute paths,
then validates the V8 external root and every member named by its top manifest.

## Strongest Valid Claim

For the two generated happy-path workflows and the 26 stored mutations, the V9
finite model reconstructs selector sources from canonical records and a validated
journal without source reseeding, disconnected Git history, open producer/type
authority, or unbound A2 accounting.

This is not yet a theorem about all selector states or every failure/recovery
edge. The inherited 153-rule matrix remains unchanged, but V9's complete replay
currently covers the normal and A2 successful closure paths, not every rule.

## Remaining Attack Surface

- Failure, quarantine, live-process reconciliation, lock-conflict, and invalid
  terminal branches are not complete end-to-end V9 traces.
- The independent verifier reconstructs selector sources and domain record types;
  it validates payload semantics globally but does not regenerate every action
  byte from a second action constructor.
- Sequence-zero recovery history is a typed trusted root snapshot, not a replay
  of the earlier executor journal.
- OS capability enforcement, process identity, filesystem durability, and Git ref
  atomicity remain outside this finite model.
- SHA-1 is used only for literal Git object compatibility.
- The review snapshot and external manifest root have not yet been frozen.

## Proof Track

A restricted theorem is plausible for the two trace families: given the closed
record registry, exact semantic predicates, contiguous journal receipts, and
fixed selector bytes, each valid prefix reconstructs one source and one selected
action until final lock release.

## Disproof Track

Reviewers should attempt:

- valid known-type but semantically unreferenced records;
- journal splice/reorder attacks with recomputed later digests;
- alternate valid capability descriptors and executable identities;
- Git tree/ref/parent substitutions with complete downstream relinking;
- resource lifetime and closure-domain substitutions with recomputed arithmetic;
- source ambiguity between contexts after a no-domain action;
- any failure path that reaches a selector source unavailable to `deriveState`.

## Next Concrete Action

Freeze a self-contained V9 review bundle on exact hashes and request independent
Theory and Red Team decisions. A `NO-GO` must preserve this snapshot and become a
versioned V10 repair; it must not trigger runtime implementation or a campaign.
