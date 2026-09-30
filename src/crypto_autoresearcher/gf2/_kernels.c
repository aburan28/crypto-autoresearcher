/*
 * Bit-packed GF(2) elimination kernels for the CERTBIN Macaulay engines.
 *
 * Layout (identical to the numpy engines in the experiments/EXP-CERTBIN-... impl directories):
 * a matrix is R rows x W uint64 words, row-major and contiguous; column c is
 * bit (c & 63) of word (c >> 6).
 *
 * Every function here reproduces, output for output, a numpy reference in
 * crypto_autoresearcher/gf2/reference.py; tests/test_gf2_kernels.py checks
 * that equality on random and on archived matrices. No function allocates
 * memory it does not free, except gf2_column_pass, whose op log is released
 * by gf2_log_free. No function touches Python objects, so ctypes releases the
 * GIL for the whole call and independent matrices can run on threads.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef uint64_t u64;
typedef int32_t i32;
typedef int64_t i64;

/* Run-time ISA dispatch (glibc ifunc): AVX-512 or AVX2 where the CPU has it,
 * baseline otherwise. The arithmetic is identical; only the XOR width changes. */
#if defined(__x86_64__) && defined(__GNUC__) && !defined(__clang__)
#define HOT __attribute__((target_clones("avx512f", "avx2", "default")))
#else
#define HOT
#endif

#define BIT(M, W, r, c) (((M)[(size_t)(r) * (W) + ((c) >> 6)] >> ((c) & 63)) & 1ULL)

static inline int lowest_bit_from(const u64 *row, int W, int wstart)
{
    for (int w = wstart; w < W; w++) {
        u64 x = row[w];
        if (x)
            return w * 64 + __builtin_ctzll(x);
    }
    return -1;
}

/* ------------------------------------------------------------------------ */
/* Column pass (the declared solver).                                        */
/* ------------------------------------------------------------------------ */
typedef struct {
    i32 *ps, *cs;          /* pivot row, pivot column; length K            */
    i64 *xoff;             /* K+1 offsets into xs                           */
    i32 *xs;               /* concatenated X_k (ascending row indices)       */
    i64 K, nx, cap_x;
} oplog_t;

static int push_x(oplog_t *L, i32 v)
{
    if (L->nx == L->cap_x) {
        i64 nc = L->cap_x ? 2 * L->cap_x : 4096;
        i32 *p = (i32 *)realloc(L->xs, (size_t)nc * sizeof(i32));
        if (!p)
            return -1;
        L->xs = p;
        L->cap_x = nc;
    }
    L->xs[L->nx++] = v;
    return 0;
}

/*
 * For each column c in 0..C-1: among rows not yet used as pivots, the pivot p
 * is the smallest ORIGINAL row index with a 1 in column c; row p is XORed into
 * every other unused row with a 1 in column c (set X, ascending). Rows never
 * move. Invariant (EXP-CERTBIN-4e92d7 impl/README.md): after columns < c are
 * processed every unused row is zero in columns < c, so XORs start at word
 * c >> 6.
 *
 * Implementation: by that invariant, the unused rows with a 1 in column c are
 * exactly the unused rows whose lowest set column (lead) is c. Rows are kept
 * in per-lead buckets, so no column is ever scanned: step c takes bucket c,
 * sorts it (smallest original index = pivot, X ascending), XORs, and moves
 * each X row to the bucket of its new lead (> c; zero rows drop out). The
 * pivot, the X sets and the final matrix are those of the scanning
 * definition.
 *
 * keep_ops = 0 records no X sets (xoff/xs stay empty) but still counts
 * sum |X_k| in *ops_strict.
 * Returns a heap oplog (free with gf2_log_free) or NULL on allocation failure.
 */
static int cmp_i32(const void *a, const void *b)
{
    i32 x = *(const i32 *)a, y = *(const i32 *)b;
    return (x > y) - (x < y);
}

