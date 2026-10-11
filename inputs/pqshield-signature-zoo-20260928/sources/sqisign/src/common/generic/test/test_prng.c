// SPDX-License-Identifier: Apache-2.0

/** @file
 *
 * @brief Unit tests for the SHAKE-based PRNG, exercising it through its public API only.
 *
 * This binary links the same prng.o the library ships, so everything here is black-box. The complementary
 * test_prng_kat.c checks prng_domain_seed()'s construction against a NIST CAVP vector, which needs white-box access to
 * the root seed and therefore lives in its own target.
 */

#include <prng.h>
#include <rng.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define STREAM_BYTES 300 // > 2 * SHAKE256_RATE, so comparisons span several squeeze blocks

// Distinct from DS_DEFAULT_DOMAIN, and distinct from each other
#define DS_TEST_DOMAIN_A "TSA"
#define DS_TEST_DOMAIN_B "TSB"

// Two consecutive squeezes of n bytes must give the same stream as one squeeze of 2n.
static int
test_prng_streaming(void)
{
    prng_domain_ctx_t split, whole;
    uint8_t a[STREAM_BYTES], b[STREAM_BYTES];
    const size_t half = STREAM_BYTES / 2;
    int res = 1;

    if (prng_domain_seed(&split, DS_TEST_DOMAIN_A) != 0 || prng_domain_seed(&whole, DS_TEST_DOMAIN_A) != 0) {
        printf("  FAIL streaming: could not derive domains\n");
        return 0;
    }

    if (prng_random_bytes(&split, a, half) != 0 || prng_random_bytes(&split, a + half, STREAM_BYTES - half) != 0 ||
        prng_random_bytes(&whole, b, STREAM_BYTES) != 0) {
        printf("  FAIL streaming: squeeze failed\n");
        res = 0;
    } else if (memcmp(a, b, STREAM_BYTES) != 0) {
        printf("  FAIL streaming: split squeeze differs from contiguous squeeze\n");
        res = 0;
    }

    prng_domain_clear(&split);
    prng_domain_clear(&whole);

    return res;
}

// The same separator must reproduce a stream; different separators must not share one.
static int
test_prng_domain_separation(void)
{
    prng_domain_ctx_t a1, a2, b;
    uint8_t sa1[STREAM_BYTES], sa2[STREAM_BYTES], sb[STREAM_BYTES];
    int res = 1;

    if (prng_domain_seed(&a1, DS_TEST_DOMAIN_A) != 0 || prng_domain_seed(&a2, DS_TEST_DOMAIN_A) != 0 ||
        prng_domain_seed(&b, DS_TEST_DOMAIN_B) != 0) {
        printf("  FAIL domain separation: could not derive domains\n");
        return 0;
    }

    if (prng_random_bytes(&a1, sa1, STREAM_BYTES) != 0 || prng_random_bytes(&a2, sa2, STREAM_BYTES) != 0 ||
        prng_random_bytes(&b, sb, STREAM_BYTES) != 0) {
        printf("  FAIL domain separation: squeeze failed\n");
        res = 0;
    } else {
        if (memcmp(sa1, sa2, STREAM_BYTES) != 0) {
            printf("  FAIL domain separation: same separator gave different streams\n");
            res = 0;
        }
        if (memcmp(sa1, sb, STREAM_BYTES) == 0) {
            printf("  FAIL domain separation: different separators gave the same stream\n");
            res = 0;
        }
    }

    prng_domain_clear(&a1);
    prng_domain_clear(&a2);
    prng_domain_clear(&b);

    return res;
}

// prng_clear() must leave the default domain unusable, and a later prng_seed() must restore it.
static int
test_prng_clear_and_reseed(void)
{
    uint8_t out[32];
    int res = 1;

    prng_clear();

#ifdef NDEBUG
    // Only reachable with asserts disabled: squeezing from a cleared context is a usage error that asserts in debug
    // builds, so it is the release-mode return path that is under test here.
    memset(out, 0xA5, sizeof(out));
    if (prng_random_bytes(&PRNG_default_domain, out, sizeof(out)) != -1) {
        printf("  FAIL clear/reseed: squeeze after prng_clear() did not fail\n");
        res = 0;
    }
    for (size_t i = 0; i < sizeof(out); i++) {
        if (out[i] != 0xA5) {
            printf("  FAIL clear/reseed: failed squeeze wrote to out\n");
            res = 0;
            break;
        }
    }
#endif

    if (prng_seed() != 0) {
        printf("  FAIL clear/reseed: reseeding after prng_clear() failed\n");
        return 0;
    }
    if (prng_random_bytes(&PRNG_default_domain, out, sizeof(out)) != 0) {
        printf("  FAIL clear/reseed: squeeze after reseeding failed\n");
        res = 0;
    }

    return res;
}

