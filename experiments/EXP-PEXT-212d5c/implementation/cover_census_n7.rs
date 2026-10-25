// Census of GHS-type covers for elliptic curves over K = GF(q^n), n an odd prime.
// EXP-PEXT-212d5c (crypto-autoresearcher): n = 7 extension of aburan28/crypto
// research/ghs_cover_census_n5_20261013/cover_census_n.rs (sha256 d2a8504b68b26ea5ef83687d682a2bae75bb254acaf7d909420103e22aa11edc,
// commit f7ed67332588643447fdeca66b3790febbcf9e92). For n in {3, 5} every code path and every output byte is the upstream tool's
// (the regression fixture of the contract compares them byte for byte). Additions, used only for n = 7:
//   * polynomial capacity 32 (a union of 7 conjugate 4-sets has up to 28 points), genus table up to 800;
//   * K-isomorphism classes in characteristic 3 by the reduced families a4 = 0 (a2 != 0) and a2 = 0, instead of a q^(3n) table;
//   * mode strata:K (q = 3): K classes per 2-torsion stratum drawn by the fixed-seed stream, every class with j in F_q, plus the
//     K-rational 2-isogeny neighbour classes of every pick; each model censused over all of its structures;
//   * mode construct (q = 3, 5, 7): every genus-7 configuration B' = {s^i x : i in S}, x in K \ F_q up to PGL2(F_q), S a weight-4
//     word of the two [7,3,4] cyclic codes, mapped to j(B') and compared with the j-line of split curves;
//   * the n = 7 derived statements of H-PEXT-d536a1 (Lemma M7, D0, E7, O7, T7) checked on every censused model.
// Upstream header follows.
//
// Fork of research/ghs_cubic_cover_census_20261012/cover_census.rs (n = 3 only, brute cocycle search).
//
// For every F_q-structure tau on P^1_K it computes the (Z/2)^m compositum of the n conjugate double
// covers by branch data: m = F_2-rank of {tau^i B : i < n}, r = |U|, U = union of the tau^i B,
// genus = 2^(m-2)(r-4)+1 (m >= 2; m = 1 is recorded and excluded).
//
// Two enumerations of the structures, which must agree (PROTOCOL.md, reproduction checks):
//   cocycles : every A in PGL2(K) with A A^s ... A^(s^(n-1)) scalar, tau = A o s (the merged tool's
//              method, generalised to n; cost |PGL2(K)| per field).
//   cosets   : every structure is tau = M s M^-1 (Lang), one per coset M PGL2(F_q); then
//              tau^i B = M s^i (M^-1 B), so (m, r) of (B, tau) equal those of (B' = M^-1 B, s).
//              N = M^-1 runs over a transversal of PGL2(F_q) \ PGL2(K) given by normal forms of the
//              triple (N(inf), N(0), N(1)); cost |PGL2(K)| / |PGL2(F_q)| per curve.
// Fast path (cosets): the s^i B' are pairwise disjoint iff gcd(B', s^k B') = 1 for 1 <= k <= (n-1)/2;
// then m = n and r = 4n without forming the union.
//
// Dependency-free: rustc --edition 2021 -O cover_census_n.rs
// ./cover_census_n <q> <n> <exhaustive|sample:N> <cosets|cocycles> [threads]
// ./cover_census_n7 <q> 7 <strata:K> cosets [threads]      (q = 3)
// ./cover_census_n7 <q> 7 construct - [threads]            (q in {3, 5, 7})
// One JSON object per line on stdout. Every aggregate is computed here (plots only render them).
use std::collections::{BTreeMap, HashMap};

const SEED: u64 = 20261012;
struct Rng(u64);
impl Rng {
    fn new(tag: u64) -> Self { Rng(SEED ^ tag.wrapping_mul(0x9E3779B97F4A7C15)) }
    fn next(&mut self) -> u64 { self.0 = self.0.wrapping_add(0x9E3779B97F4A7C15); let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58476D1CE4E5B9); z = (z ^ (z >> 27)).wrapping_mul(0x94D049BB133111EB); z ^ (z >> 31) }
    fn below(&mut self, n: u32) -> u32 { (self.next() % n as u64) as u32 }
}

// GF(q^n): 0 is zero, e >= 1 is alpha^(e-1). Identical construction to the merged tool.
struct Fld { q: u32, n: u32, size: u32, m: u32, zech: Vec<u32>, idx_of: Vec<u32>, el_of: Vec<u32> }
impl Fld {
    fn build(q: u32, n: u32) -> Fld {
        let size = q.pow(n); let m = size - 1; let nn = n as usize;
        let digits = |mut i: u32| -> Vec<u32> { let mut v = vec![0; nn]; for k in 0..nn { v[k] = i % q; i /= q; } v };
        let index = |v: &[u32]| -> u32 { let mut i = 0; for k in (0..nn).rev() { i = i * q + v[k]; } i };
        for cand in 0..size { let md = digits(cand);
            for s in 0..q {
                let mut exp_idx = vec![0u32; m as usize]; let mut cur = vec![0u32; nn]; cur[0] = 1; let mut ok = true;
                for k in 0..m as usize { let ci = index(&cur); if ci == 0 || (k > 0 && ci == 1) { ok = false; break; } exp_idx[k] = ci;
                    let mut nx = vec![0u32; nn]; let top = cur[nn - 1];
                    for i in 0..nn { let sh = if i > 0 { cur[i - 1] } else { 0 }; nx[i] = (sh + (q - md[i]) * top + s * cur[i]) % q; } cur = nx; }
                if !ok || index(&cur) != 1 { continue; }
                let mut el_of = vec![0u32; size as usize]; let mut idx_of = vec![0u32; size as usize];
                for k in 0..m as usize { el_of[exp_idx[k] as usize] = k as u32 + 1; idx_of[k + 1] = exp_idx[k]; }
                let mut zech = vec![0u32; m as usize];
                for k in 0..m as usize { let mut dv = digits(exp_idx[k]); dv[0] = (dv[0] + 1) % q; zech[k] = el_of[index(&dv) as usize]; }
                return Fld { q, n, size, m, zech, idx_of, el_of };
            } }
        panic!("no field");
    }
    #[inline] fn mul(&self, a: u32, b: u32) -> u32 { if a == 0 || b == 0 { 0 } else { let s = a + b - 2; (if s >= self.m { s - self.m } else { s }) + 1 } }
    #[inline] fn inv(&self, a: u32) -> u32 { (self.m - (a - 1)) % self.m + 1 }
    #[inline] fn neg(&self, a: u32) -> u32 { if a == 0 { 0 } else { (a - 1 + self.m / 2) % self.m + 1 } }
    #[inline] fn add(&self, a: u32, b: u32) -> u32 { if a == 0 { return b; } if b == 0 { return a; }
        let dlt = if b >= a { b - a } else { b + self.m - a }; let z = self.zech[dlt as usize]; if z == 0 { 0 } else { let s = a + z - 2; (if s >= self.m { s - self.m } else { s }) + 1 } }
    #[inline] fn sub(&self, a: u32, b: u32) -> u32 { self.add(a, self.neg(b)) }
    #[inline] fn div(&self, a: u32, b: u32) -> u32 { self.mul(a, self.inv(b)) }
    #[inline] fn frob(&self, a: u32) -> u32 { if a == 0 { 0 } else { (((a - 1) as u64 * self.q as u64) % self.m as u64) as u32 + 1 } }
    // s^k on an element: exponent times q^k (qk = q^k mod m)
    #[inline] fn frobk(&self, a: u32, qk: u64) -> u32 { if a == 0 { 0 } else { (((a - 1) as u64 * qk) % self.m as u64) as u32 + 1 } }
    #[inline] fn is_sq(&self, a: u32) -> bool { a == 0 || (a - 1) % 2 == 0 }
    fn int(&self, c: i64) -> u32 { self.el_of[c.rem_euclid(self.q as i64) as usize] }
    fn pow(&self, a: u32, e: u64) -> u32 { if a == 0 { 0 } else { (((a - 1) as u64 * (e % self.m as u64)) % self.m as u64) as u32 + 1 } }
    fn in_fq(&self, a: u32) -> bool { self.frob(a) == a }
    fn p(&self) -> u32 { let mut p = 2; while self.q % p != 0 { p += 1; } p }
}

