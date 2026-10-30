use crypto_lib::zk::stark_v2::{prove, verify, AirV2, StarkConfig};
use crypto_lib::zk::polynomial::{fr_mul, fr_sub};
use num_bigint::BigUint;
use std::sync::Arc;
fn main() {
    let cfg = StarkConfig::fast();
    let mut air = AirV2::doubling(8, 1);
    air.boundary.push((7, BigUint::from(128u32)));
    let p = prove(&air, &cfg).unwrap();
    assert!(verify(&air, &cfg, &p));
    let mut bad_input = air.clone();
    bad_input.boundary[0].1 = BigUint::from(3u32);
    assert!(!verify(&bad_input, &cfg, &p));
    let mut bad_output = air.clone();
    bad_output.boundary[1].1 = BigUint::from(129u32);
    assert!(!verify(&bad_output, &cfg, &p));
    let mut wrong_linear_air = air.clone();
    wrong_linear_air.transition = Arc::new(|a,b| fr_sub(b, &fr_mul(a, &BigUint::from(3u32))));
    assert!(!verify(&wrong_linear_air, &cfg, &p));
    let mut truncated = p.clone();
    truncated.fri.layer_roots.pop();
    assert!(!verify(&air, &cfg, &truncated));
    let mut swapped = p.clone();
    let j = swapped.trace_openings.iter().position(|o| o.0 != swapped.trace_openings[0].0).unwrap();
    swapped.trace_openings.swap(0,j);
    assert!(!verify(&air, &cfg, &swapped));
    println!("honest=true wrong_input=false wrong_output=false wrong_linear_air=false truncated_fri=false reordered_query=false");
}
