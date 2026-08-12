# OD-1: diameter of the (lambda, k) graph, and the GATE-701-C redesign, built and run

TASK-20260801-801 — GOAL-AES-001 BATCH-003 — executor

**Scope and claim tier, stated first.** Everything in this report is
derivation-level mathematics and toy-scale computation about the algebra of AES
components and about a scaled-down `GF(2^4)` analogue. **Nothing here is a
cryptanalytic claim about AES at any round count.** It is not a distinguisher,
not a key-recovery result, not a measured structural excess, and **not a barrier
statement about AES security**. No closure is proposed, no `reject_scoped` is
proposed, no evidence strength is assigned, and no official state is changed —
those are the Coordinator's, in TASK-20260801-805, conditioned on the
independent review in TASK-20260801-804.

**Provenance.** `inference` block and `artifact_provenance` digest list are in
`od1_gate701c_results.json`, and `od1_gate701c_v2.py` carries a comment-block
inference stanza in its own text, per
`protocol-amendment-GOAL-AES-001-002` (standing basis `0137a051`).

**Supersession.** `od1_gate701c_v2.py` supersedes the `GATE-701-C`
specification in BATCH-002
`tasks/TASK-20260731-701/candidate_report.yaml` (`falsification_gate`, in
particular `null_object_control.null_2`) and the validator-authored `gate701c.py`
described in `tasks/TASK-20260731-705/derivation_and_ideation_review.md` §7.4.
Both BATCH-002 records **stand exactly as written and were not edited, re-run
into, or re-scored**. No BATCH-001 or BATCH-002 file was modified; all writes
are under this task's own directory.

**Literature.** No primary source is reachable in this environment. Every
recollection anywhere in this campaign is `unverified-from-memory`. This report
makes no literature comparison, no `sota_delta`, no bit-margin and no
extrapolation; the DEC-20260731-011 strikes remain in force.

---

## 0. PRE-REGISTRATION — WRITTEN BEFORE ANY GATE MEASUREMENT

**This section was written to disk before the gate phase of
`od1_gate701c_v2.py` was executed, and has not been altered since.** The
ordering is recorded mechanically in `od1_gate701c_results.json`
(`execution_order`, with the per-phase invocation timestamps, and the
`prereg_written_at` timestamp of this file). What preceded it was only
(i) the OD-1 graph phase, which is not the gate and carries no pre-registered
prediction, and (ii) the gate's **construction-validation** phase, which
inspects the three *matrices* and never computes a gate reading — that is
construction validation of the null object, and it is the whole content of the
redesign.

### 0.1 The three matrices

Working field `GF(2^4)`, modulus `0x13` = `x^4 + x + 1`, `alpha = 0x2`
primitive of order 15. Circulant convention `M[i][j] = c[(j-i) mod 4]`, the
same convention the AES MixColumns matrix satisfies.

| id | matrix | role |
|---|---|---|
| `target` | circulant first row `(02,03,01,01)` | AES-shaped analogue, unchanged from BATCH-002 |
| `null_1` | identity (interface = ShiftRows + AddRoundKey, no MixColumns) | sensitivity anchor, unchanged from BATCH-002 |
| `null_2` | circulant first row `(01,01,01,06)` | **REDESIGNED**, see §0.2 |

### 0.2 The redesigned `null_2`: what it negates and how it was selected

The BATCH-002 `null_2` (circulant `(02,00,01,01)`) negated **"every entry of
`M` is nonzero"**, which is a **sufficient** hypothesis of `PROP-701-I` Step 2.
Negating a sufficient hypothesis need not change the conclusion, and the
TASK-20260731-705 validator measured that it does not: `65535/65535` at
dimension 16, the same reading as the target, firing the gate's own
pre-declared VOID condition (D-705-1).

The redesigned `null_2` negates instead a **necessary ingredient of Step 3**:
that the entries of `M` generate the whole multiplicative group, which is what
makes the `(lambda,k)` graph strongly connected. Its specification, all four
parts verified computationally **before** the gate was run (§2):

1. **All entries nonzero** — so Step 2's sufficient hypothesis remains **TRUE**
   and is *not* what is being tested. ✔ verified.
2. **Invertible** — ✔ verified, rank 4 over `GF(2^4)`.
3. **Entries in a proper subgroup of `GF(2^4)^*`** — ✔ verified: the entries
   `{0x1, 0x6}` generate `H = {0x1, 0x6, 0x7}`, of order **3**, proper in a
   group of order 15.
