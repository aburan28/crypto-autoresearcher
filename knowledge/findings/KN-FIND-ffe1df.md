---
id: KN-FIND-ffe1df
type: internal_finding
title: "(O2) a conditional, class-restricted, level-1, BUCKET-AVERAGED barrier for sum-compatible filters on E(F_p) - NOT a closure of the Wagner k-tree lane"
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

## THE HEADLINE CLAIM IS WITHDRAWN — red team RT-20260803-be45a8

An independent Red Team pass
(`analysis/o2-sum-compatible-filters/reviews/REDTEAM.md`) found a hole that no
angle in this line had touched, and it is **load-bearing for the entire `j = 2`
result**.

**Every theorem here bounds the wrong quantity.** All of them bound
`δ = Pr[h(P+Q) = f(h(P),h(Q))]`, which is the `q_c`-weighted **average** over
target buckets. A Wagner level fixes **one** bucket `c` and one offset `d`,
**chosen after seeing `h`**, and is paid at `max_{c,d} π_c(d)`. Since
`δ = Σ_c q_c π_c`, it is always true that

```
   max_c π_c  >=  δ .
```

**The closure therefore bounds a *lower* bound on the attacker's rate**, which
establishes nothing about the attacker. `O2_derivation_attempt.md` Lemma 5
bridges this with the words *"if the `π_c` are equal"*, and **nothing else in the
line touches that hypothesis**.

**Repairing it costs back exactly the factor the composition removed.** Expanding
the single-bucket rate, all `M²` coefficients have modulus 1 — no `ℓ²` saving,
the *same* Cauchy–Schwarz step both derivations independently flagged — giving
`ε_c <= 1/M² + Λ_W` and

```
   speedup = M·π_c  <=  1 + M²·Λ_W    →    p^{o(1)} only for M <= p^{1/4}
```

`j = 2` needs `M ≈ p^{1/3}`. **The `M²` barrier was never bypassed;
`O2_composition_closure.md` §3.3 escaped it by changing which quantity is
bounded.** This also resolves the corpus's own internal contradiction — the
composition said the loss "is real", `O2_quasigroup_scaling.md` said it was "a
proof artifact, not a phenomenon", and both were right about *different
quantities*.

**Measured, exactly and whole-group** (`p = 65539, M = 40`):
`M·max_c π_c = 1.084` against `M·δ = 1.002` — but the SHA null gives `1.082` and
the excess *decays* in `p` (1.15 → 1.08). So this is **a proof hole, not a
demonstrated attack**. The narrowest valid statement: **`j = 2` is UNPROVED, not
refuted.**

### Three further red-team findings

- **Family J has an explicit counterexample.** §2.2's `Σ|c_α| = O(log p)` rests on
  `g_t` being "supported on `O(1)` intervals" — false; each *level set* is, while
  `g_t` takes `M` values on `M` pieces. Measured at `p = 65539, M = 16`: popcount
  has **9438** intervals per level, `L¹ = 7.56·log p`, and
  `max|T_t| = 3.95e-1` — **101× the `√p` scale**, gain bound 7.3 rather than
  `1+o(1)`. It is entirely the `ξ = 0` marginal term, so it is a counterexample to
  the theorem *as stated* and identifies the dropped hypothesis: [D]'s **(H6)**
  balance/non-redundancy. Encouragingly, `T ~ M^θ` gives `θ ≈ 0.000` across
  `M = 4…256`, so the completion's *conclusion* survives even though its stated
  reason does not.
- **The published statistic was the wrong one.** `Λ_x = 0.01622` vs
  `Λ_sha = 0.01619` are "indistinguishable" — but `T_x = 2.00e-3` vs
  `T_sha = 5.84e-5` are **34× apart**, with `α(T_x) = −0.52` against
  `α(T_sha) = −1.20`. Algebraic filters sit at the Weil scale `p^{-1/2}`, the null
  at `p^{-1}`. **"The algebraic filters land on the null side" was an artifact of
  reporting `Λ` instead of `T_t`.**
