#include "quaternion_tests.h"
#include <rng.h>

// helper functions for lattices
// void ibz_vec_4_set(ibz_vec_4_t *vec, int32_t coord0, int32_t coord1, int32_t coord2, int32_t coord3)
int
quat_test_dim4_ibz_vec_4_set(void)
{
    int res = 0;
    ibz_vec_4_t a;
    ibz_vec_4_init(&a);
    ibz_vec_4_set(&a, 1, 2, 3, 4);
    res = res || !(ibz_cmp_int32(&(a.v[0]), 1) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[1]), 2) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[2]), 3) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[3]), 4) == 0);
    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_set failed\n");
    }
    return (res);
}

// void ibz_vec_4_copy(ibz_vec_4_t *new, const ibz_vec_4_t  *vec);
int
quat_test_dim4_ibz_vec_4_copy(void)
{
    int res = 0;
    ibz_vec_4_t a, b;
    ibz_vec_4_init(&a);
    ibz_vec_4_init(&b);
    ibz_vec_4_set(&a, 1, 2, 3, 4);
    ibz_vec_4_copy(&b, &a);
    res = res || !(ibz_cmp_int32(&(b.v[0]), 1) == 0);
    res = res || !(ibz_cmp_int32(&(b.v[1]), 2) == 0);
    res = res || !(ibz_cmp_int32(&(b.v[2]), 3) == 0);
    res = res || !(ibz_cmp_int32(&(b.v[3]), 4) == 0);
    ibz_vec_4_copy(&a, &a);
    res = res || !(ibz_cmp_int32(&(a.v[0]), 1) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[1]), 2) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[2]), 3) == 0);
    res = res || !(ibz_cmp_int32(&(a.v[3]), 4) == 0);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_copy failed\n");
    }
    return (res);
}

// void ibz_vec_4_copy_ibz(ibz_vec_4_t *coord, const ibz_t *coord0,const ibz_t *coord1,const ibz_t
// *coord2,const ibz_t *coord3){
int
quat_test_dim4_vec_4_copy_ibz(void)
{
    int res = 0;
    ibz_t a, b, c, d;
    ibz_vec_4_t coord;
    ibz_vec_4_init(&coord);
    ibz_init(&a);
    ibz_init(&b);
    ibz_init(&c);
    ibz_init(&d);
    ibz_set(&a, 1, 2);
    ibz_set(&b, 2, 3);
    ibz_set(&c, 3, 3);
    ibz_set(&d, 4, 4);
    ibz_vec_4_copy_ibz(&coord, &a, &b, &c, &d);
    res = res || ibz_cmp(&(coord.v[0]), &a);
    res = res || ibz_cmp(&(coord.v[1]), &b);
    res = res || ibz_cmp(&(coord.v[2]), &c);
    res = res || ibz_cmp(&(coord.v[3]), &d);

    if (res != 0) {
        printf("Quaternion unit test dim4_vec_4_copy_ibz failed\n");
    }
    return (res);
}

// void ibz_vec_4_add(ibz_vec_4_t *res, const ibz_vec_4_t *a, const ibz_vec_4_t *b);
int
quat_test_dim4_ibz_vec_4_add(void)
{
    int res = 0;
    ibz_vec_4_t a, b, c, cmp;
    ibz_vec_4_init(&a);
    ibz_vec_4_init(&b);
    ibz_vec_4_init(&c);
    ibz_vec_4_init(&cmp);

    ibz_set(&(a.v[0]), 1, 2);
    ibz_set(&(a.v[1]), -2, 3);
    ibz_set(&(a.v[2]), 7, 4);
    ibz_set(&(a.v[3]), 199, 9);
    ibz_set(&(b.v[0]), -6, 4);
    ibz_set(&(b.v[1]), 2, 3);
    ibz_set(&(b.v[2]), 67, 8);
    ibz_set(&(b.v[3]), -22, 6);
    ibz_set(&(cmp.v[0]), -5, 4);
    ibz_set(&(cmp.v[1]), 0, 0);
    ibz_set(&(cmp.v[2]), 74, 8);
    ibz_set(&(cmp.v[3]), 177, 9);
    ibz_vec_4_add(&c, &a, &b);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }

    ibz_set(&(a.v[0]), -122, 8);
    ibz_set(&(a.v[1]), 0, 0);
    ibz_set(&(a.v[2]), -7, 4);
    ibz_set(&(a.v[3]), 1889, 14);
    ibz_set(&(b.v[0]), -6, 4);
    ibz_set(&(b.v[1]), 2, 3);
    ibz_set(&(b.v[2]), 67, 8);
    ibz_set(&(b.v[3]), -1889, 14);
    ibz_set(&(cmp.v[0]), -128, 9);
    ibz_set(&(cmp.v[1]), 2, 3);
    ibz_set(&(cmp.v[2]), 60, 8);
    ibz_set(&(cmp.v[3]), 0, 0);
    ibz_vec_4_add(&c, &a, &b);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }

    ibz_set(&(a.v[0]), -1, 2);
    ibz_set(&(a.v[1]), 2, 3);
    ibz_set(&(a.v[2]), -7, 4);
    ibz_set(&(a.v[3]), 19, 6);
    ibz_set(&(cmp.v[0]), -2, 3);
    ibz_set(&(cmp.v[1]), 4, 4);
    ibz_set(&(cmp.v[2]), -14, 5);
    ibz_set(&(cmp.v[3]), 38, 7);
    ibz_vec_4_add(&a, &a, &a);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(a.v[i]), &(cmp.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_add failed\n");
    }
    return (res);
}

