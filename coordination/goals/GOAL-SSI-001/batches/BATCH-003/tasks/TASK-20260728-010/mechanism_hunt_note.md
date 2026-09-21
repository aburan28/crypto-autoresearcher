# Bounded mechanism hunt against the corrected supersingular-isogeny baseline

Task `TASK-20260728-010` · Goal `GOAL-SSI-001` · Batch `BATCH-003` · Role: idea-generator
Machine-readable companion: `mechanism_candidates.yaml` (same directory).

**Epistemic label: bounded screen.** Claim tier `theory`. Nothing here is
empirical. **Zero curve computation was performed**: no isogeny evaluated, no
`j`-invariant computed, no graph sampled, no command run.

**Axis: TIME EXPONENT ONLY.** Full cost, memory, and constant factors are out of
scope by the frozen card. Memory appears below only as mandatory disclosure.

**Budget.** 600 seconds. Four candidates were screened to completion; three short
lemma sketches were derived in place. Section 7 lists, by name, the lanes I did
not reach. Nothing in section 7 is represented as screened.

**Claim ceiling.** This is a *screen*, not a derivation of a result and not a
cryptanalytic result. It breaks nothing, establishes no bit security, changes no
status, creates no evidence/decision/hypothesis/knowledge record, and makes no
commit. `new_attack_mechanism_detected: false`.

---

## 1. The baseline I am measuring against, and the one number that matters

From `BATCH-002/TASK-20260728-009/baseline_recommendation_v2.yaml` (authoritative;
`TASK-20260728-005` is superseded and was not read):

| Regime | Operative **time** threshold | Cofactor |
|---|---|---|
| `F_{p^2}`, unconditional | `p^{1/2+o(1)}` at polynomial memory | `(log p)^{O(1)}` (cited) |
| `F_{p^2}`, heuristic-conditional | `p^{1/3+o(1)}` | **superpolynomial** `o(1)` |
| `F_p` | `p^{1/4+o(1)}` (Delfs–Galbraith) | `relayed_from_abstract`; RC4 open |

Settled and not re-opened here: MITM full cost is `Ω(p^{2/3})` uniformly in the
table size; the `p^{3/5}` rebalance does not exist.

**The L1 ceiling, stated once and attached to every candidate.** The conditional
tier sits above an `o(1)` its own author discloses as superpolynomial
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 39, read directly in this
session, verbatim): *"the overhead hiding in the o(1) term is superpolynomial,
much larger than the previous (log p)^{O(1)} cofactor"*. A threshold nobody can
evaluate at realisable `p` is not a threshold. That `o(1)` is concretely the
`u^{u}` inverse-success factor of Heuristic 1 together with the `B^{O(1)}`
modular-polynomial cost of Algorithm 1 — so **any candidate that stays inside
that architecture inherits it unchanged**, and any candidate that leaves it does
not.

---

## 2. S1 — the time exponent *is* the structural degree-bound exponent

This is the screening instrument for the whole `F_{p^2}` lane, so I derive it
rather than assert it.

Fix the architecture of the archived text (Algorithms 1–3, lines 137–205, read
directly). Its Lemma 3.3 gives the cost of building the table as
`Ψ(X,B)·X^{1+o(1)}·B^{O(1)}`, and its Lemma 3.5 gives per-attempt success
probability `u^{-u(1+o(1))}` with `u = log(p/2)/(3 log B)`. Expected total cost is
per-attempt cost × inverse success probability:

```
T  =  Ψ(X,B) · X^{1+o(1)} · B^{O(1)} · u^{u(1+o(1))}.
```

Write `Ψ(X,B) = X·v^{-v(1+o(1))}` with `v = log X / log B` (Theorem 1.4 of the
archived text, i.e. Canfield–Erdős–Pomerance). Then

```
T  =  X^{2+o(1)} · v^{-v} · u^{u} · B^{O(1)}.
```

