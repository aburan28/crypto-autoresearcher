/* MEAS-RT-C: survival depth of a property that is NOT the integral and was never
   measured in this campaign - the MIXTURE / EXCHANGE quadruple.

   DERIVED FROM SCRATCH, no literature input:
   let p1,p2 agree outside the ShiftRows diagonal D={0,5,10,15} and differ inside it.
   For a subset T of D define p3 = p1 with bytes T taken from p2, and p4 = p2 with
   bytes T taken from p1.  For EVERY byte position, {p3,p4} = {p1,p2} as a multiset,
   so S(p3_i)+S(p4_i) = S(p1_i)+S(p2_i) at every position; SubBytes then ShiftRows
   then MixColumns then AddRoundKey is (bytewise S) followed by a GF(2)-LINEAR map,
   hence the state DIFFERENCE after one full round is IDENTICAL for the pair (p1,p2)
   and for the pair (p3,p4), while the absolute states differ.  So a mixture quadruple
   is two pairs launched with the same round-1 difference from different values.
   Test 0 below verifies this derivation on the machine.

   The object tracked is the pair-of-pairs.  Statistic: does an event on pair A
   correlate with the same event on pair B after r rounds, against the null of two
   independent random pairs?  Event: the two ciphertexts agree in at least one byte
   (a "byte collision"), marginal ~ 1-(255/256)^16 ~ 0.0606.
*/
#include <wmmintrin.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

static __m128i KS(__m128i k,__m128i g){ g=_mm_shuffle_epi32(g,0xff);
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4));
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); return _mm_xor_si128(k,g); }
static void expand(const uint8_t*kb,__m128i*rk){
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
  rk[10]=KS(rk[9],_mm_aeskeygenassist_si128(rk[9],0x36)); }
static inline __m128i enc(__m128i p,__m128i*rk,int R){
  __m128i s=_mm_xor_si128(p,rk[0]);
  for(int r=1;r<R;r++) s=_mm_aesenc_si128(s,rk[r]);
  return _mm_aesenclast_si128(s,rk[R]); }
static uint64_t st;
static inline uint64_t rnd(void){ st^=st<<13; st^=st>>7; st^=st<<17; return st; }
static inline int bytecoll(__m128i a,__m128i b){
  __m128i e=_mm_cmpeq_epi8(a,b); return _mm_movemask_epi8(e)!=0; }

int main(int argc,char**argv){
  int R=argc>1?atoi(argv[1]):5;
  int LOGN=argc>2?atoi(argv[2]):22;
  int NULLMODE=argc>3?atoi(argv[3]):0;   /* 1 = pair B is an independent random pair */
  st=0xDEADBEEF12345677ULL^((uint64_t)R<<40)^((uint64_t)NULLMODE<<8)^0x1234;
  for(int i=0;i<30;i++) rnd();
  const int D[4]={0,5,10,15};
  uint64_t N=1ULL<<LOGN;
  uint64_t nA=0,nB=0,nAB=0;
  /* --- test 0: derivation check, round-1 difference equality --- */
  { int ok=1,tried=0;
    for(int t=0;t<2000;t++){
      uint8_t kb[16],p1[16],p2[16],p3[16],p4[16];
      for(int i=0;i<16;i++){ kb[i]=(uint8_t)rnd(); p1[i]=(uint8_t)rnd(); }
      memcpy(p2,p1,16); for(int i=0;i<4;i++) p2[D[i]]=(uint8_t)rnd();
      int T=1+(int)(rnd()%14);
      memcpy(p3,p1,16); memcpy(p4,p2,16);
      for(int i=0;i<4;i++) if((T>>i)&1){ p3[D[i]]=p2[D[i]]; p4[D[i]]=p1[D[i]]; }
      int diff=0; for(int i=0;i<4;i++) if(p1[D[i]]!=p2[D[i]]) diff=1;
      if(!diff) continue; tried++;
      __m128i rk[11]; expand(kb,rk);
      __m128i a=enc(_mm_loadu_si128((__m128i*)p1),rk,1), b=enc(_mm_loadu_si128((__m128i*)p2),rk,1);
      __m128i c=enc(_mm_loadu_si128((__m128i*)p3),rk,1), d=enc(_mm_loadu_si128((__m128i*)p4),rk,1);
      __m128i x=_mm_xor_si128(a,b), y=_mm_xor_si128(c,d);
      if(_mm_movemask_epi8(_mm_cmpeq_epi8(x,y))!=0xFFFF) ok=0;
    }
    printf("TEST0 round1_difference_identical_for_mixture: %s (%d quadruples)\n", ok?"HOLDS":"FAILS", tried);
  }
  /* --- main measurement --- */
  for(uint64_t t=0;t<N;t++){
    uint8_t kb[16],p1[16],p2[16],p3[16],p4[16];
    uint64_t a1=rnd(),a2=rnd(),b1=rnd(),b2=rnd();
    memcpy(kb,&a1,8); memcpy(kb+8,&a2,8);
    memcpy(p1,&b1,8); memcpy(p1+8,&b2,8);
    memcpy(p2,p1,16);
    for(int i=0;i<4;i++) p2[D[i]]=(uint8_t)rnd();
    /* DEGENERACY GUARD: require ALL FOUR diagonal bytes to differ, else for some
       subsets T the mixture pair is literally the original pair, which produces a
       round-INDEPENDENT correlation artifact (measured at ~half the raw signal). */
    int alldiff=1; for(int i=0;i<4;i++) if(p1[D[i]]==p2[D[i]]) alldiff=0;
    if(!alldiff) continue;
    int T=1+(int)(rnd()%14);            /* proper nonempty subset */
    memcpy(p3,p1,16); memcpy(p4,p2,16);
    if(NULLMODE){
      uint64_t c1=rnd(),c2=rnd();
      memcpy(p3,&c1,8); memcpy(p3+8,&c2,8);
      memcpy(p4,p3,16);
      for(int i=0;i<4;i++) p4[D[i]]=(uint8_t)rnd();
    } else {
      for(int i=0;i<4;i++) if((T>>i)&1){ p3[D[i]]=p2[D[i]]; p4[D[i]]=p1[D[i]]; }
    }
    __m128i rk[11]; expand(kb,rk);
    __m128i c1=enc(_mm_loadu_si128((__m128i*)p1),rk,R);
    __m128i c2=enc(_mm_loadu_si128((__m128i*)p2),rk,R);
    __m128i c3=enc(_mm_loadu_si128((__m128i*)p3),rk,R);
    __m128i c4=enc(_mm_loadu_si128((__m128i*)p4),rk,R);
    int A=bytecoll(c1,c2), B=bytecoll(c3,c4);
    nA+=A; nB+=B; nAB+=(A&B);
  }
  double pa=(double)nA/N, pb=(double)nB/N, pab=(double)nAB/N;
  double exp_ab=pa*pb;
  double sd=sqrt(exp_ab*(1-exp_ab)/(double)N);
  printf("R=%d mode=%s N=2^%d  P[A]=%.6f P[B]=%.6f  P[A&B]=%.6f  indep=%.6f  "
         "ratio=%.4f  z=%.2f\n", R, NULLMODE?"NULL":"MIX", LOGN, pa,pb,pab,exp_ab,
         pab/exp_ab, (pab-exp_ab)/sd);
  return 0;
}
