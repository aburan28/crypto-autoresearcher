#![recursion_limit = "256"]
//! Public-fixture Pollard-rho calibration for the Koblitz crossover task.
//!
//! This executable is deliberately limited to the exact toy rungs.  Every
//! discrete logarithm is a published synthetic fixture used to validate the
//! walk.  It never accepts an external point or a secret scalar.

use crypto_lib::binary_ecc::curve::point_neg;
use crypto_lib::binary_ecc::{BinaryPoint, F2mElement};
use crypto_lib::cryptanalysis::koblitz_index_calculus::{points_with_x, KoblitzCurve};
use num_bigint::BigUint;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use serde_json::json;
use std::collections::{BTreeSet, HashMap};
use std::time::Instant;

const TASK_ID: &str = "TASK-KIC-SAT-RHO-CROSSOVER-20260909";
const JUMPS: usize = 32;
const MAX_RESTARTS: u64 = 128;
/// Fruitless-collision restart budget for larger fields (n≥41).
const MAX_RESTARTS_LARGE: u64 = 100_000;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Quotient {
    Ordinary,
    Negation,
    SignedFrobenius,
}

#[derive(Clone, Copy)]
enum FixtureTarget {
    SeededScalar,
    ExplicitScalar(u64),
    PublicHash(u64),
}

impl FixtureTarget {
    fn parse(value: Option<&str>) -> Self {
        match value {
            None => Self::SeededScalar,
            Some(value) if value.starts_with("hash:") => Self::PublicHash(
                value[5..]
                    .parse()
                    .expect("public hash target seed must be a u64"),
            ),
            Some(value) => Self::ExplicitScalar(
                value
                    .parse()
                    .expect("explicit validation scalar must be a u64"),
            ),
        }
    }
}

impl Quotient {
    fn parse(value: &str) -> Self {
        match value {
            "ordinary" => Self::Ordinary,
            "negation_only" => Self::Negation,
            "signed_frobenius" => Self::SignedFrobenius,
            _ => panic!("unknown quotient mode {value}"),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Ordinary => "ordinary",
            Self::Negation => "negation_only",
            Self::SignedFrobenius => "signed_frobenius",
        }
    }

    fn uses_negation(self) -> bool {
        self != Self::Ordinary
    }
}

#[derive(Clone)]
struct State {
    point: BinaryPoint,
    a: u64,
    b: u64,
}

