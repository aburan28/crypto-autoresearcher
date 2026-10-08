#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <ec.h>
#include <rng.h>
#include <bench_test_arguments.h>
#include "test_extras.h"

/******************************
Test functions
******************************/

int
inner_test_generated_basis(ec_basis_t *basis, ec_curve_t *curve, unsigned int n)
{
    unsigned int i;
    int passed = 1;

    ec_point_t P, Q;
    ec_copy_point(&P, &basis->P);
    ec_copy_point(&Q, &basis->Q);

    // Double points to get point of order 2
    for (i = 0; i < n - 1; i++) {
        ec_xDBL_A24(&P, &P, &curve->A24, curve->is_A24_computed_and_normalized);
        ec_xDBL_A24(&Q, &Q, &curve->A24, curve->is_A24_computed_and_normalized);
    }
    if (ec_is_zero(&P)) {
        printf("Point P generated does not have full order\n");
        passed = 0;
    }
    if (ec_is_zero(&Q)) {
        printf("Point Q generated does not have full order\n");
        passed = 0;
    }
    if (ec_is_equal(&P, &Q)) {
        printf("Points P, Q are linearly dependent\n");
        passed = 0;
    }

    if (!fp2_is_zero(&Q.x)) {
        printf("Points Q is not above the Montgomery point\n");
        passed = 0;
    }

    // This should give the identity
    ec_xDBL_A24(&P, &P, &curve->A24, curve->is_A24_computed_and_normalized);
    ec_xDBL_A24(&Q, &Q, &curve->A24, curve->is_A24_computed_and_normalized);
    if (!ec_is_zero(&P)) {
        printf("Point P generated does not have order exactly 2^n\n");
        passed = 0;
    }
    if (!ec_is_zero(&Q)) {
        printf("Point Q generated does not have order exactly 2^n\n");
        passed = 0;
    }

    if (passed == 0) {
        printf("Test failed with n = %u\n", n);
    }

    return passed;
}

int
inner_test_hint_basis(ec_basis_t *basis, ec_basis_t *basis_hint)
{
    int passed = 1;

    if (!ec_is_equal(&basis->P, &basis_hint->P)) {
        printf("The points P do not match using the hint\n");
        passed = 0;
    }

    if (!ec_is_equal(&basis->Q, &basis_hint->Q)) {
        printf("The points Q do not match using the hint\n");
        passed = 0;
    }

    if (!ec_is_equal(&basis->PmQ, &basis_hint->PmQ)) {
        printf("The points PmQ do not match using the hint\n");
        passed = 0;
    }

    if (passed == 0) {
        printf("Test failed\n");
    }

    return passed;
}

/******************************
Test wrapper functions
******************************/

int
test_basis_generation_E0(unsigned int n)
{
    ec_basis_t basis;
    ec_curve_t curve;

    ec_curve_init(&curve);

    // Set a supersingular elliptic curve
    // E : y^2 = x^3 + 6*x^2 + x
    fp2_set_small(&(curve.A), 0);
    fp2_set_one(&(curve.C));
    ec_curve_normalize_A24(&curve);

    // Generate a basis
    (void)ec_curve_to_basis_2f_to_hint(&basis, &curve, n, 0);

    // Test result
    return inner_test_generated_basis(&basis, &curve, n);
}

int
test_basis_generation(unsigned int n)
{
    ec_basis_t basis;
    ec_curve_t curve;

    ec_curve_init(&curve);

    // Set a supersingular elliptic curve
    // E : y^2 = x^3 + 6*x^2 + x
    fp2_set_small(&(curve.A), 6);
    fp2_set_one(&(curve.C));
    ec_curve_normalize_A24(&curve);

    // Generate a basis
    (void)ec_curve_to_basis_2f_to_hint(&basis, &curve, n, 0);

    // Test result
    return inner_test_generated_basis(&basis, &curve, n);
}

