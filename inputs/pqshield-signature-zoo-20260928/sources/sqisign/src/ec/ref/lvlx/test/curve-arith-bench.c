#include <bench.h>
#include <bench_test_arguments.h>
#include <assert.h>
#include <stdio.h>
#include <inttypes.h>
#include <string.h>

#include "test_extras.h"
#include <ec.h>
#include <mp_internal.h>
#include <mp.h>
#include <isog.h>
#include <rng.h>

#define STRINGIFY2(x) #x
#define STRINGIFY(x) STRINGIFY2(x)

static uint64_t
ec_bench_xDBL(unsigned int Nbench)
{
    uint64_t cycles0, cycles1;
    unsigned int i;
    ec_point_t P[Nbench], A24[Nbench];
    for (i = 0; i < Nbench; i++) {
        fp2_random_test(&(P[i].x));
        fp2_random_test(&(P[i].z));
        fp2_random_test(&(A24[i].x));
        fp2_random_test(&(A24[i].z));
    }
    cycles0 = cpucycles();
    for (i = 0; i < Nbench; i++) {
        ec_xDBL(&P[i], &P[i], &A24[i]);
    }
    cycles1 = cpucycles();
    return cycles1 - cycles0;
}

static uint64_t
ec_bench_xEVAL4(unsigned int Nbench)
{
    uint64_t cycles0, cycles1;
    unsigned int i;
    ec_point_t P[Nbench];
    ec_kps4_t KPS[Nbench];
    for (i = 0; i < Nbench; i++) {
        fp2_random_test(&(P[i].x));
        fp2_random_test(&(P[i].z));
        for (int j = 0; j < 3; j++) {
            fp2_random_test(&(KPS[i].K[j]));
        }
    }
    cycles0 = cpucycles();
    for (i = 0; i < Nbench; i++) {
        iso_xeval_4(&P[i], &P[i], 1, &KPS[i]);
    }
    cycles1 = cpucycles();
    return cycles1 - cycles0;
}

static uint64_t
ec_bench_biscalar_mul(unsigned int Nbench)
{
    uint64_t cycles0, cycles1;
    unsigned int i;
    ec_basis_t PQ[Nbench];
    ec_curve_t E[Nbench];
    ibz_t p[Nbench], q[Nbench];
    ibz_t bound = { 0 };
    memset(p, 0, sizeof(p));
    memset(q, 0, sizeof(q));
    ibz_mul_2exp(&bound, &ibz_const_one, TORSION_EVEN_POWER);
    ibz_sub(&bound, &bound, &ibz_const_one);
    ibz_set_bound(&bound, TORSION_EVEN_POWER + 1);
    for (i = 0; i < Nbench; i++) {
        fp2_random_test(&(PQ[i].P.x));
        fp2_random_test(&(PQ[i].P.z));
        fp2_random_test(&(PQ[i].Q.x));
        fp2_random_test(&(PQ[i].Q.z));
        fp2_random_test(&(PQ[i].PmQ.x));
        fp2_random_test(&(PQ[i].PmQ.z));
        fp2_random_test(&(E[i].A));
        fp2_random_test(&(E[i].C));
        ec_normalize_curve_and_A24(&E[i]);
        ibz_rand_interval(&p[i], &ibz_const_zero, &bound);
        ibz_rand_interval(&q[i], &ibz_const_zero, &bound);
    }
    cycles0 = cpucycles();
    for (i = 0; i < Nbench; i++) {
        if (!ec_biscalar_mul(&PQ[i].P, p[i].limbs, q[i].limbs, TORSION_EVEN_POWER, &PQ[i], &E[i])) {
            printf("Error returned by ec_biscalar_mul\n");
            return 1;
        }
    }
    cycles1 = cpucycles();
    return cycles1 - cycles0;
}

