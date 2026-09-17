/* j1_kcoef.c -- J1 extension: the COEFFICIENT TWIST at odd characteristic.
 *
 * (A) is derived for lambda in K[X], not just F_p[X].  When lambda has
 * coefficients outside F_p the twisted iterate
 *     Lambda_{k+1} = Lambda_k^{(n')} o lambda
 * has a NON-TRIVIAL coefficient twist (c -> c^{p^{n'}}), and the identity
 *     x^{p^{(k+1)n'}} = Lambda_{k+1}(x)
 * depends on that twist being taken.  EXP-QSP-33b442 exercises K-coefficients
 * only at p = 2 (Stage 1b, n = 11 and 13).  This program exercises them at
 * odd p.
 *
 * LINEAGE: written from the statement of H-QSP-5540d7 (A).  Shares no code
 * with experiments/EXP-QSP-33b442/implementation/.
 *
 * Instruments (both written here, no shared path with each other's counting):
 *   A  brute enumeration of all p^n elements: N = #{x : x^{p^{n'}} = lambda(x)}
 *   C  the derivation object: build Lambda_{q+1} WITH the twist, form
 *      D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}}, check D != 0, deg D <= max(...),
 *      check EVERY brute root of L satisfies D(x) = 0 (the injection step
 *      itself), then count K-roots of D and apply the closing test L(x) = 0.
 *
 * usage: ./j1_kcoef p n nprime dmin dmax ndraws seed
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 16
static int P, NN;
static int RED[MAXN*MAXN];
static int md(long long v){ long long t=v%P; if(t<0)t+=P; return (int)t; }
static long long KT[2*MAXN];

static void kmul(const int*a,const int*b,int*out){
    for(int i=0;i<2*NN;i++) KT[i]=0;
    for(int i=0;i<NN;i++){ if(!a[i])continue; long long ai=a[i];
        for(int j=0;j<NN;j++){ if(!b[j])continue; KT[i+j]+=ai*b[j]; } }
    for(int i=2*NN-2;i>=NN;i--){ long long v=KT[i]%P; KT[i]=0; if(!v)continue;
        for(int j=0;j<NN;j++) KT[j]+=v*RED[(i-NN)*NN+j]; }
    for(int i=0;i<NN;i++) out[i]=md(KT[i]);
}
static void kadd(const int*a,const int*b,int*o){ for(int i=0;i<NN;i++) o[i]=md((long long)a[i]+b[i]); }
static void ksub(const int*a,const int*b,int*o){ for(int i=0;i<NN;i++) o[i]=md((long long)a[i]-b[i]); }
static int  kiszero(const int*a){ for(int i=0;i<NN;i++) if(a[i]) return 0; return 1; }
static void kpow(const int*a,long long e,int*out){
    int r[MAXN],b[MAXN],t[MAXN];
    for(int i=0;i<NN;i++){ r[i]=0; b[i]=a[i]; } r[0]=1;
    while(e){ if(e&1){ kmul(r,b,t); memcpy(r,t,NN*sizeof(int)); } kmul(b,b,t); memcpy(b,t,NN*sizeof(int)); e>>=1; }
    memcpy(out,r,NN*sizeof(int));
}
static long long ipow(long long b,int e){ long long r=1; while(e--) r*=b; return r; }

/* ---- K[X] : poly stored as (deg+1) blocks of NN ints, index 0 = constant ---- */
static void kp_eval(const int*f,int fd,const int*x,int*out){   /* Horner */
    int acc[MAXN],t[MAXN];
    for(int i=0;i<NN;i++) acc[i]=0;
    for(int i=fd;i>=0;i--){ kmul(acc,x,t); kadd(t,f+(size_t)i*NN,acc); }
    memcpy(out,acc,NN*sizeof(int));
}
/* out = f(g(X)), degrees fd, gd ; out buffer must hold fd*gd+1 blocks */
static int kp_compose(const int*f,int fd,const int*g,int gd,int*out,int outcap){
    int accd=-1; int *acc=(int*)calloc((size_t)(fd*gd+1)*NN,sizeof(int));
    int *tmp=(int*)calloc((size_t)(fd*gd+1)*NN,sizeof(int));
    for(int i=fd;i>=0;i--){
        /* acc = acc*g */
        if(accd>=0){
            int nd=accd+gd;
            memset(tmp,0,(size_t)(nd+1)*NN*sizeof(int));
            int pr[MAXN];
            for(int a=0;a<=accd;a++){ if(kiszero(acc+(size_t)a*NN)) continue;
                for(int b=0;b<=gd;b++){ if(kiszero(g+(size_t)b*NN)) continue;
                    kmul(acc+(size_t)a*NN,g+(size_t)b*NN,pr);
                    kadd(tmp+(size_t)(a+b)*NN,pr,tmp+(size_t)(a+b)*NN); } }
            memcpy(acc,tmp,(size_t)(nd+1)*NN*sizeof(int)); accd=nd;
        }
        if(accd<0){ accd=0; memset(acc,0,(size_t)NN*sizeof(int)); }
        kadd(acc,f+(size_t)i*NN,acc);
        while(accd>0 && kiszero(acc+(size_t)accd*NN)) accd--;
    }
    if((accd+1)>outcap){ fprintf(stderr,"compose overflow\n"); exit(1); }
    memcpy(out,acc,(size_t)(accd+1)*NN*sizeof(int));
    free(acc); free(tmp); return accd;
}
/* xorshift64 PRNG -- deterministic, seed printed */
static unsigned long long RS;
static unsigned long long rnd(){ RS^=RS<<13; RS^=RS>>7; RS^=RS<<17; return RS; }

