#include <limits.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

#include "api.h"
#include "gf.h"
#include "fql.h"
#include "linsys.h"
#include "prim.h"
#include "prg.h"
#include "qrop.h"
#include "qruov.h"
#include "qruov_common.h"
#include "rng.h"
#include "util.h"
#include "emi_transform_scalar.h"

#include "linsys_round2_ref.h"

#if defined(__has_include)
#if __has_include("helpers.h")
#include "helpers.h"
#define QRUOV_HAS_AVX2_HELPERS 1
#endif
#endif

#ifdef QRUOV_HAS_EMI_TRANSFORM
#include "emi_transform.h"
extern const int MAT_EVAL[];
extern const int MAT_INTERP[];
extern const int MAT_REEVAL[];
#endif

#if P3_COEFF_LEN > SIG_S_COEFF_LEN
#define FQ_MAX_COEFF_LEN P3_COEFF_LEN
#else
#define FQ_MAX_COEFF_LEN SIG_S_COEFF_LEN
#endif

#define LINSYS_COMPARE_TRIALS 100

static const int linsys_probe_ranks[] = {
    0, 1, 2, 3, 4, 5, 8,
    QRUOV_m - 2, QRUOV_m - 1, QRUOV_m,
};

static int expect_equal_bytes(const char *name, const uint8_t *got, const uint8_t *want, size_t size)
{
    for (size_t i = 0; i < size; i++) {
        if (got[i] != want[i]) {
            fprintf(stderr, "%s failed: byte %zu differs (got %02x, want %02x)\n",
                    name, i, got[i], want[i]);
            return 0;
        }
    }
    return 1;
}

