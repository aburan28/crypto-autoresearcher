# Independent source review of compact CM implementation 9a2e133099

Task: `TASK-20261016-3d848c`.

Native agent identity: `/root/frontier_coordinator_resume/cm_norm_independent_review`.

Date: 2026-10-16, America/Los_Angeles.

The mathematical acceptance paths and the normal public `construct`/`verify` resource paths hold at the scope of this static review. I found no actionable false mathematical acceptance in those paths. One required control is missing from the published test definitions: the frozen plan names lost/zero RSS acknowledgement, but the compact tests exercise positive RSS only. The control-coverage joint therefore **breaks** as a completeness claim. Add that negative resource control before describing all required controls as implemented and checked.

This is a read-only review of published source and test definitions, not an execution receipt. No tests, installed binaries, mathematical trials, M8191 computation, or benchmarks were run. I did not access the unpushed clean-retake payloads, clean-build directories, live P192 outputs, or their terminal interpretation. I transferred or uploaded no artifact. Repository files were not modified. Only this authorized temporary report was written; the Coordinator owns archival, extracted attestation, diagram/PDF work, and any subsequent implementation or execution decisions.

## Frozen inputs and review scope

The plan was readable at harness commit `00a1d352a0`, at `coordination/goals/GOAL-ISOU-f30a07/compact-m8191-draft/implementation-review-9a2e133099/review-plan.yaml`. Its five joint names are preserved verbatim below. The crypto source under review is commit `9a2e133099eb4b10ed182e25384bd53fca262146`, from `/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015`. The local HEAD was `c6a590ec72d9e65a59df0d4e23a1f3300ec4d11d`; I did not use that later commit's receipt payloads as evidence.

All seven named working-tree files matched the frozen SHA-256 manifest before their source was used:

| File | SHA-256 |
|---|---|
| `tools/isogeny-cli/src/main.rs` | `874b093b0d372e8683399583d1e651fbdfadcde2991d7bcaf48712f822fa1e3a` |
| `tools/isogeny-cli/src/compact_cm.rs` | `b82ff8fec77a12c3e6a2be543a1605c945fbcb715669cc2ab0bd1d42f25dda7d` |
| `tools/isogeny-cli/src/compact_cm_verify.rs` | `277af787edfa8cd11e5d28b461f628afcda6afa88cd14501f625d84b24ef13d4` |
| `tools/isogeny-cli/src/supervisor.rs` | `f81ffdb692486087d7dcc4028b061c040db55e18fdf84eaa1809e8a7d7246b8e` |
| `tools/isogeny-cli/tests/compact_cm_cli.rs` | `1320cf930ee75475c285e7da88358db009513f862ef2c83708de8a01b5ac0445` |
| `docs/identity-certificates/cm-eisenstein-norm.json` | `e9cf2eb2ef3e0e61907169d90355a11e18da9ddd3a7c9a2a4955d79ef49e94a5` |
| `docs/identity-certificates/cm-eisenstein-norm.md` | `3973446d60c21f4c72830b1eab3b73ac990478991df9ebd0db39e815d5aee111` |

Additional dependency, documentation, and test-definition excerpts were read using `git show` at the frozen crypto commit. I explicitly used my own earlier mathematical review, `TASK-20261016-3b4ca9`, as the prior contract. This is continuity with the same reviewer's prior mathematical work, not an additional independent mathematical attestation. No sibling review was read.

The repository's `report-evidence` skill was applied to preserve the distinction between static inspection, implemented controls, executed results, and unresolved requirements. It imposed no additional approval request.

## Actionable finding: missing negative resource control

**[P2] Complete the lost/zero RSS control required by the frozen plan.**

The frozen plan explicitly includes `lost/zero RSS acknowledgement` among its proves-too-much objects. The complete compact integration test, [compact_cm_cli.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/tests/compact_cm_cli.rs:21), checks a successful resource receipt and positive peak RSS at lines 68–81, existing-output refusal at lines 85–96, arithmetic mutations, and evaluator behavior. It does not define a failed RSS-read, zero-RSS-before-release, missing-acknowledgement, or monitor-loss rejection case. The compact verifier unit tests likewise contain mathematical controls but no resource failure injection. A search across the published CLI test definitions found no such resource control.

