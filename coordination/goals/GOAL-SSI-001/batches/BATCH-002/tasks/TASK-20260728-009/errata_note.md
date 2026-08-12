# Erratum to the BATCH-002 matched-baseline derivation: applying RC1, RC2, RC3, RC6

Task `TASK-20260728-009` · Goal `GOAL-SSI-001` · Batch `BATCH-002` · Role: idea-generator
Supersedes (does not edit) `TASK-20260728-005/derivation_note.md` and
`TASK-20260728-005/baseline_recommendation.yaml`, committed at snapshot
`9396d64003037b7bf108df042ab06fb852243eea` and immutable.
Mandate: `RT-20260728-007` required controls **RC1, RC2, RC3, RC6**
(`reviews/TASK-20260728-007/red_team_report.yaml`, `falsification_review.md`),
verdict `ACCEPT_WITH_MANDATORY_CORRECTIONS`.

**Epistemic label: `derivation`.** Claim tier `theory`. Nothing here is empirical.
**Zero curve computation was performed**: no isogeny evaluated, no `j`-invariant
computed, no graph sampled, no command run. Every corrected exponent below is
either derived in place where a reader can check the algebra, or cited to an
archived record with its recorded confidence.

**I did not author the artifact I am correcting.** Fresh session; I read
`derivation_note.md`, `baseline_recommendation.yaml`, `red_team_report.yaml` and
`falsification_review.md` for the first time in this task. I re-derived every
reviewer figure rather than copying it, and I record below the one place where I
disagree with the reviewer.

**Claim ceiling honoured.** This erratum claims no break, no new attack
mechanism, no completion of any `GOAL-SSI-001` criterion, and settles nothing
about CGL, SQIsign, CSIDH, `KN-OPEN-013/014/015`, concrete bit security, quantum
attacks, or torsion-image attacks. It is **not a cryptanalytic result.**

---

## 0. Summary of the four controls

| Control | Objection | Reviewer's derivation | My independent check | Outcome |
|---|---|---|---|---|
| **RC1** | F1 | `min_m max(m^{4/3}, p·m^{-2/3}) = p^{2/3}` at `m = p^{1/2}`; the rebalanced-MITM regime does not exist | **Confirmed**, and confirmed robust to a table-free sort-and-merge implementation (§1.3) | The rebalanced MITM figure is **withdrawn**; MITM is `Ω(p^{2/3})` uniformly in `m` |
| **RC2** | F2 | Restate Lemmas 4/5/7 at `d = (1+ε)log_ℓ p` with birthday parameter `|im f| = Θ(n_V)` | **Confirmed on the substance**, with one sharpening (§2.1) and **one disagreement** (§2.4, §5) | Algorithm 2's `p^{1/2+o(1)}` **does** follow after restatement |
| **RC3** | F3 | Replace Alg. 3 step 1 with `Θ(p^{1/2})` restarts of `Θ(log_ℓ p)` walks; relabel the unconditional tier `CITED` | **Confirmed**; the v1 specification was internally contradictory | Repair adopted; it is **H1′-conditional**, so the unconditional tier survives **by citation only** |
| **RC6** | F1,N1,N2,N4,N5,N7 | Correct the machine-readable fields in a superseding artifact | Done in `baseline_recommendation_v2.yaml` | 18 fields changed; full diff in §4 |

RC4 (fetch `KN-LIT-078`), RC5 (fetch `KN-LIT-094` §3) and RC7 (pre-register the
heuristic validation) are **not in this task's scope**. They are carried as named
open successors in §6 and in `open_successor_controls` of the v2 YAML. No web
fetch and no web search was performed for this task.

**All four gate verdicts G1–G4 survive, and G1 survives strengthened.** Nothing
below weakens them.

---

## 1. RC1 — recharging Algorithm 1's table-construction phase

### 1.1 What v1 charged and what it omitted

v1 Lemma 3 charged W2 to the `q` lookups (`T_wall ≥ q/m^{2/3}` at `H ≥ m`) but
charged the `m` table insertions of Algorithm 1 line 4 only as "each of `m`
entries costs one unit; `H·T ≥ m`". Those insertions are `m` *random* accesses
into an `m`-cell memory: the key of entry `s` is `j(endpoint(s))`, which under H1
is near-uniform on `V` and therefore uncorrelated with the order in which paths
are enumerated. Under W2 they are indistinguishable from the lookups. I agree
with the reviewer that this is one convention applied asymmetrically *inside* one
algorithm, and that it is the only such asymmetry in v1 (checked again in §1.4).

### 1.2 The corrected charge — derived in place

Let `m` be the table size and `q` the query count; success requires `m·q = Ω(p)`
(v1 §4.1, under H1/H4).

*Build phase.* By v1 Lemma 2 (bisection lower bound, W2) with `A = m` accesses
into `w = m` cells, the wall-clock time is `Ω(m/m^{2/3}) = Ω(m^{1/3})`. The `m`
table cells exist throughout, so `H ≥ m`. Hence

```
FC_build = H · T_build = Ω( m · m^{1/3} ) = Ω( m^{4/3} ).
```

*Query phase.* `q` lookups into the same `m`-cell memory: `T_query = Ω(q/m^{2/3})`
at `H ≥ m`, hence `FC_query = Ω(q·m^{1/3})`.

*Total.* With `q ≥ κ·p/m`,

```
FC(Alg. 1) = Ω( max( m^{4/3} , q·m^{1/3} ) ) = Ω( max( m^{4/3} , p·m^{-2/3} ) ).
```

*Optimisation.* `m ↦ m^{4/3}` is strictly increasing and `m ↦ p·m^{-2/3}` is
strictly decreasing, so the maximum of the two is minimised exactly at their
crossing:

```
m^{4/3} = p·m^{-2/3}  ⟺  m^2 = p  ⟺  m = p^{1/2},
value  (p^{1/2})^{4/3} = p^{2/3}  =  p·(p^{1/2})^{-2/3} = p^{2/3}.
```

Therefore `min_m FC(Alg. 1) = p^{2/3}`, attained at the **textbook balance**
`m = q = p^{1/2}`, and `FC(Alg. 1) = Ω(p^{2/3})` for **every** `m`.

**I confirm the reviewer's derivation. The full-cost-optimal MITM rebalance of v1
§4.4 consequence 2 does not exist.** Its table size and its full-cost exponent
were artifacts of the uncharged build phase and are **withdrawn**, together with
the second gap figure of v1 `gap_widening.full_cost_gap_vs_rebalanced_MITM` that
was computed from them. The withdrawn values are enumerated, with reasons, in
`superseded_fields` entries 2, 7, 10 and 17 of `baseline_recommendation_v2.yaml`.

### 1.3 Robustness check I added (not in the review)

The `p^{2/3}` floor is not an artifact of choosing a *hash table*. Consider the
table-free variant: enumerate the `m + q` endpoints and find the meet by sorting
the union. On a 3-D mesh of `N = m+q` cells, sorting `N` items whose destination
ranks are uncorrelated with their generation positions requires `Ω(N)` items to
cross a bisecting plane of `O(N^{2/3})` wires, so `T = Ω(N^{1/3})` at `H ≥ N` and
`FC = Ω(N^{4/3})`. Subject to `m·q = Ω(p)` we have `N = m+q ≥ 2p^{1/2}`, so
`FC = Ω(p^{2/3})` again. Two structurally different implementations of the same
meet-in-the-middle give the same floor, which is what I would want before
withdrawing a published number.

### 1.4 Does the omission affect any other algorithm? No — and one cross-check

- **Algorithm 2 (LMCS):** writes once per trail of length `L`; at polylog `w` the
  whole run performs `O(√w)` = polylog writes. Charging them changes nothing.
- **Algorithm 3 (DG):** after the RC3 repair (§3) it stores one `O(log p)`-step
  path; polylog writes.
- **Lemma 9 (the archived `p^{1/3+o(1)}` algorithm under vOW rebalancing):**
  already charged writes correctly. Its constraint `n/L ≤ w^{2/3}` *is* the
  access-throughput bound, and reads and writes occur at the same rate.

I verified Lemma 9's optimisation independently, since I am carrying its numbers
forward. With `M = N = p^{1/3+o(1)}`, golden regime, `T = Θ(M^{3/2}/√w)`,
`L = √(M/w)`, `n ≤ L·w^{2/3} = M^{1/2}w^{1/6}`:

```
FC = (n+w)·T/n = (M^{3/2}/√w)·(1 + w/n).
  n ≥ w  (memory below the crossover):  FC = Θ(M^{3/2}/√w)          — decreasing in w
  n < w  (memory above the crossover):  FC = M^{3/2}√w/n = Θ(M·w^{1/3}) — increasing in w
  crossover and optimum at w = M^{3/5}: FC = M^{3/2}/M^{3/10} = M^{6/5} = p^{2/5+o(1)}
  at w = M (as operated):               FC = M·M^{1/3} = M^{4/3} = p^{4/9+o(1)}
```

(Note: `M^{3/5}` here is a *memory budget* for the archived algorithm's claw
problem, an entirely different quantity from the withdrawn MITM table size of
§1.2. The two must not be conflated.)

Both figures reproduce. **And a genuine internal consistency check falls out:**
at `w = M` Lemma 9's `M·w^{1/3}` equals `M^{4/3}`, which is exactly RC1's
corrected build charge `m^{4/3}` applied to an `M`-cell table. RC1's recharge and
Lemma 9 are the *same* charge written twice. That independently corroborates the
reviewer's claim that Lemma 9 was already correct, and it corroborates RC1.
**C-γ (`p^{4/9}` operated, `p^{2/5}` rebalanced) survives F1 intact.**

### 1.5 Consequences carried into v2

- `FC(Alg. 1) = Ω(p^{2/3})` uniformly in `m`. **G1 is strengthened**: MITM's
  full-cost exponent strictly exceeds its step-count exponent `1/2` for *every*
  table size.
- The `F_p` full-cost gap against MITM-over-the-full-graph becomes `p^{5/12}` for
  every MITM parameterisation (`p^{2/3}` vs `p^{1/4+o(1)}` under H3′), and
  `p^{1/3}` against the H3′-free fallback (`p^{2/3}` vs `p^{1/3+o(1)}`).
- **MITM as DG's inner search inside `V_p` is unchanged at `p^{1/3+o(1)}`.**
  Re-derived: `FC = Ω(max(m^{4/3}, S·m^{-2/3}))`, minimised at `m = S^{1/2}`
  giving `S^{2/3}`, and `S = p^{1/2+o(1)}` gives `p^{1/3+o(1)}`. v1's formula and
  the corrected formula coincide at the textbook balance, so this number does not
  move; what moves is that it is now the **optimum over `m`**, not a balance
  point.
