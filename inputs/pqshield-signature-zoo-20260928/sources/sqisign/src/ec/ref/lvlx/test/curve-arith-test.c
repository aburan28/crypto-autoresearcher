#include <assert.h>
#include <stdio.h>
#include <inttypes.h>

#include "test_extras.h"
#include <ec.h>
#include <mp.h>
#include <isog.h>
#include <rng.h>
#include <bench_test_arguments.h>

/******************************
Test functions
******************************/

/**
 * @brief Given a curve E, compute (A+2 : 4C)
 *
 * @param A24 the value (A+2 : 4C) to return into
 * @param E a curve
 */
static inline void
AC_to_A24(ec_point_t *A24, const ec_curve_t *E)
{
    // Maybe we already have this computed
    if (E->is_A24_computed_and_normalized) {
        ec_copy_point(A24, &E->A24);
        return;
    }

    // A24 = (A+2C : 4C)
    fp2_add(&A24->z, &E->C, &E->C);
    fp2_add(&A24->x, &E->A, &A24->z);
    fp2_add(&A24->z, &A24->z, &A24->z);
}

int
ec_test_xDBL_xADD(const ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;

    ec_point_t P, Q, PQ, R1, R2;

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&P, curve);
        ec_random_test(&Q, curve);
        projective_difference_point(&PQ, &P, &Q, curve);

        // 2(P + Q) = 2P + 2Q
        ec_xADD(&R1, &P, &Q, &PQ);
        ec_dbl(&R1, &R1, curve);
        ec_dbl(&P, &P, curve);
        ec_dbl(&Q, &Q, curve);
        ec_dbl(&PQ, &PQ, curve);
        ec_xADD(&R2, &P, &Q, &PQ);
        if (!ec_is_equal(&R1, &R2)) {
            printf("Failed 2(P + Q) = 2P + 2Q\n");
            return 1;
        }

        // (P+Q) + (P-Q) = 2P
        ec_xADD(&R1, &P, &Q, &PQ);
        ec_dbl(&Q, &Q, curve);
        ec_xADD(&R1, &R1, &PQ, &Q);
        ec_dbl(&P, &P, curve);
        ec_dbl(&PQ, &PQ, curve);
        if (!ec_is_equal(&R1, &P)) {
            printf("Failed (P+Q) + (P-Q) = 2P\n");
            return 1;
        }
    }

    return 0;
}

int
ec_test_xDBLADD(const ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;

    ec_point_t P, Q, PQ, R1, R2;

    ec_point_t A24;
    AC_to_A24(&A24, curve);
    ec_normalize_point(&A24);

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&P, curve);
        ec_random_test(&Q, curve);
        projective_difference_point(&PQ, &P, &Q, curve);

        ec_xDBLADD(&R1, &R2, &P, &Q, &PQ, &A24);
        ec_xADD(&PQ, &P, &Q, &PQ);
        if (!ec_is_equal(&R2, &PQ)) {
            printf("Failed addition in ec_xDBLADD\n");
            return 1;
        }
        ec_dbl(&P, &P, curve);
        if (!ec_is_equal(&R1, &P)) {
            printf("Failed doubling in ec_xDBLADD\n");
            return 1;
        }
    }
    return 0;
}

int
ec_test_xDBL_variants(ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;
    ec_curve_t E;
    ec_point_t P, R1, R2, R3, R4;
    ec_point_t A24, A24norm;
    fp2_t z;

    AC_to_A24(&A24, curve);
    ec_copy_point(&A24norm, &A24);
    ec_normalize_point(&A24norm);

    // Randomize projective representation
    ec_copy_curve(&E, curve);
    fp2_random_test(&z);
    fp2_mul(&(E.A24.x), &(A24.x), &z);
    fp2_mul(&(E.A24.z), &(A24.z), &z);
    E.is_A24_computed_and_normalized = false;

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&P, curve);
        ec_xDBL(&R1, &P, (const ec_point_t *)curve);
        ec_xDBL_A24(&R2, &P, &(E.A24), false);
        ec_xDBL_A24(&R3, &P, &A24norm, true);
        ec_xDBL_E0(&R4, &P);
        if (!ec_is_equal(&R1, &R2)) {
            printf("xDBL and xDBL_A24 dont match\n");
            return 1;
        }
        if (!ec_is_equal(&R1, &R3)) {
            printf("xDBL and xDBL_A24 normalized dont match\n");
            return 1;
        }
        if (!ec_is_equal(&R1, &R4)) {
            printf("xDBL and xDBL_E0 dont match\n");
            return 1;
        }
    }
    return 0;
}

