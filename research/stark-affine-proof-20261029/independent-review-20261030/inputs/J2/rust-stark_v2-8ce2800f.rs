//! **STARK v2**: a scalable transparent argument of knowledge with
//! a coset low-degree extension, a composition polynomial that
//! encodes the AIR, a DEEP out-of-domain sample (DEEP-ALI), and
//! degree-bounded FRI on the DEEP quotient.
//!
//! **Educational and unaudited.  Not zero-knowledge (no masking: the
//! opened trace-LDE values and the out-of-domain values `f(z)`, `f(ω·z)`
//! leak information about the witness), no grinding, no proven
//! soundness bound.  It must not back a research claim.**
//!
//! 1. **Coset LDE.**  The trace polynomial `f(X)`, interpolated on
//!    `H_trace = ⟨ω⟩` of size `n`, is evaluated on the coset
//!    `g · H_lde` of size `L = n · β` (`β` = blow-up, a power of two
//!    `≥ 2`; `g = 7` generates `F_r*`, so the coset misses `H_trace`).
//!    Because `ω = ω_L^β`, `f(ω·x)` sits `β` positions after `f(x)`.
//!
//! 2. **Composition polynomial**, evaluated pointwise on the coset:
//!
//!    ```text
//!    Comp(x) = α₁ · C(f(x), f(ω·x)) / Z(x)  +  Σ_k α₂^k · (f(x) − v_k) / (x − ω^{p_k})
//!    Z(x)    = (xⁿ − 1) / (x − ω^{n−1})
//!    ```
//!
//!    For a valid trace and a transition `C` of degree 1 in the trace
//!    values, `Comp` is a polynomial of degree `< n`; if a transition
//!    or a boundary fails, the division leaves a non-polynomial and
//!    `Comp` is far from every degree-`< n` polynomial — unless the
//!    poles cancel, which is why `α₁, α₂` must be drawn only after the
//!    statement (the `v_k`) is fixed.
//!
//! 3. **Out-of-domain (DEEP) sample.**  After the trace and composition
//!    commitments the transcript draws `z`, redrawing while `z ∈ H_trace`
//!    or `z ∈ g · H_lde` ([`ood_point_ok`]); then `ω·z` is outside both
//!    too.  The prover sends `f(z)`, `f(ω·z)` and `Comp(z)`, which the
//!    transcript absorbs before any further challenge, and the verifier
//!    checks the AIR at `z`: `Comp(z)` must equal item 2's formula
//!    evaluated on `f(z)`, `f(ω·z)`.
//!
//! 4. **DEEP quotient.**  With fresh coefficients `γ₁, γ₂, γ₃, λ₀, λ₁`
//!    drawn after the OOD values,
//!
//!    ```text
//!    D(x) = (λ₀ + λ₁·x) · [ γ₁·(f(x) − f(z))/(x − z)
//!                          + γ₂·(f(ω·x) − f(ω·z))/(x − z)
//!                          + γ₃·(Comp(x) − Comp(z))/(x − z) ]
//!    ```
//!
//!    Each quotient is a polynomial of degree `< n − 1` exactly when the
//!    claimed value is the committed polynomial's value at that point;
//!    a wrong claim leaves a pole and a function far from low degree.
//!    The factor `(λ₀ + λ₁·x)` is the degree adjustment: it lifts the
//!    bound `< n − 1` to the `< n` that FRI tests, so a bracket of
//!    degree `n − 1` (e.g. a committed trace polynomial of degree `n`)
//!    fails FRI.
//!
//! 5. **Degree-bounded FRI** folds `D`'s evaluations `log₂ n` times to
//!    a final layer of `β` values, which must be constant.
//!
//! **Transcript (Fiat-Shamir).**  It absorbs, in order: a
//! domain-separation tag; the whole statement — an AIR identifier
//! ([`air_fingerprint`]), `n`, `β`, `q`, the FRI fold count `log₂ n`
//! and final-layer size `β`, and every boundary `(p_k, v_k)`
//! ([`statement_transcript`]); the trace commitment; then draws `α₁`,
//! `α₂`; absorbs the composition commitment; draws `z`; absorbs
//! `f(z)`, `f(ω·z)`, `Comp(z)`; draws `γ₁, γ₂, γ₃, λ₀, λ₁`; absorbs each
//! FRI layer root (layer 0 commits to `D`) before its folding
//! challenge; the last layer root and the final constant; and only
//! then draws the `q` query positions.  A prover therefore cannot pick
//! a public input after seeing `α₁, α₂` (the "frozen heart" forgery of
//! the 2026-10-17 sheriff re-audit), nor an OOD value after seeing the
//! DEEP coefficients or the queries.
//!
//! The verifier takes `β`, `q` and the FRI depth from its own
//! [`StarkConfig`], never from the proof, and rejects a proof whose
//! query count, layer count or final layer differs.  It draws `z`
//! itself, rejects non-canonical OOD values, and checks the AIR at `z`.
//! At each position it opens `f(x)`, `f(ω·x)` and `Comp(x)` (each Merkle
//! path bound to its position, each value a canonical field element
//! `< r`), recomputes `Comp(x)` from the AIR (a check beyond standard
//! DEEP-ALI, kept from the pre-DEEP construction), recomputes `D(x)`
//! from `f(x)`, `Comp(x)` and the OOD values, checks that FRI's first
//! layer holds that value, and checks the folding down to the
//! committed constant final layer.  Malformed input returns `false`;
//! it never panics.
//!
//! **Soundness: no security level is claimed for this code.**  The
//! usual *conjectured* analysis of a DEEP-ALI STARK (ethSTARK; DEEP-FRI,
//! Ben-Sasson, Goldberg, Kopparty and Saraf 2019) assumes the
//! Reed–Solomon proximity conjecture (FRI and random linear
//! combinations stay sound up to the list-decoding radius for rate `ρ`)
//! and Fiat–Shamir in the random-oracle model.  Under those
//! assumptions it bounds the soundness error of one proof by roughly
//!
//! ```text
//! ε  ≲  ρ^q · 2^(−g)  +  ε_field  +  ε_hash,                    ρ = 1/β (code rate)
//! ε_field  ≲  (k + 1)/r                       α₁, α₂ (ALI combination)
//!          +  (2n + k)/(r − n − L)            z hits a root of a false AIR identity
//!          +  (5 + log₂ n) · L/r              γ's, λ's and the FRI folds (conjectured)
//! ```
//!
//! with `q` queries, `g` grinding bits and `k` boundary constraints.
//! Here `g = 0`, so the conjectured query term is `β^(−q)` (`8^(−80) =
//! 2^(−240)` for [`StarkConfig::default`], `4^(−20) = 2^(−40)` for
//! [`StarkConfig::fast`]).  `F_r` is the BLS12-381 scalar field (`r ≈
//! 2^254.86`, no extension field), so for any trace this code can
//! build (`L ≤ 2^32`) `ε_field` is below about `2^(−215)`.  `ε_hash`:
//! every commitment is a SHA-256 Merkle tree, and a SHA-256 collision
//! (generic cost about `2^128`) lets a prover open one leaf two ways,
//! so nothing above 128 bits can hold whatever `q` and `β` are; a
//! prover making `T` hash queries also gains a factor of about `T`
//! through Fiat–Shamir.  Proven (non-conjectural) FRI bounds are weaker
//! than the conjectured query term; this module does not state one.
//! [`AffineTransition`] fixes total degree at most one in the trace
//! values; this degree restriction is part of the API rather than a caller
//! supplied promise.
//!
//! ## API
//!
//! - [`AirV2`]: boundary constraints and an explicit affine transition
//!   on adjacent trace rows.  The transition degree is fixed by its type.
//! - [`StarkConfig`]: `(blow_up, query_count)`.
//! - [`prove`] / [`verify`]; [`OodValues`] are the out-of-domain claims
//!   carried by [`StarkProofV2`].

use super::merkle::{MerkleProof, MerkleTree};
use super::polynomial::{fr_add, fr_inv, fr_mul, fr_sub, Poly};
use super::stark::{
    absorb_scalar, absorb_u64, draw_challenge, fri_check, fri_commit_to, fri_query,
    fri_transcript_after, opening_ok, probe_point, query_positions, reduced_bytes, FriCommitment,
    FriQueryOpening, FriReject,
};
use crate::bls12_381::fq::scalar_modulus;
use num_bigint::BigUint;
use num_traits::One;
use std::sync::Arc;

/// Transcript domain-separation tag.  The `statement-bound` suffix marks
/// the transcript that absorbs the statement before any challenge; `v3`
/// and `deep` mark the one with the out-of-domain sample.
const FS_TAG: &str = "ZK-STARK-V2/v3/statement-bound-deep";

/// Number of fixed pseudo-random points (beyond `(0,0)`, `(1,0)`,
/// `(0,1)`) at which [`air_fingerprint`] evaluates a transition.
const AIR_PROBES: u64 = 2;

/// Configuration: blow-up factor and number of FRI queries.  The
/// verifier's copy is authoritative: proofs made with another
/// configuration are rejected.
#[derive(Clone, Debug)]
pub struct StarkConfig {
    pub blow_up: usize,
    pub query_count: usize,
}

