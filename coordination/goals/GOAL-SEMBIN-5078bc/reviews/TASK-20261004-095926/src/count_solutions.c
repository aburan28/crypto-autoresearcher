/* count_solutions.c -- exact |V| = #{a in F_2^N : f(a)=0 for all generators} for systems that are
 * AFFINE in the "solved" variable set Y once the "enumerated" set E is fixed (every monomial has at most
 * one variable of Y).  Reads the mask format of to_masks.py.
 *
 *   mode A: structured Gray-code method: requires every monomial to have E-part of size <= 1 when it has
 *           a Y variable and size <= 1 (or 0) when it has no Y variable ... i.e. rhs and the Y-coefficients are
 *           affine in x_E.  Precomputes XOR masks, updates them with one XOR per Gray step.
 *   mode C: direct term evaluation per assignment, any E-degree; no precomputed masks, no Gray code.
 *
 * usage: count_solutions MODE FILE FIRSTE NE [dumpfile maxdump]
 *   E = variables FIRSTE .. FIRSTE+NE-1 (bit positions), Y = all the others (must be <= 32 of them wide? no: <= 63).
 * prints: total, number of assignments with >=1 solution, histogram of solution-space dimension, #consistent
 * Dumps all solutions (as decimal bitmask over the N vars) if total <= maxdump.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

typedef uint64_t u64;
static int N, M;
static int *nt; static u64 **mon;

static int popc(u64 x){return __builtin_popcountll(x);}

typedef struct { u64 total, nsat; u64 hist[64]; } stat_t;

/* gaussian elimination on rows (u,b) over ky unknowns; returns -1 if inconsistent else rank. */
static int elim(u64 *u, u64 *b, int m, int ky, u64 *piv_u, u64 *piv_b, int *piv_has)
{
    int rank = 0;
    for (int i = 0; i < ky; i++) piv_has[i] = 0;
    for (int e = 0; e < m; e++) {
        u64 ue = u[e], be = b[e];
        while (ue) {
            int h = 63 - __builtin_clzll(ue);
            if (piv_has[h]) { ue ^= piv_u[h]; be ^= piv_b[h]; }
            else { piv_u[h] = ue; piv_b[h] = be; piv_has[h] = 1; rank++; break; }
        }
        if (!ue && be) return -1;
    }
    return rank;
}

