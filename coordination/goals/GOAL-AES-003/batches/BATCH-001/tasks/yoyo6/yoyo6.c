/* YOYO-6 : iterated adaptive two-directional probe on reduced-round AES-128.
   Built after PREREGISTRATION.md was frozen. AES-NI. */
#include <wmmintrin.h>
#include <smmintrin.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <math.h>

/* ---------------- AES-128 (AES-NI), r-round with final-round-no-MC ------- */
typedef struct { __m128i EK[11], DK[11]; } aes_t;
#define EXP(k,rc) do{ __m128i t=_mm_aeskeygenassist_si128(k,rc); t=_mm_shuffle_epi32(t,0xff); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,_mm_slli_si128(k,4)); \
  k=_mm_xor_si128(k,_mm_slli_si128(k,4)); k=_mm_xor_si128(k,t);}while(0)
static void keyexp(aes_t*a,const unsigned char*key){
  __m128i k=_mm_loadu_si128((const __m128i*)key); a->EK[0]=k;
  EXP(k,0x01);a->EK[1]=k; EXP(k,0x02);a->EK[2]=k; EXP(k,0x04);a->EK[3]=k; EXP(k,0x08);a->EK[4]=k;
  EXP(k,0x10);a->EK[5]=k; EXP(k,0x20);a->EK[6]=k; EXP(k,0x40);a->EK[7]=k; EXP(k,0x80);a->EK[8]=k;
  EXP(k,0x1b);a->EK[9]=k; EXP(k,0x36);a->EK[10]=k;
  a->DK[0]=a->EK[0]; for(int i=1;i<10;i++) a->DK[i]=_mm_aesimc_si128(a->EK[i]); a->DK[10]=a->EK[10];
}
static inline __m128i enc(const aes_t*a,__m128i s,int r){
  s=_mm_xor_si128(s,a->EK[0]);
  for(int i=1;i<r;i++) s=_mm_aesenc_si128(s,a->EK[i]);
  return _mm_aesenclast_si128(s,a->EK[r]);
}
static inline __m128i dec(const aes_t*a,__m128i s,int r){
  s=_mm_xor_si128(s,a->EK[r]);
  for(int i=r-1;i>=1;i--) s=_mm_aesdec_si128(s,a->DK[i]);
  return _mm_aesdeclast_si128(s,a->EK[0]);
}
/* ---------------- geometry ---------------------------------------------- */
static int PW[4][4], CW[4][4];
static void geom(void){
  for(int j=0;j<4;j++) for(int t=0;t<4;t++){
    PW[j][t]=4*(((j+t)%4+4)%4)+t;
    CW[j][t]=4*(((j-t)%4+4)%4)+t;
  }
}
/* ---------------- rng ---------------------------------------------------- */
static inline uint64_t sm(uint64_t*x){ uint64_t z=(*x+=0x9E3779B97F4A7C15ULL);
  z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }

/* ---------------- accumulators ------------------------------------------ */
#define MAXG 8
typedef struct {
  uint64_t n;
  uint64_t cnt[MAXG][4][5];      /* per gen, per word j, m_j histogram      */
  uint64_t zhist[MAXG][17];      /* per gen, Z histogram                    */
  uint64_t g1[MAXG],g2[MAXG],g3[MAXG],g4[MAXG]; /* max_j m_j >= k           */
  uint64_t wzero[MAXG][4];       /* which word attains m_j=4                */
  uint64_t whist[MAXG][5];       /* W = #{j: m_j=4} histogram               */
  uint64_t trivial[MAXG];        /* no-op swap: swapped CW already equal    */
  uint64_t degen;                /* V6 degenerate constructions             */
  /* persistence: conditional on gen1 nontrivial hit (W>=1) */
  uint64_t hits1, surv[MAXG], hitW[5];
  uint64_t runhist[MAXG+1];
  uint64_t runhist_nd[MAXG+1]; uint64_t bnoop[MAXG];   /* leading consecutive-hit run length from gen 1 */
} acc_t;

typedef struct {
  uint64_t n; uint64_t seed; int r,tid,G,Amask,Smask,Tmask,prp; acc_t A;
} arg_t;