// void ibz_vec_4_sub(ibz_vec_4_t *res, const ibz_vec_4_t *a, const ibz_vec_4_t *b);
int
quat_test_dim4_ibz_vec_4_sub(void)
{
    int res = 0;
    ibz_vec_4_t a, b, c, cmp;
    ibz_vec_4_init(&a);
    ibz_vec_4_init(&b);
    ibz_vec_4_init(&c);
    ibz_vec_4_init(&cmp);

    ibz_set(&(a.v[0]), 1, 2);
    ibz_set(&(a.v[1]), -2, 3);
    ibz_set(&(a.v[2]), 7, 4);
    ibz_set(&(a.v[3]), 199, 9);
    ibz_set(&(b.v[0]), -6, 4);
    ibz_set(&(b.v[1]), 2, 3);
    ibz_set(&(b.v[2]), 67, 8);
    ibz_set(&(b.v[3]), -22, 6);
    ibz_set(&(cmp.v[0]), 7, 4);
    ibz_set(&(cmp.v[1]), -4, 4);
    ibz_set(&(cmp.v[2]), -60, 8);
    ibz_set(&(cmp.v[3]), 221, 9);
    ibz_vec_4_sub(&c, &a, &b);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }

    ibz_set(&(a.v[0]), -122, 8);
    ibz_set(&(a.v[1]), 0, 0);
    ibz_set(&(a.v[2]), -7, 4);
    ibz_set(&(a.v[3]), 1889, 14);
    ibz_set(&(b.v[0]), -6, 4);
    ibz_set(&(b.v[1]), 2, 3);
    ibz_set(&(b.v[2]), 67, 8);
    ibz_set(&(b.v[3]), -1889, 14);
    ibz_set(&(cmp.v[0]), -116, 8);
    ibz_set(&(cmp.v[1]), -2, 3);
    ibz_set(&(cmp.v[2]), -74, 8);
    ibz_set(&(cmp.v[3]), 3778, 15);
    ibz_vec_4_sub(&c, &a, &b);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }

    ibz_set(&(a.v[0]), -1, 2);
    ibz_set(&(a.v[1]), 2, 3);
    ibz_set(&(a.v[2]), -7, 4);
    ibz_set(&(a.v[3]), 19, 6);
    ;
    ibz_set(&(cmp.v[0]), 0, 0);
    ibz_set(&(cmp.v[1]), 0, 0);
    ibz_set(&(cmp.v[2]), 0, 0);
    ibz_set(&(cmp.v[3]), 0, 0);
    ibz_vec_4_sub(&a, &a, &a);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(a.v[i]), &(cmp.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_sub failed\n");
    };
    return (res);
}

// void ibz_vec_4_is_zero(ibz_vec_4_t *x);
int
quat_test_dim4_ibz_vec_4_is_zero(void)
{
    int res = 0;
    ibz_vec_4_t x;
    ibz_vec_4_init(&x);
    ibz_vec_4_set(&x, 0, 0, 0, 0);
    res = res || !ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 20, 0, 0, 0);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 0, -1, 0, 0);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 0, 0, 2, 0);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 0, 0, 0, 1);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 1, 1, 1, 1);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, -1, 1, 1, -1);
    res = res || ibz_vec_4_is_zero(&x);
    ibz_vec_4_set(&x, 0, 0, 0, 0);
    ibz_set(&(x.v[0]), 0, 0);
    ibz_set(&(x.v[1]), 0, 0);
    ibz_set(&(x.v[2]), 0, 0);
    ibz_set(&(x.v[3]), 0, 0);
    res = res | (1 - ibz_vec_4_is_zero(&x));
    ibz_set(&(x.v[3]), 1, 2);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[3]), -1, 2);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[2]), 1, 2);
    ibz_set(&(x.v[3]), 0, 0);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[2]), -20, 6);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[1]), 1, 2);
    ibz_set(&(x.v[2]), 0, 0);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[1]), -50000, 18);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[0]), 1, 2);
    ibz_set(&(x.v[1]), 0, 0);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[0]), -90000, 19);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[0]), 0, 0);
    ibz_set(&(x.v[1]), -500, 10);
    ibz_set(&(x.v[2]), 20, 6);
    ibz_set(&(x.v[3]), 0, 0);
    res = res | ibz_vec_4_is_zero(&x);
    ibz_set(&(x.v[0]), 19, 6);
    ibz_set(&(x.v[1]), -500, 10);
    ibz_set(&(x.v[2]), 20, 6);
    ibz_set(&(x.v[3]), -2, 3);
    res = res | ibz_vec_4_is_zero(&x);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_is_zero failed\n");
    }
    return (res);
}