The affected implementation is the positive-sample filter and ready-file release in [supervisor.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/supervisor.rs:261), the missing-monitor grace path at lines 281–294, and the worker wait at [compact_cm.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm.rs:608). Source inspection supports the normal path, but a positive run cannot check those failure branches. Thus this finding is a concrete missing control definition, not an assertion that an actual monitored run failed.

Fix: provide a controlled RSS-reader/acknowledgement test seam and fixed negative cases. At minimum, persistent `None` or zero RSS before release must withhold acknowledgement, admit no arithmetic work, return a non-PASS outer receipt and nonzero public exit, and retain a censored/resource-failure record. A lost monitor during active arithmetic must reach the stated grace/termination path and must not produce an accepted public receipt. Test the worker's absent acknowledgement without performing a scientific target. Verify that a later valid positive sample permits progress, so the instrument distinguishes missing monitoring from a normal run. These are acceptance-instrument controls, not repetitions of arithmetic implementation details.

The focused source review can be archived now. The completeness claim remains partial until a separate authorized change adds and executes the missing controls. This finding does not change any custody-upload or scientific-execution gate.

## Joint 1: arithmetic_and_primality — holds at static-review scope

The producer implements an odd-prime exponent gate in `compact_cm.rs:107–114`, reconstructs `2^e-1`, starts with state 4, executes exactly `e-2` transitions, and requires terminal zero in `compact_cm.rs:122–159`. Its Mersenne reduction repeatedly folds high bits and subtracts the modulus once the folded value is at most `e` bits. The negative intermediate case when the state is zero is handled by adding the modulus before subtracting two; that remains congruent to the recurrence.

The independent path in [compact_cm_verify.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm_verify.rs:41) independently gates the exponent, reconstructs the degree, checks exponent and transition metadata, and fixes the selected Conrad theorem string. Its loop at lines 65–75 hashes the initial state and every resulting state, with exactly `e-2` general modular recurrence transitions. It compares the recomputed final zero and digest at lines 76–83. It does not trust the reported terminal or digest in place of replay. The producer uses `num_bigint::BigUint` and Mersenne folding; replay uses repository `Int`/`Big` and general division. Their integer implementations and reduction paths are distinct.

The hash framing agrees: a little-endian `u32` index, a little-endian `u64` decimal length, and canonical decimal state bytes. This is a consistent binding convention; the digest is not treated as a primality theorem. Exponent 11 passes exponent primality but fails the M11 recurrence; exponent 9 fails exponent primality; exponent 2 is outside the explicitly documented odd-prime domain. These are correctly distinguished in the code and public test definitions.

Cornacchia production is at `compact_cm.rs:174–208`. The verifier at `compact_cm_verify.rs:86–136` checks normalized nonnegative root, the root congruence, each replayed division equation and remainder bound, the first remainder below the square-root boundary, a nonnegative exact quotient by three, the integer square and equation, transcript count/digest, and the unreduced coefficient transformation. The target primes have the congruence needed for the producer's square-root exponent; the verifier accepts only an actually checked root. Root zero is not a hidden accepted corner: the supported Mersenne degrees are at least seven, and zero fails the root congruence.

No false-accept path was identified in these predicates. The current tests do not explicitly mutate every Cornacchia receipt field; adding root/transcript/square corruption controls would improve coverage, but I found no demonstrated missing arithmetic check from that test omission alone. No numerical acceptance of M8191 is asserted.

## Joint 2: geometric_expression_and_exact_identity — holds at static-review scope

The geometric source and trusted-primality basis are fixed in [compact_cm.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm.rs:10). The domain includes exact p, n, cofactor, generator, curve equation, and source identity. The verifier requires exact equality to that tuple at `compact_cm_verify.rs:279–282`. Its result explicitly labels p/n primality as trusted standardized parameters, rather than claiming self-contained primality certificates. The generator and unique-Hasse-multiple test at lines 349–362 are sufficient under that declared trust basis: n is prime, G is nonzero and n-torsion, and no second positive multiple of n fits the interval. The integer width `floor(sqrt(4p))` gives the correct integer Hasse interval.

Canonical signed parsing is bounded and rejects leading zeroes, negative zero, and nondecimal input. The certificate's a and b are parsed as signed integers and the norm is recomputed directly at `compact_cm_verify.rs:302–309`, before subgroup scalar reduction. Canonical Cornacchia certificates are restricted to a=x+y, b=2y; the evaluator supports general signed expressions. That restriction is explicitly documented and is not silently presented as acceptance of every equivalent signed representation.

The required exact identity is

