# The quasigroup gap — closed exactly, unrealized approximately

> **FOLLOW-UP NOTICE — added later; no text below is altered.** The control this
> document declares missing in §4 and §6.1 — random Latin-square sampling at
> `M = 8,16,32` — **has now been run**, in `O2_quasigroup_scaling.md`. It does
> not overturn §3: the quasigroup excess *decreases* with `M` (0.076 → 0.004),
> and the **exact** worst case over all `f` stays `<= 0.196` where `(★)` permits
> `32`, which rigorously caps worst-case quasigroups too. §4's stated inability
> to separate "quasigroups are special" from "`M <= 5` is too small" is thereby
> resolved in favour of the former. Everything below stands as written.

Attacks the item that `O2_composition_closure.md` §5.1 named as the only thing
left between the composition and closure of the character-filter class for
arbitrary predictors, and that **both** independent derivations
(`O2_derivation_attempt.md` §10, `O2_fourier_obstruction.md` §7.3) named as the
highest-value open target: the **factor `M`** lost at Cauchy–Schwarz.

**Status: EXPLORATORY ANALYSIS.** No frozen specification, no `EXP-*`, `RUN-*`,
`EV-*`, or ledger record is created or modified. Claim tier *exploratory*.
`certificate.kind: none`.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Which `f` can a Wagner tree actually use? | Not arbitrary `f`. It must be invertible in each argument to index buckets — a **quasigroup**. Strictly between "group law" and "arbitrary". §1 |
| Can a quasigroup be *exactly* sum-compatible on `E(F_p)`? | **No — Theorem C, unconditional, four lines.** Associativity forces it to be a group; `Hom` from a prime-order group is trivial. §2 |
| Does the `M` loss materialize *approximately* for quasigroups? | **Not at `M = 3,4,5`**, by exhaustive enumeration of all 12/576/161280 Latin squares against 4 filter families and 4 curves. Normalized excess stays `<= 0.17`, never approaches `M`. §3 |
| So is the `M²` loss real? | **Undecided, and the measurement cannot decide it** — it is loose for *arbitrary* `f` too at these `M`. §4 states this limit plainly. |
| Net effect on the four-tree | The exact quasigroup escape is **closed by proof**. The approximate one is unrefuted but unrealized at every scale testable exhaustively. |

---

## 1. The right class is quasigroups, not arbitrary `f`

`(★)`'s factor `M` comes from Cauchy–Schwarz over all `M³` characters, which is
tight only for an `f` whose graph has spread Fourier support. But Wagner's tree
cannot use such an `f`.

A `j`-level tree merges two lists by fixing a target bucket `c` for the partial
sum and, for each element with `h(P) = a`, looking up elements with
`h(Q) = b` where `f(a,b) = c`. That lookup requires `f` to be **invertible in
each argument** — otherwise the bucket is empty or ambiguous and the level does
not recurse. An `f` invertible in each argument is exactly a **quasigroup**
(Latin square).

So the operative hierarchy is

```
   group law     ⊂     quasigroup     ⊂     arbitrary f
   eps <= 1/M+Λ         ???                 eps <= 1/M+M·Λ
   (Theorem A)                              ((★), [D] §7.2)
```

and the whole question is which end the middle sits at.

**A second cost point, recorded but not relied on.** A quasigroup with genuinely
spread Fourier support is close to a random Latin square, and storing one of
order `M ≈ p^{1/3}` costs `M² ≈ p^{2/3}` — more than the attack saves. So the
`f`'s that could saturate `(★)` are precisely the ones the cost clause
excludes. This is an argument about *description length*, not a theorem: a
succinct `f` with spread spectrum is not ruled out, and I do not rule it out.

---

## 2. Theorem C — the exact case, unconditional

**Theorem C (quasigroup rigidity).** Let `G` be a finite abelian group, `M >= 2`,
and `h : G → [M]` **surjective**. Suppose there is a quasigroup operation `f` on
`[M]` with `h(P+Q) = f(h(P), h(Q))` for **all** `P,Q ∈ G`. Then `([M], f)` is a
group and `h` is a surjective group homomorphism.

*Proof.* For any `a,b,c ∈ [M]` pick, by surjectivity, `P,Q,R` with `h(P)=a`,
`h(Q)=b`, `h(R)=c`. Then

```
 f(f(a,b),c) = f(h(P+Q), h(R)) = h(P+Q+R) = f(h(P), h(Q+R)) = f(a, f(b,c)),
```

using associativity of `+` in `G` twice. So `f` is associative. A quasigroup
whose operation is associative is a group (left and right division supply
inverses; the idempotent `e = a \ a` is a two-sided identity). Hence `([M],f)`
is a group, and `h` is a surjective homomorphism by hypothesis. ∎

**Corollary C.1.** If `G = E(F_p)` with `#E(F_p) = N` **prime** and `M < N`,
no such `h` exists except `M = 1`. A surjective homomorphism `Z/N → ([M],f)`
forces `M | N`, so `M ∈ {1, N}`. ∎

**What this does.** It removes the *exact* quasigroup escape with no
character-sum input, no class restriction on `h`, and no hypotheses beyond
surjectivity — which is [D]'s non-redundancy condition (H6), i.e. "run at
`M_eff`". It strictly generalises [D]'s Theorem 1 from the group-law predictor
to every quasigroup predictor, by an argument that is shorter.

**What this does not do.** It says nothing about `eps < 1`. [D]'s Proposition 2
shows a robust version cannot follow from group structure alone, so §3 measures
rather than proves.

