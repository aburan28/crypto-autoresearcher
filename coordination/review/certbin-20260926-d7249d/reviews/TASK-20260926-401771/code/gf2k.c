/*
 * gf2k.c -- TASK-20260926-401771 (J1 author-independent verifier) C kernels.
 *
 * Written from the specification text only (EXP-CERTBIN-060020 object,
 * certificate_format; EXP-CERTBIN-e94b27 object). No line is taken from, or
 * shaped by, any producer code base. Built by code/build.sh into a scratch
 * directory; loaded by code/kern.py via ctypes.
 *
 * Bit convention for packed GF(2) vectors: coordinate c lives in 64-bit word
 * c >> 6 at bit c & 63 (little-endian bit order, the ann-v1 "bit c (LSB first)"
 * convention).
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * F_{2^19} = F_2[t]/(t^19 + t^5 + t^2 + t + 1), element <-> 19-bit integer.
 * A second, independent implementation of the multiplication (the first is
 * gf19.py); descent route B uses only this one.
 * ------------------------------------------------------------------------- */
static const uint64_t MODPOLY = 524327ULL; /* t^19 + t^5 + t^2 + t + 1 */

static inline uint32_t gfmul(uint32_t a, uint32_t b) {
    uint64_t r = 0;
    for (int i = 0; i < 19; i++)
        if ((b >> i) & 1u) r ^= ((uint64_t)a) << i;
    for (int i = 36; i >= 19; i--)
        if ((r >> i) & 1ULL) r ^= MODPOLY << (i - 19);
    return (uint32_t)r;
}

uint32_t k_gfmul(uint32_t a, uint32_t b) { return gfmul(a, b); }

/* Direct evaluation of S_3(x_1, x_2, x_R) = (x1x2 + x1xR + x2xR)^2 + x1x2xR + B
 * at every assignment v in {0,1}^20 (v_j = bit j of the integer v):
 * x_1 = sum_{j<10} v_j t^j, x_2 = sum_{j<10} v_{10+j} t^j. out has 2^20 entries. */
void k_s3_eval_all(uint32_t xR, uint32_t B, uint32_t *out) {
    for (uint32_t v = 0; v < (1u << 20); v++) {
        uint32_t x1 = v & 0x3FFu, x2 = (v >> 10) & 0x3FFu;
        uint32_t p12 = gfmul(x1, x2);
        uint32_t s = p12 ^ gfmul(x1, xR) ^ gfmul(x2, xR);
        out[v] = gfmul(s, s) ^ gfmul(p12, xR) ^ B;
    }
}

/* In-place binary Moebius transform over n variables of a word array
 * (each of the 32 bit lanes transformed independently). It is an involution:
 * ANF coefficients <-> truth table. */
void k_mobius_u32(uint32_t *a, int n) {
    uint32_t N = 1u << n;
    for (int i = 0; i < n; i++) {
        uint32_t h = 1u << i;
        for (uint32_t base = 0; base < N; base += 2 * h)
            for (uint32_t x = base; x < base + h; x++)
                a[x + h] ^= a[x];
    }
}

/* ---------------------------------------------------------------------------
 * Gauss-Jordan reduction to RREF over GF(2) on packed rows.
 * M: rows x words. Pivots are searched only in columns [0, ncols); bits at
 * columns >= ncols (e.g. an augmented provenance block starting at a word
 * boundary) are carried along. Column order = pivot preference order.
 * After return, rows 0..rank-1 are the RREF rows, piv[r] their pivot columns
 * (strictly increasing); rows rank.. are zero in [0, ncols).
 * ------------------------------------------------------------------------- */
int k_rref(uint64_t *M, int rows, int words, int ncols, int32_t *piv) {
    int r = 0;
    uint64_t *tmp = (uint64_t *)malloc((size_t)words * 8);
    for (int c = 0; c < ncols && r < rows; c++) {
        int w = c >> 6;
        uint64_t b = 1ULL << (c & 63);
        int p = -1;
        for (int i = r; i < rows; i++)
            if (M[(size_t)i * words + w] & b) { p = i; break; }
        if (p < 0) continue;
        if (p != r) {
            memcpy(tmp, M + (size_t)p * words, (size_t)words * 8);
            memcpy(M + (size_t)p * words, M + (size_t)r * words, (size_t)words * 8);
            memcpy(M + (size_t)r * words, tmp, (size_t)words * 8);
        }
        const uint64_t *pr = M + (size_t)r * words;
        for (int i = 0; i < rows; i++) {
            if (i == r) continue;
            uint64_t *ri = M + (size_t)i * words;
            if (ri[w] & b)
                for (int k = w; k < words; k++) ri[k] ^= pr[k];
        }
        piv[r] = c;
        r++;
    }
    free(tmp);
    return r;
}

/* ---------------------------------------------------------------------------
 * Parity check: for every vector V[i] and functional L[l], lambda_l(V_i) =
 * parity(popcount(L_l AND V_i)). Returns the number of (i, l) pairs with odd
 * parity; writes the first such pair (i-major order) to first[0..1], and,
 * if bad_v != NULL, the number of odd functionals per vector.
 * ------------------------------------------------------------------------- */
