# PQShield NIST PQC Signatures Zoo reference snapshot

This is a frozen **external reference**, transcribed from the user-supplied PQShield NIST PQC Signatures Zoo table on 2026-09-28. It is not an autoresearcher experiment, a security claim, or a current NIST status determination. The pasted table says its scheme specifications were last updated 2026-09-08; the benchmark environment is dated 2026-09-22. Check the upstream [zoo](https://pqshield.github.io/nist-sigs-zoo/) and [source repository](https://github.com/PQShield/nist-sigs-zoo) before using a row as current data. The pasted table SHA-256 is `ffa58df2fb1e183aa4b950908356e63a2f9d6a06676d9e699b18eaa774aa076b`.

`parameter_sets.csv` preserves all **87** displayed parameter rows across **15** scheme names, including three pre-quantum schemes (eight parameter sets) as controls. Key and signature sizes are integer bytes. Signing and verification timings retain the displayed units and precision; they are **not** normalized or measurements from this program. `source_status` and `source_marker` are copied labels, not independently verified classifications. The table's `pk_plus_sig_bytes` was checked against each row's sum.

## Benchmark provenance from the pasted page

- CPU: Intel Xeon Platinum 8488C, 16 cores, 2 threads per core; benchmark thread pinned to one core.
- OS: Ubuntu 26.04.1 LTS, kernel 7.0.0-1012-aws.
- Compiler: cc (Ubuntu 15.2.0-16ubuntu1); OpenSSL 3.5.5.
- Method: median over 1,000 iterations, fewer for slow schemes; `rdpmc CPU_CYCLES` for real core cycles in user space; `clock_gettime(CLOCK_MONOTONIC)` for wall time.
- The table's prose contains conflicting license labels: “benchmark data” CC-BY-4.0 and “data” CC BY-SA 4.0. Upstream's [repository README](https://github.com/PQShield/nist-sigs-zoo) says data CC BY-SA 4.0. Preserve attribution and recheck the applicable license before redistribution.

## Pinned implementation source snapshots

All 13 user-supplied source revisions are vendored under [`sources/`](sources/) as extracted GitHub commit archives. [`source_manifest.json`](source_manifest.json) records each full commit ID, archive URL, archive SHA-256, file count, and size. Each source snapshot retains its upstream license file. The archive URLs are commit-addressed; this import did not run or benchmark the implementations. Their relationship to each individual timing row has not been independently established. `fndsa` corresponds to the zoo's Falcon rows; `sdith` and `sdith2` are separate revisions of the same repository.

| Label | Source commit |
| --- | --- |
| faest | [faest-sign/faest-arch-opt@1d833097](https://github.com/faest-sign/faest-arch-opt/commit/1d8330979cb467c54edac43ffe695da249fa3417) |
| fndsa | [pornin/c-fn-dsa@33026d4d](https://github.com/pornin/c-fn-dsa/commit/33026d4d2734049a23f065f77eea11c35de58d76) |
| hawk | [hawk-sign/dev@1b9fef52](https://github.com/hawk-sign/dev/commit/1b9fef52559273fe7b40fe3e22968eaedd3a4c2a) |
| mayo | [PQCMayo/MAYO-C@74de637a](https://github.com/PQCMayo/MAYO-C/commit/74de637a7c4a7f9fafa888183bc05f5cf920cd2d) |
| mldsa | [pq-crystals/dilithium@6e00625c](https://github.com/pq-crystals/dilithium/commit/6e00625c5b29f516c6de973fe2ee2fbb150973f9) |
| mqom | [mqom/mqom-v3@d9c64e38](https://github.com/mqom/mqom-v3/commit/d9c64e386b186ee186684a0389fc32009bd67cd1) |
| qruov | [qruov/round3@3d84d0f6](https://github.com/qruov/round3/commit/3d84d0f6afae80c88deefab03b1dd6633a147f96) |
| sdith | [sdith/sdith@fff41ae5](https://github.com/sdith/sdith/commit/fff41ae5b12ba3c6b90d8f97b2ede57aa277a92f) |
| sdith2 | [sdith/sdith@ce7adf06](https://github.com/sdith/sdith/commit/ce7adf06476674d4ff990f378f83f9981cd6745b) |
| slhdsa | [pq-code-package/slhdsa-c@fac08b7d](https://github.com/pq-code-package/slhdsa-c/commit/fac08b7d0a93849de0ee163c63712395e012b38c) |
| snova | [PQCLAB-SNOVA/SNOVA@9b29c1e3](https://github.com/PQCLAB-SNOVA/SNOVA/commit/9b29c1e332cbd85757c8d6362a57b9a8c8298a38) |
| sqisign | [SQISign/the-sqisign@6d017708](https://github.com/SQISign/the-sqisign/commit/6d017708db403bf83977fa70770fc4f7f9e9ff21) |
| uov | [pqov/pqov@fac2ec1f](https://github.com/pqov/pqov/commit/fac2ec1fe6d8ea508eab4b98eb5341e1eed930a4) |

## Existing research-goal coverage

The zoo's twelve post-quantum scheme names map to existing goals: FAEST → `GOAL-FAEST-001`; Falcon/FN-DSA → `GOAL-FNDSA-001`; HAWK → `GOAL-HAWK-001`; MAYO → `GOAL-MAYO-001`; ML-DSA → `GOAL-MLDSA-001`; MQOM → `GOAL-MQOM-001`; QR-UOV → `GOAL-QRUOV-001`; SDitH → `GOAL-SDITH-001`; SLH-DSA → `GOAL-SLHDSA-001`; SNOVA → `GOAL-SNOVA-001`; SQIsign → `GOAL-SQISIGN-001`; UOV → `GOAL-UOV-001`. The ECDSA, EdDSA, and RSA rows are classical comparison controls. This reference snapshot does not change any goal or hypothesis state.

## Local deviations from the pinned archives

- `sources/sqisign/src/quaternion/ref/include/quaternion.h`: upstream commit `6d017708` ships an unresolved merge-conflict marker block (`<<<<<<< HEAD` / `=======` / `>>>>>>> main`) inside the Doxygen comment for `QuaternionResponseComputation`. This repository's merge-hygiene gate (`tools/check_merge_hygiene.py`, run by CI) refuses any tracked file containing such markers, so on 2026-09-30 the four marker lines and the `main`-side alternative brief were removed, keeping the `HEAD`-side comment text. No code changed. The exact edit is [`local-deviations/0001-sqisign-quaternion-h-drop-upstream-conflict-marker.patch`](local-deviations/0001-sqisign-quaternion-h-drop-upstream-conflict-marker.patch). `source_manifest.json` still records the untouched upstream archive hash, so this one file differs from that archive by exactly that comment. Every other file in `sources/` is verbatim.
