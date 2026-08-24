
#include <stdio.h>
#include <stdint.h>
#include <time.h>
typedef unsigned __int128 u128;
typedef uint64_t u64;
static u64 P=2381327587ULL;
static inline u64 mmul(u64 a,u64 b){ return (u64)(((u128)a*b)%P); }
static inline u64 msqr(u64 a){ return (u64)(((u128)a*a)%P); }
static u64 minv(u64 a){
    int64_t t=0,newt=1; int64_t r=(int64_t)P, newr=(int64_t)a;
    while(newr!=0){ int64_t q=r/newr; int64_t tmp=t-q*newt; t=newt; newt=tmp; tmp=r-q*newr; r=newr; newr=tmp; }
    if(t<0) t+=(int64_t)P; return (u64)t;
}
int main(){
    u64 x=123456789%P, y=987654321%P, acc=0;
    struct timespec t0,t1;
    long N=20000000;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    for(long i=0;i<N;i++){ acc^=mmul(x,y); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double mul_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/N;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    x=123456789%P;
    for(long i=0;i<N;i++){ acc^=msqr(x); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double sqr_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/N;
    long M=2000000;
    clock_gettime(CLOCK_MONOTONIC,&t0);
    x=123456789%P;
    for(long i=0;i<M;i++){ acc^=minv((x%(P-1))+1); x=(x+1)%P; }
    clock_gettime(CLOCK_MONOTONIC,&t1);
    double inv_ns=((t1.tv_sec-t0.tv_sec)*1e9+(t1.tv_nsec-t0.tv_nsec))/M;
    printf("{\"mul_ns\":%f,\"sqr_ns\":%f,\"inv_ns\":%f,\"checksum\":%llu}\n", mul_ns, sqr_ns, inv_ns, (unsigned long long)acc);
    return 0;
}
