#ifndef MP_TEST_UTILS_H
#define MP_TEST_UTILS_H

// Shared fixtures and random-generation helpers for the mp test and bench executables (test_mp.c, bench_mp.c),
// compiled into both targets -- the same pattern as src/gf/gfx/test/test_utils.{h,c} in the gf module.

#include <stdint.h>

#include <mp.h>

// Count number of words for given bitlength
#define WORDS(bitlen) (int)(((bitlen) + (8 * sizeof(digit_t) - 1)) / (8 * sizeof(digit_t)))

// Fixed test primes of increasing size; pXXX has XXX significant bits. p260 and p390 are congruent to 1 mod 4 (p520 is
// not), which matters for the sqrt tests and benchmarks.
extern const ibz_t p10;
extern const ibz_t p60;
extern const ibz_t p110;
extern const ibz_t p260;
extern const ibz_t p957;
#if BITS >= 384
extern const ibz_t p390;
extern const ibz_t p1469;
#endif
#if BITS >= 512
extern const ibz_t p520;
extern const ibz_t p1981;
#endif
#if BITS >= 704
extern const ibz_t p650;
extern const ibz_t p2493;
#endif

#if BITS < 384
#define NUM_TEST_PRIMES 5
#elif BITS < 512
#define NUM_TEST_PRIMES 7
#elif BITS < 704
#define NUM_TEST_PRIMES 9
#else
#define NUM_TEST_PRIMES 11
#endif
extern ibz_t test_primes[NUM_TEST_PRIMES];

uint32_t rand_u32_range(uint32_t bound);
uint64_t rand_u64(void);
int ibz_eq(const ibz_t *a, const ibz_t *b);
void ibz_set_u64(ibz_t *out, uint64_t v, int bits);
void rand_ibz_nonneg(ibz_t *out, int bits);
void rand_ibz_signed(ibz_t *out, int bits);
void rand_ibz_odd_positive(ibz_t *out, int bits);

// Computes (a*b) mod m via binary double-and-add, without ever forming the full a*b product. ibz_mul needs
// a->bitlen + b->bitlen - 1 bits of headroom and silently truncates past the container's capacity, so it corrupts
// results for test primes whose square doesn't fit; this stays bounded by ~2*m at every step instead.
void ibz_mulmod(ibz_t *res, const ibz_t *a, const ibz_t *b, const ibz_t *m);

#endif
