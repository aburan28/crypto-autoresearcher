/* sq.c -- reduced-round AES-128 integral (Square) attacks.
 *
 * INDEPENDENCE: this file implements AES from scratch two ways --
 *   (1) AES-NI hardware instructions (aesenc / aesenclast / aeskeygenassist),
 *   (2) a software reference whose S-box, inverse S-box and MixColumns
 *       matrices are DERIVED here from GF(2^8) arithmetic.
 * No table or code is taken from aes_reduced.py or from pycryptodome. Cross
 * agreement with those two is therefore meaningful.
 *
 * Reduced-round convention matches the campaign instrument aes_reduced.py:
 *   s = P ^ RK[0]; rounds 1..r-1 full; round r = SB,SR,ARK (no MixColumns);
 *   round keys = first r+1 of the standard FIPS-197 128-bit expansion.
 * AES-NI implements exactly this: (r-1) x aesenc + 1 x aesenclast.
 *
 * Build: gcc -O3 -maes -msse4.1 -pthread -o sq sq.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <wmmintrin.h>
#include <smmintrin.h>

/* ---------------- GF(2^8), derived tables ---------------- */
static uint8_t SB[256], ISB[256];
static uint8_t gmul(uint8_t a, uint8_t b){ uint16_t r=0,x=a; for(int i=0;i<8;i++){ if((b>>i)&1) r^=x; x<<=1; if(x&0x100) x^=0x11b;} return (uint8_t)r; }
static uint8_t ginv(uint8_t a){ if(!a) return 0; uint8_t r=1; for(int i=0;i<254;i++) r=gmul(r,a); return r; }
static uint8_t affine(uint8_t b){ uint8_t o=0; for(int i=0;i<8;i++){ int bit=((b>>i)&1)^((b>>((i+4)&7))&1)^((b>>((i+5)&7))&1)^((b>>((i+6)&7))&1)^((b>>((i+7)&7))&1)^((0x63>>i)&1); o|=bit<<i;} return o; }
static void build_tables(void){ for(int x=0;x<256;x++) SB[x]=affine(ginv((uint8_t)x)); for(int x=0;x<256;x++) ISB[SB[x]]=(uint8_t)x; }
static const uint8_t MIX[4][4]={{2,3,1,1},{1,2,3,1},{1,1,2,3},{3,1,1,2}};
static const uint8_t IMIX[4][4]={{0x0e,0x0b,0x0d,0x09},{0x09,0x0e,0x0b,0x0d},{0x0d,0x09,0x0e,0x0b},{0x0b,0x0d,0x09,0x0e}};

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
/* invert the key schedule: given RK[r], recover RK[0] (the master key) */
static void key_invert(const uint8_t rkr[16], int r, uint8_t master[16]){
    uint8_t w[4*64]; memcpy(w+16*r, rkr, 16); /* words 4r..4r+3 known */
    for(int i=4*r+3;i>=4;i--){
        uint8_t *wi=w+4*i, *wm4=w+4*(i-4), *wm1=w+4*(i-1);
        /* w[i] = w[i-4] ^ f(w[i-1]) ; we know w[i] and w[i-1] (computed later),
           so iterate downward: w[i-4] = w[i] ^ f(w[i-1]) */
        uint8_t t[4]; memcpy(t,wm1,4);
        if(i%4==0){ uint8_t tmp=t[0]; t[0]=SB[t[1]]; t[1]=SB[t[2]]; t[2]=SB[t[3]]; t[3]=SB[tmp]; t[0]^=rcon_v(i/4); }
        for(int j=0;j<4;j++) wm4[j]=wi[j]^t[j];
    }
    memcpy(master,w,16);
}

/* ---------------- AES-NI ---------------- */
static __m128i ni_rk[11];
static void ni_key_expand(const uint8_t key[16]){
    static const int rc[10]={0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
    __m128i k=_mm_loadu_si128((const __m128i*)key); ni_rk[0]=k;
    for(int i=0;i<10;i++){
        __m128i t;
        switch(rc[i]){
            case 0x01: t=_mm_aeskeygenassist_si128(k,0x01); break;
            case 0x02: t=_mm_aeskeygenassist_si128(k,0x02); break;
            case 0x04: t=_mm_aeskeygenassist_si128(k,0x04); break;
            case 0x08: t=_mm_aeskeygenassist_si128(k,0x08); break;
            case 0x10: t=_mm_aeskeygenassist_si128(k,0x10); break;
            case 0x20: t=_mm_aeskeygenassist_si128(k,0x20); break;
            case 0x40: t=_mm_aeskeygenassist_si128(k,0x40); break;
            case 0x80: t=_mm_aeskeygenassist_si128(k,0x80); break;
            case 0x1b: t=_mm_aeskeygenassist_si128(k,0x1b); break;
            default:   t=_mm_aeskeygenassist_si128(k,0x36); break;
        }
        t=_mm_shuffle_epi32(t,0xff);
        __m128i s=_mm_slli_si128(k,4); k=_mm_xor_si128(k,s);
        s=_mm_slli_si128(s,4); k=_mm_xor_si128(k,s);
        s=_mm_slli_si128(s,4); k=_mm_xor_si128(k,s);
        k=_mm_xor_si128(k,t);
        ni_rk[i+1]=k;
    }
}
static inline __m128i ni_enc(__m128i b, int rounds){
    b=_mm_xor_si128(b, ni_rk[0]);
    for(int i=1;i<rounds;i++) b=_mm_aesenc_si128(b, ni_rk[i]);
    b=_mm_aesenclast_si128(b, ni_rk[rounds]);
    return b;
}

/* ---------------- utilities ---------------- */
static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+1e-9*ts.tv_nsec; }
static void hex2bin(const char*h, uint8_t*o, int n){ for(int i=0;i<n;i++){ unsigned v; sscanf(h+2*i,"%2x",&v); o[i]=v; } }
static void phex(const uint8_t*b,int n){ for(int i=0;i<n;i++) printf("%02x",b[i]); }

/* =========================================================================
 *  MODE selftest : print reduced-round ciphertexts from BOTH implementations
 * ========================================================================= */
