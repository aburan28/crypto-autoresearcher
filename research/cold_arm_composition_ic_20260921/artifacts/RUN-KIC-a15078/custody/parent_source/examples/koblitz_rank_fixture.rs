#![recursion_limit = "512"]
//! Point-defined factor base, exact-support relation collection, and rank trace.
//!
//! This is the fully charged V2 control for the Koblitz crossover task.  The
//! base is selected only from public point coordinates. Known-answer controls
//! retain a validation scalar; `hash:SEED` derives a subgroup point without
//! constructing its scalar and accepts recovery only after `[d]G = Q`.

use crypto_lib::binary_ecc::curve::point_neg;
use crypto_lib::binary_ecc::{BinaryPoint, F2mElement};
use crypto_lib::cryptanalysis::koblitz_index_calculus::{point_key, points_with_x, KoblitzCurve};
use num_bigint::BigUint;
use num_traits::ToPrimitive;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use rayon::prelude::*;
use serde_json::json;
use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::time::Instant;

const TASK_ID: &str = "TASK-KIC-SAT-RHO-CROSSOVER-20260909";
const RECEIPT_TASK_ID: &str = "TASK-20260921-bd19a7";

#[derive(Clone)]
struct Base {
    points: Vec<BinaryPoint>,
    point_labels: Vec<(usize, u64)>,
    representatives: Vec<BinaryPoint>,
    scanned_x: u64,
    signed_size: usize,
    point_selection: &'static str,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum PairMode {
    Full,
    SignedQuotient,
    SignedExpanded,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum TargetMode {
    Independent,
    CoefficientWalk,
    PartitionWalk,
}

#[derive(Clone, Copy)]
enum FixtureTarget {
    SeededScalar,
    ExplicitScalar(u64),
    PublicHash(u64),
}

impl FixtureTarget {
    fn parse(value: Option<&str>) -> Self {
        match value {
            None => Self::SeededScalar,
            Some(value) if value.starts_with("hash:") => Self::PublicHash(
                value[5..]
                    .parse()
                    .expect("public hash target seed must be a u64"),
            ),
            Some(value) => Self::ExplicitScalar(
                value
                    .parse()
                    .expect("explicit validation scalar must be a u64"),
            ),
        }
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum QueryMode {
    Pointwise,
    BatchInverse,
    BatchInverse4,
    BatchInverse8,
    BatchInverse16,
    BatchInverse32,
    BatchInverse64,
    BatchInverse128,
    BatchInverse256,
    FiberBatch16,
    FiberBatch32,
    FiberBatch64,
    PairPair16,
    PairPair32,
    PairPair64,
    PairPair128,
    PairPair256,
    PairPairParallel512,
    PairPairParallel1024,
    PairPairParallel2048,
    PairPairParallel4096,
}

impl QueryMode {
    fn parse(value: &str) -> Self {
        match value {
            "pointwise" => Self::Pointwise,
            "batch_inverse" => Self::BatchInverse,
            "batch_inverse_4" => Self::BatchInverse4,
            "batch_inverse_8" => Self::BatchInverse8,
            "batch_inverse_16" => Self::BatchInverse16,
            "batch_inverse_32" => Self::BatchInverse32,
            "batch_inverse_64" => Self::BatchInverse64,
            "batch_inverse_128" => Self::BatchInverse128,
            "batch_inverse_256" => Self::BatchInverse256,
            "fiber_batch_16" => Self::FiberBatch16,
            "fiber_batch_32" => Self::FiberBatch32,
            "fiber_batch_64" => Self::FiberBatch64,
            "pair_pair_16" => Self::PairPair16,
            "pair_pair_32" => Self::PairPair32,
            "pair_pair_64" => Self::PairPair64,
            "pair_pair_128" => Self::PairPair128,
            "pair_pair_256" => Self::PairPair256,
            "pair_pair_parallel_512" => Self::PairPairParallel512,
            "pair_pair_parallel_1024" => Self::PairPairParallel1024,
            "pair_pair_parallel_2048" => Self::PairPairParallel2048,
            "pair_pair_parallel_4096" => Self::PairPairParallel4096,
            _ => panic!("unknown query mode {value}"),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Pointwise => "pointwise",
            Self::BatchInverse => "batch_inverse",
            Self::BatchInverse4 => "batch_inverse_4",
            Self::BatchInverse8 => "batch_inverse_8",
            Self::BatchInverse16 => "batch_inverse_16",
            Self::BatchInverse32 => "batch_inverse_32",
            Self::BatchInverse64 => "batch_inverse_64",
            Self::BatchInverse128 => "batch_inverse_128",
            Self::BatchInverse256 => "batch_inverse_256",
            Self::FiberBatch16 => "fiber_batch_16",
            Self::FiberBatch32 => "fiber_batch_32",
            Self::FiberBatch64 => "fiber_batch_64",
            Self::PairPair16 => "pair_pair_16",
            Self::PairPair32 => "pair_pair_32",
            Self::PairPair64 => "pair_pair_64",
            Self::PairPair128 => "pair_pair_128",
            Self::PairPair256 => "pair_pair_256",
            Self::PairPairParallel512 => "pair_pair_parallel_512",
            Self::PairPairParallel1024 => "pair_pair_parallel_1024",
            Self::PairPairParallel2048 => "pair_pair_parallel_2048",
            Self::PairPairParallel4096 => "pair_pair_parallel_4096",
        }
    }

    fn width(self, points: usize) -> Option<usize> {
        match self {
            Self::Pointwise => None,
            Self::BatchInverse => Some(points),
            Self::BatchInverse4 => Some(4),
            Self::BatchInverse8 => Some(8),
            Self::BatchInverse16 => Some(16),
            Self::BatchInverse32 => Some(32),
            Self::BatchInverse64 => Some(64),
            Self::BatchInverse128 => Some(128),
            Self::BatchInverse256 => Some(256),
            Self::FiberBatch16
            | Self::FiberBatch32
            | Self::FiberBatch64
            | Self::PairPair16
            | Self::PairPair32
            | Self::PairPair64
            | Self::PairPair128
            | Self::PairPair256
            | Self::PairPairParallel512
            | Self::PairPairParallel1024
            | Self::PairPairParallel2048
            | Self::PairPairParallel4096 => None,
        }
    }

    fn fiber_width(self) -> Option<usize> {
        match self {
            Self::FiberBatch16 => Some(16),
            Self::FiberBatch32 => Some(32),
            Self::FiberBatch64 => Some(64),
            _ => None,
        }
    }

    fn pair_pair_width(self) -> Option<usize> {
        match self {
            Self::PairPair16 => Some(16),
            Self::PairPair32 => Some(32),
            Self::PairPair64 => Some(64),
            Self::PairPair128 => Some(128),
            Self::PairPair256 => Some(256),
            Self::PairPairParallel512 => Some(512),
            Self::PairPairParallel1024 => Some(1024),
            Self::PairPairParallel2048 => Some(2048),
            Self::PairPairParallel4096 => Some(4096),
            _ => None,
        }
    }

    fn pair_pair_parallel(self) -> bool {
        matches!(
            self,
            Self::PairPairParallel512
                | Self::PairPairParallel1024
                | Self::PairPairParallel2048
                | Self::PairPairParallel4096
        )
    }
}

#[derive(Clone)]
struct RawFiber {
    x: u64,
    members: Vec<(usize, u64)>,
}

impl TargetMode {
    fn parse(value: &str) -> Self {
        match value {
            "independent" => Self::Independent,
            "coefficient_walk" => Self::CoefficientWalk,
            "partition_walk" => Self::PartitionWalk,
            _ => panic!("unknown target mode {value}"),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Independent => "independent",
            Self::CoefficientWalk => "coefficient_walk",
            Self::PartitionWalk => "partition_walk",
        }
    }
}

impl PairMode {
    fn parse(value: &str) -> Self {
        match value {
            "full" => Self::Full,
            "signed_quotient" => Self::SignedQuotient,
            "signed_expanded" => Self::SignedExpanded,
            _ => panic!("unknown pair-index mode {value}"),
        }
    }

    fn name(self) -> &'static str {
        match self {
            Self::Full => "full",
            Self::SignedQuotient => "signed_quotient",
            Self::SignedExpanded => "signed_expanded",
        }
    }
}

#[derive(Clone, Copy, Default)]
struct QuotientPairWitness {
    columns: [u16; 2],
    coefficients: [u64; 2],
    image_y: u64,
}

impl QuotientPairWitness {
    fn new(labels: [(usize, u64); 2], image_y: u64) -> Self {
        Self {
            columns: [labels[0].0 as u16, labels[1].0 as u16],
            coefficients: [labels[0].1, labels[1].1],
            image_y,
        }
    }

    fn labels(self) -> [(usize, u64); 2] {
        [
            (self.columns[0] as usize, self.coefficients[0]),
            (self.columns[1] as usize, self.coefficients[1]),
        ]
    }

    fn from_point_indices(indices: [usize; 2], image_y: u64) -> Self {
        Self {
            columns: indices.map(|index| u16::try_from(index).expect("factor-base index fits u16")),
            coefficients: [0; 2],
            image_y,
        }
    }

    fn point_indices(self) -> [usize; 2] {
        self.columns.map(usize::from)
    }
}

struct CompactPairTable {
    keys_x: Vec<u64>,
    keys_y: Vec<u64>,
    // Cursor scans need only x and y to form the left pair point. Keep the
    // relation labels in separate cold arrays and load them after an exact
    // right-pair hit. In the signed-expanded table `columns` stores the two
    // factor-base point indices directly, so its 16-byte coefficient payload
    // is not allocated at all.
    columns: Vec<[u16; 2]>,
    coefficients: Vec<[u64; 2]>,
    image_y: Vec<u64>,
    x_filter: Vec<u64>,
    x_filter_mask: usize,
    x_filter_exact: bool,
    x_filter_split_hash: bool,
    x_filter_insert_hash_reuse: bool,
    x_filter_direct_bits: bool,
    x_filter_blocked: bool,
    x_filter_window_shift: u32,
    mask: usize,
    len: usize,
    x_only: bool,
}

impl CompactPairTable {
    fn with_capacity(expected: usize, x_only: bool, x_domain: usize) -> Self {
        let capacity = expected.max(2).next_power_of_two();
        let x_filter_exact = x_only && x_domain <= (1usize << 29);
        let filter_bits = if !x_only {
            0
        } else if x_filter_exact {
            x_domain
        } else {
            (expected.max(4) * 16).next_power_of_two()
        };
        Self {
            keys_x: vec![u64::MAX; capacity],
            keys_y: if x_only {
                Vec::new()
            } else {
                vec![0; capacity]
            },
            columns: vec![[0; 2]; capacity],
            coefficients: if x_only {
                Vec::new()
            } else {
                vec![[0; 2]; capacity]
            },
            image_y: vec![0; capacity],
            x_filter: if filter_bits != 0 {
                vec![0; filter_bits.div_ceil(u64::BITS as usize)]
            } else {
                Vec::new()
            },
            x_filter_mask: filter_bits.saturating_sub(1),
            x_filter_exact,
            x_filter_split_hash: std::env::var("KIC_DISABLE_SPLIT_BLOOM_HASH").as_deref()
                != Ok("1"),
            x_filter_insert_hash_reuse: std::env::var("KIC_DISABLE_INSERT_HASH_REUSE").as_deref()
                != Ok("1"),
            x_filter_direct_bits: std::env::var("KIC_DISABLE_DIRECT_X_FILTER_BITS").as_deref()
                != Ok("1"),
            x_filter_blocked: std::env::var("KIC_ENABLE_BLOCKED_X_FILTER").as_deref() == Ok("1"),
            x_filter_window_shift: if filter_bits == 0 || x_filter_exact {
                0
            } else {
                let field_bits = (x_domain - 1).trailing_zeros();
                let filter_index_bits = filter_bits.trailing_zeros();
                field_bits.saturating_sub(filter_index_bits)
            },
            mask: capacity - 1,
            len: 0,
            x_only,
        }
    }

    fn hash((x, y): (u64, u64)) -> u64 {
        let mut value = x ^ y.rotate_left(23) ^ 0x9e37_79b9_7f4a_7c15;
        value ^= value >> 30;
        value = value.wrapping_mul(0xbf58_476d_1ce4_e5b9);
        value ^= value >> 27;
        value = value.wrapping_mul(0x94d0_49bb_1331_11eb);
        value ^ (value >> 31)
    }

    fn insert(&mut self, key: (u64, u64), value: QuotientPairWitness) {
        let hash_key = if self.x_only { (key.0, 0) } else { key };
        let mixed = Self::hash(hash_key);
        let mut index = mixed as usize & self.mask;
        loop {
            if self.keys_x[index] == u64::MAX {
                self.keys_x[index] = key.0;
                if !self.x_only {
                    self.keys_y[index] = key.1;
                }
                self.columns[index] = value.columns;
                if !self.x_only {
                    self.coefficients[index] = value.coefficients;
                }
                self.image_y[index] = value.image_y;
                if self.x_only {
                    if self.x_filter_blocked && !self.x_filter_exact {
                        self.insert_x_filter_blocked(key.0);
                    } else if self.x_filter_direct_bits && !self.x_filter_exact {
                        self.insert_x_filter_direct(key.0);
                    } else if self.x_filter_insert_hash_reuse {
                        self.insert_x_filter_with_mixed(key.0, mixed);
                    } else {
                        self.insert_x_filter(key.0);
                    }
                }
                self.len += 1;
                return;
            }
            if self.keys_x[index] == key.0 && (self.x_only || self.keys_y[index] == key.1) {
                return;
            }
            index = (index + 1) & self.mask;
        }
    }

    fn get(&self, key: (u64, u64)) -> Option<QuotientPairWitness> {
        if self.x_only && !self.might_contain_x(key.0) {
            return None;
        }
        self.get_after_x_filter(key)
    }

    /// Exact table lookup for a key that already passed `might_contain_x`.
    /// Pair-query batches use this to avoid reading the Bloom filter twice for
    /// every surviving candidate. The open-addressed table remains the exact
    /// fallback, so this changes no membership decision.
    fn get_after_x_filter(&self, key: (u64, u64)) -> Option<QuotientPairWitness> {
        let hash_key = if self.x_only { (key.0, 0) } else { key };
        let mut index = Self::hash(hash_key) as usize & self.mask;
        loop {
            if self.keys_x[index] == u64::MAX {
                return None;
            }
            if self.keys_x[index] == key.0 && (self.x_only || self.keys_y[index] == key.1) {
                return Some(QuotientPairWitness {
                    columns: self.columns[index],
                    coefficients: if self.x_only {
                        [0; 2]
                    } else {
                        self.coefficients[index]
                    },
                    image_y: self.image_y[index],
                });
            }
            index = (index + 1) & self.mask;
        }
    }

    fn len(&self) -> usize {
        self.len
    }

    fn might_contain_x(&self, x: u64) -> bool {
        if !self.x_only {
            return true;
        }
        if self.x_filter_blocked && !self.x_filter_exact {
            let (word, mask) = self.x_filter_blocked_word_and_mask(x);
            return self.x_filter[word] & mask == mask;
        }
        let (first, second) = self.x_filter_indices(x);
        self.x_filter[first / u64::BITS as usize] & (1u64 << (first % u64::BITS as usize)) != 0
            && self.x_filter[second / u64::BITS as usize] & (1u64 << (second % u64::BITS as usize))
                != 0
    }

    fn insert_x_filter(&mut self, x: u64) {
        let mixed = Self::hash((x, 0));
        self.insert_x_filter_with_mixed(x, mixed);
    }

    fn insert_x_filter_direct(&mut self, x: u64) {
        let (first, second) = self.x_filter_direct_indices(x);
        self.x_filter[first / u64::BITS as usize] |= 1u64 << (first % u64::BITS as usize);
        self.x_filter[second / u64::BITS as usize] |= 1u64 << (second % u64::BITS as usize);
    }

    fn insert_x_filter_blocked(&mut self, x: u64) {
        let (word, mask) = self.x_filter_blocked_word_and_mask(x);
        self.x_filter[word] |= mask;
    }

    fn insert_x_filter_with_mixed(&mut self, x: u64, mixed: u64) {
        let (first, second) = self.x_filter_indices_with_mixed(x, mixed);
        self.x_filter[first / u64::BITS as usize] |= 1u64 << (first % u64::BITS as usize);
        self.x_filter[second / u64::BITS as usize] |= 1u64 << (second % u64::BITS as usize);
    }

    fn x_filter_indices(&self, x: u64) -> (usize, usize) {
        if self.x_filter_exact {
            let index = x as usize;
            return (index, index);
        }
        if self.x_filter_direct_bits {
            return self.x_filter_direct_indices(x);
        }
        self.x_filter_indices_with_mixed(x, Self::hash((x, 0)))
    }

    fn x_filter_indices_with_mixed(&self, x: u64, mixed: u64) -> (usize, usize) {
        if self.x_filter_exact {
            let index = x as usize;
            return (index, index);
        }
        if self.x_filter_direct_bits {
            return self.x_filter_direct_indices(x);
        }
        let first = mixed as usize & self.x_filter_mask;
        let second = if self.x_filter_split_hash {
            (mixed >> 32) as usize & self.x_filter_mask
        } else {
            Self::hash((x ^ 0xd6e8_feb8_6659_fd93, x.rotate_left(17))) as usize & self.x_filter_mask
        };
        (first, second)
    }

    #[inline(always)]
    fn x_filter_direct_indices(&self, x: u64) -> (usize, usize) {
        debug_assert!(!self.x_filter_exact);
        let first = x as usize & self.x_filter_mask;
        let second = (x >> self.x_filter_window_shift) as usize & self.x_filter_mask;
        (first, second)
    }

    #[inline(always)]
    fn x_filter_blocked_word_and_mask(&self, x: u64) -> (usize, u64) {
        debug_assert!(!self.x_filter_exact);
        debug_assert!(self.x_filter.len().is_power_of_two());
        let word = x as usize & (self.x_filter.len() - 1);
        let fingerprint = x >> self.x_filter.len().trailing_zeros();
        let mask = (1u64 << (fingerprint & 63))
            | (1u64 << ((fingerprint >> 6) & 63))
            | (1u64 << ((fingerprint >> 12) & 63))
            | (1u64 << ((fingerprint >> 18) & 63));
        (word, mask)
    }

    fn allocated_bytes(&self) -> usize {
        self.keys_x.len() * std::mem::size_of::<u64>()
            + self.keys_y.len() * std::mem::size_of::<u64>()
            + self.columns.len() * std::mem::size_of::<[u16; 2]>()
            + self.coefficients.len() * std::mem::size_of::<[u64; 2]>()
            + self.image_y.len() * std::mem::size_of::<u64>()
            + self.x_filter.len() * std::mem::size_of::<u64>()
    }

    fn slots_for_column(
        &self,
        point_labels: &[(usize, u64)],
        column: usize,
        column_count: usize,
    ) -> Vec<u32> {
        assert!(self.x_only);
        assert!(self.keys_x.len() <= u32::MAX as usize);
        let mut result = Vec::with_capacity(self.len * 2 / column_count + 1);
        for slot in 0..self.keys_x.len() {
            if self.keys_x[slot] == u64::MAX {
                continue;
            }
            let indices = self.columns[slot].map(usize::from);
            let left = point_labels[indices[0]].0;
            let right = point_labels[indices[1]].0;
            if left == column || right == column {
                result.push(slot as u32);
            }
        }
        result
    }

    fn x_filter_kind(&self) -> &'static str {
        if !self.x_only {
            "disabled"
        } else if self.x_filter_exact {
            "exact_dense_bitset"
        } else {
            "two_hash_bloom_prefilter_with_exact_table_fallback"
        }
    }

    fn x_filter_bits(&self) -> usize {
        self.x_filter.len() * u64::BITS as usize
    }

    fn x_filter_hash_strategy(&self) -> &'static str {
        if self.x_filter_exact {
            "exact_index"
        } else if self.x_filter_blocked {
            "blocked_one_word_four_bit_x_fingerprint"
        } else if self.x_filter_direct_bits {
            "direct_low_and_high_x_bit_windows"
        } else if self.x_filter_split_hash {
            "single_mix_split_29_bit_indices"
        } else {
            "two_independent_64_bit_mixes"
        }
    }

    fn x_filter_insert_hash_reuse(&self) -> bool {
        self.x_filter_insert_hash_reuse && !self.x_filter_direct_bits && !self.x_filter_blocked
    }

    fn x_filter_direct_bits(&self) -> bool {
        self.x_filter_direct_bits && !self.x_filter_exact && !self.x_filter_blocked
    }

    fn x_filter_blocked(&self) -> bool {
        self.x_filter_blocked && !self.x_filter_exact
    }

    fn slots(&self) -> usize {
        self.keys_x.len()
    }

    fn signed_point_at_slot(&self, slot: usize, negative: bool) -> Option<RawPoint> {
        let key_x = *self.keys_x.get(slot)?;
        if key_x == u64::MAX || (key_x == 0 && negative) {
            return None;
        }
        let point = if key_x == 0 {
            None
        } else {
            let x = key_x - 1;
            let mut y = self.image_y[slot];
            if negative {
                y ^= x;
            }
            Some((x, y))
        };
        Some(point)
    }

    /// Return the positive point as `(x + 1, y)`, with `(0, 0)` encoding
    /// infinity. The outer `Option` still distinguishes an empty table slot.
    fn compact_point_at_slot(&self, slot: usize) -> Option<(u64, u64)> {
        let key_x = *self.keys_x.get(slot)?;
        if key_x == u64::MAX {
            None
        } else {
            Some((key_x, self.image_y[slot]))
        }
    }

    fn signed_labels_at_slot(
        &self,
        slot: usize,
        negative: bool,
        modulus: u64,
        point_labels: &[(usize, u64)],
        label_to_index: &HashMap<(usize, u64), usize>,
    ) -> ([usize; 2], [(usize, u64); 2]) {
        debug_assert!(self.keys_x.get(slot).is_some_and(|&key| key != u64::MAX));
        debug_assert!(self.x_only);
        let mut indices = self.columns[slot].map(usize::from);
        let mut labels = indices.map(|index| point_labels[index]);
        if negative {
            labels = labels.map(|(column, coefficient)| {
                (
                    column,
                    if coefficient == 0 {
                        0
                    } else {
                        modulus - coefficient
                    },
                )
            });
            indices = labels.map(|label| label_to_index[&label]);
        }
        (indices, labels)
    }
}

fn compact_point_key(point: &BinaryPoint) -> (u64, u64) {
    match point {
        BinaryPoint::Infinity => (0, 0),
        BinaryPoint::Affine { x, y } => (
            x.raw_bits().first().copied().unwrap_or(0) + 1,
            y.raw_bits().first().copied().unwrap_or(0),
        ),
    }
}

// Common ARM carryless-product port; both IC and rho use the same guard.
#[inline]
fn arm_pmull_enabled() -> bool {
    #[cfg(target_arch = "aarch64")]
    { std::arch::is_aarch64_feature_detected!("aes") }
    #[cfg(not(target_arch = "aarch64"))]
    { false }
}

