#include <wmmintrin.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
static __m128i EK[11],DK[11];
#define EXP(k,rc) do{ __m128i t=_mm_aeskeygenassist_si128(k,rc); t=_mm_shuffle_epi32(t,0xff); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4)); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,t);}while(0)
static void keyexp(const unsigned char*key){ __m128i k=_mm_loadu_si128((const __m128i*)key); EK[0]=k;
  EXP(k,0x01);EK[1]=k;EXP(k,0x02);EK[2]=k;EXP(k,0x04);EK[3]=k;EXP(k,0x08);EK[4]=k;EXP(k,0x10);EK[5]=k;
  EXP(k,0x20);EK[6]=k;EXP(k,0x40);EK[7]=k;EXP(k,0x80);EK[8]=k;EXP(k,0x1b);EK[9]=k;EXP(k,0x36);EK[10]=k;
  DK[0]=EK[0]; for(int i=1;i<10;i++) DK[i]=_mm_aesimc_si128(EK[i]); DK[10]=EK[10]; }
static __m128i enc(__m128i s,int r){ s=_mm_xor_si128(s,EK[0]); for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,EK[i]); return _mm_aesenclast_si128(s,EK[r]); }
static __m128i dec(__m128i s,int r){ s=_mm_xor_si128(s,EK[r]); for(int i=r-1;i>=1;i--) s=_mm_aesdec_si128(s,DK[i]); return _mm_aesdeclast_si128(s,EK[0]); }
/* one A-step: encrypt pair, swap ciphertext word 0 (inverse-SR diagonal), decrypt */
static void astep(unsigned char*a,unsigned char*b,int r){
  static const int CW[4]={0,13,10,7};
  unsigned char c0[16],c1[16];
  _mm_storeu_si128((__m128i*)c0,enc(_mm_loadu_si128((__m128i*)a),r));
  _mm_storeu_si128((__m128i*)c1,enc(_mm_loadu_si128((__m128i*)b),r));
  for(int q=0;q<4;q++){ unsigned char t=c0[CW[q]]; c0[CW[q]]=c1[CW[q]]; c1[CW[q]]=t; }
  _mm_storeu_si128((__m128i*)a,dec(_mm_loadu_si128((__m128i*)c0),r));
  _mm_storeu_si128((__m128i*)b,dec(_mm_loadu_si128((__m128i*)c1),r));
}
int main(){ unsigned char key[16]; for(int i=0;i<16;i++)key[i]=i*7+3; keyexp(key);
  int bad=0,n=0;
  for(int r=1;r<=10;r++) for(int t=0;t<200;t++){
    unsigned char p0[16],p1[16],s0[16],s1[16];
    for(int i=0;i<16;i++){p0[i]=(unsigned char)(r*31+t*17+i); p1[i]=p0[i];}
    p1[0]^=(unsigned char)(t+1); p1[5]^=(unsigned char)(t+2);
    memcpy(s0,p0,16); memcpy(s1,p1,16);
    astep(p0,p1,r); astep(p0,p1,r);            /* apply twice */
    n++; if(memcmp(p0,s0,16)||memcmp(p1,s1,16)) bad++;
  }
  printf("A-step applied TWICE with same mask: %d trials, %d not-identity\n",n,bad);
  printf("=> involution (period 2) holds: %s\n", bad==0?"YES":"NO");
  return 0; }
