#include <stdio.h>
#include <internal.h>
#include <prng.h>
#include "quaternion_tests.h"
#include <quaternion_data.h>
#include <quaternion_constants.h>

// void quat_xyn_to_inert_ideal(quat_ideal_t *ideal, const ibz_t *x, const ibz_t
// *y, const ibz_t *n);
// void quat_to_lattice(quat_lattice_t *lattice, const quat_ideal_t *ideal);
int
quat_test_ideal_xyn_to_inert_ideal(void)
{
    int res = 0;
    int found = 0;
    ibz_t norm, tmp, x, y, n4;
    quat_alg_elem_t gen;
    quat_lattice_t order;
    quat_lattice_t ideal;
    quat_ideal_t ipt;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&x);
    ibz_init(&y);
    ibz_init(&n4);
    quat_alg_elem_init(&gen);
    quat_lattice_init(&ideal);
    quat_ideal_init(&ipt);
    quat_lattice_init(&order);
    quat_lattice_O0_set(&order);
    // test code
    ibz_set(&x, 0, 0);
    ibz_set(&y, 0, 0);
    ibz_set(&norm, 1, 2);
    quat_xyn_to_inert_ideal(&ipt, &x, &y, &norm);
    quat_to_lattice(&ideal, &ipt);
    res = res || !ibz_mat_4x4_equal(&ideal.basis, &order.basis);
    res = res || !(ibz_cmp(&ideal.denom, &order.denom) == 0);
    res = res || !ibz_is_one(&ipt.norm);
    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&norm, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 50);
        ibz_add(&n4, &norm, &norm);
        ibz_add(&n4, &n4, &n4);
        while (!found) {
            ibz_rand_interval(&x, &ibz_const_zero, &norm);
            ibz_mul(&tmp, &x, &x);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &QUATALG_PINFTY.p);
            ibz_neg(&tmp, &tmp);
            ibz_mod(&tmp, &tmp, &norm);
            found = (ibz_get(&tmp) % 4 == 1);
            found = found && (1 == ibz_legendre(&tmp, &norm));
            ibz_sqrt_mod_p(&y, &tmp, &norm);
            found = found && (ibz_get(&y) % 4 == 1);
        }
#ifndef NDEBUG
        ibz_t sum, prod;
        ibz_init(&sum);
        ibz_init(&prod);
        ibz_mul(&sum, &x, &x);
        ibz_mul(&sum, &sum, &ibz_const_two);
        ibz_mul(&sum, &sum, &ibz_const_two);
        ibz_mul(&prod, &y, &y);
        ibz_add(&prod, &prod, &QUATALG_PINFTY.p);
        assert(ibz_get(&prod) % 4 == 0);
        ibz_add(&sum, &sum, &prod);
        ibz_mod(&sum, &sum, &n4);
        ibz_mod(&prod, &sum, &norm);
        assert(ibz_is_zero(&prod));
        assert(ibz_is_zero(&sum));
#endif
        ibz_sub(&y, &y, &ibz_const_one);
        ibz_div(&y, &tmp, &y, &ibz_const_two);
        assert(ibz_is_zero(&tmp));
        quat_xyn_to_inert_ideal(&ipt, &x, &y, &norm);
        quat_to_lattice(&ideal, &ipt);
        quat_alg_elem_set(&gen, 2, 0, 0, 1, 0);
        ibz_add(&gen.coord.v[0], &x, &x);
        ibz_add(&gen.coord.v[1], &y, &y);
        ibz_add(&gen.coord.v[1], &gen.coord.v[1], &ibz_const_one);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !quat_lattice_contains(NULL, &ideal, &gen);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &ideal);
        res = res || !(ibz_cmp(&ipt.norm, &tmp) == 0);
        res = res || !(ibz_cmp(&ipt.norm, &norm) == 0);
        res = res || !(ibz_cmp(&ipt.x, &ipt.norm) < 0);
        res = res || !(ibz_cmp(&ipt.y, &ipt.norm) < 0);
        res = res || !(ibz_cmp(&ipt.x, &ibz_const_zero) >= 0);
        res = res || !(ibz_cmp(&ipt.y, &ibz_const_zero) >= 0);
        found = 0;
    }

    if (res != 0) {
        printf("Quaternion unit test ideal_xyn_to_inert_ideal failed\n");
    }
    return (res);
}

int
quat_test_ideal_odd_inert_gen()
{
    int res = 0;
    quat_ideal_t ideal;
    quat_alg_elem_t cmp, gen;
    quat_ideal_init(&ideal);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&cmp);

    ibz_set(&ideal.x, 3, 3);
    ibz_set(&ideal.y, 2, 3);
    ibz_set(&ideal.norm, 9, 5);
    // assume p=19

    quat_alg_elem_set(&cmp, 2, 6, 5, 1, 0);

    quat_ideal_odd_inert_gen(&gen, &ideal);
    res = res || !quat_alg_elem_equal(&gen, &cmp);

    if (res != 0) {
        printf("Quaternion unit test ideal_odd_inert_gen failed\n");
    }

    return (res);
}

// void quat_ideal_copy(quat_ideal_t *copy, const quat_ideal_t *copied);
int
quat_test_ideal_copy()
{
    int res = 0;
    quat_ideal_t copy, copied;
    quat_ideal_init(&copy);
    quat_ideal_init(&copied);
    ibz_set(&copied.norm, 3, 3);
    ibz_set(&copied.x, 2, 3);
    ibz_set(&copied.y, 1, 2);
    quat_ideal_copy(&copy, &copied);
    res = res || !(ibz_cmp(&copied.norm, &copy.norm) == 0);
    res = res || !(ibz_cmp(&copied.y, &copy.y) == 0);
    res = res || !(ibz_cmp(&copied.x, &copy.x) == 0);

    if (res) {
        printf("Quaternion unit test ideal_copy failed\n");
    }
    return (res);
}

