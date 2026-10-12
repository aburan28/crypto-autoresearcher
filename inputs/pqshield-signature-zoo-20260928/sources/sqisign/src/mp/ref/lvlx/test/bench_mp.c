#include <bench.h>
#include <bench_test_arguments.h>
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

#include <mp.h>
#include <prng.h>
#include <rng.h>

#include "mp_test_utils.h"

#define STRINGIFY2(x) #x
#define STRINGIFY(x) STRINGIFY2(x)

#define MAXBITS (IBZ_NLIMBS * NUM_BITS_LIMB)

#define BENCH_SAMPLES 20

#define PEEK_WORD(x)                                                                                                   \
    do {                                                                                                               \
        asm volatile("" ::"m"(x) : "memory");                                                                          \
    } while (0)

static uint64_t
median_cycles(uint64_t *runs, size_t n)
{
    qsort(runs, n, sizeof runs[0], CMPFUNC);
    return runs[n / 2];
}

// One low byte of the value, only used to keep results live and stop the compiler from eliding calls.
static uint32_t
ibz_peek(const ibz_t *x)
{
    for (int i = 0; i < IBZ_NLIMBS; ++i)
        PEEK_WORD(x->limbs[i]);
    return (uint32_t)ibz_get(x) & 0xff;
}

static uint64_t
time_calls(int iterations, void (*step)(void *), void *ctx)
{
    uint64_t cycle_runs[BENCH_SAMPLES];
    for (int i = 0; i < BENCH_SAMPLES; i++) {
        uint64_t cycles1 = cpucycles();
        for (int n = 0; n < iterations; n++) {
            step(ctx);
        }
        uint64_t cycles2 = cpucycles();
        cycle_runs[i] = cycles2 - cycles1;
    }
    return median_cycles(cycle_runs, BENCH_SAMPLES);
}

static void
report(const char *name, int bits, uint64_t cycles_per_call, uint32_t peek)
{
    printf("  %-14s (%5d bits) runs in %12" PRIu64 " cycles, (%u ignore me)\n", name, bits, cycles_per_call, peek);
}

/******************************
Size-swept operations: one context struct + step() per operation, benchmarked at a caller-supplied operand size.
******************************/

typedef struct
{
    ibz_t a, b;
    int bits;
} binop_ctx_t;

static void
step_ibz_add(void *v)
{
    binop_ctx_t *c = v;
    ibz_add_and_set_bound(&c->a, &c->a, &c->b, c->bits);
    ibz_add_and_set_bound(&c->b, &c->b, &c->a, c->bits);
}

static void
bench_ibz_add(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_add, &c);
    report("ibz_add", bits, cycles / (2 * iterations), ibz_peek(&c.b));
}

static void
step_ibz_sub(void *v)
{
    binop_ctx_t *c = v;
    ibz_sub(&c->a, &c->a, &c->b);
    ibz_set_bound(&c->a, c->bits);
    ibz_sub(&c->b, &c->b, &c->a);
    ibz_set_bound(&c->b, c->bits);
}

static void
bench_ibz_sub(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_sub, &c);
    report("ibz_sub", bits, cycles / (2 * iterations), ibz_peek(&c.b));
}

static void
step_ibz_neg(void *v)
{
    binop_ctx_t *c = v;
    ibz_neg(&c->a, &c->a);
    ibz_neg(&c->b, &c->b);
}

static void
bench_ibz_neg(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_neg, &c);
    report("ibz_neg", bits, cycles / (2 * iterations), ibz_peek(&c.b));
}

static void
step_ibz_abs(void *v)
{
    binop_ctx_t *c = v;
    ibz_abs(&c->a, &c->a);
    ibz_abs(&c->b, &c->b);
}

static void
bench_ibz_abs(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_abs, &c);
    report("ibz_abs", bits, cycles / (2 * iterations), ibz_peek(&c.b));
}

