// Property-based tests for the ibz_t big-integer API declared in mp.h.
//
// Follows the style of src/ec/ref/lvlx/test/curve-arith-test.c: each test_* function checks algebraic identities over
// many random inputs rather than comparing against a separate reference implementation.
//
// Random ibz_t values are built directly out of the ibz_t API itself (ibz_rand_interval_minm_m, ibz_mul_2exp, ibz_add,
// ibz_neg, ...) -- analogous to how ec_random_test in the EC tests is built out of the lower-level field arithmetic it
// exercises. Native random integers (offsets, exponents, list indices) are drawn independently from the PRNG's default
// domain so that they never depend on ibz_get, which is one of the functions under test.

#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#include <prng.h>
#include <rng.h>
#include <bench_test_arguments.h>
#include "mp_test_utils.h"
#include <mp.h>

#define PASSED 0
#define FAILED 1

/******************************
Test functions
******************************/

int
test_ibz_set_copy_swap(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int32_t v = (int32_t)rand_u32_range((1 << 24) - 1) - ((1 << 23) - 1);
        ibz_t a = { 0 };
        ibz_set(&a, v, 24);
        if (ibz_cmp_int32(&a, v) != 0) {
            printf("Failed: ibz_set/ibz_cmp_int32 mismatch (v=%d)\n", v);
            return FAILED;
        }

        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB);
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen == 0)
            continue;
        rand_ibz_signed(&a, bitlen);
        ibz_t b = { 0 };
        ibz_copy(&b, &a);
        if (!ibz_eq(&a, &b)) {
            printf("Failed: ibz_copy(target, value) != value\n");
            return FAILED;
        }

        a.limbs[0] ^= 1; // flip a bit in a
        if (ibz_eq(&a, &b)) {
            printf("Failed: ibz_copy aliases its source\n");
            return FAILED;
        }

        ibz_t pre_a = { 0 }, pre_b = { 0 };
        ibz_copy(&pre_a, &a);
        ibz_copy(&pre_b, &b);
        ibz_swap(&a, &b);
        if (!ibz_eq(&a, &pre_b) || !ibz_eq(&b, &pre_a)) {
            printf("Failed: ibz_swap did not exchange its arguments\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_set_bound(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        ibz_t a = { 0 }, orig = { 0 };
        int maxbitlen = IBZ_NLIMBS * NUM_BITS_LIMB - 10;
        int bitlen = (i * maxbitlen) / Ntest;
        rand_ibz_signed(&a, bitlen);
        ibz_copy(&orig, &a);

        // Growing the bound must preserve the value
        ibz_set_bound(&a, bitlen + 10);
        if (!ibz_eq(&a, &orig)) {
            printf("Failed: ibz_set_bound(a, 64) changed the value\n");
            return FAILED;
        }
        // Shrinking back to a bound the value still fits
        ibz_set_bound(&a, bitlen);
        if (!ibz_eq(&a, &orig)) {
            printf("Failed: ibz_set_bound(a, 48) changed the value\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_get(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = IBZ_NLIMBS * NUM_BITS_LIMB - 32;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen == 0)
            continue;
        int32_t v = (int32_t)rand_u32_range((1 << 20) - 1) - ((1 << 19) - 1);
        ibz_t a = { 0 }, noise = { 0 };
        ibz_set(&a, v, 20);
        int32_t got = ibz_get(&a);
        if (got != v) {
            printf("Failed: ibz_get(ibz_set(v)) != v (v=%d, got=%d)\n", v, got);
            return FAILED;
        }
        rand_ibz_nonneg(&noise, 10);
        ibz_mul_2exp(&noise, &noise, 33);
        ibz_add(&a, &a, &noise);
        got = ibz_get(&a);
        if (got != v) {
            printf("Failed: ibz_get(ibz_set(v)) != v mod 2**32 (v=%d, got=%d)\n", v, got);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_str_roundtrip(unsigned int Ntest)
{
    char buf[256];
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = 512;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t a = { 0 }, back = { 0 };
        rand_ibz_signed(&a, bitlen);

        ibz_convert_to_str(&a, buf, 10);
        ibz_set_from_str(&back, buf, 10);
        if (!ibz_eq(&a, &back)) {
            printf("Failed: base-10 string roundtrip mismatch (\"%s\")\n", buf);
            return FAILED;
        }

        ibz_convert_to_str(&a, buf, 16);
        ibz_set_from_str(&back, buf, 16);
        if (!ibz_eq(&a, &back)) {
            printf("Failed: base-16 string roundtrip mismatch (\"%s\")\n", buf);
            return FAILED;
        }

        // base-16 digit count of |a| must match ibz_size_in_base
        if (!ibz_is_zero(&a)) {
            ibz_t absa = { 0 };
            ibz_abs(&absa, &a);
            ibz_convert_to_str(&absa, buf, 16);
            if (ibz_size_in_base(&a, 16) != (int)strlen(buf)) {
                printf("Failed: ibz_size_in_base(a, 16) != strlen of base-16 string (\"%s\")\n", buf);
                return FAILED;
            }
        }
    }

    ibz_t bad = { 0 };
    if (ibz_set_from_str(&bad, "xyz", 10) != 0) {
        printf("Failed: ibz_set_from_str accepted an invalid string\n");
        return FAILED;
    }

    if (ibz_print(&bad, 7) != 0) {
        printf("Failed: ibz_print accepted unsupported base 7\n");
        return FAILED;
    }
    printf("\r");
    ibz_t v255 = { 0 };
    ibz_set(&v255, 255, 9);
    printf("ibz_print sanity check, expect 255/ff: ");
    if (!ibz_print(&v255, 10)) {
        printf("\nFailed: ibz_print(10) reported failure\n");
        return FAILED;
    }
    printf("/");
    if (!ibz_print(&v255, 16)) {
        printf("\nFailed: ibz_print(16) reported failure\n");
        return FAILED;
    }
    printf("\n");
    return PASSED;
}

int
test_ibz_add_sub(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        ibz_t a = { 0 }, b = { 0 }, c = { 0 };
        int maxbitlen = IBZ_NLIMBS * NUM_BITS_LIMB - 2;
        int bitlen = (i * maxbitlen) / Ntest;
        rand_ibz_signed(&a, bitlen);
        rand_ibz_signed(&b, bitlen);
        rand_ibz_signed(&c, bitlen);

        ibz_t ab = { 0 }, ba = { 0 };
        ibz_add(&ab, &a, &b);
        ibz_add(&ba, &b, &a);
        if (!ibz_eq(&ab, &ba)) {
            printf("Failed: a + b != b + a\n");
            return FAILED;
        }

        ibz_t abc1 = { 0 }, bc = { 0 }, abc2 = { 0 };
        ibz_add(&abc1, &ab, &c);
        ibz_add(&bc, &b, &c);
        ibz_add(&abc2, &a, &bc);
        if (!ibz_eq(&abc1, &abc2)) {
            printf("Failed: (a + b) + c != a + (b + c)\n");
            return FAILED;
        }

        ibz_t back = { 0 };
        ibz_sub(&back, &ab, &b);
        if (!ibz_eq(&back, &a)) {
            printf("Failed: (a + b) - b != a\n");
            return FAILED;
        }

        ibz_t neg_a = { 0 }, zero_res = { 0 };
        ibz_neg(&neg_a, &a);
        ibz_add(&zero_res, &a, &neg_a);
        if (!ibz_is_zero(&zero_res)) {
            printf("Failed: a + (-a) != 0\n");
            return FAILED;
        }

        ibz_t cneg_a = { 0 };
        ibz_cneg(&cneg_a, &a, (digit_t)(-1));
        if (!ibz_eq(&cneg_a, &neg_a)) {
            printf("Failed: cneg(a,true) != -a\n");
            return FAILED;
        }
        ibz_cneg(&cneg_a, &a, (digit_t)(0));
        if (!ibz_eq(&cneg_a, &a)) {
            printf("Failed: cneg(a,false) != a\n");
            return FAILED;
        }

        ibz_t self_sub = { 0 };
        ibz_sub(&self_sub, &a, &a);
        if (!ibz_is_zero(&self_sub)) {
            printf("Failed: a - a != 0\n");
            return FAILED;
        }

        ibz_t plus_zero = { 0 };
        ibz_add(&plus_zero, &a, &ibz_const_zero);
        if (!ibz_eq(&plus_zero, &a)) {
            printf("Failed: a + 0 != a\n");
            return FAILED;
        }

        ibz_t overflow_a = { 0 }, overflow_b = { 0 }, ab1 = { 0 }, ab2 = { 0 };
        ibz_copy(&overflow_a, &a);
        ibz_set_bound(&overflow_a, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_copy(&overflow_b, &b);
        ibz_set_bound(&overflow_b, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_add(&ab1, &overflow_a, &b);
        if (ab1.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a + b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab1, &ab) != 0) {
            printf("Failed: a + b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        ibz_add(&ab2, &overflow_a, &overflow_b);
        if (ab2.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a + b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab2, &ab) != 0) {
            printf("Failed: a + b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
        ibz_sub(&ab, &a, &b);
        ibz_sub(&ab1, &overflow_a, &b);
        if (ab1.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a - b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab1, &ab) != 0) {
            printf("Failed: a - b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        ibz_sub(&ab2, &overflow_a, &overflow_b);
        if (ab2.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a - b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab2, &ab) != 0) {
            printf("Failed: a - b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a+b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_mul(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 3;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t a = { 0 }, b = { 0 }, c = { 0 };
        rand_ibz_signed(&a, bitlen);
        rand_ibz_signed(&b, bitlen);
        rand_ibz_signed(&c, bitlen);

        ibz_t ab = { 0 }, ba = { 0 };
        ibz_mul(&ab, &a, &b);
        ibz_mul(&ba, &b, &a);
        if (!ibz_eq(&ab, &ba)) {
            printf("Failed: a * b != b * a\n");
            return FAILED;
        }

        ibz_t abc1 = { 0 }, bc = { 0 }, abc2 = { 0 };
        ibz_mul(&abc1, &ab, &c);
        ibz_mul(&bc, &b, &c);
        ibz_mul(&abc2, &a, &bc);
        if (!ibz_eq(&abc1, &abc2)) {
            printf("Failed: (a * b) * c != a * (b * c)\n");
            return FAILED;
        }

        ibz_t bpc = { 0 }, dist1 = { 0 }, ac = { 0 }, dist2 = { 0 };
        ibz_add(&bpc, &b, &c);
        ibz_mul(&dist1, &a, &bpc);
        ibz_mul(&ac, &a, &c);
        ibz_add(&dist2, &ab, &ac);
        if (!ibz_eq(&dist1, &dist2)) {
            printf("Failed: a * (b + c) != a * b + a * c\n");
            return FAILED;
        }

        ibz_t a1 = { 0 };
        ibz_mul(&a1, &a, &ibz_const_one);
        if (!ibz_eq(&a1, &a)) {
            printf("Failed: a * 1 != a\n");
            return FAILED;
        }

        ibz_t a0 = { 0 };
        ibz_mul(&a0, &a, &ibz_const_zero);
        if (!ibz_is_zero(&a0)) {
            printf("Failed: a * 0 != 0\n");
            return FAILED;
        }

        ibz_t negone = { 0 }, an = { 0 }, nega = { 0 };
        ibz_set(&negone, -1, 2);
        ibz_mul(&an, &a, &negone);
        ibz_neg(&nega, &a);
        if (!ibz_eq(&an, &nega)) {
            printf("Failed: a * (-1) != -a\n");
            return FAILED;
        }

        ibz_t overflow_a = { 0 }, overflow_b = { 0 }, ab1 = { 0 }, ab2 = { 0 };
        ibz_copy(&overflow_a, &a);
        ibz_set_bound(&overflow_a, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_copy(&overflow_b, &b);
        ibz_set_bound(&overflow_b, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_mul(&ab1, &overflow_a, &b);
        if (ab1.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a*b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a*b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab1, &ab) != 0) {
            printf("Failed: a*b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a*b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   b.bitlen,
                   ab1.bitlen);
            return FAILED;
        }
        ibz_mul(&ab2, &overflow_a, &overflow_b);
        if (ab2.bitlen > IBZ_NLIMBS * NUM_BITS_LIMB) {
            printf("Failed: a*b does not cap the result bitlen (a.bitlen=%d, b.bitlen=%d, (a*b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
        if (ibz_cmp(&ab2, &ab) != 0) {
            printf("Failed: a*b is computed incorrectly when bounds overflow (a.bitlen=%d, b.bitlen=%d, "
                   "(a*b).bitlen=%d)\n",
                   overflow_a.bitlen,
                   overflow_b.bitlen,
                   ab2.bitlen);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_div_mod(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 2 - 1;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen == 0)
            continue;
        ibz_t a = { 0 }, b = { 0 };
        rand_ibz_signed(&a, bitlen);
        while (1) {
            rand_ibz_signed(&b, bitlen);
            if (!ibz_is_zero(&b))
                break;
        }

        ibz_t q = { 0 }, r = { 0 }, recon = { 0 };
        ibz_div(&q, &r, &a, &b);
        ibz_mul(&recon, &q, &b);
        ibz_add(&recon, &recon, &r);
        if (!ibz_eq(&recon, &a)) {
            printf("Failed: ibz_div: quotient * b + remainder != a\n");
            return FAILED;
        }

        ibz_t absr = { 0 }, absb = { 0 };
        ibz_abs(&absr, &r);
        ibz_abs(&absb, &b);
        if (ibz_cmp(&absr, &absb) >= 0) {
            printf("Failed: ibz_div: |remainder| >= |b|\n");
            return FAILED;
        }

        ibz_mod(&r, &a, &b);
        if (!ibz_is_positive(&r) || ibz_cmp(&r, &absb) >= 0) {
            printf("Failed: ibz_mod result not in [0, |b|)\n");
            return FAILED;
        }

        ibz_t diff = { 0 };
        ibz_sub(&diff, &a, &r);
        if (!ibz_divides(&diff, &b)) {
            printf("Failed: b does not divide (a - (a mod b))\n");
            return FAILED;
        }

        unsigned long int dd = 3 + (unsigned long int)rand_u32_range(1000);
        unsigned long int rr = ibz_mod_ui(&a, dd);
        if (rr >= dd) {
            printf("Failed: ibz_mod_ui result >= divisor\n");
            return FAILED;
        }

        ibz_t dz = { 0 }, rz = { 0 };
        ibz_set(&dz, (int32_t)dd, 11);
        ibz_set(&rz, (int32_t)rr, 11);
        ibz_sub(&diff, &a, &rz);
        if (!ibz_divides(&diff, &dz)) {
            printf("Failed: d does not divide (a - ibz_mod_ui(a, d))\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_divides(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 2 - 1;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen < 3)
            continue;
        ibz_t a = { 0 }, b = { 0 }, ab = { 0 };
        while (1) {
            rand_ibz_signed(&a, bitlen);
            ibz_abs(&b, &a);
            if (ibz_cmp(&b, &ibz_const_one) > 0)
                break;
        }
        rand_ibz_signed(&b, bitlen);
        ibz_mul(&ab, &a, &b);

        if (!ibz_divides(&ab, &a)) {
            printf("Failed: a does not divide a * b\n");
            return FAILED;
        }

        ibz_t abp1 = { 0 };
        ibz_add(&abp1, &ab, &ibz_const_one);
        if (ibz_divides(&abp1, &a)) {
            printf("Failed: a divides a * b + 1 with |a| > 1\n");
            return FAILED;
        }

        if (!ibz_divides(&ibz_const_zero, &a)) {
            printf("Failed: a does not divide 0\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_shifts_two_adic(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) - 130;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen < 2)
            continue;
        ibz_t a = { 0 }, overflow_a = { 0 };
        rand_ibz_nonneg(&a, bitlen);
        ibz_copy(&overflow_a, &a);
        ibz_set_bound(&overflow_a, IBZ_NLIMBS * NUM_BITS_LIMB);
        uint32_t e = rand_u32_range(128);

        ibz_t shifted = { 0 }, back = { 0 };
        ibz_mul_2exp(&shifted, &a, e);
        ibz_div_2exp(&back, &shifted, e);
        if (!ibz_eq(&back, &a)) {
            printf("Failed: (a << e) >> e != a (e=%u, a.bitlen=%d)\n", e, bitlen);
            return FAILED;
        }
        ibz_mul_2exp(&back, &overflow_a, e);
        if (!ibz_eq(&back, &shifted)) {
            printf("Failed: a << e computed incorrectly when bound overflows (e=%u, a.bitlen=%d)\n", e, bitlen);
            return FAILED;
        }
        ibz_div_2exp(&back, &back, e);
        if (!ibz_eq(&back, &a)) {
            printf("Failed: (a << e) >> e != a when bound overflows (e=%u, a.bitlen=%d)\n", e, bitlen);
            return FAILED;
        }

        ibz_t hi = { 0 }, hi_shifted = { 0 }, recon = { 0 }, m2e = { 0 };
        ibz_div_2exp(&hi, &a, e);
        ibz_mul_2exp(&hi_shifted, &hi, e);
        ibz_sub(&recon, &a, &hi_shifted);
        ibz_mod2exp(&m2e, &a, e);
        if (!ibz_eq(&recon, &m2e)) {
            printf("Failed: ibz_mod2exp inconsistent with div_2exp/mul_2exp reconstruction (e=%u)\n", e);
            return FAILED;
        }

        a.limbs[0] |= 1; // Make a odd
        ibz_mul_2exp(&a, &a, e);

        int got = ibz_two_adic(&a);
        if (got != (int)e) {
            printf("Failed: ibz_two_adic(odd * 2^%u) != %u (got %d)\n", e, e, got);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_pow(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 32;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t x = { 0 };
        rand_ibz_nonneg(&x, bitlen);
        if (ibz_is_zero(&x))
            continue;
        uint32_t e1 = rand_u32_range(16);
        uint32_t e2 = rand_u32_range(16);

        ibz_t xe1 = { 0 }, xe2 = { 0 }, prod = { 0 }, xsum = { 0 };
        ibz_pow(&xe1, &x, e1, 4);
        ibz_pow(&xe2, &x, e2, 4);
        ibz_mul(&prod, &xe1, &xe2);
        ibz_pow(&xsum, &x, e1 + e2, 5);
        if (!ibz_eq(&xsum, &prod)) {
            printf("Failed: x^(e1+e2) != x^e1 * x^e2 (e1=%u, e2=%u)\n", e1, e2);
            return FAILED;
        }

        ibz_t overflow_x = { 0 };
        ibz_copy(&overflow_x, &x);
        ibz_set_bound(&overflow_x, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_pow(&prod, &overflow_x, e1 + e2, 5);
        if (!ibz_eq(&xsum, &prod)) {
            printf("Failed: x^e computed incorrectly when bound overflows.\n");
            return FAILED;
        }

        ibz_t x0 = { 0 };
        ibz_pow(&x0, &x, 0, 5);
        if (!ibz_is_one(&x0)) {
            printf("Failed: x^0 != 1\n");
            return FAILED;
        }

        ibz_t x1 = { 0 };
        ibz_pow(&x1, &x, 1, 5);
        if (!ibz_eq(&x1, &x)) {
            printf("Failed: x^1 != x\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_pow_mod(unsigned int Ntest)
{
    for (size_t mi = 0; mi < NUM_TEST_PRIMES; mi++) {
        ibz_t m = test_primes[mi];
        for (unsigned int i = 0; i < Ntest; i++) {
            uint32_t e = rand_u32_range(31);
            ibz_t x = { 0 }, e_ibz = { 0 };
            rand_ibz_odd_positive(&x, m.bitlen - 1);
            ibz_mod(&x, &x, &m);
            ibz_set(&e_ibz, (int32_t)e, 6);

            ibz_t expected = { 0 };
            ibz_copy(&expected, &ibz_const_one);
            for (uint32_t j = 0; j < e; j++) {
                ibz_mulmod(&expected, &expected, &x, &m);
            }

            ibz_t actual = { 0 };
            ibz_pow_mod(&actual, &x, &e_ibz, &m);

            if (!ibz_eq(&actual, &expected)) {
                printf("Failed: ibz_pow_mod(x, e, m) != (x^e mod m) (e=%u, m_bits=%d)\n", e, m.bitlen - 1);
                return FAILED;
            }
        }
    }
    return PASSED;
}

int
test_ibz_cmp_predicates(unsigned int Ntest)
{
    ibz_t z = { 0 };
    ibz_copy(&z, &ibz_const_zero);
    if (!ibz_is_zero(&z) || ibz_is_one(&z)) {
        printf("Failed: is_zero/is_one disagree on ibz_const_zero\n");
        return FAILED;
    }

    ibz_t o = { 0 };
    ibz_copy(&o, &ibz_const_one);
    if (!ibz_is_one(&o) || ibz_is_zero(&o)) {
        printf("Failed: is_zero/is_one disagree on ibz_const_one\n");
        return FAILED;
    }

    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) - 1;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t a = { 0 }, b = { 0 };
        rand_ibz_signed(&a, bitlen);
        rand_ibz_signed(&b, bitlen);

        if (ibz_cmp(&a, &a) != 0) {
            printf("Failed: ibz_cmp(a, a) != 0\n");
            return FAILED;
        }

        int c1 = ibz_cmp(&a, &b);
        int c2 = ibz_cmp(&b, &a);
        if ((c1 > 0 && c2 >= 0) || (c1 < 0 && c2 <= 0) || (c1 == 0 && c2 != 0)) {
            printf("Failed: ibz_cmp is not antisymmetric\n");
            return FAILED;
        }

        ibz_t diff = { 0 };
        ibz_sub(&diff, &a, &b);
        if ((c1 >= 0) != (ibz_is_positive(&diff) != 0)) {
            printf("Failed: ibz_cmp(a, b) inconsistent with ibz_is_positive(a - b)\n");
            return FAILED;
        }

        if ((ibz_is_positive(&a) != 0) != (ibz_cmp_int32(&a, 0) >= 0)) {
            printf("Failed: ibz_is_positive inconsistent with ibz_cmp_int32(a, 0)\n");
            return FAILED;
        }

        ibz_t ap1 = { 0 };
        ibz_add(&ap1, &a, &ibz_const_one);
        if (ibz_is_even(&a) == ibz_is_even(&ap1)) {
            printf("Failed: parity of a and a+1 must differ\n");
            return FAILED;
        }
        if ((ibz_is_odd(&a) != 0) == (ibz_is_even(&a) != 0)) {
            printf("Failed: ibz_is_odd and ibz_is_even disagree\n");
            return FAILED;
        }
    }

    for (unsigned int i = 0; i < Ntest; i++) {
        int32_t v = (int32_t)rand_u32_range((1 << 20) - 1) - ((1 << 19) - 1);
        ibz_t a = { 0 };
        ibz_set(&a, v, 20);
        if (ibz_cmp_int32(&a, v) != 0 || ibz_cmp_int32(&a, v - 1) <= 0 || ibz_cmp_int32(&a, v + 1) >= 0) {
            printf("Failed: ibz_cmp_int32 ordering mismatch (v=%d)\n", v);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_rand_interval(unsigned int Ntest)
{
    ibz_t bound = { 0 };

    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) - 65;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen == 0)
            continue;
        ibz_mul_2exp(&bound, &ibz_const_one, bitlen - 1);

        ibz_t r = { 0 };
        if (!ibz_rand_interval(&r, &ibz_const_zero, &bound)) {
            printf("Failed: ibz_rand_interval reported failure\n");
            return FAILED;
        }
        if (ibz_cmp(&r, &ibz_const_zero) < 0 || ibz_cmp(&r, &bound) > 0) {
            printf("Failed: ibz_rand_interval result out of [0, bound]\n");
            return FAILED;
        }
        if (!ibz_is_zero(&r)) {
            ibz_t mr = { 0 }, rr = { 0 };
            ibz_neg(&mr, &r);
            if (!ibz_rand_interval(&rr, &mr, &r)) {
                printf("Failed: ibz_rand_interval (-r, r) reported failure\n");
                return FAILED;
            }
            ibz_abs(&rr, &rr);
            if (ibz_cmp(&rr, &r) > 0) {
                printf("Failed: |ibz_rand_interval(-r,r)| > r\n");
                return FAILED;
            }
        }
    }

    for (unsigned int i = 0; i < Ntest; i++) {
        int32_t m = 1 + (int32_t)rand_u32_range(1 << 20);
        ibz_t r = { 0 };
        if (!ibz_rand_interval_minm_m(&r, m)) {
            printf("Failed: ibz_rand_interval_minm_m reported failure\n");
            return FAILED;
        }
        if (ibz_cmp_int32(&r, -m) < 0 || ibz_cmp_int32(&r, m) > 0) {
            printf("Failed: ibz_rand_interval_minm_m result out of [-m, m]\n");
            return FAILED;
        }
    }

    const int32_t large_m[] = { (1 << 30) - 1, 1 << 30, INT32_MAX - 1, INT32_MAX };
    for (size_t i = 0; i < sizeof(large_m) / sizeof(large_m[0]); i++) {
        int32_t m = large_m[i];
        ibz_t r = { 0 };
        if (!ibz_rand_interval_minm_m(&r, m)) {
            printf("Failed: ibz_rand_interval_minm_m reported failure for m = %" PRId32 "\n", m);
            return FAILED;
        }
        if (ibz_cmp_int32(&r, -m) < 0 || ibz_cmp_int32(&r, m) > 0) {
            printf("Failed: ibz_rand_interval_minm_m result out of [-m, m] for m = %" PRId32 "\n", m);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_bitsize(unsigned int Ntest)
{
    ibz_t x = { 0 };
    ibz_copy(&x, &ibz_const_zero);
    if (ibz_bitsize(&x) != 0) {
        printf("Failed: ibz_bitsize(0) != 0 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_copy(&x, &ibz_const_one);
    if (ibz_bitsize(&x) != 1) {
        printf("Failed: ibz_bitsize(1) != 1 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_copy(&x, &ibz_const_two);
    if (ibz_bitsize(&x) != 2) {
        printf("Failed: ibz_bitsize(2) != 2 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_copy(&x, &ibz_const_three);
    if (ibz_bitsize(&x) != 2) {
        printf("Failed: ibz_bitsize(3) != 2 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_neg(&x, &ibz_const_one);
    if (ibz_bitsize(&x) != 1) {
        printf("Failed: ibz_bitsize(-1) != 1 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_neg(&x, &ibz_const_two);
    if (ibz_bitsize(&x) != 2) {
        printf("Failed: ibz_bitsize(-2) != 2 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_neg(&x, &ibz_const_three);
    if (ibz_bitsize(&x) != 2) {
        printf("Failed: ibz_bitsize(-3) != 2 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }

    ibz_mul_2exp(&x, &ibz_const_one, 64);
    if (ibz_bitsize(&x) != 65) {
        printf("Failed: ibz_bitsize(2^64) != 65 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }
    ibz_neg(&x, &x);
    if (ibz_bitsize(&x) != 65) {
        printf("Failed: ibz_bitsize(-2^64) != 65 (got %d)\n", ibz_bitsize(&x));
        return FAILED;
    }

    for (unsigned int i = 0; i < Ntest; i++) {
        int k = 1 + (int)rand_u32_range(256);

        ibz_t a = { 0 };
        ibz_mul_2exp(&a, &ibz_const_one, (uint32_t)(k - 1)); // a = 2^(k-1)
        if (ibz_bitsize(&a) != k) {
            printf("Failed: ibz_bitsize(2^%d) != %d (got %d)\n", k - 1, k, ibz_bitsize(&a));
            return FAILED;
        }

        ibz_neg(&a, &a);
        if (ibz_bitsize(&a) != k) {
            printf("Failed: ibz_bitsize(-2^%d) != %d (got %d)\n", k - 1, k, ibz_bitsize(&a));
            return FAILED;
        }

        ibz_t b = { 0 };
        ibz_mul_2exp(&b, &ibz_const_one, (uint32_t)k);
        ibz_sub(&b, &b, &ibz_const_one); // b = 2^k - 1
        if (ibz_bitsize(&b) != k) {
            printf("Failed: ibz_bitsize(2^%d - 1) != %d (got %d)\n", k, k, ibz_bitsize(&b));
            return FAILED;
        }

        ibz_neg(&b, &b);
        if (ibz_bitsize(&b) != k) {
            printf("Failed: ibz_bitsize(1 - 2^%d) != %d (got %d)\n", k, k, ibz_bitsize(&b));
            return FAILED;
        }

        if (ibz_size_in_base(&a, 2) != ibz_bitsize(&a)) {
            printf("Failed: ibz_size_in_base(a, 2) != ibz_bitsize(a)\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_bound_helpers(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        ibz_t a = { 0 };
        rand_ibz_signed(&a, 48);
        int32_t bv = (int32_t)rand_u32_range((1 << 16) - 1) - ((1 << 15) - 1);
        ibz_t bz = { 0 };
        ibz_set(&bz, bv, 16);

        ibz_t prod = { 0 }, expected_prod = { 0 };
        ibz_mul_by_int_and_set_bound(&prod, &a, bv, 128);
        ibz_mul(&expected_prod, &a, &bz);
        if (!ibz_eq(&prod, &expected_prod)) {
            printf("Failed: ibz_mul_by_int_and_set_bound(a, b) != a * b (b=%d)\n", bv);
            return FAILED;
        }

        ibz_t sum = { 0 }, expected_sum = { 0 };
        ibz_add_and_set_bound(&sum, &a, &bz, 128);
        ibz_add(&expected_sum, &a, &bz);
        if (!ibz_eq(&sum, &expected_sum)) {
            printf("Failed: ibz_add_and_set_bound(a, b) != a + b (b=%d)\n", bv);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_extract(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        // ibz_extract_u64 is hard-coded to a 64-bit window: it returns bits
        // [offset, offset+64) of |a|, regardless of the sign of a.
        int offset_u = (int)rand_u32_range(256);

        ibz_t low_u = { 0 }, window_u = { 0 }, high_u = { 0 }, a_u = { 0 };
        rand_ibz_nonneg(&low_u, offset_u + 1); // bits [0, offset_u)

        uint64_t window_u_val = rand_u64();       // bits [offset_u, offset_u+64), full range
        ibz_set_u64(&window_u, window_u_val, 65); // guard bit keeps the value non-negative

        rand_ibz_nonneg(&high_u, 21); // bits [offset_u+64, offset_u+84)

        ibz_mul_2exp(&window_u, &window_u, (uint32_t)offset_u);
        ibz_mul_2exp(&high_u, &high_u, (uint32_t)(offset_u + 64));
        ibz_add(&a_u, &low_u, &window_u);
        ibz_add(&a_u, &a_u, &high_u);

        uint64_t extracted_u = ibz_extract_u64(&a_u, offset_u);
        if (extracted_u != window_u_val) {
            printf("Failed: ibz_extract_u64 mismatch (expected %" PRIu64 ", got %" PRIu64 ")\n",
                   window_u_val,
                   extracted_u);
            return FAILED;
        }

        // Extraction reads |a|, so negating a must leave the result unchanged.
        ibz_neg(&a_u, &a_u);
        extracted_u = ibz_extract_u64(&a_u, offset_u);
        if (extracted_u != window_u_val) {
            printf("Failed: ibz_extract_u64 is not sign-independent (expected %" PRIu64 ", got %" PRIu64 ")\n",
                   window_u_val,
                   extracted_u);
            return FAILED;
        }

        // ibz_extract_i64 is hard-coded to a 63-bit magnitude window: it
        // returns bits [offset, offset+63) of |a|, signed by sign(a).
        int offset_i = (int)rand_u32_range(256);

        ibz_t low_i = { 0 }, window_i = { 0 }, high_i = { 0 }, a_i = { 0 };
        rand_ibz_nonneg(&low_i, offset_i + 1); // bits [0, offset_i)

        // Mask to 63 bits: bit 63 belongs to high_i, not to the window, and
        // must not leak into the extracted magnitude.
        uint64_t window_i_val = rand_u64() & (((uint64_t)1 << 63) - 1);
        ibz_set_u64(&window_i, window_i_val, 64); // guard bit keeps the value non-negative

        rand_ibz_nonneg(&high_i, 21); // bits [offset_i+63, offset_i+83)

        ibz_mul_2exp(&window_i, &window_i, (uint32_t)offset_i);
        ibz_mul_2exp(&high_i, &high_i, (uint32_t)(offset_i + 63));
        ibz_add(&a_i, &low_i, &window_i);
        ibz_add(&a_i, &a_i, &high_i);

        int64_t extracted_i = ibz_extract_i64(&a_i, offset_i);
        if (extracted_i != (int64_t)window_i_val) {
            printf("Failed: ibz_extract_i64 mismatch on positive input (expected %" PRId64 ", got %" PRId64 ")\n",
                   (int64_t)window_i_val,
                   extracted_i);
            return FAILED;
        }

        ibz_neg(&a_i, &a_i);
        extracted_i = ibz_extract_i64(&a_i, offset_i);
        if (extracted_i != -(int64_t)window_i_val) {
            printf("Failed: ibz_extract_i64 sign not propagated from a negative input (expected %" PRId64
                   ", got %" PRId64 ")\n",
                   -(int64_t)window_i_val,
                   extracted_i);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_gcd(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB);
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen < 2)
            continue;
        ibz_t a = { 0 }, b = { 0 }, g = { 0 };
        while (1) {
            rand_ibz_nonneg(&a, bitlen);
            if (!ibz_is_zero(&a))
                break;
        }
        while (1) {
            rand_ibz_nonneg(&b, bitlen);
            if (!ibz_is_zero(&b))
                break;
        }

        ibz_gcd(&g, &a, &b);
        if (!ibz_divides(&a, &g) || !ibz_divides(&b, &g)) {
            printf("Failed: ibz_gcd(a, b) does not divide both a and b\n");
            return FAILED;
        }

        ibz_gcd(&g, &a, &ibz_const_zero);
        if (!ibz_eq(&g, &a)) {
            printf("Failed: ibz_gcd(a, 0) != |a|\n");
            return FAILED;
        }
    }

    ibz_t g00 = { 0 };
    ibz_gcd(&g00, &ibz_const_zero, &ibz_const_zero);
    if (!ibz_is_zero(&g00)) {
        printf("Failed: ibz_gcd(0, 0) != 0\n");
        return FAILED;
    }
    return PASSED;
}

int
test_ibz_xgcd(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 2;
        int bitlen = (i * maxbitlen) / Ntest;
        if (bitlen < 2)
            continue;
        ibz_t a = { 0 }, b = { 0 };
        while (1) {
            rand_ibz_nonneg(&a, bitlen);
            if (!ibz_is_zero(&a))
                break;
        }
        while (1) {
            rand_ibz_nonneg(&b, bitlen);
            if (!ibz_is_zero(&b))
                break;
        }

        ibz_t g = { 0 }, u = { 0 }, v = { 0 };
        ibz_xgcd(&g, &u, &v, &a, &b);

        ibz_t g2 = { 0 };
        ibz_gcd(&g2, &a, &b);
        if (!ibz_eq(&g, &g2)) {
            printf("Failed: ibz_xgcd gcd differs from ibz_gcd\n");
            return FAILED;
        }

        ibz_t ua = { 0 }, vb = { 0 }, bezout = { 0 };
        ibz_mul(&ua, &u, &a);
        ibz_mul(&vb, &v, &b);
        ibz_add(&bezout, &ua, &vb);
        if (!ibz_eq(&bezout, &g)) {
            printf("Failed: u*a + v*b != ibz_xgcd(a, b)\n");
            return FAILED;
        }
    }

    // b = 0: gcd is |a| and the Bezout identity reduces to u*a = g
    ibz_t a = { 0 }, g = { 0 }, u = { 0 }, v = { 0 }, absa = { 0 }, ua = { 0 };
    rand_ibz_signed(&a, 48);
    ibz_xgcd(&g, &u, &v, &a, &ibz_const_zero);
    ibz_abs(&absa, &a);
    ibz_mul(&ua, &u, &a);
    if (!ibz_eq(&g, &absa) || !ibz_eq(&ua, &g)) {
        printf("Failed: ibz_xgcd(a, 0) != (|a|, sgn(a), 0)\n");
        return FAILED;
    }
    return PASSED;
}

int
test_ibz_crt(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 2;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t m1 = { 0 }, m2 = { 0 }, g = { 0 };
        rand_ibz_odd_positive(&m1, bitlen);
        rand_ibz_odd_positive(&m2, bitlen);
        ibz_gcd(&g, &m1, &m2);
        if (!ibz_is_one(&g)) {
            continue; // ibz_crt requires coprime moduli
        }

        ibz_t a1 = { 0 }, a2 = { 0 };
        rand_ibz_signed(&a1, bitlen);
        rand_ibz_signed(&a2, bitlen);

        ibz_t x = { 0 };
        ibz_crt(&x, &a1, &a2, &m1, &m2);

        ibz_t mod = { 0 };
        ibz_mul(&mod, &m1, &m2);
        if (!ibz_is_positive(&x) || ibz_cmp(&x, &mod) >= 0) {
            printf("Failed: ibz_crt result not in [0, m1*m2)\n");
            return FAILED;
        }

        ibz_t xm = { 0 }, am = { 0 };
        ibz_mod(&xm, &x, &m1);
        ibz_mod(&am, &a1, &m1);
        if (!ibz_eq(&xm, &am)) {
            printf("Failed: ibz_crt result != a1 (mod m1)\n");
            return FAILED;
        }
        ibz_mod(&xm, &x, &m2);
        ibz_mod(&am, &a2, &m2);
        if (!ibz_eq(&xm, &am)) {
            printf("Failed: ibz_crt result != a2 (mod m2)\n");
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_legendre(unsigned int Ntest)
{
    for (size_t pi = 0; pi < NUM_TEST_PRIMES; pi++) {
        ibz_t pz = test_primes[pi];

        if (ibz_legendre(&ibz_const_zero, &pz) != 0) {
            printf("Failed: ibz_legendre(0, p) != 0 (pbits=%d)\n", pz.bitlen - 1);
            return FAILED;
        }

        for (unsigned int i = 0; i < Ntest; i++) {
            ibz_t a = { 0 }, b = { 0 }, ab = { 0 };
            rand_ibz_nonneg(&a, pz.bitlen - 2);
            rand_ibz_nonneg(&b, pz.bitlen - 2);
            ibz_mulmod(&ab, &a, &b, &pz);

            int la = ibz_legendre(&a, &pz);
            int lb = ibz_legendre(&b, &pz);
            int lab = ibz_legendre(&ab, &pz);
            if (la * lb != lab) {
                printf("Failed: Legendre symbol not multiplicative (pbits=%d)\n", pz.bitlen - 1);
                return FAILED;
            }

            ibz_t sq = { 0 };
            ibz_mulmod(&sq, &a, &a, &pz);
            if ((ibz_legendre(&sq, &pz) != 1) && (!ibz_is_zero(&a))) {
                printf("Failed: ibz_legendre(a^2, p) != 1 (pbits=%d)\n", pz.bitlen - 1);
                return FAILED;
            }
        }
    }
    return PASSED;
}

int
test_ibz_invmod(unsigned int Ntest)
{
    for (size_t pi = 0; pi < NUM_TEST_PRIMES; pi++) {
        ibz_t m = test_primes[pi];
        for (unsigned int i = 0; i < Ntest; i++) {
            ibz_t a = { 0 };
            rand_ibz_nonneg(&a, m.bitlen - 2);
            if (ibz_is_zero(&a))
                continue;

            ibz_t inv = { 0 };
            if (!ibz_invmod(&inv, &a, &m)) {
                printf("Failed: ibz_invmod failed for pbits=%d\n", m.bitlen - 1);
                return FAILED;
            }

            ibz_t r = { 0 };
            ibz_mulmod(&r, &a, &inv, &m);
            if (!ibz_is_one(&r)) {
                printf("Failed: a * ibz_invmod(a, p) != 1 (mod p) (pbits=%d)\n", m.bitlen - 1);
                return FAILED;
            }
        }
        ibz_t inv = { 0 };
        if (ibz_invmod(&inv, &m, &m)) {
            printf("Failed: ibz_invmod(p,p) does not report failure (pbits=%d)\n", m.bitlen - 1);
            return FAILED;
        }
    }
    return PASSED;
}

// Checks that ibz_invmat produces a genuine 2x2 inverse modulo 2^e, by multiplying the original matrix by the
// (in-place) result and checking that the product is the identity modulo 2^e.
int
test_ibz_invmat(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 4;
        int e = (i * maxbitlen) / Ntest;
        if (e < 1)
            continue;

        ibz_t r1 = { 0 }, r2 = { 0 }, s1 = { 0 }, s2 = { 0 };
        ibz_set(&r1, 1, 2);
        ibz_set(&s2, 1, 2);
        rand_ibz_nonneg(&s1, e - 1);
        rand_ibz_nonneg(&r2, e - 1);
        // r2 even guarantees det = r1*s2 - r2*s1 = 1 - r2*s1 is odd, hence
        // invertible modulo 2^e for any e, without needing to search for one.
        r2.limbs[0] &= ((digit_t)-1) << 1;

        ibz_t or1 = { 0 }, or2 = { 0 }, os1 = { 0 }, os2 = { 0 };
        ibz_copy(&or1, &r1);
        ibz_copy(&or2, &r2);
        ibz_copy(&os1, &s1);
        ibz_copy(&os2, &s2);

        ibz_invmat(&r1, &r2, &s1, &s2, e);

        ibz_t c11 = { 0 }, c12 = { 0 }, c21 = { 0 }, c22 = { 0 }, t1 = { 0 }, t2 = { 0 };
        ibz_mul(&t1, &or1, &r1);
        ibz_mul(&t2, &or2, &s1);
        ibz_add(&c11, &t1, &t2);
        ibz_mul(&t1, &or1, &r2);
        ibz_mul(&t2, &or2, &s2);
        ibz_add(&c12, &t1, &t2);
        ibz_mul(&t1, &os1, &r1);
        ibz_mul(&t2, &os2, &s1);
        ibz_add(&c21, &t1, &t2);
        ibz_mul(&t1, &os1, &r2);
        ibz_mul(&t2, &os2, &s2);
        ibz_add(&c22, &t1, &t2);

        ibz_mod2exp(&c11, &c11, (uint32_t)e);
        ibz_mod2exp(&c12, &c12, (uint32_t)e);
        ibz_mod2exp(&c21, &c21, (uint32_t)e);
        ibz_mod2exp(&c22, &c22, (uint32_t)e);

        if (!ibz_is_one(&c11) || !ibz_is_zero(&c12) || !ibz_is_zero(&c21) || !ibz_is_one(&c22)) {
            printf("Failed: matrix * ibz_invmat(matrix) != identity (mod 2^%d)\n", e);
            return FAILED;
        }

        ibz_set_bound(&or1, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_set_bound(&or2, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_set_bound(&os1, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_set_bound(&os2, IBZ_NLIMBS * NUM_BITS_LIMB);
        ibz_invmat(&or1, &or2, &os1, &os2, e);
        if ((ibz_cmp(&r1, &or1) != 0) || (ibz_cmp(&r2, &or2) != 0) || (ibz_cmp(&s1, &os1) != 0) ||
            (ibz_cmp(&s2, &os2) != 0)) {
            printf("Failed: ibz_invmat(matrix) computed incorrectly when bounds overflow\n");
            return FAILED;
        }

        if ((r1.bitlen != e + 1) || (r2.bitlen != e + 1) || (s1.bitlen != e + 1) || (s2.bitlen != e + 1) ||
            (or1.bitlen != e + 1) || (or2.bitlen != e + 1) || (os1.bitlen != e + 1) || (os2.bitlen != e + 1)) {
            printf("Failed: ibz_invmat is not setting output bounds to e+1\n");
            return FAILED;
        }
    }
    return PASSED;
}

// Verifies that s = ibz_sqrt_floor(a) is the floor of the root, in remainder form: 0 <= a - s^2 <= 2s pins s down
// exactly without ever forming (s+1)^2, which needs one bit more than an ibz_t can hold once a fills the container.
// Also re-runs the call with the output aliasing the input, since that is a supported (and used) call pattern.
static int
check_sqrt_floor(const ibz_t *a, const char *what)
{
    ibz_t s = { 0 }, sq = { 0 }, r = { 0 }, aliased = { 0 };

    ibz_sqrt_floor(&s, a);
    ibz_mul(&sq, &s, &s);
    ibz_sub(&r, a, &sq);
    if (ibz_cmp(&r, &ibz_const_zero) < 0) {
        printf("Failed: ibz_sqrt_floor(%s)^2 > a\n", what);
        return FAILED;
    }
    ibz_sub(&r, &r, &s);
    ibz_sub(&r, &r, &s);
    if (ibz_cmp(&r, &ibz_const_zero) > 0) {
        printf("Failed: a - ibz_sqrt_floor(%s)^2 > 2*ibz_sqrt_floor(%s)\n", what, what);
        return FAILED;
    }

    ibz_copy(&aliased, a);
    ibz_sqrt_floor(&aliased, &aliased);
    if (!ibz_eq(&aliased, &s)) {
        printf("Failed: ibz_sqrt_floor(%s) differs when the output aliases the input\n", what);
        return FAILED;
    }
    return PASSED;
}

int
test_ibz_sqrt_floor(unsigned int Ntest)
{
    for (unsigned int i = 0; i < Ntest; i++) {
        int maxbitlen = (IBZ_NLIMBS * NUM_BITS_LIMB) / 2 - 1;
        int bitlen = (i * maxbitlen) / Ntest;
        ibz_t a = { 0 };
        rand_ibz_nonneg(&a, bitlen);

        ibz_t s = { 0 };
        ibz_sqrt_floor(&s, &a);

        ibz_t s2 = { 0 };
        ibz_mul(&s2, &s, &s);
        if (ibz_cmp(&s2, &a) > 0) {
            printf("Failed: ibz_sqrt_floor(a)^2 > a\n");
            return FAILED;
        }

        ibz_t sp1 = { 0 }, sp1sq = { 0 };
        ibz_add(&sp1, &s, &ibz_const_one);
        ibz_mul(&sp1sq, &sp1, &sp1);
        if (ibz_cmp(&sp1sq, &a) <= 0) {
            printf("Failed: (ibz_sqrt_floor(a) + 1)^2 <= a\n");
            return FAILED;
        }

        // The bitlen field is only a bound on the value's size: re-test the same value under the loosest bound the
        // function accepts, which used to derail the Newton iteration's starting point (deterministic regression case
        // for what rand_ibz_nonneg above only produces with geometrically small probability).
        ibz_set_bound(&a, maxbitlen);
        ibz_sqrt_floor(&s, &a);
        ibz_mul(&s2, &s, &s);
        if (ibz_cmp(&s2, &a) > 0) {
            printf("Failed: ibz_sqrt_floor(a)^2 > a (loose bitlen bound)\n");
            return FAILED;
        }
        ibz_add(&sp1, &s, &ibz_const_one);
        ibz_mul(&sp1sq, &sp1, &sp1);
        if (ibz_cmp(&sp1sq, &a) <= 0) {
            printf("Failed: (ibz_sqrt_floor(a) + 1)^2 <= a (loose bitlen bound)\n");
            return FAILED;
        }
    }

    const int capacity = IBZ_NLIMBS * NUM_BITS_LIMB;

    // Small values against a table, each also under the loosest bound the function accepts, which sends the trimming
    // step across a whole container of zero limbs before it reaches the single-limb path.
    {
        static const int expected[18] = { 0, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4 };
        for (int v = 0; v < 18; v++) {
            ibz_t a = { 0 }, s = { 0 }, e = { 0 };
            ibz_set(&a, v, 32);
            ibz_set(&e, expected[v], 32);
            ibz_sqrt_floor(&s, &a);
            if (!ibz_eq(&s, &e)) {
                printf("Failed: ibz_sqrt_floor(%d) is wrong\n", v);
                return FAILED;
            }
            ibz_set_bound(&a, capacity);
            ibz_sqrt_floor(&s, &a);
            if (!ibz_eq(&s, &e)) {
                printf("Failed: ibz_sqrt_floor(%d) is wrong under a loose bound\n", v);
                return FAILED;
            }
        }
    }

    // Powers of two and their two neighbors at every bit position. This sweeps the single-limb dispatch boundary at
    // NUM_BITS_LIMB, both parities of the normalization shift (hence both limb offsets), and, as 2^k - 1, the all-ones
    // value of every length.
    for (int k = 1; k <= capacity - 3; k++) {
        ibz_t p = { 0 }, q = { 0 };
        ibz_set(&p, 1, 2);
        ibz_mul_2exp(&p, &p, (uint32_t)k);
        if (check_sqrt_floor(&p, "2^k") == FAILED)
            return FAILED;
        ibz_sub(&q, &p, &ibz_const_one);
        if (check_sqrt_floor(&q, "2^k - 1") == FAILED)
            return FAILED;
        ibz_add(&q, &p, &ibz_const_one);
        if (check_sqrt_floor(&q, "2^k + 1") == FAILED)
            return FAILED;
    }

    // Perfect squares and their neighbors, where the root is known in advance rather than only bracketed: the sharpest
    // check for an off-by-one in the final correction.
    for (unsigned int i = 0; i < Ntest; i++) {
        ibz_t x = { 0 }, xm1 = { 0 }, sq = { 0 }, v = { 0 }, s = { 0 };
        int bits = 2 + (int)((i * (unsigned int)(capacity / 2 - 2)) / Ntest);
        rand_ibz_nonneg(&x, bits);
        if (ibz_is_zero(&x))
            ibz_copy(&x, &ibz_const_one); // x^2 - 1 below must not go negative
        ibz_sub(&xm1, &x, &ibz_const_one);
        ibz_mul(&sq, &x, &x);

        ibz_sqrt_floor(&s, &sq);
        if (!ibz_eq(&s, &x)) {
            printf("Failed: ibz_sqrt_floor(x^2) != x\n");
            return FAILED;
        }
        ibz_sub(&v, &sq, &ibz_const_one);
        ibz_sqrt_floor(&s, &v);
        if (!ibz_eq(&s, &xm1)) {
            printf("Failed: ibz_sqrt_floor(x^2 - 1) != x - 1\n");
            return FAILED;
        }
        ibz_add(&v, &sq, &ibz_const_one);
        ibz_sqrt_floor(&s, &v);
        if (!ibz_eq(&s, &x)) {
            printf("Failed: ibz_sqrt_floor(x^2 + 1) != x\n");
            return FAILED;
        }
        ibz_add(&v, &sq, &x);
        ibz_sqrt_floor(&s, &v);
        if (!ibz_eq(&s, &x)) {
            printf("Failed: ibz_sqrt_floor(x^2 + x) != x\n");
            return FAILED;
        }
    }

    // Random values across the whole width an ibz_t can hold
    for (unsigned int i = 0; i < Ntest; i++) {
        ibz_t a = { 0 };
        int bitlen = 2 + (int)((i * (unsigned int)(capacity - 2)) / Ntest);
        rand_ibz_nonneg(&a, bitlen);
        if (check_sqrt_floor(&a, "random, full width") == FAILED)
            return FAILED;
        ibz_set_bound(&a, capacity);
        if (check_sqrt_floor(&a, "random, full width under a loose bound") == FAILED)
            return FAILED;
    }
    return PASSED;
}

int
test_ibz_sqrt_mod_p(unsigned int Ntest)
{
    for (size_t pi = 0; pi < NUM_TEST_PRIMES; pi++) {
        ibz_t q = test_primes[pi];
        for (unsigned int i = 0; i < Ntest; i++) {
            ibz_t a = { 0 };
            rand_ibz_nonneg(&a, q.bitlen - 2);

            ibz_t sqmod = { 0 };
            ibz_mulmod(&sqmod, &a, &a, &q);

            ibz_t r = { 0 }, r2 = { 0 };
            if (!ibz_sqrt_mod_p(&r, &sqmod, &q)) {
                printf("Failed: ibz_sqrt_mod_p returned false for a known square (pbits=%d)\n", q.bitlen - 1);
                return FAILED;
            }
            ibz_mulmod(&r2, &r, &r, &q);
            if (!ibz_eq(&r2, &sqmod)) {
                printf("Failed: ibz_sqrt_mod_p(a^2 mod p, p)^2 != a^2 (mod p) (pbits=%d)\n", q.bitlen - 1);
                return FAILED;
            }
        }
    }
    ibz_t a, q;
    ibz_set(&a, 3, 7);
    ibz_set(&q, 5, 7);
    if (ibz_sqrt_mod_p(&a, &a, &q)) {
        printf("Failed: ibz_sqrt_mod_p returned true for a non-square (p=%d, a=%d)\n", 5, 3);
        return FAILED;
    }
    return PASSED;
}

int
test_ibz_sqrt_m1_mod(void)
{
    for (size_t pi = 0; pi < NUM_TEST_PRIMES; pi++) {
        ibz_t pz = test_primes[pi];
        ibz_t r = { 0 };
        if ((ibz_get(&pz) & 3) != 1)
            continue;
        ibz_sqrt_m1_mod(&r, &pz);

        if (!ibz_is_positive(&r) || ibz_cmp(&r, &pz) >= 0) {
            printf("Failed: ibz_sqrt_m1_mod result not in [0, p) (pbits=%d)\n", pz.bitlen - 1);
            return FAILED;
        }

        ibz_t r2 = { 0 }, pm1 = { 0 };
        ibz_mulmod(&r2, &r, &r, &pz);
        ibz_sub(&pm1, &pz, &ibz_const_one);
        if (!ibz_eq(&r2, &pm1)) {
            printf("Failed: ibz_sqrt_m1_mod(p)^2 != -1 (mod p) (pbits=%d)\n", pz.bitlen - 1);
            return FAILED;
        }
    }
    return PASSED;
}

int
test_ibz_probab_prime(void)
{
    static const int32_t known_primes[] = { 2, 3, 5, 7, 11, 13, 97, 7919 };
    static const int32_t known_composites[] = { 1, 4, 6, 8, 9, 15, 100, 7921 };

    for (size_t i = 0; i < sizeof(known_primes) / sizeof(known_primes[0]); i++) {
        ibz_t n = { 0 };
        ibz_set(&n, known_primes[i], 14);
        if (!ibz_probab_prime(&n, 20)) {
            printf("Failed: ibz_probab_prime(%d) reported composite\n", known_primes[i]);
            return FAILED;
        }
    }

    for (size_t i = 0; i < sizeof(known_composites) / sizeof(known_composites[0]); i++) {
        ibz_t n = { 0 };
        ibz_set(&n, known_composites[i], 14);
        if (ibz_probab_prime(&n, 20)) {
            printf("Failed: ibz_probab_prime(%d) reported prime\n", known_composites[i]);
            return FAILED;
        }
    }

    for (size_t i = 0; i < NUM_TEST_PRIMES; i++) {
        ibz_t p = test_primes[i];
        ibz_t pp1 = { 0 };
        ibz_add(&pp1, &p, &ibz_const_one);
        ibz_set_bound(&pp1, p.bitlen); // ibz_add conservatively bumps bitlen by 1; p+1 still fits in p's own bound
        if (!ibz_probab_prime(&p, 20)) {
            printf("Failed: ibz_probab_prime reported composite for known large prime (pbits=%d)\n", p.bitlen - 1);
            return FAILED;
        }
        if (ibz_probab_prime(&pp1, 20)) {
            printf("Failed: ibz_probab_prime reported prime for known large non-prime (pbits=%d)\n", p.bitlen - 1);
            return FAILED;
        }
    }
    return PASSED;
}

// Deterministic regression tests for corner cases found in review; each block names the exact former defect.
int
test_ibz_regressions(void)
{
    const int capacity = IBZ_NLIMBS * NUM_BITS_LIMB;

    // ibz_copy_bits used to leave the sign limb of a limb-aligned import unwritten, so a dirty target survived
    {
        ibz_t t = { 0 };
        memset(t.limbs, 0xFF, sizeof(t.limbs)); // dirty target: every stale bit set
        t.bitlen = capacity;
        digit_t src[WORDS(64)];
        memset(src, 0, sizeof(src));
        src[0] = 5;
        ibz_copy_bits(&t, src, 64);
        ibz_t five = { 0 };
        ibz_set(&five, 5, 4);
        if (!ibz_eq(&t, &five) || !ibz_is_positive(&t)) {
            printf("Failed: ibz_copy_bits kept stale target bits on a limb-aligned import\n");
            return FAILED;
        }
    }

    // ibz_copy_bits used to preserve the source's garbage bit at index bitlen (the result's sign position)
    {
        ibz_t t = { 0 };
        digit_t src[WORDS(64)];
        memset(src, 0, sizeof(src));
        src[0] = 5;
        src[WORDS(64) - 1] |= ((digit_t)1) << (63 % NUM_BITS_LIMB); // garbage at bit index 63 == bitlen
        ibz_copy_bits(&t, src, 63);
        ibz_t five = { 0 };
        ibz_set(&five, 5, 4);
        if (!ibz_eq(&t, &five) || !ibz_is_positive(&t)) {
            printf("Failed: ibz_copy_bits kept the source bit at the sign position of an unaligned import\n");
            return FAILED;
        }
    }

    // ibz_xgcd used to compute the cofactor sign masks after overwriting gcd, breaking gcd==a / gcd==b aliasing
    {
        ibz_t x = { 0 }, b = { 0 }, u = { 0 }, v = { 0 }, a_copy = { 0 }, b_copy = { 0 }, t1 = { 0 }, t2 = { 0 };
        ibz_set(&x, -3, 32);
        ibz_set(&b, 5, 32);
        ibz_copy(&a_copy, &x);
        ibz_copy(&b_copy, &b);
        ibz_xgcd(&x, &u, &v, &x, &b); // gcd aliases the negative input a
        ibz_mul(&t1, &u, &a_copy);
        ibz_mul(&t2, &v, &b_copy);
        ibz_add(&t1, &t1, &t2);
        if (!ibz_is_one(&x) || !ibz_eq(&t1, &x)) {
            printf("Failed: ibz_xgcd with gcd aliasing a negative a returned wrong cofactor signs\n");
            return FAILED;
        }

        ibz_t y = { 0 }, a2 = { 0 };
        ibz_set(&a2, 5, 32);
        ibz_set(&y, -3, 32);
        ibz_copy(&b_copy, &y);
        ibz_xgcd(&y, &u, &v, &a2, &y); // gcd aliases the negative input b
        ibz_mul(&t1, &u, &a2);
        ibz_mul(&t2, &v, &b_copy);
        ibz_add(&t1, &t1, &t2);
        if (!ibz_is_one(&y) || !ibz_eq(&t1, &y)) {
            printf("Failed: ibz_xgcd with gcd aliasing a negative b returned wrong cofactor signs\n");
            return FAILED;
        }
    }

    // ibz_sqrt_floor's debug postcondition used to read a after an aliased sqrt was already written
    {
        ibz_t n9 = { 0 }, three = { 0 };
        ibz_set(&n9, 9, 32);
        ibz_set(&three, 3, 4);
        ibz_sqrt_floor(&n9, &n9);
        if (!ibz_eq(&n9, &three)) {
            printf("Failed: ibz_sqrt_floor with sqrt aliasing a\n");
            return FAILED;
        }
    }

    // ibz_div_2exp / ibz_mul_2exp: capacity-sized shifts used to go through unchecked int casts
    {
        ibz_t big = { 0 }, r = { 0 };
        ibz_set(&big, 123, 32);
        ibz_div_2exp(&r, &big, (uint32_t)capacity);
        if (!ibz_is_zero(&r)) {
            printf("Failed: ibz_div_2exp by 2^capacity must give 0\n");
            return FAILED;
        }
        ibz_mul_2exp(&r, &big, (uint32_t)capacity);
        if (!ibz_is_zero(&r)) {
            printf("Failed: ibz_mul_2exp by 2^capacity must saturate to 0\n");
            return FAILED;
        }
    }

    return PASSED;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int iterations = 20 * SQISIGN_TEST_REPS;
    int help = 0;
    int seed_set = 0;
    int res = 0;

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
        printf("Where <iterations> is the number of iterations used for testing; if not "
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

    unsigned int N = (unsigned int)iterations;

    res |= test_ibz_set_copy_swap(N);
    res |= test_ibz_set_bound(N);
    res |= test_ibz_get(N);
    res |= test_ibz_str_roundtrip(N);
    res |= test_ibz_add_sub(N);
    res |= test_ibz_mul(N);
    res |= test_ibz_div_mod(N);
    res |= test_ibz_divides(N);
    res |= test_ibz_shifts_two_adic(N);
    res |= test_ibz_pow(N);
    res |= test_ibz_pow_mod(N);
    res |= test_ibz_cmp_predicates(N);
    res |= test_ibz_rand_interval(N);
    res |= test_ibz_bitsize(N);
    res |= test_ibz_bound_helpers(N);
    res |= test_ibz_extract(N);
    res |= test_ibz_gcd(N);
    res |= test_ibz_xgcd(N);
    res |= test_ibz_crt(N);
    res |= test_ibz_legendre(N);
    res |= test_ibz_invmod(N);
    res |= test_ibz_invmat(N);
    res |= test_ibz_sqrt_floor(N);
    res |= test_ibz_sqrt_mod_p(N);
    res |= test_ibz_sqrt_m1_mod();
    res |= test_ibz_probab_prime();
    res |= test_ibz_regressions();

    if (res) {
        printf("Tests failed!\n");
    } else {
        printf("All mp (ibz) arithmetic tests passed.\n");
    }

    return res;
}