HOT oplog_t *gf2_column_pass(u64 *M, i64 R, i64 W, i64 C, int keep_ops, i64 *ops_strict)
{
    oplog_t *L = (oplog_t *)calloc(1, sizeof(oplog_t));
    size_t rn = (size_t)(R > 0 ? R : 1), cn = (size_t)(C > 0 ? C : 1);
    i32 *head = (i32 *)malloc(cn * sizeof(i32));
    i32 *next = (i32 *)malloc(rn * sizeof(i32));
    i32 *tmp = (i32 *)malloc(rn * sizeof(i32));
    i64 kmax = R < C ? R : C;
    if (!L || !head || !next || !tmp)
        goto fail;
    L->ps = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->cs = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->xoff = (i64 *)malloc((size_t)(kmax + 2) * sizeof(i64));
    if (!L->ps || !L->cs || !L->xoff)
        goto fail;
    for (i64 c = 0; c < C; c++)
        head[c] = -1;
    for (i64 r = R - 1; r >= 0; r--) {
        int lc = lowest_bit_from(M + (size_t)r * W, (int)W, 0);
        if (lc >= 0 && lc < C) {
            next[r] = head[lc];
            head[lc] = (i32)r;
        }
    }
    i64 total = 0;
    L->xoff[0] = 0;
    for (i64 c = 0; c < C; c++) {
        if (head[c] < 0)
            continue;
        i64 n = 0;
        for (i32 r = head[c]; r >= 0; r = next[r])
            tmp[n++] = r;
        head[c] = -1;
        if (n > 1)
            qsort(tmp, (size_t)n, sizeof(i32), cmp_i32);
        int w = (int)(c >> 6);
        i32 p = tmp[0];
        const u64 *prow = M + (size_t)p * W;
        for (i64 t = 1; t < n; t++) {
            i32 r = tmp[t];
            u64 *rrow = M + (size_t)r * W;
            for (int x = w; x < W; x++)
                rrow[x] ^= prow[x];
            if (keep_ops && push_x(L, r))
                goto fail;
            int lc = lowest_bit_from(rrow, (int)W, w);
            if (lc >= 0 && lc < C) {
                next[r] = head[lc];
                head[lc] = r;
            }
        }
        total += n - 1;
        L->ps[L->K] = p;
        L->cs[L->K] = (i32)c;
        L->K++;
        L->xoff[L->K] = L->nx;
    }
    free(head); free(next); free(tmp);
    *ops_strict = total;
    return L;
fail:
    free(head); free(next); free(tmp);
    if (L) {
        free(L->ps); free(L->cs); free(L->xoff); free(L->xs); free(L);
    }
    return NULL;
}

/*
 * Same contract and outputs as gf2_column_pass, restructured by 64-column
 * word blocks (Four-Russians style); tests check both against the reference.
 *
 * Within the block of word w every pivot choice and every X set depend only on
 * word w of the active rows (the unused rows whose lead lies in word w; no
 * other row has a 1 there). So the block is eliminated on a compact array of
 * those words while each active row a records coef[a], the set of the block's
 * pivot slots it has absorbed, expressed over the pivot rows' BLOCK-START
 * states B_i (row a now = start(a) + sum_{i in coef[a]} B_i). Words > w are
 * brought up to date once per block: B_i are snapshotted, 8-bit Gray-code
 * tables of their sums are built, and each updated row takes one table XOR per
 * byte of coef instead of one row XOR per absorbed pivot. XOR is associative
 * and commutative, so the final matrix equals the step-by-step one.
 */
/*
 * Trailing update of one word block (words w0 .. w0+tail-1 of every active
 * row): row act[a] ^= XOR of Bs[i] over the set bits i of coef[a], where
 * Bs[i] is the pre-block tail of the i-th pivot of the block. The result is a
 * fixed function of (coef, Bs), so neither the chunking nor the thread count
 * can change a single output bit.
 *
 * Columns are cut into chunks of CH words. For each chunk all ceil(npiv/8)
 * Gray-code tables (256 x CH words each) are built once and every row chunk
 * is read and written once with all its lookups applied (M4RI's multi-table
 * form; the previous version streamed each row once per 8-pivot group).
 * Chunks own disjoint columns, so threads take whole chunks: no two threads
 * write the same word, and each thread's tables are private.
 */
#define TAIL_TABLE_WORDS (1 << 17)   /* 1 MiB of tables per thread */

HOT static void tail_chunk(u64 *M, i64 W, i64 w0, i64 x0, i64 ch, const i32 *rows,
                           const u64 *cfs, int cw, i64 nr, const u64 *Bs, i64 tail, int npiv,
                           int tables, u64 *T)
{
    int ngroups = (npiv + 7) / 8;
    if (!tables) {
        for (i64 a = 0; a < nr; a++) {
            u64 *row = M + (size_t)rows[a] * W + w0 + x0;
            for (int q = 0; q < cw; q++) {
                u64 cf = cfs[(size_t)a * cw + q];
                while (cf) {
                    int i = 64 * q + __builtin_ctzll(cf);
                    cf &= cf - 1;
                    const u64 *bi = Bs + (size_t)i * tail + x0;
                    for (i64 x = 0; x < ch; x++)
                        row[x] ^= bi[x];
                }
            }
        }
        return;
    }
    for (int g = 0; g < ngroups; g++) {
        int k = npiv - 8 * g < 8 ? npiv - 8 * g : 8;
        int ns = 1 << k;
        u64 *Tg = T + (size_t)g * 256 * ch;
        memset(Tg, 0, (size_t)ch * sizeof(u64));
        for (int s2 = 1; s2 < ns; s2++) {
            int lb = __builtin_ctz(s2);
            const u64 *src = Tg + (size_t)(s2 & (s2 - 1)) * ch;
            const u64 *bi = Bs + (size_t)(8 * g + lb) * tail + x0;
            u64 *dst = Tg + (size_t)s2 * ch;
            for (i64 x = 0; x < ch; x++)
                dst[x] = src[x] ^ bi[x];
        }
    }
    const u64 *t[64];                       /* <= 64*SB_MAX/8 groups */
    for (i64 a = 0; a < nr; a++) {
        const u64 *cf = cfs + (size_t)a * cw;
        u64 *row = M + (size_t)rows[a] * W + w0 + x0;
        int nt = 0;
        for (int g = 0; g < ngroups; g++) {
            int s2 = (int)((cf[g >> 3] >> (8 * (g & 7))) & 0xFF);
            if (s2)
                t[nt++] = T + ((size_t)g * 256 + s2) * ch;
        }
        int j = 0;
        for (; j + 4 <= nt; j += 4) {
            const u64 *a0 = t[j], *a1 = t[j + 1], *a2 = t[j + 2], *a3 = t[j + 3];
            for (i64 x = 0; x < ch; x++)
                row[x] ^= a0[x] ^ a1[x] ^ a2[x] ^ a3[x];
        }
        for (; j + 2 <= nt; j += 2) {
            const u64 *a0 = t[j], *a1 = t[j + 1];
            for (i64 x = 0; x < ch; x++)
                row[x] ^= a0[x] ^ a1[x];
        }
        if (j < nt) {
            const u64 *a0 = t[j];
            for (i64 x = 0; x < ch; x++)
                row[x] ^= a0[x];
        }
    }
}

