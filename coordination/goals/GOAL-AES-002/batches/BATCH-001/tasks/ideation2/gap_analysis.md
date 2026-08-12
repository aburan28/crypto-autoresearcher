# Full-round AES, second pass: attacking the gap the first pass's ceiling leaves open

Prepared against `RQ-AES-002` / `GOAL-AES-002` BATCH-001. **Nothing in this file is a claim
about AES security, a distinguisher, a key recovery, a speedup, or an impossibility
statement.** It is a derivation of where the first pass's obstruction register is wrong, an
answer to whether the O-3 premise is forced, an enumeration of a fourth object class, and an
honest accounting. No official state is changed. Nothing is written to the repository or the
ledger.

---

## 0. Epistemic preamble — read before using any number below

**0.1 Timestamps.** The `Bash` tool is not enabled in this session, so `date -u` could not be
run and **no wall-clock UTC stamp exists for this session**. The harness-supplied date is
**2026-08-01**. Section boundaries are marked by ordinal (S1 = context ingestion, S2 =
derivation, S3 = drafting) and were reported in the session transcript. Writing an invented
UTC time would be a fabrication under `AGENTS.md` rule 9, so none is written. The halt
discipline `start + 2400 s` could not be enforced by clock; it was enforced by scope (two
candidates, no third exploratory leg). This is a defect of this session's record and is
declared rather than concealed. It is the identical defect the first pass declared.

**0.2 Sources.** No primary cryptographic source was read and none is reachable
(`eprint.iacr.org`, `csrc.nist.gov`, `arxiv.org` unreachable under this campaign's network
policy — RQ-AES-002 `provenance`). No WebSearch was performed in this session, so this file
contains **not even secondary-summary corroboration**. Every recalled fact carries an
explicit `UNVERIFIED-FROM-MEMORY` label and a recall confidence. Per `RQ-AES-002` R3 the
prohibition is symmetric: **no recalled figure is used to promote or to dismiss anything**,
in either direction.

**0.3 What is derived here versus recalled.** Derivations D-1 through D-6 below are exact
arithmetic or elementary algebra performed in text in this session. They are re-derivable in
minutes and are **not** quoted from any document. Everything else is labelled.

**0.4 Zero compute.** No program was run. No AES measurement of any kind was taken. Every
"measured" quantity cited is measured in a **cited prior record of this repository**
(`gate_results.json` / `RUN-FRGATES-20260801-001`), never here.

**0.5 CM-1 is not committed.** `RQ-AES-002` constraints make cost model CM-1 a **hard
pre-dispatch gate**: no cryptanalytic measurement and no cost claim may be dispatched until
CM-1 exists as a committed, independently reviewed artifact. The two gates proposed here are
therefore **proposals blocked on CM-1**, and every cost figure in this file is an
**unadjudicated number**, not evidence. Stated up front so that nothing below reads as a
cost claim.

**0.6 The anti-laundering clause, discharged once and binding on every margin below.**
Every margin in this file is stated against the **DEFINITIONAL exhaustive-key-search
reference** for the named key size (2^128 / 2^192 / 2^256 full-AES evaluations), under a cost
model that is **not yet frozen as CM-1**; and the comparison against the **published state of
the art is UNADJUDICABLE in this environment and is asserted in neither direction**
(`RQ-AES-002` R5). Where a sentence below states a margin, that clause is incorporated by
reference into it.

---

## 1. What the first pass established, taken as given and not re-litigated

- **O-3, the amortization ceiling.** Any attack that *enumerates* 2^kappa candidates and pays
  at least one S-box-equivalent per candidate is floored at 2^kappa / N_S with
  N_S = 200 / 224 / 276. Maximum possible gain 7.64 / 7.81 / 8.11 bits. Re-derived
  independently by the dispatching session from FIPS-197; taken as exact.
- Every data-path object dies at 4-6 rounds against 10-14. This campaign's own objects died
  at 0.5-2 rounds (`EV-AES-001` B-5, `KN-FIND-017`).
- CAND-FR-2 measured dead at round 4 of 10 (`gate_results.json` GATE 2: AES-128 death rounds
  2-4, AES-256 3-5, at a 5-sigma floor of 2^-7.18 relative, N = 2^19 — the floor is
  load-bearing and is restated wherever that reading is used).
- The AES-128 key schedule is a bijection, so `sigma(K)` linearization is a change of
  coordinates (LP-1); a key mask does not shorten the data path (LP-2).
- **O-5 as written: generic MQ over a quadratic representation needs >= 1408 GF(2) variables,
  giving >= 2^704.**

