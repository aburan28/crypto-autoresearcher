#include "lll_test_internals.h"
#include <lll.h>
#include "quaternion_tests.h"
#include <quaternion_data.h>
#include <quaternion_constants.h>
#include <torsion_constants.h>
#include <rng.h>
#include <prng.h>
#include <stdlib.h>

static int
quat_test_lll_ibq_consts(void)
{
    ibq_t t;
    ibz_t tmp1, tmp2, tmp3;
    ibz_init(&tmp1);
    ibz_init(&tmp2);
    ibz_init(&tmp3);
    ibq_init(&t);

    ibz_set(&tmp1, 123, 8);
    ibz_set(&tmp2, -123, 8);
    if (!ibq_set(&t, &tmp1, &tmp2))
        return -1;
    if (ibq_is_one(&t))
        return -1;
    if (!ibq_is_ibz(&t))
        return -1;
    if (!ibq_to_ibz(&tmp3, &t))
        return -1;
    if (ibz_is_one(&tmp3))
        return -1;
    ibz_set(&tmp2, 123, 8);
    if (!ibq_set(&t, &tmp1, &tmp2))
        return -1;
    if (!ibq_is_one(&t))
        return -1;
    if (!ibq_is_ibz(&t))
        return -1;
    if (!ibq_to_ibz(&tmp3, &t))
        return -1;
    if (!ibz_is_one(&tmp3))
        return -1;
    ibz_set(&tmp1, 0, 0);
    ibq_set(&t, &tmp1, &tmp2);
    if (!ibq_is_zero(&t))
        return -1;
    if (!ibq_is_ibz(&t))
        return -1;
    if (!ibq_to_ibz(&tmp3, &t))
        return -1;
    if (!ibz_is_zero(&tmp3))
        return -1;
    return 0;
}

// test for lll verification
// void ibq_vec_4_copy_ibz(ibq_vec_4_t *vec, const ibz_t *coeff0, const ibz_t *coeff1,const ibz_t
// *coeff2,const ibz_t *coeff3);
static int
quat_test_lll_ibq_vec_4_copy_ibz(void)
{
    int res = 0;
    ibq_vec_4_t vec;
    ibz_vec_4_t vec_z;
    ibz_vec_4_init(&vec_z);
    ibq_vec_4_init(&vec);
    ibz_vec_4_set(&vec_z, 2, 3, 4, 5);
    ibq_vec_4_copy_ibz(&vec, &(vec_z.v[0]), &(vec_z.v[1]), &(vec_z.v[2]), &(vec_z.v[3]));
    for (int i = 0; i < 4; i++) {
        ibq_to_ibz(&(vec_z.v[i]), &(vec.v[i]));
        res = res || (ibz_cmp_int32(&(vec_z.v[i]), i + 2) != 0);
    }

    if (res != 0) {
        printf("Quaternion unit test lll_ibq_vec_4_copy_ibz failed\n");
    }
    return (res);
}

// void quat_lll_bilinear(ibq_t *b, const ibq_vec_4_t *vec0, const ibq_vec_4_t *vec1, const ibz_t *q);
static int
quat_test_lll_bilinear(void)
{
    int res = 0;
    ibz_vec_4_t init_helper;
    ibq_vec_4_t vec0, vec1;
    ibz_t q;
    ibq_t cmp, b;
    ibz_vec_4_init(&init_helper);
    ibq_init(&cmp);
    ibq_init(&b);
    ibz_init(&q);
    ibq_vec_4_init(&vec0);
    ibq_vec_4_init(&vec1);
    ibz_vec_4_set(&init_helper, 1, 2, 3, 4);
    ibq_vec_4_copy_ibz(&vec0, &(init_helper.v[0]), &(init_helper.v[1]), &(init_helper.v[2]), &(init_helper.v[3]));
    ibz_vec_4_set(&init_helper, 9, -8, 7, -6);
    ibq_vec_4_copy_ibz(&vec1, &(init_helper.v[0]), &(init_helper.v[1]), &(init_helper.v[2]), &(init_helper.v[3]));
    for (int i = 0; i < 4; i++) {
        ibq_inv(&(vec0.v[i]), &(vec0.v[i]));
    }
    ibz_set(&q, 3, 3);
    ibz_vec_4_set(&init_helper, 15, 2, 0, 0);
    ibq_set(&cmp, &(init_helper.v[0]), &(init_helper.v[1]));
    quat_lll_bilinear(&b, &vec0, &vec1, &q);
    res = res || (ibq_cmp(&b, &cmp));

    if (res != 0) {
        printf("Quaternion unit test quat_lll_bilinear failed\n");
    }
    return (res);
}

