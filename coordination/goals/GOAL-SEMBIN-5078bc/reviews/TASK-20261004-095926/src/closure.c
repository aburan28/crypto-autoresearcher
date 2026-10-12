/* closure.c -- packed-bit implementation of the degree-capped Boolean-ring closure W_D(S) of
 * TASK-20261004-095926, written from the statement alone (no M4RI, no shared code with the Python reference).
 *
 * Boolean ring B = F_2[x_1..x_N]/(x_i^2+x_i): monomial = bitmask (bit j-1 <-> x_j), product = OR.
 * Order: size first, equal size: m LARGER than m' iff the largest variable index in m^m' belongs to m'
 *        (grevlex, x_1 largest).  With the bitmask encoding: among equal sizes larger <=> smaller mask.
 * Columns: all monomials of size <= D, DESCENDING in that order  (column 0 = largest monomial).
 *          col(mask) = off[|mask|] + colex_rank(mask);  off[D]=0, off[s]=off[s+1]+C(N,s+1).
 *          The leading monomial of a nonzero row = its lowest set column.
 * Basis: reduced row echelon form.  Row r = e_{piv(r)} + tail(r); tail has set bits only at columns that are NOT
 *          pivots and lie to the right of piv(r).  Tails are stored over a "compact" column layout (epoch) that
 *          drops pivot columns at every compaction.
 * Closure: products mu*f for every basis row f and every square-free mu, 1<=|mu|<=D-deg f (deg f = |LM f| for a
 *          graded order); every row is multiplied in the (reduced) form in which it was created; by F_2-linearity of
 *          mu*(.) and the degree filtration of the echelon basis this yields the smallest closed subspace
 *          (argument in the report).  Rows are processed in WAVES: wave 0 = the reduced generators, wave t = products
 *          of the rows created in wave t-1.  rank after wave t is reported.
 *
 * usage: closure SYSTEM.masks [options]
 *   -D n          degree cap (default 4)
 *   -o PREFIX     write PREFIX.lm (ascending LM masks, decimal, one per line) and PREFIX.json
 *   -t n          threads (default OMP_NUM_THREADS)
 *   -B n          batch size (default 256)
 *   -E            disable the early exit on 1 in W
 *   -b k          MUTANT PT-1(a): multiplier budget lowered by k
 *   -S            LITERAL single-level span: raw generators g times every mu with |mu|<=D-deg g, nothing else
 *   -g            MUTANT PT-1(c): multiply only the wave-0 rows (reduced generators): products stop after wave 1
 *   -d            MUTANT PT-1(d): drop the last batch of products of every wave
 *   -w n          stop after wave n (partial progress)
 *   -q            quiet
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <omp.h>
#include <immintrin.h>

typedef uint64_t u64;
typedef uint32_t u32;

static int N, D, M;
static long C;                 /* number of columns */
static long off[16];
static long binom[80][12];
static u64 *mask_of;           /* column -> mask */
static unsigned char *size_of;
static int *T;                 /* T[v*C+col] = col of (mask|1<<v), or -1 if size exceeds D */

static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }
static inline int popc(u64 x) { return __builtin_popcountll(x); }

static inline long col_of(u64 m)
{
    int s = popc(m);
    long r = 0; int i = 1;
    u64 x = m;
    while (x) { int a = __builtin_ctzll(x); r += binom[a][i]; i++; x &= x - 1; }
    return off[s] + r;
}

