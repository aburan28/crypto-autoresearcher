//! Native-XOR balanced-S5 SAT control over point-defined Koblitz bases.
//!
//! Four factor-base points are constrained to sum to one published synthetic
//! target through three balanced S3 links.  All SAT models are lifted through
//! the original curve group; no unknown, external, or production point is used.

#![recursion_limit = "256"]

use crypto_lib::binary_ecc::curve::point_neg;
use crypto_lib::binary_ecc::{BinaryPoint, F2mElement};
use crypto_lib::cryptanalysis::binary_semaev::binary_semaev_s3;
use crypto_lib::cryptanalysis::koblitz_groebner::FieldStructure;
use crypto_lib::cryptanalysis::koblitz_index_calculus::{point_key, points_with_x, KoblitzCurve};
use crypto_lib::cryptanalysis::sat::{to_dimacs_xor, Lit, SolveResult, Solver};
use num_bigint::BigUint;
use num_traits::ToPrimitive;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use rayon::prelude::*;
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::process::Command;
use std::time::Instant;

const TASK_ID: &str = "TASK-KIC-S5-THREE-PAIRINGS-XOR-20260910";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum TargetClass {
    Planted,
    Natural,
    ProvenNegative,
    Scalar,
}

impl TargetClass {
    fn parse(value: &str) -> Self {
        match value {
            "planted" => Self::Planted,
            "natural" => Self::Natural,
            "proven_negative" => Self::ProvenNegative,
            "scalar" => Self::Scalar,
            _ => panic!("unknown target class {value}"),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Planted => "planted",
            Self::Natural => "natural",
            Self::ProvenNegative => "proven_negative",
            Self::Scalar => "scalar",
        }
    }
}

#[derive(Clone)]
struct PointBase {
    points: Vec<BinaryPoint>,
    point_labels: Vec<(usize, u64)>,
    representatives: Vec<BinaryPoint>,
    x_codes: Vec<u64>,
    orbit_columns: usize,
    signed_size: usize,
    scanned_x: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct PairXEntry {
    left_index: usize,
    right_index: usize,
    sum_code: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct CompatiblePairEdge {
    left_entry_index: usize,
    right_entry_index: usize,
}

fn affine_coordinates(point: &BinaryPoint) -> Option<[u64; 2]> {
    match point {
        BinaryPoint::Infinity => None,
        BinaryPoint::Affine { x, y } => Some([
            x.raw_bits().first().copied().unwrap_or(0),
            y.raw_bits().first().copied().unwrap_or(0),
        ]),
    }
}

fn balanced_orbits(
    subgroup_order: &BigUint,
    signed_size: usize,
    numerator: u32,
    denominator: u32,
) -> usize {
    let rhs = subgroup_order * BigUint::from(6u32 * numerator);
    for columns in 1usize.. {
        let points = BigUint::from((signed_size * columns) as u64);
        if points.pow(3) * BigUint::from(denominator) >= rhs {
            return columns;
        }
    }
    unreachable!()
}

fn signed_orbit(curve: &KoblitzCurve, point: &BinaryPoint) -> Vec<BinaryPoint> {
    let mut by_key = BTreeMap::new();
    let mut current = point.clone();
    for _ in 0..curve.n {
        by_key
            .entry(point_key(&current))
            .or_insert_with(|| current.clone());
        let negative = point_neg(&current);
        by_key.entry(point_key(&negative)).or_insert(negative);
        current = curve.frobenius(&current);
    }
    by_key.into_values().collect()
}

fn point_defined_base(curve: &KoblitzCurve, columns: usize) -> PointBase {
    let cofactor = curve.cofactor.to_u64().unwrap();
    let mut seen_orbits = HashSet::new();
    let mut orbits = Vec::new();
    let mut scanned_x = 0u64;
    for raw_x in 0..(1u64 << curve.n) {
        scanned_x += 1;
        let x = F2mElement::from_biguint(&BigUint::from(raw_x), curve.n);
        for point in points_with_x(&curve.curve, &x) {
            let projected = curve.mul(&point, &BigUint::from(cofactor));
            if projected == BinaryPoint::Infinity {
                continue;
            }
            let orbit = signed_orbit(curve, &projected);
            let canonical = point_key(&orbit[0]);
            if !seen_orbits.insert(canonical) {
                continue;
            }
            assert!(orbit.iter().all(|member| {
                curve.mul(member, &curve.subgroup_order) == BinaryPoint::Infinity
            }));
            orbits.push(orbit);
            if orbits.len() == columns {
                break;
            }
        }
        if orbits.len() == columns {
            break;
        }
    }
    assert_eq!(orbits.len(), columns);
    orbits.sort_by_key(|orbit| point_key(&orbit[0]));
    let signed_size = orbits[0].len();
    assert!(orbits.iter().all(|orbit| orbit.len() == signed_size));
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let lambda = curve.lambda.to_u64().unwrap();
    let representatives: Vec<_> = orbits.iter().map(|orbit| orbit[0].clone()).collect();
    let mut labels_by_key = HashMap::new();
    for (column, representative) in representatives.iter().enumerate() {
        let mut current = representative.clone();
        let mut coefficient = 1u64;
        for _ in 0..curve.n {
            labels_by_key
                .entry(point_key(&current))
                .or_insert((column, coefficient));
            labels_by_key
                .entry(point_key(&point_neg(&current)))
                .or_insert((column, (modulus - coefficient) % modulus));
            current = curve.frobenius(&current);
            coefficient = ((coefficient as u128 * lambda as u128) % modulus as u128) as u64;
        }
    }
    let mut points: Vec<_> = orbits.into_iter().flatten().collect();
    points.sort_by_key(point_key);
    points.dedup_by_key(|point| point_key(point));
    assert_eq!(points.len(), columns * signed_size);
    let point_labels: Vec<_> = points
        .iter()
        .map(|point| labels_by_key[&point_key(point)])
        .collect();
    assert!(points
        .iter()
        .zip(&point_labels)
        .all(|(point, &(column, coefficient))| {
            curve.mul(&representatives[column], &BigUint::from(coefficient)) == *point
        }));
    let mut x_codes: Vec<_> = points
        .iter()
        .filter_map(|point| match point {
            BinaryPoint::Infinity => None,
            BinaryPoint::Affine { x, .. } => Some(x.raw_bits().first().copied().unwrap_or(0)),
        })
        .collect();
    x_codes.sort_unstable();
    x_codes.dedup();
    PointBase {
        points,
        point_labels,
        representatives,
        x_codes,
        orbit_columns: columns,
        signed_size,
        scanned_x,
    }
}

fn point_defined_base_from_jsonl(
    curve: &KoblitzCurve,
    columns: usize,
    path: &str,
) -> (PointBase, String, String) {
    let bytes = std::fs::read(path).expect("read KIC_FACTOR_BASE_JSONL");
    let first_line = bytes
        .split(|byte| *byte == b'\n')
        .next()
        .expect("factor-base JSONL is empty");
    let record: serde_json::Value =
        serde_json::from_slice(first_line).expect("parse factor-base JSONL header");
    assert_eq!(record["kind"], "point_defined_factor_base");
    assert_eq!(record["n"].as_u64(), Some(curve.n as u64));
    assert_eq!(record["a"].as_u64(), Some(curve.a as u64));
    assert_eq!(record["orbit_columns"].as_u64(), Some(columns as u64));
    assert_eq!(
        record["subgroup_order"].as_u64(),
        curve.subgroup_order.to_u64()
    );

    let raw_points: Vec<Option<[u64; 2]>> =
        serde_json::from_value(record["factor_base_point_coordinates"].clone())
            .expect("factor-base point coordinates");
    let raw_representatives: Vec<Option<[u64; 2]>> =
        serde_json::from_value(record["factor_base_representatives"].clone())
            .expect("factor-base representatives");
    let point_labels: Vec<(usize, u64)> =
        serde_json::from_value(record["factor_base_point_labels"].clone())
            .expect("factor-base labels");
    let decode = |raw: Option<[u64; 2]>| match raw {
        None => BinaryPoint::Infinity,
        Some([x, y]) => BinaryPoint::Affine {
            x: F2mElement::from_biguint(&BigUint::from(x), curve.n),
            y: F2mElement::from_biguint(&BigUint::from(y), curve.n),
        },
    };
    let points: Vec<_> = raw_points.into_iter().map(decode).collect();
    let representatives: Vec<_> = raw_representatives.into_iter().map(decode).collect();
    assert_eq!(points.len(), point_labels.len());
    assert_eq!(representatives.len(), columns);
    assert_eq!(
        points.len(),
        record["factor_base_points"].as_u64().unwrap() as usize
    );
    let signed_size = record["signed_automorphism_size"].as_u64().unwrap() as usize;
    assert_eq!(points.len(), columns * signed_size);
    assert!(point_labels
        .iter()
        .all(|&(column, coefficient)| column < columns && coefficient < curve.subgroup_order.to_u64().unwrap()));
    let mut x_codes: Vec<_> = points
        .iter()
        .filter_map(|point| match point {
            BinaryPoint::Infinity => None,
            BinaryPoint::Affine { x, .. } => Some(x.raw_bits().first().copied().unwrap_or(0)),
        })
        .collect();
    x_codes.sort_unstable();
    x_codes.dedup();
    (
        PointBase {
            points,
            point_labels,
            representatives,
            x_codes,
            orbit_columns: columns,
            signed_size,
            scanned_x: record["field_x_values_scanned"].as_u64().unwrap_or(0),
        },
        record["base_hash"].as_str().unwrap().to_owned(),
        blake3::hash(&bytes).to_hex().to_string(),
    )
}

fn pair_index(
    curve: &KoblitzCurve,
    points: &[BinaryPoint],
) -> HashMap<(BigUint, BigUint), (usize, usize)> {
    let mut pairs = HashMap::new();
    for left in 0..points.len() {
        for right in left..points.len() {
            let sum = curve.add(&points[left], &points[right]);
            pairs.entry(point_key(&sum)).or_insert((left, right));
        }
    }
    pairs
}

fn pair_sum_x_domain(curve: &KoblitzCurve, points: &[BinaryPoint]) -> Vec<u64> {
    let mut codes = BTreeSet::new();
    for left in 0..points.len() {
        for right in left..points.len() {
            if let BinaryPoint::Affine { x, .. } = curve.add(&points[left], &points[right]) {
                codes.insert(x.raw_bits().first().copied().unwrap_or(0));
            }
        }
    }
    codes.into_iter().collect()
}

fn pair_x_entries(curve: &KoblitzCurve, base: &PointBase) -> Vec<PairXEntry> {
    let x_index: HashMap<_, _> = base
        .x_codes
        .iter()
        .enumerate()
        .map(|(index, &code)| (code, index))
        .collect();
    let point_x_indices: Vec<_> = base
        .points
        .iter()
        .map(|point| match point {
            BinaryPoint::Infinity => unreachable!(),
            BinaryPoint::Affine { x, .. } => x_index[&x.raw_bits().first().copied().unwrap_or(0)],
        })
        .collect();
    let mut entries = BTreeSet::new();
    for left in 0..base.points.len() {
        for right in left..base.points.len() {
            let BinaryPoint::Affine { x, .. } = curve.add(&base.points[left], &base.points[right])
            else {
                continue;
            };
            let left_index = point_x_indices[left].min(point_x_indices[right]);
            let right_index = point_x_indices[left].max(point_x_indices[right]);
            entries.insert(PairXEntry {
                left_index,
                right_index,
                sum_code: x.raw_bits().first().copied().unwrap_or(0),
            });
        }
    }
    entries.into_iter().collect()
}

fn exact_four_witness(
    curve: &KoblitzCurve,
    points: &[BinaryPoint],
    pairs: &HashMap<(BigUint, BigUint), (usize, usize)>,
    target: &BinaryPoint,
) -> Option<[usize; 4]> {
    for left in 0..points.len() {
        for middle in left..points.len() {
            let first = curve.add(&points[left], &points[middle]);
            let rest = curve.add(target, &point_neg(&first));
            if let Some(&(right, last)) = pairs.get(&point_key(&rest)) {
                return Some([left, middle, right, last]);
            }
        }
    }
    None
}

fn exact_four_sum_coverage(
    curve: &KoblitzCurve,
    base: &PointBase,
    pairs: &HashMap<(BigUint, BigUint), (usize, usize)>,
) -> (usize, usize, Vec<u64>) {
    let mut pair_sums: Vec<_> = pairs
        .values()
        .map(|&(left, right)| curve.add(&base.points[left], &base.points[right]))
        .collect();
    pair_sums.sort_by_key(point_key);
    pair_sums.dedup_by_key(|point| point_key(point));
    assert_eq!(pair_sums.len(), pairs.len());

    let mut reachable = HashSet::new();
    for left in 0..pair_sums.len() {
        for right in left..pair_sums.len() {
            reachable.insert(point_key(&curve.add(&pair_sums[left], &pair_sums[right])));
        }
    }
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let mut negative_scalars = Vec::new();
    let mut target = curve.generator().clone();
    for scalar in 1..modulus {
        if !reachable.contains(&point_key(&target)) {
            negative_scalars.push(scalar);
        }
        target = curve.add(&target, curve.generator());
    }
    assert_eq!(target, BinaryPoint::Infinity);
    (pair_sums.len(), reachable.len(), negative_scalars)
}

fn exact_cancellation_witness(
    curve: &KoblitzCurve,
    base: &PointBase,
    pairs: &HashMap<(BigUint, BigUint), (usize, usize)>,
    target: &BinaryPoint,
) -> Option<[usize; 4]> {
    let &(left, right) = pairs.get(&point_key(target))?;
    let cancel = base
        .points
        .iter()
        .position(|point| *point == point_neg(&base.points[0]))?;
    let witness = [0, cancel, left, right];
    let sum = witness.iter().fold(BinaryPoint::Infinity, |sum, &index| {
        curve.add(&sum, &base.points[index])
    });
    assert_eq!(sum, *target);
    Some(witness)
}

#[derive(Clone, Copy, Default, PartialEq, Eq, PartialOrd, Ord, Hash)]
struct Mono256([u64; 4]);

impl Mono256 {
    fn variable(index: usize) -> Self {
        assert!(index < 256);
        let mut words = [0u64; 4];
        words[index / 64] = 1u64 << (index % 64);
        Self(words)
    }

    fn union(self, other: Self) -> Self {
        Self(std::array::from_fn(|index| self.0[index] | other.0[index]))
    }

    fn degree(self) -> u32 {
        self.0.iter().map(|word| word.count_ones()).sum()
    }

    fn variables(self) -> Vec<usize> {
        let mut result = Vec::new();
        for (word_index, &word) in self.0.iter().enumerate() {
            let mut remaining = word;
            while remaining != 0 {
                let bit = remaining.trailing_zeros() as usize;
                result.push(word_index * 64 + bit);
                remaining &= remaining - 1;
            }
        }
        result
    }

    fn singleton(self) -> Option<usize> {
        (self.degree() == 1).then(|| self.variables()[0])
    }

    fn eval(self, assignment: &[bool]) -> bool {
        self.variables().into_iter().all(|index| assignment[index])
    }
}

#[derive(Clone, Default)]
struct Poly256 {
    terms: BTreeSet<Mono256>,
}

impl Poly256 {
    fn one() -> Self {
        Self {
            terms: BTreeSet::from([Mono256::default()]),
        }
    }

    fn variable(index: usize) -> Self {
        Self {
            terms: BTreeSet::from([Mono256::variable(index)]),
        }
    }

    fn add(&self, other: &Self) -> Self {
        let mut terms = self.terms.clone();
        for &term in &other.terms {
            if !terms.insert(term) {
                terms.remove(&term);
            }
        }
        Self { terms }
    }

    fn mul(&self, other: &Self) -> Self {
        let mut terms = BTreeSet::new();
        for &left in &self.terms {
            for &right in &other.terms {
                let term = left.union(right);
                if !terms.insert(term) {
                    terms.remove(&term);
                }
            }
        }
        Self { terms }
    }

    fn eval(&self, assignment: &[bool]) -> bool {
        self.terms
            .iter()
            .fold(false, |parity, &term| parity ^ term.eval(assignment))
    }
}

#[derive(Clone)]
struct SymbolicField {
    coordinates: Vec<Poly256>,
}

impl SymbolicField {
    fn variables(offset: usize, n: usize) -> Self {
        Self {
            coordinates: (0..n)
                .map(|index| Poly256::variable(offset + index))
                .collect(),
        }
    }

    fn constant(value: &F2mElement, n: usize) -> Self {
        let bits = value.raw_bits().first().copied().unwrap_or(0);
        Self {
            coordinates: (0..n)
                .map(|index| {
                    if (bits >> index) & 1 == 1 {
                        Poly256::one()
                    } else {
                        Poly256::default()
                    }
                })
                .collect(),
        }
    }

    fn add(&self, other: &Self) -> Self {
        Self {
            coordinates: self
                .coordinates
                .iter()
                .zip(&other.coordinates)
                .map(|(left, right)| left.add(right))
                .collect(),
        }
    }

    fn mul(&self, other: &Self, structure: &FieldStructure) -> Self {
        let n = structure.n as usize;
        let mut coordinates = vec![Poly256::default(); n];
        for left in 0..n {
            for right in 0..n {
                let product = self.coordinates[left].mul(&other.coordinates[right]);
                let mask = structure.reduced[left][right];
                for output in 0..n {
                    if (mask >> output) & 1 == 1 {
                        coordinates[output] = coordinates[output].add(&product);
                    }
                }
            }
        }
        Self { coordinates }
    }

    fn square(&self, structure: &FieldStructure) -> Self {
        let n = structure.n as usize;
        let mut coordinates = vec![Poly256::default(); n];
        for input in 0..n {
            let mask = structure.squares[input];
            for output in 0..n {
                if (mask >> output) & 1 == 1 {
                    coordinates[output] = coordinates[output].add(&self.coordinates[input]);
                }
            }
        }
        Self { coordinates }
    }
}

fn symbolic_s3(
    left: &SymbolicField,
    right: &SymbolicField,
    third: &SymbolicField,
    b: &F2mElement,
    structure: &FieldStructure,
) -> Vec<Poly256> {
    let sum_square = left.add(right).square(structure);
    let third_square = third.square(structure);
    let product = left.mul(right, structure);
    sum_square
        .mul(&third_square, structure)
        .add(&product.mul(third, structure))
        .add(&product.square(structure))
        .add(&SymbolicField::constant(b, structure.n as usize))
        .coordinates
}

struct S5Encoding {
    solver: Solver,
    equations: Vec<Poly256>,
    problem_variables: usize,
    monomials: usize,
    selector_variables: usize,
    cardinality_auxiliaries: usize,
    domain_encoding: &'static str,
    symmetry_breaking: bool,
    pairing: usize,
    algebra_encoding: &'static str,
    multiplication_encoding: &'static str,
    pair_table_entries: usize,
    pair_selector_variables: usize,
    pair_table_propagation: &'static str,
    final_support_clauses: usize,
    final_compatible_selector_pairs: usize,
    final_s3_circuit_installed: bool,
    edge_selector_variables: usize,
    target_compatible_pair_edges: usize,
    globally_sorted_compatible_pair_edges: usize,
    edge_link_xor_rows: usize,
    edge_selector_domain_empty: bool,
}

#[derive(Default)]
struct CircuitBuilder {
    next_variable: u32,
    clauses: Vec<Vec<Lit>>,
    xors: Vec<(Vec<u32>, bool)>,
    and_gates: usize,
    karatsuba: bool,
}

impl CircuitBuilder {
    fn new(reserved_variables: usize, karatsuba: bool) -> Self {
        Self {
            next_variable: reserved_variables as u32 + 1,
            karatsuba,
            ..Self::default()
        }
    }

    fn variable(&mut self) -> u32 {
        let result = self.next_variable;
        self.next_variable += 1;
        result
    }

    fn xor_wire(&mut self, inputs: &[u32], rhs: bool) -> u32 {
        let output = self.variable();
        let mut row = Vec::with_capacity(inputs.len() + 1);
        row.push(output);
        row.extend_from_slice(inputs);
        self.xors.push((row, rhs));
        output
    }

    fn and_wire(&mut self, left: u32, right: u32) -> u32 {
        let output = self.variable();
        self.clauses
            .push(vec![-(left as Lit), -(right as Lit), output as Lit]);
        self.clauses.push(vec![left as Lit, -(output as Lit)]);
        self.clauses.push(vec![right as Lit, -(output as Lit)]);
        self.and_gates += 1;
        output
    }

    fn mux_wire(&mut self, select: u32, when_false: u32, when_true: u32) -> u32 {
        let output = self.variable();
        self.clauses.push(vec![
            select as Lit,
            -(when_false as Lit),
            output as Lit,
        ]);
        self.clauses.push(vec![
            select as Lit,
            when_false as Lit,
            -(output as Lit),
        ]);
        self.clauses.push(vec![
            -(select as Lit),
            -(when_true as Lit),
            output as Lit,
        ]);
        self.clauses.push(vec![
            -(select as Lit),
            when_true as Lit,
            -(output as Lit),
        ]);
        self.and_gates += 1;
        output
    }

    fn frobenius_wire(
        &mut self,
        input: &[u32],
        power: usize,
        structure: &FieldStructure,
    ) -> Vec<u32> {
        let n = structure.n as usize;
        assert_eq!(input.len(), n);
        let square_code = |code: u64| {
            (0..n).fold(0u64, |value, bit| {
                if (code >> bit) & 1 == 1 {
                    value ^ structure.squares[bit]
                } else {
                    value
                }
            })
        };
        let mut images: Vec<u64> = (0..n).map(|bit| 1u64 << bit).collect();
        for _ in 0..power {
            images.iter_mut().for_each(|image| *image = square_code(*image));
        }
        (0..n)
            .map(|output| {
                let inputs: Vec<u32> = (0..n)
                    .filter(|&bit| (images[bit] >> output) & 1 == 1)
                    .map(|bit| input[bit])
                    .collect();
                self.xor_wire(&inputs, false)
            })
            .collect()
    }

    fn field_xor(&mut self, left: &[u32], right: &[u32]) -> Vec<u32> {
        left.iter()
            .zip(right)
            .map(|(&a, &b)| self.xor_wire(&[a, b], false))
            .collect()
    }

    fn constrain_unsigned_less_equal(&mut self, left: &[u32], right: &[u32]) {
        assert_eq!(left.len(), right.len());
        let mut equal_prefix = None;
        for bit in (0..left.len()).rev() {
            let mut no_greater = Vec::new();
            if let Some(prefix) = equal_prefix {
                no_greater.push(-(prefix as Lit));
            }
            no_greater.push(-(left[bit] as Lit));
            no_greater.push(right[bit] as Lit);
            self.clauses.push(no_greater);
            let equal_bit = self.xor_wire(&[left[bit], right[bit]], true);
            equal_prefix = Some(match equal_prefix {
                Some(prefix) => self.and_wire(prefix, equal_bit),
                None => equal_bit,
            });
        }
    }

    fn field_square(&mut self, input: &[u32], structure: &FieldStructure) -> Vec<u32> {
        let n = structure.n as usize;
        (0..n)
            .map(|output| {
                let inputs: Vec<_> = (0..n)
                    .filter(|&index| (structure.squares[index] >> output) & 1 == 1)
                    .map(|index| input[index])
                    .collect();
                self.xor_wire(&inputs, false)
            })
            .collect()
    }

    fn field_mul(&mut self, left: &[u32], right: &[u32], structure: &FieldStructure) -> Vec<u32> {
        if self.karatsuba {
            return self.field_mul_karatsuba(left, right, structure);
        }
        let n = structure.n as usize;
        let mut products = vec![vec![0u32; n]; n];
        for i in 0..n {
            for j in 0..n {
                products[i][j] = self.and_wire(left[i], right[j]);
            }
        }
        (0..n)
            .map(|output| {
                let mut inputs = Vec::new();
                for i in 0..n {
                    for j in 0..n {
                        if (structure.reduced[i][j] >> output) & 1 == 1 {
                            inputs.push(products[i][j]);
                        }
                    }
                }
                self.xor_wire(&inputs, false)
            })
            .collect()
    }

    fn optional_xor_wire(&mut self, left: Option<u32>, right: Option<u32>) -> Option<u32> {
        match (left, right) {
            (None, value) | (value, None) => value,
            (Some(left), Some(right)) if left == right => None,
            (Some(left), Some(right)) => Some(self.xor_wire(&[left, right], false)),
        }
    }

    fn toggle_terms(destination: &mut BTreeSet<u32>, source: &BTreeSet<u32>) {
        for &variable in source {
            if !destination.insert(variable) {
                destination.remove(&variable);
            }
        }
    }

    fn karatsuba_polynomial_terms(
        &mut self,
        left: &[Option<u32>],
        right: &[Option<u32>],
    ) -> Vec<BTreeSet<u32>> {
        assert_eq!(left.len(), right.len());
        assert!(left.len().is_power_of_two());
        if left.len() == 1 {
            return vec![match (left[0], right[0]) {
                (Some(left), Some(right)) => BTreeSet::from([self.and_wire(left, right)]),
                _ => BTreeSet::new(),
            }];
        }
        let half = left.len() / 2;
        let (left_low, left_high) = left.split_at(half);
        let (right_low, right_high) = right.split_at(half);
        let left_sum: Vec<_> = left_low
            .iter()
            .zip(left_high)
            .map(|(&low, &high)| self.optional_xor_wire(low, high))
            .collect();
        let right_sum: Vec<_> = right_low
            .iter()
            .zip(right_high)
            .map(|(&low, &high)| self.optional_xor_wire(low, high))
            .collect();
        let low = self.karatsuba_polynomial_terms(left_low, right_low);
        let high = self.karatsuba_polynomial_terms(left_high, right_high);
        let middle = self.karatsuba_polynomial_terms(&left_sum, &right_sum);
        let mut result = vec![BTreeSet::new(); 2 * left.len() - 1];
        for index in 0..low.len() {
            Self::toggle_terms(&mut result[index], &low[index]);
            Self::toggle_terms(&mut result[half + index], &low[index]);
        }
        for index in 0..middle.len() {
            Self::toggle_terms(&mut result[half + index], &middle[index]);
        }
        for index in 0..high.len() {
            Self::toggle_terms(&mut result[half + index], &high[index]);
            Self::toggle_terms(&mut result[2 * half + index], &high[index]);
        }
        result
    }

    fn field_mul_karatsuba(
        &mut self,
        left: &[u32],
        right: &[u32],
        structure: &FieldStructure,
    ) -> Vec<u32> {
        let n = structure.n as usize;
        assert_eq!(left.len(), n);
        assert_eq!(right.len(), n);
        let padded = n.next_power_of_two();
        let mut left_padded: Vec<Option<u32>> = left.iter().copied().map(Some).collect();
        let mut right_padded: Vec<Option<u32>> = right.iter().copied().map(Some).collect();
        left_padded.resize(padded, None);
        right_padded.resize(padded, None);
        let product = self.karatsuba_polynomial_terms(&left_padded, &right_padded);
        let mut reduced = vec![BTreeSet::new(); n];
        for (exponent, terms) in product.iter().take(2 * n - 1).enumerate() {
            let left_exponent = exponent.min(n - 1);
            let right_exponent = exponent - left_exponent;
            let mask = structure.reduced[left_exponent][right_exponent];
            for output in 0..n {
                if (mask >> output) & 1 == 1 {
                    Self::toggle_terms(&mut reduced[output], terms);
                }
            }
        }
        reduced
            .into_iter()
            .map(|terms| self.xor_wire(&terms.into_iter().collect::<Vec<_>>(), false))
            .collect()
    }

    fn field_mul_constant(
        &mut self,
        input: &[u32],
        constant: &F2mElement,
        structure: &FieldStructure,
    ) -> Vec<u32> {
        let n = structure.n as usize;
        let constant_bits = constant.raw_bits().first().copied().unwrap_or(0);
        (0..n)
            .map(|output| {
                let mut inputs = Vec::new();
                for left in 0..n {
                    for right in 0..n {
                        if (constant_bits >> right) & 1 == 1
                            && (structure.reduced[left][right] >> output) & 1 == 1
                        {
                            inputs.push(input[left]);
                        }
                    }
                }
                self.xor_wire(&inputs, false)
            })
            .collect()
    }

    fn field_variables(&mut self, n: usize) -> Vec<u32> {
        (0..n).map(|_| self.variable()).collect()
    }

    fn constrain_field_constant(&mut self, input: &[u32], value: u64) {
        for (bit, &variable) in input.iter().enumerate() {
            let literal = if (value >> bit) & 1 == 1 {
                variable as Lit
            } else {
                -(variable as Lit)
            };
            self.clauses.push(vec![literal]);
        }
    }

    fn field_inverse_witness(
        &mut self,
        input: &[u32],
        structure: &FieldStructure,
    ) -> Vec<u32> {
        let inverse = self.field_variables(structure.n as usize);
        let product = self.field_mul(input, &inverse, structure);
        self.constrain_field_constant(&product, 1);
        inverse
    }

    /// Directional regular S3 root circuit.  It covers the branch where
    /// `left`, `right`, and `left+right` are nonzero.  The inverse witnesses
    /// enforce those regularity conditions without enumerating point pairs.
    fn constrain_s3_root(
        &mut self,
        left: &[u32],
        right: &[u32],
        third: &[u32],
        root_selector: u32,
        b: &F2mElement,
        structure: &FieldStructure,
    ) {
        assert!(structure.n % 2 == 1, "half-trace root circuit needs odd n");
        let sum = self.field_xor(left, right);
        let a = self.field_square(&sum, structure);
        let product = self.field_mul(left, right, structure);
        let product_square = self.field_square(&product, structure);
        let b_bits = b.raw_bits().first().copied().unwrap_or(0);
        let c: Vec<_> = product_square
            .iter()
            .enumerate()
            .map(|(bit, &wire)| self.xor_wire(&[wire], (b_bits >> bit) & 1 == 1))
            .collect();
        let inverse_a = self.field_inverse_witness(&a, structure);
        let inverse_product_square = self.field_inverse_witness(&product_square, structure);
        let q = self.field_mul(&product, &inverse_a, structure);
        let ca = self.field_mul(&c, &a, structure);
        let d = self.field_mul(&ca, &inverse_product_square, structure);

        let mut half_trace = d.clone();
        let mut power = d.clone();
        for _ in 0..(structure.n - 1) / 2 {
            let square = self.field_square(&power, structure);
            power = self.field_square(&square, structure);
            half_trace = self.field_xor(&half_trace, &power);
        }
        let half_trace_square = self.field_square(&half_trace, structure);
        for bit in 0..structure.n as usize {
            self.xors.push((
                vec![half_trace_square[bit], half_trace[bit], d[bit]],
                false,
            ));
        }
        let mut selected_root = half_trace;
        selected_root[0] = self.xor_wire(&[selected_root[0], root_selector], false);
        let computed_third = self.field_mul(&q, &selected_root, structure);
        for bit in 0..structure.n as usize {
            self.xors
                .push((vec![third[bit], computed_third[bit]], false));
        }
    }

    fn constrain_s3(
        &mut self,
        left: &[u32],
        right: &[u32],
        third: &[u32],
        b: &F2mElement,
        structure: &FieldStructure,
    ) {
        let sum = self.field_xor(left, right);
        let sum_square = self.field_square(&sum, structure);
        let third_square = self.field_square(third, structure);
        let term_one = self.field_mul(&sum_square, &third_square, structure);
        let product = self.field_mul(left, right, structure);
        let term_two = self.field_mul(&product, third, structure);
        let product_square = self.field_square(&product, structure);
        let b_bits = b.raw_bits().first().copied().unwrap_or(0);
        for output in 0..structure.n as usize {
            self.xors.push((
                vec![term_one[output], term_two[output], product_square[output]],
                (b_bits >> output) & 1 == 1,
            ));
        }
    }

    fn constrain_s3_constant_third(
        &mut self,
        left: &[u32],
        right: &[u32],
        third: &F2mElement,
        b: &F2mElement,
        structure: &FieldStructure,
    ) {
        // In characteristic two, ((left + right) * third)^2 is the first
        // S3 term.  Multiplication by the published target is linear, so the
        // only nonlinear multiplication in this final link is left * right.
        let sum = self.field_xor(left, right);
        let sum_times_third = self.field_mul_constant(&sum, third, structure);
        let term_one = self.field_square(&sum_times_third, structure);
        let product = self.field_mul(left, right, structure);
        let term_two = self.field_mul_constant(&product, third, structure);
        let product_square = self.field_square(&product, structure);
        let b_bits = b.raw_bits().first().copied().unwrap_or(0);
        for output in 0..structure.n as usize {
            self.xors.push((
                vec![term_one[output], term_two[output], product_square[output]],
                (b_bits >> output) & 1 == 1,
            ));
        }
    }

    fn finish(self) -> Solver {
        let mut solver = Solver::new(self.next_variable - 1);
        for clause in self.clauses {
            assert!(solver.add_clause(clause));
        }
        for (variables, rhs) in self.xors {
            assert!(solver.add_xor(&variables, rhs));
        }
        solver
    }
}

fn add_coordinate_domain(solver: &mut Solver, offset: usize, width: usize, codes: &[u64]) {
    fn visit(solver: &mut Solver, offset: usize, bit: usize, codes: &[u64], prefix: &mut Vec<Lit>) {
        if codes.is_empty() {
            assert!(solver.add_clause(prefix.clone()));
            return;
        }
        if bit == 0 {
            return;
        }
        let current = bit - 1;
        let split = codes.partition_point(|code| (code >> current) & 1 == 0);
        let variable = (offset + current + 1) as Lit;
        prefix.push(variable);
        visit(solver, offset, current, &codes[..split], prefix);
        *prefix.last_mut().unwrap() = -variable;
        visit(solver, offset, current, &codes[split..], prefix);
        prefix.pop();
    }
    visit(solver, offset, width, codes, &mut Vec::new());
}

fn install_domain_constraints(
    solver: &mut Solver,
    width: usize,
    domain: &[u64],
    one_hot_domain: bool,
    symmetry_breaking: bool,
    selector_offset: usize,
    cardinality_offset: usize,
    selector_variables: usize,
) {
    assert!(!domain.is_empty());
    if one_hot_domain {
        let mut cardinality_prefixes: Vec<Vec<u32>> = Vec::with_capacity(4);
        for summand in 0..4 {
            let selectors: Vec<u32> = (0..domain.len())
                .map(|index| (selector_offset + summand * domain.len() + index + 1) as u32)
                .collect();
            assert!(solver.add_clause(selectors.iter().map(|&value| value as Lit).collect()));
            if selectors.len() > 1 {
                let auxiliary: Vec<u32> = (0..selectors.len() - 1)
                    .map(|index| {
                        (cardinality_offset + summand * (domain.len() - 1) + index + 1) as u32
                    })
                    .collect();
                assert!(solver.add_clause(vec![-(selectors[0] as Lit), auxiliary[0] as Lit]));
                for index in 1..selectors.len() - 1 {
                    assert!(solver
                        .add_clause(vec![-(selectors[index] as Lit), auxiliary[index] as Lit,]));
                    assert!(solver.add_clause(vec![
                        -(auxiliary[index - 1] as Lit),
                        auxiliary[index] as Lit,
                    ]));
                    assert!(solver.add_clause(vec![
                        -(selectors[index] as Lit),
                        -(auxiliary[index - 1] as Lit),
                    ]));
                }
                assert!(solver.add_clause(vec![
                    -(selectors[selectors.len() - 1] as Lit),
                    -(auxiliary[auxiliary.len() - 1] as Lit),
                ]));
                cardinality_prefixes.push(auxiliary);
            } else {
                cardinality_prefixes.push(Vec::new());
            }
            for bit in 0..width {
                let mut parity = vec![(summand * width + bit + 1) as u32];
                parity.extend(
                    domain
                        .iter()
                        .zip(&selectors)
                        .filter_map(|(&code, &selector)| {
                            (((code >> bit) & 1) == 1).then_some(selector)
                        }),
                );
                assert!(solver.add_xor(&parity, false));
            }
        }
        if symmetry_breaking {
            for summand in 0..3 {
                for (&left_prefix, &right_prefix) in cardinality_prefixes[summand]
                    .iter()
                    .zip(&cardinality_prefixes[summand + 1])
                {
                    assert!(solver.add_clause(vec![-(right_prefix as Lit), left_prefix as Lit]));
                }
            }
        }
        let priorities: Vec<u32> = (0..selector_variables)
            .map(|index| (selector_offset + index + 1) as u32)
            .collect();
        solver.set_branch_priority(&priorities);
    } else {
        for summand in 0..4 {
            add_coordinate_domain(solver, summand * width, width, domain);
        }
        solver.set_branch_priority(&(1..=(4 * width) as u32).collect::<Vec<_>>());
    }
}

fn install_binary_index_domain(
    solver: &mut Solver,
    coordinate_width: usize,
    domain: &[u64],
    index_offset: usize,
    index_width: usize,
) {
    assert!(!domain.is_empty());
    assert!(domain.windows(2).all(|window| window[0] < window[1]));
    let allowed_indices: Vec<u64> = (0..domain.len() as u64).collect();
    for summand in 0..4 {
        let offset = index_offset + summand * index_width;
        add_coordinate_domain(solver, offset, index_width, &allowed_indices);
        for (index, &code) in domain.iter().enumerate() {
            let mut not_selected = Vec::with_capacity(index_width);
            for bit in 0..index_width {
                let variable = (offset + bit + 1) as Lit;
                not_selected.push(if (index >> bit) & 1 == 1 {
                    -variable
                } else {
                    variable
                });
            }
            for bit in 0..coordinate_width {
                let mut clause = not_selected.clone();
                let coordinate = (summand * coordinate_width + bit + 1) as Lit;
                clause.push(if (code >> bit) & 1 == 1 {
                    coordinate
                } else {
                    -coordinate
                });
                assert!(solver.add_clause(clause));
            }
        }
    }
    let priorities: Vec<u32> = (0..4 * index_width)
        .map(|index| (index_offset + index + 1) as u32)
        .collect();
    solver.set_branch_priority(&priorities);
}

fn install_binary_index_range(
    solver: &mut Solver,
    domain_len: usize,
    index_offset: usize,
    index_width: usize,
) {
    assert!(domain_len > 0);
    let allowed_indices: Vec<u64> = (0..domain_len as u64).collect();
    for summand in 0..4 {
        add_coordinate_domain(
            solver,
            index_offset + summand * index_width,
            index_width,
            &allowed_indices,
        );
    }
    let priorities: Vec<u32> = (0..4 * index_width)
        .map(|index| (index_offset + index + 1) as u32)
        .collect();
    solver.set_branch_priority(&priorities);
}

fn install_sequential_exactly_one(
    solver: &mut Solver,
    selector_offset: usize,
    cardinality_offset: usize,
    count: usize,
) {
    assert!(count > 0);
    let selectors: Vec<u32> = (0..count)
        .map(|index| (selector_offset + index + 1) as u32)
        .collect();
    assert!(solver.add_clause(selectors.iter().map(|&value| value as Lit).collect()));
    if count == 1 {
        return;
    }
    let auxiliary: Vec<u32> = (0..count - 1)
        .map(|index| (cardinality_offset + index + 1) as u32)
        .collect();
    assert!(solver.add_clause(vec![-(selectors[0] as Lit), auxiliary[0] as Lit]));
    for index in 1..count - 1 {
        assert!(solver.add_clause(vec![-(selectors[index] as Lit), auxiliary[index] as Lit,]));
        assert!(solver.add_clause(vec![
            -(auxiliary[index - 1] as Lit),
            auxiliary[index] as Lit,
        ]));
        assert!(solver.add_clause(vec![
            -(selectors[index] as Lit),
            -(auxiliary[index - 1] as Lit),
        ]));
    }
    assert!(solver.add_clause(vec![
        -(selectors[count - 1] as Lit),
        -(auxiliary[count - 2] as Lit),
    ]));
}

fn install_pair_table_link(
    solver: &mut Solver,
    entries: &[PairXEntry],
    selector_offset: usize,
    cardinality_offset: usize,
    factor_index_offset: usize,
    index_width: usize,
    left_summand: usize,
    right_summand: usize,
    output_offset: usize,
    field_width: usize,
    direct_implications: bool,
    reverse_support: bool,
) {
    install_sequential_exactly_one(solver, selector_offset, cardinality_offset, entries.len());
    if direct_implications {
        // With exactly one table entry selected these clauses are already
        // implied by the coordinate XORs. They expose that implication to
        // ordinary unit propagation under partial index assignments.
        for (index, entry) in entries.iter().enumerate() {
            let selector = (selector_offset + index + 1) as Lit;
            for (offset, width, code) in [
                (
                    factor_index_offset + left_summand * index_width,
                    index_width,
                    entry.left_index as u64,
                ),
                (
                    factor_index_offset + right_summand * index_width,
                    index_width,
                    entry.right_index as u64,
                ),
                (output_offset, field_width, entry.sum_code),
            ] {
                for bit in 0..width {
                    let variable = (offset + bit + 1) as Lit;
                    let value = if (code >> bit) & 1 == 1 {
                        variable
                    } else {
                        -variable
                    };
                    assert!(solver.add_clause(vec![-selector, value]));
                }
            }
        }
    }
    if reverse_support {
        assert!(direct_implications);
        let factor_count = entries.iter().map(|entry| entry.right_index).max().unwrap() + 1;
        let mut by_pair: BTreeMap<(usize, usize), Vec<u32>> = BTreeMap::new();
        for (index, entry) in entries.iter().enumerate() {
            by_pair
                .entry((entry.left_index, entry.right_index))
                .or_default()
                .push((selector_offset + index + 1) as u32);
        }
        for left_index in 0..factor_count {
            for right_index in left_index..factor_count {
                let mut clause = Vec::with_capacity(2 * index_width + 2);
                for (summand, value) in [(left_summand, left_index), (right_summand, right_index)] {
                    for bit in 0..index_width {
                        let variable =
                            (factor_index_offset + summand * index_width + bit + 1) as Lit;
                        clause.push(if (value >> bit) & 1 == 1 {
                            -variable
                        } else {
                            variable
                        });
                    }
                }
                if let Some(selectors) = by_pair.get(&(left_index, right_index)) {
                    clause.extend(selectors.iter().map(|&value| value as Lit));
                }
                assert!(solver.add_clause(clause));
            }
        }
    }
    for bit in 0..index_width {
        let mut left_row =
            vec![(factor_index_offset + left_summand * index_width + bit + 1) as u32];
        let mut right_row =
            vec![(factor_index_offset + right_summand * index_width + bit + 1) as u32];
        for (index, entry) in entries.iter().enumerate() {
            let selector = (selector_offset + index + 1) as u32;
            if (entry.left_index >> bit) & 1 == 1 {
                left_row.push(selector);
            }
            if (entry.right_index >> bit) & 1 == 1 {
                right_row.push(selector);
            }
        }
        assert!(solver.add_xor(&left_row, false));
        assert!(solver.add_xor(&right_row, false));
    }
    for bit in 0..field_width {
        let mut row = vec![(output_offset + bit + 1) as u32];
        row.extend(entries.iter().enumerate().filter_map(|(index, entry)| {
            (((entry.sum_code >> bit) & 1) == 1).then_some((selector_offset + index + 1) as u32)
        }));
        assert!(solver.add_xor(&row, false));
    }
}

fn final_compatible_x_codes(
    curve: &KoblitzCurve,
    target_x: &F2mElement,
    entries: &[PairXEntry],
) -> BTreeMap<u64, BTreeSet<u64>> {
    let target_points = points_with_x(&curve.curve, target_x);
    assert!(!target_points.is_empty());
    let unique_codes: BTreeSet<_> = entries.iter().map(|entry| entry.sum_code).collect();
    let mut compatible_codes: BTreeMap<u64, BTreeSet<u64>> = BTreeMap::new();
    for &left_code in &unique_codes {
        let left_x = F2mElement::from_biguint(&BigUint::from(left_code), curve.n);
        let left_points = points_with_x(&curve.curve, &left_x);
        assert!(!left_points.is_empty());
        for left in &left_points {
            for target in &target_points {
                if let BinaryPoint::Affine { x, .. } = curve.add(left, target) {
                    let right_code = x.raw_bits().first().copied().unwrap_or(0);
                    if unique_codes.contains(&right_code) {
                        compatible_codes
                            .entry(left_code)
                            .or_default()
                            .insert(right_code);
                    }
                }
            }
        }
    }
    compatible_codes
}

fn pairing_factor_indices(pairing: usize) -> [usize; 4] {
    match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    }
}

fn edge_factor_indices(
    edge: &CompatiblePairEdge,
    entries: &[PairXEntry],
    pairing: usize,
) -> [usize; 4] {
    let pairing_indices = pairing_factor_indices(pairing);
    let left = entries[edge.left_entry_index];
    let right = entries[edge.right_entry_index];
    let mut indices = [0usize; 4];
    indices[pairing_indices[0]] = left.left_index;
    indices[pairing_indices[1]] = left.right_index;
    indices[pairing_indices[2]] = right.left_index;
    indices[pairing_indices[3]] = right.right_index;
    indices
}

/// Construct the exact target-dependent join of two retained pair-table rows.
///
/// The first count is the complete compatible entry-pair join before the
/// global x-index ordering constraint.  The returned deterministic edge list
/// contains exactly the compatible rows that also satisfy that global order
/// for this pairing.  Pre-filtering those rows is equivalent to retaining the
/// four binary-index comparators in the SAT formulation.
fn target_compatible_pair_edges(
    curve: &KoblitzCurve,
    target_x: &F2mElement,
    entries: &[PairXEntry],
    pairing: usize,
) -> (usize, Vec<CompatiblePairEdge>) {
    let compatible_codes = final_compatible_x_codes(curve, target_x, entries);
    let mut entries_by_code: BTreeMap<u64, Vec<usize>> = BTreeMap::new();
    for (index, entry) in entries.iter().enumerate() {
        entries_by_code
            .entry(entry.sum_code)
            .or_default()
            .push(index);
    }
    let mut all_edges = Vec::new();
    for (left_entry_index, left_entry) in entries.iter().enumerate() {
        let Some(right_codes) = compatible_codes.get(&left_entry.sum_code) else {
            continue;
        };
        for right_code in right_codes {
            if let Some(right_indices) = entries_by_code.get(right_code) {
                all_edges.extend(right_indices.iter().map(|&right_entry_index| {
                    CompatiblePairEdge {
                        left_entry_index,
                        right_entry_index,
                    }
                }));
            }
        }
    }
    all_edges.sort_unstable();
    all_edges.dedup();
    let compatible_before_global_sort = all_edges.len();
    all_edges.retain(|edge| {
        edge_factor_indices(edge, entries, pairing)
            .windows(2)
            .all(|window| window[0] <= window[1])
    });
    (compatible_before_global_sort, all_edges)
}

fn install_target_compatible_edge_link(
    solver: &mut Solver,
    domain: &[u64],
    entries: &[PairXEntry],
    edges: &[CompatiblePairEdge],
    pairing: usize,
    field_width: usize,
    factor_index_offset: usize,
    index_width: usize,
    selector_offset: usize,
    cardinality_offset: usize,
) -> usize {
    if edges.is_empty() {
        // An empty exact join is a mathematical contradiction.  Keep the
        // empty clause in the solver so extended-DIMACS export remains UNSAT.
        assert!(!solver.add_clause(Vec::new()));
        return 0;
    }
    install_sequential_exactly_one(solver, selector_offset, cardinality_offset, edges.len());

    let selector = |edge_index: usize| (selector_offset + edge_index + 1) as u32;
    let edge_factor_indices: Vec<_> = edges
        .iter()
        .map(|edge| edge_factor_indices(edge, entries, pairing))
        .collect();
    let mut xor_rows = 0usize;
    for summand in 0..4 {
        for bit in 0..index_width {
            let mut row = vec![(factor_index_offset + summand * index_width + bit + 1) as u32];
            row.extend(edge_factor_indices.iter().enumerate().filter_map(
                |(edge_index, indices)| {
                    (((indices[summand] >> bit) & 1) == 1).then_some(selector(edge_index))
                },
            ));
            assert!(solver.add_xor(&row, false));
            xor_rows += 1;
        }
        for bit in 0..field_width {
            let mut row = vec![(summand * field_width + bit + 1) as u32];
            row.extend(edge_factor_indices.iter().enumerate().filter_map(
                |(edge_index, indices)| {
                    let factor_index = indices[summand];
                    (((domain[factor_index] >> bit) & 1) == 1).then_some(selector(edge_index))
                },
            ));
            assert!(solver.add_xor(&row, false));
            xor_rows += 1;
        }
    }
    for (intermediate, entry_side) in [(0usize, true), (1usize, false)] {
        for bit in 0..field_width {
            let mut row = vec![((4 + intermediate) * field_width + bit + 1) as u32];
            row.extend(edges.iter().enumerate().filter_map(|(edge_index, edge)| {
                let entry_index = if entry_side {
                    edge.left_entry_index
                } else {
                    edge.right_entry_index
                };
                (((entries[entry_index].sum_code >> bit) & 1) == 1).then_some(selector(edge_index))
            }));
            assert!(solver.add_xor(&row, false));
            xor_rows += 1;
        }
    }
    solver.set_branch_priority(&(0..edges.len()).map(selector).collect::<Vec<_>>());
    xor_rows
}

fn install_final_pair_compatibility(
    solver: &mut Solver,
    curve: &KoblitzCurve,
    target_x: &F2mElement,
    entries: &[PairXEntry],
    left_selector_offset: usize,
    right_selector_offset: usize,
) -> (usize, usize) {
    let compatible_codes = final_compatible_x_codes(curve, target_x, entries);
    let mut entries_by_code: BTreeMap<u64, Vec<usize>> = BTreeMap::new();
    for (index, entry) in entries.iter().enumerate() {
        entries_by_code
            .entry(entry.sum_code)
            .or_default()
            .push(index);
    }
    let compatible_selector_pairs = entries
        .iter()
        .map(|entry| {
            compatible_codes
                .get(&entry.sum_code)
                .into_iter()
                .flatten()
                .map(|code| entries_by_code.get(code).map_or(0, Vec::len))
                .sum::<usize>()
        })
        .sum();
    let mut installed_clauses = 0usize;
    for (left_index, left_entry) in entries.iter().enumerate() {
        let mut clause = vec![-((left_selector_offset + left_index + 1) as Lit)];
        if let Some(codes) = compatible_codes.get(&left_entry.sum_code) {
            for code in codes {
                if let Some(right_indices) = entries_by_code.get(code) {
                    clause.extend(
                        right_indices
                            .iter()
                            .map(|&index| (right_selector_offset + index + 1) as Lit),
                    );
                }
            }
        }
        installed_clauses += 1;
        if !solver.add_clause(clause) {
            return (installed_clauses, compatible_selector_pairs);
        }
    }
    for (right_index, right_entry) in entries.iter().enumerate() {
        let mut clause = vec![-((right_selector_offset + right_index + 1) as Lit)];
        for (left_code, right_codes) in &compatible_codes {
            if !right_codes.contains(&right_entry.sum_code) {
                continue;
            }
            if let Some(left_indices) = entries_by_code.get(left_code) {
                clause.extend(
                    left_indices
                        .iter()
                        .map(|&index| (left_selector_offset + index + 1) as Lit),
                );
            }
        }
        installed_clauses += 1;
        if !solver.add_clause(clause) {
            return (installed_clauses, compatible_selector_pairs);
        }
    }
    (installed_clauses, compatible_selector_pairs)
}

fn encode_balanced_s5(
    n: u32,
    target_x: &F2mElement,
    b: &F2mElement,
    structure: &FieldStructure,
    domain: &[u64],
    one_hot_domain: bool,
    symmetry_breaking: bool,
    pairing: usize,
) -> S5Encoding {
    let width = n as usize;
    let problem_variables = 6 * width;
    assert!(problem_variables <= 256);
    let x1 = SymbolicField::variables(0, width);
    let x2 = SymbolicField::variables(width, width);
    let x3 = SymbolicField::variables(2 * width, width);
    let x4 = SymbolicField::variables(3 * width, width);
    let summands = [x1, x2, x3, x4];
    let u = SymbolicField::variables(4 * width, width);
    let v = SymbolicField::variables(5 * width, width);
    let target = SymbolicField::constant(target_x, width);
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };
    let mut equations = symbolic_s3(
        &summands[pairing_indices[0]],
        &summands[pairing_indices[1]],
        &u,
        b,
        structure,
    );
    equations.extend(symbolic_s3(
        &summands[pairing_indices[2]],
        &summands[pairing_indices[3]],
        &v,
        b,
        structure,
    ));
    equations.extend(symbolic_s3(&u, &v, &target, b, structure));

