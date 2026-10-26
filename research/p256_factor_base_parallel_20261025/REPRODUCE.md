# Reproduce the local checks

The public branch and the sealed 716-file ZIP are different custody layers.
The ZIP is the proposed research delta on top of public commit
`c35b9da6a65e019eaa517fc1a5f7774428ff35db`. The later complete delivery archive
also includes the reference inputs, reviews, comparisons, corrections and
shared delivery files. Apply that complete overlay to public commit
`8068a7f07b9c5173ab672bced978003f85ca0173`. Neither archive contains downloaded
third-party papers.

Python checks used CPython 3.12.14, SymPy 1.14.0 and python-flint 0.8.0.
`requirements-study.txt` also pins the optional graph/report packages used in
this environment. Sage checks used `sagemath/sagemath:10.6`, digest
`sha256:19995db6194f4a4bab18ce9a88556fd15b9ed5e916b4504fefe618a7796ddbdb`.
Ghostscript 10.05.1 and Poppler are needed for the PDF compaction/text check.
The repository-prescribed `/usr/local/bin/python3` was absent; receipts record
the actual interpreter rather than pretending that requirement was met.

Use a separate checkout or scratch copy for a rerun, and choose fresh output
labels/directories according to each command record. The retained producer
and review artifacts are sealed inputs, not destinations to overwrite.

From the repository root, custody and exporter-software checks are:

```sh
python3 research/p256_factor_base_parallel_20261025/verify_delivery.py
python3 research/p256_factor_base_parallel_20261025/test_progress_export.py
```

Custody checks verify bytes, parsers, declared metadata amendments, retained
unknowns and PDF hashes. They do not certify prescribed execution, mathematics
or performance. The exporter tests use synthetic software fixtures and prove
that dirty working-tree data cannot change the committed-source metric.

The arithmetic replay commands and source/input digests are in each producer's
`execution.json`, `commands.md`, `commands.json` or `commands.log`. The separate
review entry points are under `reviews/`; their final `result.json` and seals
identify the exact independent files, commands and coverage. Their code does
not import producer arithmetic for the calculations labeled independent.

The exact cardinality screen can be regenerated to a new destination:

```sh
python3 research/p256_factor_base_parallel_20261025/screen_bounds.py /tmp/p256-counting-replay.json
python3 research/p256_factor_base_parallel_20261025/analysis/cartier-proposal/check_arithmetic.py
```

Render a report to a fresh stem from the study directory:

```sh
python3 build_reports.py --stem report-rebuild tracks/f1
```

The renderer uses the clarification source automatically where supplied,
checks extracted text before/after compaction and refuses an oversized PDF.
Review-specific delivery sources are named in their delivery records; full
plots remain editable SVGs even when the compact PDF uses a simpler diagram.

Current scientific boundaries remain explicit: no comparative performance
trial, natural large-base yield measurement, whole ECDLP solve, formal proof
certificate, hypothesis promotion or canonical review admission was completed.
`reviews/local-custody-exception.json` records the local-pushed-input exception;
each reviewer additionally records its actual checkout, blindness and model
limitations. The public-disclosure approval question is separate from these
mathematical and software checks.

Generated review SVGs were normalized for trailing whitespace after sealing. Their exact originals remain losslessly packed as `*.svg.original.gz`, with hashes and XML/path-equivalence checks in `archive/svg-formatting-corrections.json`. Rehydrate originals only in a scratch copy when checking those earlier reviewer seals; the mathematical source and certificate data were unchanged.
