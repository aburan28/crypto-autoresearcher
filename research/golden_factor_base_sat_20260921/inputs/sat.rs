//! From-scratch CDCL SAT solver for cryptanalytic boolean problems.
//!
//! Modern SAT solving for cryptanalysis goes back to Massacci-Marraro
//! (2000) and exploded after Soos-Nohl-Castelluccia's CryptoMiniSat
//! (2009) added XOR-clause reasoning. The technique is now standard for:
//!
//! - **Algebraic attacks**: solve the polynomial system describing a
//!   reduced-round cipher (see `cryptanalysis::aes::algebraic`).
//! - **Differential trail search**: encode active S-box constraints as
//!   clauses (Mouha-Preneel 2013, Sun et al. 2014).
//! - **Index calculus**: decide whether a point decomposes over a
//!   factor base (see [`crate::cryptanalysis::semaev_sat`]).
//! - **Preimage / collision search**: encode reduced hash functions.
//!
//! This module ships a **Conflict-Driven Clause Learning (CDCL)** SAT
//! solver from scratch — no external crate:
//!
//! - Two-watched-literal unit propagation,
//! - 1-UIP conflict analysis with clause learning and local
//!   minimization,
//! - Non-chronological backjumping,
//! - VSIDS variable activity over a position-tracked heap,
//! - Phase saving and Luby-sequence restarts,
//! - Periodic learnt-clause forgetting.
//!
//! # Two features that matter for algebraic cryptanalysis
//!
//! Both exist because the systems this solver is pointed at are not
//! generic CNF — they are *gate-structured parity systems*, and a
//! solver that treats them as opaque clauses does badly on them.
//!
//! **Native XOR constraints** ([`Solver::add_xor`]).  Parity rows are
//! held outside the CNF and reasoned about by Gauss-Jordan elimination
//! interleaved with unit propagation.  Refuting a dense parity
//! constraint by resolution alone takes exponentially many steps
//! (Urquhart 1987), so a plain CDCL has to rediscover linear algebra
//! one conflict at a time.
//!
//! **Branching priority** ([`Solver::set_branch_priority`]).  In a gate
//! encoding most variables are *defined* by others; deciding one is
//! case-splitting on something propagation already knew.  Naming the
//! genuinely free variables collapses the search tree to `2^(free)`.
//! On a Weil-descended Semaev system that is the single largest win
//! available — `2^18` rather than `2^767`.
//!
//! It is **not competitive** with state-of-the-art solvers like kissat
//! on general CNF: the data layout follows the textbook and there is no
//! inprocessing, vivification, or LBD-based clause scoring.
//!
//! ## DIMACS I/O
//!
//! [`parse_dimacs`] parses the standard `.cnf` format; [`to_dimacs`]
//! emits it; [`parse_dimacs_xor`] additionally reads CryptoMiniSat's
//! `x`-prefixed parity lines.  This lets you round-trip with `kissat`,
//! `cadical`, or `cryptominisat` while developing.
//!
//! ## Worked example
//!
//! ```
//! use crypto::cryptanalysis::sat::{Solver, SolveResult};
//!
//! let mut s = Solver::new(3);
//! // (x1 ∨ x2) ∧ (¬x1 ∨ x3) ∧ (¬x2 ∨ ¬x3)
//! s.add_clause(vec![1, 2]);
//! s.add_clause(vec![-1, 3]);
//! s.add_clause(vec![-2, -3]);
//! assert!(matches!(s.solve(), SolveResult::Sat));
//! let model = s.model();
//! // Verify the model satisfies all clauses.
//! ```
//!
//! ## References
//!
//! - **N. Eén, N. Sörensson**, *An extensible SAT-solver*, SAT 2003 —
//!   the MiniSat design this follows.
//! - **M. Soos, K. Nohl, C. Castelluccia**, *Extending SAT solvers to
//!   cryptographic problems*, SAT 2009 — XOR-native reasoning.
//! - **A. Urquhart**, *Hard examples for resolution*, JACM 1987.

use std::collections::HashSet;

/// Standard SAT literal encoding: positive integer = positive
/// literal, negative integer = negated literal, `|lit| - 1` = variable
/// index (0-based internally; 1-based in DIMACS).
pub type Lit = i32;

#[inline]
fn var_of(lit: Lit) -> u32 {
    (lit.unsigned_abs() - 1) as u32
}

#[inline]
fn is_neg(lit: Lit) -> bool {
    lit < 0
}

/// A watch-list entry: the clause, plus one of its other literals.
///
/// The **blocker** is checked first.  If it is already true the clause
/// is satisfied and can be skipped without dereferencing it at all —
/// which is the point, since every clause is its own heap allocation
/// and touching one is a cache miss.
#[derive(Debug, Clone, Copy)]
struct Watcher {
    cref: usize,
    blocker: Lit,
}

/// Decision levels bucketed into 32 bits, so "could this literal's
/// reason stay inside the clause's levels?" is one AND.
#[inline]
fn abstract_level(level: i32) -> u32 {
    1u32 << (level & 31)
}

/// Outcome of solving.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SolveResult {
    Sat,
    Unsat,
    /// Hit conflict / restart budget without resolving.
    Unknown,
}

/// Reason a literal was assigned: a free decision, a unit-propagation
/// source clause, or a parity row.
#[derive(Debug, Clone, Copy)]
enum Reason {
    Decision,
    Propagated(usize), // clause index in `clauses`
    /// Implied by a reduced XOR row.  The reason clause lives in
    /// `xor_reason[var]` and is rewritten in place on each such
    /// implication, so parity reasoning does not grow the clause
    /// database — an earlier version pushed one clause per parity
    /// implication and never reclaimed it.
    XorPropagated,
}

/// What `propagate` ran into.
#[derive(Debug, Clone, Copy)]
enum Conflict {
    /// The clause at this index is falsified.
    Clause(usize),
    /// A parity row is inconsistent; the falsified clause witnessing it
    /// is in `xor_conflict`.
    Xor,
}

/// Counters for one solve.  Cheap to maintain and the only way to tell
/// which engine is actually costing the time.
#[derive(Debug, Clone, Copy, Default)]
pub struct SolverStats {
    pub decisions: u64,
    pub conflicts: u64,
    pub restarts: u64,
    /// Literals assigned by clause propagation.
    pub propagations: u64,
    /// Gauss-Jordan passes run.
    pub xor_passes: u64,
    /// Literals implied by a parity row.
    pub xor_propagations: u64,
    pub xor_conflicts: u64,
    /// Times a row had to choose a new pivot, the only work the
    /// incremental matrix does beyond a popcount per row.
    pub xor_repivots: u64,
    pub learnt_clauses: u64,

    // ── work counters ───────────────────────────────────────────────
    // Proxies for where the time goes.  Timing each call would cost
    // more than the calls do; counting the operations does not.
    /// Row-into-row XORs performed by re-pivoting, each `O(words)`.
    pub xor_row_ops: u64,
    /// Rows examined in the parity read-off, each `O(words)`.
    pub xor_row_scans: u64,
    /// Literals written into parity reason clauses.
    pub xor_reason_lits: u64,
    /// Clauses examined by watched-literal propagation.
    pub clause_visits: u64,
    /// Literals scanned while looking for a replacement watch.
    pub clause_lit_visits: u64,
    /// Literals walked across reason clauses during conflict analysis.
    pub analyze_lit_visits: u64,
    /// Literals in learnt clauses, before and after minimization.
    pub learnt_lits_raw: u64,
    pub learnt_lits_kept: u64,
    // ── phase timings, in nanoseconds ───────────────────────────────
    // `Instant::now` costs ~25 ns against ~80 µs per conflict, so
    // timing the phases directly is cheaper than guessing at them.
    pub ns_propagate_clauses: u64,
    pub ns_propagate_xors: u64,
    pub ns_analyze: u64,
    pub ns_minimize: u64,
    pub ns_reduce_db: u64,
    /// Summed decision level at conflict, and the deepest level seen.
    /// If the free-variable set really determines everything, the level
    /// should never exceed the number of free variables.
    pub conflict_level_sum: u64,
    pub max_level: u64,
}

/// Max-heap of variables by VSIDS activity, with position tracking so a
/// bumped variable percolates up in place.
///
/// Replaces a linear scan over every variable per decision, which on an
/// `n = 19` Semaev instance meant 767 comparisons for each of millions
/// of decisions.
#[derive(Debug, Clone)]
struct VarHeap {
    heap: Vec<u32>,
    /// `pos[v]` is `v`'s index in `heap`, or `-1` when absent.
    pos: Vec<i32>,
}

/// Branching order key: priority class first, then VSIDS activity.
#[inline]
fn key_gt(a: u32, b: u32, act: &[f64], prio: &[bool]) -> bool {
    let (pa, pb) = (prio[a as usize], prio[b as usize]);
    if pa != pb {
        return pa;
    }
    act[a as usize] > act[b as usize]
}

impl VarHeap {
    fn new(n_vars: u32) -> Self {
        // With all activities equal, any permutation is a valid heap.
        Self {
            heap: (0..n_vars).collect(),
            pos: (0..n_vars as i32).collect(),
        }
    }

    #[inline]
    fn contains(&self, v: u32) -> bool {
        self.pos[v as usize] >= 0
    }

    fn percolate_up(&mut self, mut i: usize, act: &[f64], prio: &[bool]) {
        let v = self.heap[i];
        while i > 0 {
            let parent = (i - 1) >> 1;
            if !key_gt(v, self.heap[parent], act, prio) {
                break;
            }
            self.heap[i] = self.heap[parent];
            self.pos[self.heap[i] as usize] = i as i32;
            i = parent;
        }
        self.heap[i] = v;
        self.pos[v as usize] = i as i32;
    }

    fn percolate_down(&mut self, mut i: usize, act: &[f64], prio: &[bool]) {
        let v = self.heap[i];
        loop {
            let left = 2 * i + 1;
            if left >= self.heap.len() {
                break;
            }
            let right = left + 1;
            let child = if right < self.heap.len()
                && key_gt(self.heap[right], self.heap[left], act, prio)
            {
                right
            } else {
                left
            };
            if !key_gt(self.heap[child], v, act, prio) {
                break;
            }
            self.heap[i] = self.heap[child];
            self.pos[self.heap[i] as usize] = i as i32;
            i = child;
        }
        self.heap[i] = v;
        self.pos[v as usize] = i as i32;
    }

    /// Re-insert a variable that left the heap (on unassignment).
    fn insert(&mut self, v: u32, act: &[f64], prio: &[bool]) {
        if self.contains(v) {
            return;
        }
        self.heap.push(v);
        self.pos[v as usize] = (self.heap.len() - 1) as i32;
        self.percolate_up(self.heap.len() - 1, act, prio);
    }

    /// A variable's activity rose; restore the heap property.
    fn bumped(&mut self, v: u32, act: &[f64], prio: &[bool]) {
        if self.contains(v) {
            let i = self.pos[v as usize] as usize;
            self.percolate_up(i, act, prio);
        }
    }

    /// Rebuild after a wholesale change of the ordering key.
    fn rebuild(&mut self, n_vars: u32, act: &[f64], prio: &[bool]) {
        self.heap.clear();
        self.pos.iter_mut().for_each(|p| *p = -1);
        for v in 0..n_vars {
            self.insert(v, act, prio);
        }
    }

