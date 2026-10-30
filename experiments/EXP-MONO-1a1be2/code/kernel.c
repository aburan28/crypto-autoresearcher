/* EXP-MONO-1a1be2 compiled inner loops (TASK-20261029-a97206, IM-7).
 *
 * Affine Weierstrass arithmetic over F_Q = F_q[t]/(g), Q = q^n, n <= 7, and the
 * enumerations the contract needs: ordered tuples, multisets, x-multisets with
 * canonical sign patterns, S-set marking, and the target-sampled arm-C counter.
 * Built at run time by counters.build_kernel into a temporary directory; no binary
 * is committed. All entry points are plain C for ctypes.
 *
 * Target index: idx(P) = 2*code(x) + [code(y) > code(-y)], idx(O) = 2Q, where
 * code(e) = sum_i e.c[i] q^i. A target array has 2Q+1 slots.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 8
typedef struct { uint32_t c[MAXN]; } elt;
typedef struct { int inf; elt x, y; } pt;

static int n_ = 1;
static uint32_t q_ = 3;
static uint64_t Q_ = 3;
static uint32_t G_[MAXN];
static uint32_t *invq_ = NULL;
static int8_t *chiq_ = NULL;
static elt FR_[MAXN];
static elt A_, B_;
static int ref_arith_ = 0;

/* ---------------------------------------------------------------- field */
#define TABLE_Q_MAX (1u << 20)      /* inverse and chi tables only for q up to this; otherwise pow in F_q */
static uint32_t powq(uint64_t a, uint64_t e) {
    uint64_t r = 1, b = a % q_;
    while (e) { if (e & 1) r = r * b % q_; b = b * b % q_; e >>= 1; }
    return (uint32_t)r;
}
static inline uint32_t inv_scalar(uint32_t a) { return invq_ ? invq_[a] : powq(a, (uint64_t)q_ - 2); }
static inline int chi_scalar(uint32_t a) {
    if (chiq_) return chiq_[a];
    if (a == 0) return 0;
    return powq(a, (q_ - 1) / 2) == 1 ? 1 : -1;
}
static inline void e_zero_set(elt *r) { memset(r, 0, sizeof(elt)); }
static inline void e_add(elt *r, const elt *a, const elt *b) {
    for (int i = 0; i < n_; i++) { uint32_t s = a->c[i] + b->c[i]; if (s >= q_) s -= q_; r->c[i] = s; }
}
static inline void e_sub(elt *r, const elt *a, const elt *b) {
    for (int i = 0; i < n_; i++) { uint32_t s = a->c[i] + q_ - b->c[i]; if (s >= q_) s -= q_; r->c[i] = s; }
}
static inline void e_neg(elt *r, const elt *a) {
    for (int i = 0; i < n_; i++) r->c[i] = a->c[i] ? q_ - a->c[i] : 0;
}
static inline int e_iszero(const elt *a) {
    for (int i = 0; i < n_; i++) if (a->c[i]) return 0;
    return 1;
}
static inline int e_scalar(const elt *a) {
    for (int i = 1; i < n_; i++) if (a->c[i]) return 0;
    return 1;
}
static inline void e_mul_s(elt *r, const elt *a, uint32_t s) {
    for (int i = 0; i < n_; i++) r->c[i] = (uint32_t)(((uint64_t)a->c[i] * s) % q_);
}
static void e_mul(elt *r, const elt *a, const elt *b) {
    uint64_t acc[2 * MAXN];
    int n = n_;
    for (int k = 0; k < 2 * n - 1; k++) acc[k] = 0;
    for (int i = 0; i < n; i++) {
        uint64_t ai = a->c[i];
        if (!ai) continue;
        for (int j = 0; j < n; j++) acc[i + j] += ai * b->c[j];
    }
    for (int k = 0; k < 2 * n - 1; k++) acc[k] %= q_;
    for (int k = 2 * n - 2; k >= n; k--) {
        uint64_t c = acc[k];
        if (!c) continue;
        for (int j = 0; j < n; j++) {
            uint64_t add = c * (uint64_t)(G_[j] ? q_ - G_[j] : 0);
            acc[k - n + j] = (acc[k - n + j] + add) % q_;
        }
    }
    for (int i = 0; i < n; i++) r->c[i] = (uint32_t)acc[i];
}
static void e_pow(elt *r, const elt *a, uint64_t e) {
    elt res, base = *a, t;
    e_zero_set(&res); res.c[0] = 1;
    while (e) {
        if (e & 1) { e_mul(&t, &res, &base); res = t; }
        e >>= 1;
        if (e) { e_mul(&t, &base, &base); base = t; }
    }
    *r = res;
}
static void e_frob(elt *r, const elt *z) {
    elt out; e_zero_set(&out);
    for (int j = 0; j < n_; j++) {
        if (!z->c[j]) continue;
        for (int i = 0; i < n_; i++)
            out.c[i] = (uint32_t)((out.c[i] + (uint64_t)z->c[j] * FR_[j].c[i]) % q_);
    }
    *r = out;
}
/* inverse of nonzero z. Norm method by default; Fermat z^(Q-2) in reference mode. */
static void e_inv(elt *r, const elt *z) {
    if (e_scalar(z)) { e_zero_set(r); r->c[0] = inv_scalar(z->c[0]); return; }
    if (ref_arith_) { e_pow(r, z, Q_ - 2); return; }
    elt cur, acc, nm, t;
    e_frob(&cur, z); acc = cur;
    for (int i = 2; i < n_; i++) { e_frob(&t, &cur); cur = t; e_mul(&t, &acc, &cur); acc = t; }
    e_mul(&nm, z, &acc);               /* norm, a scalar in F_q */
    e_mul_s(r, &acc, inv_scalar(nm.c[0]));
}
static inline uint64_t e_code(const elt *a) {
    uint64_t r = 0;
    for (int i = n_ - 1; i >= 0; i--) r = r * q_ + a->c[i];
    return r;
}
static inline void e_from_code(elt *r, uint64_t code) {
    e_zero_set(r);
    for (int i = 0; i < n_; i++) { r->c[i] = (uint32_t)(code % q_); code /= q_; }
}

