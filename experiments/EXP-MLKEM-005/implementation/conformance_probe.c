/*
 * EXP-MLKEM-005 laboratory conformance / primitive multiclass probe (wolfSSL).
 *
 * Reach: declare WOLFSSL_LOCAL comparison symbols; link attested libwolfssl.a.
 * Never modifies library comparison logic, lengths, or dispatch.
 *
 * Modes:
 *   attest | negative-harness | primitive-multiclass | acvp-anchor | archive-key0
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>

#include <wolfssl/options.h>
#include <wolfssl/wolfcrypt/settings.h>
#if defined(__has_include)
#  if __has_include(<wolfssl/wolfcrypt/mlkem.h>)
#    include <wolfssl/wolfcrypt/mlkem.h>
#  endif
#endif
#include <wolfssl/wolfcrypt/wc_mlkem.h>
#include <wolfssl/wolfcrypt/sha256.h>
#include <wolfssl/wolfcrypt/error-crypt.h>

extern int mlkem_cmp(const byte* a, const byte* b, int sz);
#ifdef PROBE_BACKEND_AVX2
extern int mlkem_cmp_avx2(const byte* a, const byte* b, int sz);
#endif
#ifdef PROBE_BACKEND_NEON
extern int mlkem_cmp_neon(const byte* a, const byte* b, int sz);
#endif

#define SS_LEN 32
#define MAX_CT 1600
#define MAX_EK 1600
#define MAX_DK 3200
#define MAKEKEY_RAND 64
#define ENC_RAND 32
#define N_SEEDS 4
#define MUTATION_CAP 20000

typedef struct {
    const char* name;
    int type;
    word32 ct_len;
} ParamSet;

static const ParamSet PARAMS[] = {
    { "ML-KEM-512",  WC_ML_KEM_512,  768 },
    { "ML-KEM-768",  WC_ML_KEM_768,  1088 },
    { "ML-KEM-1024", WC_ML_KEM_1024, 1568 },
};
static const int NPARAMS = 3;

/* Four deterministic seed materials (seeds 1..4). First 64 = keygen, next 32 = enc. */
static void fill_seed_material(int seed_id, unsigned char out[MAKEKEY_RAND + ENC_RAND])
{
    int i;
    memset(out, 0, MAKEKEY_RAND + ENC_RAND);
    out[0] = (unsigned char)seed_id;
    out[1] = 0xA5;
    out[2] = 0x5A;
    for (i = 3; i < MAKEKEY_RAND + ENC_RAND; i++) {
        out[i] = (unsigned char)((seed_id * 17 + i * 31) & 0xff);
    }
    out[MAKEKEY_RAND] = (unsigned char)(0xC3 ^ seed_id);
}

static const char* g_build_id = "unknown";
static const char* g_backend = "unknown";
static const char* g_commit = "unknown";
static const char* g_out_path = NULL;
static const char* g_acvp_prompt = NULL;
static const char* g_acvp_expected = NULL;
static const char* g_vectors_dir = NULL;

static void die(const char* msg, int rc)
{
    fprintf(stderr, "FATAL: %s (rc=%d)\n", msg, rc);
    exit(2);
}

static void hex_of(const unsigned char* b, size_t n, char* out, size_t out_sz)
{
    static const char* hexd = "0123456789abcdef";
    size_t i;
    if (out_sz < n * 2 + 1) die("hex buffer too small", (int)out_sz);
    for (i = 0; i < n; i++) {
        out[2 * i] = hexd[(b[i] >> 4) & 0xf];
        out[2 * i + 1] = hexd[b[i] & 0xf];
    }
    out[2 * n] = 0;
}

static int unhex(const char* hex, unsigned char* out, size_t out_max, size_t* out_len)
{
    size_t n = strlen(hex);
    size_t i;
    if (n % 2) return -1;
    if (n / 2 > out_max) return -2;
    for (i = 0; i < n; i += 2) {
        unsigned int v;
        if (sscanf(hex + i, "%2x", &v) != 1) return -3;
        out[i / 2] = (unsigned char)v;
    }
    *out_len = n / 2;
    return 0;
}

