//! Sheriff SHF-20261016-3caa6f re-audit, independent reader "stark" (B2.3, B2.4).
//!
//! New mutation controls for crypto:src/zk/stark.rs (v1) and stark_v2.rs (v2)
//! at crypto 42b9ca8.  Written from the code on disk only (blind to the PR
//! text and commit messages).  Every mutant is a FALSE statement, an invalid
//! proof, or a malleated proof; the verifier must reject each.  Honest rows
//! and "attack_control" rows must be accepted / rejected as stated.
//!
//! Output: one JSON object per line on stdout.  Rate rows ("kind":"rate")
//! measure the v1 escape probability against the documented spot-check
//! bound (1 - k/n)^q.  Seeds are deterministic (sha256 of a tag and index).

use crypto_lib::bls12_381::fq::scalar_modulus;
use crypto_lib::hash::sha256::sha256;
use crypto_lib::zk::merkle::MerkleTree;
use crypto_lib::zk::plonk::primitive_nth_root;
use crypto_lib::zk::polynomial::{fr_add, fr_inv, fr_mul, fr_sub, Poly};
use crypto_lib::zk::stark::{
    self, fri_commit, fri_commit_to, fri_query, query_positions, Air, StarkProof,
};
use crypto_lib::zk::stark_v2::{self, AirV2, StarkConfig, StarkProofV2};
use num_bigint::BigUint;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use std::time::Instant;

type T1 = Arc<dyn Fn(&BigUint) -> BigUint + Send + Sync>;
type T2 = Arc<dyn Fn(&BigUint, &BigUint) -> BigUint + Send + Sync>;

fn big(x: u64) -> BigUint {
    BigUint::from(x)
}
fn one() -> BigUint {
    big(1)
}
fn r() -> BigUint {
    scalar_modulus()
}
fn inv(x: &BigUint) -> BigUint {
    fr_inv(x).expect("invertible")
}
fn esc(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}
fn to_bytes(s: &BigUint) -> Vec<u8> {
    let mut buf = [0u8; 32];
    let b = s.to_bytes_be();
    buf[32 - b.len()..].copy_from_slice(&b);
    buf.to_vec()
}
fn hash_scalar(tag: &str, i: u64) -> BigUint {
    let mut m = tag.as_bytes().to_vec();
    m.extend_from_slice(&i.to_be_bytes());
    BigUint::from_bytes_be(&sha256(&m)) % r()
}

struct Out {
    mutants_accepted: Vec<String>,
    honest_rejected: Vec<String>,
    panics: Vec<String>,
}

impl Out {
    #[allow(clippy::too_many_arguments)]
    fn row(
        &mut self,
        control: &str,
        module: &str,
        class: &str,
        kind: &str,
        statement_true: Option<bool>,
        res: (bool, bool),
        expect_accept: bool,
        detail: &str,
    ) {
        let (accepted, panicked) = res;
        let ok = accepted == expect_accept;
        if !expect_accept && accepted {
            self.mutants_accepted.push(control.to_string());
        }
        if expect_accept && !accepted {
            self.honest_rejected.push(control.to_string());
        }
        if panicked {
            self.panics.push(control.to_string());
        }
        let st = statement_true.map_or("null".to_string(), |b| b.to_string());
        println!(
            "{{\"control\":\"{control}\",\"module\":\"{module}\",\"b2_class\":\"{class}\",\"kind\":\"{kind}\",\"statement_true\":{st},\"verifier_accepted\":{accepted},\"verifier_panicked\":{panicked},\"expected_accept\":{expect_accept},\"ok\":{ok},\"detail\":\"{}\"}}",
            esc(detail)
        );
    }
}

fn guard<F: FnOnce() -> bool>(f: F) -> (bool, bool) {
    match catch_unwind(AssertUnwindSafe(f)) {
        Ok(b) => (b, false),
        Err(_) => (false, true),
    }
}
fn v1v(air: &Air, p: &StarkProof) -> (bool, bool) {
    guard(|| stark::verify(air, p))
}
fn v2v(air: &AirV2, cfg: &StarkConfig, p: &StarkProofV2) -> (bool, bool) {
    guard(|| stark_v2::verify(air, cfg, p))
}

fn subgroup(n: usize) -> Vec<BigUint> {
    let w = primitive_nth_root(n);
    let mut out = Vec::with_capacity(n);
    let mut acc = one();
    for _ in 0..n {
        out.push(acc.clone());
        acc = fr_mul(&acc, &w);
    }
    out
}
fn coset(n: usize) -> Vec<BigUint> {
    subgroup(n).into_iter().map(|x| fr_mul(&x, &big(7))).collect()
}
fn pow_fr(b: &BigUint, k: usize) -> BigUint {
    let mut acc = one();
    for _ in 0..k {
        acc = fr_mul(&acc, b);
    }
    acc
}

// ───────────────────────────── v1 ─────────────────────────────

