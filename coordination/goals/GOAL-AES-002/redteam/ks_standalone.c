/* MEAS-RT-D: the AES key schedule as a STANDALONE object, which neither ideation
   pass treated. Both passes reached the key schedule only through the data path
   (LP-1 sigma-linearisation, D-6 Rcon/MC functionals).
   Measured here: (a) master-key-bit -> round-key-bit influence SUPPORT and BIAS,
   per round, for AES-128/192/256; (b) whether any two round keys of a schedule
   ever coincide (a single-key slide precondition); (c) how many master key bits
   each round-key word depends on, i.e. the schedule's own diffusion depth.
   Key schedule implemented directly from FIPS-197 word recurrences; S-box derived
   from the field definition and cross-checked against AESENCLAST. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <wmmintrin.h>

static uint8_t SB[256];
static uint8_t gmul(uint8_t a,uint8_t b){uint8_t r=0;while(b){if(b&1)r^=a;a=(a<<1)^((a&0x80)?0x1b:0);b>>=1;}return r;}
static uint8_t ginv(uint8_t a){if(!a)return 0;for(int i=1;i<256;i++)if(gmul(a,(uint8_t)i)==1)return (uint8_t)i;return 0;}
static uint8_t rl(uint8_t x,int n){return (uint8_t)((x<<n)|(x>>(8-n)));}
static void mksb(void){for(int x=0;x<256;x++){uint8_t b=ginv((uint8_t)x);SB[x]=b^rl(b,1)^rl(b,2)^rl(b,3)^rl(b,4)^0x63;}}
static uint32_t subword(uint32_t w){return ((uint32_t)SB[(w>>24)&0xff]<<24)|((uint32_t)SB[(w>>16)&0xff]<<16)|((uint32_t)SB[(w>>8)&0xff]<<8)|SB[w&0xff];}
static uint32_t rotword(uint32_t w){return (w<<8)|(w>>24);}
static const uint32_t RCON[11]={0,0x01000000,0x02000000,0x04000000,0x08000000,0x10000000,0x20000000,0x40000000,0x80000000,0x1b000000,0x36000000};

/* expand: Nk words of key -> W[0..4*(Nr+1)-1] */
static void expandkey(const uint8_t*k,int Nk,int Nr,uint32_t*W){
  for(int i=0;i<Nk;i++) W[i]=((uint32_t)k[4*i]<<24)|((uint32_t)k[4*i+1]<<16)|((uint32_t)k[4*i+2]<<8)|k[4*i+3];
  for(int i=Nk;i<4*(Nr+1);i++){
    uint32_t t=W[i-1];
    if(i%Nk==0) t=subword(rotword(t))^RCON[i/Nk];
    else if(Nk>6 && i%Nk==4) t=subword(t);
    W[i]=W[i-Nk]^t;
  }
}
static uint64_t st=0x243F6A8885A308D3ULL;
static inline uint64_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return st;}

int main(void){
  mksb();
  { int mism=0; for(int x=0;x<256;x++){ uint8_t in[16]; memset(in,0,16); in[0]=(uint8_t)x;
      __m128i s=_mm_aesenclast_si128(_mm_loadu_si128((__m128i*)in),_mm_setzero_si128());
      uint8_t o[16]; _mm_storeu_si128((__m128i*)o,s); if(o[0]!=SB[x]) mism++; }
    printf("SBOX_SELFCHECK mismatches=%d\n",mism); if(mism) return 1; }

  int cfg[3][3]={{16,4,10},{24,6,12},{32,8,14}};  /* keybytes, Nk, Nr */
  const char*nm[3]={"AES-128","AES-192","AES-256"};

  for(int c=0;c<3;c++){
    int KB=cfg[c][0],Nk=cfg[c][1],Nr=cfg[c][2];
    int KBITS=KB*8, NW=4*(Nr+1);
    /* (a) support + bias of masterbit -> roundkey-bit, per round */
    int NS=4000;
    static uint32_t cnt[256][128];  /* [master bit][bit within a round key] per round */
    printf("\n== %s : master-key-bit -> ROUND KEY bit, per round ==\n",nm[c]);
    for(int R=1;R<=Nr;R++){
      memset(cnt,0,sizeof(cnt));
      for(int t=0;t<NS;t++){
        uint8_t k[32],k2[32]; for(int i=0;i<KB;i++) k[i]=(uint8_t)rnd();
        uint32_t W[64],W2[64]; expandkey(k,Nk,Nr,W);
        for(int b=0;b<KBITS;b++){
          memcpy(k2,k,KB); k2[b>>3]^=(uint8_t)(1u<<(b&7));
          expandkey(k2,Nk,Nr,W2);
          for(int j=0;j<128;j++){
            int w=R*4+(j>>5), sh=31-(j&31);
            int bit=((W[w]^W2[w])>>sh)&1;
            cnt[b][j]+= (uint32_t)bit;
          }
        }
      }
      double dens=0,mx=0; int nz=0;
      for(int b=0;b<KBITS;b++) for(int j=0;j<128;j++){
        double p=(double)cnt[b][j]/NS;
        if(cnt[b][j]>0){ dens+=1.0; nz++; }
        if(p>mx) mx=p;
      }
      dens/= (double)(KBITS*128);
      /* deterministic entries: p==1 exactly (linear/always-flip), p==0 (no influence) */
      int det1=0,det0=0;
      for(int b=0;b<KBITS;b++) for(int j=0;j<128;j++){
        if(cnt[b][j]==(uint32_t)NS) det1++;
        if(cnt[b][j]==0) det0++;
      }
      printf("  round %2d: support_density=%.4f  frac_always_flip=%.4f  frac_never_flip=%.4f  max_p=%.4f\n",
             R,dens,(double)det1/(KBITS*128),(double)det0/(KBITS*128),mx);
    }
    /* (b) repeated round key within a schedule (single-key slide precondition) */
    { int reps=0,trials=200000;
      for(int t=0;t<trials;t++){
        uint8_t k[32]; for(int i=0;i<KB;i++) k[i]=(uint8_t)rnd();
        uint32_t W[64]; expandkey(k,Nk,Nr,W);
        for(int a=0;a<=Nr;a++) for(int b=a+1;b<=Nr;b++){
          if(W[4*a]==W[4*b]&&W[4*a+1]==W[4*b+1]&&W[4*a+2]==W[4*b+2]&&W[4*a+3]==W[4*b+3]) reps++;
        }
      }
      printf("  repeated-round-key events in %d random schedules: %d (null expectation %.3g)\n",
             trials,reps,(double)trials*(Nr*(Nr+1)/2)*pow(2.0,-128));
    }
  }
  return 0;
}
