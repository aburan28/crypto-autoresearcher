/* yoyo.c -- adaptive two-directional (yoyo-type) probing of reduced-round AES-128.
 *
 * INDEPENDENCE: AES is implemented here two ways --
 *   (1) AES-NI (aesenc/aesenclast/aesdec/aesdeclast/aesimc/aeskeygenassist),
 *   (2) a software reference whose S-box, inverse S-box, MixColumns and
 *       InvMixColumns matrices are DERIVED here from GF(2^8) arithmetic.
 * Machinery and reduced-round convention follow the campaign instrument
 * sq.c / aes_reduced.py:
 *   s = P ^ RK[0]; rounds 1..r-1 full; round r = SB,SR,ARK (no MixColumns);
 *   round keys = first r+1 of the standard FIPS-197 128-bit expansion.
 * Decryption is the exact inverse of that, both ways.
 *
 * Build: gcc -O3 -maes -msse4.1 -pthread -o yoyo yoyo.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <wmmintrin.h>
#include <smmintrin.h>
#include <math.h>

/* ---------------- GF(2^8), derived tables ---------------- */
static uint8_t SB[256], ISB[256];
static uint8_t gmul(uint8_t a, uint8_t b){ uint16_t r=0,x=a; for(int i=0;i<8;i++){ if((b>>i)&1) r^=x; x<<=1; if(x&0x100) x^=0x11b;} return (uint8_t)r; }
static uint8_t ginv(uint8_t a){ if(!a) return 0; uint8_t r=1; for(int i=0;i<254;i++) r=gmul(r,a); return r; }
static uint8_t affine(uint8_t b){ uint8_t o=0; for(int i=0;i<8;i++){ int bit=((b>>i)&1)^((b>>((i+4)&7))&1)^((b>>((i+5)&7))&1)^((b>>((i+6)&7))&1)^((b>>((i+7)&7))&1)^((0x63>>i)&1); o|=bit<<i;} return o; }
static void build_tables(void){ for(int x=0;x<256;x++) SB[x]=affine(ginv((uint8_t)x)); for(int x=0;x<256;x++) ISB[SB[x]]=(uint8_t)x; }
static const uint8_t MIX[4][4]={{2,3,1,1},{1,2,3,1},{1,1,2,3},{3,1,1,2}};
static const uint8_t IMIX[4][4]={{0x0e,0x0b,0x0d,0x09},{0x09,0x0e,0x0b,0x0d},{0x0d,0x09,0x0e,0x0b},{0x0b,0x0d,0x09,0x0e}};

/* word structures, derived in the pre-registration (section 1) */
/* plaintext words  PW[j][r] = 4*((j+r) mod 4) + r  (forward diagonals)      */
/* ciphertext words CW[j][r] = 4*((j-r) mod 4) + r  (inverse-SR diagonals)   */
static int PW[4][4], CW[4][4];
static void build_words(void){
    for(int j=0;j<4;j++) for(int r=0;r<4;r++){
        PW[j][r] = 4*((j+r)&3) + r;
        CW[j][r] = 4*(((j-r)&3)) + r;
    }
}