#[derive(Clone)]
struct Jump {
    point: BinaryPoint,
    a: u64,
    b: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum RawPoint {
    Infinity,
    Affine { x: u64, y: u64 },
}

#[derive(Clone, Copy)]
struct RawState {
    point: RawPoint,
    a: u64,
    b: u64,
}

#[derive(Clone, Copy)]
struct RawJump {
    point: RawPoint,
    a: u64,
    b: u64,
}

#[derive(Default)]
struct Charges {
    group_additions: u64,
    scalar_multiplications: u64,
    canonicalizations: u64,
    frobenius_maps: u64,
    negations_examined: u64,
    partition_hashes: u64,
    table_queries: u64,
    table_inserts: u64,
    failed_collisions: u64,
    fruitless_cycle_restarts: u64,
}

fn point_key(point: &BinaryPoint) -> (u8, u64, u64) {
    match point {
        BinaryPoint::Infinity => (0, 0, 0),
        BinaryPoint::Affine { x, y } => (
            1,
            x.raw_bits().first().copied().unwrap_or(0),
            y.raw_bits().first().copied().unwrap_or(0),
        ),
    }
}

fn raw_point(point: &BinaryPoint) -> RawPoint {
    match point {
        BinaryPoint::Infinity => RawPoint::Infinity,
        BinaryPoint::Affine { x, y } => RawPoint::Affine {
            x: x.raw_bits().first().copied().unwrap_or(0),
            y: y.raw_bits().first().copied().unwrap_or(0),
        },
    }
}

fn raw_key(point: RawPoint) -> (u8, u64, u64) {
    match point {
        RawPoint::Infinity => (0, 0, 0),
        RawPoint::Affine { x, y } => (1, x, y),
    }
}

fn raw_reduce(curve: &KoblitzCurve, mut wide: u128) -> u64 {
    if curve.n <= 31 && wide <= u64::MAX as u128 {
        let mut narrow = wide as u64;
        let mask = (1u64 << curve.n) - 1;
        while narrow >> curve.n != 0 {
            let high = narrow >> curve.n;
            narrow &= mask;
            for &term in &curve.curve.irreducible.low_terms {
                narrow ^= high << term;
            }
        }
        return narrow;
    }
    let mask = (1u128 << curve.n) - 1;
    while wide >> curve.n != 0 {
        let high = wide >> curve.n;
        wide &= mask;
        for &term in &curve.curve.irreducible.low_terms {
            wide ^= high << term;
        }
    }
    wide as u64
}

// Common ARM carryless-product port; both IC and rho use the same guard.
#[inline]
fn arm_pmull_enabled() -> bool {
    #[cfg(target_arch = "aarch64")]
    { std::arch::is_aarch64_feature_detected!("aes") }
    #[cfg(not(target_arch = "aarch64"))]
    { false }
}

#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "aes")]
unsafe fn arm_pmull_product(left: u64, right: u64) -> u128 {
    std::arch::aarch64::vmull_p64(left, right)
}

fn raw_square(curve: &KoblitzCurve, value: u64) -> u64 {
    #[cfg(target_arch = "aarch64")]
    if arm_pmull_enabled() {
        // SAFETY: the runtime guard proves the required PMULL feature.
        return raw_reduce(curve, unsafe { arm_pmull_product(value, value) });
    }
    if curve.n <= 31 {
        let mut wide = value;
        wide = (wide | (wide << 16)) & 0x0000_ffff_0000_ffff;
        wide = (wide | (wide << 8)) & 0x00ff_00ff_00ff_00ff;
        wide = (wide | (wide << 4)) & 0x0f0f_0f0f_0f0f_0f0f;
        wide = (wide | (wide << 2)) & 0x3333_3333_3333_3333;
        wide = (wide | (wide << 1)) & 0x5555_5555_5555_5555;
        return raw_reduce(curve, wide as u128);
    }
    let mut bits = value;
    let mut wide = 0u128;
    while bits != 0 {
        let bit = bits.trailing_zeros();
        wide ^= 1u128 << (2 * bit);
        bits &= bits - 1;
    }
    raw_reduce(curve, wide)
}

fn raw_mul_field(curve: &KoblitzCurve, left: u64, right: u64) -> u64 {
    #[cfg(target_arch = "aarch64")]
    if arm_pmull_enabled() {
        // SAFETY: the runtime guard proves the required PMULL feature.
        return raw_reduce(curve, unsafe { arm_pmull_product(left, right) });
    }
    if curve.n <= 31 {
        let mut product = 0u64;
        let mut value = right;
        while value != 0 {
            let bit = value.trailing_zeros();
            product ^= left << bit;
            value &= value - 1;
        }
        return raw_reduce(curve, product as u128);
    }
    let mut product = 0u128;
    let mut value = right;
    while value != 0 {
        let bit = value.trailing_zeros();
        product ^= (left as u128) << bit;
        value &= value - 1;
    }
    raw_reduce(curve, product)
}

fn raw_inverse(curve: &KoblitzCurve, value: u64) -> u64 {
    assert_ne!(value, 0);
    let exponent = (1u64 << curve.n) - 2;
    let mut result = 1u64;
    let mut base = value;
    for bit in 0..curve.n {
        if (exponent >> bit) & 1 == 1 {
            result = raw_mul_field(curve, result, base);
        }
        base = raw_square(curve, base);
    }
    result
}

fn raw_neg(point: RawPoint) -> RawPoint {
    match point {
        RawPoint::Infinity => RawPoint::Infinity,
        RawPoint::Affine { x, y } => RawPoint::Affine { x, y: y ^ x },
    }
}

fn raw_double(curve: &KoblitzCurve, point: RawPoint) -> RawPoint {
    let RawPoint::Affine { x, y } = point else {
        return RawPoint::Infinity;
    };
    if x == 0 {
        return RawPoint::Infinity;
    }
    let lambda = x ^ raw_mul_field(curve, y, raw_inverse(curve, x));
    let x3 = raw_square(curve, lambda) ^ lambda ^ curve.a as u64;
    let y3 = raw_square(curve, x) ^ raw_mul_field(curve, lambda ^ 1, x3);
    RawPoint::Affine { x: x3, y: y3 }
}

fn raw_add(curve: &KoblitzCurve, left: RawPoint, right: RawPoint) -> RawPoint {
    match (left, right) {
        (RawPoint::Infinity, point) | (point, RawPoint::Infinity) => point,
        (RawPoint::Affine { x: x1, y: y1 }, RawPoint::Affine { x: x2, y: y2 }) => {
            if x1 == x2 {
                return if y1 ^ y2 == x1 {
                    RawPoint::Infinity
                } else {
                    raw_double(curve, left)
                };
            }
            let lambda = raw_mul_field(curve, y1 ^ y2, raw_inverse(curve, x1 ^ x2));
            let x3 = raw_square(curve, lambda) ^ lambda ^ x1 ^ x2 ^ curve.a as u64;
            let y3 = raw_mul_field(curve, lambda, x1 ^ x3) ^ x3 ^ y1;
            RawPoint::Affine { x: x3, y: y3 }
        }
    }
}

fn raw_scalar_mul(curve: &KoblitzCurve, point: RawPoint, scalar: u64) -> RawPoint {
    let mut result = RawPoint::Infinity;
    for bit in (0..64 - scalar.leading_zeros()).rev() {
        result = raw_double(curve, result);
        if (scalar >> bit) & 1 == 1 {
            result = raw_add(curve, result, point);
        }
    }
    result
}

fn mul_mod(left: u64, right: u64, modulus: u64) -> u64 {
    ((left as u128 * right as u128) % modulus as u128) as u64
}

fn signed_automorphism_size(lambda: u64, modulus: u64, n: u32) -> usize {
    let mut scalars = BTreeSet::new();
    let mut current = 1u64;
    for _ in 0..n {
        scalars.insert(current);
        scalars.insert((modulus - current) % modulus);
        current = mul_mod(current, lambda, modulus);
    }
    assert_eq!(current, 1);
    scalars.len()
}

fn sub_mod(left: u64, right: u64, modulus: u64) -> u64 {
    if left >= right {
        left - right
    } else {
        modulus - (right - left)
    }
}

fn inverse_mod(value: u64, modulus: u64) -> Option<u64> {
    if value == 0 {
        return None;
    }
    let (mut old_r, mut r) = (modulus as i128, value as i128);
    let (mut old_t, mut t) = (0i128, 1i128);
    while r != 0 {
        let quotient = old_r / r;
        (old_r, r) = (r, old_r - quotient * r);
        (old_t, t) = (t, old_t - quotient * t);
    }
    (old_r == 1).then_some(old_t.rem_euclid(modulus as i128) as u64)
}

fn canonicalize(
    curve: &KoblitzCurve,
    state: State,
    mode: Quotient,
    modulus: u64,
    lambda: u64,
    charges: &mut Charges,
) -> State {
    charges.canonicalizations += 1;
    if state.point == BinaryPoint::Infinity || mode == Quotient::Ordinary {
        return state;
    }

    let powers = if mode == Quotient::SignedFrobenius {
        curve.n
    } else {
        1
    };
    let mut point = state.point.clone();
    let mut multiplier = 1u64;
    let mut best_key = point_key(&point);
    let mut best_point = point.clone();
    let mut best_multiplier = multiplier;

    for exponent in 0..powers {
        let key = point_key(&point);
        if key < best_key {
            best_key = key;
            best_point = point.clone();
            best_multiplier = multiplier;
        }
        if mode.uses_negation() {
            charges.negations_examined += 1;
            let negative = point_neg(&point);
            let negative_key = point_key(&negative);
            if negative_key < best_key {
                best_key = negative_key;
                best_point = negative;
                best_multiplier = if multiplier == 0 {
                    0
                } else {
                    modulus - multiplier
                };
            }
        }
        if exponent + 1 < powers {
            point = curve.frobenius(&point);
            multiplier = mul_mod(multiplier, lambda, modulus);
            charges.frobenius_maps += 1;
        }
    }

    State {
        point: best_point,
        a: mul_mod(state.a, best_multiplier, modulus),
        b: mul_mod(state.b, best_multiplier, modulus),
    }
}

fn raw_canonicalize(
    curve: &KoblitzCurve,
    state: RawState,
    mode: Quotient,
    modulus: u64,
    lambda: u64,
    charges: &mut Charges,
) -> RawState {
    charges.canonicalizations += 1;
    if state.point == RawPoint::Infinity || mode == Quotient::Ordinary {
        return state;
    }
    let powers = if mode == Quotient::SignedFrobenius {
        curve.n
    } else {
        1
    };
    let mut point = state.point;
    let mut multiplier = 1u64;
    let mut best_key = raw_key(point);
    let mut best_point = point;
    let mut best_multiplier = multiplier;
    for exponent in 0..powers {
        let key = raw_key(point);
        if key < best_key {
            best_key = key;
            best_point = point;
            best_multiplier = multiplier;
        }
        if mode.uses_negation() {
            charges.negations_examined += 1;
            let negative = raw_neg(point);
            if raw_key(negative) < best_key {
                best_key = raw_key(negative);
                best_point = negative;
                best_multiplier = modulus - multiplier;
            }
        }
        if exponent + 1 < powers {
            point = match point {
                RawPoint::Infinity => RawPoint::Infinity,
                RawPoint::Affine { x, y } => RawPoint::Affine {
                    x: raw_square(curve, x),
                    y: raw_square(curve, y),
                },
            };
            multiplier = mul_mod(multiplier, lambda, modulus);
            charges.frobenius_maps += 1;
        }
    }
    RawState {
        point: best_point,
        a: mul_mod(state.a, best_multiplier, modulus),
        b: mul_mod(state.b, best_multiplier, modulus),
    }
}

fn partition(point: &BinaryPoint) -> usize {
    let (_, x, y) = point_key(point);
    let mut value = x ^ y.rotate_left(21) ^ 0x9e37_79b9_7f4a_7c15;
    value ^= value >> 30;
    value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value ^= value >> 27;
    value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^= value >> 31;
    value as usize % JUMPS
}

fn raw_partition(point: RawPoint) -> usize {
    let (_, x, y) = raw_key(point);
    let mut value = x ^ y.rotate_left(21) ^ 0x9e37_79b9_7f4a_7c15;
    value ^= value >> 30;
    value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    value ^= value >> 27;
    value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
    value ^= value >> 31;
    value as usize % JUMPS
}

fn random_state(
    curve: &KoblitzCurve,
    q: &BinaryPoint,
    rng: &mut StdRng,
    modulus: u64,
    charges: &mut Charges,
) -> State {
    loop {
        let a = rng.gen_range(0..modulus);
        let b = rng.gen_range(0..modulus);
        charges.scalar_multiplications += 2;
        charges.group_additions += 1;
        let point = curve.add(
            &curve.mul(curve.generator(), &BigUint::from(a)),
            &curve.mul(q, &BigUint::from(b)),
        );
        if point != BinaryPoint::Infinity {
            return State { point, a, b };
        }
    }
}

fn make_jumps(
    curve: &KoblitzCurve,
    q: &BinaryPoint,
    rng: &mut StdRng,
    modulus: u64,
    charges: &mut Charges,
) -> Vec<Jump> {
    (0..JUMPS)
        .map(|_| loop {
            let state = random_state(curve, q, rng, modulus, charges);
            if state.point != BinaryPoint::Infinity {
                break Jump {
                    point: state.point,
                    a: state.a,
                    b: state.b,
                };
            }
        })
        .collect()
}

fn raw_random_state(
    curve: &KoblitzCurve,
    generator: RawPoint,
    q: RawPoint,
    rng: &mut StdRng,
    modulus: u64,
    charges: &mut Charges,
) -> RawState {
    loop {
        let a = rng.gen_range(0..modulus);
        let b = rng.gen_range(0..modulus);
        charges.scalar_multiplications += 2;
        charges.group_additions += 1;
        let point = raw_add(
            curve,
            raw_scalar_mul(curve, generator, a),
            raw_scalar_mul(curve, q, b),
        );
        if point != RawPoint::Infinity {
            return RawState { point, a, b };
        }
    }
}

fn raw_make_jumps(
    curve: &KoblitzCurve,
    generator: RawPoint,
    q: RawPoint,
    rng: &mut StdRng,
    modulus: u64,
    charges: &mut Charges,
) -> Vec<RawJump> {
    (0..JUMPS)
        .map(|_| {
            let state = raw_random_state(curve, generator, q, rng, modulus, charges);
            RawJump {
                point: state.point,
                a: state.a,
                b: state.b,
            }
        })
        .collect()
}

fn public_hash_target(curve: &KoblitzCurve, seed: u64) -> (BinaryPoint, u64) {
    const DOMAIN: &[u8] = b"ic-workflow-public-target-v1\0";
    let mask = (1u64 << curve.n) - 1;
    for counter in 0u64..1_000_000 {
        let mut hasher = blake3::Hasher::new();
        hasher.update(DOMAIN);
        hasher.update(&curve.n.to_le_bytes());
        hasher.update(&[curve.a]);
        hasher.update(&curve.k.to_le_bytes());
        hasher.update(&curve.b_index.to_le_bytes());
        hasher.update(&seed.to_le_bytes());
        hasher.update(&counter.to_le_bytes());
        let digest = hasher.finalize();
        let bytes = digest.as_bytes();
        let mut word = [0u8; 8];
        word.copy_from_slice(&bytes[..8]);
        let x = F2mElement::from_biguint(&BigUint::from(u64::from_le_bytes(word) & mask), curve.n);
        let mut lifts = points_with_x(&curve.curve, &x);
        lifts.sort_by_key(point_key);
        if lifts.is_empty() {
            continue;
        }
        let raw = lifts[usize::from(bytes[8] & 1) % lifts.len()].clone();
        let target = curve.mul(&raw, &curve.cofactor);
        if target == BinaryPoint::Infinity {
            continue;
        }
        assert_eq!(
            curve.mul(&target, &curve.subgroup_order),
            BinaryPoint::Infinity
        );
        return (target, counter);
    }
    panic!("public hash-to-curve target attempt cap exhausted");
}

fn solve_fixture(
    curve: &KoblitzCurve,
    mode: Quotient,
    fixture_index: u64,
    fixture_seed: u64,
    fixture_target: FixtureTarget,
) -> serde_json::Value {
    let modulus = curve.subgroup_order.to_u64_digits()[0];
    let lambda = curve.lambda.to_u64_digits()[0];
    let signed_size = signed_automorphism_size(lambda, modulus, curve.n);
    let mut rng = StdRng::seed_from_u64(fixture_seed);
    let generated_scalar = rng.gen_range(1..modulus);
    let target_generation_started = Instant::now();
    let (known_scalar, q, fixture_scalar_source, public_hash_seed, public_hash_counter) =
        match fixture_target {
            FixtureTarget::SeededScalar => (
                Some(generated_scalar),
                curve.mul(curve.generator(), &BigUint::from(generated_scalar)),
                "seeded_fixture_scalar",
                None,
                None,
            ),
            FixtureTarget::ExplicitScalar(scalar) => (
                Some(scalar),
                curve.mul(curve.generator(), &BigUint::from(scalar)),
                "explicit_public_validation_scalar",
                None,
                None,
            ),
            FixtureTarget::PublicHash(seed) => {
                let (target, counter) = public_hash_target(curve, seed);
                (
                    None,
                    target,
                    "public_hash_unknown_scalar",
                    Some(seed),
                    Some(counter),
                )
            }
        };
    let target_generation_ms = target_generation_started.elapsed().as_secs_f64() * 1000.0;
    let mut charges = Charges {
        scalar_multiplications: 1,
        ..Charges::default()
    };
    let started = Instant::now();
    let jumps = make_jumps(curve, &q, &mut rng, modulus, &mut charges);
    let setup_ms = started.elapsed().as_secs_f64() * 1000.0;
    let walk_started = Instant::now();
    let mut table: HashMap<(u8, u64, u64), (u64, u64)> = HashMap::new();
    let ideal_steps = (std::f64::consts::PI * modulus as f64
        / (2.0
            * match mode {
                Quotient::Ordinary => 1.0,
                Quotient::Negation => 2.0,
                Quotient::SignedFrobenius => signed_size as f64,
            }))
    .sqrt();
    // Toy rungs finish with 200×√(πr/2A); n≥41 needs more headroom —
    // distinguished-point density and restart waste grow with the field.
    let safety = if curve.n >= 41 { 2_000 } else { 200 };
    let max_steps = (ideal_steps.ceil() as u64)
        .saturating_mul(safety)
        .max(10_000);
    let mut steps = 0u64;
    let mut restarts = 0u64;
    let mut recovered = None;
    let restart_cap = if curve.n >= 41 {
        MAX_RESTARTS_LARGE
    } else {
        MAX_RESTARTS
    };

    'restart: while restarts <= restart_cap && steps < max_steps {
        let initial = random_state(curve, &q, &mut rng, modulus, &mut charges);
        let mut state = canonicalize(curve, initial, mode, modulus, lambda, &mut charges);
        loop {
            let key = point_key(&state.point);
            charges.table_queries += 1;
            if let Some(&(old_a, old_b)) = table.get(&key) {
                let numerator = sub_mod(old_a, state.a, modulus);
                let denominator = sub_mod(state.b, old_b, modulus);
                if let Some(inverse) = inverse_mod(denominator, modulus) {
                    let candidate = mul_mod(numerator, inverse, modulus);
                    charges.scalar_multiplications += 1;
                    if curve.mul(curve.generator(), &BigUint::from(candidate)) == q {
                        recovered = Some(candidate);
                        break 'restart;
                    }
                    charges.failed_collisions += 1;
                } else {
                    charges.failed_collisions += 1;
                }
                charges.fruitless_cycle_restarts += 1;
                restarts += 1;
                continue 'restart;
            }
            table.insert(key, (state.a, state.b));
            charges.table_inserts += 1;
            let jump_index = partition(&state.point);
            charges.partition_hashes += 1;
            let jump = &jumps[jump_index];
            state = State {
                point: curve.add(&state.point, &jump.point),
                a: (state.a + jump.a) % modulus,
                b: (state.b + jump.b) % modulus,
            };
            charges.group_additions += 1;
            state = canonicalize(curve, state, mode, modulus, lambda, &mut charges);
            steps += 1;
            if steps >= max_steps {
                break 'restart;
            }
        }
    }
    let walk_ms = walk_started.elapsed().as_secs_f64() * 1000.0;
    let recovered = recovered.expect("public rho fixture exceeded the frozen step/restart cap");
    if let Some(expected) = known_scalar {
        assert_eq!(recovered, expected);
    }
    let table_entries = table.len();
    let generator_point_key = point_key(curve.generator());
    let q_point_key = point_key(&q);

