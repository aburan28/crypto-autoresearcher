# Adversarial re-screen — slice4 (19 records)

Reviewer: red team. Snapshot: `/tmp/wt-ideas-100` @ `9b49a54f0` (read-only; nothing committed
or edited). Web search unavailable — **all external novelty is UNADJUDICATED** and every verdict
below is an in-corpus / internal-soundness verdict only.

Headline: **9 of 19 carry a substantive, computationally demonstrated defect**; 4 more need a
`discriminated_from` note against a same-round sibling that neither cites; 6 survive checking.
Two records (`c5f9a2`, `40aab9`) should not have been filed in their current form.

---

## Verdict table

| ID | verdict | one-line reason |
|---|---|---|
| IDEA-20260808-ddb522 | REFUTED (partial) | HA-1 calls the cost invariance "PROVED"; the AES **key schedule** is not column-rotation equivariant — full-cipher equivariance fails 1000/1000. |
| IDEA-20260808-f7e6e7 | PARTIAL-OVERLAP + defect | Same-round `IDEA-20260808-812554` derives the identical `C_rel = m!N B^{(m-1)(σ-1)}` and σ=1 cancellation; pre-registered `dσ/dτ = 2` is actually **0.5**. |
| IDEA-20260808-8aaddb | NOVEL (defect noted) | Well-screened; but its own known positive (`0.011 = 1/397`, d=2) sits **at** the detector's own stated false-positive rate `k²·10⁻ᵈ`. |
| IDEA-20260808-e2315e | SCOPE-INFLATED (cost model) | Pre-registers `ω' ≥ 2` (threshold 2.5) while its own cited KN-TECH-015 states `Õ(D⁶·B³)` ⇒ ω'=6 ⇒ threshold **7.5**; lattice memory charged `N^δ` where a D×D basis is `N^{2δ}`. |
| IDEA-20260808-f332da | NOVEL | Every derived number reproduced exactly; records a hand computation that contradicts its own stated P1 direction. Best-constructed record in the slice. |
| IDEA-20260808-40aab9 | **REFUTED** + PARTIAL-OVERLAP | The headline iff is false: exhibited curves with `k_emb = 1` and rank-1 `N`-torsion. Same-round `bba3dc` states the correct criterion. |
| IDEA-20260808-71fea9 | PARTIAL-OVERLAP | Its (b2)+(b3) are `IDEA-20260808-8e13ff`'s T2+T3 verbatim in substance; 8e13ff cites 71fea9, 71fea9 does not cite 8e13ff. |
| IDEA-20260808-2df781 | NOVEL (correction) | Sound integer program; the pre-registered artifact tell is stated **backwards** (nesting gives non-increasing, not strictly decreasing). |
| IDEA-20260808-d21021 | REFUTED (partial) | C-A is false as written: the marginal takes **two** values (0.4742 off `S_e`, 0.5259 on it, 46σ apart) and does not reprove Prop. 6.1.2. |
| IDEA-20260808-a3bcf0 | REFUTED (partial) | Claim (A) prices only `C(p,p/2)` (6–13 bits) and drops the redundancy factor `C(k+l−p,ε)` (**11–25 bits**) — the larger of the two. |
| IDEA-20260808-63427b | NOVEL (defect noted) | The pre-registered pool factor `4.08/2.92 = 1.40` evaluates numerator at N=4096 and denominator at N=2048; self-consistent value is **1.30–1.34**. |
| IDEA-20260808-90632c | NOVEL | Central 0.866 factor verified by Monte Carlo (0.8660–0.8692) with the Gaussian null at 1.000. Clean. |
| IDEA-20260808-726aa3 | NOVEL (correction) | Main-term exponent inflated by `p^{m-1}` (measured ratio 1.0e6 at p=1009, m=3) and error term missing `1/d^m`; the two cancel only at β = 1/m. |
| IDEA-20260808-56e892 | REFUTED (partial) | Its DG row `p^{1/4+θ/12}` gives `p^{0.278}` at θ=1/3, contradicting its own cited KN-TECH-057's archived `p^{1/3}`; BSGS row uses a different, correct rule. |
| IDEA-20260808-d873bc | REFUTED (partial) | HA-1 charges `M·T` (θ=1) and attributes it to KN-TECH-035/-044, which charge `W·S^{1/3}` (θ=1/3). The crossover M* is a function of exactly this. |
| IDEA-20260808-287361 | REFUTED (design) + PARTIAL-OVERLAP | Plug-in posterior entropy collapses to 0 by q=4 **under the record's own null**, even at N=10⁴; screen omits `IDEA-20260801-020`. |
| IDEA-20260808-dfd76a | NOVEL | Headline claim verified directly against the frozen text: `[6]` is cited at line 193 and appears in neither the affected nor the safe list. |
| IDEA-20260808-3f8a2b | REFUTED (cost model) + PARTIAL-OVERLAP | Its own formulas give `cost_ratio ≈ 0.02–0.11`, not the pre-registered 0.3–0.7, and an **asymptotic** `1/|F|` gain, contradicting "constant factor only". |
| IDEA-20260808-c5f9a2 | **REFUTED** | The claimed `m/d` advantage is an `m!` vs `(m-1)!` overcount; at d=1 the oracle is a constant function and the "algorithm" *is* exhaustive search. |

---

## Kills and required corrections

### IDEA-20260808-c5f9a2 — REFUTED. Should not have been filed.

Three independent failures, each fatal.

**(1) The pre-registered advantage is a double-count, not a mechanism.** The record's corrected
derivation sets `Y_exhaust = B^m/(m! N)` and `Y_phi = (B/d)·B^{m-1}/((m-1)! N)`, giving
`Y_phi/Y_exhaust = m/d`. The `m` comes from dividing by `(m-1)!` in one arm and `m!` in the other.
At `d = 1` the algorithm literally reads "for each of the B factor-base points `P_i`, decompose
`R − P_i` at arity `m−1`", which *is* exhaustive arity-`m` decomposition of `R`. Counted directly:

