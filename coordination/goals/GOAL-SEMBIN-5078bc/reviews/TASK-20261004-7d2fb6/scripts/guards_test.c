// guards_test.c -- joint W5 (5): exhaustive unit checks of closure.c's column layout and enumerators, by #include-ing the UNMODIFIED source
// (a copy of the git blob) so its static functions are reachable. For every N tested and D = 4 (and 7, the largest D the arrays allow):
//   * ncols == sum_{d<=D} C(N,d); every block d has exactly C(N,d) masks, each of popcount d, strictly ascending (so no duplicates);
//   * the column order equals the statement's ORDER, checked pairwise on consecutive columns with an independent comparator;
//   * col_of2(col_mask_[j]) == j for every j; col_of2 of a mask of popcount > D is -1; col_of2 of an absent equal-size mask (outside 2^N) is -1;
//   * gen_masks_deg(N, d, .) agrees with an independent recursive enumeration for d <= 4 at N <= 28;
//   * write_product: mu*poly agrees with a reference (sorted set of unions, mod 2) on random inputs, dropped_terms_ stays 0 when |mu| <= D - deg.
#include "closure_orig.c"
#include <assert.h>
static int larger(u64 a, u64 b) {            // statement ORDER: a > b
    int sa = popc(a), sb = popc(b); if (sa != sb) return sa > sb;
    u64 x = a ^ b; if (!x) return 0; int hb = 63 - __builtin_clzll(x); return (b >> hb) & 1;
}
static long binom(int n, int k) { long c = 1; for (int i = 0; i < k; i++) c = c * (n - i) / (i + 1); return c; }
static void rec(int N, int start, int left, u64 cur, u64 *out, long *cnt) {
    if (left == 0) { out[(*cnt)++] = cur; return; }
    for (int v = start; v < N; v++) rec(N, v + 1, left - 1, cur | (1ULL << v), out, cnt);
}
static int cmpu(const void *a, const void *b) { u64 x = *(u64*)a, y = *(u64*)b; return x < y ? -1 : x > y; }
int main(void) {
    int Ns[] = {8, 12, 22, 28, 40, 44, 46, 50, 62}; int fails = 0;
    for (int D = 4; D <= 7; D += 3) for (unsigned q = 0; q < sizeof Ns / sizeof *Ns; q++) {
        int N = Ns[q]; if (D == 7 && N > 28) continue;
        setup_columns(N, D);
        long tot = 0; for (int d = 0; d <= D; d++) tot += binom(N, d);
        int ok = (ncols_ == tot);
        for (int d = 0; d <= D && ok; d++) {
            long s = blk_start(d), e = blk_end(d);
            if (e - s != binom(N, d)) { ok = 0; break; }
            for (long j = s; j < e; j++) {
                if (popc(col_mask_[j]) != d) { ok = 0; break; }
                if (col_mask_[j] >> N) { ok = 0; break; }
                if (j > s && !(col_mask_[j - 1] < col_mask_[j])) { ok = 0; break; }
            }
        }
        for (long j = 1; j < ncols_ && ok; j++) if (!larger(col_mask_[j - 1], col_mask_[j])) ok = 0;   // strictly descending in the statement's ORDER
        for (long j = 0; j < ncols_ && ok; j += (N > 30 ? 1 : 1)) if (col_of2(col_mask_[j]) != j) ok = 0;
        if (ok) { u64 big = (1ULL << (D + 1)) - 1; if (col_of2(big) != -1) ok = 0; if (N < 63 && col_of2(1ULL << N) != -1) ok = 0; }   // popcount D+1 ; a mask outside the N variables
        if (ok && N <= 28 && D == 4) {
            for (int d = 0; d <= 4; d++) {
                long c1 = binom(N, d); u64 *a = malloc(8 * (c1 ? c1 : 1)), *b = malloc(8 * (c1 ? c1 : 1)); long c2 = 0;
                long g = gen_masks_deg(N, d, a); rec(N, 0, d, 0, b, &c2); qsort(b, c2, 8, cmpu);
                if (g != c1 || c2 != c1 || memcmp(a, b, 8 * c1)) ok = 0;
                free(a); free(b);
            }
        }
        printf("N=%2d D=%d ncols=%ld  columns/order/col_of2/enumerators: %s\n", N, D, ncols_, ok ? "PASS" : "FAIL");
        fails += !ok;
        free(col_mask_); col_mask_ = NULL; free(deg_off_); deg_off_ = NULL;
    }
    // write_product against a reference, N = 20, D = 4
    setup_columns(20, 4); srand(12345); dropped_terms_ = 0; int wp_ok = 1;
    u64 *tmp = malloc(8 * (ncols_ + 1));
    for (int trial = 0; trial < 300 && wp_ok; trial++) {
        int dg = 1 + rand() % 3; int cnt = 1 + rand() % 40; u64 masks[64];
        for (int i = 0; i < cnt; i++) { u64 m = 0; int sz = rand() % (dg + 1); while (popc(m) < sz) m |= 1ULL << (rand() % 20); masks[i] = m; }
        // make sure poly_deg == dg is not required: use the actual degree
        int pd = poly_deg(masks, cnt); int msz = rand() % (4 - pd + 1); u64 mu = 0; while (popc(mu) < msz) mu |= 1ULL << (rand() % 20);
        mzd_t *M = mzd_init(1, ncols_); write_product(M, 0, masks, cnt, mu, tmp);
        // reference: multiset of unions, parity
        u64 u[64]; for (int i = 0; i < cnt; i++) u[i] = masks[i] | mu; qsort(u, cnt, 8, cmpu);
        long ref = 0; u64 refm[64]; for (int i = 0; i < cnt;) { int j = i; while (j < cnt && u[j] == u[i]) j++; if ((j - i) & 1) refm[ref++] = u[i]; i = j; }
        u64 *got = malloc(8 * ncols_); long gc = row_masks(M, 0, got); qsort(got, gc, 8, cmpu);
        if (gc != ref || memcmp(got, refm, 8 * ref)) wp_ok = 0;
        free(got); mzd_free(M);
    }
    printf("write_product vs reference (300 random trials, |mu| + deg <= D): %s ; dropped_terms_ = %lld (must be 0)\n", wp_ok && dropped_terms_ == 0 ? "PASS" : "FAIL", dropped_terms_);
    fails += !(wp_ok && dropped_terms_ == 0);
    printf("TOTAL FAILS: %d\n", fails);
    return fails != 0;
}
