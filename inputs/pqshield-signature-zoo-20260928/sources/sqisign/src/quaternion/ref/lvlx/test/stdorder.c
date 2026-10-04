#include "quaternion_tests.h"
#include <stdlib.h>
#include <assert.h>
#include <prng.h>

// helpers for setting parameters

// test if parameters are such that represent_inter is likely to find a solution
int
quat_test_input_for_repres_bound(const ibz_t *p, const ibz_t *M)
{
    ibz_t c, r;
    ibz_init(&c);
    ibz_init(&r);
    ibz_div(&c, &r, M, p);
    ibz_set(&r, 1 << 20, 22);
    int res = (ibz_cmp(&r, &c) <= 0);
    return (res);
}

// void quat_change_to_O0_basis(ibz_vec_4_t *vec, const quat_alg_elem_t *el);
int
quat_test_change_to_O0_basis()
{
    int res = 0;
    quat_alg_elem_t cmp, elem;
    ibz_vec_4_t out;
    quat_lattice_t O0;
    quat_alg_elem_init(&elem);
    quat_alg_elem_init(&cmp);
    ibz_vec_4_init(&out);
    quat_lattice_init(&O0);
    quat_lattice_O0_set(&O0);

    quat_alg_elem_set(&cmp, 2, 2, 7, 1, -4);
    quat_alg_elem_copy(&elem, &cmp);
    quat_change_to_O0_basis(&out, &elem);
    res = res || !quat_alg_elem_equal(&elem, &cmp);
    quat_alg_elem_set(&elem, 1, 0, 0, 0, 0);
    ibz_mat_4x4_eval(&(elem.coord), &(O0.basis), &out);
    ibz_copy(&(elem.denom), &(O0.denom));
    res = res || !quat_alg_elem_equal(&elem, &cmp);

    quat_alg_elem_set(&cmp, 2, 1, 0, 6, -3);
    quat_alg_elem_copy(&elem, &cmp);
    quat_change_to_O0_basis(&out, &elem);
    res = res || !quat_alg_elem_equal(&elem, &cmp);
    quat_alg_elem_set(&elem, 1, 0, 0, 0, 0);
    ibz_mat_4x4_eval(&(elem.coord), &(O0.basis), &out);
    ibz_copy(&(elem.denom), &(O0.denom));
    res = res || !quat_alg_elem_equal(&elem, &cmp);

    quat_alg_elem_set(&cmp, 1, -8, 2, 1, 3);
    quat_alg_elem_copy(&elem, &cmp);
    quat_change_to_O0_basis(&out, &elem);
    res = res || !quat_alg_elem_equal(&elem, &cmp);
    quat_alg_elem_set(&elem, 1, 0, 0, 0, 0);
    ibz_mat_4x4_eval(&(elem.coord), &(O0.basis), &out);
    ibz_copy(&(elem.denom), &(O0.denom));
    res = res || !quat_alg_elem_equal(&elem, &cmp);

    if (res) {
        printf("Quaternion unit test change_to_O0_basis failed");
    }
    return (res);
}

