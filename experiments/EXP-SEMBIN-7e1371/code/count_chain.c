/* count_chain.c -- exact |V(I)| for the chained eq. (5) system at any t >= 2,
 * by enumeration, with no Groebner engine involved.
 *
 * The degree-4 certificate's verdict is "sufficient iff the closure's standard
 * monomial count equals |V(I)|".  Without |V(I)| the verdict is undetermined,
 * and on this host no F4 run completes at the larger cells -- so the boundary
 * the experiment is looking for would be invisible for want of a denominator,
 * not for want of a certificate.  This supplies it.
 *
 * The chain is
 *     S_3(u_1, x_1, x_2) = 0,
 *     S_3(u_i, u_{i+1}, x_{i+2}) = 0   (1 <= i <= t-3),
 *     S_3(u_{t-2}, x_t, z) = 0,
 * and every one of those equations is F_2-AFFINE in whichever single unknown is
 * solved for, because
 *     S_3(a,b,c) = a^2 b^2 + a^2 c^2 + b^2 c^2 + a b c + B
 * is, in each variable separately, a sum of a square times a constant, that
 * variable times a constant, and a constant -- and u -> u^2 and u -> cu are both
 * F_2-linear on F_{2^n}.  So the count walks the chain:
 *
 *   for (x_1, x_2) in V^2:            solve for u_1 in F_{2^n}   (n x n solve)
 *     for x_3 in V:                   solve for u_2 in F_{2^n}   (n x n solve)
 *       ...
 *         for x_t in V: the last equation is one n x k solve, counted directly.
 *
 * Cost is about |V|^{t-1} field-linear solves: seconds at the cells this
 * experiment declares.  Every solution of every intermediate solve is
 * enumerated (the affine solve returns a particular solution and a kernel
 * basis), so the count is exact, not a sample.
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

static uint64_t sq(uint64_t a) { return gfmul(a, a); }

/* Solve sum_j x_j * col[j] = rhs over F_2 (cols are n-bit field elements).
 * Returns rank, writes a particular solution's coefficient vector to *part and
 * the kernel basis coefficient vectors to kern[]; returns -1 if inconsistent. */
static int affine_solve(const uint64_t *col, int ncol, uint64_t rhs,
                        uint64_t *part, uint64_t *kern, int *nkern) {
    uint64_t bas[64], tag[64];
    memset(bas, 0, sizeof(bas));
    memset(tag, 0, sizeof(tag));
    int rank = 0;
    uint64_t used = 0;
    for (int j = 0; j < ncol; j++) {
        uint64_t v = col[j], tg = 1ULL << j;
        while (v) {
            int r = __builtin_ctzll(v);
            if (!bas[r]) { bas[r] = v; tag[r] = tg; rank++; used |= 1ULL << j; break; }
            v ^= bas[r]; tg ^= tag[r];
        }
        if (!v && col[j]) {
            /* col[j] is dependent: tg is a kernel vector (tg includes bit j) */
            kern[(*nkern)++] = tg;
        } else if (!col[j]) {
            kern[(*nkern)++] = 1ULL << j;   /* zero column: free variable */
        }
    }
    uint64_t v = rhs, tg = 0;
    while (v) {
        int r = __builtin_ctzll(v);
        if (!bas[r]) return -1;
        v ^= bas[r]; tg ^= tag[r];
    }
    *part = tg;
    return rank;
}

/* context for one cell */
typedef struct {
    int n, t, k;
    uint64_t z, B;
    const uint64_t *V;      /* 2^k elements of V */
    const uint64_t *basis;  /* k field elements spanning V */
    long nV;
    uint64_t fld[64];       /* F_2 basis of F_{2^n}: 1, a, a^2, ... as bit masks */
    long long total;
    long long kernel_overflow;
} ctx_t;

static uint64_t combo(const uint64_t *bas, uint64_t mask, int nb) {
    uint64_t r = 0;
    for (int i = 0; i < nb; i++) if ((mask >> i) & 1) r ^= bas[i];
    return r;
}