    fn pop_max(&mut self, act: &[f64], prio: &[bool]) -> Option<u32> {
        if self.heap.is_empty() {
            return None;
        }
        let top = self.heap[0];
        self.pos[top as usize] = -1;
        let last = self.heap.pop().unwrap();
        if !self.heap.is_empty() {
            self.heap[0] = last;
            self.pos[last as usize] = 0;
            self.percolate_down(0, act, prio);
        }
        Some(top)
    }
}

/// CDCL SAT solver.
pub struct Solver {
    /// Number of variables (1-indexed externally).
    n_vars: u32,
    /// Clauses, original + learnt; learnt start at `n_orig_clauses`.
    clauses: Vec<Vec<Lit>>,
    n_orig_clauses: usize,
    /// Per-variable assignment: None = unassigned.
    assignment: Vec<Option<bool>>,
    /// Bitset mirror of `assignment`: `assigned_w` marks assigned
    /// variables, `value_w` their values.  Parity rows are bitmasks, so
    /// with this the whole read-off is `mask & !assigned` and a
    /// popcount — `O(words)` per row instead of `O(set bits)` with a
    /// two-byte `Option<bool>` lookup for each one.
    assigned_w: Vec<u64>,
    value_w: Vec<u64>,
    /// Per-variable decision level when assigned.
    level: Vec<i32>,
    /// Per-variable reason for assignment.
    reason: Vec<Reason>,
    /// Per-variable last-phase, for phase saving.
    saved_phase: Vec<bool>,
    /// Per-variable VSIDS activity.
    activity: Vec<f64>,
    activity_inc: f64,
    activity_decay: f64,
    /// Trail: order in which literals were assigned.
    trail: Vec<Lit>,
    /// Index into `trail` of first unpropagated literal.
    qhead: usize,
    /// `trail_lim[d] = trail.len() when decision level d began`.
    trail_lim: Vec<usize>,
    /// Two-watched-literal scheme: for each literal (encoded as
    /// `2*var + neg` so we can index a `Vec`), a list of clause
    /// indices watching it.
    watches: Vec<Vec<Watcher>>,
    /// Counter of conflicts since the last restart.
    conflicts_since_restart: u64,
    /// Total conflicts across the whole solve.
    conflicts: u64,
    /// Maximum total conflicts before giving up. `u64::MAX` means
    /// no limit.
    pub conflict_budget: u64,
    /// Set when `add_clause` detects UNSAT (empty clause or
    /// conflict-on-unit).  `solve()` short-circuits to UNSAT when set.
    is_unsat: bool,
    /// Native XOR (parity) constraints, held *outside* the CNF.  Each
    /// row is `(variable-set bitmask, right-hand side)`, meaning
    /// `⊕_{v ∈ mask} x_v = rhs`.  See [`Solver::add_xor`].
    xors: Vec<XorRow>,
    /// Bumped on every assignment and every backjump.  Lets
    /// [`Solver::propagate`] skip the Gauss-Jordan pass when nothing
    /// has moved since the last one.
    epoch: u64,
    /// `epoch` as of the last completed Gauss-Jordan pass.
    xor_epoch: u64,
    /// Per-variable reason clause for parity implications, rewritten in
    /// place rather than appended to the clause database.
    xor_reason: Vec<Vec<Lit>>,
    /// Reason clause for a parity conflict, likewise reused.
    xor_conflict: Vec<Lit>,
    /// **Live Gauss-Jordan matrix**: row-reduced linear combinations of
    /// `xors`, carried across propagations instead of re-eliminated
    /// from scratch each time.  Row operations are algebraically valid
    /// whatever the trail says, so they are never undone — not on
    /// propagation, not on backjump.
    ///
    /// The invariant that makes per-row reasoning *complete*:
    ///
    /// > every row has a **pivot** variable that is unassigned and
    /// > occurs in no other row.
    ///
    /// Restricted to the unassigned columns the matrix is then `[I | B]`
    /// after permutation, so any sum of `k` rows still contains all `k`
    /// of their distinct pivots.  A combination can therefore be unit
    /// only for `k = 1`, and inconsistent only if some single row is
    /// fully assigned — which is exactly what a per-row check finds.
    /// Nothing is missed by not re-eliminating.
    ///
    /// Backjumping only *unassigns* variables, which cannot break the
    /// invariant, so it costs no work there either.
    matrix: Vec<XorRow>,
    /// `pivot[i]` is row `i`'s basic variable; `None` once the row has
    /// no unassigned variable left.
    pivot: Vec<Option<u32>>,
    /// `analyze` scratch: which variables have been resolved on.  Only
    /// the entries in `seen_stack` are dirty, so clearing is O(touched)
    /// rather than O(variables).
    seen: Vec<bool>,
    seen_stack: Vec<u32>,
    /// Scratch stack for recursive clause minimization.
    redundant_stack: Vec<Lit>,
    /// Accumulator for the learnt clause, reused across conflicts.  It
    /// grows to a few hundred literals before minimization, so letting
    /// it reallocate per conflict was pure waste.
    learnt_buf: Vec<Lit>,
    /// Branching order by activity.
    order: VarHeap,
    /// Variables to branch on before any others.  See
    /// [`Solver::set_branch_priority`].
    branch_priority: Vec<bool>,
    /// Learnt clauses that have been detached from the watch lists and
    /// are no longer propagated.  They stay in `clauses` so that every
    /// index — in `reason`, in `watches` — remains valid.
    detached: Vec<bool>,
    /// Learnt-clause budget before the next reduction.  Set it before
    /// `solve()` to force more aggressive forgetting; left at 0 it is
    /// chosen from the problem size.
    pub max_learnts: usize,
    /// Counters for the current solve.
    pub stats: SolverStats,
}

/// One parity constraint: `⊕_{v ∈ mask} x_v = rhs`, with `mask` a
/// bitmask over 0-indexed variables.
#[derive(Clone, Debug)]
struct XorRow {
    mask: Vec<u64>,
    rhs: bool,
}

/// Outcome of one Gauss-Jordan pass over the XOR rows.
enum XorStep {
    /// Nothing new could be derived.
    Fixpoint,
    /// At least one literal was enqueued; re-run clause propagation.
    Propagated,
    /// A row is inconsistent; the falsified clause witnessing it has
    /// been written into `xor_conflict`.
    Conflict,
}

#[inline]
fn bs_words(n_vars: u32) -> usize {
    (n_vars as usize + 63) / 64
}

#[inline]
fn bs_get(mask: &[u64], v: u32) -> bool {
    (mask[v as usize / 64] >> (v % 64)) & 1 == 1
}

#[inline]
fn bs_flip(mask: &mut [u64], v: u32) {
    mask[v as usize / 64] ^= 1u64 << (v % 64);
}

#[inline]
fn watch_index(lit: Lit) -> usize {
    let v = var_of(lit) as usize;
    2 * v + (if is_neg(lit) { 1 } else { 0 })
}

#[inline]
fn negated(lit: Lit) -> Lit {
    -lit
}

impl Solver {
    /// Create a fresh solver for `n_vars` variables, indexed 1..=n_vars.
    pub fn new(n_vars: u32) -> Self {
        let n = n_vars as usize;
        Solver {
            n_vars,
            clauses: Vec::new(),
            n_orig_clauses: 0,
            assignment: vec![None; n],
            assigned_w: vec![0; bs_words(n_vars)],
            value_w: vec![0; bs_words(n_vars)],
            level: vec![-1; n],
            reason: vec![Reason::Decision; n],
            saved_phase: vec![true; n],
            activity: vec![0.0; n],
            activity_inc: 1.0,
            activity_decay: 0.95,
            trail: Vec::new(),
            qhead: 0,
            trail_lim: Vec::new(),
            watches: vec![Vec::new(); 2 * n],
            conflicts_since_restart: 0,
            conflicts: 0,
            conflict_budget: u64::MAX,
            is_unsat: false,
            xors: Vec::new(),
            epoch: 0,
            xor_epoch: u64::MAX,
            xor_reason: vec![Vec::new(); n],
            xor_conflict: Vec::new(),
            matrix: Vec::new(),
            pivot: Vec::new(),
            seen: vec![false; n],
            seen_stack: Vec::new(),
            redundant_stack: Vec::new(),
            learnt_buf: Vec::new(),
            order: VarHeap::new(n_vars),
            branch_priority: vec![false; n],
            detached: Vec::new(),
            max_learnts: 0,
            stats: SolverStats::default(),
        }
    }

    /// **Add a native XOR (parity) constraint** `x_{v₁} ⊕ … ⊕ x_{v_k}
    /// = rhs`, with variables given 1-indexed exactly as in
    /// [`Solver::add_clause`].  Returns `false` if the constraint is
    /// trivially unsatisfiable (`0 = 1`).
    ///
    /// XOR rows are held outside the CNF and reasoned about by
    /// Gauss-Jordan elimination in [`Solver::propagate`], rather than
    /// being Tseitin-expanded into clauses.  This is the difference
    /// between polynomial-time and exponential-time handling of a
    /// dense parity constraint: resolution needs exponentially many
    /// steps to refute one (Urquhart 1987), which is why a plain CDCL
    /// stalls on Weil-descended Semaev systems.
    ///
    /// Duplicated variables cancel (`x ⊕ x = 0`), so the caller need
    /// not deduplicate.
    pub fn add_xor(&mut self, vars: &[u32], rhs: bool) -> bool {
        let mut mask = vec![0u64; bs_words(self.n_vars)];
        for &v in vars {
            debug_assert!(v >= 1 && v <= self.n_vars, "xor var {v} out of range");
            bs_flip(&mut mask, v - 1); // duplicates cancel
        }
        if mask.iter().all(|w| *w == 0) {
            // Empty parity: `0 = rhs`.  Satisfiable iff rhs is false.
            if rhs {
                self.is_unsat = true;
                return false;
            }
            return true;
        }
        self.xors.push(XorRow { mask, rhs });
        self.matrix.clear(); // rebuilt on the next pass
        self.xor_epoch = u64::MAX; // force a pass on the next propagate
        true
    }

    /// Number of native XOR constraints installed.
    pub fn n_xors(&self) -> usize {
        self.xors.len()
    }

    /// **Add `count` fresh variables**, returning their 1-indexed
    /// range.  Every per-variable structure grows, the parity bitmasks
    /// are widened, and the live Gauss-Jordan matrix is rebuilt on the
    /// next propagation.  Meant for callers that layer constraints —
    /// symmetry breaking, cardinality chains — over an encoding they
    /// did not size themselves; call it before `solve`, at level 0.
    pub fn add_vars(&mut self, count: u32) -> std::ops::RangeInclusive<u32> {
        debug_assert!(
            self.trail_lim.is_empty(),
            "add_vars must be called at decision level 0"
        );
        let old = self.n_vars;
        let new_total = old + count;
        let n = new_total as usize;
        let words = bs_words(new_total);
        self.assignment.resize(n, None);
        self.assigned_w.resize(words, 0);
        self.value_w.resize(words, 0);
        self.level.resize(n, -1);
        self.reason.resize(n, Reason::Decision);
        self.saved_phase.resize(n, true);
        self.activity.resize(n, 0.0);
        self.watches.resize(2 * n, Vec::new());
        self.xor_reason.resize(n, Vec::new());
        self.seen.resize(n, false);
        self.branch_priority.resize(n, false);
        self.order.pos.resize(n, -1);
        for row in &mut self.xors {
            row.mask.resize(words, 0);
        }
        self.matrix.clear();
        self.pivot.clear();
        self.xor_epoch = u64::MAX;
        self.n_vars = new_total;
        for v in old..new_total {
            self.order.insert(v, &self.activity, &self.branch_priority);
        }
        (old + 1)..=new_total
    }

