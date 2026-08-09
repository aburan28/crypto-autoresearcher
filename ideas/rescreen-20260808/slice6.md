# Adversarial re-screen — slice 6 (18 records)

Reviewer: Red Team. Repo read-only at `/tmp/wt-ideas-100` (main). Web search
unavailable — **all external novelty is UNADJUDICATED**; every verdict below is
an internal-corpus verdict plus direct computation.

## Verdict table

| ID | verdict | one-line reason |
|---|---|---|
| IDEA-20260808-83b3ba | **REFUTED** | "a random invertible GF(2^8) 4x4 typically gives branch 4" — measured: **76.7% are MDS (branch 5)**, 23.2% branch 4, 0.06% branch 3, branch 2 never. The branch-3-4 arm is not constructible as stated; also overlaps same-day `bfee7e`. |
| IDEA-20260808-031a59 | **SCOPE-INFLATED** | The closure is *not* "unconditional in transport cost": its second horn is a solver-degree claim, and the pullback of a window is a degree-`deg φ` algebraic condition, not "an arbitrary set". |
| IDEA-20260808-b3c97b | **REFUTED** | The D2 detector scores **0.1148** on the four actual placeholders — *below* the genuine-digest mean 0.1237 — not 1.0. Zero power on its own motivating artifact. D1 (length) is what catches them. |
| IDEA-20260808-0bde1a | NOVEL (controls required) | `R = n·sqrt(m+2)` is correct arithmetic, but "node count grows ≥4× per unit D" and "terminates at D=40 in 10^3 s" are mutually inconsistent (4^40 = 2^80). Must report `R/λ1` and the Gaussian-heuristic count. |
| IDEA-20260808-ba4e37 | **PARTIAL-OVERLAP** | Point-side closure duplicates its own cited 0807-30868b/464ff8 **and** same-day `40aab9`; class side wholly conditional on an unread KN-LIT-7489; **missing KN-TECH-057** (states vOW p^{1/4} unconditionally). |
| IDEA-20260808-4d77a6 | **PARTIAL-OVERLAP + refuted heuristic** | Identity (A) **verified exactly, 20/20 traces over F_307**. HA-1 is false: conditional on `ℓ\|f`, `A−1 mod ℓ` occupies exactly `ℓ−1` of `ℓ` residues and `P(ℓ\|A−1)` ≈ `1/(ℓ−1)`, not `1/ℓ` (0.481 vs 0.333 at ℓ=3, 6.3σ). Same-day `ceca08` states the same identity. |
| IDEA-20260808-d830c6 | **PARTIAL-OVERLAP** | Its screen claims "no KN-FIND records the r-factor or KN-OPEN-006's economics". **KN-FIND-002** (visible, line 3 of KNOWLEDGE_BARRIERS.txt) already records the linear-algebra half of exactly the boundary this record says is missing. |
| IDEA-20260808-b1358c | NOVEL (cost-model objection) | Galois facts all check out (3 involutions; σ_{n−1}=cτ: ζ→−ζ^{-1}; fixed field of ⟨c,τ⟩ has degree n/4). But `sota_delta` mixes two cost models: 0.292·257 = 75 bits vs the relayed 2^108. |
| IDEA-20260808-ae175e | **PARTIAL-OVERLAP** | Kronecker derivation is correct as written, but same-day `f104a2` uses the same emulsifier-Kronecker structure; and HA-1's Schwartz–Zippel model does not describe θ (a root of a *fixed* spec polynomial, not a uniform element of K). |
| IDEA-20260808-b9a74c | **REFUTED** | Claim (A) needs `def` to vary **per coordinate**; claim (B) asserts the vanishing depth is "an explicit function of (m,t,n)" — i.e. coordinate-independent. Internal contradiction: the def-refined signature separates nothing by its own claim (B). Also dominated by same-day `3d3be9`. |
| IDEA-20260808-4f83f6 | **REFUTED** | The identity `w − c·s2 = A·z − c·t` is exact, but ML-DSA's public key is `(ρ, t1)`, **not `t`**. R2 is `(pk, t0)`-computable — the same class as R3. The advertised "clean PUBLIC/SECRET split" collapses. |
| IDEA-20260808-721f2b | NOVEL (units objection) | DP and null controls are sound, but the "published bound" is a bound on forging *advantage* and the DP returns an expected *query count*; the ratio is not a tightness factor until the conversion is pinned. |
| IDEA-20260808-f4edc6 | **REFUTED** (acceptance criterion) | "Measured mean differs from `C(B+m-1,m)/N` by more than floating-point error ⇒ harness bug" is unmeetable. Sample-mean sd is `sqrt(mu/T)` = 1.2%–9.6% of mu at the record's own cells; simulated gap 0.159%. Fires on a correct harness with probability ≈1. |
| IDEA-20260808-71c077 | **NOVEL** | Every arithmetic claim re-verified and correct (see below). One objection: its *own* consistency check (1.703 vs 1.704) is evidence the third exponent is derived from the other two, weakening the "three constraints on two unknowns" framing. Cites KN-TECH-057. |
| IDEA-20260808-ae34ad | **REFUTED** (arm 1) | `IDEA-20260805-88ecef` charges `M = q·k` **cells** of "one a-bit index", explicitly a lower bound, with charge `M^θ`. The "64-bit cell" this record attacks appears nowhere in it; a 14.4-bit Bloom filter is *larger* than an a-bit index (a = 6 at 128f). |
| IDEA-20260808-3da739 | **REFUTED** (firing rule) | The audit fires iff a published point's provenance has a secret-dependent kernel — SQIsign's own response isogeny satisfies that **and** is publicly computable after publication, so the audit false-positives on the honest protocol. **Missing KN-TECH-057.** |
| IDEA-20260808-f313da | **REFUTED** (prediction 3) | Measured `corr(gain, log N1/log p^{1/3})` = **+0.727 / +0.727 / +0.619 / +0.509** at u=2/3/4/5. Never negative. The record's own falsification condition fires at every tested parameter. Headline (gain ≪ 3) survives. |
| IDEA-20260808-621df3 | NOVEL (filing defect) | `rho_f(B) = 2⌊√B⌋` when `4B < \|D_f\|` is correct. But: **no `goal_id`** and 11 fields present in every sibling record are absent. |

---

## Non-NOVEL verdicts, with the specific claim and the specific counter

### IDEA-20260808-83b3ba — REFUTED

