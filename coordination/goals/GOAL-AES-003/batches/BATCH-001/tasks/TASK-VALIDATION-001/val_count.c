/* VALIDATOR independent re-implementation of the count5 statistic.
 * Written from the PREREGISTRATION.md spec text only; shares no code with
 * count5.c (own key schedule via AESKEYGENASSIST, own projection index
 * derivation, own sharding, own accumulation, own null modes).
 *
 * usage: val_count <r> <j0> <mode> <hex> <basehex> <pi:id|fd> [w8|w64]
 *   mode=key   : hex = 16-byte AES-128 key, schedule computed here
 *   mode=rk    : hex = 176-byte round key blob (independent-round-key null)
 *   mode=balls : uniform random-function null; hex = 8-byte seed
 *   pi=id : bytes 4*((j0-t)%4)+t   (inverse-ShiftRows / ciphertext diagonal)
 *   pi=fd : bytes 4*((j0+t)%4)+t   (forward diagonal, sibling null)
 *   w64   : 64-bit counters (sparse low-round controls, MAP_NORESERVE)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <wmmintrin.h>
#include <sys/mman.h>
#include <time.h>

#define NT 4
static __m128i rk[11];
static int R, J0, WIDE, BALLS;
static uint64_t SEED;
static uint8_t *c8; static uint64_t *c64;
static unsigned __int128 ACC_N[NT],ACC_S2[NT],ACC_NP[NT];
static uint64_t ACC_MAX[NT];
static int8_t pidx[4];

/* --- own AES-128 key schedule ------------------------------------------ */
#define KSTEP(K,RC) do{ __m128i t=_mm_aeskeygenassist_si128(K,RC); \
  t=_mm_shuffle_epi32(t,0xff); \
  __m128i u=K; u=_mm_xor_si128(u,_mm_slli_si128(u,4)); \
  u=_mm_xor_si128(u,_mm_slli_si128(u,4)); \
  u=_mm_xor_si128(u,_mm_slli_si128(u,4)); K=_mm_xor_si128(u,t);}while(0)
static void ks(const uint8_t *k){
  __m128i K=_mm_loadu_si128((const __m128i*)k); rk[0]=K;
  KSTEP(K,0x01); rk[1]=K;  KSTEP(K,0x02); rk[2]=K;
  KSTEP(K,0x04); rk[3]=K;  KSTEP(K,0x08); rk[4]=K;
  KSTEP(K,0x10); rk[5]=K;  KSTEP(K,0x20); rk[6]=K;
  KSTEP(K,0x40); rk[7]=K;  KSTEP(K,0x80); rk[8]=K;
  KSTEP(K,0x1b); rk[9]=K;  KSTEP(K,0x36); rk[10]=K;
}
static void hx(const char*h,uint8_t*o,int n){unsigned v;for(int i=0;i<n;i++){sscanf(h+2*i,"%2x",&v);o[i]=(uint8_t)v;}}

/* splitmix64 for the balls-in-bins null */
static inline uint64_t sm64(uint64_t *s){
  uint64_t z=(*s+=0x9E3779B97F4A7C15ull);
  z=(z^(z>>30))*0xBF58476D1CE4E5B9ull; z=(z^(z>>27))*0x94D049BB133111EBull;
  return z^(z>>31);
}

static uint8_t BASE[16];

typedef struct{int t;}A;
static void*wrk(void*ap){
  int t=((A*)ap)->t;
  uint64_t lo=(uint64_t)t<<30, hi=lo+(1ull<<30);
  if(BALLS){
    /* every thread regenerates the SAME global stream of 2^32 balls and
       counts only those landing in its own value shard */
    uint64_t s=SEED;
    for(uint64_t i=0;i<(1ull<<31);i++){
      uint64_t x=sm64(&s);
      uint32_t v1=(uint32_t)x, v2=(uint32_t)(x>>32);
      if(v1>=lo&&v1<hi){ if(WIDE)c64[v1]++; else if(c8[v1]!=255)c8[v1]++; }
      if(v2>=lo&&v2<hi){ if(WIDE)c64[v2]++; else if(c8[v2]!=255)c8[v2]++; }
    }
  }
  if(!BALLS){
    uint8_t pb[16]; memcpy(pb,BASE,16);
    for(uint64_t d0=0; d0<256; d0++){
      pb[0]=(uint8_t)d0;
      for(uint64_t d1=0; d1<256; d1++){
        pb[5]=(uint8_t)d1;
        for(uint64_t d2=0; d2<256; d2++){
          pb[10]=(uint8_t)d2;
          __m128i p[16];
          for(uint64_t d3=0; d3<256; d3+=16){
            for(int k=0;k<16;k++){ pb[15]=(uint8_t)(d3+k);
              p[k]=_mm_loadu_si128((__m128i*)pb); }
            for(int k=0;k<16;k++) p[k]=_mm_xor_si128(p[k],rk[0]);
            for(int i=1;i<R;i++) for(int k=0;k<16;k++) p[k]=_mm_aesenc_si128(p[k],rk[i]);
            for(int k=0;k<16;k++) p[k]=_mm_aesenclast_si128(p[k],rk[R]);
            for(int k=0;k<16;k++){
              uint8_t cb[16]; _mm_storeu_si128((__m128i*)cb,p[k]);
              uint32_t v=(uint32_t)cb[pidx[0]] | ((uint32_t)cb[pidx[1]]<<8)
                       | ((uint32_t)cb[pidx[2]]<<16) | ((uint32_t)cb[pidx[3]]<<24);
              if(v>=lo&&v<hi){ if(WIDE)c64[v]++; else if(c8[v]!=255)c8[v]++; }
            }
          }
        }
      }
    }
  }
  unsigned __int128 an=0,as=0,apr=0; uint64_t mx=0;
  for(uint64_t v=lo;v<hi;v++){
    uint64_t m = WIDE? c64[v] : (uint64_t)c8[v];
    if(m){ an+=m; as+=(unsigned __int128)m*m; apr+=(unsigned __int128)m*(m-1)/2;
           if(m>mx)mx=m; }
  }
  ACC_N[t]=an; ACC_S2[t]=as; ACC_NP[t]=apr; ACC_MAX[t]=mx;
  return NULL;
}

