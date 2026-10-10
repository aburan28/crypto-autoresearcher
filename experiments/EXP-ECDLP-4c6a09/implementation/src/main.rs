//! EXP-ECDLP-4c6a09 (H-ECDLP-4da36f, SNFS-G3): Solinas number fields.
//!
//! For the four NIST low-weight shapes f and toy primes p = f(2^k), lift seeded curves E/Q to
//! K_f = Q[t]/(f), enumerate K_f-points by a sieved sup-norm-shell search, reduce them at the
//! degree-one prime (t - 2^k, p) and measure distinct residues D(W), the covering exponent gamma,
//! the count of proven non-torsion new points and the smallest naive height over log p, against
//! random monic g of the same degree and weight, f = t^d - c (the EXP-ECDLP-3e8403 form) and Q;
//! regress gamma on log root discriminant with a bootstrap interval. The rank arm is skipped and
//! reported as skipped (no 2-descent over number fields is available). Observations only.

use nfield::ecnf::{self, CurveNF, Event};
use nfield::field::{big, is_irreducible_over_q, is_prime_big, ln_big, rat, NumberField};
use nfield::{gp, Rng};
use num_bigint::{BigInt, BigUint};
use num_traits::{Signed, ToPrimitive, Zero};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, HashSet};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

const EXP: &str = "EXP-ECDLP-4c6a09";
const HYP: &str = "H-ECDLP-4da36f";

/// NIST shapes, low -> high coefficients; p = f(2^k) is the NIST prime at the listed k.
fn nist_shapes() -> Vec<(&'static str, Vec<i64>)> {
    vec![
        ("P-192", vec![-1, -1, 0, 1]),                                 // t^3 - t - 1,               k = 64
        ("P-224", vec![1, 0, 0, -1, 0, 0, 0, 1]),                      // t^7 - t^3 + 1,             k = 32
        ("P-256", vec![-1, 0, 0, 1, 0, 0, 1, -1, 1]),                  // t^8 - t^7 + t^6 + t^3 - 1, k = 32
        ("P-384", vec![-1, 1, 0, -1, -1, 0, 0, 0, 0, 0, 0, 0, 1]),     // t^12 - t^4 - t^3 + t - 1,  k = 32
    ]
}

/// CTRL-SHAPE: each shape evaluated at its deployed k must give the public NIST prime (FIPS 186-4,
/// D.1.2). Public parameters, used only to pin the polynomial shapes; the cells use toy primes.
fn nist_primes() -> Vec<(&'static str, u32, BigUint)> {
    let two = BigUint::from(2u32);
    vec![
        ("P-192", 64, two.pow(192) - two.pow(64) - BigUint::from(1u32)),
        ("P-224", 32, two.pow(224) - two.pow(96) + BigUint::from(1u32)),
        ("P-256", 32, two.pow(256) - two.pow(224) + two.pow(192) + two.pow(96) - BigUint::from(1u32)),
        ("P-384", 32, two.pow(384) - two.pow(128) - two.pow(96) + two.pow(32) - BigUint::from(1u32)),
    ]
}

fn poly_eval(g: &[i64], x: &BigInt) -> BigInt {
    let mut v = BigInt::zero();
    for &c in g.iter().rev() {
        v = v * x + big(c);
    }
    v
}

fn check_shapes() -> bool {
    let shapes = nist_shapes();
    for (name, k, prime) in nist_primes() {
        let g = &shapes.iter().find(|(n, _)| *n == name).unwrap().1;
        let v = poly_eval(g, &big(2).pow(k));
        assert!(v == BigInt::from(prime), "CTRL-SHAPE failed for {}", name);
    }
    true
}

fn poly_text(g: &[i64]) -> String {
    let mut terms: Vec<String> = Vec::new();
    for i in (0..g.len()).rev() {
        let c = g[i];
        if c == 0 {
            continue;
        }
        let mono = if i == 0 { "1".to_string() } else if i == 1 { "t".to_string() } else { format!("t^{}", i) };
        let sign = if c < 0 { "-" } else { "+" };
        if c.abs() == 1 && i > 0 {
            terms.push(format!("{}{}", sign, mono));
        } else {
            terms.push(format!("{}{}{}", sign, c.abs(), if i == 0 { String::new() } else { format!("*{}", mono) }));
        }
    }
    let s = terms.join(" ");
    if let Some(stripped) = s.strip_prefix('+') { stripped.to_string() } else { s }
}