int kinit(int n, uint32_t q, const uint32_t *g) {
    if (n < 1 || n > 7) return -1;
    n_ = n; q_ = q; Q_ = 1;
    for (int i = 0; i < n; i++) Q_ *= q;
    for (int i = 0; i < MAXN; i++) G_[i] = 0;
    for (int i = 0; i < n; i++) G_[i] = g[i];
    free(invq_); invq_ = NULL;
    free(chiq_); chiq_ = NULL;
    if (q <= TABLE_Q_MAX) {
        invq_ = (uint32_t *)calloc(q, sizeof(uint32_t));
        chiq_ = (int8_t *)calloc(q, 1);
        if (!invq_ || !chiq_) return -2;
        for (uint32_t a = 1; a < q; a++) {              /* Fermat in F_q (q prime) */
            uint64_t r = 1, b = a, e = q - 2;
            while (e) { if (e & 1) r = r * b % q; b = b * b % q; e >>= 1; }
            invq_[a] = (uint32_t)r;
        }
        for (uint32_t a = 1; a < q; a++) chiq_[a] = -1;
        for (uint64_t a = 1; a < q; a++) chiq_[(a * a) % q] = 1;
    }
    /* Frobenius table FR_[j] = (t^q)^j */
    elt tt; e_zero_set(&tt);
    if (n == 1) { tt.c[0] = 0; }      /* t = 0 in F_q[t]/(t); Frobenius is identity */
    else tt.c[1] = 1;
    elt tq; e_pow(&tq, &tt, q);
    if (n == 1) { e_zero_set(&tq); }
    elt one; e_zero_set(&one); one.c[0] = 1;
    FR_[0] = one;
    for (int j = 1; j < n; j++) { elt t2; e_mul(&t2, &FR_[j - 1], &tq); FR_[j] = t2; }
    return 0;
}
void kset_curve(const uint32_t *a, const uint32_t *b) {
    e_zero_set(&A_); e_zero_set(&B_);
    for (int i = 0; i < n_; i++) { A_.c[i] = a[i]; B_.c[i] = b[i]; }
}
void kset_ref(int flag) { ref_arith_ = flag; }

