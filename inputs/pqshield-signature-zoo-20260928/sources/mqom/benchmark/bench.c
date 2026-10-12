#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#include "timing.h"
#include "utils.h"
#include "api.h"
#include "benchmark.h"
#include "stack_measure.h"

#define B_KEY_GENERATION 0
#define B_SIGN_ALGO 1
#define B_VERIFY_ALGO 2
#define NUMBER_OF_ALGO_BENCHES 3

/* Welford's online algorithm: numerically stable single-pass mean/variance */
typedef struct {
	double count;
	double mean;
	double m2;
} welford_t;

static inline void welford_init(welford_t *w) {
	w->count = 0.0;
	w->mean = 0.0;
	w->m2 = 0.0;
}

static inline void welford_update(welford_t *w, double x) {
	double delta, delta2;
	w->count += 1.0;
	delta = x - w->mean;
	w->mean += delta / w->count;
	delta2 = x - w->mean;
	w->m2 += delta * delta2;
}

/* Population standard deviation (matches the sqrt(E[X^2]-E[X]^2) semantics
 * this replaces). */
static inline double welford_std(const welford_t *w) {
	if (w->count < 1.0) {
		return 0.0;
	}
	return sqrt(w->m2 / w->count);
}

#ifdef BENCHMARK_GRINDING
/* Population variance. */
static inline double welford_var(const welford_t *w) {
	if (w->count < 1.0) {
		return 0.0;
	}
	return w->m2 / w->count;
}

/* Paired online covariance accumulator (same idea as welford_t, extended to
 * two variables): fits a linear model of Sign() cost vs grinding trial
 * count via cost_per_trial = Cov(trials, cost) / Var(trials), the standard
 * least-squares slope. Uses every sample collected this run, not just two
 * points: the slope from N paired samples is effectively an average over
 * all pairwise slopes, far less noisy than any single two-point estimate. */
typedef struct {
	double count;
	double mean_x;
	double mean_y;
	double c_xy;
} covacc_t;

static inline void covacc_init(covacc_t *c) {
	c->count = 0.0;
	c->mean_x = 0.0;
	c->mean_y = 0.0;
	c->c_xy = 0.0;
}

static inline void covacc_update(covacc_t *c, double x, double y) {
	double dx;
	c->count += 1.0;
	dx = x - c->mean_x;
	c->mean_x += dx / c->count;
	c->mean_y += (y - c->mean_y) / c->count;
	c->c_xy += dx * (y - c->mean_y);
}

static inline double covacc_cov(const covacc_t *c) {
	if (c->count < 1.0) {
		return 0.0;
	}
	return c->c_xy / c->count;
}
#endif /* BENCHMARK_GRINDING */

/* ---- per-operation wrappers for stack_measure_run ---- */
#ifdef MEASURE_STACK
typedef struct { uint8_t *pk; uint8_t *sk; } _sm_keygen_args_t;
typedef struct {
    uint8_t            *sm;
    unsigned long long *smlen;
    const uint8_t      *m;
    unsigned long long  mlen;
    const uint8_t      *sk;
} _sm_sign_args_t;
typedef struct {
    uint8_t            *m2;
    unsigned long long *m2len;
    const uint8_t      *sm;
    unsigned long long  smlen;
    const uint8_t      *pk;
} _sm_verify_args_t;

static void _sm_run_keygen(void *arg) {
    _sm_keygen_args_t *a = (_sm_keygen_args_t *)arg;
    crypto_sign_keypair(a->pk, a->sk);
}
static void _sm_run_sign(void *arg) {
    _sm_sign_args_t *a = (_sm_sign_args_t *)arg;
    crypto_sign(a->sm, a->smlen, a->m, a->mlen, a->sk);
}
static void _sm_run_verify(void *arg) {
    _sm_verify_args_t *a = (_sm_verify_args_t *)arg;
    crypto_sign_open(a->m2, a->m2len, a->sm, a->smlen, a->pk);
}
#endif /* MEASURE_STACK */
/* ---- end wrappers ---- */

int randombytes(unsigned char* x, unsigned long long xlen) {
	for (unsigned long long j = 0; j < xlen; j++) {
		x[j] = (uint8_t) rand();
	}
	return 0;
}

#ifdef BENCHMARK
btimer_t timers[NUMBER_OF_BENCHES];