// void quat_lll_gram_schmidt_transposed_with_ibq(ibq_mat_4x4_t *orthogonalised_transposed, const ibz_mat_4x4_t *mat,
// const ibz_t *q);
static int
quat_test_lll_gram_schmidt_transposed_with_ibq(void)
{
    int res = 0;
    int zero;
    ibq_mat_4x4_t ot, cmp;
    ibz_mat_4x4_t mat;
    ibz_t q, num, denom;
    ibq_t b;
    ibz_init(&q);
    ibz_init(&num);
    ibz_init(&denom);
    ibq_init(&b);
    ibz_mat_4x4_init(&mat);
    ibq_mat_4x4_init(&ot);
    ibq_mat_4x4_init(&cmp);

    ibz_mat_4x4_zero(&mat);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibz_set(&(mat.m[i][j]), i * i + (j + 5) * j - 2 + (i == j), 8);
        }
    }
    ibz_set(&q, 3, 3);
    quat_lll_gram_schmidt_transposed_with_ibq(&ot, &mat, &q);
    // test orthogonality
    for (int i = 0; i < 4; i++) {
        for (int j = i + 1; j < 4; j++) {
            quat_lll_bilinear(&b, &(ot.m[i]), &(ot.m[j]), &q);
            res = res || !ibq_is_zero(&b);
        }
    }
    // test first vector is identical to mat
    for (int i = 0; i < 4; i++) {
        ibq_to_ibz(&q, &(ot.m[0].v[i]));
        res = res || ibz_cmp(&q, &(mat.m[i][0]));
    }
    // test no zero vector
    for (int i = 0; i < 4; i++) {
        zero = 1;
        for (int j = 0; j < 4; j++) {
            zero = zero && ibq_is_zero(&(ot.m[i].v[j]));
        }
        res = res || zero;
    }

    ibz_set(&(mat.m[0][0]), 1, 2);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 1, 2);
    ibz_set(&(mat.m[0][3]), 0, 0);
    ibz_set(&(mat.m[1][0]), 0, 0);
    ibz_set(&(mat.m[1][1]), 1, 2);
    ibz_set(&(mat.m[1][2]), 0, 0);
    ibz_set(&(mat.m[1][3]), 1, 2);
    ibz_set(&(mat.m[2][0]), 1, 2);
    ibz_set(&(mat.m[2][1]), 0, 0);
    ibz_set(&(mat.m[2][2]), 2, 3);
    ibz_set(&(mat.m[2][3]), 0, 0);
    ibz_set(&(mat.m[3][0]), 0, 0);
    ibz_set(&(mat.m[3][1]), 1, 2);
    ibz_set(&(mat.m[3][2]), 0, 0);
    ibz_set(&(mat.m[3][3]), 2, 3);
    ibz_set(&denom, 1, 2);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibq_set(&(cmp.m[i].v[j]), &(mat.m[j][i]), &denom);
        }
    }
    ibz_set(&denom, 3, 3);
    ibz_set(&num, -2, 3);
    ibq_set(&(cmp.m[2].v[0]), &num, &denom);
    ibq_set(&(cmp.m[3].v[1]), &num, &denom);
    ibz_set(&num, 1, 2);
    ibq_set(&(cmp.m[2].v[2]), &num, &denom);
    ibq_set(&(cmp.m[3].v[3]), &num, &denom);
    ibz_set(&q, 2, 3);
    quat_lll_gram_schmidt_transposed_with_ibq(&ot, &mat, &q);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            res = res || ibq_cmp(&(cmp.m[i].v[j]), &(ot.m[i].v[j]));
        }
    }

    ibz_set(&(mat.m[0][0]), 1, 2);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 1, 2);
    ibz_set(&(mat.m[0][3]), 0, 0);
    ibz_set(&(mat.m[1][0]), 0, 0);
    ibz_set(&(mat.m[1][1]), 1, 2);
    ibz_set(&(mat.m[1][2]), 0, 0);
    ibz_set(&(mat.m[1][3]), 1, 2);
    ibz_set(&(mat.m[2][0]), 1, 2);
    ibz_set(&(mat.m[2][1]), 0, 0);
    ibz_set(&(mat.m[2][2]), 2, 3);
    ibz_set(&(mat.m[2][3]), 1, 2);
    ibz_set(&(mat.m[3][0]), 0, 0);
    ibz_set(&(mat.m[3][1]), 1, 2);
    ibz_set(&(mat.m[3][2]), 0, 0);
    ibz_set(&(mat.m[3][3]), 2, 3);
    ibz_set(&denom, 1, 2);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            ibq_set(&(cmp.m[i].v[j]), &(mat.m[j][i]), &denom);
        }
    }
    ibz_set(&denom, 3, 3);
    ibz_set(&num, -2, 3);
    ibq_set(&(cmp.m[2].v[0]), &num, &denom);
    ibq_set(&(cmp.m[3].v[1]), &num, &denom);
    ibz_set(&num, 1, 2);
    ibq_set(&(cmp.m[2].v[2]), &num, &denom);
    ibq_set(&(cmp.m[3].v[3]), &num, &denom);
    ibz_set(&num, 0, 0);
    ibq_set(&(cmp.m[3].v[0]), &num, &denom);
    ibq_set(&(cmp.m[3].v[2]), &num, &denom);
    ibz_set(&q, 2, 3);
    quat_lll_gram_schmidt_transposed_with_ibq(&ot, &mat, &q);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            res = res || ibq_cmp(&(cmp.m[i].v[j]), &(ot.m[i].v[j]));
        }
    }

    if (res != 0) {
        printf("Quaternion unit test dim4_gram_schmidt_transposed_with_ibq failed\n");
    }
    return (res);
}

