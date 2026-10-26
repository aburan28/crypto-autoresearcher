# Factor-base width engineering draft

This directory implements the local engineering handoff
[`TASK-20261025-fa3055`](../../ledger/handoffs/TASK-20261025-fa3055.yaml) for
[`EXP-ECDLP-a9b6a5`](../../experiments/EXP-ECDLP-a9b6a5/specification.yaml).
It is unpublished, uncommitted engineering. No p4099 target relation acceptance,
rank, pilot, benchmark, `Context.construct` call or scientific run has occurred.
No speedup, security or general structural claim is made.

`build_inputs.py` reuses the original deterministic `describe()` rule on exactly
p4099 A2 B13/r4021 and B16/r4111. Both EC1 curve identities, generators, first
eight atoms and their native lifts remain identical. Canonical square roots and
the first distinct norm-x classes append to sixteen, with a complete per-x
trace. The inherited x=0 atom is retained; branches through x=0 continue to be
rejected by the unchanged constructor. No new nonzero-lift eligibility rule is
introduced.

The original m8 seed0 source shuffle depends on the old fixture UID. Its exact
domain string and shuffled array are now materialized once in `width_binding`,
and independently checked. m16 traversal reuses that array without hashing the
new width UID into the source schedule. Branches are lexicographic triples and
lexicographic options in range(4)^3; old numeric branch indices are mapped to
the new indices through tuple/options descriptors. Every one of the old 3,584
descriptors/source embeds in the new 35,840 descriptors/source. This is an input
identity, independent of relation acceptance. Existing historical m8 accepted
rows are zero on both curves, so empirical positive-witness embedding is
vacuous. A separate positive p101 planted witness exercises old8-to16 padding,
source lift, descriptor, canonical geometry and explicit witness equality.

`check_inputs.py` uses independent point arithmetic, curve-order recounts and a
separate exhaustive square-root table to check inputs, trace/prefix/schedule,
descriptor inclusion and all public +/-[a]P anchors for a=1..64. It invokes no
constructor and learns no unknown-log table. Actual input-derived U is 15 on
each new base: atom0 is publicly known and the remaining canonical norm classes
are unknown under those declared exposures. The finite rank is unobserved.
Historical m8 U7/rank0/zero-row observations are read from frozen local checker
metadata. Native blob pointer, logical/stored hash, canonical manifest, receipt
and custody links are checked locally. This does not hydrate the raw blobs or
make a fresh remote GET; those custody gates remain missing.

`collect_width.py` has one future scientific arm, `m16_full35840`, and no sample,
pilot, branch limit, m8 replay or early-rank stop. It preserves every source
status including unliftable and exceptional sources, canonical aliases,
attempt digests, source checkpoints, immediate accepted-witness records, rank
progress and first-full location while continuing full enumeration. Accepted
rows carry the inherited cubic/residual/principal witness and E1 source
equation. Every call retains its actual native-to-projected map and public
derivations; equal/opposite/zero/known columns normalize explicitly. Full M,b,
affine and augmented ranks, independent-row and echelon-pivot witnesses,
consistency, nullity and a finite right-kernel basis are retained.

`check_width.py` imports neither this collector nor producer arithmetic. It
reuses the frozen independent `Census`, `check_census.outcome` and `independent`
arithmetic path and separately checks schedule, every accepted/rejected/alias
status, witnesses, attempt commitments, row locations, source checkpoints,
matrix certificates and right kernels. Fixed reverse atom permutation with
per-atom sign/deck changes checks A/A equations and canonical projected
matrices. This is code-path independence within one engineering session; it
does not replace the later independently staffed phased scientific review or
its fresh derivation after an official freeze.

The planted same-shape null-source control also draws one deterministic seeded
uniform scalar from F_r excluding the actual source, then checks independent
rejection of the false label. It is distinct from the a+1 mutation and makes no
random-cover or benefit claim. A planted interrupted collector verifies that
already accepted witness bytes and the unfinished source's statuses/error
location survive as explicitly censored records.

The direct producer and checker APIs refuse targets without the post-admission
capability. Their software mode accepts only explicit `software_control: true`
fixtures with p<=211. These Python capabilities prevent accidental entry;
they are not a sandbox, security boundary, authorization record or execution
proof. Native launch still enforces the frozen specification/approval/plan,
clean revision/live authority, exact canonical config, complete source/input
hash map, dependency versions and canonical run directory through the existing
`native_runtime_v2.binding`. The source-binding manifest itself must be an
additional exact future plan input. A matching hash never grants authority.

Raw public-construction counters, field/group/pow-call/hash vectors, stage
vectors, digest/status/event bytes, online/final matrix units, inline checker
times, total wall/CPU, caches and self RSS are retained separately. The replay
checker records its own wall/CPU/RSS and branch/witness counters. These remain
partial S: pow internals, Python bookkeeping, general byte movement, full
independent primitive/matrix counts and canonical compression/upload/readback
costs are excluded until separately reconciled. Historical timings differ in
implementation and host; no matched cost or speed comparison is asserted.

