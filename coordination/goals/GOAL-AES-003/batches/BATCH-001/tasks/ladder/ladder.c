/* CAND-ND-1: projection-multiplicity ladder. Independent implementation. */
#include <wmmintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static __m128i EK[11];
#define EXP(k,rc) do{ __m128i t=_mm_aeskeygenassist_si128(k,rc); t=_mm_shuffle_epi32(t,0xff); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4)); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,t);}while(0)
static void keyexp(const unsigned char*key){ __m128i k=_mm_loadu_si128((const __m128i*)key); EK[0]=k;
  EXP(k,0x01);EK[1]=k;EXP(k,0x02);EK[2]=k;EXP(k,0x04);EK[3]=k;EXP(k,0x08);EK[4]=k;EXP(k,0x10);EK[5]=k;
  EXP(k,0x20);EK[6]=k;EXP(k,0x40);EK[7]=k;EXP(k,0x80);EK[8]=k;EXP(k,0x1b);EK[9]=k;EXP(k,0x36);EK[10]=k; }
static inline __m128i enc(__m128i s,int r){ s=_mm_xor_si128(s,EK[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,EK[i]); return _mm_aesenclast_si128(s,EK[r]); }
static int cmp32(const void*a,const void*b){ uint32_t x=*(const uint32_t*)a,y=*(const uint32_t*)b; return x<y?-1:(x>y); }
int main(int argc,char**argv){
  int r=atoi(argv[1]); int lgN=atoi(argv[2]); unsigned seed=atoi(argv[3]);
  int PD[4]={0,5,10,15};                 /* plaintext diagonal D_0 (forward diagonal) */
  int CW[4]={0,13,10,7};                 /* ciphertext word 0 = inverse-SR diagonal */
  unsigned char key[16]; srand(seed);
  for(int i=0;i<16;i++) key[i]=rand()&0xff;
  keyexp(key);
  size_t N=(size_t)1<<lgN;
  uint32_t*proj=malloc(N*4);
  unsigned char base[16]; for(int i=0;i<16;i++) base[i]=rand()&0xff;
  for(size_t t=0;t<N;t++){
    unsigned char p[16]; memcpy(p,base,16);
    /* vary ONLY the four diagonal bytes -> all pairwise differences lie in D_0 */
    p[PD[0]]=(unsigned char)(t&0xff); p[PD[1]]=(unsigned char)((t>>8)&0xff);
    p[PD[2]]=(unsigned char)((t>>16)&0xff); p[PD[3]]=(unsigned char)((t>>24)&0xff);
    unsigned char c[16]; _mm_storeu_si128((__m128i*)c,enc(_mm_loadu_si128((__m128i*)p),r));
    proj[t]=((uint32_t)c[CW[0]])|((uint32_t)c[CW[1]]<<8)|((uint32_t)c[CW[2]]<<16)|((uint32_t)c[CW[3]]<<24);
  }
  qsort(proj,N,4,cmp32);
  /* count colliding PAIRS = sum over fibres of C(m,2) */
  unsigned long long pairs=0; size_t i=0; size_t maxmult=0;
  while(i<N){ size_t j=i; while(j<N && proj[j]==proj[i]) j++;
    size_t m=j-i; if(m>maxmult) maxmult=m; pairs += (unsigned long long)m*(m-1)/2; i=j; }
  double expct = (double)N*(N-1)/2.0/4294967296.0;
  printf("{\"rounds\":%d,\"N\":%zu,\"colliding_pairs\":%llu,\"null_expectation\":%.1f,\"max_multiplicity\":%zu}\n",
         r,N,pairs,expct,maxmult);
  return 0; }