static void build_columns(void)
{
    for (int n = 0; n < 80; n++) { binom[n][0] = 1; for (int k = 1; k < 12; k++) binom[n][k] = (n == 0) ? 0 : binom[n - 1][k - 1] + binom[n - 1][k]; }
    off[D] = 0;
    for (int s = D - 1; s >= 0; s--) off[s] = off[s + 1] + binom[N][s + 1];
    C = off[0] + 1;
    mask_of = malloc(sizeof(u64) * C); size_of = malloc(C);
    for (int s = 0; s <= D; s++) {
        long idx = 0;
        if (s == 0) { mask_of[off[0]] = 0; size_of[off[0]] = 0; continue; }
        u64 m = ((u64)1 << s) - 1, lim = (u64)1 << N;
        while (m < lim) {
            mask_of[off[s] + idx] = m; size_of[off[s] + idx] = s; idx++;
            u64 c = m & -m, r = m + c; m = (((r ^ m) >> 2) / c) | r;
        }
        if (idx != binom[N][s]) { fprintf(stderr, "column count mismatch\n"); exit(2); }
    }
    for (long col = 0; col < C; col++) if (col_of(mask_of[col]) != col) { fprintf(stderr, "col_of mismatch %ld\n", col); exit(2); }
    T = malloc(sizeof(int) * (size_t)N * C);
    for (int v = 0; v < N; v++) for (long col = 0; col < C; col++) {
        u64 m = mask_of[col];
        if ((m >> v) & 1) T[(size_t)v * C + col] = (int)col;
        else if (size_of[col] == D) T[(size_t)v * C + col] = -1;
        else T[(size_t)v * C + col] = (int)col_of(m | ((u64)1 << v));
    }
}

/* ----------------------------------------------------------------------- row store */
typedef struct { u64 *tail; int lo; int piv; } Row;
static Row *rows; static long nrows = 0, caprows = 0;
static int *rowoncol;          /* column -> row index or -1 */
static int *cidx;              /* column -> compact index in the current epoch, or -1 */
static int *cinv;              /* compact index -> column */
static long W = 0, sEpoch = 0; /* words per tail, compact bits in the epoch */
static long lowstart_k = 0;    /* first compact index whose column has size <= D-1 */
static long lowbase, nlow, nlw;

static u64 *amalloc(size_t words) { void *p = NULL; if (posix_memalign(&p, 64, words * 8 + 64)) { fprintf(stderr, "OOM\n"); exit(3); } return (u64 *)p; }

static void epoch_init_identity(void)
{
    sEpoch = C; W = (C + 63) / 64;
    cidx = malloc(sizeof(int) * C); cinv = malloc(sizeof(int) * C);
    for (long col = 0; col < C; col++) { cidx[col] = (int)col; cinv[col] = (int)col; }
    lowstart_k = off[D - 1];
}

static long npivots_by_size[16];

/* recompute epoch: drop pivot columns, shrink all tails */
static void compact(void)
{
    long newc = 0;
    int *newidx = malloc(sizeof(int) * C);
    for (long col = 0; col < C; col++) newidx[col] = (rowoncol[col] < 0) ? (int)(newc++) : -1;
    long W2 = (newc + 63) / 64;
    int *ncinv = malloc(sizeof(int) * (newc + 1));
    for (long col = 0; col < C; col++) if (newidx[col] >= 0) ncinv[newidx[col]] = (int)col;
    /* keep masks per old word and output offsets */
    u64 *keep = calloc(W, 8); long *outpos = malloc(sizeof(long) * (W + 1));
    for (long k = 0; k < sEpoch; k++) if (newidx[cinv[k]] >= 0) keep[k >> 6] |= (u64)1 << (k & 63);
    outpos[0] = 0; for (long w = 0; w < W; w++) outpos[w + 1] = outpos[w] + popc(keep[w]);
    #pragma omp parallel for schedule(static)
    for (long r = 0; r < nrows; r++) {
        u64 *old = rows[r].tail; u64 *nw = amalloc(W2 > 0 ? W2 : 1);
        memset(nw, 0, 8 * (W2 > 0 ? W2 : 1));
        for (long w = rows[r].lo; w < W; w++) {
            u64 x = old[w]; if (!x) continue;
            u64 bits = _pext_u64(x, keep[w]); if (!bits) continue;
            long p = outpos[w]; long wi = p >> 6; int sh = p & 63;
            nw[wi] |= bits << sh;
            if (sh && (bits >> (64 - sh))) nw[wi + 1] |= bits >> (64 - sh);
        }
        long lo = 0; while (lo < W2 && !nw[lo]) lo++;
        free(old); rows[r].tail = nw; rows[r].lo = (int)(lo < W2 ? lo : W2);
    }
    /* sanity: no tail bits beyond newc */
    free(cidx); free(cinv); free(keep); free(outpos);
    cidx = newidx; cinv = ncinv; W = W2; sEpoch = newc;
    /* low start */
    lowstart_k = 0; while (lowstart_k < sEpoch && cinv[lowstart_k] < off[D - 1]) lowstart_k++;
}

