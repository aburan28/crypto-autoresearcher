# Localization: Stage-2 S62 / oracle-A / W_4 void (EV-CERTBIN-383c07)

Source package: `RUN-CERTBIN-9dcb6d` / `AMD-20261003-9e0869` /
`DEC-20261003-a6c85a`. Evidence: `EV-CERTBIN-383c07` /
`DEC-20261003-c7e6d1` (refine). Trigger: `S62:F-S3:101` under `V_R`
(`x_R=31046`; `M_4.one=false`, `W_4.one=true`, `oracle_A_sat=false`).

## Finding

Archive `U62`/`S62`/`C20` labels of `RUN-CERTBIN-c417e0` are defined by
the **polynomial-V** oracle `oracles_rc1.oracle_A` (coords in
`{0,…,2^l-1}`). They are not V-invariant sat/unsat obligations.

Re-derivation from `stage2/per-set-rows.json` of `RUN-CERTBIN-9dcb6d`:

| V-set | archive-S62 sat | archive-S62 unsat | W_4 on S62 | sat∧W_4 | unsat∧W_4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| V_N | 38 | 24 | 24 | 0 | 24 |
| V_R | 37 | 25 | 25 | 0 | 25 |
| V_S_octic1 | 40 | 22 | 22 | 0 | 22 |
| V_S_octic2 | 34 | 28 | 28 | 0 | 28 |

Same pattern on archive-U62: `sat∧W_4 = 0` and `unsat∧¬W_4 = 0` on every
V-set — W_4 is **sound and complete** relative to `oracle_A_general` under
the tested V's. The first trigger row under `V_R` is oracle-A **unsat**
under that V (so W_4 refute is consistent); under `V_S_octic1` the same
archive key is oracle-A **sat** and W_4 does not refute.

## Diagnosis

The void was **artifactual transfer control**, not a W_4 false refute and
not an oracle-A reconstruction bug:

1. AMD-20261003-9e0869 / stage2.py required archive-S62 to remain sat under
   every new V and treated any W_4-one on archive-S62 as O-ARTIFACT.
2. Under non-polynomial V, many archive-S62 targets become unsat; W_4 then
   correctly reports one — which the old control mis-labeled as instrument
   void, blocking E-SET/E-POLY reading.

## Re-scope (AMD-20261003-894083)

- Keep soundness void: current-V `oracle_A_sat` ∧ (`M_4`∨`W_4`) one →
  O-ARTIFACT.
- Drop archive-S62-must-remain-sat / archive-S62-W_4-one as O-ARTIFACT.
- Report archive-label transfer counts as observations.
- Rates remain CP95 W_4/M_4 on archived U62 under the current V; when W_4
  matches current-V unsat, the rate equals the fraction of archive-U62
  remaining unsat (disclose in RESULTS / control_policy).

Prior `RUN-CERTBIN-9dcb6d` / `EV-CERTBIN-383c07` unchanged (immutable).
No Bedrock/AUXIN. No break / exponent / ECC2K-130.