static void* work(void*vp){
  arg_t*a=vp;
  uint64_t st=a->seed ^ (0x9E3779B97F4A7C15ULL*(uint64_t)(a->tid+1));
  /* key: derived from seed; PRP arm uses an independent second key, 10 rounds */
  aes_t K,P; unsigned char kb[16]; uint64_t ks=a->seed^0xABCDEFULL;
  for(int i=0;i<16;i++) kb[i]=(unsigned char)sm(&ks);
  keyexp(&K,kb);
  for(int i=0;i<16;i++) kb[i]=(unsigned char)sm(&ks);
  keyexp(&P,kb);
  const aes_t*C = a->prp ? &P : &K;
  int R = a->prp ? 10 : a->r;

  unsigned char p0[16],p1[16],b0[16],b1[16];
  for(uint64_t t=0;t<a->n;t++){
    uint64_t x=sm(&st),y=sm(&st);
    memcpy(p0,&x,8); memcpy(p0+8,&y,8); memcpy(p1,p0,16);
    for(int j=0;j<4;j++) if(a->Amask>>j&1){
      uint64_t d=sm(&st); unsigned char*dd=(unsigned char*)&d;
      if(!(dd[0]|dd[1]|dd[2]|dd[3])) dd[0]=1;          /* genuinely active   */
      for(int q=0;q<4;q++) p1[PW[j][q]]^=dd[q];
    }
    int alleq=1; for(int i=0;i<16;i++) if(p0[i]!=p1[i]){alleq=0;break;}
    if(alleq){ a->A.degen++; continue; }

    int gen1hit=0, bdegen=0; int hitseq[MAXG]; for(int i=0;i<MAXG;i++) hitseq[i]=0;
    for(int g=0; g<a->G; g++){
      if(g>0){ /* B-step: swap plaintext words of Tmask */
        int bn=1;
        for(int j=0;j<4&&bn;j++) if(a->Tmask>>j&1)
          for(int q=0;q<4;q++) if(p0[PW[j][q]]!=p1[PW[j][q]]){bn=0;break;}
        if(bn){ a->A.bnoop[g]++; bdegen=1; }
        for(int j=0;j<4;j++) if(a->Tmask>>j&1)
          for(int q=0;q<4;q++){ unsigned char tmp=p0[PW[j][q]]; p0[PW[j][q]]=p1[PW[j][q]]; p1[PW[j][q]]=tmp; }
      }
      /* A-step */
      __m128i c0=enc(C,_mm_loadu_si128((__m128i*)p0),R);
      __m128i c1=enc(C,_mm_loadu_si128((__m128i*)p1),R);
      _mm_storeu_si128((__m128i*)b0,c0); _mm_storeu_si128((__m128i*)b1,c1);
      int noop=1;
      for(int j=0;j<4&&noop;j++) if(a->Smask>>j&1)
        for(int q=0;q<4;q++) if(b0[CW[j][q]]!=b1[CW[j][q]]){noop=0;break;}
      for(int j=0;j<4;j++) if(a->Smask>>j&1)
        for(int q=0;q<4;q++){ unsigned char tmp=b0[CW[j][q]]; b0[CW[j][q]]=b1[CW[j][q]]; b1[CW[j][q]]=tmp; }
      __m128i q0=dec(C,_mm_loadu_si128((__m128i*)b0),R);
      __m128i q1=dec(C,_mm_loadu_si128((__m128i*)b1),R);
      _mm_storeu_si128((__m128i*)p0,q0); _mm_storeu_si128((__m128i*)p1,q1);

      /* statistics on d = p0 ^ p1 */
      int mx=0,W=0,Z=0;
      for(int j=0;j<4;j++){
        int m=0;
        for(int q=0;q<4;q++) if(p0[PW[j][q]]==p1[PW[j][q]]) m++;
        a->A.cnt[g][j][m]++;
        if(m>mx) mx=m;
        if(m==4){ W++; a->A.wzero[g][j]++; }
        Z+=m;
      }
      a->A.zhist[g][Z]++;
      a->A.whist[g][W]++;
      if(noop) a->A.trivial[g]++;
      if(mx>=1) a->A.g1[g]++;
      if(mx>=2) a->A.g2[g]++;
      if(mx>=3) a->A.g3[g]++;
      if(mx>=4 && !noop) a->A.g4[g]++;
      if(g==0 && mx>=4 && !noop){ gen1hit=1; a->A.hits1++; a->A.hitW[W]++; }
      if(gen1hit && mx>=4 && !noop) a->A.surv[g]++;
      if(mx>=4 && !noop) hitseq[g]=1;
    }
    { int lead=0; while(lead<a->G && hitseq[lead]) lead++; a->A.runhist[lead]++;
      if(!bdegen) a->A.runhist_nd[lead]++; }
    a->A.n++;
  }
  return 0;
}