/* ----------------------------------------------------------------------- snapshots (rows still to be multiplied) */
typedef struct { u64 *bits; int deg; } Snap;     /* bits over low columns (sizes <= D-1) */
typedef struct { Snap *a; long n, cap; } SnapList;
static void sl_push(SnapList *l, Snap s) { if (l->n == l->cap) { l->cap = l->cap ? 2 * l->cap : 1024; l->a = realloc(l->a, sizeof(Snap) * l->cap); } l->a[l->n++] = s; }

/* multipliers */
static int *mus[8]; static long nmus[8];
static void build_mus(void)
{
    for (int k = 1; k <= D; k++) {
        nmus[k] = binom[N][k]; mus[k] = malloc(sizeof(int) * k * nmus[k]);
        long idx = 0; u64 m = ((u64)1 << k) - 1, lim = (u64)1 << N;
        while (m < lim) {
            int j = 0; u64 x = m; while (x) { mus[k][idx * k + j++] = __builtin_ctzll(x); x &= x - 1; }
            idx++;
            u64 c = m & -m, r = m + c; m = (((r ^ m) >> 2) / c) | r;
        }
    }
}

static int budget_shift = 0, mut_gens_only = 0, mut_drop_last = 0, early_exit = 1, quiet = 0, literal_single = 0;
static int one_in_W = 0;

/* build the snapshot (creation form) of a freshly created row from acc (compact layout, includes the pivot bit) */
static Snap make_snap(const u64 *acc, int deg)
{
    Snap s; s.deg = deg; s.bits = calloc(nlw, 8);
    for (long k = lowstart_k; k < sEpoch; k++) { /* iterate set bits efficiently */
        long w = k >> 6; u64 x = acc[w] >> (k & 63); if (!x) { k = (w + 1) * 64 - 1; continue; }
        k += __builtin_ctzll(x);
        if (k >= sEpoch) break;
        long col = cinv[k]; long b = col - lowbase;
        s.bits[b >> 6] ^= (u64)1 << (b & 63);
    }
    return s;
}

