# Bounded export allocation candidate

This separate producer preserves the batched producer's matrix operations, elimination, projection, monomial order and certificate bytes. It changes only the admission formula and accepted resource-argument ceiling. The running campaign remains on its original binary.

## Source accounting

The existing batched exporter constructs `projection` with at most `work` rows and columns, then multiplies a window of at most 4096 map rows into that projection. It writes each product and frees it before creating the next. It never allocates a second full exported map. The old admission formula nevertheless reserved `2 * columns * stride`.

The candidate reserves `(columns + 4096) * stride` instead. The unchanged `3*work` term covers the relation matrix and projection at export (the relation matrix retains no more than rank plus the last chunk rows; the unchanged chunk allowance remains). During closure the unchanged relation, action, low-row and chunk allowances remain. The 35% margin, 64 MiB fixed allowance and padded strides remain. M4RI internal workspace and allocator behavior are still reasons for an enforced process address-space limit and pod memory headroom; this accounting is not a measured-RSS guarantee or a minimum-memory theorem.

The CLI ceiling is 96 GiB for this separately named candidate. A launcher must enforce at most 96 GiB address space, verify actual pod/host capacity, and refuse launch without placement and exclusive campaign ownership. Merely changing the CLI argument is insufficient. No large input has been run with this candidate.

## Exact admitted scope and next execution requirements

For the SHA-bound n47 random00 seed in `native-envelope-plan-001.json`, replacing only the full-export term gives 92,117,754,292 bytes (85.791 GiB) at chunk 60000, or 84,455,395,520 bytes (78.655 GiB) at chunk 4096. These are algebraic transformations of the retained structural counts, not new closure measurements. The original 64 GiB attempt remains a resource refusal.

The observed lab CPU pool limit is 128 GiB. A prospective 112 GiB pod with a 96 GiB process cap could accommodate the calculated envelope, but actual scheduling, runtime controls and memory admission remain unverified. Both current 48 GiB cloud workers must finish before this job is submitted; do not launch another panel worker into those reserved slots. The local campaign stays independent and unchanged.

Before a frontier run: retain software controls and source/binary hashes; package a portable worker; validate its runtime controls and resource admission; freeze a one-input continuation binding the original certificate, exact solution count zero, original independent checker, artifact uploads and watchdog. No LFD >= 6 claim follows until a degree-five certificate is independently accepted with positive codimension. A killed-constant projection, allocation/OOM failure or other refusal remains inconclusive.

## References and limits

Internal source review: `quotient_lift_batched.cpp` export and admission paths; `test_batched_export.py`; `validate_cascade.py`; `reports/native-envelope-001/report.md`. The change reuses existing batched multiplication and certificate validation, with no literature novelty or performance claim. Qualification receipts live in `validation/bounded-export-20261030/`.

## Worker qualification and publication

`run_lift_worker.py` and `runtime/bounded-lift-worker-manifest-002.json` define the portable worker. The request pins the exact manifest, and the manifest pins every executable, checker, fixture and driver. The local end-to-end control in `validation/lift-worker-20261030-v2/` passed all 47 artifact hashes; its degree-five codimension and exact count both equal 3, with no spurious LFD >= 6 field. A mismatched manifest was rejected before child execution.

The published archive is bound by `runtime/bounded-lift-publication-002.json`, including an anonymous download/hash verification. `runtime/bounded-lift-request-002.json` selects the retained n47 input and caps the child at 96 GiB within a prospective 112 GiB pod. This request is prepared, not a launch or a frozen scientific protocol. The worker checks finite cgroup headroom for cloud execution, reruns three candidate/checker fixtures, rechecks the D4 seed, recomputes the exact count, runs the D5 producer, and accepts a bound only after the original checker. It uploads closed stages, but cannot resume within native elimination. Actual cloud qualification and the one-input frozen protocol remain outstanding. Version001 is retained; version002 adds mandatory request-to-manifest binding.