4. **The induced `(lambda,k)` graph is NOT strongly connected** — ✔ verified:
   60 nodes, **5 strongly connected components of size 12 each**, which are
   exactly the 5 cosets of `H` in `GF(2^4)^*`, each carrying all four indices
   `k`.

**Selection rule, fixed a priori, deterministic, yielding exactly ONE
candidate.**

- `H` is chosen among the two nontrivial proper subgroups of `GF(2^4)^*`
  (orders 3 and 5) as the order-3 one, on the **structural** ground that it is
  `GF(4)^*`, the multiplicative group of the subfield `GF(4) < GF(2^4)` — the
  only proper subgroup here that is a subfield's multiplicative group, and
  hence the only one for which the predicted stall admits an independent hand
  argument. That is the same standard the gate itself imposes on `null_1`
  ("sensitivity is demonstrated, not assumed"). The choice is made on this
  criterion, not on any reading.
- Among 4×4 circulants with all entries in `H`, enumerate first rows
  `alpha^(5e)` for `e in {0,1,2}^4` in lexicographic order of `(e0,e1,e2,e3)`
  and take the **first invertible** one. The enumeration is recorded in full in
  the results file: `(01,01,01,01)` has rank 1 (singular); `(01,01,01,06)` has
  rank 4 and is taken. Two candidates examined for *invertibility*, one
  selected, **one run**.

**ONE REDESIGNED NULL, RUN ONCE.** No second candidate null will be built and
no candidate will be discarded on the basis of its reading. If the redesigned
gate does not discriminate, that is reported plainly as the batch result and
the work stops there.

### 0.3 The hand argument for the predicted stall (the analogue of `null_1`'s)

Let `H = GF(4)^*` and let all entries of the matrix lie in `H`. Fix a nonzero
`Delta`, let `i` be the least index with `Delta_i != 0` and put `mu = Delta_i`.
Let

```
S  =  GF(4) * mu  =  {0, mu, 0x6*mu, 0x7*mu}   ⊂ GF(2^4),
```

a **2-dimensional `GF(2)`-subspace** of `GF(2^4)` (a `GF(4)`-line). Then:

- the start vector `v0 = mu * m_i` has coordinates `mu * M[r][i] ∈ mu*H ⊂ S`;
- if `u` has all coordinates in `S`, then `T_j(u) = u_j * m_j` has coordinates
  `u_j * M[r][j] ∈ S * H = S`, because `S` is closed under multiplication by
  `GF(4)^*`;
- `S` is closed under addition, so `S^4` is closed under `GF(2)`-span.

Hence the closure is contained in `S^4`, of `GF(2)`-dimension `4 * 2 = 8 < 16`.
**The stall is proved, not hoped for.** This is the structural content of the
redesign: the target's engine works because the scalar orbit is unrestricted;
`null_2` restricts it to a `GF(4)`-line and the engine must stop at half the
dimension.

### 0.4 PRE-REGISTERED PREDICTED READINGS

Reading = `(number of the 65535 nonzero Delta whose closure reaches dimension
16)` together with the dimension histogram.

| matrix | pre-registered prediction (binding) | secondary expectation (non-binding, recorded) |
|---|---|---|
| `target` | **65535 / 65535 reach dimension 16** | histogram concentrated entirely at 16 |
| `null_1` | **0 / 65535 reach dimension 16**; every closure stalls at dimension **1** | — |
| `null_2` | **0 / 65535 reach dimension 16**; every closure has dimension **≤ 8** | dimension exactly 8 for all or nearly all `Delta` |

**Correction of the BATCH-002 record, stated as a correction.**
`candidate_report.yaml` (`null_object_control.null_1`) predicts that `null_1`'s
span "has dimension 4, NOT 16". That predicted stall dimension is **corrected
here from 4 to 1**, on the TASK-20260731-705 validator's measurement (0/65535
reach 16; the stall is at dimension 1). The reason is elementary: with the
identity matrix `m_k = e_k`, the start vector `lambda*e_k` has only its `k`-th
coordinate nonzero, and `T_k(lambda*e_k) = lambda*e_k` reproduces itself, so no
second scalar is ever generated and the span is the single `GF(2)`-line through
`lambda*e_k`. The containment claim in the BATCH-002 text is right; the
achieved dimension is not. **The BATCH-002 record is left unedited** — it is
committed and immutable; this is a superseding correction, not an overwrite.

### 0.5 PRE-REGISTERED VOID CONDITION

Inherited verbatim in force from `GATE-701-C`, and made explicit in three
parts:

- **VOID-A.** The gate is VOID, and no conclusion of any kind is drawn from it,
  if **either** null returns the same reading as the AES-shaped target
  (i.e. 65535/65535 reaching dimension 16).
- **VOID-B.** The gate is VOID if `null_1` does **not** stall — `null_1` is the
  control-of-the-control and is read before the target.
- **VOID-C.** The gate is VOID if the `target` itself fails to reach
  65535/65535 at dimension 16 *and* the failure is traced to the closure
  routine rather than to `M` (an implementation fault, reported as
  `implementation_error`, never as a mathematical result).

**FAIL_ESCALATE** (unchanged from BATCH-002): if some nonzero `Delta` closes to
dimension < 16 on the AES-shaped `target`, then a lossy propagating projection
exists in the analogue, `PROP-701-I`'s proof has an error, and the surviving
`Delta` is itself the next object to study.

### 0.6 PRE-REGISTERED DISCRIMINATION VERDICT RULE

The gate **DISCRIMINATES** if and only if the readings of `target`, `null_1`
and `null_2` are **pairwise distinguishable** — three qualitatively different
readings, not three values separated by a threshold. Concretely, with the
predictions above: `16` vs `1` vs `≤8`. If any two of the three coincide, the
gate does not discriminate and VOID-A fires.

*(End of pre-registered section. Everything below §0 was written after the
measurements it reports.)*

---

## 1. OD-1 — the exact diameter, measured

Object: the directed graph of `verify_derivation.py` claim C11. Nodes
`(lambda, k)`, `lambda in GF(2^8)^*`, `k in {0,1,2,3}` — 1020 nodes. Edges
`(lambda,k) -> (lambda * M[j][k], j)` for every `j in {0,1,2,3}`, with `M` the
AES MixColumns circulant of first row `(02,03,01,01)`, `GF(2^8)` modulus
`0x11B`. All-pairs BFS from every one of the 1020 nodes, forward graph and
reverse graph. Zero edges are dropped (no entry of `M` is zero).

| quantity | forward graph | reverse graph |
|---|---|---|
| nodes | 1020 | 1020 |
| **diameter** | **30** | **30** |
| radius | 30 | 30 |
| eccentricity distribution | `{30: 1020}` — every node has eccentricity exactly 30 | `{30: 1020}` |
| realizing pair at distance 30 | `(lambda=0x01, k=0) -> (lambda=0x84, k=0)` | `(lambda=0x01, k=0) -> (lambda=0x96, k=0)` |
| ordered pairs with no path | 0 | 0 |

**d = 30.** The eccentricity distribution is a single value: the graph is
distance-regular enough in this respect that radius equals diameter and every
node sits at distance ≤ 30 from every other, with the bound attained from every
node. No estimate appears anywhere; the figure is the output of an exhaustive
all-pairs BFS taking 0.74 s.

**Strong connectivity re-confirmed independently of C11**, three ways, all
agreeing: forward reachability from `(0x01, k=0)` = 1020; reverse reachability
from `(0x01, k=0)` = 1020; Kosaraju SCC decomposition = **1** component of size
1020; and, redundantly, the all-pairs BFS found 0 ordered pairs with no path.

### 1.1 The 2-step graph `G^2`, which is what the extension actually needs

`PROP-701-I`'s engine advances by **one graph edge per interface**, but only
produces a *global* (as opposed to hyperplane-local) invariance after **two**
interfaces — Step 1 at one interface, Step 2's union upgrade at the next.
Global statements therefore live on **walks of even length**. The relevant
object is `G^2`, whose edges are the length-2 walks of `G`:

| quantity | `G^2` |
|---|---|
| nodes with a self-loop | **1020 of 1020** |
| strongly connected | yes, 1 SCC |
| **diameter** | **16** |
| radius | 16 |
| eccentricity distribution | `{16: 1020}` |
| realizing pair | `(0x01, k=0) -> (0x84, k=2)` at distance 16 |

Every node of `G^2` carries a self-loop. That is not an accident: with the AES
circulant, `M[i][k] * M[k][i] = c[t] * c[-t]` with `t = (k-i) mod 4`, and at
`t = 2` this is `01 * 01 = 1`, so `(lambda,k) -> (lambda*M[k+2][k], k+2) ->
(lambda, k)` is a 2-walk returning to the start, for every node. Consequently
reachability in `G^2` is **monotone**: once a node is held it is held forever,
and "reachable in exactly `n` steps" equals "reachable in at most `n` steps".
This is what makes the counting below a clean bound rather than a parity
argument.

