/* I1: Bareiss determinant of the Sylvester matrix over F_2[X].
 * Independent of I2 (Newton interpolation over F_{2^n}).
 * Input (stdin):
 *   ncoeff_f
 *   hex_coeff_0 ...  (one F_2[X] Y-coefficient per line, bitpacked hex, low degree first)
 *   ncoeff_g
 *   hex_coeff_0 ...
 * Output (stdout):
 *   deg <d_or_-1>
 *   zero <0|1>
 *   poly <hex>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

#define MAXW 96
#define MAXN 32

typedef struct { uint64_t w[MAXW]; } Poly;

static int pdeg(const Poly *a) {
    for (int i = MAXW - 1; i >= 0; i--) {
        if (a->w[i]) return 64 * i + 63 - __builtin_clzll(a->w[i]);
    }
    return -1;
}

static int pis0(const Poly *a) {
    for (int i = 0; i < MAXW; i++) if (a->w[i]) return 0;
    return 1;
}

static void pzero(Poly *a) { memset(a->w, 0, sizeof(a->w)); }

static void pcpy(Poly *d, const Poly *s) { memcpy(d->w, s->w, sizeof(d->w)); }

static void pxor(Poly *a, const Poly *b) {
    for (int i = 0; i < MAXW; i++) a->w[i] ^= b->w[i];
}

static void pshl_xor(Poly *a, const Poly *b, int s) {
    int ws = s / 64, bs = s % 64;
    for (int i = MAXW - 1; i >= 0; i--) {
        uint64_t v = b->w[i];
        if (!v) continue;
        int t = i + ws;
        if (t < MAXW) a->w[t] ^= v << bs;
        if (bs && t + 1 < MAXW) a->w[t + 1] ^= v >> (64 - bs);
    }
}

static void pmul(const Poly *a, const Poly *b, Poly *r) {
    pzero(r);
    int da = pdeg(a), db = pdeg(b);
    if (da < 0 || db < 0) return;
    if (da + db >= MAXW * 64) {
        fprintf(stderr, "poly overflow mul deg %d+%d\n", da, db);
        exit(2);
    }
    for (int i = 0; i < MAXW; i++) {
        uint64_t aw = a->w[i];
        if (!aw) continue;
        for (int bit = 0; bit < 64; bit++) {
            if ((aw >> bit) & 1ULL) pshl_xor(r, b, 64 * i + bit);
        }
    }
}

static void pdivrem(const Poly *num, const Poly *den, Poly *q, Poly *rem) {
    pzero(q); pcpy(rem, num);
    int dd = pdeg(den);
    if (dd < 0) { fprintf(stderr, "div0\n"); exit(2); }
    int dr = pdeg(rem);
    while (dr >= dd) {
        int s = dr - dd;
        int ws = s / 64, bs = s % 64;
        if (ws < MAXW) q->w[ws] |= 1ULL << bs;
        pshl_xor(rem, den, s);
        dr = pdeg(rem);
    }
}

static int pexactdiv(const Poly *num, const Poly *den, Poly *q) {
    Poly rem;
    pdivrem(num, den, q, &rem);
    return pis0(&rem);
}

static void pfrom_u64(Poly *a, uint64_t lo) {
    pzero(a);
    a->w[0] = lo;
}

static int hexval(int c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static int parse_hex_poly(const char *s, Poly *a) {
    pzero(a);
    while (*s && isspace((unsigned char)*s)) s++;
    if (s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) s += 2;
    int n = (int)strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) n--;
    /* hex is big-endian (high nibble = high bits of the integer) */
    int bitpos = 0;
    for (int i = n - 1; i >= 0; i--) {
        int v = hexval(s[i]);
        if (v < 0) continue;
        for (int b = 0; b < 4; b++) {
            if (v & (1 << b)) {
                int p = bitpos + b;
                a->w[p / 64] |= 1ULL << (p % 64);
            }
        }
        bitpos += 4;
    }
    return 0;
}

static void print_hex_poly(const Poly *a) {
    int d = pdeg(a);
    if (d < 0) { printf("0"); return; }
    int nbits = d + 1;
    int nibbles = (nbits + 3) / 4;
    for (int ni = nibbles - 1; ni >= 0; ni--) {
        int v = 0;
        for (int b = 0; b < 4; b++) {
            int p = 4 * ni + b;
            if (a->w[p / 64] & (1ULL << (p % 64))) v |= 1 << b;
        }
        printf("%x", v);
    }
}

static Poly MAT[MAXN][MAXN];

int main(void) {
    int nf, ng;
    if (scanf("%d", &nf) != 1) return 1;
    Poly f[MAXN];
    for (int i = 0; i < nf; i++) {
        char buf[4096];
        if (scanf("%4095s", buf) != 1) return 1;
        parse_hex_poly(buf, &f[i]);
    }
    if (scanf("%d", &ng) != 1) return 1;
    Poly g[MAXN];
    for (int i = 0; i < ng; i++) {
        char buf[4096];
        if (scanf("%4095s", buf) != 1) return 1;
        parse_hex_poly(buf, &g[i]);
    }
    while (nf > 0 && pis0(&f[nf - 1])) nf--;
    while (ng > 0 && pis0(&g[ng - 1])) ng--;
    if (nf <= 0 || ng <= 0) {
        printf("deg -1\nzero 1\npoly 0\n");
        return 0;
    }
    int mf = nf - 1, mg = ng - 1;
    int N = mf + mg;
    if (N == 0) {
        /* both degree 0 */
        printf("deg %d\nzero 0\npoly ", pdeg(&g[0]));
        print_hex_poly(&g[0]);
        printf("\n");
        return 0;
    }
    if (N > MAXN) { fprintf(stderr, "N too big %d\n", N); return 2; }
    for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) pzero(&MAT[i][j]);
    for (int i = 0; i < mg; i++)
        for (int t = 0; t < nf; t++)
            pcpy(&MAT[i][i + t], &f[t]);
    for (int i = 0; i < mf; i++)
        for (int t = 0; t < ng; t++)
            pcpy(&MAT[mg + i][i + t], &g[t]);

    Poly prev, tmp, num, q;
    pfrom_u64(&prev, 1);
    for (int k = 0; k < N - 1; k++) {
        int piv = -1;
        for (int r = k; r < N; r++) {
            if (!pis0(&MAT[r][k])) { piv = r; break; }
        }
        if (piv < 0) {
            printf("deg -1\nzero 1\npoly 0\n");
            return 0;
        }
        if (piv != k) {
            for (int j = k; j < N; j++) {
                Poly sw = MAT[k][j];
                MAT[k][j] = MAT[piv][j];
                MAT[piv][j] = sw;
            }
        }
        for (int i = k + 1; i < N; i++) {
            for (int j = k + 1; j < N; j++) {
                pmul(&MAT[i][j], &MAT[k][k], &tmp);
                pmul(&MAT[i][k], &MAT[k][j], &num);
                pxor(&tmp, &num);
                if (!pexactdiv(&tmp, &prev, &q)) {
                    fprintf(stderr, "inexact Bareiss k=%d i=%d j=%d\n", k, i, j);
                    return 3;
                }
                pcpy(&MAT[i][j], &q);
            }
        }
        pcpy(&prev, &MAT[k][k]);
    }
    Poly *det = &MAT[N - 1][N - 1];
    if (pis0(det)) {
        printf("deg -1\nzero 1\npoly 0\n");
        return 0;
    }
    printf("deg %d\nzero 0\npoly ", pdeg(det));
    print_hex_poly(det);
    printf("\n");
    return 0;
}
