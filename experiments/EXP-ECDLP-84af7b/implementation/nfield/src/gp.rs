//! Optional PARI/GP cross-checks through FFI (feature `pari`). Every function returns None when
//! the feature is off, so the runners never depend on it; results are recorded as controls with
//! provenance "pari (libpari FFI)".

use num_bigint::BigInt;

#[cfg(feature = "pari")]
mod ffi {
    use std::ffi::{c_char, CStr, CString};
    use std::sync::Once;

    extern "C" {
        fn nfield_pari_init(parisize: usize);
        fn nfield_pari_eval(expr: *const c_char) -> *mut c_char;
        fn nfield_pari_free(s: *mut c_char);
        fn nfield_pari_version() -> *const c_char;
    }

    static INIT: Once = Once::new();

    pub fn init() {
        INIT.call_once(|| unsafe { nfield_pari_init(64_000_000) });
    }

    pub fn version() -> Option<String> {
        init();
        unsafe {
            let p = nfield_pari_version();
            if p.is_null() {
                None
            } else {
                Some(CStr::from_ptr(p).to_string_lossy().into_owned())
            }
        }
    }

    pub fn eval(expr: &str) -> Option<String> {
        init();
        let c = CString::new(expr).ok()?;
        unsafe {
            let p = nfield_pari_eval(c.as_ptr());
            if p.is_null() {
                return None;
            }
            let s = CStr::from_ptr(p).to_string_lossy().into_owned();
            nfield_pari_free(p);
            Some(s)
        }
    }
}

pub fn available() -> bool {
    cfg!(feature = "pari")
}

pub fn version() -> Option<String> {
    #[cfg(feature = "pari")]
    {
        ffi::version().map(|v| format!("libpari {} (FFI)", v))
    }
    #[cfg(not(feature = "pari"))]
    {
        None
    }
}

#[allow(unused_variables)]
pub fn eval(expr: &str) -> Option<String> {
    #[cfg(feature = "pari")]
    {
        ffi::eval(expr)
    }
    #[cfg(not(feature = "pari"))]
    {
        None
    }
}

/// (rank lower bound, rank upper bound) from ellrank for E/Q given [a1, a2, a3, a4, a6].
pub fn ellrank_q(ainvs: &[i64]) -> Option<(i64, i64)> {
    let a = ainvs.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
    let s = eval(&format!("my(E=ellinit([{}]), r=ellrank(E)); [r[1], r[2]]", a))?;
    let inner = s.trim().trim_start_matches('[').trim_end_matches(']');
    let parts: Vec<&str> = inner.split(',').map(|x| x.trim()).collect();
    if parts.len() < 2 {
        return None;
    }
    Some((parts[0].parse().ok()?, parts[1].parse().ok()?))
}

/// Field discriminant of Q[t]/(g), g low -> high integer coefficients.
pub fn nfdisc(g: &[BigInt]) -> Option<BigInt> {
    let poly = g
        .iter()
        .enumerate()
        .filter(|(_, c)| !num_traits::Zero::is_zero(*c))
        .map(|(i, c)| format!("({})*y^{}", c, i))
        .collect::<Vec<_>>()
        .join("+");
    let s = eval(&format!("nfdisc({})", poly))?;
    s.trim().parse::<BigInt>().ok()
}
