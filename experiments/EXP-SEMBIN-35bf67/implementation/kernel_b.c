/* EXP-SEMBIN-35bf67 rank arm B: executor-written GF(2) kernels, no M4RI code.
 *  - k_muladd: four-Russians product with four 8-bit Gray tables (32 rows of B per pass),
 *              column-blocked so the tables stay cache resident.
 *  - k_rref  : plain Gauss-Jordan elimination, leftmost pivot by word scan.
 */
#include "kernel.h"
#include <stdlib.h>
#include <string.h>

#ifndef NBW
#define NBW 32 /* column block in words (2048 columns) */
#endif

static word *tab = NULL; /* 4 tables x 256 entries x NBW words */

static void build_table(word *T, const word *B, size_t Bs, int j0, int kk, int cb, int bw) {
  memset(T, 0, (size_t)bw * sizeof(word));
  for (int i = 1; i < (1 << kk); i++) {
    int low = __builtin_ctz(i);
    const word *src = T + (size_t)(i & (i - 1)) * NBW;
    const word *br = B + (size_t)(j0 + low) * Bs + cb;
    word *dst = T + (size_t)i * NBW;
    for (int w = 0; w < bw; w++) dst[w] = src[w] ^ br[w];
  }
}

void k_muladd(word *C, size_t Cs, int m, int n, const word *A, size_t As, int kd,
              const word *B, size_t Bs) {
  if (m == 0 || n == 0 || kd == 0) return;
  if (!tab) tab = (word *)aligned_alloc(64, sizeof(word) * 4 * 256 * NBW);
  int nw = (n + 63) / 64;
  for (int cb = 0; cb < nw; cb += NBW) {
    int bw = nw - cb < NBW ? nw - cb : NBW;
    for (int j0 = 0; j0 < kd; j0 += 32) {
      int nt = 0, kks[4];
      for (int t = 0; t < 4 && j0 + 8 * t < kd; t++) {
        int kk = kd - (j0 + 8 * t);
        if (kk > 8) kk = 8;
        kks[t] = kk;
        build_table(tab + (size_t)t * 256 * NBW, B, Bs, j0 + 8 * t, kk, cb, bw);
        nt++;
      }
      int wi = j0 >> 6, sh = j0 & 63; /* j0 multiple of 32: 32 bits within one word */
      const word *T0 = tab, *T1 = tab + 256 * NBW, *T2 = tab + 512 * NBW, *T3 = tab + 768 * NBW;
      for (int r = 0; r < m; r++) {
        word a = A[(size_t)r * As + wi] >> sh;
        unsigned b0 = a & 0xff, b1 = (a >> 8) & 0xff, b2 = (a >> 16) & 0xff, b3 = (a >> 24) & 0xff;
        if (nt < 4) { b3 = 0; if (nt < 3) { b2 = 0; if (nt < 2) b1 = 0; } }
        /* bits beyond kd in A are zero by contract, so masked bytes index valid entries */
        (void)kks;
        if (!(b0 | b1 | b2 | b3)) continue;
        word *c = C + (size_t)r * Cs + cb;
        const word *t0 = T0 + (size_t)b0 * NBW, *t1 = T1 + (size_t)b1 * NBW;
        const word *t2 = T2 + (size_t)b2 * NBW, *t3 = T3 + (size_t)b3 * NBW;
        for (int w = 0; w < bw; w++) c[w] ^= t0[w] ^ t1[w] ^ t2[w] ^ t3[w];
      }
    }
  }
}

int k_rref(word *X, size_t Xs, int m, int n, int *piv) {
  int nw = (n + 63) / 64;
  int cur = 0;
  word *tmp = (word *)malloc(sizeof(word) * Xs);
  for (int w = 0; w < nw && cur < m; w++) {
    for (;;) {
      word orv = 0;
      for (int i = cur; i < m; i++) orv |= X[(size_t)i * Xs + w];
      if (!orv) break;
      int b = __builtin_ctzll(orv);
      word bit = (word)1 << b;
      int pr = -1;
      for (int i = cur; i < m; i++)
        if (X[(size_t)i * Xs + w] & bit) { pr = i; break; }
      if (pr != cur) {
        memcpy(tmp, X + (size_t)pr * Xs, sizeof(word) * Xs);
        memcpy(X + (size_t)pr * Xs, X + (size_t)cur * Xs, sizeof(word) * Xs);
        memcpy(X + (size_t)cur * Xs, tmp, sizeof(word) * Xs);
      }
      const word *p = X + (size_t)cur * Xs;
      for (int i = 0; i < m; i++) {
        if (i == cur) continue;
        word *q = X + (size_t)i * Xs;
        if (q[w] & bit)
          for (int v = w; v < nw; v++) q[v] ^= p[v];
      }
      piv[cur] = w * 64 + b;
      cur++;
      if (cur == m) break;
    }
  }
  free(tmp);
  return cur;
}

const char *k_name(void) { return "B:executor-c(gray4x8-m4rm,gauss-jordan)"; }