    json!({
        "schema_version":"1.0",
        "task_id":TASK_ID,
        "kind":"rho_public_fixture",
        "evidence_class":"measured_rho_observation",
        "n":curve.n,
        "a":curve.curve.a.raw_bits().first().copied().unwrap_or(0),
        "subgroup_order":modulus,
        "lambda":lambda,
        "quotient_mode":mode.name(),
        "arithmetic_backend":"reference_f2m",
        "automorphism_size":match mode {
            Quotient::Ordinary => 1,
            Quotient::Negation => 2,
            Quotient::SignedFrobenius => signed_size as u32,
        },
        "fixture_index":fixture_index,
        "fixture_seed":fixture_seed,
        "published_fixture_scalar":known_scalar,
        "fixture_scalar_source":fixture_scalar_source,
        "target_scalar_constructed":known_scalar.is_some(),
        "target_kind":if known_scalar.is_some() {"known_scalar_multiple"} else {"public_hash_to_curve_cofactor"},
        "public_hash_seed":public_hash_seed,
        "public_hash_counter":public_hash_counter,
        "recovered_fixture_scalar":recovered,
        "generator":[generator_point_key.1,generator_point_key.2],
        "published_q":[q_point_key.1,q_point_key.2],
        "generator_point_key":[generator_point_key.1,generator_point_key.2],
        "published_q_point_key":[q_point_key.1,q_point_key.2],
        "field_modulus_low_terms":curve.curve.irreducible.low_terms,
        "verified":true,
        "ideal_steps":ideal_steps,
        "walk_steps":steps,
        "restarts":restarts,
        "jump_count":JUMPS,
        "distinguished_bits":0,
        "table_entries":table_entries,
        "table_payload_lower_bound_bytes":table_entries * (1 + 5 * std::mem::size_of::<u64>()),
        "setup_ms":setup_ms,
        "target_generation_ms":target_generation_ms,
        "walk_ms":walk_ms,
        "total_ms":target_generation_ms + setup_ms + walk_ms,
        "charges":{
            "group_additions":charges.group_additions,
            "scalar_multiplications":charges.scalar_multiplications,
            "canonicalizations":charges.canonicalizations,
            "frobenius_maps":charges.frobenius_maps,
            "negations_examined":charges.negations_examined,
            "partition_hashes":charges.partition_hashes,
            "table_queries":charges.table_queries,
            "table_inserts":charges.table_inserts,
            "failed_collisions":charges.failed_collisions,
            "fruitless_cycle_restarts":charges.fruitless_cycle_restarts
        },
        "scope":if known_scalar.is_some() {"published synthetic toy fixture; no external point or production key"} else {"public_hash_unknown_scalar"}
    })
}

