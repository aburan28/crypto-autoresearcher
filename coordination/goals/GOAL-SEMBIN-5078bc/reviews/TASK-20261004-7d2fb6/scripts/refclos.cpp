// refclos.cpp -- reviewer's own reference for the degree-capped Boolean closure W_D and a saturation verifier.
// SCRATCH (TASK-20261004-7d2fb6, joint W5). Independent of closure.c: no shared code, a different algorithm
// (worklist over every INSERTED vector, non-reduced echelon, hash-map column index), and the monomial ORDER and
// the multiplier BUDGET are implemented literally from the Coordinator's statement on the task card, not from the
// column layout of closure.c.
//
// Statement being implemented (card statement_for_W5_quantity):
//   B = F_2[x_1..x_N]/(x_i^2+x_i); monomial = subset of {1..N} (here bit i-1); product of monomials = union.
//   ORDER: size first (larger size = larger monomial); equal size: m is LARGER than m' iff the LARGEST variable
//   index in m XOR m' belongs to m'.  LM(f) = largest monomial of f.  deg f = largest monomial size of f.
//   W_D = smallest F_2-subspace of {f : deg f <= D} containing every generator and, for every f in W and every
//   squarefree monomial mu with 1 <= |mu| <= D - deg f, containing mu*f.
//   N_std = # squarefree monomials (all sizes 0..N) containing no member of LM(W) as a subset.
//
// Modes
//   refclos closure GENS.sys D OUTPREFIX          compute W_D; write OUTPREFIX.stats, OUTPREFIX.lm (leading masks in ORDER
//                                                 descending), OUTPREFIX.rref (binary RREF rows, only if RREF=1 in env)
//   refclos compare GENS.sys D GIVEN.bin          compute W_D, then test GIVEN (rows of another implementation, binary
//                                                 mask lists) for inclusion in W_D; prints rank_ref, rank_given, #given rows
//                                                 not in W_D, #reference rows not in span(GIVEN)
//   refclos saturate GENS.sys D GIVEN.bin         saturation check on the span of GIVEN: every generator in the span, and for
//                                                 every echelon vector r of the span and every mu with 1<=|mu|<=D-deg(LM r)
//                                                 mu*r reduces to 0. Prints the violation count and the first violation.
// File formats
//   GENS.sys: "N ngens" then per generator "cnt mask1 ... maskcnt"   (masks decimal, bit i <-> variable x_{i+1})
//   GIVEN.bin: repeated records [u32 count][count x u64 masks]
#include <bits/stdc++.h>
using namespace std;
typedef uint64_t u64;
static int N, D;
static vector<u64> colmask;               // column -> monomial
static unordered_map<u64, int> colidx;    // monomial -> column
static int ncols, W;

static inline int pc(u64 x) { return __builtin_popcountll(x); }
// a is LARGER than b in the statement's ORDER
static bool larger(u64 a, u64 b) {
    int sa = pc(a), sb = pc(b);
    if (sa != sb) return sa > sb;
    u64 x = a ^ b;
    if (!x) return false;
    int hb = 63 - __builtin_clzll(x);   // largest variable index in the symmetric difference
    return (b >> hb) & 1;               // belongs to b  =>  a is larger
}
static void build_columns() {
    // enumerate all squarefree monomials of size <= D by recursion (not Gosper), then sort by ORDER, largest first
    vector<u64> all;
    function<void(int, int, u64)> rec = [&](int start, int left, u64 cur) {
        all.push_back(cur);
        if (left == 0) return;
        for (int v = start; v < N; v++) rec(v + 1, left - 1, cur | (1ULL << v));
    };
    rec(0, D, 0);
    sort(all.begin(), all.end(), [](u64 a, u64 b) { return larger(a, b); });
    colmask = all; ncols = (int)all.size(); W = (ncols + 63) / 64;
    colidx.reserve(ncols * 2);
    for (int j = 0; j < ncols; j++) colidx[colmask[j]] = j;
}
typedef vector<u64> Row;
static vector<Row> rows;                // echelon vectors in insertion order
static vector<int> pivrow;              // column -> index in rows or -1
static vector<int> rowpiv;              // row -> leading column