    /// **Branch on these variables first**, exhausting them before any
    /// other variable is ever chosen as a decision.
    ///
    /// In a gate-style encoding most variables are *defined*: monomial
    /// auxiliaries are conjunctions of other variables, and parity rows
    /// determine the rest.  Deciding one of those is wasted work — its
    /// value was already implied, so the solver is case-splitting on
    /// something propagation would have told it.  Naming the genuinely
    /// free variables collapses the search tree from `2^(all vars)` to
    /// `2^(free vars)`; on the `n = 19, l = 6` Semaev instance that is
    /// `2^18` rather than `2^767`.
    ///
    /// This is only a branching *order*, not a restriction: if the
    /// priority set is exhausted while something is still unassigned,
    /// the solver carries on with the rest, so a caller that names an
    /// incomplete set gets a slower solve rather than a wrong answer.
    ///
    /// Variables are 1-indexed, as in [`Solver::add_clause`].
    pub fn set_branch_priority(&mut self, vars: &[u32]) {
        self.branch_priority.iter_mut().for_each(|p| *p = false);
        for &v in vars {
            debug_assert!(v >= 1 && v <= self.n_vars, "priority var {v} out of range");
            self.branch_priority[(v - 1) as usize] = true;
        }
        self.order
            .rebuild(self.n_vars, &self.activity, &self.branch_priority);
    }

    /// Propagate to fixpoint at the current level without deciding.
    /// Returns `true` on conflict.  Test hook for checking what the
    /// parity engine derives, with no search on top.
    #[cfg(test)]
    pub(crate) fn propagate_to_fixpoint_for_test(&mut self) -> bool {
        if self.is_unsat {
            return true;
        }
        self.propagate().is_some()
    }

    /// Current value of a variable (1-indexed), if assigned.
    #[cfg(test)]
    pub(crate) fn value_of_for_test(&self, v: u32) -> Option<bool> {
        self.assignment[(v - 1) as usize]
    }

    /// Verify a model against the installed XOR rows.  The CNF part is
    /// checked separately by [`check_model`].
    pub fn check_xors(&self, model: &[bool]) -> bool {
        self.xors.iter().all(|row| {
            let mut parity = false;
            for v in 0..self.n_vars {
                if bs_get(&row.mask, v) && model[v as usize] {
                    parity = !parity;
                }
            }
            parity == row.rhs
        })
    }

    /// Add a clause `lits` (DIMACS literal encoding). Returns false if
    /// the empty clause is added (immediately UNSAT).
    pub fn add_clause(&mut self, mut lits: Vec<Lit>) -> bool {
        // Deduplicate and remove tautologies.
        lits.sort_by_key(|&l| (var_of(l), l));
        lits.dedup();
        for w in lits.windows(2) {
            if w[0] == -w[1] {
                return true; // tautology — drop
            }
        }
        // Incremental clauses may arrive after root propagation has
        // already consumed the trail. Remove root-false literals before
        // choosing watches: otherwise both watches can be false with no
        // pending event to visit them, losing a unit or conflicting clause.
        // Root assignments persist across reset_search and are consequences
        // of the permanent formula, so this simplification is sound.
        if self.trail_lim.is_empty() {
            if lits.iter().any(|&l| self.lit_value(l) == Some(true)) {
                return true;
            }
            lits.retain(|&l| self.lit_value(l) != Some(false));
        }
        match lits.len() {
            0 => {
                self.is_unsat = true;
                false
            }
            1 => {
                // Unit clause: assign now (at level 0).
                let l = lits[0];
                match self.enqueue(l, Reason::Propagated(self.clauses.len())) {
                    Ok(()) => {
                        self.clauses.push(vec![l]);
                        self.n_orig_clauses = self.clauses.len();
                        true
                    }
                    Err(()) => {
                        self.is_unsat = true;
                        false
                    }
                }
            }
            _ => {
                let idx = self.clauses.len();
                let (l0, l1) = (lits[0], lits[1]);
                self.watches[watch_index(l0)].push(Watcher {
                    cref: idx,
                    blocker: l1,
                });
                self.watches[watch_index(l1)].push(Watcher {
                    cref: idx,
                    blocker: l0,
                });
                self.clauses.push(lits);
                self.n_orig_clauses = self.clauses.len();
                true
            }
        }
    }

    /// Install a normalized, non-unit permanent clause without discarding the
    /// current trail. Lazy theory clauses arrive at a propagation fixpoint, so
    /// their watches must be selected from literals that are not currently
    /// false. If only one such literal remains, the clause is unit and is
    /// enqueued immediately; if none remain, the installed clause is the
    /// current conflict.
    ///
    /// False fallback watches are ordered by decreasing decision level. When
    /// conflict analysis backjumps, those are the first literals to become
    /// unassigned, preserving the two-watch invariant without replaying the
    /// whole trail.
    fn add_lazy_clause_at_current_level(&mut self, mut lits: Vec<Lit>) -> Option<Conflict> {
        debug_assert!(lits.len() >= 2);
        lits.sort_by(|&left, &right| {
            let key = |lit: Lit| {
                (
                    self.lit_value(lit) != Some(false),
                    self.level[var_of(lit) as usize],
                )
            };
            key(right).cmp(&key(left))
        });
        let non_false = lits
            .iter()
            .take_while(|&&lit| self.lit_value(lit) != Some(false))
            .count();
        let idx = self.clauses.len();
        let (l0, l1) = (lits[0], lits[1]);
        self.clauses.push(lits);
        self.watches[watch_index(l0)].push(Watcher {
            cref: idx,
            blocker: l1,
        });
        self.watches[watch_index(l1)].push(Watcher {
            cref: idx,
            blocker: l0,
        });
        self.detached.resize(self.clauses.len(), false);
        // Theory clauses are permanent propagation lemmas. Advancing this
        // boundary also retains any learnt clauses that preceded them, which
        // costs memory but cannot change an answer.
        self.n_orig_clauses = self.clauses.len();
        match non_false {
            0 => Some(Conflict::Clause(idx)),
            1 if self.lit_value(l0).is_none() => {
                if self.enqueue(l0, Reason::Propagated(idx)).is_err() {
                    Some(Conflict::Clause(idx))
                } else {
                    None
                }
            }
            _ => None,
        }
    }

    /// Look up the truth value of a literal under the current trail.
    fn lit_value(&self, lit: Lit) -> Option<bool> {
        let v = var_of(lit) as usize;
        self.assignment[v].map(|b| if is_neg(lit) { !b } else { b })
    }

    /// Assign `lit` to true with the given reason. Returns `Err` if it
    /// conflicts with the current assignment.
    fn enqueue(&mut self, lit: Lit, r: Reason) -> Result<(), ()> {
        match self.lit_value(lit) {
            Some(true) => Ok(()),
            Some(false) => Err(()),
            None => {
                let v = var_of(lit) as usize;
                self.assignment[v] = Some(!is_neg(lit));
                let (w, bit) = (v / 64, 1u64 << (v % 64));
                self.assigned_w[w] |= bit;
                if is_neg(lit) {
                    self.value_w[w] &= !bit;
                } else {
                    self.value_w[w] |= bit;
                }
                self.level[v] = self.trail_lim.len() as i32;
                self.reason[v] = r;
                self.saved_phase[v] = !is_neg(lit);
                self.trail.push(lit);
                self.epoch += 1;
                self.stats.propagations += 1;
                Ok(())
            }
        }
    }

    /// Propagate to fixpoint over *both* reasoning engines: watched-
    /// literal unit propagation over the CNF, and Gauss-Jordan
    /// elimination over the native XOR rows.  Each engine can feed the
    /// other, so we alternate until neither derives anything new.
    ///
    /// Returns `Some(clause_idx)` on conflict.  For an XOR conflict the
    /// index points at a freshly installed clause that is falsified by
    /// the current trail, so `analyze()` and `backjump()` handle it with
    /// no special-casing.
    fn propagate(&mut self) -> Option<Conflict> {
        loop {
            let t = std::time::Instant::now();
            let cnf = self.propagate_clauses();
            self.stats.ns_propagate_clauses += t.elapsed().as_nanos() as u64;
            if let Some(c) = cnf {
                return Some(Conflict::Clause(c));
            }
            if self.xors.is_empty() || self.epoch == self.xor_epoch {
                // Nothing has moved since the last Gauss-Jordan pass.
                return None;
            }
            self.xor_epoch = self.epoch;
            let t = std::time::Instant::now();
            let step = self.propagate_xors();
            self.stats.ns_propagate_xors += t.elapsed().as_nanos() as u64;
            match step {
                XorStep::Conflict => return Some(Conflict::Xor),
                XorStep::Propagated => continue,
                XorStep::Fixpoint => return None,
            }
        }
    }