int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    char mode = argv[1][0];
    FILE *f = fopen(argv[2], "r");
    int e0 = atoi(argv[3]), ne = atoi(argv[4]);
    const char *dumpf = argc > 5 ? argv[5] : NULL;
    u64 maxdump = argc > 6 ? strtoull(argv[6], 0, 10) : 0;
    if (fscanf(f, "%d %d", &N, &M) != 2) return 2;
    nt = malloc(sizeof(int) * M); mon = malloc(sizeof(u64*) * M);
    for (int e = 0; e < M; e++) {
        if (fscanf(f, "%d", &nt[e]) != 1) return 2;
        mon[e] = malloc(sizeof(u64) * (nt[e] + 1));
        for (int t = 0; t < nt[e]; t++) if (fscanf(f, "%lu", &mon[e][t]) != 1) return 2;
    }
    fclose(f);
    u64 Emask = (((u64)1 << ne) - 1) << e0;
    u64 Ymask = (((u64)1 << N) - 1) & ~Emask;
    int ky = N - ne;
    /* map Y variables to 0..ky-1 */
    int ypos[64]; int yv = 0;
    for (int j = 0; j < N; j++) ypos[j] = ((Ymask >> j) & 1) ? yv++ : -1;
    /* validate affine-ness */
    for (int e = 0; e < M; e++) for (int t = 0; t < nt[e]; t++) {
        if (popc(mon[e][t] & Ymask) > 1) { fprintf(stderr, "NOT AFFINE in Y: poly %d term %lu\n", e, mon[e][t]); return 3; }
    }
    /* mode A precompute */
    u64 *b0 = calloc(M, 8), *u0 = calloc(M, 8);
    u64 (*Bm)[64] = calloc(M, sizeof(u64) * 64);   /* Bm[e][i]: toggles rhs when E var i flips */
    u64 (*Um)[64] = calloc(M, sizeof(u64) * 64);   /* Um[e][i]: toggles u when E var i flips */
    if (mode == 'A') {
        for (int e = 0; e < M; e++) for (int t = 0; t < nt[e]; t++) {
            u64 m = mon[e][t]; u64 em = m & Emask, ym = m & Ymask;
            if (popc(em) > 1) { fprintf(stderr, "mode A needs E-degree <= 1\n"); return 3; }
            if (ym == 0) {
                if (em == 0) b0[e] ^= 1; else Bm[e][__builtin_ctzll(em) - e0] ^= 1;
            } else {
                int j = ypos[__builtin_ctzll(ym)];
                if (em == 0) u0[e] ^= (u64)1 << j; else Um[e][__builtin_ctzll(em) - e0] ^= (u64)1 << j;
            }
        }
    }
    /* packed bit versions: for each e, Bmask over i -> a single u64? b changes by bit: Bm[e][i] in {0,1}. Pack across e: Bpk[i] bit e */
    int total_threads = omp_get_max_threads();
    stat_t *st = calloc(total_threads, sizeof(stat_t));
    u64 nE = (u64)1 << ne;
    FILE *df = NULL; u64 dumped = 0;
    int dumping = dumpf != NULL && maxdump > 0;
    if (dumping) df = fopen(dumpf, "w");
    u64 *dump_buf = NULL; u64 dump_n = 0;
    if (dumping) dump_buf = malloc(8 * (maxdump + 1));
    int overflow = 0;
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        stat_t *s = &st[tid];
        u64 *u = malloc(8 * M), *b = malloc(8 * M);
        u64 piv_u[64], piv_b[64]; int piv_has[64];
        u64 chunk = nE / (u64)omp_get_num_threads();
        u64 lo = chunk * tid, hi = (tid == omp_get_num_threads() - 1) ? nE : lo + chunk;
        /* initial state at x = gray(lo) */
        u64 g = lo ^ (lo >> 1);
        if (mode == 'A') {
            for (int e = 0; e < M; e++) {
                u64 uu = u0[e], bb = b0[e];
                for (int i = 0; i < ne; i++) if ((g >> i) & 1) { uu ^= Um[e][i]; bb ^= Bm[e][i]; }
                u[e] = uu; b[e] = bb;
            }
        }
        for (u64 it = lo; it < hi; it++) {
            u64 gx = it ^ (it >> 1);
            u64 xE = gx << e0;
            if (mode == 'A') {
                if (it != lo) {
                    int i = __builtin_ctzll(it);   /* bit that changed from gray(it-1) to gray(it) */
                    for (int e = 0; e < M; e++) { u[e] ^= Um[e][i]; b[e] ^= Bm[e][i]; }
                }
            } else { /* mode C: direct, assignments visited in plain gray order too (any order is fine) */
                for (int e = 0; e < M; e++) {
                    u64 uu = 0, bb = 0;
                    for (int t = 0; t < nt[e]; t++) {
                        u64 m = mon[e][t]; u64 em = m & Emask;
                        if ((em & xE) == em) {
                            u64 ym = m & Ymask;
                            if (ym) uu ^= (u64)1 << ypos[__builtin_ctzll(ym)]; else bb ^= 1;
                        }
                    }
                    u[e] = uu; b[e] = bb;
                }
            }
            int rank = elim(u, b, M, ky, piv_u, piv_b, piv_has);
            if (rank >= 0) {
                int d = ky - rank;
                s->nsat++; s->total += (u64)1 << d; s->hist[d]++;
                if (dumping) {
                    /* enumerate solutions: reduced echelon via back substitution */
                    /* make fully reduced pivots */
                    u64 pu[64], pb[64]; int ph[64]; memcpy(pu, piv_u, sizeof pu); memcpy(pb, piv_b, sizeof pb); memcpy(ph, piv_has, sizeof ph);
                    for (int h = 0; h < ky; h++) if (ph[h]) for (int h2 = h + 1; h2 < ky; h2++) if (ph[h2] && ((pu[h2] >> h) & 1)) { pu[h2] ^= pu[h]; pb[h2] ^= pb[h]; }
                    /* free variables = those without pivot */
                    int fr[64], nf = 0; for (int h = 0; h < ky; h++) if (!ph[h]) fr[nf++] = h;
                    for (u64 fv = 0; fv < ((u64)1 << nf); fv++) {
                        u64 y = 0;
                        for (int q = 0; q < nf; q++) if ((fv >> q) & 1) y |= (u64)1 << fr[q];
                        for (int h = 0; h < ky; h++) if (ph[h]) {
                            /* pivot var h = pb[h] ^ sum over free vars in pu[h] below h of their values */
                            u64 rest = pu[h] & ~((u64)1 << h);
                            int val = (int)(pb[h] ^ (u64)(popc(rest & y) & 1));
                            if (val) y |= (u64)1 << h;
                        }
                        /* expand y (Y-compressed) to full bitmask */
                        u64 full = xE;
                        for (int j = 0; j < N; j++) if (ypos[j] >= 0 && ((y >> ypos[j]) & 1)) full |= (u64)1 << j;
                        #pragma omp critical
                        { if (dump_n < maxdump) dump_buf[dump_n++] = full; else overflow = 1; }
                    }
                }
            }
        }
        free(u); free(b);
    }
    stat_t tot; memset(&tot, 0, sizeof tot);
    for (int t = 0; t < total_threads; t++) { tot.total += st[t].total; tot.nsat += st[t].nsat; for (int d = 0; d < 64; d++) tot.hist[d] += st[t].hist[d]; }
    printf("mode=%c N=%d M=%d E=[%d..%d) ky=%d total=%lu consistent_assignments=%lu hist_dim:", mode, N, M, e0, e0 + ne, ky, tot.total, tot.nsat);
    for (int d = 0; d < 64; d++) if (tot.hist[d]) printf(" d%d:%lu", d, tot.hist[d]);
    printf("\n");
    if (dumping && !overflow) {
        /* sort dump for stable output */
        int cmp(const void *a, const void *b) { u64 x = *(u64*)a, y = *(u64*)b; return x < y ? -1 : x > y; }
        qsort(dump_buf, dump_n, 8, cmp);
        for (u64 i = 0; i < dump_n; i++) fprintf(df, "%lu\n", dump_buf[i]);
        fclose(df);
        printf("dumped %lu solutions\n", dump_n);
    } else if (dumping) printf("dump overflow (total > maxdump) -- not written\n");
    return 0;
}