fn solve_fixture_packed(
    curve: &KoblitzCurve,
    mode: Quotient,
    fixture_index: u64,
    fixture_seed: u64,
    fixture_target: FixtureTarget,
) -> serde_json::Value {
    let modulus = curve.subgroup_order.to_u64_digits()[0];
    let lambda = curve.lambda.to_u64_digits()[0];
    let signed_size = signed_automorphism_size(lambda, modulus, curve.n);
    let generator = raw_point(curve.generator());
    let mut rng = StdRng::seed_from_u64(fixture_seed);
    let generated_scalar = rng.gen_range(1..modulus);
    let target_generation_started = Instant::now();
    let (known_scalar, reference_q, fixture_scalar_source, public_hash_seed, public_hash_counter) =
        match fixture_target {
            FixtureTarget::SeededScalar => (
                Some(generated_scalar),
                curve.mul(curve.generator(), &BigUint::from(generated_scalar)),
                "seeded_fixture_scalar",
                None,
                None,
            ),
            FixtureTarget::ExplicitScalar(scalar) => (
                Some(scalar),
                curve.mul(curve.generator(), &BigUint::from(scalar)),
                "explicit_public_validation_scalar",
                None,
                None,
            ),
            FixtureTarget::PublicHash(seed) => {
                let (target, counter) = public_hash_target(curve, seed);
                (
                    None,
                    target,
                    "public_hash_unknown_scalar",
                    Some(seed),
                    Some(counter),
                )
            }
        };
    let target_generation_ms = target_generation_started.elapsed().as_secs_f64() * 1000.0;
    let mut charges = Charges::default();
    let started = Instant::now();
    let q = raw_point(&reference_q);
    charges.scalar_multiplications += 1;
    let jumps = raw_make_jumps(curve, generator, q, &mut rng, modulus, &mut charges);
    let setup_ms = started.elapsed().as_secs_f64() * 1000.0;
    let walk_started = Instant::now();
    let mut table: HashMap<(u8, u64, u64), (u64, u64)> = HashMap::new();
    let ideal_steps = (std::f64::consts::PI * modulus as f64
        / (2.0
            * match mode {
                Quotient::Ordinary => 1.0,
                Quotient::Negation => 2.0,
                Quotient::SignedFrobenius => signed_size as f64,
            }))
    .sqrt();
    // Toy rungs finish with 200×√(πr/2A); n≥41 needs more headroom —
    // distinguished-point density and restart waste grow with the field.
    let safety = if curve.n >= 41 { 2_000 } else { 200 };
    let max_steps = (ideal_steps.ceil() as u64)
        .saturating_mul(safety)
        .max(10_000);
    let mut steps = 0u64;
    let mut restarts = 0u64;
    let mut recovered = None;
    let restart_cap = if curve.n >= 41 {
        MAX_RESTARTS_LARGE
    } else {
        MAX_RESTARTS
    };

    'restart: while restarts <= restart_cap && steps < max_steps {
        let initial = raw_random_state(curve, generator, q, &mut rng, modulus, &mut charges);
        let mut state = raw_canonicalize(curve, initial, mode, modulus, lambda, &mut charges);
        loop {
            let key = raw_key(state.point);
            charges.table_queries += 1;
            if let Some(&(old_a, old_b)) = table.get(&key) {
                let numerator = sub_mod(old_a, state.a, modulus);
                let denominator = sub_mod(state.b, old_b, modulus);
                if let Some(inverse) = inverse_mod(denominator, modulus) {
                    let candidate = mul_mod(numerator, inverse, modulus);
                    charges.scalar_multiplications += 1;
                    if raw_scalar_mul(curve, generator, candidate) == q {
                        recovered = Some(candidate);
                        break 'restart;
                    }
                    charges.failed_collisions += 1;
                } else {
                    charges.failed_collisions += 1;
                }
                charges.fruitless_cycle_restarts += 1;
                restarts += 1;
                continue 'restart;
            }
            table.insert(key, (state.a, state.b));
            charges.table_inserts += 1;
            let jump = raw_make_jump_ref(&jumps, raw_partition(state.point));
            charges.partition_hashes += 1;
            state = RawState {
                point: raw_add(curve, state.point, jump.point),
                a: (state.a + jump.a) % modulus,
                b: (state.b + jump.b) % modulus,
            };
            charges.group_additions += 1;
            state = raw_canonicalize(curve, state, mode, modulus, lambda, &mut charges);
            steps += 1;
            if steps >= max_steps {
                break 'restart;
            }
        }
    }
    let walk_ms = walk_started.elapsed().as_secs_f64() * 1000.0;
    let recovered = recovered.expect("packed public rho fixture exceeded cap");
    let validation_started = Instant::now();
    if let Some(expected) = known_scalar {
        assert_eq!(recovered, expected);
    }
    assert_eq!(raw_point(&reference_q), q);
    assert_eq!(
        curve.mul(curve.generator(), &BigUint::from(recovered)),
        reference_q
    );
    let validation_ms = validation_started.elapsed().as_secs_f64() * 1000.0;
    let table_entries = table.len();
    let generator_point_key = raw_key(generator);
    let q_point_key = raw_key(q);

    json!({
        "schema_version":"1.0",
        "task_id":TASK_ID,
        "kind":"rho_public_fixture",
        "evidence_class":"measured_rho_observation",
        "n":curve.n,
        "a":curve.a,
        "subgroup_order":modulus,
        "lambda":lambda,
        "quotient_mode":mode.name(),
        "arithmetic_backend":"packed_u64_polynomial_basis",
        "field_multiplication_backend":if arm_pmull_enabled() {"aarch64_pmull"} else {"portable_sparse_carryless"},
        "field_squaring_backend":if arm_pmull_enabled() {"aarch64_pmull"} else {"portable_bit_interleave"},
        "automorphism_size":match mode {
            Quotient::Ordinary => 1,
            Quotient::Negation => 2,
            Quotient::SignedFrobenius => signed_size as u32,
        },
        "fixture_index":fixture_index,
        "fixture_seed":fixture_seed,
        "published_fixture_scalar":known_scalar,
        "fixture_scalar_source":fixture_scalar_source,
        "target_scalar_constructed":known_scalar.is_some(),
        "target_kind":if known_scalar.is_some() {"known_scalar_multiple"} else {"public_hash_to_curve_cofactor"},
        "public_hash_seed":public_hash_seed,
        "public_hash_counter":public_hash_counter,
        "recovered_fixture_scalar":recovered,
        "generator":[generator_point_key.1,generator_point_key.2],
        "published_q":[q_point_key.1,q_point_key.2],
        "generator_point_key":[generator_point_key.1,generator_point_key.2],
        "published_q_point_key":[q_point_key.1,q_point_key.2],
        "field_modulus_low_terms":curve.curve.irreducible.low_terms,
        "verified":true,
        "reference_group_validation":true,
        "ideal_steps":ideal_steps,
        "walk_steps":steps,
        "restarts":restarts,
        "jump_count":JUMPS,
        "distinguished_bits":0,
        "table_entries":table_entries,
        "table_payload_lower_bound_bytes":table_entries * (1 + 5 * std::mem::size_of::<u64>()),
        "setup_ms":setup_ms,
        "target_generation_ms":target_generation_ms,
        "walk_ms":walk_ms,
        "validation_ms":validation_ms,
        "total_ms":target_generation_ms + setup_ms + walk_ms + validation_ms,
        "charges":{
            "group_additions":charges.group_additions,
            "scalar_multiplications":charges.scalar_multiplications,
            "canonicalizations":charges.canonicalizations,
            "frobenius_maps":charges.frobenius_maps,
            "negations_examined":charges.negations_examined,
            "partition_hashes":charges.partition_hashes,
            "table_queries":charges.table_queries,
            "table_inserts":charges.table_inserts,
            "failed_collisions":charges.failed_collisions,
            "fruitless_cycle_restarts":charges.fruitless_cycle_restarts
        },
        "scope":if known_scalar.is_some() {"published synthetic toy fixture; no external point or production key"} else {"public_hash_unknown_scalar"}
    })
}

