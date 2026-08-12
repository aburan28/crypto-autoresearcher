/* sq4.c -- MINI-AES-64: a 4-bit-cell AES-shaped analogue, its integral
 * distinguishers, and integral key recoveries at 5, 6 and 7 rounds.
 *
 * ANALOGY LIMIT (read this first): MINI-AES-64 is NOT AES-128. A result here
 * is evidence about the STRUCTURE of the attack at reduced scale. It is not a
 * statement about AES-128 at any round count.
 *
 * CIPHER
 *   field    GF(2^4), x^4 + x + 1 (0x13)
 *   state    4x4 cells of 4 bits, column-major s[4c+r], 64-bit block
 *   key      64 bits, AES-shaped schedule (RotWord/SubWord/Rcon)
 *   SubCells x -> A(x^-1) with x^-1 in GF(2^4) (0->0) and A a GF(2)-affine map
 *   ShiftRows row r rotated left by r (AES offsets)
 *   MixColumns circulant(02,03,01,01) over GF(2^4)  [MDS: verified]
 *   round r of R: SubCells, ShiftRows, MixColumns (omitted in round R), ARK
 *
 * INDEPENDENCE: this file derives every table from field arithmetic written
 * here. The certificate verifier (ref4.py) is a separate implementation that
 * shares no code with this file.
 *
 * Build: gcc -O3 -pthread -o sq4 sq4.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>

/* ------------------------- GF(2^4) ------------------------- */
static uint8_t gm4(uint8_t a, uint8_t b){
    uint8_t r=0; a&=0xf; b&=0xf;
    while(b){ if(b&1) r^=a; b>>=1; a<<=1; if(a&0x10) a^=0x13; }
    return r&0xf;
}
static uint8_t ginv4(uint8_t a){ if(!a) return 0; uint8_t r=1; for(int i=0;i<14;i++) r=gm4(r,a); return r; }
static uint8_t affine4(uint8_t b){
    uint8_t o=0;
    for(int i=0;i<4;i++){
        int bit = ((b>>i)&1) ^ ((b>>((i+1)&3))&1) ^ ((b>>((i+2)&3))&1) ^ ((0x6>>i)&1);
        o |= bit<<i;
    }
    return o;
}
static uint8_t SB[16], ISB[16], GM[16][16];
static const uint8_t MIX[4][4]  = {{2,3,1,1},{1,2,3,1},{1,1,2,3},{3,1,1,2}};
static const uint8_t IMIX[4][4] = {{0xe,0xb,0xd,0x9},{0x9,0xe,0xb,0xd},{0xd,0x9,0xe,0xb},{0xb,0xd,0x9,0xe}};

static uint16_t T[4][16];   /* SB+MC contribution of row rr to an output column */
static uint16_t TL[4][16];  /* last round: SB only */
static void build_tables(void){
    for(int x=0;x<16;x++) SB[x]=affine4(ginv4(x));
    for(int x=0;x<16;x++) ISB[SB[x]]=x;
    for(int a=0;a<16;a++) for(int x=0;x<16;x++) GM[a][x]=gm4(a,x);
    for(int rr=0;rr<4;rr++) for(int v=0;v<16;v++){
        uint16_t w=0; for(int i=0;i<4;i++) w |= (uint16_t)GM[MIX[i][rr]][SB[v]] << (4*i);
        T[rr][v]=w; TL[rr][v]=(uint16_t)SB[v]<<(4*rr);
    }
}

/* ------------------------- key schedule ------------------------- */
static uint8_t rcon4(int i){ uint8_t v=1; for(int j=1;j<i;j++) v=gm4(v,2); return v; }
static void key_expand(const uint8_t key[16], uint8_t rk[][16], int nrk){
    uint8_t w[4*16][4];
    for(int i=0;i<4;i++) for(int j=0;j<4;j++) w[i][j]=key[4*i+j];
    for(int i=4;i<4*nrk;i++){
        uint8_t t[4]; memcpy(t,w[i-1],4);
        if(i%4==0){ uint8_t tmp=t[0]; t[0]=SB[t[1]]; t[1]=SB[t[2]]; t[2]=SB[t[3]]; t[3]=SB[tmp]; t[0]^=rcon4(i/4); }
        for(int j=0;j<4;j++) w[i][j]=w[i-4][j]^t[j];
    }
    for(int r=0;r<nrk;r++) for(int i=0;i<4;i++) for(int j=0;j<4;j++) rk[r][4*i+j]=w[4*r+i][j];
}
/* given round key number r, recover the master key */
static void key_invert(const uint8_t rkr[16], int r, uint8_t master[16]){
    uint8_t w[4*16][4];
    for(int i=0;i<4;i++) for(int j=0;j<4;j++) w[4*r+i][j]=rkr[4*i+j];
    for(int i=4*r+3;i>=4;i--){
        uint8_t t[4]; memcpy(t,w[i-1],4);
        if(i%4==0){ uint8_t tmp=t[0]; t[0]=SB[t[1]]; t[1]=SB[t[2]]; t[2]=SB[t[3]]; t[3]=SB[tmp]; t[0]^=rcon4(i/4); }
        for(int j=0;j<4;j++) w[i-4][j]=w[i][j]^t[j];
    }
    for(int i=0;i<4;i++) for(int j=0;j<4;j++) master[4*i+j]=w[i][j];
}