impl StarkConfig {
    /// Default: `blow_up = 8`, `query_count = 80`.  Conjectured query
    /// term `8^(−80)` (module docs, "Soundness"); that is not a
    /// security level for this code, which claims none.
    #[allow(clippy::should_implement_trait)]
    pub fn default() -> Self {
        Self {
            blow_up: 8,
            query_count: 80,
        }
    }
    /// Faster: `blow_up = 4`, `query_count = 20`, conjectured query
    /// term `4^(−20)`.  Good for tests.
    pub fn fast() -> Self {
        Self {
            blow_up: 4,
            query_count: 20,
        }
    }
}

/// An affine adjacent-row constraint `a·prev + b·next + c` over the scalar
/// field.  Its representation fixes the total degree at most one; callers
/// cannot supply an arbitrary transition closure with a hidden higher degree.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct AffineTransition {
    previous: BigUint,
    next: BigUint,
    constant: BigUint,
}

impl AffineTransition {
    /// Coefficients are reduced to canonical scalar-field representatives.
    pub fn new(previous: BigUint, next: BigUint, constant: BigUint) -> Self {
        let modulus = scalar_modulus();
        Self {
            previous: previous % &modulus,
            next: next % &modulus,
            constant: constant % &modulus,
        }
    }

    /// Evaluate the complete transition constraint in the scalar field.
    pub fn evaluate(&self, previous: &BigUint, next: &BigUint) -> BigUint {
        fr_add(
            &fr_add(&fr_mul(&self.previous, previous), &fr_mul(&self.next, next)),
            &self.constant,
        )
    }
}

/// An AIR with boundary constraints and an affine transition operating on
/// adjacent trace rows (`f(X), f(ω·X)`).
#[derive(Clone)]
pub struct AirV2 {
    /// Number of trace rows.  Must be a power of 2.
    pub n: usize,
    /// Boundary constraints: `(position, expected_value)` pairs.
    /// Each `position` is in `[0, n)`.
    pub boundary: Vec<(usize, BigUint)>,
    /// Degree-at-most-one constraint on consecutive trace values.  It must
    /// evaluate to zero on valid adjacent rows.
    pub transition: AffineTransition,
    /// Generator of the trace (the prover's actual computation).
    pub generate_trace: Arc<dyn Fn() -> Vec<BigUint> + Send + Sync>,
}

impl AirV2 {
    /// **Doubling AIR**: trace[i+1] = 2·trace[i], starting from `start`.
    /// Boundary: `trace[0] = start`.
    pub fn doubling(n: usize, start: u64) -> Self {
        let s = start;
        let s_for_gen = s;
        let gen = move || -> Vec<BigUint> {
            let mut t = Vec::with_capacity(n);
            t.push(BigUint::from(s_for_gen));
            for i in 1..n {
                t.push(fr_mul(&t[i - 1], &BigUint::from(2u32)));
            }
            t
        };
        // Constraint: next − 2·prev = 0.
        let transition = AffineTransition::new(
            fr_sub(&BigUint::from(0u32), &BigUint::from(2u32)),
            BigUint::one(),
            BigUint::from(0u32),
        );
        let generate_trace = Arc::new(gen);
        let boundary = vec![(0, BigUint::from(s))];
        Self {
            n,
            boundary,
            transition,
            generate_trace,
        }
    }
}

// ── Domain helpers ────────────────────────────────────────────────

/// Build the multiplicative subgroup of size `n` (`n` must be a
/// power of 2 dividing 2³²).
fn subgroup(n: usize) -> Vec<BigUint> {
    let omega = super::plonk::primitive_nth_root(n);
    let mut out = Vec::with_capacity(n);
    let mut acc = BigUint::one();
    for _ in 0..n {
        out.push(acc.clone());
        acc = fr_mul(&acc, &omega);
    }
    out
}

/// `g · H` where `g` is a non-trivial coset shift.  We use
/// `g = 7` (multiplicative generator of F_r*) to ensure the coset
/// is disjoint from the trace domain.
fn coset(n: usize, shift: &BigUint) -> Vec<BigUint> {
    subgroup(n).into_iter().map(|x| fr_mul(&x, shift)).collect()
}

fn coset_shift() -> BigUint {
    BigUint::from(7u32)
}

// ── Polynomial evaluation on subgroups ─────────────────────────────

/// Naive O(n²) DFT: evaluate polynomial `p` on the domain `dom`.
#[cfg(test)]
fn eval_on_domain(p: &Poly, dom: &[BigUint]) -> Vec<BigUint> {
    dom.iter().map(|x| p.evaluate(x)).collect()
}

/// Naive interpolation: given evaluations of a polynomial of degree
/// `< n` on a multiplicative subgroup of size `n`, recover the
/// polynomial.  Uses Lagrange via [`Poly::interpolate`].
fn interpolate_from_subgroup(dom: &[BigUint], evals: &[BigUint]) -> Poly {
    let pts: Vec<(BigUint, BigUint)> = dom
        .iter()
        .zip(evals)
        .map(|(d, e)| (d.clone(), e.clone()))
        .collect();
    Poly::interpolate(&pts)
}

// ── Composition polynomial ─────────────────────────────────────────

/// `xⁿ` by repeated squaring (`n` is a power of two).
fn pow_pow2(x: &BigUint, n: usize) -> BigUint {
    let mut xn = x.clone();
    let mut k = 1;
    while k < n {
        xn = fr_mul(&xn, &xn);
        k *= 2;
    }
    xn
}

/// `Comp(x)` from the trace values `f(x)`, `f(ω·x)` at one point
/// (module docs, item 2).  Prover and verifier call the same function,
/// on the coset and at the out-of-domain point `z`.  `None` if `x` is a
/// pole (a point of `H_trace`); the coset and `z` never are.
fn composition_at(
    air: &AirV2,
    h_trace: &[BigUint],
    x: &BigUint,
    fx: &BigUint,
    f_wx: &BigUint,
    alpha1: &BigUint,
    alpha2: &BigUint,
) -> Option<BigUint> {
    let n = air.n;
    // Z(x) = (xⁿ − 1) / (x − ω^{n−1}).
    let z = fr_mul(
        &fr_sub(&pow_pow2(x, n), &BigUint::one()),
        &fr_inv(&fr_sub(x, &h_trace[n - 1]))?,
    );
    let transition = fr_mul(&air.transition.evaluate(fx, f_wx), &fr_inv(&z)?);
    let mut acc = fr_mul(alpha1, &transition);
    let mut alpha2_pow = BigUint::one();
    for (pos, val) in &air.boundary {
        let term = fr_mul(&fr_sub(fx, val), &fr_inv(&fr_sub(x, h_trace.get(*pos)?))?);
        acc = fr_add(&acc, &fr_mul(&alpha2_pow, &term));
        alpha2_pow = fr_mul(&alpha2_pow, alpha2);
    }
    Some(acc)
}

/// **AIR identifier**: the transition evaluated (mod `r`) at `(0,0)`,
/// `(1,0)`, `(0,1)` and [`AIR_PROBES`] fixed public points
/// `H("ZK-STARK-V2/air-probe" ‖ j)`.  A transition of degree `≤ 1`
/// (the only kind this module supports) is determined exactly by its
/// first three values.  Higher-degree transitions are not representable by
/// [`AffineTransition`].
pub fn air_fingerprint(air: &AirV2) -> Vec<u8> {
    let (zero, one) = (BigUint::from(0u32), BigUint::one());
    let mut points = vec![
        (zero.clone(), zero.clone()),
        (one.clone(), zero.clone()),
        (zero, one),
    ];
    points.extend((0..AIR_PROBES).map(|j| {
        (
            probe_point("ZK-STARK-V2/air-probe", 2 * j),
            probe_point("ZK-STARK-V2/air-probe", 2 * j + 1),
        )
    }));
    let mut out = b"air:v2-adjacent-row-transition".to_vec();
    for (a, b) in &points {
        out.extend_from_slice(&reduced_bytes(&air.transition.evaluate(a, b)));
    }
    out
}

/// The Fiat-Shamir transcript state before the trace commitment: tag,
/// AIR identifier, `n`, `β`, `q`, FRI fold count and final-layer size,
/// and every boundary `(position, value)`.  `None` if the configuration
/// is invalid, a boundary position is `≥ n`, or a boundary value is not
/// canonical (`≥ r`).
pub fn statement_transcript(air: &AirV2, config: &StarkConfig) -> Option<Vec<u8>> {
    let (n, beta, q) = (air.n, config.blow_up, config.query_count);
    if !n.is_power_of_two() || n < 2 || !beta.is_power_of_two() || beta < 2 || q == 0 {
        return None;
    }
    let mut t = FS_TAG.as_bytes().to_vec();
    t.extend_from_slice(&air_fingerprint(air));
    absorb_u64(&mut t, b"n", n as u64);
    absorb_u64(&mut t, b"blow_up", beta as u64);
    absorb_u64(&mut t, b"q", q as u64);
    absorb_u64(&mut t, b"fri_folds", n.trailing_zeros() as u64);
    absorb_u64(&mut t, b"fri_final_size", beta as u64);
    absorb_u64(&mut t, b"boundaries", air.boundary.len() as u64);
    for (pos, val) in &air.boundary {
        if *pos >= n {
            return None;
        }
        absorb_u64(&mut t, b"p", *pos as u64);
        if !absorb_scalar(&mut t, val) {
            return None;
        }
    }
    t.extend_from_slice(b"trace_commit");
    Some(t)
}

