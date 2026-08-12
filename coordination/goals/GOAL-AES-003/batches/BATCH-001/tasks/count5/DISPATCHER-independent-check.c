/* Independent check of the mod-8 counting property. Own implementation. */
#include <wmmintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
static __m128i EK[11];
#define EXP(k,rc) do{ __m128i t=_mm_aeskeygenassist_si128(k,rc); t=_mm_shuffle_epi32(t,0xff); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4)); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,t);}while(0)
static void keyexp(const unsigned char*key){ __m128i k=_mm_loadu_si128((const __m128i*)key); EK[0]=k;
  EXP(k,0x01);EK[1]=k;EXP(k,0x02);EK[2]=k;EXP(k,0x04);EK[3]=k;EXP(k,0x08);EK[4]=k;EXP(k,0x10);EK[5]=k;
  EXP(k,0x20);EK[6]=k;EXP(k,0x40);EK[7]=k;EXP(k,0x80);EK[8]=k;EXP(k,0x1b);EK[9]=k;EXP(k,0x36);EK[10]=k; }
static inline __m128i enc(__m128i s,int r){ s=_mm_xor_si128(s,EK[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,EK[i]); return _mm_aesenclast_si128(s,EK[r]); }
static uint8_t *cnt;                 /* uint16 to avoid the uint8 saturation the prior run hit */
static int R,J0; static unsigned char BASE[16];
typedef struct{ uint64_t lo,hi; } arg_t;
static void* work(void*vp){
  arg_t*a=vp; int PD[4]={0,5,10,15};
  int ID[4]; for(int t=0;t<4;t++) ID[t]=4*(((J0-t)%4+4)%4)+t;   /* inverse-SR diagonal */
  for(uint64_t x=a->lo;x<a->hi;x++){
    unsigned char p[16]; memcpy(p,BASE,16);
    p[PD[0]]=x&0xff; p[PD[1]]=(x>>8)&0xff; p[PD[2]]=(x>>16)&0xff; p[PD[3]]=(x>>24)&0xff;
    unsigned char c[16]; _mm_storeu_si128((__m128i*)c,enc(_mm_loadu_si128((__m128i*)p),R));
    uint32_t v=((uint32_t)c[ID[0]])|((uint32_t)c[ID[1]]<<8)|((uint32_t)c[ID[2]]<<16)|((uint32_t)c[ID[3]]<<24);
    __sync_fetch_and_add(&cnt[v],1);
  }
  return 0; }
int main(int argc,char**argv){
  R=atoi(argv[1]); J0=atoi(argv[2]); unsigned seed=atoi(argv[3]); int T=4;
  srand(seed); unsigned char key[16];
  for(int i=0;i<16;i++) key[i]=rand()&0xff;
  for(int i=0;i<16;i++) BASE[i]=rand()&0xff;
  keyexp(key);
  cnt=calloc((size_t)1<<32,1); if(!cnt){fprintf(stderr,"alloc fail\n");return 1;}
  pthread_t th[8]; arg_t ar[8]; uint64_t N=1ULL<<32, per=N/T;
  for(int i=0;i<T;i++){ ar[i]=(arg_t){i*per,(i==T-1)?N:(i+1)*per}; pthread_create(&th[i],0,work,&ar[i]); }
  for(int i=0;i<T;i++) pthread_join(th[i],0);
  unsigned long long pairs=0,tot=0,nonempty=0,maxocc=0,sat=0;
  for(uint64_t v=0;v<(1ULL<<32);v++){ uint8_t m=cnt[v];
    if(m){nonempty++; tot+=m; if(m>maxocc)maxocc=m; if(m==255)sat++;}
    pairs += (unsigned long long)m*(m-1)/2; }
  printf("{\"rounds\":%d,\"j0\":%d,\"total\":%llu,\"nonempty_buckets\":%llu,\"max_occ\":%llu,\"saturated\":%llu,\"pairs\":%llu,\"pairs_mod_8\":%llu}\n",
         R,J0,tot,nonempty,maxocc,sat,pairs,pairs%8);
  return 0; }