fn weight(g: &[i64]) -> usize {
    g.iter().filter(|&&c| c != 0).count()
}

fn toy_primes_for(g: &[i64], kmin: u32, kmax: u32, min_bits: u64) -> Vec<(u32, BigUint)> {
    let mut out = Vec::new();
    for k in kmin..=kmax {
        let p = poly_eval(g, &big(2).pow(k));
        if p.is_positive() {
            let pu = p.to_biguint().unwrap();
            if pu >= BigUint::from(2u32).pow(min_bits as u32) && is_prime_big(&pu) {
                out.push((k, pu));
            }
        }
    }
    out
}

fn random_shape(d: usize, w: usize, rng: &mut Rng) -> Vec<i64> {
    loop {
        let mut g = vec![0i64; d + 1];
        g[d] = 1;
        g[0] = rng.choice(&[-1, 1]);
        let idx = if w > 2 { rng.sample(d - 1, w - 2) } else { vec![] };
        for i in idx {
            g[i + 1] = rng.choice(&[-1, 1]);
        }
        let gb: Vec<BigInt> = g.iter().map(|&c| big(c)).collect();
        if !NumberField::new(gb.clone()).discriminant().is_zero() && is_irreducible_over_q(&gb) == Some(true) {
            return g;
        }
    }
}

/// n seeded curves y^2 = x^3 + A x + B with A, B in [-20, 20], nonsingular with good reduction at p.
fn seeded_curves(n: usize, p: &BigUint, rng: &mut Rng) -> Vec<(i64, i64)> {
    let pb = BigInt::from(p.clone());
    let mut out = Vec::new();
    while out.len() < n {
        let a = rng.range(-20, 20);
        let b = rng.range(-20, 20);
        let disc = big(4) * big(a).pow(3) + big(27) * big(b).pow(2);
        if disc.is_zero() || (&disc % &pb).is_zero() {
            continue;
        }
        out.push((a, b));
    }
    out
}

#[derive(Clone, Default)]
struct Rung {
    work: u64,
    shells_completed: u64,
    points_found_cumulative: usize,
    distinct_residues: usize,
    new_nontorsion_points_cumulative: u64,
    rational_points_seen: u64,
    points_without_residue: u64,
}

fn fit_gamma(rungs: &[Rung]) -> Option<f64> {
    let pts: Vec<(f64, f64)> = rungs.iter().filter(|r| r.distinct_residues > 0).map(|r| ((r.work as f64).ln(), (r.distinct_residues as f64).ln())).collect();
    let pts: Vec<(f64, f64)> = pts.iter().rev().take(3).rev().cloned().collect();
    if pts.len() < 2 {
        return None;
    }
    let n = pts.len() as f64;
    let mx = pts.iter().map(|p| p.0).sum::<f64>() / n;
    let my = pts.iter().map(|p| p.1).sum::<f64>() / n;
    let sxx: f64 = pts.iter().map(|p| (p.0 - mx).powi(2)).sum();
    if sxx == 0.0 {
        return None;
    }
    Some(pts.iter().map(|p| (p.0 - mx) * (p.1 - my)).sum::<f64>() / sxx)
}

struct CellOut {
    rungs: Vec<Rung>,
    gamma: Option<f64>,
    new_nontorsion: u64,
    min_height_over_logp: Option<f64>,
}

