// cnt.c -- TASK-20260802-142a4b counting engine.
// Written for this task. Its distinguishing feature relative to BATCH-001's
// count5.c is the software T-table engine with a CONFIGURABLE GF(2^8) mixing
// matrix; count5.c is AES-NI only and cannot vary the mixing layer at all.
// count5.c was read for its conventions (byte order, coset layout, projection
// index convention, the (sum m^2 - N)/2 cross-check); no code was copied.
//
// COUNTING KERNEL (authoritative description, corrected 2026-08-02T18:34Z):
// VALUE-PARTITIONED threads with PLAIN NON-ATOMIC increments. Every thread
// scans the whole 2^32 input space and increments only the slice of the value
// space it owns, so there are no data races and no atomics. An earlier version
// of this file partitioned the INPUT space and used atomic increments; it was
// replaced before any measurement was recorded and produced no result. That
// superseded design is described in RESULTS.json deviation D-2 and is NOT what
// this code does.
//
// Object: full 2^32 coset of D_0 (bytes 0,5,10,15 free), r-round AES-shaped SPN
// with the C1 convention (final round has no mixing layer), projection
// pi_{j0}(c) = bytes at ID_{j0} = {4*((j0-t) mod 4)+t : t=0..3}, byte t at bit 8t.
// Reports the occupancy histogram, N, and n = sum_v C(m_v,2) with the
// independent cross-check n_alt = (sum_v m_v^2 - N)/2.
//
// No RNG inside. All parameters are supplied on the command line.
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>
#include <wmmintrin.h>

static const uint8_t SBOX[256] = {
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16};

static uint8_t gmul(uint8_t a, uint8_t b){
  uint8_t p=0;
  for(int i=0;i<8;i++){
    if(b&1) p^=a;
    uint8_t hi=a&0x80; a<<=1; if(hi) a^=0x1b;
    b>>=1;
  }
  return p;
}

// ---- parameters ----
static int Rr, J0, ENG_SOFT, CW, WBITS, NTHREADS;
static uint32_t RKw[11][4];          // round keys as column words
static __m128i RKx[11];
static uint32_t base_cols[4];
static uint8_t MAT[4][4];            // mixing matrix, MAT[row][col]
static uint32_t T[4][256];           // T[j][x] = MAT[:,j]*S[x] packed
static uint8_t *cnt8; static uint16_t *cnt16;
static uint64_t ENTRIES; static uint32_t CURWIN, IDXMASK;
static uint64_t inwin_cnt[64];
static uint64_t *HIST;               // per-thread histograms
static uint64_t HBINS;

static void hex2b(const char*h,uint8_t*o,int n){for(int i=0;i<n;i++){unsigned v;sscanf(h+2*i,"%2x",&v);o[i]=(uint8_t)v;}}

static void keysched(const uint8_t*key){
  uint8_t rk[176]; memcpy(rk,key,16);
  uint8_t rcon=1;
  for(int i=16;i<176;i+=4){
    uint8_t t[4]={rk[i-4],rk[i-3],rk[i-2],rk[i-1]};
    if(i%16==0){
      uint8_t tmp=t[0];
      t[0]=(uint8_t)(SBOX[t[1]]^rcon); t[1]=SBOX[t[2]]; t[2]=SBOX[t[3]]; t[3]=SBOX[tmp];
      rcon=gmul(rcon,2);
    }
    for(int j=0;j<4;j++) rk[i+j]=rk[i-16+j]^t[j];
  }
  for(int r=0;r<11;r++){
    for(int c=0;c<4;c++)
      RKw[r][c]=(uint32_t)rk[16*r+4*c]|((uint32_t)rk[16*r+4*c+1]<<8)
               |((uint32_t)rk[16*r+4*c+2]<<16)|((uint32_t)rk[16*r+4*c+3]<<24);
    RKx[r]=_mm_loadu_si128((const __m128i*)(rk+16*r));
  }
}