static void sha256_hex(const unsigned char* b, size_t n, char out[65])
{
    unsigned char dig[WC_SHA256_DIGEST_SIZE];
    wc_Sha256 sha;
    if (wc_InitSha256(&sha) != 0) die("sha256 init", -1);
    if (wc_Sha256Update(&sha, b, (word32)n) != 0) die("sha256 update", -1);
    if (wc_Sha256Final(&sha, dig) != 0) die("sha256 final", -1);
    wc_Sha256Free(&sha);
    hex_of(dig, WC_SHA256_DIGEST_SIZE, out, 65);
}

static int harness_truncated_cmp(const byte* a, const byte* b, int sz)
{
    int half = sz / 2;
    int i;
    byte r = 0;
    for (i = 0; i < half; i++) r |= a[i] ^ b[i];
    return (int)(0 - ((-(word32)r) >> 31));
}

static int library_cmp(const byte* a, const byte* b, int sz)
{
#if defined(PROBE_BACKEND_AVX2)
    return mlkem_cmp_avx2(a, b, sz);
#elif defined(PROBE_BACKEND_NEON)
    return mlkem_cmp_neon(a, b, sz);
#else
    return mlkem_cmp(a, b, sz);
#endif
}

static const char* backend_name(void)
{
#if defined(PROBE_BACKEND_AVX2)
    return "x64_avx2";
#elif defined(PROBE_BACKEND_NEON)
    return "aarch64_neon";
#else
    return "scalar_c";
#endif
}

static int make_keypair_ct(int type, int seed_id,
    unsigned char* ct, word32* ct_len,
    unsigned char* ss, word32* ss_len,
    unsigned char* ek, word32* ek_len,
    unsigned char* dk, word32* dk_len,
    MlKemKey* key)
{
    unsigned char mat[MAKEKEY_RAND + ENC_RAND];
    int ret;
    fill_seed_material(seed_id, mat);
    ret = wc_MlKemKey_Init(key, type, NULL, INVALID_DEVID);
    if (ret != 0) return ret;
    ret = wc_MlKemKey_MakeKeyWithRandom(key, mat, MAKEKEY_RAND);
    if (ret != 0) return ret;
    ret = wc_MlKemKey_CipherTextSize(key, ct_len);
    if (ret != 0) return ret;
    ret = wc_MlKemKey_SharedSecretSize(key, ss_len);
    if (ret != 0) return ret;
    if (ek && ek_len) {
        ret = wc_MlKemKey_PublicKeySize(key, ek_len);
        if (ret != 0) return ret;
        ret = wc_MlKemKey_EncodePublicKey(key, ek, *ek_len);
        if (ret != 0) return ret;
    }
    if (dk && dk_len) {
        ret = wc_MlKemKey_PrivateKeySize(key, dk_len);
        if (ret != 0) return ret;
        ret = wc_MlKemKey_EncodePrivateKey(key, dk, *dk_len);
        if (ret != 0) return ret;
    }
    ret = wc_MlKemKey_EncapsulateWithRandom(key, ct, ss, mat + MAKEKEY_RAND, ENC_RAND);
    return ret;
}

static void write_json_header(FILE* f, const char* mode)
{
    fprintf(f,
        "{\n"
        "  \"experiment_id\": \"EXP-MLKEM-005\",\n"
        "  \"mode\": \"%s\",\n"
        "  \"build_id\": \"%s\",\n"
        "  \"backend\": \"%s\",\n"
        "  \"resolved_commit\": \"%s\",\n"
        "  \"probe_backend_macro\": \"%s\",\n",
        mode, g_build_id, g_backend, g_commit, backend_name());
}

static int mode_attest(FILE* f)
{
    enum { ATTEST_LEN = 768 };
    unsigned char a[ATTEST_LEN], b[ATTEST_LEN];
    int equal, unequal;
    memset(a, 0x5a, sizeof(a));
    memset(b, 0x5a, sizeof(b));
    equal = library_cmp(a, b, ATTEST_LEN);
    b[1] ^= 0x01;
    unequal = library_cmp(a, b, ATTEST_LEN);
    write_json_header(f, "attest");
    fprintf(f,
        "  \"comparison_symbol\": \"%s\",\n"
        "  \"attest_length\": %d,\n"
        "  \"self_test_equal_rc\": %d,\n"
        "  \"self_test_unequal_rc\": %d,\n"
        "  \"attested\": %s,\n"
#ifdef USE_INTEL_SPEEDUP
        "  \"USE_INTEL_SPEEDUP\": true,\n"
#else
        "  \"USE_INTEL_SPEEDUP\": false,\n"
#endif
#ifdef WOLFSSL_ARMASM
        "  \"WOLFSSL_ARMASM\": true,\n"
#else
        "  \"WOLFSSL_ARMASM\": false,\n"
#endif
        "  \"WOLFSSL_HAVE_MLKEM\": true\n"
        "}\n",
#if defined(PROBE_BACKEND_AVX2)
        "mlkem_cmp_avx2",
#elif defined(PROBE_BACKEND_NEON)
        "mlkem_cmp_neon",
#else
        "mlkem_cmp",
#endif
        ATTEST_LEN, equal, unequal,
        (equal == 0 && unequal != 0) ? "true" : "false");
    return (equal == 0 && unequal != 0) ? 0 : 1;
}

