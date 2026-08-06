/* rc8probe_feistel.c -- TASK-20260805-b95720 (BATCH-014, GOAL-AES-003 RC-D).
 *
 * Purpose: retest BATCH-009's OUTCOME-A (EV-AES-e4c091) -- "the r=5 yoyo
 * excess does not survive substituting the cipher with a lazily-sampled
 * IDEAL random permutation oracle" -- against a DIFFERENT kind of
 * substitute: a keyed, deterministic, NON-ideal Feistel-network PRP that is
 * independently constructed (see src/INDEPENDENCE_AUDIT.md) and evaluated
 * directly (O(1) memory per query), not resampled per trial.
 *
 * PROVENANCE OF REUSED CODE (disclosed, per task instructions "copy/adapt,
 * don't reinvent" for the harness machinery):
 *   - splitmix64 (sm64), the plaintext-draw-with-rejection loop, the
 *     trivial-swap exclusion, the PW/CW forward/inverse ShiftRows-diagonal
 *     probe geometry, the worker/job threading structure, and the CLI/JSON
 *     reporting shape are copied and adapted from rc8probe.c
 *     (BATCH-007, TASK-20260803-e55757, committed 1a0ad198) -- this is
 *     HARNESS machinery (plaintext generation + yoyo-statistic counting),
 *     not oracle/round-function code, and reuse of it is exactly what the
 *     task card asked for so the comparison is apples-to-apples.
 *   - Everything cipher-specific from rc8probe.c (SBOX/ISBOX, GF(2^8)
 *     log/antilog tables, gmul/ginv, build_aes_sbox, build_random_sbox,
 *     the M2/M3/M9/MB/MD/ME MixColumns tables, key_expand, add_rk,
 *     sub_bytes/inv_sub_bytes, shift_rows/inv_shift_rows,
 *     mix_columns/inv_mix_columns, enc_r/dec_r, load_sbox, do_pin's AES KAT
 *     branch) is DELETED, not reused. The oracle below (feistel_encrypt /
 *     feistel_decrypt / feistel_round_keys) shares no table and no code with
 *     any of it, nor with rc8probe's own ideal-permutation (perm128) code
 *     from BATCH-011/BATCH-012 (rc8probe_ideal.c), which this file also does
 *     not include or call. See INDEPENDENCE_AUDIT.md for the side-by-side.
 *
 * Oracle: 128-bit block, 16-round balanced Feistel network, 64-bit halves.
 * Round function is a murmur3-style 64-bit integer avalanche finalizer
 * (addition mod 2^64, xor-shift, multiplication by odd 64-bit constants) --
 * NOT AES's GF(2^8) polynomial arithmetic, NOT a byte-substitution table,
 * NOT a ShiftRows-style byte permutation. DETERMINISTIC: fixed round count,
 * one key -> one fixed set of round subkeys -> the SAME permutation on every
 * trial (verified by `rc8probe_feistel detcheck`, not merely asserted).
 *
 * Pure measurement. certificate.kind: none.
 * build: gcc -O3 -pthread -o rc8probe_feistel rc8probe_feistel.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

/* ---------------- splitmix64 (harness RNG; reused from rc8probe.c) ------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ================================================================= */
/* THE ORACLE: keyed deterministic Feistel PRP. Independent of AES.  */
/* See INDEPENDENCE_AUDIT.md for the explicit side-by-side comparison */
/* against AES's actual S-box / MixColumns / ShiftRows.               */
/* ================================================================= */
#define FEISTEL_ROUNDS 16
static uint64_t RK[FEISTEL_ROUNDS];   /* fixed round subkeys, derived once from the 128-bit key */
static int RK_ready = 0;

/* Round function F(x, k): a 64-bit integer avalanche mix built from
 * addition, xor-shift, and multiplication by odd constants (the
 * "murmur3 fmix64" finalizer family). No GF(2^8) multiply, no S-box
 * lookup table, no byte rotation/permutation matching AES's ShiftRows. */