// int quat_ideal_create_O0_inert_odd(quat_ideal_t *ideal, const quat_alg_elem_t *gen, const ibz_t *norm);
int
quat_test_ideal_create_O0_inert_odd(void)
{
    int res = 0;
    ibz_t norm, tmp, tp;
    quat_alg_elem_t gen;
    quat_ideal_t inert;
    quat_lattice_t ideal;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&tp);
    quat_ideal_init(&inert);
    quat_lattice_init(&ideal);
    quat_alg_elem_init(&gen);
    quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
    // test code
    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&norm, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 49);
        ibz_mul(&norm, &norm, &ibz_const_three);
        ibz_mul(&norm, &norm, &ibz_const_three);
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_rand_interval_bits(&tmp, 20);
            ibz_abs(&tmp, &tmp);
            ibz_mul(&tmp, &tmp, &norm);
            quat_represent_integer_even(&gen, &tmp);
        }
        res = res || !quat_ideal_create_O0_inert_odd(&inert, &gen, &norm);
        res = res || !(ibz_cmp(&inert.norm, &norm) == 0);
        res = res || !quat_ideal_shape(&inert);
        quat_to_lattice(&ideal, &inert);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !quat_lattice_contains(NULL, &ideal, &gen);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &ideal);
        res = res || !(ibz_cmp(&inert.norm, &tmp) == 0);
        quat_ideal_odd_inert_gen(&gen, &inert);
        res = res || !quat_lattice_contains(NULL, &ideal, &gen);
        ibz_mat_4x4_zero(&ideal.basis);
        ibz_vec_4_set(&gen.coord, 0, 0, 0, 0);
    }

    if (res != 0) {
        printf("Quaternion unit test ideal_create_O0_inert_odd failed\n");
    }
    return (res);
}

// void quat_ideal_create_O0_pow_two(quat_ideal_t *ideal, const quat_alg_elem_t *gen)
int
quat_test_ideal_create_O0_pow_two(void)
{
    int res = 0;
    int output = 1;
    ibz_t norm, tmp, n, d;
    quat_alg_elem_t gen;
    ibz_vec_4_t test_vec;
    quat_lattice_t O0;
    quat_ideal_t inert;
    quat_lattice_t ideal;
    ibz_vec_4_t coords;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&d);
    ibz_init(&n);
    ibz_vec_4_init(&test_vec);
    quat_ideal_init(&inert);
    quat_lattice_init(&ideal);
    quat_alg_elem_init(&gen);
    ibz_vec_4_init(&coords);
    quat_lattice_init(&O0);
    quat_lattice_O0_set(&O0);

    // check bad input case
    ibz_mul_2exp(&norm, &ibz_const_one, 246);
    quat_alg_elem_set(&gen, 1, 0, 0, 9, -6);
    ibz_set_from_str(&gen.coord.v[0], "1515838864748385364062013262586364732167", 10);
    ibz_set_from_str(&gen.coord.v[1], "406851704559284124345546273642822117202", 10);
    output = quat_ideal_create_O0_pow_two(&inert, &gen, &norm);
    res = res || output;
    quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);

    // test code
    for (int i = 0; i < 10; i++) {
        ibz_mul_2exp(&norm, &ibz_const_one, ibz_bitsize(&QUATALG_PINFTY.p) + 9 + i);
        // Needed because of some RI bug to investiagte
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_rand_interval_bits(&tmp, 20);
            ibz_add(&tmp, &tmp, &tmp);
            ibz_add(&tmp, &tmp, &ibz_const_one);
            ibz_abs(&tmp, &tmp);
            ibz_mul(&tmp, &tmp, &norm);
            quat_represent_integer_even(&gen, &tmp);
        }
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_div(&n, &d, &n, &norm);
        assert(ibz_is_zero(&d));
        assert(!ibz_is_even(&n));
        quat_alg_make_primitive(&test_vec, &d, &gen, &O0);
        assert(ibz_is_one(&d));
        output = quat_ideal_create_O0_pow_two(&inert, &gen, &norm);
        quat_to_lattice(&ideal, &inert);

        if (output) {
            res = res || !(ibz_cmp(&inert.norm, &norm) == 0);
            res = res || !quat_ideal_shape(&inert);
            quat_to_lattice(&ideal, &inert);
            res = res || !quat_lattice_is_O0_ideal(&ideal);
            res = res || !quat_lattice_contains(NULL, &ideal, &gen);
            res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
            res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
            quat_lattice_norm(&tmp, &ideal);
            res = res || !(ibz_cmp(&inert.norm, &tmp) == 0);
            quat_ideal_odd_inert_gen(&gen, &inert);
            res = res || !quat_lattice_contains(NULL, &ideal, &gen);
        } else {
            quat_change_to_O0_basis(&coords, &gen);
            res = res || !(ibz_is_even(&coords.v[2]) && ibz_is_even(&coords.v[3]));
        }
        ibz_mat_4x4_zero(&ideal.basis);
        ibz_set(&inert.norm, 0, 0);
        ibz_set(&ideal.denom, 1, 2);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
    }
    if (res != 0) {
        printf("Quaternion unit test ideal_create_O0_pow_two failed\n");
    }
    return (res);
}

