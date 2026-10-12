// SPDX-License-Identifier: Apache-2.0
// Exploratory laboratory timing driver for upstream SQIsign p324_3.
#define _POSIX_C_SOURCE 200809L
#include <api.h>
#include <rng.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define KEYS 8
#define ROUNDS 32
#define MSG_LEN 32

// Defined only by the instrumented build. Uninstrumented signing cannot read it.
extern volatile unsigned long long sqisign_probe_loop2_iterations __attribute__((weak));

static uint32_t shuffle_state = 0x13579bdfU;
static uint32_t
next_shuffle(void)
{
    uint32_t x = shuffle_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return shuffle_state = x;
}

static uint64_t
nanoseconds(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        return 0;
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static uint64_t
checksum(const unsigned char *p, size_t n)
{
    uint64_t h = UINT64_C(14695981039346656037);
    for (size_t i = 0; i < n; i++) {
        h ^= p[i];
        h *= UINT64_C(1099511628211);
    }
    return h;
}

int
main(void)
{
    unsigned char seed[48] = { 0 };
    unsigned char pk[KEYS][CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[KEYS][CRYPTO_SECRETKEYBYTES];
    const int instrumented = &sqisign_probe_loop2_iterations != NULL;

    randombytes_init(seed, NULL, 256);
    fprintf(stderr, "variant=%s keys=%d rounds=%d seed=48-zero-bytes instrumented=%d\n",
            CRYPTO_ALGNAME, KEYS, ROUNDS, instrumented);
    for (int k = 0; k < KEYS; k++) {
        if (crypto_sign_keypair(pk[k], sk[k]) != 0) {
            fprintf(stderr, "keygen failed key=%d\n", k);
            return 1;
        }
    }
    puts("round,key,position,sign_ns,loop2_iterations,signature_fnv64");
    fflush(stdout);
    for (int r = 0; r < ROUNDS; r++) {
        unsigned char msg[MSG_LEN];
        int order[KEYS];
        for (int i = 0; i < MSG_LEN; i++)
            msg[i] = (unsigned char)((r * 17 + i * 29) & 255);
        for (int i = 0; i < KEYS; i++)
            order[i] = i;
        for (int i = KEYS - 1; i > 0; i--) {
            unsigned j = next_shuffle() % (unsigned)(i + 1);
            int tmp = order[i];
            order[i] = order[j];
            order[j] = tmp;
        }
        for (int pos = 0; pos < KEYS; pos++) {
            unsigned char sm[CRYPTO_BYTES + MSG_LEN];
            unsigned char opened[MSG_LEN];
            unsigned long long sm_len = 0, opened_len = 0;
            int k = order[pos];
            if (instrumented)
                sqisign_probe_loop2_iterations = 0;
            uint64_t t0 = nanoseconds();
            int ret = crypto_sign(sm, &sm_len, msg, MSG_LEN, sk[k]);
            uint64_t t1 = nanoseconds();
            if (ret != 0 || sm_len != sizeof(sm)) {
                fprintf(stderr, "sign failed round=%d key=%d ret=%d len=%llu\n", r, k, ret, sm_len);
                return 2;
            }
            uint64_t iterations = instrumented ? sqisign_probe_loop2_iterations : 0;
            if (crypto_sign_open(opened, &opened_len, sm, sm_len, pk[k]) != 0 ||
                opened_len != MSG_LEN || memcmp(opened, msg, MSG_LEN) != 0) {
                fprintf(stderr, "verify failed round=%d key=%d\n", r, k);
                return 3;
            }
            printf("%d,%d,%d,%" PRIu64 ",%" PRIu64 ",%016" PRIx64 "\n",
                   r, k, pos, t1 - t0, iterations, checksum(sm, sm_len));
            fflush(stdout);
        }
    }
    fprintf(stderr, "completed=%d verified signatures\n", KEYS * ROUNDS);
    return 0;
}
