//! Polynomials over Z/q for a prime q < 2^62, coefficients low -> high, always trimmed (no
//! trailing zeros; the zero polynomial is the empty vector). Used for roots, distinct-degree and
//! equal-degree factorisation, finite-field square roots and inverses, and the mod-q sieve.

use crate::rng::Rng;
use num_bigint::BigUint;
use num_traits::{One, Zero};

pub type Poly = Vec<u64>;

#[inline]
pub fn mulmod(a: u64, b: u64, q: u64) -> u64 {
    ((a as u128 * b as u128) % q as u128) as u64
}

pub fn powmod(mut a: u64, mut e: u64, q: u64) -> u64 {
    let mut r = 1 % q;
    a %= q;
    while e > 0 {
        if e & 1 == 1 {
            r = mulmod(r, a, q);
        }
        a = mulmod(a, a, q);
        e >>= 1;
    }
    r
}

pub fn invmod(a: u64, q: u64) -> u64 {
    // q prime
    powmod(a, q - 2, q)
}

pub fn trim(a: &mut Poly) {
    while let Some(&0) = a.last() {
        a.pop();
    }
}

pub fn trimmed(mut a: Poly) -> Poly {
    trim(&mut a);
    a
}

pub fn reduce_coeffs(a: &[i64], q: u64) -> Poly {
    trimmed(a.iter().map(|&c| c.rem_euclid(q as i64) as u64).collect())
}

pub fn deg(a: &Poly) -> isize {
    a.len() as isize - 1
}

pub fn add(a: &Poly, b: &Poly, q: u64) -> Poly {
    let n = a.len().max(b.len());
    let mut r = vec![0u64; n];
    for i in 0..n {
        let x = if i < a.len() { a[i] } else { 0 };
        let y = if i < b.len() { b[i] } else { 0 };
        r[i] = (x + y) % q;
    }
    trimmed(r)
}

pub fn sub(a: &Poly, b: &Poly, q: u64) -> Poly {
    let n = a.len().max(b.len());
    let mut r = vec![0u64; n];
    for i in 0..n {
        let x = if i < a.len() { a[i] } else { 0 };
        let y = if i < b.len() { b[i] } else { 0 };
        r[i] = (x + q - y) % q;
    }
    trimmed(r)
}

pub fn sub_const(a: &Poly, c: u64, q: u64) -> Poly {
    let mut r = a.clone();
    if r.is_empty() {
        r.push(0);
    }
    r[0] = (r[0] + q - c % q) % q;
    trimmed(r)
}

/// Remainder of a modulo the monic polynomial m.
pub fn rem(a: &Poly, m: &Poly, q: u64) -> Poly {
    debug_assert!(*m.last().unwrap() == 1);
    let dm = m.len() - 1;
    let mut a = a.clone();
    if dm == 0 {
        return Vec::new();
    }
    let mut i = a.len();
    while i > dm {
        i -= 1;
        let c = a[i];
        if c != 0 {
            for j in 0..=dm {
                let t = mulmod(c, m[j], q);
                a[i - dm + j] = (a[i - dm + j] + q - t) % q;
            }
        }
    }
    a.truncate(dm);
    trimmed(a)
}

pub fn mul(a: &Poly, b: &Poly, m: &Poly, q: u64) -> Poly {
    if a.is_empty() || b.is_empty() {
        return Vec::new();
    }
    let mut r = vec![0u64; a.len() + b.len() - 1];
    for (i, &ai) in a.iter().enumerate() {
        if ai == 0 {
            continue;
        }
        for (j, &bj) in b.iter().enumerate() {
            if bj != 0 {
                r[i + j] = (r[i + j] + mulmod(ai, bj, q)) % q;
            }
        }
    }
    rem(&r, m, q)
}