fn raw_make_jump_ref(jumps: &[RawJump], index: usize) -> &RawJump {
    &jumps[index]
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        (5..=8).contains(&args.len()),
        "usage: <n> <a> <mode> <fixtures> [reference|packed] [batch_seed] [explicit_fixture_scalar|hash:public_seed]"
    );
    let n: u32 = args[1].parse().unwrap();
    let a: u8 = args[2].parse().unwrap();
    let mode = Quotient::parse(&args[3]);
    let fixtures: u64 = args[4].parse().unwrap();
    let backend = args.get(5).map(String::as_str).unwrap_or("reference");
    let batch_seed = args.get(6).map(|value| value.parse::<u64>().unwrap());
    let fixture_target = FixtureTarget::parse(args.get(7).map(String::as_str));
    assert!(matches!(backend, "reference" | "packed"));
    assert!(matches!(n, 7 | 11 | 13 | 17 | 19 | 23 | 37 | 41 | 53));
    assert!(fixtures > 0);
    let curve = KoblitzCurve::new(a, n).expect("frozen exact rung must construct");
    let modulus = curve.subgroup_order.to_u64_digits()[0];
    if let FixtureTarget::ExplicitScalar(scalar) = fixture_target {
        assert!(fixtures == 1, "an explicit scalar requires one fixture");
        assert!(
            (1..modulus).contains(&scalar),
            "explicit scalar must be in 1..r"
        );
    }
    if matches!(fixture_target, FixtureTarget::PublicHash(_)) {
        assert!(fixtures == 1, "a public hash target requires one fixture");
    }
    for fixture_index in 0..fixtures {
        let material = if let Some(batch_seed) = batch_seed {
            format!(
                "TASK-KIC-DIRECT-BATCH-20260910|rho|{n}|{a}|{}|{batch_seed}|{fixture_index}",
                mode.name()
            )
        } else {
            format!("{TASK_ID}|rho|{n}|{a}|{}|{fixture_index}", mode.name())
        };
        let digest = blake3::hash(material.as_bytes());
        let seed = u64::from_le_bytes(digest.as_bytes()[..8].try_into().unwrap());
        let result = if backend == "packed" {
            solve_fixture_packed(&curve, mode, fixture_index, seed, fixture_target)
        } else {
            solve_fixture(&curve, mode, fixture_index, seed, fixture_target)
        };
        println!("{}", result);
    }
}