fn dbl1() -> T1 {
    Arc::new(|x| fr_mul(x, &big(2)))
}
fn trip1() -> T1 {
    Arc::new(|x| fr_mul(x, &big(3)))
}
fn air1(n: usize, start: BigUint, end: BigUint, t: T1) -> Air {
    Air { n, boundary_start: start, boundary_end: end, transition: t }
}
fn doubling_trace(n: usize, start: &BigUint) -> Vec<BigUint> {
    let mut t = vec![start.clone()];
    for i in 1..n {
        let nx = fr_mul(&t[i - 1], &big(2));
        t.push(nx);
    }
    t
}
/// Number of i in [0, n-2] with t[i+1] != 2 t[i].
fn bad_rows(t: &[BigUint]) -> Vec<usize> {
    (0..t.len() - 1).filter(|&i| fr_mul(&t[i], &big(2)) != t[i + 1]).collect()
}

const V1_TAG: &str = "ZK-STARK/v1";

/// Cheating v1 prover: commits to an arbitrary trace, mirrors stark::prove's
/// transcript, and chooses the FRI depth (full fold, or zero folds) and q.
fn forge_v1(trace: &[BigUint], q: usize, full_fri: bool) -> StarkProof {
    let n = trace.len();
    let dom = subgroup(n);
    let leaves: Vec<Vec<u8>> = trace.iter().map(to_bytes).collect();
    let tree = MerkleTree::from_leaves(&leaves);
    let root = tree.root();
    let mut ts = V1_TAG.as_bytes().to_vec();
    ts.extend_from_slice(&root);
    let fri = if full_fri { fri_commit(trace, &dom, &mut ts) } else { fri_commit_to(trace, &dom, &mut ts, n) };
    let pos = query_positions(&mut ts, q, n);
    let open = |p: usize| (p, trace[p].clone(), tree.proof(p).unwrap());
    let fri_queries = pos.iter().map(|&p| (p, fri_query(&fri, p))).collect();
    StarkProof {
        trace_commitment_root: root,
        trace_queries: pos.iter().map(|&p| open(p)).collect(),
        trace_next: pos.iter().map(|&p| open((p + 1) % n)).collect(),
        boundary_openings: vec![open(0), open(n - 1)],
        fri_queries,
        fri,
    }
}
fn v1_pos(p: &StarkProof) -> Vec<usize> {
    p.trace_queries.iter().map(|t| t.0).collect()
}
/// Cheat trace for (start 1, end e) over n = 8 with exactly one broken
/// transition at row k: rows 0..=k double from 1, rows k+1.. double into e.
fn one_break_trace(k: usize, e: &BigUint) -> Vec<BigUint> {
    let n = 8;
    let half = inv(&big(2));
    (0..n)
        .map(|j| if j <= k { big(1u64 << j) } else { fr_mul(e, &pow_fr(&half, n - 1 - j)) })
        .collect()
}

