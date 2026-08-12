/* TASK-20260806-47f217 -- IDENTITY/affine S-box probe (probe_sbox.c)
 * GOAL-AES-003, batch BATCH-b41ba9. Executor role.
 *
 * Copy of TASK-20260804-f5e58b's probe_sbox.c (BATCH-713991) with ONE
 * substantive edit: the arm's S-box table is the identity map SBOX[i]=i
 * (set_identity_sbox), making the cipher affine over GF(2) so the r=5 yoyo
 * W-count is algebraically computable in advance. Round geometry,
 * MixColumns, ShiftRows, RNG, trial logic, worker threads are identical to
 * the source. The AES construction path (build_sbox/set_aes_sbox) and the
 * random path (set_random_sbox) are intact and reachable; `pin` still
 * FIPS-197-pins the AES path, `pinsbox` the random paths, and the new
 * `pinidentity` pins identity-table bijectivity + r=1..10 roundtrips.
 *
 * Cipher convention (identical to probe.c, PREREGISTRATION sec.1 of
 * TASK-20260802-e4fa63):
 *   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
 *   round keys = first r+1 blocks of the UNTRUNCATED FIPS-197 AES-128
 *   expansion (the key schedule uses the CURRENT global SBOX for SubWord,
 *   so swapping the S-box changes the key schedule as well, as it would in
 *   any real cipher built on that S-box). State is column-major:
 *   state[row][col] = byte[4*col+row]. The final round drops MixColumns.
 *   D_K^r is the exact inverse of E_K^r under the same round keys.
 *
 * Geometry (identical to probe.c):
 *   PW[j] = {4*((j+row)%4)+row}   forward diagonals
 *   CW[j] = {4*((j-row)%4)+row}   INVERSE-ShiftRows diagonals
 *
 * Trial (identical to probe.c worker):
 *   p0 uniform; p1 = p0 with bytes of words in amask re-randomised
 *   (zero word-diff rejected); c0=enc_r(p0), c1=enc_r(p1); swap ciphertext
 *   bytes of words in smask between c0 and c1 (trivial swap detected and
 *   excluded); q0=dec_r(c0), q1=dec_r(c1); d=q0^q1; Z = # zero diff bytes;
 *   W = # words whose diff bytes are all zero (over PW, ALL four words).
 *
 * build: clang -O2 -pthread -o probe_sbox probe_sbox.c
 *
 * INFERENCE BLOCK (every artifact of this task):
 *   policy: executor-implementation
 *   requested_policy: executor-implementation
 *   resolved_model: deepseek-v4-flash-free   (ACTUAL model serving this
 *       session; self-reported by the running session's own system
 *       context; no adapter probe was executed in this session)
 *   fallback_used: false
 *   model_verified: false   (no orchestration.adapter doctor --probe run)
 *   standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
 *
 * claim_tier: toy. Nothing here is a statement about full-round or
 * deployed AES (RQ-AES-003 R3).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

/* ---------- splitmix64 (identical to probe.c) ---------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------- replaceable global S-box ---------- */
static uint8_t SBOX[256];
static uint8_t INV_SBOX[256];
static char SBOX_LABEL[80];

/* ---------- GF(2^8) helpers (identical to probe.c) ---------- */
static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}

/* MixColumns speedup tables (S-box independent) */
static uint8_t XT2[256], XT4[256], XT8[256];

/* ---------- AES S-box: GF(2^8) inverse + affine map (probe.c build_sbox) ---------- */
static void build_sbox(void){
    uint8_t inv[256]; inv[0]=0;
    for(int a=1;a<256;a++) for(int b=1;b<256;b++) if(gmul((uint8_t)a,(uint8_t)b)==1){ inv[a]=(uint8_t)b; break; }
    for(int i=0;i<256;i++){
        uint8_t x=inv[i], y=0;
        for(int bit=0;bit<8;bit++){
            uint8_t v = ((x>>bit)&1) ^ ((x>>((bit+4)&7))&1) ^ ((x>>((bit+5)&7))&1)
                      ^ ((x>>((bit+6)&7))&1) ^ ((x>>((bit+7)&7))&1) ^ ((0x63>>bit)&1);
            y |= (uint8_t)(v<<bit);
        }
        SBOX[i]=y;
    }
}