// void ibz_vec_4_scalar_mul(ibz_vec_4_t *prod, const ibz_t *scalar, const ibz_vec_4_t *vec);
int
quat_test_dim4_ibz_vec_4_scalar_mul(void)
{
    int res = 0;
    int s;
    ibz_t scalar;
    ibz_vec_4_t prod, vec;
    ibz_vec_4_init(&vec);
    ibz_vec_4_init(&prod);
    ibz_init(&scalar);

    s = 5;
    ibz_set(&scalar, s, 4);
    for (int i = 0; i < 4; i++) {
        ibz_set(&(vec.v[i]), i, 3);
    }
    ibz_vec_4_scalar_mul(&prod, &scalar, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(prod.v[i]), i * s) != 0);
    }

    ibz_vec_4_scalar_mul(&vec, &scalar, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(vec.v[i]), i * s) != 0);
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_scalar_mul failed\n");
    }
    return (res);
}

// int ibz_vec_4_scalar_div(ibz_vec_4_t *quot, const ibz_t *scalar, const ibz_vec_4_t *vec);
int
quat_test_dim4_ibz_vec_4_scalar_div(void)
{
    int res = 0;
    int s;
    ibz_t scalar;
    ibz_vec_4_t quot, vec;
    ibz_vec_4_init(&vec);
    ibz_vec_4_init(&quot);
    ibz_init(&scalar);

    s = 5;
    ibz_set(&scalar, s, 4);
    for (int i = 0; i < 4; i++) {
        ibz_set(&(vec.v[i]), i * s, 7);
    }
    res = res || !ibz_vec_4_scalar_div(&quot, &scalar, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(quot.v[i]), i) != 0);
    }

    res = res || ibz_vec_4_scalar_div(&vec, &scalar, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(vec.v[i]), i) != 0);
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_scalar_div failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_copy(ibz_mat_4x4_t *new, const ibz_mat_4x4_t *mat);
int
quat_test_dim4_ibz_mat_4x4_copy(void)
{
    int res = 0;
    ibz_mat_4x4_t mat, new;
    ibz_mat_4x4_init(&new);
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_zero(&mat);
    ibz_set(&(mat.m[0][0]), 1, 2);
    ibz_set(&(mat.m[0][1]), 2, 3);
    ibz_set(&(mat.m[0][2]), -7, 4);
    ibz_set(&(mat.m[0][3]), 77, 8);
    ibz_set(&(mat.m[2][0]), 13, 5);
    ibz_set(&(mat.m[1][1]), 20, 6);
    ibz_set(&(mat.m[3][2]), -77, 8);
    ibz_set(&(mat.m[3][3]), 7, 4);
    ibz_mat_4x4_copy(&new, &mat);
    res = res || !ibz_mat_4x4_equal(&new, &mat);
    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_copy failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_transpose(ibz_mat_4x4_t *transposed, const ibz_mat_4x4_t *mat)
int
quat_test_dim4_ibz_mat_4x4_transpose(void)
{
    int res = 0;
    ibz_mat_4x4_t mat, transposed, cmp;
    ibz_mat_4x4_init(&transposed);
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_init(&cmp);
    ibz_mat_4x4_zero(&mat);
    ibz_mat_4x4_zero(&cmp);
    ibz_set(&(mat.m[0][0]), 1, 2);
    ibz_set(&(cmp.m[0][0]), 1, 2);
    ibz_set(&(mat.m[0][1]), 2, 3);
    ibz_set(&(cmp.m[1][0]), 2, 3);
    ibz_set(&(mat.m[0][2]), -7, 4);
    ibz_set(&(cmp.m[2][0]), -7, 4);
    ibz_set(&(mat.m[0][3]), 77, 8);
    ibz_set(&(cmp.m[3][0]), 77, 8);
    ibz_set(&(mat.m[2][0]), 13, 5);
    ibz_set(&(cmp.m[0][2]), 13, 5);
    ibz_set(&(mat.m[1][1]), 20, 6);
    ibz_set(&(cmp.m[1][1]), 20, 6);
    ibz_set(&(mat.m[3][2]), -77, 8);
    ibz_set(&(cmp.m[2][3]), -77, 8);
    ibz_set(&(mat.m[3][3]), 7, 4);
    ibz_set(&(cmp.m[3][3]), 7, 4);
    ibz_mat_4x4_transpose(&transposed, &mat);
    res = res || !ibz_mat_4x4_equal(&transposed, &cmp);
    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_transpose failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_zero(ibz_mat_4x4_t *zero);
int
quat_test_dim4_ibz_mat_4x4_zero(void)
{
    int res = 0;
    ibz_mat_4x4_t mat, cmp;
    ibz_mat_4x4_init(&cmp);
    ibz_mat_4x4_init(&mat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(cmp.m[i][j]), 0, 0);
        }
    }
    ibz_mat_4x4_zero(&mat);
    res = res || !ibz_mat_4x4_equal(&cmp, &mat);
    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_zero failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_identity(ibz_mat_4x4_t *id);
int
quat_test_dim4_ibz_mat_4x4_identity(void)
{
    int res = 0;
    ibz_mat_4x4_t mat, cmp;
    ibz_mat_4x4_init(&cmp);
    ibz_mat_4x4_init(&mat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(cmp.m[i][j]), 0, 0);
        }
        ibz_set(&(cmp.m[i][i]), 1, 2);
    }
    ibz_mat_4x4_identity(&mat);
    res = res || !ibz_mat_4x4_equal(&cmp, &mat);
    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_identity failed\n");
    }
    return (res);
}

