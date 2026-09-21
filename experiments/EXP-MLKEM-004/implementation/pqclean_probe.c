/*
 * EXP-MLKEM-004 mechanism-matched second-implementation probe (PQClean ML-KEM).
 *
 * Primitive: PQClean verify() from the selected backend (avx2 or aarch64),
 * expected to use fixed-bound hand-written vector/SIMD comparison tails.
 * Decapsulation: crypto_kem_dec public API.
 * Never modifies library comparison logic, lengths, or dispatch.
 *
 * Compile with -I for the chosen scheme include path and link the PQClean
 * object archive for that scheme/backend.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "api.h"

#define N_SEEDS 4
#define MUTATION_CAP 20000
#define MAX_CT 1568
#define SS_LEN 32

/* PQClean common verify symbol (scheme-local). */
int verify(const uint8_t *a, const uint8_t *b, size_t len);

static const char *g_build_id = "BUILD-PQCLEAN";
static const char *g_backend = "unknown";
static const char *g_commit = "unknown";
static const char *g_out_path = NULL;
static const char *g_scheme = "ml-kem-1024";
static const char *g_acvp = NULL;

typedef struct {
    const char *name;
    size_t ct_len;
    size_t pk_len;
    size_t sk_len;
    size_t ss_len;
} Scheme;

/* Lengths filled from api.h macros when possible. */
static Scheme g_ps;

static void die(const char *m, int rc)
{
    fprintf(stderr, "FATAL: %s (%d)\n", m, rc);
    exit(2);
}

static void fill_seed(int seed_id, uint8_t *buf, size_t n)
{
    size_t i;
    for (i = 0; i < n; i++)
        buf[i] = (uint8_t)((seed_id * 17 + (int)i * 31) & 0xff);
    buf[0] = (uint8_t)seed_id;
}

static void hdr(FILE *f, const char *mode)
{
    fprintf(f,
            "{\n  \"experiment_id\": \"EXP-MLKEM-004\",\n  \"mode\": \"%s\",\n"
            "  \"build_id\": \"%s\",\n  \"backend\": \"%s\",\n"
            "  \"resolved_commit\": \"%s\",\n  \"implementation\": \"PQClean\",\n"
            "  \"scheme\": \"%s\",\n",
            mode, g_build_id, g_backend, g_commit, g_scheme);
}

static int mode_attest(FILE *f)
{
    uint8_t a[MAX_CT], b[MAX_CT];
    int eq, neq;
    size_t n = g_ps.ct_len;
    if (n == 0 || n > MAX_CT)
        die("bad ct_len", 1);
    memset(a, 0x5a, n);
    memset(b, 0x5a, n);
    eq = verify(a, b, n);
    b[1] ^= 1;
    neq = verify(a, b, n);
    hdr(f, "attest");
    fprintf(f,
            "  \"comparison_symbol\": \"verify\",\n"
            "  \"attest_length\": %zu,\n"
            "  \"self_test_equal_rc\": %d,\n"
            "  \"self_test_unequal_rc\": %d,\n"
            "  \"attested\": %s,\n"
            "  \"decap_api\": \"crypto_kem_dec\",\n"
            "  \"mechanism_claim\": \"fixed_bound_handwritten_vector_tail\"\n}\n",
            n, eq, neq, (eq == 0 && neq != 0) ? "true" : "false");
    return (eq == 0 && neq != 0) ? 0 : 1;
}

static int keypair_encap(int seed_id, uint8_t *pk, uint8_t *sk, uint8_t *ct, uint8_t *ss)
{
    /* PQClean keypair uses RNG; we still get a live key/ciphertext for differential compare.
     * Seed only documents the trial index; not a deterministic KAT. */
    (void)seed_id;
    if (crypto_kem_keypair(pk, sk) != 0)
        return -1;
    if (crypto_kem_enc(ct, ss, pk) != 0)
        return -2;
    return 0;
}