static void
step_ibz_cmp(void *v) // read-only, so mutate afterwards to keep the call live (see file header)
{
    binop_ctx_t *c = v;
    int z = ibz_cmp(&c->a, &c->b);
    PEEK_WORD(z);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_cmp(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_cmp, &c);
    report("ibz_cmp", bits, cycles / iterations, ibz_peek(&c.a));
}

static void
step_ibz_bitsize(void *v) // read-only, so mutate afterwards to keep the call live (see file header)
{
    binop_ctx_t *c = v;
    int z = ibz_bitsize(&c->a);
    PEEK_WORD(z);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_bitsize(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_bitsize, &c);
    report("ibz_bitsize", bits, cycles / iterations, ibz_peek(&c.a));
}

static void
step_ibz_mul(void *v)
{
    binop_ctx_t *c = v;
    ibz_mul(&c->a, &c->a, &c->b);
    ibz_set_bound(&c->a, c->bits);
    ibz_mul(&c->b, &c->b, &c->a);
    ibz_set_bound(&c->b, c->bits);
}

static void
bench_ibz_mul(int iterations, int bits)
{
    binop_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    rand_ibz_signed(&c.b, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_mul, &c);
    report("ibz_mul", bits, cycles / (2 * iterations), ibz_peek(&c.b));
}

typedef struct
{
    ibz_t a, b, q, r;
    int bits;
} divmod_ctx_t;

static void
step_ibz_div(void *v)
{
    divmod_ctx_t *c = v;
    ibz_div(&c->q, &c->r, &c->a, &c->b);
    ibz_add_and_set_bound(&c->a, &c->a, &c->b, c->bits);
}

static void
bench_ibz_div(int iterations, int bits)
{
    divmod_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    do {
        rand_ibz_signed(&c.b, bits);
    } while (ibz_is_zero(&c.b));
    uint64_t cycles = time_calls(iterations, step_ibz_div, &c);
    report("ibz_div", bits, cycles / iterations, ibz_peek(&c.q));
}

static void
step_ibz_mod(void *v)
{
    divmod_ctx_t *c = v;
    ibz_mod(&c->r, &c->a, &c->b);
    ibz_add_and_set_bound(&c->a, &c->a, &c->b, c->bits);
}

static void
bench_ibz_mod(int iterations, int bits)
{
    divmod_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    do {
        rand_ibz_signed(&c.b, bits);
    } while (ibz_is_zero(&c.b));
    uint64_t cycles = time_calls(iterations, step_ibz_mod, &c);
    report("ibz_mod", bits, cycles / iterations, ibz_peek(&c.r));
}

static void
step_ibz_mod_ui(void *v)
{
    divmod_ctx_t *c = v;
    int z = ibz_mod_ui(&c->a, 1000003);
    PEEK_WORD(z);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_mod_ui(int iterations, int bits)
{
    divmod_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_mod_ui, &c);
    report("ibz_mod_ui", bits, cycles / iterations, ibz_peek(&c.a));
}

static void
step_ibz_divides(void *v)
{
    divmod_ctx_t *c = v;
    int z = ibz_divides(&c->a, &c->b);
    PEEK_WORD(z);
    ibz_add_and_set_bound(&c->a, &c->a, &c->b, c->bits);
}

static void
bench_ibz_divides(int iterations, int bits)
{
    divmod_ctx_t c = { .bits = bits };
    rand_ibz_signed(&c.a, bits);
    do {
        rand_ibz_signed(&c.b, bits);
    } while (ibz_is_zero(&c.b));
    uint64_t cycles = time_calls(iterations, step_ibz_divides, &c);
    report("ibz_divides", bits, cycles / iterations, ibz_peek(&c.a));
}

typedef struct
{
    ibz_t a, out;
    uint32_t e;
    int bits;
} shift_ctx_t;