static int tail_update(u64 *M, i64 W, i64 w0, i64 tail, const i32 *act, const u64 *coef,
                       int cw, i64 na, const u64 *Bs, int npiv, int nthreads, i32 *rows, u64 *cfs,
                       u64 *Tpool)
{
    i64 nr = 0, pops = 0;
    for (i64 a = 0; a < na; a++) {
        const u64 *cf = coef + (size_t)a * cw;
        i64 pc = 0;
        for (int q = 0; q < cw; q++)
            pc += __builtin_popcountll(cf[q]);
        if (pc) {
            rows[nr] = act[a];
            memcpy(cfs + (size_t)nr * cw, cf, (size_t)cw * sizeof(u64));
            pops += pc;
            nr++;
        }
    }
    if (!nr)
        return 0;
    int ngroups = (npiv + 7) / 8;
    /* tables cost ~2^8 row XORs per group to build, then <= 1 per group per row */
    int tables = pops > (i64)ngroups * (256 + nr);
    i64 ch = tables ? TAIL_TABLE_WORDS / (256 * ngroups) : tail;
    if (ch < 8)
        ch = 8;
    if (ch > tail)
        ch = tail;
    if (ch >= 8)
        ch &= ~(i64)7;                       /* whole cache lines per chunk */
    i64 nch = (tail + ch - 1) / ch;
    int nt = 1;
#ifdef _OPENMP
    /* threads only where the block carries enough work to pay for them */
    if (nthreads > 1 && (double)nr * (double)tail > (double)(1 << 15)) {
        nt = nthreads;
        if (nch < nt) {                       /* split finer so every thread has columns */
            ch = (tail + nt - 1) / nt;
            if (ch >= 8)
                ch = (ch + 7) & ~(i64)7;
            nch = (tail + ch - 1) / ch;
        }
        if (nch < nt)
            nt = (int)nch;
    }
#endif
    (void)nt;                                /* unused without OpenMP */
    /* Tpool: nthreads private table areas of TAIL_TABLE_WORDS words each,
     * allocated once per pass (a fresh 1 MiB malloc per step is an mmap and a
     * page-fault storm per step). ngroups * 256 * ch <= TAIL_TABLE_WORDS. */
#ifdef _OPENMP
#pragma omp parallel num_threads(nt) if (nt > 1)
#endif
    {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        u64 *T = Tpool + (size_t)tid * TAIL_TABLE_WORDS;
#ifdef _OPENMP
#pragma omp for schedule(dynamic, 1)
#endif
        for (i64 q = 0; q < nch; q++) {
            i64 x0 = q * ch, c2 = tail - x0 < ch ? tail - x0 : ch;
            tail_chunk(M, W, w0, x0, c2, rows, cfs, cw, nr, Bs, tail, npiv, tables, T);
        }
    }
    return 0;
}

/*
 * Super-blocked column pass: the declared solver, output for output (op log,
 * final matrix, ops_strict) equal to gf2_column_pass, processing SB words
 * (64*SB columns) per step instead of one.
 *
 * Why the op log cannot change: when the pass reaches column c of the
 * super-block [w, w+SB), every unused row with a 1 in c has its lead in
 * [w*64, c] (all columns left of w*64 are eliminated from unused rows), so it
 * is in the super-block's active set, whose super-block words are held exactly
 * in val. The pivot (smallest unused row index with bit c) and X (the other
 * such rows, ascending) are therefore the ones the column-at-a-time pass
 * picks. Only the far tail (words >= w+SB) is deferred: each active row
 * carries its combination of the super-block pivots' pre-step far tails in
 * coef (up to 64*SB bits), applied once at the end of the step. A pivot's own
 * far tail at its pivot time is its pre-step tail plus its own coef
 * combination, which is why pc = coef[p] ^ e_slot is the right thing to XOR.
 *
 * The payoff is memory traffic: a row that travels right through the matrix
 * is read and written once per 64*SB columns rather than once per 64.
 */
#define SB_MAX 8