    /// One Gauss-Jordan pass over the XOR rows under the current trail.
    ///
    /// Each row carries the *full* variable set of its combination, and
    /// its right-hand side is the combination's original rhs; the value
    /// implied by the current assignment is therefore
    /// `rhs ⊕ parity(mask ∩ assigned-true)`.  Because both mask and rhs
    /// XOR when two rows are combined, that relation survives
    /// elimination — which is what lets us read a reason clause straight
    /// off a reduced row.
    fn propagate_xors(&mut self) -> XorStep {
        self.stats.xor_passes += 1;
        let words = bs_words(self.n_vars);
        if self.matrix.len() != self.xors.len() {
            self.rebuild_matrix();
        }

        // ── Phase 1: restore the pivot invariant ────────────────────
        //
        // Only rows whose pivot has since been assigned are touched, so
        // the usual cost is `O(broken rows × rows × words)` rather than
        // the `O(rows² × words)` of re-eliminating from scratch.
        let mut step = XorStep::Fixpoint;
        let mut src = XorRow {
            mask: vec![0; words],
            rhs: false,
        };
        for i in 0..self.matrix.len() {
            let intact = match self.pivot[i] {
                Some(p) => self.assignment[p as usize].is_none(),
                None => false,
            };
            if intact {
                continue;
            }
            self.stats.xor_repivots += 1;

            match self.lowest_unassigned(&self.matrix[i].mask) {
                None => {
                    // No unassigned variable left: the row is decided.
                    self.pivot[i] = None;
                    if self.row_residual(i) {
                        let mut buf = std::mem::take(&mut self.xor_conflict);
                        let mask = std::mem::take(&mut self.matrix[i].mask);
                        self.write_xor_reason(&mask, None, &mut buf);
                        self.matrix[i].mask = mask;
                        self.xor_conflict = buf;
                        self.stats.xor_conflicts += 1;
                        return XorStep::Conflict;
                    }
                }
                Some(p) => {
                    self.pivot[i] = Some(p);
                    // Clear `p` from every other row, so it lives in
                    // this one alone.
                    src.rhs = self.matrix[i].rhs;
                    src.mask.copy_from_slice(&self.matrix[i].mask);
                    for j in 0..self.matrix.len() {
                        if j == i || !bs_get(&self.matrix[j].mask, p) {
                            continue;
                        }
                        self.stats.xor_row_ops += 1;
                        self.matrix[j].rhs ^= src.rhs;
                        for w in 0..words {
                            self.matrix[j].mask[w] ^= src.mask[w];
                        }
                    }
                }
            }
        }

        // ── Phase 2: read off unit implications ─────────────────────
        //
        // With the invariant restored, a row implies something exactly
        // when its pivot is its *only* unassigned variable — so this is
        // a popcount, and no further elimination is needed.
        let mut propagated = false;
        'rows: for i in 0..self.matrix.len() {
            let p = match self.pivot[i] {
                Some(p) => p,
                None => continue, // decided in phase 1
            };
            self.stats.xor_row_scans += 1;
            let mut parity = self.matrix[i].rhs;
            let mut lone = true;
            for w in 0..words {
                let m = self.matrix[i].mask[w];
                if m == 0 {
                    continue;
                }
                let free = m & !self.assigned_w[w];
                if free.count_ones() > 1 || (free != 0 && free.trailing_zeros() + (w * 64) as u32 != p)
                {
                    lone = false;
                    break;
                }
                parity ^= ((m & self.assigned_w[w] & self.value_w[w]).count_ones() & 1) == 1;
            }
            if !lone {
                continue 'rows;
            }

            let lit = if parity { (p + 1) as Lit } else { -((p + 1) as Lit) };
            let mut buf = std::mem::take(&mut self.xor_reason[p as usize]);
            let mask = std::mem::take(&mut self.matrix[i].mask);
            self.write_xor_reason(&mask, Some(lit), &mut buf);
            self.matrix[i].mask = mask;
            self.stats.xor_reason_lits += buf.len() as u64;
            self.xor_reason[p as usize] = buf;
            self.stats.xor_propagations += 1;
            if self.enqueue(lit, Reason::XorPropagated).is_err() {
                // Unreachable while the invariant holds — the pivot was
                // unassigned — but treat it as a conflict rather than
                // silently dropping an implication.
                std::mem::swap(&mut self.xor_conflict, &mut self.xor_reason[p as usize]);
                self.stats.xor_conflicts += 1;
                return XorStep::Conflict;
            }
            propagated = true;
        }