/* ----------------------------------------------------------------------- the reduction of a candidate */
/* H: hit-parity bitset over full columns (Hw words); acc: W words output (compact layout) */
static void reduce_candidate(const Snap *sn, const int *mu, int nmu, u64 *H, long Hw, u64 *acc)
{
    memset(H, 0, 8 * Hw);
    for (long wi = 0; wi < nlw; wi++) {
        u64 x = sn->bits[wi];
        while (x) {
            int b = __builtin_ctzll(x); x &= x - 1;
            long col = lowbase + wi * 64 + b;
            for (int q = 0; q < nmu; q++) { col = T[(size_t)mu[q] * C + col]; if (col < 0) { fprintf(stderr, "budget violation\n"); abort(); } }
            H[col >> 6] ^= (u64)1 << (col & 63);
        }
    }
    memset(acc, 0, 8 * W);
    for (long w = 0; w < Hw; w++) {
        u64 x = H[w];
        while (x) {
            int b = __builtin_ctzll(x); x &= x - 1;
            long col = w * 64 + b;
            int r = rowoncol[col];
            if (r >= 0) {
                const u64 *t = rows[r].tail; for (long i = rows[r].lo; i < W; i++) acc[i] ^= t[i];
            } else {
                long k = cidx[col]; acc[k >> 6] ^= (u64)1 << (k & 63);
            }
        }
    }
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: closure SYSTEM.masks [opts]\n"); return 2; }
    D = 4; const char *outp = NULL; int threads = omp_get_max_threads(); long B = 256; int stop_wave = 1 << 30;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "-D")) D = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-o")) outp = argv[++i];
        else if (!strcmp(argv[i], "-t")) threads = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-B")) B = atol(argv[++i]);
        else if (!strcmp(argv[i], "-E")) early_exit = 0;
        else if (!strcmp(argv[i], "-b")) budget_shift = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-g")) mut_gens_only = 1;
        else if (!strcmp(argv[i], "-S")) literal_single = 1;
        else if (!strcmp(argv[i], "-d")) mut_drop_last = 1;
        else if (!strcmp(argv[i], "-w")) stop_wave = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-q")) quiet = 1;
        else { fprintf(stderr, "bad option %s\n", argv[i]); return 2; }
    }
    omp_set_num_threads(threads);
    double t0 = now();
    FILE *f = fopen(argv[1], "r"); if (!f) { perror("open"); return 2; }
    if (fscanf(f, "%d %d", &N, &M) != 2) return 2;
    if (N > 62) { fprintf(stderr, "N too large\n"); return 2; }
    build_columns(); build_mus();
    lowbase = off[D - 1]; nlow = C - lowbase; nlw = (nlow + 63) / 64;
    long Hw = (C + 63) / 64;
    /* read generators as sorted unique column lists (parity-reduced) */
    int **gcols = malloc(sizeof(int *) * M); int *gn = malloc(sizeof(int) * M);
    for (int e = 0; e < M; e++) {
        int t; if (fscanf(f, "%d", &t) != 1) return 2;
        u64 *tmp = malloc(8 * (t + 1));
        for (int i = 0; i < t; i++) if (fscanf(f, "%lu", &tmp[i]) != 1) return 2;
        gcols[e] = malloc(sizeof(int) * (t + 1)); gn[e] = 0;
        for (int i = 0; i < t; i++) {
            if (popc(tmp[i]) > D) { fprintf(stderr, "generator %d has degree > D\n", e); return 2; }
            gcols[e][gn[e]++] = (int)col_of(tmp[i]);
        }
        free(tmp);
    }
    fclose(f);
    rowoncol = malloc(sizeof(int) * C); for (long i = 0; i < C; i++) rowoncol[i] = -1;
    epoch_init_identity();
    long nthr = threads;
    u64 **Hs = malloc(sizeof(u64 *) * nthr); for (int i = 0; i < nthr; i++) Hs[i] = amalloc(Hw);
    u64 *batch = NULL; long batch_cap_W = 0;
    SnapList cur = {0}, next = {0};
    long wave_rank[64]; double wave_time[64]; long wave_cand[64]; int nwaves = 0;
    long total_cand = 0;
    int epoch_compactions = 0;
    double tlast_report = now();

    /* helper lambdas as macros are awkward; implement batch processing inline via a work array */
    typedef struct { const Snap *sn; int mu[4]; int nmu; } Work;
    Work *work = malloc(sizeof(Work) * B);

    /* wave 0: generators.  A "work item" with nmu = 0 means: candidate is the generator itself. */
    long gen_idx = 0;
    int deg_of_gen_ok = 1; (void)deg_of_gen_ok;
    Snap *gsnap = malloc(sizeof(Snap) * M);
    for (int e = 0; e < M; e++) {
        gsnap[e].bits = calloc(nlw, 8); gsnap[e].deg = 0;
        for (int i = 0; i < gn[e]; i++) {
            long col = gcols[e][i]; int s = size_of[col];
            if (s > gsnap[e].deg) gsnap[e].deg = s;
            if (s <= D - 1) { long b = col - lowbase; gsnap[e].bits[b >> 6] ^= (u64)1 << (b & 63); }
        }
    }
    /* generic driver: process a list of work items in batches */
    long cand_this_wave = 0;
    int wave = 0;
    long gen_pos = 0;           /* for wave 0 */
    long snap_pos = 0; int mu_k = 1; long mu_i = 0;   /* for wave >= 1 */
    int done = 0;
    double tw = now();
    long wave_total = 0, wave_done = 0;      /* work items of the current wave (waves >= 1) */
    int stop_after_wave1 = 0;
    #define WAVE_TOTAL_COMPUTE() do { wave_total = 0; for (long ii = 0; ii < cur.n; ii++) { int top_ = D - cur.a[ii].deg - budget_shift; for (int kk_ = 1; kk_ <= top_; kk_++) wave_total += nmus[kk_]; } wave_done = 0; } while (0)
    while (!done) {
        /* ---- collect a batch of work */
        long nb = 0;
        if (wave == 0) {
            while (nb < B && gen_pos < M) {
                work[nb].sn = &gsnap[gen_pos]; work[nb].nmu = -1;      /* marker: the raw generator itself */
                nb++; gen_pos++;
            }
        } else {
            while (nb < B && snap_pos < cur.n) {
                const Snap *sn = &cur.a[snap_pos];
                int top = D - sn->deg - budget_shift;
                if (top < 1 || mu_k > top) { snap_pos++; mu_k = 1; mu_i = 0; continue; }
                if (mu_i >= nmus[mu_k]) { mu_k++; mu_i = 0; continue; }
                work[nb].sn = sn; work[nb].nmu = mu_k;
                for (int q = 0; q < mu_k; q++) work[nb].mu[q] = mus[mu_k][mu_i * mu_k + q];
                mu_i++; nb++;
            }
        }
        if (nb == 0) {
            /* wave finished */
            wave_rank[nwaves] = nrows; wave_time[nwaves] = now() - tw; wave_cand[nwaves] = cand_this_wave; nwaves++;
            if (!quiet) {
                long by[8] = {0}; for (long r = 0; r < nrows; r++) by[size_of[rows[r].piv]]++;
                fprintf(stderr, "[wave %d done] rank=%ld new_snaps=%ld cand=%ld t=%.1fs elapsed=%.1fs s_epoch=%ld LM by size:", wave, nrows, next.n, cand_this_wave, now() - tw, now() - t0, sEpoch);
                for (int s = 0; s <= D; s++) fprintf(stderr, " %ld", by[s]); fprintf(stderr, "\n");
            }
            if (wave == 0 && literal_single) {
                /* replace the reduced generator rows by the raw generators (their own degree) and stop after wave 1 */
                for (long i = 0; i < next.n; i++) free(next.a[i].bits);
                next.n = 0;
                for (int e = 0; e < M; e++) { if (gsnap[e].deg <= D - 1) { Snap sc; sc.deg = gsnap[e].deg; sc.bits = malloc(8 * nlw); memcpy(sc.bits, gsnap[e].bits, 8 * nlw); sl_push(&next, sc); } }
                stop_after_wave1 = 1;
            }
            for (long i = 0; i < cur.n; i++) free(cur.a[i].bits);
            free(cur.a); cur = next; next.a = NULL; next.n = next.cap = 0;
            wave++; cand_this_wave = 0; snap_pos = 0; mu_k = 1; mu_i = 0; tw = now();
            WAVE_TOTAL_COMPUTE();
            if (cur.n == 0 || one_in_W || wave > stop_wave || (stop_after_wave1 && wave > 1) || (mut_gens_only && wave > 1)) { done = 1; }
            continue;
        }
        int drop = 0;
        if (wave >= 1) { wave_done += nb; if (mut_drop_last && wave_done >= wave_total) drop = 1; }
        if (drop) { cand_this_wave += nb; continue; }          /* PT-1(d): the last batch of the wave is not reduced or inserted */
        /* ---- ensure batch buffer */
        if (batch_cap_W < W || !batch) { free(batch); batch = amalloc((size_t)B * W); batch_cap_W = W; }
        /* ---- Phase A (parallel): produce candidates reduced against the old RREF */
        long nold = nrows;
        #pragma omp parallel for schedule(dynamic, 4)
        for (long i = 0; i < nb; i++) {
            u64 *acc = batch + (size_t)i * W; int tid = omp_get_thread_num();
            if (work[i].nmu < 0) {
                int e = (int)(work[i].sn - gsnap);
                u64 *H = Hs[tid]; memset(H, 0, 8 * Hw);
                for (int q = 0; q < gn[e]; q++) { long col = gcols[e][q]; H[col >> 6] ^= (u64)1 << (col & 63); }
                memset(acc, 0, 8 * W);
                for (long w = 0; w < Hw; w++) { u64 x = H[w]; while (x) { int b = __builtin_ctzll(x); x &= x - 1; long col = w * 64 + b; int r = rowoncol[col];
                    if (r >= 0) { const u64 *t = rows[r].tail; for (long j = rows[r].lo; j < W; j++) acc[j] ^= t[j]; } else { long k = cidx[col]; acc[k >> 6] ^= (u64)1 << (k & 63); } } }
            } else {
                reduce_candidate(work[i].sn, work[i].mu, work[i].nmu, Hs[tid], Hw, acc);
            }
        }
        cand_this_wave += nb; total_cand += nb;
        /* ---- Phase B (sequential): Gauss-Jordan among the batch candidates */
        long nnew0 = nrows;
        for (long i = 0; i < nb; i++) {
            u64 *acc = batch + (size_t)i * W;
            for (long j = nnew0; j < nrows; j++) {         /* reduce by the new pivots created earlier in this batch */
                long k = cidx[rows[j].piv];
                if ((acc[k >> 6] >> (k & 63)) & 1) {
                    acc[k >> 6] ^= (u64)1 << (k & 63);
                    const u64 *t = rows[j].tail; for (long q = rows[j].lo; q < W; q++) acc[q] ^= t[q];
                }
            }
            long fw = 0; while (fw < W && !acc[fw]) fw++;
            if (fw == W) continue;
            long k = fw * 64 + __builtin_ctzll(acc[fw]);
            int pcol = cinv[k];
            if (nrows == caprows) { caprows = caprows ? 2 * caprows : 4096; rows = realloc(rows, sizeof(Row) * caprows); }
            int deg = size_of[pcol];
            Snap sn = {0};
            int want_snap = (deg <= D - 1);
            if (mut_gens_only && wave >= 1) want_snap = 0;
            if (want_snap) sn = make_snap(acc, deg);
            for (long j = nnew0; j < nrows; j++) {          /* eliminate the new pivot from earlier new rows */
                u64 *tj = rows[j].tail;
                if ((tj[k >> 6] >> (k & 63)) & 1) { for (long q = (k >> 6); q < W; q++) tj[q] ^= acc[q]; }
            }
            u64 *nt = amalloc(W); memcpy(nt, acc, 8 * W); nt[k >> 6] &= ~((u64)1 << (k & 63));
            rows[nrows].tail = nt; rows[nrows].lo = (int)(k >> 6); rows[nrows].piv = pcol;
            rowoncol[pcol] = (int)nrows; nrows++;
            if (size_of[pcol] == 0 && early_exit) one_in_W = 1;
            if (sn.bits) sl_push(&next, sn);
        }
        /* ---- Phase C (parallel): eliminate the new pivots from the old rows */
        long nnew = nrows - nnew0;
        if (nnew > 0 && nold > 0) {
            long *kk = malloc(sizeof(long) * nnew);
            for (long j = 0; j < nnew; j++) kk[j] = cidx[rows[nnew0 + j].piv];
            #pragma omp parallel for schedule(static)
            for (long r = 0; r < nold; r++) {
                u64 *tr = rows[r].tail;
                for (long j = 0; j < nnew; j++) {
                    long k = kk[j];
                    if ((tr[k >> 6] >> (k & 63)) & 1) {
                        tr[k >> 6] ^= (u64)1 << (k & 63);
                        const u64 *tj = rows[nnew0 + j].tail;
                        for (long q = rows[nnew0 + j].lo; q < W; q++) tr[q] ^= tj[q];
                    }
                }
            }
            free(kk);
        }
        /* ---- compaction */
        if ((C - nrows) < (long)(0.80 * (double)(W * 64)) && W > 4) { compact(); epoch_compactions++; if (!quiet) fprintf(stderr, "  compact: s=%ld W=%ld rank=%ld elapsed=%.1fs\n", sEpoch, W, nrows, now() - t0); }
        if (!quiet && now() - tlast_report > 60) {
            tlast_report = now();
            fprintf(stderr, "  [progress wave %d] rank=%ld cand=%ld/%ld snap_pos=%ld/%ld elapsed=%.0fs\n", wave, nrows, cand_this_wave, wave_total, snap_pos, cur.n, now() - t0);
        }
        if (one_in_W && early_exit) {
            wave_rank[nwaves] = nrows; wave_time[nwaves] = now() - tw; wave_cand[nwaves] = cand_this_wave; nwaves++;
            done = 1;
        }
    }
    double t1 = now();
    /* ---------- output */
    long by[8] = {0};
    long r_out = nrows;
    int *ispivot = calloc(C, sizeof(int));
    for (long r = 0; r < nrows; r++) { ispivot[rows[r].piv] = 1; by[size_of[rows[r].piv]]++; }
    int constant_in = ispivot[off[0]];
    if (one_in_W && early_exit) { r_out = C; for (long col = 0; col < C; col++) ispivot[col] = 1; for (int s = 0; s <= D; s++) by[s] = binom[N][s]; }
    /* ascending masks of LM set */
    u64 *lms = malloc(8 * (C + 1)); long nl = 0;
    for (long col = 0; col < C; col++) if (ispivot[col]) lms[nl++] = mask_of[col];
    int cmp(const void *a, const void *b) { u64 x = *(const u64 *)a, y = *(const u64 *)b; return x < y ? -1 : x > y; }
    qsort(lms, nl, 8, cmp);
    if (outp) {
        char fn[1024]; snprintf(fn, sizeof fn, "%s.lm", outp); FILE *g = fopen(fn, "w");
        for (long i = 0; i < nl; i++) fprintf(g, "%lu\n", lms[i]);
        fclose(g);
    }
    /* standard monomial count: faces of the complex of subsets containing no LM */
    /* iterative DFS */
    unsigned long nstd = 0;
    {
        int elems[64]; int stackv[64]; int depth = 0;
        /* face = elems[0..depth-1] ascending; extension candidates v > last */
        if (!ispivot[off[0]]) {
            nstd = 1;
            int cand_next[64]; (void)cand_next;
            int nxt[64]; nxt[0] = 0; depth = 0; (void)stackv;
            /* recursive implementation with explicit stack of next vertex */
            while (1) {
                int v = nxt[depth];
                if (v >= N) { if (depth == 0) break; depth--; nxt[depth]++; continue; }
                /* try to add v to face elems[0..depth-1] */
                int ok = 1; u64 vm = (u64)1 << v;
                u64 base = 0; for (int i = 0; i < depth; i++) base |= (u64)1 << elems[i];
                /* all subsets T of the face with |T| <= D-1 : T u {v} must not be an LM */
                /* enumerate subsets of size 0..D-1 by index combos */
                if (ispivot[col_of(vm)]) ok = 0;
                if (ok && D >= 2) for (int a = 0; a < depth && ok; a++) {
                    u64 m1 = vm | ((u64)1 << elems[a]);
                    if (ispivot[col_of(m1)]) { ok = 0; break; }
                    if (D >= 3) for (int b2 = a + 1; b2 < depth && ok; b2++) {
                        u64 m2 = m1 | ((u64)1 << elems[b2]);
                        if (ispivot[col_of(m2)]) { ok = 0; break; }
                        if (D >= 4) for (int c3 = b2 + 1; c3 < depth && ok; c3++) {
                            u64 m3 = m2 | ((u64)1 << elems[c3]);
                            if (ispivot[col_of(m3)]) { ok = 0; break; }
                        }
                    }
                }
                if (D > 4 && ok) { fprintf(stderr, "N_std for D>4 not implemented\n"); ok = 0; }
                if (ok) { nstd++; elems[depth] = v; depth++; nxt[depth] = v + 1; }
                else nxt[depth]++;
            }
        }
    }
    printf("{\"N\": %d, \"M\": %d, \"D\": %d, \"columns\": %ld, \"rank\": %ld, \"one_in_W\": %d, \"lm_by_size\": [", N, M, D, C, r_out, one_in_W ? 1 : (constant_in ? 1 : 0));
    for (int s = 0; s <= D; s++) printf("%ld%s", by[s], s < D ? ", " : "");
    printf("], \"n_lm\": %ld, \"N_std\": %lu, \"wave_ranks\": [", nl, nstd);
    for (int i = 0; i < nwaves; i++) printf("%ld%s", wave_rank[i], i + 1 < nwaves ? ", " : "");
    printf("], \"wave_candidates\": [");
    for (int i = 0; i < nwaves; i++) printf("%ld%s", wave_cand[i], i + 1 < nwaves ? ", " : "");
    printf("], \"wave_seconds\": [");
    for (int i = 0; i < nwaves; i++) printf("%.1f%s", wave_time[i], i + 1 < nwaves ? ", " : "");
    printf("], \"total_candidates\": %ld, \"early_exit_one\": %d, \"wall_s\": %.1f, \"compactions\": %d, \"mutant\": {\"budget_shift\": %d, \"gens_only\": %d, \"drop_last\": %d}}\n",
           total_cand, (one_in_W && early_exit) ? 1 : 0, t1 - t0, epoch_compactions, budget_shift, mut_gens_only, mut_drop_last);
    if (outp) {
        /* also write the final rows? not needed. */
    }
    return 0;
}