oplog_t *gf2_column_pass_sb(u64 *M, i64 R, i64 W, i64 C, int keep_ops, i64 *ops_strict,
                            int nthreads, int SB)
{
    if (SB < 1)
        SB = 1;
    if (SB > SB_MAX)
        SB = SB_MAX;
    oplog_t *L = (oplog_t *)calloc(1, sizeof(oplog_t));
    size_t rn = (size_t)(R > 0 ? R : 1), wn = (size_t)(W > 0 ? W : 1);
    size_t bmw = (rn + 63) / 64;
    int NB = 64 * SB;                                  /* columns per step */
    i32 *lw = (i32 *)malloc(rn * sizeof(i32));         /* lead word, -1 = zero or pivot */
    i64 *wcount = (i64 *)calloc(wn, sizeof(i64));
    i32 *act = (i32 *)malloc(rn * sizeof(i32));
    u64 *val = (u64 *)malloc(rn * SB * sizeof(u64));
    u64 *coef = (u64 *)malloc(rn * SB * sizeof(u64));
    uint8_t *isp = (uint8_t *)malloc(rn);
    u64 *bm = (u64 *)malloc((size_t)NB * bmw * sizeof(u64));   /* per-column bitmaps over act */
    u64 *Bs = (u64 *)malloc((size_t)NB * wn * sizeof(u64));
    i32 *rows = (i32 *)malloc(rn * sizeof(i32));
    u64 *cfs = (u64 *)malloc(rn * SB * sizeof(u64));
    i32 *piv_a = (i32 *)malloc((size_t)NB * sizeof(i32));
    int ntp = nthreads < 1 ? 1 : nthreads;
    u64 *Tpool = (u64 *)malloc((size_t)ntp * TAIL_TABLE_WORDS * sizeof(u64));
    i64 kmax = R < C ? R : C;
    if (!L || !lw || !wcount || !act || !val || !coef || !isp || !bm || !Bs || !rows || !cfs || !piv_a || !Tpool)
        goto fail;
    L->ps = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->cs = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->xoff = (i64 *)malloc((size_t)(kmax + 2) * sizeof(i64));
    if (!L->ps || !L->cs || !L->xoff)
        goto fail;
    for (i64 r = 0; r < R; r++) {
        int lc = lowest_bit_from(M + (size_t)r * W, (int)W, 0);
        lw[r] = (lc >= 0 && lc < C) ? (i32)(lc >> 6) : -1;
        if (lw[r] >= 0)
            wcount[lw[r]]++;
    }
    i64 total = 0;
    L->xoff[0] = 0;
    for (i64 w = 0; w < W; w += SB) {
        int sw = (int)(W - w < SB ? W - w : SB);       /* words in this step */
        i64 any = 0;
        for (int q = 0; q < sw; q++)
            any += wcount[w + q];
        if (!any)
            continue;
        i64 na = 0;
        for (i64 r = 0; r < R; r++)
            if (lw[r] >= (i32)w && lw[r] < (i32)(w + sw))
                act[na++] = (i32)r;
        size_t nwa = ((size_t)na + 63) / 64;
        int nbits = 64 * sw;
        memset(bm, 0, (size_t)nbits * nwa * sizeof(u64));
        for (i64 a = 0; a < na; a++) {
            u64 *v = val + (size_t)a * SB, *cf = coef + (size_t)a * SB;
            const u64 *row = M + (size_t)act[a] * W + w;
            int lead = -1;
            for (int q = 0; q < sw; q++) {
                v[q] = row[q];
                cf[q] = 0;
                if (lead < 0 && row[q])
                    lead = 64 * q + __builtin_ctzll(row[q]);
            }
            isp[a] = 0;
            bm[(size_t)lead * nwa + (a >> 6)] |= 1ULL << (a & 63);
        }
        int npiv = 0;
        u64 pv[SB_MAX], pc[SB_MAX];
        for (int b = 0; b < nbits; b++) {
            i64 c = w * 64 + b;
            if (c >= C)
                break;
            u64 *bb = bm + (size_t)b * nwa;
            size_t q = 0;
            while (q < nwa && !bb[q])
                q++;
            if (q == nwa)
                continue;
            i32 p = (i32)(q * 64 + __builtin_ctzll(bb[q]));
            bb[q] &= bb[q] - 1;
            int slot = npiv++;
            piv_a[slot] = p;
            isp[p] = 1;
            const u64 *vp = val + (size_t)p * SB, *cp = coef + (size_t)p * SB;
            for (int k = 0; k < sw; k++) {
                pv[k] = vp[k];
                pc[k] = cp[k];
            }
            pc[slot >> 6] ^= 1ULL << (slot & 63);
            int b0 = b >> 6;                            /* words below b0 are zero in X rows */
            i64 n = 1;
            for (; q < nwa; q++) {
                u64 word = bb[q];
                bb[q] = 0;
                while (word) {
                    i32 x = (i32)(q * 64 + __builtin_ctzll(word));
                    word &= word - 1;
                    if (keep_ops && push_x(L, act[x]))
                        goto fail;
                    u64 *vx = val + (size_t)x * SB, *cx = coef + (size_t)x * SB;
                    int nb = -1;
                    for (int k = b0; k < sw; k++) {
                        vx[k] ^= pv[k];
                        if (nb < 0 && vx[k])
                            nb = 64 * k + __builtin_ctzll(vx[k]);
                    }
                    for (int k = 0; k <= (slot >> 6); k++)
                        cx[k] ^= pc[k];
                    if (nb >= 0)                        /* nb > b */
                        bm[(size_t)nb * nwa + (x >> 6)] |= 1ULL << (x & 63);
                    n++;
                }
            }
            total += n - 1;
            L->ps[L->K] = act[p];
            L->cs[L->K] = (i32)c;
            L->K++;
            L->xoff[L->K] = L->nx;
        }
        /* bring words >= w+sw up to date */
        i64 w1 = w + sw, tail = W - w1;
        if (tail > 0 && npiv) {
            for (int i = 0; i < npiv; i++)
                memcpy(Bs + (size_t)i * tail, M + (size_t)act[piv_a[i]] * W + w1,
                       (size_t)tail * sizeof(u64));
            int cw = (npiv + 63) / 64;
            if (cw < SB) {                              /* compact coef to cw words per row */
                for (i64 a = 0; a < na; a++)
                    for (int k = 0; k < cw; k++)
                        coef[(size_t)a * cw + k] = coef[(size_t)a * SB + k];
            }
            if (tail_update(M, W, w1, tail, act, coef, cw < SB ? cw : SB, na, Bs, npiv, ntp,
                            rows, cfs, Tpool))
                goto fail;
        }
        for (int q = 0; q < sw; q++)
            wcount[w + q] = 0;
        for (i64 a = 0; a < na; a++) {
            i32 r = act[a];
            u64 *row = M + (size_t)r * W;
            for (int q = 0; q < sw; q++)
                row[w + q] = val[(size_t)a * SB + q];
            if (isp[a]) {
                lw[r] = -1;
                continue;
            }
            /* every unused active row is now zero in words w .. w+sw-1 */
            int lc = lowest_bit_from(row, (int)W, (int)w1);
            lw[r] = (lc >= 0 && lc < C) ? (i32)(lc >> 6) : -1;
            if (lw[r] >= 0)
                wcount[lw[r]]++;
        }
    }
    free(lw); free(wcount); free(act); free(val); free(coef); free(isp); free(bm); free(Bs);
    free(rows); free(cfs); free(piv_a); free(Tpool);
    *ops_strict = total;
    return L;
fail:
    free(lw); free(wcount); free(act); free(val); free(coef); free(isp); free(bm); free(Bs);
    free(rows); free(cfs); free(piv_a); free(Tpool);
    if (L) {
        free(L->ps); free(L->cs); free(L->xoff); free(L->xs); free(L);
    }
    return NULL;
}