`(a+b*t)(a-b-b*t) = a*a-a*b+b*b - b*b*(t*t+t+1)`.

The producer expands this into sparse exact integer coefficient maps at `compact_cm.rs:240–305`. Replay uses a separate dense coefficient expansion over `Int` at `compact_cm_verify.rs:138–188`. The verifier first requires the exact recognized statement at lines 287–290, so arbitrary expression trees do not enter that acceptance path as substitute degree theorems. The exact identity check is distinct from the IDC1 check at lines 291–301. The latter remains supplementary finite-field evidence.

My prior review establishes the geometric bridge: primitive cube-root automorphism phi has phi²+phi+1=0, dual(phi)=phi², and dual([a]+[b]phi)=[a-b]-[b]phi. Exact integer expansion therefore gives geometric degree a²-ab+b². Positive characteristic does not reduce these morphism coefficients modulo p or n.

The verifier's beta and lambda congruences, nonzero derivative/product, subgroup scalar, inverse, and norm product are checked at `compact_cm_verify.rs:310–348`. Degree equal to the characteristic is rejected separately. Thus point agreement is not used in place of a degree or separability proof.

The alias test at `compact_cm_verify.rs:499–526` checks point agreement for a+n and recomputes the geometric norm change n(2x+n)>0 before rejecting the old certificate. The exact-integer versus finite-field coefficient-shift control is defined at lines 477–496. Both exercise the intended proof boundary.

## Joint 3: independent_group_replay — holds at static-review scope

The producer uses projective Jacobian scalar multiplication with `BigUint` field operations at `compact_cm.rs:347–432`; final addition uses its affine helper. The independent engine in [compact_cm_verify.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm_verify.rs:189) uses fixed-limb Montgomery field operations, binary extended-GCD inversion, affine group formulas, and least-significant-bit signed scalar multiplication. It does not call the producer's scalar multiplication or geometric evaluator. The shared `BigUint` dependency is used for field setup/conversion, not as the verifier's per-operation field arithmetic or signed scalar backend; this is meaningful implementation diversity, not complete absence of shared infrastructure.

Range and on-curve checks occur before independent point decoding at lines 199–210. Infinity, negation, vertical-pair addition, doubling with y=0, and zero scalar handling follow the expected group cases in lines 224–260. `Int::bits()` uses the magnitude, so negative scalar iteration is consistent with the explicit base negation.

Full-point beta/lambda pairing is checked at lines 363–368. The expected input set is independently reconstructed as O, G, -G, 2G, 3G, 17G, 101G, 65537G at lines 369–376. Exact vector length, ordered inputs, and full output encodings are checked; a shortened, duplicated, or changed fixed input set is not silently accepted.

The replay loop at lines 380–403 checks on-curve output, independent geometric evaluation, separately reduced subgroup action, both dual compositions, and a group-law relation. None of these fixed-point diagnostics claims global degree identification. The producer's geometric evaluator validates the supplied point and uses the original signed coefficient magnitudes with explicit sign handling at `compact_cm.rs:348–449`.

Signed and zero fixtures and off-curve producer rejection are defined at `compact_cm_verify.rs:450–474`. The alternate-beta acceptance/wrong-pairing rejection test at lines 529–556 updates the associated derivative, scalar, inverse, and outputs, ensuring that the pairing check itself is reached rather than an earlier stale-metadata guard. No test pass or complete audit of the pre-existing integer/field libraries is asserted by this source review.

## Joint 4: resources_fresh_outputs_and_byte_binding — holds for normal public construct/verify paths

The normal public wrapper is [compact_cm.rs](/Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm.rs:641). `construct` and `verify` enforce positive bounded timeouts, require a fresh output directory through `create_dir`, construct their own worker argv and artifact subdirectory, and invoke the supervisor. Existing outer output directories are rejected before the generic supervisor's sealed-receipt reuse branch can be reached by these public operations. The worker also requires a fresh artifact directory.

The supervisor identifies the compact worker at `supervisor.rs:235–244`. Before release, zero RSS is filtered out at lines 261–263, and only a usable positive sample creates the ready file at lines 272–279. The worker waits for that file before invoking the operation at `compact_cm.rs:612–623`. Persistent monitor failure follows the bounded grace/kill path at `supervisor.rs:281–294`; timeout and sampled memory excess have separate terminal states. The ready-done marker is created after the operation returns, including caught operation failure, before the worker exits. The supervisor stops RSS sampling after that marker but retains its wall watchdog; the memory envelope is sampled, not an operating-system hard limit.

