/* j1_fp_sweep.c -- independent odd-characteristic sweep for joint J1 of the
 * TASK-20260917-34b637 review of EXP-QSP-33b442.
 *
 * LINEAGE: written from the STATEMENT of H-QSP-5540d7 (A) alone.  Nothing here
 * is copied or adapted from experiments/EXP-QSP-33b442/implementation/
 * (qspcore.py, gf2rc.c, runlib.py, stage*.py) or from
 * analysis/qsp-ecc2k130/explore/.  Those files were not read before this one
 * was written and run.  The producer's package is bit-packed GF(2)[X] and is
 * p = 2 only; this is dense F_p[X] for arbitrary prime p.
 *
 * Quantity: for K = F_p^n, lambda in F_p[X] of exact degree d,
 *     L = X^{p^{n'}} - lambda(X),   n = q n' + r, 0 <= r < n',
 *     N = #{ x in K : x^{p^{n'}} = lambda(x) }  (DISTINCT roots of L in K)
 * and the claim under test is  N <= max(d^{q+1}, p^{n'-r})  whenever
 *     D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}} != 0,  Lambda_1 = lambda,
 *     Lambda_{k+1} = Lambda_k^{(n')} o lambda   (twist trivial over F_p).
 *
 * Three instruments, all written here:
 *   A  brute enumeration of all p^n elements of K            (exact, no algebra)
 *   B  N = deg gcd(X^{p^n} - X, L), X^{p^n} mod L by GENERIC repeated p-th
 *      powering -- deliberately NOT via the twisted-iterate identity under test
 *   C  the injection count: build D, take its K-roots, apply the closing test
 *      L(x) = 0; also checks deg D <= max(...), D != 0, and that the root set
 *      of L in K divides D (the injection step of (A) itself).
 *
 * usage: ./j1_fp_sweep p n nprime dmin dmax brute_limit
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int P;                      /* characteristic */

static int md(long long v){ long long t = v % P; if(t<0) t+=P; return (int)t; }

/* ------------------------------ dense F_p[X] ------------------------------ */
/* poly = int array c[0..deg], deg = -1 for the zero polynomial */

typedef struct { int *c; int deg; int cap; } poly;

static void pinit(poly *a,int cap){ a->c=(int*)calloc(cap>0?cap:1,sizeof(int)); a->cap=cap>0?cap:1; a->deg=-1; }
static void pfree(poly *a){ free(a->c); a->c=NULL; a->cap=0; a->deg=-1; }
static void pensure(poly *a,int need){ if(need>a->cap){ int nc=need*2+8; a->c=(int*)realloc(a->c,nc*sizeof(int)); memset(a->c+a->cap,0,(nc-a->cap)*sizeof(int)); a->cap=nc; } }
static void pnorm(poly *a){ while(a->deg>=0 && a->c[a->deg]==0) a->deg--; }
static void pzero(poly *a){ memset(a->c,0,a->cap*sizeof(int)); a->deg=-1; }
static void pcopy(poly *dst,const poly *src){ pensure(dst,src->deg+1>0?src->deg+1:1); memset(dst->c,0,dst->cap*sizeof(int)); if(src->deg>=0) memcpy(dst->c,src->c,(src->deg+1)*sizeof(int)); dst->deg=src->deg; }
static void pmono(poly *a,int k,int c){ pensure(a,k+1); memset(a->c,0,a->cap*sizeof(int)); a->c[k]=md(c); a->deg=k; pnorm(a); }

static int inv_mod(int x){ /* Fermat */ long long r=1,b=md(x); int e=P-2; while(e){ if(e&1) r=r*b%P; b=b*b%P; e>>=1;} return (int)r; }

static void psub_into(poly *a,const poly *b){ /* a -= b */
    int m = a->deg > b->deg ? a->deg : b->deg;
    pensure(a,m+1);
    for(int i=a->deg+1;i<=m;i++) a->c[i]=0;      /* the gap is ZERO, not stale */
    for(int i=0;i<=b->deg;i++) a->c[i]=md((long long)a->c[i]-b->c[i]);
    if(b->deg>a->deg) a->deg=b->deg;
    pnorm(a);
}