fn run_v1(o: &mut Out) {
    let n = 8;
    let m = "stark_v1";
    let honest = air1(n, big(1), big(128), dbl1());
    let p_h = stark::prove(&honest, 20).unwrap();
    o.row("v1.H0_honest_prove_q20", m, "honest", "honest", Some(true), v1v(&honest, &p_h), true, "stark::prove(doubling 1->128, q=20)");

    // H1: the cheating-prover tool reproduces stark::prove bit for bit.
    let p_f = forge_v1(&honest.execute(), 20, true);
    let same = p_f.trace_commitment_root == p_h.trace_commitment_root
        && p_f.fri.layer_roots == p_h.fri.layer_roots
        && v1_pos(&p_f) == v1_pos(&p_h);
    o.row("v1.H1_forge_tool_reproduces_prove", m, "honest", "honest", Some(true), v1v(&honest, &p_f), true,
        &format!("forge_v1 == stark::prove (roots, FRI roots, positions): {same}"));

    // N1a: one tampered value (row 3 = 99), re-committed; statement 1->128 is
    // TRUE but the witness breaks transitions 2->3 and 3->4.
    let mut t = honest.execute();
    t[3] = big(99);
    let p = forge_v1(&t, 20, true);
    let pos = v1_pos(&p);
    o.row("v1.N1a_tampered_value_recommitted", m, "tampered_trace", "invalid_proof", Some(true), v1v(&honest, &p), false,
        &format!("bad rows {:?}; positions {:?}; escape prob (6/8)^20=0.0032", bad_rows(&t), pos));

    // N1b: the original M1 shape with the producer's prover: 1 -> 12345, one broken transition at row 6.
    let false_air = air1(n, big(1), big(12345), dbl1());
    let cheat = air1(n, big(1), big(12345), Arc::new(|x: &BigUint| if *x == big(64) { big(12345) } else { fr_mul(x, &big(2)) }));
    let forged = stark::prove(&cheat, 20).unwrap();
    let fpos = v1_pos(&forged);
    let first_hit = fpos.iter().position(|&p| p == 6);
    o.row("v1.N1b_false_output_one_broken_row_q20", m, "tampered_trace", "false_statement", Some(false), v1v(&false_air, &forged), false,
        &format!("stark::prove(cheat,20); positions {fpos:?}; first query on row 6 at index {first_hit:?}; row 7 is a no-op position; escape prob (7/8)^20=0.0692"));

    // N2: wrong public input.
    o.row("v1.N2a_wrong_public_output", m, "wrong_public_input", "false_statement", Some(false),
        v1v(&air1(n, big(1), big(129), dbl1()), &p_h), false, "honest 1->128 proof, verifier statement 1->129");
    o.row("v1.N2b_wrong_public_input_start", m, "wrong_public_input", "false_statement", Some(false),
        v1v(&air1(n, big(3), big(128), dbl1()), &p_h), false, "honest 1->128 proof, verifier statement 3->128");

    // N3: wrong AIR.
    o.row("v1.N3a_wrong_air_tripling", m, "wrong_air", "false_statement", Some(false),
        v1v(&air1(n, big(1), big(128), trip1()), &p_h), false, "honest doubling proof, verifier AIR tripling 1->128 (false: 3^7=2187)");
    o.row("v1.N3b_wrong_air_length", m, "wrong_air", "invalid_proof", Some(true),
        v1v(&air1(16, big(1), big(32768), dbl1()), &p_h), false, "n=8 proof, verifier AIR n=16 1->32768");

    // N4: valid proof of a different (true) statement.
    let other = air1(n, big(2), big(256), dbl1());
    let p_o = stark::prove(&other, 20).unwrap();
    o.row("v1.N4_valid_proof_of_other_statement", m, "other_statement", "invalid_proof", Some(true), v1v(&honest, &p_o), false,
        "valid proof of 2->256 presented for 1->128");

    // N5: truncated FRI.
    let mut p = p_h.clone();
    p.fri.layer_roots.pop();
    o.row("v1.N5a_fri_drop_last_root", m, "truncated_fri", "invalid_proof", Some(true), v1v(&honest, &p), false, "pop last FRI layer root");
    let mut p = p_h.clone();
    for fq in p.fri_queries.iter_mut() {
        fq.1.openings.pop();
    }
    o.row("v1.N5b_fri_drop_last_openings", m, "truncated_fri", "invalid_proof", Some(true), v1v(&honest, &p), false, "pop last opening of every FRI query");
    let p = forge_v1(&honest.execute(), 20, false);
    o.row("v1.N5c_fri_zero_folds_rederived", m, "truncated_fri", "invalid_proof", Some(true), v1v(&honest, &p), false,
        "FRI truncated to the trace root alone (fri_commit_to final_size=n), transcript and positions re-derived; v1 docs say FRI adds no soundness, so this is a grinding knob, not a false statement");

    // N6: reordered / duplicated queries.
    let hp = v1_pos(&p_h);
    let j = (1..hp.len()).find(|&j| hp[j] != hp[0]).unwrap();
    let mut p = p_h.clone();
    p.trace_queries.swap(0, j);
    p.trace_next.swap(0, j);
    p.fri_queries.swap(0, j);
    o.row("v1.N6a_reordered_queries", m, "reordered_query", "invalid_proof", Some(true), v1v(&honest, &p), false, &format!("swap queries 0 and {j}"));
    let mut p = p_h.clone();
    p.trace_queries[j] = p.trace_queries[0].clone();
    p.trace_next[j] = p.trace_next[0].clone();
    p.fri_queries[j] = p.fri_queries[0].clone();
    o.row("v1.N6b_duplicated_query", m, "duplicated_query", "invalid_proof", Some(true), v1v(&honest, &p), false, &format!("query {j} replaced by a copy of query 0"));

    // N7: reduced query count (the verifier takes q from the proof).
    let f1 = stark::prove(&cheat, 1).unwrap();
    o.row("v1.N7a_false_output_q1_producer_prover", m, "reduced_query_count", "false_statement", Some(false), v1v(&false_air, &f1), false,
        &format!("stark::prove(cheat, 1): one query at position {:?}; verifier has no minimum q beyond 1; predicted accept prob 7/8", v1_pos(&f1)));
    if let Some(h) = first_hit {
        if h >= 1 {
            let mut p = forged.clone();
            p.trace_queries.truncate(h);
            p.trace_next.truncate(h);
            p.fri_queries.truncate(h);
            o.row("v1.N7b_truncate_rejected_forgery_to_prefix", m, "reduced_query_count", "false_statement", Some(false), v1v(&false_air, &p), false,
                &format!("N1b forgery truncated to its first {h} queries (positions are a prefix-stable function of the transcript)"));
        }
    }

    // N8a: grinding a single broken row with q = 20 fixed (the case the
    // module docs describe): vary the break row k, the encoding of row k+1
    // (v, v+r, v+2r below 2^256), and the FRI depth (full or zero folds).
    let e = big(12345);
    let lim = one() << 256;
    let mut tried = 0usize;
    let mut accepted = Vec::new();
    for k in 0..=6usize {
        let base = one_break_trace(k, &e);
        let mut encs = vec![base.clone()];
        if k + 1 < 7 {
            for mult in 1..=2u64 {
                let w = &base[k + 1] + r() * big(mult);
                if w < lim {
                    let mut t = base.clone();
                    t[k + 1] = w;
                    encs.push(t);
                }
            }
        }
        for (ei, t) in encs.iter().enumerate() {
            for full in [true, false] {
                tried += 1;
                let p = forge_v1(t, 20, full);
                if v1v(&false_air, &p).0 {
                    accepted.push(format!("k={k},enc={ei},full_fri={full}"));
                }
            }
        }
    }
    let res = (!accepted.is_empty(), false);
    o.row("v1.N8a_grind_one_broken_row_q20", m, "grinding", "false_statement", Some(false), res, false,
        &format!("{tried} commitment variants of 1->12345 with one broken row, q=20; accepted variants {accepted:?}; predicted per-variant escape (7/8)^20=0.0692, P(any of {tried})={:.3}",
            1.0 - (1.0 - (7.0f64 / 8.0).powi(20)).powi(tried as i32)));

    // N8b: grinding with two broken rows (rows 2 and 6), free value v, q = 20.
    let tag = "sheriff-SHF-20261016-3caa6f/reader-stark/v1-grind-2row/";
    let t0 = Instant::now();
    let mut found = None;
    for i in 0..20_000u64 {
        let v = hash_scalar(tag, i);
        let t: Vec<BigUint> = vec![big(1), big(2), big(4), v.clone(), fr_mul(&v, &big(2)), fr_mul(&v, &big(4)), fr_mul(&v, &big(8)), big(12345)];
        let p = forge_v1(&t, 20, true);
        if v1v(&false_air, &p).0 {
            found = Some((i + 1, bad_rows(&t)));
            break;
        }
    }
    o.row("v1.N8b_grind_two_broken_rows_q20", m, "grinding", "false_statement", Some(false), (found.is_some(), false), false,
        &format!("attempts until first accepted forgery of 1->12345 (bad rows, attempts) = {found:?}; predicted mean attempts 1/(6/8)^20 = 315; seed tag {tag}; {:.1}s", t0.elapsed().as_secs_f64()));

    // Rate rows: the documented bound (1 - k/n)^q, its decay in q, and a null.
    let mut rate = |name: &str, k_bad: usize, q: usize, trials: u64, mk: &dyn Fn(u64) -> (Air, Vec<BigUint>)| {
        let t0 = Instant::now();
        let mut acc = 0u64;
        for i in 0..trials {
            let (air, t) = mk(i);
            let p = forge_v1(&t, q, true);
            if v1v(&air, &p).0 {
                acc += 1;
            }
        }
        let pred = (1.0 - k_bad as f64 / 8.0).powi(q as i32);
        let nn = trials as f64;
        let sd = (nn * pred * (1.0 - pred)).sqrt();
        let z = if sd > 0.0 { (acc as f64 - nn * pred) / sd } else { 0.0 };
        println!(
            "{{\"control\":\"{name}\",\"module\":\"stark_v1\",\"b2_class\":\"spot_check_bound\",\"kind\":\"rate\",\"k_bad_rows\":{k_bad},\"q\":{q},\"trials\":{trials},\"accepted\":{acc},\"rate\":{:.5},\"predicted_(1-k/n)^q\":{pred:.5},\"z\":{z:.2},\"seconds\":{:.1}}}",
            acc as f64 / nn,
            t0.elapsed().as_secs_f64()
        );
    };
    // Null: honest proofs of true statements s -> 128 s.
    rate("v1.R0_null_honest_k0_q20", 0, 20, 500, &|i| {
        let s = big(1000 + i);
        (air1(8, s.clone(), fr_mul(&s, &big(128)), dbl1()), doubling_trace(8, &s))
    });
    for q in [1usize, 5, 10, 20, 40] {
        rate(&format!("v1.R1_escape_k1_q{q}"), 1, q, 2000, &|i| {
            let e = big(20_000 + i);
            (air1(8, big(1), e.clone(), dbl1()), one_break_trace(6, &e))
        });
    }
    rate("v1.R2_escape_k2_q20", 2, 20, 20_000, &|i| {
        let v = hash_scalar("sheriff-SHF-20261016-3caa6f/reader-stark/v1-rate-2row/", i);
        let t = vec![big(1), big(2), big(4), v.clone(), fr_mul(&v, &big(2)), fr_mul(&v, &big(4)), fr_mul(&v, &big(8)), big(12345)];
        (air1(8, big(1), big(12345), dbl1()), t)
    });

    // Robustness: oversize opened value.
    let mut p = p_h.clone();
    p.trace_queries[0].1 = one() << 300;
    o.row("v1.M1_oversize_opened_value", m, "robustness", "invalid_proof", Some(true), v1v(&honest, &p), false,
        "trace_queries[0] value set to 2^300 (position and leaf_index unchanged): verifier should return false, not panic");
}