#[cfg(test)]
mod packed_tests {
    use super::*;

    #[test]
    fn packed_rho_arithmetic_matches_reference() {
        for (n, a) in [
            (7, 1),
            (11, 1),
            (13, 0),
            (17, 1),
            (19, 1),
            (23, 1),
            (37, 0),
            (41, 0),
        ] {
            let curve = KoblitzCurve::new(a, n).unwrap();
            let generator = raw_point(curve.generator());
            for scalar in 0..128u64 {
                assert_eq!(
                    raw_scalar_mul(&curve, generator, scalar),
                    raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar)))
                );
            }
            let left = raw_scalar_mul(&curve, generator, 37);
            let right = raw_scalar_mul(&curve, generator, 91);
            assert_eq!(
                raw_add(&curve, left, right),
                raw_point(&curve.add(
                    &curve.mul(curve.generator(), &BigUint::from(37u64)),
                    &curve.mul(curve.generator(), &BigUint::from(91u64)),
                ))
            );
            let RawPoint::Affine { x, .. } = left else {
                panic!("nonzero scalar must be affine");
            };
            let reference = crypto_lib::binary_ecc::F2mElement::from_biguint(&BigUint::from(x), n);
            assert_eq!(
                raw_square(&curve, x),
                reference
                    .square(&curve.curve.irreducible)
                    .raw_bits()
                    .first()
                    .copied()
                    .unwrap_or(0)
            );
        }
    }
}