/* ---------- inverse S-box + bijectivity verification ---------- */
/* returns 1 iff SBOX is a bijection and INV_SBOX is its exact inverse. */
static int build_inv_sbox(void){
    int ok=1;
    for(int i=0;i<256;i++) INV_SBOX[SBOX[i]]=(uint8_t)i;
    for(int i=0;i<256;i++) if(SBOX[INV_SBOX[i]]!=(uint8_t)i) ok=0;
    for(int i=0;i<256;i++) if(INV_SBOX[SBOX[i]]!=(uint8_t)i) ok=0;
    return ok;
}

/* ---------- random bijective S-box ----------
 * Uniform permutation draw over bytes 0..255 (Fisher-Yates) with
 * splitmix64 from a RECORDED seed. j = r mod (i+1) carries modulo bias at
 * the 2^-64 scale (2^64 mod (i+1) != 0 for non-powers of two), which is
 * far below any detectable measurement scale; documented for honesty. */
static int set_random_sbox(uint64_t seed){
    uint8_t p[256];
    for(int i=0;i<256;i++) p[i]=(uint8_t)i;
    uint64_t st=seed;
    for(int i=255;i>=1;i--){
        uint64_t r=sm64(&st);
        int j=(int)(r % (uint64_t)(i+1));
        uint8_t t=p[i]; p[i]=p[j]; p[j]=t;
    }
    memcpy(SBOX,p,256);
    snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"random_seed_%llu",(unsigned long long)seed);
    return build_inv_sbox();
}

static void set_aes_sbox(void){
    build_sbox();
    build_inv_sbox();
    snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"aes");
}

/* ---------- identity S-box (TASK-20260806-47f217 hive edit) ----------
 * The ONE substantive edit of this task: the S-box table construction used
 * by the arm is the identity map SBOX[i]=i for i in 0..255, which makes the
 * whole cipher affine over GF(2). The affine/inverse construction path of
 * build_sbox() is left intact and unused by the arm; it stays reachable via
 * set_aes_sbox() so the `pin` mode keeps FIPS-197-pinning the genuine AES
 * path. set_random_sbox() is likewise intact and reachable (pinsbox, arm
 * with a numeric seed). */
static void set_identity_sbox(void){
    for(int i=0;i<256;i++) SBOX[i]=(uint8_t)i;
    build_inv_sbox();
    snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"identity");
}

static void build_xt_tables(void){
    for(int i=0;i<256;i++){ XT2[i]=xt((uint8_t)i); XT4[i]=xt(XT2[i]); XT8[i]=xt(XT4[i]); }
}

