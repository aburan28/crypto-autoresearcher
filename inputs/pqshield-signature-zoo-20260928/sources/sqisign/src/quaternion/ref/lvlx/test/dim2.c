#include "quaternion_tests.h"
#include <rng.h>
#include <quaternion_constants.h>

// void ibz_vec_2_set(ibz_vec_2_t *vec, int a0, int a1);
int
quat_test_dim2_ibz_vec_2_set(void)
{
    int res = 0;
    ibz_vec_2_t vec;
    ibz_vec_2_init(&vec);
    ibz_vec_2_set(&vec, 2, 5);
    res = res || (ibz_cmp_int32(&(vec.v[0]), 2) != 0);
    res = res || (ibz_cmp_int32(&(vec.v[1]), 5) != 0);
    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_vec_2_set failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_set(ibz_mat_2x2_t *mat, int a00, int a01, int a10, int a11);
int
quat_test_dim2_ibz_mat_2x2_set(void)
{
    int res = 0;
    ibz_mat_2x2_t mat;
    ibz_mat_2x2_init(&mat);
    ibz_mat_2x2_set(&mat, 2, 7, -1, 5);
    res = res || (ibz_cmp_int32(&(mat.m[0][0]), 2) != 0);
    res = res || (ibz_cmp_int32(&(mat.m[0][1]), 7) != 0);
    res = res || (ibz_cmp_int32(&(mat.m[1][0]), -1) != 0);
    res = res || (ibz_cmp_int32(&(mat.m[1][1]), 5) != 0);
    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_set failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_copy(ibz_vec_2_t *copy, const ibz_mat_2x2_t *copied);
int
quat_test_dim2_ibz_mat_2x2_copy(void)
{
    int res = 0;
    ibz_mat_2x2_t mat, copy;
    ibz_mat_2x2_init(&mat);
    ibz_mat_2x2_init(&copy);

    ibz_mat_2x2_set(&mat, 1, -1, 2, 4);
    ibz_mat_2x2_set(&copy, 0, -0, 0, 0);
    res = res || (0 == ibz_cmp_int32(&(copy.m[0][0]), 1));
    res = res || (0 == ibz_cmp_int32(&(copy.m[0][1]), -1));
    res = res || (0 == ibz_cmp_int32(&(copy.m[1][0]), 2));
    res = res || (0 == ibz_cmp_int32(&(copy.m[1][1]), 4));
    res = res || (0 != ibz_cmp_int32(&(mat.m[0][0]), 1));
    res = res || (0 != ibz_cmp_int32(&(mat.m[0][1]), -1));
    res = res || (0 != ibz_cmp_int32(&(mat.m[1][0]), 2));
    res = res || (0 != ibz_cmp_int32(&(mat.m[1][1]), 4));
    ibz_mat_2x2_copy(&copy, &mat);
    res = res || (0 != ibz_cmp_int32(&(copy.m[0][0]), 1));
    res = res || (0 != ibz_cmp_int32(&(copy.m[0][1]), -1));
    res = res || (0 != ibz_cmp_int32(&(copy.m[1][0]), 2));
    res = res || (0 != ibz_cmp_int32(&(copy.m[1][1]), 4));
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            res = res || (0 != ibz_cmp(&(mat.m[i][j]), &(copy.m[i][j])));
        }
    }

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_copy failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_det_from_ibz(ibz_t *det, const ibz_t *a11, const ibz_t *a12, const ibz_t *a21, const ibz_t *a22);
int
quat_test_dim2_ibz_mat_2x2_det_from_ibz(void)
{
    int res = 0;
    ibz_t det, cmp, a11, a12, a21, a22;
    ibz_init(&a11);
    ibz_init(&a12);
    ibz_init(&a21);
    ibz_init(&a22);
    ibz_init(&det);
    ibz_init(&cmp);

    ibz_set(&a11, 1, 2);
    ibz_set(&a12, 0, 0);
    ibz_set(&a21, 0, 0);
    ibz_set(&a22, 1, 2);
    ibz_set(&cmp, 1, 2);
    ibz_mat_2x2_det_from_ibz(&det, &a11, &a12, &a21, &a22);
    res = res || ibz_cmp(&cmp, &det);

    ibz_set(&a11, 2, 3);
    ibz_set(&a12, 3, 3);
    ibz_set(&a21, 1, 2);
    ibz_set(&a22, -2, 3);
    ibz_set(&cmp, -7, 4);
    ibz_mat_2x2_det_from_ibz(&det, &a11, &a12, &a21, &a22);
    res = res || ibz_cmp(&cmp, &det);

    ibz_set(&a11, 0, 0);
    ibz_set(&a12, 3, 3);
    ibz_set(&a21, -1, 2);
    ibz_set(&a22, 0, 0);
    ibz_set(&cmp, 3, 3);
    ibz_mat_2x2_det_from_ibz(&det, &a11, &a12, &a21, &a22);
    res = res || ibz_cmp(&cmp, &det);

    ibz_set(&a11, 2, 3);
    ibz_set(&cmp, 0, 0);
    ibz_mat_2x2_det_from_ibz(&a11, &a11, &a11, &a11, &a11);
    res = res || ibz_cmp(&cmp, &a11);

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_det_from_ibz failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_eval(ibz_vec_2_t *res, const ibz_mat_2x2_t *mat, const ibz_vec_2_t *vec);
int
quat_test_dim2_ibz_mat_2x2_eval(void)
{
    int res = 0;
    ibz_vec_2_t vec, ret, cmp;
    ibz_mat_2x2_t mat;
    ibz_vec_2_init(&vec);
    ibz_mat_2x2_init(&mat);
    ibz_vec_2_init(&ret);
    ibz_vec_2_init(&cmp);

    ibz_mat_2x2_set(&mat, 1, -1, 2, 4);
    ibz_vec_2_set(&vec, 1, -1);
    ibz_vec_2_set(&cmp, 2, -2);
    ibz_mat_2x2_eval(&ret, &mat, &vec);
    res = res || ibz_cmp(&(ret.v[0]), &(cmp.v[0]));
    res = res || ibz_cmp(&(ret.v[1]), &(cmp.v[1]));

    ibz_mat_2x2_set(&mat, 2, -2, 1, 3);
    ibz_vec_2_set(&vec, 2, 4);
    ibz_vec_2_set(&cmp, -4, 14);
    ibz_mat_2x2_eval(&vec, &mat, &vec);
    res = res || ibz_cmp(&(vec.v[0]), &(cmp.v[0]));
    res = res || ibz_cmp(&(vec.v[1]), &(cmp.v[1]));

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_eval failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_mul(ibz_mat_2x2_t *prod, const ibz_mat_2x2_t *mat_a, const ibz_mat_2x2_t *mat_b);
int
quat_test_dim2_ibz_mat_2x2_mul(void)
{
    int res = 0;
    ibz_mat_2x2_t a, b, cmp, prod;
    ibz_mat_2x2_init(&a);
    ibz_mat_2x2_init(&b);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&cmp);

    ibz_mat_2x2_set(&a, 2, -2, 1, 3);
    ibz_mat_2x2_set(&b, 5, 3, 4, 1);
    ibz_mat_2x2_set(&cmp, 2, 4, 17, 6);
    ibz_mat_2x2_mul(&prod, &a, &b);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));
    ibz_mat_2x2_set(&cmp, 13, -1, 9, -5);
    ibz_mat_2x2_mul(&prod, &b, &a);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));

    ibz_mat_2x2_set(&a, 2, 7, 1, -2);
    ibz_mat_2x2_set(&cmp, 11, 0, 0, 11);
    ibz_mat_2x2_mul(&a, &a, &a);
    res = res || ibz_cmp(&(a.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(a.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(a.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(a.m[1][1]), &(cmp.m[1][1]));

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_mul failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_scalar_mul(ibz_mat_2x2_t *prod, const ibz_t *scalar, const ibz_mat_2x2_t *mat);
int
quat_test_dim2_ibz_mat_2x2_scalar_mul(void)
{
    int res = 0;
    ibz_mat_2x2_t a, cmp, prod;
    ibz_t s;
    ibz_mat_2x2_init(&a);
    ibz_init(&s);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&cmp);

    ibz_mat_2x2_set(&a, 2, -2, 1, 3);
    ibz_set(&s, 6, 4);
    ibz_mat_2x2_set(&cmp, 12, -12, 6, 18);
    ibz_mat_2x2_scalar_mul(&prod, &s, &a);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));
    ibz_mat_2x2_set(&cmp, -4, 4, -2, -6);
    ibz_mat_2x2_scalar_mul(&prod, &a.m[0][1], &a);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));

    ibz_mat_2x2_set(&a, 2, 7, 1, -2);
    ibz_mat_2x2_set(&cmp, 4, 14, 2, -4);
    ibz_mat_2x2_scalar_mul(&a, &a.m[0][0], &a);
    res = res || ibz_cmp(&(a.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(a.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(a.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(a.m[1][1]), &(cmp.m[1][1]));

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_scalar_mul failed\n");
    }
    return (res);
}

// int ibz_mat_2x2_inv_with_det_as_denom(ibz_mat_2x2_t *inv, const ibz_t *det, const ibz_mat_2x2_t *mat);
int
quat_test_dim2_ibz_mat_2x2_inv_with_det_as_denom(void)
{
    int res = 0;
    ibz_t m;
    ibz_mat_2x2_t a, inv, id, prod;
    ibz_init(&m);
    ibz_mat_2x2_init(&a);
    ibz_mat_2x2_init(&inv);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&id);
    ibz_mat_2x2_set(&id, 1, 0, 0, 1);

    // inverse exists
    ibz_mat_2x2_set(&a, 2, -3, 1, 3);
    if (ibz_mat_2x2_inv_with_det_as_denom(&inv, &m, &a)) {
        ibz_mat_2x2_mul(&prod, &inv, &a);
        res = res || ibz_cmp(&(prod.m[0][0]), &m);
        res = res || ibz_cmp(&(prod.m[0][1]), &ibz_const_zero);
        res = res || ibz_cmp(&(prod.m[1][0]), &ibz_const_zero);
        res = res || ibz_cmp(&(prod.m[1][1]), &m);
    } else {
        res = 1;
    }
    ibz_set(&m, 12, 5);
    ibz_mat_2x2_set(&a, 2, 7, 1, -2);
    ibz_mat_2x2_set(&inv, 2, 7, 1, -2);
    if (ibz_mat_2x2_inv_with_det_as_denom(&inv, &m, &inv)) {
        ibz_mat_2x2_mul(&prod, &a, &inv);
        res = res || ibz_cmp(&(prod.m[0][0]), &m);
        res = res || ibz_cmp(&(prod.m[0][1]), &ibz_const_zero);
        res = res || ibz_cmp(&(prod.m[1][0]), &ibz_const_zero);
        res = res || ibz_cmp(&(prod.m[1][1]), &m);
    } else {
        res = 1;
    }

    // no inverse
    ibz_set(&m, 25, 6);
    ibz_mat_2x2_set(&a, 2, -2, -1, 1);
    res = res || ibz_mat_2x2_inv_with_det_as_denom(NULL, &m, &a);
    res = res || ibz_mat_2x2_inv_with_det_as_denom(&prod, &m, &a);
    res = res || ibz_mat_2x2_inv_with_det_as_denom(&prod, NULL, &a);
    res = res || ibz_mat_2x2_inv_with_det_as_denom(NULL, NULL, &a);

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_inv_with_det_as_denom failed\n");
    }
    return (res);
}