fn run_cell(k: &NumberField, e: &CurveNF, p: &BigUint, root: &BigUint, ladder: &[u64], aux: &[u64], split_for_t: &[u64], t: u64, seed: u64) -> CellOut {
    let mut ladder: Vec<u64> = ladder.to_vec();
    ladder.sort_unstable();
    ladder.dedup();
    let mut rungs: Vec<Rung> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();
    let mut residues: HashSet<String> = HashSet::new();
    let mut cum = Rung::default();
    let mut min_height: Option<f64> = None;
    let mut rung_i = 0usize;
    let (mut last_tried, mut last_shells) = (0u64, 0u64);
    let logp = ln_big(&BigInt::from(p.clone()));
    let snapshot = |rungs: &mut Vec<Rung>, cum: &Rung, residues: &HashSet<String>, seen: &HashSet<String>, tried: u64, shells: u64| {
        let mut r = cum.clone();
        r.work = tried;
        r.shells_completed = shells;
        r.points_found_cumulative = seen.len();
        r.distinct_residues = residues.len();
        rungs.push(r);
    };
    let max_work = *ladder.last().unwrap();
    e.iter_search(aux, max_work, &ladder, &seed.to_string(), &[1, 2, 3, 4], &mut |ev| match ev {
        Event::Checkpoint { tried, shells } => {
            last_tried = tried;
            last_shells = shells;
            while rung_i < ladder.len() && tried >= ladder[rung_i] {
                snapshot(&mut rungs, &cum, &residues, &seen, tried, shells);
                rung_i += 1;
            }
        }
        Event::Shell { tried, shells } => {
            last_tried = tried;
            last_shells = shells;
        }
        Event::Point { tried, shells, point } => {
            last_tried = tried;
            last_shells = shells;
            let key = format!("{}|{}", k.elt_to_string(&point.0), k.elt_to_string(&point.1));
            if !seen.insert(key) {
                return;
            }
            match e.reduce_point_big(&point, p, root) {
                None => {
                    cum.points_without_residue += 1;
                    return;
                }
                Some((x, y)) => {
                    residues.insert(format!("{},{}", x, y));
                }
            }
            if k.is_rational(&point.0) && k.is_rational(&point.1) {
                cum.rational_points_seen += 1;
                return;
            }
            if !ecnf::is_torsion_candidate(e, &point, split_for_t, t) {
                cum.new_nontorsion_points_cumulative += 1;
                let h = k.height(&point.0);
                min_height = Some(min_height.map_or(h, |m: f64| m.min(h)));
            }
        }
    });
    while rung_i < ladder.len() {
        snapshot(&mut rungs, &cum, &residues, &seen, last_tried, last_shells);
        rung_i += 1;
    }
    let gamma = fit_gamma(&rungs);
    CellOut { gamma, new_nontorsion: cum.new_nontorsion_points_cumulative, min_height_over_logp: min_height.map(|h| h / logp), rungs }
}

fn slope(pairs: &[(f64, f64)]) -> Option<f64> {
    let n = pairs.len() as f64;
    let mx = pairs.iter().map(|p| p.0).sum::<f64>() / n;
    let my = pairs.iter().map(|p| p.1).sum::<f64>() / n;
    let sxx: f64 = pairs.iter().map(|p| (p.0 - mx).powi(2)).sum();
    if sxx == 0.0 { None } else { Some(pairs.iter().map(|p| (p.0 - mx) * (p.1 - my)).sum::<f64>() / sxx) }
}

fn regress(pairs: &[(f64, f64)], rng: &mut Rng, boots: usize) -> Value {
    if pairs.len() < 3 {
        return Value::Null;
    }
    let s0 = slope(pairs);
    let mut bs: Vec<f64> = Vec::new();
    for _ in 0..boots {
        let sample: Vec<(f64, f64)> = (0..pairs.len()).map(|_| pairs[rng.below(pairs.len() as u64) as usize]).collect();
        if let Some(s) = slope(&sample) {
            bs.push(s);
        }
    }
    bs.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let ci = if bs.is_empty() { Value::Null } else { json!([bs[(0.005 * bs.len() as f64) as usize], bs[((0.995 * bs.len() as f64) as usize).saturating_sub(1)]]) };
    json!({"slope": s0, "n": pairs.len(), "ci99": ci})
}

struct Args {
    kmin: u32,
    kmax: u32,
    min_bits: u64,
    max_primes_per_shape: usize,
    random_g: usize,
    curves: usize,
    ladder: Vec<u64>,
    seeds: Vec<u64>,
    aux_primes: usize,
    shapes: Vec<String>,
    out: String,
}

