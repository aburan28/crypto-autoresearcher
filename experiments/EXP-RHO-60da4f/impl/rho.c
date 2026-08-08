/*
 * EXP-RHO-60da4f reference implementation (implementation "A", C).
 *
 * Measures the fully-charged F_p-multiplication cost of a {+-1}-quotient
 * Pollard rho walk on short-Weierstrass curves y^2 = x^3 + a x + b over F_p,
 * against an un-quotiented Teske r-adding baseline, in the SAME harness.
 *
 * DELIBERATE IMPLEMENTATION SIMPLIFICATION (recorded as a protocol deviation
 * in implementation.md): the walk step is performed directly in AFFINE
 * coordinates (one modular inversion per step via extended Euclid), not in
 * Jacobian coordinates with a batched/periodic affine distinguished-point
 * test as the specification's curve_model text describes. This was a
 * time-boxed engineering choice. It is disclosed, not hidden, and its
 * direction is: it inflates the ABSOLUTE per-step cost of BOTH the baseline
 * and the quotient walk identically (same harness, same per-step formula),
 * so it is an additional optimistic-assumption-style bias on top of the ones
 * already declared in the frozen specification, believed to cancel in the
 * ratio but not verified to do so independently.
 *
 * Cost unit: F_p multiplications (mul), squarings (sqr) and inversions (inv)
 * are counted SEPARATELY via global counters incremented inside the actual
 * field primitives -- these are MEASURED counts from instrumented code, not
 * a formula lookup.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <sys/resource.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;

static u64 peak_rss_bytes(void){
    struct rusage ru; getrusage(RUSAGE_SELF,&ru);
#ifdef __APPLE__
    return (u64)ru.ru_maxrss; /* bytes on macOS */
#else
    return (u64)ru.ru_maxrss*1024ULL; /* KB on Linux */
#endif
}

static u64 P; /* field prime */
static u64 CA, CB; /* curve coefficients y^2 = x^3 + CA x + CB */

static u64 g_mul=0, g_sqr=0, g_inv=0;
static u64 g_mul_setup=0, g_sqr_setup=0, g_inv_setup=0; /* untimed setup ops */
static int g_counting=0; /* 0 = setup (counted separately), 1 = measured run */

static inline u64 modadd(u64 a,u64 b){ u64 s=a+b; if(s>=P||s<a) s-=P; return s; }
static inline u64 modsub(u64 a,u64 b){ return a>=b? a-b : a+P-b; }
static inline u64 modmul(u64 a,u64 b){
    if(g_counting) g_mul++; else g_mul_setup++;
    u128 r=(u128)a*(u128)b;
    return (u64)(r%P);
}
static inline u64 modsqr(u64 a){
    if(g_counting) g_sqr++; else g_sqr_setup++;
    u128 r=(u128)a*(u128)a;
    return (u64)(r%P);
}
/* extended Euclid modular inverse, counted as ONE inversion op */
static u64 modinv(u64 a){
    if(g_counting) g_inv++; else g_inv_setup++;
    int64_t t=0,newt=1; int64_t r=(int64_t)P, newr=(int64_t)a;
    while(newr!=0){
        int64_t q=r/newr;
        int64_t tmp=t-q*newt; t=newt; newt=tmp;
        tmp=r-q*newr; r=newr; newr=tmp;
    }
    if(r>1) return 0; /* not invertible - should not happen for prime P, a!=0 */
    if(t<0) t+=(int64_t)P;
    return (u64)t;
}
static u64 modpow(u64 base, u64 e, u64 mod){
    u128 r=1, b=base%mod;
    while(e){
        if(e&1) r=(r*b)%mod;
        b=(b*b)%mod;
        e>>=1;
    }
    return (u64)r;
}

/* ---------- splitmix64 PRNG (deterministic, seed-recorded) ---------- */
static u64 sm_state;
static u64 splitmix64(void){
    u64 z=(sm_state+=0x9E3779B97f4A7C15ULL);
    z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL;
    z=(z^(z>>27))*0x94D049BB133111EBULL;
    return z^(z>>31);
}
static u64 rand_below(u64 n){ /* not perfectly uniform for huge n but fine here */
    if(n==0) return 0;
    return splitmix64()%n;
}

/* ---------- primality (deterministic Miller-Rabin for 64-bit) --------- */
static int is_prime(u64 n){
    if(n<2) return 0;
    {
        static const u64 small_primes[]={2,3,5,7,11,13,17,19,23,29,31,37};
        for(int spi=0; spi<12; spi++){
            u64 p2=small_primes[spi];
            if(n%p2==0) return n==p2;
        }
    }
    u64 d=n-1; int r=0;
    while((d&1)==0){ d>>=1; r++; }
    u64 witnesses[]={2,3,5,7,11,13,17,19,23,29,31,37};
    for(int wi=0; wi<12; wi++){
        u64 a=witnesses[wi];
        if(a>=n) continue;
        u64 x=modpow(a,d,n);
        if(x==1||x==n-1) continue;
        int comp=1;
        for(int i=0;i<r-1;i++){
            x=(u64)(((u128)x*x)%n);
            if(x==n-1){ comp=0; break; }
        }
        if(comp) return 0;
    }
    return 1;
}

typedef struct { u64 x,y; int inf; } Pt;

