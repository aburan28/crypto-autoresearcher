/*
 * ca_modarith.h - 64-bit modular arithmetic, Montgomery multiplication,
 * primality testing and integer factoring for word-sized moduli.
 *
 * All moduli are < 2^64.  Functions that use Montgomery representation
 * require an odd modulus.
 */
#ifndef CA_MODARITH_H
#define CA_MODARITH_H

#include "ca_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned __int128 ca_u128;
typedef __int128 ca_i128;

#ifdef CA_GLV_FIELD_COUNT
/* Diagnostic builds only (-DCA_GLV_FIELD_COUNT): deterministic counts of the
 * field multiplications, squarings and inversions (and the division steps of
 * the inversions' extended Euclid), booked by the phase glv_rho_solve is in.
 * Single-threaded use; the arithmetic itself is unchanged. */
#    define CA_FC_PHASES 6
enum { CA_FC_OUTSIDE, CA_FC_SETUP, CA_FC_BATCH, CA_FC_POST, CA_FC_ESCAPE, CA_FC_RESTART };
enum { CA_FC_MUL, CA_FC_SQR, CA_FC_INV, CA_FC_EUCLID, CA_FC_KINDS };
enum {
    CA_FC_EV_BATCHES,
    CA_FC_EV_BATCH_WALKS,
    CA_FC_EV_ESC2,
    CA_FC_EV_ESC4,
    CA_FC_EV_RESTARTS,
    CA_FC_EV_RETRIES,
    CA_FC_EV_N
};
extern uint64_t ca_fc_cnt[CA_FC_PHASES][CA_FC_KINDS];
extern uint64_t ca_fc_ev[CA_FC_EV_N];
extern uint32_t ca_fc_phase;
CA_API void ca_fc_reset(void);
/* out: CA_FC_PHASES * CA_FC_KINDS counts, then CA_FC_EV_N event counts. */
CA_API void ca_fc_read(uint64_t *out);
#    define CA_FC_ADD(kind, n) (ca_fc_cnt[ca_fc_phase][(kind)] += (n))
#else
#    define CA_FC_ADD(kind, n) ((void)0)
#endif

/* ---- plain modular arithmetic ------------------------------------------ */

static inline uint64_t ca_addmod(uint64_t a, uint64_t b, uint64_t m)
{
    /* assumes a, b < m */
    uint64_t s = a + b;
    if (s < a || s >= m) s -= m;
    return s;
}

static inline uint64_t ca_submod(uint64_t a, uint64_t b, uint64_t m)
{
    return a >= b ? a - b : a + (m - b);
}

static inline uint64_t ca_mulmod(uint64_t a, uint64_t b, uint64_t m)
{
    return (uint64_t)(((ca_u128)a * b) % m);
}

CA_API uint64_t ca_powmod(uint64_t base, uint64_t exp, uint64_t m);
/* Modular inverse; returns 0 if gcd(a, m) != 1. */
CA_API uint64_t ca_invmod(uint64_t a, uint64_t m);
CA_API uint64_t ca_gcd(uint64_t a, uint64_t b);
/* Extended gcd on unsigned inputs: returns g and x with a*x == g (mod m). */
CA_API uint64_t ca_isqrt(uint64_t n);          /* floor(sqrt(n)) */
CA_API uint64_t ca_iroot(uint64_t n, unsigned k); /* floor(n^(1/k)) */
/* Square root modulo an odd prime p (Tonelli-Shanks). Returns 1 on success. */
CA_API int ca_sqrtmod_prime(uint64_t a, uint64_t p, uint64_t *root);
/* Legendre symbol a^((p-1)/2): returns 0, 1 or -1. */
CA_API int ca_legendre(uint64_t a, uint64_t p);

/* Chinese remainder theorem for two coprime moduli. Result mod m1*m2. */
CA_API uint64_t ca_crt2(uint64_t r1, uint64_t m1, uint64_t r2, uint64_t m2);

