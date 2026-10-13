/* Deterministic x-only candidate sieve for the m=51 ordinary binary class.
 *
 * Scientific mode maps global_index through a frozen, keyed 51-bit Feistel
 * permutation.  Thus every admitted index has a distinct b, and splitting or
 * reordering index ranges cannot change it.  The range containing the
 * permutation's unique b=0 preimage is rejected.  root_seed affects only the
 * three point-x probes, which use separate indexed RNG domains.
 * A row is emitted only when all three point probes are killed by NORD.
 * This is a sieve, not an exact cardinality or conductor certificate.
 *
 * mock-scan deliberately writes an incompatible, visibly tagged schema and
 * singular b=0 fixtures.  Its output can exercise orchestration but can never
 * be accepted by a scientific-output parser.
 *
 * Usage:
 *   search selftest
 *   search reference-vectors <input.csv> <out.csv>
 *   search scan <root_seed> <start> <count> <out.csv>
 *   search mock-scan <root_seed> <start> <count> <out.csv>
 */
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <immintrin.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "params.h"

#define MASK ((1ULL << M) - 1ULL)
#define POINT_PROBES 3u
#define POINT_TRIES 256u
#define FIELD_SIZE (1ULL << M)

#define DOMAIN_X0 0x4D353150524F4230ULL
#define DOMAIN_X1 0x4D353150524F4231ULL
#define DOMAIN_X2 0x4D353150524F4232ULL
#define DOMAIN_MOCK_X 0x4D35314D4F434B58ULL

#define FEISTEL_ROUNDS 12u
#define PRP_ZERO_PREIMAGE 1143900985707342ULL

_Static_assert(M > 1 && M < 64, "field degree must fit the 64-bit backend");
_Static_assert(M == 51, "frozen Feistel packing requires a 51-bit field");
_Static_assert(NORD > 1, "target order must be nontrivial");
_Static_assert((FEISTEL_ROUNDS & 1u) == 0,
               "final Feistel packing requires an even round count");
_Static_assert(DOMAIN_X0 != DOMAIN_X1 && DOMAIN_X0 != DOMAIN_X2 &&
                   DOMAIN_X1 != DOMAIN_X2,
               "point-probe RNG domains must be disjoint");

typedef uint64_t fe;

static inline fe clmul_low(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  return (fe)_mm_cvtsi128_si64(r);
}

static inline fe fmul(fe a, fe b) {
  __m128i r = _mm_clmulepi64_si128(_mm_cvtsi64_si128((long long)a),
                                   _mm_cvtsi64_si128((long long)b), 0);
  uint64_t lo = (uint64_t)_mm_cvtsi128_si64(r);
  uint64_t hi = (uint64_t)_mm_extract_epi64(r, 1);
  uint64_t t = (lo >> M) | (hi << (64 - M));
  uint64_t p = (lo & MASK) ^ clmul_low(t, RED);
  t = p >> M;
  return (p & MASK) ^ clmul_low(t, RED);
}

static inline fe fsqr(fe a) { return fmul(a, a); }

static fe fsqrn(fe a, unsigned n) {
  while (n-- != 0) a = fsqr(a);
  return a;
}

static fe finv(fe a) {
  int k = 1;
  int n = M - 1;
  int top = 63 - __builtin_clzll((unsigned long long)n);
  fe b = a;
  for (int i = top - 1; i >= 0; i--) {
    b = fmul(fsqrn(b, (unsigned)k), b);
    k *= 2;
    if ((n >> i) & 1) {
      b = fmul(fsqr(b), a);
      k++;
    }
  }
  return fsqr(b);
}

static int ftrace(fe a) {
  fe t = a, s = a;
  for (int i = 1; i < M; i++) {
    s = fsqr(s);
    t ^= s;
  }
  return (int)(t & 1ULL);
}

static uint64_t mix64(uint64_t z) {
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}

static uint64_t indexed_word(uint64_t seed, uint64_t index,
                             uint64_t domain, uint64_t attempt) {
  return mix64(seed ^ domain ^ mix64(index + 0x9E3779B97F4A7C15ULL) ^
               mix64(attempt + 0xD1B54A32D192ED03ULL));
}