/// Absorb the trace commitment and draw `(α₁, α₂)`.
fn absorb_trace_draw_alphas(t: &mut Vec<u8>, trace_commit: &[u8; 32]) -> (BigUint, BigUint) {
    t.extend_from_slice(trace_commit);
    let alpha1 = draw_challenge(t);
    let alpha2 = draw_challenge(t);
    t.extend_from_slice(b"composition_commit");
    (alpha1, alpha2)
}

// ── DEEP: out-of-domain sample and quotient ────────────────────────

/// Is `z` usable as the out-of-domain point: outside the trace domain
/// `H_trace` (`zⁿ ≠ 1`) and outside the LDE coset `g · H_lde`
/// (`(z/g)^L ≠ 1`)?  Then `ω·z` is outside both as well (`ω ∈ H_trace
/// ⊂ H_lde`), so neither `x − z` nor `x − ω·z` vanishes on the coset and
/// `Comp(z)` has no pole.
pub fn ood_point_ok(z: &BigUint, n: usize, lde_size: usize) -> bool {
    let Some(g_inv) = fr_inv(&coset_shift()) else {
        return false;
    };
    pow_pow2(z, n) != BigUint::one() && pow_pow2(&fr_mul(z, &g_inv), lde_size) != BigUint::one()
}

/// Draw challenges until one passes `accept` (rejection sampling; a
/// rejected draw stays in the transcript, so prover and verifier redraw
/// identically).
fn draw_accepted(t: &mut Vec<u8>, accept: impl Fn(&BigUint) -> bool) -> BigUint {
    loop {
        let z = draw_challenge(t);
        if accept(&z) {
            return z;
        }
    }
}

/// Absorb the composition commitment and draw the out-of-domain point
/// `z`, redrawn while it lies in `H_trace` or the LDE coset.
fn absorb_composition_draw_z(
    t: &mut Vec<u8>,
    composition_commit: &[u8; 32],
    n: usize,
    lde_size: usize,
) -> BigUint {
    t.extend_from_slice(composition_commit);
    t.extend_from_slice(b"ood_point");
    draw_accepted(t, |z| ood_point_ok(z, n, lde_size))
}

/// The prover's out-of-domain claims: `f(z)`, `f(ω·z)` and `Comp(z)`.
#[derive(Clone, Debug)]
pub struct OodValues {
    pub f_z: BigUint,
    pub f_wz: BigUint,
    pub comp_z: BigUint,
}

/// The DEEP combination coefficients: `γ₁, γ₂, γ₃` for the three
/// quotients and `(λ₀, λ₁)` for the degree adjustment.
struct DeepCoeffs {
    gamma: [BigUint; 3],
    lambda: [BigUint; 2],
}

/// Draw the DEEP coefficients (after the OOD values).
fn draw_deep_coeffs(t: &mut Vec<u8>) -> DeepCoeffs {
    t.extend_from_slice(b"deep_coeffs");
    let gamma = [draw_challenge(t), draw_challenge(t), draw_challenge(t)];
    let lambda = [draw_challenge(t), draw_challenge(t)];
    t.extend_from_slice(b"deep_fri");
    DeepCoeffs { gamma, lambda }
}

/// Absorb the OOD values (each canonical, else `None`) and draw the
/// DEEP coefficients.
fn absorb_ood_draw_deep(t: &mut Vec<u8>, ood: &OodValues) -> Option<DeepCoeffs> {
    t.extend_from_slice(b"ood_values");
    for v in [&ood.f_z, &ood.f_wz, &ood.comp_z] {
        if !absorb_scalar(t, v) {
            return None;
        }
    }
    Some(draw_deep_coeffs(t))
}

/// The DEEP quotient combination at `x` (module docs, item 4), from
/// `f(x)`, `f(ω·x)` and `Comp(x)`.
///
/// ```text
/// D(x) = (λ₀ + λ₁·x) · [ γ₁·(f(x) − f(z))/(x − z)
///                       + γ₂·(f(ωx) − f(ωz))/(x − z)
///                       + γ₃·(Comp(x) − Comp(z))/(x − z) ]
/// ```
///
/// `None` if `x = z`.
fn deep_at(
    x: &BigUint,
    fx: &BigUint,
    f_wx: &BigUint,
    comp_x: &BigUint,
    z: &BigUint,
    ood: &OodValues,
    c: &DeepCoeffs,
) -> Option<BigUint> {
    let inv_xz = fr_inv(&fr_sub(x, z))?;
    let q_f = fr_mul(&fr_sub(fx, &ood.f_z), &inv_xz);
    let q_fw = fr_mul(&fr_sub(f_wx, &ood.f_wz), &inv_xz);
    let q_c = fr_mul(&fr_sub(comp_x, &ood.comp_z), &inv_xz);
    let sum = fr_add(
        &fr_add(&fr_mul(&c.gamma[0], &q_f), &fr_mul(&c.gamma[1], &q_fw)),
        &fr_mul(&c.gamma[2], &q_c),
    );
    let adjust = fr_add(&c.lambda[0], &fr_mul(&c.lambda[1], x));
    Some(fr_mul(&adjust, &sum))
}

// ── Prover / Verifier ──────────────────────────────────────────────

#[derive(Clone, Debug)]
pub struct StarkProofV2 {
    pub trace_commit: [u8; 32],
    pub composition_commit: [u8; 32],
    /// `f(z)`, `f(ω·z)`, `Comp(z)` at the out-of-domain point `z`.
    pub ood: OodValues,
    /// FRI on the DEEP combination `D` (its layer 0 commits to `D` on
    /// the coset).
    pub fri: FriCommitment,
    /// Per-query openings on the trace and composition LDE tables:
    /// `f(x)`, `f(ω·x)` (position `+ β`) and `Comp(x)`.
    pub trace_openings: Vec<(usize, BigUint, MerkleProof)>,
    pub trace_next_openings: Vec<(usize, BigUint, MerkleProof)>,
    pub composition_openings: Vec<(usize, BigUint, MerkleProof)>,
    pub fri_openings: Vec<(usize, FriQueryOpening)>,
}

/// Deviations from the honest prover, used by the tests as cheating
/// provers.  [`prove`] uses the default (no deviation).
#[derive(Clone, Debug, Default)]
struct ProverKnobs {
    /// Fold FRI to this many values instead of `β`.
    fri_final_size: Option<usize>,
    /// Build the composition with `α₁ = 0` (drops the transition).
    alpha1_zero: bool,
    /// Commit the zero polynomial as the composition.
    composition_zero: bool,
    /// Claim `f(z) + 1` (and the `Comp(z)` the AIR formula gives for
    /// it), and build the DEEP quotient from those claims.
    ood_wrong_f_z: bool,
    /// Claim `Comp(z) + 1` and build the DEEP quotient from it.
    ood_wrong_comp_z: bool,
    /// Draw the DEEP coefficients without absorbing the OOD values.
    ood_unbound: bool,
    /// Use this point as `z` instead of the transcript's.
    ood_point: Option<BigUint>,
    /// Add 1 to every DEEP value (still low degree).
    deep_offset: bool,
    /// Run FRI on the composition, not on the DEEP combination.
    fri_on_composition: bool,
    /// Commit `f + (Xⁿ − 1)`, degree `n`, which agrees with the trace on
    /// `H_trace` (a valid witness whose DEEP quotient exceeds the bound).
    trace_degree_n: bool,
    /// Leave out the `(λ₀ + λ₁·x)` degree adjustment.
    skip_degree_adjust: bool,
    /// Keep FRI layer 0 and replace every later layer with zeros (each
    /// root re-committed, the transcript re-derived): the final-layer
    /// root check passes, and only fold consistency can reject.
    fri_zero_tail: bool,
    /// Add 1 to every value of FRI layer 1 (re-committed): an
    /// inconsistent intermediate layer.
    fri_shift_layer1: bool,
}

/// **Prove** the AIR is satisfied by an executed trace.  The prover
/// does not check the trace: an invalid one yields a proof that
/// [`verify`] rejects.  `None` if the configuration or the statement is
/// invalid (see [`statement_transcript`]) or the trace has the wrong
/// length; trace values are reduced mod `r`.
pub fn prove(air: &AirV2, config: &StarkConfig) -> Option<StarkProofV2> {
    prove_with(air, config, &ProverKnobs::default())
}

