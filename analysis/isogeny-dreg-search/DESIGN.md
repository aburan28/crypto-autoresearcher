# Exhaustive isogeny-class search for a cheaper prime-field decomposition presentation

**Status: analysis note and instrument design, not an evidence record.**
Nothing here transitions a hypothesis, closes a lane, or claims a speedup.
`sota_delta`: zero. Claim tier of every number in this note: **toy**. The
demonstration runs in section 10 are smoke runs of the instrument, not
`RUN-*` records, and carry no evidential weight until an approved `EXP-*`
contract re-runs them under the run wrapper.

Instrument: [`tools/isogeny_dreg_search.py`](../../tools/isogeny_dreg_search.py)
(pure Python, no dependencies).
Tests: [`tests/test_isogeny_dreg_search.py`](../../tests/test_isogeny_dreg_search.py).
Proposal record: `ledger/proposals/IDEA-20260903-47f358.yaml`.
Lane: `RQ-ICINV-475b5e` (GOAL-ENDO-001, L1), successor to `RQ-ISO-001` /
`EV-ISO-001`.

---

## 0. The request and its honest instantiation

The brief: *devise a computational approach to searching isogenies of
generic prime-field curves for a faster Gröbner-basis / root-finding
decomposition step whose degree of regularity does not explode; the search
must be exhaustive and cover everything below 2^40.*

Two things have to be pinned before any code is worth writing.

**What an isogeny can change.** Let `E / F_p` be ordinary with
`N = #E(F_p)` prime (the cryptographic case). Then:

1. *(Tate)* every `F_p`-rational isogeny from `E`, of any degree, lands on a
   curve with the same trace `t`; the set of reachable curves is exactly the
   `F_p`-isogeny class, finite, of size `Σ_{O ⊇ Z[π]} h(O) ≈ √p`.
2. Because `N` is prime and `ℓ ∤ N`, every rational `ℓ`-isogeny
   `φ : E → E'` is a **bijection** `E(F_p) → E'(F_p)`. A decomposition
   `R = P_1 + … + P_m` exists on `E` iff `φ(R) = φ(P_1) + … + φ(P_m)` exists
   on `E'`. An isogeny cannot create or destroy relations.
3. What it *does* change is the **presentation**: the summation polynomial
   `S_3` of the model `(a', b')`, and the pull-back of any factor base
   through the degree-`ℓ` rational function `x' = f_φ(x)`.
4. `F_p`-isomorphic models `(u^4 a, u^6 b)` give `S_3` systems related by
   the scaling `x ↦ u^2 x`; every degree-type functional is
   isomorphism-invariant. So the search object is the **set of
   `F_p`-isomorphism classes in the isogeny class**, i.e. `j` together with
   the twist fixed by `t`.

This is the lossy-projection test of `docs/inventor-protocol.md` §2 applied
before computing. The *tracked object* is the pair
`(model, factor-base pull-back)` and the projection that is kept is the
degree-graded shape of the ideal it presents — Newton polytope of `S_3`,
first-fall degree with the field/subgroup equations, root count and
splitting of the fibre polynomial. What is discarded (the actual point set)
is discarded compatibly, because fact 2 says the point set is the same on
every vertex.

**What "exhaustive below 2^40" can mean.** Three readings, with the count
that decides each:

| reading | size | status in this design |
| --- | --- | --- |
| every prime `p < 2^40` × every curve in its class | `≈ 4·10^10` primes × `≈ 2^19` curves ≈ **2^55** models | impossible by counting; never claimed; `--cost-model` prints the number |
| a fixed curve, every rational isogeny of degree `< 2^40` | ≈ `2^40 · L(1,χ_D)` codomains at crypto `p`, but a **prime**-degree `ℓ ≈ 2^40` isogeny needs `Φ_ℓ` or the `ℓ`-torsion field — no known algorithm computes it | not enumerable at crypto scale; the smooth-degree sub-ball is, and is the crypto-scale fallback (section 9) |
| a fixed curve with `p ≲ 2^40`, **its whole isogeny class**, i.e. every curve any rational isogeny of any degree can reach | `≈ √p / π · L(1,χ) ≤ 2^20` models per curve | **this is the exhaustive layer**: it subsumes every degree bound, and it is certified by a class-number census |

So the instrument is exhaustive over the *class* — the largest object an
isogeny search can be exhaustive over — for fields up to about `2^40`, and
it certifies that exhaustiveness on every run. The field itself is sampled
generically (random prime, random `(a, b)`), never swept.

## 1. The search, stage by stage

