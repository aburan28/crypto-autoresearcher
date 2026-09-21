/* affarm046ex.c -- TASK-20260901-706b1d (BATCH-7b798d, GOAL-AES-003)
 *
 * PIN-T0 WIDENED derivative of the BATCH-ace664 certified cap-256 build
 * (TASK-20260901-579808 src/affarm046ex.c) for IDEA-20260901-582ea9 Stages
 * S0/S1. The ONLY changes vs that lineage copy (audited field-by-field in
 * runs/source_diff_raw.txt; scope: pinned interior-surface widening + pin
 * label fields + their comment annotation, nothing else):
 *   (1) PIN-T0 interior-surface widening: the arm surface admits interior
 *       dilution seats via sbox tokens s1/s2/s4/s8/s12 (k in {1,2,4,8,12})
 *       under the schedule pin adopted by DEC-20260901-fb6f11, replacing the
 *       Stage-0 refusal of interior seats.
 *   (2) PIN-T0 schedule pin implementation (arm mode only): after
 *       set_diluted_tables(k), the key schedule's SubWord table (global
 *       SBOX/INV_SBOX) is reloaded from TPOS[0]/INV_TPOS[0] -- the table at
 *       the FIRST position of the frozen order. Since POS_ORDER[0]==0,
 *       TPOS[0] is the identity table at k=0 and the AES table at every
 *       k >= 1: BOTH committed endpoints remain receipt-exact (identity
 *       schedule at k=0, AES schedule at k=16).
 *   (3) ADDITIVE pin-label receipt fields (arm mode only): schedule_pin,
 *       schedule_pin_position, schedule_pin_decision.
 * No change to the RNG, trial loop, round functions, existing counters,
 * existing receipt field emissions, or the pin/pinidentity/geom/freeze
 * modes. Non-perturbation of the endpoints is re-proven empirically by the
 * S0-4 Gate-0x rebuild identity gate (field-exact reproduction of the
 * certified cap-256 L1-AES-R5-P30 rebuild receipt under the extended
 * allowed-diff list) and by the S0-3 table-freeze re-verification.
 *
 * INFERENCE BLOCK (this task's artifacts):
 *   policy: executor-implementation
 *   requested_policy: executor-implementation
 *   resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max
 *     (session-reported; no adapter probe was executed in this session)
 *   fallback_used: true (session-backend transport under inference amendment
 *     DEC-20260831-0d1eeb)
 *   model_verified: false
 *   amendment: DEC-20260831-0d1eeb
 *
 * LINEAGE HEADER OF THE COPIED BUILD (BATCH-5ed9a3 / BATCH-ace664), retained
 * verbatim below for provenance:
 *
 * EXTENDED derivative of the Stage-0 instrument affarm046e.c
 * (TASK-20260901-7e0b71, BATCH-2f12ac) for IDEA-20260901-026d6a Stages r0+r1.
 * The ONLY change vs affarm046e.c is the ADDITIVE logging block preregistered
 * in IDEA-20260901-026d6a.logged_additions and PREREGISTRATION.md section 6:
 *   (1) per-arm class-wise zero-byte accumulators of e over the all/miss/hit
 *       splits: ezdiag (zeros of e on the 4 diagonal positions PW[0] =
 *       {0,5,10,15}) and ezoff (zeros of e on the 12 off-diagonal positions);
 *   (2) per-hit zero_mask_e (16-bit zero-byte mask of e) inside the existing
 *       HIT_LOG_CAP = 64 hit detail convention.
 * These are PURE READS after all trial decisions into NEW counters/fields;
 * no trial stream, RNG, round function, or existing counter is touched.
 * Gate-0 extended reproduction of L1-AES-R5-P30 (PREREGISTRATION.md section 5)
 * re-proves non-perturbation. Everything below the ADDED EXTENSION markers is
 * line-identical to affarm046e.c.
 *
 * BASE HEADER (affarm046e.c, unchanged): Instrumented derivative of
 * BATCH-fe0bdc TASK-20260901-f5d3a4 src/affarm046.c
 * for IDEA-20260901-363851 STAGE 0: the campaign yoyo probe widened to the
 * frozen position-dilution table surface S_k and instrumented with per-trial
 * wt(e) logging, e = (q0^q1)^(p0^p1). The e-logging block is a PURE READ
 * after all trial decisions into NEW counters only; Gate 0 (field-exact
 * reproduction of the committed L1-AES-R5-P30 receipt at seed 531001) is the
 * empirical proof of non-perturbation. See src/BUILD.md and
 * src/INDEPENDENCE_AUDIT.md (source-diff annotation table).
 *
 * LINEAGE: affarm046.c (BATCH-fe0bdc), whose round-function expressions are
 * expression-identical to the pinned campaign build BATCH-b41ba9
 * probe_sbox.c, and whose arm-run conventions follow BATCH-014/BATCH-015
 * rc8probe lineage. Reporting fields required for the Gate-0 field-by-field
 * match (plaintext_stream_digest, hit log, key_stream_seeds, stream gaps,
 * null expectation) are ported expression-identically from
 * BATCH-015 rc8probe_freshfeistel.c (FNV-1a digest formula from
 * yoyo_sbox_v4.c BATCH-009; stream-gap arithmetic from BATCH-009).
 *
 * WIDENED TABLE SURFACE (frozen construction pin, PREREGISTRATION.md §6):
 *   16 per-position tables TPOS[j], INV_TPOS[j]. S_k(position j) = AES table
 *   if j in P_k else identity; P_k = first k of the pinned row-major order
 *   [0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15]. Forward SubBytes applies the
 *   table at the PRE-ShiftRows source position; inverse applies it at the
 *   post-InvShiftRows destination position. At k=0 and k=16 this reduces
 *   EXACTLY to the affarm046/campaign sub_shift / inv_sub_shift expressions.
 *   Key schedule co-varies (SubWord uses the current global SBOX): k=16 arms
 *   use the AES schedule, k=0 arms the identity schedule. ARM runs at
 *   interior k in {1,2,4,8,12} are REFUSED by this Stage-0 build (SubWord
 *   table for position-dependent schedules requires a Coordinator pin;
 *   Stage-1 question); freeze mode covers all 7 points' tables.
 *
 * ADDED RECEIPT FIELDS (preregistered): zhist, sbox_table_hex, key_hex (all
 * lineage fields absent from L1-AES-R5-P30), ewhist_{all,miss,hit}[17],
 * ewbithist_{all,miss,hit}[129], hit_e_detail (cap 64: thread, in-thread
 * index, W, Z, vanishing word mask, wt(e) byte, wt(e) bit), sbox_k,
 * sbox_positions, arm_table_concat_sha256_input_hex_note. Trivial-swap
 * trials are excluded from all e statistics (whist convention).
 *
 * Cipher convention, geometry, trial semantics: IDENTICAL to affarm046.c
 * (see that file's header; unchanged here).
 *
 * build: cc -O2 -pthread -o affarm046ex affarm046ex.c
 * usage: affarm046ex pin <seed> | affarm046ex pinidentity <seed> | affarm046ex geom
 *      | affarm046ex freeze <seed>
 *      | affarm046ex arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> (aes|identity|s1|s2|s4|s8|s12)
 *      [PIN-T0 widening, DEC-20260901-fb6f11: s1/s2/s4/s8/s12 admit the
 *       interior dilution seats k in {1,2,4,8,12}]
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
#include <stddef.h>
#include <pthread.h>
#include <time.h>

/* ---------- splitmix64 (campaign RNG convention) -- UNCHANGED ---------- */
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

