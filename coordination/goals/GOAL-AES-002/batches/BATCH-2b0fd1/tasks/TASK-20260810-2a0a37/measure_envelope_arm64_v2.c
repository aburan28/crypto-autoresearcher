/* =====================================================================
 * measure_envelope_arm64_v2.c — TASK-20260810-2a0a37 (GOAL-AES-002/BATCH-2b0fd1)
 *
 * REPAIR of measure_envelope_arm64.c, by NEW immutable path. v1's round
 * composition was WRONG: it passed PLAIN round keys to vaeseq_u8 and then
 * vaesmcq_u8, composing MC(SR(SB(s)) XOR rk), which is NOT the AES round
 * (AddRoundKey must follow MixColumns). MEASURED: 0/8 agreement with the
 * openssl CLI (run2-aesni.json, cross_check_acc_build), while a pure-
 * Python implementation of the same tables agreed 4/4. v2 derives the
 * AESE-form round keys ke_r = MC^{-1}(rk[r]) for rounds 1..9 at runtime
 * and SELF-VERIFIES the derivation (forward MC applied to ke_r must
 * reproduce rk[r]; failure aborts with a nonzero exit). Correctness is
 * adjudicated ONLY by execution against the openssl CLI in the driver —
 * no constant here is trusted because it was recalled.
 * Benchmark ONLY; NO cryptanalysis; nothing asserted about AES security
 * at any round count; infrastructure failures are infrastructure signal
 * (AGENTS.md rule 5); expressly NOT a completion (GOAL-AES-002
 * non_completion_criteria (vi)).
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
 * claim_tier_of_this_artifact: infrastructure measurement only; no
 *   margin, no cryptanalytic claim, nothing about AES at any round
 *   count; R5 of RQ-AES-002 binds any later record quoting these numbers.
 * -----------------------------------------------------------------------
 * ===================================================================== */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <arm_neon.h>

static unsigned char SBOX[256], RCON[11];

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
        if (x) for (int y = 1; y < 256; y++) if (gmul((uint8_t)x, (uint8_t)y) == 1) { inv = (uint8_t)y; break; }
        uint8_t r = (uint8_t)(0x63 ^ inv), t = inv;
        for (int i = 0; i < 4; i++) { t = (uint8_t)((t << 1) | (t >> 7)); r ^= t; }
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
            unsigned char f = t0;
            t0 = (unsigned char)(SBOX[t1] ^ RCON[rci++]);
            t1 = SBOX[t2]; t2 = SBOX[t3]; t3 = SBOX[f];
        }
        w[i]   = (unsigned char)(w[i-16] ^ t0);
        w[i+1] = (unsigned char)(w[i-15] ^ t1);
        w[i+2] = (unsigned char)(w[i-14] ^ t2);
        w[i+3] = (unsigned char)(w[i-13] ^ t3);
    }
}

/* forward MixColumns on a 16-byte state (coefficients 2,3,1,1; verified
   end-to-end by openssl agreement in the driver, not trusted a priori) */
static void mc_fwd(unsigned char s[16]) {
    for (int c = 0; c < 4; c++) {
        unsigned char *p = s + 4 * c;
        unsigned char a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = (unsigned char)(gmul(a0, 2) ^ gmul(a1, 3) ^ a2 ^ a3);
        p[1] = (unsigned char)(a0 ^ gmul(a1, 2) ^ gmul(a2, 3) ^ a3);
        p[2] = (unsigned char)(a0 ^ a1 ^ gmul(a2, 2) ^ gmul(a3, 3));
        p[3] = (unsigned char)(gmul(a0, 3) ^ a1 ^ a2 ^ gmul(a3, 2));
    }
}

/* candidate inverse MixColumns (coefficients 0e,0b,0d,09 — RECALLED, and
   therefore NOT trusted: every use is gated by the runtime check below) */
static void mc_inv_candidate(unsigned char s[16]) {
    for (int c = 0; c < 4; c++) {
        unsigned char *p = s + 4 * c;
        unsigned char a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = (unsigned char)(gmul(a0, 0x0e) ^ gmul(a1, 0x0b) ^ gmul(a2, 0x0d) ^ gmul(a3, 0x09));
        p[1] = (unsigned char)(gmul(a0, 0x09) ^ gmul(a1, 0x0e) ^ gmul(a2, 0x0b) ^ gmul(a3, 0x0d));
        p[2] = (unsigned char)(gmul(a0, 0x0d) ^ gmul(a1, 0x09) ^ gmul(a2, 0x0e) ^ gmul(a3, 0x0b));
        p[3] = (unsigned char)(gmul(a0, 0x0b) ^ gmul(a1, 0x0d) ^ gmul(a2, 0x09) ^ gmul(a3, 0x0e));
    }
}