fn parse_args() -> Args {
    let mut a = Args { kmin: 4, kmax: 12, min_bits: 12, max_primes_per_shape: 3, random_g: 20, curves: 5, ladder: vec![300, 1000, 3000, 10000, 30000, 100000], seeds: vec![1, 2, 3], aux_primes: 8, shapes: nist_shapes().iter().map(|(n, _)| n.to_string()).collect(), out: String::new() };
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    while i < argv.len() {
        match argv[i].as_str() {
            "--ladder" | "--seeds" | "--shapes" => {
                let which = argv[i].clone();
                let mut v: Vec<String> = Vec::new();
                while i + 1 < argv.len() && !argv[i + 1].starts_with("--") {
                    i += 1;
                    v.push(argv[i].clone());
                }
                match which.as_str() {
                    "--ladder" => a.ladder = v.iter().map(|x| x.parse().unwrap()).collect(),
                    "--seeds" => a.seeds = v.iter().map(|x| x.parse().unwrap()).collect(),
                    _ => a.shapes = v,
                }
            }
            "--kmin" => { i += 1; a.kmin = argv[i].parse().unwrap(); }
            "--kmax" => { i += 1; a.kmax = argv[i].parse().unwrap(); }
            "--min-bits" => { i += 1; a.min_bits = argv[i].parse().unwrap(); }
            "--max-primes-per-shape" => { i += 1; a.max_primes_per_shape = argv[i].parse().unwrap(); }
            "--random-g" => { i += 1; a.random_g = argv[i].parse().unwrap(); }
            "--curves" => { i += 1; a.curves = argv[i].parse().unwrap(); }
            "--aux-primes" => { i += 1; a.aux_primes = argv[i].parse().unwrap(); }
            "--out" => { i += 1; a.out = argv[i].clone(); }
            "-h" | "--help" => {
                eprintln!("usage: g3 [--kmin K] [--kmax K] [--min-bits B] [--max-primes-per-shape N] [--random-g N] [--curves N] [--ladder W ...] [--seeds S ...] [--aux-primes N] [--shapes P-192 ...] --out DIR");
                std::process::exit(0);
            }
            other => panic!("unknown argument {}", other),
        }
        i += 1;
    }
    assert!(!a.out.is_empty(), "--out is required");
    a
}

struct Fld {
    kind: &'static str,
    shape: String,
    g: Vec<i64>,
    k: u32,
    p: BigUint,
    d: usize,
    weight: usize,
}

fn bigint_json(x: &BigInt) -> Value {
    match x.to_i64() { Some(v) => json!(v), None => json!(x.to_string()) }
}

fn sha256_file(path: &std::path::Path) -> String {
    format!("{:x}", Sha256::digest(std::fs::read(path).unwrap_or_default()))
}

fn now_unix() -> f64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs_f64()
}

fn mean(xs: &[Option<f64>]) -> Option<f64> {
    let v: Vec<f64> = xs.iter().filter_map(|x| *x).collect();
    if v.is_empty() { None } else { Some(v.iter().sum::<f64>() / v.len() as f64) }
}

