#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <wmmintrin.h>
static int hb(const char*s){int v=0;for(int i=0;i<2;i++){char c=s[i];v<<=4;v|=(c>='0'&&c<='9')?c-'0':((c|32)-'a'+10);}return v;}
int main(void){
  char rk[1024],pt[64];int r,fmc;
  while(scanf("%1023s %d %d %63s",rk,&r,&fmc,pt)==4){
    uint8_t kb[176],p[16];
    for(int i=0;i<16*(r+1);i++)kb[i]=(uint8_t)hb(rk+2*i);
    for(int i=0;i<16;i++)p[i]=(uint8_t)hb(pt+2*i);
    __m128i s=_mm_loadu_si128((__m128i*)p);
    s=_mm_xor_si128(s,_mm_loadu_si128((__m128i*)kb));
    if(fmc){for(int i=1;i<=r;i++)s=_mm_aesenc_si128(s,_mm_loadu_si128((__m128i*)(kb+16*i)));}
    else{for(int i=1;i<r;i++)s=_mm_aesenc_si128(s,_mm_loadu_si128((__m128i*)(kb+16*i)));
         if(r>=1)s=_mm_aesenclast_si128(s,_mm_loadu_si128((__m128i*)(kb+16*r)));}
    uint8_t o[16];_mm_storeu_si128((__m128i*)o,s);
    for(int i=0;i<16;i++)printf("%02x",o[i]);printf("\n");fflush(stdout);
  }
  return 0;
}