// Small polynomials on the stack, low -> high, n = length (0 for the zero polynomial). Degree <= 23.
const PL: usize = 32;
#[derive(Clone, Copy, PartialEq)]
struct P { c: [u32; PL], n: usize }
fn pz() -> P { P { c: [0; PL], n: 0 } }
fn ptrim(mut a: P) -> P { while a.n > 0 && a.c[a.n - 1] == 0 { a.n -= 1; } a }
fn pmul(f: &Fld, a: &P, b: &P) -> P { let mut r = pz(); if a.n == 0 || b.n == 0 { return r; } r.n = a.n + b.n - 1; assert!(r.n <= PL);
    for i in 0..a.n { if a.c[i] == 0 { continue; } for j in 0..b.n { r.c[i + j] = f.add(r.c[i + j], f.mul(a.c[i], b.c[j])); } } r }
fn pdivrem(f: &Fld, a: &P, b: &P) -> (P, P) { let mut r = *a; let mut qv = pz(); if r.n < b.n { return (qv, r); } qv.n = r.n - b.n + 1; let li = f.inv(b.c[b.n - 1]);
    while r.n >= b.n { let k = r.n - b.n; let c = f.mul(r.c[r.n - 1], li); qv.c[k] = c; for j in 0..b.n { r.c[k + j] = f.sub(r.c[k + j], f.mul(c, b.c[j])); } r = ptrim(r); if r.n == 0 { break; } }
    (qv, r) }
fn pmonic(f: &Fld, mut a: P) -> P { if a.n > 0 { let li = f.inv(a.c[a.n - 1]); for i in 0..a.n { a.c[i] = f.mul(a.c[i], li); } } a }
fn pgcd(f: &Fld, a: &P, b: &P) -> P { let (mut x, mut y) = (*a, *b); while y.n > 0 { let r = pdivrem(f, &x, &y).1; x = y; y = r; } pmonic(f, x) }

// A finite subset of P^1: monic squarefree affine polynomial plus a flag for infinity.
#[derive(Clone, Copy, PartialEq)]
struct Set { p: P, inf: bool }
fn size(s: &Set) -> usize { s.p.n.max(1) - 1 + s.inf as usize }
fn sdiff(f: &Fld, a: &Set, b: &Set) -> Set { let g = pgcd(f, &a.p, &b.p); Set { p: pmul(f, &pdivrem(f, &a.p, &g).0, &pdivrem(f, &b.p, &g).0), inf: a.inf ^ b.inf } }
fn union(f: &Fld, a: &Set, b: &Set) -> Set { let g = pgcd(f, &a.p, &b.p); Set { p: pmul(f, &a.p, &pdivrem(f, &b.p, &g).0), inf: a.inf | b.inf } }
fn meets(f: &Fld, a: &Set, b: &Set) -> bool { (a.inf && b.inf) || pgcd(f, &a.p, &b.p).n > 1 }
fn sfrob(f: &Fld, s: &Set, qk: u64) -> Set { let mut t = *s; for i in 0..t.p.n { t.p.c[i] = f.frobk(t.p.c[i], qk); } t }
// quartic binary form F = sum c[i] X^i Z^(4-i)  ->  its zero set
fn set_of(f: &Fld, c: &[u32; 5]) -> Set { let mut p = pz(); p.n = 5; p.c[..5].copy_from_slice(c); let p = ptrim(p); Set { inf: p.n < 5, p: pmonic(f, p) } }
type Mat = [u32; 4]; // [a, b, c, d] acting on points as x -> (a x + b)/(c x + d)
// zeros moved by A (no Frobenius):  G(X, Z) = F(dX - bZ, -cX + aZ)
fn mob(f: &Fld, c: &[u32; 5], a: &Mat) -> [u32; 5] {
    let l1 = [f.neg(a[1]), a[3]]; let l2 = [a[0], f.neg(a[2])];
    let mut p1 = [[0u32; 5]; 5]; let mut p2 = [[0u32; 5]; 5]; p1[0][0] = 1; p2[0][0] = 1;
    for i in 1..5 { for j in 0..i { p1[i][j] = f.add(p1[i][j], f.mul(p1[i - 1][j], l1[0])); p1[i][j + 1] = f.add(p1[i][j + 1], f.mul(p1[i - 1][j], l1[1]));
        p2[i][j] = f.add(p2[i][j], f.mul(p2[i - 1][j], l2[0])); p2[i][j + 1] = f.add(p2[i][j + 1], f.mul(p2[i - 1][j], l2[1])); } }
    let mut g = [0u32; 5];
    for i in 0..5 { let ci = c[i]; if ci == 0 { continue; } for u in 0..=i { if p1[i][u] == 0 { continue; } let t = f.mul(ci, p1[i][u]); for v in 0..=(4 - i) { g[u + v] = f.add(g[u + v], f.mul(t, p2[4 - i][v])); } } }
    g
}
// tau(F) for tau = A o sigma (merged tool): conjugate the coefficients, then move the zeros by A
fn tau(f: &Fld, c: &[u32; 5], a: &Mat) -> [u32; 5] { let cs = [f.frob(c[0]), f.frob(c[1]), f.frob(c[2]), f.frob(c[3]), f.frob(c[4])]; mob(f, &cs, a) }
fn mmul(f: &Fld, a: &Mat, b: &Mat) -> Mat { [f.add(f.mul(a[0], b[0]), f.mul(a[1], b[2])), f.add(f.mul(a[0], b[1]), f.mul(a[1], b[3])), f.add(f.mul(a[2], b[0]), f.mul(a[3], b[2])), f.add(f.mul(a[2], b[1]), f.mul(a[3], b[3]))] }
fn mfrob(f: &Fld, a: &Mat) -> Mat { [f.frob(a[0]), f.frob(a[1]), f.frob(a[2]), f.frob(a[3])] }
// all A in PGL2(K) with A A^s ... A^(s^(n-1)) scalar, normalised as in the merged tool
fn cocycles(f: &Fld, threads: usize) -> Vec<Mat> {
    let n = f.n;
    let test = |a: &Mat| -> bool { let mut prod = *a; let mut cur = *a; for _ in 1..n { cur = mfrob(f, &cur); prod = mmul(f, &prod, &cur); }
        prod[1] == 0 && prod[2] == 0 && prod[0] == prod[3] && prod[0] != 0 };
    let mut out: Vec<Mat> = vec![];
    std::thread::scope(|sc| { let hs: Vec<_> = (0..threads).map(|t| { let test = &test; sc.spawn(move || { let mut v = vec![];
        for b in (t as u32..f.size).step_by(threads) { for c in 0..f.size { for d in 0..f.size { if d == f.mul(b, c) { continue; } let a = [1, b, c, d]; if test(&a) { v.push(a); } } } } v }) }).collect();
        for h in hs { out.extend(h.join().unwrap()); } });
    for c in 1..f.size { for d in 0..f.size { let a = [0, 1, c, d]; if test(&a) { out.push(a); } } }
    out.sort(); out
}