**Section 3 of this file argues O-5 is wrong as a bound on the algebraic lane, and by roughly
325-460 bits.** That is this pass's principal quantitative finding. It is a correction to an
obstruction, not a result about AES, and it makes the algebraic lane *worse than exhaustive
search by 118-251 bits* rather than by 576 bits — still hopeless, but in a different regime,
with a different required structural gain, and with a different gate.

---

## 2. Is the O-3 premise forced? — the direct answer

O-3 has two premises, and the first pass conflated them:

- **(P-a)** the attack enumerates 2^kappa candidates, touching each individually;
- **(P-b)** it pays at least one S-box-equivalent of marginal work per candidate.

**(P-b) is not a law. It fails exactly when the candidate test *factors*.** If the predicate
`[E_K(P) = C]` can be written as a match between a forward function of `(K_1, P)` and a
backward function of `(K_2, C)` on an m-bit projection, then 2^kappa candidates are tested at
cost 2^{kappa/2} evaluations plus matching, i.e. **2^{-kappa/2} S-boxes per candidate** —
sublinear, and O-3's floor evaporates. So the honest answer to the directive's question 2 is:

> **The O-3 premise is breakable in principle, and the mechanism that breaks it is a
> functional decomposition of the candidate test — a meet-in-the-middle factorization — not
> a cleverer enumeration order. O-3 does not bound the space of attacks; it bounds the space
> of attacks whose candidate test does not factor.**

The next question is whether AES's test factors. It does not, and the argument is short.

**Derivation D-3 (exact-factorization impossibility for full-round AES-128).**
Fix a partition `K = K_1 || K_2` with both parts nonempty. For an exact MITM factorization
there must exist an intermediate bit `b` that is (i) computable from `(P, K_1)` alone and
(ii) computable from `(C, K_2)` alone. Requirement (i) forces `b` to have **zero functional
dependence on every bit of K_2**; requirement (ii) forces zero dependence on every bit of
`K_1`. AES reaches full key-and-state dependence in **two rounds** forward from `P` (branch
number 5 of MixColumns plus ShiftRows across columns; recall HIGH on the branch number,
locally recomputable) and symmetrically two rounds backward from `C`. Hence bits satisfying
(i) live at round <= 1 and bits satisfying (ii) live at round >= 9, and for 10 rounds the two
sets are disjoint. **No exact MITM factorization of the full-round AES-128 candidate test
exists for any nontrivial key partition.** The same argument gives the same conclusion for 12
and 14 rounds a fortiori.

**Derivation D-4 (what the biclique family actually does, and why it does not escape O-3).**
The published full-round family (recall MEDIUM-HIGH that it exists; figures not used here in
either direction) escapes D-3 not by finding an exact factorization but by (a) constructing a
structure valid only on a *small* key subspace and (b) *recomputing* the changed part of the
computation per candidate. Step (b) is exactly premise (P-b): it pays a nonzero number of
S-boxes per candidate by construction. **So the family that reaches round 10 is inside O-3 by
construction, and O-3 survives against it.** The measured instance is consistent: GATE 1
measured rho_min = 0.77 for AES-128 over an exhaustive sweep of all 65535 nonzero 16-bit
key-difference supports and all 11 splice points, i.e. 154 of 200 S-boxes recomputed per
candidate — 7.27 bits *above* the O-3 class ceiling, not below it.

**Conclusion of section 2, and it is the pivot of this whole pass.**
Combining D-3 and D-4: within the enumerative world, the O-3 premise is **forced for
full-round AES** — not by S-box counting, but by two-round full diffusion, which is a
*different and stronger* obstruction than O-3 itself. Therefore:

> **The only route that escapes O-3 is one that never enumerates candidates at all.** That is
> the algebraic / solving lane, class C. Gaps 1 and 2 of the directive collapse into a single
> question, and section 3 is that question.

This also sharpens the first pass's framing. The first pass said class B is capped at 7.64
bits by O-3. The sharper statement is: class B is capped at 7.64 bits by O-3, **and cannot
approach that cap**, because approaching it requires a near-total factorization of the test
which D-3 forbids; GATE 1's measured 7.27-bit shortfall against the ceiling is the first
measured instance of that.

---

## 3. Gap 1 — the structured-MQ question, and why O-5 is wrong

The directive asks for the actual solving complexity of the structured system rather than the
generic bound. Answer, in four parts.

### 3.1 O-5 bounds the wrong solver family

O-5 says: a quadratic representation of 10-round AES-128 needs N >= 1408 GF(2) variables, and
a generic MQ solver running in 2^{cN} with c >= 0.5 therefore costs >= 2^704.