static const uint64_t FEISTEL_KEYS[FEISTEL_ROUNDS] = {
    0x824FED8E0FDE5218ULL, 0x00B2A56B05421B2DULL,
    0xFD0F52502A0D3737ULL, 0x78CDB4C19DD24202ULL,
    0x722CFEF7C6D0EA93ULL, 0xE007ABB4C970F252ULL,
    0xA56276B6D4746BEDULL, 0x08E8F877EC4098BCULL,
    0x02EA18FD04E1DD08ULL, 0xEFB6477DE16EC1DAULL,
    0xAF1A485BBAF930E9ULL, 0xC80FF63F19D1D47CULL};

static uint64_t bit_mask(unsigned bits) {
  return (1ULL << bits) - 1ULL;
}

/*
 * Frozen 12-round unbalanced Feistel PRP.  Initially L has 26 bits and R has
 * 25.  Round i emits old_l_bits from mix64(R ^ key[i] ^ old_r_bits<<56),
 * then swaps the side widths.  Twelve rounds restore the initial packing.
 */
static fe permute51(fe input) {
  uint64_t left = (input >> 25) & bit_mask(26);
  uint64_t right = input & bit_mask(25);
  unsigned left_bits = 26;
  unsigned right_bits = 25;
  for (unsigned round = 0; round < FEISTEL_ROUNDS; round++) {
    uint64_t output =
        mix64(right ^ FEISTEL_KEYS[round] ^
              ((uint64_t)right_bits << 56)) & bit_mask(left_bits);
    uint64_t new_left = right;
    uint64_t new_right = left ^ output;
    left = new_left;
    right = new_right;
    unsigned swap = left_bits;
    left_bits = right_bits;
    right_bits = swap;
  }
  return ((left & bit_mask(26)) << 25) | (right & bit_mask(25));
}

static fe permute51_inverse(fe input) {
  uint64_t left = (input >> 25) & bit_mask(26);
  uint64_t right = input & bit_mask(25);
  for (int round = (int)FEISTEL_ROUNDS - 1; round >= 0; round--) {
    unsigned old_left_bits = (round & 1) != 0 ? 25u : 26u;
    unsigned old_right_bits = (round & 1) != 0 ? 26u : 25u;
    uint64_t old_right = left;
    uint64_t output =
        mix64(old_right ^ FEISTEL_KEYS[round] ^
              ((uint64_t)old_right_bits << 56)) & bit_mask(old_left_bits);
    uint64_t old_left = right ^ output;
    left = old_left;
    right = old_right;
  }
  return ((left & bit_mask(26)) << 25) | (right & bit_mask(25));
}

static fe indexed_b(uint64_t index) {
  return permute51(index & MASK);
}

static uint64_t probe_domain(unsigned probe) {
  static const uint64_t domains[POINT_PROBES] = {
      DOMAIN_X0, DOMAIN_X1, DOMAIN_X2};
  return domains[probe];
}

/* Historical Lopez--Dahab x-only ladder: return whether [NORD]P is O. */
static int kills(fe b, fe x) {
  fe X0 = x, Z0 = 1, X1, Z1;
  fe x2 = fsqr(x); X1 = fsqr(x2) ^ b; Z1 = x2;
  for (int i = 62 - __builtin_clzll(NORD); i >= 0; i--) {
    fe T = fmul(X0, Z1), U = fmul(X1, Z0), Za = fsqr(T ^ U), Xa = fmul(x, Za) ^ fmul(T, U);
    if ((NORD >> i) & 1) { fe xx = fsqr(X1), zz = fsqr(Z1); X1 = fsqr(xx) ^ fmul(b, fsqr(zz)); Z1 = fmul(xx, zz); X0 = Xa; Z0 = Za; }
    else { fe xx = fsqr(X0), zz = fsqr(Z0); X0 = fsqr(xx) ^ fmul(b, fsqr(zz)); Z0 = fmul(xx, zz); X1 = Xa; Z1 = Za; }
  }
  return Z0 == 0;
}