// ---------- transversal of PGL2(F_q) \ PGL2(K) by normal forms of (N(inf), N(0), N(1)) ----------
// Points of P^1(K): 0..size-1 are field elements, size is infinity.
struct Trans { inf: u32, rep_b: Vec<u32>, rep_a2: Vec<u32>, rep_a1: Vec<u32>, total: u64 }
fn apply(f: &Fld, m: &Mat, x: u32, inf: u32) -> u32 {
    if x == inf { return if m[2] == 0 { inf } else { f.div(m[0], m[2]) }; }
    let num = f.add(f.mul(m[0], x), m[1]); let den = f.add(f.mul(m[2], x), m[3]); if den == 0 { inf } else { f.div(num, den) } }
fn trans(f: &Fld) -> Trans {
    let inf = f.size; let fq: Vec<u32> = (0..f.size).filter(|&x| f.in_fq(x)).collect(); assert_eq!(fq.len() as u32, f.q);
    let mut pgl: Vec<Mat> = vec![]; for &b in &fq { for &c in &fq { for &d in &fq { if d != f.mul(b, c) { pgl.push([1, b, c, d]); } } } }
    for &c in &fq { if c == 0 { continue; } for &d in &fq { pgl.push([0, 1, c, d]); } }
    let qq = f.q as u64; assert_eq!(pgl.len() as u64, qq * qq * qq - qq);
    let non: Vec<u32> = (0..f.size).filter(|&x| !f.in_fq(x)).collect();
    // Case B: a not in P^1(F_q); PGL2(F_q) acts freely on K \ F_q for n an odd prime (a fixed point would fix its n conjugates)
    let rep_b: Vec<u32> = non.iter().cloned().filter(|&x| pgl.iter().all(|m| { let y = apply(f, m, x, inf); assert!(y != inf); y >= x })).collect();
    // Case A2: b not in F_q, up to x -> u x + v (free)
    let rep_a2: Vec<u32> = non.iter().cloned().filter(|&x| fq.iter().filter(|&&u| u != 0).all(|&u| fq.iter().all(|&v| f.add(f.mul(u, x), v) >= x))).collect();
    // Case A1: c in K*, up to x -> u x
    let rep_a1: Vec<u32> = (1..f.size).filter(|&x| fq.iter().filter(|&&u| u != 0).all(|&u| f.mul(u, x) >= x)).collect();
    let qn = f.size as u64; let total = rep_a1.len() as u64 + rep_a2.len() as u64 * (qn - 1) + rep_b.len() as u64 * qn * (qn - 1);
    assert_eq!(rep_b.len() as u64 * (qq * qq * qq - qq), qn - qq, "PGL2(F_q) not free on K minus F_q");
    Trans { inf, rep_b, rep_a2, rep_a1, total }
}
// matrix N with N(inf) = a, N(0) = b, N(1) = c
fn from_triple(f: &Fld, a: u32, b: u32, c: u32, inf: u32) -> Mat {
    if a == inf { return [f.sub(c, b), b, 0, 1]; }
    if b == inf { return [a, f.sub(c, a), 1, 0]; }
    if c == inf { return [a, f.neg(b), 1, f.neg(1)]; }
    [f.mul(a, f.sub(c, b)), f.mul(b, f.sub(a, c)), f.sub(c, b), f.sub(a, c)]
}
fn for_each_coset<F: FnMut(&Mat)>(f: &Fld, t: &Trans, mut body: F) {
    let inf = t.inf;
    for &c in &t.rep_a1 { body(&from_triple(f, inf, 0, c, inf)); }
    for &b in &t.rep_a2 { for c in 0..f.size { if c != b { body(&from_triple(f, inf, b, c, inf)); } } }
    for &a in &t.rep_b { for b in 0..=f.size { if b == a { continue; } for c in 0..=f.size { if c == a || c == b { continue; } body(&from_triple(f, a, b, c, inf)); } } }
}

// ---------- evaluation of one structure from its n conjugate branch sets ----------
const GMAX: usize = 800;
#[derive(Clone)]
struct Res { by_genus: Vec<u64>, m1: u64, min_g: u32, types: HashMap<(u32, u32, i32), u64>, mismatch: u64, mr: BTreeMap<(u32, u32), u64>, structures: u64 }
impl Default for Res { fn default() -> Self { Res { by_genus: vec![0; GMAX], m1: 0, min_g: 99, types: HashMap::new(), mismatch: 0, mr: BTreeMap::new(), structures: 0 } } }
fn genus(m: u32, r: u32) -> u32 { (1u32 << (m - 2)) * (r - 4) + 1 }
// sets[i] = tau^i B for i < n
fn eval(f: &Fld, sets: &[Set], res: &mut Res) {
    res.structures += 1;
    if sets[1] == sets[0] { res.m1 += 1; *res.mr.entry((1, size(&sets[0]) as u32)).or_insert(0) += 1; return; }
    let mut span: Vec<Set> = vec![Set { p: { let mut p = pz(); p.n = 1; p.c[0] = 1; p }, inf: false }];
    let mut u = sets[0];
    for s in sets { u = union(f, &u, s); if span.iter().any(|v| v == s) { continue; } let add: Vec<Set> = span.iter().map(|v| sdiff(f, v, s)).collect(); span.extend(add); }
    let m = span.len().trailing_zeros(); assert!(span.len() == 1 << m);
    let r = size(&u) as u32; let g = genus(m, r);
    *res.mr.entry((m, r)).or_insert(0) += 1; res.by_genus[g as usize] += 1;
    // subcover-sum cross-check: genus = sum over nonzero characters of (support - 2)/2
    let sum: i32 = span.iter().skip(1).map(|v| (size(v) as i32 - 2) / 2).sum(); if sum != g as i32 { res.mismatch += 1; }
    if g <= res.min_g {
        // a genus-0 quotient by an involution of the group: a hyperplane of the span all of whose
        // nonzero vectors have support 2. For m = 3 these are the 7 two-dimensional subspaces (merged
        // tool's test); for m >= 4 no such hyperplane exists (PROTOCOL.md, Lemma H); m = 2 undetermined.
        let hyp = if m == 2 { -1 } else if m >= 4 { 0 } else {
            let nz: Vec<&Set> = span.iter().skip(1).collect(); let mut found = false;
            for i in 0..nz.len() { for j in i + 1..nz.len() { let w = sdiff(f, nz[i], nz[j]); if size(&union(f, &union(f, nz[i], nz[j]), &w)) == 3 { found = true; } } }
            found as i32 };
        if g < res.min_g { res.min_g = g; res.types.clear(); }
        *res.types.entry((m, r, hyp)).or_insert(0) += 1;
    }
}
fn census_cosets(f: &Fld, t: &Trans, b0f: &[u32; 5]) -> Res {
    let n = f.n as usize; let mut res = Res::default(); let qk: Vec<u64> = (0..n).map(|k| (f.q as u64).pow(k as u32) % f.m as u64).collect();
    if n == 7 { res.min_g = 9999; } // n = 7 genera reach 769; the upstream sentinel 99 is kept for n <= 5 (byte-identical output)
    let gfast = genus(n as u32, 4 * n as u32);
    for_each_coset(f, t, |nm| {
        let s0 = set_of(f, &mob(f, b0f, nm));
        let mut overlap = false; for k in 1..=(n - 1) / 2 { if meets(f, &s0, &sfrob(f, &s0, qk[k])) { overlap = true; break; } }
        if !overlap && gfast > res.min_g { res.structures += 1; res.by_genus[gfast as usize] += 1; *res.mr.entry((n as u32, 4 * n as u32)).or_insert(0) += 1; return; }
        let sets: Vec<Set> = (0..n).map(|k| sfrob(f, &s0, qk[k])).collect(); eval(f, &sets, &mut res);
    });
    res
}
fn census_cocycles(f: &Fld, cos: &[Mat], b0f: &[u32; 5]) -> Res {
    let n = f.n as usize; let mut res = Res::default();
    for a in cos { let mut forms = vec![*b0f]; for i in 1..n { let nx = tau(f, &forms[i - 1], a); forms.push(nx); }
        let sets: Vec<Set> = forms.iter().map(|c| set_of(f, c)).collect(); eval(f, &sets, &mut res); }
    res
}

