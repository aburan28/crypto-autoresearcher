/* closure2.c -- SECOND, structurally different packed implementation of the closure quantity (written independently of closure.c).
 *
 *  - columns: ascending in the monomial order (index = rank in the sorted list), LM = HIGHEST set bit (closure.c: descending order, lowest bit)
 *  - basis: plain non-reduced echelon, rows dense and full width, head reduction one pivot at a time (closure.c: reduced echelon on tails, compaction, batches)
 *  - products: LITERAL fixed-point passes (every current row times every allowed mu, recomputed each pass, until a whole pass adds nothing)
 *    (closure.c: waves over the rows at creation)
 *  - multiplication by mu: OR of masks, column lookup by a hash table (closure.c: product tables)
 * No code is shared with closure.c.  Small/medium N only (the passes are repeated).
 * usage: closure2 SYSTEM.masks [-D n] [-o PREFIX]   prints one JSON line; writes PREFIX.lm (ascending masks, decimal)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef uint64_t u64;

static int N, D, M;
static long C;
static u64 *mons;                 /* ascending order */
static unsigned char *msize;
static u64 *hkeys; static long *hvals; static long hcap;

static int popc(u64 x) { return __builtin_popcountll(x); }
/* ascending order key: (size, -mask)  <=>  smaller size first; equal size: larger mask first */
static int cmp_mon(const void *a, const void *b)
{
    u64 x = *(const u64 *)a, y = *(const u64 *)b; int sx = popc(x), sy = popc(y);
    if (sx != sy) return sx < sy ? -1 : 1;
    return x > y ? -1 : (x < y ? 1 : 0);
}
static void hput(u64 k, long v) { long h = (long)((k * 0x9E3779B97F4A7C15ULL) >> 20) % hcap; while (hkeys[h] != ~0ULL) h = (h + 1) % hcap; hkeys[h] = k; hvals[h] = v; }
static long hget(u64 k) { long h = (long)((k * 0x9E3779B97F4A7C15ULL) >> 20) % hcap; while (hkeys[h] != ~0ULL) { if (hkeys[h] == k) return hvals[h]; h = (h + 1) % hcap; } return -1; }

static long W;                    /* words per row */
static u64 **rows; static long nrows = 0, caprows = 0;
static long *pivrow;              /* by highest bit -> row index or -1 */

static long top_bit(const u64 *x, long hint)
{
    long w = hint; while (w >= 0 && !x[w]) w--;
    if (w < 0) return -1;
    return w * 64 + 63 - __builtin_clzll(x[w]);
}
/* reduce x in place; returns highest bit of the remainder or -1 */
static long reduce(u64 *x)
{
    long h = top_bit(x, W - 1);
    while (h >= 0) {
        long r = pivrow[h];
        if (r < 0) return h;
        const u64 *y = rows[r]; for (long w = h >> 6; w >= 0; w--) x[w] ^= y[w];
        h = top_bit(x, h >> 6);
    }
    return -1;
}
static int insert_row(u64 *x)           /* x is consumed or freed */
{
    long h = reduce(x);
    if (h < 0) return 0;
    if (nrows == caprows) { caprows = caprows ? 2 * caprows : 1024; rows = realloc(rows, sizeof(u64 *) * caprows); }
    u64 *c = malloc(8 * W); memcpy(c, x, 8 * W);
    rows[nrows] = c; pivrow[h] = nrows; nrows++;
    return 1;
}

