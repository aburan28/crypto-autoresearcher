#include <inttypes.h>
#include "id2iso_tests.h"
#include <hd.h>
#include <prng.h>
#include <tools.h>

static int
ec_is_on_curve(ec_point_t *P, ec_curve_t *E)
{
    fp2_t y_sq, X, tmp;

    fp2_copy(&X, &P->z);
    fp2_inv(&X);
    fp2_mul(&X, &X, &P->x);
    fp2_mul(&y_sq, &X, &X);
    fp2_mul(&y_sq, &y_sq, &X); // X^3
    fp2_copy(&tmp, &E->C);
    fp2_inv(&tmp);
    fp2_mul(&tmp, &tmp, &E->A);
    fp2_mul(&tmp, &tmp, &X);
    fp2_mul(&tmp, &tmp, &X);
    fp2_add(&y_sq, &y_sq, &tmp); // X^3 + A X^2
    fp2_add(&y_sq, &y_sq, &X);   // X^3 + A X^2 + X

    if (fp2_is_square(&y_sq)) {
        return 1;
    } else {
        return 0;
    }
}

int
dim2id2iso_test_dimid2iso(void)
{
    // var dec
    int found = 1;
    ibz_t temp, remainder, n1, n2;
    quat_alg_elem_t gen;

    quat_ideal_t ideal_small;
    quat_lattice_t right_order;
    ibz_mat_4x4_t reduced;
    quat_alg_elem_t beta1;
    ibz_t d1;

    // var init
    ibz_init(&temp);
    ibz_init(&remainder);
    ibz_init(&n1);
    ibz_init(&n2);
    quat_alg_elem_init(&gen);
    quat_ideal_init(&ideal_small);
    quat_lattice_init(&right_order);
    ibz_mat_4x4_init(&reduced);

    quat_alg_elem_init(&beta1);

    ibz_init(&d1);

    // computation of ideal_small
    ibz_generate_random_prime(&n1, 1, ibz_bitsize(&QUATALG_PINFTY.p));
    quat_random_ideal_O0_given_prime_norm(&ideal_small, &n1, &PRNG_default_domain);
    ec_basis_t bas_end;
    ec_curve_t codom;
    ec_curve_init(&codom);

    found = dim2id2iso_ideal_to_isogeny_qlapoty(&beta1, &d1, &codom, &bas_end, &ideal_small);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&n1, 1, ibz_bitsize(&QUATALG_PINFTY.p));
        quat_random_ideal_O0_given_prime_norm(&ideal_small, &n1, &PRNG_default_domain);
        found = dim2id2iso_ideal_to_isogeny_qlapoty(&beta1, &d1, &codom, &bas_end, &ideal_small);
    }
    return found;
}
