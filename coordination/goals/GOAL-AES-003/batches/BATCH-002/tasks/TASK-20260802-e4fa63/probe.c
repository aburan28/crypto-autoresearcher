/* TASK-20260802-e4fa63 yoyo probe -- written from scratch in this session.
 * Reuses no producer binary, no dispatcher binary and no BATCH-001 source.
 * Pure measurement. certificate.kind: none.
 *
 * Convention (see PREREGISTRATION.md sec.1):
 *   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
 *   round keys = first r+1 of the UNTRUNCATED FIPS-197 AES-128 expansion.
 * Geometry (sec.2):
 *   plaintext words  PW[j] = {4*((j+row)%4)+row}   -> PW[0]={0,5,10,15}
 *   ciphertext words CW[j] = {4*((j-row)%4)+row}   -> CW[0]={0,13,10,7}
 *
 * build: gcc -O2 -maes -msse4.1 -pthread -o probe probe.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <wmmintrin.h>
#include <smmintrin.h>

/* ---------- splitmix64 (this session's RNG) ---------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------- S-box derived from GF(2^8) inverse + affine map ---------- */
static uint8_t SBOX[256];
static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}
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

/* ---------- AES-128 key expansion, FIPS-197, 11 round keys ---------- */
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

typedef struct { __m128i ek[11]; __m128i dk[11]; } sched;

static void sched_init(const uint8_t key[16], sched *s){
    uint8_t rk[11][16]; key_expand(key, rk);
    for(int i=0;i<=10;i++) s->ek[i]=_mm_loadu_si128((const __m128i*)rk[i]);
    s->dk[0]=s->ek[0]; s->dk[10]=s->ek[10];
    for(int i=1;i<10;i++) s->dk[i]=_mm_aesimc_si128(s->ek[i]);
}

static inline __m128i enc_r(__m128i x, const sched *s, int r){
    x=_mm_xor_si128(x, s->ek[0]);
    for(int i=1;i<r;i++) x=_mm_aesenc_si128(x, s->ek[i]);
    return _mm_aesenclast_si128(x, s->ek[r]);
}
static inline __m128i dec_r(__m128i x, const sched *s, int r){
    x=_mm_xor_si128(x, s->ek[r]);
    for(int i=r-1;i>=1;i--) x=_mm_aesdec_si128(x, s->dk[i]);
    return _mm_aesdeclast_si128(x, s->ek[0]);
}

/* ---------- geometry ---------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j=0;j<4;j++) for(int row=0;row<4;row++){
        PW[j][row] = 4*(((j+row)%4+4)%4)+row;
        CW[j][row] = 4*(((j-row)%4+4)%4)+row;
    }
}

/* ---------- arm worker ---------- */
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
    union { __m128i v; uint8_t b[16]; } p0,p1,c0,c1,q0,q1,d;
    for(uint64_t t=0;t<J->ntrials;t++){
        uint64_t a=sm64(&st), b=sm64(&st);
        memcpy(p0.b, &a, 8); memcpy(p0.b+8, &b, 8);
        p1.v=p0.v;
        /* re-randomise every byte in every active word; reject zero word-diff */
        int ok=0;
        while(!ok){
            ok=1;
            for(int j=0;j<4;j++) if(J->amask & (1<<j)){
                uint64_t rnd=sm64(&st); int nz=0;
                for(int row=0;row<4;row++){
                    uint8_t nb=(uint8_t)(rnd>>(8*row));
                    p1.b[PW[j][row]]=nb;
                    if(nb != p0.b[PW[j][row]]) nz=1;
                }
                if(!nz) ok=0;
            }
        }
        c0.v=enc_r(p0.v,s,r);
        c1.v=enc_r(p1.v,s,r);
        /* swap ciphertext words in smask; detect trivial swap */
        int trivial=1;
        for(int j=0;j<4;j++) if(J->smask & (1<<j))
            for(int row=0;row<4;row++){
                int i=CW[j][row];
                uint8_t x=c0.b[i], y=c1.b[i];
                if(x!=y) trivial=0;
                c0.b[i]=y; c1.b[i]=x;
            }
        q0.v=dec_r(c0.v,s,r);
        q1.v=dec_r(c1.v,s,r);
        d.v=_mm_xor_si128(q0.v,q1.v);
        int Z=0; for(int i=0;i<16;i++) if(d.b[i]==0) Z++;
        int W=0;
        for(int j=0;j<4;j++){
            int z=1; for(int row=0;row<4;row++) if(d.b[PW[j][row]]) { z=0; break; }
            if(z){ W++; if(!trivial) J->wword[j]++; }
        }
        if(trivial){ J->trivial++; continue; }
        J->zhist[Z]++; J->whist[W]++;
        if(W>=1) J->wge1++;
    }
    return NULL;
}