static int mode_selftest(int argc, char**argv){
    uint8_t key[16], pt[16]; hex2bin(argv[2],key,16); hex2bin(argv[3],pt,16);
    uint8_t rk[11][16]; key_expand(key,rk,11);
    ni_key_expand(key);
    printf("{\"key\":\""); phex(key,16); printf("\",\"pt\":\""); phex(pt,16); printf("\",\"rounds\":{");
    for(int r=1;r<=10;r++){
        uint8_t o1[16],o2[16];
        sw_encrypt(pt,rk,r,o1);
        __m128i c=ni_enc(_mm_loadu_si128((const __m128i*)pt), r);
        _mm_storeu_si128((__m128i*)o2,c);
        printf("%s\"%d\":{\"sw\":\"", r>1?",":"", r); phex(o1,16);
        printf("\",\"aesni\":\""); phex(o2,16); printf("\"}");
    }
    printf("}}\n");
    return 0;
}

/* =========================================================================
 *  MODE attack4 : 4-round key recovery from Lambda-sets of 256 texts
 * ========================================================================= */
static int mode_attack4(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    unsigned seed = (unsigned)strtoul(argv[3],0,10);
    ni_key_expand(key);
    int R=4;
    /* per position: candidate sets intersected over successive Lambda-sets */
    uint8_t cand[16][256]; memset(cand,1,sizeof cand);
    int nsets=0; long long partial_decrypts=0; long long chosen_pt=0;
    double t0=now();
    srand(seed);
    int remaining[16]; int done=0;
    while(!done && nsets<8){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        int actpos = nsets % 16;
        uint8_t par[16][256]; memset(par,0,sizeof par);
        for(int v=0;v<256;v++){
            uint8_t pt[16]; memcpy(pt,base,16); pt[actpos]=v;
            __m128i c=ni_enc(_mm_loadu_si128((const __m128i*)pt),R);
            uint8_t ct[16]; _mm_storeu_si128((__m128i*)ct,c);
            for(int i=0;i<16;i++) par[i][ct[i]]^=1;
            chosen_pt++;
        }
        for(int i=0;i<16;i++) for(int k=0;k<256;k++){
            if(!cand[i][k]) continue;
            uint8_t s=0; for(int v=0;v<256;v++) if(par[i][v]) s^=ISB[v^k];
            partial_decrypts += 256;
            if(s) cand[i][k]=0;
        }
        nsets++;
        done=1; for(int i=0;i<16;i++){ int c=0; for(int k=0;k<256;k++) c+=cand[i][k]; remaining[i]=c; if(c!=1) done=0; }
    }
    double t1=now();
    uint8_t rk4[16]; int ok=1;
    for(int i=0;i<16;i++){ int f=-1; for(int k=0;k<256;k++) if(cand[i][k]){ if(f<0) f=k; else ok=0; } rk4[i]=f<0?0:f; if(f<0) ok=0; }
    uint8_t master[16]; key_invert(rk4,4,master);
    printf("{\"rounds\":4,\"lambda_sets\":%d,\"chosen_plaintexts\":%lld,\"partial_decryptions\":%lld,"
           "\"seconds\":%.4f,\"unique\":%d,\"rk4\":\"", nsets, chosen_pt, partial_decrypts, t1-t0, ok);
    phex(rk4,16); printf("\",\"recovered_master\":\""); phex(master,16); printf("\"}\n");
    return 0;
}

/* =========================================================================
 *  MODE attack5 : 5-round key recovery, 2^32-text structure
 *  Structure: plaintext bytes {0,5,10,15} take all 2^32 values (that diagonal
 *  maps to one column under ShiftRows), other 12 bytes constant.
 *  After round 1 the set is a union of 2^24 one-byte-active Lambda-sets, so it
 *  is balanced after 4 rounds -> one round is peeled with one key byte guess.
 * ========================================================================= */
typedef struct { uint8_t base[16]; int rounds; int b0lo,b0hi; uint64_t par[16][256/64]; uint64_t n; } job5;
static const int DIAG[4]={0,5,10,15};
static void* worker5(void*arg){
    job5*J=(job5*)arg; memset(J->par,0,sizeof J->par); uint64_t n=0;
    uint8_t pt[16]; memcpy(pt,J->base,16);
    uint8_t parb[16][256]; memset(parb,0,sizeof parb);
    for(int b0=J->b0lo;b0<J->b0hi;b0++){
        pt[DIAG[0]]=b0;
        for(int b1=0;b1<256;b1++){ pt[DIAG[1]]=b1;
        for(int b2=0;b2<256;b2++){ pt[DIAG[2]]=b2;
            for(int b3=0;b3<256;b3+=4){
                pt[DIAG[3]]=b3;   __m128i x0=_mm_loadu_si128((const __m128i*)pt);
                pt[DIAG[3]]=b3+1; __m128i x1=_mm_loadu_si128((const __m128i*)pt);
                pt[DIAG[3]]=b3+2; __m128i x2=_mm_loadu_si128((const __m128i*)pt);
                pt[DIAG[3]]=b3+3; __m128i x3=_mm_loadu_si128((const __m128i*)pt);
                x0=_mm_xor_si128(x0,ni_rk[0]); x1=_mm_xor_si128(x1,ni_rk[0]);
                x2=_mm_xor_si128(x2,ni_rk[0]); x3=_mm_xor_si128(x3,ni_rk[0]);
                for(int i=1;i<J->rounds;i++){ x0=_mm_aesenc_si128(x0,ni_rk[i]); x1=_mm_aesenc_si128(x1,ni_rk[i]);
                                              x2=_mm_aesenc_si128(x2,ni_rk[i]); x3=_mm_aesenc_si128(x3,ni_rk[i]); }
                x0=_mm_aesenclast_si128(x0,ni_rk[J->rounds]); x1=_mm_aesenclast_si128(x1,ni_rk[J->rounds]);
                x2=_mm_aesenclast_si128(x2,ni_rk[J->rounds]); x3=_mm_aesenclast_si128(x3,ni_rk[J->rounds]);
                uint8_t c[4][16];
                _mm_storeu_si128((__m128i*)c[0],x0); _mm_storeu_si128((__m128i*)c[1],x1);
                _mm_storeu_si128((__m128i*)c[2],x2); _mm_storeu_si128((__m128i*)c[3],x3);
                for(int j=0;j<4;j++) for(int i=0;i<16;i++) parb[i][c[j][i]]^=1;
                n+=4;
            }
        }}
    }
    for(int i=0;i<16;i++) for(int v=0;v<256;v++) if(parb[i][v]) J->par[i][v>>6]^=1ULL<<(v&63);
    J->n=n; return 0;
}
static void run_structure(const uint8_t base[16], int rounds, uint8_t par[16][256], uint64_t*ntexts, int nthreads){
    job5 J[8]; pthread_t th[8];
    int step=256/nthreads;
    for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds; J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step; }
    for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker5,&J[t]);
    uint64_t n=0; memset(par,0,16*256);
    for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
        for(int i=0;i<16;i++) for(int v=0;v<256;v++) par[i][v]^= (J[t].par[i][v>>6]>>(v&63))&1; }
    *ntexts=n;
}
static int mode_attack5(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    int rounds = atoi(argv[3]);            /* 5 for the attack, 10 for the PRP control */
    int nstruct = atoi(argv[4]);
    unsigned seed=(unsigned)strtoul(argv[5],0,10);
    int nthreads = argc>6?atoi(argv[6]):4;
    ni_key_expand(key); srand(seed);
    uint8_t cand[16][256]; memset(cand,1,sizeof cand);
    uint64_t total=0; long long pdec=0; double t0=now();
    printf("{\"rounds\":%d,\"structures\":[", rounds);
    for(int s=0;s<nstruct;s++){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        uint8_t par[16][256]; uint64_t n; double ts=now();
        run_structure(base,rounds,par,&n,nthreads); total+=n;
        int surv[16];
        for(int i=0;i<16;i++){ int c=0;
            for(int k=0;k<256;k++){ if(!cand[i][k]) continue;
                uint8_t sm=0; for(int v=0;v<256;v++) if(par[i][v]) sm^=ISB[v^k];
                pdec+=256; if(sm) cand[i][k]=0; else c++; }
            surv[i]=c; }
        printf("%s{\"idx\":%d,\"base\":\"",s?",":"",s); phex(base,16);
        printf("\",\"texts\":%llu,\"seconds\":%.2f,\"survivors_per_byte\":[",(unsigned long long)n, now()-ts);
        for(int i=0;i<16;i++) printf("%s%d",i?",":"",surv[i]);
        printf("]}"); fflush(stdout);
    }
    double t1=now();
    uint8_t rk[16]; int uniq=1;
    for(int i=0;i<16;i++){ int f=-1,c=0; for(int k=0;k<256;k++) if(cand[i][k]){ if(f<0)f=k; c++; } rk[i]=f<0?0:f; if(c!=1) uniq=0; }
    uint8_t master[16]; key_invert(rk,rounds,master);
    printf("],\"chosen_plaintexts\":%llu,\"partial_decryptions\":%lld,\"seconds\":%.2f,\"unique\":%d,\"rk_last\":\"",
           (unsigned long long)total,pdec,t1-t0,uniq);
    phex(rk,16); printf("\",\"recovered_master\":\""); phex(master,16); printf("\"}\n");
    return 0;
}