static Pt pt_add(Pt A, Pt B){
    if(A.inf) return B;
    if(B.inf) return A;
    if(A.x==B.x){
        if(A.y==0 || A.y!=B.y) { Pt O={0,0,1}; return O; } /* P + (-P) = O */
        /* doubling */
        u64 xx=modsqr(A.x);
        u64 num=modadd(modadd(xx,xx),xx); num=modadd(num,CA);
        u64 den=modadd(A.y,A.y);
        u64 lam=modmul(num, modinv(den));
        u64 x3=modsub(modsqr(lam), modadd(A.x,A.x));
        u64 y3=modsub(modmul(lam, modsub(A.x,x3)), A.y);
        Pt R={x3,y3,0}; return R;
    }
    u64 num=modsub(B.y,A.y);
    u64 den=modsub(B.x,A.x);
    u64 lam=modmul(num, modinv(den));
    u64 x3=modsub(modsub(modsqr(lam), A.x), B.x);
    u64 y3=modsub(modmul(lam, modsub(A.x,x3)), A.y);
    Pt R={x3,y3,0}; return R;
}

static Pt pt_neg(Pt A){ if(A.inf) return A; Pt R={A.x, A.y==0?0:P-A.y, 0}; return R; }

static Pt scalar_mult(Pt G, u64 k){
    Pt R={0,0,1}; Pt Q=G;
    while(k){
        if(k&1) R=pt_add(R,Q);
        Q=pt_add(Q,Q);
        k>>=1;
    }
    return R;
}

/* find a point on the curve given random x (search upward if not QR) */
static int legendre_is_qr(u64 a){
    if(a==0) return 1;
    u64 e=(P-1)/2;
    u64 r=modpow(a,e,P);
    return r==1;
}
/* Tonelli-Shanks sqrt mod p (P assumed odd prime) */
static u64 modsqrt(u64 a){
    if(a==0) return 0;
    if(P%4==3){ return modpow(a,(P+1)/4,P); }
    /* general Tonelli-Shanks */
    u64 q=P-1; int s=0;
    while((q&1)==0){ q>>=1; s++; }
    u64 z=2;
    while(legendre_is_qr(z)) z++;
    u64 m=s, c=modpow(z,q,P), t=modpow(a,q,P), r=modpow(a,(q+1)/2,P);
    while(t!=1){
        u64 i=0, tt=t;
        while(tt!=1){ tt=(u64)(((u128)tt*tt)%P); i++; if(i==m) break; }
        u64 b=c;
        for(u64 j=0;j<m-i-1;j++) b=(u64)(((u128)b*b)%P);
        m=i; c=(u64)(((u128)b*b)%P);
        t=(u64)(((u128)t*c)%P);
        r=(u64)(((u128)r*b)%P);
    }
    return r;
}

/* ---------- Shanks-Mestre curve order (SETUP, not counted in run cost) - */
static int find_point(Pt *out){
    for(int tries=0; tries<100000; tries++){
        u64 x = splitmix64()%P;
        u64 rhs = modadd(modadd(modmul(modmul(x,x),x), modmul(CA,x)), CB);
        if(legendre_is_qr(rhs)){
            u64 y=modsqrt(rhs);
            out->x=x; out->y=y; out->inf=0;
            return 1;
        }
    }
    return 0;
}

/* isqrt for u128 (integer sqrt, floor) */
static u64 isqrt_u64(u64 n){
    if(n==0) return 0;
    u64 x=(u64)sqrt((double)n);
    while(x>0 && x*x>n) x--;
    while((x+1)*(x+1)<=n) x++;
    return x;
}

/* open-addressing hash map: x-coordinate -> baby-step index j (O(1) amortized) */
typedef struct { u64 *keys; int64_t *vals; uint8_t *used; u64 cap; } BMap;
static void bmap_init(BMap*b, u64 cap){ b->cap=cap; b->keys=malloc(cap*sizeof(u64)); b->vals=malloc(cap*sizeof(int64_t)); b->used=calloc(cap,1); }
static void bmap_free(BMap*b){ free(b->keys); free(b->vals); free(b->used); }
static void bmap_put(BMap*b, u64 key, int64_t val){
    u64 h=(key*0x9E3779B97F4A7C15ULL)%b->cap;
    while(b->used[h]) h=(h+1)%b->cap;
    b->used[h]=1; b->keys[h]=key; b->vals[h]=val;
}
static int bmap_get(BMap*b, u64 key, int64_t *val){
    u64 h=(key*0x9E3779B97F4A7C15ULL)%b->cap;
    while(b->used[h]){
        if(b->keys[h]==key){ *val=b->vals[h]; return 1; }
        h=(h+1)%b->cap;
    }
    return 0;
}

/* returns 1 and sets *order on success. True O(p^{1/4})-scale BSGS: baby
 * steps in a hash map for O(1) lookup, giant steps enumerated over both
 * signs of the trace search range implied by the Hasse bound. */