The `mechanism` field states: *"identity gives 2, a random invertible GF(2^8)
4x4 matrix typically gives 4, a Cauchy or Vandermonde MDS matrix gives 5."*
That is the entire construction of the pre-registered four-point knob.

I computed the branch-number distribution over 20,000 uniformly random
**invertible** 4×4 matrices over GF(2^8) (AES modulus 0x11B; note 2 is *not*
primitive there — order 51 — so the log table must be built on 3, which is
where a naive implementation silently breaks). Branch number computed exactly
from the minor characterisation, sanity-gated on `branch(MixColumns)=5` and
`branch(I)=2`:

```
B = 3 :     13   frac 0.0006
B = 4 :   4642   frac 0.2321
B = 5 :  15345   frac 0.7672
(singular draws rejected: 85)
```

A random invertible matrix is **MDS with probability 0.767** — the same branch
number as the "random MDS" arm. Branch 3 needs rejection sampling at rate
6×10^-4; branch 2 requires a column of Hamming weight 1 and effectively never
occurs. So of the four design points, two coincide, one is unreachable by the
stated recipe, and the fourth (identity) is not a member of the family at all.
The record's confounder ("must be measured per draw, not assumed") does not
repair this: it converts the recipe into a 77%-rejection loop with no procedure
at all for branch 3.

Second, independent objection — the **ordering is probably inverted**. With
`L = I` the round function has no inter-byte diffusion whatsoever; the cipher
degenerates to byte-local S-box chains permuted by ShiftRows. The campaign's
own scale (per `bfee7e`: AES 59 against a null of 4.0; ideal permutation 14
against 1) makes *higher hits = more structure*. Predicting that the
branch-2 identity arm lands "near the ideal-permutation reading" of 14 predicts
that the *least* diffusive cipher looks *most* ideal. The pre-registered
decision table has no branch for "strictly decreasing", which is the outcome I
expect.

Third, overlap: **IDEA-20260808-bfee7e** (same `goal_id: GOAL-AES-003`, same
`question_id: RQ-AES-003`, same day) derives a **closed-form** geometric null
for the r=5 excess from ShiftRows/MixColumns coset geometry "with zero cipher
evaluations", and its pre-registered dichotomy ("the excess is a geometric
artifact of the probe on ANY MDS-layer SPN and the claimed distinguisher is
withdrawn") is 83b3ba's own conclusion reached at zero compute. 83b3ba's
`dominated_by` checked "RC-A, RC-B, RC-C, RC-D and both BATCH-015 candidates" —
in-campaign arms only. This is a real Pareto gap on the compute axis.

Suggested `discriminated_from` text if the record is kept: *"IDEA-20260808-bfee7e
derives the geometric null in closed form at zero cipher evaluations and reaches
the same three-way verdict; this record supplies the empirical ordering that
would corroborate or contradict that derivation, and must be run after it, not
instead of it. The linear-layer arms must be CONSTRUCTED at target branch number
(a random invertible draw is MDS 77% of the time, measured), not sampled."*

### IDEA-20260808-031a59 — SCOPE-INFLATED

Claim: *"The closure is unconditional in transport cost, which is strictly
stronger than the corpus's current position."*

The argument is a dichotomy. Horn 1 (keep sums within a curve → `h·B^m` typed
decompositions instead of `(hB)^m`) is arithmetically right; the penalty is
`h^{m-1}`. Horn 2 is where the "unconditional" claim actually lives:
*"once transported they are just sums on E again, at which point the factor base
is the union of h pullbacks and is no longer describable (the pullback of a
window is an arbitrary set, so the solver cost reverts to exhaustive)."*

The pullback `φ_i^{-1}(V_i)` is **not an arbitrary set**. It is cut out by
`x(φ_i(P)) ∈ window`, where `x∘φ_i` is a rational map of degree `deg φ_i`. That
is a describable algebraic condition; what it costs is a `deg φ_i`-fold increase
in the degree fed to the summation-polynomial solver. So horn 2 is a
*transport-degree* claim, and the closure is conditional on transport degree
after all — precisely the thing the record advertises it does not need. The
conclusion may well be right; the stated unconditionality is not established.

