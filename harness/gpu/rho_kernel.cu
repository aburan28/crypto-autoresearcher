/* Batched Teske r-adding rho walk, one CUDA thread per group of walks.
 *
 * What this measures: sustained rho STEP throughput, with the scalar
 * accumulators (a, b) carried and distinguished points detected -- i.e. the
 * cost of a walk that could actually solve an instance, not a stripped inner
 * loop. What it does NOT measure: the host-side DP table, transfer, and
 * collision search. Those are amortized to near zero at realistic DP rates but
 * are not zero, so a throughput number from here is an UPPER BOUND on
 * end-to-end campaign rate and must be reported as such.
 *
 * Branch selection and the DP test both read the low limb of the Montgomery
 * representation of x. That is a deterministic function of the point, which is
 * all an r-adding walk requires, and it avoids a per-step conversion out of
 * the Montgomery domain that would distort the very thing being measured. The
 * Python reference in bench_rho_throughput.py replicates it exactly.
 */
#include "mont256.h"

#define LIMBS 4

extern "C" __global__ void rho_steps(
    u64 *X, u64 *Y, u64 *A, u64 *Bc,          /* walk state, nwalks each */
    const u64 *TX, const u64 *TY,             /* precomputed T_s points   */
    const u64 *TC, const u64 *TD,             /* and their (c_s, d_s)     */
    const u64 *p, u64 n0, const u64 *one, const u64 *order,
    u64 *dxbuf, u64 *dxinv, u64 *scratch,     /* nwalks * LIMBS scratch   */
    int nwalks, int walks_per_thread, int nsteps, int nbranch, int dp_bits,
    unsigned long long *dp_count)
{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int base = tid * walks_per_thread;
    if (base >= nwalks) return;
    int w = walks_per_thread;
    if (base + w > nwalks) w = nwalks - base;

    size_t off = (size_t)base * LIMBS;
    u64 *x = &X[off], *y = &Y[off], *a = &A[off], *b = &Bc[off];
    u64 *dx = &dxbuf[off], *di = &dxinv[off], *sc = &scratch[off];

    u64 pl[LIMBS], onel[LIMBS], ordl[LIMBS];
    f_copy(pl, p); f_copy(onel, one); f_copy(ordl, order);

    unsigned long long dps = 0;
    unsigned int branch_mask = (unsigned int)(nbranch - 1);

    for (int step = 0; step < nsteps; step++) {
        /* 1. pick a branch per walk and form the denominators x - T_s.x */
        for (int i = 0; i < w; i++) {
            unsigned int s = (unsigned int)x[(size_t)i * LIMBS] & branch_mask;
            f_sub(&dx[(size_t)i * LIMBS], &x[(size_t)i * LIMBS],
                  &TX[(size_t)s * LIMBS], pl);
        }

        /* 2. ONE field inversion for all w walks (Montgomery's trick) */
        f_batch_inv(di, dx, sc, w, LIMBS, pl, n0, onel);

        /* 3. the adds, plus the coefficient bookkeeping a += c_s, b += d_s */
        for (int i = 0; i < w; i++) {
            unsigned int s = (unsigned int)x[(size_t)i * LIMBS] & branch_mask;
            ec_add_affine_pre(&x[(size_t)i * LIMBS], &y[(size_t)i * LIMBS],
                              &TX[(size_t)s * LIMBS], &TY[(size_t)s * LIMBS],
                              &di[(size_t)i * LIMBS], pl, n0);
            s_addmod(&a[(size_t)i * LIMBS], &a[(size_t)i * LIMBS],
                     &TC[(size_t)s * LIMBS], ordl);
            s_addmod(&b[(size_t)i * LIMBS], &b[(size_t)i * LIMBS],
                     &TD[(size_t)s * LIMBS], ordl);

            /* 4. distinguished-point test (counted, not stored: the host-side
             *    table is out of scope for a throughput measurement) */
            u64 lo = x[(size_t)i * LIMBS];
            if (dp_bits > 0 && (lo & ((1ULL << dp_bits) - 1ULL)) == 0ULL) dps++;
        }
    }

    if (dps) atomicAdd(dp_count, dps);
}