```
B= 50 m=3: C(B,m) =    19600 ;  B * C(B,m-1) =    61250 ;  ratio = 3.1250   (claimed 'gain' = m = 3)
B= 50 m=4: C(B,m) =   230300 ;  B * C(B,m-1) =   980000 ;  ratio = 4.2553   (claimed 'gain' = m = 4)
B= 20 m=3: C(B,m) =     1140 ;  B * C(B,m-1) =     3800 ;  ratio = 3.3333   (claimed 'gain' = m = 3)
```

Every ordered tuple is counted `m` times; the same relation set is found. True ratio = 1. This is
the same species of defect as `IDEA-20260808-2e14f7`'s degree-`d` fibre factor.

**(2) "phi(E) has index d in E" is false.** The index is `|ker φ(F_p)|`, not `deg φ` (exact
sequence + Lang). Measured over sampled curves with `φ = [2]`, `deg φ = 4`:

```
index = 1   e.g. p=23, y^2=x^3+1x+3, #E=27
index = 2   e.g. p=23, y^2=x^3+0x+1, #E=24
index = 4   e.g. p=23, y^2=x^3+1x+2, #E=24
```

Worse, the record's own assumption places the work in `G = <P>` of **prime** order `N`. There
`[2]` is a bijection:

```
p=53, N=13:  |G| = 13,  |[2]G| = 13,  index = 1
=> the oracle 'is R in [2]G?' answers YES for every R in G: it is a CONSTANT function.
```

This is `H-ENDO-001`'s scalar-action fact, which the corpus already carries and which the record
does not screen against.

**(3) The record contains three mutually contradictory predictions.** Section (C) PREDICTION 1
says `Y_phi/Y_exhaust ~ d`; PREDICTION 2 says the advantage is maximised at *large* degree;
PREDICTION 3 says it *vanishes* at degree 1. The `predictions:` block then pre-registers
**3.0 ± 0.5 for the degree-1 automorphism** — the maximum advantage, at the degree where (C)
PREDICTION 3 says there is none, and where the oracle is a constant function.

**(4) The null is required to reproduce the treatment.** `NULL OBJECT 1` states: "The algorithm
run with `O_rand` must yield `Y_rand = Y_exhaust * (m/d)`." By the record's own design the entire
claimed effect is reproduced by a random oracle carrying zero information about `φ`. Under
`docs/inventor-protocol.md` §3 that is a controlled null, not a finding — and the record says so
without noticing.

### IDEA-20260808-40aab9 — REFUTED on its headline if-and-only-if.

Claim (B): "Over `F_p` with `N` prime and `N ‖ #E(F_p)` … the full `N`-torsion is `F_p`-rational
if and only if `ord_N(p) = 1`." Prediction 1: "rank 1 in exactly those instances with `k_emb > 1`,
rank 2 in exactly those with `k_emb = 1`, with no exceptions. This is an if-and-only-if, so a
single off-diagonal cell falsifies (B)."

Under the record's own hypothesis `N ‖ #E(F_p)`, the `N`-Sylow of `E(F_p)` has order exactly `N`,
so the rank-2 cell is **provably empty** — for every curve, including `k_emb = 1` ones. Exhibited
by search and confirmed by explicit group enumeration:

```
#E(F_53) for y^2=x^3+x+15 : 52
N=13 divides #E: True ; N^2 divides #E: False
N | p-1 : True   ord_N(p) = 1
trace t = p+1-#E = 2 (nonzero => ordinary)
|E(F_53)[13]| = 13 => F_p-rank of the 13-torsion = 1
```

Eight such curves found in the first search window; all have `k_emb = 1` and rank 1. By the
record's own falsification condition, (B) is falsified. Two further consequences:

- The record's **planted positive control** ("choose `p` and `N` with `N | p−1` … The instrument
  must report rank 2 for them; if it reports rank 1 everywhere, the rank test is broken and no
  negative conclusion may be drawn") is unsatisfiable under its own scope, so the minimal test as
  designed returns "instrument broken" and blocks the conclusion.
- Balasubramanian–Koblitz is misapplied. Its hypothesis is `N ∤ q − 1`; the record invokes it at
  exactly the excluded case `k = 1`. This is the "cited theorem's hypotheses checked" failure.

**What survives, narrowest form:** rational full `N`-torsion ⟹ `N | p − 1` ⟹ MOV applies. The
closure direction the record actually needs is intact and is in fact *stronger* than claimed —
`k_emb = 1` alone does **not** deliver the graph kernel. The title's "if and only if" and the
sentence "the Kani route and the MOV route coincide exactly" must be withdrawn.

**Overlap:** same-round `IDEA-20260808-bba3dc` states the correct criterion — "`E[M]` is rational
over `F_{p^k}` with `k` = ord of `π` in `(O/MO)^*`" — which correctly forces `M² | #E(F_p)` as well.
Neither record cites the other. `40aab9` needs: *"IDEA-20260808-bba3dc gives the correct
torsion-rationality criterion (order of π in (O/MO)^*, not ord_N(p)); this record's k_emb = 1
condition is necessary but not sufficient and its converse is false under N ‖ #E."*

### IDEA-20260808-56e892 — REFUTED on its own table.

The record's deliverable is a per-primitive θ-parametrized charging table whose stated purpose is
to stop the program using two incompatible memory charges. Two of its own rows use incompatible
rules:

```
BSGS: W=n^0.5, S=n^0.5;  correct charged exp = 0.5 + theta*0.5 = 0.666667  (at theta=1/3)
DG   : W=p^0.25, S=p^0.25;  correct charged exp = 0.25 + theta*0.25 = 0.333333  (at theta=1/3)
KN-TECH-057 archived: DG full cost = p^(1/3);  KN-TECH-035 archived: BSGS full cost = n^(2/3)

Record states 'BSGS n^(1/2 + theta/2)' and 'DG p^(1/4 + theta/12)'
  BSGS at theta=1/3 -> n^0.666667   MATCHES archived 2/3? True
  DG   at theta=1/3 -> p^0.277778   MATCHES archived 1/3? False
```

The DG row substitutes the already-evaluated clock exponent `1/12 = (1/4)·(1/3)` as if it were
`θ/12`. Its own reproduction check (θ = 0 must return `p^{1/4}`) passes and therefore does not
catch it. This is exactly the class of error the record exists to prevent, in the record itself.
The GNFS rows are fine: `c(0) = (64/9)^{1/3} = 1.922999` ✓, and the "symmetric alternative"
`2.243510` is precisely `c(0) + θ·β(0) = 1.922999 + 0.9615/3` — i.e. the *un-re-optimised* charge,
which should be labelled as such rather than as a modelling branch. The `2980` figure and the
92-bit shift reproduce (`f(3072) = 50.02`, target `49.34`, `f(2960) = 49.22`, `f(3000) = 49.51`,
interpolation → 2977).

### IDEA-20260808-d873bc — REFUTED on its charging convention.

HA-1: "Full cost equals hardware quantity times time occupied (the Wiener composition), so an
attack holding `M` bits for time `T` costs at least `M·T`" and "This is a model definition already
adopted by this program for its ECDLP, lattice and isogeny work (KN-TECH-035, KN-TECH-044)."

It is not. KN-TECH-057, verbatim: "a table of `S` entries occupies volume `S`, giving a clock cycle
`τ = S^{1/3}` … Full cost = `W × τ`." KN-TECH-035's complexity line: "BSGS `n^{1/2}` processor
steps but `n^{2/3+o(1)}` full cost" — i.e. `n^{1/2} · (n^{1/2})^{1/3}`, θ = 1/3, not θ = 1.
Sibling records `f332da` and `56e892` both use θ = 1/3 and cite the same two sources.

This is load-bearing: the whole deliverable is the crossover memory `M*` at which the charged ISD
curve crosses the flat grinding curve, and `M*` is a direct function of how hard memory is charged.
At θ = 1 the ISD curve is raised roughly three times as much in the exponent as at θ = 1/3, so the
record's prior "`M*` above 2^60 bits" is computed under a charge its own sources do not license.
Fix: re-state HA-1 as `W·S^θ` with θ declared on the program's grid, and report `M*` as a function
of θ, which is what the record's own MODEL-DEPENDENCE CONTROL already asks for.

### IDEA-20260808-d21021 — C-A is false as written.

C-A: "For every fixed ciphertext support triple and uniformly random secret supports,
`Pr[e'_c = 1]` is the SAME number for every coordinate `c` … This reproves the specification's own
Prop. 6.1.2." Under the record's own conditioning `e` is attacker-derived and therefore
deterministic, so `e'_c = u_c ⊕ e_c` and the marginal takes two values. Simulation
(n=101, ω=7, ω_r=9, ω_e=5, 2×10⁵ draws):

```
S_e = [7, 11, 30, 54, 70]
mean Pr[e'_c=1] over c IN  S_e : 0.52593
mean Pr[e'_c=1] over c NOT in S_e: 0.47423
per-coordinate values in S_e : [0.5259, 0.5258, 0.5273, 0.526, 0.5246]
range over c NOT in S_e      : [0.4720, 0.4773]
Monte-Carlo s.e. per coordinate ~ 0.00112
```

A 0.052 separation at 0.0011 s.e. — 46σ, and the two groups do not overlap. The record does *not*
reprove Prop. 6.1.2, whose Bernoulli(p*) is over the full ciphertext ensemble including random `e`.

**What survives:** the use C-A is put to — `E[w(e')]` invariant under Ψ — still holds, because
`|S_e| = ω_e` is fixed: `E[w(e')] = n·q + ω_e(1−2q)`. Measured 48.156 vs predicted 48.155. C-B's
structure also survives; note that `r_{S_e}(d)` enters through the sign autocorrelation
`Σ_c(1−2e_c)(1−2e_{c−d}) = n − 4ω_e + 4r_{S_e}(d)`, not through a variance contribution from `e`,
and the record's derivation should say so. Required correction text for the record: *"C-A: the
marginal is `q` off `S_e` and `1−q` on `S_e`; it is constant across coordinates only after
averaging over `e`. The Ψ-invariance of `E[w(e')]` follows from `|S_e|` being fixed, not from a
uniform marginal."*

### IDEA-20260808-a3bcf0 — claim (A) prices the smaller of two factors.

Claim (A): "the number of representations of the target sub-error … is at most `C(p, p/2)` times a
factor from the redundancy positions … `C(p,p/2)` is a small CONSTANT (at p = 4 it is 6, at p = 8
it is 70). The representation technique is **therefore** worth at most a few bits."

The `therefore` drops the acknowledged second factor without bounding it. `R = C(p,p/2)·C(k+l−p,ε)`:

```
mceliece348864   k= 2720 l= 20 p=  8 eps=2: log2 C(p,p/2)= 6.13 bits  log2 C(k+l-p,eps)= 21.83 bits  total= 27.96
mceliece6688128  k= 5024 l= 20 p= 12 eps=2: log2 C(p,p/2)= 9.85 bits  log2 C(k+l-p,eps)= 23.59 bits  total= 33.45
mceliece8192128  k= 6528 l= 20 p= 16 eps=2: log2 C(p,p/2)=13.65 bits  log2 C(k+l-p,eps)= 24.35 bits  total= 38.00
```

