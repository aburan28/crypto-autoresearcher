//! The number field K = Q[t]/(g) for a monic g in Z[t]: exact arithmetic on elements (vectors of
//! rationals in the power basis), the polynomial discriminant, roots and complete splitting
//! modulo primes, embeddings into F_q, degree-one and lift primes, exact square roots, Gaussian
//! period polynomials for the cyclic subfields of Q(zeta_m), and seeded random fields in which a
//! given prime splits completely.

use crate::modpoly::{self, Poly};
use crate::rng::Rng;
use num_bigint::{BigInt, BigUint, Sign};
use num_integer::Integer;
use num_rational::BigRational;
use num_traits::{One, Signed, ToPrimitive, Zero};
use std::cell::RefCell;
use std::collections::HashMap;

pub type Elt = Vec<BigRational>;

pub fn big(x: i64) -> BigInt {
    BigInt::from(x)
}

pub fn rat(x: i64) -> BigRational {
    BigRational::from_integer(big(x))
}

pub fn rat_frac(n: i64, d: i64) -> BigRational {
    BigRational::new(big(n), big(d))
}

/// Natural log of a positive big integer (f64), accurate to about 1e-15 relative.
pub fn ln_big(x: &BigInt) -> f64 {
    let x = x.abs();
    let bits = x.bits();
    if bits <= 60 {
        return (x.to_f64().unwrap()).ln();
    }
    let shift = bits - 60;
    let top = (&x >> shift).to_f64().unwrap();
    top.ln() + (shift as f64) * std::f64::consts::LN_2
}

/// Deterministic Miller-Rabin for u64 (bases cover all n < 2^64).
pub fn is_prime_u64(n: u64) -> bool {
    if n < 2 {
        return false;
    }
    for &p in &[2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if n.is_multiple_of(p) {
            return n == p;
        }
    }
    let mut d = n - 1;
    let mut s = 0;
    while d.is_multiple_of(2) {
        d /= 2;
        s += 1;
    }
    'outer: for &a in &[2u64, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        let mut x = modpoly::powmod(a, d, n);
        if x == 1 || x == n - 1 {
            continue;
        }
        for _ in 0..s - 1 {
            x = modpoly::mulmod(x, x, n);
            if x == n - 1 {
                continue 'outer;
            }
        }
        return false;
    }
    true
}

/// Miller-Rabin with the first twelve prime bases (deterministic below 3.3e24, a strong
/// probable-prime test beyond).
pub fn is_prime_big(n: &BigUint) -> bool {
    if n.bits() <= 63 {
        return is_prime_u64(n.to_u64().unwrap());
    }
    let one = BigUint::one();
    let two = BigUint::from(2u32);
    for &p in &[2u32, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if (n % BigUint::from(p)).is_zero() {
            return false;
        }
    }
    let nm1 = n - &one;
    let mut d = nm1.clone();
    let mut s = 0u32;
    while (&d % &two).is_zero() {
        d /= &two;
        s += 1;
    }
    'outer: for &a in &[2u32, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        let mut x = BigUint::from(a).modpow(&d, n);
        if x == one || x == nm1 {
            continue;
        }
        for _ in 0..s - 1 {
            x = (&x * &x) % n;
            if x == nm1 {
                continue 'outer;
            }
        }
        return false;
    }
    true
}

/// Rational r = n/d with |n|, d <= sqrt(m/2) and r = a mod m, or None.
pub fn rational_reconstruct(a: &BigInt, m: &BigInt) -> Option<BigRational> {
    let a = a.mod_floor(m);
    let bound: BigInt = (m / BigInt::from(2)).sqrt();
    let (mut r0, mut r1) = (m.clone(), a);
    let (mut s0, mut s1) = (BigInt::zero(), BigInt::one());
    while r1 > bound {
        let qq = &r0 / &r1;
        let r2 = &r0 - &qq * &r1;
        r0 = r1;
        r1 = r2;
        let s2 = &s0 - &qq * &s1;
        s0 = s1;
        s1 = s2;
    }
    if s1.is_zero() || s1.abs() > bound {
        return None;
    }
    if s1.is_negative() {
        r1 = -r1;
        s1 = -s1;
    }
    if r1.gcd(&s1) != BigInt::one() {
        return None;
    }
    Some(BigRational::new(r1, s1))
}

