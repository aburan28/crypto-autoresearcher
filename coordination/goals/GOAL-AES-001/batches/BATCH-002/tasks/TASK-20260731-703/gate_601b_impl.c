/* ===================================================================
 * gate_601b_impl.c  --  GATE-601-B, TASK-20260731-703, GOAL-AES-001 BATCH-002
 *
 * WHAT THIS PROGRAM DOES
 * ----------------------
 * It implements TWO aggregations of the same key-guess function on a
 * SMALL-SCALE, AES-SHAPED cipher with n-bit cells and a 4x4 cell state,
 * and measures three things and nothing else:
 *
 *   YIELD 1  correctness equivalence: do the two aggregations return the
 *            IDENTICAL surviving-key set on the same inputs?
 *   YIELD 2  S-box independence of the counted-operation ratio: is the ratio
 *            unchanged when the cipher's S-box is replaced by a freshly drawn,
 *            seeded random bijection on the cell alphabet (null control)?
 *   YIELD 3  the measured counted-operation ratio (reorganized / direct) at
 *            each cell width actually run.
 *
 * SCOPE.  The cipher below is NOT AES.  It is a scaled-down AES-shaped SPN.
 * Nothing measured here is a statement about AES at any round count.
 *
 * THE TWO AGGREGATIONS
 * --------------------
 * Guess k = (k_1,k_2,k_3,k_4) over the cell alphabet GF(2)^n; guess space
 * q^4 = 2^(4n)  (2^16 at n = 4).  For a data structure D of ciphertexts,
 *
 *     g(k) = XOR_{c in D} Sinv( XOR_{i=1..4} G_i[ c_i XOR k_i ] ),
 *     G_i[y] = Minv[0][i] (*) Sinv(y)        ((*) = GF(2^n) multiplication)
 *
 * and k survives structure D iff g(k) == 0.  A key survives the run iff it
 * survives every structure.
 *
 *   DIRECT   = partial-sums aggregation.  Peels one cell at a time, carrying
 *              a parity table that shrinks by a factor q per peeled cell.
 *
 *   REORG    = the same g, computed as a 4-dimensional Walsh-Hadamard
 *              convolution over the group (GF(2)^n)^4.  For an output-bit
 *              mask u, with N0 the parity table over the 4-tuple c and
 *              F_u(x) = (-1)^<u, Sinv(XOR_i G_i[x_i])>,
 *                  C_u(k) = SUM_c N0[c] F_u(c XOR k) = (N0 (x) F_u)(k),
 *              an XOR-convolution, so C_u = WHT^-1( WHT(N0) . WHT(F_u) ).
 *              g(k) == 0 iff bit_u(k) == 0 for the n basis masks u = e_0..e_n-1,
 *              where bit_u(k) = ((T - C_u(k))/2) mod 2 and T = SUM_c N0[c].
 *
 * COUNTING CONVENTION (identical macros, identical rules, both sides)
 * ------------------------------------------------------------------
 *   TL  one indexed read of any array (lookup table or working table)
 *   XR  one XOR of a data value or of an index value
 *   AD  one integer addition or subtraction on a data value
 *   ML  one integer multiplication on a data value
 *   total = TL + XR + AD + ML
 * NOT counted on either side: array writes, memset/clear, loop bookkeeping,
 * shifts and masks used for bit-field packing, comparisons and branches.
 * Shared preprocessing that is identical for both sides (key setup, S-box
 * construction, encryption of the data, construction of the parity tables N0)
 * is OUTSIDE both counters.  The G_i tables are used by both sides and are
 * counted in both, identically.
 *
 * DETERMINISM.  All randomness comes from splitmix64 with explicitly recorded
 * seeds.  The program takes no input other than its argv and prints JSON.
 *
 * Build:  gcc -O2 -std=c11 -Wall -Wextra -o gate_601b gate_601b_impl.c
 * Run:    ./gate_601b [seed_base] [structures] [keys3] [keys4] [keys5]
 * =================================================================== */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

/* ------------------------------------------------------------------ *
 * operation counters                                                  *
 * ------------------------------------------------------------------ */
typedef struct { uint64_t tl, xr, ad, ml; } ops_t;
static ops_t *CUR = NULL;
#define C_TL(k) (CUR->tl += (uint64_t)(k))
#define C_XR(k) (CUR->xr += (uint64_t)(k))
#define C_AD(k) (CUR->ad += (uint64_t)(k))
#define C_ML(k) (CUR->ml += (uint64_t)(k))
static uint64_t ops_total(const ops_t *o) { return o->tl + o->xr + o->ad + o->ml; }