static void pmul(poly *out,const poly *a,const poly *b){
    if(a->deg<0||b->deg<0){ pzero(out); return; }
    int nd=a->deg+b->deg;
    int *tmp=(int*)calloc(nd+1,sizeof(int));
    for(int i=0;i<=a->deg;i++){ if(!a->c[i]) continue; long long ai=a->c[i];
        for(int j=0;j<=b->deg;j++){ if(!b->c[j]) continue; tmp[i+j]=md(tmp[i+j]+ai*b->c[j]); } }
    pensure(out,nd+1); memset(out->c,0,out->cap*sizeof(int));
    memcpy(out->c,tmp,(nd+1)*sizeof(int)); out->deg=nd; pnorm(out); free(tmp);
}

/* rem = a mod b (b != 0); also optional quotient ignored */
static void pmod_poly(poly *rem,const poly *a,const poly *b){
    pcopy(rem,a);
    if(b->deg<0){ fprintf(stderr,"div by zero poly\n"); exit(1); }
    int db=b->deg; int il=inv_mod(b->c[db]);
    for(int i=rem->deg;i>=db;i--){
        if(!rem->c[i]) continue;
        int f=(int)((long long)rem->c[i]*il%P);
        for(int j=0;j<=db;j++) rem->c[i-db+j]=md((long long)rem->c[i-db+j]-(long long)f*b->c[j]);
    }
    pnorm(rem);
}

static void pgcd(poly *out,const poly *x,const poly *y){
    poly a,b,t; pinit(&a,(x->deg>0?x->deg:0)+2); pinit(&b,(y->deg>0?y->deg:0)+2); pinit(&t,(x->deg>0?x->deg:0)+2);
    pcopy(&a,x); pcopy(&b,y);
    while(b.deg>=0){ pmod_poly(&t,&a,&b); pcopy(&a,&b); pcopy(&b,&t); }
    if(a.deg>=0){ int il=inv_mod(a.c[a.deg]); for(int i=0;i<=a.deg;i++) a.c[i]=(int)((long long)a.c[i]*il%P); }
    pcopy(out,&a); pfree(&a); pfree(&b); pfree(&t);
}

/* f(g(X)) by Horner */
static void pcompose(poly *out,const poly *f,const poly *g){
    poly acc,tmp; pinit(&acc,8); pinit(&tmp,8); pzero(&acc);
    for(int i=f->deg;i>=0;i--){
        pmul(&tmp,&acc,g); pcopy(&acc,&tmp);
        pensure(&acc,1); if(acc.deg<0){ acc.deg=0; acc.c[0]=0; }
        acc.c[0]=md(acc.c[0]+f->c[i]); pnorm(&acc);
    }
    pcopy(out,&acc); pfree(&acc); pfree(&tmp);
}

/* ---- X^{p^n} mod L  by GENERIC repeated p-th powering, L = X^D - lam ---- */
/* uses only: coefficients are in F_p so g(X)^p = g(X^p); and X^{D+j} = X^j*lam */
static void pth_power_mod_L(poly *g,int D,const poly *lam,int *buf,int bufcap){
    if(g->deg<0) return;
    int hd=g->deg*P;
    if(hd+1>bufcap){ fprintf(stderr,"buf too small\n"); exit(1); }
    memset(buf,0,(size_t)bufcap*sizeof(int));   /* clear ALL of it: the nd scan
                                                   below reads up to index D-1 */
    for(int i=0;i<=g->deg;i++) buf[i*P]=g->c[i];
    for(int i=hd;i>=D;i--){
        int v=buf[i]; if(!v) continue; buf[i]=0;
        for(int j=0;j<=lam->deg;j++) buf[i-D+j]=md((long long)buf[i-D+j]+(long long)v*lam->c[j]);
    }
    int nd=D-1; while(nd>=0 && buf[nd]==0) nd--;
    pensure(g,nd+1>0?nd+1:1); memset(g->c,0,g->cap*sizeof(int));
    for(int i=0;i<=nd;i++) g->c[i]=buf[i];
    g->deg=nd;
}

