#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int P=2, NN=4;
static int FMOD[5]={1,1,0,0,1};
static int RED[3*4];
static int md(long long v){ long long t=v%P; if(t<0)t+=P; return (int)t; }
static void kmul(const int*a,const int*b,int*out){
    long long t[8]; memset(t,0,sizeof(t));
    for(int i=0;i<NN;i++){ if(!a[i])continue; long long ai=a[i];
        for(int j=0;j<NN;j++){ if(!b[j])continue; t[i+j]+=ai*b[j]; } }
    for(int i=2*NN-2;i>=NN;i--){ long long v=t[i]%P; t[i]=0; if(!v)continue;
        for(int j=0;j<NN;j++) t[j]+= v*RED[(i-NN)*NN+j]; }
    for(int i=0;i<NN;i++) out[i]=md(t[i]);
}
static void kpow(const int*a,long long e,int*out){
    int r[4]={1,0,0,0}, b[4], t[4]; memcpy(b,a,sizeof(b));
    while(e){ if(e&1){ kmul(r,b,t); memcpy(r,t,sizeof(r)); } kmul(b,b,t); memcpy(b,t,sizeof(b)); e>>=1; }
    memcpy(out,r,sizeof(r));
}
int main(){
    int cur[4]; for(int j=0;j<4;j++) cur[j]=md(-FMOD[j]);
    for(int i=0;i<3;i++){ for(int j=0;j<4;j++) RED[i*4+j]=cur[j];
        int top=cur[3], nx[4]={0,0,0,0};
        for(int j=3;j>=1;j--) nx[j]=cur[j-1];
        for(int j=0;j<4;j++) nx[j]=md((long long)nx[j]+(long long)top*md(-FMOD[j]));
        memcpy(cur,nx,sizeof(cur)); }
    for(int i=0;i<3;i++){ printf("z^%d mod f = ",4+i); for(int j=0;j<4;j++) printf("%d",RED[i*4+j]); printf("\n"); }
    int cnt=0;
    for(int x=0;x<16;x++){
        int xv[4],sq[4],p8[4]; int t=x; for(int j=0;j<4;j++){ xv[j]=t%2; t/=2; }
        kmul(xv,xv,sq); kpow(xv,8,p8);
        int eq=1; for(int j=0;j<4;j++) if(sq[j]!=p8[j]) eq=0;
        printf("x=%2d coords=%d%d%d%d  x^2=%d%d%d%d  x^8=%d%d%d%d  %s\n",x,xv[0],xv[1],xv[2],xv[3],
               sq[0],sq[1],sq[2],sq[3], p8[0],p8[1],p8[2],p8[3], eq?"MATCH":"");
        if(eq) cnt++;
    }
    printf("count x^8==x^2 : %d\n",cnt);
    return 0;
}