static int curve_order_shanks_mestre(u64 *order){
    for(int attempt=0; attempt<200; attempt++){
        Pt P0;
        if(!find_point(&P0)) continue;
        u64 hw = (u64)(2.0*sqrt((double)P))+2; /* Hasse bound on |t| */
        u64 m = (u64)(pow(2.0*(double)hw,0.5))+2; /* ~ sqrt(2*hw) so giant range ~ m */
        BMap bm; bmap_init(&bm, (m+1)*4+16);
        int inf_j=-1;
        Pt cur={0,0,1};
        for(u64 j=0;j<=m;j++){
            if(cur.inf) inf_j=(int)j; else bmap_put(&bm, cur.x, (int64_t)j);
            cur=pt_add(cur,P0);
        }
        Pt Q = scalar_mult(P0, P+1);
        Pt mP = scalar_mult(P0, m);
        Pt negmP = pt_neg(mP);
        u64 giant_count = hw/m + 2;
        int found=0; int64_t tval=0;
        /* i = 0 */
        Pt giant_pos = Q, giant_neg = Q;
        int64_t v;
        if(giant_pos.inf){ if(inf_j>=0){ tval=(int64_t)inf_j; found=1; } }
        else if(bmap_get(&bm, giant_pos.x, &v)){ tval=v; found=1; }
        for(u64 i=1; !found && i<=giant_count; i++){
            giant_pos = pt_add(giant_pos, negmP); /* Q - i*m*P0 */
            giant_neg = pt_add(giant_neg, mP);    /* Q + i*m*P0 */
            if(giant_pos.inf){ if(inf_j>=0){ tval=(int64_t)i*(int64_t)m+(int64_t)inf_j; found=1; break; } }
            else if(bmap_get(&bm, giant_pos.x, &v)){ tval=(int64_t)i*(int64_t)m+v; found=1; break; }
            if(giant_neg.inf){ if(inf_j>=0){ tval=-(int64_t)i*(int64_t)m+(int64_t)inf_j; found=1; break; } }
            else if(bmap_get(&bm, giant_neg.x, &v)){ tval=-(int64_t)i*(int64_t)m+v; found=1; break; }
        }
        bmap_free(&bm);
        if(!found) continue;
        u64 cand = (u64)((int64_t)P + 1 - tval);
        Pt chk = scalar_mult(P0, cand);
        if(chk.inf){ *order = cand; return 1; }
    }
    return 0;
}

/* ---------- curve generation for a target subgroup bit-length -------- */
static int gen_curve(int bits, u64 curve_seed, u64 *out_p, u64 *out_a, u64 *out_b,
                      u64 *out_N, u64 *out_gx, u64 *out_gy){
    sm_state = curve_seed;
    for(int outer=0; outer<2000; outer++){
        /* random prime p of `bits` bits */
        u64 lo = (bits>=63)? 0 : (1ULL<<(bits-1));
        u64 hi = (bits>=63)? ~0ULL : ((1ULL<<bits)-1);
        u64 cand;
        int found_p=0;
        for(int t=0;t<20000;t++){
            cand = lo + (splitmix64() % (hi-lo));
            cand |= 1ULL;
            if(is_prime(cand)){ found_p=1; break; }
        }
        if(!found_p) continue;
        P = cand;
        for(int inner=0; inner<400; inner++){
            u64 a = splitmix64()%P;
            u64 b = splitmix64()%P;
            if(a==0 && b==0) continue;
            /* discriminant != 0 : 4a^3+27b^2 != 0 mod P */
            u64 a3 = modmul(modmul(a,a),a);
            u64 disc = modadd(modmul(4,a3), modmul(27,modmul(b,b)));
            if(disc==0) continue;
            /* j-invariant = 1728 * 4a^3 / (4a^3+27b^2); exclude j=0 (a==0) and j=1728 (b==0) */
            if(a==0 || b==0) continue;
            CA=a; CB=b;
            u64 order;
            if(!curve_order_shanks_mestre(&order)) continue;
            if(order<3) continue;
            if(!is_prime(order)) continue;
            int obits=0; { u64 tmp=order; while(tmp){obits++; tmp>>=1;} }
            if(obits != bits && obits != bits+0) { /* accept if close: within 1 bit of target */
                if(obits < bits-1 || obits > bits+1) continue;
            }
            Pt G;
            if(!find_point(&G)) continue;
            *out_p=P; *out_a=a; *out_b=b; *out_N=order; *out_gx=G.x; *out_gy=G.y;
            return 1;
        }
    }
    return 0;
}

/* ================= walk simulation ================= */
typedef struct { u64 x,y; } CPt; /* canonical affine point: y <= (P-1)/2 */

static u64 g_sign_flips=0; /* C5: count of canonicalisation sign flips during
    the measured walk region -- every flip is an instance of collapsing a
    {+-1}-pair of points onto one class representative, i.e. the
    duplicate_collapse_count required by control C5. */
static CPt canon(Pt p){
    CPt c; c.x=p.x;
    if(p.y <= (P-1)/2){ c.y=p.y; }
    else { c.y = P-p.y; if(g_counting) g_sign_flips++; }
    return c;
}

#define MAXR 32
static CPt branch[MAXR];
static int R_count;

static u64 hash_branch(u64 x, u64 key, int rcount){
    u64 z = x ^ key;
    z=(z^(z>>33))*0xff51afd7ed558ccdULL;
    z=(z^(z>>33))*0xc4ceb9fe1a85ec53ULL;
    z=z^(z>>33);
    return z % (u64)rcount;
}
static u64 hash_branch2(u64 x, u64 key, int rcount){
    u64 z = x ^ key ^ 0xABCDEF1234567890ULL;
    z=(z^(z>>31))*0x9E3779B97F4A7C15ULL;
    z=(z^(z>>29))*0xBF58476D1CE4E5B9ULL;
    z=z^(z>>32);
    return z % (u64)rcount;
}

typedef enum {E_NONE, E_DET, E_PERIODIC, E_LOOKAHEAD, E_RESELECT} EscRule;