Two smaller items. (i) `prediction 2` ("the matrix is block-diagonal by curve
… so the aggregated system is h independent systems") is true only in horn 1;
under free transport, relations mix pullback points and block-diagonality fails
— it is asserted unconditionally. (ii) The `mechanism` attributes the penalty to
**KN-FIND-007 consequence 4**, which I read in full: that consequence is about
partitioning *one* base, `B1+B2+B3 = B`, with penalty `m^m/m! ≈ 4.817` at m=3,
independent of h. The penalty here is `h^{m-1}`. Right arithmetic, wrong
citation for the mechanism.

### IDEA-20260808-b3c97b — REFUTED (CLAIM A / D2)

The record's motivating facts check out exactly: `ledger/evidence/EV-ECDLP-65b004.yaml`
carries four `hash: sha256:…` values of **62 hex characters** each (SHA-256 is
64), and the record's own integrity note says so.

Its CLAIM A then says: *"(D2) a nibble-transition statistic — the fraction of the
63 adjacent-nibble transitions obeying the best affine successor rule x -> x + c
mod 16. For a genuine digest that fraction has mean 1/16 and standard deviation
about 0.030; the observed filler scores 1.0. A threshold at 0.5 therefore has a
false-positive rate on genuine digests far below any rate this corpus could
exhibit."*

Applying D2 exactly as specified to the four actual placeholders:

```
D2 on the four placeholders: ['0.1148', '0.1148', '0.1148', '0.1148']
D2 on 200000 genuine SHA-256 digests: mean 0.1237  sd 0.0194  min 0.0794  max 0.2698
  fraction above the record's threshold 0.5: 0.0
```

**The placeholders score 0.1148 — below the genuine-digest mean of 0.1237.**
D2 has *zero* power against the exact artifact it was designed for; it would
never fire. The filler is not a single additive successor rule: its high nibbles
cycle `a,b,c,d,e,f` (period 6) and its low nibbles cycle `1..9,0` (period 10),
period 30 bytes. At nibble lag 2 the best additive rule matches 0.867 — but that
is not the statistic the record defines. Relatedly, the `claim` describes the
filler as "cyclic rotations of the same `0123456789abcdef` filler"; they are
rotations *of each other*, but the base string is not that.

Two secondary points. The claim's "mean 1/16 and sd about 0.030" is the law of a
*single fixed* rule, not the best-of-16 maximum the record actually specifies
(measured 0.1237 / 0.0194); `HA-14` does disclose the correction, so `claim` and
`heuristic_assumptions` disagree with each other. And the record's own prediction
bullet ("genuine digests concentrate near 0.06-0.20") is **correct** — 99.81% of
200,000 genuine digests fall inside — which only sharpens the problem, because
the placeholders fall inside that same band.

What survives: D1 (length + alphabet) does catch these, cheaply and completely.
CLAIM B (per-role sensitivity `s_R, s_V, s_T` and the escape-correlation `ρ`) is
untouched by this and is the more valuable half. D2 must be withdrawn or
respecified (a period-detector / repeat-structure test, not an affine successor
rule) before dispatch, and the "complete separation" sentence deleted.

### IDEA-20260808-ba4e37 — PARTIAL-OVERLAP

Part (B)'s point-DDH closure (alternation kills a pairing on cyclic G; the
Tate–Lichtenbaum route needs `F_{p^{k_emb}}`; usable over `F_p` iff `k_emb = 1`
iff `N | p−1`; and `(N,p)` are public so there is nothing to hide) is
mathematically fine, and the record honestly scopes it with HA-2 to
"pairing-shaped" distinguishers. But it is the same closure as its own cited
`IDEA-20260807-30868b` / `-464ff8`, **and** same-day `IDEA-20260808-40aab9`
reaches the identical degenerate cell (`N | p−1`, MOV-degenerate, "CM cannot
supply the missing second point because every endomorphism acts on G as a
scalar") by the Kani/Robert route. Three records now close the same cell.

Parts (C)/(D) rest entirely on KN-LIT-7489, which the record states it did not
read. `honest_prior_of_survival` 0.6 for the transfer is appropriate; the record
is literature-blocked and should be held, not dispatched.

**KN-TECH-057 gap.** `best_known_baseline` reads *"For class-action DDH: sqrt(h)
= p^{1/4} generic"* and `memory_exponent` *"p^{1/4}-with-memory-w for the generic
class-action baseline via van Oorschot-Wiener on the action"*. KN-TECH-057
records the `F_p` vOW `p^{1/4}` row as **conditional on unproven `F_p` subgraph
mixing**, with Delfs–Galbraith at full cost `p^{1/3}` as the fallback matched
baseline. The record states the conditional row as unconditional.

Suggested `discriminated_from` addition: *"IDEA-20260808-40aab9 closes the same
k_emb = 1 / N | p−1 cell for prime-field ordinary curves by the Kani/Robert
route; this record reaches it by pairing alternation and adds only the
point/class separation. The class-action baseline is KN-TECH-057's F_p vOW row,
which is conditional on unproven F_p subgraph mixing; DG at p^{1/3} is the
unconditional fallback."*

### IDEA-20260808-4d77a6 — PARTIAL-OVERLAP + refuted heuristic

**Part (A) is correct.** I re-derived it (`π = A + mθ` with `A = (t − f·D_0)/2`;
`(π−1)O` has basis rows `(A−1, m)` and `(mv, (A−1)+mu)`; the first Smith
invariant is `gcd(A−1, m)`) and then tested it directly: over `F_307`, all
`p²` curves enumerated and grouped by trace, and for each trace with `f > 1` I
compared the *set* of measured `n_1` values against
`{gcd(A−1, f/f_E) : f_E | f}` (Deuring–Waterhouse says every `f_E | f` occurs).
**20 traces, 20/20 exact set match**, including `t = −16, f = 18` where both
predicted and observed sets are `{1, 2, 3, 6, 9, 18}`. Note a trap: a naive
random-point exponent estimate produces spurious `n_1 = 4` values at `p = 307`
(impossible, since `n_1 | p−1 = 306`); the identity survives once the exponent is
computed robustly.

**HA-1 is falsified.** It states *"the residue A − 1 mod ell is equidistributed
in Z/ell independently of the event ell | f"*, giving a non-vacuity density
"about 1/ell per ell | f". Over 4,000 random ordinary `(p,t)` at `p ∈ [2^20, 2^21]`:

```
 ell | #samples with ell|f | P(ell | A-1 GIVEN ell|f) | HA-1 predicts 1/ell
   3 |          403        |          0.4814         |        0.3333
   5 |          169        |          0.2899         |        0.2000
   7 |           78        |          0.1795         |        0.1429
  11 |           44        |          0.1364         |        0.0909
Support of (A-1) mod ell CONDITIONAL on ell|f:
  ell= 3 : 2 distinct residues out of 3   {0,1}
  ell= 5 : 4 distinct residues out of 5   {0,1,2,3}
  ell= 7 : 6 distinct residues out of 7   {0..5}
  ell=11 : 10 distinct residues out of 11 {0..9}
```

Conditional on `ℓ|f` the residue `−1 mod ℓ` **never occurs**, and the law is
uniform on the other `ℓ−1`. The reason is forced by the record's own setup:
`ℓ|f ⇒ A ≡ t/2 (mod ℓ)` and `ℓ²|D ⇒ t² ≡ 4p (mod ℓ²)`, so `A−1 ≡ ±√p − 1` with
`√p ≠ 0`. So `P(ℓ | A−1 | ℓ|f) = 1/(ℓ−1)`, not `1/ℓ` — a 6.3σ deviation at ℓ=3.
The stated `rigorous_ingredient` (Deuring/Waterhouse weighting of traces) does
not support the independence assertion; it is contradicted by the very
congruence that defines the conditioning event. The record's own falsification
test ("a measured rate that is flat in ell falsifies HA-1") will not catch this,
because `1/(ℓ−1)` is also decreasing. Direction of the error is *favourable* to
the instrument, which is why it needs saying.

**Overlap.** `IDEA-20260808-ceca08` (same day, GOAL-ECTD-001) states the same
identity verbatim — *"n_1 = gcd(A-1, f/f_E) leaks the volcano level through the
public group structure"* — and credits it to internal slice record "E3-01", a
working-file name with no committed IDEA id. Neither record cross-references the
other. More materially, ceca08 supplies the **unconditional** bound `n_1² |
#E(F_p)` and `n_1 | p−1`, hence `n_1 | cofactor`: on any near-prime-order curve
the instrument returns 0 identically, and the leak is at most `log2(cofactor)`
bits. 4d77a6 frames non-vacuity as an open density measurement governed by HA-1
and never states the forced bound. That bound, not HA-1, is the scope statement
that matters.

Suggested `discriminated_from` text: *"IDEA-20260808-ceca08 states the same
identity and adds the unconditional bound n_1² | #E(F_p), hence n_1 | cofactor —
so the instrument is identically vacuous on any cryptographic (cofactor ≤ 8)
curve, independently of HA-1's density. This record supplies the derivation, the
cost comparison against the modular-polynomial route, and the toy non-vacuity
measurement; the crypto-scale scope statement is ceca08's."*

### IDEA-20260808-d830c6 — PARTIAL-OVERLAP

`novelty_screen`: *"Screened against KNOWLEDGE_BARRIERS.txt (no KN-FIND currently
records the r-factor or KN-OPEN-006's economics …)."*

**KN-FIND-002 is fully visible** in the dedup corpus (line 3 of
`KNOWLEDGE_BARRIERS.txt`), and its body already records the negative half of the
boundary this record says the corpus lacks:

> "This contextualizes H-STR-002: the block-circulant LA advantage (387x
> displacement rank reduction at B=397) is non-generic — phi is available to the
> generic model, and the structured LA advantage does not provide sub-birthday
> information."

