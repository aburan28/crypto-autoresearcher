# EXP-CRYPTO-5e8beb implementation

Task: `TASK-20260907-6bd7c0`. Specification:
`experiments/EXP-CRYPTO-5e8beb/specification.yaml` (`status: approved`,
`approved_by: coordinator`, `approval_decision_id: DEC-20260907-ff7355`,
`scientific_execution_authorized: false`).

**This directory implements the diagnostic. It runs nothing.** `maximum_runs`
is `0` in both the task handoff and this task's budget; no fixture,
partition, kernel row, transcript, TV or hash in these files has been
computed or evaluated by this task. The only verification performed was
`python3 -m py_compile` on each `.py` file (syntax only, no execution) --
see `implementation-report.yaml`. The specification's own final field,
`launch_gate`, states the specification alone is not a launch authorization;
this README does not change that.

## Protocol-to-code map

| Specification field | Implementing file / function |
| --- | --- |
| `fixture_definition.states`, `prime_partitions.coordinate_feature` | `fixtures.coordinate_feature`, `fixtures.coordinate_cell_sizes` |
| `prime_partitions.generation` (SHA256 rejection Fisher-Yates) | `fixtures.generate_permutation`, `fixtures._digest_int`; independently re-derived in `reference.reference_generate_permutation` |
| `prime_partitions.matching` | `fixtures.build_matched_feature` |
| `prime_partitions.duplicate_rule` | `fixtures.feature_hash`, `fixtures.duplicate_groups` |
| `prime_partitions.extra_controls_per_N` (identity/constant) | `fixtures.identity_feature`, `fixtures.constant_feature` |
| `composite_partitions` (C15 mod3/mod5/identity/constant) | `fixtures.composite_feature` |
| `fixture_definition.representative` | `fixtures.representative` |
| `fixture_definition.description` (`table_bits`, descriptors) | `fixtures.bits_per_symbol`, `fixtures.table_bits`, `fixtures.canonical_descriptor` |
| `ordering.partitions` (272 fixed order) | `fixtures.iter_partition_specs`, `fixtures.PartitionSpec` |
| `ordering.kernels` | `fixtures.KERNEL_ORDER` |
| `kernels.common_law`, `kernels.R1`-`R4` | `fixtures.RAW_KERNEL_LAWS` |
| `kernels.P` | `fixtures.p_translation_law` |
| `kernels.U` | `fixtures.u_uniform_law` |
| `kernels.translation_order` | `kernels.reduce_law`, `kernels.reduced_law` |
| `quantities.K` | `kernels.build_K` |
| `quantities.TV` | `kernels.total_variation` |
| `quantities.delta_l` | `kernels.certify_kernel` (`KernelCertificate.delta_l`) |
| `quantities.delta` (joint, not `sum_l nu(l)*delta_l`) | `kernels.certify_kernel` (`KernelCertificate.delta`, computed pair-by-pair as `sum_l nu(l)*TV`, then maximized over pairs) |
| `quantities.per_operation_max` | `kernels.certify_kernel` (`KernelCertificate.per_operation_max`) |
| `quantities.maximizer_ties` | `kernels.maximizer_witness` |
| `quantities.simulator` | `transcripts.propagate_simulator` |
| `quantities.transcript`, `quantities.horizons`, `quantities.initial_states` | `transcripts.propagate_real`, `transcripts.propagate_simulator` (horizons 0-3 passed as argument; every initial state, no averaging) |
| `quantities.bound`, `quantities.vacuity` | `transcripts.coupling_bound`, `transcripts.is_vacuous` |
| `computation.producer` | `transcripts.propagate_real`, `transcripts.propagate_simulator`, `transcripts.transcript_marginal` |
| `computation.independent_checker` | `reference.py` in full (no import of `fixtures`/`kernels`/`transcripts`); latent-path enumeration via `itertools.product`, not DP: `reference.reference_real_transcript_distribution`, `reference.reference_simulator_transcript_distribution` |
| `computation.certificates` | `certificates.serialize_fraction`, `certificates.serialize_distribution`, `certificates.hash_object`, `certificates.expected_artifact_index` |
| `assumption_trap` (persistent A, freshness violated, `bound_inapplicable`) | `transcripts.trap_real_distribution`, `transcripts.trap_comparison_distribution`, `transcripts.certify_trap`, `transcripts.certify_all_trap_starts`; independently: `reference.reference_trap_certificate` |
| `controls.exact_identity_constant`, `controls.C15_cosets`, `controls.hidden_uniform`, `controls.public_prime_rigidity`, `controls.matched_sizes` | Consequences of the generic `kernels.certify_kernel` / `fixtures.build_partition` machinery on the relevant partition kinds -- **not** special-cased or hardcoded, so a real run either reproduces the stated exact values or reports a genuine mismatch |
| `controls.full_joint_and_freshness` | `transcripts.certify_all_trap_starts` (all 11 starts, tagged `bound_inapplicable`) |
| `controls.independent_exact_tables` | `reference.agrees_exactly` (exact equality only, no floating tolerance anywhere in any of these files) |
| `panel_advantage` (per-panel/paired qualifiers, positive/negative outcomes) | Not yet assembled into a scoring routine in this task; `certificates.py`'s `CertificateStatus`/`CertificateResult` and `kernels.KernelCertificate` supply the exact per-partition/per-kernel values a later scientific task combines into the 32 panels and 16 paired qualifiers exactly as specified, with **both** `conjecture_positive` and `conjecture_negative` branches representable (neither is preferred: qualification is a plain comparison against the frozen `>=1/8` mean gap and `>=24/32` strict-win thresholds, with no code path that special-cases either outcome) |
| `artifacts` (root/partition/kernel/transcript/trap filenames, directory layout) | `certificates.expected_partition_dir/_kernel_dir/_transcript_dir/_trap_dir`, `certificates.expected_artifact_index`, `certificates.expected_counts` |
| `runtime.supervisor`, `runtime.native`, `runtime.docker`, `runtime.transport` (LUMP1), `runtime.receipts` | `driver.py` in full: `LaunchBinding`/`check_launch_admission`, `Lump1Frame`/`encode_lump1_frame`/`parse_lump1_frame`/`decode_chunk_payload`, `extract_verified_file`, `build_native_plan`/`build_docker_plan`, `HOST_OWNED_FILENAMES` |
| `runtime.admission` (source-only preflight) | `runtime_preflight.check_declared_constants`, `runtime_preflight.check_protection_establishable`, `runtime_preflight.full_preflight_report` |
| `launch_gate` | `driver.check_launch_admission`, `driver.LaunchNotAuthorizedError`, `driver.main` (refuses without all four bindings) |