int main(int argc,char**argv){
    if(argc<8){ fprintf(stderr,"usage: %s p n nprime dmin dmax ndraws seed\n",argv[0]); return 2; }
    P=atoi(argv[1]); int n=atoi(argv[2]); int np=atoi(argv[3]);
    int dmin=atoi(argv[4]), dmax=atoi(argv[5]); int ndraws=atoi(argv[6]);
    RS=strtoull(argv[7],NULL,10); NN=n;
    int q=n/np, r=n%np; long long pn=ipow(P,n); long long pnr=ipow(P,np-r);

    /* irreducible f of degree n over F_p : trial by order of z */
    int FM[MAXN+1]; int found=0;
    for(long long code=0;code<ipow(P,n)&&!found;code++){
        long long t=code; for(int i=0;i<n;i++){ FM[i]=(int)(t%P); t/=P; } FM[n]=1;
        /* build RED for this candidate and test that z has the right order
           by checking z^{p^n} == z and z^{p^{n/ell}} != z for prime ell | n */
        { int cur[MAXN]; for(int j=0;j<n;j++) cur[j]=md(-FM[j]);
          for(int i=0;i<n-1;i++){ for(int j=0;j<n;j++) RED[i*n+j]=cur[j];
            int top=cur[n-1],nx[MAXN]; for(int j=0;j<n;j++) nx[j]=0;
            for(int j=n-1;j>=1;j--) nx[j]=cur[j-1];
            for(int j=0;j<n;j++) nx[j]=md((long long)nx[j]+(long long)top*md(-FM[j]));
            memcpy(cur,nx,n*sizeof(int)); } }
        int z[MAXN],o[MAXN]; for(int j=0;j<n;j++) z[j]=0; if(n>1) z[1]=1; else z[0]=1;
        kpow(z,ipow(P,n),o);
        int ok=1; for(int j=0;j<n;j++) if(o[j]!=z[j]) ok=0;
        if(ok){ int m=n;
            for(int ell=2;ell<=m&&ok;ell++){ if(n%ell) continue;
                int isp=1; for(int k2=2;k2*k2<=ell;k2++) if(ell%k2==0) isp=0;
                if(!isp) continue;
                kpow(z,ipow(P,n/ell),o);
                int same=1; for(int j=0;j<n;j++) if(o[j]!=z[j]) same=0;
                if(same) ok=0; } }
        if(ok) found=1;
    }
    if(!found){ fprintf(stderr,"no irreducible\n"); return 1; }
    printf("#CELL p=%d n=%d nprime=%d q=%d r=%d p^n=%lld p^(np-r)=%lld seed=%llu f=",P,n,np,q,r,pn,pnr,RS);
    for(int i=0;i<=n;i++) printf("%d%s",FM[i],i==n?"":","); printf("\n");

    /* sigma^{n'} on every element, via the linear map applied to coords */
    int FROB[MAXN*MAXN];
    { int e[MAXN],o[MAXN];
      for(int i=0;i<n;i++){ for(int j=0;j<n;j++) e[j]=0; e[i]=1; kpow(e,ipow(P,np),o);
        for(int j=0;j<n;j++) FROB[i*n+j]=o[j]; } }

    unsigned char *elts=(unsigned char*)malloc((size_t)pn*n);
    unsigned char *sig =(unsigned char*)malloc((size_t)pn*n);
    for(long long x=0;x<pn;x++){ long long t=x;
        for(int j=0;j<n;j++){ elts[(size_t)x*n+j]=(unsigned char)(t%P); t/=P; }
        for(int j=0;j<n;j++){ long long acc=0;
            for(int i=0;i<n;i++) if(elts[(size_t)x*n+i]) acc+=(long long)elts[(size_t)x*n+i]*FROB[i*n+j];
            sig[(size_t)x*n+j]=(unsigned char)md(acc); } }

    for(int d=dmin;d<=dmax;d++){
        long long dq1=ipow(d,q+1); long long bound=dq1>pnr?dq1:pnr;
        long long viol=0,degen=0,degbad=0,notroot=0,disagree=0,nonFp=0;
        long long maxN=0; double maxratio=0;
        int *lam=(int*)calloc((size_t)(d+1)*NN,sizeof(int));
        int cap=(int)bound+8;
        int *cur=(int*)calloc((size_t)cap*NN,sizeof(int));
        int *tw =(int*)calloc((size_t)cap*NN,sizeof(int));
        int *nxt=(int*)calloc((size_t)(cap*2+8)*NN,sizeof(int));
        int *Dp =(int*)calloc((size_t)cap*NN,sizeof(int));
        int xv[MAXN],ev[MAXN],lv[MAXN];
        for(int t=0;t<ndraws;t++){
            /* draw lambda of EXACT degree d with coefficients in K */
            for(int i=0;i<=d;i++) for(int j=0;j<NN;j++) lam[(size_t)i*NN+j]=(int)(rnd()%P);
            while(kiszero(lam+(size_t)d*NN)) for(int j=0;j<NN;j++) lam[(size_t)d*NN+j]=(int)(rnd()%P);
            int outside=0;
            for(int i=0;i<=d;i++) for(int j=1;j<NN;j++) if(lam[(size_t)i*NN+j]) outside=1;
            if(outside) nonFp++;

            /* instrument C: twisted iterates */
            int curd=d; memcpy(cur,lam,(size_t)(d+1)*NN*sizeof(int));
            for(int k=1;k<=q;k++){
                for(int i=0;i<=curd;i++) kpow(cur+(size_t)i*NN,ipow(P,np),tw+(size_t)i*NN);   /* THE TWIST */
                curd=kp_compose(tw,curd,lam,d,nxt,cap*2+8);
                memcpy(cur,nxt,(size_t)(curd+1)*NN*sizeof(int));
            }
            int Dd=curd>(int)pnr?curd:(int)pnr;
            memset(Dp,0,(size_t)cap*NN*sizeof(int));
            memcpy(Dp,cur,(size_t)(curd+1)*NN*sizeof(int));
            Dp[(size_t)pnr*NN+0]=md(Dp[(size_t)pnr*NN+0]-1);
            while(Dd>0 && kiszero(Dp+(size_t)Dd*NN)) Dd--;
            int Dzero = (Dd==0 && kiszero(Dp));
            if(Dzero){ degen++; continue; }
            if(Dd>bound){ degbad++; printf("DEGVIOL d=%d draw=%d degD=%d bound=%lld\n",d,t,Dd,bound); }

            /* instrument A: brute enumeration + the injection check on every root */
            long long N=0, nDroots=0, ninj=0;
            for(long long x=0;x<pn;x++){
                for(int j=0;j<NN;j++) xv[j]=elts[(size_t)x*n+j];
                kp_eval(lam,d,xv,lv);                                  /* lambda(x) */
                int isroot=1; for(int j=0;j<NN;j++) if(lv[j]!=sig[(size_t)x*n+j]) { isroot=0; break; }
                kp_eval(Dp,Dd,xv,ev);                                  /* D(x) */
                int Dvanish=kiszero(ev);
                if(isroot) N++;
                if(Dvanish) nDroots++;
                if(Dvanish && isroot) ninj++;
                if(isroot && !Dvanish){ notroot++;      /* THE INJECTION STEP FAILING */
                    printf("INJECTION_FAIL d=%d draw=%d x=%lld\n",d,t,x); }
            }
            if(ninj!=N){ disagree++; printf("C_DISAGREE d=%d draw=%d N=%lld Ninj=%lld\n",d,t,N,ninj); }
            if(N>bound){ viol++;
                printf("VIOLATION p=%d n=%d np=%d d=%d draw=%d N=%lld bound=%lld lam=",P,n,np,d,t,N,bound);
                for(int i=0;i<=d;i++){ printf("["); for(int j=0;j<NN;j++) printf("%d%s",lam[(size_t)i*NN+j],j==NN-1?"":" "); printf("]"); }
                printf("\n"); }
            if(N>maxN) maxN=N;
            double rt=(double)N/(double)bound; if(rt>maxratio) maxratio=rt;
        }
        printf("KSUMMARY p=%d n=%d np=%d q=%d r=%d d=%d draws=%d nonFp_lambda=%lld dq1=%lld pnr=%lld bound=%lld "
               "violations=%lld degenerate=%lld degD_gt_bound=%lld injection_failures=%lld C_dis=%lld maxN=%lld maxratio=%.6f\n",
               P,n,np,q,r,d,ndraws,nonFp,dq1,pnr,bound,viol,degen,degbad,notroot,disagree,maxN,maxratio);
        fflush(stdout);
        free(lam); free(cur); free(tw); free(nxt); free(Dp);
    }
    free(elts); free(sig);
    return 0;
}