Input: `(p, a, b)` or `--bits n` (random prime and random model of that
size), a seed, the factor-base parameters `k` (for F3) and `h` (for F2).

**S0 — class data.** `t = p + 1 − #E` (exact character sum for
`p ≤ 2^17`, Mestre-style BSGS order above). `D = t² − 4p = f² D_0`.
Predicted class mass `H(4p − t²)`, the Hurwitz–Kronecker class number,
computed independently by counting reduced primitive binary quadratic forms
of every discriminant `D/f'^2`. Supersingular input is refused.

**S1 — rational `ℓ`-subgroups without modular polynomials.** For odd `ℓ`,
the `ℓ`-division polynomial `ψ_ℓ ∈ F_p[x]` (degree `(ℓ²−1)/2`, built by the
standard recursion and checked for degree and leading coefficient `ℓ`) is
distinct-degree factored up to degree `(ℓ−1)/2`. Each irreducible factor
`q` of degree `r` gives `x(Q) ∈ F_{p^r} = F_p[t]/q`; the `x`-only
differential-addition ladder produces `x([i]Q)` for `i ≤ (ℓ−1)/2`, and
`h(x) = ∏ (x − x([i]Q))` is a kernel polynomial iff all its coefficients
lie in `F_p`. Distinct kernel polynomials are the rational cyclic
subgroups. `ℓ = 2` uses the rational roots of `x³ + ax + b`. Primes inert
in `Q(√D)` are skipped (no rational `ℓ`-isogeny exists anywhere in the
class).

**S2 — codomain by Vélu / Kohel.** From the kernel polynomial's first three
elementary symmetric functions, Newton's identities give the power sums
`p_1, p_2, p_3` and Vélu's `a' = a − 5v`, `b' = b − 7w` with
`v = 6p_2 + 2an`, `w = 10p_3 + 6ap_1 + 4bn`. Every codomain is checked to
have order `N` (`[N]P = O` on random points; with `N` prime this is a proof
of `#E' = N`), and for `ℓ ∈ {2, 3}` additionally `Φ_ℓ(j, j') = 0` with the
classical modular polynomial. Any failure aborts; it is a bug, never a
result.

**S3 — closure and certificate.** Breadth-first closure over the
generating primes, repeated until no vertex has an unexplored edge or the
census is met. The census: `Σ_{members} 2/|Aut(E')|` must equal
`H(4p − t²)` exactly (rational arithmetic, no tolerance). Equality is
`certified: true`; anything less is reported as a coverage fraction and the
run may not be described as exhaustive. Exceeding the census is an
isomorphism-key or Vélu bug and aborts.

**S4 — functionals on every member, identical code on the null set.**

* **F1** monomial support of `S_3(x_1, x_2, x_3)`. Pre-registered: `13` for
  every model with `a'b' ≠ 0`; fewer only at `j ∈ {0, 1728}`, which exist
  in a class iff `D_0 ∈ {−3, −4}` — a class invariant.
* **F2** first-fall degree of `{ S_3(x_1, x_2, x_R), x_1^h − 1, x_2^h − 1 }`
  over `F_p` — the prime-field PDP shape with a subgroup factor base of
  order `h | p − 1` — read off the degree-graded Macaulay matrix in two
  variables (sparse elimination under a degree-compatible order; a fall at
  `D` is a new pivot of degree `< D` that `M_{D−1}` did not have).
  Pre-registered closed form: `d_ff = h + 2`, from
  `x_1^{h−2} S_3 − c·x_2^2 (x_1^h − 1)`. This is the "explosion" the brief
  refers to, in its exact form: the fall degree is pinned by the subgroup
  order, not by the curve.
* **F3** fibre root statistic for the polynomial factor base `x = u^k`:
  for random `(R, u_1)`, the number of `F_p`-roots in `u_2` of
  `S_3(u_1^k, u_2^k, x_R)`, via `deg gcd(f, u^p − u)`. Roots come in
  `μ_k`-orbits, so the count lies in `{0, k, 2k}`; pre-registered mean `≈ 1`
  (each of the two `X`-roots is a `k`-th power with probability `1/k`), with
  per-sample variance of order `k`. A reducible fibre curve or a degenerate
  model raises the mean by a multiple of `≈ 1`.

**S5 — decision.** A member is a *survivor* if F1 `≠ 13`, or F2 differs
from the null set's value, or F3's mean lies more than four standard errors
outside the null band (standard error pooled from the null histograms, never
below `√(k / samples)`). Survivors are the only members that earn a full
Gröbner-basis verification; on the demonstration runs there are none on
generic input and exactly the `j = 0` members on a `D_0 = −3` input
(positive control).

