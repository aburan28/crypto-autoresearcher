/* affarm046.c -- TASK-20260901-f5d3a4 (BATCH-fe0bdc, GOAL-AES-003)
 *
 * FRESH implementation of the affine fixture instrument for
 * IDEA-20260901-04606c Stage 1: the campaign's yoyo probe with SBOX[i] = i
 * (cipher affine over GF(2)), arm surface restricted to the identity table.
 *
 * LINEAGE AND CONVENTION-DRIFT CONTROL (full audit in INDEPENDENCE_AUDIT.md):
 * Round-function EXPRESSIONS are kept expression-identical to the pinned
 * campaign build BATCH-b41ba9 TASK-20260806-47f217 probe_sbox.c (the exact-
 * port discipline of algebra_rank.py); the file's organization, mode set,
 * and arm surface are new. The mandated controls:
 *   (1) KAT PINS -- `pin` mode runs the FIPS-197 C.1 KAT (enc+dec, r=10) and
 *       the BATCH-003 r=5/r=10 anchor ciphertexts under the AES table, plus
 *       512-vector r=1..10 roundtrips. These external constants catch any
 *       self-consistent-but-unpinned convention drift that the affine
 *       algebraic checks cannot (record confounders).
 *   (2) SOURCE-DIFF AUDIT -- diff of this file against the campaign build is
 *       recorded in runs/source_diff.txt with an annotation table.
 * Arm-run conventions (JSON arm receipt to stdout, /usr/bin/time -l timing
 * file, .err capture, per-thread seed formula, calibration before the frozen
 * arm) follow the campaign harness lineage BATCH-014 TASK-20260805-b95720
 * rc8probe_feistel.c / BATCH-015 TASK-20260805-d408ac rc8probe_freshfeistel.c.
 * No cipher code was taken from the Feistel harnesses (different family).
 *
 * Cipher convention (pinned, BATCH-002 / probe_sbox.c header):
 *   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
 *   round keys = first r+1 blocks of the UNTRUNCATED FIPS-197 AES-128
 *   expansion using the CURRENT global SBOX for SubWord. State column-major:
 *   byte[4*col+row]. Final round drops MixColumns. D_K^r exact inverse.
 * Geometry:
 *   PW[j][row] = 4*((j+row)%4)+row   forward diagonals
 *   CW[j][row] = 4*((j-row)%4)+row   inverse-ShiftRows diagonals
 * Trial (probe worker semantics):
 *   p0 uniform; p1 = p0 with bytes of words in amask re-randomised (zero
 *   word-diff rejected); c0=enc_r(p0), c1=enc_r(p1); swap ciphertext bytes
 *   of words in smask between c0,c1 (trivial swap detected and excluded);
 *   q0=dec_r(c0), q1=dec_r(c1); Z = # zero diff bytes; W = # PW words whose
 *   diff bytes are all zero (ALL four words).
 *
 * build: cc -O2 -pthread -o affarm046 affarm046.c
 * usage: affarm046 pin <seed> | affarm046 pinidentity <seed> | affarm046 geom
 *      | affarm046 arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> identity
 *
 * claim_tier: toy. Nothing here is a statement about full-round or deployed
 * AES (RQ-AES-003 R3). No comparison to published cryptanalysis.
 *
 * INFERENCE BLOCK (every artifact of this task):
 *   policy: executor-implementation
 *   requested_policy: executor-implementation
 *   resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
 *     (ACTUAL model serving this session under inference amendment
 *      DEC-20260831-0d1eeb; no adapter probe was executed in this session)
 *   fallback_used: true
 *   model_verified: false
 *   standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>

/* ---------- splitmix64 (campaign RNG convention) ---------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------- global S-box ---------- */
static uint8_t SBOX[256];
static uint8_t INV_SBOX[256];
static char SBOX_LABEL[80];

static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}
static uint8_t XT2[256], XT4[256], XT8[256];

