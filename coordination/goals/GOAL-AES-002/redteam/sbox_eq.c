/* MEAS-RT-A: exact count of low-degree GF(2) equations satisfied by the AES S-box.
   Replaces the "39 equations per S-box, UNVERIFIED-FROM-MEMORY" input of
   algebraic_lane_receipt.json with a derived, locally recomputable number.
   S-box built from FIPS-197 definition (inverse in GF(2^8) mod 0x11B, then the
   fixed affine map), and cross-checked against the CPU's own AESENCLAST. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <wmmintrin.h>

static uint8_t gmul(uint8_t a, uint8_t b){
  uint8_t r=0; while(b){ if(b&1) r^=a; b>>=1; a = (a<<1) ^ ((a&0x80)?0x1b:0); }
  return r;
}
static uint8_t ginv(uint8_t a){ if(!a) return 0; for(int i=1;i<256;i++) if(gmul(a,(uint8_t)i)==1) return (uint8_t)i; return 0; }
static uint8_t rotl8(uint8_t x,int n){ return (uint8_t)((x<<n)|(x>>(8-n))); }

/* GF(2) rank of an r x c bit matrix stored as rows of uint64 words */
#define MAXW 32
static int rank_gf2(uint64_t *M, int rows, int cols){
  int W=(cols+63)/64, r=0;
  for(int c=0;c<cols && r<rows;c++){
    int w=c/64, b=c%64, piv=-1;
    for(int i=r;i<rows;i++) if((M[(size_t)i*W+w]>>b)&1ULL){ piv=i; break; }
    if(piv<0) continue;
    for(int w2=0;w2<W;w2++){ uint64_t t=M[(size_t)r*W+w2]; M[(size_t)r*W+w2]=M[(size_t)piv*W+w2]; M[(size_t)piv*W+w2]=t; }
    for(int i=0;i<rows;i++){ if(i!=r && ((M[(size_t)i*W+w]>>b)&1ULL))
        for(int w2=0;w2<W;w2++) M[(size_t)i*W+w2]^=M[(size_t)r*W+w2]; }
    r++;
  }
  return r;
}