// void quat_ideal_create_O0_odd(quat_ideal_t *ideal, quat_alg_elem_t *split_gen, const quat_alg_elem_t *gen,
// const ibz_t *norm)
int
quat_test_ideal_create_O0_odd(void)
{
    int res = 0;
    ibz_t norm, tmp, n, d;
    quat_alg_elem_t gen, split_gen, tmp_gen;
    quat_lattice_t ideal;
    quat_ideal_t opt;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&d);
    ibz_init(&n);
    quat_ideal_init(&opt);
    quat_lattice_init(&ideal);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&split_gen);
    quat_alg_elem_init(&tmp_gen);
    quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
    quat_alg_elem_set(&split_gen, 1, 0, 0, 0, 0);
    quat_alg_elem_set(&tmp_gen, 1, 0, 0, 0, 0);
    ibz_set(&ideal.denom, 1, 2);
    ibz_mat_4x4_zero(&ideal.basis);
    // test code
    for (int i = 0; i < 10; i++) {
        ibz_rand_interval_bits(&norm, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        ibz_abs(&norm, &norm);
        ibz_add(&norm, &norm, &norm);
        ibz_add(&norm, &norm, &ibz_const_one);
        ibz_set(&tmp, 5, 4);
        ibz_mul(&norm, &tmp, &norm);

        int exp = ibz_bitsize(&QUATALG_PINFTY.p) - ibz_bitsize(&norm);
        // Needed because of some RI bug to investiagte
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_mul_2exp(&tmp, &ibz_const_one, 30 + exp);
            ibz_mul(&tmp, &norm, &tmp);
            quat_represent_integer_even(&gen, &tmp);
            exp = exp + 1;
        }
        quat_alg_normalize(&gen);
        if (!ibz_is_one(&gen.denom)) {
            assert(ibz_cmp(&gen.denom, &ibz_const_two) == 0);
            ibz_copy(&gen.denom, &ibz_const_one);
        }

        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_div(&n, &d, &n, &norm);
        assert(ibz_is_zero(&d));
        ibz_gcd(&tmp, &n, &norm);
        assert(ibz_is_one(&tmp));

        quat_ideal_create_O0_odd(&opt, &split_gen, &gen, &norm);
        quat_to_lattice(&ideal, &opt);
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                ibz_set_bound(&ideal.basis.m[i][j], ibz_bitsize(&ideal.basis.m[i][j]) + 1);
        ibz_set_bound(&ideal.denom, ibz_bitsize(&ideal.denom) + 1);

        res = res || !(ibz_divides(&opt.norm, &norm));
        res = res || !quat_ideal_shape(&opt);
        quat_to_lattice(&ideal, &opt);
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                ibz_set_bound(&ideal.basis.m[i][j], ibz_bitsize(&ideal.basis.m[i][j]) + 1);
        ibz_set_bound(&ideal.denom, ibz_bitsize(&ideal.denom) + 1);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &ideal);
        res = res || !(ibz_cmp(&opt.norm, &tmp) == 0);
        // see if inert part is ideal
        quat_ideal_odd_inert_gen(&tmp_gen, &opt);
        res = res || !quat_lattice_contains(NULL, &ideal, &tmp_gen);

        // test split part
        res = res || !(ibz_cmp(&split_gen.denom, &ibz_const_one) == 0);
        res = res || !(ibz_cmp(&split_gen.coord.v[2], &ibz_const_zero) == 0);
        res = res || !(ibz_cmp(&split_gen.coord.v[3], &ibz_const_zero) == 0);
        quat_alg_norm(&n, &d, &split_gen, &QUATALG_PINFTY);
        res = res || !ibz_divides(&norm, &n);
        ibz_mul(&d, &n, &opt.norm);
        res = res || !(ibz_cmp(&d, &norm) == 0);

        quat_alg_conj(&tmp_gen, &split_gen);
        ibz_mul(&tmp_gen.denom, &tmp_gen.denom, &n);
        quat_alg_mul(&tmp_gen, &gen, &tmp_gen, &QUATALG_PINFTY); // multiply by inverse of split part
        quat_alg_normalize(&tmp_gen);
        ibz_set_bound(&tmp_gen.coord.v[0], ibz_bitsize(&tmp_gen.coord.v[0]) + 1);
        ibz_set_bound(&tmp_gen.coord.v[1], ibz_bitsize(&tmp_gen.coord.v[1]) + 1);
        ibz_set_bound(&tmp_gen.coord.v[2], ibz_bitsize(&tmp_gen.coord.v[2]) + 1);
        ibz_set_bound(&tmp_gen.coord.v[3], ibz_bitsize(&tmp_gen.coord.v[3]) + 1);
        ibz_set_bound(&tmp_gen.denom, 3);
        res = res || !quat_lattice_contains(NULL, &ideal, &tmp_gen);

        ibz_mat_4x4_zero(&ideal.basis);
        ibz_set(&opt.norm, 0, 0);
        ibz_set(&ideal.denom, 1, 2);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
        quat_alg_elem_set(&split_gen, 1, 0, 0, 0, 0);
    }
    if (res != 0) {
        printf("Quaternion unit test ideal_create_O0_odd failed\n");
    }
    return (res);
}

// int quat_random_ideal_O0_given_prime_norm(quat_ideal_t *ideal, const ibz_t *norm, prng_domain_ctx_t *prng_domain);
int
quat_test_ideal_random_ideal_O0_given_prime_norm()
{
    int res = 0;
    quat_lattice_t ideal;
    quat_ideal_t opt;
    quat_lattice_t test;
    quat_lattice_t O0;
    ibz_t p, norm;
    quat_ideal_init(&opt);
    quat_lattice_init(&test);
    ibz_init(&norm);
    ibz_init(&p);
    quat_lattice_init(&ideal);
    quat_lattice_init(&(O0));
    quat_lattice_O0_set(&O0);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 50);
        res = res || !quat_random_ideal_O0_given_prime_norm(&opt, &p, &PRNG_default_domain);
        res = res || (ibz_cmp(&(opt.norm), &p) != 0);
        res = res || !quat_ideal_shape(&opt);
        quat_to_lattice(&ideal, &opt);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&p, &ideal);
        res = res || !(ibz_cmp(&opt.norm, &p) == 0);
    }

    if (res) {
        printf("Quaternion unit test ideal_random_ideal_O0_given_prime_norm failed\n");
    }
    return (res);
}

// int quat_random_ideal_O0_given_arbitrary_odd_norm(quat_ideal_t *ideal, quat_alg_elem_t *split_gen, const
// ibz_t *norm, const quat_represent_integer_params_t *params, const ibz_t *prime_cofactor, prng_domain_ctx_t
// *prng_domain);
int
quat_test_ideal_random_ideal_O0_given_arbitrary_odd_norm(void)
{
    int res = 0;
    ibz_t norm, tmp, cofactor, n, d;
    quat_alg_elem_t tmp_gen, split_gen;
    ibz_vec_4_t test_vec;
    quat_lattice_t ideal;
    quat_ideal_t opt;
    quat_lattice_t test;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&d);
    ibz_init(&n);
    ibz_init(&cofactor);
    ibz_vec_4_init(&test_vec);
    quat_ideal_init(&opt);
    quat_lattice_init(&ideal);
    quat_alg_elem_init(&split_gen);
    quat_alg_elem_init(&tmp_gen);
    quat_lattice_init(&test);
    quat_alg_elem_set(&split_gen, 1, 0, 0, 0, 0);
    quat_alg_elem_set(&tmp_gen, 1, 1, 0, 0, 0);
    ibz_mat_4x4_zero(&ideal.basis);
    ibz_set(&ideal.denom, 1, 2);
    ibz_mat_4x4_zero(&test.basis);
    ibz_set(&test.denom, 1, 2);

    ibz_generate_random_prime(&cofactor, 0, 60);
    for (int i = 0; i < 10; i++) {
        // sample odd number
        ibz_set(&n, 2, 3);
        while (!ibz_is_one(&n)) {
            ibz_rand_interval_bits(&norm, ibz_bitsize(&QUATALG_PINFTY.p) - 1);
            ibz_abs(&norm, &norm);
            ibz_add(&norm, &norm, &norm);
            ibz_add(&norm, &norm, &ibz_const_one);
            ibz_gcd(&n, &norm, &cofactor);
        }

        // varying shift_gen is tested in protocol_quaternion_response_kat_stability
        quat_alg_elem_set(&tmp_gen, 1, 1, 0, 0, 0);
        quat_random_ideal_O0_given_arbitrary_odd_norm(&opt, &split_gen, &norm, &tmp_gen, &PRNG_default_domain);
        quat_to_lattice(&ideal, &opt);

        ibz_mod(&tmp, &norm, &opt.norm);
        res = res || !(ibz_is_zero(&tmp));
        res = res || !quat_ideal_shape(&opt);
        quat_to_lattice(&ideal, &opt);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &ideal);
        res = res || !(ibz_cmp(&opt.norm, &tmp) == 0);
        // see if inert part is ideal
        quat_ideal_odd_inert_gen(&tmp_gen, &opt);
        res = res || !quat_lattice_contains(NULL, &ideal, &tmp_gen);

        // test split part
        res = res || !(ibz_cmp(&split_gen.denom, &ibz_const_one) == 0);
        res = res || !(ibz_cmp(&split_gen.coord.v[2], &ibz_const_zero) == 0);
        res = res || !(ibz_cmp(&split_gen.coord.v[3], &ibz_const_zero) == 0);
        quat_alg_norm(&n, &d, &split_gen, &QUATALG_PINFTY);
        res = res || !ibz_divides(&norm, &n);
        ibz_mul(&d, &n, &opt.norm);
        res = res || !(ibz_cmp(&d, &norm) == 0);

        ibz_mat_4x4_zero(&ideal.basis);
        ibz_set(&opt.norm, 0, 0);
        ibz_set(&ideal.denom, 1, 2);
        quat_alg_elem_set(&split_gen, 1, 0, 0, 0, 0);
        assert(!res);
    }
    if (res != 0) {
        printf("Quaternion unit test ideal_random_ideal_O0_given_arbitrary_odd_norm failed\n");
    }
    return (res);
}

