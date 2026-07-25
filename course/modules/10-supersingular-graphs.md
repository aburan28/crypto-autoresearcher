# Module 10 — The Supersingular Isogeny Graph

> **Goal.** Assemble everything into the star object: the ℓ-isogeny
> graph on supersingular j-invariants — small-world, Ramanujan,
> rapid-mixing — and the hard problems living on it.
>
> **Lab:** [`lab06_ss_graph.py`](../labs/lab06_ss_graph.py) builds and
> verifies these graphs; the playground's **Isogeny graph** tab lets you
> walk them by hand for p = 83, 431, 1013.

## 1. The definition

Fix a prime p (the characteristic) and a small prime ℓ ≠ p (the step
size; ℓ = 2 in the labs). The **supersingular ℓ-isogeny graph** G_ℓ(p):

* **vertices**: supersingular j-invariants over F̄_p — all in F_{p²}
  (module 08 §5), exactly ⌊p/12⌋ + ε of them;
* **edges**: ℓ-isogenies between the corresponding curves, up to
  isomorphism — i.e. pairs with Φ_ℓ(j₁, j₂) = 0, counted with
  multiplicity.

Every vertex has out-degree ℓ + 1 (the ℓ + 1 order-ℓ subgroups of
E[ℓ] ≅ (ℤ/ℓ)², module 07 §2; Vélu, module 09 §4, realizes each). Duals
make edges two-sided, so the graph is (ℓ + 1)-regular and essentially
undirected — with the by-now-familiar caveat that the extra
automorphisms at j = 0 and j = 1728 fold edges and create the loops,
multi-edges and slight directional asymmetries your lab data displays
(p = 83: j = 0 sends all three edges to j = 50; j = 1728 = 68 has a
self-loop).

Everything is connected: **one** component (a theorem of Mestre-style
"graph method" pedigree; equivalently, all supersingular curves over
F̄_p are ℓ-isogenous). Your lab proves it *empirically* every run: BFS
from a single seed finds exactly ⌊p/12⌋ + ε vertices — none missing.

## 2. Expansion: the miracle property

G_ℓ(p) is not just connected — it is an **expander**, in fact
**Ramanujan**:

**Theorem (Pizer, via Eichler/Deuring).** The adjacency operator of
G_ℓ(p) has trivial eigenvalue ℓ + 1, and every other eigenvalue λ
satisfies **|λ| ≤ 2√ℓ** — the optimal (Ramanujan) bound.

(Why one can even *prove* this: vertices correspond, through the
Deuring correspondence, to quaternion ideal classes, and the adjacency
operator becomes a Brandt matrix / Hecke operator T_ℓ on modular forms;
the eigenvalue bound is the Ramanujan–Petersson bound, proved by
Eichler–Shimura–Deligne. The deepest theorem this course touches, fully
outsourced.)

**What expansion buys, quantitatively.** A random walk's distance from
the uniform distribution shrinks by the factor (2√ℓ)/(ℓ + 1) < 1 each
step. After

  O(log p) steps

the endpoint is statistically indistinguishable from a uniformly random
vertex among all ~p/12. For ℓ = 2: ratio 2√2/3 ≈ 0.94 — each step
strips a constant fraction; a few hundred steps suffice at p ≈ 2²⁵⁶.
Lab 06's exercise 6.2 has you *measure* this mixing on p = 1013.

Working intuitions (all made honest by the theorem):

* the graph has **no small bottlenecks** — you cannot fence off a
  neighbourhood;
* **diameter O(log p)**: everything is close to everything;
* short random walks already "forget" their starting point — a walk is
  a good cryptographic randomizer.

## 3. The hard problems

**Path finding (isogeny problem).** Given supersingular j₁, j₂, find
*any* ℓ-isogeny path between them.

* The path *exists* and has length O(log p) (connectivity + diameter).
* Best known classical attacks: meet-in-the-middle / collision search
  over the ~p/12 vertices — **Õ(√p) = Õ(2^(n/2))** time (birthday
  bound; with the memory-limited van Oorschot–Wiener collision machinery
  in practice). Delfs–Galbraith: if both curves happen to be defined
  over F_p (the thin commutative sliver, module 08 Q4), paths can be
  found in Õ(p^(1/4)) — which is why protocols avoid/special-case the
  F_p-subgraph.
