---
id: KN-FIND-61347e
type: internal_finding
title: "Cross-genus Poincare-factor embedding cannot beat Pollard rho on the embedded elliptic factor (Hasse-Weil order-inflation closure)"
tags: [isogeny, jacobian, genus-g, index-calculus, hasse-weil, tate, ecdlp, prime-field, closure, rq-crypto-001]
confidence: strong
internal_refs: [DEC-20260902-4c82fd, DEC-20260901-d599ae]
knowledge_refs: [KN-OPEN-de67f0, KN-OPEN-2f5e66]
proof_status: derivation
proof_refs: []
added: 2026-09-02
superseded_by: null
---

## Finding

Let `E/F_p` be an ordinary elliptic curve with prime subgroup order
`N = #E(F_p)`. Suppose `E` is realised, by ANY explicit construction
(gluing along compatible torsion per Kani–Rosen, or any other method), as a
Poincaré/isogeny factor over `F_p` of the Jacobian of a smooth genus-`g`
curve `C/F_p`, `g >= 2`, so `Jac(C)` is `F_p`-isogenous to `E x A` for a
complementary abelian variety `A/F_p` of dimension `g - 1`. Then:

1. **The complementary factor is forced, unconditionally.** By Tate's
   isogeny theorem (1966), isogenous abelian varieties over `F_p` have
   identical characteristic polynomials of Frobenius; since the
   characteristic polynomial of a product is the product of the factors',
   `#Jac(C)(F_p) = N * #A(F_p)` **exactly** (not an estimate). Combined with
   the Hasse–Weil bound `#Jac(C)(F_p) = Theta(p^g)` and Hasse's bound
   `N = Theta(p)` for `E`, this gives `#A(F_p) = Theta(N^{g-1})` for
   **every** honest `F_p`-rational embedding — no construction can make the
   complementary factor small.
2. **Every genus-`g` index-calculus attack through this embedding is
   strictly worse than direct rho.** The best published genus-`g`
   hyperelliptic/plane-curve index-calculus family (Gaudry, EUROCRYPT 2000,
   at `g=2`; the Gaudry–Thomé–Thériault–Diem double-large-prime family for
   general `g`) costs `Otilde(p^{2-2/g}) = Otilde(N^{2-2/g})` on the full
   ambient Jacobian. The exponent `2-2/g` is monotonically increasing in
   `g >= 2`, with minimum value **1** at `g=2` — already strictly worse than
   direct Pollard rho's `Otilde(N^{1/2})` by a full exponent factor of 2,
   for every `g >= 2`.

**This closure is robust even to an unverified citation.** It holds using
only the well-established, uncontroversial `g=2` case (Gaudry's own
published result: genus-2 index calculus is `Otilde(p)`, no better than
generic on the Jacobian) — the general-`g` Gaudry–Thomé–Thériault–Diem
exponent formula, checked by the producing session only at WebSearch-snippet
depth, is not load-bearing for the qualitative conclusion, since the
exponent's monotonicity in `g` means `g=2` is already the attacker's best
case among `g >= 2`.

## What was checked (proves-too-much control)

The identical cost formula, applied instead to the **ambient** Jacobian's
own discrete log (not the extracted `E`-factor), correctly reproduces the
genuine, independently well-known **positive** result: at `g >= 3`,
`Otilde(N^{2-2/g})` (e.g. `N^{4/3}` at `g=3`) **is** strictly better than
generic on the ambient group (`Otilde(N^{g/2})`, e.g. `N^{1.5}` at `g=3`).
The argument does not, and must not, negate this known-true case — the
`N^{g-1}` inflation applies only to the extracted-factor reading, and the
producing session's own control checked this explicitly.

## What this does NOT establish

- **Not a general impossibility.** The closure applies only to the STATED
  algorithm family (Gaudry / Gaudry–Thomé–Thériault–Diem genus-`g` index
  calculus applied to the full ambient Jacobian, then projected). It does
  NOT certify that no different algorithm exploiting the embedding could do
  better (a "factor-restricted" or "relative" index calculus, explicitly
  named as an open forward direction — see below).
- **Not a claim about the embedding's construction cost**, which is not
  charged anywhere in this argument (the closure holds even if the
  embedding were handed over for free — a lower bound on the attack's cost
  from the index-calculus stage alone).
- **Not a claim about hybrid constructions** that use the embedding for
  some other purpose (a distinguisher, a re-randomization device, a partial
  relation source combined with a different collection method).
- **Not verified against the full Gaudry–Thomé–Thériault–Diem paper** (only
  a WebSearch-snippet-depth citation of eprint 2004/153); this does not
  affect the closure's qualitative conclusion (see above) but should be
  discharged before citing the exact general-`g` exponent formula elsewhere.

## Forward guidance

A single genuinely different "factor-restricted" index-calculus algorithm
that solves DLP on a genus-`g` Jacobian using work scaling with the embedded
factor's own size `N` rather than the full ambient order `N * #A(F_p)`
would reopen this entire line. No such algorithm is known to this program's
corpus as of this finding.

## Provenance

- `coordination/goals/GOAL-ECDLP-001/proposals/B71-CRYPTO001-NEW-MECHANISM-20260902-2fb7f8/tasks/TASK-20260902-2fb7f8/candidate-mechanisms.yaml` (internal — CAND-1's full derivation, citations, and controls)
- `coordination/goals/GOAL-ECDLP-001/proposals/B71-CRYPTO001-NEW-MECHANISM-20260902-2fb7f8/tasks/TASK-20260902-2fb7f8/proof-search-map.yaml` (internal — the four-audit application, including the nearby-object/proves-too-much control)
- `ledger/decisions/DEC-20260902-4c82fd.yaml` (internal — this finding's promoting decision, including the Coordinator's independent robustness argument via the g=2-alone case)
- `ledger/decisions/DEC-20260901-d599ae.yaml` (internal — the rerank decision commissioning this ideation round)
- Tate, J., "Endomorphisms of abelian varieties over finite fields," Invent. Math. 2 (1966), 134–144 (recalled — classical, standard reference for the isogeny theorem)
- Weil / Hasse–Weil bound for curves (recalled — classical)
- Gaudry, P., "An algorithm for solving the discrete log problem on hyperelliptic curves," EUROCRYPT 2000 (recalled — the load-bearing g=2 baseline this finding's robustness rests on)
- Gaudry, Thomé, Thériault, Diem, "A double large prime variation for small genus hyperelliptic index calculus," Math. Comp. 76 (2007); eprint.iacr.org/2004/153 (retrieved at WebSearch-snippet depth only — not load-bearing for this finding's qualitative conclusion, per the g=2-alone robustness argument above)
- Kani, E. and Rosen, M., "Idempotent relations and factors of Jacobians," Math. Ann. 284 (1989), 307–327 (recalled — the explicit gluing construction cited as an example embedding)
