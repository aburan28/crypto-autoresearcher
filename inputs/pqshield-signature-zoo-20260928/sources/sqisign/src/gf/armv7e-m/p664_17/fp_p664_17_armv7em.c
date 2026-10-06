// clang-format off
#include "code_p664_17_mont.c"

// The generated arithmetic above is all-static with _p664_17_ct-suffixed names;
// alias the plain modarith names the wrapper below uses.
#define modint modint_p664_17_ct
#define modmul modmul_p664_17_ct
#define modzer modzer_p664_17_ct
#define modone modone_p664_17_ct
#define modcmp modcmp_p664_17_ct
#define modis0 modis0_p664_17_ct
#define modcpy modcpy_p664_17_ct
#define modcsw modcsw_p664_17_ct
#define modadd modadd_p664_17_ct
#define modsub modsub_p664_17_ct
#define modneg modneg_p664_17_ct
#define modsqr modsqr_p664_17_ct
#define modinv modinv_p664_17_ct
#define modqr modqr_p664_17_ct
#define modsqrt modsqrt_p664_17_ct
#define modpro modpro_p664_17_ct
#define redc redc_p664_17_ct
#define nres nres_p664_17_ct
#define modfsb modfsb_p664_17_ct
#define modshl modshl_p664_17_ct
#define modshr modshr_p664_17_ct

/******************************************************************************
 * SQIsign fp_* API wrappers over the modarith code above.
 * Rendered from scripts/add_parameter_set_templates/field.c.j2 — generic for any prime
 * with p == 3 (mod 4). Do not hand-edit; regenerate as described in
 * src/gf/armv7e-m/README.md instead.
 ******************************************************************************/

#include <fp.h>

const fp_t ZERO = {
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0
};

const fp_t ONE = {
    0xf,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x1000000
};

// Montgomery representation of 2^-1
static const fp_t TWO_INV = {
    0x7,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x9000000
};

// Montgomery representation of 3^-1
static const fp_t THREE_INV = {
    0xaaaaaaaf,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xaaaaaaaa,
    0xbaaaaaa
};

void
fp_set_small(fp_t *x, const digit_t val)
{
    modint((int)val, x->fp);
}

void
fp_mul_small(fp_t *x, const fp_t *a, const uint32_t val)
{
    // via modmul (radix-independent; avoids modmli small-multiplier limits)
    fp_t t;
    modint((int)val, t.fp);
    modmul(a->fp, t.fp, x->fp);
}

void
fp_set_zero(fp_t *x)
{
    modzer(x->fp);
}

void
fp_set_one(fp_t *x)
{
    modone(x->fp);
}

uint32_t
fp_is_equal(const fp_t *a, const fp_t *b)
{
    return -(uint32_t)modcmp(a->fp, b->fp);
}

uint32_t
fp_is_zero(const fp_t *a)
{
    return -(uint32_t)modis0(a->fp);
}

void
fp_copy(fp_t *out, const fp_t *a)
{
    modcpy(a->fp, out->fp);
}

void
fp_cswap(fp_t *a, fp_t *b, uint32_t ctl)
{
    modcsw((int)(ctl & 0x1), a->fp, b->fp);
}

void
fp_add(fp_t *out, const fp_t *a, const fp_t *b)
{
    modadd(a->fp, b->fp, out->fp);
}

void
fp_sub(fp_t *out, const fp_t *a, const fp_t *b)
{
    modsub(a->fp, b->fp, out->fp);
}

void
fp_neg(fp_t *out, const fp_t *a)
{
    modneg(a->fp, out->fp);
}

void
fp_sqr(fp_t *out, const fp_t *a)
{
    modsqr(a->fp, out->fp);
}

void
fp_mul(fp_t *out, const fp_t *a, const fp_t *b)
{
    modmul(a->fp, b->fp, out->fp);
}

void
fp_inv(fp_t *x)
{
    modinv(x->fp, NULL, x->fp);
}

uint32_t
fp_is_square(const fp_t *a)
{
    return -(uint32_t)modqr(NULL, a->fp);
}

void
fp_sqrt(fp_t *a)
{
    modsqrt(a->fp, NULL, a->fp);
}

void
fp_half(fp_t *out, const fp_t *a)
{
    modmul(TWO_INV.fp, a->fp, out->fp);
}

void
fp_exp3div4(fp_t *out, const fp_t *a)
{
    // p == 3 (mod 4)  =>  modpro computes a^((p-3)/4)
    modpro(a->fp, out->fp);
}

void
fp_div3(fp_t *out, const fp_t *a)
{
    modmul(THREE_INV.fp, a->fp, out->fp);
}

void
fp_encode(void *dst, const fp_t *a)
{
    // little-endian canonical encoding
    int i;
    spint c[21];
    unsigned char *out = dst;
    redc(a->fp, c);
    for (i = 0; i < 84; i++) {
        out[i] = (unsigned char)(c[0] & (spint)0xff);
        (void)modshr(8, c);
    }
}

uint32_t
fp_decode(fp_t *d, const void *src)
{
    // inverse of fp_encode; returns 0xFFFFFFFF iff the input was canonical
    int i;
    spint res;
    const unsigned char *b = src;
    for (i = 0; i < 21; i++) {
        d->fp[i] = 0;
    }
    for (i = 84 - 1; i >= 0; i--) {
        modshl(8, d->fp);
        d->fp[0] += (spint)b[i];
    }
    res = (spint)-modfsb(d->fp);
    nres(d->fp, d->fp);
    for (i = 0; i < 21; i++) {
        d->fp[i] &= res;
    }
    return (uint32_t)res;
}

void
fp_decode_reduce(fp_t *d, const void *src, size_t len)
{
    // Reduce a little-endian byte string of arbitrary length mod p.
    // Radix-256 Horner using only fp_add/fp_set_small: correct for ANY prime,
    // no prime-shape-specific fast reduction required.
    const unsigned char *b = src;
    size_t i;
    fp_set_zero(d);
    for (i = len; i-- > 0;) {
        fp_t t;
        int k;
        for (k = 0; k < 8; k++) {
            fp_add(d, d, d); // d *= 2  (eight times => d *= 256)
        }
        fp_set_small(&t, (digit_t)b[i]);
        fp_add(d, d, &t);
    }
}

_Static_assert(NWORDS_FIELD == Nlimbs_p664_17_ct,
               "saturated 32-bit layout: compile with -DSQISIGN_GF_IMPL_SAT32");
