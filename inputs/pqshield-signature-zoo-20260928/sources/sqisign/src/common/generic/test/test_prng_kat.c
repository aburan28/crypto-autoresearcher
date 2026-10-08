// SPDX-License-Identifier: Apache-2.0

/** @file
 *
 * @brief Known-answer test for prng_domain_seed() against a NIST CAVP SHAKE-256 vector.
 *
 * prng_domain_seed() derives a stream as SHAKE256(root_seed || domain), absorbing 48 + 3 = 51 bytes. The CAVP
 * SHAKE256ShortMsg record with Len = 408 has a message of exactly that size, so splitting it into a 48-byte root seed
 * and a 3-byte separator turns it into a known-answer test of the production code path: the first 32 bytes squeezed
 * must equal the vector's Output.
 *
 * Installing a chosen root seed is not possible through the public API -- prng_root is static and is only ever written
 * by randombytes() -- so this file includes prng.c directly. That is why it is a separate target from test_prng.c: the
 * black-box contract tests there run against the same prng.o the library ships, and only this known-answer test needs
 * to reach inside. Nothing here adds a test hook to prng.c or to the shipped library.
 *
 * Because prng.c is compiled into this translation unit, the target must not also link a library containing it; see the
 * explicit source list in CMakeLists.txt.
 */

#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Including a .c file is deliberate here, as explained above
// NOLINTNEXTLINE(bugprone-suspicious-include) - deliberate, see above
#include "../prng.c"

// Truncating either field would silently turn this into a test of something else
_Static_assert(PRNG_SEED_BYTES == 48, "the CAVP vector is split 48 + 3; PRNG_SEED_BYTES no longer matches");
_Static_assert(PRNG_DOMAIN_SEP_BYTES == 3, "the CAVP vector is split 48 + 3; PRNG_DOMAIN_SEP_BYTES no longer matches");

// NIST CAVP SHA-3 byte-oriented test vectors (CAVS 19.0), SHAKE256ShortMsg.rsp, Len = 408, [Outputlen = 256].
// The full 51-byte Msg: the first 48 bytes are used as the root seed, the last 3 as the domain separator.
static const uint8_t cavp_msg[51] = {
    0xcf, 0xca, 0x89, 0x67, 0xea, 0xbe, 0x1a, 0xab, 0x78, 0x3d, 0x5c, 0xea, 0xf3, 0x6d, 0x2c, 0x98, 0xc6,
    0x9a, 0xf7, 0x86, 0x54, 0x2a, 0xd8, 0x6e, 0x3b, 0xd3, 0x00, 0xcd, 0xda, 0x0b, 0x5b, 0xf0, 0x11, 0xc0,
    0x71, 0x52, 0x47, 0x4a, 0x8a, 0x25, 0xb2, 0x9e, 0x15, 0x2f, 0xd2, 0xc4, 0x4a, 0xd7, 0x3f, 0x8b, 0x0f,
};

static const uint8_t cavp_output[32] = {
    0xe5, 0x60, 0xb7, 0xf4, 0x56, 0x16, 0x08, 0x9d, 0x76, 0x36, 0x2f, 0x48, 0x3f, 0x58, 0x5f, 0xdd,
    0xc2, 0x8c, 0x8a, 0x10, 0xdc, 0x78, 0x50, 0x36, 0xf9, 0x7a, 0xc2, 0xe3, 0x9b, 0x61, 0x59, 0x54,
};

// The separator is the vector's last three bytes, 3f 8b 0f. None is NUL, so it generates a valid C string of length 3,
// even if it requires the awkward \x syntax below to declare.
static const char cavp_domain[PRNG_DOMAIN_SEP_BYTES + 1] = "\x3f\x8b\x0f";

int
main(void)
{
    prng_domain_ctx_t ctx;
    uint8_t got[sizeof(cavp_output)];

    printf("Running PRNG known-answer test\n");

    // Install the vector's first 48 bytes as this thread's root seed, which no public entry point can do
    memcpy(prng_root.seed, cavp_msg, PRNG_SEED_BYTES);
    prng_root.seeded = PRNG_SEEDED_MAGIC;

    if (prng_domain_seed(&ctx, cavp_domain) != 0) {
        printf("prng_domain_seed failed\n");
        return 1;
    }
    if (prng_random_bytes(&ctx, got, sizeof(got)) != 0) {
        printf("prng_random_bytes failed\n");
        return 1;
    }

    prng_domain_clear(&ctx);
    prng_clear();

    if (memcmp(got, cavp_output, sizeof(cavp_output)) != 0) {
        printf("PRNG known-answer test failed. Got:\n    ");
        for (size_t i = 0; i < sizeof(got); i++)
            printf("0x%02x, ", got[i]);
        printf("\nExpected:\n    ");
        for (size_t i = 0; i < sizeof(cavp_output); i++)
            printf("0x%02x, ", cavp_output[i]);
        printf("\n");
        return 1;
    }

    printf("PRNG known-answer test passed\n");

    return 0;
}
