// Shared fixtures and random-generation helpers for the mp test and bench executables; see mp_test_utils.h.

#include <assert.h>
#include <string.h>

#include <prng.h>

#include "mp_test_utils.h"

#if RADIX == 32
const ibz_t p10 = { .limbs = { 0x377 }, .bitlen = 11 };
const ibz_t p60 = {
    .limbs = { 0x3c0a9ae3, 0xb362a44 },
    .bitlen = 61
};
const ibz_t p110 = {
    .limbs = { 0x979187c9, 0x089c5148, 0x71f04d8b, 0x2ba6 },
    .bitlen = 111
};
const ibz_t p260 = {
    .limbs = { 0x4913cc21, 0xf1d2add1, 0xa3fb81eb, 0xc6a72aea, 0x20c0361a, 0xc9d0a74b, 0xf808ae9c, 0x0a1d5ef8, 0x8 },
    .bitlen = 261
};
const ibz_t p957 = {
    .limbs = { 0x83ef419d, 0xb9b491d5, 0x3535a511, 0x8bf5d8c5, 0xd3a816cd, 0x6f4ba765, 0xc0969c6b, 0x10a19e0f,
              0xfc1865aa, 0x25b21afa, 0xed9a11ea, 0x77a65575, 0x839718d8, 0x6e40b111, 0x8b5c0a32, 0x5c479c64,
              0xb988d366, 0x37dfecc0, 0x72e1cd10, 0xb34f8115, 0x7a12f75f, 0x60348d25, 0x075e9d48, 0x431bb154,
              0xf4fba1eb, 0xc2758fe3, 0xa1e28148, 0x23b1bacc, 0x7f4d186e, 0x1f8ca92c },
    .bitlen = 958
};
#if BITS >= 384
const ibz_t p390 = {
    .limbs = { 0x1c184d2d,
              0x90c8418c, 0x912bb38f,
              0xc0f3dcf2, 0x6baa9a7e,
              0x135a4610, 0xacd3ae70,
              0x1bc59a07, 0xdbd15e9d,
              0xb4a4e34e, 0x8ec2d65c,
              0x2af33cde, 0x3b },
    .bitlen = 391
};
const ibz_t p1469 = {
    .limbs = { 0xdef1909d, 0xa32aabf5, 0x71f4ebc1, 0xbc7a0139, 0x9e8d8988, 0xa7bb9c7c, 0x30bac2bb, 0xd618d0a2,
              0x810a55d3, 0xbd018e4b, 0x7a834cb0, 0xd5d9c4a6, 0x8a9f48cf, 0xa7c26a21, 0x5c2dbd87, 0x79d8e2ab,
              0x2f35e287, 0x06e51d80, 0x9ef2fba7, 0x9320bd8d, 0xbbeddcee, 0xa09a65c4, 0x7d1c3742, 0xb14d4d6e,
              0x1d23f0f6, 0xf3f05972, 0x7b8fa8ee, 0x67f38697, 0x2a1abf92, 0xb36b82b2, 0xd95597c6, 0x5a053895,
              0x7fd58b5e, 0x829cbdf1, 0x06299eb2, 0x0e75bcaf, 0xd6f56727, 0xf00b6575, 0xc5de451d, 0xe7bf4e05,
              0xd17c8d6e, 0xf026c54e, 0x4e63ddd8, 0x54b765c2, 0x552a90fd, 0x1dfcc5e6 },
    .bitlen = 1470
};
#endif
#if BITS >= 512
const ibz_t p520 = {
    .limbs = { 0xdb4ed99f,
              0xac0d2453, 0xfd14b337,
              0x9048300e, 0xa03bd914,
              0xf892f56e, 0xc04a8f21,
              0x27166e06, 0x7e16e1d,
              0xe58c2dca, 0xeddbe963,
              0xa5e4d27c, 0x1736ce49,
              0x4c20fa06, 0xee04fc16,
              0xb1c0bead, 0xaf },
    .bitlen = 521
};
const ibz_t p1981 = {
    .limbs = { 0xe298a757, 0xcc64f4da, 0x507611b3, 0x3eb2b8e1, 0x96fe1c37, 0x6b386987, 0xb074c256, 0xe4b59dee,
              0x2cd66a23, 0xc3061565, 0x51fa4602, 0xa50b6470, 0x52f8477b, 0x813f0d8e, 0x8d844443, 0x6d2fbcf1,
              0xe7a59a34, 0x3ad4e837, 0xd992b258, 0x73d65184, 0xcc3a9cfb, 0x877603ac, 0x2d2ee09f, 0x3ba28588,
              0x9eb407a8, 0xfa316a83, 0x78946153, 0xd02790ba, 0x033e0aeb, 0xe32d615c, 0xdd6822dc, 0xc3750107,
              0xa9de5c0f, 0x5bc313cd, 0xc1588057, 0xd08ff6b4, 0x740af369, 0x3c0962f1, 0x09d9ad77, 0xb6c918d8,
              0x26f69df8, 0xb128990d, 0x9bdc498f, 0xcef97f88, 0x426d387c, 0xa4855ff1, 0xd8b05999, 0xa6ce6c96,
              0x8290f3a6, 0x1f8088cc, 0xaac60632, 0x7ad75ad4, 0x6349536d, 0xd0149d89, 0xdf3e2d8d, 0x1569ab4e,
              0x79ad36de, 0x90e0db51, 0x4d527dc9, 0x5068f320, 0x6a6453d3, 0x1f853443 },
    .bitlen = 1982
};
#endif
#if BITS >= 704
const ibz_t p650 = {
    .limbs = { 0xdfb5aee5, 0x310ba698, 0x79fb1bd1, 0x16d5d989, 0x47091792, 0x84d5b5b5, 0x7c50dd3f,
              0xac29b7c9, 0xe90c6cc0, 0x5466cf34, 0xd01377be, 0x2821e638, 0x4e6c8945, 0x2efa98ec,
              0x9f31d008, 0x9382229,  0x707344a4, 0x198a2e03, 0xa308d313, 0x3f6a8885, 0x324 },
    .bitlen = 651
};
const ibz_t p2493 = {
    .limbs = { 0xdb3141db, 0x7e25ff40, 0xc35a5dcd, 0xb9dc7a44, 0x944ac33,  0xe3d1929c, 0x9b61267a, 0xf57eb5d1,
              0xb4dc3c98, 0xb672e1f0, 0xeba0c18f, 0x515d4e2a, 0x8b1b7de1, 0x9d9f70a0, 0x7be3974c, 0x750aa435,
              0xa08a0f46, 0xb5a662e1, 0x51555885, 0x2ae51cb,  0x131f40a2, 0xa2ba44c3, 0x9d52ad5c, 0x732a92f,
              0xd2ab02e3, 0x3bc5797e, 0xde98a59,  0xf6b8abbe, 0x5d80f451, 0x7364f074, 0x8301d0c0, 0x7c73cee5,
              0xc5c6d9c7, 0x86520bc8, 0x1943042f, 0x9e2e8d81, 0xc9579300, 0xace186a9, 0xee12d2cd, 0x73daa520,
              0xc410aa57, 0xc38c5e6a, 0x7b9475b2, 0xf06caba4, 0x1fa499eb, 0x4d22c7f5, 0xc38aba73, 0xb31b4906,
              0x142c77e0, 0xb8400f97, 0x3d9c8b67, 0xc9250cca, 0x2f8963fc, 0xb5d3e482, 0x6b5133f4, 0xbdc70d7f,
              0xde80d6fd, 0x617feb96, 0x34c6fdad, 0xde89885d, 0xcc4bcfd8, 0xbc90b6ae, 0xadaa3848, 0xe9fc26ad,
              0xbe4be286, 0x6605614d, 0x79a74863, 0xbdf2a336, 0x31c6809b, 0x4a29410f, 0xc7627364, 0x804177d4,
              0x114cf98e, 0x252049c1, 0x701b839a, 0x9898cc51, 0x442d1846, 0x1921fb54 },
    .bitlen = 2494
};
#endif
#elif RADIX == 64
const ibz_t p10 = { .limbs = { 0x377 }, .bitlen = 11 };
const ibz_t p60 = { .limbs = { 0xb362a443c0a9ae3 }, .bitlen = 61 };
const ibz_t p110 = {
    .limbs = { 0x089c5148979187c9, 0x2ba671f04d8b },
    .bitlen = 111
};
const ibz_t p260 = {
    .limbs = { 0xf1d2add14913cc21, 0xc6a72aeaa3fb81eb, 0xc9d0a74b20c0361a, 0x0a1d5ef8f808ae9c, 0x8 },
    .bitlen = 261
};
const ibz_t p957 = {
    .limbs = { 0xb9b491d583ef419d,
              0x8bf5d8c53535a511, 0x6f4ba765d3a816cd,
              0x10a19e0fc0969c6b, 0x25b21afafc1865aa,
              0x77a65575ed9a11ea, 0x6e40b111839718d8,
              0x5c479c648b5c0a32, 0x37dfecc0b988d366,
              0xb34f811572e1cd10, 0x60348d257a12f75f,
              0x431bb154075e9d48, 0xc2758fe3f4fba1eb,
              0x23b1bacca1e28148, 0x1f8ca92c7f4d186e },
    .bitlen = 958
};
#if BITS >= 384
const ibz_t p390 = {
    .limbs = { 0x90c8418c1c184d2d,
              0xc0f3dcf2912bb38f, 0x135a46106baa9a7e,
              0x1bc59a07acd3ae70, 0xb4a4e34edbd15e9d,
              0x2af33cde8ec2d65c, 0x3b },
    .bitlen = 391
};
const ibz_t p1469 = {
    .limbs = { 0xa32aabf5def1909d, 0xbc7a013971f4ebc1, 0xa7bb9c7c9e8d8988, 0xd618d0a230bac2bb, 0xbd018e4b810a55d3,
              0xd5d9c4a67a834cb0, 0xa7c26a218a9f48cf, 0x79d8e2ab5c2dbd87, 0x06e51d802f35e287, 0x9320bd8d9ef2fba7,
              0xa09a65c4bbeddcee, 0xb14d4d6e7d1c3742, 0xf3f059721d23f0f6, 0x67f386977b8fa8ee, 0xb36b82b22a1abf92,
              0x5a053895d95597c6, 0x829cbdf17fd58b5e, 0x0e75bcaf06299eb2, 0xf00b6575d6f56727, 0xe7bf4e05c5de451d,
              0xf026c54ed17c8d6e, 0x54b765c24e63ddd8, 0x1dfcc5e6552a90fd },
    .bitlen = 1470
};
#endif
#if BITS >= 512
const ibz_t p520 = {
    .limbs = { 0xac0d2453db4ed99f,
              0x9048300efd14b337, 0xf892f56ea03bd914,
              0x27166e06c04a8f21, 0xe58c2dca07e16e1d,
              0xa5e4d27ceddbe963, 0x4c20fa061736ce49,
              0xb1c0beadee04fc16, 0xaf },
    .bitlen = 521
};
const ibz_t p1981 = {
    .limbs = { 0xcc64f4dae298a757, 0x3eb2b8e1507611b3, 0x6b38698796fe1c37, 0xe4b59deeb074c256, 0xc30615652cd66a23,
              0xa50b647051fa4602, 0x813f0d8e52f8477b, 0x6d2fbcf18d844443, 0x3ad4e837e7a59a34, 0x73d65184d992b258,
              0x877603accc3a9cfb, 0x3ba285882d2ee09f, 0xfa316a839eb407a8, 0xd02790ba78946153, 0xe32d615c033e0aeb,
              0xc3750107dd6822dc, 0x5bc313cda9de5c0f, 0xd08ff6b4c1588057, 0x3c0962f1740af369, 0xb6c918d809d9ad77,
              0xb128990d26f69df8, 0xcef97f889bdc498f, 0xa4855ff1426d387c, 0xa6ce6c96d8b05999, 0x1f8088cc8290f3a6,
              0x7ad75ad4aac60632, 0xd0149d896349536d, 0x1569ab4edf3e2d8d, 0x90e0db5179ad36de, 0x5068f3204d527dc9,
              0x1f8534436a6453d3 },
    .bitlen = 1982
};
#endif
#if BITS >= 704
const ibz_t p650 = {
    .limbs = { 0x310ba698dfb5aee5,
              0x16d5d98979fb1bd1, 0x84d5b5b547091792,
              0xac29b7c97c50dd3f, 0x5466cf34e90c6cc0,
              0x2821e638d01377be, 0x2efa98ec4e6c8945,
              0x93822299f31d008, 0x198a2e03707344a4,
              0x3f6a8885a308d313, 0x324 },
    .bitlen = 651
};
const ibz_t p2493 = {
    .limbs = { 0x7e25ff40db3141db, 0xb9dc7a44c35a5dcd, 0xe3d1929c0944ac33, 0xf57eb5d19b61267a, 0xb672e1f0b4dc3c98,
              0x515d4e2aeba0c18f, 0x9d9f70a08b1b7de1, 0x750aa4357be3974c, 0xb5a662e1a08a0f46, 0x2ae51cb51555885,
              0xa2ba44c3131f40a2, 0x732a92f9d52ad5c,  0x3bc5797ed2ab02e3, 0xf6b8abbe0de98a59, 0x7364f0745d80f451,
              0x7c73cee58301d0c0, 0x86520bc8c5c6d9c7, 0x9e2e8d811943042f, 0xace186a9c9579300, 0x73daa520ee12d2cd,
              0xc38c5e6ac410aa57, 0xf06caba47b9475b2, 0x4d22c7f51fa499eb, 0xb31b4906c38aba73, 0xb8400f97142c77e0,
              0xc9250cca3d9c8b67, 0xb5d3e4822f8963fc, 0xbdc70d7f6b5133f4, 0x617feb96de80d6fd, 0xde89885d34c6fdad,
              0xbc90b6aecc4bcfd8, 0xe9fc26adadaa3848, 0x6605614dbe4be286, 0xbdf2a33679a74863, 0x4a29410f31c6809b,
              0x804177d4c7627364, 0x252049c1114cf98e, 0x9898cc51701b839a, 0x1921fb54442d1846 },
    .bitlen = 2494
};
#endif
#endif