/* ------------------------------------------------------------------ *
 * splitmix64: the only source of randomness in this program           *
 * ------------------------------------------------------------------ */
static uint64_t sm64(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ------------------------------------------------------------------ *
 * GF(2^n) arithmetic (uncounted: cipher/table setup only)             *
 * ------------------------------------------------------------------ */
static int NB;      /* cell width in bits            */
static int Q;       /* alphabet size 2^NB            */
static int MSK;     /* Q-1                           */
static int POLY;    /* reduction polynomial          */

static int gfmul(int a, int b) {
    int r = 0;
    while (b) {
        if (b & 1) r ^= a;
        b >>= 1;
        a <<= 1;
        if (a & Q) a ^= POLY;
    }
    return r & MSK;
}
static int gfinv(int a) {
    if (a == 0) return 0;
    for (int b = 1; b < Q; b++) if (gfmul(a, b) == 1) return b;
    fprintf(stderr, "FATAL: no inverse for %d\n", a); exit(2);
}

/* ------------------------------------------------------------------ *
 * cipher instance                                                     *
 * ------------------------------------------------------------------ */
#define MAXQ 32
#define RNDS 5          /* 5 rounds; see round structure in encrypt()  */

typedef struct {
    int  sbox[MAXQ], sinv[MAXQ];
    int  M[4][4], Minv[4][4], mc_row[4];
    int  rk[RNDS + 1][16];         /* independent random round keys      */
    int  affine_taps;              /* algebraic S-box: circulant tap set  */
    int  affine_const;
    int  sbox_kind;                /* 0 = algebraic, 1 = random bijection */
    uint64_t sbox_seed;            /* seed of the random bijection draw   */
    uint64_t key_seed;
} cipher_t;

/* circulant GF(2)-linear map from a tap set, applied to an n-bit value */
static int aff_lin(int taps, int x) {
    int y = 0;
    for (int t = 0; t < NB; t++)
        if (taps & (1 << t))
            y ^= ((x << t) | (x >> (NB - t))) & MSK;
    return y;
}
static int lin_is_bijective(int taps) {
    int seen[MAXQ]; memset(seen, 0, sizeof seen);
    for (int x = 0; x < Q; x++) { int y = aff_lin(taps, x); if (seen[y]) return 0; seen[y] = 1; }
    return 1;
}

/* smallest tap mask (as an integer) giving an invertible circulant */
static int pick_affine_taps(void) {
    for (int m = 1; m < Q; m++) if (lin_is_bijective(m)) return m;
    fprintf(stderr, "FATAL: no invertible circulant\n"); exit(2);
}

static int mat_invert(const int A[4][4], int Ainv[4][4]) {
    int a[4][8];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) a[i][j] = A[i][j];
        for (int j = 0; j < 4; j++) a[i][4 + j] = (i == j);
    }
    for (int col = 0; col < 4; col++) {
        int piv = -1;
        for (int r = col; r < 4; r++) if (a[r][col]) { piv = r; break; }
        if (piv < 0) return 0;
        if (piv != col) for (int j = 0; j < 8; j++) { int t = a[col][j]; a[col][j] = a[piv][j]; a[piv][j] = t; }
        int inv = gfinv(a[col][col]);
        for (int j = 0; j < 8; j++) a[col][j] = gfmul(a[col][j], inv);
        for (int r = 0; r < 4; r++) if (r != col && a[r][col]) {
            int f = a[r][col];
            for (int j = 0; j < 8; j++) a[r][j] ^= gfmul(f, a[col][j]);
        }
    }
    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) Ainv[i][j] = a[i][4 + j];
    return 1;
}

/* A circulant MixColumns first row is ACCEPTED iff
 *   (a) every entry is nonzero   -- one active cell spreads to a full column,
 *                                   which the 3-round balance property needs;
 *   (b) the matrix is invertible;
 *   (c) row 0 of the inverse has four nonzero, PAIRWISE DISTINCT entries --
 *       a zero entry would make one guessed cell irrelevant, and two equal
 *       entries would make two guessed cells interchangeable; either way the
 *       4-cell guess space would be degenerate.
 * (2,3,1,1) satisfies this at n = 4 and n = 5 but not at n = 3 (its inverse
 * row is (5,0,6,2) over GF(2^3)), so at n = 3 the first circulant row in
 * packed order that does satisfy it is used instead.  Recorded per run. */
