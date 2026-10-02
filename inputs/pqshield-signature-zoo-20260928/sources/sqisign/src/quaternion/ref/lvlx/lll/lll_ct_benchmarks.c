/** @file
 *
 * @brief Benchmarks for the constant-time lattice reduction entry points.
 *
 * Times what SQIsign actually calls, both entry points of lll/lll_applications.c:
 *
 *   quat_ideal_reduce_basis           rank-2 Z[i] reduction of an O0-ideal
 *   quat_lattice_bound_parallelogram  dual dimension-4 reduction of a product lattice
 *
 * Inputs come from the generators in test/random_input_generation.c, at the sizes the signing
 * path actually produces.
 */

#include "quaternion_tests.h"
#include <rng.h>
#include <bench.h>
#include <bench_test_arguments.h>
#include <quaternion_data.h>
#include <torsion_constants.h>
#include <encoded_sizes.h>
#include <inttypes.h>

#define BENCH_PRIMALITY_ITERS 30
#define BENCH_WARMUPS 5

static void
report(const char *what, const char *models, uint64_t ct)
{
    printf("  %-34s %-22s CT %10" PRIu64 "\n", what, models, ct);
}

/** @brief Time quat_ideal_reduce_basis on `iterations` random O0-ideals of prime norm.
 *
 * `ideals` must hold BENCH_WARMUPS + iterations initialized entries.
 */
static int
quat_bench_ct_reduce_basis(int norm_bitsize, int iterations, quat_ideal_t *ideals, const char *models)
{
    int res = 0;
    uint64_t start, end, ct_cycles;
    char what[64];
    quat_lattice_t red;
    quat_lattice_init(&red);

    for (int i = 0; i < BENCH_WARMUPS + iterations; i++) {
        int vbits = ibz_bitsize(&(ideals[i].norm));
        assert(vbits <= norm_bitsize + 1);
        ibz_set_bound(&(ideals[i].norm), vbits + 1);
        assert(ibz_get_bound(&(ideals[i].norm)) == vbits + 1);
    }

    for (int i = 0; i < BENCH_WARMUPS; i++)
        quat_ideal_reduce_basis(&red, &(ideals[i]));

    start = cpucycles();
    for (int i = BENCH_WARMUPS; i < BENCH_WARMUPS + iterations; i++)
        quat_ideal_reduce_basis(&red, &(ideals[i]));
    end = cpucycles();
    ct_cycles = (end - start) / (uint64_t)iterations;

    snprintf(what, sizeof(what), "reduce_basis, %d-bit norms", norm_bitsize);
    report(what, models, ct_cycles);
    return (res);
}

/** @brief Time quat_lattice_bound_parallelogram on `iterations` product lattices.
 *
 * `lats` must hold BENCH_WARMUPS + iterations initialized entries, as emitted by
 * quat_test_input_resplike_lattice_generation -- two prime-norm O0-ideals fed to
 * quat_ideal_mul_O0, which is the shape quat_response_element produces.
 */
static int
quat_bench_ct_parallelogram(int bitsize, int iterations, quat_lattice_t *lats, const char *models)
{
    int res = 0;
    int trivial = 0;
    uint64_t start, end, ct_cycles;
    char what[64];
    ibz_vec_4_t box;
    ibz_mat_4x4_t U;
    ibz_t rad;
    ibz_vec_4_init(&box);
    ibz_mat_4x4_init(&U);
    ibz_init(&rad);

    // quat_lattice_sample_from_ball passes 2 * radius, and sign.c passes
    // radius = 2^RESPONSE_BITS - 1. Reproduce both steps.
    ibz_mul_2exp(&rad, &ibz_const_one, RESPONSE_BITS);
    ibz_sub(&rad, &rad, &ibz_const_one);
    ibz_set_bound(&rad, RESPONSE_BITS + 1);
    ibz_mul_2exp(&rad, &rad, 1);

    for (int i = 0; i < BENCH_WARMUPS; i++)
        quat_lattice_bound_parallelogram(&box, &U, &(lats[i]), &rad);

    start = cpucycles();
    for (int i = BENCH_WARMUPS; i < BENCH_WARMUPS + iterations; i++)
        trivial += !quat_lattice_bound_parallelogram(&box, &U, &(lats[i]), &rad);
    end = cpucycles();
    ct_cycles = (end - start) / (uint64_t)iterations;

    snprintf(what, sizeof(what), "parallelogram, %d-bit lat", bitsize);
    report(what, models, ct_cycles);
    if (trivial != 0) {
        printf("    warning: %d of %d boxes were trivial (radius too small for these lattices)\n", trivial, iterations);
        res = 1;
    }
    return (res);
}

/** @brief Run both benchmarks for the compiled level. */
static int
quat_bench_ct_level(int iterations)
{
    int res = 0;
    int randret = 0;
    int total = BENCH_WARMUPS + iterations;
    int pbits = ibz_bitsize(&QUATALG_PINFTY.p);
    quat_ideal_t *ideals;
    quat_lattice_t *lats;

    // The three production callers of quat_ideal_reduce_basis see two norm scales: the
    // secret/commitment degree (new.c, via keygen.c and sign.c) and the sqrt(p)-scale ideals of
    // the response and shortest-equivalent paths.
    int sec_bits = ibz_bitsize(&SEC_DEGREE);
    int resp_bits = pbits / 2 + 15;
    // Site #4's lattice is a product of two ideals of resp_bits each, giving bits(2N) just above
    // 2 * resp_bits -- the size measured on the signing path.
    int prod_bits = 2 * resp_bits;

    ideals = calloc(total, sizeof(quat_ideal_t));
    lats = calloc(total, sizeof(quat_lattice_t));
    if (!ideals || !lats)
        abort();
    for (int i = 0; i < total; i++) {
        quat_ideal_init(&(ideals[i]));
        quat_lattice_init(&(lats[i]));
    }

    printf(
        "CT lattice reduction benchmarks: %d-bit prime, %d iterations, %d warmups\n", pbits, iterations, BENCH_WARMUPS);
    printf("Response length %d bits, secret/commitment degree %d bits\n\n", RESPONSE_BITS, sec_bits);

    randret = quat_test_input_random_ideal_generation(ideals, sec_bits, total);
    if (randret)
        goto fin;
    res |= quat_bench_ct_reduce_basis(sec_bits, iterations, ideals, "keygen/commit");

    randret = quat_test_input_random_ideal_generation(ideals, resp_bits, total);
    if (randret)
        goto fin;
    res |= quat_bench_ct_reduce_basis(resp_bits, iterations, ideals, "response/shortest-eq");

    randret = quat_test_input_resplike_lattice_generation(lats, NULL, prod_bits, total);
    if (randret)
        goto fin;
    res |= quat_bench_ct_parallelogram(prod_bits, iterations, lats, "response");

fin:;
    if (randret)
        printf("Randomness failure in quat_bench_ct_level\n");
    for (int i = 0; i < total; i++) {
    }
    free(ideals);
    free(lats);
    return (res + 2 * randret);
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int iterations = 20;
    int help = 0;
    int seed_set = 0;

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

    if (help || iterations <= 0) {
        printf("Usage: %s [--iterations=<iterations>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for benchmarking; if not "
               "present, uses the default: %d\n",
               iterations);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is generated\n");
        printf("There is no --level flag: the CT reduction is only valid for the compiled level's prime\n");
        printf("last bit set if randomness failed\n");
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

    if (init_test_rng(seed) != 0)
        return 1;
    cpucycles_init();

    return quat_bench_ct_level(iterations);
}