The unpriced factor is 11–25 bits; the priced one is 6–14. Whether BJMM in fact wins is a
different question (larger `ε` also inflates the lists) — but it cannot be settled by bounding
`C(p,p/2)`, and the record's structural claim rests entirely on that bound.

Second, internal contradiction: the claim text says the technique is "worth **at most a few
bits**" (a small *positive* gain), while prediction 2 pre-registers that the best
representation-based configuration **trails** the argmin already at the free-memory basis (a
*negative* gain), and prediction 1 says no representation-based variant appears in the argmin under
any basis. These are not the same claim and cannot both be the pre-registration.

### IDEA-20260808-287361 — the measurement design cannot produce its pre-registered readout.

Title/claim say "EXACTLY by exhaustive enumeration"; the minimal test samples `q ≤ 8` transcripts
per key at cost `O(|V|·q·walk length)`. Under the record's **own** NULL OBJECT (transcripts
generated independently of the key, so `H(I|T^q) = H(I)` for every `q`), the plug-in estimator:

```
samples per pk N = 611
  q=1: plug-in H(I|T^q) = 2.3485 bits (truth 3.0000); apparent 'leak' delta(q) = 0.6515
  q=2:                    0.1060                                              2.8940
  q=4:                    0.0000                                              3.0000
samples per pk N = 10000        <- the record's own confounder says ~10^4 are needed
  q=1: 2.9648  (delta 0.0352)
  q=2: 1.3213  (delta 1.6787)
  q=4: 0.0006  (delta 2.9994)
  q=8: 0.0000  (delta 3.0000)
```

The pre-registered threshold `|ΔH| < 0.1 bits for all q ≤ 8` is unreachable at any feasible sample
count, and the escalation trigger "`delta(q)` growing with `q`" fires on pure estimator bias. The
record's stated granularity control cites KN-FIND-031's `1/N` floor on a *survival function*,
which does not cover plug-in entropy bias. Fix before any run: either restrict `q` so the joint
transcript alphabet is genuinely enumerable (which is what "exhaustive enumeration" would mean and
what the `O(|V|·q·L)` budget does *not* buy), or pre-declare a bias-corrected estimator
(Miller–Madow / NSB) with a power calculation.

Two overlaps the record does not carry:
- `IDEA-20260801-020` (same `RQ-SQISIGN-001`, fully visible in `EXISTING_PROPOSALS.txt`) already
  proposes a transcript-vs-matched-baseline leakage probe with a positive control. The objects
  differ (divergence test vs. posterior entropy), and 287361's claim paragraph is exactly the
  right discrimination — but the record asserts `novelty_status: screened` against
  `EXISTING_PROPOSALS.txt` and does not name the single nearest same-RQ row.
- Same-round `IDEA-20260808-19876e` proves that a leak yielding a candidate set of density
  `ρ = Θ(1)` gives `s = −log_p ρ = 0` and therefore **no exponent change**. A 0.1-bit entropy
  shrink is a constant-factor shrink. So 287361's entire detectable range is, by a sibling
  record in the same round, provably exponent-irrelevant. That must be stated in the record's
  interpretation limits.

Suggested `discriminated_from` addition: *"IDEA-20260801-020 runs a transcript-vs-baseline
divergence test; this computes a posterior over the secret ideal, which indistinguishability does
not bound. IDEA-20260808-19876e supplies the conversion lemma: any entropy shrink detectable at
this record's 0.1-bit resolution has s = 0 and moves no exponent, so the deliverable is a method
and a power statement, not a security-relevant quantity."*

### IDEA-20260808-3f8a2b — the cost model refutes the record's own scope statements.

The record's formulas are `Arm A = 2|F|^m`, `Arm B = |F|² + |F| + 2·candidates_verified`, with a
pre-registered `candidates_verified/|F|² < 0.5`:

```
|F|= 10  cand/|F|^2=0.5:  ArmA=     2000  ArmB=      210  cost_ratio=0.1050
|F|= 21  cand/|F|^2=0.5:  ArmA=    18522  ArmB=      903  cost_ratio=0.0488
|F|= 64  cand/|F|^2=0.5:  ArmA=   524288  ArmB=     8256  cost_ratio=0.0157
```

Two consequences. (a) The pre-registered band `0.3–0.7` ("30-70% cost reduction") is contradicted
by the record's own model, which gives 0.02–0.11 at the tested `|F| ≈ 10–21`. (b) `cost_ratio → 0`
like `1/|F|`, so the model asserts an **asymptotic** factor-`|F|` gain, directly contradicting
"CONSTANT FACTOR ONLY. Both arms have the same asymptotic complexity `O(|F|^m)`" and "the cost
reduction is a constant factor, not an exponent change." This is scope *deflation* rather than
inflation, but it is still an unchecked claim in a record whose entire content is a cost model, and
it makes the headline test (`is cost_ratio < 1?`) true by arithmetic — no experiment needed. The
only empirical quantity is `candidates_verified`.

Separate arithmetic error: `memory_exponent: O(|F|^2) = O(p^{2bm}) … For m=3, b=0.5, this is
O(p^3)`. With the record's own `|F| = p^b`, `|F|² = p^{2b} = p^{1.0}`, not `p^3`. Overstated by
`p^{2b(m-1)} = p²`.

