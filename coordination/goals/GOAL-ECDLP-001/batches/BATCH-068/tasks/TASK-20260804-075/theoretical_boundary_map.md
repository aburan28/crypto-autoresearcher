# GOAL-ECDLP-001 Theoretical Boundary Map
# BATCH-068 Synthesis — 2026-08-04

## Statement of the problem

Find an algorithm that solves prime-field ECDLP (given G ∈ E(F_p) of prime order N
and Q = [k]G, find k) in expected time o(N^{1/2}) (beating Pollard rho).

## Systematic closure map (BATCH-001 through BATCH-068)

### Proved closures (theorem-backed)

| Direction | Obstruction | Record |
|-----------|-------------|--------|
| NCP (noncommutative path algebra) | Commutator collapse: every target-reaching word abelianizes to a commutative relation | H-NCP-001 rejected_scoped, DEC-20260724-011 |
| TTN (tensor-train bond ranks) | Bond ranks near full (near-maximal chi); no sub-exponential tensor compression | H-TTN-001 rejected_scoped |
| TRA (transfer operator spectral) | L=O(1): character orthogonality forces localization O(1) at all coarse-graining levels | H-TRA-001 rejected_scoped |
| BKK super-heuristic | Newton saturation: MV = box Bezout at all m (H-BKKMV-001 supported as theorem at m≤5) | DEC-20260724-009 |
| Algebraic factor base (Bezout no-go) | Bezout theorem: |F_p| ≤ 3d for degree-d predicate; fixed d → O(1) factor base | IDEA-20260801-021 derivation receipt |
| Semaev monodromy exceptional locus | Galois group = C_2^{m-2} universally; no exceptional locus; no curve-dependent extra yield | BATCH-061 monodromy analysis |
| GGM oracle C+D (incidence/endomorphism) | GGM-simulable; Shoup lower bound applies; closed at exponent 1/2 by theorem | EV-GGM-79e710, DEC-20260804-3b4258 |
| BGS spectral gap | E(F_p) ≅ Z/N abelian; BGS requires non-abelian; spectral gap Θ(1/N^2) → 0 | DEC-20260804-f320c2 |
| SVP superlattice (Gao-Feng-Hu transfer) | Explicit-lattice obstruction: DLP lattice uncontructible without k | BATCH-065 analysis |
| Ordinary isogeny ECDLP (all variants) | Scalar-domain mismatch: k ∈ Z/N (order p) vs isogeny structures of order sqrt(p) | DEC-20260804-fec1e8 (SG-ECDLP-002 paused) |

### Empirical closures (toy-scale, no theorem)

| Direction | Observation | Record |
|-----------|-------------|--------|
| Semaev m=2 yield | Actual yield ≤ heuristic B^2/(2N), converges to heuristic from below | EV-YIELD-e1adbf |
| Semaev m=3 yield | Actual yield ≤ heuristic B^3/(6N), no super-heuristic signal | EV-YIELD-ca4b02 |
| Elkies ell≤23 isogeny augmentation | Augmentation ratio ≈ null-map (random bijection), no structural advantage | EV-ICI-0bdaaa |
| OIFP MITM constant C | C ≈ 40-260 (volcano slow mixing); C scaling with p unknown | EV-OIFP-97e46d, EV-OIFP-105ac9 |

### Weakened (evidence against, not fully closed)

| Hypothesis | Evidence | Record |
|------------|----------|--------|
| H-IT-001 (ordinary isogeny to anomalous/MOV) | Tate theorem: trace preserved; rho_special=0 proved | DEC-20260804-2fae6a |
| H-ICI-063e91 (Elkies ell≤23 augmentation) | Empirical falsification at m=2-3, toy scale | DEC-20260804-d0c452 |
| H-STR-002 (phi_alpha density) | Weakened by earlier batches | DEC-20260727-009 |

### GGM non-simulable but no advantage

| Oracle | Status |
|--------|--------|
| First-jet (dual-number) | NON-SIMULABLE, privately computable (= DLP oracle); no public advantage |
| Elliptic net (Somos) | NON-SIMULABLE, no k-recovery below standard DLP; no public advantage |

## The remaining gap

### The arithmetic factor base gap (open)

The Semaev index calculus uses factor base F = {P ∈ E(F_p) : x(P) < threshold}
(arithmetic, not algebraic). The BEZOUT NO-GO does NOT apply (arithmetic ≠ algebraic).
The empirical evidence shows yield ≈ heuristic B^m/(m!N), which gives the known
subexponential (but NOT sub-rho) complexity exp(c*sqrt(log N * log log N)).

No THEOREM has been proved bounding yield ≤ B^m/(m!N) + small_error. The Weil bound
approach is blocked by DL circularity (BATCH-067).

### H-PSEUDO: the breakthrough condition

Any proof that Semaev yield ≤ B^m/(m!N) * (1 + epsilon) requires:

H-PSEUDO: For F = small-x factor base with |F| = B, the character sum
|Σ_{P ∈ F} e^{2πi k*DL(P)/N}| ≤ C * sqrt(B) for all k ≠ 0.

A proof of H-PSEUDO would:
1. Close the arithmetic factor base gap (completing the algebraic + arithmetic no-go)
2. Rigorously bound the Semaev index calculus complexity
3. Constitute a significant contribution to the theory of ECDLP hardness

H-PSEUDO cannot be proved by current techniques (classical exponential sum machinery
cannot bound sums involving DL(P) without circular assumptions). It requires a new
technique for the distribution of ECDLP solutions for structured inputs.

## Structural ingredients still missing for a sub-rho ALGORITHM

For a sub-rho prime-field ECDLP algorithm, the program would need:

1. **New structural theorem**: bound some "minimal quantity" related to the DLP
   to o(N^{1/2}). Every candidate (Semaev degree, lattice shortest vector,
   conductor, OIFP MITM constant) hits Θ(N^{1/2}).

2. **Publicly computable non-simulable oracle**: encodes k-dependent information
   computable from (E, G, Q) without knowing k. All candidates either require k
   (privately computable) or are GGM-simulable.

3. **New factor-base type**: neither algebraic (Bezout-bounded) nor arithmetic
   (Semaev heuristic-bounded). No such type has been identified.

## Assessment

After 68 batches: the program has NOT found a sub-rho prime-field ECDLP algorithm
and has systematically closed every examined direction. The remaining gap (H-PSEUDO
and the related proof of ECDLP hardness aspects) is precisely the same difficulty
as proving the hardness of ECDLP itself. This is not an algorithmic failure; it is
an accurate characterization of the problem's difficulty.

GOAL-ECDLP-001 remains ACTIVE. The three remaining concrete open directions are:
1. H-PSEUDO: prove or disprove the character sum bound for structured point sets
2. OIFP MITM: determine whether the constant C = O(1) or grows with p
3. External literature survey: 2024-2026 arXiv/ePrint for new structural results
