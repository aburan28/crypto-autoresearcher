# Composing the two independent (O2) derivations — the `j = 2` four-tree closes

Reconciles two derivations of (O2) produced **independently and in parallel**
from the same parent commit `ee16c4a96`:

- `O2_derivation_attempt.md` (commit `78cbc10c2`) — Theorem 1, Proposition 2,
  Theorem 3, the Weil/Bombieri machinery. Referred to below as **[D]**.
- `O2_fourier_obstruction.md` (commit `2cf67520f`) — Theorems A and B, the exact
  identity, exhaustive verification. Referred to below as **[F]**.

Neither session saw the other's work. This document does three things: it
**corrects an overclaim in [F]** using [D]'s Proposition 2; it **composes** the
two results; and the composition **closes the single live gap [D] §10 names**.

**Status: EXPLORATORY ANALYSIS.** No frozen specification, no `EXP-*`, `RUN-*`,
`EV-*`, or ledger record is created or modified. Claim tier *exploratory* under
`docs/claims-and-verification.md`. Disposition of (O2) belongs to the Reviewer
and Coordinator. `certificate.kind: none` — no solve or relation is claimed.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Was [F]'s "unconditional" closure claim right? | **No — [D]'s Proposition 2 refutes it, and [F] is corrected here.** See §2. |
| Do the two derivations conflict anywhere else? | **No.** They agree numerically to 3–4 decimals on shared quantities and hit the *same* `M²` barrier from opposite directions. §1. |
| What does composing them give? | Wagner-level gain `<= 1 + M·Λ` with `Λ = O(D·p^{-1/2})`, hence closure for **`M <= p^{1/2-o(1)}`** instead of [D]'s `p^{1/4-o(1)}`. §3. |
| Does that close `j = 2`? | **Yes — for the group-law combining rule, which is Wagner's actual algorithm.** `j=2` needs `M ~ p^{1/3} << p^{1/2}`. This is the configuration [D] §10 calls "the single live gap". §4. |
| Is (O2) therefore closed? | **No.** Closed for the character-filter class under group-law combining. Quasigroup combining, families A/B/I/J, and arbitrary cheap `h` remain open — the last provably so. §5. |

---

## 1. The two derivations, reconciled

### 1.1 Notation collision — resolved

The documents use overlapping symbols for different objects. This table is
required reading before comparing them; below, **[C] notation** is used.

| object | [D] | [F] | **[C]** |
|---|---|---|---|
| agreement `Pr[h(P+Q) = f(h(P),h(Q))]` | `δ(h,f)` | `eps` | `eps` |
| filter alphabet size | `M` | `M` | `M` |
| divisor/degree complexity of the filter | `Δ` | — | `D` |
| max non-trivial Fourier / trilinear coefficient | `max_{ψ≠1}|T̂_ψ|` | `Delta` | `Λ` |
| max level-set Fourier coefficient | — | `delta` | `λ` |

`Λ` and `max_{ψ≠1}|T̂_ψ|` are the same object reached two ways: [F] expands the
trilinear form in the **dlog-character basis** of the cyclic group, [D] expands
it in the **character basis of the filter alphabet `μ_k^r`** and bounds it by
Weil on the curve. This is the hinge of the composition.

### 1.2 They agree

- [D] §3 cross-checks its `δ` against F1 §5: `0.5024` vs `0.5025` at `M=4`,
  `0.5088` vs `0.5111` at `M=16`. Different code, different curves.
- [F] §6 independently gets `eps = 0.50100` (`M=4`) and `0.50100` (`M=16`) for
  the dlog pull-back on `N=499`, and `0.5005` for the `Z/N` control.
- [D]'s Theorem 1 (congruence rigidity, exact case, all `h`) is **implied by**
  [F]'s Theorem A: at `eps = 1`, Theorem A forces `Λ >= 1 - 1/M`, so each `g_t`
  is a character and `h` is a homomorphism; `Hom(Z/N, Z/M)` is trivial for `N`
  prime, `M < N`. Two routes, same theorem.
- **Both hit the same `M²` barrier.** [D]'s `(★)` loses a factor `M` at
  Cauchy–Schwarz over `M³` triples; [F]'s Theorem B loses a factor `M` at
  Cauchy–Schwarz over `M` level sets. Independently derived, same place, same
  size. That is strong evidence the loss is real for adversarial `f`, not an
  artifact of either write-up.

---

## 2. Correction to [F]

[F] §0 and §4 claim the affine closure holds "**unconditionally**", resting on
its measured `Λ = Θ~(N^{-1/2})` (§6 of that document).

**That is an overclaim, and [D]'s Proposition 2 refutes it.** The dlog-interval
filter `h_M(P) = floor(M · dlog(P) / N)` has `eps ≈ 1/2` at arbitrarily large
`M` on every prime-order group. Under Theorem A that forces `Λ ≈ 1/2` — and
indeed `g_t(x) = e(t·floor(Mx/N)/M) ≈ e(tx/N)` is a dlog character, so `Λ ≈ 1`.