**Overlap:** same-round `IDEA-20260808-7c4e9d` analyses the same `EXP-SEMAEV-f48dd1` arms and
already asserts the conclusion 3f8a2b proposes to test, in near-identical words ("the x-oracle MITM
provides a constant-factor cost reduction at toy scale, with no yield improvement, no asymptotic
complexity change, and no path to crypto-scale"). `IDEA-20260808-4f3ef4` proposes a third null on
the same table. 3f8a2b cites `EXP-SEMAEV-f48dd1` and `DEC-20260808-6a7ac4` but neither sibling.

### IDEA-20260808-ddb522 — HA-1's rigorous ingredient does not cover the object.

HA-1: "Equivariance of the round function under column rotation is a PROVED identity … so the
mathematical operation count is invariant by construction. What is heuristic is **only** that the
MEASURED cost tracks the operation count."

Checked with a from-scratch AES-128 that passes the FIPS-197 C.1 known-answer test
(`69c4e0d86a7b0430d8cdb78070b4c55a`):

```
(a) round function, independent round keys:  rho(Round_k(s)) == Round_{rho k}(rho s)  -> True
(b) key schedule: is rho(KeyExpansion(K)) == KeyExpansion(rho(K)) ?  mismatches in 200/200 random keys
(c) full AES-128:  rho(AES_K(P)) == AES_{rho K}(rho P) ?  mismatches in 1000/1000 random (P,K)
```

Generator (a) is correct for the round function with **independent** round keys — `ShiftRows` does
commute with column rotation (`s[r][c+r−1]` both ways), `MixColumns` acts identically per column,
`SubBytes` is bytewise. But the AES key schedule's `i ≡ 0 mod 4` rule (RotWord/SubWord/Rcon) is not
column-rotation equivariant, so `G` does not act on the keyed cipher. The record's shape set
explicitly includes "the guessed key-byte set", and the cost-invariance measurement is proposed on
"the campaign's r=5 recovery run" — a real keyed attack. So the mathematics is heuristic too, not
only the measurement.

**Narrowest valid conclusion:** the completeness certificate is sound for shapes defined in the
independent-round-key model (the standard setting for differential/integral distinguisher shapes).
It is not established for shapes that name key bytes of the real key schedule, and HA-1 must be
split into HA-1a (proved, independent round keys) and HA-1b (unproved, real key schedule). The
record's chosen null generator (row rotation) is correctly non-commuting and is a good control.

### IDEA-20260808-e2315e — the break-even threshold is charged at 1/3 of its own model.

The decision rule is `dε/dδ > ω'·m/(m−1)`, and the record pre-registers "`ω' ≥ 2` for any practical
reduction algorithm, so the threshold is `≥ 2.5` at `m = 5`." Its own cited source,
`knowledge/techniques/KN-TECH-015.md`, states in its `complexity:` line: *"LLL on a dimension-D
shift lattice with B-bit entries, ~O~(D^6 * B^3) classical"*.

```
omega'=2 (record's pre-registration), m=5: threshold = 2.500
omega'=6 (KN-TECH-015's own O~(D^6 B^3)), m=5: threshold = 7.500
omega'=6, m=3: threshold = 9.000
```

Choosing the loosest admissible `ω'` makes the derivative test three times easier to pass, i.e. it
biases toward declaring the lane alive. The record does disclose the `D^6` in
`hidden_overhead_disclosure` but still pre-registers the threshold at `ω' = 2`. Second
under-charge: a `D`-dimensional shift lattice basis stores `D²` entries, so lattice memory is
`N^{2δ}`, not the `N^δ` the record charges — and the record's own `time_memory_tradeoff` says this
lever "must be compared against vOW at matched memory", so the memory exponent is load-bearing.
Third, minor: "eps(δ) is non-decreasing" is called rigorous, but the Howgrave-Graham condition
carries a `√dim` factor that grows with `D`; monotonicity holds up to that factor, which is
`O(log)` and exponent-irrelevant but should be stated. Fix: pre-register the threshold at
`ω' = 6` (and report `ω' = 4` as an optimistic row), charge `N^{2δ}`.

### IDEA-20260808-f7e6e7 — near-duplicate derivation plus a wrong pre-registered number.

Same-round `IDEA-20260808-812554` (`RQ-ECDLP-002`) independently derives the identical core:
`T_solve = B^{(m-1)σ}`, `C_rel = m!·N·B^{(m-1)(σ-1)}`, "at `σ = 1` the B-dependence CANCELS
IDENTICALLY and the total is `m!N` for every `m` and every `β`". `f7e6e7` adds the multi-target
`√(TN)` comparator and the `(T,σ)` admission inequality; `812554` adds the single-target condition
`σ < 1 − 2/(m−1)`. Neither cites the other. Required note for `f7e6e7`: *"IDEA-20260808-812554
derives the same `C_rel` identity and the same `σ = 1` cancellation for the single-target
comparator; this record's additional content is the Kuhn-Struik `√(TN)` baseline, the infinite-K*
consequence, and the `(τ, σ, β, m)` admission inequality."*

Arithmetic defect in a pre-registered prediction:

```
beta=0.25, m=5:  d(sigma_max)/d(tau) = 1/(2*beta*(m-1)) = 1/2.000 = 0.5000
Record: 'predicted: 1/(2 beta (m-1)); at beta = 1/4, m = 5 this is 2'
=> the quoted value is the DENOMINATOR, not the derivative. True sensitivity is 4x SMALLER.
```

The error is conservative with respect to the record's conclusion (amortisation is an even weaker
lever than claimed), but a pre-registered number that is off by 4× is not admissible. Also
"the first term is `m!*N` independent of `B` and `m`" — `m!` is not independent of `m` (6, 24, 120,
720 at m = 3..6); the correct sentence is "independent of `B`". The rest checks out: the admission
inequality `σ < 1 − (1−τ)/(2β(m−1))` is algebraically consistent with the stated form, and
`T > (m!)² N` with `T ≤ N` is a valid impossibility.

### IDEA-20260808-726aa3 — two compensating exponent errors.