## Independence discipline

`reference.py` imports nothing from `fixtures.py`, `kernels.py` or
`transcripts.py`. It re-derives, directly from the specification text, its
own copy of the SHA256 rejection shuffle, the six kernel laws, transition-row
construction, pairwise TV, and -- critically -- its own **latent-path
enumeration** (`itertools.product` over every `(label, private-draw)`
sequence of length `t`) rather than the producer's dynamic-programming
recursion. A shared transcription bug between the two paths would have to be
made independently twice from the same spec text, not inherited through a
shared helper.

## Negative finite-conjecture branch

The specification's `panel_advantage.conjecture_negative` ("all validity/
control gates pass but no paired qualifier is true; retain every
nonqualifying and single-size observation") is not a fallback or an
afterthought here: `kernels.certify_kernel` computes `delta_l`/`delta`/
`per_operation_max` identically regardless of whether a given partition ends
up qualifying, and no function in this directory branches on, or is more
permissive toward, either outcome. Scoring the 32 panels and 16 paired
qualifiers against the frozen `>=1/8` mean-gap and `>=24/32` strict-win
thresholds is left to a later scientific task's driver logic operating over
these certificates; that logic must apply the same unmodified thresholds to
both possible outcomes, exactly as `panel_advantage.forbidden` requires (no
parameter selection, null replacement, seed extension, p-value, or reliance
on P's binary maximum / U's forced zero).

## Freshness / full-transcript vs. final-marginal separation

`transcripts.trap_real_distribution` and `transcripts.trap_comparison_distribution`
implement the persistent-translation control exactly as specified: one hidden
`A` reused at both steps, public label `0` both times, compared against a
fresh-uniform two-step process with the same initial feature. The result is
tagged `certificates.CertificateStatus.BOUND_INAPPLICABLE` unconditionally
(`transcripts.TrapCertificate.classification`) -- this is never treated as a
counterexample to the coupling bound, because the trap's law violates the
bound's own freshness premise. `transcripts.final_feature_marginal` and
`transcripts.trap_final_marginal` are kept as functions entirely separate
from `transcripts.transcript_marginal`/`trap_real_distribution`'s full
transcript output, so a future driver cannot silently substitute
final-marginal agreement (expected `0` here) for full-transcript agreement
(expected `10/11` here) when reporting the trap's outcome.

## Future CLI shape (not run)

A later, separately authorized scientific task would invoke `driver.main`
with four required arguments naming: the approved specification path and its
sha256, the (Coordinator-committed) implementation manifest path, an
independent review receipt path, and a genuine launch lock path
(`--approved-spec-path`, `--approved-spec-sha256`,
`--implementation-manifest-path`, `--independent-review-receipt-path`,
`--launch-lock-path`). `driver.check_launch_admission` refuses with a
`LaunchNotAuthorizedError` naming every missing or mismatched binding; no
binding is invented or assumed by this task. Even when admission is
satisfied, `driver.main` currently returns exit code `3` and states plainly
that this implementation handoff does not implement the post-admission
scientific execution path -- that is intentional and matches
`launch_gate`'s requirement for "a separate scientific handoff and genuine
launch lock."

## Review and launch boundary

No independent review has occurred for this implementation
(`review_boundary` in `TASK-20260907-6bd7c0`). No backend/resource preflight
against a live host or Docker daemon has been performed (`runtime_preflight.py`
is source-only and always reports `ready_for_scientific_launch: False`). No
run directory, launch lock, or scientific result exists anywhere under
`experiments/EXP-CRYPTO-5e8beb/runs/`. The Coordinator's snapshot commit,
an independent (`review-adversarial`) validation/red-team pass over the
kernel/approximation derivation and full-history certificates, a genuine
backend/resource preflight, a separate scientific task handoff, and a real
launch lock are all still required before any run, per this specification's
`launch_gate` and this task's `completion_gate`.

## Bedrock

Amazon Bedrock was not selected, configured, probed, contacted, or used
anywhere in this task. `driver.bedrock_status()` returns this status
literally as a constant string for later manifest/report cross-checking.

## Scope note

This implementation does not add any scalar-dependent advice to any
combiner: every visible integer state throughout `fixtures.py`, `kernels.py`,
`transcripts.py` and `reference.py` is a toy cyclic-group coordinate in
`C_11`, `C_15` or `C_17`, never a stand-in for an unknown ECDLP scalar, and
no function here claims or implies that such a feature would be cheap to
obtain in a real ECDLP setting.
