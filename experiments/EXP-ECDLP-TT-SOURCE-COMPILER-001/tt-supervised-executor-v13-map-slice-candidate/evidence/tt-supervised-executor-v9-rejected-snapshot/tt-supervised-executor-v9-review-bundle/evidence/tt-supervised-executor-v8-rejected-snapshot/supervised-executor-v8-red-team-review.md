# Handoff: Supervised Executor V8 Pre-Freeze Red-Team Review

## Claim or task

Determine whether contract hash
`6883c450d01dd01287f0789079d87bc97720e0cd388f9812e2dd2ed6191ea17c`
and its frozen companion artifacts justify possible schema implementation of the
`MODEL-BOUND`, `ZERO-RUN` supervised-executor design.

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

Decision: **NO-GO.**

## Assumptions

- All eight `SHA256SUMS` entries passed before and after review; every named
  artifact remained `uchg`.
- The bundle directory and its parent are not `uchg`; unmanifested mutable
  AppleDouble sidecars exist.
- `local-verification-v8.json` and `supervised-executor-v8-own-audit.md` were
  excluded as evidence.
- No campaign or control suite was run. Counterexamples invoked exact verifier
  function bodies against the frozen transition and control artifacts in memory.
- The referenced `supervised-executor-repair-handoff-v7.yaml` is absent, so the
  audit follows obligation identifiers and paraphrases in the frozen contract.

## Evidence

### Risk list, ordered by severity

1. **CRITICAL: malformed and authority-forged record universes pass.**
   `validateUniverse` has no closed record-type, payload, or producer schema and
   compares raw, unnormalized paths. Executable counterexamples accepted:
   sparse A2 history; validation-terminal substitution for spawn failure;
   candidate-produced CAS against `refs/heads/attacker-controlled`;
   candidate-produced forged capability receipt; and two unknown records whose
   paths normalize to one physical path.
2. **CRITICAL: resource accounting is not bound to the durable campaign.**
   Frozen composed trace `SEC8-TRACE-REC-A2` finalizes A2 using a measurement
   containing only A0 and A1, despite A0, A1, and A2 admissions/starts. A separate
   fixture accepts an empty overlap graph and derives memory 37 instead of 73;
   the label `conservative_possible_overlap_complete` is asserted, not proved.
3. **CRITICAL: composed traces permit source reseeding.**
   `verifyTraceControl` chains only each post-record universe to the next
   pre-record universe. It never reconstructs the next source/context from the
   previous post-state. The four frozen traces therefore establish record-array
   continuity only. There is no complete A0 -> P0-P5 -> E0 -> Git -> meter trace.
4. **CRITICAL: approved Git fixtures do not form one Git history.**
   P0 produces commit OID `eeafe9a0e0fb7e4136c64ab8a95802617d260a1e`;
   P1 uses parent/ref OID `9864eb724678e58af0de7829c1a09da8b7d29a1e`.
   CAS validation ignores ref name and producer authority; tree OIDs are synthetic;
   and no post-CAS ref observation closes the TOCTOU window.
5. **HIGH: exact A0-A32 and phase flow is declarative.**
   No invariant requires contiguous recovery history. Reservations contain only
   phase, while launch validation does not bind reservation ordinal, launch
   ordinal, admission, capability receipt, and current attempt into one identity.
6. **HIGH: capability mutation coverage is not capability closure.**
   The 27 descriptor mutations test a standalone object. Durable receipts are not
   bound to descriptor bytes, executable opened-file identity, attempt,
   reservation, kernel policy, or launch identity. Inherited descriptors identify
   numbers but not targets or rights.
7. **HIGH: publication and preservation are incomplete.**
   Directory roots remain replaceable; startup reads are not an atomic cross-file
   snapshot; the verifier omits one publication binding; the control artifact is
   not self-bound; V7 bytes are external; and the original handoff is absent.

## Exact executable counterexamples reported by Red Team

| Attack | Frozen fixture/source | Accepted result |
|---|---|---|
| Sparse A2 history | fixture `de367e33...4467` | A1 records removed; `E013` still selected |
| Event substitution | source `f289539e...a8bd`, universe from `9132e332...6785` | spawn-failure label accepted over validation-failure terminal; `TN-L005` selected |
| Ref/authority attack | fixture `78348962...6555` | candidate CAS on attacker ref; `G005E` selected |
| Capability forgery | fixture `4159a3d4...9f6e` | attacker receipt accepted; `AN002` selected |
| Path alias and unknown types | fixture `c8d96c89...b5c7` | `opaque/x.json` and `opaque/dir/../x.json` accepted; `AN001` selected |
| A2 accounting omission | trace `SEC8-TRACE-REC-A2` | A2 receipt binds A0/A1-only measurement |