That is a stronger statement than "KN-OPEN-006 is open in both directions", made
in a durable `confidence: strong` finding, about the same hypothesis (H-STR-002)
and the same object. The record's central argument — that recording the boundary
adds something the corpus needs — is materially weakened by a record it claims to
have screened. The `r = 3` arithmetic itself is right (`j = 0`, `p ≡ 1 mod 3` ⇒
`|Aut| = 6` ⇒ `r = |Aut|/2 = 3`), and the proposed null (a curve with `3 ∤ N−1`,
ratio must fall to 1) is a good control the campaign does not have.

Suggested `discriminated_from` text: *"KN-FIND-002 already records, at
confidence `strong`, that the block-circulant linear-algebra advantage is
non-generic and provides no sub-birthday information, naming H-STR-002. This
record adds only the collection-side constant r = |Aut|/2 and the replication
gate; the negative half of its proposed boundary is already durable."*

### IDEA-20260808-b1358c — NOVEL, with a cost-model objection

I verified the load-bearing algebra: `(Z/2^l)^*` has exactly three involutions
`{−1, 2^{l-1}+1, 2^{l-1}−1}` (each squares to 1 mod `2^l`); `σ_{n−1}: ζ ↦ ζ^{n−1}
= −ζ^{−1}` and `σ_{n−1} = c∘τ`; at `l = 3` the fixed field of `σ_3` is `Q(√−2)`
(`ζ_8 + ζ_8³ = i√2`) as claimed; the fixed field of `⟨c, τ⟩` is `Q(ζ_n)^+` of
degree `n/4`. The `lossy_projection_test` and the `nearby_object_control`
(cyclic `(Z/2p)^*` must return nothing) are correctly chosen, and the record
names its own most likely outcome (joint rank 0 or 1) and puts the rank check
first at zero cost. `dominated_by: null` for branch (B) is *qualified* against
KN-OPEN-028's four rows and the qualification is stated — that is the right
handling under AGENTS rule 5.

Objection: `target_complexity` and `sota_delta` mix two incompatible cost models.
`0.292·(n/2+1) = 0.292·257 = 75.0` bits, but the relayed incumbent figure is
`2^108` in the HAWK spec's gate-count model — a 33-bit gap of overhead at
dimension 257. The record itself says "the additive practical offset does not
shrink with dimension", so the honest projection at `n/4 = 128` is ≈ `2^{37+33}`,
not "`2^{0.292·128 + overhead}`" quoted next to `2^108`. Require the delta to be
stated in **one** model, with the offset carried, before any HAWK-512 sentence.

### IDEA-20260808-ae175e — PARTIAL-OVERLAP

I checked the derivation by hand and it is right: for `λ` a left eigenvector of
`E` with eigenvalue `θ`, `λᵀP*` has polar form `C(θ) ⊗ M_λ` with `C(θ)_{ij} =
θ^{c(i,j)}`, and `rank(A⊗B) = rank A · rank B`. The k=1 baseline embedding is
correct.

Overlap: same-day `IDEA-20260808-f104a2` (same goal, same question) builds on the
same structural fact — *"the degree-D Macaulay matrix of the whipped system is a
sum of k(k+1)/2 Kronecker-structured blocks"* — with a different observable
(Macaulay rank deficit vs `rank C(θ)`). Neither cites the other.

Mechanism objection (random-model transfer): HA-1 justifies full rank via
Schwartz–Zippel, *"a uniform theta avoids them with probability at least 1 −
k·max(c)/|K|"*. But `θ` is **not** uniform in `K`: it is one of the `m` conjugate
roots of the specification's fixed minimal polynomial. The event `det C(θ) = 0`
is the divisibility `f(X) | det C(X)` — a yes/no property of two fixed
polynomials, not a probability. With `|K| = 16^64`, the quoted bound is ≈`2^{-250}`
and carries no information; the actual computation (factor `g`, evaluate
`rank C(θ)` per root) is the whole content and does not need HA-1 at all. Also,
the record's own "degenerate extreme" (additive `c(i,j) = a_i + a_j` ⇒ rank 1) is
a priori excluded, since a rank-1 whipped form could not hit a uniform signing
target — the record says as much in `prediction 4`. So the "decisive" framing in
the title overstates a test whose own prior of finding anything is 0.08. Keep the
test (it is genuinely cheap and key-free); drop HA-1 and the word "decisive".

### IDEA-20260808-b9a74c — REFUTED

Claim (A): *"substituting def for the hull inside the support-splitting signature
yields a per-coordinate discriminator wherever the shortened codes still have
nonzero defect."*
Claim (B): *"the shortening depth at which the defect vanishes is an explicit
function of (m, t, n)."*

These contradict each other. Support splitting works because the invariant
computed on `C` shortened at coordinate `i` **varies with `i`** — that is the
entire mechanism, and it is why the hull (not determined by parameters) is used.
Shortening an alternant code at any coordinate `i` yields an alternant code with
the same degree over a support with one point removed: the parameters
`(n−1, k−1, t)` are identical for every `i`. If, as (B) asserts, `def` is an
explicit function of `(m, t, n)`, then `def(C_i)` is the **same integer for every
coordinate**, the signature multiset is constant, and it separates zero
coordinate classes. `prediction 1` ("monotone decreasing in shortening depth")
says the same thing: a function of *depth*, not of *which* coordinate. So
`prediction 2` ("Full separation above the threshold") is refuted by the record's
own claim (B) and prediction 1 before any code is built.