// int ibz_mat_4x4_equal(const ibz_mat_4x4_t *mat1, const ibz_mat_4x4_t *mat2);
int
quat_test_dim4_ibz_mat_4x4_equal(void)
{
    int res = 0;
    ibz_mat_4x4_t a, b;
    ibz_mat_4x4_init(&a);
    ibz_mat_4x4_init(&b);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(a.m[i][j]), i + j, 4);
            ibz_set(&(b.m[i][j]), i + j, 4);
        }
    }
    res = res || (!ibz_mat_4x4_equal(&a, &b));

    ibz_set(&(b.m[2][2]), 2, 3);
    res = res || ibz_mat_4x4_equal(&a, &b);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_equal failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_scalar_mul(ibz_mat_4x4_t *prod, const ibz_t *scalar, const ibz_mat_4x4_t *mat);
int
quat_test_dim4_ibz_mat_4x4_scalar_mul(void)
{
    int res = 0;
    int s;
    ibz_t scalar;
    ibz_mat_4x4_t prod, mat, cmp;
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_init(&cmp);
    ibz_mat_4x4_init(&prod);
    ibz_init(&scalar);

    s = 5;
    ibz_set(&scalar, s, 4);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), i + j, 4);
            ibz_set(&(cmp.m[i][j]), (i + j) * s, 8);
        }
    }
    ibz_mat_4x4_scalar_mul(&prod, &scalar, &mat);
    res = res || (!ibz_mat_4x4_equal(&prod, &cmp));

    ibz_mat_4x4_scalar_mul(&mat, &scalar, &mat);
    res = res || (!ibz_mat_4x4_equal(&mat, &cmp));

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_scalar_mul failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_gcd(ibz_t *gcd, const ibz_mat_4x4_t *mat);
int
quat_test_dim4_ibz_mat_4x4_gcd(void)
{
    int res = 0;
    int d;
    ibz_t cmp, gcd;
    ibz_mat_4x4_t mat;
    ibz_mat_4x4_init(&mat);
    ibz_init(&cmp);
    ibz_init(&gcd);

    d = 2;
    ibz_set(&cmp, d, 3);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), d * i * j, 7);
        }
    }
    ibz_mat_4x4_gcd(&gcd, &mat);
    res = res || ibz_cmp(&gcd, &cmp);

    d = 21;
    ibz_set(&cmp, d, 6);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), d * i * j, 9);
        }
    }
    ibz_mat_4x4_gcd(&gcd, &mat);
    res = res || ibz_cmp(&gcd, &cmp);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_gcd failed\n");
    }
    return (res);
}

