/* =====================================================================
 * measure_envelope.c — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)
 *
 * PURPOSE. Toolchain-and-throughput benchmark ONLY. It resolves by
 * measurement whether gcc with -maes compiles and runs on this host and
 * at what rate this implementation performs AES-128 block operations.
 * It performs NO cryptanalysis, attempts no key recovery, computes no
 * distinguisher, and asserts NOTHING about AES security at any round
 * count. Any infrastructure failure of this program is infrastructure
 * signal, never negative mathematical evidence about AES (AGENTS.md
 * rule 5). This artifact is infrastructure and is expressly NOT a
 * completion (GOAL-AES-002 non_completion_criteria (vi)).
 *
 * DESIGN NOTES.
 *  - The S-box and Rcon table are COMPUTED at startup from the AES
 *    definition (GF(2^8) inversion under the modulus polynomial, then
 *    the affine map; Rcon by GF doubling). No table is transcribed from
 *    memory. Correctness is established at runtime by the driver, which
 *    cross-checks this program's outputs on random vectors against TWO
 *    independent implementations (pycryptodome and the openssl CLI),
 *    which is the specification pinning discipline of RQ-AES-002.
 *  - Round transformations use AES-NI intrinsics (_mm_aesenc_si128 /
 *    _mm_aesenclast_si128); the key expansion is scalar C.
 *  - bench modes:
 *      fresh : per iteration, expand a FRESH key and encrypt one block
 *              (the CM-1 AEU-128 shape: schedule charged, not amortised).
 *      dep   : one expanded key, blocks in a DEPENDENT chain (output feeds
 *              input) — latency-bound, no cross-block pipelining.
 *      ind   : one expanded key, INDEPENDENT blocks — throughput-bound,
 *              pipelining across blocks allowed.
 *  - Timing by CLOCK_MONOTONIC. The xor-accumulator prevents the work
 *    being optimised away; it is printed with every result line.
 *
 * ------------------- COMMENT-BLOCK INFERENCE STANZA -------------------
 * authored_by_task: TASK-20260810-2a0a37
 * authored_by_role: executor
 * handoff_inference_policy: executor-implementation
 * handoff_reasoning_effort: null (policy default)
 * fallback_used: false
 * degraded_allowed: false
 * degraded_requirements: []
 * resolved_model_id: null (not surfaced by this runtime; unverified
 *   configuration until a doctor --probe confirms a backend serves it)
 * resolved_runtime: claude-code session (api_direct-equivalent tool set)
 * bedrock: NOT selected, configured, probed or contacted, and never may
 *   be (AGENTS.md rule 16; task constraint SC-11)
 * claim_tier_of_this_artifact: infrastructure measurement only; states
 *   no margin, no cryptanalytic claim, and nothing about AES at any
 *   round count; the R5 anti-laundering clause of RQ-AES-002 applies to
 *   any later record that quotes this program's numbers in a margin.
 * -----------------------------------------------------------------------
 * ===================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <wmmintrin.h>

static unsigned char SBOX[256];
static unsigned char RCON[11];

static uint8_t gmul(uint8_t a, uint8_t b) {
    uint8_t p = 0;
    while (b) {
        if (b & 1) p ^= a;
        uint8_t hi = a & 0x80;
        a = (uint8_t)(a << 1);
        if (hi) a ^= 0x1b;
        b >>= 1;
    }
    return p;
}

static void init_tables(void) {
    for (int x = 0; x < 256; x++) {
        uint8_t inv = 0;
        if (x) {
            for (int y = 1; y < 256; y++) {
                if (gmul((uint8_t)x, (uint8_t)y) == 1) { inv = (uint8_t)y; break; }
            }
        }
        uint8_t r = (uint8_t)(0x63 ^ inv), t = inv;
        for (int i = 0; i < 4; i++) {
            t = (uint8_t)((t << 1) | (t >> 7));
            r ^= t;
        }
        SBOX[x] = r;
    }
    uint8_t rc = 1;
    for (int i = 1; i <= 10; i++) { RCON[i] = rc; rc = gmul(rc, 2); }
}

static void expand_key128(const unsigned char key[16], unsigned char w[176]) {
    memcpy(w, key, 16);
    int rci = 1;
    for (int i = 16; i < 176; i += 4) {
        unsigned char t0 = w[i-4], t1 = w[i-3], t2 = w[i-2], t3 = w[i-1];
        if (i % 16 == 0) {
            unsigned char first = t0;
            t0 = (unsigned char)(SBOX[t1] ^ RCON[rci++]);
            t1 = SBOX[t2]; t2 = SBOX[t3]; t3 = SBOX[first];
        }
        w[i]   = (unsigned char)(w[i-16] ^ t0);
        w[i+1] = (unsigned char)(w[i-15] ^ t1);
        w[i+2] = (unsigned char)(w[i-14] ^ t2);
        w[i+3] = (unsigned char)(w[i-13] ^ t3);
    }
}

typedef struct { __m128i rk[11]; unsigned char bytes[176]; } aes128_key;

static void key_init(aes128_key *k, const unsigned char key[16]) {
    expand_key128(key, k->bytes);
    for (int i = 0; i < 11; i++)
        k->rk[i] = _mm_loadu_si128((const __m128i *)(k->bytes + 16 * i));
}

static inline __m128i aes128_encrypt(__m128i b, const aes128_key *k) {
    b = _mm_xor_si128(b, k->rk[0]);
    for (int r = 1; r <= 9; r++) b = _mm_aesenc_si128(b, k->rk[r]);
    return _mm_aesenclast_si128(b, k->rk[10]);
}

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static int hexval(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static void hex2bytes(const char *h, unsigned char *out, int n) {
    for (int i = 0; i < n; i++) out[i] = (unsigned char)((hexval(h[2*i]) << 4) | hexval(h[2*i+1]));
}

int main(int argc, char **argv) {
    init_tables();

    if (argc >= 2 && strcmp(argv[1], "selftest") == 0) {
        unsigned char key[16], pt[16], ct[16];
        for (int i = 0; i < 16; i++) { key[i] = (unsigned char)i; pt[i] = (unsigned char)(0x10 + i); }
        aes128_key k; key_init(&k, key);
        __m128i b = _mm_loadu_si128((const __m128i *)pt);
        b = aes128_encrypt(b, &k);
        _mm_storeu_si128((__m128i *)ct, b);
        printf("SELFTEST key=");
        for (int i = 0; i < 16; i++) printf("%02x", key[i]);
        printf(" pt=");
        for (int i = 0; i < 16; i++) printf("%02x", pt[i]);
        printf(" ct=");
        for (int i = 0; i < 16; i++) printf("%02x", ct[i]);
        printf("\n");
        return 0;
    }

    if (argc >= 2 && strcmp(argv[1], "vec") == 0) {
        char line[256];
        while (fgets(line, sizeof line, stdin)) {
            char kh[64], ph[64];
            if (sscanf(line, "%63s %63s", kh, ph) != 2) continue;
            unsigned char key[16], pt[16], ct[16];
            hex2bytes(kh, key, 16); hex2bytes(ph, pt, 16);
            aes128_key k; key_init(&k, key);
            __m128i b = _mm_loadu_si128((const __m128i *)pt);
            b = aes128_encrypt(b, &k);
            _mm_storeu_si128((__m128i *)ct, b);
            printf("VEC ct=");
            for (int i = 0; i < 16; i++) printf("%02x", ct[i]);
            printf("\n");
            fflush(stdout);
        }
        return 0;
    }

    if (argc >= 5 && strcmp(argv[1], "bench") == 0) {
        const char *mode = argv[2];
        uint64_t N = strtoull(argv[3], NULL, 10);
        int reps = atoi(argv[4]);
        unsigned char key[16], pt[16];
        for (int i = 0; i < 16; i++) { key[i] = (unsigned char)i; pt[i] = (unsigned char)(0x10 + i); }
        aes128_key k;

        if (strcmp(mode, "fresh") == 0) {
            for (int rep = 1; rep <= reps; rep++) {
                uint64_t acc = 0;
                double t0 = now_sec();
                for (uint64_t i = 0; i < N; i++) {
                    unsigned char kk[16]; memcpy(kk, key, 16);
                    kk[0] = (unsigned char)(i & 0xff);
                    kk[1] = (unsigned char)((i >> 8) & 0xff);
                    kk[2] = (unsigned char)((i >> 16) & 0xff);
                    key_init(&k, kk);
                    __m128i b = _mm_set1_epi64x((long long)i);
                    b = aes128_encrypt(b, &k);
                    acc ^= (uint64_t)_mm_cvtsi128_si64(b) ^ (uint64_t)_mm_extract_epi64(b, 1);
                }
                double el = now_sec() - t0;
                printf("RESULT mode=fresh N=%llu rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                       (unsigned long long)N, rep, el, (double)N / el, (unsigned long long)acc);
                fflush(stdout);
            }
        } else if (strcmp(mode, "dep") == 0) {
            key_init(&k, key);
            for (int rep = 1; rep <= reps; rep++) {
                uint64_t acc = 0;
                __m128i b = _mm_loadu_si128((const __m128i *)pt);
                double t0 = now_sec();
                for (uint64_t i = 0; i < N; i++) {
                    b = aes128_encrypt(b, &k);
                    acc ^= (uint64_t)_mm_cvtsi128_si64(b) ^ (uint64_t)_mm_extract_epi64(b, 1);
                }
                double el = now_sec() - t0;
                printf("RESULT mode=dep N=%llu rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                       (unsigned long long)N, rep, el, (double)N / el, (unsigned long long)acc);
                fflush(stdout);
            }
        } else if (strcmp(mode, "ind") == 0) {
            key_init(&k, key);
            for (int rep = 1; rep <= reps; rep++) {
                uint64_t acc = 0;
                double t0 = now_sec();
                for (uint64_t i = 0; i < N; i++) {
                    __m128i b = _mm_xor_si128(_mm_set1_epi64x((long long)i),
                                              _mm_set1_epi64x((long long)(i ^ 0x5555555555555555ULL)));
                    b = aes128_encrypt(b, &k);
                    acc ^= (uint64_t)_mm_cvtsi128_si64(b) ^ (uint64_t)_mm_extract_epi64(b, 1);
                }
                double el = now_sec() - t0;
                printf("RESULT mode=ind N=%llu rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                       (unsigned long long)N, rep, el, (double)N / el, (unsigned long long)acc);
                fflush(stdout);
            }
        } else {
            fprintf(stderr, "unknown bench mode: %s\n", mode);
            return 2;
        }
        return 0;
    }

    fprintf(stderr, "usage: %s selftest | vec | bench <fresh|dep|ind> <N> <reps>\n", argv[0]);
    return 2;
}