- **The `P2` control is weaker than advertised.** It returns `0.90032` identical
  to five decimals at every `p` because it is flat *by algebraic identity*. It
  calibrates only the maximal-signal end and **never demonstrates that the
  instrument resolves the `M·T ≈ 1` boundary where closure is actually decided.**
  This line repeatedly called that control "the point"; it is necessary but far
  from sufficient.
- **"Wagner merges on a quotient homomorphism" is asserted, not derived.** A
  prime-order `E(F_p)` **has no proper quotients**, so the `(Z/2)^n` analogy pins
  nothing. The operative class is quasigroups — closed only in the *exact* case.

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
| **J — `y`-sign, popcount** | **REFUTED as stated** | not a function of `x`; and popcount is an explicit counterexample — 9438 intervals/level, `max|T_t| = 3.95e-1`, **101× the `√p` scale** |
| quasigroup combining rules | closed **exactly**; unrealized approximately | Theorem C |
| H — SHA-256 | not covered, and irrelevant | the in-arm null, outside any algebraic class by construction |

| `j` | needed `M` | exponent (`m=16`) | status |
|---|---|---|---|
| 2 | `p^{1/3}` | 0.4167 | **UNPROVED** — outside `M <= p^{1/4}`; the bucket hole is fatal here |
| 3 | `p^{1/4}` | 0.3750 | boundary case; level-1, bucket-averaged only |
| 4 | `p^{1/5}` | 0.4000 | level-1, bucket-averaged only |

**No row says "closed", and `j = 2` — the entire headline — is UNPROVED.**
Repairing the bucket hole with this line's own machinery reaches only
`M <= p^{1/4}`, and `j = 2` needs `p^{1/3}`. Earlier versions of this entry
asserted all three rows closed; that was wrong twice over, first on the
level-1 restriction and then on bucket averaging.

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

8. **The bucket-averaging hole (RT-20260803-be45a8) is the largest gap in the
   line**, and it postdates every theorem here. Until Lemma 5's equal-`π_c`
   hypothesis is either proved or replaced, **no statement in this entry
   constrains a Wagner attacker**, who picks the bucket after seeing `h`.
9. **Target-dependent `h`** has no row in the coverage table and is listed
   uncovered in [D] §7.6 item 5. Per-call filter cost is also never amortized
   over the `~p^{1/3}` calls of a single run.
10. **`O(1)`-valued combining rules** — what Proposition 2's own filter and
    Wagner-over-`Z/N` actually use — have no row either.

## The next experiment, specified by the red team

`RT-EXP-1`, the **bucket-gain ladder**: measure `G = M·max_{c,d} π_c(d)` at
`M = round(N^{1/3})`, **3 curves per `p`** across the existing 8-prime ladder, add
popcount / digit-sum / `x([2]P)` / target-dependent `h_Q`, and include a
**planted `θ = p^{-1/9}` dlog mixture calibrated to sit at `M·T ≈ 1`** — which is
the sensitivity the `P2` control never established. ~10 minutes. The claim is
refuted if any cheap family's 95% CI on `α(G−1)` excludes `<= 0` while the nulls
decay. **RUN.** See `analysis/o2-sum-compatible-filters/reviews/RT-EXP-1-RESULT.md`.
Outcome: **no attack signal for any cheap filter**, including the two the
coverage table listed as uncovered (target-dependent `h_Q`, `x([2]P)`) — all
decay indistinguishably from the SHA null over a 125x range in `p` at
`M = N^{1/3}`, the `j = 2` operating point. `popcount` and `digitsum` **tripped
the refutation criterion** (`alpha = +0.125` and `+0.495`, CIs excluding 0) and
are **both false positives**: the matched-marginal shuffle reproduces them
exactly (`+0.135`, `+0.537`), so they are entirely the free marginal-bias floor.
The instrument passes its own sensitivity test — `P2` collapses `20.0122 ->
1.0030` under that shuffle, and the planted `theta = p^{-1/9}` mixture separates
from the null where `Lambda` could not.

**This does NOT close the hole.** Lemma 5 is a PROOF gap and no theorem here
bounds `max_c pi_c`; eight toy primes are not a bound. It lowers the probability
that the gap conceals an attack. `j = 2` remains UNPROVED.

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