At the archived parameterisation `B = e^{(1/3)√L}` with `L = log(p/2)`, we get
`u = √L`, `log X ≈ L/6`, `v = √L/2`, hence
`u^{u}·v^{-v} = e^{Θ(√L·log L)} = p^{o(1)}` (superpolynomial in `log p` — this is
exactly the L1 ceiling) and `B^{O(1)} = p^{o(1)}`. So

```
T  =  X^{2+o(1)}.
```

Now replace Theorem 1.5's `(p/2)^{1/3}` by a hypothetical rigorous bound
`deg φ ≤ p^{β}` valid for **every** supersingular `E/F_{p^2}`. The split argument
of Lemma 3.4 is unchanged apart from the constant: with
`X = B^{1/2}·p^{β/2}`, maximality of `k` gives
`deg η ≤ ℓ_{k+1}·p^{β}/X ≤ B·p^{β}/(B^{1/2}p^{β/2}) = X`, so both halves still fit
in one table. Therefore

```
T  =  X^{2+o(1)}  =  (B·p^{β})^{1+o(1)}  =  p^{β+o(1)}.          (S1)
```

Memory equals the table size, `p^{β+o(1)}` (disclosure only).

**Consequence, and it is the whole point of this screen.** Inside this
architecture the time exponent is *exactly* the exponent of the rigorous
structural bound it is fed, and there is no second channel. The `u^{u}` and
`v^{-v}` and `B^{O(1)}` factors are all `p^{o(1)}` and always will be. So every
candidate for lowering the conditional tier must either **move `β`** or **leave
the architecture**. Candidates C1 and C2 take the first route; C3 takes the
second; C4 tries to port the architecture to another regime.

A pleasant secondary fact: shrinking `β` shrinks `u = β log p / log B`, which
*raises* the smoothness probability. C1 is self-reinforcing in the heuristic.

---

## 3. S2 — polynomially enlarging the target family cannot help (this family)

The `BATCH-002` record left lead L1's ceiling at *"o(1) unless the alternative
target set grows POLYNOMIALLY in p rather than by a constant multiplicity"*. I
close the polynomial branch for the obvious family, and I scope the closure
carefully.

### 3.1 The derivation

Fix `K ≥ 1` and set `T_K(E) = { F : some isogeny F → E^{(p)} has degree ≤ K }`.
By Lemma 3.2 of the archived text (`I(x) ≤ x(log x + 2)`, citing `[2, Lemma 5.7]`),
`|T_K| = O(K² log K)`.

Let `D₁` be the minimal degree of an isogeny `E → E^{(p)}` and let
`D_K = min_{F ∈ T_K} (minimal degree of an isogeny E → F)`.

*Lower bound on `D_K`.* Let `F ∈ T_K` realise `D_K` via `ψ : E → F` of degree
`D_K`, and let `θ : F → E^{(p)}` have degree `d ≤ K`. Then `θ∘ψ : E → E^{(p)}` has
degree `d·D_K ≤ K·D_K`, so by minimality `D₁ ≤ K·D_K`, i.e.

```
D_K  ≥  D₁ / K.                                                   (†)
```

*Cost.* The architecture needs one smooth-isogeny list from `E` and one from each
target, each of size `X² = B·D_K` by S1's sizing. Total

```
cost  =  Θ(K²) · B · D_K   ≥(†)   Θ(K) · B · D₁,
```

which is `Θ(K)` times the `K = 1` cost. **Polynomial `K = p^{δ}` raises the time
exponent to `1/3 + δ`.**

*What the enlargement does buy.* It multiplies the per-attempt success
probability by at most `|T_K|`, and the probability is capped at 1. The factor it
can therefore replace is at most `u^{u} = p^{o(1)}`, while the price is
`p^{Ω(1)}`. The trade is losing at every polynomial `K`.

### 3.2 Robustness sketch (a sketch, not a proof)

One might build a *single* enlarged list from `E^{(p)}` — all smooth isogenies of
degree ≤ `K·X` — instead of `Θ(K²)` lists. That list has size `(KX)² = K²X²`, the
same floor. I did not verify that no third implementation evades both; that is
flagged as an open check in `C2.minimal_test.controls`.

