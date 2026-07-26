# Research Directions 2026-07-26 — Where Special Structure Can Live on a Generic Prime Field

**Lab:** crypto-autoresearcher (empirical cryptanalysis, ECDLP over ordinary prime fields)
**Date anchor:** 2026-07-26
**Status of this document:** speculation and hypothesis generation. Nothing here is a performance claim, an evidence record, or a state transition. No run was executed for this document and no measurement is reported. Every candidate is a falsifiable probe; no candidate is asserted to beat Pollard rho. IDs are **not** allocated — the labels A–F below are provisional and become `IDEA-*` / `RQ-*` / `H-*` only through `/propose-ideas` and a Coordinator ledger commit.

**Citation status:** the literature attributions in §2 and §4 are stated from model knowledge and were **not** re-verified against primary sources in this session. Treat every one as `novelty_unverified` / `citation_unverified` until an idea-generator pass with `WebSearch` confirms them. They are included because they name the prior art a reviewer needs to check, not as evidence.

---

## 1. Scope: what "generic prime field" is taken to mean

Throughout: `E/F_p`, `p` prime, `n = #E(F_p) = p + 1 - t` prime, `|t| <= 2*sqrt(p)`, with

- `ord_n(p)` large — no MOV / Frey–Rück transfer,
- `t != 1` — not anomalous, no Smart / Satoh–Araki / Semaev p-adic descent,
- no small-CM / efficiently-computable GLV endomorphism,
- Weierstrass coefficients unstructured (no small-height model by construction).

These exclusions are the point of the exercise: they remove every published prime-field weakness, and the question is what remains.

## 2. The structural reduction

The argument this document rests on is a reduction, not a measurement.

**Claim (informal).** Every representation-dependent feature of such a curve — `j`-invariant, coefficient height, model (Weierstrass / Edwards / Hessian / Jacobi), coordinate system — is a *choice of representative*, movable by `F_p`-isomorphism or by isogeny within the class. Strip those and the curve's entire non-generic content is the pair `(p, t)`.

`t` enters only through the imaginary quadratic order `O = Z[pi]`, `pi` = Frobenius, with

```text
Delta = t^2 - 4p,   h(Delta) = p^(1/2 + o(1)),   Cl(Delta) acting on the isogeny class
```

and downstream of that: the horizontal isogeny graph, the quadratic twist `E'` with `n' = p + 1 + t`, and the shared Kummer line `P^1 = E/±1`.

**Why `Cl(Delta)` is the leading candidate.** It is the only object canonically attached to a generic prime-field curve that is simultaneously (a) curve-specific, (b) of size `~ sqrt(p)` — exactly the target exponent — and (c) *subexponentially computable* (Hafner–McCurley / Buchmann, `L(1/2)`). Every other structure attached to such a curve is either exponential to compute or computable in `O(log p)` and therefore informationally free. No other channel has this combination.

**Why the author nonetheless expects it to fail.** There is a torsor type mismatch. `Cl(Delta)` acts on the *set of curves* (a `Cl(Delta)`-torsor of size `~ sqrt(p)`); the DLP lives in a *`Z/n`-torsor*. The one obvious bridge collapses — see candidate A. Recording that collapse precisely is worth more than any of the attack probes below, because it is what closes the family.

**Runner-up: the twist pair.** `E` and `E'` share the Kummer line, and the differential-addition law on `P^1` depends only on the curve constants — it is *identical* for a curve and its twist. One algebraic object therefore carries two group structures, of orders `n` and `n'`, with `n + n' = 2(p+1)` and `n*n' = (p+1)^2 - t^2`. A bare cyclic group has no such partner, so this is a genuine non-genericity.

## 3. Candidate set

Provisional labels. Area codes verified free against `ledger/RQ-*` on 2026-07-26 (used: BKK BKKMV DREG EQJ FB FB3 ICI INC INCB ISO JET JETB NCP NET R6 REP SIG STR TRA TTN).