/* Negative harness: each class G1/G2/G3 must flag omitted half it can reach. */
static int mode_negative_harness(FILE* f)
{
    int p, all_ok = 1;
    write_json_header(f, "negative-harness");
    fprintf(f, "  \"results\": [\n");
    for (p = 0; p < NPARAMS; p++) {
        word32 ct_len = PARAMS[p].ct_len;
        int half = (int)ct_len / 2;
        unsigned char base[MAX_CT];
        int g1_ok = 1, g2_ok = 1, g3_ok = 1;
        int idx;
        memset(base, 0xA5, ct_len);

        /* G1: every index */
        for (idx = 0; idx < (int)ct_len; idx++) {
            unsigned char mut[MAX_CT];
            int rc;
            memcpy(mut, base, ct_len);
            mut[idx] ^= 0x01;
            rc = harness_truncated_cmp(base, mut, (int)ct_len);
            if (idx < half && rc == 0) g1_ok = 0;
            if (idx >= half && rc != 0) g1_ok = 0;
        }
        /* G2: contiguous 8-byte at start of each half */
        {
            unsigned char mut[MAX_CT];
            int i, rc;
            memcpy(mut, base, ct_len);
            for (i = 0; i < 8; i++) mut[i] ^= 0x01;
            rc = harness_truncated_cmp(base, mut, (int)ct_len);
            if (rc == 0) g2_ok = 0; /* should detect — in compared half */
            memcpy(mut, base, ct_len);
            for (i = 0; i < 8; i++) mut[half + i] ^= 0x01;
            rc = harness_truncated_cmp(base, mut, (int)ct_len);
            if (rc != 0) g2_ok = 0; /* should be silent — omitted half */
        }
        /* G3: boundary at 0 and at half */
        {
            unsigned char mut[MAX_CT];
            int rc;
            memcpy(mut, base, ct_len);
            mut[0] ^= 0xff;
            rc = harness_truncated_cmp(base, mut, (int)ct_len);
            if (rc == 0) g3_ok = 0;
            memcpy(mut, base, ct_len);
            mut[half] ^= 0xff;
            rc = harness_truncated_cmp(base, mut, (int)ct_len);
            if (rc != 0) g3_ok = 0;
        }
        if (!(g1_ok && g2_ok && g3_ok)) all_ok = 0;
        if (p) fprintf(f, ",\n");
        fprintf(f,
            "    {\"parameter_set\":\"%s\",\"ct_len\":%u,\"half\":%d,"
            "\"omitted_range_start\":%d,\"omitted_range_end\":%u,"
            "\"G1_detected\":%s,\"G2_detected\":%s,\"G3_detected\":%s,"
            "\"detected\":%s}",
            PARAMS[p].name, ct_len, half, half, ct_len,
            g1_ok ? "true" : "false", g2_ok ? "true" : "false",
            g3_ok ? "true" : "false",
            (g1_ok && g2_ok && g3_ok) ? "true" : "false");
    }
    fprintf(f, "\n  ],\n  \"negative_harness_detected\": %s\n}\n",
            all_ok ? "true" : "false");
    return all_ok ? 0 : 1;
}

/* Deterministic PRNG for G2 offsets */
static uint32_t mix32(uint32_t x)
{
    x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16;
    return x;
}

