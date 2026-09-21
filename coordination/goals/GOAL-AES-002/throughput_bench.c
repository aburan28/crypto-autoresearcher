#include <wmmintrin.h>
#include <stdio.h>
#include <math.h>
#include <stdint.h>
#include <time.h>
int main(void){
  __m128i k[11], b=_mm_setzero_si128();
  for(int i=0;i<11;i++) k[i]=_mm_set_epi32(i,i*7,i*13,i*29);
  const uint64_t N=20000000ULL;              /* 2e7 block encryptions */
  struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
  for(uint64_t j=0;j<N;j++){
    __m128i s=_mm_xor_si128(b,k[0]);
    for(int r=1;r<10;r++) s=_mm_aesenc_si128(s,k[r]);
    s=_mm_aesenclast_si128(s,k[10]);
    b=_mm_add_epi32(s,_mm_set_epi32(0,0,0,1));
  }
  clock_gettime(CLOCK_MONOTONIC,&t1);
  double el=(t1.tv_sec-t0.tv_sec)+(t1.tv_nsec-t0.tv_nsec)/1e9;
  volatile int sink=_mm_cvtsi128_si32(b); (void)sink;
  printf("AES-128 blocks: %llu in %.3f s -> %.3e enc/sec  (log2 = %.2f)\n",
         (unsigned long long)N, el, N/el, log2(N/el));
  return 0;
}