## 2. Controls (inventor protocol §3, before belief)

| control | what it catches |
| --- | --- |
| **matched null**: random `(a, b)` at the same `p` with a *different* trace, same `k, h`, same sample count, same code | a functional that is constant on the class *and* on the null is an instrument constant, not an isogeny-class finding — the exact trap `EV-ICINV-343679` documents for four functionals |
| **positive control**: a `D_0 = −3` class, whose `j = 0` members must surface as F1 survivors (`test_search_flags_j_zero_member_as_survivor_when_present`) | a search that cannot flag the one degeneration we know exists is not a search |
| **structural tell**: within-class spread of F3 must not exceed the between-class (null) spread by more than sampling error; a spread that does not shrink as `samples` grows is sampling noise, not structure | the "excess that does not decay" artifact |
| **order check** on every codomain, **modular check** at `ℓ ∈ {2, 3}`, **census** at the end | a Vélu, kernel-polynomial or isomorphism-key bug becoming a "finding" |
| **brute-force cross-check** at `p = 211`: every ordinary trace class enumerated by the walk equals the class found by enumerating all `p²` models | completeness of S1–S3 as code, not as theorem |

## 3. Pre-registered outcomes and what each means

* **All three functionals inside the null band on a certified class**
  (the expected outcome, and the one every demonstration run produced):
  a *scoped negative with a measured obstruction* — record the F2 value
  `h + 2` and the F3 band, over the class enumerated, at the `(p, k, h)`
  tested. It closes the "curve model" axis for these presentations at that
  scope and says nothing about other factor-base maps, other `m`, or other
  primes.
* **F1 survivors only, in a `D_0 ∈ {−3, −4}` class**: known
  automorphism degeneration (`KN-TECH-018` territory); a class invariant,
  reachable only if the input curve already has it; not a search result.
* **F3 survivor on a certified class of a generic curve**: the interesting
  case. It means the fibre curve `S_3(u_1^k, u_2^k, x_R) = 0` splits or
  degenerates for that model and not for its neighbours. Next step is not a
  claim but `/design-experiment`: reproduce with independent seeds, verify
  reducibility symbolically, and measure whether the effect changes the
  root-finding degree by more than a constant. A constant-factor gain does
  not move an exponent (`dominated_by: Pollard rho` stays unless it does).
* **Census not met**: not a result of any kind; add generating primes or
  raise the member cap and re-run.

## 4. Why a positive is unlikely, said plainly

The lossy-projection analysis in section 0 already predicts the negative:
facts 2–4 leave `(j, twist)` as the only variable, F1's support is fixed off
`j ∈ {0, 1728}`, F2's fall degree is pinned by `h`, and F3's fibre curve is
the pull-back of a genus-one curve (the image of `P ↦ (x(P), x(R − P))`)
through `(u_1, u_2) ↦ (u_1^k, u_2^k)`, whose reducibility is governed by
whether `x` is a `k`-th power in `F_p(E)` up to constants — which happens
only at `b = 0`. So the honest prior is that the search returns the
measured obstruction. It is built and run anyway for the reason
`docs/inventor-protocol.md` gives: a negative that was *argued* is
`unverified`; a negative that was *enumerated and certified* is a closure
with a number in it, and the number is reusable by the next reader with a
different factor-base map in hand. The search is decisive in both
directions and costs minutes at toy scale.

## 5. Cost model and the `2^40` plan

Measured on this reference engine (single core, pure Python, `samples=64`,
`nulls=6`, F2 on):

| `log₂ p` | `p` | class size | certified | generating primes used | enumeration | measurement | total wall |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 7127 | 96 | yes | 2, 3 | 0.0 s | 0.6 s | 0.7 s |
| 16 | 35933 | 176 | yes | 2, 5 | 0.3 s | 1.2 s | 1.5 s |
| 18 | 143729 | 144 | yes | 3, 5, 13 | 81.8 s | 1.0 s | 82.8 s |
| 20 | 863851 | 96 of 576 (coverage 1/6) | **no** with primes ≤ 13 | 3, 5, 7, 13 | 63.4 s | 0.9 s | 64.3 s — re-run with primes to 47 in progress at commit time; row to be replaced by the certified figures |

Enumeration cost is entirely the division-polynomial factoring for the
smallest *split* prime the class needs: at 18 bits the primes 3 and 5 are
ramified (order-2 class-group elements) and 13 is the first split prime, so
`ψ_13` (degree 84) is factored on every member. That is the term to
compile first. Measurement (F1 + F2 + F3 at `samples = 64`) is
`≈ 7 ms`/member throughout.