/* ------------------------- state packing ------------------------- */
static inline uint64_t pack(const uint8_t c[16]){ uint64_t s=0; for(int i=0;i<16;i++) s|=(uint64_t)(c[i]&0xf)<<(4*i); return s; }
static inline void unpack(uint64_t s, uint8_t c[16]){ for(int i=0;i<16;i++) c[i]=(s>>(4*i))&0xf; }
static inline uint64_t rkpack(const uint8_t rk[16]){ return pack(rk); }

/* fast R-round encryption on packed states */
static inline uint64_t enc(uint64_t s, const uint64_t *rk, int R){
    s ^= rk[0];
    for(int r=1;r<R;r++){
        uint64_t o=0;
        for(int c=0;c<4;c++){
            uint16_t col = T[0][(s>>(4*(4*((c+0)&3)+0)))&0xf]
                         ^ T[1][(s>>(4*(4*((c+1)&3)+1)))&0xf]
                         ^ T[2][(s>>(4*(4*((c+2)&3)+2)))&0xf]
                         ^ T[3][(s>>(4*(4*((c+3)&3)+3)))&0xf];
            o |= (uint64_t)col << (16*c);
        }
        s = o ^ rk[r];
    }
    uint64_t o=0;
    for(int c=0;c<4;c++){
        uint16_t col = TL[0][(s>>(4*(4*((c+0)&3)+0)))&0xf]
                     ^ TL[1][(s>>(4*(4*((c+1)&3)+1)))&0xf]
                     ^ TL[2][(s>>(4*(4*((c+2)&3)+2)))&0xf]
                     ^ TL[3][(s>>(4*(4*((c+3)&3)+3)))&0xf];
        o |= (uint64_t)col << (16*c);
    }
    return o ^ rk[R];
}
/* straightforward (slow) reference encryption/decryption on cell arrays */
static void ref_enc(const uint8_t pt[16], uint8_t rk[][16], int R, uint8_t out[16]){
    uint8_t s[16],t[16];
    for(int i=0;i<16;i++) s[i]=pt[i]^rk[0][i];
    for(int r=1;r<=R;r++){
        for(int i=0;i<16;i++) t[i]=SB[s[i]];
        for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++) s[4*c+rr]=t[4*((c+rr)&3)+rr];
        if(r!=R){ memcpy(t,s,16);
            for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++){ uint8_t a=0;
                for(int k=0;k<4;k++) a^=GM[MIX[rr][k]][t[4*c+k]]; s[4*c+rr]=a; } }
        for(int i=0;i<16;i++) s[i]^=rk[r][i];
    }
    memcpy(out,s,16);
}
static void ref_dec(const uint8_t ct[16], uint8_t rk[][16], int R, uint8_t out[16]){
    uint8_t s[16],t[16]; memcpy(s,ct,16);
    for(int r=R;r>=1;r--){
        for(int i=0;i<16;i++) s[i]^=rk[r][i];
        if(r!=R){ memcpy(t,s,16);
            for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++){ uint8_t a=0;
                for(int k=0;k<4;k++) a^=GM[IMIX[rr][k]][t[4*c+k]]; s[4*c+rr]=a; } }
        memcpy(t,s,16);
        for(int c=0;c<4;c++) for(int rr=0;rr<4;rr++) s[4*((c+rr)&3)+rr]=t[4*c+rr];
        for(int i=0;i<16;i++) s[i]=ISB[s[i]];
    }
    for(int i=0;i<16;i++) s[i]^=rk[0][i];
    memcpy(out,s,16);
}

/* ------------------------- utilities ------------------------- */
static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+1e-9*ts.tv_nsec; }
static void hex2cells(const char*h, uint8_t c[16]){ for(int i=0;i<16;i++){ char b[2]={h[i],0}; c[i]=(uint8_t)strtoul(b,0,16);} }
static void pcells(const uint8_t c[16]){ for(int i=0;i<16;i++) printf("%x",c[i]&0xf); }
static uint64_t rng_s;
static uint64_t rnd64(void){ uint64_t x=rng_s; x^=x<<13; x^=x>>7; x^=x<<17; rng_s=x; return x; }

/* MIX64: a keyed 64-bit bijection with no SPN structure (sibling PRP control) */
static inline uint64_t mix64(uint64_t x, uint64_t k){
    for(int i=0;i<4;i++){
        x ^= k + 0x9e3779b97f4a7c15ULL*(i+1);
        x ^= x>>30; x *= 0xbf58476d1ce4e5b9ULL;
        x ^= x>>27; x *= 0x94d049bb133111ebULL;
        x ^= x>>31;
    }
    return x;
}

