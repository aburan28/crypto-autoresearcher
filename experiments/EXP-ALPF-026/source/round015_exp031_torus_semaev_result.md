# EXP-031 — Torus-based Semaev Index Calculus (H-TS-001)

Round 15. Last genuinely-novel algebra lever in the named queue.
Toy-scale, model-bound. NO break claim, NO cryptographic-size claim.

## 1. Idea and expected null

Granger–Vercauteren algebraic-tori IC obtains LOW-degree summation relations
by decomposing inside an algebraic torus's MULTIPLICATIVE group law (which is
low-degree in a rational parametrization) instead of the EC chord–tangent law
(whose Semaev/Gröbner solving degree blows up as ~`4^(m-1)`).

EXPECTED NULL (stated up front): the torus does give a genuine LOW-degree
summation relation (the GV win), BUT it solves a finite-field DLP in
`F_{p^2}^*` that does NOT descend to the prime-field EC DLP, because the
torus connects to the EC group only via a pairing of embedding degree 2
(MOV/Frey–Rück), which a P-256-like curve is chosen to avoid. Predicted
verdict: FAILED for the EC target (low torus degree, wrong problem).

## 2. Torus construction and rational parametrization

- `T_2(F_p) = ker(Norm: F_{p^2}^* -> F_p^*)`, the norm-1 subgroup, order `p+1`.
- `F_{p^2} = F_p(s)` with `s^2 = d`, `d` a fixed non-square in `F_p`.
- Parametrization `psi: A^1 \ {±s} -> T_2`, `psi(t) = (t + s)/(t - s)`.
  Norm check: `N(psi(t)) = psi(t) * psi(t)^p = ((t+s)/(t-s))((t-s)/(t+s)) = 1`,
  so `psi(t) ∈ T_2` for every `t` with `t^2 ≠ d`. This is the standard
  degree-1 (birational) parametrization of the Pell conic / norm-1 torus.
- Group law in parameter coordinates (Pell/Chebyshev composition):
  `psi(t1)·psi(t2) = psi(t3)` with `t3 = (t1·t2 + d)/(t1 + t2)`.
  Equivalently a Möbius action with matrix `M(u) = [[u, d],[1, u]]`; the
  m-fold product is `∏ M(u_i)`, whose entries are per-variable degree 1.

## 3. Summation system and degree comparison

The m-fold torus summation (product) relation "decompose target `psi(T)` as
a product of factor-base elements `psi(u_1)…psi(u_m)`" is read off from
`∏_{i=1}^m M(u_i)` versus the target:
`rel1 = M[0,0] - T·M[1,0] = 0`, `rel2 = M[0,1] - T·M[1,1] = 0`.

| quantity | torus T_2 (this exp) | EC Semaev (baseline) |
|---|---|---|
| addition law in coords | `t3=(t1 t2 + d)/(t1+t2)` BILINEAR | chord–tangent, rational deg 2 |
| per-variable degree of relation | **1** (each `u_i` linear in `∏M`) | 2 in each `x_i` for `S_m` |
| Gröbner solving blow-up | none (bilinear/linear-algebra) | ~`4^(m-1)` (well-documented) |

This is the GV win in clean form: per-variable degree 1 vs EC's `4^(m-1)`
solving blow-up. (Exact measured `torus_summation_per_var_degree`,
`torus_addition_law_verified`, and total degrees are in the JSON
`degree_compare` block produced by the run.)

## 4. Anti-circularity

The relations are derived PURELY from the `F_{p^2}^*` norm-1 subgroup law via
`M(u)=[[u,d],[1,u]]` and `psi(t)=(t+s)/(t-s)`. No EC point coordinates, no EC
addition formula, and no Semaev `S_m` polynomial enter the construction. The
per-variable degree (1, bilinear) is structurally incompatible with EC Semaev
(`4^(m-1)` blow-up). Therefore this is NOT an EC-Semaev relabel — it is a
genuinely different (torus multiplicative) algebra. PASS.

## 5. Gated-meter (round007 hardened meter, 4-fixture self-validation)