/* ---------------- software reference (column-major state) ---------------- */
static uint8_t rcon_v(int i){ uint8_t v=1; for(int j=1;j<i;j++) v=gmul(v,2); return v; }
static void key_expand(const uint8_t key[16], uint8_t rk[][16], int nrk){
    uint8_t w[4*64]; memcpy(w,key,16);
    for(int i=4;i<4*nrk;i++){
        uint8_t t[4]; memcpy(t,w+4*(i-1),4);
        if(i%4==0){ uint8_t tmp=t[0]; t[0]=SB[t[1]]; t[1]=SB[t[2]]; t[2]=SB[t[3]]; t[3]=SB[tmp]; t[0]^=rcon_v(i/4); }
        for(int j=0;j<4;j++) w[4*i+j]=w[4*(i-4)+j]^t[j];
    }
    for(int r=0;r<nrk;r++) memcpy(rk[r], w+16*r, 16);
}
static void sw_encrypt(const uint8_t *pt, uint8_t rk[][16], int rounds, uint8_t *out){
    uint8_t s[16],t[16];
    for(int i=0;i<16;i++) s[i]=pt[i]^rk[0][i];
    for(int r=1;r<=rounds;r++){
        for(int i=0;i<16;i++) t[i]=SB[s[i]];
        for(int rr=0;rr<4;rr++) for(int c=0;c<4;c++) s[c*4+rr]=t[((c+rr)&3)*4+rr];
        if(r!=rounds){
            memcpy(t,s,16);
            for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++){
                uint8_t a=0; for(int k=0;k<4;k++) a^=gmul(MIX[rr][k], t[4*c+k]); s[4*c+rr]=a; }
        }
        for(int i=0;i<16;i++) s[i]^=rk[r][i];
    }
    memcpy(out,s,16);
}
/* exact inverse of sw_encrypt: ARK, [IMC], ISR, ISB per round, descending */
static void sw_decrypt(const uint8_t *ct, uint8_t rk[][16], int rounds, uint8_t *out){
    uint8_t s[16],t[16];
    memcpy(s,ct,16);
    for(int r=rounds;r>=1;r--){
        for(int i=0;i<16;i++) s[i]^=rk[r][i];
        if(r!=rounds){
            memcpy(t,s,16);
            for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++){
                uint8_t a=0; for(int k=0;k<4;k++) a^=gmul(IMIX[rr][k], t[4*c+k]); s[4*c+rr]=a; }
        }
        memcpy(t,s,16);
        for(int rr=0;rr<4;rr++) for(int c=0;c<4;c++) s[c*4+rr]=t[((c-rr)&3)*4+rr]; /* ISR */
        for(int i=0;i<16;i++) s[i]=ISB[s[i]];
    }
    for(int i=0;i<16;i++) s[i]^=rk[0][i];
    memcpy(out,s,16);
}

/* ---------------- AES-NI ---------------- */
typedef struct { __m128i e[11]; __m128i d[11]; } nikey; /* d[i]=aesimc(e[i]) for 1<=i<=9 */
static void ni_key_expand(const uint8_t key[16], nikey *K){
    __m128i k=_mm_loadu_si128((const __m128i*)key); K->e[0]=k;
    for(int i=0;i<10;i++){
        __m128i t;
        switch(i){
            case 0: t=_mm_aeskeygenassist_si128(k,0x01); break;
            case 1: t=_mm_aeskeygenassist_si128(k,0x02); break;
            case 2: t=_mm_aeskeygenassist_si128(k,0x04); break;
            case 3: t=_mm_aeskeygenassist_si128(k,0x08); break;
            case 4: t=_mm_aeskeygenassist_si128(k,0x10); break;
            case 5: t=_mm_aeskeygenassist_si128(k,0x20); break;
            case 6: t=_mm_aeskeygenassist_si128(k,0x40); break;
            case 7: t=_mm_aeskeygenassist_si128(k,0x80); break;
            case 8: t=_mm_aeskeygenassist_si128(k,0x1b); break;
            default:t=_mm_aeskeygenassist_si128(k,0x36); break;
        }
        t=_mm_shuffle_epi32(t,0xff);
        __m128i s=_mm_slli_si128(k,4); k=_mm_xor_si128(k,s);
        s=_mm_slli_si128(s,4); k=_mm_xor_si128(k,s);
        s=_mm_slli_si128(s,4); k=_mm_xor_si128(k,s);
        k=_mm_xor_si128(k,t);
        K->e[i+1]=k;
    }
    K->d[0]=K->e[0]; K->d[10]=K->e[10];
    for(int i=1;i<10;i++) K->d[i]=_mm_aesimc_si128(K->e[i]);
}
static inline __m128i ni_enc(__m128i b, const nikey *K, int rounds){
    b=_mm_xor_si128(b, K->e[0]);
    for(int i=1;i<rounds;i++) b=_mm_aesenc_si128(b, K->e[i]);
    return _mm_aesenclast_si128(b, K->e[rounds]);
}
/* equivalent inverse cipher: xor last rk, aesdec with InvMixColumns'd middle
   round keys in descending order, aesdeclast with rk[0]. */