static inline uint64_t feistel_F(uint64_t x, uint64_t k){
    uint64_t v = x + k;
    v ^= v >> 33;
    v *= 0xff51afd7ed558ccdULL;
    v ^= v >> 33;
    v *= 0xc4ceb9fe1a85ec53ULL;
    v ^= v >> 33;
    v += k;               /* second key injection, cheap extra key-mixing */
    return v;
}

/* Derive FEISTEL_ROUNDS 64-bit round subkeys from the 128-bit master key.
 * Uses splitmix64 (harness RNG, not AES machinery) seeded from the key
 * halves. Computed ONCE per process invocation and held fixed -- NOT
 * resampled per trial or per query. */
static void feistel_round_keys(const uint8_t key[16]){
    uint64_t k0 = 0, k1 = 0;
    for(int i = 0; i < 8; i++) k0 |= (uint64_t)key[i]     << (8*i);
    for(int i = 0; i < 8; i++) k1 |= (uint64_t)key[8 + i] << (8*i);
    uint64_t st = k0 ^ (k1 * 0x2545F4914F6CDD1DULL) ^ 0xD1B54A32D192ED03ULL;
    for(int i = 0; i < FEISTEL_ROUNDS; i++) RK[i] = sm64(&st);
    RK_ready = 1;
}

/* Balanced Feistel, 64-bit halves, standard structure:
 *   for i = 0..R-1: (L,R) <- (R, L xor F(R, RK[i]))
 * Deterministic given RK[]. O(1) memory per query -- no stored pair table. */
static void feistel_encrypt(const uint8_t in[16], uint8_t out[16]){
    uint64_t L = 0, R = 0;
    for(int i = 0; i < 8; i++) L |= (uint64_t)in[i]     << (8*i);
    for(int i = 0; i < 8; i++) R |= (uint64_t)in[8 + i] << (8*i);
    for(int i = 0; i < FEISTEL_ROUNDS; i++){
        uint64_t nL = R;
        uint64_t nR = L ^ feistel_F(R, RK[i]);
        L = nL; R = nR;
    }
    for(int i = 0; i < 8; i++) out[i]     = (uint8_t)(L >> (8*i));
    for(int i = 0; i < 8; i++) out[8 + i] = (uint8_t)(R >> (8*i));
}
/* Exact inverse: run the Feistel ladder backwards. */
static void feistel_decrypt(const uint8_t in[16], uint8_t out[16]){
    uint64_t L = 0, R = 0;
    for(int i = 0; i < 8; i++) L |= (uint64_t)in[i]     << (8*i);
    for(int i = 0; i < 8; i++) R |= (uint64_t)in[8 + i] << (8*i);
    for(int i = FEISTEL_ROUNDS - 1; i >= 0; i--){
        uint64_t pR = L;
        uint64_t pL = R ^ feistel_F(L, RK[i]);
        L = pL; R = pR;
    }
    for(int i = 0; i < 8; i++) out[i]     = (uint8_t)(L >> (8*i));
    for(int i = 0; i < 8; i++) out[8 + i] = (uint8_t)(R >> (8*i));
}

/* enc_r/dec_r signature kept matching rc8probe.c's cipher call sites so the
 * worker below is a direct adaptation; "r" (rounds) and "rk" (AES round-key
 * schedule) arguments are accepted but unused -- FEISTEL_ROUNDS and RK[]
 * (globals set once by feistel_round_keys) are what actually run. */
static void enc_r(const uint8_t in[16], uint8_t out[16]){ feistel_encrypt(in, out); }
static void dec_r(const uint8_t in[16], uint8_t out[16]){ feistel_decrypt(in, out); }