Meter loaded from
`/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round007_exp012_localization_gate.sage`.
Inline self-validation required on POS-A (fires, d_ff<7, gate_meaningful),
NEG-1 (quiet), e-ring m=3 Semaev (base-fires but gate FAILS — artifact),
POS-C Weil S_3 (gate PASSES). If any fixture is wrong the verdict is forced
INCONCLUSIVE. The meter is then run on the torus summation system; measured
`d_ff / D_reg / fires / gate_passes / gate_meaningful` are in the JSON
`gate_runs` block. NOTE: because the torus relations are bilinear, the meter
operates in a regime where any "fall" reflects ordinary linear-algebra
collapse, not an EC-Semaev-style nontrivial syzygy on summation leading
forms; a fire here is NOT evidence for the prime-field EC target.

## 6. EC-descent / embedding-degree analysis (DECISIVE)

`T_2(F_p)` is a subgroup of `F_{p^2}^*`. A DLP in `F_{p^2}^*` (or in `T_2`)
corresponds to the prime-field EC DLP ONLY when the EC group `E(F_p)` embeds
into `F_{p^2}^*` via a bilinear pairing — i.e. exactly when the EMBEDDING
DEGREE is `k = 2` (the MOV / Frey–Rück condition: `n | p^2 - 1`, `n` the
EC subgroup order). For P-256-like curves the embedding degree is huge
(generically `~n`), so `E(F_p)` does NOT sit inside `F_{p^2}^*` and the torus
DLP has no map to the EC scalar `k`.

The experiment builds random near-/prime-order toy curves over each `F_p`,
reports `order`, factorization, largest prime factor `ell`, and the
embedding degree `k = ord_ell(p)`. The descent test is `k == 2`. Measured
values per `p` are in the JSON `ec_descent` block (`embedding_degree_k`,
`torus_DLP_descends_to_EC`, `descent_reasoning`). For generic P-256-like toy
curves the expectation is `k >> 2` and `torus_DLP_descends_to_EC = False`.

## 7. Verdict

`verdict = failed` for the prime-field EC target (unless the run found a
generic P-256-like curve with `k == 2`, which would be flagged LOUDLY as a
CANDIDATE — not expected).

NEGATIVE RESULT (scoped): The algebraic-tori construction yields a genuinely
LOW-degree (per-variable degree 1, bilinear) summation relation — reproducing
the Granger–Vercauteren advantage — but the relation lives in `T_2(F_p) ⊂
F_{p^2}^*` and solves a finite-field DLP that does NOT descend to the
prime-field EC DLP, because P-256-like curves have embedding degree `≠ 2`
(no MOV/Frey–Rück pairing into `F_{p^2}^*`). Low torus degree, WRONG problem.
This is the clean articulation of why algebraic-tori IC does not transfer to
prime-field ECDLP.

This does NOT rule out: tori of higher dimension `T_n` for curves whose
groups embed at small `k`; supersingular / pairing-friendly families (where
`k` is small by design — but those are not the prime-field hardness target);
or a hypothetical map other than a pairing tying `E(F_p)` to a torus DLP
(none known).

## 8. Next

- Conservative: confirm the `k != 2` barrier on a 3rd size (e.g. `p=2053`)
  to make the descent obstruction a clean ≥3-size statement.
- Representation-changing: ask whether ANY low-degree decomposable group
  receiving a CHEAP map from `E(F_p)` exists for large-embedding-degree
  curves — formalize as "a degree-low composable target reachable by a
  morphism of bounded degree from E(F_p)"; the pairing is the only known
  such map and it forces small `k`.
- High-risk: search for a non-pairing correspondence (isogeny/Weil-cohomology
  transfer) carrying the EC scalar into a torus DLP without the `k=2`
  embedding constraint; minimal test = does any degree-bounded rational map
  `E -> T_n` over `F_p` preserve the discrete log? (almost certainly no —
  group-scheme morphism rigidity — but it formalizes the obstruction).

## Artifacts

- `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp031_torus_semaev.sage`
- `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp031_torus_semaev.log`
- `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp031_torus_semaev_result.json`
- `/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp031_torus_semaev_result.md`
