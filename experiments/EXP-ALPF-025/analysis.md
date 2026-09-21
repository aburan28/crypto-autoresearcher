# Analysis — Autolab prime-field: round015_exp030b_theta_redo

## Observation
Round 15. Experiment-engineer. Bounded redo of the round-13 EXP-030 measurement

Source excerpt / raw summary:

```
# EXP-030b — BOUNDED theta-null Kummer redo (settle H14 theta-null chart)

Round 15. Experiment-engineer. Bounded redo of the round-13 EXP-030 measurement
that stalled before the gated meter finished.

Files:
- code:  `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo.sage`
- log:   `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo.log`
- json:  `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp030b_theta_redo_result.json`
- reused build (read, 516 lines): `round013_exp030_theta_null_kummer.sage`
- gated meter (read, 685 lines): `round007_exp012_localization_gate.sage`
- base meter (read, 277 lines): `round005_meter_validation.sage`

## Headline verdict: INCONCLUSIVE on meter self-validation; STRONG NULL signal on the science.

The bounded sweep ran and produced data, but the mandatory 4-fixture meter
self-validation did **not** come back all-clean (POS-A fixture failed), which by
the hard rule forces an INCONCLUSIVE meter status. The theta-null science signal
that DID land points entirely at the EXPECTED NULL (no gate-meaningful fall), but
because the meter could not be certified in this run I do **not** record H14
theta-null as formally CLOSED — it stays OPEN pending a clean meter pass.

## Meter self-validation (4 fixtures) — FAILED on POS-A

| fixture     | required                                  | observed                                  | ok |
|-------------|-------------------------------------------|-------------------------------------------|----|
| POS-A       | base fires, d_ff=4 < D_reg                 | d_ff=4, **D_reg=None**, fires=False        | NO |
| NEG-1       | quiet (no base fire, gm=False)             | fires=False, gm=False                      | yes|
| e-ring m=3  | base fires, gate_meaningful=False (artifact)| fires=True (d_ff=3<D_reg=7), gm=False      | yes|
| POS-C Weil  | base fires AND gate_meaningful=True        | fires=True (d_ff=4<D_reg=9), gm=True       | yes|

ROOT CAUSE of the POS-A failure (diagnosed, not a meter-logic bug): the
round-007 `build_POS_A` puts 3 cubics in **4** variables (an underdetermined,
positive-dimensional ideal), so the Froberg degree-of-regularity series never
goes non-positive and `froberg_Dreg_local` returns `D_reg=None`; the fixture's
`fires := d_ff < D_reg` then evaluates False. The original round-005 POS-A used
**3** variables (where D_reg=7 is finite and POS-A fires d_ff=4<7). The 3
discriminating fixtures (NEG-1 quiet, e-ring artifact rejected gm=False, POS-C
genuine fall gm=True) behave exactly as required, so the gate itself is
discriminating; only the POS-A positive-base-fire fixture is mis-specified in
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
