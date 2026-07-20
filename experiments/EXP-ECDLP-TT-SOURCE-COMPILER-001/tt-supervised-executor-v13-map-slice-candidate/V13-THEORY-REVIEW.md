# V13 Theory Review: Typed E0 Private-Map Observation

Decision: `GO_FOR_IMMUTABLE_V13_MAP_SLICE_STAGING`

Claim status: `RESTRICTED THEOREM` for the finite-model statements below;
`OBSERVATION` for byte checks and replay results. The reviewed artifact remains
`MODEL-BOUND`, `ZERO-RUN`, and `NOVELTY-UNVERIFIED`.

This is a GO only to construct and verify a separate immutable V13 map-slice
staging root from the reviewed bytes. It is not a publication-accept receipt,
runtime or implementation authorization, campaign authorization, cryptanalytic
evidence, or an ECDLP claim. It is not permission to freeze the mutable draft
directory wholesale.

## Reviewed byte anchors

The following SHA-256 values were computed independently from the primary
files during this review:

| Artifact | SHA-256 |
|---|---|
| V12 immutable `SHA256SUMS` | `98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da` |
| V12 external root pointer | `f94cd06038c0d10057f997194fcf13e85ffd82970eb459d884b610c917dc740c` |
| V12 publication receipt | `c17390b33fbcc5f7f9e6f37056e97a1a43ad0788ad1bdab950448606c4b99bc0` |
| V12 decision receipt | `697b5c59ef8fcfb585f0aa17a0a5803d0c505a2510c6ad24d22d898b34a4e406` |
| V12 Theory review | `5f38f3ffe5c43b8b428daeac5eff462927099252ab4351544b6dcc855b40197c` |
| V12 Red Team review | `cb26483751119576d63f46c4109562ae308f85bbfe860ce8e7593c2552740bf5` |
| V13 selector | `2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383` |
| V13 builder | `3d2fa72e727bd8ef9b7f120f26d686a62784463a603105648cb50e67acc45319` |
| V13 independent verifier | `a92081c6eaf2f41fa9a0464bd88374567a129ee71f02e65df78809afcf821588` |
| V13 closed kernel | `2fad25acea1158a018d74153c6093ffe4451d05507f1ba666462283c61ab7919` |
| V13 mandatory controls | `98611e1d4f9960e790b31e46727e5a9d36778ffb421829fbe81527566a41ad83` |
| V13 local verification | `1e544369f71f0eca6c87c248c55ed325d5e998d8b093b3c5ed6149a66568efbe` |
| V13 contract | `067a1c70426704e2a1b4ee148e06da842e297488367da21aa2b955ea4c23aa49` |
| V13 topology decision | `2a79194f428d5c399c3deb356f05430c6bfe5c64b297053fff2408e1ba1d1247` |
| V13 map-control receipt | `b3999152dede99fc4bd69b5b5778df48cae73747e5321841e29e02a106502dc0` |
| V13 meta/publication-control receipt | `4334393fd02b30aaf52ad6cb3580c19bf06ea9e8ebab146f75b387d9a8ad6a0d` |

### V12 lineage observation

The external V12 root was independently accepted by the publication verifier.
All 202 manifest payloads passed `shasum -a 256 -c`, with zero failures, and
the actual `SHA256SUMS` digest equals the claimed immutable root above. The six
V12 lineage files embedded in V13 are byte-equal to their external V12
counterparts. The V12 and V13 selector files are also byte-equal, both are
455,786 bytes, and both hash to the required selector anchor. The conserved
selector reports 153 rules, 179 partitions, and 1,584,249 symbolic cases.

## Finite model and definitions

Let `M13` be the deterministic event-sourced reducer defined by the reviewed
builder and independently reimplemented verifier bytes, with:

- canonical record bytes and SHA-256 links;
- the closed record-schema and producer-authority registries;
- journal sequences replayed from sequence zero in canonical path order;
- selector inputs derived only by the reviewed `deriveKernelSource` /
  `reconstructNext` functions;
- one active E0 evaluate reservation in the canonical traces; and
- acceptance requiring both semantic-universe validation and exact
  journal/state replay.

A *P001 request pair* is the P001 `action_receipt` together with the sole
`private_map_open_intent` in that receipt's domain. A *map observation
consumer* is an `observation_receipt` whose domain contains the corresponding
`private_map_open_observation` digest.

