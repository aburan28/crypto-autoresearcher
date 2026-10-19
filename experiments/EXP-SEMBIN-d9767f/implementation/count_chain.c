/* count_chain.c -- PILOT #2 (m45closure). Exhaustive Boolean solution count of
 * a chained-S_3 Weil descent with general chain length t = m >= 3, written for
 * this pilot (generalises count_affu.c, which handled one u block).
 *
 * Variable layout (boolsys.generate): u_i bits [i*n, (i+1)*n) for i = 0..m-3,
 * x_j bits [(m-2)*n + j*k, ...) for j = 0..m-1.
 * Block i (i = 0..m-2) is the descent of one S_3 and may touch:
 *   block 0:        u_0, x_0, x_1
 *   block 1..m-3:   u_{i-1}, u_i, x_{i+1}
 *   block m-2:      u_{m-3}, x_{m-1}
 * Every monomial contains at most one bit of the block's "new" u (u_i for
 * i <= m-3), so for every assignment of the x's the blocks are solved in order,
 * each an affine GF(2) system in its new u given the previous u.  Equations are
 * assigned to blocks by their variable support; a violation returns -1.
 *
 * count_chain(N, n, m, k, neq, ptr, masks, sol_out, sol_cap, &nsol)
 *   returns the number of Boolean solutions (long long), -1 on a structural
 *   violation, -2 if some equation is the constant 1 (then the count is 0 and
 *   the caller may treat it as UNSAT).  Up to sol_cap solution masks are
 *   written to sol_out.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

typedef struct { int ubit; u64 rest; } term_t;     /* ubit = -1: no new-u bit */
typedef struct { int neq; int *cnt; term_t **t; } blk_t;

static int ins(u64 *piv, u64 row, int nu) {
    u64 um = (nu >= 64) ? ~0ULL : ((1ULL << nu) - 1);
    for (;;) {
        u64 ub = row & um;
        if (!ub) return ((row >> nu) & 1) ? -1 : 0;
        int top = 63 - __builtin_clzll(ub);
        if (piv[top]) row ^= piv[top];
        else { piv[top] = row; return 1; }
    }
}

static int N_, n_, m_, k_;
static blk_t *blk_;
static u64 *sol_out_; static long sol_cap_, ns_;
static long long total_;

/* assign holds all x bits and u_0..u_{i-1}; solve block i */
static void solve_block(int i, u64 assign) {
    blk_t *B = &blk_[i];
    if (i == m_ - 2) {                      /* last block: pure check */
        for (int e = 0; e < B->neq; e++) {
            int v = 0;
            for (int j = 0; j < B->cnt[e]; j++) {
                u64 r = B->t[e][j].rest;
                if ((r & assign) == r) v ^= 1;
            }
            if (v) return;
        }
        total_++;
        if (ns_ < sol_cap_) sol_out_[ns_++] = assign;
        return;
    }
    int nu = n_;
    u64 piv[65]; memset(piv, 0, sizeof piv);
    int rk = 0;
    for (int e = 0; e < B->neq; e++) {
        u64 row = 0;
        for (int j = 0; j < B->cnt[e]; j++) {
            u64 r = B->t[e][j].rest;
            if ((r & assign) == r) {
                int ub = B->t[e][j].ubit;
                row ^= (ub < 0) ? (1ULL << nu) : (1ULL << ub);
            }
        }
        int rr = ins(piv, row, nu);
        if (rr < 0) return;
        rk += rr;
    }
    int fv[64], nf = 0;
    for (int c = 0; c < nu; c++) if (!piv[c]) fv[nf++] = c;
    u64 um = (nu >= 64) ? ~0ULL : ((1ULL << nu) - 1);
    for (long f = 0; f < (1L << nf); f++) {
        u64 uval = 0;
        for (int b = 0; b < nf; b++) if ((f >> b) & 1) uval |= 1ULL << fv[b];
        for (int c = 0; c < nu; c++) if (piv[c]) {
            u64 row = piv[c];
            int v = (int)((row >> nu) & 1);
            u64 rest = row & um & ~(1ULL << c);
            v ^= __builtin_popcountll(rest & uval) & 1;
            if (v) uval |= 1ULL << c;
        }
        solve_block(i + 1, assign | (uval << (i * n_)));
    }
}