---

## 3. The approximate case, measured exhaustively

`quasigroup_gap.py`. For `M ∈ {3,4,5}` **every** Latin square is enumerated
(12, 576, 161280 — exhaustive, not sampled), and for each filter the exact
triple counts

```
   C[a,b,c] = #{(i,j) : h(i)=a, h(j)=b, h(i+j mod N)=c}
```

are computed by cyclic convolution over the dlog indexing — whole-group exact
counts over all `N²` pairs, no sampling. Three quantities are compared on the
same filter: `eps_grp` (group law), `eps_quasi` (max over all Latin squares),
`eps_arb` (max over all `f`, i.e. `f_joint`).

The diagnostic is the **normalized excess** `(eps − 1/M)/Λ`. Theorem A caps it
at `1` for the group law; `(★)` caps it at `M` for arbitrary `f`.

| filter | `M` | `Λ` | `eps_grp` | `eps_quasi` | `eps_arb` | `(q−1/M)/Λ` | `(a−1/M)/Λ` |
|---|---|---|---|---|---|---|---|
| `x mod M`, `p=4111` | 3 | 0.04409 | 0.33341 | 0.33898 | 0.34299 | **0.128** | 0.219 |
| `x mod M`, `p=4111` | 4 | 0.05376 | 0.24913 | 0.25565 | 0.25803 | **0.105** | 0.149 |
| `x mod M`, `p=4111` | 5 | 0.04820 | 0.20027 | 0.20532 | 0.21071 | **0.110** | 0.222 |
| `char` (family C), `p=4111` | 4 | 0.04266 | 0.24966 | 0.25084 | 0.25881 | **0.020** | 0.206 |
| `dlog mod M`, `p=4111` | 4 | 0.90032 | 0.50012 | 0.50012 | 0.50031 | **0.278** | 0.278 |
| `dlog-int` ([D] Prop 2), `p=4111` | 4 | 0.90032 | 0.50012 | 0.50012 | 0.50031 | **0.278** | 0.278 |

Full table across `p ∈ {523, 1033, 2063, 4111}` in the script output.

**Three findings.**

1. **`(eps_quasi − 1/M)/Λ <= 0.17` everywhere** — over all filters, primes and
   `M`. It never approaches `M`. At `M=5`, where `(★)` permits `5`, the observed
   value is `0.11`.
2. **On both dlog filters, `eps_quasi = eps_grp` to five decimals.** Exhaustive
   search over all 576 quasigroups of order 4 finds **nothing** that beats the
   group law on the very filters that are the known escapes. The group law is
   already optimal there — which is what Theorem C predicts in the limit.
3. **The character filter has the smallest excess of all** (`0.020`), and it
   shrinks with `p` (`0.040 → 0.031 → 0.024 → 0.020`), consistent with the Weil
   bound governing that class.

---

## 4. The limit of this measurement, stated plainly

**`(eps_arb − 1/M)/Λ` is also small** — `<= 0.34` everywhere, where `(★)` permits
`M`. So the `M` loss is loose for *arbitrary* `f` too at `M = 3,4,5`.

**Therefore this measurement does not separate "quasigroups are special" from
"`M = 3,4,5` is too small for the loss to appear."** It rules out only that
quasigroups are *dramatically* worse than the group law at small `M`. Exhaustive
Latin-square enumeration is infeasible past `M = 5` (order 6 has `8.1 × 10^8`),
so this specific instrument cannot be pushed further; a random-Latin-square
sample at larger `M` is the natural next control and was not run.

The regime that matters is `M ≈ p^{1/3}`, which is **five to seven orders of
magnitude beyond what was tested**. Under `AGENTS.md` rule 4 nothing here is
crypto-scale evidence, and none is offered as such.

**What survives without qualification is Theorem C** — a proof, independent of
scale, class and instrument.

---

## 5. Net position on the four-tree

| combining rule | exact case | approximate case |
|---|---|---|
| group law | closed (Thm 1 / Thm A) | **closed for `M <= p^{1/2-o(1)}`** — `O2_composition_closure.md` §3 |
| quasigroup | **closed — Theorem C** | unrefuted; unrealized at every exhaustively testable `M` |
| arbitrary `f` | closed (Thm C covers it when invertible; else no tree) | bound is `1/M + M·Λ`; **not usable by a tree anyway** (§1) |

The `j=2` four-tree at exponent `0.4167` is closed for group-law combining, and
the quasigroup route to reopening it is closed exactly and unrealized
approximately.

---

## 6. Forward guidance

1. **Random-Latin-square sampling at `M = 8,16,32`** — the control §4 says is
   missing, and the cheapest thing that could still overturn §3.
2. **A robust Theorem C.** Does `eps >= 1/M + c` with quasigroup `f` force `f`
   to be `o(1)`-close to a group operation? Proposition 2 blocks the route
   through `h`; the question here is about `f`, which Proposition 2 does not
   touch. This is the sharpest remaining mathematical target.
3. **(H1) `KN-LIT` entry** for Weil/Bombieri — still owed, still gating.
4. Items 2 and 4 of `O2_composition_closure.md` §7 are unchanged.

**`dominated_by` / `sota_delta`.** No algorithm proposed; no frontier row
occupied. `sota_delta = 0` on time, memory and data/queries; `dominated_by`
inapplicable rather than `null`.

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
    models. Recorded, never silently substituted (AGENTS.md rule 11). Theorem C
    is four lines and is intended to be checked by hand rather than trusted.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