/* ---------------------------------------------------------------- group */
static void p_add(pt *r, const pt *p, const pt *s) {
    if (p->inf) { *r = *s; return; }
    if (s->inf) { *r = *p; return; }
    elt dx, dy, lam, t, u, x3, y3;
    e_sub(&dx, &s->x, &p->x);
    if (e_iszero(&dx)) {
        e_add(&t, &p->y, &s->y);
        if (e_iszero(&t)) { r->inf = 1; return; }
        e_mul(&u, &p->x, &p->x);
        e_add(&t, &u, &u); e_add(&t, &t, &u); e_add(&t, &t, &A_);
        e_add(&dy, &p->y, &p->y);
        e_inv(&u, &dy);
        e_mul(&lam, &t, &u);
    } else {
        e_sub(&dy, &s->y, &p->y);
        if (e_scalar(&dx)) e_mul_s(&lam, &dy, inv_scalar(dx.c[0]));
        else { e_inv(&u, &dx); e_mul(&lam, &dy, &u); }
    }
    e_mul(&t, &lam, &lam);
    e_sub(&x3, &t, &p->x); e_sub(&x3, &x3, &s->x);
    e_sub(&t, &p->x, &x3); e_mul(&y3, &lam, &t); e_sub(&y3, &y3, &p->y);
    r->inf = 0; r->x = x3; r->y = y3;
}
static inline uint64_t p_idx(const pt *p) {
    if (p->inf) return 2 * Q_;
    elt ny; e_neg(&ny, &p->y);
    uint64_t yc = e_code(&p->y), nyc = e_code(&ny);
    return 2 * e_code(&p->x) + (yc > nyc ? 1 : 0);
}
uint64_t kpoint_index(const uint32_t *x, const uint32_t *y, int inf) {
    pt p; p.inf = inf; e_zero_set(&p.x); e_zero_set(&p.y);
    for (int i = 0; i < n_; i++) { p.x.c[i] = x[i]; p.y.c[i] = y[i]; }
    return p_idx(&p);
}
/* P + S for single points, exposed for tests; out arrays of n coefficients. */
int kadd(const uint32_t *x1, const uint32_t *y1, int inf1, const uint32_t *x2, const uint32_t *y2, int inf2,
         uint32_t *xo, uint32_t *yo) {
    pt p, s, r;
    p.inf = inf1; s.inf = inf2; e_zero_set(&p.x); e_zero_set(&p.y); e_zero_set(&s.x); e_zero_set(&s.y);
    for (int i = 0; i < n_; i++) { p.x.c[i] = x1[i]; p.y.c[i] = y1[i]; s.x.c[i] = x2[i]; s.y.c[i] = y2[i]; }
    p_add(&r, &p, &s);
    if (r.inf) return 1;
    for (int i = 0; i < n_; i++) { xo[i] = r.x.c[i]; yo[i] = r.y.c[i]; }
    return 0;
}
int kmul_test(const uint32_t *a, const uint32_t *b, uint32_t *o) {
    elt x, y, r; e_zero_set(&x); e_zero_set(&y);
    for (int i = 0; i < n_; i++) { x.c[i] = a[i]; y.c[i] = b[i]; }
    e_mul(&r, &x, &y);
    for (int i = 0; i < n_; i++) o[i] = r.c[i];
    return 0;
}
int kinv_test(const uint32_t *a, uint32_t *o) {
    elt x, r; e_zero_set(&x);
    for (int i = 0; i < n_; i++) x.c[i] = a[i];
    if (e_iszero(&x)) return 1;
    e_inv(&r, &x);
    for (int i = 0; i < n_; i++) o[i] = r.c[i];
    return 0;
}

/* ------------------------------------------------------- point counting */
/* Exhaustive count of E(F_Q). Marks squares in a bitset, then sums over x.
 * If mask != NULL (2Q+1 bytes) it sets bit 1 on every point index (valid target)
 * and bit 2 on O and on the 2-torsion points. Returns N. */