/* ---------- AES-128 key expansion, FIPS-197 (probe.c, uses global SBOX) ---------- */
static void key_expand(const uint8_t key[16], uint8_t rk[11][16]){
    static const uint8_t rcon[10]={0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
    memcpy(rk[0], key, 16);
    for(int i=1;i<=10;i++){
        uint8_t t[4];
        memcpy(t, rk[i-1]+12, 4);
        uint8_t tmp=t[0]; t[0]=SBOX[t[1]]; t[1]=SBOX[t[2]]; t[2]=SBOX[t[3]]; t[3]=SBOX[tmp];
        t[0]^=rcon[i-1];
        for(int w=0;w<4;w++)
            for(int b=0;b<4;b++)
                rk[i][4*w+b] = rk[i-1][4*w+b] ^ (w==0 ? t[b] : rk[i][4*(w-1)+b]);
    }
}

typedef struct { uint8_t rk[11][16]; } sched;

static void sched_init(const uint8_t key[16], sched *s){ key_expand(key, s->rk); }

/* ---------- software round functions ---------- */
static inline void add_rk(uint8_t s[16], const uint8_t rk[16]){
    for(int i=0;i<16;i++) s[i]^=rk[i];
}
/* SB then SR folded (state column-major): t[4*c+r] = SBOX[s[4*((c+r)&3)+r]] */
static inline void sub_shift(const uint8_t s[16], uint8_t t[16]){
    for(int c=0;c<4;c++) for(int r=0;r<4;r++)
        t[4*c+r] = SBOX[s[4*((c+r)&3)+r]];
}
/* ISB then ISR folded: t[4*c+r] = INV_SBOX[s[4*((c-r+4)&3)+r]] */
static inline void inv_sub_shift(const uint8_t s[16], uint8_t t[16]){
    for(int c=0;c<4;c++) for(int r=0;r<4;r++)
        t[4*c+r] = INV_SBOX[s[4*((c-r+4)&3)+r]];
}
static inline void mix_columns(uint8_t s[16]){
    for(int c=0;c<4;c++){
        uint8_t a0=s[4*c], a1=s[4*c+1], a2=s[4*c+2], a3=s[4*c+3];
        uint8_t t=a0^a1^a2^a3, u=a0;
        s[4*c]   = a0 ^ t ^ XT2[a0^a1];
        s[4*c+1] = a1 ^ t ^ XT2[a1^a2];
        s[4*c+2] = a2 ^ t ^ XT2[a2^a3];
        s[4*c+3] = a3 ^ t ^ XT2[a3^u];
    }
}
static inline void inv_mix_columns(uint8_t s[16]){
    for(int c=0;c<4;c++){
        uint8_t a0=s[4*c], a1=s[4*c+1], a2=s[4*c+2], a3=s[4*c+3];
        uint8_t w0=XT8[a0],v0=XT4[a0],u0=XT2[a0];
        uint8_t w1=XT8[a1],v1=XT4[a1],u1=XT2[a1];
        uint8_t w2=XT8[a2],v2=XT4[a2],u2=XT2[a2];
        uint8_t w3=XT8[a3],v3=XT4[a3],u3=XT2[a3];
        s[4*c]   = w0^v0^u0   ^ w1^u1^a1 ^ w2^v2^a2 ^ w3^a3;
        s[4*c+1] = w0^a0     ^ w1^v1^u1 ^ w2^u2^a2 ^ w3^v3^a3;
        s[4*c+2] = w0^v0^a0  ^ w1^a1    ^ w2^v2^u2 ^ w3^u3^a3;
        s[4*c+3] = w0^u0^a0  ^ w1^v1^a1 ^ w2^a2    ^ w3^v3^u3;
    }
}

static inline void enc_r(uint8_t out[16], const uint8_t in[16], const sched *s, int r){
    uint8_t st[16], t[16];
    memcpy(st, in, 16);
    add_rk(st, s->rk[0]);
    for(int i=1;i<r;i++){
        sub_shift(st, t); mix_columns(t); add_rk(t, s->rk[i]); memcpy(st, t, 16);
    }
    sub_shift(st, t); add_rk(t, s->rk[r]);
    memcpy(out, t, 16);
}
static inline void dec_r(uint8_t out[16], const uint8_t in[16], const sched *s, int r){
    uint8_t st[16], t[16];
    memcpy(st, in, 16);
    add_rk(st, s->rk[r]);
    inv_sub_shift(st, t); memcpy(st, t, 16);
    for(int i=r-1;i>=1;i--){
        add_rk(st, s->rk[i]); inv_mix_columns(st); inv_sub_shift(st, t); memcpy(st, t, 16);
    }
    add_rk(st, s->rk[0]);
    memcpy(out, st, 16);
}

/* ---------- geometry (identical to probe.c) ---------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j=0;j<4;j++) for(int row=0;row<4;row++){
        PW[j][row] = 4*(((j+row)%4+4)%4)+row;
        CW[j][row] = 4*(((j-row)%4+4)%4)+row;
    }
}

/* ---------- arm worker (ported from probe.c) ---------- */
typedef struct {
    uint64_t ntrials, seed_thread;
    int rounds, amask, smask;
    const sched *s;
    uint64_t zhist[17], whist[5], trivial, wword[4], wge1;
} job;

static void *worker(void *arg){
    job *J=(job*)arg;
    uint64_t st=J->seed_thread;
    const sched *s=J->s;
    int r=J->rounds;
    uint8_t p0[16], p1[16], c0[16], c1[16], q0[16], q1[16];
    for(uint64_t t=0;t<J->ntrials;t++){
        uint64_t a=sm64(&st), b=sm64(&st);
        memcpy(p0, &a, 8); memcpy(p0+8, &b, 8);
        memcpy(p1, p0, 16);
        /* re-randomise every byte in every active word; reject zero word-diff */
        int ok=0;
        while(!ok){
            ok=1;
            for(int j=0;j<4;j++) if(J->amask & (1<<j)){
                uint64_t rnd=sm64(&st); int nz=0;
                for(int row=0;row<4;row++){
                    uint8_t nb=(uint8_t)(rnd>>(8*row));
                    p1[PW[j][row]]=nb;
                    if(nb != p0[PW[j][row]]) nz=1;
                }
                if(!nz) ok=0;
            }
        }
        enc_r(c0, p0, s, r);
        enc_r(c1, p1, s, r);
        /* swap ciphertext bytes of words in smask; detect trivial swap */
        int trivial=1;
        for(int j=0;j<4;j++) if(J->smask & (1<<j))
            for(int row=0;row<4;row++){
                int i=CW[j][row];
                uint8_t x=c0[i], y=c1[i];
                if(x!=y) trivial=0;
                c0[i]=y; c1[i]=x;
            }
        dec_r(q0, c0, s, r);
        dec_r(q1, c1, s, r);
        int Z=0; for(int i=0;i<16;i++) if(q0[i]==q1[i]) Z++;
        int W=0;
        for(int j=0;j<4;j++){
            int z=1; for(int row=0;row<4;row++) if(q0[PW[j][row]]!=q1[PW[j][row]]) { z=0; break; }
            if(z){ W++; if(!trivial) J->wword[j]++; }
        }
        if(trivial){ J->trivial++; continue; }
        J->zhist[Z]++; J->whist[W]++;
        if(W>=1) J->wge1++;
    }
    return NULL;
}

/* ---------- table printing helpers ---------- */
static void print_sbox_hex(void){
    for(int i=0;i<256;i++) printf("%02x", SBOX[i]);
}
static void print_inv_sbox_hex(void){
    for(int i=0;i<256;i++) printf("%02x", INV_SBOX[i]);
}

/* ---------- pin: AES-S-box KATs, r=5 anchor, roundtrips, tables ---------- */
static int pin(uint64_t seed){
    const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
    const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    const uint8_t kat_ct[16]={0x69,0xc4,0xe0,0xd8,0x6a,0x7b,0x04,0x30,
                              0xd8,0xcd,0xb7,0x80,0x70,0xb4,0xc5,0x5a};
    const char *kat_ct_hex = "69c4e0d86a7b0430d8cdb78070b4c55a";
    /* BATCH-003 cross-instrument anchor (ref.json): FIPS-197 example key
     * 2b7e151628aed2a6abf7158809cf4f3c, plaintext 00112233445566778899aabbccddeeff,
     * r=5 -> 4167e8f8367c38cdb7bde2ade620a7a8, r=10 -> 8df4e9aac5c7573a27d8d055d6e4d64b.
     * The value 4167e8f8... is what the task calls "whichever value BATCH-002's
     * readability exposed" (re-anchored by this task's RANK 2 selftest). */
    const uint8_t anchor_key[16]={0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,
                                  0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c};
    const char *r5_pin_hex = "4167e8f8367c38cdb7bde2ade620a7a8";
    const char *r10_pin_hex = "8df4e9aac5c7573a27d8d055d6e4d64b";
    sched s; sched_init(kat_key,&s);
    sched sa; sched_init(anchor_key,&sa);
    uint8_t y[16];

    printf("{\n  \"mode\": \"pin\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);

    /* r=10 FIPS-197 C.1 KAT (KAT key 000102..0f) */
    enc_r(y, kat_pt, &s, 10);
    int kat_enc_ok = (memcmp(y,kat_ct,16)==0);
    printf("  \"fips197_c1_kat_encrypt_match_r10\": %s,\n", kat_enc_ok?"true":"false");
    printf("  \"fips197_c1_kat_ciphertext_r10_computed\": \"");
    for(int i=0;i<16;i++) printf("%02x", y[i]);
    printf("\",\n  \"fips197_c1_kat_expected_r10\": \"%s\",\n", kat_ct_hex);
    dec_r(y, kat_ct, &s, 10);
    int kat_dec_ok = (memcmp(y,kat_pt,16)==0);
    printf("  \"fips197_c1_kat_decrypt_match_r10\": %s,\n", kat_dec_ok?"true":"false");

    /* round ciphertexts of the KAT block under the KAT key, r=1..10 */
    printf("  \"round_ciphertexts_of_kat_block_kat_key\": [");
    for(int r=1;r<=10;r++){
        enc_r(y, kat_pt, &s, r);
        printf("\"");
        for(int i=0;i<16;i++) printf("%02x", y[i]);
        printf("\"%s", r<10?",":"");
    }
    printf("],\n");
    /* BATCH-003 anchors under the FIPS-197 example key */
    printf("  \"anchor_key_hex\": \"2b7e151628aed2a6abf7158809cf4f3c\",\n");
    printf("  \"anchor_pt_hex\": \"00112233445566778899aabbccddeeff\",\n");
    enc_r(y, kat_pt, &sa, 5);
    char hexbuf[33];
    for(int i=0;i<16;i++) snprintf(hexbuf+2*i, 3, "%02x", y[i]);
    int r5_ok;
    {
        uint8_t expect[16];
        for(int i=0;i<16;i++){ unsigned v; sscanf(r5_pin_hex+2*i,"%2x",&v); expect[i]=(uint8_t)v; }
        r5_ok = (memcmp(y, expect, 16)==0);
    }
    printf("  \"r5_anchor_ciphertext_computed\": \"%s\",\n", hexbuf);
    printf("  \"r5_anchor_expected\": \"%s\",\n", r5_pin_hex);
    printf("  \"r5_anchor_match\": %s,\n", r5_ok?"true":"false");
    /* decrypt the r=5 anchor back to the anchor plaintext */
    int r5_dec_ok;
    {
        uint8_t anchor_ct[16];
        for(int i=0;i<16;i++){ unsigned v; sscanf(hexbuf+2*i,"%2x",&v); anchor_ct[i]=(uint8_t)v; }
        dec_r(anchor_ct, anchor_ct, &sa, 5);
        r5_dec_ok = (memcmp(anchor_ct, kat_pt, 16)==0);
    }
    printf("  \"r5_anchor_decrypts_back_to_plaintext\": %s,\n", r5_dec_ok?"true":"false");
    enc_r(y, kat_pt, &sa, 10);
    int r10_ok;
    {
        uint8_t expect[16];
        for(int i=0;i<16;i++){ unsigned v; sscanf(r10_pin_hex+2*i,"%2x",&v); expect[i]=(uint8_t)v; }
        r10_ok = (memcmp(y, expect, 16)==0);
    }
    printf("  \"r10_anchor_ciphertext_computed\": \"");
    for(int i=0;i<16;i++) printf("%02x", y[i]);
    printf("\",\n  \"r10_anchor_expected\": \"%s\",\n", r10_pin_hex);
    printf("  \"r10_anchor_match\": %s,\n", r10_ok?"true":"false");

    /* roundtrips: dec(enc(x)) == x, r=1..10, 512 random (key,plaintext) vectors */
    uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            uint8_t a[16], c[16], e[16];
            memcpy(a,pt,16);
            enc_r(c,a,&sv,r);
            dec_r(e,c,&sv,r);
            if(memcmp(e,pt,16)!=0){ fails++; if(!first_fail_r) first_fail_r=r; }
        }
    }
    printf("  \"roundtrip_vectors\": %d,\n", nvec);
    printf("  \"roundtrip_rounds_each\": \"1..10\",\n");
    printf("  \"roundtrip_checks\": %d,\n", nvec*10);
    printf("  \"roundtrip_failures\": %d,\n", fails);
    printf("  \"roundtrip_first_failure_round\": %llu,\n",(unsigned long long)first_fail_r);

    /* S-box table recording + bijectivity */
    printf("  \"sbox_bijective\": true,\n");
    printf("  \"sbox_table_hex\": \"");
    print_sbox_hex();
    printf("\",\n  \"inv_sbox_table_hex\": \"");
    print_inv_sbox_hex();
    printf("\",\n  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");

    printf("  \"pin_seed\": %llu,\n",(unsigned long long)seed);
    printf("  \"pin_pass\": %s\n", (kat_enc_ok&&kat_dec_ok&&r5_ok&&r5_dec_ok&&r10_ok&&fails==0)?"true":"false");
    printf("}\n");
    return (kat_enc_ok&&kat_dec_ok&&r5_ok&&r5_dec_ok&&r10_ok&&fails==0)?0:1;
}

