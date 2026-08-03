---
id: KN-FIND-ffe1df
type: internal_finding
title: "(O2) no cheap sum-compatible filter on E(F_p): the Wagner k-tree route to a sub-rho ECDLP exponent is closed for every F1 filter family except the null"
tags:
- ecdlp
- prime-field
- wagner-k-tree
- character-sums
- toy
- internal-finding
confidence: reported
internal_refs:
- RQ-ECDLP-002
proof_status: derivation
proof_refs: []
added: 2026-08-03
superseded_by: null
---

## Frontmatter note

`proof_status: derivation` and `proof_refs: []` are literal, not placeholders.
**This finding is promoted from derivations, not from any evidence record**: no
`EXP-*`, `RUN-*`, `EV-*` or `DEC-*` record exists for the (O2) line, because the
work is proof plus measurement rather than a protocolled experiment. The
`internal_refs` therefore name the goal and question this attaches to, not
evidence it was promoted from — the usual promotion chain
(`EV-* → DEC-* → KN-FIND-*`) is **absent here and that is a real gap**, not a
formatting choice. The proofs live in the artifact paths listed below.

## Artifacts

- `analysis/o2-sum-compatible-filters/` — all documents and scripts.
- Literature: [[KN-LIT-7639]] (H1, multiplicative — partly traced),
  [[KN-LIT-f6de4b]] (H1′, additive — **largely untraced**; see "What is NOT
  established" item 3, which that entry corrects downward).

## The finding

Let `E/F_p` have `#E(F_p) = N` prime. A Wagner `j`-level k-tree over `E(F_p)`
needs a cheaply computable filter `h : E(F_p) → [M]` with alphabet
`M ≈ N^{1/(j+1)}` whose agreement `eps = Pr[h(P+Q) = f(h(P),h(Q))]` beats `1/M`
by a growing factor. **No such filter exists in any algebraically structured
family**, and consequently no configuration `j >= 2` moves the ECDLP exponent
below Pollard rho's `1/2` by this route.

### Coverage

| filter family (F1 taxonomy) | status | route |
|---|---|---|
| C, D, E, F, G — characters, residues, 2-descent, subgroup projections | closed | Theorem A + Weil (multiplicative) |
| A, B, I, J — intervals, bit windows, congruences, popcount, `y`-sign | closed | Theorem A + Weil (additive completion) |
| quasigroup combining rules | closed **exactly**; unrealized approximately | Theorem C |
| H — SHA-256 | not covered, and irrelevant | the in-arm null, outside any algebraic class by construction |

| `j` | needed `M` | exponent (`m=16`) | status |
|---|---|---|---|
| 2 | `p^{1/3}` | 0.4167 | **closed** |
| 3 | `p^{1/4}` | 0.3750 | **closed** |
| 4 | `p^{1/5}` | 0.4000 | **closed** |

## The three results it rests on

**Theorem A** (`O2_fourier_obstruction.md`). For affine/group-law `f`, an exact
Fourier identity gives `eps <= 1/M + max_{t≠0}|T_t|`, with **no factor `M`**,
where `T_t = E_{P,Q}[g_t(P)g_t(Q)conj(g_t(P+Q))]` and `g_t = e(t·h/M)`. Verified
to `1e-15` on 18/18 configurations by exhaustive enumeration.

**The composition** (`O2_composition_closure.md`). The Weil/Bombieri bound
`|T_t| = O(D·p^{-1/2})` substituted into Theorem A rather than into the
`M`-lossy `(★)` moves closure from `M <= p^{1/4}` to `M <= p^{1/2-o(1)}`, which
covers `j = 2`. The operative point: Wagner's k-tree merges on a **quotient
homomorphism**, so its combining rule is the group law, and the group-law branch
— not the adversarial one — governs.

**Theorem C** (`O2_quasigroup_gap.md`). A tree must invert `f` in each argument
to index buckets, so `f` is a quasigroup. Exact sum-compatibility plus
associativity of `+` on `E` forces `f` associative; an associative quasigroup is
a group; so `h` is a surjective homomorphism `E(F_p) → ([M],f)`, impossible for
`N` prime and `M < N`. Four lines, no character-sum input, no restriction on `h`.

**Additive completion** (`O2_additive_completion.md`). For families A/B/I/J the
same fibred argument runs with additive characters. Degeneracy is *easier*: if
`F_R = g^p − g + c` every pole order is divisible by `p`, but `x(·)` and
`x(R−·)` have double poles at distinct places for `R ≠ O`, so with `p > 2` the
exceptional set is the **single point** `R = O` with `α+β = 0`.

## Why this is a barrier result and not an attack

`sota_delta = 0` on time, memory and data/queries. `dominated_by` inapplicable
rather than `null`. No solve, relation, or speedup is claimed;
`certificate.kind: none`. The value is **negative information that redirects
search**: it retires the last exponent-moving configuration the campaign had
identified, so effort should move off the sum-compatible-filter lane entirely.

## Independence of the derivations

Two of the underlying documents (`O2_derivation_attempt.md`,
`O2_fourier_obstruction.md`) were produced in **separate parallel sessions from
the same parent commit `ee16c4a96`, neither seeing the other**. They agree
numerically to 3–4 decimals on shared quantities and hit the same `M²`
Cauchy–Schwarz barrier from opposite directions. **Both resolved to
`claude-opus-5`**, so this is procedural independence, not model independence,
and is evidence about the derivations rather than about the backend.

## What is NOT established

1. **Approximate quasigroup combining.** Theorem C covers the exact case only.
   Sampling (Jacobson–Matthews, all Latin squares at `M <= 5`, uniform samples to
   `M = 32`) finds the excess *decreasing*, and the **exact** worst case over all
   `f` stays ~160× below the `(★)` ceiling — but no robust Theorem C is proved.
2. **Arbitrary cheap `h`.** Proposition 2 of `O2_derivation_attempt.md` proves no
   group-theoretic argument can reach it: the dlog-interval pullback achieves
   `eps ≈ 1/2` at arbitrarily large `M` on every prime-order group. Only a
   definitional cost restriction closes this, and the cost clause is **not a
   theorem**.
3. **Literature hypotheses.** (H1) multiplicative Weil/Bombieri on a curve is
   only partly traced — see [[KN-LIT-7639]]; its form, non-degeneracy hypothesis
   and validity regime (`g << √q`, here `g = 1`) are confirmed, the explicit
   `(2g−2+2m)` constant and general `k > 2` on curves are not. (H1′) the
   *additive* case is better attested but has **no `KN-LIT` entry yet** — one is
   owed.
4. **Constants** are not carried out anywhere in this line.
5. **Toy scale.** All computation is `N <= 65539`. Under `AGENTS.md` rule 4 this
   is not crypto-scale validation. The theorems are asymptotic; the computations
   check their steps and their `p`-dependence over ~3 orders of magnitude.

## Promotion-gate status

This entry records **proved statements and measured scaling**, not an
asymptotic-complexity claim advancing toward `supported`. The four gates of
`/coordinate-research-goal` are therefore **not applicable** — no cost model, no
concrete-cost table, and no heuristic-validation experiment is claimed or owed.
Independent review has **not** been performed: no Validator or Red Team pass
exists on any of these documents. `status: established_scoped` reflects proof
plus measurement, not adjudication.

## Provenance note (recorded against interest)

[[KN-LIT-7639]] was minted **sequentially** as max+1, which `CLAUDE.md` names as
the collision bug — the same mechanism that forked `GOAL-ECDLP-001` across
`BATCH-025..028`. It is merged and immutable, and a rename would break its
archive, so it stands. This entry uses a random 6-hex suffix as the convention
requires.
