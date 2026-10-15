//! Exact arity-3 group-law enumerator for the prospective conductor-gap panel.
//! Input and output formats are specified in ORACLE_FORMAT.md. This program
//! records observations only; it does not classify an experiment.
use std::collections::HashSet;
use std::env;
use std::fs;
use std::io::{self, BufWriter, Write};

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
enum Point {
    Infinity,
    Affine(u64, u64),
}

#[derive(Clone, Copy)]
struct Curve {
    p: u64,
    a: u64,
    b: u64,
    r: u64,
}

#[derive(Clone, Copy)]
struct Pair {
    sum: Point,
    i: u16,
    j: u16,
}

#[derive(Clone, Copy)]
struct Target {
    id: usize,
    alpha: u64,
    beta: u64,
    point: Point,
}

fn modular_sum(x: u64, y: u64, p: u64) -> u64 {
    ((x as u128 + y as u128) % p as u128) as u64
}

fn modular_sub(x: u64, y: u64, p: u64) -> u64 {
    ((x as u128 + p as u128 - y as u128) % p as u128) as u64
}

fn modular_mul(x: u64, y: u64, p: u64) -> u64 {
    ((x as u128 * y as u128) % p as u128) as u64
}

fn modular_pow(mut x: u64, mut n: u64, p: u64) -> u64 {
    let mut out = 1;
    while n != 0 {
        if n & 1 != 0 {
            out = modular_mul(out, x, p);
        }
        x = modular_mul(x, x, p);
        n >>= 1;
    }
    out
}

fn negate(pt: Point, p: u64) -> Point {
    match pt {
        Point::Infinity => Point::Infinity,
        Point::Affine(x, y) => Point::Affine(x, if y == 0 { 0 } else { p - y }),
    }
}

fn add(left: Point, right: Point, curve: Curve) -> Point {
    let (x1, y1) = match left {
        Point::Infinity => return right,
        Point::Affine(x, y) => (x, y),
    };
    let (x2, y2) = match right {
        Point::Infinity => return left,
        Point::Affine(x, y) => (x, y),
    };
    if x1 == x2 && modular_sum(y1, y2, curve.p) == 0 {
        return Point::Infinity;
    }
    let (numerator, denominator) = if x1 == x2 {
        (
            modular_sum(
                modular_mul(3, modular_mul(x1, x1, curve.p), curve.p),
                curve.a,
                curve.p,
            ),
            modular_mul(2, y1, curve.p),
        )
    } else {
        (
            modular_sub(y2, y1, curve.p),
            modular_sub(x2, x1, curve.p),
        )
    };
    assert_ne!(denominator, 0, "invalid addition denominator");
    let slope = modular_mul(
        numerator,
        modular_pow(denominator, curve.p - 2, curve.p),
        curve.p,
    );
    let x3 = modular_sub(
        modular_sub(modular_mul(slope, slope, curve.p), x1, curve.p),
        x2,
        curve.p,
    );
    let y3 = modular_sub(
        modular_mul(slope, modular_sub(x1, x3, curve.p), curve.p),
        y1,
        curve.p,
    );
    Point::Affine(x3, y3)
}

fn on_curve(point: Point, curve: Curve) -> bool {
    match point {
        Point::Infinity => true,
        Point::Affine(x, y) => {
            x < curve.p
                && y < curve.p
                && modular_mul(y, y, curve.p)
                    == modular_sum(
                        modular_sum(
                            modular_mul(modular_mul(x, x, curve.p), x, curve.p),
                            modular_mul(curve.a, x, curve.p),
                            curve.p,
                        ),
                        curve.b,
                        curve.p,
                    )
        }
    }
}

fn parse_u64(value: Option<&str>, label: &str) -> Result<u64, String> {
    value
        .ok_or_else(|| format!("missing {label}"))?
        .parse::<u64>()
        .map_err(|e| format!("invalid {label}: {e}"))
}

fn parse_usize(value: Option<&str>, label: &str) -> Result<usize, String> {
    value
        .ok_or_else(|| format!("missing {label}"))?
        .parse::<usize>()
        .map_err(|e| format!("invalid {label}: {e}"))
}

