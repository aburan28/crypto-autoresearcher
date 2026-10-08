// Differential test: fp_generic vs the shipping gfXXXX + sat64 fp.c reference.
// Build with -DGFHDR='"gf5248.h"' -DGFT=gf5248 -DHAVE_REF=1 (or HAVE_REF=0 for
// property-only testing of a new prime with no reference implementation).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fp_generic.h>

#if HAVE_REF
#include GFHDR
#define XG(a, b) a##b
#define G(a, b) XG(a, b)
#define REF(n) G(GFT, _##n)
typedef GFT ref_t;
// sat64/<lvl>/fp.c compiled with -Dfp_inv=ref_fp_inv etc.
void ref_fp_inv(ref_t *);
void ref_fp_sqrt(ref_t *);
void ref_fp_exp3div4(ref_t *);
uint32_t ref_fp_is_square(const ref_t *);
#endif

#define NB (8 * FPG_N)

static uint64_t st = 0xdeadbeefcafef00dULL;
static uint64_t
rnd(void)
{
    st ^= st << 13;
    st ^= st >> 7;
    st ^= st << 17;
    return st;
}
static void
rnd_dom(fpg_t *x)
{
    for (int i = 0; i < FPG_N; i++)
        x->v[i] = rnd();
    x->v[FPG_N - 1] &= (UINT64_C(1) << (FPG_BITS - 64 * (FPG_N - 1))) - 1;
}
static const fpg_t PP = { FPG_P_INIT };
static int nfail = 0;
static void
fail(const char *op, int it)
{
    if (nfail < 20)
        printf("  FAIL %s (iter %d)\n", op, it);
    nfail++;
}
#if HAVE_REF
static void
canon(uint8_t *b, const void *x)
{
    REF(encode)(b, (const ref_t *)x);
}
#else
static void
canon(uint8_t *b, const void *x)
{
    fp_encode(b, (const fpg_t *)x);
}
#endif
static void
chk(const char *op, int it, const void *mine, const void *ref)
{
    uint8_t b1[NB], b2[NB];
    canon(b1, mine);
    canon(b2, ref);
    if (memcmp(b1, b2, NB))
        fail(op, it);
}