pub fn small_primes(limit: u64) -> Vec<u64> {
    (2..limit).filter(|&n| is_prime_u64(n)).collect()
}

const IRRED_BIG_PRIMES: [u64; 20] = [
    1000003, 1000033, 1000037, 1000039, 1000081, 1000099, 1000117, 1000121, 1000133, 1000151,
    1000159, 1000171, 1000183, 1000187, 1000193, 1000199, 1000211, 1000213, 1000231, 1000249,
];

fn reduce_big(g: &[BigInt], q: u64) -> Poly {
    let qb = BigInt::from(q);
    modpoly::trimmed(g.iter().map(|c| c.mod_floor(&qb).to_u64().unwrap()).collect())
}

/// Some(true) if g is irreducible modulo some small prime (a sufficient test); None if undecided.
pub fn is_irreducible_over_q(g: &[BigInt]) -> Option<bool> {
    let d = g.len() - 1;
    let mut primes = small_primes(400);
    primes.retain(|&p| p >= 3);
    primes.extend_from_slice(&IRRED_BIG_PRIMES);
    for q in primes {
        if let Some(pat) = modpoly::ddf_pattern(&reduce_big(g, q), q) {
            if pat == vec![(d, 1)] {
                return Some(true);
            }
        }
    }
    None
}

// ---------------------------------------------------------------------------------------------
// polynomials over Z/M for a big modulus M (Hensel lifting), reduced modulo the monic g
// ---------------------------------------------------------------------------------------------

fn bp_norm(a: &[BigInt], m: &BigInt) -> Vec<BigInt> {
    a.iter().map(|c| c.mod_floor(m)).collect()
}

fn bp_mul(a: &[BigInt], b: &[BigInt], g: &[BigInt], m: &BigInt) -> Vec<BigInt> {
    let d = g.len() - 1;
    let mut r = vec![BigInt::zero(); 2 * d - 1];
    for (i, ai) in a.iter().enumerate() {
        if ai.is_zero() {
            continue;
        }
        for (j, bj) in b.iter().enumerate() {
            if !bj.is_zero() {
                r[i + j] += ai * bj;
            }
        }
    }
    for i in (d..=2 * d - 2).rev() {
        let c = r[i].mod_floor(m);
        if !c.is_zero() {
            for j in 0..=d {
                r[i - d + j] -= &c * &g[j];
            }
        }
        r[i] = BigInt::zero();
    }
    r.truncate(d);
    bp_norm(&r, m)
}

fn bp_sub(a: &[BigInt], b: &[BigInt], m: &BigInt) -> Vec<BigInt> {
    a.iter().zip(b).map(|(x, y)| (x - y).mod_floor(m)).collect()
}

pub struct NumberField {
    pub g: Vec<BigInt>,
    pub d: usize,
    root_cache: RefCell<HashMap<u64, Vec<u64>>>,
    lift_cache: RefCell<Option<Vec<(u64, Vec<(Poly, usize)>)>>>,
    disc_cache: RefCell<Option<BigInt>>,
}

impl NumberField {
    pub fn new(g: Vec<BigInt>) -> NumberField {
        assert!(g.last().map(|c| c.is_one()).unwrap_or(false), "g must be monic");
        let d = g.len() - 1;
        NumberField { g, d, root_cache: RefCell::new(HashMap::new()), lift_cache: RefCell::new(None), disc_cache: RefCell::new(None) }
    }

    pub fn from_i64(g: &[i64]) -> NumberField {
        NumberField::new(g.iter().map(|&c| big(c)).collect())
    }

    pub fn g_mod(&self, q: u64) -> Poly {
        reduce_big(&self.g, q)
    }