Additionally, on the deliverable, same-day `IDEA-20260808-3d3be9` (same goal,
same question) proposes to *"evaluate the square-code dimension defect directly
on real standardized public keys, with matched random and alternant nulls, and
report a measured distance instead of a transcribed one"*. b9a74c's claim (B) is
the transcribed version — its own `hidden_overhead_disclosure` says *"The
threshold formula's constants are transcribed from unread records"*. On
GOAL-MCE-001 criterion 1, 3d3be9 dominates on both reliability and cost.

Narrowest surviving conclusion: the toy `def`-vs-rate-vs-shortening table is
still worth producing as an instrument calibration, with the random-code null and
the saturation-margin report the record already specifies. The per-coordinate
discriminator claim should be withdrawn.

### IDEA-20260808-4f83f6 — REFUTED (part A)

Part (A): *"R2 is a PUBLIC predicate: w − c s2 = A y − c s2 = A(z − c s1) − c s2
= A z − c(A s1 + s2) = A z − c t, so R2 depends on the secret only through the
public t; hence conditioning on R2 cannot bias z given c."*

The identity is exact — I verified it by substitution (`w = Ay`, `z = y + c·s1`,
`t = A·s1 + s2` ⇒ `Az − ct = Ay + cAs1 − cAs1 − cs2 = w − cs2`). Two errors follow it.

1. **`t` is not public.** ML-DSA's public key is `(ρ, t1)` with
   `t = t1·2^d + t0`, and `t0` lives in the private key. The program's own
   `GOAL-MLDSA-002.yaml` states the point directly: *"FIPS 204's assertion that
   t0 need not be regarded as secret because it is reconstructible from a small
   number of signatures"* — reconstructible, i.e. **not published**. So R2 is
   `(pk, t0)`-computable, which is *exactly the class the record assigns to R3*.
   The advertised "clean split into PUBLIC and SECRET rejections", which is the
   title and the headline, does not exist. The real partition the record has
   discovered is `z`-biasing vs `c`-biasing, which is a different and still
   useful statement.
2. **"conditioning on R2 cannot bias z given c" is false.** Given `c` and `t`,
   R2 is a deterministic predicate on `z`; conditioning on `¬R2` restricts `z` to
   a `(c,t)`-dependent set. The correct statement is that the accepted pair is
   *simulatable given `t`* — which is why FIPS 204 needs R3 and the hint at all,
   and which is the same `(pk, t0)` conclusion as part B.

Part (B) (the `t0`-dependent deviation in the accepted-challenge law) and the
per-predicate rejection rates are unaffected, and the record is commendably
explicit that part B is likely dominated by the hint route. Rewrite part A as
"R1 and R2 do not depend on `(s1, s2)` beyond `t`; R2, R3 and R4 all depend on
`t0`; only R1 is `pk`-computable" and the record stands.

### IDEA-20260808-f4edc6 — REFUTED (pre-registered acceptance criterion)

`prediction 1`: *"measured mean vs C(B+m-1,m)/N — predicted: equal to machine
precision, at every cell … this is an identity and any deviation is a bug in the
harness."* `falsification_conditions[0]`: *"Measured mean differs from
C(B+m-1,m)/N by more than floating-point error ⇒ harness bug; nothing else may be
interpreted until fixed."*

`C(B+m-1,m)/N` is exact **in expectation** over a uniform target. The *sample*
mean over `T` targets is a random variable with `sd = sqrt(mu/T)`:

```
p~2^22 B=64  m=3 T=10^4 : mu=0.01091  sd(sample mean)=1.04e-03  (9.57% of mu)
p~2^22 B=128 m=3 T=10^4 : mu=0.08530  sd=2.92e-03               (3.42% of mu)
p~2^22 B=256 m=3 T=10^4 : mu=0.67450  sd=8.21e-03               (1.22% of mu)
p~2^22 B=128 m=4 T=10^5 : mu=2.79346  sd=5.29e-03               (0.19% of mu)
```

Direct simulation in an abstract group (N=2^20, B=200, m=3, T=2×10^4): exact mean
1.290703, sample mean 1.288650, gap 0.159% — about `10^{13}` times machine
epsilon. As written, the gate fires on a correct harness with probability ≈ 1
and blocks every other reading in the ledger. Fix: state the tolerance as a
Poisson band `mu ± z·sqrt(mu/T)` with the required `T` pre-registered per cell.

Cross-record contradiction worth resolving before dispatch: same-day
`IDEA-20260808-0e9fa1` (same `question_id: RQ-ECDLP-002`) proposes to decide
*"unconditionally, whether the windowed decomposition count matches the
KN-FIND-007 mean or falls below it."* f4edc6 is right that the mean cannot fall
below — it is an exact linearity identity for a uniform target, independent of
the geometry of `V`. What can fall below is *coverage*, which is f4edc6's
`prediction 2`. The two records should be reconciled or 0e9fa1's premise
corrected.

### IDEA-20260808-ae34ad — REFUTED (arm 1 and headline arithmetic)

Claim: *"IDEA-20260805-88ecef takes the position that the FORS multi-target
attack buys its advantage with a table holding roughly q*k revealed leaf indices
with random access … an approximate membership structure with about
1.44*log2(1/eps) bits per element suffices — at eps = 2^-10 that is about 14.4
bits per target versus a 64-bit cell, a factor about 4.4 reduction."*

I read 88ecef's mechanism. It charges:

> "Total live cells M = q*k (**one a-bit index** per tree per signature; the
> n-byte preimages are only needed for the single winning trial, so the working
> table is index-only and **M = q*k is a LOWER bound on the honest memory**,
> which is the conservative direction for an argument that charging matters).
> … a random access into M cells costs M^theta unit operations … W_theta(q) =
> U(q) * M(q)^theta"

Three consequences.

1. **The 64-bit cell is a strawman.** 88ecef never charges 64 bits per element;
   it charges `M = q·k` *cells* and applies `M^θ`. Reducing bits-per-cell does
   not change `M`, so arm (1) cannot move 88ecef's number at all.
2. **Even in a bits-charged model the Bloom filter loses.** A filter at
   `1.44·log2(1/ε) = 14.4` bits/element at `ε = 2^-10` is compared against an
   `a`-bit index. 88ecef's own worked cells are `k = 14` and `k = 33`, i.e. the
   FIPS 205 128s (`a = 12`) and 128f (`a = 6`) sets. At `a = 6` the filter is
   2.4× **larger**; at `a = 12`, 1.2× larger; at `a = 14`, a wash. The claimed
   "factor about 4.4 reduction" exists only against a cell width nobody used.