// void quat_ideal_intersect_O0(quat_ideal_t *intersection, const quat_ideal_t *a, const quat_ideal_t
// *b, const quat_alg_elem_t *split_a);
int
quat_test_ideal_intersection()
{
    int res = 0;
    int ret = 0;
    quat_lattice_t a, b, as, inters, inter;
    quat_ideal_t a_ideal;
    quat_ideal_t b_ideal;
    quat_ideal_t a_cp;
    quat_ideal_t b_cp;
    quat_ideal_t inter_ideal;
    ibz_t p, norm, tmp, n_split, n, d;
    quat_alg_elem_t split, tmp_gen;
    ibz_init(&norm);
    ibz_init(&p);
    ibz_init(&tmp);
    ibz_init(&n_split);
    ibz_init(&n);
    ibz_init(&d);
    quat_alg_elem_init(&split);
    quat_alg_elem_init(&tmp_gen);
    quat_ideal_init(&a_ideal);
    quat_ideal_init(&b_ideal);
    quat_ideal_init(&a_cp);
    quat_ideal_init(&b_cp);
    quat_ideal_init(&inter_ideal);
    quat_lattice_init(&a);
    quat_lattice_init(&as);
    quat_lattice_init(&b);
    quat_lattice_init(&inter);
    quat_lattice_init(&inters);

    // No split part
    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&a_ideal, &p, &PRNG_default_domain);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&b_ideal, &p, &PRNG_default_domain);
        quat_to_lattice(&a, &a_ideal);
        quat_to_lattice(&b, &b_ideal);
        ibz_gcd(&p, &a_ideal.norm, &b_ideal.norm);
        if (ret) {
            printf("random ideal generation failure\n");
            printf("Quaternion unit test ideal_intersection failed\n");
            return (1);
        }
        assert(ibz_is_one(&p));
        quat_ideal_intersect_O0(&inter_ideal, &a_ideal, &b_ideal, NULL);
        quat_to_lattice(&inter, &inter_ideal);
        res = res || !quat_lattice_inclusion(&inter, &a);
        res = res || !quat_lattice_inclusion(&inter, &b);
        ibz_mul(&tmp, &a_ideal.norm, &b_ideal.norm);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
        res = res || !quat_ideal_shape(&inter_ideal);
        quat_to_lattice(&inter, &inter_ideal);
        res = res || !quat_lattice_is_O0_ideal(&inter);
        res = res || !ibz_mat_4x4_is_hnf(&inter.basis);
        res = res || !(ibz_cmp(&inter.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &inter);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
    }
    // with small split part
    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&a_ideal, &p, &PRNG_default_domain);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&b_ideal, &p, &PRNG_default_domain);
        if (ret) {
            printf("Randomness failurre in quaternion unit test ideal_intersection\n");
            return (ret);
        }
        quat_to_lattice(&a, &a_ideal);
        quat_to_lattice(&b, &b_ideal);
        ibz_gcd(&p, &a_ideal.norm, &b_ideal.norm);
        assert(ibz_is_one(&p));
        quat_alg_elem_set(&split, 1, 2, 1, 0, 0);

        quat_lattice_from_ideal_split(&as, &a_ideal, &split);

        quat_ideal_copy(&a_cp, &a_ideal);
        quat_ideal_copy(&b_cp, &b_ideal);
        quat_ideal_intersect_O0(&inter_ideal, &a_ideal, &b_ideal, &split);
        ibz_mul(&tmp, &a_ideal.norm, &b_ideal.norm);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
        quat_to_lattice(&inter, &inter_ideal);
        quat_lattice_from_ideal_split(&inters, &inter_ideal, &split);
        res = res || !quat_lattice_inclusion(&inters, &b);
        res = res || !quat_lattice_inclusion(&inter, &a);
        res = res || !quat_ideal_shape(&inter_ideal);
        res = res || !quat_lattice_is_O0_ideal(&inter);
        res = res || !ibz_mat_4x4_is_hnf(&inter.basis);
        res = res || !(ibz_cmp(&inter.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &inter);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);

        // left same as output
        quat_ideal_intersect_O0(&a_ideal, &a_ideal, &b_ideal, &split);
        quat_ideal_copy(&inter_ideal, &a_ideal);
        quat_ideal_copy(&a_ideal, &a_cp);
        quat_ideal_copy(&b_ideal, &b_cp);
        ibz_mul(&tmp, &a_ideal.norm, &b_ideal.norm);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
        quat_to_lattice(&inter, &inter_ideal);
        quat_lattice_from_ideal_split(&inters, &inter_ideal, &split);
        res = res || !quat_lattice_inclusion(&inters, &b);
        res = res || !quat_lattice_inclusion(&inter, &a);
        res = res || !quat_ideal_shape(&inter_ideal);
        res = res || !quat_lattice_is_O0_ideal(&inter);
        res = res || !ibz_mat_4x4_is_hnf(&inter.basis);
        res = res || !(ibz_cmp(&inter.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &inter);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);

        // right same as output
        quat_ideal_intersect_O0(&b_ideal, &a_ideal, &b_ideal, &split);
        quat_ideal_copy(&inter_ideal, &b_ideal);
        quat_ideal_copy(&a_ideal, &a_cp);
        quat_ideal_copy(&b_ideal, &b_cp);
        ibz_mul(&tmp, &a_ideal.norm, &b_ideal.norm);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
        quat_to_lattice(&inter, &inter_ideal);
        quat_lattice_from_ideal_split(&inters, &inter_ideal, &split);
        res = res || !quat_lattice_inclusion(&inters, &b);
        res = res || !quat_lattice_inclusion(&inter, &a);
        res = res || !quat_ideal_shape(&inter_ideal);
        res = res || !quat_lattice_is_O0_ideal(&inter);
        res = res || !ibz_mat_4x4_is_hnf(&inter.basis);
        res = res || !(ibz_cmp(&inter.denom, &ibz_const_two) == 0);
        quat_lattice_norm(&tmp, &inter);
        res = res || (ibz_cmp(&(inter_ideal.norm), &tmp) != 0);
    }
    if (res) {
        printf("Quaternion unit test ideal_intersection failed\n");
    }
    return (res);
}

