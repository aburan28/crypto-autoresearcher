//! EXP-ECDLP-84af7b (H-ECDLP-2f1033, SNFS-G1): cyclotomic lift with complete splitting.
//!
//! For Mersenne primes p = 2^c - 1 and the cyclic subfields K of Q(zeta_c) of degree d | c - 1 (in
//! which p splits completely), lift rank-0 curves E/Q to K, enumerate K-points by a sieved
//! sup-norm-shell search, reduce them at the d primes above p, and measure the relation yield
//! ratio R(W) = (new non-torsion points) / (distinct residues), the covering exponent
//! gamma = dlog D / dlog W, and the trace relation [T] sum_i r_i(P) = O (CTRL-TRACE). Controls: the
//! cyclic degree-d subfields of Q(zeta_m) for primes m != c in which p also splits completely
//! (abelian controls), and seeded random completely split fields where the search finds them.
//! Observations only; this binary asserts nothing about the hypothesis.

use nfield::ecnf::{self, CurveNF, Event};
use nfield::field::{big, gaussian_period_polynomial, is_prime_u64, ln_big, random_split_field, NumberField};
use nfield::{gp, Rng};
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{Signed, ToPrimitive, Zero};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, HashSet};
use std::time::{Instant, SystemTime, UNIX_EPOCH};

const EXP: &str = "EXP-ECDLP-84af7b";
const HYP: &str = "H-ECDLP-2f1033";

struct Curve {
    label: &'static str,
    ainvs: [i64; 5],
    note: &'static str,
}

const CURVES: [Curve; 7] = [
    Curve { label: "32a2", ainvs: [0, 0, 0, -1, 0], note: "y^2 = x^3 - x, CM by Z[i], rank 0 (1 is not congruent)" },
    Curve { label: "congruent-2", ainvs: [0, 0, 0, -4, 0], note: "y^2 = x^3 - 4x, rank 0 (2 is not congruent)" },
    Curve { label: "congruent-3", ainvs: [0, 0, 0, -9, 0], note: "y^2 = x^3 - 9x, rank 0 (3 is not congruent)" },
    Curve { label: "36a1", ainvs: [0, 0, 0, 0, 1], note: "y^2 = x^3 + 1, CM by Z[zeta_3], rank 0" },
    Curve { label: "mordell-m1", ainvs: [0, 0, 0, 0, -1], note: "y^2 = x^3 - 1, rank 0" },
    Curve { label: "11a1", ainvs: [0, -1, 1, -10, -20], note: "non-CM, rank 0 (Cremona 11a1, recalled a-invariants)" },
    Curve { label: "14a1", ainvs: [1, 0, 1, 4, -6], note: "non-CM, rank 0 (Cremona 14a1, recalled a-invariants)" },
];

/// (a2', a4', a6') with y'^2 = x^3 + a2' x^2 + a4' x + a6' isomorphic over Q to [a1,a2,a3,a4,a6]
/// via y' = y + (a1 x + a3)/2: the x-coordinate is unchanged, so torsion stays in small shells.
fn b_model(a: &[i64; 5]) -> (BigRational, BigRational, BigRational) {
    let (a1, a2, a3, a4, a6) = (a[0], a[1], a[2], a[3], a[4]);
    (
        BigRational::new(big(a1 * a1 + 4 * a2), big(4)),
        BigRational::new(big(2 * a4 + a1 * a3), big(2)),
        BigRational::new(big(a3 * a3 + 4 * a6), big(4)),
    )
}

fn subfield_degrees(c: u64, dmax: usize) -> Vec<usize> {
    (2..=dmax).filter(|&d| (c - 1).is_multiple_of(d as u64)).collect()
}