## Restricted theorem: scoped typed E0 map observation

Within `M13`, every accepted canonical E0 evaluate path that progresses beyond
P001 has exactly one request-bound, intent-bound, gateway-authored private-map
observation with one of the two finite observed values `map_opened` and
`map_open_failed`. The success branch can select P004; the failure branch can
select P003; P002 is not canonically reachable. This statement is limited to
the accepted finite model and does not assert that the gateway reports an OS
event truthfully.

### Proof sketch and obligations discharged

1. **P001 request/intent binding.** P001 emits one
   `private_map_open_intent`; its action receipt has the same sequence and
   contains that exact digest. Observation construction and semantic audit
   require the observation's `request_action_receipt_sha256` to identify that
   P001 receipt and `open_intent_sha256` to identify that intent. Journal replay
   independently requires the observation receipt's request and subject to be
   the same pair.

2. **`WAIT(private_map_open)`.** Once the intent exists and no map observation
   exists, both reducers return `kind: wait`, context `e0_private_map`,
   observation kind `private_map_open`, with the P001 receipt as request and
   the intent as subject. An independently constructed, otherwise journaled
   P002 action immediately after P001 was rejected by both reducers as
   `ACTION_EXECUTED_WHILE_NOT_READY`.

3. **Authority and finite values.** The closed registry assigns
   `private_map_open_observation` only to `observation_gateway`; producer
   substitution is rejected. Observation construction accepts exactly
   `map_opened` or `map_open_failed`, mapping these respectively to
   `(outcome="opened", descriptor_token="private-map:<ordinal>:E0")` and
   `(outcome="open_failed", descriptor_token=null)`. Other receipt values and
   inconsistent domain values are rejected.

4. **P002 canonical unreachability and no-domain semantics.** The inherited
   P002 selector row requires `event=open_syscall_success` while the map state
   is `MAP_OPEN_INTENT_DURABLE`, and its action-domain type list is empty.
   Canonical derivation instead waits before any observation, emits
   `open_syscall_failure` after a failed observation, and emits
   `publish_opened_receipt` with state `MAP_OPENED_UNRECEIPTED` after a
   successful observation. It therefore never derives P002. This does not
   remove P002 from the conserved selector or prove it unreachable under an
   unmodeled source-provider interface.

5. **P003 terminal-only behavior.** The P003 action-domain type list is exactly
   `[phase_terminal]`. Its constructor emits one E0 `phase_terminal` with
   `event_kind=map_open_failure`, `outcome=TERMINAL_HARNESS_FAILURE`, and the
   failed observation as predecessor. Exact action-domain replay rejects extra
   or substituted outputs.

6. **Conditional G000 pre-ref observation.** Ordinary phase routes already
   contain `ref_observation_pre`, so G000 emits its usual three records:
   `git_blob_object`, `git_tree_object`, and `commit_intent`. The P003 route
   enters repository validation without P006; only there, G000 conditionally
   prepends one `ref_observation_pre`. Across the stored positives I observed
   24 ordinary three-record G000 actions and exactly one four-record G000
   action, the E0 map-failure commit at sequence 99.

7. **Exactly-one-consumer semantics.** Every map domain observation is required
   to occur in exactly one map observation receipt. Request and subject sets
   reject a second consumption as `MAP_OBSERVATION_REUSED`; the registered
   duplicate control confirms this even when the appended duplicate receipt
   deliberately has an empty domain. An observation with its consumer removed
   is rejected as `MAP_OBSERVATION_ONE_SHOT_INVALID`. The deliberate dangling
   receipt policy is also sound in the composed validator: a first, uniquely
   bound map receipt with no domain is not prematurely classified by the
   one-shot scan, but exact journal/state reconstruction requires its one
   observation record and rejects it as `OBSERVATION_RECORD_MISMATCH`. I
   independently constructed this no-domain receipt in memory and both
   reducers produced that rejection.

The proof is a proof about branch structure and acceptance predicates in the
reviewed program bytes. It is not a proof of reducer correctness relative to a
real operating system or of exhaustive security over every possible future
extension.

## Empirical replay observations

Both reducers independently accepted all five stored positive universes and
reproduced their pinned final digests:

| Trace | Steps | Records | Final journal SHA-256 | Final universe SHA-256 |
|---|---:|---:|---|---|
| `SEC13-TRACE-A0-END-TO-END` | 119 | 255 | `6fce75028de44925ebf6d3e7ebd9bf346e8e381e13d0aca4d01b51d00e01abf6` | `a1680f9434930ecbd34abc93560bf9e7f513bdbc3e788cb51df36e978af15bd6` |
| `SEC13-TRACE-A2-END-TO-END` | 120 | 268 | `79ee385262d84d3e96aba03a87ddb114c993cabf0ff8c2ab202fae19058c8e23` | `6aafc3ba23d2c8e9222866ace80c84ed423f8133a13742333d4ab1beb4ef8548` |
| `SEC13-TRACE-P0-SPAWN-FAILURE` | 36 | 81 | `b5a74f10517c1ed7a6bb1f221172fda976354c253cbcd1d4b755b1d1026a6225` | `0e0c59d721d3e3ca6782a6e39a32ff559ad070a5049ce9e58d31940727fbd09b` |
| `SEC13-TRACE-P0-RUNTIME-FAILURE` | 38 | 84 | `b1ca74b0f03a7b5f0d574dec41f4ccdab39cdb99dacb86e2a8914620714d12fd` | `3b53743e2b23ea44980ec95db9859742da3d51f38c6551d2f476e18e35629542` |
| `SEC13-TRACE-E0-MAP-FAILURE` | 109 | 239 | `aede40018877465b5ee8cae7de40e73a3794960c09bbc4018c23a532662a2eff` | `436c8065595bfb8a6b7954f4c0cf33d0ba55b58afa0def642b7c347cbcbdabb6` |

The totals are exactly 422 journal transitions and 927 final records. Every
trace contains exactly one final released lock. Positive rule/observation
counts are P001 = 3, P002 = 0, P003 = 1, P004 = 2,
`map_opened` = 2, and `map_open_failed` = 1.

The mandatory manifest contains 84 unique controls, all marked `COMPLETE`:
70 inherited controls replayed under V13 bytes (30 semantic, 19 spawn, 16
reap, and five meta/publication) plus 14 typed-map controls. In read-only replay
I independently matched the bytes and exact dual-reducer first rejection for
all 79 state-mutation inputs. The five meta/publication controls also
reproduced: both injected decision disagreements yielded
`DECISION_PARITY_MISMATCH`, manifest substitution yielded
`PINNED_REGRESSION_SUITE_MISMATCH`, an unlisted payload yielded
`PUBLICATION_DIRECTORY_MISMATCH`, and an intermediate symlink yielded
`EVIDENCE_PATH_COMPONENT_SYMLINK`. The synthetic clean publication control was
accepted with manifest SHA-256
`b6fe349dcce9e08417b7b69a3aa83c386513f7baca3af2aeb4079356a187cde5`.

`local-verification-v13.json` declares `PASS`; its 551 stored checks all have
status `pass`, all 18 byte snapshots matched current primary bytes, and it
reports five traces, 422 steps, and 30/30 independently replayed artifact
regressions. I did not regenerate this receipt because regeneration would have
modified an existing artifact.

## Objections, limits, and model-escape routes

- **Publication is deliberately open.** The mandatory gate has
  `full_v13_replay_pass=true` but `publication_pass=false` and `pass=false`;
  the kernel has `publication_equality_gate=false` and
  `artifact_freeze_authorized=false`. No V13 immutable root existed during the
  review, so exact final payload equality could not yet be tested.
- **The mutable draft is not itself a valid publication root.** Before this
  review was added, Git showed zero staged paths, zero tracked worktree diffs,
  and 335 untracked paths under the draft. I also observed 105 AppleDouble
  files and one intentional symlink inside the meta-publication work fixture.
  A wholesale directory copy would therefore violate the publication model;
  work fixtures, AppleDouble files, and symlinks must not enter the immutable
  payload set.
- **Byte drift invalidates this decision.** The draft is shared and mutable.
  This GO binds only the hashes listed above plus this review's eventual staged
  bytes. Any changed primary hash requires a new review or an explicit scoped
  reconciliation.