- **`honest_open_item #1` closes in Wiener's favour, with one caveat.** Applying
  the corrected formula to BSGS in a group of order `n` (table `m`, giant steps
  `q = n/m`) gives `min_m max(m^{4/3}, n·m^{-2/3}) = n^{2/3}` at `m = n^{1/2}`.
  v1 could not reconcile the smaller in-place figure its own optimisation
  produced with the `n^{2/3+o(1)}` recorded in `KN-LIT-094`; the discrepancy was
  the uncharged build phase, and with the build charged the published figure is
  recovered *as the optimum*. **Caveat I add:** what closes here is the
  **internal inconsistency inside `SSI-FC-2026`**. Whether Wiener himself states
  `n^{2/3}` as an optimum over `m` or only at `m = √n` is `RC5`, a literature
  fetch that is not in this task's scope. The v2 record therefore reads
  `closed_within_SSI_FC_2026; external attribution pending RC5`, not "closed".

---

## 2. RC2 — restating Lemmas 4, 5, 7 (and H1, H2, H4)

### 2.1 Why v1's sizing is incompatible with v1's H1 — checked two ways

v1 fixes `I = Z/(ℓ+1) × (Z/ℓ)^{d-1}`, `|I| = (ℓ+1)ℓ^{d-1} = Θ(n_V)`, i.e.
`ℓ^d = Θ(n_V)`, and then runs the birthday analysis with `M = |D| = 2|I|`. v1's
H1 asserts `TV ≤ p^{-Ω(1)}` for `d ≥ c·log_ℓ p` with `c` never quantified.

**(i) The rigorous ingredient H1 cites does not reach `p^{-Ω(1)}` at that length.**
For the `(ℓ+1)`-regular Ramanujan graph on `n_V` vertices, the standard
`L²→L¹` bound gives, for the length-`d` non-backtracking walk,

```
TV( law(endpoint), U_V )  ≤  (1/2)·poly(d)·√(n_V) · ℓ^{-d/2}
                          =  (1/2)·poly(d)·( n_V / ℓ^d )^{1/2}.
```

Demanding `TV ≤ n_V^{-δ}` forces `ℓ^d ≥ n_V^{1+2δ}/poly(d)`. So the cited bound
delivers `p^{-Ω(1)}` **only** when `ℓ^d ≥ n_V^{1+Ω(1)}` — i.e. `c > 1` strictly.
At `ℓ^d = Θ(n_V)` it delivers only `TV ≤ O(poly(d))`, which is vacuous. **I
confirm the reviewer's `c > 1` conclusion, and I regard this spectral argument as
the decisive one**, because it is a statement about the ingredient H1 names
rather than about a model.

**(ii) The counting argument, with the rigorous/model boundary drawn explicitly.**
The endpoint law is supported on at most `|I|` vertices with atoms in
`(1/|I|)·Z_{≥0}`.

- If `|I| ≤ (1-δ)·n_V`: at least `δ·n_V` vertices carry zero mass, so
  `TV ≥ δ = Ω(1)`. **Rigorous, no model needed.**
- If `|I| = A·n_V` for a constant `A ≥ 1`: the support bound is vacuous, but
  under the very random-mapping model H1's own classical companion invokes, the
  number `N_v` of paths landing on `v` is `Poisson(A)`, and

```
TV = (1/2)·Σ_v | N_v/|I| - 1/n_V |
   = (1/(2·A·n_V))·Σ_v | N_v - A |
   → (1/(2A))·E| Poisson(A) - A |   =  Ω(1),
```

  a constant independent of `p` (for `A = 1`, `(1/2)·E|Poisson(1)-1| ≈ 0.368`).
  **Model-internal, not rigorous** — but it is exactly the self-inconsistency
  that matters: H1's asserted conclusion contradicts the classical distribution
  theorem H1 invokes as its own justification.

The reviewer states (ii) as "an `e^{-1}` fraction of `V` is unhit under H1's own
random model", correctly flagging it as model-internal. I record the sharpening
that the rigorous half of the objection is (i) plus the `|I| ≤ (1-δ)n_V` case of
(ii); this is a sharpening of emphasis, not a disagreement.

**Why it is not pedantry.** With `|I| = p^{1+ε}`, v1's Lemma 5 taken literally
returns `T = Θ(√M) = Θ(p^{(1+ε)/2})`, not `p^{1/2+o(1)}`. v1's stated cost
follows from v1's stated lemmas only at the walk length where v1's stated
heuristic is false.

### 2.2 Restated heuristics

**H1′ (endpoint mixing, quantified).** Fix `ε > 0` and let
`d ≥ (1+ε)·log_ℓ p`. The endpoint of a uniformly random non-backtracking
`ℓ`-isogeny path of length `d` from a fixed supersingular `E/F_{p^2}` is within
total-variation distance `O( poly(d)·p^{-ε/2} ) = p^{-Ω(1)}` of uniform on `V`.
*Rigorous ingredient:* the Ramanujan spectral gap (`KN-TECH-024`, confidence
`established`) via the bound displayed in §2.1(i); the `(1+ε)` form is precisely
what that bound supports, which is why the quantifier had to move.
*Still a heuristic here* because the exact non-backtracking operator norm and the
`poly(d)` factor are not re-derived in this repository; both absorb into `o(1)`
under W3.
*Falsification:* an explicit family `(p, ℓ, E)` whose length-`(1+ε)log_ℓ p`
endpoint law deviates from uniform by more than `p^{-o(1)}`.
*Validation route (successor batch, RC7):* chi-square of endpoint occupancy
against uniform at increasing `d`, with crypto-scale sampling via the Deuring
correspondence as in `paper_fulltext.md` §4.2. Toy scale validates nothing at
cryptographic scale and must never be reported as if it did.