static void
step_ibz_mul_2exp(void *v)
{
    shift_ctx_t *c = v;
    ibz_mul_2exp(&c->out, &c->a, c->e);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_mul_2exp(int iterations, int bits)
{
    shift_ctx_t c = { .bits = bits, .e = 1 + rand_u32_range(64) };
    rand_ibz_nonneg(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_mul_2exp, &c);
    report("ibz_mul_2exp", bits, cycles / iterations, ibz_peek(&c.out));
}

static void
step_ibz_div_2exp(void *v)
{
    shift_ctx_t *c = v;
    ibz_div_2exp(&c->out, &c->a, c->e);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_div_2exp(int iterations, int bits)
{
    shift_ctx_t c = { .bits = bits, .e = 1 + rand_u32_range(64) };
    rand_ibz_nonneg(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_div_2exp, &c);
    report("ibz_div_2exp", bits, cycles / iterations, ibz_peek(&c.out));
}

static void
step_ibz_mod2exp(void *v)
{
    shift_ctx_t *c = v;
    ibz_mod2exp(&c->out, &c->a, c->e);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_mod2exp(int iterations, int bits)
{
    shift_ctx_t c = { .bits = bits, .e = 1 + rand_u32_range(64) };
    rand_ibz_nonneg(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_mod2exp, &c);
    report("ibz_mod2exp", bits, cycles / iterations, ibz_peek(&c.out));
}

typedef struct
{
    ibz_t a;
    int bits;
} unary_ctx_t;

static void
step_ibz_two_adic(void *v)
{
    unary_ctx_t *c = v;
    int z = ibz_two_adic(&c->a);
    PEEK_WORD(z);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_two, c->bits);
}

static void
bench_ibz_two_adic(int iterations, int bits)
{
    unary_ctx_t c = { .bits = bits };
    do {
        rand_ibz_nonneg(&c.a, bits);
    } while (ibz_is_zero(&c.a));
    uint64_t cycles = time_calls(iterations, step_ibz_two_adic, &c);
    report("ibz_two_adic", bits, cycles / iterations, ibz_peek(&c.a));
}

typedef struct
{
    ibz_t x, out;
    uint32_t e;
    int bits;
} pow_ctx_t;

static void
step_ibz_pow(void *v)
{
    pow_ctx_t *c = v;
    ibz_pow(&c->out, &c->x, c->e, 5);
    ibz_add_and_set_bound(&c->x, &c->x, &ibz_const_one, c->bits);
}

static void
bench_ibz_pow(int iterations, int bits)
{
    pow_ctx_t c = { .bits = bits, .e = 3 + rand_u32_range(13) };
    do {
        rand_ibz_nonneg(&c.x, bits);
    } while (ibz_is_zero(&c.x));
    uint64_t cycles = time_calls(iterations, step_ibz_pow, &c);
    report("ibz_pow", bits, cycles / iterations, ibz_peek(&c.out));
}

typedef struct
{
    ibz_t a, b, g;
    int bits;
} gcd_ctx_t;

static void
step_ibz_gcd(void *v)
{
    gcd_ctx_t *c = v;
    ibz_gcd(&c->g, &c->a, &c->b);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
    ibz_add_and_set_bound(&c->b, &c->b, &ibz_const_one, c->bits);
}

static void
bench_ibz_gcd(int iterations, int bits)
{
    gcd_ctx_t c = { .bits = bits };
    do {
        rand_ibz_nonneg(&c.a, bits);
    } while (ibz_is_zero(&c.a));
    do {
        rand_ibz_nonneg(&c.b, bits);
    } while (ibz_is_zero(&c.b));
    uint64_t cycles = time_calls(iterations, step_ibz_gcd, &c);
    report("ibz_gcd", bits, cycles / iterations, ibz_peek(&c.g));
}

typedef struct
{
    ibz_t a, b, g, u, v;
    int bits;
} xgcd_ctx_t;

static void
step_ibz_xgcd(void *vv)
{
    xgcd_ctx_t *c = vv;
    ibz_xgcd(&c->g, &c->u, &c->v, &c->a, &c->b);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
    ibz_add_and_set_bound(&c->b, &c->b, &ibz_const_one, c->bits);
}

static void
bench_ibz_xgcd(int iterations, int bits)
{
    xgcd_ctx_t c = { .bits = bits };
    do {
        rand_ibz_nonneg(&c.a, bits);
    } while (ibz_is_zero(&c.a));
    do {
        rand_ibz_nonneg(&c.b, bits);
    } while (ibz_is_zero(&c.b));
    uint64_t cycles = time_calls(iterations, step_ibz_xgcd, &c);
    report("ibz_xgcd", bits, cycles / iterations, ibz_peek(&c.g));
}

typedef struct
{
    ibz_t a, s;
    int bits;
} sqrtfloor_ctx_t;

static void
step_ibz_sqrt_floor(void *v)
{
    sqrtfloor_ctx_t *c = v;
    ibz_sqrt_floor(&c->s, &c->a);
    ibz_add_and_set_bound(&c->a, &c->a, &ibz_const_one, c->bits);
}

static void
bench_ibz_sqrt_floor(int iterations, int bits)
{
    sqrtfloor_ctx_t c = { .bits = bits };
    rand_ibz_nonneg(&c.a, bits);
    uint64_t cycles = time_calls(iterations, step_ibz_sqrt_floor, &c);
    report("ibz_sqrt_floor", bits, cycles / iterations, ibz_peek(&c.s));
}

/******************************
Modular arithmetic: swept over test_primes[] (increasing modulus size), rather than a single fixed-size modulus --
mp.c no longer fixes numwords to one compile-time field size, so these are meaningful at any modulus size that fits.
******************************/

typedef struct
{
    ibz_t a, modp;
} modop_ctx_t;

static void
step_ibz_legendre(void *v)
{
    modop_ctx_t *c = v;
    int z = ibz_legendre(&c->a, &c->modp);
    PEEK_WORD(z);
    ibz_add(&c->a, &c->a, &ibz_const_one);
    ibz_mod(&c->a, &c->a, &c->modp);
}

static void
bench_ibz_legendre(int iterations, const ibz_t *modp)
{
    modop_ctx_t c = { 0 };
    ibz_copy(&c.modp, modp);
    do {
        rand_ibz_nonneg(&c.a, modp->bitlen - 2);
    } while (ibz_is_zero(&c.a));
    uint64_t cycles = time_calls(iterations, step_ibz_legendre, &c);
    report("ibz_legendre", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.a));
}

typedef struct
{
    ibz_t a, inv, modp;
} invmod_ctx_t;

static void
step_ibz_invmod(void *v)
{
    invmod_ctx_t *c = v;
    (void)ibz_invmod(&c->inv, &c->a, &c->modp);
    ibz_add(&c->a, &c->a, &ibz_const_one);
    ibz_mod(&c->a, &c->a, &c->modp);
}

static void
bench_ibz_invmod(int iterations, const ibz_t *modp)
{
    invmod_ctx_t c = { 0 };
    ibz_copy(&c.modp, modp);
    do {
        rand_ibz_nonneg(&c.a, modp->bitlen - 2);
    } while (ibz_is_zero(&c.a));
    uint64_t cycles = time_calls(iterations, step_ibz_invmod, &c);
    report("ibz_invmod", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.inv));
}