| tag | area | kind | claim | dup risk |
|---|---|---|---|---|
| A | ENDO | barrier | `End(E)` action on `E(F_p)` collapses to a freely computable integer | low |
| B | CGT | attack-probe + barrier | do `Cl(Delta)` relations constrain `k`? | low |
| C | VELU | cost-model audit | re-audit every isogeny-charging barrier under sqrt-elu | low |
| D | ICLASS | measurement | `min|j|` over the isogeny class `~ p/h(Delta)` | medium |
| E | COND | density + null | square part `Delta = f^2 * Delta_K`, hidden-CM class | medium |
| F | KUM | measurement | twist-blind Kummer walk information yield | **high** |

### A · ENDO — Frobenius-collapse barrier

**Mechanism.** `E(F_p)` is cyclic of prime order `n`, so every group endomorphism is multiplication by an integer. The content is that the integer is *free*: Frobenius fixes `F_p`-rational points, so `pi` acts as `1`, and for `alpha = u + v*pi` the action on `E(F_p)` is multiplication by

```text
lambda_alpha = u + v  (mod n)
```

The characteristic polynomial degenerates accordingly: `t = p + 1 - n` gives `t == p+1 (mod n)`, hence `X^2 - tX + p == (X - 1)(X - p) (mod n)` — the eigenvalues are just `1` and `p mod n`, computable in `O(log p)` from `(p, t, n)` with no isogeny computation.

**Claim to prove.** The map `O -> Z/n`, `u + v*pi |-> u + v`, is a surjective ring homomorphism with kernel `(pi - 1)`. **Corollary:** any algorithm with an oracle for arbitrary endomorphism evaluation on `E(F_p)` is simulable in the generic group model at `O(log p)` overhead per call, so the GLV, volcano-walking, Deuring-transport and CM-descent families are exponent-neutral.

**Contrasting control (important).** On *oriented supersingular* curves `End` is a quaternion order whose action on points does **not** collapse to a scalar — which is precisely why intertwiner / Schur-selector arguments have content in that regime. Candidate A should be stated as that dichotomy, with the supersingular case as the named control, rather than as a bare lemma. See §5 for the adjacent live track.

**Falsification.** Exhibit `E`, `alpha in End(E)`, `P in E(F_p)` with `alpha(P) != lambda_alpha * P`; or exhibit an `End`-using algorithm not so simulable.

**Minimal discriminating test.** 30–60-bit `p`; construct a small-`l` endomorphism as an `l`-isogeny cycle returning to `E`; check `alpha(P) = lambda*P` on random `P`; confirm `lambda*lambda' == p` and `lambda + lambda' == t (mod n)`. Cheap; expected to confirm.

**Adjacency.** `H-ISO-001` (`rejected_scoped`) tested only factor-base density on `l`-isogeny neighbours and does not contain this. `G30-020` (A2 boundary theorem, cross-curve advice) is the nearest goal-program neighbour and is disjoint: it concerns transport between curves, A concerns the action on one curve's points.

### B · CGT — class-group transport

**Mechanism.** A relation `prod l_i^(e_i) = (alpha)` principal in `Cl(Delta)` yields an explicit `alpha = u + v*pi` with `u^2 + t*u*v + p*v^2 = prod l_i^(e_i)`, hence, applying the §A homomorphism to `alpha` and its conjugate,

```text
lambda * lambda_bar == prod l_i^(e_i)  (mod n),   lambda = u + v,  lambda_bar = u + v*(t-1)
```

So class-group relations manufacture a free supply of integer pairs mod `n` with known smooth product. Question: does any of this constrain `k`?

**Prediction (barrier form): no**, on two independent grounds — (i) the relations live in the multiplicative group `(Z/n)^*` while `k` lives in the additive `Z/n`; (ii) the same `(u, v)` are obtainable by direct lattice reduction on the norm form, without ever computing `Cl(Delta)`, so the channel carries no information the `L(1/2)` computation was needed for. Ground (ii) is the likely kill and is the more valuable of the two to record.

**Falsification.** Any construction turning `lambda`-relations into a constraint on `k`.

**Minimal discriminating test.** Toy `p`; harvest class-group relations; measure whether the set of `k` consistent with all harvested relations shrinks below `n` at all. Predicted shrinkage: zero. Decisive and cheap.

