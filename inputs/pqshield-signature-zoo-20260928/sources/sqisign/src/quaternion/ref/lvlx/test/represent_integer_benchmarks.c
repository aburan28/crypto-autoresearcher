#include <bench.h>
#include <bench_test_arguments.h>
#include <rng.h>
#include <quaternion_data.h>
#include <quaternion_constants.h>
#include <internal.h>

#define STRINGIFY2(x) #x
#define STRINGIFY(x) STRINGIFY2(x)

// return 0 if ok, anything else if error
// sample array of odd numbers
int
quat_bench_represent_integer_benchmarks_input_generation(ibz_t *n_gammas, int bitsize, int iterations)
{
    int randret = 1;
    ibz_t max;
    ibz_init(&max);
    ibz_mul_2exp(&max, &ibz_const_one, bitsize - 1);
    for (int i = 0; i < iterations; i++) {
        randret = randret && ibz_rand_interval(&(n_gammas[i]), &ibz_const_one, &max);
        ibz_mul(&(n_gammas[i]), &ibz_const_two, &(n_gammas[i]));
        ibz_add(&(n_gammas[i]), &ibz_const_one, &(n_gammas[i]));
    }
    return (!randret);
}

// 0 if ok, 1 otherwise
int
quat_bench_represent_integer_benchmarks_test(const quat_alg_elem_t *gamma, const ibz_t *n_gamma)
{
    ibz_vec_4_t coord;
    ibz_t norm_d, norm_n;
    ibz_init(&norm_d);
    ibz_init(&norm_n);
    ibz_vec_4_init(&coord);
    int res = 0;
    quat_alg_norm(&norm_n, &norm_d, gamma, &QUATALG_PINFTY);
    res = res || !ibz_is_one(&norm_d);
    res = res || !(ibz_cmp(&norm_n, n_gamma) == 0);
    res = res || !quat_lattice_contains(NULL, &MAXORD_O0, gamma);
    return (res);
}

int
quat_bench_represent_integer_benchmarks(int bitsize, int iterations, int test)
{
    int res = 0;
    int randret = 0;
    uint64_t start, end, sum;
    ibz_t *n_gammas;
    ibz_t aux;
    quat_alg_elem_t *gammas;
    n_gammas = malloc(iterations * sizeof(ibz_t));
    gammas = malloc(iterations * sizeof(quat_alg_elem_t));
    for (int i = 0; i < iterations; i++) {
        ibz_init(&(n_gammas[i]));
        quat_alg_elem_init(&(gammas[i]));
    }
    ibz_init(&aux);

    printf(
        "Running represent_integer benchmarks for " STRINGIFY(
            SQISIGN_VARIANT) " with %d iterations, inputs of bitsize %d, %d-bit prime and %d-round primality tests\n",
        iterations,
        bitsize,
        ibz_bitsize(&QUATALG_PINFTY.p),
        QUAT_primality_num_iter);
    if (test) {
        printf("Tests are run on the outputs\n");
    }

    // adjust bitsize
    ibz_set(&aux, 1, 2);
    int bitsize_adjustment = ibz_bitsize(&aux);

    randret = randret || quat_bench_represent_integer_benchmarks_input_generation(
                             n_gammas, bitsize + bitsize_adjustment, iterations);

    if (randret)
        goto randomness_failure;

    sum = 0;
    for (int iter = 0; iter < iterations; iter++) {
        start = cpucycles();
        res = res | !quat_represent_integer(&(gammas[iter]), &(n_gammas[iter]), &PRNG_default_domain);
        end = cpucycles();
        sum = sum + end - start;
    }

    printf("RepresentInteger took %" PRIu64 " cycles on average per iteration (adjusted bitsize %d)\n",
           sum / iterations,
           bitsize + bitsize_adjustment);
    if (test) {
        for (int iter = 0; iter < iterations; iter++) {
            res = res || quat_bench_represent_integer_benchmarks_test(&(gammas[iter]), &(n_gammas[iter]));
        }
    }
randomness_failure:;
    if (randret)
        printf("Randomness failure in quat_bench_represent_integer_benchmarks\n");

    if (res) {
        printf("Tests in quat_bench_represent_integer_benchmarks failed\n");
    }
    free(n_gammas);
    free(gammas);

    return (res | 2 * randret);
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12];
    int iterations = 100;
    int help = 0;
    int seed_set = 0;
    int tests = 0;
    int bitsize = 0;
    int invalid = 0;

#ifndef NDEBUG
    fprintf(stderr,
            "\x1b[31mIt looks like SQIsign was compiled with assertions enabled.\n"
            "This will severely impact performance measurements.\x1b[0m\n");
#endif

    for (int i = 1; i < argc; i++) {
        if (!tests && strcmp(argv[i], "--tests") == 0) {
            tests = 1;
            continue;
        }

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

        if (sscanf(argv[i], "--bitsize=%d", &bitsize) == 1) {
            continue;
        }
    }

    invalid = invalid || (argc > 6);
    invalid = invalid || (iterations < 0);
    invalid = invalid || !((bitsize == 0) || (bitsize >= ibz_bitsize(&QUATALG_PINFTY.p) + 20));

    if (help || invalid) {
        if (invalid) {
            printf("Invalid input\n");
        }
        printf("Usage: %s [--bitsize=<bitsize>] [--iterations=<iterations>] [--tests] [--seed=<seed>]\n", argv[0]);
        printf("Where <bitsize> is least 20 higher than the bitsize of the prime used in the "
               "algebra(which depends on the level); if no present, uses a level-dependet default;\n");
        printf("Where <iterations> is the number of iterations used for benchmarking; if not "
               "present, uses the default: %d)\n",
               iterations);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is "
               "generated\n");
        printf("Additional verifications are run on each output if --tests is passed\n");
        printf("Output has last bit set if tests failed, second-to-last if randomness failed\n");
        return (1);
    }

    if (bitsize == 0) {
        bitsize = ibz_bitsize(&QUATALG_PINFTY.p) + 25;
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

    return (quat_bench_represent_integer_benchmarks(bitsize, iterations, tests));
}