/* =========================================================================
 *  MODE targets : emit (plaintext, ciphertext) pairs from the ORACLE at a
 *  given round count, for independent certificate verification.
 * ========================================================================= */
static int mode_targets(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    int rounds=atoi(argv[3]); int n=atoi(argv[4]); unsigned seed=(unsigned)strtoul(argv[5],0,10);
    ni_key_expand(key); srand(seed);
    printf("{\"rounds\":%d,\"pairs\":[",rounds);
    for(int i=0;i<n;i++){
        uint8_t pt[16]; for(int j=0;j<16;j++) pt[j]=rand()&0xff;
        uint8_t ct[16]; _mm_storeu_si128((__m128i*)ct, ni_enc(_mm_loadu_si128((const __m128i*)pt),rounds));
        printf("%s[\"",i?",":""); phex(pt,16); printf("\",\""); phex(ct,16); printf("\"]");
    }
    printf("]}\n"); return 0;
}

/* =========================================================================
 *  MODE attack6 : 6-round key recovery, partial sums, RESTRICTED key space.
 *
 *  Balance holds at level 4 (after 4 rounds) for the 2^32-text structure.
 *  For ciphertext diagonal d (positions p0..p3 -> column c of level5) and row r:
 *      sum_texts  ISB[ (XOR_t IMIX[r][t] * ISB[C[p_t]^K6[p_t]]) ^ K5'[4c+r] ] = 0
 *  5 unknown bytes (K6[p0..p3], K5'[4c+r]).  This mode is given K6[p0],K6[p1],
 *  K6[p2] as a hint and searches (K6[p3], K5') = 2^16 per (d,r); across the 4
 *  diagonals the searched space is 2^32 on K6 plus 16 bytes of K5'.
 *  Partial sums: the first three bytes are folded ON THE FLY into a parity
 *  table indexed by (z012, c3) of 2^16 bits, so the 2^32 texts are touched
 *  once instead of once per candidate key.
 * ========================================================================= */
static uint8_t GM[256][256];
static void build_gm(void){ for(int a=0;a<256;a++) for(int x=0;x<256;x++) GM[a][x]=gmul((uint8_t)a,(uint8_t)x); }
/* level5[4c+r] = ISB[ C[q] ^ K6[q] ] with q = 4*((c-r) mod 4) + r, i.e. the
   INVERSE-ShiftRows diagonal of the ciphertext (fixed after a first run in
   which the forward-ShiftRows diagonal was used by mistake: see report). */
static const int DIAGP[4][4]={{0,13,10,7},{4,1,14,11},{8,5,2,15},{12,9,6,3}};
typedef struct { uint8_t base[16]; int rounds; int b0lo,b0hi; uint8_t hint[4][3];
                 uint64_t (*tab)[4][1024]; uint64_t n; } job6;   /* tab[d][r][2^16 bits] */
