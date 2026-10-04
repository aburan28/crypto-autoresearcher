//! # SAT-encoded binary Semaev solver.
//!
//! Bridges the CDCL SAT solver in [`crate::cryptanalysis::sat`] to the
//! binary-Semaev polynomial systems produced by Weil descent, for both
//! two-point (`S₃`) and three-point (symmetrised `S₄`) decomposition.
//!
//! This is the **hybrid SAT/algebraic** entry in the ECDLP research-
//! direction map: clause learning plus native XOR-constraint reasoning,
//! the route Soos-Nohl-Castelluccia (CryptoMiniSat 2009) pioneered.
//!
//! # The three modelling choices that decide tractability
//!
//! 1. **Factor base.**  Index calculus confines each unknown
//!    x-coordinate to an `l`-dimensional `F₂`-subspace with `l ≈ n/m`,
//!    not to all of `F_{2ⁿ}`.  That turns `n` equations in `2n`
//!    unknowns into `n` equations in `m·l ≈ n` unknowns — determined
//!    rather than wildly under-determined.  See
//!    [`encode_semaev_s3_subspace`].
//! 2. **Parity encoding.**  The descended system *is* a set of parity
//!    constraints.  Handing them to the solver natively
//!    ([`XorEncoding::Native`]) lets it eliminate them by Gauss-Jordan;
//!    Tseitin-expanding them ([`XorEncoding::Cnf`]) forces the search
//!    to rediscover linear algebra by resolution, which provably takes
//!    exponentially many steps on a dense parity constraint.
//! 3. **Decomposition size.**  `m = 2` (`S₃`) has no asymptotic payoff;
//!    `m = 3` (symmetrised `S₄`, [`encode_semaev_s4`]) is where index
//!    calculus begins to mean something.
//!
//! # Measured
//!
//! `cargo run --release --example semaev_sat_bench`.  Aggregates over
//! **every satisfiable instance** of each reference-corpus family —
//! per-instance times on satisfiable instances swing by an order of
//! magnitude on search luck, so a single instance measures nothing.
//!
//! | family | symmetry breaking | instances | total | median | conflicts |
//! |---|---|---:|---:|---:|---:|
//! | `n15l5` | off | 10 | 5.1 s | 460 ms | 129 493 |
//! | `n15l5` | on | 10 | 1.3 s | 180 ms | 33 148 |
//! | `n17l6` | off | 10 | 27.1 s | 3.0 s | 431 921 |
//! | `n17l6` | on | 10 | 8.4 s | 663 ms | 146 310 |
//! | `n19l6` | off | 11 | 74.2 s | 5.3 s | 987 666 |
//! | `n19l6` | on | 11 | 17.8 s | 1.8 s | 311 671 |
//!
//! Breaking the `3!` symmetry is worth a steady 3–5× — not far off the
//! `6×` the orbit size allows, less the cost of the ordering clauses.
//! The first working version needed 231 s for one `n = 19` instance;
//! the median is now 1.8 s.  `cargo run --release --example
//! semaev_profile` breaks a solve down by phase.
//! (`n19l6` has eleven satisfiable instances, not ten: one of the
//! upstream `-U` instances is misannotated.  See
//! [`crate::cryptanalysis::semaev_corpus`].)
//!
//! Encoding size at `n = 19, l = 6`, without symmetry breaking:
//!
//! | encoding | vars | clauses | parity rows |
//! |---|---:|---:|---:|
//! | native | 767 | 2 364 | 52 |
//! | Tseitin CNF | 2 892 | 25 074 | 0 |
//!
//! The native column matches, exactly, the instance size that the
//! independent C generator in
//! [`mtrimoska/EC-Index-Calculus-Benchmarks`][up] emits for the same
//! family (`p cnf 767 2416` with 52 `x`-lines).  See
//! [`crate::cryptanalysis::semaev_corpus`] and
//! `RESEARCH_TRIMOSKA_BENCHMARKS.md`.
//!
//! [up]: https://github.com/mtrimoska/EC-Index-Calculus-Benchmarks
//!
//! # Limits
//!
//! - **Clauses are `Vec<Vec<Lit>>`**, so every clause visit is a
//!   pointer chase.  Propagation and conflict analysis are ~78% of the
//!   time between them; a flat clause arena is the largest remaining
//!   item.  The parity engine is now only ~20%.
//! - **`S₄` is specialised to `b = 1`**, the Koblitz curve
//!   `y² + xy = x³ + x² + 1`.  See
//!   [`crate::cryptanalysis::binary_semaev_s4`].
//! - **The route does not scale, and this is the finding that matters
//!   most.**  The solver never prunes the candidate space — one
//!   conflict per factor-base triple at every `l` measured — while cost
//!   per conflict grows with instance size.  Against direct evaluation
//!   of the symmetrised `S₄` at every triple the deficit widens from 5×
//!   at `l = 5` to 62× at `l = 8`.  Further solver optimisation cannot
//!   recover that.  `cargo run --release --example semaev_scaling`.
//! - **Decoded solutions are always re-verified** against the original
//!   Semaev polynomial over `F_{2ⁿ}`, so an encoding bug shows up as a
//!   test failure rather than a wrong answer.
//!
//! # References
//!
//! - **M. Soos, K. Nohl, C. Castelluccia**, *Extending SAT solvers
//!   to cryptographic problems*, SAT 2009.
//! - **A. Urquhart**, *Hard examples for resolution*, JACM 1987 — why
//!   parity constraints must not go through CNF.
//! - **J.-C. Faugère, P. Gaudry, L. Huot, G. Renault**, *Using
//!   symmetries in the index calculus for elliptic curves discrete
//!   logarithm*, J. Cryptology 2014.
//! - **P. Gaudry**, *Index calculus for abelian varieties of small
//!   dimension and the elliptic curve discrete logarithm problem*, 2009.
//! - **G. Tseitin**, *On the complexity of derivation in propositional
//!   calculus*, 1968 — the AND/XOR gate-CNF encoding.

use crate::binary_ecc::{F2mElement, IrreduciblePoly};
use crate::cryptanalysis::binary_semaev::binary_semaev_s3;
use crate::cryptanalysis::binary_semaev_s4::weil_descend_s4;
use crate::cryptanalysis::ffd_harness::{
    monomial_index, quad_monomial_index, weil_descend_s3, weil_descend_s3_subspace, F2BoolPoly,
};
use crate::cryptanalysis::pq_groebner_f2::F2BoolPoly as BoolPoly;
use crate::cryptanalysis::sat::{Lit, SolveResult, Solver};

// ── Encoding ────────────────────────────────────────────────────────

/// How parity constraints reach the solver.
///
/// The Weil-descended system *is* a set of parity constraints, so this
/// is the single most consequential encoding choice in the pipeline.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum XorEncoding {
    /// Tseitin-expand each parity constraint into CNF: direct
    /// truth-table expansion for narrow sums, chained auxiliaries for
    /// wide ones.  This is what a solver without XOR support requires,
    /// and it is why a dense parity system explodes — resolution needs
    /// exponentially many steps to refute one.
    Cnf,
    /// Install parity constraints natively, for Gauss-Jordan
    /// elimination inside the solver (see [`Solver::add_xor`]).  The
    /// default, and the reason `n` beyond 5 is reachable at all.
    Native,
}