static uint64_t
ec_bench_biscalar_mul_verif(unsigned int Nbench)
{
    uint64_t cycles0, cycles1;
    unsigned int i;
    ec_basis_t PQ[Nbench];
    ec_curve_t E[Nbench];
    ibz_t p[Nbench], q[Nbench];
    ibz_t bound = { 0 };
    memset(p, 0, sizeof(p));
    memset(q, 0, sizeof(q));
    ibz_mul_2exp(&bound, &ibz_const_one, TORSION_EVEN_POWER);
    ibz_sub(&bound, &bound, &ibz_const_one);
    ibz_set_bound(&bound, TORSION_EVEN_POWER + 1);
    for (i = 0; i < Nbench; i++) {
        fp2_random_test(&(PQ[i].P.x));
        fp2_random_test(&(PQ[i].P.z));
        fp2_random_test(&(PQ[i].Q.x));
        fp2_random_test(&(PQ[i].Q.z));
        fp2_random_test(&(PQ[i].PmQ.x));
        fp2_random_test(&(PQ[i].PmQ.z));
        fp2_random_test(&(E[i].A));
        fp2_random_test(&(E[i].C));
        ec_normalize_curve_and_A24(&E[i]);
        ibz_rand_interval(&p[i], &ibz_const_zero, &bound);
        ibz_rand_interval(&q[i], &ibz_const_zero, &bound);
    }
    cycles0 = cpucycles();
    for (i = 0; i < Nbench; i++) {
        if (!ec_biscalar_mul_verif(&PQ[i].P, p[i].limbs, q[i].limbs, TORSION_EVEN_POWER, &PQ[i], &E[i])) {
            printf("Error returned by ec_biscalar_mul\n");
            return 1;
        }
    }
    cycles1 = cpucycles();
    return cycles1 - cycles0;
}

static uint64_t
ec_bench_isog_strategy(unsigned int Nbench)
{
    uint64_t cycles0, cycles1;
    unsigned int i;
    ec_curve_t E0;
    ec_isog_even_t phi[Nbench];
    ec_basis_t basis2;
    ec_curve_init(&E0);
    fp2_set_small(&(E0.A), 6);
    fp2_set_one(&(E0.C));
    (void)ec_curve_to_basis_2f_to_hint(&basis2, &E0, TORSION_EVEN_POWER, 0);
    for (i = 0; i < Nbench; i++) {
        ec_copy_curve(&phi[i].curve, &E0);
        phi[i].length = TORSION_EVEN_POWER;
        if (i == 0) {
            ec_xADD(&phi[i].kernel, &basis2.P, &basis2.Q, &basis2.PmQ);
        }
        if (i == 1) {
            ec_xADD(&phi[i].kernel, &phi[i - 1].kernel, &basis2.Q, &basis2.P);
        }
        if (i > 1) {
            ec_xADD(&phi[i].kernel, &phi[i - 1].kernel, &basis2.Q, &phi[i - 2].kernel);
        }
    }
    cycles0 = cpucycles();
    for (i = 2; i < Nbench; i++) {
        if (iso_isogeny_2chain(&phi[i].curve, &phi[i])) {
            printf("Failed isogeny strategy\n");
            return 0;
        }
    }
    cycles1 = cpucycles();
    return cycles1 - cycles0;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int iterations = 100 * SQISIGN_TEST_REPS;
    int help = 0;
    int seed_set = 0;

#ifndef NDEBUG
    fprintf(stderr,
            "\x1b[31mIt looks like SQIsign was compiled with assertions enabled.\n"
            "This will severely impact performance measurements.\x1b[0m\n");
#endif

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
    }

    if (help || iterations <= 0) {
        printf("Usage: %s [--iterations=<iterations>] [--seed=<seed>]\n", argv[0]);
        printf("Where <iterations> is the number of iterations used for benchmarking; if not "
               "present, uses the default: %d)\n",
               iterations);
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
    if (init_test_rng(seed) != 0) {
        return 1;
    }
    cpucycles_init();

    printf("Benchmarking elliptic curve arithmetic for " STRINGIFY(SQISIGN_VARIANT) ":\n\n");

    uint64_t cycles;

    cycles = ec_bench_xDBL(10 * iterations);
    printf("Bench xDBL_A24:\t%" PRIu64 " cycles\n", cycles / (10 * iterations));

    cycles = ec_bench_xEVAL4(iterations);
    printf("Bench xEVAL4:\t%" PRIu64 " cycles\n", cycles / iterations);

    cycles = ec_bench_isog_strategy(iterations);
    printf("Bench isog strategy:\t%" PRIu64 " cycles\n", cycles / iterations);

    cycles = ec_bench_biscalar_mul(iterations);
    printf("Bench ec biscalar mul:\t%" PRIu64 " cycles\n", cycles / iterations);

    cycles = ec_bench_biscalar_mul_verif(iterations);
    printf("Bench ec biscalar mul verif:\t%" PRIu64 " cycles\n", cycles / iterations);

    return 0;
}