typedef struct { uint8x16_t rk[11]; uint8x16_t ke[10]; unsigned char bytes[176]; } aes128_key;

static void key_init(aes128_key *k, const unsigned char key[16]) {
    expand_key128(key, k->bytes);
    unsigned char tmp[16];
    for (int r = 1; r <= 9; r++) {
        memcpy(tmp, k->bytes + 16 * r, 16);
        mc_inv_candidate(tmp);
        unsigned char chk[16];
        memcpy(chk, tmp, 16);
        mc_fwd(chk);
        if (memcmp(chk, k->bytes + 16 * r, 16) != 0) {
            fprintf(stderr, "SELF-CHECK FAILED: MC(MC_inv_candidate(rk[%d])) != rk[%d]\n", r, r);
            exit(3);
        }
        k->ke[r] = vld1q_u8(tmp);
    }
    for (int i = 0; i < 11; i++) k->rk[i] = vld1q_u8(k->bytes + 16 * i);
}

/* AESE = SR(SB(s)) XOR k ; AESMC = MC. Round r (1..9):
   MC(SR(SB(s)) XOR ke_r) = MC(SR(SB(s))) XOR rk[r]  (MC linear, ke_r = MC^-1(rk_r)).
   Final round: SR(SB(s)) XOR rk[10], no MC. */
static inline uint8x16_t aes128_encrypt(uint8x16_t b, const aes128_key *k) {
    b = veorq_u8(b, k->rk[0]);
    for (int r = 1; r <= 9; r++) b = vaesmcq_u8(vaeseq_u8(b, k->ke[r]));
    return vaeseq_u8(b, k->rk[10]);
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

int main(int argc, char **argv) {
    init_tables();
    if (argc >= 2 && strcmp(argv[1], "vec") == 0) {
        char line[256];
        while (fgets(line, sizeof line, stdin)) {
            char kh[64], ph[64];
            if (sscanf(line, "%63s %63s", kh, ph) != 2) continue;
            unsigned char key[16], pt[16], ct[16], h[16];
            for (int i = 0; i < 16; i++) key[i] = (unsigned char)((hexval(kh[2*i]) << 4) | hexval(kh[2*i+1]));
            for (int i = 0; i < 16; i++) pt[i]  = (unsigned char)((hexval(ph[2*i]) << 4) | hexval(ph[2*i+1]));
            (void)h;
            aes128_key k; key_init(&k, key);
            uint8x16_t b = vld1q_u8(pt);
            b = aes128_encrypt(b, &k);
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
        if (strcmp(mode, "dep") == 0) {
            key_init(&k, key);
            for (int rep = 1; rep <= reps; rep++) {
                uint64_t acc = 0;
                uint8x16_t b = vld1q_u8(pt);
                double t0 = now_sec();
                for (uint64_t i = 0; i < N; i++) {
                    b = aes128_encrypt(b, &k);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0) ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
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
                    b = aes128_encrypt(b, &k);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0) ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
                }
                double el = now_sec() - t0;
                printf("RESULT mode=ind N=%llu rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                       (unsigned long long)N, rep, el, (double)N / el, (unsigned long long)acc);
                fflush(stdout);
            }
        } else if (strcmp(mode, "fresh") == 0) {
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
                    b = aes128_encrypt(b, &k);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(b), 0) ^ vgetq_lane_u64(vreinterpretq_u64_u8(b), 1);
                }
                double el = now_sec() - t0;
                printf("RESULT mode=fresh N=%llu rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                       (unsigned long long)N, rep, el, (double)N / el, (unsigned long long)acc);
                fflush(stdout);
            }
        } else { fprintf(stderr, "unknown mode\n"); return 2; }
        return 0;
    }
    fprintf(stderr, "usage: %s vec | bench <fresh|dep|ind> <N> <reps>\n", argv[0]);
    return 2;
}
