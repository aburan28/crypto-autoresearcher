/* Fused CUDA column pass for the rank-profile solver (gf2/gpu/rankpass.py).
 *
 * Same pivots (ps, cs, in order) and final matrix as the CPU blocked pass
 * (_kernels.c gf2_column_pass_blocked_mt without an op log). Per 64-column
 * word block w the host launches, on one stream and with one host sync (the
 * active-row count):
 *
 *   rp_block_elim  one CUDA block: the in-word elimination of the active rows'
 *                  word w (pivot = smallest active index with lead bit b, as on
 *                  the CPU), recording coef (pivot slots absorbed) and the
 *                  pivots (ps, cs) at the device counter K;
 *   rp_gather      the pivots' pre-block tails Bs (npiv x tail);
 *   rp_union       per tail word, whether any pivot tail is nonzero there;
 *   rp_update      per WPB-word chunk: the 8-bit tables of the pivot tails in
 *                  shared memory, then every active row with a nonzero coef
 *                  takes one table entry per coef byte (the CPU tail_chunk
 *                  update); chunks where every pivot tail is zero exit at once;
 *   rp_leads       write back word w, retire pivots, and find each other active
 *                  row's next lead word.
 *
 * The tables hold, for byte value s of group g, the XOR of the pivot tails
 * whose bits are set in s; that is what the CPU Gray-code tables hold, so the
 * update is the same function of (coef, Bs) and gives the same bits.
 */
#include <stdint.h>

#define WPB 4   /* tail words per update block: 4 * 8 * 256 * 8 B = 64 KiB of tables */

