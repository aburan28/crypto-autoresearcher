# Handoff: V9 Frozen Zero-Run Independent Red Team

## Claim or task

Determine whether frozen V9 schemas and controls are eligible for implementation
after checking integrity, both traces, all 20 repair obligations, all 26 stored
mutations, and strengthened fully rehashed attacks.

## Status

`NEGATIVE RESULT` | `MODEL-BOUND` | `ZERO-RUN`

**Decision: NO-GO.** No campaign was run and no file under
`/Volumes/Volume/autolab` was edited by the reviewer.

## Assumptions

- SHA-256 collision/preimage resistance.
- The verifier canonical-JSON implementation is the intended byte model.
- Private copies accurately represent the frozen inputs.
- Runtime/OS enforcement is outside this zero-run review.
- Builder probes are supplemental; verifier acceptance establishes each
  verifier counterexample.

## Evidence so far

### Frozen root

- External/top-manifest SHA-256:
  `b5426daa7d9ebf66db356ae2080780712e8318f03bec04c37d12b45580bd2b1c`.
- All 36 listed payloads passed; the bundle had 37 regular files total, no
  symlinks, and no unlisted payloads before mutation.
- Embedded rejected-snapshot manifests passed.
- Unchanged verifier SHA-256:
  `e050b19ebd36858e42581f8fac0b17c80867a0f34b994b7876d8bddaa2d85c12`.
- Original verifier result: `PASS`, receipt
  `49f5c78846f840762ac021eede24d7a5329fe3c391a6c4e09e36fe3ba15b7939`,
  132 checks, 26/26 regressions.

### Trace coverage

- A0: 105 steps, 241 records, 97 actions, 8 observations.
- A2: 106 steps, 254 records, 98 actions, 8 observations.
- Both terminate only through `valid_outcome`.
- Neither covers failure, quarantine, lock conflict, live-process
  reconciliation, invalid-terminal, or recovery branches.
- Only 40 of 153 rules and 10 of 18 schemas appear in implemented verifier
  action semantics.

### Accepted fully rehashed counterexamples

| Counterexample | Mutated artifact | Accepted receipt | Property defeated |
|---|---|---|---|
| False A2 recalculation roots | `38bf002e...093c` | `4890ae3c...ef1a` | Identity, closure, postcondition, outcome; builder rejects |
| False late closure/resource/outcome | `ccedc0f1...930f` | `e8481a01...9f15` | Closure, resource, outcome, postcondition |
| Cross-phase Git blob/tree | `c0d7fc6f...49b5` | `a1af2534...2bca` | Git content identity and phase closure; builder also accepts |
| Capability/launch relinking | `a0f72b00...b4d8` | `2c4cdab4...6c5` | Private-map, launch, process-token identity |
| Invalid resource observations | `6c500756...c8d5` | `7212fddc...9b6b` | Value domains and resource accounting |
| Sequence-zero known-type A3 | `42db1592...8709` | `17ff8e66...8b34` | Trusted-root exactness and closure; builder also accepts |
| Cross-phase terminal | `7e829935...5d8d` | `710de980...dd71` | Event, identity, phase, outcome |
| Mandatory-suite substitution | `e0061d15...e3d5` | `92e92566...cc62` | Regression identity and differential evidence |
| Intermediate evidence symlink | `d86c360e...fb22` | `7e5958c1...bf16` | Evidence path uniqueness and publication |
| Unlisted publication payload | original artifact | original PASS receipt | Manifest closure and publication |

Full hashes and mutation scripts are preserved under
`tt-supervised-executor-v9-local-counterexamples/`.

The supplied final-receipt schema counterexample was not independently executed
before the stop request and is not counted as a dynamically confirmed Red Team
case. The code defect is independently confirmed: verifier `inspectRecord` never
checks the required record-schema literal.

### Counterexample details

#### Recalculation and late closure

The recalculation case binds nonexistent terminal and totals digests and relinks
M008/M009. The late-closure case additionally supplies a false committed root,
a forged resource receipt, a `recoverable_crash` attempt end, and lock status
`held`. Both still produce full verifier PASS receipts.

#### Cross-phase Git and terminal

The Git mutation makes the P1 tree contain the valid P0 blob while P1 intent
continues to name P1 content. Literal Git object syntax and OIDs remain valid.
The terminal mutation makes a P1 valid terminal point to P0 result/content. Both
survive fully recomputed journals, showing that same-type checks do not enforce
same-phase identity.

#### Capability/launch

The E0 map descriptor token is relabeled as an A0/P0/fd99 decoy, E0 launch drops
the map receipt, and its process token is replaced by an A0/P0 replay token.
The exact static capability descriptor remains pinned, but actual map/process
use is not bound end to end.

#### Resource observation

A2 `bootstrap_observed=23` exceeds cap 22 and
`meter_observed_preterminal=-1`; measurement arithmetic and every downstream
link are recomputed. The domain and overlap graph remain structurally complete,
yet the verifier accepts invalid observed values.

