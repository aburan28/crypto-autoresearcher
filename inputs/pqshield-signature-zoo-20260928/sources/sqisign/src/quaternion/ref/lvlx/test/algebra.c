#include "quaternion_tests.h"

// tests of internal helper functions

// static inline void quat_alg_init_set_ui(quat_alg_t *alg, unsigned int p);
int
quat_test_init_set_ui(void)
{
    int res = 0;
    int p = 5;
    quat_alg_t alg;
    quat_alg_init_set_ui(&alg, p);
    res = res || (ibz_cmp_int32(&(alg.p), p) != 0);
    if (res != 0) {
        printf("Quaternion unit test alg_init_set_ui failed\n");
    }
    return (res);
}

// void quat_alg_coord_mul(ibz_vec_4_t *res, const ibz_vec_4_t *a, const ibz_vec_4_t *b, const quat_alg_t *alg);
int
quat_test_alg_coord_mul(void)
{
    int res = 0;
    quat_alg_t alg;
    quat_alg_init_set_ui(&alg, 7);
    ibz_vec_4_t a, b, c, cmp;
    ibz_vec_4_init(&a);
    ibz_vec_4_init(&b);
    ibz_vec_4_init(&c);
    ibz_vec_4_init(&cmp);

    ibz_vec_4_set(&a, 152, 57, 190, 28);
    ibz_vec_4_set(&b, 165, 35, 231, 770);
    ibz_vec_4_set(&cmp, -435065, 993549, 23552, 128177);
    quat_alg_coord_mul(&c, &a, &b, &alg);
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }
    ibz_set(&(alg.p), 11, 5);
    ibz_set(&(cmp.v[0]), -696865, 32);
    ibz_set(&(cmp.v[1]), 1552877, 32);
    quat_alg_coord_mul(&c, &a, &b, &alg);
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(c.v[i]), &(cmp.v[i]));
    }

    ibz_set(&(alg.p), 7, 4);
    ibz_vec_4_set(&a, 1, 1, 1, 1);
    ibz_vec_4_set(&cmp, -14, 2, 2, 2);
    quat_alg_coord_mul(&a, &a, &a, &alg);
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(a.v[i]), &(cmp.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_coord_mul failed\n");
    }
    return (res);
}

// void quat_alg_equal_denom(quat_alg_elem_t *res_a, quat_alg_elem_t *res_b, const quat_alg_elem_t
// *a, const quat_alg_elem_t *b);
int
quat_test_alg_equal_denom(void)
{
    int res = 0;
    quat_alg_elem_t a, b, res_a, res_b, cmp_a, cmp_b;
    quat_alg_elem_init(&a);
    quat_alg_elem_init(&b);
    quat_alg_elem_init(&res_a);
    quat_alg_elem_init(&res_b);
    quat_alg_elem_init(&cmp_a);
    quat_alg_elem_init(&cmp_b);

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 3, -6, 2, 67, -19);
    quat_alg_elem_set(&cmp_a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp_b, 9, -18, 6, 201, -57);
    quat_alg_equal_denom(&res_a, &res_b, &a, &b);
    res = res || ibz_cmp(&(res_a.denom), &(cmp_a.denom));
    res = res || ibz_cmp(&(res_b.denom), &(cmp_b.denom));
    res = res || ibz_cmp(&(cmp_a.denom), &(cmp_b.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(res_a.coord.v[i]), &(cmp_a.coord.v[i]));
        res = res || ibz_cmp(&(res_b.coord.v[i]), &(cmp_b.coord.v[i]));
    }

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 6, -6, 2, 67, -19);
    quat_alg_elem_set(&cmp_a, 18, -24, 0, -14, 38);
    quat_alg_elem_set(&cmp_b, 18, -18, 6, 201, -57);
    quat_alg_equal_denom(&res_a, &res_b, &a, &b);
    res = res || ibz_cmp(&(res_a.denom), &(cmp_a.denom));
    res = res || ibz_cmp(&(res_b.denom), &(cmp_b.denom));
    res = res || ibz_cmp(&(cmp_a.denom), &(cmp_b.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(res_a.coord.v[i]), &(cmp_a.coord.v[i]));
        res = res || ibz_cmp(&(res_b.coord.v[i]), &(cmp_b.coord.v[i]));
    }

    quat_alg_elem_set(&a, 6, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 6, -6, 2, 67, -19);
    quat_alg_elem_set(&cmp_a, 6, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp_b, 6, -6, 2, 67, -19);
    quat_alg_equal_denom(&res_a, &res_b, &a, &b);
    res = res || ibz_cmp(&(res_a.denom), &(cmp_a.denom));
    res = res || ibz_cmp(&(res_b.denom), &(cmp_b.denom));
    res = res || ibz_cmp(&(cmp_a.denom), &(cmp_b.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(res_a.coord.v[i]), &(cmp_a.coord.v[i]));
        res = res || ibz_cmp(&(res_b.coord.v[i]), &(cmp_b.coord.v[i]));
    }

    quat_alg_elem_set(&a, 6, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp_a, 6, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp_b, 6, -12, 0, -7, 19);
    quat_alg_equal_denom(&a, &b, &a, &a);
    res = res || ibz_cmp(&(a.denom), &(a.denom));
    res = res || ibz_cmp(&(b.denom), &(b.denom));
    res = res || ibz_cmp(&(cmp_a.denom), &(cmp_b.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(a.coord.v[i]), &(a.coord.v[i]));
        res = res || ibz_cmp(&(b.coord.v[i]), &(b.coord.v[i]));
    }
    if (res != 0) {
        printf("Quaternion unit test alg_equal_denom failed\n");
    }
    return (res);
}

