#ifndef LLL_INTERNALS_H
#define LLL_INTERNALS_H

/** @file
 *
 * @authors Sina Schaeffler
 *
 * @brief Declarations of functions only used for the LLL tets
 */

#include <quaternion.h>

/**
 * @ingroup quat_helpers
 * @defgroup lll_internal Functions only used for LLL or its tests
 * @{
 */

/**
 * @ingroup lll_internal
 * @defgroup ibq_t Types for rationals
 * @{
 */

/** @brief Type for fractions of integers
 *
 * @typedef ibq_t
 *
 * For fractions of integers of arbitrary size for lattice tests
 */
typedef struct ibq
{
    ibz_t q[2];
} ibq_t; // struct so that const pointers to it are valid ISO C11

/** @brief Type for fractions of integers
 *
 * @typedef ibq_vec_4_t
 *
 * Vector of rationals
 */
typedef struct ibqv
{
    ibq_t v[4];
} ibq_vec_4_t;

/** @brief Type for fractions of integers
 *
 * @typedef ibq_mat_4x4_t
 *
 * Matrix of rationals
 */
typedef struct ibqm
{
    ibq_vec_4_t m[4]; // rows are vectors, so a row pointer is a valid ibq_vec_4_t *
} ibq_mat_4x4_t;

/**@}
 */

/**
 * @ingroup lll_internal
 * @defgroup ibq_c Constructors and Destructors and Printers
 * @{
 */

void ibq_init(ibq_t *x);

void ibq_mat_4x4_init(ibq_mat_4x4_t *mat);

void ibq_vec_4_init(ibq_vec_4_t *vec);

void ibq_mat_4x4_print(const ibq_mat_4x4_t *mat);
void ibq_vec_4_print(const ibq_vec_4_t *vec);

/** @}
 */

/**
 * @ingroup lll_internal
 * @defgroup ibq_qa Basic fraction arithmetic
 * @{
 */

void ibq_denom(ibz_t *denom, const ibq_t *x);
void ibq_num(ibz_t *num, const ibq_t *x);

/** @brief Put x in lowest terms, with a strictly positive denominator.
 *
 * Called by every ibq_ arithmetic operation. ibz_t is fixed-width, so unreduced fractions
 * overflow within a few operations rather than merely growing.
 */
void ibq_reduce(ibq_t *x);

/** @brief sum=a+b
 */
void ibq_add(ibq_t *sum, const ibq_t *a, const ibq_t *b);

/** @brief diff=a-b
 */
void ibq_sub(ibq_t *diff, const ibq_t *a, const ibq_t *b);

/** @brief neg=-x
 */
void ibq_neg(ibq_t *neg, const ibq_t *x);

/** @brief abs=|x|
 */
void ibq_abs(ibq_t *abs, const ibq_t *x);

/** @brief prod=a*b
 */
void ibq_mul(ibq_t *prod, const ibq_t *a, const ibq_t *b);

/** @brief inv=1/x
 *
 * @returns 0 if x is 0, 1 if inverse exists and was computed
 */
int ibq_inv(ibq_t *inv, const ibq_t *x);

/** @brief inv=x/y
 *
 * @returns 0 if x is 0, 1 if quotient exists and was computed
 */
int ibq_div(ibq_t *frac, const ibq_t *x, const ibq_t *y);

/** @brief Compare a and b
 *
 * @returns a positive value if a > b, zero if a = b, and a negative value if a < b
 */
int ibq_cmp(const ibq_t *a, const ibq_t *b);

/** @brief Test if x is 0
 *
 * @returns 1 if x=0, 0 otherwise
 */
int ibq_is_zero(const ibq_t *x);

/** @brief Test if x is 1
 *
 * @returns 1 if x=1, 0 otherwise
 */
int ibq_is_one(const ibq_t *x);

/** @brief Set q to a/b if b not 0
 *
 * @returns 1 if b not 0 and q is set, 0 otherwise
 */
int ibq_set(ibq_t *q, const ibz_t *a, const ibz_t *b);

/** @brief Copy value into target
 */
void ibq_copy(ibq_t *target, const ibq_t *value);

/** @brief Checks if q is an integer
 *
 * @returns 1 if yes, 0 if not
 */
int ibq_is_ibz(const ibq_t *q);

/**
 * @brief Converts a fraction q to an integer y, if q is an integer.
 *
 * @returns 1 if z is an integer, 0 if not
 */