// int ibz_mat_4x4_scalar_div(ibz_mat_4x4_t *quot, const ibz_t *scalar, const ibz_mat_4x4_t *mat);
int
quat_test_dim4_ibz_mat_4x4_scalar_div(void)
{
    int res = 0;
    int s;
    ibz_t scalar;
    ibz_mat_4x4_t quot, mat, cmp;
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_init(&cmp);
    ibz_mat_4x4_init(&quot);
    ibz_init(&scalar);

    s = 5;
    ibz_set(&scalar, s, 4);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), (i + j) * s, 8);
            ibz_set(&(cmp.m[i][j]), (i + j), 4);
        }
    }
    ibz_mat_4x4_scalar_div(&quot, &scalar, &mat);
    res = res || (!ibz_mat_4x4_equal(&quot, &cmp));

    ibz_mat_4x4_scalar_div(&mat, &scalar, &mat);
    res = res || (!ibz_mat_4x4_equal(&mat, &cmp));

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_scalar_div failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_mul(ibz_mat_4x4_t *res, const ibz_mat_4x4_t *a, const ibz_mat_4x4_t *b)
int
quat_test_dim4_ibz_mat_4x4_mul(void)
{
    int res = 0;
    ibz_mat_4x4_t a, b, prod, cmp;
    ibz_mat_4x4_init(&a);
    ibz_mat_4x4_init(&b);
    ibz_mat_4x4_init(&prod);
    ibz_mat_4x4_init(&cmp);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(a.m[i][j]), 0, 0);
            ibz_set(&(b.m[i][j]), 0, 0);
            ibz_set(&(cmp.m[i][j]), 0, 0);
        }
    }

    ibz_set(&(a.m[0][0]), 1, 2);
    ibz_set(&(a.m[0][1]), 2, 3);
    ibz_set(&(a.m[0][2]), 1, 2);
    ibz_set(&(a.m[1][1]), 1, 2);
    ibz_set(&(a.m[1][2]), 3, 3);
    ibz_set(&(a.m[2][2]), 1, 2);
    ibz_set(&(a.m[2][3]), 4, 4);
    ibz_set(&(a.m[3][3]), 1, 2);
    ibz_set(&(b.m[0][0]), -1, 2);
    ibz_set(&(b.m[1][0]), 1, 2);
    ibz_set(&(b.m[1][1]), -2, 3);
    ibz_set(&(b.m[2][0]), 1, 2);
    ibz_set(&(b.m[2][2]), 3, 3);
    ibz_set(&(b.m[3][0]), 1, 2);
    ibz_set(&(b.m[3][1]), 5, 4);
    ibz_set(&(b.m[3][2]), -1, 2);
    ibz_set(&(b.m[3][3]), 2, 3);
    ibz_set(&(cmp.m[0][0]), 4, 4);
    ibz_set(&(cmp.m[0][1]), -4, 4);
    ibz_set(&(cmp.m[0][2]), 1, 2);
    ibz_set(&(cmp.m[1][0]), 10, 5);
    ibz_set(&(cmp.m[1][1]), -2, 3);
    ibz_set(&(cmp.m[1][2]), 3, 3);
    ibz_set(&(cmp.m[2][0]), 7, 4);
    ibz_set(&(cmp.m[2][1]), 20, 6);
    ibz_set(&(cmp.m[2][2]), -3, 3);
    ibz_set(&(cmp.m[2][3]), 8, 5);
    ibz_set(&(cmp.m[3][0]), 1, 2);
    ibz_set(&(cmp.m[3][1]), 5, 4);
    ibz_set(&(cmp.m[3][2]), -1, 2);
    ibz_set(&(cmp.m[3][3]), 2, 3);
    ibz_mat_4x4_mul(&prod, &a, &b);
    res = res || ibz_mat_4x4_equal(&cmp, &prod);

    ibz_mat_4x4_mul(&b, &a, &b);
    res = res || ibz_mat_4x4_equal(&b, &cmp);

    ibz_set(&(b.m[0][0]), -1, 2);
    ibz_set(&(b.m[1][0]), 1, 2);
    ibz_set(&(b.m[1][1]), -2, 3);
    ibz_set(&(b.m[2][0]), 1, 2);
    ibz_set(&(b.m[2][2]), 3, 3);
    ibz_set(&(b.m[3][0]), 1, 2);
    ibz_set(&(b.m[3][1]), 5, 4);
    ibz_set(&(b.m[3][2]), -1, 2);
    ibz_set(&(b.m[3][3]), 2, 3);
    ibz_mat_4x4_mul(&a, &a, &b);
    res = res || ibz_mat_4x4_equal(&a, &cmp);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_mul failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_inv_make_coeff_pmp(ibz_t *coeff, const ibz_t *a1, const ibz_t *a2, const ibz_t *b1, const ibz_t *b2,
// const ibz_t *c1, const ibz_t *c2);
int
quat_test_dim4_ibz_mat_4x4_inv_make_coeff_pmp(void)
{
    int res = 0;
    ibz_t coeff, cmp, a1, a2, b1, b2, c1, c2;
    ibz_init(&a1);
    ibz_init(&a2);
    ibz_init(&b1);
    ibz_init(&b2);
    ibz_init(&c1);
    ibz_init(&c2);
    ibz_init(&coeff);
    ibz_init(&cmp);

    ibz_set(&a1, 0, 0);
    ibz_set(&a2, 3, 3);
    ibz_set(&b1, -1, 2);
    ibz_set(&b2, 0, 0);
    ibz_set(&c1, -1, 2);
    ibz_set(&c2, 0, 0);
    ibz_set(&cmp, 0, 0);
    ibz_mat_4x4_inv_make_coeff_pmp(&coeff, &a1, &a2, &b1, &b2, &c1, &c2);
    res = res || ibz_cmp(&cmp, &coeff);

    ibz_set(&a1, 2, 3);
    ibz_set(&a2, 3, 3);
    ibz_set(&b1, -1, 2);
    ibz_set(&b2, 1, 2);
    ibz_set(&c1, -4, 4);
    ibz_set(&c2, 2, 3);
    ibz_set(&cmp, -1, 2);
    ibz_mat_4x4_inv_make_coeff_pmp(&coeff, &a1, &a2, &b1, &b2, &c1, &c2);
    res = res || ibz_cmp(&cmp, &coeff);

    ibz_set(&a1, 2, 3);
    ibz_set(&cmp, 4, 4);
    ibz_mat_4x4_inv_make_coeff_pmp(&a1, &a1, &a1, &a1, &a1, &a1, &a1);
    res = res || ibz_cmp(&cmp, &a1);

    if (res != 0) {
        printf("Quaternion unit test dim4_inv_make_coeff_pmp failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_inv_make_coeff_mpm(ibz_t *coeff, const ibz_t *a1, const ibz_t *a2, const ibz_t *b1,
// const ibz_t *b2, const ibz_t *c1, const ibz_t *c2);
int
quat_test_dim4_ibz_mat_4x4_inv_make_coeff_mpm(void)
{
    int res = 0;
    ibz_t coeff, cmp, a1, a2, b1, b2, c1, c2;
    ibz_init(&a1);
    ibz_init(&a2);
    ibz_init(&b1);
    ibz_init(&b2);
    ibz_init(&c1);
    ibz_init(&c2);
    ibz_init(&coeff);
    ibz_init(&cmp);

    ibz_set(&a1, 0, 0);
    ibz_set(&a2, 3, 3);
    ibz_set(&b1, -1, 2);
    ibz_set(&b2, 0, 0);
    ibz_set(&c1, -1, 2);
    ibz_set(&c2, 0, 0);
    ibz_set(&cmp, 0, 0);
    ibz_mat_4x4_inv_make_coeff_mpm(&coeff, &a1, &a2, &b1, &b2, &c1, &c2);
    res = res || ibz_cmp(&cmp, &coeff);

    ibz_set(&a1, 2, 3);
    ibz_set(&a2, 3, 3);
    ibz_set(&b1, -1, 2);
    ibz_set(&b2, 1, 2);
    ibz_set(&c1, -4, 4);
    ibz_set(&c2, 2, 3);
    ibz_set(&cmp, 1, 2);
    ibz_mat_4x4_inv_make_coeff_mpm(&coeff, &a1, &a2, &b1, &b2, &c1, &c2);
    res = res || ibz_cmp(&cmp, &coeff);

    ibz_set(&a1, 2, 3);
    ibz_set(&cmp, -4, 4);
    ibz_mat_4x4_inv_make_coeff_mpm(&a1, &a1, &a1, &a1, &a1, &a1, &a1);
    res = res || ibz_cmp(&cmp, &a1);

    if (res != 0) {
        printf("Quaternion unit test dim4_inv_make_coeff_mpm failed\n");
    }
    return (res);
}

// returns 1 if inverse is valid, 0 otherwise
int
quat_test_dim4_validate_mat_4x4_rational_inv_if_exists(const ibz_mat_4x4_t *mat,
                                                       const ibz_t *det,
                                                       const ibz_mat_4x4_t *inv)
{
    int res = 1;
    ibz_mat_4x4_t det_id, prod;
    ibz_mat_4x4_init(&det_id);
    ibz_mat_4x4_init(&prod);
    ibz_mat_4x4_identity(&det_id);
    ibz_mat_4x4_scalar_mul(&det_id, det, &det_id);
    ibz_mat_4x4_mul(&prod, inv, mat);
    res = res && ibz_mat_4x4_equal(&det_id, &prod);
    ibz_mat_4x4_mul(&prod, mat, inv);
    res = res && ibz_mat_4x4_equal(&det_id, &prod);
    return (res);
}

// int ibz_4x4_inv_with_det_as_denom(ibz_mat_4x4_t *inv, ibz_t *det, const ibz_mat_4x4_t mat);
int
quat_test_dim4_ibz_mat_4x4_inv_with_det_as_denom(void)
{
    int res = 0;
    ibz_t det;
    ibz_mat_4x4_t mat, inv;
    ibz_init(&det);
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_init(&inv);

    ibz_mat_4x4_zero(&mat);
    res = res || ibz_mat_4x4_inv_with_det_as_denom(&inv, &det, &mat);
    res = res || !ibz_is_zero(&det);
    ibz_mat_4x4_identity(&mat);
    if (ibz_mat_4x4_inv_with_det_as_denom(&inv, &det, &mat)) {
        res = res || !ibz_is_one(&det);
        res = res || !quat_test_dim4_validate_mat_4x4_rational_inv_if_exists(&inv, &det, &mat);
    } else {
        res = 1;
    }
    ibz_set(&(mat.m[0][0]), 2, 3);
    ibz_set(&(mat.m[0][1]), -17, 6);
    ibz_set(&(mat.m[0][2]), 3, 3);
    ibz_set(&(mat.m[0][3]), 5, 4);
    ibz_set(&(mat.m[1][1]), -2, 3);
    ibz_set(&(mat.m[1][2]), 3, 3);
    ibz_set(&(mat.m[1][3]), 2, 3);
    ibz_set(&(mat.m[2][2]), -3, 3);
    ibz_set(&(mat.m[2][3]), 0, 0);
    ibz_set(&(mat.m[3][3]), 1, 2);
    if (ibz_mat_4x4_inv_with_det_as_denom(&inv, &det, &mat)) {
        res = res || (ibz_cmp_int32(&det, 12) != 0);
        res = res || !quat_test_dim4_validate_mat_4x4_rational_inv_if_exists(&inv, &det, &mat);
    } else {
        res = 1;
    }
    ibz_set(&(mat.m[3][0]), 1, 2);
    ibz_set(&(mat.m[3][1]), 8, 5);
    ibz_set(&(mat.m[3][2]), -9, 5);
    ibz_set(&(mat.m[2][0]), 3, 3);
    ibz_set(&(mat.m[2][1]), 0, 0);
    ibz_set(&(mat.m[1][0]), 4, 4);
    if (ibz_mat_4x4_inv_with_det_as_denom(&inv, &det, &mat)) {
        res = res || (ibz_cmp_int32(&det, -1503) != 0);
        res = res || !quat_test_dim4_validate_mat_4x4_rational_inv_if_exists(&inv, &det, &mat);
    } else {
        res = 1;
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_inv_with_det_as_denom failed\n");
    }
    return (res);
}

// int ibz_4x4_inv_with_det_as_denom(ibz_mat_4x4_t *inv, ibz_t *det, const ibz_mat_4x4_t mat);
int
quat_test_ibz_mat_4x4_inv_with_det_as_denom_randomized(int matrix_bitsize, int iterations)
{
    int res = 0;
    int randret = 0;
    ibz_t det;
    ibz_mat_4x4_t mat, inv;
    ibz_mat_4x4_t det_id, prod;
    ibz_mat_4x4_init(&det_id);
    ibz_mat_4x4_init(&prod);
    ibz_init(&det);
    ibz_mat_4x4_init(&mat);
    ibz_mat_4x4_init(&inv);

    for (int r = 0; r < iterations; r++) {
        do {
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++) {
                    randret = randret | !ibz_rand_interval_bits(&mat.m[i][j], matrix_bitsize);
                    if (randret != 0) {
                        printf("Randomness failed in quaternion unit test for ibz_mat_2x2_inv_mod\n");
                        return (res);
                    }
                }
        } while (!ibz_mat_4x4_inv_with_det_as_denom(&inv, &det, &mat));
        ibz_mat_4x4_identity(&det_id);
        ibz_mat_4x4_scalar_mul(&det_id, &det, &det_id);
        ibz_mat_4x4_mul(&prod, &inv, &mat);
        res = res || !ibz_mat_4x4_equal(&det_id, &prod);
        ibz_mat_4x4_mul(&prod, &mat, &inv);
        res = res || !ibz_mat_4x4_equal(&det_id, &prod);
    }
    if (res != 0) {
        printf("Quaternion unit test for ibz_mat_4x4_inv_with_det_as_denom failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_eval(ibz_vec_4_t  *res, const ibz_mat_4x4_t *mat, const ibz_vec_4_t *vec);
// void ibz_mat_4x4_eval_t(ibz_vec_4_t *res, const ibz_vec_4_t *vec, const ibz_mat_4x4_t *mat);
int
quat_test_dim4_ibz_mat_4x4_eval(void)
{
    int res = 0;
    ibz_mat_4x4_t mat;
    ibz_vec_4_t vec, cmp, vres;
    ibz_vec_4_init(&cmp);
    ibz_vec_4_init(&vres);
    ibz_vec_4_init(&vec);
    ibz_mat_4x4_init(&mat);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), i * j, 5);
        }
        ibz_set(&(vec.v[i]), i, 3);
    }
    ibz_set(&(cmp.v[0]), 0, 0);
    ibz_set(&(cmp.v[1]), 14, 5);
    ibz_set(&(cmp.v[2]), 28, 6);
    ibz_set(&(cmp.v[3]), 42, 7);
    ibz_mat_4x4_eval(&vres, &mat, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(vres.v[i]), &(cmp.v[i]));
    }
    ibz_vec_4_set(&vres, 0, 0, 0, 0);
    ibz_mat_4x4_transpose(&mat, &mat);
    ibz_mat_4x4_eval_t(&vres, &vec, &mat);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(vres.v[i]), &(cmp.v[i]));
    }
    ibz_mat_4x4_transpose(&mat, &mat);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), i * (j - 1) + 1, 4);
        }
        ibz_set(&(vec.v[i]), i * i - 2, 4);
    }
    ibz_set(&(cmp.v[0]), 6, 4);
    ibz_set(&(cmp.v[1]), 24, 6);
    ibz_set(&(cmp.v[2]), 42, 7);
    ibz_set(&(cmp.v[3]), 60, 7);
    ibz_mat_4x4_eval(&vres, &mat, &vec);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(vres.v[i]), &(cmp.v[i]));
    }
    ibz_vec_4_set(&vres, 0, 0, 0, 0);
    ibz_mat_4x4_transpose(&mat, &mat);
    ibz_mat_4x4_eval_t(&vres, &vec, &mat);
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(vres.v[i]), &(cmp.v[i]));
    }
    ibz_mat_4x4_transpose(&mat, &mat);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_mat_4x4_eval failed\n");
    }
    return (res);
}