// modular 2x2 operations

// void ibz_mat_2x2_mul_mod(ibz_mat_2x2_t *prod, const ibz_mat_2x2_t *mat_a, const ibz_mat_2x2_t *mat_b,
// const ibz_t *m);
int
quat_test_dim2_ibz_mat_2x2_mul_mod(void)
{
    int res = 0;
    ibz_t m;
    ibz_mat_2x2_t a, b, cmp, prod;
    ibz_init(&m);
    ibz_mat_2x2_init(&a);
    ibz_mat_2x2_init(&b);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&cmp);

    ibz_set(&m, 7, 4);
    ibz_mat_2x2_set(&a, 2, -2, 1, 3);
    ibz_mat_2x2_set(&b, 5, 3, 4, 1);
    ibz_mat_2x2_set(&cmp, 2, 4, 3, 6);
    ibz_mat_2x2_mul_mod(&prod, &a, &b, &m);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));
    ibz_mat_2x2_set(&cmp, 6, 6, 2, 2);
    ibz_mat_2x2_mul_mod(&prod, &b, &a, &m);
    res = res || ibz_cmp(&(prod.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(prod.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(prod.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(prod.m[1][1]), &(cmp.m[1][1]));

    ibz_set(&m, 12, 5);
    ibz_mat_2x2_set(&a, 2, 7, 1, -2);
    ibz_mat_2x2_set(&cmp, 11, 0, 0, 11);
    ibz_mat_2x2_mul_mod(&a, &a, &a, &m);
    res = res || ibz_cmp(&(a.m[0][0]), &(cmp.m[0][0]));
    res = res || ibz_cmp(&(a.m[0][1]), &(cmp.m[0][1]));
    res = res || ibz_cmp(&(a.m[1][0]), &(cmp.m[1][0]));
    res = res || ibz_cmp(&(a.m[1][1]), &(cmp.m[1][1]));

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_mul_mod failed\n");
    }
    return (res);
}

// int ibz_mat_2x2_inv_mod(ibz_mat_2x2_t *inv, const ibz_mat_2x2_t *mat, const ibz_t *m);
int
quat_test_dim2_ibz_mat_2x2_inv_mod(void)
{
    int res = 0;
    ibz_t m;
    ibz_mat_2x2_t a, inv, id, prod;
    ibz_init(&m);
    ibz_mat_2x2_init(&a);
    ibz_mat_2x2_init(&inv);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&id);
    ibz_mat_2x2_set(&id, 1, 0, 0, 1);

    // inverse exists
    ibz_set(&m, 7, 4);
    ibz_mat_2x2_set(&a, 2, -3, 1, 3);
    if (ibz_mat_2x2_inv_mod(&inv, &a, &m)) {
        // ibz_mat_2x2_mul_mod(&prod,&a,&inv, &m);
        ibz_mat_2x2_mul_mod(&prod, &inv, &a, &m);
        res = res || ibz_cmp(&(prod.m[0][0]), &(id.m[0][0]));
        res = res || ibz_cmp(&(prod.m[0][1]), &(id.m[0][1]));
        res = res || ibz_cmp(&(prod.m[1][0]), &(id.m[1][0]));
        res = res || ibz_cmp(&(prod.m[1][1]), &(id.m[1][1]));
    } else {
        res = 1;
    }
    ibz_set(&m, 12, 5);
    ibz_mat_2x2_set(&a, 2, 7, 1, -2);
    ibz_mat_2x2_set(&inv, 2, 7, 1, -2);
    if (ibz_mat_2x2_inv_mod(&inv, &inv, &m)) {
        ibz_mat_2x2_mul_mod(&prod, &a, &inv, &m);
        res = res || ibz_cmp(&(prod.m[0][0]), &(id.m[0][0]));
        res = res || ibz_cmp(&(prod.m[0][1]), &(id.m[0][1]));
        res = res || ibz_cmp(&(prod.m[1][0]), &(id.m[1][0]));
        res = res || ibz_cmp(&(prod.m[1][1]), &(id.m[1][1]));
    } else {
        res = 1;
    }

    // no inverse
    ibz_set(&m, 25, 6);
    ibz_mat_2x2_set(&a, 2, -2, -1, 1);
    res = res || ibz_mat_2x2_inv_mod(&inv, &a, &m);
    ibz_set(&m, 7, 4);
    ibz_mat_2x2_set(&a, 2, 3, 1, -2);
    res = res || ibz_mat_2x2_inv_mod(&inv, &a, &m);
    ibz_set(&m, 25, 6);
    ibz_mat_2x2_set(&a, 2, 1, 1, -2);
    res = res || ibz_mat_2x2_inv_mod(&inv, &a, &m);

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_inv_mod failed\n");
    }
    return (res);
}

