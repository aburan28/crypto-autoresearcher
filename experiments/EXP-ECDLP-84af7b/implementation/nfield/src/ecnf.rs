//! Elliptic curves y^2 = x^3 + a2 x^2 + a4 x + a6 over the number field K with rational
//! coefficients: finite-field reductions, bounded point search in sup-norm shells sieved by
//! quadratic-residue tests at auxiliary primes, torsion bounds by reduction, residues at the
//! degree-one primes above p and the Galois trace relation.

use crate::field::{big, rat, Elt, NumberField};
use crate::modpoly::{invmod, mulmod, powmod};
use crate::rng::Rng;
use num_bigint::{BigInt, BigUint};
use num_integer::Integer;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use std::collections::HashSet;

// ---------------------------------------------------------------------------------------------
// finite-field curve arithmetic (affine, short Weierstrass, p < 2^63)
// ---------------------------------------------------------------------------------------------

pub type FpPoint = Option<(u64, u64)>;

pub fn fp_add(p1: FpPoint, p2: FpPoint, a: u64, p: u64) -> FpPoint {
    let (x1, y1) = match p1 {
        None => return p2,
        Some(v) => v,
    };
    let (x2, y2) = match p2 {
        None => return p1,
        Some(v) => v,
    };
    let lam = if x1 == x2 {
        if (y1 + y2) % p == 0 {
            return None;
        }
        let num = (mulmod(3, mulmod(x1, x1, p), p) + a) % p;
        mulmod(num, invmod(mulmod(2, y1, p), p), p)
    } else {
        mulmod((y2 + p - y1) % p, invmod((x2 + p - x1) % p, p), p)
    };
    let x3 = (mulmod(lam, lam, p) + 2 * p - x1 - x2) % p;
    let y3 = (mulmod(lam, (x1 + p - x3) % p, p) + p - y1) % p;
    Some((x3, y3))
}

pub fn fp_mul(mut k: u64, mut pt: FpPoint, a: u64, p: u64) -> FpPoint {
    let mut r: FpPoint = None;
    while k > 0 {
        if k & 1 == 1 {
            r = fp_add(r, pt, a, p);
        }
        pt = fp_add(pt, pt, a, p);
        k >>= 1;
    }
    r
}

/// Exact point count by Legendre sums (p < ~2^22).
pub fn fp_count(p: u64, a: u64, b: u64) -> u64 {
    let mut table = vec![false; p as usize];
    for y in 0..p {
        table[mulmod(y, y, p) as usize] = true;
    }
    let mut n = p as i64 + 1;
    for x in 0..p {
        let v = (mulmod(mulmod(x, x, p), x, p) + mulmod(a, x, p) + b) % p;
        if v == 0 {
            continue;
        }
        n += if table[v as usize] { 1 } else { -1 };
    }
    n as u64
}

pub fn sqrt_mod_prime(n: u64, p: u64) -> u64 {
    let n = n % p;
    if n == 0 {
        return 0;
    }
    if p % 4 == 3 {
        return powmod(n, (p + 1) / 4, p);
    }
    let mut q = p - 1;
    let mut s = 0;
    while q.is_multiple_of(2) {
        q /= 2;
        s += 1;
    }
    let mut z = 2;
    while powmod(z, (p - 1) / 2, p) != p - 1 {
        z += 1;
    }
    let (mut m, mut c, mut t, mut r) = (s, powmod(z, q, p), powmod(n, q, p), powmod(n, q.div_ceil(2), p));
    while t != 1 {
        let mut i = 0;
        let mut tt = t;
        while tt != 1 {
            tt = mulmod(tt, tt, p);
            i += 1;
        }
        let b = powmod(c, 1u64 << (m - i - 1), p);
        m = i;
        c = mulmod(b, b, p);
        t = mulmod(t, c, p);
        r = mulmod(r, b, p);
    }
    r
}

