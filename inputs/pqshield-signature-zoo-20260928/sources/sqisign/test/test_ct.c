// SPDX-License-Identifier: Apache-2.0

// Constant-time testing harness: one keypair and one signature through the library API, no verification
// (verification operates on public data only and is allowed to be variable-time). Secret data is poisoned
// (marked undefined) so that valgrind memcheck reports any secret-dependent branch or memory access; the
// accepted exemptions live in test/ct-*.supp. Build with ENABLE_CT_TESTING=ON and run under valgrind; outside
// valgrind the client requests are no-ops and this is just a keypair+sign smoke test.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <rng.h>
#include <sig.h>
#include <api.h>
#include <bench_test_arguments.h>
#if defined(TARGET_BIG_ENDIAN)
#include <tutil.h>
#endif

#include <ct_testing.h>

static int
test_ct(unsigned long long msglen)
{
    unsigned char *pk = calloc(CRYPTO_PUBLICKEYBYTES, 1);
    unsigned char *sk = calloc(CRYPTO_SECRETKEYBYTES, 1);
    unsigned char *sig = calloc(CRYPTO_BYTES + msglen, 1);
    unsigned char *msg = malloc(msglen);

    unsigned long long smlen = CRYPTO_BYTES + msglen;
    int res;

    randombytes(msg, msglen);
    // Messages are public by protocol; only their randombytes source is tainted
    CT_TESTING_MAKE_PUBLIC(msg, msglen);

    printf("Testing Keygen, Sign (CT harness): %s\n", CRYPTO_ALGNAME);

    res = crypto_sign_keypair(pk, sk);
    if (res == 0) {
        // Poison the serialized secret key so signing is checked even if keygen taint did not reach every sk byte
        CT_TESTING_MAKE_SECRET(sk, CRYPTO_SECRETKEYBYTES);
        res = crypto_sign(sig, &smlen, msg, msglen, sk);
    }

    free(pk);
    free(sk);
    free(sig);
    free(msg);
    return res != 0 ? -1 : 0;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int help = 0;
    int seed_set = 0;
    int msglen_set = 0;
    int res = 0;
    unsigned long long msglen = 32;

    for (int i = 1; i < argc; i++) {
        unsigned int _msglen;

        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (!msglen_set && sscanf(argv[i], "--msglen=%u", &_msglen) == 1) {
            msglen = (unsigned long long)_msglen;
            msglen_set = 1;
        }
    }

    if (help) {
        printf("Usage: %s [--seed=<seed>] [--msglen=<len>]\n", argv[0]);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is "
               "generated\n");
        return 1;
    }

    if (!seed_set) {
        randombytes_select((unsigned char *)seed, sizeof(seed));
    }

    print_seed(seed);

#if defined(TARGET_BIG_ENDIAN)
    for (int i = 0; i < 12; i++) {
        seed[i] = BSWAP32(seed[i]);
    }
#endif

    randombytes_init((unsigned char *)seed, NULL, 256);

    res = test_ct(msglen);

    if (res != 0) {
        printf("test failed for %s\n", CRYPTO_ALGNAME);
    }
    return res;
}