// reduce v in place; return its leading column after reduction, or -1 if zero
static int reduce(Row &v) {
    for (int w = 0; w < W; w++) {
        while (v[w]) {
            int c = w * 64 + __builtin_ctzll(v[w]);
            int pr = pivrow[c];
            if (pr < 0) return c;
            const Row &r = rows[pr];
            for (int q = w; q < W; q++) v[q] ^= r[q];
        }
    }
    return -1;
}
static Row poly_to_row(const vector<u64> &masks) {
    Row v(W, 0);
    for (u64 m : masks) { int j = colidx.at(m); v[j >> 6] ^= 1ULL << (j & 63); }
    return v;
}
static int insert_row(Row &v) {          // v already reduced, nonzero; returns index
    int c = -1;
    for (int w = 0; w < W && c < 0; w++) if (v[w]) c = w * 64 + __builtin_ctzll(v[w]);
    int id = (int)rows.size();
    rows.push_back(v); rowpiv.push_back(c); pivrow[c] = id;
    return id;
}
static vector<vector<u64>> mults;        // mults[s] = all monomials of size s over N variables
static void build_mults() {
    mults.assign(D + 1, {});
    function<void(int, int, u64, int)> rec = [&](int start, int left, u64 cur, int size) {
        if (left == 0) { mults[size].push_back(cur); return; }
        for (int v = start; v < N; v++) rec(v + 1, left - 1, cur | (1ULL << v), size);
    };
    for (int s = 1; s <= D; s++) rec(0, s, 0, s);
}
static int lm_deg(const Row &v) {        // size of the leading monomial (= deg f in this order)
    for (int w = 0; w < W; w++) if (v[w]) return pc(colmask[w * 64 + __builtin_ctzll(v[w])]);
    return -1;
}
// mu * f, as a row; counts terms that would exceed degree D (must be 0)
static long long overflow_terms = 0;
static Row product(const Row &f, u64 mu) {
    Row p(W, 0);
    for (int w = 0; w < W; w++) {
        u64 x = f[w];
        while (x) {
            int b = __builtin_ctzll(x); x &= x - 1;
            u64 t = colmask[w * 64 + b] | mu;
            auto it = colidx.find(t);
            if (it == colidx.end()) { overflow_terms++; continue; }
            p[it->second >> 6] ^= 1ULL << (it->second & 63);
        }
    }
    return p;
}
static void read_gens(const char *path, vector<vector<u64>> &gens) {
    FILE *f = fopen(path, "r"); if (!f) { perror(path); exit(2); }
    int ng; if (fscanf(f, "%d %d", &N, &ng) != 2) exit(2);
    gens.resize(ng);
    for (int g = 0; g < ng; g++) {
        int c; if (fscanf(f, "%d", &c) != 1) exit(2);
        gens[g].resize(c);
        for (int i = 0; i < c; i++) { unsigned long long m; if (fscanf(f, "%llu", &m) != 1) exit(2); gens[g][i] = m; }
    }
    fclose(f);
}
static vector<vector<u64>> read_given(const char *path) {
    vector<vector<u64>> out;
    FILE *f = fopen(path, "rb"); if (!f) { perror(path); exit(2); }
    uint32_t c;
    while (fread(&c, 4, 1, f) == 1) {
        vector<u64> r(c);
        if (c && fread(r.data(), 8, c, f) != c) exit(2);
        out.push_back(r);
    }
    fclose(f);
    return out;
}
static void init_state() { rows.clear(); rowpiv.clear(); pivrow.assign(ncols, -1); }

