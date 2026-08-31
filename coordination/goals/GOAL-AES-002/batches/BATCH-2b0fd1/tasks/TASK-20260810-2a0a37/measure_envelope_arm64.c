/* =====================================================================
 * measure_envelope_arm64.c — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)
 *
 * RELATIONSHIP TO measure_envelope.c IN THIS TASK DIRECTORY: it is the
 * arm64-native counterpart written after MEASUREMENT showed the host is
 * Apple Silicon (arm64), where x86-64 intrinsics cannot compile. It is
 * a NEW immutable path, not an edit. measure_envelope.c remains the
 * declared artifact of this task and its -maes compile failure on this
 * host is the measured resolution of the RQ-AES-001/GOAL-AES-001
 * toolchain contradiction's central point.
 *
 * PURPOSE. Toolchain-and-throughput benchmark ONLY, for the arm64 host
 * actually measured. AES-128 block operations via the Arm Cryptography
 * Extension (vaeseq_u128/vaesmcq_u128 are the arm64 counterparts of
 * _mm_aesenc_si128). NO cryptanalysis, no key recovery, no
 * distinguisher, NOTHING asserted about AES security at any round
 * count. Any infrastructure failure is infrastructure signal, never
 * negative mathematical evidence about AES (AGENTS.md rule 5). This
 * artifact is infrastructure and is expressly NOT a completion
 * (GOAL-AES-002 non_completion_criteria (vi)).
 *
 * DESIGN NOTES.
 *  - S-box and Rcon are COMPUTED at startup from the AES definition
 *    (GF(2^8) inversion + affine map; Rcon by GF doubling). Nothing is
 *    transcribed from memory. Correctness is established by the driver
 *    against independent implementations (openssl CLI; see run logs).
 *  - bench modes:
 *      fresh : expand a FRESH key and encrypt one block per iteration
 *              (the CM-1 AEU-128 shape: schedule charged, not amortised).
 *      dep   : one key, DEPENDENT chain (output feeds input) — latency-bound.
 *      ind   : one key, INDEPENDENT blocks — throughput/pipelining allowed.
 *  - Timing by CLOCK_MONOTONIC. xor-accumulator prevents dead-code
 *    elimination and is printed with every result line.
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
 *   round count; R5 of RQ-AES-002 applies to any later record that
 *   quotes this program's numbers in a margin.
 * -----------------------------------------------------------------------
 * ===================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <arm_neon.h>

#if __has_include(<arm_acle.h>)
#include <arm_acle.h>
#endif

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

/* One AES-128 round using the Arm Cryptography Extension:
 * vaeseq_u128 = AESE (SubBytes + ShiftRows + AddRoundKey),
 * vaesmcq_u128 = AESMC (MixColumns). AESE applies the round key itself,
 * so the round-key XOR is folded into the AESE call. */
static inline uint8x16_t aes128_encrypt(uint8x16_t b, const uint8x16_t rk[11]) {
    b = veorq_u8(b, rk[0]);
    for (int r = 1; r <= 9; r++)
        b = vaesmcq_u8(vaeseq_u8(b, rk[r]));
    return vaeseq_u8(b, rk[10]); /* final round: no MixColumns */
}

typedef struct { uint8x16_t rk[11]; unsigned char bytes[176]; } aes128_key;

static void key_init(aes128_key *k, const unsigned char key[16]) {
    expand_key128(key, k->bytes);
    for (int i = 0; i < 11; i++)
        k->rk[i] = vld1q_u8(k->bytes + 16 * i);
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
        uint8x16_t b = vld1q_u8(pt);
        b = aes128_encrypt(b, k.rk);
        vst1q_u8(ct, b);
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
            uint8x16_t b = vld1q_u8(pt);
            b = aes128_encrypt(b, k.rk);
            vst1q_u8(ct, b);
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
                    uint8x16_t b = vreinterpretq_u8_u64(vdupq_n_u64(i));
                    b = aes128_encrypt(b, k.rk);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0)
                         ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
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
                uint8x16_t b = vld1q_u8(pt);
                double t0 = now_sec();
                for (uint64_t i = 0; i < N; i++) {
                    b = aes128_encrypt(b, k.rk);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0)
                         ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
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
                    uint8x16_t b = veorq_u8(vreinterpretq_u8_u64(vdupq_n_u64(i)),
                                            vreinterpretq_u8_u64(vdupq_n_u64(i ^ 0x5555555555555555ULL)));
                    b = aes128_encrypt(b, k.rk);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0)
                         ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
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