/* diagonals: plaintext cells feeding output column 0 and 1 of ShiftRows */
static const int DIAG0[4]={0,5,10,15};
static const int DIAG1[4]={4,9,14,3};
/* DIAGP[cc][t] = ciphertext cell needed for column cc of the previous state */
static int DIAGP[4][4];
static void build_diagp(void){ for(int cc=0;cc<4;cc++) for(int t=0;t<4;t++) DIAGP[cc][t]=4*(((cc-t)%4+4)%4)+t; }

/* =====================================================================
 * MODE selftest / pin
 * ===================================================================== */
static int mode_selftest(int argc,char**argv){
    uint8_t key[16],pt[16]; hex2cells(argv[2],key); hex2cells(argv[3],pt);
    uint8_t rk[16][16]; key_expand(key,rk,16);
    uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
    printf("{\"key\":\""); pcells(key); printf("\",\"pt\":\""); pcells(pt); printf("\",\"rounds\":{");
    for(int R=1;R<=8;R++){
        uint8_t o1[16],o2[16],back[16];
        ref_enc(pt,rk,R,o1);
        unpack(enc(pack(pt),rkp,R),o2);
        ref_dec(o1,rk,R,back);
        printf("%s\"%d\":{\"ref\":\"",R>1?",":"",R); pcells(o1);
        printf("\",\"fast\":\""); pcells(o2);
        printf("\",\"agree\":%d,\"roundtrip\":%d}", memcmp(o1,o2,16)==0, memcmp(back,pt,16)==0);
    }
    printf("}}\n"); return 0;
}