#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "aes")]
unsafe fn arm_pmull_product(left: u64, right: u64) -> u128 {
    std::arch::aarch64::vmull_p64(left, right)
}

fn square_raw_dispatched(curve: &KoblitzCurve, value: u64) -> u64 {
    #[cfg(target_arch = "aarch64")]
    if arm_pmull_enabled() {
        // SAFETY: the runtime guard proves the required PMULL feature.
        return reduce_raw(curve, unsafe { arm_pmull_product(value, value) });
    }
    #[cfg(target_arch = "x86_64")]
    if pclmul_enabled() {
        if curve.n == 53 && n53_fast_reduction_enabled() && fused_pcl_n53_enabled() {
            // SAFETY: the cached runtime feature check guards every call.
            return unsafe { pclmul_reduce_n53(value, value) };
        }
        // In characteristic two the carryless product value * value has no
        // cross terms, so it is exactly the interleaved polynomial square.
        // SAFETY: the cached runtime feature check guards every call.
        return reduce_raw(curve, unsafe { pclmul_u64(value, value) });
    }
    if curve.n <= 31 {
        let mut wide = value;
        wide = (wide | (wide << 16)) & 0x0000_ffff_0000_ffff;
        wide = (wide | (wide << 8)) & 0x00ff_00ff_00ff_00ff;
        wide = (wide | (wide << 4)) & 0x0f0f_0f0f_0f0f_0f0f;
        wide = (wide | (wide << 2)) & 0x3333_3333_3333_3333;
        wide = (wide | (wide << 1)) & 0x5555_5555_5555_5555;
        return reduce_raw(curve, wide as u128);
    }
    let mut bits = value;
    let mut wide = 0u128;
    while bits != 0 {
        let bit = bits.trailing_zeros();
        wide ^= 1u128 << (2 * bit);
        bits &= bits - 1;
    }
    reduce_raw(curve, wide)
}

#[inline(always)]
fn square_raw(curve: &KoblitzCurve, value: u64) -> u64 {
    #[cfg(target_arch = "x86_64")]
    if curve.n == 53 && combined_n53_fast_path_enabled() {
        // SAFETY: the combined cached predicate includes the runtime PCLMUL
        // feature check and both exact degree-53 reduction controls.
        return unsafe { pclmul_reduce_n53(value, value) };
    }
    square_raw_dispatched(curve, value)
}

fn reduce_raw(curve: &KoblitzCurve, mut wide: u128) -> u64 {
    if curve.n == 53 && n53_fast_reduction_enabled() {
        debug_assert_eq!(curve.curve.irreducible.low_terms, [0, 1, 2, 6]);
        const MASK: u64 = (1u64 << 53) - 1;
        // x^53 = x^6 + x^2 + x + 1. A product has degree at most
        // 104, so one full fold leaves at most six high bits and a second
        // fixed fold completes the reduction.
        let high = (wide >> 53) as u64;
        let first = (wide as u64 & MASK) ^ high ^ (high << 1) ^ (high << 2) ^ (high << 6);
        let overflow = first >> 53;
        return (first & MASK) ^ overflow ^ (overflow << 1) ^ (overflow << 2) ^ (overflow << 6);
    }
    if curve.n <= 31 && wide <= u64::MAX as u128 {
        let mut narrow = wide as u64;
        let mask = (1u64 << curve.n) - 1;
        while narrow >> curve.n != 0 {
            let high = narrow >> curve.n;
            narrow &= mask;
            for &term in &curve.curve.irreducible.low_terms {
                narrow ^= high << term;
            }
        }
        return narrow;
    }
    let mask = (1u128 << curve.n) - 1;
    while wide >> curve.n != 0 {
        let high = wide >> curve.n;
        wide &= mask;
        for &term in &curve.curve.irreducible.low_terms {
            wide ^= high << term;
        }
    }
    wide as u64
}

#[inline(always)]
fn n53_fast_reduction_enabled() -> bool {
    use std::sync::OnceLock;
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var("KIC_DISABLE_N53_FAST_REDUCTION").as_deref() != Ok("1"))
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn pclmul_u64(left: u64, right: u64) -> u128 {
    use std::arch::x86_64::*;
    let x = _mm_set_epi64x(0, left as i64);
    let y = _mm_set_epi64x(0, right as i64);
    let product = _mm_clmulepi64_si128::<0x00>(x, y);
    let low = _mm_cvtsi128_si64(product) as u64;
    let high = _mm_cvtsi128_si64(_mm_srli_si128::<8>(product)) as u64;
    (high as u128) << 64 | low as u128
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn pclmul_reduce_n53(left: u64, right: u64) -> u64 {
    use std::arch::x86_64::*;
    const MASK: u64 = (1u64 << 53) - 1;
    let x = _mm_set_epi64x(0, left as i64);
    let y = _mm_set_epi64x(0, right as i64);
    let product = _mm_clmulepi64_si128::<0x00>(x, y);
    let low = _mm_cvtsi128_si64(product) as u64;
    let high_word = _mm_cvtsi128_si64(_mm_srli_si128::<8>(product)) as u64;
    let high = (low >> 53) | (high_word << 11);
    let first = (low & MASK) ^ high ^ (high << 1) ^ (high << 2) ^ (high << 6);
    let overflow = first >> 53;
    (first & MASK) ^ overflow ^ (overflow << 1) ^ (overflow << 2) ^ (overflow << 6)
}

#[inline(always)]
fn fused_pcl_n53_enabled() -> bool {
    use std::sync::OnceLock;
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var("KIC_DISABLE_FUSED_PCL_N53").as_deref() != Ok("1"))
}

#[inline(always)]
fn pclmul_enabled() -> bool {
    #[cfg(target_arch = "x86_64")]
    {
        use std::sync::OnceLock;
        static ENABLED: OnceLock<bool> = OnceLock::new();
        *ENABLED.get_or_init(|| {
            std::env::var("KIC_DISABLE_PCLMUL").as_deref() != Ok("1")
                && std::arch::is_x86_feature_detected!("pclmulqdq")
        })
    }
    #[cfg(not(target_arch = "x86_64"))]
    {
        false
    }
}

#[inline(always)]
fn combined_n53_fast_path_enabled() -> bool {
    #[cfg(target_arch = "x86_64")]
    {
        use std::sync::OnceLock;
        static ENABLED: OnceLock<bool> = OnceLock::new();
        *ENABLED.get_or_init(|| {
            std::env::var("KIC_DISABLE_COMBINED_N53_FAST_PATH").as_deref() != Ok("1")
                && pclmul_enabled()
                && n53_fast_reduction_enabled()
                && fused_pcl_n53_enabled()
        })
    }
    #[cfg(not(target_arch = "x86_64"))]
    {
        false
    }
}

fn field_mul_backend() -> &'static str {
    if arm_pmull_enabled() { return "aarch64_pmull"; }
    if pclmul_enabled() {
        "x86_64_pclmulqdq"
    } else {
        "portable_sparse_carryless"
    }
}

fn field_square_backend(curve: &KoblitzCurve) -> &'static str {
    if arm_pmull_enabled() { return "aarch64_pmull"; }
    if pclmul_enabled() {
        "x86_64_pclmulqdq"
    } else if curve.n <= 31 {
        "portable_interleaved_bit_spread"
    } else {
        "portable_sparse_bit_interleave"
    }
}

fn field_reduction_backend(curve: &KoblitzCurve) -> &'static str {
    if curve.n == 53 && n53_fast_reduction_enabled() {
        "n53_fixed_two_fold"
    } else {
        "generic_polynomial_fold"
    }
}

fn field_product_pipeline(curve: &KoblitzCurve) -> &'static str {
    if curve.n == 53 && pclmul_enabled() && n53_fast_reduction_enabled() && fused_pcl_n53_enabled()
    {
        "x86_64_pclmul_n53_fused_reduce"
    } else {
        "separate_product_and_reduction"
    }
}

fn field_product_dispatch(curve: &KoblitzCurve) -> &'static str {
    if curve.n == 53 && combined_n53_fast_path_enabled() {
        "inline_combined_n53_predicate"
    } else {
        "legacy_per_operation_feature_dispatch"
    }
}

fn mul_raw_dispatched(curve: &KoblitzCurve, left: u64, right: u64) -> u64 {
    #[cfg(target_arch = "aarch64")]
    if arm_pmull_enabled() {
        // SAFETY: the runtime guard proves the required PMULL feature.
        return reduce_raw(curve, unsafe { arm_pmull_product(left, right) });
    }
    #[cfg(target_arch = "x86_64")]
    if pclmul_enabled() {
        if curve.n == 53 && n53_fast_reduction_enabled() && fused_pcl_n53_enabled() {
            // SAFETY: the cached runtime feature check guards every call.
            return unsafe { pclmul_reduce_n53(left, right) };
        }
        // SAFETY: the cached runtime feature check above guards every call.
        return reduce_raw(curve, unsafe { pclmul_u64(left, right) });
    }
    if curve.n <= 31 {
        let mut product = 0u64;
        let mut value = right;
        while value != 0 {
            let bit = value.trailing_zeros();
            product ^= left << bit;
            value &= value - 1;
        }
        return reduce_raw(curve, product as u128);
    }
    let mut product = 0u128;
    let mut value = right;
    while value != 0 {
        let bit = value.trailing_zeros();
        product ^= (left as u128) << bit;
        value &= value - 1;
    }
    reduce_raw(curve, product)
}

#[inline(always)]
fn mul_raw(curve: &KoblitzCurve, left: u64, right: u64) -> u64 {
    #[cfg(target_arch = "x86_64")]
    if curve.n == 53 && combined_n53_fast_path_enabled() {
        // SAFETY: the combined cached predicate includes the runtime PCLMUL
        // feature check and both exact degree-53 reduction controls.
        return unsafe { pclmul_reduce_n53(left, right) };
    }
    mul_raw_dispatched(curve, left, right)
}

fn inverse_raw(curve: &KoblitzCurve, value: u64) -> u64 {
    assert_ne!(value, 0);
    let exponent = (1u64 << curve.n) - 2;
    let mut result = 1u64;
    let mut base = value;
    for bit in 0..curve.n {
        if (exponent >> bit) & 1 == 1 {
            result = mul_raw(curve, result, base);
        }
        base = square_raw(curve, base);
    }
    result
}

type RawPoint = Option<(u64, u64)>;

fn to_raw_point(point: &BinaryPoint) -> RawPoint {
    raw_affine(point)
}

fn public_hash_target(curve: &KoblitzCurve, seed: u64) -> (BinaryPoint, u64) {
    const DOMAIN: &[u8] = b"ic-workflow-public-target-v1\0";
    let mask = (1u64 << curve.n) - 1;
    for counter in 0u64..1_000_000 {
        let mut hasher = blake3::Hasher::new();
        hasher.update(DOMAIN);
        hasher.update(&curve.n.to_le_bytes());
        hasher.update(&[curve.a]);
        hasher.update(&curve.k.to_le_bytes());
        hasher.update(&curve.b_index.to_le_bytes());
        hasher.update(&seed.to_le_bytes());
        hasher.update(&counter.to_le_bytes());
        let digest = hasher.finalize();
        let bytes = digest.as_bytes();
        let mut word = [0u8; 8];
        word.copy_from_slice(&bytes[..8]);
        let x = F2mElement::from_biguint(&BigUint::from(u64::from_le_bytes(word) & mask), curve.n);
        let mut lifts = points_with_x(&curve.curve, &x);
        lifts.sort_by_key(point_key);
        if lifts.is_empty() {
            continue;
        }
        let raw = lifts[usize::from(bytes[8] & 1) % lifts.len()].clone();
        let target = curve.mul(&raw, &curve.cofactor);
        if target == BinaryPoint::Infinity {
            continue;
        }
        assert_eq!(
            curve.mul(&target, &curve.subgroup_order),
            BinaryPoint::Infinity,
            "public hash target must enter the prime-order subgroup"
        );
        return (target, counter);
    }
    panic!("public hash-to-curve target attempt cap exhausted");
}

fn raw_neg_point(point: RawPoint) -> RawPoint {
    point.map(|(x, y)| (x, y ^ x))
}

fn raw_double_point(curve: &KoblitzCurve, point: RawPoint) -> RawPoint {
    let (x, y) = point?;
    if x == 0 {
        return None;
    }
    let lambda = x ^ mul_raw(curve, y, inverse_raw(curve, x));
    let x3 = square_raw(curve, lambda) ^ lambda ^ curve.a as u64;
    let y3 = square_raw(curve, x) ^ mul_raw(curve, lambda ^ 1, x3);
    Some((x3, y3))
}

fn raw_add_point(curve: &KoblitzCurve, left: RawPoint, right: RawPoint) -> RawPoint {
    match (left, right) {
        (None, point) | (point, None) => point,
        (Some((x1, y1)), Some((x2, y2))) => {
            if x1 == x2 {
                return if y1 ^ y2 == x1 {
                    None
                } else {
                    raw_double_point(curve, left)
                };
            }
            let lambda = mul_raw(curve, y1 ^ y2, inverse_raw(curve, x1 ^ x2));
            let x3 = square_raw(curve, lambda) ^ lambda ^ x1 ^ x2 ^ curve.a as u64;
            let y3 = mul_raw(curve, lambda, x1 ^ x3) ^ x3 ^ y1;
            Some((x3, y3))
        }
    }
}

fn raw_scalar_point(curve: &KoblitzCurve, point: RawPoint, scalar: u64) -> RawPoint {
    let mut result = None;
    for bit in (0..64 - scalar.leading_zeros()).rev() {
        result = raw_double_point(curve, result);
        if (scalar >> bit) & 1 == 1 {
            result = raw_add_point(curve, result, point);
        }
    }
    result
}

fn raw_compact_key(point: RawPoint) -> (u64, u64) {
    point.map(|(x, y)| (x + 1, y)).unwrap_or((0, 0))
}

fn target_partition(point: RawPoint) -> usize {
    let (x, y) = raw_compact_key(point);
    let mut value = x ^ y.rotate_left(17) ^ 0xd6e8_feb8_6659_fd93;
    value ^= value >> 32;
    value = value.wrapping_mul(0x9e37_79b9_7f4a_7c15);
    value ^= value >> 29;
    value as usize % 3
}

fn raw_affine(point: &BinaryPoint) -> Option<(u64, u64)> {
    match point {
        BinaryPoint::Infinity => None,
        BinaryPoint::Affine { x, y } => Some((
            x.raw_bits().first().copied().unwrap_or(0),
            y.raw_bits().first().copied().unwrap_or(0),
        )),
    }
}

fn canonical_signed_point(
    curve: &KoblitzCurve,
    point: &BinaryPoint,
    modulus: u64,
    lambda: u64,
) -> ((u64, u64), u64, usize) {
    canonical_signed_key(curve, compact_point_key(point), modulus, lambda)
}

fn canonical_signed_key(
    curve: &KoblitzCurve,
    key: (u64, u64),
    modulus: u64,
    lambda: u64,
) -> ((u64, u64), u64, usize) {
    if key.0 == 0 {
        return (key, 1, 0);
    }
    let mut current_x = key.0 - 1;
    let mut current_y = key.1;
    let mut multiplier = 1u64;
    let mut best_key = (current_x + 1, current_y);
    let mut best_multiplier = multiplier;
    let mut maps = 0usize;
    for exponent in 0..curve.n {
        let key = (current_x + 1, current_y);
        if key < best_key {
            best_key = key;
            best_multiplier = multiplier;
        }
        let negative_key = (current_x + 1, current_y ^ current_x);
        if negative_key < best_key {
            best_key = negative_key;
            best_multiplier = modulus - multiplier;
        }
        if exponent + 1 < curve.n {
            current_x = square_raw(curve, current_x);
            current_y = square_raw(curve, current_y);
            multiplier = ((multiplier as u128 * lambda as u128) % modulus as u128) as u64;
            maps += 1;
        }
    }
    (best_key, best_multiplier, maps)
}

#[derive(Default)]
struct Echelon {
    pivots: Vec<Option<Vec<u64>>>,
    rank: usize,
}

#[derive(Default)]
struct ReverseEchelon {
    pivots: Vec<Option<Vec<u64>>>,
    rank: usize,
}

#[derive(Clone)]
struct AffinePivot {
    coefficients: Vec<u64>,
    rhs: u64,
    weights: Vec<u64>,
}

#[derive(Clone)]
struct TargetCertificate {
    weights: Vec<u64>,
    returned_d: u64,
    pivot_column: usize,
    prefix_rows: usize,
    rank_a_b: usize,
}

enum AffineInsertOutcome {
    Dependent,
    Pivot(usize),
    Inconsistent,
    TargetIdentified(TargetCertificate),
}

struct AffineCertificateEchelon {
    pivots: Vec<Option<AffinePivot>>,
    rank_a_b: usize,
    original_rows: usize,
    target_column: usize,
}

#[derive(Clone)]
struct CertificateRecomputation {
    w_a: Vec<u64>,
    w_b: u64,
    w_rhs: u64,
    valid: bool,
}

fn mod_mul(left: u64, right: u64, modulus: u64) -> u64 {
    ((left as u128 * right as u128) % modulus as u128) as u64
}

fn mod_sub(left: u64, right: u64, modulus: u64) -> u64 {
    if left >= right { left - right } else { modulus - (right - left) }
}

impl AffineCertificateEchelon {
    fn new(variables: usize, target_column: usize) -> Self {
        assert_eq!(target_column + 1, variables, "target certificate requires the final variable column");
        Self {
            pivots: vec![None; variables],
            rank_a_b: 0,
            original_rows: 0,
            target_column,
        }
    }

    fn insert(&mut self, mut coefficients: Vec<u64>, mut rhs: u64, modulus: u64) -> AffineInsertOutcome {
        assert_eq!(coefficients.len(), self.pivots.len());
        for pivot in self.pivots.iter_mut().flatten() {
            pivot.weights.push(0);
        }
        let row_index = self.original_rows;
        self.original_rows += 1;
        let mut weights = vec![0u64; self.original_rows];
        weights[row_index] = 1;
        for column in 0..coefficients.len() {
            if coefficients[column] == 0 {
                continue;
            }
            if let Some(pivot) = &self.pivots[column] {
                let factor = coefficients[column];
                for index in column..coefficients.len() {
                    coefficients[index] = mod_sub(
                        coefficients[index],
                        mod_mul(factor, pivot.coefficients[index], modulus),
                        modulus,
                    );
                }
                rhs = mod_sub(rhs, mod_mul(factor, pivot.rhs, modulus), modulus);
                for index in 0..weights.len() {
                    weights[index] = mod_sub(
                        weights[index],
                        mod_mul(factor, pivot.weights[index], modulus),
                        modulus,
                    );
                }
                continue;
            }
            let inverse = modpow(coefficients[column], modulus - 2, modulus);
            for value in &mut coefficients[column..] {
                *value = mod_mul(*value, inverse, modulus);
            }
            rhs = mod_mul(rhs, inverse, modulus);
            for value in &mut weights {
                *value = mod_mul(*value, inverse, modulus);
            }
            let pivot = AffinePivot {
                coefficients,
                rhs,
                weights,
            };
            self.rank_a_b += 1;
            let outcome = if column == self.target_column {
                AffineInsertOutcome::TargetIdentified(TargetCertificate {
                    weights: pivot.weights.clone(),
                    returned_d: pivot.rhs,
                    pivot_column: column,
                    prefix_rows: self.original_rows,
                    rank_a_b: self.rank_a_b,
                })
            } else {
                AffineInsertOutcome::Pivot(column)
            };
            self.pivots[column] = Some(pivot);
            return outcome;
        }
        if rhs == 0 {
            AffineInsertOutcome::Dependent
        } else {
            AffineInsertOutcome::Inconsistent
        }
    }
}

fn recompute_target_certificate(
    rows: &[Vec<u64>],
    right_hand_sides: &[u64],
    weights: &[u64],
    target_column: usize,
    returned_d: u64,
    modulus: u64,
) -> CertificateRecomputation {
    assert_eq!(rows.len(), right_hand_sides.len());
    assert_eq!(rows.len(), weights.len());
    let mut combined = vec![0u64; rows[0].len()];
    let mut w_rhs = 0u64;
    for ((row, &rhs), &weight) in rows.iter().zip(right_hand_sides).zip(weights) {
        for (value, &coefficient) in combined.iter_mut().zip(row) {
            *value = ((*value as u128 + mod_mul(weight, coefficient, modulus) as u128)
                % modulus as u128) as u64;
        }
        w_rhs = ((w_rhs as u128 + mod_mul(weight, rhs, modulus) as u128)
            % modulus as u128) as u64;
    }
    let w_b = combined[target_column];
    let w_a = combined[..target_column].to_vec();
    let valid = w_a.iter().all(|&value| value == 0) && w_b == 1 && w_rhs == returned_d;
    CertificateRecomputation { w_a, w_b, w_rhs, valid }
}

