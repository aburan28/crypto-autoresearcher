# Polynomial lattice integer-HNF transformation exhausts memory

- **Status:** investigating
- **Kind:** implementation bottleneck and resource limit; no mathematical obstruction established
- **Affected work:** EXP-IC-74cbb1, H-IC-4fb1db, RQ-IC-a39c7e, TASK-20261015-2454ff; [failed run](../experiments/EXP-IC-74cbb1/runs/RUN-IC-0dacba/execution-receipt.json), [inspected failure report](../experiments/EXP-IC-74cbb1/reports/run-20261015T0754Z/report.pdf)
- **Next action owner:** Executor TASK-20261015-59d003 for the exact-HNF repair; Coordinator for source custody and prospective successor admission
- **Last updated:** 2026-10-15

## Problem

The prescribed polynomial-lattice trial cannot finish because its integer-HNF transformation update raises `MemoryError` under the frozen 2 GiB address-space limit.

The frozen workload includes curves (43,1,0), (97,0,2), (101,2,3), windows 2/4/8, dense and finite-union sparse shifts for m=2/3, t=1/2, L=0/1, and separate m=2/3/5 density controls. Exact row rank, support, covolume and integer-lattice certificates must be derived before classifying the n=64, D=256, 4096-bit instrument caps. A shorter rationally independent row subset is not an acceptable replacement for the original Z-lattice. The exact triggering cell was not serialized and remains unknown.

## Evidence and uncertainty

- **Observed:** RUN-IC-0dacba ended with native `infrastructure_error`, driver exit 1 and checker returncode null. The traceback ends at `tools/lattice_ic_polynomial.py:197` while allocating `U[i]` in `_integer_row_hnf`. The eight runtime files are preserved in commit `38d2ea4496eb12bdfa4ae6c13d22d12b5f6cf56b`; the report is preserved in `cb2cb77badff469ea437971b90b27b2010934d38`.
- **Inputs:** source/authority commit `719e976e26b975fdc16e9c57a65cf240b50ebe25`; driver SHA-256 `3733ce902927979a91cb1e48a4e7b8a083ea0a18b0b215ad7078b7ad23dd39cc`; plan SHA-256 `09cd06c39a7b30bb4c5a76ec71639d74951d1b0ce8c03c9da3cae58a144bcb2a`; seed 1729; Linux RLIMIT_AS 2048 MiB.
- **Missing measurements:** no manifest or raw result was written. No relation/root/certificate yield, actual failing matrix dimensions, peak RSS or driver CPU measurement is available. Earlier in-memory work is not scored as a completed result.
- **Suspected explanation:** uncontrolled intermediate coefficient growth in the naive unimodular transformation is plausible from the allocation site, but has not been independently profiled. The recorded fact is the allocation failure.
- **Not established:** no scientific cap overflow, small-root impossibility, hypothesis falsification, generic ECDLP conclusion or performance advantage follows.

## What would unblock it

- [ ] An archived implementation repair computes exact HNF with both `H = C*A` and `A = D*H` for integer matrices, retaining the original weighted Z-row lattice and strict norm/root criteria.
- [ ] Meaningful non-study regressions cover dependent/nonprimitive rows and transformation growth; the polynomial and unchanged combined-interface tests pass. Scientific fixtures, target laws, caps and 2 GiB resource guard remain unchanged.
- [ ] A prospective additive amendment and native-ready successor contract bind the repaired sources and a fresh RUN ID, preserving the original failed plan, attempt and report.
- [ ] The admitted successor completes its full fixed schedule and separate certificate checker; independent lattice/cost review addresses the repair and retained failure.

These are exit conditions for this implementation obstruction. They would not establish a useful relation-construction advantage, novelty or cryptographic-scale transfer.

## Next discriminating step

- **Action:** execute the narrow two-file [HNF repair handoff](../ledger/handoffs/TASK-20261015-59d003.yaml), then archive source and approve a normal successor only after actual readiness.
- **Controls:** independent exact HNF comparison, two-way integer membership, nonprimitive/dependent-row counterexamples, original strict norm/dimension/root/lift tests and unchanged combined tests.
- **Limits:** the existing scientific scope/caps and 2 GiB guard; no silent resource increase, fixture substitution, rational row deletion, replay into the failed directory or altered acceptance criterion.
- **Outcomes:** a passing regression enables prospective admission; another resource or implementation failure is retained as an instrument limit. A mathematical observation requires actual serialized outputs and independent review.
- **Recheck:** accepted repair source, completed successor output/checker, or a new exact growth counterexample.

## Resolution and history

2026-10-15: opened after the first polynomial attempt failed during HNF transformation construction. Original eight files and the missing two outputs remain unchanged. Investigation continues; no research status changes.


2026-10-15 later operational outcome: repaired successor EXP-IC-66c447/RUN-IC-0d0c36 ended with actual `claim_expired`, null driver/checker returncodes, empty stderr and absent raw/manifest. This does not identify HNF as the active stage or establish a new HNF defect. Source software repair acceptance remains recorded; full-grid completion is still unestablished. The distinct [claim-authority/progress-observability problem](lattice-ic-polynomial-lease-progress-observability.md) owns prospective telemetry and longer normal-lease remedy after exact failed custody. The original MemoryError evidence and this record's full-grid/independent-review exit conditions remain unchanged.


2026-10-15 fresh attempt: accepted durable-telemetry source and exact same-grid approval now run as EXP-IC-9f9a4b/RUN-IC-fe080b under unchanged2GiB, normal upfront1440minute authority. A recorded active exact_integer_row_hnf start boundary identifies only a new attempt's current operational boundary; it is not a timeout, certificate failure, HNF repair refutation or diagnosis of the previous expiry. Full-grid completion and independent lattice/cost review remain unestablished; [continuation](../research/lattice_ic_experiments_20261015/coordinator/polynomial-telemetry-successor/continuation-20261015-active.json) retains the scoped evidence.
