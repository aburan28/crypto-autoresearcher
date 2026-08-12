/* (1) cross-check my FIPS-197 key schedule against the CPU's aeskeygenassist path
   (2) EXACT byte-level dependency: which master-key BYTES can affect which
       round-key BYTES, computed as a transitive closure over the word recurrence. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <wmmintrin.h>
static uint8_t SB[256];
static uint8_t gm(uint8_t a,uint8_t b){uint8_t r=0;while(b){if(b&1)r^=a;a=(a<<1)^((a&0x80)?0x1b:0);b>>=1;}return r;}
static uint8_t gi(uint8_t a){if(!a)return 0;for(int i=1;i<256;i++)if(gm(a,(uint8_t)i)==1)return (uint8_t)i;return 0;}
static uint8_t rl(uint8_t x,int n){return (uint8_t)((x<<n)|(x>>(8-n)));}
static uint32_t sw(uint32_t w){return ((uint32_t)SB[(w>>24)&255]<<24)|((uint32_t)SB[(w>>16)&255]<<16)|((uint32_t)SB[(w>>8)&255]<<8)|SB[w&255];}
static uint32_t rw(uint32_t w){return (w<<8)|(w>>24);}
static const uint32_t RC[11]={0,0x01000000,0x02000000,0x04000000,0x08000000,0x10000000,0x20000000,0x40000000,0x80000000,0x1b000000,0x36000000};
static __m128i KSa(__m128i k,__m128i g){g=_mm_shuffle_epi32(g,0xff);
 k=_mm_xor_si128(k,_mm_slli_si128(k,4));k=_mm_xor_si128(k,_mm_slli_si128(k,4));
 k=_mm_xor_si128(k,_mm_slli_si128(k,4));return _mm_xor_si128(k,g);}
int main(void){
  for(int x=0;x<256;x++){uint8_t b=gi((uint8_t)x);SB[x]=b^rl(b,1)^rl(b,2)^rl(b,3)^rl(b,4)^0x63;}
  /* (1) */
  uint8_t k[16]={0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c};
  uint32_t W[44];
  for(int i=0;i<4;i++)W[i]=((uint32_t)k[4*i]<<24)|((uint32_t)k[4*i+1]<<16)|((uint32_t)k[4*i+2]<<8)|k[4*i+3];
  for(int i=4;i<44;i++){uint32_t t=W[i-1]; if(i%4==0)t=sw(rw(t))^RC[i/4]; W[i]=W[i-4]^t;}
  __m128i rk[11]; rk[0]=_mm_loadu_si128((__m128i*)k);
  const int rc[10]={0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
  int bad=0;
  for(int r=1;r<=10;r++){
    switch(rc[r-1]){
      case 0x01: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x01)); break;
      case 0x02: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x02)); break;
      case 0x04: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x04)); break;
      case 0x08: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x08)); break;
      case 0x10: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x10)); break;
      case 0x20: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x20)); break;
      case 0x40: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x40)); break;
      case 0x80: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x80)); break;
      case 0x1b: rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x1b)); break;
      default:   rk[r]=KSa(rk[r-1],_mm_aeskeygenassist_si128(rk[r-1],0x36)); break;
    }
    uint8_t o[16]; _mm_storeu_si128((__m128i*)o,rk[r]);
    for(int j=0;j<4;j++){ uint32_t w=((uint32_t)o[4*j]<<24)|((uint32_t)o[4*j+1]<<16)|((uint32_t)o[4*j+2]<<8)|o[4*j+3];
      if(w!=W[4*r+j]) bad++; }
  }
  printf("KS_CROSSCHECK_vs_AESNI word_mismatches=%d ; W[43]=%08x (FIPS-197 A.1 expects b6630ca6)\n",bad,W[43]);
  /* (2) exact byte dependency closure for AES-128 */
  { uint32_t dep[44][4];  /* dep[i][b] = bitmask over 16 master bytes affecting byte b of W[i] */
    for(int i=0;i<4;i++) for(int b=0;b<4;b++) dep[i][b]=1u<<(4*i+b);
    for(int i=4;i<44;i++){
      uint32_t t[4];
      if(i%4==0){ /* RotWord then SubWord: byte b of result depends on byte (b+1)%4 of W[i-1] */
        for(int b=0;b<4;b++) t[b]=dep[i-1][(b+1)%4];
      } else for(int b=0;b<4;b++) t[b]=dep[i-1][b];
      for(int b=0;b<4;b++) dep[i][b]=dep[i-4][b]|t[b];
    }
    for(int R=0;R<=10;R++){
      int tot=0;
      for(int j=0;j<4;j++) for(int b=0;b<4;b++) tot+=__builtin_popcount(dep[4*R+j][b]);
      printf("  AES-128 round %2d: master-BYTES influencing round-key bytes = %3d / 256  (%.4f)\n",
             R,tot,tot/256.0);
    }
    /* which pairs are permanently absent at R=10 */
    int miss=0; for(int j=0;j<4;j++) for(int b=0;b<4;b++)
      miss += 16-__builtin_popcount(dep[43-3+j*0][b]); /* placeholder */
    (void)miss;
  }
  return 0;
}