The source and input hash map is `source-bindings.json`. The `input_sha256`
map excludes that manifest's self hash; the future plan must add the manifest
itself. `bind_sources.py --check` verifies the map. Tests and public input
construction are software validation only. The renderer is exercised against
a planted retained cell, and its PDF is opened, text-checked and rasterized
with PyMuPDF. No target is used by that smoke test.

Commands already used for local software work (from repository root):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/prym_factor_base_width_20261025/build_inputs.py
PYTHONDONTWRITEBYTECODE=1 python3 research/prym_factor_base_width_20261025/check_inputs.py
PYTHONDONTWRITEBYTECODE=1 python3 research/prym_factor_base_width_20261025/bind_sources.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s research/prym_factor_base_width_20261025 -p test_width.py -v
PYTHONDONTWRITEBYTECODE=1 python3 research/prym_factor_base_width_20261025/bind_sources.py --check
```

Generation commands use exclusive creation to avoid replacing existing outputs;
the deterministic functions can be recomputed in memory for comparison. The
software transcript retains failed test assertions and their correction as
software defects, not mathematical observations. Pytest is absent in this
runtime; the tests use stdlib unittest with Python 3.12.14.

Future launcher contract, **not run or authorized here**:

```sh
python3 research/prym_factor_base_width_20261025/collect_width.py --config research/prym_factor_base_width_20261025/config.json --run-dir {run_dir}
python3 research/prym_factor_base_width_20261025/check_width.py --config research/prym_factor_base_width_20261025/config.json --run-dir {run_dir}
```

The concrete future storage supervisor is now
`research/prym_factor_base_width_20261025/execute_with_storage.py`. Its
`contract.json` pins EXP-ECDLP-a9b6a5 / RUN-ECDLP-967315, the canonical run path
and delivery directory, 65,537-byte compression/offload thresholds and all
three delivery outputs. It imports the frozen census delivery adapter into an
isolated module instance and rebinds only `EXPERIMENT`, `RUN`, `DELIVERY` and
`HERE`; its `Publisher`, `storage_adapter` and `run` implementations are reused
unchanged. The old script retains its old IDs and exact bytes. Wrong plan
experiment/run IDs are refused before Publisher construction or native calls.
The wrapper has only `run` and `probe` modes, with no historical mode.

Future outer invocation, **not executed here**:

```sh
python3 research/prym_factor_base_width_20261025/execute_with_storage.py run --plan experiments/EXP-ECDLP-a9b6a5/trial-plan.json --owner {owner} --epoch {epoch}
```

`supervisor_execution.entrypoint` is the new wrapper path, `mode` is `run`,
`native_supervisor` is `tools/experiment_execution.py`, and `storage_contract`
is `research/prym_factor_base_width_20261025/contract.json`. Required delivery
outputs are `.artifacts.json`, `.gitignore` and `custody.json` under
`experiments/EXP-ECDLP-a9b6a5/artifact-deliveries/RUN-ECDLP-967315`.
Canonical push/verify/fresh GET and fatal delivery-before-seal semantics are
inherited. Storage tests mock the native supervisor/Publisher/remote probe;
the failure control uses local planted incompressible bytes and proves that
upload failure propagates before its modeled seal point while recoverable
gzip remains. No actual probe, network call, target run or custody output has
been produced. Configured artifact identity/readback remain future gates.

The expanded local suite, including storage controls, is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s research/prym_factor_base_width_20261025 -p 'test*.py' -v
```

Native trial artifacts are `manifest.yaml`, `raw-result.json`, `events.jsonl`,
`verification.json`, `report.md`, `graph.svg`, `graph-source.json`, and
`report.pdf`, alongside the supervisor's standard launch/environment/stdout/
stderr/command/receipt files. Event JSONL includes immediate accepted-witness
records followed by complete source-block records; a failed source may leave
accepted records without a complete source block, which is censored work.
The full new scientific workload is derived as
2*64*C(16,3)*4^3 = 4,587,520 attempts (2,293,760/curve), with zero new m8
attempts. This is not a measured run result.

Missing launch gates: exact published/committed prospective
plan/source/input/approval/archive/native-live bindings;
Director compile and preapproval acceptance; canonical artifact identity and
historical raw hydration/readback; future full target collection and exhaustive
replay; independent phased plan/seal/release/read timeline and scientific
review; complete cost reconciliation and prescribed-execution proof support.
Historical missing exact unblind timing is not repaired by this directory.

The merged-main protocol/export integration is implemented under additive
`TASK-20261026-f08a97`. `export_width.py` is the frozen analysis/export helper;
it consumes genuine native packages, retains the same two scientific arms
`m16_candidate` and `m8_reference`, and emits four logical rows for b13/b16,
seed0, replicate0, with no warmups or new m8 execution. Per-cell row IDs append
the instance to the observed physical native run ID; `backend_ref` and backend
metadata retain the original ID, input package path, observed launch argv and
the full shared host/cost/receipt context. Historical labels remain disclosed
as seen before this conditioned follow-up. Positive/negative software controls
and transported encoding qualify the checker and add no target arm.