/* ---------- AES S-box (for the KAT pins only) ---------- */
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
static int build_inv_sbox(void){
    int ok=1;
    for(int i=0;i<256;i++) INV_SBOX[SBOX[i]]=(uint8_t)i;
    for(int i=0;i<256;i++) if(SBOX[INV_SBOX[i]]!=(uint8_t)i) ok=0;
    for(int i=0;i<256;i++) if(INV_SBOX[SBOX[i]]!=(uint8_t)i) ok=0;
    return ok;
}
static void set_aes_sbox(void){
    build_sbox();
    build_inv_sbox();
    snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"aes");
}
static void set_identity_sbox(void){
    for(int i=0;i<256;i++) SBOX[i]=(uint8_t)i;
    build_inv_sbox();
    snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"identity");
}
static int identity_tables_ok(void){
    for(int i=0;i<256;i++) if(SBOX[i]!=(uint8_t)i || INV_SBOX[i]!=(uint8_t)i) return 0;
    return 1;
}
static void build_xt_tables(void){
    for(int i=0;i<256;i++){ XT2[i]=xt((uint8_t)i); XT4[i]=xt(XT2[i]); XT8[i]=xt(XT4[i]); }
}

/* ---------- AES-128 key expansion, FIPS-197 (uses global SBOX) ---------- */
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

/* ---------- pinned round functions (expression-identical to probe_sbox.c) ---------- */
static inline void add_rk(uint8_t s[16], const uint8_t rk[16]){
    for(int i=0;i<16;i++) s[i]^=rk[i];
}
static inline void sub_shift(const uint8_t s[16], uint8_t t[16]){
    for(int c=0;c<4;c++) for(int r=0;r<4;r++)
        t[4*c+r] = SBOX[s[4*((c+r)&3)+r]];
}
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

/* ---------- geometry ---------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j=0;j<4;j++) for(int row=0;row<4;row++){
        PW[j][row] = 4*(((j+row)%4+4)%4)+row;
        CW[j][row] = 4*(((j-row)%4+4)%4)+row;
    }
}

/* ---------- trial worker (pinned instrument semantics) ---------- */
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

