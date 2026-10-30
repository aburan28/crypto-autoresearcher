/*
 * ca_group.h - abstract finite cyclic group interface.
 *
 * Every generic algorithm in the library (BSGS, rho, kangaroo, grumpy
 * giants, Pohlig-Hellman, Cheon) is written against this interface.  Two
 * concrete groups ship with the library:
 *
 *   - ca_group_zp   : a subgroup of the multiplicative group (Z/pZ)^*
 *   - ca_group_ec   : a subgroup of E(F_p) for a short Weierstrass curve
 *
 * Elements are 32-byte POD values (ca_elem).  A group is a small opaque
 * object created by one of the constructors below.  Groups are immutable
 * after construction and may be shared freely between threads.
 */
#ifndef CA_GROUP_H
#define CA_GROUP_H

#include "ca_types.h"
#include "ca_modarith.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ca_group ca_group;

typedef enum ca_group_kind {
    CA_GROUP_ZP = 1,
    CA_GROUP_EC = 2
} ca_group_kind;

/* The dispatch table.  Only needed if you implement your own group. */
typedef struct ca_group_vtable {
    void (*op)(const ca_group *g, ca_elem *r, const ca_elem *a, const ca_elem *b);
    void (*dbl)(const ca_group *g, ca_elem *r, const ca_elem *a);
    void (*inv)(const ca_group *g, ca_elem *r, const ca_elem *a);
    void (*identity)(const ca_group *g, ca_elem *r);
    int (*is_identity)(const ca_group *g, const ca_elem *a);
    int (*equal)(const ca_group *g, const ca_elem *a, const ca_elem *b);
    /* Canonical 64-bit hash of an element (equal elements hash equal). */
    uint64_t (*hash)(const ca_group *g, const ca_elem *a);
    /* Batched op: r[i] = a[i] * b[i] for i < n.  scratch has 2*n elements. */
    void (*batch_op)(const ca_group *g, ca_elem *r, const ca_elem *a,
                     const ca_elem *b, size_t n, uint64_t *scratch);
    /* Conversion to/from the public word representation. */
    int (*encode)(const ca_group *g, ca_elem *r, const uint64_t *words);
    void (*decode)(const ca_group *g, uint64_t *words, const ca_elem *a);
    /* Validate membership (on curve / nonzero residue). */
    int (*is_valid)(const ca_group *g, const ca_elem *a);
    /* Replace a by the canonical representative of {a, -a}; returns 1 if a
     * was negated.  NULL when the group has no cheap negation (then the
     * negation map is unavailable). */
    int (*canonicalize)(const ca_group *g, ca_elem *a);
} ca_group_vtable;

struct ca_group {
    const ca_group_vtable *vt;
    ca_group_kind kind;
    uint64_t order;       /* order of the subgroup of interest (n) */
    uint64_t p;           /* field characteristic / modulus */
    uint64_t a, b;        /* curve coefficients (EC only, normal form) */
    ca_mont mont;         /* Montgomery context for F_p */
    uint64_t a_mont, b_mont;
    uint64_t cofactor;    /* #E / n or (p-1)/n when known, else 0 */

    /* Optional efficiently-computable endomorphism psi(P) = endo_lambda * P
     * on a CM curve, enabled by ca_curve_group (see ca_curve.h) when the
     * subgroup order is compatible.  endo_kind: 0 none, 1 j-invariant 0
     * (psi(x,y) = (c*x, -y)), 2 j-invariant 1728 (psi(x,y) = (-x, c*y)).
     * aut_order is the size of <psi> (4 or 6); the rho walk folds the search
     * space by it.  c is endo_c_mont (Montgomery form). */
    uint32_t endo_kind;
    uint32_t aut_order;
    uint64_t endo_lambda;
    uint64_t endo_c_mont;
};

/* ---- constructors ------------------------------------------------------ */

/* Subgroup of (Z/pZ)^* of order `order` (0 => p-1, i.e. the full group).
 * p must be an odd prime.  Fails if order does not divide p-1. */
CA_API ca_status ca_group_zp_init(ca_group *g, uint64_t p, uint64_t order);

/* Subgroup of order `order` of E(F_p): y^2 = x^3 + a x + b.  p must be an
 * odd prime > 3, and the curve must be non-singular.  order may be 0 if
 * unknown (some algorithms then refuse to run). */
CA_API ca_status ca_group_ec_init(ca_group *g, uint64_t p, uint64_t a, uint64_t b,
                                  uint64_t order);

/* ---- element operations (thin wrappers around the vtable) -------------- */

