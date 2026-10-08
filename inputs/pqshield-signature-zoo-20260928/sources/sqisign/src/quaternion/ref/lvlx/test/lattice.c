#include "quaternion_tests.h"
#include <stdlib.h>
#include <prng.h>
#include <quaternion_data.h>

// int ibz_mat_4x4_is_hnf(const ibz_mat_4x4_t *mat);
int
quat_test_ibz_mat_4x4_is_hnf(void)
{
    int res = 0;
    ibz_mat_4x4_t mat;
    ibz_mat_4x4_init(&mat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), 0, 0);
        }
    }
    res = res || (!ibz_mat_4x4_is_hnf(&mat));
    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 6, 4);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][1]), 6, 4);
    ibz_set(&(mat.m[1][2]), 5, 4);
    ibz_set(&(mat.m[1][3]), 4, 4);
    ibz_set(&(mat.m[2][2]), 5, 4);
    ibz_set(&(mat.m[2][3]), 4, 4);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (!ibz_mat_4x4_is_hnf(&mat));

    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][1]), 0, 0);
    ibz_set(&(mat.m[1][2]), 0, 0);
    ibz_set(&(mat.m[1][3]), 0, 0);
    ibz_set(&(mat.m[2][2]), 5, 4);
    ibz_set(&(mat.m[2][3]), 4, 4);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (!ibz_mat_4x4_is_hnf(&mat));

    // negative tests
    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][1]), 1, 2);
    ibz_set(&(mat.m[1][2]), 5, 4);
    ibz_set(&(mat.m[1][3]), 9, 5);
    ibz_set(&(mat.m[2][2]), 5, 4);
    ibz_set(&(mat.m[2][3]), 4, 4);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (ibz_mat_4x4_is_hnf(&mat));

    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][1]), 1, 2);
    ibz_set(&(mat.m[1][2]), -5, 4);
    ibz_set(&(mat.m[1][3]), 1, 2);
    ibz_set(&(mat.m[2][2]), 5, 4);
    ibz_set(&(mat.m[2][3]), 4, 4);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (ibz_mat_4x4_is_hnf(&mat));

    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][0]), 2, 3);
    ibz_set(&(mat.m[1][1]), 3, 3);
    ibz_set(&(mat.m[1][2]), 1, 2);
    ibz_set(&(mat.m[1][3]), 1, 2);
    ibz_set(&(mat.m[2][2]), 5, 4);
    ibz_set(&(mat.m[2][3]), 4, 4);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (ibz_mat_4x4_is_hnf(&mat));

    ibz_set(&(mat.m[0][0]), 7, 4);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 5, 4);
    ibz_set(&(mat.m[0][3]), 4, 4);
    ibz_set(&(mat.m[1][0]), 2, 3);
    ibz_set(&(mat.m[1][1]), 3, 3);
    ibz_set(&(mat.m[1][2]), -1, 2);
    ibz_set(&(mat.m[1][3]), 7, 4);
    ibz_set(&(mat.m[2][2]), 0, 0);
    ibz_set(&(mat.m[2][3]), 0, 0);
    ibz_set(&(mat.m[3][3]), 4, 4);
    res = res || (ibz_mat_4x4_is_hnf(&mat));
    if (res != 0) {
        printf("Quaternion unit test hnf_ibz_mat_4x4_is_hnf failed\n");
    }
    return (res);
}

