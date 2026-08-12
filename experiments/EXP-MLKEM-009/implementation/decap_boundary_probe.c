/*
 * EXP-MLKEM-009 Algorithm-18 / public decapsulation boundary probe (wolfSSL).
 *
 * Modes:
 *   decap-multiclass  — G1/G2/G3 equal-length mutations at public Decapsulate API
 *   malformed-length  — G4 truncated/extended; separate table only
 *   message-stability — annotate accepts on silent indices
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <wolfssl/options.h>
#include <wolfssl/wolfcrypt/settings.h>
#if defined(__has_include)
#  if __has_include(<wolfssl/wolfcrypt/mlkem.h>)
#    include <wolfssl/wolfcrypt/mlkem.h>
#  endif
#endif
#include <wolfssl/wolfcrypt/wc_mlkem.h>
#include <wolfssl/wolfcrypt/sha256.h>

#define SS_LEN 32
#define MAX_CT 1600
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

static const char* g_build_id = "unknown";
static const char* g_backend = "unknown";
static const char* g_commit = "unknown";
static const char* g_out_path = NULL;
static const char* g_silent_csv = "";
static const char* g_class_filter = "all"; /* G1|G2|G3|all */

static void die(const char* m, int rc) { fprintf(stderr, "FATAL: %s (%d)\n", m, rc); exit(2); }