fn prove_with(air: &AirV2, config: &StarkConfig, knobs: &ProverKnobs) -> Option<StarkProofV2> {
    let mut transcript = statement_transcript(air, config)?;
    let n = air.n;
    let beta = config.blow_up;
    let r = scalar_modulus();
    let trace: Vec<BigUint> = (air.generate_trace)().iter().map(|v| v % &r).collect();
    if trace.len() != n {
        return None;
    }
    let h_trace = subgroup(n);
    let omega = h_trace[1].clone();

    // Trace polynomial via Lagrange, evaluated on the coset g · H_lde.
    let f_poly = interpolate_from_subgroup(&h_trace, &trace);
    let lde_size = n * beta;
    let h_lde = coset(lde_size, &coset_shift());
    // The committed trace polynomial (optionally f + (Xⁿ − 1)).
    let f_eval = |x: &BigUint| {
        let v = f_poly.evaluate(x) % &r;
        if knobs.trace_degree_n {
            fr_add(&v, &fr_sub(&pow_pow2(x, n), &BigUint::one()))
        } else {
            v
        }
    };
    let f_lde: Vec<BigUint> = h_lde.iter().map(&f_eval).collect();

    let trace_leaves: Vec<Vec<u8>> = f_lde.iter().map(reduced_bytes).collect();
    let trace_tree = MerkleTree::from_leaves(&trace_leaves);
    let trace_commit = trace_tree.root();

    // α₁, α₂ depend on the statement and the trace commitment.
    let (alpha1, alpha2) = absorb_trace_draw_alphas(&mut transcript, &trace_commit);
    let alpha1 = if knobs.alpha1_zero {
        BigUint::from(0u32)
    } else {
        alpha1
    };
    let mut composition_lde = Vec::with_capacity(lde_size);
    for i in 0..lde_size {
        composition_lde.push(if knobs.composition_zero {
            BigUint::from(0u32)
        } else {
            composition_at(
                air,
                &h_trace,
                &h_lde[i],
                &f_lde[i],
                &f_lde[(i + beta) % lde_size],
                &alpha1,
                &alpha2,
            )?
        });
    }
    let comp_leaves: Vec<Vec<u8>> = composition_lde.iter().map(reduced_bytes).collect();
    let comp_tree = MerkleTree::from_leaves(&comp_leaves);
    let composition_commit = comp_tree.root();

    // Out-of-domain point z and the claims f(z), f(ωz), Comp(z).
    let z_honest = absorb_composition_draw_z(&mut transcript, &composition_commit, n, lde_size);
    let z = knobs.ood_point.clone().unwrap_or(z_honest);
    let wz = fr_mul(&omega, &z);
    let one = BigUint::one();
    let f_z = if knobs.ood_wrong_f_z {
        fr_add(&f_eval(&z), &one)
    } else {
        f_eval(&z)
    };
    let f_wz = f_eval(&wz);
    // A forced in-domain z may be a pole; a cheating prover sends 0.
    let comp_z = composition_at(air, &h_trace, &z, &f_z, &f_wz, &alpha1, &alpha2);
    let comp_z = match (comp_z, knobs.ood_point.is_some()) {
        (Some(c), _) => c,
        (None, true) => BigUint::from(0u32),
        (None, false) => return None,
    };
    let comp_z = if knobs.composition_zero {
        BigUint::from(0u32)
    } else if knobs.ood_wrong_comp_z {
        fr_add(&comp_z, &one)
    } else {
        comp_z
    };
    let ood = OodValues { f_z, f_wz, comp_z };
    let mut coeffs = if knobs.ood_unbound {
        draw_deep_coeffs(&mut transcript)
    } else {
        absorb_ood_draw_deep(&mut transcript, &ood)?
    };
    if knobs.skip_degree_adjust {
        coeffs.lambda = [BigUint::one(), BigUint::from(0u32)];
    }

    // DEEP combination on the coset (degree < n − 1 before the
    // adjustment, < n after it).
    let mut deep_lde = Vec::with_capacity(lde_size);
    for i in 0..lde_size {
        let d = deep_at(
            &h_lde[i],
            &f_lde[i],
            &f_lde[(i + beta) % lde_size],
            &composition_lde[i],
            &z,
            &ood,
            &coeffs,
        );
        deep_lde.push(match (d, knobs.ood_point.is_some()) {
            (Some(d), _) => d,
            (None, true) => BigUint::from(0u32),
            (None, false) => return None,
        });
        if knobs.deep_offset {
            deep_lde[i] = fr_add(&deep_lde[i], &one);
        }
    }
    let fri_input = if knobs.fri_on_composition {
        &composition_lde
    } else {
        &deep_lde
    };

    // FRI to a constant final layer of β values: degree < n.
    let final_size = knobs.fri_final_size.unwrap_or(beta);
    if !final_size.is_power_of_two() || final_size > lde_size {
        return None;
    }
    let fri = if knobs.fri_zero_tail || knobs.fri_shift_layer1 {
        let honest = fri_commit_to(fri_input, &h_lde, &mut transcript.clone(), final_size);
        let mut layers = honest.layers;
        for (k, layer) in layers.iter_mut().enumerate().skip(1) {
            for v in layer.iter_mut() {
                if knobs.fri_zero_tail {
                    *v = BigUint::from(0u32);
                } else if k == 1 {
                    *v = fr_add(v, &one);
                }
            }
        }
        let fri = fri_from_layers(layers);
        transcript = fri_transcript_after(&transcript, &fri)?;
        fri
    } else {
        fri_commit_to(fri_input, &h_lde, &mut transcript, final_size)
    };
    let positions = query_positions(&mut transcript, config.query_count, lde_size);

    let open = |tree: &MerkleTree, table: &[BigUint], p: usize| {
        (p, table[p].clone(), tree.proof(p).unwrap())
    };
    Some(StarkProofV2 {
        trace_commit,
        composition_commit,
        ood,
        trace_openings: positions
            .iter()
            .map(|&p| open(&trace_tree, &f_lde, p))
            .collect(),
        trace_next_openings: positions
            .iter()
            .map(|&p| open(&trace_tree, &f_lde, (p + beta) % lde_size))
            .collect(),
        composition_openings: positions
            .iter()
            .map(|&p| open(&comp_tree, &composition_lde, p))
            .collect(),
        fri_openings: positions.iter().map(|&p| (p, fri_query(&fri, p))).collect(),
        fri,
    })
}

/// A FRI commitment to the given layer tables, as a cheating prover
/// would commit them (no folding is checked).
fn fri_from_layers(layers: Vec<Vec<BigUint>>) -> FriCommitment {
    let layer_trees: Vec<MerkleTree> = layers
        .iter()
        .map(|l| MerkleTree::from_leaves(&l.iter().map(reduced_bytes).collect::<Vec<_>>()))
        .collect();
    FriCommitment {
        layer_roots: layer_trees.iter().map(|t| t.root()).collect(),
        final_constant: layers.last().unwrap()[0].clone(),
        layers,
        layer_trees,
    }
}

/// Why [`verify`] rejected a proof (the tests check which gate fired).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Reject {
    /// Invalid configuration or statement.
    Statement,
    /// Wrong query count or FRI layer count.
    Shape,
    /// A non-canonical OOD value.
    OodValue,
    /// `Comp(z)` differs from the AIR formula at `z`.
    OodAir,
    /// A Merkle opening fails or sits at the wrong position.
    Opening,
    /// An opened `Comp(x)` differs from the AIR formula at `x`.
    Composition,
    /// FRI's first layer differs from the recomputed DEEP value.
    Deep,
    /// The FRI transcript, folding or final layer fails, and why.
    Fri(FriReject),
}

/// **Verify** a STARK v2 proof (module docs, "Transcript" and the
/// paragraph after it) against the verifier's own `config`.
pub fn verify(air: &AirV2, config: &StarkConfig, proof: &StarkProofV2) -> bool {
    check(air, config, proof).is_ok()
}

fn check(air: &AirV2, config: &StarkConfig, proof: &StarkProofV2) -> Result<(), Reject> {
    check_gated(air, config, proof, true)
}

/// [`check`], with the FRI depth gate switchable: `depth_gate = false`
/// is used only by the S2N-2 control test, to show that this gate alone
/// rejects an over-folded proof of a false statement.
fn check_gated(
    air: &AirV2,
    config: &StarkConfig,
    proof: &StarkProofV2,
    depth_gate: bool,
) -> Result<(), Reject> {
    // Checks n, β, q, boundary positions and canonical boundary values.
    let mut transcript = statement_transcript(air, config).ok_or(Reject::Statement)?;
    let n = air.n;
    let beta = config.blow_up;
    let q = config.query_count;
    if proof.trace_openings.len() != q
        || proof.trace_next_openings.len() != q
        || proof.composition_openings.len() != q
        || proof.fri_openings.len() != q
    {
        return Err(Reject::Shape);
    }
    // log₂ n folds: the final layer of β values must be constant.
    if depth_gate && proof.fri.layer_roots.len() != n.trailing_zeros() as usize + 1 {
        return Err(Reject::Shape);
    }
    let lde_size = n * beta;
    let depth = lde_size.trailing_zeros() as usize;
    let h_lde = coset(lde_size, &coset_shift());
    let h_trace = subgroup(n);

    let (alpha1, alpha2) = absorb_trace_draw_alphas(&mut transcript, &proof.trace_commit);
    // z is the verifier's own draw: outside H_trace and the coset.
    let z = absorb_composition_draw_z(&mut transcript, &proof.composition_commit, n, lde_size);
    let ood = &proof.ood;
    let coeffs = absorb_ood_draw_deep(&mut transcript, ood).ok_or(Reject::OodValue)?;
    // The AIR holds at z: Comp(z) is the composition of f(z), f(ωz).
    let comp_z = composition_at(air, &h_trace, &z, &ood.f_z, &ood.f_wz, &alpha1, &alpha2);
    if comp_z.as_ref() != Some(&ood.comp_z) {
        return Err(Reject::OodAir);
    }
    let fri_transcript_initial = transcript.clone();
    let mut after_fri = fri_transcript_after(&fri_transcript_initial, &proof.fri)
        .ok_or(Reject::Fri(FriReject::FinalValue))?;
    let positions = query_positions(&mut after_fri, q, lde_size);

    for (i, &p) in positions.iter().enumerate() {
        let (fx, f_wx, comp) = (
            &proof.trace_openings[i],
            &proof.trace_next_openings[i],
            &proof.composition_openings[i],
        );
        if !opening_ok(fx, p, depth, &proof.trace_commit)
            || !opening_ok(f_wx, (p + beta) % lde_size, depth, &proof.trace_commit)
            || !opening_ok(comp, p, depth, &proof.composition_commit)
        {
            return Err(Reject::Opening);
        }
        // The committed composition is the AIR's composition here ...
        let x = &h_lde[p];
        if Some(&comp.1)
            != composition_at(air, &h_trace, x, &fx.1, &f_wx.1, &alpha1, &alpha2).as_ref()
        {
            return Err(Reject::Composition);
        }
        // ... and FRI's first layer is the DEEP combination of the
        // opened f(x) and Comp(x) with the OOD claims.
        let deep = deep_at(x, &fx.1, &f_wx.1, &comp.1, &z, ood, &coeffs);
        let (fri_pos, fri_open) = &proof.fri_openings[i];
        if *fri_pos != p
            || deep.is_none()
            || fri_open.openings.first().map(|o| &o.0) != deep.as_ref()
        {
            return Err(Reject::Deep);
        }
    }
    fri_check(
        &proof.fri,
        &h_lde,
        &proof.fri_openings,
        &fri_transcript_initial,
    )
    .map_err(Reject::Fri)
}