* Best known quantum: still exponential (Grover/claw variants ~p^(1/4)
  to p^(1/6)-ish depending on model; Kuperberg applies only to the
  *commutative* CSIDH setting, module 11). **No Shor analogue**: the
  graph walk has no visible abelian hidden subgroup — precisely the
  post-quantum selling point (contrast module 07 §4's quantum caveat).

**Endomorphism ring problem.** Given supersingular E, compute End(E)
(as a quaternion maximal order, module 08 §3).

**Theorem-shaped fact (Eichler; refined by Kohel, Petit, Wesolowski):
path finding and endomorphism-ring computation are equivalent** (under
polynomial reductions, heuristics removed by Wesolowski 2021). Knowing
End(E) for both endpoints lets you *construct* a connecting isogeny via
quaternion arithmetic (KLPT algorithm); conversely paths reveal
endomorphisms. One-way-ness of "curve ↦ its endomorphism ring" is *the*
foundational assumption of isogeny cryptography — SQIsign (module 11)
is this equivalence weaponized constructively.

**Hashing (CGL).** Charles–Goren–Lauter 2006: use the input bits to
steer a non-backtracking walk (at ℓ = 2: kernel choice ∈ {2 remaining
subgroups} per step = 1 bit per step); output the final j. Collision =
two distinct paths to one vertex = a cycle = a nontrivial endomorphism:
collision resistance *reduces to* the endomorphism problem. You can
implement CGL over lab 06's graphs in ~15 lines — module 11's capstone.

## 4. Reading the lab data like a native

From `lab06` (p = 83, seed j = 1728 ≡ 68):

```text
j = 68 → 67, 67, 68     j = 1728: self-loop + double edge (Aut ℤ/4 folding)
j = 0  → 50, 50, 50     j = 0: all three edges to one neighbour (Aut ℤ/6)
j = 38±66i ↔ conjugate  Galois-conjugate j's mirror each other
```

Notice the conjugate pair 38+66i, 38+17i (66 = −17 mod 83): Frobenius
j ↦ j^p is a graph automorphism — the graph is "mirror-symmetric" along
F_p-rational vertices, exactly the structure Delfs–Galbraith exploits.
The playground's graph tab draws p = 431's 37 vertices; find the
mirror axis by eye, then find it again in the p = 1013 layout.

## 5. Scale awareness (a habit this repository enforces)

Everything you just computed is **toy-scale**: p = 1013 has 85 vertices;
cryptographic p ≈ 2²⁵⁶ has ~2²⁵² — more vertices than atoms in the
observable universe, squared. Toy graphs are for *structure* (counts,
regularity, mixing, symmetries), never for extrapolating *security*
claims; a statement like "BFS found a path quickly" at p = 1013 says
nothing at 2²⁵⁶ where you cannot even store one level of the BFS
frontier. Keep the tiers separate in your head — the host repository's
`docs/claims-and-verification.md` exists because conflating them is the
single easiest way to fool yourself in this field.

## 6. Self-check

<details><summary><b>Q1.</b> For p = 431 (37 vertices, 3-regular): how
many edges does G₂(431) have (as an undirected multigraph, counting the
special-vertex quirks naively as half-edges)?</summary>

Directed edge count 37·3 = 111; undirected ≈ 111/2 = 55.5 — not an
integer! The parity obstruction is resolved precisely by the loops at
special vertices (a loop contributes 1 to the vertex degree count...
in fact contributes 2 half-edges at one vertex). Moral: at j = 0/1728
naive counting breaks; the graph is only "morally" undirected. Count
carefully with your lab data (`ssgraph_data.js` for p = 431) — the
directed multigraph is the trustworthy object.
</details>

<details><summary><b>Q2.</b> Why does a collision in CGL yield an
endomorphism, and of what degree?</summary>

Two distinct length-k, k′ walks j₀ → j both compose with the reverse
(dual) of the other into a closed walk j₀ → j₀: an endomorphism of
degree 2^(k+k′) (for ℓ = 2). If it's not an integer multiple [m], it's
a nontrivial element of End(E₀) — computing which is presumed hard.
(Non-backtracking matters: backtracking walks give the trivial φ̂∘φ =
[2] relations for free.)
</details>

<details><summary><b>Q3.</b> Estimate: how long must a walk on
G₂(p) be before the endpoint is ~uniform, for p ≈ 2²⁵⁶? Use the mixing
factor 2√2/3 per step.</summary>

Need (2√2/3)^k · √(#V) ≲ 2⁻λ security margin; #V ≈ 2²⁵², so
k ≳ (126 + λ)/log₂(3/(2√2)) ≈ (126 + 128)/0.085 ≈ 3000 steps for
λ = 128. Constants vary by convention; the point is Θ(log p) with a
concrete, smallish multiplier — walks this short are computable in
milliseconds, yet land uniformly in a set of size 2²⁵².
</details>

<details><summary><b>Q4.</b> The graph for ℓ = 3 is 4-regular. How many
distinct non-backtracking walks of length k leave one generic vertex,
and why does this make ℓ = 2 the natural "one bit per step" choice for
CGL while ℓ = 3 wastes entropy?</summary>

First step: 4 choices, thereafter 3 (can't take the dual back):
4·3^(k−1). For ℓ = 2: 3·2^(k−1) — after the first step exactly 2
choices = exactly 1 bit; binary input maps on cleanly. With ℓ = 3 you'd
encode in base 3 (log₂3 ≈ 1.585 bits/step) with awkward
binary-to-ternary conversion. Bandwidth vs. step cost trade-offs like
this recur throughout isogeny protocol design (SIDH used both: 2-walks
for Alice, 3-walks for Bob, on a p = 2^a·3^b·f − 1).
</details>

## 7. Where this goes

One module left: spend the graph. Key exchange on it (SIDH — and the
spectacular 2022 attack that killed it), commutative group actions
beside it (CSIDH), and signatures from its deepest structure (SQIsign
via the Deuring correspondence).

**Next:** [Module 11 — Isogeny-Based Cryptography](11-isogeny-crypto.md)
