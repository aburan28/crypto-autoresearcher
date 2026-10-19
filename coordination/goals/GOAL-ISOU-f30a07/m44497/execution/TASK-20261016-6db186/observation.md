# Terminal native M44497 compact observation

EXP-ISOU-0c7e60 / TASK-20261016-6db186 / GOAL-ISOU-f30a07. Observation delivery only; independent postrun review and admission remain separate. One candidate, one conditional verifier, no retry or substitution.

Constructor RUN-ISOU-bb340e status: CONSTRUCTED.
Independent verifier RUN-ISOU-384b62 status: VERIFIED_COMPACT.
Exact target: degree2^44497-1 on secp256k1 ICV1 icv1-fp256-t432420386565659656852420866390673177327-76dadd18. Compact unreduced integer CM expression; native verifier recomputed degree primality and norm/point/dual checks. SEC2 p/n primality remains TRUSTED_STANDARD. No expanded-map challenge score or worldwide-record conclusion.

## Recorded resources and custody

~~~json
{
  "construct": {
    "resources": {
      "command": [
        "/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/compact-final-e82d80feaf/isogeny",
        "compact-cm",
        "__worker",
        "construct",
        "--exponent",
        "44497",
        "--out",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/artifact",
        "--rss-ready",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/resources-ready"
      ],
      "status": "PASS",
      "exit_code": 0,
      "elapsed_ms_operational_only": 83051,
      "map_count": null,
      "resident_memory_limit_bytes": "8589934592",
      "sampled_peak_resident_bytes": "5406720",
      "memory_sampling_interval_ms": 25,
      "unavailable_memory_samples": 0,
      "memory_monitor_grace_ms": 100,
      "stdout": "native.json",
      "stdout_sha256": "77b0a461da1db9685faccb050a76f49fa9e08d3b15a085841c4de406e46cf522",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "os_time": {
      "real_seconds": 83.06,
      "user_seconds": 57.73,
      "system_seconds": 0.93,
      "user_plus_system_seconds_derived": 58.66,
      "scope": "public native command and waited descendants; excludes build, orchestration and other trials"
    },
    "certificate": {
      "sha256": "85b5db3665a52a8fd04554964c03a6ed208bbb7ad1749770f5fa9d528b77f5d1",
      "bytes": 63615
    }
  },
  "verify": {
    "resources": {
      "command": [
        "/Volumes/SSD990-2/crypto/isogeny-degree-challenge-builds-20261015/compact-final-e82d80feaf/isogeny",
        "compact-cm",
        "__worker",
        "verify",
        "--input",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-bb340e/native/certificate.json",
        "--out",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-384b62/native/artifact",
        "--rss-ready",
        "/Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/experiments/EXP-ISOU-0c7e60/runs/RUN-ISOU-384b62/native/resources-ready"
      ],
      "status": "PASS",
      "exit_code": 0,
      "elapsed_ms_operational_only": 351076,
      "map_count": null,
      "resident_memory_limit_bytes": "8589934592",
      "sampled_peak_resident_bytes": "5341184",
      "memory_sampling_interval_ms": 25,
      "unavailable_memory_samples": 0,
      "memory_monitor_grace_ms": 100,
      "stdout": "native.json",
      "stdout_sha256": "366c9b758efea02b26a11c024ab409955597ad3888b29f02fbdc4e0b10dfbde9",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "os_time": {
      "real_seconds": 351.04,
      "user_seconds": 237.36,
      "system_seconds": 3.92,
      "user_plus_system_seconds_derived": 241.28,
      "scope": "public native command and waited descendants; excludes build, orchestration and other trials"
    },
    "certificate": null
  }
}
~~~

OS CPU covers each public native command and its waited descendants only. Worker elapsed, supervisor elapsed and OS real are distinct retained timers; nested intervals are not summed. Canonical cpu_seconds:null is preserved. Shared-host single-instance observations establish no speed ratio.

Certificate metadata (string lengths and counts; no additional arithmetic implementation):

~~~json
{
  "exponent": 44497,
  "degree_decimal_digits": 13395,
  "source_icv1": "icv1-fp256-t432420386565659656852420866390673177327-76dadd18",
  "representation": "compact known-endomorphism self-map; unreduced signed integer coefficients",
  "a_decimal_characters": 6698,
  "b_decimal_characters": 6698,
  "public_evaluation_count": 8,
  "primality_metadata": {
    "exponent": 44497,
    "states_sha256": "71bcb12e23c41e4a4fbd3d14498c96d9fbdcce3c778d48dd1c90506f2844fb35",
    "terminal": "0",
    "theorem": "Keith Conrad, The Lucas-Lehmer Test, Theorem 2.2",
    "transitions": 44495
  }
}
~~~

## Immutable provenance

Sourcee82d80feaf82d3730576ccd9137911b336f9dab8; postrun binarySHA256 b3cbd6ac5d457a0f6d6398d1fcefc408f627e60be52c81c9009406486b61587b.
Frozen plan, source/input/adapter and approved queue were rehashed. Original bytes remained stable during packaging.
Raw archiveSHA256 9abc49de038066691ff20d2c83a46a5b260ca116ac69739f9c2d43e4b13c354d; bytes 96856; original raw files 47.
Archive contains the exact certificate, both original native/run trees, OS logs, per-file hashes, terminal metadata, collector source, OS first-start receipt and an explicitly labelled wrapper-prefix snapshot rather than a final close receipt.
The initial goal-claim push refused a concurrent remote auto-update before any mathematics started. The existing claim/epoch was retained, the own branch fetched, its file diff verified empty, then a normal merge/push published4b2ebf2956eda0c038252aa461173c7c16428418. The goal-claim-published.json receipt preserves claim identity and launch timing; no native candidate was repeated.

Anomalies: none detected by this descriptive collector; independent review pending.

First constructor invocationUTC 2026-10-16T12:05:37Z; OS worker start independently retained in construct-worker-start.json.
Both adapters terminalUTC 2026-10-16T12:12:51Z.
Next: producer release, declared binderTASK-20261016-3e1186, reserved four-file reportTASK-20261016-6239ad at run-20261016T1205Z,22-path snapshotTASK-20261016-47aaec and independent postrun reviewTASK-20261016-4bad89. No new scientific trial is authorized here.