    let selector_variables = if one_hot_domain { 4 * domain.len() } else { 0 };
    let cardinality_auxiliaries = if one_hot_domain {
        4 * domain.len().saturating_sub(1)
    } else {
        0
    };
    let selector_offset = problem_variables;
    let cardinality_offset = selector_offset + selector_variables;
    let mut monomial_variables = BTreeMap::new();
    for equation in &equations {
        for &term in &equation.terms {
            if term.degree() >= 2 {
                monomial_variables.insert(term, 0u32);
            }
        }
    }
    let mut next = (problem_variables + selector_variables + cardinality_auxiliaries) as u32 + 1;
    for variable in monomial_variables.values_mut() {
        *variable = next;
        next += 1;
    }
    let mut solver = Solver::new(next - 1);
    for (&monomial, &output) in &monomial_variables {
        let inputs: Vec<Lit> = monomial
            .variables()
            .into_iter()
            .map(|index| (index + 1) as Lit)
            .collect();
        let mut forward: Vec<_> = inputs.iter().map(|input| -*input).collect();
        forward.push(output as Lit);
        assert!(solver.add_clause(forward));
        for input in inputs {
            assert!(solver.add_clause(vec![input, -(output as Lit)]));
        }
    }
    for equation in &equations {
        let mut variables = Vec::new();
        let mut rhs = false;
        for &term in &equation.terms {
            match term.degree() {
                0 => rhs = !rhs,
                1 => variables.push((term.singleton().unwrap() + 1) as u32),
                _ => variables.push(monomial_variables[&term]),
            }
        }
        assert!(solver.add_xor(&variables, rhs));
    }
    if one_hot_domain {
        let mut cardinality_prefixes: Vec<Vec<u32>> = Vec::with_capacity(4);
        for summand in 0..4 {
            let selectors: Vec<u32> = (0..domain.len())
                .map(|index| (selector_offset + summand * domain.len() + index + 1) as u32)
                .collect();
            assert!(solver.add_clause(selectors.iter().map(|&value| value as Lit).collect()));
            if selectors.len() > 1 {
                let auxiliary: Vec<u32> = (0..selectors.len() - 1)
                    .map(|index| {
                        (cardinality_offset + summand * (domain.len() - 1) + index + 1) as u32
                    })
                    .collect();
                assert!(solver.add_clause(vec![-(selectors[0] as Lit), auxiliary[0] as Lit]));
                for index in 1..selectors.len() - 1 {
                    assert!(solver
                        .add_clause(vec![-(selectors[index] as Lit), auxiliary[index] as Lit,]));
                    assert!(solver.add_clause(vec![
                        -(auxiliary[index - 1] as Lit),
                        auxiliary[index] as Lit,
                    ]));
                    assert!(solver.add_clause(vec![
                        -(selectors[index] as Lit),
                        -(auxiliary[index - 1] as Lit),
                    ]));
                }
                assert!(solver.add_clause(vec![
                    -(selectors[selectors.len() - 1] as Lit),
                    -(auxiliary[auxiliary.len() - 1] as Lit),
                ]));
                cardinality_prefixes.push(auxiliary);
            } else {
                cardinality_prefixes.push(Vec::new());
            }
            for bit in 0..width {
                let mut parity = vec![(summand * width + bit + 1) as u32];
                parity.extend(
                    domain
                        .iter()
                        .zip(&selectors)
                        .filter_map(|(&code, &selector)| {
                            (((code >> bit) & 1) == 1).then_some(selector)
                        }),
                );
                assert!(solver.add_xor(&parity, false));
            }
        }
        if symmetry_breaking {
            for summand in 0..3 {
                for (&left_prefix, &right_prefix) in cardinality_prefixes[summand]
                    .iter()
                    .zip(&cardinality_prefixes[summand + 1])
                {
                    assert!(solver.add_clause(vec![-(right_prefix as Lit), left_prefix as Lit,]));
                }
            }
        }
        let priorities: Vec<u32> = (0..selector_variables)
            .map(|index| (selector_offset + index + 1) as u32)
            .collect();
        solver.set_branch_priority(&priorities);
    } else {
        for summand in 0..4 {
            add_coordinate_domain(&mut solver, summand * width, width, domain);
        }
        solver.set_branch_priority(&(1..=(4 * width) as u32).collect::<Vec<_>>());
    }
    S5Encoding {
        solver,
        equations,
        problem_variables,
        monomials: monomial_variables.len(),
        selector_variables,
        cardinality_auxiliaries,
        domain_encoding: if one_hot_domain {
            "one_hot_sequential_exactly_one"
        } else {
            "binary_coordinate_trie"
        },
        symmetry_breaking,
        pairing,
        algebra_encoding: "expanded_anf_monomials",
        multiplication_encoding: "expanded_anf",
        pair_table_entries: 0,
        pair_selector_variables: 0,
        pair_table_propagation: "not_applicable",
        final_support_clauses: 0,
        final_compatible_selector_pairs: 0,
        final_s3_circuit_installed: true,
        edge_selector_variables: 0,
        target_compatible_pair_edges: 0,
        globally_sorted_compatible_pair_edges: 0,
        edge_link_xor_rows: 0,
        edge_selector_domain_empty: false,
    }
}