/// The result of SAT-encoding a binary-Semaev `S_3` system.
pub struct SemaevSatEncoding {
    pub n: u32,
    /// Dimension of the factor-base subspace each `Xᵢ` is confined to.
    /// Equal to `n` for the unrestricted descent.
    pub l: u32,
    /// `2l` boolean variables for the bits of `(X₁, X₂)`.
    pub bit_var_offset: u32,
    /// Map `(i, j)` (with `i < j < 2n`) → SAT variable index for the
    /// auxiliary `z_{ij} = xᵢ ∧ xⱼ`.  `None` if the pair never
    /// appears in any equation.
    pub aux_quad_var: std::collections::BTreeMap<(u32, u32), u32>,
    /// The underlying CDCL solver, with all encoding clauses
    /// installed.
    pub solver: Solver,
    /// `true` if an empty clause was added during encoding (which
    /// indicates trivial UNSAT, e.g. `1 = 0` after Weil descent).
    /// In that case `solver.solve()` should return UNSAT immediately,
    /// but as a safety we also expose this flag.
    pub trivially_unsat: bool,
}

/// **Encode the binary Semaev `S_3` system** for given `b` and `x_3`
/// into a SAT instance, then return a [`SemaevSatEncoding`] ready to
/// call `.solve()` on.
pub fn encode_semaev_s3(
    n: u32,
    irr: &IrreduciblePoly,
    b: &F2mElement,
    x3: &F2mElement,
) -> SemaevSatEncoding {
    encode_semaev_s3_subspace(n, n, irr, b, x3, XorEncoding::Native)
}

/// **Encode `S₃` with the unknowns confined to a factor base** — the
/// `l`-dimensional subspace `⟨1, z, …, z^{l−1}⟩ ⊆ F_{2ⁿ}`.
///
/// This is the index-calculus setting: `n` equations in `2l` unknowns
/// rather than `n` equations in `2n`.  At `l ≈ n/2` the system is
/// essentially determined, which is the shape a CDCL can actually work
/// on; the unrestricted version leaves `2ⁿ` solutions and a dense
/// quadratic system to wade through.
pub fn encode_semaev_s3_subspace(
    n: u32,
    l: u32,
    irr: &IrreduciblePoly,
    b: &F2mElement,
    x3: &F2mElement,
    encoding: XorEncoding,
) -> SemaevSatEncoding {
    let equations = weil_descend_s3_subspace(n, l, irr, b, x3);
    encode_equations_with(n, l, equations, encoding)
}

/// **Encode a set of quadratic `F_2`-equations** into a SAT instance.
/// Generic; used by both the Semaev pipeline and the harness's own
/// self-check tests.
pub fn encode_equations(n: u32, equations: Vec<F2BoolPoly>) -> SemaevSatEncoding {
    encode_equations_with(n, n, equations, XorEncoding::Native)
}

/// **Encode a set of quadratic `F_2`-equations** in `2l` bit-variables,
/// choosing how parity constraints reach the solver.
pub fn encode_equations_with(
    n: u32,
    l: u32,
    equations: Vec<F2BoolPoly>,
    encoding: XorEncoding,
) -> SemaevSatEncoding {
    let num_bit_vars = 2 * l;

    // First pass: collect every quadratic monomial that appears in any
    // equation.  Each gets one auxiliary boolean.
    let mut aux_quad_var: std::collections::BTreeMap<(u32, u32), u32> =
        std::collections::BTreeMap::new();
    for eq in &equations {
        for i in 0..num_bit_vars {
            for j in (i + 1)..num_bit_vars {
                let idx = quad_monomial_index(i, j, num_bit_vars);
                if idx < eq.coeffs.len() && eq.coeffs[idx] {
                    aux_quad_var.entry((i, j)).or_insert(0);
                }
            }
        }
    }

    // Assign auxiliary variable indices (after the bit-variables).
    let mut next = num_bit_vars + 1; // SAT variables are 1-indexed in DIMACS
    for (_, v) in aux_quad_var.iter_mut() {
        *v = next;
        next += 1;
    }
    // Total variable count so far is `next - 1`; XOR-chaining below may
    // add more, so we instantiate the solver lazily after the first pass.

    // Second pass: collect XOR-chaining auxiliaries.  Native parity
    // constraints need none — the chain exists only for the CNF path.
    let mut xor_chain_aux: Vec<Vec<u32>> = Vec::with_capacity(equations.len());
    for eq in &equations {
        if encoding == XorEncoding::Native {
            xor_chain_aux.push(Vec::new());
            continue;
        }
        // `count_xor_terms` counts the constant, which is a parity
        // flip rather than a literal.
        let lit_count =
            count_xor_terms(eq, num_bit_vars, &aux_quad_var) - usize::from(eq.coeffs[0]);
        // Number of intermediate XOR gates for an n-input XOR encoded
        // as a chain of width-2 (3-clause) XOR gates: max(0, n - 1).
        // But to keep clauses short we collapse in groups of up to 3
        // inputs per XOR gate, so we use ⌈(n - 1) / 2⌉ aux vars.
        // For widths ≤ 4 we use the direct encoding and need no aux.
        let aux_needed = xor_chain_aux_needed(lit_count);
        let chain: Vec<u32> = (0..aux_needed)
            .map(|_| {
                let v = next;
                next += 1;
                v
            })
            .collect();
        xor_chain_aux.push(chain);
    }

    let total_vars = next - 1;
    let mut solver = Solver::new(total_vars);
    let mut trivially_unsat = false;

    // Emit the AND constraints for each quadratic auxiliary.
    for ((i, j), &z) in aux_quad_var.iter() {
        // z = xᵢ ∧ xⱼ:
        //   (¬xᵢ ∨ ¬xⱼ ∨ z),
        //   (xᵢ ∨ ¬z),
        //   (xⱼ ∨ ¬z).
        let xi = (i + 1) as Lit;
        let xj = (j + 1) as Lit;
        let zi = z as Lit;
        solver.add_clause(vec![-xi, -xj, zi]);
        solver.add_clause(vec![xi, -zi]);
        solver.add_clause(vec![xj, -zi]);
    }

    // Emit the parity constraint for each equation.
    for (eq, chain) in equations.iter().zip(xor_chain_aux.iter()) {
        let (lits, parity) = collect_xor_lits(eq, num_bit_vars, &aux_quad_var);
        if lits.is_empty() {
            // The equation reduced to `0 = parity`.
            if parity {
                solver.add_clause(vec![]);
                trivially_unsat = true;
            }
            continue;
        }
        match encoding {
            XorEncoding::Native => {
                // `⊕ lits = parity`.  All literals here are positive.
                let vars: Vec<u32> = lits.iter().map(|l| l.unsigned_abs()).collect();
                if !solver.add_xor(&vars, parity) {
                    trivially_unsat = true;
                }
            }
            XorEncoding::Cnf => {
                if encode_xor_eq_zero(&mut solver, &lits, parity, chain) {
                    trivially_unsat = true;
                }
            }
        }
    }

    // The bit-variables are free; every quadratic auxiliary is defined
    // by its AND clauses.
    let free: Vec<u32> = (1..=num_bit_vars).collect();
    solver.set_branch_priority(&free);

    SemaevSatEncoding {
        n,
        l,
        bit_var_offset: 1, // SAT vars 1..=num_bit_vars are bit-vars.
        aux_quad_var,
        solver,
        trivially_unsat,
    }
}

/// Decode a satisfying assignment into the two `F_{2^n}` x-coords.
///
/// Only the low `l` bits of each are free — the rest are zero by
/// construction, since both lie in the factor-base subspace.
pub fn decode_x1_x2(enc: &SemaevSatEncoding) -> (F2mElement, F2mElement) {
    let model = enc.solver.model();
    let (n, l) = (enc.n, enc.l);
    let bits_x1: Vec<u32> = (0..l).filter(|i| model[*i as usize]).collect();
    let bits_x2: Vec<u32> = (0..l).filter(|i| model[(l + *i) as usize]).collect();
    (
        F2mElement::from_bit_positions(&bits_x1, n),
        F2mElement::from_bit_positions(&bits_x2, n),
    )
}

// ── S₄ (three-point decomposition) ──────────────────────────────────