oplog_t *gf2_column_pass_blocked_mt(u64 *M, i64 R, i64 W, i64 C, int keep_ops, i64 *ops_strict,
                                    int nthreads)
{
    oplog_t *L = (oplog_t *)calloc(1, sizeof(oplog_t));
    size_t rn = (size_t)(R > 0 ? R : 1), wn = (size_t)(W > 0 ? W : 1);
    size_t bmw = (rn + 63) / 64;
    i32 *lw = (i32 *)malloc(rn * sizeof(i32));      /* lead word, -1 = zero or pivot */
    i64 *wcount = (i64 *)calloc(wn, sizeof(i64));
    i32 *act = (i32 *)malloc(rn * sizeof(i32));
    u64 *val = (u64 *)malloc(rn * sizeof(u64));
    u64 *coef = (u64 *)malloc(rn * sizeof(u64));
    uint8_t *isp = (uint8_t *)malloc(rn);
    u64 *bm = (u64 *)malloc(64 * bmw * sizeof(u64));  /* per-bit bitmaps over act */
    u64 *Bs = (u64 *)malloc((size_t)64 * wn * sizeof(u64));
    i32 *rows = (i32 *)malloc(rn * sizeof(i32));
    u64 *cfs = (u64 *)malloc(rn * sizeof(u64));
    int ntp = nthreads < 1 ? 1 : nthreads;
    u64 *Tpool = (u64 *)malloc((size_t)ntp * TAIL_TABLE_WORDS * sizeof(u64));
    i64 kmax = R < C ? R : C;
    i32 piv_a[64];
    if (!L || !lw || !wcount || !act || !val || !coef || !isp || !bm || !Bs || !rows || !cfs || !Tpool)
        goto fail;
    L->ps = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->cs = (i32 *)malloc((size_t)(kmax + 1) * sizeof(i32));
    L->xoff = (i64 *)malloc((size_t)(kmax + 2) * sizeof(i64));
    if (!L->ps || !L->cs || !L->xoff)
        goto fail;
    for (i64 r = 0; r < R; r++) {
        int lc = lowest_bit_from(M + (size_t)r * W, (int)W, 0);
        lw[r] = (lc >= 0 && lc < C) ? (i32)(lc >> 6) : -1;
        if (lw[r] >= 0)
            wcount[lw[r]]++;
    }
    i64 total = 0;
    L->xoff[0] = 0;
    for (i64 w = 0; w < W; w++) {
        if (!wcount[w])
            continue;
        /* active rows of this word, ascending (a scan keeps them sorted) */
        i64 na = 0;
        for (i64 r = 0; r < R; r++)
            if (lw[r] == (i32)w)
                act[na++] = (i32)r;
        size_t nwa = ((size_t)na + 63) / 64;
        memset(bm, 0, 64 * nwa * sizeof(u64));
        for (i64 a = 0; a < na; a++) {
            val[a] = M[(size_t)act[a] * W + w];
            coef[a] = 0;
            isp[a] = 0;
            int b = __builtin_ctzll(val[a]);
            bm[(size_t)b * nwa + (a >> 6)] |= 1ULL << (a & 63);
        }
        int npiv = 0;
        for (int b = 0; b < 64; b++) {
            i64 c = w * 64 + b;
            if (c >= C)
                break;
            u64 *bb = bm + (size_t)b * nwa;
            /* smallest member = pivot; the rest, ascending, = X */
            size_t q = 0;
            while (q < nwa && !bb[q])
                q++;
            if (q == nwa)
                continue;
            i32 p = (i32)(q * 64 + __builtin_ctzll(bb[q]));
            bb[q] &= bb[q] - 1;
            int slot = npiv++;
            piv_a[slot] = p;
            isp[p] = 1;
            u64 pv = val[p], pc = coef[p] ^ (1ULL << slot);
            i64 n = 1;
            for (; q < nwa; q++) {
                u64 word = bb[q];
                bb[q] = 0;
                while (word) {
                    i32 x = (i32)(q * 64 + __builtin_ctzll(word));
                    word &= word - 1;
                    if (keep_ops && push_x(L, act[x]))
                        goto fail;
                    val[x] ^= pv;
                    coef[x] ^= pc;
                    if (val[x]) {
                        int nb = __builtin_ctzll(val[x]);   /* > b */
                        bm[(size_t)nb * nwa + (x >> 6)] |= 1ULL << (x & 63);
                    }
                    n++;
                }
            }
            total += n - 1;
            L->ps[L->K] = act[p];
            L->cs[L->K] = (i32)c;
            L->K++;
            L->xoff[L->K] = L->nx;
        }
        /* bring words > w up to date */
        i64 tail = W - w - 1;
        if (tail > 0 && npiv) {
            for (int i = 0; i < npiv; i++)
                memcpy(Bs + (size_t)i * tail, M + (size_t)act[piv_a[i]] * W + w + 1,
                       (size_t)tail * sizeof(u64));
            if (tail_update(M, W, w + 1, tail, act, coef, 1, na, Bs, npiv, ntp, rows, cfs, Tpool))
                goto fail;
        }
        wcount[w] = 0;
        for (i64 a = 0; a < na; a++) {
            i32 r = act[a];
            u64 *row = M + (size_t)r * W;
            row[w] = val[a];
            if (isp[a]) {
                lw[r] = -1;
                continue;
            }
            /* every unused active row is now zero in word w */
            int lc = lowest_bit_from(row, (int)W, (int)w + 1);
            lw[r] = (lc >= 0 && lc < C) ? (i32)(lc >> 6) : -1;
            if (lw[r] >= 0)
                wcount[lw[r]]++;
        }
    }
    free(lw); free(wcount); free(act); free(val); free(coef); free(isp); free(bm); free(Bs); free(rows); free(cfs); free(Tpool);
    *ops_strict = total;
    return L;
fail:
    free(lw); free(wcount); free(act); free(val); free(coef); free(isp); free(bm); free(Bs); free(rows); free(cfs); free(Tpool);
    if (L) {
        free(L->ps); free(L->cs); free(L->xoff); free(L->xs); free(L);
    }
    return NULL;
}