### 3.3 Scope of the closure — read this before quoting S2

`(†)` uses precisely that every member of `T_K` composes *back* to an
`E → E^{(p)}` isogeny of degree ≤ `K·D_K`. A target family defined by a **different
structural relation** — targets in a higher-dimensional Kani construction, Galois
conjugates over a larger field, or anything not reachable from `E^{(p)}` by a
bounded-degree isogeny — is **not covered**. S2 is a scoped screen result. It
declares no direction impossible.

This is consistent with Remark 1 of the archived text (line 191, read directly),
which prices the *constant-multiplicity* version as "absorbed in the hidden term
of the asymptotic complexity". S2 extends that verdict from constant to
polynomial multiplicity for this family.

---

## 4. S3 — recognizable-subgraph mechanisms have a `p^{1/3}` time floor

Delfs–Galbraith is usually described as a single algorithm. It is better read as
one point of a one-parameter family, and locating the family's optimum is
informative.

### 4.1 The mechanism class

Let `W ⊆ V` satisfy: **(i) recognizability** — membership testable in `p^{o(1)}`;
**(ii) walkability** — `W` carries a subgraph structure so a pseudorandom walk can
be run *inside* it; **(iii) connectivity** within `W`. The mechanism: walk both
inputs into `W`, then collision-search inside `W`.

*Hitting term.* Under H1′ of the authoritative baseline (endpoint mixing,
Ramanujan gap, `KN-TECH-024`), a walk endpoint is near-uniform on `V`, so a
restart hits `W` with probability `|W|/n_V`. Expected cost `p^{1+o(1)}/|W|`.
(The meet-in-the-middle alternative — enumerate smooth isogenies from `E` of
degree ≤ `d` until a codomain lies in `W`, needing `d² ≈ p/|W|` — costs the *same*
`p/|W|`, because with a *set* target there is no far-side table to collide
against. The S1 speedup does not apply to set targets. This is worth stating
explicitly: it is the precise reason MITM helps for `E^{(p)}` and not for `V_p`.)

*Inner term.* A distinguished-point collision search inside `W` costs
`|W|^{1/2+o(1)}`.

```
T(|W|)  =  p^{1+o(1)}/|W|  +  |W|^{1/2+o(1)}.
```

The first term decreases and the second increases in `|W|`, so the minimum is at
the crossing: `p/|W| = |W|^{1/2}` ⟺ `|W| = p^{2/3}`, value

```
min_{|W|}  T  =  p^{1/3+o(1)},   attained at |W| = p^{2/3+o(1)}.   (S3)
```

### 4.2 Two consistency checkpoints that pass

- `W = V_p`, `|W| = p^{1/2+o(1)}`, arbitrary `F_{p^2}` input:
  `p^{1/2+o(1)} + p^{1/4+o(1)} = p^{1/2+o(1)}` — the archived unconditional tier.
- `W = V_p`, `F_p`-rational input: the hitting term is **zero** (the input is
  already in `W`), leaving `p^{1/4+o(1)}` — the archived `F_p` baseline. This also
  shows the `1/3` floor governs only inputs that must pay to reach `W`.

### 4.3 The confounder that kills the obvious construction

"Just enlarge `W`" fails. Take `W_d` = the `d`-neighbourhood of `V_p`, of size
`≈ d²p^{1/2}`. Membership testing now costs `≈ d²` (walk out `d` steps and test
`j ∈ F_p`), so the hitting phase costs `(p/|W_d|)·d² = p^{1/2}` — the enlargement
and the test cost cancel exactly. Worse, `W_d` is **not walkable**: an
`ℓ`-isogeny step from a curve at distance `d` from `V_p` need not stay within
distance `d`, so requirement (ii) fails and the inner term is not `|W_d|^{1/2}`.
Both requirements bite.

### 4.4 What S3 says and does not say