That is a correct statement **about solvers whose exponent is linear in the variable count**
(the exhaustive-search and polynomial-method line). It is **not** a bound on the
Gröbner/XL/Macaulay family, whose cost is *not* exponential in N. For that family the cost is

```
cost  ~  C(N, <= d_reg)^omega   ~   C(N, d_reg)^omega ,      memory ~ (columns)^2 dense
                                                              or (rows x row-weight) sparse
```

with `d_reg` the degree of regularity (equivalently the degree the solver actually reaches).
`d_reg` is bounded by N but is typically far below it. **Applying a 2^{cN} bound to a family
whose cost is C(N, d_reg)^omega is a category error, and it is the single largest defect in
the first pass's obstruction register.**

### 3.2 Derivation D-1 — what d_reg would have to be

Exact binomial arithmetic at N = 1408 (the first pass's variable count; the alternative
count 1600, obtained by carrying the 40 key-schedule S-box outputs and 9 x 128 round-boundary
state bits explicitly, moves every figure below by under 2 bits per unit of d and is noted
rather than hidden):

| d | log2 C(1408, d) | cost at omega = 2 | cost at omega = 2.37 |
|---|---|---|---|
| 5 | 45.4 | 2^90.8 | 2^107.6 |
| 6 | 53.26 | 2^106.5 | **2^126.2** |
| 7 | 60.91 | **2^121.8** | 2^144.4 |
| 8 | 68.36 | 2^136.7 | 2^162.1 |

> **A Gröbner/XL attack on the 1408-variable quadratic representation of full-round AES-128
> beats the DEFINITIONAL exhaustive-key-search reference of 2^128 full-AES evaluations — under
> a cost model that is NOT yet frozen as CM-1, and with the published-state-of-the-art
> comparison UNADJUDICABLE in this environment and asserted in neither direction — if and
> only if `d_reg <= 6` at omega = 2.37, or `d_reg <= 7` at omega = 2.**

That is a sharp, checkable, single-number requirement, and it replaces "2^704" as the honest
statement of what the algebraic lane needs. It also tells you exactly what to measure.

### 3.3 Derivation D-2 — how far the semi-regular prediction sits from that

The number of quadratic relations M per S-box is **derivable locally, not recalled**: the
space of GF(2)-polynomials of degree <= 2 in the 16 in/out variables has
`1 + 16 + C(16,2) = 137` monomials; evaluating them on the 256 points of the S-box graph
gives a 137 x 256 GF(2) matrix whose corank is the relation count. Building and ranking that
matrix is milliseconds of pure Python. The commonly recalled value is 39 per S-box (recall
MEDIUM, **UNVERIFIED-FROM-MEMORY**, used here only to size the arithmetic and replaced by the
derived rank in the proposed gate). Taking M = 200 x 39 = 7800 for AES-128:

The Macaulay matrix at degree d has `C(N,d)` leading columns and about `M x C(N, d-2)` rows,
so it becomes square at

```
C(N,d) <= M x C(N,d-2)   <=>   (N-d)(N-d+1) / (d(d-1))  <=  M
                          =>   (N-d)/d <= sqrt(M) = 88.3   =>   d >= N/89.3 ~ 15.8
```

so **d\* ~ 16** for (N, M) = (1408, 7800). This crossover ignores trivial (Koszul) syzygies,
which reduce the effective row supply and therefore push the true semi-regular `d_reg`
slightly *higher*; d\* ~ 16 is a lower proxy, not the value. Cost there:
`log2 C(1408,16) ~ 123.0`, giving

```
cost at d ~ 16 :   2^246  (omega = 2)   to   2^291  (omega = 2.37)
```

Sensitivity: if the derived M were 4000 rather than 7800, d\* ~ 22 and the band moves to
2^320 - 2^379. So the honest band is:

> **Corrected obstruction O-5' (replacing O-5).** Under the standard dense-Macaulay cost
> model, the Gröbner/XL family on full-round AES-128 costs roughly **2^246 to 2^379** at the
> semi-regular crossover degree — **not 2^704**. O-5 overstates the algebraic lane by roughly
> **325 to 460 bits**. The lane still misses the DEFINITIONAL exhaustive-key-search reference
> of 2^128 by **118 to 251 bits** (published-SOTA comparison unadjudicable here, asserted in
> neither direction), and closing that gap requires the true `d_reg` to fall from ~16-22 to
> **<= 6-7**, a factor of about 2.3 to 3.5 — not a factor of 100.