int main(int argc,char**argv){
  if(argc<7){fprintf(stderr,"args\n");return 2;}
  R=atoi(argv[1]); J0=atoi(argv[2]);
  const char*mode=argv[3];
  WIDE = (argc>7 && strcmp(argv[7],"w64")==0);
  if(!strcmp(mode,"key")){ uint8_t k[16]; hx(argv[4],k,16); ks(k); }
  else if(!strcmp(mode,"rk")){ uint8_t b[176]; hx(argv[4],b,176);
    for(int i=0;i<11;i++) rk[i]=_mm_loadu_si128((__m128i*)(b+16*i)); }
  else if(!strcmp(mode,"balls")){ BALLS=1; SEED=strtoull(argv[4],0,16); }
  else {fprintf(stderr,"mode\n");return 2;}
  hx(argv[5],BASE,16);
  int fd = (strcmp(argv[6],"fd")==0);
  for(int t=0;t<4;t++){
    int m = fd ? ((J0+t)%4+4)%4 : ((J0-t)%4+4)%4;
    pidx[t]=(int8_t)(4*m+t);
  }
  size_t need = WIDE ? (1ull<<32)*8 : (1ull<<32);
  void *p=mmap(NULL,need,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE,-1,0);
  if(p==MAP_FAILED){perror("mmap");return 3;}
  madvise(p,need,MADV_HUGEPAGE);
  if(WIDE) c64=(uint64_t*)p; else c8=(uint8_t*)p;

  struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
  pthread_t th[NT]; A ar[NT];
  for(int i=0;i<NT;i++){ar[i].t=i;pthread_create(&th[i],0,wrk,&ar[i]);}
  for(int i=0;i<NT;i++)pthread_join(th[i],0);
  clock_gettime(CLOCK_MONOTONIC,&t1);

  unsigned __int128 N=0,S2=0,np=0; uint64_t mx=0;
  for(int t=0;t<NT;t++){N+=ACC_N[t];S2+=ACC_S2[t];np+=ACC_NP[t];
                        if(ACC_MAX[t]>mx)mx=ACC_MAX[t];}
  unsigned __int128 alt=(S2-N)/2;
  /* 128-bit decimal print */
  char nb[48],pb2[48]; unsigned __int128 x;
  #define P128(dst,val) do{ x=val; int i=47; dst[i--]=0; if(!x)dst[i--]='0'; \
    while(x){dst[i--]='0'+(int)(x%10);x/=10;} memmove(dst,dst+i+1,47-i);}while(0)
  P128(nb,N); P128(pb2,np);
  double s=(t1.tv_sec-t0.tv_sec)+1e-9*(t1.tv_nsec-t0.tv_nsec);
  printf("{\"r\":%d,\"j0\":%d,\"mode\":\"%s\",\"pi\":\"%s\",\"wide\":%d,",
    R,J0,mode,fd?"fd":"id",WIDE);
  printf("\"N\":%s,\"n\":%s,\"identity_agree\":%s,\"n_mod8\":%llu,\"n_mod16\":%llu,",
    nb,pb2,(np==alt)?"true":"false",(unsigned long long)(np%8),(unsigned long long)(np%16));
  printf("\"max_occ\":%llu,\"saturated\":%s,\"seconds\":%.1f}\n",
    (unsigned long long)mx,(!WIDE&&mx>=255)?"true":"false",s);
  return 0;
}
