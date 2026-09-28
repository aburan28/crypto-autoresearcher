#include "quaternion_tests.h"
#include <stdlib.h>
#include <assert.h>
#include "lll_test_internals.h"
#include <lll.h>
#include "../lll_config.h"

// cvp helper functions

// int quat_dim2_lattice_contains(ibz_mat_2x2_t *basis, ibz_t *coord1, ibz_t *coord2);
static int
quat_test_lll_dim2_lattice_contains()
{
    int res = 0;
    ibz_mat_2x2_t basis;
    ibz_t c1, c2;
    ibz_mat_2x2_init(&basis);
    ibz_init(&c1);
    ibz_init(&c2);
    ibz_mat_2x2_set(&basis, -1, 2, 5, 0);
    ibz_set(&c1, 0, 0);
    ibz_set(&c2, 0, 0);
    res = res || !quat_dim2_lattice_contains(&basis, &c1, &c2);
    ibz_set(&c1, 1, 2);
    ibz_set(&c2, 5, 4);
    res = res || !quat_dim2_lattice_contains(&basis, &c1, &c2);
    ibz_set(&c1, 1, 2);
    ibz_set(&c2, 4, 4);
    res = res || quat_dim2_lattice_contains(&basis, &c1, &c2);

    if (res != 0) {
        printf("Quaternion unit test lll_dim2_lattice_contains failed\n");
    }
    return (res);
}

// void quat_dim2_lattice_norm(ibz_t *norm, const ibz_t *coord1, const ibz_t *coord2, const ibz_t *norm_q)
static int
quat_test_lll_dim2_lattice_norm()
{
    int res = 0;
    ibz_t norm, cmp, a, b;
    ibz_init(&a);
    ibz_init(&b);
    ibz_init(&norm);
    ibz_init(&cmp);
    ibz_set(&a, 1, 2);
    ibz_set(&b, 2, 3);
    ibz_set(&cmp, 1 * 1 + 2 * 2, 4);
    quat_dim2_lattice_norm(&norm, &a, &b);
    res = res || ibz_cmp(&norm, &cmp);
    ibz_set(&a, 7, 4);
    ibz_set(&b, -2, 3);
    ibz_set(&cmp, 7 * 7 + 2 * 2, 8);
    quat_dim2_lattice_norm(&norm, &a, &b);
    res = res || ibz_cmp(&norm, &cmp);
    ibz_set(&cmp, 7 * 7 + 7 * 7, 8);
    quat_dim2_lattice_norm(&a, &a, &a);
    res = res || ibz_cmp(&a, &cmp);
    if (res != 0) {
        printf("Quaternion unit test lll_dim2_lattice_norm failed\n");
    }
    return (res);
}

// void quat_dim2_lattice_bilinear(ibz_t *res, const ibz_t *v11, const ibz_t *v12,const ibz_t *v21, const ibz_t *v22,
// const ibz_t *norm_q);
static int
quat_test_lll_dim2_lattice_bilinear()
{
    int res = 0;
    ibz_t prod, cmp, a, b, c, d;
    ibz_init(&a);
    ibz_init(&b);
    ibz_init(&c);
    ibz_init(&d);
    ibz_init(&prod);
    ibz_init(&cmp);
    ibz_set(&a, 1, 2);
    ibz_set(&b, 2, 3);
    ibz_set(&c, 3, 3);
    ibz_set(&d, 4, 4);
    ibz_set(&cmp, 1 * 3 + 2 * 4, 5);
    quat_dim2_lattice_bilinear(&prod, &a, &b, &c, &d);
    res = res || ibz_cmp(&prod, &cmp);
    ibz_set(&a, 7, 4);
    ibz_set(&b, -2, 3);
    ibz_set(&c, 4, 4);
    ibz_set(&d, 7, 4);
    ibz_set(&cmp, 7 * 4 - 2 * 7, 7);
    quat_dim2_lattice_bilinear(&prod, &a, &b, &c, &d);
    res = res || ibz_cmp(&prod, &cmp);
    ibz_set(&cmp, 7 * 7 + 7 * 7, 8);
    quat_dim2_lattice_bilinear(&a, &a, &a, &a, &a);
    res = res || ibz_cmp(&a, &cmp);
    if (res != 0) {
        printf("Quaternion unit test lll_dim2_lattice_bilinear failed\n");
    }
    return (res);
}

