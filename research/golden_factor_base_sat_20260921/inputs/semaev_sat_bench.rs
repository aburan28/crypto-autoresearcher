//! Measure what each modelling and solver choice costs the SAT
//! pipeline for binary-Semaev index calculus.
//!
//! Axes measured:
//!
//! 1. **Parity encoding** — native XOR rows (Gauss-Jordan inside the
//!    solver) versus Tseitin expansion into CNF.
//! 2. **Factor base** — confining the unknowns to an `l`-dimensional
//!    subspace instead of all of `F_{2ⁿ}`.
//! 3. **Symmetry breaking** — whether the `3!` orderings of
//!    `(X₁, X₂, X₃)` are all explored.
//! 4. **Scale** — how the symmetrised `S₄` solve grows with `l`.
//!
//! ```bash
//! cargo run --release --example semaev_sat_bench
//! ```

use crypto_lib::binary_ecc::{F2mElement, IrreduciblePoly};
use crypto_lib::cryptanalysis::binary_semaev::binary_semaev_s3;
use crypto_lib::cryptanalysis::binary_semaev_s4::{elementary_symmetric_3, symmetrised_s4_eval};
use crypto_lib::cryptanalysis::sat::SolveResult;
use crypto_lib::cryptanalysis::semaev_corpus::CORPUS;
use crypto_lib::cryptanalysis::semaev_sat::{
    decode_x1_x2, encode_semaev_s3_subspace, encode_semaev_s4_with, S4Options, XorEncoding,
};
use std::time::{Duration, Instant};

fn irr_for(n: u32) -> IrreduciblePoly {
    let low = match n {
        4 => vec![0, 1],
        5 => vec![0, 2],
        6 => vec![0, 1],
        7 => vec![0, 1],
        8 => vec![0, 2, 3, 4],
        9 => vec![0, 1],
        10 => vec![0, 3],
        11 => vec![0, 2],
        12 => vec![0, 1, 2, 3],
        13 => vec![0, 1, 3, 4],
        15 => vec![0, 2, 4, 5],
        17 => vec![0, 3],
        19 => vec![0, 1, 2, 5],
        _ => panic!("no irreducible tabulated for n = {n}"),
    };
    IrreduciblePoly {
        degree: n,
        low_terms: low,
    }
}

/// Build a `b` that puts `X₁ = X₂ = x₃` on the `S₃` variety, so the
/// instance is known-SAT.
fn planted_s3(irr: &IrreduciblePoly, x3: &F2mElement) -> F2mElement {
    let x3_2 = x3.square(irr);
    let x3_3 = x3_2.mul(x3, irr);
    let x3_4 = x3_3.mul(x3, irr);
    x3_3.add(&x3_4)
}

/// Find an `x_R` that genuinely decomposes over the `l`-dimensional
/// factor base, by exhaustive search.  Used for the small ladder rungs
/// the reference corpus does not cover.
fn find_decomposable(n: u32, l: u32, irr: &IrreduciblePoly) -> F2mElement {
    let elt = |v: u32| {
        let bits: Vec<u32> = (0..l).filter(|j| (v >> j) & 1 == 1).collect();
        F2mElement::from_bit_positions(&bits, n)
    };
    let span = 1u32 << l;
    for r in 1..(1u32 << n) {
        let bits: Vec<u32> = (0..n).filter(|j| (r >> j) & 1 == 1).collect();
        let x_r = F2mElement::from_bit_positions(&bits, n);
        for a in 0..span {
            let xa = elt(a);
            for b in a..span {
                let xb = elt(b);
                for c in b..span {
                    let (e1, e2, e3) = elementary_symmetric_3(&xa, &xb, &elt(c), irr);
                    if symmetrised_s4_eval(&e1, &e2, &e3, &x_r, irr).is_zero() {
                        return x_r;
                    }
                }
            }
        }
    }
    panic!("no decomposable target for n = {n}, l = {l}");
}

