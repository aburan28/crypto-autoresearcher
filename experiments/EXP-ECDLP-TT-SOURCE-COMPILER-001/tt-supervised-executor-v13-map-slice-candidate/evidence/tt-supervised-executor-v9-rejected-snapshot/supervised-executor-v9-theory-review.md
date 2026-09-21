# Handoff: V9 Frozen Zero-Run Theory Review

## Claim or task

Independently determine whether frozen V9 closes all 20 V8 obligations and
establishes the claimed two-trace restricted invariant.

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `TOY-EVIDENCE` | `ZERO-RUN`

**Decision: NO-GO. Preserve V9 as negative evidence and cut V10.**

## Assumptions

- Conclusions concern the frozen JavaScript reducer/verifier and canonical
  JSON/SHA-256 evidence model.
- SHA-256 collisions were neither assumed nor used; counterexamples use honest
  canonical rehashing.
- Producer labels are model fields, not authenticated runtime identities.
- OS capabilities, process identity, filesystem durability, and live Git-ref
  atomicity remain outside the model.
- Local PASS receipts and the own-audit were treated as claims to reproduce.
- No file under `/Volumes/Volume/autolab` was modified by the reviewer.

## Evidence so far

### Integrity and baseline

- External/top-manifest SHA-256:
  `b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c`.
- All 36 top-manifest members passed.
- Nested V8-rejected, V8-frozen, and V7-rejected manifests passed.
- No unmanifested AppleDouble payload was found in the frozen bundle.
- Two fresh builder runs reproduced artifact SHA-256
  `e651f2c42c2ccc555ce33ada4e64aabd717bdc85e06c94a3e5d97fcae9e8a35c`.
- The unchanged verifier reproduced receipt
  `49f5c78846f840762ac021eede24d7a5329fe3c391a6c4e09e36fe3ba15b7939`,
  132 checks, two traces, 211 steps, and 26/26 stored regressions.

The exact frozen traces are:

| Trace | Steps | Records | Final universe |
|---|---:|---:|---|
| A0 | 105 | 241 | `40cc113397e10dde9fbf0b9ea53aa328d49f8346eddb038a01b9b0688a22528b` |
| A2 | 106 | 254 | `6bf7a3b7987dc244f7f8f0a9a97f310c71c870082532bf06ea64986aae21c001` |

Both are successful happy paths ending at `LOCK_RELEASED`; neither is a complete
failure/recovery trace.

### Independently reproduced recalculation counterexample

The reviewer independently changed the A2 recalculation terminal digest to
zeroes and totals digest to `ff...ff`, then rehashed and relinked every affected
closure/journal record and final root. The unchanged verifier accepted:

```text
artifact: 38bf002efc5c7fa02395f2875497c6ae5081f92fe583969be634151ad3cf093c
receipt:  4890ae3c9f7dc8836f6e4fb8eb60a7ddf3cf4bab7a712fe2ae78922af9a0ef1a
checks:   132
stored regressions: 26/26
```

The builder rejects that universe as `RECALCULATION_LINKAGE_MISMATCH`, directly
falsifying builder/verifier equivalence. This fails `V9-IDENTITY-01`,
`V9-POST-01`, and `V9-DIFFERENTIAL-01`, and weakens closure/outcome claims.

### Independent known-type closure counterexample

The reviewer inserted a canonical, authorized sequence-zero record:

```text
kernel/SEC9-TRACE-A2-END-TO-END/attempts/A3/lifetime.json
bbe2b733039ba5ac968cebc9654fad227e680bb0a0b89e2613b10cb78b9a6c55
```

A3 was never admitted and no typed payload edge referenced this lifetime. After
recomputing every journal receipt and final root, both the builder reducer and
unchanged verifier still reached `LOCK_RELEASED`.

Therefore, for accepted universe `V'`:

```text
Accept(V') = true
A3 not in admitted_attempts(V')
L_A3 not in Reach(V')
L_A3 in records(V')
```

This directly falsifies exact typed closure (`V9-CLOSURE-01`) and the claimed
global trace/reducer invariant.

### Schema counterexample boundary

The reviewer did not complete a separate dynamic replay before the stop request,
so the supplied schema receipt is not counted as independently reproduced. The
static defect is confirmed: the builder checks
`record.schema == tt-supervised-record-v3`; the verifier checks envelope keys,
type, producer, canonical bytes, and digest but never checks that literal.

### Obligation assessment

| Obligation | Assessment |
|---|---|
| V9-REDUCER-01 | Not closed: only 40 of 153 selector rule IDs have V9 action semantics. |
| V9-SCHEMA-01 | Failed: envelope schema and cross-field constraints diverge. |
| V9-PATH-01 | Frozen-instance pass for canonical durable paths. |
| V9-ORDINAL-01 | Frozen-instance pass for supplied traces; global base closure failed. |
| V9-IDENTITY-01 | Failed by recalculation and known-type closure substitutions. |
| V9-PHASE-01 | Partial happy-path enforcement only. |
| V9-TRACE-01 | Failed as a global claim; exact-universe closure is false. |
| V9-POST-01 | Failed: verifier does not reconstruct exact action-domain bytes. |
| V9-EVENT-01 | Not closed: failure event actions are not covered end to end. |
| V9-AUTHORITY-01 | Restricted producer-label allowlist only. |
| V9-CLOSURE-01 | Failed directly by the A3 lifetime record. |
| V9-GIT-01 | Frozen-instance pass for generated Git object bytes/OIDs. |
| V9-GIT-02 | Frozen-instance pass for the 14 supplied parent/ref/CAS rows. |
| V9-OUTCOME-01 | Not closed beyond successful outcomes and one point mutation. |
| V9-CAPABILITY-01 | Not closed at kernel-policy/runtime identity boundary. |
| V9-RESOURCE-01 | Frozen A0-A2 arithmetic pass; global closure failed. |
| V9-RESOURCE-02 | Partial; verifier receipt equality is weaker than builder. |
| V9-CONTEXT-01 | Partial on two happy paths, not all selector states. |
| V9-PUBLISH-01 | Passed for the exact frozen portable bytes. |
| V9-DIFFERENTIAL-01 | Failed directly by recalculation acceptance divergence. |

All 26 stored regressions reproduced their expected rejection, but they are
point mutations rather than a structural completeness proof. In particular,
the unreferenced-record control uses an unknown type rather than an authorized
known type, and the journal-splice control does not recompute the chain.

## Strongest valid restricted claim

`OBSERVATION`:

> For exactly the two manifest-bound original universes, the frozen builder and
> verifier deterministically replay 105 and 106 successful steps to
> `LOCK_RELEASED`; all 26 stored direct mutations reject; all supplied Git OIDs
> and parent/ref/CAS rows agree; and admitted A2 resource arithmetic is exact.

This does not quantify over all accepted universes, known-type sequence-zero
additions, fully recomputed journals, alternate record schemas, failure branches,
or a deployed runtime.

## Failure modes

- Sequence-zero membership is a broad whitelist, not exact trusted-root closure.
- Hash-consistent journals do not prove typed semantic reachability.
- The verifier does not reconstruct recalculation/lock bytes independently.
- Builder/verifier schema enforcement differs.
- Selector totality evidence applies to a stronger inherited validator than the
  implemented V9 source validator.
- Failure/outcome branches and kernel-policy evidence remain absent.

## Next concrete action

Cut V10 from frozen V9 with exact typed-reachability equality at sequence zero,
independent exact-byte reconstruction for every selector outcome, and mandatory
fully rehashed controls for A3 lifetime, forged recalculation, and forged schema.

## Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-review-bundle`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-review-bundle.sha256`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-local-counterexamples`