uint64_t kcount_points(uint8_t *mask) {
    uint64_t nbytes = (Q_ + 7) / 8;
    uint8_t *sq = (uint8_t *)calloc(nbytes, 1);
    if (!sq) return 0;
    elt w, w2; e_zero_set(&w);
    for (uint64_t code = 0; code < Q_; code++) {
        e_mul(&w2, &w, &w);
        uint64_t c2 = e_code(&w2);
        sq[c2 >> 3] |= (uint8_t)(1u << (c2 & 7));
        for (int i = 0; i < n_; i++) { if (++w.c[i] < q_) break; w.c[i] = 0; }
    }
    uint64_t total = 1;
    elt x, x2, x3, ax, f; e_zero_set(&x);
    if (mask) { mask[2 * Q_] = 1 | 2; }
    for (uint64_t code = 0; code < Q_; code++) {
        e_mul(&x2, &x, &x); e_mul(&x3, &x2, &x); e_mul(&ax, &A_, &x);
        e_add(&f, &x3, &ax); e_add(&f, &f, &B_);
        if (e_iszero(&f)) {
            total += 1;
            if (mask) mask[2 * code] = 1 | 2;
        } else {
            uint64_t fc = e_code(&f);
            if (sq[fc >> 3] & (1u << (fc & 7))) {
                total += 2;
                if (mask) { mask[2 * code] = 1; mask[2 * code + 1] = 1; }
            }
        }
        for (int i = 0; i < n_; i++) { if (++x.c[i] < q_) break; x.c[i] = 0; }
    }
    free(sq);
    return total;
}

/* ---------------------------------------------------------- enumeration */
enum { K_ORD = 0, K_ORD2 = 1, K_MS = 2, K_MSW = 3, K_XM = 4, K_MARK = 5 };

typedef struct {
    int kind, m, nb;
    pt *base, *nbase;
    int *is2, *negpos;
    uint32_t *hist, *hist2;
    uint8_t *mask;
    uint64_t n_leaf, n_cf, overflow;
    uint64_t fact[MAXN + 1];
    int *cnt;
    /* sampled */
    uint64_t *tkeys; int32_t *tslot; uint64_t tmask; int nsampled;
    uint32_t *counts; uint64_t m_S, n_S_leaf;
    /* x-multiset */
    int xi[MAXN]; uint64_t buf[256]; int nbuf;
    uint64_t *out; int64_t cap, ncollect;
} ctx_t;
static ctx_t E;

static inline void hist_inc(uint32_t *h, uint64_t i, uint64_t w) {
    if ((uint64_t)h[i] + w > 0xFFFFFFFFull) { E.overflow = 1; return; }
    h[i] += (uint32_t)w;
}

static inline uint64_t hmix(uint64_t k) { return (k * 0x9E3779B97F4A7C15ull) >> 20; }
static inline int tlookup(uint64_t key) {
    uint64_t h = hmix(key) & E.tmask;
    while (E.tkeys[h] != ~0ull) {
        if (E.tkeys[h] == key) return E.tslot[h];
        h = (h + 1) & E.tmask;
    }
    return -1;
}

static void leaf_ms(const pt *sum, int viol, uint64_t den) {
    E.n_leaf++;
    if (viol == 0) E.n_cf++;
    uint64_t idx = p_idx(sum);
    switch (E.kind) {
        case K_MS: hist_inc(E.hist, idx, 1); break;
        case K_MSW: hist_inc(E.hist, idx, E.fact[E.m] / den); break;
        case K_MARK: E.mask[idx] |= 4; break;
        case 7: if (E.ncollect < E.cap) E.out[E.ncollect] = idx; E.ncollect++; break;
        case 6: { /* sampled */
            int s = tlookup(idx);
            if (s >= 0) {
                E.counts[s]++;
                if (s >= E.nsampled && viol == 0) E.m_S++;
            }
            break;
        }
    }
}