#[cfg(test)]
mod tests {
    use super::*;
    use num_traits::Zero;

    type T2 = AffineTransition;

    fn big(x: u64) -> BigUint {
        BigUint::from(x)
    }
    fn dbl() -> T2 {
        AffineTransition::new(fr_sub(&big(0), &big(2)), big(1), big(0))
    }
    fn trip() -> T2 {
        AffineTransition::new(fr_sub(&big(0), &big(3)), big(1), big(0))
    }
    fn air2(n: usize, boundary: Vec<(usize, BigUint)>, t: T2, trace: Vec<BigUint>) -> AirV2 {
        AirV2 {
            n,
            boundary,
            transition: t,
            generate_trace: Arc::new(move || trace.clone()),
        }
    }
    fn doubling_trace(n: usize, start: u64) -> Vec<BigUint> {
        (0..n).map(|i| big(start << i)).collect()
    }
    /// Doubling AIR with boundaries (0, 1) and (7, 128), honest trace.
    fn two_boundary_air() -> AirV2 {
        air2(
            8,
            vec![(0, big(1)), (7, big(128))],
            dbl(),
            doubling_trace(8, 1),
        )
    }
    /// The false statement "1 doubled seven times is 12345", proved from
    /// the trace [1, 2, .., 64, 12345] (one broken transition).
    fn false_output_air() -> AirV2 {
        let mut t = doubling_trace(8, 1);
        t[7] = big(12345);
        air2(8, vec![(0, big(1)), (7, big(12345))], dbl(), t)
    }

    /// AIR doubling generates the expected trace.
    #[test]
    fn air_doubling_generates_powers_of_two() {
        let air = AirV2::doubling(8, 3);
        let trace = (air.generate_trace)();
        let expected: Vec<BigUint> = (0..8).map(|i| BigUint::from(3 * (1u64 << i))).collect();
        assert_eq!(trace, expected);
    }

    /// AIR transition constraint zeroes on valid adjacent pairs.
    #[test]
    fn air_transition_zero_on_valid_pair() {
        let air = AirV2::doubling(8, 3);
        // Valid pair: (3, 6).  3·2 = 6.
        let c = air
            .transition
            .evaluate(&BigUint::from(3u32), &BigUint::from(6u32));
        assert!(c.is_zero());
    }

    /// AIR transition is non-zero on invalid pair.
    #[test]
    fn air_transition_nonzero_on_invalid_pair() {
        let air = AirV2::doubling(8, 3);
        // Invalid pair: (3, 7).
        let c = air
            .transition
            .evaluate(&BigUint::from(3u32), &BigUint::from(7u32));
        assert!(!c.is_zero());
    }

    /// The old closure API could encode this quadratic rule while the proof
    /// bound assumed total degree one.  No affine rule agrees with `prev·next`
    /// at these four field points: the first three force all coefficients to
    /// zero, and the fourth then differs.
    #[test]
    fn quadratic_transition_is_outside_the_air_type() {
        let zero = big(0);
        let one = big(1);
        let product = |a: &BigUint, b: &BigUint| fr_mul(a, b);
        let constant = product(&zero, &zero);
        let previous = fr_sub(&product(&one, &zero), &constant);
        let next = fr_sub(&product(&zero, &one), &constant);
        let affine = AffineTransition::new(previous, next, constant);
        for (a, b) in [(&zero, &zero), (&one, &zero), (&zero, &one)] {
            assert_eq!(affine.evaluate(a, b), product(a, b));
        }
        assert_ne!(affine.evaluate(&one, &one), product(&one, &one));
    }