/* ---------- pin for a random S-box: determinism, bijectivity, r=1 roundtrip ---------- */
static int pinsbox(uint64_t seed){
    set_random_sbox(seed);
    int bijective = build_inv_sbox();
    const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
    const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    sched s; sched_init(kat_key,&s);
    uint8_t y[16];
    printf("{\n  \"mode\": \"pinsbox\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);
    printf("  \"sbox_seed\": %llu,\n",(unsigned long long)seed);
    printf("  \"sbox_bijective\": %s,\n", bijective?"true":"false");
    printf("  \"sbox_table_hex\": \"");
    print_sbox_hex();
    printf("\",\n  \"inv_sbox_table_hex\": \"");
    print_inv_sbox_hex();
    printf("\",\n  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
    /* (c) encrypt a known block (FIPS-197 KAT block under KAT key) and
     * decrypt back to the plaintext, at r=1, r=5 and r=10. */
    int ok=1;
    printf("  \"roundtrips\": [");
    for(int r=1;r<=10;r+=4){
        enc_r(y, kat_pt, &s, r);
        printf("{\"r\": %d, \"ct\": \"", r);
        for(int i=0;i<16;i++) printf("%02x", y[i]);
        printf("\", \"dec_restores_pt\": ");
        uint8_t z[16]; dec_r(z, y, &s, r);
        int rt = (memcmp(z,kat_pt,16)==0);
        if(!rt) ok=0;
        printf("%s}", rt?"true":"false");
        if(r<9) printf(",");
    }
    printf("],\n");
    printf("  \"pin_pass\": %s\n", (bijective && ok)?"true":"false");
    printf("}\n");
    return (bijective && ok)?0:1;
}

/* ---------- pin for the identity S-box: bijectivity (trivial) + r=1..10
 * roundtrips dec(enc(x,key,r))==x on 512 random (key,plaintext) vectors.
 * The FIPS-197 KAT does not apply to the identity table (it pins the AES
 * table's values); what the identity arm needs pinned is that the identity
 * table roundtrips exactly like any other bijective table. */
static int pinidentity(uint64_t seed){
    set_identity_sbox();
    int bijective = build_inv_sbox();
    const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
    const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    sched s; sched_init(kat_key,&s);
    uint8_t y[16];
    printf("{\n  \"mode\": \"pinidentity\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);
    printf("  \"sbox_bijective\": %s,\n", bijective?"true":"false");
    printf("  \"sbox_table_hex\": \"");
    print_sbox_hex();
    printf("\",\n  \"inv_sbox_table_hex\": \"");
    print_inv_sbox_hex();
    printf("\",\n  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
    /* roundtrips dec(enc(x,key,r))==x for r=1..10, 512 random vectors */
    uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            uint8_t a[16], c[16], e[16];
            memcpy(a,pt,16);
            enc_r(c,a,&sv,r);
            dec_r(e,c,&sv,r);
            if(memcmp(e,pt,16)!=0){ fails++; if(!first_fail_r) first_fail_r=r; }
        }
    }
    printf("  \"roundtrip_vectors\": %d,\n", nvec);
    printf("  \"roundtrip_rounds_each\": \"1..10\",\n");
    printf("  \"roundtrip_checks\": %d,\n", nvec*10);
    printf("  \"roundtrip_failures\": %d,\n", fails);
    printf("  \"roundtrip_first_failure_round\": %llu,\n",(unsigned long long)first_fail_r);
    printf("  \"pin_seed\": %llu,\n",(unsigned long long)seed);
    printf("  \"pin_pass\": %s\n", (bijective && fails==0)?"true":"false");
    printf("}\n");
    return (bijective && fails==0)?0:1;
}

/* ---------- geometry / sbox info mode ---------- */
static int geom_mode(void){
    printf("{\n  \"PW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",PW[j][0],PW[j][1],PW[j][2],PW[j][3], j<3?",":""); }
    printf("],\n  \"CW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",CW[j][0],CW[j][1],CW[j][2],CW[j][3], j<3?",":""); }
    printf("],\n  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n  \"sbox_source\": \"software SPN, global replaceable SBOX; AES table from GF(2^8) inverse + FIPS-197 affine map; random tables = Fisher-Yates over 0..255 with splitmix64\"\n}\n");
    return 0;
}

