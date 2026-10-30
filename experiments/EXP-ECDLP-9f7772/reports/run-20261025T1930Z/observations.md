# Recorded solver outcomes

All requested outcomes, including misses, failures, censoring and structural NAs, remain in the sealed records. Counts below refer to public target IDs; duplicated configurations and A/A repeats are not independent curve replications.

| Arm | Requested | Solved | Failed | Censored | Invalid |
| --- | --- | --- | --- | --- | --- |
| AutoRho | 768 | 768 | 0 | 0 | 0 |
| Rho A/A repeat | 768 | 768 | 0 | 0 | 0 |
| Candidate then rho | 768 | 768 | 0 | 0 | 0 |
| Bernstein–Lange precomputation | 768 | 768 | 0 | 0 | 0 |
| BSGS | 768 | 768 | 0 | 0 | 0 |

## Primary candidate alone and explicit fallback

| Panel | Bits | Targets | Candidate-only hits | Fallback calls | Hybrid statuses |
| --- | --- | --- | --- | --- | --- |
| full | all | 768 | 3 | 765 | {"solved": 768} |
| full | 12 | 192 | 2 | 190 | {"solved": 192} |
| full | 14 | 192 | 1 | 191 | {"solved": 192} |
| full | 16 | 192 | 0 | 192 | {"solved": 192} |
| full | 18 | 192 | 0 | 192 | {"solved": 192} |
| core | all | 192 | 1 | 191 | {"solved": 192} |
| core | 12 | 48 | 0 | 48 | {"solved": 48} |
| core | 14 | 48 | 1 | 47 | {"solved": 48} |
| core | 16 | 48 | 0 | 48 | {"solved": 48} |
| core | 18 | 48 | 0 | 48 | {"solved": 48} |
| extension | all | 576 | 2 | 574 | {"solved": 576} |
| extension | 12 | 144 | 2 | 142 | {"solved": 144} |
| extension | 14 | 144 | 0 | 144 | {"solved": 144} |
| extension | 16 | 144 | 0 | 144 | {"solved": 144} |
| extension | 18 | 144 | 0 | 144 | {"solved": 144} |

The complete hybrid is the frozen candidate followed on a miss by the named rho solver. Every fallback has the same deterministic arithmetic vector as its paired standalone rho arm. Candidate-only success is a separate field; a correct fallback answer does not establish candidate-only completeness. Primary and secondary x-mod-7/exact/beam 8 lists match, so their hits must not be counted twice.

## Required setup, target CPU and reuse

| Arm | Setup CPU(s) | Target CPU(s) | Total CPU(s) | Aggregate ms/target |
| --- | --- | --- | --- | --- |
| AutoRho | 0 | 0.308699 | 0.308699 | 0.401952 |
| Rho A/A repeat | 0 | 0.310823 | 0.310823 | 0.404718 |
| Candidate then rho | 0.275634 | 0.992687 | 1.26832 | 1.65146 |
| Bernstein–Lange precomputation | 0.0536332 | 0.131367 | 0.185001 | 0.240886 |
| BSGS | 0.00562228 | 0.0533561 | 0.0589784 | 0.0767948 |

These are sums of recorded method setup and target intervals, not the whole study CPU. The aggregate final column is a ratio of sums. The registered paired estimator gives each curve equal weight: for each curve, divide candidate method setup-plus-target CPU by the same curve’s rho CPU, then take the geometric mean. Full-panel setup reuse is m=16. The fixed core reuses setup over m=8 on 24 core curves. No secondary configuration or A/A rerun increases the number of distinct targets available for amortization.

Cold-use totals are reconstructed as recorded setup plus one recorded target interval. Setup was not independently rerun cold for every target. Whole per-arm CPU captures upstream hash/table/RNG work and candidate DP/log/sort work that EC field counters do not fully describe. Timing boundaries exclude common input validation, parsing, JSON/log formatting, module orchestration and final table teardown; none is silently claimed measured inside these intervals.

