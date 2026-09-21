/* 4-round AES integral: full-diagonal delta-set of 2^32 plaintexts.
   Bytes 0,5,10,15 (a ShiftRows diagonal) take all 2^32 values; rest fixed.
   Accumulate XOR of ciphertexts. Balanced => structure survives r rounds. */
#include <wmmintrin.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static __m128i KS(__m128i k, __m128i g){ g=_mm_shuffle_epi32(g,0xff);
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4));
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); return _mm_xor_si128(k,g); }
int main(int argc,char**argv){
  int R = argc>1? atoi(argv[1]) : 4;          /* round count */
  uint64_t seed = argc>2? strtoull(argv[2],0,10) : 1;
  uint8_t kb[16], base[16];
  for(int i=0;i<16;i++){ seed=seed*6364136223846793005ULL+1442695040888963407ULL;
    kb[i]=(seed>>33)&0xff; }
  for(int i=0;i<16;i++){ seed=seed*6364136223846793005ULL+1442695040888963407ULL;
    base[i]=(seed>>33)&0xff; }
  __m128i rk[11]; rk[0]=_mm_loadu_si128((__m128i*)kb);
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
  __m128i acc=_mm_setzero_si128();
  uint8_t p[16]; memcpy(p,base,16);
  const int D[4]={0,5,10,15};
  for(uint64_t v=0; v<(1ULL<<32); v++){
    p[D[0]]=v&0xff; p[D[1]]=(v>>8)&0xff; p[D[2]]=(v>>16)&0xff; p[D[3]]=(v>>24)&0xff;
    __m128i s=_mm_xor_si128(_mm_loadu_si128((__m128i*)p),rk[0]);
    for(int r=1;r<R;r++) s=_mm_aesenc_si128(s,rk[r]);
    s=_mm_aesenclast_si128(s,rk[R]);
    acc=_mm_xor_si128(acc,s);
  }
  uint8_t o[16]; _mm_storeu_si128((__m128i*)o,acc);
  int bal=0; for(int i=0;i<16;i++) if(o[i]==0) bal++;
  printf("R=%d seed=%llu balanced_bytes=%d/16  acc=", R,(unsigned long long)argv[2]?strtoull(argv[2],0,10):1, bal);
  for(int i=0;i<16;i++) printf("%02x",o[i]); printf("\n");
  return 0;
}