Memory honesty, since the profile requires it beside time: at d = 6 the Macaulay matrix has
2^53.3 columns, so dense memory is ~2^106 bits and sparse (Wiedemann, row weight <= 137)
memory is ~2^57 words. Both are physically unrealizable on any machine that will ever exist,
and both are far below 2^128. **An algebraic attack in this lane would be a time-only win at
astronomically infeasible memory, and any Pareto comparison must say so in the same breath.**

### 3.4 Derivation D-5 — the GF(2^8) representation buys exactly nothing, and the cancellation is structural

The directive asks whether the GF(2^8) representation gives a smaller system. It does not,
and the reason is exact rather than empirical.

- Over GF(2^8) the S-box's nonlinear core is inversion, and `y' = x^{-1}` is the single
  quadratic relation `x * y' = 1` (with the `Inv(0)=0` convention handled separately). Two
  variables, one quadratic equation, per S-box. That looks like a 8x reduction in variable
  count against the GF(2) picture.
- But the AES S-box is `S = L o Inv` with `L` **GF(2)-affine and not GF(2^8)-affine**. As a
  map on GF(2^8), `L(y') = sum_{i=0}^{7} lambda_i y'^{2^i} + 0x63` is a linearized polynomial
  of **degree 2^7 = 128**. A system carrying it is degree-128, and `C(400, 128)` is
  astronomically above 2^128 — the representation is worse, not better.
- Restoring quadraticity requires introducing the **Frobenius conjugates** `x^{2^i}` as
  independent variables (the BES-style embedding; recall MEDIUM-HIGH that such an embedding
  exists, **UNVERIFIED-FROM-MEMORY**, and used here only as the name for a construction that
  is derived above rather than cited). That multiplies the variable count by exactly the
  extension degree, **8**.

> **Obstruction O-6 (the descent cancellation).** Moving the AES system from GF(2) to GF(2^8)
> divides the variable count by the extension degree 8 and multiplies it back by the same
> factor 8 the moment quadraticity is restored, because the affine layer `L` is GF(2)-linear
> and its GF(2^8) description is its Frobenius orbit. The cancellation is exact and is a
> property of the extension degree, not of AES's constants. **There is no smaller system.**
> The choice is between ~1408 variables at degree 2 and ~200-400 variables at degree 128, and
> `C(N,d)` is monotone the wrong way in that trade.

Corollary, and it matters for how one reads the "39 equations per S-box" figure: the apparent
**over-determinedness of the GF(2) system (M/N ~ 5.5) is descent of a system that is
essentially *determined* over GF(2^8)** (one quadratic per S-box per conjugate). The extra
GF(2) equations are GF(2)-linear consequences of the same GF(2^8) content plus the field
equations. That is why "M/N ~ 5.5, so d_reg should collapse" does not follow: the equation
supply is inflated but the information content is not. **This is the precise form of the trap
XSL fell into**, and it is stated here as a mechanism rather than as a recollection: XSL's
error (recall MEDIUM, UNVERIFIED-FROM-MEMORY, and not used to dismiss anything) was to
*count* generated equations rather than to *rank* them. Any algebraic candidate under this
question must therefore rank, never count — which is exactly what CAND-FR2-A is built to do.

### 3.5 Sparsity and block structure — named, and each fails for a different reason

- **Sparsity** reduces the linear-algebra constant, not `d_reg`. Sparse elimination
  (Wiedemann-type) moves `omega` from 2.37 toward 2 at a cost linear in the row weight. In
  D-1's table that shifts the requirement from `d_reg <= 6` to `d_reg <= 7`. **One unit of
  d_reg, not a lane.**
- **Block structure** would reduce cost only if it induced a small *separator* of the
  equation hypergraph, because a separator-parameterized dynamic program costs 2^{width}.
  The first pass argued width ~256 via the natural round path decomposition. The obvious
  candidate for a smaller separator is the **super-box** structure, and it fails for a
  nameable reason:

> **Obstruction O-7 (the super-box separator).** Two AES rounds decompose into four parallel
> 32-bit super-boxes. Between consecutive super-box layers, ShiftRows sends **one byte from
> each super-box to each of the four next-layer super-boxes**: the layer-to-layer dependency
> graph is complete bipartite `K_{4,4}` with 8-bit edges, so any cut between super-box layers
> costs 4 x 4 x 8 = **128 bits**, exactly the state size, and any "vertical" cut separating
> two super-box columns across all five layers costs strictly more. **The super-box
> decomposition — the natural candidate for a sub-state separator — does not produce one.**
> This is an argument, not a theorem; the rigorous treewidth lower bound remains the open item
> the first pass named, and is unproved here too.

Note the unification, which is the second structural contribution of this pass: **D-3's
matching-width obstruction, O-7's separator obstruction, and the block-structure route into
d_reg are the same question** — does the AES dependency structure admit a separator materially
below the state size? Three apparently independent lanes (biclique factorization, treewidth
dynamic programming, block-structured Gröbner) rest on one quantity.

