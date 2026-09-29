/* rc8probe_freshfeistel.c -- TASK-20260805-d408ac (BATCH-015, GOAL-AES-003).
 *
 * Purpose: rerun BATCH-009's cipher-substitution comparison (EV-AES-e4c091
 * OUTCOME-A) with a substitute oracle that (a) costs O(1) memory per query
 * (direct evaluation, no stored pair table -- unlike perm128, EV-AES-837cd8),
 * (b) APPROXIMATES AN IDEAL RANDOM PERMUTATION (unlike BATCH-014's RC-D
 * rc8probe_feistel.c, which was deliberately deterministic and non-ideal),
 * and (c) is RESAMPLED WITH A FRESH RANDOM KEY EVERY TRIAL (the opposite of
 * RC-D's fixed key), matching perm128's per-trial fresh-permutation semantics.
 *
 * THE ORACLE (new construction, this task): 128-bit block, 16-round balanced
 * Feistel network on two 64-bit halves. Round function ff_F is built from
 * SipRound, the ARX compression round of SipHash-2-4 (add/rotl/xor only --
 * no GF(2^8) arithmetic, no S-box table, no byte permutation, and NOT the
 * murmur3-fmix64 multiply/xor-shift mix used by BATCH-014's RC-D oracle).
 * Each trial draws a FRESH 128-bit key (k0,k1) from a dedicated per-thread
 * splitmix64 key stream, derives 16 round subkeys from it, and uses that
 * key's permutation for exactly that trial's oracle queries. See
 * src/CONSTRUCTION_JUSTIFICATION.md for the round-count/round-function
 * argument and src/INDEPENDENCE_AUDIT.md for the side-by-side audit.
 *
 * PROVENANCE OF REUSED CODE (disclosed, per the task card "reusing
 * rc8probe.c's plaintext-stream and yoyo-statistic measurement harness"):
 *   - HARNESS machinery copied/adapted from rc8probe.c (BATCH-007,
 *     TASK-20260803-e55757): splitmix64 (sm64), the plaintext-draw-with-
 *     rejection loop, the trivial-swap exclusion, the PW/CW forward/inverse
 *     ShiftRows-diagonal probe geometry, the worker/job threading structure,
 *     the per-thread seed formula, the key derivation from the arm seed for
 *     the LIVE AES arm, and the CLI/JSON reporting shape.
 *   - LIVE ARM code copied from rc8probe.c: gf_init/GLOG/GEXP, gmul/ginv,
 *     SBOX/ISBOX, rotl8/build_aes_sbox, the M2/M3/M9/MB/MD/ME MixColumns
 *     tables, key_expand, add_rk/sub_bytes/inv_sub_bytes/shift_rows/
 *     inv_shift_rows/mix_columns/inv_mix_columns, enc_r/dec_r, and the
 *     do_pin FIPS-197 C.1 KAT + round-trip gate. The live arm IS 5-round
 *     AES itself (that is the comparison's live side); the AES-vocabulary
 *     prohibition applies to the SUBSTITUTE oracle below, which shares none
 *     of it (INDEPENDENCE_AUDIT.md).
 *   - DIGEST formula copied from yoyo_sbox_v4.c (BATCH-009,
 *     TASK-20260803-a0a7b9, lines 280-306): the order-sensitive FNV-1a-style
 *     64-bit digest over 8-byte words of the full (p0,p1) stream,
 *     byte-for-byte the same formula BATCH-009 used for its
 *     plaintext_stream_digest field. Deliberate: this lets this task VERIFY
 *     byte-identical plaintext generation against BATCH-009's recorded
 *     digests by digest equality, closing the V3 gap BATCH-014 disclosed
 *     (its byte-wise FNV digest was a different formula and could not be
 *     compared). This is measurement-harness bookkeeping, not oracle code.
 *   - NOT reused: rc8probe_feistel.c's oracle (feistel_F/feistel_round_keys/
 *     feistel_encrypt/feistel_decrypt -- BATCH-014 RC-D; wrong semantics for
 *     this task AND its round function is contract-prohibited verbatim),
 *     perm128's pair-storage architecture (rc8probe_ideal.c BATCH-011/012;
 *     structurally cannot be O(1) memory), and yoyo_sbox_v2-v4's oracle/
 *     ideal-mode code (v4's ideal branch, injectivity rejection, dom/rng
 *     storage are all absent here).
 *
 * Pure measurement. certificate.kind: none.
 * build: cc -O3 -pthread -o rc8probe_freshfeistel rc8probe_freshfeistel.c
 */
/* B4 EXCLUSION-TOGGLE AUDIT variant (TASK-20260901-e2e66e, BATCH-803af6,
 * GOAL-AES-003; frozen spec IDEA-20260901-02f7c4). Derived from
 * rc8probe_freshfeistel.c with exactly two kinds of change:
 *   (1) THE EXCLUSION TOGGLE: EXCLUDE_TRIVIAL below gates the two
 *       trivial-swap exclusion sites in worker() (the wword gate and the
 *       trial skip). 1 = standard campaign build (exclusion enabled;
 *       counting behavior byte-identical to rc8probe_freshfeistel.c,
 *       verified by the equivalence gate of PREREGISTRATION.md section 5).
 *       0 = audit build (exclusion disabled; trivial trials counted as
 *       ordinary trials). The on/off source pair differs ONLY in that
 *       #define line -- see src/INDEPENDENCE_AUDIT.md.
 *   (2) RECEIPT AUGMENTATION, IDENTICAL IN BOTH BUILDS: a per-thread
 *       trivial-trial index log (trivial_trials entries [thread,t,W],
 *       cap 64/thread + overflow counter) and hit-log entries carrying W
 *       (hit_trials entries [thread,t,W]), so trivial trials are
 *       individually identifiable in the raw receipts, as the idea
 *       record's confounders field requires for B4 to be a toggle rather
 *       than a new run.
 */
#define EXCLUDE_TRIVIAL 0
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <math.h>