Truncated fixture digests identify the exact frozen review findings; the frozen
control artifact and verifier hashes are authoritative for reproduction.

## Obligation audit

| Obligation | Result | Red-team finding |
|---|---|---|
| `V8-ORDINAL-01` | Fail | Sparse A2 history selects E013; A2 receipt omits A2 measurement. |
| `V8-ORDINAL-02` | Fail | Phase, capability, resource, and reservation records are not one ordinal chain. |
| `V8-PHASE-01` | Fail | Successor history and reservation-attempt identity are not reconstructed. |
| `V8-TRACE-01` | Fail | Only record arrays compose; source, context, and post-state are reseeded. |
| `V8-EVENT-01` | Fail | Validation terminal substitutes for spawn failure; E0 remains declarative. |
| `V8-RECOVERY-01` | Narrowly satisfied | R005T/R005F fixtures exist; surrounding recovery state is declarative. |
| `V8-EVIDENCE-01` | Fail | Presence substitutes for payload, producer, authority, and state derivation. |
| `V8-IDENTITY-01` | Fail | Launch/process, reservation, capability, phase, and attempt identities are open. |
| `V8-POST-01` | Fail | Local union works; action and next source remain fixture-controlled. |
| `V8-UNIQUE-01` | Fail | Raw paths miss aliases; unknown types and logical identities pass. |
| `V8-GIT-01` | Fail | Candidate-produced alternate-ref CAS passes. |
| `V8-GIT-02` | Fail | P1 parent differs from P0; tree and post-CAS ref are unverified. |
| `V8-CONTEXT-01` | Fail | Schema/context and dispatcher match are supplied externally. |
| `V8-OVERLAP-01` | Narrowly satisfied | Per-schema products do not cover cross-context selector composition. |
| `V8-CAPABILITY-01` | Fail | Malformed candidate-produced capability receipt passes. |
| `V8-RESOURCE-01` | Fail | Attempt/vertex sets and overlap completeness are not derived. |
| `V8-RESOURCE-02` | Fail | A2 trace directly demonstrates measurement/receipt mismatch. |
| `V8-PUBLISH-01` | Fail | Directory root, cross-file atomicity, control binding, and V7 bytes are missing. |

## Overclaim corrections

- `complete durable record universe` becomes `raw record array with partial
  linkage checks`.
- `exact A0-A32 flow` becomes `A0-A32 values occur in domains and isolated
  fixtures`.
- `composed traces prohibit reseeding` is false; only record arrays chain.
- `every event resolves exactly` is false; terminal predicates alias labels.
- `exact Git bytes/OIDs/ref/CAS` is false across phases.
- `capability closure` is only top-level descriptor mutation coverage.
- `exact resource accounting` is arithmetic over caller-supplied unbound inputs.
- `complete V7 preservation` is only external filename/hash assertions.

## Required falsification suite

V9 must reject:

- normalized path aliases;
- unknown record types and payload keys;
- unauthorized producer swaps;
- sparse or noncontiguous ordinals;
- reservation/launch ordinal drift;
- phase/context/source reseeding;
- terminal-label substitution;
- alternate Git refs and disconnected parents;
- post-CAS ref movement;
- omitted attempts and deleted overlap edges with recomputed claims;
- forged capability receipts and inherited-descriptor target substitution;
- cross-file publication swaps.

State, context, phase, ordinal, resource membership, and authority must come from
one closed reduction over canonical record bytes, not source status fields.

## Next concrete action

Produce a V9 bundle that replaces the split declarative model with one closed
`deriveState(canonicalRecordUniverse)` reducer, binds every record to a closed
payload schema and authorized producer, uses actual predecessor Git OIDs and
post-CAS ref receipts, derives resource and capability membership from durable
identities, includes the original handoff and V7 evidence bytes under one pinned
manifest, and contains mandatory rejection fixtures for every counterexample.

## Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/SHA256SUMS`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/verify_v8_design_artifacts.mjs`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/build_v8_design_artifacts.mjs`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-transition-matrix-v7.json`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-control-matrix-v7.json`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-contract-v8.md`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v8-review-bundle/supervised-executor-topology-decision-v7.md`
