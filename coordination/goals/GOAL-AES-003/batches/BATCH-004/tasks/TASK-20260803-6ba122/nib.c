/* TASK-20260803-6ba122 : nibble-SPN collision counter with FULL occupancy histograms.
 *
 * Written from scratch for this task.  Geometry read from BATCH-001's mini.c as a
 * specification (4x4 nibble state, ShiftRows row-t rotate, column-preserving
 * MixColumns over GF(2^4) mod x^4+x+1, independent uniform round keys, no key
 * schedule).  Emits JSON on stdout: one object per arm.
 *
 * Usage: nib <r> <j0> <seed> <randsbox> <trials> <layer>
 *   layer: 0 = NZ (no zero entry), 1 = Z1 (one zero), 4 = Z4 (four zeros)
 *
 * Counters: fiber counts are uint32 (max possible 65536, no overflow possible);
 * n is unsigned long long (max C(65536,2) = 2147450880, fits).  The engine
 * asserts sum(counts) == 2^16 and asserts no fiber count exceeds 65536.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static uint8_t S[16], M[4][4];
static uint8_t RK[16][16];
static uint8_t MT[16][16];      /* MT[a][b] = a*b over GF(2^4) */
static uint64_t rs;
static uint32_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (uint32_t)(rs>>11); }

static uint8_t gmul(uint8_t a,uint8_t b){
  uint8_t p=0;
  for(int i=0;i<4;i++){ if(b&1) p^=a; uint8_t hi=a&8; a=(uint8_t)((a<<1)&0xf); if(hi) a^=0x3; b>>=1; }
  return p;
}

/* cell index = 4*col + row */
static void round_fn(uint8_t*s,const uint8_t*rk,int last){
  uint8_t a[16],b[16];
  for(int i=0;i<16;i++) a[i]=S[s[i]];
  for(int c=0;c<4;c++) for(int t=0;t<4;t++) b[4*c+t]=a[4*((c+t)&3)+t];
  if(!last){
    for(int c=0;c<4;c++){ uint8_t col[4];
      for(int i=0;i<4;i++){ uint8_t v=0; for(int t=0;t<4;t++) v^=MT[M[i][t]][b[4*c+t]]; col[i]=v; }
      for(int i=0;i<4;i++) b[4*c+i]=col[i]; }
  }
  for(int i=0;i<16;i++) s[i]=b[i]^rk[i];
}
static void enc(uint8_t*s,int r){
  for(int i=0;i<16;i++) s[i]^=RK[0][i];
  for(int i=1;i<r;i++) round_fn(s,RK[i],0);
  round_fn(s,RK[r],1);
}

static uint32_t cnt[1<<16];
/* occupancy histogram: fiber size -> how many projection values have it */
static uint32_t occhist[65537];