    // --- elements ------------------------------------------------------------------------
    pub fn elt(&self, coeffs: &[BigRational]) -> Elt {
        let mut c: Vec<BigRational> = coeffs.to_vec();
        c.resize(self.d, BigRational::zero());
        c.truncate(self.d);
        c
    }

    pub fn elt_i64(&self, coeffs: &[i64]) -> Elt {
        self.elt(&coeffs.iter().map(|&x| rat(x)).collect::<Vec<_>>())
    }

    pub fn from_rational(&self, r: &BigRational) -> Elt {
        self.elt(std::slice::from_ref(r))
    }

    pub fn zero(&self) -> Elt {
        vec![BigRational::zero(); self.d]
    }

    pub fn add(&self, a: &Elt, b: &Elt) -> Elt {
        a.iter().zip(b).map(|(x, y)| x + y).collect()
    }

    pub fn sub(&self, a: &Elt, b: &Elt) -> Elt {
        a.iter().zip(b).map(|(x, y)| x - y).collect()
    }

    pub fn neg(&self, a: &Elt) -> Elt {
        a.iter().map(|x| -x).collect()
    }

    pub fn mul(&self, a: &Elt, b: &Elt) -> Elt {
        let d = self.d;
        if d == 1 {
            return vec![&a[0] * &b[0]];
        }
        let mut res = vec![BigRational::zero(); 2 * d - 1];
        for (i, ai) in a.iter().enumerate() {
            if ai.is_zero() {
                continue;
            }
            for (j, bj) in b.iter().enumerate() {
                if !bj.is_zero() {
                    res[i + j] += ai * bj;
                }
            }
        }
        for i in (d..=2 * d - 2).rev() {
            if !res[i].is_zero() {
                let c = res[i].clone();
                for j in 0..=d {
                    let t = &c * BigRational::from_integer(self.g[j].clone());
                    res[i - d + j] -= t;
                }
            }
        }
        res.truncate(d);
        res
    }

    pub fn is_zero(&self, a: &Elt) -> bool {
        a.iter().all(|x| x.is_zero())
    }

    pub fn is_rational(&self, a: &Elt) -> bool {
        a.iter().skip(1).all(|x| x.is_zero())
    }

    /// Inverse by solving the d x d linear system M_a y = 1 over Q.
    pub fn inv(&self, a: &Elt) -> Option<Elt> {
        let d = self.d;
        let mut cols = Vec::new();
        for i in 0..d {
            let mut ei = self.zero();
            ei[i] = BigRational::one();
            cols.push(self.mul(a, &ei));
        }
        let mut m: Vec<Vec<BigRational>> = (0..d)
            .map(|i| {
                let mut row: Vec<BigRational> = (0..d).map(|j| cols[j][i].clone()).collect();
                row.push(if i == 0 { BigRational::one() } else { BigRational::zero() });
                row
            })
            .collect();
        for c in 0..d {
            let piv = (c..d).find(|&r| !m[r][c].is_zero())?;
            m.swap(c, piv);
            let pv = m[c][c].clone();
            for x in m[c].iter_mut() {
                *x = &*x / &pv;
            }
            for r in 0..d {
                if r != c && !m[r][c].is_zero() {
                    let f = m[r][c].clone();
                    let rowc = m[c].clone();
                    for (x, y) in m[r].iter_mut().zip(&rowc) {
                        *x -= &f * y;
                    }
                }
            }
        }
        Some((0..d).map(|i| m[i][d].clone()).collect())
    }

    /// Naive logarithmic height proxy: log of max(|numerators|, lcm of denominators).
    pub fn height(&self, a: &Elt) -> f64 {
        let mut den = BigInt::one();
        for x in a {
            den = den.lcm(x.denom());
        }
        let mut num = BigInt::zero();
        for x in a {
            let n = (x * BigRational::from_integer(den.clone())).to_integer().abs();
            if n > num {
                num = n;
            }
        }
        let m = if num > den { num } else { den };
        if m <= BigInt::one() {
            0.0
        } else {
            ln_big(&m)
        }
    }

    pub fn elt_to_string(&self, a: &Elt) -> String {
        a.iter().map(rat_to_string).collect::<Vec<_>>().join(",")
    }