static inline void enc_soft(uint32_t*c){
  c[0]^=RKw[0][0]; c[1]^=RKw[0][1]; c[2]^=RKw[0][2]; c[3]^=RKw[0][3];
  for(int i=1;i<Rr;i++){
    uint32_t n0,n1,n2,n3;
    n0=T[0][ c[0]&0xff]^T[1][(c[1]>>8)&0xff]^T[2][(c[2]>>16)&0xff]^T[3][(c[3]>>24)];
    n1=T[0][ c[1]&0xff]^T[1][(c[2]>>8)&0xff]^T[2][(c[3]>>16)&0xff]^T[3][(c[0]>>24)];
    n2=T[0][ c[2]&0xff]^T[1][(c[3]>>8)&0xff]^T[2][(c[0]>>16)&0xff]^T[3][(c[1]>>24)];
    n3=T[0][ c[3]&0xff]^T[1][(c[0]>>8)&0xff]^T[2][(c[1]>>16)&0xff]^T[3][(c[2]>>24)];
    c[0]=n0^RKw[i][0]; c[1]=n1^RKw[i][1]; c[2]=n2^RKw[i][2]; c[3]=n3^RKw[i][3];
  }
  uint32_t n0,n1,n2,n3;
  n0=(uint32_t)SBOX[c[0]&0xff]|((uint32_t)SBOX[(c[1]>>8)&0xff]<<8)|((uint32_t)SBOX[(c[2]>>16)&0xff]<<16)|((uint32_t)SBOX[(c[3]>>24)]<<24);
  n1=(uint32_t)SBOX[c[1]&0xff]|((uint32_t)SBOX[(c[2]>>8)&0xff]<<8)|((uint32_t)SBOX[(c[3]>>16)&0xff]<<16)|((uint32_t)SBOX[(c[0]>>24)]<<24);
  n2=(uint32_t)SBOX[c[2]&0xff]|((uint32_t)SBOX[(c[3]>>8)&0xff]<<8)|((uint32_t)SBOX[(c[0]>>16)&0xff]<<16)|((uint32_t)SBOX[(c[1]>>24)]<<24);
  n3=(uint32_t)SBOX[c[3]&0xff]|((uint32_t)SBOX[(c[0]>>8)&0xff]<<8)|((uint32_t)SBOX[(c[1]>>16)&0xff]<<16)|((uint32_t)SBOX[(c[2]>>24)]<<24);
  c[0]=n0^RKw[Rr][0]; c[1]=n1^RKw[Rr][1]; c[2]=n2^RKw[Rr][2]; c[3]=n3^RKw[Rr][3];
}

static inline uint32_t proj(const uint32_t*c){
  return (c[J0&3]&0xffu)|(c[(J0-1)&3]&0xff00u)|(c[(J0-2)&3]&0xff0000u)|(c[(J0-3)&3]&0xff000000u);
}

typedef struct{int tid;} arg_t;

static void*worker(void*ap){
  int tid=((arg_t*)ap)->tid;
  uint64_t lo=0, hi=1ull<<32;                       // every thread: full input scan
  uint64_t qspan=ENTRIES/NTHREADS;                  // this thread's value slice
  uint64_t qlo=(uint64_t)tid*qspan, qhi=qlo+qspan;
  uint64_t inw=0;
  uint32_t m0=base_cols[0]&~0xffu, m1=base_cols[1]&~0xff00u,
           m2=base_cols[2]&~0xff0000u, m3=base_cols[3]&~0xff000000u;
  if(ENG_SOFT){
    for(uint64_t a=lo;a<hi;a++){
      uint32_t c[4];
      c[0]=m0|(uint32_t)(a&0xff); c[1]=m1|(uint32_t)(a&0xff00);
      c[2]=m2|(uint32_t)(a&0xff0000); c[3]=m3|(uint32_t)(a&0xff000000);
      enc_soft(c);
      uint32_t v=proj(c);
      if(WBITS==0 || (v>>(32-WBITS))==CURWIN){
        uint32_t idx=v&IDXMASK;
        if((uint64_t)idx>=qlo && (uint64_t)idx<qhi){ inw++;
          if(CW==8) cnt8[idx]++; else cnt16[idx]++; }
      }
    }
  } else {
    for(uint64_t a=lo;a<hi;a+=8){
      __m128i p[8];
      for(int k=0;k<8;k++){
        uint64_t x=a+k;
        uint32_t c0=m0|(uint32_t)(x&0xff), c1=m1|(uint32_t)(x&0xff00),
                 c2=m2|(uint32_t)(x&0xff0000), c3=m3|(uint32_t)(x&0xff000000);
        p[k]=_mm_set_epi32((int)c3,(int)c2,(int)c1,(int)c0);
      }
      for(int k=0;k<8;k++) p[k]=_mm_xor_si128(p[k],RKx[0]);
      for(int i=1;i<Rr;i++) for(int k=0;k<8;k++) p[k]=_mm_aesenc_si128(p[k],RKx[i]);
      for(int k=0;k<8;k++) p[k]=_mm_aesenclast_si128(p[k],RKx[Rr]);
      for(int k=0;k<8;k++){
        uint32_t c[4]; _mm_storeu_si128((__m128i*)c,p[k]);
        uint32_t v=proj(c);
        if(WBITS==0 || (v>>(32-WBITS))==CURWIN){
          uint32_t idx=v&IDXMASK;
          if((uint64_t)idx>=qlo && (uint64_t)idx<qhi){ inw++;
            if(CW==8) cnt8[idx]++; else cnt16[idx]++; }
        }
      }
    }
  }
  inwin_cnt[tid]=inw;
  return NULL;
}