/// Group order of y^2 = x^3 + a x + b over F_p by baby-step giant-step order candidates
/// intersected over random points; None if ambiguous after `tries` points.
pub fn fp_order_bsgs(p: u64, a: u64, b: u64, rng: &mut Rng, tries: usize) -> Option<u64> {
    let random_point = |rng: &mut Rng| -> (u64, u64) {
        loop {
            let x = rng.below(p);
            let v = (mulmod(mulmod(x, x, p), x, p) + mulmod(a, x, p) + b) % p;
            if v == 0 {
                continue;
            }
            if powmod(v, (p - 1) / 2, p) == 1 {
                return (x, sqrt_mod_prime(v, p));
            }
        }
    };
    let w = (p as f64).sqrt() as u64;
    let lo = p + 1 - 2 * w - 1;
    let width = 4 * w + 3;
    let m = (width as f64).sqrt() as u64 + 1;
    let mut cands: Option<HashSet<u64>> = None;
    for _ in 0..tries {
        let pt = Some(random_point(rng));
        let mut baby: std::collections::HashMap<FpPoint, u64> = std::collections::HashMap::new();
        let mut r: FpPoint = None;
        for j in 0..m {
            baby.entry(r).or_insert(j);
            r = fp_add(r, pt, a, p);
        }
        let mp = r;
        let mut base = fp_mul(lo, pt, a, p);
        let mut c: HashSet<u64> = HashSet::new();
        for i in 0..m + 2 {
            if let Some(&j) = baby.get(&base) {
                c.insert(lo + i * m - j);
            }
            let neg = base.map(|(x, y)| (x, (p - y) % p));
            if let Some(&j) = baby.get(&neg) {
                c.insert(lo + i * m + j);
            }
            base = fp_add(base, mp, a, p);
        }
        let c: HashSet<u64> = c.into_iter().filter(|&n| n >= lo && n <= lo + width && fp_mul(n, pt, a, p).is_none()).collect();
        cands = Some(match cands {
            None => c,
            Some(prev) => prev.intersection(&c).cloned().collect(),
        });
        if cands.as_ref().unwrap().len() == 1 {
            return cands.unwrap().into_iter().next();
        }
    }
    None
}

// ---------------------------------------------------------------------------------------------
// curves over K
// ---------------------------------------------------------------------------------------------

pub type KPoint = (Elt, Elt);

pub struct CurveNF<'a> {
    pub k: &'a NumberField,
    pub a2: BigRational,
    pub a4: BigRational,
    pub a6: BigRational,
    pub shift: BigRational,
    /// short model x' = x + a2/3: y^2 = x'^3 + A x' + B
    pub a_short: BigRational,
    pub b_short: BigRational,
    a2_elt: Elt,
    a4_elt: Elt,
    a6_elt: Elt,
}