/* ---------------- splitmix64 (harness RNG; reused from rc8probe.c) ------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static double wall_now(void){
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

/* ================================================================= */
/* LIVE ARM: 5-round AES, copied from rc8probe.c (BATCH-007).        */
/* This section is the comparison's LIVE side, not the substitute.   */
/* ================================================================= */
static uint8_t GLOG[256], GEXP[512];
static void gf_init(void){
    uint8_t x = 1;
    for(int i = 0; i < 255; i++){
        GEXP[i] = x;
        GLOG[x] = (uint8_t)i;
        uint8_t hi = (uint8_t)(x & 0x80);
        uint8_t t  = (uint8_t)(x << 1);
        if(hi) t ^= 0x1b;
        x = (uint8_t)(t ^ x);
    }
    GLOG[0] = 0;
    for(int i = 255; i < 512; i++) GEXP[i] = GEXP[i - 255];
}
static inline uint8_t gmul(uint8_t a, uint8_t b){
    if(a == 0 || b == 0) return 0;
    return GEXP[(int)GLOG[a] + (int)GLOG[b]];
}
static inline uint8_t ginv(uint8_t a){
    if(a == 0) return 0;
    return GEXP[255 - (int)GLOG[a]];
}
static uint8_t SBOX[256], ISBOX[256];
static inline uint8_t rotl8(uint8_t v, int n){
    return (uint8_t)((v << n) | (v >> (8 - n)));
}
static void build_aes_sbox(void){
    for(int a = 0; a < 256; a++){
        uint8_t x = ginv((uint8_t)a);
        SBOX[a] = (uint8_t)(x ^ rotl8(x,1) ^ rotl8(x,2) ^ rotl8(x,3) ^ rotl8(x,4) ^ 0x63);
    }
}
static int check_bijective(void){
    int cnt[256]; memset(cnt, 0, sizeof cnt);
    for(int i = 0; i < 256; i++) cnt[SBOX[i]]++;
    for(int i = 0; i < 256; i++) if(cnt[i] != 1) return 0;
    for(int i = 0; i < 256; i++) ISBOX[SBOX[i]] = (uint8_t)i;
    for(int i = 0; i < 256; i++) if(ISBOX[SBOX[i]] != (uint8_t)i) return 0;
    for(int i = 0; i < 256; i++) if(SBOX[ISBOX[i]] != (uint8_t)i) return 0;
    return 1;
}
static uint8_t M2[256], M3[256], M9[256], MB[256], MD[256], ME[256];
static void build_mul_tables(void){
    for(int i = 0; i < 256; i++){
        uint8_t v = (uint8_t)i;
        M2[i] = gmul(v, 0x02); M3[i] = gmul(v, 0x03);
        M9[i] = gmul(v, 0x09); MB[i] = gmul(v, 0x0b);
        MD[i] = gmul(v, 0x0d); ME[i] = gmul(v, 0x0e);
    }
}
static void key_expand(const uint8_t key[16], uint8_t rk[11][16]){
    static const uint8_t RCON[10] = {0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
    uint8_t w[44][4];
    for(int i = 0; i < 4; i++) for(int b = 0; b < 4; b++) w[i][b] = key[4*i + b];
    for(int i = 4; i < 44; i++){
        uint8_t t[4];
        t[0] = w[i-1][0]; t[1] = w[i-1][1]; t[2] = w[i-1][2]; t[3] = w[i-1][3];
        if(i % 4 == 0){
            uint8_t r0 = t[0];
            t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = r0;
            for(int b = 0; b < 4; b++) t[b] = SBOX[t[b]];
            t[0] ^= RCON[i/4 - 1];
        }
        for(int b = 0; b < 4; b++) w[i][b] = (uint8_t)(w[i-4][b] ^ t[b]);
    }
    for(int i = 0; i <= 10; i++)
        for(int c = 0; c < 4; c++)
            for(int b = 0; b < 4; b++)
                rk[i][4*c + b] = w[4*i + c][b];
}
static inline void add_rk(uint8_t s[16], const uint8_t k[16]){
    for(int i = 0; i < 16; i++) s[i] ^= k[i];
}
static inline void sub_bytes(uint8_t s[16]){
    for(int i = 0; i < 16; i++) s[i] = SBOX[s[i]];
}
static inline void inv_sub_bytes(uint8_t s[16]){
    for(int i = 0; i < 16; i++) s[i] = ISBOX[s[i]];
}
static inline void shift_rows(uint8_t s[16]){
    uint8_t t[16];
    for(int c = 0; c < 4; c++)
        for(int r = 0; r < 4; r++)
            t[4*c + r] = s[4*((c + r) & 3) + r];
    memcpy(s, t, 16);
}
static inline void inv_shift_rows(uint8_t s[16]){
    uint8_t t[16];
    for(int c = 0; c < 4; c++)
        for(int r = 0; r < 4; r++)
            t[4*c + r] = s[4*((c - r) & 3) + r];
    memcpy(s, t, 16);
}
static inline void mix_columns(uint8_t s[16]){
    for(int c = 0; c < 4; c++){
        uint8_t *p = s + 4*c;
        uint8_t a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = (uint8_t)(M2[a0] ^ M3[a1] ^ a2      ^ a3);
        p[1] = (uint8_t)(a0      ^ M2[a1] ^ M3[a2] ^ a3);
        p[2] = (uint8_t)(a0      ^ a1      ^ M2[a2] ^ M3[a3]);
        p[3] = (uint8_t)(M3[a0] ^ a1      ^ a2      ^ M2[a3]);
    }
}
static inline void inv_mix_columns(uint8_t s[16]){
    for(int c = 0; c < 4; c++){
        uint8_t *p = s + 4*c;
        uint8_t a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
        p[0] = (uint8_t)(ME[a0] ^ MB[a1] ^ MD[a2] ^ M9[a3]);
        p[1] = (uint8_t)(M9[a0] ^ ME[a1] ^ MB[a2] ^ MD[a3]);
        p[2] = (uint8_t)(MD[a0] ^ M9[a1] ^ ME[a2] ^ MB[a3]);
        p[3] = (uint8_t)(MB[a0] ^ MD[a1] ^ M9[a2] ^ ME[a3]);
    }
}
static void enc_r(const uint8_t in[16], uint8_t out[16], const uint8_t rk[11][16], int r){
    uint8_t s[16]; memcpy(s, in, 16);
    add_rk(s, rk[0]);
    for(int i = 1; i < r; i++){
        sub_bytes(s); shift_rows(s); mix_columns(s); add_rk(s, rk[i]);
    }
    sub_bytes(s); shift_rows(s); add_rk(s, rk[r]);
    memcpy(out, s, 16);
}
static void dec_r(const uint8_t in[16], uint8_t out[16], const uint8_t rk[11][16], int r){
    uint8_t s[16]; memcpy(s, in, 16);
    add_rk(s, rk[r]); inv_shift_rows(s); inv_sub_bytes(s);
    for(int i = r - 1; i >= 1; i--){
        add_rk(s, rk[i]); inv_mix_columns(s); inv_shift_rows(s); inv_sub_bytes(s);
    }
    add_rk(s, rk[0]);
    memcpy(out, s, 16);
}
/* FIPS-197 C.1 KAT + round-trip pin gate, copied from rc8probe.c. */
static int do_pin(int is_aes, uint64_t rtseed, int nvec, int quiet){
    int kat_enc = -1, kat_dec = -1;
    char ctbuf[33]; ctbuf[0] = 0;
    if(is_aes){
        const uint8_t K[16]  = {0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,
                                0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f};
        const uint8_t PT[16] = {0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                                0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
        const uint8_t CT[16] = {0x69,0xc4,0xe0,0xd8,0x6a,0x7b,0x04,0x30,
                                0xd8,0xcd,0xb7,0x80,0x70,0xb4,0xc5,0x5a};
        uint8_t rk[11][16]; key_expand(K, rk);
        uint8_t y[16], x[16];
        enc_r(PT, y, rk, 10); kat_enc = (memcmp(y, CT, 16) == 0);
        for(int i = 0; i < 16; i++) sprintf(ctbuf + 2*i, "%02x", y[i]);
        dec_r(CT, x, rk, 10); kat_dec = (memcmp(x, PT, 16) == 0);
    }
    uint64_t st = rtseed; int fails = 0, first_fail_r = 0;
    for(int v = 0; v < nvec; v++){
        uint8_t k[16], pt[16];
        for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int q=0;q<8;q++) k[i+q]  = (uint8_t)(z >> (8*q)); }
        for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int q=0;q<8;q++) pt[i+q] = (uint8_t)(z >> (8*q)); }
        uint8_t rk[11][16]; key_expand(k, rk);
        for(int r = 1; r <= 10; r++){
            uint8_t c[16], e[16];
            enc_r(pt, c, rk, r); dec_r(c, e, rk, r);
            if(memcmp(e, pt, 16) != 0){ fails++; if(!first_fail_r) first_fail_r = r; }
        }
    }
    int pass = (fails == 0) && (!is_aes || (kat_enc == 1 && kat_dec == 1));
    if(!quiet){
        printf("  \"fips197_c1_kat_applicable\": %s,\n", is_aes ? "true" : "false");
        if(is_aes){
            printf("  \"fips197_c1_kat_encrypt_match\": %s,\n", kat_enc ? "true" : "false");
            printf("  \"fips197_c1_kat_decrypt_match\": %s,\n", kat_dec ? "true" : "false");
            printf("  \"fips197_c1_kat_ciphertext_computed\": \"%s\",\n", ctbuf);
            printf("  \"fips197_c1_kat_ciphertext_expected\": \"69c4e0d86a7b0430d8cdb78070b4c55a\",\n");
        }
        printf("  \"roundtrip_vectors\": %d,\n", nvec);
        printf("  \"roundtrip_checks\": %d,\n", nvec * 10);
        printf("  \"roundtrip_failures\": %d,\n", fails);
        printf("  \"roundtrip_first_failure_round\": %d,\n", first_fail_r);
        printf("  \"pin_seed\": %llu,\n", (unsigned long long)rtseed);
        printf("  \"pin_pass\": %s,\n", pass ? "true" : "false");
    }
    return pass;
}