// void quat_lattice_reduce_denom(quat_lattice_t *reduced, const quat_lattice_t *lat);
int
quat_test_lattice_reduce_denom(void)
{
    int res = 0;
    int s;
    quat_lattice_t red, lat, cmp;
    quat_lattice_init(&red);
    quat_lattice_init(&cmp);
    quat_lattice_init(&lat);

    s = 15;
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(lat.basis.m[i][j]), (i + j) * s, 11);
            ibz_set(&(cmp.basis.m[i][j]), (i + j), 11);
        }
    }
    ibz_set(&(lat.denom), 4 * s, 8);
    ibz_set(&(cmp.denom), 4, 4);

    quat_lattice_reduce_denom(&red, &lat);
    res = res || (!ibz_mat_4x4_equal(&(red.basis), &(cmp.basis)));
    res = res || ibz_cmp(&(red.denom), &(cmp.denom));

    quat_lattice_reduce_denom(&lat, &lat);
    res = res || (!ibz_mat_4x4_equal(&(lat.basis), &(cmp.basis)));
    res = res || ibz_cmp(&(lat.denom), &(cmp.denom));

    if (res != 0) {
        printf("Quaternion unit test lattice_reduce_denom failed\n");
    }
    return (res);
}

// int quat_lattice_contains(quat_alg_coord_t *coord, const quat_lattice_t *lat, const quat_alg_elem_t *x);
int
quat_test_lattice_contains(void)
{
    int res = 0;
    quat_alg_elem_t x;
    ibz_vec_4_t coord, cmp;
    quat_lattice_t lat;
    quat_alg_elem_init(&x);
    ibz_vec_4_init(&coord);
    ibz_vec_4_init(&cmp);
    quat_lattice_init(&lat);

    // lattice 1
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(lat.basis.m[i][j]), 0, 0);
        }
    }
    ibz_set(&(lat.basis.m[0][0]), 4, 4);
    ibz_set(&(lat.basis.m[0][2]), 3, 3);
    ibz_set(&(lat.basis.m[1][1]), 5, 4);
    ibz_set(&(lat.basis.m[2][2]), 3, 3);
    ibz_set(&(lat.basis.m[3][3]), 7, 4);
    ibz_set(&(lat.denom), 4, 4);

    // x 1, should fail
    ibz_set(&(x.denom), 3, 3);
    ibz_set(&(x.coord.v[0]), 1, 2);
    ibz_set(&(x.coord.v[1]), -2, 3);
    ibz_set(&(x.coord.v[2]), 26, 7);
    ibz_set(&(x.coord.v[3]), 9, 5);

    res = res || quat_lattice_contains(&coord, &lat, &x);
    // again, but with NULL
    res = res || quat_lattice_contains(NULL, &lat, &x);

    // lattice 2
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(lat.basis.m[i][j]), 0, 0);
        }
    }
    ibz_set(&(lat.basis.m[0][0]), 1, 2);
    ibz_set(&(lat.basis.m[1][1]), 2, 3);
    ibz_set(&(lat.basis.m[2][2]), 1, 2);
    ibz_set(&(lat.basis.m[3][3]), 3, 3);
    ibz_set(&(lat.denom), 6, 4);
    // x 1, should succeed
    ibz_set(&(x.denom), 3, 3);
    ibz_set(&(x.coord.v[0]), 1, 2);
    ibz_set(&(x.coord.v[1]), -2, 3);
    ibz_set(&(x.coord.v[2]), 26, 7);
    ibz_set(&(x.coord.v[3]), 9, 5);
    ibz_set(&(cmp.v[0]), 2, 3);
    ibz_set(&(cmp.v[1]), -2, 3);
    ibz_set(&(cmp.v[2]), 52, 8);
    ibz_set(&(cmp.v[3]), 6, 4);

    res = res || (0 == quat_lattice_contains(&coord, &lat, &x));

    res = res || ibz_cmp(&(coord.v[0]), &(cmp.v[0]));
    res = res || ibz_cmp(&(coord.v[1]), &(cmp.v[1]));
    res = res || ibz_cmp(&(coord.v[2]), &(cmp.v[2]));
    res = res || ibz_cmp(&(coord.v[3]), &(cmp.v[3]));
    // again, but with NULL
    res = res || (0 == quat_lattice_contains(NULL, &lat, &x));

    if (res != 0) {
        printf("Quaternion unit test lattice_contains failed\n");
    }
    return (res);
}