/* ---- Montgomery arithmetic (odd modulus) ------------------------------- */

typedef struct ca_mont {
    uint64_t p;     /* odd modulus */
    uint64_t pinv;  /* -p^{-1} mod 2^64 */
    uint64_t r1;    /* R mod p (Montgomery form of 1) */
    uint64_t r2;    /* R^2 mod p */
    uint64_t r3;    /* R^3 mod p */
} ca_mont;

CA_API int ca_mont_init(ca_mont *m, uint64_t p);

/* t * R^{-1} mod p, canonical, for t < p * 2^64 (which holds whenever t is
 * a product of two residues < p, or a single word).
 *
 * Subtraction form: with u = t * p^{-1} mod 2^64, t - u*p is divisible by
 * 2^64 and (t - u*p) / 2^64 = hi(t) - hi(u*p) lies in (-p, p), so one
 * conditional add of p finishes it.  That is the same residue the addition
 * form t + u'*p (u' = -u) reaches, without its 128-bit add, carry test and
 * final compare.  p^{-1} is -pinv, so the struct is unchanged. */
static inline uint64_t ca_mont_redc(const ca_mont *m, ca_u128 t)
{
    uint64_t u = (uint64_t)t * ((uint64_t)0 - m->pinv);
    uint64_t hi = (uint64_t)(t >> 64);
    uint64_t mh = (uint64_t)(((ca_u128)u * m->p) >> 64);
    uint64_t r = hi - mh;
    if (hi < mh) r += m->p;
    return r;
}

static inline uint64_t ca_mont_mul(const ca_mont *m, uint64_t a, uint64_t b)
{
    CA_FC_ADD(CA_FC_MUL, 1);
    return ca_mont_redc(m, (ca_u128)a * b);
}

static inline uint64_t ca_mont_sqr(const ca_mont *m, uint64_t a)
{
    CA_FC_ADD(CA_FC_SQR, 1);
    return ca_mont_redc(m, (ca_u128)a * a);
}

static inline uint64_t ca_mont_to(const ca_mont *m, uint64_t a)
{
    return ca_mont_mul(m, a % m->p, m->r2);
}

static inline uint64_t ca_mont_from(const ca_mont *m, uint64_t a)
{
    return ca_mont_redc(m, (ca_u128)a);
}

CA_API uint64_t ca_mont_pow(const ca_mont *m, uint64_t a, uint64_t e);
/* Inverse in Montgomery form (input and output in Montgomery form). */
CA_API uint64_t ca_mont_inv(const ca_mont *m, uint64_t a);

/* ---- primes and factoring --------------------------------------------- */

CA_API int ca_is_prime(uint64_t n);          /* deterministic for 64-bit */
CA_API uint64_t ca_next_prime(uint64_t n);   /* smallest prime > n; 0 if none fits in 64 bits */

#define CA_MAX_FACTORS 16

typedef struct ca_factor {
    uint64_t p;
    unsigned e;
} ca_factor;

typedef struct ca_factorization {
    ca_factor f[CA_MAX_FACTORS];
    unsigned count;
} ca_factorization;

/* Full factorisation of a 64-bit integer (trial division + Pollard-Brent). */
CA_API ca_status ca_factorize(uint64_t n, ca_factorization *out);

/* Multiplicative order of a modulo prime p (p-1 factored internally). */
CA_API uint64_t ca_mult_order(uint64_t a, uint64_t p);
/* Smallest primitive root modulo prime p, or 0 if p is not prime. */
CA_API uint64_t ca_primitive_root(uint64_t p);

/* Sieve of Eratosthenes: fills primes[] with primes <= bound. Returns count.
 * If primes == NULL only counts. */
CA_API size_t ca_sieve_primes(uint64_t bound, uint32_t *primes, size_t cap);

#ifdef __cplusplus
}
#endif
#endif /* CA_MODARITH_H */