fn main() {
    let args = parse_args();
    std::fs::create_dir_all(&args.out).expect("create out dir");
    let started = now_unix();
    let t_start = Instant::now();
    let mut cell_seconds: Vec<f64> = Vec::new();
    let shapes = nist_shapes();
    let mut raw = Map::new();
    raw.insert("experiment_id".into(), json!(EXP));
    raw.insert("hypothesis_id".into(), json!(HYP));
    raw.insert("gp_version".into(), json!(gp::version()));
    raw.insert("ctrl_shape".into(), json!(check_shapes()));
    let mut cells: Vec<Value> = Vec::new();
    for &seed in &args.seeds {
        let mut rng = Rng::seeded(&format!("{}:{}", EXP, seed));
        let mut fields: Vec<Fld> = Vec::new();
        for name in &args.shapes {
            let f = &shapes.iter().find(|(n, _)| n == name).unwrap_or_else(|| panic!("unknown shape {}", name)).1;
            for (k, p) in toy_primes_for(f, args.kmin, args.kmax, args.min_bits).into_iter().take(args.max_primes_per_shape) {
                fields.push(Fld { kind: "solinas", shape: name.clone(), g: f.clone(), k, p, d: f.len() - 1, weight: weight(f) });
            }
            let (d, w) = (f.len() - 1, weight(f));
            let mut made = 0;
            let mut attempts = 0;
            while made < args.random_g && attempts < 50 * args.random_g {
                attempts += 1;
                let g = random_shape(d, w, &mut rng);
                let ps = toy_primes_for(&g, args.kmin, args.kmax, args.min_bits);
                if ps.is_empty() {
                    continue;
                }
                let (k, p) = ps[0].clone();
                fields.push(Fld { kind: "random_g", shape: name.clone(), g, k, p, d, weight: w });
                made += 1;
            }
            for cc in [3i64, 5, 7, 11, 13] {
                let mut g = vec![0i64; d + 1];
                g[0] = -cc;
                g[d] = 1;
                let ps = toy_primes_for(&g, args.kmin, args.kmax, args.min_bits);
                if let Some((k, p)) = ps.first() {
                    fields.push(Fld { kind: "tdc", shape: name.clone(), g, k: *k, p: p.clone(), d, weight: 2 });
                    break;
                }
            }
            if let Some((k, p)) = toy_primes_for(f, args.kmin, args.kmax, args.min_bits).first() {
                fields.push(Fld { kind: "Q", shape: name.clone(), g: vec![0, 1], k: *k, p: p.clone(), d: 1, weight: 1 });
            }
        }
        for fld in &fields {
            let gb: Vec<BigInt> = fld.g.iter().map(|&c| big(c)).collect();
            let k = NumberField::new(gb.clone());
            let p = &fld.p;
            let root = if k.d > 1 { BigUint::from(2u32).modpow(&BigUint::from(fld.k), p) } else { BigUint::zero() };
            assert!(k.d == 1 || (poly_eval(&fld.g, &big(2).pow(fld.k)) % BigInt::from(p.clone())).is_zero());
            let avoid: Vec<u64> = p.to_u64().into_iter().collect();
            let aux = k.degree_one_primes(args.aux_primes, 1_000_000, &avoid, 200000);
            let split_for_t: Vec<u64> = aux.iter().take(6).cloned().collect();
            let mut rngo = Rng::seeded(&format!("{}:order:{}:{}", EXP, seed, p));
            let disc = k.discriminant();
            let nfd = if k.d > 1 { gp::nfdisc(&gb) } else { Some(BigInt::from(1)) };
            let mut frec = Map::new();
            frec.insert("kind".into(), json!(fld.kind));
            frec.insert("shape".into(), json!(fld.shape));
            frec.insert("g".into(), json!(fld.g));
            frec.insert("g_text".into(), json!(poly_text(&fld.g)));
            frec.insert("k".into(), json!(fld.k));
            frec.insert("p".into(), json!(p.to_string()));
            frec.insert("p_bits".into(), json!(p.bits()));
            frec.insert("d".into(), json!(fld.d));
            frec.insert("weight".into(), json!(fld.weight));
            frec.insert("disc".into(), bigint_json(&disc));
            frec.insert("root_discriminant".into(), json!(k.root_discriminant()));
            frec.insert("nfdisc_pari".into(), nfd.as_ref().map(bigint_json).unwrap_or(Value::Null));
            if let Some(n) = &nfd {
                if !n.is_zero() {
                    frec.insert("root_discriminant_field".into(), json!(if k.d > 1 { (ln_big(n) / k.d as f64).exp() } else { 1.0 }));
                }
            }
            let frec = Value::Object(frec);
            let curves = seeded_curves(args.curves, p, &mut Rng::seeded(&format!("{}:curves:{}:{}:{}", EXP, seed, fld.shape, fld.k)));
            for (ci, (a, b)) in curves.iter().enumerate() {
                let e = CurveNF::new(&k, rat(*a), rat(*b), rat(0));
                let t = ecnf::torsion_bound(&e, &split_for_t, &mut rngo);
                let t0 = Instant::now();
                let cell = run_cell(&k, &e, p, &root, &args.ladder, &aux, &split_for_t, t, seed);
                cell_seconds.push((t0.elapsed().as_secs_f64() * 1000.0).round() / 1000.0);
                let last = cell.rungs.last().unwrap();
                eprintln!("seed={} {} {} k={} curve={}: D={} gamma={:?} N={}", seed, fld.kind, fld.shape, fld.k, ci, last.distinct_residues, cell.gamma, cell.new_nontorsion);
                cells.push(json!({
                    "seed": seed, "field": frec, "curve": {"A": a.to_string(), "B": b.to_string()}, "curve_index": ci,
                    "torsion_bound_T": t,
                    "rungs": cell.rungs.iter().map(|r| json!({
                        "work": r.work, "shells_completed": r.shells_completed, "points_found_cumulative": r.points_found_cumulative,
                        "distinct_residues": r.distinct_residues, "new_nontorsion_points_cumulative": r.new_nontorsion_points_cumulative,
                        "rational_points_seen": r.rational_points_seen, "points_without_residue": r.points_without_residue})).collect::<Vec<_>>(),
                    "gamma": cell.gamma, "new_nontorsion_points": cell.new_nontorsion,
                    "min_new_point_log_height_over_log_p": cell.min_height_over_logp,
                    "rank_arm": "skipped: no 2-descent over number fields available; new non-torsion point count is a lower bound on rank gain only if the points are independent, which is not certified",
                }));
            }
        }
    }
    // summary: per shape, gamma solinas minus random_g, and the regression
    let mut summ: BTreeMap<String, BTreeMap<&str, Vec<Option<f64>>>> = BTreeMap::new();
    for cell in &cells {
        let shape = cell["field"]["shape"].as_str().unwrap().to_string();
        let kind: &str = match cell["field"]["kind"].as_str().unwrap() { "solinas" => "solinas", "random_g" => "random_g", "tdc" => "tdc", _ => "Q" };
        let s = summ.entry(shape).or_insert_with(|| { let mut m = BTreeMap::new(); for k in ["solinas", "random_g", "tdc", "Q"] { m.insert(k, vec![]); } m });
        s.get_mut(kind).unwrap().push(cell["gamma"].as_f64());
    }
    let mut per_shape = Map::new();
    for (shape, s) in &summ {
        let mut o = Map::new();
        for (k, v) in s {
            o.insert((*k).into(), json!(v));
        }
        let diff = match (mean(&s["solinas"]), mean(&s["random_g"])) { (Some(a), Some(b)) => Some(a - b), _ => None };
        o.insert("gamma_solinas_minus_random_g".into(), json!(diff));
        per_shape.insert(shape.clone(), Value::Object(o));
    }
    let mut rngb = Rng::seeded(&format!("{}:boot", EXP));
    let pairs: Vec<(f64, f64)> = cells
        .iter()
        .filter(|c| c["field"]["d"].as_u64().unwrap() > 1)
        .filter_map(|c| {
            let rd = c["field"].get("root_discriminant_field").and_then(|v| v.as_f64()).or_else(|| c["field"]["root_discriminant"].as_f64())?;
            let gm = c["gamma"].as_f64()?;
            Some((rd.ln(), gm))
        })
        .collect();
    let regression = regress(&pairs, &mut rngb, 1000);
    raw.insert("cells".into(), Value::Array(cells));
    raw.insert("summary".into(), json!({"per_shape": Value::Object(per_shape), "regression_gamma_vs_log_root_discriminant": regression}));
    let raw_path = std::path::Path::new(&args.out).join("raw-result.json");
    std::fs::write(&raw_path, serde_json::to_string_pretty(&Value::Object(raw)).unwrap() + "\n").expect("write raw-result.json");
    let here = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let nf = here.join("../../EXP-ECDLP-84af7b/implementation/nfield");
    let mut sources = Map::new();
    sources.insert("src/main.rs".into(), json!(sha256_file(&here.join("src/main.rs"))));
    sources.insert("Cargo.toml".into(), json!(sha256_file(&here.join("Cargo.toml"))));
    for f in ["src/lib.rs", "src/field.rs", "src/ecnf.rs", "src/modpoly.rs", "src/rng.rs", "src/gp.rs", "csrc/pari_shim.c", "Cargo.toml"] {
        sources.insert(format!("nfield/{}", f), json!(sha256_file(&nf.join(f))));
    }
    let rustc = std::process::Command::new("rustc").arg("--version").output().ok().map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string());
    let git = std::process::Command::new("git").args(["rev-parse", "HEAD"]).output().ok().filter(|o| o.status.success()).map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string());
    let manifest: Vec<(&str, Value)> = vec![
        ("experiment_id", json!(EXP)),
        ("command", json!(std::env::args().collect::<Vec<_>>().join(" "))),
        ("implementation", json!(format!("Rust (snfs-g3 {} / nfield), pari feature {}", env!("CARGO_PKG_VERSION"), if gp::available() { "on" } else { "off" }))),
        ("rustc", json!(rustc)),
        ("platform", json!(format!("{} {}", std::env::consts::OS, std::env::consts::ARCH))),
        ("gp_version", json!(gp::version())),
        ("source_sha256", Value::Object(sources)),
        ("raw_result_sha256", json!(sha256_file(&raw_path))),
        ("started_unix", json!(started)),
        ("finished_unix", json!(now_unix())),
        ("wall_clock_seconds", json!((t_start.elapsed().as_secs_f64() * 1000.0).round() / 1000.0)),
        ("cell_seconds", json!(cell_seconds)),
        ("raw_result_is_replay_deterministic", json!("raw-result.json carries no timing; CTRL-REPLAY compares it byte for byte")),
        ("git_commit", json!(git)),
        ("asserts_nothing_about", json!("the hypothesis; observations only")),
    ];
    let mut text = String::new();
    for (k, v) in manifest {
        text.push_str(&format!("{}: {}\n", k, serde_json::to_string(&v).unwrap()));
    }
    std::fs::write(std::path::Path::new(&args.out).join("manifest.yaml"), text).expect("write manifest");
}
