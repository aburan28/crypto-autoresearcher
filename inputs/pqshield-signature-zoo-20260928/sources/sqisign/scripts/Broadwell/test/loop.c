/* Closed feedback loop: outputs become the next inputs, as real code does. */
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define TOPMASK ((SHIFT >= 64) ? ~0ULL : ((1ULL << SHIFT) - 1))
typedef uint64_t fp_t[N];
typedef struct
{
    fp_t re, im;
} fp2_t;
extern void fp_add(fp_t *, const fp_t *, const fp_t *);
extern void fp_mul(fp_t *, const fp_t *, const fp_t *);
extern void fp2_mul_c0(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_mul_c1(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_sq_c0(fp2_t *, const fp2_t *);
extern void fp2_sq_c1(fp_t *, const fp2_t *);
static uint64_t st = 0x9e3779b97f4a7c15ULL;
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
int
main(int argc, char **argv)
{
    int iters = argc > 1 ? atoi(argv[1]) : 1000;
    fp2_t A, B, C;
    fp_t t0;
    for (int i = 0; i < N; i++) {
        A.re[i] = rnd();
        A.im[i] = rnd();
        B.re[i] = rnd();
        B.im[i] = rnd();
    }
    A.re[N - 1] &= TOPMASK;
    A.im[N - 1] &= TOPMASK;
    B.re[N - 1] &= TOPMASK;
    B.im[N - 1] &= TOPMASK;
    for (int it = 0; it < iters; it++) {
        /* one fp2 multiply + one fp2 square, results fed straight back */
        ph("A0", A.re, N);
        ph("A1", A.im, N);
        ph("B0", B.re, N);
        ph("B1", B.im, N);
        fp2_mul_c0(&t0, &A, &B);
        ph("m0", t0, N);
        memcpy(C.re, t0, sizeof t0);
        fp2_mul_c1(&t0, &A, &B);
        ph("m1", t0, N);
        memcpy(C.im, t0, sizeof t0);
        memcpy(&A, &C, sizeof C);
        ph("A0", A.re, N);
        ph("A1", A.im, N);
        ph("B0", B.re, N);
        ph("B1", B.im, N);
        {
            fp2_t s;
            fp2_sq_c0(&s, &A);
            ph("s0", s.re, N);
            memcpy(C.re, s.re, sizeof s.re);
        }
        fp2_sq_c1(&t0, &A);
        ph("s1", t0, N);
        memcpy(C.im, t0, sizeof t0);
        memcpy(&B, &C, sizeof C);
    }
    return 0;
}
