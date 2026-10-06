#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "api.h"
#include "rng.h"

#ifdef CLOCK_MONOTONIC_RAW
#define BENCH_CLOCK_ID CLOCK_MONOTONIC_RAW
#else
#define BENCH_CLOCK_ID CLOCK_MONOTONIC
#endif

static double now_sec(void)
{
    struct timespec ts;
    clock_gettime(BENCH_CLOCK_ID, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

static int default_count(void)
{
    int count = 200;
    const char *s = getenv("COUNT");
    if (s != NULL) {
        int v = atoi(s);
        if (v > 0) count = v;
    }
    return count;
}

static void seed_rng_deterministic(void)
{
    unsigned char seed[48];
    for (int i = 0; i < (int)sizeof(seed); i++) seed[i] = (unsigned char)i;
    randombytes_init(seed, NULL, 256);
}

static int warmup(unsigned char *pk, unsigned char *sk, unsigned char *m, size_t mlen,
                  unsigned char *sm, unsigned long long *smlen, unsigned long long *out_mlen)
{
    if (crypto_sign_keypair(pk, sk) != 0) return 0;
    randombytes(m, (unsigned long long)mlen);
    if (crypto_sign(sm, smlen, m, (unsigned long long)mlen, sk) != 0) return 0;
    if (crypto_sign_open(m, out_mlen, sm, *smlen, pk) != 0) return 0;
    return 1;
}

static void bench_keygen(int count, unsigned char *pk, unsigned char *sk)
{
    double t0 = now_sec();
    for (int i = 0; i < count; i++) (void)crypto_sign_keypair(pk, sk);
    double t1 = now_sec();
    printf("keygen: %.3f ms/op (%d)\n", (t1 - t0) * 1000.0 / count, count);
}

static void bench_sign(int count, unsigned char *sm, unsigned long long *smlen,
                       const unsigned char *m, unsigned long long mlen,
                       const unsigned char *sk)
{
    double t0 = now_sec();
    for (int i = 0; i < count; i++) (void)crypto_sign(sm, smlen, m, mlen, sk);
    double t1 = now_sec();
    printf("sign: %.3f ms/op (%d)\n", (t1 - t0) * 1000.0 / count, count);
}

static void bench_verify(int count, unsigned char *m_out, unsigned long long *mlen_out,
                         const unsigned char *sm, unsigned long long smlen,
                         const unsigned char *pk)
{
    double t0 = now_sec();
    for (int i = 0; i < count; i++) (void)crypto_sign_open(m_out, mlen_out, sm, smlen, pk);
    double t1 = now_sec();
    printf("verify: %.3f ms/op (%d)\n", (t1 - t0) * 1000.0 / count, count);
}

int main(int argc, char **argv)
{
    int count = default_count();
    unsigned char pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char sk[CRYPTO_SECRETKEYBYTES];
    unsigned char m[128];
    unsigned char m_out[128];
    unsigned char sm[128 + CRYPTO_BYTES];
    unsigned long long smlen = 0;
    unsigned long long mlen_out = 0;

    seed_rng_deterministic();
    if (!warmup(pk, sk, m, sizeof(m), sm, &smlen, &mlen_out)) {
        fprintf(stderr, "bench: warmup failed\n");
        return 1;
    }

    if (argc == 1) {
        bench_keygen(count, pk, sk);
        bench_sign(count, sm, &smlen, m, (unsigned long long)sizeof(m), sk);
        bench_verify(count, m_out, &mlen_out, sm, smlen, pk);
        return 0;
    }

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "keygen") == 0) {
            bench_keygen(count, pk, sk);
        } else if (strcmp(argv[i], "sign") == 0) {
            bench_sign(count, sm, &smlen, m, (unsigned long long)sizeof(m), sk);
        } else if (strcmp(argv[i], "verify") == 0) {
            bench_verify(count, m_out, &mlen_out, sm, smlen, pk);
        } else {
            fprintf(stderr, "unknown benchmark: %s (use keygen/sign/verify)\n", argv[i]);
            return 1;
        }
    }
    return 0;
}