    // --- discriminant ----------------------------------------------------------------------
    /// Polynomial discriminant disc(g) = (-1)^(d(d-1)/2) Res(g, g') (g monic), via the Sylvester
    /// matrix over Q.
    pub fn discriminant(&self) -> BigInt {
        if let Some(d) = self.disc_cache.borrow().as_ref() {
            return d.clone();
        }
        let d = self.d;
        let res = if d == 1 {
            BigInt::one()
        } else {
            let g = &self.g;
            let dg: Vec<BigInt> = (1..=d).map(|i| big(i as i64) * &g[i]).collect();
            let n = 2 * d - 1;
            let mut m = vec![vec![BigRational::zero(); n]; n];
            for r in 0..d - 1 {
                for j in 0..=d {
                    m[r][r + j] = BigRational::from_integer(g[d - j].clone());
                }
            }
            for r in 0..d {
                for j in 0..d {
                    m[d - 1 + r][r + j] = BigRational::from_integer(dg[d - 1 - j].clone());
                }
            }
            let mut det = BigRational::one();
            let mut singular = false;
            for c in 0..n {
                let piv = (c..n).find(|&r| !m[r][c].is_zero());
                let piv = match piv {
                    None => {
                        singular = true;
                        break;
                    }
                    Some(p) => p,
                };
                if piv != c {
                    m.swap(c, piv);
                    det = -det;
                }
                let pv = m[c][c].clone();
                det *= &pv;
                for r in c + 1..n {
                    if !m[r][c].is_zero() {
                        let f = &m[r][c] / &pv;
                        let rowc = m[c].clone();
                        for (x, y) in m[r].iter_mut().zip(&rowc) {
                            *x -= &f * y;
                        }
                    }
                }
            }
            if singular {
                BigInt::zero()
            } else {
                let sign = if (d * (d - 1) / 2) % 2 == 1 { -1 } else { 1 };
                (det * BigRational::from_integer(big(sign))).to_integer()
            }
        };
        *self.disc_cache.borrow_mut() = Some(res.clone());
        res
    }

    pub fn root_discriminant(&self) -> f64 {
        let dsc = self.discriminant();
        if dsc.is_zero() {
            return 0.0;
        }
        (ln_big(&dsc) / self.d as f64).exp()
    }

    // --- primes and embeddings ------------------------------------------------------------
    pub fn roots_mod(&self, q: u64) -> Vec<u64> {
        if let Some(r) = self.root_cache.borrow().get(&q) {
            return r.clone();
        }
        let r = if self.d > 1 {
            modpoly::roots(&self.g_mod(q), q)
        } else {
            let qb = BigInt::from(q);
            vec![(-&self.g[0]).mod_floor(&qb).to_u64().unwrap()]
        };
        self.root_cache.borrow_mut().insert(q, r.clone());
        r
    }

    pub fn splits_completely(&self, q: u64) -> bool {
        self.roots_mod(q).len() == self.d && !(self.discriminant() % BigInt::from(q)).is_zero()
    }

    /// Image of a in F_q under t -> root (q < 2^63); None if a denominator vanishes mod q.
    pub fn embed(&self, a: &Elt, q: u64, root: u64) -> Option<u64> {
        let qb = BigInt::from(q);
        let mut num = 0u64;
        let mut pw = 1u64;
        for x in a {
            if !x.is_zero() {
                let den = x.denom().mod_floor(&qb).to_u64().unwrap();
                if den == 0 {
                    return None;
                }
                let n = x.numer().mod_floor(&qb).to_u64().unwrap();
                let v = modpoly::mulmod(modpoly::mulmod(n, modpoly::invmod(den, q), q), pw, q);
                num = (num + v) % q;
            }
            pw = modpoly::mulmod(pw, root, q);
        }
        Some(num)
    }