static int mode_pin(int argc,char**argv){
    unsigned long seed=strtoul(argv[2],0,10); rng_s=seed?seed:1;
    /* S-box properties */
    int seen[16]; memset(seen,0,sizeof seen); int bij=1;
    for(int x=0;x<16;x++){ if(seen[SB[x]]) bij=0; seen[SB[x]]=1; }
    int ddt_max=0, fixed=0;
    for(int a=1;a<16;a++){ int cnt[16]; memset(cnt,0,sizeof cnt);
        for(int x=0;x<16;x++) cnt[SB[x]^SB[x^a]]++;
        for(int b=0;b<16;b++) if(cnt[b]>ddt_max) ddt_max=cnt[b]; }
    int lat_max=0;
    for(int a=1;a<16;a++) for(int b=1;b<16;b++){ int s=0;
        for(int x=0;x<16;x++){ int p=__builtin_popcount(a&x)^__builtin_popcount(b&SB[x]); s+= (p&1)?-1:1; }
        if(abs(s)>lat_max) lat_max=abs(s); }
    for(int x=0;x<16;x++) if(SB[x]==x) fixed++;
    /* MDS re-check of MIX and IMIX by brute force determinant over GF(2^4) */
    int mds_ok=1, sing=0;
    for(int mask_r=1;mask_r<16;mask_r++) for(int mask_c=1;mask_c<16;mask_c++){
        if(__builtin_popcount(mask_r)!=__builtin_popcount(mask_c)) continue;
        int rs[4],cs[4],n=0,m=0;
        for(int i=0;i<4;i++){ if(mask_r>>i&1) rs[n++]=i; if(mask_c>>i&1) cs[m++]=i; }
        uint8_t A[4][4]; for(int i=0;i<n;i++) for(int j=0;j<n;j++) A[i][j]=MIX[rs[i]][cs[j]];
        uint8_t d=1; int singular=0;
        for(int c=0;c<n;c++){ int p=-1; for(int r=c;r<n;r++) if(A[r][c]){p=r;break;}
            if(p<0){ singular=1; break; }
            if(p!=c) for(int k=0;k<n;k++){ uint8_t tmp=A[c][k]; A[c][k]=A[p][k]; A[p][k]=tmp; }
            d=gm4(d,A[c][c]); uint8_t ic=ginv4(A[c][c]);
            for(int r=c+1;r<n;r++) if(A[r][c]){ uint8_t f=gm4(A[r][c],ic);
                for(int k=c;k<n;k++) A[r][k]^=gm4(f,A[c][k]); } }
        if(singular||d==0){ mds_ok=0; sing++; }
    }
    /* MIX * IMIX == I ? */
    int inv_ok=1;
    for(int i=0;i<4;i++) for(int j=0;j<4;j++){ uint8_t a=0;
        for(int k=0;k<4;k++) a^=gm4(MIX[i][k],IMIX[k][j]);
        if(a != (i==j)) inv_ok=0; }
    /* round trip on many random keys, all round counts 1..8 */
    int trials=atoi(argv[3]); int rt_ok=1, fast_ok=1;
    for(int t=0;t<trials;t++){
        uint8_t key[16],pt[16]; uint64_t a=rnd64(),b=rnd64();
        for(int i=0;i<16;i++){ key[i]=(a>>(4*i))&0xf; pt[i]=(b>>(4*i))&0xf; }
        uint8_t rk[16][16]; key_expand(key,rk,16);
        uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
        for(int R=1;R<=8;R++){
            uint8_t ct[16],back[16],ct2[16];
            ref_enc(pt,rk,R,ct); ref_dec(ct,rk,R,back);
            unpack(enc(pack(pt),rkp,R),ct2);
            if(memcmp(back,pt,16)) rt_ok=0;
            if(memcmp(ct,ct2,16)) fast_ok=0;
        }
    }
    /* avalanche: single input-bit flip, mean output bit differences per round */
    int av_trials=2000; double av[9]; int minb[9],maxb[9];
    for(int R=1;R<=8;R++){ long long sum=0; minb[R]=64; maxb[R]=0;
        for(int t=0;t<av_trials;t++){
            uint8_t key[16],pt[16]; uint64_t a=rnd64(),b=rnd64();
            for(int i=0;i<16;i++){ key[i]=(a>>(4*i))&0xf; pt[i]=(b>>(4*i))&0xf; }
            uint8_t rk[16][16]; key_expand(key,rk,16);
            uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
            int bit = rnd64()%64;
            uint64_t p0=pack(pt), p1=p0^(1ULL<<bit);
            uint64_t d = enc(p0,rkp,R)^enc(p1,rkp,R);
            int pc=__builtin_popcountll(d); sum+=pc;
            if(pc<minb[R]) minb[R]=pc; if(pc>maxb[R]) maxb[R]=pc;
        }
        av[R]=(double)sum/av_trials;
    }
    /* active-cell diffusion: how many cells differ after R rounds for a 1-cell diff */
    double ac[9];
    for(int R=1;R<=8;R++){ long long sum=0;
        for(int t=0;t<500;t++){
            uint8_t key[16],pt[16]; uint64_t a=rnd64(),b=rnd64();
            for(int i=0;i<16;i++){ key[i]=(a>>(4*i))&0xf; pt[i]=(b>>(4*i))&0xf; }
            uint8_t rk[16][16]; key_expand(key,rk,16);
            uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
            int cell=rnd64()%16; uint8_t dv=1+rnd64()%15;
            uint64_t p0=pack(pt), p1=p0^((uint64_t)dv<<(4*cell));
            uint64_t d=enc(p0,rkp,R)^enc(p1,rkp,R);
            int n=0; for(int i=0;i<16;i++) if((d>>(4*i))&0xf) n++;
            sum+=n;
        }
        ac[R]=(double)sum/500;
    }
    printf("{\"sbox\":{\"table\":[");
    for(int x=0;x<16;x++) printf("%s%d",x?",":"",SB[x]);
    printf("],\"bijective\":%d,\"ddt_max\":%d,\"lat_max_abs\":%d,\"fixed_points\":%d,\"differential_uniformity\":%d,\"max_dp\":%.4f,\"max_lin_bias\":%.4f},",
        bij,ddt_max,lat_max,fixed,ddt_max,ddt_max/16.0,lat_max/32.0);
    printf("\"mixcolumns\":{\"row\":\"02,03,01,01\",\"field\":\"GF(2^4) x^4+x+1\",\"MDS_all_square_submatrices_nonsingular\":%d,\"singular_submatrices\":%d,\"inverse_row\":\"0e,0b,0d,09\",\"MIX_times_IMIX_is_identity\":%d,\"zero_coeff_in_inverse\":0},",
        mds_ok,sing,inv_ok);
    printf("\"roundtrip_ok\":%d,\"fast_vs_ref_ok\":%d,\"trials\":%d,",rt_ok,fast_ok,trials);
    printf("\"avalanche_mean_output_bits_flipped_of_64\":{");
    for(int R=1;R<=8;R++) printf("%s\"%d\":%.2f",R>1?",":"",R,av[R]);
    printf("},\"avalanche_min_max\":{");
    for(int R=1;R<=8;R++) printf("%s\"%d\":[%d,%d]",R>1?",":"",R,minb[R],maxb[R]);
    printf("},\"active_cells_after_1cell_diff_of_16\":{");
    for(int R=1;R<=8;R++) printf("%s\"%d\":%.2f",R>1?",":"",R,ac[R]);
    printf("}}\n");
    return 0;
}

/* =====================================================================
 * MODE dist : integral distinguisher + controls
 *   argv: dist <nactive> <maxround> <trials> <seed> <cipher>
 *   nactive = number of active plaintext cells taken from DIAG0 then DIAG1
 *   cipher: "mini" = R-round MINI-AES-64, "prp" = MIX64 keyed bijection,
 *           "spn12" = MINI-AES-64 driven to 12 rounds (matched structural control)
 * ===================================================================== */