// int ibz_mat_2x2_inv_mod(ibz_mat_2x2_t *inv, const ibz_mat_2x2_t *mat, const ibz_t *m);
int
quat_test_dim2_ibz_mat_2x2_inv_mod_randomized(int bitsize_matrix, int bitsize_modulus, int iterations)
{
    int randret = 0;
    int res = 0;
    ibz_t m, det, gcd;
    ibz_mat_2x2_t a, inv, id, prod;
    ibz_init(&m);
    ibz_init(&det);
    ibz_init(&gcd);
    ibz_mat_2x2_init(&a);
    ibz_mat_2x2_init(&inv);
    ibz_mat_2x2_init(&prod);
    ibz_mat_2x2_init(&id);
    ibz_mat_2x2_set(&id, 1, 0, 0, 1);

    for (int iter = 0; iter < iterations; iter++) {
        // generate random matrix and modulo, with modulo larger than 2
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                randret = randret | !ibz_rand_interval_bits(&(a.m[i][j]), bitsize_matrix);
            }
        }
        randret = randret | !ibz_rand_interval_bits(&m, bitsize_modulus);
        ibz_abs(&m, &m);
        ibz_add(&m, &m, &ibz_const_two);
        if (randret != 0) {
            printf("Randomness failed in quaternion unit test with randomization for "
                   "ibz_mat_2x2_inv_mod\n");
            return (res);
        }

        // compute det
        ibz_mat_2x2_det_from_ibz(&det, &(a.m[0][0]), &(a.m[0][1]), &(a.m[1][0]), &(a.m[1][1]));
        // is it prime to mod
        ibz_gcd(&gcd, &det, &m);
        if (ibz_is_one(&gcd)) {
            // matrix should be invertible mod m
            if (ibz_mat_2x2_inv_mod(&inv, &a, &m)) {
                ibz_mat_2x2_mul_mod(&prod, &inv, &a, &m);
                res = res || ibz_cmp(&(prod.m[0][0]), &(id.m[0][0]));
                res = res || ibz_cmp(&(prod.m[0][1]), &(id.m[0][1]));
                res = res || ibz_cmp(&(prod.m[1][0]), &(id.m[1][0]));
                res = res || ibz_cmp(&(prod.m[1][1]), &(id.m[1][1]));
            } else {
                res = 1;
            }
        } else {
            res = res || ibz_mat_2x2_inv_mod(&inv, &a, &m);
        }
    }

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_inv_mod_randomized failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_normalize(ibz_mat_2x2_t *mat, int e);
int
quat_test_dim2_ibz_mat_2x2_normalize(int iterations)
{
    int res = 0;
    ibz_mat_2x2_t mat;
    ibz_t mid, bound, tmp;
    ibz_init(&mid);
    ibz_init(&bound);
    ibz_init(&tmp);
    ibz_mat_2x2_init(&mat);
    int bound_bits = QUAT_qlapoty_used_power_of_two;

    ibz_mul_2exp(&mid, &ibz_const_one, bound_bits - 1);
    ibz_mul_2exp(&bound, &mid, 1);
    for (int iter = 0; iter < iterations; iter++) {
        for (int i = 0; i < 2; ++i) {
            for (int j = 0; j < 2; ++j) {
                ibz_rand_interval(&mat.m[i][j], &ibz_const_zero, &bound);
            }
        }
        ibz_mat_2x2_normalize(&mat, bound_bits);
        for (int i = 0; i < 2; ++i) {
            for (int j = 0; j < 2; ++j) {
                res = res || (!ibz_is_positive(&tmp) || ibz_cmp(&tmp, &bound) >= 0);

                int r = ibz_cmp(&tmp, &mid);
                if (r > 0)
                    return (0);
                res = res || (r < 0 && !ibz_is_zero(&tmp));
            }
        }
    }

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_mat_2x2_normalize failed\n");
    }
    return (res);
}