    /// Image of a in F_p under t -> root for a big prime p.
    pub fn embed_big(&self, a: &Elt, p: &BigUint, root: &BigUint) -> Option<BigUint> {
        let pb = BigInt::from_biguint(Sign::Plus, p.clone());
        let mut num = BigInt::zero();
        let mut pw = BigInt::one();
        let rootb = BigInt::from_biguint(Sign::Plus, root.clone());
        for x in a {
            if !x.is_zero() {
                let den = x.denom().mod_floor(&pb);
                if den.is_zero() {
                    return None;
                }
                let inv = den.to_biguint().unwrap().modpow(&(p - BigUint::from(2u32)), p);
                let n = x.numer().mod_floor(&pb);
                num = (num + n * BigInt::from_biguint(Sign::Plus, inv) * &pw).mod_floor(&pb);
            }
            pw = (&pw * &rootb).mod_floor(&pb);
        }
        Some(num.to_biguint().unwrap())
    }

    /// The first `count` primes >= start (not in avoid) in which K splits completely.
    pub fn split_primes(&self, count: usize, start: u64, avoid: &[u64]) -> Vec<u64> {
        let mut out = Vec::new();
        let mut q = start | 1;
        while out.len() < count {
            if !avoid.contains(&q) && is_prime_u64(q) && self.splits_completely(q) {
                out.push(q);
            }
            q += 2;
        }
        out
    }

    /// The first `count` primes q >= start (q not dividing disc, not in avoid) at which g has at
    /// least one root mod q. For a Galois K these are the completely split primes.
    pub fn degree_one_primes(&self, count: usize, start: u64, avoid: &[u64], max_scan: usize) -> Vec<u64> {
        let mut out = Vec::new();
        let disc = self.discriminant();
        let mut q = start | 1;
        let mut scanned = 0;
        while out.len() < count && scanned < max_scan {
            scanned += 1;
            if !avoid.contains(&q) && is_prime_u64(q) && !(&disc % BigInt::from(q)).is_zero() && !self.roots_mod(q).is_empty() {
                out.push(q);
            }
            q += 2;
        }
        out
    }

    /// Primes q (not dividing disc) modulo which g has the fewest irreducible factors, among the
    /// first `candidates` primes >= start; cached. Used by sqrt for Hensel lifting.
    pub fn lift_primes(&self) -> Vec<(u64, Vec<(Poly, usize)>)> {
        if let Some(l) = self.lift_cache.borrow().as_ref() {
            return l.clone();
        }
        let (count, start, candidates) = (3usize, 1_000_007u64, 40usize);
        let disc = self.discriminant();
        let mut found: Vec<(usize, u64, Vec<(Poly, usize)>)> = Vec::new();
        let mut q = start | 1;
        while found.len() < candidates {
            if is_prime_u64(q) && !(&disc % BigInt::from(q)).is_zero() {
                let fac = modpoly::factor(&self.g_mod(q), q);
                if let Some(fac) = fac {
                    found.push((fac.len(), q, fac));
                }
            }
            q += 2;
        }
        found.sort_by_key(|a| (a.0, a.1));
        let out: Vec<(u64, Vec<(Poly, usize)>)> = found.into_iter().take(count).map(|(_, q, f)| (q, f)).collect();
        *self.lift_cache.borrow_mut() = Some(out.clone());
        out
    }

    // --- squares and square roots ---------------------------------------------------------
    /// Some(true) if every embedding at q is a nonzero square, Some(false) if some embedding is a
    /// non-residue, None if an embedding vanishes or a denominator is divisible by q.
    pub fn embeds_are_squares(&self, a: &Elt, q: u64) -> Option<bool> {
        for r in self.roots_mod(q) {
            let v = self.embed(a, q, r)?;
            if v == 0 {
                return None;
            }
            if modpoly::powmod(v, (q - 1) / 2, q) != 1 {
                return Some(false);
            }
        }
        Some(true)
    }