impl<'a> CurveNF<'a> {
    pub fn new(k: &'a NumberField, a4: BigRational, a6: BigRational, a2: BigRational) -> CurveNF<'a> {
        let three = rat(3);
        let shift = &a2 / &three;
        let a_short = &a4 - &a2 * &a2 / &three;
        let b_short = &a6 - &a2 * &a4 / &three + rat(2) * &a2 * &a2 * &a2 / rat(27);
        let disc = rat(4) * &a_short * &a_short * &a_short + rat(27) * &b_short * &b_short;
        assert!(!disc.is_zero(), "singular curve");
        CurveNF { a2_elt: k.from_rational(&a2), a4_elt: k.from_rational(&a4), a6_elt: k.from_rational(&a6), k, a2, a4, a6, shift, a_short, b_short }
    }

    pub fn rhs(&self, x: &Elt) -> Elt {
        let k = self.k;
        let x2 = k.mul(x, x);
        let t = k.add(&k.add(&k.mul(&x2, x), &k.mul(&self.a2_elt, &x2)), &k.mul(&self.a4_elt, x));
        k.add(&t, &self.a6_elt)
    }

    fn coeff_mod(c: &BigRational, q: u64) -> u64 {
        let qb = BigInt::from(q);
        let n = c.numer().mod_floor(&qb).to_u64().unwrap();
        let d = c.denom().mod_floor(&qb).to_u64().unwrap();
        mulmod(n, invmod(d, q), q)
    }

    /// Short-model (A, B) reduced mod q.
    pub fn short_mod(&self, q: u64) -> (u64, u64) {
        (Self::coeff_mod(&self.a_short, q), Self::coeff_mod(&self.b_short, q))
    }

    /// Values of x^3 + a2 x^2 + a4 x + a6 at each root mod q, for x = x_num / e.
    pub fn rhs_embed(&self, x_num: &[i64], e_inv: u64, q: u64, roots: &[u64]) -> Vec<u64> {
        let a2 = Self::coeff_mod(&self.a2, q);
        let a4 = Self::coeff_mod(&self.a4, q);
        let a6 = Self::coeff_mod(&self.a6, q);
        roots
            .iter()
            .map(|&r| {
                let mut xv = 0u64;
                let mut pw = 1u64;
                for &c in x_num {
                    if c != 0 {
                        let cu = c.rem_euclid(q as i64) as u64;
                        xv = (xv + mulmod(cu, pw, q)) % q;
                    }
                    pw = mulmod(pw, r, q);
                }
                xv = mulmod(xv, e_inv, q);
                (mulmod(mulmod((xv + a2) % q, xv, q), xv, q) + mulmod(a4, xv, q) + a6) % q
            })
            .collect()
    }

    /// Reduction of a K-point at the degree-one prime (t - root, q) in short-model coordinates;
    /// None if the point is not integral there.
    pub fn reduce_point(&self, pt: &KPoint, q: u64, root: u64) -> FpPoint {
        let x = self.k.embed(&pt.0, q, root)?;
        let y = self.k.embed(&pt.1, q, root)?;
        let s = Self::coeff_mod(&self.shift, q);
        Some(((x + s) % q, y))
    }

    /// The same at a big prime p (short-model x, y as big integers).
    pub fn reduce_point_big(&self, pt: &KPoint, p: &BigUint, root: &BigUint) -> Option<(BigUint, BigUint)> {
        let x = self.k.embed_big(&pt.0, p, root)?;
        let y = self.k.embed_big(&pt.1, p, root)?;
        let pb = BigInt::from(p.clone());
        let sn = self.shift.numer().mod_floor(&pb);
        let sd = self.shift.denom().mod_floor(&pb).to_biguint().unwrap();
        let sd_inv = sd.modpow(&(p - BigUint::from(2u32)), p);
        let s = (sn * BigInt::from(sd_inv)).mod_floor(&pb).to_biguint().unwrap();
        Some(((x + s) % p, y))
    }

    /// Bounded point search: x = a(t)/e with coefficient vectors in sup-norm shells X = 0, 1, ...
    /// and denominators e in `denominators`, sieved at the auxiliary primes, then an exact square
    /// root in K. Calls `on_event` with Point / Shell / Checkpoint events; stops after `max_work`
    /// candidates. A shell that fits in twice the remaining budget is exhausted in seeded random
    /// order; a larger one is sampled uniformly without replacement.
    pub fn iter_search(&self, aux: &[u64], max_work: u64, checkpoints: &[u64], seed: &str, denominators: &[i64], on_event: &mut dyn FnMut(Event)) {
        let k = self.k;
        let d = k.d;
        let aux_roots: Vec<Vec<u64>> = aux.iter().map(|&q| k.roots_mod(q)).collect();
        let e_inv: Vec<Vec<u64>> = denominators.iter().map(|&e| aux.iter().map(|&q| invmod((e as u64) % q, q)).collect()).collect();
        let mut rng = Rng::seeded(&format!("ecnf-search:{}:{}", seed, d));
        let mut cps: Vec<u64> = checkpoints.to_vec();
        cps.sort_unstable();
        cps.dedup();
        let mut cp_i = 0usize;
        let mut tried = 0u64;
        let mut shells_done = 0u64;
        let mut seen_x: HashSet<String> = HashSet::new();
        let mut x_shell = 0i64;
        while tried < max_work {
            for (ei, &e) in denominators.iter().enumerate() {
                let vecs = shell_order(d, x_shell, (max_work - tried) as usize, &mut rng);
                for vec in vecs {
                    if tried >= max_work {
                        return;
                    }
                    let any = vec.iter().any(|&v| v != 0);
                    if e > 1 && any {
                        let mut gg = e;
                        for &v in &vec {
                            if v != 0 {
                                gg = gg.gcd(&v.abs());
                            }
                        }
                        if gg != 1 {
                            continue;
                        }
                    }
                    if !any && e > 1 {
                        continue;
                    }
                    tried += 1;
                    while cp_i < cps.len() && tried >= cps[cp_i] {
                        on_event(Event::Checkpoint { tried, shells: shells_done });
                        cp_i += 1;
                    }
                    let mut ok: Option<bool> = Some(true);
                    'aux: for (qi, &q) in aux.iter().enumerate() {
                        for v in self.rhs_embed(&vec, e_inv[ei][qi], q, &aux_roots[qi]) {
                            if v == 0 {
                                ok = None;
                                break 'aux;
                            }
                            if powmod(v, (q - 1) / 2, q) != 1 {
                                ok = Some(false);
                                break 'aux;
                            }
                        }
                    }
                    if ok == Some(false) {
                        continue;
                    }
                    let x: Elt = vec.iter().map(|&v| BigRational::new(big(v), big(e))).collect();
                    let key = k.elt_to_string(&x);
                    if !seen_x.insert(key) {
                        continue;
                    }
                    let z = self.rhs(&x);
                    if k.is_zero(&z) {
                        on_event(Event::Point { tried, shells: shells_done, point: (x, k.zero()) });
                        continue;
                    }
                    if let Some(y) = k.sqrt(&z, aux) {
                        let ny = k.neg(&y);
                        on_event(Event::Point { tried, shells: shells_done, point: (x.clone(), y) });
                        on_event(Event::Point { tried, shells: shells_done, point: (x, ny) });
                    }
                }
            }
            shells_done = (x_shell + 1) as u64;
            x_shell += 1;
            on_event(Event::Shell { tried, shells: shells_done });
        }
    }
}