Direct known-answer check of the main term (count `m`-tuples in `H^m` on a codim-1 hypersurface;
`H ≤ F_p^*` of index `d`, `m = 3`):

```
p= 1009 d=2 B=  504: exact count=  127009 | B^m/p =   126882.1 | record's p^(m*beta+m-2) = 1.29e+11  (record/exact = 1.02e+06)
p= 4001 d=4 B= 1000: exact count=  251169 | B^m/p =  249937.5  | record's p^(m*beta+m-2) = 4.00e+12  (record/exact = 1.59e+07)
```

The correct main term is `B^m/p = p^{mβ−1}` (agrees to <1%); the record's stated `mβ + (m−2)` is
larger by exactly `p^{m−1}` (≈ `p²` at m=3, matching the measured ratios). Symmetrically the error
term omits the `1/d^m` normalisation, so the correct error is `~p^{(m−1)/2}`, not
`d^m·p^{(m−1)/2}`. The two errors cancel **exactly at the operating point β = 1/m**, so the
deliverable `γ > (m−1)/2` is unaffected — but the β-threshold is not:

```
m=3: record's beta-threshold 0.5000 vs correct 0.6667 (operating point 1/m = 0.3333)
m=5: record's beta-threshold 0.4000 vs correct 0.6000 (operating point 1/m = 0.2000)
```

The record understates the β-range in which Weil/Deligne fails. Fix the two exponents; the
conclusion and `γ(m) = (m−1)/2` stand.

### IDEA-20260808-63427b — the pre-registered pool factor mixes two dimensions.

```
M = 2^83.0;  ln M = 57.531
  N= 2048: sqrt(2 ln N) = 3.9050 ; sqrt(2 ln(2N/ln M)) = 2.9208 ; ratio = 1.3370
  N= 4096: sqrt(2 ln N) = 4.0787 ; sqrt(2 ln(2N/ln M)) = 3.1492 ; ratio = 1.2952
Record: 'at beta = 400, N = 2048 is 4.08/2.92 = 1.40'
  4.08 is sqrt(2 ln N) at N=4096; 2.92 is sqrt(2 ln(2N/ln M)) at N=2048.
ML-DSA N = 256(k+l+1): 44 -> 2304, 65 -> 3072, 87 -> 4096; 2048 is not a parameter set.
```

Self-consistent value is 1.30–1.34, ~8% below the pre-registered 1.40, and the quoted `N = 2048` is
not an ML-DSA dimension. The mechanism (sphere-concentration relaxation `√(2 ln N)` plus an
extreme-value pool term) is sound and both corrections are correctly signed; only the number is
wrong. Recompute at 2304 / 3072 / 4096.

### IDEA-20260808-8aaddb — the derived-not-measured detector has no power at its own known positive.

`HA-15` gives a chance rate `k²·10^{−d}`. The known positive is `cost_ratio = 0.011 = 1/397`, which
carries `d = 2` significant digits:

```
k= 5, d=2: expected chance matches = 0.250
k=10, d=2: expected chance matches = 1.000
k=20, d=2: expected chance matches = 4.000
```

So the documented known positive sits at or below the detector's own false-positive rate, and the
prediction "At least one flag (the 0.011 = 1/397 case … is a known positive)" cannot validate the
detector. The record's `MATCHED NULL` (reproduced `phi_alpha` values) is the right control, but the
positive control needs a value quoted to `d ≥ 4`, or the detector must be restricted to that
regime and its coverage at `d = 2` reported as zero. Otherwise the record is `NOVEL` and is the
best-screened instrument record in the slice: its `discriminated_from` correctly names both
same-round siblings (`IDEA-20260808-b3c97b` artifact-hash ladder, `IDEA-20260808-90c7ab`
post-archival edits) under their pre-allocation slice names, and I verified both are genuinely
different objects.

### IDEA-20260808-2df781 — the artifact tell is stated backwards.

Dyadic sets nest (`c/2^b = 2c/2^{b+1}`), so `R_a^min(b)` is **non-increasing**, with equality
possible — e.g. a target already exactly dyadic at denominator `2^b` gives `R_a^min = 0` at every
`b' ≥ b`. The record's tell reads "If `R_a^min` does not decrease as `b` increases, the optimisation
is mis-specified", which would condemn a correct solver on a tie. Correct tell: `R_a^min`
*increasing* in `b` ⇒ mis-specified. The rest is sound: the objective `Σ_z P(z)^a Q(z)^{1−a}` is
separable with one knapsack constraint, so the DP over partial sums is exact, and `2^b ≈ 2^{15..16}`
states with `Z+1 ≈ 13` items is trivial. Minor: "R_a is a convex function of P on the simplex" is
loose (Rényi divergence is quasi-convex in general for `a > 1`), but convexity is not load-bearing —
separability is.

### IDEA-20260808-71fea9 — same test as a same-round sibling.

`IDEA-20260808-8e13ff`'s gate tests T2 ("QUANTITATIVE FORM. The obstruction predicts a threshold,
exponent, or equality — not a direction") and T3 ("NEARBY-OBJECT DISSOLUTION … the inventor
protocol's null-control requirement, transposed from signals to closures") are, in substance and
almost in wording, 71fea9's (b2) and (b3). 8e13ff explicitly cites 71fea9 ("Slice record E3-11 asks
whether the round's closures share a root cause — a question about their CONTENT; this record asks
whether each individually deserves promotion — a question about their EVIDENCE"). 71fea9 does not
reciprocate. Required note: *"IDEA-20260808-8e13ff independently proposes the same two tests as a
promotion GATE for individual closures; this record uses them as a CLASSIFIER over the round's
closures to test H-ROOT. The tests are shared; the deliverables (a gate vs. a partition) differ,
and 8e13ff's own discrimination paragraph states this."*