        match step {
            XorStep::Conflict => XorStep::Conflict,
            _ if propagated => {
                step = XorStep::Propagated;
                step
            }
            _ => XorStep::Fixpoint,
        }
    }

    /// Reset the working matrix to the original rows, dropping every
    /// pivot assignment.  The next pass re-eliminates from scratch.
    ///
    /// Row operations are never undone, so the matrix accumulates
    /// fill-in over a long solve: rows drift denser, which lengthens
    /// the reason clauses read off them.  Rebuilding at restarts, where
    /// the trail is empty anyway, bounds that drift.
    fn rebuild_matrix(&mut self) {
        self.matrix.clear();
        self.matrix.extend_from_slice(&self.xors);
        self.pivot.clear();
        self.pivot.resize(self.matrix.len(), None);
    }

    /// `rhs ⊕ parity(assigned-true variables of the row)` — zero when a
    /// fully assigned row is satisfied.
    fn row_residual(&self, i: usize) -> bool {
        let mut parity = self.matrix[i].rhs;
        for (w, &m) in self.matrix[i].mask.iter().enumerate() {
            if m != 0 {
                parity ^= ((m & self.assigned_w[w] & self.value_w[w]).count_ones() & 1) == 1;
            }
        }
        parity
    }

    /// Lowest-numbered unassigned variable in `mask`, if any.
    fn lowest_unassigned(&self, mask: &[u64]) -> Option<u32> {
        for (w, &word) in mask.iter().enumerate() {
            let free = word & !self.assigned_w[w];
            if free != 0 {
                return Some((w * 64) as u32 + free.trailing_zeros());
            }
        }
        None
    }

    /// Build the clause witnessing what a reduced XOR row implies:
    /// every assigned variable of the row appears negated-as-assigned,
    /// so the clause is false under the current trail except for
    /// `implied` (absent for a conflict clause, which is wholly false).
    fn write_xor_reason(&self, mask: &[u64], implied: Option<Lit>, clause: &mut Vec<Lit>) {
        clause.clear();
        if let Some(l) = implied {
            clause.push(l);
        }
        let implied_var = implied.map(var_of);
        for (w, &word) in mask.iter().enumerate() {
            let mut bits = word;
            while bits != 0 {
                let v = (w * 64) as u32 + bits.trailing_zeros();
                bits &= bits - 1;
                if Some(v) == implied_var {
                    continue;
                }
                match self.assignment[v as usize] {
                    Some(true) => clause.push(-((v + 1) as Lit)),
                    Some(false) => clause.push((v + 1) as Lit),
                    None => debug_assert!(false, "reason clause over an unassigned variable"),
                }
            }
        }
    }

    /// Unit propagation over the CNF. Returns `Some(clause_idx)` on conflict.
    fn propagate_clauses(&mut self) -> Option<usize> {
        while self.qhead < self.trail.len() {
            let lit = self.trail[self.qhead];
            self.qhead += 1;
            // Clauses watching `¬lit` — that watcher has just become
            // false, so each needs a replacement or is unit.
            let wi = watch_index(-lit);
            // Compact the watch list in place with a read and a write
            // cursor.  Building a fresh vector here meant one heap
            // allocation per propagated literal, which at ~280
            // propagations a conflict is millions per solve.
            let mut ws = std::mem::take(&mut self.watches[wi]);
            let (mut i, mut j) = (0usize, 0usize);
            let mut conflict: Option<usize> = None;

            while i < ws.len() {
                let w = ws[i];
                i += 1;
                // Blocker: if this literal is already true the clause is
                // satisfied and is never dereferenced.
                if self.lit_value(w.blocker) == Some(true) {
                    ws[j] = w;
                    j += 1;
                    continue;
                }
                let cidx = w.cref;
                self.stats.clause_visits += 1;

                // Canonical layout: the false watcher sits at [0].
                if self.clauses[cidx][0] != -lit {
                    self.clauses[cidx].swap(0, 1);
                }
                let other = self.clauses[cidx][1];
                let other_value = self.lit_value(other);
                if other_value == Some(true) {
                    ws[j] = Watcher {
                        cref: cidx,
                        blocker: other,
                    };
                    j += 1;
                    continue;
                }

                // Look for a literal that is not false to watch instead.
                let clen = self.clauses[cidx].len();
                let mut moved = false;
                for k in 2..clen {
                    self.stats.clause_lit_visits += 1;
                    let l = self.clauses[cidx][k];
                    if self.lit_value(l) != Some(false) {
                        self.clauses[cidx].swap(0, k);
                        // `l` is not false and `¬lit` is, so this never
                        // writes back into the list being compacted.
                        self.watches[watch_index(l)].push(Watcher {
                            cref: cidx,
                            blocker: other,
                        });
                        moved = true;
                        break;
                    }
                }
                if moved {
                    continue; // the watch now lives elsewhere
                }

                // No replacement: the clause is unit in `other`, or
                // falsified.
                self.clauses[cidx][0] = -lit;
                ws[j] = Watcher {
                    cref: cidx,
                    blocker: other,
                };
                j += 1;
                match other_value {
                    None => {
                        if self.enqueue(other, Reason::Propagated(cidx)).is_err() {
                            conflict = Some(cidx);
                            break;
                        }
                    }
                    Some(false) => {
                        conflict = Some(cidx);
                        break;
                    }
                    Some(true) => unreachable!("handled above"),
                }
            }

            // Keep whatever the loop did not reach.
            while i < ws.len() {
                ws[j] = ws[i];
                i += 1;
                j += 1;
            }
            ws.truncate(j);
            self.watches[wi] = ws;

            if let Some(c) = conflict {
                return Some(c);
            }
        }
        None
    }

    /// **Is `p` implied by the rest of the learnt clause?**
    ///
    /// Walks the implication graph backwards rather than looking only
    /// one step at a reason (Eén–Sörensson's `litRedundant`).  The
    /// distinction matters far more with a parity engine than in
    /// ordinary CDCL: every parity implication's reason names each
    /// assigned variable of its row, so reasons overlap heavily and a
    /// literal is usually reachable through a chain rather than
    /// directly.
    ///
    /// Marks made on a successful walk are kept — those variables are
    /// now known to be implied by the clause — and rolled back on
    /// failure, which is what `top` records.
    fn lit_redundant(
        &mut self,
        p: Lit,
        abstract_levels: u32,
        stack: &mut Vec<Lit>,
    ) -> bool {
        let top = self.seen_stack.len();
        stack.clear();
        stack.push(p);
        while let Some(q) = stack.pop() {
            let qv = var_of(q) as usize;
            let src = self.reason[qv];
            let len = match src {
                Reason::Decision => continue,
                Reason::Propagated(idx) => self.clauses[idx].len(),
                Reason::XorPropagated => self.xor_reason[qv].len(),
            };
            for i in 0..len {
                let r = match src {
                    Reason::Decision => unreachable!(),
                    Reason::Propagated(idx) => self.clauses[idx][i],
                    Reason::XorPropagated => self.xor_reason[qv][i],
                };
                let rv = var_of(r) as usize;
                // The propagated literal itself, anything already in the
                // clause, and anything fixed at level 0 are all fine.
                if rv == qv || self.seen[rv] || self.level[rv] <= 0 {
                    continue;
                }
                let has_reason = !matches!(self.reason[rv], Reason::Decision);
                if has_reason && (abstract_level(self.level[rv]) & abstract_levels) != 0 {
                    self.seen[rv] = true;
                    self.seen_stack.push(rv as u32);
                    stack.push(r);
                } else {
                    for j in top..self.seen_stack.len() {
                        self.seen[self.seen_stack[j] as usize] = false;
                    }
                    self.seen_stack.truncate(top);
                    return false;
                }
            }
        }
        true
    }

    /// 1-UIP conflict analysis. Returns `(learnt_clause, backjump_level)`.
    ///
    /// The `seen` marks are cleared through `seen_stack` rather than by
    /// re-zeroing a per-variable vector, and reason clauses are copied
    /// into a reused buffer rather than cloned — both were per-conflict
    /// allocations on a path taken millions of times.
    fn analyze(&mut self, conflict: Conflict) -> (Vec<Lit>, i32) {
        let current_level = self.trail_lim.len() as i32;
        let mut learnt = std::mem::take(&mut self.learnt_buf);
        learnt.clear();
        let mut counter = 0i32;
        let mut p: Lit = 0;
        let mut src = conflict;
        let mut trail_pos = self.trail.len();

        loop {
            // Read the reason in place.  Copying it into a scratch
            // buffer was a memcpy of up to a hundred literals at every
            // resolution step, and conflict analysis is the hottest
            // phase of the solve.
            let xor_var = if p == 0 { usize::MAX } else { var_of(p) as usize };
            let len = match src {
                Conflict::Clause(idx) => self.clauses[idx].len(),
                Conflict::Xor if xor_var == usize::MAX => self.xor_conflict.len(),
                Conflict::Xor => self.xor_reason[xor_var].len(),
            };

            self.stats.analyze_lit_visits += len as u64;
            for i in 0..len {
                let q = match src {
                    Conflict::Clause(idx) => self.clauses[idx][i],
                    Conflict::Xor if xor_var == usize::MAX => self.xor_conflict[i],
                    Conflict::Xor => self.xor_reason[xor_var][i],
                };
                if p != 0 && q == p {
                    continue;
                }
                let v = var_of(q) as usize;
                // Skip variables fixed at level 0.  Their literals are
                // permanently false in the learnt clause, so carrying
                // them adds nothing and costs a great deal: this
                // encoding propagates heavily at level 0, and including
                // those literals was leaving learnt clauses averaging
                // 188 literals on an `n = 19` instance.
                if !self.seen[v] && self.level[v] > 0 {
                    self.seen[v] = true;
                    self.seen_stack.push(v as u32);
                    // Bump activity, and reposition in the branching heap.
                    self.activity[v] += self.activity_inc;
                    if self.activity[v] > 1e100 {
                        for a in self.activity.iter_mut() {
                            *a *= 1e-100;
                        }
                        self.activity_inc *= 1e-100;
                    }
                    self.order.bumped(v as u32, &self.activity, &self.branch_priority);
                    if self.level[v] >= current_level {
                        counter += 1;
                    } else {
                        learnt.push(q);
                    }
                }
            }

            // Find the next literal to resolve on — walk back the trail.
            while trail_pos > 0 {
                trail_pos -= 1;
                let l = self.trail[trail_pos];
                if self.seen[var_of(l) as usize] {
                    p = l;
                    break;
                }
            }
            let v = var_of(p) as usize;
            self.seen[v] = false;
            counter -= 1;
            if counter <= 0 {
                break;
            }
            // The reason of p must be a propagation (not a decision).
            match self.reason[v] {
                Reason::Propagated(idx) => src = Conflict::Clause(idx),
                Reason::XorPropagated => src = Conflict::Xor,
                Reason::Decision => break,
            }
        }


        // **Local clause minimization** (MiniSat's `analyze` follow-up).
        // A literal whose own reason is built entirely from literals
        // already in the clause is implied by them and adds nothing.
        //
        // This matters far more here than in an ordinary CDCL: a parity
        // row's reason names *every* assigned variable of its combined
        // mask, and Gauss-Jordan makes those masks dense, so unminimized
        // learnt clauses run to hundreds of literals and then have to be
        // walked on every propagation.
        //
        // `seen` is still marked for exactly the clause's literals at
        // this point, which is what makes the test a lookup.
        self.stats.learnt_lits_raw += learnt.len() as u64;
        if learnt.len() > 1 {
            // Cheap filter: a literal can only be redundant if its
            // reason stays inside the levels the clause already covers.
            let mut abstract_levels = 0u32;
            for &q in &learnt {
                abstract_levels |= abstract_level(self.level[var_of(q) as usize]);
            }
            let t_min = std::time::Instant::now();
            let mut stack = std::mem::take(&mut self.redundant_stack);
            let mut w = 0usize;
            for r in 0..learnt.len() {
                let q = learnt[r];
                let v = var_of(q) as usize;
                let redundant = !matches!(self.reason[v], Reason::Decision)
                    && self.lit_redundant(q, abstract_levels, &mut stack);
                if !redundant {
                    learnt[w] = q;
                    w += 1;
                }
            }
            learnt.truncate(w);
            self.redundant_stack = stack;
            self.stats.ns_minimize += t_min.elapsed().as_nanos() as u64;
        }
        self.stats.learnt_lits_kept += learnt.len() as u64;

        // Clear only the marks we set.
        for v in self.seen_stack.drain(..) {
            self.seen[v as usize] = false;
        }

        // Asserting literal: ¬p, then the clause exactly sized for the
        // database.  The accumulator goes back for the next conflict.
        let mut clause: Vec<Lit> = Vec::with_capacity(learnt.len() + 1);
        clause.push(-p);
        clause.extend_from_slice(&learnt);
        learnt.clear();
        self.learnt_buf = learnt;

        // Backjump level: the second-highest level in the clause.
        let mut bj_level = 0;
        if clause.len() > 1 {
            let mut max_i = 1;
            for i in 2..clause.len() {
                if self.level[var_of(clause[i]) as usize]
                    > self.level[var_of(clause[max_i]) as usize]
                {
                    max_i = i;
                }
            }
            clause.swap(1, max_i);
            bj_level = self.level[var_of(clause[1]) as usize];
        }
        // Decay activity.
        self.activity_inc /= self.activity_decay;
        (clause, bj_level)
    }

    /// Undo all assignments above `level`.
    fn backjump(&mut self, level: i32) {
        let level = level.max(0) as usize;
        if self.trail_lim.len() <= level {
            return;
        }
        let target = self.trail_lim[level];
        while self.trail.len() > target {
            let l = self.trail.pop().unwrap();
            let v = var_of(l) as usize;
            self.assignment[v] = None;
            self.assigned_w[v / 64] &= !(1u64 << (v % 64));
            self.level[v] = -1;
            self.order.insert(v as u32, &self.activity, &self.branch_priority);
        }
        self.trail_lim.truncate(level);
        self.qhead = target;
        self.epoch += 1;
    }

    /// Pick the unassigned variable with the highest activity.  Returns
    /// `None` if all variables are assigned.
    ///
    /// Variables are popped from the activity heap; an assigned one may
    /// surface because unassignment re-inserts rather than repositions,
    /// so we skip those.
    fn pick_branching_variable(&mut self) -> Option<u32> {
        while let Some(v) = self.order.pop_max(&self.activity, &self.branch_priority) {
            if self.assignment[v as usize].is_none() {
                return Some(v);
            }
        }
        None
    }

    /// **Drop the least useful half of the learnt clauses.**
    ///
    /// Learning never stops, so without this the watch lists grow for
    /// the whole solve and every propagation pays for clauses that
    /// stopped earning their keep.  Clauses are ranked by length, the
    /// cheap stand-in for LBD: a short clause prunes more.
    ///
    /// Detached clauses stay in `clauses` and are only unhooked from
    /// the watch lists, so every stored index stays valid; they are
    /// learnt, hence implied by the original problem, so dropping them
    /// can cost propagation power but never soundness.  A clause that
    /// is currently some variable's reason is kept, or conflict
    /// analysis would resolve against something no longer there.
    ///
    /// Called only at decision level 0, just after a restart, where the
    /// trail holds nothing but level-0 implications.
    fn reduce_db(&mut self) {
        self.detached.resize(self.clauses.len(), false);

        let mut locked = vec![false; self.clauses.len()];
        for &l in &self.trail {
            if let Reason::Propagated(idx) = self.reason[var_of(l) as usize] {
                locked[idx] = true;
            }
        }

        let mut candidates: Vec<usize> = (self.n_orig_clauses..self.clauses.len())
            .filter(|&i| !self.detached[i] && !locked[i] && self.clauses[i].len() > 2)
            .collect();
        if candidates.len() < 2 {
            return;
        }
        // Longest first, so the front half is the one to drop.
        candidates.sort_by_key(|&i| std::cmp::Reverse(self.clauses[i].len()));
        for &i in candidates.iter().take(candidates.len() / 2) {
            self.detached[i] = true;
        }

        // Rebuild the watch lists from what survives.  Cheaper and much
        // less error-prone than unhooking clauses one at a time.
        for w in self.watches.iter_mut() {
            w.clear();
        }
        for (idx, c) in self.clauses.iter().enumerate() {
            if c.len() < 2 || self.detached.get(idx).copied().unwrap_or(false) {
                continue;
            }
            let (l0, l1) = (c[0], c[1]);
            self.watches[watch_index(l0)].push(Watcher {
                cref: idx,
                blocker: l1,
            });
            self.watches[watch_index(l1)].push(Watcher {
                cref: idx,
                blocker: l0,
            });
        }
    }

    /// Main solve loop. Runs until SAT/UNSAT or conflict budget hits.
    pub fn solve(&mut self) -> SolveResult {
        let mut no_theory = |_: &[Option<bool>]| None;
        self.solve_with_lazy_clauses(&[], &mut no_theory)
    }

    /// Solve while allowing a theory callback to install globally valid lazy
    /// clauses whenever every `trigger_var` is assigned.
    ///
    /// The callback sees the current partial assignment and may return guarded
    /// consequence clauses. Non-unit clauses are attached at the current
    /// propagation fixpoint, where they can imply theory variables without
    /// losing the decisions that selected the current pattern. Empty or unit
    /// consequences use the conservative level-zero [`Self::add_clause`] path.
    /// Returning `None` means the current frontier has already been handled and
    /// ordinary CDCL should continue.
    ///
    /// The caller is responsible for clause soundness.  This is intended for
    /// small theory propagators whose consequences are expensive to encode
    /// eagerly, such as finite-field root relations.
    pub fn solve_with_lazy_clauses<F>(
        &mut self,
        trigger_vars: &[u32],
        theory: &mut F,
    ) -> SolveResult
    where
        F: FnMut(&[Option<bool>]) -> Option<Vec<Vec<Lit>>>,
    {
        if self.is_unsat {
            return SolveResult::Unsat;
        }
        // Initial propagation at level 0 catches trivial UNSAT from
        // unit clauses.
        if self.propagate().is_some() {
            return SolveResult::Unsat;
        }
        if self.max_learnts == 0 {
            self.max_learnts = (self.n_orig_clauses / 3).max(4000);
        }
        self.detached.resize(self.clauses.len(), false);
        let mut luby_index = 1u64;
        let mut restart_limit = 100u64 * luby(luby_index);
        let mut pending_conflict = None;
        loop {
            if let Some(conflict_idx) = pending_conflict.take().or_else(|| self.propagate()) {
                self.conflicts += 1;
                self.stats.conflicts += 1;
                let lvl = self.trail_lim.len() as u64;
                self.stats.conflict_level_sum += lvl;
                self.stats.max_level = self.stats.max_level.max(lvl);
                self.conflicts_since_restart += 1;
                if self.conflicts >= self.conflict_budget {
                    return SolveResult::Unknown;
                }
                if self.trail_lim.is_empty() {
                    return SolveResult::Unsat;
                }
                let t = std::time::Instant::now();
                let (learnt, bj_level) = self.analyze(conflict_idx);
                self.stats.ns_analyze += t.elapsed().as_nanos() as u64;
                self.backjump(bj_level);
                // Install the learnt clause.
                if learnt.len() == 1 {
                    // It's a unit at the backjump level (which is 0).
                    let _ = self.enqueue(learnt[0], Reason::Propagated(self.clauses.len()));
                    self.clauses.push(learnt);
                } else {
                    self.stats.learnt_clauses += 1;
                    let idx = self.clauses.len();
                    let l0 = learnt[0];
                    let l1 = learnt[1];
                    self.clauses.push(learnt);
                    self.watches[watch_index(l0)].push(Watcher {
                        cref: idx,
                        blocker: l1,
                    });
                    self.watches[watch_index(l1)].push(Watcher {
                        cref: idx,
                        blocker: l0,
                    });
                    // The first lit is the asserting one — it's
                    // implied at the new (lower) level.
                    let _ = self.enqueue(l0, Reason::Propagated(idx));
                }
                // Restart?
                if self.conflicts_since_restart >= restart_limit {
                    self.backjump(0);
                    self.stats.restarts += 1;
                    self.conflicts_since_restart = 0;
                    // Level 0: a good moment to shed accumulated
                    // fill-in in the parity matrix.
                    if !self.xors.is_empty() {
                        self.rebuild_matrix();
                        self.xor_epoch = u64::MAX;
                    }
                    let learnt_now = self.clauses.len() - self.n_orig_clauses;
                    if learnt_now > self.max_learnts {
                        let t = std::time::Instant::now();
                        self.reduce_db();
                        self.stats.ns_reduce_db += t.elapsed().as_nanos() as u64;
                        // Let the budget grow, so reductions get rarer
                        // as the solve goes deeper.
                        self.max_learnts = self.max_learnts + self.max_learnts / 2;
                    }
                    luby_index += 1;
                    restart_limit = 100u64 * luby(luby_index);
                }
            } else {
                if !trigger_vars.is_empty()
                    && trigger_vars
                        .iter()
                        .all(|&variable| self.assignment[(variable - 1) as usize].is_some())
                {
                    if let Some(clauses) = theory(&self.assignment) {
                        assert!(!clauses.is_empty(), "lazy theory returned an empty update");
                        let mut normalized = Vec::with_capacity(clauses.len());
                        for mut clause in clauses {
                            clause.sort_by_key(|&lit| (var_of(lit), lit));
                            clause.dedup();
                            if clause.windows(2).any(|pair| pair[0] == -pair[1]) {
                                continue;
                            }
                            normalized.push(clause);
                        }
                        let has_current_conflict = normalized.iter().any(|clause| {
                            !clause.is_empty()
                                && clause
                                    .iter()
                                    .all(|&lit| self.lit_value(lit) == Some(false))
                        });
                        if has_current_conflict
                            || normalized.iter().any(|clause| clause.len() < 2)
                        {
                            self.backjump(0);
                            for clause in normalized {
                                if !self.add_clause(clause) {
                                    return SolveResult::Unsat;
                                }
                            }
                            self.detached.resize(self.clauses.len(), false);
                        } else {
                            for clause in normalized {
                                let conflict = self.add_lazy_clause_at_current_level(clause);
                                if pending_conflict.is_none() {
                                    pending_conflict = conflict;
                                }
                            }
                        }
                        continue;
                    }
                }
                // No conflict — pick a new variable.
                match self.pick_branching_variable() {
                    None => return SolveResult::Sat,
                    Some(v) => {
                        self.stats.decisions += 1;
                        self.trail_lim.push(self.trail.len());
                        let lit = if self.saved_phase[v as usize] {
                            (v + 1) as i32
                        } else {
                            -((v + 1) as i32)
                        };
                        let _ = self.enqueue(lit, Reason::Decision);
                    }
                }
            }
        }
    }

    /// Get the satisfying assignment after a successful `solve()`.
    pub fn model(&self) -> Vec<bool> {
        self.assignment.iter().map(|a| a.unwrap_or(false)).collect()
    }

    /// Number of variables.
    pub fn n_vars(&self) -> u32 {
        self.n_vars
    }

    /// Total number of (original + learnt) clauses.
    /// **Return the solver to decision level 0**, undoing the
    /// assignments a previous [`Self::solve`] left on the trail.
    ///
    /// [`Self::add_clause`] assumes it is called before search: a unit
    /// clause is enqueued at the current level, and the two watched
    /// literals are chosen without regard to what is already assigned.
    /// After a SAT answer the trail sits at a non-zero decision level,
    /// so adding a clause there can silently corrupt those invariants.
    /// Calling this first makes incremental use — add a blocking clause,
    /// solve again — safe, which is how a caller enumerates models
    /// without rebuilding the whole encoding each time.
    pub fn reset_search(&mut self) {
        self.backjump(0);
    }

    /// Scramble phase-saving polarity with a deterministic xorshift seed.
    ///
    /// Intended for multi-shot search: after a conflict-budget timeout,
    /// [`Self::reset_search`] then scramble phases so the next shot explores
    /// a different decision polarity trajectory while keeping learnt clauses.
    pub fn scramble_saved_phases(&mut self, seed: u64) {
        let mut state = seed | 1;
        for phase in &mut self.saved_phase {
            state ^= state << 13;
            state ^= state >> 7;
            state ^= state << 17;
            *phase = (state & 1) != 0;
        }
    }

    /// Force every saved phase to a constant polarity (search-polarity lever).
    pub fn set_all_saved_phases(&mut self, value: bool) {
        for phase in &mut self.saved_phase {
            *phase = value;
        }
    }

    /// Cumulative conflicts across all calls to [`Self::solve`].
    ///
    /// A machine-independent measure of search effort: unlike wall
    /// clock it is comparable across runs and machines, which is what
    /// a benchmark wants when comparing encodings.
    pub fn conflicts(&self) -> u64 {
        self.conflicts
    }

    pub fn n_clauses(&self) -> usize {
        self.clauses.len()
    }
}