    /// Exact square root of a in K, or None (a not a square). At a lift prime q with
    /// g = h_1 ... h_m mod q: square roots in each F_q[t]/(h_j) by Tonelli-Shanks (a non-residue
    /// anywhere proves a is not a square), CRT for each of the 2^(m-1) sign patterns, Hensel lift
    /// of y and (2y)^-1 in (Z/q^k)[t]/(g) with k doubling, rational reconstruction, exact check.
    pub fn sqrt(&self, a: &Elt, aux_primes: &[u64]) -> Option<Elt> {
        if self.is_zero(a) {
            return Some(a.clone());
        }
        for &q in aux_primes {
            if self.embeds_are_squares(a, q) == Some(false) {
                return None;
            }
        }
        let mut den = BigInt::one();
        for x in a {
            den = den.lcm(x.denom());
        }
        let a_int: Vec<BigInt> = a.iter().map(|x| (x * BigRational::from_integer(den.clone())).to_integer()).collect();
        let seed = format!("nfield-sqrt:{}:{}:{}", self.g.iter().map(|c| c.to_string()).collect::<Vec<_>>().join(","), a_int.iter().map(|c| c.to_string()).collect::<Vec<_>>().join(","), den);
        let mut rng = Rng::seeded(&seed);
        let g = &self.g;
        let d = self.d;
        for (q, factors) in self.lift_primes() {
            let qb = BigInt::from(q);
            if (&den % &qb).is_zero() {
                continue;
            }
            let den_inv_q = modpoly::invmod(den.mod_floor(&qb).to_u64().unwrap(), q);
            let a_q: Poly = modpoly::trimmed(a_int.iter().map(|x| modpoly::mulmod(x.mod_floor(&qb).to_u64().unwrap(), den_inv_q, q)).collect());
            let gq = self.g_mod(q);
            let mut parts: Vec<Poly> = Vec::new();
            let mut singular = false;
            for (h, e) in &factors {
                let r = if a_q.is_empty() { Vec::new() } else { modpoly::rem(&a_q, h, q) };
                if r.is_empty() {
                    singular = true;
                    break;
                }
                {
                    let s = modpoly::ff_sqrt(&r, h, *e, q, &mut rng)?;
                    parts.push(s)
                }
            }
            if singular {
                continue;
            }
            let m = parts.len();
            for pattern in 0u64..(1u64 << (m - 1)) {
                let signed: Vec<Poly> = (0..m)
                    .map(|j| {
                        if j == 0 || (pattern >> (j - 1)) & 1 == 0 {
                            parts[j].clone()
                        } else {
                            parts[j].iter().map(|&c| (q - c) % q).collect()
                        }
                    })
                    .collect();
                let y0 = if m > 1 { modpoly::crt(&signed, &factors, &gq, q) } else { signed[0].clone() };
                let inv_parts: Vec<Poly> = factors
                    .iter()
                    .map(|(h, e)| {
                        let twoy: Poly = modpoly::trimmed(y0.iter().map(|&c| modpoly::mulmod(2, c, q)).collect());
                        modpoly::ff_inverse(&modpoly::rem(&twoy, h, q), h, *e, q)
                    })
                    .collect();
                let z0 = if m > 1 { modpoly::crt(&inv_parts, &factors, &gq, q) } else { inv_parts[0].clone() };
                let to_big = |p: &Poly| -> Vec<BigInt> {
                    let mut v: Vec<BigInt> = p.iter().map(|&c| BigInt::from(c)).collect();
                    v.resize(d, BigInt::zero());
                    v
                };
                let mut y = to_big(&y0);
                let mut z = to_big(&z0);
                let mut k = 1u32;
                for _ in 0..7 {
                    k *= 2;
                    let mk = qb.pow(k);
                    let den_inv = modinv_big(&den, &mk)?;
                    let a_k: Vec<BigInt> = a_int.iter().map(|x| (x * &den_inv).mod_floor(&mk)).collect();
                    let y2 = bp_mul(&y, &y, g, &mk);
                    let diff = bp_sub(&y2, &a_k, &mk);
                    let corr = bp_mul(&diff, &z, g, &mk);
                    y = bp_sub(&y, &corr, &mk);
                    let twoy: Vec<BigInt> = y.iter().map(|c| (c * BigInt::from(2)).mod_floor(&mk)).collect();
                    let yz = bp_mul(&twoy, &z, g, &mk);
                    let mut two_minus = vec![BigInt::zero(); d];
                    two_minus[0] = BigInt::from(2);
                    let two_minus = bp_sub(&two_minus, &yz, &mk);
                    z = bp_mul(&z, &two_minus, g, &mk);
                    let mut cand: Elt = Vec::new();
                    let mut ok = true;
                    for c in &y {
                        match rational_reconstruct(c, &mk) {
                            Some(r) => cand.push(r),
                            None => {
                                ok = false;
                                break;
                            }
                        }
                    }
                    if ok && self.mul(&cand, &cand) == *a {
                        return Some(cand);
                    }
                }
            }
            return None;
        }
        None
    }
}