/* Deterministically find the x-coordinate of a point on E_b. */
static int point_x(fe b, uint64_t seed, uint64_t index,
                   unsigned probe, fe *x) {
  uint64_t domain = probe_domain(probe);
  for (uint64_t attempt = 0; attempt < POINT_TRIES; attempt++) {
    fe c = indexed_word(seed, index, domain, attempt) & MASK;
    if (c == 0) continue;
    fe v = c ^ fmul(b, finv(fsqr(c)));
    if (!ftrace(v)) {
      *x = c;
      return 1;
    }
  }
  return 0;
}

static int candidate_probes(fe b, uint64_t seed, uint64_t index,
                            fe x[POINT_PROBES]) {
  for (unsigned probe = 0; probe < POINT_PROBES; probe++) {
    if (!point_x(b, seed, index, probe, &x[probe])) return -1;
    if (!kills(b, x[probe])) return 0;
  }
  return 1;
}

static int parse_u64(const char *s, uint64_t *out) {
  uint64_t value = 0;
  if (s == NULL || *s == '\0') return 0;
  for (const unsigned char *p = (const unsigned char *)s; *p != '\0'; p++) {
    unsigned digit;
    if (*p < (unsigned char)'0' || *p > (unsigned char)'9') return 0;
    digit = (unsigned)(*p - (unsigned char)'0');
    if (value > (UINT64_MAX - digit) / 10ULL) return 0;
    value = value * 10ULL + digit;
  }
  *out = value;
  return 1;
}

static int parse_canonical_u64(const char *s, uint64_t *out) {
  if (s == NULL || (s[0] == '0' && s[1] != '\0')) return 0;
  return parse_u64(s, out);
}

static int valid_range(uint64_t start, uint64_t count) {
  return count != 0 && count - 1ULL <= UINT64_MAX - start;
}

static int valid_scientific_domain(uint64_t start, uint64_t count) {
  uint64_t stop;
  if (start >= FIELD_SIZE || count > FIELD_SIZE - start) {
    return 0;
  }
  stop = start + count;
  return PRP_ZERO_PREIMAGE < start || PRP_ZERO_PREIMAGE >= stop;
}