// according to conditions from https://cseweb.ucsd.edu/classes/wi12/cse206A-a/lec3.pdf
static int
quat_dim2_lattice_verify_lll(const ibz_mat_2x2_t *mat)
{
    ibz_t prod, norm_a, norm_bstar, norm_b, b_ab, b_abstar, b_bbstar, p01_denom, p00_denom, norm_p00, norm_p01;
    ibz_vec_2_t p00, p01, bstar;
    ibz_vec_2_init(&p00);
    ibz_vec_2_init(&p01);
    ibz_vec_2_init(&bstar);
    ibz_init(&prod);
    ibz_init(&norm_a);
    ibz_init(&norm_bstar);
    ibz_init(&norm_b);
    ibz_init(&b_ab);
    ibz_init(&b_bbstar);
    ibz_init(&b_abstar);
    ibz_init(&p00_denom);
    ibz_init(&p01_denom);
    ibz_init(&norm_p00);
    ibz_init(&norm_p01);
    quat_dim2_lattice_norm(&norm_a, &(mat->m[0][0]), &(mat->m[1][0]));
    quat_dim2_lattice_norm(&norm_b, &(mat->m[0][1]), &(mat->m[1][1]));
    quat_dim2_lattice_bilinear(&b_ab, &(mat->m[0][0]), &(mat->m[1][0]), &(mat->m[0][1]), &(mat->m[1][1]));
    ibz_mul(&(bstar.v[0]), &(mat->m[0][1]), &norm_b);
    ibz_mul(&prod, &(mat->m[0][0]), &b_ab);
    ibz_sub(&(bstar.v[0]), &(bstar.v[0]), &prod);
    ibz_mul(&(bstar.v[1]), &(mat->m[1][1]), &norm_b);
    ibz_mul(&prod, &(mat->m[1][0]), &b_ab);
    ibz_sub(&(bstar.v[1]), &(bstar.v[1]), &prod);
    quat_dim2_lattice_norm(&norm_bstar, &(bstar.v[0]), &(bstar.v[1]));
    quat_dim2_lattice_bilinear(&b_bbstar, &(bstar.v[0]), &(bstar.v[1]), &(mat->m[0][1]), &(mat->m[1][1]));
    quat_dim2_lattice_bilinear(&b_abstar, &(mat->m[0][0]), &(mat->m[1][0]), &(bstar.v[0]), &(bstar.v[1]));
    // first projection
    ibz_mul(&(p00.v[0]), &(mat->m[0][0]), &norm_bstar);
    ibz_mul(&prod, &(bstar.v[0]), &b_abstar);
    ibz_add(&(p00.v[0]), &(p00.v[0]), &prod);
    ibz_mul(&(p00.v[1]), &(mat->m[1][0]), &norm_bstar);
    ibz_mul(&prod, &(bstar.v[1]), &b_abstar);
    ibz_add(&(p00.v[1]), &(p00.v[1]), &prod);
    ibz_copy(&p00_denom, &norm_bstar);
    // second projection
    ibz_mul(&(p01.v[0]), &(mat->m[0][0]), &b_ab);
    ibz_mul(&(p01.v[0]), &(p01.v[0]), &norm_bstar);
    ibz_mul(&prod, &(bstar.v[0]), &b_bbstar);
    ibz_mul(&prod, &prod, &norm_a);
    ibz_add(&(p01.v[0]), &(p01.v[0]), &prod);
    ibz_mul(&(p01.v[1]), &(mat->m[1][0]), &b_ab);
    ibz_mul(&(p01.v[1]), &(p01.v[1]), &norm_bstar);
    ibz_mul(&prod, &(bstar.v[1]), &b_bbstar);
    ibz_mul(&prod, &prod, &norm_a);
    ibz_add(&(p01.v[1]), &(p01.v[1]), &prod);
    ibz_mul(&p01_denom, &norm_a, &norm_bstar);
    // compute norms
    quat_dim2_lattice_norm(&norm_p00, &(p00.v[0]), &(p00.v[1]));
    quat_dim2_lattice_norm(&norm_p01, &(p01.v[0]), &(p01.v[1]));
    // compare on same denom
    ibz_mul(&norm_p00, &norm_p00, &norm_a);
    ibz_mul(&norm_p00, &norm_p00, &norm_a);
    ibz_mul(&p00_denom, &p00_denom, &norm_a);
    int res = (ibz_cmp(&norm_p00, &norm_p01) <= 0);
    // Size reduction: |mu| <= 1/2, i.e. 2*|<a,b>| <= |a|^2.
    ibz_abs(&prod, &b_ab);
    ibz_add(&prod, &prod, &prod);
    res = res && (ibz_cmp(&prod, &norm_a) <= 0);
    return (res);
}

