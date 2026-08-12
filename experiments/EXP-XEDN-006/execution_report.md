# EXP-XEDN-006 execution report

- frozen_sha: `76f0cfe2f32362ff1110fc7c7b42db40d293099ae7718927c46223a42450b34f`
- gate_supported: True
- gate_falsified: False
- slope: {"slope": 0.0, "intercept": 1.0, "jackknife_ci": [0.0, 0.0], "ci_includes_0": true, "n": 3, "points": [{"p": 7, "max_abs_coeff": 1}, {"p": 13, "max_abs_coeff": 1}, {"p": 19, "max_abs_coeff": 1}]}
- validity: valid_with_findings — Success gate on measurable core sizes {7,13,19}: bounded coeffs ≤3, slope CI includes 0, μ₃ absent. Unmeasurable sizes [31] (free-x relation density).

## Per-p max_|coeff|

- p=7: eligible=16 max=1 mu3_absent_frac=1
- p=13: eligible=14 max=1 mu3_absent_frac=1
- p=19: eligible=9 max=1 mu3_absent_frac=1
- p=31: eligible=2 max=None mu3_absent_frac=1