fn encode_balanced_s5_factorized(
    n: u32,
    target_x: &F2mElement,
    b: &F2mElement,
    structure: &FieldStructure,
    domain: &[u64],
    domain_encoding: &str,
    symmetry_breaking: bool,
    pairing: usize,
    karatsuba: bool,
    rooted: bool,
) -> S5Encoding {
    let width = n as usize;
    let problem_variables = 6 * width;
    let one_hot_domain = domain_encoding == "one_hot";
    let binary_index_domain = domain_encoding == "binary_index";
    let index_width = if binary_index_domain {
        ((usize::BITS - domain.len().saturating_sub(1).leading_zeros()) as usize).max(1)
    } else {
        0
    };
    assert!(!rooted || domain_encoding == "trie");
    let domain_selector_variables = if one_hot_domain {
        4 * domain.len()
    } else if binary_index_domain {
        4 * index_width
    } else {
        0
    };
    let cardinality_auxiliaries = if one_hot_domain {
        4 * domain.len().saturating_sub(1)
    } else {
        0
    };
    let selector_offset = problem_variables;
    let cardinality_offset = selector_offset + domain_selector_variables;
    let root_selector_offset = cardinality_offset + cardinality_auxiliaries;
    let root_selector_variables = usize::from(rooted) * 2;
    let reserved_variables =
        problem_variables + domain_selector_variables + cardinality_auxiliaries + root_selector_variables;

    let summands: [Vec<u32>; 4] = std::array::from_fn(|summand| {
        (0..width)
            .map(|bit| (summand * width + bit + 1) as u32)
            .collect()
    });
    let u: Vec<u32> = (0..width).map(|bit| (4 * width + bit + 1) as u32).collect();
    let v: Vec<u32> = (0..width).map(|bit| (5 * width + bit + 1) as u32).collect();
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };

    let mut builder = CircuitBuilder::new(reserved_variables, karatsuba);
    if rooted {
        builder.constrain_s3_root(
            &summands[pairing_indices[0]],
            &summands[pairing_indices[1]],
            &u,
            (root_selector_offset + 1) as u32,
            b,
            structure,
        );
        builder.constrain_s3_root(
            &summands[pairing_indices[2]],
            &summands[pairing_indices[3]],
            &v,
            (root_selector_offset + 2) as u32,
            b,
            structure,
        );
    } else {
        builder.constrain_s3(
            &summands[pairing_indices[0]],
            &summands[pairing_indices[1]],
            &u,
            b,
            structure,
        );
        builder.constrain_s3(
            &summands[pairing_indices[2]],
            &summands[pairing_indices[3]],
            &v,
            b,
            structure,
        );
    }
    builder.constrain_s3_constant_third(&u, &v, target_x, b, structure);
    if binary_index_domain && symmetry_breaking {
        for summand in 0..3 {
            let left: Vec<u32> = (0..index_width)
                .map(|bit| (selector_offset + summand * index_width + bit + 1) as u32)
                .collect();
            let right: Vec<u32> = (0..index_width)
                .map(|bit| (selector_offset + (summand + 1) * index_width + bit + 1) as u32)
                .collect();
            builder.constrain_unsigned_less_equal(&left, &right);
        }
    }
    let and_gates = builder.and_gates;
    let mut solver = builder.finish();
    if binary_index_domain {
        install_binary_index_domain(&mut solver, width, domain, selector_offset, index_width);
    } else {
        install_domain_constraints(
            &mut solver,
            width,
            domain,
            one_hot_domain,
            symmetry_breaking,
            selector_offset,
            cardinality_offset,
            domain_selector_variables,
        );
    }
    if rooted {
        let mut priorities: Vec<u32> = (1..=(4 * width) as u32).collect();
        priorities.push((root_selector_offset + 1) as u32);
        priorities.push((root_selector_offset + 2) as u32);
        solver.set_branch_priority(&priorities);
    }

    S5Encoding {
        solver,
        equations: Vec::new(),
        problem_variables,
        monomials: and_gates,
        selector_variables: domain_selector_variables + root_selector_variables,
        cardinality_auxiliaries,
        domain_encoding: if one_hot_domain {
            "one_hot_sequential_exactly_one"
        } else if binary_index_domain {
            "binary_index_lookup"
        } else {
            "binary_coordinate_trie"
        },
        symmetry_breaking,
        pairing,
        algebra_encoding: if rooted {
            "factorized_half_trace_s3_root_circuit"
        } else {
            "factorized_field_arithmetic_circuit"
        },
        multiplication_encoding: if karatsuba {
            "carryless_karatsuba"
        } else {
            "schoolbook"
        },
        pair_table_entries: 0,
        pair_selector_variables: 0,
        pair_table_propagation: "not_applicable",
        final_support_clauses: 0,
        final_compatible_selector_pairs: 0,
        final_s3_circuit_installed: true,
        edge_selector_variables: 0,
        target_compatible_pair_edges: 0,
        globally_sorted_compatible_pair_edges: 0,
        edge_link_xor_rows: 0,
        edge_selector_domain_empty: false,
    }
}

fn encode_balanced_s5_lazy_domain(
    n: u32,
    domain: &[u64],
    symmetry_breaking: bool,
    pairing: usize,
) -> S5Encoding {
    let _width = n as usize;
    let problem_variables = 0;
    let index_width =
        ((usize::BITS - domain.len().saturating_sub(1).leading_zeros()) as usize).max(1);
    let selector_variables = 4 * index_width;
    let selector_offset = problem_variables;
    let mut builder = CircuitBuilder::new(problem_variables + selector_variables, false);
    if symmetry_breaking {
        for summand in 0..3 {
            let left: Vec<u32> = (0..index_width)
                .map(|bit| (selector_offset + summand * index_width + bit + 1) as u32)
                .collect();
            let right: Vec<u32> = (0..index_width)
                .map(|bit| (selector_offset + (summand + 1) * index_width + bit + 1) as u32)
                .collect();
            builder.constrain_unsigned_less_equal(&left, &right);
        }
    }
    let comparison_gates = builder.and_gates;
    let mut solver = builder.finish();
    install_binary_index_range(&mut solver, domain.len(), selector_offset, index_width);
    S5Encoding {
        solver,
        equations: Vec::new(),
        problem_variables,
        monomials: comparison_gates,
        selector_variables,
        cardinality_auxiliaries: 0,
        domain_encoding: "binary_index_lookup",
        symmetry_breaking,
        pairing,
        algebra_encoding: "implicit_lazy_regular_s3_theory",
        multiplication_encoding: "not_encoded_lazy_theory",
        pair_table_entries: 0,
        pair_selector_variables: 0,
        pair_table_propagation: "not_applicable",
        final_support_clauses: 0,
        final_compatible_selector_pairs: 0,
        final_s3_circuit_installed: false,
        edge_selector_variables: 0,
        target_compatible_pair_edges: 0,
        globally_sorted_compatible_pair_edges: 0,
        edge_link_xor_rows: 0,
        edge_selector_domain_empty: false,
    }
}

fn encode_balanced_s5_frobenius_orbits(
    n: u32,
    target_x: &F2mElement,
    b: &F2mElement,
    structure: &FieldStructure,
    domain: &[u64],
    representative_x_codes: &[u64],
    symmetry_breaking: bool,
    pairing: usize,
    karatsuba: bool,
    representative_encoding: &str,
    rooted: bool,
    lazy_pair_roots: bool,
) -> S5Encoding {
    assert!(matches!(representative_encoding, "one_hot" | "binary"));
    assert!(!(rooted && lazy_pair_roots));
    let width = n as usize;
    let square_code = |code: u64| {
        (0..width).fold(0u64, |value, bit| {
            if (code >> bit) & 1 == 1 {
                value ^ structure.squares[bit]
            } else {
                value
            }
        })
    };
    let mut certified_domain = BTreeSet::new();
    for &representative in representative_x_codes {
        let mut code = representative;
        for _ in 0..width {
            certified_domain.insert(code);
            code = square_code(code);
        }
    }
    assert_eq!(
        certified_domain,
        domain.iter().copied().collect(),
        "representative Frobenius orbits must exactly cover the factor-base x-domain"
    );

    let problem_variables = 6 * width;
    let representatives = representative_x_codes.len();
    let representative_index_width =
        ((usize::BITS - representatives.saturating_sub(1).leading_zeros()) as usize).max(1);
    let frobenius_width =
        ((usize::BITS - width.saturating_sub(1).leading_zeros()) as usize).max(1);
    let binary_representatives = representative_encoding == "binary";
    let representative_variables = if binary_representatives {
        4 * representative_index_width
    } else {
        4 * representatives
    };
    let cardinality_auxiliaries = if binary_representatives {
        0
    } else {
        4 * representatives.saturating_sub(1)
    };
    let frobenius_variables = 4 * frobenius_width;
    let representative_offset = problem_variables;
    let cardinality_offset = representative_offset + representative_variables;
    let frobenius_offset = cardinality_offset + cardinality_auxiliaries;
    let representative_wire_offset = frobenius_offset + frobenius_variables;
    let representative_wire_variables = usize::from(binary_representatives) * 4 * width;
    let root_selector_offset = representative_wire_offset + representative_wire_variables;
    // Lazy pair-roots still need the two static half-trace root selectors; the
    // theory layer only learns compressed support, it does not replace them.
    let root_selector_variables = usize::from(rooted || lazy_pair_roots) * 2;
    let reserved_variables = root_selector_offset + root_selector_variables;
    let summands: [Vec<u32>; 4] = std::array::from_fn(|summand| {
        (0..width)
            .map(|bit| (summand * width + bit + 1) as u32)
            .collect()
    });
    let u: Vec<u32> = (0..width).map(|bit| (4 * width + bit + 1) as u32).collect();
    let v: Vec<u32> = (0..width).map(|bit| (5 * width + bit + 1) as u32).collect();
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };
    let mut builder = CircuitBuilder::new(reserved_variables, karatsuba);
    for summand in 0..4 {
        let mut current: Vec<u32> = if binary_representatives {
            (0..width)
                .map(|bit| (representative_wire_offset + summand * width + bit + 1) as u32)
                .collect()
        } else {
            let selectors: Vec<u32> = (0..representatives)
                .map(|index| {
                    (representative_offset + summand * representatives + index + 1) as u32
                })
                .collect();
            (0..width)
                .map(|bit| {
                    let inputs: Vec<u32> = representative_x_codes
                        .iter()
                        .zip(&selectors)
                        .filter_map(|(&code, &selector)| {
                            (((code >> bit) & 1) == 1).then_some(selector)
                        })
                        .collect();
                    builder.xor_wire(&inputs, false)
                })
                .collect()
        };
        for exponent_bit in 0..frobenius_width {
            let transformed = builder.frobenius_wire(
                &current,
                1usize << exponent_bit,
                structure,
            );
            let select =
                (frobenius_offset + summand * frobenius_width + exponent_bit + 1) as u32;
            current = current
                .iter()
                .zip(&transformed)
                .map(|(&when_false, &when_true)| {
                    builder.mux_wire(select, when_false, when_true)
                })
                .collect();
        }
        for (&coordinate, &derived) in summands[summand].iter().zip(&current) {
            builder.xors.push((vec![coordinate, derived], false));
        }
    }
    if rooted || lazy_pair_roots {
        // Selector-native half-trace roots for each paired side. Exceptional
        // relative-Frobenius support is handled separately by compressed
        // nogoods / theory; this static circuit must still pin u,v to a root.
        builder.constrain_s3_root(
            &summands[pairing_indices[0]],
            &summands[pairing_indices[1]],
            &u,
            (root_selector_offset + 1) as u32,
            b,
            structure,
        );
        builder.constrain_s3_root(
            &summands[pairing_indices[2]],
            &summands[pairing_indices[3]],
            &v,
            (root_selector_offset + 2) as u32,
            b,
            structure,
        );
    } else {
        builder.constrain_s3(
            &summands[pairing_indices[0]],
            &summands[pairing_indices[1]],
            &u,
            b,
            structure,
        );
        builder.constrain_s3(
            &summands[pairing_indices[2]],
            &summands[pairing_indices[3]],
            &v,
            b,
            structure,
        );
    }
    builder.constrain_s3_constant_third(&u, &v, target_x, b, structure);
    if symmetry_breaking {
        for summand in 0..3 {
            builder.constrain_unsigned_less_equal(&summands[summand], &summands[summand + 1]);
        }
    }
    let nonlinear_auxiliaries = builder.and_gates;
    let mut solver = builder.finish();
    if binary_representatives {
        install_binary_index_range(
            &mut solver,
            representatives,
            representative_offset,
            representative_index_width,
        );
        for summand in 0..4 {
            let index_offset = representative_offset + summand * representative_index_width;
            for (index, &code) in representative_x_codes.iter().enumerate() {
                let mut guard = Vec::with_capacity(representative_index_width);
                for bit in 0..representative_index_width {
                    let variable = (index_offset + bit + 1) as Lit;
                    guard.push(if (index >> bit) & 1 == 1 {
                        -variable
                    } else {
                        variable
                    });
                }
                for bit in 0..width {
                    let mut clause = guard.clone();
                    let wire = (representative_wire_offset + summand * width + bit + 1) as Lit;
                    clause.push(if (code >> bit) & 1 == 1 { wire } else { -wire });
                    assert!(solver.add_clause(clause));
                }
            }
        }
    } else {
        for summand in 0..4 {
            install_sequential_exactly_one(
                &mut solver,
                representative_offset + summand * representatives,
                cardinality_offset + summand * representatives.saturating_sub(1),
                representatives,
            );
        }
    }
    for summand in 0..4 {
        add_coordinate_domain(
            &mut solver,
            frobenius_offset + summand * frobenius_width,
            frobenius_width,
            &(0..width as u64).collect::<Vec<_>>(),
        );
    }
    // Default: all orbit representatives, then all Frobenius shifts, then optional
    // root selectors. `KIC_ORBIT_BRANCH_ORDER=pair_then_pair` decides the first
    // Semaev pair (pairing indices 0/1) before the second pair (2/3).
    // `pair_then_pair_reversed` flips that order. Both keep pair_table_entries=0.
    // `field_bits_then_pair_then_pair` decides the 6·n Semaev field bits first,
    // then the same pair-then-pair orbit schedule (still pair_table_entries=0).
    // `intermediates_then_pair_then_pair` decides only the Semaev intermediate
    // wires u/v (offsets 4n/5n — the pair_sum_trie domain) before the pair schedule.
    let branch_order = std::env::var("KIC_ORBIT_BRANCH_ORDER").unwrap_or_else(|_| "reps_then_shift".to_owned());
    let mut priorities: Vec<u32> = Vec::new();
    let pair_then_pair_family = matches!(
        branch_order.as_str(),
        "pair_then_pair"
            | "pair_then_pair_reversed"
            | "field_bits_then_pair_then_pair"
            | "intermediates_then_pair_then_pair"
    );
    if branch_order == "field_bits_then_pair_then_pair" {
        priorities.extend(1..=problem_variables as u32);
    } else if branch_order == "intermediates_then_pair_then_pair" {
        // u = vars [4n+1 .. 5n], v = vars [5n+1 .. 6n]
        priorities.extend(u.iter().copied());
        priorities.extend(v.iter().copied());
    }
    if pair_then_pair_family {
        let rep_stride = if binary_representatives {
            representative_index_width
        } else {
            representatives
        };
        let reversed = branch_order == "pair_then_pair_reversed";
        let first = if reversed {
            &pairing_indices[2..]
        } else {
            &pairing_indices[..2]
        };
        let second = if reversed {
            &pairing_indices[..2]
        } else {
            &pairing_indices[2..]
        };
        for &summand in first {
            priorities.extend((0..rep_stride).map(|index| {
                (representative_offset + summand * rep_stride + index + 1) as u32
            }));
        }
        for &summand in first {
            priorities.extend((0..frobenius_width).map(|index| {
                (frobenius_offset + summand * frobenius_width + index + 1) as u32
            }));
        }
        for &summand in second {
            priorities.extend((0..rep_stride).map(|index| {
                (representative_offset + summand * rep_stride + index + 1) as u32
            }));
        }
        for &summand in second {
            priorities.extend((0..frobenius_width).map(|index| {
                (frobenius_offset + summand * frobenius_width + index + 1) as u32
            }));
        }
    } else if branch_order == "shift_then_reps" {
        // Decide Frobenius shifts before orbit representatives.
        priorities.extend(
            (0..frobenius_variables).map(|index| (frobenius_offset + index + 1) as u32),
        );
        priorities.extend((0..representative_variables).map(|index| {
            (representative_offset + index + 1) as u32
        }));
    } else {
        priorities.extend((0..representative_variables).map(|index| {
            (representative_offset + index + 1) as u32
        }));
        priorities.extend(
            (0..frobenius_variables).map(|index| (frobenius_offset + index + 1) as u32),
        );
    }
    priorities.extend((0..root_selector_variables).map(|index| {
        (root_selector_offset + index + 1) as u32
    }));
    solver.set_branch_priority(&priorities);
    S5Encoding {
        solver,
        equations: Vec::new(),
        problem_variables,
        monomials: nonlinear_auxiliaries,
        selector_variables: representative_variables + frobenius_variables + root_selector_variables,
        cardinality_auxiliaries,
        domain_encoding: if binary_representatives {
            "binary_representative_plus_binary_frobenius_shift"
        } else {
            "one_hot_representative_plus_binary_frobenius_shift"
        },
        symmetry_breaking,
        pairing,
        algebra_encoding: if lazy_pair_roots {
            "lazy_pair_roots_plus_factorized_final_s3_over_frobenius_orbits"
        } else if rooted {
            "half_trace_rooted_s5_over_frobenius_orbit_factor_base"
        } else {
            "factorized_s5_over_frobenius_orbit_factor_base"
        },
        multiplication_encoding: if karatsuba {
            "carryless_karatsuba"
        } else {
            "schoolbook"
        },
        pair_table_entries: 0,
        pair_selector_variables: 0,
        pair_table_propagation: "not_applicable",
        final_support_clauses: 0,
        final_compatible_selector_pairs: 0,
        final_s3_circuit_installed: true,
        edge_selector_variables: 0,
        target_compatible_pair_edges: 0,
        globally_sorted_compatible_pair_edges: 0,
        edge_link_xor_rows: 0,
        edge_selector_domain_empty: false,
    }
}

fn encode_balanced_s5_pair_table(
    curve: &KoblitzCurve,
    n: u32,
    target_x: &F2mElement,
    b: &F2mElement,
    structure: &FieldStructure,
    domain: &[u64],
    entries: &[PairXEntry],
    symmetry_breaking: bool,
    pairing: usize,
    karatsuba: bool,
    direct_implications: bool,
    reverse_support: bool,
    final_support: bool,
    drop_final_s3: bool,
) -> S5Encoding {
    assert!(!drop_final_s3 || final_support);
    assert!(
        symmetry_breaking,
        "unordered pair tables require sorted factor indices"
    );
    let width = n as usize;
    let problem_variables = 6 * width;
    let index_width =
        ((usize::BITS - domain.len().saturating_sub(1).leading_zeros()) as usize).max(1);
    let factor_index_variables = 4 * index_width;
    let pair_selector_variables = 2 * entries.len();
    let cardinality_auxiliaries = 2 * entries.len().saturating_sub(1);
    let factor_index_offset = problem_variables;
    let pair_selector_offset = factor_index_offset + factor_index_variables;
    let cardinality_offset = pair_selector_offset + pair_selector_variables;
    let reserved_variables = problem_variables
        + factor_index_variables
        + pair_selector_variables
        + cardinality_auxiliaries;

    let u: Vec<u32> = (0..width).map(|bit| (4 * width + bit + 1) as u32).collect();
    let v: Vec<u32> = (0..width).map(|bit| (5 * width + bit + 1) as u32).collect();
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };

    let mut builder = CircuitBuilder::new(reserved_variables, karatsuba);
    if !drop_final_s3 {
        builder.constrain_s3_constant_third(&u, &v, target_x, b, structure);
    }
    if symmetry_breaking {
        for summand in 0..3 {
            let left: Vec<u32> = (0..index_width)
                .map(|bit| (factor_index_offset + summand * index_width + bit + 1) as u32)
                .collect();
            let right: Vec<u32> = (0..index_width)
                .map(|bit| (factor_index_offset + (summand + 1) * index_width + bit + 1) as u32)
                .collect();
            builder.constrain_unsigned_less_equal(&left, &right);
        }
    }
    let and_gates = builder.and_gates;
    let mut solver = builder.finish();
    install_binary_index_domain(&mut solver, width, domain, factor_index_offset, index_width);
    install_pair_table_link(
        &mut solver,
        entries,
        pair_selector_offset,
        cardinality_offset,
        factor_index_offset,
        index_width,
        pairing_indices[0],
        pairing_indices[1],
        4 * width,
        width,
        direct_implications,
        reverse_support,
    );
    install_pair_table_link(
        &mut solver,
        entries,
        pair_selector_offset + entries.len(),
        cardinality_offset + entries.len().saturating_sub(1),
        factor_index_offset,
        index_width,
        pairing_indices[2],
        pairing_indices[3],
        5 * width,
        width,
        direct_implications,
        reverse_support,
    );
    let (final_support_clauses, final_compatible_selector_pairs) = if final_support {
        install_final_pair_compatibility(
            &mut solver,
            curve,
            target_x,
            entries,
            pair_selector_offset,
            pair_selector_offset + entries.len(),
        )
    } else {
        (0, 0)
    };

    S5Encoding {
        solver,
        equations: Vec::new(),
        problem_variables,
        monomials: and_gates,
        selector_variables: factor_index_variables + pair_selector_variables,
        cardinality_auxiliaries,
        domain_encoding: "binary_index_plus_exact_pair_table",
        symmetry_breaking,
        pairing,
        algebra_encoding: if drop_final_s3 {
            "exact_pair_tables_plus_target_compatibility_join"
        } else {
            "exact_pair_tables_plus_factorized_final_s3"
        },
        multiplication_encoding: if drop_final_s3 {
            "not_used_for_final_s3"
        } else if karatsuba {
            "carryless_karatsuba"
        } else {
            "schoolbook"
        },
        pair_table_entries: entries.len(),
        pair_selector_variables,
        pair_table_propagation: if final_support {
            "xor_plus_binary_and_final_compatibility_support"
        } else if reverse_support {
            "xor_plus_binary_and_reverse_support_implications"
        } else if direct_implications {
            "xor_plus_binary_implications"
        } else {
            "xor_only"
        },
        final_support_clauses,
        final_compatible_selector_pairs,
        final_s3_circuit_installed: !drop_final_s3,
        edge_selector_variables: 0,
        target_compatible_pair_edges: 0,
        globally_sorted_compatible_pair_edges: 0,
        edge_link_xor_rows: 0,
        edge_selector_domain_empty: false,
    }
}

fn encode_balanced_s5_target_edge_selectors(
    curve: &KoblitzCurve,
    n: u32,
    target_x: &F2mElement,
    domain: &[u64],
    entries: &[PairXEntry],
    symmetry_breaking: bool,
    pairing: usize,
) -> S5Encoding {
    assert!(
        symmetry_breaking,
        "target-compatible edges require globally sorted factor indices"
    );
    let width = n as usize;
    let problem_variables = 6 * width;
    let index_width =
        ((usize::BITS - domain.len().saturating_sub(1).leading_zeros()) as usize).max(1);
    let factor_index_variables = 4 * index_width;
    let (target_compatible_pair_edges, edges) =
        target_compatible_pair_edges(curve, target_x, entries, pairing);
    let edge_selector_variables = edges.len();
    let cardinality_auxiliaries = edge_selector_variables.saturating_sub(1);
    let factor_index_offset = problem_variables;
    let edge_selector_offset = factor_index_offset + factor_index_variables;
    let cardinality_offset = edge_selector_offset + edge_selector_variables;
    let reserved_variables = problem_variables
        + factor_index_variables
        + edge_selector_variables
        + cardinality_auxiliaries;

    let mut builder = CircuitBuilder::new(reserved_variables, false);
    for summand in 0..3 {
        let left: Vec<u32> = (0..index_width)
            .map(|bit| (factor_index_offset + summand * index_width + bit + 1) as u32)
            .collect();
        let right: Vec<u32> = (0..index_width)
            .map(|bit| (factor_index_offset + (summand + 1) * index_width + bit + 1) as u32)
            .collect();
        builder.constrain_unsigned_less_equal(&left, &right);
    }
    let mut solver = builder.finish();
    install_binary_index_domain(&mut solver, width, domain, factor_index_offset, index_width);
    let edge_link_xor_rows = install_target_compatible_edge_link(
        &mut solver,
        domain,
        entries,
        &edges,
        pairing,
        width,
        factor_index_offset,
        index_width,
        edge_selector_offset,
        cardinality_offset,
    );

    S5Encoding {
        solver,
        equations: Vec::new(),
        problem_variables,
        monomials: 0,
        selector_variables: factor_index_variables + edge_selector_variables,
        cardinality_auxiliaries,
        domain_encoding: "binary_index_plus_target_compatible_edge_selector",
        symmetry_breaking,
        pairing,
        algebra_encoding: "exact_target_specific_pair_pair_join_then_sat_selection",
        multiplication_encoding: "not_used",
        pair_table_entries: entries.len(),
        pair_selector_variables: 0,
        pair_table_propagation: "single_exactly_one_compatible_edge_xor_link",
        final_support_clauses: 0,
        final_compatible_selector_pairs: target_compatible_pair_edges,
        final_s3_circuit_installed: false,
        edge_selector_variables,
        target_compatible_pair_edges,
        globally_sorted_compatible_pair_edges: edges.len(),
        edge_link_xor_rows,
        edge_selector_domain_empty: edges.is_empty(),
    }
}