// void quat_dim2_lattice_short_basis(ibz_mat_2x2_t *reduced, const ibz_mat_2x2_t *basis, const ibz_t *norm_q);
static int
quat_test_lll_dim2_lattice_short_basis()
{
    int res = 0;
    ibz_mat_2x2_t basis, cmp, red;
    ibz_t prod, sum, bound;
    ibz_init(&prod);
    ibz_init(&sum);
    ibz_init(&bound);
    ibz_mat_2x2_init(&basis);
    ibz_mat_2x2_init(&cmp);
    ibz_mat_2x2_init(&red);
    ibz_set(&prod, 0, 0);
    ibz_set(&sum, 0, 0);

    // first test
    ibz_mat_2x2_set(&basis, 48, 4, 81, 9);
    quat_dim2_lattice_short_basis(&red, &basis);
    // check second basis vector larger (or at least equal) than 1st
    quat_dim2_lattice_norm(&sum, &red.m[0][0], &red.m[1][0]);
    quat_dim2_lattice_norm(&prod, &red.m[0][1], &red.m[1][1]);
    res = res || (ibz_cmp(&sum, &prod) > 0);
    // check mutual inclusion of lattices
    res = res || (!quat_dim2_lattice_contains(&red, &(basis.m[0][0]), &(basis.m[1][0])));
    res = res || (!quat_dim2_lattice_contains(&red, &(basis.m[0][1]), &(basis.m[1][1])));
    res = res || (!quat_dim2_lattice_contains(&basis, &(red.m[0][0]), &(red.m[1][0])));
    res = res || (!quat_dim2_lattice_contains(&basis, &(red.m[0][1]), &(red.m[1][1])));
    // check bilinear form value is small
    ibz_set(&bound, 50 * 100, 32);
    quat_dim2_lattice_bilinear(&sum, &(red.m[0][0]), &(red.m[0][1]), &(red.m[0][1]), &(red.m[1][1]));
    res = res || (ibz_cmp(&sum, &bound) > 0);
    // check norm smaller than original
    ibz_set(&bound, 50 * 50, 15);
    quat_dim2_lattice_norm(&sum, &(red.m[0][0]), &(red.m[1][0]));
    res = res || (ibz_cmp(&sum, &bound) > 0);
    quat_dim2_lattice_norm(&prod, &(red.m[0][1]), &(red.m[1][1]));
    res = res || (ibz_cmp(&prod, &bound) > 0);
    res = res || !quat_dim2_lattice_verify_lll(&red);

    // 2nd test
    ibz_mat_2x2_set(&basis, 364, 0, 1323546, 266606);
    quat_dim2_lattice_short_basis(&red, &basis);
    // check second basis vector larger (or at least equal) than 1st
    res = res || (ibz_cmp(&sum, &prod) > 0);
    // check mutual inclusion of lattices
    res = res || (!quat_dim2_lattice_contains(&red, &(basis.m[0][0]), &(basis.m[1][0])));
    res = res || (!quat_dim2_lattice_contains(&red, &(basis.m[0][1]), &(basis.m[1][1])));
    res = res || (!quat_dim2_lattice_contains(&basis, &(red.m[0][0]), &(red.m[1][0])));
    res = res || (!quat_dim2_lattice_contains(&basis, &(red.m[0][1]), &(red.m[1][1])));
    // check bilinear form value is small
    quat_dim2_lattice_norm(&bound, &(basis.m[0][1]), &(basis.m[1][1]));
    quat_dim2_lattice_bilinear(&sum, &(red.m[0][0]), &(red.m[0][1]), &(red.m[0][1]), &(red.m[1][1]));
    res = res || (ibz_cmp(&sum, &bound) > 0);
    // check norm smaller than original
    quat_dim2_lattice_norm(&bound, &(basis.m[0][1]), &(basis.m[1][1]));
    quat_dim2_lattice_norm(&sum, &(red.m[0][0]), &(red.m[1][0]));
    res = res || (ibz_cmp(&sum, &bound) > 0);
    quat_dim2_lattice_norm(&prod, &(red.m[0][1]), &(red.m[1][1]));
    res = res || (ibz_cmp(&prod, &bound) > 0);
    // check lll
    res = res || !quat_dim2_lattice_verify_lll(&red);

    if (res != 0) {
        printf("Quaternion unit test lll_dim2_lattice_short_basis failed\n");
    }
    return res;
}