static void* worker6(void*arg){
    job6*J=(job6*)arg; memset(J->tab,0,4*4*1024*8); uint64_t n=0;
    uint8_t pt[16]; memcpy(pt,J->base,16);
    /* per-diagonal combined tables: Z[d][r][u0][u1] would be 64K each; instead
       fold with per-coefficient multiplication tables (L1-resident). */
    for(int b0=J->b0lo;b0<J->b0hi;b0++){ pt[DIAG[0]]=b0;
      for(int b1=0;b1<256;b1++){ pt[DIAG[1]]=b1;
        for(int b2=0;b2<256;b2++){ pt[DIAG[2]]=b2;
          for(int b3=0;b3<256;b3+=4){
            __m128i x[4];
            for(int q=0;q<4;q++){ pt[DIAG[3]]=b3+q; x[q]=_mm_xor_si128(_mm_loadu_si128((const __m128i*)pt),ni_rk[0]); }
            for(int i=1;i<J->rounds;i++) for(int q=0;q<4;q++) x[q]=_mm_aesenc_si128(x[q],ni_rk[i]);
            for(int q=0;q<4;q++) x[q]=_mm_aesenclast_si128(x[q],ni_rk[J->rounds]);
            uint8_t c[4][16];
            for(int q=0;q<4;q++) _mm_storeu_si128((__m128i*)c[q],x[q]);
            for(int q=0;q<4;q++){
              for(int d=0;d<4;d++){
                uint8_t u0=ISB[c[q][DIAGP[d][0]]^J->hint[d][0]];
                uint8_t u1=ISB[c[q][DIAGP[d][1]]^J->hint[d][1]];
                uint8_t u2=ISB[c[q][DIAGP[d][2]]^J->hint[d][2]];
                uint8_t c3b=c[q][DIAGP[d][3]];
                for(int r=0;r<4;r++){
                  uint8_t z = GM[IMIX[r][0]][u0]^GM[IMIX[r][1]][u1]^GM[IMIX[r][2]][u2];
                  unsigned idx = ((unsigned)z<<8)|c3b;
                  J->tab[d][r][idx>>6] ^= 1ULL<<(idx&63);
                }
              }
            }
            n+=4;
          } } } }
    J->n=n; return 0;
}
static int mode_attack6(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    int rounds=atoi(argv[3]);              /* 6 for the attack, 10 for the PRP control */
    int nstruct=atoi(argv[4]); unsigned seed=(unsigned)strtoul(argv[5],0,10);
    int nthreads=argc>6?atoi(argv[6]):4;
    build_gm(); ni_key_expand(key); srand(seed);
    /* oracle-side: true round keys, used ONLY to supply the 3-byte hints */
    uint8_t rk[11][16]; key_expand(key,rk,11);
    uint8_t hint[4][3];
    for(int d=0;d<4;d++) for(int t=0;t<3;t++) hint[d][t]=rk[rounds][DIAGP[d][t]];
    /* candidate bitmaps cand[d][r][k3][k4] */
    static uint8_t cand[4][4][256][256];
    memset(cand,1,sizeof cand);
    double t0=now(); uint64_t total=0; long long fold_ops=0, ps_ops=0;
    printf("{\"rounds\":%d,\"hint_bytes_per_diagonal\":3,\"structures\":[",rounds);
    for(int s=0;s<nstruct;s++){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        job6 J[8]; pthread_t th[8]; int step=256/nthreads;
        for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds;
            J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step;
            memcpy(J[t].hint,hint,sizeof hint);
            J[t].tab=malloc(4*4*1024*8); }
        double ts=now();
        for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker6,&J[t]);
        static uint64_t tab[4][4][1024]; memset(tab,0,sizeof tab);
        uint64_t n=0;
        for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
            for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int w=0;w<1024;w++) tab[d][r][w]^=J[t].tab[d][r][w];
            free(J[t].tab); }
        total+=n; fold_ops += (long long)n*16;
        double tfold=now()-ts;
        /* ---- partial-sums tail: fold byte 3 (guess k3), then test k4 ---- */
        double tp=now();
        for(int d=0;d<4;d++) for(int r=0;r<4;r++){
            uint8_t a3=IMIX[r][3];
            for(int k3=0;k3<256;k3++){
                uint8_t hist[256]; memset(hist,0,256);
                for(unsigned idx=0;idx<65536;idx++){
                    if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
                    uint8_t z=idx>>8, c3b=idx&0xff;
                    hist[z ^ GM[a3][ISB[c3b^k3]]] ^= 1;
                }
                ps_ops += 65536;
                for(int k4=0;k4<256;k4++){
                    if(!cand[d][r][k3][k4]) continue;
                    uint8_t sm=0; for(int v=0;v<256;v++) if(hist[v]) sm^=ISB[v^k4];
                    ps_ops += 256;
                    if(sm) cand[d][r][k3][k4]=0;
                }
            }
        }
        double tps=now()-tp;
        long long surv=0; for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int a=0;a<256;a++) for(int b=0;b<256;b++) surv+=cand[d][r][a][b];
        printf("%s{\"idx\":%d,\"base\":\"",s?",":"",s); phex(base,16);
        printf("\",\"texts\":%llu,\"fold_seconds\":%.2f,\"partialsum_seconds\":%.2f,\"surviving_(k3,k4)_pairs\":%lld}",
               (unsigned long long)n,tfold,tps,surv); fflush(stdout);
    }
    /* consistency: K6[p3] must agree across the 4 rows of a diagonal */
    uint8_t rk6[16]; int uniq=1;
    for(int d=0;d<4;d++){
        for(int t=0;t<3;t++) rk6[DIAGP[d][t]]=hint[d][t];
        int found=-1,cnt=0;
        for(int k3=0;k3<256;k3++){
            int ok=1;
            for(int r=0;r<4;r++){ int any=0; for(int k4=0;k4<256;k4++) if(cand[d][r][k3][k4]) any=1; if(!any) ok=0; }
            if(ok){ cnt++; if(found<0) found=k3; }
        }
        if(cnt!=1) uniq=0;
        rk6[DIAGP[d][3]] = found<0?0:found;
    }
    uint8_t master[16]; key_invert(rk6,rounds,master);
    double t1=now();
    printf("],\"chosen_plaintexts\":%llu,\"fold_ops\":%lld,\"partialsum_ops\":%lld,\"seconds\":%.2f,"
           "\"unique\":%d,\"rk_last\":\"",(unsigned long long)total,fold_ops,ps_ops,t1-t0,uniq);
    phex(rk6,16); printf("\",\"recovered_master\":\""); phex(master,16); printf("\"}\n");
    return 0;
}


/* =========================================================================
 *  MODE compare6 : NAIVE vs PARTIAL SUMS on the identical 6-round subproblem,
 *  identical input data, both implemented here, both run to completion.
 *
 *  Subproblem: given the parity table T[z012][c3] (2^16 bits) produced by one
 *  2^32-text structure with three last-round-key bytes folded in, decide which
 *  of the 2^16 candidates (k3,k4) satisfy the balance equation
 *      XOR_{texts} ISB[ z012 ^ IMIX[r][3]*ISB[c3^k3] ^ k4 ] = 0.
 *  NAIVE      : for each of the 2^16 candidates, re-sum the whole table.
 *  PARTIALSUMS: for each k3 fold the table once into a 256-bin histogram, then
 *               reuse that histogram for all 256 values of k4.
 *  Both must return the SAME candidate set; that equality is checked.
 * ========================================================================= */