// void quat_mod_O0(quat_alg_elem_t *red, const quat_alg_elem_t *x, const ibz_t *mod)
int
quat_test_mod_O0()
{
    int res = 0;
    ibz_t mod, det, rst;
    ibz_mat_4x4_t inv;
    quat_alg_elem_t r, e, c;
    quat_lattice_t O0;
    ibz_vec_4_t cc, rc, ec;
    ibz_mat_4x4_init(&inv);
    ibz_init(&mod);
    ibz_init(&det);
    ibz_init(&rst);
    ibz_vec_4_init(&cc);
    ibz_vec_4_init(&ec);
    ibz_vec_4_init(&rc);
    quat_alg_elem_init(&r);
    quat_alg_elem_init(&e);
    quat_alg_elem_init(&c);
    quat_lattice_init(&O0);
    quat_lattice_O0_set(&O0);
    // O0_inverse and det
    ibz_mat_4x4_zero(&inv);
    ibz_set(&inv.m[0][0], 2, 3);
    ibz_set(&inv.m[1][1], 2, 3);
    ibz_set(&inv.m[0][3], -2, 3);
    ibz_set(&inv.m[1][2], -2, 3);
    ibz_set(&inv.m[2][2], 4, 4);
    ibz_set(&inv.m[3][3], 4, 4);
    ibz_set(&det, 4, 4);

    for (int i = 0; i < 10; i++) {
        ibz_rand_interval_bits(&mod, 20);
        ibz_abs(&mod, &mod);
        ibz_add(&mod, &mod, &ibz_const_two);
        for (int k = 0; k < 4; k++) {
            ibz_rand_interval_bits(&ec.v[k], 30);
            ibz_mod(&cc.v[k], &ec.v[k], &mod);
        }
        ibz_mat_4x4_eval(&e.coord, &O0.basis, &ec);
        ibz_mat_4x4_eval(&c.coord, &O0.basis, &cc);
        ibz_set(&e.denom, 2, 4);
        ibz_set(&c.denom, 2, 4);
        quat_mod_O0(&r, &e, &mod);
        res = res || !quat_alg_elem_equal(&r, &c);
        quat_mod_O0(&r, &c, &mod);
        res = res || !quat_alg_elem_equal(&r, &c);
        ibz_mat_4x4_eval(&rc, &inv, &r.coord);
        for (int k = 0; k < 4; k++) {
            ibz_div(&rc.v[k], &rst, &rc.v[k], &det);
            assert(ibz_is_zero(&rst));
            res = res || !(ibz_cmp(&ibz_const_zero, &rc.v[k]) <= 0);
            res = res || !(ibz_cmp(&rc.v[k], &mod) < 0);
        }

        quat_mod_O0(&e, &e, &mod);
        res = res || !quat_alg_elem_equal(&e, &c);
    }

    if (res != 0) {
        printf("Quaternion unit test new_mod_O0 failed\n");
    }

    return (res);
}

int
quat_test_represent_integer_internal()
{
    int bitsize = ibz_bitsize(&QUATALG_PINFTY.p) + 50;
    int tested = 0;
    int rand_ret = 0;
    int res = 0;
    ibz_t norm_n, M, norm_d;
    ibz_vec_4_t coord;
    quat_alg_elem_t gamma;
    quat_alg_elem_init(&gamma);
    ibz_vec_4_init(&coord);
    ibz_init(&M);
    ibz_init(&norm_d);
    ibz_init(&norm_n);

    // setup
    while (!tested) {
        rand_ret = rand_ret | !ibz_rand_interval_bits(&M, bitsize);
        tested = (ibz_get(&M) % 2 == 1);
        tested = tested && quat_test_input_for_repres_bound(&(QUATALG_PINFTY.p), &M);
        if (rand_ret)
            break;
    }

    if (!rand_ret) {
        res = !quat_represent_integer(&gamma, &M, &PRNG_default_domain);
        if (!res) {
            quat_alg_norm(&norm_n, &norm_d, &gamma, &QUATALG_PINFTY);
            res = res || !ibz_is_one(&norm_d);
            res = res || !(ibz_cmp(&norm_n, &M) == 0);
            res = res || !quat_lattice_contains(NULL, &MAXORD_O0, &gamma);
        }
    } else {
        printf("Randomness failure in quat_represent_integer test\n");
    }
    return (res | (rand_ret));
}

// int quat_represent_integer(quat_alg_elem_t *gamma, const ibz_t *n_gamma, const quat_represent_integer_params_t
// *params);
int
quat_test_represent_integer(void)
{
    int res = 0;

    for (int i = 0; i < 5; i++)
        res = res | quat_test_represent_integer_internal();

    if (res) {
        printf("Quaternion unit test represent_integer failed\n");
    }
    return (res);
}

int
quat_test_stdorder(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of functions for special extremal orders\n");

    res = res | quat_test_mod_O0();
    res = res | quat_test_change_to_O0_basis();
    res = res | quat_test_represent_integer();

    return (res);
}