/// Plain product (no modulus), coefficients mod q.
pub fn mul_plain(a: &Poly, b: &Poly, q: u64) -> Poly {
    if a.is_empty() || b.is_empty() {
        return Vec::new();
    }
    let mut r = vec![0u64; a.len() + b.len() - 1];
    for (i, &ai) in a.iter().enumerate() {
        for (j, &bj) in b.iter().enumerate() {
            r[i + j] = (r[i + j] + mulmod(ai, bj, q)) % q;
        }
    }
    trimmed(r)
}

pub fn pow(a: &Poly, e: &BigUint, m: &Poly, q: u64) -> Poly {
    let mut r: Poly = vec![1 % q];
    r = rem(&r, m, q);
    let mut base = rem(a, m, q);
    let bits = e.bits();
    for i in 0..bits {
        if e.bit(i) {
            r = mul(&r, &base, m, q);
        }
        if i + 1 < bits {
            base = mul(&base, &base, m, q);
        }
    }
    r
}

pub fn pow_u64(a: &Poly, e: u64, m: &Poly, q: u64) -> Poly {
    pow(a, &BigUint::from(e), m, q)
}

/// (quotient, remainder) of a by b (b nonzero), both trimmed.
pub fn divmod(a: &Poly, b: &Poly, q: u64) -> (Poly, Poly) {
    assert!(!b.is_empty());
    let inv = invmod(*b.last().unwrap(), q);
    let mut r = a.clone();
    let mut quo = vec![0u64; if a.len() >= b.len() { a.len() - b.len() + 1 } else { 0 }];
    while r.len() >= b.len() && !r.is_empty() {
        let c = mulmod(*r.last().unwrap(), inv, q);
        let k = r.len() - b.len();
        quo[k] = c;
        for j in 0..b.len() {
            let t = mulmod(c, b[j], q);
            r[k + j] = (r[k + j] + q - t) % q;
        }
        trim(&mut r);
    }
    (trimmed(quo), r)
}

pub fn monic(a: &Poly, q: u64) -> Poly {
    if a.is_empty() {
        return a.clone();
    }
    let inv = invmod(*a.last().unwrap(), q);
    a.iter().map(|&c| mulmod(c, inv, q)).collect()
}

pub fn gcd(a: &Poly, b: &Poly, q: u64) -> Poly {
    let mut a = a.clone();
    let mut b = b.clone();
    while !b.is_empty() {
        let (_, r) = divmod(&a, &b, q);
        a = b;
        b = r;
    }
    monic(&a, q)
}

pub fn derivative(a: &Poly, q: u64) -> Poly {
    let mut r = Vec::new();
    for i in 1..a.len() {
        r.push(mulmod(a[i], i as u64 % q, q));
    }
    trimmed(r)
}

pub fn eval(a: &Poly, x: u64, q: u64) -> u64 {
    let mut v = 0u64;
    for &c in a.iter().rev() {
        v = (mulmod(v, x, q) + c) % q;
    }
    v
}

fn x_poly() -> Poly {
    vec![0, 1]
}

/// All distinct roots of g in F_q (Cantor-Zassenhaus on the linear part), sorted.
pub fn roots(g: &[u64], q: u64) -> Vec<u64> {
    let g = monic(&trimmed(g.iter().map(|&c| c % q).collect()), q);
    if g.len() <= 1 {
        return Vec::new();
    }
    if q == 2 {
        return (0..2).filter(|&r| eval(&g, r, q) == 0).collect();
    }
    let xq = pow_u64(&x_poly(), q, &g, q);
    let h = gcd(&sub(&xq, &x_poly(), q), &g, q);
    let mut out = Vec::new();
    let mut rng = Rng::seeded("modpoly-roots");
    split_roots(&h, q, &mut rng, &mut out);
    out.sort_unstable();
    out.dedup();
    out
}

fn split_roots(h: &Poly, q: u64, rng: &mut Rng, out: &mut Vec<u64>) {
    let d = deg(h);
    if d <= 0 {
        return;
    }
    if d == 1 {
        out.push(mulmod(q - h[0], invmod(h[1], q), q) % q);
        return;
    }
    loop {
        let a: Poly = vec![rng.below(q), 1];
        let t = pow_u64(&a, (q - 1) / 2, h, q);
        let d1 = gcd(&sub_const(&t, 1, q), h, q);
        let dd = deg(&d1);
        if dd > 0 && dd < d {
            split_roots(&d1, q, rng, out);
            let (quo, _) = divmod(h, &d1, q);
            split_roots(&monic(&quo, q), q, rng, out);
            return;
        }
    }
}