// int quat_lll_verify(const ibz_mat_4x4_t *mat, const ibq_t *delta, const ibq_t *eta, const quat_alg_t *alg);
static int
quat_test_lll_verify(void)
{
    int res = 0;
    ibz_mat_4x4_t mat;
    ibz_t q, coeff_num, coeff_denom;
    ibq_t eta, delta;
    quat_alg_t alg;
    ibz_mat_4x4_init(&mat);
    ibz_init(&q);
    ibq_init(&delta);
    ibq_init(&eta);
    ibz_init(&coeff_num);
    ibz_init(&coeff_denom);

    // reduced: non-1 norm
    ibz_set(&q, 3, 3);
    quat_alg_init_set(&alg, &q);
    ibq_set(&eta, &ibz_const_one, &ibz_const_two);
    ibq_set(&delta, &ibz_const_three, &ibz_const_two);
    ibq_mul(&delta, &delta, &eta);
    ibz_set(&(mat.m[0][0]), 0, 0);
    ibz_set(&(mat.m[0][1]), 2, 3);
    ibz_set(&(mat.m[0][2]), 3, 3);
    ibz_set(&(mat.m[0][3]), -14, 5);
    ibz_set(&(mat.m[1][0]), 2, 3);
    ibz_set(&(mat.m[1][1]), -1, 2);
    ibz_set(&(mat.m[1][2]), -4, 4);
    ibz_set(&(mat.m[1][3]), -8, 5);
    ibz_set(&(mat.m[2][0]), 1, 2);
    ibz_set(&(mat.m[2][1]), -2, 3);
    ibz_set(&(mat.m[2][2]), 1, 2);
    ibz_set(&(mat.m[2][3]), 0, 0);
    ibz_set(&(mat.m[3][0]), 1, 2);
    ibz_set(&(mat.m[3][1]), 1, 2);
    ibz_set(&(mat.m[3][2]), 0, 0);
    ibz_set(&(mat.m[3][3]), 7, 4);
    res = res || !quat_lll_verify(&mat, &delta, &eta, &alg);

    // reduced: non-1 norm
    ibz_set(&q, 103, 8);
    quat_alg_init_set(&alg, &q);
    ibz_set(&coeff_num, 99, 8);
    ibz_set(&coeff_denom, 100, 8);
    ibq_set(&delta, &coeff_num, &coeff_denom);
    ibz_set(&(mat.m[0][0]), 3, 3);
    ibz_set(&(mat.m[0][1]), 0, 0);
    ibz_set(&(mat.m[0][2]), 90, 8);
    ibz_set(&(mat.m[0][3]), -86, 8);
    ibz_set(&(mat.m[1][0]), 11, 5);
    ibz_set(&(mat.m[1][1]), 15, 5);
    ibz_set(&(mat.m[1][2]), 12, 5);
    ibz_set(&(mat.m[1][3]), 50, 7);
    ibz_set(&(mat.m[2][0]), 1, 2);
    ibz_set(&(mat.m[2][1]), -2, 3);
    ibz_set(&(mat.m[2][2]), 0, 0);
    ibz_set(&(mat.m[2][3]), 3, 3);
    ibz_set(&(mat.m[3][0]), -1, 2);
    ibz_set(&(mat.m[3][1]), 0, 0);
    ibz_set(&(mat.m[3][2]), 5, 4);
    ibz_set(&(mat.m[3][3]), 5, 4);
    res = res || !quat_lll_verify(&mat, &delta, &eta, &alg);

    if (res != 0) {
        printf("Quaternion unit test quat_lll_verify failed\n");
    }
    return (res);
}

