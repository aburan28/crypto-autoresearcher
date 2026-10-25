# Current formal target provenance inventory

**Scope:** Static repository inventory at main `0b38ac1157f777cb4a77d35e53d7ed583c541eb4` (formal tree `96f334e856c87d397b5db720899d833a75db0352`). This is an evidence review, not a research run or a proof of claim fidelity. The machine-readable [inventory](provenance.json), [builder](build.py), [diagram source](coverage.dot), [rendered diagram](coverage.svg), and [PDF](report.pdf) are kept together. The inventory records the Git blob ID and SHA-256 of every declared source, target spec, and theorem file.

## Observation

| Static fact at the named commit | Count |
| --- | ---: |
| Target YAML specs | 87 |
| Declared theorem paths that exist as Git blobs | 87 |
| Distinct declared source paths | 30 |
| Specs containing a canonical `EXP-*` identifier | 12 |
| Source paths directly under `experiments/` | 6 |
| Declared source paths inside `/runs/` | 0 |
| Specs with an explicit `/runs/` path or `RUN-*` reference | 0 |

The 12 `EXP-*` references name two experiments: `EXP-BINSTD-8bdf86` and `EXP-FROB-91ee9c`. Source status labels in the specs are 54 `COMPUTED`, 23 `PROVED`, eight `STATED`, one `DERIVATION`, and one `MEASURED_WITH_ALGEBRAIC_EXPLANATION`. These are source labels, not independently checked outcome tiers. The builder checks unique task and claim IDs, parses every YAML spec, and reads the source and theorem bytes from the named Git commit. It does not use the working tree as evidence for those source bytes.

![Static provenance topology; dashed links are open obligations](coverage.svg)

The diagram shows declared links and two missing evidence classes. An absent direct run path in a spec does **not** show that its source document lacks provenance elsewhere. A generic mathematical theorem can be useful without an experiment ID. Conversely, the presence of a theorem file does **not** show that it compiled at this commit or proves the source claim. No new speed, success, attack-cost, or experiment-validity conclusion follows from these counts.

## Interpretation and limits

The previously archived full per-target sweep covered 84 targets on an earlier pinned formal tree. Three targets were added later and have separate exact-source receipts, but there is no fresh full 87-target sweep or independent semantic sign-off across this current set. Existing proof receipts remain valid for their pinned bytes; this report does not broaden them to the current tree. The open [semantic fidelity problem](../../../problems/formal-target-semantic-fidelity-unreviewed.md) remains the controlling limitation.

For each claim that might be promoted to a dashboard or scientific conclusion, the next review must name the source and any frozen run record, exact theorem statement and assumptions, the model bridge, controls, and independent reviewer conclusion. Empirical measurements may have no appropriate Lean theorem; their provenance, controls, units and uncertainty need separate validation. The Semaev first-fall correction is a known reason to check meaning instead of counting compiled declarations.

## Graph and dashboard disposition

This report adds a provenance topology diagram generated from the static inventory counts. It changes no canonical scientific graph because it records no new experiment result or decision. Existing measured dashboard values are unchanged. The public Pages snapshot remains gated on current-head PR checks and a full-history build from merged main; this static inventory does not authorize publication.

## Rebuild and falsification check

From a checkout containing the named Git commit, run `python3 docs/reports/2026-10-25-formal-target-provenance/build.py`, then `dot -Tsvg coverage.dot -o coverage.svg` and `dot -Tpdf coverage.dot -o coverage.pdf` in this directory. The builder fails if a declared source or theorem path is missing, a YAML schema differs, or task/claim identifiers collide. The pinned `source_sha256` values permit later byte-for-byte drift checks. A byte match establishes custody only, not semantic fidelity.
