/* gate.c -- GATE-RR78-1 pair-count engine.
 *
 * NO RNG INSIDE. Every key, coset base, matrix and plaintext-stream key is
 * supplied by the Python driver from a recorded master seed.
 *
 * Reads config lines on stdin, writes one JSON object per line on stdout.
 * Config line (whitespace separated):
 *   id r finalmc nbits j0 mode base_hex free_csv rk_hex invmat_hex ptrk_hex
 * mode: coset | randpt | constcoset
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <time.h>
#include <wmmintrin.h>
#include <emmintrin.h>

#define NTHREADS 4
static uint8_t *cnt = NULL;              /* 2^32 uint8 counters, 4 GB */
static uint32_t *vals = NULL;            /* touched pi values, small-N path */

/* ---- GF(2^8) with AES modulus, derived not transcribed ---- */
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; b>>=1; if(a&0x80) a=(uint8_t)((a<<1)^0x1b); else a<<=1; }
    return r;
}

typedef struct {
    int r, finalmc, j0, mode;
    uint64_t n_texts;
    int nbits;
    __m128i rk[16];
    __m128i ptrk[11];
    uint8_t base[16];
    int freeb[4];
    uint8_t gt[4][4][256];   /* gt[row][k][x] = invmat[row][k] * x */
    int srcbyte[4][4];       /* srcbyte[row][k] = 4*((j0-row)&3)+k */
} cfg_t;

typedef struct {
    const cfg_t *c; uint64_t lo, hi;
    int overflow; int const_seen; uint32_t const_val; int const_init;
    uint64_t local_touch_base;
} job_t;

static inline __m128i encrypt(__m128i s, const cfg_t *c){
    s = _mm_xor_si128(s, c->rk[0]);
    if (c->finalmc) { for (int i=1;i<=c->r;i++) s=_mm_aesenc_si128(s,c->rk[i]); }
    else { for (int i=1;i<c->r;i++) s=_mm_aesenc_si128(s,c->rk[i]);
           if (c->r>=1) s=_mm_aesenclast_si128(s,c->rk[c->r]); }
    return s;
}
static inline __m128i ptstream(uint64_t i, const cfg_t *c){
    uint8_t b[16]; memset(b,0,16); memcpy(b,&i,8);
    __m128i s = _mm_loadu_si128((const __m128i*)b);
    s = _mm_xor_si128(s, c->ptrk[0]);
    for (int k=1;k<10;k++) s=_mm_aesenc_si128(s,c->ptrk[k]);
    return _mm_aesenclast_si128(s,c->ptrk[10]);
}
static inline uint32_t project(const uint8_t *ct, const cfg_t *c){
    uint32_t p=0;
    for (int row=0; row<4; row++){
        uint8_t v=0;
        for (int k=0;k<4;k++) v ^= c->gt[row][k][ ct[ c->srcbyte[row][k] ] ];
        p |= ((uint32_t)v) << (8*row);
    }
    return p;
}

static void *worker(void *arg){
    job_t *J = (job_t*)arg; const cfg_t *c = J->c;
    uint8_t buf[16*8];
    for (uint64_t i=J->lo; i<J->hi; i+=8){
        __m128i s[8]; int nb = (J->hi-i < 8) ? (int)(J->hi-i) : 8;
        for (int t=0;t<nb;t++){
            uint64_t idx=i+t;
            if (c->mode==1){ s[t]=ptstream(idx,c); }
            else {
                uint8_t p[16]; memcpy(p,c->base,16);
                for (int f=0; f<c->nbits/8; f++) p[c->freeb[f]] = (uint8_t)((idx>>(8*f))&0xff);
                s[t]=_mm_loadu_si128((const __m128i*)p);
            }
        }
        for (int t=0;t<nb;t++) s[t]=encrypt(s[t],c);
        for (int t=0;t<nb;t++) _mm_storeu_si128((__m128i*)(buf+16*t), s[t]);
        for (int t=0;t<nb;t++){
            uint32_t p = project(buf+16*t, c);
            if (!J->const_init){ J->const_init=1; J->const_val=p; J->const_seen=1; }
            else if (J->const_seen && p!=J->const_val) J->const_seen=0;
            if (c->mode==2) continue;              /* constant-check only */
            uint8_t old = __atomic_fetch_add(&cnt[p], 1, __ATOMIC_RELAXED);
            if (old==255) J->overflow=1;
            if (vals) vals[i+t] = p;
        }
    }
    return NULL;
}