// void quat_qf_eval(ibz_t *res, const ibz_mat_4x4_t *qf, const quat_alg_coord_t *coord);
int
quat_test_dim4_qf_eval(void)
{
    int res = 0;
    ibz_t ires, cmp;
    ibz_mat_4x4_t qf;
    ibz_vec_4_t vec;
    ibz_init(&cmp);
    ibz_init(&ires);
    ibz_vec_4_init(&vec);
    ibz_mat_4x4_init(&qf);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(qf.m[i][j]), i * j, 5);
        }
        ibz_set(&(vec.v[i]), i, 3);
    }
    ibz_set(&(cmp), 196, 9);
    quat_qf_eval(&ires, &qf, &vec);
    res = res || ibz_cmp(&ires, &cmp);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(qf.m[i][j]), (i + 1) * (j + 1) - 4, 5);
        }
        ibz_set(&(vec.v[i]), (i - 1) * 2 - 2, 4);
    }
    ibz_set(&(cmp), -4 * 16, 9);
    quat_qf_eval(&ires, &qf, &vec);
    res = res || ibz_cmp(&ires, &cmp);

    if (res != 0) {
        printf("Quaternion unit test dim4_qf_eval failed\n");
    }
    return (res);
}

// void ibz_vec_4_content(ibz_t *content, const quat_alg_coord_t *v);
int
quat_test_dim4_ibz_vec_4_content(void)
{
    int res = 0;
    ibz_t c, cmp;
    ibz_vec_4_t x;
    ibz_init(&c);
    ibz_init(&cmp);
    ibz_vec_4_init(&x);

    ibz_set(&(x.v[0]), 0, 0);
    ibz_set(&(x.v[1]), 0, 0);
    ibz_set(&(x.v[2]), 0, 0);
    ibz_set(&(x.v[3]), 0, 0);
    ibz_set(&cmp, 0, 0);
    ibz_vec_4_content(&c, &x);
    res = res || ibz_cmp(&c, &cmp);

    ibz_set(&(x.v[0]), 5, 4);
    ibz_set(&(x.v[1]), 25, 6);
    ibz_set(&(x.v[2]), 125, 8);
    ibz_set(&(x.v[3]), 30, 6);
    ibz_set(&cmp, 5, 4);
    ibz_vec_4_content(&c, &x);
    res = res || ibz_cmp(&c, &cmp);

    ibz_set(&(x.v[0]), 5, 4);
    ibz_set(&(x.v[1]), 2, 3);
    ibz_set(&(x.v[2]), 125, 8);
    ibz_set(&(x.v[3]), 30, 6);
    ibz_set(&cmp, 1, 2);
    ibz_vec_4_content(&c, &x);
    res = res || ibz_cmp(&c, &cmp);

    ibz_set(&(x.v[0]), 5, 4);
    ibz_set(&(x.v[1]), -2, 3);
    ibz_set(&(x.v[2]), 125, 9);
    ibz_set(&(x.v[3]), 0, 0);
    ibz_set(&cmp, 1, 2);
    ibz_vec_4_content(&c, &x);
    res = res || ibz_cmp(&c, &cmp);

    ibz_set(&(x.v[0]), 0, 0);
    ibz_set(&(x.v[1]), -2, 3);
    ibz_set(&(x.v[2]), 0, 0);
    ibz_set(&(x.v[3]), 0, 0);
    ibz_set(&cmp, 2, 3);
    ibz_vec_4_content(&c, &x);
    res = res || ibz_cmp(&c, &cmp);

    if (res != 0) {
        printf("Quaternion unit test dim4_ibz_vec_4_content failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_dim4(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of matrices, vectors and quadratic forms in dimension 4\n");
    res = res | quat_test_dim4_ibz_vec_4_set();
    res = res | quat_test_dim4_ibz_vec_4_copy();
    res = res | quat_test_dim4_vec_4_copy_ibz();
    res = res | quat_test_dim4_ibz_vec_4_add();
    res = res | quat_test_dim4_ibz_vec_4_sub();
    res = res | quat_test_dim4_ibz_vec_4_is_zero();
    res = res | quat_test_dim4_ibz_vec_4_scalar_mul();
    res = res | quat_test_dim4_ibz_vec_4_content();
    res = res | quat_test_dim4_ibz_mat_4x4_copy();
    res = res | quat_test_dim4_ibz_mat_4x4_transpose();
    res = res | quat_test_dim4_ibz_mat_4x4_zero();
    res = res | quat_test_dim4_ibz_mat_4x4_identity();
    res = res | quat_test_dim4_ibz_mat_4x4_equal();
    res = res | quat_test_dim4_ibz_mat_4x4_scalar_mul();
    res = res | quat_test_dim4_ibz_mat_4x4_mul();
    res = res | quat_test_dim4_ibz_mat_4x4_gcd();
    res = res | quat_test_dim4_ibz_mat_4x4_scalar_div();
    res = res | quat_test_dim4_ibz_mat_4x4_inv_make_coeff_pmp();
    res = res | quat_test_dim4_ibz_mat_4x4_inv_make_coeff_mpm();
    res = res | quat_test_dim4_ibz_mat_4x4_inv_with_det_as_denom();
    res = res | quat_test_ibz_mat_4x4_inv_with_det_as_denom_randomized(100, 10);
    res = res | quat_test_dim4_ibz_mat_4x4_eval();
    res = res | quat_test_dim4_qf_eval();
    return (res);
}