static int mc_row_ok(const int row[4], int Minv0[4]) {
    for (int i = 0; i < 4; i++) if ((row[i] & MSK) == 0) return 0;
    int M[4][4], Mi[4][4];
    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) M[i][j] = row[(j - i + 4) % 4] & MSK;
    if (!mat_invert(M, Mi)) return 0;
    for (int i = 0; i < 4; i++) if (Mi[0][i] == 0) return 0;
    for (int i = 0; i < 4; i++) for (int j = i + 1; j < 4; j++) if (Mi[0][i] == Mi[0][j]) return 0;
    for (int i = 0; i < 4; i++) Minv0[i] = Mi[0][i];
    return 1;
}
static void pick_mc_row(int out[4]) {
    int mi0[4];
    int aes[4] = {2 & MSK, 3 & MSK, 1, 1};
    if (mc_row_ok(aes, mi0)) { memcpy(out, aes, sizeof aes); return; }
    for (uint32_t packed = 0; packed < (1u << (4 * NB)); packed++) {
        int row[4];
        for (int i = 0; i < 4; i++) row[i] = (int)((packed >> (NB * i)) & (uint32_t)MSK);
        if (mc_row_ok(row, mi0)) { memcpy(out, row, sizeof row); return; }
    }
    fprintf(stderr, "FATAL: no acceptable MixColumns row at n=%d\n", NB); exit(2);
}

static void build_cipher(cipher_t *C, int sbox_kind, uint64_t sbox_seed, uint64_t key_seed) {
    memset(C, 0, sizeof *C);
    C->sbox_kind = sbox_kind;
    C->sbox_seed = sbox_seed;
    C->key_seed  = key_seed;

    if (sbox_kind == 0) {
        /* AES-shaped S-box: GF(2^n) inversion followed by an invertible
         * GF(2)-affine map (circulant + constant). */
        C->affine_taps = pick_affine_taps();
        C->affine_const = 0x63 & MSK;
        for (int x = 0; x < Q; x++)
            C->sbox[x] = aff_lin(C->affine_taps, gfinv(x)) ^ C->affine_const;
    } else {
        /* NULL CONTROL: a freshly drawn random bijection on the cell alphabet.
         * Fisher-Yates over splitmix64 seeded by sbox_seed. */
        C->affine_taps = -1; C->affine_const = -1;
        for (int x = 0; x < Q; x++) C->sbox[x] = x;
        uint64_t s = sbox_seed;
        for (int i = Q - 1; i > 0; i--) {
            int j = (int)(sm64(&s) % (uint64_t)(i + 1));
            int t = C->sbox[i]; C->sbox[i] = C->sbox[j]; C->sbox[j] = t;
        }
    }
    { /* bijectivity self-check */
        int seen[MAXQ]; memset(seen, 0, sizeof seen);
        for (int x = 0; x < Q; x++) { if (seen[C->sbox[x]]) { fprintf(stderr, "FATAL: S-box not a bijection\n"); exit(2);} seen[C->sbox[x]] = 1; }
    }
    for (int x = 0; x < Q; x++) C->sinv[C->sbox[x]] = x;

    /* MixColumns: AES-shaped circulant (2,3,1,1) over GF(2^n), accepted iff it
     * satisfies the three conditions in mc_row_ok(); otherwise the first
     * circulant row in packed order that does.  See pick_mc_row(). */
    int row0[4]; pick_mc_row(row0);
    for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) C->M[i][j] = row0[(j - i + 4) % 4] & MSK;
    if (!mat_invert(C->M, C->Minv)) { fprintf(stderr, "FATAL: MixColumns singular at n=%d\n", NB); exit(2); }
    memcpy(C->mc_row, row0, sizeof row0);

    uint64_t s = key_seed;
    for (int r = 0; r <= RNDS; r++) for (int i = 0; i < 16; i++) C->rk[r][i] = (int)(sm64(&s) & (uint64_t)MSK);
}

/* state layout: st[row + 4*col] */
static void sub_bytes(const cipher_t *C, int *st) { for (int i = 0; i < 16; i++) st[i] = C->sbox[st[i]]; }
static void shift_rows(int *st) {                    /* row r shifted left by r */
    int t[16];
    for (int r = 0; r < 4; r++) for (int c = 0; c < 4; c++) t[r + 4 * c] = st[r + 4 * ((c + r) & 3)];
    memcpy(st, t, sizeof t);
}
static void mix_cols(const cipher_t *C, int *st) {
    int t[16];
    for (int c = 0; c < 4; c++) for (int r = 0; r < 4; r++) {
        int v = 0;
        for (int i = 0; i < 4; i++) v ^= gfmul(C->M[r][i], st[i + 4 * c]);
        t[r + 4 * c] = v;
    }
    memcpy(st, t, sizeof t);
}
static void add_rk(const cipher_t *C, int *st, int r) { for (int i = 0; i < 16; i++) st[i] ^= C->rk[r][i]; }

