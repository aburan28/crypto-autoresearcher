//! Sheriff B2 mutation controls for crypto:src/zk/stark.rs and stark_v2.rs.
//!
//! A verifier is sound only if it rejects proofs of false statements. Each
//! control below builds a proof of a statement that is FALSE (checked with
//! the AIR's own `check_trace`, or by construction) and asks the verifier.
//! The honest controls must verify; every mutant must be rejected. Output is
//! one JSON object per line; the exit code is the number of mutants accepted.

use crypto_lib::zk::polynomial::fr_mul;
use crypto_lib::zk::stark::{self, Air, FriCommitment, StarkProof};
use crypto_lib::zk::stark_v2::{self, AirV2, StarkConfig, StarkProofV2};
use num_bigint::BigUint;
use std::sync::Arc;

fn big(x: u64) -> BigUint {
    BigUint::from(x)
}

fn doubling(n: usize, start: u64, end: u64) -> Air {
    Air {
        n,
        boundary_start: big(start),
        boundary_end: big(end),
        transition: Arc::new(|x| fr_mul(x, &big(2))),
    }
}

fn empty_fri() -> FriCommitment {
    FriCommitment { layer_roots: vec![[0u8; 32]], final_constant: big(0), layers: vec![], layer_trees: vec![] }
}

fn report(name: &str, statement_true: bool, accepted: bool, expect_accept: bool) -> u32 {
    let ok = accepted == expect_accept;
    println!(
        "{{\"control\":\"{name}\",\"statement_true\":{statement_true},\"verifier_accepted\":{accepted},\"expected_accept\":{expect_accept},\"ok\":{ok}}}"
    );
    u32::from(!expect_accept && accepted)
}

fn main() {
    let mut accepted_mutants = 0;
    let n = 8;

    // ---- stark.rs (v1) ----
    let honest = doubling(n, 1, 128);
    let p = stark::prove(&honest, 20).expect("power-of-two n");
    accepted_mutants += report("v1.honest", honest.check_trace(&honest.execute()), stark::verify(&honest, &p), true);

    // M1: false public output. 1 doubled 7 times is 128, not 12345. The prover
    // commits to a trace that obeys the boundaries but breaks one transition.
    let false_air = doubling(n, 1, 12345);
    let cheat = Air {
        n,
        boundary_start: big(1),
        boundary_end: big(12345),
        transition: Arc::new(|x| if *x == big(64) { big(12345) } else { fr_mul(x, &big(2)) }),
    };
    let forged = stark::prove(&cheat, 20).expect("power-of-two n");
    let truth = false_air.check_trace(&cheat.execute());
    accepted_mutants += report("v1.M1_false_output_broken_transition", truth, stark::verify(&false_air, &forged), false);

    // M2: an empty proof (no queries) for the same false statement.
    let empty = StarkProof { trace_commitment_root: [0u8; 32], fri: empty_fri(), trace_queries: vec![], fri_queries: vec![] };
    accepted_mutants += report("v1.M2_empty_proof", false, stark::verify(&false_air, &empty), false);

    // ---- stark_v2.rs ----
    let cfg = StarkConfig::fast();
    let honest2 = AirV2::doubling(n, 1);
    let p2 = stark_v2::prove(&honest2, &cfg).expect("prove");
    accepted_mutants += report("v2.honest", true, stark_v2::verify(&honest2, &cfg, &p2), true);

    // M3: the honest proof (trace starts at 1) presented for a different
    // statement (trace starts at 5).
    let false2 = AirV2::doubling(n, 5);
    accepted_mutants += report("v2.M3_proof_reused_for_other_boundary", false, stark_v2::verify(&false2, &cfg, &p2), false);

    // M4: an empty proof for the false statement.
    let empty2 = StarkProofV2 {
        trace_commit: [0u8; 32],
        composition_commit: [0u8; 32],
        fri: empty_fri(),
        trace_openings: vec![],
        composition_openings: vec![],
        fri_openings: vec![],
    };
    accepted_mutants += report("v2.M4_empty_proof", false, stark_v2::verify(&false2, &cfg, &empty2), false);

    std::process::exit(accepted_mutants as i32);
}
