# Frozen candidate for larger solver validation

This source extends the public-input decoder from `harness/classical_ecdlp_followup/src/decoder.cpp` to the new 12/14/16/18-bit subgroup confirmation cohort. The old source remains unchanged. This directory contains no cohort targets or scalar-label files, and no confirmation targets were opened while the candidate was developed.

The secondary confirmation matrix preserves the previous candidate's four features (`x_mod_7`, fifth residue where applicable, `x_hash_7`, constant), model/exact prefix modes, beams 1/8, 2,048 unlabelled training samples, 512 heldout samples, four public offset views, Laplace pseudocount one, range-aware score, RNG seed domains and all-candidate public verification. It performs no full subgroup orbit construction or point census.

The source changes are input bounds and modular arithmetic reassociation, a functional API, stage measurement, and a switch for optional diagnostics. The public guards accept p≤1,048,575 and prime subgroup r≤524,287; the new frozen cohort is narrower. Whole-curve cardinality remains a trusted public certificate. Prime field/subgroup, nonsingularity, Hasse interval, cofactor coprimality, prime-order base and target membership checks remain. The bounded N sanity guard precedes squaring the Hasse trace.

## CLI and public API

Compile `main.cpp` as one C++20 translation unit. It includes `decoder.hpp`, whose implementation is exposed to the baseline/hybrid runner as a single-TU header. Do not link the separate CLI main into a baseline executable.

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wconversion -Werror candidate/main.cpp -o /tmp/solver-candidate
/tmp/solver-candidate --self-test
/tmp/solver-candidate --run FIXTURES_TSV PUBLIC_TARGETS_TSV FRESH_OUTPUT_JSONL
```

The `--run` route is a scientific measurement command only under the new admitted source-bound plan and live executor claim. Existing output files are refused. Input TSV formats are unchanged. Private scalar columns, duplicate IDs, noncanonical infinity, off-curve targets and unknown fixture IDs are refused.

The baseline runner includes `../candidate/decoder.hpp` and uses:

- `dec::Ops`, `Cost`, `difference`, `cost_json`, `Target`, public parsers, and `lab::Fixture`.
- `train(f, dec::Kind::xmod7, ops, false)` for the primary standalone kernel. It preserves the exact trained kernels and RNGs while omitting optional heldout, Dobrushin and mixing diagnostics. `diagnostics_performed` is false; absent costs/times are zero because that work was not executed. `emit_kernel` refuses such a model, preventing unmeasured diagnostic arrays from being serialized as observations.
- `make_views(f, target, model, ops)` for the four target-independent public offsets and their terminal feature labels.
- `solve_candidate(f, target, model, views, 8, true, ops)` for the primary exact-prefix beam-eight candidate.

`CandidateResult` exposes `search.candidates`, scores and live-payload sizes, `verified`, `hits`, separate `inference` and `verification` operation vectors, their `total`, and stage CPU/wall seconds. Every returned scalar is checked, including failures. The optional verified scalar is set only by the full public point equation; it never feeds back into candidate generation.

The complete primary hybrid is implemented by the baseline runner: on a candidate miss it calls the same measured rho fallback used in the named baseline. A successful fallback validates the composite, not the candidate alone. Fresh primary `Ops`/training is measured separately from the secondary matrix; later secondary features can reuse the documented Tonelli cache and are not independent cold setups.

## Measurements and records

Kernel rows retain separate construction and heldout counters and wall/process-CPU seconds. Target rows retain shared view counters/time, inference counters/time, verification counters/time, and their combined operation vector. Wall time uses `steady_clock`; CPU time uses the process CPU clock in the single-threaded executable. These unlike units are not added. The primary runner records its outer whole-process CPU envelope as well.

The row scope is `larger_solver_validation` and the track is `solver-candidate`. Rows remain `kernel`, `target`, or structural `not_applicable`. The standalone matrix's exact count is `4 * T * K + 4 * F`, where T is targets per fixture, K is the number of applicable fixture-feature pairs, and F is fixtures. For 48 fixtures with 16 targets each this is `64*K+192`, at most 12,480 rows. No missing or zero-hit target case is omitted.

Fixed developer serialization checks currently observe target rows below 4.7 KiB and kernels below 8 KiB. Larger decimal coordinates/counters increase those lengths. A conservative source-bound storage estimate is 8 KiB per target row and 16 KiB per kernel row; the driver must retain overflow rather than truncate. The scientific partition manifest must bind complete reconstruction, not these estimates alone.

## Developer evidence and limits

The inherited checks plus fixed larger-domain and functional-API controls total 2,966 assertions. The fixed CLI controls make 333 assertions over 48 tiny developer rows and independently verify every returned candidate with separate Python arithmetic. Positive, miss, identity, malformed-input and overwrite controls are included. New fixed arithmetic fixtures are explicitly excluded from confirmation sampling.

Diagnostic-free and full modes are checked for identical training counts, probabilities, public views, candidate lists, scores and verified outputs at both widths and prefix modes. Operation-vector stage sums reconcile. These are development checks and source-interface tests; they do not constitute independent scientific review, a formal blindness guarantee, an exponent estimate or a measured baseline improvement.

Original source SHA-256: decoder `7ffb572cac3dea4251b1e3c8b3d6e61c7959e789043f1b7e1105b173ad6d118a`, common header `f4620ba53737f547f109cebc0b380a842ba0208c302b2103675c2446efd0dcaf`. See `source-manifest.json` and `tests/development-checks.json` for the actual new bytes and check receipts.
