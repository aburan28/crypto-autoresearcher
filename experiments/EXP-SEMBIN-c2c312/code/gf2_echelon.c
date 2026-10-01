/* gf2_echelon.c -- thin M4RI wrapper for exact GF(2) row-reduction of sparse-input
 * matrices, callable from Python via ctypes.
 *
 *   gf2_echelon_begin(nrows, ncols, row_ptr, col_idx, full) -> rank
 *       builds a dense mzd_t from CSR-style input (row_ptr has nrows+1 entries,
 *       col_idx has row_ptr[nrows] entries), runs mzd_echelonize(full) and keeps
 *       the result in a static handle.  Rows are the input polynomials, columns
 *       are monomials; the caller orders columns so that the leftmost column is
 *       the largest monomial, so pivots are leading monomials.
 *   gf2_echelon_nnz() -> total number of ones in the nonzero (first `rank`) rows
 *   gf2_echelon_dump(out_row_ptr, out_col_idx) -> writes the reduced rows in CSR
 *   gf2_echelon_end() -> frees the matrix
 *
 * Exact arithmetic over GF(2); no randomness; single-threaded.
 */
#include <m4ri/m4ri.h>
#include <stdlib.h>

static mzd_t *G = NULL;
static long G_rank = 0;

long gf2_echelon_begin(long nrows, long ncols, const long *row_ptr,
                       const int *col_idx, int full) {
    if (G) { mzd_free(G); G = NULL; }
    if (nrows <= 0 || ncols <= 0) { G_rank = 0; return 0; }
    G = mzd_init((rci_t)nrows, (rci_t)ncols);
    for (long i = 0; i < nrows; i++) {
        for (long p = row_ptr[i]; p < row_ptr[i + 1]; p++) {
            mzd_write_bit(G, (rci_t)i, (rci_t)col_idx[p], 1);
        }
    }
    G_rank = (long)mzd_echelonize(G, full);
    return G_rank;
}

long gf2_echelon_nnz(void) {
    if (!G) return 0;
    long nnz = 0;
    for (long i = 0; i < G_rank; i++) {
        for (rci_t j = 0; j < G->ncols; j++) {
            nnz += mzd_read_bit(G, (rci_t)i, j);
        }
    }
    return nnz;
}

void gf2_echelon_dump(long *out_row_ptr, int *out_col_idx) {
    long pos = 0;
    out_row_ptr[0] = 0;
    if (!G) return;
    for (long i = 0; i < G_rank; i++) {
        for (rci_t j = 0; j < G->ncols; j++) {
            if (mzd_read_bit(G, (rci_t)i, j)) out_col_idx[pos++] = (int)j;
        }
        out_row_ptr[i + 1] = pos;
    }
}

void gf2_echelon_end(void) {
    if (G) { mzd_free(G); G = NULL; }
    G_rank = 0;
}