// void quat_ideal_mul_O0(quat_lattice_t *prod, const quat_ideal_t *a, const quat_ideal_t *b);
int
quat_test_ideal_mul_O0()
{
    int res = 0;
    int red = 0;
    quat_lattice_t a, b, prod;
    quat_ideal_t a_ideal, b_ideal;
    quat_alg_elem_t a_gen, b_gen, ac_gen, prod_gen;
    ibz_t np;
    ibz_t p, norm;
    ibz_init(&np);
    ibz_init(&norm);
    ibz_init(&p);
    quat_alg_elem_init(&a_gen);
    quat_alg_elem_init(&b_gen);
    quat_alg_elem_init(&ac_gen);
    quat_alg_elem_init(&prod_gen);
    quat_lattice_init(&a);
    quat_lattice_init(&b);
    quat_lattice_init(&prod);
    quat_ideal_init(&a_ideal);
    quat_ideal_init(&b_ideal);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        red = red || !quat_random_ideal_O0_given_prime_norm(&a_ideal, &p, &PRNG_default_domain);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
        red = red || !quat_random_ideal_O0_given_prime_norm(&b_ideal, &p, &PRNG_default_domain);
        quat_to_lattice(&a, &a_ideal);
        quat_to_lattice(&b, &b_ideal);
        if (red) {
            printf("Randomness failure in quaternion unit test ideal_mul_O0\n");
            return (res);
        }
        ibz_gcd(&p, &a_ideal.norm, &b_ideal.norm);
        assert(ibz_is_one(&p));
        // actual test
        quat_ideal_mul_O0(&prod, &a_ideal, &b_ideal);
        res = res || !quat_lattice_is_ideal(&prod);
        quat_ideal_odd_inert_gen(&a_gen, &a_ideal);
        quat_ideal_odd_inert_gen(&b_gen, &b_ideal);
        quat_alg_conj(&ac_gen, &a_gen);
        quat_alg_mul(&prod_gen, &ac_gen, &b_gen, &QUATALG_PINFTY);
        res = res || !quat_lattice_contains(NULL, &prod, &prod_gen);
        quat_lattice_norm(&np, &prod);
        ibz_mul(&norm, &a_ideal.norm, &b_ideal.norm);
        res = res || !(ibz_cmp(&norm, &np) == 0);
        assert(!res);
    }
    if (res) {
        printf("Quaternion unit test ideal_mul_O0 failed\n");
    }
    return (res);
}

// void quat_ideal_product_gram_matrix(ibz_mat_4x4_t *gram, const quat_lattice_t *lat);
int
quat_test_ideal_product_gram_matrix()
{
    int res = 0;
    int red = 0;
    quat_lattice_t prod;
    quat_ideal_t a_ideal, b_ideal;
    ibz_t np;
    ibz_t p, norm;
    ibz_mat_4x4_t g, g_cmp, g_norm, g_test;
    ibz_init(&np);
    ibz_init(&norm);
    ibz_init(&p);
    ibz_mat_4x4_init(&g);
    ibz_mat_4x4_init(&g_cmp);
    ibz_mat_4x4_init(&g_norm);
    ibz_mat_4x4_init(&g_test);
    quat_lattice_init(&prod);
    quat_ideal_init(&a_ideal);
    quat_ideal_init(&b_ideal);

    for (int i = 0; i < 10; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p));
        red = red || !quat_random_ideal_O0_given_prime_norm(&a_ideal, &p, &PRNG_default_domain);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p));
        red = red || !quat_random_ideal_O0_given_prime_norm(&b_ideal, &p, &PRNG_default_domain);
        if (red) {
            printf("Randomness failure in quaternion unit test ideal_product_gram_matrix\n");
            return (res);
        }
        ibz_gcd(&p, &a_ideal.norm, &b_ideal.norm);
        res = res || !(ibz_is_one(&p));
        quat_ideal_mul_O0(&prod, &a_ideal, &b_ideal);
        quat_lattice_gram(&g_cmp, &prod);
        int UNUSED test_d1 = ibz_mat_4x4_scalar_div(&g_cmp, &prod.denom, &g_cmp);
        res = res || !(test_d1);
        int UNUSED test_d2 = ibz_mat_4x4_scalar_div(&g_cmp, &prod.denom, &g_cmp);
        res = res || !(test_d2);
        ibz_mul(&np, &a_ideal.norm, &b_ideal.norm);
        int UNUSED test = ibz_mat_4x4_scalar_div(&g_test, &np, &g_cmp);
        res = res || !(test);
        res = res || ibz_mat_4x4_equal(&g_test, &g_cmp);

        quat_ideal_product_gram_matrix(&g, &prod);
        ibz_mat_4x4_scalar_mul(&g_norm, &a_ideal.norm, &g);
        ibz_mat_4x4_scalar_mul(&g_norm, &b_ideal.norm, &g_norm);

        res = res || !ibz_mat_4x4_equal(&g_norm, &g_cmp);
        res = res || !ibz_mat_4x4_equal(&g, &g_test);

        ibz_mat_4x4_scalar_mul(&g_test, &np, &g_test);
        res = res || !ibz_mat_4x4_equal(&g_test, &g_cmp);
    }
    if (res) {
        printf("Quaternion unit test ideal_product_gram_matrix failed\n");
    }
    return (res);
}