extern "C" __global__ void rp_init_leads(const uint64_t *M, int64_t R, int64_t W, int64_t C,
                                         int32_t *lw)
{
    int64_t r = (int64_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (r >= R)
        return;
    const uint64_t *row = M + r * W;
    int32_t out = -1;
    for (int64_t w = 0; w < W; w++) {
        uint64_t x = row[w];
        if (x) {
            int64_t c = 64 * w + __ffsll((long long)x) - 1;
            out = c < C ? (int32_t)w : -1;
            break;
        }
    }
    lw[r] = out;
}

/* One block. act: na active rows, ascending. state[0] = K (pivots so far),
 * state[1] = npiv of this step (written here, read by the later kernels). */
extern "C" __global__ void rp_block_elim(const uint64_t *M, int64_t W, int64_t w, int nbits,
                                         const int32_t *act, int64_t na, uint64_t *val,
                                         uint64_t *coef, uint8_t *isp, int32_t *piv_a,
                                         int32_t *ps, int32_t *cs, int64_t *state)
{
    __shared__ int32_t minp;
    __shared__ int npiv;
    int tid = threadIdx.x, nt = blockDim.x;
    for (int64_t a = tid; a < na; a += nt) {
        val[a] = M[(int64_t)act[a] * W + w];
        coef[a] = 0;
        isp[a] = 0;
    }
    if (tid == 0)
        npiv = 0;
    __syncthreads();
    for (int b = 0; b < nbits; b++) {
        if (tid == 0)
            minp = 0x7fffffff;
        __syncthreads();
        uint64_t bit = 1ULL << b, low = (bit << 1) - 1;
        for (int64_t a = tid; a < na; a += nt)
            if (!isp[a] && (val[a] & low) == bit)      /* lead bit is b */
                atomicMin(&minp, (int32_t)a);
        __syncthreads();
        int32_t p = minp;
        if (p == 0x7fffffff)
            continue;                                   /* uniform across the block */
        int slot = npiv;
        uint64_t pv = val[p], pc = coef[p] ^ (1ULL << slot);
        __syncthreads();                                /* everyone has read slot, pv, pc */
        if (tid == 0) {
            isp[p] = 1;
            piv_a[slot] = p;
            int64_t K = state[0] + slot;
            ps[K] = act[p];
            cs[K] = (int32_t)(64 * w + b);
            npiv = slot + 1;
        }
        for (int64_t a = tid; a < na; a += nt)
            if (a != p && !isp[a] && (val[a] & low) == bit) {
                val[a] ^= pv;
                coef[a] ^= pc;
            }
        __syncthreads();
    }
    if (tid == 0) {
        state[1] = npiv;
        state[0] += npiv;
    }
}

extern "C" __global__ void rp_gather(const uint64_t *M, int64_t W, int64_t w1, int64_t tail,
                                     const int32_t *act, const int32_t *piv_a,
                                     const int64_t *state, uint64_t *Bs)
{
    int i = blockIdx.y;
    if (i >= (int)state[1])
        return;
    const uint64_t *src = M + (int64_t)act[piv_a[i]] * W + w1;
    for (int64_t x = (int64_t)blockIdx.x * blockDim.x + threadIdx.x; x < tail;
         x += (int64_t)gridDim.x * blockDim.x)
        Bs[(int64_t)i * tail + x] = src[x];
}

extern "C" __global__ void rp_union(const uint64_t *Bs, int64_t tail, const int64_t *state,
                                    uint8_t *uni)
{
    int64_t x = (int64_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (x >= tail)
        return;
    int np = (int)state[1];
    uint64_t u = 0;
    for (int i = 0; i < np; i++)
        u |= Bs[(int64_t)i * tail + x];
    uni[x] = u != 0;
}

/* blockDim.x = 256 (one table entry per thread per group and word). */
extern "C" __global__ void rp_update(uint64_t *M, int64_t W, int64_t w1, int64_t tail,
                                     const int32_t *act, int64_t na, const uint64_t *coef,
                                     const uint64_t *Bs, const uint8_t *uni,
                                     const int64_t *state)
{
    extern __shared__ uint64_t T[];                     /* [WPB][8][256] */
    int64_t x0 = (int64_t)blockIdx.x * WPB;
    int nw = tail - x0 < WPB ? (int)(tail - x0) : WPB;
    int any = 0;
    for (int q = 0; q < nw; q++)
        any |= uni[x0 + q];
    if (!any)
        return;                                         /* every pivot tail is zero here */
    int np = (int)state[1];
    if (!np)
        return;
    int ng = (np + 7) / 8;
    int s = threadIdx.x;                                /* 0..255 */
    for (int q = 0; q < nw; q++)
        for (int g = 0; g < ng; g++) {
            uint64_t v = 0;
            for (int i = 0; i < 8; i++) {
                int piv = 8 * g + i;
                if (((s >> i) & 1) && piv < np)
                    v ^= Bs[(int64_t)piv * tail + x0 + q];
            }
            T[(q * 8 + g) * 256 + s] = v;
        }
    __syncthreads();
    /* thread -> (row slot, word): consecutive threads take consecutive words of one row */
    int q = threadIdx.x % WPB;
    if (q >= nw)
        return;
    for (int64_t a = threadIdx.x / WPB; a < na; a += blockDim.x / WPB) {
        uint64_t cf = coef[a];
        if (!cf)
            continue;
        uint64_t acc = 0;
        for (int g = 0; g < ng; g++)
            acc ^= T[(q * 8 + g) * 256 + (int)((cf >> (8 * g)) & 0xFF)];
        if (acc)
            M[(int64_t)act[a] * W + w1 + x0 + q] ^= acc;
    }
}

extern "C" __global__ void rp_leads(uint64_t *M, int64_t W, int64_t C, int64_t w,
                                    const int32_t *act, int64_t na, const uint64_t *val,
                                    const uint8_t *isp, int32_t *lw)
{
    int64_t a = (int64_t)blockIdx.x * blockDim.x + threadIdx.x;
    if (a >= na)
        return;
    int32_t r = act[a];
    uint64_t *row = M + (int64_t)r * W;
    row[w] = val[a];
    if (isp[a]) {
        lw[r] = -1;
        return;
    }
    int32_t out = -1;                                   /* word w is now zero in this row */
    for (int64_t k = w + 1; k < W; k++) {
        uint64_t x = row[k];
        if (x) {
            int64_t c = 64 * k + __ffsll((long long)x) - 1;
            out = c < C ? (int32_t)k : -1;
            break;
        }
    }
    lw[r] = out;
}
