/*
 * gf2kern.c -- GF(2) kernels written for TASK-20260926-f0736e (blind
 * re-derivation, REVIEW-CERTBIN-20260926-d7249d). Own code; imports and copies
 * nothing from crypto_autoresearcher or any archived engine.
 *
 * Representation: a vector over F_2 with ncols coordinates is packed into
 * nwords = ceil(ncols/64) uint64 words, coordinate c = bit (c % 64) of word
 * (c / 64).  Column 0 is the FIRST column of the order used by the caller
 * (the caller uses a degree-descending order, so the lowest set coordinate of
 * a vector is its leading, highest-degree monomial).
 *
 * Elimination method: incremental SEMI-ECHELON basis.  Every basis row has a
 * distinct leading column (its lowest set coordinate) and no set coordinate
 * before it.  A vector is reduced by scanning its words left to right and
 * XOR-ing in the basis row whose leading column is the lowest remaining set
 * pivot coordinate, until no pivot coordinate is set.  A non-zero remainder is
 * appended as a new basis row.  Rows already in the basis are never modified,
 * so the rank equals the number of rows and the span is exact.  Optional tag
 * vectors (tw words per row) are carried along with every XOR, which records
 * each basis row as a combination of the inserted generators.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static int reduce_vec(int nw, const uint64_t *rows, const int *pivrow,
                      const uint64_t *pivmask, uint64_t *v, int tw,
                      const uint64_t *tagrows, uint64_t *vtag)
{
    for (int w = 0; w < nw; w++) {
        uint64_t x = v[w] & pivmask[w];
        while (x) {
            int b = __builtin_ctzll(x);
            int c = w * 64 + b;
            int r = pivrow[c];
            const uint64_t *row = rows + (size_t)r * nw;
            for (int u = w; u < nw; u++) v[u] ^= row[u];
            if (tw) {
                const uint64_t *t = tagrows + (size_t)r * tw;
                for (int u = 0; u < tw; u++) vtag[u] ^= t[u];
            }
            x = v[w] & pivmask[w];
        }
    }
    for (int w = 0; w < nw; w++)
        if (v[w]) return w * 64 + __builtin_ctzll(v[w]);
    return -1;
}

/*
 * Insert nv vectors (V, nv x nw) into the basis.  rank = current number of
 * rows, cap = row capacity.  result[i] = new row index if vector i was
 * independent, -1 if it reduced to zero.  If tw > 0, vector i carries the unit
 * tag at bit tagidx[i] (or a zero tag if tagidx[i] < 0).  Returns the new rank,
 * or -1 on capacity overflow.
 */
int insert_batch(int nw, uint64_t *rows, int *lead, int *pivrow,
                 uint64_t *pivmask, int rank, int cap, const uint64_t *V,
                 int nv, int *result, int tw, uint64_t *tagrows,
                 const int *tagidx)
{
    uint64_t *tmp = (uint64_t *)malloc((size_t)nw * 8);
    uint64_t *ttmp = tw ? (uint64_t *)malloc((size_t)tw * 8) : NULL;
    for (int i = 0; i < nv; i++) {
        memcpy(tmp, V + (size_t)i * nw, (size_t)nw * 8);
        if (tw) {
            memset(ttmp, 0, (size_t)tw * 8);
            if (tagidx[i] >= 0) ttmp[tagidx[i] >> 6] |= 1ULL << (tagidx[i] & 63);
        }
        int c = reduce_vec(nw, rows, pivrow, pivmask, tmp, tw, tagrows, ttmp);
        if (c < 0) { result[i] = -1; continue; }
        if (rank >= cap) { free(tmp); if (ttmp) free(ttmp); return -1; }
        memcpy(rows + (size_t)rank * nw, tmp, (size_t)nw * 8);
        if (tw) memcpy(tagrows + (size_t)rank * tw, ttmp, (size_t)tw * 8);
        lead[rank] = c;
        pivrow[c] = rank;
        pivmask[c >> 6] |= 1ULL << (c & 63);
        result[i] = rank;
        rank++;
    }
    free(tmp);
    if (ttmp) free(ttmp);
    return rank;
}