// The next two tests cover the quat_ layer wrappers in lvlx/lll_applications.c, not lll internals.

// void quat_ideal_reduce_basis(quat_lattice_t *reduced, const quat_ideal_t *ideal);
static int
quat_test_ideal_O0_reduce_basis_at(int norm_bitsize, int iterations)
{
    int res = 0;
    quat_ideal_t *ideals = NULL;
    quat_lattice_t lat, red, test;
    ibq_t delta, eta;

    quat_lattice_init(&lat);
    quat_lattice_init(&red);
    quat_lattice_init(&test);
    ibq_init(&delta);
    ibq_init(&eta);
    quat_lll_set_ct_ibq_parameters(&delta, &eta);

    ideals = calloc((size_t)iterations, sizeof(quat_ideal_t));
    if (ideals == NULL) {
        res = 1;
        return (res);
    }
    for (int i = 0; i < iterations; i++)
        quat_ideal_init(&(ideals[i]));

    if (quat_test_input_random_ideal_generation(ideals, norm_bitsize, iterations)) {
        free(ideals);
        return (1);
    }

    for (int i = 0; i < iterations; i++) {
        quat_to_lattice(&lat, &(ideals[i]));
        quat_lattice_reduce_denom(&lat, &lat);

        quat_ideal_reduce_basis(&red, &(ideals[i]));

        // LLL-reducedness of the output basis.
        if (!quat_lll_verify(&red.basis, &delta, &eta, &QUATALG_PINFTY)) {
            res = 1;
            break;
        }

        // The reduced basis must still span a sublattice of the ideal.
        // Only the original basis is triangular, so without HNF we can
        // only compute the inclusion one way.
        // Could extend with ibz_mat_4x4_inv_with_det_as_denom but might
        // overflow integers.
        ibz_mat_4x4_copy(&(test.basis), &red.basis);
        ibz_copy(&(test.denom), &(lat.denom));
        if (!quat_lattice_inclusion(&test, &lat)) {
            res = 1;
            break;
        }
    }

    free(ideals);
    return (res);
}

static int
quat_test_ideal_O0_reduce_basis()
{
    int res = 0;
    // The same two norm scales the CT benchmark uses, since they are the ones the production
    // callers of quat_ideal_reduce_basis produce: the secret/commitment degree, and the
    // sqrt(p)-scale ideals of the response and shortest-equivalent paths.
    res |= quat_test_ideal_O0_reduce_basis_at(ibz_bitsize(&SEC_DEGREE), 10);
    res |= quat_test_ideal_O0_reduce_basis_at(ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 15, 10);

    if (res != 0) {
        printf("Quaternion unit test ideal_O0_reduce_basis failed\n");
    }
    return (res);
}