**Priority.** This is the flagship. It is the strongest form of the structural hypothesis in §2, so refuting it is worth more than refuting several weaker candidates.

### C · VELU — sqrt-elu cost-model re-audit

**Mechanism.** Barriers charging "degree-`d` isogeny costs `~O(d)`" predate the sqrt-elu evaluation technique (Bernstein–De Feo–Leroux–Smith, ANTS 2020), which evaluates at `~O(sqrt(d))`. The arithmetic lands on a knife edge worth recording: completing the square gives, for `v != 0`,

```text
N(u + v*pi) = (u + v*t/2)^2 + v^2 * (4p - t^2)/4  >=  |Delta|/4
```

so the minimum non-scalar endomorphism degree is `|Delta|/4`, which is `Theta(p)` for generic `t`. sqrt-elu therefore brings endomorphism evaluation to `~O(sqrt(p))` — **exactly** the birthday bound, a tie rather than a win. And by candidate A the action is free anyway, so the channel is moot regardless.

**Deliverable.** Enumerate every ledger barrier carrying an isogeny/degree cost term; recompute exponents under the `~O(sqrt(d))` model; report any sign flip. Mostly derivation, low cost, high closure value — a cost-model refresh that should be recorded once and cited thereafter.

### D · ICLASS — minimum-height representative in the isogeny class

**Mechanism.** Ordinary isogeny paths are findable in `L_p(1/2)`, i.e. *below* `sqrt(p)`. "Search the class for a weak representative" is therefore a well-posed attack whose only remaining freedom is a representation-sensitive weakness (small coefficients, small `j`, special model), since order-based weaknesses are constant on the class.

**Prediction.** The class holds `~h(Delta) ~ sqrt(p)` curves with `j`-invariants equidistributed in `F_p`, so the expected minimum satisfies `min|j| ~ p/h(Delta) ~ sqrt(p)` — far too large for any height-based global lift to gain.

**Falsification.** A measured `min|j|` significantly below the `p/h(Delta)` law, i.e. non-equidistribution of `j` over the class. That would be a real anomaly and would require independent review before any attack framing.

**Minimal discriminating test.** Enumerate full isogeny classes at small `p`; measure `min|j|` and minimum coefficient height against the predicted law.

### E · COND — hidden-CM density and null

**Mechanism.** Write `Delta = f^2 * Delta_K`. If `|Delta_K|` is small, `E` sits at the floor of a volcano whose surface has small CM discriminant — a "hidden CM-special" curve. Detecting this requires extracting the square part of a `p`-sized integer, which is factoring-hard, so such curves are not excluded by standard generation hygiene.

**Prediction: a no-op.** Descending the volcano converts a small-norm surface endomorphism into one of norm `~ f^2 * N ~ p`, and by candidate A its action on `E(F_p)` was free anyway. Worth recording because "hidden CM" is recurring folklore that keeps re-entering proposals.

**Minimal discriminating test.** Sample random `p` and random curves; factor `t^2 - 4p` at toy sizes where factoring is feasible; tabulate the square-part distribution; for small-`Delta_K` hits, measure whether any hardness proxy (rho collision rate, `m=3` Semaev `d_reg`, decomposition yield) leaves the random-control band. The density figure is a genuine deliverable independent of the hardness null.

### F · KUM — twist-blind Kummer walk

**Mechanism.** Pseudo-addition on `P^1` depends only on the curve constants and is identical for `E` and `E'`; `x`-coordinates partition `F_p` between the two curves (excluding roots of the cubic).

**Prediction.** A twist-blind walk mixes over `p + 1 ~ n + n'` states, so its birthday bound is `sqrt(2p)` — *worse* by `sqrt(2)`, not better — and cross-twist collisions carry zero mutual information with `k`.

**Dup risk: highest in the set.** `grep -ril Kummer` returns 51 files in `ideas/` against 1 in `ledger/`. Do not file without a per-file anti-dup pass.

## 4. Prior art a reviewer must check (all `citation_unverified`)