int main(void){
  uint8_t S[256];
  for(int x=0;x<256;x++){ uint8_t b=ginv((uint8_t)x);
    S[x]= b ^ rotl8(b,1) ^ rotl8(b,2) ^ rotl8(b,3) ^ rotl8(b,4) ^ 0x63; }

  /* cross-check against the CPU: AESENCLAST(state,0) = ShiftRows(SubBytes(state)).
     byte 0 of the state is fixed by ShiftRows, so out[0] == S(in[0]). */
  int mism=0;
  for(int x=0;x<256;x++){
    uint8_t in[16]; memset(in,0,16); in[0]=(uint8_t)x;
    __m128i s=_mm_loadu_si128((__m128i*)in);
    s=_mm_aesenclast_si128(s,_mm_setzero_si128());
    uint8_t o[16]; _mm_storeu_si128((__m128i*)o,s);
    if(o[0]!=S[x]) mism++;
  }
  printf("SBOX_SELFCHECK aesenclast_mismatches=%d  S(00)=%02x S(01)=%02x S(53)=%02x\n",mism,S[0],S[1],S[0x53]);
  if(mism){ printf("SBOX DERIVATION FAILED - abort\n"); return 1; }

  /* variables: v0..v7 = input bits x (LSB first), v8..v15 = output bits y */
  /* ---- degree<=2 monomial space over 16 vars: 1 + 16 + 120 = 137 ---- */
  {
    int cols=137; int W=(cols+63)/64;
    static uint64_t M[256*3];
    memset(M,0,sizeof(M));
    for(int x=0;x<256;x++){
      int v[16];
      for(int i=0;i<8;i++) v[i]=(x>>i)&1;
      for(int i=0;i<8;i++) v[8+i]=(S[x]>>i)&1;
      int c=0; uint64_t *row=&M[(size_t)x*W];
      row[0]|=1ULL; c=1;                                    /* constant */
      for(int i=0;i<16;i++,c++) if(v[i]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<16;i++) for(int j=i+1;j<16;j++,c++) if(v[i]&v[j]) row[c/64]|=1ULL<<(c%64);
    }
    int rk=rank_gf2(M,256,cols);
    printf("DEG2_ALL       monomials=%d  rank=%d  independent_equations=%d\n",cols,rk,cols-rk);
  }
  /* ---- bi-affine subspace: 1 + 8x + 8y + 64 xy = 81 ---- */
  {
    int cols=81; int W=(cols+63)/64;
    static uint64_t M[256*2];
    memset(M,0,sizeof(M));
    for(int x=0;x<256;x++){
      int xb[8],yb[8];
      for(int i=0;i<8;i++){ xb[i]=(x>>i)&1; yb[i]=(S[x]>>i)&1; }
      int c=0; uint64_t *row=&M[(size_t)x*W];
      row[0]|=1ULL; c=1;
      for(int i=0;i<8;i++,c++) if(xb[i]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<8;i++,c++) if(yb[i]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<8;i++) for(int j=0;j<8;j++,c++) if(xb[i]&yb[j]) row[c/64]|=1ULL<<(c%64);
    }
    int rk=rank_gf2(M,256,cols);
    printf("DEG2_BIAFFINE  monomials=%d  rank=%d  independent_equations=%d\n",cols,rk,cols-rk);
  }
  /* ---- degree<=3: 1+16+120+560 = 697 ---- */
  {
    int cols=697; int W=(cols+63)/64;
    uint64_t *M=calloc((size_t)256*W,8);
    for(int x=0;x<256;x++){
      int v[16];
      for(int i=0;i<8;i++) v[i]=(x>>i)&1;
      for(int i=0;i<8;i++) v[8+i]=(S[x]>>i)&1;
      int c=0; uint64_t *row=&M[(size_t)x*W];
      row[0]|=1ULL; c=1;
      for(int i=0;i<16;i++,c++) if(v[i]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<16;i++) for(int j=i+1;j<16;j++,c++) if(v[i]&v[j]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<16;i++) for(int j=i+1;j<16;j++) for(int k=j+1;k<16;k++,c++)
        if(v[i]&v[j]&v[k]) row[c/64]|=1ULL<<(c%64);
    }
    int rk=rank_gf2(M,256,cols);
    printf("DEG3_ALL       monomials=%d  rank=%d  independent_equations=%d\n",cols,rk,cols-rk);
    free(M);
  }
  /* ---- null control: a uniformly random bijection on 8 bits, same statistics ---- */
  {
    uint8_t P[256]; for(int i=0;i<256;i++) P[i]=(uint8_t)i;
    uint64_t s=88172645463325252ULL;
    for(int i=255;i>0;i--){ s^=s<<13; s^=s>>7; s^=s<<17; int j=(int)(s%(uint64_t)(i+1)); uint8_t t=P[i];P[i]=P[j];P[j]=t; }
    int cols=137; int W=(cols+63)/64;
    static uint64_t M[256*3]; memset(M,0,sizeof(M));
    for(int x=0;x<256;x++){
      int v[16];
      for(int i=0;i<8;i++) v[i]=(x>>i)&1;
      for(int i=0;i<8;i++) v[8+i]=(P[x]>>i)&1;
      int c=0; uint64_t *row=&M[(size_t)x*W];
      row[0]|=1ULL; c=1;
      for(int i=0;i<16;i++,c++) if(v[i]) row[c/64]|=1ULL<<(c%64);
      for(int i=0;i<16;i++) for(int j=i+1;j<16;j++,c++) if(v[i]&v[j]) row[c/64]|=1ULL<<(c%64);
    }
    int rk=rank_gf2(M,256,cols);
    printf("NULL_RANDBIJ_DEG2 monomials=%d rank=%d independent_equations=%d\n",cols,rk,cols-rk);
  }
  return 0;
}