/// A SAT-encoded, symmetrised binary Semaev `S₄` system: "is the target
/// x-coordinate the sum of three factor-base points?"
pub struct S4SatEncoding {
    pub n: u32,
    pub l: u32,
    /// `3l` variables for the bits of `X₁, X₂, X₃`, at SAT indices
    /// `1..=3l`.
    pub n_x_vars: u32,
    /// `6l − 3` variables for the coefficients of `e₁, e₂, e₃`,
    /// immediately after the x-variables.
    pub n_e_vars: u32,
    /// One auxiliary per distinct monomial of degree ≥ 2, after those.
    pub n_aux_vars: u32,
    pub solver: Solver,
    pub trivially_unsat: bool,
}

impl S4SatEncoding {
    /// Decode a satisfying assignment into the three factor-base
    /// x-coordinates.
    pub fn decode(&self) -> [F2mElement; 3] {
        let model = self.solver.model();
        let l = self.l;
        std::array::from_fn(|i| {
            let bits: Vec<u32> = (0..l)
                .filter(|j| model[(i as u32 * l + *j) as usize])
                .collect();
            F2mElement::from_bit_positions(&bits, self.n)
        })
    }
}

/// Knobs for the `S₄` encoder.
#[derive(Debug, Clone, Copy)]
pub struct S4Options {
    /// How parity constraints reach the solver.
    pub encoding: XorEncoding,
    /// Add lexicographic ordering constraints `X₁ ≤ X₂ ≤ X₃`.
    ///
    /// The whole system — both the descended `S₄` and the `eᵢ`
    /// correspondence — is symmetric in `X₁, X₂, X₃`, so every solution
    /// occurs in all `3! = 6` orderings and the search rediscovers each
    /// of them.  Forcing a canonical order preserves satisfiability and
    /// cuts the space by up to `6×`; it costs `O(l)` clauses per pair.
    pub break_symmetry: bool,
}

impl Default for S4Options {
    fn default() -> Self {
        Self {
            encoding: XorEncoding::Native,
            break_symmetry: true,
        }
    }
}

/// **Encode the symmetrised binary Semaev `S₄` system** for target
/// x-coordinate `x_r`, with the three unknowns confined to the
/// `l`-dimensional factor-base subspace.
///
/// The model has two halves (see
/// [`crate::cryptanalysis::binary_semaev_s4`]): a correspondence tying
/// each `e`-variable to a symmetric function of the `X`-bits, and the
/// descended `S₄` itself over the `e`-variables.  Both are parity
/// constraints over monomials, so with [`XorEncoding::Native`] the only
/// clauses emitted are the AND-definitions of the monomials — the
/// constraints themselves cost nothing in CNF.
pub fn encode_semaev_s4(
    n: u32,
    l: u32,
    irr: &IrreduciblePoly,
    b: &F2mElement,
    x_r: &F2mElement,
    encoding: XorEncoding,
) -> S4SatEncoding {
    encode_semaev_s4_with(
        n,
        l,
        irr,
        b,
        x_r,
        S4Options {
            encoding,
            ..Default::default()
        },
    )
}

/// [`encode_semaev_s4`] with the full set of knobs.
pub fn encode_semaev_s4_with(
    n: u32,
    l: u32,
    irr: &IrreduciblePoly,
    b: &F2mElement,
    x_r: &F2mElement,
    opts: S4Options,
) -> S4SatEncoding {
    let encoding = opts.encoding;
    let sys = weil_descend_s4(n, l, irr, b, x_r);
    let n_x = sys.n_x_vars();
    let n_e = sys.n_e_vars();

    // Map each ANF monomial from its own variable space into the single
    // SAT numbering, so that an x-monomial and an e-monomial can never
    // collide in the auxiliary map.
    let to_sat_x = |v: u32| v + 1;
    let to_sat_e = |v: u32| n_x + v + 1;

    let mut rows: Vec<(Vec<Vec<u32>>, bool, Option<u32>)> = Vec::new();
    for (i, row) in sys.correspondence.iter().enumerate() {
        for (d, sigma) in row.iter().enumerate() {
            let monos: Vec<Vec<u32>> = sigma
                .monomials()
                .filter(|m| !m.is_empty())
                .map(|m| m.iter().map(|v| to_sat_x(*v)).collect())
                .collect();
            let e_sat = to_sat_e(sys.e_var(i, d));
            rows.push((monos, sigma.has_constant(), Some(e_sat)));
        }
    }
    for eq in &sys.semaev {
        let monos: Vec<Vec<u32>> = eq
            .monomials()
            .filter(|m| !m.is_empty())
            .map(|m| m.iter().map(|v| to_sat_e(*v)).collect())
            .collect();
        rows.push((monos, eq.has_constant(), None));
    }

    // Allocate one auxiliary per distinct monomial of degree ≥ 2.
    let mut aux_of: std::collections::BTreeMap<Vec<u32>, u32> = std::collections::BTreeMap::new();
    for (monos, _, _) in &rows {
        for m in monos {
            if m.len() >= 2 {
                aux_of.entry(m.clone()).or_insert(0);
            }
        }
    }
    let mut next = n_x + n_e + 1;
    for v in aux_of.values_mut() {
        *v = next;
        next += 1;
    }
    let n_aux = next - (n_x + n_e + 1);

    // The CNF path additionally needs chain auxiliaries per row.
    let mut chains: Vec<Vec<u32>> = Vec::with_capacity(rows.len());
    for (monos, _, e_sat) in &rows {
        if encoding == XorEncoding::Native {
            chains.push(Vec::new());
            continue;
        }
        let width = monos.len() + usize::from(e_sat.is_some());
        let count = parity_cnf_aux_count(width);
        chains.push(
            (0..count)
                .map(|_| {
                    let v = next;
                    next += 1;
                    v
                })
                .collect(),
        );
    }

    // Lexicographic ordering needs one "equal so far" auxiliary per bit
    // position per adjacent pair.
    let sym_base = next;
    if opts.break_symmetry {
        next += 2 * l;
    }

    let mut solver = Solver::new(next - 1);
    let mut trivially_unsat = false;

    if opts.break_symmetry {
        // X₁ ≤ X₂ and X₂ ≤ X₃, lexicographically on the bit vectors.
        for pair in 0..2u32 {
            let a: Vec<u32> = (0..l)
                .map(|j| to_sat_x(sys.x_var(pair as usize, j)))
                .collect();
            let bb: Vec<u32> = (0..l)
                .map(|j| to_sat_x(sys.x_var(pair as usize + 1, j)))
                .collect();
            let eq: Vec<u32> = (0..l).map(|j| sym_base + pair * l + j).collect();
            encode_lex_le(&mut solver, &a, &bb, &eq);
        }
    }

    // AND-definitions: `z ↔ v₁ ∧ … ∧ v_k`.
    for (mono, &z) in aux_of.iter() {
        let zi = z as Lit;
        let mut big = Vec::with_capacity(mono.len() + 1);
        big.push(zi);
        for &v in mono {
            solver.add_clause(vec![-zi, v as Lit]);
            big.push(-(v as Lit));
        }
        solver.add_clause(big);
    }

    // One parity constraint per row.
    for ((monos, rhs, e_sat), chain) in rows.iter().zip(chains.iter()) {
        let mut vars: Vec<u32> = Vec::with_capacity(monos.len() + 1);
        if let Some(e) = e_sat {
            vars.push(*e);
        }
        for m in monos {
            vars.push(if m.len() == 1 { m[0] } else { aux_of[m] });
        }
        if vars.is_empty() {
            if *rhs {
                solver.add_clause(vec![]);
                trivially_unsat = true;
            }
            continue;
        }
        match encoding {
            XorEncoding::Native => {
                if !solver.add_xor(&vars, *rhs) {
                    trivially_unsat = true;
                }
            }
            XorEncoding::Cnf => {
                let lits: Vec<Lit> = vars.iter().map(|v| *v as Lit).collect();
                if encode_xor_eq_zero(&mut solver, &lits, *rhs, chain) {
                    trivially_unsat = true;
                }
            }
        }
    }

    // Every other variable is defined: monomials by their AND clauses,
    // e-variables by the correspondence rows.  Branching on the x-bits
    // alone is enough to determine the whole assignment.
    let free: Vec<u32> = (1..=n_x).collect();
    solver.set_branch_priority(&free);

    S4SatEncoding {
        n,
        l,
        n_x_vars: n_x,
        n_e_vars: n_e,
        n_aux_vars: n_aux,
        solver,
        trivially_unsat,
    }
}