**Says.** (a) No mechanism of this class beats `p^{1/3+o(1)}` time. (b) The
coincidence that the heuristic-conditional frontier and the optimum of a
completely different mechanism are both `1/3` is now explained rather than
noticed. (c) Attaining `p^{1/3}` in this class requires a recognizable, walkable
`W` of size `p^{2/3+o(1)}` — one concrete existence question replacing an
open-ended hope.

**Does not say.** It is not a lower bound on path-finding. It bounds one
mechanism class, under H1′, with a stated cost model, and it carries explicit
falsification conditions in the YAML.

**Why the existence question is nonetheless interesting.** Such a `W` would give
`p^{1/3}·(log p)^{O(1)}` — an exponent move `1/2 → 1/3` against the
**unconditional** tier, at `(log p)^{O(1)}` cofactors, i.e. **below** the L1
ceiling. At any realisable `p` that dominates a `p^{1/3+o(1)}` algorithm whose
`o(1)` is superpolynomial, even though the exponents tie.

**The blocker, honestly labelled.** The natural `W` of size `p^{2/3}` is the
`𝒪`-orientable locus for an imaginary quadratic order of discriminant `≈ p^{4/3}`
(class number `≈ p^{2/3}`, and the class-group action supplies walkability —
`KN-TECH-027`). Its membership test is *deciding orientability*, which I
**recollect** is believed to be as hard as computing the endomorphism ring, in
which case the mechanism is circular. **I did not verify this and read no source
for it in this session.** It is recorded as an unchecked recollection and is
exactly what C3's minimal test must settle.

---

## 5. External ingredient scouting — what I searched and what I found

Search heuristic 2 of `agents/idea-generator.md` says to hunt for external
structural theorems that convert a bottleneck into a tractable step. By S1 the
scarce ingredient is precisely a better `β`. I hunted for it and **failed**.

| # | Action | Outcome |
|---|---|---|
| 1 | WebSearch: `E → E^{(p)}` degree bound `(p/2)^{1/3}` | **Failed** to locate. Surfaced eprint 2025/189 (experimental path-finding between conjugates) |
| 2 | WebSearch: smallest-degree isogeny to conjugate, `p^{1/3}`, 2025 eprint | **Partial.** Confirmed the archived text is eprint 2026/1486; surfaced eprint 2025/1605 |
| 3 | WebSearch: `"Frobenius conjugate"` + degree upper bound + eprint | **Failed** to locate. Surfaced eprint 2026/1278 and AWS 2026 notes |
| 4 | WebFetch `https://eprint.iacr.org/2025/1605` | **Abstract retrieved** |
| 5 | WebFetch `https://eprint.iacr.org/2025/189.pdf` | **Failed — HTTP 403.** Nothing read |

**Reference `[4]` of the archived text — the source of Theorem 1.5 and the single
load-bearing ingredient of the entire `p^{1/3}` result — was not identified.**
Its proof technique, its tightness status, and whether its authors conjecture an
improvement are all unknown to this screen. Every `novelty_status` in the
companion YAML is therefore capped at `unverified`, and C1's minimal test is this
retrieval done properly.

**Logged ingredient (abstract only, not the full paper).** *Refined Humbert
Invariants in Supersingular Isogeny Degree Analysis*, eprint 2025/1605. Its
abstract states it proves *"an upper bound on the largest minimal isogeny degree
among pairs of supersingular elliptic curves, independent of their
endomorphism-ring structures"*, verified experimentally to `p = 659`. This is a
**different quantity** from `β`: it bounds the distance between *arbitrary* pairs,
and a counting argument (the number of curves within degree `d` of a fixed curve
is `O(d² log d)` by Lemma 3.2, so covering `≈ p/12` curves needs `d = Ω(p^{1/2})`
up to logs) forces that quantity to be at least about `p^{1/2}` — feeding it into
S1 would give `p^{1/2}`, no better than the unconditional tier. The point of
Theorem 1.5 is precisely that `E^{(p)}` is *not* a generic target. Recorded as a
scouted ingredient with its limitation, not as a lead. **I read only the
abstract; the exponent in that bound is not known to me.** No `knowledge/` entry
was created — `knowledge/` is outside this task's write scope.