### 1.2 `n*`: the exact number of `G^2` steps the argument needs

A `pi^(0)`-collision `Delta` with least nonzero coordinate index `i` and value
`mu = Delta_i` yields, after two interfaces, **global** invariance of `pi^(2)`
at the **four** nodes `S0(mu,i) = {(mu * M[k][i], k) : k = 0..3}` (§3, Step
1–2). Each further pair of interfaces advances every held node by one `G^2`
step. Define

```
n* = max over the 1020 possible (mu, i) of the number of G^2 steps
     needed for S0(mu,i) to cover all 1020 nodes.
```

**Measured: `n* = 15`, attained for every one of the 1020 starting pairs
(`distribution: {15: 1020}`); witness `mu = 0x01, i = 0`.**

So starting from four nodes rather than one buys exactly one step against the
`G^2` diameter of 16, and buys it uniformly.

---

## 2. GATE-701-C v2 — construction validation of the nulls, run BEFORE the gate

Executed as `--phase construction`, whose output is in
`od1_gate701c_results.json` under `construction`. This phase inspects the three
*matrices* only; it computes no gate reading.

| property | `target` `(02,03,01,01)` | `null_1` identity | `null_2` `(01,01,01,06)` |
|---|---|---|---|
| all entries nonzero | **yes** | no (12 zero entries) | **yes** |
| rank over `GF(2^4)` | 4 | 4 | **4** |
| invertible | yes | yes | **yes** |
| subgroup generated by entries | `{1..15}` | `{0x1}` | **`{0x1, 0x6, 0x7}`** |
| subgroup order | 15 (= whole group) | 1 | **3** |
| subgroup proper | **no** | yes (trivial) | **yes** |
| `(lambda,k)` graph over `GF(2^4)`: nodes | 60 | 60 | 60 |
| edges dropped (target scalar 0) | 0 | 180 | 0 |
| SCC count | **1** | 60 | **5** |
| SCC sizes | `{60: 1}` | `{1: 60}` | **`{12: 5}`** |
| strongly connected | **yes** | no | **NO** |

**The redesigned `null_2` is exactly the intended object, verified before the
gate was run.** Its five components of size 12 are precisely the five cosets of
`H = {1,6,7}` in `GF(2^4)^*` — `{1,6,7}`, `{2,12,14}`, `{3,9,10}`,
`{4,11,15}`, `{5,8,13}` — each carrying all four indices `k`. The index moves
freely within a component (the matrix has `01` entries off the diagonal) but
the scalar can never leave its coset, because every entry lies in `H`. That is
the negation of the **necessary** ingredient of Step 3 — strong connectivity of
the `(lambda,k)` graph — with Step 2's **sufficient** hypothesis (all entries
nonzero) left standing and true.

Note the contrast with `null_1`, which also fails strong connectivity but by a
different and cruder mechanism: 180 of its 240 edges leave the node set
entirely (target scalar 0), so it degenerates to 60 isolated fixed points. It
is a sensitivity anchor, not a Step-3 negation, and both facts are now recorded
rather than assumed.

---

## 3. The OD-1 extension, as a numbered proposition with a derivation

Notation as in `PROP-701-I`: `F = GF(2^8)`, `M` the AES MixColumns matrix with
columns `m_0..m_3`, `Phi = ARK . MC . SR` the super-box interface, `k_j` the
round-key word added at the interface (on differences all `k_j = 0`). Write

> `A_r(lambda, k)` := "`pi^(r)` is invariant under the global translation
> `w -> w + lambda*m_k` of `F^4`".

### Proposition 801-1 (layer-dependent families die after a bounded number of interfaces)

**Hypotheses.**

- (H1) `pi^(r) : F^4 -> X_r`, `r = 0,1,...,L`, is a family of maps, `pi^(r)`
  applied to **every** super-box word at layer `r` (the same map at all four
  word positions within a layer; the maps at different layers are unrelated).
- (H2) For each `r = 0..L-1` the family propagates deterministically across
  interface `r`: there are functions `F_j^(r) : X_r^4 -> X_{r+1}` such that for
  **every** state `s` and every output word index `j`,
  `pi^(r+1)( word_j(Phi(s)) ) = F_j^(r)( pi^(r)(word_0(s)), ..., pi^(r)(word_3(s)) )`.
- (H3) `pi^(0)` is **not injective**.
- (H4) `L >= 2 + 2*n*`, where `n*` is the covering number of §1.2.
  **Measured: `n* = 15`, so the hypothesis reads `L >= 32`.**