int
test_basis_generation_with_hints(unsigned int n)
{
    int check_1, check_2;
    ec_basis_t basis, basis_hint;
    ec_curve_t curve;
    ec_curve_init(&curve);

    // Set a supersingular elliptic curve
    // E : y^2 = x^3 + 6*x^2 + x
    fp2_set_small(&(curve.A), 6);
    fp2_set_one(&(curve.C));
    ec_curve_normalize_A24(&curve);

    // Generate a basis with hints
    uint8_t hint = ec_curve_to_basis_2f_to_hint(&basis, &curve, n, 0);

    // Ensure the basis from the hint is good
    check_1 = inner_test_generated_basis(&basis, &curve, n);

    // Generate a basis using hints
    ec_curve_to_basis_2f_from_hint(&basis_hint, &curve, n, hint);

    // These two bases should be the same
    check_2 = inner_test_hint_basis(&basis, &basis_hint);

    return check_1 && check_2;
}

int
test_basis_generation_with_hints_different_order(unsigned int n, unsigned int m)
{
    int check_1, check_2;
    ec_basis_t basis, basis_hint;
    ec_curve_t curve;
    ec_curve_init(&curve);

    // Set a supersingular elliptic curve
    // E : y^2 = x^3 + 6*x^2 + x
    fp2_set_small(&(curve.A), 6);
    fp2_set_one(&(curve.C));
    ec_curve_normalize_A24(&curve);

    // Generate a basis with hints
    uint8_t hint = ec_curve_to_basis_2f_to_hint(&basis, &curve, n, m);

    // Ensure the basis from the hint is good
    check_1 = inner_test_generated_basis(&basis, &curve, n);

    // Generate a basis using hints
    ec_curve_to_basis_2f_from_hint(&basis_hint, &curve, m, hint);

    ec_dbl_iter_basis(&basis, (n - m), &basis, &curve);

    // These two bases (of order 2^m) should be the same
    check_2 = inner_test_hint_basis(&basis, &basis_hint);

    return check_1 && check_2;
}

int
test_point_diff_invariance(int reps)
{
    ec_point_t P, Q, PQ, PQ2;
    ec_curve_t curve;

    for (int i = 0; i < reps; i++) {
        fp2_random_test(&curve.A);
        fp2_random_test(&curve.C);
        ec_random_test(&P, &curve);
        ec_random_test(&Q, &curve);

        projective_difference_point(&PQ, &P, &Q, &curve);

        ec_normalize_curve(&curve);
        ec_normalize_point(&P);
        ec_normalize_point(&Q);

        projective_difference_point(&PQ2, &P, &Q, &curve);

        fp2_mul(&PQ.x, &PQ.x, &PQ2.z);
        fp2_mul(&PQ2.x, &PQ2.x, &PQ.z);

        if (!fp2_is_equal(&PQ.x, &PQ2.x)) {
            return 0;
        }
    }
    return 1;
}

int
test_basis(void)
{
    int passed;

    // Test full order
    passed = test_basis_generation(TORSION_EVEN_POWER);
    passed &= test_basis_generation_with_hints(TORSION_EVEN_POWER);

    // Test partial order
    passed &= test_basis_generation(128);
    passed &= test_basis_generation_with_hints(128);

    // Test with different order for to_hint and from_hint
    passed &= test_basis_generation_with_hints_different_order(TORSION_EVEN_POWER, 128);

    // Special case when we have A = 0
    passed &= test_basis_generation_E0(TORSION_EVEN_POWER);
    passed &= test_basis_generation_E0(128);

    // Test that point difference does not depend on projective representation
    passed &= test_point_diff_invariance(1024);

    return passed;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int help = 0;
    int seed_set = 0;
    bool ok;

    for (int i = 1; i < argc; i++) {
        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }
    }

    if (help) {
        printf("Usage: %s [--seed=<seed>]\n", argv[0]);
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

    ok = test_basis();
    if (!ok) {
        printf("Tests failed!\n");
    } else {
        printf("All basis generation tests passed.\n");
    }
    return !ok;
}