// int quat_lattice_inclusion(const quat_lattice_t *sublat, const quat_lattice_t *overlat)
int
quat_test_lattice_inclusion(void)
{
    int res = 0;
    quat_lattice_t lat, cmp;
    quat_lattice_init(&lat);
    quat_lattice_init(&cmp);

    ibz_set(&lat.denom, 1, 2);
    ibz_set(&cmp.denom, 1, 2);
    ibz_mat_4x4_identity(&(lat.basis));
    ibz_mat_4x4_identity(&(cmp.basis));
    res = res || !quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(lat.denom), 5, 4);
    ibz_set(&(cmp.denom), 4, 4);
    res = res || quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(lat.denom), 1, 2);
    ibz_set(&(cmp.denom), 3, 3);
    res = res || !quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(lat.denom), 3, 3);
    ibz_set(&(cmp.denom), 3, 3);
    res = res || !quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(lat.basis.m[0][0]), 1, 2);
    ibz_set(&(lat.basis.m[1][1]), 2, 3);
    ibz_set(&(lat.basis.m[2][2]), 1, 2);
    ibz_set(&(lat.basis.m[3][3]), 3, 3);
    ibz_set(&(lat.denom), 6, 4);
    ibz_mat_4x4_copy(&(cmp.basis), &(lat.basis));
    ibz_set(&(cmp.denom), 6, 4);
    res = res || !quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(cmp.denom), 12, 5);
    res = res || !quat_lattice_inclusion(&lat, &cmp);
    ibz_set(&(cmp.denom), 6, 4);
    ibz_set(&(cmp.basis.m[3][3]), 165, 9);
    res = res || quat_lattice_inclusion(&lat, &cmp);
    if (res != 0) {
        printf("Quaternion unit test lattice_inclusion failed\n");
    }
    return (res);
}

// int quat_lattice_equal(const quat_lattice_t *lat1, const quat_lattice_t *lat2);
int
quat_test_lattice_equal(void)
{
    int res = 0;
    quat_lattice_t lat, cmp;
    quat_lattice_init(&lat);
    quat_lattice_init(&cmp);

    ibz_set(&lat.denom, 1, 2);
    ibz_set(&cmp.denom, 1, 2);
    ibz_mat_4x4_identity(&(lat.basis));
    ibz_mat_4x4_identity(&(cmp.basis));
    res = res || !quat_lattice_equal(&lat, &cmp);
    ibz_set(&(lat.denom), 5, 4);
    ibz_set(&(cmp.denom), 4, 4);
    res = res || quat_lattice_equal(&lat, &cmp);
    ibz_set(&(lat.denom), 1, 2);
    ibz_set(&(cmp.denom), -1, 2);
    res = res || !quat_lattice_equal(&lat, &cmp);
    ibz_set(&(lat.denom), 3, 3);
    ibz_set(&(cmp.denom), 3, 3);
    res = res || !quat_lattice_equal(&lat, &cmp);
    ibz_set(&(lat.basis.m[0][0]), 1, 2);
    ibz_set(&(lat.basis.m[1][1]), 2, 3);
    ibz_set(&(lat.basis.m[2][2]), 1, 2);
    ibz_set(&(lat.basis.m[3][3]), 3, 3);
    ibz_set(&(lat.denom), 6, 4);
    ibz_mat_4x4_copy(&(cmp.basis), &(lat.basis));
    ibz_set(&(cmp.denom), 6, 4);
    res = res || !quat_lattice_equal(&lat, &cmp);
    ibz_set(&(cmp.denom), -7, 4);
    res = res || quat_lattice_equal(&lat, &cmp);
    ibz_set(&(cmp.denom), 6, 4);
    ibz_set(&(cmp.basis.m[3][3]), 165, 9);
    res = res || quat_lattice_equal(&lat, &cmp);
    if (res != 0) {
        printf("Quaternion unit test lattice_equal failed\n");
    }
    return (res);
}