fn decode_code(model: &[bool], offset: usize, width: usize) -> u64 {
    (0..width).fold(0u64, |value, bit| {
        value | (u64::from(model[offset + bit]) << bit)
    })
}

fn decode_partial_code(assignment: &[Option<bool>], offset: usize, width: usize) -> u64 {
    (0..width).fold(0u64, |value, bit| {
        value | (u64::from(assignment[offset + bit].unwrap()) << bit)
    })
}

fn push_forbidden_binary_assignment(clause: &mut Vec<Lit>, offset: usize, width: usize, value: usize) {
    for bit in 0..width {
        let variable = (offset + bit + 1) as Lit;
        if ((value >> bit) & 1) == 1 {
            clause.push(-variable);
        } else {
            clause.push(variable);
        }
    }
}

#[derive(Clone, Debug)]
#[allow(dead_code)]
struct RelativePairSupportCertificate {
    n: u32,
    representative_x_codes: Vec<u64>,
    exceptional_relative_states: Vec<(usize, usize, usize)>,
    support_digest_blake3: String,
}

fn digest_relative_pair_support(
    representative_x_codes: &[u64],
    exceptional_relative_states: &[(usize, usize, usize)],
) -> String {
    let mut hasher = blake3::Hasher::new();
    hasher.update(b"relative-frobenius-pair-support-cert-v1");
    hasher.update(&(representative_x_codes.len() as u32).to_le_bytes());
    for &code in representative_x_codes {
        hasher.update(&code.to_le_bytes());
    }
    hasher.update(&(exceptional_relative_states.len() as u32).to_le_bytes());
    for &(left, right, shift) in exceptional_relative_states {
        hasher.update(&(left as u32).to_le_bytes());
        hasher.update(&(right as u32).to_le_bytes());
        hasher.update(&(shift as u32).to_le_bytes());
    }
    hasher.finalize().to_hex().to_string()
}

fn scan_exceptional_relative_states(
    curve: &KoblitzCurve,
    representative_x_codes: &[u64],
) -> (Vec<(usize, usize, usize)>, f64) {
    let started = Instant::now();
    let width = curve.n as usize;
    let representatives = representative_x_codes.len();
    let mut shifted = vec![vec![0u64; width]; representatives];
    for (index, &code) in representative_x_codes.iter().enumerate() {
        shifted[index][0] = code;
        for exponent in 1..width {
            shifted[index][exponent] = frobenius_code(curve, shifted[index][exponent - 1], 1);
        }
    }
    let exceptional_states: Vec<(usize, usize, usize)> = (0..representatives)
        .into_par_iter()
        .flat_map_iter(|left_rep| {
            let left = representative_x_codes[left_rep];
            let mut local = Vec::new();
            for right_rep in 0..representatives {
                for relative_shift in 0..width {
                    let right = shifted[right_rep][relative_shift];
                    if regular_s3_x_roots(curve, left, right).is_none() {
                        local.push((left_rep, right_rep, relative_shift));
                    }
                }
            }
            local
        })
        .collect();
    (exceptional_states, started.elapsed().as_secs_f64() * 1000.0)
}

fn load_relative_pair_support_certificate(
    path: &str,
    representative_x_codes: &[u64],
    n: u32,
) -> RelativePairSupportCertificate {
    let value: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(path).expect("read pair-support certificate"))
            .expect("parse pair-support certificate");
    assert_eq!(value["kind"], "relative_frobenius_pair_support_certificate");
    assert_eq!(value["schema_version"], "1.0");
    assert_eq!(value["n"].as_u64().unwrap() as u32, n);
    assert_eq!(value["pair_table_entries"].as_u64().unwrap_or(0), 0);
    assert_eq!(value["edge_selectors"].as_u64().unwrap_or(0), 0);
    let cert_reps: Vec<u64> = value["representative_x_codes"]
        .as_array()
        .expect("representative_x_codes")
        .iter()
        .map(|v| v.as_u64().expect("rep code"))
        .collect();
    assert_eq!(
        cert_reps, representative_x_codes,
        "pair-support certificate representatives must match the live orbit factor base"
    );
    let exceptional_relative_states: Vec<(usize, usize, usize)> = value["exceptional_relative_states"]
        .as_array()
        .expect("exceptional_relative_states")
        .iter()
        .map(|row| {
            let arr = row.as_array().expect("exceptional triple");
            (
                arr[0].as_u64().unwrap() as usize,
                arr[1].as_u64().unwrap() as usize,
                arr[2].as_u64().unwrap() as usize,
            )
        })
        .collect();
    let support_digest_blake3 = value["support_digest_blake3"]
        .as_str()
        .expect("support_digest_blake3")
        .to_owned();
    let recomputed = digest_relative_pair_support(representative_x_codes, &exceptional_relative_states);
    assert_eq!(
        support_digest_blake3, recomputed,
        "pair-support certificate digest mismatch"
    );
    RelativePairSupportCertificate {
        n,
        representative_x_codes: cert_reps,
        exceptional_relative_states,
        support_digest_blake3,
    }
}

fn write_relative_pair_support_certificate(
    path: &str,
    n: u32,
    representative_x_codes: &[u64],
    exceptional_relative_states: &[(usize, usize, usize)],
    support_digest_blake3: &str,
) {
    let payload = json!({
        "schema_version": "1.0",
        "kind": "relative_frobenius_pair_support_certificate",
        "n": n,
        "orbit_representatives": representative_x_codes.len(),
        "representative_x_codes": representative_x_codes,
        "exceptional_relative_states": exceptional_relative_states
            .iter()
            .map(|(a,b,c)| json!([a,b,c]))
            .collect::<Vec<_>>(),
        "exceptional_relative_state_count": exceptional_relative_states.len(),
        "support_digest_blake3": support_digest_blake3,
        "pair_table_entries": 0,
        "edge_selectors": 0,
        "claim_boundary": "Reusable compressed exceptional relative-Frobenius pair-support certificate only. Not an edge/pair table, not unrestricted extraction, not vs_rho, not ledger promotion."
    });
    std::fs::write(path, serde_json::to_vec_pretty(&payload).unwrap()).expect("write pair-support certificate");
}

fn scan_regular_relative_states(
    curve: &KoblitzCurve,
    representative_x_codes: &[u64],
) -> (Vec<(usize, usize, usize, [u64; 2])>, f64) {
    let started = Instant::now();
    let width = curve.n as usize;
    let representatives = representative_x_codes.len();
    let mut shifted = vec![vec![0u64; width]; representatives];
    for (index, &code) in representative_x_codes.iter().enumerate() {
        shifted[index][0] = code;
        for exponent in 1..width {
            shifted[index][exponent] = frobenius_code(curve, shifted[index][exponent - 1], 1);
        }
    }
    let regular_states: Vec<(usize, usize, usize, [u64; 2])> = (0..representatives)
        .into_par_iter()
        .flat_map_iter(|left_rep| {
            let left = representative_x_codes[left_rep];
            let mut local = Vec::new();
            for right_rep in 0..representatives {
                for relative_shift in 0..width {
                    let right = shifted[right_rep][relative_shift];
                    if let Some(roots) = regular_s3_x_roots(curve, left, right) {
                        local.push((left_rep, right_rep, relative_shift, roots));
                    }
                }
            }
            local
        })
        .collect();
    (regular_states, started.elapsed().as_secs_f64() * 1000.0)
}

fn frobenius_basis_images(curve: &KoblitzCurve, power: usize) -> Vec<u64> {
    (0..curve.n as usize)
        .map(|bit| frobenius_code(curve, 1u64 << bit, power))
        .collect()
}

fn solver_new_var(solver: &mut Solver) -> u32 {
    *solver.add_vars(1).start()
}

fn solver_xor_wire(solver: &mut Solver, inputs: &[u32]) -> u32 {
    let out = solver_new_var(solver);
    if inputs.is_empty() {
        assert!(solver.add_clause(vec![-(out as Lit)]));
        return out;
    }
    let mut vars = Vec::with_capacity(inputs.len() + 1);
    vars.push(out);
    vars.extend(inputs.iter().copied());
    assert!(solver.add_xor(&vars, false));
    out
}

fn solver_mux_bit(solver: &mut Solver, select: u32, when_false: u32, when_true: u32) -> u32 {
    let out = solver_new_var(solver);
    let s = select as Lit;
    let c = when_false as Lit;
    let t = when_true as Lit;
    let o = out as Lit;
    assert!(solver.add_clause(vec![-s, -t, o]));
    assert!(solver.add_clause(vec![-s, t, -o]));
    assert!(solver.add_clause(vec![s, -c, o]));
    assert!(solver.add_clause(vec![s, c, -o]));
    out
}

fn link_absolute_to_canonical_via_frobenius_mux(
    solver: &mut Solver,
    curve: &KoblitzCurve,
    canonical: &[u32],
    absolute_offset: usize,
    frobenius_offset: usize,
    frobenius_width: usize,
) -> usize {
    let width = canonical.len();
    let mut current = canonical.to_vec();
    let mut xor_rows = 0usize;
    for bit in 0..frobenius_width {
        let images = frobenius_basis_images(curve, 1usize << bit);
        let twisted: Vec<u32> = (0..width)
            .map(|output| {
                let inputs: Vec<u32> = (0..width)
                    .filter(|&input| ((images[input] >> output) & 1) == 1)
                    .map(|input| current[input])
                    .collect();
                xor_rows += 1;
                solver_xor_wire(solver, &inputs)
            })
            .collect();
        let select = (frobenius_offset + bit + 1) as u32;
        current = current
            .iter()
            .zip(&twisted)
            .map(|(&when_false, &when_true)| solver_mux_bit(solver, select, when_false, when_true))
            .collect();
    }
    for (bit, &wired) in current.iter().enumerate() {
        let absolute = (absolute_offset + bit + 1) as Lit;
        let w = wired as Lit;
        assert!(solver.add_clause(vec![-w, absolute]));
        assert!(solver.add_clause(vec![w, -absolute]));
    }
    xor_rows
}

/// Relative-frame positive support: one Frobenius mux per Semaev side plus
/// per-state forcing of the canonical intermediate (no ×n absolute root expand).
fn install_relative_orbit_pair_support_positive_relative_frame(
    solver: &mut Solver,
    curve: &KoblitzCurve,
    representative_x_codes: &[u64],
    pairing: usize,
    representative_encoding: &str,
) -> serde_json::Value {
    let started = Instant::now();
    let width = curve.n as usize;
    assert!(
        width <= 53,
        "KIC_ORBIT_PAIR_SUPPORT_POSITIVE relative mode is bounded to n <= 53"
    );
    let representatives = representative_x_codes.len();
    let binary_representatives = representative_encoding == "binary";
    let representative_index_width =
        ((usize::BITS - representatives.saturating_sub(1).leading_zeros()) as usize).max(1);
    let representative_variables = if binary_representatives {
        4 * representative_index_width
    } else {
        4 * representatives
    };
    let cardinality_auxiliaries = if binary_representatives {
        0
    } else {
        4 * representatives.saturating_sub(1)
    };
    let frobenius_width =
        ((usize::BITS - width.saturating_sub(1).leading_zeros()) as usize).max(1);
    let problem_variables = 6 * width;
    let representative_offset = problem_variables;
    let frobenius_offset = representative_offset + representative_variables + cardinality_auxiliaries;
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };
    let sides = [
        ([pairing_indices[0], pairing_indices[1]], 4 * width),
        ([pairing_indices[2], pairing_indices[3]], 5 * width),
    ];
    let (regular_states, scan_ms) = scan_regular_relative_states(curve, representative_x_codes);
    let expand_started = Instant::now();
    let mut positive_clauses = 0usize;
    let mut root_selectors = 0usize;
    let mut relative_matches = 0usize;
    let mut mux_xor_rows = 0usize;
    for &([left_summand, right_summand], third_offset) in &sides {
        let canonical: Vec<u32> = (0..width).map(|_| solver_new_var(solver)).collect();
        mux_xor_rows += link_absolute_to_canonical_via_frobenius_mux(
            solver,
            curve,
            &canonical,
            third_offset,
            frobenius_offset + left_summand * frobenius_width,
            frobenius_width,
        );
        for &(left_rep, right_rep, relative_shift, roots_at_left0) in &regular_states {
            let match_var = solver_new_var(solver);
            relative_matches += 1;
            let mut disjunct = vec![-(match_var as Lit)];
            for left_shift in 0..width {
                let right_shift = (left_shift + relative_shift) % width;
                let witness = solver_new_var(solver);
                let mut witness_guard = Vec::new();
                if binary_representatives {
                    push_forbidden_binary_assignment(
                        &mut witness_guard,
                        representative_offset + left_summand * representative_index_width,
                        representative_index_width,
                        left_rep,
                    );
                    push_forbidden_binary_assignment(
                        &mut witness_guard,
                        representative_offset + right_summand * representative_index_width,
                        representative_index_width,
                        right_rep,
                    );
                } else {
                    witness_guard.push(
                        -((representative_offset
                            + left_summand * representatives
                            + left_rep
                            + 1) as Lit),
                    );
                    witness_guard.push(
                        -((representative_offset
                            + right_summand * representatives
                            + right_rep
                            + 1) as Lit),
                    );
                }
                push_forbidden_binary_assignment(
                    &mut witness_guard,
                    frobenius_offset + left_summand * frobenius_width,
                    frobenius_width,
                    left_shift,
                );
                push_forbidden_binary_assignment(
                    &mut witness_guard,
                    frobenius_offset + right_summand * frobenius_width,
                    frobenius_width,
                    right_shift,
                );
                // alignment => witness
                let mut imply = witness_guard.clone();
                imply.push(witness as Lit);
                assert!(solver.add_clause(imply));
                positive_clauses += 1;
                // witness => alignment (negate each forbidden guard lit)
                for &literal in &witness_guard {
                    assert!(solver.add_clause(vec![-(witness as Lit), -literal]));
                    positive_clauses += 1;
                }
                // witness => match
                assert!(solver.add_clause(vec![-(witness as Lit), match_var as Lit]));
                positive_clauses += 1;
                disjunct.push(witness as Lit);
            }
            assert!(solver.add_clause(disjunct));
            positive_clauses += 1;
            let selector = solver_new_var(solver);
            root_selectors += 1;
            let guard = vec![-(match_var as Lit)];
            for bit in 0..width {
                let output = canonical[bit] as Lit;
                let first = ((roots_at_left0[0] >> bit) & 1) == 1;
                let second = ((roots_at_left0[1] >> bit) & 1) == 1;
                if first == second {
                    let mut clause = guard.clone();
                    clause.push(if first { output } else { -output });
                    assert!(solver.add_clause(clause));
                    positive_clauses += 1;
                } else if !first && second {
                    assert!(solver.add_clause({
                        let mut c = guard.clone();
                        c.extend([-output, selector as Lit]);
                        c
                    }));
                    assert!(solver.add_clause({
                        let mut c = guard.clone();
                        c.extend([output, -(selector as Lit)]);
                        c
                    }));
                    positive_clauses += 2;
                } else {
                    assert!(solver.add_clause({
                        let mut c = guard.clone();
                        c.extend([output, selector as Lit]);
                        c
                    }));
                    assert!(solver.add_clause({
                        let mut c = guard.clone();
                        c.extend([-output, -(selector as Lit)]);
                        c
                    }));
                    positive_clauses += 2;
                }
            }
        }
    }
    let expand_ms = expand_started.elapsed().as_secs_f64() * 1000.0;
    json!({
        "enabled": true,
        "mode": "relative_frame",
        "pair_table_entries": 0,
        "edge_selectors": 0,
        "regular_relative_states": regular_states.len(),
        "relative_matches": relative_matches,
        "root_selectors": root_selectors,
        "positive_clauses": positive_clauses,
        "mux_xor_rows": mux_xor_rows,
        "scan_ms": scan_ms,
        "expand_ms": expand_ms,
        "install_ms": started.elapsed().as_secs_f64() * 1000.0,
        "n_bound": 53,
        "claim_boundary": "Relative-frame positive regular pair-support (canonical intermediate + Frobenius mux); no edge/pair table; not unrestricted extraction; not vs_rho; not ledger promotion"
    })
}

/// Install positive regular relative-Frobenius pair-support constraints.
///
/// Default mode expands absolute Frobenius alignments (O(regular_states · n)).
/// `KIC_ORBIT_PAIR_SUPPORT_POSITIVE_MODE=relative` uses a canonical intermediate
/// plus a Frobenius mux so root forcing is O(regular_states) rather than
/// O(regular_states · n). Still `pair_table_entries = 0` / no edge selectors.
fn install_relative_orbit_pair_support_positive(
    solver: &mut Solver,
    curve: &KoblitzCurve,
    representative_x_codes: &[u64],
    pairing: usize,
    representative_encoding: &str,
) -> serde_json::Value {
    if std::env::var("KIC_ORBIT_PAIR_SUPPORT_POSITIVE_MODE").as_deref() == Ok("relative") {
        return install_relative_orbit_pair_support_positive_relative_frame(
            solver,
            curve,
            representative_x_codes,
            pairing,
            representative_encoding,
        );
    }
    let started = Instant::now();
    let width = curve.n as usize;
    assert!(
        width <= 23,
        "KIC_ORBIT_PAIR_SUPPORT_POSITIVE is bounded to n <= 23 (absolute expansion)"
    );
    let representatives = representative_x_codes.len();
    let binary_representatives = representative_encoding == "binary";
    let representative_index_width =
        ((usize::BITS - representatives.saturating_sub(1).leading_zeros()) as usize).max(1);
    let representative_variables = if binary_representatives {
        4 * representative_index_width
    } else {
        4 * representatives
    };
    let cardinality_auxiliaries = if binary_representatives {
        0
    } else {
        4 * representatives.saturating_sub(1)
    };
    let frobenius_width =
        ((usize::BITS - width.saturating_sub(1).leading_zeros()) as usize).max(1);
    let problem_variables = 6 * width;
    let representative_offset = problem_variables;
    let frobenius_offset = representative_offset + representative_variables + cardinality_auxiliaries;
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };
    let sides = [
        ([pairing_indices[0], pairing_indices[1]], 4 * width),
        ([pairing_indices[2], pairing_indices[3]], 5 * width),
    ];

    let (regular_states, scan_ms) =
        scan_regular_relative_states(curve, representative_x_codes);
    let expand_started = Instant::now();
    let mut positive_clauses = 0usize;
    let mut root_selectors = 0usize;
    let mut absolute_alignments = 0usize;
    for &( [left_summand, right_summand], third_offset) in &sides {
        for &(left_rep, right_rep, relative_shift, roots_at_left0) in &regular_states {
            for left_shift in 0..width {
                absolute_alignments += 1;
                let right_shift = (left_shift + relative_shift) % width;
                let twisted = [
                    frobenius_code(curve, roots_at_left0[0], left_shift),
                    frobenius_code(curve, roots_at_left0[1], left_shift),
                ];
                let selector = solver.add_vars(1).next().unwrap();
                root_selectors += 1;
                let mut guard = Vec::with_capacity(
                    2 + 2 * frobenius_width
                        + if binary_representatives {
                            2 * representative_index_width
                        } else {
                            2
                        },
                );
                if binary_representatives {
                    push_forbidden_binary_assignment(
                        &mut guard,
                        representative_offset + left_summand * representative_index_width,
                        representative_index_width,
                        left_rep,
                    );
                    push_forbidden_binary_assignment(
                        &mut guard,
                        representative_offset + right_summand * representative_index_width,
                        representative_index_width,
                        right_rep,
                    );
                } else {
                    guard.push(
                        -((representative_offset
                            + left_summand * representatives
                            + left_rep
                            + 1) as Lit),
                    );
                    guard.push(
                        -((representative_offset
                            + right_summand * representatives
                            + right_rep
                            + 1) as Lit),
                    );
                }
                push_forbidden_binary_assignment(
                    &mut guard,
                    frobenius_offset + left_summand * frobenius_width,
                    frobenius_width,
                    left_shift,
                );
                push_forbidden_binary_assignment(
                    &mut guard,
                    frobenius_offset + right_summand * frobenius_width,
                    frobenius_width,
                    right_shift,
                );
                for clause in guarded_s3_root_clauses(
                    &guard,
                    third_offset,
                    selector,
                    twisted,
                    width,
                ) {
                    assert!(solver.add_clause(clause));
                    positive_clauses += 1;
                }
            }
        }
    }
    let expand_ms = expand_started.elapsed().as_secs_f64() * 1000.0;
    json!({
        "enabled": true,
        "pair_table_entries": 0,
        "edge_selectors": 0,
        "regular_relative_states": regular_states.len(),
        "absolute_alignments": absolute_alignments,
        "root_selectors": root_selectors,
        "positive_clauses": positive_clauses,
        "scan_ms": scan_ms,
        "expand_ms": expand_ms,
        "install_ms": started.elapsed().as_secs_f64() * 1000.0,
        "n_bound": 23,
        "claim_boundary": "Static positive regular relative-Frobenius pair-support only; no edge/pair table; not unrestricted extraction claim by itself; not vs_rho; not ledger promotion"
    })
}

/// Install compressed relative-Frobenius pair-support nogoods on orbit selectors.
///
/// For each paired summand side and each exceptional relative state
/// `(left_rep, right_rep, relative_shift)`, forbid every absolute Frobenius
/// alignment realizing that relative shift. Uses the representative-orbit
/// compression measured by `relative_pair_stats` — never materializes an
/// endpoint pair/edge table.
fn install_relative_orbit_pair_support_nogoods(
    solver: &mut Solver,
    curve: &KoblitzCurve,
    representative_x_codes: &[u64],
    pairing: usize,
    representative_encoding: &str,
) -> serde_json::Value {
    let started = Instant::now();
    let width = curve.n as usize;
    let representatives = representative_x_codes.len();
    let binary_representatives = representative_encoding == "binary";
    let representative_index_width =
        ((usize::BITS - representatives.saturating_sub(1).leading_zeros()) as usize).max(1);
    let representative_variables = if binary_representatives {
        4 * representative_index_width
    } else {
        4 * representatives
    };
    let cardinality_auxiliaries = if binary_representatives {
        0
    } else {
        4 * representatives.saturating_sub(1)
    };
    let frobenius_width =
        ((usize::BITS - width.saturating_sub(1).leading_zeros()) as usize).max(1);
    let problem_variables = 6 * width;
    let representative_offset = problem_variables;
    let frobenius_offset = representative_offset + representative_variables + cardinality_auxiliaries;
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => panic!("pairing must be 0, 1, or 2"),
    };
    let sides = [
        [pairing_indices[0], pairing_indices[1]],
        [pairing_indices[2], pairing_indices[3]],
    ];

    // Reusable certificate path: load exceptional relative states without
    // rescanning, or scan once and optionally persist. Never materializes an
    // endpoint pair/edge table either way.
    let cert_in = std::env::var("KIC_ORBIT_PAIR_SUPPORT_CERT").ok();
    let cert_out = std::env::var("KIC_ORBIT_PAIR_SUPPORT_CERT_OUT").ok();
    let (exceptional_states, scan_ms, loaded_from_certificate) = if let Some(path) = &cert_in {
        let loaded = load_relative_pair_support_certificate(path, representative_x_codes, curve.n);
        (loaded.exceptional_relative_states, 0.0, true)
    } else {
        let (states, ms) = scan_exceptional_relative_states(curve, representative_x_codes);
        (states, ms, false)
    };
    let support_digest_blake3 =
        digest_relative_pair_support(representative_x_codes, &exceptional_states);
    if let Some(path) = &cert_out {
        write_relative_pair_support_certificate(
            path,
            curve.n,
            representative_x_codes,
            &exceptional_states,
            &support_digest_blake3,
        );
    }
    let relative_states = representatives * representatives * width;
    let exceptional_relative_states = exceptional_states.len();

    let expand_started = Instant::now();
    let mut nogood_clauses = 0usize;
    for &[left_summand, right_summand] in &sides {
        for &(left_rep, right_rep, relative_shift) in &exceptional_states {
            for left_shift in 0..width {
                let right_shift = (left_shift + relative_shift) % width;
                let mut clause = Vec::with_capacity(
                    2 + 2 * frobenius_width
                        + if binary_representatives {
                            2 * representative_index_width
                        } else {
                            2
                        },
                );
                if binary_representatives {
                    push_forbidden_binary_assignment(
                        &mut clause,
                        representative_offset + left_summand * representative_index_width,
                        representative_index_width,
                        left_rep,
                    );
                    push_forbidden_binary_assignment(
                        &mut clause,
                        representative_offset + right_summand * representative_index_width,
                        representative_index_width,
                        right_rep,
                    );
                } else {
                    clause.push(
                        -((representative_offset
                            + left_summand * representatives
                            + left_rep
                            + 1) as Lit),
                    );
                    clause.push(
                        -((representative_offset
                            + right_summand * representatives
                            + right_rep
                            + 1) as Lit),
                    );
                }
                push_forbidden_binary_assignment(
                    &mut clause,
                    frobenius_offset + left_summand * frobenius_width,
                    frobenius_width,
                    left_shift,
                );
                push_forbidden_binary_assignment(
                    &mut clause,
                    frobenius_offset + right_summand * frobenius_width,
                    frobenius_width,
                    right_shift,
                );
                assert!(solver.add_clause(clause));
                nogood_clauses += 1;
            }
        }
    }
    let expand_ms = expand_started.elapsed().as_secs_f64() * 1000.0;

    json!({
        "enabled": true,
        "pair_table_entries": 0,
        "edge_selectors": 0,
        "relative_states_scanned": relative_states,
        "exceptional_relative_states": exceptional_relative_states,
        "nogood_clauses": nogood_clauses,
        "pairing_sides": sides.len(),
        "representatives": representatives,
        "representative_encoding": representative_encoding,
        "scan_ms": scan_ms,
        "expand_ms": expand_ms,
        "install_ms": started.elapsed().as_secs_f64() * 1000.0,
        "scan_parallel": !loaded_from_certificate,
        "loaded_from_certificate": loaded_from_certificate,
        "support_digest_blake3": support_digest_blake3,
        "certificate_in": cert_in,
        "certificate_out": cert_out,
        "claim_boundary": "Compressed exceptional relative-Frobenius pair-support nogoods only; reusable certificate optional; not an edge/pair table, not unrestricted extraction, not vs_rho, not ledger promotion"
    })
}