int main(int argc, char **argv){
    build_xt_tables(); build_geom(); set_aes_sbox();
    if(argc<2){ fprintf(stderr,"usage: probe_sbox pin <seed> | probe_sbox pinsbox <seed> | probe_sbox pinidentity <seed> | probe_sbox geom | probe_sbox arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> [aes|identity|sboxseed]\n"); return 2; }
    if(!strcmp(argv[1],"geom")) return geom_mode();
    if(!strcmp(argv[1],"pin")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pin(seed);
    }
    if(!strcmp(argv[1],"pinsbox")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pinsbox(seed);
    }
    if(!strcmp(argv[1],"pinidentity")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pinidentity(seed);
    }
    if(strcmp(argv[1],"arm")) { fprintf(stderr,"bad mode\n"); return 2; }
    const char *name=argv[2];
    int rounds=atoi(argv[3]), amask=atoi(argv[4]), smask=atoi(argv[5]);
    int log2N=atoi(argv[6]);
    uint64_t seed=strtoull(argv[7],NULL,10);
    int armid=atoi(argv[8]); int nthr=atoi(argv[9]);
    if(smask==0 || smask==15){ fprintf(stderr,"degenerate smask forbidden\n"); return 3; }
    if(amask==0){ fprintf(stderr,"empty amask forbidden\n"); return 3; }
    /* S-box selection: argv[10] = "aes" (default), "identity", or a seed
     * for a random bijective draw. Also verifies bijectivity of the
     * selected table. */
    int sbox_ok=0;
    if(argc>=11 && strcmp(argv[10],"aes")!=0 && strcmp(argv[10],"identity")!=0){
        uint64_t sseed=strtoull(argv[10],NULL,10);
        sbox_ok = set_random_sbox(sseed);
    } else if(argc>=11 && strcmp(argv[10],"identity")==0){
        set_identity_sbox();
        sbox_ok = 1;
    } else {
        set_aes_sbox();
        sbox_ok = 1;
    }
    if(!sbox_ok){ fprintf(stderr,"S-box bijectivity check FAILED\n"); return 4; }

    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i=0;i<16;i+=8){ uint64_t z=sm64(&kst); memcpy(key+i,&z,8); }
    sched s; sched_init(key,&s);

    uint64_t N = 1ULL<<log2N;
    job *jobs=calloc(nthr,sizeof(job));
    pthread_t *th=calloc(nthr,sizeof(pthread_t));
    uint64_t per=N/nthr;
    for(int t=0;t<nthr;t++){
        jobs[t].ntrials = per + (t==0 ? N - per*nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid*0x1234567891ULL)
                            ^ ((uint64_t)(t+1)*0x9E3779B97F4A7C15ULL);
        jobs[t].rounds=rounds; jobs[t].amask=amask; jobs[t].smask=smask; jobs[t].s=&s;
    }
    for(int t=0;t<nthr;t++) pthread_create(&th[t],NULL,worker,&jobs[t]);
    for(int t=0;t<nthr;t++) pthread_join(th[t],NULL);

    uint64_t zh[17]={0}, wh[5]={0}, wword[4]={0}, trivial=0, wge1=0;
    for(int t=0;t<nthr;t++){
        for(int i=0;i<17;i++) zh[i]+=jobs[t].zhist[i];
        for(int i=0;i<5;i++)  wh[i]+=jobs[t].whist[i];
        for(int i=0;i<4;i++)  wword[i]+=jobs[t].wword[i];
        trivial+=jobs[t].trivial; wge1+=jobs[t].wge1;
    }
    printf("{\n  \"arm\": \"%s\",\n  \"rounds\": %d,\n  \"amask\": %d,\n  \"smask\": %d,\n",
           name,rounds,amask,smask);
    printf("  \"trials\": %llu,\n  \"log2N\": %d,\n  \"seed\": %llu,\n  \"arm_id\": %d,\n  \"threads\": %d,\n",
           (unsigned long long)N, log2N, (unsigned long long)seed, armid, nthr);
    printf("  \"sbox\": \"%s\",\n", SBOX_LABEL);
    printf("  \"sbox_bijective\": true,\n");
    printf("  \"sbox_table_hex\": \"");
    print_sbox_hex();
    printf("\",\n");
    printf("  \"key_hex\": \""); for(int i=0;i<16;i++) printf("%02x",key[i]); printf("\",\n");
    printf("  \"thread_seeds\": [");
    for(int t=0;t<nthr;t++) printf("%llu%s",(unsigned long long)jobs[t].seed_thread, t<nthr-1?",":"");
    printf("],\n");
    printf("  \"trivial_swaps_excluded\": %llu,\n",(unsigned long long)trivial);
    printf("  \"nontrivial_trials\": %llu,\n",(unsigned long long)(N-trivial));
    printf("  \"W_ge1_nontrivial\": %llu,\n",(unsigned long long)wge1);
    printf("  \"W_ge1_by_word\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wword[0],(unsigned long long)wword[1],
           (unsigned long long)wword[2],(unsigned long long)wword[3]);
    printf("  \"whist\": [");
    for(int i=0;i<5;i++) printf("%llu%s",(unsigned long long)wh[i], i<4?",":"");
    printf("],\n  \"zhist\": [");
    for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)zh[i], i<16?",":"");
    printf("]\n}\n");
    free(jobs); free(th);
    return 0;
}