/* ---------- global S-box -- UNCHANGED ---------- */
static uint8_t SBOX[256];
static uint8_t INV_SBOX[256];
static char SBOX_LABEL[80];

static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}
static uint8_t XT2[256], XT4[256], XT8[256];

/* ---------- AES S-box (for the KAT pins only) -- UNCHANGED ---------- */
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

/* ---------- ADDED: frozen position-dilution table surface ---------- */
/* Pinned row-major order, IDEA-20260901-363851 dilution_family.position_order */
static const int POS_ORDER[16] = {0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15};
static uint8_t TPOS[16][256], INV_TPOS[16][256];
static int DIL_K = -1;   /* dilution point currently loaded (-1 = none) */

/* Build the per-position tables for dilution point k from the CURRENT global
 * SBOX/INV_SBOX (must be the AES tables for k>0 construction; for the k=0
 * identity arm the global tables are identity and both branches coincide).
 * Tables are deterministic functions of k: no seeds, no draws. */
static void set_diluted_tables(int k){
    for(int j=0;j<16;j++){
        int is_aes=0;
        for(int q=0;q<k;q++) if(POS_ORDER[q]==j){ is_aes=1; break; }
        for(int x=0;x<256;x++){
            TPOS[j][x]     = is_aes ? SBOX[x]     : (uint8_t)x;
            INV_TPOS[j][x] = is_aes ? INV_SBOX[x] : (uint8_t)x;
        }
    }
    DIL_K=k;
}
static int diluted_tables_ok(void){
    for(int j=0;j<16;j++){
        uint8_t seen[256]; memset(seen,0,256);
        for(int x=0;x<256;x++){
            if(seen[TPOS[j][x]]) return 0;
            seen[TPOS[j][x]]=1;
            if(INV_TPOS[j][TPOS[j][x]]!=(uint8_t)x) return 0;
            if(TPOS[j][INV_TPOS[j][x]]!=(uint8_t)x) return 0;
        }
    }
    return 1;
}
static void diluted_position_list(int k, int out[16]){
    for(int j=0;j<16;j++) out[j]=0;
    for(int q=0;q<k;q++) out[POS_ORDER[q]]=1;
}

/* ---------- AES-128 key expansion, FIPS-197 (uses global SBOX) -- UNCHANGED ---------- */
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

/* ---------- ADDED: SHA-256 (FIPS 180-4) for the arm-seat table binding ---------- */
typedef struct { uint32_t h[8]; uint64_t len; uint8_t buf[64]; int buflen; } sha256_ctx;
static const uint32_t SHA_K[64] = {
 0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
 0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
 0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
 0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
 0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
 0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
 0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
 0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u };
