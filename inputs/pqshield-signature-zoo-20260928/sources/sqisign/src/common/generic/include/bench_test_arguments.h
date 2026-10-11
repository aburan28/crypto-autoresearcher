// SPDX-License-Identifier: Apache-2.0
#ifndef BENCH_TEST_ARGUMENTS_H__
#define BENCH_TEST_ARGUMENTS_H__

#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <prng.h>
#include <rng.h>

// Seed the randomness needed by a test or benchmark main().
//
// @param[in] seed 12 uint32_t words (48 bytes), as filled by parse_seed() or randombytes_select()
// @return int 0 on success, 1 on PRNG seeding failure
//
// inline to work around -Wunused-function
static inline int
init_test_rng(const uint32_t *seed)
{
    randombytes_init((unsigned char *)seed, NULL, 256);
    if (prng_seed() != 0) {
        printf("PRNG seeding failed\n");
        return 1;
    }

    return 0;
}

static int
parse_seed(const char *arg, uint32_t *seed)
{
    if (sscanf(arg, "--seed=%u", &seed[0]) == 1)
        return 0;

    if (sscanf(arg,
               "--seed={ "
               "0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", "
               "0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 ", 0x%" PRIx32 " }",
               &seed[0],
               &seed[1],
               &seed[2],
               &seed[3],
               &seed[4],
               &seed[5],
               &seed[6],
               &seed[7],
               &seed[8],
               &seed[9],
               &seed[10],
               &seed[11]) == 12)
        return 0;

    return 1;
}

static void
print_seed(const uint32_t *seed)
{
    printf("Random seed: \"--seed={ ");
    for (int i = 0; i < 12; i++) {
        printf("0x%08x%s", seed[i], (i < 11) ? ", " : " }\"\n");
    }

    // Flushing ensures that at least the seed is printed in case of a crash, to allow reproducing the bug later.
    fflush(stdout);
}

#endif