static inline __m128i ni_dec(__m128i b, const nikey *K, int rounds){
    b=_mm_xor_si128(b, K->e[rounds]);
    for(int i=rounds-1;i>=1;i--) b=_mm_aesdec_si128(b, K->d[i]);
    return _mm_aesdeclast_si128(b, K->e[0]);
}

/* ---------------- utilities ---------------- */
static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+1e-9*ts.tv_nsec; }
static void hex2bin(const char*h, uint8_t*o, int n){ for(int i=0;i<n;i++){ unsigned v; sscanf(h+2*i,"%2x",&v); o[i]=v; } }
static void phex(const uint8_t*b,int n){ for(int i=0;i<n;i++) printf("%02x",b[i]); }
static inline uint64_t splitmix64(uint64_t *s){
    uint64_t z=(*s+=0x9E3779B97F4A7C15ULL);
    z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL;
    z=(z^(z>>27))*0x94D049BB133111EBULL;
    return z^(z>>31);
}

/* =========================================================================
 *  MODE selftest : both implementations, BOTH directions, r = 1..10
 * ========================================================================= */
static int mode_selftest(int argc, char**argv){
    (void)argc;
    uint8_t key[16], pt[16]; hex2bin(argv[2],key,16); hex2bin(argv[3],pt,16);
    uint8_t rk[11][16]; key_expand(key,rk,11);
    nikey K; ni_key_expand(key,&K);
    printf("{\"key\":\""); phex(key,16); printf("\",\"pt\":\""); phex(pt,16); printf("\",\"rounds\":{");
    for(int r=1;r<=10;r++){
        uint8_t o1[16],o2[16],b1[16],b2[16];
        sw_encrypt(pt,rk,r,o1);
        _mm_storeu_si128((__m128i*)o2, ni_enc(_mm_loadu_si128((const __m128i*)pt),&K,r));
        /* decrypt the SOFTWARE ciphertext with both, so decryption is pinned
           against an independently produced ciphertext */
        sw_decrypt(o1,rk,r,b1);
        _mm_storeu_si128((__m128i*)b2, ni_dec(_mm_loadu_si128((const __m128i*)o1),&K,r));
        printf("%s\"%d\":{\"sw_enc\":\"", r>1?",":"", r); phex(o1,16);
        printf("\",\"ni_enc\":\""); phex(o2,16);
        printf("\",\"sw_dec_of_sw_enc\":\""); phex(b1,16);
        printf("\",\"ni_dec_of_sw_enc\":\""); phex(b2,16); printf("\"}");
    }
    printf("}}\n");
    return 0;
}

/* MODE decvec : decrypt a GIVEN ciphertext at each r (for cross-impl pinning
 * of the decryption direction on ciphertexts that are not images of anything) */
static int mode_decvec(int argc, char**argv){
    (void)argc;
    uint8_t key[16], ct[16]; hex2bin(argv[2],key,16); hex2bin(argv[3],ct,16);
    uint8_t rk[11][16]; key_expand(key,rk,11);
    nikey K; ni_key_expand(key,&K);
    printf("{\"key\":\""); phex(key,16); printf("\",\"ct\":\""); phex(ct,16); printf("\",\"rounds\":{");
    for(int r=1;r<=10;r++){
        uint8_t o1[16],o2[16];
        sw_decrypt(ct,rk,r,o1);
        _mm_storeu_si128((__m128i*)o2, ni_dec(_mm_loadu_si128((const __m128i*)ct),&K,r));
        printf("%s\"%d\":{\"sw_dec\":\"", r>1?",":"", r); phex(o1,16);
        printf("\",\"ni_dec\":\""); phex(o2,16); printf("\"}");
    }
    printf("}}\n");
    return 0;
}

/* =========================================================================
 *  MODE yoyo : the object.  See PREREGISTRATION.md section 2.
 * ========================================================================= */