/// Inverse of a modulo m (m a prime power, gcd(a, m) = 1), by the extended Euclidean algorithm.
pub fn modinv_big(a: &BigInt, m: &BigInt) -> Option<BigInt> {
    let e = a.mod_floor(m).extended_gcd(m);
    if !e.gcd.is_one() {
        return None;
    }
    Some(e.x.mod_floor(m))
}

pub fn rat_to_string(x: &BigRational) -> String {
    if x.denom().is_one() {
        x.numer().to_string()
    } else {
        format!("{}/{}", x.numer(), x.denom())
    }
}

// ---------------------------------------------------------------------------------------------
// cyclic subfields of Q(zeta_m) by Gaussian periods, and random split fields
// ---------------------------------------------------------------------------------------------

/// Multiply in Z[x]/(Phi_m), m prime, via x^m = 1 then the normal form that removes x^(m-1).
fn cyclo_mul(a: &[BigInt], b: &[BigInt], m: usize) -> Vec<BigInt> {
    let mut res = vec![BigInt::zero(); m];
    for (i, ai) in a.iter().enumerate() {
        if ai.is_zero() {
            continue;
        }
        for (j, bj) in b.iter().enumerate() {
            if !bj.is_zero() {
                res[(i + j) % m] += ai * bj;
            }
        }
    }
    let t = res[m - 1].clone();
    let mut out: Vec<BigInt> = res[..m - 1].iter().map(|v| v - &t).collect();
    out.push(BigInt::zero());
    out
}

/// Monic defining polynomial (low -> high) of the degree-d subfield of Q(zeta_m), m prime,
/// d | m - 1, by Gaussian periods.
pub fn gaussian_period_polynomial(m: u64, d: usize) -> Vec<BigInt> {
    assert!((m - 1).is_multiple_of(d as u64));
    let mu = m as usize;
    let order = |a: u64| -> u64 {
        let mut k = 1;
        let mut v = a % m;
        while v != 1 {
            v = v * a % m;
            k += 1;
        }
        k
    };
    let gen = (2..m).find(|&a| order(a) == m - 1).unwrap();
    let f = (mu - 1) / d;
    let mut periods: Vec<Vec<BigInt>> = Vec::new();
    for j in 0..d {
        let mut vec = vec![BigInt::zero(); mu - 1];
        for i in 0..f {
            let e = modpoly::powmod(gen, (j + d * i) as u64, m) as usize;
            if e == mu - 1 {
                for k in 0..mu - 1 {
                    vec[k] -= 1;
                }
            } else {
                vec[e] += 1;
            }
        }
        vec.push(BigInt::zero());
        periods.push(vec);
    }
    let mut poly: Vec<Vec<BigInt>> = vec![{
        let mut one = vec![BigInt::zero(); mu];
        one[0] = BigInt::one();
        one
    }];
    for eta in &periods {
        let neg_eta: Vec<BigInt> = eta.iter().map(|v| -v).collect();
        let mut new = vec![vec![BigInt::zero(); mu]; poly.len() + 1];
        for (i, coef) in poly.iter().enumerate() {
            for k in 0..mu {
                new[i + 1][k] += &coef[k];
            }
            let prod = cyclo_mul(coef, &neg_eta, mu);
            for k in 0..mu - 1 {
                new[i][k] += &prod[k];
            }
        }
        poly = new;
    }
    let mut out = Vec::new();
    for coef in &poly {
        assert!(coef[1..mu - 1].iter().all(|v| v.is_zero()), "period polynomial coefficient not rational");
        out.push(coef[0].clone());
    }
    assert!(out.last().unwrap().is_one());
    out
}