fn regular_s3_x_roots(curve: &KoblitzCurve, left: u64, right: u64) -> Option<[u64; 2]> {
    let n = curve.n;
    let irr = &curve.curve.irreducible;
    let left = F2mElement::from_biguint(&BigUint::from(left), n);
    let right = F2mElement::from_biguint(&BigUint::from(right), n);
    let sum = left.add(&right);
    let a = sum.square(irr);
    let product = left.mul(&right, irr);
    let product_square = product.square(irr);
    let inverse_combined = a.mul(&product_square, irr).flt_inverse(irr)?;
    let inverse_a = product_square.mul(&inverse_combined, irr);
    let inverse_product_square = a.mul(&inverse_combined, irr);
    let q = product.mul(&inverse_a, irr);
    let c = product_square.add(&curve.curve.b);
    let d = c.mul(&a, irr).mul(&inverse_product_square, irr);
    let mut half_trace = d.clone();
    let mut power = d.clone();
    for _ in 0..(n - 1) / 2 {
        power = power.square(irr).square(irr);
        half_trace = half_trace.add(&power);
    }
    if half_trace.square(irr).add(&half_trace) != d {
        return None;
    }
    let first = q.mul(&half_trace, irr);
    let second = first.add(&q);
    assert!(binary_semaev_s3(&left, &right, &first, &curve.curve.b, irr).is_zero());
    assert!(binary_semaev_s3(&left, &right, &second, &curve.curve.b, irr).is_zero());
    let raw = |value: &F2mElement| value.raw_bits().first().copied().unwrap_or(0);
    Some([raw(&first), raw(&second)])
}

fn frobenius_code(curve: &KoblitzCurve, code: u64, exponent: usize) -> u64 {
    let mut value = F2mElement::from_biguint(&BigUint::from(code), curve.n);
    for _ in 0..exponent % curve.n as usize {
        value = value.square(&curve.curve.irreducible);
    }
    value.raw_bits().first().copied().unwrap_or(0)
}

fn factor_base_frobenius_coordinates(
    curve: &KoblitzCurve,
    base: &PointBase,
) -> (Vec<u64>, HashMap<u64, (usize, usize)>) {
    let representatives: Vec<u64> = base
        .representatives
        .iter()
        .map(|point| match point {
            BinaryPoint::Affine { x, .. } => x.raw_bits().first().copied().unwrap_or(0),
            BinaryPoint::Infinity => panic!("factor-base representative must be affine"),
        })
        .collect();
    let mut coordinates = HashMap::new();
    for (representative, &code) in representatives.iter().enumerate() {
        let mut current = code;
        for exponent in 0..curve.n as usize {
            assert!(coordinates.insert(current, (representative, exponent)).is_none());
            current = frobenius_code(curve, current, 1);
        }
        assert_eq!(current, code);
    }
    assert_eq!(coordinates.len(), base.x_codes.len());
    assert!(base.x_codes.iter().all(|code| coordinates.contains_key(code)));
    (representatives, coordinates)
}

fn relative_frobenius_pair_stats(
    curve: &KoblitzCurve,
    base: &PointBase,
    seed: u64,
) -> serde_json::Value {
    let started = Instant::now();
    let swap_reduced = std::env::var("KIC_RELATIVE_SWAP_REDUCED").as_deref() == Ok("1");
    let (representatives, coordinates) = factor_base_frobenius_coordinates(curve, base);
    let degree = curve.n as usize;
    let mut shifted_representatives = vec![vec![0u64; degree]; representatives.len()];
    for (index, &code) in representatives.iter().enumerate() {
        shifted_representatives[index][0] = code;
        for exponent in 1..degree {
            shifted_representatives[index][exponent] =
                frobenius_code(curve, shifted_representatives[index][exponent - 1], 1);
        }
    }

    let blocks: Vec<_> = representatives
        .par_iter()
        .enumerate()
        .map(|(left_index, &left)| {
            let mut regular = 0usize;
            let mut exceptional = 0usize;
            let mut roots_out = Vec::with_capacity(2 * representatives.len() * degree);
            let mut block_digest = blake3::Hasher::new();
            for right_index in 0..representatives.len() {
                for relative_shift in 0..degree {
                    let inverse_shift = (degree - relative_shift) % degree;
                    if swap_reduced
                        && (left_index, right_index, relative_shift)
                            > (right_index, left_index, inverse_shift)
                    {
                        continue;
                    }
                    block_digest.update(&(left_index as u32).to_le_bytes());
                    block_digest.update(&(right_index as u32).to_le_bytes());
                    block_digest.update(&(relative_shift as u32).to_le_bytes());
                    let right = shifted_representatives[right_index][relative_shift];
                    match regular_s3_x_roots(curve, left, right) {
                        Some(mut roots) => {
                            roots.sort_unstable();
                            regular += 1;
                            block_digest.update(&[1]);
                            for root in roots {
                                block_digest.update(&root.to_le_bytes());
                                roots_out.push(root);
                            }
                        }
                        None => {
                            exceptional += 1;
                            block_digest.update(&[0]);
                        }
                    }
                }
            }
            (
                regular,
                exceptional,
                roots_out,
                *block_digest.finalize().as_bytes(),
            )
        })
        .collect();
    let regular_states = blocks.iter().map(|block| block.0).sum::<usize>();
    let exceptional_states = blocks.iter().map(|block| block.1).sum::<usize>();
    let root_entries = blocks.iter().map(|block| block.2.len()).sum::<usize>();
    let mut unique_root_codes = HashSet::with_capacity(root_entries);
    let mut digest = blake3::Hasher::new();
    digest.update(b"relative-frobenius-pair-block-digest-v1");
    for (left_index, block) in blocks.into_iter().enumerate() {
        digest.update(&(left_index as u32).to_le_bytes());
        digest.update(&block.3);
        unique_root_codes.extend(block.2);
    }

    let exhaustive = curve.n <= 11;
    let checks = if exhaustive {
        base.x_codes.len() * base.x_codes.len()
    } else {
        4096
    };
    let mut rng = StdRng::seed_from_u64(seed ^ 0x5245_4c46_524f_4250);
    let mut checked_regular = 0usize;
    let mut checked_exceptional = 0usize;
    for check in 0..checks {
        let (left_position, right_position) = if exhaustive {
            (check / base.x_codes.len(), check % base.x_codes.len())
        } else {
            (
                rng.gen_range(0..base.x_codes.len()),
                rng.gen_range(0..base.x_codes.len()),
            )
        };
        let left = base.x_codes[left_position];
        let right = base.x_codes[right_position];
        let &(left_representative, left_shift) = coordinates.get(&left).unwrap();
        let &(right_representative, right_shift) = coordinates.get(&right).unwrap();
        let relative_shift = (right_shift + degree - left_shift) % degree;
        let inverse_shift = (degree - relative_shift) % degree;
        let (canonical_left, canonical_right, canonical_shift, common_shift) = if swap_reduced
            && (left_representative, right_representative, relative_shift)
                > (right_representative, left_representative, inverse_shift)
        {
            (
                right_representative,
                left_representative,
                inverse_shift,
                right_shift,
            )
        } else {
            (
                left_representative,
                right_representative,
                relative_shift,
                left_shift,
            )
        };
        let canonical = regular_s3_x_roots(
            curve,
            representatives[canonical_left],
            shifted_representatives[canonical_right][canonical_shift],
        );
        let actual = regular_s3_x_roots(curve, left, right);
        match (canonical, actual) {
            (Some(canonical), Some(mut actual)) => {
                let mut expanded = canonical.map(|root| frobenius_code(curve, root, common_shift));
                expanded.sort_unstable();
                actual.sort_unstable();
                assert_eq!(expanded, actual);
                checked_regular += 1;
            }
            (None, None) => checked_exceptional += 1,
            _ => panic!("relative Frobenius canonicalization changed S3 root existence"),
        }
    }

    let representative_pairs = representatives.len() * representatives.len();
    let ordered_relative_states = representative_pairs * degree;
    let relative_states = if swap_reduced {
        (ordered_relative_states + representatives.len()) / 2
    } else {
        ordered_relative_states
    };
    assert_eq!(relative_states, regular_states + exceptional_states);
    let expanded_ordered_endpoint_pairs = base.x_codes.len() * base.x_codes.len();
    let expanded_endpoint_pairs = if swap_reduced {
        base.x_codes.len() * (base.x_codes.len() + 1) / 2
    } else {
        expanded_ordered_endpoint_pairs
    };
    assert_eq!(expanded_endpoint_pairs, relative_states * degree);
    assert_eq!(root_entries, 2 * regular_states);
    json!({
        "schema_version":"1.0",
        "kind":"relative_frobenius_pair_support_stats",
        "n":curve.n,
        "factor_base_x_coordinates":base.x_codes.len(),
        "orbit_representatives":representatives.len(),
        "representative_pairs_ordered":representative_pairs,
        "ordered_relative_shift_states":ordered_relative_states,
        "relative_shift_states":relative_states,
        "swap_reduced":swap_reduced,
        "regular_relative_states":regular_states,
        "exceptional_relative_states":exceptional_states,
        "regular_root_entries":root_entries,
        "unique_canonical_root_codes":unique_root_codes.len(),
        "expanded_ordered_endpoint_pairs":expanded_ordered_endpoint_pairs,
        "expanded_endpoint_pairs_in_selected_symmetry_class":expanded_endpoint_pairs,
        "expanded_regular_root_entries":root_entries * degree,
        "state_compression_ratio":expanded_endpoint_pairs as f64 / relative_states as f64,
        "root_entry_compression_ratio":degree,
        "canonical_payload_lower_bound_bytes":root_entries * (3 * std::mem::size_of::<u32>() + std::mem::size_of::<u64>()),
        "expanded_payload_lower_bound_bytes":root_entries * degree * (2 * std::mem::size_of::<u32>() + std::mem::size_of::<u64>()),
        "support_digest_blake3":digest.finalize().to_hex().to_string(),
        "support_digest_scheme":"blake3 ordered left-block digests v1",
        "rayon_threads":rayon::current_num_threads(),
        "equivariance_checks":checks,
        "equivariance_check_mode":if exhaustive {"exhaustive"} else {"deterministic_sample"},
        "checked_regular_pairs":checked_regular,
        "checked_exceptional_pairs":checked_exceptional,
        "equivariance_discrepancies":0,
        "construction_ms":started.elapsed().as_secs_f64()*1000.0,
        "claim_boundary":"Pair-support state compression and exact Frobenius-equivariance measurement only; no target join, relation extraction, SAT speedup, or sub-rho claim"
    })
}

fn guarded_s3_root_clauses(
    guard: &[Lit],
    third_offset: usize,
    selector: u32,
    roots: [u64; 2],
    width: usize,
) -> Vec<Vec<Lit>> {
    let mut clauses = Vec::with_capacity(2 * width);
    for bit in 0..width {
        let output = (third_offset + bit + 1) as Lit;
        let first = (roots[0] >> bit) & 1 == 1;
        let second = (roots[1] >> bit) & 1 == 1;
        if first == second {
            let mut clause = guard.to_vec();
            clause.push(if first { output } else { -output });
            clauses.push(clause);
            continue;
        }
        let mut forward = guard.to_vec();
        let mut reverse = guard.to_vec();
        if !first && second {
            forward.extend([-output, selector as Lit]);
            reverse.extend([output, -(selector as Lit)]);
        } else {
            forward.extend([output, selector as Lit]);
            reverse.extend([-output, -(selector as Lit)]);
        }
        clauses.push(forward);
        clauses.push(reverse);
    }
    clauses
}

fn parse_complete_external_model(contents: &str, variables: usize) -> Result<Vec<bool>, String> {
    let statuses: Vec<_> = contents
        .lines()
        .map(str::trim)
        .filter(|line| line.starts_with("s "))
        .collect();
    if statuses != ["s SATISFIABLE"] {
        return Err("expected exactly one SATISFIABLE status".to_owned());
    }
    let mut assignment = vec![None; variables];
    for line in contents.lines().map(str::trim) {
        let Some(values) = line.strip_prefix("v ") else {
            continue;
        };
        for token in values.split_whitespace() {
            let literal: i64 = token.parse().map_err(|_| "invalid model literal")?;
            if literal == 0 {
                continue;
            }
            let variable = literal.unsigned_abs();
            if variable > variables as u64 {
                return Err("model literal outside the declared variable range".to_owned());
            }
            let slot = &mut assignment[variable as usize - 1];
            let value = literal > 0;
            if slot.is_some_and(|previous| previous != value) {
                return Err("contradictory duplicate model literal".to_owned());
            }
            *slot = Some(value);
        }
    }
    assignment
        .into_iter()
        .map(|value| value.ok_or_else(|| "model omits a declared variable".to_owned()))
        .collect()
}

fn check_exported_assignment(dimacs: &str, model: &[bool]) -> Result<(usize, usize), String> {
    let mut header = None;
    let mut clause_count = 0;
    let mut xor_count = 0;
    for (line_number, line) in dimacs.lines().map(str::trim).enumerate() {
        if line.is_empty() || line.starts_with('c') {
            continue;
        }
        if line.starts_with("p ") {
            let parts: Vec<_> = line.split_whitespace().collect();
            if header.is_some() || parts.len() != 4 || parts[1] != "cnf" {
                return Err("invalid or repeated DIMACS header".to_owned());
            }
            let variables: usize = parts[2].parse().map_err(|_| "invalid variable count")?;
            let clauses: usize = parts[3].parse().map_err(|_| "invalid clause count")?;
            if variables != model.len() {
                return Err("assignment length differs from DIMACS header".to_owned());
            }
            header = Some(clauses);
            continue;
        }
        let (xor, row) = match line.strip_prefix('x') {
            Some(row) => (true, row),
            None => (false, line),
        };
        let literals: Vec<i64> = row
            .split_whitespace()
            .map(|token| token.parse().map_err(|_| "invalid DIMACS literal"))
            .collect::<Result<_, _>>()?;
        if literals.last() != Some(&0) {
            return Err("unterminated DIMACS constraint".to_owned());
        }
        let mut value = false;
        for &literal in &literals[..literals.len() - 1] {
            let variable = literal.unsigned_abs();
            if variable == 0 || variable > model.len() as u64 {
                return Err("invalid DIMACS variable".to_owned());
            }
            let literal_value = model[variable as usize - 1] ^ (literal < 0);
            value = if xor {
                value ^ literal_value
            } else {
                value || literal_value
            };
        }
        if !value {
            return Err(if xor {
                format!("violated XOR constraint at line {}: {line}", line_number + 1)
            } else {
                format!("violated CNF clause at line {}: {line}", line_number + 1)
            });
        }
        if xor {
            xor_count += 1;
        } else {
            clause_count += 1;
        }
    }
    if header != Some(clause_count) && header != Some(clause_count + xor_count) {
        return Err("missing header or incorrect CNF clause count".to_owned());
    }
    Ok((clause_count, xor_count))
}

fn numeric_chain_valid(
    model: &[bool],
    n: u32,
    pairing: usize,
    target_x: &F2mElement,
    b: &F2mElement,
    curve: &KoblitzCurve,
) -> bool {
    let width = n as usize;
    let values: Vec<_> = (0..6)
        .map(|index| {
            F2mElement::from_biguint(&BigUint::from(decode_code(model, index * width, width)), n)
        })
        .collect();
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => return false,
    };
    binary_semaev_s3(
        &values[pairing_indices[0]],
        &values[pairing_indices[1]],
        &values[4],
        b,
        &curve.curve.irreducible,
    )
    .is_zero()
        && binary_semaev_s3(
            &values[pairing_indices[2]],
            &values[pairing_indices[3]],
            &values[5],
            b,
            &curve.curve.irreducible,
        )
        .is_zero()
        && binary_semaev_s3(
            &values[4],
            &values[5],
            target_x,
            b,
            &curve.curve.irreducible,
        )
        .is_zero()
}

fn lift_x_tuple(
    curve: &KoblitzCurve,
    base: &PointBase,
    codes: &[u64; 4],
    target: &BinaryPoint,
) -> Option<[usize; 4]> {
    let point_index: HashMap<_, _> = base
        .points
        .iter()
        .enumerate()
        .map(|(index, point)| (point_key(point), index))
        .collect();
    let choices: Vec<Vec<usize>> = codes
        .iter()
        .map(|&code| {
            let x = F2mElement::from_biguint(&BigUint::from(code), curve.n);
            points_with_x(&curve.curve, &x)
                .iter()
                .filter_map(|point| point_index.get(&point_key(point)).copied())
                .collect()
        })
        .collect();
    if choices.iter().any(Vec::is_empty) {
        return None;
    }
    for &a in &choices[0] {
        for &b in &choices[1] {
            for &c in &choices[2] {
                for &d in &choices[3] {
                    let indices = [a, b, c, d];
                    let sum = indices.iter().fold(BinaryPoint::Infinity, |acc, &index| {
                        curve.add(&acc, &base.points[index])
                    });
                    if sum == *target {
                        return Some(indices);
                    }
                }
            }
        }
    }
    None
}

fn has_exceptional_cancellation_lift(
    curve: &KoblitzCurve,
    base: &PointBase,
    codes: &[u64; 4],
    target: &BinaryPoint,
) -> bool {
    let point_index: HashMap<_, _> = base
        .points
        .iter()
        .enumerate()
        .map(|(index, point)| (point_key(point), index))
        .collect();
    let choices: Vec<Vec<usize>> = codes
        .iter()
        .map(|&code| {
            let x = F2mElement::from_biguint(&BigUint::from(code), curve.n);
            points_with_x(&curve.curve, &x)
                .iter()
                .filter_map(|point| point_index.get(&point_key(point)).copied())
                .collect()
        })
        .collect();
    if choices.iter().any(Vec::is_empty) {
        return false;
    }
    for &a in &choices[0] {
        for &b in &choices[1] {
            for &c in &choices[2] {
                for &d in &choices[3] {
                    let indices = [a, b, c, d];
                    let sum = indices.iter().fold(BinaryPoint::Infinity, |acc, &index| {
                        curve.add(&acc, &base.points[index])
                    });
                    if sum != *target {
                        continue;
                    }
                    for left in 0..4 {
                        for right in left + 1..4 {
                            if curve.add(&base.points[indices[left]], &base.points[indices[right]])
                                == BinaryPoint::Infinity
                            {
                                return true;
                            }
                        }
                    }
                }
            }
        }
    }
    false
}

fn direct_valid_x_tuples(
    curve: &KoblitzCurve,
    base: &PointBase,
    target: &BinaryPoint,
    symmetry_breaking: bool,
) -> BTreeSet<[u64; 4]> {
    let mut result = BTreeSet::new();
    for &x1 in &base.x_codes {
        for &x2 in &base.x_codes {
            for &x3 in &base.x_codes {
                for &x4 in &base.x_codes {
                    let mut tuple = [x1, x2, x3, x4];
                    if lift_x_tuple(curve, base, &tuple, target).is_some() {
                        if symmetry_breaking {
                            tuple.sort_unstable();
                        }
                        result.insert(tuple);
                    }
                }
            }
        }
    }
    result
}

fn direct_exceptional_x_tuples(
    curve: &KoblitzCurve,
    base: &PointBase,
    target: &BinaryPoint,
    symmetry_breaking: bool,
) -> BTreeSet<[u64; 4]> {
    let mut result = BTreeSet::new();
    for &x1 in &base.x_codes {
        for &x2 in &base.x_codes {
            for &x3 in &base.x_codes {
                for &x4 in &base.x_codes {
                    let mut tuple = [x1, x2, x3, x4];
                    if has_exceptional_cancellation_lift(curve, base, &tuple, target) {
                        if symmetry_breaking {
                            tuple.sort_unstable();
                        }
                        result.insert(tuple);
                    }
                }
            }
        }
    }
    result
}

struct ModularEchelon {
    pivots: BTreeMap<usize, Vec<u64>>,
    modulus: u64,
    columns: usize,
}

impl ModularEchelon {
    fn new(columns: usize, modulus: u64) -> Self {
        Self {
            pivots: BTreeMap::new(),
            modulus,
            columns,
        }
    }

    fn rank(&self) -> usize {
        self.pivots.len()
    }

    fn insert(&mut self, mut row: Vec<u64>) -> bool {
        assert_eq!(row.len(), self.columns);
        for (&pivot, existing) in &self.pivots {
            let factor = row[pivot];
            if factor == 0 {
                continue;
            }
            for column in pivot..self.columns {
                let product =
                    ((factor as u128 * existing[column] as u128) % self.modulus as u128) as u64;
                row[column] = if row[column] >= product {
                    row[column] - product
                } else {
                    self.modulus - (product - row[column])
                };
            }
        }
        let Some(pivot) = row.iter().position(|&value| value != 0) else {
            return false;
        };
        let inverse = modpow_u64(row[pivot], self.modulus - 2, self.modulus);
        for value in &mut row[pivot..] {
            *value = ((*value as u128 * inverse as u128) % self.modulus as u128) as u64;
        }
        for existing in self.pivots.values_mut() {
            let factor = existing[pivot];
            if factor == 0 {
                continue;
            }
            for column in pivot..self.columns {
                let product =
                    ((factor as u128 * row[column] as u128) % self.modulus as u128) as u64;
                existing[column] = if existing[column] >= product {
                    existing[column] - product
                } else {
                    self.modulus - (product - existing[column])
                };
            }
        }
        self.pivots.insert(pivot, row);
        true
    }
}

fn modpow_u64(mut base: u64, mut exponent: u64, modulus: u64) -> u64 {
    let mut result = 1u64;
    while exponent != 0 {
        if exponent & 1 == 1 {
            result = ((result as u128 * base as u128) % modulus as u128) as u64;
        }
        base = ((base as u128 * base as u128) % modulus as u128) as u64;
        exponent >>= 1;
    }
    result
}

fn dense_rank_mod(rows: &[Vec<u64>], columns: usize, modulus: u64) -> usize {
    let mut matrix = rows.to_vec();
    let mut rank = 0usize;
    for column in 0..columns {
        let Some(pivot) = (rank..matrix.len()).find(|&row| matrix[row][column] != 0) else {
            continue;
        };
        matrix.swap(rank, pivot);
        let inverse = modpow_u64(matrix[rank][column], modulus - 2, modulus);
        for value in &mut matrix[rank][column..] {
            *value = ((*value as u128 * inverse as u128) % modulus as u128) as u64;
        }
        for row in 0..matrix.len() {
            if row == rank || matrix[row][column] == 0 {
                continue;
            }
            let factor = matrix[row][column];
            for index in column..columns {
                let product =
                    ((factor as u128 * matrix[rank][index] as u128) % modulus as u128) as u64;
                matrix[row][index] = if matrix[row][index] >= product {
                    matrix[row][index] - product
                } else {
                    modulus - (product - matrix[row][index])
                };
            }
        }
        rank += 1;
        if rank == matrix.len() {
            break;
        }
    }
    rank
}

fn solve_full_column_rank_system(
    rows: &[Vec<u64>],
    right_hand_sides: &[u64],
    columns: usize,
    modulus: u64,
) -> Option<Vec<u64>> {
    assert_eq!(rows.len(), right_hand_sides.len());
    let mut matrix: Vec<Vec<u64>> = rows
        .iter()
        .zip(right_hand_sides)
        .map(|(row, &rhs)| {
            let mut augmented = row.clone();
            augmented.push(rhs);
            augmented
        })
        .collect();
    let mut pivot_row = 0usize;
    for column in 0..columns {
        let pivot = (pivot_row..matrix.len()).find(|&row| matrix[row][column] != 0)?;
        matrix.swap(pivot_row, pivot);
        let inverse = modpow_u64(matrix[pivot_row][column], modulus - 2, modulus);
        for value in &mut matrix[pivot_row][column..=columns] {
            *value = ((*value as u128 * inverse as u128) % modulus as u128) as u64;
        }
        for row in 0..matrix.len() {
            if row == pivot_row || matrix[row][column] == 0 {
                continue;
            }
            let factor = matrix[row][column];
            for index in column..=columns {
                let product =
                    ((factor as u128 * matrix[pivot_row][index] as u128) % modulus as u128) as u64;
                matrix[row][index] = if matrix[row][index] >= product {
                    matrix[row][index] - product
                } else {
                    modulus - (product - matrix[row][index])
                };
            }
        }
        pivot_row += 1;
    }
    Some((0..columns).map(|row| matrix[row][columns]).collect())
}

struct CmsChildUsage {
    pid: u32,
    user_seconds: f64,
    system_seconds: f64,
    peak_rss_bytes: u64,
}

#[cfg(unix)]
fn execute_cms_with_rusage(
    mut command: Command,
    stdout_path: &std::path::Path,
    stderr_path: &std::path::Path,
) -> (std::process::Output, Option<CmsChildUsage>) {
    use std::os::unix::process::ExitStatusExt;
    use std::process::Stdio;

    command.stdout(Stdio::from(std::fs::File::create(stdout_path).unwrap()));
    command.stderr(Stdio::from(std::fs::File::create(stderr_path).unwrap()));
    let child = command.spawn().unwrap();
    let pid = child.id();
    let mut status = 0i32;
    let mut usage = std::mem::MaybeUninit::<libc::rusage>::zeroed();
    loop {
        let waited = unsafe { libc::wait4(pid as libc::pid_t, &mut status, 0, usage.as_mut_ptr()) };
        if waited == pid as libc::pid_t {
            break;
        }
        assert_eq!(waited, -1);
        let error = std::io::Error::last_os_error();
        if error.raw_os_error() == Some(libc::EINTR) {
            continue;
        }
        panic!("wait4 failed for CryptoMiniSat child {pid}: {error}");
    }
    drop(child);
    let usage = unsafe { usage.assume_init() };
    let peak_rss_bytes = if cfg!(target_os = "macos") {
        usage.ru_maxrss as u64
    } else {
        (usage.ru_maxrss as u64).saturating_mul(1024)
    };
    let child_usage = CmsChildUsage {
        pid,
        user_seconds: usage.ru_utime.tv_sec as f64 + usage.ru_utime.tv_usec as f64 / 1_000_000.0,
        system_seconds: usage.ru_stime.tv_sec as f64 + usage.ru_stime.tv_usec as f64 / 1_000_000.0,
        peak_rss_bytes,
    };
    let output = std::process::Output {
        status: std::process::ExitStatus::from_raw(status),
        stdout: std::fs::read(stdout_path).unwrap(),
        stderr: std::fs::read(stderr_path).unwrap(),
    };
    (output, Some(child_usage))
}

#[cfg(not(unix))]
fn execute_cms_with_rusage(
    mut command: Command,
    _stdout_path: &std::path::Path,
    _stderr_path: &std::path::Path,
) -> (std::process::Output, Option<CmsChildUsage>) {
    (command.output().unwrap(), None)
}

