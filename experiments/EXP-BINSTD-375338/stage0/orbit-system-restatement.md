# Orbit-system restatement (Stage 0) — EXP-BINSTD-375338

Task `TASK-20261001-ff051b`. Observations/documentation only. No attack claim.
No per-instance CNF-XOR leaf-count / division-by-mu claim.

## Source reading (a77711 Lemmas A1/A2 at q=2)

IDEA-20260906-a77711 states that absolute Frobenius σ (coordinate-wise
squaring at q=2) is an **equivariance between conjugate targets**, not a
symmetry of a single fixed-target Semaev instance:

- **Lemma A1 (equivariance):** σ maps the solution ideal / decomposition set
  I_R of target R to I_{σR}. Equivalently, if (x₁,…,x_m) decomposes R then
  (x₁²,…,x_m²) decomposes σ(R) = (x_R², y_R²) as points on a Koblitz curve.
- **Lemma A2 (disjointness):** for R ∈ G \ {O} with σR ≠ ±R,
  V(I_R) ∩ V(I_{σR}) = ∅ — a shifted tuple does **not** solve the same
  instance.

Consequently the correct algebraic object is the **orbit system** bundling
the n conjugate instances {I_R, I_{σR}, …, I_{σ^{n-1}R}} together with the
orbit of the target. A per-instance "shift-canonical" constraint that keeps
only one representative of a Frobenius orbit inside a **single** I_R is
**unsound**: it deletes solutions that belong to conjugate instances.

## HOLD-R absorption (IDEA-20260922-7ab503 review)

analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-7ab503.yaml
(verdict defective / HOLD-R) requires:

1. Primary claim = equivariance (A1/A2), **not** source IDEA claim (A)/(D)
   leaf-ratio ~1/μ on one CNF-XOR instance.
2. K-163 and ECC2K-130 are **STRUCTURALLY EMPTY** for useful mid-dimension
   Frobenius-stable V (ord₁₆₃(2)=162, ord₁₃₁(2)=130); live rows route to FROB.
3. Parser `(0xHEX)` regression is already fixed on the current tree — Stage 0
   records a fixture only.
4. Named toys BIN-TOY-K19 / BIN-TOY-K17-STABLE; RC-1 null; Z/ℓ replica.

## What Stage 1 measures (authorized)

On BIN-TOY-K19 (non-stable poly window, same emptiness pattern as ECC2K-130):

- (a) same_instance_hits — predict 0
- (b) conjugate_instance_hits — predict 1.0 (as points); in-V fraction near 0
- (c) leg-swap control — predict 1.0
- (d) Z/ℓ scalar replica — statistics must match
- (e) solutions_lost under per-instance orbit-canonical constraint — predict >0
  with median fraction near (1 − 1/n)

Stable-V positive control at n=17; NULL-RC1 not-on-curve control.

`orbit_system_restatement_complete: true`
`per_instance_leaf_ratio_authorized: false`
