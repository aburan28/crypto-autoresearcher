# RM Kummer FFT rounding guard correction — 2026-10-25

## Scope and observation

This is a source-code validation and repair of `harness/endosweep/rmkummer.py` at main snapshot `af671797aac46cee67b8781ade98d331c4711f4e`. It does not rerun or change the archived 2026-10-08 RM Kummer survey, its counts, or a performance dashboard value.

The frozen survey README says the FFT point counter raises if its correlation is more than `10^-3` from an integer. The code instead required **both** `err > 10^-3` and `err > 10^-6 * max(1, max(abs(S)))`. Thus the synthetic output `S = 6000.003` has `err = 0.003` but passes the old guard because `0.003 < 0.006000003`. Nonfinite output also bypassed those comparisons. These are source-level counterexamples to the stated guard, not observed outputs of the historical survey.

The correction rejects nonfinite output and raises whenever the residual exceeds `10^-3`, matching the documented check. [The guard diagram](guard.svg) shows the repaired path and the separate archival-validation boundary. Its editable source is [guard.dot](guard.dot).

## Validation and limits

The targeted regression test injects the synthetic `6000.003`, NaN and infinity outputs and requires `ArithmeticError`. The existing small-prime family-count test compares FFT-derived Jacobian orders with brute-force orders on sampled nonsingular curves at `p = 101, 109`. The test command is:

```sh
/var/tmp/rm-fft-venv-20261025/bin/python -m pytest -q tests/test_endosweep_rm_qcurves.py -k 'fft_rounding_guard_rejects_bad_output or fft_family_counts_match_bruteforce_orders'
```

Result: **4 passed, 11 deselected** for that targeted command. A complete run of `tests/test_endosweep_rm_qcurves.py` also passed **15 of 15**. The isolated environment supplied NumPy 1.26.4, SymPy 1.14.0 and pytest 8.4.2; the path above identifies the actual host command and is not a repository dependency. Build the visual and PDF from this directory with `dot -Tsvg guard.dot -o guard.svg`, `dot -Tpdf guard.dot -o guard-diagram.pdf`, `pdflatex -interaction=nonstopmode -halt-on-error report.tex`, and Ghostscript `pdfwrite` with `-dPDFSETTINGS=/screen` to keep the final PDF below the 64 KiB artifact limit.

The fixed residual check is a numerical consistency guard, not a proof that every rounded integer is the true character sum. A floating point result can lie within the threshold of an incorrect integer. The archived summary has 56,630 RM members, 5,628 split cases and 859 recorded hits; its summary arithmetic and hashes were separately checked against named main snapshot `0b38ac1157f777cb4a77d35e53d7ed583c541eb4`, but there has been no independent exact replay of all members or verified original execution-source custody. Its 12 reported PARI spot checks do not replace that replay. These historical claims retain their previous validation status.

The remaining exact-census and source-custody obligations are tracked in [RM Kummer FFT census lacks all-member exact validation](../../../problems/rm-kummer-fft-counts-unverified.md). Future generated Markdown now describes rounded FFT outputs and this open validation limit rather than asserting that every computed count is exact.

No canonical graph receives a new measured value: this is a guard correction and a scoped implementation audit. The [PDF report](report.pdf) embeds the diagram. The original report and JSON remain immutable.