int
ec_test_zero_identities(ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;

    ec_point_t P, Q, R, ec_zero;

    fp2_set_one(&(P.x));
    fp2_set_zero(&(P.z));

    fp2_set_one(&(ec_zero.x));
    fp2_set_zero(&(ec_zero.z));

    ec_curve_normalize_A24(curve);
    assert(ec_is_zero(&P));

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&P, curve);

        ec_xADD(&R, &ec_zero, &ec_zero, &ec_zero);
        if (!ec_is_zero(&R)) {
            printf("Failed 0 + 0 = 0\n");
            return 1;
        }

        ec_dbl(&R, &P, curve);
        ec_xADD(&R, &P, &P, &R);
        if (!ec_is_zero(&R)) {
            printf("Failed P - P = 0\n");
            return 1;
        }

        ec_dbl(&R, &ec_zero, curve);
        if (!ec_is_zero(&R)) {
            printf("Failed 2*0 = 0\n");
            return 1;
        }

        ec_xADD(&R, &P, &ec_zero, &P);
        if (!ec_is_equal(&R, &P)) {
            printf("Failed P + 0 = P\n");
            return 1;
        }
        ec_xADD(&R, &ec_zero, &P, &P);
        if (!ec_is_equal(&R, &P)) {
            printf("Failed P + 0 = P\n");
            return 1;
        }

        ec_xDBLADD(&R, &Q, &P, &ec_zero, &P, &curve->A24);
        if (!ec_is_equal(&Q, &P)) {
            printf("Failed P + 0 = P in ec_xDBLADD\n");
            return 1;
        }
        ec_xDBLADD(&R, &Q, &ec_zero, &P, &P, &curve->A24);
        if (!ec_is_equal(&Q, &P)) {
            printf("Failed P + 0 = P in ec_xDBLADD\n");
            return 1;
        }
        if (!ec_is_zero(&R)) {
            printf("Failed 2*0 = 0 in ec_xDBLADD\n");
            return 1;
        }
    }
    return 0;
}

int
ec_test_barycentric_coordinates(const ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;

    ec_point_t P, Q, PmQ, PpQ, tmp;
    ec_bary_coordinates_t uvw;

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&P, curve);
        ec_random_test(&Q, curve);
        projective_difference_point(&PmQ, &P, &Q, curve);

        ec_xADD(&PpQ, &P, &Q, &PmQ);
        ec_points_to_bary_coordinates(&uvw, &P, &Q, &PmQ);
        fp2_sub(&tmp.x, &uvw.u, &uvw.v);
        fp2_copy(&tmp.z, &uvw.w);

        if (!ec_is_equal(&PpQ, &tmp)) {
            printf("Failed P + Q = (u - v : w)\n");
            return 1;
        }
        fp2_add(&tmp.x, &uvw.u, &uvw.v);
        if (!ec_is_equal(&PmQ, &tmp)) {
            printf("Failed P - Q = (u + v : w)\n");
            return 1;
        }
    }
    return 0;
}

