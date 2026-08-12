/*
 * EXP-MLKEM-005 second-implementation probe (liboqs ML-KEM).
 * Primitive: pqcrystals_ml_kem_{512,768,1024}_{ref,avx2}_verify
 * Decapsulation: OQS_KEM_decaps (live dispatch)
 * Never modifies library comparison logic.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <oqs/oqs.h>

#define N_SEEDS 4
#define MUTATION_CAP 20000
#define MAX_CT 1568
#define SS_LEN 32

extern int pqcrystals_ml_kem_512_ref_verify(const uint8_t *a, const uint8_t *b, size_t len);
extern int pqcrystals_ml_kem_768_ref_verify(const uint8_t *a, const uint8_t *b, size_t len);
extern int pqcrystals_ml_kem_1024_ref_verify(const uint8_t *a, const uint8_t *b, size_t len);
extern int pqcrystals_ml_kem_512_avx2_verify(const uint8_t *a, const uint8_t *b, size_t len);
extern int pqcrystals_ml_kem_768_avx2_verify(const uint8_t *a, const uint8_t *b, size_t len);
extern int pqcrystals_ml_kem_1024_avx2_verify(const uint8_t *a, const uint8_t *b, size_t len);

typedef int (*verify_fn)(const uint8_t*, const uint8_t*, size_t);

static const char* g_build_id = "liboqs";
static const char* g_backend = "unknown";
static const char* g_commit = "unknown";
static const char* g_out_path = NULL;
static const char* g_acvp = NULL;
static int g_use_avx2 = 1;

static void die(const char* m, int rc) { fprintf(stderr, "FATAL: %s (%d)\n", m, rc); exit(2); }

static void fill_seed(int seed_id, uint8_t* buf, size_t n)
{
    size_t i;
    for (i = 0; i < n; i++) buf[i] = (uint8_t)((seed_id * 17 + (int)i * 31) & 0xff);
    buf[0] = (uint8_t)seed_id;
}

static verify_fn select_verify(const char* alg, size_t* ct_len)
{
    if (strcmp(alg, OQS_KEM_alg_ml_kem_512) == 0) {
        *ct_len = 768;
        return g_use_avx2 ? pqcrystals_ml_kem_512_avx2_verify : pqcrystals_ml_kem_512_ref_verify;
    }
    if (strcmp(alg, OQS_KEM_alg_ml_kem_768) == 0) {
        *ct_len = 1088;
        return g_use_avx2 ? pqcrystals_ml_kem_768_avx2_verify : pqcrystals_ml_kem_768_ref_verify;
    }
    if (strcmp(alg, OQS_KEM_alg_ml_kem_1024) == 0) {
        *ct_len = 1568;
        return g_use_avx2 ? pqcrystals_ml_kem_1024_avx2_verify : pqcrystals_ml_kem_1024_ref_verify;
    }
    return NULL;
}

static const char* algs[] = {
    OQS_KEM_alg_ml_kem_512,
    OQS_KEM_alg_ml_kem_768,
    OQS_KEM_alg_ml_kem_1024,
};
static const char* ps_names[] = { "ML-KEM-512", "ML-KEM-768", "ML-KEM-1024" };

static void hdr(FILE* f, const char* mode)
{
    fprintf(f,
        "{\n  \"experiment_id\": \"EXP-MLKEM-005\",\n  \"mode\": \"%s\",\n"
        "  \"build_id\": \"%s\",\n  \"backend\": \"%s\",\n"
        "  \"resolved_commit\": \"%s\",\n  \"implementation\": \"liboqs\",\n",
        mode, g_build_id, g_backend, g_commit);
}

static int mode_attest(FILE* f)
{
    size_t ct_len = 0;
    verify_fn v = select_verify(OQS_KEM_alg_ml_kem_512, &ct_len);
    uint8_t a[768], b[768];
    int eq, neq;
    memset(a, 0x5a, sizeof(a));
    memset(b, 0x5a, sizeof(b));
    eq = v(a, b, 768);
    b[1] ^= 1;
    neq = v(a, b, 768);
    hdr(f, "attest");
    fprintf(f,
        "  \"comparison_symbol\": \"%s\",\n"
        "  \"self_test_equal_rc\": %d,\n"
        "  \"self_test_unequal_rc\": %d,\n"
        "  \"attested\": %s,\n"
        "  \"decap_api\": \"OQS_KEM_decaps\"\n}\n",
        g_use_avx2 ? "pqcrystals_ml_kem_*_avx2_verify" : "pqcrystals_ml_kem_*_ref_verify",
        eq, neq, (eq == 0 && neq != 0) ? "true" : "false");
    return (eq == 0 && neq != 0) ? 0 : 1;
}

static int mode_primitive(FILE* f)
{
    int ai, first = 1;
    hdr(f, "primitive-multiclass");
    fprintf(f, "  \"parameter_results\": [\n");
    for (ai = 0; ai < 3; ai++) {
        size_t ct_len = 0;
        verify_fn v = select_verify(algs[ai], &ct_len);
        int silent_votes[MAX_CT];
        int indices_hit[MAX_CT];
        int seed, events = 0, capped = 0, i, n_silent = 0;
        OQS_KEM* kem = OQS_KEM_new(algs[ai]);
        if (!kem || !v) return 1;
        memset(silent_votes, 0, sizeof(silent_votes));
        memset(indices_hit, 0, sizeof(indices_hit));

        for (seed = 1; seed <= N_SEEDS && !capped; seed++) {
            uint8_t *pk = malloc(kem->length_public_key);
            uint8_t *sk = malloc(kem->length_secret_key);
            uint8_t *ct = malloc(kem->length_ciphertext);
            uint8_t *ss = malloc(kem->length_shared_secret);
            uint8_t *mut = malloc(kem->length_ciphertext);
            size_t idx;
            if (!pk || !sk || !ct || !ss || !mut) die("oom", 1);
            /* Deterministic keypair via encaps path: use OQS_randombytes override? 
             * liboqs keypair uses system RNG. For differential compare we only need
             * a valid ciphertext buffer — generate via keypair+encaps then mutate. */
            if (OQS_KEM_keypair(kem, pk, sk) != OQS_SUCCESS) die("keypair", 1);
            if (OQS_KEM_encaps(kem, ct, ss, pk) != OQS_SUCCESS) die("encaps", 1);

            if (v(ct, ct, ct_len) != 0) die("equal verify", 1);

            /* G1 */
            for (idx = 0; idx < ct_len; idx++) {
                int op;
                for (op = 0; op < 2; op++) {
                    if (events >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, ct_len);
                    mut[idx] ^= (op == 0) ? 0x01 : 0xff;
                    if (v(ct, mut, ct_len) == 0) silent_votes[idx]++;
                    indices_hit[idx] = 1;
                    events++;
                }
                if (capped) break;
            }
            /* G2 spot on omission-style tail */
            if (!capped) {
                size_t off;
                for (off = 0; off + 8 <= ct_len; off += 64) {
                    size_t j;
                    if (events >= MUTATION_CAP) { capped = 1; break; }
                    memcpy(mut, ct, ct_len);
                    for (j = 0; j < 8; j++) { mut[off + j] ^= 0x01; indices_hit[off + j] = 1; }
                    if (v(ct, mut, ct_len) == 0) {
                        for (j = 0; j < 8; j++) silent_votes[off + j]++;
                    }
                    events++;
                }
            }
            /* G3 alignments */
            if (!capped) {
                size_t align, off;
                for (align = 16; align <= 64; align *= 2) {
                    for (off = 0; off < ct_len; off += align) {
                        if (events >= MUTATION_CAP) { capped = 1; break; }
                        memcpy(mut, ct, ct_len);
                        mut[off] ^= 0xff;
                        indices_hit[off] = 1;
                        if (v(ct, mut, ct_len) == 0) silent_votes[off]++;
                        events++;
                    }
                }
            }
            free(pk); free(sk); free(ct); free(ss); free(mut);
        }
        OQS_KEM_free(kem);

        for (i = 0; i < (int)ct_len; i++) if (silent_votes[i] >= 2) n_silent++;
        if (!first) fprintf(f, ",\n");
        first = 0;
        fprintf(f,
            "    {\"parameter_set\":\"%s\",\"class\":\"G1_G2_G3_combined\","
            "\"ct_len\":%zu,\"mutation_events\":%d,\"capped\":%s,"
            "\"silent_byte_count\":%d,\"silent_byte_set\":[",
            ps_names[ai], ct_len, events, capped ? "true" : "false", n_silent);
        {
            int printed = 0;
            for (i = 0; i < (int)ct_len; i++) {
                if (silent_votes[i] >= 2) {
                    if (printed) fprintf(f, ",");
                    fprintf(f, "%d", i);
                    printed++;
                }
            }
        }
        fprintf(f, "]}");
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