/* Solve S_3(a, Y, c) = 0 for Y in the span of gen[0..ng-1] (field elements).
 * S_3(a,Y,c) = Y^2 (a^2 + c^2) + Y (a c) + (a^2 c^2 + B).
 * Calls back with each solution, or counts them if cb_count is non-NULL. */
static void solve_middle(ctx_t *C, uint64_t a, uint64_t c, const uint64_t *gen, int ng,
                         uint64_t *sols, int *nsol, int max_sol) {
    uint64_t A = sq(a) ^ sq(c), Bc = gfmul(a, c);
    uint64_t rhs = gfmul(sq(a), sq(c)) ^ C->B;
    uint64_t col[64], kern[64], part;
    int nk = 0;
    for (int j = 0; j < ng; j++) col[j] = gfmul(sq(gen[j]), A) ^ gfmul(gen[j], Bc);
    int rank = affine_solve(col, ng, rhs, &part, kern, &nk);
    *nsol = 0;
    if (rank < 0) return;
    if (nk > 20) { C->kernel_overflow++; return; }
    long lim = 1L << nk;
    for (long s = 0; s < lim; s++) {
        uint64_t coef = part;
        for (int i = 0; i < nk; i++) if ((s >> i) & 1) coef ^= kern[i];
        if (*nsol < max_sol) sols[(*nsol)++] = combo(gen, coef, ng);
    }
}

static void recurse(ctx_t *C, int level, uint64_t u_prev) {
    /* level counts how many u's are fixed: u_1 .. u_level are known, u_level = u_prev */
    if (level == C->t - 2) {
        /* last equation: S_3(u_{t-2}, x_t, z) = 0 with x_t in V */
        uint64_t sols[4096];
        int ns = 0;
        solve_middle(C, u_prev, C->z, C->basis, C->k, sols, &ns, 4096);
        C->total += ns;
        return;
    }
    /* middle equation: S_3(u_level, u_{level+1}, x_{level+2}) = 0 */
    for (long xi = 0; xi < C->nV; xi++) {
        uint64_t x = C->V[xi];
        uint64_t sols[4096];
        int ns = 0;
        solve_middle(C, u_prev, x, C->fld, C->n, sols, &ns, 4096);
        for (int s = 0; s < ns; s++) recurse(C, level + 1, sols[s]);
    }
}

/* basis: k field elements spanning V; Vlist: the 2^k elements of V, with
 * Vlist[0] = 0 and Vlist[1 << j] = basis[j] (the caller builds it). */
long long count_chain(int n, uint64_t modulus, int t, int k,
                      const uint64_t *basis, const uint64_t *Vlist, long nV,
                      uint64_t z, uint64_t B, long long *kernel_overflow) {
    NBITS = n;
    MODP = modulus;
    ctx_t C;
    memset(&C, 0, sizeof(C));
    C.n = n; C.t = t; C.k = k; C.z = z; C.B = B; C.V = Vlist; C.nV = nV; C.basis = basis;
    for (int j = 0; j < n; j++) C.fld[j] = 1ULL << j;   /* 1, a, a^2, ... */
    /* note: V is passed as a list; the generator basis for a "solve for x in V"
     * step is basis[0..k-1], which the caller guarantees equals Vlist[1<<j]. */
    if (t == 2) {
        /* S_3(x_1, x_2, z) = 0 with both in V: one outer loop, one k-column solve */
        for (long i = 0; i < nV; i++) {
            uint64_t sols[4096];
            int ns = 0;
            solve_middle(&C, Vlist[i], z, basis, k, sols, &ns, 4096);
            C.total += ns;
        }
        if (kernel_overflow) *kernel_overflow = C.kernel_overflow;
        return C.total;
    }
    for (long i = 0; i < nV; i++) {
        for (long j = 0; j < nV; j++) {
            /* S_3(u_1, x_1, x_2) = 0, solve for u_1 in F_{2^n} */
            uint64_t sols[4096];
            int ns = 0;
            solve_middle(&C, Vlist[i], Vlist[j], C.fld, n, sols, &ns, 4096);
            for (int s = 0; s < ns; s++) recurse(&C, 1, sols[s]);
        }
    }
    if (kernel_overflow) *kernel_overflow = C.kernel_overflow;
    return C.total;
}