// void ibz_vec_2_copy(ibz_vec_2_t *copy, const ibz_vec_2_t *copied)
int
quat_test_dim2_ibz_vec_2_copy()
{
    int res = 0;
    ibz_vec_2_t a, b, c;
    ibz_vec_2_init(&a);
    ibz_vec_2_init(&b);
    ibz_vec_2_init(&c);
    ibz_set(&a.v[0], 1, 2);
    ibz_set(&a.v[1], 2, 3);
    ibz_set(&b.v[0], 21, 7);
    ibz_set(&b.v[1], 23, 7);
    ibz_set(&c.v[0], 21, 7);
    ibz_set(&c.v[1], 23, 7);
    res = res || (ibz_cmp(&a.v[0], &c.v[0]) == 0);
    res = res || (ibz_cmp(&a.v[1], &c.v[1]) == 0);
    ibz_vec_2_copy(&a, &b);
    res = res || !(ibz_cmp(&a.v[0], &c.v[0]) == 0);
    res = res || !(ibz_cmp(&a.v[1], &c.v[1]) == 0);
    res = res || !(ibz_cmp(&b.v[0], &c.v[0]) == 0);
    res = res || !(ibz_cmp(&b.v[1], &c.v[1]) == 0);
    if (res) {
        printf("Quaternion unit test dim2_ibz_vec_2_copy failed\n");
    }
    return (res);
}

