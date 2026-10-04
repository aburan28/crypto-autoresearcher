/* gf5248_div-based fp_inv vs exponentiation-based, and legendre vs a^((p-1)/2). */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "fp.h"

static uint64_t
rdtscp_(void)
{
    unsigned a;
    return __builtin_ia32_rdtscp(&a);
}
static uint64_t st = 0x123456789abcdefULL;
static uint64_t
rnd(void)
{
    st ^= st << 13;
    st ^= st >> 7;
    st ^= st << 17;
    return st;
}

/* a^(p-2) = (a^((p-3)/4))^4 * a   for p = 3 mod 4 */
static void
fp_inv_exp(fp_t *x)
{
    fp_t t;
    fp_copy(&t, x);
    fp_exp3div4(&t);
    fp_sqr(&t, &t);
    fp_sqr(&t, &t);
    fp_mul(x, &t, x);
}
/* legendre via a^((p-1)/2) = (a^((p-3)/4))^2 * a */
static uint32_t
fp_is_square_exp(const fp_t *a)
{
    fp_t t;
    fp_copy(&t, a);
    fp_exp3div4(&t);
    fp_sqr(&t, &t);
    fp_mul(&t, &t, a);
    fp_t one;
    fp_set_one(&one);
    return fp_is_equal(&t, &one) | fp_is_zero(a);
}
#define BENCH(label, code)                                                                                             \
    do {                                                                                                               \
        uint64_t best = ~0ULL;                                                                                         \
        for (int r = 0; r < 7; r++) {                                                                                  \
            uint64_t c0 = rdtscp_();                                                                                   \
            for (int i = 0; i < ITER; i++) {                                                                           \
                code;                                                                                                  \
            }                                                                                                          \
            uint64_t d = rdtscp_() - c0;                                                                               \
            if (d < best)                                                                                              \
                best = d;                                                                                              \
        }                                                                                                              \
        printf("  %-28s %8.0f cycles/op\n", label, (double)best / ITER);                                               \
    } while (0)
#define ITER 20000
int
main(void)
{
    fp_t a, b;
    uint64_t buf[8];
    for (int i = 0; i < 8; i++)
        buf[i] = rnd();
    memcpy(&a, buf, sizeof(fp_t));
    memcpy(&b, buf, sizeof(fp_t));
    /* correctness first */
    fp_t x, y;
    memcpy(&x, buf, sizeof(fp_t));
    memcpy(&y, buf, sizeof(fp_t));
    fp_inv(&x);
    fp_inv_exp(&y);
    printf("  inv agree: %s\n", fp_is_equal(&x, &y) ? "YES" : "NO");
    printf("  issq agree: %s\n", (fp_is_square(&a) == fp_is_square_exp(&a)) ? "YES" : "NO");
    BENCH("fp_inv (gf5248_div)", {
        memcpy(&x, buf, sizeof(fp_t));
        fp_inv(&x);
    });
    BENCH("fp_inv (exponentiation)", {
        memcpy(&x, buf, sizeof(fp_t));
        fp_inv_exp(&x);
    });
    BENCH("fp_is_square (legendre)", { fp_is_square(&a); });
    BENCH("fp_is_square (exp)", { fp_is_square_exp(&a); });
    BENCH("fp_mul (reference)", { fp_mul(&x, &a, &b); });
    return 0;
}
