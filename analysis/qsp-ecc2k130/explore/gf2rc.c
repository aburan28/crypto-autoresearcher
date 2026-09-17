/* gf2rc: number of distinct roots in F_{2^n} of L(X) = X^{2^np} + lam(X),
 * lam in F_2[X] with deg lam < 2^np, computed as deg gcd(L, X^{2^n} - X).
 * Input lines on stdin:  n np lam_hex   (lam_hex = big-endian hex of the bit-packed lam)
 * Output lines:          n np lam_hex count
 * Word-level GF(2)[X] arithmetic; polynomials up to 2^np <= 2^22 bits.
 * Written for analysis/qsp-ecc2k130/explore (2026-09-17); no dependencies.  */
#define _POSIX_C_SOURCE 200809L   /* getline */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint64_t u64;
static u64 spread16[256];

static void init_spread(void) {
    for (int b = 0; b < 256; b++) { u64 r = 0; for (int i = 0; i < 8; i++) if (b >> i & 1) r |= 1ULL << (2 * i); spread16[b] = r; }
}
static int degree(const u64 *a, int nw) { for (int i = nw - 1; i >= 0; i--) if (a[i]) return 64 * i + 63 - __builtin_clzll(a[i]); return -1; }
static void clear(u64 *a, int nw) { memset(a, 0, nw * sizeof(u64)); }
/* r = a^2 (a has nw words, r has 2*nw words) */
static void square(const u64 *a, u64 *r, int nw) {
    clear(r, 2 * nw);
    for (int i = 0; i < nw; i++) {
        u64 w = a[i], lo = 0, hi = 0;
        for (int b = 0; b < 4; b++) lo |= spread16[(w >> (8 * b)) & 0xff] << (16 * b);
        for (int b = 4; b < 8; b++) hi |= spread16[(w >> (8 * b)) & 0xff] << (16 * (b - 4));
        r[2 * i] = lo; r[2 * i + 1] = hi;
    }
}
/* a ^= b << s  (b has nb words; a large enough) */
static void xor_shift(u64 *a, const u64 *b, int nb, long s) {
    long ws = s / 64; int bs = s % 64;
    for (int i = nb - 1; i >= 0; i--) {
        u64 v = b[i]; if (!v) continue;
        a[i + ws] ^= v << bs;
        if (bs) a[i + ws + 1] ^= v >> (64 - bs);
    }
}
/* reduce a (2*nw words, degree < 2^(np+1)) modulo X^{2^np} + lam, lam given by exponent list */
static void reduce_sparse(u64 *a, int nw, long np2, const long *lexp, int nl) {
    /* while deg a >= np2: take high = a >> np2, a = low ^ high*lam.  high*lam = XOR of high << e. */
    int total = 2 * nw;
    for (;;) {
        int d = degree(a, total);
        if (d < np2) return;
        /* extract high part into tmp */
        int hw = (d - np2) / 64 + 1;
        u64 *high = calloc(hw + 1, sizeof(u64));
        long ws = np2 / 64; int bs = np2 % 64;
        for (int i = 0; i < hw; i++) {
            u64 v = a[i + ws] >> bs;
            if (bs && i + ws + 1 < total) v |= a[i + ws + 1] << (64 - bs);
            high[i] = v;
        }
        /* clear bits >= np2 in a */
        for (int i = ws + 1; i < total; i++) a[i] = 0;
        a[ws] &= (bs ? ((1ULL << bs) - 1) : 0);
        if (!bs) a[ws] = 0;
        for (int k = 0; k < nl; k++) xor_shift(a, high, hw, lexp[k]);
        free(high);
    }
}
/* gcd degree of a (deg < 2^np, nw words) and L = X^{2^np} + lam.  Euclid: first reduce L mod a. */
static int gcd_degree(u64 *L, u64 *a, int nwL) {
    /* generic Euclid on (L, a) with word ops; nwL words each */
    u64 *x = L, *y = a;
    for (;;) {
        int dy = degree(y, nwL);
        if (dy < 0) return degree(x, nwL);
        int dx = degree(x, nwL);
        while (dx >= dy) {
            long s = dx - dy; long ws = s / 64; int bs = s % 64;
            int yw = dy / 64 + 1;
            for (int i = yw - 1; i >= 0; i--) {
                u64 v = y[i]; if (!v) continue;
                x[i + ws] ^= v << bs;
                if (bs && i + ws + 1 < nwL) x[i + ws + 1] ^= v >> (64 - bs);
            }
            dx = degree(x, nwL);
        }
        u64 *t = x; x = y; y = t;
    }
}
int main(void) {
    init_spread();
    char *line = NULL; size_t cap = 0;
    while (getline(&line, &cap, stdin) > 0) {
        int n, np, off = 0;
        if (sscanf(line, "%d %d %n", &n, &np, &off) != 2 || off == 0) continue;
        char *hex = line + off;           /* lam_hex may be up to 2^22 / 4 digits: never a fixed buffer */
        hex[strcspn(hex, " \t\r\n")] = 0;
        if (!*hex) continue;
        long np2 = 1L << np;
        int nw = np2 / 64 + 1;
        /* parse lam */
        long lexp[64]; int nl = 0;
        int len = strlen(hex);
        for (int i = 0; i < len; i++) {
            int c = hex[len - 1 - i]; int v = (c >= 'a') ? c - 'a' + 10 : (c >= 'A') ? c - 'A' + 10 : c - '0';
            for (int b = 0; b < 4; b++) if (v >> b & 1) { if (nl < 64) lexp[nl++] = 4L * i + b; }
        }
        int bad = 0;
        for (int k = 0; k < nl; k++) if (lexp[k] >= np2) bad = 1;
        if (bad) { printf("%d %d %s -1\n", n, np, hex); fflush(stdout); continue; }   /* deg lam must be < 2^np */
        u64 *x = calloc(2 * nw + 2, sizeof(u64)), *tmp = calloc(2 * nw + 2, sizeof(u64));
        x[0] = 2; /* X */
        for (int k = 0; k < n; k++) {
            square(x, tmp, nw);
            reduce_sparse(tmp, nw, np2, lexp, nl);
            memcpy(x, tmp, nw * sizeof(u64));
            for (int i = nw; i < 2 * nw + 2; i++) x[i] = 0;
        }
        x[0] ^= 2; /* h = X^{2^n} - X mod L */
        u64 *L = calloc(2 * nw + 2, sizeof(u64));
        L[np2 / 64] |= 1ULL << (np2 % 64);
        for (int k = 0; k < nl; k++) L[lexp[k] / 64] ^= 1ULL << (lexp[k] % 64);
        int cnt;
        if (degree(x, nw) < 0) cnt = np2; else cnt = gcd_degree(L, x, nw + 1);
        printf("%d %d %s %d\n", n, np, hex, cnt);
        fflush(stdout);
        free(x); free(tmp); free(L);
    }
    free(line);
    return 0;
}
