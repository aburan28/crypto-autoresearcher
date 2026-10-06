/* EXP-SEMBIN-35bf67 -- GF(2) linear-algebra kernel interface.
 * Two independent implementations:
 *   kernel_a.c : M4RI release-20240729 (mzd_addmul, mzd_echelonize_pluq)
 *   kernel_b.c : executor-written C (Gray-code four-Russians product, Gauss-Jordan)
 * The arms share NO code below this interface.
 * Matrices are row-major arrays of 64-bit words; bit j of a row is word j>>6, bit j&63.
 * Strides are in words, even, and row starts are 16-byte aligned. Bits at column
 * indices >= ncols are zero on entry and must be zero on exit.
 */
#ifndef SEMBIN_KERNEL_H
#define SEMBIN_KERNEL_H
#include <stdint.h>
#include <stddef.h>
typedef uint64_t word;

/* C[m x n] ^= A[m x kd] * B[kd x n] over GF(2). */
void k_muladd(word *C, size_t Cs, int m, int n,
              const word *A, size_t As, int kd,
              const word *B, size_t Bs);

/* In-place reduced row echelon form of X[m x n] (leftmost pivots).
 * Returns rank d; rows 0..d-1 hold the RREF rows with pivot columns piv[0..d-1]
 * strictly increasing; rows d..m-1 are zero. */
int k_rref(word *X, size_t Xs, int m, int n, int *piv);

const char *k_name(void);
#endif
