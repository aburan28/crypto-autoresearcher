# EXP-ECDLP-a98ea9 stage-two run manifests do not parse

- **Status:** `open`
- **Kind:** archived evidence parseability and source custody
- **Affected work:** [EXP-ECDLP-a98ea9 implementation](../experiments/EXP-ECDLP-a98ea9/implementation.md), its [S2](../experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2/manifest.yaml), [S2b](../experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2b/manifest.yaml), and [S2c](../experiments/EXP-ECDLP-a98ea9/runs/RUN-ECDLP-a98ea9-S2c/manifest.yaml) manifests
- **Next action owner:** coordinator to assign an additive archive correction and independent review
- **Last updated:** 2026-10-25

## Problem

Three frozen stage-two `manifest.yaml` files cannot be parsed as YAML because
`git.dirty_summary` contains unquoted, unindented multiline `git status`
output. Their fields cannot be accepted as machine-readable run evidence until
an additive, source-bound correction is reviewed. Preserve the originals.

## Evidence and uncertainty

- **Observed:** A PyYAML `safe_load` sweep of 3,585 immediate `runs/*/manifest.yaml`
  blobs in Git tree `165d8c0bc4ff6e7d419eaa0f6c5db1e0a5415518` at commit
  `5998553341fb29d3b9ca1a4c9ac6e58d96ca3ffa` parsed 3,582 and rejected
  exactly the three linked files. The only experiment-tree change through main
  `e6b61d8fa4b4d0b4d8229c37b02c74f3cf9afd90` added a PEXT Lean manifest.
  The original SHA-256 values, in S2/S2b/S2c order, are
  `68aa48e22dcb0b8ffe7999908850b80f6b57f8ff5c7dcece0e7eb4a1e403f4fa`,
  `9d2d75c90e166ca9e920228f3e59709c41d45bbc74319dea2c5485e12803942f`,
  and `8d0fb05253c63b617941cc3e5dfb6af1dce9b72f491de4213c0fd351f8900656`.
  Reproduce with `yaml.safe_load` on each linked file.
- **Observed text, not a parsed verdict:** S2 and S2b contain
  `validity.status: gate_failure`; S2c contains `validity.status: valid`.
  Text matches do not validate the runs or their claims.
- **Derived or proved:** The YAML syntax failure is reproducible on the exact
  tracked bytes. No cryptanalytic result follows from this finding.
- **Future-writer repair:** `implementation/runrecord.py` now serializes every
  string value as a JSON string literal, which PyYAML reads as a YAML string.
  It also emits empty lists and maps explicitly instead of YAML nulls.
  [Regression tests](../experiments/EXP-ECDLP-a98ea9/implementation/test_runrecord.py)
  cover multiline `git status` output, string values resembling numbers or
  booleans, and empty collections. Four other parseable manifests from this
  experiment round-trip with unchanged parsed data. This changes only future
  manifests; it does not repair the three archived records.
- **Suspected explanation:** The writer serialized multiline `git status`
  output as a plain scalar. Whether other run fields are accurate remains
  unreviewed.
- **Missing capability:** A reviewed additive correction binding each original
  hash, with every intended field sourced and a consumer that selects it
  explicitly.
- **What this evidence does not establish:** It does not show that S2c's
  computation failed or succeeded. The current merge-hygiene parser checks
  ledger YAML and experiment specifications, not `runs/*/manifest.yaml`.

## What would unblock it

- [ ] Preserve the originals and add a versioned parseable correction for
  each, naming its original path and SHA-256. Change no observed result field
  without separately sourced evidence.
- [ ] Independently parse the corrections and their referenced raw outputs,
  verify artifact hashes and execution identity, and adjudicate each stage-two
  gate under its frozen specification.
- [ ] Make consumers select the reviewed correction explicitly and reject an
  unparseable original without inferring a `valid` verdict.

These conditions establish machine-readable custody. They do not themselves
prove a stage-two cryptanalytic claim or performance result in Lean.

## Next discriminating step

- **Action or proof obligation:** Produce a field-by-field diff between the
  originals and proposed parseable corrections; independently review the raw
  outputs and hashes.
- **Inputs and controls:** Use the three SHA-bound manifests, their command,
  environment and raw files, the frozen specification, and a changed-hash
  negative control.
- **Execution limits and stop condition:** Archive validation only; no new
  scientific run is authorized. Stop promotion on any unsourced field or hash
  failure.
- **Outcomes and next actions:** A matching correction enters run
  adjudication; a mismatch or missing output keeps that run unresolved.
- **Recheck trigger:** Reviewed corrections and independent validation receipts.

A planned correction is not a completed experiment.

## Resolution and history

- 2026-10-25: Opened after the exact-tree sweep reproduced the three parser
  failures. The future writer was repaired and tested. No original artifact
  was changed or promoted.

Unresolved. Recording this problem does not establish a research result.
