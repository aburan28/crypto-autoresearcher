/* EXP-SEMBIN-79a02d -- E2: Boolean brute-force solution enumeration.
 * Bit-sliced: the 6 lowest variables span 64 lanes of a word; the remaining
 * N-6 variables are iterated. A monomial evaluates to lowtab[low part] when
 * its high part is contained in the current high assignment, else 0.
 *   enum_bool <gens>   -> JSON {"count":..,"solutions":[hex...]} (list capped at 4096)
 */
#include "gf2_common.h"
int main(int argc, char **argv) {
  if (argc < 2) return 1;
  int N; poly_t *P; int np = read_gens(argv[1], &N, &P);
  if (N < 6 || N > 40) { fprintf(stderr, "N out of range\n"); return 2; }
  double t0 = now_s();
  u64 lowtab[64];
  for (int s = 0; s < 64; s++) {
    u64 w = 0;
    for (int lane = 0; lane < 64; lane++) if ((lane & s) == s) w |= 1ULL << lane;
    lowtab[s] = w;
  }
  u64 **mh = malloc(sizeof(u64 *) * np); unsigned char **ml = malloc(sizeof(char *) * np);
  for (int i = 0; i < np; i++) {
    mh[i] = malloc(8 * P[i].nt); ml[i] = malloc(P[i].nt);
    for (int t = 0; t < P[i].nt; t++) { mh[i][t] = P[i].t[t] >> 6; ml[i][t] = (unsigned char)(P[i].t[t] & 63); }
  }
  u64 count = 0; int cap = 4096; u64 *sols = malloc(8 * cap); int ns = 0;
  u64 H = 1ULL << (N - 6);
  for (u64 h = 0; h < H; h++) {
    u64 alive = ~0ULL;
    for (int i = 0; i < np && alive; i++) {
      u64 v = 0; const u64 *a = mh[i]; const unsigned char *b = ml[i];
      for (int t = 0; t < P[i].nt; t++) if ((h & a[t]) == a[t]) v ^= lowtab[b[t]];
      alive &= ~v;
    }
    while (alive) {
      int lane = __builtin_ctzll(alive); alive &= alive - 1;
      if (ns < cap) sols[ns++] = (h << 6) | (u64)lane;
      count++;
    }
  }
  printf("{\"route\":\"E2-boolean-bruteforce\",\"N\":%d,\"ngens\":%d,\"count\":%llu,\"solutions\":[", N, np, (unsigned long long)count);
  for (int i = 0; i < ns; i++) printf("\"%llx\"%s", (unsigned long long)sols[i], i + 1 < ns ? "," : "");
  printf("],\"seconds\":%.3f,\"peak_rss_kb\":%ld}\n", now_s() - t0, peak_rss_kb());
  return 0;
}
