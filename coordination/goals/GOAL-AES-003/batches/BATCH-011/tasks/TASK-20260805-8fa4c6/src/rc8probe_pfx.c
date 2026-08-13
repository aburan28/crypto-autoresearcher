/* rc8probe.c -- TASK-20260803-e55757 (BATCH-007 RANK 2).
 *
 * INDEPENDENT re-implementation of the yoyo W>=1 statistic measured by
 * BATCH-006's yoyo_sbox_v2, written for this task. Same measured object,
 * different instrument:
 *
 *   - NO T-tables. State is 16 bytes; SubBytes / ShiftRows / MixColumns /
 *     AddRoundKey are four separate byte-level steps with small GF(2^8)
 *     multiply tables.
 *   - DIRECT inverse cipher (ARK, InvShiftRows, InvSubBytes, InvMixColumns
 *     in straight reversed order, forward round keys only) rather than the
 *     equivalent-inverse cipher with InvMixColumns'd round keys.
 *   - AES S-box from log/antilog tables over generator 0x03, not from an
 *     O(256^2) product search.
 *   - Word-oriented key expansion with explicit RotWord/SubWord/Rcon.
 *
 * Reproduced deliberately, because they are part of the DEFINITION of the
 * object being replicated (see PREREGISTRATION.md): splitmix64, the
 * Fisher-Yates-with-rejection S-box draw, the plaintext/active-word draw and
 * its rejection condition, the trivial-swap exclusion, the PW/CW geometry,
 * the key derivation from the arm seed and the per-thread trial split.
 *
 * E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
 * Analytic null P(W>=1) ~ 4*2^-32.
 *
 * Pure measurement. certificate.kind: none.
 * build: gcc -O3 -pthread -o rc8probe rc8probe.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

/* ---------------- splitmix64 (part of the object definition) ------------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------------- GF(2^8), log/antilog over generator 0x03 --------------- */
static uint8_t GLOG[256], GEXP[512];
static void gf_init(void){
    uint8_t x = 1;
    for(int i = 0; i < 255; i++){
        GEXP[i] = x;
        GLOG[x] = (uint8_t)i;
        /* x *= 3  ==  x ^ xtime(x) */
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

/* ---------------- the S-box parameter ------------------------------------ */
static uint8_t SBOX[256], ISBOX[256];

/* AES S-box: multiplicative inverse then the FIPS-197 affine map, expressed
 * as a byte rotation identity: y = x ^ rotl(x,1) ^ rotl(x,2) ^ rotl(x,3)
 *                                  ^ rotl(x,4) ^ 0x63, x = inv(a). */
static inline uint8_t rotl8(uint8_t v, int n){
    return (uint8_t)((v << n) | (v >> (8 - n)));
}
static void build_aes_sbox(void){
    for(int a = 0; a < 256; a++){
        uint8_t x = ginv((uint8_t)a);
        SBOX[a] = (uint8_t)(x ^ rotl8(x,1) ^ rotl8(x,2) ^ rotl8(x,3) ^ rotl8(x,4) ^ 0x63);
    }
}

/* Fisher-Yates over 0..255 with splitmix64 and rejection sampling.
 * Part of the object definition; re-implemented from the documented rule. */
static void build_random_sbox(uint64_t seed){
    uint64_t st = seed;
    for(int i = 0; i < 256; i++) SBOX[i] = (uint8_t)i;
    for(int i = 255; i >= 1; i--){
        uint64_t m = (uint64_t)i + 1ULL;
        uint64_t lim = UINT64_MAX - (UINT64_MAX % m);
        uint64_t r;
        do { r = sm64(&st); } while (r >= lim);
        uint64_t j = r % m;
        uint8_t t = SBOX[i]; SBOX[i] = SBOX[j]; SBOX[j] = t;
    }
}

/* returns 1 iff SBOX is a permutation of 0..255; fills ISBOX. */
static int check_bijective(void){
    int cnt[256]; memset(cnt, 0, sizeof cnt);
    for(int i = 0; i < 256; i++) cnt[SBOX[i]]++;
    for(int i = 0; i < 256; i++) if(cnt[i] != 1) return 0;
    for(int i = 0; i < 256; i++) ISBOX[SBOX[i]] = (uint8_t)i;
    for(int i = 0; i < 256; i++) if(ISBOX[SBOX[i]] != (uint8_t)i) return 0;
    for(int i = 0; i < 256; i++) if(SBOX[ISBOX[i]] != (uint8_t)i) return 0;
    return 1;
}

/* ---------------- MixColumns multiply tables (NOT T-tables) -------------- */
static uint8_t M2[256], M3[256], M9[256], MB[256], MD[256], ME[256];
static void build_mul_tables(void){
    for(int i = 0; i < 256; i++){
        uint8_t v = (uint8_t)i;
        M2[i] = gmul(v, 0x02); M3[i] = gmul(v, 0x03);
        M9[i] = gmul(v, 0x09); MB[i] = gmul(v, 0x0b);
        MD[i] = gmul(v, 0x0d); ME[i] = gmul(v, 0x0e);
    }
}

/* ---------------- key expansion (word-oriented) -------------------------- */
/* state byte index i = 4*col + row (column-major), matching the convention. */
static void key_expand(const uint8_t key[16], uint8_t rk[11][16]){
    static const uint8_t RCON[10] = {0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
    uint8_t w[44][4];
    for(int i = 0; i < 4; i++) for(int b = 0; b < 4; b++) w[i][b] = key[4*i + b];
    for(int i = 4; i < 44; i++){
        uint8_t t[4];
        t[0] = w[i-1][0]; t[1] = w[i-1][1]; t[2] = w[i-1][2]; t[3] = w[i-1][3];
        if(i % 4 == 0){
            uint8_t r0 = t[0];                       /* RotWord */
            t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = r0;
            for(int b = 0; b < 4; b++) t[b] = SBOX[t[b]];   /* SubWord */
            t[0] ^= RCON[i/4 - 1];
        }
        for(int b = 0; b < 4; b++) w[i][b] = (uint8_t)(w[i-4][b] ^ t[b]);
    }
    for(int i = 0; i <= 10; i++)
        for(int c = 0; c < 4; c++)
            for(int b = 0; b < 4; b++)
                rk[i][4*c + b] = w[4*i + c][b];
}

/* ---------------- byte-level round primitives ---------------------------- */
static inline void add_rk(uint8_t s[16], const uint8_t k[16]){
    for(int i = 0; i < 16; i++) s[i] ^= k[i];
}
static inline void sub_bytes(uint8_t s[16]){
    for(int i = 0; i < 16; i++) s[i] = SBOX[s[i]];
}
static inline void inv_sub_bytes(uint8_t s[16]){
    for(int i = 0; i < 16; i++) s[i] = ISBOX[s[i]];
}
/* ShiftRows: out[4c+r] = in[4*((c+r)&3)+r] */
static inline void shift_rows(uint8_t s[16]){
    uint8_t t[16];
    for(int c = 0; c < 4; c++)
        for(int r = 0; r < 4; r++)
            t[4*c + r] = s[4*((c + r) & 3) + r];
    memcpy(s, t, 16);
}
/* InvShiftRows: out[4c+r] = in[4*((c-r)&3)+r] */
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

/* r-round encryption: ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0 */
static void enc_r(const uint8_t in[16], uint8_t out[16], const uint8_t rk[11][16], int r){
    uint8_t s[16]; memcpy(s, in, 16);
    add_rk(s, rk[0]);
    for(int i = 1; i < r; i++){
        sub_bytes(s); shift_rows(s); mix_columns(s); add_rk(s, rk[i]);
    }
    sub_bytes(s); shift_rows(s); add_rk(s, rk[r]);
    memcpy(out, s, 16);
}
/* the DIRECT inverse of enc_r, forward round keys only */
static void dec_r(const uint8_t in[16], uint8_t out[16], const uint8_t rk[11][16], int r){
    uint8_t s[16]; memcpy(s, in, 16);
    add_rk(s, rk[r]); inv_shift_rows(s); inv_sub_bytes(s);
    for(int i = r - 1; i >= 1; i--){
        add_rk(s, rk[i]); inv_mix_columns(s); inv_shift_rows(s); inv_sub_bytes(s);
    }
    add_rk(s, rk[0]);
    memcpy(out, s, 16);
}

/* ---------------- geometry ---------------------------------------------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j = 0; j < 4; j++) for(int row = 0; row < 4; row++){
        PW[j][row] = 4 * (((j + row) % 4 + 4) % 4) + row;   /* forward SR diagonals */
        CW[j][row] = 4 * (((j - row) % 4 + 4) % 4) + row;   /* inverse SR diagonals */
    }
}

/* ---------------- worker ------------------------------------------------- */
typedef struct {
    uint64_t ntrials, seed_thread;
    int rounds, amask, smask;
    const uint8_t (*rk)[16];
    uint64_t whist[5], trivial, wword[4], wge1;
    /* TASK-20260805-8fa4c6 addition: k-byte prefix-zero event counters,
     * k=1,2,3, per word j, mirroring the existing k=4 (wword) count but
     * checking only the first k bytes of PW[j] rather than all 4. Counted
     * only on nontrivial trials, same guard as wword. Additions only. */
    uint64_t pfx1[4], pfx2[4], pfx3[4];
} job;

static void *worker(void *arg){
    job *J = (job*)arg;
    uint64_t st = J->seed_thread;
    const uint8_t (*rk)[16] = J->rk;
    int r = J->rounds;
    uint8_t p0[16], p1[16], c0[16], c1[16], q0[16], q1[16], d[16];
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
        enc_r(p0, c0, rk, r);
        enc_r(p1, c1, rk, r);
        int trivial = 1;
        for(int j = 0; j < 4; j++) if(J->smask & (1 << j))
            for(int row = 0; row < 4; row++){
                int i = CW[j][row];
                uint8_t x = c0[i], y = c1[i];
                if(x != y) trivial = 0;
                c0[i] = y; c1[i] = x;
            }
        dec_r(c0, q0, rk, r);
        dec_r(c1, q1, rk, r);
        for(int i = 0; i < 16; i++) d[i] = (uint8_t)(q0[i] ^ q1[i]);
        int W = 0;
        for(int j = 0; j < 4; j++){
            int z = 1;
            for(int row = 0; row < 4; row++) if(d[PW[j][row]]) { z = 0; break; }
            if(z){ W++; if(!trivial) J->wword[j]++; }
        }
        /* TASK-20260805-8fa4c6 addition: prefix-k counters, k=1,2,3.
         * Independently derived from rc8probe's own PW/d state (not
         * transcribed from any other instrument): for each word j, a
         * prefix of length k is "zero" iff d[PW[j][0..k-1]] are all zero,
         * checking the SAME row ordering PW already uses for the k=4 word
         * check above, restricted to a byte-prefix instead of the full
         * word. Guarded by !trivial exactly as wword is, so the k=4
         * (wword) and k=1..3 (pfx1..3) counts are computed over the
         * identical nontrivial-trial population and are directly
         * comparable. This is a separate loop over j so the existing W/z
         * loop above is left untouched. */
        if(!trivial){
            for(int j = 0; j < 4; j++){
                int p1z = (d[PW[j][0]] == 0);
                int p2z = p1z && (d[PW[j][1]] == 0);
                int p3z = p2z && (d[PW[j][2]] == 0);
                if(p1z) J->pfx1[j]++;
                if(p2z) J->pfx2[j]++;
                if(p3z) J->pfx3[j]++;
            }
        }
        if(trivial){ J->trivial++; continue; }
        J->whist[W]++;
        if(W >= 1) J->wge1++;
    }
    return NULL;
}