// Tests of public functions

// void quat_alg_add(quat_alg_elem_t *res, const quat_alg_elem_t *a, const quat_alg_elem_t *b);
int
quat_test_alg_add(void)
{
    int res = 0;
    quat_alg_elem_t a, b, c, cmp;
    quat_alg_elem_init(&a);
    quat_alg_elem_init(&b);
    quat_alg_elem_init(&c);
    quat_alg_elem_init(&cmp);

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 3, -6, 2, 7, -19);
    quat_alg_elem_set(&cmp, 9, -30, 6, 14, -38);
    quat_alg_add(&c, &a, &b);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }
    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 6, -6, 2, 7, -19);
    quat_alg_elem_set(&cmp, 18, -42, 6, 7, -19);
    quat_alg_add(&c, &a, &b);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp, 9, -24, 0, -14, 38);
    quat_alg_add(&a, &a, &a);
    res = res || ibz_cmp(&(a.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(a.coord.v[i]), &(cmp.coord.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_add failed\n");
    }
    return (res);
}

// void quat_alg_sub(quat_alg_elem_t *res, const quat_alg_elem_t *a, const quat_alg_elem_t *b);
int
quat_test_alg_sub(void)
{
    int res = 0;
    quat_alg_elem_t a, b, c, cmp;
    quat_alg_elem_init(&a);
    quat_alg_elem_init(&b);
    quat_alg_elem_init(&c);
    quat_alg_elem_init(&cmp);

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 3, -6, 2, 7, -19);
    quat_alg_elem_set(&cmp, 9, -12 - 3 * (-6), -3 * 2, -7 - 3 * 7, 19 - 3 * (-19));
    quat_alg_sub(&c, &a, &b);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&b, 6, -6, 2, 7, -19);
    quat_alg_elem_set(&cmp, 18, -2 * 12 - 3 * (-6), -3 * 2, -2 * 7 - 3 * 7, 2 * 19 - 3 * (-19));
    quat_alg_sub(&a, &a, &b);
    res = res || ibz_cmp(&(a.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(a.coord.v[i]), &(cmp.coord.v[i]));
    }

    quat_alg_elem_set(&a, 9, -12, 0, -7, 19);
    quat_alg_elem_set(&cmp, 9, 0, 0, 0, 0);
    quat_alg_sub(&a, &a, &a);
    res = res || ibz_cmp(&(a.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(a.coord.v[i]), &(cmp.coord.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_sub failed\n");
    }
    return (res);
}

// void quat_alg_mul(quat_alg_elem_t *res, const quat_alg_elem_t *a, const quat_alg_elem_t *b, const quat_alg_t *alg);
int
quat_test_alg_mul(void)
{
    int res = 0;
    quat_alg_t alg;
    quat_alg_init_set_ui(&alg, 7);
    quat_alg_elem_t a, b, c, cmp;
    quat_alg_elem_init(&a);
    quat_alg_elem_init(&b);
    quat_alg_elem_init(&c);
    quat_alg_elem_init(&cmp);

    quat_alg_elem_set(&a, 76, 152, 57, 190, 28);
    quat_alg_elem_set(&b, 385, 165, 35, 231, 770);
    quat_alg_elem_set(&cmp, 29260, -435065, 993549, 23552, 128177);
    quat_alg_mul(&c, &a, &b, &alg);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }
    ibz_set(&(alg.p), 11, 5);
    ibz_set(&(cmp.coord.v[0]), -696865, 32);
    ibz_set(&(cmp.coord.v[1]), 1552877, 32);
    ibz_set(&(cmp.denom), 29260, 32);
    quat_alg_mul(&c, &a, &b, &alg);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }

    ibz_set(&(alg.p), 7, 4);
    quat_alg_elem_set(&a, 2, 1, 1, 1, 1);
    quat_alg_elem_set(&cmp, 4, -14, 2, 2, 2);
    quat_alg_mul(&c, &a, &a, &alg);
    res = res || ibz_cmp(&(c.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(c.coord.v[i]), &(cmp.coord.v[i]));
    }

    ibz_set(&(alg.p), 7, 4);
    quat_alg_elem_set(&a, 2, 1, 1, 1, 1);
    quat_alg_elem_set(&cmp, 4, -14, 2, 2, 2);
    quat_alg_mul(&a, &a, &a, &alg);
    res = res || ibz_cmp(&(a.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(a.coord.v[i]), &(cmp.coord.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_mul failed\n");
    }
    return (res);
}

// void quat_alg_norm(quat_alg_elem_t *res, const quat_alg_elem_t *a, const quat_alg_t *alg);
int
quat_test_alg_norm(void)
{
    int res = 0;
    quat_alg_t alg;
    quat_alg_init_set_ui(&alg, 11);
    quat_alg_elem_t a;
    ibz_t num, denom, cmp_num, cmp_denom;
    quat_alg_elem_init(&a);
    ibz_init(&num);
    ibz_init(&denom);
    ibz_init(&cmp_num);
    ibz_init(&cmp_denom);

    ibz_set(&(alg.p), 11, 5);
    quat_alg_elem_set(&a, 2, 1, 5, 7, 2);
    ibz_set(&cmp_num, 609, 11);
    ibz_set(&cmp_denom, 4, 4);
    quat_alg_norm(&num, &denom, &a, &alg);
    res = res || (ibz_cmp(&num, &cmp_num));
    res = res || (ibz_cmp(&denom, &cmp_denom));

    // same vector, not reduced
    ibz_set(&(alg.p), 11, 5);
    quat_alg_elem_set(&a, 4, 2, 10, 14, 4);
    ibz_set(&cmp_num, 609, 11);
    ibz_set(&cmp_denom, 4, 4);
    quat_alg_norm(&num, &denom, &a, &alg);
    res = res || (ibz_cmp(&num, &cmp_num));
    res = res || (ibz_cmp(&denom, &cmp_denom));

    ibz_set(&(alg.p), 11, 5);
    quat_alg_elem_set(&a, 76, 152, 57, 190, 28);
    ibz_set(&cmp_num, 432077, 32);
    ibz_set(&cmp_denom, 5776, 16);
    quat_alg_norm(&num, &denom, &a, &alg);
    res = res || (ibz_cmp(&num, &cmp_num));
    res = res || (ibz_cmp(&denom, &cmp_denom));

    ibz_set(&(alg.p), 11, 5);
    quat_alg_elem_set(&a, 28, 0, 12, 35, 49);
    ibz_set(&cmp_num, 20015, 32);
    ibz_set(&cmp_denom, 392, 10);
    quat_alg_norm(&num, &denom, &a, &alg);
    res = res || (ibz_cmp(&num, &cmp_num));
    res = res || (ibz_cmp(&denom, &cmp_denom));

    ibz_set(&(alg.p), 7, 4);
    quat_alg_elem_set(&a, 76, 152, 57, 190, 28);
    ibz_set(&cmp_num, 284541, 26);
    ibz_set(&cmp_denom, 5776, 16);
    quat_alg_norm(&num, &denom, &a, &alg);
    res = res || (ibz_cmp(&num, &cmp_num));
    res = res || (ibz_cmp(&denom, &cmp_denom));

    if (res != 0) {
        printf("Quaternion unit test alg_norm failed\n");
    }
    return (res);
}

// void quat_alg_scalar(quat_alg_elem_t *elem, const ibz_t *numerator, const ibz_t *denominator);
int
quat_test_alg_scalar(void)
{
    int res = 0;
    quat_alg_elem_t elem, cmp;
    ibz_t denom, num;
    quat_alg_elem_init(&cmp);
    quat_alg_elem_init(&elem);
    ibz_init(&num);
    ibz_init(&denom);

    ibz_set(&num, 1, 2);
    ibz_set(&denom, 1, 2);
    quat_alg_elem_set(&cmp, 1, 1, 0, 0, 0);
    quat_alg_scalar(&elem, &num, &denom);
    res = res || ibz_cmp(&(elem.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(elem.coord.v[i]), &(cmp.coord.v[i]));
    }

    ibz_set(&num, 5, 4);
    ibz_set(&denom, 9, 5);
    quat_alg_elem_set(&cmp, 9, 5, 0, 0, 0);
    quat_alg_scalar(&elem, &num, &denom);
    res = res || ibz_cmp(&(elem.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(elem.coord.v[i]), &(cmp.coord.v[i]));
    }

    ibz_set(&num, -125, 8);
    ibz_set(&denom, 25, 6);
    quat_alg_elem_set(&cmp, 25, -125, 0, 0, 0);
    quat_alg_scalar(&elem, &num, &denom);
    res = res || ibz_cmp(&(elem.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(elem.coord.v[i]), &(cmp.coord.v[i]));
    }
    if (res != 0) {
        printf("Quaternion unit test alg_scalar failed\n");
    }
    return (res);
}

// void quat_alg_conj(quat_alg_elem_t *conj, const quat_alg_elem_t *x);
int
quat_test_alg_conj(void)
{
    int res = 0;
    quat_alg_elem_t a, conj, cmp;
    quat_alg_elem_init(&cmp);
    quat_alg_elem_init(&conj);
    quat_alg_elem_init(&a);

    quat_alg_elem_set(&a, 25, 0, 0, 0, 7);
    quat_alg_elem_set(&cmp, 25, 0, 0, 0, -7);

    quat_alg_conj(&conj, &a);
    res = res || ibz_cmp(&(conj.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(conj.coord.v[i]), &(cmp.coord.v[i]));
    }
    quat_alg_elem_set(&a, 25, -125, 2, 0, -30);
    quat_alg_elem_set(&cmp, 25, -125, -2, 0, 30);
    quat_alg_conj(&conj, &a);
    res = res || ibz_cmp(&(conj.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(conj.coord.v[i]), &(cmp.coord.v[i]));
    }
    if (res != 0) {
        printf("Quaternion unit test alg_conj failed\n");
    }
    return (res);
}

// void quat_alg_make_primitive(quat_alg_coord_t *primitive_x, ibz_t *content, const quat_alg_elem_t
// *x, const quat_lattice_t *order, const quat_alg_t *alg);
int
quat_test_alg_make_primitive(void)
{
    int res = 0;
    quat_alg_elem_t x;
    quat_alg_t alg;
    quat_lattice_t order;
    ibz_vec_4_t prim, x_coord_in_order;
    ibz_t cmp_cnt, cnt;
    quat_alg_elem_init(&x);
    quat_alg_init_set_ui(&alg, 19);
    ibz_vec_4_init(&x_coord_in_order);
    ibz_vec_4_init(&prim);
    quat_lattice_init(&order);
    ibz_init(&cmp_cnt);
    ibz_init(&cnt);
    quat_alg_elem_set(&x, 1, 0, 0, 0, 0);
    ibz_mat_4x4_zero(&order.basis);
    ibz_set(&order.denom, 1, 2);

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(order.basis.m[i][j]), 0, 0);
        }
    }
    ibz_set(&(order.basis.m[0][0]), 1, 2);
    ibz_set(&(order.basis.m[1][1]), 2, 3);
    ibz_set(&(order.basis.m[2][2]), 1, 2);
    ibz_set(&(order.basis.m[3][3]), 3, 3);
    ibz_set(&(order.denom), 6, 4);
    // x=1, should succeed if order
    // is it an order?
    res = res || (0 == quat_lattice_contains(&prim, &order, &x));

    // actual test
    quat_alg_elem_set(&x, 6, 2, -4, 26, 18);

    res = res || (0 == quat_lattice_contains(&x_coord_in_order, &order, &x));
    ibz_vec_4_content(&cmp_cnt, &x_coord_in_order);
    quat_alg_make_primitive(&prim, &cnt, &x, &order);
    res = res || ibz_cmp(&cnt, &cmp_cnt);
    ibz_vec_4_content(&cmp_cnt, &prim);
    res = res || !ibz_is_one(&cmp_cnt);
    // multiply by cnt, and compare to x in order
    // assumes contains is correct
    for (int i = 0; i < 4; i++) {
        ibz_mul(&cmp_cnt, &cnt, &(prim.v[i]));
        res = res || ibz_cmp(&cmp_cnt, &(x_coord_in_order.v[i]));
    }

    // on a primitive element
    quat_alg_elem_set(&x, 6, 2, -4, 5, 18);

    res = res || (0 == quat_lattice_contains(&x_coord_in_order, &order, &x));
    ibz_vec_4_content(&cmp_cnt, &x_coord_in_order);
    quat_alg_make_primitive(&prim, &cnt, &x, &order);
    res = res || ibz_cmp(&cnt, &cmp_cnt);
    ibz_vec_4_content(&cmp_cnt, &prim);
    res = res || !ibz_is_one(&cmp_cnt);
    // this x is is primitive, so cnt should be 1
    res = res || !ibz_is_one(&cnt);
    // multiply by cnt, and compare to x in order
    // assumes contains is correct
    for (int i = 0; i < 4; i++) {
        ibz_mul(&cmp_cnt, &cnt, &(prim.v[i]));
        res = res || ibz_cmp(&cmp_cnt, &(x_coord_in_order.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_make_primitive failed\n");
    }
    return (res);
}

// void quat_alg_normalize(quat_alg_elem_t *x);
int
quat_test_alg_normalize(void)
{
    int res = 0;
    quat_alg_elem_t x, cmp;
    ibz_t gcd;
    quat_alg_elem_init(&x);
    quat_alg_elem_init(&cmp);
    ibz_init(&gcd);

    // sign change
    quat_alg_elem_set(&x, -25, -125, 2, 0, -30);
    quat_alg_elem_set(&cmp, 25, 125, -2, 0, 30);
    quat_alg_normalize(&x);
    res = res || ibz_cmp(&(x.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(x.coord.v[i]), &(cmp.coord.v[i]));
    }
    // divide by gcd
    quat_alg_elem_set(&x, 48, -36, 18, 0, -300);
    quat_alg_elem_set(&cmp, 8, -6, 3, 0, -50);
    quat_alg_normalize(&x);
    res = res || ibz_cmp(&(x.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(x.coord.v[i]), &(cmp.coord.v[i]));
    }
    // divide by gcd
    quat_alg_elem_set(&x, -6, -36, 18, 0, -300);
    quat_alg_elem_set(&cmp, 1, 6, -3, 0, 50);
    quat_alg_normalize(&x);
    res = res || ibz_cmp(&(x.denom), &(cmp.denom));
    for (int i = 0; i < 4; i++) {
        ;
        res = res || ibz_cmp(&(x.coord.v[i]), &(cmp.coord.v[i]));
    }

    if (res != 0) {
        printf("Quaternion unit test alg_normalize failed\n");
    }
    return (res);
}

// int quat_alg_elem_equal(const quat_alg_elem_t *a, const quat_alg_elem_t *b);
int
quat_test_alg_elem_equal(void)
{
    int res = 0;
    quat_alg_elem_t a, b;
    quat_alg_elem_init(&a);
    quat_alg_elem_init(&b);
    ibz_vec_4_set(&(a.coord), 1, -3, -2, 2);
    ibz_set(&(a.denom), 5, 4);
    ibz_vec_4_set(&(b.coord), 3, -9, -6, 6);
    ibz_set(&(b.denom), 15, 5);
    res = res || !quat_alg_elem_equal(&a, &b);
    res = res || !quat_alg_elem_equal(&a, &a);
    res = res || !quat_alg_elem_equal(&b, &b);
    ibz_vec_4_set(&(a.coord), 1, -3, -2, 2);
    ibz_set(&(a.denom), 5, 4);
    ibz_vec_4_set(&(b.coord), 3, -9, -6, 3);
    ibz_set(&(b.denom), 15, 5);
    res = res || quat_alg_elem_equal(&a, &b);
    ibz_vec_4_set(&(a.coord), 5, -15, -10, 10);
    ibz_set(&(a.denom), 25, 6);
    ibz_vec_4_set(&(b.coord), 3, -9, -6, 6);
    ibz_set(&(b.denom), 15, 5);
    res = res || !quat_alg_elem_equal(&a, &b);
    ibz_vec_4_set(&(a.coord), 5, -15, -10, 10);
    ibz_set(&(a.denom), 25, 6);
    ibz_vec_4_set(&(b.coord), 0, -9, -6, 6);
    ibz_set(&(b.denom), 5, 4);
    res = res || quat_alg_elem_equal(&a, &b);
    if (res != 0) {
        printf("Quaternion unit test alg_elem_equal failed\n");
    }
    return (res);
}

// int quat_alg_elem_is_zero(const quat_alg_elem_t *x);
int
quat_test_alg_elem_is_zero(void)
{
    int res = 0;
    quat_alg_elem_t x;
    quat_alg_elem_init(&x);
    quat_alg_elem_set(&x, 1, 0, 0, 0, 0);
    res = res | (1 - quat_alg_elem_is_zero(&x));
    ibz_set(&(x.denom), 56865, 20);
    res = res | (1 - quat_alg_elem_is_zero(&x));
    ibz_set(&(x.denom), 0, 0);
    // maybe failure should be accepted here, but according to doc, this is still 0
    res = res | (1 - quat_alg_elem_is_zero(&x));
    ibz_set(&(x.coord.v[3]), 1, 2);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.denom), 56865, 20);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[3]), -1, 2);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[2]), 1, 2);
    ibz_set(&(x.coord.v[3]), 0, 0);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[2]), -20, 6);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[1]), 1, 2);
    ibz_set(&(x.coord.v[2]), 0, 0);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[1]), -50000, 20);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[0]), 1, 2);
    ibz_set(&(x.coord.v[1]), 0, 0);
    res = res | quat_alg_elem_is_zero(&x);
    ibz_set(&(x.coord.v[0]), -90000, 22);
    res = res | quat_alg_elem_is_zero(&x);
    quat_alg_elem_set(&x, 1, 0, -500, 20, 0);
    res = res | quat_alg_elem_is_zero(&x);
    quat_alg_elem_set(&x, 1, 19, -500, 20, -2);
    res = res | quat_alg_elem_is_zero(&x);
    if (res != 0) {
        printf("Quaternion unit test alg_elem_is_zero failed\n");
    }
    return (res);
}