fn parse_input(input: &str) -> Result<(Curve, Vec<Point>, Vec<Target>), String> {
    let mut lines = input.lines();
    let header = lines.next().ok_or("empty input")?;
    let mut fields = header.split_whitespace();
    if fields.next() != Some("curve") {
        return Err("expected curve header".into());
    }
    let p = parse_u64(fields.next(), "p")?;
    let a = parse_u64(fields.next(), "a")?;
    let b = parse_u64(fields.next(), "b")?;
    let r = parse_u64(fields.next(), "r")?;
    let nbase = parse_usize(fields.next(), "nbase")?;
    let ntarget = parse_usize(fields.next(), "ntarget")?;
    if fields.next().is_some() || p <= 3 || a >= p || b >= p || nbase == 0 || nbase % 2 != 0
        || nbase > u16::MAX as usize || r <= 3
    {
        return Err("invalid curve header or base size".into());
    }
    let curve = Curve { p, a, b, r };
    let mut base = Vec::with_capacity(nbase);
    for index in 0..nbase {
        let line = lines.next().ok_or("missing base line")?;
        let mut f = line.split_whitespace();
        if f.next() != Some("base") || parse_usize(f.next(), "base id")? != index {
            return Err(format!("invalid base id at {index}"));
        }
        let point = Point::Affine(parse_u64(f.next(), "base x")?, parse_u64(f.next(), "base y")?);
        if f.next().is_some() || !on_curve(point, curve) {
            return Err(format!("invalid base point at {index}"));
        }
        base.push(point);
    }
    for index in (0..nbase).step_by(2) {
        if negate(base[index], p) != base[index + 1] {
            return Err(format!("base signed pair invalid at {index}"));
        }
    }
    let mut targets = Vec::with_capacity(ntarget);
    for index in 0..ntarget {
        let line = lines.next().ok_or("missing target line")?;
        let mut f = line.split_whitespace();
        if f.next() != Some("target") || parse_usize(f.next(), "target id")? != index {
            return Err(format!("invalid target id at {index}"));
        }
        let alpha = parse_u64(f.next(), "alpha")?;
        let beta = parse_u64(f.next(), "beta")?;
        let point = Point::Affine(parse_u64(f.next(), "target x")?, parse_u64(f.next(), "target y")?);
        if f.next().is_some() || alpha >= r || beta == 0 || beta >= r || !on_curve(point, curve) {
            return Err(format!("invalid target at {index}"));
        }
        targets.push(Target { id: index, alpha, beta, point });
    }
    if lines.any(|line| !line.trim().is_empty()) {
        return Err("extra input lines".into());
    }
    Ok((curve, base, targets))
}

fn run(path: &str) -> Result<(), String> {
    let input = fs::read_to_string(path).map_err(|e| format!("read input: {e}"))?;
    let (curve, base, targets) = parse_input(&input)?;
    let n = base.len();
    let count = n.checked_mul(n + 1).ok_or("pair count overflow")? / 2;
    let mut pairs = Vec::with_capacity(count);
    for i in 0..n {
        for j in i..n {
            pairs.push(Pair { sum: add(base[i], base[j], curve), i: i as u16, j: j as u16 });
        }
    }
    pairs.sort_unstable_by_key(|pair| pair.sum);
    let mut output = BufWriter::new(io::stdout().lock());
    writeln!(output, "collector-v1\t{}\t{}\t{}\t{}", curve.p, curve.r, n, targets.len())
        .map_err(|e| e.to_string())?;
    for target in targets {
        let mut found: HashSet<[u16; 3]> = HashSet::new();
        for (k, point) in base.iter().enumerate() {
            let residual = add(target.point, negate(*point, curve.p), curve);
            let mut lo = pairs.partition_point(|pair| pair.sum < residual);
            while lo < pairs.len() && pairs[lo].sum == residual {
                let pair = pairs[lo];
                let mut triple = [pair.i, pair.j, k as u16];
                triple.sort_unstable();
                found.insert(triple);
                lo += 1;
            }
        }
        let mut triples: Vec<_> = found.into_iter().collect();
        triples.sort_unstable();
        let mut ordered = 0_u64;
        let mut useful = 0_u64;
        for triple in &triples {
            let [i, j, k] = *triple;
            ordered += if i == k { 1 } else if i == j || j == k { 3 } else { 6 };
            if i != j && j != k && i / 2 != j / 2 && j / 2 != k / 2 && i / 2 != k / 2 {
                useful += 1;
            }
        }
        writeln!(output, "target\t{}\t{}\t{}\t{}\t{}\t{}", target.id, target.alpha, target.beta, triples.len(), ordered, useful)
            .map_err(|e| e.to_string())?;
        for [i, j, k] in triples {
            writeln!(output, "triple\t{}\t{}\t{}\t{}", target.id, i, j, k)
                .map_err(|e| e.to_string())?;
        }
    }
    output.flush().map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    let mut args = env::args();
    let program = args.next().unwrap_or_else(|| "collector".into());
    let Some(path) = args.next() else {
        eprintln!("usage: {program} INPUT");
        std::process::exit(2);
    };
    if args.next().is_some() {
        eprintln!("usage: {program} INPUT");
        std::process::exit(2);
    }
    if let Err(error) = run(&path) {
        eprintln!("collector error: {error}");
        std::process::exit(1);
    }
}