// void ibz_vec_2_gaussian_mul(ibz_vec_2_t *prod, const ibz_vec_2_t *a, const ibz_vec_2_t *b);
int
quat_test_dim2_ibz_vec_2_gaussian_mul()
{
    int res = 0;
    ibz_vec_2_t a, b, g, c;
    ibz_t tmp, sum;
    ibz_vec_2_init(&a);
    ibz_vec_2_init(&b);
    ibz_vec_2_init(&g);
    ibz_vec_2_init(&c);
    ibz_init(&sum);
    ibz_init(&tmp);
    for (int i = 0; i < 10; i++) {
        ibz_rand_interval_bits(&a.v[0], 10);
        ibz_rand_interval_bits(&b.v[0], 10);
        ibz_rand_interval_bits(&a.v[1], 10);
        ibz_rand_interval_bits(&b.v[1], 10);
        ibz_vec_2_gaussian_mul(&g, &a, &b);
        ibz_mul(&tmp, &a.v[0], &b.v[0]);
        ibz_mul(&sum, &a.v[1], &b.v[1]);
        ibz_sub(&sum, &tmp, &sum);
        ibz_mul(&tmp, &a.v[0], &b.v[1]);
        ibz_mul(&c.v[1], &a.v[1], &b.v[0]);
        ibz_add(&c.v[1], &tmp, &c.v[1]);
        ibz_copy(&c.v[0], &sum);
        res = res || !(ibz_cmp(&c.v[0], &g.v[0]) == 0);
        res = res || !(ibz_cmp(&c.v[1], &g.v[1]) == 0);
    }
    if (res) {
        printf("Quaternion unit test dim2_ibz_vec_2_gaussian_mul failed\n");
    }
    return (res);
}

