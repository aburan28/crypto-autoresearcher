# EXP-ECDLP-fac9ea v3 — lambda-registry census report

Run RUN-ECDLP-8e13c2, generated 2026-09-21T18:40:36Z under TASK-20260921-4888d4.
Specification v1 + amendments DEC-20260921-d3fafb (ladder) and
DEC-20260921-f1d95a (probability normalisation), both pre-run.
Observations only; gate verdicts use the frozen vocabulary; gates are
necessary, not sufficient. Gates: lambda > 1/4 learning route
(IDEA-20260904-f68c7f (D)); lambda >= 1/6 n^{1/3}-corner
(IDEA-20260920-b6ad24 (A3)); PGL_2 deviation marks a row artifactual
and voids it from the gate table (frozen rule).

## Controls

| control | result |
|---|---|
| C01_all_ones_numerically_zero | PASS |
| C02A_parseval_band_0.5 | PASS |
| C02_seed_set_agreement_AB | PASS |
| R03_reproduction_band_0.36_0.42 | PASS |
| R03B_deterministic_replication_identical | PASS |
| all_ok_cells_vhat0_equals_1 | PASS |
| R03_reproduction_marginal_note | note: point-estimate semantics per the frozen text ('fitted lambda in [0.36, 0.42]'): lambda = 0.4191, SE 0.0062; the +-2SE interval [0.4068, 0.4314] extends past 0.42 -- the reproduction is MARGINAL at the band edge, disclosed |

## Gate table (frozen registry)

| row | lambda | SE | n | verdict | moebius | two-ladder | jackknife |
|---|---|---|---|---|---|---|---|
| R01 | 0.0806 | 0.0020 | 16 | artifactual | DEVIATION | agree | ok |
| R02 | 0.0806 | 0.0020 | 16 | artifactual | DEVIATION | agree | ok |
| R03 | 0.4191 | 0.0062 | 16 | artifactual | DEVIATION | agree | ok |
| R04 | 0.4088 | 0.0040 | 16 | artifactual | DEVIATION | agree | ok |
| R05 | 0.3806 | 0.0046 | 16 | artifactual | DEVIATION | agree | ok |
| R06 | 0.5013 | 0.0037 | 10 | corner_open_and_learning_open | stable | agree | ok |
| R07 | 0.5709 | 0.0349 | 4 | corner_open_and_learning_open | stable | agree | ok |
| R08 | 0.5000 | 0.0000 | 16 | corner_open_and_learning_open | stable | agree | ok |
| R09 | 0.1133 | 0.0047 | 16 | artifactual | DEVIATION | agree | ok |

## Control and auxiliary fits

| row | lambda | SE | note |
|---|---|---|---|
| C02A | 0.4996 | 0.0006 | Parseval level 0.5 |
| C02B | 0.5001 | 0.0002 | Parseval level 0.5, seed set B |
| R03B | 0.4191 | 0.0062 | deterministic replication of R03 |
| C01 | 0 (exact) | - | all cells numerically zero: True |
| R01M | 0.5010 | 0.0016 | PGL_2 battery |
| R02M | 0.5005 | 0.0004 | PGL_2 battery |
| R03M | 0.5229 | 0.0014 | PGL_2 battery |
| R04M | 0.5247 | 0.0011 | PGL_2 battery |
| R05M | 0.5215 | 0.0008 | PGL_2 battery |
| R06M | 0.4934 | 0.0056 | PGL_2 battery |
| R07M | 0.5423 | 0.0296 | PGL_2 battery |
| R08M | 0.4999 | 0.0001 | PGL_2 battery |
| R09M | 0.5013 | 0.0005 | PGL_2 battery |
| R06:curve0 | 0.4998 | 0.0006 | curve-restricted, auxiliary |
| R06:curve1 | 0.4990 | 0.0011 | curve-restricted, auxiliary |
| R06:curve2 | 0.5001 | 0.0014 | curve-restricted, auxiliary |
| R07:curve0 | 0.5116 | 0.0052 | curve-restricted, auxiliary |
| R07:curve1 | 0.5134 | 0.0051 | curve-restricted, auxiliary |
| R07:curve2 | 0.5072 | 0.0039 | curve-restricted, auxiliary |
| R08:curve0 | 0.5001 | 0.0004 | curve-restricted, auxiliary |
| R08:curve1 | 0.5003 | 0.0004 | curve-restricted, auxiliary |
| R08:curve2 | 0.5011 | 0.0009 | curve-restricted, auxiliary |

## Band census consequence

ALL CONTROLS PASSED. Reading the gate table under the frozen rules:

- Every structured ADDITIVE statistic in the registry (R01 interval,
  R02 AP, R03/R03B popcount level, R04 base-3, R05 base-10, R09
  low-bit) is PGL_2-UNSTABLE: its lambda is a property of the specific
  x-line embedding, not of the statistic class, so the frozen rule
  voids all of them from the gate table (verdict: artifactual). The
  digit-family lambda (R03 = 0.4191) reproduces the
  KN-FIND-ffe1df 0.39 measurement MARGINALLY (band edge 0.42) but is
  representation-unstable, so it cannot serve as a stable key.
- The only PGL_2-STABLE rows above the 1/4 threshold are the
  multiplicative cosets R06, R08, and they sit at
  the RANDOM-SET Parseval level (lambda ~ 0.50; C02A reads
  0.4996): flat Gauss-sum structure, spectrally
  indistinguishable from a random set of matched density. They
  'open' both gates only in the vacuous necessary-condition
  sense -- they carry no bias structure a construction can key on.
- STABLE AND ABOVE THE PARSEVAL LEVEL: R07 --
  the only candidate band inhabitants a successor construction
  step could key on; each needs more primes (R07 has 4 fit
  points) before its level is decided.

SCOPED NEGATIVE, recorded: within the frozen registry, ladders
(p <= 2^24.2 measured; the 2^26-class tail prime is checkpointed
resource_exhaustion after a disclosed machine-protection breach,
values preserved for a chunked-convolution amendment), and the
frozen probability normalisation: NO natural coordinate statistic
is simultaneously PGL_2-stable and spectrally distinct from the
random-set level. Named successors: (a) the R07 index-5 coset
level (0.5709 +- 0.0349, 4 points, ~2 sigma above Parseval) with a
wider prime set; (b) synthetic coordinate-statistic design outside
the registry; (c) the chunked-convolution amendment to recover the
2^26-class tail point for the jackknife.

Per-cell raw values, wall times, RSS high-water marks, and unavailable
certificates: registry.json and manifest.yaml. The census's own charged
cost is the wall_seconds column.