static int mode_compare6(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    int rounds=atoi(argv[3]); unsigned seed=(unsigned)strtoul(argv[4],0,10);
    int nthreads=argc>5?atoi(argv[5]):4;
    build_gm(); ni_key_expand(key); srand(seed);
    uint8_t rk[11][16]; key_expand(key,rk,11);
    uint8_t hint[4][3]; for(int d=0;d<4;d++) for(int t=0;t<3;t++) hint[d][t]=rk[rounds][DIAGP[d][t]];
    uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
    job6 J[8]; pthread_t th[8]; int step=256/nthreads;
    for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds;
        J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step;
        memcpy(J[t].hint,hint,sizeof hint); J[t].tab=malloc(4*4*1024*8); }
    double ts=now();
    for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker6,&J[t]);
    static uint64_t tab[4][4][1024]; memset(tab,0,sizeof tab); uint64_t n=0;
    for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
        for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int w=0;w<1024;w++) tab[d][r][w]^=J[t].tab[d][r][w];
        free(J[t].tab); }
    double tfold=now()-ts;
    int d=0,r=0; uint8_t a3=IMIX[r][3];
    int odd=0; for(unsigned i=0;i<65536;i++) if((tab[d][r][i>>6]>>(i&63))&1) odd++;
    /* ---- NAIVE ---- */
    static uint8_t candN[256][256]; long long naive_ops=0; double t0=now();
    for(int k3=0;k3<256;k3++) for(int k4=0;k4<256;k4++){
        uint8_t sm=0;
        for(unsigned idx=0;idx<65536;idx++){
            if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
            sm ^= ISB[ (uint8_t)(idx>>8) ^ GM[a3][ISB[(idx&0xff)^k3]] ^ k4 ];
        }
        naive_ops += odd; candN[k3][k4] = (sm==0);
    }
    double naive_s=now()-t0;
    /* ---- PARTIAL SUMS ---- */
    static uint8_t candP[256][256]; long long ps_ops=0; t0=now();
    for(int k3=0;k3<256;k3++){
        uint8_t hist[256]; memset(hist,0,256);
        for(unsigned idx=0;idx<65536;idx++){
            if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
            hist[ (uint8_t)(idx>>8) ^ GM[a3][ISB[(idx&0xff)^k3]] ] ^= 1;
        }
        ps_ops += odd;
        for(int k4=0;k4<256;k4++){
            uint8_t sm=0; for(int v=0;v<256;v++) if(hist[v]) sm^=ISB[v^k4];
            ps_ops += 256; candP[k3][k4]=(sm==0);
        }
    }
    double ps_s=now()-t0;
    int agree=1,nc=0; for(int a=0;a<256;a++) for(int b=0;b<256;b++){ if(candN[a][b]!=candP[a][b]) agree=0; nc+=candN[a][b]; }
    printf("{\"rounds\":%d,\"texts\":%llu,\"fold_seconds\":%.2f,\"odd_table_entries\":%d,"
           "\"naive\":{\"seconds\":%.3f,\"table_reads\":%lld},"
           "\"partial_sums\":{\"seconds\":%.3f,\"table_reads\":%lld},"
           "\"measured_speedup\":%.2f,\"op_count_ratio\":%.2f,\"same_candidate_set\":%d,\"candidates\":%d}\n",
           rounds,(unsigned long long)n,tfold,odd,naive_s,naive_ops,ps_s,ps_ops,
           naive_s/ps_s,(double)naive_ops/(double)ps_ops,agree,nc);
    return 0;
}


/* =========================================================================
 *  MODE attack7 : 7-ROUND SCOPED PROBE.  *** NOT A KEY RECOVERY ***
 *
 *  The attacker is GIVEN the whole last round key K7 (so it can peel round 7)
 *  and 3 of the 4 bytes of each K6' = MC^{-1}(K6) diagonal.  It then searches
 *  for the remaining K6' byte and the K5' byte using the SAME level-4 balance
 *  property and the SAME partial-sum fold as the 6-round attack:
 *      level6 = ISB(SR^{-1}(C ^ K7));  Z = MC^{-1}(level6)
 *      level5[4c+r] = ISB[ Z[q] ^ K6'[q] ],  q = 4*((c-r) mod 4)+r
 *      XOR_texts ISB[ (XOR_t IMIX[r][t]*level5[4c+t]) ^ K5'[4c+r] ] = 0
 *  Because K7 is an input, the master key is NOT recovered here; this run
 *  measures only whether the integral filter still isolates the correct bytes
 *  at 7 rounds.  No certificate is claimed for it.
 * ========================================================================= */
typedef struct { uint8_t base[16]; int rounds; int b0lo,b0hi; uint8_t k7[16]; uint8_t hint[4][3];
                 uint64_t (*tab)[4][1024]; uint64_t n; } job7;