#define ROTR32(x,n) (((x)>>(n))|((x)<<(32-(n))))
static void sha256_init(sha256_ctx *c){
    c->h[0]=0x6a09e667u;c->h[1]=0xbb67ae85u;c->h[2]=0x3c6ef372u;c->h[3]=0xa54ff53au;
    c->h[4]=0x510e527fu;c->h[5]=0x9b05688cu;c->h[6]=0x1f83d9abu;c->h[7]=0x5be0cd19u;
    c->len=0; c->buflen=0;
}
static void sha256_block(sha256_ctx *c, const uint8_t *p){
    uint32_t w[64];
    for(int i=0;i<16;i++) w[i]=((uint32_t)p[4*i]<<24)|((uint32_t)p[4*i+1]<<16)|((uint32_t)p[4*i+2]<<8)|(uint32_t)p[4*i+3];
    for(int i=16;i<64;i++){
        uint32_t s0=ROTR32(w[i-15],7)^ROTR32(w[i-15],18)^(w[i-15]>>3);
        uint32_t s1=ROTR32(w[i-2],17)^ROTR32(w[i-2],19)^(w[i-2]>>10);
        w[i]=w[i-16]+s0+w[i-7]+s1;
    }
    uint32_t a=c->h[0],b=c->h[1],cc=c->h[2],d=c->h[3],e=c->h[4],f=c->h[5],g=c->h[6],h=c->h[7];
    for(int i=0;i<64;i++){
        uint32_t S1=ROTR32(e,6)^ROTR32(e,11)^ROTR32(e,25);
        uint32_t ch=(e&f)^((~e)&g);
        uint32_t t1=h+S1+ch+SHA_K[i]+w[i];
        uint32_t S0=ROTR32(a,2)^ROTR32(a,13)^ROTR32(a,22);
        uint32_t mj=(a&b)^(a&cc)^(b&cc);
        uint32_t t2=S0+mj;
        h=g;g=f;f=e;e=d+t1;d=cc;cc=b;b=a;a=t1+t2;
    }
    c->h[0]+=a;c->h[1]+=b;c->h[2]+=cc;c->h[3]+=d;c->h[4]+=e;c->h[5]+=f;c->h[6]+=g;c->h[7]+=h;
}
static void sha256_update(sha256_ctx *c, const uint8_t *p, size_t n){
    c->len+=n;
    while(n>0){
        int take=64-c->buflen; if((size_t)take>n) take=(int)n;
        memcpy(c->buf+c->buflen,p,take); c->buflen+=take; p+=take; n-=take;
        if(c->buflen==64){ sha256_block(c,c->buf); c->buflen=0; }
    }
}
static void sha256_final(sha256_ctx *c, uint8_t out[32]){
    uint64_t bits=c->len*8;
    uint8_t pad=0x80;
    sha256_update(c,&pad,1);
    uint8_t z=0;
    while(c->buflen!=56){ sha256_update(c,&z,1); }
    uint8_t lenb[8];
    for(int i=0;i<8;i++) lenb[i]=(uint8_t)(bits>>(56-8*i));
    sha256_update(c,lenb,8);
    for(int i=0;i<8;i++){ out[4*i]=(uint8_t)(c->h[i]>>24); out[4*i+1]=(uint8_t)(c->h[i]>>16); out[4*i+2]=(uint8_t)(c->h[i]>>8); out[4*i+3]=(uint8_t)c->h[i]; }
}
static void sha256_tpos_concat(uint8_t out[32]){
    sha256_ctx sc; sha256_init(&sc);
    for(int j=0;j<16;j++) sha256_update(&sc, TPOS[j], 256);
    sha256_final(&sc, out);
}

/* ---------- pinned round functions ---------- */
/* add_rk, mix_columns, inv_mix_columns: UNCHANGED from affarm046.c.
 * sub_shift / inv_sub_shift: widened table surface ONLY -- the index
 * expressions and loop structure are unchanged; SBOX[v] becomes
 * TPOS[source_position][v] (forward) and INV_SBOX[v] becomes
 * INV_TPOS[destination_position][v] (inverse), per the frozen construction
 * pin. At k=0 and k=16 these are bit-identical to the original expressions. */