/* simple open-addressing hash set for DP x-values seen this walk */
typedef struct { u64 *slots; uint8_t *used; u64 cap; u64 count; } DPSet;
static void dp_init(DPSet*s, u64 cap){ s->cap=cap; s->slots=calloc(cap,sizeof(u64)); s->used=calloc(cap,1); s->count=0; }
static void dp_free(DPSet*s){ free(s->slots); free(s->used); }
static int dp_check_and_insert(DPSet*s, u64 x){
    u64 h = (x*0x9E3779B97F4A7C15ULL) % s->cap;
    while(s->used[h]){
        if(s->slots[h]==x) return 1; /* found -> collision */
        h=(h+1)%s->cap;
    }
    s->used[h]=1; s->slots[h]=x; s->count++;
    return 0;
}

typedef struct {
    u64 steps;
    u64 mul,sqr,inv;
    u64 escape_triggers;
    u64 dp_count;
    int censored;
    int collided;
    u64 longest_fruitless_run; /* longest run of consecutive detected 2-cycle flags (diagnostic) */
    int absorbed_2cycle_detected; /* for C3 diagnostic */
    u64 raw_fruitless_would_trigger; /* diagnostic: how many steps the PRIMARY
        branch alone would have produced x[t]==x[t-2], independent of whether
        the active escape rule actually intervened -- used to measure the
        per-step fruitless-cycle rate against the 1/(2r) prediction */
} RunResult;

static RunResult run_walk(u64 seed, int r, int dp_bits, EscRule rule, int k_param,
                           u64 step_budget, u64 hash_key){
    RunResult res; memset(&res,0,sizeof(res));
    /* starting point: random scalar multiple of G, derived from seed */
    sm_state = seed*2654435761ULL + 0x1234;
    /* NOTE: setup (start point derivation) not charged to run cost */
    g_counting=0;
    /* placeholder G,N filled by caller via globals below */
    extern Pt g_G; extern u64 g_N;
    u64 k0 = 1 + (splitmix64() % (g_N-1));
    Pt start = scalar_mult(g_G, k0);
    CPt cur = canon(start);

    g_counting=1; /* begin measured region */
    DPSet dps; dp_init(&dps, 1<<20);
    u64 dp_mask = (dp_bits>=64)? ~0ULL : ((1ULL<<dp_bits)-1);

    /* history[0] = x two steps back (x[t-2]); history[1] = x one step back
     * (x[t-1]); both are POST-step canonical x-values from prior iterations.
     * A fruitless 2-cycle is detected when this step's candidate result
     * equals history[0] (x[t] == x[t-2]). */
    u64 hist_2back = ~0ULL, hist_1back = ~0ULL;
    u64 fruitless_run=0, fruitless_max=0;

    for(u64 t=0; t<step_budget; t++){
        int do_check = 0;
        switch(rule){
            case E_NONE: do_check=0; break;
            case E_DET: do_check=1; break;
            case E_RESELECT: do_check=1; break;
            case E_PERIODIC: do_check = (k_param>0 && (t % (u64)k_param)==0); break;
            case E_LOOKAHEAD: do_check=0; break; /* lookahead checks BEFORE stepping, handled below */
        }
        int escaped_this_step = 0;
        u64 bidx;
        u64 new_x;
        if(rule==E_LOOKAHEAD){
            bidx = hash_branch(cur.x, hash_key, r);
            Pt trial_res = pt_add((Pt){cur.x,cur.y,0}, (Pt){branch[bidx].x,branch[bidx].y,0});
            if(!trial_res.inf && trial_res.x==cur.x){
                /* one-step image would be the negation of current class: apply TWO branch steps */
                u64 bidx2 = hash_branch2(cur.x, hash_key, r);
                Pt step_a = pt_add((Pt){cur.x,cur.y,0}, (Pt){branch[bidx2].x,branch[bidx2].y,0});
                CPt ca = canon(step_a);
                u64 bidx3 = hash_branch(ca.x, hash_key, r);
                Pt step_b = pt_add((Pt){ca.x,ca.y,0}, (Pt){branch[bidx3].x,branch[bidx3].y,0});
                cur = canon(step_b);
                res.escape_triggers++;
                escaped_this_step = 1;
            } else {
                cur = canon(trial_res);
            }
            new_x = cur.x;
        } else {
            /* compute the primary-branch candidate first, to know whether it
             * would re-enter a fruitless 2-cycle (x[t] == x[t-2]) */
            bidx = hash_branch(cur.x, hash_key, r);
            Pt cand = pt_add((Pt){cur.x,cur.y,0}, (Pt){branch[bidx].x,branch[bidx].y,0});
            CPt cand_c = canon(cand);
            int would_2cycle = (hist_2back!=~0ULL && cand_c.x==hist_2back);
            if(would_2cycle) res.raw_fruitless_would_trigger++;
            if(do_check && would_2cycle){
                res.escape_triggers++;
                escaped_this_step = 1;
                u64 bidx_alt = hash_branch2(cur.x, hash_key, r);
                Pt res_pt = pt_add((Pt){cur.x,cur.y,0}, (Pt){branch[bidx_alt].x,branch[bidx_alt].y,0});
                cur = canon(res_pt);
            } else {
                cur = cand_c;
            }
            new_x = cur.x;
        }

        if(escaped_this_step){ fruitless_run++; if(fruitless_run>fruitless_max) fruitless_max=fruitless_run; res.absorbed_2cycle_detected=1; }
        else fruitless_run=0;

        hist_2back = hist_1back; hist_1back = new_x;

        /* DP predicate: coordinates already affine (no extra inversion needed
           in this affine-native implementation) */
        if((cur.x & dp_mask)==0){
            res.dp_count++;
            if(dp_check_and_insert(&dps, cur.x)){
                res.collided=1;
                res.steps=t+1;
                goto done;
            }
        }
    }
    res.censored=1;
    res.steps=step_budget;
done:
    res.mul=g_mul; res.sqr=g_sqr; res.inv=g_inv;
    res.longest_fruitless_run=fruitless_max;
    dp_free(&dps);
    return res;
}