3. **The headline bits do not follow from the record's own numbers.** The stated
   arithmetic gives `6 → 3.85` bits per element, a **2.15**-bit change, not the
   "3-4 bits" claimed; and 88ecef's credit is the ladder `θ·log2(q·k) = 22.6
   (θ=1/3) / 33.9 (θ=1/2) / 67.8 (θ=1)` bits, not the "15-20 bits" attributed to
   it.

What survives, and is the record's real content: arm (2), the distinguished-
prefix partition trading success probability for `O(1)` memory (the van
Oorschot–Wiener move on a covering problem, correctly identified), and arm (3),
that the grinding search has **no shared state**, which is a direct and
legitimate challenge to whether `M^θ` should be charged at all under a parallel
model. Both are unaddressed by 88ecef. Reissue the record as those two arms with
the Bloom arm deleted and 88ecef's actual `M^θ` model reproduced first, as the
record itself promises ("must therefore reproduce it exactly before departing
from it").

### IDEA-20260808-3da739 — REFUTED (audit firing rule)

Falsifiable form: *"The audit fires if and only if some published point's
provenance is an isogeny whose kernel is secret-dependent AND whose degree
exceeds the available torsion level."*
HB-4: *"Torsion images under a publicly computable isogeny confer no advantage …
because the attacker can recompute them from public data at polynomial cost."*

These two do not partition the objects. SQIsign's **response** isogeny has a
secret-dependent kernel (it is computed through the secret key ideal) **and** is
published as an efficient representation, hence is publicly computable once the
signature is seen. It therefore satisfies the firing condition *and* is exempted
by HB-4. The audit as specified emits a false positive on the honest protocol,
which is the worst failure mode for an instrument whose stated deliverable is
"does not apply". The record's own confounder half-sees this ("'Secret-dependent'
is not binary in a Fiat-Shamir protocol … the audit must classify compositions,
not just atoms") but the firing rule is stated on atoms. A third category —
*secret-dependent kernel, publicly computable after publication, images therefore
free* — is required, and the audit must be re-derived around whether the
published images are images **under the key isogeny at a torsion level exceeding
its degree**, which is the actual Kani ingredient.

Also: **missing KN-TECH-057** (see the sweep below). `best_known_baseline` is
"p^{1/3+o(1)} conditional key recovery (KN-TECH-058)" with no classical
full-cost matched row.

### IDEA-20260808-f313da — REFUTED (prediction 3), headline preserved

`prediction 3`: *"correlation between (multiplicity gain) and (N1/p^{1/3}) —
predicted: NEGATIVE — curves with small N1 get more gain."*
`falsification_conditions[2]`: *"The gain-versus-N1 correlation is non-negative,
falsifying the convexity mechanism."*

I computed the gain exactly as the record defines it — `gain = P0/ρ(u_1)` with
`P0 = 1 − Π(1−ρ(u_i))` — under the record's own constraint `N1·N2·N3 = p`,
using a numerically exact Dickman `ρ` (validated: `ρ(2) = 0.306853`,
`ρ(3) = 0.0486084`, matching the standard values), at `p ~ 2^248`:

```
u_balanced=2  corr = +0.7270   mean gain 1.0526  range [1.0000, 2.1707]
u_balanced=3  corr = +0.7266   mean gain 1.0844  range [1.0000, 2.8491]
u_balanced=4  corr = +0.6191   mean gain 1.0815  range [1.0000, 2.9731]
u_balanced=5  corr = +0.5094   mean gain 1.0720  range [1.0000, 2.9818]

Explicit points at u_balanced = 3:
  (log N_i/log p)=(1/3,1/3,1/3)     u=(3.00,3.00,3.00)  gain = 2.8565
  (0.30, 0.33, 0.37)                u=(2.70,2.97,3.33)  gain = 1.7572
  (0.20, 0.38, 0.42)                u=(1.80,3.42,3.78)  gain = 1.0395
  (0.10, 0.42, 0.48)                u=(0.90,3.78,4.32)  gain = 1.0000