/* ================================================================= */
/* THE SUBSTITUTE ORACLE (new construction, this task):              */
/* fresh-key-per-trial 16-round balanced Feistel, SipRound-based     */
/* round function. Independent of AES and of every prior campaign    */
/* oracle -- see src/INDEPENDENCE_AUDIT.md.                          */
/* ================================================================= */
#define FF_ROUNDS 16

static inline uint64_t rotl64(uint64_t x, int b){
    return (x << b) | (x >> (64 - b));
}
/* SipRound: the ARX compression round of SipHash-2-4. Addition mod 2^64,
 * rotation, xor ONLY -- no multiplication, no GF(2^8), no table lookup,
 * no byte-array permutation. (SipHash-2-4 reference: Aumasson & Bernstein,
 * "SipHash: a fast short-input PRF", INDOCRYPT 2012 -- citation provenance
 * 'recalled', recorded per AGENTS.md rule 9 in CONSTRUCTION_JUSTIFICATION.md.) */
static inline void sipround(uint64_t *v0, uint64_t *v1, uint64_t *v2, uint64_t *v3){
    *v0 += *v1; *v1 = rotl64(*v1, 13); *v1 ^= *v0; *v0 = rotl64(*v0, 32);
    *v2 += *v3; *v3 = rotl64(*v3, 16); *v3 ^= *v2;
    *v0 += *v3; *v3 = rotl64(*v3, 21); *v3 ^= *v0;
    *v2 += *v1; *v1 = rotl64(*v1, 17); *v1 ^= *v2; *v2 = rotl64(*v2, 32);
}
/* Round function F(x, k): SipHash-style initialization of the 4-word state
 * from (x, k) with SipHash's public IV constants, two SipRounds, and the
 * SipHash finalization xor. A keyed 64-bit->64-bit function built from a
 * cryptographically designed PRF round; structurally distinct from both
 * AES's round function and from RC-D's murmur3-fmix64 mix. */
static inline uint64_t ff_F(uint64_t x, uint64_t k){
    uint64_t v0 = k ^ 0x736f6d6570736575ULL;
    uint64_t v1 = x ^ 0x646f72616e646f6dULL;
    uint64_t v2 = k ^ 0x6c7967656e657261ULL;
    uint64_t v3 = x ^ 0x7465646279746573ULL;
    sipround(&v0, &v1, &v2, &v3);
    sipround(&v0, &v1, &v2, &v3);
    return v0 ^ v1 ^ v2 ^ v3;
}
/* Per-TRIAL round-key derivation. Called inside the trial loop with the
 * trial's freshly drawn key (k0,k1); RK lives on the worker's stack. */
static inline void ff_trial_subkeys(uint64_t k0, uint64_t k1, uint64_t RK[FF_ROUNDS]){
    uint64_t st = k0 ^ rotl64(k1, 27) ^ 0x6A09E667F3BCC908ULL;
    for(int i = 0; i < FF_ROUNDS; i++) RK[i] = sm64(&st);
}
/* Balanced Feistel ladder with per-trial RK passed in (NO global key state,
 * unlike RC-D's fixed global RK[]). O(1) memory per query. */