/// The `count` smallest primes m = 1 mod d, m != c, such that p is a d-th power residue mod m,
/// i.e. p splits completely in the cyclic degree-d subfield of Q(zeta_m).
fn abelian_control_conductors(c: u64, d: usize, p: u64, count: usize) -> Vec<u64> {
    let mut out = Vec::new();
    let mut m = d as u64 + 1;
    while out.len() < count {
        if m != c && is_prime_u64(m) && (m - 1).is_multiple_of(d as u64) && nfield::modpoly::powmod(p % m, (m - 1) / d as u64, m) == 1 {
            out.push(m);
        }
        m += d as u64;
    }
    out
}

#[derive(Clone)]
struct Field {
    kind: &'static str,
    d: usize,
    g: Vec<BigInt>,
    conductor: Option<u64>,
    label: String,
}

fn rat_str(x: &BigRational) -> String {
    nfield::field::rat_to_string(x)
}

fn bigint_json(x: &BigInt) -> Value {
    match x.to_i64() {
        Some(v) => json!(v),
        None => json!(x.to_string()),
    }
}

/// Field metadata: polynomial discriminant, PARI nfdisc when built with the pari feature, and the
/// field root discriminant: exact m^((d-1)/d) for a cyclic degree-d subfield of Q(zeta_m) with m
/// prime (conductor-discriminant formula), else from nfdisc, else the polynomial bound (flagged).
fn field_record(fld: &Field, k: &NumberField) -> Value {
    let mut rec = Map::new();
    rec.insert("kind".into(), json!(fld.kind));
    rec.insert("d".into(), json!(fld.d));
    rec.insert("g".into(), json!(fld.g.iter().map(bigint_json).collect::<Vec<_>>()));
    rec.insert("label".into(), json!(fld.label));
    if let Some(m) = fld.conductor {
        rec.insert("conductor".into(), json!(m));
    }
    let disc = k.discriminant();
    rec.insert("disc".into(), bigint_json(&disc));
    rec.insert("root_discriminant_poly".into(), json!(k.root_discriminant()));
    let nfd = if k.d > 1 { gp::nfdisc(&fld.g) } else { Some(BigInt::from(1)) };
    rec.insert("nfdisc_pari".into(), nfd.as_ref().map(bigint_json).unwrap_or(Value::Null));
    let (field_disc, source): (BigInt, &str) = match (fld.conductor, &nfd) {
        (Some(m), _) if fld.d > 1 => {
            let fd = big(m as i64).pow((fld.d - 1) as u32);
            if let Some(n) = &nfd {
                rec.insert("ctrl_disc_pari_agrees".into(), json!(n.abs() == fd));
            }
            (fd, "conductor-discriminant formula (cyclic, prime conductor)")
        }
        (_, Some(n)) => (n.abs(), "PARI nfdisc (libpari FFI)"),
        _ => (disc.abs(), "polynomial discriminant (upper bound; built without pari)"),
    };
    rec.insert("field_disc".into(), bigint_json(&field_disc));
    rec.insert("field_disc_source".into(), json!(source));
    let rd = if k.d > 1 && !field_disc.is_zero() { (ln_big(&field_disc) / k.d as f64).exp() } else { 1.0 };
    rec.insert("root_discriminant_field".into(), json!(rd));
    Value::Object(rec)
}

#[derive(Clone, Default)]
struct Rung {
    work: u64,
    shells_completed: u64,
    points_found_cumulative: usize,
    distinct_residues: usize,
    new_nontorsion_points: u64,
    residue_coincidences: u64,
    rational_points_seen: u64,
    points_without_residue: u64,
    trace_relation_ok: u64,
    trace_relation_fail: u64,
    min_new_point_log_height_over_log_p: Option<f64>,
}