#define BATCH 4
typedef struct {
    uint64_t seed;
    uint64_t ntrials;
    int rounds, amask, smask, rekey;
    uint8_t basekey[16];
    uint64_t zhist[17], whist[5];
    uint64_t whist_nt[5];      /* W histogram over NON-TRIVIAL swaps only */
    uint64_t trivial;          /* swap was a no-op: Dc == 0 on every word of S */
    uint64_t ctzw[5];          /* # of zero-difference ciphertext words in Dc */
    uint64_t wpos[4];          /* for W==1 non-trivial events: which plaintext word */
    uint64_t xtab[5][5];       /* [ctzw][W] cross-tab, non-trivial only */
    uint64_t degenerate;
    uint64_t done;
} jobY;

static void* workerY(void*arg){
    jobY *J=(jobY*)arg;
    memset(J->zhist,0,sizeof J->zhist); memset(J->whist,0,sizeof J->whist);
    memset(J->whist_nt,0,sizeof J->whist_nt); memset(J->ctzw,0,sizeof J->ctzw);
    memset(J->wpos,0,sizeof J->wpos); memset(J->xtab,0,sizeof J->xtab);
    J->trivial=0; J->degenerate=0;
    uint64_t st=J->seed;
    nikey K;
    if(!J->rekey) ni_key_expand(J->basekey,&K);
    uint64_t n=0;
    uint8_t p0[BATCH][16], p1[BATCH][16], c0[BATCH][16], c1[BATCH][16];
    while(n < J->ntrials){
        if(J->rekey){ uint8_t kk[16]; for(int i=0;i<2;i++){ uint64_t v=splitmix64(&st); memcpy(kk+8*i,&v,8);} ni_key_expand(kk,&K); }
        for(int b=0;b<BATCH;b++){
            for(int i=0;i<2;i++){ uint64_t v=splitmix64(&st); memcpy(p0[b]+8*i,&v,8); }
            memcpy(p1[b],p0[b],16);
            for(int j=0;j<4;j++) if((J->amask>>j)&1){
                for(;;){
                    uint64_t v=splitmix64(&st);
                    int diff=0;
                    for(int r=0;r<4;r++){ uint8_t nb=(uint8_t)(v>>(8*r)); p1[b][PW[j][r]]=nb; if(nb!=p0[b][PW[j][r]]) diff=1; }
                    if(diff) break;
                    J->degenerate++;  /* resampled; counted */
                }
            }
        }
        __m128i x[2*BATCH];
        for(int b=0;b<BATCH;b++){ x[2*b]=_mm_loadu_si128((const __m128i*)p0[b]); x[2*b+1]=_mm_loadu_si128((const __m128i*)p1[b]); }
        for(int i=0;i<2*BATCH;i++) x[i]=_mm_xor_si128(x[i],K.e[0]);
        for(int rr=1;rr<J->rounds;rr++) for(int i=0;i<2*BATCH;i++) x[i]=_mm_aesenc_si128(x[i],K.e[rr]);
        for(int i=0;i<2*BATCH;i++) x[i]=_mm_aesenclast_si128(x[i],K.e[J->rounds]);
        for(int b=0;b<BATCH;b++){ _mm_storeu_si128((__m128i*)c0[b],x[2*b]); _mm_storeu_si128((__m128i*)c1[b],x[2*b+1]); }
        /* diagnostics on the ciphertext difference, computed BEFORE the swap */
        int triv[BATCH], nzw[BATCH];
        for(int b=0;b<BATCH;b++){
            int t=1, z=0;
            for(int j=0;j<4;j++){
                int allz=1; for(int r=0;r<4;r++) if(c0[b][CW[j][r]]!=c1[b][CW[j][r]]) allz=0;
                if(allz) z++;
                if(((J->smask>>j)&1) && !allz) t=0;
            }
            triv[b]=t; nzw[b]=z; J->ctzw[z]++;
        }
        /* swap ciphertext words in S */
        for(int b=0;b<BATCH;b++) for(int j=0;j<4;j++) if((J->smask>>j)&1)
            for(int r=0;r<4;r++){ uint8_t t=c0[b][CW[j][r]]; c0[b][CW[j][r]]=c1[b][CW[j][r]]; c1[b][CW[j][r]]=t; }
        for(int b=0;b<BATCH;b++){ x[2*b]=_mm_loadu_si128((const __m128i*)c0[b]); x[2*b+1]=_mm_loadu_si128((const __m128i*)c1[b]); }
        for(int i=0;i<2*BATCH;i++) x[i]=_mm_xor_si128(x[i],K.e[J->rounds]);
        for(int rr=J->rounds-1;rr>=1;rr--) for(int i=0;i<2*BATCH;i++) x[i]=_mm_aesdec_si128(x[i],K.d[rr]);
        for(int i=0;i<2*BATCH;i++) x[i]=_mm_aesdeclast_si128(x[i],K.e[0]);
        for(int b=0;b<BATCH;b++){
            __m128i d=_mm_xor_si128(x[2*b],x[2*b+1]);
            uint8_t dd[16]; _mm_storeu_si128((__m128i*)dd,d);
            int Z=0; for(int i=0;i<16;i++) if(!dd[i]) Z++;
            int W=0; for(int j=0;j<4;j++){ int z=1; for(int r=0;r<4;r++) if(dd[PW[j][r]]) z=0; W+=z; }
            J->zhist[Z]++; J->whist[W]++;
            if(!triv[b]){
                J->whist_nt[W]++;
                J->xtab[nzw[b]][W]++;
                if(W==1) for(int j=0;j<4;j++){ int z=1; for(int r=0;r<4;r++) if(dd[PW[j][r]]) z=0; if(z) J->wpos[j]++; }
            } else J->trivial++;
        }
        n+=BATCH;
    }
    J->done=n;
    return 0;
}