static void ff_encrypt(const uint8_t in[16], uint8_t out[16], const uint64_t RK[FF_ROUNDS]){
    uint64_t L = 0, R = 0;
    for(int i = 0; i < 8; i++) L |= (uint64_t)in[i]     << (8*i);
    for(int i = 0; i < 8; i++) R |= (uint64_t)in[8 + i] << (8*i);
    for(int i = 0; i < FF_ROUNDS; i++){
        uint64_t nL = R;
        uint64_t nR = L ^ ff_F(R, RK[i]);
        L = nL; R = nR;
    }
    for(int i = 0; i < 8; i++) out[i]     = (uint8_t)(L >> (8*i));
    for(int i = 0; i < 8; i++) out[8 + i] = (uint8_t)(R >> (8*i));
}
static void ff_decrypt(const uint8_t in[16], uint8_t out[16], const uint64_t RK[FF_ROUNDS]){
    uint64_t L = 0, R = 0;
    for(int i = 0; i < 8; i++) L |= (uint64_t)in[i]     << (8*i);
    for(int i = 0; i < 8; i++) R |= (uint64_t)in[8 + i] << (8*i);
    for(int i = FF_ROUNDS - 1; i >= 0; i--){
        uint64_t pR = L;
        uint64_t pL = R ^ ff_F(L, RK[i]);
        L = pL; R = pR;
    }
    for(int i = 0; i < 8; i++) out[i]     = (uint8_t)(L >> (8*i));
    for(int i = 0; i < 8; i++) out[8 + i] = (uint8_t)(R >> (8*i));
}

/* ---------------- geometry (byte-identical to rc8probe.c) --------------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j = 0; j < 4; j++) for(int row = 0; row < 4; row++){
        PW[j][row] = 4 * (((j + row) % 4 + 4) % 4) + row;   /* forward SR diagonals */
        CW[j][row] = 4 * (((j - row) % 4 + 4) % 4) + row;   /* inverse SR diagonals */
    }
}

/* Per-thread key-stream seeds for the fresh-key oracle. Constants chosen to
 * be disjoint from the plaintext-thread-seed constants (0x1234567891,
 * 0x9E3779B97F4A7C15) and from the AES-arm key-derivation constant
 * (0xA5A5A5A5A5A5A5A5); stream-gap exclusion is computed and reported at run
 * time (stream_gap_* fields) exactly as BATCH-009 did for its two streams. */
#define KEYARM_C1 0x517CC1B727220A95ULL
#define KEYARM_C2 0x6A09E667F3BCC908ULL
static inline uint64_t key_thread_seed(uint64_t seed, int armid, int t){
    return seed ^ ((uint64_t)armid * KEYARM_C1) ^ ((uint64_t)(t + 1) * KEYARM_C2);
}

/* ---------------- worker (adapted from rc8probe.c's worker) ------------- */
typedef struct {
    uint64_t ntrials, seed_thread;
    int oracle;                 /* 0 = live AES (enc_r/dec_r), 1 = fresh-feistel */
    int rounds, amask, smask;
    const uint8_t (*rk)[16];    /* live AES arm only */
    uint64_t seed_key_thread;   /* fresh-feistel arm only */
    uint64_t whist[5], trivial, wword[4], wge1;
    uint64_t hit_thread_idx[64]; int hit_count, hit_overflow;
    uint8_t hit_w[64];                       /* B4 receipt augmentation: W per logged hit */
    uint64_t trivial_idx[64]; uint8_t trivial_w[64];  /* B4 receipt augmentation: trivial log */
    int trivial_log_count; uint64_t trivial_log_overflow;
    uint64_t pstream_digest;
    uint64_t kstream_digest;    /* fresh-feistel: order-sensitive digest over drawn keys */
    uint64_t first_keys[4][2];  /* first 4 trial keys (k0,k1), for the record */
    int first_keys_n;
} job;

#define HIT_LOG_CAP 64

static void *worker(void *arg){
    job *J = (job*)arg;
    uint64_t st = J->seed_thread;
    uint64_t kst = J->seed_key_thread;
    const uint8_t (*rk)[16] = J->rk;
    int r = J->rounds;
    uint8_t p0[16], p1[16], c0[16], c1[16], q0[16], q1[16], d[16];
    uint64_t RK[FF_ROUNDS];
    /* Digest init and formula copied from yoyo_sbox_v4.c (BATCH-009): FNV-1a
     * 64 over 8-byte little-endian words of the full (p0,p1) stream. */
    uint64_t pdig = 1469598103934665603ULL;
    uint64_t kdig = 1469598103934665603ULL;
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
        {   uint64_t w;
            for(int i = 0; i < 16; i += 8){ memcpy(&w, p0 + i, 8); pdig = (pdig ^ w) * 1099511628211ULL; }
            for(int i = 0; i < 16; i += 8){ memcpy(&w, p1 + i, 8); pdig = (pdig ^ w) * 1099511628211ULL; }
        }
        if(J->oracle == 0){
            enc_r(p0, c0, rk, r);
            enc_r(p1, c1, rk, r);
        } else {
            /* FRESH RANDOM KEY PER TRIAL: two consecutive draws from this
             * thread's dedicated key stream form this trial's 128-bit key;
             * subkeys are derived from them and used for this trial only. */
            uint64_t k0 = sm64(&kst), k1 = sm64(&kst);
            kdig = (kdig ^ k0) * 1099511628211ULL;
            kdig = (kdig ^ k1) * 1099511628211ULL;
            if(J->first_keys_n < 4){
                J->first_keys[J->first_keys_n][0] = k0;
                J->first_keys[J->first_keys_n][1] = k1;
                J->first_keys_n++;
            }
            ff_trial_subkeys(k0, k1, RK);
            ff_encrypt(p0, c0, RK);
            ff_encrypt(p1, c1, RK);
        }
        int trivial = 1;
        for(int j = 0; j < 4; j++) if(J->smask & (1 << j))
            for(int row = 0; row < 4; row++){
                int i = CW[j][row];
                uint8_t x = c0[i], y = c1[i];
                if(x != y) trivial = 0;
                c0[i] = y; c1[i] = x;
            }
        if(J->oracle == 0){
            dec_r(c0, q0, rk, r);
            dec_r(c1, q1, rk, r);
        } else {
            ff_decrypt(c0, q0, RK);
            ff_decrypt(c1, q1, RK);
        }
        for(int i = 0; i < 16; i++) d[i] = (uint8_t)(q0[i] ^ q1[i]);
        int W = 0;
        for(int j = 0; j < 4; j++){
            int z = 1;
            for(int row = 0; row < 4; row++) if(d[PW[j][row]]) { z = 0; break; }
            if(z){ W++; if(!EXCLUDE_TRIVIAL || !trivial) J->wword[j]++; }  /* B4 TOGGLE SITE 1 */
        }
        if(trivial){
            J->trivial++;
            /* B4 receipt augmentation (identical in both builds): log every
             * trivial trial individually so the toggle delta is checkable
             * trial-by-trial from the raw receipts. */
            if(J->trivial_log_count < HIT_LOG_CAP){
                J->trivial_idx[J->trivial_log_count] = t;
                J->trivial_w[J->trivial_log_count] = (uint8_t)W;
                J->trivial_log_count++;
            } else J->trivial_log_overflow++;
            if(EXCLUDE_TRIVIAL) continue;  /* B4 TOGGLE SITE 2 */
        }
        J->whist[W]++;
        if(W >= 1){
            J->wge1++;
            if(J->hit_count < HIT_LOG_CAP){
                J->hit_thread_idx[J->hit_count] = t;
                J->hit_w[J->hit_count] = (uint8_t)W;   /* B4 receipt augmentation */
                J->hit_count++;
            }
            else J->hit_overflow++;
        }
    }
    J->pstream_digest = pdig;
    J->kstream_digest = kdig;
    return NULL;
}