// int quat_lattice_bound_parallelogram(ibz_vec_4_t *box, ibz_mat_4x4_t *U, const quat_lattice_t *lat, const ibz_t
// *radius);
static int
quat_test_lattice_paralellogram_randomized(int iterations, int bitsize)
{
    int res = 0;

    quat_lattice_t lattice;
    ibz_t radius, length, tmp;
    ibz_mat_4x4_t U, G;
    ibz_vec_4_t box, dbox, x;
    quat_lattice_init(&lattice);
    ibz_vec_4_init(&box);
    ibz_vec_4_init(&dbox);
    ibz_vec_4_init(&x);
    ibz_mat_4x4_init(&U);
    ibz_mat_4x4_init(&G);
    ibz_init(&radius);
    ibz_init(&length);
    ibz_init(&tmp);

    for (int it = 0; it < iterations; it++) {
        // Create a random positive definite quadatic form
        int UNUSED randret = quat_test_input_resplike_lattice_generation(&lattice, &radius, bitsize, 1);
        assert(randret == 0);

        ibz_mat_4x4_transpose(&G, &lattice.basis);
        ibz_mat_4x4_mul(&G, &G, &lattice.basis);

        // Set radius to 2 × sqrt(lattice norm)
        ibz_abs(&radius, &radius);
        ibz_sqrt_floor(&radius, &radius);
        ibz_mul(&radius, &radius, &ibz_const_two);

        // Caveat: the exhaustive sample below is only affordable for a small box, which
        // the real sqisign prime does not give. Shrink the radius until the box is enumerable;
        // replace by a derived radius or by random sampling.
        for (int guard = 0; guard < 64; guard++) {
            quat_lattice_bound_parallelogram(&box, &U, &lattice, &radius);
            int maxbits = 0;
            for (int i = 0; i < 4; i++)
                if (ibz_bitsize(&box.v[i]) > maxbits)
                    maxbits = ibz_bitsize(&box.v[i]);
            if (maxbits <= 2 || ibz_is_zero(&radius)) // box[i] <= 3 for all i
                break;
            ibz_div_2exp(&radius, &radius, 2 * (maxbits - 2));
        }
        for (int i = 0; i < 4; i++) {
            // dbox is a box with sides dbox[i] =  2*box[i] + 1
            ibz_add(&dbox.v[i], &box.v[i], &box.v[i]);
            ibz_add(&dbox.v[i], &dbox.v[i], &ibz_const_one);
            // initialize x[i] to the bottom of dbox[i]
            ibz_neg(&x.v[i], &dbox.v[i]);
        }

        // Integrate U into the Gram matrix
        ibz_mat_4x4_mul(&G, &U, &G);
        ibz_mat_4x4_transpose(&U, &U);
        ibz_mat_4x4_mul(&G, &G, &U);

        // We treat x[0]...x[4] as a counter, incrementing one by one
        // but skipping values that are inside the parallelogram defined by box.
        while (1) {
            // x is out of the parallelogram, so its length must be greater than the radius
            quat_qf_eval(&length, &G, &x);
            if (ibz_cmp(&length, &radius) <= 0) {
                res = 1;
                break;
            }

            // Increment counter
            ibz_add(&x.v[0], &x.v[0], &ibz_const_one);
            // if x[0] just entered the interval
            ibz_add(&tmp, &x.v[0], &box.v[0]);
            if (ibz_is_zero(&tmp)) {
                int inbox = 1;
                for (int i = 1; i < 4; i++) {
                    ibz_abs(&tmp, &x.v[i]);
                    inbox &= ibz_cmp(&tmp, &box.v[i]) <= 0;
                }
                // if x[1]...x[3] are all in the respective intervals jump straight to the end of x[0]'s interval
                if (inbox)
                    ibz_set(&x.v[0], 1, 2);
            }

            // if x[0] became positive, loop the counter
            if (ibz_is_one(&x.v[0])) {
                ibz_neg(&x.v[0], &dbox.v[0]);
                int carry = 1;
                for (int i = 1; carry && i < 4; i++) {
                    ibz_add(&x.v[i], &x.v[i], &ibz_const_one);
                    if (ibz_cmp(&x.v[i], &dbox.v[i]) > 0) {
                        ibz_neg(&x.v[i], &dbox.v[i]);
                    } else {
                        carry = 0;
                    }
                }

                // If there still is a carry, we are at the end
                if (carry)
                    break;
            }
        }
    }

    if (res != 0) {
        printf("Quaternion unit test lattice_paralellogram_randomized failed\n");
    }
    return (res);
}