int ibq_to_ibz(ibz_t *z, const ibq_t *q);
/** @}
 */

/**
 * @ingroup lll_internal
 * @defgroup quat_lll_verify_helpers Helper functions for lll verification in dimension 4
 * @{
 */

/** @brief LLL parameters (delta = 3/4, eta = 51/100) satisfied by the constant-time reducer.
 *
 * The CT path Gauss-reduces a rank-2 Z[i] lattice, so its rank-4 Z-basis meets the classical
 * delta = 3/4 bound but not the delta = 99/100 the old L2 reducer targeted. See the derivation
 * above the definition in lll_verification.c.
 */
void quat_lll_set_ct_ibq_parameters(ibq_t *delta, ibq_t *eta);

/** @brief Set an ibq vector to 4 given integer coefficients
 */
void ibq_vec_4_copy_ibz(ibq_vec_4_t *vec,
                        const ibz_t *coeff0,
                        const ibz_t *coeff1,
                        const ibz_t *coeff2,
                        const ibz_t *coeff3);

/** @brief Bilinear form vec00*vec10+vec01*vec11+q*vec02*vec12+q*vec03*vec13 for ibz_q
 */
void quat_lll_bilinear(ibq_t *b, const ibq_vec_4_t *vec0, const ibq_vec_4_t *vec1, const ibz_t *q);

/** @brief Outputs the transposition of the orthogonalised matrix of mat (as fractions)
 *
 * For the bilinear form vec00*vec10+vec01*vec11+q*vec02*vec12+q*vec03*vec13
 */
void quat_lll_gram_schmidt_transposed_with_ibq(ibq_mat_4x4_t *orthogonalised_transposed,
                                               const ibz_mat_4x4_t *mat,
                                               const ibz_t *q);

/** @brief Verifies if mat is lll-reduced for parameter coeff and norm defined by q
 *
 * For the bilinear form vec00*vec10+vec01*vec11+q*vec02*vec12+q*vec03*vec13
 */
int quat_lll_verify(const ibz_mat_4x4_t *mat, const ibq_t *delta, const ibq_t *eta, const quat_alg_t *alg);
/** @}
 */

/**
 * @defgroup quat_cvp_helpers Helper functions for 2x2 cvp
 * @{
 */

/** @brief Basis of the integral lattice represented by basis, which is small for the norm x^2 + y^2 (in standard basis)
 *
 * Additionally, the first vector in the basis has a smaller norm than the second one.
 *
 * Algorithm 1.3.14 from Henri Cohen's "A Course in Computational Algebraic Number Theory" (Springer Verlag, in series
 * "Graduate texts in Mathematics") from 1993 which finds a shortest vector in the lattice.
 *
 * @param reduced Output: Matrix of 2 column vectors of small norm x^2 + y^2 which are a basis of the lattice the basis
 * argument represents
 * @param basis Basis of a rank 2 lattice in dimension 2
 */
void quat_dim2_lattice_short_basis(ibz_mat_2x2_t *reduced, const ibz_mat_2x2_t *basis);

/** @brief Checks if the vector (coord1,coord2) has integer coordinates in basis
 *
 * @param basis Rank 2 matrix
 * @param coord1
 * @param coord2
 * @returns 1 if the vector (coord1,coord2) has integer coordinates in basis, 0 otherwise
 */
int quat_dim2_lattice_contains(const ibz_mat_2x2_t *basis, const ibz_t *coord1, const ibz_t *coord2);

/** @brief v11*v21 + v12*v22
 *
 * This defines a bilinear form in dimension 2 where v11,v12 are coordinates of the first vector, v21,v22 of the second
 * vector
 *
 * @param res Output: v11*v21+v12*v22
 * @param v11
 * @param v12
 * @param v21
 * @param v22
 */
void quat_dim2_lattice_bilinear(ibz_t *res, const ibz_t *v11, const ibz_t *v12, const ibz_t *v21, const ibz_t *v22);

/** @brief coord1^2 + coord2^2
 *
 * This defines a quadratic form in dimension 2 where coord1 is the first and coord2 the second coordinate of the vector
 * on which it is evaluated
 *
 * @param norm Output: coord1^2 + coord2^2
 * @param coord1
 * @param coord2
 */
void quat_dim2_lattice_norm(ibz_t *norm, const ibz_t *coord1, const ibz_t *coord2);
// end of 2d
/** @}
 */

// end of lll_internal
/** @}
 */
#endif