| Panel | Bits | Numerator/rho | Complete pairs/requested | Geometric mean | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| full | all | Rho A/A repeat | 48/48 | 1.00632 | 0.878921 | 1.14727 |
| full | 12 | Rho A/A repeat | 12/12 | 1.01297 | 0.953953 | 1.13347 |
| full | 14 | Rho A/A repeat | 12/12 | 0.990379 | 0.878921 | 1.09478 |
| full | 16 | Rho A/A repeat | 12/12 | 1.01755 | 0.898431 | 1.14727 |
| full | 18 | Rho A/A repeat | 12/12 | 1.0046 | 0.933733 | 1.08337 |
| full | all | Candidate then rho | 48/48 | 4.46058 | 2.75334 | 6.5497 |
| full | 12 | Candidate then rho | 12/12 | 5.91762 | 5.26162 | 6.5497 |
| full | 14 | Candidate then rho | 12/12 | 4.93346 | 4.20466 | 5.31359 |
| full | 16 | Candidate then rho | 12/12 | 4.27399 | 3.8669 | 4.91335 |
| full | 18 | Candidate then rho | 12/12 | 3.17274 | 2.75334 | 3.79914 |
| full | all | Bernstein–Lange precomputation | 48/48 | 0.540612 | 0.242839 | 1.70225 |
| full | 12 | Bernstein–Lange precomputation | 12/12 | 0.64914 | 0.242839 | 1.70225 |
| full | 14 | Bernstein–Lange precomputation | 12/12 | 0.406756 | 0.324679 | 0.605905 |
| full | 16 | Bernstein–Lange precomputation | 12/12 | 0.521443 | 0.387751 | 0.724888 |
| full | 18 | Bernstein–Lange precomputation | 12/12 | 0.620389 | 0.432439 | 1.05963 |
| full | all | BSGS | 48/48 | 0.165236 | 0.0808442 | 0.287414 |
| full | 12 | BSGS | 12/12 | 0.113981 | 0.0808442 | 0.146955 |
| full | 14 | BSGS | 12/12 | 0.149752 | 0.122824 | 0.174663 |
| full | 16 | BSGS | 12/12 | 0.194694 | 0.168368 | 0.24365 |
| full | 18 | BSGS | 12/12 | 0.22432 | 0.1817 | 0.287414 |
| core | all | Rho A/A repeat | 24/24 | 0.996069 | 0.873104 | 1.25557 |
| core | 12 | Rho A/A repeat | 6/6 | 0.968616 | 0.91049 | 1.01776 |
| core | 14 | Rho A/A repeat | 6/6 | 1.01423 | 0.899248 | 1.25557 |
| core | 16 | Rho A/A repeat | 6/6 | 1.00414 | 0.873104 | 1.06072 |
| core | 18 | Rho A/A repeat | 6/6 | 0.997881 | 0.901882 | 1.14749 |
| core | all | Candidate then rho | 24/24 | 5.38542 | 2.71707 | 8.53534 |
| core | 12 | Candidate then rho | 6/6 | 7.00968 | 6.2321 | 8.53534 |
| core | 14 | Candidate then rho | 6/6 | 6.55962 | 5.90326 | 7.17791 |
| core | 16 | Candidate then rho | 6/6 | 5.31779 | 4.7485 | 5.81305 |
| core | 18 | Candidate then rho | 6/6 | 3.44009 | 2.71707 | 4.2808 |
| core | all | Bernstein–Lange precomputation | 24/24 | 0.671105 | 0.291422 | 2.17765 |
| core | 12 | Bernstein–Lange precomputation | 6/6 | 0.642119 | 0.291422 | 2.17765 |
| core | 14 | Bernstein–Lange precomputation | 6/6 | 0.595802 | 0.460476 | 0.77815 |
| core | 16 | Bernstein–Lange precomputation | 6/6 | 0.71877 | 0.607729 | 0.939659 |
| core | 18 | Bernstein–Lange precomputation | 6/6 | 0.737658 | 0.57963 | 0.876545 |
| core | all | BSGS | 24/24 | 0.175868 | 0.106881 | 0.260868 |
| core | 12 | BSGS | 6/6 | 0.121063 | 0.106881 | 0.142947 |
| core | 14 | BSGS | 6/6 | 0.165417 | 0.115404 | 0.218164 |
| core | 16 | BSGS | 6/6 | 0.215218 | 0.185898 | 0.255919 |
| core | 18 | BSGS | 6/6 | 0.221963 | 0.182763 | 0.260868 |