/// Distinct-degree factorisation pattern of squarefree g mod q: (degree, count) pairs; None if g
/// is not squarefree mod q.
pub fn ddf_pattern(g: &[u64], q: u64) -> Option<Vec<(usize, usize)>> {
    let f = monic(&trimmed(g.iter().map(|&c| c % q).collect()), q);
    if deg(&gcd(&f, &derivative(&f, q), q)) > 0 {
        return None;
    }
    let mut f = f;
    let mut out = Vec::new();
    let mut h = x_poly();
    let mut i = 1usize;
    while f.len() > 2 * i {
        h = pow_u64(&h, q, &f, q);
        let gi = gcd(&sub(&h, &x_poly(), q), &f, q);
        if deg(&gi) > 0 {
            out.push((i, (gi.len() - 1) / i));
            f = monic(&divmod(&f, &gi, q).0, q);
            h = rem(&h, &f, q);
        }
        i += 1;
    }
    if f.len() > 1 {
        out.push((f.len() - 1, 1));
    }
    Some(out)
}

/// Monic irreducible factors of squarefree g mod q (q odd), as (factor, degree), sorted by
/// (degree, coefficients). None if g is not squarefree mod q.
pub fn factor(g: &[u64], q: u64) -> Option<Vec<(Poly, usize)>> {
    let f = monic(&trimmed(g.iter().map(|&c| c % q).collect()), q);
    if deg(&gcd(&f, &derivative(&f, q), q)) > 0 {
        return None;
    }
    let mut f = f;
    let mut pieces: Vec<(Poly, usize)> = Vec::new();
    let mut h = x_poly();
    let mut i = 1usize;
    while f.len() > 2 * i {
        h = pow_u64(&h, q, &f, q);
        let gi = gcd(&sub(&h, &x_poly(), q), &f, q);
        if deg(&gi) > 0 {
            pieces.push((gi.clone(), i));
            f = monic(&divmod(&f, &gi, q).0, q);
            h = rem(&h, &f, q);
        }
        i += 1;
    }
    if f.len() > 1 {
        let e = f.len() - 1;
        pieces.push((f, e));
    }
    let mut out = Vec::new();
    let mut rng = Rng::seeded("modpoly-edf");
    for (piece, e) in pieces {
        edf(&piece, e, q, &mut rng, &mut out);
    }
    out.sort();
    Some(out)
}

fn edf(h: &Poly, e: usize, q: u64, rng: &mut Rng, out: &mut Vec<(Poly, usize)>) {
    let d = h.len() - 1;
    if d == e {
        out.push((h.clone(), e));
        return;
    }
    let exp = (BigUint::from(q).pow(e as u32) - BigUint::one()) / BigUint::from(2u32);
    loop {
        let a: Poly = trimmed((0..d).map(|_| rng.below(q)).collect());
        if a.is_empty() {
            continue;
        }
        let t = pow(&a, &exp, h, q);
        let d1 = gcd(&sub_const(&t, 1, q), h, q);
        let dd = deg(&d1) as usize;
        if dd > 0 && dd < d {
            edf(&d1, e, q, rng, out);
            let (quo, _) = divmod(h, &d1, q);
            edf(&monic(&quo, q), e, q, rng, out);
            return;
        }
    }
}

/// Inverse in F_q[t]/(h), h irreducible of degree e: a^(q^e - 2).
pub fn ff_inverse(a: &Poly, h: &Poly, e: usize, q: u64) -> Poly {
    let exp = BigUint::from(q).pow(e as u32) - BigUint::from(2u32);
    pow(a, &exp, h, q)
}