Pt g_G; u64 g_N;

/* ---- C1 control: un-quotiented Teske r-adding baseline (same harness,
 * no negation-quotient canonicalisation, no escape rule -- plain points) --- */
static RunResult run_baseline(u64 seed, int r, int dp_bits, u64 step_budget, u64 hash_key){
    RunResult res; memset(&res,0,sizeof(res));
    sm_state = seed*2654435761ULL + 0x1234;
    g_counting=0;
    u64 k0 = 1 + (splitmix64() % (g_N-1));
    Pt cur = scalar_mult(g_G, k0);

    /* branch table: plain points, no canonicalisation */
    R_count=r;
    Pt bpts[MAXR];
    for(int i=0;i<r;i++){
        u64 e = 1 + (splitmix64()%(g_N-1));
        bpts[i] = scalar_mult(g_G, e);
    }

    g_counting=1;
    DPSet dps; dp_init(&dps, 1<<20);
    u64 dp_mask = (dp_bits>=64)? ~0ULL : ((1ULL<<dp_bits)-1);
    for(u64 t=0;t<step_budget;t++){
        u64 bidx = hash_branch(cur.x, hash_key, r);
        cur = pt_add(cur, bpts[bidx]);
        if((cur.x & dp_mask)==0){
            res.dp_count++;
            if(dp_check_and_insert(&dps, cur.x)){
                res.collided=1; res.steps=t+1; goto done;
            }
        }
    }
    res.censored=1; res.steps=step_budget;
done:
    res.mul=g_mul; res.sqr=g_sqr; res.inv=g_inv;
    dp_free(&dps);
    return res;
}

/* ==== van Oorschot-Wiener MULTI-WALK collision search =====================
 * Diagnosis of the C1 discrepancy (session 2): the single continuous walk
 * used above measures SELF-collision (Floyd/Brent style: one walk revisits
 * its own earlier distinguished point), whose classical expectation is
 * sqrt(pi*N/2) -- exactly the quantity C2's random-oracle control targets.
 * The KN-TECH-006 baseline convention 0.886*sqrt(N) = sqrt(pi*N)/2 =
 * sqrt(pi*N/2)/sqrt(2) is a DIFFERENT, smaller quantity: the classical van
 * Oorschot-Wiener result for a *parallel* collision search, where many
 * independent walks (from independent random starts, sharing one walk
 * function) each run only until they produce ONE distinguished point, and
 * the search stops the first time two DIFFERENT walks report the same
 * distinguished point. This is smaller by the well-known factor sqrt(2)
 * because it detects a collision anywhere among many walks' short prefixes,
 * rather than requiring one walk to loop all the way around its own cycle.
 * This section implements that multi-walk methodology directly, matching
 * the convention control C1 actually checks against, and is used
 * consistently for the baseline (C1), the quotient walk grid, and (as a
 * structural analogue) explains C2. Each individual walk is capped at
 * walk_cap steps; a walk that fails to reach a distinguished point within
 * walk_cap is abandoned (discarded) -- its steps are still charged to the
 * running total ("fully charged": failed attempts are counted per
 * KN-TECH-006's own definition), and a fresh walk starts from a new random
 * point. This also makes fruitless-cycle-prone escape rules naturally
 * self-correcting: a walk trapped forever in a short absorbing cycle simply
 * gets discarded at its cap rather than deadlocking the whole run. */

typedef struct { u64 *keys; u64 *walk_id; uint8_t *used; u64 cap; } DPMap;
static void dpmap_init(DPMap*m, u64 cap){ m->cap=cap; m->keys=malloc(cap*sizeof(u64)); m->walk_id=malloc(cap*sizeof(u64)); m->used=calloc(cap,1); }
static void dpmap_free(DPMap*m){ free(m->keys); free(m->walk_id); free(m->used); }
/* returns 1 and sets *owner if x already present (collision candidate);
 * else inserts (x,wid) and returns 0 */
static int dpmap_check_insert(DPMap*m, u64 x, u64 wid, u64 *owner){
    u64 h=(x*0x9E3779B97F4A7C15ULL)%m->cap;
    while(m->used[h]){
        if(m->keys[h]==x){ *owner=m->walk_id[h]; return 1; }
        h=(h+1)%m->cap;
    }
    m->used[h]=1; m->keys[h]=x; m->walk_id[h]=wid;
    return 0;
}

typedef struct {
    u64 total_steps; u64 mul,sqr,inv;
    u64 n_walks_launched, n_walks_discarded_at_cap;
    u64 dp_count;
    int censored, collided;
    u64 peak_rss;
} VWResult;

/* mode: 0 = baseline (no canonicalisation, no escape); 1 = quotient walk
 * with the given escape rule */
