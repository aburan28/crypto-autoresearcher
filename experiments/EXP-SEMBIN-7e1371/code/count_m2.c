/* count_m2.c -- exact solution count for the m = t = 2 systems of this
 * experiment, by exhaustive enumeration of V, not by any Groebner engine.
 *
 * The degree-4 certificate's verdict is "sufficient iff #standard monomials of
 * the degree-capped closure equals |V(I)|".  At the m = 2 window (n = 40..45)
 * |V(I)| cannot be read off an F4 run that does not finish, so without an
 * independent count the verdict is undetermined at exactly the cells the
 * experiment is about.  This supplies the count directly:
 *
 *   S_3(x1, x2, z) = (x1 x2)^2 + z^2 (x1 + x2)^2 + z (x1 x2) + B
 *
 * is F_2-LINEAR in x2 for fixed x1 (squaring and multiplication by a constant
 * are both F_2-linear on F_{2^n}), so
 *
 *   |V(I)| = sum over x1 in V of #{ x2 in V : L_{x1}(x2) = c(x1) },
 *
 * and each inner count is 2^(k - rank) or 0 from one k-column F_2 solve.  The
 * columns of L_{x1} are themselves F_2-affine in x1, so the enumeration walks V
 * in Gray-code order and pays one XOR per column per step.  Cost is
 * 2^k * O(k^2) word operations -- seconds at k = 23, against the 111-126 GB the
 * literature reports for a Groebner run at the same cells.
 *
 * This counts the Boolean system's zeros exactly, by definition of the descent:
 * the N = 2k Boolean variables parametrise (x1, x2) in V x V bijectively and
 * the n descended equations vanish together iff S_3(x1, x2, z) = 0 in F_{2^n}.
 */
#include <stdint.h>
#include <string.h>

static int NBITS;
static uint64_t MODP;

static uint64_t gfmul(uint64_t a, uint64_t b) {
    uint64_t r = 0;
    for (int i = 0; i < NBITS; i++) {
        if ((b >> i) & 1) r ^= a;
        a <<= 1;
        if ((a >> NBITS) & 1) a ^= MODP;
    }
    return r;
}

/* Exact |V(I)| for S_3(x1,x2,z) = 0 with x1,x2 in the span of basis[0..k-1].
 * Returns the count; *pairs_consistent receives the number of x1 with a
 * solvable inner system, *max_inner the largest inner solution count seen. */
long long count_m2(int n, uint64_t modulus, int k, const uint64_t *basis,
                   uint64_t z, uint64_t B,
                   long long *pairs_consistent, long long *max_inner) {
    NBITS = n;
    MODP = modulus;
    uint64_t z2 = gfmul(z, z);
    uint64_t colc[64], cD[64], D[64][64], col[64], bas[64];
    for (int j = 0; j < k; j++) {
        uint64_t vj = basis[j];
        colc[j] = gfmul(z2, gfmul(vj, vj));
        cD[j] = gfmul(z2, gfmul(vj, vj));
        for (int i = 0; i < k; i++) {
            uint64_t p = gfmul(basis[i], vj);
            D[i][j] = gfmul(p, p) ^ gfmul(z, p);
        }
    }
    for (int j = 0; j < k; j++) col[j] = colc[j];
    uint64_t cvec = B;
    long long total = 0, consistent = 0, mx = 0;
    unsigned long long limit = 1ULL << k;
    for (unsigned long long g = 0; g < limit; g++) {
        if (g) {
            int i = __builtin_ctzll(g);      /* Gray code: toggle basis vector i */
            for (int j = 0; j < k; j++) col[j] ^= D[i][j];
            cvec ^= cD[i];
        }
        memset(bas, 0, sizeof(uint64_t) * (size_t)(n + 1));
        int rank = 0;
        for (int j = 0; j < k; j++) {
            uint64_t v = col[j];
            while (v) {
                int r = __builtin_ctzll(v);
                if (!bas[r]) { bas[r] = v; rank++; break; }
                v ^= bas[r];
            }
        }
        uint64_t v = cvec;
        while (v) {
            int r = __builtin_ctzll(v);
            if (!bas[r]) break;
            v ^= bas[r];
        }
        if (v == 0) {
            long long inner = 1LL << (k - rank);
            total += inner;
            consistent++;
            if (inner > mx) mx = inner;
        }
    }
    if (pairs_consistent) *pairs_consistent = consistent;
    if (max_inner) *max_inner = mx;
    return total;
}

/* Direct O(2^{2k}) reference count, for validating count_m2 at small k. */
long long count_m2_reference(int n, uint64_t modulus, int k, const uint64_t *basis,
                             uint64_t z, uint64_t B) {
    NBITS = n;
    MODP = modulus;
    uint64_t z2 = gfmul(z, z);
    long long total = 0;
    unsigned long long limit = 1ULL << k;
    for (unsigned long long a = 0; a < limit; a++) {
        uint64_t x1 = 0;
        for (int i = 0; i < k; i++) if ((a >> i) & 1) x1 ^= basis[i];
        for (unsigned long long b = 0; b < limit; b++) {
            uint64_t x2 = 0;
            for (int i = 0; i < k; i++) if ((b >> i) & 1) x2 ^= basis[i];
            uint64_t p = gfmul(x1, x2), s = x1 ^ x2;
            uint64_t val = gfmul(p, p) ^ gfmul(z2, gfmul(s, s)) ^ gfmul(z, p) ^ B;
            if (val == 0) total++;
        }
    }
    return total;
}
