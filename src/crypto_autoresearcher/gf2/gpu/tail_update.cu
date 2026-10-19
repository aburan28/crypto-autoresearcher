/* gf2 trailing-update kernel for CUDA.
 *
 * Bit-identical to src/crypto_autoresearcher/gf2/_kernels.c::tail_chunk when
 * called with the same (rows, cfs, Bs, npiv, tables) arguments. One CUDA block
 * owns one column chunk; threads in the block cooperatively build the Gray
 * tables (when tables!=0) and then each thread updates a stripe of rows.
 *
 * Host-side differential tests (tests/test_gf2_gpu_tail.py) compare this
 * against the CPU tail on random inputs whenever a CUDA device is present.
 * Without a GPU the source still ships and the CPU path is unchanged.
 *
 * Compiled at run time via CuPy/NVRTC (same pattern as harness/gpu/rho_kernel.cu).
 */
/* NVRTC ships no libc headers (no <stdint.h>): fixed-width types by hand */
typedef unsigned long long uint64_t;
typedef long long int64_t;
typedef int int32_t;
typedef unsigned char uint8_t;

extern "C" __global__ void gf2_tail_chunk(
    uint64_t *M,           /* R * W packed matrix, row-major */
    int64_t W,
    int64_t w0,            /* first word of the trailing region */
    int64_t x0,            /* offset within the trailing region for this chunk */
    int64_t ch,            /* chunk width in words */
    const int32_t *rows,   /* nr row indices to update */
    const uint64_t *cfs,   /* nr * cw coefficient words */
    int cw,
    int64_t nr,
    const uint64_t *Bs,    /* npiv * tail pre-block pivot tails */
    int64_t tail,
    int npiv,
    int tables,
    uint64_t *T            /* scratch: ngroups * 256 * ch words (block-local OK) */
)
{
    int ngroups = (npiv + 7) / 8;
    int tid = threadIdx.x;
    int nt = blockDim.x;

    if (!tables) {
        for (int64_t a = tid; a < nr; a += nt) {
            uint64_t *row = M + (int64_t)rows[a] * W + w0 + x0;
            for (int q = 0; q < cw; q++) {
                uint64_t cf = cfs[(int64_t)a * cw + q];
                while (cf) {
                    int i = 64 * q + __ffsll((unsigned long long)cf) - 1;
                    cf &= cf - 1;
                    const uint64_t *bi = Bs + (int64_t)i * (int64_t)tail + x0;
                    for (int64_t x = 0; x < ch; x++)
                        row[x] ^= bi[x];
                }
            }
        }
        return;
    }

    /* Build Gray tables cooperatively: each thread writes a stripe of words. */
    for (int g = 0; g < ngroups; g++) {
        int k = npiv - 8 * g < 8 ? npiv - 8 * g : 8;
        int ns = 1 << k;
        uint64_t *Tg = T + (int64_t)g * 256 * (int64_t)ch;
        for (int64_t x = tid; x < ch; x += nt)
            Tg[x] = 0;
        __syncthreads();
        for (int s2 = 1; s2 < ns; s2++) {
            int lb = __ffs(s2) - 1;
            const uint64_t *src = Tg + (int64_t)(s2 & (s2 - 1)) * (int64_t)ch;
            const uint64_t *bi = Bs + (int64_t)(8 * g + lb) * (int64_t)tail + x0;
            uint64_t *dst = Tg + (int64_t)s2 * (int64_t)ch;
            for (int64_t x = tid; x < ch; x += nt)
                dst[x] = src[x] ^ bi[x];
            __syncthreads();
        }
    }

    for (int64_t a = tid; a < nr; a += nt) {
        const uint64_t *cf = cfs + (int64_t)a * cw;
        uint64_t *row = M + (int64_t)rows[a] * W + w0 + x0;
        const uint64_t *tptr[64];
        int ntp = 0;
        for (int g = 0; g < ngroups; g++) {
            int s2 = (int)((cf[g >> 3] >> (8 * (g & 7))) & 0xFF);
            if (s2)
                tptr[ntp++] = T + ((int64_t)g * 256 + (int64_t)s2) * (int64_t)ch;
        }
        int j = 0;
        for (; j + 4 <= ntp; j += 4) {
            const uint64_t *a0 = tptr[j], *a1 = tptr[j + 1],
                           *a2 = tptr[j + 2], *a3 = tptr[j + 3];
            for (int64_t x = 0; x < ch; x++)
                row[x] ^= a0[x] ^ a1[x] ^ a2[x] ^ a3[x];
        }
        for (; j + 2 <= ntp; j += 2) {
            const uint64_t *a0 = tptr[j], *a1 = tptr[j + 1];
            for (int64_t x = 0; x < ch; x++)
                row[x] ^= a0[x] ^ a1[x];
        }
        if (j < ntp) {
            const uint64_t *a0 = tptr[j];
            for (int64_t x = 0; x < ch; x++)
                row[x] ^= a0[x];
        }
    }
}
