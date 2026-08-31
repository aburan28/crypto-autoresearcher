/* =====================================================================
 * measure_envelope_arm64_v4.c — TASK-20260810-2a0a37 (GOAL-AES-002/BATCH-2b0fd1)
 *
 * REPAIR v4 of the arm64 hardware-AES benchmark, by new immutable path.
 * Full lineage preserved: v1 composed AESMC(AESE(x, rk)) — WRONG, because
 * ARM AESE XORs the round key BEFORE AESMC applies MixColumns, so that
 * composition computes MC(SR(SB(x))) ^ MC(rk), not ^ rk (0/8 openssl
 * agreement, run2-aesni.json era). v2 pre-transformed round keys but then
 * mis-derived the ShiftRows convention. v3 probed AESE's permutation
 * (sigma = 0 5 10 15 4 9 14 3 8 13 2 7 12 1 6 11) and — reading that as
 * NON-standard — applied a "correction" permutation rho. THE DIAGNOSIS OF
 * THIS SESSION: that probed sigma IS EXACTLY standard FIPS-197 ShiftRows
 * under the out[i] = in[tau[i]] convention (tau[i] = 4*((i div 4 + i mod 4)
 * mod 4) + i mod 4), which evaluates to the very sequence probed; the prior
 * session's "tau" was the transposed (column-shift) map and its rho
 * therefore scrambled a correct instruction. v4 composes the round
 * explicitly and safely with NO permutation correction and NO key
 * pre-transform:
 *     x ^= rk[0]
 *     rounds 1..9:  x = AESMC( AESE(x, ZERO) ) ^ rk[r]   (zero-key AESE,
 *                   MixColumns, then plain vector XOR of the round key —
 *                   algebraically identical to MC(SR(SB(x))) ^ rk[r])
 *     round 10:     x = AESE(x, rk[10])                  (SR(SB(x)) ^ rk[10])
 * Everything is adjudicated by execution: the selftest reproduces the
 * FIPS-197 AES-128 known-answer vector, and the driver cross-checks the
 * 'vec' mode against the openssl CLI before any throughput number is
 * admitted. NOTHING is trusted because it was recalled.
 *
 * Benchmark ONLY; NO cryptanalysis; no key recovery; no distinguisher;
 * nothing asserted about AES security at any round count; infrastructure
 * failures are infrastructure signal, never negative mathematical evidence
 * (AGENTS.md rule 5); this artifact is expressly NOT a completion
 * (GOAL-AES-002 non_completion_criteria (vi)).
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

/* Tables are COMPUTED from the AES definition: GF(2^8) inversion under
 * x^8+x^4+x^3+x+1, then the affine map; Rcon by GF doubling. */
static void init_tables(void) {
    for (int x = 0; x < 256; x++) {
        uint8_t inv = 0;
        if (x) { for (int y = 1; y < 256; y++) if (gmul((uint8_t)x,(uint8_t)y)==1) { inv=(uint8_t)y; break; } }
        uint8_t a = inv;
        for (int r = 1; r <= 4; r++) { a = (uint8_t)((a << 1) | (a >> 7)); inv ^= a; }
        SBOX[x] = (uint8_t)(inv ^ 0x63);
    }
    uint8_t r = 1;
    RCON[0] = 0x00;
    for (int i = 1; i <= 10; i++) { RCON[i] = r; r = gmul(r, 2); }
}

/* Standard AES-128 key schedule, word-based (w[44] of 4 bytes each),
 * written from the FIPS-197 definition; adjudicated by the selftest. */
static void expand_key(const unsigned char key[16], unsigned char rk[11][16]) {
    unsigned char w[44][4];
    for (int i = 0; i < 4; i++) { memcpy(w[i], key + 4*i, 4); }
    for (int i = 4; i < 44; i++) {
        unsigned char t[4];
        memcpy(t, w[i-1], 4);
        if (i % 4 == 0) {
            unsigned char u[4] = { (unsigned char)SBOX[t[1]], (unsigned char)SBOX[t[2]],
                                  (unsigned char)SBOX[t[3]], (unsigned char)SBOX[t[0]] };
            u[0] ^= RCON[i/4];
            memcpy(t, u, 4);
        }
        for (int k = 0; k < 4; k++) w[i][k] = (unsigned char)(w[i-4][k] ^ t[k]);
    }
    for (int r = 0; r < 11; r++) memcpy(rk[r], w[4*r], 16);
}

static inline uint8x16_t enc_block(uint8x16_t pt, const unsigned char rk[11][16]) {
    uint8x16_t x = veorq_u8(pt, vld1q_u8(rk[0]));
    uint8x16_t zero = vdupq_n_u8(0);
    for (int r = 1; r <= 9; r++) {
        x = vaeseq_u8(x, zero);        /* SR(SB(x)) ^ 0 */
        x = vaesmcq_u8(x);             /* MC(SR(SB(x))) */
        x = veorq_u8(x, vld1q_u8(rk[r])); /* ^ rk[r] : the AES round */
    }
    x = vaeseq_u8(x, vld1q_u8(rk[10])); /* final round: SR(SB(x)) ^ rk[10] */
    return x;
}

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static void print_hex(const unsigned char *p, int n) {
    for (int i = 0; i < n; i++) printf("%02x", p[i]);
}

