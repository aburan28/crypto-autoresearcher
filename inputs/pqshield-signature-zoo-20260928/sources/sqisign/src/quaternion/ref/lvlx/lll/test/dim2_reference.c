#include "internal.h"
#include "lll_test_internals.h"
#include <stdio.h>

// enumerate in dim 2

// helper for cvp
int
quat_dim2_lattice_contains(const ibz_mat_2x2_t *basis, const ibz_t *coord1, const ibz_t *coord2)
{
    int res = 1;
    ibz_t prod, sum, det, r;
    ibz_init(&det);
    ibz_init(&r);
    ibz_init(&sum);
    ibz_init(&prod);
    // compute det, then both coordinates (inverse*det)*vec, where vec is (coord1, coord2) and check wthether det
    // divides both results
    ibz_mat_2x2_det_from_ibz(&det, &basis->m[0][0], &basis->m[0][1], &basis->m[1][0], &basis->m[1][1]);
    ibz_mul(&sum, coord1, &basis->m[1][1]);
    ibz_mul(&prod, coord2, &basis->m[0][1]);
    ibz_sub(&sum, &sum, &prod);
    ibz_div(&prod, &r, &sum, &det);
    res = res & ibz_is_zero(&r);
    ibz_mul(&sum, coord2, &basis->m[0][0]);
    ibz_mul(&prod, coord1, &basis->m[1][0]);
    ibz_sub(&sum, &sum, &prod);
    ibz_div(&prod, &r, &sum, &det);
    res = res & ibz_is_zero(&r);
    return (res);
}

void
quat_dim2_lattice_norm(ibz_t *norm, const ibz_t *coord1, const ibz_t *coord2)
{
    ibz_t prod, sum;
    ibz_init(&prod);
    ibz_init(&sum);
    ibz_mul(&sum, coord1, coord1);
    ibz_mul(&prod, coord2, coord2);
    ibz_add(norm, &sum, &prod);
}

void
quat_dim2_lattice_bilinear(ibz_t *res, const ibz_t *v11, const ibz_t *v12, const ibz_t *v21, const ibz_t *v22)
{
    ibz_t prod, sum;
    ibz_init(&prod);
    ibz_init(&sum);
    ibz_mul(&sum, v11, v21);
    ibz_mul(&prod, v12, v22);
    ibz_add(res, &sum, &prod);
}

// algo 3.1.14 Cohen (exact solution for shortest vector in dimension 2, then take a second, orthogonal vector)
void
quat_dim2_lattice_short_basis(ibz_mat_2x2_t *reduced, const ibz_mat_2x2_t *basis)
{
    ibz_vec_2_t a, b, t;
    ibz_t prod, sum, norm_a, norm_b, r, norm_t, n;
    ibz_vec_2_init(&a);
    ibz_vec_2_init(&b);
    ibz_vec_2_init(&t);
    ibz_init(&prod);
    ibz_init(&sum);
    ibz_init(&r);
    ibz_init(&n);
    ibz_init(&norm_t);
    ibz_init(&norm_a);
    ibz_init(&norm_b);
    // init a,b
    ibz_copy(&(a.v[0]), &(basis->m[0][0]));
    ibz_copy(&(a.v[1]), &(basis->m[1][0]));
    ibz_copy(&(b.v[0]), &(basis->m[0][1]));
    ibz_copy(&(b.v[1]), &(basis->m[1][1]));
    // compute initial norms
    quat_dim2_lattice_norm(&norm_a, &(a.v[0]), &(a.v[1]));
    quat_dim2_lattice_norm(&norm_b, &(b.v[0]), &(b.v[1]));
    // exchange if needed
    if (ibz_cmp(&norm_a, &norm_b) < 0) {
        ibz_copy(&sum, &(a.v[0]));
        ibz_copy(&(a.v[0]), &(b.v[0]));
        ibz_copy(&(b.v[0]), &sum);
        ibz_copy(&sum, &(a.v[1]));
        ibz_copy(&(a.v[1]), &(b.v[1]));
        ibz_copy(&(b.v[1]), &sum);
        ibz_copy(&sum, &norm_a);
        ibz_copy(&norm_a, &norm_b);
        ibz_copy(&norm_b, &sum);
    }
    ibz_set(&n, 0, 0);
    // this is still too big, but for now it doesn't trigger a problem
    int bound = 10 + ibz_get_bound(&norm_b);
    while (1) {
        ibz_set_bound(&n, bound); // to avoid a blow-up in the bound which will only be decreasing in practice
        ibz_set_bound(&norm_b, bound);
        ibz_set_bound(&(a.v[0]), bound);
        ibz_set_bound(&(a.v[1]), bound);
        ibz_set_bound(&(b.v[0]), bound);
        ibz_set_bound(&(b.v[1]), bound);

        // compute n
        quat_dim2_lattice_bilinear(&n, &(a.v[0]), &(a.v[1]), &(b.v[0]), &(b.v[1]));
        // set r
        // this is not very accurate, but the values are decreasing anyway to it will be okay
        ibz_rounded_div(&r, &n, &norm_b);
        ibz_set_bound(&r, bound / 2);
        // compute t_norm
        ibz_set(&prod, 2, 3);
        ibz_mul(&prod, &prod, &n);
        ibz_mul(&prod, &prod, &r);
        ibz_sub(&sum, &norm_a, &prod);
        ibz_mul(&prod, &r, &r);
        ibz_mul(&prod, &prod, &norm_b);
        ibz_add(&norm_t, &sum, &prod);
        // test:
        if (ibz_cmp(&norm_b, &norm_t) > 0) {
            // compute t, a, b
            ibz_copy(&norm_a, &norm_b);
            ibz_copy(&norm_b, &norm_t);
            // t is a -rb, a is b, b is t
            ibz_mul(&prod, &r, &(b.v[0]));
            ibz_sub(&(t.v[0]), &(a.v[0]), &prod);
            ibz_mul(&prod, &r, &(b.v[1]));
            ibz_sub(&(t.v[1]), &(a.v[1]), &prod);
            ibz_copy(&(a.v[0]), &(b.v[0]));
            ibz_copy(&(a.v[1]), &(b.v[1]));
            ibz_copy(&(b.v[0]), &(t.v[0]));
            ibz_copy(&(b.v[1]), &(t.v[1]));
            ibz_set_bound(&a.v[0], ibz_bitsize(&a.v[0]) + 1);
            ibz_set_bound(&a.v[1], ibz_bitsize(&a.v[1]) + 1);
            ibz_set_bound(&b.v[0], ibz_bitsize(&b.v[0]) + 1);
            ibz_set_bound(&b.v[1], ibz_bitsize(&b.v[1]) + 1);
        } else {
            break;
        }
    }
    // output : now b is short: need to get 2nd short vector: idea: take shortest among t and a
    if (ibz_cmp(&norm_t, &norm_a) < 0) {
        ibz_mul(&prod, &r, &(b.v[0]));
        ibz_sub(&(a.v[0]), &(a.v[0]), &prod);
        ibz_mul(&prod, &r, &(b.v[1]));
        ibz_sub(&(a.v[1]), &(a.v[1]), &prod);
    }
    ibz_copy(&(reduced->m[0][0]), &(b.v[0]));
    ibz_copy(&(reduced->m[1][0]), &(b.v[1]));
    ibz_copy(&(reduced->m[0][1]), &(a.v[0]));
    ibz_copy(&(reduced->m[1][1]), &(a.v[1]));
}