fn modpow(mut base: u64, mut exponent: u64, modulus: u64) -> u64 {
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

fn signed_scalars(lambda: u64, modulus: u64, n: u32) -> BTreeSet<u64> {
    let mut result = BTreeSet::new();
    let mut value = 1u64;
    for _ in 0..n {
        result.insert(value);
        result.insert((modulus - value) % modulus);
        value = ((value as u128 * lambda as u128) % modulus as u128) as u64;
    }
    assert_eq!(value, 1);
    result
}

fn balanced_orbits(
    subgroup_order: &BigUint,
    signed_size: usize,
    numerator: u32,
    denominator: u32,
) -> usize {
    let rhs = subgroup_order * BigUint::from(6u32 * numerator);
    for k in 1usize.. {
        let points = BigUint::from((signed_size * k) as u64);
        if points.pow(3) * BigUint::from(denominator) >= rhs {
            return k;
        }
    }
    unreachable!()
}

fn signed_point_orbit(curve: &KoblitzCurve, point: &BinaryPoint) -> Vec<BinaryPoint> {
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

fn absolute_trace_bit(curve: &KoblitzCurve, x: &F2mElement) -> bool {
    let mut trace = F2mElement::zero(curve.n);
    let mut power = x.clone();
    for _ in 0..curve.n {
        trace = trace.add(&power);
        power = power.square(&curve.curve.irreducible);
    }
    assert!(trace.is_zero() || trace == F2mElement::one(curve.n));
    !trace.is_zero()
}

fn batch_target_minus_base(
    curve: &KoblitzCurve,
    target: &BinaryPoint,
    points: &[BinaryPoint],
) -> Vec<BinaryPoint> {
    let BinaryPoint::Affine {
        x: target_x,
        y: target_y,
    } = target
    else {
        return points.iter().map(point_neg).collect();
    };
    let irr = &curve.curve.irreducible;
    let mut denominators: Vec<Option<F2mElement>> = Vec::with_capacity(points.len());
    let mut prefixes: Vec<Option<F2mElement>> = Vec::with_capacity(points.len());
    let mut product = F2mElement::one(curve.n);
    for point in points {
        let BinaryPoint::Affine { x, .. } = point else {
            denominators.push(None);
            prefixes.push(None);
            continue;
        };
        if x == target_x {
            denominators.push(None);
            prefixes.push(None);
            continue;
        }
        let denominator = target_x.add(x);
        prefixes.push(Some(product.clone()));
        product = product.mul(&denominator, irr);
        denominators.push(Some(denominator));
    }
    let mut inverse_product = product
        .flt_inverse(irr)
        .expect("nonempty nonzero batch product");
    let mut inverses: Vec<Option<F2mElement>> = vec![None; points.len()];
    for index in (0..points.len()).rev() {
        let (Some(denominator), Some(prefix)) = (&denominators[index], &prefixes[index]) else {
            continue;
        };
        inverses[index] = Some(inverse_product.mul(prefix, irr));
        inverse_product = inverse_product.mul(denominator, irr);
    }
    points
        .iter()
        .enumerate()
        .map(|(index, point)| {
            let negative = point_neg(point);
            let BinaryPoint::Affine { x, y } = &negative else {
                return target.clone();
            };
            let Some(inverse) = &inverses[index] else {
                return curve.add(target, &negative);
            };
            let lambda = target_y.add(y).mul(inverse, irr);
            let x3 = lambda
                .square(irr)
                .add(&lambda)
                .add(target_x)
                .add(x)
                .add(&curve.curve.a);
            let y3 = lambda.mul(&target_x.add(&x3), irr).add(&x3).add(target_y);
            BinaryPoint::Affine { x: x3, y: y3 }
        })
        .collect()
}

fn batch_target_minus_keys(
    curve: &KoblitzCurve,
    target: &BinaryPoint,
    points: &[BinaryPoint],
) -> Vec<(u64, u64)> {
    let Some((target_x, target_y)) = raw_affine(target) else {
        return points
            .iter()
            .map(|point| {
                let (x, y) = raw_affine(point).expect("factor-base points are affine");
                (x + 1, y ^ x)
            })
            .collect();
    };
    let raw_points: Vec<_> = points
        .iter()
        .map(|point| raw_affine(point).expect("factor-base points are affine"))
        .collect();
    let mut denominators = vec![0u64; points.len()];
    let mut prefixes = vec![0u64; points.len()];
    let mut product = 1u64;
    for (index, &(x, _)) in raw_points.iter().enumerate() {
        let denominator = target_x ^ x;
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    let mut inverses = vec![0u64; points.len()];
    for index in (0..points.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = mul_raw(curve, inverse_product, prefixes[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
    }
    raw_points
        .iter()
        .enumerate()
        .map(|(index, &(x, y))| {
            if denominators[index] == 0 {
                return compact_point_key(&curve.add(target, &point_neg(&points[index])));
            }
            let negative_y = y ^ x;
            let lambda = mul_raw(curve, target_y ^ negative_y, inverses[index]);
            let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ x ^ (curve.a as u64);
            let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
            (x3 + 1, y3)
        })
        .collect()
}

fn batch_raw_target_minus_keys(
    curve: &KoblitzCurve,
    target: RawPoint,
    points: &[RawPoint],
) -> Vec<(u64, u64)> {
    let Some((target_x, target_y)) = target else {
        return points
            .iter()
            .map(|&point| raw_compact_key(raw_neg_point(point)))
            .collect();
    };
    let mut denominators = vec![0u64; points.len()];
    let mut prefixes = vec![0u64; points.len()];
    let mut product = 1u64;
    for (index, point) in points.iter().enumerate() {
        let (x, _) = point.expect("factor-base points are affine");
        let denominator = target_x ^ x;
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    let mut inverses = vec![0u64; points.len()];
    for index in (0..points.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = mul_raw(curve, inverse_product, prefixes[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
    }
    points
        .iter()
        .enumerate()
        .map(|(index, point)| {
            let (x, y) = (*point).unwrap();
            if denominators[index] == 0 {
                return raw_compact_key(raw_add_point(curve, target, raw_neg_point(*point)));
            }
            let lambda = mul_raw(curve, target_y ^ y ^ x, inverses[index]);
            let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ x ^ curve.a as u64;
            let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
            (x3 + 1, y3)
        })
        .collect()
}

#[derive(Default)]
struct RawBatchScratch {
    denominators: Vec<u64>,
    prefixes_and_inverses: Vec<u64>,
}

fn batch_raw_target_minus_points_x_filtered(
    curve: &KoblitzCurve,
    target: RawPoint,
    points: &[RawPoint],
    table: &CompactPairTable,
    output: &mut Vec<(usize, (u64, u64))>,
    scratch: &mut RawBatchScratch,
) -> usize {
    assert!(table.x_only);
    output.clear();
    let Some((target_x, target_y)) = target else {
        for (index, &point) in points.iter().enumerate() {
            let key = raw_compact_key(raw_neg_point(point));
            if table.might_contain_x(key.0) {
                output.push((index, key));
            }
        }
        return points.len();
    };
    scratch.denominators.resize(points.len(), 0);
    scratch.prefixes_and_inverses.resize(points.len(), 0);
    let mut product = 1u64;
    for (index, point) in points.iter().enumerate() {
        let denominator = point.map(|(x, _)| target_x ^ x).unwrap_or(0);
        scratch.denominators[index] = denominator;
        if denominator != 0 {
            scratch.prefixes_and_inverses[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    for index in (0..points.len()).rev() {
        let denominator = scratch.denominators[index];
        if denominator == 0 {
            continue;
        }
        let inverse = mul_raw(curve, inverse_product, scratch.prefixes_and_inverses[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
        scratch.prefixes_and_inverses[index] = inverse;
    }
    for (index, &point) in points.iter().enumerate() {
        let Some((x, y)) = point else {
            let key = raw_compact_key(target);
            if table.might_contain_x(key.0) {
                output.push((index, key));
            }
            continue;
        };
        if scratch.denominators[index] == 0 {
            let key = raw_compact_key(raw_add_point(curve, target, raw_neg_point(point)));
            if table.might_contain_x(key.0) {
                output.push((index, key));
            }
            continue;
        }
        let lambda = mul_raw(
            curve,
            target_y ^ y ^ x,
            scratch.prefixes_and_inverses[index],
        );
        let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ x ^ curve.a as u64;
        let key_x = x3 + 1;
        if !table.might_contain_x(key_x) {
            continue;
        }
        let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
        output.push((index, (key_x, y3)));
    }
    points.len()
}

/// Compute both `target - point` and `target - (-point)` while sharing the
/// denominator product and inverse for the two signs of every affine point.
/// Results retain positive-then-negative order for each input point. Infinity
/// has only one sign, matching `CompactPairTable::signed_point_at_slot`.
fn batch_raw_target_minus_signed_points_x_filtered(
    curve: &KoblitzCurve,
    target: RawPoint,
    points: &[RawPoint],
    table: &CompactPairTable,
    output: &mut Vec<(usize, bool, (u64, u64))>,
    scratch: &mut RawBatchScratch,
) -> usize {
    assert!(table.x_only);
    output.clear();
    let Some((target_x, target_y)) = target else {
        let mut attempted = 0usize;
        for (index, &point) in points.iter().enumerate() {
            let positive_key = raw_compact_key(raw_neg_point(point));
            attempted += 1;
            if table.might_contain_x(positive_key.0) {
                output.push((index, false, positive_key));
            }
            if point.is_some() {
                let negative_key = raw_compact_key(point);
                attempted += 1;
                if table.might_contain_x(negative_key.0) {
                    output.push((index, true, negative_key));
                }
            }
        }
        return attempted;
    };

    scratch.denominators.resize(points.len(), 0);
    scratch.prefixes_and_inverses.resize(points.len(), 0);
    let mut product = 1u64;
    for (index, point) in points.iter().enumerate() {
        let denominator = point.map(|(x, _)| target_x ^ x).unwrap_or(0);
        scratch.denominators[index] = denominator;
        if denominator != 0 {
            scratch.prefixes_and_inverses[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    for index in (0..points.len()).rev() {
        let denominator = scratch.denominators[index];
        if denominator == 0 {
            continue;
        }
        let inverse = mul_raw(curve, inverse_product, scratch.prefixes_and_inverses[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
        scratch.prefixes_and_inverses[index] = inverse;
    }

    let mut attempted = 0usize;
    for (index, &point) in points.iter().enumerate() {
        let Some((x, y)) = point else {
            let key = raw_compact_key(target);
            attempted += 1;
            if table.might_contain_x(key.0) {
                output.push((index, false, key));
            }
            continue;
        };
        if scratch.denominators[index] == 0 {
            for (negative, left) in [(false, point), (true, raw_neg_point(point))] {
                let key = raw_compact_key(raw_add_point(curve, target, raw_neg_point(left)));
                attempted += 1;
                if table.might_contain_x(key.0) {
                    output.push((index, negative, key));
                }
            }
            continue;
        }

        let inverse = scratch.prefixes_and_inverses[index];
        for (negative, numerator) in [(false, target_y ^ y ^ x), (true, target_y ^ y)] {
            let lambda = mul_raw(curve, numerator, inverse);
            let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ x ^ curve.a as u64;
            let key_x = x3 + 1;
            attempted += 1;
            if !table.might_contain_x(key_x) {
                continue;
            }
            let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
            output.push((index, negative, (key_x, y3)));
        }
    }
    attempted
}

/// Dual-sign batch inversion over compact `(x + 1, y)` points. This is the
/// same exact computation as `batch_raw_target_minus_signed_points_x_filtered`
/// without carrying a 24-byte `Option<(u64, u64)>` through every scratch pass.
fn batch_compact_target_minus_signed_points_x_filtered(
    curve: &KoblitzCurve,
    target: RawPoint,
    points: &[(u64, u64)],
    table: &CompactPairTable,
    output: &mut Vec<(usize, bool, (u64, u64))>,
    scratch: &mut RawBatchScratch,
) -> usize {
    assert!(table.x_only);
    output.clear();
    let Some((target_x, target_y)) = target else {
        let mut attempted = 0usize;
        for (index, &(key_x, y)) in points.iter().enumerate() {
            if key_x == 0 {
                attempted += 1;
                if table.might_contain_x(0) {
                    output.push((index, false, (0, 0)));
                }
                continue;
            }
            let x = key_x - 1;
            attempted += 1;
            if table.might_contain_x(key_x) {
                output.push((index, false, (key_x, y ^ x)));
            }
            attempted += 1;
            if table.might_contain_x(key_x) {
                output.push((index, true, (key_x, y)));
            }
        }
        return attempted;
    };

    scratch.denominators.resize(points.len(), 0);
    scratch.prefixes_and_inverses.resize(points.len(), 0);
    let mut product = 1u64;
    for (index, &(key_x, _)) in points.iter().enumerate() {
        let denominator = if key_x == 0 {
            0
        } else {
            target_x ^ (key_x - 1)
        };
        scratch.denominators[index] = denominator;
        if denominator != 0 {
            scratch.prefixes_and_inverses[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    for index in (0..points.len()).rev() {
        let denominator = scratch.denominators[index];
        if denominator == 0 {
            continue;
        }
        let inverse = mul_raw(curve, inverse_product, scratch.prefixes_and_inverses[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
        scratch.prefixes_and_inverses[index] = inverse;
    }

    let mut attempted = 0usize;
    for (index, &(key_x, y)) in points.iter().enumerate() {
        if key_x == 0 {
            let key = raw_compact_key(target);
            attempted += 1;
            if table.might_contain_x(key.0) {
                output.push((index, false, key));
            }
            continue;
        }
        let x = key_x - 1;
        if scratch.denominators[index] == 0 {
            let point = Some((x, y));
            for (negative, left) in [(false, point), (true, raw_neg_point(point))] {
                let key = raw_compact_key(raw_add_point(curve, target, raw_neg_point(left)));
                attempted += 1;
                if table.might_contain_x(key.0) {
                    output.push((index, negative, key));
                }
            }
            continue;
        }

        let inverse = scratch.prefixes_and_inverses[index];
        for (negative, numerator) in [(false, target_y ^ y ^ x), (true, target_y ^ y)] {
            let lambda = mul_raw(curve, numerator, inverse);
            let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ x ^ curve.a as u64;
            let rest_x = x3 + 1;
            attempted += 1;
            if !table.might_contain_x(rest_x) {
                continue;
            }
            let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
            output.push((index, negative, (rest_x, y3)));
        }
    }
    attempted
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn inverse_n53_binary_unchecked(value: u64) -> u64 {
    debug_assert_ne!(value, 0);
    const EXPONENT: u64 = (1u64 << 53) - 2;
    let mut result = 1u64;
    let mut base = value;
    for bit in 0..53 {
        if (EXPONENT >> bit) & 1 == 1 {
            result = unsafe { pclmul_reduce_n53(result, base) };
        }
        base = unsafe { pclmul_reduce_n53(base, base) };
    }
    result
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn frobenius_power_n53_unchecked(mut value: u64, squarings: u32) -> u64 {
    for _ in 0..squarings {
        value = unsafe { pclmul_reduce_n53(value, value) };
    }
    value
}

/// Itoh--Tsujii inversion for GF(2^53). The addition chain
/// 1,2,4,8,16,32,48,52 computes x^(2^52-1), followed by one square.
/// This uses 52 squarings and seven general multiplications instead of the
/// binary method's 53 squarings and 52 general multiplications.
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn inverse_n53_itoh_unchecked(value: u64) -> u64 {
    debug_assert_ne!(value, 0);
    let beta_1 = value;
    let beta_2 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_1, 1), beta_1) };
    let beta_4 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_2, 2), beta_2) };
    let beta_8 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_4, 4), beta_4) };
    let beta_16 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_8, 8), beta_8) };
    let beta_32 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_16, 16), beta_16) };
    let beta_48 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_32, 16), beta_16) };
    let beta_52 = unsafe { pclmul_reduce_n53(frobenius_power_n53_unchecked(beta_48, 4), beta_4) };
    unsafe { pclmul_reduce_n53(beta_52, beta_52) }
}

fn itoh_n53_inverse_enabled() -> bool {
    use std::sync::OnceLock;
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var("KIC_DISABLE_ITOH_N53_INVERSE").as_deref() != Ok("1"))
}

fn prefiltered_exact_lookup_enabled() -> bool {
    use std::sync::OnceLock;
    static ENABLED: OnceLock<bool> = OnceLock::new();
    *ENABLED
        .get_or_init(|| std::env::var("KIC_DISABLE_PREFILTERED_EXACT_LOOKUP").as_deref() != Ok("1"))
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn inverse_n53_selected_unchecked(value: u64) -> u64 {
    if itoh_n53_inverse_enabled() {
        unsafe { inverse_n53_itoh_unchecked(value) }
    } else {
        unsafe { inverse_n53_binary_unchecked(value) }
    }
}

/// Degree-53 PCLMUL specialization of the compact dual-sign batch. The caller
/// checks the combined runtime predicate once per chunk; no feature dispatch
/// remains inside the field-operation loops.
#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn batch_compact_n53_target_minus_signed_points_x_filtered(
    curve: &KoblitzCurve,
    target: RawPoint,
    points: &[(u64, u64)],
    table: &CompactPairTable,
    output: &mut Vec<(usize, bool, (u64, u64))>,
    scratch: &mut RawBatchScratch,
) -> usize {
    debug_assert_eq!(curve.n, 53);
    assert!(table.x_only);
    output.clear();
    let Some((target_x, target_y)) = target else {
        let mut attempted = 0usize;
        for (index, &(key_x, y)) in points.iter().enumerate() {
            if key_x == 0 {
                attempted += 1;
                if table.might_contain_x(0) {
                    output.push((index, false, (0, 0)));
                }
                continue;
            }
            let x = key_x - 1;
            attempted += 1;
            if table.might_contain_x(key_x) {
                output.push((index, false, (key_x, y ^ x)));
            }
            attempted += 1;
            if table.might_contain_x(key_x) {
                output.push((index, true, (key_x, y)));
            }
        }
        return attempted;
    };

    scratch.denominators.resize(points.len(), 0);
    scratch.prefixes_and_inverses.resize(points.len(), 0);
    let mut product = 1u64;
    for (index, &(key_x, _)) in points.iter().enumerate() {
        let denominator = if key_x == 0 {
            0
        } else {
            target_x ^ (key_x - 1)
        };
        scratch.denominators[index] = denominator;
        if denominator != 0 {
            scratch.prefixes_and_inverses[index] = product;
            product = unsafe { pclmul_reduce_n53(product, denominator) };
        }
    }
    let mut inverse_product = unsafe { inverse_n53_selected_unchecked(product) };
    for index in (0..points.len()).rev() {
        let denominator = scratch.denominators[index];
        if denominator == 0 {
            continue;
        }
        let inverse =
            unsafe { pclmul_reduce_n53(inverse_product, scratch.prefixes_and_inverses[index]) };
        inverse_product = unsafe { pclmul_reduce_n53(inverse_product, denominator) };
        scratch.prefixes_and_inverses[index] = inverse;
    }

    let mut attempted = 0usize;
    for (index, &(key_x, y)) in points.iter().enumerate() {
        if key_x == 0 {
            let key = raw_compact_key(target);
            attempted += 1;
            if table.might_contain_x(key.0) {
                output.push((index, false, key));
            }
            continue;
        }
        let x = key_x - 1;
        if scratch.denominators[index] == 0 {
            let point = Some((x, y));
            for (negative, left) in [(false, point), (true, raw_neg_point(point))] {
                let key = raw_compact_key(raw_add_point(curve, target, raw_neg_point(left)));
                attempted += 1;
                if table.might_contain_x(key.0) {
                    output.push((index, negative, key));
                }
            }
            continue;
        }

        let inverse = scratch.prefixes_and_inverses[index];
        for (negative, numerator) in [(false, target_y ^ y ^ x), (true, target_y ^ y)] {
            let lambda = unsafe { pclmul_reduce_n53(numerator, inverse) };
            let x3 = unsafe { pclmul_reduce_n53(lambda, lambda) }
                ^ lambda
                ^ target_x
                ^ x
                ^ curve.a as u64;
            let rest_x = x3 + 1;
            attempted += 1;
            if !table.might_contain_x(rest_x) {
                continue;
            }
            let y3 = unsafe { pclmul_reduce_n53(lambda, target_x ^ x3) } ^ x3 ^ target_y;
            output.push((index, negative, (rest_x, y3)));
        }
    }
    attempted
}

fn batch_raw_add_keys(curve: &KoblitzCurve, pairs: &[(RawPoint, RawPoint)]) -> Vec<(u64, u64)> {
    let mut denominators = vec![0u64; pairs.len()];
    let mut prefixes = vec![0u64; pairs.len()];
    let mut product = 1u64;
    for (index, &(left, right)) in pairs.iter().enumerate() {
        let denominator = match (left, right) {
            (Some((x1, _)), Some((x2, _))) if x1 != x2 => x1 ^ x2,
            _ => 0,
        };
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    let mut inverses = vec![0u64; pairs.len()];
    for index in (0..pairs.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = mul_raw(curve, inverse_product, prefixes[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
    }
    pairs
        .iter()
        .enumerate()
        .map(|(index, &(left, right))| {
            let (Some((x1, y1)), Some((x2, y2))) = (left, right) else {
                return raw_compact_key(raw_add_point(curve, left, right));
            };
            if denominators[index] == 0 {
                return raw_compact_key(raw_add_point(curve, left, right));
            }
            let lambda = mul_raw(curve, y1 ^ y2, inverses[index]);
            let x3 = square_raw(curve, lambda) ^ lambda ^ x1 ^ x2 ^ curve.a as u64;
            let y3 = mul_raw(curve, lambda, x1 ^ x3) ^ x3 ^ y1;
            (x3 + 1, y3)
        })
        .collect()
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn batch_raw_add_keys_n53(
    curve: &KoblitzCurve,
    pairs: &[(RawPoint, RawPoint)],
) -> Vec<(u64, u64)> {
    debug_assert_eq!(curve.n, 53);
    let mut denominators = vec![0u64; pairs.len()];
    let mut prefixes = vec![0u64; pairs.len()];
    let mut product = 1u64;
    for (index, &(left, right)) in pairs.iter().enumerate() {
        let denominator = match (left, right) {
            (Some((x1, _)), Some((x2, _))) if x1 != x2 => x1 ^ x2,
            _ => 0,
        };
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = unsafe { pclmul_reduce_n53(product, denominator) };
        }
    }
    let mut inverse_product = unsafe { inverse_n53_selected_unchecked(product) };
    let mut inverses = vec![0u64; pairs.len()];
    for index in (0..pairs.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = unsafe { pclmul_reduce_n53(inverse_product, prefixes[index]) };
        inverse_product = unsafe { pclmul_reduce_n53(inverse_product, denominator) };
    }
    pairs
        .iter()
        .enumerate()
        .map(|(index, &(left, right))| {
            let (Some((x1, y1)), Some((x2, y2))) = (left, right) else {
                return raw_compact_key(raw_add_point(curve, left, right));
            };
            if denominators[index] == 0 {
                return raw_compact_key(raw_add_point(curve, left, right));
            }
            let lambda = unsafe { pclmul_reduce_n53(y1 ^ y2, inverses[index]) };
            let x3 =
                unsafe { pclmul_reduce_n53(lambda, lambda) } ^ lambda ^ x1 ^ x2 ^ curve.a as u64;
            let y3 = unsafe { pclmul_reduce_n53(lambda, x1 ^ x3) } ^ x3 ^ y1;
            (x3 + 1, y3)
        })
        .collect()
}

fn batch_raw_add_keys_selected(
    curve: &KoblitzCurve,
    pairs: &[(RawPoint, RawPoint)],
    specialized_n53: bool,
) -> Vec<(u64, u64)> {
    if specialized_n53 && curve.n == 53 && combined_n53_fast_path_enabled() {
        #[cfg(target_arch = "x86_64")]
        {
            // SAFETY: the combined predicate includes the runtime PCLMUL
            // check and exact fused degree-53 reduction controls.
            return unsafe { batch_raw_add_keys_n53(curve, pairs) };
        }
    }
    batch_raw_add_keys(curve, pairs)
}

fn raw_fibers(points: &[RawPoint]) -> Vec<RawFiber> {
    let mut grouped: BTreeMap<u64, Vec<(usize, u64)>> = BTreeMap::new();
    for (index, point) in points.iter().enumerate() {
        let (x, y) = (*point).expect("factor-base points are affine");
        grouped.entry(x).or_default().push((index, y));
    }
    let mut fibers: Vec<_> = grouped
        .into_iter()
        .map(|(x, mut members)| {
            members.sort_unstable();
            RawFiber { x, members }
        })
        .collect();
    fibers.sort_by_key(|fiber| fiber.members[0].0);
    fibers
}

fn batch_raw_target_minus_fibers(
    curve: &KoblitzCurve,
    target: RawPoint,
    fibers: &[RawFiber],
    output: &mut Vec<(usize, (u64, u64))>,
) {
    assert!(fibers.len() <= 64);
    output.clear();
    let Some((target_x, target_y)) = target else {
        for fiber in fibers {
            for &(index, y) in &fiber.members {
                output.push((index, (fiber.x + 1, y ^ fiber.x)));
            }
        }
        return;
    };
    let mut denominators = [0u64; 64];
    let mut prefixes = [0u64; 64];
    let mut product = 1u64;
    for (index, fiber) in fibers.iter().enumerate() {
        let denominator = target_x ^ fiber.x;
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    let mut inverses = [0u64; 64];
    for index in (0..fibers.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = mul_raw(curve, inverse_product, prefixes[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
    }
    for (fiber_index, fiber) in fibers.iter().enumerate() {
        for &(point_index, y) in &fiber.members {
            let key = if denominators[fiber_index] == 0 {
                raw_compact_key(raw_add_point(
                    curve,
                    target,
                    raw_neg_point(Some((fiber.x, y))),
                ))
            } else {
                let lambda = mul_raw(curve, target_y ^ y ^ fiber.x, inverses[fiber_index]);
                let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ fiber.x ^ curve.a as u64;
                let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
                (x3 + 1, y3)
            };
            output.push((point_index, key));
        }
    }
    output.sort_by_key(|(index, _)| *index);
}

fn batch_raw_target_minus_fibers_x_filtered(
    curve: &KoblitzCurve,
    target: RawPoint,
    fibers: &[RawFiber],
    table: &CompactPairTable,
    output: &mut Vec<(usize, (u64, u64))>,
) -> usize {
    assert!(fibers.len() <= 64);
    assert!(table.x_only);
    output.clear();
    let attempted = fibers.iter().map(|fiber| fiber.members.len()).sum();
    let Some((target_x, target_y)) = target else {
        for fiber in fibers {
            for &(index, y) in &fiber.members {
                let key = (fiber.x + 1, y ^ fiber.x);
                if table.might_contain_x(key.0) {
                    output.push((index, key));
                }
            }
        }
        return attempted;
    };
    let mut denominators = [0u64; 64];
    let mut prefixes = [0u64; 64];
    let mut product = 1u64;
    for (index, fiber) in fibers.iter().enumerate() {
        let denominator = target_x ^ fiber.x;
        denominators[index] = denominator;
        if denominator != 0 {
            prefixes[index] = product;
            product = mul_raw(curve, product, denominator);
        }
    }
    let mut inverse_product = inverse_raw(curve, product);
    let mut inverses = [0u64; 64];
    for index in (0..fibers.len()).rev() {
        let denominator = denominators[index];
        if denominator == 0 {
            continue;
        }
        inverses[index] = mul_raw(curve, inverse_product, prefixes[index]);
        inverse_product = mul_raw(curve, inverse_product, denominator);
    }
    for (fiber_index, fiber) in fibers.iter().enumerate() {
        for &(point_index, y) in &fiber.members {
            if denominators[fiber_index] == 0 {
                let key = raw_compact_key(raw_add_point(
                    curve,
                    target,
                    raw_neg_point(Some((fiber.x, y))),
                ));
                if table.might_contain_x(key.0) {
                    output.push((point_index, key));
                }
                continue;
            }
            let lambda = mul_raw(curve, target_y ^ y ^ fiber.x, inverses[fiber_index]);
            let x3 = square_raw(curve, lambda) ^ lambda ^ target_x ^ fiber.x ^ curve.a as u64;
            let key_x = x3 + 1;
            if !table.might_contain_x(key_x) {
                continue;
            }
            let y3 = mul_raw(curve, lambda, target_x ^ x3) ^ x3 ^ target_y;
            output.push((point_index, (key_x, y3)));
        }
    }
    output.sort_by_key(|(index, _)| *index);
    attempted
}

fn frobenius_key_images(
    curve: &KoblitzCurve,
    key: (u64, u64),
    modulus: u64,
    lambda: u64,
) -> (Vec<((u64, u64), u64)>, usize) {
    if key.0 == 0 {
        return (vec![(key, 1)], 0);
    }
    let mut current_x = key.0 - 1;
    let mut current_y = key.1;
    let mut multiplier = 1u64;
    let mut images = Vec::with_capacity(curve.n as usize);
    for exponent in 0..curve.n {
        images.push(((current_x + 1, current_y), multiplier));
        if exponent + 1 < curve.n {
            current_x = square_raw(curve, current_x);
            current_y = square_raw(curve, current_y);
            multiplier = ((multiplier as u128 * lambda as u128) % modulus as u128) as u64;
        }
    }
    (images, curve.n.saturating_sub(1) as usize)
}

fn lookup_signed_expanded_pair(
    rest_key: (u64, u64),
    modulus: u64,
    quotient_pairs: &CompactPairTable,
    point_labels: &[(usize, u64)],
    label_to_index: &HashMap<(usize, u64), usize>,
    x_prefiltered: bool,
) -> Option<([usize; 2], [(usize, u64); 2])> {
    let pair = if x_prefiltered {
        quotient_pairs.get_after_x_filter(rest_key)
    } else {
        quotient_pairs.get(rest_key)
    };
    pair.map(|pair| {
        let stored_indices = pair.point_indices();
        let stored = stored_indices.map(|index| point_labels[index]);
        let image_y = pair.image_y;
        let (indices, labels) = if rest_key.1 == image_y {
            (stored_indices, stored)
        } else {
            let raw_x = rest_key.0.saturating_sub(1);
            assert_eq!(rest_key.1, image_y ^ raw_x);
            let labels = stored.map(|(column, coefficient)| {
                (
                    column,
                    if coefficient == 0 {
                        0
                    } else {
                        modulus - coefficient
                    },
                )
            });
            (labels.map(|label| label_to_index[&label]), labels)
        };
        (indices, labels)
    })
}

#[derive(Default)]
struct PairPairChunkScratch {
    points: Vec<RawPoint>,
    compact_points: Vec<(u64, u64)>,
    signed_slots: Vec<usize>,
    separate_rests: Vec<(usize, (u64, u64))>,
    dual_rests: Vec<(usize, bool, (u64, u64))>,
    batch: RawBatchScratch,
}

#[derive(Default)]
struct PairPairChunkResult {
    witness: Option<([usize; 4], [(usize, u64); 4])>,
    additions: usize,
    x_filter_rejections: usize,
    exact_table_misses: usize,
    batch_inversions: usize,
    shared_denominator_inputs: usize,
}

/// Evaluate one fixed cursor interval of the signed-expanded pair table.
/// Intervals are independent and their results are consumed in cursor order,
/// so a parallel wave returns the same earliest witness as a serial scan.
fn pair_pair_cursor_chunk(
    curve: &KoblitzCurve,
    target: RawPoint,
    quotient_pairs: &CompactPairTable,
    point_labels: &[(usize, u64)],
    label_to_index: &HashMap<(usize, u64), usize>,
    modulus: u64,
    slot_order: Option<&[u32]>,
    start_slot: usize,
    cursor_start: usize,
    cursor_end: usize,
    dual_sign: bool,
    compact_scratch: bool,
    specialized_n53_batch: bool,
    scratch: &mut PairPairChunkScratch,
) -> PairPairChunkResult {
    let slots = quotient_pairs.slots();
    scratch.points.clear();
    scratch.compact_points.clear();
    scratch.signed_slots.clear();
    let step = if dual_sign { 2 } else { 1 };
    if dual_sign {
        assert_eq!(cursor_start & 1, 0);
        assert_eq!(cursor_end & 1, 0);
    }
    if compact_scratch && dual_sign {
        scratch
            .compact_points
            .reserve((cursor_end - cursor_start) / step);
    } else {
        scratch.points.reserve((cursor_end - cursor_start) / step);
    }
    scratch
        .signed_slots
        .reserve((cursor_end - cursor_start) / step);
    for cursor in (cursor_start..cursor_end).step_by(step) {
        let slot = if let Some(order) = slot_order {
            let ordered = start_slot + cursor / 2;
            order[if ordered >= order.len() {
                ordered - order.len()
            } else {
                ordered
            }] as usize
        } else {
            (start_slot + cursor / 2) & (slots - 1)
        };
        let negative = !dual_sign && cursor & 1 == 1;
        let occupied = if compact_scratch && dual_sign {
            quotient_pairs.compact_point_at_slot(slot).map(|point| {
                scratch.compact_points.push(point);
            })
        } else {
            quotient_pairs
                .signed_point_at_slot(slot, negative)
                .map(|point| {
                    scratch.points.push(point);
                })
        };
        if occupied.is_some() {
            scratch.signed_slots.push(slot << 1 | usize::from(negative));
        }
    }
    if scratch.points.is_empty() && scratch.compact_points.is_empty() {
        return PairPairChunkResult::default();
    }
    let use_specialized_n53_batch = dual_sign
        && compact_scratch
        && specialized_n53_batch
        && curve.n == 53
        && combined_n53_fast_path_enabled();
    let attempted = if use_specialized_n53_batch {
        #[cfg(target_arch = "x86_64")]
        {
            // SAFETY: the combined predicate includes the runtime PCLMUL
            // feature check and the exact fused degree-53 reduction controls.
            unsafe {
                batch_compact_n53_target_minus_signed_points_x_filtered(
                    curve,
                    target,
                    &scratch.compact_points,
                    quotient_pairs,
                    &mut scratch.dual_rests,
                    &mut scratch.batch,
                )
            }
        }
        #[cfg(not(target_arch = "x86_64"))]
        {
            unreachable!("the specialized n53 batch is x86_64-only")
        }
    } else if dual_sign && compact_scratch {
        batch_compact_target_minus_signed_points_x_filtered(
            curve,
            target,
            &scratch.compact_points,
            quotient_pairs,
            &mut scratch.dual_rests,
            &mut scratch.batch,
        )
    } else if dual_sign {
        batch_raw_target_minus_signed_points_x_filtered(
            curve,
            target,
            &scratch.points,
            quotient_pairs,
            &mut scratch.dual_rests,
            &mut scratch.batch,
        )
    } else {
        batch_raw_target_minus_points_x_filtered(
            curve,
            target,
            &scratch.points,
            quotient_pairs,
            &mut scratch.separate_rests,
            &mut scratch.batch,
        )
    };
    let filtered_hits = if dual_sign {
        scratch.dual_rests.len()
    } else {
        scratch.separate_rests.len()
    };
    let mut result = PairPairChunkResult {
        additions: attempted,
        x_filter_rejections: attempted - filtered_hits,
        batch_inversions: usize::from(target.is_some()),
        shared_denominator_inputs: if dual_sign {
            if compact_scratch {
                scratch.compact_points.len()
            } else {
                scratch.points.len()
            }
        } else {
            0
        },
        ..PairPairChunkResult::default()
    };
    let mut consume = |position: usize, negative: bool, rest_key: (u64, u64)| {
        let Some((right_indices, right_labels)) = lookup_signed_expanded_pair(
            rest_key,
            modulus,
            quotient_pairs,
            point_labels,
            label_to_index,
            prefiltered_exact_lookup_enabled(),
        ) else {
            result.exact_table_misses += 1;
            return false;
        };
        let signed_slot = scratch.signed_slots[position];
        let negative = negative ^ (signed_slot & 1 == 1);
        let (left_indices, left_labels) = quotient_pairs.signed_labels_at_slot(
            signed_slot >> 1,
            negative,
            modulus,
            point_labels,
            label_to_index,
        );
        result.witness = Some((
            [
                left_indices[0],
                left_indices[1],
                right_indices[0],
                right_indices[1],
            ],
            [
                left_labels[0],
                left_labels[1],
                right_labels[0],
                right_labels[1],
            ],
        ));
        true
    };
    if dual_sign {
        for &(position, negative, rest_key) in &scratch.dual_rests {
            if consume(position, negative, rest_key) {
                break;
            }
        }
    } else {
        for &(position, rest_key) in &scratch.separate_rests {
            if consume(position, false, rest_key) {
                break;
            }
        }
    }
    result
}

fn lookup_pair_witness(
    pair_mode: PairMode,
    curve: &KoblitzCurve,
    rest_key: (u64, u64),
    right: usize,
    modulus: u64,
    lambda: u64,
    base: &Base,
    full_pairs: &HashMap<(u64, u64), (usize, usize)>,
    quotient_pairs: &CompactPairTable,
    label_to_index: &HashMap<(usize, u64), usize>,
) -> (Option<([usize; 3], [(usize, u64); 3])>, usize) {
    match pair_mode {
        PairMode::Full => {
            let witness = full_pairs.get(&rest_key).map(|&(left, middle)| {
                let indices = [left, middle, right];
                let labels = indices.map(|index| base.point_labels[index]);
                (indices, labels)
            });
            (witness, 0)
        }
        PairMode::SignedQuotient => {
            let (key, multiplier, maps) = canonical_signed_key(curve, rest_key, modulus, lambda);
            let witness = quotient_pairs.get(key).map(|pair| {
                let stored = pair.labels();
                let inverse = modpow(multiplier, modulus - 2, modulus);
                let left_label = (
                    stored[0].0,
                    ((stored[0].1 as u128 * inverse as u128) % modulus as u128) as u64,
                );
                let middle_label = (
                    stored[1].0,
                    ((stored[1].1 as u128 * inverse as u128) % modulus as u128) as u64,
                );
                let labels = [left_label, middle_label, base.point_labels[right]];
                let indices = labels.map(|label| label_to_index[&label]);
                (indices, labels)
            });
            (witness, maps)
        }
        PairMode::SignedExpanded => {
            let witness = lookup_signed_expanded_pair(
                rest_key,
                modulus,
                quotient_pairs,
                &base.point_labels,
                label_to_index,
                false,
            )
            .map(|(pair_indices, pair_labels)| {
                let labels = [pair_labels[0], pair_labels[1], base.point_labels[right]];
                let indices = [pair_indices[0], pair_indices[1], right];
                (indices, labels)
            });
            (witness, 0)
        }
    }
}

fn raw_trace_bit(curve: &KoblitzCurve, value: u64) -> bool {
    let mut trace = 0u64;
    let mut power = value;
    for _ in 0..curve.n {
        trace ^= power;
        power = square_raw(curve, power);
    }
    assert!(trace == 0 || trace == 1);
    trace == 1
}

fn raw_points_with_x(curve: &KoblitzCurve, x: u64) -> Vec<RawPoint> {
    if x == 0 {
        return vec![Some((0, 1))];
    }
    let inverse_x = inverse_raw(curve, x);
    let rhs = x ^ curve.a as u64 ^ square_raw(curve, inverse_x);
    if raw_trace_bit(curve, rhs) {
        return Vec::new();
    }
    let mut half_trace = 0u64;
    let mut power = rhs;
    for _ in 0..=(curve.n - 1) / 2 {
        half_trace ^= power;
        power = square_raw(curve, square_raw(curve, power));
    }
    assert_eq!(square_raw(curve, half_trace) ^ half_trace, rhs);
    let y = mul_raw(curve, x, half_trace);
    vec![Some((x, y)), Some((x, y ^ x))]
}

fn raw_signed_orbit(curve: &KoblitzCurve, point: RawPoint) -> Vec<RawPoint> {
    let mut by_key = BTreeMap::new();
    let mut current = point;
    for _ in 0..curve.n {
        by_key.entry(raw_compact_key(current)).or_insert(current);
        let negative = raw_neg_point(current);
        by_key.entry(raw_compact_key(negative)).or_insert(negative);
        current = current.map(|(x, y)| (square_raw(curve, x), square_raw(curve, y)));
    }
    by_key.into_values().collect()
}

fn binary_from_raw(curve: &KoblitzCurve, point: RawPoint) -> BinaryPoint {
    match point {
        None => BinaryPoint::Infinity,
        Some((x, y)) => BinaryPoint::Affine {
            x: F2mElement::from_biguint(&BigUint::from(x), curve.n),
            y: F2mElement::from_biguint(&BigUint::from(y), curve.n),
        },
    }
}

fn point_defined_base(curve: &KoblitzCurve, wanted: usize) -> Base {
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let lambda = curve.lambda.to_u64().unwrap();
    let signed_size = signed_scalars(lambda, modulus, curve.n).len();
    let cofactor_two = curve.cofactor == BigUint::from(2u8);
    let cofactor = curve.cofactor.to_u64().unwrap();
    let mut accepted: Vec<Vec<RawPoint>> = Vec::new();
    let mut seen_orbits = HashSet::new();
    let mut scanned_x = 0u64;
    let mask = if curve.n >= 64 {
        u64::MAX
    } else {
        (1u64 << curve.n) - 1
    };
    // Exhaustive affine order is fine on small fields; past ~32 bits a
    // full `2^n` walk is impossible, so draw abscissae from a fixed LCG.
    let exhaustive = curve.n <= 32;
    let budget = if exhaustive {
        1u64 << curve.n
    } else {
        1u64 << 24
    };
    let mut state = 0xD1B54A32D192ED03u64 ^ (curve.n as u64) ^ ((wanted as u64) << 17);
    for i in 0..budget {
        let x = if exhaustive {
            i
        } else {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            state & mask
        };
        scanned_x += 1;
        for point in raw_points_with_x(curve, x) {
            let subgroup_point = if cofactor_two {
                if raw_trace_bit(curve, x) ^ (curve.a == 1) {
                    None
                } else {
                    point
                }
            } else {
                raw_scalar_point(curve, point, cofactor)
            };
            if subgroup_point.is_none() {
                continue;
            }
            let orbit = raw_signed_orbit(curve, subgroup_point);
            let canonical = raw_compact_key(orbit[0]);
            if !seen_orbits.insert(canonical) {
                continue;
            }
            accepted.push(orbit);
            if accepted.len() == wanted {
                break;
            }
        }
        if accepted.len() == wanted {
            break;
        }
    }
    assert_eq!(
        accepted.len(),
        wanted,
        "failed to collect {wanted} orbits at n={} after {scanned_x} abscissae",
        curve.n
    );
    accepted.sort_by_key(|orbit| raw_compact_key(orbit[0]));
    let mut points = Vec::new();
    let mut point_labels = Vec::new();
    let mut representatives = Vec::new();
    for (column, orbit) in accepted.into_iter().enumerate() {
        let representative = orbit[0];
        representatives.push(binary_from_raw(curve, representative));
        let mut labels = HashMap::new();
        let mut current = representative;
        let mut coefficient = 1u64;
        for _ in 0..curve.n {
            labels
                .entry(raw_compact_key(current))
                .or_insert(coefficient);
            labels
                .entry(raw_compact_key(raw_neg_point(current)))
                .or_insert(modulus - coefficient);
            current = current.map(|(x, y)| (square_raw(curve, x), square_raw(curve, y)));
            coefficient = ((coefficient as u128 * lambda as u128) % modulus as u128) as u64;
        }
        assert_eq!(labels.len(), orbit.len());
        for member in orbit {
            points.push(binary_from_raw(curve, member));
            point_labels.push((column, labels[&raw_compact_key(member)]));
        }
    }
    Base {
        points,
        point_labels,
        representatives,
        scanned_x,
        signed_size,
        point_selection: if cofactor_two {
            "first admissible signed Frobenius orbits in affine coordinate order"
        } else {
            "small-cofactor projections of the first affine curve points in coordinate order"
        },
    }
}

fn reference_point_defined_base(curve: &KoblitzCurve, wanted: usize) -> Base {
    let modulus = curve.subgroup_order.to_u64().unwrap();
    let lambda = curve.lambda.to_u64().unwrap();
    let signed_size = signed_scalars(lambda, modulus, curve.n).len();
    let field_size = 1u64 << curve.n;
    let cofactor_two = curve.cofactor == BigUint::from(2u8);
    let mut accepted: Vec<Vec<BinaryPoint>> = Vec::new();
    let mut seen_orbits = HashSet::new();
    let mut scanned_x = 0u64;

    for raw_x in 0..field_size {
        scanned_x += 1;
        let x = F2mElement::from_biguint(&BigUint::from(raw_x), curve.n);
        let rational = points_with_x(&curve.curve, &x);
        for point in rational {
            let in_subgroup = if cofactor_two {
                !(absolute_trace_bit(curve, &x) ^ (curve.a == 1))
            } else {
                curve.mul(&point, &curve.subgroup_order) == BinaryPoint::Infinity
            };
            if point == BinaryPoint::Infinity || !in_subgroup {
                continue;
            }
            let orbit = signed_point_orbit(curve, &point);
            let canonical = point_key(&orbit[0]);
            if !seen_orbits.insert(canonical) {
                continue;
            }
            if !cofactor_two {
                assert_eq!(
                    curve.mul(&point, &curve.subgroup_order),
                    BinaryPoint::Infinity,
                );
            }
            accepted.push(orbit);
            if accepted.len() == wanted {
                break;
            }
        }
        if accepted.len() == wanted {
            break;
        }
    }
    assert_eq!(
        accepted.len(),
        wanted,
        "field scan did not find enough subgroup orbits"
    );

    accepted.sort_by_key(|orbit| point_key(&orbit[0]));
    let mut points = Vec::new();
    let mut point_labels = Vec::new();
    let mut representatives = Vec::new();
    for (column, orbit) in accepted.into_iter().enumerate() {
        let representative = orbit[0].clone();
        representatives.push(representative.clone());
        let mut labels = HashMap::new();
        let mut current = representative;
        let mut coefficient = 1u64;
        for _ in 0..curve.n {
            labels.entry(point_key(&current)).or_insert(coefficient);
            labels
                .entry(point_key(&point_neg(&current)))
                .or_insert((modulus - coefficient) % modulus);
            current = curve.frobenius(&current);
            coefficient = ((coefficient as u128 * lambda as u128) % modulus as u128) as u64;
        }
        assert_eq!(labels.len(), orbit.len());
        for member in orbit {
            points.push(member.clone());
            point_labels.push((column, labels[&point_key(&member)]));
        }
    }
    let keys: HashSet<_> = points.iter().map(point_key).collect();
    assert_eq!(keys.len(), points.len());
    assert!(points.iter().all(|point| {
        keys.contains(&point_key(&curve.frobenius(point)))
            && keys.contains(&point_key(&point_neg(point)))
    }));
    Base {
        points,
        point_labels,
        representatives,
        scanned_x,
        signed_size,
        point_selection: "first admissible signed Frobenius orbits in affine coordinate order",
    }
}

impl Echelon {
    fn new(columns: usize) -> Self {
        Self {
            pivots: vec![None; columns],
            rank: 0,
        }
    }

    fn insert(&mut self, mut row: Vec<u64>, modulus: u64) -> bool {
        for column in 0..row.len() {
            if row[column] == 0 {
                continue;
            }
            if let Some(pivot) = &self.pivots[column] {
                let factor = row[column];
                for index in column..row.len() {
                    let product =
                        ((factor as u128 * pivot[index] as u128) % modulus as u128) as u64;
                    row[index] = if row[index] >= product {
                        row[index] - product
                    } else {
                        modulus - (product - row[index])
                    };
                }
                continue;
            }
            let inverse = modpow(row[column], modulus - 2, modulus);
            for value in &mut row[column..] {
                *value = ((*value as u128 * inverse as u128) % modulus as u128) as u64;
            }
            self.pivots[column] = Some(row);
            self.rank += 1;
            return true;
        }
        false
    }
}

impl ReverseEchelon {
    fn new(columns: usize) -> Self {
        Self {
            pivots: vec![None; columns],
            rank: 0,
        }
    }

    fn insert(&mut self, mut row: Vec<u64>, modulus: u64) -> bool {
        for column in (0..row.len()).rev() {
            if row[column] == 0 {
                continue;
            }
            if let Some(pivot) = &self.pivots[column] {
                let factor = row[column];
                for index in 0..=column {
                    let product =
                        ((factor as u128 * pivot[index] as u128) % modulus as u128) as u64;
                    row[index] = if row[index] >= product {
                        row[index] - product
                    } else {
                        modulus - (product - row[index])
                    };
                }
                continue;
            }
            let inverse = modpow(row[column], modulus - 2, modulus);
            for value in &mut row[..=column] {
                *value = ((*value as u128 * inverse as u128) % modulus as u128) as u64;
            }
            self.pivots[column] = Some(row);
            self.rank += 1;
            return true;
        }
        false
    }
}

fn dense_rank(input: &[Vec<u64>], columns: usize, modulus: u64) -> usize {
    let mut matrix = input.to_vec();
    let mut rank = 0usize;
    for column in 0..columns {
        let Some(pivot) = (rank..matrix.len()).find(|&row| matrix[row][column] != 0) else {
            continue;
        };
        matrix.swap(rank, pivot);
        let inverse = modpow(matrix[rank][column], modulus - 2, modulus);
        for index in column..columns {
            matrix[rank][index] =
                ((matrix[rank][index] as u128 * inverse as u128) % modulus as u128) as u64;
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
            assert_eq!(row.len(), columns);
            let mut augmented = row.clone();
            augmented.push(rhs);
            augmented
        })
        .collect();
    let mut pivot_row = 0usize;
    for column in 0..columns {
        let pivot = (pivot_row..matrix.len()).find(|&row| matrix[row][column] != 0)?;
        matrix.swap(pivot_row, pivot);
        let inverse = modpow(matrix[pivot_row][column], modulus - 2, modulus);
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

type PairExpansionJob = (usize, usize, u64, usize, usize);
type ExpandedSupportEntry = ((u64, u64), [usize; 2]);

fn expand_support_batch(
    curve: &KoblitzCurve,
    jobs: &[PairExpansionJob],
    sum_keys: &[(u64, u64)],
    frobenius_next_index: &[usize],
    job_chunk: usize,
) -> Vec<(Vec<ExpandedSupportEntry>, usize)> {
    jobs.par_chunks(job_chunk)
        .zip(sum_keys.par_chunks(job_chunk))
        .map(|(job_chunk, key_chunk)| {
            let mut entries = Vec::with_capacity(job_chunk.len() * curve.n as usize);
            let mut maps = 0usize;
            for (&(_, _, _, left, right), &key) in job_chunk.iter().zip(key_chunk) {
                let mut image_key = key;
                let mut image_indices = [left, right];
                for exponent in 0..curve.n {
                    entries.push((image_key, image_indices));
                    if exponent + 1 < curve.n && image_key.0 != 0 {
                        let x = square_raw(curve, image_key.0 - 1);
                        let y = square_raw(curve, image_key.1);
                        image_key = (x + 1, y);
                        image_indices = image_indices.map(|index| frobenius_next_index[index]);
                        maps += 1;
                    }
                }
            }
            (entries, maps)
        })
        .collect()
}

#[cfg(target_arch = "x86_64")]
#[target_feature(enable = "pclmulqdq")]
unsafe fn expand_support_batch_n53(
    curve: &KoblitzCurve,
    jobs: &[PairExpansionJob],
    sum_keys: &[(u64, u64)],
    frobenius_next_index: &[usize],
    job_chunk: usize,
) -> Vec<(Vec<ExpandedSupportEntry>, usize)> {
    debug_assert_eq!(curve.n, 53);
    jobs.par_chunks(job_chunk)
        .zip(sum_keys.par_chunks(job_chunk))
        .map(|(job_chunk, key_chunk)| {
            let mut entries = Vec::with_capacity(job_chunk.len() * 53);
            let mut maps = 0usize;
            for (&(_, _, _, left, right), &key) in job_chunk.iter().zip(key_chunk) {
                let mut image_key = key;
                let mut image_indices = [left, right];
                for exponent in 0..53 {
                    entries.push((image_key, image_indices));
                    if exponent + 1 < 53 && image_key.0 != 0 {
                        let x = unsafe { pclmul_reduce_n53(image_key.0 - 1, image_key.0 - 1) };
                        let y = unsafe { pclmul_reduce_n53(image_key.1, image_key.1) };
                        image_key = (x + 1, y);
                        image_indices = image_indices.map(|index| frobenius_next_index[index]);
                        maps += 1;
                    }
                }
            }
            (entries, maps)
        })
        .collect()
}

fn expand_support_batch_selected(
    curve: &KoblitzCurve,
    jobs: &[PairExpansionJob],
    sum_keys: &[(u64, u64)],
    frobenius_next_index: &[usize],
    job_chunk: usize,
    specialized_n53: bool,
) -> Vec<(Vec<ExpandedSupportEntry>, usize)> {
    if specialized_n53 && curve.n == 53 && combined_n53_fast_path_enabled() {
        #[cfg(target_arch = "x86_64")]
        {
            // SAFETY: the combined predicate includes the runtime PCLMUL
            // check and exact fused degree-53 reduction controls.
            return unsafe {
                expand_support_batch_n53(curve, jobs, sum_keys, frobenius_next_index, job_chunk)
            };
        }
    }
    expand_support_batch(curve, jobs, sum_keys, frobenius_next_index, job_chunk)
}

fn main() {
    let arguments: Vec<_> = std::env::args().collect();
    assert!(
        (6..=11).contains(&arguments.len()),
        "usage: <n> <a> <eta_numerator> <eta_denominator> <seed> [full|signed_quotient|signed_expanded] [independent|coefficient_walk|partition_walk] [pointwise|batch_inverse_*|fiber_batch_*|pair_pair_*] [batch_fixtures] [explicit_fixture_scalar|hash:public_seed]"
    );
    let n: u32 = arguments[1].parse().unwrap();
    let a: u8 = arguments[2].parse().unwrap();
    let eta_numerator: u32 = arguments[3].parse().unwrap();
    let eta_denominator: u32 = arguments[4].parse().unwrap();
    let seed: u64 = arguments[5].parse().unwrap();
    let pair_mode = PairMode::parse(arguments.get(6).map(String::as_str).unwrap_or("full"));
    let target_mode = TargetMode::parse(
        arguments
            .get(7)
            .map(String::as_str)
            .unwrap_or("independent"),
    );
    let query_mode = QueryMode::parse(arguments.get(8).map(String::as_str).unwrap_or("pointwise"));
    let batch_fixtures: u64 = arguments
        .get(9)
        .map(String::as_str)
        .unwrap_or("1")
        .parse()
        .unwrap();
    let fixture_target = FixtureTarget::parse(arguments.get(10).map(String::as_str));
    let summary_only = std::env::var("KIC_SUMMARY_ONLY").as_deref() == Ok("1");
    let batch_corpus = std::env::var("KIC_BATCH_CORPUS").ok();
    let relation_cap_extra: usize = std::env::var("KIC_RELATION_CAP_EXTRA")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(0);
    let required_rank_surplus: usize = std::env::var("KIC_RANK_SURPLUS")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(32);
    let rank_aware_pair_scan = std::env::var("KIC_RANK_AWARE_PAIR_SCAN").as_deref() == Ok("1");
    let rank_target_deficiency: usize = std::env::var("KIC_RANK_TARGET_DEFICIENCY")
        .ok()
        .map(|value| value.parse().unwrap())
        .unwrap_or(1);
    let dual_sign_pair_scan =
        std::env::var("KIC_DISABLE_DUAL_SIGN_PAIR_SCAN").as_deref() != Ok("1");
    let compact_pair_scratch =
        std::env::var("KIC_DISABLE_COMPACT_PAIR_SCRATCH").as_deref() != Ok("1");
    let specialized_n53_pair_batch =
        std::env::var("KIC_DISABLE_SPECIALIZED_N53_PAIR_BATCH").as_deref() != Ok("1");
    let specialized_n53_support_expansion =
        std::env::var("KIC_ENABLE_SPECIALIZED_N53_SUPPORT_EXPANSION").as_deref() == Ok("1");
    let specialized_n53_pair_sums =
        std::env::var("KIC_ENABLE_SPECIALIZED_N53_PAIR_SUMS").as_deref() == Ok("1");
    let parallel_support_expansion =
        std::env::var("KIC_PARALLEL_SUPPORT_EXPANSION").as_deref() == Ok("1");
    let pipelined_support_expansion =
        std::env::var("KIC_PIPELINED_SUPPORT_EXPANSION").as_deref() == Ok("1");
    let incremental_rank_crosscheck =
        std::env::var("KIC_INCREMENTAL_RANK_CROSSCHECK").as_deref() == Ok("1");
    assert!(matches!(n, 7 | 11 | 13 | 17 | 19 | 23 | 37 | 41 | 53));
    assert!(eta_numerator > 0 && eta_denominator > 0);
    assert!(batch_fixtures > 0);
    assert!(!rank_aware_pair_scan || query_mode.pair_pair_parallel());
    assert!(rank_target_deficiency > 0);
    assert!(!parallel_support_expansion || pair_mode == PairMode::SignedExpanded);
    assert!(!pipelined_support_expansion || parallel_support_expansion);

    let curve_setup_started = Instant::now();
    let curve = KoblitzCurve::new(a, n).expect("frozen exact rung must construct");
    let curve_setup_ms = curve_setup_started.elapsed().as_secs_f64() * 1000.0;
    let setup_started = Instant::now();
    let modulus = curve.subgroup_order.to_u64().unwrap();
    if let FixtureTarget::ExplicitScalar(scalar) = fixture_target {
        assert!(
            batch_fixtures == 1,
            "an explicit scalar requires one fixture"
        );
        assert!(
            (1..modulus).contains(&scalar),
            "explicit scalar must be in 1..r"
        );
    }
    if matches!(fixture_target, FixtureTarget::PublicHash(_)) {
        assert!(
            batch_fixtures == 1,
            "a public hash target requires one fixture"
        );
    }
    let signed_size = signed_scalars(curve.lambda.to_u64().unwrap(), modulus, n).len();
    let columns = balanced_orbits(
        &curve.subgroup_order,
        signed_size,
        eta_numerator,
        eta_denominator,
    );
    let base_started = Instant::now();
    let base = point_defined_base(&curve, columns);
    let base_ms = base_started.elapsed().as_secs_f64() * 1000.0;
    let raw_base_points: Vec<_> = base.points.iter().map(to_raw_point).collect();
    let base_fibers = raw_fibers(&raw_base_points);

    let pair_started = Instant::now();
    let pair_types = columns * (columns + 1) / 2;
    let mut full_pairs = if pair_mode == PairMode::Full {
        HashMap::with_capacity(base.points.len() * (base.points.len() + 1) / 2)
    } else {
        HashMap::with_capacity(0)
    };
    let quotient_capacity = match pair_mode {
        PairMode::Full => 0,
        PairMode::SignedQuotient => pair_types * base.signed_size,
        PairMode::SignedExpanded => pair_types * base.signed_size * (base.signed_size / 2),
    };
    let mut quotient_pairs = CompactPairTable::with_capacity(
        quotient_capacity,
        pair_mode == PairMode::SignedExpanded,
        (1usize << n) + 1,
    );
    let mut pair_additions = 0usize;
    let mut pair_canonicalization_maps = 0usize;
    let mut pair_batch_inversions = 0usize;
    let lambda = curve.lambda.to_u64().unwrap();
    let label_to_index: HashMap<_, _> = base
        .point_labels
        .iter()
        .copied()
        .enumerate()
        .map(|(index, label)| (label, index))
        .collect();
    assert_eq!(label_to_index.len(), base.points.len());
    let frobenius_next_index: Vec<usize> = base
        .point_labels
        .iter()
        .map(|&(column, coefficient)| {
            let next = ((coefficient as u128 * lambda as u128) % modulus as u128) as u64;
            label_to_index[&(column, next)]
        })
        .collect();
    match pair_mode {
        PairMode::Full => {
            for left in 0..base.points.len() {
                for right in left..base.points.len() {
                    let sum = curve.add(&base.points[left], &base.points[right]);
                    full_pairs
                        .entry(compact_point_key(&sum))
                        .or_insert((left, right));
                    pair_additions += 1;
                }
            }
        }
        PairMode::SignedQuotient | PairMode::SignedExpanded => {
            let automorphisms: Vec<_> = signed_scalars(lambda, modulus, n).into_iter().collect();
            assert_eq!(automorphisms.len(), base.signed_size);
            let diagonal_relatives: Vec<_> = automorphisms
                .iter()
                .copied()
                .filter(|&value| value <= modpow(value, modulus - 2, modulus))
                .collect();
            let mut jobs: Vec<PairExpansionJob> = Vec::new();
            let mut operands = Vec::new();
            for left_column in 0..columns {
                let left = label_to_index[&(left_column, 1)];
                for right_column in left_column..columns {
                    let relatives = if left_column == right_column {
                        &diagonal_relatives
                    } else {
                        &automorphisms
                    };
                    for &relative in relatives {
                        let right = label_to_index[&(right_column, relative)];
                        jobs.push((left_column, right_column, relative, left, right));
                        operands.push((
                            to_raw_point(&base.points[left]),
                            to_raw_point(&base.points[right]),
                        ));
                    }
                }
            }
            let sum_keys =
                batch_raw_add_keys_selected(&curve, &operands, specialized_n53_pair_sums);
            pair_batch_inversions = usize::from(!sum_keys.is_empty());
            if parallel_support_expansion {
                const JOB_CHUNK: usize = 1_024;
                let job_batch = if pipelined_support_expansion {
                    32_768
                } else {
                    65_536
                };
                pair_additions += jobs.len();
                let mut consume = |expanded: Vec<(Vec<ExpandedSupportEntry>, usize)>| {
                    for (entries, maps) in expanded {
                        pair_canonicalization_maps += maps;
                        for (image_key, image_indices) in entries {
                            quotient_pairs.insert(
                                image_key,
                                QuotientPairWitness::from_point_indices(image_indices, image_key.1),
                            );
                        }
                    }
                };
                if pipelined_support_expansion {
                    let batches = jobs.len().div_ceil(job_batch);
                    let (sender, receiver) = std::sync::mpsc::sync_channel(1);
                    std::thread::scope(|scope| {
                        scope.spawn(|| {
                            let pool = rayon::ThreadPoolBuilder::new()
                                .num_threads(3)
                                .build()
                                .expect("three-thread support expansion pool");
                            for batch_start in (0..jobs.len()).step_by(job_batch) {
                                let batch_end = (batch_start + job_batch).min(jobs.len());
                                let expanded = pool.install(|| {
                                    expand_support_batch_selected(
                                        &curve,
                                        &jobs[batch_start..batch_end],
                                        &sum_keys[batch_start..batch_end],
                                        &frobenius_next_index,
                                        JOB_CHUNK,
                                        specialized_n53_support_expansion,
                                    )
                                });
                                sender.send(expanded).expect("support expansion consumer");
                            }
                        });
                        for _ in 0..batches {
                            consume(receiver.recv().expect("support expansion producer"));
                        }
                    });
                } else {
                    for batch_start in (0..jobs.len()).step_by(job_batch) {
                        let batch_end = (batch_start + job_batch).min(jobs.len());
                        consume(expand_support_batch_selected(
                            &curve,
                            &jobs[batch_start..batch_end],
                            &sum_keys[batch_start..batch_end],
                            &frobenius_next_index,
                            JOB_CHUNK,
                            specialized_n53_support_expansion,
                        ));
                    }
                }
            } else {
                for ((left_column, right_column, relative, left, right), key) in
                    jobs.into_iter().zip(sum_keys)
                {
                    if pair_mode == PairMode::SignedQuotient {
                        let (canonical, multiplier, maps) =
                            canonical_signed_key(&curve, key, modulus, lambda);
                        pair_canonicalization_maps += maps;
                        quotient_pairs.insert(
                            canonical,
                            QuotientPairWitness::new(
                                [
                                    (left_column, multiplier),
                                    (
                                        right_column,
                                        ((relative as u128 * multiplier as u128) % modulus as u128)
                                            as u64,
                                    ),
                                ],
                                canonical.1,
                            ),
                        );
                    } else {
                        let mut image_key = key;
                        let mut image_indices = [left, right];
                        for exponent in 0..curve.n {
                            quotient_pairs.insert(
                                image_key,
                                QuotientPairWitness::from_point_indices(image_indices, image_key.1),
                            );
                            if exponent + 1 < curve.n && image_key.0 != 0 {
                                let x = square_raw(&curve, image_key.0 - 1);
                                let y = square_raw(&curve, image_key.1);
                                image_key = (x + 1, y);
                                image_indices =
                                    image_indices.map(|index| frobenius_next_index[index]);
                                pair_canonicalization_maps += 1;
                            }
                        }
                    }
                    pair_additions += 1;
                }
            }
        }
    }
    let support_index_entries = match pair_mode {
        PairMode::Full => full_pairs.len(),
        PairMode::SignedQuotient | PairMode::SignedExpanded => quotient_pairs.len(),
    };
    let pair_ms = pair_started.elapsed().as_secs_f64() * 1000.0;
    let setup_ms = setup_started.elapsed().as_secs_f64() * 1000.0;
    let base_validation_started = Instant::now();
    assert!(base
        .representatives
        .iter()
        .all(|point| { curve.mul(point, &curve.subgroup_order) == BinaryPoint::Infinity }));
    let base_validation_ms = base_validation_started.elapsed().as_secs_f64() * 1000.0;
    let representative_keys: Vec<_> = base
        .representatives
        .iter()
        .map(|point| {
            let (x, y) = point_key(point);
            json!([x.to_string(), y.to_string()])
        })
        .collect();
    let factor_base_point_keys = (!summary_only).then(|| {
        base.points
            .iter()
            .map(|point| {
                let (x, y) = point_key(point);
                json!([x.to_string(), y.to_string()])
            })
            .collect::<Vec<_>>()
    });
    let factor_base_point_coordinates = (!summary_only).then(|| {
        base.points
            .iter()
            .map(|point| to_raw_point(point).map(|(x, y)| [x, y]))
            .collect::<Vec<_>>()
    });
    let factor_base_point_labels = (!summary_only).then_some(&base.point_labels);
    let generator_key = point_key(curve.generator());
    let base_hash = blake3::hash(&serde_json::to_vec(&representative_keys).unwrap())
        .to_hex()
        .to_string();
    println!(
        "{}",
        json!({
            "schema_version":"1.0",
            "task_id":RECEIPT_TASK_ID,
            "kind":"point_defined_factor_base",
            "evidence_class":"measured_factor_base_construction",
            "n":n,
            "a":a,
            "subgroup_order":modulus,
            "cofactor":curve.cofactor.to_string(),
            "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
            "orbit_columns":columns,
            "signed_automorphism_size":base.signed_size,
            "factor_base_points":base.points.len(),
            "base_hash":&base_hash,
            "field_modulus_low_terms":curve.curve.irreducible.low_terms,
            "field_mul_backend":field_mul_backend(),
            "field_square_backend":field_square_backend(&curve),
            "field_reduction_backend":field_reduction_backend(&curve),
            "field_product_pipeline":field_product_pipeline(&curve),
            "field_product_dispatch":field_product_dispatch(&curve),
            "generator":to_raw_point(curve.generator()).map(|(x,y)| [x,y]),
            "factor_base_point_coordinates":factor_base_point_coordinates,
            "factor_base_representatives":base.representatives.iter().map(|point| to_raw_point(point).map(|(x,y)| [x,y])).collect::<Vec<_>>(),
            "generator_point_key":[generator_key.0.to_string(),generator_key.1.to_string()],
            "representative_point_keys":representative_keys,
            "factor_base_point_keys":factor_base_point_keys,
            "factor_base_point_labels":factor_base_point_labels,
            "compact_evidence":summary_only,
            "point_selection":base.point_selection,
            "field_x_values_scanned":base.scanned_x,
            "base_construction_ms":base_ms,
            "support_index_ms":pair_ms,
            "parallel_support_expansion":parallel_support_expansion,
            "pipelined_support_expansion":pipelined_support_expansion,
            "specialized_n53_support_expansion":parallel_support_expansion && specialized_n53_support_expansion && n==53 && combined_n53_fast_path_enabled(),
            "specialized_n53_pair_sums":specialized_n53_pair_sums && n==53 && combined_n53_fast_path_enabled(),
            "parallel_support_expansion_threads":if pipelined_support_expansion {3} else if parallel_support_expansion {rayon::current_num_threads()} else {0},
            "parallel_support_expansion_job_batch":if pipelined_support_expansion {32768} else if parallel_support_expansion {65536} else {0},
            "parallel_support_expansion_job_chunk":if parallel_support_expansion {1024} else {0},
            "pair_index_mode":pair_mode.name(),
            "total_setup_ms":setup_ms,
            "curve_setup_ms":curve_setup_ms,
            "independent_base_validation_ms":base_validation_ms,
            "pair_group_additions":pair_additions,
            "pair_canonicalization_maps":pair_canonicalization_maps,
            "pair_batch_inversions":pair_batch_inversions,
            "support_index_entries":support_index_entries,
            "support_payload_lower_bound_bytes":support_index_entries * (4 * std::mem::size_of::<u64>() + 2 * std::mem::size_of::<usize>()),
            "support_table_allocated_bytes":if pair_mode==PairMode::Full {0} else {quotient_pairs.allocated_bytes()},
            "support_x_prefilter_kind":quotient_pairs.x_filter_kind(),
            "support_x_prefilter_bits":quotient_pairs.x_filter_bits(),
            "support_x_prefilter_hash_strategy":quotient_pairs.x_filter_hash_strategy(),
            "support_x_prefilter_insert_hash_reuse":quotient_pairs.x_filter_insert_hash_reuse(),
            "support_x_prefilter_direct_bits":quotient_pairs.x_filter_direct_bits(),
            "support_x_prefilter_blocked":quotient_pairs.x_filter_blocked(),
            "frobenius_closed":true,
            "negation_closed":true,
            "subgroup_membership_verified":true,
            "selection_uses_scalar_labels":false
        })
    );

    let batch_started = Instant::now();
    let mut batch_online_charged_ms = 0.0f64;
    let mut batch_fixture_generation_ms = 0.0f64;
    let mut batch_reference_validation_ms = 0.0f64;
    let mut batch_target_trials = 0usize;
    let mut batch_admitted_relations = 0usize;
    let mut batch_support_queries = 0usize;
    let mut batch_rank_plus_32 = 0u64;
    for fixture_index in 0..batch_fixtures {
        let fixture_material = if batch_fixtures == 1 {
            format!("{TASK_ID}|rank|{n}|{a}|{eta_numerator}/{eta_denominator}|{seed}")
        } else if let Some(corpus) = &batch_corpus {
            format!("TASK-KIC-DIRECT-BATCH-20260910|rank|{n}|{a}|{corpus}|{seed}|{fixture_index}")
        } else {
            format!(
            "TASK-KIC-DIRECT-BATCH-20260910|rank|{n}|{a}|{eta_numerator}/{eta_denominator}|{seed}|{fixture_index}"
        )
        };
        let digest = blake3::hash(fixture_material.as_bytes());
        let fixture_seed = u64::from_le_bytes(digest.as_bytes()[..8].try_into().unwrap());
        let mut rng = StdRng::seed_from_u64(fixture_seed);
        let fixture_generation_started = Instant::now();
        // Consume the ordinary draw even when a public explicit scalar is
        // supplied, so changing only the target does not change the relation
        // coefficient stream that follows.
        let generated_scalar = rng.gen_range(1..modulus);
        let (known_scalar, q, fixture_scalar_source, public_hash_seed, public_hash_counter) =
            match fixture_target {
                FixtureTarget::SeededScalar => (
                    Some(generated_scalar),
                    curve.mul(curve.generator(), &BigUint::from(generated_scalar)),
                    "seeded_fixture_scalar",
                    None,
                    None,
                ),
                FixtureTarget::ExplicitScalar(scalar) => (
                    Some(scalar),
                    curve.mul(curve.generator(), &BigUint::from(scalar)),
                    "explicit_public_validation_scalar",
                    None,
                    None,
                ),
                FixtureTarget::PublicHash(public_seed) => {
                    let (target, counter) = public_hash_target(&curve, public_seed);
                    (
                        None,
                        target,
                        "public_hash_unknown_scalar",
                        Some(public_seed),
                        Some(counter),
                    )
                }
            };
        let target_scalar_constructed = known_scalar.is_some();
        let target_kind = if target_scalar_constructed {
            "known_scalar_multiple"
        } else {
            "public_hash_to_curve_cofactor"
        };
        let fixture_generation_ms = fixture_generation_started.elapsed().as_secs_f64() * 1000.0;
        let generator_raw = to_raw_point(curve.generator());
        let q_raw = to_raw_point(&q);
        let fixture_setup_started = Instant::now();
        let (mut walk_a, mut walk_b, delta_a, delta_b, mut walk_target, walk_jump) =
            match target_mode {
                TargetMode::CoefficientWalk => {
                    let walk_a = rng.gen_range(0..modulus);
                    let walk_b = rng.gen_range(1..modulus);
                    let delta_a = rng.gen_range(1..modulus);
                    let delta_b = rng.gen_range(1..modulus);
                    let walk_target = raw_add_point(
                        &curve,
                        raw_scalar_point(&curve, generator_raw, walk_a),
                        raw_scalar_point(&curve, q_raw, walk_b),
                    );
                    let walk_jump = raw_add_point(
                        &curve,
                        raw_scalar_point(&curve, generator_raw, delta_a),
                        raw_scalar_point(&curve, q_raw, delta_b),
                    );
                    (walk_a, walk_b, delta_a, delta_b, walk_target, walk_jump)
                }
                TargetMode::PartitionWalk => {
                    let walk_a = rng.gen_range(0..modulus);
                    let walk_b = rng.gen_range(1..modulus);
                    let walk_target = raw_add_point(
                        &curve,
                        raw_scalar_point(&curve, generator_raw, walk_a),
                        raw_scalar_point(&curve, q_raw, walk_b),
                    );
                    (walk_a, walk_b, 0, 0, walk_target, None)
                }
                TargetMode::Independent => (0, 0, 0, 0, None, None),
            };
        let fixture_setup_ms = fixture_setup_started.elapsed().as_secs_f64() * 1000.0;
        let mut echelon = Echelon::new(columns + 1);
        let mut rank_a_echelon = Echelon::new(columns);
        let mut augmented_echelon = Echelon::new(columns + 2);
        let mut certificate_echelon = AffineCertificateEchelon::new(columns + 1, columns);
        let mut reverse_echelon = ReverseEchelon::new(columns + 1);
        let mut rows = Vec::new();
        let mut right_hand_sides = Vec::new();
        let mut exact_rows = HashSet::new();
        let mut projective_rows = HashSet::new();
        let mut duplicate_rows = 0usize;
        let mut scalar_multiple_rows = 0usize;
        let mut accepted = 0usize;
        let mut trials = 0usize;
        let mut rank_full_at = None;
        let mut target_certificate: Option<TargetCertificate> = None;
        let mut target_inconsistency_at = None;
        let mut target_pivot_at = None;
        let mut certificate_tracker_pivots = 0usize;
        let mut certificate_tracker_dependents = 0usize;
        let mut decomposition_queries = 0usize;
        let mut query_additions = 0usize;
        let mut query_canonicalization_maps = 0usize;
        let mut query_x_filter_rejections = 0usize;
        let mut query_exact_table_misses = 0usize;
        let mut target_walk_additions = 0usize;
        let mut query_batch_inversions = 0usize;
        let mut query_parallel_waves = 0usize;
        let mut query_parallel_chunks = 0usize;
        let mut query_shared_sign_denominator_inputs = 0usize;
        let mut rank_targeted_trials = 0usize;
        let mut rank_targeted_nonincrements = 0usize;
        let mut rank_target_slot_index_builds = 0usize;
        let mut rank_target_slot_column = None;
        let mut rank_target_slots = Vec::new();
        let mut reference_validation_records = Vec::new();
        let mut relation_hashes = Vec::new();
        let mut walk_seen = HashSet::new();
        let mut target_walk_restarts = 0usize;
        let mut target_scalar_multiplications = match target_mode {
            TargetMode::Independent => 0,
            TargetMode::CoefficientWalk => 4,
            TargetMode::PartitionWalk => 2,
        };
        let mut fiber_rest_scratch = Vec::with_capacity(128);
        let mut pair_point_scratch = Vec::with_capacity(64);
        let mut pair_signed_slot_scratch = Vec::with_capacity(64);
        let mut pair_rest_scratch = Vec::with_capacity(64);
        let mut pair_batch_scratch = RawBatchScratch::default();
        let parallel_lanes = if query_mode.pair_pair_parallel() {
            rayon::current_num_threads().max(1)
        } else {
            0
        };
        let mut pair_parallel_scratch: Vec<PairPairChunkScratch> =
            (0..parallel_lanes).map(|_| Default::default()).collect();
        let mut pair_parallel_results = Vec::with_capacity(parallel_lanes);
        let mut dense_rank_recomputations = 0usize;
        let mut dimension_bound_rank_crosschecks = 0usize;
        let mut reverse_incremental_rank_crosschecks = 0usize;
        let mut terminal_dense_rank_crosschecks = 0usize;
        let mut target_generation_ns = 0u128;
        let mut query_total_ns = 0u128;
        let mut packed_verification_ns = 0u128;
        let mut rank_diagnostics_ns = 0u128;
        let mut receipt_construction_ns = 0u128;
        let collection_started = Instant::now();
        let relation_cap = 2 * columns + 64 + relation_cap_extra;
        let target_cap = 100_000usize;

        while trials < target_cap {
            if let Some(full_at) = rank_full_at {
                if accepted >= full_at + required_rank_surplus {
                    break;
                }
            } else if accepted >= relation_cap {
                break;
            }
            trials += 1;
            let target_generation_started = Instant::now();
            if target_mode != TargetMode::Independent
                && !walk_seen.insert(raw_compact_key(walk_target))
            {
                loop {
                    walk_a = rng.gen_range(0..modulus);
                    walk_b = rng.gen_range(1..modulus);
                    walk_target = raw_add_point(
                        &curve,
                        raw_scalar_point(&curve, generator_raw, walk_a),
                        raw_scalar_point(&curve, q_raw, walk_b),
                    );
                    target_scalar_multiplications += 2;
                    if walk_seen.insert(raw_compact_key(walk_target)) {
                        break;
                    }
                }
                target_walk_restarts += 1;
            }
            let (coefficient_a, coefficient_b, target) = match target_mode {
                TargetMode::Independent => {
                    let coefficient_a = rng.gen_range(0..modulus);
                    let coefficient_b = rng.gen_range(1..modulus);
                    let target = raw_add_point(
                        &curve,
                        raw_scalar_point(&curve, generator_raw, coefficient_a),
                        raw_scalar_point(&curve, q_raw, coefficient_b),
                    );
                    target_scalar_multiplications += 2;
                    (coefficient_a, coefficient_b, target)
                }
                TargetMode::CoefficientWalk => {
                    let result = (walk_a, walk_b, walk_target.clone());
                    walk_a = (walk_a + delta_a) % modulus;
                    walk_b = (walk_b + delta_b) % modulus;
                    walk_target = raw_add_point(&curve, walk_target, walk_jump);
                    target_walk_additions += 1;
                    result
                }
                TargetMode::PartitionWalk => {
                    let result = (walk_a, walk_b, walk_target);
                    match target_partition(walk_target) {
                        0 => {
                            walk_a = (walk_a + 1) % modulus;
                            walk_target = raw_add_point(&curve, walk_target, generator_raw);
                        }
                        1 => {
                            walk_b = (walk_b + 1) % modulus;
                            walk_target = raw_add_point(&curve, walk_target, q_raw);
                        }
                        _ => {
                            walk_a = (2 * walk_a) % modulus;
                            walk_b = (2 * walk_b) % modulus;
                            walk_target = raw_double_point(&curve, walk_target);
                        }
                    }
                    target_walk_additions += 1;
                    result
                }
            };
            target_generation_ns += target_generation_started.elapsed().as_nanos();
            let query_started = Instant::now();
            let mut witness: Option<(Vec<usize>, Vec<(usize, u64)>)> = None;
            let targeted_column =
                if rank_aware_pair_scan && echelon.rank + rank_target_deficiency >= columns + 1 {
                    echelon.pivots[..columns].iter().position(Option::is_none)
                } else {
                    None
                };
            rank_targeted_trials += usize::from(targeted_column.is_some());
            if let Some(column) = targeted_column {
                if rank_target_slot_column != Some(column) {
                    rank_target_slots =
                        quotient_pairs.slots_for_column(&base.point_labels, column, columns);
                    assert!(!rank_target_slots.is_empty());
                    rank_target_slot_column = Some(column);
                    rank_target_slot_index_builds += 1;
                }
            }
            if let Some(width) = query_mode.pair_pair_width() {
                assert!(pair_mode == PairMode::SignedExpanded);
                let slots = quotient_pairs.slots();
                let slot_order = targeted_column.map(|_| rank_target_slots.as_slice());
                let scan_slots = slot_order.map_or(slots, <[u32]>::len);
                let start_slot = if slot_order.is_some() {
                    CompactPairTable::hash(raw_compact_key(target)) as usize % scan_slots
                } else {
                    CompactPairTable::hash(raw_compact_key(target)) as usize & (slots - 1)
                };
                if query_mode.pair_pair_parallel() {
                    let cursors = 2 * scan_slots;
                    let chunks = cursors.div_ceil(width);
                    let lanes = pair_parallel_scratch.len();
                    let mut wave_start = 0usize;
                    while wave_start < chunks && witness.is_none() {
                        let wave_end = (wave_start + lanes).min(chunks);
                        pair_parallel_scratch[..wave_end - wave_start]
                            .par_iter_mut()
                            .enumerate()
                            .map(|(lane, scratch)| {
                                let chunk = wave_start + lane;
                                let cursor_start = chunk * width;
                                pair_pair_cursor_chunk(
                                    &curve,
                                    target,
                                    &quotient_pairs,
                                    &base.point_labels,
                                    &label_to_index,
                                    modulus,
                                    slot_order,
                                    start_slot,
                                    cursor_start,
                                    (cursor_start + width).min(cursors),
                                    dual_sign_pair_scan,
                                    compact_pair_scratch,
                                    specialized_n53_pair_batch,
                                    scratch,
                                )
                            })
                            .collect_into_vec(&mut pair_parallel_results);
                        query_parallel_waves += 1;
                        query_parallel_chunks += pair_parallel_results.len();
                        for result in pair_parallel_results.drain(..) {
                            query_additions += result.additions;
                            decomposition_queries += result.additions;
                            query_x_filter_rejections += result.x_filter_rejections;
                            query_exact_table_misses += result.exact_table_misses;
                            query_batch_inversions += result.batch_inversions;
                            query_shared_sign_denominator_inputs +=
                                result.shared_denominator_inputs;
                            if witness.is_none() {
                                if let Some((indices, labels)) = result.witness {
                                    witness = Some((indices.to_vec(), labels.to_vec()));
                                }
                            }
                        }
                        wave_start = wave_end;
                    }
                } else {
                    let mut cursor = 0usize;
                    while cursor < 2 * slots && witness.is_none() {
                        pair_point_scratch.clear();
                        pair_signed_slot_scratch.clear();
                        while cursor < 2 * slots && pair_point_scratch.len() < width {
                            let slot = (start_slot + cursor / 2) & (slots - 1);
                            let negative = cursor & 1 == 1;
                            cursor += 1;
                            if let Some(point) = quotient_pairs.signed_point_at_slot(slot, negative)
                            {
                                pair_point_scratch.push(point);
                                pair_signed_slot_scratch.push(slot << 1 | usize::from(negative));
                            }
                        }
                        if pair_point_scratch.is_empty() {
                            continue;
                        }
                        let attempted = batch_raw_target_minus_points_x_filtered(
                            &curve,
                            target,
                            &pair_point_scratch,
                            &quotient_pairs,
                            &mut pair_rest_scratch,
                            &mut pair_batch_scratch,
                        );
                        query_additions += attempted;
                        decomposition_queries += attempted;
                        query_x_filter_rejections += attempted - pair_rest_scratch.len();
                        query_batch_inversions += usize::from(target.is_some());
                        for &(position, rest_key) in &pair_rest_scratch {
                            let Some((right_indices, right_labels)) = lookup_signed_expanded_pair(
                                rest_key,
                                modulus,
                                &quotient_pairs,
                                &base.point_labels,
                                &label_to_index,
                                prefiltered_exact_lookup_enabled(),
                            ) else {
                                query_exact_table_misses += 1;
                                continue;
                            };
                            let signed_slot = pair_signed_slot_scratch[position];
                            let (left_indices, left_labels) = quotient_pairs.signed_labels_at_slot(
                                signed_slot >> 1,
                                signed_slot & 1 == 1,
                                modulus,
                                &base.point_labels,
                                &label_to_index,
                            );
                            witness = Some((
                                vec![
                                    left_indices[0],
                                    left_indices[1],
                                    right_indices[0],
                                    right_indices[1],
                                ],
                                vec![
                                    left_labels[0],
                                    left_labels[1],
                                    right_labels[0],
                                    right_labels[1],
                                ],
                            ));
                            break;
                        }
                    }
                }
            } else if let Some(width) = query_mode.fiber_width() {
                for start in (0..base_fibers.len()).step_by(width) {
                    let end = (start + width).min(base_fibers.len());
                    let attempted = if pair_mode == PairMode::SignedExpanded {
                        batch_raw_target_minus_fibers_x_filtered(
                            &curve,
                            target,
                            &base_fibers[start..end],
                            &quotient_pairs,
                            &mut fiber_rest_scratch,
                        )
                    } else {
                        batch_raw_target_minus_fibers(
                            &curve,
                            target,
                            &base_fibers[start..end],
                            &mut fiber_rest_scratch,
                        );
                        fiber_rest_scratch.len()
                    };
                    query_additions += attempted;
                    decomposition_queries += attempted;
                    query_x_filter_rejections += attempted - fiber_rest_scratch.len();
                    query_batch_inversions += usize::from(target.is_some());
                    for &(right, rest_key) in &fiber_rest_scratch {
                        let (candidate, maps) = lookup_pair_witness(
                            pair_mode,
                            &curve,
                            rest_key,
                            right,
                            modulus,
                            lambda,
                            &base,
                            &full_pairs,
                            &quotient_pairs,
                            &label_to_index,
                        );
                        query_canonicalization_maps += maps;
                        if let Some((indices, labels)) = candidate {
                            witness = Some((indices.to_vec(), labels.to_vec()));
                            break;
                        }
                    }
                    if witness.is_some() {
                        break;
                    }
                }
            } else if let Some(width) = query_mode.width(base.points.len()) {
                for start in (0..base.points.len()).step_by(width) {
                    let end = (start + width).min(base.points.len());
                    let rests =
                        batch_raw_target_minus_keys(&curve, target, &raw_base_points[start..end]);
                    query_additions += rests.len();
                    query_batch_inversions += usize::from(target.is_some());
                    for (offset, &rest_key) in rests.iter().enumerate() {
                        let right = start + offset;
                        decomposition_queries += 1;
                        let (candidate, maps) = lookup_pair_witness(
                            pair_mode,
                            &curve,
                            rest_key,
                            right,
                            modulus,
                            lambda,
                            &base,
                            &full_pairs,
                            &quotient_pairs,
                            &label_to_index,
                        );
                        query_canonicalization_maps += maps;
                        if let Some((indices, labels)) = candidate {
                            witness = Some((indices.to_vec(), labels.to_vec()));
                            break;
                        }
                    }
                    if witness.is_some() {
                        break;
                    }
                }
            } else {
                for (right, &point) in raw_base_points.iter().enumerate() {
                    let rest = raw_add_point(&curve, target, raw_neg_point(point));
                    query_additions += 1;
                    decomposition_queries += 1;
                    let (candidate, maps) = lookup_pair_witness(
                        pair_mode,
                        &curve,
                        raw_compact_key(rest),
                        right,
                        modulus,
                        lambda,
                        &base,
                        &full_pairs,
                        &quotient_pairs,
                        &label_to_index,
                    );
                    query_canonicalization_maps += maps;
                    if let Some((indices, labels)) = candidate {
                        witness = Some((indices.to_vec(), labels.to_vec()));
                        break;
                    }
                }
            }
            let query_elapsed = query_started.elapsed();
            let query_ms = query_elapsed.as_secs_f64() * 1000.0;
            query_total_ns += query_elapsed.as_nanos();
            let Some((indices, witness_labels)) = witness else {
                continue;
            };
            let packed_verification_started = Instant::now();
            let sum = indices.iter().fold(None, |accumulator, &index| {
                raw_add_point(&curve, accumulator, raw_base_points[index])
            });
            assert_eq!(
                sum, target,
                "support-index relation must verify in the group"
            );
            reference_validation_records.push((indices.clone(), coefficient_a, coefficient_b));
            packed_verification_ns += packed_verification_started.elapsed().as_nanos();

            let rank_started = Instant::now();
            let mut row = vec![0u64; columns + 1];
            for &(column, coefficient) in &witness_labels {
                row[column] = (row[column] + coefficient) % modulus;
            }
            row[columns] = (modulus - coefficient_b) % modulus;
            let exact_duplicate = !exact_rows.insert(row.clone());
            duplicate_rows += usize::from(exact_duplicate);
            let first_nonzero = row.iter().copied().find(|&value| value != 0).unwrap();
            let normalization_inverse = modpow(first_nonzero, modulus - 2, modulus);
            let normalized_row: Vec<_> = row
                .iter()
                .map(|value| {
                    ((*value as u128 * normalization_inverse as u128) % modulus as u128) as u64
                })
                .collect();
            let scalar_multiple = !projective_rows.insert(normalized_row);
            scalar_multiple_rows += usize::from(scalar_multiple);
            let rank_before = echelon.rank;
            let incremented = echelon.insert(row.clone(), modulus);
            let rank_after = echelon.rank;
            assert_eq!(rank_after, rank_before + usize::from(incremented));
            let rank_a_before = rank_a_echelon.rank;
            let rank_a_incremented = rank_a_echelon.insert(row[..columns].to_vec(), modulus);
            let rank_a_after = rank_a_echelon.rank;
            assert_eq!(rank_a_after, rank_a_before + usize::from(rank_a_incremented));
            let mut augmented_row = row.clone();
            augmented_row.push(coefficient_a);
            let rank_a_b_a_before = augmented_echelon.rank;
            let rank_a_b_a_incremented = augmented_echelon.insert(augmented_row, modulus);
            let rank_a_b_a_after = augmented_echelon.rank;
            assert_eq!(
                rank_a_b_a_after,
                rank_a_b_a_before + usize::from(rank_a_b_a_incremented)
            );
            let certificate_outcome =
                certificate_echelon.insert(row.clone(), coefficient_a, modulus);
            let (certificate_outcome_name, stop_after_receipt) = match certificate_outcome {
                AffineInsertOutcome::Dependent => {
                    certificate_tracker_dependents += 1;
                    ("DEPENDENT", false)
                }
                AffineInsertOutcome::Pivot(column) => {
                    certificate_tracker_pivots += 1;
                    assert!(column < columns);
                    ("FACTOR_PIVOT", false)
                }
                AffineInsertOutcome::Inconsistent => {
                    target_inconsistency_at = Some(accepted + 1);
                    ("INCONSISTENT", true)
                }
                AffineInsertOutcome::TargetIdentified(certificate) => {
                    certificate_tracker_pivots += 1;
                    target_pivot_at = Some(accepted + 1);
                    target_certificate = Some(certificate);
                    ("TARGET_PIVOT", true)
                }
            };
            rank_targeted_nonincrements += usize::from(targeted_column.is_some() && !incremented);
            rows.push(row.clone());
            right_hand_sides.push(coefficient_a);
            let independently_crosschecked_rank = if incremental_rank_crosscheck {
                let reverse_before = reverse_echelon.rank;
                let reverse_incremented = reverse_echelon.insert(row.clone(), modulus);
                assert_eq!(
                    reverse_echelon.rank,
                    reverse_before + usize::from(reverse_incremented)
                );
                reverse_incremental_rank_crosschecks += 1;
                reverse_echelon.rank
            } else if rank_before == columns + 1 {
                dimension_bound_rank_crosschecks += 1;
                columns + 1
            } else if columns > 64 || std::env::var("KIC_SKIP_DENSE_RANK").as_deref() == Ok("1") {
                // Full dense GE after every accepted row is O(#rows · K³) and
                // dominates past ~64 columns (n=53 balanced bases). Trust the
                // incremental echelon; optional end-of-run dense check remains
                // available via KIC_INCREMENTAL_RANK_CROSSCHECK.
                rank_after
            } else {
                dense_rank_recomputations += 1;
                dense_rank(&rows, columns + 1, modulus)
            };
            assert_eq!(independently_crosschecked_rank, rank_after);
            accepted += 1;
            if rank_after == columns + 1 && rank_full_at.is_none() {
                rank_full_at = Some(accepted);
            }
            rank_diagnostics_ns += rank_started.elapsed().as_nanos();
            let receipt_started = Instant::now();
            let point_indices: Vec<_> = indices.into_iter().collect();
            assert_eq!(
                point_indices
                    .iter()
                    .map(|&index| base.point_labels[index])
                    .collect::<Vec<_>>(),
                witness_labels
            );
            let (target_x, target_y) = raw_compact_key(target);
            let relation_material = serde_json::to_vec(&json!({
                "n":n,
                "a":a,
                "base_hash":&base_hash,
                "trial":trials,
                "coefficient_a":coefficient_a,
                "coefficient_b":coefficient_b,
                "target":[target_x,target_y],
                "indices":&point_indices,
                "row":&row
            }))
            .unwrap();
            let relation_hash = blake3::hash(&relation_material).to_hex().to_string();
            relation_hashes.push(relation_hash.clone());
            if !summary_only {
                let labels: Vec<_> = point_indices
                    .iter()
                    .map(|&index| {
                        let (column, coefficient) = base.point_labels[index];
                        json!({"column":column,"coefficient":coefficient})
                    })
                    .collect();
                println!(
                    "{}",
                    json!({
                        "schema_version":"1.0",
                        "task_id":RECEIPT_TASK_ID,
                        "kind":"relation_rank_receipt",
                        "evidence_class":"measured_exact_support_relation",
                        "n":n,
                        "a":a,
                        "fixture_seed":fixture_seed,
                        "base_hash":&base_hash,
                        "relation_hash":relation_hash,
                        "published_fixture_scalar":known_scalar,
                        "target_scalar_constructed":target_scalar_constructed,
                        "target_kind":target_kind,
                        "public_hash_seed":public_hash_seed,
                        "public_hash_counter":public_hash_counter,
                        "trial":trials,
                        "accepted_relation":accepted,
                        "coefficient_a":coefficient_a,
                        "coefficient_b":coefficient_b,
                        "target_point_key":[target_x,target_y],
                        "factor_point_indices":&point_indices,
                        "orbit_labels":labels,
                        "sparse_row":&row,
                        "rank_before":rank_before,
                        "rank_after":rank_after,
                        "rank_incremented":incremented,
                        "rank_A_before":rank_a_before,
                        "rank_A_after":rank_a_after,
                        "rank_A_incremented":rank_a_incremented,
                        "rank_A_b_before":rank_before,
                        "rank_A_b_after":rank_after,
                        "rank_A_b_incremented":incremented,
                        "rank_A_b_a_before":rank_a_b_a_before,
                        "rank_A_b_a_after":rank_a_b_a_after,
                        "rank_A_b_a_incremented":rank_a_b_a_incremented,
                        "certificate_tracker_outcome":certificate_outcome_name,
                        "duplicate_row":exact_duplicate,
                        "scalar_multiple_row":scalar_multiple,
                        "dense_crosscheck_rank":rank_after,
                        "query_ms":query_ms,
                        "verified_group_identity":true,
                        "group_identity_backend":"packed_u64_polynomial_basis",
                        "fixture_scalar_used_by_collector":false
                    })
                );
            }
            receipt_construction_ns += receipt_started.elapsed().as_nanos();
            if stop_after_receipt {
                break;
            }
        }
        if incremental_rank_crosscheck {
            let terminal_dense_rank = dense_rank(&rows, columns + 1, modulus);
            assert_eq!(terminal_dense_rank, echelon.rank);
            assert_eq!(terminal_dense_rank, reverse_echelon.rank);
            terminal_dense_rank_crosschecks += 1;
        }
        let linear_solve_started = Instant::now();
        let solution = (target_certificate.is_none() && echelon.rank == columns + 1).then(|| {
            solve_full_column_rank_system(&rows, &right_hand_sides, columns + 1, modulus).unwrap()
        });
        let linear_solve_ms = linear_solve_started.elapsed().as_secs_f64() * 1000.0;
        let solution_validation_started = Instant::now();
        if let Some(solution) = &solution {
            if let Some(expected) = known_scalar {
                assert_eq!(solution[columns], expected);
            }
            assert_eq!(
                curve.mul(curve.generator(), &BigUint::from(solution[columns])),
                q,
                "recovered scalar must reconstruct the public target"
            );
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
        let certificate_validation_started = Instant::now();
        let certificate_recomputation = target_certificate.as_ref().map(|certificate| {
            assert_eq!(certificate.pivot_column, columns);
            assert_eq!(certificate.prefix_rows, rows.len());
            assert_eq!(certificate.rank_a_b, echelon.rank);
            let recomputation = recompute_target_certificate(
                &rows,
                &right_hand_sides,
                &certificate.weights,
                columns,
                certificate.returned_d,
                modulus,
            );
            assert!(recomputation.valid, "target certificate must recompute exactly");
            if let Some(expected) = known_scalar {
                assert_eq!(certificate.returned_d, expected);
            }
            assert_eq!(
                curve.mul(curve.generator(), &BigUint::from(certificate.returned_d)),
                q,
                "certificate-derived scalar must reconstruct the public target"
            );
            recomputation
        });
        let certificate_validation_ms =
            certificate_validation_started.elapsed().as_secs_f64() * 1000.0;
        let recovered_scalar = target_certificate
            .as_ref()
            .map(|certificate| certificate.returned_d)
            .or_else(|| solution.as_ref().map(|values| values[columns]));
        let certificate_digest = target_certificate.as_ref().map(|certificate| {
            blake3::hash(&serde_json::to_vec(&certificate.weights).unwrap())
                .to_hex()
                .to_string()
        });
        let certificate_nonzero_weights = target_certificate.as_ref().map(|certificate| {
            certificate.weights.iter().filter(|&&weight| weight != 0).count()
        });
        let collection_ms = collection_started.elapsed().as_secs_f64() * 1000.0;
        let reference_validation_started = Instant::now();
        for (indices, coefficient_a, coefficient_b) in &reference_validation_records {
            let target = curve.add(
                &curve.mul(curve.generator(), &BigUint::from(*coefficient_a)),
                &curve.mul(&q, &BigUint::from(*coefficient_b)),
            );
            let sum = indices
                .iter()
                .fold(BinaryPoint::Infinity, |accumulator, &index| {
                    curve.add(&accumulator, &base.points[index])
                });
            assert_eq!(sum, target, "independent reference relation validation");
        }
        let reference_validation_ms = reference_validation_started.elapsed().as_secs_f64() * 1000.0;
        let q_key = point_key(&q);
        let generator_key = point_key(curve.generator());
        let status = if target_inconsistency_at.is_some() {
            "INCONSISTENT_SYSTEM"
        } else if target_certificate.is_some() {
            "TARGET_IDENTIFIED"
        } else if rank_full_at
            .map(|full_at| accepted >= full_at + required_rank_surplus)
            .unwrap_or(false)
        {
            match required_rank_surplus {
                0 => "FULL_RANK",
                32 => "RANK_PLUS_32",
                _ => "RANK_PLUS_SURPLUS",
            }
        } else if accepted >= relation_cap {
            "RANK_DEFICIENT"
        } else {
            "TARGET_CAP"
        };
        batch_online_charged_ms += fixture_setup_ms + collection_ms;
        batch_fixture_generation_ms += fixture_generation_ms;
        batch_reference_validation_ms += reference_validation_ms;
        batch_target_trials += trials;
        batch_admitted_relations += accepted;
        batch_support_queries += decomposition_queries;
        batch_rank_plus_32 += u64::from(status == "RANK_PLUS_32");
        println!(
            "{}",
            json!({
                "schema_version":"1.0",
                "task_id":RECEIPT_TASK_ID,
                "kind":"relation_rank_summary",
                "evidence_class":"measured_exact_support_relation",
                "fixture_index":fixture_index,
                "fixture_seed":fixture_seed,
                "published_fixture_scalar":known_scalar,
                "fixture_scalar_source":fixture_scalar_source,
                "target_scalar_constructed":target_scalar_constructed,
                "target_kind":target_kind,
                "public_hash_seed":public_hash_seed,
                "public_hash_counter":public_hash_counter,
                "published_q":to_raw_point(&q).map(|(x,y)| [x,y]),
                "generator_point_key":[generator_key.0.to_string(),generator_key.1.to_string()],
                "published_q_point_key":[q_key.0.to_string(),q_key.1.to_string()],
                "recovered_fixture_scalar":recovered_scalar,
                "factor_base_log_solution":solution.as_ref().map(|values| &values[..columns]),
                "factor_base_logs_known_by_construction":false,
                "linear_solution_verified":solution.is_some(),
                "target_certificate_verified":certificate_recomputation.as_ref().is_some_and(|value| value.valid),
                "final_target_group_verified":recovered_scalar.is_some(),
                "n":n,
                "a":a,
                "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
                "status":status,
                "orbit_columns":columns,
                "matrix_columns":columns+1,
                "factor_base_points":base.points.len(),
                "base_hash":&base_hash,
                "target_trials":trials,
                "admitted_relations":accepted,
                "terminal_rank":echelon.rank,
                "rank_A":rank_a_echelon.rank,
                "rank_A_b":echelon.rank,
                "rank_A_b_a":augmented_echelon.rank,
                "target_pivot_at_relation":target_pivot_at,
                "target_inconsistency_at_relation":target_inconsistency_at,
                "certificate_tracker_pivots":certificate_tracker_pivots,
                "certificate_tracker_dependents":certificate_tracker_dependents,
                "certificate_prefix_rows":target_certificate.as_ref().map(|value| value.prefix_rows),
                "certificate_weights":target_certificate.as_ref().map(|value| &value.weights),
                "certificate_nonzero_weights":certificate_nonzero_weights,
                "certificate_digest":certificate_digest,
                "certificate_wA":certificate_recomputation.as_ref().map(|value| &value.w_a),
                "certificate_wb":certificate_recomputation.as_ref().map(|value| value.w_b),
                "certificate_wa":certificate_recomputation.as_ref().map(|value| value.w_rhs),
                "duplicate_rows":duplicate_rows,
                "scalar_multiple_rows":scalar_multiple_rows,
                "full_rank_at_relation":rank_full_at,
                "surplus_relations":rank_full_at.map(|at| accepted-at).unwrap_or(0),
                "required_surplus_relations":required_rank_surplus,
                "rank_aware_pair_scan":rank_aware_pair_scan,
                "rank_target_deficiency":rank_target_deficiency,
                "rank_targeted_trials":rank_targeted_trials,
                "rank_targeted_nonincrements":rank_targeted_nonincrements,
                "rank_target_slot_index_builds":rank_target_slot_index_builds,
                "rank_target_slot_index_entries":rank_target_slots.len(),
                "rank_target_slot_index_allocated_bytes":rank_target_slots.capacity()*std::mem::size_of::<u32>(),
                "relation_cap_without_rank":relation_cap,
                "relation_cap_extra":relation_cap_extra,
                "collection_ms":collection_ms,
                "linear_solve_ms":linear_solve_ms,
                "solution_validation_ms":solution_validation_ms,
                "certificate_validation_ms":certificate_validation_ms,
                "setup_ms":setup_ms,
                "curve_setup_ms":curve_setup_ms,
                "fixture_setup_ms":fixture_setup_ms,
                "fixture_generation_ms":fixture_generation_ms,
                "charged_total_ms":setup_ms+fixture_setup_ms+collection_ms,
                "pair_group_additions":pair_additions,
                "pair_index_mode":pair_mode.name(),
                "pair_canonicalization_maps":pair_canonicalization_maps,
                "pair_batch_inversions":pair_batch_inversions,
                "field_mul_backend":field_mul_backend(),
                "field_square_backend":field_square_backend(&curve),
                "field_reduction_backend":field_reduction_backend(&curve),
                "field_product_pipeline":field_product_pipeline(&curve),
                "field_product_dispatch":field_product_dispatch(&curve),
                "query_group_additions":query_additions,
                "query_canonicalization_maps":query_canonicalization_maps,
                "query_x_filter_rejections":query_x_filter_rejections,
                "query_exact_table_misses":query_exact_table_misses,
                "query_mode":query_mode.name(),
                "decomposition_arity":if query_mode.pair_pair_width().is_some() {4} else {3},
                "query_batch_inversions":query_batch_inversions,
                "query_parallel_threads":if query_mode.pair_pair_parallel() {rayon::current_num_threads()} else {1},
                "query_parallel_waves":query_parallel_waves,
                "query_parallel_chunks":query_parallel_chunks,
                "query_shared_sign_denominator_inputs":query_shared_sign_denominator_inputs,
                "query_dual_sign_denominator_sharing":query_mode.pair_pair_parallel() && dual_sign_pair_scan,
                "query_compact_pair_scratch":query_mode.pair_pair_parallel() && dual_sign_pair_scan && compact_pair_scratch,
                "query_specialized_n53_pair_batch":query_mode.pair_pair_parallel() && dual_sign_pair_scan && compact_pair_scratch && specialized_n53_pair_batch && n==53 && combined_n53_fast_path_enabled(),
                "query_itoh_n53_inverse":query_mode.pair_pair_parallel() && specialized_n53_pair_batch && n==53 && combined_n53_fast_path_enabled() && itoh_n53_inverse_enabled(),
                "query_prefiltered_exact_lookup":query_mode.pair_pair_width().is_some() && prefiltered_exact_lookup_enabled(),
                "query_raw_point_scratch_bytes":std::mem::size_of::<RawPoint>(),
                "query_compact_point_scratch_bytes":std::mem::size_of::<(u64,u64)>(),
                "target_mode":target_mode.name(),
                "target_walk_additions":target_walk_additions,
                "target_walk_restarts":target_walk_restarts,
                "target_scalar_multiplications":target_scalar_multiplications,
                "support_queries":decomposition_queries,
                "all_relations_group_verified":true,
                "reference_validation_ms":reference_validation_ms,
                "reference_relations_validated":reference_validation_records.len(),
                "rank_crosschecked_after_every_relation":true,
                "dense_rank_recomputations":dense_rank_recomputations,
                "dimension_bound_rank_crosschecks":dimension_bound_rank_crosschecks,
                "post_full_rank_crosscheck":if incremental_rank_crosscheck {
                    "reverse-pivot incremental rank with terminal dense check"
                } else {
                    "ambient dimension bound"
                },
                "rank_crosscheck_mode":if incremental_rank_crosscheck {
                    "forward_and_reverse_incremental_plus_terminal_dense"
                } else {
                    "dense_until_full_then_ambient_dimension"
                },
                "reverse_incremental_rank_crosschecks":reverse_incremental_rank_crosschecks,
                "terminal_dense_rank_crosschecks":terminal_dense_rank_crosschecks,
                "variant":match pair_mode { PairMode::Full=>"V2_full_pair_support_index", PairMode::SignedQuotient=>"V2_signed_quotient_pair_support_index", PairMode::SignedExpanded=>"V2_signed_expanded_pair_support_index" },
                "summary_only_timing":summary_only,
                "relation_hashes":summary_only.then_some(&relation_hashes),
                "relation_receipts_emitted":!summary_only,
                "timing_breakdown_ms":{
                    "target_generation":target_generation_ns as f64/1_000_000.0,
                    "query":query_total_ns as f64/1_000_000.0,
                    "packed_verification":packed_verification_ns as f64/1_000_000.0,
                    "rank_and_diagnostics":rank_diagnostics_ns as f64/1_000_000.0,
                    "receipt_construction":receipt_construction_ns as f64/1_000_000.0
                },
                "claim_boundary":if target_scalar_constructed {
                    "public synthetic relation/rank control; fixture scalar retained only for validation"
                } else {
                    "public_hash_unknown_scalar"
                }
            })
        );
    }
    if batch_fixtures > 1 {
        let observed_batch_section_ms = batch_started.elapsed().as_secs_f64() * 1000.0;
        println!(
            "{}",
            json!({
                "schema_version":"1.0",
                "task_id":"TASK-KIC-DIRECT-BATCH-20260910",
                "kind":"retained_support_batch_summary",
                "evidence_class":"direct_measured_retained_support_batch",
                "n":n,
                "a":a,
                "eta":{"numerator":eta_numerator,"denominator":eta_denominator},
                "batch_seed":seed,
                "batch_fixtures":batch_fixtures,
                "batch_corpus":&batch_corpus,
                "independent_fixture_seed_domain":if batch_corpus.is_some() {
                    "BLAKE3(TASK-KIC-DIRECT-BATCH-20260910 || rank || curve || corpus || batch_seed || fixture_index)"
                } else {
                    "BLAKE3(TASK-KIC-DIRECT-BATCH-20260910 || rank || curve || eta || batch_seed || fixture_index)"
                },
                "support_table_builds":1,
                "support_table_instance_reused":true,
                "support_index_entries":support_index_entries,
                "support_table_allocated_bytes":if pair_mode==PairMode::Full {0} else {quotient_pairs.allocated_bytes()},
                "support_x_prefilter_kind":quotient_pairs.x_filter_kind(),
                "support_x_prefilter_bits":quotient_pairs.x_filter_bits(),
                "support_x_prefilter_hash_strategy":quotient_pairs.x_filter_hash_strategy(),
                "support_x_prefilter_insert_hash_reuse":quotient_pairs.x_filter_insert_hash_reuse(),
                "support_x_prefilter_direct_bits":quotient_pairs.x_filter_direct_bits(),
                "support_x_prefilter_blocked":quotient_pairs.x_filter_blocked(),
                "base_hash":&base_hash,
                "pair_index_mode":pair_mode.name(),
                "query_mode":query_mode.name(),
                "target_mode":target_mode.name(),
                "rank_plus_32_fixtures":batch_rank_plus_32,
                "all_fixtures_rank_plus_32":batch_rank_plus_32==batch_fixtures,
                "all_relations_group_verified":true,
                "all_relations_reference_validated":true,
                "total_target_trials":batch_target_trials,
                "total_admitted_relations":batch_admitted_relations,
                "total_support_queries":batch_support_queries,
                "curve_setup_ms":curve_setup_ms,
                "support_setup_ms":setup_ms,
                "online_charged_ms":batch_online_charged_ms,
                "projection_matched_charged_total_ms":setup_ms+batch_online_charged_ms,
                "full_algorithm_charged_total_ms":curve_setup_ms+setup_ms+batch_online_charged_ms,
                "fixture_generation_evidence_ms":batch_fixture_generation_ms,
                "reference_validation_evidence_ms":batch_reference_validation_ms,
                "observed_batch_section_ms":observed_batch_section_ms,
                "scope":"deterministic public synthetic fixtures only; no external point, unknown scalar, production key, or key recovery claim"
            })
        );
    }
}

#[cfg(test)]
mod packed_tests {
    use super::*;

    #[test]
    fn packed_field_and_group_operations_match_reference() {
        for (n, a) in [(7, 1), (11, 1), (13, 0), (17, 1), (19, 1), (23, 1)] {
            let curve = KoblitzCurve::new(a, n).unwrap();
            let mask = (1u64 << n) - 1;
            let mut state = 0x9e37_79b9_7f4a_7c15u64 ^ n as u64;
            for _ in 0..256 {
                state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                let left = state & mask;
                state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                let right = state & mask;
                let left_fe = F2mElement::from_biguint(&BigUint::from(left), n);
                let right_fe = F2mElement::from_biguint(&BigUint::from(right), n);
                assert_eq!(
                    square_raw(&curve, left),
                    left_fe
                        .square(&curve.curve.irreducible)
                        .raw_bits()
                        .first()
                        .copied()
                        .unwrap_or(0)
                );
                assert_eq!(
                    mul_raw(&curve, left, right),
                    left_fe
                        .mul(&right_fe, &curve.curve.irreducible)
                        .raw_bits()
                        .first()
                        .copied()
                        .unwrap_or(0)
                );
                if left != 0 {
                    assert_eq!(
                        inverse_raw(&curve, left),
                        left_fe
                            .flt_inverse(&curve.curve.irreducible)
                            .unwrap()
                            .raw_bits()
                            .first()
                            .copied()
                            .unwrap_or(0)
                    );
                }
            }
            let generator_raw = to_raw_point(curve.generator());
            for scalar in 0..64u64 {
                assert_eq!(
                    raw_scalar_point(&curve, generator_raw, scalar),
                    to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar)))
                );
            }
            let target = curve.mul(curve.generator(), &BigUint::from(71u64));
            let points: Vec<_> = (1..=48u64)
                .map(|scalar| curve.mul(curve.generator(), &BigUint::from(scalar)))
                .collect();
            let reference = batch_target_minus_keys(&curve, &target, &points);
            let packed = batch_raw_target_minus_keys(
                &curve,
                to_raw_point(&target),
                &points.iter().map(to_raw_point).collect::<Vec<_>>(),
            );
            assert_eq!(packed, reference);
            for x in 0..(1u64 << n).min(512) {
                let reference_points: HashSet<_> = points_with_x(
                    &curve.curve,
                    &F2mElement::from_biguint(&BigUint::from(x), n),
                )
                .iter()
                .map(to_raw_point)
                .collect();
                let packed_points: HashSet<_> = raw_points_with_x(&curve, x).into_iter().collect();
                assert_eq!(packed_points, reference_points, "n={n}, x={x}");
            }
            if curve.cofactor == BigUint::from(2u8) {
                let wanted = balanced_orbits(&curve.subgroup_order, 2 * n as usize, 1, 1);
                let packed_base = point_defined_base(&curve, wanted);
                let reference_base = reference_point_defined_base(&curve, wanted);
                assert_eq!(
                    packed_base
                        .representatives
                        .iter()
                        .map(point_key)
                        .collect::<Vec<_>>(),
                    reference_base
                        .representatives
                        .iter()
                        .map(point_key)
                        .collect::<Vec<_>>()
                );
                assert_eq!(packed_base.point_labels, reference_base.point_labels);
            }
        }
    }

    #[test]
    fn x_filter_and_lazy_y_recovery_match_full_fiber_batch() {
        let curve = KoblitzCurve::new(1, 23).unwrap();
        let raw_points: Vec<_> = (1..=48u64)
            .map(|scalar| to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar))))
            .collect();
        let fibers = raw_fibers(&raw_points);
        assert!(fibers.len() <= 64);
        let target = to_raw_point(&curve.mul(curve.generator(), &BigUint::from(71u64)));
        let mut full = Vec::new();
        batch_raw_target_minus_fibers(&curve, target, &fibers, &mut full);

        for x_domain in [(1usize << 23) + 1, (1usize << 37) + 1] {
            let mut table = CompactPairTable::with_capacity(16, true, x_domain);
            for (position, &(_, key)) in full.iter().enumerate() {
                if position % 5 == 0 {
                    table.insert(key, QuotientPairWitness::default());
                }
            }
            let expected: Vec<_> = full
                .iter()
                .copied()
                .filter(|(_, key)| table.might_contain_x(key.0))
                .collect();
            let mut filtered = Vec::new();
            let attempted = batch_raw_target_minus_fibers_x_filtered(
                &curve,
                target,
                &fibers,
                &table,
                &mut filtered,
            );
            assert_eq!(attempted, full.len());
            assert_eq!(filtered, expected);
            assert!(filtered.len() < full.len());
            let pointwise_full = batch_raw_target_minus_keys(&curve, target, &raw_points);
            let pointwise_expected: Vec<_> = pointwise_full
                .iter()
                .copied()
                .enumerate()
                .filter(|(_, key)| table.might_contain_x(key.0))
                .collect();
            let mut pointwise_filtered = Vec::new();
            let mut pointwise_scratch = RawBatchScratch::default();
            let pointwise_attempted = batch_raw_target_minus_points_x_filtered(
                &curve,
                target,
                &raw_points,
                &table,
                &mut pointwise_filtered,
                &mut pointwise_scratch,
            );
            assert_eq!(pointwise_attempted, raw_points.len());
            assert_eq!(pointwise_filtered, pointwise_expected);
            for (_, key) in full.iter().step_by(5) {
                assert!(table.might_contain_x(key.0));
                assert!(table.get(*key).is_some());
            }
        }
    }

    #[test]
    fn dual_sign_batch_matches_separate_signed_inputs() {
        let curve = KoblitzCurve::new(1, 23).unwrap();
        let target = to_raw_point(&curve.mul(curve.generator(), &BigUint::from(71u64)));
        let points: Vec<_> = (1..=48u64)
            .map(|scalar| to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar))))
            .collect();
        let mut signed_points = Vec::with_capacity(points.len() * 2);
        let mut signed_positions = Vec::with_capacity(points.len() * 2);
        for (position, &point) in points.iter().enumerate() {
            signed_points.push(point);
            signed_positions.push((position, false));
            if point.is_some() {
                signed_points.push(raw_neg_point(point));
                signed_positions.push((position, true));
            }
        }

        let keys = batch_raw_target_minus_keys(&curve, target, &signed_points);
        let mut table = CompactPairTable::with_capacity(keys.len() * 2, true, (1 << 23) + 1);
        for &key in &keys {
            table.insert(key, QuotientPairWitness::default());
        }

        let mut separate = Vec::new();
        let mut separate_scratch = RawBatchScratch::default();
        let separate_attempted = batch_raw_target_minus_points_x_filtered(
            &curve,
            target,
            &signed_points,
            &table,
            &mut separate,
            &mut separate_scratch,
        );
        let separate_normalized: Vec<_> = separate
            .into_iter()
            .map(|(position, key)| {
                let (point_position, negative) = signed_positions[position];
                (point_position, negative, key)
            })
            .collect();

        let mut dual = Vec::new();
        let mut dual_scratch = RawBatchScratch::default();
        let dual_attempted = batch_raw_target_minus_signed_points_x_filtered(
            &curve,
            target,
            &points,
            &table,
            &mut dual,
            &mut dual_scratch,
        );
        assert_eq!(dual_attempted, separate_attempted);
        assert_eq!(dual, separate_normalized);
        assert_eq!(dual_scratch.denominators.len() * 2, signed_points.len());

        let compact_points: Vec<_> = points.iter().copied().map(raw_compact_key).collect();
        let mut compact = Vec::new();
        let mut compact_scratch = RawBatchScratch::default();
        let compact_attempted = batch_compact_target_minus_signed_points_x_filtered(
            &curve,
            target,
            &compact_points,
            &table,
            &mut compact,
            &mut compact_scratch,
        );
        assert_eq!(compact_attempted, dual_attempted);
        assert_eq!(compact, dual);
        assert!(
            std::mem::size_of::<(u64, u64)>() < std::mem::size_of::<RawPoint>(),
            "compact point scratch must reduce each entry"
        );
    }

    #[test]
    fn bloom_hash_strategies_retain_every_inserted_x() {
        for blocked in [false, true] {
            for direct_bits in [false, true] {
                for split_hash in [false, true] {
                    for reuse_insert_hash in [false, true] {
                        for degree in [23, 37] {
                            let mut table =
                                CompactPairTable::with_capacity(512, true, (1usize << degree) + 1);
                            table.x_filter_split_hash = split_hash;
                            table.x_filter_insert_hash_reuse = reuse_insert_hash;
                            table.x_filter_direct_bits = direct_bits;
                            table.x_filter_blocked = blocked;
                            let keys: Vec<_> = (0..512u64)
                                .map(|index| {
                                    let x = CompactPairTable::hash((index, index.rotate_left(17)))
                                        & ((1u64 << degree) - 1);
                                    (x + 1, index)
                                })
                                .collect();
                            for &key in &keys {
                                table.insert(key, QuotientPairWitness::default());
                            }
                            for &key in &keys {
                                assert!(table.might_contain_x(key.0));
                                assert!(table.get(key).is_some());
                            }
                        }
                    }
                }
            }
        }
    }

    #[cfg(target_arch = "x86_64")]
    #[test]
    fn specialized_n53_pair_batch_matches_generic() {
        if !combined_n53_fast_path_enabled() {
            return;
        }
        let curve = KoblitzCurve::new(0, 53).unwrap();
        let mask = (1u64 << 53) - 1;
        let mut inverse_state = 0xd6e8_feb8_6659_fd93u64;
        for _ in 0..256 {
            inverse_state = inverse_state
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1);
            let value = (inverse_state & mask).max(1);
            let binary = unsafe { inverse_n53_binary_unchecked(value) };
            let itoh = unsafe { inverse_n53_itoh_unchecked(value) };
            assert_eq!(itoh, binary);
            assert_eq!(unsafe { pclmul_reduce_n53(value, itoh) }, 1);
        }
        let target = to_raw_point(&curve.mul(curve.generator(), &BigUint::from(71u64)));
        let points: Vec<_> = (1..=48u64)
            .map(|scalar| to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar))))
            .collect();
        let mut signed_points = Vec::with_capacity(points.len() * 2);
        for &point in &points {
            signed_points.push(point);
            signed_points.push(raw_neg_point(point));
        }
        let keys = batch_raw_target_minus_keys(&curve, target, &signed_points);
        let mut table = CompactPairTable::with_capacity(keys.len() * 2, true, (1usize << 53) + 1);
        for &key in &keys {
            table.insert(key, QuotientPairWitness::default());
        }
        let compact_points: Vec<_> = points.iter().copied().map(raw_compact_key).collect();
        let mut generic = Vec::new();
        let mut generic_scratch = RawBatchScratch::default();
        let generic_attempted = batch_compact_target_minus_signed_points_x_filtered(
            &curve,
            target,
            &compact_points,
            &table,
            &mut generic,
            &mut generic_scratch,
        );
        let mut specialized = Vec::new();
        let mut specialized_scratch = RawBatchScratch::default();
        let specialized_attempted = unsafe {
            batch_compact_n53_target_minus_signed_points_x_filtered(
                &curve,
                target,
                &compact_points,
                &table,
                &mut specialized,
                &mut specialized_scratch,
            )
        };
        assert_eq!(specialized_attempted, generic_attempted);
        assert_eq!(specialized, generic);
        assert_eq!(
            specialized_scratch.denominators,
            generic_scratch.denominators
        );
        assert_eq!(
            specialized_scratch.prefixes_and_inverses,
            generic_scratch.prefixes_and_inverses
        );
    }

    #[cfg(target_arch = "x86_64")]
    #[test]
    fn specialized_n53_support_expansion_matches_generic() {
        if !combined_n53_fast_path_enabled() {
            return;
        }
        let curve = KoblitzCurve::new(0, 53).unwrap();
        let generator = to_raw_point(curve.generator());
        let jobs: Vec<PairExpansionJob> = (0..16usize)
            .map(|index| (index, index, 1, index, (index + 1) % 16))
            .collect();
        let sum_keys: Vec<_> = (0..16u64)
            .map(|index| raw_compact_key(raw_scalar_point(&curve, generator, index + 1)))
            .collect();
        let frobenius_next_index: Vec<_> = (0..16usize).collect();
        let generic = expand_support_batch(&curve, &jobs, &sum_keys, &frobenius_next_index, 4);
        let specialized =
            unsafe { expand_support_batch_n53(&curve, &jobs, &sum_keys, &frobenius_next_index, 4) };
        assert_eq!(specialized, generic);
    }

    #[cfg(target_arch = "x86_64")]
    #[test]
    fn specialized_n53_pair_sums_match_generic() {
        if !combined_n53_fast_path_enabled() {
            return;
        }
        let curve = KoblitzCurve::new(0, 53).unwrap();
        let generator = to_raw_point(curve.generator());
        let mut points: Vec<_> = (1..=48u64)
            .map(|scalar| raw_scalar_point(&curve, generator, scalar))
            .collect();
        points.push(None);
        let mut pairs = Vec::new();
        for index in 0..points.len() {
            pairs.push((points[index], points[(index * 17 + 3) % points.len()]));
            pairs.push((points[index], points[index]));
        }
        let generic = batch_raw_add_keys(&curve, &pairs);
        let specialized = unsafe { batch_raw_add_keys_n53(&curve, &pairs) };
        assert_eq!(specialized, generic);
    }

    #[test]
    fn packed_n37_field_group_and_point_defined_base_validate() {
        let curve = KoblitzCurve::new(0, 37).unwrap();
        assert_eq!(curve.subgroup_order, BigUint::from(230_603_167u64));
        assert_eq!(curve.cofactor, BigUint::from(596u64));
        let mask = (1u64 << 37) - 1;
        let mut state = 0x9e37_79b9_7f4a_7c15u64;
        for index in 0..64 {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let left = state & mask;
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let right = state & mask;
            let left_fe = F2mElement::from_biguint(&BigUint::from(left), 37);
            let right_fe = F2mElement::from_biguint(&BigUint::from(right), 37);
            assert_eq!(
                square_raw(&curve, left),
                left_fe
                    .square(&curve.curve.irreducible)
                    .raw_bits()
                    .first()
                    .copied()
                    .unwrap_or(0)
            );
            assert_eq!(
                mul_raw(&curve, left, right),
                left_fe
                    .mul(&right_fe, &curve.curve.irreducible)
                    .raw_bits()
                    .first()
                    .copied()
                    .unwrap_or(0)
            );
            if index < 16 && left != 0 {
                assert_eq!(
                    inverse_raw(&curve, left),
                    left_fe
                        .flt_inverse(&curve.curve.irreducible)
                        .unwrap()
                        .raw_bits()
                        .first()
                        .copied()
                        .unwrap_or(0)
                );
            }
        }
        let generator = to_raw_point(curve.generator());
        for scalar in 0..32u64 {
            assert_eq!(
                raw_scalar_point(&curve, generator, scalar),
                to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar)))
            );
        }
        let base = point_defined_base(&curve, 1);
        assert_eq!(base.representatives.len(), 1);
        assert_eq!(base.points.len(), 74);
        assert!(base
            .points
            .iter()
            .all(|point| { curve.mul(point, &curve.subgroup_order) == BinaryPoint::Infinity }));
    }

    #[test]
    fn packed_n41_field_group_and_point_defined_base_validate() {
        let curve = KoblitzCurve::new(0, 41).unwrap();
        assert_eq!(curve.subgroup_order, BigUint::from(549_756_390_943u64));
        assert_eq!(curve.cofactor, BigUint::from(4u64));
        let mask = (1u64 << 41) - 1;
        let mut state = 0xd6e8_feb8_6659_fd93u64;
        for index in 0..32 {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let left = state & mask;
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let right = state & mask;
            let left_fe = F2mElement::from_biguint(&BigUint::from(left), 41);
            let right_fe = F2mElement::from_biguint(&BigUint::from(right), 41);
            assert_eq!(
                square_raw(&curve, left),
                left_fe
                    .square(&curve.curve.irreducible)
                    .raw_bits()
                    .first()
                    .copied()
                    .unwrap_or(0)
            );
            assert_eq!(
                mul_raw(&curve, left, right),
                left_fe
                    .mul(&right_fe, &curve.curve.irreducible)
                    .raw_bits()
                    .first()
                    .copied()
                    .unwrap_or(0)
            );
            if index < 8 && left != 0 {
                assert_eq!(
                    inverse_raw(&curve, left),
                    left_fe
                        .flt_inverse(&curve.curve.irreducible)
                        .unwrap()
                        .raw_bits()
                        .first()
                        .copied()
                        .unwrap_or(0)
                );
            }
        }
        let generator = to_raw_point(curve.generator());
        for scalar in 0..16u64 {
            assert_eq!(
                raw_scalar_point(&curve, generator, scalar),
                to_raw_point(&curve.mul(curve.generator(), &BigUint::from(scalar)))
            );
        }
        let base = point_defined_base(&curve, 1);
        assert_eq!(base.representatives.len(), 1);
        assert_eq!(base.points.len(), 82);
        assert!(base
            .points
            .iter()
            .all(|point| { curve.mul(point, &curve.subgroup_order) == BinaryPoint::Infinity }));
    }

    #[test]
    fn forward_and_reverse_incremental_ranks_match_dense_elimination() {
        let modulus = 991u64;
        let mut state = 0x94d0_49bb_1331_11ebu64;
        for columns in 2..=12 {
            let mut rows = Vec::new();
            let mut forward = Echelon::new(columns);
            let mut reverse = ReverseEchelon::new(columns);
            for _ in 0..64 {
                let row: Vec<_> = (0..columns)
                    .map(|_| {
                        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                        state % modulus
                    })
                    .collect();
                rows.push(row.clone());
                forward.insert(row.clone(), modulus);
                reverse.insert(row, modulus);
                let dense = dense_rank(&rows, columns, modulus);
                assert_eq!(forward.rank, dense);
                assert_eq!(reverse.rank, dense);
            }
        }
    }

    #[test]
    fn full_rank_solver_recovers_unique_public_solution() {
        let modulus = 991u64;
        let solution = vec![137u64, 503, 947];
        let rows = vec![
            vec![1, 0, 0],
            vec![0, 1, 0],
            vec![0, 0, 1],
            vec![17, 29, 41],
        ];
        let right_hand_sides = rows
            .iter()
            .map(|row| {
                row.iter()
                    .zip(&solution)
                    .fold(0u64, |sum, (&left, &right)| {
                        (sum + ((left as u128 * right as u128) % modulus as u128) as u64) % modulus
                    })
            })
            .collect::<Vec<_>>();
        assert_eq!(
            solve_full_column_rank_system(&rows, &right_hand_sides, 3, modulus),
            Some(solution)
        );
    }
}