---

## 4. Gap 3 — statistical attacks with no key enumeration in the distinguishing phase

Searched; no admissible candidate produced; the closure is stated at the
`docs/inventor-protocol.md` section 4 standard rather than as a fatigue report.

**Named obstruction, in three parts.**
1. **O-1 (given).** The wide-trail bound governs *characteristics*, and an 8-round
   characteristic sits at <= 2^-300 differentially / <= 2^-150 linearly. A depth-8
   distinguisher via a single trail is out of reach by >150 bits.
2. **O-8 (derived here — the single-ciphertext determinism requirement, generalized).** The
   first pass's O-4 said an *offline key-difference sieve* needs q ~ 1 rather than q above
   random, because with one target ciphertext there is no data axis over which to aggregate a
   bias. **That argument does not depend on the object being a key difference.** It applies to
   *every* statistical functional of the key-indexed map used as a filter: with `t` known
   plaintext/ciphertext pairs (the definitional reference needs 2), a filter of bias
   `epsilon` yields `O(t epsilon^2)` bits of key information, so a filter usable inside a
   2^128 budget needs `epsilon` within `2^-40` of deterministic, or needs a data axis whose
   cost is then charged. **O-8 therefore closes the entire *statistical* wing of the fourth
   object class defined in section 6, not merely its first-order member.**
3. **Envelope foreclosure.** `DEC-20260731-019` ruling 10 removes MILP and SAT, which is the
   entire modern automated search methodology for differential, linear and division-property
   distinguishers. This program cannot *search* for a depth-8 distinguisher even in principle
   at this envelope. That is an infrastructure fact, never negative mathematical evidence
   (`AGENTS.md` rule 5).

**Forward guidance — what remains open, named concretely.** The only crack in O-1 is the
characteristic-versus-hull gap, and there is a specific, measurable, *unmeasured* sub-question
inside it that nobody in this program has touched: **the conversion from a characteristic
bound to a differential bound rests on the Markov-cipher idealization of independent round
keys, and AES's round keys are not independent** — they are a deterministic bijective function
of a 128-bit master key, which is 128 bits of entropy spread across 1408 bits of round key.
The measurable question is whether the *real-key-schedule* differential probability at
r = 2,3,4 deviates systematically upward from the *independent-round-keys* value at the same
r, and whether the deviation grows or decays with r. That is a validation-ladder step-1
measurement (`docs/inventor-protocol.md` section 6), it is cheap, its null is literally the
Markov model, and its round-count decay check is built in. It is **not proposed as a candidate
here** because a reduced-round reading cannot speak to depth 10 and this pass declines to
propose an instrument whose only honest output would be cross-filed under `RQ-AES-001`. It is
recorded as open direction (ii-sharpened).

---

## 5. Gap 4 — the fixed round constants and the specific MDS matrix

Searched. The specific constants enter the cipher's structure through exactly **three**
functionals, and each deduplicates to a family already declared off-limits as a primary lens.
Recorded as a closure with mechanism, not as a candidate.

**Derivation D-6 (the three functionals).**

1. **The Rcon orbit's escape from every SB/SR/MC-invariant subspace.** The all-16-bytes-equal
   state subspace (256 states) is invariant under SubBytes (bytewise), under ShiftRows (row
   shifts fix an all-equal state) and under MixColumns (`02 + 03 + 01 + 01 = 01`, so MC is the
   identity on constant columns — the fact recorded in `KN-FIND-018` practice rule 4). The
   only round operation that can leave it is AddRoundKey. If a key produced an all-equal
   expanded key, the subspace would be invariant under the whole cipher. It cannot:
   `K` all-equal to `a` gives `W[3] = (a,a,a,a)`, `SubWord(RotWord(W[3])) = (S(a),...,S(a))`,
   and XORing `Rcon_1 = 01` in the first byte only yields `(S(a) + 01, S(a), S(a), S(a))`,
   which is **not** constant. **Rcon breaks the invariance in the first key-schedule step, by
   construction, for every key.** Verifiable locally in seconds. Family: invariant subspace —
   off-limits, and already recorded dead in <= 1 round in the first pass's dedup table.