#### Sequence-zero closure

An authorized A3 `resource_lifetime` with no admission/start/consumer is added to
the trusted base and all 106 journals are relinked. Both builder and verifier
accept, directly falsifying exact reachability closure.

#### Regression substitution

All 26 mandatory controls can be replaced with 26 copies of a trivial unknown-
record rejection while preserving 26/26 PASS. The verifier trusts artifact-
supplied IDs, operations, and expected reasons instead of pinning the suite.

#### Publication

Adding an unlisted payload does not change the expected top-manifest digest or
the verifier PASS result. An in-bundle intermediate symlink alias can also steer
evidence resolution. The pristine frozen directory was manually clean; V9 does
not enforce that closure itself.

### Strengthened attacks correctly rejected

- A fully relinked alternate executable/descriptor/fd descriptor rejects as
  `CAPABILITY_DESCRIPTOR_INVALID`.
- Fully rehashed journal deletion/reorder attacks reach semantic replay and
  reject as `ACTION_SOURCE_SCHEMA_MISMATCH`.
- Alternate ref, parent, CAS, post-ref, and literal-tree-byte attacks reject.
- Exact resource-domain and overlap-edge omissions reject.

These are useful restricted controls, but do not repair accepted same-type,
cross-phase, or unconsumed-record substitutions.

### Stored regressions

All 26 stored mutations reproduced the claimed reason. Most do not relink
downstream dependencies. The unreferenced-record test uses an unknown type, the
journal-deletion test leaves a simple gap, and the publication test compares
artifact metadata rather than an actual swapped file.

### Obligation disposition

| Obligation | Disposition |
|---|---|
| V9-REDUCER-01 | Falsified: only 40/153 rules have semantics; lock presence alone completes. |
| V9-SCHEMA-01 | Falsified by invalid resource values and static schema omission. |
| V9-PATH-01 | Partial: durable paths checked, intermediate evidence symlink accepted. |
| V9-ORDINAL-01 | Partial: sparse/range controls pass, known-type base extra accepted. |
| V9-IDENTITY-01 | Falsified by closure, terminal, map, and process substitutions. |
| V9-PHASE-01 | Falsified by cross-phase Git and terminal links. |
| V9-TRACE-01 | Happy-path only; no adverse branches and semantic corruptions accepted. |
| V9-POST-01 | Falsified: type multisets replace exact action-output reconstruction. |
| V9-EVENT-01 | Falsified by same-type cross-phase terminal linkage. |
| V9-AUTHORITY-01 | Restricted producer-label allowlist only. |
| V9-CLOSURE-01 | Falsified by A3 lifetime and unreferenced P1 blob. |
| V9-GIT-01 | Falsified by valid P1 tree containing P0 blob. |
| V9-GIT-02 | Restricted parent/ref/CAS continuity survived attacks. |
| V9-OUTCOME-01 | Falsified by recoverable-crash/valid-closure coexistence. |
| V9-CAPABILITY-01 | Falsified beyond hard-pinned descriptor bytes. |
| V9-RESOURCE-01 | Falsified by invalid observed values; graph shape alone is insufficient. |
| V9-RESOURCE-02 | Falsified: verifier omits receipt input/result parity. |
| V9-CONTEXT-01 | Partial only on covered traces; 113 rules remain outside semantics. |
| V9-PUBLISH-01 | Falsified by unlisted payload and symlink alias. |
| V9-DIFFERENTIAL-01 | Falsified by builder/verifier divergence and replaceable suite. |

## Strongest valid restricted claim

For the exact frozen bytes, V9 faithfully replays two serialized successful
traces and rejects the exact 26 stored first-order mutations. It enforces
canonical record hashing, exact payload-key sets, canonical durable paths, the
known producer map, one exact capability descriptor, selected Git parent/ref/CAS
equalities, and source-context continuity for the 40 implemented action rules.

It does not establish semantic closure, same-phase identity, total reducer
coverage, adverse-branch correctness, mandatory-regression identity, or
publication closure.

## Failure modes

- Hash-consistent known-type records can carry false or unconsumed semantics.
- Journals authenticate supplied history but not correct action generation.
- Closure is presence-based instead of typed reachability.
- Phase/ordinal identity is absent from multiple edges.
- Git syntax/ref continuity can coexist with wrong-phase content.
- Resource graph shape can coexist with false values.
- Mandatory controls are self-described and replaceable.
- Root cleanliness is manually observed, not verifier-enforced.

## Next concrete action

Cut a fresh zero-run V10 snapshot with all accepted V9 universes pinned as
mandatory regressions and verifier-owned exact typed-edge reachability as the
closure invariant.

## Artifact paths

- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-review-bundle`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-review-bundle.sha256`
- `/Volumes/Volume/autolab/research/tt-supervised-executor-v9-local-counterexamples`