typedef struct
{
    ibz_t x, e, out, modp;
} powmod_ctx_t;

static void
step_ibz_pow_mod(void *v)
{
    powmod_ctx_t *c = v;
    ibz_pow_mod(&c->out, &c->x, &c->e, &c->modp);
    ibz_add(&c->x, &c->x, &ibz_const_one);
    ibz_mod(&c->x, &c->x, &c->modp);
}

static void
bench_ibz_pow_mod(int iterations, const ibz_t *modp)
{
    powmod_ctx_t c = { 0 };
    ibz_copy(&c.modp, modp);
    rand_ibz_odd_positive(&c.x, modp->bitlen - 1);
    ibz_mod(&c.x, &c.x, modp);
    ibz_set(&c.e, (int32_t)(1 + rand_u32_range(30)), 6);
    uint64_t cycles = time_calls(iterations, step_ibz_pow_mod, &c);
    report("ibz_pow_mod", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.out));
}

typedef struct
{
    ibz_t a, s, modp;
} sqrtmodp_ctx_t;

// a is always a genuine quadratic residue (r^2 mod p, computed once below) and never mutated: a
// non-residue is rejected by ibz_sqrt_mod_p right after its Legendre-symbol check, while an actual
// square forces the full square-root computation -- the worst case, and the one that matters when
// this runs against a value that really is a square.
static void
step_ibz_sqrt_mod_p(void *v)
{
    sqrtmodp_ctx_t *c = v;
    (void)ibz_sqrt_mod_p(&c->s, &c->a, &c->modp);
}

