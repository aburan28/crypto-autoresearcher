# Q-curves over F_{p^2} against FourQ

Cost unit: F_p multiplications (M), 127-bit p, S = 0.8 M, M2 = 3 M, S2 = 2 M.  Map cost (modelled): c(d) = 3*(sum isogeny_step_cost(ell) + 20) + 6 -> d=2: 78.0, d=3: 82.8, d=5: 94.8, d=7: 106.8, d=11: 130.8, d=13: 142.8.

## FourQ under the harness model

Verified maps (fourq.py): psi^2 = 0 psi + 32 on the subgroup; phi^2 = 0 phi + -80 on the subgroup; measured map costs {'phi (deg 5)': 211.0, 'psi (deg 2)': 169.0}.

| configuration | coeff bits | total M (Edwards) | total M (Weierstrass) |
|:--|--:|--:|--:|
| FourQ 4-dim, measured maps | 62 | 3326.6 | 3878.0 |
| FourQ 4-dim, modelled maps | 62 | 3028.4 | 3579.8 |
| FourQ psi alone (2-dim), measured map | 123 | 3950.2 | 4333.8 |
| generic 1-dim (no endomorphism), Edwards | 246 | 6073.0 | |
| Longa-Sica GLV+GLS, j = 0 (zeta_3, psi_GLS), synthetic n | 61 | 2524.8 | 2911.2 |

## psi alone (2-dim), every degree

| map | psi^2 | map cost M | coeff bits | total M (Edwards) | total M (Weierstrass) |
|:--|--:|--:|--:|--:|--:|
| GLS (degenerate d = 1) | -1 | 6.0 | 122 | 3658.0 | 3994.3 |
| Smith degree-2 Q-curve, psi alone | -2 | 78.0 | 123 | 3859.2 | 4242.8 |
| Smith degree-2 Q-curve, psi alone | 2 | 78.0 | 123 | 3859.2 | 4242.8 |
| Smith degree-3 Q-curve, psi alone | -3 | 82.8 | 123 | 3864.0 | 4247.6 |
| Smith degree-3 Q-curve, psi alone | 3 | 82.8 | 123 | 3864.0 | 4247.6 |
| Smith degree-5 Q-curve, psi alone | -5 | 94.8 | 122 | 3847.6 | 4229.0 |
| Smith degree-5 Q-curve, psi alone | 5 | 94.8 | 122 | 3847.6 | 4229.0 |
| Smith degree-7 Q-curve, psi alone | -7 | 106.8 | 122 | 3859.6 | 4241.0 |
| Smith degree-7 Q-curve, psi alone | 7 | 106.8 | 123 | 3888.0 | 4271.6 |
| Smith degree-11 Q-curve, psi alone | -11 | 130.8 | 123 | 3912.0 | 4295.6 |
| Smith degree-11 Q-curve, psi alone | 11 | 130.8 | 124 | 3940.4 | 4326.2 |
| Smith degree-13 Q-curve, psi alone | -13 | 142.8 | 123 | 3924.0 | 4307.6 |
| Smith degree-13 Q-curve, psi alone | 13 | 142.8 | 122 | 3895.6 | 4277.0 |

## CM Q-curves at p = 2^127 - 1 (|D| <= 3000, cofactor <= 4096)

Funnel: {'fundamental_D': 909, 'p_split': 459, 'class_of_p_order_2': 67, 'candidates_small_cofactor': 6}.

| D | twist | cofactor | n bits | 4 \| #E | class norms | best 2-dim (deg: M) | best 4-dim degrees | coeff bits | total M (Edwards) | total M (Weierstrass) | FourQ? |
|--:|--:|--:|--:|:--|:--|:--|:--|--:|--:|--:|:--|
| -40 | -1 | 392 | 246 | True | [2, 5, 7, 13, 22, 23] | 2: 3830.8 | [2, 5] | 62 | 3028.4 | 3579.8 | yes |
| -212 | -1 | 334 | 246 | False | [2, 27, 31, 39, 51] | 2: 3859.2 | [2, 27] | 62 | 3050.0 | 3601.4 |  |
| -840 | 1 | 3348 | 243 | True | [7, 30, 37, 58] | 7: 3831.2 | [7, 30] | 61 | 3078.0 | 3618.2 |  |
| -795 | 1 | 457 | 246 | False | [3] | 3: 3864.0 | None | None | None | None |  |
| -1588 | 1 | 758 | 245 | False | [2] | 2: 3830.8 | None | None | None | None |  |
| -1752 | 1 | 972 | 245 | True | [6] | 6: 3847.6 | None | None | None | None |  |