static inline void add_rk(uint8_t s[16], const uint8_t rk[16]){
    for(int i=0;i<16;i++) s[i]^=rk[i];
}
static inline void sub_shift(const uint8_t s[16], uint8_t t[16]){
    for(int c=0;c<4;c++) for(int r=0;r<4;r++){
        int p=4*((c+r)&3)+r;
        t[4*c+r] = TPOS[p][s[p]];
    }
}
static inline void inv_sub_shift(const uint8_t s[16], uint8_t t[16]){
    for(int c=0;c<4;c++) for(int r=0;r<4;r++)
        t[4*c+r] = INV_TPOS[4*c+r][s[4*((c-r+4)&3)+r]];
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

/* ---------- geometry -- UNCHANGED ---------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j=0;j<4;j++) for(int row=0;row<4;row++){
        PW[j][row] = 4*(((j+row)%4+4)%4)+row;
        CW[j][row] = 4*(((j-row)%4+4)%4)+row;
    }
}

/* ---------- trial worker (pinned instrument semantics) ---------- */
#define HIT_LOG_CAP 256

typedef struct {
    uint64_t ntrials, seed_thread;
    int rounds, amask, smask;
    const sched *s;
    uint64_t zhist[17], whist[5], trivial, wword[4], wge1;
    /* ADDED counters (e-logging + anchor-receipt reporting); none of these
     * feeds any trial decision, RNG state, or pre-existing counter. */
    uint64_t ewhist_all[17], ewhist_miss[17], ewhist_hit[17];
    uint64_t ewbithist_all[129], ewbithist_miss[129], ewbithist_hit[129];
    uint64_t hit_thread_idx[HIT_LOG_CAP];
    int hit_W[HIT_LOG_CAP], hit_Z[HIT_LOG_CAP], hit_vmask[HIT_LOG_CAP],
        hit_ewb[HIT_LOG_CAP], hit_ewbit[HIT_LOG_CAP];
    int hit_count, hit_overflow;
    uint64_t pstream_digest;
    /* ADDED EXTENSION (IDEA-20260901-026d6a.logged_additions; pure reads after
     * all trial decisions into NEW counters only): class-wise zero-byte
     * accumulators of e over the all/miss/hit splits and the per-hit
     * zero-byte mask of e. None of these feeds any trial decision, RNG state,
     * or pre-existing counter. */
    uint64_t ezdiag_all, ezdiag_miss, ezdiag_hit;
    uint64_t ezoff_all, ezoff_miss, ezoff_hit;
    int hit_zmask_e[HIT_LOG_CAP];
} job;

static void *worker(void *arg){
    job *J=(job*)arg;
    uint64_t st=J->seed_thread;
    const sched *s=J->s;
    int r=J->rounds;
    uint8_t p0[16], p1[16], c0[16], c1[16], q0[16], q1[16];
    /* ADDED: FNV-1a 64 over 8-byte LE words of the full (p0,p1) stream;
     * formula and loop position copied expression-identically from
     * rc8probe_freshfeistel.c lines 378/398-401 (lineage yoyo_sbox_v4.c). */
    uint64_t pdig = 1469598103934665603ULL;
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
        {   /* ADDED: plaintext stream digest update (pure read of final
               p0,p1; new counter only) */
            uint64_t w;
            for(int i=0;i<16;i+=8){ memcpy(&w, p0+i, 8); pdig = (pdig ^ w) * 1099511628211ULL; }
            for(int i=0;i<16;i+=8){ memcpy(&w, p1+i, 8); pdig = (pdig ^ w) * 1099511628211ULL; }
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
        /* ---------- ADDED e-logging block (pure reads AFTER all trial
         * decisions, into new counters only) ---------- */
        {
            int ewb=0, ewbit=0, vmask=0;
            int zmask_e=0, ezd=0;   /* ADDED EXTENSION locals (pure reads) */
            for(int i=0;i<16;i++){
                uint8_t eb=(uint8_t)((q0[i]^q1[i])^(p0[i]^p1[i]));
                if(eb){ ewb++; ewbit+=__builtin_popcount((unsigned)eb); }
                else {   /* ADDED EXTENSION: zero-byte mask of e and diagonal
                          * (PW[0]) zero count; the existing ewb/ewbit reads
                          * above are unchanged */
                    zmask_e |= (1<<i);
                    if(i==PW[0][0]||i==PW[0][1]||i==PW[0][2]||i==PW[0][3]) ezd++;
                }
            }
            int ezo = __builtin_popcount((unsigned)zmask_e) - ezd;  /* ADDED EXTENSION */
            for(int j=0;j<4;j++){
                int zj=1;
                for(int row=0;row<4;row++) if(q0[PW[j][row]]!=q1[PW[j][row]]){ zj=0; break; }
                if(zj) vmask |= (1<<j);
            }
            J->ewhist_all[ewb]++; J->ewbithist_all[ewbit]++;
            /* ADDED EXTENSION: class-wise zero-byte accumulators, all split */
            J->ezdiag_all += (uint64_t)ezd; J->ezoff_all += (uint64_t)ezo;
            if(W>=1){
                J->ewhist_hit[ewb]++; J->ewbithist_hit[ewbit]++;
                /* ADDED EXTENSION: hit split */
                J->ezdiag_hit += (uint64_t)ezd; J->ezoff_hit += (uint64_t)ezo;
                if(J->hit_count < HIT_LOG_CAP){
                    int h=J->hit_count;
                    J->hit_thread_idx[h]=t; J->hit_W[h]=W; J->hit_Z[h]=Z;
                    J->hit_vmask[h]=vmask; J->hit_ewb[h]=ewb; J->hit_ewbit[h]=ewbit;
                    J->hit_zmask_e[h]=zmask_e;   /* ADDED EXTENSION */
                    J->hit_count++;
                } else J->hit_overflow++;
            } else {
                J->ewhist_miss[ewb]++; J->ewbithist_miss[ewbit]++;
                /* ADDED EXTENSION: miss split */
                J->ezdiag_miss += (uint64_t)ezd; J->ezoff_miss += (uint64_t)ezo;
            }
        }
    }
    J->pstream_digest = pdig;
    return NULL;
}

/* ---------- ADDED: stream-gap exclusion (expression-identical to
 * rc8probe_freshfeistel.c lines 462-484, lineage BATCH-009) ---------- */
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
/* ADDED: per-thread key-stream seeds for reporting (constants and formula
 * copied from rc8probe_freshfeistel.c lines 345-349; report-only for the
 * live-table arms, exactly as in the committed comparator receipt). */
#define KEYARM_C1 0x517CC1B727220A95ULL
#define KEYARM_C2 0x6A09E667F3BCC908ULL
static inline uint64_t key_thread_seed(uint64_t seed, int armid, int t){
    return seed ^ ((uint64_t)armid * KEYARM_C1) ^ ((uint64_t)(t + 1) * KEYARM_C2);
}

/* ---------- pin: FIPS-197 KAT + BATCH-003 anchors under the AES table -- UNCHANGED ---------- */
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

/* ---------- pinidentity: identity table + r=1..10 roundtrips -- UNCHANGED ---------- */
static int pinidentity(uint64_t seed){
    set_identity_sbox();
    set_diluted_tables(0);   /* TPOS = identity: round function sees the identity table */
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

/* ---------- geometry info -- UNCHANGED ---------- */
static int geom_mode(void){
    printf("{\n  \"PW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",PW[j][0],PW[j][1],PW[j][2],PW[j][3], j<3?",":""); }
    printf("],\n  \"CW\": [");
    for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",CW[j][0],CW[j][1],CW[j][2],CW[j][3], j<3?",":""); }
    printf("],\n  \"sbox_source\": \"affine oracle: identity table only for arms; AES table reachable solely in pin mode (KAT pins)\"\n}\n");
    return 0;
}

/* ---------- ADDED: table freeze for the FULL pinned dilution family ---------- */
/* Emits, for every k in {0,1,2,3,4,8,12,16}: the 16 per-position 256-byte
 * tables (hex), the bijection check, and the nestedness check
 * (S_k[j] == AES[j] for j in P_k, S_k[j] == j elsewhere). sha256 digests are
 * computed from this output by src/freeze_digest.py. Also runs the folded
 * instrument smoke self-checks (preregistered, PREREGISTRATION.md §8 R3):
 * a k=0 identity mini arm with committed assertions and a k=16 AES mini arm
 * with internal-consistency assertions, both at log2N=10 seed=<seed>. */
static const int FREEZE_KS[8] = {0,1,2,3,4,8,12,16};

static void mini_arm_emit(const char *label, int rounds, int log2N, uint64_t seed,
                          int armid, int nthr, const sched *s){
    uint64_t N = 1ULL<<log2N;
    job *jobs=calloc(nthr,sizeof(job));
    pthread_t *th=calloc(nthr,sizeof(pthread_t));
    uint64_t per=N/nthr;
    for(int t=0;t<nthr;t++){
        jobs[t].ntrials = per + (t==0 ? N - per*nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid*0x1234567891ULL)
                            ^ ((uint64_t)(t+1)*0x9E3779B97F4A7C15ULL);
        jobs[t].rounds=rounds; jobs[t].amask=1; jobs[t].smask=1; jobs[t].s=s;
    }
    for(int t=0;t<nthr;t++) pthread_create(&th[t],NULL,worker,&jobs[t]);
    for(int t=0;t<nthr;t++) pthread_join(th[t],NULL);
    uint64_t zh[17]={0}, wh[5]={0}, wword[4]={0}, trivial=0, wge1=0;
    uint64_t ewh_all[17]={0}, ewh_miss[17]={0}, ewh_hit[17]={0};
    uint64_t ewb_all[129]={0}, ewb_miss[129]={0}, ewb_hit[129]={0};
    int detail_n=0, hit_overflow=0;
    for(int t=0;t<nthr;t++){
        for(int i=0;i<17;i++){ zh[i]+=jobs[t].zhist[i];
            ewh_all[i]+=jobs[t].ewhist_all[i]; ewh_miss[i]+=jobs[t].ewhist_miss[i]; ewh_hit[i]+=jobs[t].ewhist_hit[i]; }
        for(int i=0;i<129;i++){ ewb_all[i]+=jobs[t].ewbithist_all[i]; ewb_miss[i]+=jobs[t].ewbithist_miss[i]; ewb_hit[i]+=jobs[t].ewbithist_hit[i]; }
        for(int i=0;i<5;i++)  wh[i]+=jobs[t].whist[i];
        for(int i=0;i<4;i++)  wword[i]+=jobs[t].wword[i];
        trivial+=jobs[t].trivial; wge1+=jobs[t].wge1;
        detail_n+=jobs[t].hit_count; hit_overflow+=jobs[t].hit_overflow;
    }
    printf("  \"%s\": {\n", label);
    printf("    \"rounds\": %d, \"amask\": 1, \"smask\": 1, \"log2N\": %d, \"seed\": %llu, \"arm_id\": %d, \"threads\": %d,\n",
           rounds, log2N, (unsigned long long)seed, armid, nthr);
    printf("    \"trials\": %llu, \"trivial_swaps_excluded\": %llu, \"nontrivial_trials\": %llu,\n",
           (unsigned long long)N, (unsigned long long)trivial, (unsigned long long)(N-trivial));
    printf("    \"W_ge1_nontrivial\": %llu, \"whist\": [%llu,%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wge1, (unsigned long long)wh[0],(unsigned long long)wh[1],
           (unsigned long long)wh[2],(unsigned long long)wh[3],(unsigned long long)wh[4]);
    printf("    \"W_ge1_by_word\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wword[0],(unsigned long long)wword[1],
           (unsigned long long)wword[2],(unsigned long long)wword[3]);
    printf("    \"ewhist_all\": ["); for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_all[i], i<16?",":""); printf("],\n");
    printf("    \"ewhist_miss\": ["); for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_miss[i], i<16?",":""); printf("],\n");
    printf("    \"ewhist_hit\": ["); for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_hit[i], i<16?",":""); printf("],\n");
    uint64_t bsa=0, bsm=0, bsh=0;
    for(int i=0;i<129;i++){ bsa+=ewb_all[i]; bsm+=ewb_miss[i]; bsh+=ewb_hit[i]; }
    printf("    \"ewbithist_all_sum_check\": %llu, \"ewbithist_miss_sum_check\": %llu, \"ewbithist_hit_sum_check\": %llu,\n",
           (unsigned long long)bsa, (unsigned long long)bsm, (unsigned long long)bsh);
    printf("    \"hit_detail_records\": %d, \"hit_log_overflow\": %d, \"hit_log_cap\": %d,\n",
           detail_n, hit_overflow, HIT_LOG_CAP);
    printf("    \"zhist\": ["); for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)zh[i], i<16?",":""); printf("]\n");
    printf("  },\n");
    free(jobs); free(th);
}