/// Luby sequence `1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8, …`
/// (Luby-Sinclair-Zuckerman 1993). Used for restart timing.
/// Iterative — the natural recursion grows logarithmically but on
/// pathological inputs we don't want to risk the stack.
fn luby(i: u64) -> u64 {
    // i is 1-indexed in this codebase; the sequence starts at i = 1.
    // Luby recurrence (Luby-Sinclair-Zuckerman 1993):
    //   t_i = 2^{k-1}            if i = 2^k - 1
    //        t_{i - 2^{k-1} + 1}  otherwise (with k = ⌊log₂ i⌋ + 1)
    let mut n = i;
    loop {
        if n == 0 {
            return 1; // guard; shouldn't happen with i >= 1
        }
        // Find the smallest k with 2^k > n  (i.e. 2^k >= n + 1).
        let mut k: u64 = 0;
        while (1u64 << k) < n + 1 {
            k += 1;
        }
        // Now (1 << k) >= n + 1.  Two cases:
        if n + 1 == 1u64 << k {
            // n == 2^k - 1: base case, return 2^{k-1} (= 1 when k = 0).
            return if k == 0 { 1 } else { 1u64 << (k - 1) };
        }
        // Otherwise, recurse on n - (2^{k-1} - 1).
        n -= (1u64 << (k - 1)) - 1;
    }
}

/// Parse a DIMACS CNF string.
///
/// Format:
/// ```text
/// c comment
/// p cnf <n_vars> <n_clauses>
/// 1 -2 3 0
/// -1 2 0
/// ```
pub fn parse_dimacs(input: &str) -> Result<Solver, String> {
    let mut n_vars: Option<u32> = None;
    let mut current: Vec<Lit> = Vec::new();
    let mut clauses: Vec<Vec<Lit>> = Vec::new();
    for (lineno, line) in input.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('c') {
            continue;
        }
        if line.starts_with("p ") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() < 4 || parts[1] != "cnf" {
                return Err(format!("line {}: bad header `{line}`", lineno + 1));
            }
            n_vars = Some(
                parts[2]
                    .parse()
                    .map_err(|e| format!("line {}: {e}", lineno + 1))?,
            );
            continue;
        }
        // Literal stream; 0 terminates a clause.
        for tok in line.split_whitespace() {
            let l: Lit = tok
                .parse()
                .map_err(|e| format!("line {}: {e}", lineno + 1))?;
            if l == 0 {
                clauses.push(std::mem::take(&mut current));
            } else {
                current.push(l);
            }
        }
    }
    if !current.is_empty() {
        clauses.push(current);
    }
    let n = n_vars.ok_or("missing `p cnf` header")?;
    let mut solver = Solver::new(n);
    for c in clauses {
        if !solver.add_clause(c) {
            // Empty clause → UNSAT but still a valid instance.
            break;
        }
    }
    Ok(solver)
}

/// Parse an **extended DIMACS** string in which lines beginning with
/// `x` are XOR (parity) constraints, as emitted by CryptoMiniSat and by
/// the `EC-Index-Calculus-Benchmarks` generator.
///
/// The convention is that `x 1 2 3 0` means `x₁ ⊕ x₂ ⊕ x₃ = 1`, and
/// each negated literal flips the right-hand side, so
/// `x -1 2 3 0` means `x₁ ⊕ x₂ ⊕ x₃ = 0`.  Ordinary clause lines are
/// parsed exactly as in [`parse_dimacs`].
///
/// XOR rows go to [`Solver::add_xor`] rather than being Tseitin-
/// expanded, so the returned solver reasons about them by Gaussian
/// elimination.
pub fn parse_dimacs_xor(input: &str) -> Result<Solver, String> {
    let mut n_vars: Option<u32> = None;
    let mut clauses: Vec<Vec<Lit>> = Vec::new();
    let mut xors: Vec<(Vec<u32>, bool)> = Vec::new();

    for (lineno, line) in input.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('c') {
            continue;
        }
        if line.starts_with("p ") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() < 3 || parts[1] != "cnf" {
                return Err(format!("line {}: bad header `{line}`", lineno + 1));
            }
            n_vars = Some(
                parts[2]
                    .parse()
                    .map_err(|e| format!("line {}: {e}", lineno + 1))?,
            );
            continue;
        }
        let is_xor = line.starts_with('x');
        let payload = if is_xor { &line[1..] } else { line };
        let mut lits: Vec<Lit> = Vec::new();
        for tok in payload.split_whitespace() {
            let l: Lit = tok
                .parse()
                .map_err(|_| format!("line {}: bad literal `{tok}`", lineno + 1))?;
            if l == 0 {
                break;
            }
            lits.push(l);
        }
        if lits.is_empty() {
            if !is_xor && payload.split_whitespace().any(|token| token == "0") {
                clauses.push(Vec::new());
            }
            continue;
        }
        if is_xor {
            // rhs starts true and flips once per negated literal.
            let negations = lits.iter().filter(|l| **l < 0).count();
            let rhs = negations % 2 == 0;
            xors.push((lits.iter().map(|l| l.unsigned_abs()).collect(), rhs));
        } else {
            clauses.push(lits);
        }
    }

    let n = n_vars.ok_or("missing `p cnf` header")?;
    let mut solver = Solver::new(n);
    for c in clauses {
        if !solver.add_clause(c) {
            break;
        }
    }
    for (vars, rhs) in xors {
        if !solver.add_xor(&vars, rhs) {
            break;
        }
    }
    Ok(solver)
}

/// Emit a DIMACS string for a solver's *original* clauses.
pub fn to_dimacs(solver: &Solver) -> String {
    let mut s = format!("p cnf {} {}\n", solver.n_vars, solver.n_orig_clauses);
    for c in solver.clauses.iter().take(solver.n_orig_clauses) {
        for &l in c {
            s.push_str(&l.to_string());
            s.push(' ');
        }
        s.push_str("0\n");
    }
    s
}