#[cfg(test)]
mod target_certificate_tests {
    use super::*;

    fn named_ranks(rows: &[Vec<u64>], variables: usize, modulus: u64) -> (usize, usize, usize) {
        let target_column = variables - 1;
        let mut rank_a = Echelon::new(target_column);
        let mut rank_a_b = Echelon::new(variables);
        let mut rank_a_b_a = Echelon::new(variables + 1);
        for row in rows {
            rank_a.insert(row[..target_column].to_vec(), modulus);
            rank_a_b.insert(row[..variables].to_vec(), modulus);
            rank_a_b_a.insert(row.clone(), modulus);
        }
        (rank_a.rank, rank_a_b.rank, rank_a_b_a.rank)
    }

    fn insert_rows(rows: &[Vec<u64>], modulus: u64) -> (AffineCertificateEchelon, Option<TargetCertificate>, bool) {
        let variables = rows[0].len() - 1;
        let mut tracker = AffineCertificateEchelon::new(variables, variables - 1);
        let mut certificate = None;
        let mut inconsistent = false;
        for row in rows {
            match tracker.insert(row[..variables].to_vec(), row[variables], modulus) {
                AffineInsertOutcome::TargetIdentified(value) => {
                    certificate = Some(value);
                    break;
                }
                AffineInsertOutcome::Inconsistent => {
                    inconsistent = true;
                    break;
                }
                AffineInsertOutcome::Dependent | AffineInsertOutcome::Pivot(_) => {}
            }
        }
        (tracker, certificate, inconsistent)
    }