/* ---------------- stream-gap exclusion ----------------------------------- */
/* All splitmix64 streams walk ONE cycle of length 2^64 (state += odd const).
 * Two same-step progressions either never meet in the measured window or
 * coincide from the meeting point on; the circular shift between them is
 * delta = (s_b - s_a) * c^{-1} mod 2^64. Report min circular distance, as
 * BATCH-009 did with stream_gap_min_log2 for its two streams. */
static uint64_t sm64_step_inverse(void){
    uint64_t c = 0x9E3779B97F4A7C15ULL;
    uint64_t inv = 1;
    for(int i = 0; i < 6; i++) inv = inv * (2 - c * inv);  /* Newton mod 2^64 */
    return inv;
}
static int floor_log2_u64(uint64_t x){
    if(x == 0) return -1;
    return 63 - __builtin_clzll(x);
}
static uint64_t circ_shift(uint64_t sa, uint64_t sb, uint64_t cinv){
    return (sb - sa) * cinv;
}
static int min_gap_log2(const uint64_t *seeds, int n, uint64_t cinv){
    int best = 64;
    for(int i = 0; i < n; i++) for(int j = i + 1; j < n; j++){
        uint64_t d = circ_shift(seeds[i], seeds[j], cinv);
        uint64_t dist = d < (UINT64_MAX - d) ? d : (UINT64_MAX - d);
        int lg = floor_log2_u64(dist);
        if(lg < best) best = lg;
    }
    return best;
}

/* ---------------- fresh-key oracle self-gates ----------------------------- */
/* Round-trip + 2-point injectivity under MANY fresh keys. */
static int ff_gate(uint64_t seed, int nkeys, int quiet){
    uint64_t st = seed ^ 0xFE157E157E157E15ULL;
    int rt_fail = 0, inj_fail = 0;
    uint8_t x[16], y[16], c[16], e[16], c2[16];
    for(int v = 0; v < nkeys; v++){
        uint64_t k0 = sm64(&st), k1 = sm64(&st);
        uint64_t RK[FF_ROUNDS]; ff_trial_subkeys(k0, k1, RK);
        for(int q = 0; q < 4; q++){
            for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int b=0;b<8;b++) x[i+b] = (uint8_t)(z >> (8*b)); }
            for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int b=0;b<8;b++) y[i+b] = (uint8_t)(z >> (8*b)); }
            if(memcmp(x, y, 16) == 0){ y[0] ^= 1; }
            ff_encrypt(x, c, RK);
            ff_decrypt(c, e, RK);
            if(memcmp(e, x, 16) != 0) rt_fail++;
            ff_encrypt(y, c2, RK);
            if(memcmp(c, c2, 16) == 0) inj_fail++;
        }
    }
    if(!quiet){
        printf("  \"ff_gate_fresh_keys\": %d,\n", nkeys);
        printf("  \"ff_gate_roundtrip_failures\": %d,\n", rt_fail);
        printf("  \"ff_gate_injectivity_failures\": %d,\n", inj_fail);
        printf("  \"ff_gate_pass\": %s,\n", (rt_fail == 0 && inj_fail == 0) ? "true" : "false");
    }
    return rt_fail == 0 && inj_fail == 0;
}

/* Key-distinctness check: simulate the exact per-thread key streams for the
 * given thread seeds and verify all drawn 128-bit keys are pairwise distinct
 * (open-addressed set; memory = slots*16 bytes + occupancy bits). */
typedef struct { uint64_t lo, hi; } key128;
static int keycheck(const uint64_t *kseeds, int nthr, int per_thread_log2,
                    uint64_t *out_checked, uint64_t *out_dups, size_t *out_table_bytes){
    uint64_t M = 1ULL << per_thread_log2;
    uint64_t total = M * (uint64_t)nthr;
    int lgslots = per_thread_log2 + 4;               /* load factor ~1/16 */
    if(lgslots > 26) lgslots = 26;
    uint64_t slots = 1ULL << lgslots;
    key128 *tab = calloc(slots, sizeof(key128));
    uint8_t *occ = calloc(slots / 8 + 1, 1);
    if(!tab || !occ){ free(tab); free(occ); return -1; }
    uint64_t mask = slots - 1, dups = 0, checked = 0;
    for(int t = 0; t < nthr; t++){
        uint64_t s = kseeds[t];
        for(uint64_t i = 0; i < M; i++){
            key128 k; k.lo = sm64(&s); k.hi = sm64(&s);
            uint64_t h = k.lo ^ rotl64(k.hi, 32);
            h ^= h >> 33; h *= 0xff51afd7ed558ccdULL; h ^= h >> 33;  /* set hash only */
            uint64_t idx = h & mask;
            for(;;){
                if(!(occ[idx >> 3] & (1u << (idx & 7)))){
                    occ[idx >> 3] |= (uint8_t)(1u << (idx & 7));
                    tab[idx] = k; break;
                }
                if(tab[idx].lo == k.lo && tab[idx].hi == k.hi){ dups++; break; }
                idx = (idx + 1) & mask;
            }
            checked++;
        }
    }
    *out_checked = checked; *out_dups = dups;
    *out_table_bytes = slots * sizeof(key128) + slots / 8 + 1;
    free(tab); free(occ);
    return 0;
}