/* Round structure of the small-scale cipher (a definitional choice, stated
 * in run_record.md; it is NOT the AES round structure):
 *    X = P + K0
 *    rounds 1..3 : SB, SR, MC, ARK          <- output X3 is balanced
 *    round  4    : SB, SR, MC               <- no AddRoundKey (keeps the
 *                                              guess space at exactly 4 cells)
 *    round  5    : SB, SR, ARK(K5)          <- no MixColumns (AES-shaped)
 */
static void encrypt(const cipher_t *C, const int *pt, int *ct) {
    int st[16]; memcpy(st, pt, sizeof st);
    add_rk(C, st, 0);
    for (int r = 1; r <= 3; r++) { sub_bytes(C, st); shift_rows(st); mix_cols(C, st); add_rk(C, st, r); }
    sub_bytes(C, st); shift_rows(st); mix_cols(C, st);              /* round 4 */
    sub_bytes(C, st); shift_rows(st); add_rk(C, st, 5);             /* round 5 */
    memcpy(ct, st, 16 * sizeof(int));
}
/* the state at the output of round 3 (used only by the balance self-check) */
static void encrypt_to_r3(const cipher_t *C, const int *pt, int *out) {
    int st[16]; memcpy(st, pt, sizeof st);
    add_rk(C, st, 0);
    for (int r = 1; r <= 3; r++) { sub_bytes(C, st); shift_rows(st); mix_cols(C, st); add_rk(C, st, r); }
    memcpy(out, st, 16 * sizeof(int));
}

/* the four ciphertext cells the guess acts on: (row i, col (4-i)%4) */
static int relpos(int i) { return i + 4 * ((4 - i) & 3); }
/* the correct guess, packed */
static uint32_t true_guess(const cipher_t *C) {
    uint32_t k = 0;
    for (int i = 0; i < 4; i++) k |= (uint32_t)(C->rk[5][relpos(i)] & MSK) << (NB * i);
    return k;
}

/* ------------------------------------------------------------------ *
 * data: R structures, each q^4 plaintexts (a disjoint union of q^3     *
 * Lambda-sets), reduced to a parity table N0 over the 4 relevant cells *
 * ------------------------------------------------------------------ */
static void build_N0(const cipher_t *C, uint64_t struct_seed, uint8_t *N0, uint32_t n4) {
    memset(N0, 0, n4);
    int pt[16], ct[16];
    uint64_t s = struct_seed;
    for (int i = 0; i < 16; i++) pt[i] = (int)(sm64(&s) & (uint64_t)MSK);
    const int act[4] = {0, 5, 10, 15};   /* varied cells: the state diagonal */
    for (int a3 = 0; a3 < Q; a3++) { pt[act[3]] = a3;
    for (int a2 = 0; a2 < Q; a2++) { pt[act[2]] = a2;
    for (int a1 = 0; a1 < Q; a1++) { pt[act[1]] = a1;
    for (int a0 = 0; a0 < Q; a0++) { pt[act[0]] = a0;
        encrypt(C, pt, ct);
        uint32_t idx = 0;
        for (int i = 0; i < 4; i++) idx |= (uint32_t)(ct[relpos(i)] & MSK) << (NB * i);
        N0[idx] ^= 1;
    }}}}
}

/* ------------------------------------------------------------------ *
 * shared table used by BOTH aggregations: G_i[y] = Minv[0][i] * Sinv(y) *
 * Counted identically on both sides.                                   *
 * ------------------------------------------------------------------ */
static void build_G(const cipher_t *C, int G[4][MAXQ]) {
    for (int i = 0; i < 4; i++)
        for (int y = 0; y < Q; y++) {
            C_TL(1);                                  /* read Sinv[y]  */
            G[i][y] = gfmul(C->Minv[0][i], C->sinv[y]);
            C_ML(1);                                  /* the GF multiply */
        }
}

/* ------------------------------------------------------------------ *
 * DIRECT aggregation: partial sums                                     *
 * ------------------------------------------------------------------ */