2. **The unipotent flag of MixColumns.** `KN-FIND-017` establishes `ord(M) = 4` via the
   circulant isomorphism `F[y]/(y^4+1) = F[z]/(z^4)`, `c = 1 + n` with `n = 02z + z^3`
   nilpotent. **Corollary derived here:** `M` is therefore *unipotent* (`M - I` nilpotent),
   so it preserves the complete flag `(z^3) subset (z^2) subset (z) subset R` of
   GF(2^8)-dimensions 1, 2, 3 inside each column. Since `z = y + 1`, the 1-dimensional piece
   `(z^3) = span{(y+1)^3} = span{y^3 + y^2 + y + 1}` is exactly the **constant-column
   subspace** — which is why `KN-FIND-017` Corollary 2.2 found the constant vectors to be the
   exception where `L` preserves collinearity. The flag is a genuine structural fact about
   the *specific* AES matrix and not about a generic MDS matrix. It is destroyed by ShiftRows
   (which mixes columns) and by the GF(2)-affine layer. Family: subspace trail / invariant
   subspace — off-limits.
3. **Branch number 5.** Feeds O-1 and D-3 directly. Family: wide trail — off-limits.

**Forward guidance.** What is *not* closed: (a) the **joint** functional of the Rcon sequence
and the MC flag across the key schedule — the AES-128 key schedule has no MixColumns, so the
flag and the constants never meet, and whether that separation is exploitable in AES-192/256
(whose schedules are longer and whose constant supply is sparser) was not examined here;
(b) **`ord(MC o ShiftRows)` as a GF(2)-linear map on the 128-bit state has never been computed
in this program**, is a seconds-long pure-Python computation, and a small order would be a
striking structural fact worth knowing before anyone reasons about the linear layer again.
Both are named OPEN AND UNATTEMPTED, never tried or screened.

---

## 6. Gap 5 — the fourth object class

The first pass found objects of the cipher (class A), of the enumeration (class B) and of the
ideal (class C), and recorded "I found no fourth class" as a statement about its search. There
is a fourth class, and it is the natural home of everything in section 2.

> **Class D — objects of the KEY-INDEXED FUNCTION.**
> Fix a plaintext `P`. Let `f_P : {0,1}^kappa -> {0,1}^128`, `f_P(K) = E_K(P)`. The attacker
> has **full, free, offline evaluation access to `f_P` at every point of its domain**; the
> attack problem is to invert `f_P` at the single point `C`. A class-D tracked object is a
> **structure functional of `f_P`** — a lossy summary of the whole map in the key variable,
> with no propagation-through-rounds semantics required.

**Why this is a class and not class A relabelled.** Class A tracks the propagation of an
object through the rounds of the *state*, with the key fixed. Class D fixes the *plaintext*
and takes a global functional of the map in the *key*. Class B tracks the enumeration order;
class D tracks the function being enumerated over. Class C tracks the ideal in state-and-key
variables jointly; class D's members live after state elimination. The reframing that makes
the class useful is the observation in section 2: **full-round AES key recovery is the
inversion, at one point, of a specific, fully known, efficiently evaluable function** — and the
complete list of known ways to invert such a function sub-exhaustively *is* a list of class-D
structure functionals.

**Members, each with its lossy-projection verdict and its status.**

| # | Structure functional (the tracked object) | Lossy-projection test | Status in this program |
|---|---|---|---|
| D1 | **Decomposition width** — the minimum m such that `[f_P(K)=C]` factors as an m-bit match between `(K_1,P)`-forward and `(K_2,C)`-backward parts | PASSES (discards the functional form, retains only the split boundary) | **Closed by D-3** for exact splits; the almost-independent relaxation is CAND-FR2-B |
| D2 | **Linear-structure set** — `{delta : ⟨beta, f_P(K+delta)⟩ + ⟨beta, f_P(K)⟩ constant in K}` | PASSES | **Measured dead at r=4** (GATE 2, floor 2^-7.18 relative, N=2^19) |
| D3 | **Influence / junta support** — `I(b,k) = Pr_K[flipping key bit k changes intermediate bit b]`, and its exact-zero set | PASSES (discards magnitudes and functional form, retains support) | **UN-MINED — CAND-FR2-B** |
| D4 | **Algebraic degree in K** — least d with a nonvanishing d-th order derivative over a key coset | PASSES | **Out of envelope, derived below** |
| D5 | **Fourier concentration** — the tau-heavy Walsh support of `K -> (-1)^{⟨beta, f_P(K)⟩}` | PASSES (discards all coefficients below tau and all magnitudes; propagates conservatively — linear maps permute the support exactly, nonlinear layers contain it in a convolution of supports, so a measured concentration is a lower bound: the safe direction) | **Closed a priori by O-8** as an attack route; residual value only as a descriptive statistic |