static int mode_yoyo(int argc,char**argv){
    /* yoyo <keyhex|"rekey"> <rounds> <amask> <smask> <log2_trials> <seed> [threads] */
    const char *keyarg=argv[2];
    int rounds=atoi(argv[3]); int amask=atoi(argv[4]); int smask=atoi(argv[5]);
    double lg=atof(argv[6]);
    uint64_t seed=strtoull(argv[7],0,10);
    int nthreads=argc>8?atoi(argv[8]):4;
    int rekey = !strcmp(keyarg,"rekey");
    uint8_t key[16]; memset(key,0,16);
    if(!rekey) hex2bin(keyarg,key,16);
    uint64_t total=(uint64_t)(lg>=63?0:( (double)1.0*(1ULL<<(int)lg) ));
    if(lg!=(int)lg) total=(uint64_t)(pow(2.0,lg));
    uint64_t per=total/nthreads; per=(per/BATCH)*BATCH; if(per<BATCH) per=BATCH;
    jobY J[8]; pthread_t th[8];
    for(int t=0;t<nthreads;t++){
        memset(&J[t],0,sizeof J[t]);
        J[t].seed = seed ^ (0xA5A5A5A5A5A5A5A5ULL*(uint64_t)(t+1));
        J[t].ntrials=per; J[t].rounds=rounds; J[t].amask=amask; J[t].smask=smask;
        J[t].rekey=rekey; memcpy(J[t].basekey,key,16);
    }
    double t0=now();
    for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,workerY,&J[t]);
    uint64_t zh[17]={0}, wh[5]={0}, whnt[5]={0}, ctz[5]={0}, wp[4]={0}, xt[5][5]={{0}}, triv=0, deg=0, n=0;
    for(int t=0;t<nthreads;t++){ pthread_join(th[t],0);
        for(int i=0;i<17;i++) zh[i]+=J[t].zhist[i];
        for(int i=0;i<5;i++){ wh[i]+=J[t].whist[i]; whnt[i]+=J[t].whist_nt[i]; ctz[i]+=J[t].ctzw[i]; }
        for(int i=0;i<4;i++) wp[i]+=J[t].wpos[i];
        for(int a=0;a<5;a++) for(int b=0;b<5;b++) xt[a][b]+=J[t].xtab[a][b];
        triv+=J[t].trivial; deg+=J[t].degenerate; n+=J[t].done; }
    double t1=now();
    printf("{\"mode\":\"yoyo\",\"key\":\"%s\",\"rounds\":%d,\"amask\":%d,\"smask\":%d,\"seed\":%llu,"
           "\"threads\":%d,\"trials\":%llu,\"seconds\":%.3f,\"resampled_zero_word_diffs\":%llu,\"zhist\":[",
           rekey?"rekey":argv[2],rounds,amask,smask,(unsigned long long)seed,nthreads,
           (unsigned long long)n,t1-t0,(unsigned long long)deg);
    for(int i=0;i<17;i++) printf("%s%llu",i?",":"",(unsigned long long)zh[i]);
    printf("],\"whist\":[");
    for(int i=0;i<5;i++) printf("%s%llu",i?",":"",(unsigned long long)wh[i]);
    printf("],\"trivial_swaps\":%llu,\"whist_nontrivial\":[",(unsigned long long)triv);
    for(int i=0;i<5;i++) printf("%s%llu",i?",":"",(unsigned long long)whnt[i]);
    printf("],\"ct_zero_words_hist\":[");
    for(int i=0;i<5;i++) printf("%s%llu",i?",":"",(unsigned long long)ctz[i]);
    printf("],\"W1_word_index\":[");
    for(int i=0;i<4;i++) printf("%s%llu",i?",":"",(unsigned long long)wp[i]);
    printf("],\"xtab_ctzerowords_by_W\":[");
    for(int a=0;a<5;a++){ printf("%s[",a?",":""); for(int b=0;b<5;b++) printf("%s%llu",b?",":"",(unsigned long long)xt[a][b]); printf("]"); }
    printf("]}\n");
    return 0;
}