/* ---------------- geometry (byte-identical to rc8probe.c) --------------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j = 0; j < 4; j++) for(int row = 0; row < 4; row++){
        PW[j][row] = 4 * (((j + row) % 4 + 4) % 4) + row;   /* forward SR diagonals */
        CW[j][row] = 4 * (((j - row) % 4 + 4) % 4) + row;   /* inverse SR diagonals */
    }
}

/* ---------------- worker (adapted from rc8probe.c's worker) ------------- */
typedef struct {
    uint64_t ntrials, seed_thread;
    int amask, smask;
    uint64_t whist[5], trivial, wword[4], wge1;
    uint64_t hit_thread_idx[64]; int hit_count;   /* bounded hit log, like v4 */
    uint64_t pstream_digest;
} job;

#define HIT_LOG_CAP 64

static void *worker(void *arg){
    job *J = (job*)arg;
    uint64_t st = J->seed_thread;
    uint8_t p0[16], p1[16], c0[16], c1[16], q0[16], q1[16], d[16];
    uint64_t digest = 1469598103934665603ULL; /* FNV-ish order-sensitive accumulator */
    for(uint64_t t = 0; t < J->ntrials; t++){
        uint64_t a = sm64(&st), b = sm64(&st);
        for(int i = 0; i < 8; i++) p0[i]     = (uint8_t)(a >> (8*i));
        for(int i = 0; i < 8; i++) p0[8 + i] = (uint8_t)(b >> (8*i));
        memcpy(p1, p0, 16);
        int ok = 0;
        while(!ok){
            ok = 1;
            for(int j = 0; j < 4; j++) if(J->amask & (1 << j)){
                uint64_t rnd = sm64(&st); int nz = 0;
                for(int row = 0; row < 4; row++){
                    uint8_t nb = (uint8_t)(rnd >> (8*row));
                    p1[PW[j][row]] = nb;
                    if(nb != p0[PW[j][row]]) nz = 1;
                }
                if(!nz) ok = 0;
            }
        }
        /* order-sensitive digest of the (p0,p1) pair stream, mirroring v4's
         * plaintext_stream_digest gate -- lets a matched-exposure comparison
         * verify byte-identical plaintext generation against other arms that
         * used the same seed/armid/threads. */
        for(int i = 0; i < 16; i++){ digest ^= p0[i]; digest *= 1099511628211ULL; }
        for(int i = 0; i < 16; i++){ digest ^= p1[i]; digest *= 1099511628211ULL; }

        enc_r(p0, c0);
        enc_r(p1, c1);
        int trivial = 1;
        for(int j = 0; j < 4; j++) if(J->smask & (1 << j))
            for(int row = 0; row < 4; row++){
                int i = CW[j][row];
                uint8_t x = c0[i], y = c1[i];
                if(x != y) trivial = 0;
                c0[i] = y; c1[i] = x;
            }
        dec_r(c0, q0);
        dec_r(c1, q1);
        for(int i = 0; i < 16; i++) d[i] = (uint8_t)(q0[i] ^ q1[i]);
        int W = 0;
        for(int j = 0; j < 4; j++){
            int z = 1;
            for(int row = 0; row < 4; row++) if(d[PW[j][row]]) { z = 0; break; }
            if(z){ W++; if(!trivial) J->wword[j]++; }
        }
        if(trivial){ J->trivial++; continue; }
        J->whist[W]++;
        if(W >= 1){
            J->wge1++;
            if(J->hit_count < HIT_LOG_CAP) J->hit_thread_idx[J->hit_count++] = t;
        }
    }
    J->pstream_digest = digest;
    return NULL;
}