#ifdef NDEBUG
// Check that usage errors are reported rather than acted on. Both paths assert in debug builds, so this only runs with
// asserts disabled.
static int
test_prng_usage_errors(void)
{
    prng_domain_ctx_t ctx;
    uint8_t out[32];
    int res = 1;

    // An unseeded context must not produce output
    memset(&ctx, 0, sizeof(ctx));
    memset(out, 0x5A, sizeof(out));
    if (prng_random_bytes(&ctx, out, sizeof(out)) != -1) {
        printf("  FAIL usage errors: squeeze from an unseeded context did not fail\n");
        res = 0;
    }
    for (size_t i = 0; i < sizeof(out); i++) {
        if (out[i] != 0x5A) {
            printf("  FAIL usage errors: failed squeeze wrote to out\n");
            res = 0;
            break;
        }
    }

    // A separator of the wrong length must be rejected
    if (prng_domain_seed(&ctx, "TOOLONG") != -1) {
        printf("  FAIL usage errors: over-long separator was accepted\n");
        res = 0;
        prng_domain_clear(&ctx);
    }
    const char too_short[PRNG_DOMAIN_SEP_BYTES + 1] = "XY";
    if (prng_domain_seed(&ctx, too_short) != -1) {
        printf("  FAIL usage errors: too-short separator was accepted\n");
        res = 0;
        prng_domain_clear(&ctx);
    }

    return res;
}
#endif

// Regression anchor for the whole chain: a fixed randombytes() seed must give a fixed PRNG stream.
//
// Unlike test_prng_kat.c, this is not based on a published KAT; it exists so that an unintended change to the
// construction (absorb order, PRNG_SEED_BYTES, the default separator, or the test DRBG feeding it) shows up as a test
// failure rather than only as a KAT mismatch. If you change any of those deliberately, update the value below -- and
// expect the scheme KATs in KAT/ to need regenerating too.
static int
test_prng_golden_value(void)
{
    // Deliberately not all-zero, so a memset'd buffer could not accidentally reproduce it
    uint8_t seed[48] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f
    };
    // Cross-checked against an independent computation of SHAKE256(root || DS_DEFAULT_DOMAIN) over the 48 bytes the
    // test DRBG produces from the seed above.
    static const uint8_t expected[32] = { 0x9a, 0xe7, 0xba, 0x8f, 0x33, 0xfa, 0xb1, 0xb2, 0xa5, 0x4c, 0xdc,
                                          0x09, 0x80, 0x8c, 0x25, 0x19, 0xff, 0x53, 0x6a, 0x71, 0x26, 0x93,
                                          0xe4, 0xc9, 0x23, 0xec, 0x90, 0xeb, 0x52, 0xb7, 0xec, 0xdf };
    uint8_t got[32];

    randombytes_init(seed, NULL, 256);
    if (prng_seed() != 0) {
        printf("  FAIL golden value: seeding failed\n");
        return 0;
    }
    if (prng_random_bytes(&PRNG_default_domain, got, sizeof(got)) != 0) {
        printf("  FAIL golden value: squeeze failed\n");
        return 0;
    }

    if (memcmp(got, expected, sizeof(expected)) != 0) {
        printf("  FAIL golden value: PRNG stream changed. Got:\n    ");
        for (size_t i = 0; i < sizeof(got); i++)
            printf("0x%02x, ", got[i]);
        printf("\n");
        return 0;
    }

    return 1;
}

int
main(void)
{
    uint32_t seed[12] = { 0 };
    int res = 1;

    printf("Running PRNG unit tests\n");

    randombytes_init((unsigned char *)seed, NULL, 256);
    if (prng_seed() != 0) {
        printf("PRNG seeding failed\n");
        return 1;
    }

    res &= test_prng_streaming();
    res &= test_prng_domain_separation();
#ifdef NDEBUG
    res &= test_prng_usage_errors();
#endif
    // Leaves the default domain freshly seeded, so it must precede nothing that assumes the seed above
    res &= test_prng_clear_and_reseed();
    res &= test_prng_golden_value();

    prng_clear();

    if (!res) {
        printf("PRNG unit tests failed\n");
        return 1;
    }

    printf("PRNG unit tests passed\n");

    return 0;
}
