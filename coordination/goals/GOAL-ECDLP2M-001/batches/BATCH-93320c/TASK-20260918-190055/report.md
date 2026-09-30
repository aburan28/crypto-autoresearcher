# Red-team report: TASK-20260918-190055

Independent adversarial review of IDEA-20260918-6c07e1 and
IDEA-20260918-9abf42. Policy `review-adversarial`, `maximum_runs: 0`.
No sibling reports read. Producer is the dispatching Coordinator — treated as
aggravating (C-6).

Snapshot inputs read from committed ledger / frozen sources (see attestation).
Arithmetic below was derived **before** reading either proposal's
`baseline_reproduction` block (`blind_from_respected: true`).

---

## 1. IDEA-20260918-6c07e1 — verdict: **holds**

Core exclusion (E) holds under the normalisation the record itself flags in
(S4): `deg λ < 2^{n'}`, so `deg L = 2^{n'}`, and under F₂ coefficients and
exact complete splitting. No joint among J-1–J-5 **breaks** the congruence
argument. Soft scope defects on title wording and (S4) vs Definition 3.1 are
recorded as mandatory findings, not as a break of (E) as scoped by (S4).

### Joints (6c07e1)

| Joint | Verdict | Note |
| --- | --- | --- |
| J-1 Frobenius stability / orbit count | holds | See §1.1 |
| J-2 Residue set / ord₁₃₁(2) | holds | Blind recompute §4 |
| J-3 Proves-too-much (n'=130, (7,3), (31,15)) | holds | Finding F-1 |
| J-4 Scope (S1)/(S2)/(S4) | holds with narrowing | Findings F-2, F-3 |
| J-5 Second-hand citations | holds | Finding F-4; attributions confirmed |

### 1.1 J-1 edges

**(a) Multiplicity.** If “|V|” meant roots with multiplicity, a non-squarefree
L could have `|V|_mult = deg L` while fewer distinct roots. The record’s (C)
equates complete splitting with `L | X^{2^{131}} − X`. Over characteristic 2,
`X^{2^{131}} − X` is separable, so any divisor is squarefree: distinct-root
count equals degree. The identity `|V| = deg L` is the right one for (C).

Constructed edge (toy): L can have `gcd(L, L') ≠ 1` when λ' shares factors
with L, but such L cannot divide `X^{2^n} − X`. So multiplicity cannot rescue
a complete splitter inside the claim’s definition.

**(b) Empty V.** `a = 0, b = 0` gives `|V| = 0 ≠ 2^{n'}`. Exclusion still
holds. The argument nowhere requires V nonempty for the negative conclusion.

**(c) `a = 0` with `b > 0`.** Complete splitting would need `131 | 2^{n'}`,
impossible. Record correctly excludes residue 0.

**(S2) K-coefficients.** Concrete counterexample to `λ(x)² = λ(x²)`:
`λ = cX` with `c ∈ F_{2^{131}} \ F₂`. Then `λ(x)² = c² x²` while
`λ(x²) = c x²`, equal iff `c² = c`. Premise of (A) fails exactly as claimed.

---

## 2. IDEA-20260918-9abf42 — verdicts (split)

### COUNTING claim (theorem): **holds**

For odd prime `n`, exactly `2^f` Frobenius-stable F₂-subspaces with
`f = 1 + (n−1)/ord_n(2)`, dimensions the subset sums of irreducible factor
degrees of `T^n − 1` (equivalently `n` minus those sums — same set by
complementarity). At `n = 131`: exactly four, dimensions `{0,1,130,131}`.

| Joint | Verdict | Note |
| --- | --- | --- |
| J-5 Prop 2 attribution | holds | Finding F-4 |
| J-6 Counting theorem | holds | Blind factorisation §4; table rows n=23,43 match |
| J-8 Independence from 6c07e1 | holds | Different objects; see §2.3 |

### LADDER claim (design): **holds** (with mandatory prior-repair)

Rich/poor split by `ord_n(2)`, uncontrolled `ord_n(2)` in prior ladders, and
the `n = 7` A-vs-B cell are coherent. Curve orders 116 and 142 re-derived.
**Break in the preregistration’s citation path, not in the design:**
IDEA-20260906-a77711 does **not** say what 9abf42 cites it for. Finding F-5.

| Joint | Verdict | Note |
| --- | --- | --- |
| J-7 Ladder / equivariance prior | holds on design; **breaks** on a77711 attribution | Finding F-5 |

---

## 3. Mandatory findings (completion_gate)

### F-1. n' = 130 NON-EXCLUSION / proves-too-much — **PASSES**

Reconstructed argument: complete splitting ⇒ `2^{n'} ≡ a (mod n)` with
`a ∈ {1,2}` (residue 0 impossible).

| Object | Residue | In {1,2}? | Argument excludes? |
| --- | --- | --- | --- |
| n=131, n'=130 (Type 1bis) | `2^{130} ≡ 1 (mod 131)` | yes | **no** |
| (n,n')=(7,3), λ=X²+X | `2^3 ≡ 1 (mod 7)` | yes | **no** |
| (n,n')=(31,15) | `2^{15} ≡ 1 (mod 31)` | yes | **no** |

Family sweep: Type 1bis has `n' = n−1`; for odd prime `n`, Fermat gives
`2^{n−1} ≡ 1 (mod n)` — always permitted. Type 2 Mersenne examples in the
program’s records sit at residues 1. **No published complete splitter checked
here is excluded.** Failure signature ABSENT.

For 9abf42 at n=31: formula gives `f=7`, 128 subspaces, dimension lattice
5-spaced — the record does **not** claim useful stable bases are nonexistent
in general; reading it that way would prove too much, and the record’s own
nearby-object control already forbids that reading. PASSES.

### F-2. Lemma C.2 / approximate-regime scope limit — **REAL; record does not quietly claim it**

**(Half A — regime free.)** Legal Frobenius-stable cardinalities are
`|V| = a + 131b`, `a ∈ {0,1,2}`. For target `T = 2^{n'}`, the nearest legal
value is always within absolute distance ≤ 64 of `T` (residues only need to
hit `{0,1,2}` mod 131). Relative gap → 0 as `n'` grows. Examples:

- n'=33: gap 28, relative ~3·10⁻⁹
- n'=66: gap 2
- n'=129: gap 64

So `|V| ≈ 2^{n'}` is always compatible with the orbit count. (S1) is correct:
the congruence does **not** close the approximate regime.

**(Half B — no quiet overclaim.)** Claim (E), title’s exclusion, predictions,
and falsification_route all restrict to exact `|V| = 2^{n'}`. why_it_matters
and interpretation_limits repeat that the QSP line stays open on approximate
splitting. **No sentence was found that extends (E) to Lemma C.2’s regime.**

Citation hygiene (non-breaking): Lemma C.2 of Huang (KN-LIT-0a321c) is a
**degree lower bound** when L splits almost completely
(`⌊n/n'⌋ ℓ + (n mod n') ≥ log_q |V|`), not the definition of the approximate
regime. The regime itself is named in Euler–Petit Definition 2
(“approximately p^{n'} roots”). (S1)’s math is right; the Lemma C.2 pointer
is the bound that *applies in* that regime, which is acceptable if read that
way.

### F-3. Normalisation (S4) vs KN-LIT-0a321c Definition 3.1 — **resolved**

Frozen text (Huang `paper_fulltext.md` ~628–634):

> Definition 3.1. … we call polynomials `X^{q^{n'}} − λ(X) ∈ K[X]` dividing
> `X^{q^n} − X` with `log_q(d) = log_q(deg(λ)) < n'²/n` quasi-subfield
> polynomials.

**Definition 3.1 does not explicitly require `deg λ < q^{n'}`.** It requires
divisibility and the quality bound on `log_q(deg λ)`.

Implicit usage elsewhere: Lemma 4.1’s setup writes “so that `|V| = q^{n'}`”
when L splits, which forces `deg L = q^{n'}` and hence (absent leading-term
cancellation) `deg λ < q^{n'}`. Euler–Petit Definition 2 likewise writes the
form `L := X^{p^{n'}} − λ(X)` with quality `β ≤ 1`.

**Scope IDEA-20260918-6c07e1 retains:** claim (E) only under
`deg λ < 2^{n'}` (as (S4) already hedges). If `deg λ ≥ 2^{n'}`, then
`deg L = deg λ` and complete splitting demands `deg λ ≡ a (mod 131)`,
`a ∈ {1,2}` — a different, much weaker constraint that does **not** exclude
n' ∈ [2,129].

**Title defect (not a break of (E) under S4):** “WITH NO DEGREE BOUND” and
“WHATEVER deg λ IS” overclaim relative to (S4) and relative to Definition 3.1.
Honest restatement: no *census* degree bound (3..7) — the shape still needs
`deg λ < 2^{n'}`. Coordinator prior P-4 (0.45) loses, as predicted.

### F-4. Second-hand attributions — **CONFIRMED** (with quantifier notes)

#### Proposition 2 of Euler–Petit (KN-LIT-4fe9d2)

Frozen text (`inputs/EULER-PETIT-2019-QSP/paper_fulltext.md` ~374–383):

> Proposition 2. Let `f = a₀ + a₁X + ··· + X^d ∈ F_p[X]`. Then the following
> properties are equivalent.
> 1. `L_f(X)` splits completely over `F_{p^n}[X]`
> 2. `L_f(X)` divides `X^{p^n} − X`
> 3. `f` divides `X^n − 1`

| Check | Outcome |
| --- | --- |
| Direction | **IFF** (three-way equivalence) — proposals’ “exactly when” / “iff” correct |
| Quantifiers | `f ∈ F_p[X]` — F_p-coefficient linearized `L_f` only; **not** non-linearized λ |
| Distinct roots | Implied by (2): divisor of separable `X^{p^n}−X` |
| p=2 specialisation | `T^n−1` / `X^n−1` — fine |

Both proposals’ attributions match. Prop 2 does **not** by itself classify
non-linearized QSPs — 6c07e1 correctly treats that as a separate congruence
argument.

Type 1bis at n'=n−1 is in Proposition 5 of the same paper (~1798–1829),
consistent with the baseline reproduction.

#### “Splits completely” / Definition 3.1 (Huang)

Frozen Definition 3.1 (above) builds complete splitting (`L | X^{q^n}−X`)
into the QSP definition, plus quality. Euler–Petit Definition 2 (~165–179)
explicitly allows “splits completely **(or at least has approximately
p^{n'} roots)**”. 6c07e1’s use of exact splitting as `|V| = deg L` with
distinct roots matches both sources’ exact branch.

### F-5. Equivariance prior misstatement (J-7) — **LADDER citation breaks**

IDEA-20260918-9abf42 cites IDEA-20260906-a77711 as implying:

> Frobenius carries a decomposition of a target R to a decomposition of
> σ(R), so for a FIXED target the descended system is not T-equivariant
> … [hence] NO DIFFERENCE BETWEEN ARMS A AND B in first-fall degree.

What a77711 actually states (Lemma A1 / Prediction A):

- `σ(I_R) = I_{R^π}` — equivariance **between conjugate targets**, for a
  **π-stable** V.
- Prediction A: invariant-ring rewriting of the **orbit system** `I_orb`
  does not lower solving degree vs plain `I_R`.
- Constant-factor gains when V is stable: n relations / n fewer unknowns.

That is **not** a theorem that a stable dim-4 factor base and a random
dim-4 factor base have equal first-fall degree. Bridging A-vs-B fall-degree
equality requires an extra lemma 9abf42 does not supply. Misquoting a prior
into a preregistration is exactly the corruption J-7’s attack plan names.

**Repair before any contract:** keep the null A-vs-B prediction if desired
(it is still a coherent prior), but cite it as a **new** preregistered guess,
not as a corollary of a77711 Lemma A1. Optionally add a bridging obligation.

**Design half still holds:** n=7 admits stable dim 4 (degrees `{1,3,3}` →
dims include 4); m=2 with `2·4 ≥ 7` is admissible; arms A/B are size-matched
at fixed n (field-size confound affects the multi-n rich/poor ladder, not the
single n=7 cell); orders `#E₀(F_{2^7}) = 116 = 4·29` and
`#E₁ = 142 = 2·71` re-derived from the Koblitz trace recursion match the
record.

### F-6. Blind re-derivation arithmetic — **AGREES** with both records

**(i) `S = {n' ∈ [1,131] : 2^{n'} mod 131 ∈ {1,2}}`**

Independent computation:

- `2^{10} ≡ 107`, `2^{26} ≡ 53`, `2^{65} ≡ 130 ≡ −1`, `2^{130} ≡ 1`,
  `2^{131} ≡ 2` (mod 131).
- Maximal proper divisors of 130 = 2·5·13 all fail ⇒ `ord_131(2) = 130`.
- Full enumeration of n' ∈ [1,131]: **`S = {1, 130, 131}`** only.

Agrees with IDEA-20260918-6c07e1.

**(ii) n=23 and n=43 stable-subspace counts**

Independent factorisation of `T^n − 1` over F₂:

| n | ord_n(2) | f | #subspaces | factor degrees | dimension set |
| --- | --- | --- | --- | --- | --- |
| 23 | 11 | 3 | **8** | {1,11,11} | {0,1,11,12,22,23} |
| 43 | 14 | 4 | **16** | {1,14,14,14} | {0,1,14,15,28,29,42,43} |

Agrees with IDEA-20260918-9abf42’s table. Note: `#` distinct dimensions can be
`< 2^f` when equal-degree irreducibles repeat; the record correctly lists
8 (resp. 16) **subspaces** and the compressed dimension **set**. Exactness
of `2^f` is on the subspace count (bijection with squarefree divisors), not
on the cardinality of the dimension set.

`dim(g) = n − deg g` vs “dimensions = subset sums of factor degrees”: both
conventions yield the **same set** by complementarity. Mild wording conflation;
answers correct. (H-FROB-d93575’s `dim ker g(π) = deg g` is the dual labelling.)

---

## 4. J-8 — two proposals or one fact twice?

**Genuinely two routes; not one fact counted twice** (prior P-7 loses).

- 6c07e1 quantifies over **root sets** of (possibly non-linearized)
  F₂-polynomials: Frobenius-stable as **sets** (unions of orbits), not as
  subspaces. Exclusion uses `|V| ≡ a (mod 131)` vs `2^{n'}`.
- 9abf42 quantifies over **F₂-subspaces** closed under Frobenius: ideals of
  `F₂[T]/(T^n−1)`.

For **linearized** L, the root set is a subspace, so at n=131 the counting
theorem already forbids useful n' ∈ [2,129] for F₂-coefficient linearized
QSPs — recovering Prop 2. For **non-linearized** λ, the root set need not be
a subspace (Type-2 `X^8+X²+X` over F_{2^7} has 8 roots forming a subspace;
non-linearized shapes need not). 6c07e1’s exclusion of non-linearized exact
splitters is **not** a corollary of 9abf42.

Shared arithmetic input `ord_131(2)=130` is expected and not a collapse.

**Novelty note on 9abf42 (iii):** calling the module correspondence a
“re-derivation” of Prop 2 is mathematically fair (same classification). It is
also the classical proof path; a77711 already states the primitive-root case
(“0, F_q, trace-zero, everything”). Novelty (ii) at n=131 is largely prior in
a77711; novelty (i) closed form and (iv) ladder confound remain the usable
additions. Prior P-6’s skepticism is justified for (iii) as *novelty*, not for
correctness.

---

## 5. Self-review hazard (C-6)

The review_plan’s joints and proves-too-much objects are aimed at the real
weak points (arithmetic slip, n'=130, S4 normalisation, second-hand
citations, a77711 misquote). That is not self-serving framing.

Residual hazard: **one reviewer owns all eight joints**
(`single_reviewer_disclosure`), so agreement is one agent’s taste, not
cross-joint independence. Accepted only because C-7 forbids status change on
this verdict. If either proposal is promoted, a multi-reviewer round is
mandatory; this report does not substitute.

Coordinator-as-producer did not soft-ball the controls: P-4 and P-6 were
pre-registered as likely losses, and both landed as predicted (S4 title
overclaim; re-derivation novelty thin). The a77711 misstatement (F-5) is an
**additional** break the plan’s J-7 attack anticipated and that the producer’s
prior underweighted.

---

## 6. Narrowest supported statements

**On 6c07e1:** For every n' ∈ [2,129] and every `λ ∈ F₂[X]` with
`deg λ < 2^{n'}`, the polynomial `X^{2^{n'}} + λ(X)` does not split
completely over `F_{2^{131}}`. Approximate splitting, K-coefficients,
non-root-set factor bases, and `deg λ ≥ 2^{n'}` are untouched.

**On 9abf42 (counting):** For every odd prime n, `#` of Frobenius-stable
F₂-subspaces of `F_{2^n}` equals `2^{1+(n−1)/ord_n(2)}`, with dimensions as
above; at n=131 exactly `{0,1,130,131}`.

**On 9abf42 (ladder):** Toy FROB ladders should stratify on `ord_n(2)`; the
n=7 stable-vs-random dim-4 cell is an admissible discriminator. Do not cite
a77711 as proving A-vs-B fall-degree equality until a bridging lemma exists.

**Neither verdict promotes, extends DEC-20260917-793ae2, or closes a line
(C-7).**

---

## 7. Next concrete action (for Coordinator; not performed here)

1. Compose this report into a decision: if citing 6c07e1, supersede or amend
   title/claim wording to drop “no degree bound” / “whatever deg λ” in favour
   of explicit `deg λ < 2^{n'}`.
2. Before any FROB contract from 9abf42: repair the a77711 citation in a
   superseding proposal or in the contract’s `preregistered_prediction` block.
3. Promotion of either derivation, if ever sought, requires
   `review-breakthrough` multi-reviewer ownership — this round does not
   qualify.

---

## 8. review_attestation

```yaml
review_attestation:
  task_id: TASK-20260918-190055
  independent_session: true
  requested_policy: review-adversarial
  reasoning_effort: xhigh
  joints_owned:
    - J-1
    - J-2
    - J-3
    - J-4
    - J-5
    - J-6
    - J-7
    - J-8
  sources_read:
    - ledger/handoffs/TASK-20260918-190055.yaml
    - agents/red-team.md
    - AGENTS.md
    - ledger/proposals/IDEA-20260918-6c07e1.yaml
    - ledger/proposals/IDEA-20260918-9abf42.yaml
    - ledger/decisions/DEC-20260918-7e0865.yaml
    - ledger/decisions/DEC-20260917-793ae2.yaml
    - ledger/questions/RQ-QSP-f9bbdb.yaml
    - ledger/questions/RQ-FROB-7d8dd4.yaml
    - inputs/EULER-PETIT-2019-QSP/paper_fulltext.md
    - inputs/HUANG-2020-JMC-QSP/paper_fulltext.md
    - knowledge/literature/KN-LIT-4fe9d2.md
    - knowledge/literature/KN-LIT-0a321c.md
    - ledger/proposals/IDEA-20260906-a77711.yaml
    - ledger/hypotheses/H-FROB-d93575.yaml
    - templates/research-records.md
  sources_not_read:
    - coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/report.md
    - experiments/EXP-SEMBIN-4fa22c/specification.yaml
    - experiments/EXP-QSP-33b442/analysis.md
    - full body of DEC-20260917-793ae2 beyond the opening decision_scope
    - full body of DEC-20260918-7e0865 beyond activation/context/actions
  read_sibling_reports: false
  blind_from_respected: true
  blind_from_note: >-
    Quantities (i) S and (ii) n=23,43 subspace counts/dimensions were computed
    and written down before reading either proposal's baseline_reproduction
    block; those blocks were read only after independent values were fixed.
  verdicts:
    IDEA-20260918-6c07e1: holds
    IDEA-20260918-9abf42_counting: holds
    IDEA-20260918-9abf42_ladder: holds
  verdict_notes: >-
    Ladder design holds; ladder's a77711 attribution for the A-vs-B
    preregistration breaks (F-5) and must be repaired before contract use.
    No joint breaks the counting theorem or the 6c07e1 congruence under S4.
```