// void quat_lattice_gram(ibz_mat_4x4_t *G, const quat_lattice_t *lattice);
int
quat_test_lattice_gram()
{
    int res = 0;

    quat_lattice_t lattice;
    ibz_mat_4x4_t gram;
    ibz_t test, norm1, norm2;
    ibz_vec_4_t vec1, vec2;
    quat_alg_elem_t elem1, elem2;
    quat_lattice_init(&lattice);
    ibz_mat_4x4_init(&gram);
    ibz_init(&test);
    ibz_init(&norm1);
    ibz_init(&norm2);
    ibz_vec_4_init(&vec1);
    ibz_vec_4_init(&vec2);
    quat_alg_elem_init(&elem1);
    quat_alg_elem_init(&elem2);

    quat_lattice_O0_set(&lattice);
    quat_lattice_gram(&gram, &lattice);
    quat_alg_elem_set(&elem1, 1, 2, 3, 4, 1);
    quat_alg_elem_set(&elem2, 1, 2, 4, 4, 1);
    quat_lattice_contains(&vec1, &lattice, &elem1);
    quat_lattice_contains(&vec2, &lattice, &elem2);
    quat_alg_conj(&elem2, &elem2);
    quat_alg_mul(&elem1, &elem1, &elem2, &QUATALG_PINFTY);
    ibz_mul(&norm1, &(elem1.coord.v[0]), &ibz_const_two);
    ibz_div(&norm1, &test, &norm1, &(elem1.denom));

    ibz_mat_4x4_eval(&vec1, &gram, &vec1);
    ibz_set(&norm2, 0, 0);
    for (int i = 0; i < 4; i++) {
        ibz_mul(&test, &(vec1.v[i]), &(vec2.v[i]));
        ibz_add(&norm2, &norm2, &test);
    }
    ibz_div(&norm2, &test, &norm2, &(lattice.denom));
    ibz_div(&norm2, &test, &norm2, &(lattice.denom));
    res = res | !(ibz_cmp(&norm1, &norm2) == 0);

    ibz_mat_4x4_zero(&(lattice.basis));
    ibz_set(&(lattice.basis.m[0][0]), 202, 9);
    ibz_set(&(lattice.basis.m[1][1]), 202, 9);
    ibz_set(&(lattice.basis.m[2][2]), 1, 2);
    ibz_set(&(lattice.basis.m[3][3]), 1, 2);
    ibz_set(&(lattice.basis.m[0][2]), 158, 9);
    ibz_set(&(lattice.basis.m[0][3]), 53, 8);
    ibz_set(&(lattice.basis.m[1][2]), 149, 9);
    ibz_set(&(lattice.basis.m[1][3]), 158, 9);
    ibz_set(&(lattice.denom), 2, 3);
    quat_lattice_gram(&gram, &lattice);

    quat_alg_elem_set(&elem1, 2, 360, 149, 1, 0);
    quat_alg_elem_set(&elem2, 2, 53, 360, 0, 1);
    int ok = quat_lattice_contains(&vec1, &lattice, &elem1);
    ok = ok && quat_lattice_contains(&vec2, &lattice, &elem2);
    assert(ok);
    quat_alg_conj(&elem2, &elem2);
    quat_alg_mul(&elem1, &elem1, &elem2, &QUATALG_PINFTY);
    ibz_mul(&norm1, &(elem1.coord.v[0]), &ibz_const_two);
    ibz_div(&norm1, &test, &norm1, &(elem1.denom));

    ibz_mat_4x4_eval(&vec1, &gram, &vec1);
    ibz_set(&norm2, 0, 0);
    for (int i = 0; i < 4; i++) {
        ibz_mul(&test, &(vec1.v[i]), &(vec2.v[i]));
        ibz_add(&norm2, &norm2, &test);
    }
    ibz_div(&norm2, &test, &norm2, &(lattice.denom));
    ibz_div(&norm2, &test, &norm2, &(lattice.denom));
    res = res | !(ibz_cmp(&norm1, &norm2) == 0);

    if (res != 0) {
        printf("Quaternion unit test lattice_gram failed\n");
    }
    return (res);
}