Primary metric mapping is exact: `attempted=cell.attempts`,
`accepted=len(cell.rows)`, `U=cell.projection.U`,
`rank=cell.projection.rank`,
`augmented_rank=cell.projection.augmented_rank`, and
`nullity=cell.projection.U-cell.projection.rank`. `reason_<status>`, producer
vectors, matrix units, caches, progress/checkpoints and independent checker
vectors are retained as counters. Shared physical construction, checker,
timing and environment data remain backend metadata and must not be summed
as separate per-cell costs. Full witness/matrix bytes remain bound raw files.
Failure or censored cells with retained native evidence remain excluded rows
and contribute to the exported flow; missing indispensable native files,
commit/executable identities, seed0 or successful-cell coverage are refused.
Unknown producer or host/isolation fields stay null/unrecorded. Every clock
is diagnostic and `wall_valid=false`, including resumed or unisolated rows.
No planned value fills missing observed identity, seed, host or verification.

The helper requires actually hydrated raw/events bytes matching the native
receipt and checker commitments. A `.blob.json` pointer is not hydration;
the helper performs no network access. Make hydrated analysis copies outside
sealed run directories while preserving originals, then run the following
**future post-run steps, not executed on target inputs here**:

```sh
python3 research/prym_factor_base_width_20261025/prepare_export_inputs.py --run-dir experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315 --output-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315
python3 research/prym_factor_base_width_20261025/prepare_export_inputs.py --run-dir experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6 --output-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-ea49a6
python3 research/prym_factor_base_width_20261025/export_width.py analysis --protocol experiments/EXP-ECDLP-a9b6a5/protocol.json --candidate-run-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315 --reference-run-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-ea49a6 --output experiments/EXP-ECDLP-a9b6a5/width-analysis.json
python3 research/prym_factor_base_width_20261025/export_width.py export --protocol experiments/EXP-ECDLP-a9b6a5/protocol.json --candidate-run-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315 --reference-run-dir experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-ea49a6 --output experiments/EXP-ECDLP-a9b6a5/export.json
python3 tools/experiment_protocol.py check-export experiments/EXP-ECDLP-a9b6a5/export.json --protocol experiments/EXP-ECDLP-a9b6a5/protocol.json --verify-files
```

The export command also writes `export-analysis.json`; both outputs are
write-once and outside the native seal. The old storage adapter remains
unchanged, so successful post-run export/check-export and its separately bound
canonical custody are explicit completion gates, following native delivery.
No claim is made that the inherited adapter itself performs this post-run
export. A successful planted native-shaped package passes the generic checker
with file verification; negative tests reject protocol/file/coverage/seed/
identity/hydration defects without running a relation constructor.

`prepare_export_inputs.py` makes those two concrete replay caches from exactly
the seven native files consumed by the exporter. Logical raw/events bytes use
`tools.artifact_store.read_bytes`, including hash-checked decompression and
configured-reader/cache hydration; physical small metadata/receipt bytes are
copied unchanged. Native content hashes, pointer metadata and run/source
identity are verified before the write-once destination is published, and
source stored-form hashes are rechecked unchanged. Existing complete or
incomplete destinations are refused. The helper adds no sidecar and never
edits a sealed directory. These cache copies are ephemeral and reconstructible;
original canonical pointers/receipts/custody remain authoritative. They are
ignored by repository publication and add no authoritative run artifacts.
The four preparation tests use planted native packages and local file-store
pointers, with S3 disabled/missing storage mocked. No actual target package
has been hydrated here. Missing canonical access remains a runtime gate.

`runtime_width.py` checks the actual frozen `protocol.json` file SHA declared
in both plan and specification `execution_plan.protocol_hashes`, separately
from `freeze.protocol_sha256` (the canonical hash excluding the freeze block).
It requires the protocol as an additional native input, verifies its frozen
helper SHA before any target construction, and records both hashes in a
successful raw result. The source/input manifest excludes protocol.json and
its own self hash to avoid recursive freeze bindings; the native plan adds
both explicitly. The protective watchdog is 86,400 s; the prospective claim
TTL is 1,500 min / 90,000 s, with no renewal promise or budget cap. Timeout
remains censored infrastructure, never a mathematical negative.

`source-bindings-premerge-20261026.json` preserves the exact earlier local
manifest (SHA71f79cd22b01c6a7fbc4a5ce3aebe80cb3dd42b129a30a1282ba16a7347ebd9d).
The current manifest rebinds merged dependencies, the export helper, generic
protocol checker and both schemas. The additive `export-engineering-status.json`
records that change, exact tests/hashes/argv and remaining runtime gates;
earlier engineering snapshots and failed software transcripts remain intact.
