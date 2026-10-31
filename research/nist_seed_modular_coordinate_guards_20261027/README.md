# Modular-coordinate and corrected-draft audit

The fixed cohort remains ten publications and eleven reconstructed omissions,
across six streams. The historical selector remains unidentified. Read the
[observation report](report.md), its inspected [PDF](report.pdf), and the
full-identity [comparison](comparison.csv).

The independent audit checks 1,281 coordinate specializations over 61 prime
levels through 293, with 1,185 rational parameters and 2,071 resulting
source/Fricke-target/Atkin fibers. None of the cohort inputs hits the tested
exceptional loci. Constructed ordinary positive controls do hit them.

The newly recovered Charlap-Coley-Robbins draft contains a printed coefficient
discrepancy explicitly corrected by Morain in 1995. Literal use fails every
degree-13 cyclic kernel over the algebraic closure of every cohort field,
including all ten publications. This is an exact source-based diagnostic,
not authentication of a historical executable or a full point-counter run.
The draft's separate root-matching step is not yet reconstructed.

## Reproduce the verification

Check the archive digest in [BUNDLE.json](BUNDLE.json), then extract and replay:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/verify.py
```

For independent rational-root completeness, run the same command with
`--fibers` under a Python environment containing `python-flint==0.9.0`.
[FLINT-RUNTIME.json](FLINT-RUNTIME.json) pins the wheel used here. The ordinary
replay requires only the standard library; the full root audit uses native
FLINT arithmetic in process. Neither invokes the external PARI/C++ producers
or the network. The full audit passed after archive extraction into a new
directory; [portable-replay.stdout](portable-replay.stdout) retains the result. The separate `audit_publication.py evidence` command
checks all reviewable mirrors and full-identity CSV rows against that export.

The 148-file export contains raw outputs, exact inputs, protocols, source
tables and their GPL notice, controls and unsuccessful preparation/verifier
attempts. [SOURCE-BOUNDARY.json](SOURCE-BOUNDARY.json) specifies deliberately
excluded publisher PDFs, images, binaries and duplicate normalized tables.
The unchanged sealed archive also preserves the pre-strengthening verifier;
the final verifier adds exact UID/cohort binding without changing native data.

## Figures and delivery

With ReportLab installed, `python3 -B make_report.py` regenerates the Markdown,
three-page PDF, quantitative SVG and evidence-flow diagram. Both SVGs have
editable source; workflow data is also in [workflow.diagram.json](workflow.diagram.json).
No scientific run is needed. Earlier study figures retain their own scope.

The object-store tool refused publication at its canonical `HeadObject` guard
with HTTP403. No remote upload is verified. The existing PR `large-file-ok`
exception retains the exact archive bytes in Git; the refusal is retained in
[STORE-DELIVERY.json](STORE-DELIVERY.json). The PR also has inherited immutable
A/A-record collisions; current validation metadata is recorded separately.
Neither a scientific solution nor green merge readiness is claimed.