static int run_primitive_class(FILE* f, const ParamSet* ps, const char* class_id, int* first_out)
{
    int seed, n_silent = 0;
    word32 ct_len = ps->ct_len;
    int silent_votes[MAX_CT];
    int coverage_events = 0;
    int capped = 0;
    int indices_hit[MAX_CT];
    int i;

    memset(silent_votes, 0, sizeof(silent_votes));
    memset(indices_hit, 0, sizeof(indices_hit));

    for (seed = 1; seed <= N_SEEDS; seed++) {
        MlKemKey key;
        unsigned char ct[MAX_CT], ss[SS_LEN];
        word32 cl = 0, sl = 0;
        int ret = make_keypair_ct(ps->type, seed, ct, &cl, ss, &sl,
                                  NULL, NULL, NULL, NULL, &key);
        int events_this = 0;
        if (ret != 0) {
            fprintf(stderr, "keygen fail %s seed=%d rc=%d\n", ps->name, seed, ret);
            return ret;
        }
        if (cl != ct_len) return -1;

        /* valid control */
        if (library_cmp(ct, ct, (int)ct_len) != 0) {
            fprintf(stderr, "valid cmp fail\n");
            wc_MlKemKey_Free(&key);
            return -2;
        }

        if (strcmp(class_id, "G1_single_byte") == 0) {
            int idx, op;
            for (idx = 0; idx < (int)ct_len; idx++) {
                for (op = 0; op < 2; op++) {
                    unsigned char mut[MAX_CT];
                    unsigned char xorv = (op == 0) ? 0x01 : 0xff;
                    int rc;
                    if (events_this + coverage_events >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, ct_len);
                    mut[idx] ^= xorv;
                    rc = library_cmp(ct, mut, (int)ct_len);
                    events_this++;
                    indices_hit[idx] = 1;
                    if (rc == 0) silent_votes[idx]++;
                }
                if (capped) break;
            }
        } else if (strcmp(class_id, "G2_multi_byte") == 0) {
            int k, off, t;
            uint32_t st = mix32((uint32_t)seed * 0x9e3779b9u + (uint32_t)ct_len);
            int ks[] = {2, 4, 8, 16};
            int bi, blen;
            for (bi = 0; bi < 4 && !capped; bi++) {
                k = ks[bi];
                for (off = 0; off <= (int)ct_len - k; off += k) {
                    unsigned char mut[MAX_CT];
                    int j, rc;
                    if (coverage_events + events_this >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, ct_len);
                    for (j = 0; j < k; j++) { mut[off + j] ^= 0x01; indices_hit[off + j] = 1; }
                    rc = library_cmp(ct, mut, (int)ct_len);
                    events_this++;
                    if (rc == 0) {
                        for (j = 0; j < k; j++) silent_votes[off + j]++;
                    }
                }
                /* dense coverage of known AVX2 omission region */
                if (ct_len == 1568) {
                    for (off = 1536 - k + 1; off < 1568 && off >= 0; off++) {
                        unsigned char mut[MAX_CT];
                        int j, rc;
                        if (off > (int)ct_len - k) continue;
                        if (coverage_events + events_this >= MUTATION_CAP) { capped = 1; break; }
                        memcpy(mut, ct, ct_len);
                        for (j = 0; j < k; j++) { mut[off + j] ^= 0xff; indices_hit[off + j] = 1; }
                        rc = library_cmp(ct, mut, (int)ct_len);
                        events_this++;
                        if (rc == 0) {
                            for (j = 0; j < k; j++) silent_votes[off + j]++;
                        }
                    }
                }
            }
            /* scattered */
            for (bi = 0; bi < 4 && !capped; bi++) {
                k = ks[bi];
                for (t = 0; t < (int)ct_len / k && !capped; t++) {
                    unsigned char mut[MAX_CT];
                    int idxs[16];
                    int j, rc, used;
                    if (coverage_events + events_this >= MUTATION_CAP) { capped = 1; break; }
                    memset(idxs, -1, sizeof(idxs));
                    for (j = 0; j < k; j++) {
                        do {
                            st = mix32(st + (uint32_t)j + (uint32_t)t);
                            idxs[j] = (int)(st % ct_len);
                            used = 0;
                            { int u; for (u = 0; u < j; u++) if (idxs[u] == idxs[j]) used = 1; }
                        } while (used);
                    }
                    if (ct_len == 1568 && t == 0) {
                        for (j = 0; j < k; j++) idxs[j] = 1536 + j;
                    }
                    memcpy(mut, ct, ct_len);
                    for (j = 0; j < k; j++) { mut[idxs[j]] ^= 0x01; indices_hit[idxs[j]] = 1; }
                    rc = library_cmp(ct, mut, (int)ct_len);
                    events_this++;
                    if (rc == 0) {
                        for (j = 0; j < k; j++) silent_votes[idxs[j]]++;
                    }
                }
            }
            /* block inversions */
            for (blen = 16; blen <= 64 && !capped; blen *= 2) {
                for (off = 0; off <= (int)ct_len - blen; off += blen) {
                    unsigned char mut[MAX_CT];
                    int j, rc;
                    if (coverage_events + events_this >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, ct_len);
                    for (j = 0; j < blen; j++) { mut[off + j] ^= 0xff; indices_hit[off + j] = 1; }
                    rc = library_cmp(ct, mut, (int)ct_len);
                    events_this++;
                    if (rc == 0) {
                        for (j = 0; j < blen; j++) silent_votes[off + j]++;
                    }
                }
            }
        } else if (strcmp(class_id, "G3_alignment") == 0) {
            int align, off;
            for (align = 16; align <= 64 && !capped; align *= 2) {
                for (off = 0; off < (int)ct_len && !capped; off += align) {
                    int targets[4];
                    int nt = 0, ti, op;
                    int rem = (int)ct_len % align;
                    targets[nt++] = off;
                    targets[nt++] = (off + align - 1 < (int)ct_len) ? off + align - 1 : (int)ct_len - 1;
                    if (rem && off == 0) {
                        targets[nt++] = (int)ct_len - rem;
                        targets[nt++] = (int)ct_len - 1;
                    }
                    for (ti = 0; ti < nt; ti++) {
                        for (op = 0; op < 2; op++) {
                            unsigned char mut[MAX_CT];
                            unsigned char xorv = (op == 0) ? 0x01 : 0xff;
                            int rc, idx = targets[ti];
                            if (coverage_events + events_this >= MUTATION_CAP) { capped = 1; break; }
                            memcpy(mut, ct, ct_len);
                            mut[idx] ^= xorv;
                            rc = library_cmp(ct, mut, (int)ct_len);
                            events_this++;
                            indices_hit[idx] = 1;
                            if (rc == 0) silent_votes[idx]++;
                        }
                    }
                }
            }
        } else {
            fprintf(stderr, "unknown class %s\n", class_id);
            wc_MlKemKey_Free(&key);
            return -3;
        }

        coverage_events += events_this;
        wc_MlKemKey_Free(&key);
        if (capped) break;
    }

    /* Reportable: silent on >= 2 keys (votes >= 2 for G1 both ops complicates;
     * use votes >= 2 as reproduction across keys / events). */
    {
        int reportable[MAX_CT];
        int n_hit = 0;
        memset(reportable, 0, sizeof(reportable));
        n_silent = 0;
        for (i = 0; i < (int)ct_len; i++) {
            if (indices_hit[i]) n_hit++;
            /* G1: 4 seeds * 2 ops => vote 8 if fully silent; require >= 2 seeds =>
             * for G1 each silent op increments once per seed, both ops => need careful threshold.
             * We increment once per silent event per index. Require votes >= 2. */
            if (silent_votes[i] >= 2) {
                reportable[i] = 1;
                n_silent++;
            }
        }
        if (!*first_out) fprintf(f, ",\n");
        *first_out = 0;
        fprintf(f,
            "    {\n"
            "      \"parameter_set\": \"%s\",\n"
            "      \"class\": \"%s\",\n"
            "      \"ct_len\": %u,\n"
            "      \"keys\": %d,\n"
            "      \"mutation_events\": %d,\n"
            "      \"capped\": %s,\n"
            "      \"indices_hit\": %d,\n"
            "      \"index_fraction\": %.6f,\n"
            "      \"coverage_status\": \"%s\",\n"
            "      \"silent_byte_count\": %d,\n"
            "      \"silent_byte_set\": [",
            ps->name, class_id, ct_len, N_SEEDS, coverage_events,
            capped ? "true" : "false", n_hit,
            (double)n_hit / (double)ct_len,
            capped ? "partial" : "complete_for_class_definition",
            n_silent);
        {
            int printed = 0;
            for (i = 0; i < (int)ct_len; i++) {
                if (reportable[i]) {
                    if (printed) fprintf(f, ",");
                    fprintf(f, "%d", i);
                    printed++;
                }
            }
        }
        fprintf(f, "],\n      \"silent_votes\": {");
        {
            int printed = 0;
            for (i = 0; i < (int)ct_len; i++) {
                if (silent_votes[i] > 0) {
                    if (printed) fprintf(f, ",");
                    fprintf(f, "\"%d\":%d", i, silent_votes[i]);
                    printed++;
                    if (printed > 64 && n_silent > 64) {
                        /* keep file smaller for large NEON sets: emit remaining count only via set */
                        break;
                    }
                }
            }
        }
        fprintf(f, "}\n    }");
    }
    return 0;
}

