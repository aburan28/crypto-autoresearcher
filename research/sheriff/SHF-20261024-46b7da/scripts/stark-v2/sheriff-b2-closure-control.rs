use crypto_lib::zk::stark_v2::{air_fingerprint, prove, verify, AirV2, StarkConfig};
use crypto_lib::zk::polynomial::{fr_add, fr_mul, fr_sub};
use num_bigint::BigUint;
use std::sync::Arc;
fn main() {
    let one = BigUint::from(1u32);
    let two = BigUint::from(2u32);
    let mut honest = AirV2::doubling(8, 1);
    honest.boundary.push((7, BigUint::from(128u32)));
    let mut false_air = honest.clone();
    let one_c = one.clone();
    let two_c = two.clone();
    false_air.transition = Arc::new(move |a, b| {
        let base = fr_sub(b, &fr_mul(a, &two_c));
        if a == &one_c && b == &two_c { fr_add(&base, &one_c) } else { base }
    });
    assert_eq!(air_fingerprint(&honest), air_fingerprint(&false_air));
    let trace = (honest.generate_trace)();
    let first_pair_constraint = (false_air.transition)(&trace[0], &trace[1]);
    assert_eq!(first_pair_constraint, one);
    for cfg in [StarkConfig::fast(), StarkConfig::default()] {
        let p = prove(&honest, &cfg).unwrap();
        let honest_accepted = verify(&honest, &cfg, &p);
        let false_accepted = verify(&false_air, &cfg, &p);
        let pf = prove(&false_air, &cfg).unwrap();
        let false_self_accepted = verify(&false_air, &cfg, &pf);
        println!("n={} beta={} q={} fingerprint_equal=true false_air_row0_constraint={} honest_accepted={} false_accepted={} false_self_accepted={}", honest.n, cfg.blow_up, cfg.query_count, first_pair_constraint, honest_accepted, false_accepted, false_self_accepted);
    }
}