// the worklist closure. returns number of products formed
static long long run_closure(const vector<vector<u64>> &gens) {
    init_state();
    deque<int> q;
    for (auto &g : gens) {
        Row v = poly_to_row(g);
        if (reduce(v) >= 0) { int id = insert_row(v); q.push_back(id); }
    }
    long long nprod = 0;
    while (!q.empty()) {
        int id = q.front(); q.pop_front();
        Row f = rows[id];                       // the vector exactly as inserted
        int dg = lm_deg(f);
        int smax = D - dg; if (getenv("MAXMU")) smax = std::min(smax, atoi(getenv("MAXMU")));   // MAXMU: restrict multiplier size (size-1 closure generates every multiple; used only to compute the whole ideal I with D = N+1)
        for (int s = 1; s <= smax; s++)
            for (u64 mu : mults[s]) {
                Row p = product(f, mu); nprod++;
                if (reduce(p) >= 0) { int nid = insert_row(p); q.push_back(nid); }
            }
    }
    return nprod;
}
static long long count_std(const vector<u64> &lms) {   // SOS DP: forbidden = up-set of the leading monomials
    if (N > 30) return -1;
    vector<uint8_t> forb((size_t)1 << N, 0);
    for (u64 m : lms) forb[m] = 1;
    for (int i = 0; i < N; i++) {
        size_t bit = (size_t)1 << i;
        for (size_t m = 0; m < ((size_t)1 << N); m++) if ((m & bit) && forb[m ^ bit]) forb[m] = 1;
    }
    long long c = 0;
    for (size_t m = 0; m < ((size_t)1 << N); m++) c += !forb[m];
    return c;
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    string mode = argv[1];
    vector<vector<u64>> gens; read_gens(argv[2], gens);
    D = atoi(argv[3]);
    build_columns(); build_mults();
    if (mode == "closure") {
        string pre = argv[4];
        long long nprod = run_closure(gens);
        // leading monomials in ORDER descending = increasing column
        vector<int> lc; for (int j = 0; j < ncols; j++) if (pivrow[j] >= 0) lc.push_back(j);
        vector<u64> lms; for (int j : lc) lms.push_back(colmask[j]);
        bool one = pivrow[ncols - 1] >= 0;      // the monomial 1 is the smallest in ORDER = last column
        long long std = count_std(lms);
        map<int, long> bydeg; for (u64 m : lms) bydeg[pc(m)]++;
        FILE *s = fopen((pre + ".stats").c_str(), "w");
        fprintf(s, "N=%d D=%d ncols=%d rank=%zu contains_one=%d std=%lld products=%lld overflow_terms=%lld", N, D, ncols, rows.size(), (int)one, std, nprod, overflow_terms);
        for (auto &kv : bydeg) fprintf(s, " lm_deg%d=%ld", kv.first, kv.second);
        fprintf(s, "\n"); fclose(s);
        FILE *l = fopen((pre + ".lm").c_str(), "w");
        for (u64 m : lms) fprintf(l, "%llu\n", (unsigned long long)m);
        fclose(l);
        if (getenv("RREF")) {
            // back-substitute to the reduced form, rows in increasing leading column
            vector<int> order(lc.size());
            vector<Row> R; for (int j : lc) R.push_back(rows[pivrow[j]]);
            for (int i = (int)R.size() - 1; i >= 0; i--) {
                int c = lc[i];
                for (int j = 0; j < i; j++) if ((R[j][c >> 6] >> (c & 63)) & 1) for (int q = 0; q < W; q++) R[j][q] ^= R[i][q];
            }
            FILE *o = fopen((pre + ".rref").c_str(), "wb");
            for (auto &r : R) {
                vector<u64> ms;
                for (int w = 0; w < W; w++) { u64 x = r[w]; while (x) { int b = __builtin_ctzll(x); x &= x - 1; ms.push_back(colmask[w * 64 + b]); } }
                sort(ms.begin(), ms.end());
                uint32_t c = ms.size(); fwrite(&c, 4, 1, o); fwrite(ms.data(), 8, c, o);
            }
            fclose(o);
        }
        printf("rank=%zu contains_one=%d std=%lld products=%lld overflow_terms=%lld\n", rows.size(), (int)one, std, nprod, overflow_terms);
        return 0;
    }
    if (mode == "macaulay") {
        // single-level degree-D Macaulay matrix of the ORIGINAL generators: span of g and mu*g (1 <= |mu| <= D - deg g, deg g = largest monomial size of g as written)
        init_state(); long long nprod = 0;
        for (auto &g : gens) { Row v = poly_to_row(g); if (reduce(v) >= 0) insert_row(v); }
        for (auto &g : gens) {
            int dg = 0; for (u64 m : g) dg = std::max(dg, pc(m));
            Row base = poly_to_row(g);
            for (int s = 1; s <= D - dg; s++)
                for (u64 mu : mults[s]) { Row p = product(base, mu); nprod++; if (reduce(p) >= 0) insert_row(p); }
        }
        printf("rank=%zu products=%lld overflow_terms=%lld\n", rows.size(), nprod, overflow_terms);
        return 0;
    }
    if (mode == "compare") {
        auto given = read_given(argv[4]);
        long long nprod = run_closure(gens);
        size_t rank_ref = rows.size();
        long notin = 0;
        for (auto &g : given) { Row v = poly_to_row(g); if (reduce(v) >= 0) notin++; }
        // reverse inclusion: echelonize GIVEN with the same machinery and test each reference row
        vector<Row> refrows = rows; vector<int> refpiv = rowpiv;
        init_state();
        for (auto &g : given) { Row v = poly_to_row(g); if (reduce(v) >= 0) insert_row(v); }
        size_t rank_given = rows.size();
        long refnot = 0;
        for (auto &r : refrows) { Row v = r; if (reduce(v) >= 0) refnot++; }
        printf("rank_ref=%zu rank_given=%zu given_rows=%zu given_not_in_ref=%ld ref_not_in_given=%ld products=%lld overflow_terms=%lld\n",
               rank_ref, rank_given, given.size(), notin, refnot, nprod, overflow_terms);
        return 0;
    }
    if (mode == "saturate") {
        auto given = read_given(argv[4]);
        init_state();
        deque<int> ids;
        for (auto &g : given) { Row v = poly_to_row(g); if (reduce(v) >= 0) ids.push_back(insert_row(v)); }
        size_t rank = rows.size();
        long gens_not_in = 0;
        for (auto &g : gens) { Row v = poly_to_row(g); if (reduce(v) >= 0) gens_not_in++; }
        long long checked = 0, violations = 0; long first_row = -1; u64 first_mu = 0;
        for (int id : ids) {
            Row f = rows[id]; int dg = lm_deg(f);
            for (int s = 1; s <= D - dg; s++)
                for (u64 mu : mults[s]) {
                    Row p = product(f, mu); checked++;
                    if (reduce(p) >= 0) { if (!violations) { first_row = id; first_mu = mu; } violations++; }
                }
        }
        printf("rank_given_span=%zu gens_not_in_span=%ld pairs_checked=%lld saturation_violations=%lld first_violation_row_lm=%llu first_mu=%llu overflow_terms=%lld\n",
               rank, gens_not_in, checked, violations,
               (unsigned long long)(first_row >= 0 ? colmask[rowpiv[first_row]] : 0), (unsigned long long)first_mu, overflow_terms);
        return 0;
    }
    return 2;
}