static int mode_primitive(FILE *f)
{
    int seed, idx, first = 1;
    size_t ct_len = g_ps.ct_len;
    int silent_votes[MAX_CT];
    int indices_hit[MAX_CT];
    int i, events = 0, capped = 0;
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[MAX_CT], ss[CRYPTO_BYTES];

    memset(silent_votes, 0, sizeof(silent_votes));
    memset(indices_hit, 0, sizeof(indices_hit));
    hdr(f, "primitive-multiclass");
    fprintf(f, "  \"parameter_results\": [\n");

    for (seed = 1; seed <= N_SEEDS && !capped; seed++) {
        if (keypair_encap(seed, pk, sk, ct, ss) != 0)
            die("keypair/encap", seed);
        if (verify(ct, ct, ct_len) != 0)
            die("equal verify", 1);

        /* G1 */
        for (idx = 0; idx < (int)ct_len; idx++) {
            int op;
            for (op = 0; op < 2; op++) {
                uint8_t mut[MAX_CT];
                uint8_t xorv = (op == 0) ? 0x01 : 0xff;
                int rc;
                if (events >= MUTATION_CAP) {
                    capped = 1;
                    break;
                }
                memcpy(mut, ct, ct_len);
                mut[idx] ^= xorv;
                rc = verify(ct, mut, ct_len);
                events++;
                indices_hit[idx] = 1;
                if (rc == 0)
                    silent_votes[idx]++;
            }
            if (capped)
                break;
        }
    }

    {
        int n_silent = 0, n_hit = 0, printed = 0;
        for (i = 0; i < (int)ct_len; i++)
            if (indices_hit[i])
                n_hit++;
        fprintf(f,
                "    {\"parameter_set\":\"%s\",\"class\":\"G1_single_byte\","
                "\"ct_len\":%zu,\"keys\":%d,\"mutation_events\":%d,\"capped\":%s,"
                "\"indices_hit\":%d,\"index_fraction\":%.6f,"
                "\"coverage_status\":\"%s\",\"silent_byte_count\":",
                g_ps.name, ct_len, N_SEEDS, events, capped ? "true" : "false", n_hit,
                (double)n_hit / (double)ct_len,
                capped ? "partial" : "complete_for_class_definition");
        for (i = 0; i < (int)ct_len; i++)
            if (silent_votes[i] >= 2)
                n_silent++;
        fprintf(f, "%d,\"silent_byte_set\":[", n_silent);
        for (i = 0; i < (int)ct_len; i++) {
            if (silent_votes[i] >= 2) {
                if (printed)
                    fprintf(f, ",");
                fprintf(f, "%d", i);
                printed++;
            }
        }
        fprintf(f, "]}\n");
    }

    /* G2 dense on R for ml-kem-1024 */
    {
        int silent2[MAX_CT];
        int hit2[MAX_CT];
        int events2 = 0, capped2 = 0, printed = 0, n_silent = 0, n_hit = 0;
        memset(silent2, 0, sizeof(silent2));
        memset(hit2, 0, sizeof(hit2));
        for (seed = 1; seed <= N_SEEDS && !capped2; seed++) {
            int k, off;
            if (keypair_encap(seed, pk, sk, ct, ss) != 0)
                die("keypair g2", seed);
            for (k = 2; k <= 16; k *= 2) {
                for (off = 0; off <= (int)ct_len - k; off += k) {
                    uint8_t mut[MAX_CT];
                    int j, rc;
                    if (events2 >= MUTATION_CAP) {
                        capped2 = 1;
                        break;
                    }
                    memcpy(mut, ct, ct_len);
                    for (j = 0; j < k; j++) {
                        mut[off + j] ^= 0x01;
                        hit2[off + j] = 1;
                    }
                    rc = verify(ct, mut, ct_len);
                    events2++;
                    if (rc == 0)
                        for (j = 0; j < k; j++)
                            silent2[off + j]++;
                }
            }
        }
        for (i = 0; i < (int)ct_len; i++)
            if (hit2[i])
                n_hit++;
        for (i = 0; i < (int)ct_len; i++)
            if (silent2[i] >= 2)
                n_silent++;
        fprintf(f,
                "    ,{\"parameter_set\":\"%s\",\"class\":\"G2_multi_byte\","
                "\"ct_len\":%zu,\"mutation_events\":%d,\"capped\":%s,"
                "\"indices_hit\":%d,\"index_fraction\":%.6f,"
                "\"coverage_status\":\"%s\",\"silent_byte_count\":%d,\"silent_byte_set\":[",
                g_ps.name, ct_len, events2, capped2 ? "true" : "false", n_hit,
                (double)n_hit / (double)ct_len,
                capped2 ? "partial" : "complete_for_class_definition", n_silent);
        for (i = 0; i < (int)ct_len; i++) {
            if (silent2[i] >= 2) {
                if (printed)
                    fprintf(f, ",");
                fprintf(f, "%d", i);
                printed++;
            }
        }
        fprintf(f, "]}\n");
    }

    /* G3 alignment */
    {
        int silent3[MAX_CT];
        int hit3[MAX_CT];
        int events3 = 0, printed = 0, n_silent = 0, n_hit = 0, align, off;
        memset(silent3, 0, sizeof(silent3));
        memset(hit3, 0, sizeof(hit3));
        for (seed = 1; seed <= N_SEEDS; seed++) {
            if (keypair_encap(seed, pk, sk, ct, ss) != 0)
                die("keypair g3", seed);
            for (align = 16; align <= 64; align *= 2) {
                for (off = 0; off < (int)ct_len; off += align) {
                    int targets[2] = {off, (off + align - 1 < (int)ct_len) ? off + align - 1
                                                                          : (int)ct_len - 1};
                    int ti, op;
                    for (ti = 0; ti < 2; ti++) {
                        for (op = 0; op < 2; op++) {
                            uint8_t mut[MAX_CT];
                            uint8_t xorv = (op == 0) ? 0x01 : 0xff;
                            int rc, t = targets[ti];
                            memcpy(mut, ct, ct_len);
                            mut[t] ^= xorv;
                            rc = verify(ct, mut, ct_len);
                            events3++;
                            hit3[t] = 1;
                            if (rc == 0)
                                silent3[t]++;
                        }
                    }
                }
            }
        }
        for (i = 0; i < (int)ct_len; i++)
            if (hit3[i])
                n_hit++;
        for (i = 0; i < (int)ct_len; i++)
            if (silent3[i] >= 2)
                n_silent++;
        fprintf(f,
                "    ,{\"parameter_set\":\"%s\",\"class\":\"G3_alignment\","
                "\"ct_len\":%zu,\"mutation_events\":%d,\"capped\":false,"
                "\"indices_hit\":%d,\"index_fraction\":%.6f,"
                "\"coverage_status\":\"complete_for_class_definition\","
                "\"silent_byte_count\":%d,\"silent_byte_set\":[",
                g_ps.name, ct_len, events3, n_hit, (double)n_hit / (double)ct_len, n_silent);
        for (i = 0; i < (int)ct_len; i++) {
            if (silent3[i] >= 2) {
                if (printed)
                    fprintf(f, ",");
                fprintf(f, "%d", i);
                printed++;
            }
        }
        fprintf(f, "]}\n  ]\n}\n");
    }
    (void)first;
    return 0;
}

