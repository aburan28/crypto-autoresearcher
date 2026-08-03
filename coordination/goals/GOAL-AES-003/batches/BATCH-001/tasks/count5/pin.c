#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <wmmintrin.h>
static void hex2bytes(const char*h,uint8_t*o,int n){for(int i=0;i<n;i++){unsigned v;sscanf(h+2*i,"%2x",&v);o[i]=v;}}
int main(int argc,char**argv){ // pin <r> <RKhex176> <pt hex16>
  int r=atoi(argv[1]); uint8_t rkb[176],pt[16];
  hex2bytes(argv[2],rkb,176); hex2bytes(argv[3],pt,16);
  __m128i RK[11]; for(int i=0;i<11;i++)RK[i]=_mm_loadu_si128((__m128i*)(rkb+16*i));
  __m128i s=_mm_loadu_si128((__m128i*)pt);
  s=_mm_xor_si128(s,RK[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,RK[i]);
  s=_mm_aesenclast_si128(s,RK[r]);
  uint8_t o[16]; _mm_storeu_si128((__m128i*)o,s);
  for(int i=0;i<16;i++) printf("%02x",o[i]); printf("\n"); return 0;}