    fn early_rows(modulus: u64) -> Vec<Vec<u64>> {
        vec![
            vec![1, 1, 0, 1, 12 % modulus],
            vec![1, 1, 0, 2, 19 % modulus],
        ]
    }

    #[test]
    fn early_target_certificate_and_negative_checker_controls() {
        for modulus in [17u64, 21_044_858_204_113] {
            let rows = early_rows(modulus);
            assert_eq!(named_ranks(&rows, 4, modulus), (1, 2, 2));
            let (_tracker, certificate, inconsistent) = insert_rows(&rows, modulus);
            assert!(!inconsistent);
            let certificate = certificate.unwrap();
            assert_eq!(certificate.returned_d, 7);
            assert_eq!(certificate.prefix_rows, 2);
            assert_eq!(certificate.weights, vec![modulus - 1, 1]);
            let coefficients: Vec<_> = rows.iter().map(|row| row[..4].to_vec()).collect();
            let rhs: Vec<_> = rows.iter().map(|row| row[4]).collect();
            assert!(recompute_target_certificate(
                &coefficients, &rhs, &certificate.weights, 3, 7, modulus
            ).valid);
            let mut mutated = certificate.weights.clone();
            mutated[0] = (mutated[0] + 1) % modulus;
            assert!(!recompute_target_certificate(
                &coefficients, &rhs, &mutated, 3, 7, modulus
            ).valid);
            let doubled: Vec<_> = certificate.weights.iter().map(|&value| mod_mul(value, 2, modulus)).collect();
            let wrong_wb = recompute_target_certificate(&coefficients, &rhs, &doubled, 3, 7, modulus);
            assert_eq!(wrong_wb.w_b, 2);
            assert!(!wrong_wb.valid);
            assert!(!recompute_target_certificate(
                &coefficients, &rhs, &certificate.weights, 3, 8, modulus
            ).valid);
        }
    }