typedef struct { int na, R; long long lo, hi; const int*act; uint64_t basep; uint64_t rkp[16]; int cipher; uint64_t ck; uint64_t x; } jobd;
static void* workd(void*arg){
    jobd*J=(jobd*)arg; uint64_t x=0;
    for(long long i=J->lo;i<J->hi;i++){
        uint64_t p=J->basep;
        for(int t=0;t<J->na;t++){ uint64_t v=(i>>(4*t))&0xf; p &= ~((uint64_t)0xf<<(4*J->act[t])); p |= v<<(4*J->act[t]); }
        uint64_t c;
        if(J->cipher==0) c=enc(p,J->rkp,J->R);
        else if(J->cipher==1) c=mix64(p,J->ck);
        else c=enc(p,J->rkp,12);
        x^=c;
    }
    J->x=x; return 0;
}
static uint64_t sweep_xor(const int*act,int na,uint64_t basep,uint64_t*rkp,int R,int cipher,uint64_t ck,int nthr){
    long long N=1LL<<(4*na); jobd J[8]; pthread_t th[8];
    if(nthr>8) nthr=8;
    for(int t=0;t<nthr;t++){ J[t].na=na;J[t].R=R;J[t].act=act;J[t].basep=basep;J[t].cipher=cipher;J[t].ck=ck;
        memcpy(J[t].rkp,rkp,sizeof(uint64_t)*16);
        J[t].lo=(long long)(N/nthr)*t; J[t].hi=(t==nthr-1)?N:(long long)(N/nthr)*(t+1); }
    for(int t=0;t<nthr;t++) pthread_create(&th[t],0,workd,&J[t]);
    uint64_t x=0; for(int t=0;t<nthr;t++){ pthread_join(th[t],0); x^=J[t].x; }
    return x;
}
static int mode_dist(int argc,char**argv){
    int na=atoi(argv[2]), maxR=atoi(argv[3]), trials=atoi(argv[4]);
    rng_s=strtoul(argv[5],0,10); if(!rng_s) rng_s=1;
    const char*ciph=argv[6]; int nthr=argc>7?atoi(argv[7]):4;
    int cipher = !strcmp(ciph,"mini")?0 : (!strcmp(ciph,"prp")?1:2);
    int minR = argc>8?atoi(argv[8]):1;
    int act[8]; for(int t=0;t<4;t++){ act[t]=DIAG0[t]; act[4+t]=DIAG1[t]; }
    printf("{\"cipher\":\"%s\",\"active_cells\":%d,\"texts_per_set\":%.0f,\"trials\":%d,\"levels\":[",ciph,na,(double)(1LL<<(4*na)),trials);
    double t0=now();
    for(int R=minR;R<=maxR;R++){
        int allbal=0; long long cellbal=0; long long celltot=0;
        for(int t=0;t<trials;t++){
            uint8_t key[16]; uint64_t a=rnd64(); for(int i=0;i<16;i++) key[i]=(a>>(4*i))&0xf;
            uint8_t rk[16][16]; key_expand(key,rk,16);
            uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
            uint64_t basep=rnd64(); uint64_t ck=rnd64();
            uint64_t x=sweep_xor(act,na,basep,rkp,R,cipher,ck,nthr);
            if(x==0) allbal++;
            for(int i=0;i<16;i++){ celltot++; if(((x>>(4*i))&0xf)==0) cellbal++; }
        }
        printf("%s{\"rounds\":%d,\"all16_balanced\":%d,\"of\":%d,\"balanced_cells\":%lld,\"of_cells\":%lld,\"cell_rate\":%.4f}",
               R>minR?",":"",R,allbal,trials,cellbal,celltot,(double)cellbal/celltot);
        fflush(stdout);
    }
    printf("],\"seconds\":%.2f}\n",now()-t0);
    return 0;
}

/* =====================================================================
 * ORACLE.  The key lives here only.  Attack routines below receive
 * ciphertext parity tables, never the key.
 * ===================================================================== */
static uint64_t ORACLE_RK[16];
static int ORACLE_R;
static long long ORACLE_QUERIES=0;
static void oracle_init(const uint8_t key[16], int R){
    uint8_t rk[16][16]; key_expand(key,rk,16);
    for(int i=0;i<16;i++) ORACLE_RK[i]=rkpack(rk[i]);
    ORACLE_R=R;
}

/* =====================================================================
 * MODE attack5 : 5 rounds, balance at level 4 from the 2^16 one-diagonal set,
 * one round peeled, 16 candidates per cell of K5.  Unrestricted key space.
 * ===================================================================== */