Extrapolation (`--cost-model`): class size `≈ 2√p / π · L(1,χ)`, so
`≈ 6.7·10^5` members at `p ≈ 2^40`. Per-member cost is dominated by
factoring `ψ_ℓ` for the generating primes (degree `(ℓ²−1)/2`, `O(ℓ⁴ log p)`
word operations) and by the F3 root counts (`O(k² log p)` per sample). A
compiled engine at `≈ 5 ms`/member puts the whole class at `≈ 1 CPU-hour`;
the pure-Python reference engine is for `p < 2^24`. Above `2^17` the trace
comes from BSGS and remains exact; the census remains exact at every size
because form counting is `O(√|D|)`.

**At cryptographic `p`** the class is `≈ 2^128` and no exhaustive layer
exists. The fallback the tool does not yet implement, recorded here so the
gap is legible: enumerate the **smooth-degree ball** — every ideal
`∏ 𝔩_i^{e_i}` of norm `< 2^40` over split primes `ℓ_i ≤ B` — by the same
S1–S2 walk, apply the `O(1)` screens F1 and F3 to every node, and run the
Gröbner verification on survivors. That is exhaustive over smooth degrees
below `2^40` and *silent* on non-smooth ones, which are unreachable by any
known algorithm without `Φ_ℓ` for `ℓ ≈ 2^40`; a plan that calls the
smooth ball "everything below `2^40`" would be overclaiming and this note
does not.

## 6. Relation to what the ledger already holds

* `RQ-ISO-001` / `H-ISO-001` / `EV-ISO-001` (2026-07-16): 2/3/5-isogeny
  *neighbours* of one curve at `p ≈ 2^13`, factor base = the `d` smallest
  `x`-coordinates, `m = 3`; `d_reg` and yield inside the control band;
  `H-ISO-001` is `rejected_scoped`. Its factor base has no algebraic shape,
  so its `d_reg` was pinned at 2 by construction; its walk was three steps
  from one vertex, and its unresolved confound reads *"larger isogeny
  degrees / longer walks untested"*. This design answers that confound
  completely: not three neighbours but the certified whole class.
* `RQ-ICINV-475b5e` / `EV-ICINV-343679` (GOAL-ENDO-001 lane L1): one
  complete class of 138 curves at one prime; Betti table, regularity,
  singular locus and elimination degree found class-constant *and*
  null-constant — the trap section 2 guards against. Its `refine`
  disposition asks for other functionals and other primes; F3 is such a
  functional, and the instrument here is dependency-free and runs at any
  `p < 2^24` in minutes.
* `KN-OPEN-002` (growth of the solving degree of prime-field summation
  systems): F2's closed form `h + 2` is a measured data point on the
  subgroup-factor-base variant of exactly that question.

Novelty screen: the knowledge-retrieval index (`kb/`) was queried and
answered with its documented empty-index error (`CRYPTO_KB_QDRANT_URL`
= `:memory:`), so the screen was done by grep over `ledger/`, `knowledge/`
and `analysis/` for `isogen`, `summation`, `degree of regularity`; the
records above are everything it found on this axis. Absence in an empty
index is not evidence of novelty (AGENTS.md "Knowledge retrieval policy").

## 7. Reproduction

```bash
python3 -m pytest -q tests/test_isogeny_dreg_search.py
python3 tools/isogeny_dreg_search.py --bits 13 --seed 3 --samples 64 --nulls 4 --out demo13.json
python3 tools/isogeny_dreg_search.py --p 1009 --a 0 --b 7 --no-f2 --out jzero.json   # positive control
python3 tools/isogeny_dreg_search.py --cost-model
```

Every run is deterministic in `--seed`; the JSON carries every member's
`(a, b, j)`, its functionals, the null set, the census fractions, the
number of order and modular checks passed, and timings.

## 8. Open directions (what the next session should try, not what this one claims)

1. **Other factor-base maps.** F3 with `x = g(u)` for `g` whose critical
   values are chosen relative to the model (`g = u^k + c u`), searched
   jointly over `(member, c)`. Section 4's argument only covers `u^k`.
2. **Chained systems.** `m = 3` with the subgroup equations; pre-registered
   prediction is again a closed form in `h`, to be derived before running.
3. **The smooth-degree ball at crypto `p`** (section 5), as a screening
   pass over `2^30`–`2^40` nodes with F1/F3 only.
4. **Turn the obstruction over** (`resource_check`): a functional that is
   provably class-constant is a class invariant computable from any vertex —
   which is a tool for *identifying* classes, not for attacking them; note
   it and move on.