fn solve_with_cryptominisat(
    encoding: &S5Encoding,
    cms: &str,
    seconds: u64,
    conflicts: u64,
    artifact_directory: &std::path::Path,
    instance_id: &str,
) -> (SolveResult, Option<Vec<bool>>, f64, i32) {
    std::fs::create_dir_all(artifact_directory).unwrap();
    let dimacs = to_dimacs_xor(&encoding.solver);
    let formula_path = artifact_directory.join(format!("{instance_id}.xor"));
    let stdout_path = artifact_directory.join(format!("{instance_id}.cms.out"));
    let stderr_path = artifact_directory.join(format!("{instance_id}.cms.err"));
    std::fs::write(&formula_path, dimacs.as_bytes()).unwrap();
    let started = Instant::now();
    let mut command = Command::new(cms);
    command
        .args([
            "--verb",
            "0",
            "--threads",
            "1",
            "--random",
            "0",
            "--maxtime",
            &seconds.to_string(),
            "--maxconfl",
            &conflicts.to_string(),
            "--printsol",
            "1",
        ])
        .arg(&formula_path);
    let (output, child_usage) = execute_cms_with_rusage(command, &stdout_path, &stderr_path);
    let wall_ms = started.elapsed().as_secs_f64() * 1000.0;
    std::fs::write(&stdout_path, &output.stdout).unwrap();
    std::fs::write(&stderr_path, &output.stderr).unwrap();
    let exit_code = output.status.code().unwrap_or(-1);
    let stdout = String::from_utf8(output.stdout).unwrap();
    let outcome = match exit_code {
        10 => SolveResult::Sat,
        20 => SolveResult::Unsat,
        15 => SolveResult::Unknown,
        _ => panic!("CryptoMiniSat failed with exit code {exit_code}"),
    };
    let required_status = match outcome {
        SolveResult::Sat => "s SATISFIABLE",
        SolveResult::Unsat => "s UNSATISFIABLE",
        SolveResult::Unknown => "s INDETERMINATE",
    };
    assert_eq!(
        stdout
            .lines()
            .map(str::trim)
            .filter(|line| line.starts_with("s "))
            .collect::<Vec<_>>(),
        vec![required_status]
    );
    let model = if outcome == SolveResult::Sat {
        let model =
            parse_complete_external_model(&stdout, encoding.solver.n_vars() as usize).unwrap();
        check_exported_assignment(&dimacs, &model).unwrap();
        Some(model)
    } else {
        None
    };
    if let Some(usage) = child_usage {
        let resource_path = artifact_directory.join(format!("{instance_id}.cms.resource.json"));
        std::fs::write(
            resource_path,
            serde_json::to_vec_pretty(&json!({
                "schema_version":"1.0",
                "kind":"cryptominisat_child_resource_receipt",
                "pid":usage.pid,
                "exit_code":exit_code,
                "wall_ms":wall_ms,
                "child_user_seconds":usage.user_seconds,
                "child_system_seconds":usage.system_seconds,
                "child_peak_rss_bytes":usage.peak_rss_bytes,
                "rss_scope":"this directly waited CryptoMiniSat child",
                "rss_unit":"bytes",
                "formula_path":formula_path,
                "cms_path":cms,
            }))
            .unwrap(),
        )
        .unwrap();
    }
    (outcome, model, wall_ms, exit_code)
}

fn run_external_rank_batch(
    curve: &KoblitzCurve,
    base: &PointBase,
    exact_pairs: &HashMap<(BigUint, BigUint), (usize, usize)>,
    n: u32,
    a: u8,
    eta_numerator: u32,
    eta_denominator: u32,
    root_seed: u64,
    base_ms: f64,
    reference_pair_index_ms: f64,
    task_id: &str,
) -> serde_json::Value {
    assert!(n <= 19, "external rank batch is bounded to n <= 19");
    let batch_started = Instant::now();
    let cms = std::env::var("KIC_CMS_PATH")
        .unwrap_or_else(|_| "/opt/homebrew/bin/cryptominisat5".to_owned());
    let artifact_directory = std::path::PathBuf::from(
        std::env::var("KIC_BATCH_ARTIFACT_DIR").expect("KIC_BATCH_ARTIFACT_DIR is required"),
    );
    let target_cap: usize = std::env::var("KIC_BATCH_TARGET_CAP")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(512);
    let surplus: usize = std::env::var("KIC_BATCH_RELATION_SURPLUS")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(32);
    let solver_seconds: u64 = std::env::var("KIC_BATCH_SOLVER_SECONDS")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(5);
    let solver_conflicts: u64 = std::env::var("KIC_BATCH_SOLVER_CONFLICTS")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(500_000);
    let drop_final_s3 = std::env::var("KIC_BATCH_DROP_FINAL_S3").as_deref() == Ok("1");
    let edge_selectors = std::env::var("KIC_BATCH_EDGE_SELECTORS").as_deref() == Ok("1");

    let pair_table_started = Instant::now();
    let entries = pair_x_entries(curve, base);
    let pair_table_ms = pair_table_started.elapsed().as_secs_f64() * 1000.0;
    let batch_setup_started = Instant::now();
    let structure = FieldStructure::new(n, &curve.curve.irreducible);
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let mut rng = StdRng::seed_from_u64(root_seed);
    let published_dlog = rng.gen_range(1..modulus);
    let q = curve.mul(curve.generator(), &BigUint::from(published_dlog));
    let matrix_columns = base.orbit_columns + 1;
    let mut echelon = ModularEchelon::new(matrix_columns, modulus);
    let mut rows = Vec::new();
    let mut right_hand_sides = Vec::new();
    let mut relations = Vec::new();
    let mut target_observations = Vec::new();
    let mut accepted = 0usize;
    let mut full_rank_at = None;
    let mut duplicate_rows = 0usize;
    let mut trials = 0usize;
    let mut identity_targets = 0usize;
    let mut negative_targets = 0usize;
    let mut censored_targets = 0usize;
    let mut exceptional_relations = 0usize;
    let mut solver_attempts = 0usize;
    let mut formula_ms = 0.0f64;
    let mut solver_ms = 0.0f64;
    let mut validation_ms = 0.0f64;
    let mut reference_oracle_validation_ms = 0.0f64;
    let batch_setup_ms = batch_setup_started.elapsed().as_secs_f64() * 1000.0;
    let collection_started = Instant::now();

    while trials < target_cap {
        if let Some(full_at) = full_rank_at {
            if accepted >= full_at + surplus {
                break;
            }
        }
        trials += 1;
        let coefficient_a = rng.gen_range(0..modulus);
        let coefficient_b = rng.gen_range(1..modulus);
        let target_scalar = ((coefficient_a as u128
            + coefficient_b as u128 * published_dlog as u128)
            % modulus as u128) as u64;
        let target = curve.add(
            &curve.mul(curve.generator(), &BigUint::from(coefficient_a)),
            &curve.mul(&q, &BigUint::from(coefficient_b)),
        );
        if target == BinaryPoint::Infinity {
            assert_eq!(target_scalar, 0);
            identity_targets += 1;
            continue;
        }
        let exceptional = exact_cancellation_witness(curve, base, exact_pairs, &target);
        let mut selected_indices = exceptional;
        let mut selected_pairing = None;
        let mut attempts = Vec::new();
        if selected_indices.is_some() {
            exceptional_relations += 1;
        } else {
            let BinaryPoint::Affine { x: target_x, .. } = &target else {
                unreachable!();
            };
            for pairing in 0..3 {
                let encoding_started = Instant::now();
                let encoding = if edge_selectors {
                    encode_balanced_s5_target_edge_selectors(
                        curve,
                        n,
                        target_x,
                        &base.x_codes,
                        &entries,
                        true,
                        pairing,
                    )
                } else {
                    encode_balanced_s5_pair_table(
                        curve,
                        n,
                        target_x,
                        &curve.curve.b,
                        &structure,
                        &base.x_codes,
                        &entries,
                        true,
                        pairing,
                        false,
                        true,
                        false,
                        true,
                        drop_final_s3,
                    )
                };
                let this_formula_ms = encoding_started.elapsed().as_secs_f64() * 1000.0;
                formula_ms += this_formula_ms;
                solver_attempts += 1;
                let instance_id = format!("trial-{trials:04}-pairing-{pairing}");
                let (outcome, model, this_solver_ms, exit_code) = solve_with_cryptominisat(
                    &encoding,
                    &cms,
                    solver_seconds,
                    solver_conflicts,
                    &artifact_directory,
                    &instance_id,
                );
                solver_ms += this_solver_ms;
                let cms_resource_path =
                    artifact_directory.join(format!("{instance_id}.cms.resource.json"));
                attempts.push(json!({
                    "pairing":pairing,
                    "outcome":match outcome { SolveResult::Sat=>"SAT", SolveResult::Unsat=>"UNSAT", SolveResult::Unknown=>"UNKNOWN" },
                    "exit_code":exit_code,
                    "formula_ms":this_formula_ms,
                    "solver_ms":this_solver_ms,
                    "variables":encoding.solver.n_vars(),
                    "ordinary_clauses":encoding.solver.n_clauses(),
                    "native_xor_rows":encoding.solver.n_xors(),
                    "final_support_clauses":encoding.final_support_clauses,
                    "final_compatible_selector_pairs":encoding.final_compatible_selector_pairs,
                    "algebra_encoding":encoding.algebra_encoding,
                    "final_s3_circuit_installed":encoding.final_s3_circuit_installed,
                    "edge_selector_variables":encoding.edge_selector_variables,
                    "target_compatible_pair_edges":encoding.target_compatible_pair_edges,
                    "globally_sorted_compatible_pair_edges":encoding.globally_sorted_compatible_pair_edges,
                    "edge_link_xor_rows":encoding.edge_link_xor_rows,
                    "edge_selector_domain_empty":encoding.edge_selector_domain_empty,
                    "formula_path":artifact_directory.join(format!("{instance_id}.xor")),
                    "cms_stdout_path":artifact_directory.join(format!("{instance_id}.cms.out")),
                    "cms_stderr_path":artifact_directory.join(format!("{instance_id}.cms.err")),
                    "cms_resource_path":cms_resource_path.exists().then_some(cms_resource_path),
                }));
                if outcome != SolveResult::Sat {
                    continue;
                }
                let validation_started = Instant::now();
                let model = model.unwrap();
                assert!(numeric_chain_valid(
                    &model[..encoding.problem_variables],
                    n,
                    pairing,
                    target_x,
                    &curve.curve.b,
                    curve,
                ));
                let width = n as usize;
                let codes: [u64; 4] =
                    std::array::from_fn(|index| decode_code(&model, index * width, width));
                assert!(codes.windows(2).all(|pair| pair[0] <= pair[1]));
                selected_indices = lift_x_tuple(curve, base, &codes, &target);
                assert!(selected_indices.is_some());
                selected_pairing = Some(pairing);
                validation_ms += validation_started.elapsed().as_secs_f64() * 1000.0;
                break;
            }
        }

        let Some(indices) = selected_indices else {
            let reference_started = Instant::now();
            let expected = exact_four_witness(curve, &base.points, exact_pairs, &target);
            reference_oracle_validation_ms += reference_started.elapsed().as_secs_f64() * 1000.0;
            if attempts.iter().any(|entry| entry["outcome"] == "UNKNOWN") {
                censored_targets += 1;
            } else {
                assert!(
                    attempts.iter().all(|entry| entry["outcome"] == "UNSAT"),
                    "a non-SAT terminal target must be UNSAT in every pairing"
                );
                assert!(
                    expected.is_none(),
                    "complete SAT pairings rejected a direct four-sum witness"
                );
                negative_targets += 1;
            }
            target_observations.push(json!({
                "trial":trials,
                "coefficient_a":coefficient_a,
                "coefficient_b":coefficient_b,
                "published_target_scalar":target_scalar,
                "decomposable":expected.is_some(),
                "relation_admitted":false,
                "attempts":attempts,
            }));
            continue;
        };
        let group_validation_started = Instant::now();
        let factor_sum = indices.iter().fold(BinaryPoint::Infinity, |sum, &index| {
            curve.add(&sum, &base.points[index])
        });
        assert_eq!(factor_sum, target);
        let mut row = vec![0u64; matrix_columns];
        for &index in &indices {
            let (column, coefficient) = base.point_labels[index];
            row[column] = (row[column] + coefficient) % modulus;
        }
        row[base.orbit_columns] = (modulus - coefficient_b) % modulus;
        let relation_left = (0..base.orbit_columns).fold(BinaryPoint::Infinity, |sum, column| {
            curve.add(
                &sum,
                &curve.mul(&base.representatives[column], &BigUint::from(row[column])),
            )
        });
        let relation_left = curve.add(
            &relation_left,
            &curve.mul(&q, &BigUint::from(row[base.orbit_columns])),
        );
        let relation_right = curve.mul(curve.generator(), &BigUint::from(coefficient_a));
        assert_eq!(relation_left, relation_right);
        validation_ms += group_validation_started.elapsed().as_secs_f64() * 1000.0;
        accepted += 1;
        let independent = echelon.insert(row.clone());
        if !independent {
            duplicate_rows += 1;
        }
        rows.push(row.clone());
        right_hand_sides.push(coefficient_a);
        assert_eq!(
            echelon.rank(),
            dense_rank_mod(&rows, matrix_columns, modulus)
        );
        if full_rank_at.is_none() && echelon.rank() == matrix_columns {
            full_rank_at = Some(accepted);
        }
        relations.push(json!({
            "trial":trials,
            "coefficient_a":coefficient_a,
            "coefficient_b":coefficient_b,
            "published_target_scalar":target_scalar,
            "point_indices":indices,
            "row":row,
            "pairing":selected_pairing,
            "exceptional_cancellation":selected_pairing.is_none(),
            "rank_after":echelon.rank(),
            "attempts":attempts,
            "group_verified":true,
        }));
    }
    let collection_ms = collection_started.elapsed().as_secs_f64() * 1000.0;
    let algorithm_collection_ms = (collection_ms - reference_oracle_validation_ms).max(0.0);
    let status = if full_rank_at.is_some_and(|full_at| accepted >= full_at + surplus) {
        "RANK_PLUS_SURPLUS"
    } else if trials >= target_cap {
        "TARGET_CAP"
    } else {
        "INCOMPLETE"
    };
    let linear_solve_started = Instant::now();
    let solution = (echelon.rank() == matrix_columns).then(|| {
        solve_full_column_rank_system(&rows, &right_hand_sides, matrix_columns, modulus).unwrap()
    });
    let linear_solve_ms = linear_solve_started.elapsed().as_secs_f64() * 1000.0;
    let solution_validation_started = Instant::now();
    if let Some(solution) = &solution {
        assert_eq!(solution[base.orbit_columns], published_dlog);
        for (column, representative) in base.representatives.iter().enumerate() {
            assert_eq!(
                curve.mul(curve.generator(), &BigUint::from(solution[column])),
                *representative
            );
        }
        for (row, &rhs) in rows.iter().zip(&right_hand_sides) {
            let value = row.iter().zip(solution).fold(0u64, |sum, (&left, &right)| {
                (sum + ((left as u128 * right as u128) % modulus as u128) as u64) % modulus
            });
            assert_eq!(value, rhs);
        }
    }
    let solution_validation_ms = solution_validation_started.elapsed().as_secs_f64() * 1000.0;
    let charged_total_ms = base_ms
        + reference_pair_index_ms
        + pair_table_ms
        + batch_setup_ms
        + algorithm_collection_ms
        + linear_solve_ms
        + solution_validation_ms;
    let all_inclusive_component_ms = charged_total_ms + reference_oracle_validation_ms;
    let batch_function_wall_ms = batch_started.elapsed().as_secs_f64() * 1000.0;
    json!({
        "schema_version":"1.0",
        "task_id":task_id,
        "kind":"retained_pair_table_external_sat_rank_batch",
        "scope":"public synthetic aG+bQ relations with published dlog validator label; no external point, private key, or key recovery",
        "n":n,
        "a":a,
        "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
        "root_seed":root_seed,
        "published_dlog_validator_label":published_dlog,
        "target_point_construction":"aG_plus_bQ",
        "published_dlog_used_to_construct_target_points":false,
        "recovered_dlog":solution.as_ref().map(|values| values[base.orbit_columns]),
        "factor_base_log_solution":solution.as_ref().map(|values| &values[..base.orbit_columns]),
        "linear_solution_verified":solution.is_some(),
        "orbit_columns":base.orbit_columns,
        "matrix_columns":matrix_columns,
        "factor_base_points":base.points.len(),
        "factor_base_x_coordinates":base.x_codes.len(),
        "field_modulus_low_terms":curve.curve.irreducible.low_terms,
        "subgroup_order":modulus,
        "cofactor":curve.cofactor.to_u64().unwrap(),
        "generator":affine_coordinates(curve.generator()),
        "published_q":affine_coordinates(&q),
        "factor_base_point_coordinates":base.points.iter().map(affine_coordinates).collect::<Vec<_>>(),
        "factor_base_point_labels":base.point_labels,
        "factor_base_representatives":base.representatives.iter().map(affine_coordinates).collect::<Vec<_>>(),
        "pair_table_entries":entries.len(),
        "support_table_builds":1,
        "support_table_reused":true,
        "drop_final_s3":drop_final_s3 || edge_selectors,
        "requested_pair_table_drop_final_s3":drop_final_s3,
        "edge_selectors_enabled":edge_selectors,
        "relation_encoder_classification":if edge_selectors {
            "exact_target_specific_pair_pair_join_followed_by_sat_selection"
        } else {
            "retained_pair_tables_with_final_compatibility_support_and_sat"
        },
        "edge_selector_final_s3_omitted":edge_selectors,
        "target_specific_pair_pair_join_charged_in_formula_construction_ms":edge_selectors,
        "status":status,
        "target_cap":target_cap,
        "target_trials":trials,
        "identity_targets_skipped":identity_targets,
        "negative_targets":negative_targets,
        "censored_targets":censored_targets,
        "solver_attempts":solver_attempts,
        "admitted_relations":accepted,
        "exceptional_relations":exceptional_relations,
        "terminal_rank":echelon.rank(),
        "full_rank_at_relation":full_rank_at,
        "required_surplus_relations":surplus,
        "surplus_relations":full_rank_at.map_or(0, |value| accepted-value),
        "duplicate_rows":duplicate_rows,
        "all_relations_group_verified":true,
        "rank_dense_crosschecked_after_every_relation":true,
        "base_ms":base_ms,
        "reference_pair_index_ms":reference_pair_index_ms,
        "pair_table_ms":pair_table_ms,
        "batch_setup_ms":batch_setup_ms,
        "formula_construction_ms":formula_ms,
        "cryptominisat_wall_ms":solver_ms,
        "validation_ms":validation_ms,
        "reference_oracle_validation_ms":reference_oracle_validation_ms,
        "collection_wall_ms":collection_ms,
        "algorithm_collection_ms":algorithm_collection_ms,
        "linear_solve_ms":linear_solve_ms,
        "solution_validation_ms":solution_validation_ms,
        "batch_function_wall_ms":batch_function_wall_ms,
        "charged_total_ms":charged_total_ms,
        "all_inclusive_component_ms":all_inclusive_component_ms,
        "cms_path":cms,
        "cms_seconds_per_pairing":solver_seconds,
        "cms_conflicts_per_pairing":solver_conflicts,
        "artifact_directory":artifact_directory,
        "relations":relations,
        "nonrelation_targets":target_observations,
    })
}