#if BITS < 384
ibz_t test_primes[NUM_TEST_PRIMES] = { p10, p60, p110, p260, p957 };
#elif BITS < 512
ibz_t test_primes[NUM_TEST_PRIMES] = { p10, p60, p110, p260, p390, p957, p1469 };
#elif BITS < 704
ibz_t test_primes[NUM_TEST_PRIMES] = { p10, p60, p110, p260, p390, p520, p957, p1469, p1981 };
#else
ibz_t test_primes[NUM_TEST_PRIMES] = { p10, p60, p110, p260, p390, p520, p650, p957, p1469, p1981, p2493 };
#endif

uint32_t
rand_u32_range(uint32_t bound) // uniform-ish value in [0, bound)
{
    uint32_t v = 0;
    int ret = prng_random_bytes(&PRNG_default_domain, (unsigned char *)&v, sizeof(v));
    assert(ret == 0);
    (void)ret;
    return bound ? (v % bound) : 0;
}

uint64_t
rand_u64(void) // uniform value in [0, 2^64)
{
    uint64_t v = 0;
    int ret = prng_random_bytes(&PRNG_default_domain, (unsigned char *)&v, sizeof(v));
    assert(ret == 0);
    (void)ret;
    return v;
}

int
ibz_eq(const ibz_t *a, const ibz_t *b)
{
    return ibz_cmp(a, b) == 0;
}