// ───────────────────────────── v2 ─────────────────────────────

const V2_TAG: &str = "ZK-STARK-V2/v1";

fn dbl2() -> T2 {
    Arc::new(|p, nx| fr_sub(nx, &fr_mul(p, &big(2))))
}
fn trip2() -> T2 {
    Arc::new(|p, nx| fr_sub(nx, &fr_mul(p, &big(3))))
}
fn air2(n: usize, boundary: Vec<(usize, BigUint)>, t: T2, trace: Vec<BigUint>) -> AirV2 {
    AirV2 { n, boundary, transition: t, generate_trace: Arc::new(move || trace.clone()) }
}
/// Doubling AIR statement truth: all boundaries consistent with t_j = 2^j t_0.
fn doubling_statement_true(n: usize, boundary: &[(usize, BigUint)]) -> bool {
    let half = inv(&big(2));
    let starts: Vec<BigUint> = boundary.iter().map(|(p, v)| fr_mul(v, &pow_fr(&half, *p))).collect();
    let _ = n;
    starts.windows(2).all(|w| w[0] == w[1])
}
fn v2_alphas(tc: &[u8; 32]) -> (BigUint, BigUint, Vec<u8>) {
    let mut t = V2_TAG.as_bytes().to_vec();
    t.extend_from_slice(tc);
    let a1b = sha256(&t);
    t.extend_from_slice(&a1b);
    let a1 = BigUint::from_bytes_be(&a1b) % r();
    let a2b = sha256(&t);
    t.extend_from_slice(&a2b);
    let a2 = BigUint::from_bytes_be(&a2b) % r();
    (a1, a2, t)
}
/// Replica of the module-doc composition (item 2); validated by H1.
fn comp_at(air: &AirV2, h: &[BigUint], x: &BigUint, fx: &BigUint, fwx: &BigUint, a1: &BigUint, a2: &BigUint) -> BigUint {
    let n = air.n;
    let mut xn = x.clone();
    let mut k = 1;
    while k < n {
        xn = fr_mul(&xn, &xn);
        k *= 2;
    }
    let z = fr_mul(&fr_sub(&xn, &one()), &inv(&fr_sub(x, &h[n - 1])));
    let mut acc = fr_mul(a1, &fr_mul(&(air.transition)(fx, fwx), &inv(&z)));
    let mut a2p = one();
    for (p, v) in &air.boundary {
        let term = fr_mul(&fr_sub(fx, v), &inv(&fr_sub(x, &h[*p])));
        acc = fr_add(&acc, &fr_mul(&a2p, &term));
        a2p = fr_mul(&a2p, a2);
    }
    acc
}