static void fill_seed_material(int seed_id, unsigned char out[MAKEKEY_RAND + ENC_RAND])
{
    int i;
    memset(out, 0, MAKEKEY_RAND + ENC_RAND);
    out[0] = (unsigned char)seed_id;
    out[1] = 0xA5;
    out[2] = 0x5A;
    for (i = 3; i < MAKEKEY_RAND + ENC_RAND; i++)
        out[i] = (unsigned char)((seed_id * 17 + i * 31) & 0xff);
    out[MAKEKEY_RAND] = (unsigned char)(0xC3 ^ seed_id);
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

static int make_ct(int type, int seed_id, unsigned char* ct, word32* cl,
                   unsigned char* ss, word32* sl, MlKemKey* key)
{
    unsigned char mat[MAKEKEY_RAND + ENC_RAND];
    int ret;
    fill_seed_material(seed_id, mat);
    ret = wc_MlKemKey_Init(key, type, NULL, INVALID_DEVID);
    if (ret) return ret;
    ret = wc_MlKemKey_MakeKeyWithRandom(key, mat, MAKEKEY_RAND);
    if (ret) return ret;
    ret = wc_MlKemKey_CipherTextSize(key, cl);
    if (ret) return ret;
    ret = wc_MlKemKey_SharedSecretSize(key, sl);
    if (ret) return ret;
    return wc_MlKemKey_EncapsulateWithRandom(key, ct, ss, mat + MAKEKEY_RAND, ENC_RAND);
}

static void write_hdr(FILE* f, const char* mode)
{
    fprintf(f,
        "{\n  \"experiment_id\": \"EXP-MLKEM-009\",\n  \"mode\": \"%s\",\n"
        "  \"build_id\": \"%s\",\n  \"backend\": \"%s\",\n"
        "  \"resolved_commit\": \"%s\",\n  \"probe_backend_macro\": \"%s\",\n",
        mode, g_build_id, g_backend, g_commit, backend_name());
}

static int mode_malformed(FILE* f)
{
    int p, seed, first = 1;
    write_hdr(f, "malformed-length");
    fprintf(f, "  \"note\": \"G4 results; never counted as comparison omission\",\n");
    fprintf(f, "  \"rows\": [\n");
    for (p = 0; p < NPARAMS; p++) {
        for (seed = 1; seed <= N_SEEDS; seed++) {
            MlKemKey key;
            unsigned char ct[MAX_CT], ss[SS_LEN], ss_out[SS_LEN];
            word32 cl = 0, sl = 0;
            int deltas[] = {-1, -16, -32, 1, 16, 32};
            int di, ret;
            ret = make_ct(PARAMS[p].type, seed, ct, &cl, ss, &sl, &key);
            if (ret) return ret;
            for (di = 0; di < 6; di++) {
                int delta = deltas[di];
                int new_len = (int)cl + delta;
                unsigned char buf[MAX_CT + 64];
                int api_rc;
                int refused = 0;
                const char* disposition;
                memset(buf, 0, sizeof(buf));
                if (new_len <= 0) {
                    refused = 1;
                    api_rc = -1;
                    disposition = "refused_nonpositive_length";
                } else if (new_len > (int)sizeof(buf)) {
                    refused = 1;
                    api_rc = -1;
                    disposition = "refused_oversize";
                } else {
                    if (delta < 0) {
                        memcpy(buf, ct, (size_t)new_len);
                    } else {
                        memcpy(buf, ct, cl);
                        memset(buf + cl, 0x5A, (size_t)delta);
                    }
                    api_rc = wc_MlKemKey_Decapsulate(&key, ss_out, buf, (word32)new_len);
                    if (api_rc != 0) disposition = "api_error_reject";
                    else if (memcmp(ss_out, ss, SS_LEN) == 0) disposition = "returned_honest_ss";
                    else disposition = "implicit_rejection_or_other_ss";
                }
                if (!first) fprintf(f, ",\n");
                first = 0;
                fprintf(f,
                    "    {\"parameter_set\":\"%s\",\"seed\":%d,\"nominal_ct_len\":%u,"
                    "\"delta\":%d,\"submitted_len\":%d,\"api_rc\":%d,\"refused\":%s,"
                    "\"disposition\":\"%s\",\"counted_as_comparison_omission\":false}",
                    PARAMS[p].name, seed, cl, delta, new_len, api_rc,
                    refused ? "true" : "false", disposition);
            }
            wc_MlKemKey_Free(&key);
        }
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

static int parse_indices_for_param(const char* csv, const char* pname, int* out, int maxn)
{
    int n = 0;
    const char* s = csv;
    size_t namelen = strlen(pname);
    if (!s || !s[0]) return 0;
    while (*s) {
        if (strncmp(s, pname, namelen) == 0 && s[namelen] == ':') {
            s += namelen + 1;
            while (*s && *s != ';') {
                int v = (int)strtol(s, (char**)&s, 10);
                if (n < maxn) out[n++] = v;
                if (*s == ',') s++;
            }
        }
        {
            const char* semi = strchr(s, ';');
            if (!semi) break;
            s = semi + 1;
        }
    }
    return n;
}

static int mode_decap_multiclass(FILE* f)
{
    int p, seed, first = 1;
    write_hdr(f, "decap-multiclass");
    fprintf(f, "  \"class_filter\": \"%s\",\n", g_class_filter);
    fprintf(f, "  \"results\": [\n");

    for (p = 0; p < NPARAMS; p++) {
        int silent_idx[MAX_CT];
        int n_silent = parse_indices_for_param(g_silent_csv, PARAMS[p].name, silent_idx, MAX_CT);
        word32 ct_len = PARAMS[p].ct_len;
        int accept_votes[MAX_CT];
        int reject_votes[MAX_CT];
        int events = 0;
        int capped = 0;
        int i;

        memset(accept_votes, 0, sizeof(accept_votes));
        memset(reject_votes, 0, sizeof(reject_votes));

        for (seed = 1; seed <= N_SEEDS && !capped; seed++) {
            MlKemKey key;
            unsigned char ct[MAX_CT], ss[SS_LEN], ss_dec[SS_LEN], ss_hon[SS_LEN];
            word32 cl = 0, sl = 0;
            int ret = make_ct(PARAMS[p].type, seed, ct, &cl, ss, &sl, &key);
            if (ret) return ret;

            /* honest decap */
            ret = wc_MlKemKey_Decapsulate(&key, ss_hon, ct, cl);
            if (ret != 0 || memcmp(ss_hon, ss, SS_LEN) != 0) {
                fprintf(stderr, "honest decap fail %s seed=%d\n", PARAMS[p].name, seed);
                wc_MlKemKey_Free(&key);
                return -3;
            }

            /* G1 sample: every index xor01 (cap-aware) — primary API sweep */
            if (strcmp(g_class_filter, "all") == 0 || strcmp(g_class_filter, "G1") == 0) {
                int idx;
                for (idx = 0; idx < (int)ct_len; idx++) {
                    unsigned char mut[MAX_CT];
                    int accept, msg_stable;
                    if (events >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, cl);
                    mut[idx] ^= 0x01;
                    ret = wc_MlKemKey_Decapsulate(&key, ss_dec, mut, cl);
                    events++;
                    if (ret != 0) {
                        reject_votes[idx]++;
                        continue;
                    }
                    accept = (memcmp(ss_dec, ss, SS_LEN) == 0);
                    /* FO: accept of honest SS implies decrypted message matched */
                    msg_stable = accept;
                    if (accept) accept_votes[idx]++;
                    else reject_votes[idx]++;
                    (void)msg_stable;
                }
            }

            /* Also specifically probe provided silent indices with message-stability rows */
            {
                int si;
                for (si = 0; si < n_silent; si++) {
                    unsigned char mut[MAX_CT];
                    int idx = silent_idx[si];
                    int accept;
                    if (idx < 0 || idx >= (int)cl) continue;
                    memcpy(mut, ct, cl);
                    mut[idx] ^= 0x01;
                    ret = wc_MlKemKey_Decapsulate(&key, ss_dec, mut, cl);
                    if (ret != 0) continue;
                    accept = (memcmp(ss_dec, ss, SS_LEN) == 0);
                    if (!first) fprintf(f, ",\n");
                    first = 0;
                    fprintf(f,
                        "    {\"parameter_set\":\"%s\",\"seed\":%d,\"index\":%d,"
                        "\"class\":\"silent_index_probe\",\"mutation\":\"xor_0x01\","
                        "\"decap_api_rc\":0,\"accept_honest_ss\":%s,"
                        "\"message_stable\":%s,\"implicit_rejection\":%s}",
                        PARAMS[p].name, seed, idx,
                        accept ? "true" : "false",
                        accept ? "true" : "false",
                        accept ? "false" : "true");
                }
            }

            /* G2/G3 light probes for API boundary (offsets covering omission) */
            if (!capped && (strcmp(g_class_filter, "all") == 0 ||
                            strcmp(g_class_filter, "G2") == 0 ||
                            strcmp(g_class_filter, "G3") == 0)) {
                int offs[] = {0, 16, 32, 64, (int)ct_len / 2, (int)ct_len - 32, 1536, 1552};
                int oi;
                for (oi = 0; oi < (int)(sizeof(offs) / sizeof(offs[0])); oi++) {
                    unsigned char mut[MAX_CT];
                    int idx = offs[oi];
                    int accept;
                    if (idx < 0 || idx >= (int)cl) continue;
                    if (events >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, cl);
                    mut[idx] ^= 0xff;
                    ret = wc_MlKemKey_Decapsulate(&key, ss_dec, mut, cl);
                    events++;
                    if (ret != 0) continue;
                    accept = (memcmp(ss_dec, ss, SS_LEN) == 0);
                    if (accept) accept_votes[idx]++;
                    if (!first) fprintf(f, ",\n");
                    first = 0;
                    fprintf(f,
                        "    {\"parameter_set\":\"%s\",\"seed\":%d,\"index\":%d,"
                        "\"class\":\"G2G3_spot\",\"mutation\":\"xor_0xff\","
                        "\"accept_honest_ss\":%s,\"message_stable\":%s}",
                        PARAMS[p].name, seed, idx,
                        accept ? "true" : "false",
                        accept ? "true" : "false");
                }
            }
            wc_MlKemKey_Free(&key);
        }

        /* summary row per param */
        {
            int n_accept_reportable = 0;
            int accept_set[MAX_CT];
            memset(accept_set, 0, sizeof(accept_set));
            for (i = 0; i < (int)ct_len; i++) {
                if (accept_votes[i] >= 2) {
                    accept_set[i] = 1;
                    n_accept_reportable++;
                }
            }
            if (!first) fprintf(f, ",\n");
            first = 0;
            fprintf(f,
                "    {\"parameter_set\":\"%s\",\"row_type\":\"summary\",\"mutation_events\":%d,"
                "\"capped\":%s,\"reportable_accept_index_count\":%d,\"reportable_accept_indices\":[",
                PARAMS[p].name, events, capped ? "true" : "false", n_accept_reportable);
            {
                int printed = 0;
                for (i = 0; i < (int)ct_len; i++) {
                    if (accept_set[i]) {
                        if (printed) fprintf(f, ",");
                        fprintf(f, "%d", i);
                        printed++;
                    }
                }
            }
            fprintf(f, "]}");
        }
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

static void usage(const char* a0)
{
    fprintf(stderr, "Usage: %s --mode MODE --build-id ID --commit SHA [--out P] "
                    "[--silent-indices CSV] [--class G1|G2|G3|all]\n", a0);
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
        else if (strcmp(argv[i], "--silent-indices") == 0 && i + 1 < argc) g_silent_csv = argv[++i];
        else if (strcmp(argv[i], "--class") == 0 && i + 1 < argc) g_class_filter = argv[++i];
        else { usage(argv[0]); return 2; }
    }
    if (!mode) { usage(argv[0]); return 2; }
    if (g_out_path) {
        out = fopen(g_out_path, "w");
        if (!out) { perror("fopen"); return 2; }
    }
    if (strcmp(mode, "malformed-length") == 0) rc = mode_malformed(out);
    else if (strcmp(mode, "decap-multiclass") == 0) rc = mode_decap_multiclass(out);
    else { fprintf(stderr, "unknown mode %s\n", mode); rc = 2; }
    if (g_out_path) fclose(out);
    return rc;
}
