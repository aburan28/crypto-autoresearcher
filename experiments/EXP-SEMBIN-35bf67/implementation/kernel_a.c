/* EXP-SEMBIN-35bf67 rank arm A: M4RI release-20240729 (git d0a1ee18), built from source.
 * Thin views over the driver's buffers; all elimination is M4RI's. */
#include "kernel.h"
#include <m4ri/m4ri.h>
#include <stdlib.h>
#include <string.h>

static mzd_t *view(const word *data, size_t stride, int nrows, int ncols) {
  mzd_t *A = (mzd_t *)aligned_alloc(64, 64);
  memset(A, 0, 64);
  A->nrows = nrows;
  A->ncols = ncols;
  A->width = (ncols + m4ri_radix - 1) / m4ri_radix;
  A->rowstride = (wi_t)stride;
  A->high_bitmask = __M4RI_LEFT_BITMASK(ncols % m4ri_radix);
  A->flags = (A->high_bitmask != m4ri_ffff) ? mzd_flag_nonzero_excess : 0;
  A->data = (word *)data;
  return A;
}

void k_muladd(word *C, size_t Cs, int m, int n, const word *A, size_t As, int kd,
              const word *B, size_t Bs) {
  if (m == 0 || n == 0 || kd == 0) return;
  mzd_t *c = view(C, Cs, m, n), *a = view(A, As, m, kd), *b = view(B, Bs, kd, n);
  mzd_addmul(c, a, b, 0);
  free(c); free(a); free(b);
}

int k_rref(word *X, size_t Xs, int m, int n, int *piv) {
  if (m == 0 || n == 0) return 0;
  mzd_t *x = view(X, Xs, m, n);
  rci_t d = mzd_echelonize_pluq(x, 1);
  free(x);
  for (int i = 0; i < d; i++) {
    const word *row = X + (size_t)i * Xs;
    int w = 0;
    while (row[w] == 0) w++;
    piv[i] = w * 64 + __builtin_ctzll(row[w]);
  }
  return (int)d;
}

const char *k_name(void) { return "A:m4ri-20240729-d0a1ee18(mzd_addmul,mzd_echelonize_pluq)"; }