**Conclusion.** `pi^(L)` is constant. (Indeed `pi^(r)` is constant for every
`r >= 32`.)

**Derivation.**

*Lemma 1 (Step 1, layer-indexed).* Let `pi^(r)(a) = pi^(r)(b)`, `Delta = a+b !=
0`. Compare two states identical except that input word 1 is `a` resp. `b`.
Under ShiftRows with offsets `(0,1,2,3)`, input word 1 contributes exactly one
coordinate `i_j = (1-j) mod 4` of the pre-MixColumns vector of output word `j`,
so the two output words `j` differ by `Delta_{i_j} m_{i_j}`. All four inputs of
`F_j^(r)` agree, so the two output words have equal `pi^(r+1)`. Hence for every
`i` with `Delta_i != 0`,
`pi^(r+1)(u) = pi^(r+1)(u + Delta_i m_i)` for all `u` in the affine hyperplane
`U_i = { M y + k_j : y_i = a_i }`, `j = (1-i) mod 4`. ∎

This is `PROP-701-I` Step 1 with the layer index carried through. Nothing but
(H2) at the single interface `r` is used.

*Lemma 2 (Step 2, layer-indexed — and the exact point of departure from
`PROP-701-I`).* Fix `i` with `Delta_i != 0` and put `v = Delta_i m_i`. Every
entry of `M` is nonzero (`verify_derivation.py` C9), so all four coordinates of
`v` are nonzero. For each `u in U_i` the pair `(u, u+v)` is a `pi^(r+1)`
collision; applying **Lemma 1 at interface `r+1`** gives, for every `k`,
`pi^(r+2)(w) = pi^(r+2)(w + v_k m_k)` for all `w` in
`{ M y + k_j : y_k = u_k }`. As `u` ranges over `U_i`, `u_k = sum_l M[k][l] y_l
+ (k_j)_k` sweeps all of `F` (`y_i` fixed, `y_l` free for `l != i`, `M[k][l] !=
0`), so the union of these hyperplanes is `F^4`. Hence
`A_{r+2}( Delta_i M[k][i], k )` for every `k = 0..3`. ∎