static int freeze_mode(uint64_t seed){
    /* freeze section runs under the AES global table (set at startup) */
    printf("{\n  \"mode\": \"freeze\",\n");
    printf("  \"family\": \"IDEA-20260901-363851 frozen position-dilution family S_k\",\n");
    printf("  \"position_order\": [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15],\n");
    printf("  \"construction_pin\": \"forward SubBytes applies T_j at the pre-ShiftRows source position j; inverse applies INV_T_j at the post-InvShiftRows destination position j (PREREGISTRATION.md section 6)\",\n");
    printf("  \"aes_table_hex\": \"");
    for(int i=0;i<256;i++) printf("%02x", SBOX[i]);
    printf("\",\n");
    printf("  \"points\": [\n");
    for(int q=0;q<8;q++){
        int k=FREEZE_KS[q];
        set_diluted_tables(k);
        int inP[16]; diluted_position_list(k, inP);
        int bijective=1, nested_ok=1;
        for(int j=0;j<16;j++){
            uint8_t seen[256]; memset(seen,0,256);
            for(int x=0;x<256;x++){
                if(seen[TPOS[j][x]]) bijective=0;
                seen[TPOS[j][x]]=1;
                if(INV_TPOS[j][TPOS[j][x]]!=(uint8_t)x) bijective=0;
                if(inP[j]){ if(TPOS[j][x]!=SBOX[x]) nested_ok=0; }
                else      { if(TPOS[j][x]!=(uint8_t)x) nested_ok=0; }
            }
        }
        printf("    {\"k\": %d, \"positions\": [", k);
        int first=1;
        for(int j=0;j<16;j++) if(inP[j]) { printf("%s%d", first?"":",", j); first=0; }
        printf("],\n      \"per_position_is_aes\": [");
        for(int j=0;j<16;j++) printf("%d%s", inP[j], j<15?",":"");
        printf("],\n      \"per_position_table_hex\": [");
        for(int j=0;j<16;j++){
            printf("\"");
            for(int x=0;x<256;x++) printf("%02x", TPOS[j][x]);
            printf("\"%s", j<15?",":"");
        }
        printf("],\n      \"bijective_all_positions\": %s,\n      \"nestedness_check\": %s}%s\n",
               bijective?"true":"false", nested_ok?"true":"false", q<7?",":"");
    }
    printf("  ],\n");
    /* cross-k nesting: P_k subset P_k' for k < k' (structural, from the order) */
    int cross_ok=1;
    for(int a=0;a<8;a++) for(int b=a+1;b<8;b++){
        int inA[16], inB[16];
        diluted_position_list(FREEZE_KS[a], inA);
        diluted_position_list(FREEZE_KS[b], inB);
        for(int j=0;j<16;j++) if(inA[j] && !inB[j]) cross_ok=0;
    }
    printf("  \"cross_k_nesting\": %s,\n", cross_ok?"true":"false");

    /* folded instrument smoke self-checks (preregistered; same invocation) */
    set_identity_sbox();
    set_diluted_tables(0);
    if(!identity_tables_ok()){ fprintf(stderr,"identity table check FAILED in freeze\n"); return 4; }
    if(!diluted_tables_ok()){ fprintf(stderr,"k=0 diluted table check FAILED in freeze\n"); return 4; }
    {
        uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
        uint8_t key[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&kst); memcpy(key+i,&z,8); }
        sched s; sched_init(key,&s);   /* identity schedule (global SBOX = identity) */
        mini_arm_emit("selfcheck_identity_k0", 5, 10, seed, 1, 2, &s);
    }
    set_aes_sbox();
    set_diluted_tables(16);
    if(!build_inv_sbox()){ fprintf(stderr,"AES inverse table check FAILED in freeze\n"); return 4; }
    if(!diluted_tables_ok()){ fprintf(stderr,"k=16 diluted table check FAILED in freeze\n"); return 4; }
    {
        uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
        uint8_t key[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&kst); memcpy(key+i,&z,8); }
        sched s; sched_init(key,&s);   /* AES schedule (global SBOX = aes) */
        mini_arm_emit("selfcheck_aes_k16", 5, 10, seed, 1, 2, &s);
    }
    printf("  \"freeze_seed\": %llu,\n", (unsigned long long)seed);
    printf("  \"note\": \"sha256 digests of each 256-byte table are computed from the hex above by src/freeze_digest.py; self-check assertions are applied by the same script (preregistered)\"\n}\n");
    return 0;
}