/* Empirical sanity battery on the fresh-key construction's realized outputs.
 * Working-assumption check (NOT a proof of idealness): under a uniform
 * random permutation, for fixed input the output byte is uniform, and for
 * two fixed distinct inputs the outputs never collide but agree on any one
 * byte with probability ~2^-8. */
static void qualcheck(uint64_t seed, uint64_t N, double *chi2_out, int npos,
                      const int *pos, uint64_t *match_obs, uint64_t *inj_coll){
    uint64_t st = seed ^ 0x9A11CE9A11CE9A11ULL;
    uint8_t p[16], p2[16], c[16], c2[16];
    for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int b=0;b<8;b++) p[i+b]  = (uint8_t)(z >> (8*b)); }
    for(int i = 0; i < 16; i += 8){ uint64_t z = sm64(&st); for(int b=0;b<8;b++) p2[i+b] = (uint8_t)(z >> (8*b)); }
    if(memcmp(p, p2, 16) == 0) p2[0] ^= 1;
    uint64_t hist[4][256]; memset(hist, 0, sizeof hist);
    uint64_t matches = 0, coll = 0;
    for(uint64_t t = 0; t < N; t++){
        uint64_t k0 = sm64(&st), k1 = sm64(&st);
        uint64_t RK[FF_ROUNDS]; ff_trial_subkeys(k0, k1, RK);
        ff_encrypt(p, c, RK);
        ff_encrypt(p2, c2, RK);
        if(memcmp(c, c2, 16) == 0) coll++;
        if(c[0] == c2[0]) matches++;
        for(int q = 0; q < npos; q++) hist[q][c[pos[q]]]++;
    }
    double expc = (double)N / 256.0;
    for(int q = 0; q < npos; q++){
        double s = 0.0;
        for(int b = 0; b < 256; b++){ double dv = (double)hist[q][b] - expc; s += dv * dv / expc; }
        chi2_out[q] = s;
    }
    *match_obs = matches; *inj_coll = coll;
}

/* ---------------- run an arm (shared by arm mode and rate probes) --------- */
typedef struct {
    const char *name; int oracle; int rounds, amask, smask, log2N;
    uint64_t seed; int armid, nthr;
    double elapsed;
} arm_spec;

