# Fresh native index-calculus builder stalls before main on the current macOS host

- **Status:** `investigating`
- **Kind:** access/tool limit; exact wide-field fallback implementation gap
- **Affected work:** [TASK-20261017-08bc0f](../ledger/handoffs/TASK-20261017-08bc0f.yaml), [the packed-tail engineering report](../research/icperf_prime50_packed_tails_20261017/report.md), and the [full-width arity grid](full-width-ic-arity-grid-unmeasured.md)
- **Next action owner:** Coordinator for a runnable follow-on handoff; executor for a controlled host or exact wider-field backend
- **Last updated:** 2026-10-17

## Problem

Freshly compiled arm64 Mach-O executables on the current macOS host failed to reach `main` within a five-second diagnostic window, so the new `__uint128_t` packed-tail builder has not yet been validated here for prime fields above the alternate Numba backend's proved `p<2^50` range. This blocks a verified full-width prime-field table-construction result for later 51–63-bit fixtures and any complete-cost inference using that native path. The 50-bit prime-order fixture has `p=1125899798684033<2^50`; its Numba path is separately tested and does not resolve wider fields.

## Evidence and uncertainty

- **Observed:** Both `/usr/bin/clang++` and `/usr/bin/c++` compiled a fresh `#include <cstdio>` executable that immediately prints `hello`; each build exited 0, but each execution timed out and was killed after 5 seconds. The control was repeated outside the filesystem sandbox with the same timeout. A freshly compiled `wide_tails.cpp` binary also emitted no first instrumentation line; `sample` placed 885 samples in `_dyld_start`, and `lsof` showed its input file was not opened. Ad hoc code-sign verification succeeded; re-signing did not change the five-second result. An independently built trivial dynamic library initially stalled on `ctypes.CDLL` load, but that same pending call later completed and returned 42; its elapsed time was not recorded. This late completion leaves a long startup delay as a live alternative to a persistent launch block. Exact code, bounded control commands and effects are recorded in the [engineering report](../research/icperf_prime50_packed_tails_20261017/report.md); the current source is [wide_tails.cpp](../src/crypto_autoresearcher/index_calculus/wide_tails.cpp).
- **Observed alternate path:** The exact corrected-quotient Numba backend passed seven small-control tests, including the same 50-bit fixture at tail arities 2, 3 and 4, on 2026-10-17. Its arithmetic precondition is `p<2^50`; see [wide_tails.py](../src/crypto_autoresearcher/index_calculus/wide_tails.py) and [the controls](../tests/test_index_calculus_wide_tails.py). The B=132, h=4 build completed with 104,294,212 entries and the archived checker passed; its 1,668,707,392-byte full table remains local-only. The [source snapshot receipt](../coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-eb1158/archives/TASK-20261017-acf159/snapshot-receipt.json) binds the code and report, not the full table bytes.
- **Derived or proved:** The native launcher stall precedes the builder's first instruction in the observed controls. This local behavior does not prove a general macOS restriction or any mathematical limitation. The Numba quotient correction has a stated bound only for `p<2^50`.
- **Suspected explanation:** Local loader, code-signing, endpoint security, or host-runtime startup delay; unconfirmed. A longer bounded replay of the hello controls and a fresh executable on a clean controlled host would distinguish a local delay from a persistent block or source-level bug.
- **Missing capability:** A controlled runtime that launches fresh native binaries, or an independently validated exact modular arithmetic fallback for every required `p<2^63` fixture under the same memory and wall bounds.
- **What this evidence does not establish:** No conclusion about degree of regularity, factor-base quality, relation yield, rank, complete IC cost, or prime-field security follows from an executable that did not start.

## What would unblock it

- [ ] On a controlled host, both independent hello controls exit 0 and print `hello` within 5 seconds, then the native builder passes full scalar parity for p=1019 and the certified 50-bit fixture at h=2,3,4; record executable digest, host, exact commands and raw logs.
- [ ] For any 51–63-bit prime fixture pursued without that host, supply a mathematically justified exact `p<2^63` fallback, independent modular-product tests at boundary operands and random seeded operands, full small-table parity, and measured bounded construction.

Either route would unblock only table construction. Wide decomposition scans, elite-base algebra, useful relations, rank, linear algebra, complete per-target costs and matched rho still require separate admitted work.

## Next discriminating step

- **Action or proof obligation:** First run the existing hello controls with a 60-second startup window on this host and record time to first output; then run a 50-bit small-tail parity control here or on a clean host. If native execution remains unavailable within the stated window, specify and independently test an exact 63-bit JIT modular product before extending the table builder.
- **Inputs and controls:** Fresh `clang++` and `c++` builds, the archived p1019 and 50-bit small-x B8 fixtures, original scalar `TailTable`, altered point/code/orientation controls, and the same source digest.
- **Execution limits and stop condition:** The historical controls stopped after 5 seconds. The proposed next diagnostic stops after 60 seconds per hello control; any later full table attempt uses a separately frozen handoff with explicit RSS, disk, wall and custody limits. Do not reinterpret a timeout as a negative algebraic result.
- **Outcomes and next actions:** A launching host plus parity promotes native engineering validation; a parity failure sends the source for correction; a repeat pre-main stall keeps the runtime impediment open; a proved and validated JIT fallback can bypass it for the specified field range.
- **Recheck trigger:** Controlled runtime becomes available or a wider exact fallback is implemented.

## Resolution and history

2026-10-17: Opened after repeated five-second fresh-binary pre-main stalls and a working 50-bit Numba control path. A previously pending trivial dynamic-library load later completed, so the next control now measures a longer startup window. The 50-bit B=132 build and source archive later completed under TASK-20261017-08bc0f and TASK-20261017-acf159; this does not validate the 51–63-bit native path. Unresolved.