static void agg_direct(const cipher_t *C, uint8_t **N0, int R, uint8_t *alive, ops_t *ops, ops_t *pre) {
    CUR = ops; memset(ops, 0, sizeof *ops);
    const uint32_t n4 = 1u << (4 * NB), n3 = 1u << (3 * NB), n2 = 1u << (2 * NB), n1 = (uint32_t)Q;
    int G[4][MAXQ]; build_G(C, G);
    *pre = *ops;      /* key- and structure-independent precomputation so far */

    uint8_t *T1 = malloc(n4), *T2 = malloc(n3), *T3 = malloc(n2), *T4 = malloc(n1);
    if (!T1 || !T2 || !T3 || !T4) { fprintf(stderr, "FATAL: alloc\n"); exit(3); }

    for (uint32_t i = 0; i < n4; i++) alive[i] = 1;

    for (int r = 0; r < R; r++) {
        const uint8_t *T0 = N0[r];
        for (int k1 = 0; k1 < Q; k1++) {
            memset(T1, 0, n4);
            for (uint32_t idx = 0; idx < n4; idx++) {
                C_TL(1); uint8_t v = T0[idx];
                uint32_t c1 = idx & (uint32_t)MSK;
                C_XR(1); C_TL(1); uint32_t z = (uint32_t)G[0][c1 ^ (uint32_t)k1];
                uint32_t nidx = (idx & ~(uint32_t)MSK) | z;
                C_TL(1); C_XR(1); T1[nidx] ^= v;
            }
            for (int k2 = 0; k2 < Q; k2++) {
                memset(T2, 0, n3);
                for (uint32_t idx = 0; idx < n4; idx++) {
                    C_TL(1); uint8_t v = T1[idx];
                    uint32_t zp = idx & (uint32_t)MSK, c2 = (idx >> NB) & (uint32_t)MSK;
                    C_XR(1); C_TL(1); uint32_t g2 = (uint32_t)G[1][c2 ^ (uint32_t)k2];
                    C_XR(1); uint32_t z = zp ^ g2;
                    uint32_t nidx = ((idx >> (2 * NB)) << NB) | z;
                    C_TL(1); C_XR(1); T2[nidx] ^= v;
                }
                for (int k3 = 0; k3 < Q; k3++) {
                    memset(T3, 0, n2);
                    for (uint32_t idx = 0; idx < n3; idx++) {
                        C_TL(1); uint8_t v = T2[idx];
                        uint32_t zp = idx & (uint32_t)MSK, c3 = (idx >> NB) & (uint32_t)MSK;
                        C_XR(1); C_TL(1); uint32_t g3 = (uint32_t)G[2][c3 ^ (uint32_t)k3];
                        C_XR(1); uint32_t z = zp ^ g3;
                        uint32_t nidx = ((idx >> (2 * NB)) << NB) | z;
                        C_TL(1); C_XR(1); T3[nidx] ^= v;
                    }
                    for (int k4 = 0; k4 < Q; k4++) {
                        memset(T4, 0, n1);
                        for (uint32_t idx = 0; idx < n2; idx++) {
                            C_TL(1); uint8_t v = T3[idx];
                            uint32_t zp = idx & (uint32_t)MSK, c4 = (idx >> NB) & (uint32_t)MSK;
                            C_XR(1); C_TL(1); uint32_t g4 = (uint32_t)G[3][c4 ^ (uint32_t)k4];
                            C_XR(1); uint32_t z = zp ^ g4;
                            C_TL(1); C_XR(1); T4[z] ^= v;
                        }
                        int g = 0;
                        for (uint32_t z = 0; z < n1; z++) {
                            C_TL(1);
                            if (T4[z] & 1) { C_TL(1); C_XR(1); g ^= C->sinv[z]; }
                        }
                        uint32_t kk = (uint32_t)k1 | ((uint32_t)k2 << NB)
                                    | ((uint32_t)k3 << (2 * NB)) | ((uint32_t)k4 << (3 * NB));
                        if (g != 0) alive[kk] = 0;
                    }
                }
            }
        }
    }
    free(T1); free(T2); free(T3); free(T4);
    CUR = NULL;
}

/* ------------------------------------------------------------------ *
 * REORG aggregation: 4-dimensional Walsh-Hadamard convolution          *
 * ------------------------------------------------------------------ */