Additional descriptive arithmetic references the documented precomputation baseline directly; these views do not replace the registered primary hybrid/rho comparison.

| Panel | Bits | Numerator/BL | Complete pairs/requested | Geometric mean | Min | Max |
| --- | --- | --- | --- | --- | --- | --- |
| full | all | Candidate then rho | 48/48 | 8.25098 | 3.20749 | 22.6863 |
| full | 12 | Candidate then rho | 12/12 | 9.1161 | 3.26314 | 22.6863 |
| full | 14 | Candidate then rho | 12/12 | 12.1288 | 8.48855 | 15.4863 |
| full | 16 | Candidate then rho | 12/12 | 8.19646 | 6.28367 | 11.343 |
| full | 18 | Candidate then rho | 12/12 | 5.11411 | 3.20749 | 7.68511 |
| full | all | BSGS | 48/48 | 0.305647 | 0.0589534 | 0.562493 |
| full | 12 | BSGS | 12/12 | 0.175587 | 0.0589534 | 0.455363 |
| full | 14 | BSGS | 12/12 | 0.368161 | 0.260321 | 0.52902 |
| full | 16 | BSGS | 12/12 | 0.373375 | 0.243599 | 0.562493 |
| full | 18 | BSGS | 12/12 | 0.361579 | 0.177074 | 0.532641 |
| core | all | Candidate then rho | 24/24 | 8.0247 | 3.70735 | 22.5743 |
| core | 12 | Candidate then rho | 6/6 | 10.9165 | 3.91952 | 22.5743 |
| core | 14 | Candidate then rho | 6/6 | 11.0097 | 7.90215 | 15.588 |
| core | 16 | Candidate then rho | 6/6 | 7.39846 | 5.70592 | 9.41416 |
| core | 18 | Candidate then rho | 6/6 | 4.66353 | 3.70735 | 5.90172 |
| core | all | BSGS | 24/24 | 0.262058 | 0.0541651 | 0.421107 |
| core | 12 | BSGS | 6/6 | 0.188536 | 0.0541651 | 0.412505 |
| core | 14 | BSGS | 6/6 | 0.277637 | 0.195528 | 0.415536 |
| core | 16 | BSGS | 6/6 | 0.299426 | 0.231279 | 0.421107 |
| core | 18 | BSGS | 6/6 | 0.300903 | 0.211682 | 0.383103 |

A ratio below 1 means less recorded CPU in that named cost regime; a ratio above 1 means more. This defines the measured comparison and is not a claim about a different scale, setup-reuse count, memory regime or implementation. Invalid, censored or zero-timing pairs retain their outcomes and have no qualified complete-cost ratio. A valid-pair subset is labeled and does not erase unresolved requested pairs. Whiskers and ranges are full observed spreads, not confidence intervals.

## A/A controls

All 768 rho A/A pairs have matching seed, answer/status and complete arithmetic counter vector. Target CPU A/A/rho summary: `{"n": 768, "min": 0.443989821067185, "median": 1.000102646594899, "max": 3.4474470770194237, "mean": 1.0206611450216123, "geometric_mean": 1.0052506947052433}`. Zero-timing cases: `[]`. These repeats reveal slot/timing variation; they are not independent stochastic replicates or new targets. No guessed noise correction is subtracted.

## Complete secondary matrix