// int quat_ideal_create_O0_inert(quat_ideal_t *ideal, const quat_alg_elem_t *gen, const ibz_t *norm);
int
quat_test_ideal_create_O0_inert()
{
    int res = 0;
    int inert_ok = 0;
    ibz_t norm, tmp, n, d, cofactor;
    quat_alg_elem_t gen, split_gen, tmp_gen;
    quat_lattice_t ideal;
    quat_ideal_t inert;
    // use sqisign prime instead
    ibz_init(&norm);
    ibz_init(&tmp);
    ibz_init(&d);
    ibz_init(&n);
    ibz_init(&cofactor);
    quat_ideal_init(&inert);
    quat_lattice_init(&ideal);
    quat_alg_elem_init(&gen);
    quat_alg_elem_init(&split_gen);
    quat_alg_elem_init(&tmp_gen);
    ibz_generate_random_prime(&cofactor, 0, 50);
    quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
    // test code
    for (int i = 0; i < 10; i++) {
        ibz_rand_interval_bits(&norm, ibz_bitsize(&QUATALG_PINFTY.p) - 1);
        ibz_abs(&norm, &norm);

        // Needed because of some RI bug to investiagte
        while (quat_alg_elem_is_zero(&gen)) {
            ibz_mul(&tmp, &norm, &cofactor);
            quat_represent_integer_even(&gen, &tmp);
        }
        quat_alg_normalize(&gen);

        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_div(&n, &d, &n, &norm);
        assert(ibz_is_zero(&d));
        ibz_gcd(&tmp, &n, &norm);
        assert(ibz_is_one(&tmp));
        if (i % 4 == 3) {
            quat_alg_elem_set(&split_gen, 1, 1, 1, 0, 0);
            quat_alg_mul(&gen, &split_gen, &gen, &QUATALG_PINFTY);
            ibz_add(&norm, &norm, &norm);
        }
        if (i % 5 == 0) {
            ibz_set(&tmp, 5, 4);
            quat_alg_elem_set(&split_gen, 1, 2, 1, 0, 0);
            for (int j = 0; j < 1 + (i / 10); j++) {
                quat_alg_mul(&gen, &split_gen, &gen, &QUATALG_PINFTY);
                ibz_mul(&norm, &norm, &tmp);
            }
        }
        inert_ok = quat_ideal_create_O0_inert(&inert, &gen, &norm);
        quat_to_lattice(&ideal, &inert);

        if (!inert_ok) {
            res = res || !(ibz_divides(&norm, &inert.norm));
        } else {
            res = res || !(ibz_cmp(&inert.norm, &norm) == 0);
        }
        res = res || !quat_ideal_shape(&inert);
        quat_to_lattice(&ideal, &inert);
        res = res || !quat_lattice_is_O0_ideal(&ideal);
        res = res || !ibz_mat_4x4_is_hnf(&ideal.basis);
        res = res || !(ibz_cmp(&ideal.denom, &ibz_const_two) == 0);
        ibz_set(&ideal.denom, 2, 3);
        quat_lattice_norm(&tmp, &ideal);
        res = res || !(ibz_cmp(&inert.norm, &tmp) == 0);
        quat_mod_O0(&gen, &gen, &inert.norm);
        if (inert_ok) {
            res = res || !quat_lattice_contains(NULL, &ideal, &gen);
        }
        // should maybe find way to also test if split input ideal is correct
        // also if splitting is detected correctly
        ibz_mat_4x4_zero(&ideal.basis);
        ibz_set(&inert.norm, 0, 0);
        ibz_set(&ideal.denom, 1, 2);
        quat_alg_elem_set(&gen, 1, 0, 0, 0, 0);
        quat_alg_elem_set(&split_gen, 1, 0, 0, 0, 0);
    }
    if (res != 0) {
        printf("Quaternion unit test ideal_create_O0_inert failed\n");
    }
    return (res);
}

// void quat_ideal_shortest_equivalent(quat_alg_elem_t *gen, quat_alg_elem_t *equiv, quat_ideal_t *red, const
// quat_ideal_t *ideal);
int
quat_test_ideal_shortest_equivalent()
{
    int res = 0;
    int ret = 0;
    quat_lattice_t lat;
    quat_lattice_t red;
    quat_ideal_t test, old;
    quat_alg_elem_t gen, equiv;
    ibz_t p, norm, n, d, c;
    quat_ideal_t ideal_i, ideal_e;
    quat_lattice_init(&red);
    ibz_init(&norm);
    ibz_init(&p);
    ibz_init(&d);
    ibz_init(&n);
    ibz_init(&c);
    quat_alg_elem_init(&gen);
    quat_ideal_init(&test);
    quat_alg_elem_init(&equiv);
    quat_lattice_init(&lat);
    quat_ideal_init(&ideal_e);
    quat_ideal_init(&ideal_i);
    quat_ideal_init(&old);
    for (int i = 0; i < 10; i++) {
        if (res)
            break;
        // should use non-prime
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p));
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&ideal_i, &p, &PRNG_default_domain);
        if (ret) {
            printf("Randomness failure in quaternion unit test ideal_shortest_equivalent\n");
            return (ret);
        }
        quat_ideal_shortest_equivalent(&gen, &equiv, &ideal_e, &ideal_i);
        // test generator
        quat_lattice_O0_set(&lat);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);
        res = res || !quat_lattice_contains(NULL, &lat, &equiv);
        quat_ideal_create_O0_inert(&test, &gen, &ideal_e.norm);
        res = res || !quat_ideal_equal(&test, &ideal_e);
        quat_to_lattice(&lat, &ideal_e);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);
        // test equivalence
        quat_to_lattice(&lat, &ideal_i);
        res = res || !quat_lattice_contains(NULL, &lat, &equiv);
        // check norm of red against norm of equiv
        quat_alg_norm(&n, &d, &equiv, &QUATALG_PINFTY);
        res = res || !ibz_is_one(&d);
        ibz_div(&n, &d, &n, &ideal_i.norm);
        res = res || !ibz_is_zero(&d);
        res = res || !(ibz_cmp(&n, &ideal_e.norm) == 0);
        ibz_sqrt_floor(&d, &QUATALG_PINFTY.p);
        // check norm of equiv small enough
        res = res || !(ibz_cmp(&d, &ideal_e.norm) > 0);
        // multiply conj(equiv)/NI with genI and check if in red
        quat_ideal_odd_inert_gen(&gen, &ideal_i);
        quat_alg_conj(&equiv, &equiv);
        ibz_mul(&equiv.denom, &equiv.denom, &ideal_i.norm);
        quat_alg_mul(&gen, &gen, &equiv, &QUATALG_PINFTY);
        quat_mod_O0(&gen, &gen, &ideal_e.norm);
        quat_to_lattice(&lat, &ideal_e);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);
        quat_ideal_copy(&old, &ideal_e);

        // without equiv
        quat_ideal_shortest_equivalent(&gen, NULL, &ideal_e, &ideal_i);
        quat_lattice_O0_set(&lat);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);
        res = res || !quat_ideal_equal(&old, &ideal_e);
        quat_ideal_create_O0_inert(&test, &gen, &ideal_e.norm);
        res = res || !quat_ideal_equal(&test, &ideal_e);
        quat_to_lattice(&lat, &ideal_e);
        quat_mod_O0(&gen, &gen, &ideal_e.norm);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);

        // without gen
        quat_ideal_shortest_equivalent(NULL, &equiv, &ideal_e, &ideal_i);
        quat_to_lattice(&lat, &ideal_i);
        res = res || !quat_lattice_contains(NULL, &lat, &equiv);
        // check norm of red against norm of equiv
        quat_alg_norm(&n, &d, &equiv, &QUATALG_PINFTY);
        res = res || !ibz_is_one(&d);
        ibz_div(&n, &d, &n, &ideal_i.norm);
        res = res || !ibz_is_zero(&d);
        res = res || !(ibz_cmp(&n, &ideal_e.norm) == 0);
        ibz_sqrt_floor(&d, &QUATALG_PINFTY.p);
        // check norm of equiv small enough
        res = res || !(ibz_cmp(&d, &ideal_e.norm) > 0);
        // multiply conj(equiv)/NI with genI and check if in red
        quat_ideal_odd_inert_gen(&gen, &ideal_i);
        quat_alg_conj(&equiv, &equiv);
        ibz_mul(&equiv.denom, &equiv.denom, &ideal_i.norm);
        quat_alg_mul(&gen, &gen, &equiv, &QUATALG_PINFTY);
        quat_to_lattice(&lat, &ideal_e);
        quat_mod_O0(&gen, &gen, &ideal_e.norm);
        res = res || !quat_lattice_contains(NULL, &lat, &gen);
        quat_ideal_copy(&old, &ideal_e);

        // without both
        quat_ideal_shortest_equivalent(NULL, NULL, &ideal_e, &ideal_i);
        res = res || !quat_ideal_equal(&old, &ideal_e);
    }

    if (res != 0) {
        printf("Quaternion unit test ideal_create_shortest_equivalent failed\n");
    }
    return (res);
}

