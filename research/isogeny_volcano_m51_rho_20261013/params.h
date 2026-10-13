#ifndef ISOGENY_VOLCANO_M51_RHO_PARAMS_H
#define ISOGENY_VOLCANO_M51_RHO_PARAMS_H

/*
 * m = 51 Koblitz isogeny-class study.
 *
 * Field: F_2^51 = F_2[x]/(x^51 + x^6 + x^3 + x + 1).
 * Group order: NORD = COF * ELL.
 *
 * LAMBDA_TAU is the eigenvalue of the 2-power Frobenius on the selected
 * prime-order subgroup of the crater curve y^2 + xy = x^3 + 1.
 * LAMBDA_TAU17 = LAMBDA_TAU^17 has exact order 3 and is the eigenvalue used
 * for curves whose coefficients are fixed by the 2^17-power Frobenius.
 */
#define M 51
#define RED 0x4bULL
#define ELL 17192986687ULL
#define COF 130972ULL
#define QPOW 35
#define NORD 2251799852369764ULL
#define LAMBDA_TAU 10848089173ULL
#define LAMBDA_TAU17 17024429279ULL

#endif