```

The correlation is **strongly positive at every parameter**, and the record's own
falsification condition fires. The mechanism is forced by the record's *own*
constraint: `N1N2N3 ≈ p` is fixed, so a smaller `N1` pushes `N2, N3` up and
drives `ρ(u2)/ρ(u1) → 0`. The gain is **maximal at balanced minima** (2.86 at
`u = (3,3,3)`) and collapses to exactly 1 as `N1` shrinks.

The inference chain is also broken independently of the sign. *"since u → u log u
is convex, the sum Σ ρ(u_i) is MAXIMISED at unequal u_i"* — the conclusion about
`Σρ` is true (`ρ'' = [(log u+1)² − 1/u]·ρ ≥ 0` for `u ≥ 1`), though not for the
stated reason (`exp(−convex)` is log-concave, not convex, in general). But the
record's "gain" is the **ratio** `Σρ(u_i)/ρ(u_1)`, and convexity of `Σρ` says
nothing about that ratio; the ratio is maximised at *equal* `u_i`. And
`prediction 2` ("strictly between 1 and 3") is a tautology: `ρ` is decreasing and
`u_1 ≤ u_2 ≤ u_3`, so `ρ(u_1) ≤ Σρ(u_i) ≤ 3ρ(u_1)` identically — it cannot
discriminate anything.

**Preserve the headline.** The record's actual conclusion — that the multiplicity
gain is *well below* the naive factor 3 on typical curves, and that Section 4.1's
caveat is right in sign — is confirmed: mean gain 1.05–1.08 across all tested
`u`. That is the finding; the convexity mechanism and prediction 3 should be
deleted and replaced by "the gain is maximal at balanced minima and → 1 as N1
falls, so it is small exactly where the record's own Lemma-3.5 route is
strongest".

On the constraint itself: `p/4 ≤ N1N2N3 ≤ p/2` given `det N = p/4` is the
classical Gauss–Seeber bound for reduced positive ternary forms (`det ≤ a11a22a33
≤ 2·det`), and `N1N2N3 ≥ det` follows from Hadamard plus `|det V| ≥ 1`. My quick
numeric harness for successive minima was **not reliable** (94% inside `[1,2]`,
failures traceable to a too-small enumeration box and a float rank test), so I did
not independently confirm the upper constant `2`. The record's own FORCED-VALUE
CONTROL is the correct check and should be run first — it is well designed and
can genuinely fail.

Credit where due: this record cites KN-TECH-057 **and** its `dominated_by`
explicitly checks "KN-TECH-057's four full-cost rows" along with KN-TECH-058's
two tiers and the vOW curve. That is the best `dominated_by` field in the slice.

### IDEA-20260808-621df3 — NOVEL content, filing defect

The arithmetic identity is correct. For `D ≡ 0 (mod 4)` the principal form is
`x² + (|D|/4)y²`; for `D ≡ 1 (mod 4)` it is `x² + xy + ((1−D)/4)y²`, whose
minimum over real `x` at fixed `y` is `|D|y²/4`. In both cases every `y ≠ 0`
gives a value exceeding `B` exactly when `|D_f| > 4B`, so the only elements of
norm `≤ B` are `±x` with `x² ≤ B`, i.e. `rho_f(B) = 2⌊√B⌋`. The three
statements of the threshold across `claim` / `mechanism` / `predictions` are
mutually consistent (`4B < |D_f|`).

**Filing defects.** (i) **No `goal_id`** — the record carries only
`question_id: RQ-ECDLP-002` and is bound to no campaign. This is shared with all
six of its concurrent-session siblings (`3f8a2b`, `4f3ef4`, `7c4e9d`, `a3f7c1`,
`b8e2d4`, `c5f9a2`). (ii) Eleven fields present in every sibling record in this
slice are absent: `proposed_by`, `why_not_a_renamed_known_approach`,
`heuristic_assumptions`, `target_complexity`, `interpretation_limits`,
`discriminated_from`, `source_refs`, `estimated_cost`, `recommended_priority`,
`honest_prior_of_survival`. Without `source_refs` the "four prior source
artifacts" it proposes to hash are unnamed.

**Oracle-closure check (KN-FIND-002 / -b7e091 / -982fdf).** 621df3 is *not* an
oracle proposal — it is a reanalysis of a counting premise with
`sota_delta: 0` and `dominated_by: Pollard rho`. The GGM closures do not bite. Its
six siblings (x-oracle / MITM / y-coordinate / full-point / endomorphism-image)
do sit on that ground and are not in my slice; note only that `c5f9a2`
("ENDOMORPHISM-IMAGE ORACLE FOR STRUCTURAL DECOMPOSITION: an oracle that returns
whether a p…") is prima facie inside **KN-FIND-002 §2** and **KN-FIND-b7e091
Oracle D**, which close endomorphism-image oracles for prime-field curves at
exponent 1/2 with `O(1)` (indeed zero) overhead, since `End_{F_p}(E) = Z` forces
`φ = [m]`. Whoever holds that record should be asked to state its escape from
that closure explicitly.

**Closure burden.** The record asserts a closure (the G3 excursions are a cutoff
artifact). It supplies a named obstruction and a falsifiable control — good. It
does **not** supply forward guidance: if every prior `G3 > 4` cell turns out to
be sparse, the conservation prediction remains untested in the density-valid
regime at *any* depth, and the record does not name the `(B, |D_f|)` pair that
would test it. That is a required addition under `docs/inventor-protocol.md` §4.

---

## KN-TECH-057 sweep (assigned deliverable)

**Root cause confirmed.** `/tmp/ideas-ctx/KNOWLEDGE_BARRIERS.txt` line 117 reads
literally `- KN-TECH-057: >-` with no title text, while line 118 —
`KN-TECH-058: Supersingular isogeny-problem baselines, corrected against archived
primary text …` — is fully visible. So a generator working from the dedup file
saw the *successor-flavoured* record and not the full-cost record. Twelve of the
126 records cite KN-TECH-057 anyway (they read `knowledge/techniques/` directly):
`19876e, 287361, 3fdef7, 56e892, 589c19, 70243a, 71c077, 71c2b2, dfd76a, ee5d81,
f313da, f332da`.

I swept every `IDEA-20260808-*.yaml` for a `best_known_baseline` naming an
isogeny path-finding / EndRing / supersingular cost row. **Records that state
such a baseline and do not cite KN-TECH-057:**

| ID | goal | baseline as stated | what 057 supplies |
|---|---|---|---|
| **3da739** (this slice) | GOAL-SQISIGN-002 | `p^{1/3+o(1)}` conditional key recovery (KN-TECH-058) | the classical matched full-cost rows: vOW `p^{1/2}` (F_{p^2}), DG `p^{1/3}` (F_p), MITM `p^{2/3}` |
| **ba4e37** (this slice) | GOAL-ECTD-001 | `sqrt(h) = p^{1/4}` generic, "vOW on the action" | the F_p vOW `p^{1/4}` row is **conditional on unproven F_p subgraph mixing**; DG `p^{1/3}` is the unconditional fallback |
| 750ead | GOAL-SQISIGN-002 | `p^{1/3+o(1)}` conditional key recovery, zero data | same as 3da739 |
| 8a6cb5 | GOAL-SSI-001 | `p^{1/3+o(1)}` conditional on Heuristic 1 | same; and 057's memory/wiring penalty bears directly on its table-amortisation lever A7 |
| bba3dc | GOAL-CRYPTO-001 | "KN-TECH-050 memory-charged path-finding" | 057 is the record that decides **which algorithm is the matched baseline** under full cost (MITM/DG → vOW) |
| 5ee6b4 (borderline) | GOAL-ECTD-001 | linear class scan `h·τ ~ p^{1/2+o(1)}` | ordinary-class rather than supersingular; flagged for completeness only |

Recommended coordinator action: repair the `KNOWLEDGE_BARRIERS.txt` extractor
(block-scalar `title:`) and issue a one-line correction to the five records above
requiring the matched full-cost row to be named. The other blanked entries —
`KN-FIND-720727` (ML-DSA formal proofs cover cryptographic adversaries only;
physical fault injection is outside the model) and `KN-FIND-860118` (the
uncorroborated "standardized schemes are broken under quantum attack" claim) — do
**not** collide with anything in this slice: `4f83f6` is explicitly a
non-fault, unmodified-signer measurement and states "NOT A BREAK, and the record
must be unreadable as one"; no record in slice 6 asserts a quantum break.

---

## What I actually checked

**Corpus files read in full or in relevant part:**
`knowledge/techniques/KN-TECH-057.md`; `knowledge/findings/KN-FIND-002.md`,
`KN-FIND-b7e091.md`, `KN-FIND-982fdf.md`, `KN-FIND-007.md`;
`ledger/evidence/EV-ECDLP-65b004.yaml`; `ledger/hypotheses/H-RSA-68884a.yaml`;
`ledger/goals/GOAL-MLDSA-002.yaml`; `ledger/proposals/IDEA-20260805-88ecef.yaml`;
and all 18 assigned records in full. Cross-checked against
`/tmp/ideas-ctx/{EXISTING_PROPOSALS,EXISTING_HYPOTHESES,REJECTED_TITLES,CATALOGUE_TITLES,DEFERRED_TITLES,KNOWLEDGE_BARRIERS}.txt`
and against all 126 `IDEA-20260808-*` records by topical grep (branch number,
MixColumns, yoyo, isogeny class, self-pairing, volcano, emulsifier, Schur,
support-splitting, windowed, FORS, provenance, successive minima, involution,
TCitH, LowBits, batch).

**Computations actually run (all outputs above are real):**

1. Branch-number distribution of 20,000 random invertible 4×4 matrices over
   GF(2^8), computed from the minor characterisation, gated on
   `branch(MixColumns) = 5` and `branch(I) = 2`. (83b3ba)
2. Lenstra CM-structure identity `n_1 = gcd(A−1, m)` tested by full curve
   enumeration over `F_307` (all `p²` curves, grouped by trace, group exponent
   from 60 random points per curve, `n_1 = N/exponent`): predicted vs observed
   `n_1`-sets, 20 traces, 20/20 exact match. (4d77a6)
3. Conditional law of `A−1 mod ℓ` given `ℓ | f` over 4,000 random ordinary
   `(p, t)` at `p ∈ [2^20, 2^21]`, `ℓ ∈ {3,5,7,11}`, with the residue-support
   histogram. (4d77a6 HA-1)
4. Dickman `ρ` computed on a `h = 0.002` grid and validated against
   `ρ(2) = 0.306853`, `ρ(3) = 0.0486084`; then 20,000 constrained triples per
   `u_balanced ∈ {2,3,4,5}` to measure `corr(gain, log N1/log p^{1/3})`. (f313da)
5. D2 statistic (best additive successor rule over adjacent nibbles) on the four
   real EV-ECDLP-65b004 placeholders and on 200,000 genuine SHA-256 digests, plus
   the lag-2 variant and the filler's period structure. (b3c97b)
6. Sampling-error arithmetic and a direct 20,000-target simulation
   (`N = 2^20`, `B = 200`, `m = 3`) of the KN-FIND-007 mean identity. (f4edc6)
7. Re-derivation of every numeric anchor in 71c077: `1.181 + 1.022 − 0.5 = 1.703`
   vs 1.704; `c(0)³ = 64/9`, `c(0) = 1.922999`; `c(1/3) = (2401/324)^{1/3} =
   1.949616`; `β(0)³ = 8/9`; `δ(0)³ = 3`; `2.243510 = (2 + 1/3)(8/9)^{1/3}`, the
   symmetric-charging value H-RSA-68884a records at θ = 1/3;
   `L[1/6, c] ⊂ L[1/3, o(1)]`. All correct.
8. By hand: the MAYO Kronecker identity (`polar(λᵀP*) = C(θ) ⊗ M_λ`);
   the ML-DSA identity `w − c·s2 = A·z − c·t`; the HAWK involution enumeration in
   `(Z/2^l)^*` and the `Q(√−2)` anchor at `l = 3`; the Gauss–Seeber ternary
   bound; the `rho_f(B) = 2⌊√B⌋` sparse-row identity; the Bloom-vs-`a`-bit-index
   comparison at the FIPS 205 sets 88ecef uses.

**What I could NOT verify, and what would settle it:**

- **All external novelty.** Web search unavailable. Every "NOVEL" above means
  "novel against this corpus". The specific external risks the records name
  themselves and that I could not adjudicate: KN-LIT-7592's unread appendices
  (b1358c), KN-LIT-7489 (ba4e37, entirely blocking its parts C/D), the MAYO
  specification (ae175e, which says it is "void until the spec is read"), the
  MQOM v2.1 spec (721f2b), FIPS 205 §index-derivation (ae34ad arm 2),
  Couvreur–Otmani–Tillich (b9a74c).
- **The Gauss–Seeber upper constant `2`** in f313da. My successive-minima harness
  was unreliable (enumeration box ±6, float rank test); the theorem is classical
  and I accepted it. The record's own FORCED-VALUE CONTROL settles it and can
  genuinely fail — run it first.
- **0bde1a's enumeration feasibility.** The record's two quantitative predictions
  ("node count grows ≥ 4× per unit of D" and "terminates for D ≤ 40 within
  10^3 s") imply ≤ 2^36 nodes at D = 40 while 4^40 = 2^80. The missing number is
  `R/λ1(L)` for the X1-01 embedding, which I could not read (`out/X1b.yaml.orig`
  only). Settled by reporting `R/λ1` and `vol(B_D(R))/det(L)` at one cell before
  any NEG-1 claim.
- **83b3ba's direction of effect.** I argued from the campaign's own scale
  (AES 59 vs null 4.0; ideal permutation 14 vs 1) that the identity-layer arm
  should be maximal, not minimal. Settled by one run of the identity-layer arm at
  the campaign's existing exposure — which is cheap and should be the *first*
  arm, since a decreasing ordering voids the pre-registered table.
- **The six unbound sibling records** (`3f8a2b`, `4f3ef4`, `7c4e9d`, `a3f7c1`,
  `b8e2d4`, `c5f9a2`) are outside my slice; I flag only that `c5f9a2` is prima
  facie inside KN-FIND-002 §2 / KN-FIND-b7e091 Oracle D and needs an explicit
  escape statement.

## One concrete next action

Run the three computations that each cost minutes and each void a
`recommended_priority: high` record before any batch is spent on it: (1) the
identity-layer yoyo arm for **83b3ba** (if hits exceed AES's 59 the pre-registered
ordering is inverted and the whole four-point design must be rewritten);
(2) D2 against the four real EV-ECDLP-65b004 placeholders for **b3c97b** (it
scores 0.1148 — reproduce it and withdraw D2, keeping D1 and Claim B); and
(3) 88ecef's `M^θ` charge reproduced exactly with `M = q·k` a-bit index cells for
**ae34ad** (which deletes arm 1 and leaves the prefix-partition and
no-shared-state arms, which are the record's real content).