| Feature | Mode | Beam | Cases | Hits | Checks | Sum B/r |
| --- | --- | --- | --- | --- | --- | --- |
| constant | model | 1 | 768 | 0 | 768 | 0.0961802 |
| constant | model | 8 | 768 | 0 | 6144 | 0.769441 |
| constant | exact | 1 | 768 | 0 | 768 | 0.0961802 |
| constant | exact | 8 | 768 | 0 | 6144 | 0.769441 |
| x_hash_7 | model | 1 | 768 | 0 | 768 | 0.0961802 |
| x_hash_7 | model | 8 | 768 | 0 | 6144 | 0.769441 |
| x_hash_7 | exact | 1 | 768 | 0 | 768 | 0.0961802 |
| x_hash_7 | exact | 8 | 768 | 2 | 6144 | 0.769441 |
| x_mod_7 | model | 1 | 768 | 0 | 768 | 0.0961802 |
| x_mod_7 | model | 8 | 768 | 2 | 6144 | 0.769441 |
| x_mod_7 | exact | 1 | 768 | 1 | 768 | 0.0961802 |
| x_mod_7 | exact | 8 | 768 | 3 | 6144 | 0.769441 |
| power_residue_5 | model | 1 | 480 | 0 | 480 | 0.0620935 |
| power_residue_5 | model | 8 | 480 | 0 | 3840 | 0.496748 |
| power_residue_5 | exact | 1 | 480 | 0 | 480 | 0.0620935 |
| power_residue_5 | exact | 8 | 480 | 3 | 3840 | 0.496748 |

The secondary output includes 174 kernels, 11,136 target cases and 18 explicit fifth-residue NAs. The constant feature gives no scalar information; paired constant modes can repeat the same lists. For constant guesses, B/r is an exact ideal-uniform population probability. For other features it is only a matched candidate-budget reference. The pooled union across configurations is not one decoder’s success rate.

Training/heldout construction, all views and each inference/check remain in the study record. Optional diagnostics are charged study work, not primary algorithm requirements. Shared secondary views count once per feature/target; shared fixture-validation counters count once per curve, not once per kernel.

## Memory, common validation and retained scope

Common curve-plus-all 16-target membership validation CPU: 0.008770006s across 48 rows. It is recorded once outside the arm timers; charging its entire 16-target work to a reconstructed one-target cold or eight-target core would mislabel the measurement.

Memory fields are explicit kernel/vector payloads or upstream byte estimates, with omissions stated in source records. No per-arm peak RSS was measured. The 12GiB setting is a declared operational envelope, not memory usage. Scalar-mul calls contain group operations; powers/inversions contain field multiplies. These nested counters are not additive primitive work.

| Arm | Recorded payload/estimate min–max(bytes) | Target table estimate min–max(bytes) | Exact source scope |
| --- | --- | --- | --- |
| AutoRho | 98,688–98,688 | 98,688–98,688 | Maximum per-target upstream table_bytes_peak_estimate per curve. |
| Rho A/A repeat | 98,688–98,688 | 98,688–98,688 | Maximum per-target upstream table_bytes_peak_estimate per curve. |
| Candidate then rho | 3,136–3,136 | 98,688–98,688 | Setup kernel_numeric_payload_bytes only; excludes views/beam/objects and fallback table. Target upstream estimate is retained separately. |
| Bernstein–Lange precomputation | 1,136–2,080 | 112–928 | Setup upstream table_bytes_peak_estimate; constructor/table estimate, not RSS. |
| BSGS | 1,504–15,872 | 1,504–15,872 | Setup baby-vector capacity payload; excludes object, allocator and sort stack. |

The fresh data span four toy subgroup-bit sizes with 48 curve replication units. Full/core panels overlap; targets/configurations share preprocessing. No bootstrap, significance test or exponent fit was registered or computed. The records support the actual checked solver outcomes and implementation comparisons at these inputs, and identify costs to address in a next revision. Novelty is a separate assessment; the report does not change hypothesis status or exhaust a mathematical family.

## Raw evidence and reproducibility

Raw publication `c4b940ac5360e17cb221772f968bab20f67266c3` preceded analysis. Archive binding: `1822ae0b7247c08dd9062eba62358b8bf19ff728`. Sealed parts manifest SHA-256 `f9b3ce5158877d5d41fdc25fd43a24ba9f2b6397403d49b0d566578796978d67`; public verification manifest `5ef079e04624a1e70d98853a9ecd67e5559ca64640646df48996b2328b32379a`. Every producer stream reconstructs to its original byte length and SHA-256. Exact per-target lists/counters and all failed outcomes remain linked in the raw run rather than being replaced by the summaries.