static int run_arm(const arm_spec *A, const uint8_t rk[11][16], int emit_json){
    uint64_t N = 1ULL << A->log2N;
    job *jobs = calloc(A->nthr, sizeof(job));
    pthread_t *th = calloc(A->nthr, sizeof(pthread_t));
    uint64_t cinv = sm64_step_inverse();
    uint64_t pseed[64], kseed[64];
    uint64_t per = N / A->nthr;
    double t0 = wall_now();
    for(int t = 0; t < A->nthr; t++){
        jobs[t].ntrials = per + (t == 0 ? N - per * A->nthr : 0);
        jobs[t].seed_thread = A->seed ^ ((uint64_t)A->armid * 0x1234567891ULL)
                            ^ ((uint64_t)(t + 1) * 0x9E3779B97F4A7C15ULL);
        jobs[t].oracle = A->oracle;
        jobs[t].rounds = A->rounds; jobs[t].amask = A->amask; jobs[t].smask = A->smask;
        jobs[t].rk = rk;
        jobs[t].seed_key_thread = key_thread_seed(A->seed, A->armid, t);
        pseed[t] = jobs[t].seed_thread; kseed[t] = jobs[t].seed_key_thread;
    }
    for(int t = 0; t < A->nthr; t++) pthread_create(&th[t], NULL, worker, &jobs[t]);
    for(int t = 0; t < A->nthr; t++) pthread_join(th[t], NULL);
    double t1 = wall_now();
    ((arm_spec*)A)->elapsed = t1 - t0;

    uint64_t wh[5] = {0}, wword[4] = {0}, trivial = 0, wge1 = 0, hit_overflow = 0;
    for(int t = 0; t < A->nthr; t++){
        for(int i = 0; i < 5; i++) wh[i] += jobs[t].whist[i];
        for(int i = 0; i < 4; i++) wword[i] += jobs[t].wword[i];
        trivial += jobs[t].trivial; wge1 += jobs[t].wge1; hit_overflow += jobs[t].hit_overflow;
    }
    int pgap = min_gap_log2(pseed, A->nthr, cinv);
    int kgap = min_gap_log2(kseed, A->nthr, cinv);
    /* cross-family exclusion: any key-stream seed equal to any plaintext-stream seed */
    int cross_equal = 0;
    for(int i = 0; i < A->nthr; i++) for(int j = 0; j < A->nthr; j++)
        if(kseed[i] == pseed[j]) cross_equal = 1;

    if(emit_json){
        printf("{\n  \"probe\": \"rc8probe_freshfeistel\",\n  \"arm\": \"%s\",\n", A->name);
        printf("  \"build\": \"B4-exclusion-toggle-audit\",\n");
        printf("  \"exclude_trivial_build\": %d,\n", EXCLUDE_TRIVIAL);
        printf("  \"task_id\": \"TASK-20260901-e2e66e\",\n");
        if(A->oracle == 0){
            printf("  \"oracle\": \"live_aes_r%d_byte_level_rc8probe_code\",\n", A->rounds);
            printf("  \"sbox_is_aes\": true,\n");
            printf("  \"sbox_first8\": [");
            for(int i = 0; i < 8; i++) printf("%d%s", SBOX[i], i < 7 ? "," : "");
            printf("],\n");
            printf("  \"ideal_permutation\": false,\n");
            printf("  \"resampled_per_trial\": false,\n");
            printf("  \"fresh_key_per_trial\": false,\n");
        } else {
            printf("  \"oracle\": \"fresh_key_per_trial_feistel16_64bit_halves_sipround_F\",\n");
            printf("  \"rounds_field_ignored_input\": %d,\n", A->rounds);
            printf("  \"feistel_rounds_actual\": %d,\n", FF_ROUNDS);
            printf("  \"round_function\": \"SipRound x2 keyed mix (SipHash-2-4 compression round; add/rotl/xor only)\",\n");
            printf("  \"ideal_permutation\": false,\n");
            printf("  \"ideal_approximating_construction\": true,\n");
            printf("  \"resampled_per_trial\": true,\n");
            printf("  \"fresh_key_per_trial\": true,\n");
            printf("  \"fresh_key_mechanism\": \"two consecutive splitmix64 draws per trial from a dedicated per-thread key stream; per-trial subkey derivation; NO global key state (contrast RC-D's global fixed RK[])\",\n");
        }
        printf("  \"amask\": %d,\n  \"smask\": %d,\n", A->amask, A->smask);
        printf("  \"trials\": %llu,\n  \"log2N\": %d,\n  \"seed\": %llu,\n  \"arm_id\": %d,\n  \"threads\": %d,\n",
               (unsigned long long)N, A->log2N, (unsigned long long)A->seed, A->armid, A->nthr);
        printf("  \"thread_seeds\": [");
        for(int t = 0; t < A->nthr; t++) printf("%llu%s", (unsigned long long)jobs[t].seed_thread, t < A->nthr-1 ? "," : "");
        printf("],\n");
        printf("  \"key_stream_seeds\": [");
        for(int t = 0; t < A->nthr; t++) printf("%llu%s", (unsigned long long)jobs[t].seed_key_thread, t < A->nthr-1 ? "," : "");
        printf("],\n");
        printf("  \"stream_gap_min_log2_plaintext_threads\": %d,\n", pgap);
        printf("  \"stream_gap_min_log2_key_threads\": %d,\n", kgap);
        printf("  \"key_stream_seed_equals_any_plaintext_stream_seed\": %s,\n", cross_equal ? "true" : "false");
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
        printf("  \"plaintext_stream_digest\": [");
        for(int t = 0; t < A->nthr; t++) printf("\"%016llx\"%s", (unsigned long long)jobs[t].pstream_digest, t < A->nthr-1 ? "," : "");
        printf("],\n");
        if(A->oracle == 1){
            printf("  \"key_stream_digest\": [");
            for(int t = 0; t < A->nthr; t++) printf("\"%016llx\"%s", (unsigned long long)jobs[t].kstream_digest, t < A->nthr-1 ? "," : "");
            printf("],\n");
            printf("  \"first_trial_keys_hex\": [");
            int first = 1;
            for(int t = 0; t < A->nthr; t++)
                for(int i = 0; i < jobs[t].first_keys_n; i++){
                    if(!first) printf(",");
                    printf("[\"%016llx%016llx\",%d]",
                           (unsigned long long)jobs[t].first_keys[i][0],
                           (unsigned long long)jobs[t].first_keys[i][1], t);
                    first = 0;
                }
            printf("],\n");
            printf("  \"distinct_keys_within_thread\": \"provable -- splitmix64 state advances by an odd constant (single 2^64 cycle, bijective output mix), so consecutive 128-bit key pairs cannot repeat within 2^64 >> trials drawn; cross-thread exclusion reported via stream_gap_min_log2_key_threads and verified empirically by the selfcheck keycheck\",\n");
        }
        printf("  \"elapsed_seconds_measured\": %.9f,\n", t1 - t0);
        printf("  \"measured_rate_trials_per_sec\": %.1f,\n", (double)N / (t1 - t0));
        { int hl = 0; for(int t = 0; t < A->nthr; t++) hl += jobs[t].hit_count;
          printf("  \"hit_trials_logged\": %d,\n", hl); }
        printf("  \"hit_log_overflow\": %llu,\n", (unsigned long long)hit_overflow);
        printf("  \"hit_trials\": [");
        { int f2 = 1;
          for(int t = 0; t < A->nthr; t++)
            for(int i = 0; i < jobs[t].hit_count; i++){
                if(!f2) printf(",");
                printf("[%d,%llu,%d]", t, (unsigned long long)jobs[t].hit_thread_idx[i], (int)jobs[t].hit_w[i]);
                f2 = 0;
            }
        }
        printf("],\n");
        printf("  \"hit_log_cap\": %d,\n", HIT_LOG_CAP);
        { uint64_t tlov = 0; int tlc = 0;
          for(int t = 0; t < A->nthr; t++){ tlov += jobs[t].trivial_log_overflow; tlc += jobs[t].trivial_log_count; }
          printf("  \"trivial_trials_logged\": %d,\n", tlc);
          printf("  \"trivial_log_overflow\": %llu,\n", (unsigned long long)tlov);
          printf("  \"trivial_log_cap_per_thread\": %d,\n", HIT_LOG_CAP);
          printf("  \"trivial_trials\": [");
          int f3 = 1;
          for(int t = 0; t < A->nthr; t++)
            for(int i = 0; i < jobs[t].trivial_log_count; i++){
                if(!f3) printf(",");
                printf("[%d,%llu,%d]", t, (unsigned long long)jobs[t].trivial_idx[i], (int)jobs[t].trivial_w[i]);
                f3 = 0;
            }
          printf("]\n");
        }
        printf("}\n");
    }
    free(jobs); free(th);
    return 0;
}

