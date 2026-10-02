#include <stdlib.h>
/* Dumps inputs+outputs of the generated asm as hex; check.py verifies mod p. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#ifndef N
#error "define N"
#endif
#define TOPMASK ((SHIFT >= 64) ? ~0ULL : ((1ULL << SHIFT) - 1))
typedef uint64_t fp_t[N];
typedef struct
{
    fp_t re, im;
} fp2_t;

extern void fp_add(fp_t *, const fp_t *, const fp_t *);
extern void fp_sub(fp_t *, const fp_t *, const fp_t *);
extern void fp_mul(fp_t *, const fp_t *, const fp_t *);
extern void fp_sqr(fp_t *, const fp_t *);
#ifdef FP2_FUSED /* arm64 generator: one call computes both components */
extern void fp2_mul(fp2_t *, const fp2_t *, const fp2_t *);
extern void fp2_sqr(fp2_t *, const fp2_t *);
#else
extern void fp2_mul_c0(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_mul_c1(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_sq_c0(fp2_t *, const fp2_t *);
extern void fp2_sq_c1(fp_t *, const fp2_t *);
#endif

static uint64_t st = 0x243f6a8885a308d3ULL;
static uint64_t
rnd(void)
{
    st ^= st << 13;
    st ^= st >> 7;
    st ^= st << 17;
    return st;
}
static void
ph(const char *tag, const uint64_t *v, int n)
{
    printf("%s ", tag);
    for (int i = n - 1; i >= 0; i--)
        printf("%016llx", (unsigned long long)v[i]);
    printf("\n");
}
/* canary check: callee-saved regs + return address survive */
int
main(int argc, char **argv)
{
    int iters = argc > 1 ? atoi(argv[1]) : 2000;
    fp_t a, b, c;
    fp2_t A, B, C2;
    for (int it = 0; it < iters; it++) {
        for (int i = 0; i < N; i++) {
            a[i] = rnd();
            b[i] = rnd();
        }
        /* input contract: value < 2^BITS, i.e. mask the top limb to SHIFT bits */
        a[N - 1] &= TOPMASK;
        b[N - 1] &= TOPMASK;
        ph("a", a, N);
        ph("b", b, N);
        fp_add(&c, &a, &b);
        ph("add", c, N);
        fp_sub(&c, &a, &b);
        ph("sub", c, N);
        fp_mul(&c, &a, &b);
        ph("mul", c, N);
        fp_sqr(&c, &a);
        ph("sqr", c, N);
        memcpy(A.re, a, sizeof a);
        for (int i = 0; i < N; i++)
            A.im[i] = rnd();
        memcpy(B.re, b, sizeof b);
        for (int i = 0; i < N; i++)
            B.im[i] = rnd();
        A.im[N - 1] &= TOPMASK;
        B.im[N - 1] &= TOPMASK;
        ph("A0", A.re, N);
        ph("A1", A.im, N);
        ph("B0", B.re, N);
        ph("B1", B.im, N);
#ifdef FP2_FUSED
        fp2_mul(&C2, &A, &B);
        ph("m0", C2.re, N);
        ph("m1", C2.im, N);
        /* in-place aliasing: fp2_mul(x, x, y) must match the non-aliased call */
        {
            fp2_t T = A, U = B;
            fp2_mul(&T, &T, &B);
            if (memcmp(&T, &C2, sizeof T)) {
                fprintf(stderr, "fp2_mul(x, x, y) aliasing mismatch\n");
                return 3;
            }
            fp2_mul(&U, &A, &U);
            if (memcmp(&U, &C2, sizeof U)) {
                fprintf(stderr, "fp2_mul(x, y, x) aliasing mismatch\n");
                return 3;
            }
        }
#else
        fp2_mul_c0(&c, &A, &B);
        ph("m0", c, N);
        fp2_mul_c1(&c, &A, &B);
        ph("m1", c, N);
#endif
#ifdef FP2_FUSED
        fp2_sqr(&C2, &A);
        ph("s0", C2.re, N);
        ph("s1", C2.im, N);
        /* in-place aliasing: fp2_sqr(x, x) must match the non-aliased call */
        {
            fp2_t T = A;
            fp2_sqr(&T, &T);
            if (memcmp(&T, &C2, sizeof T)) {
                fprintf(stderr, "fp2_sqr(x, x) aliasing mismatch\n");
                return 3;
            }
        }
#else
        fp2_sq_c0(&C2, &A);
        ph("s0", C2.re, N);
        fp2_sq_c1(&c, &A);
        ph("s1", c, N);
#endif
    }
    return 0;
}