/* ---------- pin: FIPS-197 KAT + BATCH-003 anchors under the AES table ---------- */
static int pin(uint64_t seed){
    const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
    const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    const uint8_t kat_ct[16]={0x69,0xc4,0xe0,0xd8,0x6a,0x7b,0x04,0x30,
                              0xd8,0xcd,0xb7,0x80,0x70,0xb4,0xc5,0x5a};
    const char *kat_ct_hex = "69c4e0d86a7b0430d8cdb78070b4c55a";
    const uint8_t anchor_key[16]={0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,
                                  0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c};
    const char *r5_pin_hex = "4167e8f8367c38cdb7bde2ade620a7a8";
    const char *r10_pin_hex = "8df4e9aac5c7573a27d8d055d6e4d64b";
    sched s; sched_init(kat_key,&s);
    sched sa; sched_init(anchor_key,&sa);
    uint8_t y[16];

    printf("{\n  \"mode\": \"pin\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);
    enc_r(y, kat_pt, &s, 10);
    int kat_enc_ok = (memcmp(y,kat_ct,16)==0);
    printf("  \"fips197_c1_kat_encrypt_match_r10\": %s,\n", kat_enc_ok?"true":"false");
    printf("  \"fips197_c1_kat_ciphertext_r10_computed\": \"");
    for(int i=0;i<16;i++) printf("%02x", y[i]);
    printf("\",\n  \"fips197_c1_kat_expected_r10\": \"%s\",\n", kat_ct_hex);
    dec_r(y, kat_ct, &s, 10);
    int kat_dec_ok = (memcmp(y,kat_pt,16)==0);
    printf("  \"fips197_c1_kat_decrypt_match_r10\": %s,\n", kat_dec_ok?"true":"false");

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
    int r5_dec_ok;
    {
        uint8_t back[16];
        dec_r(back, y, &sa, 5);
        r5_dec_ok = (memcmp(back, kat_pt, 16)==0);
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

    uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            uint8_t c[16], e[16];
            enc_r(c,pt,&sv,r);
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
    printf("  \"pin_pass\": %s\n", (kat_enc_ok&&kat_dec_ok&&r5_ok&&r5_dec_ok&&r10_ok&&fails==0)?"true":"false");
    printf("}\n");
    return (kat_enc_ok&&kat_dec_ok&&r5_ok&&r5_dec_ok&&r10_ok&&fails==0)?0:1;
}

/* ---------- pinidentity: identity table + r=1..10 roundtrips ---------- */
static int pinidentity(uint64_t seed){
    set_identity_sbox();
    int bijective = identity_tables_ok();
    printf("{\n  \"mode\": \"pinidentity\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);
    printf("  \"sbox_bijective\": %s,\n", bijective?"true":"false");
    printf("  \"sbox_table_hex\": \"");
    for(int i=0;i<256;i++) printf("%02x", SBOX[i]);
    printf("\",\n  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
    uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            uint8_t c[16], e[16];
            enc_r(c,pt,&sv,r);
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

/* ---------- geometry info ---------- */
static int geom_mode(void){
    printf("{\n  \"PW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",PW[j][0],PW[j][1],PW[j][2],PW[j][3], j<3?",":""); }
    printf("],\n  \"CW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",CW[j][0],CW[j][1],CW[j][2],CW[j][3], j<3?",":""); }
    printf("],\n  \"sbox_source\": \"affine oracle: identity table only for arms; AES table reachable solely in pin mode (KAT pins)\"\n}\n");
    return 0;
}

int main(int argc, char **argv){
    build_xt_tables(); build_geom(); set_aes_sbox();
    if(argc<2){ fprintf(stderr,"usage: affarm046 pin <seed> | affarm046 pinidentity <seed> | affarm046 geom | affarm046 arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> identity\n"); return 2; }
    if(!strcmp(argv[1],"geom")) return geom_mode();
    if(!strcmp(argv[1],"pin")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pin(seed);
    }
    if(!strcmp(argv[1],"pinidentity")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pinidentity(seed);
    }
    if(strcmp(argv[1],"arm")){ fprintf(stderr,"bad mode\n"); return 2; }
    if(argc<11){ fprintf(stderr,"arm needs 9 arguments (final: sbox token)\n"); return 2; }
    const char *name=argv[2];
    int rounds=atoi(argv[3]), amask=atoi(argv[4]), smask=atoi(argv[5]);
    int log2N=atoi(argv[6]);
    uint64_t seed=strtoull(argv[7],NULL,10);
    int armid=atoi(argv[8]); int nthr=atoi(argv[9]);
    if(strcmp(argv[10],"identity")!=0){ fprintf(stderr,"this oracle runs the identity table ONLY (affine scope)\n"); return 3; }
    if(smask==0 || smask==15){ fprintf(stderr,"degenerate smask forbidden\n"); return 3; }
    if(amask==0){ fprintf(stderr,"empty amask forbidden\n"); return 3; }
    if(rounds<1 || rounds>10){ fprintf(stderr,"rounds must be 1..10 (toy tier)\n"); return 3; }
    if(log2N<1 || log2N>40){ fprintf(stderr,"log2N out of range\n"); return 3; }
    if(nthr<1 || nthr>64){ fprintf(stderr,"threads out of range\n"); return 3; }
    set_identity_sbox();
    if(!identity_tables_ok()){ fprintf(stderr,"identity table check FAILED\n"); return 4; }

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
    printf("  \"sbox\": \"identity\",\n");
    printf("  \"sbox_bijective\": true,\n");
    printf("  \"sbox_table_hex\": \"");
    for(int i=0;i<256;i++) printf("%02x", SBOX[i]);
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