#[cfg(all(test, target_arch = "aarch64"))]
mod cold_arm_port_tests {
    use super::*;
    fn bitwise_product(a: u64, b: u64) -> u128 {
        let mut p = 0u128;
        for i in 0..64 { if (b >> i) & 1 != 0 { p ^= (a as u128) << i; } }
        p
    }
    fn bitwise_reduce(curve: &KoblitzCurve, mut p: u128) -> u64 {
        let mut modulus = 1u128 << curve.n;
        for &term in &curve.curve.irreducible.low_terms { modulus ^= 1u128 << term; }
        for i in (curve.n..128).rev() {
            if (p >> i) & 1 != 0 { p ^= modulus << (i - curve.n); }
        }
        p as u64
    }
    #[test]
    fn pmull_matches_independent_bitwise_edges_and_corpus() {
        assert!(arm_pmull_enabled(), "this ARM fairness gate requires available PMULL");
        let edge = [0, 1, u64::MAX, 1u64 << 63, (1u64 << 53)-1, (1u64 << 13)-1, 0xaaaaaaaaaaaaaaaa, 0x5555555555555555];
        for &a in &edge { for &b in &edge {
            assert_eq!(unsafe { arm_pmull_product(a,b) }, bitwise_product(a,b));
        }}
        let mut x = 0x8a5cd789635d2dffu64;
        for _ in 0..256 {
            x ^= x << 13; x ^= x >> 7; x ^= x << 17;
            let y = x.rotate_left(29) ^ 0x6a09e667f3bcc909;
            assert_eq!(unsafe { arm_pmull_product(x,y) }, bitwise_product(x,y));
            assert_eq!(unsafe { arm_pmull_product(x,x) }, bitwise_product(x,x));
        }
    }
    #[test]
    fn reduced_n13_n53_operations_match_independent_bitwise_oracle() {
        assert!(arm_pmull_enabled());
        for n in [13u32,53] {
            let curve = KoblitzCurve::new(0,n).unwrap();
            let mask = (1u64 << n)-1;
            let mut x = 0xd1b54a32d192ed03u64;
            for i in 0..256 {
                x ^= x << 13; x ^= x >> 7; x ^= x << 17;
                let a = if i == 0 {0} else if i == 1 {mask} else {x & mask};
                let b = x.rotate_left(17) & mask;
                assert_eq!(raw_mul_field(&curve,a,b),bitwise_reduce(&curve,bitwise_product(a,b)));
                assert_eq!(raw_square(&curve,a),bitwise_reduce(&curve,bitwise_product(a,a)));
            }
        }
    }
}