Pollard (1978); Shoup generic lower bound (EUROCRYPT 1997); Menezes–Okamoto–Vanstone and Frey–Rück transfers; Smart, Satoh–Araki, Semaev on anomalous curves; Semaev summation polynomials (ePrint 2004/031); Gaudry and Diem index calculus over extension fields; Gallant–Lambert–Vanstone (GLV); Jacobson–Koblitz–Silverman–Stein–Teske on xedni calculus and the height obstruction; Kohel and Sutherland on isogeny volcanoes; Hafner–McCurley and Buchmann on subexponential imaginary-quadratic class groups; Galbraith and Galbraith–Hess–Smart on constructing isogenies; Jao–Miller–Venkatesan, "Do all elliptic curves of the same order have the same difficulty of discrete log?" (ASIACRYPT 2005) — the direct reference for candidate D; Bisson–Sutherland on computing ordinary endomorphism rings; Bernstein–De Feo–Leroux–Smith (sqrt-elu, ANTS 2020) — the direct reference for candidate C.

## 5. Anti-duplication screens actually run

Reported exactly as executed, including limits. All screens are keyword-based; none is a semantic dedup pass.

- `class group`, `Hafner`, `Buchmann`, `velusqrt` / `sqrt-elu`: **0 hits** across all 1890 files of the external report corpus `/Volumes/Volume/git/autolab/research/` and 0 in `ledger/`. B and C are corpus-bare **on these terms**.
- `volcano | quadratic twist | Elkies | endomorphism ring`: 16 of 93 `idea_generation_*.md` reports.
- `orient`: 23 of 93 `idea_generation_*.md` reports — loose stem match, sense **not** verified. "Orientation" is the modern name for the `O -> End(E)` embedding that A and B concern, so this screen must be resolved per-report before filing either.
- `Kummer`: 51 files in `ideas/`, 1 in `ledger/`.
- Against the 30-goal program: `class group`, `endomorphism`, `CM`, `discriminant`, `orientation`, `volcano` return no substantive match. Nearest neighbours are `G30-019` (ISOWALK-C1) and `G30-020` (A2 boundary theorem), both in cluster 07 TRANSFER and both concerned with transport *between* curves — disjoint from A/B/C/E, adjacent to D. **Note for a reviewer on `main`:** this screen was run against `research_goals_20260723.md`, which lives in a separate working lineage and is **not present on `main`**. The G30 disjointness bullet is therefore not reproducible from this branch alone; treat it as unverified here and re-run it when that document is on a shared branch.
- `H-ISO-001` (`rejected_scoped`) covers only factor-base density on `l`-isogeny neighbours; it does not cover A, B, C, D or E.

**Screen limitation.** Several greps over the external corpus exceeded their timeout and were bounded or restricted to `idea_generation_*.md`. The 0-hit findings above completed before their bound; the 16/93 and 23/93 figures are from the restricted file set only. No claim of exhaustive coverage is made.

## 6. Adjacent live track — not a duplicate

`/Volumes/Volume/git/autolab/research/twisting_*_20260726.md` (4 files, same date anchor) work the `O`-twisting-endomorphism and double-orientation Schur-selector axis. That track is set in **oriented supersingular** curves and SCALLOP / PEARL-SCALLOP protocol security; its result record self-classifies as `HYPOTHESIS / CONDITIONAL WARNING / COHERENCE-OBSTRUCTION / NOT-A-BREAKTHROUGH` and states explicitly that it is not an ECDLP consequence.

Same structural axis (a CM order acting on a curve), opposite regime. The contrast is load-bearing for candidate A and is folded into it above.

## 7. Suggested order

**A → B → C** is the high-value block. A is nearly free and unifies existing rejections into one statement; B is the strongest form of the structural hypothesis, so its refutation is the real prize; C is a one-off cost-model refresh. D and E produce scaling laws and a density figure rather than closures. F only after the `Kummer` dedup pass.

## 8. Next action

None taken. Filing proposals, allocating IDs, and any hypothesis-status change require `/propose-ideas` and a Coordinator ledger commit under `AGENTS.md`. This document is a planning record only.
