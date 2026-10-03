// SPDX-License-Identifier: Apache-2.0

/** @file
 *
 * @brief Checks that running signature operations in parallel is equivalent to running them serially.
 *
 * Both layers of randomness have thread storage duration: the SHAKE PRNG root and default domain (see prng.h) and, in
 * sqisign_common_test which this binary links, the AES-CTR-DRBG behind randombytes() (see rng.h). Within the library,
 * the only consumers of randomness are the prng_seed() calls entering protocols_keygen()/protocols_sign() and the
 * prng_random_bytes() draws beneath them, and both entry points prng_clear() on the way out. So once a thread has
 * seeded its own generator, everything it computes is a deterministic function of that seed.
 *
 * That makes the real property testable rather than merely "nothing crashed": each thread is given its own seed, runs
 * its operations concurrently with the others, and the whole schedule is then replayed one thread at a time on a single
 * thread. The two runs must agree byte for byte. A mismatch means state leaked between concurrent operations.
 *
 * Every seed derives from the one printed at startup, so a failure replays exactly from its --seed= line.
 */

#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <verification.h>
#include <signature.h>
#include <rng.h>
#include <fips202.h>
#include <encoded_sizes.h>
#include <bench_test_arguments.h>

#include <pthread.h>

#define WORKER_SEED_BYTES 48 // what randombytes_init() consumes

// One record per operation. secret_key_to_bytes() encodes the public key alongside the secret key, so no separate
// public-key field is needed.
#define RECORD_BYTES (SECRETKEY_BYTES + SIGNATURE_BYTES)

int threads = 4;
int iterations = SQISIGN_TEST_REPS;

typedef struct
{
    int index;
    unsigned char *seed; // WORKER_SEED_BYTES, drawn by main() from the printed seed
    unsigned char *out;  // iterations * RECORD_BYTES
    int ok;
} worker_t;

// The body both runs execute, identically: seed this thread, then keygen/sign/verify.
static void
run_ops(worker_t *w)
{
    public_key_t pk;
    secret_key_t sk;
    signature_t sig;

    w->ok = 0;

    // Each thread seeds its own generator. With the thread-local CTR-DRBG this is what makes the loop below depend on
    // w->seed and nothing else.
    randombytes_init(w->seed, NULL, 256);

    public_key_init(&pk);
    secret_key_init(&sk);

    for (int i = 0; i < iterations; ++i) {
        unsigned char msg[32] = { 0 };
        unsigned char *rec = w->out + (size_t)i * RECORD_BYTES;

        // Derived from the indices rather than drawn from the generator, so that both runs sign identical messages
        // without consuming any of the stream being compared
        msg[0] = (unsigned char)w->index;
        msg[1] = (unsigned char)i;

        int kcheck = protocols_keygen(&pk, &sk);
        assert(kcheck);
        if (!kcheck) {
            printf("  keygen failed (thread %d, iteration %d)\n", w->index, i);
            return;
        }

        int scheck = protocols_sign(&sig, &pk, &sk, msg, sizeof(msg));
        assert(scheck);
        if (!scheck) {
            printf("  sign failed (thread %d, iteration %d)\n", w->index, i);
            return;
        }

        int vcheck = protocols_verify(&sig, &pk, msg, sizeof(msg));
        assert(vcheck);
        if (!vcheck) {
            printf("  verify failed (thread %d, iteration %d)\n", w->index, i);
            return;
        }

        secret_key_to_bytes(rec, &sk, &pk);
        signature_to_bytes(rec + SECRETKEY_BYTES, &sig);
    }

    w->ok = 1;
}

static void *
worker_main(void *arg)
{
    run_ops((worker_t *)arg);
    return NULL;
}

// Print a digest of every key and signature produced, so that reproducibility is visible.
//
// The equivalence check below compares the two runs of a single invocation; this makes the results comparable across
// invocations too. Two runs with the same --seed=, --threads= and --iterations= must print the same digest, and it
// stays the same for as long as the KATs do: compare digests freely across builds whose KATs are unchanged, and expect
// a new one whenever the KATs are regenerated.
static void
print_digest(const unsigned char *records)
{
    uint8_t digest[16];

    shake256(digest, sizeof(digest), records, (size_t)threads * iterations * RECORD_BYTES);

    printf("Result digest: ");
    for (size_t i = 0; i < sizeof(digest); i++)
        printf("%02x", digest[i]);
    printf("\n");
}

