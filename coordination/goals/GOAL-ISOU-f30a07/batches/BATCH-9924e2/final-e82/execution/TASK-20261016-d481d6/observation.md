# Terminal native observation: EXP-ISOU-32a530 / RUN-ISOU-93b2b3

Observation delivery only; no frontier, worldwide-record or performance promotion. The sealed map was not regenerated.

Native public status: CENSORED; reason: TIMEOUT. Exact entry, resource receipt and outer result are embedded in the raw archive summary. Adapter exit acknowledges observation delivery and is not mathematical success.

Source e82d80feaf82d3730576ccd9137911b336f9dab8; expected executable SHA256 b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b; post-run executable SHA256 b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b.
Sealed map SHA256 82e3951488c793c5901ecf1dfeb3ab072b7cda16730899330df7caa9832a170c; all post-run input identities are retained in the summary.

## Recorded resource and OS receipts

```json
{
  "native_resources": {
    "command": [
      "/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/compact-final-e82d80feaf/isogeny",
      "challenge",
      "__judge",
      "--input",
      "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-32a530/runs/RUN-ISOU-93b2b3/native/artifact",
      "--rss-ready",
      "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-32a530/runs/RUN-ISOU-93b2b3/native/resources-ready"
    ],
    "elapsed_ms_operational_only": 3600033,
    "exit_code": null,
    "map_count": null,
    "memory_monitor_grace_ms": 100,
    "memory_sampling_interval_ms": 25,
    "resident_memory_limit_bytes": "8589934592",
    "sampled_peak_resident_bytes": "250052608",
    "status": "TIMEOUT",
    "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "stdout": "verification.json",
    "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "unavailable_memory_samples": 0
  },
  "os_time": {
    "real_seconds": 3600.05,
    "user_seconds": 1716.81,
    "system_seconds": 62.75,
    "user_plus_system_seconds_derived": 1779.56,
    "scope": "public native judge and its waited descendants; excludes build, orchestration and historical attempts"
  }
}
```

Actual OS CPU is recorded only when the terminal time receipt parses. Its scope is the public native process and waited children, not the complete campaign. Sampled ps readings are not terminal CPU receipts.

## Trace observations

Times below are recorded monotonic wall differences in milliseconds on a shared host. Stages nest: do not add overlapping parent/child values. An unfinished stage has no completed duration; core COMPLETED, if present, is separate from public admission.

| Stage ID | Parent ID | Stage | Terminal event | Derived elapsed ms |
|---|---|---|---|---|
| 1 | 0 | setup/loading/parsing | end | 5 |
| 2 | 0 | setup/field_parsing | end | 1 |
| 4 | 3 | source_loading_and_registry | end | 10 |
| 5 | 3 | source_generator_subgroup_order | end | 0 |
| 7 | 6 | coefficient_parsing | end | 32 |
| 9 | 8 | kernel_degree | end | 0 |
| 10 | 8 | squarefree_kernel_gcd | end | 21671 |
| 11 | 8 | selected_division_polynomial_torsion | end | 2001627 |
| 12 | 8 | subgroup_inverse | end | 23 |
| 0 | None | total | no end recorded | unavailable |
| 3 | 0 | attempt_0 | no end recorded | unavailable |
| 6 | 3 | map_0 | no end recorded | unavailable |
| 8 | 6 | kernel_validation | no end recorded | unavailable |
| 13 | 8 | subgroup_modular_composition | no end recorded | unavailable |

Parseable trace records: 23; parse errors: 0; terminal trace records: 0.

## Custody and limitations

Archive native-evidence.tar.gz: 3594206 bytes; SHA256 55c1c18440109a8c1e87c266a67e6d366cbfd64c988a86b5e52ff528126be0ae. It preserves 21 original raw files, exact per-file hashes, parsed metadata, the collector source and an explicitly labelled Conductor wrapper prefix snapshot. Original raw files hash-identical before/after packaging. Wrapper prefix is not a final session-close receipt.

Anomalies: none detected by this descriptive collector; independent validation remains pending.

A timeout is censored verification evidence, not an algebraic counterexample. No speed ratio is derived from the historical timeout, this diagnostic, or shared-host observations. Native point/map acceptance and any leaderboard change require the separate complete admission/review gates. Next: report-only completion and terminal snapshot, then the already queued compact construction and fresh verification.