// Computes (a*b) mod m via binary double-and-add, without ever forming the full a*b product. ibz_mul needs
// a->bitlen + b->bitlen - 1 bits of headroom and silently truncates past the container's capacity, so it corrupts
// results for test primes whose square doesn't fit; this stays bounded by ~2*m at every step instead.
void
ibz_mulmod(ibz_t *res, const ibz_t *a, const ibz_t *b, const ibz_t *m)
{
    ibz_t aa = { 0 }, bb = { 0 }, r = { 0 };
    ibz_mod(&aa, a, m);
    ibz_mod(&bb, b, m);

    ibz_copy(&r, &ibz_const_zero);
    ibz_set_bound(&r, m->bitlen);
    int bits = ibz_bitsize(&bb);
    for (int i = bits - 1; i >= 0; i--) {
        ibz_add(&r, &r, &r);
        if (ibz_cmp(&r, m) >= 0) {
            ibz_sub(&r, &r, m);
        }
        ibz_set_bound(&r, m->bitlen);

        int word = i / NUM_BITS_LIMB, bitpos = i % NUM_BITS_LIMB;
        if ((bb.limbs[word] >> bitpos) & 1) {
            ibz_add(&r, &r, &aa);
            if (ibz_cmp(&r, m) >= 0) {
                ibz_sub(&r, &r, m);
            }
            ibz_set_bound(&r, m->bitlen);
        }
    }
    ibz_copy(res, &r);
}