int main(int argc,char**argv){
  if(argc<7){ fprintf(stderr,"usage: nib r j0 seed randsbox trials layer\n"); return 2; }
  int r=atoi(argv[1]), j0=atoi(argv[2]);
  uint64_t seed=strtoull(argv[3],0,10);
  int randsbox=atoi(argv[4]), trials=atoi(argv[5]), layer=atoi(argv[6]);

  for(int a=0;a<16;a++) for(int b=0;b<16;b++) MT[a][b]=gmul((uint8_t)a,(uint8_t)b);

  uint8_t row[4]={2,3,1,1};
  for(int i=0;i<4;i++) for(int t=0;t<4;t++) M[i][t]=row[((t-i)%4+4)%4];
  const char*lname="NZ";
  if(layer==1){ M[0][0]=0; lname="Z1"; }
  else if(layer==4){ M[0][0]=0; M[1][3]=0; M[2][2]=0; M[3][1]=0; lname="Z4"; }
  else if(layer!=0){ printf("{\"error\":\"bad layer\"}\n"); return 3; }

  /* in-engine non-singularity gate (independent of gf16_verify.py) */
  { uint8_t A[4][4]; memcpy(A,M,16); int rank=0; uint8_t det=1;
    for(int c=0;c<4;c++){ int p=-1; for(int i=rank;i<4;i++) if(A[i][c]){p=i;break;}
      if(p<0){ det=0; continue; }
      if(p!=rank) for(int k=0;k<4;k++){ uint8_t z=A[p][k];A[p][k]=A[rank][k];A[rank][k]=z; }
      uint8_t piv=A[rank][c], iv=0; for(uint8_t z=1;z<16;z++) if(MT[piv][z]==1){iv=z;break;}
      det=MT[det][piv];
      for(int k=0;k<4;k++) A[rank][k]=MT[A[rank][k]][iv];
      for(int i=0;i<4;i++) if(i!=rank&&A[i][c]){ uint8_t f=A[i][c];
        for(int k=0;k<4;k++) A[i][k]^=MT[f][A[rank][k]]; }
      rank++; }
    if(rank!=4){ printf("{\"error\":\"MIXING LAYER SINGULAR\",\"layer\":\"%s\",\"rank\":%d}\n",lname,rank); return 4; }
    fprintf(stderr,"engine matrix gate: layer=%s rank=%d det=%u OK\n",lname,rank,det);
  }

  rs = seed ? seed : 88172645463325252ull;
  for(int w=0;w<64;w++) rnd();   /* warm up xorshift */

  int pidx[4]; for(int t=0;t<4;t++) pidx[t]=4*(((j0-t)%4+4)%4)+t;
  int dcell[4]={0,5,10,15};

  printf("{\"r\":%d,\"j0\":%d,\"layer\":\"%s\",\"layer_code\":%d,\"seed\":%llu,"
         "\"rand_sbox\":%d,\"trials\":%d,\"matrix\":[",
         r,j0,lname,layer,(unsigned long long)seed,randsbox,trials);
  for(int i=0;i<4;i++){ printf("%s[%u,%u,%u,%u]",i?",":"",M[i][0],M[i][1],M[i][2],M[i][3]); }
  printf("],\"trial_results\":[");

  int n0mod8=0, nzero=0, invalid=0;
  for(int tr=0;tr<trials;tr++){
    for(int i=0;i<16;i++) S[i]=(uint8_t)i;
    if(randsbox){ for(int i=15;i>0;i--){ int j=(int)(rnd()%(uint32_t)(i+1)); uint8_t z=S[i];S[i]=S[j];S[j]=z; } }
    else { uint8_t aessub[16]={0x6,0xb,0x5,0x4,0x2,0xe,0x7,0xa,0x9,0xd,0xf,0xc,0x3,0x1,0x0,0x8};
           memcpy(S,aessub,16); }
    for(int i=0;i<16;i++) for(int k=0;k<16;k++) RK[i][k]=(uint8_t)(rnd()&0xf);
    uint8_t base[16]; for(int k=0;k<16;k++) base[k]=(uint8_t)(rnd()&0xf);

    memset(cnt,0,sizeof cnt);
    for(uint32_t x=0;x<65536u;x++){
      uint8_t s[16]; memcpy(s,base,16);
      for(int t=0;t<4;t++) s[dcell[t]]=(uint8_t)((x>>(4*t))&0xf);
      enc(s,r);
      uint32_t v=0; for(int t=0;t<4;t++) v|=(uint32_t)s[pidx[t]]<<(4*t);
      cnt[v]++;
    }
    memset(occhist,0,sizeof occhist);
    unsigned long long n=0, N=0; uint32_t maxocc=0; unsigned long long g=0;
    for(uint32_t v=0;v<65536u;v++){
      uint32_t c=cnt[v];
      N+=c; occhist[c]++;
      if(c>maxocc) maxocc=c;
      n += (unsigned long long)c*(unsigned long long)(c-1)/2ull;
      if(c){ unsigned long long a=g,b=c; while(b){unsigned long long t2=a%b;a=b;b=t2;} g=a; }
    }
    int ok = (N==65536ull) && (maxocc<=65536u);
    if(!ok) invalid++;
    if(n%8==0) n0mod8++;
    if(n==0) nzero++;
    /* divisibility signature */
    int all_div16 = (g%16ull==0);
    printf("%s{\"trial\":%d,\"n\":%llu,\"n_mod8\":%llu,\"n_mod16\":%llu,\"max_occ\":%u,"
           "\"N_check\":%llu,\"N_ok\":%s,\"gcd_nonzero_fibers\":%llu,\"all_fibers_div16\":%s,\"hist\":{",
           tr?",":"",tr,n,n%8ull,n%16ull,maxocc,N,ok?"true":"false",g,all_div16?"true":"false");
    int first=1;
    for(uint32_t c=0;c<=maxocc;c++) if(occhist[c]){ printf("%s\"%u\":%u",first?"":",",c,occhist[c]); first=0; }
    printf("}}");
    fflush(stdout);
  }
  printf("],\"summary\":{\"trials\":%d,\"trials_n_0mod8\":%d,\"trials_n_eq_0\":%d,"
         "\"invalid_trials\":%d}}\n", trials,n0mod8,nzero,invalid);
  return invalid?5:0;
}