static uint64_t splitmix64_next(uint64_t *state)
{
    uint64_t z = (*state += UINT64_C(0x9e3779b97f4a7c15));
    z = (z ^ (z >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    z = (z ^ (z >> 27)) * UINT64_C(0x94d049bb133111eb);
    return z ^ (z >> 31);
}

static int seed_rng_for_tests(void)
{
    uint64_t seed = 0;
    const char *seed_env = getenv("QRUOV_TEST_SEED");
    if (seed_env != NULL && seed_env[0] != '\0') {
        char *end = NULL;
        errno = 0;
        unsigned long long parsed = strtoull(seed_env, &end, 0);
        if (errno != 0 || end == NULL || *end != '\0') {
            fprintf(stderr, "invalid QRUOV_TEST_SEED: %s\n", seed_env);
            return 0;
        }
        seed = (uint64_t)parsed;
    } else {
        if (RAND_bytes((unsigned char *)&seed, (int)sizeof(seed)) != 1) {
            fprintf(stderr, "failed to generate QRUOV_TEST_SEED\n");
            return 0;
        }
    }

    printf("QRUOV_TEST_SEED=0x%016llx\n", (unsigned long long)seed);

    unsigned char entropy[48];
    uint64_t state = seed;
    for (size_t i = 0; i < sizeof(entropy) / 8; i++) {
        store_u64_be(&entropy[i * 8], splitmix64_next(&state));
    }
    randombytes_init(entropy, NULL, 256);
    return 1;
}

/* shake tests */

static int shake_reference_256(const uint8_t *input, size_t input_size, uint8_t *dst, size_t dst_size)
{
    int ok = 0;
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (ctx == NULL) return 0;
    if (EVP_DigestInit_ex2(ctx, EVP_shake256(), NULL) != 1) goto out;
    if (input_size > 0 && EVP_DigestUpdate(ctx, input, input_size) != 1) goto out;
    if (EVP_DigestFinalXOF(ctx, dst, dst_size) != 1) goto out;
    ok = 1;
out:
    EVP_MD_CTX_free(ctx);
    return ok;
}

static int test_shake_empty_known_vector(void)
{
    static const uint8_t expected[64] = {
        0x46, 0xb9, 0xdd, 0x2b, 0x0b, 0xa8, 0x8d, 0x13,
        0x23, 0x3b, 0x3f, 0xeb, 0x74, 0x3e, 0xeb, 0x24,
        0x3f, 0xcd, 0x52, 0xea, 0x62, 0xb8, 0x1b, 0x82,
        0xb5, 0x0c, 0x27, 0x64, 0x6e, 0xd5, 0x76, 0x2f,
        0xd7, 0x5d, 0xc4, 0xdd, 0xd8, 0xc0, 0xf2, 0x00,
        0xcb, 0x05, 0x01, 0x9d, 0x67, 0xb5, 0x92, 0xf6,
        0xfc, 0x82, 0x1c, 0x49, 0x47, 0x9a, 0xb4, 0x86,
        0x40, 0x29, 0x2e, 0xac, 0xb3, 0xb7, 0xc4, 0xbe
    };
    uint8_t actual[sizeof(expected)];
    shake256 ctx;
    shake256_init(&ctx);
    shake256_digestfinal(&ctx, actual, sizeof(actual));
    shake256_free(&ctx);
    return expect_equal_bytes("test_shake_empty_known_vector", actual, expected, sizeof(expected));
}

static int test_shake_digestfinal_matches_reference(void)
{
    static const uint8_t input[] = {'a', 'b', 'c'};
    uint8_t expected[96];
    uint8_t actual[96];
    shake256 ctx;
    if (!shake_reference_256(input, sizeof(input), expected, sizeof(expected))) {
        fprintf(stderr, "shake reference failed in digestfinal test\n");
        return 0;
    }
    shake256_init(&ctx);
    shake256_update(&ctx, input, sizeof(input));
    shake256_digestfinal(&ctx, actual, sizeof(actual));
    shake256_free(&ctx);
    return expect_equal_bytes("test_shake_digestfinal_matches_reference", actual, expected, sizeof(expected));
}

static int test_shake_squeeze_matches_reference(void)
{
    static const uint8_t input[] = {'a', 'b', 'c'};
    static const size_t chunks[] = {1, 17, 31, 64, 47};
    uint8_t expected[160];
    uint8_t actual[160];
    size_t offset = 0;
    shake256 ctx;
    if (!shake_reference_256(input, sizeof(input), expected, sizeof(expected))) {
        fprintf(stderr, "shake reference failed in squeeze test\n");
        return 0;
    }
    shake256_init(&ctx);
    shake256_update(&ctx, input, sizeof(input));
    for (size_t i = 0; i < sizeof(chunks) / sizeof(chunks[0]); i++) {
        shake256_squeeze(&ctx, actual + offset, chunks[i]);
        offset += chunks[i];
    }
    shake256_free(&ctx);
    return expect_equal_bytes("test_shake_squeeze_matches_reference", actual, expected, sizeof(expected));
}

static int run_shake_tests(void)
{
    int failures = 0;
    printf("shake_test: PRIM_NO_EVP_DIGEST_SQUEEZE=%d\n", (int)PRIM_NO_EVP_DIGEST_SQUEEZE);
    if (!test_shake_empty_known_vector()) failures++;
    if (!test_shake_digestfinal_matches_reference()) failures++;
    if (!test_shake_squeeze_matches_reference()) failures++;
    if (failures != 0) {
        fprintf(stderr, "shake_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("shake_test: all tests passed\n");
    return 0;
}

/* prg tests */

#if !PRG_IS_AES
static int prg_ref_shake128(const uint8_t seed[16], uint16_t index, uint8_t *out, size_t len)
{
    int ok = 0;
    uint8_t idx_be[2];
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (ctx == NULL) return 0;
    store_u16_be(idx_be, index);
    if (EVP_DigestInit_ex2(ctx, EVP_shake128(), NULL) != 1) goto out;
    if (EVP_DigestUpdate(ctx, seed, 16) != 1) goto out;
    if (EVP_DigestUpdate(ctx, idx_be, sizeof(idx_be)) != 1) goto out;
    if (EVP_DigestFinalXOF(ctx, out, len) != 1) goto out;
    ok = 1;
out:
    EVP_MD_CTX_free(ctx);
    return ok;
}
#endif

#if PRG_IS_AES
static int prg_ref_aes128ctr(const uint8_t seed[16], uint16_t index, uint8_t *out, size_t len)
{
    int ok = 0;
    int out_len = 0;
    uint8_t nonce[8];
    uint8_t ctr_iv[16] = {0};
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL) return 0;
    if (len > (size_t)INT_MAX) goto out;
    store_u64_be(nonce, (uint64_t)index);
    memcpy(ctr_iv, nonce, 8);
    if (EVP_EncryptInit_ex2(ctx, EVP_aes_128_ctr(), seed, ctr_iv, NULL) != 1) goto out;
    memset(out, 0, len);
    if (EVP_EncryptUpdate(ctx, out, &out_len, out, (int)len) != 1) goto out;
    if (out_len != (int)len) goto out;
    ok = 1;
out:
    EVP_CIPHER_CTX_free(ctx);
    return ok;
}
#endif

static int test_prg_matches_reference(void)
{
    static const uint16_t indices[] = {0, 1, 42, 257, 65535};
    uint8_t seed[16];
    uint8_t got[96];
    uint8_t want[96];
    prg ctx;

    for (size_t i = 0; i < sizeof(seed); i++) seed[i] = (uint8_t)i;
    prg_init(&ctx, seed);
    for (size_t i = 0; i < sizeof(indices) / sizeof(indices[0]); i++) {
        prg_yield(&ctx, got, indices[i], sizeof(got));
#if PRG_IS_AES
        if (!prg_ref_aes128ctr(seed, indices[i], want, sizeof(want))) {
#else
        if (!prg_ref_shake128(seed, indices[i], want, sizeof(want))) {
#endif
            prg_free(&ctx);
            return 0;
        }
        if (!expect_equal_bytes("test_prg_matches_reference", got, want, sizeof(got))) {
            prg_free(&ctx);
            return 0;
        }
    }
    prg_free(&ctx);
    return 1;
}

static int test_prg_repeat_same_index(void)
{
    uint8_t seed[16];
    uint8_t out1[80];
    uint8_t out2[80];
    prg ctx;
    for (size_t i = 0; i < sizeof(seed); i++) seed[i] = (uint8_t)(0xa0 + i);
    prg_init(&ctx, seed);
    prg_yield(&ctx, out1, 1234, sizeof(out1));
    prg_yield(&ctx, out2, 1234, sizeof(out2));
    prg_free(&ctx);
    return expect_equal_bytes("test_prg_repeat_same_index", out1, out2, sizeof(out1));
}

static int run_prg_tests(void)
{
    int failures = 0;
    printf("prg_test: PRG_IS_AES=%d\n", (int)PRG_IS_AES);
    if (!test_prg_matches_reference()) failures++;
    if (!test_prg_repeat_same_index()) failures++;
    if (failures != 0) {
        fprintf(stderr, "prg_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("prg_test: all tests passed\n");
    return 0;
}

/* fq pack tests */

static size_t fq_packed_len(size_t n)
{
    return BITS2BYTE(QRUOV_q_LOG * n);
}

static unsigned fq_used_bits_last_byte(size_t n)
{
    return (unsigned)((QRUOV_q_LOG * n) & 7u);
}

static void fq_set_packed_coeff(uint8_t *packed, size_t idx, uint8_t value)
{
    size_t bitpos = idx * QRUOV_q_LOG;
    for (unsigned b = 0; b < QRUOV_q_LOG; b++) {
        size_t pos = bitpos + b;
        uint8_t mask = (uint8_t)(1u << (pos & 7));
        if (((value >> b) & 1u) != 0) {
            packed[pos >> 3] |= mask;
        } else {
            packed[pos >> 3] &= (uint8_t)~mask;
        }
    }
}

static uint8_t fq_get_packed_coeff(const uint8_t *packed, size_t idx)
{
    uint8_t value = 0;
    size_t bitpos = idx * QRUOV_q_LOG;
    for (unsigned b = 0; b < QRUOV_q_LOG; b++) {
        size_t pos = bitpos + b;
        if ((packed[pos >> 3] & (uint8_t)(1u << (pos & 7))) != 0) {
            value |= (uint8_t)(1u << b);
        }
    }
    return value;
}

static void fq_ref_store(uint8_t *dst, const uint8_t *src, size_t n)
{
    size_t bitpos = 0;
    memset(dst, 0, fq_packed_len(n));
    for (size_t i = 0; i < n; i++) {
        uint8_t v = src[i];
        for (unsigned b = 0; b < QRUOV_q_LOG; b++) {
            if (((v >> b) & 1u) != 0) dst[bitpos >> 3] |= (uint8_t)(1u << (bitpos & 7));
            bitpos++;
        }
    }
}

static void fq_ref_load(uint8_t *dst, const uint8_t *src, size_t n)
{
    size_t bitpos = 0;
    for (size_t i = 0; i < n; i++) {
        uint8_t v = 0;
        for (unsigned b = 0; b < QRUOV_q_LOG; b++) {
            v |= (uint8_t)(((src[bitpos >> 3] >> (bitpos & 7)) & 1u) << b);
            bitpos++;
        }
        dst[i] = v;
    }
}

static void fastop_ref_rejection_sample(uint8_t *dst, int tau, int length)
{
    for (int i = 0; i < tau; i++) {
        dst[i] &= QRUOV_q;
    }
    const uint8_t *aux = dst + length;
    const uint8_t *aux_end = dst + tau;
    while (aux < aux_end && *aux == QRUOV_q) aux++;
    for (int i = 0; i < length; i++) {
        if (*dst == QRUOV_q) {
            if (aux < aux_end) {
                *dst = *aux++;
                while (aux < aux_end && *aux == QRUOV_q) aux++;
            } else {
                *dst = 0;
            }
        }
        dst++;
    }
}

static uint8_t fastop_ref_rejection_dotprod(unsigned int length, unsigned int tau,
                                            uint8_t *src, const uint8_t *vec)
{
    uint32_t sum = 0;
    fastop_ref_rejection_sample(src, (int)tau, (int)length);
    for (unsigned int i = 0; i < length; i++) {
        sum += (uint32_t)src[i] * vec[i];
    }
    return gf_reduce(sum);
}

static uint8_t fastop_ref_dotprod(unsigned int length, const uint8_t *a, const uint8_t *b)
{
    uint32_t sum = 0;
    for (unsigned int i = 0; i < length; i++) {
        sum += (uint32_t)a[i] * b[i];
    }
    return gf_reduce(sum);
}

static void fastop_ref_row_elim(uint8_t *dst, const uint8_t *pivot, uint8_t m_mul, int len)
{
    for (int t = 0; t < len; t++) {
        dst[t] = (uint8_t)(((uint32_t)dst[t] + (uint32_t)m_mul * pivot[t]) % QRUOV_q);
    }
}

static void fastop_fill_rejsamp_input(uint8_t *src, int tau, int length)
{
    for (int i = 0; i < length; i++) {
        if ((i % 4) == 0) {
            src[i] = 0xff;
        } else {
            src[i] = (uint8_t)((11u * (unsigned)i + 3u) % QRUOV_q);
        }
    }
    for (int i = length; i < tau; i++) {
        if (((i - length) % 5) == 0) {
            src[i] = 0xff;
        } else {
            src[i] = (uint8_t)((7u * (unsigned)i + 1u) % QRUOV_q);
        }
    }
}

static int test_fastop_store_matches_reference(size_t n)
{
    uint8_t src[FQ_MAX_COEFF_LEN];
    uint8_t got[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    uint8_t want[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    for (size_t i = 0; i < n; i++) src[i] = (uint8_t)((29u * i + 9u) % QRUOV_q);
    memset(got, 0, fq_packed_len(n));
    fastop_store_fq(got, src, n);
    fq_ref_store(want, src, n);
    return expect_equal_bytes("test_fastop_store_matches_reference", got, want, fq_packed_len(n));
}

static int test_fastop_load_matches_reference(size_t n)
{
    uint8_t src[FQ_MAX_COEFF_LEN] = {0};
    uint8_t packed[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    uint8_t got[FQ_MAX_COEFF_LEN];
    uint8_t want[FQ_MAX_COEFF_LEN];
    for (size_t i = 0; i < n; i++) src[i] = (uint8_t)((23u * i + 5u) % QRUOV_q);
    fq_ref_store(packed, src, n);
    fastop_load_fq(got, packed, n);
    fq_ref_load(want, packed, n);
    return expect_equal_bytes("test_fastop_load_matches_reference", got, want, n);
}

static int test_fastop_rejection_sample_matches_reference(void)
{
    enum { FASTOP_TEST_TAU = 80, FASTOP_TEST_LEN = 48 };
    uint8_t got[FASTOP_TEST_TAU];
    uint8_t want[FASTOP_TEST_TAU];

    fastop_fill_rejsamp_input(got, FASTOP_TEST_TAU, FASTOP_TEST_LEN);
    memcpy(want, got, sizeof(want));
    fastop_rejection_sample(got, FASTOP_TEST_TAU, FASTOP_TEST_LEN);
    fastop_ref_rejection_sample(want, FASTOP_TEST_TAU, FASTOP_TEST_LEN);
    return expect_equal_bytes("test_fastop_rejection_sample_matches_reference",
                              got, want, FASTOP_TEST_LEN);
}

static int test_fastop_rejection_dotprod_matches_reference(void)
{
    enum { FASTOP_TEST_TAU = 80, FASTOP_TEST_LEN = 48 };
    uint8_t src_got[FASTOP_TEST_TAU];
    uint8_t src_want[FASTOP_TEST_TAU];
    uint8_t vec[FASTOP_TEST_LEN];
    uint8_t got;
    uint8_t want;

    fastop_fill_rejsamp_input(src_got, FASTOP_TEST_TAU, FASTOP_TEST_LEN);
    memcpy(src_want, src_got, sizeof(src_want));
    for (int i = 0; i < FASTOP_TEST_LEN; i++) {
        vec[i] = (uint8_t)((13u * (unsigned)i + 2u) % QRUOV_q);
    }

    got = fastop_rejection_dotprod(FASTOP_TEST_LEN, FASTOP_TEST_TAU, src_got, vec);
    want = fastop_ref_rejection_dotprod(FASTOP_TEST_LEN, FASTOP_TEST_TAU, src_want, vec);
    if (got != want) {
        fprintf(stderr, "test_fastop_rejection_dotprod_matches_reference failed: got %u, want %u\n",
                got, want);
        return 0;
    }
    return 1;
}

static int test_fastop_dotprod_matches_reference(void)
{
    static const unsigned int lengths[] = {0, 1, 7, 16, 17, 31, 32, 33, 63, 64, QRUOV_m};
    uint8_t a[QRUOV_m + 64];
    uint8_t b[QRUOV_m + 64];

    for (size_t t = 0; t < sizeof(lengths) / sizeof(lengths[0]); t++) {
        unsigned int len = lengths[t];
        for (unsigned int i = 0; i < len; i++) {
            a[i] = (uint8_t)((17u * i + 3u) % QRUOV_q);
            b[i] = (uint8_t)((29u * i + 5u) % QRUOV_q);
        }
        uint8_t got = fastop_dotprod(len, a, b);
        uint8_t want = fastop_ref_dotprod(len, a, b);
        if (got != want) {
            fprintf(stderr,
                    "test_fastop_dotprod_matches_reference failed at len=%u: got %u, want %u\n",
                    len, got, want);
            return 0;
        }
    }

    return 1;
}

static int test_fastop_rejection_all_rejected_zero_fill(void)
{
    enum { TAIL_TEST_TAU = 64, TAIL_TEST_LEN = 40, TAIL_TEST_EXTRA = 64, TAIL_TEST_BUF_LEN = TAIL_TEST_TAU + TAIL_TEST_EXTRA };
    uint8_t buf[TAIL_TEST_BUF_LEN];
    uint8_t expected[TAIL_TEST_LEN];

    memset(buf, 0xff, TAIL_TEST_TAU);
    memset(buf + TAIL_TEST_TAU, 1, TAIL_TEST_EXTRA);
    memset(expected, 0, sizeof(expected));

    fastop_rejection_sample(buf, TAIL_TEST_TAU, TAIL_TEST_LEN);
    return expect_equal_bytes("test_fastop_rejection_all_rejected_zero_fill",
                              buf, expected, sizeof(expected));
}

static int test_fastop_rejection_dotprod_all_rejected_zero_fill(void)
{
    enum { TAIL_TEST_TAU = 64, TAIL_TEST_LEN = 40, TAIL_TEST_EXTRA = 64, TAIL_TEST_BUF_LEN = TAIL_TEST_TAU + TAIL_TEST_EXTRA };
    uint8_t buf[TAIL_TEST_BUF_LEN];
    uint8_t vec[TAIL_TEST_LEN];
    const uint8_t want = 0;

    memset(buf, 0xff, TAIL_TEST_TAU);
    memset(buf + TAIL_TEST_TAU, 1, TAIL_TEST_EXTRA);
    for (int i = 0; i < TAIL_TEST_LEN; i++) {
        vec[i] = (uint8_t)(((5 * i) % (QRUOV_q - 1)) + 1);
    }

    const uint8_t got = fastop_rejection_dotprod(TAIL_TEST_LEN, TAIL_TEST_TAU, buf, vec);
    if (got != want) {
        fprintf(stderr, "test_fastop_rejection_dotprod_all_rejected_zero_fill failed: got %u, want %u\n",
                got, want);
        return 0;
    }
    return 1;
}

static int test_fastop_rejection_dotprod_partial_tail_then_zero_fill(void)
{
    enum { TAIL_TEST_TAU = 64, TAIL_TEST_LEN = 40, TAIL_TEST_EXTRA = 64, TAIL_TEST_BUF_LEN = TAIL_TEST_TAU + TAIL_TEST_EXTRA };
    static const int rejected[] = {0, 4, 7, 18, 27, 31, 32, 37, 39};
    static const uint8_t repl[] = {6, 5, 4};
    uint8_t buf[TAIL_TEST_BUF_LEN];
    uint8_t repaired[TAIL_TEST_LEN];
    uint8_t vec[TAIL_TEST_LEN];
    uint32_t sum = 0;

    for (int i = 0; i < TAIL_TEST_LEN; i++) {
        uint8_t v = (uint8_t)(((2 * i) % (QRUOV_q - 1)) + 1);
        buf[i] = v;
        repaired[i] = v;
        vec[i] = (uint8_t)(((5 * i) % (QRUOV_q - 1)) + 1);
    }
    for (size_t i = 0; i < sizeof(rejected) / sizeof(rejected[0]); i++) {
        buf[rejected[i]] = 0xff;
        repaired[rejected[i]] = (i < sizeof(repl)) ? repl[i] : 0;
    }
    for (size_t i = 0; i < sizeof(repl); i++) {
        buf[TAIL_TEST_LEN + (int)i] = repl[i];
    }
    for (int i = TAIL_TEST_LEN + (int)sizeof(repl); i < TAIL_TEST_TAU; i++) {
        buf[i] = 0xff;
    }
    for (int i = TAIL_TEST_TAU; i < TAIL_TEST_BUF_LEN; i++) {
        buf[i] = 1;
    }
    for (int i = 0; i < TAIL_TEST_LEN; i++) {
        sum += (uint32_t)repaired[i] * vec[i];
    }

    const uint8_t want = gf_reduce(sum);
    const uint8_t got = fastop_rejection_dotprod(TAIL_TEST_LEN, TAIL_TEST_TAU, buf, vec);
    if (got != want) {
        fprintf(stderr,
                "test_fastop_rejection_dotprod_partial_tail_then_zero_fill failed: got %u, want %u\n",
                got, want);
        return 0;
    }
    return 1;
}

static int test_fastop_rejection_sample_partial_tail_then_zero_fill(void)
{
    enum { TAIL_TEST_TAU = 64, TAIL_TEST_LEN = 40, TAIL_TEST_EXTRA = 64, TAIL_TEST_BUF_LEN = TAIL_TEST_TAU + TAIL_TEST_EXTRA };
    static const int rejected[] = {0, 4, 7, 18, 27, 31, 32, 37, 39};
    static const uint8_t repl[] = {6, 5, 4};
    uint8_t buf[TAIL_TEST_BUF_LEN];
    uint8_t expected[TAIL_TEST_LEN];

    for (int i = 0; i < TAIL_TEST_LEN; i++) {
        uint8_t v = (uint8_t)(((2 * i) % (QRUOV_q - 1)) + 1);
        buf[i] = v;
        expected[i] = v;
    }
    for (size_t i = 0; i < sizeof(rejected) / sizeof(rejected[0]); i++) {
        buf[rejected[i]] = 0xff;
        expected[rejected[i]] = (i < sizeof(repl)) ? repl[i] : 0;
    }
    for (size_t i = 0; i < sizeof(repl); i++) {
        buf[TAIL_TEST_LEN + (int)i] = repl[i];
    }
    for (int i = TAIL_TEST_LEN + (int)sizeof(repl); i < TAIL_TEST_TAU; i++) {
        buf[i] = 0xff;
    }
    for (int i = TAIL_TEST_TAU; i < TAIL_TEST_BUF_LEN; i++) {
        buf[i] = 1;
    }

    fastop_rejection_sample(buf, TAIL_TEST_TAU, TAIL_TEST_LEN);
    return expect_equal_bytes("test_fastop_rejection_sample_partial_tail_then_zero_fill",
                              buf, expected, sizeof(expected));
}

static int test_fastop_row_elim_matches_reference(void)
{
    enum { FASTOP_TEST_LEN = 47 };
    uint8_t dst_got[FASTOP_TEST_LEN];
    uint8_t dst_want[FASTOP_TEST_LEN];
    uint8_t pivot[FASTOP_TEST_LEN];
    const uint8_t m_mul = (uint8_t)(QRUOV_q > 1 ? QRUOV_q - 1 : 0);

    for (int i = 0; i < FASTOP_TEST_LEN; i++) {
        dst_got[i] = (uint8_t)((5u * (unsigned)i + 1u) % QRUOV_q);
        pivot[i] = (uint8_t)((9u * (unsigned)i + 4u) % QRUOV_q);
    }
    memcpy(dst_want, dst_got, sizeof(dst_want));
    fastop_row_elim(dst_got, pivot, m_mul, FASTOP_TEST_LEN);
    fastop_ref_row_elim(dst_want, pivot, m_mul, FASTOP_TEST_LEN);
    return expect_equal_bytes("test_fastop_row_elim_matches_reference",
                              dst_got, dst_want, sizeof(dst_got));
}

static int run_fastop_tests(void)
{
    static const size_t sizes[] = {1, 2, 3, 7, 8, 9, 17, P3_COEFF_LEN, SIG_S_COEFF_LEN};
    int failures = 0;

    for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
        if (!test_fastop_store_matches_reference(sizes[i])) failures++;
        if (!test_fastop_load_matches_reference(sizes[i])) failures++;
    }
    if (!test_fastop_rejection_sample_matches_reference()) failures++;
    if (!test_fastop_rejection_dotprod_matches_reference()) failures++;
    if (!test_fastop_dotprod_matches_reference()) failures++;
    if (!test_fastop_rejection_all_rejected_zero_fill()) failures++;
    if (!test_fastop_rejection_dotprod_all_rejected_zero_fill()) failures++;
    if (!test_fastop_rejection_sample_partial_tail_then_zero_fill()) failures++;
    if (!test_fastop_rejection_dotprod_partial_tail_then_zero_fill()) failures++;
    if (!test_fastop_row_elim_matches_reference()) failures++;
    if (failures != 0) {
        fprintf(stderr, "fastop_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("fastop_test: all tests passed\n");
    return 0;
}

static int find_active_p3_coeff(const uint8_t *oil, size_t *idx_out)
{
    size_t idx = 0;
    for (int i = 0; i < QRUOV_M; i++) {
        for (int j = i; j < QRUOV_M; j++) {
            uint8_t prod[QRUOV_L];
            uint8_t perm[QRUOV_L];
            fql_mul(prod, &oil[i * QRUOV_L], &oil[j * QRUOV_L]);
            if (i != j) {
                fql_add(prod, prod, prod);
            }
            fql_perm(perm, prod);
            for (int l = 0; l < QRUOV_L; l++) {
                if (perm[l] != 0) {
                    *idx_out = idx + (size_t)l;
                    return 1;
                }
            }
            idx += QRUOV_L;
        }
    }
    return 0;
}

static void fill_test_message(uint8_t *msg, size_t msg_len)
{
    for (size_t i = 0; i < msg_len; i++) {
        msg[i] = (uint8_t)((msg_len + 17u * i) & 0xffu);
    }
}

static int test_fq_store_matches_reference(size_t n)
{
    uint8_t src[FQ_MAX_COEFF_LEN];
    uint8_t got[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    uint8_t want[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    for (size_t i = 0; i < n; i++) src[i] = (uint8_t)((37u * i + 13u) % QRUOV_q);
    memset(got, 0, fq_packed_len(n));
    store_fq(got, src, n);
    fq_ref_store(want, src, n);
    return expect_equal_bytes("test_fq_store_matches_reference", got, want, fq_packed_len(n));
}

static int test_fq_load_matches_reference(size_t n)
{
    uint8_t src[FQ_MAX_COEFF_LEN] = {0};
    uint8_t packed[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    uint8_t got[FQ_MAX_COEFF_LEN];
    uint8_t want[FQ_MAX_COEFF_LEN];
    for (size_t i = 0; i < n; i++) src[i] = (uint8_t)((19u * i + 7u) % QRUOV_q);
    fq_ref_store(packed, src, n);
    load_fq(got, packed, n);
    fq_ref_load(want, packed, n);
    return expect_equal_bytes("test_fq_load_matches_reference", got, want, n);
}

static int test_fq_roundtrip(size_t n)
{
    uint8_t src[FQ_MAX_COEFF_LEN];
    uint8_t packed[BITS2BYTE(QRUOV_q_LOG * FQ_MAX_COEFF_LEN)];
    uint8_t out[FQ_MAX_COEFF_LEN];
    for (size_t i = 0; i < n; i++) src[i] = (uint8_t)((11u * i + 5u) % QRUOV_q);
    memset(packed, 0, fq_packed_len(n));
    store_fq(packed, src, n);
    load_fq(out, packed, n);
    return expect_equal_bytes("test_fq_roundtrip", out, src, n);
}

#ifdef QRUOV_HAS_AVX2_HELPERS
static uint8_t fq_naive_worst_case_dot(int len)
{
    return (uint64_t)(QRUOV_q - 1) * (QRUOV_q - 1) * len % QRUOV_q;
}

static int test_fq_eval_vnni_max_matmul_matches_naive(void)
{
    int ok = 0;
    enum { M = QRUOV_M, N = QRUOV_M, K = ROUND_UP4(QRUOV_V) };
    const size_t a_size = (size_t)QRUOV_LL * (size_t)M * (size_t)K;
    const size_t b_size = (size_t)QRUOV_LL * (size_t)K * (size_t)N;
    const size_t c_size = (size_t)QRUOV_LL * (size_t)M * (size_t)N;
    uint8_t *A = malloc(a_size);
    uint8_t *Bvnni = malloc(b_size);
    uint8_t *got = malloc(c_size);
    const uint8_t want = fq_naive_worst_case_dot(K);

    if (A == NULL || Bvnni == NULL || got == NULL) {
        fprintf(stderr, "test_fq_eval_vnni_max_matmul_matches_naive: allocation failed\n");
        goto cleanup;
    }

    memset(A, QRUOV_q - 1, a_size);
    memset(Bvnni, QRUOV_q - 1, b_size);
    memset(got, 0, c_size);
    fql_matmul_eval_vnni_fast(got, A, Bvnni, M, N, K);

    for (int l = 0; l < QRUOV_LL; l++) {
        for (int i = 0; i < M; i++) {
            for (int j = 0; j < N; j++) {
                uint8_t got_v = got[l * M * N + i * N + j];
                if (got_v != want) {
                    fprintf(stderr,
                            "test_fq_eval_vnni_max_matmul_matches_naive failed: "
                            "entry (%d, %d, %d) differs (got %u, want %u)\n",
                            l, i, j, got_v, want);
                    goto cleanup;
                }
            }
        }
    }

    ok = 1;

cleanup:
    free(A);
    free(Bvnni);
    free(got);
    return ok;
}

static int test_fql_vnni_max_matmul_matches_naive_shape(const char *name, int n, int k)
{
    int ok = 0;
    const size_t a_size = (size_t)QRUOV_L * (size_t)k;
    const size_t b_size = (size_t)QRUOV_L * (size_t)k * (size_t)n;
    const size_t c_size = (size_t)QRUOV_L * (size_t)n;
    const size_t vec_size = (size_t)k * (size_t)QRUOV_L;
    uint8_t *A = malloc(a_size);
    uint8_t *Bvnni = malloc(b_size);
    uint8_t *got = malloc(c_size);
    uint8_t *lhs = malloc(vec_size);
    uint8_t *rhs = malloc(vec_size);
    uint8_t want[QRUOV_L];

    if (A == NULL || Bvnni == NULL || got == NULL || lhs == NULL || rhs == NULL) {
        fprintf(stderr, "%s: allocation failed\n", name);
        goto cleanup;
    }

    memset(A, QRUOV_q - 1, a_size);
    memset(Bvnni, QRUOV_q - 1, b_size);
    memset(got, 0, c_size);
    memset(lhs, QRUOV_q - 1, vec_size);
    memset(rhs, QRUOV_q - 1, vec_size);
    fql_dot(want, lhs, rhs, k);
    /* Current AVX2 callers only use fql_matmul_vnni_fast with M = 1. */
    fql_matmul_vnni_fast(got, A, Bvnni, 1, n, k);

    for (int l = 0; l < QRUOV_L; l++) {
        for (int j = 0; j < n; j++) {
            uint8_t got_v = got[l * n + j];
            if (got_v != want[l]) {
                fprintf(stderr, "%s failed: entry (%d, %d) differs (got %u, want %u)\n",
                        name, l, j, got_v, want[l]);
                goto cleanup;
            }
        }
    }

    ok = 1;

cleanup:
    free(A);
    free(Bvnni);
    free(got);
    free(lhs);
    free(rhs);
    return ok;
}

static int test_fql_vnni_max_matmul_v4_matches_naive(void)
{
    enum { V4 = ROUND_UP4(QRUOV_V) };
    return test_fql_vnni_max_matmul_matches_naive_shape(
            "test_fql_vnni_max_matmul_v4_matches_naive", V4, V4);
}

static int test_fql_vnni_max_matmul_m_matches_naive(void)
{
    enum { V4 = ROUND_UP4(QRUOV_V) };
    return test_fql_vnni_max_matmul_matches_naive_shape(
            "test_fql_vnni_max_matmul_m_matches_naive", QRUOV_M, V4);
}
#endif

static int run_fq_tests(void)
{
    static const size_t sizes[] = {1, 2, 3, 7, 8, 9, 17, P3_COEFF_LEN, SIG_S_COEFF_LEN};
    int failures = 0;
    for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
        if (!test_fq_store_matches_reference(sizes[i])) failures++;
        if (!test_fq_load_matches_reference(sizes[i])) failures++;
        if (!test_fq_roundtrip(sizes[i])) failures++;
    }
#ifdef QRUOV_HAS_AVX2_HELPERS
    if (!test_fq_eval_vnni_max_matmul_matches_naive()) failures++;
    if (!test_fql_vnni_max_matmul_v4_matches_naive()) failures++;
    if (!test_fql_vnni_max_matmul_m_matches_naive()) failures++;
#endif
    if (failures != 0) {
        fprintf(stderr, "fq_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("fq_test: all tests passed\n");
    return 0;
}

#ifdef QRUOV_HAS_EMI_TRANSFORM
#ifdef QRUOV_HAS_AVX2_HELPERS
#define EMI_TEST_SIZES 32, 33, 97
#define EMI_TRIPLE_PRODUCT_SIZES 32, 64
#else
#define EMI_TEST_SIZES 1, 2, 3, 15, 16, 17, 31, 32, 33, 97
#define EMI_TRIPLE_PRODUCT_SIZES 1, 17, 32, 64
#endif

static void fq_rand_values(uint8_t *buffer, size_t size);
static void emi_ref_evaluate(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{
    emi_transform_apply_scalar(output, plane_out, input, plane_in, size, MAT_EVAL, QRUOV_LL, QRUOV_L);
}

static void emi_ref_reevaluate(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{
    emi_transform_apply_scalar(output, plane_out, input, plane_in, size, MAT_REEVAL, QRUOV_LL, QRUOV_LL);
}

static void emi_ref_interpolate(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{
    emi_transform_apply_scalar(output, plane_out, input, plane_in, size, MAT_INTERP, QRUOV_L, QRUOV_LL);
}

static int emi_expect_equal_plane_major(const char *name, const uint8_t *got, int got_plane,
                                        const uint8_t *want, int want_plane, int rows, int size)
{
    for (int row = 0; row < rows; row++) {
        for (int i = 0; i < size; i++) {
            uint8_t got_v = got[row * got_plane + i];
            uint8_t want_v = want[row * want_plane + i];
            if (got_v != want_v) {
                fprintf(stderr,
                        "%s failed: entry (%d, %d) differs (got %u, want %u)\n",
                        name, row, i, got_v, want_v);
                return 0;
            }
        }
    }
    return 1;
}

static void emi_fill_random_plane_major(uint8_t *dst, int rows, int plane, int size)
{
    memset(dst, 0, (size_t)rows * (size_t)plane);
    for (int row = 0; row < rows; row++) {
        fq_rand_values(&dst[row * plane], (size_t)size);
    }
}

static void emi_fill_constant_plane_major(uint8_t *dst, int rows, int plane, int size, uint8_t value)
{
    memset(dst, 0, (size_t)rows * (size_t)plane);
    for (int row = 0; row < rows; row++) {
        memset(&dst[row * plane], value, (size_t)size);
    }
}

static void ln_get_fql(uint8_t dst[QRUOV_L], const uint8_t *src, int plane, int idx)
{
    for (int l = 0; l < QRUOV_L; l++) {
        dst[l] = src[l * plane + idx];
    }
}

static void emi_pointwise_mul(uint8_t *dst, int plane_out, const uint8_t *a, int plane_a,
                              const uint8_t *b, int plane_b, int size)
{
    for (int l = 0; l < QRUOV_LL; l++) {
        for (int i = 0; i < size; i++) {
            dst[l * plane_out + i] = gf_mul(a[l * plane_a + i], b[l * plane_b + i]);
        }
    }
}

static int test_emi_evaluate_matches_reference(void)
{
    static const int sizes[] = {EMI_TEST_SIZES};

    for (size_t s = 0; s < sizeof(sizes) / sizeof(sizes[0]); s++) {
        int ok = 0;
        int size = sizes[s];
        int plane_in = size + 7;
        int plane_eval = size + 11;
        size_t in_size = (size_t)QRUOV_L * (size_t)plane_in;
        size_t eval_size = (size_t)QRUOV_LL * (size_t)plane_eval;
        uint8_t *input = malloc(in_size);
        uint8_t *got = malloc(eval_size);
        uint8_t *want = malloc(eval_size);
        if (input == NULL || got == NULL || want == NULL) {
            fprintf(stderr, "test_emi_evaluate_matches_reference: allocation failed at size %d\n", size);
            goto cleanup;
        }

        emi_fill_random_plane_major(input, QRUOV_L, plane_in, size);
        memset(got, 0, eval_size);
        memset(want, 0, eval_size);
        evaluate(got, plane_eval, input, plane_in, size);
        emi_ref_evaluate(want, plane_eval, input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_evaluate_matches_reference",
                                          got, plane_eval, want, plane_eval, QRUOV_LL, size)) {
            goto cleanup;
        }

        ok = 1;

cleanup:
        free(input);
        free(got);
        free(want);

        if (!ok) return 0;
    }

    return 1;
}

static int test_emi_reevaluate_matches_reference(void)
{
    static const int sizes[] = {EMI_TEST_SIZES};

    for (size_t s = 0; s < sizeof(sizes) / sizeof(sizes[0]); s++) {
        int ok = 0;
        int size = sizes[s];
        int plane_in = size + 7;
        int plane_out = size + 11;
        size_t in_size = (size_t)QRUOV_LL * (size_t)plane_in;
        size_t out_size = (size_t)QRUOV_LL * (size_t)plane_out;
        uint8_t *input = malloc(in_size);
        uint8_t *got = malloc(out_size);
        uint8_t *want = malloc(out_size);
        if (input == NULL || got == NULL || want == NULL) {
            fprintf(stderr, "test_emi_reevaluate_matches_reference: allocation failed at size %d\n", size);
            goto cleanup;
        }

        emi_fill_random_plane_major(input, QRUOV_LL, plane_in, size);
        memset(got, 0, out_size);
        memset(want, 0, out_size);
        reevaluate(got, plane_out, input, plane_in, size);
        emi_ref_reevaluate(want, plane_out, input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_reevaluate_matches_reference",
                                          got, plane_out, want, plane_out, QRUOV_LL, size)) {
            goto cleanup;
        }

        ok = 1;

cleanup:
        free(input);
        free(got);
        free(want);

        if (!ok) return 0;
    }

    return 1;
}

static int test_emi_interpolate_matches_reference(void)
{
    static const int sizes[] = {EMI_TEST_SIZES};

    for (size_t s = 0; s < sizeof(sizes) / sizeof(sizes[0]); s++) {
        int ok = 0;
        int size = sizes[s];
        int plane_in = size + 7;
        int plane_out = size + 11;
        size_t in_size = (size_t)QRUOV_LL * (size_t)plane_in;
        size_t out_size = (size_t)QRUOV_L * (size_t)plane_out;
        uint8_t *input = malloc(in_size);
        uint8_t *got = malloc(out_size);
        uint8_t *want = malloc(out_size);
        if (input == NULL || got == NULL || want == NULL) {
            fprintf(stderr, "test_emi_interpolate_matches_reference: allocation failed at size %d\n", size);
            goto cleanup;
        }

        emi_fill_random_plane_major(input, QRUOV_LL, plane_in, size);
        memset(got, 0, out_size);
        memset(want, 0, out_size);
        interpolate(got, plane_out, input, plane_in, size);
        emi_ref_interpolate(want, plane_out, input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_interpolate_matches_reference",
                                          got, plane_out, want, plane_out, QRUOV_L, size)) {
            goto cleanup;
        }

        ok = 1;

cleanup:
        free(input);
        free(got);
        free(want);

        if (!ok) return 0;
    }

    return 1;
}

static int test_emi_triple_product(void)
{
    static const int sizes[] = {EMI_TRIPLE_PRODUCT_SIZES};

    for (size_t s = 0; s < sizeof(sizes) / sizeof(sizes[0]); s++) {
        int ok = 0;
        int size = sizes[s];
        int plane_fql = size + 5;
        int plane_eval = size + 9;
        size_t fql_size = (size_t)QRUOV_L * (size_t)plane_fql;
        size_t eval_size = (size_t)QRUOV_LL * (size_t)plane_eval;
        uint8_t *a = malloc(fql_size);
        uint8_t *b = malloc(fql_size);
        uint8_t *c = malloc(fql_size);
        uint8_t *abc = malloc(fql_size);
        uint8_t *a_eval = malloc(eval_size);
        uint8_t *b_eval = malloc(eval_size);
        uint8_t *c_eval = malloc(eval_size);
        uint8_t *ab_eval = malloc(eval_size);
        uint8_t *ab_reval = malloc(eval_size);
        uint8_t *abc_eval = malloc(eval_size);
        if (a == NULL || b == NULL || c == NULL || abc == NULL ||
            a_eval == NULL || b_eval == NULL || c_eval == NULL ||
            ab_eval == NULL || ab_reval == NULL || abc_eval == NULL) {
            fprintf(stderr, "test_emi_triple_product: allocation failed at size %d\n", size);
            goto cleanup;
        }

        memset(a, 0, fql_size);
        memset(b, 0, fql_size);
        memset(c, 0, fql_size);
        memset(abc, 0, fql_size);
        memset(a_eval, 0, eval_size);
        memset(b_eval, 0, eval_size);
        memset(c_eval, 0, eval_size);
        memset(ab_eval, 0, eval_size);
        memset(ab_reval, 0, eval_size);
        memset(abc_eval, 0, eval_size);
        for (int l = 0; l < QRUOV_L; l++) {
            fq_rand_values(&a[l * plane_fql], (size_t)size);
            fq_rand_values(&b[l * plane_fql], (size_t)size);
            fq_rand_values(&c[l * plane_fql], (size_t)size);
        }

        evaluate(a_eval, plane_eval, a, plane_fql, size);
        evaluate(b_eval, plane_eval, b, plane_fql, size);
        evaluate(c_eval, plane_eval, c, plane_fql, size);
        emi_pointwise_mul(ab_eval, plane_eval, a_eval, plane_eval, b_eval, plane_eval, size);
        reevaluate(ab_reval, plane_eval, ab_eval, plane_eval, size);
        emi_pointwise_mul(abc_eval, plane_eval, ab_reval, plane_eval, c_eval, plane_eval, size);
        interpolate(abc, plane_fql, abc_eval, plane_eval, size);

        for (int i = 0; i < size; i++) {
            uint8_t av[QRUOV_L], bv[QRUOV_L], cv[QRUOV_L], abv[QRUOV_L], want[QRUOV_L];
            ln_get_fql(av, a, plane_fql, i);
            ln_get_fql(bv, b, plane_fql, i);
            ln_get_fql(cv, c, plane_fql, i);
            fql_mul(abv, av, bv);
            fql_mul(want, abv, cv);
            for (int l = 0; l < QRUOV_L; l++) {
                uint8_t got_v = abc[l * plane_fql + i];
                if (got_v != want[l]) {
                    fprintf(stderr,
                            "test_emi_triple_product failed: coeff (%d, %d) differs (got %u, want %u)\n",
                            l, i, got_v, want[l]);
                    goto cleanup;
                }
            }
        }

        ok = 1;

cleanup:
        free(a);
        free(b);
        free(c);
        free(abc);
        free(a_eval);
        free(b_eval);
        free(c_eval);
        free(ab_eval);
        free(ab_reval);
        free(abc_eval);

        if (!ok) return 0;
    }

    return 1;
}

static int test_emi_max_input_matches_reference(void)
{
    static const int sizes[] = {EMI_TEST_SIZES};

    for (size_t s = 0; s < sizeof(sizes) / sizeof(sizes[0]); s++) {
        int ok = 0;
        int size = sizes[s];
        int plane_in = size + 7;
        int plane_out = size + 11;
        size_t eval_in_size = (size_t)QRUOV_L * (size_t)plane_in;
        size_t eval_out_size = (size_t)QRUOV_LL * (size_t)plane_out;
        size_t reeval_in_size = (size_t)QRUOV_LL * (size_t)plane_in;
        size_t interp_out_size = (size_t)QRUOV_L * (size_t)plane_out;
        uint8_t *eval_input = malloc(eval_in_size);
        uint8_t *reeval_input = malloc(reeval_in_size);
        uint8_t *got = malloc(eval_out_size);
        uint8_t *want = malloc(eval_out_size);
        uint8_t *interp_got = malloc(interp_out_size);
        uint8_t *interp_want = malloc(interp_out_size);

        if (eval_input == NULL || reeval_input == NULL || got == NULL || want == NULL ||
            interp_got == NULL || interp_want == NULL) {
            fprintf(stderr, "test_emi_max_input_matches_reference: allocation failed at size %d\n", size);
            goto cleanup;
        }

        emi_fill_constant_plane_major(eval_input, QRUOV_L, plane_in, size, (uint8_t)(QRUOV_q - 1));
        memset(got, 0, eval_out_size);
        memset(want, 0, eval_out_size);
        evaluate(got, plane_out, eval_input, plane_in, size);
        emi_ref_evaluate(want, plane_out, eval_input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_max_input_matches_reference/evaluate",
                                          got, plane_out, want, plane_out, QRUOV_LL, size)) {
            goto cleanup;
        }

        emi_fill_constant_plane_major(reeval_input, QRUOV_LL, plane_in, size, (uint8_t)(QRUOV_q - 1));
        memset(got, 0, eval_out_size);
        memset(want, 0, eval_out_size);
        reevaluate(got, plane_out, reeval_input, plane_in, size);
        emi_ref_reevaluate(want, plane_out, reeval_input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_max_input_matches_reference/reevaluate",
                                          got, plane_out, want, plane_out, QRUOV_LL, size)) {
            goto cleanup;
        }

        memset(interp_got, 0, interp_out_size);
        memset(interp_want, 0, interp_out_size);
        interpolate(interp_got, plane_out, reeval_input, plane_in, size);
        emi_ref_interpolate(interp_want, plane_out, reeval_input, plane_in, size);
        if (!emi_expect_equal_plane_major("test_emi_max_input_matches_reference/interpolate",
                                          interp_got, plane_out, interp_want, plane_out, QRUOV_L, size)) {
            goto cleanup;
        }

        ok = 1;

cleanup:
        free(eval_input);
        free(reeval_input);
        free(got);
        free(want);
        free(interp_got);
        free(interp_want);

        if (!ok) return 0;
    }

    return 1;
}

static int run_emi_tests(void)
{
    int failures = 0;
    if (!test_emi_evaluate_matches_reference()) failures++;
    if (!test_emi_reevaluate_matches_reference()) failures++;
    if (!test_emi_interpolate_matches_reference()) failures++;
    if (!test_emi_triple_product()) failures++;
    if (!test_emi_max_input_matches_reference()) failures++;
    if (failures != 0) {
        fprintf(stderr, "emi_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("emi_test: all tests passed\n");
    return 0;
}

#undef EMI_TEST_SIZES
#undef EMI_TRIPLE_PRODUCT_SIZES
#endif

/* linsys tests */

static void fq_rand_values(uint8_t *buffer, size_t size)
{
    randombytes(buffer, (unsigned long long)size);
    for (size_t i = 0; i < size; i++) {
        buffer[i] %= QRUOV_q;
    }
}

static int fq_rank_ref(const uint8_t *mat, int rows, int cols)
{
    size_t size = (size_t)rows * (size_t)cols;
    uint8_t *tmp = malloc(size);
    if (tmp == NULL) return -1;
    memcpy(tmp, mat, size);

    int rank = 0;
    for (int col = 0; col < cols && rank < rows; col++) {
        int pivot = rank;
        while (pivot < rows && tmp[pivot * cols + col] == 0) {
            pivot++;
        }
        if (pivot == rows) continue;

        if (pivot != rank) {
            for (int k = col; k < cols; k++) {
                uint8_t t = tmp[rank * cols + k];
                tmp[rank * cols + k] = tmp[pivot * cols + k];
                tmp[pivot * cols + k] = t;
            }
        }

        uint8_t inv = gf_inv(tmp[rank * cols + col]);
        for (int k = col; k < cols; k++) {
            tmp[rank * cols + k] = gf_mul(tmp[rank * cols + k], inv);
        }
        for (int row = 0; row < rows; row++) {
            if (row == rank) continue;
            uint8_t factor = tmp[row * cols + col];
            if (factor == 0) continue;
            for (int k = col; k < cols; k++) {
                tmp[row * cols + k] = gf_sub(tmp[row * cols + k],
                                             gf_mul(factor, tmp[rank * cols + k]));
            }
        }
        rank++;
    }

    free(tmp);
    return rank;
}

static void fq_matvec_mul(uint8_t *dst, const uint8_t *mat, const uint8_t *vec, int dim)
{
    for (int i = 0; i < dim; i++) {
        uint32_t acc = 0;
        for (int j = 0; j < dim; j++) {
            acc += (uint32_t)mat[i * dim + j] * vec[j];
        }
        dst[i] = gf_reduce(acc);
    }
}

// Construct an exact-rank square matrix by zeroing random columns of a full-rank matrix.
static void fq_rand_mat_zerocol(uint8_t *mat, int dim, int rank)
{
    if (rank < 0 || rank > dim) {
        fprintf(stderr, "fq_rand_mat_zerocol: invalid rank %d for dimension %d\n", rank, dim);
        exit(1);
    }

    const int max_attempts = 128;
    for (int attempts = 0; attempts < max_attempts; attempts++) {
        fq_rand_values(mat, (size_t)dim * (size_t)dim);
        int mat_rank = fq_rank_ref(mat, dim, dim);
        if (mat_rank < 0) {
            fprintf(stderr, "fq_rand_mat_zerocol: rank reference allocation failed\n");
            exit(1);
        }
        if (mat_rank != dim) continue;

        if (rank == dim) return;

        int perm[QRUOV_m];
        for (int i = 0; i < dim; i++) perm[i] = i;
        for (int i = 0; i < dim - rank; i++) {
            uint32_t t = 0;
            randombytes((unsigned char *)&t, (unsigned long long)sizeof(t));
            t = (uint32_t)i + (t % (uint32_t)(dim - i));
            int tmp = perm[i];
            perm[i] = perm[t];
            perm[t] = tmp;
        }
        for (int i = 0; i < dim - rank; i++) {
            for (int row = 0; row < dim; row++) {
                mat[row * dim + perm[i]] = 0;
            }
        }
        return;
    }

    fprintf(stderr, "fq_rand_mat_zerocol: failed to generate full-rank %dx%d matrix\n", dim, dim);
    exit(1);
}

static int test_linsys_lu_rank_with_zero_columns(void)
{
    uint8_t eqn[QRUOV_m * QRUOV_m];
    uint8_t eqn_copy[QRUOV_m * QRUOV_m];
    linsys_echelon echelon;

    for (size_t i = 0; i < sizeof(linsys_probe_ranks) / sizeof(linsys_probe_ranks[0]); i++) {
        int rank = linsys_probe_ranks[i];
        if (rank < 0 || rank > QRUOV_m) continue;
        fq_rand_mat_zerocol(eqn, QRUOV_m, rank);
        memcpy(eqn_copy, eqn, sizeof(eqn));
        int ref_rank = fq_rank_ref(eqn_copy, QRUOV_m, QRUOV_m);
        if (ref_rank < 0) {
            fprintf(stderr, "test_linsys_lu_rank_with_zero_columns: rank reference allocation failed\n");
            return 0;
        }
        linsys_lu_decompose(eqn, &echelon);
        if (echelon.rank != ref_rank) {
            fprintf(stderr,
                    "test_linsys_lu_rank_with_zero_columns failed: expected rank %d, got %d\n",
                    ref_rank, echelon.rank);
            return 0;
        }
    }

    return 1;
}

static int test_linsys_consistency_with_zero_columns(void)
{
    uint8_t eqn[QRUOV_m * QRUOV_m];
    uint8_t eqn_copy[QRUOV_m * QRUOV_m];
    uint8_t x[QRUOV_m];
    uint8_t u[QRUOV_m];
    uint8_t b_consistent[QRUOV_m];
    uint8_t b_inconsistent[QRUOV_m];
    uint8_t t_consistent[QRUOV_m];
    uint8_t t_inconsistent[QRUOV_m];
    uint8_t consistency_rhs[QRUOV_m];
    linsys_echelon echelon;

    for (size_t i = 0; i < sizeof(linsys_probe_ranks) / sizeof(linsys_probe_ranks[0]); i++) {
        int rank = linsys_probe_ranks[i];
        if (rank < 0 || rank > QRUOV_m) continue;
        fq_rand_mat_zerocol(eqn, QRUOV_m, rank);
        fq_rand_values(x, sizeof(x));
        fq_rand_values(u, sizeof(u));
        memcpy(eqn_copy, eqn, sizeof(eqn));
        fq_matvec_mul(b_consistent, eqn_copy, x, QRUOV_m);
        for (int j = 0; j < QRUOV_m; j++) {
            t_consistent[j] = gf_add(b_consistent[j], u[j]);
        }
        linsys_lu_decompose(eqn, &echelon);
        linsys_prepare_consistency(&echelon, u, consistency_rhs);
        if (!linsys_check_prepared_consistency(&echelon, consistency_rhs, t_consistent)) {
            fprintf(stderr,
                    "test_linsys_consistency_with_zero_columns failed: prepared consistent rhs rejected at rank %d\n",
                    rank);
            return 0;
        }
        if (!linsys_check_consistency(&echelon, b_consistent)) {
            fprintf(stderr,
                    "test_linsys_consistency_with_zero_columns failed: consistent rhs rejected at rank %d\n",
                    rank);
            return 0;
        }

        if (rank == QRUOV_m) continue;

        memcpy(b_inconsistent, b_consistent, sizeof(b_inconsistent));
        // The first dependent consistency row has coefficient 1 for this
        // permuted RHS entry, so perturbing it forces inconsistency.
        uint8_t row_id = echelon.eqn[rank]->original_row_id;
        b_inconsistent[row_id] = gf_add(b_inconsistent[row_id], 1);
        for (int j = 0; j < QRUOV_m; j++) {
            t_inconsistent[j] = gf_add(b_inconsistent[j], u[j]);
        }
        if (linsys_check_consistency(&echelon, b_inconsistent)) {
            fprintf(stderr,
                    "test_linsys_consistency_with_zero_columns failed: inconsistent rhs accepted at rank %d\n",
                    rank);
            return 0;
        }
        if (linsys_check_prepared_consistency(&echelon, consistency_rhs, t_inconsistent)) {
            fprintf(stderr,
                    "test_linsys_consistency_with_zero_columns failed: prepared inconsistent rhs accepted at rank %d\n",
                    rank);
            return 0;
        }
    }

    return 1;
}

static int test_linsys_sample_solution_with_zero_columns(void)
{
    uint8_t eqn[QRUOV_m * QRUOV_m];
    uint8_t eqn_copy[QRUOV_m * QRUOV_m];
    uint8_t b[QRUOV_m];
    uint8_t b_check[QRUOV_m];
    uint8_t free_x1[QRUOV_m];
    uint8_t free_x2[QRUOV_m];
    uint8_t sol1[QRUOV_m];
    uint8_t sol2[QRUOV_m];
    uint8_t witness_x[QRUOV_m];
    linsys_echelon echelon;

    for (size_t i = 0; i < sizeof(linsys_probe_ranks) / sizeof(linsys_probe_ranks[0]); i++) {
        int rank = linsys_probe_ranks[i];
        if (rank < 0 || rank > QRUOV_m) continue;
        fq_rand_mat_zerocol(eqn, QRUOV_m, rank);
        fq_rand_values(witness_x, sizeof(witness_x));
        memcpy(eqn_copy, eqn, sizeof(eqn));
        fq_matvec_mul(b, eqn_copy, witness_x, QRUOV_m);
        linsys_lu_decompose(eqn, &echelon);
        if (!linsys_check_consistency(&echelon, b)) {
            fprintf(stderr,
                    "test_linsys_sample_solution_with_zero_columns failed: consistent rhs rejected at rank %d\n",
                    rank);
            return 0;
        }

        memset(free_x1, 0, sizeof(free_x1));
        for (int j = 0; j < QRUOV_m; j++) {
            free_x2[j] = (uint8_t)((j + 1) % QRUOV_q);
        }

        linsys_sample_solution(&echelon, b, free_x1, sol1);
        fq_matvec_mul(b_check, eqn_copy, sol1, QRUOV_m);
        if (!expect_equal_bytes("test_linsys_sample_solution_with_zero_columns(sol1)", b_check, b, sizeof(b))) {
            return 0;
        }

        linsys_sample_solution(&echelon, b, free_x2, sol2);
        fq_matvec_mul(b_check, eqn_copy, sol2, QRUOV_m);
        if (!expect_equal_bytes("test_linsys_sample_solution_with_zero_columns(sol2)", b_check, b, sizeof(b))) {
            return 0;
        }

        if (rank < QRUOV_m && memcmp(sol1, sol2, sizeof(sol1)) == 0) {
            fprintf(stderr,
                    "test_linsys_sample_solution_with_zero_columns failed: free variables had no effect at rank %d\n",
                    rank);
            return 0;
        }
    }

    return 1;
}

static int test_linsys_matches_round2_ref(void)
{
    uint8_t eqn[QRUOV_m * QRUOV_m];
    uint8_t eqn_now[QRUOV_m * QRUOV_m];
    uint8_t eqn_round2[QRUOV_m * QRUOV_m];
    uint8_t witness_x[QRUOV_m];
    uint8_t u[QRUOV_m];
    uint8_t b[QRUOV_m];
    uint8_t bad_b[QRUOV_m];
    uint8_t t[QRUOV_m];
    uint8_t bad_t[QRUOV_m];
    uint8_t consistency_rhs[QRUOV_m];
    uint8_t check[QRUOV_m];
    uint8_t free_x1[QRUOV_m];
    uint8_t free_x2[QRUOV_m];
    uint8_t sol_now[QRUOV_m];
    uint8_t sol_round2[QRUOV_m];
    linsys_echelon now;
    round2_linsys_echelon round2;

    for (int trial = 0; trial < LINSYS_COMPARE_TRIALS; trial++) {
        for (size_t i = 0; i < sizeof(linsys_probe_ranks) / sizeof(linsys_probe_ranks[0]); i++) {
            int rank = linsys_probe_ranks[i];
            if (rank < 0 || rank > QRUOV_m) continue;

            fq_rand_mat_zerocol(eqn, QRUOV_m, rank);
            fq_rand_values(witness_x, sizeof(witness_x));
            fq_rand_values(u, sizeof(u));

            fq_matvec_mul(b, eqn, witness_x, QRUOV_m);
            for (int j = 0; j < QRUOV_m; j++) {
                t[j] = gf_add(b[j], u[j]);
            }
            memcpy(eqn_now, eqn, sizeof(eqn_now));
            memcpy(eqn_round2, eqn, sizeof(eqn_round2));
            linsys_lu_decompose(eqn_now, &now);
            round2_linsys_lu_decompose(eqn_round2, &round2);

            if (now.rank != round2.rank) {
                fprintf(stderr,
                        "test_linsys_matches_round2_ref failed: rank mismatch at target rank %d trial %d (%d vs %d)\n",
                        rank, trial, now.rank, round2.rank);
                return 0;
            }

            linsys_prepare_consistency(&now, u, consistency_rhs);
            int prep_now = linsys_check_prepared_consistency(&now, consistency_rhs, t);
            int cons_now = linsys_check_consistency(&now, b);
            int cons_round2 = round2_linsys_check_consistency(&round2, b);
            if (prep_now != cons_round2 || cons_now != cons_round2 || !cons_now) {
                fprintf(stderr,
                        "test_linsys_matches_round2_ref failed: consistency mismatch at rank %d trial %d (%d/%d vs %d)\n",
                        rank, trial, cons_now, prep_now, cons_round2);
                return 0;
            }

            if (rank < QRUOV_m) {
                if (now.eqn[rank]->original_row_id != round2.eqn[rank]->original_row_id) {
                    fprintf(stderr,
                            "test_linsys_matches_round2_ref failed: dependent-row mismatch at rank %d trial %d\n",
                            rank, trial);
                    return 0;
                }
                memcpy(bad_b, b, sizeof(bad_b));
                bad_b[now.eqn[rank]->original_row_id] = gf_add(bad_b[now.eqn[rank]->original_row_id], 1);
                for (int j = 0; j < QRUOV_m; j++) {
                    bad_t[j] = gf_add(bad_b[j], u[j]);
                }
                prep_now = linsys_check_prepared_consistency(&now, consistency_rhs, bad_t);
                cons_now = linsys_check_consistency(&now, bad_b);
                cons_round2 = round2_linsys_check_consistency(&round2, bad_b);
                if (prep_now != cons_round2 || cons_now != cons_round2 || cons_now) {
                    fprintf(stderr,
                            "test_linsys_matches_round2_ref failed: inconsistent rhs mismatch at rank %d trial %d (%d/%d vs %d)\n",
                            rank, trial, cons_now, prep_now, cons_round2);
                    return 0;
                }
            }

            memset(free_x1, 0, sizeof(free_x1));
            for (int j = 0; j < QRUOV_m; j++) {
                free_x2[j] = (uint8_t)((trial + j + 1) % QRUOV_q);
            }

            linsys_sample_solution(&now, b, free_x1, sol_now);
            round2_linsys_sample_solution(&round2, b, free_x1, sol_round2);
            if (!expect_equal_bytes("test_linsys_matches_round2_ref(sol1)", sol_now, sol_round2, sizeof(sol_now))) {
                return 0;
            }
            fq_matvec_mul(check, eqn, sol_now, QRUOV_m);
            if (!expect_equal_bytes("test_linsys_matches_round2_ref(sol1 check)", check, b, sizeof(check))) {
                return 0;
            }

            linsys_sample_solution(&now, b, free_x2, sol_now);
            round2_linsys_sample_solution(&round2, b, free_x2, sol_round2);
            if (!expect_equal_bytes("test_linsys_matches_round2_ref(sol2)", sol_now, sol_round2, sizeof(sol_now))) {
                return 0;
            }
            fq_matvec_mul(check, eqn, sol_now, QRUOV_m);
            if (!expect_equal_bytes("test_linsys_matches_round2_ref(sol2 check)", check, b, sizeof(check))) {
                return 0;
            }
        }
    }

    return 1;
}

static int run_linsys_tests(void)
{
    int failures = 0;
    if (!test_linsys_lu_rank_with_zero_columns()) failures++;
    if (!test_linsys_consistency_with_zero_columns()) failures++;
    if (!test_linsys_sample_solution_with_zero_columns()) failures++;
    if (!test_linsys_matches_round2_ref()) failures++;
    if (failures != 0) {
        fprintf(stderr, "linsys_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("linsys_test: all tests passed\n");
    return 0;
}

/* qruov_common tests */

static void first_salt_hash(uint8_t t[QRUOV_m], SALT sig_r, const SEED_PK seed_pk,
                            const SEED_SK seed_r, const unsigned char *msg,
                            size_t msg_len)
{
    uint8_t mu[64];
    shake256 r_stream;
    compute_mu(mu, seed_pk, msg, msg_len);
    shake256_init(&r_stream);
    shake256_update(&r_stream, seed_r, SEED_SK_LEN);
    shake256_squeeze(&r_stream, sig_r, SALT_LEN);
    shake256_free(&r_stream);
    compute_hash(t, mu, sig_r);
    secure_zero(mu, sizeof(mu));
}

static int try_sign_solve_oil_solvable_system_at_rank(int rank, int check_solution)
{
    uint8_t oil[QRUOV_m];
    SALT sig_r;
    SALT first_sig_r;
    uint8_t eqn[QRUOV_m * QRUOV_m];
    uint8_t eqn_copy[QRUOV_m * QRUOV_m];
    uint8_t u[QRUOV_m];
    uint8_t t[QRUOV_m];
    uint8_t b[QRUOV_m];
    uint8_t check[QRUOV_m];
    uint8_t witness_oil[QRUOV_m];
    SEED_PK seed_pk;
    SEED_SK seed_r;
    SEED_SK seed_sol;
    static const unsigned char msg[] = "qruov sign solvable rank";
    const size_t msg_len = sizeof(msg) - 1;

    memset(seed_pk, 0, sizeof(seed_pk));
    memset(seed_r, 0, sizeof(seed_r));
    memset(seed_sol, 0, sizeof(seed_sol));
    fq_rand_mat_zerocol(eqn, QRUOV_m, rank);
    memcpy(eqn_copy, eqn, sizeof(eqn_copy));
    fq_rand_values(witness_oil, sizeof(witness_oil));
    fq_matvec_mul(b, eqn_copy, witness_oil, QRUOV_m);
    first_salt_hash(t, first_sig_r, seed_pk, seed_r, msg, msg_len);
    for (int i = 0; i < QRUOV_m; i++) {
        u[i] = gf_sub(t[i], b[i]);
    }

    int ret = qruov_common_sign_solve_oil(oil, sig_r, eqn, u, seed_pk, seed_r, seed_sol,
                                          msg, msg_len);
    if (ret != 0 || !check_solution) {
        return ret;
    }

    if (!expect_equal_bytes("try_sign_solve_oil_solvable_system_at_rank(sig_r)",
                            sig_r, first_sig_r, SALT_LEN)) {
        return 1;
    }
    fq_matvec_mul(check, eqn_copy, oil, QRUOV_m);
    for (int i = 0; i < QRUOV_m; i++) {
        check[i] = gf_add(check[i], u[i]);
    }
    if (!expect_equal_bytes("try_sign_solve_oil_solvable_system_at_rank(solution)",
                            check, t, sizeof(check))) {
        return 1;
    }
    return 0;
}

static int test_sign_solve_oil_rejects_below_delta_rank(void)
{
    return try_sign_solve_oil_solvable_system_at_rank(QRUOV_m - QRUOV_delta - 1, 0) != 0;
}

static int test_sign_solve_oil_accepts_delta_rank(void)
{
    return try_sign_solve_oil_solvable_system_at_rank(QRUOV_m - QRUOV_delta, 1) == 0;
}

static int test_prepare_seed_pk_from_seed_matches_reference(void)
{
    SEED_SK seed_sk;
    SEED_PK actual;
    SEED_PK expected;
    uint8_t input[SEED_SK_LEN + 2];

    for (size_t i = 0; i < SEED_SK_LEN; i++) {
        seed_sk[i] = (uint8_t)(3u * i + 1u);
    }
    memcpy(input, seed_sk, SEED_SK_LEN);
    input[SEED_SK_LEN] = 0;
    input[SEED_SK_LEN + 1] = 1;

    if (!shake_reference_256(input, sizeof(input), expected, sizeof(expected))) {
        fprintf(stderr, "shake reference failed in seed_pk test\n");
        return 0;
    }
    prepare_seed_pk_from_seed(actual, seed_sk);
    return expect_equal_bytes("test_prepare_seed_pk_from_seed_matches_reference",
                              actual, expected, sizeof(expected));
}

static int test_sig_canonical_helpers(void)
{
    SIG_S sig_s;
    memset(sig_s, 0, sizeof(sig_s));
    if (!qruov_common_is_canonical_s(sig_s)) return 0;

    sig_s[0] = (QRUOV_q - 1) / 2;
    sig_s[1] = (uint8_t)(QRUOV_q - 1);
    if (!qruov_common_is_canonical_s(sig_s)) return 0;
    qruov_common_canonicalize_s(sig_s);
    if (sig_s[0] != (QRUOV_q - 1) / 2) return 0;
    if (sig_s[1] != (uint8_t)(QRUOV_q - 1)) return 0;

    sig_s[0] = (uint8_t)((QRUOV_q + 1) / 2);
    sig_s[1] = 1;
    if (qruov_common_is_canonical_s(sig_s)) return 0;
    qruov_common_canonicalize_s(sig_s);
    if (!qruov_common_is_canonical_s(sig_s)) return 0;
    if (sig_s[0] != (uint8_t)((QRUOV_q - 1) / 2)) return 0;
    if (sig_s[1] != (uint8_t)(QRUOV_q - 1)) return 0;
    return 1;
}

static int run_qruov_common_tests(void)
{
    int failures = 0;
    if (!test_sign_solve_oil_rejects_below_delta_rank()) {
        fprintf(stderr, "qruov_common_test: test_sign_solve_oil_rejects_below_delta_rank failed\n");
        failures++;
    }
    if (!test_sign_solve_oil_accepts_delta_rank()) {
        fprintf(stderr, "qruov_common_test: test_sign_solve_oil_accepts_delta_rank failed\n");
        failures++;
    }
    if (!test_prepare_seed_pk_from_seed_matches_reference()) {
        fprintf(stderr, "qruov_common_test: test_prepare_seed_pk_from_seed_matches_reference failed\n");
        failures++;
    }
    if (!test_sig_canonical_helpers()) {
        fprintf(stderr, "qruov_common_test: test_sig_canonical_helpers failed\n");
        failures++;
    }
    if (failures != 0) {
        return 1;
    }
    printf("qruov_common_test: all tests passed\n");
    return 0;
}

/* sign api tests */

enum { SIGN_TEST_SAMPLES = 16 };

static int test_sign_keypair_derives_seed_pk(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    SEED_PK expected_seed_pk;

    if (CRYPTO_SECRETKEYBYTES != SEED_SK_LEN) return 0;
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        prepare_seed_pk_from_seed(expected_seed_pk, sk);
        if (memcmp(pk, expected_seed_pk, SEED_PK_LEN) != 0) return 0;
    }
    return 1;
}

static int test_generated_sig_canonical(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign canonical sig";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned long long smlen = 0;
    SIG_S sig_s;
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
        if (smlen != (unsigned long long)CRYPTO_BYTES + (unsigned long long)(sizeof(msg) - 1)) return 0;
        if (!check_fq_trailing_bits(sm + SALT_LEN, SIG_S_COEFF_LEN)) return 0;
        if (!load_fq_checked(sig_s, sm + SALT_LEN, SIG_S_COEFF_LEN)) return 0;
        if (!qruov_common_is_canonical_s(sig_s)) return 0;
    }
    return 1;
}

static int test_generated_pk_canonical(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    uint8_t p3[P3_COEFF_LEN];
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (!load_fq_checked(p3, pk + SEED_PK_LEN, P3_COEFF_LEN)) return 0;
    }
    return 1;
}

static int test_sign_roundtrip(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign selftest";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        if (smlen != (unsigned long long)CRYPTO_BYTES + msg_len) return 0;
        if (crypto_sign_open(out, &mlen, sm, smlen, pk) != 0) return 0;
        if (mlen != msg_len) return 0;
        if (memcmp(out, msg, (size_t)msg_len) != 0) return 0;
    }
    return 1;
}

static int test_sign_roundtrip_message_lengths(void)
{
    static const size_t msg_lens[] = { 0, 1, 2, 3, 135, 136, 137, 255, 256, 1024 };
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char msg[1024];
    unsigned char sm[CRYPTO_BYTES + sizeof(msg)];
    unsigned char out[sizeof(msg)];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;

    for (size_t i = 0; i < sizeof(msg_lens) / sizeof(msg_lens[0]); i++) {
        const size_t msg_len = msg_lens[i];
        fill_test_message(msg, msg_len);
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, (unsigned long long)msg_len, sk) != 0) return 0;
        if (smlen != (unsigned long long)CRYPTO_BYTES + (unsigned long long)msg_len) return 0;
        if (crypto_sign_open(out, &mlen, sm, smlen, pk) != 0) return 0;
        if (mlen != (unsigned long long)msg_len) return 0;
        if (memcmp(out, msg, msg_len) != 0) return 0;
    }
    return 1;
}

static int test_sign_in_place_roundtrip(void)
{
    static const size_t msg_lens[] = { 0, 1, 2, 3, 135, 136, 137, 255, 256, 1024 };
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char msg[1024];
    unsigned char sm[CRYPTO_BYTES + sizeof(msg)];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;

    for (size_t i = 0; i < sizeof(msg_lens) / sizeof(msg_lens[0]); i++) {
        const size_t msg_len = msg_lens[i];
        fill_test_message(msg, msg_len);
        if (crypto_sign_keypair(pk, sk) != 0) return 0;

        memset(sm, 0, sizeof(sm));
        memcpy(sm, msg, msg_len);
        if (crypto_sign(sm, &smlen, sm, (unsigned long long)msg_len, sk) != 0) return 0;
        if (smlen != (unsigned long long)CRYPTO_BYTES + (unsigned long long)msg_len) return 0;
        if (memcmp(sm + CRYPTO_BYTES, msg, msg_len) != 0) return 0;

        if (crypto_sign_open(sm, &mlen, sm, smlen, pk) != 0) return 0;
        if (mlen != (unsigned long long)msg_len) return 0;
        if (memcmp(sm, msg, msg_len) != 0) return 0;
    }
    return 1;
}

static int test_sign_tamper_salt_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign tamper salt";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        memcpy(sm_bad, sm, (size_t)smlen);
        sm_bad[0] ^= 1;
        mlen = 123;
        if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
        if (mlen != 0) return 0;
    }
    return 1;
}

static int test_sign_tamper_sig_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign tamper sig";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    SIG_S sig_s;
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        if (!load_fq_checked(sig_s, sm + SALT_LEN, SIG_S_COEFF_LEN)) return 0;
        memcpy(sm_bad, sm, (size_t)smlen);
        sig_s[0] = (uint8_t)((sig_s[0] + 1u) % QRUOV_q);
        store_fq(sm_bad + SALT_LEN, sig_s, SIG_S_COEFF_LEN);
        mlen = 123;
        if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
        if (mlen != 0) return 0;
    }
    return 1;
}

static int test_sign_negated_sig_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign negated sig";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 123;
    SIG_S sig_s;
    int saw_nonzero = 0;

    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
    if (!load_fq_checked(sig_s, sm + SALT_LEN, SIG_S_COEFF_LEN)) return 0;
    if (!qruov_common_is_canonical_s(sig_s)) return 0;
    for (int i = 0; i < SIG_S_COEFF_LEN; i++) {
        if (sig_s[i] != 0) {
            sig_s[i] = (uint8_t)(QRUOV_q - sig_s[i]);
            saw_nonzero = 1;
        }
    }
    if (!saw_nonzero) return 0;
    if (qruov_common_is_canonical_s(sig_s)) return 0;

    memcpy(sm_bad, sm, (size_t)smlen);
    store_fq(sm_bad + SALT_LEN, sig_s, SIG_S_COEFF_LEN);
    if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_tamper_msg_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign tamper msg";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        memcpy(sm_bad, sm, (size_t)smlen);
        sm_bad[QRUOV_SIG_LEN] ^= 1;
        mlen = 123;
        if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
        if (mlen != 0) return 0;
    }
    return 1;
}

static int test_sign_tamper_seed_pk_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char pk_bad[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign tamper seed pk";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        memcpy(pk_bad, pk, sizeof(pk_bad));
        pk_bad[0] ^= 1;
        mlen = 123;
        if (crypto_sign_open(out, &mlen, sm, smlen, pk_bad) == 0) return 0;
        if (mlen != 0) return 0;
    }
    return 1;
}

static int test_sign_tamper_p3_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char pk_bad[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign tamper p3";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    unsigned long long msg_len = (unsigned long long)(sizeof(msg) - 1);
    SIG_S sig_s;
    size_t active_idx = 0;
    for (int i = 0; i < SIGN_TEST_SAMPLES; i++) {
        if (crypto_sign_keypair(pk, sk) != 0) return 0;
        if (crypto_sign(sm, &smlen, msg, msg_len, sk) != 0) return 0;
        if (!load_fq_checked(sig_s, sm + SALT_LEN, SIG_S_COEFF_LEN)) return 0;
        if (!find_active_p3_coeff(sig_s + QRUOV_V * QRUOV_L, &active_idx)) return 0;
        memcpy(pk_bad, pk, sizeof(pk_bad));
        uint8_t coeff = fq_get_packed_coeff(pk_bad + SEED_PK_LEN, active_idx);
        fq_set_packed_coeff(pk_bad + SEED_PK_LEN, active_idx, (uint8_t)((coeff + 1u) % QRUOV_q));
        mlen = 123;
        if (crypto_sign_open(out, &mlen, sm, smlen, pk_bad) == 0) return 0;
        if (mlen != 0) return 0;
    }
    return 1;
}

static int test_sign_short_input_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char out[1];
    unsigned char sm[CRYPTO_BYTES];
    unsigned long long mlen = 9;
    memset(pk, 0, sizeof(pk));
    memset(sm, 0, sizeof(sm));
    if (crypto_sign_open(out, &mlen, sm, (unsigned long long)(CRYPTO_BYTES - 1), pk) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_open_failure_returns_minus_one(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char out[1];
    unsigned char sm[CRYPTO_BYTES];
    unsigned long long mlen = 9;
    memset(pk, 0, sizeof(pk));
    memset(sm, 0, sizeof(sm));
    if (crypto_sign_open(out, &mlen, sm, (unsigned long long)(CRYPTO_BYTES - 1), pk) != -1) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_nonzero_trailing_sig_bits_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign trailing sig";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 123;
    const unsigned used_bits = fq_used_bits_last_byte(SIG_S_COEFF_LEN);
    if (used_bits == 0) return 1;
    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
    memcpy(sm_bad, sm, (size_t)smlen);
    sm_bad[SALT_LEN + fq_packed_len(SIG_S_COEFF_LEN) - 1] |= (unsigned char)(1u << used_bits);
    if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_nonzero_trailing_pk_bits_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char pk_bad[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign trailing pk";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 123;
    const unsigned used_bits = fq_used_bits_last_byte(P3_COEFF_LEN);
    if (used_bits == 0) return 1;
    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
    memcpy(pk_bad, pk, sizeof(pk_bad));
    pk_bad[SEED_PK_LEN + fq_packed_len(P3_COEFF_LEN) - 1] |= (unsigned char)(1u << used_bits);
    if (crypto_sign_open(out, &mlen, sm, smlen, pk_bad) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_noncanonical_sig_coeff_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign coeff sig";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char sm_bad[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 123;
    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
    memcpy(sm_bad, sm, (size_t)smlen);
    fq_set_packed_coeff(sm_bad + SALT_LEN, 0, QRUOV_q);
    if (crypto_sign_open(out, &mlen, sm_bad, smlen, pk) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int test_sign_noncanonical_pk_coeff_reject(void)
{
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char pk_bad[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    static const unsigned char msg[] = "qruov sign coeff pk";
    unsigned char sm[CRYPTO_BYTES + sizeof(msg) - 1];
    unsigned char out[sizeof(msg) - 1];
    unsigned long long smlen = 0;
    unsigned long long mlen = 123;
    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    if (crypto_sign(sm, &smlen, msg, (unsigned long long)(sizeof(msg) - 1), sk) != 0) return 0;
    memcpy(pk_bad, pk, sizeof(pk_bad));
    fq_set_packed_coeff(pk_bad + SEED_PK_LEN, 0, QRUOV_q);
    if (crypto_sign_open(out, &mlen, sm, smlen, pk_bad) == 0) return 0;
    if (mlen != 0) return 0;
    return 1;
}

static int run_sign_tests(void)
{
    int failures = 0;
#define RUN_SIGN_TEST(fn) \
    do { \
        if (!(fn)()) { \
            fprintf(stderr, "sign_test: %s failed\n", #fn); \
            failures++; \
        } \
    } while (0)
    RUN_SIGN_TEST(test_sign_keypair_derives_seed_pk);
    RUN_SIGN_TEST(test_generated_sig_canonical);
    RUN_SIGN_TEST(test_generated_pk_canonical);
    RUN_SIGN_TEST(test_sign_roundtrip);
    RUN_SIGN_TEST(test_sign_roundtrip_message_lengths);
    RUN_SIGN_TEST(test_sign_in_place_roundtrip);
    RUN_SIGN_TEST(test_sign_tamper_salt_reject);
    RUN_SIGN_TEST(test_sign_tamper_sig_reject);
    RUN_SIGN_TEST(test_sign_negated_sig_reject);
    RUN_SIGN_TEST(test_sign_tamper_msg_reject);
    RUN_SIGN_TEST(test_sign_tamper_seed_pk_reject);
    RUN_SIGN_TEST(test_sign_tamper_p3_reject);
    RUN_SIGN_TEST(test_sign_short_input_reject);
    RUN_SIGN_TEST(test_sign_open_failure_returns_minus_one);
    RUN_SIGN_TEST(test_sign_nonzero_trailing_sig_bits_reject);
    RUN_SIGN_TEST(test_sign_nonzero_trailing_pk_bits_reject);
    RUN_SIGN_TEST(test_sign_noncanonical_sig_coeff_reject);
    RUN_SIGN_TEST(test_sign_noncanonical_pk_coeff_reject);
#undef RUN_SIGN_TEST
    if (failures != 0) {
        fprintf(stderr, "sign_test: %d test(s) failed\n", failures);
        return 1;
    }
    printf("sign_test: all tests passed\n");
    return 0;
}

int main(void)
{
    int failures = 0;
    if (!seed_rng_for_tests()) return 1;
    qruov_init();
    if (run_shake_tests() != 0) failures++;
    if (run_prg_tests() != 0) failures++;
    if (run_fq_tests() != 0) failures++;
    if (run_fastop_tests() != 0) failures++;
#ifdef QRUOV_HAS_EMI_TRANSFORM
    if (run_emi_tests() != 0) failures++;
#endif
    if (run_linsys_tests() != 0) failures++;
    if (run_qruov_common_tests() != 0) failures++;
    if (run_sign_tests() != 0) failures++;
    if (failures != 0) {
        fprintf(stderr, "test: %d test group(s) failed\n", failures);
        return 1;
    }
    printf("test: all tests passed\n");
    return 0;
}