**Honest scoring on the three axes required by `docs/inventor-protocol.md` section 1.**
*Genuinely new or repackaging:* the **lens** is new to this program's map and it does real work
(it is what lets sections 2 and 3 be one question rather than two); but **three of its five
members are repackagings** — D1 is the biclique family, D2 is CAND-FR-2, D5 collapses into the
statistical wing that O-8 closes. Only **D3 is both un-mined and un-closed**. *Concretely
testable:* D3's one-step propagation is exactly definable and cheaply measurable; D4's is
definable but not measurable here; D5's is definable and measurable only at toy key sizes.
*Survival depth:* D1 dies at round 2 (D-3); D2 measured dead at round 4; D3 is **defined and
measurable at the full round count** and is predicted to reach the null at round 2-3; D4 is
defined at full depth and unmeasurable past round 1; D5 predicted null by round 4.

**Derivation D-7 (why D4 is out of envelope, declared rather than estimated).** Measuring the
algebraic degree of `f_P` in `K` requires summing `E_K(P)` over an affine key subspace of
dimension `d`, costing `2^d` AES evaluations. The measured machine reach is **2^38.8 AES
evaluations per 1600 s task and 2^42.6 for the whole campaign**. The degree of `f_P` in `K` is
about 7 per byte after round 1 and saturates near the GF(2) bound of 127 by round 3. So from
round 2 onward the required `d` exceeds the instrument's ceiling by 80-90 bits. **The
instrument can confirm "degree >= 39 at r >= 2", which is uninformative.** Declared OUT OF
ENVELOPE per the directive, not estimated into a result.

---

## 7. The verdict the directive asks for

**Does any class escape both O-3 and the depth wall?**

| Class | Escapes O-3 (the amortization ceiling)? | Escapes the depth wall? | Blocked by |
|---|---|---|---|
| A — data-path statistical | Yes (no enumeration) | **No** — dies at 4-6 of 10-14 | O-1 + O-8 + envelope |
| B — enumeration / recomputation | **No** — inside it by construction (D-4) | Yes (defined on the whole graph) | O-3, and cannot even approach its own ceiling (D-3) |
| C — algebraic / solving | **Yes** — never enumerates | **Yes** — the system does not decay with rounds, it grows | `d_reg`, i.e. **O-5', not O-5** |
| D — key-indexed function | Yes, in the same way C does (it feeds a non-enumerative inversion) | D3 yes, D1/D2/D5 no | O-8 for the statistical wing; D3 predicted at the null by round 3 |

> **YES — exactly one class escapes both walls, and it is class C.** It has always been the
> only one that does. The first pass's own trichotomy said so ("the only class whose object
> survives to round 10 with no loss whatsoever"), and then bounded it with a figure — 2^704 —
> that applies to a different solver family. **The second pass's finding is that the wall
> stopping class C was mis-identified, and that the correct wall sits at 2^246-2^379 rather
> than 2^704, requiring `d_reg <= 6-7` against a semi-regular crossover proxy of ~16-22.**
>
> This is not encouragement. A factor-2.3-to-3.5 drop in `d_reg` below the semi-regular value,
> sustained at N = 1408, is an enormous structural demand; this program's own only prior
> structured-versus-random `d_reg` measurement (`research/dreg-linear-law/FINDING_v2.md`,
> item 5) found the **structured** system's degree of regularity *higher* than the random
> null's — the wrong direction for an attacker. The honest expectation is that AES behaves the
> same way. But that expectation is now a **measurable, pre-registered prediction with a
> matched null**, instead of a 2^704 that was never the right number.

---

## 8. Obstruction register after this pass

| id | status | statement |
|---|---|---|
| O-1 | unchanged, recalled | wide trail; bounds characteristics, not hulls |
| O-2 | unchanged, recalled | extension budget e <= 2-3 |
| O-3 | **narrowed and strengthened** | premise (P-b) is not a law; it fails when the candidate test factors. For full-round AES it is **forced by D-3**, a stronger obstruction than O-3's own counting argument |
| O-4 | measured | GATE 2: object at the null from r = 4, at floor 2^-7.18 relative |
| O-5 | **SUPERSEDED by O-5'** | 2^704 bounds solvers with exponent linear in N; it does not bound the Gröbner/XL family |
| O-5' | derived here | Gröbner/XL on AES-128 costs ~2^246-2^379 at the semi-regular crossover; needs `d_reg <= 6-7` to reach 2^128; memory 2^57 sparse / 2^106 dense |
| O-6 | derived here | the GF(2)-to-GF(2^8) descent cancellation is exact; there is no smaller system |
| O-7 | derived here (argument) | the super-box decomposition gives no sub-128-bit separator; layer-to-layer connectivity is `K_{4,4}` with 8-bit edges |
| O-8 | derived here | the single-ciphertext determinism requirement generalizes from key differences to **every** statistical class-D functional; closes class D's statistical wing |
| D-3 | derived here | no exact MITM factorization of the full-round candidate test exists for any nontrivial key partition |
| LP-1, LP-2 | unchanged | `sigma(K)` determines K; a key mask does not shorten the data path |