**H2′ (random-function model, on the right parameter).** `f = h∘g : D → D`
factors through the vertex set, so `im f ⊆ h(V)` and `|im f| ≤ n_V` whatever `d`
is; after one step every iterate lies in `im f`. Assume `f` restricted to `im f`
behaves, for collision statistics, like a uniformly random self-map of a set of
size `Θ(n_V)`: after `t` evaluations from random starts the expected number of
detected collisions is `Θ(t²/n_V)`.
*Change from v1's H2:* the birthday parameter is `|im f| = Θ(n_V)`, **not**
`|D| = 2|I|`.
*Validation route:* measure the collision rate against `Θ(t²/|im f|)`. A run
compared against `Θ(t²/|D|)` would appear to confirm a model that is wrong by
exactly the factor this objection identifies.

**H3′ (`F_p`-subgraph mixing).** The analogue of H1′ inside `V_p`, at walk length
`(1+ε)·log_ℓ S`. Still **weaker than H1′**: `V_p` carries class-group (CM)
structure (`KN-TECH-027`) rather than the full Ramanujan structure, and this
erratum does **not** claim H3′ follows from `KN-TECH-024`. The `F_p` verdict is
constructed not to depend on it.

**H4′ (claw multiplicity and useful fraction).** Under H1′ with
`|I| = Θ(ℓ^d) = Θ(p^{1+ε})` per side, the number of cross-side claws is
`C = Θ(|I|²/n_V) = Θ(p^{1+2ε})`; and the fraction of *detected `f`-collisions*
that are cross-side genuine claws is `Θ(1)`.
*Falsification (absorbing N8):* measured claw counts, **or the measured
cross-side fraction of detected collisions**, deviating from these by a growing
factor; or a structural bias in `g` that suppresses cross-side coincidences.

### 2.3 `h` specified — and why this is load-bearing, not cosmetic

v1 leaves `h : V → D` as a "public pseudorandom bijection-like encoding". It
cannot be a bijection (`|D| = 2|I| ≫ |V|`), and the review classifies this (N6)
as nonfatal. **I take it as load-bearing for the restated Lemma 4′** and specify
it:

```
h(v) = ( b(v), i(v) ),   b(v) ∈ {1,2} one PRF output bit,
                          i(v) ∈ I    a PRF output, both keyed on a canonical
                          encoding of j(v); cost poly(log p), absorbed in W3's o(1).
```

If `b(·)` were constant — e.g. if `h` mapped `V` into `{1}×I` — then after one
step every iterate would sit on side 1, no cross-side collision would ever be
detected, and Algorithm 2 would return `⊥` on every input. The pseudorandom side
bit is a **correctness requirement** of Algorithm 2, not a presentational detail.
This is a mild disagreement with the review's severity classification of N6; it
does not change any verdict.

### 2.4 Lemma 4′ (claw multiplicity and useful fraction) — derived in place, under H1′, H2′

*(a) Claw count.* Under H1′ both endpoint laws are within `p^{-Ω(1)}` of uniform
on `V`, so each of the `|I|²` cross-side pairs collides with probability
`(1+o(1))/n_V`, giving

```
C = Θ( |I|² / n_V ) = Θ( p^{2+2ε} / p ) = Θ( p^{1+2ε} ).
```

**Here I disagree with the review.** `red_team_report.yaml` F2
`note_on_lemma_4_robustness` says Lemma 4's *conclusion* `C = Θ(M)` "happens to
be robust: it holds both in the near-bijective regime the note actually sits in
and in the repaired regime." It does not hold in the repaired regime:
`M = |D| = 2|I| = Θ(p^{1+ε})` while `C = Θ(p^{1+2ε})`, so
`C/M = Θ(p^{ε}) → ∞` and `C = ω(M)`, not `Θ(M)`. The reviewer's *operative*
point — that claws are abundant and the `w`-independence is strengthened — is
correct and is what Lemma 5′ consumes; the literal equality is not. I therefore
retire `C = Θ(M)` rather than carrying it forward, and replace it with (a) and
(b). This is the one substantive point on which I differ from the review.