Also, 71fea9's paraphrase of the "higher-dimensional-isogeny blocker … whose obstruction is an
EXTENSION DEGREE (~ord(π mod M))" is `IDEA-20260808-bba3dc`'s statement, not `40aab9`'s; 40aab9's
obstruction is a (refuted) rationality equality. The record's own confounder already flags that its
paraphrases are unverified, which is why this is a note rather than a defect.

---

## Records that survived checking

- **`f332da`** (Bleichenbacher, θ = 1/3). Every derived number reproduces: `s* = 42.04`,
  `t* = 45.79` vs balanced `42.67`; `N/(3(k+1))` = 10.7 / 14.2 / 21.3 bits at N = 160 / 256 / 384;
  `(850 GiB / 16 B)^{1/3} = 3854 = 2^{11.91}`. It records a hand computation that **contradicts its
  own stated P1 direction** and refuses to fix it quietly. It correctly places the pipeline on
  KN-TECH-057's charged side by argument (butterfly access pattern vs. vOW's amortised
  `O(p^{-1/6})` distinguished-point touches) rather than assumption, and HA-5's validation route
  measures the access rate rather than assuming it. Only note: the quoted step count `2^{47.7}`
  is the merge term alone; `t·2^t ≈ 2^{48.1}` is dropped (disclosed in
  `hidden_overhead_disclosure` item (iii)), so the headline `2^{61.9}` is ~1 bit low.
- **`90632c`** (ML-KEM Beta / CBD kurtosis). Verified by Monte Carlo at d = 512, 4×10⁵ draws:

  ```
  beta= 32: rho_sd(CBD)=0.8692   rho_sd(Gauss)=1.0002
  beta= 64: rho_sd(CBD)=0.8670   rho_sd(Gauss)=0.9989
  beta=128: rho_sd(CBD)=0.8660   rho_sd(Gauss)=0.9999    predicted sqrt(3/4)=0.8660
  E[R]_CBD matches beta/d to 4 decimals in every cell.
  ```
  CBD(2) moments confirmed exactly: `E[e²]=1`, `E[e⁴]=5/2`, `Var(e²)=3/2` vs Gaussian 2. The
  Gaussian null arm is correctly specified (removes non-Gaussianity, leaves the projector), which
  is the specific defect `RT-20260806-d008e0` found in the frozen design.
- **`dfd76a`** (SSI scope census). Its headline prediction is verified directly against
  `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`: the affected list at line 31 is CGL [14], the
  SQIsign family [7,19,20,22,34], GPS [28], PRISM [5], ⊗-MIKE [39]; the safe list is CSIDH [13],
  (qt-)Pegasis [17,18], M(D)-SIDH [25], FESTA [9], POKE [8]. Reference [6] (Basso et al.,
  "Supersingular Curves You Can Trust", EUROCRYPT 2023) is cited at line 193 for the mixing lemma
  and appears in **neither** list. The record's scope control ("run the identical census on the SAFE
  list; if any safe scheme comes back affected the instrument is wrong") is the right shape and
  respects KN-TECH-058's no-widening instruction.
- **`8aaddb`**, **`2df781`**, **`726aa3`**, **`63427b`** — novel in-corpus, with the specific
  corrections above.

---

## KN-TECH-057 / KN-FIND-720727 / KN-FIND-860118 adjudication

I confirmed the corpus defect: `KNOWLEDGE_BARRIERS.txt` renders `KN-FIND-006`, `-720727`,
`-860118`, `-a8990a` with empty titles and `KN-TECH-057` as the literal `>-`. (Same-round
`IDEA-20260808-3fdef7` documents this independently and correctly.)

- **KN-TECH-057** touches four records in my slice (`f332da`, `56e892`, `d873bc`, `287361`/`dfd76a`
  indirectly). Despite the blanked index entry, `f332da` and `56e892` both read the source file in
  full and both cite it accurately for the θ = 1/3 rule; `f332da` uses it correctly, `56e892`'s DG
  row does not (above). `d873bc` cites KN-TECH-035/-044 for a charge those records do not make
  (above) — this is the one place where the invisible index entry plausibly contributed. No record
  in my slice restates KN-TECH-057's content as new.
- **KN-FIND-720727** (ML-DSA formal proofs cover cryptographic adversaries only; fault injection is
  outside the model). `IDEA-20260808-63427b` is the only ML-DSA record in my slice; it is a norm-
  conversion / lattice-estimate record and makes no claim about the formal model or fault
  adversaries. No overlap, no restatement.
- **KN-FIND-860118** (the uncorroborated "standardized schemes are broken under quantum attack"
  claim in KN-LIT-1743, and the closed ML-KEM instantiation of arXiv:2605.17412v2).
  `IDEA-20260808-90632c` is the only ML-KEM record in my slice; it concerns the dispersion of a
  projected-error ratio and does not touch the determinant-ideal pipeline, PIP, or any break claim.
  No overlap. Note for the Coordinator: KN-FIND-860118's own correction — "graded cells localise
  the cause to the **q-ary modulus, not the rank**" — is directly relevant to any future ML-KEM
  structural proposal and is currently invisible to generators.

---

## What I actually checked

**Records read in full:** all 19 assigned `.yaml` files. Plus, in full or in substantial part:
`IDEA-20260808-812554`, `-bba3dc`, `-8e13ff`, `-19876e`, `-a3f7c1`, `-b8e2d4`, `-baf8bc`,
`-b6ba7a`, `-7c4e9d`, `-4f3ef4`, `-4854f8`, `-5d8b39`, `-b3c97b`, `-90c7ab`, `-3fdef7`;
`IDEA-20260807-406fef`, `IDEA-20260807-653dda`, `IDEA-20260801-020`.