// void quat_ideal_small_equivalent_coprime_enumeration(quat_alg_elem_t *gen, quat_ideal_t *equiv, const
// quat_lattice_t *ideal, const ibz_t *ideal_norm, const ibz_t *coprime_to);
int
quat_test_ideal_small_equivalent_coprime_enumeration()
{
    int res = 0;
    int ret = 0;
    quat_lattice_t ideal;
    quat_lattice_t red;
    quat_ideal_t id;
    quat_ideal_t equiv;
    quat_lattice_t equiv_lat;
    quat_ideal_t test;
    quat_alg_elem_t gen;
    ibz_t p, norm, n, d, c;
    quat_ideal_init(&id);
    quat_ideal_init(&test);
    ibz_init(&norm);
    ibz_init(&p);
    ibz_init(&d);
    ibz_init(&n);
    ibz_init(&c);
    quat_alg_elem_init(&gen);
    quat_ideal_init(&equiv);
    quat_lattice_init(&ideal);
    quat_lattice_init(&equiv_lat);
    quat_lattice_init(&red);

    // tests with coprimality
    for (int i = 0; i < 5; i++) {
        ibz_set(&c, 0, 0);
        while (ibz_is_zero(&c))
            ibz_rand_interval_bits(&c, 10);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&id, &p, &PRNG_default_domain);
        if (ret) {
            goto randomness_failure;
        }
        quat_ideal_reduce_basis(&red, &id);
        quat_to_lattice(&ideal, &id);
        quat_ideal_small_equivalent_coprime_enumeration(&gen, &equiv, &red, &id.norm, &c, &PRNG_default_domain);

        // test coprime
        ibz_gcd(&d, &c, &equiv.norm);
        res = res || !ibz_is_one(&d);
        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test generator
        quat_to_lattice(&equiv_lat, &equiv);
        quat_alg_conj(&gen, &gen);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        ibz_copy(&gen.coord.v[0], &red.basis.m[0][3]);
        ibz_copy(&gen.coord.v[1], &red.basis.m[1][3]);
        ibz_copy(&gen.coord.v[2], &red.basis.m[2][3]);
        ibz_copy(&gen.coord.v[3], &red.basis.m[3][3]);
        ibz_copy(&gen.denom, &red.denom);
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        assert(ibz_is_one(&d));
        ibz_set(&d, QUAT_equiv_bound_coeff, 9);
        ibz_mul(&d, &d, &d);
        ibz_mul(&d, &d, &d);
        ibz_mul(&n, &d, &n);
        ibz_div(&n, &d, &n, &id.norm);
        assert(ibz_is_zero(&d));
        res = res || (ibz_cmp(&equiv.norm, &n) > 0);
    }
    // test with primality
    for (int i = 0; i < 3; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&id, &p, &PRNG_default_domain);
        if (ret) {
            goto randomness_failure;
        }

        quat_ideal_reduce_basis(&red, &id);
        quat_to_lattice(&ideal, &id);
        quat_ideal_small_equivalent_coprime_enumeration(
            &gen, &equiv, &red, &id.norm, &ibz_const_zero, &PRNG_default_domain);

        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test prime
        res = res || !ibz_probab_prime(&equiv.norm, 30);
        // test generator
        quat_alg_conj(&gen, &gen);
        quat_to_lattice(&equiv_lat, &equiv);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        ibz_copy(&gen.coord.v[0], &red.basis.m[0][3]);
        ibz_copy(&gen.coord.v[1], &red.basis.m[1][3]);
        ibz_copy(&gen.coord.v[2], &red.basis.m[2][3]);
        ibz_copy(&gen.coord.v[3], &red.basis.m[3][3]);
        ibz_copy(&gen.denom, &red.denom);
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_div(&n, &d, &n, &id.norm);
        assert(ibz_is_zero(&d));
        ibz_set(&d, QUAT_equiv_bound_coeff, 9);
        ibz_mul(&d, &d, &d);
        ibz_mul(&d, &d, &d);
        ibz_mul(&n, &d, &n);
        res = res || (ibz_cmp(&equiv.norm, &n) > 0);

        // using NULL
        res = res || !quat_ideal_small_equivalent_coprime_enumeration(
                         &gen, &equiv, &red, &id.norm, NULL, &PRNG_default_domain);
        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test generator
        quat_alg_conj(&gen, &gen);
        quat_to_lattice(&equiv_lat, &equiv);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        ibz_copy(&gen.coord.v[0], &red.basis.m[0][3]);
        ibz_copy(&gen.coord.v[1], &red.basis.m[1][3]);
        ibz_copy(&gen.coord.v[2], &red.basis.m[2][3]);
        ibz_copy(&gen.coord.v[3], &red.basis.m[3][3]);
        ibz_copy(&gen.denom, &red.denom);
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_set(&d, QUAT_equiv_bound_coeff, 9);
        ibz_mul(&d, &d, &d);
        ibz_mul(&d, &d, &d);
        ibz_mul(&n, &d, &n);
        ibz_div(&n, &d, &n, &id.norm);
        assert(ibz_is_zero(&d));
        res = res || (ibz_cmp(&equiv.norm, &n) > 0);
    }