*(b) Useful fraction (this replaces v1's underived parenthetical, N8).* Take two
distinct covered points `y ≠ y'`. `f(y) = f(y')` iff `h(g(y)) = h(g(y'))`, which
has two disjoint causes:

- `g(y) = g(y')` — a genuine claw — with probability `(1+o(1))/n_V = Θ(p^{-1})`
  under H1′;
- `g(y) ≠ g(y')` but `h` maps them together, with probability `O(1/|D|) =
  O(p^{-1-ε})` under the near-uniformity of `h`.

The second cause is smaller by `Θ(p^{-ε})`, so a `1 - O(p^{-ε})` fraction of
detected `f`-collisions are genuine claws. Among genuine claws the two sides are
opposite with probability `1/2 - o(1)`, because each covered point's side bit is
`b(·)` evaluated at *its predecessor's* endpoint and is therefore independent of
the endpoint that collides (§2.3). Hence

```
Pr[ a detected f-collision is a usable cross-side claw ] = 1/2 - o(1) = Θ(1).  ∎
```

### 2.5 Lemma 5′ (cost of collecting `k` detected collisions with memory `w`)

Identical to v1 Lemma 5 with the birthday parameter replaced,
`M' := |im f| = Θ(n_V) = Θ(p)`, under H2′ and the vOW parameterisation
`L = max(1, √(M'/w))`:

```
T(k) = √( 2·M'·k )        for k ≤ w/2      (one function version suffices)
T(k) = 2·k·√( M'/w )      for k ≥ w/2      (⌈2k/w⌉ versions)
```

*Proof.* Within one version of `f`, `w` stored trails of length `L` cover
`t = wL = √(M'w)` evaluations; under H2′ the expected number of detected
collisions among `t` covered points is `t²/(2M')`. Solving `t²/(2M') = k` gives
`t = √(2M'k)`, admissible while `t ≤ √(M'w)`, i.e. `k ≤ w/2`. Beyond that,
re-key `f` and pay `√(M'w)` per further `w/2` collisions. The branches agree at
`k = w/2`. ∎

*Cross-check, unchanged by the restatement.* At `k = M'/2` (one golden collision)
`T = √(M'³/w)`, which is the van Oorschot–Wiener tradeoff quoted **verbatim** at
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 39: *"solves a claw-finding
problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with
memory w"*. I read that line directly in this session.

### 2.6 Lemma 6 (correctness) — unchanged, and Lemma 7′ (cost)

**Lemma 6** is untouched by the restatement: if line 7 of Algorithm 2 succeeds,
`RECONSTRUCT` returns a genuine isogeny `E_1 → E_2` of degree dividing `ℓ^{2d}`
described by `2d = 2(1+ε)·log_ℓ p = Θ(log p)` steps — polynomial description
size, hence a valid solution to Problem 1. Correctness needs no heuristic.

**Lemma 7′ (cost, under H1′, H2′, H4′, W1–W4, W6).** By Lemma 4′(b) the expected
number of detected collisions that must be sifted is `k = Θ(1)`. By Lemma 5′ with
`k = Θ(1)` and any `w ≥ 2`,

```
T_evals  = Θ( √M' ) = Θ( p^{1/2} ),   independent of w
T_steps  = Θ( √M' · d ) = p^{1/2+o(1)}   ℓ-isogeny steps
memory   = w, free, may be polylog;   H = n + w
W2 charge: one table access per trail of length L = √(M'/w) = p^{1/2-o(1)} at
           polylog w, so n/L ≤ w^{2/3} holds with wide margin
FC(Alg. 2) = (n+w)·p^{1/2+o(1)}/n = p^{1/2+o(1)}.  ∎
```

### 2.7 Does Algorithm 2's `p^{1/2+o(1)}` follow from its own lemmas after the restatement?

**Yes.** The headline is unchanged and the `w`-independence is *strengthened*
(`C = Θ(p^{1+2ε})` super-abundant, useful fraction `Θ(1)`, `k = Θ(1)` with more
margin than v1 claimed). What changed is the **justification**, not the number.

I record why the defect was invisible in v1: at v1's sizing, `|D| = 2|I| = Θ(p)`
coincided *numerically* with `|im f| = Θ(n_V) = Θ(p)`, so the wrong birthday
parameter produced the right exponent. Decoupling `d` from the index-space size
is what exposes it.

The same restatement applies verbatim to v1 §6.2's instantiation inside `V_p`:
index space `|I_p| = Θ(S^{1+ε})`, birthday parameter `|im f_p| = Θ(S) =
p^{1/2+o(1)}`, so `T_steps = Θ(√S)·Θ(log p) = p^{1/4+o(1)}` at polylog memory,
under **H3′**. Unchanged number, corrected derivation.

---

## 3. RC3 — Algorithm 3 step 1, and the `CITED` relabel

### 3.1 The defect

v1 Algorithm 3 step 1 reads *"random-walk in the `F_{p^2}` graph until an
`F_p`-rational curve is reached. `Θ(n_V/S) = p^{1/2+o(1)}` steps, `O(1)` memory:
nothing is stored"*, and step 3 reads *"compose the three pieces."* I confirm the
reviewer: these are contradictory, and the contradiction is exactly what v1's own
Proposition 10 falsifies. A walk that stores nothing cannot be composed; a stored
walk of `Θ(p^{1/2})` steps certifies an isogeny of degree `ℓ^{Θ(p^{1/2})}` whose
only representation is the trail, at `Θ(p^{1/2})` memory. v1 applied a
falsification standard to a rival construction that it did not apply to its own
baseline, and v1 §6.1's *"step 1's memory profile is derived here"* is a
derivation from an inconsistent specification.

### 3.2 Algorithm 3′ step 1 — the repair, derived in place

```
Algorithm 3' step 1 (descent to V_p, restart form)
 for i in {1,2}:
 1. repeat:
 2.     run a FRESH non-backtracking walk of length d_0 = (1+eps)*log_ell(p) from E_i
 3.     test whether the endpoint is F_p-rational (j in F_p; a test on the
        canonical F_{p^2} representation, cost poly(log p))
 4.     if not, DISCARD the whole path and restart
 5. until success; keep the successful O(log p)-step path
```

*Cost.* Under **H1′** the endpoint of each restart is within `p^{-Ω(1)}` of
uniform on `V`, so each restart succeeds with probability
`(1+o(1))·S/n_V = p^{-1/2+o(1)}`. Expected restarts `p^{1/2+o(1)}`; each costs
`d_0 = Θ(log p)` steps; total `p^{1/2+o(1)}` steps — the step count is unchanged.

*Memory.* One in-progress path plus one stored successful path: `Θ(log p)` graph
elements = **polylog**.

*Output.* A path of `Θ(log p)` `ℓ`-isogenies, of polynomial description size,
which step 3 can actually compose. Proposition 10 no longer applies to Algorithm
3′, because the object emitted is `Θ(log p)` steps long rather than
`Θ(p^{1/2})`.

### 3.3 The consequence the repair carries: `CITED`, not `DERIVED`

The repair is **conditional on H1′** — the hitting probability `S/n_V` is exactly
the near-uniformity statement. Therefore:

- The in-note reconstruction of the classical `F_{p^2}` baseline's memory profile
  is `DERIVED_CONDITIONAL_ON_H1_PRIME`, not unconditional.
- The **`F_{p^2}` unconditional tier's memory profile is recorded as `CITED`**,
  resting on `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 39, which I read
  directly in this session: *"This allows one to interpolate between the
  `p^{1/3+o(1)}` high-memory algorithm presented here and the classic
  `p^{1/2+o(1)}` algorithms with polynomial memory like [21]."* Reading
  "polynomial memory" against an input size of `log p` as `poly(log p)` is
  standard but **is a reading**; v2 labels it an interpretation of a quotation,
  not a quotation.
- **C-α is relabelled `CITED`**, not `DERIVED`, until `KN-LIT-078` is read
  (RC4). C-α's *conclusion* survives — a premise needs only one solid
  counter-fact, and the archived sentence is one.
- The `F_p` verdict is untouched: its inputs are already `F_p`-rational, so step
  1 is never executed.

---

## 4. RC6 — every field whose value changed between v1 and v2

Machine-readable form: `baseline_recommendation_v2.yaml`, block
`superseded_fields`. Summary, 18 entries:

| # | v1 field | v1 value | v2 value | Driver |
|---|---|---|---|---|
| 1 | `cost_convention.asymmetric_charge_audit` | asserted that the producer found no asymmetry | `ONE_FOUND_AND_CORRECTED` (F1, §1) | N4 |
| 2 | `regime_F_p2.exponent_table` row "MITM, full-cost-optimal" | a rebalanced table size with `full_cost_exponent: 0.6` | **row withdrawn**; no such regime exists | F1 |
| 3 | `regime_F_p2.exponent_table` row 1 basis | "textbook balance" | balance **is** the optimum; `Ω(p^{2/3})` uniform in `m` | F1 |
| 4 | `regime_F_p2.exponent_table` row 3 | LMCS **and** DG in one row, one basis | **split** into two rows with separate bases | N5 |
| 5 | LMCS row basis | "derived in place (Lemmas 4–7)… independently attested" | `DERIVED_CONDITIONAL_ON_H1_PRIME`; the archived attestation covers `[21]`, not Algorithm 2 | N5, F2 |
| 6 | DG-general row basis | (merged) | memory profile `CITED` (line 39); reconstruction `DERIVED_CONDITIONAL_ON_H1_PRIME` | F3 |
| 7 | `regime_F_p.gap_widening.full_cost_gap_vs_rebalanced_MITM` | a second gap figure computed from the withdrawn rebalance | **withdrawn** — the rebalance does not exist | F1 |
| 8 | `regime_F_p.gap_widening.full_cost_gap_vs_textbook_MITM` | `p^{5/12}` (one parameterisation) | `p^{5/12}` for **every** `m`; `p^{1/3}` against the H3′-free fallback | F1 |
| 9 | `regime_F_p.mitm_ever_competitive` | an unqualified `false` | key retired; `mitm_over_full_graph_ever_competitive: false` + new `mitm_as_inner_search_within_Vp` | N1 |
| 10 | `regime_F_p.exponent_table` row "MITM on the full graph" | a lower bound below `p^{2/3}` | `Ω(p^{2/3})` | F1 |
| 11 | `heuristics_relied_on.H1/H2/H3/H4` | unquantified `c`; birthday parameter `|D|` | H1′/H2′/H3′/H4′ (§2.2) | F2 |
| 12 | `low_memory_analogue.walk_law` | `|I| = Θ(n_V)`, `h` "bijection-like" | `|I| = Θ(p^{1+ε})`, `h` specified with a pseudorandom side bit | F2, N6 |
| 13 | `low_memory_analogue.any_vs_golden_collision_accounting` | `C = Θ(M)`, `k = Θ(1)` | `C = Θ(p^{1+2ε}) = ω(|D|)`; operative quantity is the useful fraction `Θ(1)` ⇒ `k = Θ(1)` | F2 + my §2.4 dissent |
| 14 | `new_attack_mechanism_justification` item (3) | "the `p^{2/5}` figure RAISES the effective cost" | replaced (§7); the rebalance **lowers** full cost from `p^{4/9}` to `p^{2/5}` | N2 |
| 15 | `citations.knowledge_corpus` | includes `KN-TECH-044` | `KN-TECH-044` dropped (cited, never used) | N7 |
| 16 | `decision_relevant_corrections.C_alpha` | asserted from the reconstruction | status `CITED`, not `DERIVED` | F3, R3-hardest-press |
| 17 | `gate_self_check.honest_open_items[0]` | "not settled; untested expectation" | `closed_within_SSI_FC_2026`; external attribution pending RC5 | F1 |
| 18 | `regime_F_p.matched_baseline_verdict`, `what_a_future_candidate_must_beat` | flat `p^{1/4+o(1)}`; "beat `p^{2/5+o(1)}` full cost" | `confidence: relayed_from_abstract` inline; operative thresholds are the **time** tiers, full-cost figures provisional above a superpolynomial `o(1)` | N3, CM3 |

The four strings the review forbade appear in v2 only inside
`superseded_fields`, each explicitly marked withdrawn with its reason, and
nowhere as a live claim.

---

## 5. Where I disagree with the review

The review is not infallible and I record my differences plainly.

1. **`C = Θ(M)` is not robust to the restatement (§2.4).** `red_team_report.yaml`
   F2 `note_on_lemma_4_robustness` asserts it holds "in the repaired regime".
   It does not: `C = Θ(p^{1+2ε})` against `M = Θ(p^{1+ε})`, so `C = ω(M)`. The
   reviewer's operative conclusion is right and is strengthened; the stated
   equality is wrong and I retire it rather than carry it. This is the one
   substantive disagreement.
2. **N6 (`h` unspecified) is load-bearing, not cosmetic (§2.3).** The review
   classes it nonfatal on the ground that line 7 re-tests `g(y) = g(y')`. That
   handles `h`-collisions but not the side bit: an `h` whose side component is
   constant makes Algorithm 2 return `⊥` always. I specify `h` rather than defer
   it.
3. **`honest_open_item #1` closes only *within* the convention (§1.5).** The
   review says it "closes in Wiener's favour", pending RC5 confirmation. I agree
   with the direction, and I narrow the claim: what is settled here is the
   internal inconsistency of `SSI-FC-2026`. The attribution question — whether
   `KN-LIT-094` states `n^{2/3}` as an optimum over `m` — is untouched by any
   pen-and-paper step and remains open.
4. **A sharpening, not a disagreement (§2.1).** Of the review's two arguments
   against H1 at `ℓ^d = Θ(n_V)`, the spectral one is rigorous about the cited
   ingredient; the unhit-fraction one is rigorous only when `|I| ≤ (1-δ)n_V` and
   is otherwise model-internal. The review does flag it as model-internal; I
   record which half carries the weight so a downstream reader does not
   over-attribute.

I agree with every other element of F1, F2, F3, N1–N9, and with the review's
`new_attack_mechanism_detected: false`.

---

## 6. The sourcing gap, recorded rather than papered over

The whole `F_p` regime relays through `KN-TECH-029` → `KN-LIT-078`. I read
`knowledge/literature/KN-LIT-078.md` in this session. Its own entry states,
verbatim:

> "Full paper not read; the p^{1/2} / p^{1/4} costs relayed from the abstract
> (hence confidence: reported). The IACR ePrint number could NOT be confirmed and
> is omitted (the sometimes-cited "2013/506" is a DIFFERENT paper); identifiers
> are the DCC DOI 10.1007/s10623-014-0010-1 and arXiv:1310.7789, both confirmed
> via search."

And `knowledge/techniques/KN-TECH-050.md` states, verbatim:

> "A `GOAL-SSI-001` BATCH-002 derivation may use it to structure the comparison
> and **must obtain every quoted figure from the papers themselves.**"

The `F_{p^2}` figures satisfy that instruction (archived primary text). **The
`F_p` figures do not.** v2 therefore carries
`confidence: relayed_from_abstract` inline on every `F_p` figure —
`p^{1/4+o(1)}` and `S = |V_p| = p^{1/2+o(1)}` — rather than stating them flatly.

**RC4 is not in this task's scope** and I have no authorization for a literature
fetch here. It is carried as an open successor:

- **RC4 (open).** Obtain `KN-LIT-078` (arXiv:1310.7789 / DOI
  10.1007/s10623-014-0010-1) from the primary source and record (a) the actual
  memory profile of the inner `F_p` search and (b) whether the descent to `V_p`
  is one long walk or restarts — i.e. whether §3.2's repair is what the authors
  do or an in-repo substitute. **This is a precision control, not a verdict
  control:** the `F_p` ranking is robust either way, since the H3′-free fallback
  `p^{1/3+o(1)}` still beats `p^{1/2}`.
- **RC5 (open).** Read `KN-LIT-094` §3's BSGS derivation; confirm whether
  `n^{2/3}` is stated at `m = √n` or as an optimum over `m` (§1.5).
- **RC7 (open, successor batch only).** Pre-register the H1′/H2′/H4′ validation,
  stating up front that toy scale validates nothing at cryptographic scale.

Also unresolved and recorded, not hidden: whether the `F_p`-rationality test in
§3.2 matches Delfs–Galbraith's published descent criterion is **unverified** —
`KN-LIT-078` was not read.

---

## 7. `new_attack_mechanism_detected: false` — my own verdict

I reached `false` independently, and I do **not** use v1's withdrawn item (3).

1. Algorithm 2, restated, reaches `p^{1/2+o(1)}` at polylog memory. The archived
   primary text already places "the classic `p^{1/2+o(1)}` algorithms with
   polynomial memory like [21]" at exactly that point (line 39, read directly).
   Matching a known exponent at a known memory profile is an `adaptation`.
2. The `w`-independence result is a **negative** result about attacks: memory
   buys nothing when claws are abundant. A theorem that a resource does not help
   is not an attack mechanism. RC2 strengthens it, which strengthens the
   negative.
3. RC1 makes MITM **more** expensive (`Ω(p^{2/3})` uniformly) than v1 claimed,
   for an algorithm already dominated in both regimes. Raising the cost of a
   dominated algorithm is not an attack mechanism. The rebalanced MITM table size
   v1 cited at this point is withdrawn under RC1 and does not exist.
4. **Replacing v1's unsound item (3), per N2.** The `p^{2/5+o(1)}` rebalance
   **does lower** a live attack's full cost, from `p^{4/9+o(1)}` as operated to
   `p^{2/5+o(1)}` at `w = p^{1/5+o(1)}`. I state that plainly rather than the
   withdrawn claim that it "raises the effective cost". It is nevertheless not
   target-class under `docs/target-result-profile.md` rule A1, on four grounds:
   (a) it is a parameter choice on a time–memory tradeoff the source text itself
   offers and explicitly invites (line 39); (b) it **raises** the time exponent
   from `1/3` to `2/5`, and the goal's baselines are quoted in time; (c) it is
   conditional on that paper's Heuristic 1, which this program has neither
   validated nor challenged, above a superpolynomial `o(1)` its own authors
   disclose ("the overhead hiding in the o(1) term is superpolynomial", line 39),
   so no concrete-parameter conclusion follows; (d) the best-known time exponent
   for the hard problem is unchanged at `1/3`.
5. The any-claw/golden-claw distinction **explains** why the exponents are what
   they are; it produces no algorithm that beats a baseline. It remains the
   artifact's genuine content and is present in no archived corpus entry I could
   find — but explanatory content is not a mechanism.
6. `PROP-11` (batched re-randomisation) remains correctly falsified in place. I
   did not re-verify Theorem 1.5 against the primary text in this task beyond
   reading lines 1–45; the review reports verifying it at line 81 (`RS1`) and I
   carry that as **the review's verification, attributed, not as mine**.
7. I looked for a mechanism inside this erratum's scope and found none. That is
   **absence of evidence within one derivation, not an impossibility claim** over
   the literature. This erratum declares no direction impossible.

**Consequence.** BATCH-002 satisfies no `GOAL-SSI-001` completion criterion. The
goal record requires that both `TASK-20260728-005` and `TASK-20260728-007`
independently report a new attack mechanism; both report `false`, and so does
this erratum. **Carried caveat:** producer, reviewer and this session all resolve
to `claude-opus-5` on the default backend, so this is three sessions, not three
independently-resolved judgements, and no future `GOAL-SSI-001` closure
attestation may count them as such.

---

## 8. What is preserved

All four gate verdicts survive; the errors ran in the conservative direction.

- **G1** — MITM's full cost strictly exceeds its step-count exponent.
  **Strengthened**: `Ω(p^{2/3})` uniformly in `m`, versus a step count of
  `p^{1/2}`. v1 asserted this only at two named table sizes, one of which is
  withdrawn under RC1; the corrected statement holds for every table size.
- **G2** — MITM over the full graph is never competitive on `F_p`-rational
  instances. **Unchanged.** Its proof runs off Lemma 1 (`FC ≥ T_steps`, from W1
  and W6 alone) and is untouched by F1, F2 and F3. `RT-20260725-503` **F2 is
  upheld**, not answered.
- **G3** — the low-memory analogue is **DEFINED**, not falsified, and survives
  **restated** (§2). Proposition 10's falsification of the naive continuous
  graph-walk variant survives and now also bites v1's own Algorithm 3, which §3
  repairs.
- **G4** — one verdict per regime; the two-tier `F_{p^2}` baseline and the `F_p`
  Delfs–Galbraith baseline both stand, with the labelling corrections of §3.3
  and §6.
- The **any-claw / golden-claw accounting** is the artifact's genuine content and
  is present in no archived corpus entry I could find. RC2 strengthens it.
- **C-β** (`KN-TECH-029` is stale against this repository's own archived primary
  text) survives intact and remains the single most decision-relevant output.
- **C-γ** survives F1 intact (§1.4), conditional on the source's Heuristic 1.

---

## 9. Limits

- This is cost-model hygiene plus one corpus-currency correction. **Not a
  cryptanalytic result.** It breaks nothing and establishes no bit security for
  any parameter set.
- Every `p^{1/3+o(1)}`, `p^{4/9+o(1)}` and `p^{2/5+o(1)}` figure remains
  **conditional on Heuristic 1** of
  `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`. Dropping that qualifier
  downstream is a claim-tier violation.
- H1′–H4′ are **unvalidated**. This task computed nothing and supports no
  empirical claim at any tier.
- Under `docs/target-result-profile.md` rule A1, nothing here is target-class:
  constant-factor and log-cofactor results are excluded, and no exponent of a
  named hard problem moves.
- All of v1's `uncharged_residue` is inherited unchanged, with two updates: item
  10 (Delfs–Galbraith's published memory profile) is now the explicit RC4
  successor, and item 2 (W2's achievability half) is unaffected, since RC1's
  correction is a **lower** bound and therefore does not depend on it.
- Novelty screening here was against `ledger/`, `coordination/` and `inputs/`
  only. No web literature check was performed, so any novelty statement is at
  best `novelty_status: unverified` against the open literature.
- One unreplicated erratum by one producer, in a session that shares a resolved
  model with both the artifact it corrects and the review that mandated it.

---

## 10. Inference and provenance

Requested policy `research-deep` (idea-generator). Resolved model
`claude-opus-5` (self-reported runtime identity). `model_verified: false` — this
session has **no shell**, ran no `python3 -m orchestration.adapter doctor
--probe` and no `adapter resolve`, so per `AGENTS.md` the identifier is
unverified configuration. `fallback_used: unknown` — no adapter resolution record
was produced for this session; recorded as unknown rather than guessed.
`reasoning_effort: policy_default`. `independent_session: true` — fresh session;
I authored no part of the v1 artifacts or of `RT-20260728-007`.
`model_independence: not achieved` — see §7.

No `TASK-20260728-009` card exists anywhere in this worktree (checked by
repository-wide content search, which returned no occurrence of the identifier);
the handoff reached this session in-conversation. Recorded rather than asserted
to be archived.

Tool limits: read-only tools plus file writes. No commands executed, no git
queries, **no web fetch and no web search**, no probe. **Zero curve computation.**
Nothing written outside
`coordination/goals/GOAL-SSI-001/batches/BATCH-002/tasks/TASK-20260728-009/`. No
ledger, knowledge, evidence, decision, or hypothesis record created or edited; no
official state changed; no commit made. The immutable `TASK-20260728-005`
artifacts were read and **not modified**.

Files read in this session: the two `TASK-20260728-005` artifacts; the two
`TASK-20260728-007` review artifacts; `ledger/goals/GOAL-SSI-001.yaml`;
`ledger/decisions/DEC-20260725-002.yaml`; `knowledge/literature/KN-LIT-078.md`;
`knowledge/techniques/KN-TECH-050.md`;
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` lines 1–45; `AGENTS.md`;
`agents/idea-generator.md`.