oplog_t *gf2_column_pass_blocked(u64 *M, i64 R, i64 W, i64 C, int keep_ops, i64 *ops_strict)
{
    return gf2_column_pass_blocked_mt(M, R, W, C, keep_ops, ops_strict, 1);
}

i64 gf2_log_K(const oplog_t *L) { return L->K; }
i64 gf2_log_nx(const oplog_t *L) { return L->nx; }

void gf2_log_copy(const oplog_t *L, i32 *ps, i32 *cs, i64 *xoff, i32 *xs)
{
    memcpy(ps, L->ps, (size_t)L->K * sizeof(i32));
    memcpy(cs, L->cs, (size_t)L->K * sizeof(i32));
    memcpy(xoff, L->xoff, (size_t)(L->K + 1) * sizeof(i64));
    if (L->nx)
        memcpy(xs, L->xs, (size_t)L->nx * sizeof(i32));
}

/* Zero-copy hand-off of the X list: the caller views L->xs in place and calls
 * gf2_log_free when its view is released (ps, cs, xoff are copied). */
void gf2_log_copy_meta(const oplog_t *L, i32 *ps, i32 *cs, i64 *xoff)
{
    memcpy(ps, L->ps, (size_t)L->K * sizeof(i32));
    memcpy(cs, L->cs, (size_t)L->K * sizeof(i32));
    memcpy(xoff, L->xoff, (size_t)(L->K + 1) * sizeof(i64));
}

i32 *gf2_log_xs(const oplog_t *L) { return L->xs; }