// Direct test for the constant-time dimension-2 reducer.
// quat_lll_dim2_short_basis (lll/lehmer_xgcd.c)
// the CT reducer requires column-HNF input [[A, B], [0, g]] with det = A*g <= 2^det_bits.
static int
quat_test_lll_dim2_ct_check(const ibz_mat_2x2_t *basis, int det_bits)
{
    int res = 0;
    ibz_mat_2x2_t red;
    ibz_t det_in, det_out, n0, n1, in0, in1, b, twob, old_n0;
    ibz_mat_2x2_t old_red;

    ibz_mat_2x2_init(&red);
    ibz_mat_2x2_init(&old_red);
    ibz_init(&det_in);
    ibz_init(&det_out);
    ibz_init(&n0);
    ibz_init(&n1);
    ibz_init(&in0);
    ibz_init(&in1);
    ibz_init(&b);
    ibz_init(&twob);
    ibz_init(&old_n0);

    quat_lll_dim2_short_basis(&red, basis, det_bits);

    // Unimodularity of the transform: the determinant is preserved up to sign.
    ibz_mat_2x2_det_from_ibz(&det_in, &(basis->m[0][0]), &(basis->m[0][1]), &(basis->m[1][0]), &(basis->m[1][1]));
    ibz_mat_2x2_det_from_ibz(&det_out, &(red.m[0][0]), &(red.m[0][1]), &(red.m[1][0]), &(red.m[1][1]));
    ibz_abs(&det_in, &det_in);
    ibz_abs(&det_out, &det_out);
    if (ibz_cmp(&det_in, &det_out) != 0) {
        res = 1;
    }

    // Same lattice, checked in both directions (the old test's unimodularity check).
    if (!quat_dim2_lattice_contains(&red, &(basis->m[0][0]), &(basis->m[1][0])) ||
        !quat_dim2_lattice_contains(&red, &(basis->m[0][1]), &(basis->m[1][1])) ||
        !quat_dim2_lattice_contains(basis, &(red.m[0][0]), &(red.m[1][0])) ||
        !quat_dim2_lattice_contains(basis, &(red.m[0][1]), &(red.m[1][1]))) {
        res = 1;
    }

    quat_dim2_lattice_norm(&n0, &(red.m[0][0]), &(red.m[1][0]));
    quat_dim2_lattice_norm(&n1, &(red.m[0][1]), &(red.m[1][1]));
    quat_dim2_lattice_norm(&in0, &(basis->m[0][0]), &(basis->m[1][0]));
    quat_dim2_lattice_norm(&in1, &(basis->m[0][1]), &(basis->m[1][1]));

    // Ordering: the first output vector is the shorter one.
    if (ibz_cmp(&n0, &n1) > 0) {
        res = 1;
    }

    // Lagrange-Gauss returns a shortest vector, so it is no longer than either input vector.
    if (ibz_cmp(&n0, &in0) > 0 || ibz_cmp(&n0, &in1) > 0) {
        res = 1;
    }

    // Size reduction, two-sided: 2*|<a,b>| <= |a|^2. Stated directly here as well as inside
    // quat_dim2_lattice_verify_lll below, so the property this reducer must satisfy is not
    // only implicit in the shared predicate.
    quat_dim2_lattice_bilinear(&b, &(red.m[0][0]), &(red.m[1][0]), &(red.m[0][1]), &(red.m[1][1]));
    ibz_abs(&twob, &b);
    ibz_add(&twob, &twob, &twob);
    if (ibz_cmp(&twob, &n0) > 0) {
        res = 1;
    }

    // Full LLL-reducedness, via the same predicate the old reducer is held to.
    if (!quat_dim2_lattice_verify_lll(&red)) {
        res = 1;
    }

    // Differential check against the reference reducer. The reduced basis itself is only unique
    // up to signs and swaps, but the first minimum is a lattice invariant, so its norm must
    // agree exactly.
    quat_dim2_lattice_short_basis(&old_red, basis);
    quat_dim2_lattice_norm(&old_n0, &(old_red.m[0][0]), &(old_red.m[1][0]));
    if (ibz_cmp(&n0, &old_n0) != 0) {
        res = 1;
    }
    return res;
}