typedef struct { int lo,hi; uint64_t basep; uint8_t par[16][16]; long long n; } job5;
static void* work5(void*arg){
    job5*J=(job5*)arg; memset(J->par,0,sizeof J->par); long long n=0;
    for(int i=J->lo;i<J->hi;i++){
        uint64_t p=J->basep;
        for(int t=0;t<4;t++){ uint64_t v=(i>>(4*t))&0xf; p&=~((uint64_t)0xf<<(4*DIAG0[t])); p|=v<<(4*DIAG0[t]); }
        uint64_t c=enc(p,ORACLE_RK,ORACLE_R);
        for(int k=0;k<16;k++) J->par[k][(c>>(4*k))&0xf]^=1;
        n++;
    }
    J->n=n; return 0;
}
static int mode_attack5(int argc,char**argv){
    uint8_t key[16]; hex2cells(argv[2],key);
    int R=atoi(argv[3]); int maxstruct=atoi(argv[4]); rng_s=strtoul(argv[5],0,10); if(!rng_s) rng_s=1;
    int nthr=argc>6?atoi(argv[6]):4;
    oracle_init(key,R);
    uint16_t cand[16]; for(int i=0;i<16;i++) cand[i]=0xffff;
    long long texts=0, tests=0; double t0=now(); int ns=0;
    printf("{\"cipher\":\"MINI-AES-64\",\"rounds\":%d,\"key_space\":\"full unrestricted 2^64\",\"structures\":[",R);
    int done=0;
    while(!done && ns<maxstruct){
        uint64_t basep=rnd64();
        job5 J[8]; pthread_t th[8]; int N=1<<16;
        for(int t=0;t<nthr;t++){ J[t].basep=basep; J[t].lo=(N/nthr)*t; J[t].hi=(t==nthr-1)?N:(N/nthr)*(t+1); }
        double ts=now();
        for(int t=0;t<nthr;t++) pthread_create(&th[t],0,work5,&J[t]);
        uint8_t par[16][16]; memset(par,0,sizeof par);
        for(int t=0;t<nthr;t++){ pthread_join(th[t],0); texts+=J[t].n;
            for(int i=0;i<16;i++) for(int v=0;v<16;v++) par[i][v]^=J[t].par[i][v]; }
        for(int i=0;i<16;i++) for(int k=0;k<16;k++){
            if(!((cand[i]>>k)&1)) continue;
            uint8_t s=0; for(int v=0;v<16;v++) if(par[i][v]) s^=ISB[v^k];
            tests+=16; if(s) cand[i]&=~(1u<<k);
        }
        ns++;
        done=1; for(int i=0;i<16;i++) if(__builtin_popcount(cand[i])!=1) done=0;
        printf("%s{\"idx\":%d,\"texts\":%d,\"seconds\":%.3f,\"survivors\":[",ns>1?",":"",ns-1,N,now()-ts);
        for(int i=0;i<16;i++) printf("%s%d",i?",":"",__builtin_popcount(cand[i]));
        printf("]}"); fflush(stdout);
    }
    uint8_t rkR[16]; int uniq=1;
    for(int i=0;i<16;i++){ if(__builtin_popcount(cand[i])!=1) uniq=0; rkR[i]=__builtin_ctz(cand[i]?cand[i]:1); }
    uint8_t master[16]; key_invert(rkR,R,master);
    printf("],\"structures_used\":%d,\"chosen_plaintexts\":%lld,\"candidate_tests\":%lld,\"seconds\":%.3f,\"unique\":%d,\"rk_last\":\"",
        ns,texts,tests,now()-t0,uniq); pcells(rkR);
    printf("\",\"recovered_master\":\""); pcells(master); printf("\"}\n");
    return 0;
}

/* =====================================================================
 * TWO-ROUND BOTTOM EXTENSION (shared by attack6 and attack7)
 *
 *  balance level L = R-2.  For column cc of state X_{R-1} and row r:
 *     u_t = ISB[ C[DIAGP[cc][t]] ^ KR[DIAGP[cc][t]] ],  t=0..3
 *     y   = XOR_t IMIX[r][t] * u_t
 *     X_{R-2}[...] = ISB[ y ^ Kprime[4cc+r] ]
 *  and XOR over the structure of X_{R-2}[...] must be 0.
 *  Unknowns per (cc,r): 4 cells of KR (2^16) plus 1 cell of Kprime (2^4).
 *  Partial sums fold the four KR cells one at a time.
 * ===================================================================== */