// void quat_alg_elem_set(quat_alg_elem_t *elem, int32_t denom, int32_t coord0, int32_t coord1, int32_t coord2, int32_t
// coord3)
int
quat_test_alg_elem_set(void)
{
    int res = 0;
    quat_alg_elem_t elem;
    quat_alg_elem_init(&elem);
    quat_alg_elem_set(&elem, 5, 1, 2, 3, 4);
    res = res || (ibz_cmp_int32(&(elem.coord.v[0]), 1) != 0);
    res = res || (ibz_cmp_int32(&(elem.coord.v[1]), 2) != 0);
    res = res || (ibz_cmp_int32(&(elem.coord.v[2]), 3) != 0);
    res = res || (ibz_cmp_int32(&(elem.coord.v[3]), 4) != 0);
    res = res || (ibz_cmp_int32(&(elem.denom), 5) != 0);

    if (res != 0) {
        printf("Quaternion unit test alg_elem_set failed\n");
    }
    return (res);
}

// void quat_alg_elem_copy(quat_alg_elem_t *copy, const quat_alg_elem_t *copied);
int
quat_test_alg_elem_copy()
{
    int res = 0;
    quat_alg_elem_t elem, copy;
    quat_alg_elem_init(&elem);
    quat_alg_elem_init(&copy);
    quat_alg_elem_set(&elem, 7, -2, 9, 2091, 21);
    quat_alg_elem_copy(&copy, &elem);
    res = res || !quat_alg_elem_equal(&elem, &copy);
    quat_alg_elem_set(&elem, 3, -6, 9, 2091, 21);
    quat_alg_elem_copy(&copy, &elem);
    res = res || !quat_alg_elem_equal(&elem, &copy);
    if (res) {
        printf("Quaternion unit test alg_elem_copy failed\n");
    }
    return (res);
}