static int
quat_test_lll_dim2_ct_short_basis()
{
    int res = 0;
    ibz_mat_2x2_t basis;
    ibz_t g, a, bb, det;
    ibz_mat_2x2_init(&basis);
    ibz_init(&g);
    ibz_init(&a);
    ibz_init(&bb);
    ibz_init(&det);

    // Small fixed cases, in the required column-HNF shape. The last two are the degenerate
    // shapes the randomised generator will essentially never produce: an already-reduced basis,
    // and g == 1 (so the lattice is all of Z^2 scaled by A).
    {
        const int fix[][4] = {
            // A,   B,   g
            {   364,  265, 366, 0 },
            {  4096, 2047,   8, 0 },
            {     1,    0,   1, 0 },
            { 65536,    1,   1, 0 },
        };
        for (size_t k = 0; k < sizeof(fix) / sizeof(fix[0]); k++) {
            int A = fix[k][0], B = fix[k][1], G = fix[k][2];
            ibz_mat_2x2_set(&basis, A, B, 0, G);
            ibz_mul(&det, &(basis.m[0][0]), &(basis.m[1][1]));
            res |= quat_test_lll_dim2_ct_check(&basis, ibz_bitsize(&det));
        }
    }

    // Randomised HNF bases across a range of determinant sizes. det_bits is kept well below
    // IBZ_MAX_BITS so the DIM2_WORK_BITS assert inside the reducer is satisfied.
    for (int det_bits = 8; det_bits <= 128 && !res; det_bits += 8) {
        for (int iter = 0; iter < 10 && !res; iter++) {
            int gbits = 1 + (det_bits / 4);
            // g > 0
            ibz_set(&g, 0, 0);
            while (ibz_is_zero(&g))
                ibz_rand_interval_bits(&g, gbits);
            ibz_abs(&g, &g);
            // A > 0 with A*g <= 2^det_bits
            ibz_set(&a, 0, 0);
            while (ibz_is_zero(&a))
                ibz_rand_interval_bits(&a, det_bits - gbits);
            ibz_abs(&a, &a);
            // 0 <= B, and B is reduced mod A so the input really is in HNF
            ibz_rand_interval_bits(&bb, det_bits - gbits);
            ibz_abs(&bb, &bb);
            ibz_mod(&bb, &bb, &a);

            ibz_copy(&(basis.m[0][0]), &a);
            ibz_copy(&(basis.m[0][1]), &bb);
            ibz_set(&(basis.m[1][0]), 0, 0);
            ibz_copy(&(basis.m[1][1]), &g);

            ibz_mul(&det, &a, &g);
            res |= quat_test_lll_dim2_ct_check(&basis, ibz_bitsize(&det));
        }
    }
    if (res != 0) {
        printf("Quaternion unit test lll_dim2_ct_short_basis failed\n");
    }
    return res;
}

// Direct test for the constant-time sum-of-two-squares routine.
// void quat_lll_dim2_sumofsquares(ibz_t *x, ibz_t *y, const ibz_t *p, const ibz_t *r);
//
// A prime's representation as a sum of two squares is unique up to order and sign, so the
// expected output is known exactly whenever the input is built from a known (x, y) pair.
// That is a strictly stronger oracle than the x^2 + y^2 == p check ibz_cornacchia_prime
// performs on the way out.
static int
quat_test_lll_dim2_sumofsquares_check(const ibz_t *p, const ibz_t *r, const ibz_t *exp_x, const ibz_t *exp_y)
{
    int res = 0;
    ibz_t x, y, sum, tmp;
    ibz_init(&x);
    ibz_init(&y);
    ibz_init(&sum);
    ibz_init(&tmp);

    quat_lll_dim2_sumofsquares(&x, &y, p, r);

    ibz_sum_two_squares(&sum, &x, &y);
    if (ibz_cmp(&sum, p) != 0) {
        res = 1;
    }

    if (!ibz_is_positive(&x) || !ibz_is_positive(&y) || ibz_cmp(&x, p) >= 0 || ibz_cmp(&y, p) >= 0) {
        res = 1;
    }

    // Exact match against the pair the input was built from, in either order.
    if (!((ibz_cmp(&x, exp_x) == 0 && ibz_cmp(&y, exp_y) == 0) ||
          (ibz_cmp(&x, exp_y) == 0 && ibz_cmp(&y, exp_x) == 0))) {
        res = 1;
    }
    return res;
}