fn main() {
    let task_id = std::env::var("KIC_TASK_ID").unwrap_or_else(|_| TASK_ID.to_owned());
    let arguments: Vec<_> = std::env::args().collect();
    assert_eq!(
        arguments.len(),
        10,
        "usage: <n> <a> <eta_num> <eta_den> <planted|natural|proven_negative|scalar> <seed> <conflicts> <models> <internal|emit_xor|validate_model|stats|coverage|relative_pair_stats|batch_external_rank>"
    );
    let n: u32 = arguments[1].parse().unwrap();
    let a: u8 = arguments[2].parse().unwrap();
    let eta_numerator: u32 = arguments[3].parse().unwrap();
    let eta_denominator: u32 = arguments[4].parse().unwrap();
    let target_class = TargetClass::parse(&arguments[5]);
    let seed: u64 = arguments[6].parse().unwrap();
    let conflict_budget: u64 = arguments[7].parse().unwrap();
    let model_cap: usize = arguments[8].parse().unwrap();
    let backend = &arguments[9];
    assert!(matches!(
        backend.as_str(),
        "internal"
            | "emit_xor"
            | "validate_model"
            | "stats"
            | "coverage"
            | "relative_pair_stats"
            | "batch_external_rank"
    ));
    assert!(matches!(n, 7 | 11 | 13 | 17 | 19 | 23 | 37 | 41 | 53));
    assert!(conflict_budget > 0 && model_cap > 0);

    let construction_started = Instant::now();
    let curve = KoblitzCurve::new(a, n).unwrap();
    let signed_size = 2 * n as usize;
    let columns = balanced_orbits(
        &curve.subgroup_order,
        signed_size,
        eta_numerator,
        eta_denominator,
    );
    let factor_base_input_path = std::env::var("KIC_FACTOR_BASE_JSONL").ok();
    let (base, factor_base_input_hash, factor_base_input_blake3) =
        if let Some(path) = factor_base_input_path.as_deref() {
            let (base, base_hash, source_hash) =
                point_defined_base_from_jsonl(&curve, columns, path);
            (base, Some(base_hash), Some(source_hash))
        } else {
            (point_defined_base(&curve, columns), None, None)
        };
    assert_eq!(base.signed_size, signed_size);
    let base_ms = construction_started.elapsed().as_secs_f64() * 1000.0;
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let mut rng = StdRng::seed_from_u64(seed);

    let reference_started = Instant::now();
    let exact_pairs = (n <= 23).then(|| pair_index(&curve, &base.points));
    let reference_pair_index_ms = reference_started.elapsed().as_secs_f64() * 1000.0;
    if backend == "relative_pair_stats" {
        let mut result = relative_frobenius_pair_stats(&curve, &base, seed);
        let object = result.as_object_mut().unwrap();
        object.insert("task_id".to_owned(), json!(task_id));
        object.insert("a".to_owned(), json!(a));
        object.insert(
            "eta".to_owned(),
            json!({"numerator":eta_numerator,"denominator":eta_denominator}),
        );
        object.insert("factor_base_points".to_owned(), json!(base.points.len()));
        object.insert("orbit_columns".to_owned(), json!(base.orbit_columns));
        object.insert("base_ms".to_owned(), json!(base_ms));
        object.insert(
            "factor_base_input_path".to_owned(),
            json!(factor_base_input_path),
        );
        object.insert(
            "factor_base_input_hash".to_owned(),
            json!(factor_base_input_hash),
        );
        object.insert(
            "factor_base_input_blake3".to_owned(),
            json!(factor_base_input_blake3),
        );
        println!("{result}");
        return;
    }
    if backend == "coverage" {
        assert!(n <= 17, "exact four-sum census is bounded to n <= 17");
        let coverage_started = Instant::now();
        let (pair_sum_points, reachable_group_elements, negative_scalars) =
            exact_four_sum_coverage(&curve, &base, exact_pairs.as_ref().unwrap());
        let coverage_ms = coverage_started.elapsed().as_secs_f64() * 1000.0;
        let nonzero_targets = curve.subgroup_order.to_u64().unwrap() - 1;
        println!(
            "{}",
            json!({
                "schema_version":"1.0", "task_id":task_id,
                "kind":"exact_four_sum_subgroup_coverage",
                "n":n, "a":a,
                "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
                "seed":seed,
                "factor_base_points":base.points.len(),
                "factor_base_x_coordinates":base.x_codes.len(),
                "orbit_columns":base.orbit_columns,
                "pair_sum_points":pair_sum_points,
                "reachable_group_elements_including_identity":reachable_group_elements,
                "nonzero_subgroup_targets":nonzero_targets,
                "reachable_nonzero_subgroup_targets":nonzero_targets-negative_scalars.len() as u64,
                "negative_target_count":negative_scalars.len(),
                "negative_scalars":negative_scalars,
                "complete_nonzero_subgroup_coverage":negative_scalars.is_empty(),
                "base_ms":base_ms,
                "reference_pair_index_ms":reference_pair_index_ms,
                "coverage_ms":coverage_ms,
                "scope":"exact finite public factor-base four-sum coverage; no external point or key recovery"
            })
        );
        return;
    }
    if backend == "batch_external_rank" {
        let result = run_external_rank_batch(
            &curve,
            &base,
            exact_pairs.as_ref().unwrap(),
            n,
            a,
            eta_numerator,
            eta_denominator,
            seed,
            base_ms,
            reference_pair_index_ms,
            &task_id,
        );
        println!("{result}");
        return;
    }
    let (published_scalar, planted_indices, rejected_identity_plantings, target) =
        match target_class {
            TargetClass::Planted => {
                let mut rejected = Vec::new();
                loop {
                    let indices: [usize; 4] =
                        std::array::from_fn(|_| rng.gen_range(0..base.points.len()));
                    let target = indices.iter().fold(BinaryPoint::Infinity, |sum, &index| {
                        curve.add(&sum, &base.points[index])
                    });
                    if target == BinaryPoint::Infinity {
                        rejected.push(indices);
                        continue;
                    }
                    break (None, Some(indices), rejected, target);
                }
            }
            TargetClass::Natural => {
                let scalar = rng.gen_range(1..modulus);
                (
                    Some(scalar),
                    None,
                    Vec::new(),
                    curve.mul(curve.generator(), &BigUint::from(scalar)),
                )
            }
            TargetClass::ProvenNegative => {
                let pairs = exact_pairs
                    .as_ref()
                    .expect("negative fixtures are small-rung only");
                assert!(
                    seed > 0 && seed < modulus,
                    "negative fixture seed is its public scalar"
                );
                let target = curve.mul(curve.generator(), &BigUint::from(seed));
                assert!(
                    exact_four_witness(&curve, &base.points, pairs, &target).is_none(),
                    "requested proven-negative scalar is decomposable"
                );
                (Some(seed), None, Vec::new(), target)
            }
            TargetClass::Scalar => {
                assert!(seed > 0 && seed < modulus);
                (
                    Some(seed),
                    None,
                    Vec::new(),
                    curve.mul(curve.generator(), &BigUint::from(seed)),
                )
            }
        };
    let planting_attempts = planted_indices
        .as_ref()
        .map(|_| rejected_identity_plantings.len() + 1);
    let BinaryPoint::Affine { x: target_x, .. } = &target else {
        panic!("fixture target must be affine");
    };
    if let Ok(path) = std::env::var("KIC_FIXTURE_PATH") {
        let coordinates = |point: &BinaryPoint| match point {
            BinaryPoint::Infinity => None,
            BinaryPoint::Affine { x, y } => Some([
                x.raw_bits().first().copied().unwrap_or(0),
                y.raw_bits().first().copied().unwrap_or(0),
            ]),
        };
        let fixture = json!({
            "schema_version":"1.0", "task_id":task_id,
            "n":n, "a":a, "b":1,
            "field_modulus_low_terms":curve.curve.irreducible.low_terms,
            "subgroup_order":curve.subgroup_order.to_u64().unwrap(),
            "cofactor":curve.cofactor.to_u64().unwrap(),
            "generator":coordinates(curve.generator()),
            "target":coordinates(&target),
            "target_class":target_class.name(), "seed":seed,
            "published_scalar_validator_label":published_scalar,
            "planted_point_indices_validator_only":planted_indices,
            "planting_attempts":planting_attempts,
            "rejected_identity_plantings_validator_only":rejected_identity_plantings,
            "factor_base_points":base.points.iter().map(coordinates).collect::<Vec<_>>(),
            "factor_base_x_codes":base.x_codes,
            "scope":"public synthetic affine fixture; labels are validation data"
        });
        std::fs::write(path, serde_json::to_string_pretty(&fixture).unwrap() + "\n").unwrap();
    }
    let reference_query_started = Instant::now();
    let expected = exact_pairs
        .as_ref()
        .map(|pairs| exact_four_witness(&curve, &base.points, pairs, &target).is_some());
    let exceptional_witness = exact_pairs
        .as_ref()
        .and_then(|pairs| exact_cancellation_witness(&curve, &base, pairs, &target));
    let exceptional_decomposable = exact_pairs.as_ref().map(|_| exceptional_witness.is_some());
    let reference_query_ms = reference_query_started.elapsed().as_secs_f64() * 1000.0;
    if target_class == TargetClass::Planted {
        assert_ne!(expected, Some(false));
    }

    let structure = FieldStructure::new(n, &curve.curve.irreducible);
    let domain_encoding =
        std::env::var("KIC_DOMAIN_ENCODING").unwrap_or_else(|_| "trie".to_owned());
    assert!(matches!(
        domain_encoding.as_str(),
        "trie" | "one_hot" | "binary_index"
    ));
    let algebra_encoding =
        std::env::var("KIC_ALGEBRA_ENCODING").unwrap_or_else(|_| "expanded".to_owned());
    let symmetry_breaking = std::env::var("KIC_SYMMETRY_BREAK").as_deref() == Ok("1");
    assert!(
        !symmetry_breaking
            || matches!(domain_encoding.as_str(), "one_hot" | "binary_index")
            || algebra_encoding == "orbit_factorized"
    );
    let pairing: usize = std::env::var("KIC_PAIRING")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(0);
    assert!(pairing < 3);
    assert!(matches!(
        algebra_encoding.as_str(),
        "expanded"
            | "factorized"
            | "rooted"
            | "pair_table"
            | "lazy_s3"
            | "orbit_factorized"
    ));
    let allow_partial_pairing =
        std::env::var("KIC_ALLOW_PARTIAL_PAIRING").as_deref() == Ok("1");
    let orbit_lazy_pair_roots =
        std::env::var("KIC_ORBIT_LAZY_PAIR_ROOTS").as_deref() == Ok("1");
    assert!(!orbit_lazy_pair_roots || algebra_encoding == "orbit_factorized");
    assert!(!orbit_lazy_pair_roots || allow_partial_pairing);
    assert!(
        !matches!(algebra_encoding.as_str(), "rooted" | "lazy_s3") || allow_partial_pairing,
        "rooted and lazy S3 arms cover only the regular nonzero-pairing branch; set KIC_ALLOW_PARTIAL_PAIRING=1"
    );
    let multiplication_encoding =
        std::env::var("KIC_MULTIPLICATION_ENCODING").unwrap_or_else(|_| "schoolbook".to_owned());
    assert!(matches!(
        multiplication_encoding.as_str(),
        "schoolbook" | "karatsuba"
    ));
    assert!(
        matches!(
            algebra_encoding.as_str(),
            "factorized" | "rooted" | "pair_table" | "lazy_s3" | "orbit_factorized"
        )
            || multiplication_encoding == "schoolbook"
    );
    assert!(
        matches!(
            algebra_encoding.as_str(),
            "factorized" | "pair_table" | "lazy_s3"
        )
            || domain_encoding != "binary_index"
    );
    assert!(algebra_encoding != "pair_table" || domain_encoding == "binary_index");
    let pair_table_direct_implications =
        std::env::var("KIC_PAIR_TABLE_IMPLICATIONS").as_deref() == Ok("1");
    let pair_table_reverse_support =
        std::env::var("KIC_PAIR_TABLE_REVERSE_SUPPORT").as_deref() == Ok("1");
    let pair_table_final_support =
        std::env::var("KIC_PAIR_TABLE_FINAL_SUPPORT").as_deref() == Ok("1");
    let pair_table_drop_final_s3 =
        std::env::var("KIC_PAIR_TABLE_DROP_FINAL_S3").as_deref() == Ok("1");
    assert!(!pair_table_reverse_support || pair_table_direct_implications);
    assert!(!pair_table_final_support || pair_table_direct_implications);
    assert!(!pair_table_drop_final_s3 || pair_table_final_support);
    assert!(algebra_encoding == "pair_table" || !pair_table_direct_implications);
    assert!(algebra_encoding == "pair_table" || !pair_table_reverse_support);
    assert!(algebra_encoding == "pair_table" || !pair_table_final_support);
    assert!(algebra_encoding == "pair_table" || !pair_table_drop_final_s3);
    let intermediate_domain_encoding =
        std::env::var("KIC_INTERMEDIATE_DOMAIN").unwrap_or_else(|_| "none".to_owned());
    assert!(matches!(
        intermediate_domain_encoding.as_str(),
        "none" | "pair_sum_trie"
    ));
    // pair_sum_trie is compact enough through the admitted n=53 rung; absolute
    // positive expansion remains capped separately at n<=23.
    assert!(intermediate_domain_encoding == "none" || n <= 53);
    let intermediate_domain_started = Instant::now();
    let intermediate_domain = (intermediate_domain_encoding == "pair_sum_trie")
        .then(|| pair_sum_x_domain(&curve, &base.points));
    let intermediate_domain_ms = intermediate_domain_started.elapsed().as_secs_f64() * 1000.0;
    assert!(algebra_encoding != "pair_table" || intermediate_domain_encoding == "none");
    assert!(algebra_encoding != "pair_table" || n <= 23);
    let pair_table_started = Instant::now();
    let pair_table = (algebra_encoding == "pair_table").then(|| pair_x_entries(&curve, &base));
    let pair_table_ms = pair_table_started.elapsed().as_secs_f64() * 1000.0;
    let encoding_started = Instant::now();
    let mut encoding = if algebra_encoding == "pair_table" {
        encode_balanced_s5_pair_table(
            &curve,
            n,
            target_x,
            &curve.curve.b,
            &structure,
            &base.x_codes,
            pair_table.as_ref().unwrap(),
            symmetry_breaking,
            pairing,
            multiplication_encoding == "karatsuba",
            pair_table_direct_implications,
            pair_table_reverse_support,
            pair_table_final_support,
            pair_table_drop_final_s3,
        )
    } else if algebra_encoding == "orbit_factorized" {
        // Intermediate u/v live at field-bit offsets 4n/5n (same as expanded
        // S5); pair_sum_trie may constrain those wires without a pair/edge table.
        let representative_x_codes: Vec<u64> = base
            .representatives
            .iter()
            .map(|point| match point {
                BinaryPoint::Affine { x, .. } => x.raw_bits().first().copied().unwrap_or(0),
                BinaryPoint::Infinity => panic!("factor-base representative must be affine"),
            })
            .collect();
        let representative_encoding =
            std::env::var("KIC_ORBIT_REP_ENCODING").unwrap_or_else(|_| "one_hot".to_owned());
        let orbit_rooted = std::env::var("KIC_ORBIT_ROOTED").as_deref() == Ok("1");
        assert!(
            !orbit_rooted || allow_partial_pairing,
            "the orbit half-trace root circuit covers only the regular branch; set KIC_ALLOW_PARTIAL_PAIRING=1"
        );
        encode_balanced_s5_frobenius_orbits(
            n,
            target_x,
            &curve.curve.b,
            &structure,
            &base.x_codes,
            &representative_x_codes,
            symmetry_breaking,
            pairing,
            multiplication_encoding == "karatsuba",
            &representative_encoding,
            orbit_rooted,
            orbit_lazy_pair_roots,
        )
    } else if algebra_encoding == "lazy_s3" {
        assert_eq!(domain_encoding, "binary_index");
        assert_eq!(intermediate_domain_encoding, "none");
        encode_balanced_s5_lazy_domain(n, &base.x_codes, symmetry_breaking, pairing)
    } else if matches!(algebra_encoding.as_str(), "factorized" | "rooted") {
        encode_balanced_s5_factorized(
            n,
            target_x,
            &curve.curve.b,
            &structure,
            &base.x_codes,
            &domain_encoding,
            symmetry_breaking,
            pairing,
            multiplication_encoding == "karatsuba",
            algebra_encoding == "rooted",
        )
    } else {
        encode_balanced_s5(
            n,
            target_x,
            &curve.curve.b,
            &structure,
            &base.x_codes,
            domain_encoding == "one_hot",
            symmetry_breaking,
            pairing,
        )
    };
    if let Some(codes) = &intermediate_domain {
        let width = n as usize;
        add_coordinate_domain(&mut encoding.solver, 4 * width, width, codes);
        add_coordinate_domain(&mut encoding.solver, 5 * width, width, codes);
    }
    let mut relative_pair_support_nogoods = json!({
        "enabled": false,
        "pair_table_entries": 0,
        "edge_selectors": 0
    });
    if algebra_encoding == "orbit_factorized"
        && std::env::var("KIC_ORBIT_PAIR_SUPPORT_NOGOODS").as_deref() == Ok("1")
    {
        let representative_x_codes: Vec<u64> = base
            .representatives
            .iter()
            .map(|point| match point {
                BinaryPoint::Affine { x, .. } => x.raw_bits().first().copied().unwrap_or(0),
                BinaryPoint::Infinity => panic!("factor-base representative must be affine"),
            })
            .collect();
        let representative_encoding =
            std::env::var("KIC_ORBIT_REP_ENCODING").unwrap_or_else(|_| "one_hot".to_owned());
        relative_pair_support_nogoods = install_relative_orbit_pair_support_nogoods(
            &mut encoding.solver,
            &curve,
            &representative_x_codes,
            pairing,
            &representative_encoding,
        );
    }
    let mut relative_pair_support_positive = json!({
        "enabled": false,
        "pair_table_entries": 0,
        "edge_selectors": 0
    });
    if algebra_encoding == "orbit_factorized"
        && std::env::var("KIC_ORBIT_PAIR_SUPPORT_POSITIVE").as_deref() == Ok("1")
    {
        let representative_x_codes: Vec<u64> = base
            .representatives
            .iter()
            .map(|point| match point {
                BinaryPoint::Affine { x, .. } => x.raw_bits().first().copied().unwrap_or(0),
                BinaryPoint::Infinity => panic!("factor-base representative must be affine"),
            })
            .collect();
        let representative_encoding =
            std::env::var("KIC_ORBIT_REP_ENCODING").unwrap_or_else(|_| "one_hot".to_owned());
        relative_pair_support_positive = install_relative_orbit_pair_support_positive(
            &mut encoding.solver,
            &curve,
            &representative_x_codes,
            pairing,
            &representative_encoding,
        );
    }
    let planted_x_root_units =
        std::env::var("KIC_PLANTED_X_ROOT_UNITS").as_deref() == Ok("1");
    let planted_chain_root_units =
        std::env::var("KIC_PLANTED_CHAIN_ROOT_UNITS").as_deref() == Ok("1");
    assert!(!planted_chain_root_units || planted_x_root_units);
    if planted_x_root_units {
        let indices = planted_indices
            .as_ref()
            .expect("KIC_PLANTED_X_ROOT_UNITS requires a planted target");
        for (summand, &point_index) in indices.iter().enumerate() {
            let BinaryPoint::Affine { x, .. } = &base.points[point_index] else {
                panic!("factor-base point must be affine");
            };
            let code = x.raw_bits().first().copied().unwrap_or(0);
            for bit in 0..n as usize {
                let variable = (summand * n as usize + bit + 1) as Lit;
                let literal = if (code >> bit) & 1 == 1 {
                    variable
                } else {
                    -variable
                };
                assert!(encoding.solver.add_clause(vec![literal]));
            }
        }
        if planted_chain_root_units {
            let pairing_indices = match pairing {
                0 => [0, 1, 2, 3],
                1 => [0, 2, 1, 3],
                2 => [0, 3, 1, 2],
                _ => unreachable!(),
            };
            let intermediate_points = [
                curve.add(
                    &base.points[indices[pairing_indices[0]]],
                    &base.points[indices[pairing_indices[1]]],
                ),
                curve.add(
                    &base.points[indices[pairing_indices[2]]],
                    &base.points[indices[pairing_indices[3]]],
                ),
            ];
            for (intermediate, point) in intermediate_points.iter().enumerate() {
                let BinaryPoint::Affine { x, .. } = point else {
                    panic!("planted pairing has an exceptional identity intermediate");
                };
                let code = x.raw_bits().first().copied().unwrap_or(0);
                for bit in 0..n as usize {
                    let variable = ((4 + intermediate) * n as usize + bit + 1) as Lit;
                    let literal = if (code >> bit) & 1 == 1 {
                        variable
                    } else {
                        -variable
                    };
                    assert!(encoding.solver.add_clause(vec![literal]));
                }
            }
        }
    }
    let pure_lazy_s3 = algebra_encoding == "lazy_s3";
    // Orbit lazy-pair-roots now install static half-trace selectors in-circuit.
    // The expensive root-theory layer is opt-in via KIC_S3_ROOT_THEORY so
    // selector-native roots can be measured without flooding the clause DB.
    let s3_root_theory = pure_lazy_s3
        || std::env::var("KIC_S3_ROOT_THEORY").as_deref() == Ok("1");
    let s3_root_theory_block_exceptional =
        pure_lazy_s3
            || std::env::var("KIC_S3_ROOT_THEORY_BLOCK_EXCEPTIONAL").as_deref() == Ok("1");
    let s3_final_theory =
        pure_lazy_s3 || std::env::var("KIC_S3_FINAL_THEORY").as_deref() == Ok("1");
    assert!(!s3_root_theory_block_exceptional || (s3_root_theory && allow_partial_pairing));
    assert!(!s3_final_theory || s3_root_theory);
    assert!(
        !s3_root_theory
            || (matches!(
                algebra_encoding.as_str(),
                "factorized" | "lazy_s3" | "orbit_factorized"
            )
                && matches!(domain_encoding.as_str(), "trie" | "binary_index")
                && backend == "internal"
                && !planted_x_root_units),
        "KIC_S3_ROOT_THEORY requires the unfixed factorized/trie internal arm"
    );
    let theory_selectors: Vec<u32> = if s3_root_theory && !pure_lazy_s3 {
        encoding.solver.add_vars(2).collect()
    } else {
        Vec::new()
    };
    if s3_root_theory {
        let mut priorities: Vec<u32> = if domain_encoding == "binary_index" {
            let index_width = encoding.selector_variables / 4;
            (0..4 * index_width)
                .map(|bit| (encoding.problem_variables + bit + 1) as u32)
                .collect()
        } else {
            (1..=(4 * n) as u32).collect()
        };
        priorities.extend(&theory_selectors);
        encoding.solver.set_branch_priority(&priorities);
    }
    let phase_restart_shots: u64 = std::env::var("KIC_PHASE_RESTART_SHOTS")
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(1)
        .max(1);
    // Polarity lever: force initial saved phases before search (pair_table stays 0).
    // KIC_PHASE_INIT=0|false → all false; 1|true → all true; unset keeps solver default.
    if let Ok(phase_init) = std::env::var("KIC_PHASE_INIT") {
        match phase_init.as_str() {
            "0" | "false" | "False" | "FALSE" => encoding.solver.set_all_saved_phases(false),
            "1" | "true" | "True" | "TRUE" => encoding.solver.set_all_saved_phases(true),
            other => panic!("unsupported KIC_PHASE_INIT={other} (expected 0/1/true/false)"),
        }
    }
    let conflicts_per_phase_shot = (conflict_budget / phase_restart_shots).max(1);
    encoding.solver.conflict_budget = conflicts_per_phase_shot;
    let mut phase_restart_shots_used = 0u64;
    let encoding_ms = encoding_started.elapsed().as_secs_f64() * 1000.0;
    let variables = encoding.solver.n_vars();
    let clauses = encoding.solver.n_clauses();
    let xor_rows = encoding.solver.n_xors();

    if backend == "validate_model" {
        let path = std::env::var("KIC_MODEL_PATH").expect("KIC_MODEL_PATH is required");
        let contents = std::fs::read_to_string(&path).unwrap();
        let model = parse_complete_external_model(&contents, variables as usize).unwrap();
        let (checked_clauses, checked_xors) =
            check_exported_assignment(&to_dimacs_xor(&encoding.solver), &model).unwrap();
        let assignment = &model[..encoding.problem_variables];
        assert!(encoding
            .equations
            .iter()
            .all(|equation| !equation.eval(assignment)));
        assert!(numeric_chain_valid(
            assignment,
            n,
            encoding.pairing,
            target_x,
            &curve.curve.b,
            &curve,
        ));
        let width = n as usize;
        let codes: [u64; 4] =
            std::array::from_fn(|index| decode_code(&model, index * width, width));
        assert!(codes
            .iter()
            .all(|code| base.x_codes.binary_search(code).is_ok()));
        assert!(!symmetry_breaking || codes.windows(2).all(|pair| pair[0] <= pair[1]));
        let intermediate_codes = [
            decode_code(&model, 4 * width, width),
            decode_code(&model, 5 * width, width),
        ];
        let intermediate_domain_valid = intermediate_domain.as_ref().map(|domain| {
            intermediate_codes
                .iter()
                .all(|code| domain.binary_search(code).is_ok())
        });
        assert_ne!(intermediate_domain_valid, Some(false));
        let lifted = lift_x_tuple(&curve, &base, &codes, &target);
        assert!(lifted.is_some());
        println!(
            "{}",
            json!({
                "schema_version":"1.0",
                "task_id":task_id,
                "kind":"balanced_s5_external_model_validation",
                "n":n,
                "a":a,
                "target_class":target_class.name(),
                "seed":seed,
                "expected_decomposable":expected,
                "planted_point_indices_validator_only":planted_indices,
                "planting_attempts":planting_attempts,
                "rejected_identity_plantings_validator_only":rejected_identity_plantings,
                "exceptional_decomposable":exceptional_decomposable,
                "verified_exceptional_point_indices":exceptional_witness,
                "model_path":path,
                "problem_assignment_complete":true,
                "full_assignment_complete":true,
                "all_emitted_constraints_valid":true,
                "checked_cnf_clauses":checked_clauses,
                "checked_native_xor_rows":checked_xors,
                "all_three_s3_systems_valid":true,
                "algebra_encoding":encoding.algebra_encoding,
                "multiplication_encoding":encoding.multiplication_encoding,
                "pair_table_entries":encoding.pair_table_entries,
                "pair_selector_variables":encoding.pair_selector_variables,
                "pair_table_propagation":encoding.pair_table_propagation,
                "final_support_clauses":encoding.final_support_clauses,
                "final_compatible_selector_pairs":encoding.final_compatible_selector_pairs,
                "final_s3_circuit_installed":encoding.final_s3_circuit_installed,
                "pair_table_ms":pair_table_ms,
                "intermediate_domain_encoding":intermediate_domain_encoding,
                "intermediate_domain_valid":intermediate_domain_valid,
                "intermediate_x_tuple":intermediate_codes,
                "all_four_x_in_point_defined_domain":true,
                "verified_group_decomposition":true,
                "x_tuple":codes,
                "point_indices":lifted,
                "scope":"public synthetic CryptoMiniSat model validation; no external point or key recovery"
            })
        );
        return;
    }

    if backend == "emit_xor" {
        let path = std::env::var("KIC_DIMACS_PATH").expect("KIC_DIMACS_PATH is required");
        let dimacs = to_dimacs_xor(&encoding.solver);
        std::fs::write(&path, dimacs.as_bytes()).unwrap();
        println!(
            "{}",
            json!({
                "schema_version":"1.0",
                "task_id":task_id,
                "kind":"balanced_s5_extended_dimacs",
                "n":n,
                "a":a,
                "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
                "target_class":target_class.name(),
                "seed":seed,
                "expected_decomposable":expected,
                "planted_point_indices_validator_only":planted_indices,
                "planting_attempts":planting_attempts,
                "rejected_identity_plantings_validator_only":rejected_identity_plantings,
                "exceptional_decomposable":exceptional_decomposable,
                "verified_exceptional_point_indices":exceptional_witness,
                "problem_variables":encoding.problem_variables,
                "monomial_auxiliaries":encoding.monomials,
                "nonlinear_and_auxiliaries":encoding.monomials,
                "selector_variables":encoding.selector_variables,
                "cardinality_auxiliaries":encoding.cardinality_auxiliaries,
                "domain_encoding":encoding.domain_encoding,
                "symmetry_breaking":encoding.symmetry_breaking,
                "planted_x_root_units":planted_x_root_units,
                "planted_chain_root_units":planted_chain_root_units,
                "pairing":encoding.pairing,
                "algebra_encoding":encoding.algebra_encoding,
                "multiplication_encoding":encoding.multiplication_encoding,
                "pair_table_entries":encoding.pair_table_entries,
                "pair_selector_variables":encoding.pair_selector_variables,
                "pair_table_propagation":encoding.pair_table_propagation,
                "final_support_clauses":encoding.final_support_clauses,
                "final_compatible_selector_pairs":encoding.final_compatible_selector_pairs,
                "final_s3_circuit_installed":encoding.final_s3_circuit_installed,
                "pair_table_ms":pair_table_ms,
                "intermediate_domain_encoding":intermediate_domain_encoding,
                "intermediate_domain_x_coordinates":intermediate_domain.as_ref().map(Vec::len),
                "intermediate_domain_ms":intermediate_domain_ms,
                "variables":variables,
                "ordinary_clauses":clauses,
                "native_xor_rows":xor_rows,
                "factor_base_points":base.points.len(),
                "factor_base_x_coordinates":base.x_codes.len(),
                "orbit_columns":base.orbit_columns,
                "base_ms":base_ms,
                "factor_base_input_path":&factor_base_input_path,
                "factor_base_input_hash":&factor_base_input_hash,
                "factor_base_input_blake3":&factor_base_input_blake3,
                "reference_pair_index_ms":reference_pair_index_ms,
                "reference_query_ms":reference_query_ms,
                "encoding_ms":encoding_ms,
                "dimacs_bytes":dimacs.len(),
                "dimacs_path":path,
                "scope":"public synthetic balanced-S5 export; no external point or key recovery"
            })
        );
        return;
    }
    if backend == "stats" {
        println!(
            "{}",
            json!({
                "schema_version":"1.0",
                "task_id":task_id,
                "kind":"balanced_s5_static_encoding",
                "n":n,
                "a":a,
                "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
                "target_class":target_class.name(),
                "seed":seed,
                "planted_point_indices_validator_only":planted_indices,
                "planting_attempts":planting_attempts,
                "rejected_identity_plantings_validator_only":rejected_identity_plantings,
                "problem_variables":encoding.problem_variables,
                "monomial_auxiliaries":encoding.monomials,
                "nonlinear_and_auxiliaries":encoding.monomials,
                "selector_variables":encoding.selector_variables,
                "cardinality_auxiliaries":encoding.cardinality_auxiliaries,
                "domain_encoding":encoding.domain_encoding,
                "symmetry_breaking":encoding.symmetry_breaking,
                "planted_x_root_units":planted_x_root_units,
                "planted_chain_root_units":planted_chain_root_units,
                "pairing":encoding.pairing,
                "algebra_encoding":encoding.algebra_encoding,
                "multiplication_encoding":encoding.multiplication_encoding,
                "pair_table_entries":encoding.pair_table_entries,
                "pair_selector_variables":encoding.pair_selector_variables,
                "pair_table_propagation":encoding.pair_table_propagation,
                "final_support_clauses":encoding.final_support_clauses,
                "final_compatible_selector_pairs":encoding.final_compatible_selector_pairs,
                "final_s3_circuit_installed":encoding.final_s3_circuit_installed,
                "pair_table_ms":pair_table_ms,
                "intermediate_domain_encoding":intermediate_domain_encoding,
                "intermediate_domain_x_coordinates":intermediate_domain.as_ref().map(Vec::len),
                "intermediate_domain_ms":intermediate_domain_ms,
                "variables":variables,
                "ordinary_clauses":clauses,
                "native_xor_rows":xor_rows,
                "factor_base_points":base.points.len(),
                "factor_base_x_coordinates":base.x_codes.len(),
                "orbit_columns":base.orbit_columns,
                "scanned_x":base.scanned_x,
                "base_ms":base_ms,
                "factor_base_input_path":&factor_base_input_path,
                "factor_base_input_hash":&factor_base_input_hash,
                "factor_base_input_blake3":&factor_base_input_blake3,
                "encoding_ms":encoding_ms,
                "scope":"public synthetic balanced-S5 static measurement; no external point or key recovery"
            })
        );
        return;
    }

    let direct_set =
        (n <= 11).then(|| direct_valid_x_tuples(&curve, &base, &target, symmetry_breaking));
    let exceptional_set =
        (n <= 11).then(|| direct_exceptional_x_tuples(&curve, &base, &target, symmetry_breaking));
    let solve_started = Instant::now();
    let mut valid_x_tuples = BTreeSet::new();
    let mut models = 0usize;
    let mut invalid_lifts = 0usize;
    let pairing_indices = match pairing {
        0 => [0, 1, 2, 3],
        1 => [0, 2, 1, 3],
        2 => [0, 3, 1, 2],
        _ => unreachable!(),
    };
    let theory_index_width = if domain_encoding == "binary_index" {
        encoding.selector_variables / 4
    } else {
        0
    };
    let trigger_variables: Vec<u32> = [pairing_indices[0], pairing_indices[1]]
        .into_iter()
        .flat_map(|summand| {
            if theory_index_width == 0 {
                (0..n as usize)
                    .map(|bit| (summand * n as usize + bit + 1) as u32)
                    .collect::<Vec<_>>()
            } else {
                (0..theory_index_width)
                    .map(|bit| {
                        (encoding.problem_variables + summand * theory_index_width + bit + 1)
                            as u32
                    })
                    .collect::<Vec<_>>()
            }
        })
        .collect();
    let theory_specs = if s3_root_theory && !pure_lazy_s3 {
        vec![
            (
                pairing_indices[0] * n as usize,
                pairing_indices[1] * n as usize,
                4 * n as usize,
                theory_selectors[0],
            ),
            (
                pairing_indices[2] * n as usize,
                pairing_indices[3] * n as usize,
                5 * n as usize,
                theory_selectors[1],
            ),
        ]
    } else {
        Vec::new()
    };
    let mut theory_seen = [HashSet::new(), HashSet::new()];
    let mut final_theory_seen = HashSet::new();
    let mut theory_patterns = 0usize;
    let mut theory_clauses = 0usize;
    let mut theory_exceptional_patterns = 0usize;
    let mut final_theory_patterns = 0usize;
    let mut final_theory_infeasible_patterns = 0usize;
    let mut final_theory_compatible_patterns = 0usize;
    let mut final_theory_clauses = 0usize;
    let mut theory = |assignment: &[Option<bool>]| {
        let mut learned = Vec::new();
        if pure_lazy_s3 {
            let mut roots_by_side = [None, None];
            let mut endpoint_codes = [0u64; 4];
            let mut all_endpoints_assigned = true;
            for side in 0..2 {
                let summands = [pairing_indices[2 * side], pairing_indices[2 * side + 1]];
                let offsets = summands.map(|summand| summand * theory_index_width);
                if offsets.iter().any(|&offset| {
                    !(0..theory_index_width).all(|bit| assignment[offset + bit].is_some())
                }) {
                    all_endpoints_assigned = false;
                    continue;
                }
                let indices = offsets.map(|offset| {
                    decode_partial_code(assignment, offset, theory_index_width) as usize
                });
                assert!(indices.iter().all(|&index| index < base.x_codes.len()));
                let left = base.x_codes[indices[0]];
                let right = base.x_codes[indices[1]];
                endpoint_codes[summands[0]] = left;
                endpoint_codes[summands[1]] = right;
                let roots = regular_s3_x_roots(&curve, left, right);
                roots_by_side[side] = roots;
                if theory_seen[side].insert((left, right)) {
                    theory_patterns += 1;
                    if roots.is_none() {
                        theory_exceptional_patterns += 1;
                        let mut guard = Vec::with_capacity(2 * theory_index_width);
                        for offset in offsets {
                            for bit in 0..theory_index_width {
                                let variable = (offset + bit + 1) as Lit;
                                guard.push(if assignment[offset + bit].unwrap() {
                                    -variable
                                } else {
                                    variable
                                });
                            }
                        }
                        learned.push(guard);
                    }
                }
            }
            if all_endpoints_assigned {
                if let (Some(left_roots), Some(right_roots)) =
                    (roots_by_side[0], roots_by_side[1])
                {
                    if final_theory_seen.insert(endpoint_codes) {
                        final_theory_patterns += 1;
                        let compatible = (0..2).any(|left_choice| {
                            (0..2).any(|right_choice| {
                                let left = F2mElement::from_biguint(
                                    &BigUint::from(left_roots[left_choice]),
                                    n,
                                );
                                let right = F2mElement::from_biguint(
                                    &BigUint::from(right_roots[right_choice]),
                                    n,
                                );
                                binary_semaev_s3(
                                    &left,
                                    &right,
                                    target_x,
                                    &curve.curve.b,
                                    &curve.curve.irreducible,
                                )
                                .is_zero()
                            })
                        });
                        if compatible {
                            final_theory_compatible_patterns += 1;
                        } else {
                            final_theory_infeasible_patterns += 1;
                            let mut guard = Vec::with_capacity(4 * theory_index_width);
                            for summand in 0..4 {
                                let offset = summand * theory_index_width;
                                for bit in 0..theory_index_width {
                                    let variable = (offset + bit + 1) as Lit;
                                    guard.push(if assignment[offset + bit].unwrap() {
                                        -variable
                                    } else {
                                        variable
                                    });
                                }
                            }
                            learned.push(guard);
                            final_theory_clauses += 1;
                        }
                    }
                }
            }
            if learned.is_empty() {
                return None;
            }
            theory_clauses += learned.len();
            return Some(learned);
        }
        let mut roots_by_side = [None, None];
        let mut endpoint_codes = [0u64; 4];
        let mut all_endpoints_assigned = true;
        for (side, &(left_offset, right_offset, third_offset, selector))
            in theory_specs.iter().enumerate()
        {
            if !(0..n as usize).all(|bit| {
                assignment[left_offset + bit].is_some()
                    && assignment[right_offset + bit].is_some()
            }) {
                all_endpoints_assigned = false;
                continue;
            }
            let left = decode_partial_code(assignment, left_offset, n as usize);
            let right = decode_partial_code(assignment, right_offset, n as usize);
            endpoint_codes[pairing_indices[2 * side]] = left;
            endpoint_codes[pairing_indices[2 * side + 1]] = right;
            let roots = regular_s3_x_roots(&curve, left, right);
            roots_by_side[side] = roots;
            if !theory_seen[side].insert((left, right)) {
                continue;
            }
            theory_patterns += 1;
            let mut guard = Vec::new();
            for summand_offset in [left_offset, right_offset] {
                let (guard_offset, guard_width) = if theory_index_width == 0 {
                    (summand_offset, n as usize)
                } else {
                    (
                        encoding.problem_variables
                            + (summand_offset / n as usize) * theory_index_width,
                        theory_index_width,
                    )
                };
                for bit in 0..guard_width {
                    let variable = (guard_offset + bit + 1) as Lit;
                    guard.push(if assignment[guard_offset + bit].unwrap() {
                        -variable
                    } else {
                        variable
                    });
                }
            }
            let Some(roots) = roots else {
                theory_exceptional_patterns += 1;
                if s3_root_theory_block_exceptional {
                    learned.push(guard);
                }
                continue;
            };
            learned.extend(guarded_s3_root_clauses(
                &guard,
                third_offset,
                selector,
                roots,
                n as usize,
            ));
        }
        if s3_final_theory && all_endpoints_assigned {
            if let (Some(left_roots), Some(right_roots)) = (roots_by_side[0], roots_by_side[1]) {
                if final_theory_seen.insert(endpoint_codes) {
                    final_theory_patterns += 1;
                    let mut guard = Vec::with_capacity(4 * theory_index_width.max(n as usize));
                    for summand in 0..4 {
                        let (guard_offset, guard_width) = if theory_index_width == 0 {
                            (summand * n as usize, n as usize)
                        } else {
                            (
                                encoding.problem_variables + summand * theory_index_width,
                                theory_index_width,
                            )
                        };
                        for bit in 0..guard_width {
                            let variable = (guard_offset + bit + 1) as Lit;
                            guard.push(if assignment[guard_offset + bit].unwrap() {
                                -variable
                            } else {
                                variable
                            });
                        }
                    }
                    let mut compatible = [[false; 2]; 2];
                    for left_choice in 0..2 {
                        for right_choice in 0..2 {
                            let left = F2mElement::from_biguint(
                                &BigUint::from(left_roots[left_choice]),
                                n,
                            );
                            let right = F2mElement::from_biguint(
                                &BigUint::from(right_roots[right_choice]),
                                n,
                            );
                            compatible[left_choice][right_choice] = binary_semaev_s3(
                                &left,
                                &right,
                                target_x,
                                &curve.curve.b,
                                &curve.curve.irreducible,
                            )
                            .is_zero();
                        }
                    }
                    if compatible.iter().flatten().all(|&entry| !entry) {
                        final_theory_infeasible_patterns += 1;
                        learned.push(guard);
                        final_theory_clauses += 1;
                    } else {
                        for left_choice in 0..2 {
                            for right_choice in 0..2 {
                                if compatible[left_choice][right_choice] {
                                    continue;
                                }
                                let mut clause = guard.clone();
                                clause.push(if left_choice == 0 {
                                    theory_selectors[0] as Lit
                                } else {
                                    -(theory_selectors[0] as Lit)
                                });
                                clause.push(if right_choice == 0 {
                                    theory_selectors[1] as Lit
                                } else {
                                    -(theory_selectors[1] as Lit)
                                });
                                learned.push(clause);
                                final_theory_clauses += 1;
                            }
                        }
                    }
                }
            }
        }
        if learned.is_empty() {
            None
        } else {
            theory_clauses += learned.len();
            Some(learned)
        }
    };
    let outcome = loop {
        let solve_result = if s3_root_theory {
            encoding
                .solver
                .solve_with_lazy_clauses(&trigger_variables, &mut theory)
        } else {
            encoding.solver.solve()
        };
        match solve_result {
            SolveResult::Sat => {
                models += 1;
                let model = encoding.solver.model();
                let assignment = &model[..encoding.problem_variables];
                check_exported_assignment(&to_dimacs_xor(&encoding.solver), &model)
                    .expect("internal SAT model must satisfy every installed CNF/XOR constraint");
                assert!(encoding
                    .equations
                    .iter()
                    .all(|equation| !equation.eval(assignment)));
                assert!(
                    pure_lazy_s3
                        || numeric_chain_valid(
                            assignment,
                            n,
                            encoding.pairing,
                            target_x,
                            &curve.curve.b,
                            &curve,
                        )
                );
                let width = n as usize;
                let codes: [u64; 4] = if pure_lazy_s3 {
                    std::array::from_fn(|summand| {
                        let index = decode_code(
                            &model,
                            encoding.problem_variables + summand * theory_index_width,
                            theory_index_width,
                        ) as usize;
                        base.x_codes[index]
                    })
                } else {
                    std::array::from_fn(|index| decode_code(&model, index * width, width))
                };
                assert!(codes
                    .iter()
                    .all(|code| base.x_codes.binary_search(code).is_ok()));
                if let Some(domain) = &intermediate_domain {
                    for index in 4..6 {
                        let code = decode_code(&model, index * width, width);
                        assert!(domain.binary_search(&code).is_ok());
                    }
                }
                let lifted = lift_x_tuple(&curve, &base, &codes, &target);
                assert!(!pure_lazy_s3 || lifted.is_some());
                if lifted.is_some() {
                    valid_x_tuples.insert(codes);
                } else {
                    invalid_lifts += 1;
                }
                if models >= model_cap {
                    break SolveResult::Unknown;
                }
                encoding.solver.reset_search();
                let (blocking_offset, blocking_width) = if pure_lazy_s3 {
                    (encoding.problem_variables, 4 * theory_index_width)
                } else {
                    (0, 4 * width)
                };
                let blocking: Vec<Lit> = (0..blocking_width)
                    .map(|index| {
                        let variable = (blocking_offset + index + 1) as Lit;
                        if model[blocking_offset + index] {
                            -variable
                        } else {
                            variable
                        }
                    })
                    .collect();
                // A root conflict on the last blocking clause is successful
                // exhaustion of the projected model set, not an encoding error.
                if !encoding.solver.add_clause(blocking) {
                    break SolveResult::Unsat;
                }
            }
            SolveResult::Unknown
                if phase_restart_shots_used + 1 < phase_restart_shots && models == 0 =>
            {
                phase_restart_shots_used += 1;
                encoding.solver.reset_search();
                encoding
                    .solver
                    .scramble_saved_phases(seed ^ (0x9E37_79B9_7F4A_7C15 ^ phase_restart_shots_used));
                encoding.solver.conflict_budget =
                    conflicts_per_phase_shot.saturating_mul(phase_restart_shots_used + 1);
                continue;
            }
            result => break result,
        }
    };
    phase_restart_shots_used += 1;
    drop(theory);
    let solve_ms = solve_started.elapsed().as_secs_f64() * 1000.0;
    let exhaustive_match = direct_set
        .as_ref()
        .and_then(|direct| (outcome == SolveResult::Unsat).then(|| *direct == valid_x_tuples));
    let sat_subset_of_direct = direct_set
        .as_ref()
        .map(|direct| valid_x_tuples.is_subset(direct));
    if allow_partial_pairing {
        assert_ne!(sat_subset_of_direct, Some(false));
    } else if let Some(false) = exhaustive_match {
        let direct = direct_set.as_ref().unwrap();
        eprintln!(
            "balanced-S5 mismatch: direct={}, sat={}, direct_only={:?}, sat_only={:?}",
            direct.len(),
            valid_x_tuples.len(),
            direct.difference(&valid_x_tuples).next(),
            valid_x_tuples.difference(direct).next(),
        );
        panic!("balanced-S5 SAT model set disagrees with direct group enumeration");
    }
    if let Ok(path) = std::env::var("KIC_MODELS_PATH") {
        let serialized = valid_x_tuples
            .iter()
            .map(|tuple| serde_json::to_string(tuple).unwrap())
            .collect::<Vec<_>>()
            .join("\n");
        std::fs::write(path, serialized + "\n").unwrap();
    }
    if let (Some(direct), Ok(path)) = (&direct_set, std::env::var("KIC_DIRECT_PATH")) {
        let serialized = direct
            .iter()
            .map(|tuple| serde_json::to_string(tuple).unwrap())
            .collect::<Vec<_>>()
            .join("\n");
        std::fs::write(path, serialized + "\n").unwrap();
    }
    if let (Some(exceptional), Ok(path)) = (&exceptional_set, std::env::var("KIC_EXCEPTIONAL_PATH"))
    {
        let serialized = exceptional
            .iter()
            .map(|tuple| serde_json::to_string(tuple).unwrap())
            .collect::<Vec<_>>()
            .join("\n");
        std::fs::write(path, serialized + "\n").unwrap();
    }
    if !valid_x_tuples.is_empty() {
        assert_ne!(expected, Some(false));
    } else if !allow_partial_pairing && outcome == SolveResult::Unsat {
        assert_ne!(expected, Some(true));
    }
    let decomposition_verdict = if !valid_x_tuples.is_empty() {
        "SAT"
    } else {
        match outcome {
            SolveResult::Unsat => "UNSAT",
            SolveResult::Sat | SolveResult::Unknown => "UNKNOWN",
        }
    };
    println!(
        "{}",
        json!({
            "schema_version":"1.0",
            "task_id":task_id,
            "kind":"balanced_s5_native_xor_observation",
            "evidence_class":if outcome==SolveResult::Unknown {"censored_operational_observation"} else {"measured_solver_observation"},
            "n":n,
            "a":a,
            "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
            "target_class":target_class.name(),
            "seed":seed,
            "published_scalar_validator_label":published_scalar,
            "expected_decomposable":expected,
            "planted_point_indices_validator_only":planted_indices,
            "planting_attempts":planting_attempts,
            "rejected_identity_plantings_validator_only":rejected_identity_plantings,
            "exceptional_decomposable":exceptional_decomposable,
            "verified_exceptional_point_indices":exceptional_witness,
            "verdict_scope":"single_affine_pairing",
            "decomposition_verdict":decomposition_verdict,
            "terminal_search_outcome":match outcome { SolveResult::Sat=>"SAT_MODEL", SolveResult::Unsat=>"UNSAT_AFTER_BLOCKING", SolveResult::Unknown=>"UNKNOWN" },
            "problem_variables":encoding.problem_variables,
            "monomial_auxiliaries":encoding.monomials,
            "nonlinear_and_auxiliaries":encoding.monomials,
            "selector_variables":encoding.selector_variables,
            "cardinality_auxiliaries":encoding.cardinality_auxiliaries,
            "domain_encoding":encoding.domain_encoding,
            "symmetry_breaking":encoding.symmetry_breaking,
            "planted_x_root_units":planted_x_root_units,
            "planted_chain_root_units":planted_chain_root_units,
            "pairing":encoding.pairing,
            "algebra_encoding":encoding.algebra_encoding,
            "multiplication_encoding":encoding.multiplication_encoding,
            "pair_table_entries":encoding.pair_table_entries,
            "pair_selector_variables":encoding.pair_selector_variables,
            "pair_table_propagation":encoding.pair_table_propagation,
            "relative_pair_support_nogoods":relative_pair_support_nogoods,
            "relative_pair_support_positive":relative_pair_support_positive,
            "final_support_clauses":encoding.final_support_clauses,
            "final_compatible_selector_pairs":encoding.final_compatible_selector_pairs,
            "final_s3_circuit_installed":encoding.final_s3_circuit_installed,
            "pair_table_ms":pair_table_ms,
            "intermediate_domain_encoding":intermediate_domain_encoding,
            "intermediate_domain_x_coordinates":intermediate_domain.as_ref().map(Vec::len),
            "intermediate_domain_ms":intermediate_domain_ms,
            "partial_pairing_mode":allow_partial_pairing,
            "variables":variables,
            "ordinary_clauses":clauses,
            "native_xor_rows":xor_rows,
            "factor_base_points":base.points.len(),
            "factor_base_x_coordinates":base.x_codes.len(),
            "orbit_columns":base.orbit_columns,
            "models_examined":models,
            "valid_x_tuples":valid_x_tuples.len(),
            "invalid_group_lifts":invalid_lifts,
            "direct_valid_x_tuples":direct_set.as_ref().map(BTreeSet::len),
            "direct_exceptional_x_tuples":exceptional_set.as_ref().map(BTreeSet::len),
            "exhaustive_model_set_match":exhaustive_match,
            "sat_subset_of_direct":sat_subset_of_direct,
            "conflicts":encoding.solver.conflicts(),
            "phase_restart_shots":phase_restart_shots,
            "phase_restart_shots_used":phase_restart_shots_used,
            "conflicts_per_phase_shot":conflicts_per_phase_shot,
                "s3_root_theory":s3_root_theory,
                "s3_root_theory_block_exceptional":s3_root_theory_block_exceptional,
                "s3_final_theory":s3_final_theory,
                "s3_root_theory_patterns":theory_patterns,
                "s3_root_theory_clauses":theory_clauses,
                "s3_root_theory_exceptional_patterns":theory_exceptional_patterns,
                "s3_final_theory_patterns":final_theory_patterns,
                "s3_final_theory_infeasible_patterns":final_theory_infeasible_patterns,
                "s3_final_theory_compatible_patterns":final_theory_compatible_patterns,
                "s3_final_theory_clauses":final_theory_clauses,
            "base_ms":base_ms,
            "factor_base_input_path":&factor_base_input_path,
            "factor_base_input_hash":&factor_base_input_hash,
            "factor_base_input_blake3":&factor_base_input_blake3,
            "encoding_ms":encoding_ms,
            "solve_ms":solve_ms,
            "scope":"public synthetic balanced-S5 correctness control; no external point or key recovery"
        })
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn projected_regular_x_models(
        mut encoding: S5Encoding,
        curve: &KoblitzCurve,
        base: &PointBase,
        target: &BinaryPoint,
        target_x: &F2mElement,
    ) -> BTreeSet<[u64; 4]> {
        let width = curve.n as usize;
        let mut result = BTreeSet::new();
        loop {
            match encoding.solver.solve() {
                SolveResult::Sat => {
                    let model = encoding.solver.model();
                    let assignment = &model[..encoding.problem_variables];
                    assert!(numeric_chain_valid(
                        assignment,
                        curve.n,
                        encoding.pairing,
                        target_x,
                        &curve.curve.b,
                        curve,
                    ));
                    let codes: [u64; 4] =
                        std::array::from_fn(|index| decode_code(&model, index * width, width));
                    assert!(codes.windows(2).all(|window| window[0] <= window[1]));
                    assert!(codes
                        .iter()
                        .all(|code| base.x_codes.binary_search(code).is_ok()));
                    assert!(lift_x_tuple(curve, base, &codes, target).is_some());
                    result.insert(codes);
                    encoding.solver.reset_search();
                    let blocking: Vec<Lit> = (0..4 * width)
                        .map(|index| {
                            let variable = (index + 1) as Lit;
                            if model[index] {
                                -variable
                            } else {
                                variable
                            }
                        })
                        .collect();
                    if !encoding.solver.add_clause(blocking) {
                        break;
                    }
                }
                SolveResult::Unsat => break,
                SolveResult::Unknown => panic!("unbounded n=7 equivalence solve was censored"),
            }
        }
        result
    }

    #[test]
    fn rejects_missing_contradictory_and_tampered_auxiliary_assignments() {
        let dimacs = "p cnf 3 3\n-1 -2 3 0\n1 -3 0\n2 -3 0\nx -1 2 0\n";
        let valid = parse_complete_external_model("s SATISFIABLE\nv 1 2 3 0\n", 3).unwrap();
        assert_eq!(check_exported_assignment(dimacs, &valid), Ok((3, 1)));
        assert!(parse_complete_external_model("s SATISFIABLE\nv 1 2 0\n", 3).is_err());
        assert!(parse_complete_external_model("s SATISFIABLE\nv 1 2 3 -3 0\n", 3).is_err());
        let forged = parse_complete_external_model("s SATISFIABLE\nv 1 2 -3 0\n", 3).unwrap();
        assert_eq!(&forged[..2], &valid[..2]);
        assert!(check_exported_assignment(dimacs, &forged).is_err());
        assert!(check_exported_assignment("p cnf 2 0\nx -1 2 0\n", &[true, false]).is_err());
    }

    #[test]
    fn comparator_preserves_equal_and_strict_order_cases() {
        for left in 0..8 {
            for right in 0..8 {
                let mut builder = CircuitBuilder::new(6, false);
                builder.constrain_unsigned_less_equal(&[1, 2, 3], &[4, 5, 6]);
                let mut solver = builder.finish();
                for bit in 0..3 {
                    let a = (bit + 1) as Lit;
                    let b = (bit + 4) as Lit;
                    solver.add_clause(vec![if (left >> bit) & 1 == 1 { a } else { -a }]);
                    solver.add_clause(vec![if (right >> bit) & 1 == 1 { b } else { -b }]);
                }
                assert_eq!(
                    solver.solve(),
                    if left <= right {
                        SolveResult::Sat
                    } else {
                        SolveResult::Unsat
                    }
                );
            }
        }
    }

    #[test]
    fn pair_table_equals_all_numeric_s3_roots_over_small_field() {
        let curve = KoblitzCurve::new(1, 7).unwrap();
        let base = point_defined_base(&curve, 1);
        let entries: BTreeSet<_> = pair_x_entries(&curve, &base).into_iter().collect();
        let mut direct = BTreeSet::new();
        for left in 0..base.x_codes.len() {
            for right in left..base.x_codes.len() {
                let x = F2mElement::from_biguint(&BigUint::from(base.x_codes[left]), curve.n);
                let y = F2mElement::from_biguint(&BigUint::from(base.x_codes[right]), curve.n);
                for sum_code in 0..(1u64 << curve.n) {
                    let z = F2mElement::from_biguint(&BigUint::from(sum_code), curve.n);
                    if binary_semaev_s3(&x, &y, &z, &curve.curve.b, &curve.curve.irreducible)
                        .is_zero()
                    {
                        direct.insert(PairXEntry {
                            left_index: left,
                            right_index: right,
                            sum_code,
                        });
                    }
                }
            }
        }
        assert!(!direct.is_empty());
        assert_eq!(entries, direct);
    }

    #[test]
    fn rational_final_support_equals_s3_on_the_pair_table_domain() {
        let curve = KoblitzCurve::new(1, 7).unwrap();
        let base = point_defined_base(&curve, 1);
        let entries = pair_x_entries(&curve, &base);
        let pair_codes: BTreeSet<_> = entries.iter().map(|entry| entry.sum_code).collect();
        let mut target_codes = BTreeSet::new();
        for scalar in 1..curve.subgroup_order.to_u64().unwrap() {
            let BinaryPoint::Affine { x, .. } =
                curve.mul(curve.generator(), &BigUint::from(scalar))
            else {
                unreachable!();
            };
            target_codes.insert(x.raw_bits().first().copied().unwrap_or(0));
        }
        for target_code in target_codes {
            let target_x = F2mElement::from_biguint(&BigUint::from(target_code), curve.n);
            let compatible = final_compatible_x_codes(&curve, &target_x, &entries);
            for &left_code in &pair_codes {
                let left = F2mElement::from_biguint(&BigUint::from(left_code), curve.n);
                for &right_code in &pair_codes {
                    let right = F2mElement::from_biguint(&BigUint::from(right_code), curve.n);
                    let expected = binary_semaev_s3(
                        &left,
                        &right,
                        &target_x,
                        &curve.curve.b,
                        &curve.curve.irreducible,
                    )
                    .is_zero();
                    assert_eq!(
                        compatible
                            .get(&left_code)
                            .is_some_and(|codes| codes.contains(&right_code)),
                        expected,
                        "target={target_code} left={left_code} right={right_code}"
                    );
                }
            }
        }
    }

    #[test]
    fn target_edge_selector_is_exhaustively_equivalent_at_n7() {
        let curve = KoblitzCurve::new(1, 7).unwrap();
        let base = point_defined_base(&curve, 1);
        let entries = pair_x_entries(&curve, &base);
        let structure = FieldStructure::new(curve.n, &curve.curve.irreducible);
        let mut targets = BTreeMap::new();
        for scalar in 1..curve.subgroup_order.to_u64().unwrap() {
            let target = curve.mul(curve.generator(), &BigUint::from(scalar));
            let BinaryPoint::Affine { x, .. } = &target else {
                unreachable!();
            };
            targets
                .entry(x.raw_bits().first().copied().unwrap_or(0))
                .or_insert(target);
        }
        assert!(!targets.is_empty());
        for (target_code, target) in targets {
            let BinaryPoint::Affine { x: target_x, .. } = &target else {
                unreachable!();
            };
            let direct = direct_valid_x_tuples(&curve, &base, &target, true);
            let exceptional = direct_exceptional_x_tuples(&curve, &base, &target, true);
            let mut all_edge_models = BTreeSet::new();
            let mut all_old_models = BTreeSet::new();
            for pairing in 0..3 {
                let first_edges = target_compatible_pair_edges(&curve, target_x, &entries, pairing);
                let second_edges =
                    target_compatible_pair_edges(&curve, target_x, &entries, pairing);
                assert_eq!(
                    first_edges, second_edges,
                    "target={target_code} pairing={pairing}"
                );

                let edge_encoding = encode_balanced_s5_target_edge_selectors(
                    &curve,
                    curve.n,
                    target_x,
                    &base.x_codes,
                    &entries,
                    true,
                    pairing,
                );
                assert!(!edge_encoding.final_s3_circuit_installed);
                assert_eq!(
                    edge_encoding.globally_sorted_compatible_pair_edges,
                    first_edges.1.len()
                );
                let edge_models =
                    projected_regular_x_models(edge_encoding, &curve, &base, &target, target_x);
                let old_encoding = encode_balanced_s5_pair_table(
                    &curve,
                    curve.n,
                    target_x,
                    &curve.curve.b,
                    &structure,
                    &base.x_codes,
                    &entries,
                    true,
                    pairing,
                    false,
                    true,
                    false,
                    true,
                    false,
                );
                assert!(old_encoding.final_s3_circuit_installed);
                let old_models =
                    projected_regular_x_models(old_encoding, &curve, &base, &target, target_x);
                assert_eq!(
                    edge_models, old_models,
                    "target={target_code} pairing={pairing}"
                );
                all_edge_models.extend(edge_models);
                all_old_models.extend(old_models);
            }
            assert_eq!(all_edge_models, all_old_models, "target={target_code}");
            let mut regular_or_exceptional = all_edge_models;
            regular_or_exceptional.extend(exceptional);
            assert_eq!(
                regular_or_exceptional, direct,
                "target={target_code}: regular pair joins plus explicit cancellation must equal direct group enumeration"
            );
        }
    }

    #[test]
    fn empty_target_edge_domain_retains_exported_root_unsat() {
        let curve = KoblitzCurve::new(1, 7).unwrap();
        let base = point_defined_base(&curve, 1);
        let BinaryPoint::Affine { x: target_x, .. } = curve.generator() else {
            unreachable!();
        };
        let mut encoding = encode_balanced_s5_target_edge_selectors(
            &curve,
            curve.n,
            target_x,
            &base.x_codes,
            &[],
            true,
            0,
        );
        assert!(encoding.edge_selector_domain_empty);
        assert_eq!(encoding.target_compatible_pair_edges, 0);
        assert_eq!(encoding.globally_sorted_compatible_pair_edges, 0);
        let dimacs = to_dimacs_xor(&encoding.solver);
        assert!(dimacs.lines().any(|line| line.trim() == "0"));
        assert_eq!(encoding.solver.solve(), SolveResult::Unsat);
    }

    #[test]
    fn schoolbook_and_karatsuba_circuits_agree_with_field_arithmetic() {
        let mut rng = StdRng::seed_from_u64(0x5_2026_0910);
        for n in [7u32, 11, 23, 37, 41, 53] {
            let curve = KoblitzCurve::new(if n < 37 { 1 } else { 0 }, n).unwrap();
            let structure = FieldStructure::new(n, &curve.curve.irreducible);
            for _ in 0..4 {
                let x = rng.gen_range(0..(1u64 << n));
                let y = rng.gen_range(0..(1u64 << n));
                let x_field = F2mElement::from_biguint(&BigUint::from(x), n);
                let y_field = F2mElement::from_biguint(&BigUint::from(y), n);
                let expected = x_field.mul(&y_field, &curve.curve.irreducible);
                for karatsuba in [false, true] {
                    let mut builder = CircuitBuilder::new(2 * n as usize, karatsuba);
                    let left: Vec<_> = (1..=n).collect();
                    let right: Vec<_> = (n + 1..=2 * n).collect();
                    let output = builder.field_mul(&left, &right, &structure);
                    let mut solver = builder.finish();
                    for bit in 0..n {
                        let a = (bit + 1) as Lit;
                        let b = (n + bit + 1) as Lit;
                        assert!(solver.add_clause(vec![if (x >> bit) & 1 == 1 { a } else { -a }]));
                        assert!(solver.add_clause(vec![if (y >> bit) & 1 == 1 { b } else { -b }]));
                    }
                    assert_eq!(solver.solve(), SolveResult::Sat);
                    let model = solver.model();
                    let actual = output
                        .iter()
                        .enumerate()
                        .fold(0u64, |value, (bit, &variable)| {
                            value | (u64::from(model[variable as usize - 1]) << bit)
                        });
                    assert_eq!(actual, expected.raw_bits().first().copied().unwrap_or(0));
                }
            }
        }
    }

    #[test]
    fn full_rank_linear_solver_recovers_the_public_unknowns() {
        let modulus = 71;
        let expected = [17u64, 29u64, 43u64];
        let rows = vec![
            vec![1, 2, 3],
            vec![3, 5, 7],
            vec![11, 13, 17],
            vec![19, 23, 29],
        ];
        let right_hand_sides: Vec<_> = rows
            .iter()
            .map(|row| {
                row.iter()
                    .zip(expected)
                    .fold(0u64, |sum, (&left, right)| (sum + left * right) % modulus)
            })
            .collect();
        assert_eq!(dense_rank_mod(&rows, 3, modulus), 3);
        assert_eq!(
            solve_full_column_rank_system(&rows, &right_hand_sides, 3, modulus),
            Some(expected.to_vec())
        );
    }
}