#ifdef BENCHMARK_CYCLES
#define display_timer(label,num) printf("   - " label ": %f ms (%f cycles)\n", btimer_get(&timers[num]), btimer_get_cycles(&timers[num]))
#else
#define display_timer(label,num) printf("   - " label ": %f ms\n", btimer_get(&timers[num]))
#endif
#endif

int main(int argc, char *argv[]) {
	srand((unsigned int) time(NULL));

	int nb_tests = get_number_of_tests(argc, argv, 1);
	if (nb_tests < 0) {
		exit(EXIT_FAILURE);
	}

	print_configuration();
	printf("\n");

	btimer_t timers_algos[NUMBER_OF_ALGO_BENCHES];

	// Initialisation
	welford_t wf_timer[NUMBER_OF_ALGO_BENCHES];
	for (int j = 0; j < NUMBER_OF_ALGO_BENCHES; j++) {
		btimer_init(&timers_algos[j]);
		welford_init(&wf_timer[j]);
	}
#ifdef BENCHMARK
	for (int num = 0; num < NUMBER_OF_BENCHES; num++) {
		btimer_init(&timers[num]);
	}
#endif
	welford_t wf_sig_size;
	welford_init(&wf_sig_size);
#ifdef BENCHMARK_GRINDING
	/* Grinding trial count per signature, extracted from the produced nonce
	 * (sm = m || sig_id[DIGEST_SIZE] | salt[SALT_SIZE] | nonce[4] | ...):
	 * nonces are tried sequentially from 0, so nonce_value + 1 = number of
	 * grinding trials for that signature. Independent of BENCHMARK/timing. */
	welford_t wf_grind;
	welford_init(&wf_grind);
	/* Paired with per-iteration Sign() wall-clock time to fit an actual
	 * measured cost-per-trial via linear regression - see the "Grinding
	 * statistics" summary block below. (Cycles are derived from this ms fit
	 * rather than regressed directly: raw per-iteration RDPMC reads are too
	 * jittery at that granularity, see the comment there.) */
	covacc_t cov_ms_trials;
	covacc_init(&cov_ms_trials);
#endif /* BENCHMARK_GRINDING */

	// Execution
	int score = 0;
	int ret;
	for (int i = 0; i < nb_tests; i++) {
#ifdef BENCHMARK
		for (int num = 0; num < NUMBER_OF_BENCHES; num++) {
			btimer_count(&timers[num]);
		}
#endif

		// Generate the keys
		uint8_t pk[CRYPTO_PUBLICKEYBYTES];
		uint8_t sk[CRYPTO_SECRETKEYBYTES];
		btimer_start(&timers_algos[B_KEY_GENERATION]);
		ret = crypto_sign_keypair(pk, sk);
		btimer_end(&timers_algos[B_KEY_GENERATION]);
		btimer_count(&timers_algos[B_KEY_GENERATION]);
		welford_update(&wf_timer[B_KEY_GENERATION], btimer_diff(&timers_algos[B_KEY_GENERATION]));
		if (ret) {
			printf("Failure (num %d): crypto_sign_keypair\n", i);
			continue;
		}

		// Select the message
#define MLEN 32
		uint8_t m[MLEN] = {1, 2, 3, 4};
		uint8_t m2[MLEN] = {0};
		unsigned long long m2len = 0;

		// Sign the message
		uint8_t sm[MLEN + CRYPTO_BYTES];
		unsigned long long smlen = 0;
		btimer_start(&timers_algos[B_SIGN_ALGO]);
		ret = crypto_sign(sm, &smlen, m, MLEN, sk);
		btimer_end(&timers_algos[B_SIGN_ALGO]);
		btimer_count(&timers_algos[B_SIGN_ALGO]);
		double sign_ms = btimer_diff(&timers_algos[B_SIGN_ALGO]);
		welford_update(&wf_timer[B_SIGN_ALGO], sign_ms);
		// Update statistics
		size_t signature_len = smlen - MLEN;
		welford_update(&wf_sig_size, (double) signature_len);
		if (ret) {
			printf("Failure (num %d): crypto_sign\n", i);
			continue;
		}

#ifdef BENCHMARK_GRINDING
		{
			const uint8_t *_nonce_bytes = &sm[MLEN + MQOM3_PARAM_DIGEST_SIZE + MQOM3_PARAM_SALT_SIZE];
			uint32_t _nonce = (uint32_t) _nonce_bytes[0]
			                 | ((uint32_t) _nonce_bytes[1] << 8)
			                 | ((uint32_t) _nonce_bytes[2] << 16)
			                 | ((uint32_t) _nonce_bytes[3] << 24);
			double trial_count = (double) _nonce + 1.0;
			welford_update(&wf_grind, trial_count);
			covacc_update(&cov_ms_trials, trial_count, sign_ms);
		}
#endif /* BENCHMARK_GRINDING */

		// Verify/Open the signature
		btimer_start(&timers_algos[B_VERIFY_ALGO]);
		ret = crypto_sign_open(m2, &m2len, sm, smlen, pk);
		btimer_end(&timers_algos[B_VERIFY_ALGO]);
		btimer_count(&timers_algos[B_VERIFY_ALGO]);
		welford_update(&wf_timer[B_VERIFY_ALGO], btimer_diff(&timers_algos[B_VERIFY_ALGO]));
		if (ret) {
			printf("Failure (num %d): crypto_sign_open\n", i);
			continue;
		}

		// Test of correction of the primitives
		if (m2len != MLEN) {
			printf("Failure (num %d): message size does not match\n", i);
			continue;
		}
		{
			int mismatch = -1;
			for (int h = 0; h < MLEN; h++) {
				if (m[h] != m2[h]) {
					mismatch = h;
					break;
				}
			}
			if (mismatch >= 0) {
				printf("Failure (num %d): message does not match (char %d)\n", i, mismatch);
				continue;
			}
		}

		score++;
	}

	// Compute some statistics
	double std_timer[NUMBER_OF_ALGO_BENCHES];
	std_timer[B_KEY_GENERATION] = welford_std(&wf_timer[B_KEY_GENERATION]);
	std_timer[B_SIGN_ALGO] = welford_std(&wf_timer[B_SIGN_ALGO]);
	std_timer[B_VERIFY_ALGO] = welford_std(&wf_timer[B_VERIFY_ALGO]);
	double mean_of_sig_size = wf_sig_size.mean;
	double std_sig_size = welford_std(&wf_sig_size);

	// Display Infos
	printf("===== SUMMARY =====\n");
	printf("Correctness: %d/%d\n", score, nb_tests);
	printf("\n");

	printf("Parameters:\n");
	printf(" - Variant:  %s\n", MQOM3_PARAM_LABEL);
	printf(" - lambda=%d, N=%d (2^%d), tau=%d, w=%d, eta=%d\n",
	       MQOM3_PARAM_SECURITY,
	       MQOM3_PARAM_NB_EVALS,
	       MQOM3_PARAM_NB_EVALS_LOG,
	       MQOM3_PARAM_TAU,
	       MQOM3_PARAM_W,
	       MQOM3_PARAM_ETA);
#if MQOM3_PARAM_OT_VARIANT == 1
	printf(" - OT: Topen=%d, H=%d\n",
	       MQOM3_PARAM_LARGE_GGM_T_OPEN,
	       MQOM3_PARAM_LARGE_GGM_H);
#endif
	printf("\n");

	print_alloc_usage("keygen+sign+verif");
	printf("\n");

	printf("Timing in ms:\n");
	printf(" - Key Gen: %.2f ms (std=%.2f)\n",
	       btimer_get(&timers_algos[B_KEY_GENERATION]),
	       std_timer[B_KEY_GENERATION]
	      );
	printf(" - Sign:    %.2f ms (std=%.2f)\n",
	       btimer_get(&timers_algos[B_SIGN_ALGO]),
	       std_timer[B_SIGN_ALGO]
	      );
	printf(" - Verify:  %.2f ms (std=%.2f)\n",
	       btimer_get(&timers_algos[B_VERIFY_ALGO]),
	       std_timer[B_VERIFY_ALGO]
	      );
	printf("\n");

#ifdef BENCHMARK_CYCLES
	printf("Timing in cycles:\n");
	printf(" - Key Gen: %.2f cycles\n", btimer_get_cycles(&timers_algos[B_KEY_GENERATION]));
	printf(" - Sign:    %.2f cycles\n", btimer_get_cycles(&timers_algos[B_SIGN_ALGO]));
	printf(" - Verify:  %.2f cycles\n", btimer_get_cycles(&timers_algos[B_VERIFY_ALGO]));
	printf("\n");
#endif

	printf("Communication cost:\n");
	printf(" - PK size: %ld B\n", CRYPTO_PUBLICKEYBYTES);
	printf(" - SK size: %ld B\n", CRYPTO_SECRETKEYBYTES);
	printf(" - Signature size (MAX): %ld B\n", CRYPTO_BYTES);
	printf(" - Signature size: %.0f B (std=%.0f)\n", mean_of_sig_size, std_sig_size);
	printf("\n");

#ifdef BENCHMARK_GRINDING
	{
		/* Grinding statistics: derived from MQOM3_PARAM_W (AES truncation
		 * check, p1 = 2^-(W-1)) and MQOM3_PARAM_GRIND_WTOT (total
		 * proof-of-work in bits) */
		double w_tot = MQOM3_PARAM_GRIND_WTOT;
		double p1 = pow(2.0, -(MQOM3_PARAM_W - 1));
		double p_total = pow(2.0, -(w_tot - 1.0));
		double p2 = p_total / p1;
		double mean_theory = 1.0 / p_total;
		double std_theory = sqrt(1.0 - p_total) / p_total;
		double cv_theory = sqrt(1.0 - p_total);
		double mean_emp = wf_grind.mean;
		double std_emp = welford_std(&wf_grind);
		static const double target_eps[] = {0.10, 0.05, 0.01};
		static const int target_k[] = {32, 64, 80, 128, 256};
		double bits_per_trial = -log2(1.0 - p_total);

		/* Fit Sign_cost = intercept + slope * trials by linear regression
		 * over this run's (trial_count, Sign() cost) samples (slope =
		 * Cov(trials, cost) / Var(trials), the standard least-squares
		 * estimator */
		double var_trials = welford_var(&wf_grind);
		int have_fit = (var_trials > 0.0);
		double slope_ms = 0.0, intercept_ms = 0.0;
#ifdef BENCHMARK_CYCLES
		double slope_cyc = 0.0, intercept_cyc = 0.0;
#endif
		if (have_fit) {
			slope_ms = covacc_cov(&cov_ms_trials) / var_trials;
			intercept_ms = wf_timer[B_SIGN_ALGO].mean - slope_ms * wf_grind.mean;
#ifdef BENCHMARK_CYCLES
			/* Derive cycles from the (robust, wall-clock) ms fit scaled by
			 * this run's average cycles/ms ratio */
			double cycles_per_ms = btimer_get_cycles(&timers_algos[B_SIGN_ALGO]) / wf_timer[B_SIGN_ALGO].mean;
			slope_cyc = slope_ms * cycles_per_ms;
			intercept_cyc = intercept_ms * cycles_per_ms;
#endif
		}

		printf("Grinding statistics:\n");
		printf(" - w=%d, w_tot=%.1f bits  (p1=2^-%d=%.3e, p2=2^-%.1f=%.3e, p_total=2^-%.1f=%.3e)\n",
		       MQOM3_PARAM_W, w_tot,
		       MQOM3_PARAM_W - 1, p1,
		       w_tot - MQOM3_PARAM_W, p2,
		       w_tot - 1.0, p_total);
		printf(" - Trials/signature - theory:     mean=%.1f, std=%.1f (CV=%.3f)\n",
		       mean_theory, std_theory, cv_theory);
		printf(" - Trials/signature - this run:   mean=%.1f, std=%.1f  (%d samples)\n",
		       mean_emp, std_emp, nb_tests);
		printf(" - Std of this run's average (%d samples): %.2f trials (%.1f%% of the mean)\n",
		       nb_tests, std_emp / sqrt((double) nb_tests),
		       100.0 * std_emp / sqrt((double) nb_tests) / mean_emp);
		printf(" - Recommended N for a target precision on the average (95%% CI, CV~%.3f):\n", cv_theory);
		for (size_t k = 0; k < sizeof(target_eps) / sizeof(target_eps[0]); k++) {
			double eps = target_eps[k];
			double n_req = pow(1.96 * cv_theory / eps, 2.0);
			printf("     epsilon=%3.0f%%: N >= %.0f\n", eps * 100.0, ceil(n_req));
		}
		printf("\n");

		if (have_fit) {
			printf(" - Fitted linear model (Sign() cost vs grinding trial count, this run):\n");
#ifdef BENCHMARK_CYCLES
			printf("     per-trial cost: %.5f ms (%.0f cycles); non-grinding overhead: %.3f ms (%.0f cycles)\n",
			       slope_ms, slope_cyc, intercept_ms, intercept_cyc);
#else
			printf("     per-trial cost: %.5f ms; non-grinding overhead: %.3f ms\n",
			       slope_ms, intercept_ms);
#endif
			/* Theoretical average Sign() cost: intercept + slope * mean_theor */
			printf(" - Theoretical average Sign() cost (intercept + slope * mean_theory trials):\n");
#ifdef BENCHMARK_CYCLES
			printf("     %.3f ms (%.2f Mcycles)  [vs directly observed: %.3f ms (%.2f Mcycles), noisier - see SEM above]\n",
			       intercept_ms + slope_ms * mean_theory,
			       (intercept_cyc + slope_cyc * mean_theory) / 1.0e6,
			       wf_timer[B_SIGN_ALGO].mean,
			       btimer_get_cycles(&timers_algos[B_SIGN_ALGO]) / 1.0e6);
#else
			printf("     %.3f ms  [vs directly observed: %.3f ms, noisier - see SEM above]\n",
			       intercept_ms + slope_ms * mean_theory,
			       wf_timer[B_SIGN_ALGO].mean);
#endif
			printf("\n");
		}

		/* Worst-case trial budget */
		printf(" - Worst-case trial budget per Sign() call for target failure probability 2^-k\n");
		printf("   (n(k) = ceil(k / -log2(1-p_total)); P(more than n(k) trials needed) <= 2^-k):\n");
		for (size_t j = 0; j < sizeof(target_k) / sizeof(target_k[0]); j++) {
			int k = target_k[j];
			double n_k = ceil((double) k / bits_per_trial);
			printf("     k=%3d: mean=%.1f, n(k)/mean=%6.2f, n(k)=%.0f",
			       k, mean_theory, n_k / mean_theory, n_k);
			if (have_fit) {
				double est_ms = intercept_ms + slope_ms * n_k;
				printf(", est. Sign ~ %.2f ms", est_ms);
#ifdef BENCHMARK_CYCLES
				double est_mcycles = (intercept_cyc + slope_cyc * n_k) / 1.0e6;
				printf(" (~%.2f Mcycles)", est_mcycles);
#endif
			}
			printf("\n");
		}
		printf("\n");
	}
#endif /* BENCHMARK_GRINDING */

#ifdef BENCHMARK
	printf("\n===== DETAILED BENCHMARK =====\n");
	{
		/* Computed sub-sums for BLC, PIOP, and total sign overhead */
		double blc_sub = btimer_get(&timers[BS_BLC_EXPAND_TREE])
		               + btimer_get(&timers[BS_BLC_SEED_COMMIT])
		               + btimer_get(&timers[BS_BLC_PRG])
		               + btimer_get(&timers[BS_BLC_XOF])
		               + btimer_get(&timers[BS_BLC_ARITH]);
		double piop_sub = btimer_get(&timers[BS_PIOP_EXPAND_MQ])
		                + btimer_get(&timers[BS_PIOP_EXPAND_BATCHING_MAT])
		                + btimer_get(&timers[BS_PIOP_MAT_MUL_EXT])
		                + btimer_get(&timers[BS_PIOP_COMPUTE_T1])
		                + btimer_get(&timers[BS_PIOP_COMPUTE_PZI])
		                + btimer_get(&timers[BS_PIOP_BATCH_AND_MASK]);
		double sign_probed = btimer_get(&timers[BS_SIGN_HASH_MSG])
		                   + btimer_get(&timers[BS_BLC_COMMIT])
		                   + btimer_get(&timers[BS_PIOP_COMPUTE])
		                   + btimer_get(&timers[BS_SIGN_HASH_FS])
		                   + btimer_get(&timers[BS_SAMPLE_CHALLENGE])
		                   + btimer_get(&timers[BS_BLC_OPEN]);

		printf(" - Signing\n");
		display_timer("Hash_3 (message hash)", BS_SIGN_HASH_MSG);
		display_timer("BLC.Commit", BS_BLC_COMMIT);
		display_timer("[BLC.Commit] Expand Trees", BS_BLC_EXPAND_TREE);
		display_timer("[BLC.Commit] Seed Commit", BS_BLC_SEED_COMMIT);
		display_timer("[BLC.Commit] PRG", BS_BLC_PRG);
		display_timer("[BLC.Commit] XOF", BS_BLC_XOF);
		display_timer("[BLC.Commit] Arithm", BS_BLC_ARITH);
		printf("   - [BLC.Commit] sub-sum: %f ms (total BLC.Commit: %f ms)\n",
		       blc_sub, btimer_get(&timers[BS_BLC_COMMIT]));
		display_timer("PIOP.Compute", BS_PIOP_COMPUTE);
		display_timer("[PIOP.Compute] ExpandMQ", BS_PIOP_EXPAND_MQ);
		display_timer("[PIOP.Compute] Expand Batching Mat", BS_PIOP_EXPAND_BATCHING_MAT);
		display_timer("[PIOP.Compute] Matrix Mul Ext", BS_PIOP_MAT_MUL_EXT);
		display_timer("[PIOP.Compute] Compute t1", BS_PIOP_COMPUTE_T1);
		display_timer("[PIOP.Compute] Compute P_zi", BS_PIOP_COMPUTE_PZI);
		display_timer("[PIOP.Compute] Batch and Mask", BS_PIOP_BATCH_AND_MASK);
		printf("   - [PIOP.Compute] sub-sum: %f ms (total PIOP.Compute: %f ms)\n",
		       piop_sub, btimer_get(&timers[BS_PIOP_COMPUTE]));
		display_timer("Hash_1+2+4 (Fiat-Shamir)", BS_SIGN_HASH_FS);
		display_timer("Sample Challenge", BS_SAMPLE_CHALLENGE);
		display_timer("BLC.Open", BS_BLC_OPEN);
		printf("   - Sign probed sub-sum: %f ms (wall-clock Sign: %f ms)\n",
		       sign_probed, btimer_get(&timers_algos[B_SIGN_ALGO]));
		printf(" - Wildcards (user-defined pins, 0 if unused)\n");
		display_timer("Pin A", B_PIN_A);
		display_timer("Pin B", B_PIN_B);
		display_timer("Pin C", B_PIN_C);
		display_timer("Pin D", B_PIN_D);
	}
#endif

#ifdef MEASURE_STACK
	{
		/* Per-operation stack and heap measurement (single run each). */
		uint8_t _meas_pk[CRYPTO_PUBLICKEYBYTES];
		uint8_t _meas_sk[CRYPTO_SECRETKEYBYTES];
		uint8_t _meas_m[MLEN] = {5, 6, 7, 8};
		uint8_t _meas_m2[MLEN];
		uint8_t _meas_sm[MLEN + CRYPTO_BYTES];
		unsigned long long _meas_smlen = 0;
		unsigned long long _meas_m2len = 0;

		/* Pre-generate keys and a signature so verify has valid inputs. */
		crypto_sign_keypair(_meas_pk, _meas_sk);
		crypto_sign(_meas_sm, &_meas_smlen, _meas_m, MLEN, _meas_sk);

		/* KeyGen */
		reset_alloc_usage();
		_sm_keygen_args_t _kg_args = { _meas_pk, _meas_sk };
		size_t _kg_stack = stack_measure_run(_sm_run_keygen, &_kg_args, STACK_MEASURE_SIZE);
		long int _kg_heap = alloc_peak_usage;

		/* Sign */
		reset_alloc_usage();
		_sm_sign_args_t _sg_args = { _meas_sm, &_meas_smlen, _meas_m, MLEN, _meas_sk };
		size_t _sg_stack = stack_measure_run(_sm_run_sign, &_sg_args, STACK_MEASURE_SIZE);
		long int _sg_heap = alloc_peak_usage;

		/* Verify */
		reset_alloc_usage();
		_sm_verify_args_t _vf_args = { _meas_m2, &_meas_m2len, _meas_sm, _meas_smlen, _meas_pk };
		size_t _vf_stack = stack_measure_run(_sm_run_verify, &_vf_args, STACK_MEASURE_SIZE);
		long int _vf_heap = alloc_peak_usage;

		printf("\n===== MEMORY USAGE =====\n");
		printf(" - Key Gen stack: %zu B\n", _kg_stack);
		printf(" - Sign stack: %zu B\n", _sg_stack);
		printf(" - Verify stack: %zu B\n", _vf_stack);
#ifdef MQOM_ALLOC_PROBE_ACTIVE
		printf(" - Key Gen heap: %ld B\n", _kg_heap);
		printf(" - Sign heap: %ld B\n", _sg_heap);
		printf(" - Verify heap: %ld B\n", _vf_heap);
#else
		/* Without the probe alloc_peak_usage is a dummy that stays at 0.
		 * Say so rather than print three misleading zeroes. */
		(void)_kg_heap; (void)_sg_heap; (void)_vf_heap;
		printf(" - heap: not measured (rebuild with USE_ALLOC_PROBE=1)\n");
#endif
	}
#endif /* MEASURE_STACK */

	return 0;
}