    #[test]
    fn zero_b_never_identifies_and_target_unit_does() {
        for modulus in [17u64, 21_044_858_204_113] {
            let zero_b = vec![
                vec![1, 1, 0, 0, 5],
                vec![0, 1, 1, 0, 8],
                vec![1, 0, 0, 0, 2],
            ];
            let (_, certificate, inconsistent) = insert_rows(&zero_b, modulus);
            assert!(!inconsistent);
            assert!(certificate.is_none());
            let unit = vec![vec![0, 0, 0, 1, 7]];
            let (_, certificate, inconsistent) = insert_rows(&unit, modulus);
            assert!(!inconsistent);
            assert_eq!(certificate.unwrap().returned_d, 7);
        }
    }

    #[test]
    fn duplicate_rescale_preserves_target_and_inconsistent_rhs_is_explicit() {
        for modulus in [17u64, 21_044_858_204_113] {
            let first = early_rows(modulus)[0].clone();
            let second = early_rows(modulus)[1].clone();
            let scaled: Vec<_> = first.iter().map(|&value| mod_mul(value, 3, modulus)).collect();
            let rows = vec![first.clone(), first.clone(), scaled, second];
            let (_, certificate, inconsistent) = insert_rows(&rows, modulus);
            assert!(!inconsistent);
            assert_eq!(certificate.unwrap().returned_d, 7);
            let mut bad = first.clone();
            bad[4] = (bad[4] + 1) % modulus;
            let (_, certificate, inconsistent) = insert_rows(&[first, bad], modulus);
            assert!(inconsistent);
            assert!(certificate.is_none());
        }
    }