static int mode_decap(FILE* f)
{
    int ai, first = 1;
    hdr(f, "decap-multiclass");
    fprintf(f, "  \"results\": [\n");
    for (ai = 0; ai < 3; ai++) {
        OQS_KEM* kem = OQS_KEM_new(algs[ai]);
        int seed, events = 0, capped = 0;
        int accept_votes[MAX_CT];
        size_t ct_len;
        int i, n_acc = 0;
        if (!kem) return 1;
        ct_len = kem->length_ciphertext;
        memset(accept_votes, 0, sizeof(accept_votes));
        for (seed = 1; seed <= N_SEEDS && !capped; seed++) {
            uint8_t *pk = malloc(kem->length_public_key);
            uint8_t *sk = malloc(kem->length_secret_key);
            uint8_t *ct = malloc(ct_len);
            uint8_t *ss = malloc(SS_LEN);
            uint8_t *ss2 = malloc(SS_LEN);
            uint8_t *mut = malloc(ct_len);
            size_t idx;
            if (OQS_KEM_keypair(kem, pk, sk) != OQS_SUCCESS) die("kp", 1);
            if (OQS_KEM_encaps(kem, ct, ss, pk) != OQS_SUCCESS) die("enc", 1);
            if (OQS_KEM_decaps(kem, ss2, ct, sk) != OQS_SUCCESS || memcmp(ss, ss2, SS_LEN) != 0)
                die("honest decap", 1);
            for (idx = 0; idx < ct_len; idx++) {
                int accept;
                if (events >= MUTATION_CAP) { capped = 1; break; }
                memcpy(mut, ct, ct_len);
                mut[idx] ^= 0x01;
                if (OQS_KEM_decaps(kem, ss2, mut, sk) != OQS_SUCCESS) {
                    events++;
                    continue;
                }
                accept = (memcmp(ss2, ss, SS_LEN) == 0);
                if (accept) accept_votes[idx]++;
                events++;
            }
            free(pk); free(sk); free(ct); free(ss); free(ss2); free(mut);
        }
        for (i = 0; i < (int)ct_len; i++) if (accept_votes[i] >= 2) n_acc++;
        if (!first) fprintf(f, ",\n");
        first = 0;
        fprintf(f,
            "    {\"parameter_set\":\"%s\",\"mutation_events\":%d,\"capped\":%s,"
            "\"reportable_accept_index_count\":%d,\"reportable_accept_indices\":[",
            ps_names[ai], events, capped ? "true" : "false", n_acc);
        {
            int printed = 0;
            for (i = 0; i < (int)ct_len; i++) {
                if (accept_votes[i] >= 2) {
                    if (printed) fprintf(f, ",");
                    fprintf(f, "%d", i);
                    printed++;
                }
            }
        }
        fprintf(f, "],\"decap_api\":\"OQS_KEM_decaps\",\"message_stability_note\":"
                "\"accept_honest_ss_implies_FO_message_stable\"}");
        OQS_KEM_free(kem);
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

static int unhex(const char* hex, uint8_t* out, size_t max, size_t* out_len)
{
    size_t n = strlen(hex), i;
    if (n % 2) return -1;
    if (n / 2 > max) return -2;
    for (i = 0; i < n; i += 2) {
        unsigned v;
        if (sscanf(hex + i, "%2x", &v) != 1) return -3;
        out[i / 2] = (uint8_t)v;
    }
    *out_len = n / 2;
    return 0;
}

static int json_str(const char* json, const char* key, char* out, size_t out_sz)
{
    char pat[64];
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

static int mode_acvp(FILE* f)
{
    FILE* pf;
    long sz;
    char* buf;
    int n_tested = 0, n_pass = 0, ok = 1, first = 1;
    hdr(f, "acvp-anchor");
    if (!g_acvp) {
        fprintf(f, "  \"error\":\"no file\",\"anchor_ok\":false\n}\n");
        return 1;
    }
    pf = fopen(g_acvp, "r");
    if (!pf) { fprintf(f, "  \"error\":\"fopen\",\"anchor_ok\":false\n}\n"); return 1; }
    fseek(pf, 0, SEEK_END); sz = ftell(pf); fseek(pf, 0, SEEK_SET);
    buf = malloc((size_t)sz + 1);
    if (fread(buf, 1, (size_t)sz, pf) != (size_t)sz) { free(buf); fclose(pf); return 1; }
    buf[sz] = 0; fclose(pf);
    fprintf(f, "  \"anchor_file\":\"%s\",\n  \"cases\":[\n", g_acvp);
    {
        const char* cursor = buf;
        while ((cursor = strstr(cursor, "\"ek\"")) != NULL && n_tested < 15) {
            char ek_h[4096], m_h[128], c_h[4096], k_h[128], ps[32];
            uint8_t ek[1600], m[32], c_exp[1600], k_exp[32], c_got[1600], k_got[32];
            size_t ek_l=0,m_l=0,c_l=0,k_l=0;
            char window[16384];
            const char* ws = cursor > buf + 200 ? cursor - 200 : buf;
            const char* we = cursor + 8000 < buf + sz ? cursor + 8000 : buf + sz;
            size_t wl = (size_t)(we - ws);
            OQS_KEM* kem;
            int pass;
            const char* pset;
            if (wl >= sizeof(window)) wl = sizeof(window) - 1;
            memcpy(window, ws, wl); window[wl] = 0;
            if (json_str(window, "ek", ek_h, sizeof(ek_h)) ||
                json_str(window, "m", m_h, sizeof(m_h)) ||
                json_str(window, "c", c_h, sizeof(c_h)) ||
                json_str(window, "k", k_h, sizeof(k_h))) { cursor += 4; continue; }
            pset = strstr(ws > buf + 500 ? ws - 500 : buf, "ML-KEM-");
            if (!pset || sscanf(pset, "%31s", ps) != 1) { cursor += 4; continue; }
            { char* q = ps; while (*q && *q != '"' && *q != ',' && *q != ' ') q++; *q = 0; }
            if (unhex(ek_h, ek, sizeof(ek), &ek_l) || unhex(m_h, m, sizeof(m), &m_l) ||
                unhex(c_h, c_exp, sizeof(c_exp), &c_l) || unhex(k_h, k_exp, sizeof(k_exp), &k_l)) {
                cursor += 4; continue;
            }
            if (m_l != 32 || k_l != 32) { cursor += 4; continue; }
            kem = OQS_KEM_new(ps);
            if (!kem) { cursor += 4; continue; }
            /* OQS encaps is randomized; for ACVP need deterministic enc with m.
             * Use underlying pqcrystals enc if available via derandomized API —
             * liboqs public API may not expose enc_derand. Try OQS_KEM_encaps_derand if present.
             */
#if defined(OQS_VERSION_MAJOR)
            /* Fall back: decapsulation VAL check using dk+c -> k when present */
#endif
            /* Prefer decap check when dk present in window */
            {
                char dk_h[8192];
                uint8_t dk[3200];
                size_t dk_l = 0;
                if (json_str(window, "dk", dk_h, sizeof(dk_h)) == 0 &&
                    unhex(dk_h, dk, sizeof(dk), &dk_l) == 0 &&
                    dk_l == kem->length_secret_key && c_l == kem->length_ciphertext) {
                    if (OQS_KEM_decaps(kem, k_got, c_exp, dk) == OQS_SUCCESS &&
                        memcmp(k_got, k_exp, 32) == 0) pass = 1;
                    else pass = 0;
                    n_tested++; if (pass) n_pass++; else ok = 0;
                    if (!first) fprintf(f, ",\n"); first = 0;
                    fprintf(f, "    {\"parameter_set\":\"%s\",\"check\":\"decap\",\"pass\":%s}",
                            ps, pass ? "true" : "false");
                }
            }
            OQS_KEM_free(kem);
            cursor += 4;
        }
    }
    fprintf(f,
        "\n  ],\n  \"n_tested\":%d,\"n_pass\":%d,"
        "\"anchor_name\":\"liboqs_in_tree_ACVP_ML-KEM-encapDecap-FIPS203_internalProjection\","
        "\"anchor_grade\":\"%s\",\"anchor_ok\":%s\n}\n",
        n_tested, n_pass,
        (n_tested > 0 && ok) ? "strong" : "weak",
        (n_tested > 0 && ok) ? "true" : "false");
    free(buf);
    return (n_tested > 0 && ok) ? 0 : 1;
}

static int mode_malformed(FILE* f)
{
    int ai, seed, first = 1;
    hdr(f, "malformed-length");
    fprintf(f, "  \"note\":\"G4; never counted as comparison omission\",\n  \"rows\":[\n");
    for (ai = 0; ai < 3; ai++) {
        OQS_KEM* kem = OQS_KEM_new(algs[ai]);
        if (!kem) return 1;
        for (seed = 1; seed <= N_SEEDS; seed++) {
            uint8_t *pk = malloc(kem->length_public_key);
            uint8_t *sk = malloc(kem->length_secret_key);
            uint8_t *ct = malloc(kem->length_ciphertext);
            uint8_t *ss = malloc(SS_LEN);
            uint8_t *ss2 = malloc(SS_LEN);
            int deltas[] = {-1,-16,-32,1,16,32};
            int di;
            OQS_KEM_keypair(kem, pk, sk);
            OQS_KEM_encaps(kem, ct, ss, pk);
            for (di = 0; di < 6; di++) {
                int delta = deltas[di];
                int new_len = (int)kem->length_ciphertext + delta;
                const char* disp;
                int api_rc = -1;
                /* OQS_KEM_decaps requires exact length by API contract; calling with
                 * wrong length is undefined — we record as refused_by_harness without
                 * invoking UB. */
                if (new_len != (int)kem->length_ciphertext) {
                    disp = "refused_by_harness_exact_length_api";
                    api_rc = -1;
                } else {
                    api_rc = (int)OQS_KEM_decaps(kem, ss2, ct, sk);
                    disp = "exact_length_ok";
                }
                if (!first) fprintf(f, ",\n"); first = 0;
                fprintf(f,
                    "    {\"parameter_set\":\"%s\",\"seed\":%d,\"delta\":%d,"
                    "\"submitted_len\":%d,\"api_rc\":%d,\"disposition\":\"%s\","
                    "\"counted_as_comparison_omission\":false}",
                    ps_names[ai], seed, delta, new_len, api_rc, disp);
            }
            free(pk); free(sk); free(ct); free(ss); free(ss2);
        }
        OQS_KEM_free(kem);
    }
    fprintf(f, "\n  ]\n}\n");
    return 0;
}

int main(int argc, char** argv)
{
    const char* mode = NULL;
    int i, rc = 0;
    FILE* out = stdout;
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--mode") && i+1 < argc) mode = argv[++i];
        else if (!strcmp(argv[i], "--build-id") && i+1 < argc) g_build_id = argv[++i];
        else if (!strcmp(argv[i], "--commit") && i+1 < argc) g_commit = argv[++i];
        else if (!strcmp(argv[i], "--out") && i+1 < argc) g_out_path = argv[++i];
        else if (!strcmp(argv[i], "--acvp-prompt") && i+1 < argc) g_acvp = argv[++i];
        else if (!strcmp(argv[i], "--backend") && i+1 < argc) {
            g_backend = argv[++i];
            g_use_avx2 = (strcmp(g_backend, "ref") != 0);
        }
    }
    if (!g_backend || !strcmp(g_backend, "unknown"))
        g_backend = g_use_avx2 ? "liboqs_avx2_verify" : "liboqs_ref_verify";
    if (!mode) return 2;
    if (g_out_path) { out = fopen(g_out_path, "w"); if (!out) return 2; }
    if (!strcmp(mode, "attest")) rc = mode_attest(out);
    else if (!strcmp(mode, "primitive-multiclass")) rc = mode_primitive(out);
    else if (!strcmp(mode, "decap-multiclass")) rc = mode_decap(out);
    else if (!strcmp(mode, "acvp-anchor")) rc = mode_acvp(out);
    else if (!strcmp(mode, "malformed-length")) rc = mode_malformed(out);
    else rc = 2;
    if (g_out_path) fclose(out);
    return rc;
}