static void* worker7(void*arg){
    job7*J=(job7*)arg; memset(J->tab,0,4*4*1024*8); uint64_t n=0;
    uint8_t pt[16]; memcpy(pt,J->base,16);
    for(int b0=J->b0lo;b0<J->b0hi;b0++){ pt[DIAG[0]]=b0;
      for(int b1=0;b1<256;b1++){ pt[DIAG[1]]=b1;
        for(int b2=0;b2<256;b2++){ pt[DIAG[2]]=b2;
          for(int b3=0;b3<256;b3+=4){
            __m128i x[4];
            for(int q=0;q<4;q++){ pt[DIAG[3]]=b3+q; x[q]=_mm_xor_si128(_mm_loadu_si128((const __m128i*)pt),ni_rk[0]); }
            for(int i=1;i<J->rounds;i++) for(int q=0;q<4;q++) x[q]=_mm_aesenc_si128(x[q],ni_rk[i]);
            for(int q=0;q<4;q++) x[q]=_mm_aesenclast_si128(x[q],ni_rk[J->rounds]);
            uint8_t c[4][16];
            for(int q=0;q<4;q++) _mm_storeu_si128((__m128i*)c[q],x[q]);
            for(int q=0;q<4;q++){
              uint8_t l6[16], Z[16];
              for(int cc=0;cc<4;cc++) for(int rr=0;rr<4;rr++)
                  l6[4*cc+rr] = ISB[ c[q][DIAGP[cc][rr]] ^ J->k7[DIAGP[cc][rr]] ];
              for(int cc=0;cc<4;cc++) for(int rr=0;rr<4;rr++)
                  Z[4*cc+rr] = GM[IMIX[rr][0]][l6[4*cc+0]]^GM[IMIX[rr][1]][l6[4*cc+1]]
                             ^ GM[IMIX[rr][2]][l6[4*cc+2]]^GM[IMIX[rr][3]][l6[4*cc+3]];
              for(int d=0;d<4;d++){
                uint8_t u0=ISB[Z[DIAGP[d][0]]^J->hint[d][0]];
                uint8_t u1=ISB[Z[DIAGP[d][1]]^J->hint[d][1]];
                uint8_t u2=ISB[Z[DIAGP[d][2]]^J->hint[d][2]];
                uint8_t z3=Z[DIAGP[d][3]];
                for(int r=0;r<4;r++){
                  uint8_t z = GM[IMIX[r][0]][u0]^GM[IMIX[r][1]][u1]^GM[IMIX[r][2]][u2];
                  unsigned idx=((unsigned)z<<8)|z3;
                  J->tab[d][r][idx>>6]^=1ULL<<(idx&63);
                }
              }
            }
            n+=4;
          } } } }
    J->n=n; return 0;
}
static int mode_attack7(int argc,char**argv){
    uint8_t key[16]; hex2bin(argv[2],key,16);
    int rounds=atoi(argv[3]); int nstruct=atoi(argv[4]); unsigned seed=(unsigned)strtoul(argv[5],0,10);
    int nthreads=argc>6?atoi(argv[6]):4;
    build_gm(); ni_key_expand(key); srand(seed);
    uint8_t rk[12][16]; key_expand(key,rk,12);
    uint8_t k6p[16];   /* K6' = MC^{-1}(K6) */
    for(int cc=0;cc<4;cc++) for(int rr=0;rr<4;rr++)
        k6p[4*cc+rr]=GM[IMIX[rr][0]][rk[rounds-1][4*cc+0]]^GM[IMIX[rr][1]][rk[rounds-1][4*cc+1]]
                    ^GM[IMIX[rr][2]][rk[rounds-1][4*cc+2]]^GM[IMIX[rr][3]][rk[rounds-1][4*cc+3]];
    uint8_t hint[4][3]; for(int d=0;d<4;d++) for(int t=0;t<3;t++) hint[d][t]=k6p[DIAGP[d][t]];
    static uint8_t cand[4][4][256][256]; memset(cand,1,sizeof cand);
    double t0=now(); uint64_t total=0;
    printf("{\"rounds\":%d,\"given\":\"full K%d + 3 of 4 K%d' bytes per diagonal\",\"structures\":[",rounds,rounds,rounds-1);
    for(int s=0;s<nstruct;s++){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        job7 J[8]; pthread_t th[8]; int step=256/nthreads;
        for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds;
            J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step;
            memcpy(J[t].k7,rk[rounds],16); memcpy(J[t].hint,hint,sizeof hint);
            J[t].tab=malloc(4*4*1024*8); }
        double ts=now();
        for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker7,&J[t]);
        static uint64_t tab[4][4][1024]; memset(tab,0,sizeof tab); uint64_t n=0;
        for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
            for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int w=0;w<1024;w++) tab[d][r][w]^=J[t].tab[d][r][w];
            free(J[t].tab); }
        total+=n; double tfold=now()-ts; double tp=now();
        for(int d=0;d<4;d++) for(int r=0;r<4;r++){
            uint8_t a3=IMIX[r][3];
            for(int k3=0;k3<256;k3++){
                uint8_t hist[256]; memset(hist,0,256);
                for(unsigned idx=0;idx<65536;idx++){
                    if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
                    hist[(uint8_t)(idx>>8) ^ GM[a3][ISB[(idx&0xff)^k3]]] ^= 1;
                }
                for(int k4=0;k4<256;k4++){
                    if(!cand[d][r][k3][k4]) continue;
                    uint8_t sm=0; for(int v=0;v<256;v++) if(hist[v]) sm^=ISB[v^k4];
                    if(sm) cand[d][r][k3][k4]=0;
                }
            }
        }
        long long surv=0; for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int a=0;a<256;a++) for(int b=0;b<256;b++) surv+=cand[d][r][a][b];
        printf("%s{\"idx\":%d,\"texts\":%llu,\"fold_seconds\":%.2f,\"tail_seconds\":%.2f,\"surviving_pairs\":%lld}",
               s?",":"",s,(unsigned long long)n,tfold,now()-tp,surv); fflush(stdout);
    }
    /* which K6' byte survives on every row of its diagonal, and is it the true one? */
    int correct=0, uniq=1; uint8_t rec[4], truth[4];
    for(int d=0;d<4;d++){
        int found=-1,cnt=0;
        for(int k3=0;k3<256;k3++){ int ok=1;
            for(int r=0;r<4;r++){ int any=0; for(int k4=0;k4<256;k4++) if(cand[d][r][k3][k4]) any=1; if(!any) ok=0; }
            if(ok){ cnt++; if(found<0) found=k3; } }
        if(cnt!=1) uniq=0;
        rec[d]=found<0?0:found; truth[d]=k6p[DIAGP[d][3]];
        if(cnt==1 && rec[d]==truth[d]) correct++;
    }
    printf("],\"chosen_plaintexts\":%llu,\"seconds\":%.2f,\"unique_per_diagonal\":%d,"
           "\"recovered_K6prime_bytes\":\"",(unsigned long long)total,now()-t0,uniq);
    phex(rec,4); printf("\",\"true_K6prime_bytes\":\""); phex(truth,4);
    printf("\",\"diagonals_correct\":%d,\"note\":\"NOT a key recovery: K%d was given as input\"}\n",correct,rounds);
    return 0;
}

/* =========================================================================
 *  ADDED FOR TASK-20260802-9dcca8 (BATCH-002 rank 1): the WRONG-HINT NULL.
 *  Modes attack6n / attack7n are byte-for-byte the BATCH-001 attack6 /
 *  attack7 pipelines (same worker6/worker7 fold, same partial-sum tail,
 *  same survivor test) with exactly TWO changes:
 *    (1) the 3 hint bytes per diagonal may be taken from a SEPARATE hint
 *        key instead of the target key's own schedule (nwrong of 3),
 *    (2) richer reporting: per-diagonal survivor count, the full survivor
 *        list, the true byte and the hint key's corresponding byte.
 *  The oracle ALWAYS encrypts under the target key. In attack7n the last
 *  round key K7 handed to the attack is ALWAYS the TRUE one, exactly as
 *  in BATCH-001, so the only variable changed is the truth of the hint.
 *  usage: sq_null attack6n <targetkey> <hintkey> <rounds> <nstruct> <seed> <nthreads> <nwrong>
 * ========================================================================= */