// void quat_alg_elem_copy_ibz(quat_alg_elem_t *elem, const ibz_t *denom, const ibz_t *coord0, const ibz_t *coord1,
// const ibz_t *coord2,const ibz_t *coord3){
int
quat_test_alg_elem_copy_ibz(void)
{
    int res = 0;
    ibz_t a, b, c, d, q;
    quat_alg_elem_t elem;
    quat_alg_elem_init(&elem);
    ibz_init(&a);
    ibz_init(&b);
    ibz_init(&c);
    ibz_init(&d);
    ibz_init(&q);
    ibz_set(&a, 1, 2);
    ibz_set(&b, 2, 3);
    ibz_set(&c, 3, 3);
    ibz_set(&d, 4, 4);
    ibz_set(&q, 5, 4);
    quat_alg_elem_copy_ibz(&elem, &q, &a, &b, &c, &d);
    res = res || ibz_cmp(&(elem.coord.v[0]), &a);
    res = res || ibz_cmp(&(elem.coord.v[1]), &b);
    res = res || ibz_cmp(&(elem.coord.v[2]), &c);
    res = res || ibz_cmp(&(elem.coord.v[3]), &d);
    res = res || ibz_cmp(&(elem.denom), &q);

    if (res != 0) {
        printf("Quaternion unit test alg_elem_copy_ibz failed\n");
    }
    return (res);
}

