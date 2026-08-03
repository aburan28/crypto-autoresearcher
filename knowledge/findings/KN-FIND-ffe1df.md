---
id: KN-FIND-ffe1df
type: internal_finding
title: "(O2) no cheap sum-compatible filter on E(F_p): the Wagner level-1 filtering gain is p^o(1) for the algebraic character families and for x-based interval/bit-window filters"
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

## Independent validation — verdict `failed` (VAL-20260803-3b7c1a)

An independent Validator pass (`analysis/o2-sum-compatible-filters/reviews/VALIDATION.md`)
returned **`failed`** on the artifacts as committed, with five confirmed errors.
Every claim below is stated **after** that review and is narrowed by it. The
five, recorded here because this entry is what survives:

1. **Theorem A's printed identity is wrong** — a conjugate is missing; the
   correct form is `Σ_ξ conj(ĝ_t(ξ))|ĝ_t(ξ)|²`. The **bound is valid** and "no
   factor `M`" is correct. The "18/18 verified to `1e-15`" check **could not
   have caught this**: it exercises only `d = 0`, where both forms agree because
   the total is real.
2. **The composition's substitution is invalid as written** — (A) is stated with
   `Λ` while the Weil bound governs `|T̂_ψ|`, and `|T_t| <= Λ` is one-way
   (measured gap **262×** at `p = 32779`). The repair is free: use
   **(A′) `eps <= 1/M + max_{t≠0}|T_t|`**, the identity *before* Parseval. The
   conclusion survives; the empirical arm was conservative in the right
   direction. This entry cites A′ throughout.
3. **The additive assembly is false as quantified** — at `(α,β) = (0,0)`,
   `S = 1` exactly, so `max|S| = O(p^{-1/2})` fails and the assembled bound is
   vacuous without an unstated balance hypothesis on `|c_0^{(t)}|` (measured
   `<= 0.003` for `x`-filters but **0.999 for popcount**).
4. **The claimed class ≠ the claimed families** — see the coverage table.
5. **`(eps_quasi − 1/M)/Λ <= 0.17` "over all filters, primes and `M`" is false**;
   the true maximum is **0.322**, and this entry's own source table showed
   `0.278`. `0.17` holds only over `x mod M` and `char`. The qualitative
   conclusion — never approaching `M` — is unaffected.

The Validator independently **confirmed** Theorem C in full, including the case
this entry did not check (non-surjective `h`: the argument runs on `im(h)`,
giving `M_eff | N`), and confirmed the degeneracy lemma's pole-order core, that
2-torsion `R` is not special, and that all six scripts reproduce every quoted
table digit-for-digit.

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
| C, E, F, G — quadratic characters, rational-function coords, 2-descent, subgroup projections | closed at level 1 | Theorem A′ + Weil (multiplicative) |
| **D — cubic/quartic/octic residue characters (`k = 3,4,8`)** | **NOT closed** | needs general `k > 2` on a genus-1 curve, which [[KN-LIT-7639]] explicitly does **not** cover |
| A, B — **`x`-based** intervals and bit windows only | closed at level 1, conditional on (H1′) | Theorem A′ + additive completion |
| **A, B — `y`-based, joint `(x,y)`, and nonlinear members** (`x±y`, `xy`, `x⊕y`, `x^{-1}`) | **NOT closed** | outside §2.2's expansion; never measured |
| **I — popcount, digit sums** | **NOT closed** | not `O(1)` intervals and not an AP; measured L¹ grows `~p^{0.39}`, not `O(log p)` |
| **J — `y`-sign** | **NOT closed** | not a function of `x` at all, so the expansion never starts |
| quasigroup combining rules | closed **exactly**; unrealized approximately | Theorem C |
| H — SHA-256 | not covered, and irrelevant | the in-arm null, outside any algebraic class by construction |

| `j` | needed `M` | exponent (`m=16`) | status |
|---|---|---|---|
| 2 | `p^{1/3}` | 0.4167 | level-1 gain is `p^{o(1)}` |
| 3 | `p^{1/4}` | 0.3750 | level-1 gain is `p^{o(1)}` |
| 4 | `p^{1/5}` | 0.4000 | level-1 gain is `p^{o(1)}` |

**"Level-1", not "closed" — this is a correction forced by validation.**
Theorem A′ is proved for **uniform independent `P,Q`**, which is the tree's
*first* merge only. At levels `>= 2` the inputs are conditioned on having matched
at the previous level and are no longer uniform or independent, so the bound does
not transfer as stated. `O2_fourier_obstruction.md` §7 recorded this as its
limitation 4; **the composition and the first version of this entry both dropped
it silently while asserting "every configuration `j >= 2` is closed."**