static FILE *open_exclusive(const char *path) {
  int fd = open(path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
  if (fd < 0) {
    fprintf(stderr, "cannot exclusively create %s: %s\n", path,
            strerror(errno));
    return NULL;
  }
  FILE *out = fdopen(fd, "w");
  if (out == NULL) {
    int saved_errno = errno;
    (void)close(fd);
    (void)unlink(path);
    errno = saved_errno;
    fprintf(stderr, "cannot open stream for %s: %s\n", path,
            strerror(errno));
  }
  return out;
}

static int finish_output(FILE *out, const char *path) {
  if (fflush(out) != 0) {
    fprintf(stderr, "cannot flush %s: %s\n", path, strerror(errno));
    (void)fclose(out);
    return 0;
  }
  if (fsync(fileno(out)) != 0) {
    fprintf(stderr, "cannot sync %s: %s\n", path, strerror(errno));
    (void)fclose(out);
    return 0;
  }
  if (fclose(out) != 0) {
    fprintf(stderr, "cannot close %s: %s\n", path, strerror(errno));
    return 0;
  }
  return 1;
}

static int strip_csv_record(char *line, ssize_t length) {
  size_t size;
  if (length <= 0 || memchr(line, '\0', (size_t)length) != NULL) return 0;
  size = (size_t)length;
  if (line[size - 1] == '\n') size--;
  if (size != 0 && line[size - 1] == '\r') size--;
  line[size] = '\0';
  return size != 0 && strchr(line, '\r') == NULL && strchr(line, '\n') == NULL;
}

static int split_reference_fields(char *line, char *fields[6]) {
  char *cursor = line;
  for (size_t i = 0; i < 6; i++) {
    char *comma;
    fields[i] = cursor;
    comma = strchr(cursor, ',');
    if (i == 5) {
      if (comma != NULL || *cursor == '\0') return 0;
    } else {
      if (comma == NULL || comma == cursor) return 0;
      *comma = '\0';
      cursor = comma + 1;
    }
  }
  return 1;
}

/*
 * Non-scientific differential-test interface.  Its tagged schema is
 * intentionally incompatible with scan output and cannot enter the candidate
 * pipeline.  Input columns are canonical unsigned decimal strings:
 * case_id,mul_a,mul_b,inv_a,curve_b,x
 */
static int run_reference_vectors(const char *input_path,
                                 const char *output_path) {
  static const char input_header[] =
      "case_id,mul_a,mul_b,inv_a,curve_b,x";
  FILE *input = NULL;
  FILE *output = NULL;
  char *line = NULL;
  size_t capacity = 0;
  ssize_t length;
  uint64_t last_case_id = 0;
  uint64_t rows = 0;
  int output_created = 0;
  int status = 1;

  input = fopen(input_path, "r");
  if (input == NULL) {
    fprintf(stderr, "cannot open reference input %s: %s\n", input_path,
            strerror(errno));
    goto cleanup;
  }
  length = getline(&line, &capacity, input);
  if (!strip_csv_record(line, length) || strcmp(line, input_header) != 0) {
    fprintf(stderr, "reference input has an invalid header\n");
    goto cleanup;
  }

  output = open_exclusive(output_path);
  if (output == NULL) goto cleanup;
  output_created = 1;
  fprintf(stderr,
          "REFERENCE-VECTORS ONLY: differential-test data, not scientific data\n");
  if (fprintf(output,
              "record_kind,case_id,mul_product,inv_result,kills_nord\n") < 0) {
    fprintf(stderr, "cannot write %s: %s\n", output_path, strerror(errno));
    goto cleanup;
  }

  while ((length = getline(&line, &capacity, input)) >= 0) {
    char *fields[6];
    uint64_t values[6];
    if (length > 512 || !strip_csv_record(line, length) ||
        !split_reference_fields(line, fields)) {
      fprintf(stderr, "malformed reference record at row %" PRIu64 "\n",
              rows + 2);
      goto cleanup;
    }
    for (size_t i = 0; i < 6; i++) {
      if (!parse_canonical_u64(fields[i], &values[i])) {
        fprintf(stderr,
                "noncanonical reference integer at row %" PRIu64 "\n",
                rows + 2);
        goto cleanup;
      }
    }
    if ((rows != 0 && values[0] <= last_case_id) || values[1] > MASK ||
        values[2] > MASK || values[3] == 0 || values[3] > MASK ||
        values[4] == 0 || values[4] > MASK || values[5] > MASK) {
      fprintf(stderr, "out-of-domain reference record at row %" PRIu64 "\n",
              rows + 2);
      goto cleanup;
    }
    if (fprintf(output,
                "REFERENCE_ONLY,%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%d\n",
                values[0], fmul((fe)values[1], (fe)values[2]),
                finv((fe)values[3]), kills((fe)values[4], (fe)values[5])) <
        0) {
      fprintf(stderr, "cannot write %s: %s\n", output_path, strerror(errno));
      goto cleanup;
    }
    last_case_id = values[0];
    rows++;
  }
  if (ferror(input) != 0 || rows == 0) {
    fprintf(stderr, "reference input is empty or unreadable\n");
    goto cleanup;
  }
  if (fclose(input) != 0) {
    input = NULL;
    fprintf(stderr, "cannot close %s: %s\n", input_path, strerror(errno));
    goto cleanup;
  }
  input = NULL;
  if (!finish_output(output, output_path)) {
    output = NULL;
    goto cleanup;
  }
  output = NULL;
  output_created = 0;
  status = 0;

cleanup:
  free(line);
  if (input != NULL) (void)fclose(input);
  if (output != NULL) (void)fclose(output);
  if (output_created != 0) (void)unlink(output_path);
  return status;
}

static int run_scan(uint64_t seed, uint64_t start, uint64_t count,
                    const char *path) {
  FILE *out = open_exclusive(path);
  if (out == NULL) return 1;
  if (fprintf(out, "global_index,b,x0,x1,x2\n") < 0) {
    fprintf(stderr, "cannot write %s: %s\n", path, strerror(errno));
    (void)fclose(out);
    return 1;
  }
  for (uint64_t offset = 0; offset < count; offset++) {
    uint64_t index = start + offset;
    fe b = indexed_b(index);
    fe x[POINT_PROBES];
    int result = candidate_probes(b, seed, index, x);
    if (result < 0) {
      fprintf(stderr,
              "point generation exhausted at global index %" PRIu64 "\n",
              index);
      (void)fclose(out);
      return 1;
    }
    if (result == 0) continue;
    if (fprintf(out, "%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                     ",%" PRIu64 "\n",
                index, b, x[0], x[1], x[2]) < 0) {
      fprintf(stderr, "cannot write %s: %s\n", path, strerror(errno));
      (void)fclose(out);
      return 1;
    }
  }
  return finish_output(out, path) ? 0 : 1;
}

static int run_mock_scan(uint64_t seed, uint64_t start, uint64_t count,
                         const char *path) {
  FILE *out = open_exclusive(path);
  if (out == NULL) return 1;
  fprintf(stderr,
          "MOCK-SCAN ONLY: writing tagged singular fixtures, not scientific data\n");
  if (fprintf(out, "record_kind,global_index,b,x0,x1,x2\n") < 0) {
    fprintf(stderr, "cannot write %s: %s\n", path, strerror(errno));
    (void)fclose(out);
    return 1;
  }
  for (uint64_t offset = 0; offset < count; offset++) {
    uint64_t index = start + offset;
    uint64_t x0 = indexed_word(seed, index, DOMAIN_MOCK_X, 0) & MASK;
    uint64_t x1 = indexed_word(seed, index, DOMAIN_MOCK_X, 1) & MASK;
    uint64_t x2 = indexed_word(seed, index, DOMAIN_MOCK_X, 2) & MASK;
    if (fprintf(out, "MOCK_FIXTURE,%" PRIu64 ",0,%" PRIu64 ",%" PRIu64
                     ",%" PRIu64 "\n",
                index, x0, x1, x2) < 0) {
      fprintf(stderr, "cannot write %s: %s\n", path, strerror(errno));
      (void)fclose(out);
      return 1;
    }
  }
  return finish_output(out, path) ? 0 : 1;
}

static int selftest_curve(fe b, uint64_t seed, uint64_t index) {
  fe x[POINT_PROBES];
  return candidate_probes(b, seed, index, x) == 1;
}

static int selftest(void) {
  static const struct {
    fe input;
    fe output;
  } prp_vectors[] = {
      {0ULL, 325821132841042ULL},
      {1ULL, 2117735011170056ULL},
      {2ULL, 801276827696746ULL},
      {42ULL, 1218540018519903ULL},
      {3599999999ULL, 1615711514229309ULL},
      {MASK, 976302417368263ULL}};
  uint64_t parsed = 0;
  const fe x_expected[POINT_PROBES] = {
      569140238631623ULL, 1549270749159026ULL, 1338773304965067ULL};
  fe x_a[POINT_PROBES], x_b[POINT_PROBES];

  if (fmul(0, MASK) != 0 || fmul(1, MASK) != MASK ||
      fmul(0x123456789ABULL, finv(0x123456789ABULL)) != 1) {
    fprintf(stderr, "selftest: field arithmetic failed\n");
    return 1;
  }
  if (permute51_inverse(0) != PRP_ZERO_PREIMAGE) {
    fprintf(stderr, "selftest: zero preimage changed\n");
    return 1;
  }
  for (size_t i = 0; i < sizeof(prp_vectors) / sizeof(prp_vectors[0]); i++) {
    if (permute51(prp_vectors[i].input) != prp_vectors[i].output ||
        permute51_inverse(prp_vectors[i].output) != prp_vectors[i].input) {
      fprintf(stderr, "selftest: frozen PRP vector failed\n");
      return 1;
    }
  }
  for (uint64_t i = 0; i < 1024; i++) {
    fe word = indexed_word(0x51B1ECA7ULL, i, DOMAIN_MOCK_X, 7) & MASK;
    if (permute51_inverse(permute51(word)) != word ||
        permute51(permute51_inverse(word)) != word) {
      fprintf(stderr, "selftest: 51-bit permutation round trip failed\n");
      return 1;
    }
  }
  if (!selftest_curve(KNOWN_CRATER_B, 0x51C0FFEEULL, 17) ||
      !selftest_curve(KNOWN_FLOOR_271_B, 0x51C0FFEEULL, 271)) {
    fprintf(stderr, "selftest: known in-class curve failed the sieve\n");
    return 1;
  }
  if (candidate_probes(2, 0x51C0FFEEULL, 2, x_a) != 0) {
    fprintf(stderr, "selftest: deterministic negative curve passed\n");
    return 1;
  }
  if (candidate_probes(KNOWN_CRATER_B, 123456789ULL, 42, x_a) != 1 ||
      candidate_probes(KNOWN_CRATER_B, 123456789ULL, 42, x_b) != 1 ||
      memcmp(x_a, x_b, sizeof(x_a)) != 0 ||
      memcmp(x_a, x_expected, sizeof(x_a)) != 0 ||
      indexed_b(42) != 1218540018519903ULL) {
    fprintf(stderr, "selftest: indexed derivation is not deterministic\n");
    return 1;
  }
  if (!parse_u64("18446744073709551615", &parsed) ||
      parsed != UINT64_MAX || parse_u64("", &parsed) ||
      parse_u64("-1", &parsed) || parse_u64("+1", &parsed) ||
      parse_u64(" 1", &parsed) || parse_u64("1x", &parsed) ||
      parse_u64("18446744073709551616", &parsed) || valid_range(0, 0) ||
      valid_range(UINT64_MAX, 2) || !valid_range(UINT64_MAX, 1) ||
      valid_scientific_domain(FIELD_SIZE, 1) ||
      valid_scientific_domain(PRP_ZERO_PREIMAGE, 1) ||
      !valid_scientific_domain(0, 3600000000ULL)) {
    fprintf(stderr, "selftest: malformed-input checks failed\n");
    return 1;
  }
  puts("selftest ok");
  return 0;
}

static void usage(const char *program) {
  fprintf(stderr,
          "usage:\n"
          "  %s selftest\n"
          "  %s reference-vectors <input.csv> <out.csv>\n"
          "  %s scan <root_seed> <start> <count> <out.csv>\n"
          "  %s mock-scan <root_seed> <start> <count> <out.csv>\n",
          program, program, program, program);
}

int main(int argc, char **argv) {
  uint64_t seed, start, count;
  int mock;

  if (argc == 2 && strcmp(argv[1], "selftest") == 0) return selftest();
  if (argc == 4 && strcmp(argv[1], "reference-vectors") == 0) {
    if (argv[2][0] == '\0' || argv[3][0] == '\0') {
      fprintf(stderr, "invalid reference input or output path\n");
      return 2;
    }
    return run_reference_vectors(argv[2], argv[3]);
  }
  if (argc != 6 ||
      (strcmp(argv[1], "scan") != 0 && strcmp(argv[1], "mock-scan") != 0)) {
    usage(argv[0]);
    return 2;
  }
  if (!parse_u64(argv[2], &seed) || !parse_u64(argv[3], &start) ||
      !parse_u64(argv[4], &count) || !valid_range(start, count) ||
      argv[5][0] == '\0') {
    fprintf(stderr, "invalid numeric range or output path\n");
    usage(argv[0]);
    return 2;
  }
  mock = strcmp(argv[1], "mock-scan") == 0;
  if (!mock && !valid_scientific_domain(start, count)) {
    fprintf(stderr,
            "scientific range exceeds the 51-bit permutation domain or "
            "contains its singular b=0 preimage\n");
    return 2;
  }
  return mock ? run_mock_scan(seed, start, count, argv[5])
              : run_scan(seed, start, count, argv[5]);
}
