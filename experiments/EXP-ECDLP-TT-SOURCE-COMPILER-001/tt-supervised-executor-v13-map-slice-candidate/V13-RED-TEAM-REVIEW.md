# V13 Independent Red-Team Review

Review date: 2026-07-20  
Repository HEAD observed: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95`  
Reviewed root: `/Volumes/Volume/autolab/research/tt-supervised-executor-v13-draft`

## Decision

`NO_GO` for immutable V13 map-slice staging.

This is a staging decision, not a rejection of the scoped finite-model map
slice. The inspected reducer bytes support the typed E0 private-map boundary
on the five stored traces and the registered mutations. Immutable staging is
not ready because the publication verifier is not bound to a mandatory V13
payload allowlist or payload count and does not forbid a listed AppleDouble
file. The initial mutable draft already contains 105 AppleDouble entries.
Consequently, an incomplete bundle or a metadata-polluted bundle can receive a
publication `ACCEPT` if its self-selected manifest lists exactly those bytes.

No runtime, campaign, cryptanalytic, or ECDLP conclusion follows from this
review.

## Scope and method

- Primary bytes were inspected directly. No prose status was treated as proof.
- No builder, regression writer, cleanup, copy, manifest generator, or full
  verifier command was run. The full verifier writes
  `local-verification-v13.json`, so running it would have violated the
  read-only instruction.
- Read-only early-exit replay modes, digest checks, manifest checks, and the
  publication verifier were used. Three additional adversarial universes were
  generated only in process memory and sent through `/dev/stdin`; no fixture or
  work file was created.
- The decision covers only immutable staging of this finite-model V13
  map-slice draft.

## Initial pre-review filesystem state

These counts preserve the defects as first observed, before this review file
was added:

| Item | Exact count |
|---|---:|
| Regular files | 334 |
| Directories, including the root | 31 |
| Symlinks | 1 |
| AppleDouble names `._*` | 105 |
| Top-level AppleDouble names | 19 |
| Non-AppleDouble regular files | 229 |
| Top-level non-AppleDouble regular files | 26 |

The AppleDouble distribution was: map work 14 of 28 files; meta/publication
work 7 of 18; reap work 16 of 32; semantic work 30 of 60; spawn work 19 of 38;
and top level 19. The evidence tree had 113 regular files and zero AppleDouble
names. The sole symlink was the intentional negative fixture
`meta-publication-regressions-v13-work/symlink-bundle/alias`, targeting
`real`. The intentional unlisted-file fixture was
`meta-publication-regressions-v13-work/unlisted-bundle/UNLISTED-PAYLOAD.bin`.

There was no top-level V13 `SHA256SUMS`, external V13 root marker, V13
publication receipt, or V13 checkpoint decision. Git reported the entire draft
as untracked. These facts are compatible with a mutable draft, but they mean
there is no immutable V13 object to attest yet.

## Byte anchors

All hashes are SHA-256 over the inspected primary bytes.

| Artifact | SHA-256 |
|---|---|
| `build_v13_closed_kernel.mjs` | `3d2fa72e727bd8ef9b7f120f26d686a62784463a603105648cb50e67acc45319` |
| `verify_v13_closed_kernel.mjs` | `a92081c6eaf2f41fa9a0464bd88374567a129ee71f02e65df78809afcf821588` |
| `selector-rules-v13.json` | `2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383` |
| `supervised-executor-closed-kernel-v13.json` | `2fad25acea1158a018d74153c6093ffe4451d05507f1ba666462283c61ab7919` |
| `local-verification-v13.json` | `1e544369f71f0eca6c87c248c55ed325d5e998d8b093b3c5ed6149a66568efbe` |
| `mandatory-regressions-v13.json` | `98611e1d4f9960e790b31e46727e5a9d36778ffb421829fbe81527566a41ad83` |
| `semantic-regressions-v13.json` | `20fe69098fc3285f814c0c9e88c7f112961ba11ec5d4ce11ad08c3bbf1562ea5` |
| `spawn-failure-regressions-v13.json` | `86e9dfbb1e6e84d4ba09a1f9e5a6bf65ac1f31e7b4cc56de3e05bf5e181d1ec8` |
| `reap-failure-regressions-v13.json` | `62a3d51df9e1f5a7befbbf281a7e88a4f86fa19b09531bf3567709e1a1c5d435` |
| `map-failure-regressions-v13.json` | `b3999152dede99fc4bd69b5b5778df48cae73747e5321841e29e02a106502dc0` |
| `meta-publication-regressions-v13.json` | `4334393fd02b30aaf52ad6cb3580c19bf06ea9e8ebab146f75b387d9a8ad6a0d` |
| `verify_publication_v13.mjs` | `7b02b258fdd09f9418ff2f55ea267ea63cde7f610725ab0d9a072ec7074f170f` |
| `supervised-executor-contract-v13.md` | `067a1c70426704e2a1b4ee148e06da842e297488367da21aa2b955ea4c23aa49` |
| `supervised-executor-topology-decision-v13.md` | `2a79194f428d5c399c3deb356f05430c6bfe5c64b297053fff2408e1ba1d1247` |

The mandatory-regression pin was accepted independently at
`98611e1d4f9960e790b31e46727e5a9d36778ffb421829fbe81527566a41ad83`.
Its exact registry is 70 inherited controls plus 14 V13 map controls, 84 of 84
marked complete. Its own gate correctly retains
`publication_pass: false` and `pass: false`.

## Finite-model evidence that survived attack

Both replay implementations accepted every stored positive universe with the
stored journal count and universe digest: 10 of 10 validator/trace runs.

| Trace | Steps | Final records | Final-universe SHA-256 | Final-journal SHA-256 |
|---|---:|---:|---|---|
| `SEC13-TRACE-A0-END-TO-END` | 119 | 255 | `a1680f9434930ecbd34abc93560bf9e7f513bdbc3e788cb51df36e978af15bd6` | `6fce75028de44925ebf6d3e7ebd9bf346e8e381e13d0aca4d01b51d00e01abf6` |
| `SEC13-TRACE-A2-END-TO-END` | 120 | 268 | `6aafc3ba23d2c8e9222866ace80c84ed423f8133a13742333d4ab1beb4ef8548` | `79ee385262d84d3e96aba03a87ddb114c993cabf0ff8c2ab202fae19058c8e23` |
| `SEC13-TRACE-P0-SPAWN-FAILURE` | 36 | 81 | `0e0c59d721d3e3ca6782a6e39a32ff559ad070a5049ce9e58d31940727fbd09b` | `b5a74f10517c1ed7a6bb1f221172fda976354c253cbcd1d4b755b1d1026a6225` |
| `SEC13-TRACE-P0-RUNTIME-FAILURE` | 38 | 84 | `3b53743e2b23ea44980ec95db9859742da3d51f38c6551d2f476e18e35629542` | `b1ca74b0f03a7b5f0d574dec41f4ccdab39cdb99dacb86e2a8914620714d12fd` |
| `SEC13-TRACE-E0-MAP-FAILURE` | 109 | 239 | `436c8065595bfb8a6b7954f4c0cf33d0ba55b58afa0def642b7c347cbcbdabb6` | `aede40018877465b5ee8cae7de40e73a3794960c09bbc4018c23a532662a2eff` |

The aggregate is exactly 422 journal transitions and 927 final records.

For the map-failure trace, the exact local chain is:

- P001 action receipt
  `441185d85d540f86299e0708996e1adff2c743b3f75145c3af9377d5098c329a`
  writes the sole intent
  `1858feff1c613f1616af900029c24735ebd9a247b4b5b62c31ce661952b30759`.
- Gateway observation receipt
  `cf14a0f69512cf0ddd8aa523edb11aaf21cc8982a8bee6e500375a6e720fb9b2`
  binds that exact request and subject and carries the sole failed-map domain
  record
  `2e9fa6142444c56c8d691ce1f8af92df12f9274f47678dab9ceaefe37eef9009`.
- P003 action receipt
  `54016da666b4abc87ea474f4335105388e28ce59d31136afa070c0ee18ae3431`
  has exactly one domain record, terminal
  `33470eba108847629244b15a93e6341835c4ab7e547ff97fdf08e2b323f3b152`.
- G000 has four domain records on this branch because it conditionally adds
  the previously absent E0 `ref_observation_pre`
  `38d0500cb4b4555bc940c07af195e456e6d5e31c6387a5b3e9b9ff652642e761`.
  Ordinary paths have a prior P006/AN008/AE008 ref observation and G000 has
  three domain records.
- The E0 committed record is
  `9c5691c7bb18f0a3df50f2e60e266784c7d5545323f4ff58056a340e24743dd4`;
  all seven phases are committed, closure completes, and replay terminates at
  `LOCK_RELEASED`.

The current receipts and inputs were not stale: 18 local-verification byte
snapshots, four additional meta snapshots, and all 79 stored mutation input
hash/count/universe tuples matched current bytes with zero mismatches. All 79
inputs replayed through both reducers, giving 158 of 158 exact stored
decision/rejection/exit-code matches. The suite split is 30 semantic, 19
spawn, 16 reap, and 14 map mutations; the remaining five mandatory controls
are meta/publication controls.

The 14 map controls cover wrong request, wrong subject, empty/null context,
value/domain mismatch, invalid value, wrong domain request, cross ordinal,
cross intent, observation after close, P001 self-authorship, producer-label
forgery, duplicate consumption, and missing consumption. Descriptor-token and
opened-receipt-over-failed-map controls also reject in the semantic suite.

Three independent in-memory controls sharpened gaps in the stored suite:

| Control | Input SHA-256 | Universe SHA-256 | Builder/verifier result |
|---|---|---|---|
| Force P002 immediately after the valid P001 wait prefix | `5247477dc775ac54fd36ec0fbc809bb82e400becc398e4019c8cae631a2aca69` | `bd97cefa8f9d0f919321f9a5fdf5a992b52c852f94988e66b493aeccc38d0a38` | both `ACTION_EXECUTED_WHILE_NOT_READY` |
| Add a valid E0 ref-pre record to the P003 domain | `75cf817b4e5ea4a7c75b0802f6ef1448243d6f53858540fbcfdd92f10f6cbeb7` | `c60fbe95bd882febaea000c99771849d96e0c05e896fe6ac83d1f7ef0e7f75ab` | both `ACTION_RECORD_MISMATCH` |
| Bind a typed map observation to an `E0:close_prior_failure` reservation | `9ecda1a045fe92e2573b62e7e417ce3d64e8cbd0f5841a7e711e3296ca1e00ba` | `bd550841821cd88b106f85508572b852344004510b6b066f7cae33d3ba546522` | both `PRIVATE_MAP_OBSERVATION_INVALID` |

These in-memory inputs were not persisted and therefore are observations in
this review, not mandatory immutable fixtures.

## Risk list

### RT-V13-01 — Critical: publication completeness is self-selected

`verify_publication_v13.mjs` accepts any exact manifest/directory pair. It has
no V13 required-path list, no required payload count, and no pin to the 84-case
mandatory registry or the independent reviews. Its clean positive control was
re-run read-only and accepted a bundle containing exactly one payload with
manifest root
`b6fe349dcce9e08417b7b69a3aa83c386513f7baca3af2aeb4079356a187cde5`.
Thus exact manifest equality proves only that the manifest describes the
directory; it does not prove that the directory is a complete V13 checkpoint.

The verifier is byte-identical to V12's generic publication verifier at
`7b02b258fdd09f9418ff2f55ea267ea63cde7f610725ab0d9a072ec7074f170f`.
Reusing it is not itself wrong, but calling its bare `ACCEPT` V13-complete
would be wrong.

### RT-V13-02 — Critical: listed AppleDouble bytes are accepted

The verifier rejects an unlisted file and rejects any encountered symlink, but
it does not reject names such as `._*` or `.DS_Store`. If such a regular file
is included in `SHA256SUMS`, directory equality and digest replay accept it.
This is not hypothetical metadata exposure: 105 AppleDouble entries were
present initially. A recursive manifest generator could therefore freeze the
pollution instead of detecting it.

The intentional symlink and unlisted fixtures are safely rejected when their
fixture roots are checked (`EVIDENCE_PATH_COMPONENT_SYMLINK` and
`PUBLICATION_DIRECTORY_MISMATCH` respectively). They remain a staging hazard
because no V13 payload policy explicitly excludes every `*-work/` directory.

### RT-V13-03 — High: mandatory regression completeness is not publication completeness

The mandatory manifest is correctly byte-pinned and records 84 of 84 complete,
but its publication gate is false. It names controls, not the complete V13
publication payload. A truncated staging directory can omit the mandatory
manifest, builder, verifier, evidence, or this review and still receive the
generic publication verifier's `ACCEPT` if its manifest omits the same files.

### RT-V13-04 — Medium: producer authority is syntactic

Both reducers reject a record whose `producer` string is changed to an
unauthorized role. They do not authenticate who created bytes bearing the
allowed `observation_gateway` string. An adversary able to rewrite and rehash a
whole modeled universe can claim that label. The valid statement is therefore
schema-level producer separation inside replay, not OS-level or
cryptographically attested producer identity.

### RT-V13-05 — Medium: parity is exact but independence is bounded

Builder and verifier are distinct byte sequences and showed exact parity on
the inspected positives and mutations. They share the same selector, finite
record vocabulary, assumptions, fixtures, and conceptual design. The local
verification receipt is generated by the verifier itself and remains mutable.
This establishes differential replay agreement, not independent provenance or
formal correctness. The two parity meta-controls are deliberate comparator
fault injections, not naturally discovered disagreements.

### RT-V13-06 — Medium: first rejection is not causal necessity

The mutation receipts explicitly say downstream selector sources/actions were
not causally regenerated and secondary rejection causes can remain. Exact
first-rejection parity is useful, but it does not prove that the named
invariant is the only reason the mutated campaign fails. Late duplicate and
missing-consumer controls reject as registered; stronger prefix-local causal
fixtures remain appropriate before freezing the interpretation.

### RT-V13-07 — Medium: future stale-request scope remains open

Within the current one-E0 canonical path, the unique durable path for the map
intent plus journal replay prevents a second accepted P001 intent, and exact
request/subject binding rejects the inspected wrong, cross-intent, and
cross-ordinal cases. That is not evidence for typed restart or a future model
that retains multiple same-rule requests across attempts. Restart and process
reconciliation remain outside V13.

### RT-V13-08 — Low: lineage is currently valid but externally dependent

All 18 evidence-manifest pins matched. The embedded V9 rejected snapshot,
review bundle, and local-counterexample roots independently verified at 99,
36, and 54 payloads. The live V11 and V12 predecessors independently verified
at 172 and 202 payloads, with manifest roots
`9f29dac6a7dcecae6bad22c75bc034276b13155039b38fab8b17a667d883709d`
and
`98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da`.
The copied V11/V12 root markers and publication receipts matched the live
copies. However, V13 embeds selected predecessor markers/receipts rather than
the complete V11/V12 roots, so long-term replay still depends on those external
immutable roots remaining available unless staging makes that dependency
explicit.

## Overclaim corrections

- Replace “gateway-authored observation” with “a replay-valid record carrying
  the gateway-only producer label”; OS truthfulness and producer
  authentication are unproved.
- Replace “P002 is unreachable” with “P002 was absent from all five positive
  traces, and both reducers rejected a forced P002 action at the canonical
  post-P001 wait prefix.” This is not selector-space totality or a theorem over
  future restart state.
- Replace “both reducers prove the boundary” with “both reducer
  implementations agree on the inspected finite universes and registered
  mutations.” Shared defects remain possible.
- Do not convert 84 complete controls into publication readiness. The current
  mandatory and publication gates themselves remain false.
- Preserve `MODEL-BOUND`, `ZERO-RUN`, and `NOVELTY-UNVERIFIED`. No process was
  spawned, no private map was opened, no filesystem/Git durability was tested,
  no campaign was authorized, and no ECDLP evidence was produced.

## Required controls before a future staging GO

- Bind publication verification to a pinned V13 payload policy containing the
  exact required relative paths and exact expected count. Missing any required
  artifact must reject even when the truncated directory exactly matches its
  own manifest.
- Reject AppleDouble, `.DS_Store`, symlinks at every path component, special
  files, unlisted files, duplicate paths, and every excluded work directory as
  policy violations, not merely as accidental manifest mismatches.
- Require zero AppleDouble and zero symlink counts in the candidate stage,
  explicit exclusion of all five `*-work/` trees, source-to-stage byte equality
  for every allowed payload, a separately stored external root, and exact
  manifest replay after all writers have stopped.
- Persist and register the forced-P002, active-E0-close observation, and
  P003-extra-domain controls, plus missing-mandatory-payload and
  listed-AppleDouble publication counterexamples. Their hashes and expected
  first rejections must be included in the revised mandatory and publication
  policy bytes.
- Include this initial `NO_GO` review unchanged in any repaired staging bundle
  so the defects and repair lineage are not erased.

## Residual limitations

- The full verifier was not executed because it writes an existing receipt.
  Positive and mutation replay branches were executed read-only, and current
  snapshot hashes were checked independently.
- No exhaustive selector-state search, rule-totality proof, restart model,
  process reconciliation, crash model, OS witness, or filesystem durability
  test was performed.
- The draft was mutable and shared. The hashes above identify only the bytes
  observed during this review; any later byte change requires a new review or
  an explicitly versioned repair attestation.
- The publication defect is sufficient for `NO_GO`; unfinished broader checks
  are not interpreted as passing.

## Handoff: V13 map-slice immutable-staging red team

### Claim or task

Determine whether the current mutable V13 typed E0 private-map draft is ready
to be copied into an immutable map-slice checkpoint.

### Status

`NEGATIVE RESULT`

Decision: `NO_GO` for immutable V13 map-slice staging.

### Assumptions

- The reviewed scope is the finite event-sourced model and exact hashes above.
- V11 and V12 live predecessor roots remain the external objects verified in
  this review.
- Runtime, OS, durability, campaign, cryptanalytic, and ECDLP claims are
  excluded.

### Evidence so far

- Five positive traces, 422 transitions, and 927 final records replayed with
  exact builder/verifier parity.
- Seventy inherited plus 14 map controls are complete in the pinned mandatory
  registry; 158 of 158 read-only mutation replays matched their stored exact
  decisions.
- Three additional in-memory controls rejected P002 residual action,
  P003 extra domain, and typed-map observation over E0 close mode under both
  reducers.
- Publication verification accepted a one-payload bundle and has no V13
  required payload set/count; 105 AppleDouble entries existed initially and
  listed AppleDouble files are not forbidden.

### Failure modes

- A truncated, self-consistent manifest can be called a publication success.
- A metadata-polluted manifest can freeze listed AppleDouble files.
- Syntactic producer labels can be forged outside the finite model.
- Shared builder/verifier assumptions and non-causal mutation relinking can
  hide a common defect.
- Future restart state can invalidate the present one-request reasoning.

### Next concrete action

Produce one clean candidate staging directory from a pinned V13 required-path/count policy that includes this review and durable versions of the five missing falsification controls, then run both replay validators and the policy-bound publication verifier against those settled bytes.

### Artifact paths

- `V13-RED-TEAM-REVIEW.md`
- `supervised-executor-closed-kernel-v13.json`
- `mandatory-regressions-v13.json`
- `local-verification-v13.json`
- `verify_publication_v13.mjs`