static void
bench_ibz_sqrt_mod_p(int iterations, const ibz_t *modp)
{
    sqrtmodp_ctx_t c = { 0 };
    ibz_copy(&c.modp, modp);
    ibz_t r = { 0 };
    rand_ibz_nonneg(&r, modp->bitlen - 2);
    ibz_mulmod(&c.a, &r, &r, modp); // a = r^2 mod p, a genuine quadratic residue
    uint64_t cycles = time_calls(iterations, step_ibz_sqrt_mod_p, &c);
    report("ibz_sqrt_mod_p", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.s));
}

typedef struct
{
    ibz_t p, r;
} sqrtm1_ctx_t;

static void
step_ibz_sqrt_m1_mod(void *v) // internally randomised, so no mutation is needed to keep the call live
{
    sqrtm1_ctx_t *c = v;
    ibz_sqrt_m1_mod(&c->r, &c->p);
}

// Caller must only pass a modp congruent to 1 mod 4 -- ibz_sqrt_m1_mod asserts it.
static void
bench_ibz_sqrt_m1_mod(int iterations, const ibz_t *modp)
{
    sqrtm1_ctx_t c = { 0 };
    ibz_copy(&c.p, modp);
    uint64_t cycles = time_calls(iterations, step_ibz_sqrt_m1_mod, &c);
    report("ibz_sqrt_m1_mod", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.r));
}

typedef struct
{
    ibz_t n;
} probprime_ctx_t;

// n is always the real test prime, never drifted: a genuine prime can never be rejected by
// Miller-Rabin, so it forces every one of the `reps` rounds on every call -- the worst case. Letting
// n drift (as an earlier version of this benchmark did) would mostly test composites instead, which
// get rejected after a single round and so read far faster; that made this benchmark measure "how
// fast can most odd numbers be rejected" rather than "how expensive is confirming an actual prime,"
// which is the case that matters when this runs against a real candidate. bench_ibz_probab_prime_random
// below runs the same step against a merely-random odd input, to show the other end of that range.
static void
step_ibz_probab_prime(void *v)
{
    probprime_ctx_t *c = v;
    int z = ibz_probab_prime(&c->n, 20);
    PEEK_WORD(z);
}

static void
bench_ibz_probab_prime(int iterations, const ibz_t *modp)
{
    probprime_ctx_t c = { 0 };
    ibz_copy(&c.n, modp);
    uint64_t cycles = time_calls(iterations, step_ibz_probab_prime, &c);
    report("ibz_probab_prime", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.n));
}

// Same op, but n is a merely-random odd number of the same size instead of a confirmed prime --
// almost certainly composite (primes near an N-bit number have density ~1/ln(2^N)), so this shows
// the fast-rejection end of ibz_probab_prime's range, opposite the guaranteed-worst-case reading
// above.
static void
bench_ibz_probab_prime_random(int iterations, const ibz_t *modp)
{
    probprime_ctx_t c = { 0 };
    rand_ibz_odd_positive(&c.n, modp->bitlen - 1);
    uint64_t cycles = time_calls(iterations, step_ibz_probab_prime, &c);
    report("ibz_probab_prime_random", modp->bitlen - 1, cycles / iterations, ibz_peek(&c.n));
}

