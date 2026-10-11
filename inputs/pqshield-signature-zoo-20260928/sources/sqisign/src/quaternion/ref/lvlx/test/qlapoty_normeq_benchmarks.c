#include <bench.h>
#include <bench_test_arguments.h>
#include <quaternion_tests.h>
#include <rng.h>
#include <prng.h>
#include <quaternion_constants.h>
#include <quaternion_data.h>
#include <torsion_constants.h>
#include "internal.h"

#define STRINGIFY2(x) #x
#define STRINGIFY(x) STRINGIFY2(x)

int
quat_bench_qlapoty_benchmarks(int iterations)
{
    int res = 0;
    int randret = 0;
    int warmup = 100;
    int two_power = QUAT_qlapoty_used_power_of_two;
    int iter_prime = QUAT_primality_num_iter;
    int bitsize = ibz_bitsize(&(QUATALG_PINFTY.p)) * 2;
    uint64_t start, end, sum;
    quat_ideal_t *ideals;
    quat_alg_elem_t *mu1s, *mu2s, *thetas, *smalls;
    ideals = malloc((warmup + iterations) * sizeof(quat_ideal_t));
    mu1s = malloc((warmup + iterations) * sizeof(quat_alg_elem_t));
    mu2s = malloc((warmup + iterations) * sizeof(quat_alg_elem_t));
    thetas = malloc((warmup + iterations) * sizeof(quat_alg_elem_t));
    smalls = malloc((warmup + iterations) * sizeof(quat_alg_elem_t));
    for (int i = 0; i < (warmup + iterations); i++) {
        quat_ideal_init(&(ideals[i]));
        quat_alg_elem_init(&(mu1s[i]));
        quat_alg_elem_init(&(mu2s[i]));
        quat_alg_elem_init(&(thetas[i]));
        quat_alg_elem_init(&(smalls[i]));
    }

    printf("Running qlapoty_normeq benchmarks with %d iterations, inputs of bitsize %d, "
           "%d-round primality tests and a %d-bit target\n",
           iterations,
           bitsize,
           iter_prime,
           two_power);

    randret = randret || quat_test_input_random_ideal_generation(ideals, bitsize, iterations + warmup);

    if (randret)
        goto cleanup;

    for (int iter = 0; iter < warmup; iter++) {
        res =
            res | !quat_qlapoty_normeq(&(mu1s[iter]), &(mu2s[iter]), &(thetas[iter]), &(smalls[iter]), &(ideals[iter]));
    }
    sum = 0;
    for (int iter = warmup; iter < iterations + warmup; iter++) {
        start = cpucycles();
        res =
            res | !quat_qlapoty_normeq(&(mu1s[iter]), &(mu2s[iter]), &(thetas[iter]), &(smalls[iter]), &(ideals[iter]));
        end = cpucycles();
        sum = sum + end - start;
    }

    printf("Qlapoty took %" PRIu64 " cycles on average per iteration\n", sum / iterations);
cleanup:;
    if (randret)
        printf("Randomness failure in quat_bench_qlapoty_normeq_benchmarks\n");

    free(mu1s);
    free(mu2s);
    free(smalls);
    free(thetas);
    free(ideals);
    return (randret);
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12];
    int iterations = 100;
    int help = 0;
    int seed_set = 0;
    int invalid = 0;

#ifndef NDEBUG
    fprintf(stderr,
            "\x1b[31mIt looks like SQIsign was compiled with assertions enabled.\n"
            "This will severely impact performance measurements.\x1b[0m\n");
#endif

    for (int i = 1; i < argc; i++) {
        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (sscanf(argv[i], "--iterations=%d", &iterations) == 1) {
            continue;
        }
    }

    invalid = invalid || (argc > 3);
    invalid = invalid || (iterations < 0);

    if (help || invalid) {
        if (invalid) {
            printf("Invalid input\n");
        }
        printf("Usage: %s [--iterations=<iterations>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for benchmarking; if not present, uses the "
               "default: %d)\n",
               iterations);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is generated\n");
        printf("last bit set if randomness failed\n");
        return (1);
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

    if (init_test_rng(seed) != 0)
        return (1);
    cpucycles_init();
    return (quat_bench_qlapoty_benchmarks(iterations));
}