static void*histw(void*ap){
  int tid=((arg_t*)ap)->tid;
  uint64_t span=ENTRIES/NTHREADS, lo=(uint64_t)tid*span, hi=lo+span;
  uint64_t*h=HIST+(uint64_t)tid*HBINS;
  if(CW==8) for(uint64_t i=lo;i<hi;i++) h[cnt8[i]]++;
  else      for(uint64_t i=lo;i<hi;i++) h[cnt16[i]]++;
  return NULL;
}

int main(int argc,char**argv){
  // cnt <engine soft|aesni> <r> <j0> <key32hex> <base32hex> <matrix32hex> <cw> <wbits> <threads>
  if(argc<10){fprintf(stderr,"usage: cnt engine r j0 keyhex basehex matrixhex cw wbits threads\n");return 2;}
  ENG_SOFT = (strcmp(argv[1],"soft")==0);
  Rr=atoi(argv[2]); J0=atoi(argv[3]);
  uint8_t key[16],base[16],mm[16];
  hex2b(argv[4],key,16); hex2b(argv[5],base,16); hex2b(argv[6],mm,16);
  CW=atoi(argv[7]); WBITS=atoi(argv[8]); NTHREADS=atoi(argv[9]);
  if(NTHREADS<1||NTHREADS>16){fprintf(stderr,"bad threads\n");return 2;}
  for(int r=0;r<4;r++) for(int c=0;c<4;c++) MAT[r][c]=mm[4*r+c];
  keysched(key);
  for(int c=0;c<4;c++)
    base_cols[c]=(uint32_t)base[4*c]|((uint32_t)base[4*c+1]<<8)|((uint32_t)base[4*c+2]<<16)|((uint32_t)base[4*c+3]<<24);
  for(int j=0;j<4;j++) for(int x=0;x<256;x++){
    uint32_t w=0; for(int i=0;i<4;i++) w|=(uint32_t)gmul(MAT[i][j],SBOX[x])<<(8*i);
    T[j][x]=w;
  }
  if(argc>=12 && strcmp(argv[10],"block")==0){
    // single-block pin mode: encrypt argv[11] with BOTH engines, print hex
    uint8_t pt[16]; hex2b(argv[11],pt,16);
    uint32_t c[4];
    for(int i=0;i<4;i++) c[i]=(uint32_t)pt[4*i]|((uint32_t)pt[4*i+1]<<8)|((uint32_t)pt[4*i+2]<<16)|((uint32_t)pt[4*i+3]<<24);
    enc_soft(c);
    printf("{\"soft\":\"");
    for(int i=0;i<4;i++) for(int b=0;b<4;b++) printf("%02x",(unsigned)((c[i]>>(8*b))&0xff));
    __m128i s=_mm_loadu_si128((const __m128i*)pt);
    s=_mm_xor_si128(s,RKx[0]);
    for(int i=1;i<Rr;i++) s=_mm_aesenc_si128(s,RKx[i]);
    s=_mm_aesenclast_si128(s,RKx[Rr]);
    uint8_t out[16]; _mm_storeu_si128((__m128i*)out,s);
    printf("\",\"aesni\":\"");
    for(int i=0;i<16;i++) printf("%02x",out[i]);
    printf("\"}\n");
    return 0;
  }
  ENTRIES=1ull<<(32-WBITS);
  IDXMASK=(uint32_t)(ENTRIES-1);
  HBINS=(CW==8)?256:65536;
  size_t bytes=(size_t)ENTRIES*(CW==8?1:2);
  uint64_t gh[65536]; memset(gh,0,sizeof gh);
  uint64_t N=0;
  struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
  int nwin=1<<WBITS;
  int overflow_suspect=0;
  for(int w=0;w<nwin;w++){
    CURWIN=(uint32_t)w;
    void*p=mmap(NULL,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE,-1,0);
    if(p==MAP_FAILED){perror("mmap");return 3;}
    madvise(p,bytes,MADV_HUGEPAGE);
    cnt8=(uint8_t*)p; cnt16=(uint16_t*)p;
    HIST=calloc((size_t)NTHREADS*HBINS,sizeof(uint64_t));
    memset(inwin_cnt,0,sizeof inwin_cnt);
    pthread_t th[16]; arg_t ar[16];
    for(int i=0;i<NTHREADS;i++){ar[i].tid=i;pthread_create(&th[i],NULL,worker,&ar[i]);}
    for(int i=0;i<NTHREADS;i++)pthread_join(th[i],NULL);
    uint64_t inw=0; for(int i=0;i<NTHREADS;i++) inw+=inwin_cnt[i];
    for(int i=0;i<NTHREADS;i++){ar[i].tid=i;pthread_create(&th[i],NULL,histw,&ar[i]);}
    for(int i=0;i<NTHREADS;i++)pthread_join(th[i],NULL);
    uint64_t wsum=0;
    for(uint64_t b=0;b<HBINS;b++){uint64_t s=0;for(int i=0;i<NTHREADS;i++)s+=HIST[(uint64_t)i*HBINS+b];gh[b]+=s;wsum+=s*b;}
    if(wsum!=inw) overflow_suspect=1;   // exact detector: counter wrap or lost update
    N+=inw;
    free(HIST); munmap(p,bytes);
  }
  clock_gettime(CLOCK_MONOTONIC,&t1);
  unsigned __int128 npairs=0,S2=0;
  for(uint64_t b=0;b<HBINS;b++){npairs+=(unsigned __int128)gh[b]*((uint64_t)b*(b-1)/2);S2+=(unsigned __int128)gh[b]*b*b;}
  unsigned __int128 alt=(S2-(unsigned __int128)N)/2;
  uint64_t maxocc=0; for(uint64_t b=0;b<HBINS;b++) if(gh[b]) maxocc=b;
  // print n as decimal (may exceed 64 bits? no: <= C(2^32,2) < 2^63)
  unsigned long long n64=(unsigned long long)npairs, a64=(unsigned long long)alt;
  double secs=(t1.tv_sec-t0.tv_sec)+1e-9*(t1.tv_nsec-t0.tv_nsec);
  printf("{\"engine\":\"%s\",\"r\":%d,\"j0\":%d,\"cw\":%d,\"wbits\":%d,\"threads\":%d,",
    ENG_SOFT?"soft":"aesni",Rr,J0,CW,WBITS,NTHREADS);
  printf("\"key\":\"%s\",\"base\":\"%s\",\"matrix\":\"%s\",",argv[4],argv[5],argv[6]);
  printf("\"N\":%llu,\"N_ok\":%s,\"n\":%llu,\"n_alt\":%llu,\"agree\":%s,",
    (unsigned long long)N,(N==(1ull<<32))?"true":"false",n64,a64,(npairs==alt)?"true":"false");
  printf("\"n_mod8\":%llu,\"n_mod16\":%llu,\"max_occ\":%llu,",
    (unsigned long long)(npairs%8),(unsigned long long)(npairs%16),(unsigned long long)maxocc);
  printf("\"counter_integrity_ok\":%s,\"saturating\":false,",overflow_suspect?"false":"true");
  printf("\"occ_hist\":{");
  int first=1;
  for(uint64_t b=0;b<HBINS;b++) if(gh[b]){printf("%s\"%llu\":%llu",first?"":",",(unsigned long long)b,(unsigned long long)gh[b]);first=0;}
  printf("},\"seconds\":%.2f}\n",secs);
  return 0;
}