// ---------- curves y^2 = x^3 + a2 x^2 + a4 x + a6 ----------
#[derive(Clone, Copy)]
struct Cv { a2: u32, a4: u32, a6: u32 }
fn cubic(f: &Fld, c: &Cv, x: u32) -> u32 { f.add(f.add(f.mul(x, f.mul(x, f.add(x, c.a2))), f.mul(c.a4, x)), c.a6) }
fn dcubic(f: &Fld, c: &Cv, x: u32) -> u32 { f.add(f.add(f.mul(f.int(3), f.mul(x, x)), f.mul(f.int(2), f.mul(c.a2, x))), c.a4) }
fn disc(f: &Fld, c: &Cv) -> u32 { let (b2, b4, b6) = (f.mul(f.int(4), c.a2), f.mul(f.int(2), c.a4), f.mul(f.int(4), c.a6));
    let b8 = f.sub(f.mul(f.int(4), f.mul(c.a2, c.a6)), f.mul(c.a4, c.a4));
    let t1 = f.neg(f.mul(f.mul(b2, b2), b8)); let t2 = f.mul(f.int(8), f.mul(b4, f.mul(b4, b4))); let t3 = f.mul(f.int(27), f.mul(b6, b6)); let t4 = f.mul(f.int(9), f.mul(b2, f.mul(b4, b6)));
    f.add(f.sub(f.sub(t1, t2), t3), t4) }
fn jinv(f: &Fld, c: &Cv) -> u32 { let (b2, b4) = (f.mul(f.int(4), c.a2), f.mul(f.int(2), c.a4)); let c4 = f.sub(f.mul(b2, b2), f.mul(f.int(24), b4)); f.div(f.mul(c4, f.mul(c4, c4)), disc(f, c)) }
fn roots(f: &Fld, c: &Cv) -> Vec<u32> { (0..f.size).filter(|&x| cubic(f, c, x) == 0).collect() }
fn order(f: &Fld, c: &Cv) -> u64 { let mut n = 1u64; for x in 0..f.size { let v = cubic(f, c, x); n += if v == 0 { 1 } else if f.is_sq(v) { 2 } else { 0 }; } n }
// #E(K)[4]: O, the 2-torsion, and the points P = (x, y), y != 0, with 2P of order 2, i.e. f(x(2P)) = 0,
// x(2P) = f'(x)^2 / (4 f(x)) - a2 - 2x (independent of the sign of y)
fn four_torsion(f: &Fld, c: &Cv) -> u64 { let mut n = 1 + roots(f, c).len() as u64;
    for x in 0..f.size { let v = cubic(f, c, x); if v == 0 || !f.is_sq(v) { continue; } let d = dcubic(f, c, x);
        let x2 = f.sub(f.sub(f.div(f.mul(d, d), f.mul(f.int(4), v)), c.a2), f.mul(f.int(2), x)); if cubic(f, c, x2) == 0 { n += 2; } }
    n }
fn b0form(c: &Cv) -> [u32; 5] { [c.a6, c.a4, c.a2, 1, 0] }
fn maxprime(mut n: u64) -> u64 { let mut best = 1; let mut p = 2; while p * p <= n { while n % p == 0 { n /= p; best = p; } p += 1; } if n > 1 { n } else { best } }
// K-rational 2-isogeny neighbours. Short form (p > 3, merged tool): kernel (e, 0) gives A' = -15 e^2 - 4A, B' = -22 e^3 - 8 A e.
// General form: shift x -> x + e, y^2 = x (x^2 + s x + t), s = 3e + a2, t = 3e^2 + 2 a2 e + a4; neighbour y^2 = x (x^2 - 2 s x + s^2 - 4t).
fn neighbours(f: &Fld, c: &Cv, short: bool) -> Vec<Cv> { roots(f, c).into_iter().map(|e| { let e2 = f.mul(e, e);
    if short { Cv { a2: 0, a4: f.sub(f.mul(f.int(-15), e2), f.mul(f.int(4), c.a4)), a6: f.sub(f.mul(f.int(-22), f.mul(e, e2)), f.mul(f.int(8), f.mul(c.a4, e))) } }
    else { let s = f.add(f.mul(f.int(3), e), c.a2); let t = f.add(f.add(f.mul(f.int(3), e2), f.mul(f.int(2), f.mul(c.a2, e))), c.a4);
        Cv { a2: f.neg(f.mul(f.int(2), s)), a4: f.sub(f.mul(s, s), f.mul(f.int(4), t)), a6: 0 } } }).collect() }