// helper for gaussian gcd test
int
quat_test_dim2_ibz_vec_2_check_gaussian_gcd(const ibz_vec_2_t *a, const ibz_vec_2_t *b)
{
    int res = 0;
    ibz_vec_2_t g, qa, ra, qb, rb, u;
    ibz_t n;
    ibz_vec_2_init(&g);
    ibz_vec_2_init(&qa);
    ibz_vec_2_init(&ra);
    ibz_vec_2_init(&qb);
    ibz_vec_2_init(&rb);
    ibz_vec_2_init(&u);
    ibz_init(&n);

    ibz_vec_2_gaussian_gcd(&g, a, b);

    res = res || ibz_vec_2_is_zero(&g);
    if (res)
        return (res);

    // gcd divides both
    ibz_vec_2_gaussian_euclidean_division(&qa, &ra, a, &g);
    ibz_vec_2_gaussian_euclidean_division(&qb, &rb, b, &g);
    res = res || (!ibz_vec_2_is_zero(&ra) || !ibz_vec_2_is_zero(&rb));
    if (res)
        return (res);

    // here gcd(a/g, b/g) is unit
    ibz_vec_2_gaussian_gcd(&u, &qa, &qb);
    ibz_sum_two_squares(&n, &u.v[0], &u.v[1]);
    res = res || (!ibz_is_one(&n));

    return (res);
}