/// Emit the solver's original CNF clauses and native parity rows as
/// CryptoMiniSat-style extended DIMACS.
///
/// An XOR row with right-hand side one is emitted as `x 1 2 ... 0`.
/// For right-hand side zero the first literal is negated, matching
/// [`parse_dimacs_xor`].  A solver that is already inconsistent also emits an
/// explicit empty clause so root UNSAT survives export.
pub fn to_dimacs_xor(solver: &Solver) -> String {
    let constraints = solver.n_orig_clauses
        + solver.xors.len()
        + usize::from(solver.is_unsat);
    let mut output = format!("p cnf {} {}\n", solver.n_vars, constraints);
    for clause in solver.clauses.iter().take(solver.n_orig_clauses) {
        for &literal in clause {
            output.push_str(&literal.to_string());
            output.push(' ');
        }
        output.push_str("0\n");
    }
    for row in &solver.xors {
        output.push('x');
        let mut first = true;
        for variable in 0..solver.n_vars {
            if !bs_get(&row.mask, variable) {
                continue;
            }
            let literal = if first && !row.rhs {
                -((variable + 1) as Lit)
            } else {
                (variable + 1) as Lit
            };
            output.push(' ');
            output.push_str(&literal.to_string());
            first = false;
        }
        output.push_str(" 0\n");
    }
    if solver.is_unsat {
        output.push_str("0\n");
    }
    output
}

