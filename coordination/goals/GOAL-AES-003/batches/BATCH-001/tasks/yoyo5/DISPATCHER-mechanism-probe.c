#include <wmmintrin.h>
#include <smmintrin.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

static __m128i EK[11], DK[11];
#define EXP(k,rc) do{ __m128i t=_mm_aeskeygenassist_si128(k,rc); t=_mm_shuffle_epi32(t,0xff); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4)); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,t);}while(0)
static void keyexp(const unsigned char*key){
  __m128i k=_mm_loadu_si128((const __m128i*)key); EK[0]=k;
  EXP(k,0x01);EK[1]=k; EXP(k,0x02);EK[2]=k; EXP(k,0x04);EK[3]=k; EXP(k,0x08);EK[4]=k;
  EXP(k,0x10);EK[5]=k; EXP(k,0x20);EK[6]=k; EXP(k,0x40);EK[7]=k; EXP(k,0x80);EK[8]=k;
  EXP(k,0x1b);EK[9]=k; EXP(k,0x36);EK[10]=k;
  DK[0]=EK[0]; for(int i=1;i<10;i++) DK[i]=_mm_aesimc_si128(EK[i]); DK[10]=EK[10];
}
static inline __m128i enc(__m128i s,int r){          /* r-round AES, last round no MixColumns */
  s=_mm_xor_si128(s,EK[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,EK[i]);
  return _mm_aesenclast_si128(s,EK[r]);
}
static inline __m128i dec(__m128i s,int r){          /* exact inverse of enc(.,r) */
  s=_mm_xor_si128(s,EK[r]);
  for(int i=r-1;i>=1;i--) s=_mm_aesdec_si128(s,DK[i]);
  return _mm_aesdeclast_si128(s,EK[0]);
}
static int NACT_G=4;
typedef struct{ uint64_t n,seed; int r,tid; uint64_t hits,trivial; } arg_t;
static inline uint64_t sm(uint64_t*x){ uint64_t z=(*x+=0x9E3779B97F4A7C15ULL);
  z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
static void* work(void*vp){
  arg_t*a=vp; uint64_t st=a->seed^(0x1234567ULL*(a->tid+1));
  unsigned char p0[16],p1[16];
  for(uint64_t t=0;t<a->n;t++){
    uint64_t x=sm(&st),y=sm(&st);
    memcpy(p0,&x,8); memcpy(p0+8,&y,8); memcpy(p1,p0,16);
    /* activate DIAGONAL 0 = bytes 0,5,10,15 with a nonzero difference */
    uint64_t d=sm(&st); unsigned char*dd=(unsigned char*)&d;
    if(!(dd[0]|dd[1]|dd[2]|dd[3])) dd[0]=1;   /* active word genuinely active */
    { static const int PW0[4]={0,5,10,15};
      for(int q=0;q<4;q++){ unsigned char v = (q<NACT_G)? dd[q] : 0; if(q<NACT_G && v==0) v=1; p1[PW0[q]]^=v; } }
    __m128i c0=enc(_mm_loadu_si128((__m128i*)p0),a->r);
    __m128i c1=enc(_mm_loadu_si128((__m128i*)p1),a->r);
    /* swap COLUMN 0 (bytes 0..3) between the two ciphertexts */
    unsigned char b0[16],b1[16];
    _mm_storeu_si128((__m128i*)b0,c0); _mm_storeu_si128((__m128i*)b1,c1);
    static const int CW0[4]={0,13,10,7};      /* inverse-ShiftRows diagonal 0 */
    int noop=1; for(int q=0;q<4;q++) if(b0[CW0[q]]!=b1[CW0[q]]) {noop=0;break;}
    unsigned char t0[16],t1[16]; memcpy(t0,b0,16); memcpy(t1,b1,16);
    for(int q=0;q<4;q++){ t0[CW0[q]]=b1[CW0[q]]; t1[CW0[q]]=b0[CW0[q]]; }
    __m128i q0=dec(_mm_loadu_si128((__m128i*)t0),a->r);
    __m128i q1=dec(_mm_loadu_si128((__m128i*)t1),a->r);
    unsigned char e0[16],e1[16];
    _mm_storeu_si128((__m128i*)e0,q0); _mm_storeu_si128((__m128i*)e1,q1);
    /* count zero-difference DIAGONALS in the decrypted pair */
    int W=0;
    for(int j=0;j<4;j++){
      int z=1;
      for(int k=0;k<4;k++){ int idx=4*((j+k)%4)+k; if(e0[idx]!=e1[idx]){z=0;break;} }
      W+=z;
    }
    if(W>=1){ if(noop) a->trivial++; else a->hits++; }
  }
  return 0;
}
int main(int argc,char**argv){
  int r=atoi(argv[1]); int lgN=atoi(argv[2]); uint64_t seed=strtoull(argv[3],0,10); int T=4;
  int NACT=argc>4?atoi(argv[4]):4;
  unsigned char key[16]; uint64_t ks=seed^0xABCDEF;
  for(int i=0;i<16;i++) key[i]=(unsigned char)(sm(&ks));
  NACT_G=NACT; keyexp(key);
  uint64_t N=1ULL<<lgN, per=N/T;
  pthread_t th[8]; arg_t ar[8];
  for(int i=0;i<T;i++){ ar[i]=(arg_t){per,seed,r,i,0,0}; pthread_create(&th[i],0,work,&ar[i]); }
  uint64_t hits=0,triv=0;
  for(int i=0;i<T;i++){ pthread_join(th[i],0); hits+=ar[i].hits; triv+=ar[i].trivial; }
  double expct = 4.0*(double)N/4294967296.0;
  printf("{\"nact\":%d,\"rounds\":%d,\"N\":%llu,\"nontrivial_hits\":%llu,\"trivial\":%llu,\"expected_null\":%.2f,\"ratio\":%.2f}\n",
     NACT,r,(unsigned long long)N,(unsigned long long)hits,(unsigned long long)triv,expct, expct>0?hits/expct:0.0);
  return 0;
}