pub enum Event {
    Point { tried: u64, shells: u64, point: KPoint },
    Shell { tried: u64, shells: u64 },
    Checkpoint { tried: u64, shells: u64 },
}

pub fn shell_size(d: usize, x: i64) -> u128 {
    if x == 0 {
        1
    } else {
        (2 * x as u128 + 1).pow(d as u32) - (2 * x as u128 - 1).pow(d as u32)
    }
}

/// Integer vectors of length d with sup-norm exactly X, in a deterministic order, O(size).
pub fn shell(d: usize, x: i64) -> Vec<Vec<i64>> {
    if x == 0 {
        return vec![vec![0; d]];
    }
    let mut out = Vec::new();
    let inner: Vec<i64> = (-(x - 1)..x).collect();
    let full: Vec<i64> = (-x..=x).collect();
    for i in 0..d {
        let mut head = vec![inner[0]; i];
        let mut head_idx = vec![0usize; i];
        loop {
            for &s in &[-x, x] {
                let mut tail_idx = vec![0usize; d - i - 1];
                loop {
                    let mut v = head.clone();
                    v.push(s);
                    for &ti in &tail_idx {
                        v.push(full[ti]);
                    }
                    out.push(v);
                    // increment tail
                    let mut pos = tail_idx.len();
                    loop {
                        if pos == 0 {
                            break;
                        }
                        pos -= 1;
                        tail_idx[pos] += 1;
                        if tail_idx[pos] < full.len() {
                            break;
                        }
                        tail_idx[pos] = 0;
                        if pos == 0 {
                            pos = usize::MAX;
                            break;
                        }
                    }
                    if tail_idx.is_empty() || pos == usize::MAX {
                        break;
                    }
                }
            }
            // increment head
            if i == 0 {
                break;
            }
            let mut pos = i;
            let mut carried_out = false;
            loop {
                pos -= 1;
                head_idx[pos] += 1;
                if head_idx[pos] < inner.len() {
                    head[pos] = inner[head_idx[pos]];
                    break;
                }
                head_idx[pos] = 0;
                head[pos] = inner[0];
                if pos == 0 {
                    carried_out = true;
                    break;
                }
            }
            if carried_out {
                break;
            }
        }
    }
    out
}

/// Vectors of sup-norm exactly X: exhaustive in seeded random order when the shell is at most
/// twice the budget, otherwise `budget` uniform samples without replacement.
pub fn shell_order(d: usize, x: i64, budget: usize, rng: &mut Rng) -> Vec<Vec<i64>> {
    let size = shell_size(d, x);
    if size <= 2 * budget as u128 {
        let mut vecs = shell(d, x);
        rng.shuffle(&mut vecs);
        return vecs;
    }
    let mut seen: HashSet<Vec<i64>> = HashSet::new();
    let mut out = Vec::new();
    while out.len() < budget {
        let v: Vec<i64> = (0..d).map(|_| rng.range(-x, x)).collect();
        if v.iter().map(|c| c.abs()).max().unwrap() != x || seen.contains(&v) {
            continue;
        }
        seen.insert(v.clone());
        out.push(v);
    }
    out
}

// ---------------------------------------------------------------------------------------------
// torsion bound, residues and the trace relation
// ---------------------------------------------------------------------------------------------

/// gcd of #E(F_q) over degree-one primes q bounds |E(K)_tors|.
pub fn torsion_bound(curve: &CurveNF, primes: &[u64], rng: &mut Rng) -> u64 {
    let mut g = 0u64;
    for &q in primes {
        let (a, b) = curve.short_mod(q);
        let n = if q < 1 << 21 { fp_count(q, a, b) } else { fp_order_bsgs(q, a, b, rng, 6).unwrap_or(0) };
        g = g.gcd(&n);
    }
    g
}