No contradiction with Theorem A: the inequality holds, and correctly reports
that this filter has near-maximal dlog correlation. But it destroys the word
"unconditional", because `Λ = Θ~(N^{-1/2})` is **not** a property of all `h` —
[F] measured it for two families and extrapolated.

**Corrected statement of [F]'s result.** Theorem A is unconditional *as an
inequality*. The closure conclusion is conditional on `Λ(h) = o(1/M)`, which
[F] measured for the x-coordinate and SHA families and which **provably fails**
for the dlog-interval family. [F] §7.3 did flag `Λ`'s scaling as "measured, not
proven"; the headline did not carry that qualifier, and should have.

**This makes the joint result stronger, not weaker.** [D]'s Theorem 3 supplies
exactly what [F] was missing: a *named class restriction* plus a *proof* of the
`Λ` bound on that class, in place of an extrapolated measurement. And [D]'s
Corollary 2.2 explains why the restriction is unavoidable — (O2) is not a
group-theoretic statement, so no class-free proof exists.

---

## 3. The composition

### 3.1 The two inputs

**Input 1 — [F] Theorem A** (affine `f`, no factor `M`). For
`f(a,b) = a + b + d (mod M)`,

```
   eps  <=  1/M  +  Λ(h).                                              (A)
```

Proved in [F] §2 from the exact identity
`eps = (1/M) Σ_t e(-td/M) Σ_ξ ĝ_t(ξ)|ĝ_t(ξ)|²`, verified to `1e-15` on 18/18
configurations by exhaustive enumeration.

**[D] states this same improvement**, in the §7.2 parenthetical: *"For a
group-law predictor `f(a,b)=ab` only `M` triples have `c_ψ ≠ 0`, and (★)
improves to `δ ≤ 1/M + max_ψ |T̂_ψ|`."* [D] then sets it aside — *"F1's
`f_joint` is adversarial, so (★) is the form that must be used against it."*
The inequality is [D]'s as much as [F]'s; §3.3 is about which one the Wagner
question calls for.

**Input 2 — [D] Theorem 3** (the Weil bound). For a non-redundant character
filter of complexity `(k, r, D)`, `M = k^r`, on `#E(F_p) = N` prime,

```
   Λ(h)  =  max_{ψ≠1} |T̂_ψ|   <=   c₁ D p^{-1/2}  +  c₂ D / N.         (W)
```

Proved in [D] §7.4 by fibring over `R = P+Q` and applying Weil/Bombieri for
multiplicative character sums on a genus-1 curve, with degeneracy controlled by
Lemmas 7.1/7.2.

### 3.2 The composition

Substituting (W) into (A) rather than into `(★)`:

```
   eps  <=  1/M  +  c₁ D p^{-1/2}  +  c₂ D / N.                        (C)
```

By [D]'s filter-gain Lemma 5, a Wagner level's speedup is `eps · M`, so

```
   gain  <=  1  +  M · ( c₁ D p^{-1/2} + c₂ D / N ),
```

which is `p^{o(1)}` exactly when `M <= p^{1/2 - o(1)}` for `D = p^{o(1)}`.

**Contrast.** [D]'s own route substitutes (W) into the `M`-lossy `(★)`, giving
`gain <= 1 + M² (c₁ D p^{-1/2} + ...)`, hence only `M <= p^{1/4-o(1)}`. **The
single factor `M` is the entire difference between closing `j=2` and not.**

### 3.3 Why the group-law branch is the operative one

[D] set the group-law form aside because `f_joint` is adversarial. That is the
right criterion for F1's *measurement* — F1 asked whether any `(h,f)` beats
chance, and there `f` is adversarial by construction. It is the wrong criterion
for the *Wagner* question.

Wagner's k-tree merges two lists by keeping pairs whose partial sum lands in a
prescribed bucket of a **quotient homomorphism** — over `(Z/2)^n` it is a block
of bits under XOR, and `h(a+b) = h(a) + h(b)` holds exactly, with no carries.
The combining rule *is* the group law. That is what makes the tree recurse:
the filter must be compatible with the same operation being summed.

So for the question "can a Wagner four-tree run on `E(F_p)`", (A) — not `(★)` —
is the governing inequality, and the composition applies.

**The boundary, stated precisely.** A hypothetical variant using a *quasigroup*
`f` (invertible in each argument, so buckets remain indexable) would still
support a tree, and for such `f` the `M` loss is not known to be removable.
No such variant has been exhibited in the literature or in this campaign. So:
closed for Wagner's algorithm as published; open for an algorithm nobody has
yet written down.

### 3.4 Empirical check on (W)

(W) is asymptotic. Measuring `Λ` directly for genuine F1 family-C character
filters, by exhaustive enumeration over whole groups (`charfilter_decay.py`):