Acceptance at `supervisor.rs:313–353` requires successful child exit, a parsed PASS status, and no recorded timeout, memory excess, or unavailable-monitor failure. The public wrapper uses that outer receipt at `compact_cm.rs:696–730` to select its exit/result. A non-PASS resource outcome cannot be elevated by a successful-looking inner mathematical record. I found no direct internal-worker invocation that, by itself, creates or satisfies the strict public outer resource receipt.

The public verification path reads at most 2 MiB plus one byte, rejects excess input, and parses, verifies, and hashes the same retained byte vector at `compact_cm.rs:537–548` and `571–586`. It does not hash a later reopen of the input. This closes the relevant parsed-bytes/hash mismatch. The worker stdout/stderr hashes are separately recorded by the supervisor. Construction copies and hashes the resulting certificate bytes after outer success at lines 712–715.

Two precise scope limitations remain:

- `compact-cm __worker` is reachable from ordinary dispatch and checks only for the existence of its ready file. A caller-provided existing ready file can reach arithmetic without a supervisor. This is a reachable internal unprotected path and a limit on claims about all invocations. It is **not** a demonstrated public scientific-admission bypass: such an invocation supplies no qualifying outer resource receipt and does not match the frozen public scientific argv. If a broader future claim requires every callable entry point to enforce monitoring, replace the path-only acknowledgement with a parent-owned IPC channel and reject direct worker entry. No such broader gate is invented here.
- `evaluate` deliberately bypasses the constructor/replay supervisor at `compact_cm.rs:641–644`, even though it re-verifies the entire certificate at lines 589–599. The README explicitly documents that the watchdog applies to `construct` and `verify`. Treat evaluation's resource scope accordingly; this is intentional documented behavior, not a newly asserted defect.

The missing negative resource controls are reported separately above. Static tracing of this normal path does not substitute for executing those controls.

## Joint 5: control_coverage_and_claim_limits — breaks as complete-control coverage

The published source defines the principal mathematical controls: low-degree positive rungs, distinct e11/e9/e2 rejection, altered norm/degree/beta/derivative/subgroup fields, altered LL metadata/digest, exact-Z coefficient errors including the evaluation-modulus alias, signed/zero expressions, the subgroup-order degree alias, wrong pairing with updated scalar metadata, and acceptance of the other primitive beta with its corresponding lambda. The CLI integration source also defines fresh-output refusal, positive measured RSS, eight point rows, separate evaluator agreement, and invalid point rejection.

However, it contains no lost/zero RSS rejection control named by the frozen plan. Consequently, the claim that the fixed required controls are complete cannot hold at this source snapshot. This is the [P2] finding, with a specific repair and expected outcomes above. The inspected definitions also do not justify saying any tests passed, because this task deliberately ran none.

The scope language in `docs/identity-certificates/cm-eisenstein-norm.md` and the compact README is otherwise accurate: trusted SEC2 p/n, exact integer identity versus evaluated supplement, canonical Cornacchia certificate schema versus signed evaluator, Frobenius and 1-Frobenius as theorem-level controls outside this executable input schema, compact representation separate from expanded maps, and no M8191 instance established by implementation controls. The verifier emits null expanded-map score and `scientific_promotion:false` at `compact_cm_verify.rs:405–406`. I found no code path silently promoting the compact result to the full-map board.

## Recommendation and remaining obligations

Archive this focused source review and correct the missing negative resource control before asserting complete control coverage. The static mathematical implementation findings do not require changing the reviewed norm theorem or adding Gross-specific intermediate GCD requirements; the selected standard Lucas–Lehmer contract is Conrad Theorem 2.2.

Any changed source needs its normal verification and a new frozen source identity. The later M8191 execution remains a separate frozen `/run` with its own resource receipts and independent replay. This report gives no scientific execution approval, no actual target result, no release-asset claim, no custody-upload authorization, and no official-state transition. The user's pending custody approval and all prior gates remain unchanged.

## Review attestation

The following YAML has one allowed verdict enum per exact joint name. Extract it into the Coordinator-owned attestation YAML before running `tools/check_review_independence.py`, which reads YAML documents rather than Markdown fences. No checker composition, unit test, integration test, or binary run was executed in this review.

