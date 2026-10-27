# CCR root matching on the fixed NIST/ANSI cohort

The missing historical selector remains unresolved. Corrected CCR recovery
finds every one of 112 rational cyclic kernels across 147 curve/degree cells.
All eleven reconstructed omissions and all ten publications enter a favorable
case at degree seven or higher. No cohort input has the tested projection
collision or repeated-root complication. The literal-draft conversion finds
no kernels at degree five or higher, including for the publications.

The subsequent [finite two-predicate audit](two-rule-audit-20261027/report.md)
tests combinations directly: 1,913 frozen predicates reduce to 495 observation
signatures, with zero robust or possible fits among 122,265 signature pairs
and all 16 Boolean functions per pair. This includes local CM splitting,
power residues of j and coefficients, all 61 source-table root levels, and
recorded validation features. Its scope is two atoms from that library;
arbitrary complex or field-dependent rules remain outside that result.

The [signed Frobenius extension](signed-frobenius-20261027/report.md) adds
full torsion actions and source eigenvalue-list metrics. It finds 16 exact
retrospective signature-pair fits, including a two-cap separator at auxiliary
prime 199 covering all ten publications and eleven omissions. Independently
frozen source-policy checks expose the remaining gap: uniform caps reject
every publication, unknown-degree mode loses four, and the later counter's
reported working-prime traces stop below 199 on all omissions. Every fit and
counterexample is retained; historical use remains unestablished.

Read [the report](report.md), its inspected [PDF](report.pdf), the complete
[21-curve comparison](comparison.csv), and the [147 cell results](cells.csv).
These are reconstructed omissions, not documented historical rejection events.
Fresh mathematical projection root sets are reconstructed; historical q-series
tables, executable use, root order and stopping policy are not established.

The source distinguishes auxiliary-prime selection from curve selection:
without a suitable root, advance to the next auxiliary prime; choose a
non-repeated S1 root; try quotient-coefficient pairings and validate the kernel.
The special-j controls exercise projection collisions, including a repeated
S1 value already excluded by that source root rule. No cohort case has it.

## Exact replay

Check [BUNDLE.json](BUNDLE.json), extract the archive, and run under a Python
environment with `python-flint==0.9.0`:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/verify.py
python3 -B audit_publication.py evidence
```

The full replay passed after archive extraction into a different directory;
[portable-replay.stdout](portable-replay.stdout) retains the result. Neither
auditor invokes an external scientific producer or network. FLINT arithmetic
runs in process. [FLINT-RUNTIME.json](FLINT-RUNTIME.json) pins the runtime used.
The second auditor binds all public mirrors, both full-identity CSVs and the
source-rule summary to that export.

The 65-file export retains all three native attempts and their process and
case framing. Attempt01 stops at a control gate before cohort calls. Attempt02
starts all 147 cohort cells but leaves 46 partial after a reconstruction error
used inexact GP factorials. Attempt03 uses exact factorials and a maximum-degree
control, and all 147 cells finish. Those failures are operational observations;
they do not count as curve rejections. The original paper bytes, scan images,
interpreter and FLINT binaries are excluded explicitly, with exact digests and
retrieval locations retained.

## Derived artifacts and delivery

With ReportLab installed, `python3 -B make_report.py` regenerates the Markdown,
three-page PDF, quantitative SVG and workflow diagram from recorded values.
[workflow.diagram.json](workflow.diagram.json) is editable diagram data. Every
final PDF page was visually inspected. Earlier study figures retain their own
sealed-run scope; no canonical frontier or formal hypothesis state changes.

Canonical object-store delivery was refused with HeadObject403. Exact archive
bytes were pushed in Git under the existing `large-file-ok` PR exception. No
remote store success or green merge-readiness claim is made; the earlier
immutable A/A-record collisions remain a separate publication issue.
