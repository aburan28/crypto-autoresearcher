#include "quaternion_tests.h"
#include <quaternion_data.h>
#include <quaternion_constants.h>
#include <stdlib.h>
#include <assert.h>
#include <prng.h>

// int quat_qlapoty_normeq(quat_alg_elem_t *mu1, quat_alg_elem_t *mu2, quat_alg_elem_t *theta, quat_alg_elem_t
// *smallest, const quat_ideal_t *ideal);
int
quat_test_qlapoty_qlapoty_normeq()
{
    int output = 0;
    int res = 0;
    quat_alg_elem_t mu1, mu2, theta, tmp, small;
    quat_lattice_t lat, small_equiv;
    ibz_t n, cofactor, d, n1, n2;
    quat_ideal_t ideal, I1, I2, small_ideal;
    quat_ideal_init(&ideal);
    ibz_init(&n);
    ibz_init(&n1);
    ibz_init(&n2);
    ibz_init(&d);
    ibz_init(&cofactor);
    quat_lattice_init(&lat);
    quat_ideal_init(&I1);
    quat_ideal_init(&I2);
    quat_ideal_init(&small_ideal);
    quat_lattice_init(&small_equiv);
    quat_alg_elem_init(&mu1);
    quat_alg_elem_init(&tmp);
    quat_alg_elem_init(&mu2);
    quat_alg_elem_init(&theta);
    quat_alg_elem_init(&small);

    // set &n to a prime larger than p^2
    for (int i = 0; i < 10; i++) {
        ibz_set(&n, 0, 0);
        ibz_set(&cofactor, 0, 0);
        ibz_generate_random_prime(&n, 0, 2 * ibz_bitsize(&QUATALG_PINFTY.p) - 2); // "larger than p^2"
        ibz_set_bound(&n, 2 * ibz_bitsize(&QUATALG_PINFTY.p));
        quat_random_ideal_O0_given_prime_norm(&ideal, &n, &PRNG_default_domain);
        quat_ideal_small_equivalent_coprime(NULL, &ideal, &ideal, NULL, &PRNG_default_domain);
        ibz_copy(&n, &ideal.norm);
        quat_to_lattice(&lat, &ideal);
        if (i > 0) {
            output = quat_qlapoty_normeq(&mu1, &mu2, &theta, &small, &ideal);
            res = res || !output;

            if (!res) {
                res = res || !quat_lattice_contains(NULL, &lat, &small);
                quat_alg_conj(&small, &small);
                quat_alg_norm(&n, &d, &small, &QUATALG_PINFTY);
                assert(ibz_is_one(&d));
                ibz_div(&n, &d, &n, &ideal.norm);
                assert(ibz_is_zero(&d));
                ibz_set_bound(&n, ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 3);
                if (!ibz_is_zero(&small.coord.v[3]) || !ibz_is_zero(&small.coord.v[2])) {
                    int UNUSED inert = quat_ideal_create_O0_inert(&small_ideal, &small, &n);
                    assert(inert);
                    res = res || !quat_ideals_equivalence(&small_ideal, &ideal);

                    quat_to_lattice(&small_equiv, &small_ideal);
                    res = res || !quat_lattice_contains(NULL, &small_equiv, &mu1);
                    res = res || !quat_lattice_contains(NULL, &small_equiv, &mu2);
                } else {
                    ibz_copy(&small_ideal.norm, &n);
                }
                ibz_sqrt_floor(&n, &QUATALG_PINFTY.p);
                res = res || !(ibz_cmp(&small_ideal.norm, &n) < 0);

                quat_alg_norm(&n, &d, &mu1, &QUATALG_PINFTY);
                assert(ibz_is_one(&d));
                ibz_div(&n1, &d, &n, &small_ideal.norm);
                assert(ibz_is_zero(&d));
                res = res || !ibz_is_odd(&n1);

                quat_alg_conj(&mu1, &mu1);
                ibz_mul(&mu1.denom, &mu1.denom, &small_ideal.norm);
                quat_alg_mul(&tmp, &mu2, &mu1, &QUATALG_PINFTY);
                quat_alg_sub(&tmp, &tmp, &theta);
                res = res || !quat_alg_elem_is_zero(&tmp);

                quat_alg_norm(&n, &d, &mu2, &QUATALG_PINFTY);
                assert(ibz_is_one(&d));
                ibz_div(&n2, &d, &n, &small_ideal.norm);
                assert(ibz_is_zero(&d));
                res = res || !ibz_is_odd(&n2);

                // check norms
                ibz_add(&n, &n1, &n2);
                ibz_mul_2exp(&cofactor, &ibz_const_one, QUAT_qlapoty_used_power_of_two);
                res = res || !(ibz_cmp(&cofactor, &n) == 0);
                // Qlapoty condition for usable output
                quat_alg_normalize(&theta);
                res = res || !(ibz_cmp(&theta.denom, &ibz_const_two) == 0);
            }
            if (res) {
                break;
            }
        }
    }

    if (res != 0) {
        printf("Quaternion randomized unit test qlapoty_qlapoty_normeq failed\n");
    }
    return (res);
}

