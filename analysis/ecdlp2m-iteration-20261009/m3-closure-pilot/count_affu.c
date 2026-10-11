/* count_affu.c -- PILOT (m3closure). Exhaustive solution count of a Boolean
 * system in which every monomial contains at most one "u" variable (bits
 * 0..nu-1) -- true for the chained S_3 descent (u enters S_3 only bilinearly
 * with x's or through Frobenius-linear squares) and for its same-support nulls.
 * Equations are split into group A (touching x-bits in maskA only) and group B
 * (touching x-bits in maskB only). For every assignment of the x-bits the
 * system is affine in u; it is solved by GF(2) elimination.
 * Written for this pilot; independent of the curve-level enumerator.
 *
 * count_affu(N, nu, neq, ptr, masks, xa_bits, nxa, xb_bits, nxb, sol_out, sol_cap, &nsol)
 *   returns the total number of Boolean solutions (as long long), -1 on a
 *   structural violation. Up to sol_cap solution masks are written to sol_out.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

typedef struct { int neq; int *cnt; u64 **xm; u64 **um; } grp_t;

static u64 pdep_bits(u64 v, const int *bits, int nb) {
    u64 r = 0;
    for (int i = 0; i < nb; i++) if ((v >> i) & 1) r |= 1ULL << bits[i];
    return r;
}

/* insert row (nu+1 bits; bit nu = constant) into echelon array piv[nu+1];
 * returns 0 if dependent, 1 if new, -1 if it yields 1 = 0 (inconsistent) */
static int ins(u64 *piv, u64 row, int nu) {
    u64 um = (nu >= 64) ? ~0ULL : ((1ULL << nu) - 1);
    for (;;) {
        u64 ub = row & um;
        if (!ub) return ((row >> nu) & 1) ? -1 : 0;   /* 1 = 0, or dependent */
        int top = 63 - __builtin_clzll(ub);
        if (piv[top]) row ^= piv[top];
        else { piv[top] = row; return 1; }
    }
}

long long count_affu(int N, int nu, int neq, const long *ptr, const u64 *masks,
                     const int *xa_bits, int nxa, const int *xb_bits, int nxb,
                     u64 *sol_out, long sol_cap, long *nsol) {
    u64 umask = (nu >= 64) ? ~0ULL : ((1ULL << nu) - 1);
    u64 maskA = 0, maskB = 0;
    for (int i = 0; i < nxa; i++) maskA |= 1ULL << xa_bits[i];
    for (int i = 0; i < nxb; i++) maskB |= 1ULL << xb_bits[i];
    /* classify equations */
    int *g = malloc(sizeof(int) * neq);
    int na = 0, nb = 0;
    for (int e = 0; e < neq; e++) {
        u64 xs = 0;
        for (long p = ptr[e]; p < ptr[e + 1]; p++) {
            u64 m = masks[p];
            if (__builtin_popcountll(m & umask) > 1) { free(g); return -1; }
            xs |= m & ~umask;
        }
        if ((xs & ~maskA) == 0) { g[e] = 0; na++; }
        else if ((xs & ~maskB) == 0) { g[e] = 1; nb++; }
        else { free(g); return -1; }
    }
    (void)N;
    /* row tables: rowsA[xa][i] for i<na, rowsB[xb][i] for i<nb */
    long SA = 1L << nxa, SB = 1L << nxb;
    u64 *rowsA = calloc((size_t)SA * (na ? na : 1), sizeof(u64));
    u64 *rowsB = calloc((size_t)SB * (nb ? nb : 1), sizeof(u64));
    int ia = 0, ib = 0;
    for (int e = 0; e < neq; e++) {
        int isA = (g[e] == 0);
        long S = isA ? SA : SB;
        const int *bits = isA ? xa_bits : xb_bits;
        int nbits = isA ? nxa : nxb;
        for (long v = 0; v < S; v++) {
            u64 X = pdep_bits(v, bits, nbits);
            u64 row = 0;
            for (long p = ptr[e]; p < ptr[e + 1]; p++) {
                u64 m = masks[p];
                u64 xm = m & ~umask;
                if ((xm & X) == xm) {
                    u64 um = m & umask;
                    row ^= um ? um : (1ULL << nu);
                }
            }
            if (isA) rowsA[v * na + ia] = row; else rowsB[v * nb + ib] = row;
        }
        if (isA) ia++; else ib++;
    }
    long long total = 0;
    long ns = 0;
    u64 pivA[65], piv[65];
    for (long va = 0; va < SA; va++) {
        memset(pivA, 0, sizeof pivA);
        int bad = 0, rkA = 0;
        for (int i = 0; i < na; i++) {
            int r = ins(pivA, rowsA[va * na + i], nu);
            if (r < 0) { bad = 1; break; }
            rkA += r;
        }
        if (bad) continue;
        for (long vb = 0; vb < SB; vb++) {
            memcpy(piv, pivA, sizeof piv);
            int rk = rkA, bad2 = 0;
            for (int i = 0; i < nb; i++) {
                int r = ins(piv, rowsB[vb * nb + i], nu);
                if (r < 0) { bad2 = 1; break; }
                rk += r;
            }
            if (bad2) continue;
            int fr = nu - rk;
            total += 1LL << fr;
            if (ns < sol_cap) {
                /* enumerate solutions: free vars = non-pivot u columns */
                int fv[64], nf = 0;
                for (int c = 0; c < nu; c++) if (!piv[c]) fv[nf++] = c;
                for (long f = 0; f < (1L << nf) && ns < sol_cap; f++) {
                    u64 uval = 0;
                    for (int i = 0; i < nf; i++) if ((f >> i) & 1) uval |= 1ULL << fv[i];
                    /* back-substitute from low pivots up: pivot row with top c has bits < c */
                    for (int c = 0; c < nu; c++) if (piv[c]) {
                        u64 row = piv[c];
                        int v = (int)((row >> nu) & 1);
                        u64 rest = row & umask & ~(1ULL << c);
                        v ^= __builtin_popcountll(rest & uval) & 1;
                        if (v) uval |= 1ULL << c;
                    }
                    sol_out[ns++] = uval | pdep_bits(va, xa_bits, nxa) | pdep_bits(vb, xb_bits, nxb);
                }
            }
        }
    }
    free(g); free(rowsA); free(rowsB);
    *nsol = ns;
    return total;
}
