//! Fallback replay (NOT `cargo test`): the 18 `#[test]` bodies of
//! crypto:src/zk/stark.rs and stark_v2.rs at 42b9ca8, transcribed through the
//! public API because the sparse checkout cannot compile the lib test target.
//! One JSON line per test; a panic or false assertion is a failure.
use crypto_lib::zk::plonk::primitive_nth_root;
use crypto_lib::zk::polynomial::{fr_mul, Poly};
use crypto_lib::zk::stark::*;
use crypto_lib::zk::stark_v2::{self, AirV2, StarkConfig};
use num_bigint::BigUint;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;

fn doubling_air(n: usize, start: u64) -> Air {
    let trace_target = start * (1u64 << (n - 1));
    let transition: Arc<dyn Fn(&BigUint) -> BigUint + Send + Sync> = Arc::new(|x| fr_mul(x, &BigUint::from(2u32)));
    Air { n, boundary_start: BigUint::from(start), boundary_end: BigUint::from(trace_target), transition }
}
fn run(name: &str, f: impl FnOnce() -> bool) -> bool {
    let ok = matches!(catch_unwind(AssertUnwindSafe(f)), Ok(true));
    println!("{{\"test\":\"{name}\",\"passed\":{ok}}}");
    ok
}
fn main() {
    std::panic::set_hook(Box::new(|i| eprintln!("[panic] {i}")));
    let mut pass = 0; let mut total = 0;
    let mut t = |name: &str, f: Box<dyn FnOnce() -> bool>| { total += 1; if run(name, f) { pass += 1; } };
    // ---- zk::stark::tests ----
    t("zk::stark::tests::air_execution_doubling", Box::new(|| { let air = doubling_air(8, 1); let tr = air.execute(); let e: Vec<BigUint> = (0..8).map(|i| BigUint::from(1u64 << i)).collect(); tr == e && air.check_trace(&tr) }));
    t("zk::stark::tests::air_check_rejects_bad_trace", Box::new(|| { let air = doubling_air(8, 1); let mut tr = air.execute(); tr[3] = BigUint::from(99u32); !air.check_trace(&tr) }));
    t("zk::stark::tests::fri_commit_and_verify_polynomial", Box::new(|| {
        let n = 16; let omega = primitive_nth_root(n); let mut domain = Vec::new(); let mut acc = BigUint::from(1u32);
        for _ in 0..n { domain.push(acc.clone()); acc = fr_mul(&acc, &omega); }
        let p = Poly::from_coeffs(vec![BigUint::from(1u32), BigUint::from(2u32), BigUint::from(3u32)]);
        let evals: Vec<BigUint> = domain.iter().map(|x| p.evaluate(x)).collect();
        let mut ts = b"FRI-TEST".to_vec(); let init = ts.clone();
        let c = fri_commit(&evals, &domain, &mut ts);
        let qs: Vec<(usize, FriQueryOpening)> = [0usize, 3, 7].iter().map(|&p| (p, fri_query(&c, p))).collect();
        fri_verify(&c, &domain, &qs, &init) }));
    t("zk::stark::tests::stark_prove_verify_doubling", Box::new(|| { let air = doubling_air(8, 1); let p = prove(&air, 3).unwrap(); verify(&air, &p) }));
    t("zk::stark::tests::rejects_false_output_with_broken_transition", Box::new(|| {
        let false_air = Air { boundary_end: BigUint::from(12345u32), ..doubling_air(8, 1) };
        if false_air.check_trace(&false_air.execute()) { return false; }
        let cheat = Air { transition: Arc::new(|x: &BigUint| if *x == BigUint::from(64u32) { BigUint::from(12345u32) } else { fr_mul(x, &BigUint::from(2u32)) }), ..false_air.clone() };
        let forged = prove(&cheat, 64).unwrap(); !verify(&false_air, &forged) }));
    t("zk::stark::tests::rejects_empty_proof", Box::new(|| { let air = doubling_air(8, 1); let mut p = prove(&air, 8).unwrap(); p.trace_queries.clear(); p.trace_next.clear(); p.fri_queries.clear(); !verify(&air, &p) }));
    t("zk::stark::tests::rejects_proof_for_another_output", Box::new(|| { let p = prove(&doubling_air(8, 1), 8).unwrap(); let other = Air { boundary_end: BigUint::from(256u32), ..doubling_air(8, 1) }; !verify(&other, &p) }));
    t("zk::stark::tests::rejects_moved_query_position", Box::new(|| { let air = doubling_air(8, 1); let mut p = prove(&air, 8).unwrap(); let (pos, _, _) = p.trace_queries[0].clone(); let moved = (pos + 1) % 8; p.trace_queries[0] = (moved, air.execute()[moved].clone(), p.trace_queries[0].2.clone()); !verify(&air, &p) }));
    // ---- zk::stark_v2::tests ----
    t("zk::stark_v2::tests::air_doubling_generates_powers_of_two", Box::new(|| { let air = AirV2::doubling(8, 3); let tr = (air.generate_trace)(); tr == (0..8).map(|i| BigUint::from(3 * (1u64 << i))).collect::<Vec<_>>() }));
    t("zk::stark_v2::tests::air_transition_zero_on_valid_pair", Box::new(|| { let air = AirV2::doubling(8, 3); (air.transition)(&BigUint::from(3u32), &BigUint::from(6u32)) == BigUint::default() }));
    t("zk::stark_v2::tests::air_transition_nonzero_on_invalid_pair", Box::new(|| { let air = AirV2::doubling(8, 3); (air.transition)(&BigUint::from(3u32), &BigUint::from(7u32)) != BigUint::default() }));
    t("zk::stark_v2::tests::stark_v2_prove_verify_doubling_fast", Box::new(|| { let air = AirV2::doubling(8, 1); let c = StarkConfig::fast(); let p = stark_v2::prove(&air, &c).unwrap(); stark_v2::verify(&air, &c, &p) }));
    t("zk::stark_v2::tests::stark_v2_prove_verify_doubling_default", Box::new(|| { let air = AirV2::doubling(16, 3); let c = StarkConfig::default(); let p = stark_v2::prove(&air, &c).unwrap(); stark_v2::verify(&air, &c, &p) }));
    t("zk::stark_v2::tests::rejects_proof_reused_for_another_boundary", Box::new(|| { let c = StarkConfig::fast(); let p = stark_v2::prove(&AirV2::doubling(8, 1), &c).unwrap(); !stark_v2::verify(&AirV2::doubling(8, 5), &c, &p) }));
    t("zk::stark_v2::tests::rejects_empty_proof", Box::new(|| { let air = AirV2::doubling(8, 1); let c = StarkConfig::fast(); let mut p = stark_v2::prove(&air, &c).unwrap(); p.trace_openings.clear(); p.trace_next_openings.clear(); p.composition_openings.clear(); p.fri_openings.clear(); !stark_v2::verify(&air, &c, &p) }));
    t("zk::stark_v2::tests::rejects_trace_with_broken_transition", Box::new(|| { let c = StarkConfig::fast(); let mut cheat = AirV2::doubling(8, 1); cheat.generate_trace = Arc::new(|| { let mut t: Vec<BigUint> = (0..8).map(|i| BigUint::from(1u64 << i)).collect(); t[5] = BigUint::from(33u32); t }); let f = stark_v2::prove(&cheat, &c).unwrap(); !stark_v2::verify(&AirV2::doubling(8, 1), &c, &f) }));
    t("zk::stark_v2::tests::rejects_truncated_fri", Box::new(|| { let air = AirV2::doubling(8, 1); let c = StarkConfig::fast(); let mut p = stark_v2::prove(&air, &c).unwrap(); p.fri.layer_roots.pop(); !stark_v2::verify(&air, &c, &p) }));
    t("zk::stark_v2::tests::rejects_swapped_queries", Box::new(|| { let air = AirV2::doubling(8, 1); let c = StarkConfig::fast(); let mut p = stark_v2::prove(&air, &c).unwrap();
        let b = (1..c.query_count).find(|&j| p.trace_openings[j].0 != p.trace_openings[0].0).unwrap();
        p.trace_openings.swap(0, b); p.trace_next_openings.swap(0, b); p.composition_openings.swap(0, b); p.fri_openings.swap(0, b); !stark_v2::verify(&air, &c, &p) }));
    println!("{{\"summary\":true,\"passed\":{pass},\"total\":{total},\"note\":\"transcribed replay, not cargo test\"}}");
}