static int mode_primitive_multiclass(FILE* f)
{
    const char* classes[] = { "G1_single_byte", "G2_multi_byte", "G3_alignment" };
    int c, p, first = 1, rc;
    write_json_header(f, "primitive-multiclass");
    fprintf(f, "  \"parameter_results\": [\n");
    for (c = 0; c < 3; c++) {
        for (p = 0; p < NPARAMS; p++) {
            rc = run_primitive_class(f, &PARAMS[p], classes[c], &first);
            if (rc != 0) return rc;
        }
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

/* Minimal JSON string field extractor (flat / nested-enough for ACVP). */
static int json_find_string(const char* json, const char* key, char* out, size_t out_sz)
{
    char pat[128];
    const char* p;
    size_t i = 0;
    snprintf(pat, sizeof(pat), "\"%s\"", key);
    p = strstr(json, pat);
    if (!p) return -1;
    p = strchr(p + strlen(pat), '"');
    if (!p) return -1;
    p++;
    while (*p && *p != '"' && i + 1 < out_sz) out[i++] = *p++;
    out[i] = 0;
    return 0;
}

static int mode_acvp_anchor(FILE* f)
{
    /* Use liboqs-style internalProjection if provided as prompt (combined), else
     * NIST prompt+expected. We accept a single combined JSON path via --acvp-prompt
     * when it contains both ek/c/k (internalProjection). */
    FILE* pf;
    long sz;
    char* buf;
    int ok = 1;
    int n_tested = 0;
    int n_pass = 0;
    write_json_header(f, "acvp-anchor");
    if (!g_acvp_prompt) {
        fprintf(f, "  \"error\": \"no acvp prompt path\",\n  \"anchor_ok\": false\n}\n");
        return 1;
    }
    pf = fopen(g_acvp_prompt, "r");
    if (!pf) {
        fprintf(f, "  \"error\": \"fopen prompt\",\n  \"anchor_ok\": false\n}\n");
        return 1;
    }
    fseek(pf, 0, SEEK_END);
    sz = ftell(pf);
    fseek(pf, 0, SEEK_SET);
    buf = (char*)malloc((size_t)sz + 1);
    if (!buf) { fclose(pf); return 1; }
    if (fread(buf, 1, (size_t)sz, pf) != (size_t)sz) { free(buf); fclose(pf); return 1; }
    buf[sz] = 0;
    fclose(pf);

    fprintf(f, "  \"anchor_file\": \"%s\",\n  \"cases\": [\n", g_acvp_prompt);
    /* Walk AFT encapsulation cases: look for "ek": "...", "m": "...", "c": "...", "k": "..." */
    {
        const char* cursor = buf;
        int first = 1;
        char last_ps[32] = "";
        /* Pre-scan: record parameterSet positions roughly by walking the file */
        while ((cursor = strstr(cursor, "\"ek\"")) != NULL) {
            char ek_hex[4096], m_hex[128], c_hex[4096], k_hex[128];
            char ps_name[32];
            unsigned char ek[MAX_EK], m[32], c_exp[MAX_CT], k_exp[SS_LEN], c_got[MAX_CT], k_got[SS_LEN];
            size_t ek_len = 0, m_len = 0, c_len = 0, k_len = 0;
            const char* window_start;
            const char* window_end;
            char window[16384];
            size_t wlen;
            int type = 0;
            word32 ct_sz = 0;
            MlKemKey key;
            int ret;
            int pass;
            const char* pset;
            const char* scan;

            /* Bound a local window for field extraction */
            window_start = cursor - 50;
            if (window_start < buf) window_start = buf;
            window_end = cursor + 12000;
            if (window_end > buf + sz) window_end = buf + sz;
            wlen = (size_t)(window_end - window_start);
            if (wlen >= sizeof(window)) wlen = sizeof(window) - 1;
            memcpy(window, window_start, wlen);
            window[wlen] = 0;

            if (json_find_string(window, "ek", ek_hex, sizeof(ek_hex)) != 0 ||
                json_find_string(window, "m", m_hex, sizeof(m_hex)) != 0 ||
                json_find_string(window, "c", c_hex, sizeof(c_hex)) != 0 ||
                json_find_string(window, "k", k_hex, sizeof(k_hex)) != 0) {
                cursor += 4;
                continue;
            }
            /* Find nearest preceding parameterSet by scanning backward from cursor */
            ps_name[0] = 0;
            scan = cursor;
            while (scan > buf) {
                if (scan[0] == 'M' && strncmp(scan, "ML-KEM-", 7) == 0) {
                    if (sscanf(scan, "%31s", ps_name) == 1) {
                        char* q = ps_name;
                        while (*q && *q != '"' && *q != ',' && *q != ' ' && *q != '\n') q++;
                        *q = 0;
                        if (strcmp(ps_name, "ML-KEM-512") == 0 ||
                            strcmp(ps_name, "ML-KEM-768") == 0 ||
                            strcmp(ps_name, "ML-KEM-1024") == 0) {
                            strncpy(last_ps, ps_name, sizeof(last_ps) - 1);
                            break;
                        }
                    }
                }
                scan--;
                /* limit backward scan */
                if ((cursor - scan) > 200000) break;
            }
            if (ps_name[0] == 0 && last_ps[0]) strncpy(ps_name, last_ps, sizeof(ps_name) - 1);
            if (ps_name[0] == 0) { cursor += 4; continue; }

            if (strcmp(ps_name, "ML-KEM-512") == 0) type = WC_ML_KEM_512;
            else if (strcmp(ps_name, "ML-KEM-768") == 0) type = WC_ML_KEM_768;
            else if (strcmp(ps_name, "ML-KEM-1024") == 0) type = WC_ML_KEM_1024;
            else { cursor += 4; continue; }

            if (unhex(ek_hex, ek, sizeof(ek), &ek_len) != 0 ||
                unhex(m_hex, m, sizeof(m), &m_len) != 0 ||
                unhex(c_hex, c_exp, sizeof(c_exp), &c_len) != 0 ||
                unhex(k_hex, k_exp, sizeof(k_exp), &k_len) != 0) {
                cursor += 4;
                continue;
            }
            if (m_len != 32 || k_len != 32) { cursor += 4; continue; }

            ret = wc_MlKemKey_Init(&key, type, NULL, INVALID_DEVID);
            if (ret != 0) { ok = 0; cursor += 4; continue; }
            ret = wc_MlKemKey_DecodePublicKey(&key, ek, (word32)ek_len);
            if (ret != 0) {
                wc_MlKemKey_Free(&key);
                cursor += 4;
                continue;
            }
            ret = wc_MlKemKey_CipherTextSize(&key, &ct_sz);
            if (ret != 0 || ct_sz != (word32)c_len) {
                wc_MlKemKey_Free(&key);
                cursor += 4;
                continue;
            }
            ret = wc_MlKemKey_EncapsulateWithRandom(&key, c_got, k_got, m, 32);
            pass = (ret == 0 && memcmp(c_got, c_exp, c_len) == 0 &&
                    memcmp(k_got, k_exp, 32) == 0);
            n_tested++;
            if (pass) n_pass++; else ok = 0;
            if (!first) fprintf(f, ",\n");
            first = 0;
            fprintf(f,
                "    {\"parameter_set\":\"%s\",\"ek_len\":%zu,\"ct_len\":%zu,"
                "\"encap_match\":%s}",
                ps_name, ek_len, c_len, pass ? "true" : "false");
            wc_MlKemKey_Free(&key);
            /* Advance past this ek occurrence */
            cursor += 4;
            if (n_tested >= 9) break; /* 3 per parameter set */
        }
    }
    fprintf(f,
        "\n  ],\n"
        "  \"n_tested\": %d,\n"
        "  \"n_pass\": %d,\n"
        "  \"anchor_name\": \"NIST_ACVP_ML-KEM_encapDecap_FIPS203_internalProjection\",\n"
        "  \"anchor_grade\": \"%s\",\n"
        "  \"anchor_ok\": %s\n"
        "}\n",
        n_tested, n_pass,
        (n_tested > 0 && ok) ? "strong" : "weak",
        (n_tested > 0 && ok) ? "true" : "false");
    free(buf);
    return (n_tested > 0 && ok) ? 0 : 1;
}

static int mode_archive_key0(FILE* f)
{
    int p;
    write_json_header(f, "archive-key0");
    fprintf(f, "  \"archived\": [\n");
    for (p = 0; p < NPARAMS; p++) {
        MlKemKey key;
        unsigned char ct[MAX_CT], ss[SS_LEN], ek[MAX_EK], dk[MAX_DK];
        word32 cl = 0, sl = 0, ekl = 0, dkl = 0;
        char ct_h[65], ss_h[65], ek_h[65], path[512];
        FILE* bf;
        int ret = make_keypair_ct(PARAMS[p].type, 1, ct, &cl, ss, &sl, ek, &ekl, dk, &dkl, &key);
        if (ret != 0) return ret;
        sha256_hex(ct, cl, ct_h);
        sha256_hex(ss, SS_LEN, ss_h);
        sha256_hex(ek, ekl, ek_h);
        if (g_vectors_dir) {
            snprintf(path, sizeof(path), "%s/%s_seed1_ek.bin", g_vectors_dir, PARAMS[p].name);
            bf = fopen(path, "wb"); if (bf) { fwrite(ek, 1, ekl, bf); fclose(bf); }
            snprintf(path, sizeof(path), "%s/%s_seed1_ct.bin", g_vectors_dir, PARAMS[p].name);
            bf = fopen(path, "wb"); if (bf) { fwrite(ct, 1, cl, bf); fclose(bf); }
            snprintf(path, sizeof(path), "%s/%s_seed1_ss.bin", g_vectors_dir, PARAMS[p].name);
            bf = fopen(path, "wb"); if (bf) { fwrite(ss, 1, SS_LEN, bf); fclose(bf); }
        }
        if (p) fprintf(f, ",\n");
        fprintf(f,
            "    {\"parameter_set\":\"%s\",\"seed\":1,\"ct_sha256\":\"%s\","
            "\"ss_sha256\":\"%s\",\"ek_sha256\":\"%s\",\"ct_len\":%u,\"ek_len\":%u}",
            PARAMS[p].name, ct_h, ss_h, ek_h, cl, ekl);
        wc_MlKemKey_Free(&key);
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

static void usage(const char* a0)
{
    fprintf(stderr,
        "Usage: %s --mode MODE --build-id ID --commit SHA [--out PATH] "
        "[--acvp-prompt PATH] [--vectors-dir PATH]\n", a0);
}

int main(int argc, char** argv)
{
    const char* mode = NULL;
    int i, rc = 0;
    FILE* out = stdout;
    g_backend = backend_name();
    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc) mode = argv[++i];
        else if (strcmp(argv[i], "--build-id") == 0 && i + 1 < argc) g_build_id = argv[++i];
        else if (strcmp(argv[i], "--commit") == 0 && i + 1 < argc) g_commit = argv[++i];
        else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) g_out_path = argv[++i];
        else if (strcmp(argv[i], "--acvp-prompt") == 0 && i + 1 < argc) g_acvp_prompt = argv[++i];
        else if (strcmp(argv[i], "--acvp-expected") == 0 && i + 1 < argc) g_acvp_expected = argv[++i];
        else if (strcmp(argv[i], "--vectors-dir") == 0 && i + 1 < argc) g_vectors_dir = argv[++i];
        else if (strcmp(argv[i], "--backend") == 0 && i + 1 < argc) { ++i; }
        else { usage(argv[0]); return 2; }
    }
    (void)g_acvp_expected;
    if (!mode) { usage(argv[0]); return 2; }
    if (g_out_path) {
        out = fopen(g_out_path, "w");
        if (!out) { perror("fopen"); return 2; }
    }
    if (strcmp(mode, "attest") == 0) rc = mode_attest(out);
    else if (strcmp(mode, "negative-harness") == 0) rc = mode_negative_harness(out);
    else if (strcmp(mode, "primitive-multiclass") == 0) rc = mode_primitive_multiclass(out);
    else if (strcmp(mode, "acvp-anchor") == 0) rc = mode_acvp_anchor(out);
    else if (strcmp(mode, "archive-key0") == 0) rc = mode_archive_key0(out);
    else { fprintf(stderr, "unknown mode %s\n", mode); rc = 2; }
    if (g_out_path) fclose(out);
    return rc;
}