fn fmt(d: Duration) -> String {
    if d.as_secs_f64() >= 1.0 {
        format!("{:.1}s", d.as_secs_f64())
    } else if d.as_micros() >= 1000 {
        format!("{:.0}ms", d.as_secs_f64() * 1e3)
    } else {
        format!("{}µs", d.as_micros())
    }
}

fn header() {
    println!(
        "  {:<15} {:<8} {:>6} {:>8} {:>5} {:>10} {:>10} {:>9}  {}",
        "params", "parity", "vars", "clauses", "rows", "decisions", "conflicts", "solve", "result"
    );
}

fn run_s3(n: u32, l: u32, encoding: XorEncoding) {
    let irr = irr_for(n);
    let x3 = F2mElement::from_bit_positions(&[1, 3], n);
    let b = planted_s3(&irr, &x3);
    let mut enc = encode_semaev_s3_subspace(n, l, &irr, &b, &x3, encoding);
    let (vars, clauses, rows) = (
        enc.solver.n_vars(),
        enc.solver.n_clauses(),
        enc.solver.n_xors(),
    );
    enc.solver.conflict_budget = 5_000_000;
    let t = Instant::now();
    let res = enc.solver.solve();
    let solve = t.elapsed();
    let st = enc.solver.stats;
    let verdict = match res {
        SolveResult::Sat => {
            let (x1, x2) = decode_x1_x2(&enc);
            if binary_semaev_s3(&x1, &x2, &x3, &b, &irr).is_zero() {
                "SAT (verified)"
            } else {
                "SAT (BAD DECODE)"
            }
        }
        SolveResult::Unsat => "UNSAT",
        SolveResult::Unknown => "budget hit",
    };
    println!(
        "  S₃ n={n:<2} l={l:<7} {:<8} {vars:>6} {clauses:>8} {rows:>5} {:>10} {:>10} {:>9}  {verdict}",
        match encoding {
            XorEncoding::Native => "native",
            XorEncoding::Cnf => "cnf",
        },
        st.decisions,
        st.conflicts,
        fmt(solve)
    );
}

fn run_s4(label: &str, n: u32, l: u32, x_r: &F2mElement, opts: S4Options, solve_it: bool) {
    let irr = irr_for(n);
    let b = F2mElement::one(n);
    let enc0 = Instant::now();
    let mut enc = encode_semaev_s4_with(n, l, &irr, &b, x_r, opts);
    let build = enc0.elapsed();
    let (vars, clauses, rows) = (
        enc.solver.n_vars(),
        enc.solver.n_clauses(),
        enc.solver.n_xors(),
    );
    if !solve_it {
        println!(
            "  {label:<15} {:<8} {vars:>6} {clauses:>8} {rows:>5} {:>10} {:>10} {:>9}  (encode {})",
            match opts.encoding {
                XorEncoding::Native => "native",
                XorEncoding::Cnf => "cnf",
            },
            "-",
            "-",
            "-",
            fmt(build)
        );
        return;
    }
    enc.solver.conflict_budget = 40_000_000;
    let t = Instant::now();
    let res = enc.solver.solve();
    let solve = t.elapsed();
    let st = enc.solver.stats;
    let verdict = match res {
        SolveResult::Sat => {
            let xs = enc.decode();
            let (e1, e2, e3) = elementary_symmetric_3(&xs[0], &xs[1], &xs[2], &irr);
            if symmetrised_s4_eval(&e1, &e2, &e3, x_r, &irr).is_zero() {
                "SAT (verified)".to_string()
            } else {
                "SAT (BAD DECODE)".to_string()
            }
        }
        SolveResult::Unsat => "UNSAT".to_string(),
        SolveResult::Unknown => "budget hit".to_string(),
    };
    println!(
        "  {label:<15} {:<8} {vars:>6} {clauses:>8} {rows:>5} {:>10} {:>10} {:>9}  {verdict}",
        match opts.encoding {
            XorEncoding::Native => "native",
            XorEncoding::Cnf => "cnf",
        },
        st.decisions,
        st.conflicts,
        fmt(solve)
    );
}