/* ---------------- determinism self-check --------------------------------- */
static int do_detcheck(const uint8_t key[16]){
    feistel_round_keys(key);
    uint8_t in[16], o1[16], o2[16], back[16];
    uint64_t st = 424242ULL;
    int ok = 1, nfixed = 0;
    for(int trial = 0; trial < 4096; trial++){
        for(int i = 0; i < 16; i += 8){
            uint64_t z = sm64(&st);
            for(int q = 0; q < 8; q++) in[i+q] = (uint8_t)(z >> (8*q));
        }
        feistel_encrypt(in, o1);
        feistel_encrypt(in, o2);           /* SAME key + input, called again */
        if(memcmp(o1, o2, 16) != 0) ok = 0;
        feistel_decrypt(o1, back);
        if(memcmp(back, in, 16) != 0) ok = 0;
        if(memcmp(in, o1, 16) == 0) nfixed++;
    }
    /* Also confirm the SAME key produces the SAME round-key schedule across
     * two independent derivations (not resampled). */
    uint64_t rk_first[FEISTEL_ROUNDS];
    memcpy(rk_first, RK, sizeof RK);
    feistel_round_keys(key);
    int rk_match = (memcmp(rk_first, RK, sizeof RK) == 0);
    printf("{\n  \"mode\": \"detcheck\",\n");
    printf("  \"trials\": 4096,\n");
    printf("  \"same_key_same_input_same_output\": %s,\n", ok ? "true" : "false");
    printf("  \"decrypt_inverts_encrypt\": %s,\n", ok ? "true" : "false");
    printf("  \"round_key_schedule_reproducible\": %s,\n", rk_match ? "true" : "false");
    printf("  \"fixed_points_in_4096_trials\": %d,\n", nfixed);
    printf("  \"deterministic\": %s\n}\n", (ok && rk_match) ? "true" : "false");
    return ok && rk_match;
}