static void wht(int64_t *a, uint32_t n) {           /* in-place, size n = 2^m */
    for (uint32_t len = 1; len < n; len <<= 1)
        for (uint32_t i = 0; i < n; i += (len << 1))
            for (uint32_t j = i; j < i + len; j++) {
                C_TL(2); int64_t u = a[j], v = a[j + len];
                C_AD(2); a[j] = u + v; a[j + len] = u - v;
            }
}

static void agg_reorg(const cipher_t *C, uint8_t **N0, int R, uint8_t *alive, ops_t *ops, ops_t *pre) {
    CUR = ops; memset(ops, 0, sizeof *ops);
    const uint32_t n4 = 1u << (4 * NB);
    int G[4][MAXQ]; build_G(C, G);

    uint8_t  *Z  = malloc(n4);
    int64_t  *WN = malloc((size_t)n4 * sizeof(int64_t));
    int64_t  *P  = malloc((size_t)n4 * sizeof(int64_t));
    int64_t **WF = malloc((size_t)NB * sizeof(int64_t *));
    if (!Z || !WN || !P || !WF) { fprintf(stderr, "FATAL: alloc\n"); exit(3); }
    for (int b = 0; b < NB; b++) {
        WF[b] = malloc((size_t)n4 * sizeof(int64_t));
        if (!WF[b]) { fprintf(stderr, "FATAL: alloc\n"); exit(3); }
    }
    static const int64_t SGN[2] = {1, -1};

    /* Z[x] = XOR_i G_i[x_i]; key- and structure-independent, built once. */
    for (uint32_t x4 = 0; x4 < (uint32_t)Q; x4++) {
        C_TL(1); uint32_t a = (uint32_t)G[3][x4];
        for (uint32_t x3 = 0; x3 < (uint32_t)Q; x3++) {
            C_TL(1); C_XR(1); uint32_t b = a ^ (uint32_t)G[2][x3];
            for (uint32_t x2 = 0; x2 < (uint32_t)Q; x2++) {
                C_TL(1); C_XR(1); uint32_t c = b ^ (uint32_t)G[1][x2];
                uint32_t base = (x4 << (3 * NB)) | (x3 << (2 * NB)) | (x2 << NB);
                for (uint32_t x1 = 0; x1 < (uint32_t)Q; x1++) {
                    C_TL(1); C_XR(1); Z[base | x1] = (uint8_t)(c ^ (uint32_t)G[0][x1]);
                }
            }
        }
    }
    /* WHT(F_u) for the n basis masks; key- and structure-independent. */
    for (int b = 0; b < NB; b++) {
        for (uint32_t x = 0; x < n4; x++) {
            C_TL(3);                       /* Z[x], sinv[.], SGN[.] */
            WF[b][x] = SGN[(C->sinv[Z[x]] >> b) & 1];
        }
        wht(WF[b], n4);
    }
    *pre = *ops;      /* key- and structure-independent precomputation so far */

    for (uint32_t i = 0; i < n4; i++) alive[i] = 1;

    for (int r = 0; r < R; r++) {
        for (uint32_t x = 0; x < n4; x++) { C_TL(1); WN[x] = (int64_t)N0[r][x]; }
        wht(WN, n4);
        C_TL(1); int64_t T = WN[0];                   /* T = SUM_c N0[c] */
        for (int b = 0; b < NB; b++) {
            for (uint32_t x = 0; x < n4; x++) { C_TL(2); C_ML(1); P[x] = WN[x] * WF[b][x]; }
            wht(P, n4);
            for (uint32_t k = 0; k < n4; k++) {
                C_TL(1); int64_t cu = P[k] / (int64_t)n4;
                C_AD(1); int64_t m = (T - cu) >> 1;
                if (m & 1) alive[k] = 0;
            }
        }
    }
    for (int b = 0; b < NB; b++) free(WF[b]);
    free(WF); free(P); free(WN); free(Z);
    CUR = NULL;
}