/// The target x-coordinate of a corpus instance by name.
fn corpus_target(name: &str) -> (u32, u32, F2mElement) {
    let inst = CORPUS
        .iter()
        .find(|c| c.name == name)
        .unwrap_or_else(|| panic!("no corpus instance {name}"));
    (inst.n, inst.l, inst.x_r())
}

/// Solve every satisfiable instance of one corpus family under one
/// configuration, and report the aggregate.
///
/// Per-instance timings on satisfiable instances are dominated by
/// search-trajectory luck — the same change can be 10× better on one
/// instance and 5× worse on the next — so a single instance says
/// almost nothing.  These numbers are over all ten.
fn run_family(family: &str, opts: S4Options) -> (usize, Duration, Duration, u64) {
    let mut times: Vec<Duration> = Vec::new();
    let mut total = Duration::ZERO;
    let mut conflicts = 0u64;
    let mut solved = 0usize;
    for inst in CORPUS
        .iter()
        .filter(|c| c.name.starts_with(family) && c.truly_sat)
    {
        let irr = inst.irr();
        let mut enc = encode_semaev_s4_with(inst.n, inst.l, &irr, &inst.b(), &inst.x_r(), opts);
        enc.solver.conflict_budget = 40_000_000;
        let t = Instant::now();
        let res = enc.solver.solve();
        let dt = t.elapsed();
        assert_eq!(res, SolveResult::Sat, "{} must be satisfiable", inst.name);
        let xs = enc.decode();
        let (e1, e2, e3) = elementary_symmetric_3(&xs[0], &xs[1], &xs[2], &irr);
        assert!(
            symmetrised_s4_eval(&e1, &e2, &e3, &inst.x_r(), &irr).is_zero(),
            "{}: decoded triple must decompose the target",
            inst.name
        );
        conflicts += enc.solver.stats.conflicts;
        total += dt;
        times.push(dt);
        solved += 1;
    }
    times.sort();
    let median = times[times.len() / 2];
    (solved, total, median, conflicts)
}

fn main() {
    println!("\n=== S₃ · parity encoding, unrestricted (l = n) ===");
    header();
    for n in [5u32, 6, 7] {
        run_s3(n, n, XorEncoding::Cnf);
        run_s3(n, n, XorEncoding::Native);
    }

    println!("\n=== S₃ · factor base l = ⌈n/2⌉ ===");
    header();
    for n in [8u32, 10, 12] {
        let l = n.div_ceil(2);
        run_s3(n, l, XorEncoding::Cnf);
        run_s3(n, l, XorEncoding::Native);
    }

    println!("\n=== symmetrised S₄ · every satisfiable corpus instance ===");
    println!(
        "  {:<10} {:<10} {:>7} {:>12} {:>12} {:>14}",
        "family", "symmetry", "solved", "total", "median", "conflicts"
    );
    for family in ["n15l5", "n17l6", "n19l6"] {
        for (label, break_symmetry) in [("off", false), ("on", true)] {
            let (solved, total, median, conflicts) = run_family(
                family,
                S4Options {
                    encoding: XorEncoding::Native,
                    break_symmetry,
                },
            );
            println!(
                "  {family:<10} {label:<10} {solved:>7} {:>12} {:>12} {conflicts:>14}",
                fmt(total),
                fmt(median)
            );
        }
    }

    println!("\n=== symmetrised S₄ · encoding size, n = 19 ===");
    header();
    let (n, l, x_r) = corpus_target("n19l6-1-S");
    run_s4(
        "n19l6 cnf",
        n,
        l,
        &x_r,
        S4Options {
            encoding: XorEncoding::Cnf,
            break_symmetry: false,
        },
        false,
    );
    run_s4(
        "n19l6 native",
        n,
        l,
        &x_r,
        S4Options {
            encoding: XorEncoding::Native,
            break_symmetry: false,
        },
        false,
    );
    println!();
}