int
main(int argc, char **argv)
{
    int iters = argc > 1 ? atoi(argv[1]) : 1000000;
    fpg_t a, b, d1, t;
    uint8_t buf[4 * NB], e1[NB], e2[NB];

#if HAVE_REF
    ref_t r1, r2;
    chk("ONE const", 0, &fpg_ONE, &G(GFT, _ONE));
    chk("ZERO const", 0, &fpg_ZERO, &G(GFT, _ZERO));
#endif

    for (int it = 0; it < iters; it++) {
        rnd_dom(&a);
        rnd_dom(&b);
        uint32_t x32 = (uint32_t)rnd();
        uint32_t ctl = (rnd() & 1) ? 0xFFFFFFFFu : 0;

#if HAVE_REF
        // value ops vs gfXXXX
        fp_neg(&d1, &a);
        REF(neg)(&r1, (const ref_t *)&a);
        chk("neg", it, &d1, &r1);
        fp_half(&d1, &a);
        REF(half)(&r1, (const ref_t *)&a);
        chk("half", it, &d1, &r1);
        fp_div3(&d1, &a);
        REF(div3)(&r1, (const ref_t *)&a);
        chk("div3", it, &d1, &r1);
        fp_mul_small(&d1, &a, x32);
        REF(mul_small)(&r1, (const ref_t *)&a, x32);
        chk("mul_small", it, &d1, &r1);
        fp_set_small(&d1, x32);
        REF(set_small)(&r1, x32);
        chk("set_small", it, &d1, &r1);

        // select / cswap
        fp_select(&d1, &a, &b, ctl);
        REF(select)(&r1, (const ref_t *)&a, (const ref_t *)&b, ctl);
        chk("select", it, &d1, &r1);
        fpg_t ca = a, cb = b;
        ref_t ra, rb;
        memcpy(&ra, &a, sizeof a);
        memcpy(&rb, &b, sizeof b);
        fp_cswap(&ca, &cb, ctl);
        REF(cswap)(&ra, &rb, ctl);
        chk("cswap.a", it, &ca, &ra);
        chk("cswap.b", it, &cb, &rb);

        // predicates (incl. the two representations of the same value)
        if (fp_is_zero(&a) != REF(iszero)((const ref_t *)&a))
            fail("iszero", it);
        uint32_t eq_m = fp_is_equal(&a, &b);
        uint32_t eq_r = REF(equals)((const ref_t *)&a, (const ref_t *)&b);
        if (eq_m != eq_r)
            fail("equals", it);
        fpg_t u = { { 0 } }, u2;
        u.v[0] = rnd();
        u.v[0] &= (UINT64_C(1) << 32) - 1; // u < 2^T for sure
        unsigned char cc = 0;
        for (int i = 0; i < FPG_N; i++) {
            __extension__ unsigned __int128 s = (unsigned __int128)u.v[i] + PP.v[i] + cc;
            u2.v[i] = (uint64_t)s;
            cc = (unsigned char)(s >> 64);
        }
        if (fp_is_equal(&u, &u2) != 0xFFFFFFFFu)
            fail("equals.rep", it);
        if (REF(equals)((const ref_t *)&u, (const ref_t *)&u2) != 0xFFFFFFFFu)
            fail("equals.rep.ref", it);

        // encode / decode
        fp_encode(e1, &a);
        REF(encode)(e2, (const ref_t *)&a);
        if (memcmp(e1, e2, NB))
            fail("encode", it);
        uint32_t m1 = fp_decode(&d1, e1);
        uint32_t m2 = REF(decode)(&r1, e1);
        if (m1 != m2)
            fail("decode.mask", it);
        chk("decode.val", it, &d1, &r1);
        for (int i = 0; i < NB; i++)
            buf[i] = (uint8_t)rnd();
        m1 = fp_decode(&d1, buf);
        m2 = REF(decode)(&r1, buf);
        if (m1 != m2)
            fail("decode.rand.mask", it);
        chk("decode.rand.val", it, &d1, &r1);

        // decode_reduce, misc lengths
        size_t lens[] = { 0, 1, 7, 8, (size_t)NB - 1, (size_t)NB, (size_t)NB + 1, 2 * (size_t)NB + 5, 4 * (size_t)NB };
        size_t len = lens[rnd() % 9];
        for (size_t i = 0; i < len; i++)
            buf[i] = (uint8_t)rnd();
        fp_decode_reduce(&d1, buf, len);
        REF(decode_reduce)(&r1, buf, len);
        chk("decode_reduce", it, &d1, &r1);

        // inversion vs gf divstep, and the fp.c exponentiation surface
        t = a;
        fp_inv(&t);
        REF(invert)(&r1, (const ref_t *)&a);
        chk("inv", it, &t, &r1);
        memcpy(&r2, &a, sizeof a);
        ref_fp_exp3div4(&r2);
        t = a;
        fp_exp3div4(&t);
        chk("exp3div4", it, &t, &r2);
        fp_sqr(&d1, &a); // a^2: a known QR
        memcpy(&r2, &d1, sizeof d1);
        ref_fp_sqrt(&r2);
        t = d1;
        fp_sqrt(&t);
        chk("sqrt", it, &t, &r2);
        if (fp_is_square(&d1) != 0xFFFFFFFFu)
            fail("issq.sq", it);
        if (fp_is_square(&a) != ref_fp_is_square((const ref_t *)&a))
            fail("issq", it);
#else
        // property tests (no reference available)
        t = a;
        fp_inv(&t);
        fp_mul(&d1, &t, &a);
        uint8_t o1[NB], o2[NB];
        fp_encode(o1, &d1);
        fp_encode(o2, &fpg_ONE);
        if (fp_is_zero(&a) == 0 && memcmp(o1, o2, NB))
            fail("inv*a==1", it);
        fp_sqr(&d1, &a);
        t = d1;
        fp_sqrt(&t);
        fp_sqr(&t, &t);
        chk("sqrt^2", it, &t, &d1);
        if (fp_is_square(&d1) != 0xFFFFFFFFu)
            fail("issq.sq", it);
        fp_encode(e1, &a);
        if (fp_decode(&d1, e1) != 0xFFFFFFFFu)
            fail("dec(enc)", it);
        chk("roundtrip", it, &d1, &a);
        // decode_reduce of a canonical block == decode
        fp_decode_reduce(&d1, e1, NB);
        fp_decode(&t, e1);
        chk("decred==dec", it, &d1, &t);
        fp_half(&d1, &a);
        fp_add(&d1, &d1, &d1);
        chk("2*half", it, &d1, &a);
        fp_div3(&d1, &a);
        fp_mul_small(&d1, &d1, 3);
        chk("3*div3", it, &d1, &a);
#endif
        if (nfail > 40)
            break;
    }
    printf("%s: %d iterations, %d failures\n", nfail ? "FAIL" : "PASS", iters, nfail);
    return nfail != 0;
}