// void quat_gaussian_gcd(ibz_vec_2_t *gcd, const ibz_vec_2_t *a, const ibz_vec_2_t *b);
int
quat_test_dim2_ibz_vec_2_gaussian_gcd()
{
    int res = 0;
    ibz_vec_2_t a, b, g, x, y, ax, by, gg;
    ibz_t na, ng, nprod, ngg;
    ibz_vec_2_init(&a);
    ibz_vec_2_init(&b);
    ibz_vec_2_init(&g);
    ibz_vec_2_init(&x);
    ibz_vec_2_init(&y);
    ibz_vec_2_init(&ax);
    ibz_vec_2_init(&by);
    ibz_vec_2_init(&gg);
    ibz_init(&na);
    ibz_init(&ng);
    ibz_init(&nprod);
    ibz_init(&ngg);

    for (int i = 0; i < 20; i++) {
        do {
            ibz_rand_interval_bits(&a.v[0], 10);
            ibz_rand_interval_bits(&b.v[0], 10);
            ibz_rand_interval_bits(&a.v[1], 10);
            ibz_rand_interval_bits(&b.v[1], 10);
        } while (ibz_vec_2_is_zero(&a) && ibz_vec_2_is_zero(&b));
        res = res || quat_test_dim2_ibz_vec_2_check_gaussian_gcd(&a, &b);

        // gcd(a, 0)
        ibz_set(&b.v[0], 0, 0);
        ibz_set(&b.v[1], 0, 0);
        if (!ibz_vec_2_is_zero(&a)) {
            ibz_vec_2_gaussian_gcd(&g, &a, &b);
            ibz_sum_two_squares(&na, &a.v[0], &a.v[1]);
            ibz_sum_two_squares(&ng, &g.v[0], &g.v[1]);
            res = res || (ibz_cmp(&na, &ng) != 0);
            // gcd(a, a)
            ibz_vec_2_gaussian_gcd(&g, &a, &a);
            ibz_sum_two_squares(&ng, &g.v[0], &g.v[1]);
            res = res || (ibz_cmp(&na, &ng) != 0);
        }

        // N(gcd(gx, gy)) = N(g) N(gcd(x, y))
        do {
            ibz_rand_interval_bits(&g.v[0], 6);
            ibz_rand_interval_bits(&g.v[1], 6);
        } while (ibz_vec_2_is_zero(&g));
        do {
            ibz_rand_interval_bits(&x.v[0], 6);
            ibz_rand_interval_bits(&x.v[1], 6);
            ibz_rand_interval_bits(&y.v[0], 6);
            ibz_rand_interval_bits(&y.v[1], 6);
        } while (ibz_vec_2_is_zero(&x) || ibz_vec_2_is_zero(&y));
        ibz_vec_2_gaussian_mul(&ax, &g, &x);
        ibz_vec_2_gaussian_mul(&by, &g, &y);
        ibz_vec_2_gaussian_gcd(&gg, &ax, &by);
        ibz_sum_two_squares(&ngg, &gg.v[0], &gg.v[1]);
        ibz_vec_2_gaussian_gcd(&a, &x, &y);
        ibz_sum_two_squares(&na, &a.v[0], &a.v[1]);
        ibz_sum_two_squares(&ng, &g.v[0], &g.v[1]);
        ibz_mul(&nprod, &ng, &na);
        if (ibz_cmp(&ngg, &nprod) != 0) {
            res = 1;
        }
        res = res || quat_test_dim2_ibz_vec_2_check_gaussian_gcd(&ax, &by);
    }

    ibz_set(&a.v[0], 12, 16);
    ibz_set(&a.v[1], 18, 16);
    ibz_set(&b.v[0], 30, 16);
    ibz_set(&b.v[1], 6, 16);
    ibz_vec_2_gaussian_gcd(&g, &a, &b);
    ibz_sum_two_squares(&ng, &g.v[0], &g.v[1]);
    ibz_vec_2_gaussian_gcd(&a, &a, &b);
    ibz_sum_two_squares(&na, &a.v[0], &a.v[1]);
    if (ibz_cmp(&ng, &na) != 0) {
        res = 1;
    }

    if (res != 0) {
        printf("Quaternion unit test dim2_ibz_vec_2_gaussian_gcd failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_dim2(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of functions for matrices, vectors and lattices in "
           "dimension 2\n");
    res = res | quat_test_dim2_ibz_vec_2_set();
    res = res | quat_test_dim2_ibz_mat_2x2_set();
    res = res | quat_test_dim2_ibz_mat_2x2_copy();
    res = res | quat_test_dim2_ibz_mat_2x2_det_from_ibz();
    res = res | quat_test_dim2_ibz_mat_2x2_eval();
    res = res | quat_test_dim2_ibz_mat_2x2_mul();
    res = res | quat_test_dim2_ibz_mat_2x2_scalar_mul();
    res = res | quat_test_dim2_ibz_mat_2x2_inv_with_det_as_denom();
    res = res | quat_test_dim2_ibz_mat_2x2_mul_mod();
    res = res | quat_test_dim2_ibz_mat_2x2_inv_mod();
    res = res | quat_test_dim2_ibz_mat_2x2_inv_mod_randomized(370, 270, 100);
    res = res | quat_test_dim2_ibz_mat_2x2_normalize(100);
    res = res | quat_test_dim2_ibz_vec_2_copy();
    res = res | quat_test_dim2_ibz_vec_2_gaussian_mul();
    res = res | quat_test_dim2_ibz_vec_2_gaussian_gcd();
    return (res);
}