    #[test]
    fn k75_certificate_identifies_at_row_74_with_expected_weights() {
        for modulus in [17u64, 21_044_858_204_113] {
            let factor_values: Vec<_> = (0..75).map(|column| (column as u64 + 2) % modulus).collect();
            let mut rows = Vec::new();
            for column in 0..72 {
                let mut row = vec![0u64; 77];
                row[column] = 1;
                row[76] = factor_values[column];
                rows.push(row);
            }
            let mut row73 = vec![0u64; 77];
            let mut rhs73 = 7u64;
            for column in 0..72 {
                row73[column] = (column as u64 + 1) % modulus;
                rhs73 = ((rhs73 as u128
                    + mod_mul(row73[column], factor_values[column], modulus) as u128)
                    % modulus as u128) as u64;
            }
            row73[74] = 1;
            rhs73 = (rhs73 + factor_values[74]) % modulus;
            row73[75] = 1;
            row73[76] = rhs73;
            rows.push(row73);
            let mut row74 = vec![0u64; 77];
            let mut rhs74 = 14u64 % modulus;
            for column in 0..72 {
                row74[column] = (2 * (column as u64 + 1)) % modulus;
                rhs74 = ((rhs74 as u128
                    + mod_mul(row74[column], factor_values[column], modulus) as u128)
                    % modulus as u128) as u64;
            }
            row74[74] = 1;
            rhs74 = (rhs74 + factor_values[74]) % modulus;
            row74[75] = 2;
            row74[76] = rhs74;
            rows.push(row74);
            let (tracker, certificate, inconsistent) = insert_rows(&rows, modulus);
            assert!(!inconsistent);
            let certificate = certificate.unwrap();
            assert_eq!(certificate.prefix_rows, 74);
            assert_eq!(certificate.rank_a_b, 74);
            assert_eq!(tracker.rank_a_b, 74);
            assert_eq!(named_ranks(&rows, 76, modulus), (73, 74, 74));
            assert_eq!(certificate.returned_d, 7);
            let expected: Vec<_> = (0..72)
                .map(|column| (modulus - ((column as u64 + 1) % modulus)) % modulus)
                .chain([modulus - 1, 1])
                .collect();
            assert_eq!(certificate.weights, expected);
            let coefficients: Vec<_> = rows.iter().map(|row| row[..76].to_vec()).collect();
            let rhs: Vec<_> = rows.iter().map(|row| row[76]).collect();
            assert!(recompute_target_certificate(
                &coefficients, &rhs, &certificate.weights, 75, 7, modulus
            ).valid);
        }
    }
}