#[derive(Default, Clone)]
struct Knobs {
    fri_final: Option<usize>,
    alpha1: Option<BigUint>,
    comp_zero: bool,
    noncanonical_lde: bool,
}

/// Replica of stark_v2::prove with cheating knobs (validated by H1).
fn prove_v2(air: &AirV2, trace: &[BigUint], beta: usize, q: usize, k: &Knobs) -> StarkProofV2 {
    let n = trace.len();
    let h = subgroup(n);
    let pts: Vec<(BigUint, BigUint)> = h.iter().cloned().zip(trace.iter().cloned()).collect();
    let f = Poly::interpolate(&pts);
    let l = n * beta;
    let hl = coset(l);
    let f_lde: Vec<BigUint> = hl.iter().map(|x| f.evaluate(x)).collect();
    let lim = one() << 256;
    let committed: Vec<BigUint> = f_lde
        .iter()
        .map(|v| {
            let w = v + r();
            if k.noncanonical_lde && w < lim { w } else { v.clone() }
        })
        .collect();
    let ttree = MerkleTree::from_leaves(&committed.iter().map(to_bytes).collect::<Vec<_>>());
    let tc = ttree.root();
    let (a1, a2, mut ts) = v2_alphas(&tc);
    let a1u = k.alpha1.clone().unwrap_or(a1);
    let comp: Vec<BigUint> = (0..l)
        .map(|i| if k.comp_zero { BigUint::default() } else { comp_at(air, &h, &hl[i], &f_lde[i], &f_lde[(i + beta) % l], &a1u, &a2) })
        .collect();
    let ctree = MerkleTree::from_leaves(&comp.iter().map(to_bytes).collect::<Vec<_>>());
    let cc = ctree.root();
    ts.extend_from_slice(&cc);
    let fri = fri_commit_to(&comp, &hl, &mut ts, k.fri_final.unwrap_or(beta));
    let pos = query_positions(&mut ts, q, l);
    let open = |tree: &MerkleTree, tab: &[BigUint], p: usize| (p, tab[p].clone(), tree.proof(p).unwrap());
    let fri_openings = pos.iter().map(|&p| (p, fri_query(&fri, p))).collect();
    StarkProofV2 {
        trace_commit: tc,
        composition_commit: cc,
        trace_openings: pos.iter().map(|&p| open(&ttree, &committed, p)).collect(),
        trace_next_openings: pos.iter().map(|&p| open(&ttree, &committed, (p + beta) % l)).collect(),
        composition_openings: pos.iter().map(|&p| open(&ctree, &comp, p)).collect(),
        fri_openings,
        fri,
    }
}
fn v2_pos(p: &StarkProofV2) -> Vec<usize> {
    p.trace_openings.iter().map(|t| t.0).collect()
}

