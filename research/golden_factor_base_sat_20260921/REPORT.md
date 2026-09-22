# Affine factor base SAT experiment: N7 checkpoint

The first affine-flat candidate did not meet its frozen speed or static-propagation thresholds. Independent finite replay confirms correct decomposition decisions, model validation and accounting. This result concerns the tested N7 implementation only; it does not close the affine-base approach or establish an IC-versus-rho comparison.

| Held-out cold wall comparison | Median paired ratio | Descriptive paired bootstrap 95% interval |
|---|---:|---:|
| Flat SAT / explicit same-base SAT | 1.2291 | 0.9731–2.1219 |
| Flat SAT / direct MITM | 1.7023 | 1.0162–2.6851 |
| Flat SAT / null-base SAT | 1.1056 | 0.8340–1.7126 |

Ratios above one mean the flat implementation was slower. All 70 control and 64 scientific outer workers completed validly. The two independent numeric derivations agree on all eight held-out ratios, the frozen bootstrap, and 276 semantic prefixes across six eligible cases. Neither encoding refuted a prefix through the specified unit/XOR propagation, so the median propagation advantage was zero. Both factor bases admit exact three-point decompositions for all 70 nonzero subgroup targets.

The candidate consists of 28 signed points on K1/F2^7. Although constructed from two affine 2-flats and their conjugates, only two of the eight seed values survived rational-point and odd-subgroup admission. The admitted domain therefore reduces to one affine line and its Frobenius shifts. This exact structural observation motivates the next experiment; it is not a demonstrated explanation of the measured timing.

The next ranked step searches the existing 37-orbit N19 pool for complete affine planes with four seed abscissae from four distinct full Frobenius orbits, all already admitted. Exact three-point coverage will be compared against the existing four-orbit control, which covers 6224 of 6909 signed Frobenius target orbits. SAT comparisons require a subsequent frozen contract and a strong same-domain baseline. Coverage is not solver ease.

Evidence: EXP-KIC-424885 / RUN-KIC-c2b1b7, scientific snapshot afad85a6dae42178feac397b25d7d7c99870fcf5, Coordinator DEC-20260921-735e48. The final v2 review combines an explicitly reused source-aware review with a separate permanently blind arithmetic/prefix replay. The canonical independence checker passes. A post-seal sibling status-summary exposure is explicitly disclosed; the report records no protected-file read or numeric exposure. This is not claimed to be an untouched blind session after sealing.

The original incomplete review and archive remain unchanged. The original solver tar contained a dangling executable symlink. A new regular-file bundle supplies bytes matching the historical executable/library digests and is disclosed as post-run retrieval; no portable replay environment is claimed. The original staged-unblinding checker failure is preserved, with the independent blind-only correction recorded separately.

Limits: tiny field, Python startup in cold measurements, one host, fixed target panel with orbit dependence, a particular explicit-domain encoding, no asymptotic inference. Construction is charged per point-decomposition query here; full single-target IC can reuse its own base across relation attempts, so these timings cannot be multiplied blindly into an IC estimate. No new rho benchmark was performed. The unrelated full-ledger validation still has ten existing AES-manifest errors; scoped new-record/run checks pass.

All sources here are internal experiment artifacts. Official hypothesis and goal statuses remain unchanged.