static int
quat_test_lll_prime_constants(void)
{
    int res = 0;
    ibz_t p, s, s1, sq, sq1;
    ibz_init(&p);
    ibz_init(&s);
    ibz_init(&s1);
    ibz_init(&sq);
    ibz_init(&sq1);

    if (QUAT_P_BITS != ibz_bitsize(&QUATALG_PINFTY.p)) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_P_BITS %d != bits(p) %d\n",
               (int)QUAT_P_BITS,
               ibz_bitsize(&QUATALG_PINFTY.p));
        res = 1;
    }

    if (!ibz_set_from_str(&p, QUAT_P_HEX, 16)) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_P_HEX does not parse\n");
        return 1;
    }
    if (ibz_cmp(&p, &QUATALG_PINFTY.p) != 0) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_P_HEX != QUATALG_PINFTY.p\n");
        res = 1;
    }

    // QUAT_SQRT_P_HEX is isqrt(p): s^2 <= p < (s+1)^2.
    if (!ibz_set_from_str(&s, QUAT_SQRT_P_HEX, 16)) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_SQRT_P_HEX does not parse\n");
        return 1;
    }
    if (QUAT_SQRT_P_BITS != ibz_bitsize(&s)) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_SQRT_P_BITS %d != bits(s) %d\n",
               (int)QUAT_SQRT_P_BITS,
               ibz_bitsize(&s));
        res = 1;
    }
    // Widen only after the bitsize check: a too-small QUAT_SQRT_P_BITS would make this a
    // *narrowing* ibz_set_bound and truncate s before the check could report it.
    ibz_set_bound(&s, QUAT_SQRT_P_BITS + 1);
    ibz_mul(&sq, &s, &s);
    ibz_add_int_and_set_bound(&s1, &s, 1, QUAT_SQRT_P_BITS + 2);
    ibz_mul(&sq1, &s1, &s1);
    if (!(ibz_cmp(&sq, &QUATALG_PINFTY.p) <= 0 && ibz_cmp(&QUATALG_PINFTY.p, &sq1) < 0)) {
        printf("Quaternion unit test lll_prime_constants failed: QUAT_SQRT_P_HEX is not isqrt(p)\n");
        res = 1;
    }

    return (res);
}