/// Frozen-heart forgery: the transcript never absorbs the boundary values,
/// so the prover commits to a trace that breaks the transition at row p,
/// derives alpha1, alpha2 from the trace commitment, and only then picks
/// the public value v at row p that cancels the composition's pole at
/// omega^p.  The composition is then a polynomial of degree < n, and the
/// producer's own prover emits a proof.
fn frozen_heart(
    n: usize,
    cheat: &[BigUint],
    p: usize,
    other: &[(usize, BigUint)],
    k_index: usize,
    cfg: &StarkConfig,
    nudge: u64,
) -> (AirV2, StarkProofV2, BigUint) {
    let placeholder = air2(n, vec![], dbl2(), cheat.to_vec());
    let tc = stark_v2::prove(&placeholder, cfg).unwrap().trace_commit;
    let (a1, a2, _) = v2_alphas(&tc);
    let h = subgroup(n);
    let mut zp = one();
    for i in 0..=n - 2 {
        if i != p {
            zp = fr_mul(&zp, &fr_sub(&h[p], &h[i]));
        }
    }
    let c_p = fr_sub(&cheat[p + 1], &fr_mul(&cheat[p], &big(2)));
    let v = fr_add(&fr_add(&cheat[p], &fr_mul(&fr_mul(&a1, &c_p), &inv(&fr_mul(&pow_fr(&a2, k_index), &zp)))), &big(nudge));
    let mut boundary = other.to_vec();
    boundary.insert(k_index, (p, v.clone()));
    let air_false = air2(n, boundary, dbl2(), cheat.to_vec());
    let proof = stark_v2::prove(&air_false, cfg).unwrap();
    (air_false, proof, v)
}

