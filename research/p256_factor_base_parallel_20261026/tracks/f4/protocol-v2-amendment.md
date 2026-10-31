# F4 prospective checkpoint metadata amendment

Filed 2026-10-26 under [TASK-20261026-d7f8e2](../../handoffs/TASK-20261026-d7f8e2.json).
Archival owner: `TASK-20261026-54bcce`, including the declared additive scope
extension. This note and `protocol.v2.draft.json` are the only files prepared by
this task. Root separately owns the future frozen `protocol.v2.json` and custody
receipts. This preparation grants no run or Phase B release and changes no
official scientific status. The native inherited model binding is unprobed;
this is a bounded metadata correction, not scientific review or certification.

The original [protocol.json](protocol.json) remains byte-for-byte intact:

- Original frozen canonical SHA-256, excluding `freeze`:
  `e9bed18327e439468ec65e7b0ac0e3c175ff615c15d80f2218fb44c8a66145bd`.
- Original file SHA-256:
  `63744929ebd3a01f9eb64848b1d4f40b1d8b6760d985b65f000fd995d6afb015`.
- Declared input/handoff snapshot:
  `a527b62b11e6dcc2a365bae2bf9cfd0107a765cd` on
  `research/p256-pass2-checkpoint-20261026`, supplied as committed and pushed
  by root. All nine declared input/handoff files were compared with those Git
  object bytes; local HEAD is that commit. The remote-tracking ref is absent
  locally, so pushed status was not independently rechecked here.

The amendment applies only prospectively, before affected version 2 data.
Historical protocols, partial attempts and observations retain their original
identity and provenance; none is rebound to version 2.

Source review (provenance: `internal`; read by
`/root/f4_prospective_checkpoint_amendment`) established the actual interface:

- [AGENTS.md](../../../../AGENTS.md), “Resume checkpoints in S3 before every
  run,” requires the canonical S3 effort backup before a launch and updates
  while the effort proceeds. The task did not run the gate, upload, restore or
  access credentials.
- [Protocol documentation](../../../../docs/experiment-protocol.md), sections
  1 and 4, distinguishes application/CRIU restore from count and clock
  semantics, and requires additive dated versions. The
  [canonical schema](../../../../schemas/experiment-protocol.v1.json) permits
  `policy: none`, null interval/grace, and `restore_validation: none`; it fixes
  restored wall time as invalid and counted units as valid. The
  [checker](../../../../tools/experiment_protocol.py), `lint_protocol`, checks
  schema, freeze hashes and prospective amendments without executing the
  scientific scripts.
- [run.py](run.py), lines 33–42, writes exclusive fresh JSON files; lines
  190–209 write each finished arm and append its row; lines 214–240 retain
  each natural case or explicit failure. These are incremental output
  records, with no periodic application state-save or restore path. The
  `counter_checkpoint` variable tracks counter differences for arm accounting;
  it is not persistent process state.
- [run.py](run.py), lines 398–416, accepts an explicit protocol, refuses an
  unfrozen protocol or existing output directory, and invokes the shared
  root release/checkpoint gate before creating the output. Lines 431–439
  retain process failure information where the process can handle the stop.
- [export.py](export.py), lines 18–27 and 43–53, binds the selected frozen
  protocol and emits `attempts: 1`, `resumed: 0`, `checkpoint: null` and
  `wall_valid: false`. [REPRODUCE.md](REPRODUCE.md), lines 35–39, already
  documents partial-directory preservation and no in-place row continuation.

The original periodic application declaration (60-second interval, 10-second
grace, manifest restore validation) therefore describes unavailable behavior.
Version 2 records `none` for application checkpointing. The mandatory canonical
S3 resume backup and root gate still apply. Any subsequent authorized attempt
uses a fresh output identity and cannot continue or splice an old row. Preserve
all prior complete and partial records and their counted units; cross-restore
wall/CPU clocks stay invalid. An interrupted attempt remains unknown or
`not_completed`, with no invented missing rows or mathematical empty results.
Root supplies the existing 120-second process watchdog externally; the timeout,
2 GiB limit and stopping rules are unchanged.

The complete allowed JSON delta from version 1 is:

| JSON pointer | Original | Version 2 draft |
| --- | --- | --- |
| `/version` | `1` | `2` |
| `/execution/checkpoint/policy` | `"application"` | `"none"` |
| `/execution/checkpoint/interval_seconds` | `60` | `null` |
| `/execution/checkpoint/grace_seconds` | `10` | `null` |
| `/execution/checkpoint/restore_validation` | `"manifest_sha256"` | `"none"` |
| `/extensions/checkpoint_detail` | Original S3/fresh-output explanation | Explicit distinction between mandatory S3 backup and unavailable application checkpoint/row continuation; partial-record/count/clock preservation and external watchdog clarification |
| `/amendments` | `[]` | One entry identified by the existing handoff ID, filed `2026-10-26`, `filed_before_affected_data: true`, linking the original canonical hash and listing the correction |
| `/freeze/status` | `"frozen"` | `"draft"` |
| `/freeze/protocol_sha256` | Original canonical hash above | `null` |
| `/freeze/commit` | `"de1f9bbe50801ba5cccbe915b7aece2a0ea5c5ff"` | `null` |
| `/freeze/frozen_at` | `"2026-10-26T15:40:24Z"` | `null` |
| `/freeze/filed_before_affected_data` | `true` | `null` pending the separate freeze; the amendment itself is marked before affected data |

The exact original `extensions.checkpoint_detail` value is:

```json
"S3 resume gate before data; fresh per-case durable records; no in-place row resume. A restored process must use a fresh output attempt and discard cross-restore clocks."
```

Its exact replacement is:

```json
"The mandatory canonical S3 resume checkpoint and root release/checkpoint gate remain required before scientific execution and kept current under AGENTS.md. This effort backup is separate from application row continuation. The runner writes fresh per-case and completed-arm records; it has no periodic application checkpoint or restore-validation path and refuses an existing output directory. Preserve every completed/partial attempt and its counted units. Any subsequent authorized attempt needs a fresh output identity and cannot continue or merge an old row. Cross-restore wall/CPU clocks remain invalid; retained counted units remain valid. Root supplies the existing 120-second process watchdog externally."
```

Every other JSON value is identical, including
`execution.checkpoint.after_restore: {"wall_time":"invalid","counted_units":"valid"}`.
All scientific seeds, 128 natural cases, four arms, controls, claims, metrics,
analysis plan and source/input bytes are unchanged. The analysis hash remains
`4d9dd78208f833a0df2d6a10ddc34fba491c074ad6d3e37be06a2204824c91c8`;
all instrument commits remain
`de1f9bbe50801ba5cccbe915b7aece2a0ea5c5ff` and executable hashes remain
`fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`.

Validation performed from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/experiment_protocol.py validate research/p256_factor_base_parallel_20261026/tracks/f4/protocol.v2.draft.json
```

Observed result: `OK: experiment.protocol/v1` with `0 finding(s)` and exit
status 0. A separate recursive JSON comparison asserted exactly the 12 changed
pointers listed above, the corrected checkpoint values, unchanged
`after_restore`, and the complete draft freeze reset. It also compared the
original protocol and declared inputs with the supplied snapshot, and all nine
source/input paths selected by `run.py:source_observation` with the unchanged
instrument commit, including the analysis digest. Those byte comparisons
passed. Draft canonical SHA-256, excluding `freeze`:
`e9e6fa1abb9ed371f0a2bf691bdbc41d3aef1623f562a7d288357b2945e40c4e`.
This digest is informational; the draft has no frozen hash or execution
authority. No scientific module was imported or run, and no sibling report
was read. The source review addresses only checkpoint metadata, not the
mathematical claims or external scientific literature.

After root separately creates, freezes and archives `protocol.v2.json`, binds
its new canonical hash into the release/checkpoint evidence, and provides the
required real S3 checkpoint and Phase B release, the prospective launch is the
following command from the repository root under root's external 120-second
watchdog. It has **not** been executed by this task. `runs/run-v2-01` must be
unused; choose another fresh attempt identity if it exists.

```sh
/workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261026/tracks/f4/run.py --out research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-v2-01 --seed 2026102604 --protocol research/p256_factor_base_parallel_20261026/tracks/f4/protocol.v2.json --release research/p256_factor_base_parallel_20261026/tracks/f4/phase-b-release.json
```

For that future frozen protocol and a completed attempt, use the explicit
version 2 protocol in the canonical checks:

```sh
python3 tools/experiment_protocol.py validate research/p256_factor_base_parallel_20261026/tracks/f4/protocol.v2.json
python3 tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-v2-01/export.json --protocol research/p256_factor_base_parallel_20261026/tracks/f4/protocol.v2.json --verify-files
python3 tools/experiment_protocol.py flow research/p256_factor_base_parallel_20261026/tracks/f4/runs/run-v2-01/export.json
```

The unchanged runner defaults to `protocol.json`, so omitting `--protocol`
would select version 1. The `flow` command takes only the export path and has
no protocol option. If a stopped attempt has no complete export, retain its
partial files and root launcher logs; do not manufacture an export or rows to
make these prospective checks pass.
