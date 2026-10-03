// SPDX-License-Identifier: Apache-2.0

/** @file
 *
 * @brief Unit tests for the thread-locality of the AES-CTR-DRBG randombytes().
 *
 * Links sqisign_common_test, so randombytes() here is the deterministic NIST CTR-DRBG rather than the system RNG. The
 * contract under test (see rng.h) is that its state has thread storage duration, which gives two properties:
 *
 *   - a thread that calls randombytes_init() produces exactly the stream a single-threaded program with that seed would
 *     produce, no matter what other threads are doing;
 *   - a thread that does not call randombytes_init() draws from the zeroed initial state.
 *
 * sqisign_test_threadsafety proves the same thing end to end through keygen/sign/verify, but this test pins the RNG
 * contract at the RNG, in milliseconds.
 */

#include <rng.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if defined(SQISIGN_SINGLE_THREADED)

int
main(void)
{
    printf("SQISIGN_SINGLE_THREADED is set, so the DRBG state is deliberately shared: skipping\n");
    return 0;
}

#else

#include <pthread.h>

#define NTHREADS 4
#define SEED_BYTES 48
#define DRAW_BYTES 64 // > one 16-byte AES block, so a draw spans several DRBG generate steps

typedef struct
{
    unsigned char seed[SEED_BYTES];
    int seed_it; // 0 to skip randombytes_init() and exercise the zeroed initial state
    unsigned char out[DRAW_BYTES];
} worker_t;

// Distinct, and deliberately not all-zero so that a seed left memset would not pass for a real one
static void
fill_seed(unsigned char *seed, int index)
{
    for (int i = 0; i < SEED_BYTES; i++)
        seed[i] = (unsigned char)(0xa5 ^ (index * SEED_BYTES + i));
}

static void *
worker_main(void *arg)
{
    worker_t *w = arg;

    if (w->seed_it)
        randombytes_init(w->seed, NULL, 256);
    randombytes(w->out, DRAW_BYTES);

    return NULL;
}

// Runs one worker to completion on a thread of its own. Used for the reference draws too, so that every draw in this
// file starts from a generator no other draw has touched.
static int
run_on_own_thread(worker_t *w)
{
    pthread_t handle;

    if (pthread_create(&handle, NULL, &worker_main, w) != 0)
        return 0;

    return pthread_join(handle, NULL) == 0;
}

// Each thread's concurrent draw must equal the draw it makes when running alone.
static int
test_streams_match_sequential(const worker_t *seq, const worker_t *par)
{
    int res = 1;

    for (int i = 0; i < NTHREADS; i++) {
        if (memcmp(seq[i].out, par[i].out, DRAW_BYTES) != 0) {
            printf("  FAIL thread-local streams: thread %d differs between the sequential and concurrent runs\n", i);
            res = 0;
        }
    }

    return res;
}

// Distinct seeds must give distinct streams, i.e. the threads are not sharing a generator.
static int
test_streams_are_distinct(const worker_t *w)
{
    int res = 1;

    for (int i = 0; i < NTHREADS; i++) {
        unsigned char zero[DRAW_BYTES] = { 0 };

        if (memcmp(w[i].out, zero, DRAW_BYTES) == 0) {
            printf("  FAIL distinct streams: thread %d produced all zeros\n", i);
            res = 0;
        }

        for (int j = i + 1; j < NTHREADS; j++) {
            if (memcmp(w[i].out, w[j].out, DRAW_BYTES) == 0) {
                printf("  FAIL distinct streams: threads %d and %d produced the same bytes\n", i, j);
                res = 0;
            }
        }
    }

    return res;
}

// An uninitialized thread must draw from the zeroed generator state, reproducibly.
static int
test_uninitialized_thread_is_deterministic(void)
{
    worker_t a = { { 0 }, 0, { 0 } }, b = { { 0 }, 0, { 0 } };
    unsigned char zero[DRAW_BYTES] = { 0 };

    if (!run_on_own_thread(&a) || !run_on_own_thread(&b)) {
        printf("  FAIL uninitialized thread: could not run workers\n");
        return 0;
    }

    if (memcmp(a.out, b.out, DRAW_BYTES) != 0) {
        printf("  FAIL uninitialized thread: two unseeded threads disagree\n");
        return 0;
    }

    // The DRBG encrypts under an all-zero key, but its output must not itself be zeros
    if (memcmp(a.out, zero, DRAW_BYTES) == 0) {
        printf("  FAIL uninitialized thread: output is all zeros\n");
        return 0;
    }

    return 1;
}

int
main(void)
{
    worker_t seq[NTHREADS] = { 0 }, par[NTHREADS] = { 0 };
    pthread_t handles[NTHREADS];
    int res = 1;

    printf("Running CTR-DRBG thread-locality tests\n");

    for (int i = 0; i < NTHREADS; i++) {
        fill_seed(seq[i].seed, i);
        seq[i].seed_it = 1;
        memcpy(&par[i], &seq[i], sizeof(par[i]));
    }

    // Reference: each seed drawn alone, one thread at a time
    for (int i = 0; i < NTHREADS; i++) {
        if (!run_on_own_thread(&seq[i])) {
            printf("  FAIL reference run: could not run worker %d\n", i);
            return 1;
        }
    }

    // The same seeds again, this time all in flight at once
    for (int i = 0; i < NTHREADS; i++) {
        if (pthread_create(&handles[i], NULL, &worker_main, &par[i]) != 0) {
            printf("  FAIL concurrent run: could not create thread %d\n", i);
            return 1;
        }
    }
    for (int i = 0; i < NTHREADS; i++)
        pthread_join(handles[i], NULL);

    res &= test_streams_match_sequential(seq, par);
    res &= test_streams_are_distinct(par);
    res &= test_uninitialized_thread_is_deterministic();

    if (!res) {
        printf("CTR-DRBG thread-locality tests failed\n");
        return 1;
    }

    printf("CTR-DRBG thread-locality tests passed\n");

    return 0;
}

#endif /* SQISIGN_SINGLE_THREADED */