// Set out to the non-negative value v, with `bits` two's complement bits of precision.
void
ibz_set_u64(ibz_t *out, uint64_t v, int bits)
{
    memset(out->limbs, 0, sizeof(out->limbs));
    for (int i = 0; i < WORDS(64); i++) {
        out->limbs[i] = (digit_t)(v >> (i * RADIX));
    }
    out->bitlen = bits;
}

// Random non-negative ibz_t of `bits` two's complement bits:
// uniform in [0, 2^(bits-1)), i.e. the sign bit (bit bits-1) is cleared.
void
rand_ibz_nonneg(ibz_t *out, int bits)
{
    if (bits <= 0) {
        ibz_copy(out, &ibz_const_zero);
        return;
    }
    int w = WORDS(bits) - 1; // last word in use
    int wordbits = (int)(8 * sizeof(digit_t));
    int pad = (wordbits - bits % wordbits) % wordbits; // number of bits above the signed bit in the last word
    // Fill necessary words
    int ret = prng_random_bytes(&PRNG_default_domain, (unsigned char *)out->limbs, sizeof(digit_t) * WORDS(bits));
    assert(ret == 0);
    (void)ret;
    // turn to 0 everything at and above the signed bit
    if (pad + 1 >= wordbits) {
        out->limbs[w] = 0;
    } else {
        out->limbs[w] >>= pad + 1;
    }
    out->bitlen = bits;
}

// Random signed ibz_t of `bits` two's complement bits: a uniform magnitude in [0, 2^(bits-1)) with a uniform sign.
// Never produces -2^(bits-1).
void
rand_ibz_signed(ibz_t *out, int bits)
{
    if (bits <= 0) {
        ibz_copy(out, &ibz_const_zero);
        return;
    }
    rand_ibz_nonneg(out, bits);
    unsigned char sign = 0;
    int ret = prng_random_bytes(&PRNG_default_domain, &sign, sizeof(sign));
    assert(ret == 0);
    (void)ret;
    if (sign & 1) {
        ibz_neg(out, out);
    }
}

// Odd, strictly positive value of `bits` two's complement bits (bits >= 2).
// Guaranteed non-zero by construction (low bit set), no rejection sampling.
void
rand_ibz_odd_positive(ibz_t *out, int bits)
{
    rand_ibz_nonneg(out, bits);
    out->limbs[0] |= 1;
}
