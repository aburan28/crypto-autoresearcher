/* nibble_decay.c — TASK-20260804-d7d0ec, GOAL-AES-003 BATCH-713991
 *
 * THE ZERO-ENTRY DECAY CONTROL, in the nibble form the red team specified
 * (RC-1 / counterexample_or_mutation): a 4x4-nibble AES-shaped SPN over
 * GF(2^4), x^4+x+1, on the same geometry as the BATCH-001 validator's scaled
 * analogue (TASK-VALIDATION-001/mini.c conventions):
 *   - cell index = 4*col+row
 *   - ShiftRows: row t rotates left by t
 *   - MixColumns: column-preserving, matrix MCM (parameterised)
 *   - last round WITHOUT MixColumns (C1)
 *   - independent uniform round keys (derivation uses no key schedule)
 *   - full 2^16 diagonal coset D_0 = cells {0,5,10,15}
 *   - projection ID_{j0} = {4*((j0-t)%4)+t}, packed to 16 bits
 *   - statistic n = sum_v C(cnt[v],2), occupancy histogram over 2^16 buckets
 *
 * Matrix parameter: "M1"  = the campaign's byte-scale zero-entry matrix
 *                          [[0,3,1,1],[1,2,3,0],[1,1,0,3],[3,0,1,2]] over
 *                          GF(2^4) — four zeros, the maximally adversarial
 *                          case at j0=0 (all four r=4-critical entries zero).
 *                   "CTRL" = circulant (2,3,1,1) over GF(2^4) — the
 *                          no-zero-entry control (AES-MixColumns analogue).
 *
 * STARTUP VERIFICATION (own Gauss-Jordan over GF(2^4)): computes determinant,
 * rank and explicit inverse of the exact matrix used, checks M * M^-1 = I,
 * and REFUSES to run if singular. This is the item the BATCH-001 validator
 * recorded as not_executed because its substitute circulant (2,3,0,1) was
 * singular; that failure is not repeated here.
 *
 * Output: one JSON object per trial on stdout (JSONL), then a summary line.
 * Per trial: n, n_mod8, n_mod16, max_occ, the sparse occupancy histogram
 * {occ: count}, and whether every nonzero occupancy is a multiple of 16
 * (the nibble analogue of the GF(2^8) multiple-of-256 fiber signature).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static uint8_t S[16], MCM[4][4];
static uint8_t RKc[12][16];
static uint64_t rs;
static uint32_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (uint32_t)rs; }

static uint8_t gmul(uint8_t a,uint8_t b){ /* GF(2^4), x^4+x+1 */
  uint8_t p=0; for(int i=0;i<4;i++){ if(b&1)p^=a; uint8_t hi=a&8; a=(a<<1)&0xf; if(hi)a^=0x3; b>>=1; }
  return p; }

static uint8_t ginv(uint8_t a){ for(uint8_t z=1;z<16;z++) if(gmul(a,z)==1) return z; return 0; }

/* Gauss-Jordan over GF(2^4) on a 4x4 matrix. Returns rank; fills det and
 * (if rank==4) inv. Verifies M*M^-1 == I. */