void gf2_log_free(oplog_t *L)
{
    if (!L)
        return;
    free(L->ps); free(L->cs); free(L->xoff); free(L->xs); free(L);
}

/* ------------------------------------------------------------------------ */
/* Row pass (the separate row-sequential instrument).                        */
/* ------------------------------------------------------------------------ */
/*
 * Rows in original order; Z = rows lying in the span of earlier rows; leads =
 * leading (lowest) columns of an echelon basis of the whole row space. The
 * numpy reference keeps its basis fully reduced; this keeps an echelon basis
 * indexed by lead column. Span membership and the SET of leading positions of
 * a row space do not depend on which echelon basis is kept, so Z and the
 * sorted leads are identical.
 *
 * Z (length R buffer) receives the Z rows ascending; leads (length min(R,C))
 * receives the lead columns ascending. Returns nZ, and *nleads; -1 on
 * allocation failure.
 */
HOT i64 gf2_row_pass(const u64 *M0, i64 R, i64 W, i64 C, i32 *Z, i32 *leads, i64 *nleads)
{
    i32 *slot = (i32 *)malloc((size_t)(C > 0 ? C : 1) * sizeof(i32));
    i64 kmax = R < C ? R : C;
    u64 *basis = (u64 *)malloc((size_t)(kmax > 0 ? kmax : 1) * W * sizeof(u64));
    u64 *v = (u64 *)malloc((size_t)(W > 0 ? W : 1) * sizeof(u64));
    if (!slot || !basis || !v) {
        free(slot); free(basis); free(v);
        return -1;
    }
    for (i64 c = 0; c < C; c++)
        slot[c] = -1;
    i64 nb = 0, nz = 0;
    for (i64 i = 0; i < R; i++) {
        memcpy(v, M0 + (size_t)i * W, (size_t)W * sizeof(u64));
        int lc = lowest_bit_from(v, (int)W, 0);
        while (lc >= 0 && slot[lc] >= 0) {
            const u64 *b = basis + (size_t)slot[lc] * W;
            int w0 = lc >> 6;
            for (int x = w0; x < W; x++)
                v[x] ^= b[x];
            lc = lowest_bit_from(v, (int)W, w0);
        }
        if (lc < 0) {
            Z[nz++] = (i32)i;
            continue;
        }
        memcpy(basis + (size_t)nb * W, v, (size_t)W * sizeof(u64));
        slot[lc] = (i32)nb;
        nb++;
    }
    i64 nl = 0;
    for (i64 c = 0; c < C; c++)
        if (slot[c] >= 0)
            leads[nl++] = (i32)c;
    *nleads = nl;
    free(slot); free(basis); free(v);
    return nz;
}

/* ------------------------------------------------------------------------ */
/* Canonical JSON of the op log: [[p,c,[x,...]],...] with no spaces.         */
/* ------------------------------------------------------------------------ */
static char *put_int(char *o, i64 x)
{
    char tmp[24];
    int n = 0;
    if (x < 0) {
        *o++ = '-';
        x = -x;
    }
    do {
        tmp[n++] = (char)('0' + (x % 10));
        x /= 10;
    } while (x);
    while (n)
        *o++ = tmp[--n];
    return o;
}

/* Upper bound on the output size: 12 bytes per integer plus brackets. */
i64 gf2_ops_json_bound(i64 K, i64 nx) { return 2 + K * (2 + 2 * 12 + 4) + nx * 12 + 16; }

i64 gf2_ops_json(const i32 *ps, const i32 *cs, const i64 *xoff, const i32 *xs, i64 K, char *out)
{
    char *o = out;
    *o++ = '[';
    for (i64 k = 0; k < K; k++) {
        if (k)
            *o++ = ',';
        *o++ = '[';
        o = put_int(o, ps[k]);
        *o++ = ',';
        o = put_int(o, cs[k]);
        *o++ = ',';
        *o++ = '[';
        for (i64 t = xoff[k]; t < xoff[k + 1]; t++) {
            if (t > xoff[k])
                *o++ = ',';
            o = put_int(o, xs[t]);
        }
        *o++ = ']';
        *o++ = ']';
    }
    *o++ = ']';
    return (i64)(o - out);
}

/* Canonical JSON of an int list: [a,b,...]. Bound: 12 bytes per entry + 2. */
i64 gf2_json_ints(const i32 *v, i64 n, char *out)
{
    char *o = out;
    *o++ = '[';
    for (i64 i = 0; i < n; i++) {
        if (i)
            *o++ = ',';
        o = put_int(o, v[i]);
    }
    *o++ = ']';
    return (i64)(o - out);
}

/* Canonical JSON of [[a0,b0],[a1,b1],...]. Bound: 27 bytes per pair + 2. */
i64 gf2_json_pairs(const i32 *a, const i32 *b, i64 n, char *out)
{
    char *o = out;
    *o++ = '[';
    for (i64 i = 0; i < n; i++) {
        if (i)
            *o++ = ',';
        *o++ = '[';
        o = put_int(o, a[i]);
        *o++ = ',';
        o = put_int(o, b[i]);
        *o++ = ']';
    }
    *o++ = ']';
    return (i64)(o - out);
}

