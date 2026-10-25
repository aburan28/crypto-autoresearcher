# Partial native execution: EXP-ECDLP-615fcf

Partial arithmetic/control observations retained; native output invalid, no complete two-primary-route measurement or scientific verdict.

Run `RUN-ECDLP-7f3a18`; source `EXP-ECDLP-c9110e`; hypothesis `H-ECDLP-242aa4`; goal `GOAL-ECDLP-001`. Raw archive `3b337e34b7ed320a7bdf4fcdf36be2ac28588c33`.

Two primary routes were requested. Route A driver exited 0 and the checker exited 1; native status is invalid_output. Thirteen real files are preserved; manifest.yaml was never emitted. Dependent primary route B RUN-ECDLP-f8d192 was not launched. Native elapsed 6.680862 seconds is derived as finished_at minus started_at. The primary and independent checker compiled and ran arithmetic; the checker then failed in metadata git status with threaded-lstat resource error 128.

Exact checker stderr:

```text
fatal: unable to create threaded lstat: Resource temporarily unavailable
Command '['git', 'status', '--porcelain']' returned non-zero exit status 128.
```

The independent-check artifact records measurement_valid:true, route_agreement:true and prediction_match:true for the observed primary transcript. This is not the second primary RUN and does not make the native trial valid. Canonical whole-driver timing/resources and certificate fields are unavailable because there is no manifest; actual per-subprocess argv/CPU/wall/RSS observations remain in native-primary.json and independent-check.json. No missing measurement is replaced by zero.

Recorded partial observations:

```json
{
  "boundary": "Independent checker computation is not a separately allocated second primary run.",
  "independent_check_measurement_valid": true,
  "independent_check_prediction_match": true,
  "independent_check_route_agreement": true,
  "partial_primary_observations": {
    "bound": 96,
    "commuting_counts": [
      4,
      4,
      4
    ],
    "curve_model": "y^2=x^3+8*x^2+2*x over F11",
    "double_T": [
      5,
      7
    ],
    "gap": 288,
    "nearby_bound": 384,
    "point_count": 12,
    "witness_left": [
      7,
      1
    ],
    "witness_right": [
      7,
      10
    ]
  }
}
```

The fixed scientific source is the generalized curve y^2=x(x^2+8x+2) over F11; no source parameter was edited. All readings are deterministic in-sample calibration, with no uncertainty interval, attack-cost claim, hypothesis verdict or formal certificate. A prospective process-local Git thread setting may be recorded for future fresh runs; it was not applied to this attempt. The failed slot and unlaunched dependent identity remain untouched.

Canonical graph scope checked: knowledge/frontiers/ecdlp and this experiment frozen specification. No scientific graph/status changes follow. A stopping-point diagram is used because only one primary route ran and metadata failed.

Exact [commands](command.json), full raw/source/provenance/resource data [report-data.json](report-data.json), [diagram](pipeline.svg), [editable source](pipeline.dot), [PDF](report.pdf). Sources: `experiments/EXP-ECDLP-615fcf/runs/RUN-ECDLP-7f3a18` native receipt/logs, primary-output.json, raw-result.json, native-primary.json, independent-check.json and certificate.yaml. The latter is an instrument witness, not a mathematical certificate.