int main(int argc, char **argv){
    build_geom();
    if(argc < 2){
        fprintf(stderr,
          "usage: rc8probe_feistel detcheck <seed>\n"
          "       rc8probe_feistel arm <name> <rounds_ignored> <amask> <smask> <log2N> <seed> <armid> <threads>\n");
        return 2;
    }
    if(!strcmp(argv[1], "detcheck")){
        uint64_t seed = argc > 2 ? strtoull(argv[2], NULL, 10) : 90210ULL;
        uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
        uint8_t key[16];
        for(int i = 0; i < 16; i += 8){
            uint64_t z = sm64(&kst);
            for(int q = 0; q < 8; q++) key[i + q] = (uint8_t)(z >> (8*q));
        }
        int ok = do_detcheck(key);
        return ok ? 0 : 1;
    }
    if(strcmp(argv[1], "arm")){ fprintf(stderr, "bad mode\n"); return 2; }
    if(argc < 10){ fprintf(stderr, "arm needs 8 args\n"); return 2; }

    const char *name = argv[2];
    /* argv[3] = rounds field, kept for CLI-shape parity with rc8probe.c;
     * the Feistel oracle always runs FEISTEL_ROUNDS (16) rounds regardless
     * of this value, and that is reported explicitly below so it is never
     * mistaken for a tunable round count. */
    int rounds_field_ignored = atoi(argv[3]);
    int amask = atoi(argv[4]), smask = atoi(argv[5]);
    int log2N = atoi(argv[6]);
    uint64_t seed = strtoull(argv[7], NULL, 10);
    int armid = atoi(argv[8]); int nthr = atoi(argv[9]);
    if(smask == 0 || smask == 15){ fprintf(stderr, "degenerate smask forbidden\n"); return 3; }
    if(amask == 0){ fprintf(stderr, "empty amask forbidden\n"); return 3; }

    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i = 0; i < 16; i += 8){
        uint64_t z = sm64(&kst);
        for(int q = 0; q < 8; q++) key[i + q] = (uint8_t)(z >> (8*q));
    }
    feistel_round_keys(key);   /* fixed once, NOT resampled per trial */

    uint64_t N = 1ULL << log2N;
    job *jobs = calloc(nthr, sizeof(job));
    pthread_t *th = calloc(nthr, sizeof(pthread_t));
    uint64_t per = N / nthr;
    for(int t = 0; t < nthr; t++){
        jobs[t].ntrials = per + (t == 0 ? N - per * nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid * 0x1234567891ULL)
                            ^ ((uint64_t)(t + 1) * 0x9E3779B97F4A7C15ULL);
        jobs[t].amask = amask; jobs[t].smask = smask;
    }
    for(int t = 0; t < nthr; t++) pthread_create(&th[t], NULL, worker, &jobs[t]);
    for(int t = 0; t < nthr; t++) pthread_join(th[t], NULL);

    uint64_t wh[5] = {0}, wword[4] = {0}, trivial = 0, wge1 = 0;
    for(int t = 0; t < nthr; t++){
        for(int i = 0; i < 5; i++) wh[i] += jobs[t].whist[i];
        for(int i = 0; i < 4; i++) wword[i] += jobs[t].wword[i];
        trivial += jobs[t].trivial; wge1 += jobs[t].wge1;
    }
    printf("{\n  \"probe\": \"rc8probe_feistel\",\n  \"arm\": \"%s\",\n  \"oracle\": \"keyed_deterministic_feistel16_64bit_halves\",\n",
           name);
    printf("  \"rounds_field_ignored_input\": %d,\n", rounds_field_ignored);
    printf("  \"feistel_rounds_actual\": %d,\n", FEISTEL_ROUNDS);
    printf("  \"ideal_permutation\": false,\n");
    printf("  \"resampled_per_trial\": false,\n");
    printf("  \"amask\": %d,\n  \"smask\": %d,\n", amask, smask);
    printf("  \"trials\": %llu,\n  \"log2N\": %d,\n  \"seed\": %llu,\n  \"arm_id\": %d,\n  \"threads\": %d,\n",
           (unsigned long long)N, log2N, (unsigned long long)seed, armid, nthr);
    printf("  \"key_hex\": \""); for(int i = 0; i < 16; i++) printf("%02x", key[i]); printf("\",\n");
    printf("  \"thread_seeds\": [");
    for(int t = 0; t < nthr; t++) printf("%llu%s", (unsigned long long)jobs[t].seed_thread, t < nthr-1 ? "," : "");
    printf("],\n");
    printf("  \"trivial_swaps_excluded\": %llu,\n", (unsigned long long)trivial);
    printf("  \"nontrivial_trials\": %llu,\n", (unsigned long long)(N - trivial));
    printf("  \"W_ge1_nontrivial\": %llu,\n", (unsigned long long)wge1);
    printf("  \"W_ge1_by_word\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wword[0], (unsigned long long)wword[1],
           (unsigned long long)wword[2], (unsigned long long)wword[3]);
    printf("  \"whist\": [");
    for(int i = 0; i < 5; i++) printf("%llu%s", (unsigned long long)wh[i], i < 4 ? "," : "");
    printf("],\n");
    printf("  \"null_expectation_analytic\": %.10f,\n", (double)(N - trivial) * 4.0 / 4294967296.0);
    /* order-sensitive digest per thread, mirroring v4's plaintext_stream_digest */
    printf("  \"plaintext_stream_digest_per_thread\": [");
    for(int t = 0; t < nthr; t++) printf("\"%016llx\"%s", (unsigned long long)jobs[t].pstream_digest, t < nthr-1 ? "," : "");
    printf("],\n");
    printf("  \"hit_trials_logged\": %d,\n", nthr > 0 ? jobs[0].hit_count : 0);
    printf("  \"hit_trials\": [");
    { int first = 1;
      for(int t = 0; t < nthr; t++)
        for(int i = 0; i < jobs[t].hit_count; i++){
            if(!first) printf(",");
            printf("[%d,%llu]", t, (unsigned long long)jobs[t].hit_thread_idx[i]);
            first = 0;
        }
    }
    printf("],\n");
    printf("  \"hit_log_cap\": %d\n", HIT_LOG_CAP);
    printf("}\n");
    free(jobs); free(th);
    return 0;
}