typedef struct { uint64_t lo,hi; uint64_t hist[256]; } hjob_t;
static void *hworker(void *arg){
    hjob_t *H=(hjob_t*)arg; memset(H->hist,0,sizeof(H->hist));
    for (uint64_t i=H->lo;i<H->hi;i++) H->hist[cnt[i]]++;
    return NULL;
}

static int hexbyte(const char*s){ int v=0; for(int i=0;i<2;i++){ char ch=s[i]; v<<=4;
    v |= (ch>='0'&&ch<='9')?ch-'0':((ch|32)-'a'+10); } return v; }
static void hex2bin(const char*s, uint8_t*o, int n){ for(int i=0;i<n;i++) o[i]=(uint8_t)hexbyte(s+2*i); }

int main(void){
    cnt = (uint8_t*)malloc((size_t)1<<32);
    if(!cnt){ fprintf(stderr,"alloc 4GB failed\n"); return 2; }
    memset(cnt,0,(size_t)1<<32);
    char line[8192];
    while (fgets(line,sizeof(line),stdin)){
        char id[64], base_hex[64], free_csv[64], rk_hex[1024], im_hex[64], ptrk_hex[512], mode_s[32];
        int r,finalmc,nbits,j0;
        if (sscanf(line,"%63s %d %d %d %d %31s %63s %63s %1023s %63s %511s",
                   id,&r,&finalmc,&nbits,&j0,mode_s,base_hex,free_csv,rk_hex,im_hex,ptrk_hex)!=11){
            if (line[0]=='\n'||line[0]=='#') continue;
            fprintf(stderr,"bad config line: %s",line); return 3;
        }
        cfg_t c; memset(&c,0,sizeof(c));
        c.r=r; c.finalmc=finalmc; c.nbits=nbits; c.j0=j0;
        c.mode = (!strcmp(mode_s,"randpt"))?1:((!strcmp(mode_s,"constcoset"))?2:0);
        c.n_texts = 1ULL<<nbits;
        uint8_t kb[16*16]; hex2bin(rk_hex,kb,16*(r+1));
        for (int i=0;i<=r;i++) c.rk[i]=_mm_loadu_si128((const __m128i*)(kb+16*i));
        uint8_t pk[176]; hex2bin(ptrk_hex,pk,176);
        for (int i=0;i<11;i++) c.ptrk[i]=_mm_loadu_si128((const __m128i*)(pk+16*i));
        hex2bin(base_hex,c.base,16);
        { char *tok=strtok(free_csv,","); int f=0; while(tok&&f<4){ c.freeb[f++]=atoi(tok); tok=strtok(NULL,","); } }
        uint8_t im[16]; hex2bin(im_hex,im,16);
        for (int row=0;row<4;row++) for(int k=0;k<4;k++){
            for (int x=0;x<256;x++) c.gt[row][k][x]=gmul(im[4*row+k],(uint8_t)x);
            c.srcbyte[row][k] = 4*(((j0-row)%4+4)%4)+k;
        }
        int small = (nbits<=28);
        if (small){ vals = (uint32_t*)malloc(sizeof(uint32_t)*c.n_texts); if(!vals){fprintf(stderr,"alloc vals\n");return 2;} }
        else vals = NULL;

        struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
        pthread_t th[NTHREADS]; job_t jobs[NTHREADS];
        uint64_t chunk = (c.n_texts + NTHREADS - 1)/NTHREADS; chunk = (chunk+7)&~7ULL;
        for (int t=0;t<NTHREADS;t++){
            jobs[t].c=&c; jobs[t].lo=t*chunk; jobs[t].hi=(t+1)*chunk;
            if (jobs[t].lo>c.n_texts) jobs[t].lo=c.n_texts;
            if (jobs[t].hi>c.n_texts) jobs[t].hi=c.n_texts;
            jobs[t].overflow=0; jobs[t].const_seen=0; jobs[t].const_init=0; jobs[t].const_val=0;
            pthread_create(&th[t],NULL,worker,&jobs[t]);
        }
        int overflow=0, allconst=1; uint32_t cv=0; int cvset=0;
        for (int t=0;t<NTHREADS;t++){ pthread_join(th[t],NULL);
            overflow |= jobs[t].overflow;
            if (jobs[t].const_init){ if(!cvset){cv=jobs[t].const_val;cvset=1;}
                if(!jobs[t].const_seen || jobs[t].const_val!=cv) allconst=0; } }

        uint64_t hist[256]; memset(hist,0,sizeof(hist));
        if (c.mode==2){ /* constant-check only: no counters touched */ }
        else if (small){
            for (uint64_t i=0;i<c.n_texts;i++){ uint32_t p=vals[i]; uint8_t m=cnt[p];
                if (m){ hist[m]++; cnt[p]=0; } }
        } else {
            pthread_t ht[NTHREADS]; hjob_t hj[NTHREADS];
            uint64_t hc=((1ULL<<32)/NTHREADS);
            for (int t=0;t<NTHREADS;t++){ hj[t].lo=t*hc; hj[t].hi=(t==NTHREADS-1)?(1ULL<<32):(t+1)*hc;
                pthread_create(&ht[t],NULL,hworker,&hj[t]); }
            for (int t=0;t<NTHREADS;t++){ pthread_join(ht[t],NULL);
                for(int v=0;v<256;v++) hist[v]+=hj[t].hist[v]; }
            memset(cnt,0,(size_t)1<<32);
        }
        clock_gettime(CLOCK_MONOTONIC,&t1);
        double secs=(t1.tv_sec-t0.tv_sec)+(t1.tv_nsec-t0.tv_nsec)/1e9;

        unsigned __int128 n=0, s2=0; uint64_t s1=0, distinct=0, maxocc=0;
        for (int v=1;v<256;v++){ if(!hist[v]) continue;
            n += (unsigned __int128)hist[v]*((uint64_t)v*(v-1)/2);
            s2 += (unsigned __int128)hist[v]*((uint64_t)v*v);
            s1 += hist[v]*(uint64_t)v; distinct += hist[v]; if(v>(int)maxocc) maxocc=v; }
        unsigned __int128 n_check = (s2 - s1)/2;
        int analytic=0;
        if (c.mode==2){ if (allconst){ n = (unsigned __int128)c.n_texts*(c.n_texts-1)/2; n_check=n;
                            s1=c.n_texts; distinct=1; maxocc=0; analytic=1; } }
        char nb[64]; { unsigned __int128 x=n; char t2[64]; int L=0; if(!x) t2[L++]='0';
            while(x){ t2[L++]=(char)('0'+(int)(x%10)); x/=10; } for(int i=0;i<L;i++) nb[i]=t2[L-1-i]; nb[L]=0; }
        printf("{\"id\":\"%s\",\"r\":%d,\"finalmc\":%d,\"nbits\":%d,\"j0\":%d,\"mode\":\"%s\","
               "\"n\":%s,\"n_mod8\":%llu,\"n_mod16\":%llu,\"sum_m\":%llu,\"distinct_buckets\":%llu,"
               "\"max_occupancy\":%llu,\"overflow\":%d,\"identity_check_ok\":%d,\"pi_constant\":%d,"
               "\"analytic_saturated\":%d,\"seconds\":%.3f,\"occupancy_hist\":[",
               id,r,finalmc,nbits,j0,mode_s,nb,(unsigned long long)(n%8),(unsigned long long)(n%16),
               (unsigned long long)s1,(unsigned long long)distinct,(unsigned long long)maxocc,
               overflow,(n==n_check),allconst&&cvset,analytic,secs);
        for (int v=0;v<=(int)maxocc+1&&v<256;v++) printf("%s%llu",v?",":"",(unsigned long long)hist[v]);
        printf("]}\n"); fflush(stdout);
        if (vals){ free(vals); vals=NULL; }
    }
    free(cnt); return 0;
}