/// Constrain `a ≤ b` lexicographically, reading `a[l−1]` as the most
/// significant bit.
///
/// `eq[k]` means "`a` and `b` agree on every bit strictly above `k`",
/// so `eq[l−1]` is unconditionally true and each step down carries the
/// equality forward.  At each position the ordering is enforced by
/// `eq[k] ∧ a[k] → b[k]`, which forbids `a` from being the first to
/// carry a `1`.
///
/// `2l + 1` clauses per pair, all of length ≤ 4.
fn encode_lex_le(solver: &mut Solver, a: &[u32], b: &[u32], eq: &[u32]) {
    let l = a.len();
    debug_assert!(b.len() == l && eq.len() == l);
    if l == 0 {
        return;
    }
    let top = l - 1;
    // Above the most significant bit, the prefixes are trivially equal.
    solver.add_clause(vec![eq[top] as Lit]);

    for k in (0..l).rev() {
        let (ak, bk, ek) = (a[k] as Lit, b[k] as Lit, eq[k] as Lit);
        // eq[k] ∧ a[k] → b[k]
        solver.add_clause(vec![-ek, -ak, bk]);
        if k == 0 {
            continue;
        }
        // eq[k−1] ↔ eq[k] ∧ (a[k] ↔ b[k]).  Only the ← direction is
        // needed for soundness of the ordering, but both keep the
        // auxiliary determined, which is what stops it becoming a free
        // variable the search has to case-split on.
        let ep = eq[k - 1] as Lit;
        solver.add_clause(vec![-ep, ek]);
        solver.add_clause(vec![-ep, -ak, bk]);
        solver.add_clause(vec![-ep, ak, -bk]);
        solver.add_clause(vec![ep, -ek, ak, bk]);
        solver.add_clause(vec![ep, -ek, -ak, -bk]);
    }
}

/// Auxiliaries needed to Tseitin-chain a `w`-wide parity into clauses
/// of length ≤ 4: the first gate consumes three inputs, each later gate
/// two more.
fn parity_cnf_aux_count(w: usize) -> usize {
    if w <= 3 {
        0
    } else {
        (w - 2) / 2
    }
}

// ── XOR encoding helpers ────────────────────────────────────────────

/// Intermediate XOR gates needed to encode a parity constraint over
/// `effective_lits` literals (the constant term is a parity flip, not a
/// literal, so it does not count).
///
/// Widths `≤ 4` use the direct `2^{w−1}`-clause expansion and need
/// none.  Wider sums are folded by [`encode_xor_eq_zero`] three
/// literals at a time, each fold consuming one auxiliary, and the
/// trailing one or two literals are closed by a direct expansion — so
/// the count is `⌊w / 3⌋`.
fn xor_chain_aux_needed(effective_lits: usize) -> usize {
    if effective_lits <= 4 {
        0
    } else {
        effective_lits / 3
    }
}

fn count_xor_terms(
    eq: &F2BoolPoly,
    num_vars: u32,
    aux_quad_var: &std::collections::BTreeMap<(u32, u32), u32>,
) -> usize {
    let mut n_terms = 0;
    if eq.coeffs[0] {
        n_terms += 1; // constant 1
    }
    for i in 0..num_vars as usize {
        if eq.coeffs[1 + i] {
            n_terms += 1;
        }
    }
    for i in 0..num_vars {
        for j in (i + 1)..num_vars {
            let idx = quad_monomial_index(i, j, num_vars);
            if idx < eq.coeffs.len() && eq.coeffs[idx] {
                debug_assert!(aux_quad_var.contains_key(&(i, j)));
                n_terms += 1;
            }
        }
    }
    n_terms
}

/// Collect the literals (positive, no negations) whose parity the
/// equation constrains, together with the target parity.
///
/// The target is the equation's constant term: `Σ monomials = c`.  It
/// is returned as a separate `bool` rather than smuggled in-band — an
/// earlier version pushed a sentinel `0` into the literal vector, which
/// is also the DIMACS clause terminator, so any refactor forwarding
/// these literals to `add_clause` would have emitted a truncated clause
/// with no diagnostic.
fn collect_xor_lits(
    eq: &F2BoolPoly,
    num_vars: u32,
    aux_quad_var: &std::collections::BTreeMap<(u32, u32), u32>,
) -> (Vec<Lit>, bool) {
    let mut lits: Vec<Lit> = Vec::new();
    for i in 0..num_vars as usize {
        if eq.coeffs[1 + i] {
            lits.push((i + 1) as Lit);
        }
    }
    for i in 0..num_vars {
        for j in (i + 1)..num_vars {
            let idx = quad_monomial_index(i, j, num_vars);
            if idx < eq.coeffs.len() && eq.coeffs[idx] {
                let z = aux_quad_var[&(i, j)];
                lits.push(z as Lit);
            }
        }
    }
    (lits, eq.coeffs[0])
}

/// Emit clauses enforcing `XOR(lits) = target_parity`, using direct
/// expansion for widths ≤ 4 and chained 3-XOR gates for wider sums.
/// Returns `true` if an empty clause was emitted (= trivially UNSAT,
/// e.g. `0 = 1`).
///
/// This is the [`XorEncoding::Cnf`] path, kept so the two encodings can
/// be measured against each other.  [`XorEncoding::Native`] hands the
/// same constraint to the solver's Gauss-Jordan engine instead, which
/// costs no auxiliary variables and no clauses at all.
fn encode_xor_eq_zero(
    solver: &mut Solver,
    lits: &[Lit],
    target_parity: bool,
    chain: &[u32],
) -> bool {
    let mut effective: Vec<Lit> = lits.to_vec();

    if effective.is_empty() {
        if target_parity {
            // 0 = 1: unsatisfiable.  Add the empty clause and signal UNSAT.
            solver.add_clause(vec![]);
            return true;
        }
        return false;
    }

    if effective.len() <= 4 {
        emit_direct_xor(solver, &effective, target_parity);
        return false;
    }

    // Wider sum: chain 3-input XOR gates.
    //   y_1 = a_1 XOR a_2 XOR a_3
    //   y_2 = y_1 XOR a_4 XOR a_5
    //   y_3 = y_2 XOR a_6 XOR a_7
    //   ...
    //   final XOR(y_last, a_last_pair) = target_parity
    let mut iter = effective.drain(..);
    let mut current_aux: Option<Lit> = None;
    let mut chain_iter = chain.iter().copied();

    loop {
        let a = match iter.next() {
            Some(x) => x,
            None => break,
        };
        let b = iter.next();
        match (current_aux, b) {
            (None, None) => {
                // Single literal remains: XOR = a.  Force a = target.
                if target_parity {
                    solver.add_clause(vec![a]); // a = true
                } else {
                    solver.add_clause(vec![-a]); // a = false
                }
                return false;
            }
            (None, Some(b_lit)) => {
                // Start chain: y = a XOR b.  If more remain, create aux.
                let c = iter.next();
                if let Some(c_lit) = c {
                    let aux = chain_iter.next().expect("ran out of XOR-chain auxiliaries");
                    encode_xor3_eq_aux(solver, a, b_lit, c_lit, aux as Lit);
                    current_aux = Some(aux as Lit);
                } else {
                    // Exactly two remain: enforce a XOR b = target_parity.
                    emit_direct_xor(solver, &[a, b_lit], target_parity);
                    return false;
                }
            }
            (Some(prev), None) => {
                // Trailing single literal: enforce prev XOR a = target.
                emit_direct_xor(solver, &[prev, a], target_parity);
                return false;
            }
            (Some(prev), Some(b_lit)) => {
                let c = iter.next();
                if let Some(c_lit) = c {
                    let aux = chain_iter.next().expect("ran out of XOR-chain auxiliaries");
                    // y_new = prev XOR a XOR b XOR c.
                    // Decompose: tmp = prev XOR a XOR b, then aux = tmp XOR c.
                    // Encode in two stages — but we only have one aux.
                    // Combine into a single 5-XOR via direct expansion
                    // if 5 lits fit a small clause budget, else fall back.
                    // For simplicity, encode a 4-XOR aux = prev XOR a XOR b
                    // and then a 3-XOR aux2 = aux XOR c XOR (next).  We
                    // approximate by encoding aux = XOR(prev, a, b, c).
                    encode_xor4_eq_aux(solver, prev, a, b_lit, c_lit, aux as Lit);
                    current_aux = Some(aux as Lit);
                } else {
                    // Exactly 3 remain across this iteration: enforce
                    // prev XOR a XOR b = target.
                    emit_direct_xor(solver, &[prev, a, b_lit], target_parity);
                    return false;
                }
            }
        }
    }

    if let Some(prev) = current_aux {
        // Nothing more to consume; the chain's last aux is the answer.
        if target_parity {
            solver.add_clause(vec![prev]);
        } else {
            solver.add_clause(vec![-prev]);
        }
    }
    false
}