#[cfg(all(test, target_arch = "aarch64"))]
mod cold_arm_port_tests {
    use super::*;
    fn bitwise_product(a: u64, b: u64) -> u128 {
        let mut p = 0u128;
        for i in 0..64 { if (b >> i) & 1 != 0 { p ^= (a as u128) << i; } }
        p
    }
    fn bitwise_reduce(curve: &KoblitzCurve, mut p: u128) -> u64 {
        let mut modulus = 1u128 << curve.n;
        for &term in &curve.curve.irreducible.low_terms { modulus ^= 1u128 << term; }
        for i in (curve.n..128).rev() {
            if (p >> i) & 1 != 0 { p ^= modulus << (i - curve.n); }
        }
        p as u64
    }
    #[test]
    fn pmull_matches_independent_bitwise_edges_and_corpus() {
        assert!(arm_pmull_enabled(), "this ARM fairness gate requires available PMULL");
        let edge = [0, 1, u64::MAX, 1u64 << 63, (1u64 << 53)-1, (1u64 << 13)-1, 0xaaaaaaaaaaaaaaaa, 0x5555555555555555];
        for &a in &edge { for &b in &edge {
            assert_eq!(unsafe { arm_pmull_product(a,b) }, bitwise_product(a,b));
        }}
        let mut x = 0x8a5cd789635d2dffu64;
        for _ in 0..256 {
            x ^= x << 13; x ^= x >> 7; x ^= x << 17;
            let y = x.rotate_left(29) ^ 0x6a09e667f3bcc909;
            assert_eq!(unsafe { arm_pmull_product(x,y) }, bitwise_product(x,y));
            assert_eq!(unsafe { arm_pmull_product(x,x) }, bitwise_product(x,x));
        }
    }
    #[test]
    fn reduced_n13_n53_operations_match_independent_bitwise_oracle() {
        assert!(arm_pmull_enabled());
        for n in [13u32,53] {
            let curve = KoblitzCurve::new(0,n).unwrap();
            let mask = (1u64 << n)-1;
            let mut x = 0xd1b54a32d192ed03u64;
            for i in 0..256 {
                x ^= x << 13; x ^= x >> 7; x ^= x << 17;
                let a = if i == 0 {0} else if i == 1 {mask} else {x & mask};
                let b = x.rotate_left(17) & mask;
                assert_eq!(mul_raw(&curve,a,b),bitwise_reduce(&curve,bitwise_product(a,b)));
                assert_eq!(square_raw(&curve,a),bitwise_reduce(&curve,bitwise_product(a,a)));
            }
        }
    }
}
