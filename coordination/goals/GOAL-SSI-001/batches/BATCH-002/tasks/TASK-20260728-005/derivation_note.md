# Matched classical baseline for supersingular isogeny path-finding under one cost convention

Task `TASK-20260728-005` · Goal `GOAL-SSI-001` · Batch `BATCH-002` · Role: idea-generator
Discharges the BATCH-002 derivation gate opened by `DEC-20260725-002` under red-team
disposition `ADMIT_BASELINE_DERIVATION_FOR_BATCH_002` (`RT-20260725-503`).

**Epistemic label: `derivation`** per `docs/claims-and-verification.md` §"Refutation
artifacts". Nothing here is proved in the machine-checked sense, nothing here is
empirical, and **zero curve computation was performed**: no isogeny was evaluated,
no j-invariant computed, no graph sampled. Every statement below is either (i)
cited to an archived record or archived primary text, (ii) derived in place from
stated assumptions so a reader can check the algebra, or (iii) explicitly labelled
an **untested expectation**.

**Claim ceiling honoured.** This note claims no break, no sub-`p^{1/4}`
endomorphism-ring attack, no completion of any `GOAL-SSI-001` criterion, and
settles nothing about CGL, SQIsign, CSIDH, `KN-OPEN-013/014/015`, concrete bit
security, quantum attacks, or torsion-image attacks.

---

## 0. Executive summary of verdicts

| Gate | Verdict |
|---|---|
| **G1** `F_{p^2}` MITM | Full-cost exponent **strictly exceeds** step-count exponent under the named wiring model: `2/3` at the textbook balance and `3/5` after full-cost-optimal rebalancing, against a step-count exponent of `1/2`. It collapses to `1/2` only under a unit-cost random-access assumption, which is exactly the assumption the convention rejects. (§4) |
| **G2** `F_p` regime, objection **F2** | **F2 is discharged and upheld.** MITM is *never* competitive on `F_p`-rational instances under the shared convention. Proved in place from Lemma 1 (full cost ≥ step count): MITM's full cost ≥ `p^{1/2}` > `p^{1/4+o(1)}` ≥ Delfs–Galbraith's full cost, for *every* wiring model satisfying W1. Charging memory does not change the `F_p` ranking; it widens the gap from `p^{1/4}` to `p^{5/12}`. (§6) |
| **G3** low-memory analogue | **DEFINED**, not falsified — Algorithm 2 below, with walk law, distinguished-point predicate, collision-to-path reconstruction, and any-claw accounting all explicit. Cost `p^{1/2+o(1)}` steps at polylog memory. Separately, the *naive* continuous-graph-walk variant is **falsified in place** (Prop. 10: its output is an isogeny of degree `ℓ^{Θ(p^{1/2})}`, so it must store what it was built to avoid). (§5, §5.6) |
| **G4** recommendation | One verdict per regime in `baseline_recommendation.yaml`; uncharged residue in §9. Pre-registered falsification outcome **(3) fired in its first clause**: Delfs–Galbraith (and its memory-light equivalent) dominates MITM under every convention examined. Outcomes (1) and (2) did **not** fire. But the baseline identity *does* change — for a reason unrelated to memory charging (§7). |
| **G5** new mechanism | **`new_attack_mechanism_detected: false`.** Justification in §8, including one candidate mechanism generated and then **falsified in place** (Prop. 11). |
| **G6** limits | §9, §10. |