/* ------------------------------------------------------------------------ */
/* Fixed-schedule replays.                                                   */
/* ------------------------------------------------------------------------ */
/*
 * planes: P matrices R x W, stacked (P, R, W), modified in place.
 * e (P x K uint8): entry (p_k, c_k) of each plane immediately BEFORE step k.
 */
HOT void gf2_replay_planes(u64 *planes, i64 P, i64 R, i64 W, const i32 *ps, const i32 *cs,
                       const i64 *xoff, const i32 *xs, i64 K, uint8_t *e)
{
    for (i64 pl = 0; pl < P; pl++) {
        u64 *M = planes + (size_t)pl * R * W;
        for (i64 k = 0; k < K; k++) {
            i32 p = ps[k], c = cs[k];
            int w = c >> 6;
            e[(size_t)pl * K + k] = (uint8_t)BIT(M, W, p, c);
            const u64 *prow = M + (size_t)p * W;
            for (i64 t = xoff[k]; t < xoff[k + 1]; t++) {
                u64 *rrow = M + (size_t)xs[t] * W;
                for (int x = w; x < W; x++)
                    rrow[x] ^= prow[x];
            }
        }
    }
}

/* Direct replay on one matrix (modified in place). e initialised by caller
 * (255); stops after the first zero entry if stop_at_zero. */
HOT void gf2_replay_direct(u64 *M, i64 R, i64 W, const i32 *ps, const i32 *cs, const i64 *xoff,
                       const i32 *xs, i64 K, int stop_at_zero, uint8_t *e)
{
    (void)R;
    for (i64 k = 0; k < K; k++) {
        i32 p = ps[k], c = cs[k];
        int w = c >> 6;
        uint8_t ek = (uint8_t)BIT(M, W, p, c);
        e[k] = ek;
        if (stop_at_zero && ek == 0)
            break;
        const u64 *prow = M + (size_t)p * W;
        for (i64 t = xoff[k]; t < xoff[k + 1]; t++) {
            u64 *rrow = M + (size_t)xs[t] * W;
            for (int x = w; x < W; x++)
                rrow[x] ^= prow[x];
        }
    }
}

/* ------------------------------------------------------------------------ */
/* Certificate back-trace.                                                   */
/* ------------------------------------------------------------------------ */
/*
 * S (n_rows x nw): bit t of row r says row r (FINAL state) belongs to target
 * t. Rewritten in place over the ORIGINAL row states: for k = K-1..0,
 * S[p_k] ^= XOR_{x in X_k} S[x].
 */
HOT void gf2_backtrace(u64 *S, i64 nw, const i32 *ps, const i64 *xoff, const i32 *xs, i64 K)
{
    u64 *par = (u64 *)calloc((size_t)(nw > 0 ? nw : 1), sizeof(u64));
    if (!par)
        return;
    for (i64 k = K - 1; k >= 0; k--) {
        if (xoff[k + 1] == xoff[k])
            continue;
        memset(par, 0, (size_t)nw * sizeof(u64));
        for (i64 t = xoff[k]; t < xoff[k + 1]; t++) {
            const u64 *r = S + (size_t)xs[t] * nw;
            for (i64 x = 0; x < nw; x++)
                par[x] ^= r[x];
        }
        u64 *pr = S + (size_t)ps[k] * nw;
        for (i64 x = 0; x < nw; x++)
            pr[x] ^= par[x];
    }
    free(par);
}

/* ------------------------------------------------------------------------ */
/* Scatter-XOR of single bits: M[rows[i], cols[i]] ^= 1 for i < n.           */
/* ------------------------------------------------------------------------ */
void gf2_xor_bits(u64 *M, i64 W, const i64 *rows, const i64 *cols, i64 n)
{
    for (i64 i = 0; i < n; i++)
        M[(size_t)rows[i] * W + (cols[i] >> 6)] ^= 1ULL << (cols[i] & 63);
}

/* ------------------------------------------------------------------------ */
/* Products v_j * row (multilinear) for the mutant closure.                  */
/* ------------------------------------------------------------------------ */
/*
 * rows (n x W); colmap (nv x C int32): target column of v_j * (column c), or
 * -1 for a column the reference ignores (degree > D-1). out ((nv*n) x W),
 * zero-initialised by the caller, j-major: out[j*n + f] = v_j * rows[f].
 */
void gf2_products(const u64 *rows, i64 n, i64 W, i64 C, const i32 *colmap, i64 nv, u64 *out)
{
    for (i64 f = 0; f < n; f++) {
        const u64 *r = rows + (size_t)f * W;
        for (i64 w = 0; w < W; w++) {
            u64 x = r[w];
            while (x) {
                i64 c = w * 64 + __builtin_ctzll(x);
                x &= x - 1;
                if (c >= C)
                    continue;
                for (i64 j = 0; j < nv; j++) {
                    i32 t = colmap[(size_t)j * C + c];
                    if (t < 0)
                        continue;
                    out[((size_t)j * n + f) * W + (t >> 6)] ^= 1ULL << (t & 63);
                }
            }
        }
    }
}
