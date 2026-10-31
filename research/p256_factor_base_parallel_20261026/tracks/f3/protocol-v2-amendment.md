# F3 prospective source-binding amendment

Date: 2026-10-26. Amendment: `CORR-20261026-80a4e6`.
Preparation handoff: `TASK-20261026-33d0f6`, committed at
`e66fb1a3e25ca1b55760a79008b6469309f308b7` on
`research/p256-pass2-checkpoint-20261026`. Archival owner:
`TASK-20261026-54bcce`, under its explicit additive scope extension.

`protocol.v2.draft.json` is an additive prospective draft of
`P256-F3-PASS2-20261026`, version 2. The existing `run.py` requires a matching
digest for every file in its five-file `SOURCE_FILES` tuple. Original frozen
version 1 has `extensions.source_sha256={}`, so that admission condition is
unsatisfied even though the canonical protocol checker accepts version 1.
This amendment binds the existing unchanged bytes before affected version-2
data. It does not change the finite panel or its analysis.

The original `protocol.json` remains byte-for-byte unchanged:

- Original canonical SHA-256, excluding `freeze`:
  `92c516099637f803496f9148917e8b1c0d76decc11292be600f914a87db2befa`.
- Original file SHA-256:
  `cbe2cf64d32fbf700c66fe8946a88875e3c949cfb114fdbed131663f095c2783`.
- Original freeze timestamp: `2026-10-26T15:40:24Z`.
- Original freeze and instrument commit:
  `de1f9bbe50801ba5cccbe915b7aece2a0ea5c5ff`.

## Source custody

Each working file was compared byte-for-byte with
`git show de1f9bbe50801ba5cccbe915b7aece2a0ea5c5ff:<repository-relative-path>`.
All five comparisons matched. SHA-256 below hashes the file content; Git blob
IDs identify the corresponding original Git objects. No source was imported.

| File | Content SHA-256 | Original Git blob ID |
| --- | --- | --- |
| `run.py` | `28d537b485177c5fb85f8ec13d8d9ccb344f196276ccb6a9d49b54d93451e730` | `81ad7835ea843e3910dc941c1145480c616f3cc9` |
| `oracle.py` | `fee9395a184da559184c9acefb7bde2fe7f703da110df6ba95d37d7f502449b7` | `499d7e5d5709606f368b4b8ded73fd9e66429826` |
| `analysis.py` | `cea5eefc1a115d1df03dd93745cc8b670052a8ab0e5769c72e79319fa90cee43` | `e36c4dc9c1e4f4a2cc954b48b487b193b5dc7405` |
| `export.py` | `30fe6de1727bae7f51da0175a6049ce5a33895f3744653a2a7f7cb3edef52fb4` | `419718296ec98ff7f4509eedad8e3e0dda6b04ed` |
| `curve-record.json` | `523e025572202a0eab01e3d569e283caebd95243caf7798f1827a915461dd95b` | `e76836f360ab2bdb63784f0ebf9886f8dfa258ec` |

The executable digest remains
`fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`.
The instrument commit, both complete arm records and
`analysis_plan.script.sha256` remain exactly as in version 1. Executable
availability and its runtime digest have not been tested by this preparation.

## Exact prospective delta

The only changed JSON locations relative to original version 1 are:

1. `/version`: `1` to `2`.
2. `/extensions/source_sha256`: empty object to the five content digests above.
3. `/amendments`: append the dated, before-affected-data amendment
   `CORR-20261026-80a4e6`, linking the original canonical hash.
4. `/freeze`: set `status` to `draft`; set `protocol_sha256`, `commit`,
   `frozen_at` and `filed_before_affected_data` to `null`.

An exact structural comparison restored those four locations from the original
and found the resulting documents equal. All seeds, counts, cases, controls,
claims, metrics, stopping/decision rules, analysis fields, source/input bytes,
instrument commits and executable digests are preserved. The original
`instrument.build` arrays are also preserved. Future version-2 launch and
export commands must supply the explicit version-2 path below because both
programs otherwise default to original `protocol.json`.

## Observed metadata validation

