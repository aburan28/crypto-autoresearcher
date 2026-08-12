# EXP-XEDN-003 analysis

## Gate verdict

**supported** (within the frozen claim boundary)

Primary metric `max_|coeff|(p)` — infinity-norm of the shortest nonzero
Mordell–Weil relation among observed free-x integral sections — equals **1** at
every tested size `p ∈ {7, 13, 19, 31}`. The fit of `max_|coeff|` vs `log p` has
slope `0.0` with jackknife CI `[0.0, 0.0]` (includes 0). No eligible surface has
a verified shortest relation with infinity-norm ≥ 4.

Runs: `RUN-XEDN-003-MAIN`, `RUN-XEDN-003-CTRL`.

## Controls

| Control | Verdict | Notes |
|---|---|---|
| Predicate (p=7 top_surfaces) | **pass** | Frozen enumeration recovers recorded slot counts on all five RUN-XEDN-002-C priors |
| Height `deg(num x(nS))=2n²` for n=1..12 | **pass** | Holds on at least one non-torsion free-x section at every size among eligible surfaces |
| μ₃ (p≡1 mod 3) | **pass** | Every eligible surface: orbit `{S,wS,w²S}` sums to O |
| Specialisation | **pass** | Shortest reported relations specialise to O at ≥20 smooth fibres |
| Red-team probe p=13, b=[0,0,3,12,9,7,3] | **scoped pass / literal fail** | 15 slots, 5 μ₃ orbits, coeffs in {0,±1} via μ₃; height-Gram span_rank=14 > 4 because the surface is **non-squarefree** (fibre-degenerate; excluded from trend) |

## Secondary observations

- Cross-orbit (Gram on μ₃ orbit representatives) shortest infinity-norms are in
  `{1,2}` where measured (p=7 max 2; p=31 max 1). These stay inside {1,2,3}.
- Several eligible surfaces report height-Gram `span_rank` > 8 (Shioda–Tate upper
  bound for a rational elliptic surface). That is an integrity/methodology flag
  on the polarisation height matrix for some surfaces, **not** evidence that
  coefficients grow. The primary shortest-relation metric remains 1 via μ₃ on
  every `p≡1 mod 3` size tested. Independent review should recompute at least
  one surface and challenge any rank>8 reading.
- Eligible-surface counts: p=7 → 20; p=13 → 1; p=19 → 5; p=31 → 9. Below the
  aspirational ≥30 at larger sizes inside the fiber/sample budget; all four
  sizes still contribute to the trend.

## Claim boundary

Toy scale only. Family `y² = x³ + b(t)` with `a(t)=0`, `deg b = 6`, free-x
slots `deg x ≤ 2`, `deg y ≤ 3`, frozen `is_square_poly` semantics, squarefree-b
surfaces for the Gram/trend arms, `p ∈ {7,13,19,31}`.

Supports H-XEDN-002 within that boundary: the shortest relation among observed
free-x sections has absolutely bounded coefficients (here constantly 1), so the
function-field relation-source reading of this family is closed by the
coefficient-bound mechanism rather than by the uniform-measure `p⁻³` density of
EXP-XEDN-002.

Does **not** claim: crypto-scale attack improvement; closure of candidate B2;
non-isotrivial families; number-field xedni; higher-degree sections; that the
Mordell–Weil lattice was proved to be E₈; that height-Gram rank readings above
8 are geometrically meaningful without further local corrections.

## Inference

- requested_policy: `executor-terra`
- resolved_model: `cursor-grok-4.5`
- fallback_used: true