// The signing path replaces an ideal by a randomly chosen small equivalent representative before
// forming the product lattice this reduces, so the reduction must not depend on which one was
// drawn. Checks per iteration that two representatives give the same reduced Gram (up to the ideal
// norms), the same sampling box, and the same sampled norm for identically seeded randomness.
//
// void quat_lll_dual_reduce_ideal(quat_lattice_t *reduced, ibz_t gram_diag[4], ibz_mat_4x4_t *Ainv,
// const quat_lattice_t *hnf, const quat_alg_t *alg);
static int
quat_test_lll_dual_reduce_canonicity(int iterations, int norm_bitsize)
{
    int res = 0;

    quat_ideal_t ideal_a, ideal_b, eq_a[2], eq_b[2];
    quat_lattice_t prod[2], reduced[2];
    ibz_mat_4x4_t Ainv[2], gram[2], U[2];
    ibz_vec_4_t box[2];
    ibz_t gram_diag[2][4];
    ibz_t radius, lhs, rhs, sampled_norm[2];
    quat_alg_elem_t sampled[2];

    quat_ideal_init(&ideal_a);
    quat_ideal_init(&ideal_b);
    for (int r = 0; r < 2; r++) {
        quat_ideal_init(&eq_a[r]);
        quat_ideal_init(&eq_b[r]);
        quat_lattice_init(&prod[r]);
        quat_lattice_init(&reduced[r]);
        ibz_mat_4x4_init(&Ainv[r]);
        ibz_mat_4x4_init(&gram[r]);
        ibz_mat_4x4_init(&U[r]);
        ibz_vec_4_init(&box[r]);
        ibz_init(&sampled_norm[r]);
        quat_alg_elem_init(&sampled[r]);
        for (int i = 0; i < 4; i++)
            ibz_init(&gram_diag[r][i]);
    }
    ibz_init(&radius);
    ibz_init(&lhs);
    ibz_init(&rhs);

    // The radius the signing path uses, in quat_lattice_sample_from_ball's own (norm-normalised)
    // units: protocol.c passes 2^(RESPONSE_BITS-1) - 1.
    ibz_mul_2exp(&radius, &ibz_const_one, RESPONSE_BITS - 1);
    ibz_sub(&radius, &radius, &ibz_const_one);

    for (int it = 0; it < iterations; it++) {
        if (quat_test_input_random_ideal_generation(&ideal_a, norm_bitsize, 1) != 0 ||
            quat_test_input_random_ideal_generation(&ideal_b, norm_bitsize, 1) != 0) {
            res = 1;
            goto fin;
        }

        // Two independent equivalent representatives of each factor. Retry until the two product
        // lattices really differ, otherwise the comparison below is vacuous.
        int usable = 0;
        for (int attempt = 0; attempt < 32 && !usable; attempt++) {
            for (int r = 0; r < 2; r++) {
                if (!quat_ideal_small_equivalent_coprime(
                        NULL, &eq_a[r], &ideal_a, &ibz_const_zero, &PRNG_default_domain) ||
                    !quat_ideal_small_equivalent_coprime(
                        NULL, &eq_b[r], &ideal_b, &ibz_const_zero, &PRNG_default_domain)) {
                    res = 1;
                    goto fin;
                }
            }
            // quat_ideal_mul_O0 requires coprime norms.
            usable = (ibz_cmp(&eq_a[0].norm, &eq_b[0].norm) != 0) && (ibz_cmp(&eq_a[1].norm, &eq_b[1].norm) != 0) &&
                     ((ibz_cmp(&eq_a[0].norm, &eq_a[1].norm) != 0) || (ibz_cmp(&eq_b[0].norm, &eq_b[1].norm) != 0));
        }
        if (!usable)
            continue; // could not obtain two distinct representatives; skip, do not fail

        for (int r = 0; r < 2; r++) {
            quat_ideal_mul_O0(&prod[r], &eq_a[r], &eq_b[r]);
            quat_lll_dual_reduce_ideal(&reduced[r], gram_diag[r], &Ainv[r], &prod[r], &QUATALG_PINFTY);
            quat_lattice_gram(&gram[r], &reduced[r]);
            quat_lattice_bound_parallelogram(&box[r], &U[r], &prod[r], &radius);
        }

        // Gram_A / n(prod_A) == Gram_B / n(prod_B), cross-multiplied to stay in integers.
        // prod.basis.m[0][0] is 2*n(prod), and the factor 2 cancels.
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 4; j++) {
                ibz_mul(&lhs, &gram[0].m[i][j], &prod[1].basis.m[0][0]);
                ibz_mul(&rhs, &gram[1].m[i][j], &prod[0].basis.m[0][0]);
                if (ibz_cmp(&lhs, &rhs) != 0) {
                    res = 1;
                    goto fin;
                }
            }
        }

        // identical sampling boxes.
        for (int i = 0; i < 4; i++) {
            if (ibz_cmp(&box[0].v[i], &box[1].v[i]) != 0) {
                res = 1;
                goto fin;
            }
        }

        // same randomness in, same response norm out.
        {
            prng_domain_ctx_t dom[2];
            int ok = 1;
            for (int r = 0; r < 2; r++) {
                if (prng_domain_seed(&dom[r], DS_RESPONSE_DOMAIN) != 0) {
                    res = 1;
                    goto fin;
                }
            }
            for (int r = 0; r < 2; r++)
                ok &= quat_lattice_sample_from_ball(&sampled[r], &sampled_norm[r], &prod[r], &radius, &dom[r]);
            for (int r = 0; r < 2; r++)
                prng_domain_clear(&dom[r]);
            if (!ok) {
                res = 1;
                goto fin;
            }
            if (ibz_cmp(&sampled_norm[0], &sampled_norm[1]) != 0) {
                res = 1;
                goto fin;
            }
        }
    }