// helper which tests quat_lattice_sample_from_ball on given input, triangular must be a triangular basis of the same
// lattice, can be null but then no containment check can be done
int
quat_test_lat_ball_sample_helper(const quat_lattice_t *lat,
                                 const ibz_t *radius,
                                 const quat_lattice_t *triangular,
                                 const ibz_t *ideal_norm)
{
    int res = 0;
    quat_alg_elem_t vec;
    ibz_t norm_d, norm_n;
    ibz_t n;
    ibz_init(&norm_d);
    ibz_init(&norm_n);
    ibz_init(&n);
    quat_alg_elem_init(&vec);
    // check return value
    res |= !quat_lattice_sample_from_ball(&vec, &n, lat, radius, &PRNG_default_domain);
    // check result is in lattice
    if (triangular != NULL)
        res |= !quat_lattice_contains(NULL, triangular, &vec);
    quat_alg_norm(&norm_n, &norm_d, &vec, &QUATALG_PINFTY);
    res = res | !ibz_is_one(&norm_d);
    ibz_div(&norm_n, &norm_d, &norm_n, ideal_norm);
    res = res | !ibz_is_zero(&norm_d);
    res |= !(ibz_cmp(&norm_n, &n) == 0);
    res |= !(ibz_cmp(&n, radius) <= 0);

    return (res);
}

// int quat_lattice_sample_from_ball(ibz_vec_4_t *x, const quat_lattice_t *lattice, const quat_alg_t
// *alg, const ibz_t *radius, prng_domain_ctx_t *prng_domain);
int
quat_test_lattice_sample_from_ball_randomized(int iterations, int bitsize)
{
    int res = 0;

    ibz_t norm_n, norm_d;
    quat_alg_elem_t vec;
    quat_lattice_t *lattices;
    ibz_t radius;
    ibz_t *norms;

    ibz_init(&norm_n);
    ibz_init(&norm_d);
    ibz_set_from_str(&norm_n, "7fffffffffffffffffffffffffffffff", 16);
    lattices = malloc(iterations * sizeof(quat_lattice_t));
    norms = malloc(iterations * sizeof(ibz_t));
    for (int i = 0; i < iterations; i++) {
        quat_lattice_init(&(lattices[i]));
        ibz_init(&norms[i]);
    }
    ibz_init(&radius);
    quat_alg_elem_init(&vec);

    int randret = quat_test_input_resplike_lattice_generation(lattices, norms, bitsize, iterations);

    if (!randret) {
        for (int i = 0; i < iterations; i++) {
            ibz_copy(&radius, &(lattices[i].basis.m[0][0]));
            ibz_abs(&radius, &radius);
            res |= quat_test_lat_ball_sample_helper(&(lattices[i]), &radius, &(lattices[i]), &(norms[i]));
            if (res != 0)
                break;
        }
    }

    if (res != 0) {
        printf("Quaternion unit test lattice_sample_from_ball_randomized failed\n");
    }

    free(lattices);
    free(norms);
    return (res);
}

// int quat_lattice_bound_parallelogram(ibz_vec_4_t *box, ibz_mat_4x4_t *U, const quat_lattice_t *lat, const ibz_t
// *radius);
// Tested in lll/test/lll_tests.c

// run all previous tests
int
quat_test_lattice(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of lattice functions\n");
    res = res | quat_test_ibz_mat_4x4_is_hnf();
    res = res | quat_test_lattice_reduce_denom();
    res = res | quat_test_lattice_contains();
    res = res | quat_test_lattice_inclusion();
    res = res | quat_test_lattice_equal();
    res = res | quat_test_lattice_gram();
    res = res | quat_test_lattice_sample_from_ball_randomized(10, ibz_bitsize(&QUATALG_PINFTY.p) / 2);
    res = res | quat_test_lattice_sample_from_ball_randomized(10, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
    return (res);
}