int main(int argc, char **argv)
{
    D = 4; const char *outp = NULL; int incremental = 0;
    for (int i = 2; i < argc; i++) { if (!strcmp(argv[i], "-D")) D = atoi(argv[++i]); else if (!strcmp(argv[i], "-o")) outp = argv[++i]; else if (!strcmp(argv[i], "-i")) incremental = 1; }
    FILE *f = fopen(argv[1], "r"); if (fscanf(f, "%d %d", &N, &M) != 2) return 2;
    /* all monomials of size <= D */
    long cap = 0; for (int s = 0; s <= D; s++) { long b = 1; for (int i = 0; i < s; i++) b = b * (N - i) / (i + 1); cap += b; }
    mons = malloc(8 * cap); C = 0;
    for (int s = 0; s <= D; s++) {
        if (s == 0) { mons[C++] = 0; continue; }
        u64 m = ((u64)1 << s) - 1, lim = (u64)1 << N;
        while (m < lim) { mons[C++] = m; u64 c = m & -m, r = m + c; m = (((r ^ m) >> 2) / c) | r; }
    }
    qsort(mons, C, 8, cmp_mon);
    msize = malloc(C); for (long i = 0; i < C; i++) msize[i] = popc(mons[i]);
    hcap = 4 * C + 7; hkeys = malloc(8 * hcap); hvals = malloc(8 * hcap); for (long i = 0; i < hcap; i++) hkeys[i] = ~0ULL;
    for (long i = 0; i < C; i++) hput(mons[i], i);
    W = (C + 63) / 64; pivrow = malloc(sizeof(long) * C); for (long i = 0; i < C; i++) pivrow[i] = -1;
    /* generators */
    u64 *x = malloc(8 * W);
    for (int e = 0; e < M; e++) {
        int t; if (fscanf(f, "%d", &t) != 1) return 2;
        memset(x, 0, 8 * W);
        for (int i = 0; i < t; i++) { u64 m; if (fscanf(f, "%lu", &m) != 1) return 2; long p = hget(m); if (p < 0) { fprintf(stderr, "generator degree > D\n"); return 2; } x[p >> 6] ^= (u64)1 << (p & 63); }
        insert_row(x);
    }
    fclose(f);
    /* multiplier lists */
    int *mu_n = calloc(D + 1, sizeof(int)); u64 *mu_l[8];
    for (int s = 1; s <= D; s++) {
        long b = 1; for (int i = 0; i < s; i++) b = b * (N - i) / (i + 1);
        mu_l[s] = malloc(8 * b); mu_n[s] = 0;
        u64 m = ((u64)1 << s) - 1, lim = (u64)1 << N; while (m < lim) { mu_l[s][mu_n[s]++] = m; u64 c = m & -m, r = m + c; m = (((r ^ m) >> 2) / c) | r; }
    }
    int passes = 0; long hist[64]; hist[0] = nrows;
    int one = 0;
    if (incremental) {
        /* rows are immutable once stored: multiply each stored row exactly once, in creation order, until the queue is exhausted */
        long qpos = 0; double tl = (double)clock() / CLOCKS_PER_SEC;
        while (qpos < nrows) {
            const u64 *b = rows[qpos];
            long h = top_bit(b, W - 1); int d = msize[h];
            for (int s = 1; s <= D - d; s++) for (int q = 0; q < mu_n[s]; q++) {
                u64 mu = mu_l[s][q];
                memset(x, 0, 8 * W);
                for (long w = 0; w <= (h >> 6); w++) { u64 y = b[w]; while (y) { int bit = __builtin_ctzll(y); y &= y - 1; long p = w * 64 + bit; long p2 = hget(mons[p] | mu); x[p2 >> 6] ^= (u64)1 << (p2 & 63); } }
                insert_row(x);
            }
            qpos++;
            if (qpos % 2000 == 0) { double t = (double)clock() / CLOCKS_PER_SEC; if (t - tl > 120) { fprintf(stderr, "[closure2 -i] queue %ld/%ld rank %ld cpu %.0fs\n", qpos, nrows, nrows, t); tl = t; } }
        }
        passes = 1; hist[1] = nrows;
        goto output;
    }
    while (1) {
        long snap = nrows; long added = 0;
        long *order = malloc(sizeof(long) * snap);
        for (long i = 0; i < snap; i++) order[i] = i;                 /* creation order; any order is fine */
        for (long ii = 0; ii < snap; ii++) {
            const u64 *b = rows[order[ii]];
            long h = top_bit(b, W - 1); int d = msize[h];
            for (int s = 1; s <= D - d; s++) for (int q = 0; q < mu_n[s]; q++) {
                u64 mu = mu_l[s][q];
                memset(x, 0, 8 * W);
                for (long w = 0; w <= (h >> 6); w++) { u64 y = b[w]; while (y) { int bit = __builtin_ctzll(y); y &= y - 1; long p = w * 64 + bit; long p2 = hget(mons[p] | mu); x[p2 >> 6] ^= (u64)1 << (p2 & 63); } }
                if (insert_row(x)) added++;
            }
        }
        free(order);
        passes++; hist[passes] = nrows;
        if (!added) break;
    }
output:;
    u64 *lm = malloc(8 * (nrows + 1)); long nl = 0; long by[8] = {0};
    for (long h = 0; h < C; h++) if (pivrow[h] >= 0) { lm[nl++] = mons[h]; by[msize[h]]++; if (mons[h] == 0) one = 1; }
    int cmpu(const void *a, const void *b) { u64 p = *(u64 *)a, q = *(u64 *)b; return p < q ? -1 : p > q; }
    qsort(lm, nl, 8, cmpu);
    if (outp) { char fn[1024]; snprintf(fn, sizeof fn, "%s.lm", outp); FILE *g = fopen(fn, "w"); for (long i = 0; i < nl; i++) fprintf(g, "%lu\n", lm[i]); fclose(g); }
    /* standard monomials by Apriori-free simple DFS over faces */
    char *isl = calloc(C, 1); for (long h = 0; h < C; h++) if (pivrow[h] >= 0) isl[h] = 1;
    unsigned long nstd = 0;
    if (!isl[hget(0)]) {
        int el[64]; int nxt[64]; int depth = 0; nxt[0] = 0; nstd = 1;
        while (1) {
            int v = nxt[depth];
            if (v >= N) { if (!depth) break; depth--; nxt[depth]++; continue; }
            int ok = 1; u64 vm = (u64)1 << v;
            /* all subsets T of the face with |T| <= D-1: T+v not a leading monomial */
            int n = depth; int idx[8];
            for (int sz = 0; sz <= D - 1 && sz <= n && ok; sz++) {
                for (int i = 0; i < sz; i++) idx[i] = i;
                while (1) {
                    u64 m = vm; for (int i = 0; i < sz; i++) m |= (u64)1 << el[idx[i]];
                    if (isl[hget(m)]) { ok = 0; break; }
                    int i = sz - 1; while (i >= 0 && idx[i] == n - sz + i) i--;
                    if (i < 0) break;
                    idx[i]++; for (int j = i + 1; j < sz; j++) idx[j] = idx[j - 1] + 1;
                }
            }
            if (ok) { nstd++; el[depth] = v; depth++; nxt[depth] = v + 1; } else nxt[depth]++;
        }
    }
    printf("{\"impl\": \"closure2\", \"N\": %d, \"M\": %d, \"D\": %d, \"columns\": %ld, \"rank\": %ld, \"one_in_W\": %d, \"lm_by_size\": [", N, M, D, C, nrows, one);
    for (int s = 0; s <= D; s++) printf("%ld%s", by[s], s < D ? ", " : "");
    printf("], \"N_std\": %lu, \"pass_ranks\": [", nstd);
    for (int i = 0; i <= passes; i++) printf("%ld%s", hist[i], i < passes ? ", " : "");
    printf("]}\n");
    return 0;
}