---

## 6. Candidate summary

| ID | Mechanism (one line) | Assumption targeted | Must beat | Could it? | Novelty | A1 target-class? |
|---|---|---|---|---|---|---|
| **C1** | Replace Theorem 1.5's `(p/2)^{1/3}` with `p^{β}`, `β<1/3`; inherit `p^{β+o(1)}` via S1 | EndRing / OneEnd / Isogeny over `F_{p^2}` (SQIsign, CGL) | `p^{1/3+o(1)}` | **Yes, 1-for-1 — if the ingredient exists.** Not found | `unverified` (corpus+ledger grepped, 3 web searches, ref `[4]` not located) | **Yes**, if the ingredient exists. Inherits the L1 ceiling |
| **C2** | Enlarge the target to `T_K(E)`, `|T_K| = O(K²log K)` | same | `p^{1/3+o(1)}` | **No** — S2: exponent becomes `1/3+δ` | `adaptation` (this is L1's open branch, from the baseline record) | **No** — best case improves only the `o(1)` |
| **C3** | Recognizable walkable subgraph `W`, `|W| = p^{2/3}`, DG mechanism on it | Path-finding over `F_{p^2}` | `p^{1/2+o(1)}` uncond. / `p^{1/3+o(1)}` cond. | **Beats the unconditional tier, ties the conditional one** — if `W` exists; blocked on orientability testing | `unverified` (corpus+ledger screened; **no web search run** — bound reached) | **Yes vs. unconditional**, **no vs. conditional**. Escapes the L1 ceiling |
| **C4** | Port the mechanism to `F_p`/CSIDH by targeting the smallest endomorphism outside `Z[π]` | CSIDH class-group action, `F_p` path-finding | `p^{1/4+o(1)}` (`relayed_from_abstract`) | **No on the direct transfer** (target degenerates); **unlikely** on the repaired one | `unverified`; degeneration is elementary, likely folklore, recorded only because it is absent from the corpus | **No** as screened |

### C4's degeneration, since it is short and structural

For `E` defined over `F_p`, `E^{(p)} ≅ E`. The smallest isogeny `E → E^{(p)}` has
degree 1 and the endomorphism the architecture returns is the Frobenius `π`
itself — known a priori. **The mechanism returns nothing beyond `Z[π]` on the
entire `F_p` locus.** That is a structural explanation of the archived text's own
statement (line 35, read directly) that group-action constructions like CSIDH are
*"safe from the attack"*, and it says the same about C1 even if C1 succeeds.

The repaired target is the smallest endomorphism *outside* `Z[π]`. By S1 the cost
would be `p^{β_p+o(1)}`. My screening estimate — from an Eichler/Hurwitz
class-number-sum reading done **from memory, with no source read, and explicitly
unverified** — is `β_p ≥ 1/3 > 1/4`, i.e. dominated by Delfs–Galbraith. It must
not be quoted as a derivation; settling it is a cheap retrieval that I did not
reach.

---

## 7. What I did not reach inside the 600-second bound

Named, so the omissions are visible and nobody mistakes silence for a negative
screen. **No verdict, positive or negative, is offered on any of these.**

- **NR1 — higher-dimensional (Kani / superspecial abelian surface) mechanisms.**
  The one lane with a demonstrated record of collapsing an isogeny exponent (the
  2022 SIDH break), and where eprint 2025/1605 sits. Not screened. It is also the
  most likely place for a target family that evades S2's scope (§3.3).
- **NR2 — quaternion-side / Deuring-correspondence mechanisms** (KLPT-style ideal
  manipulation, lattice reduction on maximal orders). The archived paper uses the
  correspondence for *validation* only, never as an attack surface. Not screened.
- **NR3 — index-calculus-style relation collection for the CSIDH class-group
  action.** The natural route that would leave the `p^{γ}` regime entirely rather
  than move an exponent inside it. C4 touches the `F_p` lane only through the
  degeneration argument. Not screened.
- **NR4 — quantum mechanisms**, excluded by the frozen convention (W5 charges no
  quantum resources). Named so the omission is deliberate.
- **NR5 — verification of two recollections** carried in this artifact and
  labelled as such: C3's orientability-hardness blocker, and C4-H2's
  class-number count. Both are cheap retrievals.
- **NR6 — RC4.** `KN-LIT-078` was not read here either. The `F_p` threshold
  remains `relayed_from_abstract` and C4 is scored against it at that confidence.
- **Read-coverage gap:** I read lines 1–933 of the 1238-line
  `baseline_recommendation_v2.yaml`. Nothing is quoted from the remainder.

---

## 8. Recommendation

**Develop C1 first.** S1 shows the architecture exposes exactly one lever and
that the lever moves the time exponent one-for-one, so a single external
ingredient is decisive. Its minimal test is one literature retrieval at zero
curve compute, and **both outcomes are informative**:

- *If a matching lower bound exists* (an explicit family with minimal degree
  `p^{1/3-o(1)}`), then `β = 1/3` is optimal, C1 dies, and by S1 the entire
  Wesolowski architecture is **capped at `p^{1/3+o(1)}` time** — a barrier result
  worth recording in its own right.
- *If no lower bound is known*, C1 is the highest-leverage open lever in the area,
  and the ingredient hunt becomes the program's main line.

That asymmetry — cheapest possible test, and a valuable answer in either
direction — is why C1 outranks C3 despite C3 being the only candidate that
escapes the L1 superpolynomial ceiling. C3 is the clear second: same zero-compute
cost, but its minimal test is a hardness question whose likely answer is negative,
and its upside is a *tie* on the conditional exponent (albeit a tie that would
dominate at realisable `p`).

**Do not re-open C2**, and when citing S2 carry its §3.3 scope with it.

---

## 9. Limits

- Bounded screen inside 600 seconds. Four candidates; §7 lists what was skipped.
- S1, S2 and S3 were derived by **one session, unreviewed**, and S3 is conditional
  on H1′, which this program has neither validated nor challenged. S1's
  conclusion is conditional on the restated smoothness heuristic (C1-H1).
- Every `p^{1/3+o(1)}` figure remains conditional on Heuristic 1 of the archived
  text. Dropping that qualifier downstream is a claim-tier violation under
  `docs/claims-and-verification.md`.
- No heuristic here is validated. Zero curve compute; no empirical claim at any
  tier. Toy-scale validation would validate nothing at cryptographic scale.
- Novelty screening was against `knowledge/`, `ledger/proposals/`, the BATCH-002
  artifacts and `inputs/`, plus three web searches that **failed to locate the
  decisive reference**. Every `novelty_status` is `unverified` or `adaptation`.
- No direction is declared impossible. S2 and S3 are scoped negatives inside named
  mechanism classes, each with explicit falsification conditions.
- This session self-reports as `claude-opus-5`, the same resolved model as the
  BATCH-002 producer, reviewer and erratum sessions. Under `AGENTS.md` rule 13 it
  is not an independent judgement for any closure attestation.

## 10. Provenance

Requested policy `research-deep` (idea-generator). Resolved model `claude-opus-5`
(self-reported). `model_verified: false` — no adapter probe was run.
`fallback_used: unknown`. `reasoning_effort: policy_default`.
`independent_session: true` — I authored no BATCH-002 artifact.

Tools: `Read`, `Grep`, `Glob`, `WebSearch` (3 calls), `WebFetch` (2 calls, one
403), `Write`. No commands executed, no git operations, no probe. **Zero curve
computation.** Nothing written outside
`coordination/goals/GOAL-SSI-001/batches/BATCH-003/tasks/TASK-20260728-010/`. No
ledger, knowledge, evidence, decision or hypothesis record created or edited; no
official state changed; no commit made; no work assigned to any agent. The
immutable BATCH-002 artifacts were read and **not modified**.