```
  r=1, M=2   Λ ~ p^(-0.4964)     Λ·sqrt(p) = 2.06 → 2.00  over p = 523..65539
  r=2, M=4   Λ ~ p^(-0.4569)     Λ·sqrt(p) = 2.09 → 2.70
  r=3, M=8   Λ ~ p^(-0.4665)     Λ·sqrt(p) = 2.83 → 2.97
```

Fitted exponents `-0.457` to `-0.496` against Weil's `-0.5`, with `Λ·sqrt(p)`
flat across a **125× range in `p`**, and the constant growing slowly in `r` as
the `D`-dependence in (W) predicts. This does not prove (W) — it confirms its
`p`-dependence on the class it governs, at toy scale.

---

## 4. What closes

| `j` | needed `M` | exponent (`m=16`) | [D] via `(★)` | **composition via (A)** |
|---|---|---|---|---|
| 2 | `p^{1/3}` | **0.4167** | open — *"the single live gap"* | **CLOSED** |
| 3 | `p^{1/4}` | **0.3750** | closed (boundary) | **CLOSED**, with room |
| 4 | `p^{1/5}` | 0.4000 | closed | **CLOSED** |

**Within the character-filter class with `D = p^{o(1)}`, and under group-law
combining, every Wagner configuration `j >= 2` is closed — including the
`j = 2` four-tree at exponent `0.4167`, the last exponent-moving escape the
campaign had identified.**

This is the configuration `claim_a_adjudication.md` §3 Attack 4 named as the
real obstruction, that F1 measured and could not falsify, and that [D] §10
isolated as the one surviving target. It is now closed by an argument on the
class [D] defines, not by a sweep coming up empty.

Attack 4's conclusion — *"on `E(F_p)` every join in the class must be an
exact-equality join"* — now has a proof for character filters, rather than a
measurement.

---

## 5. What remains open

1. **Quasigroup combining rules** (§3.3). The `M²` loss stands there, from two
   independent derivations. Removing it is still the highest-value open item,
   and it is now the *only* thing between this and closure of the whole
   character-filter class for arbitrary `f`.
2. **Interval / bit-window filters** — F1 families A, B, I, J. [D] §7.6 sketches
   additive-character completion and does not carry it out; [F] measured these
   (they track the SHA null) but its extrapolation is what §2 corrects. Largest
   *routine* missing piece.
3. **Arbitrary cheap `h`.** [D]'s Proposition 2 proves no group-theoretic
   argument can cover this. Only a definitional restriction closes it.
4. **All of [D] Theorem 3's hypotheses are inherited**, including the two it
   flags: **(H1)** Weil/Bombieri not re-verified by literature search — a
   `KN-LIT` entry is owed before any promotion (`AGENTS.md` rule 9); and
   **(H3)** the explicit zero/pole count for `F_R` asserted as `O(D)`, not
   carried out. Neither affects the shape; (H3) affects `c₁`.
5. **The cost clause is still not a theorem.** The composition restricts `h`
   algebraically as a proxy for "cheap".
6. **Toy scale.** All computation here and in [D] is `N <= 65 539`. Under
   `AGENTS.md` rule 4 this is not crypto-scale validation and is not offered as
   such. The theorems are asymptotic; the computations check their steps and
   their `p`-dependence over three orders of magnitude.

**`dominated_by` / `sota_delta`.** No algorithm is proposed; no frontier row is
occupied. `sota_delta = 0` on time, memory and data/queries; `dominated_by`
inapplicable rather than `null`.

---

## 6. Attribution

The substantive machinery is [D]'s: Theorem 3, the fibred Weil argument,
Lemmas 7.1/7.2, Proposition 2 and its corollaries, and the group-law form of
`(★)`. [F] contributes the exact identity behind (A), its exhaustive
verification, and the arbitrary-`f` Theorem B.

What this document adds is the **observation that Wagner's combining rule is the
group law, so (A) rather than `(★)` governs the four-tree question**, the
composition (C) that follows, the `Λ` decay measurement on family C, and the
correction of [F] §2.

---

## 7. Forward guidance

1. **Reviewer/Coordinator disposition of (O2)** should be taken against the
   composed statement, not either document alone.
2. **A `KN-LIT` entry for (H1)** is owed before any promotion — this now gates a
   headline closure, not a side remark.
3. **Carry out (H3)'s zero/pole count.**
4. **Additive-character completion** for families A/B/I/J (§5.2).
5. **Quasigroup `f`** (§5.1) is the remaining mathematical target.
6. **F1's amendment request** — restate F1 so `M` must grow with `N`, and so the
   cost clause is definitional. Both [D] §5 and [F] §1 independently ask for
   this.

---

## Inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11). NOTE THE
    SPECIFIC CONSEQUENCE HERE: [D] and [F] were produced in genuinely separate
    parallel sessions with no shared context, which is the strongest procedural
    independence this harness can supply, but BOTH resolve to claude-opus-5, so
    this is not a model-independent check. Their agreement is evidence about the
    derivations, not about the backend. The theorems are short enough to check
    by hand, which remains the intended mitigation.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