/// Direct CNF expansion of `XOR(lits) = target_parity` for widths ≤ 4.
/// Emits exactly `2^{w-1}` clauses, each of length `w`.
fn emit_direct_xor(solver: &mut Solver, lits: &[Lit], target_parity: bool) {
    let w = lits.len();
    for assignment in 0..(1u32 << w) {
        // Count bits = parity of this assignment.
        let parity = (assignment.count_ones() % 2) == 1;
        // We want to forbid the assignments whose XOR ≠ target_parity.
        if parity != target_parity {
            // Emit a clause forbidding this assignment.
            let mut clause = Vec::with_capacity(w);
            for (i, &lit) in lits.iter().enumerate() {
                let bit = (assignment >> i) & 1 == 1;
                // If bit=1 the literal is true in this assignment, so
                // to forbid it we add ¬lit; otherwise add lit.
                if bit {
                    clause.push(-lit);
                } else {
                    clause.push(lit);
                }
            }
            solver.add_clause(clause);
        }
    }
}

/// Constraint: `aux = a XOR b XOR c`.  4 clauses, each length 4.
fn encode_xor3_eq_aux(solver: &mut Solver, a: Lit, b: Lit, c: Lit, aux: Lit) {
    // (a XOR b XOR c XOR aux) = 0 with target_parity = false.
    emit_direct_xor(solver, &[a, b, c, aux], false);
}

/// Constraint: `aux = a XOR b XOR c XOR d`.  8 clauses, each length 5.
/// We use this only when chaining; not the cheapest encoding but
/// sufficient.
fn encode_xor4_eq_aux(solver: &mut Solver, a: Lit, b: Lit, c: Lit, d: Lit, aux: Lit) {
    emit_direct_xor(solver, &[a, b, c, d, aux], false);
}

// ── Tests ───────────────────────────────────────────────────────────

// ── Generic sparse Boolean systems ─────────────────────────────────
//
// The encoder above is tied to the `ffd_harness` representation: a
// dense coefficient vector over the monomials of degree ≤ 2 in exactly
// `2n` variables — the shape of a full-field Weil descent of `S₃`.
// Index calculus over a *restricted* factor base produces a different
// shape: sparse polynomials over `m·ℓ` subspace coordinates (plus
// chaining unknowns), and for `m ≥ 3` of degree 3 rather than 2.  The
// encoder below takes that representation, so the same CDCL solver can
// answer the same decomposition question the Gröbner engine does.

/// A SAT encoding of an arbitrary sparse Boolean polynomial system.
pub struct BoolSystemSatEncoding {
    /// Number of problem variables (SAT variables `1 ..= n_vars`).
    pub n_vars: usize,
    /// Tseitin auxiliary for each monomial of degree ≥ 2, keyed by the
    /// monomial's variable mask.
    pub monomial_var: std::collections::BTreeMap<u64, u32>,
    /// The CDCL solver with every clause installed.
    pub solver: Solver,
    /// Set when encoding produced the empty clause (`1 = 0`), i.e. the
    /// system is unsatisfiable before search even starts.
    pub trivially_unsat: bool,
}

impl BoolSystemSatEncoding {
    /// Decode the current model into a bitmask over the problem
    /// variables, in the same layout the Gröbner solver returns.
    pub fn model_assignment(&self) -> u64 {
        let model = self.solver.model();
        let mut out = 0u64;
        for i in 0..self.n_vars {
            if model[i] {
                out |= 1 << i;
            }
        }
        out
    }
}

/// **Encode a sparse Boolean system** into CNF.
///
/// Each monomial of degree `k ≥ 2` gets one Tseitin auxiliary
/// `z = v_{i_1} ∧ … ∧ v_{i_k}` (`k + 1` clauses); each equation becomes
/// one parity constraint over its monomials' literals, with the
/// constant term flipping the target parity.  Assignments in `blocked`
/// are excluded by a blocking clause each, so the caller can enumerate
/// models by re-encoding with the ones it has already rejected.
///
/// Unlike [`encode_equations`], this places no restriction on the
/// degree or on the number of variables.
pub fn encode_boolean_system(
    n_vars: usize,
    equations: &[BoolPoly],
    blocked: &[u64],
) -> BoolSystemSatEncoding {
    encode_boolean_system_with(n_vars, equations, blocked, XorEncoding::Cnf)
}

