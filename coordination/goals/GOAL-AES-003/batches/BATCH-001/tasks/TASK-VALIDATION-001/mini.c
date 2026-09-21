/* VALIDATOR: scaled-down structural test of the count5 derivation.
 * 4x4 state of NIBBLES (64-bit block), same ShiftRows/MixColumns geometry as
 * AES.  The count5 derivation uses only: (a) S bijective on cells,
 * (b) MixColumns column-preserving with NO ZERO ENTRIES, (c) SR row-t rotate.
 * It uses NO property of the AES S-box and NO key schedule.  Therefore it
 * predicts, for THIS cipher too:
 *     n_4 = 0 exactly ;  n_5 = 0 mod 8 ;  n_6 not forced.
 * and predicts the SAME for a RANDOM bijective S-box (component null).
 * Coset = all 2^16 values of the plaintext diagonal D_0 = cells {0,5,10,15}.
 * Projection = cells ID_j0 = {4*((j0-t)%4)+t}, packed to 16 bits.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static uint8_t S[16], MCM[4][4];
static uint8_t RKc[12][16];     /* round keys as 16 nibbles, independent */
static uint64_t rs;
static uint32_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (uint32_t)rs; }

static uint8_t gmul(uint8_t a,uint8_t b){ /* GF(2^4), x^4+x+1 */
  uint8_t p=0; for(int i=0;i<4;i++){ if(b&1)p^=a; uint8_t hi=a&8; a=(a<<1)&0xf; if(hi)a^=0x3; b>>=1; }
  return p; }

static void round_fn(uint8_t*s,const uint8_t*rk,int last){
  uint8_t a[16],b[16];
  for(int i=0;i<16;i++) a[i]=S[s[i]];
  /* ShiftRows: row t rotate left by t. cell index = 4*col+row */
  for(int c=0;c<4;c++) for(int t=0;t<4;t++) b[4*c+t]=a[4*((c+t)&3)+t];
  if(!last){
    for(int c=0;c<4;c++){ uint8_t col[4];
      for(int i=0;i<4;i++){ uint8_t v=0; for(int t=0;t<4;t++) v^=gmul(MCM[i][t],b[4*c+t]); col[i]=v; }
      for(int i=0;i<4;i++) b[4*c+i]=col[i]; }
  }
  for(int i=0;i<16;i++) s[i]=b[i]^rk[i];
}
static void enc(uint8_t*s,int r){
  for(int i=0;i<16;i++) s[i]^=RKc[0][i];
  for(int i=1;i<r;i++) round_fn(s,RKc[i],0);
  round_fn(s,RKc[r],1);
}

static uint32_t cnt[1<<16];

int main(int argc,char**argv){
  int r=atoi(argv[1]); int j0=atoi(argv[2]); uint64_t seed=strtoull(argv[3],0,10);
  int randsbox=atoi(argv[4]); int trials=atoi(argv[5]);
  int nfree = (argc>6)?atoi(argv[6]):4;      /* free diagonal cells: 4 = full coset */
  int mczero = (argc>7)?atoi(argv[7]):0;      /* 1 = put a ZERO entry in MixColumns */
  rs=seed?seed:88172645463325252ull;
  /* AES-shaped circulant [2,3,1,1] over GF(2^4): no zero entries */
  uint8_t row[4]={2,3,1,1};
  /* mczero handled after MCM build */
  for(int i=0;i<4;i++) for(int t=0;t<4;t++) MCM[i][t]=row[(t-i+4)&3];
  if(mczero){ uint8_t r2[4]={2,3,0,1}; for(int i=0;i<4;i++) for(int t=0;t<4;t++) MCM[i][t]=r2[(t-i+4)&3]; }
  /* verify invertible by brute force on the 4x4 GF(16) matrix (det via Gauss) */
  {
    uint8_t M[4][4]; memcpy(M,MCM,16); int sing=0;
    for(int c=0;c<4;c++){ int p=-1; for(int i=c;i<4;i++) if(M[i][c]){p=i;break;}
      if(p<0){sing=1;break;} if(p!=c){ for(int k=0;k<4;k++){uint8_t z=M[c][k];M[c][k]=M[p][k];M[p][k]=z;} }
      uint8_t inv=0; for(uint8_t z=1;z<16;z++) if(gmul(M[c][c],z)==1){inv=z;break;}
      for(int k=0;k<4;k++) M[c][k]=gmul(M[c][k],inv);
      for(int i=0;i<4;i++) if(i!=c&&M[i][c]){ uint8_t f=M[i][c];
        for(int k=0;k<4;k++) M[i][k]^=gmul(f,M[c][k]); } }
    if(sing){printf("{\"error\":\"MC singular\"}\n");return 1;}
  }
  int pidx[4]; for(int t=0;t<4;t++) pidx[t]=4*(((j0-t)%4+4)%4)+t;
  int nz=0, n0mod8=0, ntot=0;
  for(int tr=0;tr<trials;tr++){
    /* S-box */
    for(int i=0;i<16;i++) S[i]=i;
    if(randsbox){ for(int i=15;i>0;i--){ int j=rnd()%(i+1); uint8_t z=S[i];S[i]=S[j];S[j]=z; } }
    else { uint8_t aessub[16]={0x6,0xb,0x5,0x4,0x2,0xe,0x7,0xa,0x9,0xd,0xf,0xc,0x3,0x1,0x0,0x8};
           memcpy(S,aessub,16); }
    /* independent uniform round keys (derivation uses no key schedule) */
    for(int i=0;i<12;i++) for(int k=0;k<16;k++) RKc[i][k]=rnd()&0xf;
    uint8_t base[16]; for(int k=0;k<16;k++) base[k]=rnd()&0xf;
    memset(cnt,0,sizeof cnt);
    int dcell[4]={0,5,10,15};
    uint32_t LIM = 1u<<(4*nfree);
    for(uint32_t x=0;x<LIM;x++){
      uint8_t s[16]; memcpy(s,base,16);
      for(int t=0;t<nfree;t++) s[dcell[t]]=(x>>(4*t))&0xf;
      enc(s,r);
      uint32_t v=0; for(int t=0;t<4;t++) v|=(uint32_t)s[pidx[t]]<<(4*t);
      cnt[v]++;
    }
    unsigned long long n=0,N=0;
    for(uint32_t v=0;v<65536;v++){ N+=cnt[v]; n+=(unsigned long long)cnt[v]*(cnt[v]-1)/2; }
    if(N!=LIM){printf("{\"error\":\"N\"}\n");return 1;}
    ntot++; if(n%8==0) n0mod8++; if(n!=0) nz++;
    if(tr<6) printf("  trial %d: n=%llu  n_mod8=%llu  n_mod16=%llu\n",tr,n,n%8,n%16);
  }
  printf("{\"r\":%d,\"j0\":%d,\"rand_sbox\":%d,\"nfree\":%d,\"mczero\":%d,\"trials\":%d,\"trials_n_eq_0\":%d,\"trials_n_0mod8\":%d}\n",
     r,j0,randsbox,nfree,mczero,ntot,ntot-nz,n0mod8);
  return 0;
}