**This is exactly where `PROP-701-I` consumes round-independence, and exactly
what replaces it here.** `PROP-701-I` re-applies Step 1 *with the same `pi`* at
the next interface, which is legitimate only because the family is
round-independent; the validator located this in
`derivation_and_ideation_review.md` §7.3 ("`u` and `u+v` are output words of
one interface being fed as input words to the next, and the argument needs the
*same* `pi` there"). Lemma 2 re-applies Step 1 with `pi^(r+1)` at interface
`r+1`, which is precisely hypothesis (H2) for that interface. The departure
therefore costs **bookkeeping, not a new assumption**: the invariance lands two
layers downstream instead of on the same map. That shift is the entire
difference between the round-independent and the layer-dependent case, and it
is why the layer-dependent case needs a *quantitative* input — the graph
distance — where `PROP-701-I` needed only strong connectivity.

*Lemma 3 (one `G^2` step per two interfaces).* Suppose `A_r(lambda,k)`. Then
every pair `(w, w + lambda m_k)` is a `pi^(r)` collision with
`Delta' = lambda m_k`, whose `i`-th coordinate is `lambda M[i][k] != 0` for
every `i`. Lemmas 1–2 applied to `Delta'` give
`A_{r+2}( lambda M[i][k] M[k'][i], k' )` for every `i` and `k'`. Those are
exactly the nodes reachable from `(lambda,k)` by a walk of length 2 in the
`(lambda,k)` graph, i.e. the `G^2`-successors of `(lambda,k)`. ∎

*Lemma 4 (monotonicity).* Every node of `G^2` carries a self-loop — measured,
1020 of 1020 (§1.1), with the reason `M[k+2][k] M[k][k+2] = c[2] c[2] = 01*01 =
1`. Hence if `A_r` holds at a node, `A_{r+2}` holds there too, and the set of
nodes carrying an `A`-statement is nondecreasing as the layer index advances by
2. ∎

*Assembly.* By (H3) pick `a != b` with `pi^(0)(a) = pi^(0)(b)`, set
`Delta = a+b != 0`, let `i` be the least index with `Delta_i != 0` and
`mu = Delta_i`. Lemmas 1–2 at `r = 0` give `A_2` at the four nodes
`S0(mu,i) = { (mu M[k][i], k) : k = 0..3 }`. Lemmas 3–4 give, for every
`n >= 0`, that `A_{2+2n}` holds at every node within `n` `G^2`-steps of
`S0(mu,i)`. By the measurement of §1.2, `n = n* = 15` covers all 1020 nodes,
and it does so for **every** one of the 1020 possible `(mu,i)`. Hence `A_32`
holds at every node: `pi^(32)` is invariant under `lambda m_k` for every
`lambda in F^*` and every `k`. The translations leaving a map invariant form a
subgroup of `(F^4,+)`, so this set contains the `GF(2)`-span of
`{ lambda m_k }`, which is the `F`-span of `{m_0,...,m_3} = F^4` because `M` is
invertible. So `pi^(32)` is constant.

Finally, constancy propagates forward: if `pi^(r)` is constant then by (H2)
each `F_j^(r)` is evaluated at a single argument tuple, so `pi^(r+1)` is
constant on `{ word_j(Phi(s)) : s }`, which is all of `F^4` because `Phi` is a
bijection. Hence `pi^(r)` is constant for every `r >= 32`, and in particular
`pi^(L)` is constant for every `L >= 32`. ∎

### Corollary 801-2

A layer-dependent family of per-super-box-word projections in which **every**
member is genuinely lossy (neither injective nor constant) cannot propagate
deterministically, in the sense of (H2), across **32 or more consecutive
interfaces**. Such a family survives at most **31** consecutive interfaces.

### 3.1 What this does and does not license — stated plainly

**It does extend `PROP-701-I` from round-independent objects to
layer-dependent ones, with an explicit finite constant, and the constant is
better than OD-1 guessed.** OD-1's text estimated "more than roughly `2d`
rounds", which with the measured `d = 30` would be about 60. The correct
constant is `2 + 2n* = 32` interfaces — about `d + 2`, not `2d` — because the
relevant object is `G^2` (diameter 16, covering number 15) rather than `G`, and
because starting from four nodes rather than one buys a uniform step. Recorded
as a correction of the OD-1 estimate. Per D-705-4 the argument is *not*
described as iterating "an unbounded number of times": it iterates exactly
`n* = 15` times, and that number is measured.

**It does not close OD-1 in any regime this campaign is asking about, and the
residual is real.** `RQ-AES-001` scopes in-scope round counts to 3–7. Under
`PROP-701-I`'s own identification of one interface with one round, the
proposition first says anything at 32 interfaces. Every layer-dependent family
of interest to this campaign lives strictly inside the untouched window.
Concretely the residual is:

- **R1 (the decisive one).** Layer-dependent families propagating across at
  most 31 interfaces are entirely untouched. All in-scope round counts fall
  strictly inside that window, so for the regime this campaign actually studies
  the extension buys nothing. A small diameter would have collapsed this hole;
  `d = 30` on 1020 nodes does not.
- **R2.** Nothing here shows the constant 32 is tight. The true minimal `L` may
  be far smaller — the argument only ever tracks *one* translation family at a
  time and throws away every other consequence of (H2). Asserting a smaller
  constant without deriving it would be a fabrication, and none is asserted.
- **R3.** (H1) still requires the same `pi^(r)` at all four word positions
  within a layer, and (H2) still quantifies over **every** state `s`. Those are
  the two D-705-5 holes (§5), and Proposition 801-1 does not touch either.
- **R4.** Every other `PROP-701-I` scope restriction is inherited unchanged:
  single 32-bit word domain (OD-2 open), single-state rather than set-valued
  (OD-3 open), strictly deterministic rather than bounded-branching (OD-4
  open).
- **R5.** The identification of "one interface `Phi`" with "one round" is
  `PROP-701-I`'s own modelling convention, carried over here and **not**
  established by anything in this task. The proposition is stated in
  interfaces; the round translation is the report's convention, flagged as
  such.

**Verdict on the OD-1 question as posed.** The extension **follows** and is
stated above as Proposition 801-1 with a derivation. It does **not** collapse
the largest hole in the closure: the residual R1 is real, because the measured
diameter is 30, not small.

---

## 4. GATE-701-C v2 — measured readings and the discrimination verdict

Run once per matrix, exhaustively over all 65535 nonzero `Delta in GF(2^4)^4`,
after §0 was on disk and after the construction validation of §2.

| matrix | pre-registered prediction (§0.4) | **measured reading** | agrees? |
|---|---|---|---|
| `target` `(02,03,01,01)` | 65535/65535 reach dim 16 | **65535/65535 at dim 16**; histogram `{16: 65535}` | **yes** |
| `null_1` identity | 0/65535 reach dim 16, stall at dim **1** | **0/65535**; histogram `{1: 65535}`, min = max = 1 | **yes** |
| `null_2` `(01,01,01,06)` | 0/65535 reach dim 16, every dim **≤ 8** | **0/65535**; histogram `{8: 65535}`, min = max = 8 | **yes**, and the secondary expectation "exactly 8" also holds |

Runtime: 9.86 s / 0.21 s / 3.79 s. Re-execution reproduces every number
byte-identically apart from the timing fields (§6.3).

**VOID conditions (§0.5):**

- **VOID-A — does NOT fire.** Neither null returns the target's reading:
  16 vs 1, and 16 vs 8.
- **VOID-B — does NOT fire.** `null_1` stalls, at dimension 1.
- **VOID-C — does NOT fire.** The target reaches 65535/65535 at dimension 16.
- **FAIL_ESCALATE — does not fire.** No `Delta` closes below 16 on the target,
  so no surviving lossy projection exists in the analogue and no error in
  `PROP-701-I`'s engine is exhibited.

### 4.1 EXPLICIT VERDICT

> **DOES THE REDESIGNED GATE DISCRIMINATE? — YES.**
>
> The three readings are pairwise distinguishable and qualitatively, not by a
> threshold: **dimension 16 (target) / dimension 1 (`null_1`) / dimension 8
> (`null_2`)**, each uniform over all 65535 `Delta`. The gate's pre-declared
> VOID condition does not fire on either null.

Recorded restrictions on that verdict, so it is not read for more than it is:

1. It is a statement about **`GATE-701-C` v2 as an instrument**: the
   falsification gate can now tell an AES-shaped interface apart from an
   interface whose scalar orbit is confined. It is **not** itself a closure, an
   evidence-strength assignment, or a licence for any state transition. Whether
   `D-705-1` is thereby discharged is the Coordinator's call in
   TASK-20260801-805, on the independent review in TASK-20260801-804.
2. `null_2`'s stall was **predicted by a hand argument before measurement**
   (§0.3) and the measurement matched it exactly, including the value 8. The
   discrimination is therefore structural and understood, not an unexplained
   numeric gap. Its mechanism is named: the closure is trapped inside `S^4` for
   a `GF(4)`-line `S`.
3. **Exactly one redesigned null was built and exactly one was run.** No
   candidate null was discarded on the basis of its reading; the only
   enumeration performed (§0.2) tested *invertibility*, was fixed a priori, and
   is recorded in full. Had `null_2` read 65535/65535 at dimension 16, that
   would have been reported as a second VOID and the work would have stopped
   there.
4. The gate never touches SubBytes, so it cannot be reading an S-box-driven
   activity pattern — the direct repair of EV-AES-001 defect I-3, unchanged
   from the BATCH-002 design.
5. The gate is a `GF(2^4)` analogue. It confirms the *engine* of the argument
   in a fully enumerable scaled-down setting. It is not evidence about
   `GF(2^8)`, and certainly not about AES.

---

## 5. The two D-705-5 scope holes, named

The TASK-20260731-705 validator recorded that `PROP-701-I`'s scope list, which
names OD-1..OD-4, omits two further holes. Naming them, as required:

**Hole (i) — word-position-dependent families `pi_0, pi_1, pi_2, pi_3` within a
single layer.** `PROP-701-I` (and Proposition 801-1's hypothesis (H1)) assume
the *same* map at all four word positions of a layer. A family indexed by word
position is neither OD-1 (layer-dependence) nor OD-2 (multi-word domain). It
breaks the index bookkeeping of Steps 1–2: Step 1 would yield an invariance for
`pi_j` at output index `j`, while Step 2's re-application needs a collision pair
with equal `pi_1` at an *input* index, and the indices do not line up. No
replacement argument is offered.
**Does this task touch it? NO.** Proposition 801-1 assumes (H1) exactly as
`PROP-701-I` does, and the gate is an experiment about the matrix, not about
the index structure of the projection family. The hole stands open, untouched.

**Hole (ii) — restriction of the "for EVERY state `s`" quantifier to a
structured subset of states.** (H2) demands deterministic propagation for every
state. An object required to propagate only on a structured subset — a coset, a
delta-set, a set defined by fixing some bytes — falls outside the hypothesis
entirely. It is adjacent to OD-3 (set-valued objects) but is not the same
thing: here the object is still single-state-valued, and only the *domain of
the propagation requirement* shrinks. Both Step 1's hyperplane construction and
Step 2's sweep of `u_k` over all of `F` consume the full quantifier, so the
proof does not survive the restriction even partially.
**Does this task touch it? NO.** Proposition 801-1 uses the full quantifier at
every interface, twice per two interfaces. The hole stands open, untouched.

---

## 6. Execution record, deviations, and what did not run

### 6.1 What was run, in order

1. `--phase graph` — OD-1 diameters. Exit 0, 0.77 s wall.
2. `--phase construction` — null construction validation. Exit 0, 0.03 s wall.
3. **§0 of this report written to disk** (2026-08-01T08:05:45Z), before any
   gate reading existed.
4. `--phase gate` — the gate. Started 2026-08-01T08:05:55Z, exit 0, 13.9 s
   wall.
5. Reproducibility re-runs of all three phases (§6.3).

Exact commands, exit statuses, timestamps and outputs are in
`od1_gate701c_results.json`.

### 6.2 Deviations from the handoff protocol

**One, recorded.** The handoff asks for "the diameter `d`" and for the OD-1
extension "to objects surviving more than roughly `2d` rounds". The diameter is
reported exactly as asked (`d = 30`, §1). The extension argument, however, is
governed not by `d` but by the covering number `n* = 15` of the 2-step graph
`G^2`, because a global invariance statement is produced only every *two*
interfaces. Both quantities are computed and reported; the proposition is
stated in terms of the one that the derivation actually uses, and the
discrepancy with the OD-1 estimate is stated explicitly in §3.1 rather than
silently absorbed. No pre-registered prediction was adjusted: the OD-1 "`2d`"
figure is an estimate in a BATCH-002 open-direction note, not a pre-registered
prediction of this task, and the BATCH-002 record is left unedited.

No other deviation. No candidate null was discarded on a reading; no prediction
was altered after measurement; no run is omitted from the manifest.

### 6.3 Reproducibility

Each of the three phases was executed twice. The JSON outputs are **identical
modulo the `wall_clock_seconds` fields**, which are measurements and vary. The
`construction` phase output is byte-identical including timing. There is **no
randomness anywhere in the script** — every computation is exhaustive over a
finite set in a fixed enumeration order — so `seeds: {}` in the manifest
records the absence of any seed rather than inventing one.

### 6.4 Checks that did NOT run, with reasons

- **`python3 -m orchestration.adapter doctor --probe` — RUN, and it did NOT
  verify a model.** Exit 0, but every backend reported unusable (no API key
  set) or unreachable (`local` at `http://localhost:8000` refused). No
  `resolved_model_id` was confirmed by any backend. `model_verified` therefore
  remains **false**; the identifier recorded in every inference block here is
  unverified configuration, exactly as in BATCH-001 and BATCH-002.
- **Independent third implementation of the closure routine — NOT written.**
  The gate's arithmetic is cross-checked only against the hand argument of
  §0.3 (which predicts `null_2` = 8 exactly, matched) and against the
  TASK-20260731-705 validator's independent implementation for the `target` and
  `null_1` readings, which agree with this run (16 and 1). No third
  implementation was written; budget and scope did not call for one, and this
  is recorded rather than glossed.
- **`verify_derivation.py` — NOT re-executed and NOT modified.** It is a
  committed BATCH-002 artifact. Its claim C11 was **re-derived from scratch**
  in this task's own script rather than trusted, and the results agree
  (1020 forward-, 1020 reverse-reachable, one SCC).
- **Cross-model independence — NOT obtained**, campaign-wide, under
  inference-amendment `0137a051`. This session cannot supply a closure
  attestation and does not.
- **No literature check of any kind was performed**; no primary source is
  reachable. Any recollection anywhere in this campaign is
  `unverified-from-memory`. No novelty claim is made or implied.

### 6.5 Budget

Declared 1500 s wall clock, 4 GB memory, maximum 6 runs. Actual compute across
all six script invocations: **28.836 s** total (the sum of the per-phase
`wall_clock_seconds` recorded in the manifest); peak memory was not
instrumented and is stated only as an unmeasured bound, well under 100 MB
(largest structures are 1020-node adjacency lists and a 16-element `GF(2)`
basis). The stop condition was not approached and was not reached.

### 6.6 What this report is not

No closure is proposed. No `reject_scoped` is proposed. No hypothesis status is
changed, no evidence strength is assigned, no knowledge promotion is requested,
and no ledger record is created. Nothing here asserts anything about AES at any
round count, about full-round AES, or about the security of any deployed
system. `GOAL-AES-001` completion is not proposed and no attestation is
recorded.