static void print_diag_report(uint8_t cand[4][4][256][256], const uint8_t hint[4][3],
                              const uint8_t truebase[16], const uint8_t hintbase[16], int nwrong){
    int uniq=1, ncorrect=0, nmatch_hintkey=0, ndiag_nonempty=0;
    printf(",\"diagonals\":[");
    for(int d=0;d<4;d++){
        int cnt=0, surv[256];
        for(int k3=0;k3<256;k3++){
            int ok=1;
            for(int r=0;r<4;r++){ int any=0; for(int k4=0;k4<256;k4++) if(cand[d][r][k3][k4]) any=1; if(!any) ok=0; }
            if(ok) surv[cnt++]=k3;
        }
        if(cnt!=1) uniq=0;
        if(cnt>0) ndiag_nonempty++;
        uint8_t tb=truebase[DIAGP[d][3]], hb=hintbase[DIAGP[d][3]];
        int matches_true=0, matches_hintkey=0;
        for(int i=0;i<cnt;i++){ if(surv[i]==tb) matches_true=1; if(surv[i]==hb) matches_hintkey=1; }
        if(cnt==1 && surv[0]==tb) ncorrect++;
        if(cnt==1 && surv[0]==hb) nmatch_hintkey++;
        printf("%s{\"d\":%d,\"survivor_count\":%d,\"survivors\":[",d?",":"",d,cnt);
        for(int i=0;i<cnt;i++) printf("%s%d",i?",":"",surv[i]);
        printf("],\"true_byte\":%d,\"hintkey_byte\":%d,\"unique\":%d,"
               "\"unique_survivor_is_true_byte\":%d,\"unique_survivor_is_hintkey_byte\":%d,"
               "\"true_byte_among_survivors\":%d,\"hintkey_byte_among_survivors\":%d,\"hint_used\":[%d,%d,%d],"
               "\"hint_true\":[%d,%d,%d],\"hint_bytes_actually_differing\":%d}",
               tb,hb,cnt==1,(cnt==1&&surv[0]==tb),(cnt==1&&surv[0]==hb),matches_true,matches_hintkey,
               hint[d][0],hint[d][1],hint[d][2],
               truebase[DIAGP[d][0]],truebase[DIAGP[d][1]],truebase[DIAGP[d][2]],
               (hint[d][0]!=truebase[DIAGP[d][0]])+(hint[d][1]!=truebase[DIAGP[d][1]])+(hint[d][2]!=truebase[DIAGP[d][2]]));
    }
    printf("],\"nwrong_requested\":%d,\"unique_all_diagonals\":%d,\"diagonals_with_survivors\":%d,"
           "\"diagonals_unique_and_correct\":%d,\"diagonals_unique_and_equal_hintkey_byte\":%d",
           nwrong,uniq,ndiag_nonempty,ncorrect,nmatch_hintkey);
}
static int mode_attack6n(int argc,char**argv){
    if(argc<9){ fprintf(stderr,"usage: sq_null attack6n <targetkey> <hintkey> <rounds> <nstruct> <seed> <nthreads> <nwrong>\n"); return 2; }
    uint8_t key[16], hkey[16]; hex2bin(argv[2],key,16); hex2bin(argv[3],hkey,16);
    int rounds=atoi(argv[4]); int nstruct=atoi(argv[5]); unsigned seed=(unsigned)strtoul(argv[6],0,10);
    int nthreads=atoi(argv[7]); int nwrong=atoi(argv[8]);
    /* TASK-20260802-447db8 RANK 4: optional SLOT BITMASK semantics. With the
       literal 9th argument "mask", argv[8] is a bitmask over slots t=0,1,2
       instead of a prefix length. Without it, slotmask=(1<<nwrong)-1 reproduces
       the original prefix semantics EXACTLY. This is the only behavioural
       change made to sq_null.c. */
    int slotmask = (argc>9 && !strcmp(argv[9],"mask")) ? nwrong : ((1<<nwrong)-1);
    build_gm(); ni_key_expand(key); srand(seed);
    uint8_t rk[11][16], hrk[11][16]; key_expand(key,rk,11); key_expand(hkey,hrk,11);
    uint8_t hint[4][3];
    for(int d=0;d<4;d++) for(int t=0;t<3;t++)
        hint[d][t] = ((slotmask>>t)&1) ? hrk[rounds][DIAGP[d][t]] : rk[rounds][DIAGP[d][t]];
    static uint8_t cand[4][4][256][256]; memset(cand,1,sizeof cand);
    double t0=now(); uint64_t total=0;
    printf("{\"mode\":\"attack6n\",\"slotmask\":%d,\"false_slots\":[%s%s%s],\"rounds\":%d,\"target_key\":\"",
        slotmask,(slotmask&1)?"0":"",((slotmask&2)?((slotmask&1)?",1":"1"):""),
        ((slotmask&4)?((slotmask&3)?",2":"2"):""),rounds); phex(key,16);
    printf("\",\"hint_key\":\""); phex(hkey,16);
    printf("\",\"seed\":%u,\"nstruct\":%d,\"nthreads\":%d,\"hint_bytes_per_diagonal\":3,\"structures\":[",seed,nstruct,nthreads);
    for(int s=0;s<nstruct;s++){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        job6 J[8]; pthread_t th[8]; int step=256/nthreads;
        for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds;
            J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step;
            memcpy(J[t].hint,hint,sizeof hint); J[t].tab=malloc(4*4*1024*8); }
        double ts=now();
        for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker6,&J[t]);
        static uint64_t tab[4][4][1024]; memset(tab,0,sizeof tab); uint64_t n=0;
        for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
            for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int w=0;w<1024;w++) tab[d][r][w]^=J[t].tab[d][r][w];
            free(J[t].tab); }
        total+=n; double tfold=now()-ts; double tp=now();
        for(int d=0;d<4;d++) for(int r=0;r<4;r++){
            uint8_t a3=IMIX[r][3];
            for(int k3=0;k3<256;k3++){
                uint8_t hist[256]; memset(hist,0,256);
                for(unsigned idx=0;idx<65536;idx++){
                    if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
                    hist[(uint8_t)(idx>>8) ^ GM[a3][ISB[(idx&0xff)^k3]]] ^= 1;
                }
                for(int k4=0;k4<256;k4++){
                    if(!cand[d][r][k3][k4]) continue;
                    uint8_t sm=0; for(int v=0;v<256;v++) if(hist[v]) sm^=ISB[v^k4];
                    if(sm) cand[d][r][k3][k4]=0;
                }
            }
        }
        long long surv=0; for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int a=0;a<256;a++) for(int b=0;b<256;b++) surv+=cand[d][r][a][b];
        printf("%s{\"idx\":%d,\"base\":\"",s?",":"",s); phex(base,16);
        printf("\",\"texts\":%llu,\"fold_seconds\":%.2f,\"partialsum_seconds\":%.2f,\"surviving_(k3,k4)_pairs\":%lld}",
               (unsigned long long)n,tfold,now()-tp,surv); fflush(stdout);
    }
    printf("],\"chosen_plaintexts\":%llu,\"seconds\":%.2f",(unsigned long long)total,now()-t0);
    print_diag_report(cand,hint,rk[rounds],hrk[rounds],nwrong);
    printf("}\n");
    return 0;
}
static int mode_attack7n(int argc,char**argv){
    if(argc<9){ fprintf(stderr,"usage: sq_null attack7n <targetkey> <hintkey> <rounds> <nstruct> <seed> <nthreads> <nwrong>\n"); return 2; }
    uint8_t key[16], hkey[16]; hex2bin(argv[2],key,16); hex2bin(argv[3],hkey,16);
    int rounds=atoi(argv[4]); int nstruct=atoi(argv[5]); unsigned seed=(unsigned)strtoul(argv[6],0,10);
    int nthreads=atoi(argv[7]); int nwrong=atoi(argv[8]);
    build_gm(); ni_key_expand(key); srand(seed);
    uint8_t rk[12][16], hrk[12][16]; key_expand(key,rk,12); key_expand(hkey,hrk,12);
    uint8_t k6p[16], hk6p[16];
    for(int cc=0;cc<4;cc++) for(int rr=0;rr<4;rr++){
        k6p[4*cc+rr]=GM[IMIX[rr][0]][rk[rounds-1][4*cc+0]]^GM[IMIX[rr][1]][rk[rounds-1][4*cc+1]]
                    ^GM[IMIX[rr][2]][rk[rounds-1][4*cc+2]]^GM[IMIX[rr][3]][rk[rounds-1][4*cc+3]];
        hk6p[4*cc+rr]=GM[IMIX[rr][0]][hrk[rounds-1][4*cc+0]]^GM[IMIX[rr][1]][hrk[rounds-1][4*cc+1]]
                    ^GM[IMIX[rr][2]][hrk[rounds-1][4*cc+2]]^GM[IMIX[rr][3]][hrk[rounds-1][4*cc+3]];
    }
    uint8_t hint[4][3];
    for(int d=0;d<4;d++) for(int t=0;t<3;t++)
        hint[d][t] = (t<nwrong) ? hk6p[DIAGP[d][t]] : k6p[DIAGP[d][t]];
    static uint8_t cand[4][4][256][256]; memset(cand,1,sizeof cand);
    double t0=now(); uint64_t total=0;
    printf("{\"mode\":\"attack7n\",\"rounds\":%d,\"target_key\":\"",rounds); phex(key,16);
    printf("\",\"hint_key\":\""); phex(hkey,16);
    printf("\",\"seed\":%u,\"nstruct\":%d,\"nthreads\":%d,\"K7_given\":\"TRUE key's K%d\",\"structures\":[",seed,nstruct,nthreads,rounds);
    for(int s=0;s<nstruct;s++){
        uint8_t base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
        job7 J[8]; pthread_t th[8]; int step=256/nthreads;
        for(int t=0;t<nthreads;t++){ memcpy(J[t].base,base,16); J[t].rounds=rounds;
            J[t].b0lo=t*step; J[t].b0hi=(t==nthreads-1)?256:(t+1)*step;
            memcpy(J[t].k7,rk[rounds],16); memcpy(J[t].hint,hint,sizeof hint);
            J[t].tab=malloc(4*4*1024*8); }
        double ts=now();
        for(int t=0;t<nthreads;t++) pthread_create(&th[t],0,worker7,&J[t]);
        static uint64_t tab[4][4][1024]; memset(tab,0,sizeof tab); uint64_t n=0;
        for(int t=0;t<nthreads;t++){ pthread_join(th[t],0); n+=J[t].n;
            for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int w=0;w<1024;w++) tab[d][r][w]^=J[t].tab[d][r][w];
            free(J[t].tab); }
        total+=n; double tfold=now()-ts; double tp=now();
        for(int d=0;d<4;d++) for(int r=0;r<4;r++){
            uint8_t a3=IMIX[r][3];
            for(int k3=0;k3<256;k3++){
                uint8_t hist[256]; memset(hist,0,256);
                for(unsigned idx=0;idx<65536;idx++){
                    if(!((tab[d][r][idx>>6]>>(idx&63))&1)) continue;
                    hist[(uint8_t)(idx>>8) ^ GM[a3][ISB[(idx&0xff)^k3]]] ^= 1;
                }
                for(int k4=0;k4<256;k4++){
                    if(!cand[d][r][k3][k4]) continue;
                    uint8_t sm=0; for(int v=0;v<256;v++) if(hist[v]) sm^=ISB[v^k4];
                    if(sm) cand[d][r][k3][k4]=0;
                }
            }
        }
        long long surv=0; for(int d=0;d<4;d++) for(int r=0;r<4;r++) for(int a=0;a<256;a++) for(int b=0;b<256;b++) surv+=cand[d][r][a][b];
        printf("%s{\"idx\":%d,\"base\":\"",s?",":"",s); phex(base,16);
        printf("\",\"texts\":%llu,\"fold_seconds\":%.2f,\"tail_seconds\":%.2f,\"surviving_pairs\":%lld}",
               (unsigned long long)n,tfold,now()-tp,surv); fflush(stdout);
    }
    printf("],\"chosen_plaintexts\":%llu,\"seconds\":%.2f",(unsigned long long)total,now()-t0);
    print_diag_report(cand,hint,k6p,hk6p,nwrong);
    printf(",\"note\":\"NOT a key recovery: the true K%d was given as input\"}\n",rounds);
    return 0;
}

int main(int argc,char**argv){
    build_tables();
    if(argc<2){ fprintf(stderr,"usage: sq <mode> ...\n"); return 2; }
    if(!strcmp(argv[1],"selftest")) return mode_selftest(argc,argv);
    if(!strcmp(argv[1],"attack4"))  return mode_attack4(argc,argv);
    if(!strcmp(argv[1],"attack5"))  return mode_attack5(argc,argv);
    if(!strcmp(argv[1],"attack6"))  return mode_attack6(argc,argv);
    if(!strcmp(argv[1],"compare6")) return mode_compare6(argc,argv);
    if(!strcmp(argv[1],"attack7"))  return mode_attack7(argc,argv);
    if(!strcmp(argv[1],"targets"))  return mode_targets(argc,argv);
    if(!strcmp(argv[1],"attack6n")) return mode_attack6n(argc,argv);
    if(!strcmp(argv[1],"attack7n")) return mode_attack7n(argc,argv);
    fprintf(stderr,"unknown mode\n"); return 2;
}
