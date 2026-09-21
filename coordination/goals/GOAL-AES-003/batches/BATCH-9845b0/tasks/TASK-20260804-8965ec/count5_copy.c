// COUNT5 measurement engine. AES-NI, no RNG inside.
// usage: count5 <r> <j0> <RK_hex 11*16 bytes> <base_hex 16 bytes> <pimode id|fd>
//               <ptmode coset|scr> [<scrRK_hex 11*16 bytes>]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <wmmintrin.h>
#include <smmintrin.h>
#include <sys/mman.h>
#include <time.h>

static __m128i RK[11], SRK[11];
static int Rr, J0, PIFD, PTSCR;
static uint8_t *cnt;                 // 2^32 bytes
static uint64_t HIST[4][256];
static __m128i shufmask;
static __m128i tbl_lo[65536];        // bytes 0,5 from low 16 bits of a
static __m128i base_masked;

static void hex2bytes(const char *h, uint8_t *o, int n){
  for(int i=0;i<n;i++){ unsigned v; sscanf(h+2*i,"%2x",&v); o[i]=(uint8_t)v; }
}
static inline __m128i encr(__m128i s, const __m128i *rk, int r){
  s=_mm_xor_si128(s,rk[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,rk[i]);
  return _mm_aesenclast_si128(s,rk[r]);
}

typedef struct { int tid; } arg_t;

static void *worker(void *ap){
  int tid=((arg_t*)ap)->tid;
  uint8_t *base_cnt = cnt;
  uint64_t lo = (uint64_t)tid<<30, hi = lo + (1ull<<30);
  for(uint64_t hi16=0; hi16<65536; hi16++){
    __m128i part = _mm_or_si128(base_masked,
        _mm_insert_epi8(_mm_insert_epi8(_mm_setzero_si128(),
            (int)(hi16&0xff),10), (int)((hi16>>8)&0xff),15));
    for(uint64_t lo16=0; lo16<65536; lo16+=8){
      __m128i p[8];
      for(int k=0;k<8;k++){
        uint64_t a = (hi16<<16)|(lo16+k);
        if(PTSCR){
          __m128i ctr=_mm_set_epi64x(0,(long long)a);
          __m128i sc=encr(ctr,SRK,10);
          uint32_t d=(uint32_t)_mm_cvtsi128_si32(sc);
          p[k]=_mm_or_si128(base_masked,
               _mm_insert_epi8(_mm_insert_epi8(_mm_insert_epi8(_mm_insert_epi8(
                 _mm_setzero_si128(),(int)(d&0xff),0),(int)((d>>8)&0xff),5),
                 (int)((d>>16)&0xff),10),(int)((d>>24)&0xff),15));
        } else {
          p[k]=_mm_or_si128(part,tbl_lo[lo16+k]);
        }
      }
      for(int k=0;k<8;k++) p[k]=_mm_xor_si128(p[k],RK[0]);
      for(int i=1;i<Rr;i++) for(int k=0;k<8;k++) p[k]=_mm_aesenc_si128(p[k],RK[i]);
      for(int k=0;k<8;k++) p[k]=_mm_aesenclast_si128(p[k],RK[Rr]);
      for(int k=0;k<8;k++){
        uint32_t v=(uint32_t)_mm_cvtsi128_si32(_mm_shuffle_epi8(p[k],shufmask));
        if((uint64_t)v>=lo && (uint64_t)v<hi){
          uint8_t *q=base_cnt+v; uint8_t c=*q; if(c!=255) *q=c+1; else *q=255;
        }
      }
    }
  }
  uint64_t *h=HIST[tid];
  for(uint64_t v=lo; v<hi; v++) h[base_cnt[v]]++;
  return NULL;
}

int main(int argc,char**argv){
  if(argc<7){ fprintf(stderr,"bad args\n"); return 2; }
  Rr=atoi(argv[1]); J0=atoi(argv[2]);
  uint8_t rkb[176]; hex2bytes(argv[3],rkb,176);
  for(int i=0;i<11;i++) RK[i]=_mm_loadu_si128((__m128i*)(rkb+16*i));
  uint8_t bb[16]; hex2bytes(argv[4],bb,16);
  PIFD = (strcmp(argv[5],"fd")==0);
  PTSCR= (strcmp(argv[6],"scr")==0);
  if(PTSCR){ if(argc<8){fprintf(stderr,"need scrRK\n");return 2;}
    uint8_t s2[176]; hex2bytes(argv[7],s2,176);
    for(int i=0;i<11;i++) SRK[i]=_mm_loadu_si128((__m128i*)(s2+16*i)); }

  int8_t sm[16]; for(int i=0;i<16;i++) sm[i]=-1;
  for(int t=0;t<4;t++){
    int idx = PIFD ? 4*(((J0+t)%4+4)%4)+t : 4*(((J0-t)%4+4)%4)+t;
    sm[t]=(int8_t)idx;
  }
  shufmask=_mm_loadu_si128((__m128i*)sm);

  uint8_t bm[16]; memcpy(bm,bb,16); bm[0]=bm[5]=bm[10]=bm[15]=0;
  base_masked=_mm_loadu_si128((__m128i*)bm);
  for(uint32_t x=0;x<65536;x++){
    uint8_t z[16]; memset(z,0,16); z[0]=x&0xff; z[5]=(x>>8)&0xff;
    tbl_lo[x]=_mm_loadu_si128((__m128i*)z);
  }

  cnt=mmap(NULL,1ull<<32,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE,-1,0);
  if(cnt==MAP_FAILED){perror("mmap");return 3;}
  madvise(cnt,1ull<<32,MADV_HUGEPAGE);

  struct timespec t0,t1; clock_gettime(CLOCK_MONOTONIC,&t0);
  pthread_t th[4]; arg_t ar[4];
  for(int i=0;i<4;i++){ ar[i].tid=i; pthread_create(&th[i],NULL,worker,&ar[i]); }
  for(int i=0;i<4;i++) pthread_join(th[i],NULL);
  clock_gettime(CLOCK_MONOTONIC,&t1);

  uint64_t hist[256]; memset(hist,0,sizeof hist);
  for(int t=0;t<4;t++) for(int v=0;v<256;v++) hist[v]+=HIST[t][v];
  unsigned __int128 N=0,S2=0,npairs=0;
  for(int v=0;v<256;v++){ N+= (unsigned __int128)hist[v]*v;
    S2+=(unsigned __int128)hist[v]*v*v;
    npairs+=(unsigned __int128)hist[v]*((uint64_t)v*(v-1)/2); }
  unsigned __int128 alt=(S2-N)/2;
  int maxocc=0; for(int v=255;v>=0;v--) if(hist[v]){maxocc=v;break;}
  double secs=(t1.tv_sec-t0.tv_sec)+1e-9*(t1.tv_nsec-t0.tv_nsec);
  printf("{\"r\":%d,\"j0\":%d,\"pimode\":\"%s\",\"ptmode\":\"%s\",",
     Rr,J0,PIFD?"fd":"id",PTSCR?"scr":"coset");
  printf("\"N\":%llu,\"n\":%llu,\"n_alt\":%llu,\"agree\":%s,",
     (unsigned long long)N,(unsigned long long)npairs,(unsigned long long)alt,
     (npairs==alt)?"true":"false");
  printf("\"n_mod8\":%llu,\"n_mod16\":%llu,\"max_occ\":%d,\"overflow\":%s,",
     (unsigned long long)(npairs%8),(unsigned long long)(npairs%16),maxocc,
     (maxocc>=255)?"true":"false");
  printf("\"occ_hist\":[");
  for(int v=0;v<=maxocc;v++) printf("%s%llu",v?",":"",(unsigned long long)hist[v]);
  printf("],\"seconds\":%.2f}\n",secs);
  return 0;
}