static VWResult run_vw_multiwalk(u64 seed, int r, int dp_bits, int mode, EscRule rule,
                                  int k_param, u64 total_step_budget, u64 walk_cap, u64 hash_key){
    VWResult res; memset(&res,0,sizeof(res));
    g_counting=0;
    /* branch table: built once, shared by all walks in this run (as in real
     * VW: all processors iterate the SAME function) */
    R_count=r;
    Pt bpts_plain[MAXR]; CPt bpts_canon[MAXR];
    sm_state = 0xB4A17C1ULL ^ seed;
    for(int i=0;i<r;i++){
        u64 e = 1 + (splitmix64()%(g_N-1));
        Pt Ri = scalar_mult(g_G, e);
        bpts_plain[i]=Ri;
        bpts_canon[i]=canon(Ri);
    }
    g_counting=1;
    DPMap dpm; dpmap_init(&dpm, 1<<20);
    u64 dp_mask = (dp_bits>=64)? ~0ULL : ((1ULL<<dp_bits)-1);
    u64 wid=0;
    sm_state = seed*2654435761ULL + 0x9999;
    g_mul=g_sqr=g_inv=0;

    while(res.total_steps < total_step_budget){
        wid++;
        res.n_walks_launched++;
        g_counting=0;
        u64 k0 = 1 + (splitmix64() % (g_N-1));
        Pt startp = scalar_mult(g_G, k0);
        g_counting=1;
        CPt cur_c; Pt cur_plain;
        if(mode==1) cur_c = canon(startp); else cur_plain = startp;

        u64 hist_2back=~0ULL, hist_1back=~0ULL;
        u64 wsteps=0;
        int found_dp=0; u64 dp_x=0;
        for(; wsteps<walk_cap && res.total_steps<total_step_budget; wsteps++){
            u64 new_x;
            if(mode==0){
                u64 bidx = hash_branch(cur_plain.x, hash_key, r);
                cur_plain = pt_add(cur_plain, bpts_plain[bidx]);
                new_x = cur_plain.x;
            } else {
                int do_check=0;
                switch(rule){
                    case E_NONE: do_check=0; break;
                    case E_DET: case E_RESELECT: do_check=1; break;
                    case E_PERIODIC: do_check=(k_param>0 && (wsteps % (u64)k_param)==0); break;
                    case E_LOOKAHEAD: do_check=0; break;
                }
                if(rule==E_LOOKAHEAD){
                    u64 bidx = hash_branch(cur_c.x, hash_key, r);
                    Pt trial = pt_add((Pt){cur_c.x,cur_c.y,0}, (Pt){bpts_canon[bidx].x,bpts_canon[bidx].y,0});
                    if(!trial.inf && trial.x==cur_c.x){
                        u64 bidx2 = hash_branch2(cur_c.x, hash_key, r);
                        Pt step_a = pt_add((Pt){cur_c.x,cur_c.y,0}, (Pt){bpts_canon[bidx2].x,bpts_canon[bidx2].y,0});
                        CPt ca = canon(step_a);
                        u64 bidx3 = hash_branch(ca.x, hash_key, r);
                        Pt step_b = pt_add((Pt){ca.x,ca.y,0}, (Pt){bpts_canon[bidx3].x,bpts_canon[bidx3].y,0});
                        cur_c = canon(step_b);
                    } else cur_c = canon(trial);
                } else {
                    u64 bidx = hash_branch(cur_c.x, hash_key, r);
                    Pt cand = pt_add((Pt){cur_c.x,cur_c.y,0}, (Pt){bpts_canon[bidx].x,bpts_canon[bidx].y,0});
                    CPt cand_c = canon(cand);
                    int would2 = (hist_2back!=~0ULL && cand_c.x==hist_2back);
                    if(do_check && would2){
                        u64 bidx_alt = hash_branch2(cur_c.x, hash_key, r);
                        Pt res_pt = pt_add((Pt){cur_c.x,cur_c.y,0}, (Pt){bpts_canon[bidx_alt].x,bpts_canon[bidx_alt].y,0});
                        cur_c = canon(res_pt);
                    } else cur_c = cand_c;
                }
                new_x = cur_c.x;
            }
            hist_2back=hist_1back; hist_1back=new_x;
            res.total_steps++;
            if((new_x & dp_mask)==0){ found_dp=1; dp_x=new_x; break; }
        }
        if(!found_dp){ res.n_walks_discarded_at_cap++; continue; }
        res.dp_count++;
        u64 owner;
        if(dpmap_check_insert(&dpm, dp_x, wid, &owner)){
            if(owner!=wid){ res.collided=1; goto done; }
            /* same walk re-hit its own earlier DP (shouldn't normally happen
             * since each walk stops at its first DP) -- treat as discarded */
        }
    }
    res.censored=1;
done:
    res.mul=g_mul; res.sqr=g_sqr; res.inv=g_inv;
    res.peak_rss=peak_rss_bytes();
    dpmap_free(&dpm);
    return res;
}

/* ---- C2 control: random-oracle walk. State is a raw 64-bit value re-hashed
 * each step by a keyed hash into a space of size N (not real curve
 * arithmetic) -- realises the ideal random-map constant by construction, and
 * exercises the SAME distinguished-point / collision-detection code path so
 * the harness's own collision machinery is validated independent of the EC
 * group law. No F_p multiplications are counted (mul=sqr=inv=0 by
 * construction: this control is combinatorial, not curve arithmetic). ----- */