// Spins for ~150ms of wall-clock-equivalent cycles before any sample is taken. Without this, whichever benchmark
// runs first pays for the CPU ramping up from an idle frequency state and for cold caches/branch predictors --
// empirically 5-10x higher than its true cost if the process starts after any idle period -- while every later
// benchmark in the same run reads correctly. That skew has nothing to do with operand size or the operation itself,
// so it must be paid once here rather than distorting whatever happens to be first in the sweep below.
static void
warmup_cpu(void)
{
    uint64_t start = cpucycles();
    volatile uint64_t sink = 0;
    while (cpucycles() - start < 400000000ULL) {
        sink += cpucycles();
    }
    (void)sink;
}

bool
mp_run(int iterations)
{
    bool OK = true;
    int n, i;
    uint64_t cycles1, cycles2;
    uint64_t cycle_runs[BENCH_SAMPLES];

    warmup_cpu();

    printf("\n-------------------------------------------------------------------------------------"
           "-------------------\n\n");
    printf("Benchmarking mp (ibz_t) big integer arithmetic for " STRINGIFY(SQISIGN_VARIANT) ": \n\n");

    /******************************
    Size-swept operations: operand size ranges over BITS/2, BITS, 3*BITS/2, 2*BITS.
    ******************************/

    static const int size_num[] = { 1, 1, 3, 2 };
    static const int size_den[] = { 2, 1, 2, 1 };
    static const char *size_label[] = { "BITS/2", "BITS", "3*BITS/2", "2*BITS" };

    for (size_t s = 0; s < sizeof(size_num) / sizeof(size_num[0]); s++) {
        int bits = BITS * size_num[s] / size_den[s];
        printf("\n-- operand size ~ %s (%d bits) --\n", size_label[s], bits);
        bench_ibz_add(iterations, bits);
        bench_ibz_sub(iterations, bits);
        bench_ibz_neg(iterations, bits);
        bench_ibz_abs(iterations, bits);
        bench_ibz_cmp(iterations, bits);
        bench_ibz_bitsize(iterations, bits);
        bench_ibz_mul(iterations, bits);
        bench_ibz_div(iterations, bits);
        bench_ibz_mod(iterations, bits);
        bench_ibz_mod_ui(iterations, bits);
        bench_ibz_divides(iterations, bits);
        bench_ibz_mul_2exp(iterations, bits);
        bench_ibz_div_2exp(iterations, bits);
        bench_ibz_mod2exp(iterations, bits);
        bench_ibz_two_adic(iterations, bits);
        bench_ibz_pow(iterations, bits);
        bench_ibz_gcd(iterations, bits);
        bench_ibz_xgcd(iterations, bits);
        bench_ibz_sqrt_floor(iterations, bits);
    }

    /******************************
    Modular arithmetic: swept over test_primes[] (increasing modulus size) instead of one fixed BENCH_PRIME, since
    numwords is now derived from the modulus itself rather than fixed to one compile-time field size.
    ******************************/

    for (size_t pi = 0; pi < NUM_TEST_PRIMES; pi++) {
        ibz_t modp = test_primes[pi];
        printf("\n-- modulus ~ %d bits (test_primes[%zu]) --\n", modp.bitlen - 1, pi);
        bench_ibz_legendre(iterations, &modp);
        bench_ibz_invmod(iterations, &modp);
        bench_ibz_pow_mod(iterations, &modp);
        bench_ibz_sqrt_mod_p(iterations, &modp);
        if ((ibz_get(&modp) & 3) == 1) { // ibz_sqrt_m1_mod asserts p = 1 mod 4
            bench_ibz_sqrt_m1_mod(iterations, &modp);
        }
        bench_ibz_probab_prime(iterations, &modp);
        bench_ibz_probab_prime_random(iterations, &modp);
    }

    /******************************
    Operations with their own fixed-size conventions, unrelated to test_primes[].
    ******************************/

    printf("\n-- fixed-size operations (unrelated to the modulus sweep above) --\n");

    // ibz_invmat (chains naturally: the output of one call is a valid input to the next, since the inverse of an
    // invertible matrix is itself invertible)
    ibz_t mr1 = { 0 }, mr2 = { 0 }, ms1 = { 0 }, ms2 = { 0 };
    int inv_e = MAXBITS / 4;
    ibz_set(&mr1, 1, 2);
    ibz_set(&ms2, 1, 2);
    rand_ibz_nonneg(&ms1, inv_e - 1);
    rand_ibz_nonneg(&mr2, inv_e - 1);
    mr2.limbs[0] &= ((digit_t)-1) << 1; // even, guarantees an odd (invertible) determinant
    for (i = 0; i < BENCH_SAMPLES; i++) {
        cycles1 = cpucycles();
        for (n = 0; n < iterations; n++) {
            (void)ibz_invmat(&mr1, &mr2, &ms1, &ms2, inv_e);
        }
        cycles2 = cpucycles();
        cycle_runs[i] = cycles2 - cycles1;
    }
    uint64_t invmat_cycles = median_cycles(cycle_runs, BENCH_SAMPLES);
    printf("  ibz_invmat runs in .............................................. %" PRIu64 " cycles, (%u ignore me)\n",
           invmat_cycles / iterations,
           ibz_peek(&mr1));

    // ibz_crt
    ibz_t cm1 = { 0 }, cm2 = { 0 }, cg = { 0 }, ca1 = { 0 }, ca2 = { 0 }, cx = { 0 };
    do {
        rand_ibz_odd_positive(&cm1, MAXBITS / 2 - 2);
        rand_ibz_odd_positive(&cm2, MAXBITS / 2 - 2);
        ibz_gcd(&cg, &cm1, &cm2);
    } while (!ibz_is_one(&cg));
    // Kept well below MAXBITS/2 so that diff_a.bitlen + u.bitlen (u from xgcd(m1,m2), bounded by ~m2.bitlen) stays
    // under ibz_crt's internal IBZ_NLIMBS * NUM_BITS_LIMB assertion. Re-pinned every iteration below since ibz_add
    // always grows its result's bit-length bound by one regardless of the mutated value.
    rand_ibz_signed(&ca1, MAXBITS / 4);
    rand_ibz_signed(&ca2, MAXBITS / 4);
    for (i = 0; i < BENCH_SAMPLES; i++) {
        cycles1 = cpucycles();
        for (n = 0; n < iterations; n++) {
            ibz_crt(&cx, &ca1, &ca1, &cm1, &cm2);
            ibz_add_and_set_bound(&ca1, &ca1, &ibz_const_one, MAXBITS / 4);
            ibz_add_and_set_bound(&ca2, &ca2, &ibz_const_one, MAXBITS / 4);
        }
        cycles2 = cpucycles();
        cycle_runs[i] = cycles2 - cycles1;
    }
    uint64_t crt_cycles = median_cycles(cycle_runs, BENCH_SAMPLES);
    printf("  ibz_crt runs in ................................................. %" PRIu64 " cycles, (%u ignore me)\n",
           crt_cycles / iterations,
           ibz_peek(&cx));

    return OK;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int iterations = 20 * SQISIGN_TEST_REPS;
    int help = 0;
    int seed_set = 0;

#ifndef NDEBUG
    fprintf(stderr,
            "\x1b[31mIt looks like SQIsign was compiled with assertions enabled.\n"
            "This will severely impact performance measurements.\x1b[0m\n");
#endif

    for (int i = 1; i < argc; i++) {
        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (sscanf(argv[i], "--iterations=%d", &iterations) == 1) {
            continue;
        }
    }

    if (help || iterations <= 0) {
        printf("Usage: %s [--iterations=<iterations>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for benchmarking; if not "
               "present, uses the default: %d)\n",
               iterations);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is "
               "generated\n");
        return 1;
    }

    if (!seed_set) {
        randombytes_select((unsigned char *)seed, sizeof(seed));
    }

    print_seed(seed);
    fflush(stdout);

#if defined(TARGET_BIG_ENDIAN)
    for (int i = 0; i < 12; i++) {
        seed[i] = BSWAP32(seed[i]);
    }
#endif

    if (init_test_rng(seed) != 0) {
        return 1;
    }
    cpucycles_init();

    return !mp_run(iterations);
}