/*
 * Reduce nv vectors in place (V, nv x nw) against the basis without inserting;
 * the tags of the XOR-ed rows accumulate into Vtag (nv x tw, caller-zeroed).
 * lead_out[i] = leading column of the remainder, -1 if zero.
 */
void reduce_batch(int nw, const uint64_t *rows, const int *pivrow,
                  const uint64_t *pivmask, uint64_t *V, int nv, int *lead_out,
                  int tw, const uint64_t *tagrows, uint64_t *Vtag)
{
    for (int i = 0; i < nv; i++)
        lead_out[i] = reduce_vec(nw, rows, pivrow, pivmask, V + (size_t)i * nw,
                                 tw, tagrows, tw ? Vtag + (size_t)i * tw : NULL);
}

/*
 * Multilinear product by one variable: for each source row (deg <= D-1 by
 * the caller's contract), dst row = XOR over set coordinates c of
 * e_{cmap[c]}.  cmap[c] < 0 marks a product outside the column set; hitting
 * one sets *err = 1.  dst must be zeroed by the caller.
 */
void mul_var(int nw_src, int nw_dst, const uint64_t *src, int nsrc,
             const int *cmap, uint64_t *dst, int *err)
{
    for (int i = 0; i < nsrc; i++) {
        const uint64_t *s = src + (size_t)i * nw_src;
        uint64_t *d = dst + (size_t)i * nw_dst;
        for (int w = 0; w < nw_src; w++) {
            uint64_t x = s[w];
            while (x) {
                int b = __builtin_ctzll(x);
                int t = cmap[w * 64 + b];
                if (t < 0) *err = 1;
                else d[t >> 6] ^= 1ULL << (t & 63);
                x &= x - 1;
            }
        }
    }
}

/*
 * Back-substitution to reduced row echelon form: afterwards no basis row has
 * a set bit at another row's leading column.  Processes rows in DESCENDING
 * leading column so every row is cleared by already-reduced rows.
 */
void full_reduce(int nw, uint64_t *rows, const int *lead, int rank,
                 const int *pivrow, int tw, uint64_t *tagrows)
{
    /* order rows by leading column descending */
    int *ord = (int *)malloc((size_t)rank * sizeof(int));
    int n = 0;
    int ncols = nw * 64;
    for (int c = ncols - 1; c >= 0; c--)
        if (pivrow[c] >= 0 && pivrow[c] < rank) ord[n++] = pivrow[c];
    /* for each row (from the one with the largest lead), clear its lead bit
       from all other rows with a smaller lead */
    for (int a = 0; a < n; a++) {
        int r = ord[a];
        int c = lead[r];
        int w = c >> 6;
        uint64_t m = 1ULL << (c & 63);
        const uint64_t *row = rows + (size_t)r * nw;
        for (int q = 0; q < rank; q++) {
            if (q == r) continue;
            uint64_t *o = rows + (size_t)q * nw;
            if (o[w] & m) {
                for (int u = w; u < nw; u++) o[u] ^= row[u];
                if (tw) {
                    uint64_t *to = tagrows + (size_t)q * tw;
                    const uint64_t *tr = tagrows + (size_t)r * tw;
                    for (int u = 0; u < tw; u++) to[u] ^= tr[u];
                }
            }
        }
    }
    free(ord);
}

/* parity[i*nb + j] = popcount(A_i & B_j) mod 2  (A: na x nw, B: nb x nw) */
void parity_products(int nw, const uint64_t *A, int na, const uint64_t *B,
                     int nb, uint8_t *out)
{
    for (int i = 0; i < na; i++) {
        const uint64_t *a = A + (size_t)i * nw;
        for (int j = 0; j < nb; j++) {
            const uint64_t *b = B + (size_t)j * nw;
            uint64_t acc = 0;
            for (int u = 0; u < nw; u++) acc ^= a[u] & b[u];
            out[(size_t)i * nb + j] = (uint8_t)(__builtin_popcountll(acc) & 1);
        }
    }
}