/* ---------------- S-box loader ------------------------------------------ */
static int load_sbox(const char *spec, uint64_t *out_seed){
    *out_seed = 0;
    if(!strcmp(spec, "aes")){ build_aes_sbox(); return 1; }
    if(!strncmp(spec, "rand:", 5)){
        *out_seed = strtoull(spec + 5, NULL, 10);
        build_random_sbox(*out_seed);
        return 0;
    }
    fprintf(stderr, "bad sbox spec '%s'\n", spec);
    exit(2);
}

/* ---------------- FIPS-197 C.1 pin + round-trip -------------------------- */
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
        printf("  \"pin_pass\": %s\n", pass ? "true" : "false");
    }
    return pass;
}

static void print_sbox_full(void){
    printf("  \"sbox\": [");
    for(int i = 0; i < 256; i++) printf("%d%s", SBOX[i], i < 255 ? "," : "");
    printf("],\n");
    printf("  \"sbox_first8\": [");
    for(int i = 0; i < 8; i++) printf("%d%s", SBOX[i], i < 7 ? "," : "");
    printf("],\n");
}

int main(int argc, char **argv){
    gf_init(); build_geom();
    if(argc < 2){
        fprintf(stderr,
          "usage: rc8probe pin  <sboxspec> <rtseed>\n"
          "       rc8probe sbox <sboxspec>\n"
          "       rc8probe arm  <name> <sboxspec> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>\n");
        return 2;
    }
    if(!strcmp(argv[1], "pin")){
        uint64_t ss; int is_aes = load_sbox(argv[2], &ss);
        int bij = check_bijective();
        build_mul_tables();
        printf("{\n  \"mode\": \"pin\",\n  \"probe\": \"rc8probe\",\n  \"sbox_spec\": \"%s\",\n  \"sbox_bijective\": %s,\n",
               argv[2], bij ? "true" : "false");
        if(!bij){ printf("  \"pin_pass\": false\n}\n"); return 1; }
        print_sbox_full();
        int ok = do_pin(is_aes, strtoull(argv[3], NULL, 10), 512, 0);
        printf("}\n");
        return ok ? 0 : 1;
    }
    if(!strcmp(argv[1], "sbox")){
        uint64_t ss; load_sbox(argv[2], &ss);
        int bij = check_bijective();
        printf("{\n  \"probe\": \"rc8probe\",\n  \"sbox_spec\": \"%s\",\n  \"sbox_seed\": %llu,\n  \"sbox_bijective\": %s,\n",
               argv[2], (unsigned long long)ss, bij ? "true" : "false");
        print_sbox_full();
        printf("  \"draw\": \"Fisher-Yates over 0..255 with splitmix64, rejection sampling (no modulo bias)\"\n}\n");
        return bij ? 0 : 1;
    }
    if(strcmp(argv[1], "arm")){ fprintf(stderr, "bad mode\n"); return 2; }
    if(argc < 11){ fprintf(stderr, "arm needs 9 args\n"); return 2; }

    const char *name = argv[2];
    const char *spec = argv[3];
    uint64_t sbox_seed; int is_aes = load_sbox(spec, &sbox_seed);
    if(!check_bijective()){
        fprintf(stderr, "S-BOX NOT BIJECTIVE -- refusing to measure\n");
        return 4;
    }
    build_mul_tables();

    /* PIN GATE: every measuring run re-verifies dec_r o enc_r = id under the
     * S-box it is about to measure, at every r in 1..10, before measuring.
     * The FIPS-197 C.1 known-answer vector is only applicable to the AES
     * S-box and is checked there (and in `pin aes`), never faked otherwise. */
    if(!do_pin(is_aes, 60600002ULL, 64, 1)){
        fprintf(stderr, "PIN FAILED under this S-box -- refusing to measure\n");
        return 5;
    }
    int rounds = atoi(argv[4]), amask = atoi(argv[5]), smask = atoi(argv[6]);
    int log2N = atoi(argv[7]);
    uint64_t seed = strtoull(argv[8], NULL, 10);
    int armid = atoi(argv[9]); int nthr = atoi(argv[10]);
    if(smask == 0 || smask == 15){ fprintf(stderr, "degenerate smask forbidden\n"); return 3; }
    if(amask == 0){ fprintf(stderr, "empty amask forbidden\n"); return 3; }

    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i = 0; i < 16; i += 8){
        uint64_t z = sm64(&kst);
        for(int q = 0; q < 8; q++) key[i + q] = (uint8_t)(z >> (8*q));
    }
    uint8_t rk[11][16]; key_expand(key, rk);

    uint64_t N = 1ULL << log2N;
    job *jobs = calloc(nthr, sizeof(job));
    pthread_t *th = calloc(nthr, sizeof(pthread_t));
    uint64_t per = N / nthr;
    for(int t = 0; t < nthr; t++){
        jobs[t].ntrials = per + (t == 0 ? N - per * nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid * 0x1234567891ULL)
                            ^ ((uint64_t)(t + 1) * 0x9E3779B97F4A7C15ULL);
        jobs[t].rounds = rounds; jobs[t].amask = amask; jobs[t].smask = smask;
        jobs[t].rk = (const uint8_t (*)[16])rk;
    }
    for(int t = 0; t < nthr; t++) pthread_create(&th[t], NULL, worker, &jobs[t]);
    for(int t = 0; t < nthr; t++) pthread_join(th[t], NULL);

    uint64_t wh[5] = {0}, wword[4] = {0}, trivial = 0, wge1 = 0;
    /* TASK-20260805-8fa4c6 addition: prefix-k aggregation totals, k=1,2,3,
     * additive alongside the existing wh/wword/trivial/wge1 totals above. */
    uint64_t pfx1[4] = {0}, pfx2[4] = {0}, pfx3[4] = {0};
    for(int t = 0; t < nthr; t++){
        for(int i = 0; i < 5; i++) wh[i] += jobs[t].whist[i];
        for(int i = 0; i < 4; i++) wword[i] += jobs[t].wword[i];
        trivial += jobs[t].trivial; wge1 += jobs[t].wge1;
        /* TASK-20260805-8fa4c6 addition: sum the per-thread prefix-k job
         * fields into the run-level totals, mirroring the wword line above. */
        for(int i = 0; i < 4; i++){
            pfx1[i] += jobs[t].pfx1[i];
            pfx2[i] += jobs[t].pfx2[i];
            pfx3[i] += jobs[t].pfx3[i];
        }
    }
    printf("{\n  \"probe\": \"rc8probe\",\n  \"arm\": \"%s\",\n  \"sbox_spec\": \"%s\",\n  \"sbox_seed\": %llu,\n  \"sbox_bijective\": true,\n",
           name, spec, (unsigned long long)sbox_seed);
    printf("  \"sbox_is_aes\": %s,\n", is_aes ? "true" : "false");
    printf("  \"sbox_first8\": [");
    for(int i = 0; i < 8; i++) printf("%d%s", SBOX[i], i < 7 ? "," : "");
    printf("],\n");
    printf("  \"rounds\": %d,\n  \"amask\": %d,\n  \"smask\": %d,\n", rounds, amask, smask);
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
    /* TASK-20260805-8fa4c6 addition: k=1,2,3 prefix-zero event counts,
     * per word and totalled, alongside the existing k=4 (wword/wge1)
     * fields above. Placed as new JSON fields inserted before the
     * pre-existing terminal null_expectation_analytic field, which is
     * left byte-for-byte unmodified; this block supplies the trailing
     * comma so that field's format string does not need to change. */
    {
        uint64_t pfx1t = pfx1[0] + pfx1[1] + pfx1[2] + pfx1[3];
        uint64_t pfx2t = pfx2[0] + pfx2[1] + pfx2[2] + pfx2[3];
        uint64_t pfx3t = pfx3[0] + pfx3[1] + pfx3[2] + pfx3[3];
        uint64_t pfx4t = wword[0] + wword[1] + wword[2] + wword[3];
        double nnt = (double)(N - trivial);
        printf("  \"prefix_k1_by_word\": [%llu,%llu,%llu,%llu],\n",
               (unsigned long long)pfx1[0], (unsigned long long)pfx1[1],
               (unsigned long long)pfx1[2], (unsigned long long)pfx1[3]);
        printf("  \"prefix_k2_by_word\": [%llu,%llu,%llu,%llu],\n",
               (unsigned long long)pfx2[0], (unsigned long long)pfx2[1],
               (unsigned long long)pfx2[2], (unsigned long long)pfx2[3]);
        printf("  \"prefix_k3_by_word\": [%llu,%llu,%llu,%llu],\n",
               (unsigned long long)pfx3[0], (unsigned long long)pfx3[1],
               (unsigned long long)pfx3[2], (unsigned long long)pfx3[3]);
        printf("  \"prefix_k1_total\": %llu,\n", (unsigned long long)pfx1t);
        printf("  \"prefix_k2_total\": %llu,\n", (unsigned long long)pfx2t);
        printf("  \"prefix_k3_total\": %llu,\n", (unsigned long long)pfx3t);
        printf("  \"prefix_k4_total\": %llu,\n", (unsigned long long)pfx4t);
        printf("  \"prefix_model_k1\": %.10f,\n", nnt * 4.0 / 256.0);
        printf("  \"prefix_model_k2\": %.10f,\n", nnt * 4.0 / 65536.0);
        printf("  \"prefix_model_k3\": %.10f,\n", nnt * 4.0 / 16777216.0);
        printf("  \"prefix_model_k4\": %.10f,\n", nnt * 4.0 / 4294967296.0);
    }
    printf("  \"null_expectation_analytic\": %.10f\n", (double)(N - trivial) * 4.0 / 4294967296.0);
    printf("}\n");
    free(jobs); free(th);
    return 0;
}