long long count_chain(int N, int n, int m, int k, int neq, const long *ptr, const u64 *masks,
                      u64 *sol_out, long sol_cap, long *nsol) {
    N_ = N; n_ = n; m_ = m; k_ = k;
    int nb = m - 1;
    u64 *umask = calloc(m, sizeof(u64)), *xmask = calloc(m, sizeof(u64));
    for (int i = 0; i < m - 2; i++) umask[i] = (((n >= 64) ? ~0ULL : ((1ULL << n) - 1)) << (i * n));
    for (int j = 0; j < m; j++) xmask[j] = (((1ULL << k) - 1) << ((m - 2) * n + j * k));
    u64 *allowed = calloc(nb, sizeof(u64)); int *newu = calloc(nb, sizeof(int));
    for (int i = 0; i < nb; i++) {
        u64 a = 0;
        if (i == 0) a = umask[0] | xmask[0] | xmask[1];
        else if (i < m - 2) a = umask[i - 1] | umask[i] | xmask[i + 1];
        else a = umask[m - 3] | xmask[m - 1];
        allowed[i] = a; newu[i] = (i < m - 2) ? i : -1;
    }
    blk_ = calloc(nb, sizeof(blk_t));
    int *bof = malloc(sizeof(int) * neq);
    int bad = 0, const_one = 0;
    for (int e = 0; e < neq; e++) {
        u64 sup = 0;
        for (long p = ptr[e]; p < ptr[e + 1]; p++) sup |= masks[p];
        if (sup == 0) {               /* constant equation */
            long c = ptr[e + 1] - ptr[e];
            bof[e] = -1;
            if (c & 1) const_one = 1;
            continue;
        }
        int b = -1;
        for (int i = 0; i < nb; i++) if ((sup & ~allowed[i]) == 0) { b = i; break; }
        if (b < 0) { bad = 1; bof[e] = -1; continue; }
        bof[e] = b; blk_[b].neq++;
    }
    if (bad) { free(umask); free(xmask); free(allowed); free(newu); free(blk_); free(bof); return -1; }
    for (int i = 0; i < nb; i++) { blk_[i].cnt = calloc(blk_[i].neq ? blk_[i].neq : 1, sizeof(int)); blk_[i].t = calloc(blk_[i].neq ? blk_[i].neq : 1, sizeof(term_t *)); blk_[i].neq = 0; }
    for (int e = 0; e < neq; e++) {
        int b = bof[e]; if (b < 0) continue;
        int idx = blk_[b].neq++;
        long c = ptr[e + 1] - ptr[e];
        blk_[b].cnt[idx] = (int)c;
        blk_[b].t[idx] = malloc(sizeof(term_t) * (c ? c : 1));
        u64 nu = (newu[b] >= 0) ? umask[newu[b]] : 0;
        for (long p = 0; p < c; p++) {
            u64 mm = masks[ptr[e] + p];
            u64 ub = mm & nu;
            if (__builtin_popcountll(ub) > 1) bad = 1;
            blk_[b].t[idx][p].ubit = ub ? (__builtin_ctzll(ub) - newu[b] * n) : -1;
            blk_[b].t[idx][p].rest = mm & ~nu;
        }
    }
    long long ret;
    if (bad) ret = -1;
    else if (const_one) ret = -2;
    else {
        total_ = 0; ns_ = 0; sol_out_ = sol_out; sol_cap_ = sol_cap;
        long SX = 1L << (m * k);
        for (long v = 0; v < SX; v++) solve_block(0, ((u64)v) << ((m - 2) * n));
        ret = total_;
    }
    *nsol = ns_;
    for (int i = 0; i < nb; i++) { for (int e = 0; e < blk_[i].neq; e++) free(blk_[i].t[e]); free(blk_[i].t); free(blk_[i].cnt); }
    free(blk_); free(bof); free(umask); free(xmask); free(allowed); free(newu);
    return ret;
}

/* count_dense: plain exhaustive evaluation over all 2^N assignments (N <= 26
 * intended); used to label dense matched nulls, which have no block structure. */
long long count_dense(int N, int neq, const long *ptr, const u64 *masks, u64 *sol_out, long sol_cap, long *nsol) {
    long long total = 0; long ns = 0;
    u64 lim = 1ULL << N;
    for (u64 a = 0; a < lim; a++) {
        int ok = 1;
        for (int e = 0; e < neq && ok; e++) {
            int v = 0;
            for (long p = ptr[e]; p < ptr[e + 1]; p++) { u64 mm = masks[p]; if ((mm & a) == mm) v ^= 1; }
            if (v) ok = 0;
        }
        if (ok) { total++; if (ns < sol_cap) sol_out[ns++] = a; }
    }
    *nsol = ns;
    return total;
}
