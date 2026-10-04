#include "quaternion_tests.h"

// Schema of tests: initialize structure, test init values, assign values

// void quat_alg_init(quat_alg_t *alg);
int
quat_test_init_alg(void)
{
    quat_alg_t alg;
    int res = 0;
    ibz_t p;
    ibz_init(&p);
    ibz_set(&p, 7, 4);
    quat_alg_init_set(&alg, &p);
    res = res || ibz_cmp(&(alg.p), &p);
    if (res != 0) {
        printf("Quaternion unit test init_alg failed\n");
    }
    return (res);
}

// void quat_alg_elem_init(quat_alg_elem_t *elem);
int
quat_test_init_alg_elem(void)
{
    quat_alg_elem_t elem;
    int res = 0;
    quat_alg_elem_init(&elem);
    for (int i = 0; i < 4; i++) {
        res = res || !ibz_is_zero(&(elem.coord.v[i]));
    }
    res = res || !ibz_is_one(&(elem.denom));
    ibz_set(&(elem.coord.v[0]), 0, 0);
    ibz_set(&(elem.coord.v[1]), 1, 2);
    ibz_set(&(elem.coord.v[2]), 2, 3);
    ibz_set(&(elem.coord.v[3]), 3, 3);
    ibz_set(&(elem.denom), 1, 2);
    res = res || !ibz_is_one(&(elem.denom));
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(elem.coord.v[i]), i) != 0);
    }
    if (res != 0) {
        printf("Quaternion unit test init_alg_elem failed\n");
    }
    return (res);
}

// void ibz_vec_2_init(ibz_vec_2_t *vec);
int
quat_test_init_ibz_vec_2(void)
{
    ibz_vec_2_t vec;
    int res = 0;
    ibz_vec_2_init(&vec);
    for (int i = 0; i < 2; i++) {
        res = res || !ibz_is_zero(&(vec.v[i]));
    }
    for (int i = 0; i < 2; i++) {
        ibz_set(&(vec.v[i]), i, 2);
    }
    for (int i = 0; i < 2; i++) {
        res = res || (ibz_cmp_int32(&(vec.v[i]), i) != 0);
    }
    if (res != 0) {
        printf("Quaternion unit test init_ibz_vec_2 failed\n");
    }
    return (res);
}

// void ibz_vec_4_init(ibz_vec_4_t *vec);
int
quat_test_init_ibz_vec_4(void)
{
    ibz_vec_4_t vec;
    int res = 0;
    ibz_vec_4_init(&vec);
    for (int i = 0; i < 4; i++) {
        res = res || !ibz_is_zero(&(vec.v[i]));
    }
    for (int i = 0; i < 4; i++) {
        ibz_set(&(vec.v[i]), i, 3);
    }
    for (int i = 0; i < 4; i++) {
        res = res || (ibz_cmp_int32(&(vec.v[i]), i) != 0);
    }
    if (res != 0) {
        printf("Quaternion unit test init_ibz_vec_4 failed\n");
    }
    return (res);
}

// void ibz_mat_2x2_init(ibz_mat_2x2_t *mat);
int
quat_test_init_ibz_mat_2x2(void)
{
    ibz_mat_2x2_t mat;
    int res = 0;
    ibz_mat_2x2_init(&mat);
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++)
            res = res || !ibz_is_zero(&(mat.m[i][j]));
    }
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            ibz_set(&(mat.m[i][j]), i + j, 4);
        }
    }
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            res = res || (ibz_cmp_int32(&(mat.m[i][j]), i + j) != 0);
        }
    }
    if (res != 0) {
        printf("Quaternion unit test init_ibz_mat_2x2 failed\n");
    }
    return (res);
}

// void ibz_mat_4x4_init(ibz_mat_4x4_t *mat);
int
quat_test_init_ibz_mat_4x4(void)
{
    ibz_mat_4x4_t mat;
    int res = 0;
    ibz_mat_4x4_init(&mat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++)
            res = res || !ibz_is_zero(&(mat.m[i][j]));
    }
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), i + j, 4);
        }
    }
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            res = res || (ibz_cmp_int32(&(mat.m[i][j]), i + j) != 0);
        }
    }
    if (res != 0) {
        printf("Quaternion unit test init_ibz_mat_4x4 failed\n");
    }
    return (res);
}

// void quat_lattice_init(quat_lattice_t *lat);
int
quat_test_init_lattice(void)
{
    quat_lattice_t lat;
    int res = 0;
    quat_lattice_init(&lat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++)
            res = res || !ibz_is_zero(&(lat.basis.m[i][j]));
    }
    res = res || !ibz_is_one(&(lat.denom));
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(lat.basis.m[i][j]), i + j, 4);
        }
    }
    ibz_set(&(lat.denom), 1, 2);
    res = res || !ibz_is_one(&(lat.denom));
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            res = res || (ibz_cmp_int32(&(lat.basis.m[i][j]), i + j) != 0);
        }
    }
    if (res != 0) {
        printf("Quaternion unit test init_alg_lattice failed\n");
    }
    return (res);
}

// void quat_ideal_init(quat_ideal_t *ideal)
int
quat_test_init_ideal()
{
    quat_ideal_t ideal;
    int res = 0;
    quat_ideal_init(&ideal);
    res = res || !ibz_is_zero(&ideal.norm);
    res = res || !ibz_is_zero(&ideal.x);
    res = res || !ibz_is_zero(&ideal.y);
    ibz_set(&(ideal.x), 1, 2);
    ibz_set(&(ideal.y), 2, 3);
    ibz_set(&(ideal.norm), 5, 4);

    res = res || (ibz_cmp_int32(&(ideal.norm), 5) != 0);
    res = res || (ibz_cmp_int32(&(ideal.x), 1) != 0);
    res = res || (ibz_cmp_int32(&(ideal.y), 2) != 0);
    if (res != 0) {
        printf("Quaternion unit test init_alg_ideal failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_init(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of initializers\n");
    res = res | quat_test_init_alg();
    res = res | quat_test_init_alg_elem();
    res = res | quat_test_init_ibz_vec_2();
    res = res | quat_test_init_ibz_vec_4();
    res = res | quat_test_init_ibz_mat_2x2();
    res = res | quat_test_init_ibz_mat_4x4();
    res = res | quat_test_init_lattice();
    res = res | quat_test_init_ideal();
    return (res);
}