/* =========================================================================
 *  MODE roundtrip : V3 check, D(E(x)) == x for both impls, all r, N randoms
 * ========================================================================= */
static int mode_roundtrip(int argc,char**argv){
    (void)argc;
    int n=atoi(argv[2]); uint64_t seed=strtoull(argv[3],0,10);
    uint64_t st=seed; int fail=0, checked=0;
    for(int i=0;i<n;i++){
        uint8_t key[16],pt[16];
        for(int q=0;q<2;q++){ uint64_t v=splitmix64(&st); memcpy(key+8*q,&v,8); }
        for(int q=0;q<2;q++){ uint64_t v=splitmix64(&st); memcpy(pt+8*q,&v,8); }
        uint8_t rk[11][16]; key_expand(key,rk,11); nikey K; ni_key_expand(key,&K);
        for(int r=1;r<=10;r++){
            uint8_t e1[16],e2[16],d1[16],d2[16];
            sw_encrypt(pt,rk,r,e1);
            _mm_storeu_si128((__m128i*)e2, ni_enc(_mm_loadu_si128((const __m128i*)pt),&K,r));
            sw_decrypt(e1,rk,r,d1);
            _mm_storeu_si128((__m128i*)d2, ni_dec(_mm_loadu_si128((const __m128i*)e2),&K,r));
            checked++;
            if(memcmp(e1,e2,16)||memcmp(d1,pt,16)||memcmp(d2,pt,16)) fail++;
        }
    }
    printf("{\"mode\":\"roundtrip\",\"vectors\":%d,\"checks\":%d,\"failures\":%d}\n",n,checked,fail);
    return fail?1:0;
}

int main(int argc,char**argv){
    build_tables(); build_words();
    if(argc<2){ fprintf(stderr,"usage: yoyo <mode> ...\n"); return 2; }
    if(!strcmp(argv[1],"selftest"))  return mode_selftest(argc,argv);
    if(!strcmp(argv[1],"decvec"))    return mode_decvec(argc,argv);
    if(!strcmp(argv[1],"roundtrip")) return mode_roundtrip(argc,argv);
    if(!strcmp(argv[1],"yoyo"))      return mode_yoyo(argc,argv);
    if(!strcmp(argv[1],"words")){
        printf("{\"PW\":[");
        for(int j=0;j<4;j++){ printf("%s[",j?",":""); for(int r=0;r<4;r++) printf("%s%d",r?",":"",PW[j][r]); printf("]"); }
        printf("],\"CW\":[");
        for(int j=0;j<4;j++){ printf("%s[",j?",":""); for(int r=0;r<4;r++) printf("%s%d",r?",":"",CW[j][r]); printf("]"); }
        printf("]}\n"); return 0; }
    fprintf(stderr,"unknown mode\n"); return 2;
}