    /// **End-to-end STARK v2** with fast config (blow_up=4, queries=20).
    #[test]
    fn stark_v2_prove_verify_doubling_fast() {
        let air = AirV2::doubling(8, 1);
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).expect("proving");
        assert!(
            verify(&air, &cfg, &proof),
            "v2 verify must accept honest proof"
        );
        let air2b = two_boundary_air();
        let proof = prove(&air2b, &cfg).unwrap();
        assert!(verify(&air2b, &cfg, &proof));
    }

    /// Default config (blow_up=8, queries=80), n = 8 and a longer trace.
    #[test]
    fn stark_v2_prove_verify_doubling_default() {
        let cfg = StarkConfig::default();
        for air in [AirV2::doubling(8, 1), AirV2::doubling(16, 3)] {
            let proof = prove(&air, &cfg).expect("proving");
            assert!(verify(&air, &cfg, &proof));
        }
    }

    // Negative controls: each is a proof of a FALSE statement or a
    // mangled proof, and the verifier must reject it.  The first two
    // are the mutants a 2026-10-16 sheriff audit found accepted
    // (crypto-autoresearcher research/sheriff/SHF-20261016-3caa6f); the
    // rest port the re-audit's mutants (SHF-20261017-e4d7f6, reader
    // "stark", new-mutants/src/main.rs, rows `v2.*`).

    /// An honest proof (trace starts at 1) for another boundary (5);
    /// N4: a valid proof of doubling(8, 3) for doubling(8, 1).
    #[test]
    fn rejects_proof_reused_for_another_boundary() {
        let cfg = StarkConfig::fast();
        let proof = prove(&AirV2::doubling(8, 1), &cfg).unwrap();
        assert!(!verify(&AirV2::doubling(8, 5), &cfg, &proof));
        let p3 = prove(&AirV2::doubling(8, 3), &cfg).unwrap();
        assert!(!verify(&AirV2::doubling(8, 1), &cfg, &p3));
    }

    /// N2a / N2b: wrong public output or input.
    #[test]
    fn rejects_wrong_public_values() {
        let cfg = StarkConfig::fast();
        let proof = prove(&two_boundary_air(), &cfg).unwrap();
        let t = doubling_trace(8, 1);
        let out = air2(8, vec![(0, big(1)), (7, big(129))], dbl(), t.clone());
        assert!(!verify(&out, &cfg, &proof));
        let inp = air2(8, vec![(0, big(3)), (7, big(128))], dbl(), t.clone());
        assert!(!verify(&inp, &cfg, &proof));
        // Dropping a boundary changes the statement too.
        let fewer = air2(8, vec![(0, big(1))], dbl(), t);
        assert!(!verify(&fewer, &cfg, &proof));
    }

    /// N3a / N3b: wrong AIR (tripling: 3^7 != 128, a false statement;
    /// and a 16-row AIR).
    #[test]
    fn rejects_wrong_air() {
        let cfg = StarkConfig::fast();
        let proof = prove(&two_boundary_air(), &cfg).unwrap();
        let tripling = air2(
            8,
            vec![(0, big(1)), (7, big(128))],
            trip(),
            doubling_trace(8, 1),
        );
        assert_ne!(
            air_fingerprint(&tripling),
            air_fingerprint(&two_boundary_air())
        );
        assert!(!verify(&tripling, &cfg, &proof));
        let p8 = prove(&AirV2::doubling(8, 1), &cfg).unwrap();
        assert!(!verify(&AirV2::doubling(16, 1), &cfg, &p8));
    }

    /// A proof with no queries proves nothing.
    #[test]
    fn rejects_empty_proof() {
        let air = AirV2::doubling(8, 1);
        let cfg = StarkConfig::fast();
        let mut proof = prove(&air, &cfg).unwrap();
        proof.trace_openings.clear();
        proof.trace_next_openings.clear();
        proof.composition_openings.clear();
        proof.fri_openings.clear();
        assert!(!verify(&air, &cfg, &proof));
    }

    /// A trace that breaks one transition: the composition is not a
    /// polynomial of degree < n, and degree-bounded FRI rejects it.
    /// Also N1a (tampered row, true statement) and N1b (false output).
    #[test]
    fn rejects_trace_with_broken_transition() {
        let cfg = StarkConfig::fast();
        let mut cheat = AirV2::doubling(8, 1);
        cheat.generate_trace = Arc::new(|| {
            let mut t: Vec<BigUint> = (0..8).map(|i| BigUint::from(1u64 << i)).collect();
            t[5] = BigUint::from(33u32);
            t
        });
        let forged = prove(&cheat, &cfg).unwrap();
        assert!(!verify(&AirV2::doubling(8, 1), &cfg, &forged));
        let mut t = doubling_trace(8, 1);
        t[3] = big(99);
        let tampered = prove(&air2(8, vec![(0, big(1))], dbl(), t), &cfg).unwrap();
        assert!(!verify(&AirV2::doubling(8, 1), &cfg, &tampered));
        let fa = false_output_air();
        assert!(!verify(&fa, &cfg, &prove(&fa, &cfg).unwrap()));
    }

    /// Dropping a FRI layer drops the degree bound (N5a); so does
    /// dropping each query's last opening (N5b) or folding once fewer
    /// with the transcript re-derived (N5c, true and false statements).
    #[test]
    fn rejects_truncated_fri() {
        let air = AirV2::doubling(8, 1);
        let cfg = StarkConfig::fast();
        let mut proof = prove(&air, &cfg).unwrap();
        proof.fri.layer_roots.pop();
        assert!(!verify(&air, &cfg, &proof));
        let mut proof = prove(&air, &cfg).unwrap();
        for fq in proof.fri_openings.iter_mut() {
            fq.1.openings.pop();
        }
        assert!(!verify(&air, &cfg, &proof));
        let fewer = ProverKnobs {
            fri_final_size: Some(2 * cfg.blow_up),
            ..ProverKnobs::default()
        };
        for a in [air, false_output_air()] {
            let p = prove_with(&a, &cfg, &fewer).unwrap();
            assert!(!verify(&a, &cfg, &p));
        }
    }

    /// N5d / M1: the final constant and the last FRI root are bound
    /// (zeroing the last root was accepted before: it was never
    /// absorbed or checked).
    #[test]
    fn rejects_tampered_fri_final_layer() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).unwrap();
        let mut p = proof.clone();
        p.fri.final_constant = fr_add(&p.fri.final_constant, &BigUint::one());
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        let last = p.fri.layer_roots.len() - 1;
        p.fri.layer_roots[last] = [0u8; 32];
        assert!(!verify(&air, &cfg, &p));
    }

    /// First index whose position differs from query 0's.
    fn distinct_from_first(p: &StarkProofV2) -> usize {
        (1..p.trace_openings.len())
            .find(|&j| p.trace_openings[j].0 != p.trace_openings[0].0)
            .expect("two distinct positions")
    }

    /// Queries must come in the order the transcript dictates.
    #[test]
    fn rejects_swapped_queries() {
        let air = AirV2::doubling(8, 1);
        let cfg = StarkConfig::fast();
        let mut proof = prove(&air, &cfg).unwrap();
        let (a, b) = (0, distinct_from_first(&proof));
        proof.trace_openings.swap(a, b);
        proof.trace_next_openings.swap(a, b);
        proof.composition_openings.swap(a, b);
        proof.fri_openings.swap(a, b);
        assert!(!verify(&air, &cfg, &proof));
    }

    /// N6b: a query replaced by a copy of another.
    #[test]
    fn rejects_duplicated_query() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let mut p = prove(&air, &cfg).unwrap();
        let j = distinct_from_first(&p);
        p.trace_openings[j] = p.trace_openings[0].clone();
        p.trace_next_openings[j] = p.trace_next_openings[0].clone();
        p.composition_openings[j] = p.composition_openings[0].clone();
        p.fri_openings[j] = p.fri_openings[0].clone();
        assert!(!verify(&air, &cfg, &p));
    }

    /// N7a / N7b / N7c: the verifier's q and β are authoritative.
    #[test]
    fn rejects_query_count_or_blowup_mismatch() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let q10 = StarkConfig {
            query_count: 10,
            ..cfg.clone()
        };
        let p10 = prove(&air, &q10).unwrap();
        assert!(verify(&air, &q10, &p10));
        assert!(!verify(&air, &cfg, &p10));
        let mut p = prove(&air, &cfg).unwrap();
        p.trace_openings.truncate(10);
        p.trace_next_openings.truncate(10);
        p.composition_openings.truncate(10);
        p.fri_openings.truncate(10);
        assert!(!verify(&air, &cfg, &p));
        assert!(!verify(&air, &q10, &p), "a prefix is not a q = 10 proof");
        let b8 = StarkConfig {
            blow_up: 8,
            query_count: 20,
        };
        assert!(!verify(&air, &b8, &prove(&air, &cfg).unwrap()));
    }

    /// N9 / N10: a committed composition of zero, or one built with
    /// α₁ = 0, for the false statement 1 -> 12345.
    #[test]
    fn rejects_composition_not_bound_to_trace() {
        let cfg = StarkConfig::fast();
        let fa = false_output_air();
        for knobs in [
            ProverKnobs {
                composition_zero: true,
                ..ProverKnobs::default()
            },
            ProverKnobs {
                alpha1_zero: true,
                ..ProverKnobs::default()
            },
        ] {
            let p = prove_with(&fa, &cfg, &knobs).unwrap();
            assert!(!verify(&fa, &cfg, &p), "{knobs:?}");
        }
    }

    /// Is the composition, built with the given α₁, α₂, of degree < n on
    /// the coset (FRI folds to a constant final layer of β values)?
    fn composition_is_low_degree(air: &AirV2, beta: usize, a1: &BigUint, a2: &BigUint) -> bool {
        let n = air.n;
        let h = subgroup(n);
        let f = interpolate_from_subgroup(&h, &(air.generate_trace)());
        let l = n * beta;
        let hl = coset(l, &coset_shift());
        let fl = eval_on_domain(&f, &hl);
        let comp: Vec<BigUint> = (0..l)
            .map(|i| composition_at(air, &h, &hl[i], &fl[i], &fl[(i + beta) % l], a1, a2).unwrap())
            .collect();
        let fri = fri_commit_to(&comp, &hl, &mut Vec::new(), beta);
        fri.layers
            .last()
            .unwrap()
            .iter()
            .all(|v| *v == fri.final_constant)
    }

    /// The frozen-heart forgery (re-audit N8a/N8b/N8c).  A cheating
    /// prover commits to a trace breaking the transition at row `p`,
    /// derives α₁, α₂ from everything it can absorb before choosing the
    /// public value at row `p` (the statement with a placeholder 0
    /// there), and picks the value `v` that cancels the composition's
    /// pole at ω^p under those α's.  Returns (false AIR, its proof from
    /// the real prover, whether the composition is low-degree under the
    /// attacker's α's).  Before statement binding the attacker's α's
    /// were the real ones and the proof was accepted.
    fn frozen_heart(
        cheat: &[BigUint],
        p: usize,
        other: &[(usize, BigUint)],
        k_index: usize,
        cfg: &StarkConfig,
        nudge: u64,
    ) -> (AirV2, StarkProofV2, bool) {
        let n = cheat.len();
        let with_value = |v: BigUint| {
            let mut boundary = other.to_vec();
            boundary.insert(k_index, (p, v));
            air2(n, boundary, dbl(), cheat.to_vec())
        };
        let placeholder = with_value(BigUint::zero());
        let tc = prove(&placeholder, cfg).unwrap().trace_commit;
        let mut t = statement_transcript(&placeholder, cfg).unwrap();
        let (a1, a2) = absorb_trace_draw_alphas(&mut t, &tc);
        let h = subgroup(n);
        let mut zp = BigUint::one();
        for (i, hi) in h.iter().enumerate().take(n - 1) {
            if i != p {
                zp = fr_mul(&zp, &fr_sub(&h[p], hi));
            }
        }
        let c_p = dbl().evaluate(&cheat[p], &cheat[p + 1]);
        let mut a2k = BigUint::one();
        for _ in 0..k_index {
            a2k = fr_mul(&a2k, &a2);
        }
        let shift = fr_mul(&fr_mul(&a1, &c_p), &fr_inv(&fr_mul(&a2k, &zp)).unwrap());
        let v = fr_add(&fr_add(&cheat[p], &shift), &big(nudge));
        let air_false = with_value(v);
        let low = composition_is_low_degree(&air_false, cfg.blow_up, &a1, &a2);
        let proof = prove(&air_false, cfg).unwrap();
        (air_false, proof, low)
    }

    /// N8a (fast and default configs): "doubling with t0 = v, t7 = 128"
    /// for v != 1, from a trace [5, 2, 4, .., 128] that breaks row 0.
    #[test]
    fn rejects_frozen_heart_forged_input() {
        let mut cheat = doubling_trace(8, 1);
        cheat[0] = big(5);
        for cfg in [StarkConfig::fast(), StarkConfig::default()] {
            let (af, pf, low) = frozen_heart(&cheat, 0, &[(7, big(128))], 0, &cfg, 0);
            // Attack control: under the α's the attacker can compute the
            // pole cancels, so only statement binding stops this proof.
            assert!(low, "forgery machinery broken");
            assert_ne!(af.boundary[0].1, big(1), "statement must be false");
            assert!(!verify(&af, &cfg, &pf), "frozen-heart forgery accepted");
        }
    }

    /// N8b: "doubling with t0 = 1, t6 = v" for v != 64 (row 6 broken).
    #[test]
    fn rejects_frozen_heart_forged_row6() {
        let mut cheat = doubling_trace(8, 1);
        cheat[7] = big(999);
        let cfg = StarkConfig::fast();
        let (af, pf, low) = frozen_heart(&cheat, 6, &[(0, big(1))], 1, &cfg, 0);
        assert!(low, "forgery machinery broken");
        assert_ne!(af.boundary[1].1, big(64));
        assert!(!verify(&af, &cfg, &pf));
    }

    /// N8c: the attack control.  With v + 1 the pole does not cancel even
    /// under the attacker's α's, so the composition is not low degree.
    #[test]
    fn frozen_heart_control_v_plus_one_is_not_low_degree() {
        let mut cheat = doubling_trace(8, 1);
        cheat[0] = big(5);
        let cfg = StarkConfig::fast();
        let (af, pf, low) = frozen_heart(&cheat, 0, &[(7, big(128))], 0, &cfg, 1);
        assert!(!low);
        assert!(!verify(&af, &cfg, &pf));
    }

    /// M2: non-canonical encodings (v + r) of opened values are
    /// rejected; so are non-canonical statement values.
    #[test]
    fn rejects_non_canonical_values() {
        let r = scalar_modulus();
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).unwrap();
        let mut p = proof.clone();
        p.trace_openings[0].1 += &r;
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.trace_next_openings[0].1 += &r;
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.composition_openings[0].1 += &r;
        p.fri_openings[0].1.openings[0].0 += &r;
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.fri_openings[0].1.openings[0].1 += &r;
        assert!(!verify(&air, &cfg, &p));
        let shifted = air2(
            8,
            vec![(0, BigUint::one() + &r), (7, big(128))],
            dbl(),
            doubling_trace(8, 1),
        );
        assert!(!verify(&shifted, &cfg, &proof));
        assert!(prove(&shifted, &cfg).is_none());
    }

    /// M3: an opened value of 2^300 returns false instead of panicking,
    /// wherever it appears; so does an out-of-range boundary position.
    #[test]
    fn oversized_values_return_false_without_panic() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).unwrap();
        let huge: BigUint = BigUint::one() << 300;
        let mut p = proof.clone();
        p.trace_openings[0].1 = huge.clone();
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.composition_openings[0].1 = huge.clone();
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.fri_openings[0].1.openings[1].0 = huge.clone();
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.fri.final_constant = huge.clone();
        assert!(!verify(&air, &cfg, &p));
        let big_value = air2(8, vec![(0, huge)], dbl(), doubling_trace(8, 1));
        assert!(!verify(&big_value, &cfg, &proof));
        let bad_pos = air2(8, vec![(8, big(1))], dbl(), doubling_trace(8, 1));
        assert!(!verify(&bad_pos, &cfg, &proof));
        assert!(prove(&bad_pos, &cfg).is_none());
    }

    // DEEP / out-of-domain sample.

    /// The verifier's `z` for `proof`, replayed from the transcript.
    fn replay_z(air: &AirV2, cfg: &StarkConfig, proof: &StarkProofV2) -> BigUint {
        let mut t = statement_transcript(air, cfg).unwrap();
        absorb_trace_draw_alphas(&mut t, &proof.trace_commit);
        let l = air.n * cfg.blow_up;
        absorb_composition_draw_z(&mut t, &proof.composition_commit, air.n, l)
    }

    /// Does the prover's FRI end in a constant final layer, i.e. is the
    /// committed FRI input of degree `< n` (the prover keeps the layers)?
    fn fri_input_low_degree(p: &StarkProofV2) -> bool {
        let last = p.fri.layers.last().unwrap();
        last.iter().all(|v| *v == last[0])
    }

    fn knobs(f: impl FnOnce(&mut ProverKnobs)) -> ProverKnobs {
        let mut k = ProverKnobs::default();
        f(&mut k);
        k
    }

    /// Positive control: the honest OOD values are the trace and
    /// composition polynomials' values at the verifier's own `z`, which
    /// is off both domains, and every gate passes (fast and default).
    #[test]
    fn deep_ood_values_are_the_polynomials_values_at_z() {
        for (air, cfg) in [
            (two_boundary_air(), StarkConfig::fast()),
            (AirV2::doubling(16, 3), StarkConfig::default()),
        ] {
            let proof = prove(&air, &cfg).unwrap();
            assert_eq!(check(&air, &cfg, &proof), Ok(()));
            let z = replay_z(&air, &cfg, &proof);
            let (n, l) = (air.n, air.n * cfg.blow_up);
            assert!(ood_point_ok(&z, n, l));
            let h = subgroup(n);
            let f = interpolate_from_subgroup(&h, &(air.generate_trace)());
            assert_eq!(proof.ood.f_z, f.evaluate(&z));
            assert_eq!(proof.ood.f_wz, f.evaluate(&fr_mul(&h[1], &z)));
            // Comp(z) from its own LDE: interpolate Comp (degree < n) from
            // n coset points and evaluate at z.
            let mut t = statement_transcript(&air, &cfg).unwrap();
            let (a1, a2) = absorb_trace_draw_alphas(&mut t, &proof.trace_commit);
            let pts: Vec<(BigUint, BigUint)> = coset(n, &coset_shift())
                .into_iter()
                .map(|x| {
                    let c = composition_at(
                        &air,
                        &h,
                        &x,
                        &f.evaluate(&x),
                        &f.evaluate(&fr_mul(&h[1], &x)),
                        &a1,
                        &a2,
                    );
                    (x, c.unwrap())
                })
                .collect();
            assert_eq!(proof.ood.comp_z, Poly::interpolate(&pts).evaluate(&z));
            assert!(fri_input_low_degree(&proof));
        }
    }

    /// The second DEEP term is the divided difference of the transformed
    /// trace polynomial `f(ω·X)`, so it must use the opened `f(ω·x)` at the
    /// same `x`.  A nonconstant trace makes this distinguishable from using
    /// the opened `f(x)` with the unrelated point `ω·z`.
    #[test]
    fn deep_uses_transformed_trace_at_same_x() {
        let x = big(11);
        let z = big(13);
        let fx = big(17);
        let f_wx = big(19);
        let ood = OodValues {
            f_z: big(23),
            f_wz: big(29),
            comp_z: big(31),
        };
        let coeffs = DeepCoeffs {
            gamma: [big(0), big(1), big(0)],
            lambda: [big(1), big(0)],
        };
        let got = deep_at(&x, &fx, &f_wx, &big(37), &z, &ood, &coeffs).unwrap();
        let expected = fr_mul(&fr_sub(&f_wx, &ood.f_wz), &fr_inv(&fr_sub(&x, &z)).unwrap());
        assert_eq!(got, expected);
        assert_ne!(fx, f_wx);
    }

    /// Wrong f(z): tampered after proving (the transcript moves), or
    /// claimed by a cheating prover that keeps the AIR consistent at z
    /// and builds the DEEP quotient from its claim, which then has a
    /// pole at z and fails FRI (fast and default configs).
    #[test]
    fn rejects_wrong_ood_f_z() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).unwrap();
        let mut p = proof.clone();
        p.ood.f_z = fr_add(&p.ood.f_z, &BigUint::one());
        assert!(!verify(&air, &cfg, &p));
        let mut p = proof.clone();
        p.ood.f_wz = fr_add(&p.ood.f_wz, &BigUint::one());
        assert!(!verify(&air, &cfg, &p));
        let k = knobs(|k| k.ood_wrong_f_z = true);
        for (a, c) in [
            (two_boundary_air(), StarkConfig::fast()),
            (AirV2::doubling(16, 3), StarkConfig::default()),
        ] {
            let p = prove_with(&a, &c, &k).unwrap();
            // Control: the claim passes the AIR check at z; only the
            // DEEP quotient's degree exposes it.
            assert!(!fri_input_low_degree(&p), "DEEP quotient low degree");
            assert_eq!(check(&a, &c, &p), Err(Reject::Fri(FriReject::FinalLayer)));
        }
    }

    /// Wrong Comp(z), and AIRs inconsistent at z whose committed
    /// composition and DEEP quotient are low degree (zero, or built with
    /// α₁ = 0, for the true statement): the OOD AIR check rejects them,
    /// before any query.
    #[test]
    fn rejects_wrong_ood_comp_z_and_air_inconsistent_at_z() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let mut p = prove(&air, &cfg).unwrap();
        p.ood.comp_z = fr_add(&p.ood.comp_z, &BigUint::one());
        assert!(!verify(&air, &cfg, &p));
        // A wrong Comp(z) leaves a pole in the DEEP quotient too, but the
        // AIR check at z fires first.
        let p = prove_with(&air, &cfg, &knobs(|k| k.ood_wrong_comp_z = true)).unwrap();
        assert!(!fri_input_low_degree(&p));
        assert_eq!(check(&air, &cfg, &p), Err(Reject::OodAir));
        for k in [
            knobs(|k| k.composition_zero = true),
            knobs(|k| k.alpha1_zero = true),
        ] {
            let p = prove_with(&air, &cfg, &k).unwrap();
            // Control: the committed composition and its DEEP quotient
            // are low degree, so only the AIR check at z rejects.
            assert!(fri_input_low_degree(&p), "control {k:?}");
            assert_eq!(check(&air, &cfg, &p), Err(Reject::OodAir), "{k:?}");
        }
        let fa = false_output_air();
        let p = prove_with(&fa, &cfg, &knobs(|k| k.ood_wrong_comp_z = true)).unwrap();
        assert_eq!(check(&fa, &cfg, &p), Err(Reject::OodAir));
    }

    /// OOD values must be bound to the transcript: a prover that draws
    /// the DEEP coefficients without absorbing them is rejected, and so
    /// is a proof whose OOD values are swapped for others that still
    /// satisfy the doubling AIR at z (f(ωz) − 2·f(z) unchanged).
    #[test]
    fn rejects_ood_values_not_bound_to_transcript() {
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let p = prove_with(&air, &cfg, &knobs(|k| k.ood_unbound = true)).unwrap();
        assert!(!verify(&air, &cfg, &p));
        let proof = prove(&air, &cfg).unwrap();
        let z = replay_z(&air, &cfg, &proof);
        let mut t = statement_transcript(&air, &cfg).unwrap();
        let (a1, a2) = absorb_trace_draw_alphas(&mut t, &proof.trace_commit);
        let h = subgroup(air.n);
        let mut p = proof.clone();
        p.ood.f_z = fr_add(&p.ood.f_z, &big(1));
        p.ood.f_wz = fr_add(&p.ood.f_wz, &big(2));
        p.ood.comp_z = composition_at(&air, &h, &z, &p.ood.f_z, &p.ood.f_wz, &a1, &a2).unwrap();
        let res = check(&air, &cfg, &p);
        assert!(res.is_err() && res != Err(Reject::OodAir), "{res:?}");
        // An honest proof's OOD values replayed into another proof.
        let mut other = prove(&AirV2::doubling(8, 1), &cfg).unwrap();
        other.ood = proof.ood.clone();
        assert!(!verify(&AirV2::doubling(8, 1), &cfg, &other));
    }

    /// z is never in H_trace or the LDE coset: [`ood_point_ok`] rejects
    /// every such point, the sampler redraws past a rejected draw, and a
    /// prover that forces z into either domain is rejected (no panic).
    #[test]
    fn rejects_ood_point_inside_the_domains() {
        let (n, beta) = (8, 4);
        let l = n * beta;
        for x in subgroup(n).iter().chain(coset(l, &coset_shift()).iter()) {
            assert!(!ood_point_ok(x, n, l));
        }
        assert!(ood_point_ok(&big(2), n, l));
        let t0 = b"ood-sampler-test".to_vec();
        let (mut t1, mut t2) = (t0.clone(), t0.clone());
        let first = draw_challenge(&mut t1);
        let second = draw_challenge(&mut t1);
        let z = draw_accepted(&mut t2, |z| *z != first);
        assert_eq!((z, t2), (second, t1));
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        assert_eq!((air.n, cfg.blow_up), (n, beta));
        for bad in [subgroup(n)[2].clone(), coset(l, &coset_shift())[3].clone()] {
            let p = prove_with(&air, &cfg, &knobs(|k| k.ood_point = Some(bad.clone()))).unwrap();
            assert!(!verify(&air, &cfg, &p));
        }
    }

    /// DEEP quotients that are not low degree, or not the DEEP of the
    /// openings: the false statement 1 -> 12345 (Comp has a pole, so its
    /// quotient does too); a low-degree table offset from the real DEEP;
    /// FRI run on the composition alone; and a committed trace of degree
    /// n (f + Xⁿ − 1, equal to the trace on H_trace), whose quotient has
    /// degree n − 1 and passes FRI's bound < n only without the degree
    /// adjustment, which the verifier always applies.
    #[test]
    fn rejects_deep_quotient_not_low_degree() {
        let cfg = StarkConfig::fast();
        let fa = false_output_air();
        let p = prove(&fa, &cfg).unwrap();
        assert!(!fri_input_low_degree(&p));
        assert_eq!(
            check(&fa, &cfg, &p),
            Err(Reject::Fri(FriReject::FinalLayer))
        );
        let air = two_boundary_air();
        for k in [
            knobs(|k| k.deep_offset = true),
            knobs(|k| k.fri_on_composition = true),
        ] {
            let p = prove_with(&air, &cfg, &k).unwrap();
            assert!(fri_input_low_degree(&p), "control {k:?}");
            assert_eq!(check(&air, &cfg, &p), Err(Reject::Deep), "{k:?}");
        }
        for c in [StarkConfig::fast(), StarkConfig::default()] {
            let p = prove_with(&air, &c, &knobs(|k| k.trace_degree_n = true)).unwrap();
            assert!(!fri_input_low_degree(&p));
            assert_eq!(check(&air, &c, &p), Err(Reject::Fri(FriReject::FinalLayer)));
            let unadjusted = knobs(|k| {
                k.trace_degree_n = true;
                k.skip_degree_adjust = true;
            });
            let p = prove_with(&air, &c, &unadjusted).unwrap();
            assert!(fri_input_low_degree(&p), "control: bound < n alone passes");
            assert_eq!(check(&air, &c, &p), Err(Reject::Deep));
        }
    }

    // FRI gates isolated (sheriff case SHF-20261028-0f3f64, crypto-
    // autoresearcher research/sheriff/SHF-20261028-0f3f64, findings
    // S2N-1 and S2N-2): each proof passes every gate but the one named.

    /// S2N-1: fold consistency.  The false statement 1 -> 12345 with its
    /// real (not low-degree) DEEP table as FRI layer 0, so the DEEP gate
    /// passes, and all-zero layers after it, so the final-layer root
    /// check passes; only fold consistency rejects.  Also a true
    /// statement whose intermediate layer 1 is shifted by 1.
    #[test]
    fn rejects_fri_fold_inconsistency() {
        let cfg = StarkConfig::fast();
        let fa = false_output_air();
        let honest = prove(&fa, &cfg).unwrap();
        let p = prove_with(&fa, &cfg, &knobs(|k| k.fri_zero_tail = true)).unwrap();
        // Controls: same layer 0 and depth as the honest prover, and a
        // constant (zero) final layer.
        assert_eq!(p.fri.layer_roots[0], honest.fri.layer_roots[0]);
        assert_eq!(p.fri.layer_roots.len(), honest.fri.layer_roots.len());
        assert!(fri_input_low_degree(&p) && !fri_input_low_degree(&honest));
        assert_eq!(p.fri.final_constant, big(0));
        assert_eq!(check(&fa, &cfg, &p), Err(Reject::Fri(FriReject::Fold)));
        let air = two_boundary_air();
        let p = prove_with(&air, &cfg, &knobs(|k| k.fri_shift_layer1 = true)).unwrap();
        assert!(fri_input_low_degree(&p), "control: final layer untouched");
        assert_eq!(check(&air, &cfg, &p), Err(Reject::Fri(FriReject::Fold)));
    }

    /// S2N-2: the verifier-fixed FRI depth (log₂ n folds).  The false
    /// statement folded to a final layer of 1 or β/2 values has extra
    /// layers, and the depth gate rejects it.  Control: at final size 1
    /// FRI bounds no degree, and with the depth gate off every other
    /// gate accepts the false statement.
    #[test]
    fn rejects_over_folded_fri_at_depth_gate() {
        let cfg = StarkConfig::fast();
        let fa = false_output_air();
        for size in [1, cfg.blow_up / 2] {
            let p = prove_with(&fa, &cfg, &knobs(|k| k.fri_final_size = Some(size))).unwrap();
            // The query-count gate is satisfied: the depth gate fired.
            assert_eq!(p.trace_openings.len(), cfg.query_count);
            assert_eq!(check(&fa, &cfg, &p), Err(Reject::Shape), "size {size}");
        }
        let p = prove_with(&fa, &cfg, &knobs(|k| k.fri_final_size = Some(1))).unwrap();
        assert_eq!(check_gated(&fa, &cfg, &p, false), Ok(()));
        let honest = prove(&fa, &cfg).unwrap();
        assert_eq!(
            check_gated(&fa, &cfg, &honest, false),
            Err(Reject::Fri(FriReject::FinalLayer))
        );
    }

    /// Non-canonical (v + r) or oversized OOD values return false.
    #[test]
    fn rejects_non_canonical_ood_values() {
        let r = scalar_modulus();
        let air = two_boundary_air();
        let cfg = StarkConfig::fast();
        let proof = prove(&air, &cfg).unwrap();
        for j in 0..3 {
            let mut p = proof.clone();
            let v = [&mut p.ood.f_z, &mut p.ood.f_wz, &mut p.ood.comp_z];
            *v[j] += &r;
            assert_eq!(check(&air, &cfg, &p), Err(Reject::OodValue));
            let mut p = proof.clone();
            let v = [&mut p.ood.f_z, &mut p.ood.f_wz, &mut p.ood.comp_z];
            *v[j] = BigUint::one() << 300;
            assert!(!verify(&air, &cfg, &p));
        }
    }
}