/// Convenience: verify that a model satisfies all clauses.
pub fn check_model(clauses: &[Vec<Lit>], model: &[bool]) -> bool {
    for c in clauses {
        let mut sat = false;
        for &l in c {
            let v = var_of(l) as usize;
            let val = if is_neg(l) { !model[v] } else { model[v] };
            if val {
                sat = true;
                break;
            }
        }
        if !sat {
            return false;
        }
    }
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    // ── native XOR reasoning ────────────────────────────────────────

    /// `x₁ ⊕ x₂ = 1` and `x₂ ⊕ x₃ = 1` and `x₁ ⊕ x₃ = 1` is the odd-
    /// cycle parity contradiction: summing all three rows gives `0 = 1`.
    /// Gaussian elimination must see it; resolution would have to search.
    #[test]
    fn xor_odd_cycle_is_unsat() {
        let mut s = Solver::new(3);
        assert!(s.add_xor(&[1, 2], true));
        assert!(s.add_xor(&[2, 3], true));
        assert!(s.add_xor(&[1, 3], true));
        assert_eq!(s.solve(), SolveResult::Unsat);
    }

    /// A triangular XOR system with a unique solution, derivable by
    /// propagation alone (no decisions needed).
    #[test]
    fn xor_system_propagates_to_unique_solution() {
        let mut s = Solver::new(3);
        s.add_xor(&[1], true); //           x₁ = 1
        s.add_xor(&[1, 2], false); //  x₁ ⊕ x₂ = 0  → x₂ = 1
        s.add_xor(&[2, 3], true); //   x₂ ⊕ x₃ = 1  → x₃ = 0
        assert_eq!(s.solve(), SolveResult::Sat);
        let m = s.model();
        assert_eq!((m[0], m[1], m[2]), (true, true, false));
        assert!(s.check_xors(&m));
    }

    /// Duplicated variables inside one row must cancel: `x ⊕ x ⊕ y = 1`
    /// is just `y = 1`.
    #[test]
    fn xor_duplicate_vars_cancel() {
        let mut s = Solver::new(2);
        assert!(s.add_xor(&[1, 1, 2], true));
        assert_eq!(s.solve(), SolveResult::Sat);
        assert!(s.model()[1], "y must be forced true");
    }

    /// `x ⊕ x = 1` reduces to `0 = 1` and is rejected at add time.
    #[test]
    fn xor_empty_row_with_true_rhs_is_unsat() {
        let mut s = Solver::new(2);
        assert!(!s.add_xor(&[1, 1], true));
        assert_eq!(s.solve(), SolveResult::Unsat);
    }

    /// XOR rows and CNF clauses must constrain each other: the parity
    /// rows admit two solutions, and the clause rules one out.
    #[test]
    fn xor_and_cnf_interact() {
        let mut s = Solver::new(3);
        s.add_xor(&[1, 2], false); // x₁ = x₂
        s.add_xor(&[2, 3], false); // x₂ = x₃
        s.add_clause(vec![1]); //     x₁ = 1  ⇒ all true
        assert_eq!(s.solve(), SolveResult::Sat);
        let m = s.model();
        assert_eq!((m[0], m[1], m[2]), (true, true, true));
        assert!(s.check_xors(&m));
    }

    /// **The incremental matrix must lose nothing.**
    ///
    /// The whole design rests on one claim: with every row carrying an
    /// unassigned pivot that occurs in no other row, a per-row check
    /// finds every implication that re-running Gaussian elimination
    /// would.  This tests that claim directly rather than trusting the
    /// argument — for random systems under random partial assignments,
    /// the solver's implications are compared against an oracle that
    /// eliminates from scratch every time.
    ///
    /// A silent incompleteness here would show up as a missed
    /// propagation, not a crash, so it is worth checking explicitly.
    #[test]
    fn incremental_matrix_matches_full_elimination() {
        let n_vars = 12u32;
        let mut state = 0xD1B5_4A32_D192_ED03u64;
        let mut next = || {
            state ^= state >> 12;
            state ^= state << 25;
            state ^= state >> 27;
            state.wrapping_mul(0x2545_F491_4F6C_DD1D)
        };

        /// Oracle: full Gauss-Jordan from scratch, returning every
        /// variable the system forces under `fixed`, with its value.
        fn oracle(
            rows: &[(Vec<u32>, bool)],
            fixed: &[Option<bool>],
            n_vars: u32,
        ) -> Option<Vec<(u32, bool)>> {
            // Dense F2 elimination over the unassigned columns.
            let mut m: Vec<(Vec<bool>, bool)> = rows
                .iter()
                .map(|(vars, rhs)| {
                    let mut row = vec![false; n_vars as usize];
                    let mut r = *rhs;
                    for &v in vars {
                        let idx = (v - 1) as usize;
                        match fixed[idx] {
                            Some(true) => r = !r,
                            Some(false) => {}
                            None => row[idx] ^= true,
                        }
                    }
                    (row, r)
                })
                .collect();
            // Row-reduce.
            let mut pivot_row = 0usize;
            for col in 0..n_vars as usize {
                let Some(sel) = (pivot_row..m.len()).find(|&r| m[r].0[col]) else {
                    continue;
                };
                m.swap(pivot_row, sel);
                for r in 0..m.len() {
                    if r != pivot_row && m[r].0[col] {
                        let (src, rhs) = (m[pivot_row].0.clone(), m[pivot_row].1);
                        for c in 0..n_vars as usize {
                            m[r].0[c] ^= src[c];
                        }
                        m[r].1 ^= rhs;
                    }
                }
                pivot_row += 1;
            }
            let mut implied = Vec::new();
            for (row, rhs) in &m {
                let set: Vec<usize> = (0..n_vars as usize).filter(|&c| row[c]).collect();
                match set.len() {
                    0 => {
                        if *rhs {
                            return None; // inconsistent
                        }
                    }
                    1 => implied.push((set[0] as u32 + 1, *rhs)),
                    _ => {}
                }
            }
            implied.sort();
            Some(implied)
        }

        for trial in 0..300 {
            let n_rows = 2 + (next() % 6) as usize;
            let rows: Vec<(Vec<u32>, bool)> = (0..n_rows)
                .map(|_| {
                    let mut vars: Vec<u32> = (1..=n_vars).filter(|_| next() % 3 != 0).collect();
                    if vars.is_empty() {
                        vars.push(1);
                    }
                    (vars, next() % 2 == 0)
                })
                .collect();

            // A random partial assignment, installed as unit clauses so
            // the solver reaches it by propagation at level 0.
            let mut fixed: Vec<Option<bool>> = vec![None; n_vars as usize];
            let mut units: Vec<Lit> = Vec::new();
            for v in 1..=n_vars {
                if next() % 3 == 0 {
                    let val = next() % 2 == 0;
                    fixed[(v - 1) as usize] = Some(val);
                    units.push(if val { v as Lit } else { -(v as Lit) });
                }
            }

            let want = oracle(&rows, &fixed, n_vars);

            let mut s = Solver::new(n_vars);
            let mut trivial_unsat = false;
            for (vars, rhs) in &rows {
                if !s.add_xor(vars, *rhs) {
                    trivial_unsat = true;
                }
            }
            for u in &units {
                if !s.add_clause(vec![*u]) {
                    trivial_unsat = true;
                }
            }
            // Drive propagation to fixpoint at level 0 without deciding.
            let conflicted = trivial_unsat || s.propagate_to_fixpoint_for_test();

            match want {
                None => assert!(
                    conflicted,
                    "trial {trial}: elimination says inconsistent, solver did not notice"
                ),
                Some(implied) => {
                    assert!(
                        !conflicted,
                        "trial {trial}: solver reported a conflict where none exists"
                    );
                    for (v, val) in implied {
                        assert_eq!(
                            s.value_of_for_test(v),
                            Some(val),
                            "trial {trial}: variable {v} should have been forced to {val}"
                        );
                    }
                }
            }
        }
    }

    /// **Differential test against brute force.**  Random dense parity
    /// systems, decided exhaustively and by the solver; every verdict
    /// must agree, and every SAT model must satisfy every row.
    #[test]
    fn xor_engine_agrees_with_brute_force() {
        let n_vars = 9u32;
        let mut state = 0x2545_F491_4F6C_DD1Du64; // xorshift64*
        let mut next = || {
            state ^= state >> 12;
            state ^= state << 25;
            state ^= state >> 27;
            state.wrapping_mul(0x2545_F491_4F6C_DD1D)
        };

        for trial in 0..200 {
            let n_rows = 3 + (next() % 6) as usize;
            let mut rows: Vec<(Vec<u32>, bool)> = Vec::new();
            for _ in 0..n_rows {
                let mut vars: Vec<u32> = Vec::new();
                for v in 1..=n_vars {
                    if next() % 2 == 0 {
                        vars.push(v);
                    }
                }
                if vars.is_empty() {
                    vars.push(1 + (next() % n_vars as u64) as u32);
                }
                rows.push((vars, next() % 2 == 0));
            }

            // Ground truth by exhaustive search.
            let mut brute_sat = false;
            for a in 0..(1u32 << n_vars) {
                if rows.iter().all(|(vars, rhs)| {
                    let parity = vars.iter().filter(|v| (a >> (**v - 1)) & 1 == 1).count() % 2 == 1;
                    parity == *rhs
                }) {
                    brute_sat = true;
                    break;
                }
            }

            let mut s = Solver::new(n_vars);
            let mut trivially_unsat = false;
            for (vars, rhs) in &rows {
                if !s.add_xor(vars, *rhs) {
                    trivially_unsat = true;
                }
            }
            let res = s.solve();

            if brute_sat {
                assert_eq!(res, SolveResult::Sat, "trial {trial}: solver missed a model");
                let m = s.model();
                assert!(s.check_xors(&m), "trial {trial}: model violates a row");
            } else {
                assert_eq!(res, SolveResult::Unsat, "trial {trial}: solver invented a model");
                let _ = trivially_unsat;
            }
        }
    }

    /// The extended-DIMACS reader must apply CryptoMiniSat's parity
    /// convention: bare literals mean `= 1`, one negation flips to `= 0`.
    #[test]
    fn parse_dimacs_xor_reads_parity_convention() {
        // x₁ ⊕ x₂ ⊕ x₃ = 1 (no negations), x₁ ⊕ x₂ = 0 (one negation),
        // plus the unit clause x₃.  Together these force x₃ = 1 and
        // x₁ = x₂.
        let src = "p cnf 3 3\nx 1 2 3 0\nx -1 2 0\n3 0\n";
        let mut s = parse_dimacs_xor(src).expect("parse");
        assert_eq!(s.n_xors(), 2);
        assert_eq!(s.solve(), SolveResult::Sat);
        let m = s.model();
        assert!(s.check_xors(&m));
        assert!(m[2], "the unit clause forces x₃ true");
        assert!(m[0] ^ m[1] ^ m[2], "first row must have odd parity");
        assert!(!(m[0] ^ m[1]), "second row must have even parity");

        // Flipping the unit clause to ¬x₃ makes the same system UNSAT.
        let src_bad = "p cnf 3 3\nx 1 2 3 0\nx -1 2 0\n-3 0\n";
        assert_eq!(
            parse_dimacs_xor(src_bad).expect("parse").solve(),
            SolveResult::Unsat
        );
    }

    #[test]
    fn extended_dimacs_export_round_trips_xors_and_root_unsat() {
        let mut original = Solver::new(4);
        assert!(original.add_clause(vec![1, -4]));
        assert!(original.add_xor(&[1, 2, 3], true));
        assert!(original.add_xor(&[2, 4], false));
        let encoded = to_dimacs_xor(&original);
        let mut reparsed = parse_dimacs_xor(&encoded).expect("parse exported XOR DIMACS");
        assert_eq!(reparsed.n_xors(), 2);
        assert_eq!(reparsed.solve(), SolveResult::Sat);
        let model = reparsed.model();
        assert!(reparsed.check_xors(&model));

        let mut root_unsat = Solver::new(1);
        assert!(!root_unsat.add_clause(Vec::new()));
        let encoded_unsat = to_dimacs_xor(&root_unsat);
        assert!(encoded_unsat.lines().any(|line| line.trim() == "0"));
        assert_eq!(
            parse_dimacs_xor(&encoded_unsat)
                .expect("parse exported root conflict")
                .solve(),
            SolveResult::Unsat
        );
    }

    #[test]
    fn lazy_clause_callback_installs_guarded_theory_consequences_on_current_trail() {
        let mut solver = Solver::new(3);
        solver.set_branch_priority(&[1, 2]);
        let mut seen = std::collections::HashSet::new();
        let mut theory = |assignment: &[Option<bool>]| {
            let left = assignment[0].unwrap();
            let right = assignment[1].unwrap();
            if !seen.insert((left, right)) {
                return None;
            }
            let mut clause = vec![if left { -1 } else { 1 }, if right { -2 } else { 2 }];
            clause.push(if left ^ right { 3 } else { -3 });
            Some(vec![clause])
        };
        assert_eq!(
            solver.solve_with_lazy_clauses(&[1, 2], &mut theory),
            SolveResult::Sat
        );
        let model = solver.model();
        assert_eq!(model[2], model[0] ^ model[1]);
        assert!(!seen.is_empty());
    }

    #[test]
    fn lazy_clause_conflict_backjumps_and_preserves_theory_answer() {
        let mut solver = Solver::new(3);
        solver.set_branch_priority(&[1, 2]);
        assert!(solver.add_clause(vec![-3]));
        let mut seen = std::collections::HashSet::new();
        let mut theory = |assignment: &[Option<bool>]| {
            let left = assignment[0].unwrap();
            let right = assignment[1].unwrap();
            if !seen.insert((left, right)) {
                return None;
            }
            let mut clause = vec![if left { -1 } else { 1 }, if right { -2 } else { 2 }];
            clause.push(if left ^ right { 3 } else { -3 });
            Some(vec![clause])
        };
        assert_eq!(
            solver.solve_with_lazy_clauses(&[1, 2], &mut theory),
            SolveResult::Sat
        );
        let model = solver.model();
        assert!(!model[2]);
        assert_eq!(model[2], model[0] ^ model[1]);
        assert!(!seen.is_empty());
    }

    /// **Clause forgetting must not change any answer.**  Under a
    /// deliberately tiny budget the solver reduces its learnt database
    /// constantly; every verdict and every model must still match a
    /// run that never forgets anything.
    #[test]
    fn aggressive_clause_reduction_preserves_answers() {
        let n_vars = 9u32;
        let mut state = 0x9E37_79B9_7F4A_7C15u64;
        let mut next = || {
            state ^= state >> 12;
            state ^= state << 25;
            state ^= state >> 27;
            state.wrapping_mul(0x2545_F491_4F6C_DD1D)
        };

        for trial in 0..60 {
            // A mixed CNF + parity instance, the shape this solver is
            // actually used on.
            let mut clauses: Vec<Vec<Lit>> = Vec::new();
            for _ in 0..(20 + next() % 20) {
                let mut c = Vec::new();
                for _ in 0..3 {
                    let v = 1 + (next() % n_vars as u64) as i32;
                    let sign = if next() % 2 == 0 { 1 } else { -1 };
                    c.push(sign * v);
                }
                clauses.push(c);
            }
            let mut xors: Vec<(Vec<u32>, bool)> = Vec::new();
            for _ in 0..3 {
                let vars: Vec<u32> = (1..=n_vars).filter(|_| next() % 2 == 0).collect();
                if !vars.is_empty() {
                    xors.push((vars, next() % 2 == 0));
                }
            }

            let build = |budget: usize| {
                let mut s = Solver::new(n_vars);
                for c in &clauses {
                    s.add_clause(c.clone());
                }
                for (vars, rhs) in &xors {
                    s.add_xor(vars, *rhs);
                }
                s.max_learnts = budget;
                s
            };

            let mut relaxed = build(1_000_000);
            let mut aggressive = build(2);
            let (ra, rb) = (relaxed.solve(), aggressive.solve());
            assert_eq!(ra, rb, "trial {trial}: forgetting changed the verdict");
            if ra == SolveResult::Sat {
                let m = aggressive.model();
                assert!(
                    check_model(&clauses, &m) && aggressive.check_xors(&m),
                    "trial {trial}: model from the forgetting run is invalid"
                );
            }
        }
    }

    /// A small known-SAT instance.
    #[test]
    fn simple_sat() {
        let mut s = Solver::new(3);
        assert!(s.add_clause(vec![1, 2]));
        assert!(s.add_clause(vec![-1, 3]));
        assert!(s.add_clause(vec![-2, -3]));
        assert!(s.add_clause(vec![1, -3]));
        assert_eq!(s.solve(), SolveResult::Sat);
        let m = s.model();
        // Verify against the original clauses.
        let orig = vec![vec![1, 2], vec![-1, 3], vec![-2, -3], vec![1, -3]];
        assert!(check_model(&orig, &m));
    }

    /// Trivially UNSAT: x ∧ ¬x.  Note: `add_clause` may return false
    /// for the second unit clause because enqueuing `-1` conflicts
    /// with the already-propagated `1`; both that path and `solve()`
    /// must reach UNSAT.
    #[test]
    fn trivial_unsat() {
        let mut s = Solver::new(1);
        assert!(s.add_clause(vec![1]));
        // The contradictory unit may be detected immediately at add
        // time (returns false) or surface from solve(); either is
        // valid UNSAT detection.
        let added = s.add_clause(vec![-1]);
        if added {
            assert_eq!(s.solve(), SolveResult::Unsat);
        } else {
            // add_clause already detected UNSAT; solve() must agree.
            assert_eq!(s.solve(), SolveResult::Unsat);
        }
    }

    /// The pigeonhole principle PHP(3, 2): 3 pigeons in 2 holes is
    /// UNSAT. Variable `x_{i,j}` = pigeon `i` is in hole `j`. Indexed
    /// 1..=6 as: (i-1)*2 + j.
    #[test]
    fn pigeonhole_3_into_2_is_unsat() {
        let x = |i: u32, j: u32| ((i - 1) * 2 + j) as i32;
        let mut s = Solver::new(6);
        // Each pigeon in some hole.
        for i in 1..=3 {
            s.add_clause(vec![x(i, 1), x(i, 2)]);
        }
        // No two pigeons in the same hole.
        for j in 1..=2 {
            for i1 in 1..=3 {
                for i2 in (i1 + 1)..=3 {
                    s.add_clause(vec![-x(i1, j), -x(i2, j)]);
                }
            }
        }
        assert_eq!(s.solve(), SolveResult::Unsat);
    }

    /// Pigeonhole 5-into-4 is also UNSAT; non-trivial for CDCL.
    #[test]
    fn pigeonhole_5_into_4_is_unsat() {
        let n_pigeons = 5u32;
        let n_holes = 4u32;
        let x = |i: u32, j: u32| ((i - 1) * n_holes + j) as i32;
        let mut s = Solver::new(n_pigeons * n_holes);
        for i in 1..=n_pigeons {
            let mut c = Vec::with_capacity(n_holes as usize);
            for j in 1..=n_holes {
                c.push(x(i, j));
            }
            s.add_clause(c);
        }
        for j in 1..=n_holes {
            for i1 in 1..=n_pigeons {
                for i2 in (i1 + 1)..=n_pigeons {
                    s.add_clause(vec![-x(i1, j), -x(i2, j)]);
                }
            }
        }
        assert_eq!(s.solve(), SolveResult::Unsat);
    }

    /// Round-trip a CNF through DIMACS.
    #[test]
    fn dimacs_roundtrip() {
        let mut s = Solver::new(4);
        s.add_clause(vec![1, -2, 3]);
        s.add_clause(vec![-1, 2]);
        s.add_clause(vec![-3, 4]);
        let dimacs = to_dimacs(&s);
        assert!(dimacs.starts_with("p cnf 4 3"));
        let s2 = parse_dimacs(&dimacs).expect("parse failed");
        assert_eq!(s2.n_vars(), 4);
        assert_eq!(s2.n_clauses(), 3);
    }

    /// Luby sequence check.
    #[test]
    fn luby_sequence_starts_correctly() {
        let seq: Vec<u64> = (1..=15).map(luby).collect();
        assert_eq!(seq, vec![1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8]);
    }

    /// Random k-SAT instance at the satisfiability threshold (clause-
    /// to-variable ratio ≈ 4.26 for 3-SAT). Should mostly be SAT.
    #[test]
    fn random_3sat_around_threshold() {
        let n = 20u32;
        let m = (4.0 * n as f64) as usize;
        let mut state = 0xc0ffee_u64;
        let mut next = || {
            state = state
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1442695040888963407);
            state >> 33
        };
        let mut s = Solver::new(n);
        let mut orig_clauses = Vec::new();
        for _ in 0..m {
            let mut clause = Vec::with_capacity(3);
            let mut vars_in_clause = HashSet::new();
            while clause.len() < 3 {
                let v = ((next() as u32) % n) + 1;
                if vars_in_clause.insert(v) {
                    let sign = (next() & 1) as u32;
                    clause.push(if sign == 0 { v as i32 } else { -(v as i32) });
                }
            }
            orig_clauses.push(clause.clone());
            s.add_clause(clause);
        }
        let result = s.solve();
        if result == SolveResult::Sat {
            let m = s.model();
            assert!(check_model(&orig_clauses, &m));
        }
        // Either SAT or UNSAT is acceptable; what we're checking is
        // that the solver terminates.
        assert_ne!(result, SolveResult::Unknown);
    }
}