typedef struct { int na; const int*act; long long lo,hi; uint64_t basep; uint8_t (*P)[65536]; long long n; } jobf;
static void* workf(void*arg){
    jobf*J=(jobf*)arg; memset(J->P,0,4*65536); long long n=0;
    for(long long i=J->lo;i<J->hi;i++){
        uint64_t p=J->basep;
        for(int t=0;t<J->na;t++){ uint64_t v=(i>>(4*t))&0xf; p&=~((uint64_t)0xf<<(4*J->act[t])); p|=v<<(4*J->act[t]); }
        uint64_t c=enc(p,ORACLE_RK,ORACLE_R);
        for(int d=0;d<4;d++){
            unsigned idx = (unsigned)((c>>(4*DIAGP[d][0]))&0xf)
                         | (unsigned)((c>>(4*DIAGP[d][1]))&0xf)<<4
                         | (unsigned)((c>>(4*DIAGP[d][2]))&0xf)<<8
                         | (unsigned)((c>>(4*DIAGP[d][3]))&0xf)<<12;
            J->P[d][idx]^=1;
        }
        n++;
    }
    J->n=n; return 0;
}
/* candidate masks: cand[d][r][k0..k3 packed] = bitmask over kprime */
static uint16_t (*CAND)[4][65536];
static long long FOLD_OPS, PS_OPS;
static void partial_sums(uint8_t P[4][65536]){
    static uint8_t T1[65536], T2[4096], T3[256];
    for(int d=0;d<4;d++) for(int r=0;r<4;r++){
        uint8_t a0=IMIX[r][0],a1=IMIX[r][1],a2=IMIX[r][2],a3=IMIX[r][3];
        for(int k0=0;k0<16;k0++){
            memset(T1,0,65536);
            for(unsigned idx=0;idx<65536;idx++){ if(!P[d][idx]) continue;
                unsigned z=GM[a0][ISB[(idx&0xf)^k0]];
                T1[(idx&0xfff0)|z]^=1; }
            PS_OPS+=65536;
            for(int k1=0;k1<16;k1++){
                memset(T2,0,4096);
                for(unsigned idx=0;idx<65536;idx++){ if(!T1[idx]) continue;
                    unsigned z=(idx&0xf)^GM[a1][ISB[((idx>>4)&0xf)^k1]];
                    T2[((idx>>8)<<4)|z]^=1; }
                PS_OPS+=65536;
                for(int k2=0;k2<16;k2++){
                    memset(T3,0,256);
                    for(unsigned idx=0;idx<4096;idx++){ if(!T2[idx]) continue;
                        unsigned z=(idx&0xf)^GM[a2][ISB[((idx>>4)&0xf)^k2]];
                        T3[((idx>>8)<<4)|z]^=1; }
                    PS_OPS+=4096;
                    for(int k3=0;k3<16;k3++){
                        unsigned kk=k0|(k1<<4)|(k2<<8)|(k3<<12);
                        uint16_t m=CAND[d][r][kk]; if(!m) continue;
                        uint8_t h[16]; memset(h,0,16);
                        for(unsigned idx=0;idx<256;idx++){ if(!T3[idx]) continue;
                            h[(idx&0xf)^GM[a3][ISB[((idx>>4)&0xf)^k3]]]^=1; }
                        PS_OPS+=256;
                        for(int kp=0;kp<16;kp++){
                            if(!((m>>kp)&1)) continue;
                            uint8_t s=0; for(int v=0;v<16;v++) if(h[v]) s^=ISB[v^kp];
                            PS_OPS+=16;
                            if(s) m&=~(1u<<kp);
                        }
                        CAND[d][r][kk]=m;
                    }
                }
            }
        }
    }
}
static int mode_attack_ext(int argc,char**argv,int R,int na){
    uint8_t key[16]; hex2cells(argv[2],key);
    int maxstruct=atoi(argv[3]); rng_s=strtoul(argv[4],0,10); if(!rng_s) rng_s=1;
    int nthr=argc>5?atoi(argv[5]):4;
    build_diagp(); oracle_init(key,R);
    int act[8]; for(int t=0;t<4;t++){ act[t]=DIAG0[t]; act[4+t]=DIAG1[t]; }
    CAND=malloc(sizeof(uint16_t)*4*4*65536);
    for(size_t i=0;i<(size_t)4*4*65536;i++) ((uint16_t*)CAND)[i]=0xffff;
    long long texts=0; double t0=now(); int ns=0; int done=0;
    printf("{\"cipher\":\"MINI-AES-64\",\"rounds\":%d,\"balance_level\":%d,\"active_plaintext_cells\":%d,"
           "\"texts_per_structure\":%.0f,\"key_space\":\"full unrestricted 2^64, no hint bytes\",\"structures\":[",
           R,R-2,na,(double)(1LL<<(4*na)));
    while(!done && ns<maxstruct){
        uint64_t basep=rnd64();
        long long N=1LL<<(4*na);
        jobf J[8]; pthread_t th[8];
        static uint8_t P[4][65536];
        memset(P,0,sizeof P);
        double ts=now();
        for(int t=0;t<nthr;t++){ J[t].na=na;J[t].act=act;J[t].basep=basep;
            J[t].lo=(N/nthr)*t; J[t].hi=(t==nthr-1)?N:(N/nthr)*(t+1);
            J[t].P=malloc(4*65536); }
        for(int t=0;t<nthr;t++) pthread_create(&th[t],0,workf,&J[t]);
        for(int t=0;t<nthr;t++){ pthread_join(th[t],0); texts+=J[t].n;
            for(int d=0;d<4;d++) for(unsigned i=0;i<65536;i++) P[d][i]^=J[t].P[d][i];
            free(J[t].P); }
        FOLD_OPS += N*4;
        double tf=now()-ts; double tp=now();
        partial_sums(P);
        double tps=now()-tp;
        long long surv=0; int uniqd=0;
        for(int d=0;d<4;d++){ long long c=0;
            for(unsigned kk=0;kk<65536;kk++){ int ok=1;
                for(int r=0;r<4;r++) if(!CAND[d][r][kk]) ok=0;
                if(ok) c++; }
            surv+=c; if(c==1) uniqd++; }
        ns++;
        done = (uniqd==4);
        printf("%s{\"idx\":%d,\"texts\":%lld,\"fold_seconds\":%.2f,\"partialsum_seconds\":%.2f,"
               "\"surviving_KR_diagonal_quads\":%lld,\"diagonals_unique\":%d}",ns>1?",":"",ns-1,N,tf,tps,surv,uniqd);
        fflush(stdout);
    }
    uint8_t rkR[16]; int uniq=1;
    for(int d=0;d<4;d++){ long long c=0; unsigned found=0;
        for(unsigned kk=0;kk<65536;kk++){ int ok=1;
            for(int r=0;r<4;r++) if(!CAND[d][r][kk]) ok=0;
            if(ok){ if(!c) found=kk; c++; } }
        if(c!=1) uniq=0;
        for(int t=0;t<4;t++) rkR[DIAGP[d][t]]=(found>>(4*t))&0xf;
    }
    uint8_t master[16]; key_invert(rkR,R,master);
    printf("],\"structures_used\":%d,\"chosen_plaintexts\":%lld,\"fold_ops\":%lld,\"partialsum_ops\":%lld,"
           "\"seconds\":%.2f,\"unique\":%d,\"rk_last\":\"",ns,texts,FOLD_OPS,PS_OPS,now()-t0,uniq);
    pcells(rkR); printf("\",\"recovered_master\":\""); pcells(master); printf("\"}\n");
    return 0;
}