/// Encode a sparse Boolean system with either CNF or native XOR rows.
/// Monomial definitions and model blocking are identical in both modes.
/// The original entry point retains CNF for reproducible comparisons.
pub fn encode_boolean_system_with(
    n_vars: usize,
    equations: &[BoolPoly],
    blocked: &[u64],
    encoding: XorEncoding,
) -> BoolSystemSatEncoding {
    assert!(n_vars <= 64, "problem variables are packed into a u64");
    assert!(
        equations
            .iter()
            .flat_map(|eq| &eq.terms)
            .all(|t| { n_vars == 64 || (t.mask >> n_vars) == 0 }),
        "monomial references a variable outside the system"
    );

    // One auxiliary per distinct monomial of degree ≥ 2.
    let mut monomial_var: std::collections::BTreeMap<u64, u32> = std::collections::BTreeMap::new();
    for eq in equations {
        for t in &eq.terms {
            if t.mask.count_ones() >= 2 {
                monomial_var.insert(t.mask, 0);
            }
        }
    }
    let mut next = n_vars as u32 + 1; // DIMACS variables are 1-indexed
    for v in monomial_var.values_mut() {
        *v = next;
        next += 1;
    }

    // Chaining auxiliaries for the wide parity constraints.
    let mut xor_chain_aux: Vec<Vec<u32>> = Vec::with_capacity(equations.len());
    for eq in equations {
        let effective = eq.terms.iter().filter(|t| t.mask != 0).count();
        let count = match encoding {
            XorEncoding::Cnf => xor_chain_aux_needed(effective),
            XorEncoding::Native => 0,
        };
        let chain: Vec<u32> = (0..count)
            .map(|_| {
                let v = next;
                next += 1;
                v
            })
            .collect();
        xor_chain_aux.push(chain);
    }

    let mut solver = Solver::new(next - 1);
    let mut trivially_unsat = false;

    // z ↔ v_{i_1} ∧ … ∧ v_{i_k}.
    for (&mask, &z) in monomial_var.iter() {
        let vars: Vec<Lit> = (0..n_vars)
            .filter(|i| (mask >> i) & 1 == 1)
            .map(|i| (i + 1) as Lit)
            .collect();
        let mut big = vars.iter().map(|v| -v).collect::<Vec<Lit>>();
        big.push(z as Lit);
        solver.add_clause(big);
        for v in vars {
            solver.add_clause(vec![v, -(z as Lit)]);
        }
    }

    // One parity constraint per equation.
    for (eq, chain) in equations.iter().zip(xor_chain_aux.iter()) {
        let mut lits: Vec<Lit> = Vec::with_capacity(eq.terms.len());
        let mut has_constant = false;
        for t in &eq.terms {
            match t.mask.count_ones() {
                0 => has_constant = true,
                1 => lits.push((t.mask.trailing_zeros() + 1) as Lit),
                _ => lits.push(monomial_var[&t.mask] as Lit),
            }
        }
        if lits.is_empty() && !has_constant {
            continue; // 0 = 0
        }
        // The constant is the target parity, not a literal — the chain
        // widths above already count it that way.
        match encoding {
            XorEncoding::Native => {
                let vars: Vec<u32> = lits.iter().map(|&v| v as u32).collect();
                if !solver.add_xor(&vars, has_constant) {
                    trivially_unsat = true;
                }
            }
            XorEncoding::Cnf => {
                if encode_xor_eq_zero(&mut solver, &lits, has_constant, chain) {
                    trivially_unsat = true;
                }
            }
        }
    }

    // Exclude assignments the caller has already seen and rejected.
    for &a in blocked {
        let clause: Vec<Lit> = (0..n_vars)
            .map(|i| {
                let lit = (i + 1) as Lit;
                if (a >> i) & 1 == 1 {
                    -lit
                } else {
                    lit
                }
            })
            .collect();
        if !solver.add_clause(clause) {
            trivially_unsat = true;
        }
    }

    BoolSystemSatEncoding {
        n_vars,
        monomial_var,
        solver,
        trivially_unsat,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cryptanalysis::binary_semaev_s4::{elementary_symmetric_3, symmetrised_s4_eval};
    use crate::cryptanalysis::pq_groebner_f2::F2BoolMono;

    /// Compare complete model sets with direct evaluation, including
    /// incremental blocking after XOR propagation and backtracking.
    #[test]
    fn sparse_encodings_match_exhaustive_model_sets() {
        use rand::{Rng, SeedableRng};
        let mut rng = rand::rngs::StdRng::seed_from_u64(0x534154);
        for n in 0..=6usize {
            for _ in 0..16 {
                let equations: Vec<BoolPoly> = (0..rng.gen_range(0..=6))
                    .map(|_| {
                        let terms = (0..rng.gen_range(0..=12))
                            .map(|_| F2BoolMono::from_mask(rng.gen_range(0..(1u64 << n))))
                            .collect();
                        BoolPoly::from_monos(terms, n)
                    })
                    .collect();
                let expected: std::collections::BTreeSet<u64> = (0..(1u64 << n))
                    .filter(|&a| equations.iter().all(|e| e.eval(a) == 0))
                    .collect();
                for mode in [XorEncoding::Cnf, XorEncoding::Native] {
                    let mut enc = encode_boolean_system_with(n, &equations, &[], mode);
                    let mut actual = std::collections::BTreeSet::new();
                    loop {
                        match enc.solver.solve() {
                            SolveResult::Sat => {
                                let a = enc.model_assignment();
                                assert!(actual.insert(a), "duplicate model: n={n}, {mode:?}");
                                assert!(expected.contains(&a), "invalid model: n={n}, {mode:?}");
                                enc.solver.reset_search();
                                let clause = (0..n)
                                    .map(|i| {
                                        let v = (i + 1) as Lit;
                                        if (a >> i) & 1 == 1 {
                                            -v
                                        } else {
                                            v
                                        }
                                    })
                                    .collect();
                                enc.solver.add_clause(clause);
                            }
                            SolveResult::Unsat => break,
                            SolveResult::Unknown => panic!("tiny exhaustive check exhausted"),
                        }
                    }
                    assert_eq!(actual, expected, "n={n}, {mode:?}");
                    let all: Vec<u64> = expected.iter().copied().collect();
                    let mut blocked = encode_boolean_system_with(n, &equations, &all, mode);
                    assert_eq!(blocked.solver.solve(), SolveResult::Unsat);
                }
            }
        }
    }

    /// Parity constraints must be encoded exactly at every width.
    ///
    /// Regression test: the chain-auxiliary count used to be
    /// `⌈(w+1)/2⌉ − 2`, which under-allocates from `w = 6` on — the
    /// encoder then panicked with "ran out of XOR-chain auxiliaries".
    /// The fold consumes three literals per auxiliary, so the count is
    /// `⌊w/3⌋`.
    #[test]
    fn xor_parity_encoding_is_exact_at_every_width() {
        for w in 1..=12usize {
            for constant in [false, true] {
                let mut monos: Vec<F2BoolMono> =
                    (0..w).map(|i| F2BoolMono::var(i as u32)).collect();
                if constant {
                    monos.push(F2BoolMono::one());
                }
                let eq = BoolPoly::from_monos(monos, w);

                let mut enc = encode_boolean_system(w, std::slice::from_ref(&eq), &[]);
                assert!(!enc.trivially_unsat, "w = {w}, constant = {constant}");
                assert_eq!(
                    enc.solver.solve(),
                    SolveResult::Sat,
                    "w = {w}, constant = {constant}"
                );
                assert_eq!(eq.eval(enc.model_assignment()), 0);

                // Small widths: enumerate every model and count them.
                // A w-input parity constraint has exactly 2^{w−1}.
                if w <= 8 {
                    let mut blocked: Vec<u64> = Vec::new();
                    loop {
                        let mut e = encode_boolean_system(w, std::slice::from_ref(&eq), &blocked);
                        match e.solver.solve() {
                            SolveResult::Sat => {
                                let m = e.model_assignment();
                                assert_eq!(eq.eval(m), 0, "model violates the equation");
                                blocked.push(m);
                            }
                            SolveResult::Unsat => break,
                            SolveResult::Unknown => panic!("budget exhausted at w = {w}"),
                        }
                    }
                    assert_eq!(
                        blocked.len(),
                        1usize << (w - 1),
                        "w = {w}, constant = {constant}"
                    );
                }
            }
        }
    }

    /// Higher-degree monomials get Tseitin auxiliaries too — the
    /// `m ≥ 3` chained Semaev systems are cubic, not quadratic.
    #[test]
    fn cubic_monomials_are_encoded() {
        // v0·v1·v2 + 1 = 0  ⇒  all three must be true.
        let eq = BoolPoly::from_monos(vec![F2BoolMono::from_mask(0b111), F2BoolMono::one()], 3);
        let mut enc = encode_boolean_system(3, std::slice::from_ref(&eq), &[]);
        assert_eq!(
            enc.monomial_var.len(),
            1,
            "one auxiliary for the cubic term"
        );
        assert_eq!(enc.solver.solve(), SolveResult::Sat);
        assert_eq!(enc.model_assignment(), 0b111);
    }

    /// An unsatisfiable system is reported as UNSAT, not as a model.
    #[test]
    fn contradictory_system_is_unsat() {
        let p = BoolPoly::from_monos(vec![F2BoolMono::var(0)], 2);
        let q = BoolPoly::from_monos(vec![F2BoolMono::var(0), F2BoolMono::one()], 2);
        let mut enc = encode_boolean_system(2, &[p, q], &[]);
        assert!(enc.trivially_unsat || enc.solver.solve() == SolveResult::Unsat);
    }

    fn irr_for(n: u32) -> IrreduciblePoly {
        match n {
            3 => IrreduciblePoly {
                degree: 3,
                low_terms: vec![0, 1],
            },
            4 => IrreduciblePoly {
                degree: 4,
                low_terms: vec![0, 1],
            },
            5 => IrreduciblePoly {
                degree: 5,
                low_terms: vec![0, 2],
            },
            6 => IrreduciblePoly {
                degree: 6,
                low_terms: vec![0, 1],
            },
            _ => panic!("no irreducible for n = {}", n),
        }
    }

    // ── S₄, three-point decomposition ───────────────────────────────

    /// `n = 19`, `l = 6` Koblitz parameters from `INFOn19l6-1-S` in the
    /// reference corpus (see `RESEARCH_TRIMOSKA_BENCHMARKS.md`), with
    /// the decomposition that generator planted.
    fn corpus_n19l6() -> (u32, u32, IrreduciblePoly, F2mElement) {
        let n = 19;
        let irr = IrreduciblePoly {
            degree: 19,
            low_terms: vec![0, 1, 2, 5],
        };
        let x_r = F2mElement::from_bit_positions(&[1, 2, 5, 6, 7, 8, 10, 11, 12, 16], n);
        (n, 6, irr, x_r)
    }

    /// **End-to-end at `n = 19`.**  Encode the corpus instance, solve,
    /// decode three factor-base x-coordinates, and confirm the
    /// symmetrised `S₄` vanishes on them.
    ///
    /// The two things that make this reachable: the unknowns are
    /// confined to the factor base (18 bits, not 38), and the parity
    /// constraints go to the solver natively instead of through Tseitin.
    /// **The lex encoder must accept exactly the ordered pairs.**  For
    /// every `(a, b)` over `l = 4` bits, forcing both vectors and
    /// solving must return SAT precisely when `a ≤ b`.
    #[test]
    fn lex_le_accepts_exactly_the_ordered_pairs() {
        let l = 4usize;
        for a_val in 0..(1u32 << l) {
            for b_val in 0..(1u32 << l) {
                let a: Vec<u32> = (1..=l as u32).collect();
                let b: Vec<u32> = (l as u32 + 1..=2 * l as u32).collect();
                let eq: Vec<u32> = (2 * l as u32 + 1..=3 * l as u32).collect();
                let mut s = Solver::new(3 * l as u32);
                encode_lex_le(&mut s, &a, &b, &eq);
                for k in 0..l {
                    let av = if (a_val >> k) & 1 == 1 { 1 } else { -1 };
                    let bv = if (b_val >> k) & 1 == 1 { 1 } else { -1 };
                    s.add_clause(vec![av * a[k] as Lit]);
                    s.add_clause(vec![bv * b[k] as Lit]);
                }
                let want = a_val <= b_val;
                let got = s.solve() == SolveResult::Sat;
                assert_eq!(got, want, "a = {a_val}, b = {b_val}");
            }
        }
    }

    /// **Symmetry breaking must preserve satisfiability.**  The system
    /// is symmetric in `X₁, X₂, X₃`, so forcing a canonical order can
    /// only remove duplicate solutions — never the last one.  Checked
    /// on the smallest corpus family, both labels.
    #[test]
    fn symmetry_breaking_preserves_satisfiability() {
        use crate::cryptanalysis::semaev_corpus::CORPUS;
        for inst in CORPUS.iter().filter(|c| c.n == 15) {
            let plain = encode_semaev_s4_with(
                inst.n,
                inst.l,
                &inst.irr(),
                &inst.b(),
                &inst.x_r(),
                S4Options {
                    encoding: XorEncoding::Native,
                    break_symmetry: false,
                },
            );
            let sym = encode_semaev_s4_with(
                inst.n,
                inst.l,
                &inst.irr(),
                &inst.b(),
                &inst.x_r(),
                S4Options {
                    encoding: XorEncoding::Native,
                    break_symmetry: true,
                },
            );
            // Both encodings must at least agree on being non-trivial.
            assert!(
                !plain.trivially_unsat && !sym.trivially_unsat,
                "{}",
                inst.name
            );
            // The ordered witness of a satisfiable instance survives.
            if inst.truly_sat {
                let xs = inst
                    .decide_exhaustively()
                    .expect("truly_sat instance has a witness");
                // `decide_exhaustively` searches X₁ ≤ X₂ ≤ X₃ already,
                // so its witness is exactly the canonical representative
                // the ordering constraints keep.
                let vals: Vec<u32> = xs
                    .iter()
                    .map(|x| {
                        (0..inst.l)
                            .filter(|j| (x.raw_bits()[(*j / 64) as usize] >> (*j % 64)) & 1 == 1)
                            .map(|j| 1u32 << j)
                            .sum()
                    })
                    .collect();
                assert!(
                    vals[0] <= vals[1] && vals[1] <= vals[2],
                    "{}: exhaustive witness is not canonically ordered",
                    inst.name
                );
            }
        }
    }

    /// **Independent agreement on instance size.**  Upstream's C
    /// generator emits `p cnf 767 2416` with 52 `x`-lines for this
    /// family, i.e. 767 variables, 2364 ordinary clauses and 52 parity
    /// rows.  Our encoder, written from the algebra rather than from
    /// their code, must land on exactly the same shape — a much
    /// sharper check on the modelling than any single instance solving.
    ///
    /// Symmetry breaking is switched off here: it is our addition, not
    /// part of the modelling being compared.
    #[test]
    fn s4_encoding_size_matches_upstream_generator() {
        let (n, l, irr, x_r) = corpus_n19l6();
        let b = F2mElement::one(n);
        let enc = encode_semaev_s4_with(
            n,
            l,
            &irr,
            &b,
            &x_r,
            S4Options {
                encoding: XorEncoding::Native,
                break_symmetry: false,
            },
        );
        assert_eq!(enc.solver.n_vars(), 767, "variable count");
        assert_eq!(enc.solver.n_clauses(), 2364, "ordinary clause count");
        assert_eq!(enc.solver.n_xors(), 52, "parity row count");
        // 3l x-variables + (6l − 3) e-variables + one per monomial.
        assert_eq!(enc.n_x_vars, 18);
        assert_eq!(enc.n_e_vars, 33);
        assert_eq!(enc.n_x_vars + enc.n_e_vars + enc.n_aux_vars, 767);
    }

    /// **End-to-end at `n = 15`** — the smaller corpus family.
    #[test]
    fn semaev_s4_round_trip_n15() {
        let n = 15;
        let l = 5;
        let irr = IrreduciblePoly {
            degree: 15,
            low_terms: vec![0, 2, 4, 5],
        };
        // Target and planted decomposition from `INFOn15l5-1-S`.
        let x_r = F2mElement::from_bit_positions(&[1, 2, 6, 7, 9, 12, 14], n);
        let b = F2mElement::one(n);
        let mut enc = encode_semaev_s4(n, l, &irr, &b, &x_r, XorEncoding::Native);
        enc.solver.conflict_budget = 5_000_000;
        assert_eq!(enc.solver.solve(), SolveResult::Sat);
        let xs = enc.decode();
        let (e1, e2, e3) = elementary_symmetric_3(&xs[0], &xs[1], &xs[2], &irr);
        assert!(symmetrised_s4_eval(&e1, &e2, &e3, &x_r, &irr).is_zero());
    }

    /// **End-to-end at `n = 19`.**  Encode the corpus instance, solve,
    /// decode three factor-base x-coordinates, and confirm the
    /// symmetrised `S₄` vanishes on them.
    ///
    /// The two things that make this reachable at all: the unknowns are
    /// confined to the factor base (18 bits, not 38), and the parity
    /// constraints go to the solver natively instead of through Tseitin.
    /// A few seconds, so it stays out of the default suite.
    #[test]
    #[ignore = "seconds; run with --ignored"]
    fn semaev_s4_round_trip_n19_corpus() {
        let (n, l, irr, x_r) = corpus_n19l6();
        let b = F2mElement::one(n);
        let mut enc = encode_semaev_s4(n, l, &irr, &b, &x_r, XorEncoding::Native);
        assert!(!enc.trivially_unsat);
        enc.solver.conflict_budget = 2_000_000;
        assert_eq!(
            enc.solver.solve(),
            SolveResult::Sat,
            "corpus instance is SAT"
        );

        let xs = enc.decode();
        let (e1, e2, e3) = elementary_symmetric_3(&xs[0], &xs[1], &xs[2], &irr);
        let val = symmetrised_s4_eval(&e1, &e2, &e3, &x_r, &irr);
        assert!(
            val.is_zero(),
            "decoded decomposition must satisfy the symmetrised S₄"
        );
        // Every decoded x-coordinate must lie in the factor base.
        for x in &xs {
            assert!(
                x.degree().map_or(true, |d| d < l),
                "decoded x-coordinate escaped the l-dimensional subspace"
            );
        }
    }

    /// **The cost of Tseitin, measured.**  Same system, both encodings:
    /// native parity constraints cost no clauses at all beyond the
    /// monomial definitions.
    #[test]
    fn native_xor_is_much_smaller_than_tseitin() {
        let (n, l, irr, x_r) = corpus_n19l6();
        let b = F2mElement::one(n);
        let native = encode_semaev_s4(n, l, &irr, &b, &x_r, XorEncoding::Native);
        let cnf = encode_semaev_s4(n, l, &irr, &b, &x_r, XorEncoding::Cnf);

        let (nv, nc) = (native.solver.n_vars(), native.solver.n_clauses());
        let (cv, cc) = (cnf.solver.n_vars(), cnf.solver.n_clauses());
        assert!(
            cc > 4 * nc,
            "expected the CNF expansion to cost several times the clauses: \
             native {nv} vars / {nc} clauses vs CNF {cv} vars / {cc} clauses"
        );
        assert!(cv > nv, "the CNF path must also allocate chain auxiliaries");
        assert!(
            native.solver.n_xors() > 0,
            "native path must install XOR rows"
        );
        assert_eq!(cnf.solver.n_xors(), 0, "CNF path must install none");
    }

    /// **Sanity**: a 4-literal XOR direct encoding gives 8 clauses,
    /// half the 16 truth-table rows.
    #[test]
    fn direct_xor_emits_correct_clause_count() {
        let mut s = Solver::new(4);
        emit_direct_xor(&mut s, &[1, 2, 3, 4], false);
        assert_eq!(s.n_clauses(), 8);
    }

    /// **Round-trip on a tiny ANF system**: x ⊕ y = 0 has exactly two
    /// solutions ((0, 0) and (1, 1)).  Encoding and solving must find
    /// at least one.
    #[test]
    fn xor_only_system_is_satisfiable() {
        // F2BoolPoly: x_0 ⊕ x_1 (linear, no constant, no quadratic).
        let mut p = F2BoolPoly::zero(2);
        p.coeffs[1] = true; // x_0
        p.coeffs[2] = true; // x_1
        let enc = encode_equations(1, vec![p]);
        // n is repurposed as the "bit-half-count"; we use n=1 → num_bit_vars = 2.
        let mut solver = enc.solver;
        assert_eq!(solver.solve(), SolveResult::Sat);
        let m = solver.model();
        assert_eq!(m[0], m[1], "solution must have x_0 = x_1");
    }

    /// **End-to-end Semaev solve at `n = 4`**: encode, solve, decode,
    /// and verify `S_3(X_1, X_2, x_3) = 0` on the original binary
    /// curve.
    #[test]
    fn semaev_sat_round_trip_n4() {
        let n = 4;
        let irr = irr_for(n);
        // Use a small `b` and `x_3`, and pick `(X_1, X_2)` that we
        // *know* is on the variety: take X_1 = X_2 = x_3, which makes
        //   S_3 = (X_1 + X_2)² x_3² + X_1 X_2 x_3 + (X_1 X_2)² + b
        //       =        0       + x_3³ + x_3⁴ + b.
        // We pick b = x_3³ + x_3⁴ so that the equation vanishes.
        let x3 = F2mElement::from_bit_positions(&[0, 2], n);
        let x3_cu = x3.mul(&x3, &irr).mul(&x3, &irr);
        let x3_4 = x3_cu.mul(&x3, &irr);
        let b = x3_cu.add(&x3_4);
        // Sanity: S_3(x_3, x_3, x_3) = 0.
        let s = binary_semaev_s3(&x3, &x3, &x3, &b, &irr);
        assert!(s.is_zero(), "S_3(x_3, x_3, x_3) must vanish with our `b`");

        let mut enc = encode_semaev_s3(n, &irr, &b, &x3);
        enc.solver.conflict_budget = 100_000;
        let res = enc.solver.solve();
        assert_eq!(res, SolveResult::Sat, "SAT solver must find a solution");
        let (x1, x2) = decode_x1_x2(&enc);
        let val = binary_semaev_s3(&x1, &x2, &x3, &b, &irr);
        assert!(
            val.is_zero(),
            "decoded (X_1, X_2) must satisfy S_3 = 0; got value with {} non-zero bits",
            val.raw_bits().iter().map(|w| w.count_ones()).sum::<u32>()
        );
    }

    /// **Round-trip at `n = 5`**, previously `#[ignore]`d because the
    /// solver had to learn the parity structure by resolution.  With
    /// native XOR rows it finishes in well under a millisecond.
    #[test]
    fn semaev_sat_round_trip_n5() {
        let n = 5;
        let irr = irr_for(n);
        let x3 = F2mElement::from_bit_positions(&[1, 3], n);
        // Construct b so the symmetric solution X_1 = X_2 = x_3 is in
        // the variety.
        let x3_2 = x3.square(&irr);
        let x3_3 = x3_2.mul(&x3, &irr);
        let x3_4 = x3_3.mul(&x3, &irr);
        let b = x3_3.add(&x3_4);

        let mut enc = encode_semaev_s3(n, &irr, &b, &x3);
        enc.solver.conflict_budget = 500_000;
        let res = enc.solver.solve();
        assert_eq!(res, SolveResult::Sat);
        let (x1, x2) = decode_x1_x2(&enc);
        let val = binary_semaev_s3(&x1, &x2, &x3, &b, &irr);
        assert!(val.is_zero());
    }

    /// **Unsatisfiable case**: pick a `b` that makes the system
    /// genuinely vacuous (constant-only).  Specifically, after Weil
    /// descent we should be able to construct an inconsistent
    /// equation `1 = 0` and verify the encoder yields UNSAT.
    #[test]
    fn inconsistent_equation_yields_unsat() {
        // Forge an F2BoolPoly equal to the constant 1.
        let mut p = F2BoolPoly::zero(2);
        p.coeffs[0] = true; // constant 1
        let enc = encode_equations(1, vec![p]);
        assert!(
            enc.trivially_unsat,
            "encoder should signal trivial UNSAT for '1 = 0'"
        );
    }
}