static int mode_decap(FILE *f)
{
    int seed, idx, first = 1;
    size_t ct_len = g_ps.ct_len;
    int accept_votes[MAX_CT];
    int events = 0;
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[MAX_CT], ss[CRYPTO_BYTES], ss_out[CRYPTO_BYTES];
    int i;

    memset(accept_votes, 0, sizeof(accept_votes));
    hdr(f, "decap-multiclass");
    fprintf(f, "  \"results\": [\n");
    for (seed = 1; seed <= N_SEEDS; seed++) {
        if (keypair_encap(seed, pk, sk, ct, ss) != 0)
            die("decap keypair", seed);
        if (crypto_kem_dec(ss_out, ct, sk) != 0 || memcmp(ss_out, ss, CRYPTO_BYTES) != 0)
            die("honest decap", seed);
        for (idx = 0; idx < (int)ct_len; idx++) {
            uint8_t mut[MAX_CT];
            int accept;
            if (events >= MUTATION_CAP)
                break;
            memcpy(mut, ct, ct_len);
            mut[idx] ^= 0x01;
            if (crypto_kem_dec(ss_out, mut, sk) != 0) {
                events++;
                continue;
            }
            accept = (memcmp(ss_out, ss, CRYPTO_BYTES) == 0);
            events++;
            if (accept)
                accept_votes[idx]++;
        }
    }
    {
        int n_acc = 0, printed = 0;
        for (i = 0; i < (int)ct_len; i++)
            if (accept_votes[i] >= 2)
                n_acc++;
        fprintf(f,
                "    {\"parameter_set\":\"%s\",\"row_type\":\"summary\","
                "\"mutation_events\":%d,\"reportable_accept_index_count\":%d,"
                "\"reportable_accept_indices\":[",
                g_ps.name, events, n_acc);
        for (i = 0; i < (int)ct_len; i++) {
            if (accept_votes[i] >= 2) {
                if (printed)
                    fprintf(f, ",");
                fprintf(f, "%d", i);
                printed++;
            }
        }
        fprintf(f, "]}\n  ]\n}\n");
    }
    (void)first;
    return 0;
}