static void rec_ms(int d, int start, const pt *sum, int viol, int last, int run, uint64_t den) {
    if (d == E.m) { leaf_ms(sum, viol, den); return; }
    pt next;
    for (int k = start; k < E.nb; k++) {
        int nv = viol;
        int nk = E.negpos[k];
        if (nk == k) { if (E.cnt[k] > 0) nv++; }
        else if (nk >= 0 && E.cnt[nk] > 0) nv++;
        int nr = (k == last) ? run + 1 : 1;
        uint64_t nd = den * (uint64_t)nr;
        if (d == 0) next = E.base[k]; else p_add(&next, sum, &E.base[k]);
        E.cnt[k]++;
        rec_ms(d + 1, k, &next, nv, k, nr, nd);
        E.cnt[k]--;
    }
}

static void rec_ord(int d, const pt *sum, uint64_t w) {
    if (d == E.m) {
        E.n_leaf++;
        hist_inc(E.hist, p_idx(sum), w);
        return;
    }
    pt next;
    for (int k = 0; k < E.nb; k++) {
        if (d == 0) next = E.base[k]; else p_add(&next, sum, &E.base[k]);
        rec_ord(d + 1, &next, (E.kind == K_ORD2 && E.is2[k]) ? w * 2 : w);
    }
}

static void rec_sg(int d, const pt *sum, int prevs) {
    if (d == E.m) { E.buf[E.nbuf++] = p_idx(sum); return; }
    int k = E.xi[d];
    pt next;
    for (int s = 1; s >= 0; s--) {                 /* 1 = +, 0 = - */
        if (E.is2[k] && s == 0) continue;
        if (d > 0 && E.xi[d - 1] == k && s > prevs) continue;
        const pt *P = s ? &E.base[k] : &E.nbase[k];
        if (d == 0) next = *P; else p_add(&next, sum, P);
        rec_sg(d + 1, &next, s);
    }
}
static void xm_leaf(void) {
    E.nbuf = 0;
    pt z; z.inf = 1;
    rec_sg(0, &z, 1);
    int nb = E.nbuf;
    for (int i = 1; i < nb; i++) {                 /* insertion sort */
        uint64_t v = E.buf[i]; int j = i - 1;
        while (j >= 0 && E.buf[j] > v) { E.buf[j + 1] = E.buf[j]; j--; }
        E.buf[j + 1] = v;
    }
    E.n_leaf++;
    int i = 0;
    while (i < nb) {
        int j = i;
        while (j < nb && E.buf[j] == E.buf[i]) j++;
        hist_inc(E.hist, E.buf[i], 1);                         /* T_X: distinct sums */
        hist_inc(E.hist2, E.buf[i], (uint64_t)(j - i));        /* T_M recount */
        i = j;
    }
}
static void rec_xm(int d, int start) {
    if (d == E.m) { xm_leaf(); return; }
    for (int k = start; k < E.nb; k++) { E.xi[d] = k; rec_xm(d + 1, k); }
}

static int cmp_pair(const void *a, const void *b) {
    const uint64_t *x = (const uint64_t *)a, *y = (const uint64_t *)b;
    return (x[0] > y[0]) - (x[0] < y[0]);
}
static int setup_base(int m, int nb, const uint32_t *bx, const uint32_t *by) {
    memset(&E, 0, sizeof(E));
    E.m = m; E.nb = nb;
    E.base = (pt *)calloc(nb ? nb : 1, sizeof(pt));
    E.nbase = (pt *)calloc(nb ? nb : 1, sizeof(pt));
    E.is2 = (int *)calloc(nb ? nb : 1, sizeof(int));
    E.negpos = (int *)calloc(nb ? nb : 1, sizeof(int));
    E.cnt = (int *)calloc(nb ? nb : 1, sizeof(int));
    uint64_t *pairs = (uint64_t *)malloc(2 * (nb ? nb : 1) * sizeof(uint64_t));
    if (!E.base || !E.nbase || !E.is2 || !E.negpos || !E.cnt || !pairs) return -1;
    E.fact[0] = 1;
    for (int i = 1; i <= MAXN; i++) E.fact[i] = E.fact[i - 1] * i;
    for (int k = 0; k < nb; k++) {
        E.base[k].inf = 0; e_zero_set(&E.base[k].x); e_zero_set(&E.base[k].y);
        for (int i = 0; i < n_; i++) { E.base[k].x.c[i] = bx[k * n_ + i]; E.base[k].y.c[i] = by[k * n_ + i]; }
        E.nbase[k] = E.base[k];
        e_neg(&E.nbase[k].y, &E.base[k].y);
        E.is2[k] = e_iszero(&E.base[k].y);
        pairs[2 * k] = p_idx(&E.base[k]); pairs[2 * k + 1] = (uint64_t)k;
    }
    qsort(pairs, nb, 2 * sizeof(uint64_t), cmp_pair);
    for (int k = 0; k < nb; k++) {
        uint64_t key = p_idx(&E.nbase[k]);
        int lo = 0, hi = nb - 1, found = -1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (pairs[2 * mid] == key) { found = (int)pairs[2 * mid + 1]; break; }
            if (pairs[2 * mid] < key) lo = mid + 1; else hi = mid - 1;
        }
        E.negpos[k] = found;       /* position of -P_k (duplicates: first match); -1 if absent */
    }
    free(pairs);
    return 0;
}
static void free_base(void) {
    free(E.base); free(E.nbase); free(E.is2); free(E.negpos); free(E.cnt);
    free(E.tkeys); free(E.tslot);
    memset(&E, 0, sizeof(E));
}