// K-isomorphism classes. Short form for p > 3 (merged tool, same representatives and order); general form for p = 3,
// orbits of (a2, a4, a6) under x -> u^2 x + r: a2' = (3r + a2)/u^2, a4' = (3r^2 + 2 a2 r + a4)/u^4, a6' = f(r)/u^6.
struct Classes { reps: Vec<Cv>, class: Vec<u32>, short: bool, fam: bool }
impl Classes {
    fn idx(&self, f: &Fld, c: &Cv) -> usize { let s = f.size as usize;
        if self.fam { let c = fam_norm(f, c); return if c.a2 != 0 { c.a2 as usize * s + c.a6 as usize } else { s * s + c.a4 as usize * s + c.a6 as usize }; }
        if self.short { c.a4 as usize * s + c.a6 as usize } else { (c.a2 as usize * s + c.a4 as usize) * s + c.a6 as usize } }
    fn of(&self, f: &Fld, c: &Cv) -> u32 { self.class[self.idx(f, c)] }
}
// characteristic 3, n = 7: a2 != 0 -> shift x -> x + r, r = -a4/(2 a2), so a4 = 0 (a2 unchanged); a2 = 0 stays (family B)
fn fam_norm(f: &Fld, c: &Cv) -> Cv { if c.a2 == 0 { return *c; } let r = f.neg(f.div(c.a4, f.mul(f.int(2), c.a2))); Cv { a2: c.a2, a4: 0, a6: cubic(f, c, r) } }
fn classes_fam(f: &Fld) -> Classes {
    let s = f.size as usize; let mut cl = Classes { reps: vec![], class: vec![u32::MAX; 2 * s * s], short: false, fam: true };
    // family A: (a2, 0, a6), a2 != 0, orbits (a2 / u^2, a6 / u^6); the only isomorphisms preserving a4 = 0 have r = 0
    for a2 in 1..f.size { for a6 in 0..f.size { let c = Cv { a2, a4: 0, a6 }; if disc(f, &c) == 0 || cl.class[cl.idx(f, &c)] != u32::MAX { continue; }
        let id = cl.reps.len() as u32; cl.reps.push(c);
        for u in 1..f.size { let c2 = Cv { a2: f.div(a2, f.pow(u, 2)), a4: 0, a6: f.div(a6, f.pow(u, 6)) }; let i = cl.idx(f, &c2); assert!(cl.class[i] == u32::MAX || cl.class[i] == id); cl.class[i] = id; } } }
    // family B: (0, a4, a6), orbits (a4 / u^4, (r^3 + a4 r + a6) / u^6)
    for a4 in 0..f.size { for a6 in 0..f.size { let c = Cv { a2: 0, a4, a6 }; if disc(f, &c) == 0 || cl.class[cl.idx(f, &c)] != u32::MAX { continue; }
        let id = cl.reps.len() as u32; cl.reps.push(c);
        for u in 1..f.size { let (u4, u6) = (f.pow(u, 4), f.pow(u, 6)); for r in 0..f.size {
            let c2 = Cv { a2: 0, a4: f.div(a4, u4), a6: f.div(cubic(f, &c, r), u6) }; let i = cl.idx(f, &c2); assert!(cl.class[i] == u32::MAX || cl.class[i] == id); cl.class[i] = id; } } } }
    cl
}
fn classes(f: &Fld) -> Classes {
    let sz = f.size as usize;
    if f.p() > 3 { let mut cl = Classes { reps: vec![], class: vec![u32::MAX; sz * sz], short: true, fam: false };
        for a in 0..f.size { for b in 0..f.size { let c = Cv { a2: 0, a4: a, a6: b }; if disc(f, &c) == 0 || cl.class[cl.idx(f, &c)] != u32::MAX { continue; }
            let id = cl.reps.len() as u32; cl.reps.push(c); for u in 1..f.size { let c2 = Cv { a2: 0, a4: f.mul(a, f.pow(u, 4)), a6: f.mul(b, f.pow(u, 6)) }; let i = cl.idx(f, &c2); cl.class[i] = id; } } }
        return cl; }
    let mut cl = Classes { reps: vec![], class: vec![u32::MAX; sz * sz * sz], short: false, fam: false };
    for a2 in 0..f.size { for a4 in 0..f.size { for a6 in 0..f.size { let c = Cv { a2, a4, a6 }; if cl.class[cl.idx(f, &c)] != u32::MAX || disc(f, &c) == 0 { continue; }
        let id = cl.reps.len() as u32; cl.reps.push(c);
        for u in 1..f.size { let (u2, u4, u6) = (f.pow(u, 2), f.pow(u, 4), f.pow(u, 6)); for r in 0..f.size {
            let c2 = Cv { a2: f.div(f.add(f.mul(f.int(3), r), a2), u2), a4: f.div(f.add(f.add(f.mul(f.int(3), f.mul(r, r)), f.mul(f.int(2), f.mul(a2, r))), a4), u4), a6: f.div(cubic(f, &c, r), u6) };
            let i = cl.idx(f, &c2); assert!(cl.class[i] == u32::MAX || cl.class[i] == id); cl.class[i] = id; } } } } }
    cl
}

// ---------- output ----------
fn types_json(r: &Res) -> String { let mut v: Vec<_> = r.types.iter().collect(); v.sort();
    format!("[{}]", v.iter().map(|((m, rr, h), c)| format!("{{\"m\":{},\"r\":{},\"hyperelliptic\":{},\"structures\":{}}}", m, rr, match h { 1 => "true", 0 => "false", _ => "null" }, c)).collect::<Vec<_>>().join(",")) }
fn hist_json<K: std::fmt::Display + Ord>(h: &BTreeMap<K, u64>) -> String { format!("{{{}}}", h.iter().map(|(g, c)| format!("\"{}\":{}", g, c)).collect::<Vec<_>>().join(",")) }
fn m4(n: u64) -> &'static str { if n % 2 == 1 { "odd" } else if n % 4 == 2 { "2mod4" } else { "0mod4" } }
struct Info { c: Cv, order: u64, e2: u64, e4: u64, j_fq: bool, j0: bool, j1728: bool }
fn info(f: &Fld, c: &Cv) -> Info { let j = jinv(f, c); Info { c: *c, order: order(f, c), e2: 1 + roots(f, c).len() as u64, e4: four_torsion(f, c), j_fq: f.in_fq(j), j0: j == 0, j1728: j == f.int(1728) } }

// Derived statements checked on every curve (PROTOCOL.md "Derived statements"); each returns true when violated.
fn violations(f: &Fld, inf: &Info, r: &Res) -> Vec<&'static str> {
    let n = f.n; let mut v = vec![];
    let support: Vec<u32> = (0..GMAX as u32).filter(|&g| r.by_genus[g as usize] > 0).collect();
    if r.mismatch > 0 { v.push("subcover_sum"); }
    if support.iter().any(|&g| g < n) { v.push("D0_genus_at_least_n"); }
    if n == 3 {
        if inf.order % 2 == 1 && (support.iter().any(|&g| g != 13 && g != 17) || r.m1 > 0) { v.push("D3odd_support_13_17"); }
        if inf.order % 4 == 2 && r.min_g < 5 { v.push("D3_2mod4_at_least_5"); }
    }
    if n == 5 {
        for (&(m, rr), _) in &r.mr { if !(m == 1 || m == 4 || m == 5) { v.push("D1_m_in_1_4_5"); } if m == 4 && !(inf.e2 == 4 && (rr == 5 || rr == 10)) { v.push("D2_m4_split_r5_or_10"); } }
        if support.iter().any(|&g| g > 5 && g < 17) { v.push("D2_gap_6_to_16"); }
        if r.by_genus[5] > 0 && inf.e2 != 4 { v.push("D2_genus5_needs_split"); }
        if inf.order % 2 == 1 { if support.iter().any(|&g| g != 33 && g != 97 && g != 129) { v.push("D4odd_support"); }
            if r.m1 + r.by_genus[33] != 1 { v.push("D4odd_one_special"); }
            if !inf.j0 && !inf.j1728 && ((r.m1 == 1) != inf.j_fq) { v.push("D4odd_m1_iff_j_in_Fq"); } }
        if inf.e2 == 2 && r.min_g < 25 { v.push("D5_Z2_at_least_25"); }
        if inf.e2 == 2 && inf.order % 4 == 2 && r.min_g < 33 { v.push("D5_2mod4_at_least_33"); }
    }
    if n == 7 {
        // allowed (m, r) per 2-torsion type: spectrum.py 7 (Lemma M7 with the orbit lemma; H-PEXT-d536a1)
        let split: &[(u32, u32)] = &[(1, 4), (3, 7), (4, 8), (6, 7), (6, 14), (7, 8), (7, 9), (7, 10), (7, 14), (7, 15), (7, 16), (7, 21), (7, 22), (7, 28)];
        let z2: &[(u32, u32)] = &[(1, 4), (7, 9), (7, 10), (7, 16), (7, 21), (7, 22), (7, 28)];
        let odd: &[(u32, u32)] = &[(1, 4), (7, 10), (7, 22), (7, 28)];
        let allowed = match inf.e2 { 4 => split, 2 => z2, _ => odd };
        for (&(m, rr), _) in &r.mr { if ![1, 3, 4, 6, 7].contains(&m) { v.push("M7_m_in_1_3_4_6_7"); } if !allowed.contains(&(m, rr)) { v.push("E7_m_r_allowed_for_type"); } }
        if r.by_genus[7] > 0 && inf.e2 != 4 { v.push("E7_genus7_needs_split"); }
        if inf.order % 2 == 1 { if support.iter().any(|&g| g != 193 && g != 577 && g != 769) { v.push("O7odd_support_193_577_769"); }
            if r.m1 + r.by_genus[193] != 1 { v.push("O7odd_one_special"); }
            if !inf.j0 && !inf.j1728 && ((r.m1 == 1) != inf.j_fq) { v.push("O7odd_m1_iff_j_in_Fq"); } }
        if inf.e2 == 2 && r.min_g < 161 { v.push("T7_Z2_at_least_161"); }
        if inf.e2 == 2 && inf.order % 4 == 2 && r.min_g < 193 { v.push("T7_2mod4_at_least_193"); }
    }
    v
}

