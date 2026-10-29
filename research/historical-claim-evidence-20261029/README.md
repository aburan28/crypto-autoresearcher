# Historical claim evidence register — initial partial seed

This is evidence-custody infrastructure for the historical validation goal,
owned by Conductor T-777. It makes missing links inspectable. It does not
decide mathematical validity, experiment validity, or official research status.

## Observed scope

`matrix.json` contains six selected claim rows across three repositories:
four commutative-ring identities from cryptanalysis, one reconstructed BINSTD
execution claim from auto researcher, and one interpretive boundary from
crypto's cover assessment. `integrity.json` records successful byte/excerpt
binding for 15 available sources (432,829 bytes) and one explicitly unavailable
elaborated-types record. These are register sizes, not a coverage percentage.
The individual-claim denominator is unknown.

The identity rows refer to the historical `0b353c9b...` producer source and
its archived native job. They do not extend that job's result to the current
integration head. J1/J2 reviews are historical scoped inputs. The BINSTD raw
records are reconstructed targets and witnesses, not original machine traces.
The cover row quotes the stated classification/implementation boundary; it
does not recompute catalog counts or establish a complete transfer pipeline.

## Prior source review and design

The existing `tools/formal_coverage_inventory.py` in crypto and cryptanalysis
counts source paths and lexical declarations. Auto researcher's
`tools/claim_class_audit.py` checks knowledge tags, and `tools/formal_task.py`
renders formal dispatch specifications. None supplies the missing complete
historical claim-to-proof/run matrix identified in
[`historical-experiment-lean-and-execution-coverage`](../../problems/historical-experiment-lean-and-execution-coverage.md).
This first register addresses exact bindings only. It preserves the
[`execution-proof-chain`](../../docs/execution-proof-chain.md) distinction
between receipt integrity and execution verification. Source provenance is
internal: each selected excerpt has a full commit ID, path, Git blob ID,
SHA-256, inclusive line range, and excerpt hash. No external literature or
new scientific mechanism is asserted by this implementation.

## Reader contract

The reader loads explicit local Git objects, disables replace objects,
lazy fetching and all Git transports, rejects symbolic refs, symlinks, noncanonical paths, changed
hashes, changed excerpts, duplicate JSON keys/IDs/references, and dangling
evidence links. Source reads are capped at 16 MiB per blob and 64 MiB total,
with the remaining allowance checked before fetching the next blob. The CLI
matrix input is capped at 16 MiB before JSON parsing. These are raw-byte caps,
not process-RSS limits: JSON objects, decoded Unicode and line splitting use
additional RAM. Large or
unavailable evidence must have an explicit unavailable record; it is not
silently skipped. No cloud fetch, build, proof run, or experiment is launched.

Roles are curated pointers. Even every required role being present yields
`scientific_validity: not_assessed_by_integrity_checker`. Missing roles remain
in the output; a successful exit means integrity only. The four claim classes
define minimum *inventory slots*, not a substitute for repository scientific
review contracts. Consumers must not treat `integrity_status: passed` as
scientific approval. The matrix declares partial coverage and nonempty
omissions; the tool cannot emit complete coverage.

The threat boundary trusts local Git, Python, and object storage. Git content
identity does not authenticate authorship or establish that an archived
receipt truthfully records execution. It also does not bind the entire
historical transitive execution chain automatically. Those remain review
obligations. The printed source statements do not substitute for elaborated
Lean declaration types.

## Reproduce

From this repository, with the three local repositories containing the
explicit objects (the required full IDs are in `matrix.json`):

```sh
python3 -m unittest tests.test_claim_evidence_matrix -v
python3 tools/claim_evidence_matrix.py \
  research/historical-claim-evidence-20261029/matrix.json \
  --repo auto=/path/to/crypto-autoresearcher \
  --repo cryptanalysis=/path/to/cryptanalysis \
  --repo crypto=/path/to/crypto \
  --output /new/path/integrity.json
```

`build_seed.py` reconstructs this initial register from the same frozen source
selection, with `PYTHONPATH=.` and `--auto`, `--cryptanalysis`, `--crypto`, and
`--output` arguments. Both commands refuse to overwrite an output. Missing
objects must be recovered through the existing approved custody workflow;
the checker does not fetch them. A future register revision is additive.

## Validation and communication

The initial eleven real-Git unit tests cover positive identity and adversarial refusal,
working-tree edits, replacement objects, unavailable evidence, role-complete
nonpromotion, and write-once receipts. The local seed check is retained in
`integrity.json`. The independent implementation review identified an aggregate
read-cap bug: the original checker rejected a source only after reading bytes
beyond its total allowance. The successor checks the allowance before fetching
the blob. Thirteen tests now pass (`unit-tests-v2.txt`), including pre-fetch
aggregate refusal and oversized matrix refusal. `integrity-v2.json` preserves
the successor reader's result; the original receipt remains unchanged. The
seed builder now uses the archive's full commit literal. Hosted CI and final
review of these fixes remain pending. The original PDF records the initial
publication stage and is preserved; these implementation fixes do not change
the evidence-flow diagram or claim/evidence contents.

`render_report.py` generates the companion diagram and one-page PDF from
the exact matrix and integrity receipt. This is an evidence-flow diagram,
not a new performance graph. The existing sheriff `sweep.svg`, known-label
proof-boundary diagram, and crypto cover-transfer graph retain their frozen
scope: this register makes no scientific decision that would change them.
It does not make the public dashboard or stale health snapshot current.

Next: expand the register from the remaining historical inventory, bind
missing protocol/execution/type artifacts, obtain independent fidelity and
execution reviews, and update affected canonical dashboards only from their
accepted evidence. Full historical validation remains open.