static int mode_malformed(FILE *f)
{
    int seed, first = 1;
    int deltas[] = {-1, -16, -32, 1, 16, 32};
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[MAX_CT], ss[CRYPTO_BYTES], ss_out[CRYPTO_BYTES];
    hdr(f, "malformed-length");
    fprintf(f, "  \"note\": \"G4 results; never counted as comparison omission\",\n");
    fprintf(f, "  \"rows\": [\n");
    for (seed = 1; seed <= N_SEEDS; seed++) {
        int di;
        if (keypair_encap(seed, pk, sk, ct, ss) != 0)
            die("malformed keypair", seed);
        for (di = 0; di < 6; di++) {
            /* PQClean crypto_kem_dec has fixed-length ciphertext; harness refuses
             * variable-length submission rather than invoking UB. */
            if (!first)
                fprintf(f, ",\n");
            first = 0;
            fprintf(f,
                    "    {\"parameter_set\":\"%s\",\"seed\":%d,\"nominal_ct_len\":%zu,"
                    "\"delta\":%d,\"submitted_len\":%d,\"api_rc\":-1,\"refused\":true,"
                    "\"disposition\":\"refused_by_harness_exact_length_api\","
                    "\"counted_as_comparison_omission\":false}",
                    g_ps.name, seed, g_ps.ct_len, deltas[di],
                    (int)g_ps.ct_len + deltas[di]);
        }
    }
    fprintf(f, "\n  ]\n}\n");
    (void)ss_out;
    return 0;
}

static int mode_acvp(FILE *f)
{
    hdr(f, "acvp-anchor");
    fprintf(f,
            "  \"anchor_file\": %s,\n"
            "  \"n_tested\": 0,\n"
            "  \"n_pass\": 0,\n"
            "  \"anchor_name\": \"not_validated_against_nist_file_in_this_probe\",\n"
            "  \"anchor_grade\": \"weak\",\n"
            "  \"anchor_ok\": false,\n"
            "  \"note\": \"PQClean probe does not upgrade grade via unused NIST downloads\"\n}\n",
            g_acvp ? g_acvp : "null");
    return 1;
}

int main(int argc, char **argv)
{
    const char *mode = NULL;
    int i, rc = 0;
    FILE *out = stdout;

    g_ps.name = "ML-KEM-1024";
    g_ps.ct_len = CRYPTO_CIPHERTEXTBYTES;
    g_ps.pk_len = CRYPTO_PUBLICKEYBYTES;
    g_ps.sk_len = CRYPTO_SECRETKEYBYTES;
    g_ps.ss_len = CRYPTO_BYTES;

    for (i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc)
            mode = argv[++i];
        else if (strcmp(argv[i], "--build-id") == 0 && i + 1 < argc)
            g_build_id = argv[++i];
        else if (strcmp(argv[i], "--commit") == 0 && i + 1 < argc)
            g_commit = argv[++i];
        else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc)
            g_out_path = argv[++i];
        else if (strcmp(argv[i], "--backend") == 0 && i + 1 < argc)
            g_backend = argv[++i];
        else if (strcmp(argv[i], "--scheme") == 0 && i + 1 < argc)
            g_scheme = argv[++i];
        else if (strcmp(argv[i], "--acvp-prompt") == 0 && i + 1 < argc)
            g_acvp = argv[++i];
        else {
            fprintf(stderr, "unknown arg %s\n", argv[i]);
            return 2;
        }
    }
    if (!mode)
        return 2;
    if (g_out_path) {
        out = fopen(g_out_path, "w");
        if (!out)
            return 2;
    }
    if (strcmp(mode, "attest") == 0)
        rc = mode_attest(out);
    else if (strcmp(mode, "primitive-multiclass") == 0)
        rc = mode_primitive(out);
    else if (strcmp(mode, "decap-multiclass") == 0)
        rc = mode_decap(out);
    else if (strcmp(mode, "malformed-length") == 0)
        rc = mode_malformed(out);
    else if (strcmp(mode, "acvp-anchor") == 0)
        rc = mode_acvp(out);
    else
        rc = 2;
    if (g_out_path)
        fclose(out);
    return rc;
}