// 2-torsion stratum of a curve (n = 7 records)
fn stratum(inf: &Info) -> &'static str { if inf.order % 2 == 1 { if inf.j_fq { "odd_jFq" } else { "odd" } } else if inf.e2 == 2 { if inf.order % 4 == 2 { "Z2_2mod4" } else { "Z2_0mod4" } } else { "split" } }

// ---------- n = 7: constructive enumeration of the genus-7 configurations ----------
// B' = {s^i x : i in S}, x in K \ F_q (one per PGL2(F_q)-orbit), S a nonzero word of one of the two [7,3,4] cyclic codes
// generated by (x+1)(x^3+x+1) = {0,2,3,4} and (x+1)(x^3+x^2+1) = {0,1,2,4} (7 rotations each). Every such B' is the branch
// set of a split curve with j = j(lambda), lambda a cross-ratio of B'; for split curves the PGL2(K)-class of B is fixed by j.
fn jlam(f: &Fld, l: u32) -> u32 { let t = f.add(f.sub(f.mul(l, l), l), 1); let d = f.mul(f.mul(l, l), f.mul(f.sub(l, 1), f.sub(l, 1)));
    f.div(f.mul(f.int(256), f.mul(t, f.mul(t, t))), d) }
fn construct(q: u32, threads: usize) {
    assert!(q == 3 || q == 5 || q == 7, "construct: q in {{3, 5, 7}}");
    let n = 7u32; let f = Fld::build(q, n); let t0 = std::time::Instant::now(); let t = trans(&f);
    let qk: Vec<u64> = (0..7).map(|k| (q as u64).pow(k) % f.m as u64).collect();
    let mut pats: Vec<[usize; 4]> = vec![];
    for base in [[0usize, 2, 3, 4], [0, 1, 2, 4]] { for k in 0..7 { let mut p = [0usize; 4]; for i in 0..4 { p[i] = (base[i] + k) % 7; } p.sort(); pats.push(p); } }
    let mut j7: BTreeMap<u32, (u32, u64)> = BTreeMap::new(); let (mut configs, mut ok37, mut other) = (0u64, 0u64, 0u64);
    for &x in &t.rep_b { let orb: Vec<u32> = (0..7).map(|k| f.frobk(x, qk[k])).collect();
        for p in &pats { configs += 1; let b: Vec<u32> = p.iter().map(|&i| orb[i]).collect();
            let mut poly = pz(); poly.n = 1; poly.c[0] = 1; for &bi in &b { let mut lin = pz(); lin.n = 2; lin.c[0] = f.neg(bi); lin.c[1] = 1; poly = pmul(&f, &poly, &lin); }
            let s0 = Set { p: poly, inf: false }; let sets: Vec<Set> = (0..7).map(|k| sfrob(&f, &s0, qk[k])).collect();
            let mut r = Res::default(); r.min_g = 9999; eval(&f, &sets, &mut r);
            if r.mr.get(&(3, 7)).copied().unwrap_or(0) == 1 { ok37 += 1; } else { other += 1; }
            let e: Vec<u32> = (1..4).map(|i| f.inv(f.sub(b[i], b[0]))).collect(); let lam = f.div(f.sub(e[2], e[0]), f.sub(e[1], e[0]));
            let j = jlam(&f, lam); let ent = j7.entry(j).or_insert((lam, 0)); ent.1 += 1; } }
    let mut seen = vec![false; f.size as usize]; let mut jsplit = 0u64; for l in 2..f.size { let j = jlam(&f, l); if !seen[j as usize] { seen[j as usize] = true; jsplit += 1; } }
    // lambda = element index 1 is the field element 1 (alpha^0); 0 is zero; both excluded above (l starts at 2)
    let js: Vec<(u32, u32, u64)> = j7.iter().map(|(&j, &(l, c))| (j, l, c)).collect(); let qq = f.size as u64;
    let next = std::sync::atomic::AtomicUsize::new(0); let mut rows: Vec<(u32, u32, u64, u64)> = vec![(0, 0, 0, 0); js.len()];
    std::thread::scope(|sc| { let hs: Vec<_> = (0..threads).map(|_| sc.spawn(|| { let mut v = vec![]; loop { let i = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed); if i >= js.len() { break; }
        let (j, l, c) = js[i]; let cv = Cv { a2: f.neg(f.add(1, l)), a4: l, a6: 0 }; v.push((i, (j, l, c, order(&f, &cv)))); } v })).collect();
        for h in hs { for (i, r) in h.join().unwrap() { rows[i] = r; } } });
    let mut v2h: BTreeMap<u32, u64> = BTreeMap::new();
    for &(j, l, c, ord) in &rows { let tw = 2 * qq + 2 - ord; assert!(ord % 4 == 0 && tw % 4 == 0, "split curves have 4 | #E(K)");
        *v2h.entry(ord.trailing_zeros()).or_insert(0) += 1; *v2h.entry(tw.trailing_zeros()).or_insert(0) += 1;
        println!("{{\"rec\":\"construct_curve\",\"q\":{},\"n\":7,\"j_idx\":{},\"lambda_idx\":{},\"configs\":{},\"order\":{},\"order_twist\":{},\"v2\":{},\"v2_twist\":{},\"j_in_Fq\":{},\"j0\":{},\"j1728\":{}}}",
            q, f.idx_of[j as usize], f.idx_of[l as usize], c, ord, tw, ord.trailing_zeros(), tw.trailing_zeros(), f.in_fq(j), j == 0, j == f.int(1728)); }
    let rate = j7.len() as f64 / jsplit as f64;
    println!("{{\"rec\":\"construct\",\"q\":{},\"n\":7,\"x_orbit_reps\":{},\"patterns\":{},\"configs\":{},\"configs_m3_r7\":{},\"configs_other\":{},\"j_genus7\":{},\"j_split\":{},\"rate\":{:.8},\"rate_times_q3\":{:.6},\"configs_over_q4\":{:.6},\"v2_classes\":{},\"wall_s\":{:.1}}}",
        q, t.rep_b.len(), pats.len(), configs, ok37, other, j7.len(), jsplit, rate, rate * (q as f64).powi(3), configs as f64 / (q as f64).powi(4), hist_json(&v2h), t0.elapsed().as_secs_f64());
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let q: u32 = args[1].parse().unwrap(); let n: u32 = args[2].parse().unwrap(); let mode = args[3].clone(); let method = args[4].clone();
    let threads: usize = args.get(5).map(|s| s.parse().unwrap()).unwrap_or(6);
    assert!(n == 3 || n == 5 || n == 7, "n must be 3, 5 or 7 (odd prime)"); assert!(q % 2 == 1);
    if mode == "construct" { assert!(n == 7, "construct is the n = 7 genus-7 enumeration"); construct(q, threads); return; }
    if n == 7 { assert!(mode.starts_with("strata:") && method == "cosets" && q == 3, "n = 7 census: q = 3, strata:K, cosets"); }
    let f = Fld::build(q, n); let qq = f.size as u64; let qb = q as u64; let expect = (qq * qq * qq - qq) / (qb * qb * qb - qb);
    let t0 = std::time::Instant::now();
    let (tr, cos) = if method == "cosets" { (Some(trans(&f)), vec![]) } else if method == "cocycles" { (None, cocycles(&f, threads)) } else { panic!("method") };
    let structures = tr.as_ref().map(|t| t.total).unwrap_or(cos.len() as u64);
    let strata_k: usize = mode.strip_prefix("strata:").map(|x| x.parse().unwrap()).unwrap_or(0);
    let sample: usize = if mode == "exhaustive" { 0 } else if strata_k > 0 { strata_k } else { mode.strip_prefix("sample:").expect("mode").parse().unwrap() };
    println!("{{\"rec\":\"field\",\"q\":{},\"n\":{},\"method\":\"{}\",\"structures\":{},\"structures_expected\":{},\"mode\":\"{}\",\"setup_s\":{:.1}}}", q, n, method, structures, expect, if sample == 0 { "exhaustive" } else if strata_k > 0 { "strata" } else { "sample" }, t0.elapsed().as_secs_f64());
    assert_eq!(structures, expect);
    let short = f.p() > 3;
    let run = |c: &Cv| -> Res { match &tr { Some(t) => census_cosets(&f, t, &b0form(c)), None => census_cocycles(&f, &cos, &b0form(c)) } };
    let par = |cvs: &[Cv]| -> Vec<Res> { let mut out: Vec<Res> = vec![Res::default(); cvs.len()]; let next = std::sync::atomic::AtomicUsize::new(0);
        std::thread::scope(|sc| { let hs: Vec<_> = (0..threads).map(|_| sc.spawn(|| { let mut v = vec![]; loop { let i = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed); if i >= cvs.len() { break; } let ts = std::time::Instant::now(); let r = run(&cvs[i]);
            if n == 7 { eprintln!("model {} of {} done: {} structures, {:.1} s", i + 1, cvs.len(), r.structures, ts.elapsed().as_secs_f64()); } v.push((i, r)); } v })).collect();
            for h in hs { for (i, r) in h.join().unwrap() { out[i] = r; } } }); out };
    let emit = |inf: &Info, r: &Res, g2: u32, gc: Option<u32>, role: &str| {
        let extra = if n == 7 { format!(",\"j_idx\":{},\"stratum\":\"{}\"", f.idx_of[jinv(&f, &inf.c) as usize], stratum(inf)) } else { String::new() };
        let bg: BTreeMap<u32, u64> = (0..GMAX as u32).filter(|&g| r.by_genus[g as usize] > 0).map(|g| (g, r.by_genus[g as usize])).collect();
        let mr: BTreeMap<String, u64> = r.mr.iter().map(|((m, rr), c)| (format!("{},{}", m, rr), *c)).collect();
        println!("{{\"rec\":\"curve\",\"q\":{},\"n\":{},\"role\":\"{}\",\"a2_idx\":{},\"A_idx\":{},\"B_idx\":{},\"order\":{},\"maxprime\":{},\"order_mod4\":\"{}\",\"v2\":{},\"E2\":{},\"E4\":{},\"j_in_Fq\":{},\"j0\":{},\"j1728\":{},\"min_genus\":{},\"types_at_min\":{},\"structures_by_genus\":{},\"m1_structures\":{},\"mismatch\":{},\"min_genus_2isog\":{},\"min_genus_class\":{},\"structures_by_m_r\":{},\"violations\":[{}]{}}}",
            q, n, role, f.idx_of[inf.c.a2 as usize], f.idx_of[inf.c.a4 as usize], f.idx_of[inf.c.a6 as usize], inf.order, maxprime(inf.order), m4(inf.order), inf.order.trailing_zeros(), inf.e2, inf.e4, inf.j_fq, inf.j0, inf.j1728,
            r.min_g, types_json(r), hist_json(&bg), r.m1, r.mismatch, g2, gc.map(|x| x.to_string()).unwrap_or("null".into()), hist_json(&mr),
            violations(&f, inf, r).iter().map(|s| format!("\"{}\"", s)).collect::<Vec<_>>().join(","), extra); };
    // aggregates: (scope, grouping, key) -> histogram of min genus
    let mut agg: BTreeMap<(String, String, String), BTreeMap<u32, u64>> = BTreeMap::new();
    let mut add = |scope: &str, inf: &Info, g: u32| { for (grp, key) in [("order_mod4", m4(inf.order).to_string()), ("E2", inf.e2.to_string()), ("E2_E4", format!("{}/{}", inf.e2, inf.e4)), ("v2", inf.order.trailing_zeros().to_string()),
        ("mod4_E2", format!("{}/{}", m4(inf.order), inf.e2)), ("odd_jFq", if inf.order % 2 == 1 { format!("{}", inf.j_fq) } else { "even".into() })] {
        if grp == "E2_E4" && n == 7 { *agg.entry((scope.to_string(), "stratum".to_string(), stratum(inf).to_string())).or_default().entry(g).or_insert(0) += 1; }
        *agg.entry((scope.to_string(), grp.to_string(), key)).or_default().entry(g).or_insert(0) += 1; } };
    let mut mr_tot: BTreeMap<(u32, u32, u64), u64> = BTreeMap::new(); let mut viol: BTreeMap<&str, u64> = BTreeMap::new(); let mut mism = 0u64; let mut checked = 0u64;
    let mut tally = |inf: &Info, r: &Res, mr_tot: &mut BTreeMap<(u32, u32, u64), u64>, viol: &mut BTreeMap<&str, u64>| { for (&(m, rr), &c) in &r.mr { *mr_tot.entry((m, rr, inf.e2)).or_insert(0) += c; }
        for v in violations(&f, inf, r) { *viol.entry(v).or_insert(0) += 1; } mism += r.mismatch; checked += 1; assert_eq!(r.structures, structures); };
    if strata_k > 0 {
        // n = 7, q = 3: every class via the characteristic-3 families; fixed-seed draw per stratum; all j in F_q classes
        let cl = classes_fam(&f); let infos: Vec<Info> = cl.reps.iter().map(|c| info(&f, c)).collect();
        let names = ["odd", "odd_jFq", "Z2_2mod4", "Z2_0mod4", "split"];
        let mut rg = Rng::new(q as u64 * 1000 + n as u64 * 10 + 7);
        let mut picks: Vec<usize> = vec![]; let mut counts: Vec<(usize, usize)> = vec![];
        for nm in names { let mut idx: Vec<usize> = (0..cl.reps.len()).filter(|&i| stratum(&infos[i]) == nm).collect();
            for i in (1..idx.len()).rev() { let j = rg.below(i as u32 + 1) as usize; idx.swap(i, j); }
            let take = if nm == "odd_jFq" { idx.len() } else { strata_k.min(idx.len()) }; counts.push((idx.len(), take)); picks.extend(idx[..take].iter().cloned()); }
        let mut models: Vec<usize> = picks.clone(); let mut nbs: Vec<Vec<usize>> = vec![];
        for &i in &picks { let v: Vec<usize> = neighbours(&f, &cl.reps[i], false).iter().map(|c2| cl.of(&f, c2) as usize).collect(); for &k in &v { if !models.contains(&k) { models.push(k); } } nbs.push(v); }
        let cvs: Vec<Cv> = models.iter().map(|&i| cl.reps[i]).collect(); let res = par(&cvs);
        let at = |i: usize| -> usize { models.iter().position(|&x| x == i).unwrap() };
        for (pi, &i) in picks.iter().enumerate() { let r = &res[at(i)]; let mut g2 = r.min_g; for &k in &nbs[pi] { g2 = g2.min(res[at(k)].min_g); }
            emit(&infos[i], r, g2, None, stratum(&infos[i])); add("self", &infos[i], r.min_g); add("2isog", &infos[i], g2); tally(&infos[i], r, &mut mr_tot, &mut viol); }
        for (mi, &i) in models.iter().enumerate() { if picks.contains(&i) { continue; } let r = &res[mi]; emit(&infos[i], r, r.min_g, None, "neighbour"); tally(&infos[i], r, &mut mr_tot, &mut viol); }
        let strata_json = names.iter().zip(&counts).map(|(nm, (a, b))| format!("\"{}\":{{\"classes\":{},\"picked\":{}}}", nm, a, b)).collect::<Vec<_>>().join(",");
        println!("{{\"rec\":\"totals\",\"q\":{},\"n\":{},\"classes\":{},\"strata\":{{{}}},\"picked\":{},\"neighbor_models\":{},\"models_total\":{},\"structures_per_model\":{},\"mismatches\":{},\"wall_s\":{:.1}}}",
            q, n, cl.reps.len(), strata_json, picks.len(), models.len() - picks.len(), models.len(), structures, mism, t0.elapsed().as_secs_f64());
    } else if sample == 0 {
        let cl = classes(&f); let infos: Vec<Info> = cl.reps.iter().map(|c| info(&f, c)).collect();
        let res = par(&cl.reps);
        let mut cmin: HashMap<u64, u32> = HashMap::new(); for i in 0..cl.reps.len() { let e = cmin.entry(infos[i].order).or_insert(99); *e = (*e).min(res[i].min_g); }
        for i in 0..cl.reps.len() { let mut g2 = res[i].min_g; for c2 in neighbours(&f, &cl.reps[i], short) { g2 = g2.min(res[cl.of(&f, &c2) as usize].min_g); }
            let gc = cmin[&infos[i].order]; emit(&infos[i], &res[i], g2, Some(gc), "class");
            add("self", &infos[i], res[i].min_g); add("2isog", &infos[i], g2); add("class", &infos[i], gc); tally(&infos[i], &res[i], &mut mr_tot, &mut viol); }
        println!("{{\"rec\":\"totals\",\"q\":{},\"n\":{},\"classes\":{},\"isogeny_classes\":{},\"mismatches\":{},\"wall_s\":{:.1}}}", q, n, cl.reps.len(), cmin.len(), mism, t0.elapsed().as_secs_f64());
    } else {
        assert!(short, "sampling uses the short Weierstrass stream of the merged tool (p > 3)");
        let tag = if n == 3 { q as u64 } else { q as u64 * 100 + n as u64 };
        let mut rg = Rng::new(tag); let mut picks = vec![]; while picks.len() < sample { let (a, b) = (rg.below(f.size), rg.below(f.size)); let c = Cv { a2: 0, a4: a, a6: b }; if disc(&f, &c) != 0 { picks.push(c); } }
        let mut all = picks.clone(); let nb: Vec<Vec<Cv>> = picks.iter().map(|c| neighbours(&f, c, true)).collect(); for v in &nb { all.extend(v.iter().cloned()); }
        let res = par(&all); let mut k = picks.len();
        for i in 0..picks.len() { let inf = info(&f, &picks[i]); let mut g2 = res[i].min_g;
            for c2 in &nb[i] { g2 = g2.min(res[k].min_g); let inf2 = info(&f, c2); tally(&inf2, &res[k], &mut mr_tot, &mut viol); emit(&inf2, &res[k], res[k].min_g, None, "neighbour"); k += 1; }
            emit(&inf, &res[i], g2, None, "sample"); add("self", &inf, res[i].min_g); add("2isog", &inf, g2); tally(&inf, &res[i], &mut mr_tot, &mut viol); }
        println!("{{\"rec\":\"totals\",\"q\":{},\"n\":{},\"sampled\":{},\"neighbor_models\":{},\"models_total\":{},\"structures_per_model\":{},\"mismatches\":{},\"wall_s\":{:.1}}}", q, n, picks.len(), all.len() - picks.len(), all.len(), structures, mism, t0.elapsed().as_secs_f64());
    }
    for ((scope, grp, key), h) in &agg { let c: u64 = h.values().sum(); let fl = *h.get(&n).unwrap_or(&0);
        println!("{{\"rec\":\"group\",\"q\":{},\"n\":{},\"scope\":\"{}\",\"by\":\"{}\",\"key\":\"{}\",\"curves\":{},\"at_floor_genus\":{},\"at_floor\":{},\"at_floor_fraction\":{:.6},\"min\":{},\"curves_by_min_genus\":{}}}",
            q, n, scope, grp, key, c, n, fl, fl as f64 / c as f64, h.keys().next().unwrap(), hist_json(h)); }
    for ((m, r, e2), c) in &mr_tot { println!("{{\"rec\":\"mr\",\"q\":{},\"n\":{},\"m\":{},\"r\":{},\"E2\":{},\"structures\":{}}}", q, n, m, r, e2, c); }
    println!("{{\"rec\":\"derived_checks\",\"q\":{},\"n\":{},\"models_checked\":{},\"violations\":{}}}", q, n, checked, hist_json(&viol.iter().map(|(k, v)| (k.to_string(), *v)).collect()));
}