long k_parity_check(const uint64_t *L, int nL, const uint64_t *V, int nV,
                    int words, int32_t *first, int32_t *bad_v) {
    long nbad = 0;
    first[0] = -1; first[1] = -1;
    for (int i = 0; i < nV; i++) {
        const uint64_t *v = V + (size_t)i * words;
        int cnt = 0;
        for (int l = 0; l < nL; l++) {
            const uint64_t *lam = L + (size_t)l * words;
            uint64_t acc = 0;
            for (int k = 0; k < words; k++) acc ^= (lam[k] & v[k]);
            if (__builtin_popcountll(acc) & 1) {
                cnt++;
                if (first[0] < 0) { first[0] = i; first[1] = l; }
            }
        }
        nbad += cnt;
        if (bad_v) bad_v[i] = cnt;
    }
    return nbad;
}

/* ---------------------------------------------------------------------------
 * Multiplication by v_j in coordinates of a fixed monomial order.
 * mask_of_col[c]: variable bitmask of coordinate c (ncols coordinates);
 * col_of_mask[m]: coordinate of mask m, or -1 if m is not a coordinate.
 * out = multilinear reduction of v_j * in (the monomial m maps to m | 1<<j,
 * contributions XOR-accumulated). Returns -1 if some product monomial has no
 * coordinate (degree overflow), else 0.
 * ------------------------------------------------------------------------- */
int k_mul_vj(const uint64_t *in, uint64_t *out, int words, int ncols, int j,
             const int32_t *mask_of_col, const int32_t *col_of_mask) {
    memset(out, 0, (size_t)words * 8);
    int err = 0;
    for (int c = 0; c < ncols; c++) {
        if ((in[c >> 6] >> (c & 63)) & 1ULL) {
            int32_t m = mask_of_col[c] | (1 << j);
            int32_t c2 = col_of_mask[m];
            if (c2 < 0) { err = -1; continue; }
            out[c2 >> 6] ^= 1ULL << (c2 & 63);
        }
    }
    return err;
}

/* (A2) kernel: for every basis vector K[a] (coordinates of the same order,
 * degree <= D-1 content) and every j in 0..nv-1, compute p = v_j * K[a] and
 * check lambda(p) = 0 for every lambda in L. Returns the number of violating
 * (a, j, l) triples; first[0..2] = first violation; overflow[0] counts
 * products that left the coordinate set. */
long k_closure_check(const uint64_t *L, int nL, const uint64_t *K, int nK,
                     int words, int ncols, int nv,
                     const int32_t *mask_of_col, const int32_t *col_of_mask,
                     int32_t *first, int32_t *overflow) {
    long nbad = 0;
    uint64_t *p = (uint64_t *)malloc((size_t)words * 8);
    first[0] = first[1] = first[2] = -1;
    overflow[0] = 0;
    for (int a = 0; a < nK; a++) {
        const uint64_t *k = K + (size_t)a * words;
        for (int j = 0; j < nv; j++) {
            if (k_mul_vj(k, p, words, ncols, j, mask_of_col, col_of_mask) < 0)
                overflow[0]++;
            for (int l = 0; l < nL; l++) {
                const uint64_t *lam = L + (size_t)l * words;
                uint64_t acc = 0;
                for (int w = 0; w < words; w++) acc ^= (lam[w] & p[w]);
                if (__builtin_popcountll(acc) & 1) {
                    nbad++;
                    if (first[0] < 0) { first[0] = a; first[1] = j; first[2] = l; }
                }
            }
        }
    }
    free(p);
    return nbad;
}

/* Reduce x against RREF rows R (rank rows, strictly increasing pivots).
 * Returns 1 if the remainder is nonzero. x is modified in place. */
int k_reduce(uint64_t *x, const uint64_t *R, int rank, int words, const int32_t *piv) {
    for (int r = 0; r < rank; r++) {
        int c = piv[r];
        if ((x[c >> 6] >> (c & 63)) & 1ULL) {
            const uint64_t *row = R + (size_t)r * words;
            for (int k = 0; k < words; k++) x[k] ^= row[k];
        }
    }
    for (int k = 0; k < words; k++) if (x[k]) return 1;
    return 0;
}

/* One mutant-closure step test: given the RREF (rank rows, pivots) of a space
 * W in the coordinate order (columns in descending degree, so a row whose
 * pivot column has degree <= D-1 lies entirely in B_{<=D-1}), multiply every
 * such row by every v_j and reduce against W. Returns the number of products
 * NOT in W (so 0 iff W^(1) = W^(0)). deg_of_col gives each column's degree.
 * If stop_first != 0, returns at the first product outside W. */
long k_step_outside(const uint64_t *R, int rank, int words, int ncols, int nv,
                    int Dm1, const int32_t *piv, const int32_t *deg_of_col,
                    const int32_t *mask_of_col, const int32_t *col_of_mask,
                    int stop_first, int32_t *first) {
    long nout = 0;
    uint64_t *p = (uint64_t *)malloc((size_t)words * 8);
    first[0] = first[1] = -1;
    for (int r = 0; r < rank; r++) {
        if (deg_of_col[piv[r]] > Dm1) continue;
        const uint64_t *b = R + (size_t)r * words;
        for (int j = 0; j < nv; j++) {
            k_mul_vj(b, p, words, ncols, j, mask_of_col, col_of_mask);
            if (k_reduce(p, R, rank, words, piv)) {
                nout++;
                if (first[0] < 0) { first[0] = r; first[1] = j; }
                if (stop_first) { free(p); return nout; }
            }
        }
    }
    free(p);
    return nout;
}