/* =====================================================================
 * MODE targets : plaintext/ciphertext pairs from the oracle, for the
 * independent certificate verifier.
 * ===================================================================== */
static int mode_targets(int argc,char**argv){
    uint8_t key[16]; hex2cells(argv[2],key);
    int R=atoi(argv[3]); int n=atoi(argv[4]); rng_s=strtoul(argv[5],0,10); if(!rng_s) rng_s=1;
    oracle_init(key,R);
    printf("{\"cipher\":\"MINI-AES-64\",\"rounds\":%d,\"pairs\":[",R);
    for(int i=0;i<n;i++){
        uint64_t p=rnd64(); uint64_t c=enc(p,ORACLE_RK,R);
        uint8_t pc[16],cc[16]; unpack(p,pc); unpack(c,cc);
        printf("%s[\"",i?",":""); pcells(pc); printf("\",\""); pcells(cc); printf("\"]");
    }
    printf("]}\n"); return 0;
}

/* MODE bench : measured encryption throughput */
static int mode_bench(int argc,char**argv){
    int R=atoi(argv[2]); long long N=atoll(argv[3]);
    uint8_t key[16]; for(int i=0;i<16;i++) key[i]=i&0xf;
    uint8_t rk[16][16]; key_expand(key,rk,16);
    uint64_t rkp[16]; for(int i=0;i<16;i++) rkp[i]=rkpack(rk[i]);
    uint64_t x=0x0123456789abcdefULL, acc=0; double t0=now();
    for(long long i=0;i<N;i++){ acc^=enc(x^i,rkp,R); }
    double dt=now()-t0;
    printf("{\"rounds\":%d,\"encryptions\":%lld,\"seconds\":%.3f,\"enc_per_sec_1core\":%.3e,\"sink\":\"%llx\"}\n",
        R,N,dt,N/dt,(unsigned long long)acc);
    return 0;
}

int main(int argc,char**argv){
    build_tables(); build_diagp();
    if(argc<2){ fprintf(stderr,"usage: sq4 <mode> ...\n"); return 2; }
    if(!strcmp(argv[1],"selftest")) return mode_selftest(argc,argv);
    if(!strcmp(argv[1],"pin"))      return mode_pin(argc,argv);
    if(!strcmp(argv[1],"dist"))     return mode_dist(argc,argv);
    if(!strcmp(argv[1],"attack5"))  return mode_attack5(argc,argv);
    if(!strcmp(argv[1],"attack6"))  return mode_attack_ext(argc,argv,6,argc>6?atoi(argv[6]):4);
    if(!strcmp(argv[1],"attack7"))  return mode_attack_ext(argc,argv,7,argc>6?atoi(argv[6]):7);
    if(!strcmp(argv[1],"targets"))  return mode_targets(argc,argv);
    if(!strcmp(argv[1],"bench"))    return mode_bench(argc,argv);
    fprintf(stderr,"unknown mode\n"); return 2;
}