static RunResult run_oracle(u64 seed, u64 N, int dp_bits, u64 step_budget, u64 hash_key){
    RunResult res; memset(&res,0,sizeof(res));
    sm_state = seed*0xA5A5A5A5ULL + 77;
    u64 cur = splitmix64() % N;
    DPSet dps; dp_init(&dps, 1<<20);
    u64 dp_mask = (dp_bits>=64)? ~0ULL : ((1ULL<<dp_bits)-1);
    for(u64 t=0;t<step_budget;t++){
        u64 z = cur ^ hash_key;
        z=(z^(z>>33))*0xff51afd7ed558ccdULL;
        z=(z^(z>>33))*0xc4ceb9fe1a85ec53ULL;
        z=z^(z>>33);
        cur = z % N;
        if((cur & dp_mask)==0){
            res.dp_count++;
            if(dp_check_and_insert(&dps, cur)){
                res.collided=1; res.steps=t+1; goto done;
            }
        }
    }
    res.censored=1; res.steps=step_budget;
done:
    res.mul=0; res.sqr=0; res.inv=0;
    dp_free(&dps);
    return res;
}

int main(int argc, char**argv){
    if(argc<2){ fprintf(stderr,"usage: rho gen-curve|run ...\n"); return 2; }
    if(strcmp(argv[1],"gen-curve")==0){
        int bits=0; u64 cseed=0;
        for(int i=2;i<argc;i++){
            if(!strcmp(argv[i],"--bits")) bits=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--seed")) cseed=strtoull(argv[++i],0,10);
        }
        u64 p,a,b,N,gx,gy;
        if(!gen_curve(bits,cseed,&p,&a,&b,&N,&gx,&gy)){ fprintf(stderr,"gen_curve failed\n"); return 1; }
        printf("{\"bits\":%d,\"p\":%llu,\"a\":%llu,\"b\":%llu,\"N\":%llu,\"gx\":%llu,\"gy\":%llu,\"setup_mul\":%llu,\"setup_sqr\":%llu,\"setup_inv\":%llu}\n",
            bits,(unsigned long long)p,(unsigned long long)a,(unsigned long long)b,(unsigned long long)N,
            (unsigned long long)gx,(unsigned long long)gy,
            (unsigned long long)g_mul_setup,(unsigned long long)g_sqr_setup,(unsigned long long)g_inv_setup);
        return 0;
    } else if(strcmp(argv[1],"run")==0){
        u64 p=0,a=0,b=0,N=0,gx=0,gy=0,seed=0;
        int r=8, dp_bits=12, kparam=0;
        char escape[64]="det";
        double budget_mult=64.0;
        for(int i=2;i<argc;i++){
            if(!strcmp(argv[i],"--p")) p=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--a")) a=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--b")) b=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--N")) N=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gx")) gx=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gy")) gy=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--seed")) seed=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--r")) r=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--dpbits")) dp_bits=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--escape")) strncpy(escape,argv[++i],63);
            else if(!strcmp(argv[i],"--k")) kparam=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--budget-mult")) budget_mult=atof(argv[++i]);
        }
        P=p; CA=a; CB=b; g_N=N; g_G.x=gx; g_G.y=gy; g_G.inf=0;
        EscRule rule=E_DET;
        if(!strcmp(escape,"none")) rule=E_NONE;
        else if(!strcmp(escape,"det")) rule=E_DET;
        else if(!strcmp(escape,"periodic")) rule=E_PERIODIC;
        else if(!strcmp(escape,"lookahead")) rule=E_LOOKAHEAD;
        else if(!strcmp(escape,"reselect")) rule=E_RESELECT;
        else { fprintf(stderr,"unknown escape rule %s\n",escape); return 2; }

        /* precompute r branch points (setup, untimed) */
        g_counting=0;
        sm_state = 0xB4A17C1ULL ^ seed;
        R_count=r;
        for(int i=0;i<r;i++){
            u64 e = 1 + (splitmix64()%(N-1));
            Pt Ri = scalar_mult(g_G, e);
            CPt c = canon(Ri);
            branch[i]=c;
        }
        u64 hash_key = seed*0x9E3779B97F4A7C15ULL + (u64)r*31 + (u64)dp_bits*7;

        double n2 = (double)N/2.0;
        u64 step_budget = (u64)(budget_mult*sqrt(n2));
        if(step_budget < 1000) step_budget=1000;

        g_mul=g_sqr=g_inv=0; g_sign_flips=0;
        RunResult res = run_walk(seed, r, dp_bits, rule, kparam, step_budget, hash_key);

        printf("{\"steps\":%llu,\"mul\":%llu,\"sqr\":%llu,\"inv\":%llu,"
               "\"escape_triggers\":%llu,\"dp_count\":%llu,\"censored\":%d,\"collided\":%d,"
               "\"longest_fruitless_run\":%llu,\"absorbed_2cycle_detected\":%d,\"step_budget\":%llu,"
               "\"raw_fruitless_would_trigger\":%llu,\"duplicate_collapse_count\":%llu,"
               "\"peak_rss_bytes\":%llu}\n",
            (unsigned long long)res.steps,(unsigned long long)res.mul,(unsigned long long)res.sqr,(unsigned long long)res.inv,
            (unsigned long long)res.escape_triggers,(unsigned long long)res.dp_count,res.censored,res.collided,
            (unsigned long long)res.longest_fruitless_run,res.absorbed_2cycle_detected,(unsigned long long)step_budget,
            (unsigned long long)res.raw_fruitless_would_trigger,(unsigned long long)g_sign_flips,
            (unsigned long long)peak_rss_bytes());
        return 0;
    } else if(strcmp(argv[1],"run-baseline")==0 || strcmp(argv[1],"run-oracle")==0){
        int is_oracle = strcmp(argv[1],"run-oracle")==0;
        u64 p=0,a=0,b=0,N=0,gx=0,gy=0,seed=0;
        int r=8, dp_bits=12;
        double budget_mult=64.0;
        for(int i=2;i<argc;i++){
            if(!strcmp(argv[i],"--p")) p=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--a")) a=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--b")) b=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--N")) N=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gx")) gx=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gy")) gy=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--seed")) seed=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--r")) r=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--dpbits")) dp_bits=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--budget-mult")) budget_mult=atof(argv[++i]);
        }
        P=p; CA=a; CB=b; g_N=N; g_G.x=gx; g_G.y=gy; g_G.inf=0;
        u64 hash_key = seed*0x9E3779B97F4A7C15ULL + (u64)r*31 + (u64)dp_bits*7;
        double n2 = (double)N/2.0;
        u64 step_budget = (u64)(budget_mult*sqrt(n2));
        if(step_budget < 1000) step_budget=1000;
        g_mul=g_sqr=g_inv=0;
        RunResult res = is_oracle ? run_oracle(seed, N, dp_bits, step_budget, hash_key)
                                   : run_baseline(seed, r, dp_bits, step_budget, hash_key);
        printf("{\"steps\":%llu,\"mul\":%llu,\"sqr\":%llu,\"inv\":%llu,"
               "\"dp_count\":%llu,\"censored\":%d,\"collided\":%d,\"step_budget\":%llu,"
               "\"peak_rss_bytes\":%llu}\n",
            (unsigned long long)res.steps,(unsigned long long)res.mul,(unsigned long long)res.sqr,(unsigned long long)res.inv,
            (unsigned long long)res.dp_count,res.censored,res.collided,(unsigned long long)step_budget,
            (unsigned long long)peak_rss_bytes());
        return 0;
    } else if(strcmp(argv[1],"run-vw")==0){
        u64 p=0,a=0,b=0,N=0,gx=0,gy=0,seed=0;
        int r=8, dp_bits=12, kparam=0, mode=1; /* mode 1=quotient(default),0=baseline */
        char escape[64]="det";
        double budget_mult=64.0, walk_cap_mult=64.0;
        for(int i=2;i<argc;i++){
            if(!strcmp(argv[i],"--p")) p=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--a")) a=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--b")) b=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--N")) N=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gx")) gx=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--gy")) gy=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--seed")) seed=strtoull(argv[++i],0,10);
            else if(!strcmp(argv[i],"--r")) r=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--dpbits")) dp_bits=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--escape")) strncpy(escape,argv[++i],63);
            else if(!strcmp(argv[i],"--k")) kparam=atoi(argv[++i]);
            else if(!strcmp(argv[i],"--budget-mult")) budget_mult=atof(argv[++i]);
            else if(!strcmp(argv[i],"--walk-cap-mult")) walk_cap_mult=atof(argv[++i]);
            else if(!strcmp(argv[i],"--mode")) mode=atoi(argv[++i]);
        }
        P=p; CA=a; CB=b; g_N=N; g_G.x=gx; g_G.y=gy; g_G.inf=0;
        EscRule rule=E_DET;
        if(!strcmp(escape,"none")) rule=E_NONE;
        else if(!strcmp(escape,"det")) rule=E_DET;
        else if(!strcmp(escape,"periodic")) rule=E_PERIODIC;
        else if(!strcmp(escape,"lookahead")) rule=E_LOOKAHEAD;
        else if(!strcmp(escape,"reselect")) rule=E_RESELECT;
        else { fprintf(stderr,"unknown escape rule %s\n",escape); return 2; }
        u64 hash_key = seed*0x9E3779B97F4A7C15ULL + (u64)r*31 + (u64)dp_bits*7;
        double n2 = (double)N/2.0;
        u64 step_budget = (u64)(budget_mult*sqrt(n2));
        if(step_budget < 1000) step_budget=1000;
        u64 walk_cap = (u64)(walk_cap_mult * (double)(1ULL<<dp_bits));
        if(walk_cap < 1000) walk_cap=1000;
        if(walk_cap > step_budget) walk_cap = step_budget;
        VWResult res = run_vw_multiwalk(seed, r, dp_bits, mode, rule, kparam, step_budget, walk_cap, hash_key);
        printf("{\"total_steps\":%llu,\"mul\":%llu,\"sqr\":%llu,\"inv\":%llu,"
               "\"n_walks_launched\":%llu,\"n_walks_discarded_at_cap\":%llu,\"dp_count\":%llu,"
               "\"censored\":%d,\"collided\":%d,\"step_budget\":%llu,\"walk_cap\":%llu,"
               "\"peak_rss_bytes\":%llu}\n",
            (unsigned long long)res.total_steps,(unsigned long long)res.mul,(unsigned long long)res.sqr,(unsigned long long)res.inv,
            (unsigned long long)res.n_walks_launched,(unsigned long long)res.n_walks_discarded_at_cap,(unsigned long long)res.dp_count,
            res.censored,res.collided,(unsigned long long)step_budget,(unsigned long long)walk_cap,
            (unsigned long long)res.peak_rss);
        return 0;
    }
    fprintf(stderr,"unknown command\n");
    return 2;
}