D = -40 reproduces FourQ (#E = 392 N).  FourQ's verified maps: {'psi (fourq.py)': '= -4 * psi_a with N(a) = 2', 'phi (fourq.py)': '= -4 * psi_a with N(a) = 5'}.  4-dim pairs on it (degrees: coeff bits, total M Edwards): [2, 5]: 62, 3028.4; [2, 7]: 62, 3040.4; [2, 7]: 62, 3040.4; [5, 7]: 62, 3074.0; [5, 7]: 62, 3074.0; [2, 13]: 62, 3076.4; [2, 13]: 62, 3076.4; [2, 22]: 62, 3076.4

## Explicit maps on points (p = 2^127 - 1)

* degree 2, FourQ's W: y^2 = x^3 - (30 - 8 sqrt5) x + 56 - 32 sqrt5 (fourq.py): psi^2 = 2, #E = 28948022309329048855892746252171976962840845737041638204827285762769800380856, cofactor 392, l = 246-bit prime, eigenvalue found: True; psi affine ops {'M2': 5, 'S2': 1, 'I2': 1, 'Mp_equiv': 19} (projective-equivalent 26.0 M); 
  * psi(P) on E (3 random points): True
  * psi(P+Q) = psi(P) + psi(Q): True
  * psi(psi(P)) = [+-2]P on 3 random points (sign 1): True
  * [#E] P = O for a random P: True
  * [l] G = O, G = [h] P != O: True
  * psi acts on <G> as a square root of 2 mod l: True
  * 2-dim decomposition reconstructs kG: True
  * decomposition: {'reconstructs kG (3 random k)': True, 'dim': 2, 'bound_bits': 123, 'empirical_max_bits': 122, 'balanced_bits': 122.5, 'basis_inf_norm_bits': [123, 123], 'l_bits': 246}
* degree 2, X_0(2) Hauptmodul, t * t^p = 4096: psi^2 = -2, #E = 28948022309329048855892746252171976963124431277220883838541816950980159968548, cofactor 824583204, l = 225-bit prime, eigenvalue found: True; psi affine ops {'M2': 5, 'S2': 1, 'I2': 1, 'Mp_equiv': 19} (projective-equivalent 26.0 M); build outcomes over attempts: {'ok': 3}
  * psi(P) on E (3 random points): True
  * psi(P+Q) = psi(P) + psi(Q): True
  * psi(psi(P)) = [+-2]P on 3 random points (sign -1): True
  * [#E] P = O for a random P: True
  * [l] G = O, G = [h] P != O: True
  * psi acts on <G> as a square root of -2 mod l: True
  * 2-dim decomposition reconstructs kG: True
  * j(E) = j(t) has j(E)^p = j of the Velu codomain: True
  * decomposition: {'reconstructs kG (3 random k)': True, 'dim': 2, 'bound_bits': 112, 'empirical_max_bits': 112, 'balanced_bits': 112.0, 'basis_inf_norm_bits': [112, 112], 'l_bits': 225}
* degree 3, X_0(3) Hauptmodul, t * t^p = 729: psi^2 = 3, #E = 28948022309329048855892746252171976963298770434382801987739213536944980204637, cofactor 75323, l = 238-bit prime, eigenvalue found: True; psi affine ops {'M2': 8, 'S2': 1, 'I2': 1, 'Mp_equiv': 28} (projective-equivalent 35.0 M); build outcomes over attempts: {'ok': 2}
  * psi(P) on E (3 random points): True
  * psi(P+Q) = psi(P) + psi(Q): True
  * psi(psi(P)) = [+-3]P on 3 random points (sign 1): True
  * [#E] P = O for a random P: True
  * [l] G = O, G = [h] P != O: True
  * psi acts on <G> as a square root of 3 mod l: True
  * 2-dim decomposition reconstructs kG: True
  * j(E) = j(t) has j(E)^p = j of the Velu codomain: True
  * decomposition: {'reconstructs kG (3 random k)': True, 'dim': 2, 'bound_bits': 119, 'empirical_max_bits': 119, 'balanced_bits': 118.5, 'basis_inf_norm_bits': [119, 119], 'l_bits': 238}