/* ---------- pin ---------- */
static int pin(uint64_t seed){
    const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
    const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
    const uint8_t kat_ct[16]={0x69,0xc4,0xe0,0xd8,0x6a,0x7b,0x04,0x30,
                              0xd8,0xcd,0xb7,0x80,0x70,0xb4,0xc5,0x5a};
    sched s; sched_init(kat_key,&s);
    union { __m128i v; uint8_t b[16]; } x,y;
    memcpy(x.b,kat_pt,16);
    y.v=enc_r(x.v,&s,10);
    int kat_enc_ok = (memcmp(y.b,kat_ct,16)==0);
    memcpy(y.b,kat_ct,16);
    x.v=dec_r(y.v,&s,10);
    int kat_dec_ok = (memcmp(x.b,kat_pt,16)==0);
    printf("  \"fips197_c1_kat_encrypt_match\": %s,\n", kat_enc_ok?"true":"false");
    printf("  \"fips197_c1_kat_decrypt_match\": %s,\n", kat_dec_ok?"true":"false");
    printf("  \"fips197_c1_kat_ciphertext_computed\": \"");
    memcpy(x.b,kat_pt,16); y.v=enc_r(x.v,&s,10);
    for(int i=0;i<16;i++) printf("%02x", y.b[i]);
    printf("\",\n");

    uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            union { __m128i v; uint8_t b[16]; } a,c,e;
            memcpy(a.b,pt,16);
            c.v=enc_r(a.v,&sv,r);
            e.v=dec_r(c.v,&sv,r);
            if(memcmp(e.b,pt,16)!=0){ fails++; if(!first_fail_r) first_fail_r=r; }
        }
    }
    printf("  \"roundtrip_vectors\": %d,\n", nvec);
    printf("  \"roundtrip_rounds_each\": \"1..10\",\n");
    printf("  \"roundtrip_checks\": %d,\n", nvec*10);
    printf("  \"roundtrip_failures\": %d,\n", fails);
    printf("  \"roundtrip_first_failure_round\": %llu,\n",(unsigned long long)first_fail_r);
    printf("  \"pin_seed\": %llu,\n",(unsigned long long)seed);
    printf("  \"pin_pass\": %s\n", (kat_enc_ok&&kat_dec_ok&&fails==0)?"true":"false");
    return (kat_enc_ok&&kat_dec_ok&&fails==0)?0:1;
}

int main(int argc, char **argv){
    build_sbox(); build_geom();
    if(argc<2){ fprintf(stderr,"usage: probe pin <seed> | probe geom | probe arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>\n"); return 2; }
    if(!strcmp(argv[1],"geom")){
        printf("{\n  \"PW\": [");
        for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",PW[j][0],PW[j][1],PW[j][2],PW[j][3], j<3?",":""); }
        printf("],\n  \"CW\": [");
        for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",CW[j][0],CW[j][1],CW[j][2],CW[j][3], j<3?",":""); }
        printf("],\n  \"sbox_first8\": [");
        for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
        printf("],\n  \"sbox_source\": \"computed at runtime from GF(2^8) inverse + FIPS-197 affine map\"\n}\n");
        return 0;
    }
    if(!strcmp(argv[1],"pin")){
        uint64_t seed=strtoull(argv[2],NULL,10);
        printf("{\n  \"mode\": \"pin\",\n");
        int rc=pin(seed);
        printf("}\n");
        return rc;
    }
    if(strcmp(argv[1],"arm")) { fprintf(stderr,"bad mode\n"); return 2; }
    const char *name=argv[2];
    int rounds=atoi(argv[3]), amask=atoi(argv[4]), smask=atoi(argv[5]);
    int log2N=atoi(argv[6]);
    uint64_t seed=strtoull(argv[7],NULL,10);
    int armid=atoi(argv[8]); int nthr=atoi(argv[9]);
    if(smask==0 || smask==15){ fprintf(stderr,"degenerate smask forbidden\n"); return 3; }
    if(amask==0){ fprintf(stderr,"empty amask forbidden\n"); return 3; }

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