**Corpus files:** `EXISTING_PROPOSALS.txt` (454), `EXISTING_HYPOTHESES.txt` (271),
`REJECTED_TITLES.txt` (367), `CATALOGUE_TITLES.txt` (262), `DEFERRED_TITLES.txt` (28),
`KNOWLEDGE_BARRIERS.txt` (150) — grepped per record for its own mechanism terms. Full title
listing of all 126 `IDEA-20260808-*` records generated and cross-read against my 19.

**Knowledge records read:** `knowledge/techniques/KN-TECH-057.md` (full),
`knowledge/techniques/KN-TECH-015.md` (full), `knowledge/techniques/KN-TECH-035.md` (complexity and
key lines), `knowledge/findings/KN-FIND-720727.md` (full), `knowledge/findings/KN-FIND-860118.md`
(full). Frozen source `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` lines 29–41, 193, 270.

**Computations run** (all outputs quoted above are real program output; nothing is estimated):

1. Elliptic-curve point counting + explicit group enumeration over `F_p`, `p ≤ 400`, to falsify
   `40aab9`'s iff and to measure `[E(F_p) : 2E(F_p)]` for `c5f9a2`.
2. Binomial arithmetic `C(B,m)` vs `B·C(B,m−1)` to expose `c5f9a2`'s `m!`/`(m−1)!` overcount.
3. `C(p,p/2)` vs `C(k+l−p,ε)` at all five Classic McEliece `(n,m,t)` triples for `a3bcf0`.
4. Monte-Carlo simulation of `e' = x·r₂ + r₁·y + e` in `F₂[X]/(X^n−1)`, 2×10⁵ draws, for `d21021`
   claim C-A.
5. From-scratch AES-128 validated against the FIPS-197 C.1 known-answer vector, then 1000 random
   round-function equivariance tests, 200 key-schedule tests, 1000 full-cipher tests, for `ddb522`.
6. Monte-Carlo of `R = ‖π_{d−β}e‖²/‖e‖²` for CBD(2) vs matched Gaussian at d = 512, 4×10⁵ draws,
   for `90632c` (confirms 0.866).
7. Plug-in conditional-entropy estimator under an exact independence null at N = 611 and N = 10⁴,
   q = 1..8, for `287361`.
8. Exact subgroup-sum counting `#{x+y+z = c : x,y,z ∈ H}` at p ∈ {1009, 2003, 4001} to check
   `726aa3`'s main-term exponent against `B^m/p`.
9. Closed-form evaluation of the θ-charged exponent rule `W·S^θ` against KN-TECH-035/-057's archived
   values for `56e892` and `d873bc`.
10. Sensitivity arithmetic `1/(2β(m−1))` for `f7e6e7`; `√(2 ln N)` / `√(2 ln(2N/ln M))` at
    N ∈ {2048, 2304, 3072, 4096} for `63427b`; `ω'·m/(m−1)` at ω' ∈ {2,4,6} for `e2315e`;
    `k²·10^{−d}` for `8aaddb`; `2|F|^m` vs `|F|²+|F|+2c` for `3f8a2b`; `f(b)` root-finding for
    `56e892`; `k+4s/3 = 4t/3` and `N/(3(k+1))` for `f332da`.

**What I could not verify, and what would settle it:**

- **All external novelty.** WebSearch/WebFetch unavailable. Specifically unadjudicated:
  superpolynomial-dimension Coppersmith (`e2315e`); Bernstein's generalized-birthday
  price-performance note and Dinur et al. dissection (`f332da`, which correctly names them as its
  own Stage-0 falsifier); Guo–Johansson ASIACRYPT 2020 (`d21021`, which correctly makes reading it
  Stage 0 and refuses to set `dominated_by: null`); Esser–Bellini's syndrome-decoding estimator
  (`a3bcf0`, whose claim (A) would be settled by one row of that table); ℓ∞-SIS literature
  (`63427b`); Burgess-type subgroup bounds (`726aa3`).
- **`56e892`'s `c(1/3) = 1.949616` and `β(1/3) = 0.835550`** come from `H-RSA-68884a`, which is
  `proposed` with unrun gates; I verified `c(0) = (64/9)^{1/3}`, `β(0) = (8/9)^{1/3}`, and that
  `2.243510 = c(0) + β(0)/3` exactly, but not the re-optimised pair. Reading `H-RSA-68884a`'s
  derivation would settle it.
- **`f332da`'s detection constraint `s ≥ 1.3028·2^k`** and `X1-02`'s `(k,s,t)` table are not in the
  committed snapshot under those names; Stage 1 cannot be reproduced without them.
- **`2df781`'s recalled `(Z, b)` for FrodoKEM** and the published Rényi order/value: the
  specification is behind the goal's shut source gate. The record correctly gates on it.
- **`d873bc`, `a3bcf0`** are blocked on primary specifications neither this program nor I have read.

---

## One concrete next action

Return `IDEA-20260808-c5f9a2` and `IDEA-20260808-40aab9` to their generators for withdrawal or
rewrite before either enters a batch: c5f9a2's entire claimed effect is an `m!`/`(m−1)!` overcount
that its own null object is required to reproduce, and 40aab9's headline if-and-only-if is falsified
by a five-line point count on a 53-element curve while a same-round sibling (`bba3dc`) already
states the correct criterion. Then have the Coordinator run one pass over the round for the
**pairs that were generated in parallel and cite each other in only one direction** —
(`f7e6e7`, `812554`), (`40aab9`, `bba3dc`), (`71fea9`, `8e13ff`), (`3f8a2b`, `7c4e9d`, `4f3ef4`) —
since in every case the *earlier-screened* record is the one missing the note, which means the
one-directional citation pattern, not the content, is the reliable detector.