fin:;
    if (res != 0) {
        printf("Quaternion unit test lll_dual_reduce_canonicity failed\n");
    }
    return (res);
}

// Unlike the dimension 4 reduction above, this one is not canonical over an equivalence class: its
// sign convention is stated in coordinates, which a scaled isometry does not preserve, so the basis
// comes out permuted and re-signed. The geometry is canonical though, so only the four vector norms
// are asserted, not the full Gram.
//
// void quat_ideal_reduce_basis(quat_lattice_t *reduced, const quat_ideal_t *ideal);
static int
quat_test_lll_reduce_basis_minima_canonicity(int iterations, int norm_bitsize)
{
    int res = 0;
    quat_ideal_t ideal, eq[2];
    quat_lattice_t red[2];
    ibz_mat_4x4_t gram[2];
    ibz_t lhs, rhs;

    quat_ideal_init(&ideal);
    for (int r = 0; r < 2; r++) {
        quat_ideal_init(&eq[r]);
        quat_lattice_init(&red[r]);
        ibz_mat_4x4_init(&gram[r]);
    }
    ibz_init(&lhs);
    ibz_init(&rhs);

    for (int it = 0; it < iterations; it++) {
        if (quat_test_input_random_ideal_generation(&ideal, norm_bitsize, 1) != 0) {
            res = 1;
            goto fin;
        }
        int ok = 1;
        for (int r = 0; r < 2; r++)
            ok &= quat_ideal_small_equivalent_coprime(NULL, &eq[r], &ideal, &ibz_const_zero, &PRNG_default_domain);
        if (!ok) {
            res = 1;
            goto fin;
        }
        if (ibz_cmp(&eq[0].norm, &eq[1].norm) == 0)
            continue; // same representative drawn twice; nothing to compare

        for (int r = 0; r < 2; r++) {
            quat_ideal_reduce_basis(&red[r], &eq[r]);
            quat_lattice_gram(&gram[r], &red[r]);
        }

        // Gram_A / n(A) == Gram_B / n(B) on the DIAGONAL, cross-multiplied to stay in integers.
        for (int i = 0; i < 4; i++) {
            ibz_mul(&lhs, &gram[0].m[i][i], &eq[1].norm);
            ibz_mul(&rhs, &gram[1].m[i][i], &eq[0].norm);
            if (ibz_cmp(&lhs, &rhs) != 0) {
                res = 1;
                goto fin;
            }
        }
    }

fin:;
    if (res != 0)
        printf("Quaternion unit test lll_reduce_basis_minima_canonicity failed\n");
    return (res);
}

// run all previous tests
int
quat_test_lll(void)
{
    int res = 0;
    printf("\nRunning quaternion tests of lll and its subfunctions\n");
    res = res | quat_test_lll_prime_constants();
    res = res | quat_test_lll_ibq_consts();
    res = res | quat_test_lll_ibq_vec_4_copy_ibz();
    res = res | quat_test_lll_bilinear();
    res = res | quat_test_lll_gram_schmidt_transposed_with_ibq();
    res = res | quat_test_lll_verify();
    res = res | quat_test_ideal_O0_reduce_basis();
    res = res | quat_test_lattice_paralellogram_randomized(100, ibz_bitsize(&QUATALG_PINFTY.p) + 20);
    res = res | quat_test_lll_reduce_basis_minima_canonicity(50, ibz_bitsize(&SEC_DEGREE));
    res = res | quat_test_lll_reduce_basis_minima_canonicity(50, ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 15);
    res = res | quat_test_lll_dual_reduce_canonicity(20, ibz_bitsize(&SEC_DEGREE));
    res = res | quat_test_lll_dual_reduce_canonicity(20, ibz_bitsize(&QUATALG_PINFTY.p) / 2 + 15);
    return (res);
}