/* kinds: 0 ordered, 1 ordered weighted 2^j, 2 multiset, 3 multiset weighted n!/prod m_j!,
 * 4 x-multiset canonical signs (hist = T_X, hist2 = T_M recount), 5 mark sums of m-multisets in mask.
 * stats[0] = leaves, stats[1] = cancellation-free leaves (kinds 2,3,5), stats[2] = overflow flag. */
int krun(int kind, int m, int nb, const uint32_t *bx, const uint32_t *by,
         uint32_t *hist, uint32_t *hist2, uint8_t *mask, uint64_t *stats) {
    if (m < 0 || m > 7 || nb < 0) return -3;
    if (setup_base(m, nb, bx, by)) return -1;
    E.kind = kind; E.hist = hist; E.hist2 = hist2; E.mask = mask;
    pt z; z.inf = 1;
    switch (kind) {
        case K_ORD: case K_ORD2: rec_ord(0, &z, 1); break;
        case K_MS: case K_MSW: case K_MARK: rec_ms(0, 0, &z, 0, -1, 0, 1); break;
        case K_XM: rec_xm(0, 0); break;
        default: free_base(); return -4;
    }
    stats[0] = E.n_leaf; stats[1] = E.n_cf; stats[2] = E.overflow;
    free_base();
    return 0;
}

/* Arm-C counter. keys[0..nsampled) are the sampled target indices, keys[nsampled..nkeys)
 * the S-set indices (cancelling-sum targets, kept separate). counts has nkeys slots.
 * stats: [0] multisets, [1] cancellation-free multisets, [2] m_S (cancellation-free multisets
 * summing into S), [3] overflow. */
int krun_sampled(int m, int nb, const uint32_t *bx, const uint32_t *by,
                 int64_t nkeys, const uint64_t *keys, int64_t nsampled, uint32_t *counts, uint64_t *stats) {
    if (setup_base(m, nb, bx, by)) return -1;
    uint64_t sz = 4;
    while (sz < (uint64_t)(2 * nkeys + 2)) sz <<= 1;
    E.tkeys = (uint64_t *)malloc(sz * sizeof(uint64_t));
    E.tslot = (int32_t *)malloc(sz * sizeof(int32_t));
    if (!E.tkeys || !E.tslot) { free_base(); return -2; }
    memset(E.tkeys, 0xFF, sz * sizeof(uint64_t));
    E.tmask = sz - 1;
    for (int64_t i = 0; i < nkeys; i++) {
        uint64_t h = hmix(keys[i]) & E.tmask;
        int dup = 0;
        while (E.tkeys[h] != ~0ull) { if (E.tkeys[h] == keys[i]) { dup = 1; break; } h = (h + 1) & E.tmask; }
        if (dup) { free_base(); return -5; }       /* keys must be distinct */
        E.tkeys[h] = keys[i]; E.tslot[h] = (int32_t)i;
    }
    E.kind = 6; E.counts = counts; E.nsampled = (int)nsampled;
    pt z; z.inf = 1;
    rec_ms(0, 0, &z, 0, -1, 0, 1);
    stats[0] = E.n_leaf; stats[1] = E.n_cf; stats[2] = E.m_S; stats[3] = E.overflow;
    free_base();
    return 0;
}