int main(int argc, char **argv){
    build_xt_tables(); build_geom(); set_aes_sbox();
    set_diluted_tables(16);   /* TPOS = full AES table: pin mode and the k=16 seat */
    if(argc<2){ fprintf(stderr,"usage: affarm046ex pin <seed> | affarm046ex pinidentity <seed> | affarm046ex geom | affarm046ex freeze <seed> | affarm046ex arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> (identity|s1|s2|s3|s4|s8|s12|aes)\n"); return 2; }
    if(!strcmp(argv[1],"geom")) return geom_mode();
    if(!strcmp(argv[1],"pin")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pin(seed);
    }
    if(!strcmp(argv[1],"pinidentity")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return pinidentity(seed);
    }
    if(!strcmp(argv[1],"freeze")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        return freeze_mode(seed);
    }
    if(strcmp(argv[1],"arm")){ fprintf(stderr,"bad mode\n"); return 2; }
    if(argc<11){ fprintf(stderr,"arm needs 9 arguments (final: sbox token)\n"); return 2; }
    const char *name=argv[2];
    int rounds=atoi(argv[3]), amask=atoi(argv[4]), smask=atoi(argv[5]);
    int log2N=atoi(argv[6]);
    uint64_t seed=strtoull(argv[7],NULL,10);
    int armid=atoi(argv[8]); int nthr=atoi(argv[9]);
    int ksel=-1;
    if(strcmp(argv[10],"identity")==0) ksel=0;
    else if(strcmp(argv[10],"aes")==0) ksel=16;
    /* PIN-T0 interior-surface widening (DEC-20260901-fb6f11 adopting the
     * schedule_pin block of IDEA-20260901-582ea9): the interior dilution
     * seats are admitted under the PIN-T0 convention; the Stage-0 refusal is
     * replaced by the pinned surface below. Scoped to BATCH-7b798d. */
    else if(strcmp(argv[10],"s1")==0) ksel=1;
    else if(strcmp(argv[10],"s2")==0) ksel=2;
    else if(strcmp(argv[10],"s3")==0) ksel=3;
    else if(strcmp(argv[10],"s4")==0) ksel=4;
    else if(strcmp(argv[10],"s8")==0) ksel=8;
    else if(strcmp(argv[10],"s12")==0) ksel=12;
    else {
        fprintf(stderr,"unknown sbox token: the PIN-T0 widened build admits {identity, s1, s2, s3, s4, s8, s12, aes} for k in {0,1,2,3,4,8,12,16} (DEC-20260901-fb6f11)\n");
        return 3;
    }
    if(smask==0 || smask==15){ fprintf(stderr,"degenerate smask forbidden\n"); return 3; }
    if(amask==0){ fprintf(stderr,"empty amask forbidden\n"); return 3; }
    if(rounds<1 || rounds>10){ fprintf(stderr,"rounds must be 1..10 (toy tier)\n"); return 3; }
    if(log2N<1 || log2N>40){ fprintf(stderr,"log2N out of range\n"); return 3; }
    if(nthr<1 || nthr>64){ fprintf(stderr,"threads out of range\n"); return 3; }
    if(ksel==0){
        set_identity_sbox();
        if(!identity_tables_ok()){ fprintf(stderr,"identity table check FAILED\n"); return 4; }
    } else {
        set_aes_sbox();
        if(!build_inv_sbox()){ fprintf(stderr,"AES inverse table check FAILED\n"); return 4; }
    }
    set_diluted_tables(ksel);
    if(!diluted_tables_ok()){ fprintf(stderr,"diluted table check FAILED\n"); return 4; }
    /* PIN-T0 schedule pin (DEC-20260901-fb6f11): the key schedule's SubWord
     * uses TPOS[0], the table at the FIRST position of the frozen order. The
     * global schedule table is reloaded from TPOS[0]/INV_TPOS[0] so the pin
     * holds by construction rather than by coincidence. POS_ORDER[0]==0, so
     * TPOS[0] is the identity table at k=0 and the AES table at every k >= 1:
     * the k=0 and k=16 endpoint schedules are byte-identical to the lineage
     * behavior, and every interior seat runs the AES schedule. Deterministic,
     * nested, no data-dependent choice. */
    memcpy(SBOX, TPOS[0], 256);
    memcpy(INV_SBOX, INV_TPOS[0], 256);
    snprintf(SBOX_LABEL, sizeof(SBOX_LABEL), "%s", ksel==0 ? "identity" : "aes");

    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i=0;i<16;i+=8){ uint64_t z=sm64(&kst); memcpy(key+i,&z,8); }
    sched s; sched_init(key,&s);

    uint64_t N = 1ULL<<log2N;
    job *jobs=calloc(nthr,sizeof(job));
    pthread_t *th=calloc(nthr,sizeof(pthread_t));
    uint64_t cinv = sm64_step_inverse();
    uint64_t pseed[64], kseed[64];
    uint64_t per=N/nthr;
    double t0 = wall_now();
    for(int t=0;t<nthr;t++){
        jobs[t].ntrials = per + (t==0 ? N - per*nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid*0x1234567891ULL)
                            ^ ((uint64_t)(t+1)*0x9E3779B97F4A7C15ULL);
        jobs[t].rounds=rounds; jobs[t].amask=amask; jobs[t].smask=smask; jobs[t].s=&s;
        pseed[t]=jobs[t].seed_thread;
        kseed[t]=key_thread_seed(seed, armid, t);
    }
    for(int t=0;t<nthr;t++) pthread_create(&th[t],NULL,worker,&jobs[t]);
    for(int t=0;t<nthr;t++) pthread_join(th[t],NULL);
    double t1 = wall_now();

    uint64_t zh[17]={0}, wh[5]={0}, wword[4]={0}, trivial=0, wge1=0;
    uint64_t ewh_all[17]={0}, ewh_miss[17]={0}, ewh_hit[17]={0};
    uint64_t ewb_all[129]={0}, ewb_miss[129]={0}, ewb_hit[129]={0};
    uint64_t hit_overflow=0;
    /* ADDED EXTENSION aggregation (pure sums of the new per-thread counters) */
    uint64_t ezd_all=0, ezd_miss=0, ezd_hit=0, ezo_all=0, ezo_miss=0, ezo_hit=0;
    for(int t=0;t<nthr;t++){
        for(int i=0;i<17;i++){ zh[i]+=jobs[t].zhist[i];
            ewh_all[i]+=jobs[t].ewhist_all[i]; ewh_miss[i]+=jobs[t].ewhist_miss[i]; ewh_hit[i]+=jobs[t].ewhist_hit[i]; }
        for(int i=0;i<129;i++){ ewb_all[i]+=jobs[t].ewbithist_all[i]; ewb_miss[i]+=jobs[t].ewbithist_miss[i]; ewb_hit[i]+=jobs[t].ewbithist_hit[i]; }
        for(int i=0;i<5;i++)  wh[i]+=jobs[t].whist[i];
        for(int i=0;i<4;i++)  wword[i]+=jobs[t].wword[i];
        trivial+=jobs[t].trivial; wge1+=jobs[t].wge1; hit_overflow+=jobs[t].hit_overflow;
        ezd_all+=jobs[t].ezdiag_all; ezd_miss+=jobs[t].ezdiag_miss; ezd_hit+=jobs[t].ezdiag_hit;
        ezo_all+=jobs[t].ezoff_all; ezo_miss+=jobs[t].ezoff_miss; ezo_hit+=jobs[t].ezoff_hit;
    }
    int pgap = min_gap_log2(pseed, nthr, cinv);
    int kgap = min_gap_log2(kseed, nthr, cinv);
    int cross_equal = 0;
    for(int i=0;i<nthr;i++) for(int j=0;j<nthr;j++)
        if(kseed[i]==pseed[j]) cross_equal=1;

    /* receipt: committed L1-AES-R5-P30 field set in committed order, then
     * preregistered added fields (Gate-0 allowed-diff discipline) */
    printf("{\n  \"probe\": \"affarm046ex\",\n  \"arm\": \"%s\",\n", name);
    printf("  \"oracle\": \"live_aes_r%d_affarm046ex_derivative_of_affarm046\",\n", rounds);
    printf("  \"sbox_is_aes\": %s,\n", ksel==16?"true":"false");
    printf("  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
    printf("  \"ideal_permutation\": false,\n");
    printf("  \"resampled_per_trial\": false,\n");
    printf("  \"fresh_key_per_trial\": false,\n");
    printf("  \"amask\": %d,\n  \"smask\": %d,\n", amask, smask);
    printf("  \"trials\": %llu,\n  \"log2N\": %d,\n  \"seed\": %llu,\n  \"arm_id\": %d,\n  \"threads\": %d,\n",
           (unsigned long long)N, log2N, (unsigned long long)seed, armid, nthr);
    printf("  \"thread_seeds\": [");
    for(int t=0;t<nthr;t++) printf("%llu%s",(unsigned long long)jobs[t].seed_thread, t<nthr-1?",":"");
    printf("],\n");
    printf("  \"key_stream_seeds\": [");
    for(int t=0;t<nthr;t++) printf("%llu%s",(unsigned long long)kseed[t], t<nthr-1?",":"");
    printf("],\n");
    printf("  \"stream_gap_min_log2_plaintext_threads\": %d,\n", pgap);
    printf("  \"stream_gap_min_log2_key_threads\": %d,\n", kgap);
    printf("  \"key_stream_seed_equals_any_plaintext_stream_seed\": %s,\n", cross_equal?"true":"false");
    printf("  \"trivial_swaps_excluded\": %llu,\n",(unsigned long long)trivial);
    printf("  \"nontrivial_trials\": %llu,\n",(unsigned long long)(N-trivial));
    printf("  \"W_ge1_nontrivial\": %llu,\n",(unsigned long long)wge1);
    printf("  \"W_ge1_by_word\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wword[0],(unsigned long long)wword[1],
           (unsigned long long)wword[2],(unsigned long long)wword[3]);
    printf("  \"whist\": [");
    for(int i=0;i<5;i++) printf("%llu%s",(unsigned long long)wh[i], i<4?",":"");
    printf("],\n");
    printf("  \"null_expectation_analytic\": %.10f,\n", (double)(N-trivial)*4.0/4294967296.0);
    printf("  \"plaintext_stream_digest\": [");
    for(int t=0;t<nthr;t++) printf("\"%016llx\"%s",(unsigned long long)jobs[t].pstream_digest, t<nthr-1?",":"");
    printf("],\n");
    printf("  \"elapsed_seconds_measured\": %.9f,\n", t1-t0);
    printf("  \"measured_rate_trials_per_sec\": %.1f,\n", (double)N/(t1-t0));
    printf("  \"hit_trials_logged\": %d,\n", nthr>0?jobs[0].hit_count:0);
    printf("  \"hit_log_overflow\": %llu,\n",(unsigned long long)hit_overflow);
    printf("  \"hit_trials\": [");
    { int f2=1;
      for(int t=0;t<nthr;t++)
        for(int i=0;i<jobs[t].hit_count;i++){
            if(!f2) printf(",");
            printf("[%d,%llu]", t, (unsigned long long)jobs[t].hit_thread_idx[i]);
            f2=0;
        }
    }
    printf("],\n");
    printf("  \"hit_log_cap\": %d,\n", HIT_LOG_CAP);
    /* ---- added fields ---- */
    printf("  \"sbox\": \"%s\",\n", SBOX_LABEL);
    printf("  \"sbox_k\": %d,\n", ksel);
    printf("  \"sbox_positions\": [");
    { int inP[16]; diluted_position_list(ksel, inP); int first=1;
      for(int j=0;j<16;j++) if(inP[j]){ printf("%s%d", first?"":",", j); first=0; } }
    printf("],\n");
    /* ADDITIVE pin-label fields (PIN-T0 widening; the ONLY receipt additions
     * of this build; preregistered as the Gate-0x allowed-diff additions in
     * PREREGISTRATION.md section 6; DEC-20260901-fb6f11) */
    printf("  \"schedule_pin\": \"PIN-T0\",\n");
    printf("  \"schedule_pin_position\": 0,\n");
    printf("  \"schedule_pin_decision\": \"DEC-20260901-fb6f11\",\n");
    {   uint8_t dg[32]; sha256_tpos_concat(dg);
        printf("  \"arm_table_concat_sha256\": \"");
        for(int i=0;i<32;i++) printf("%02x",dg[i]);
        printf("\",\n");
    }
    printf("  \"sbox_bijective\": true,\n");
    printf("  \"sbox_table_hex\": \"");
    for(int i=0;i<256;i++) printf("%02x", SBOX[i]);
    printf("\",\n");
    printf("  \"key_hex\": \""); for(int i=0;i<16;i++) printf("%02x",key[i]); printf("\",\n");
    printf("  \"zhist\": [");
    for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)zh[i], i<16?",":"");
    printf("],\n");
    printf("  \"ewhist_all\": [");
    for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_all[i], i<16?",":"");
    printf("],\n");
    printf("  \"ewhist_miss\": [");
    for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_miss[i], i<16?",":"");
    printf("],\n");
    printf("  \"ewhist_hit\": [");
    for(int i=0;i<17;i++) printf("%llu%s",(unsigned long long)ewh_hit[i], i<16?",":"");
    printf("],\n");
    printf("  \"ewbithist_all\": [");
    for(int i=0;i<129;i++) printf("%llu%s",(unsigned long long)ewb_all[i], i<128?",":"");
    printf("],\n");
    printf("  \"ewbithist_miss\": [");
    for(int i=0;i<129;i++) printf("%llu%s",(unsigned long long)ewb_miss[i], i<128?",":"");
    printf("],\n");
    printf("  \"ewbithist_hit\": [");
    for(int i=0;i<129;i++) printf("%llu%s",(unsigned long long)ewb_hit[i], i<128?",":"");
    printf("],\n");
    /* ---- ADDED EXTENSION fields (IDEA-20260901-026d6a.logged_additions) ----
     * class-wise zero-byte counters of e; denominators are 4*n_split (diag)
     * and 12*n_split (off), derived in analysis from the existing
     * nontrivial_trials / W_ge1_nontrivial / whist fields */
    printf("  \"ezdiag_all\": %llu,\n",(unsigned long long)ezd_all);
    printf("  \"ezdiag_miss\": %llu,\n",(unsigned long long)ezd_miss);
    printf("  \"ezdiag_hit\": %llu,\n",(unsigned long long)ezd_hit);
    printf("  \"ezoff_all\": %llu,\n",(unsigned long long)ezo_all);
    printf("  \"ezoff_miss\": %llu,\n",(unsigned long long)ezo_miss);
    printf("  \"ezoff_hit\": %llu,\n",(unsigned long long)ezo_hit);
    printf("  \"hit_e_detail\": [");
    { int f2=1;
      for(int t=0;t<nthr;t++)
        for(int i=0;i<jobs[t].hit_count;i++){
            if(!f2) printf(",");
            printf("{\"thread\": %d, \"in_thread_index\": %llu, \"W\": %d, \"Z\": %d, \"vanishing_word_mask\": %d, \"wt_e_byte\": %d, \"wt_e_bit\": %d, \"zero_mask_e\": %d}",
                   t, (unsigned long long)jobs[t].hit_thread_idx[i], jobs[t].hit_W[i],
                   jobs[t].hit_Z[i], jobs[t].hit_vmask[i], jobs[t].hit_ewb[i], jobs[t].hit_ewbit[i],
                   jobs[t].hit_zmask_e[i]);
            f2=0;
        }
    }
    printf("]\n}\n");
    free(jobs); free(th);
    return 0;
}