int
ec_test_biscalar_mul(ec_curve_t *curve, unsigned int Ntest)
{
    unsigned int i;

    ec_point_t R0, R1, R2, Rp, Rm;
    ec_basis_t PQ;
    ibz_t scalar0 = { 0 }, scalar1 = { 0 }, bound = { 0 };
    ibz_mul_2exp(&bound, &ibz_const_one, TORSION_EVEN_POWER);
    ibz_sub(&bound, &bound, &ibz_const_one);
    ibz_set_bound(&bound, TORSION_EVEN_POWER + 1);

    for (i = 0; i < Ntest; i++) {
        ec_random_test(&PQ.P, curve);
        ec_random_test(&PQ.Q, curve);

        ibz_rand_interval(&scalar0, &ibz_const_zero, &bound);
        ibz_rand_interval(&scalar1, &ibz_const_zero, &bound);

        const int kbits = TORSION_EVEN_POWER;
        // Compute through ec_mul
        ec_mul(&R0, scalar0.limbs, kbits, &PQ.P, curve);
        ec_mul(&R1, scalar1.limbs, kbits, &PQ.Q, curve);
        projective_difference_point(&R2, &R0, &R1, curve);
        ec_xADD(&Rp, &R0, &R1, &R2); // aP +- bQ
        ec_xADD(&Rm, &R0, &R1, &Rp); // aP -+ bQ

        // Compute through ec_biscalar_mul
        projective_difference_point(&PQ.PmQ, &PQ.P, &PQ.Q, curve);
        if (!ec_biscalar_mul(&R0, scalar0.limbs, scalar1.limbs, kbits, &PQ, curve)) {
            printf("Error returned by ec_biscalar_mul\n");
            return 1;
        }
        if (!ec_is_equal(&R0, &Rp) && !ec_is_equal(&R0, &Rm)) {
            printf("Failed ec_biscalar_mul\n");
            return 1;
        }

        // Compute through ec_biscalar_mul_verif
        if (!ec_biscalar_mul_verif(&R1, scalar0.limbs, scalar1.limbs, kbits, &PQ, curve)) {
            printf("Error returned by ec_biscalar_mul_verif\n");
            return 1;
        }
        if (!ec_is_equal(&R1, &Rp) && !ec_is_equal(&R1, &Rm)) {
            printf("Failed ec_biscalar_mul_verif\n");
            return 1;
        }
    }
    return 0;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int iterations = 100 * SQISIGN_TEST_REPS;
    int help = 0;
    int seed_set = 0;
    int res = 0;

    for (int i = 1; i < argc; i++) {
        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (sscanf(argv[i], "--iterations=%d", &iterations) == 1) {
            continue;
        }
    }

    if (help || iterations <= 0) {
        printf("Usage: %s [--iterations=<iterations>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for testing; if not "
               "present, uses the default: %d)\n",
               iterations);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is "
               "generated\n");
        return 1;
    }

    if (!seed_set) {
        randombytes_select((unsigned char *)seed, sizeof(seed));
    }

    print_seed(seed);

#if defined(TARGET_BIG_ENDIAN)
    for (int i = 0; i < 12; i++) {
        seed[i] = BSWAP32(seed[i]);
    }
#endif

    randombytes_init((unsigned char *)seed, NULL, 256);
    if (init_test_rng(seed) != 0) {
        return 1;
    }

    // Curve A=6
    ec_curve_t curve;
    ec_curve_init(&curve);
    fp2_set_small(&(curve.A), 0);
    fp2_set_small(&(curve.C), 1);
    // fp2_random_test(&(curve.C));
    // fp2_mul(&(curve.A), &(curve.A), &(curve.C));
    ec_curve_normalize_A24(&curve);

    res |= ec_test_xDBL_xADD(&curve, iterations);
    res |= ec_test_xDBLADD(&curve, iterations);
    res |= ec_test_xDBL_variants(&curve, iterations);
    res |= ec_test_zero_identities(&curve, iterations);

    fp2_random_test(&(curve.C));
    fp2_mul(&(curve.A), &(curve.A), &(curve.C));
    ec_curve_normalize_A24(&curve);

    res |= ec_test_xDBL_xADD(&curve, iterations);
    res |= ec_test_xDBLADD(&curve, iterations);
    res |= ec_test_xDBL_variants(&curve, iterations);
    res |= ec_test_zero_identities(&curve, iterations);
    res |= ec_test_biscalar_mul(&curve, iterations);
    res |= ec_test_barycentric_coordinates(&curve, iterations);

    if (res) {
        printf("Tests failed!\n");
    } else {
        printf("All ec arithmetic tests passed.\n");
    }

    return res;
}