/// Square root of a (nonzero) in F_q[t]/(h), h irreducible of degree e, q odd, by Tonelli-Shanks
/// in the cyclic group of order q^e - 1; None if a is a non-residue.
pub fn ff_sqrt(a: &Poly, h: &Poly, e: usize, q: u64, rng: &mut Rng) -> Option<Poly> {
    let n = BigUint::from(q).pow(e as u32) - BigUint::one();
    let one: Poly = vec![1];
    let half = &n / BigUint::from(2u32);
    if pow(a, &half, h, q) != one {
        return None;
    }
    let mut qq = n.clone();
    let mut s = 0u32;
    while (&qq % BigUint::from(2u32)).is_zero() {
        qq /= BigUint::from(2u32);
        s += 1;
    }
    if s == 1 {
        let exp = (&qq + BigUint::one()) / BigUint::from(2u32);
        return Some(pow(a, &exp, h, q));
    }
    let z = loop {
        let z: Poly = trimmed((0..e).map(|_| rng.below(q)).collect());
        if !z.is_empty() && pow(&z, &half, h, q) != one {
            break z;
        }
    };
    let mut m = s;
    let mut c = pow(&z, &qq, h, q);
    let mut t = pow(a, &qq, h, q);
    let exp = (&qq + BigUint::one()) / BigUint::from(2u32);
    let mut r = pow(a, &exp, h, q);
    while t != one {
        let mut i = 0u32;
        let mut tt = t.clone();
        while tt != one {
            tt = mul(&tt, &tt, h, q);
            i += 1;
        }
        let b = pow(&c, &(BigUint::one() << (m - i - 1)), h, q);
        m = i;
        c = mul(&b, &b, h, q);
        t = mul(&t, &c, h, q);
        r = mul(&r, &b, h, q);
    }
    Some(r)
}

/// y mod (q, g) with y = parts[j] mod factors[j]: sum_j parts[j] * M_j * (M_j^-1 mod h_j).
pub fn crt(parts: &[Poly], factors: &[(Poly, usize)], g: &Poly, q: u64) -> Poly {
    let mut y: Poly = Vec::new();
    for ((h, e), part) in factors.iter().zip(parts) {
        let (m, _) = divmod(g, h, q);
        let minv = ff_inverse(&rem(&m, h, q), h, *e, q);
        let term = mul(&mul(part, &minv, h, q), &m, g, q);
        y = add(&y, &term, q);
    }
    y
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roots_and_factor_agree() {
        let g: Vec<u64> = reduce_coeffs(&[-13, 0, 1], 1000003);
        let q = 1000003u64;
        let r = roots(&g, q);
        assert_eq!(r.len(), 2);
        for &x in &r {
            assert_eq!((mulmod(x, x, q) + q - 13) % q, 0);
        }
        let fac = factor(&g, q).unwrap();
        assert_eq!(fac.len(), 2);
        let g7: Vec<u64> = reduce_coeffs(&[1, 0, 0, -1, 0, 0, 0, 1], 1000099);
        let fac = factor(&g7, 1000099).unwrap();
        let degs: usize = fac.iter().map(|(_, e)| e).sum();
        assert_eq!(degs, 7);
        let mut prod: Poly = vec![1];
        for (h, _) in &fac {
            prod = mul_plain(&prod, h, 1000099);
        }
        assert_eq!(prod, g7);
    }

    #[test]
    fn ff_sqrt_roundtrip() {
        let q = 1000099u64;
        let g7: Vec<u64> = reduce_coeffs(&[1, 0, 0, -1, 0, 0, 0, 1], 1000099);
        let fac = factor(&g7, q).unwrap();
        let (h, e) = fac[0].clone();
        let mut rng = Rng::seeded("t");
        for _ in 0..5 {
            let y: Poly = trimmed((0..e).map(|_| rng.below(q)).collect());
            let a = mul(&y, &y, &h, q);
            let s = ff_sqrt(&a, &h, e, q, &mut rng).expect("square");
            assert_eq!(mul(&s, &s, &h, q), a);
        }
    }
}