Every one of O-5', O-6, O-7, O-8 and D-3 is an **argument derived in text, at the `derivation`
tier**: not machine-checked, not measured, not reviewed. `novelty_status: unverified` for all
of them — literature is not checkable here, and the honest expectation is that all are well
known to specialists.

---

## 9. Honest accounting — `docs/inventor-protocol.md` section 5

- **Objects considered (7):** the graded ideal / degree-of-regularity object (CAND-FR2-A); the
  key-influence support object D3 (CAND-FR2-B); the decomposition-width object D1 (closed by
  D-3); the algebraic-degree-in-K object D4 (out of envelope by D-7); the Fourier-concentration
  object D5 (closed by O-8); the super-box separator object (closed by O-7); the
  constants-and-MDS functionals (closed by D-6, all three deduplicating).
- **Admissible candidates:** 2. Padding was available and declined.
- **`dominated_by`:** `unresolvable in this environment: no primary source reachable; every
  recalled frontier row is unverified-from-memory` — the exact string `RQ-AES-002` R5 mandates,
  and never `null`. Against the one reference that *is* adjudicable here: both candidates are
  dominated on **time** by the definitional exhaustive-key-search reference (2^128 for
  AES-128), neither claims an attack, and neither is dominated on **data** (both need 1-2
  known pairs, the same as the reference). CAND-FR2-A's *lane* is dominated on **memory** by
  the reference by 57 to 106 bits.
- **`sota_delta`:** **0 bits** predicted for both candidates against the DEFINITIONAL
  exhaustive-key-search reference under a cost model that is not yet frozen as CM-1; the
  published-frontier comparison is **unadjudicable** and is asserted in neither direction. The
  quantitative content of this session is not a delta but a **correction to a ceiling**:
  O-5's 2^704 is replaced by O-5''s 2^246-2^379, a correction of 325-460 bits, leaving the
  algebraic lane 118-251 bits short of 2^128 rather than 576 bits short.
- **Closures enumerated:** O-5' (supersession, with mechanism), O-6, O-7, O-8, D-3, D-6, D-7 —
  each with a named obstruction, an argument, and forward guidance. The section 4 standard is
  met by O-6, O-8, D-3 and D-7 (obstruction + argument + what remains open). O-5' and O-7 are
  **arguments, not theorems**, and are labelled as such: O-5' rests on a cost model for a
  solver family and on a semi-regular *proxy*, and O-7 lacks a rigorous treewidth lower bound.
- **What is NOT claimed.** No claim about AES security at any round count, in any threat
  model. No distinguisher, no key recovery, no speedup, no measured structural excess, no
  barrier statement about AES, no impossibility claim, no novelty claim, and no relation of
  any kind — better, worse, or equal — to the published state of the art.
- **Open directions for the next session:**
  1. **Rank, never count.** Run CAND-FR2-A's gate 1 (free): the exact semi-regular `d_reg` at
     the derived AES-shaped `(N, M)`, using the in-repo instrument
     `research/dreg-linear-law/dreg_growth_law.py`, whose recurrence is the same
     divide-by-`(1+z^d)` Hilbert-series construction and which that work validated against a
     support-matched random null at every degree below `d_reg`.
  2. Derive `M` locally as the corank of the 137 x 256 S-box evaluation matrix, removing the
     recalled "39 per S-box" from the load-bearing path.
  3. Compute `ord(MC o ShiftRows)` on the 128-bit state. Seconds. Never done here.
  4. The Markov-idealization crack in O-1: real key schedule versus independent round keys, at
     r = 2,3,4, with the deviation's sign and trend. Cross-files under `RQ-AES-001`.
  5. A rigorous treewidth/separator lower bound for the AES equation hypergraph — still
     unproved, now with O-7 narrowing the space of candidate decompositions.
  6. The joint (Rcon sequence, MC unipotent flag) functional in the AES-192/256 key schedules.
     OPEN AND UNATTEMPTED.
- **Premature-closure self-check.** This session did not decline to search on saturation
  grounds; it searched five named gaps, produced two candidates, and superseded an obstruction.
  Its own negative conclusions are scoped to named mechanisms. The statement "class C is the
  only class escaping both walls" is a statement about **the four classes this program has
  enumerated**, not about AES, and a fifth class remains as available now as the fourth did
  before section 6.
