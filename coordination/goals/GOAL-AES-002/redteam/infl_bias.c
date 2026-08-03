/* MEAS-RT-B: the FINER structure the influence-density probe misses by construction.
   influence_support_receipt.json measures only whether entry (i,j) of the
   key-bit -> ciphertext-bit influence matrix is EVER set (density -> 0.4996).
   Here we measure, for every (i,j), the PROBABILITY over random (K,P) that
   flipping key bit i flips ciphertext bit j.  Density 0.5 is compatible with
   arbitrarily large per-entry bias; this probe sees the bias.
   Null control: identical estimator where the second encryption uses an
   INDEPENDENT random key rather than the flipped key. */
#include <wmmintrin.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

static __m128i KS(__m128i k, __m128i g){ g=_mm_shuffle_epi32(g,0xff);
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4));
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); return _mm_xor_si128(k,g); }
static void expand(const uint8_t*kb, __m128i*rk){
  rk[0]=_mm_loadu_si128((const __m128i*)kb);
  rk[1]=KS(rk[0],_mm_aeskeygenassist_si128(rk[0],0x01));
  rk[2]=KS(rk[1],_mm_aeskeygenassist_si128(rk[1],0x02));
  rk[3]=KS(rk[2],_mm_aeskeygenassist_si128(rk[2],0x04));
  rk[4]=KS(rk[3],_mm_aeskeygenassist_si128(rk[3],0x08));
  rk[5]=KS(rk[4],_mm_aeskeygenassist_si128(rk[4],0x10));
  rk[6]=KS(rk[5],_mm_aeskeygenassist_si128(rk[5],0x20));
  rk[7]=KS(rk[6],_mm_aeskeygenassist_si128(rk[6],0x40));
  rk[8]=KS(rk[7],_mm_aeskeygenassist_si128(rk[7],0x80));
  rk[9]=KS(rk[8],_mm_aeskeygenassist_si128(rk[8],0x1b));
  rk[10]=KS(rk[9],_mm_aeskeygenassist_si128(rk[9],0x36));
}
static __m128i enc(__m128i p, __m128i*rk, int R){
  __m128i s=_mm_xor_si128(p,rk[0]);
  for(int r=1;r<R;r++) s=_mm_aesenc_si128(s,rk[r]);
  return _mm_aesenclast_si128(s,rk[R]);
}
static uint64_t st;
static inline uint64_t rnd(void){ st^=st<<13; st^=st>>7; st^=st<<17; return st; }

int main(int argc,char**argv){
  int R = argc>1?atoi(argv[1]):10;
  int LOGN = argc>2?atoi(argv[2]):16;   /* samples per key bit = 2^LOGN */
  int NULLMODE = argc>3?atoi(argv[3]):0;
  st = 0x9E3779B97F4A7C15ULL ^ ((uint64_t)R<<32) ^ (uint64_t)NULLMODE*0x5851F42Du;
  for(int i=0;i<20;i++) rnd();
  uint64_t N = 1ULL<<LOGN;
  static uint32_t cnt[128][128];
  memset(cnt,0,sizeof(cnt));
  uint8_t kb[16],kb2[16],pb[16];
  __m128i rk[11],rk2[11];
  for(uint64_t t=0;t<N;t++){
    uint64_t a=rnd(),b=rnd(),c=rnd(),d=rnd();
    memcpy(kb,&a,8); memcpy(kb+8,&b,8); memcpy(pb,&c,8); memcpy(pb+8,&d,8);
    expand(kb,rk);
    __m128i p=_mm_loadu_si128((__m128i*)pb);
    __m128i C0=enc(p,rk,R);
    uint8_t c0[16]; _mm_storeu_si128((__m128i*)c0,C0);
    for(int i=0;i<128;i++){
      memcpy(kb2,kb,16);
      if(NULLMODE){ uint64_t e=rnd(),f=rnd(); memcpy(kb2,&e,8); memcpy(kb2+8,&f,8); }
      else kb2[i>>3] ^= (uint8_t)(1u<<(i&7));
      expand(kb2,rk2);
      __m128i C1=enc(p,rk2,R);
      uint8_t c1[16]; _mm_storeu_si128((__m128i*)c1,C1);
      for(int j=0;j<128;j++){
        int bit = ((c0[j>>3]^c1[j>>3])>>(j&7))&1;
        cnt[i][j]+= (uint32_t)bit;
      }
    }
  }
  double sd = 0.5/sqrt((double)N);
  double maxz=0, sumz2=0; int imax=0,jmax=0; int over4=0, over5=0;
  double density=0;
  for(int i=0;i<128;i++) for(int j=0;j<128;j++){
    double p=(double)cnt[i][j]/(double)N;
    double z=(p-0.5)/sd;
    if(cnt[i][j]>0) density+=1.0;
    sumz2+=z*z;
    if(fabs(z)>fabs(maxz)){ maxz=z; imax=i; jmax=j; }
    if(fabs(z)>4.0) over4++;
    if(fabs(z)>5.0) over5++;
  }
  density/=16384.0;
  /* chi-square with 16384 df; expected 16384, sd sqrt(2*16384)=181 */
  printf("R=%2d mode=%s N=2^%d  ever_set_density=%.4f  max|z|=%.2f at (kbit %d,cbit %d)  "
         "cells|z|>4=%d  |z|>5=%d  chi2=%.1f (E=16384, sd=181.0, dev=%.2f sd)\n",
         R, NULLMODE?"NULL":"FLIP", LOGN, density, fabs(maxz), imax, jmax, over4, over5,
         sumz2, (sumz2-16384.0)/181.019);
  return 0;
}
