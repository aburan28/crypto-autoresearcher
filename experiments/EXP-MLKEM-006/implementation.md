# EXP-MLKEM-006 implementation notes

Executor task: `TASK-20260724-933`. Observations only.

## Repairs relative to EXP-MLKEM-004

- Replaced harness-tautology synthetic control with `CTRL-TRUE-LIBRARY-PATH-INTERPOSITION` (`library_path_interposition.py` + injected `defective_compare` object via dlopen).
- Scoring derives G2/G3 marginals from compare_rc observations only; does not special-case single-diff mutations.
- Second peer: re-check strict fixed-bound once; if empty, lock `criterion_used=widened_optimized_compare` and pin PQClean ml-kem-1024 avx2 verify.
- Exact argv in every `command.txt`; build wall-clock in `/tmp/exp-mlkem-006/pre-run/build_timing_receipt.json`.
- Anchor grade cites the file actually validated against.
- claim_tier remains `laboratory_implementation_conformance`.

## Scope

No key recovery, oracle construction, exploitation path, disclosure, or deployed-system interaction occurred. Library comparison logic was not modified.