static int gauss_jordan(const uint8_t M[4][4], uint8_t *det, uint8_t inv[4][4]){
  uint8_t A[4][8];
  for(int i=0;i<4;i++){ for(int j=0;j<4;j++) A[i][j]=M[i][j];
    for(int j=0;j<4;j++) A[i][4+j]=(i==j)?1:0; }
  uint8_t d=1; int rank=0;
  for(int c=0;c<4;c++){
    int p=-1; for(int i=rank;i<4;i++) if(A[i][c]){p=i;break;}
    if(p<0){ *det=0; return rank; }
    if(p!=rank){ for(int k=0;k<8;k++){uint8_t z=A[rank][k];A[rank][k]=A[p][k];A[p][k]=z;} }
    uint8_t iv=ginv(A[rank][c]);
    d=gmul(d,A[rank][c]);
    for(int k=0;k<8;k++) A[rank][k]=gmul(A[rank][k],iv);
    for(int i=0;i<4;i++) if(i!=rank && A[i][c]){
      uint8_t f=A[i][c];
      for(int k=0;k<8;k++) A[i][k]^=gmul(f,A[rank][k]);
    }
    rank++;
  }
  *det=d;
  if(inv) for(int i=0;i<4;i++) for(int j=0;j<4;j++) inv[i][j]=A[i][4+j];
  return rank;
}

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
  if(argc<6){ fprintf(stderr,"usage: %s <M1|CTRL> <r> <j0> <seed> <trials> [rand_sbox]\n",argv[0]); return 2; }
  const char *mat = argv[1];
  int r=atoi(argv[2]); int j0=atoi(argv[3]); uint64_t seed=strtoull(argv[4],0,10);
  int trials=atoi(argv[5]); int randsbox=(argc>6)?atoi(argv[6]):0;

  /* ---- matrix selection ---- */
  uint8_t M1[4][4] = {{0,3,1,1},{1,2,3,0},{1,1,0,3},{3,0,1,2}};
  uint8_t CTRL[4][4]={{2,3,1,1},{1,2,3,1},{1,1,2,3},{3,1,1,2}};
  uint8_t (*M)[4] = (strcmp(mat,"M1")==0)?M1:(strcmp(mat,"CTRL")==0)?CTRL:NULL;
  if(!M){ fprintf(stderr,"unknown matrix %s\n",mat); return 2; }
  memcpy(MCM,M,16);

  /* ---- own Gauss-Jordan verification: det, rank, inverse, M*M^-1=I ---- */
  uint8_t det=0, inv[4][4];
  int rank = gauss_jordan(M,&det,inv);
  int is_identity=1;
  for(int i=0;i<4 && is_identity;i++) for(int j=0;j<4;j++){
    uint8_t acc=0; for(int k=0;k<4;k++) acc^=gmul(M[i][k],inv[k][j]);
    if(acc!=(i==j?1:0)) is_identity=0;
  }
  printf("{\"matrix\":\"%s\",\"rank\":%d,\"det\":%d,\"non_singular\":%s,\"M_times_Minv_is_identity\":%s,\"inverse\":[",
         mat,rank,det,rank==4?"true":"false",is_identity?"true":"false");
  for(int i=0;i<4;i++){ printf("["); for(int j=0;j<4;j++) printf("%d%s",inv[i][j],j<3?",":""); printf("]%s",i<3?",":""); }
  printf("]}\n");
  if(rank!=4 || !is_identity){ printf("{\"error\":\"matrix singular or inverse check failed; refusing to run\"}\n"); return 1; }

  int pidx[4]; for(int t=0;t<4;t++) pidx[t]=4*(((j0-t)%4+4)%4)+t;
  int n0mod8=0, nz=0, ntot=0, all16=0;
  for(int tr=0;tr<trials;tr++){
    rs = seed + (uint64_t)tr*2654435761u;
    for(int i=0;i<16;i++) S[i]=i;
    if(randsbox){ for(int i=15;i>0;i--){ int j=rnd()%(i+1); uint8_t z=S[i];S[i]=S[j];S[j]=z; } }
    else { uint8_t aessub[16]={0x6,0xb,0x5,0x4,0x2,0xe,0x7,0xa,0x9,0xd,0xf,0xc,0x3,0x1,0x0,0x8};
           memcpy(S,aessub,16); }
    for(int i=0;i<12;i++) for(int k=0;k<16;k++) RKc[i][k]=rnd()&0xf;
    uint8_t base[16]; for(int k=0;k<16;k++) base[k]=rnd()&0xf;
    memset(cnt,0,sizeof cnt);
    int dcell[4]={0,5,10,15};
    uint32_t LIM = 1u<<16;
    for(uint32_t x=0;x<LIM;x++){
      uint8_t s[16]; memcpy(s,base,16);
      for(int t=0;t<4;t++) s[dcell[t]]=(x>>(4*t))&0xf;
      enc(s,r);
      uint32_t v=0; for(int t=0;t<4;t++) v|=(uint32_t)s[pidx[t]]<<(4*t);
      cnt[v]++;
    }
    unsigned long long n=0,N=0;
    for(uint32_t v=0;v<65536;v++){ N+=cnt[v]; n+=(unsigned long long)cnt[v]*(cnt[v]-1)/2; }
    if(N!=LIM){ printf("{\"error\":\"N mismatch\"}\n"); return 1; }
    /* sparse occupancy histogram {occ: count} */
    uint32_t occ_hist[65537]; memset(occ_hist,0,sizeof occ_hist);
    uint32_t max_occ=0;
    for(uint32_t v=0;v<65536;v++){ occ_hist[cnt[v]]++; if(cnt[v]>max_occ) max_occ=cnt[v]; }
    int mult16=1;
    for(uint32_t o=1;o<=max_occ;o++) if(occ_hist[o] && (o%16)!=0) mult16=0;
    ntot++; if(n%8==0) n0mod8++; if(n!=0) nz++; if(mult16) all16++;
    printf("{\"trial\":%d,\"seed\":%llu,\"n\":%llu,\"n_mod8\":%llu,\"n_mod16\":%llu,\"max_occ\":%u,\"all_occ_multiple_of_16\":%d,\"occ_hist\":{",
           tr,(unsigned long long)(seed+(uint64_t)tr*2654435761u),n,n%8,n%16,max_occ,mult16);
    int first=1;
    for(uint32_t o=1;o<=max_occ;o++) if(occ_hist[o]){ printf("%s\"%u\":%u",first?"":",",o,occ_hist[o]); first=0; }
    printf("}}\n");
  }
  printf("{\"summary\":{\"matrix\":\"%s\",\"r\":%d,\"j0\":%d,\"rand_sbox\":%d,\"trials\":%d,\"trials_n_0mod8\":%d,\"trials_n_eq_0\":%d,\"trials_all_occ_multiple_of_16\":%d}}\n",
         mat,r,j0,randsbox,ntot,n0mod8,ntot-nz,all16);
  return 0;
}