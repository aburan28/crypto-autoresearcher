# Terminal native compact-candidate observation

EXP-ISOU-feb102 / TASK-20261016-145d29 / GOAL-ISOU-f30a07. Observation delivery only; independent review and any admission remain separate. No candidate was repeated or substituted.

Constructor RUN-ISOU-bdbf5d status: REJECTED.
Constructor error prefix: Lucas-Lehmer rejects M8191; terminal 10383870635347353644793006673052387697290265108910826... (full error preserved in raw JSON)
Full constructor error UTF-8 SHA256: 9b41fb403b439a9fe5daf5d10f6cef8c5148f07b9f9111ef6b9ffd2997ad491f; characters: 2502.
The terminal residue is retained in full in the original native JSON. This observation does not replace independent arithmetic review.

Verification RUN-ISOU-2b2372 status: NOT_STARTED.
Verification reason: construction_not_passed_or_certificate_hash_changed.
Verification adapter invocation time is not a native-process start. Missing verification CPU/time/resource receipts remain unavailable, not measured zero.

## Actual resources and terminal OS receipts

```json
{
  "construct": {
    "resources": {
      "command": [
        "/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/compact-final-e82d80feaf/isogeny",
        "compact-cm",
        "__worker",
        "construct",
        "--exponent",
        "8191",
        "--out",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-feb102/runs/RUN-ISOU-bdbf5d/native/artifact",
        "--rss-ready",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-feb102/runs/RUN-ISOU-bdbf5d/native/resources-ready"
      ],
      "status": "FAIL",
      "exit_code": 1,
      "elapsed_ms_operational_only": 385,
      "map_count": null,
      "resident_memory_limit_bytes": "8589934592",
      "sampled_peak_resident_bytes": "2932736",
      "memory_sampling_interval_ms": 25,
      "unavailable_memory_samples": 0,
      "memory_monitor_grace_ms": 100,
      "stdout": "native.json",
      "stdout_sha256": "706d1e889609223abd5ff89a0e2e304184a18b369828c3101e509ab0941b4acc",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "os_time": {
      "real_seconds": 0.4,
      "user_seconds": 0.32,
      "system_seconds": 0.01,
      "user_plus_system_seconds_derived": 0.33,
      "scope": "public native command and waited descendants; excludes build, orchestration and other trials"
    },
    "certificate": null
  },
  "verify": {
    "resources": null,
    "os_time": null,
    "certificate": null
  }
}
```

OS CPU covers the public native process and waited descendants only. Canonical manifest cpu_seconds:null is preserved. The resource receipt, public native exit, adapter delivery exit and mathematical outcome are distinct. Shared-host single-instance values establish no speed ratio.

## Immutable custody

Source e82d80feaf82d3730576ccd9137911b336f9dab8; post-run executable SHA256 b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b.
Frozen plan, original adapter/input/protocol and both queue bindings were rehashed. All original raw bytes remained unchanged while packaging.
Raw archive: 14903 bytes; SHA256 52301500bbeaa1d6bce211746657b6d66968cd4efd4c6fff6bbbb5ed5901c4f6; original raw files: 34.
Archive includes per-file hashes, exact terminal metadata, launcher/admission/timestamp receipts, both original run trees, collector source and an explicitly labelled Conductor wrapper-prefix snapshot (not a final close receipt).

Anomalies: none detected by this descriptive collector; independent validation pending.

Constructor first trial start: 2026-10-16T10:46:19Z.
Next: release original delivery, then publish the separately scoped single EXP/session report at run-20261016T1046Z covering construction and the verification nonstart, then terminal snapshot. No new candidate or source optimization is authorized by this observation.