/// True if P could be torsion: at every listed prime the reduction's order divides T. A False is
/// a proof that P is not torsion.
pub fn is_torsion_candidate(curve: &CurveNF, pt: &KPoint, primes: &[u64], t: u64) -> bool {
    for &q in primes {
        let (a, _) = curve.short_mod(q);
        for root in curve.k.roots_mod(q) {
            if let Some(r) = curve.reduce_point(pt, q, root) {
                if fp_mul(t, Some(r), a, q).is_some() {
                    return false;
                }
            }
        }
    }
    true
}

/// Residues of P at every degree-one prime above p (one per root of g mod p); None entries for
/// non-integral reductions.
pub fn residues_at_p(curve: &CurveNF, pt: &KPoint, p: u64) -> Vec<FpPoint> {
    curve.k.roots_mod(p).into_iter().map(|root| curve.reduce_point(pt, p, root)).collect()
}

/// [T] * sum of residues = O in E(F_p). None if some residue is missing.
pub fn trace_relation_holds(curve: &CurveNF, residues: &[FpPoint], p: u64, t: u64) -> Option<bool> {
    let (a, _) = curve.short_mod(p);
    let mut s: FpPoint = None;
    for r in residues {
        let r = (*r)?;
        s = fp_add(s, Some(r), a, p);
    }
    Some(fp_mul(t, s, a, p).is_none())
}

/// Helper: a BigInt as i64 if it fits.
pub fn to_i64(x: &BigInt) -> Option<i64> {
    x.to_i64()
}

pub fn one() -> BigRational {
    BigRational::one()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::field::rat_frac;

    #[test]
    fn shell_matches_brute_force() {
        for d in 1..=4usize {
            for x in 0..=3i64 {
                let mut got = shell(d, x);
                got.sort();
                let mut want: Vec<Vec<i64>> = Vec::new();
                let n = (2 * x + 1) as usize;
                let total = n.pow(d as u32);
                for idx in 0..total {
                    let mut v = Vec::new();
                    let mut r = idx;
                    for _ in 0..d {
                        v.push((r % n) as i64 - x);
                        r /= n;
                    }
                    if v.iter().map(|c| c.abs()).max().unwrap() == x {
                        want.push(v);
                    }
                }
                want.sort();
                assert_eq!(got, want, "d={} x={}", d, x);
                assert_eq!(got.len() as u128, shell_size(d, x));
            }
        }
    }

    #[test]
    fn torsion_of_11a1_over_q() {
        let k = NumberField::from_i64(&[0, 1]);
        // 11a1 b-model: a2 = -1 (b2/4 = (0 + 4*(-1))/4), a4 = -10, a6 = (1 + 4*(-20))/4
        let e = CurveNF::new(&k, rat(-10), rat_frac(-79, 4), rat(-1));
        let aux = k.degree_one_primes(8, 1_000_000, &[8191], 200000);
        let mut found = Vec::new();
        e.iter_search(&aux, 3000, &[], "t", &[1, 2, 3, 4], &mut |ev| {
            if let Event::Point { point, .. } = ev {
                found.push(point);
            }
        });
        assert_eq!(found.len(), 4);
        let mut rng = Rng::seeded("o");
        let t = torsion_bound(&e, &aux[..6], &mut rng);
        assert_eq!(t, 5);
        for pt in &found {
            assert!(is_torsion_candidate(&e, pt, &aux[..6], t));
            let res = residues_at_p(&e, pt, 8191);
            assert_eq!(trace_relation_holds(&e, &res, 8191, t), Some(true));
        }
    }

    #[test]
    fn nontorsion_point_found_over_quadratic_field() {
        let k = NumberField::from_i64(&[-13, 0, 1]);
        let e = CurveNF::new(&k, rat(-9), rat(0), rat(0)); // y^2 = x^3 - 9x
        let aux = k.degree_one_primes(8, 1_000_000, &[8191], 200000);
        let mut rng = Rng::seeded("o");
        let t = torsion_bound(&e, &aux[..6], &mut rng);
        let mut n = 0;
        e.iter_search(&aux, 10000, &[], "1", &[1, 2, 3, 4], &mut |ev| {
            if let Event::Point { point, .. } = ev {
                if !k.is_rational(&point.0) && !is_torsion_candidate(&e, &point, &aux[..6], t) {
                    n += 1;
                }
            }
        });
        assert!(n > 0, "expected a non-torsion point over Q(sqrt 13)");
    }
}