There is a plausible repair — a tree whose first merge yields no filtering gain
cannot bootstrap the later ones, so level 1 should suffice to close the
configuration — but **that argument has not been written down or checked, and it
is not assumed here.** Until it is, the honest scope is: *the level-1 filtering
gain is `p^{o(1)}` for the covered families*, which is strong evidence against
these configurations and is **not** a proof that the trees are closed.

## The three results it rests on

**Theorem A′** (`O2_fourier_obstruction.md`, as corrected by validation). For
affine/group-law `f` and **uniform independent `P,Q`**, `eps <= 1/M +
max_{t≠0}|T_t|` with **no factor `M`**, where
`T_t = E_{P,Q}[g_t(P)g_t(Q)conj(g_t(P+Q))]` and `g_t = e(t·h/M)`. The bound is
validated; the *identity* printed in that document is missing a conjugate, and
the "18/18 to `1e-15`" check exercises only `d = 0` and could not detect it.
Use the `|T_t|` form, never the `Λ` form — `|T_t| <= Λ` is one-way and measured
**262×** slack at `p = 32779`.

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

**Additive completion** (`O2_additive_completion.md`). For **`x`-based** interval
and bit-window filters the same fibred argument runs with additive characters.
Degeneracy is *easier*: if `F_R = g^p − g + c` every pole order is divisible by
`p`, but `x(·)` and `x(R−·)` have double poles at distinct places for `R ≠ O`, so
with `p > 2` the exceptional set is the **single point** `R = O` with `α+β = 0`.
The pole-order core is validated. Two caveats the source document does not carry:
the assembly needs an **unstated balance hypothesis** on `|c_0^{(t)}|` (the
`(α,β) = (0,0)` term has `S = 1` exactly), and it holds **conditional on (H1′)**,
which [[KN-LIT-f6de4b]] finds largely untraced to any primary source.

## Why this is a barrier result and not an attack

`sota_delta = 0` on time, memory and data/queries. `dominated_by` inapplicable
rather than `null`. No solve, relation, or speedup is claimed;
`certificate.kind: none`. The value is **negative information that redirects
search**.

**It does not retire the lane.** An earlier version of this entry said the
result "retires the last exponent-moving configuration… so effort should move
off the sum-compatible-filter lane entirely." That is withdrawn: with families
D, I, J, the non-`x` members of A and B, and levels `>= 2` all uncovered, the
lane is **narrowed, not closed**, and the remaining gaps are where any surviving
attack would live.

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
   `f` stays **222×** below the `(★)` ceiling at `M = 32` — but no robust
   Theorem C is proved. (The figure "~160×" used elsewhere in this line is the
   `M = 16` value misapplied to the `M = 32` ceiling; it understates the margin,
   so the error is conservative.) Separately, the claim
   `(eps_quasi − 1/M)/Λ <= 0.17` "over all filters, primes and `M`" is **false** —
   the true maximum is **0.322**, at `dlog mod M` / `dlog-int`, `M = 5`.
2. **Arbitrary cheap `h`.** Proposition 2 of `O2_derivation_attempt.md` proves no
   group-theoretic argument can reach it: the dlog-interval pullback achieves
   `eps ≈ 1/2` at arbitrarily large `M` on every prime-order group. Only a
   definitional cost restriction closes this, and the cost clause is **not a
   theorem**.
3. **Literature hypotheses — both weaker than this line originally claimed.**
   **(H1)** multiplicative Weil/Bombieri on a curve is only partly traced (see
   [[KN-LIT-7639]]): form, non-degeneracy hypothesis and validity regime
   (`g << √q`, here `g = 1`) are confirmed; the explicit `(2g−2+2m)` constant and
   **general `k > 2` on curves** are not — which is why **family D is now marked
   NOT closed** above rather than closed. **(H1′)** the additive case is
   **largely untraced** (see [[KN-LIT-f6de4b]]): the retrieved source states the
   genus-0 projective-line bound, not the curve-level one, and does **not** state
   the Artin–Schreier criterion the completion depends on. An earlier version of
   this entry asserted (H1′) was "better attested" and had "no `KN-LIT` entry
   yet"; **both halves of that sentence were wrong**, and it contradicted a file
   this entry already cited.
4. **Constants** are not carried out anywhere in this line.
6. **Levels `>= 2` of the tree.** See the level-1 note above — this is the
   largest single gap between what is proved and what the headline once claimed.
7. **[D]'s computations were not verifiable.** They are declared scratch and are
   not in the tree, yet [D] is the source of Proposition 2, Theorem 3 and the
   entire Weil machinery. The Validator could not check any of them.
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
