/* Resolve the disagreement: symbolic closure says AES-128 key-schedule bit support
   saturates at 1.0 by round 5; the sampled probe says 0.78125 with 21.875% of cells
   NEVER flipping. Symbolic closure is an over-approximation (it ignores XOR
   cancellation), so the sampled answer can be right. Recheck using the CPU's OWN
   key schedule (aeskeygenassist), independent of my C recurrence, many keys. */
#include <wmmintrin.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
static __m128i KS(__m128i k,__m128i g){g=_mm_shuffle_epi32(g,0xff);
 k=_mm_xor_si128(k,_mm_slli_si128(k,4));k=_mm_xor_si128(k,_mm_slli_si128(k,4));
 k=_mm_xor_si128(k,_mm_slli_si128(k,4));return _mm_xor_si128(k,g);}
static void ex(const uint8_t*kb,__m128i*rk){
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
 rk[10]=KS(rk[9],_mm_aeskeygenassist_si128(rk[9],0x36));}
static uint64_t s=0xABCDEF0123456789ULL;
static inline uint64_t R(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int main(int argc,char**argv){
  int RR=argc>1?atoi(argv[1]):10; int NS=argc>2?atoi(argv[2]):200000;
  static uint32_t c[128][128]; memset(c,0,sizeof(c));
  for(int t=0;t<NS;t++){
    uint8_t k[16],k2[16]; uint64_t a=R(),b=R(); memcpy(k,&a,8);memcpy(k+8,&b,8);
    __m128i rk[11],rk2[11]; ex(k,rk);
    uint8_t o0[16]; _mm_storeu_si128((__m128i*)o0,rk[RR]);
    for(int i=0;i<128;i++){
      memcpy(k2,k,16); k2[i>>3]^=(uint8_t)(1u<<(i&7)); ex(k2,rk2);
      uint8_t o1[16]; _mm_storeu_si128((__m128i*)o1,rk2[RR]);
      for(int j=0;j<128;j++) c[i][j]+= (uint32_t)(((o0[j>>3]^o1[j>>3])>>(j&7))&1);
    }
  }
  int zero=0,one=0; double dens=0;
  for(int i=0;i<128;i++)for(int j=0;j<128;j++){
    if(c[i][j]==0) zero++; else dens+=1.0;
    if(c[i][j]==(uint32_t)NS) one++;
  }
  printf("AESNI-KS round %d, %d keys: support_density=%.6f  never_flip=%d/16384 (%.6f)  always_flip=%d\n",
         RR,NS,dens/16384.0,zero,zero/16384.0,one);
  /* print the never-flip pattern for master bit 0 and bit 9 */
  for(int i=0;i<128;i+=37){
    printf("  masterbit %3d (byte %2d bit %d) never-flips roundkey bits:",i,i>>3,i&7);
    int n=0; for(int j=0;j<128;j++) if(c[i][j]==0){ if(n<24) printf(" %d",j); n++; }
    printf("   [count=%d]\n",n);
  }
  return 0;
}