/// Seeded search for monic irreducible g of degree d, coefficients in [-B, B], with p splitting
/// completely; returns the candidate (g, polynomial root discriminant) whose root discriminant
/// is closest to `target` (if given), or None when the search is exhausted.
pub fn random_split_field(d: usize, p: u64, seed: &str, coeff_bound: i64, tries: usize, target_rootdisc: Option<f64>) -> Option<(Vec<BigInt>, f64)> {
    let mut rng = Rng::seeded(&format!("nfield:split:{}:{}:{}", d, p, seed));
    let mut best: Option<(f64, Vec<BigInt>, f64)> = None;
    let mut found = 0;
    for _ in 0..tries {
        let mut g: Vec<BigInt> = (0..d).map(|_| big(rng.range(-coeff_bound, coeff_bound))).collect();
        g.push(BigInt::one());
        if g[0].is_zero() {
            continue;
        }
        let k = NumberField::new(g.clone());
        if k.discriminant().is_zero() || !k.splits_completely(p) {
            continue;
        }
        if is_irreducible_over_q(&g) != Some(true) {
            continue;
        }
        found += 1;
        let rd = k.root_discriminant();
        let key = match target_rootdisc {
            Some(t) => (rd.ln() - t.ln()).abs(),
            None => 0.0,
        };
        if best.as_ref().map(|b| key < b.0).unwrap_or(true) {
            best = Some((key, g.clone(), rd));
        }
        if target_rootdisc.is_none() || found >= 40 {
            break;
        }
    }
    best.map(|(_, g, rd)| (g, rd))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn periods_c13() {
        let expected: Vec<(usize, i64)> = vec![(2, 13), (3, 169), (4, 19773), (6, 371293)];
        for (d, disc) in expected {
            let g = gaussian_period_polynomial(13, d);
            let k = NumberField::new(g);
            assert_eq!(k.discriminant(), big(disc), "d = {}", d);
            assert!(k.splits_completely(8191));
        }
        let k = NumberField::new(gaussian_period_polynomial(13, 12));
        assert_eq!(k.discriminant(), big(13).pow(11));
    }

    #[test]
    fn sqrt_roundtrip_all_shapes() {
        let shapes: Vec<Vec<i64>> = vec![
            vec![-1, -1, 0, 1],
            vec![1, 0, 0, -1, 0, 0, 0, 1],
            vec![-1, 0, 0, 1, 0, 0, 1, -1, 1],
            vec![-1, 1, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1],
            vec![-13, 0, 1],
        ];
        let mut rng = Rng::seeded("sqrt-test");
        for g in shapes {
            let k = NumberField::from_i64(&g);
            for _ in 0..3 {
                let y: Elt = (0..k.d).map(|_| rat_frac(rng.range(-30, 30), rng.choice(&[1, 2, 3, 4]))).collect();
                let a = k.mul(&y, &y);
                let r = k.sqrt(&a, &[]).expect("square has a root");
                assert_eq!(k.mul(&r, &r), a);
                let b = k.add(&a, &k.from_rational(&rat(1)));
                assert!(k.sqrt(&b, &[]).is_none(), "non-square accepted");
            }
        }
    }

    #[test]
    fn inverse_and_reconstruct() {
        let k = NumberField::from_i64(&[-13, 0, 1]);
        let a = k.elt_i64(&[3, 2]);
        let inv = k.inv(&a).unwrap();
        assert_eq!(k.mul(&a, &inv), k.elt_i64(&[1, 0]));
        let m = big(1_000_003).pow(4);
        let r = rat_frac(-7, 12);
        let am = (r.numer() * modinv_big(r.denom(), &m).unwrap()).mod_floor(&m);
        assert_eq!(rational_reconstruct(&am, &m), Some(r));
    }
}
