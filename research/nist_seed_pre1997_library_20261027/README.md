# Recovered pre-1997 FreeLIP validation

This observation study retains the same 21 NIST/ANSI identities: ten publications,
eleven reconstructed omissions, and six recovered seed streams. The historical
selector remains unidentified. See [the report](report.md), its inspected
[PDF](report.pdf), and the full-identity [comparison](comparison.csv).

FreeLIP 1.0, recovered from two matching pre-1997 mirrors, completes the tested
coefficient, primality and RNG operations on every cohort curve. All 756
inversion/alias checks pass across two versions and two limb sizes; independent
arithmetic verifies 126 returned inverse integers. The 26-bit 1.0 build reproduces
all six May base-point x-coordinates after seven discarded draws. This is modern
LP64 execution, not authentication of the missing generator or original CPU.

The original compile failure and unavailable ASan fault demonstration remain
recorded. In the latter, one process timed out without probe output and a second
was sampled deadlocked in runtime startup, then interrupted. Missing capture is
not a mathematical rejection. The remaining ASan arms did not start.

## Portable validation

Check the archive digest in [BUNDLE.json](BUNDLE.json), then extract and audit:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/verify.py
python3 -B audit_bindings.py evidence
```

The first command creates `evidence/` in the current directory. Both Python
auditors are read-only, need only the standard library, and launch no native
programs or network requests. The two auditors passed after extraction into a
different directory. The raw export seals 3,688 files and retains 912 completed
process receipts, including unsuccessful processes. The top-level CSV uses LF;
the sealed raw CSV retains its original line endings.

The archive retains probes, frozen protocols, raw stdin/stdout/stderr and
receipts. Original noncommercial-licensed library source and binaries remain
in local custody rather than being redistributed in this derived archive.
[SOURCE.json](SOURCE.json) binds their bytes and external retrieval locations;
native reruns additionally require those exact sources and an appropriate C
toolchain. Portable replay verifies the recorded values, not native rerun claims.

## Regenerate communication artifacts

With ReportLab installed, `python3 -B make_report.py` regenerates the Markdown,
PDF and both vector figures. Its counts come from the sealed observations and
published summary. The editable workflow data is [workflow.diagram.json](workflow.diagram.json).
No scientific run is needed. The prior SEA and ECPP graph sets retain their own
unchanged sealed-run scopes; this study adds separate library-validation figures.

## Publication state

The scientific archive and both portable auditors pass. The refreshed-main
branch check exposes five inherited immutable A/A-record collisions, separately
bound in [PUBLICATION-STATUS.json](PUBLICATION-STATUS.json) and the canonical
[problem record](../../problems/nistseed-aa-control-and-store-delivery.md).
The new FreeLIP study does not edit those five frozen records. The PR is open;
this is not a claim that all merge gates pass.