int
quat_test_qlapoty_randomized_qlapoty()
{
    int output = 0;
    int res = 0;
    int e;
    quat_alg_elem_t mu1, mu2, theta, cmp, beta1, beta2;
    quat_lattice_t lat;
    ibz_t n, cofactor, d1, d2, tmp;
    quat_ideal_t ideal;
    quat_ideal_init(&ideal);
    ibz_init(&n);
    ibz_init(&d1);
    ibz_init(&d2);
    ibz_init(&cofactor);
    quat_lattice_init(&lat);
    quat_alg_elem_init(&mu1);
    quat_alg_elem_init(&mu2);
    quat_alg_elem_init(&theta);
    quat_alg_elem_init(&cmp);
    ibz_init(&tmp);
    quat_alg_elem_init(&beta1);
    quat_alg_elem_init(&beta2);
    // set &n to a prime larger than p^2
    for (int i = 0; i < 10; i++) {
        ibz_set(&n, 0, 0);
        ibz_set(&cofactor, 0, 0);
        ibz_generate_random_prime(&n, 0, 2 * ibz_bitsize(&QUATALG_PINFTY.p) - 2); // "larger than p^2"
        quat_random_ideal_O0_given_prime_norm(&ideal, &n, &PRNG_default_domain);
        quat_ideal_small_equivalent_coprime(NULL, &ideal, &ideal, NULL, &PRNG_default_domain);
        ibz_copy(&n, &ideal.norm);
        if (i > 0) {
            e = QUAT_qlapoty_used_power_of_two;
            output = quat_qlapoty(&beta1, &d1, &theta, &ideal);
            res = res || !output;

            if (!res) {
                // Qlapoty condition for usable output
                res = res || !(ibz_cmp(&theta.denom, &ibz_const_two) == 0);

                // check d1
                quat_alg_norm(&tmp, &n, &beta1, &QUATALG_PINFTY);
                ibz_div(&tmp, &n, &tmp, &ideal.norm);
                res = res || !(ibz_cmp(&tmp, &d1) == 0);

                // recover beta2
                quat_alg_conj(&theta, &theta);
                quat_alg_mul(&beta2, &theta, &beta1, &QUATALG_PINFTY);
                ibz_mul(&beta2.denom, &beta2.denom, &d1);
                quat_alg_normalize(&beta2);
                for (int j = 0; j < 4; j++)
                    ibz_set_bound(&beta2.coord.v[j], (e + 1 + ibz_get_bound(&ideal.norm)) / 2 + 3);
                ibz_set_bound(&beta2.denom, 3);

                // compute d2
                quat_alg_norm(&d2, &n, &beta2, &QUATALG_PINFTY);
                ibz_div(&d2, &n, &d2, &ideal.norm);
                ibz_set_bound(&d2, e + 1);

                // check theta
                quat_alg_conj(&cmp, &beta1);
                quat_alg_mul(&cmp, &beta2, &cmp, &QUATALG_PINFTY);
                ibz_mul(&cmp.denom, &cmp.denom, &ideal.norm);
                res = res || !quat_alg_elem_equal(&cmp, &theta);

                // check beta1, beta2 in ideal
                quat_to_lattice(&lat, &ideal);
                res = res || !quat_lattice_contains(NULL, &lat, &beta1);
                res = res || !quat_lattice_contains(NULL, &lat, &beta2);
            }
            if (res) {
                break;
            }
        }
    }

    if (res != 0) {
        printf("Quaternion randomized unit test qlapoty_randomized_qlapoty failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_qlapoty(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of qlapoty (sub-)functions\n");
    res = res | quat_test_qlapoty_qlapoty_normeq();
    res = res | quat_test_qlapoty_randomized_qlapoty();

    return (res);
}