// void quat_alg_scalar_mul(quat_alg_elem_t *prod, const ibz_t *scalar, const quat_alg_elem_t *elem);
int
quat_test_alg_elem_scalar_mul(void)
{
    int res = 0;
    ibz_t scalar;
    quat_alg_elem_t elem, cmp, prod;
    ibz_init(&scalar);
    quat_alg_elem_init(&elem);
    quat_alg_elem_init(&prod);
    quat_alg_elem_init(&cmp);

    ibz_set(&scalar, 6, 4);
    quat_alg_elem_set(&elem, 2, 2, -4, 5, 25);
    quat_alg_elem_set(&cmp, 2, 12, -24, 30, 150);

    quat_alg_elem_scalar_mul(&prod, &scalar, &elem);
    res = res || ibz_cmp(&(prod.coord.v[0]), &(cmp.coord.v[0]));
    res = res || ibz_cmp(&(prod.coord.v[1]), &(cmp.coord.v[1]));
    res = res || ibz_cmp(&(prod.coord.v[2]), &(cmp.coord.v[2]));
    res = res || ibz_cmp(&(prod.coord.v[3]), &(cmp.coord.v[3]));
    res = res || ibz_cmp(&(prod.denom), &(cmp.denom));
    // denom should not be modified
    res = res || ibz_cmp(&(prod.denom), &(elem.denom));

    ibz_set(&scalar, -3, 3);
    quat_alg_elem_set(&cmp, 2, -6, 12, -15, -75);

    quat_alg_elem_scalar_mul(&prod, &scalar, &elem);
    res = res || ibz_cmp(&(prod.coord.v[0]), &(cmp.coord.v[0]));
    res = res || ibz_cmp(&(prod.coord.v[1]), &(cmp.coord.v[1]));
    res = res || ibz_cmp(&(prod.coord.v[2]), &(cmp.coord.v[2]));
    res = res || ibz_cmp(&(prod.coord.v[3]), &(cmp.coord.v[3]));
    res = res || ibz_cmp(&(prod.denom), &(cmp.denom));

    if (res != 0) {
        printf("Quaternion unit test alg_elem_scalar_mul failed\n");
    }
    return (res);
}

// run all previous tests
int
quat_test_algebra(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of algebra operations\n");
    res = res | quat_test_init_set_ui();
    res = res | quat_test_alg_coord_mul();
    res = res | quat_test_alg_equal_denom();
    res = res | quat_test_alg_add();
    res = res | quat_test_alg_sub();
    res = res | quat_test_alg_mul();
    res = res | quat_test_alg_norm();
    res = res | quat_test_alg_scalar();
    res = res | quat_test_alg_conj();
    res = res | quat_test_alg_make_primitive();
    res = res | quat_test_alg_normalize();
    res = res | quat_test_alg_elem_equal();
    res = res | quat_test_alg_elem_is_zero();
    res = res | quat_test_alg_elem_set();
    res = res | quat_test_alg_elem_copy_ibz();
    res = res | quat_test_alg_elem_copy();
    res = res | quat_test_alg_elem_scalar_mul();
    return (res);
}