static inline void ca_group_op(const ca_group *g, ca_elem *r, const ca_elem *a, const ca_elem *b)
{ g->vt->op(g, r, a, b); }
static inline void ca_group_dbl(const ca_group *g, ca_elem *r, const ca_elem *a)
{ g->vt->dbl(g, r, a); }
static inline void ca_group_inv(const ca_group *g, ca_elem *r, const ca_elem *a)
{ g->vt->inv(g, r, a); }
static inline void ca_group_identity(const ca_group *g, ca_elem *r)
{ g->vt->identity(g, r); }
static inline int ca_group_is_identity(const ca_group *g, const ca_elem *a)
{ return g->vt->is_identity(g, a); }
static inline int ca_group_equal(const ca_group *g, const ca_elem *a, const ca_elem *b)
{ return g->vt->equal(g, a, b); }
static inline uint64_t ca_group_hash(const ca_group *g, const ca_elem *a)
{ return g->vt->hash(g, a); }
static inline int ca_group_encode(const ca_group *g, ca_elem *r, const uint64_t *words)
{ return g->vt->encode(g, r, words); }
static inline void ca_group_decode(const ca_group *g, uint64_t *words, const ca_elem *a)
{ g->vt->decode(g, words, a); }
static inline int ca_group_is_valid(const ca_group *g, const ca_elem *a)
{ return g->vt->is_valid(g, a); }
static inline int ca_group_has_negation_map(const ca_group *g)
{ return g->vt->canonicalize != NULL; }
static inline int ca_group_canonicalize(const ca_group *g, ca_elem *a)
{ return g->vt->canonicalize ? g->vt->canonicalize(g, a) : 0; }
static inline void ca_group_batch_op(const ca_group *g, ca_elem *r, const ca_elem *a,
                                     const ca_elem *b, size_t n, uint64_t *scratch)
{ g->vt->batch_op(g, r, a, b, n, scratch); }

/* Scalar multiplication r = k * a (additive notation) using double-and-add.
 * Adds to *ops if non-NULL. */
CA_API void ca_group_mul(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                         uint64_t *ops);
/* r = a * b^-1 */
CA_API void ca_group_div(const ca_group *g, ca_elem *r, const ca_elem *a, const ca_elem *b);

/* Multiplicative order of an element (requires g->order != 0 and
 * factors g->order).  Returns 0 if the element is not in the subgroup. */
CA_API uint64_t ca_group_elem_order(const ca_group *g, const ca_elem *a);

/* A random element of the subgroup: g^k for random k (given generator). */
CA_API void ca_group_random_power(const ca_group *g, ca_elem *r, const ca_elem *gen,
                                  uint64_t seed, uint64_t *k_out);

/* Find a generator of the order-n subgroup (Z_p^*: needs cofactor; EC:
 * random point times cofactor).  seed 0 = random. */
CA_API ca_status ca_group_find_generator(const ca_group *g, ca_elem *gen, uint64_t seed);

/* Human readable dump: writes "x" or "(x, y)" into buf. */
CA_API void ca_group_format(const ca_group *g, const ca_elem *a, char *buf, size_t len);

/* ---- elliptic curve helpers -------------------------------------------- */

/* Lift x to a point on the curve if possible (chooses the smaller y). */
CA_API int ca_ec_lift_x(const ca_group *g, ca_elem *r, uint64_t x);
/* Apply the curve's endomorphism psi once (a copy when none is enabled). */
CA_API void ca_ec_endo(const ca_group *g, ca_elem *r, const ca_elem *a);
/* Variable-time j=0 tau-adic scalar multiplication for public scalars.
 * Returns 0 without changing r when this curve has no compatible
 * endomorphism. The counts distinguish tau, mixed-addition, and tripling
 * operations; they are not generic group-op counts. */
CA_API int ca_ec_mul_tau2(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                          uint64_t *tau_steps, uint64_t *adds);
CA_API int ca_ec_mul_tau4(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                          uint64_t *tau_steps, uint64_t *adds);
CA_API int ca_ec_mul_tau4_tripling(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                                   uint64_t *tau_steps, uint64_t *adds, uint64_t *triples);
/* Prime-field j=0 scalar multiplication using the Eisenstein endomorphism
 * tau = 1 - omega and a width-2 tau-NAF.  This requires an enabled j=0
 * endomorphism and a point in the configured order-n subgroup.  Returns 1
 * when used, 0 when unavailable (r is then untouched).  The
 * optional counts are tau evaluations and mixed additions, respectively;
 * they are not interchangeable with generic group-op counts. */
CA_API int ca_ec_mul_tau2(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                          uint64_t *tau_steps, uint64_t *adds);
/* Width-4 variant with the paper's nine seed coefficients and sixfold unit
 * orbit.  Setup is charged on every call.  `adds` includes projective
 * additions and doublings used to prepare the seed table. */
CA_API int ca_ec_mul_tau4(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                          uint64_t *tau_steps, uint64_t *adds);
/* Rewrites pairs of tau powers as powers of 3 and evaluates them with the
 * Jacobian tripling formula.  `triples` counts those evaluations separately. */
CA_API int ca_ec_mul_tau4_tripling(const ca_group *g, ca_elem *r, const ca_elem *a, uint64_t k,
                                   uint64_t *tau_steps, uint64_t *adds, uint64_t *triples);
/* Paper's 4S+6M Jacobian tripling formula for a=0, converted back to the
 * library's affine representation.  Returns 1 on a supported curve and 0
 * otherwise; valid for any curve point, with aliasing allowed. */
CA_API int ca_ec_triple_j0(const ca_group *g, ca_elem *r, const ca_elem *a);
/* Random point on the curve. */
CA_API void ca_ec_random_point(const ca_group *g, ca_elem *r, uint64_t seed);
/* Count points on E(F_p) using Mestre's baby-step giant-step method.
 * Practical for p up to ~2^60 (cost O(p^{1/4})). */
CA_API ca_status ca_ec_count_points(uint64_t p, uint64_t a, uint64_t b, uint64_t *order,
                                    ca_stats *st);

#ifdef __cplusplus
}
#endif
#endif /* CA_GROUP_H */