/* ------------------------------------------------------------------ */
static uint64_t fnv1a(const uint8_t *p, size_t n) {
    uint64_t h = 1469598103934665603ULL;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= 1099511628211ULL; }
    return h;
}
static double now_s(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static int POLYS[6] = {0, 0, 0, 0x0B, 0x13, 0x25};   /* n = 3,4,5 */

/* balance self-check: for the round-3 output, every cell XORs to 0 over a
 * structure.  This is the property the aggregation relies on. */
static int balance_check(const cipher_t *C, uint64_t struct_seed) {
    int pt[16], x3[16], acc[16]; memset(acc, 0, sizeof acc);
    uint64_t s = struct_seed;
    for (int i = 0; i < 16; i++) pt[i] = (int)(sm64(&s) & (uint64_t)MSK);
    const int act[4] = {0, 5, 10, 15};
    for (int a3 = 0; a3 < Q; a3++) { pt[act[3]] = a3;
    for (int a2 = 0; a2 < Q; a2++) { pt[act[2]] = a2;
    for (int a1 = 0; a1 < Q; a1++) { pt[act[1]] = a1;
    for (int a0 = 0; a0 < Q; a0++) { pt[act[0]] = a0;
        encrypt_to_r3(C, pt, x3);
        for (int i = 0; i < 16; i++) acc[i] ^= x3[i];
    }}}}
    for (int i = 0; i < 16; i++) if (acc[i]) return 0;
    return 1;
}

int main(int argc, char **argv) {
    uint64_t seed_base = (argc > 1) ? strtoull(argv[1], NULL, 0) : 20260731ULL;
    int R              = (argc > 2) ? atoi(argv[2]) : 5;
    int keys[6]; memset(keys, 0, sizeof keys);
    keys[3] = (argc > 3) ? atoi(argv[3]) : 8;
    keys[4] = (argc > 4) ? atoi(argv[4]) : 8;
    keys[5] = (argc > 5) ? atoi(argv[5]) : 2;

    /* S-box variants: 0 = algebraic (the cipher's own S-box);
     * 1,2 = NULL CONTROL, two independent seeded random bijections. */
    const char *vname[3] = {"algebraic", "random_bijection_A", "random_bijection_B"};
    uint64_t vseed[3]    = {0, seed_base ^ 0xA5A5A5A5ULL, seed_base ^ 0x5A5A5A5AULL};

    printf("{\n  \"schema\": \"gate_601b_measurements_v1\",\n");
    printf("  \"seed_base\": %llu,\n  \"structures_per_run\": %d,\n", (unsigned long long)seed_base, R);
    printf("  \"rounds\": %d,\n  \"state_cells\": 16,\n", RNDS);
    printf("  \"keys_per_cell_width\": {\"3\": %d, \"4\": %d, \"5\": %d},\n", keys[3], keys[4], keys[5]);
    printf("  \"argv\": \"");
    for (int i = 0; i < argc; i++) printf("%s%s", i ? " " : "", argv[i]);
    printf("\",\n");
    printf("  \"counting_convention\": \"TL=indexed array read; XR=XOR of a data or index value; AD=integer add/sub on a data value; ML=integer multiply on a data value; total=TL+XR+AD+ML. Not counted on either side: array writes, memset, loop bookkeeping, shifts/masks for bit-field packing, comparisons and branches. Shared preprocessing outside both counters: key setup, S-box construction, encryption, construction of the parity tables N0.\",\n");
    printf("  \"runs\": [\n");

    int first = 1;
    double t_all = now_s();
    for (int nb = 3; nb <= 5; nb++) {
        NB = nb; Q = 1 << nb; MSK = Q - 1; POLY = POLYS[nb];
        const uint32_t n4 = 1u << (4 * nb);
        uint8_t **N0 = malloc((size_t)R * sizeof(uint8_t *));
        for (int r = 0; r < R; r++) N0[r] = malloc(n4);
        uint8_t *a_dir = malloc(n4), *a_reo = malloc(n4);
        if (!N0 || !a_dir || !a_reo) { fprintf(stderr, "FATAL: alloc\n"); return 3; }

        for (int v = 0; v < 3; v++) {
            for (int ki = 0; ki < keys[nb]; ki++) {
                uint64_t key_seed = seed_base ^ (0x1000ULL * (uint64_t)nb) ^ (0x100ULL * (uint64_t)v) ^ (uint64_t)ki;
                cipher_t C; build_cipher(&C, v == 0 ? 0 : 1, vseed[v] ^ (uint64_t)nb, key_seed);

                uint64_t bseed = key_seed ^ 0xBEEFULL;
                int bal = balance_check(&C, bseed);

                /* counting-symmetry probe: build_G() is the SAME function
                 * called by both aggregations; its standalone cost is emitted
                 * so that the shared component of both counters is visible. */
                ops_t og; memset(&og, 0, sizeof og); CUR = &og;
                { int Gp[4][MAXQ]; build_G(&C, Gp); (void)Gp; }
                CUR = NULL;

                double t0 = now_s();
                for (int r = 0; r < R; r++)
                    build_N0(&C, key_seed ^ (0xD00DULL * (uint64_t)(r + 1)), N0[r], n4);
                double t_data = now_s() - t0;

                ops_t od, orr, pd, pr;
                t0 = now_s(); agg_direct(&C, N0, R, a_dir, &od, &pd);  double t_dir = now_s() - t0;
                t0 = now_s(); agg_reorg (&C, N0, R, a_reo, &orr, &pr); double t_reo = now_s() - t0;

                uint32_t nd = 0, nr = 0;
                for (uint32_t i = 0; i < n4; i++) { nd += a_dir[i]; nr += a_reo[i]; }
                int identical = (memcmp(a_dir, a_reo, n4) == 0);
                uint32_t tk = true_guess(&C);

                if (!first) printf(",\n");
                first = 0;
                printf("    {\"cell_bits\": %d, \"guess_space\": %u, \"sbox_variant\": \"%s\",\n", nb, n4, vname[v]);
                printf("     \"sbox_seed\": %llu, \"key_index\": %d, \"key_seed\": %llu, \"structure_seed_base\": %llu,\n",
                       (unsigned long long)(v == 0 ? 0ULL : (vseed[v] ^ (uint64_t)nb)), ki,
                       (unsigned long long)key_seed, (unsigned long long)key_seed);
                printf("     \"affine_taps\": %d, \"affine_const\": %d, \"mixcolumns_row\": [%d,%d,%d,%d], \"mixcolumns_inv_row0\": [%d,%d,%d,%d], \"balance_selfcheck\": %s,\n",
                       C.affine_taps, C.affine_const,
                       C.mc_row[0], C.mc_row[1], C.mc_row[2], C.mc_row[3],
                       C.Minv[0][0], C.Minv[0][1], C.Minv[0][2], C.Minv[0][3],
                       bal ? "true" : "false");
                printf("     \"survivors_direct\": %u, \"survivors_reorg\": %u,\n", nd, nr);
                printf("     \"digest_direct\": \"%016llx\", \"digest_reorg\": \"%016llx\",\n",
                       (unsigned long long)fnv1a(a_dir, n4), (unsigned long long)fnv1a(a_reo, n4));
                printf("     \"sets_identical\": %s, \"true_guess\": %u, \"true_guess_survives_direct\": %s, \"true_guess_survives_reorg\": %s,\n",
                       identical ? "true" : "false", tk, a_dir[tk] ? "true" : "false", a_reo[tk] ? "true" : "false");
                printf("     \"ops_direct\": {\"table_lookups\": %llu, \"xors\": %llu, \"adds\": %llu, \"muls\": %llu, \"total\": %llu},\n",
                       (unsigned long long)od.tl, (unsigned long long)od.xr, (unsigned long long)od.ad,
                       (unsigned long long)od.ml, (unsigned long long)ops_total(&od));
                printf("     \"ops_reorg\": {\"table_lookups\": %llu, \"xors\": %llu, \"adds\": %llu, \"muls\": %llu, \"total\": %llu},\n",
                       (unsigned long long)orr.tl, (unsigned long long)orr.xr, (unsigned long long)orr.ad,
                       (unsigned long long)orr.ml, (unsigned long long)ops_total(&orr));
                printf("     \"ops_shared_build_G\": {\"table_lookups\": %llu, \"muls\": %llu, \"total\": %llu},\n",
                       (unsigned long long)og.tl, (unsigned long long)og.ml, (unsigned long long)ops_total(&og));
                printf("     \"ops_direct_precompute_total\": %llu, \"ops_reorg_precompute_total\": %llu,\n",
                       (unsigned long long)ops_total(&pd), (unsigned long long)ops_total(&pr));
                printf("     \"ops_direct_per_structure_total\": %llu, \"ops_reorg_per_structure_total\": %llu,\n",
                       (unsigned long long)((ops_total(&od) - ops_total(&pd)) / (uint64_t)R),
                       (unsigned long long)((ops_total(&orr) - ops_total(&pr)) / (uint64_t)R));
                printf("     \"ratio_reorg_over_direct\": %.12f,\n",
                       (double)ops_total(&orr) / (double)ops_total(&od));
                printf("     \"wall_clock_seconds\": {\"data\": %.3f, \"direct\": %.3f, \"reorg\": %.3f}}",
                       t_data, t_dir, t_reo);
                fflush(stdout);
            }
        }
        for (int r = 0; r < R; r++) free(N0[r]);
        free(N0); free(a_dir); free(a_reo);
    }
    printf("\n  ],\n  \"total_wall_clock_seconds\": %.3f\n}\n", now_s() - t_all);
    return 0;
}
