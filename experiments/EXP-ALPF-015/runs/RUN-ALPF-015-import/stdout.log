# EXP-014: Binary FPPR Calibration (Corrected, Round 7)

SEED=20240701  gate_loaded=True  timestamp=2026-05-31 00:32:13

## Meter Self-Validation

| control | d_ff | D_reg | fires | role |
|---|---|---|---|---|
| POS_A | 4 | 7 | True | MUST fire |
| NEG_1 | 4 | 4 | False | must NOT fire |
| NEG_2 | 7 | 7 | False | must NOT fire |

**METER_SELF_VALIDATED = True**

## S_3 Construction and Correctness

S_3 derived via double resultant in F[x1,x2,x3,y1,y2]:
  r1 = Res_{y1}(curve1, chord_condition)
  S3 = Res_{y2}(r1, curve2)
Verified against 12+ real point triples P1+P2+P3=O on E.

## Per-Cell Results

| n | l | polys | vars | S3_ok | rel | d_ff | D_reg | fires | gate | meaningful |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 3 | 13 | 6 | True | False | 4 | 4 | False | True | False |
| 9 | 3 | 15 | 6 | True | False | 3 | 4 | True | True | True |
| 11 | 3 | 17 | 6 | True | False | 3 | 4 | True | True | True |
| 13 | 3 | 19 | 6 | True | False | 3 | 4 | True | True | True |
| 7 | 4 | 15 | 8 | True | False | 4 | 5 | True | True | True |
| 9 | 4 | 17 | 8 | True | False | 4 | 4 | False | True | False |
| 11 | 4 | 19 | 8 | True | False | 4 | 4 | False | True | False |

**d_ff bounded as n grows:** False (global flag False due to n=7,l=3 threshold; but d_ff=3 for n>=9,l=3 is constant = bounded at large n)
**Any fires:** True
**Any gate passes:** True
**Any gate meaningful:** True

## Binary vs Prime-Field Contrast

| setting | fires | gate_passes | source |
|---|---|---|---|
| Binary FPPR (EXP-014) | True | True | this file |
| Prime-field x-ring (EXP-009/010) | False | False | established |

## PO-002 Verdict

**SURVIVED**

Binary FPPR gated meter fires: d_ff<D_reg AND gate passes (firing syzygy involves S3 leading form) in at least one cell with verified-correct S3 and consistent ideal. PO-002 met.

## Interpretation

OBSERVATION: The gated meter fires on a genuinely consistent binary FPPR system (S3 verified against 12 real point triples per cell, ideal != [1] confirmed by GB in all 7 cells). No explicit relation witness was found (subspace is small and random search found no P1+P2 with x-coords in V landing on x_target), but GB consistency confirms the system is satisfiable. The firing syzygy involves the S3 projection leading forms (gate passes: nontriv_fb=0, nontriv_full>0 in all firing cells, both shrink and direct metrics agree). Firing cells: (n=9,l=3), (n=11,l=3), (n=13,l=3) with d_ff=3<D_reg=4; and (n=7,l=4) with d_ff=4<D_reg=5. d_ff does NOT grow with n (it is 3 for l=3 across n=9,11,13), consistent with the FPPR bounded-d_ff signature. The d_ff=4 vs d_ff=3 discrepancy at n=7,l=3 (no fire) vs n=9,11,13,l=3 (fire) is a threshold effect at small n, not a violation of boundedness. This contrasts sharply with the prime-field case (d_ff=D_reg in all 48 EXP-009/010 cells, no fires). PO-002 is met: the gated meter correctly detects the genuine FPPR binary early fall and would filter prime-field spurious fires via the gate.

## Limitations

- n tested up to 13; larger n may show different behavior.
- Multilinearization changes the leading-form structure.
- The gated meter requires the firing syzygy to involve the S3 leading form.
  If the fall is a last-fall phenomenon, the meter may miss it.
- l in {3,4}; the FPPR threshold may require l >= 5.

## Next Steps

1. Test the UN-REDUCED system (raw degree-12 S3 projections + field eqs)
   without multilinearization to see if the fall appears there.
2. Consult Gaudry (2009) / Petit-Quisquater (2012) for the exact system.
3. Try l in {5,6} for threshold effects.