impl Rung {
    fn relation_yield_ratio(&self) -> Option<f64> {
        if self.distinct_residues > 0 {
            Some(self.new_nontorsion_points as f64 / self.distinct_residues as f64)
        } else {
            None
        }
    }
    fn to_json(&self) -> Value {
        json!({
            "work": self.work,
            "shells_completed": self.shells_completed,
            "points_found_cumulative": self.points_found_cumulative,
            "distinct_residues": self.distinct_residues,
            "new_nontorsion_points": self.new_nontorsion_points,
            "relation_yield_ratio": self.relation_yield_ratio(),
            "residue_coincidences": self.residue_coincidences,
            "rational_points_seen": self.rational_points_seen,
            "points_without_residue": self.points_without_residue,
            "trace_relation_ok": self.trace_relation_ok,
            "trace_relation_fail": self.trace_relation_fail,
            "min_new_point_log_height_over_log_p": self.min_new_point_log_height_over_log_p,
        })
    }
}

/// Slope of log D against log W over the last three rungs with D > 0.
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
    max_r: f64,
    total_new: u64,
    trace_fail: u64,
}

/// One enumeration up to max(ladder) candidates; each rung is a snapshot of the cumulative state
/// when `tried` first reaches that rung's work budget.
fn run_cell(k: &NumberField, e: &CurveNF, p: u64, ladder: &[u64], aux: &[u64], split_for_t: &[u64], t: u64, seed: u64) -> CellOut {
    let mut ladder: Vec<u64> = ladder.to_vec();
    ladder.sort_unstable();
    ladder.dedup();
    let mut rungs: Vec<Rung> = Vec::new();
    let mut all_points: HashSet<String> = HashSet::new();
    let mut residues: HashSet<(u64, u64)> = HashSet::new();
    let mut cum = Rung::default();
    let mut min_height: Option<f64> = None;
    let mut rung_i = 0usize;
    let (mut last_tried, mut last_shells) = (0u64, 0u64);
    let logp = (p as f64).ln();
    let snapshot = |rungs: &mut Vec<Rung>, cum: &Rung, residues: &HashSet<(u64, u64)>, all: &HashSet<String>, tried: u64, shells: u64, mh: Option<f64>| {
        let mut r = cum.clone();
        r.work = tried;
        r.shells_completed = shells;
        r.points_found_cumulative = all.len();
        r.distinct_residues = residues.len();
        r.min_new_point_log_height_over_log_p = mh.map(|h| h / logp);
        rungs.push(r);
    };
    let max_work = *ladder.last().unwrap();
    e.iter_search(aux, max_work, &ladder, &seed.to_string(), &[1, 2, 3, 4], &mut |ev| match ev {
        Event::Checkpoint { tried, shells } => {
            last_tried = tried;
            last_shells = shells;
            while rung_i < ladder.len() && tried >= ladder[rung_i] {
                snapshot(&mut rungs, &cum, &residues, &all_points, tried, shells, min_height);
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
            if !all_points.insert(key) {
                return;
            }
            let res = ecnf::residues_at_p(e, &point, p);
            if res.iter().any(|r| r.is_none()) {
                cum.points_without_residue += 1;
                return;
            }
            let uniq: HashSet<(u64, u64)> = res.iter().map(|r| r.unwrap()).collect();
            cum.residue_coincidences += (res.len() - uniq.len()) as u64;
            residues.extend(uniq.iter().cloned());
            match ecnf::trace_relation_holds(e, &res, p, t) {
                Some(true) => cum.trace_relation_ok += 1,
                Some(false) => cum.trace_relation_fail += 1,
                None => {}
            }
            if k.is_rational(&point.0) && k.is_rational(&point.1) {
                cum.rational_points_seen += 1;
                return;
            }
            if !ecnf::is_torsion_candidate(e, &point, split_for_t, t) {
                cum.new_nontorsion_points += 1;
                let h = k.height(&point.0);
                min_height = Some(min_height.map_or(h, |m: f64| m.min(h)));
            }
        }
    });
    while rung_i < ladder.len() {
        snapshot(&mut rungs, &cum, &residues, &all_points, last_tried, last_shells, min_height);
        rung_i += 1;
    }
    let gamma = fit_gamma(&rungs);
    let max_r = rungs.iter().filter_map(|r| r.relation_yield_ratio()).fold(0.0, f64::max);
    CellOut { gamma, max_r, total_new: cum.new_nontorsion_points, trace_fail: cum.trace_relation_fail, rungs }
}

struct Args {
    c: Vec<u64>,
    dmax: usize,
    ladder: Vec<u64>,
    curves: usize,
    random_fields: usize,
    abelian_controls: usize,
    seeds: Vec<u64>,
    aux_primes: usize,
    out: String,
}

fn parse_args() -> Args {
    let mut a = Args { c: vec![13, 17, 19, 31], dmax: 12, ladder: vec![300, 1000, 3000, 10000, 30000, 100000], curves: CURVES.len(), random_fields: 2, abelian_controls: 3, seeds: vec![1, 2, 3], aux_primes: 8, out: String::new() };
    let argv: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    let take_list = |i: &mut usize, argv: &[String]| -> Vec<u64> {
        let mut v = Vec::new();
        while *i + 1 < argv.len() && !argv[*i + 1].starts_with("--") {
            *i += 1;
            v.push(argv[*i].parse().expect("integer"));
        }
        v
    };
    while i < argv.len() {
        match argv[i].as_str() {
            "--c" => a.c = take_list(&mut i, &argv),
            "--ladder" => a.ladder = take_list(&mut i, &argv),
            "--seeds" => a.seeds = take_list(&mut i, &argv),
            "--dmax" => { i += 1; a.dmax = argv[i].parse().unwrap(); }
            "--curves" => { i += 1; a.curves = argv[i].parse().unwrap(); }
            "--random-fields" => { i += 1; a.random_fields = argv[i].parse().unwrap(); }
            "--abelian-controls" => { i += 1; a.abelian_controls = argv[i].parse().unwrap(); }
            "--aux-primes" => { i += 1; a.aux_primes = argv[i].parse().unwrap(); }
            "--out" => { i += 1; a.out = argv[i].clone(); }
            "-h" | "--help" => {
                eprintln!("usage: g1 [--c C ...] [--dmax D] [--ladder W ...] [--curves N] [--random-fields N] [--abelian-controls N] [--seeds S ...] [--aux-primes N] --out DIR");
                std::process::exit(0);
            }
            other => panic!("unknown argument {}", other),
        }
        i += 1;
    }
    assert!(!a.out.is_empty(), "--out is required");
    a
}

fn sha256_file(path: &std::path::Path) -> String {
    let data = std::fs::read(path).unwrap_or_default();
    format!("{:x}", Sha256::digest(&data))
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
    let mut raw = Map::new();
    raw.insert("experiment_id".into(), json!(EXP));
    raw.insert("hypothesis_id".into(), json!(HYP));
    raw.insert("gp_version".into(), json!(gp::version()));
    let mut curves_json: Vec<Value> = Vec::new();
    let mut curves: Vec<(&'static str, BigRational, BigRational, BigRational)> = Vec::new();
    for cv in CURVES.iter().take(args.curves) {
        let (a2, a4, a6) = b_model(&cv.ainvs);
        let rk = gp::ellrank_q(&cv.ainvs);
        let excluded = rk.map(|(_, hi)| hi != 0).unwrap_or(false);
        curves_json.push(json!({
            "label": cv.label, "ainvs": cv.ainvs, "note": cv.note,
            "model": {"a2": rat_str(&a2), "a4": rat_str(&a4), "a6": rat_str(&a6)},
            "ctrl_rank0": rk.map(|(lo, hi)| json!({"rank_lower": lo, "rank_upper": hi, "source": "libpari ellrank over Q (FFI)"})),
            "excluded_not_rank0": excluded,
        }));
        if !excluded {
            curves.push((cv.label, a2, a4, a6));
        }
    }
    raw.insert("curves".into(), Value::Array(curves_json));
    let mut cells: Vec<Value> = Vec::new();
    for &seed in &args.seeds {
        for &c in &args.c {
            let p: u64 = (1u64 << c) - 1;
            assert!(is_prime_u64(p), "2^c - 1 must be prime");
            let mut fields: Vec<Field> = vec![Field { kind: "cyclotomic", d: 1, g: vec![big(0), big(1)], conductor: None, label: "Q".into() }];
            for d in subfield_degrees(c, args.dmax) {
                fields.push(Field { kind: "cyclotomic", d, g: gaussian_period_polynomial(c, d), conductor: Some(c), label: format!("Q(zeta_{})^({})", c, d) });
            }
            let mut controls: Vec<Field> = Vec::new();
            for f in fields.iter().filter(|x| x.d > 1) {
                let kc = NumberField::new(f.g.clone());
                for m in abelian_control_conductors(c, f.d, p, args.abelian_controls) {
                    controls.push(Field { kind: "abelian_control", d: f.d, g: gaussian_period_polynomial(m, f.d), conductor: Some(m), label: format!("Q(zeta_{})^({})", m, f.d) });
                }
                for i in 0..args.random_fields {
                    match random_split_field(f.d, p, &format!("{}:{}", seed, i), 3, 20000, Some(kc.root_discriminant())) {
                        Some((g, _)) if g != f.g => controls.push(Field { kind: "random_split", d: f.d, g, conductor: None, label: format!("rand{}(d={})", i, f.d) }),
                        Some(_) => {}
                        None => cells.push(json!({"seed": seed, "c": c, "p": p, "field": {"kind": "random_split", "d": f.d},
                            "invalid": format!("no random completely split field of degree {} found (search exhausted)", f.d)})),
                    }
                }
            }
            fields.extend(controls);
            for fld in &fields {
                let k = NumberField::new(fld.g.clone());
                if k.d > 1 && !k.splits_completely(p) {
                    cells.push(json!({"seed": seed, "c": c, "p": p, "field": {"kind": fld.kind, "d": fld.d, "label": fld.label}, "invalid": "CTRL-SPLIT failed"}));
                    continue;
                }
                let aux = k.degree_one_primes(args.aux_primes, 1_000_000, &[p], 200000);
                let split_for_t: Vec<u64> = aux.iter().take(6).cloned().collect();
                let mut rng = Rng::seeded(&format!("{}:order:{}:{}", EXP, seed, c));
                let frec = field_record(fld, &k);
                for (label, a2, a4, a6) in &curves {
                    let e = CurveNF::new(&k, a4.clone(), a6.clone(), a2.clone());
                    let t = ecnf::torsion_bound(&e, &split_for_t, &mut rng);
                    let t0 = Instant::now();
                    let cell = run_cell(&k, &e, p, &args.ladder, &aux, &split_for_t, t, seed);
                    cell_seconds.push((t0.elapsed().as_secs_f64() * 1000.0).round() / 1000.0);
                    let last = cell.rungs.last().unwrap();
                    eprintln!("seed={} c={} {} {}: D={} N={} Rmax={:.3} gamma={:?} trace_fail={}", seed, c, fld.label, label, last.distinct_residues, cell.total_new, cell.max_r, cell.gamma, cell.trace_fail);
                    cells.push(json!({
                        "seed": seed, "c": c, "p": p, "field": frec, "curve": label, "torsion_bound_T": t,
                        "rungs": cell.rungs.iter().map(|r| r.to_json()).collect::<Vec<_>>(),
                        "gamma": cell.gamma, "max_relation_yield_ratio": cell.max_r,
                        "total_new_nontorsion_points": cell.total_new, "trace_relation_failures": cell.trace_fail,
                    }));
                }
            }
        }
    }
    // summary per (c, d): cyclotomic vs each control arm
    let mut summ: BTreeMap<String, BTreeMap<&str, Vec<Value>>> = BTreeMap::new();
    for cell in &cells {
        if cell.get("invalid").is_some() {
            continue;
        }
        let key = format!("c={} d={}", cell["c"], cell["field"]["d"]);
        let kind = cell["field"]["kind"].as_str().unwrap().to_string();
        let kind_static: &str = match kind.as_str() { "cyclotomic" => "cyclotomic", "abelian_control" => "abelian_control", _ => "random_split" };
        let s = summ.entry(key).or_insert_with(|| { let mut m = BTreeMap::new(); m.insert("cyclotomic", vec![]); m.insert("abelian_control", vec![]); m.insert("random_split", vec![]); m });
        s.get_mut(kind_static).unwrap().push(json!({"gamma": cell["gamma"], "Rmax": cell["max_relation_yield_ratio"], "N": cell["total_new_nontorsion_points"]}));
    }
    let mut summary = Map::new();
    for (key, s) in &summ {
        let mut o = Map::new();
        let gam = |arm: &str| -> Vec<Option<f64>> { s[arm].iter().map(|x| x["gamma"].as_f64()).collect() };
        let nn = |arm: &str| -> Vec<Option<f64>> { s[arm].iter().map(|x| x["N"].as_f64()).collect() };
        let rmax = |arm: &str| -> Option<f64> { s[arm].iter().filter_map(|x| x["Rmax"].as_f64()).fold(None, |m, v| Some(m.map_or(v, |mm: f64| mm.max(v)))) };
        for arm in ["cyclotomic", "abelian_control", "random_split"] {
            o.insert(arm.into(), Value::Array(s[arm].clone()));
        }
        for arm in ["abelian_control", "random_split"] {
            let gdiff = match (mean(&gam("cyclotomic")), mean(&gam(arm))) { (Some(a), Some(b)) if !s[arm].is_empty() => Some(a - b), _ => None };
            let ndiff = match (mean(&nn("cyclotomic")), mean(&nn(arm))) { (Some(a), Some(b)) if !s[arm].is_empty() => Some(a - b), _ => None };
            o.insert(format!("gamma_cyclotomic_minus_{}", arm), json!(gdiff));
            o.insert(format!("N_cyclotomic_minus_{}", arm), json!(ndiff));
            o.insert(format!("Rmax_{}", arm), json!(rmax(arm)));
        }
        o.insert("Rmax_cyclotomic".into(), json!(rmax("cyclotomic")));
        summary.insert(key.clone(), Value::Object(o));
    }
    let trace_total: u64 = cells.iter().filter(|c| c.get("invalid").is_none()).map(|c| c["trace_relation_failures"].as_u64().unwrap_or(0)).sum();
    raw.insert("cells".into(), Value::Array(cells));
    raw.insert("summary".into(), Value::Object(summary));
    raw.insert("trace_relation_failures_total".into(), json!(trace_total));
    let raw_path = std::path::Path::new(&args.out).join("raw-result.json");
    std::fs::write(&raw_path, serde_json::to_string_pretty(&Value::Object(raw)).unwrap() + "\n").expect("write raw-result.json");
    // manifest
    let here = std::path::Path::new(env!("CARGO_MANIFEST_DIR"));
    let mut sources = Map::new();
    for f in ["src/main.rs", "nfield/src/lib.rs", "nfield/src/field.rs", "nfield/src/ecnf.rs", "nfield/src/modpoly.rs", "nfield/src/rng.rs", "nfield/src/gp.rs", "nfield/csrc/pari_shim.c", "Cargo.toml", "nfield/Cargo.toml"] {
        sources.insert(f.into(), json!(sha256_file(&here.join(f))));
    }
    let rustc = std::process::Command::new("rustc").arg("--version").output().ok().map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string());
    let git = std::process::Command::new("git").args(["rev-parse", "HEAD"]).output().ok().filter(|o| o.status.success()).map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string());
    let manifest: Vec<(&str, Value)> = vec![
        ("experiment_id", json!(EXP)),
        ("command", json!(std::env::args().collect::<Vec<_>>().join(" "))),
        ("implementation", json!(format!("Rust (snfs-g1 {} / nfield), pari feature {}", env!("CARGO_PKG_VERSION"), if gp::available() { "on" } else { "off" }))),
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