The single most decision-relevant finding is **not** a cost-model correction. It is
that `KN-TECH-029`'s statement of the matched baseline is **stale against this
repository's own archived primary text**: `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`
places the best known `F_{p^2}` complexity at `p^{1/3+o(1)}` (conditional on that
paper's Heuristic 1) and states that the *classic* `p^{1/2+o(1)}` algorithms already
use **polynomial memory**. Both facts, taken together, dissolve the premise of
`IDEA-20260725-001`: there is no memory charge to levy against the classical
`F_{p^2}` baseline, because that baseline was never the memory-heavy algorithm.

---

## 1. Problems (numbered, with input encoding and what counts as a solution)

**Problem 1 (`SSI-Path-F_{p^2}`).** Given `p` prime and two supersingular elliptic
curves `E_1, E_2 / F_{p^2}` given by their `j`-invariants, output an isogeny
`E_1 → E_2`. A solution is an isogeny of **polynomial description size**: a
sequence of `poly(log p)` isogenies of degree `≤ B = poly(log p)`, or an
equivalent efficient representation. No torsion images under a secret isogeny are
supplied and no degree is prescribed.

**Problem 2 (`SSI-Path-F_p`).** Problem 1 restricted to inputs where both `E_1`
and `E_2` are `F_p`-rational.

**Problem 3 (`SSI-Path-fixed-degree`, = CSSI).** Problem 1 with the additional
promise that the sought isogeny has a **fixed known degree** `d` (in SIDH,
`d = ℓ_A^{e_A}`). Recorded only to keep it separate: it is a different problem and
its literature (`KN-LIT-124`, `KN-LIT-125`, `KN-LIT-132`) does **not** transfer to
Problems 1–2. §5.4 shows exactly where the transfer breaks.

Notation. `V` = vertex set of the supersingular `ℓ`-isogeny graph over `F_{p^2}`,
`n_V = |V| ≈ p/12`, `(ℓ+1)`-regular and Ramanujan (`KN-TECH-024`, confidence
`established`). `V_p ⊂ V` = the `F_p`-rational subgraph, `|V_p| = S`. `KN-TECH-029`
records `S` as "`~sqrt` of the full graph", i.e. `S = p^{1/2+o(1)}`; taken as
**cited, reported**, not re-derived here.

---

## 2. The cost convention: `SSI-FC-2026`

Exactly one convention, applied identically to every algorithm compared. Any
asymmetric charge invalidates the comparison, so the convention is stated as
numbered assumptions and every later exponent names the ones it uses.

**W1 (full cost).** The cost of an attack is `FC = H · T_wall`, the quantity of
hardware multiplied by the wall-clock time it is occupied. Source: Wiener's full
cost, `KN-LIT-094` (`confidence: established`, `citation_verified: read`), as
relayed by `KN-TECH-035`.

**W2 (three-dimensional memory, bisection-limited).** A memory of `w` cells is laid
out in three spatial dimensions. Random accesses to it are limited by bisection
bandwidth: any bipartition of the layout is crossed by `O(w^{2/3})` wires, so a
batch of `w` random accesses requires time `Ω(w^{1/3})`, and `Θ(w^{1/3})` is
achievable by mesh routing. **Access throughput is therefore `Θ(w^{2/3})` per unit
time.** The lower-bound half is derived in place (Lemma 2); the matching upper
bound is taken as a modelling assumption, not proved here.
*Falsification of W2:* if achievable throughput is `Θ(w)` (unit-cost RAM), every
full-cost exponent in §4 collapses to its step count; if it is `Θ(w^{2/3}/log w)`,
only `o(1)` terms move. §4.4 records that W2 reproduces Wiener's published BSGS
figure exactly at the textbook balance, which is the strongest consistency check
available inside this repository.

**W3 (unit of work).** One unit = one `ℓ`-isogeny step: evaluating the `ℓ+1`
non-backtracking neighbours of a curve via `Φ_ℓ`, which costs `(ℓ + log p)^{O(1)}`
field operations (archived: `paper_fulltext.md`, proof of Lemma 3.3). All such
polynomial cofactors are absorbed into `o(1)` uniformly for every algorithm.

**W4 (what is charged).** Table construction; table storage for its whole
occupancy; every memory access under W2; instance re-randomisation; the conversion
of a found path into an efficient isogeny representation; processors and their
occupancy time.

**W5 (what is not charged).** Quantum queries, quantum memory, and quantum gates
(out of scope by the frozen card; `KN-OPEN-014` lane). Torsion-image oracles
(forbidden; SIDH regime). Energy, cooling, latency and bandwidth effects beyond
the W2 abstraction, and the `o(1)`/constant terms (`KN-TECH-035` applicability
limits are inherited verbatim).

**W6 (parallelism).** `n` processors may be used; hardware is `H = n + w` and
`T_wall ≥ T_steps / n`, subject to the memory-throughput constraint of W2.

Name to be quoted by downstream records: **`SSI-FC-2026`**. It is the isogeny-graph
instantiation of `wiener_full_cost_plus_isogeny_step_count`
(`IDEA-20260725-001.full_cost_boundary.cost_convention_name`), made numerically
specific.

---

## 3. Heuristics (numbered, standalone, each with a falsification condition)

Per `docs/target-result-profile.md` A2/C3–C5. Every complexity statement below
names the heuristics it depends on. **None of these is validated here; this batch
computes nothing.**

**Heuristic H1 (endpoint mixing).** There is `c > 0` such that for
`d ≥ c·log_ℓ p`, the endpoint of a uniformly random non-backtracking
`ℓ`-isogeny path of length `d` from a fixed supersingular `E/F_{p^2}` is within
total-variation distance `p^{-Ω(1)}` of uniform on `V`.
*Rigorous ingredient:* the graph is Ramanujan (`KN-TECH-024`, established), so its
non-trivial spectral gap is `1 - 2√ℓ/(ℓ+1)`.
*Classical companion:* the standard expander-mixing / rapid-mixing bound for
Ramanujan graphs. The archived primary text uses the same fact with walk length
`n = O(log p)`, citing [37] and [6, Lemma 14] (`paper_fulltext.md`, proof of
Theorem 1.1).
*Falsification:* an explicit supersingular curve family and `ℓ` for which the
length-`c log_ℓ p` endpoint distribution deviates from uniform by more than
`p^{-o(1)}`.
*Validation route (for a successor batch, not this one):* sample endpoint
`j`-invariants of length-`d` walks at toy and mid scale and compare the empirical
occupancy histogram against uniform with a chi-square statistic, at increasing `d`;
crypto-scale validation would require the Deuring correspondence rather than direct
walks, exactly as in `paper_fulltext.md` §4.2.

**Heuristic H2 (random-function model for the collision map).** The map `f`
defined in Algorithm 2 behaves, for the purpose of collision statistics, like a
uniformly random self-map of its domain `D`: after `t` evaluations from random
starts, the expected number of detected collisions is `Θ(t²/|D|)`.
*Rigorous ingredient:* H1 makes the endpoint component of `f` near-uniform.
*Classical companion:* the birthday/functional-graph statistics of random mappings,
which is exactly the assumption under which the van Oorschot–Wiener analysis is
stated (`KN-LIT-012`, `KN-TECH-006`; both record it as heuristic).
*Falsification:* a measured collision rate differing from `Θ(t²/|D|)` by a growing
factor at feasible scale, or a structural bias in `f` (e.g. an arithmetic
obstruction making cross-side claws rarer than Lemma 4 predicts).

**Heuristic H3 (`F_p`-subgraph mixing).** The analogue of H1 inside `V_p`: a
suitable walk in the `F_p`-rational subgraph equidistributes on `V_p` in
`O(log p)` steps.
*Status:* **weaker than H1.** The `F_p`-rational subgraph carries class-group
(CM) structure rather than the full Ramanujan structure of `V`
(`KN-TECH-027` records the class-group action on `F_p`-rational supersingular
curves). This note does **not** claim H3 follows from `KN-TECH-024`.
*Falsification:* an obstruction to equidistribution of the relevant `F_p` walk, or
a published memory profile of Delfs–Galbraith's inner search that contradicts the
polylog-memory reconstruction of §6.2.

**Heuristic H4 (claw multiplicity).** Under H1, the number of cross-side claws in
Algorithm 2 is `C = Θ(|I_1|·|I_2| / n_V)` (Poisson heuristic for independent
near-uniform endpoints).
*Falsification:* measured claw counts deviating from this by a growing factor.

`KN-TECH-050` is the governing corpus discipline for all of the above: *never name
a baseline without naming the field regime, the memory model, and the degree
constraint.* This note names all three throughout.

---

## 4. G1 — MITM on the `F_{p^2}` graph under `SSI-FC-2026`

### 4.1 Algorithm 1 (meet-in-the-middle, stated so lemmas can bind to it)

```
Algorithm 1: MITM path search on the F_{p^2} graph
Require: E_1, E_2 supersingular over F_{p^2}; table budget m; query budget q.
Ensure : an isogeny E_1 -> E_2 of degree ℓ^(d_1+d_2), or ⊥.
 1. d_1 <- ceil(log_ℓ m); d_2 <- ceil(log_ℓ q)
 2. T <- {}                                    # hash table keyed by j-invariant
 3. for each non-backtracking path s of length d_1 from E_1 do
 4.     T[j(endpoint(s))] <- s                 # m insertions
 5. for each non-backtracking path s' of length d_2 from E_2 do
 6.     if j(endpoint(s')) in T then           # q lookups
 7.         return concat(T[j(endpoint(s'))], reverse(s'))
 8. return ⊥
```

**Step count.** `T_steps(Alg. 1) = Θ(m + q)` units under W3.

**Success condition.** Under H1 and H4 the two frontiers meet once `m·q = Ω(n_V)`,
i.e. `m·q = Ω(p)`. The textbook balance is `m = q = p^{1/2+o(1)}`, reproducing the
`Õ(p^{1/2})` **time and space** figure of `KN-TECH-029` / `KN-LIT-078` (cited,
reported).

### 4.2 Lemma 1 (full cost is never below step count) — derived in place

*Statement.* Under W1 and W6, for any algorithm `A`,
`FC(A) ≥ T_steps(A)`.

*Proof.* With `n` processors, `H ≥ n` and `T_wall ≥ T_steps/n`, so
`FC = H·T_wall ≥ n·(T_steps/n) = T_steps`. ∎

This one-line lemma is load-bearing for G2 (§6.3): it makes the `F_p` verdict
independent of every detail of W2.

### 4.3 Lemma 2 (memory-access throughput) — lower bound derived in place

*Statement.* Under W2, servicing `A` independent random accesses into a `w`-cell
three-dimensional memory requires wall-clock time `Ω(A/w^{2/3})`.

*Proof (lower bound).* Partition the cube of `w` cells by a plane into two halves.
A random access has probability `≥ 1/2 - o(1)` of having its source and target on
opposite sides, so `Ω(A)` accesses must cross. The plane meets `O(w^{2/3})` wires,
each carrying `O(1)` messages per unit time, so the crossing traffic needs time
`Ω(A/w^{2/3})`. ∎
The matching upper bound (mesh routing achieves `Θ(w^{1/3})` for a batch of `w`)
is assumed, not proved (W2).

### 4.4 Lemma 3 (MITM full cost) — derived in place

*Statement.* Under W1–W4, H1, H4, with `m·q = Θ(p)`:

- storage hardware `H ≥ m` for the whole query phase;
- the `q` lookups take time `Ω(q/m^{2/3})` (Lemma 2);
- table construction alone forces `FC ≥ m` (each of `m` entries costs one unit;
  `H·T ≥ m` for any split).

Hence `FC(Alg. 1) = Ω( max( m , q/m^{2/3} · m ) ) = Ω( max( m , p/m^{2/3} ) )`.

*Consequences (arithmetic done here so it can be checked).*

1. **Textbook balance** `m = q = p^{1/2}`:
   `FC = p / (p^{1/2})^{2/3} = p / p^{1/3} = p^{2/3}`.
2. **Full-cost-optimal rebalance.** `max(m, p/m^{2/3})` is minimised where
   `m = p/m^{2/3}`, i.e. `m^{5/3} = p`, i.e. `m = p^{3/5}`, giving
   `FC = p^{3/5}` and `q = p^{2/5}`. The step count at that point rises to
   `Θ(p^{3/5})`.
3. Both exceed the step-count exponent `1/2`. **`FC` exponent `≥ 3/5 > 1/2`
   strictly, for every choice of `m`.**

*Cross-check against the archived literature.* Apply the same formula to Shanks's
BSGS in a group of order `n` (table `m`, giant steps `q = n/m`): `FC = n/m^{2/3}`,
which at the textbook balance `m = n^{1/2}` gives `n^{2/3}` — **exactly** the
`n^{2/3+o(1)}` figure `KN-LIT-094` reports (`citation_verified: read` for that
passage). This is the strongest available internal validation of W2.
*Recorded discrepancy, not hidden:* my optimisation gives `n^{3/5}` for a
*memory-rebalanced* BSGS, below the published `n^{2/3}`. The consistent reading is
that Wiener's `n^{2/3}` prices **standard** BSGS (defined with `m = n^{1/2}`) and
not a rebalanced variant. `KN-LIT-094`'s own record states the wiring derivation
was not re-checked and the `o(1)` constants not extracted, so this note cannot
settle which reading is Wiener's. The `3/5` figure is therefore labelled
**derived in place under W1–W4, not attributed to `KN-LIT-094`.**

### 4.5 G1 verdict

**MITM's full-cost exponent strictly exceeds its step-count exponent**: `2/3`
(textbook balance) or `3/5` (full-cost-optimal), versus `1/2`. It collapses to
`1/2` if and only if W2 is replaced by unit-cost random access, i.e. the RAM model
that `KN-TECH-035` and `KN-LIT-094` exist to reject. The first pre-registered
falsification outcome of `IDEA-20260725-001` ("MITM full cost collapses to the
same exponent as step count") **did not fire**.

**But this is not decision-relevant on its own**, because §5 and §7 show MITM is
not the matched baseline in either regime, under any convention.

---

## 5. G3 — the low-memory isogeny-graph collision-search analogue: **defined**

`EV-SSI-001` records this analogue as "underspecified relative to the group
setting" and `RT-20260725-503` N1 makes it the main technical risk. It is defined
here in full. A verdict of "underspecified" is not returned.

### 5.1 Algorithm 2 (LMCS — low-memory claw search on the isogeny graph)

```
Algorithm 2: LMCS — low-memory collision search for Problem 1
Require: E_1, E_2 supersingular over F_{p^2}; walk length d with ℓ^d = Θ(n_V);
         distinguished-point parameter θ; memory budget w (may be polylog).
Ensure : an isogeny E_1 -> E_2 of degree ℓ^{2d}, or ⊥ on budget exhaustion.

 Index space.  I = Z/(ℓ+1) × (Z/ℓ)^{d-1}, |I| = (ℓ+1)ℓ^{d-1} = Θ(n_V).
               A string s ∈ I encodes a non-backtracking path of length d:
               s_0 selects one of the ℓ+1 neighbours, each later s_i selects
               one of the ℓ non-backtracking continuations.
 Domain.       D = {1,2} × I,  M := |D| = 2|I| = Θ(n_V) = Θ(p).
 Endpoint map. g(b,s) := j(endpoint of the path encoded by s started at E_b).
 Hash.         h : V -> D a public pseudorandom bijection-like encoding.

 WALK LAW (the "walk" is on path-indices, NOT on the graph):
     f : D -> D,      f(x) := h( g(x) ).
     x_{i+1} := f(x_i),  from random starting points x_0 ∈ D.

 DISTINGUISHED-POINT PREDICATE:
     x = (b,s) is distinguished iff the first ceil(log2(1/θ)) bits of the
     canonical encoding of x are zero.   Expected trail length L = 1/θ.
     Set L := max(1, sqrt(M/w))  (the van Oorschot–Wiener parameterisation).

 1. repeat on each of n processors:
 2.     x <- random element of D
 3.     walk x <- f(x) until x is distinguished, at most 20L steps
 4.     store (start, x, length) in the shared w-slot table, keyed by x
 5.     if x already stored with a different start then
 6.         re-walk both trails to locate y ≠ y' with f(y) = f(y')
 7.         if y = (1,s_1) and y' = (2,s_2) (opposite sides)
                and g(y) = g(y') (a genuine claw, not an h-collision) then
 8.             return RECONSTRUCT(s_1, s_2)
 9.         else discard (useless collision) and continue
10. until budget exhausted; return ⊥

 RECONSTRUCT(s_1, s_2):
     P1 <- the length-d path from E_1 encoded by s_1     (endpoint F)
     P2 <- the length-d path from E_2 encoded by s_2     (endpoint F)
     return the concatenation P1 · reverse(P2), an isogeny E_1 -> E_2
            of degree ℓ^{2d}, after cancelling any backtracking at the join.
```

Every ingredient `RT-20260725-503` N1 named is now explicit: **walk law** (line
"WALK LAW"), **distinguished-point predicate** (the `θ`-bit prefix test),
**collision-to-path reconstruction** (`RECONSTRUCT`), and the **any-collision
versus golden-collision** accounting (Lemma 4, §5.4).

The one design decision that makes this work, and that the group setting does not
force you to make: **the walk is on the path-index space `I`, not on the graph.**
Each application of `f` recomputes a *fresh* length-`d` path from scratch, costing
`d = Θ(log_ℓ p)` isogeny steps. That is why the output degree stays `ℓ^{2d}` —
polynomial description size — however long the collision search runs. §5.6 shows
what happens if you make the other choice.

### 5.2 Lemma 4 (claw multiplicity) — derived in place, under H1/H4

*Statement.* With `|I| = Θ(n_V)` per side, the number of cross-side claws
`C = #{(s_1,s_2) : g(1,s_1) = g(2,s_2)}` satisfies `C = Θ(n_V) = Θ(M)`.

*Proof.* Under H1 each endpoint is near-uniform on `V`, `|V| = n_V`. There are
`|I|² = Θ(n_V²)` cross-side pairs, each colliding with probability
`(1+o(1))/n_V`, giving `C = Θ(n_V)`. Total collisions of `f` are also `Θ(M)`
(genuine same-side coincidences plus `h`-collisions contribute `Θ(M)` as well),
so **a constant fraction of all `f`-collisions are usable claws.** ∎

Constants are not optimised and are not claimed; only the `Θ(M)` order is used.

### 5.3 Lemma 5 (cost of collecting `k` collisions with memory `w`) — derived in place, under H2

*Statement.* Under H2 and the vOW parameterisation `L = √(M/w)`:

```
T(k) =  sqrt(2·M·k)          for  k ≤ w/2      (one function version suffices)
T(k) =  2·k·sqrt(M/w)        for  k ≥ w/2      (⌈2k/w⌉ versions)
```

*Proof.* Within one version of `f`, `w` stored trails of length `L` cover
`t = wL = √(Mw)` evaluations, and under H2 the expected number of detected
collisions among `t` covered points is `t²/(2M)`. Solving `t²/(2M) = k` gives
`t = √(2Mk)`, admissible while `t ≤ √(Mw)`, i.e. `k ≤ w/2`. Beyond that the table
is full: re-key `f` and repeat, paying `√(Mw)` per `w/2` further collisions, so
`T(k) = (2k/w)·√(Mw) = 2k√(M/w)`. The two branches agree at `k = w/2`. ∎

*Cross-check against archived primary text.* Setting `k = M/2` (a single **golden**
collision hidden among all `Θ(M)` collisions) gives
`T = 2·(M/2)·√(M/w) = M^{3/2}/√w = √(M³/w)` — which is exactly the van
Oorschot–Wiener claw-finding tradeoff quoted in
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` §1.1: *"solves a claw-finding
problem of this size in time essentially √(N³/w) = p^{1/2+o(1)}/w^{1/2} with memory
w"*. Lemma 5 therefore reproduces the archived formula in its golden regime and
extends it to the many-claw regime, which is the regime Problems 1–2 actually live
in.

### 5.4 The any-claw vs golden-claw distinction — the crux

Combining Lemmas 4 and 5:

- **Problem 3 (fixed degree, CSSI/SIDH):** the degree constraint pins the tables to
  a size fixed by the promised degree and leaves essentially **one** claw, `C = 1`.
  Then `k = Θ(M)` and `T = Θ(√(M³/w))` — memory `w` matters at exponent level, and
  the MITM-versus-vOW debate of `KN-LIT-124` / `KN-LIT-125` is a real debate.
- **Problems 1–2 (unrestricted degree):** `C = Θ(M)` by Lemma 4, so `k = Θ(1)` and
  `T = Θ(√M)` — **independent of `w`.** Memory buys nothing.

> **Memory buys nothing when claws are abundant.** This is why the SIDH/CSSI
> cost-model literature does not transfer to pure path-finding, and it is the
> precise technical reason `IDEA-20260725-001`'s premise fails on `F_{p^2}`.

This is also the answer `KN-TECH-050` was written to demand: the degree constraint
is one of its three load-bearing parameters, and it is the one that decides this
question.

### 5.5 Lemma 6 (correctness and output size) and Lemma 7 (cost) of Algorithm 2

**Lemma 6 (correctness, under no heuristic).** If line 7 succeeds, `RECONSTRUCT`
returns a genuine isogeny `E_1 → E_2`: `P1` is an isogeny `E_1 → F` and `P2` an
isogeny `E_2 → F`, so `P1 · reverse(P2)` is an isogeny `E_1 → E_2` of degree
dividing `ℓ^{2d}`. Its description length is `2d = Θ(log_ℓ p)` — **polynomial**,
so it is a valid solution to Problem 1. ∎ (Correctness needs no heuristic; only the
*existence* of a claw within budget does.)

**Lemma 7 (cost, under H1, H2, H4, W1–W4, W6).**
`M = Θ(p)`, `C = Θ(M)`, hence `k = Θ(1)` and by Lemma 5
`T_steps = Θ(√M · d) = p^{1/2+o(1)}` units.
Memory: `w` may be polylog; hardware `H = n + w`.
Memory-access rate: one table access per trail of length `L`, so under W2 the
wiring charge is negligible whenever `n/L ≤ w^{2/3}` — satisfied with wide margin
at polylog `w` and `L = √(M/w) = p^{1/2-o(1)}`.
Therefore `T_wall = p^{1/2+o(1)}/n` and
**`FC(Alg. 2) = (n + w)·p^{1/2+o(1)}/n = p^{1/2+o(1)}`.** ∎

**Consistency with the archived record, and honest novelty status.** The archived
primary text states that *"the classic `p^{1/2+o(1)}` algorithms with polynomial
memory like [21]"* — [21] being Delfs–Galbraith — already occupy this point
(`paper_fulltext.md` §1.1). Algorithm 2 therefore **matches a known exponent with
a known memory profile**; it is an `adaptation` that makes the analogue explicit,
**not** a new algorithm and **not** novel. Novelty status: `adaptation`. Its value
here is that it discharges G3 constructively and pins the `w`-independence
(§5.4), which no archived corpus entry states.

### 5.6 Proposition 10 (the naive variant is falsified in place)

*Statement.* The "obvious" transfer — a deterministic pseudorandom walk
`F : V → V` on the graph itself, `j → j' = step(j, H(j))`, run from `E_1` and
`E_2` with distinguished points until the trails merge — solves Problem 1 in
`Θ(√n_V) = p^{1/2+o(1)}` steps with `O(1)` memory **but does not produce a valid
solution.**

*Proof.* Trail merge occurs at depth `Θ(√n_V) = Θ(p^{1/2})` by the birthday bound.
The isogeny it certifies is the concatenation of the two trails, of degree
`ℓ^{Θ(p^{1/2})}`, and the only representation the algorithm has of it is the trail
itself. Emitting it violates the polynomial-description-size requirement of
Problem 1; storing it costs `Θ(p^{1/2})` memory, which is exactly the memory the
construction was built to avoid. ∎

*Why this matters.* The failure is not a technicality; it is the structural reason
the group-setting transfer is not automatic (`RT-20260725-503` N1 was right to flag
it). Algorithm 2 evades it by walking on **path indices** rather than on the graph,
paying a `Θ(log_ℓ p)` factor per evaluation for a polynomial-size output. That
trade is the whole content of the definition.

### 5.7 G3 verdict

**DEFINED.** Walk law, distinguished-point predicate, collision-to-path
reconstruction, any-claw versus golden-claw accounting, and cost are all explicit
(Algorithm 2, Lemmas 4–7). No uncharged oracle and no nonstandard graph access is
used: Algorithm 2 needs only `Φ_ℓ` neighbour evaluation, which is the same
primitive MITM and Delfs–Galbraith need, charged identically under W3. The naive
graph-walk variant is separately **falsified in place** (Prop. 10). The second
pre-registered falsification outcome of `IDEA-20260725-001` ("the analogue is not
well-defined without uncharged oracles or nonstandard graph access") **did not
fire**.

---

## 6. G2 — the `F_p` regime, and red-team objection **F2 by name**

`RT-20260725-503` fatal objection **F2** ("Delfs–Galbraith likely already dominates
the `F_p` regime before full cost") states: charging MITM memory makes MITM worse,
which *strengthens* DG's dominance and does not change the matched baseline
identity, so the second prediction of `IDEA-20260725-001` risks being vacuous or
decision-irrelevant on `F_p`. **F2 is addressed here directly and is upheld, with a
proof rather than a plausibility argument.**

### 6.1 Algorithm 3 (Delfs–Galbraith, as recalled and instantiated)

```
Algorithm 3: DG for Problem 2 (and, with step 1, for Problem 1)
Require: E_1, E_2 supersingular over F_{p^2}.
Ensure : an isogeny E_1 -> E_2.
 1. (general case only) from each E_i, random-walk in the F_{p^2} graph until an
    F_p-rational curve is reached.                 # Θ(n_V/S) = p^{1/2+o(1)} steps,
                                                   # O(1) memory: nothing is stored
 2. run a claw search inside the F_p-rational subgraph V_p, |V_p| = S = p^{1/2+o(1)},
    between the two descended curves.              # Θ(S^{1/2}) = p^{1/4+o(1)} steps
 3. compose the three pieces.
```

Step counts `Õ(p^{1/2})` general / `Õ(p^{1/4})` for `F_p`-rational inputs are
**cited** (`KN-TECH-029`, `KN-LIT-078`; confidence `reported`). Step 1's memory
profile is derived here: a walk that stores nothing until it lands in `V_p` is
`O(1)`-memory by construction, which is the in-repo reading consistent with the
archived statement that the classic `p^{1/2+o(1)}` algorithms use polynomial
memory.

### 6.2 Memory of step 2 — derived in place, under H3

Instantiating step 2 with Algorithm 2 *restricted to `V_p`* (index space of
size `Θ(S)`, domain `M_p = Θ(S) = p^{1/2+o(1)}`): by Lemma 4 applied inside `V_p`,
claws are again abundant (`C = Θ(M_p)`), so by Lemma 5, `k = Θ(1)` and
`T_steps = Θ(√M_p) = p^{1/4+o(1)}` at **polylog memory**, giving
`FC = p^{1/4+o(1)}`.
This depends on **H3**, which is weaker than H1 (§3). If H3 fails, the fallback is
a MITM table of size `p^{1/4}` inside `V_p`, whose full cost by Lemma 3 (with
`p → S`) is `S/(S^{1/2})^{2/3} = S^{2/3} = p^{1/3+o(1)}`. **Either way the `F_p`
verdict below is unchanged**, because `p^{1/3} < p^{1/2}`.

### 6.3 Lemma 8 (MITM is never competitive on `F_p`) — derived in place, model-independent

*Statement.* Under W1 and W6 alone — no appeal to W2 — for `F_p`-rational
instances:
`FC(Alg. 1) ≥ T_steps(Alg. 1) = Ω(p^{1/2})` (Lemma 1 and §4.1), while
`FC(Alg. 3) = p^{1/4+o(1)}` under H3, or `p^{1/3+o(1)}` without H3 (§6.2).
Hence `FC(Alg. 3) / FC(Alg. 1) ≤ p^{-1/6+o(1)}` unconditionally on the wiring
model, and `≤ p^{-1/4+o(1)}` under H3. ∎

*Quantified gap widening.* Step counts: `p^{1/2}` vs `p^{1/4}`, gap `p^{1/4}`.
Full costs under W2: `p^{2/3}` (textbook MITM) or `p^{3/5}` (rebalanced MITM) vs
`p^{1/4}`, gap `p^{5/12}` or `p^{7/20}`. Charging memory **widens** the existing
gap; it never narrows it, and by Lemma 8 no wiring model satisfying W1 can reverse
the ranking.

### 6.4 G2 verdict, stated as the answer to F2

**MITM is never competitive on `F_p`-rational instances under `SSI-FC-2026`.**
F2 is **discharged (by being confirmed, with a proof)**: the prediction
`matched_baseline_identity: different` of `IDEA-20260725-001` is **false on the
`F_p` regime**, and would have been false under any honest convention. The
regimes are kept separate throughout this note precisely because the `F_{p^2}`
answer (§7) is different, and blending them would have hidden both.

The third pre-registered falsification outcome ("Delfs–Galbraith already strictly
dominates both under every honest convention, and the candidate adds no
decision-relevant correction") **fired in its first clause on this regime.** Its
second clause is addressed in §7.

---

## 7. G4 — matched baselines, and the correction that is actually decision-relevant

### 7.1 Lemma 9 (the current `F_{p^2}` frontier under `SSI-FC-2026`) — derived in place from archived statements

The archived primary text `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` states
(Theorem 1.1, Corollary 1.2, **conditional on that paper's Heuristic 1**) an
algorithm for the supersingular isogeny problem — Problem 1 above — in expected
time **and memory** `p^{1/3+o(1)}`, superseding the `p^{1/2}·(log p)^{O(1)}` that
had been stable since Delfs–Galbraith. It further states that its core is a
claw-finding problem on two sets of size `N = p^{1/3+o(1)}`, solvable by
van Oorschot–Wiener in time `√(N³/w)` with memory `w`, and parallelisable to
`√(N³/w)/n`.

Applying `SSI-FC-2026` to that claw problem (this arithmetic is mine):

- `M = Θ(N) = p^{1/3+o(1)}`, golden regime `C = O(1)`, so by Lemma 5
  `T(w) = Θ(M^{3/2}/√w)`.
- Table lookups occur once per trail of length `L = √(M/w)`, so the W2 wiring
  charge binds when `n/L > w^{2/3}`. Optimising `FC = (n+w)·T/n` subject to
  `n ≤ L·w^{2/3}` gives two branches meeting at `w = M^{3/5}`:
  - `w ≤ M^{3/5}`: `FC ≈ 2T = Θ(M^{3/2}/√w)`, decreasing in `w`;
  - `w ≥ M^{3/5}`: `FC = w^{1/3}·M/2`, increasing in `w`.
- **Optimum** at `w = M^{3/5} = p^{1/5+o(1)}`, giving
  `FC_min = Θ(M^{6/5}) = p^{2/5+o(1)}`, with wall-clock `p^{1/5+o(1)}` on
  `p^{1/5+o(1)}` processors.
- **At the paper's natural operating point** `w = M = p^{1/3+o(1)}` (store the whole
  table): `FC = M^{4/3}/2 = p^{4/9+o(1)}`.

*Reading.* Under full cost the `p^{1/3+o(1)}` headline becomes `p^{4/9+o(1)}` as
operated and `p^{2/5+o(1)}` after a memory rebalance. Both remain below the
classical `p^{1/2+o(1)}`, so the result survives memory charging — but the margin
over the classical baseline shrinks from `p^{1/6}` to `p^{1/10}`. This is a
**defender-favourable correction to an attacker's headline**, the same sign
`KN-LIT-126` reports on the quantum side and that `KN-TECH-050` warns is easy to
get backwards.

*Conditionality carried, per `docs/claims-and-verification.md`.* Every figure in
this subsection is **conditional on the Heuristic 1 of
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`**, plus H2 and W1–W4. Dropping that
qualifier anywhere downstream is a claim-tier violation.

### 7.2 The matched baselines

**Regime `F_{p^2}` (Problem 1, generic).**

| Algorithm | Steps | Memory | Full cost `SSI-FC-2026` | Depends on |
|---|---|---|---|---|
| MITM, textbook balance (Alg. 1) | `p^{1/2}` | `p^{1/2}` | `p^{2/3}` | H1,H4,W1–W4 |
| MITM, full-cost-optimal (Alg. 1, `m=p^{3/5}`) | `p^{3/5}` | `p^{3/5}` | `p^{3/5}` | H1,H4,W1–W4 |
| **LMCS (Alg. 2) / DG general (Alg. 3)** | `p^{1/2+o(1)}` | **polylog** | **`p^{1/2+o(1)}`** | H1,H2,H4,W1–W4 |
| Archived `p^{1/3+o(1)}` algorithm, as operated | `p^{1/3+o(1)}` | `p^{1/3+o(1)}` | `p^{4/9+o(1)}` | its Heuristic 1 + W1–W4 |
| Same, vOW-rebalanced at `w=p^{1/5}` | `p^{2/5+o(1)}` | `p^{1/5+o(1)}` | **`p^{2/5+o(1)}`** | its Heuristic 1 + H2 + W1–W4 |

**Matched baseline for `F_{p^2}`: quote both tiers.**
*Unconditional tier:* `p^{1/2+o(1)}` time at polynomial memory, full cost
`p^{1/2+o(1)}`.
*Heuristic-conditional tier:* `p^{1/3+o(1)}` time and memory, full cost
`p^{2/5+o(1)}` after rebalancing, conditional on the archived paper's Heuristic 1.
**MITM is not the matched baseline under any convention examined** and should be
recorded as a high-memory footnote, exactly as `IDEA-20260725-001`'s
prediction-(b) branch anticipated.

**Regime `F_p`-rational (Problem 2).**

| Algorithm | Steps | Memory | Full cost | Depends on |
|---|---|---|---|---|
| MITM on the full graph | `p^{1/2}` | `p^{1/2}` | `≥ p^{3/5}` | Lemmas 1,3 |
| DG + Alg. 2 inner search | `p^{1/4+o(1)}` | polylog | `p^{1/4+o(1)}` | H1,H2,H3,H4 |
| DG + MITM inner search | `p^{1/4}` | `p^{1/4}` | `p^{1/3+o(1)}` | H1,H4,W1–W4 |
| Archived `p^{1/3+o(1)}` algorithm | `p^{1/3+o(1)}` | `p^{1/3+o(1)}` | `p^{4/9+o(1)}` | its Heuristic 1 |

**Matched baseline for `F_p`: Delfs–Galbraith at `p^{1/4+o(1)}` steps.** It is
unaffected by memory charging, and it is *not* displaced by the `p^{1/3+o(1)}`
algorithm, since `1/4 < 1/3`. This is the cleanest instance in the whole note of
`KN-TECH-050`'s rule: the newer, asymptotically stronger algorithm for the general
problem is the **wrong** baseline on this regime.

### 7.3 Which pre-registered falsification outcome fired

| Pre-registered outcome (`IDEA-20260725-001.cheapest_falsification_gate.falsifies_if`) | Fired? |
|---|---|
| (1) MITM full cost collapses to its step-count exponent | **No.** It strictly exceeds it (§4). |
| (2) Low-memory analogue not well-defined without an uncharged oracle or nonstandard access | **No.** Defined (Algorithm 2, §5); the naive variant is separately falsified. |
| (3) DG already strictly dominates under every honest convention, and the candidate adds no decision-relevant correction | **First clause: yes** (both regimes, §6). **Second clause: no** — see below. |

Outcome (3)'s second clause fails for a reason the pre-registration did not
anticipate. The candidate's *stated* mechanism (charging MITM memory) adds nothing:
MITM was already dominated. But executing the gate surfaced two corrections that
**are** decision-relevant, and neither is a memory charge:

- **C-α.** The classical `F_{p^2}` baseline is **memory-light**, not
  memory-heavy (§5, and the archived "[21] … with polynomial memory"). A future
  candidate therefore **cannot** win a comparison by charging memory to the
  classical baseline. That closes off an entire class of accounting-artifact
  advantage claims before they are made.
- **C-β.** `KN-TECH-029`'s `Õ(p^{1/2})` classical `F_{p^2}` figure is **stale
  against this repository's own archived primary text**, which places the frontier
  at `p^{1/3+o(1)}` (conditional). Any `GOAL-SSI-001` candidate benchmarked against
  `p^{1/2}` on `F_{p^2}` would be measuring against a superseded baseline.

Correct disposition: **documentation-level for the cost model, but a genuine
baseline-identity correction on `F_{p^2}` for an unrelated reason.** Under
`docs/target-result-profile.md` rule A1 neither C-α nor C-β is target-class: C-α
moves no exponent of any hard problem, and C-β is a bookkeeping correction that
imports someone else's exponent. Both are stated plainly as such.

---

## 8. G5 — `new_attack_mechanism_detected: false`

**Verdict: false.** Justification, item by item, so a reviewer can attack each:

1. Algorithm 2 **matches** the known `p^{1/2+o(1)}`-at-polynomial-memory point
   (archived, §5.5). It moves no exponent. Novelty status `adaptation`.
2. The `p^{3/5}` MITM rebalance lowers the *full cost* of an algorithm that is
   **dominated in both regimes**; it improves nothing an attacker would run.
3. Lemma 9's `p^{2/5+o(1)}` **raises** the effective cost of the archived
   `p^{1/3+o(1)}` algorithm. A correction that makes the attack more expensive is
   not an attack mechanism.
4. The any-claw/golden-claw distinction (§5.4) is a *reason* the exponents are what
   they are; it produces no algorithm that beats a baseline.
5. Under `docs/target-result-profile.md` A1/C1–C2, none of the above changes the
   asymptotic exponent of a named hard problem. Constant-factor and
   full-cost-bookkeeping results are explicitly non-target-class.

**Therefore BATCH-002 does not count toward any `GOAL-SSI-001` completion
criterion**, exactly as `GOAL-SSI-001.open_batch.completion_counting` requires.
This flag is not inflated, and the note does not manufacture a mechanism to satisfy
a completion route.

### 8.1 One mechanism was generated and then falsified in place

Recorded because the falsification is itself the useful artifact, and because a
reviewer should be able to check that I did not silently discard a live candidate.

**Candidate (batched re-randomisation).** The archived Algorithm 3 of
`paper_fulltext.md` calls its table-building Algorithm 2 on re-randomised curves
`E'` until success, expected cost `M/P₀`. Idea: build **one** table containing
`L(E'_i, X, B)` for `k` independently re-randomised curves `E'_1,…,E'_k`, at cost
`kM`, and accept a claw between an entry with domain `E'_i` and codomain `F` and an
entry with domain `E'_j` and codomain `F^{(p)}`. Such a cross claw yields an
isogeny `E'_i → E'^{(p)}_j`; with the known re-randomisation walks
`ω_i : E → E'_i` and `ω_j : E → E'_j` it composes to
`dual(ω_j^{(p)}) ∘ θ ∘ ω_i : E → E^{(p)}`. There are `k²` ordered pairs at table
cost `kM`, suggesting expected cost `M/(kP₀)` instead of `M/P₀`.

**Proposition 11 (falsified in place).** The construction fails for `i ≠ j`.
Algorithm 2's correctness (its Lemma 3.4) needs the target isogeny to have degree
`≤ (p/2)^{1/3}`, which comes from its **Theorem 1.5** — a bound on the smallest
isogeny `E → E^{(p)}`, i.e. specific to the Frobenius conjugate **of the same
curve**, arising from the two-sided quaternionic ideal of reduced norm `p`. For
`i ≠ j` the pair `(E'_i, E'^{(p)}_j)` is a generic pair of supersingular curves and
**no archived bound replaces Theorem 1.5 for it**. Without that bound the
degree-split inequality `deg η ≤ B(p/2)^{1/3}/X = X` fails, so cross-pairs
contribute nothing at the chosen `X = B^{1/2}(p/2)^{1/6}`. The `k²`-versus-`k`
accounting evaporates. ∎

Two further reasons the candidate would need to clear even if Prop. 11 were
repaired, recorded so the corpus keeps them: the `k²` pair events are **not
independent** (no justification was constructed), and even a clean factor-`k` gain
would only shrink `1/P₀ = p^{o(1)}`, leaving the `1/3` exponent untouched — and
`paper_fulltext.md` **Remark 1** already records the closely related multiplicity
effect (several small isogenies `E → E^{(p)}`, any one of which suffices) as
"absorbed in the hidden term of the asymptotic complexity". So the direction is
both broken as stated and, in its repaired form, already known to be `o(1)`-level.

### 8.2 Two leads recorded for a successor batch (leads, not mechanisms, not claims)

- **L1.** Is there a claw-multiplicity analogue of §5.4 for the `p^{1/3+o(1)}`
  algorithm — i.e. a target set of size `p^{ε}` playing the role `{E^{(p)}}` plays,
  for which a Theorem-1.5-style bound *does* hold? Prop. 11 says the naive choice
  fails; it does not say every choice fails, and this note **declares no direction
  impossible**. Cheapest gate: a literature check for minimal-degree bounds on
  isogenies to targets other than the Frobenius conjugate.
- **L2.** `KN-LIT-132` (fixed-degree, essentially memory-free, 2024) sits in the
  Problem-3 regime; its corpus entry explicitly refuses to record its complexity
  ranges because a search-returned abstract looked internally inconsistent. §5.4
  predicts fixed-degree is exactly the regime where memory matters at exponent
  level, so that paper's intervals are the right thing to obtain from the primary
  source. Cheapest gate: fetch and record the intervals; this note quotes **no**
  number from it.

Neither lead is a mechanism, neither is claimed, and neither changes the G5 flag.

---

## 9. Uncharged residue (explicit, per G4)

Charged: isogeny steps (W3), table construction, table storage over its occupancy,
memory access under W2, processors, re-randomisation walks, and output conversion
as a `poly(log p)` cofactor absorbed in `o(1)`.

**Not charged, and therefore not accounted for anywhere above:**

1. **All constants and all `o(1)` terms.** In particular the archived
   `p^{1/3+o(1)}` result discloses a **superpolynomial** overhead inside its
   `o(1)`. Every full-cost exponent in §7 inherits that overhead unchanged; a
   rebalanced `p^{2/5+o(1)}` is not a smaller machine than `p^{4/9+o(1)}` at any
   stated `p`.
2. **The upper-bound half of W2.** Lemma 2 derives only the bisection lower bound;
   `Θ(w^{1/3})` achievability is assumed. `KN-LIT-094`'s own record states its
   wiring derivation was not re-checked in this corpus.
3. **Energy, cooling, bandwidth, latency, and interconnect topology** beyond the
   3-D mesh abstraction (`KN-TECH-035` applicability limits, inherited verbatim).
4. **The vOW shared-table communication pattern** — Algorithm 2 is charged for mesh
   routing but not for the distributed-server architecture real vOW deployments use
   (`KN-LIT-125` is the archived pointer to that gap; no number from it is quoted).
5. **Modular-polynomial precomputation** `Φ_ℓ` and any batched-evaluation
   engineering.
6. **Reliability over long runs** (error correction, restarts, checkpointing).
7. **Quantum resources of every kind** (excluded by the card; `KN-OPEN-014` lane;
   `KN-LIT-126` is the archived pointer).
8. **Torsion-image oracles** (forbidden; SIDH regime).
9. **The heuristics themselves** — H1–H4 are unvalidated here, and validating them
   would require the curve computation this batch forbids.
10. **Delfs–Galbraith's actual published memory profile.** §6.1–§6.2 reconstruct it;
    `KN-LIT-078`'s corpus entry is `confidence: reported`, records that the full
    paper was not read, and does not state a memory figure for the inner search.
11. **`S = |V_p|`** is used as `p^{1/2+o(1)}` on the authority of `KN-TECH-029`
    ("~sqrt of the full graph"); the class-number asymptotic behind it was not
    re-derived here.

---

## 10. G6 — established vs derived vs speculative, and what this cannot establish

**Established / cited (with the confidence the corpus records).**
Graph size and Ramanujan property — `KN-TECH-024` (`established`).
MITM `Õ(p^{1/2})` time and space; DG `Õ(p^{1/4})` on `F_p`; `|V_p| ≈ √|V|` —
`KN-TECH-029`, `KN-LIT-078` (`reported`).
Full cost, and BSGS `n^{1/2}` steps vs `n^{2/3+o(1)}` full cost —
`KN-LIT-094` (`established`, that passage `citation_verified: read`), `KN-TECH-035`.
Distinguished points and parallel collision search — `KN-LIT-012`, `KN-TECH-006`.
Regime discipline (field / memory model / degree constraint) — `KN-TECH-050`.
From archived primary text `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`:
Theorem 1.1 and Corollary 1.2 (`p^{1/3+o(1)}` time and memory, conditional on its
Heuristic 1); the previous best `p^{1/2}(log p)^{O(1)}` stable since [21]; the vOW
tradeoff `√(N³/w)` and its parallel form; "the classic `p^{1/2+o(1)}` algorithms
with polynomial memory like [21]"; Theorem 1.5 (`deg ≤ (p/2)^{1/3}` for
`E → E^{(p)}`); Lemma 3.4's degree split; Remark 1's multiplicity observation.
Qualitative only, no numbers quoted: `KN-LIT-124` (vOW below MITM for CSSI),
`KN-LIT-125`, `KN-LIT-126`, `KN-LIT-132` — all four corpus entries state their
numbers were never read into this repository.

**Derived in place (checkable above, attributable to no source).**
Lemma 1 (full cost ≥ step count). Lemma 2 (bisection lower bound). Lemma 3 (MITM
full cost `2/3` at balance, `3/5` optimised). Lemma 4 (claw multiplicity). Lemma 5
(collision-collection cost, cross-validated against the archived `√(N³/w)`).
Algorithm 2 and Lemmas 6–7. Prop. 10 (naive-variant falsification). Lemma 8 and the
`F_p` gap widening. Lemma 9 (`p^{4/9}` / `p^{2/5}` full costs). Prop. 11
(candidate falsification).

**Untested expectations (asserted by no source, flagged as such here).**
That Wiener's `n^{2/3}` is the textbook-balance figure rather than his optimum
(§4.4). That H3 holds for the `F_p`-rational subgraph. All numerical constants.
Any claim about which of `p^{4/9}` and `p^{2/5}` a real machine would realise.

**What this derivation cannot establish.**
It cannot establish concrete bit security for any parameter set: asymptotic
full-cost statements settle **baseline identity**, not security levels
(`KN-TECH-035` states this limit explicitly, and it is inherited). It cannot
validate H1–H4, which needs computation this batch forbids. It cannot verify the
numbers in `KN-LIT-124/125/126/132`, whose corpus entries disclaim them. It cannot
confirm or deny the archived paper's Heuristic 1. It settles nothing about CGL,
SQIsign, CSIDH hardness, sub-`p^{1/4}` endomorphism-ring attacks,
`KN-OPEN-013/014/015`, quantum attacks, or torsion-image attacks — all out of scope
by the frozen card. It is one unreplicated derivation by one producer and is worth
exactly that until `TASK-20260728-007` reviews it independently.

---

## 11. Inference and provenance

Requested policy `research-deep`. Resolved model `claude-opus-5`.
`model_verified: false` — **this session did NOT run
`python3 -m orchestration.adapter doctor --probe`** (it has no shell), so per
`AGENTS.md` the identifier is unverified configuration.
`fallback_used: unknown` — no adapter resolution record was produced for this
session, so whether `claude-opus-5` is the `research-deep` binding for the active
backend cannot be asserted here; it is recorded as unknown rather than guessed.
`reasoning_effort: policy default`. `independent_session: false` (the card sets
`independent_session_required: false`).
Read-only tools only. **Zero curve computation. Zero commands run. No web fetch was
performed for this task, so no external citation appears above that is not already
archived in this repository.** No ledger record, no official state, and nothing
outside
`coordination/goals/GOAL-SSI-001/batches/BATCH-002/tasks/TASK-20260728-005/` was
written.
