/* EXP-SEMBIN-35bf67 S-C: exhaustive Boolean evaluation of a descended system (degree <= 3).
 *
 *   exhaust SYS T PREFIX OUT        (enumerate the 2^(N-T) assignments whose top T variables
 *                                    equal PREFIX; T = 0, PREFIX = 0 for the whole cube)
 *
 * Gray-code enumeration with first/second/third derivatives (fast exhaustive search,
 * Bouillaguet et al. CHES 2010, generalized to degree 3); equations bit-packed (<= 64).
 * Derivative state is initialised by direct evaluation, and the whole routine is
 * cross-checked against naive evaluation in Stage 1 (mode 'check').
 *   exhaust check SYS OUT          (naive evaluation of all 2^N points, N <= 26)
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t u64;

static int N, E;
static int *len;
static u64 **eq;

static void readsys(const char *p) {
  FILE *f = fopen(p, "r");
  if (!f) { fprintf(stderr, "open\n"); exit(2); }
  char line[1 << 16];
  N = -1; E = -1;
  while (fgets(line, sizeof line, f)) {
    if (line[0] == '#') continue;
    if (line[0] == 'N') N = atoi(line + 2);
    else if (line[0] == 'E') { E = atoi(line + 2); break; }
  }
  if (N < 1 || N > 64 || E < 0 || E > 64) { fprintf(stderr, "bad header (E<=64 required)\n"); exit(2); }
  len = calloc(E, sizeof(int));
  eq = calloc(E, sizeof(u64 *));
  for (int e = 0; e < E; e++) {
    if (fscanf(f, "%d", &len[e]) != 1) exit(2);
    eq[e] = malloc(sizeof(u64) * (len[e] + 1));
    for (int j = 0; j < len[e]; j++) { unsigned long long x; if (fscanf(f, "%llx", &x) != 1) exit(2); eq[e][j] = x; }
  }
  fclose(f);
}

/* packed evaluation of all equations at point x (bit e = value of equation e) */
static u64 evalp(u64 x) {
  u64 r = 0;
  for (int e = 0; e < E; e++) {
    int p = 0;
    for (int j = 0; j < len[e]; j++) p ^= ((eq[e][j] & ~x) == 0);
    if (p) r |= (u64)1 << e;
  }
  return r;
}

static u64 *sols; static long ns, cap;
static void add(u64 x) { if (ns == cap) { cap = cap ? 2 * cap : 256; sols = realloc(sols, sizeof(u64) * cap); } sols[ns++] = x; }
static int cmpu(const void *a, const void *b) { u64 x = *(const u64 *)a, y = *(const u64 *)b; return x < y ? -1 : x > y; }

int main(int argc, char **argv) {
  if (argc >= 4 && !strcmp(argv[1], "check")) {
    readsys(argv[2]);
    if (N > 26) { fprintf(stderr, "check mode N<=26\n"); return 2; }
    for (u64 x = 0; x < ((u64)1 << N); x++) if (!evalp(x)) add(x);
    FILE *o = fopen(argv[3], "w");
    fprintf(o, "# count=%ld method=naive\n", ns);
    for (long i = 0; i < ns; i++) fprintf(o, "%llx\n", (unsigned long long)sols[i]);
    fclose(o);
    printf("%ld\n", ns);
    return 0;
  }
  if (argc != 5) { fprintf(stderr, "usage: exhaust SYS T PREFIX OUT | exhaust check SYS OUT\n"); return 2; }
  readsys(argv[1]);
  int T = atoi(argv[2]);
  u64 prefix = strtoull(argv[3], 0, 16);
  int L = N - T;                 /* enumerate low L variables */
  u64 base = prefix << L;        /* fixed top bits */
  /* derivative state over the low L variables, evaluated with top bits = base */
  u64 *d1 = calloc(L + 1, sizeof(u64));
  u64 *d2 = calloc((size_t)L * L + 1, sizeof(u64));
  u64 *d3 = calloc((size_t)L * L * L + 1, sizeof(u64));
#define G(x) ((x) ^ ((x) >> 1))
  for (int i = 0; i < L; i++) {
    u64 p = base | G(((u64)1 << i) - 1);
    d1[i] = evalp(p) ^ evalp(p ^ ((u64)1 << i));
  }
  for (int i = 0; i < L; i++)
    for (int j = i + 1; j < L; j++) {
      u64 p = base | G((((u64)1 << j) - ((u64)1 << i)) - 1);
      u64 ei = (u64)1 << i, ej = (u64)1 << j;
      d2[(size_t)i * L + j] = evalp(p) ^ evalp(p ^ ei) ^ evalp(p ^ ej) ^ evalp(p ^ ei ^ ej);
    }
  for (int i = 0; i < L; i++)
    for (int j = i + 1; j < L; j++)
      for (int l = j + 1; l < L; l++) {
        u64 ei = (u64)1 << i, ej = (u64)1 << j, el = (u64)1 << l, p = base, v = 0;
        for (int m = 0; m < 8; m++) v ^= evalp(p ^ ((m & 1) ? ei : 0) ^ ((m & 2) ? ej : 0) ^ ((m & 4) ? el : 0));
        d3[((size_t)i * L + j) * L + l] = v;
      }
  u64 Fv = evalp(base);
  if (!Fv) add(base);
  u64 lim = (u64)1 << L;
  for (u64 kk = 1; kk < lim; kk++) {
    int b1 = __builtin_ctzll(kk);
    u64 k2 = kk & (kk - 1);
    if (k2) {
      int b2 = __builtin_ctzll(k2);
      u64 k3 = k2 & (k2 - 1);
      if (k3) {
        int b3 = __builtin_ctzll(k3);
        d2[(size_t)b1 * L + b2] ^= d3[((size_t)b1 * L + b2) * L + b3];
      }
      d1[b1] ^= d2[(size_t)b1 * L + b2];
    }
    Fv ^= d1[b1];
    if (!Fv) add(base | G(kk));
  }
  /* verify every reported solution by direct evaluation */
  for (long i = 0; i < ns; i++) if (evalp(sols[i])) { fprintf(stderr, "reported non-solution\n"); return 5; }
  qsort(sols, ns, sizeof(u64), cmpu);
  FILE *o = fopen(argv[4], "w");
  fprintf(o, "# count=%ld method=gray T=%d prefix=%llx\n", ns, T, (unsigned long long)prefix);
  for (long i = 0; i < ns; i++) fprintf(o, "%llx\n", (unsigned long long)sols[i]);
  fclose(o);
  printf("%ld\n", ns);
  return 0;
}