```yaml
review_attestation:
  task_id: TASK-20261016-3d848c
  native_agent_identity: /root/frontier_coordinator_resume/cm_norm_independent_review
  native_agent_session_id: unverified_not_exposed
  review_kind: pinned_source_implementation_correctness
  source_commit: 9a2e133099eb4b10ed182e25384bd53fca262146
  plan_commit: 00a1d352a0
  joints_owned:
    - arithmetic_and_primality
    - geometric_expression_and_exact_identity
    - independent_group_replay
    - resources_fresh_outputs_and_byte_binding
    - control_coverage_and_claim_limits
  verdicts:
    arithmetic_and_primality: holds
    geometric_expression_and_exact_identity: holds
    independent_group_replay: holds
    resources_fresh_outputs_and_byte_binding: holds
    control_coverage_and_claim_limits: breaks
  verdict_scope:
    arithmetic_and_primality: Static source acceptance predicates only; no concrete M8191 certificate or test execution.
    geometric_expression_and_exact_identity: Exact source tuple with declared SEC2 trust, integer norm, independent exact identity, derivative and subgroup gates.
    independent_group_replay: Independent implementation paths and complete fixed-point definitions; not an executed replay or full dependency proof.
    resources_fresh_outputs_and_byte_binding: Normal public construct/verify path only; direct worker and documented evaluate exclusions are explicit.
    control_coverage_and_claim_limits: Required lost/zero RSS negative control absent from public test definitions; mathematical and representation claim limits otherwise hold.
  sources_read:
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/compact-m8191-draft/implementation-review-9a2e133099/review-plan.yaml
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/coordination/goals/GOAL-ISOU-f30a07/compact-m8191-draft/implementation-review-9a2e133099/source-files.sha256
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/ledger/handoffs/TASK-20261016-a82f9e.yaml
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/AGENTS.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/agents/validator.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/templates/research-records.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/check_review_independence.py
    - /private/tmp/isou-cm-independent-review-final.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/AGENTS.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/.agents/skills/report-evidence/SKILL.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/main.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/compact_cm_verify.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/supervisor.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/tests/compact_cm_cli.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/README.md
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/Cargo.toml
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/tools/isogeny-cli/src/verification_field.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/isogeny_algos/src/int.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/isogeny_algos/src/bigint.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/src/cryptanalysis/identity_certificate.rs
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/docs/identity-certificates/cm-eisenstein-norm.json
    - /Volumes/SSD990-2/crypto/isogeny-degree-challenge-20261015/docs/identity-certificates/cm-eisenstein-norm.md
  sources_read_scope:
    frozen_manifest_files: Seven SHA-256 matches verified; relevant full compact implementation and test definitions read.
    main_rs: Dispatch, module wiring, option parsing, provenance, main exit handling, and compact diff.
    supervisor_rs: Full source read.
    supporting_arithmetic: Relevant pinned conversion, signed magnitude, modular division, square-root, field setup, multiplication, inversion, and IDC definition/check excerpts.
    additional_cli_tests: Text search for compact/RSS/handshake/monitor cases across published test definitions only.
    crypto_AGENTS: Opening rules and relevant bounded excerpts/searches; full large file output was truncated.
    prior_harness_instructions_and_checker: Read earlier in this same native reviewer session and explicitly reused; no sibling review.
    prior_mathematical_report: This same reviewer's TASK-20261016-3b4ca9 report and selected theorem correction; relevant excerpts reread.
  source_provenance:
    implementation_and_plan: internal
    verified_by: /root/frontier_coordinator_resume/cm_norm_independent_review
    external_mathematics: Prior same-reviewer report whose primary-source retrieval is explicitly recorded there.
  read_sibling_reports: false
  blind_from_respected: true
  restricted_clean_retake_payloads_read: false
  live_p192_outputs_read: false
  producer_source_read: true
  producer_run_receipts_used: false
  own_prior_review_used: TASK-20261016-3b4ca9
  requested_policy: review-adversarial
  requested_effort: xhigh
  actual_served_model: unverified_not_exposed
  actual_served_effort: unverified_not_exposed
  provider_or_api_substitution_used: false
  test_or_isogeny_binary_execution: false
  scientific_runs_launched: false
  repository_modified: false
  artifacts_uploaded_or_transferred: false
  recommendation: Archive static review and add the missing negative resource controls before asserting complete coverage.
  scientific_execution_approval: none
  custody_gate_change: none
  official_state_transition: none
```
