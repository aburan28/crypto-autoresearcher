#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
typedef uint64_t fp_t[N];
typedef struct
{
    fp_t re, im;
} fp2_t;
extern void fp_add(fp_t *, const fp_t *, const fp_t *);
extern void fp_sub(fp_t *, const fp_t *, const fp_t *);
extern void fp_mul(fp_t *, const fp_t *, const fp_t *);
extern void fp_sqr(fp_t *, const fp_t *);
extern void fp2_mul_c0(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_mul_c1(fp_t *, const fp2_t *, const fp2_t *);
extern void fp2_sq_c0(fp2_t *, const fp2_t *);
extern void fp2_sq_c1(fp_t *, const fp2_t *);
int
main(int argc, char **argv)
{
    fp_t a, b, c;
    fp2_t A, B, C2;
    memset(a, 0x11, sizeof a);
    memset(b, 0x22, sizeof b);
    a[N - 1] &= 1;
    b[N - 1] &= 1;
    memset(&A, 0x33, sizeof A);
    memset(&B, 0x44, sizeof B);
    A.re[N - 1] &= 1;
    A.im[N - 1] &= 1;
    B.re[N - 1] &= 1;
    B.im[N - 1] &= 1;
    int w = atoi(argv[1]);
    switch (w) {
        case 0:
            fp_add(&c, &a, &b);
            break;
        case 1:
            fp_sub(&c, &a, &b);
            break;
        case 2:
            fp_mul(&c, &a, &b);
            break;
        case 3:
            fp_sqr(&c, &a);
            break;
        case 4:
            fp2_mul_c0(&c, &A, &B);
            break;
        case 5:
            fp2_mul_c1(&c, &A, &B);
            break;
        case 6:
            fp2_sq_c0(&C2, &A);
            break;
        case 7:
            fp2_sq_c1(&c, &A);
            break;
    }
    printf("survived %d\n", w);
    return 0;
}
