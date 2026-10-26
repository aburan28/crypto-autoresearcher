# Sealed review phases

`tools/check_review_independence.py` supports **prospective** sealed-then-unblind
reviews through `sealed-blind-review/v1`. Without this explicit contract it
continues checking the union of all `sources_read` against `blind_from`.
Historical prose describing a second phase does not opt in. In particular,
`TASK-20261025-5145ac` remains a failed formal independence check.

A required blind re-deriver's new plan declares:

```yaml
review_plan:
  recorded_at: '2026-10-25T00:00:00Z'
  # Usual prior, joint ownership, worked attacks and negative controls required.
  blind_rederivation:
    required: true
    assigned_to: TASK-20261025-abcdef
    quantity: expected public-input projection and descriptor count
    blind_from: [research/producer/, experiments/EXP-example/runs/]
    phased_release:
      schema: sealed-blind-review/v1
      plan_path: ledger/handoffs/TASK-20261025-abcdef.yaml
      phase1_allowed: [inputs/public.json, ledger/handoffs/TASK-20261025-abcdef.yaml]
      phase2_allowed: [inputs/public.json, research/producer/, experiments/EXP-example/runs/]
      derivation_path: experiments/EXP-example/reviews/TASK-20261025-abcdef/derivation.json
      seal_path: experiments/EXP-example/reviews/TASK-20261025-abcdef/seal.json
      release_path: experiments/EXP-example/reviews/TASK-20261025-abcdef/release.json
```

All paths are relative to the repository. Absolute paths, parent traversal,
backslashes, duplicate canonical paths, symlink cycles and escapes are rejected. Read
events must name actual files. An allowlist may name directories; the phase-one
allowlist must not overlap any protected path. The bound plan file must contain
the actual complete plan being checked, including scalar types. Duplicate YAML
or JSON keys in phased plan/report files are rejected. Changing/composing the plan requires a
new prospective plan and seal; an addendum cannot insert a release into an old
blind contract.

The reviewer first writes a JSON derivation containing `task_id`, `generated_at`,
the exact phase-one `sources_read` list, and a nonempty `quantities` object. Before
unblinding, the Coordinator records a JSON seal with exactly these fields:

```json
{
  "schema": "sealed-blind-review/v1",
  "task_id": "TASK-20261025-abcdef",
  "recorded_at": "2026-10-25T00:00:04Z",
  "plan_sha256": "<SHA256 of the actual handoff bytes>",
  "derivation_path": "<the plan's derivation_path>",
  "derivation_sha256": "<SHA256 of the actual derivation bytes>"
}
```

Commit and archive the exact derivation and seal before releasing protected
sources. The release record has the same fields, its own later `recorded_at`,
and `seal_path` and `seal_sha256` binding the seal. It does not alter the seal.
Use aware UTC timestamps throughout, with
`plan < derivation < seal < release`. Future times relative to the checking
host's UTC clock are rejected; this sanity check does not authenticate times.

The final `review_attestation` retains its complete `sources_read` union,
`blind_from_respected: true` for phase one, and:

```json
{
  "phased_release": {
    "schema": "sealed-blind-review/v1",
    "events": [
      {"seq": 1, "kind": "read", "at": "2026-10-25T00:00:01Z", "source": "inputs/public.json"},
      {"seq": 2, "kind": "seal", "at": "2026-10-25T00:00:04Z", "artifact": "<seal_path>", "sha256": "<actual seal hash>"},
      {"seq": 3, "kind": "unblind", "at": "2026-10-25T00:00:05Z", "artifact": "<release_path>", "sha256": "<actual release hash>"},
      {"seq": 4, "kind": "read", "at": "2026-10-25T00:00:06Z", "source": "research/producer/collector.py"}
    ]
  }
}
```

Record every read event in order, including repeated reads. Sequence numbers
must be contiguous unique integers. The read-event union must exactly equal the
attested source list, and its phase-one subset must exactly equal the sealed
derivation's source list. All phase-one reads strictly precede the derivation and seal;
phase-two reads strictly follow release. Reads between the seal and release are
rejected. Exactly one seal and one unblind event must bind the actual files,
hashes and timestamps. Missing or malformed evidence fails closed. All existing
joint, verdict, sibling-blindness, scoped-lift and control requirements remain.

Phase-one source files with multiple hardlinks are rejected conservatively:
an allowed path must not be another name for a protected file's inode. This
does not detect arbitrary copied or embedded protected content; independently
controlled input provenance and session custody remain necessary.

This checker validates **content and declared chronology consistency**. It does
not authenticate the people recording events, prove that undisclosed reads did
not occur, establish independent publication or commit timing, or provide a
prescribed-computation proof. Independent session isolation, prospective archival
custody and the review's arithmetic obligations remain separate requirements.

Focused controls are in `tests/test_review_phase_seals.py`; run:

```sh
python3 -m unittest discover -s tests -p test_review_phase_seals.py -v
python3 -m unittest discover -s tests -p test_review_independence.py -v
python3 -m unittest discover -s tools -p test_review_independence_addenda.py -v
python3 -m unittest discover -s tools -p test_check_review_independence.py -v
```