randomness_failure:;
    if (ret)
        printf("Randomness failure in quaternion unit test ideal_small_equivalent_coprime_enumeration\n");

    if (res) {
        printf("Quaternion unit test ideal_small_equivalent_coprime_enumeration failed\n");
    }
    return (res | ret);
}

// int quat_ideal_small_equivalent_coprime(quat_alg_elem_t *gen, quat_ideal_t *equiv, const quat_ideal_t
// *ideal, const ibz_t *coprime_to);
int
quat_test_ideal_small_equivalent_coprime()
{
    int res = 0;
    int ret = 0;
    int bound = QUAT_equiv_bound_coeff;
    quat_lattice_t ideal;
    quat_lattice_t red;
    quat_ideal_t id;
    quat_ideal_t equiv;
    quat_lattice_t equiv_lat;
    quat_ideal_t test;
    quat_alg_elem_t gen;
    ibz_t p, norm, n, d, c, n3;
    quat_ideal_init(&id);
    quat_ideal_init(&test);
    ibz_init(&norm);
    ibz_init(&p);
    ibz_init(&d);
    ibz_init(&n);
    ibz_init(&n3);
    ibz_init(&c);
    quat_alg_elem_init(&gen);
    quat_ideal_init(&equiv);
    quat_lattice_init(&ideal);
    quat_lattice_init(&equiv_lat);
    quat_lattice_init(&red);

    // tests with coprimality
    for (int i = 0; i < 5; i++) {
        ibz_set(&c, 0, 0);
        while (ibz_is_zero(&c))
            ibz_rand_interval_bits(&c, 10);
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&id, &p, &PRNG_default_domain);
        if (ret)
            goto randomness_failure;

        quat_ideal_reduce_basis(&red, &id);
        quat_to_lattice(&ideal, &id);
        ibz_copy(&gen.coord.v[0], &red.basis.m[0][3]);
        ibz_copy(&gen.coord.v[1], &red.basis.m[1][3]);
        ibz_copy(&gen.coord.v[2], &red.basis.m[2][3]);
        ibz_copy(&gen.coord.v[3], &red.basis.m[3][3]);
        ibz_copy(&gen.denom, &red.denom);
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_set(&d, bound, 9);
        ibz_mul(&d, &d, &d);
        ibz_mul(&d, &d, &d);
        ibz_mul(&n, &d, &n);
        ibz_div(&n3, &d, &n, &id.norm);
        assert(ibz_is_zero(&d));
        res = res || !quat_ideal_small_equivalent_coprime(&gen, &equiv, &id, &c, &PRNG_default_domain);

        // test coprime
        ibz_gcd(&d, &c, &equiv.norm);
        res = res || !ibz_is_one(&d);
        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test generator
        quat_to_lattice(&equiv_lat, &equiv);
        quat_alg_conj(&gen, &gen);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        res = res || (ibz_cmp(&equiv.norm, &n3) > 0);
    }
    // test with primality
    for (int i = 0; i < 3; i++) {
        ibz_generate_random_prime(&p, 0, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
        ret = ret || !quat_random_ideal_O0_given_prime_norm(&id, &p, &PRNG_default_domain);
        if (ret)
            goto randomness_failure;

        quat_ideal_reduce_basis(&red, &id);
        quat_to_lattice(&ideal, &id);
        ibz_copy(&gen.coord.v[0], &red.basis.m[0][3]);
        ibz_copy(&gen.coord.v[1], &red.basis.m[1][3]);
        ibz_copy(&gen.coord.v[2], &red.basis.m[2][3]);
        ibz_copy(&gen.coord.v[3], &red.basis.m[3][3]);
        ibz_copy(&gen.denom, &red.denom);
        quat_alg_norm(&n, &d, &gen, &QUATALG_PINFTY);
        assert(ibz_is_one(&d));
        ibz_set(&d, bound, 9);
        ibz_mul(&d, &d, &d);
        ibz_mul(&d, &d, &d);
        ibz_mul(&n, &d, &n);
        ibz_div(&n3, &d, &n, &id.norm);
        assert(ibz_is_zero(&d));
        res = res || !quat_ideal_small_equivalent_coprime(&gen, &equiv, &id, &ibz_const_zero, &PRNG_default_domain);

        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test prime
        res = res || !ibz_probab_prime(&equiv.norm, 30);
        // test generator
        quat_alg_conj(&gen, &gen);
        quat_to_lattice(&equiv_lat, &equiv);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        res = res || (ibz_cmp(&equiv.norm, &n3) > 0);

        // using NULL
        res = res || !quat_ideal_small_equivalent_coprime(&gen, &equiv, &id, NULL, &PRNG_default_domain);
        // test odd
        res = res || !ibz_is_odd(&equiv.norm);
        // test generator
        quat_alg_conj(&gen, &gen);
        quat_to_lattice(&equiv_lat, &equiv);
        res = res || !quat_lattice_contains(NULL, &equiv_lat, &gen);
        quat_ideal_create_O0_inert_odd(&test, &gen, &equiv.norm);
        res = res || !quat_ideal_equal(&test, &equiv);
        // test equivalence
        res = res || !quat_ideals_equivalence(&id, &equiv);
        // test on bound
        res = res || (ibz_cmp(&equiv.norm, &n3) > 0);
    }

randomness_failure:;
    if (ret)
        printf("Randomness failure in quaternion unit test ideal_small_equivalent_coprime\n");

    if (res) {
        printf("Quaternion unit test ideal_small_equivalent_coprime failed\n");
    }
    return (res | ret);
}

// void quat_ideal_reduce_basis(quat_lattice_t *reduced, const quat_ideal_t *ideal);
// Tested in lll/test/lll_tests.c: the reducedness check needs quat_lll_verify and the ibq_t rationals.

// run all previous tests
int
quat_test_ideal(void)
{
    int res = 0;
    printf("\nRunning tests for quaternion ideal functions\n");
    res = res | quat_test_ideal_copy();
    res = res | quat_test_ideal_odd_inert_gen();
    res = res | quat_test_ideal_xyn_to_inert_ideal();
    res = res | quat_test_ideal_create_O0_inert_odd();
    res = res | quat_test_ideal_create_O0_pow_two();
    res = res | quat_test_ideal_create_O0_odd();
    res = res | quat_test_ideal_random_ideal_O0_given_prime_norm();
    res = res | quat_test_ideal_random_ideal_O0_given_arbitrary_odd_norm();
    res = res | quat_test_ideal_intersection();
    res = res | quat_test_ideal_mul_O0();
    res = res | quat_test_ideal_product_gram_matrix();
    res = res | quat_test_ideal_create_O0_inert();
    res = res | quat_test_ideal_shortest_equivalent();
    res = res | quat_test_ideal_small_equivalent_coprime_enumeration();
    res = res | quat_test_ideal_small_equivalent_coprime();
    return (res);
}