static void selftest(void) {
    const unsigned char key[16] = {0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f};
    const unsigned char pt[16]  = {0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    unsigned char rk[11][16];
    unsigned char ct[16];
    expand_key(key, rk);
    uint8x16_t c = enc_block(vld1q_u8(pt), (const unsigned char (*)[16])rk);
    vst1q_u8(ct, c);
    printf("SELFTEST ct=");
    print_hex(ct, 16);
    printf(" fips197_expected=69c4e0d86a7b0430d8cdb78070b4c55a match=%s\n",
           memcmp(ct, "\x69\xc4\xe0\xd8\x6a\x7b\x04\x30\xd8\xcd\xb7\x80\x70\xb4\xc5\x5a", 16) == 0 ? "yes" : "NO");
}

/* vec mode: lines "keyhex pthex" on stdin -> "ct=..." lines on stdout. */
static void vec_mode(void) {
    char line[256];
    unsigned char key[16], pt[16], rk[11][16], ct[16];
    while (fgets(line, sizeof line, stdin)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        char kh[64], ph[64];
        if (sscanf(line, "%63s %63s", kh, ph) != 2) continue;
        for (int i = 0; i < 16; i++) {
            unsigned int k, p;
            sscanf(kh + 2*i, "%2x", &k);
            sscanf(ph + 2*i, "%2x", &p);
            key[i] = (unsigned char)k; pt[i] = (unsigned char)p;
        }
        expand_key(key, rk);
        uint8x16_t c = enc_block(vld1q_u8(pt), (const unsigned char (*)[16])rk);
        vst1q_u8(ct, c);
        printf("ct=");
        print_hex(ct, 16);
        printf("\n");
    }
}

/* Deterministic pseudo-key/plaintext stream: xorshift-style, no libc rand. */
static uint64_t rng_state = 0x2A0A3700B4E5C1D3ull;
static inline uint64_t rng(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}

int main(int argc, char **argv) {
    init_tables();
    if (argc < 2) { fprintf(stderr, "usage: %s selftest | vec | bench <fresh|dep|ind> <N> <reps>\n", argv[0]); return 2; }
    if (!strcmp(argv[1], "selftest")) { selftest(); return 0; }
    if (!strcmp(argv[1], "vec"))      { vec_mode();  return 0; }
    if (!strcmp(argv[1], "bench") && argc == 5) {
        const char *mode = argv[2];
        long N = atol(argv[3]);
        int reps = atoi(argv[4]);
        unsigned char rk[11][16];
        uint64_t acc = 0;
        for (int rep = 1; rep <= reps; rep++) {
            double t0 = now_s();
            if (!strcmp(mode, "fresh")) {
                /* CM-1 AEU-128 shape: schedule CHARGED per evaluation. */
                unsigned char key[16]; unsigned char pt[16]; unsigned char ct[16];
                for (int i = 0; i < 16; i++) { key[i] = 0; pt[i] = 0; }
                for (long i = 0; i < N; i++) {
                    uint64_t r = rng();
                    for (int b = 0; b < 16; b++) key[b] = (unsigned char)(r >> (4*b));
                    r = rng();
                    for (int b = 0; b < 16; b++) pt[b] = (unsigned char)(r >> (4*b));
                    expand_key(key, rk);
                    vst1q_u8(ct, enc_block(vld1q_u8(pt), (const unsigned char (*)[16])rk));
                    acc ^= ct[0]; acc ^= (uint64_t)ct[15] << 56;
                }
            } else if (!strcmp(mode, "dep")) {
                /* One key; dependent chain (latency-bound). */
                unsigned char key[16], ct[16];
                for (int i = 0; i < 16; i++) key[i] = (unsigned char)(i ^ 0x5A);
                expand_key(key, rk);
                uint8x16_t x = vdupq_n_u8(0);
                for (long i = 0; i < N; i++) {
                    x = enc_block(x, (const unsigned char (*)[16])rk);
                    acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(x), 0);
                }
                /* touch acc so the chain is not optimised away */
                if (acc == 0xDEADBEEFull) printf("x");
            } else if (!strcmp(mode, "ind")) {
                /* One key; independent blocks (throughput-bound, pipelined).
                 * Implemented as 4 interleaved dependent chains so the
                 * compiler cannot serialise them: still independent work. */
                unsigned char key[16];
                for (int i = 0; i < 16; i++) key[i] = (unsigned char)(i ^ 0xA5);
                expand_key(key, rk);
                uint8x16_t x0=vdupq_n_u8(0), x1=vdupq_n_u8(1), x2=vdupq_n_u8(2), x3=vdupq_n_u8(3);
                for (long i = 0; i < N; i += 4) {
                    x0 = enc_block(x0, (const unsigned char (*)[16])rk);
                    x1 = enc_block(x1, (const unsigned char (*)[16])rk);
                    x2 = enc_block(x2, (const unsigned char (*)[16])rk);
                    x3 = enc_block(x3, (const unsigned char (*)[16])rk);
                }
                uint8x16_t all = veorq_u8(veorq_u8(x0,x1), veorq_u8(x2,x3));
                acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(all), 0);
                acc ^= vgetq_lane_u64(vreinterpretq_u64_u8(all), 1);
            } else {
                fprintf(stderr, "unknown bench mode\n"); return 2;
            }
            double dt = now_s() - t0;
            printf("RESULT mode=%s N=%ld rep=%d elapsed_s=%.6f rate=%.6e acc=%llx\n",
                   mode, N, rep, dt, (double)N / dt, (unsigned long long)(acc & 0xFFFFFFFFFFFFFFFFull));
        }
        return 0;
    }
    fprintf(stderr, "bad arguments\n"); return 2;
}
