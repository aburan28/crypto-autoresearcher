# EXP-CRYPTO-5e8beb implementation-v3

Consolidated, self-contained implementation of `experiments/EXP-CRYPTO-5e8beb/specification.yaml`,
produced by `TASK-20260913-c43d3e` to close two independently-confirmed
review gaps from
`coordination/design/BATCH-51d1bb/reviews/TASK-20260908-0eabfe/implementation-review.yaml`
(verdict `REVISE`):

- **C8** -- no panel-advantage scoring logic existed in `implementation/`.
  `panel_scoring.py` (`implementation-v2/`, already validated against
  synthetic metadata by `TASK-20260908-630c49`) is copied in unchanged and
  wired to real `kernels.KernelCertificate` data via
  `driver.assemble_panel_metadata`. This task independently re-derives the
  synthetic-metadata finding rather than citing it -- see
  `implementation-report.yaml`'s `gaps_closed[C8]`.
- **C10** -- `driver.check_launch_admission` performed existence-only checks
  on all four required bindings. It now performs real content verification
  of each: the approved spec's YAML content, the implementation manifest's
  per-file sha256 against actual on-disk bytes, the independent review
  receipt's verdict/commit binding, and the launch lock's actual
  `tools/goal_lanes.py` claim schema (schema string, task_id, owner,
  expiry, write_scope, and absence of a sibling release).

It also closes **C9** (minor: wire `TRAP_HORIZON`/`REFERENCE_TRAP_HORIZON`
into the trap functions rather than leaving them dead) and implements two
of this task's own constraints beyond the review: real, side-effect-free
cgroup v2 / Docker capability probing in `runtime_preflight.py` (replacing
the prior always-`False` stub), and the actual end-to-end fixture-to-
certificate-to-panel-score execution path in `driver.py`.

**This is still zero-run preparation.** `scientific_execution_authorized:
false` in the frozen specification and `maximum_runs: 0` in this task's
handoff both bind. No function here was ever called against the
specification's real frozen panel (N in {11,15,17}, seeds 0..31, kernels
R1-R4/P/U) by this task, and nothing was written under
`experiments/EXP-CRYPTO-5e8beb/runs/`. `implementation-report.yaml` states
`scientific_runs: 0` and `fixtures_evaluated_on_frozen_panel: 0` explicitly
and discloses exactly what synthetic/toy testing was performed instead.

## Protocol-to-code map

| Specification field | Module / function |
|---|---|
| `fixture_definition.prime_partitions` / `composite_partitions` | `fixtures.py`: `PRIME_NS`, `Q_VALUES`, `COMPOSITE_N`, `iter_partition_specs` |
| `fixture_definition.prime_partitions.generation` | `fixtures.generate_permutation`; independently, `reference.reference_generate_permutation` |
| `kernels` (R1-R4, P, U) | `fixtures.RAW_KERNEL_LAWS`, `p_translation_law`, `u_uniform_law`; independently, `reference.reference_raw_law` |
| `quantities.K` / `delta_l` / `delta` / `TV` / `maximizer_ties` | `kernels.build_K`, `total_variation`, `certify_kernel`, `maximizer_witness` |
| `computation.producer` | `transcripts.propagate_real`, `propagate_simulator` |
| `computation.independent_checker` | `reference.py` (no import of fixtures/kernels/transcripts; latent-path enumeration via `itertools.product`, not DP) |
| `computation.certificates` | `certificates.py` (serialization/status taxonomy), `driver.write_*_artifacts` (actual file output) |
| `assumption_trap` | `transcripts.trap_real_distribution` / `trap_comparison_distribution` / `certify_trap` (now `TRAP_HORIZON`-driven, C9); independently, `reference.reference_trap_certificate` |
| `panel_advantage` | `panel_scoring.score_panel_advantage` (C8), fed by `driver.assemble_panel_metadata` |
| `runtime.admission` / `launch_gate` | `driver.check_launch_admission` (C10: real content verification), `runtime_preflight.py` (real live-host probes) |
| `runtime.transport` (LUMP1) | `driver.encode_lump1_frame`, `parse_lump1_frame`, `extract_verified_file` |
| `artifacts` | `certificates.expected_*_dir/paths`, `driver.write_partition_artifacts` / `write_kernel_artifacts` / `write_transcript_artifacts` |

## Independence discipline

Unchanged from `implementation/`: `reference.py` imports only stdlib
(`hashlib`, `itertools`, `fractions`, `typing`) and re-derives every law,
permutation-generation step, and transcript enumeration from the
specification text itself, never from `fixtures.py`/`kernels.py`/
`transcripts.py`. `driver.certify_partition_kernel` and
`driver.certify_transcript` call **both** the producer path and the
independent reference path and record their agreement (`agrees_exactly`,
never a floating tolerance) in every kernel/transcript certificate this
task's pipeline writes.

## Copy provenance (self-containment)

Per this task's constraint, `implementation-v3/` does not import from
`implementation/` or `implementation-v2/` at runtime:

- `fixtures.py`, `kernels.py`, `certificates.py` -- byte-identical copies
  from `implementation/` (sha256 matches; see `implementation-manifest.yaml`).
- `panel_scoring.py` -- byte-identical copy from `implementation-v2/`.
- `transcripts.py`, `reference.py` -- copied from `implementation/` with the
  C9 correction applied (wiring `TRAP_HORIZON`/`REFERENCE_TRAP_HORIZON`);
  verified byte-identical *output* to the originals at the frozen horizon=2
  for all 11 trap starts (see `implementation-report.yaml`).
- `runtime_preflight.py`, `driver.py` -- new in this task (see below).

## C10: real content verification

`driver.check_launch_admission(binding)` now performs, fail-closed, for
each of the four required bindings:

1. **Approved spec** -- parses `specification.yaml` as YAML and requires
   `experiment.status == 'approved'`, `experiment.approved_by` truthy, and
   `experiment.frozen` truthy (plus an optional id match). A caller can no
   longer satisfy this by supplying an arbitrary file plus that file's own
   hash.
2. **Implementation manifest** -- parses `implementation-manifest.yaml`'s
   `implementation_files_sha256` mapping and recomputes sha256 of every
   listed file's *actual current bytes* on disk, refusing on any mismatch
   or missing file.
3. **Independent review receipt** -- parses the receipt as YAML, extracts a
   verdict from either the `validation_report` schema
   (`agents/validator.md`) or the `implementation_review` shape actually
   used for static implementation reviews in this repository, requires it
   to be a passed-equivalent, and requires the receipt's recorded reviewed
   commit and a reviewed-path fragment to match caller-supplied expected
   values.
4. **Launch lock** -- parses the lock as JSON per `tools/goal_lanes.py`'s
   actual `crypto.autoresearch.task_claim.v1` claim schema: schema string,
   matching `task_id`, non-empty `owner`, parseable and non-expired
   `expires_at`, a `write_scope` entry naming this task's own scope prefix,
   and no sibling `<task_id>.<epoch>.release.json` (a release ends a live
   claim). `tools/goal_lanes.py` itself is not imported, to keep
   `implementation-v3/` self-contained; its schema semantics are
   reproduced exactly (see that module's own docstring/`classify`/`CLAIM_SCHEMA`).

Demonstrated against one fully-passing synthetic bundle and 8 deliberately
broken variants (one per named failure mode above, plus an arbitrary
non-JSON file used as a lock -- the exact case the old existence-only check
would have silently admitted). See `implementation-report.yaml`'s
`testing_performed`.

## C8: panel-advantage scoring, independently re-verified

`panel_scoring.py` is unchanged from `implementation-v2/`. This task does
not cite `TASK-20260908-630c49`'s synthetic-metadata validation on faith;
it reads the source and independently writes and runs 9 hand-constructed
metadata fixtures (boundary cases, malformed-schema rejection, `validity:
false` never downgrading to NEGATIVE, all-16-pairs, determinism/no-mutation)
plus 2 fixtures exercising the new `driver.assemble_panel_metadata` wiring
against hand-built `KernelCertificate` objects. All pass. See
`implementation-report.yaml`'s `gaps_closed[C8]` for the full list.

## Real runtime preflight (cgroup v2 / Docker)

`runtime_preflight.probe_cgroup_v2()`, `probe_docker()`, and
`probe_rlimit_capability()` actually read this container's real
`/sys/fs/cgroup` state, look for a `docker` binary and run the read-only
`docker info`, and read back (never set) this process's own
`RLIMIT_AS`/`RLIMIT_CPU`. `check_protection_establishable()` may now return
`ready_for_scientific_launch=True`, but only when a probe genuinely
supports it, and the exact observed values on this host at report time are
recorded verbatim in `implementation-report.yaml`'s
`runtime_preflight_observations` (this host: cgroup v2 controller file
present but not readable; Docker CLI present but daemon unreachable in this
sandbox; RLIMIT read-back succeeded showing no current limit). A disclosed
caveat: the RLIMIT read-back is necessary but not sufficient evidence that
a *tighter* limit could later be set, since testing that would irreversibly
narrow this session's own resource ceiling.

## The actual end-to-end execution path (not exercised on the frozen panel)

`driver.run_scientific_pipeline` and `driver.run_assumption_trap` implement
specification.computation and specification.artifacts' file layout as real,
callable code: for each declared partition spec, build the partition
(`fixtures.build_partition`), certify every declared kernel with an
independent reference cross-check (`certify_partition_kernel`), propagate
real/simulator transcripts for every initial state and horizon with a
reference cross-check (`certify_transcript`), and write every artifact file
(`write_partition_artifacts`, `write_kernel_artifacts`,
`write_transcript_artifacts`) in the exact directory/filename layout
`certificates.py` already enumerated. `driver.assemble_panel_metadata` then
wires the resulting certificates into `panel_scoring.score_panel_advantage`.

**This task never calls any of this against the real frozen panel.** It is
smoke-tested only against an explicitly non-frozen toy panel: N in {3,4},
an out-of-band toy seed (999, never a frozen 0..31 draw against N=11/17),
kernels R1/R2 only, horizons 0-2 only. Result: 4 toy partitions, 8 kernel
cells, 84 transcript checks, producer/reference agreement `True`
throughout, 476 artifact files written to a scratch location (never under
`experiments/EXP-CRYPTO-5e8beb/runs/`). This demonstrates the pipeline is
structurally sound; it is not and must never be read as any claim about the
frozen scientific panel. Full detail in `implementation-report.yaml`'s
`testing_performed`.

## Review and launch boundary

This implementation directory, once snapshotted, requires an independent
Validator/Red-Team review before any launch lock can legitimately name it.
No launch lock exists for this task; `driver.main()`'s post-admission
branch (which would run the real frozen 272-partition panel through
`run_scientific_pipeline`) is real, reviewable code, but this task never
supplies a bundle that satisfies `check_launch_admission`, so that branch
is never reached here.

## Bedrock

`driver.BEDROCK_STATUS` / `bedrock_status()`: `"NOT SELECTED, NOT
CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED"`. No Bedrock-named
provider, backend, endpoint, or model identifier is referenced anywhere in
this directory.

## Scope note

`implementation-v3/` is a complete, self-contained successor to
`implementation/` + `implementation-v2/` for the purposes of a future
scientific launch review. It does not delete, edit, or supersede either
prior directory as a durable record; both remain byte-identical to their
own reviewed/archived snapshots.
