# EXP-021 - crossbred/XL admissible-(D,k) at m=4 in the E-RING

Round 11. Semaev S5 (m=4) index-calculus decomposition system in
elementary-symmetric (e-ring) coordinates over prime-field ECDLP toy families.
Seed 42. Extends NR-025 (x-ring crossbred negative) to the e-ring.

## Degree model (LABELED)

- Symbolic S5 per-variable x-degree: 2^(m-1) = 8 (the true object).
- E-ring surrogate top-form degree ladder d_S in [3, 4, 5, 6, 8] (reduced-surrogate, same
  approach as NR-025; lower d_S = optimistic e-ring packing = BEST chance for a
  crossbred D<D_reg cut to open). d_S=8 reproduces the symbolic degree.

## Meter self-validation (inline, mandatory)

meter_self_validated = **True**

| case | d_ff | D_reg | fires | gate_passes | gate_meaningful | ok |
|---|---|---|---|---|---|---|
| POS_A | 4 | None | False | - | - | True |
| NEG_1 | None | None | False | - | - | True |
| NEG_2 | None | None | False | - | - | True |
| ERING_m3 | 3 | 7 | True | False | False | True |
| POS_C | 4 | 9 | True | True | True | True |

## Admissibility frontier (e-ring) vs NR-025 (x-ring)

NR-025 x-ring baseline: NO admissible (D,k) with D<D_reg in x-ring (reduced surrogate)