fn run_v2(o: &mut Out) {
    let n = 8;
    let m = "stark_v2";
    let cfg = StarkConfig::fast();
    let dcfg = StarkConfig::default();
    let honest_t = doubling_trace(n, &big(1));
    let b2 = vec![(0usize, big(1)), (7usize, big(128))];

    let h1 = AirV2::doubling(n, 1);
    let p_h1 = stark_v2::prove(&h1, &cfg).unwrap();
    o.row("v2.H0a_honest_fast", m, "honest", "honest", Some(true), v2v(&h1, &cfg, &p_h1), true, "AirV2::doubling(8,1), StarkConfig::fast (beta 4, q 20)");
    let p_hd = stark_v2::prove(&h1, &dcfg).unwrap();
    o.row("v2.H0b_honest_default", m, "honest", "honest", Some(true), v2v(&h1, &dcfg, &p_hd), true, "AirV2::doubling(8,1), StarkConfig::default (beta 8, q 80)");
    let a2b = air2(n, b2.clone(), dbl2(), honest_t.clone());
    let p_2b = stark_v2::prove(&a2b, &cfg).unwrap();
    o.row("v2.H0c_honest_two_boundaries", m, "honest", "honest", Some(true), v2v(&a2b, &cfg, &p_2b), true, "doubling, boundaries (0,1),(7,128)");

    // H1: the replica prover reproduces stark_v2::prove bit for bit.
    let p_r = prove_v2(&a2b, &honest_t, cfg.blow_up, cfg.query_count, &Knobs::default());
    let same = p_r.trace_commit == p_2b.trace_commit
        && p_r.composition_commit == p_2b.composition_commit
        && p_r.fri.layer_roots == p_2b.fri.layer_roots
        && p_r.fri.final_constant == p_2b.fri.final_constant
        && v2_pos(&p_r) == v2_pos(&p_2b);
    o.row("v2.H1_replica_prover_reproduces_prove", m, "honest", "honest", Some(true), v2v(&a2b, &cfg, &p_r), true,
        &format!("prove_v2 replica == stark_v2::prove (trace, composition, FRI roots, final constant, positions): {same}"));

    // N1: tampered trace, re-committed with the producer's prover.
    let mut t = honest_t.clone();
    t[3] = big(99);
    let air_t = air2(n, vec![(0, big(1))], dbl2(), t);
    let p = stark_v2::prove(&air_t, &cfg).unwrap();
    o.row("v2.N1a_tampered_value_recommitted", m, "tampered_trace", "invalid_proof", Some(true), v2v(&h1, &cfg, &p), false,
        "trace row 3 = 99 (breaks rows 2->3, 3->4), statement doubling(8,1) true, witness invalid");
    let mut t = honest_t.clone();
    t[7] = big(12345);
    let bf = vec![(0usize, big(1)), (7usize, big(12345))];
    let air_f = air2(n, bf.clone(), dbl2(), t.clone());
    let p = stark_v2::prove(&air_f, &cfg).unwrap();
    o.row("v2.N1b_false_output_one_broken_row", m, "tampered_trace", "false_statement", Some(doubling_statement_true(n, &bf)), v2v(&air_f, &cfg, &p), false,
        "boundaries (0,1),(7,12345); trace [1..64,12345]");

    // N2: wrong public input.
    let w = air2(n, vec![(0, big(1)), (7, big(129))], dbl2(), honest_t.clone());
    o.row("v2.N2a_wrong_public_output", m, "wrong_public_input", "false_statement", Some(false), v2v(&w, &cfg, &p_2b), false, "honest (0,1),(7,128) proof, verifier (0,1),(7,129)");
    let w = air2(n, vec![(0, big(3)), (7, big(128))], dbl2(), honest_t.clone());
    o.row("v2.N2b_wrong_public_input", m, "wrong_public_input", "false_statement", Some(false), v2v(&w, &cfg, &p_2b), false, "honest (0,1),(7,128) proof, verifier (0,3),(7,128)");

    // N3: wrong AIR.
    let w = air2(n, b2.clone(), trip2(), honest_t.clone());
    o.row("v2.N3a_wrong_air_tripling", m, "wrong_air", "false_statement", Some(false), v2v(&w, &cfg, &p_2b), false, "honest doubling proof, verifier AIR tripling with (0,1),(7,128) (false: 3^7 != 128)");
    o.row("v2.N3b_wrong_air_length", m, "wrong_air", "invalid_proof", Some(true), v2v(&AirV2::doubling(16, 1), &cfg, &p_h1), false, "n=8 proof, verifier AIR doubling(16,1)");

    // N4: valid proof of a different statement.
    let p3 = stark_v2::prove(&AirV2::doubling(n, 3), &cfg).unwrap();
    o.row("v2.N4_valid_proof_of_other_statement", m, "other_statement", "invalid_proof", Some(true), v2v(&h1, &cfg, &p3), false, "valid proof of doubling(8,3) presented for doubling(8,1)");

    // N5: truncated FRI.
    let mut p = p_2b.clone();
    p.fri.layer_roots.pop();
    o.row("v2.N5a_fri_drop_last_root", m, "truncated_fri", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, "pop last FRI layer root");
    let mut p = p_2b.clone();
    for fq in p.fri_openings.iter_mut() {
        fq.1.openings.pop();
    }
    o.row("v2.N5b_fri_drop_last_openings", m, "truncated_fri", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, "pop last opening of every FRI query");
    let p = prove_v2(&air_f, &t, cfg.blow_up, cfg.query_count, &Knobs { fri_final: Some(2 * cfg.blow_up), ..Knobs::default() });
    o.row("v2.N5c_fri_one_fold_fewer_rederived", m, "truncated_fri", "false_statement", Some(false), v2v(&air_f, &cfg, &p), false,
        "false statement (0,1),(7,12345); FRI re-derived with one fold fewer (final layer 2*beta)");
    let mut p = p_2b.clone();
    p.fri.final_constant = fr_add(&p.fri.final_constant, &one());
    o.row("v2.N5d_final_constant_tampered", m, "fri_final_layer", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, "final_constant + 1");

    // N6: reordered / duplicated queries.
    let hp = v2_pos(&p_2b);
    let j = (1..hp.len()).find(|&j| hp[j] != hp[0]).unwrap();
    let mut p = p_2b.clone();
    p.trace_openings.swap(0, j);
    p.trace_next_openings.swap(0, j);
    p.composition_openings.swap(0, j);
    p.fri_openings.swap(0, j);
    o.row("v2.N6a_reordered_queries", m, "reordered_query", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, &format!("swap queries 0 and {j}"));
    let mut p = p_2b.clone();
    p.trace_openings[j] = p.trace_openings[0].clone();
    p.trace_next_openings[j] = p.trace_next_openings[0].clone();
    p.composition_openings[j] = p.composition_openings[0].clone();
    p.fri_openings[j] = p.fri_openings[0].clone();
    o.row("v2.N6b_duplicated_query", m, "duplicated_query", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, &format!("query {j} replaced by a copy of query 0"));

    // N7: reduced query count / config mismatch.
    let p = prove_v2(&a2b, &honest_t, cfg.blow_up, 10, &Knobs::default());
    o.row("v2.N7a_prover_q10_verifier_q20", m, "reduced_query_count", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, "proof with 10 queries, verifier config q=20");
    let mut p = p_2b.clone();
    p.trace_openings.truncate(10);
    p.trace_next_openings.truncate(10);
    p.composition_openings.truncate(10);
    p.fri_openings.truncate(10);
    o.row("v2.N7b_truncated_to_10_queries", m, "reduced_query_count", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false, "q=20 proof truncated to its first 10 queries, verifier q=20");
    let c8 = StarkConfig { blow_up: 8, query_count: 20 };
    o.row("v2.N7c_blowup_mismatch", m, "config_mismatch", "invalid_proof", Some(true), v2v(&a2b, &c8, &p_2b), false, "beta=4 proof, verifier beta=8");

    // N8: frozen heart (public input not absorbed before alpha1, alpha2).
    let mut cheat0 = honest_t.clone();
    cheat0[0] = big(5); // breaks transition 0 -> 1 (2 != 10)
    for (name, c) in [("fast", &cfg), ("default", &dcfg)] {
        let (af, pf, v) = frozen_heart(n, &cheat0, 0, &[(7, big(128))], 0, c, 0);
        let st = doubling_statement_true(n, &af.boundary);
        o.row(&format!("v2.N8a_frozen_heart_forged_input_{name}"), m, "fiat_shamir_statement", "false_statement", Some(st), v2v(&af, c, &pf), false,
            &format!("statement: doubling with t0 = v, t7 = 128, v = {v} (true only for v = 1); trace [5,2,4,..,128] breaks row 0; v chosen after alpha1, alpha2; proof from stark_v2::prove"));
    }
    let mut cheat6 = honest_t.clone();
    cheat6[7] = big(999); // breaks transition 6 -> 7
    let (af, pf, v) = frozen_heart(n, &cheat6, 6, &[(0, big(1))], 1, &cfg, 0);
    let st = doubling_statement_true(n, &af.boundary);
    o.row("v2.N8b_frozen_heart_forged_row6", m, "fiat_shamir_statement", "false_statement", Some(st), v2v(&af, &cfg, &pf), false,
        &format!("statement: doubling with t0 = 1, t6 = v, v = {v} (true only for v = 64); trace breaks row 6"));
    let (af, pf, _) = frozen_heart(n, &cheat0, 0, &[(7, big(128))], 0, &cfg, 1);
    o.row("v2.N8c_frozen_heart_control_v_plus_1", m, "fiat_shamir_statement", "attack_control", Some(doubling_statement_true(n, &af.boundary)), v2v(&af, &cfg, &pf), false,
        "same forgery with v + 1: pole no longer cancels, must be rejected (shows N8a acceptance comes from the cancellation)");

    // N9: composition not bound to the trace (prover commits Comp = 0).
    let p = prove_v2(&air_f, &honest_t, cfg.blow_up, cfg.query_count, &Knobs { comp_zero: true, ..Knobs::default() });
    o.row("v2.N9_composition_zero_not_bound", m, "composition_binding", "false_statement", Some(false), v2v(&air_f, &cfg, &p), false,
        "false statement (0,1),(7,12345), honest trace, committed composition = 0 (low degree)");

    // N10: alpha1 not used by the prover (transition dropped from Comp).
    let p = prove_v2(&air_f, &t, cfg.blow_up, cfg.query_count, &Knobs { alpha1: Some(BigUint::default()), ..Knobs::default() });
    o.row("v2.N10_composition_with_alpha1_zero", m, "alpha_binding", "false_statement", Some(false), v2v(&air_f, &cfg, &p), false,
        "false statement (0,1),(7,12345), trace [1..64,12345] satisfies both boundaries; prover builds Comp with alpha1 = 0 (boundary terms only, low degree)");

    // Malleability and robustness.
    let mut p = p_2b.clone();
    let last = p.fri.layer_roots.len() - 1;
    p.fri.layer_roots[last] = [0u8; 32];
    o.row("v2.M1_last_fri_root_garbage", m, "malleability", "malleated_proof", Some(true), v2v(&a2b, &cfg, &p), false,
        "last FRI layer root replaced by zeros (never absorbed, never opened)");
    let p = prove_v2(&a2b, &honest_t, cfg.blow_up, cfg.query_count, &Knobs { noncanonical_lde: true, ..Knobs::default() });
    o.row("v2.M2_noncanonical_trace_encoding", m, "malleability", "malleated_proof", Some(true), v2v(&a2b, &cfg, &p), false,
        "trace LDE leaves committed as v + r where < 2^256 (non-canonical field encodings): new trace commitment, new alphas and positions, same field values");
    let mut p = p_2b.clone();
    p.trace_openings[0].1 = one() << 300;
    o.row("v2.M3_oversize_opened_value", m, "robustness", "invalid_proof", Some(true), v2v(&a2b, &cfg, &p), false,
        "trace_openings[0] value set to 2^300: verifier should return false, not panic");
}

fn main() {
    std::panic::set_hook(Box::new(|info| eprintln!("[caught panic] {info}")));
    let mut o = Out { mutants_accepted: vec![], honest_rejected: vec![], panics: vec![] };
    let t0 = Instant::now();
    run_v2(&mut o);
    run_v1(&mut o);
    println!(
        "{{\"summary\":true,\"crypto_rev\":\"42b9ca8a5aff5743c42c337f52ddd8bc8612cb59\",\"mutants_accepted\":{:?},\"honest_rejected\":{:?},\"verifier_panics\":{:?},\"seconds\":{:.1}}}",
        o.mutants_accepted, o.honest_rejected, o.panics, t0.elapsed().as_secs_f64()
    );
}
