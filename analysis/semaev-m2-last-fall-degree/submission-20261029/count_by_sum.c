/* Independent exhaustive solution count, grouping by s=X1+X2 in V.
 * No producer/checker source is included. For each s, S3=0 implies
 * u^2+u=s^2+a6/z^2, u=X1*X2/z. Then X1^2+s*X1=z*u.
 * Artin--Schreier roots use an independently built linear section; batch
 * inversions amortize field inversion. Every accepted root is checked in V.
 * Args: n modulus_hex z_hex a6_hex k basis_hex...; output ordered pair count.
 * Native exact computation, not a performance claim.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <immintrin.h>
typedef unsigned __int128 wide;
static unsigned n, k;
static uint64_t modulus, vbase[64], vech[64], lp[64], pre[64];
static uint64_t square_table[8][256], root_table[8][256], trace_mask;
static uint64_t mul(uint64_t a, uint64_t b) {
  __m128i t=_mm_clmulepi64_si128(_mm_set_epi64x(0,a),_mm_set_epi64x(0,b),0);
  wide x=(wide)(uint64_t)_mm_extract_epi64(t,1)<<64 | (uint64_t)_mm_extract_epi64(t,0);
  for(int j=2*(int)n-2;j>=(int)n;--j) if((x>>j)&1) x^=(wide)modulus<<(j-n);
  return (uint64_t)x;
}
static uint64_t lookup(uint64_t t[8][256],uint64_t a) {
  uint64_t r=0; for(unsigned j=0;j<8;++j) r^=t[j][(a>>(8*j))&255]; return r;
}
static uint64_t square(uint64_t a) { return lookup(square_table,a); }
static uint64_t inverse(uint64_t a) {
  if(!a) {fprintf(stderr,"zero inverse\n");exit(2);}
  uint64_t r=a; for(unsigned j=1;j<n-1;++j) r=mul(square(r),a); return square(r);
}
static unsigned trace(uint64_t a) {return __builtin_parityll(a&trace_mask);}
static uint64_t root(uint64_t a) {return lookup(root_table,a);}
static int in_v(uint64_t a) {
  while(a) {unsigned j=63-__builtin_clzll(a);if(!vech[j])return 0;a^=vech[j];}return 1;
}
static void setup(void) {
  for(unsigned j=0;j<8;++j) for(unsigned b=1;b<256;++b) {
    uint64_t a=(uint64_t)b<<(8*j); if(j*8<n) {
      a &= (UINT64_C(1)<<n)-1;
      square_table[j][b]=mul(a,a);
    }
  }
  for(unsigned j=0;j<n;++j) {
    uint64_t a=UINT64_C(1)<<j,x=a,t=0;
    for(unsigned i=0;i<n;++i){t^=x;x=square(x);}
    if(t>1){fprintf(stderr,"invalid field trace\n");exit(2);}
    trace_mask|=t<<j;
    uint64_t value=square(a)^a,y=a;
    while(value) {unsigned q=63-__builtin_clzll(value);
      if(!lp[q]){lp[q]=value;pre[q]=y;break;}value^=lp[q];y^=pre[q];}
  }
  unsigned rank=0;for(unsigned j=0;j<n;++j)rank+=lp[j]!=0;
  if(rank!=n-1){fprintf(stderr,"invalid Artin-Schreier rank\n");exit(2);}
  uint64_t section[64]={0};
  for(unsigned j=0;j<n;++j) {
    uint64_t value=UINT64_C(1)<<j,y=0;
    for(int q=n-1;q>=0;--q) if((value>>q)&1 && lp[q]){value^=lp[q];y^=pre[q];}
    section[j]=y;
  }
  for(unsigned j=0;j<8;++j)for(unsigned b=1;b<256;++b)
    for(unsigned i=0;i<8;++i)if((b>>i)&1)root_table[j][b]^=section[j*8+i];
}
#define BATCH 4096
int main(int argc,char **argv) {
  if(argc<7)return 2;
  n=strtoul(argv[1],0,10);modulus=strtoull(argv[2],0,16);
  uint64_t z=strtoull(argv[3],0,16),a6=strtoull(argv[4],0,16);
  k=strtoul(argv[5],0,10);
  if(n<3||n>63||k<1||k>30||argc!=(int)k+6||!z||!a6||z>=(UINT64_C(1)<<n)||a6>=(UINT64_C(1)<<n)||
     (modulus>>n)!=1){fprintf(stderr,"invalid parameters\n");return 2;}
  for(unsigned j=0;j<k;++j){vbase[j]=strtoull(argv[j+6],0,16);uint64_t a=vbase[j];
    if(a>=(UINT64_C(1)<<n))return 2;
    while(a){unsigned q=63-__builtin_clzll(a);if(!vech[q]){vech[q]=a;break;}a^=vech[q];}
    if(!a){fprintf(stderr,"dependent basis\n");return 2;}}
  setup();
  uint64_t alpha=mul(a6,inverse(square(z))),pb[64],p0=mul(z,root(alpha));
  for(unsigned j=0;j<k;++j)pb[j]=mul(z,root(square(vbase[j])));
  uint64_t total=0;
  if(!trace(alpha))for(unsigned e=0;e<2;++e){uint64_t x=p0^(e?z:0);
    for(unsigned j=1;j<n;++j)x=square(x);
    total+=in_v(x);}
  uint64_t ss[BATCH],pp[BATCH],prefix[BATCH],iv[BATCH],s=0,p=p0;
  unsigned used=0;uint64_t end=UINT64_C(1)<<k;
  for(uint64_t g=1;g<=end;++g){
    if(g<end){unsigned bit=__builtin_ctzll(g);s^=vbase[bit];p^=pb[bit];
      if(trace(s)==trace(alpha)){ss[used]=s;pp[used]=p;++used;}}
    if(used && (used==BATCH || g==end)){
      uint64_t acc=1;for(unsigned j=0;j<used;++j){prefix[j]=acc;acc=mul(acc,ss[j]);}
      acc=inverse(acc);
      for(unsigned j=used;j-->0;){iv[j]=mul(acc,prefix[j]);acc=mul(acc,ss[j]);}
      for(unsigned j=0;j<used;++j){uint64_t invsq=square(iv[j]),c=mul(pp[j],invsq),delta=mul(z,invsq);
        for(unsigned e=0;e<2;++e){uint64_t rhs=c^(e?delta:0);if(trace(rhs))continue;
          uint64_t x=mul(ss[j],root(rhs));if(in_v(x))total+=2;}}
      used=0;
    }
  }
  printf("%llu\n",(unsigned long long)total);return 0;
}