The repository's canonical checker was run from the repository root:

```sh
python3 -B tools/experiment_protocol.py validate research/p256_factor_base_parallel_20261026/tracks/f3/protocol.v2.draft.json
python3 -B tools/experiment_protocol.py hash research/p256_factor_base_parallel_20261026/tracks/f3/protocol.v2.draft.json
```

Observed result: `OK: experiment.protocol/v1` with `0 finding(s)`.
The original protocol also passed that checker with `0 finding(s)`, and its
canonical hash was recomputed and matched its original freeze record.

- Draft canonical SHA-256, excluding `freeze`:
  `194ca178b4f33d4cb5950b16b2e38daa76545c09a18b7dc62046e32cc82ac505`.
- Draft file SHA-256:
  `3df33c8e22849be39ef2f3d855e5544b31d86415f7dfc224f77808ca4fe29561`.

These are metadata/schema and byte-custody observations. The scientific
programs, analysis, panels and pilots were neither imported nor executed.
No actual checkpoint gate/upload, credential access, Phase B release or
official scientific-state change occurred. Scientific results and gate success
remain unobserved. Native inherited model binding remains unprobed; this
preparation asserts no canonical model or scientific-review admission.

Preparation procedure deviation: the initial documentation read batch used
three simultaneous read-only shell processes despite the handoff's
`max_concurrent_processes=1`. Those processes finished without writes or
scientific execution; all subsequent shell operations were sequential.

## Commands for a separately released version-2 attempt

The coordinator independently reviews the exact delta, copies the draft to
new `protocol.v2.json`, freezes it prospectively and commits it. Final freeze
metadata is the coordinator's responsibility. If the non-freeze body is copied
unchanged, its canonical hash remains the draft canonical hash above.
The unchanged runner's admission checks still require the matching executable,
a v2-bound root release and the real successful checkpoint gate. Their runtime
success is not established by this draft.

The following commands are prospective templates, checked only against the
static CLI definitions. Run them from the repository root only as part of that
later released attempt. Replace `<fresh-attempt>` with a new retained attempt
name and `<root-release.json>` with the coordinator's version-2 release path.
The analysis script reads the observed run's protocol hash and has no
`--protocol` option.

```sh
f3_track='research/p256_factor_base_parallel_20261026/tracks/f3'
f3_protocol="$f3_track/protocol.v2.json"
f3_run_dir="$f3_track/runs/<fresh-attempt>"
f3_report_dir="$f3_track/reports/<fresh-attempt>"
f3_export_path="$f3_report_dir/export.json"
f3_release='<root-release.json>'

python3 -B tools/experiment_protocol.py validate "$f3_protocol"

timeout 120s env OMP_NUM_THREADS=1 python3 -B "$f3_track/run.py" \
  --out "$f3_run_dir" --seed 2026102603 \
  --protocol "$f3_protocol" --release "$f3_release"

python3 -B "$f3_track/analysis.py" \
  --run "$f3_run_dir" --out "$f3_report_dir"

python3 -B "$f3_track/export.py" \
  --run "$f3_run_dir" --analysis "$f3_report_dir" \
  --protocol "$f3_protocol" --out "$f3_export_path"

python3 -B tools/experiment_protocol.py check-export "$f3_export_path" \
  --protocol "$f3_protocol" --verify-files
```

## Sources checked for this amendment

Provenance: `internal`, directly read during `TASK-20261026-33d0f6` preparation.
`AGENTS.md`, its linked literature/observation rules, `docs/lab-contract.md`,
`docs/experiment-protocol.md`, `schemas/experiment-protocol.v1.json`,
`tools/experiment_protocol.py` and
`.claude/skills/experiment-protocol/SKILL.md` establish the additive amendment,
canonical-hash, draft/freeze and checker semantics. The full handoff,
original F3 protocol and five files listed above establish this correction's
scope, required source map and accepted CLI options. Original source objects
at the pinned instrument commit establish byte custody. External mathematical
literature was not re-evaluated for this metadata-only amendment; the original
scientific design, literature statements and their evidence gaps are retained.
No sibling reports were read.
