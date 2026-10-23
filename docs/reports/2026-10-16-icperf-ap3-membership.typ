#set page(paper: "a4", margin: (x: 17mm, y: 13mm))
#set text(font: "Helvetica Neue", size: 9pt)
#set par(leading: 0.52em)

= AP-3 independent 2E membership validation

2026-10-16 local / 2026-10-17 UTC. Deterministic implementation validation and a proof-scoped protocol obstruction. No factor-base speed, relation-yield, or ECDLP cost claim is made.

Frozen EXP-ICPERF-42ef30 AP-3 asks for an independent 2E membership test agreeing with the x-trace criterion on at least 10,000 points per curve. If \#E = 2r with r odd, P lies in 2E exactly when [r]P = O. The checker separately evaluates that group-order test and Tr(x_P + a); both use Sage arithmetic.

#align(center)[#image("2026-10-16-icperf-ap3-membership.svg", width: 82%)]

== Recorded check

The v2 manifest binds `independent_2e.py` SHA-256 `05b0a6c3bebb82f5b356d114a2b52ffd3aeef32983c017ffaf1933388bbd4072`, Sage 10.10.rc0, Python 3.14.3, Git head `9551744186e0c6b6e9d8b91a580afb1567fbcf85`, seed 20260916, and the scan. Its summary and execution-log receipt hash every curve file and both logs. The first check is separately retained.

#table(
  columns: (1.2fr, 1fr, 1fr, 0.7fr),
  inset: 3pt,
  [Curve (n,a,b)], [Measured \#E], [In 2E / 10,000], [Disagree],
  [(15,1,1)], [32,494], [5,046], [0],
  [(17,1,1)], [131,174], [5,025], [0],
  [(19,1,1)], [525,086], [5,005], [0],
  [(17,1,107553)], [130,974], [4,949], [0],
  [(19,1,38918)], [524,794], [5,049], [0],
)

Total: 50,000 distinct affine points, zero disagreements. The shares come from ordered prefixes; no random-sample inference follows. CPU seconds: 6.463, 8.235, 10.201, 7.940, 10.706. Peak RSS: 278,134,784 bytes. These are correctness-check resource observations, not IC speed measurements.

== Twist admission proof

For x nonzero, z = y/x turns the binary curve equation into z² + z = x + a + b/x². Switching the absolute trace of a toggles solvability, so the curve and quadratic twist together have two affine points per nonzero x. Counting x=0 and infinity gives \#E + \#E′ = 2(q+1). With q even, \#E ≡ 2 (mod 4) forces \#E′ ≡ 0 (mod 4). Recorded n=15,17,19 count pairs are (32494,33044), (131174,130972), (525086,523492). C-TWIST conflicts with AR-3's cofactor-two admission.

The named problem `problems/binary-twist-cofactor-stage1-conflict.md` requires a Coordinator correction: validate a cofactor-four landing model or replace the nearby-object prediction while retaining the twist refusal. AP-1's enumerator and accepted tables are still absent. This check does not establish an end-to-end gain.

Source records: `experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2/`; frozen protocol `experiments/EXP-ICPERF-42ef30/specification.yaml`; editable diagram `docs/reports/2026-10-16-icperf-ap3-membership-chart.py`.