/* X^{p^n} mod M for a general modulus M (used for the K-roots of D) */
static void xpn_mod_general(poly *out,int n,const poly *M){
    poly cur,tmp; pinit(&cur,M->deg+2); pinit(&tmp,(M->deg+2)*P+8);
    pmono(&cur,1,1);
    if(M->deg==0){ pzero(out); pfree(&cur); pfree(&tmp); return; }
    if(M->deg==1){ /* X = root; handle by direct reduce */ }
    for(int k=0;k<n;k++){
        int hd = cur.deg<0?-1:cur.deg*P;
        pzero(&tmp);
        if(hd>=0){ pensure(&tmp,hd+1); for(int i=0;i<=cur.deg;i++) tmp.c[i*P]=cur.c[i]; tmp.deg=hd; pnorm(&tmp); }
        pmod_poly(&cur,&tmp,M);
    }
    pcopy(out,&cur); pfree(&cur); pfree(&tmp);
}

/* --------------------------- K = F_p[z]/(f) ------------------------------- */

static int NN;                /* degree n of K */
static int *FMOD;             /* f coefficients, length n+1 */
static int *RED;              /* RED[i][j] = coeff j of z^{n+i} mod f, i<n-1 */
static int *FROBM;            /* matrix of sigma^{n'} on K over F_p (row-vector convention) */

#define MAXN 40
static long long KT[2*MAXN];
static void kmul(const int *a,const int *b,int *out){
    for(int i=0;i<2*NN;i++) KT[i]=0;
    for(int i=0;i<NN;i++){ if(!a[i]) continue; long long ai=a[i];
        for(int j=0;j<NN;j++){ if(!b[j]) continue; KT[i+j]+=ai*b[j]; } }
    for(int i=2*NN-2;i>=NN;i--){ long long v=KT[i]%P; KT[i]=0; if(!v) continue;
        for(int j=0;j<NN;j++) KT[j]+= v*RED[(i-NN)*NN+j]; }
    /* note: RED indexed by (i-NN) which is 0..NN-2 */
    for(int i=0;i<NN;i++) out[i]=md(KT[i]);
}
static void kpow(const int *a,long long e,int *out){
    int r[MAXN],b[MAXN],t[MAXN];
    for(int i=0;i<NN;i++){ r[i]=0; b[i]=a[i]; }
    r[0]=1;
    while(e){ if(e&1){ kmul(r,b,t); memcpy(r,t,NN*sizeof(int)); } kmul(b,b,t); memcpy(b,t,NN*sizeof(int)); e>>=1; }
    memcpy(out,r,NN*sizeof(int));
}

static int is_irreducible(const poly *f){
    int n=f->deg; if(n<1) return 0; if(n==1) return 1;
    poly xp,xx,g,t; pinit(&xp,n+2); pinit(&xx,4); pinit(&g,n+2); pinit(&t,n+2);
    pmono(&xx,1,1);
    xpn_mod_general(&xp,n,f);
    int ok = (xp.deg==xx.deg);
    if(ok) for(int i=0;i<=xp.deg;i++) if(xp.c[i]!=xx.c[i]){ ok=0; break; }
    if(ok){
        int m=n;
        for(int ell=2;ell<=m;ell++){
            if(m%ell) continue;
            while(m%ell==0) m/=ell;
            poly xq; pinit(&xq,n+2);
            xpn_mod_general(&xq,n/ell,f);
            psub_into(&xq,&xx);
            pgcd(&g,&xq,f);
            if(g.deg!=0) ok=0;
            pfree(&xq);
            if(!ok) break;
        }
    }
    pfree(&xp); pfree(&xx); pfree(&g); pfree(&t);
    return ok;
}

static void find_irreducible(int n,poly *out){
    poly cand; pinit(&cand,n+2);
    for(int k=1;k<n;k++) for(int a=1;a<P;a++) for(int b=1;b<P;b++){
        pzero(&cand); pensure(&cand,n+1); cand.c[n]=1; cand.c[k]=a; cand.c[0]=b; cand.deg=n;
        if(is_irreducible(&cand)){ pcopy(out,&cand); pfree(&cand); return; }
    }
    /* fall back: systematic enumeration of monic degree-n polys */
    long long total=1; for(int i=0;i<n;i++) total*=P;
    for(long long code=0;code<total;code++){
        pzero(&cand); pensure(&cand,n+1); long long t=code;
        for(int i=0;i<n;i++){ cand.c[i]=(int)(t%P); t/=P; }
        cand.c[n]=1; cand.deg=n;
        if(is_irreducible(&cand)){ pcopy(out,&cand); pfree(&cand); return; }
    }
    fprintf(stderr,"no irreducible found\n"); exit(1);
}