/* ---------------- pin mode ---------------------------------------------- */
static void hex16(const unsigned char*b){ for(int i=0;i<16;i++) printf("%02x",b[i]); }
static void pinmode(void){
  aes_t K; unsigned char key[16],pt[16],out[16];
  for(int i=0;i<16;i++){ key[i]=i; pt[i]=(unsigned char)(i*0x11); }
  /* FIPS-197 C.1 */
  unsigned char fk[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
  unsigned char fp[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
  keyexp(&K,fk);
  _mm_storeu_si128((__m128i*)out,enc(&K,_mm_loadu_si128((__m128i*)fp),10));
  printf("KAT "); hex16(out); printf("\n");
  /* deterministic random vectors, r=1..10, both directions */
  uint64_t st=777;
  for(int r=1;r<=10;r++){
    for(int v=0;v<3;v++){
      unsigned char k2[16],p2[16],c2[16],d2[16];
      for(int i=0;i<16;i++) k2[i]=(unsigned char)sm(&st);
      for(int i=0;i<16;i++) p2[i]=(unsigned char)sm(&st);
      aes_t A2; keyexp(&A2,k2);
      _mm_storeu_si128((__m128i*)c2,enc(&A2,_mm_loadu_si128((__m128i*)p2),r));
      _mm_storeu_si128((__m128i*)d2,dec(&A2,_mm_loadu_si128((__m128i*)c2),r));
      printf("V %d ",r); hex16(k2); printf(" "); hex16(p2); printf(" "); hex16(c2);
      printf(" rt%s\n", memcmp(d2,p2,16)==0?"OK":"FAIL");
      /* independent dec vector */
      unsigned char c3[16],p3[16];
      for(int i=0;i<16;i++) c3[i]=(unsigned char)sm(&st);
      _mm_storeu_si128((__m128i*)p3,dec(&A2,_mm_loadu_si128((__m128i*)c3),r));
      printf("D %d ",r); hex16(k2); printf(" "); hex16(c3); printf(" "); hex16(p3); printf("\n");
    }
  }
  /* PR-I0 involution check: A-step applied twice with same mask == identity */
  uint64_t st2=999; int bad=0,tested=0;
  for(int r=1;r<=10;r++) for(int Sm=1;Sm<15;Sm++){
    unsigned char k2[16],a0[16],a1[16],s0[16],s1[16],b0[16],b1[16];
    for(int i=0;i<16;i++) k2[i]=(unsigned char)sm(&st2);
    for(int i=0;i<16;i++){ a0[i]=(unsigned char)sm(&st2); a1[i]=(unsigned char)sm(&st2); }
    memcpy(s0,a0,16); memcpy(s1,a1,16);
    aes_t A2; keyexp(&A2,k2);
    for(int rep=0;rep<2;rep++){
      __m128i c0=enc(&A2,_mm_loadu_si128((__m128i*)a0),r);
      __m128i c1=enc(&A2,_mm_loadu_si128((__m128i*)a1),r);
      _mm_storeu_si128((__m128i*)b0,c0); _mm_storeu_si128((__m128i*)b1,c1);
      for(int j=0;j<4;j++) if(Sm>>j&1)
        for(int q=0;q<4;q++){ unsigned char tmp=b0[CW[j][q]]; b0[CW[j][q]]=b1[CW[j][q]]; b1[CW[j][q]]=tmp; }
      _mm_storeu_si128((__m128i*)a0,dec(&A2,_mm_loadu_si128((__m128i*)b0),r));
      _mm_storeu_si128((__m128i*)a1,dec(&A2,_mm_loadu_si128((__m128i*)b1),r));
    }
    tested++;
    if(memcmp(a0,s0,16)||memcmp(a1,s1,16)) bad++;
  }
  printf("INVOL tested %d bad %d\n",tested,bad);
}

/* ---------------- main --------------------------------------------------- */
int main(int argc,char**argv){
  geom();
  if(argc>1 && !strcmp(argv[1],"pin")){ pinmode(); return 0; }
  /* args: r lgN seed Amask Smask Tmask G prp nthreads label */
  int r=atoi(argv[1]); double lgN=atof(argv[2]); uint64_t seed=strtoull(argv[3],0,10);
  int Am=atoi(argv[4]), Sm=atoi(argv[5]), Tm=atoi(argv[6]), G=atoi(argv[7]), prp=atoi(argv[8]);
  int T=argc>9?atoi(argv[9]):4; const char*lab=argc>10?argv[10]:"arm";
  if(G>MAXG) G=MAXG;
  uint64_t N=(uint64_t)(pow(2.0,lgN)+0.5), per=N/T;
  pthread_t th[16]; static arg_t ar[16];
  for(int i=0;i<T;i++){ memset(&ar[i],0,sizeof(arg_t));
    ar[i].n=per; ar[i].seed=seed; ar[i].r=r; ar[i].tid=i; ar[i].G=G;
    ar[i].Amask=Am; ar[i].Smask=Sm; ar[i].Tmask=Tm; ar[i].prp=prp;
    pthread_create(&th[i],0,work,&ar[i]); }
  acc_t A; memset(&A,0,sizeof A);
  for(int i=0;i<T;i++){ pthread_join(th[i],0); acc_t*s=&ar[i].A;
    A.n+=s->n; A.degen+=s->degen; A.hits1+=s->hits1;
    for(int q=0;q<=MAXG;q++){ A.runhist[q]+=s->runhist[q]; A.runhist_nd[q]+=s->runhist_nd[q]; }
    for(int q=0;q<MAXG;q++) A.bnoop[q]+=s->bnoop[q];
    for(int k=0;k<5;k++) A.hitW[k]+=s->hitW[k];
    for(int g=0;g<MAXG;g++){ A.g1[g]+=s->g1[g];A.g2[g]+=s->g2[g];A.g3[g]+=s->g3[g];A.g4[g]+=s->g4[g];
      A.trivial[g]+=s->trivial[g]; A.surv[g]+=s->surv[g];
      for(int j=0;j<4;j++){ A.wzero[g][j]+=s->wzero[g][j]; for(int m=0;m<5;m++) A.cnt[g][j][m]+=s->cnt[g][j][m]; }
      for(int z=0;z<17;z++) A.zhist[g][z]+=s->zhist[g][z];
      for(int w=0;w<5;w++) A.whist[g][w]+=s->whist[g][w]; } }
  printf("{\"label\":\"%s\",\"r\":%d,\"prp\":%d,\"N\":%llu,\"Amask\":%d,\"Smask\":%d,\"Tmask\":%d,\"G\":%d,\"seed\":%llu,\"degen\":%llu,\n",
    lab,r,prp,(unsigned long long)A.n,Am,Sm,Tm,G,(unsigned long long)seed,(unsigned long long)A.degen);
  printf(" \"g1\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.g1[g],g<G-1?",":"");
  printf("],\n \"g2\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.g2[g],g<G-1?",":"");
  printf("],\n \"g3\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.g3[g],g<G-1?",":"");
  printf("],\n \"g4\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.g4[g],g<G-1?",":"");
  printf("],\n \"trivial\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.trivial[g],g<G-1?",":"");
  printf("],\n \"surv\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.surv[g],g<G-1?",":"");
  printf("],\n \"runhist\":["); for(int q=0;q<=MAXG;q++) printf("%llu%s",(unsigned long long)A.runhist[q],q<MAXG?",":"");
  printf("],\n \"runhist_nd\":["); for(int q=0;q<=MAXG;q++) printf("%llu%s",(unsigned long long)A.runhist_nd[q],q<MAXG?",":"");
  printf("],\n \"bnoop\":["); for(int g=0;g<G;g++) printf("%llu%s",(unsigned long long)A.bnoop[g],g<G-1?",":"");
  printf("],\n \"hits1\":%llu,\"hitW\":[",(unsigned long long)A.hits1);
  for(int k=0;k<5;k++) printf("%llu%s",(unsigned long long)A.hitW[k],k<4?",":"");
  printf("],\n \"whist\":["); for(int g=0;g<G;g++){ printf("["); for(int w=0;w<5;w++) printf("%llu%s",(unsigned long long)A.whist[g][w],w<4?",":""); printf("]%s",g<G-1?",":""); }
  printf("],\n \"cnt\":["); for(int g=0;g<G;g++){ printf("["); for(int j=0;j<4;j++){ printf("["); for(int m=0;m<5;m++) printf("%llu%s",(unsigned long long)A.cnt[g][j][m],m<4?",":""); printf("]%s",j<3?",":""); } printf("]%s",g<G-1?",":""); }
  printf("],\n \"wzero\":["); for(int g=0;g<G;g++){ printf("["); for(int j=0;j<4;j++) printf("%llu%s",(unsigned long long)A.wzero[g][j],j<3?",":""); printf("]%s",g<G-1?",":""); }
  printf("],\n \"zhist\":["); for(int g=0;g<G;g++){ printf("["); for(int z=0;z<17;z++) printf("%llu%s",(unsigned long long)A.zhist[g][z],z<16?",":""); printf("]%s",g<G-1?",":""); }
  printf("]}\n");
  return 0;
}