// Draw a random prime p = x^2 + y^2 with x, y of about half_bits bits, and the matching
// r = x * y^-1 mod p. Then r^2 == -1 mod p, since x^2 == -y^2 mod p and y is invertible.
// This avoids needing ibz_sqrt_m1_mod_verified and keeps (x, y) as the expected output.
// Returns 0 if no such prime was found within the retry budget, or randomness failed.
static int
quat_test_lll_dim2_sumofsquares_input(ibz_t *p, ibz_t *r, ibz_t *x, ibz_t *y, int half_bits)
{
    ibz_t inv;
    ibz_init(&inv);
    for (int tries = 0; tries < 100000; tries++) {
        if (!ibz_rand_interval_bits(x, half_bits) || !ibz_rand_interval_bits(y, half_bits)) {
            return 0;
        }
        ibz_abs(x, x);
        ibz_abs(y, y);
        if (ibz_is_even(x) == ibz_is_even(y)) {
            continue;
        }
        ibz_sum_two_squares(p, x, y);
        if (!ibz_probab_prime(p, 1) || !ibz_probab_prime(p, QUAT_primality_num_iter)) {
            continue;
        }
        if (!ibz_invmod(&inv, y, p)) {
            continue;
        }
        ibz_mul(r, x, &inv);
        ibz_mod(r, r, p);
        if (ibz_is_zero(r)) {
            continue;
        }
        ibz_set_bound(p, ibz_bitsize(p) + 1);
        ibz_set_bound(r, ibz_bitsize(p) + 1);
        return 1;
    }
    return 0;
}

static int
quat_test_lll_dim2_sumofsquares(void)
{
    int res = 0;
    ibz_t p, r, x, y;
    ibz_init(&p);
    ibz_init(&r);
    ibz_init(&x);
    ibz_init(&y);

    {
        const int fix[][5] = {
            //  p,    r,   x,   y
            {     5,   2, 1,   2 },
            {    13,   5, 2,   3 },
            {    41,   9, 4,   5 },
            { 65537, 256, 1, 256 },
        };
        for (size_t k = 0; k < sizeof(fix) / sizeof(fix[0]); k++) {
            ibz_set(&p, fix[k][0], 32);
            ibz_set(&r, fix[k][1], 32);
            ibz_set(&x, fix[k][2], 32);
            ibz_set(&y, fix[k][3], 32);
            ibz_set_bound(&p, ibz_bitsize(&p) + 1);
            ibz_set_bound(&r, ibz_bitsize(&p) + 1);
            res |= quat_test_lll_dim2_sumofsquares_check(&p, &r, &x, &y);
        }
    }

    const int half_bit_sizes[] = { 8, 16, 32, 64, 96, 128, 168 };
    for (size_t s = 0; s < sizeof(half_bit_sizes) / sizeof(half_bit_sizes[0]) && !res; s++) {
        const int half_bits = half_bit_sizes[s];
        for (int iter = 0; iter < 3 && !res; iter++) {
            if (!quat_test_lll_dim2_sumofsquares_input(&p, &r, &x, &y, half_bits)) {
                res = 1;
                break;
            }
            res |= quat_test_lll_dim2_sumofsquares_check(&p, &r, &x, &y);
        }
    }

    if (res != 0) {
        printf("Quaternion unit test lll_dim2_sumofsquares failed\n");
    }
    return res;
}

int
quat_test_lll_dim2(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of dim2 reduction (sub-)functions\n");
    res = res | quat_test_lll_dim2_lattice_contains();
    res = res | quat_test_lll_dim2_lattice_norm();
    res = res | quat_test_lll_dim2_lattice_bilinear();
    res = res | quat_test_lll_dim2_lattice_short_basis();
    res = res | quat_test_lll_dim2_ct_short_basis();
    res = res | quat_test_lll_dim2_sumofsquares();
    return (res);
}