/* ------------------------------ main sweep -------------------------------- */

static long long ipow(long long b,int e){ long long r=1; while(e--) r*=b; return r; }

int main(int argc,char**argv){
    if(argc<7){ fprintf(stderr,"usage: %s p n nprime dmin dmax brute_limit\n",argv[0]); return 2; }
    P=atoi(argv[1]); int n=atoi(argv[2]); int np=atoi(argv[3]);
    int dmin=atoi(argv[4]), dmax=atoi(argv[5]); long long brute_limit=atoll(argv[6]);
    int verbose = (argc>7)?atoi(argv[7]):0;
    long long stride = (argc>8)?atoll(argv[8]):1;  /* 1 = exhaustive */
    NN=n;
    int q=n/np, r=n%np;
    long long D=ipow(P,np);            /* deg L */
    long long pnr=ipow(P,np-r);
    long long pn=ipow(P,n);

    /* ---- set up K for the brute instrument (if affordable) ---- */
    int do_brute = (pn<=brute_limit);
    poly f; pinit(&f,n+2);
    unsigned char *powtab=NULL, *sig=NULL;
    if(do_brute){
        find_irreducible(n,&f);
        FMOD=(int*)calloc(n+1,sizeof(int)); for(int i=0;i<=n;i++) FMOD[i]=f.c[i];
        RED=(int*)calloc((n>1?(n-1):1)*n,sizeof(int));
        if(n>1){
            int *cur=(int*)calloc(n,sizeof(int));
            for(int j=0;j<n;j++) cur[j]=md(-FMOD[j]);          /* z^n mod f */
            for(int i=0;i<n-1;i++){
                for(int j=0;j<n;j++) RED[i*n+j]=cur[j];
                int top=cur[n-1]; int *nx=(int*)calloc(n,sizeof(int));
                for(int j=n-1;j>=1;j--) nx[j]=cur[j-1];
                for(int j=0;j<n;j++) nx[j]=md((long long)nx[j]+(long long)top*md(-FMOD[j]));
                memcpy(cur,nx,n*sizeof(int)); free(nx);
            }
            free(cur);
        }
        /* powtab[i][x][j] for i=0..dmax  -- coefficients of x^i */
        powtab=(unsigned char*)malloc((size_t)(dmax+1)*pn*n);
        sig=(unsigned char*)malloc((size_t)pn*n);
        if(!powtab||!sig){ fprintf(stderr,"alloc fail\n"); return 1; }
        int *xv=(int*)calloc(n,sizeof(int)); int *tv=(int*)calloc(n,sizeof(int)); int *pv=(int*)calloc(n,sizeof(int));
        /* FROBM[i][j] = coefficient j of (z^i)^{p^{n'}} : the matrix of sigma^{n'} */
        FROBM=(int*)calloc(n*n,sizeof(int));
        { int e[MAXN],o[MAXN];
          for(int i2=0;i2<n;i2++){ for(int j=0;j<n;j++) e[j]=0; e[i2]=1;
            kpow(e,ipow(P,np),o); for(int j=0;j<n;j++) FROBM[i2*n+j]=o[j]; } }
        for(long long x=0;x<pn;x++){
            long long t=x; for(int j=0;j<n;j++){ xv[j]=(int)(t%P); t/=P; }
            /* x^0 */
            for(int j=0;j<n;j++) powtab[(size_t)0*pn*n+(size_t)x*n+j]=0;
            powtab[(size_t)0*pn*n+(size_t)x*n+0]=1;
            memset(pv,0,n*sizeof(int)); pv[0]=1;
            for(int i=1;i<=dmax;i++){
                kmul(pv,xv,tv); memcpy(pv,tv,n*sizeof(int));
                for(int j=0;j<n;j++) powtab[(size_t)i*pn*n+(size_t)x*n+j]=(unsigned char)pv[j];
            }
            /* sigma^{n'}(x) = x^{p^{n'}} is F_p-LINEAR, so apply the precomputed matrix */
            for(int j=0;j<n;j++){ long long acc=0;
                for(int i2=0;i2<n;i2++) if(xv[i2]) acc+=(long long)xv[i2]*FROBM[i2*n+j];
                tv[j]=md(acc); }
            for(int j=0;j<n;j++) sig[(size_t)x*n+j]=(unsigned char)tv[j];
        }
        free(xv); free(tv); free(pv);
    }

    printf("#CELL p=%d n=%d nprime=%d q=%d r=%d degL=%lld p^(n-r)=n/a p^(np-r)=%lld p^n=%lld brute=%d\n",
           P,n,np,q,r,D,pnr,pn,do_brute);
    if(do_brute){ printf("#FIELD f="); for(int i=0;i<=f.deg;i++) printf("%d%s",f.c[i],i==f.deg?"":","); printf("\n"); }
    fflush(stdout);

    int *buf=(int*)malloc((size_t)((D-1)*P+2)*sizeof(int)); int bufcap=(int)((D-1)*P+2);

    for(int d=dmin;d<=dmax;d++){
        long long dq1=ipow(d,q+1);
        long long bound = dq1>pnr?dq1:pnr;
        long long ncand=(long long)(P-1)*ipow(P,d);
        long long nviol=0,ndegen=0,ndisagreeAB=0,ndisagreeC=0,nnotdiv=0,ndeg_gt=0;
        long long maxN=-1; long long maxN_code=-1; double maxratio=0.0; long long maxratio_code=-1;
        long long nboundary_lead_survive=0, nboundary_lead_cancel=0;
        poly lam,L,cur,G,xx,Lq1,Dp,tmp,Grt,Drt;
        pinit(&lam,d+2); pinit(&L,D+2); pinit(&cur,D+2); pinit(&G,D+2); pinit(&xx,4);
        pinit(&Lq1,(int)dq1+2); pinit(&Dp,(int)((dq1>pnr?dq1:pnr)+2)); pinit(&tmp,(int)((dq1>pnr?dq1:pnr)+2));
        pinit(&Grt,(int)((dq1>pnr?dq1:pnr)+2)); pinit(&Drt,(int)((dq1>pnr?dq1:pnr)+2));
        pmono(&xx,1,1);
        for(long long code=0;code<ncand;code+=stride){
            /* decode: leading coeff in 1..p-1, then d low coefficients base p */
            long long t=code; int lead=(int)(t%(P-1))+1; t/=(P-1);
            pzero(&lam); pensure(&lam,d+1);
            for(int i=0;i<d;i++){ lam.c[i]=(int)(t%P); t/=P; }
            lam.c[d]=lead; lam.deg=d;

            /* ---- instrument B : N = deg gcd(X^{p^n} - X, L) ---- */
            pzero(&L); pensure(&L,(int)D+1);
            L.c[D]=1; for(int i=0;i<=d;i++) L.c[i]=md(-lam.c[i]); L.deg=(int)D;
            pmono(&cur,1,1);
            for(int k=0;k<n;k++) pth_power_mod_L(&cur,(int)D,&lam,buf,bufcap);
            psub_into(&cur,&xx);
            pgcd(&G,&cur,&L);
            long long Ngcd=G.deg<0?0:G.deg;

            /* ---- instrument C : the derivation's own object ---- */
            pcopy(&Lq1,&lam);
            for(int k=1;k<=q;k++){ pcompose(&tmp,&Lq1,&lam); pcopy(&Lq1,&tmp); }
            pcopy(&Dp,&Lq1);
            { poly mm; pinit(&mm,(int)pnr+2); pmono(&mm,(int)pnr,1); psub_into(&Dp,&mm); pfree(&mm); }
            int Dzero = (Dp.deg<0);
            long long Nsig=-1, slack=-1; int divides=1;
            if(Dzero){ ndegen++; }
            else {
                if(Dp.deg>bound){ ndeg_gt++; printf("DEGVIOL d=%d code=%lld degD=%d bound=%lld\n",d,code,Dp.deg,bound); }
                /* injection step: the K-root set of L must divide D */
                if(G.deg>0){ pmod_poly(&tmp,&Dp,&G); if(tmp.deg>=0){ divides=0; nnotdiv++;
                        printf("NOTDIV d=%d code=%lld\n",d,code); } }
                /* K-roots of D, then the closing test L(x)=0 */
                xpn_mod_general(&Drt,n,&Dp);
                psub_into(&Drt,&xx);
                pgcd(&Grt,&Drt,&Dp);
                long long nDroots=Grt.deg<0?0:Grt.deg;
                poly gg; pinit(&gg,(int)D+2); pgcd(&gg,&Grt,&L); Nsig=gg.deg<0?0:gg.deg; pfree(&gg);
                slack=nDroots-Nsig;
                if(Nsig!=Ngcd){ ndisagreeC++; printf("C_DISAGREE d=%d code=%lld Ngcd=%lld Ninj=%lld\n",d,code,Ngcd,Nsig); }
                /* equal-degree boundary bookkeeping */
                if(dq1==pnr){ if(Dp.deg==(int)pnr) nboundary_lead_survive++; else nboundary_lead_cancel++; }
            }

            /* ---- instrument A : brute enumeration ---- */
            long long Nbr=-1;
            if(do_brute){
                Nbr=0;
                for(long long x=0;x<pn;x++){
                    long long acc=0;
                    for(int i=0;i<=d;i++) if(lam.c[i]) acc+=(long long)lam.c[i]*powtab[(size_t)i*pn*n+(size_t)x*n+0];
                    if(md(acc-sig[(size_t)x*n+0])) continue;
                    int ok=1;
                    for(int j=1;j<n&&ok;j++){
                        long long a2=0;
                        for(int i=0;i<=d;i++) if(lam.c[i]) a2+=(long long)lam.c[i]*powtab[(size_t)i*pn*n+(size_t)x*n+j];
                        if(md(a2-sig[(size_t)x*n+j])) ok=0;
                    }
                    if(ok) Nbr++;
                }
                if(Nbr!=Ngcd){ ndisagreeAB++; printf("AB_DISAGREE d=%d code=%lld Nbrute=%lld Ngcd=%lld\n",d,code,Nbr,Ngcd); }
            }

            long long N = Ngcd;
            if(!Dzero){
                if(N>bound){ nviol++;
                    printf("VIOLATION p=%d n=%d np=%d d=%d code=%lld N=%lld bound=%lld lam=",P,n,np,d,code,N,bound);
                    for(int i=0;i<=lam.deg;i++) printf("%d%s",lam.c[i],i==lam.deg?"":",");
                    printf("\n"); }
                double ratio=(double)N/(double)bound;
                if(ratio>maxratio){ maxratio=ratio; maxratio_code=code; }
            }
            if(N>maxN){ maxN=N; maxN_code=code; }
            if(verbose){
                printf("ROW d=%d code=%lld lam=",d,code);
                for(int i=0;i<=lam.deg;i++) printf("%d%s",lam.c[i],i==lam.deg?"":",");
                printf(" N=%lld Nbrute=%lld Ninj=%lld bound=%lld degD=%d Dzero=%d slack=%lld divides=%d\n",
                       Ngcd,Nbr,Nsig,bound,Dp.deg,Dzero,slack,divides);
            }
        }
        if(stride>1) ncand=(ncand+stride-1)/stride;
        printf("SUMMARY p=%d n=%d np=%d q=%d r=%d d=%d ncand=%lld dq1=%lld pnr=%lld bound=%lld "
               "violations=%lld degenerate=%lld degD_gt_bound=%lld notdiv=%lld AB_dis=%lld C_dis=%lld "
               "maxN=%lld maxN_code=%lld maxratio=%.6f maxratio_code=%lld boundary_lead_survive=%lld boundary_lead_cancel=%lld\n",
               P,n,np,q,r,d,ncand,dq1,pnr,bound,nviol,ndegen,ndeg_gt,nnotdiv,ndisagreeAB,ndisagreeC,
               maxN,maxN_code,maxratio,maxratio_code,nboundary_lead_survive,nboundary_lead_cancel);
        fflush(stdout);
        pfree(&lam); pfree(&L); pfree(&cur); pfree(&G); pfree(&xx); pfree(&Lq1); pfree(&Dp); pfree(&tmp); pfree(&Grt); pfree(&Drt);
    }
    return 0;
}