/* ---------------- selfcheck mode ------------------------------------------ */
static int do_selfcheck(uint64_t seed, int rate_threads){
    printf("{\n  \"mode\": \"selfcheck\",\n  \"probe\": \"rc8probe_freshfeistel\",\n  \"seed\": %llu,\n",
           (unsigned long long)seed);
    int pin_ok = do_pin(1, 60600002ULL, 64, 0);
    int ffok = ff_gate(seed, 4096, 0);

    /* key distinctness: 4 simulated thread key streams at this seed/armid,
     * 2^20 keys each (the arm geometry uses threads <= 4). */
    uint64_t kseeds[4];
    for(int t = 0; t < 4; t++) kseeds[t] = key_thread_seed(seed, 1, t);
    uint64_t checked = 0, dups = 1; size_t table_bytes = 0;
    int kc = keycheck(kseeds, 4, 20, &checked, &dups, &table_bytes);
    printf("  \"keycheck_threads\": 4,\n");
    printf("  \"keycheck_keys_per_thread_log2\": 20,\n");
    printf("  \"keycheck_keys_checked\": %llu,\n", (unsigned long long)checked);
    printf("  \"keycheck_duplicate_keys\": %llu,\n", (unsigned long long)dups);
    printf("  \"keycheck_table_bytes\": %llu,\n", (unsigned long long)table_bytes);
    printf("  \"keycheck_pass\": %s,\n", (kc == 0 && dups == 0) ? "true" : "false");

    /* empirical sanity battery, N = 2^18 fresh-key trials */
    double chi2[4]; uint64_t match_obs = 0, inj_coll = 1;
    const int pos[4] = {0, 5, 8, 13};
    qualcheck(seed, 1ULL << 18, chi2, 4, pos, &match_obs, &inj_coll);
    double expm = (double)(1ULL << 18) / 256.0;
    double zm = ((double)match_obs - expm) / sqrt(expm * (255.0/256.0));
    printf("  \"qualcheck_trials_log2\": 18,\n");
    printf("  \"qualcheck_byte_positions\": [0,5,8,13],\n");
    printf("  \"qualcheck_chi2\": [%.3f,%.3f,%.3f,%.3f],\n", chi2[0], chi2[1], chi2[2], chi2[3]);
    printf("  \"qualcheck_chi2_df\": 255,\n");
    printf("  \"qualcheck_chi2_gate_max\": 400.0,\n");
    printf("  \"qualcheck_chi2_pass\": %s,\n",
           (chi2[0] < 400 && chi2[1] < 400 && chi2[2] < 400 && chi2[3] < 400) ? "true" : "false");
    printf("  \"qualcheck_byte0_match_count\": %llu,\n", (unsigned long long)match_obs);
    printf("  \"qualcheck_byte0_match_expected\": %.1f,\n", expm);
    printf("  \"qualcheck_byte0_match_z\": %.3f,\n", zm);
    printf("  \"qualcheck_full_output_collisions\": %llu,\n", (unsigned long long)inj_coll);
    printf("  \"qualcheck_pass\": %s,\n",
           (chi2[0] < 400 && chi2[1] < 400 && chi2[2] < 400 && chi2[3] < 400
            && inj_coll == 0 && zm > -5.5 && zm < 5.5) ? "true" : "false");

    /* rate probes at 2^20 trials with the arm thread count: timing basis for
     * the exposure decision; hit counts here are NOT decision-relevant. */
    uint8_t rk[11][16];
    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i = 0; i < 16; i += 8){
        uint64_t z = sm64(&kst);
        for(int q = 0; q < 8; q++) key[i + q] = (uint8_t)(z >> (8*q));
    }
    key_expand(key, rk);
    arm_spec pa = {"RATEPROBE-AES-2p20", 0, 5, 1, 1, 20, seed, 1, rate_threads, 0};
    run_arm(&pa, rk, 0);
    printf("  \"rateprobe_aes_trials_log2\": 20,\n");
    printf("  \"rateprobe_aes_elapsed_seconds\": %.9f,\n", pa.elapsed);
    printf("  \"rateprobe_aes_trials_per_sec\": %.1f,\n", (double)(1ULL<<20) / pa.elapsed);
    arm_spec pf = {"RATEPROBE-FF-2p20", 1, 0, 1, 1, 20, seed, 1, rate_threads, 0};
    run_arm(&pf, rk, 0);
    printf("  \"rateprobe_freshfeistel_trials_log2\": 20,\n");
    printf("  \"rateprobe_freshfeistel_elapsed_seconds\": %.9f,\n", pf.elapsed);
    printf("  \"rateprobe_freshfeistel_trials_per_sec\": %.1f,\n", (double)(1ULL<<20) / pf.elapsed);
    printf("  \"selfcheck_pass\": %s\n", (pin_ok && ffok && kc == 0 && dups == 0) ? "true" : "false");
    printf("}\n");
    return pin_ok && ffok && kc == 0 && dups == 0;
}

int main(int argc, char **argv){
    gf_init(); build_geom(); build_aes_sbox();
    if(!check_bijective()){ fprintf(stderr, "S-BOX NOT BIJECTIVE\n"); return 4; }
    build_mul_tables();
    if(argc < 2){
        fprintf(stderr,
          "usage: rc8probe_freshfeistel selfcheck <seed> <rate_threads>\n"
          "       rc8probe_freshfeistel arm <name> <oracle=aes|freshfeistel> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>\n");
        return 2;
    }
    if(!strcmp(argv[1], "selfcheck")){
        uint64_t seed = argc > 2 ? strtoull(argv[2], NULL, 10) : 531001ULL;
        int rt = argc > 3 ? atoi(argv[3]) : 2;
        int ok = do_selfcheck(seed, rt);
        return ok ? 0 : 1;
    }
    if(strcmp(argv[1], "arm")){ fprintf(stderr, "bad mode\n"); return 2; }
    if(argc < 11){ fprintf(stderr, "arm needs 9 args\n"); return 2; }

    arm_spec A;
    A.name = argv[2];
    int oracle = !strcmp(argv[3], "aes") ? 0 : (!strcmp(argv[3], "freshfeistel") ? 1 : -1);
    if(oracle < 0){ fprintf(stderr, "oracle must be aes|freshfeistel\n"); return 2; }
    A.oracle = oracle;
    A.rounds = atoi(argv[4]); A.amask = atoi(argv[5]); A.smask = atoi(argv[6]);
    A.log2N = atoi(argv[7]);
    A.seed = strtoull(argv[8], NULL, 10);
    A.armid = atoi(argv[9]); A.nthr = atoi(argv[10]);
    if(A.smask == 0 || A.smask == 15){ fprintf(stderr, "degenerate smask forbidden\n"); return 3; }
    if(A.amask == 0){ fprintf(stderr, "empty amask forbidden\n"); return 3; }
    if(A.log2N < 1 || A.log2N > 40){ fprintf(stderr, "log2N out of range\n"); return 3; }

    uint8_t rk[11][16];
    if(oracle == 0){
        /* PIN GATE (rc8probe.c): re-verify dec o enc = id at r=1..10 plus the
         * FIPS-197 C.1 KAT before measuring the live AES arm. */
        if(!do_pin(1, 60600002ULL, 64, 1)){
            fprintf(stderr, "PIN FAILED -- refusing to measure\n"); return 5;
        }
        uint64_t kst = A.seed ^ 0xA5A5A5A5A5A5A5A5ULL;
        uint8_t key[16];
        for(int i = 0; i < 16; i += 8){
            uint64_t z = sm64(&kst);
            for(int q = 0; q < 8; q++) key[i + q] = (uint8_t)(z >> (8*q));
        }
        key_expand(key, rk);
    } else {
        /* fresh-key gate: round-trip + injectivity under 4096 fresh keys. */
        if(!ff_gate(A.seed, 4096, 1)){
            fprintf(stderr, "FF GATE FAILED -- refusing to measure\n"); return 5;
        }
        memset(rk, 0, sizeof rk);
    }
    run_arm(&A, rk, 1);
    return 0;
}
