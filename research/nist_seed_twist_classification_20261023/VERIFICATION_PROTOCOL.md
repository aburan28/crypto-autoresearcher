# Independent Sage twist-form rederivation

**Frozen:** 2026-10-23 UTC after the primary Python run, before executing Sage on these 21 curves. This verification does not change the primary run or its outcome.

Read the immutable primary `runs/20261023T2102Z/results.json`, SHA-256 `55dcc0d49b8616c4a85698173761fd743fb43e1495d174e4a1b10540483b00d1`. For each of its 21 bound field and coefficient records, construct `EllipticCurve(GF(p), [a,b])` in Sage, verify `p` is prime with proof enabled, independently recompute `j`, call the finite-field `twists()` method, require exactly two rational forms, and match one to the original curve and one to `quadratic_twist()`. Verify the arithmetic twist-order identity `2p+2-n` from the independent input integers. Preserve per-row results, Sage and Python versions, exact command, source hash, timestamps, and any failure in a fresh write-once directory. Stop on the first mismatch.

This cross-check verifies classification and record binding using a different implementation. Sage's twist enumeration and the mathematical theorem remain the interpretation; it does not independently recount all 21 groups or validate historical use of any twist criterion.