// Compare the two runs record by record, reporting the first disagreement per thread.
static int
compare_runs(const unsigned char *par, const unsigned char *ser)
{
    int res = 1;

    for (int t = 0; t < threads; ++t) {
        for (int i = 0; i < iterations; ++i) {
            size_t off = ((size_t)t * iterations + i) * RECORD_BYTES;
            int sk_differs = memcmp(par + off, ser + off, SECRETKEY_BYTES) != 0;
            int sig_differs = memcmp(par + off + SECRETKEY_BYTES, ser + off + SECRETKEY_BYTES, SIGNATURE_BYTES) != 0;

            if (sk_differs || sig_differs) {
                printf("  FAIL equivalence: thread %d, iteration %d differs (%s%s%s)\n",
                       t,
                       i,
                       sk_differs ? "key" : "",
                       (sk_differs && sig_differs) ? " and " : "",
                       sig_differs ? "signature" : "");
                res = 0;
                break;
            }
        }
    }

    return res;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int help = 0;
    int seed_set = 0;

    for (int i = 1; i < argc; i++) {
        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (sscanf(argv[i], "--iterations=%d", &iterations) == 1) {
            continue;
        }

        if (sscanf(argv[i], "--threads=%d", &threads) == 1) {
            continue;
        }
    }

    if (help || iterations <= 0 || threads <= 0) {
        printf("Usage: %s [--iterations=<iterations>] [--threads=<threads>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for testing; if not "
               "present, uses the default: %d)\n",
               iterations);
        printf("Where <threads> is the number of threads used for testing; if not "
               "present, uses the default: %d)\n",
               threads);
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

#if defined(SQISIGN_SINGLE_THREADED)
    printf("SQISIGN_SINGLE_THREADED is set, so the PRNG state is deliberately shared: skipping\n");
    return 0;
#else
    randombytes_init((unsigned char *)seed, NULL, 256);

    // One seed per thread, drawn from the seed just printed, so the whole test is reproducible
    unsigned char *worker_seeds = calloc((size_t)threads, WORKER_SEED_BYTES);
    unsigned char *par = calloc((size_t)threads * iterations, RECORD_BYTES);
    unsigned char *ser = calloc((size_t)threads * iterations, RECORD_BYTES);
    worker_t *workers = calloc((size_t)threads, sizeof(*workers));
    pthread_t *handles = (pthread_t *)calloc((size_t)threads, sizeof(pthread_t));

    if (!worker_seeds || !par || !ser || !workers || !handles) {
        printf("Allocation failed\n");
        abort();
    }

    for (int t = 0; t < threads; ++t) {
        if (randombytes(worker_seeds + (size_t)t * WORKER_SEED_BYTES, WORKER_SEED_BYTES) != 0) {
            printf("Could not draw a seed for thread %d\n", t);
            abort();
        }
    }

    bool ok = true;

    // Parallel run
    {
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setstacksize(&attr, 8 << 20); // 8 MB

        for (int t = 0; t < threads; ++t) {
            workers[t].index = t;
            workers[t].seed = worker_seeds + (size_t)t * WORKER_SEED_BYTES;
            workers[t].out = par + (size_t)t * iterations * RECORD_BYTES;

            int rc = pthread_create(&handles[t], &attr, &worker_main, &workers[t]);
            if (rc != 0) {
                printf("pthread_create failed for thread %d of %d: %s\n", t + 1, threads, strerror(rc));
                abort();
            }
        }
        pthread_attr_destroy(&attr);
    }

    for (int t = 0; t < threads; ++t) {
        pthread_join(handles[t], NULL);
        ok = ok && workers[t].ok;
    }

    if (!ok)
        printf("\nSome operations failed in the parallel run!\n");

    // Serial replay of exactly the same work, on this thread
    for (int t = 0; t < threads; ++t) {
        worker_t w = {
            t, worker_seeds + (size_t)t * WORKER_SEED_BYTES, ser + (size_t)t * iterations * RECORD_BYTES, 0
        };

        run_ops(&w);
        ok = ok && w.ok;
    }

    if (ok) {
        ok = compare_runs(par, ser);
        print_digest(ser);
    }

    free(worker_seeds);
    free(par);
    free(ser);
    free(workers);
    free((void *)handles);

    if (!ok) {
        printf("\nSome tests failed!\n");
    } else {
        printf("All tests passed!\n");
    }
    return !ok;
#endif // SQISIGN_SINGLE_THREADED
}
