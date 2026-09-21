/*
 * Library-facing adequacy probe for EXP-MLKEM-006.
 *
 * Loads the independently injected defective comparator via dlopen/dlsym
 * (or direct link) and exercises G1/G2/G3 through that library entry only.
 * Attestation records the resolved symbol path so detection is not a
 * harness-local Python tautology.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define CT_LEN 1568
#define R_START 1536
#define R_END 1568
#define N_SEEDS 4

typedef int (*compare_fn)(const uint8_t *, const uint8_t *, size_t);
typedef const char *(*id_fn)(void);

static compare_fn g_cmp = NULL;
static id_fn g_id = NULL;
static void *g_handle = NULL;
static char g_lib_path[1024];
static const char *g_out = NULL;
static const char *g_mode = "attest";

static void die(const char *m)
{
    fprintf(stderr, "FATAL: %s\n", m);
    exit(2);
}

static void fill_base(int seed, uint8_t *buf, size_t n)
{
    size_t i;
    for (i = 0; i < n; i++)
        buf[i] = (uint8_t)((seed * 17 + (int)i * 31 + 0x5a) & 0xff);
}

static int load_lib(const char *path)
{
    strncpy(g_lib_path, path, sizeof(g_lib_path) - 1);
    g_handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!g_handle) {
        fprintf(stderr, "dlopen failed: %s\n", dlerror());
        return 1;
    }
    g_cmp = (compare_fn)dlsym(g_handle, "mlkem_injected_defective_compare");
    g_id = (id_fn)dlsym(g_handle, "mlkem_injected_defective_compare_id");
    if (!g_cmp)
        die("dlsym mlkem_injected_defective_compare failed");
    return 0;
}

static int mode_attest(FILE *f)
{
    uint8_t a[CT_LEN], b[CT_LEN];
    int eq, neq_out, silent_one, detect_multi;
    fill_base(1, a, CT_LEN);
    memcpy(b, a, CT_LEN);
    eq = g_cmp(a, b, CT_LEN);
    b[10] ^= 1;
    neq_out = g_cmp(a, b, CT_LEN);
    memcpy(b, a, CT_LEN);
    b[R_START] ^= 1;
    silent_one = g_cmp(a, b, CT_LEN);
    memcpy(b, a, CT_LEN);
    b[R_START] ^= 1;
    b[R_START + 1] ^= 1;
    detect_multi = g_cmp(a, b, CT_LEN);

    fprintf(f,
            "{\n"
            "  \"experiment_id\": \"EXP-MLKEM-006\",\n"
            "  \"mode\": \"attest\",\n"
            "  \"control_id\": \"CTRL-LIBRARY-FACING-ADEQUACY\",\n"
            "  \"interposition\": {\n"
            "    \"method\": \"dlopen_injected_comparator_object\",\n"
            "    \"library_path\": \"%s\",\n"
            "    \"compare_symbol\": \"mlkem_injected_defective_compare\",\n"
            "    \"object_id\": \"%s\",\n"
            "    \"library_source_modified\": false\n"
            "  },\n"
            "  \"self_test\": {\n"
            "    \"equal_rc\": %d,\n"
            "    \"outside_R_unequal_rc\": %d,\n"
            "    \"single_byte_in_R_rc\": %d,\n"
            "    \"two_byte_in_R_rc\": %d\n"
            "  },\n"
            "  \"attested\": %s,\n"
            "  \"library_call_path_exercised\": true\n"
            "}\n",
            g_lib_path,
            g_id ? g_id() : "unknown",
            eq, neq_out, silent_one, detect_multi,
            (eq == 0 && neq_out != 0 && silent_one == 0 && detect_multi != 0) ? "true" : "false");
    return (eq == 0 && neq_out != 0 && silent_one == 0 && detect_multi != 0) ? 0 : 1;
}

static int mode_grid(FILE *f)
{
    int seed, idx, xorv;
    uint8_t base[CT_LEN], mut[CT_LEN];
    int silent[CT_LEN];
    int detected[CT_LEN];
    int i;

    memset(silent, 0, sizeof(silent));
    memset(detected, 0, sizeof(detected));

    fprintf(f,
            "{\n"
            "  \"experiment_id\": \"EXP-MLKEM-006\",\n"
            "  \"mode\": \"library_facing_grid\",\n"
            "  \"control_id\": \"CTRL-LIBRARY-FACING-ADEQUACY\",\n"
            "  \"interposition\": {\n"
            "    \"method\": \"dlopen_injected_comparator_object\",\n"
            "    \"library_path\": \"%s\",\n"
            "    \"compare_symbol\": \"mlkem_injected_defective_compare\",\n"
            "    \"object_id\": \"%s\"\n"
            "  },\n"
            "  \"parameter_set\": \"ML-KEM-1024\",\n"
            "  \"ct_len\": %d,\n"
            "  \"region_R\": [%d, %d],\n"
            "  \"observations\": [\n",
            g_lib_path, g_id ? g_id() : "unknown", CT_LEN, R_START, R_END - 1);

    int first = 1;
    /* G1: every index, xor 0x01 and 0xff */
    for (seed = 1; seed <= N_SEEDS; seed++) {
        fill_base(seed, base, CT_LEN);
        for (idx = 0; idx < CT_LEN; idx++) {
            for (xorv = 0; xorv < 2; xorv++) {
                int rc;
                memcpy(mut, base, CT_LEN);
                mut[idx] ^= (xorv == 0) ? 0x01 : 0xff;
                rc = g_cmp(base, mut, CT_LEN);
                if (!first)
                    fprintf(f, ",\n");
                first = 0;
                fprintf(f,
                        "    {\"class\":\"G1_single_byte\",\"seed\":%d,\"indices\":[%d],"
                        "\"xor\":%d,\"compare_rc\":%d}",
                        seed, idx, (xorv == 0) ? 1 : 255, rc);
                if (rc == 0)
                    silent[idx] = 1;
                else
                    detected[idx] = 1;
            }
        }
    }

    /* G2 seeded multi-byte patterns confined to R */
    for (seed = 1; seed <= N_SEEDS; seed++) {
        int j;
        int rc;
        fill_base(seed, base, CT_LEN);
        memcpy(mut, base, CT_LEN);
        for (j = 0; j < 8; j++)
            mut[R_START + j] ^= 0x01;
        rc = g_cmp(base, mut, CT_LEN);
        fprintf(f,
                ",\n    {\"class\":\"G2_multi_byte\",\"seed\":%d,\"kind\":\"contiguous_k8_in_R\","
                "\"indices\":[%d,%d,%d,%d,%d,%d,%d,%d],\"compare_rc\":%d}",
                seed, R_START, R_START + 1, R_START + 2, R_START + 3, R_START + 4,
                R_START + 5, R_START + 6, R_START + 7, rc);

        memcpy(mut, base, CT_LEN);
        mut[R_START] ^= 0xff;
        mut[R_START + 7] ^= 0xff;
        mut[R_START + 15] ^= 0xff;
        mut[R_START + 31] ^= 0xff;
        rc = g_cmp(base, mut, CT_LEN);
        fprintf(f,
                ",\n    {\"class\":\"G2_multi_byte\",\"seed\":%d,\"kind\":\"scattered_k4_in_R\","
                "\"indices\":[%d,%d,%d,%d],\"compare_rc\":%d}",
                seed, R_START, R_START + 7, R_START + 15, R_START + 31, rc);
    }

    /* G3 alignment / lane-boundary pairs in R */
    for (seed = 1; seed <= N_SEEDS; seed++) {
        int rc;
        fill_base(seed, base, CT_LEN);
        memcpy(mut, base, CT_LEN);
        mut[R_START] ^= 0x01;
        mut[R_END - 1] ^= 0x01;
        rc = g_cmp(base, mut, CT_LEN);
        fprintf(f,
                ",\n    {\"class\":\"G3_alignment\",\"seed\":%d,\"kind\":\"align_pair_R_start_and_end\","
                "\"indices\":[%d,%d],\"compare_rc\":%d}",
                seed, R_START, R_END - 1, rc);

        memcpy(mut, base, CT_LEN);
        mut[1536] ^= 0xff;
        mut[1552] ^= 0xff;
        rc = g_cmp(base, mut, CT_LEN);
        fprintf(f,
                ",\n    {\"class\":\"G3_alignment\",\"seed\":%d,\"kind\":\"align_32_lane_pair\","
                "\"indices\":[1536,1552],\"compare_rc\":%d}",
                seed, rc);
    }

    fprintf(f, "\n  ],\n  \"g1_index_flags\": [\n");
    for (i = 0; i < CT_LEN; i++) {
        fprintf(f, "    {\"index\":%d,\"silent_flag\":%s,\"detected_flag\":%s}%s\n",
                i, silent[i] ? "true" : "false", detected[i] ? "true" : "false",
                (i + 1 < CT_LEN) ? "," : "");
    }
    fprintf(f, "  ]\n}\n");
    return 0;
}

int main(int argc, char **argv)
{
    const char *lib = NULL;
    int i;
    FILE *f;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--lib") == 0 && i + 1 < argc)
            lib = argv[++i];
        else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc)
            g_out = argv[++i];
        else if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc)
            g_mode = argv[++i];
    }
    if (!lib || !g_out)
        die("usage: adequacy_probe --lib PATH --mode attest|grid --out PATH");
    if (load_lib(lib) != 0)
        return 2;
    f = fopen(g_out, "w");
    if (!f)
        die("open out");
    if (strcmp(g_mode, "attest") == 0) {
        int rc = mode_attest(f);
        fclose(f);
        return rc;
    }
    if (strcmp(g_mode, "grid") == 0) {
        int rc = mode_grid(f);
        fclose(f);
        return rc;
    }
    fclose(f);
    die("unknown mode");
    return 2;
}