- **Control scope is finite.** The 84 controls establish their preregistered
  first rejections, not complete causal necessity or exhaustive mutation-space
  coverage. The stored mutation harnesses explicitly retain possible secondary
  rejection causes after relinking.
- **P002 survives outside canonical derivation.** A caller that bypasses the
  reviewed state derivation and supplies arbitrary selector sources lies
  outside the unreachability theorem. Removing or versioning the legacy row is
  a separate design choice, not required for this scoped conserved-selector
  claim.
- **Gateway and descriptor truth are assumptions.** A compromised or mistaken
  `observation_gateway` can choose either permitted class. The deterministic
  descriptor token is a model token, not an OS descriptor or proof that a map
  was opened.
- **Outside every checked model here:** process identity at the OS boundary,
  crash atomicity, filesystem durability, producer-key freshness, live Git-ref
  behavior, restart/process reconciliation, infrastructure finalization,
  implementation equivalence, campaign safety, and all ECDLP relevance.
- The existing `supervised-executor-v13-theory-handoff.md` is a
  pre-implementation design handoff whose stated action has already been
  performed; this review, not that stale action line, is the current Theory
  decision.
- The user stopped further audit expansion. No mutable builder, verifier,
  harness, receipt, work directory, evidence file, or manifest was regenerated
  or modified; full immutable-publication verification remains necessarily
  unfinished because the staging root does not yet exist.

## Decision rationale

No scoped invariant defect was found in the typed E0 private-map observation
slice. The model facts support P001 request/intent binding, the intervening
wait, closed gateway authority, a two-value observation domain, canonical P002
unreachability, terminal-only P003, conditional G000 ref observation, and
composed exactly-one-consumer enforcement. The replay evidence agrees under
the two separately written reducers. The remaining objections are precisely
publication-stage or out-of-model obligations, so they prevent a publication
ACCEPT now but do not prevent constructing the clean immutable staging root.

## Handoff: V13 typed E0 map-slice staging

### Claim or task

Stage only the reviewed typed E0 private-map finite-model slice without
expanding the decision to implementation, campaign execution, cryptanalysis,
or ECDLP.

### Status

`RESTRICTED THEOREM`

### Assumptions

- All reviewed primary hashes remain exactly as listed above.
- Canonical source derivation and dual-reducer acceptance define the scoped
  model.
- The independent Red Team decision is obtained over the same final bytes.
- Publication staging uses an explicit regular-file payload set rather than a
  wholesale copy of the mutable draft.

### Evidence so far

- V12 root `98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da`
  verified with 202/202 payloads and exact embedded lineage copies.
- Selector byte equality and required SHA-256 were independently confirmed.
- Five/five positive traces, 79/79 state-mutation controls, five/five
  meta/publication controls, and the two additional in-memory P002/dangling
  probes produced the expected dual-reducer decisions.
- The mandatory inventory is 84/84 complete under V13 bytes; publication
  equality remains false and unstaged.

### Failure modes

- Any reviewed byte changes before manifest construction.
- Work fixtures, AppleDouble metadata, or the test symlink enter the staged
  payload set.
- Builder/verifier decisions diverge or the publication verifier does not
  accept exact directory equality.
- The staging decision is misrepresented as runtime, campaign, cryptanalytic,
  or ECDLP evidence.

### Next concrete action

After an independent Red Team GO over the same bytes, create one clean
immutable V13 map-slice staging root from an explicit regular-file payload
list including this review, generate its external SHA-256 root, and require
`verify_publication_v13.mjs` to return `ACCEPT` before issuing the V13 decision
receipt.

### Artifact paths

- `research/tt-supervised-executor-v13-draft/V13-THEORY-REVIEW.md`
- `research/tt-supervised-executor-v13-draft/supervised-executor-closed-kernel-v13.json`
- `research/tt-supervised-executor-v13-draft/selector-rules-v13.json`
- `research/tt-supervised-executor-v13-draft/mandatory-regressions-v13.json`
- `research/tt-supervised-executor-v13-draft/local-verification-v13.json`
- `research/tt-supervised-executor-v13-draft/verify_publication_v13.mjs`
- `research/tt-supervised-executor-v12-reap-slice-checkpoint/`
- `research/tt-supervised-executor-v12-reap-slice-checkpoint.sha256`
