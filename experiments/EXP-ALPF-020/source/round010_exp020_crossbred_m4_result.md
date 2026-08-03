# EXP-020 - Crossbred/XL admissible (D,k) frontier, m=4 Semaev S5 x-ring

Seed: 42.  m=4, n=4 free unknowns (x4 = x(R) constant).  Reduced surrogate Semaev degree d_S_reduced=2 for EXACT Macaulay algebra; symbolic Semaev per-var degree = 2^(m-1) = 8.

## Meter self-validation (MANDATORY)

`meter_self_validated = True`

```json
{
  "POS_A": {
    "d_ff": 4,
    "D_reg": null,
    "fires": false
  },
  "NEG_1": {
    "fires": false
  },
  "NEG_2": {
    "fires": false
  },
  "ering_m3": {
    "fires": true,
    "gate_passes": false,
    "gate_meaningful": false
  },
  "POSC_weil": {
    "fires": true,
    "gate_passes": true,
    "gate_meaningful": true
  },
  "criterion": "POS-A d_ff=4; NEGs quiet; e-ring fires-but-not-meaningful; POS-C gate_meaningful"
}
```

## Field-op conversion (stated)

- **rho**: 0.886*sqrt(p)*C_grp, C_grp=12 field-mults/group-op
- **crossbred_per_solve**: Ncols(D)^omega, omega=2.807 (Strassen)
- **crossbred_enum**: FB-enum d_FB^(n-k) [primary]; p^(n-k) [pessimistic]
- **end2end**: solves_needed = (|FB|+1)/P_rel, P_rel=|FB|^m/(m! p)
- **f4**: Ncols(D_reg)^omega

## Admissible-(D,k) frontier  (D < D_reg ?)

| bits | kind | \|FB\| | D_reg(red) | D_reg(sym) | meter fires / gate_meaningful | #admissible (D<D_reg) | best (D,k,d_free) | crossbred FB-enum field-ops | rho field-ops | beats rho? |
|---|---|---|---|---|---|---|---|---|---|---|
| 13 | solinas | 3 | 5 | 31 | False / False | 0 | - | - | 9.622e+02 | - |
| 13 | random | 3 | 5 | 31 | False / False | 0 | - | - | 8.961e+02 | - |
| 13 | solinas | 4 | 7 | 32 | False / False | 0 | - | - | 9.622e+02 | - |
| 13 | random | 4 | 7 | 32 | False / False | 0 | - | - | 8.961e+02 | - |
| 13 | solinas | 5 | 9 | 33 | False / False | 0 | - | - | 9.622e+02 | - |
| 13 | random | 5 | 9 | 33 | False / False | 0 | - | - | 8.961e+02 | - |
| 15 | solinas | 3 | 5 | 31 | False / False | 0 | - | - | 1.924e+03 | - |
| 15 | random | 3 | 5 | 31 | False / False | 0 | - | - | 1.792e+03 | - |
| 15 | solinas | 4 | 7 | 32 | False / False | 0 | - | - | 1.924e+03 | - |
| 15 | random | 4 | 7 | 32 | False / False | 0 | - | - | 1.792e+03 | - |
| 15 | solinas | 5 | 9 | 33 | False / False | 0 | - | - | 1.924e+03 | - |
| 15 | random | 5 | 9 | 33 | False / False | 0 | - | - | 1.792e+03 | - |
| 17 | solinas | 3 | 5 | 31 | False / False | 0 | - | - | 3.849e+03 | - |
| 17 | random | 3 | 5 | 31 | False / False | 0 | - | - | 3.583e+03 | - |
| 17 | solinas | 4 | 7 | 32 | False / False | 0 | - | - | 3.849e+03 | - |
| 17 | random | 4 | 7 | 32 | False / False | 0 | - | - | 3.583e+03 | - |
| 17 | solinas | 5 | 9 | 33 | False / False | 0 | - | - | 3.849e+03 | - |
| 17 | random | 5 | 9 | 33 | False / False | 0 | - | - | 3.583e+03 | - |

## Scaling vs bit-size (gap crossbred/rho)

### solinas_dFB3  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 9.622e+02 | n/a | n/a | 0 |
| 15 | 1.924e+03 | n/a | n/a | 0 |
| 17 | 3.849e+03 | n/a | n/a | 0 |

### random_dFB3  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 8.961e+02 | n/a | n/a | 0 |
| 15 | 1.792e+03 | n/a | n/a | 0 |
| 17 | 3.583e+03 | n/a | n/a | 0 |

### solinas_dFB4  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 9.622e+02 | n/a | n/a | 0 |
| 15 | 1.924e+03 | n/a | n/a | 0 |
| 17 | 3.849e+03 | n/a | n/a | 0 |

### random_dFB4  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 8.961e+02 | n/a | n/a | 0 |
| 15 | 1.792e+03 | n/a | n/a | 0 |
| 17 | 3.583e+03 | n/a | n/a | 0 |

### solinas_dFB5  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 9.622e+02 | n/a | n/a | 0 |
| 15 | 1.924e+03 | n/a | n/a | 0 |
| 17 | 3.849e+03 | n/a | n/a | 0 |

### random_dFB5  (gap trend: None)

| bits | rho | crossbred(FB-enum) | ratio cb/rho | #adm<Dreg |
|---|---|---|---|---|
| 13 | 8.961e+02 | n/a | n/a | 0 |
| 15 | 1.792e+03 | n/a | n/a | 0 |
| 17 | 3.583e+03 | n/a | n/a | 0 |

## Verdict

**FAILED**

- any admissible (D,k) with D < D_reg(reduced): **False**
- any crossbred config beats rho END-TO-END (incl. relation probability): **False**

> NEGATIVE RESULT: no crossbred (D,k) admissible below D_reg for the m=4 S5 x-ring across all swept cells. This EXTENDS NR-017/NR-020 (Buchberger d_ff=D_reg) to the CROSSBRED/XL-cutoff model at m=4: the loophole (an admissible (D,k) with D<D_reg) does NOT open at m=4 either.

## What this rules out / what remains open

- RULES OUT (toy/model-bound, reduced surrogate): a crossbred/XL degree-cutoff D<D_reg shortcut for the m=4 prime-field Semaev S5 x-ring system at the swept sizes.
- DOES NOT rule out: m=5+ crossbred; e-ring / power-sum / rational-map crossbred at m=4; free-block degree d_free>2; Weil-restricted extension-field crossbred (POS-C world, where IC is known to work); non-x-ring coordinate systems with cheaper partial composition.

## Next

- EXP-021: crossbred admissibility for the m=4 e-ring (symmetric coordinates) S5 system -- e-ring lowers the per-variable degree and is the most likely place a (D,k) with D<D_reg could appear; pair with the gate to confirm any fall is summation-localized, not an FB artifact.