/* Histograms of per-target counts over valid targets. mask bit0 valid, bit1 special (O, E[2]),
 * bit2 in S. out_all counts every valid target; out_gen only valid and not special and not in S.
 * Returns the largest count seen; counts above maxc are lumped into the last bin and flagged by
 * returning maxc+1. */
int64_t khist_stats(const uint32_t *hist, const uint8_t *mask, uint64_t size, int64_t maxc,
                    uint64_t *out_all, uint64_t *out_gen) {
    int64_t mx = 0;
    for (uint64_t i = 0; i < size; i++) {
        if (!(mask[i] & 1)) continue;
        int64_t c = hist[i];
        if (c > maxc) return maxc + 1;
        if (c > mx) mx = c;
        out_all[c]++;
        if (!(mask[i] & 6)) out_gen[c]++;
    }
    return mx;
}
/* Compare two count arrays over valid targets with (mask & skip) == 0.
 * out[0] = targets with h1 != h2, out[1] = h1 < h2, out[2] = h1 > h2, out[3] = targets compared. */
void kcmp(const uint32_t *h1, const uint32_t *h2, const uint8_t *mask, uint64_t size, uint8_t skip, uint64_t *out) {
    out[0] = out[1] = out[2] = out[3] = 0;
    for (uint64_t i = 0; i < size; i++) {
        if (!(mask[i] & 1) || (mask[i] & skip)) continue;
        out[3]++;
        if (h1[i] != h2[i]) { out[0]++; if (h1[i] < h2[i]) out[1]++; else out[2]++; }
    }
}
/* Set mask bit 2 at the given target indices (O, 2-torsion). */
void kmark_special(uint8_t *mask, const uint64_t *idx, int64_t k) {
    for (int64_t i = 0; i < k; i++) mask[idx[i]] |= 2;
}
/* Sum of the counts over valid targets (exact) and over indices in [lo,hi). */
uint64_t khist_sum(const uint32_t *hist, const uint8_t *mask, uint64_t size) {
    uint64_t s = 0;
    for (uint64_t i = 0; i < size; i++) if (mask[i] & 1) s += hist[i];
    return s;
}

/* Quadratic character of f(x) = x^3 + a x + b for cnt x-tuples (n coefficients each):
 * out[i] = +1 / -1 / 0. chi_Q(z) = chi_q(Norm(z)). */
void kchi_batch(const uint32_t *xs, int64_t cnt, int8_t *out) {
    for (int64_t k = 0; k < cnt; k++) {
        elt x, x2, x3, ax, f; e_zero_set(&x);
        for (int i = 0; i < n_; i++) x.c[i] = xs[k * n_ + i];
        e_mul(&x2, &x, &x); e_mul(&x3, &x2, &x); e_mul(&ax, &A_, &x);
        e_add(&f, &x3, &ax); e_add(&f, &f, &B_);
        if (e_iszero(&f)) { out[k] = 0; continue; }
        elt cur = f, acc = f, t;
        for (int i = 1; i < n_; i++) { e_frob(&t, &cur); cur = t; e_mul(&t, &acc, &cur); acc = t; }
        out[k] = (int8_t)chi_scalar(acc.c[0]);
    }
}

/* All sums of m-multisets of the base, as target indices (with repetition), into out[0..cap).
 * Returns the number of multisets (may exceed cap; then only the first cap were stored). */
int64_t kcollect(int m, int nb, const uint32_t *bx, const uint32_t *by, uint64_t *out, int64_t cap) {
    if (setup_base(m, nb, bx, by)) return -1;
    E.kind = 7; E.out = out; E.cap = cap; E.ncollect = 0;
    pt z; z.inf = 1;
    rec_ms(0, 0, &z, 0, -1, 0, 1);
    int64_t n = E.ncollect;
    free_base();
    return n;
}