| kind | bits | |FB| | d_S | n_vars | degs | D_reg | d_ff | adm<D_reg? | min_adm_D | adm_gate_meaningful |
|---|---|---|---|---|---|---|---|---|---|---|
| solinas_a-3 | 13 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 13 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 13 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 13 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 13 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 13 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 15 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 15 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 15 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 15 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 15 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 15 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 17 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| solinas_a-3 | 17 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 17 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 17 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 17 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| solinas_a-3 | 17 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 13 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| random | 13 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| random | 13 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| random | 13 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| random | 13 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| random | 13 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 13 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 13 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 13 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 13 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 13 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 13 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 13 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 13 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 13 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 15 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| random | 15 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| random | 15 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| random | 15 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| random | 15 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| random | 15 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 15 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 15 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 15 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 15 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 15 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 15 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 15 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 15 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 15 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 17 | 3 | 3 | 4 | [3, 2, 2, 2] | 6 | 3 | True | 3 | False |
| random | 17 | 3 | 4 | 4 | [4, 2, 2, 2] | 7 | 3 | True | 3 | False |
| random | 17 | 3 | 5 | 4 | [5, 2, 2, 2] | 8 | 3 | True | 3 | False |
| random | 17 | 3 | 6 | 4 | [6, 2, 2, 2] | 9 | 3 | True | 3 | False |
| random | 17 | 3 | 8 | 4 | [8, 2, 2, 2] | 11 | 3 | True | 3 | False |
| random | 17 | 4 | 3 | 4 | [3, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 17 | 4 | 4 | 4 | [4, 2, 2, 2, 2] | 4 | 3 | True | 3 | False |
| random | 17 | 4 | 5 | 4 | [5, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 17 | 4 | 6 | 4 | [6, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 17 | 4 | 8 | 4 | [8, 2, 2, 2, 2] | 5 | 3 | True | 3 | False |
| random | 17 | 5 | 3 | 4 | [3, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 17 | 5 | 4 | 4 | [4, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 17 | 5 | 5 | 4 | [5, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 17 | 5 | 6 | 4 | [6, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |
| random | 17 | 5 | 8 | 4 | [8, 2, 2, 2, 2, 2] | 3 | 2 | True | 2 | False |

## Cost comparison (field ops, log2; end-to-end incl P_rel)

| cell | n | D_reg | D_cut | F4 2^ | crossbred 2^ | rho 2^ | P_rel 2^ | IC e2e 2^ | IC beats rho? |
|---|---|---|---|---|---|---|---|---|---|
| solinas_a-3 b13 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| solinas_a-3 b13 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| solinas_a-3 b13 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| solinas_a-3 b13 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| solinas_a-3 b13 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| solinas_a-3 b13 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| solinas_a-3 b13 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| solinas_a-3 b13 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| solinas_a-3 b13 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| solinas_a-3 b13 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| solinas_a-3 b13 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| solinas_a-3 b13 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| solinas_a-3 b13 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| solinas_a-3 b13 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| solinas_a-3 b13 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| solinas_a-3 b15 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| solinas_a-3 b15 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| solinas_a-3 b15 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| solinas_a-3 b15 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| solinas_a-3 b15 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| solinas_a-3 b15 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| solinas_a-3 b15 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| solinas_a-3 b15 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| solinas_a-3 b15 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| solinas_a-3 b15 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| solinas_a-3 b15 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| solinas_a-3 b15 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| solinas_a-3 b15 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| solinas_a-3 b15 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| solinas_a-3 b15 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| solinas_a-3 b17 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| solinas_a-3 b17 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| solinas_a-3 b17 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| solinas_a-3 b17 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| solinas_a-3 b17 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| solinas_a-3 b17 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| solinas_a-3 b17 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| solinas_a-3 b17 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| solinas_a-3 b17 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| solinas_a-3 b17 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| solinas_a-3 b17 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| solinas_a-3 b17 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| solinas_a-3 b17 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| solinas_a-3 b17 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| solinas_a-3 b17 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| random b13 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| random b13 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| random b13 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| random b13 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| random b13 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 6.8 | -11.2 | 25.3 | False |
| random b13 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| random b13 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| random b13 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| random b13 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| random b13 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 6.8 | -9.6 | 24.0 | False |
| random b13 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| random b13 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| random b13 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| random b13 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| random b13 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 6.8 | -8.3 | 20.2 | False |
| random b15 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| random b15 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| random b15 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| random b15 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| random b15 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 7.8 | -13.2 | 27.3 | False |
| random b15 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| random b15 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| random b15 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| random b15 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| random b15 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 7.8 | -11.6 | 26.0 | False |
| random b15 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| random b15 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| random b15 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| random b15 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| random b15 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 7.8 | -10.3 | 22.2 | False |
| random b17 fb3 dS3 | 4 | 6 | 3 | 17.9 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| random b17 fb3 dS4 | 4 | 7 | 3 | 19.3 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| random b17 fb3 dS5 | 4 | 8 | 3 | 20.6 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| random b17 fb3 dS6 | 4 | 9 | 3 | 21.8 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| random b17 fb3 dS8 | 4 | 11 | 3 | 23.8 | 12.1 | 8.8 | -15.2 | 29.3 | False |
| random b17 fb4 dS3 | 4 | 4 | 3 | 14.4 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| random b17 fb4 dS4 | 4 | 4 | 3 | 14.4 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| random b17 fb4 dS5 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| random b17 fb4 dS6 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| random b17 fb4 dS8 | 4 | 5 | 3 | 16.3 | 12.1 | 8.8 | -13.6 | 28.0 | False |
| random b17 fb5 dS3 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| random b17 fb5 dS4 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| random b17 fb5 dS5 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| random b17 fb5 dS6 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |
| random b17 fb5 dS8 | 4 | 3 | 2 | 12.1 | 9.3 | 8.8 | -12.3 | 24.2 | False |

## Verdict

- any admissible (D,k) with D<D_reg in e-ring: **True**
- any such admissible fall gate_meaningful (S5-localized, not e-ring FB artifact): **False**
- any IC config beats rho end-to-end (incl P_rel): **False**
- CANDIDATE (all three, PO-003 still needs downstream solver demo): **False**
- **VERDICT: FAILED**

## What this rules out / what remains open

- NEGATIVE (extends NR-025 to e-ring): admissible D<D_reg cuts exist in the e-ring
  but EVERY such fall is gate_meaningful=False -- an e-ring FB-row artifact (the e1-
  shared factor among FB constraints), NOT a summation-localized S5 fall. No index-
  calculus solver leverage; PO-003 not satisfied.

## Next

- Conservative: re-run with the FULL symbolic S5 e-ring top form (not surrogate) at the
  smallest bits to confirm the surrogate ladder did not hide a real fall.
- Representation-changing: power-sum (Newton) coords at m=4, and the partially-symmetric
  Faugere-Gaudry-Huot-Renault 'last-variable' degree-8 / others-lower split.
- High-risk: hybrid e-ring + one specialized variable (XL guess-and-determine) to force a
  low-k kept set, then gate-check whether the forced fall is S5-localized.

