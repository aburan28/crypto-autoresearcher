# BLIND READ — joint J-4: what Semaev 2015/310's ARGUMENT delivers, against what his STATEMENT claims

- **Task**: `TASK-20260916-64a93b`
- **Role**: Validator, independent session, blind read
- **Batch**: `BATCH-e0a0c1` of `GOAL-SEMBIN-fcb7a2`
- **Subject**: Igor Semaev, *New algorithm for the discrete logarithm problem on
  elliptic curves*, IACR ePrint 2015/310, revision of 2015-04-10, frozen at
  `inputs/SEMAEV-2015-310/eprint-2015-310.pdf`
- **Runs**: 0. **Measurements**: 0. One labelled symbolic hand-check
  (`recheck.py`, 53 assertions, 0 failures) in this task directory.
- **Written**: 2026-09-21

Line references of the form `:NNN` are lines of
`inputs/SEMAEV-2015-310/paper_fulltext.md` unless another file is named.
Every formula relied on below was reassembled from PDF glyph coordinates first,
and the sha256 of both frozen Semaev artifacts (and both Nagao ones) verifies
against its sidecar; see `reextract.md`.

---

## Summary of the four verdicts

| sub-joint | verdict | one line |
|---|---|---|
| J-4a | **answered, with a recorded ambiguity** | The campaign consumes Semaev's §4.5 **first fall degree** result — the number 4 — reached through Nagao's Proposition 2/5. No record of this campaign cites 2015/310 at all; the statement is identified only by paraphrase inside a `mechanism` field. |
| J-4b | **answered** | The argument proves the fake first fall degree of the **non-terminal** links is exactly 4, with a **uniform** witness. Everything else — the terminal equation, the fake→true conversion, the field→descent transfer, and d_F4 itself — is experiment, omission, or declared assumption. |
| J-4c | **gap found; three distinguishable components** | The gap is primarily **quantity** (fake vs true degree; d_ff vs d_F4), secondarily **coverage** (t = 2 gets nothing), and thirdly **quantifier** (universal statement, typical-instance evidence, 20× below the parameters of the headline). |
| J-5 | **CONTROL FAILS: the argument survives its own known-false object** | At `k > ⌈n/m⌉` Semaev reports d_F4 > 4 — and the argument for `d_F4 ≤ 4` runs there unchanged, because its only algebraic input has no `k` in it. Verified mechanically over two fields, every `k = 1..n`, random subspaces, mixed shapes, and coset shifts. |

---

## J-4a — Which statement of 2015/310 does this program consume, and how did I determine that?

### What I read, in order

1. `inputs/SEMAEV-2015-310/source_record.yaml` — the program's own record of
   what it froze and why.
2. `ledger/hypotheses/H-SEMBIN-a7e721.yaml` — the hypothesis this batch serves.
3. `experiments/EXP-SEMBIN-4fa22c/specification.yaml` — its frozen contract.
4. `inputs/NAGAO-2015-984/paper_fulltext.md` — the intermediary, because the
   campaign's object is Nagao's Proposition 5 and not Semaev's paper directly.

### The answer

**The statement this campaign consumes is Semaev's §4.5 first-fall-degree
result — "the first fall degree is 4" for the descended chained S₃ system — and
it consumes it *through Nagao*, not directly.**

The determining evidence is `H-SEMBIN-a7e721`'s `mechanism`, LINK 1:

> "The numerical bound originates as **Semaev's estimate of the FAKE first fall
> degree for summation-polynomial descents**, not as a statement about the true
> degree. It is imported rather than proved in 2015/984."

and Nagao's own attribution, which confirms the route:

- `inputs/NAGAO-2015-984/paper_fulltext.md` :587-600 — "**Proposition 2 (Semaev
  [14] and its generalization to p ≥ 3).** First fall degree of EQS2(m,R) is
  bounded by 4 (p = 2), 3p+1 (p ≥ 3)."
- ibid. :719-729 and :844 — Proposition 5 restates the same bound for EQS4 with
  footnote 6: "**The situation is the same as the Semaev's case. So, we omit the
  proof.**"

Nagao's [14] is 2015/310 (ibid. :956-960). So the "4" that Proposition 5 asserts
for the coset-shifted EQS4 systems is Semaev's §4.5 number, carried across two
steps whose proofs Nagao omits.

Three things fix it as the **first-fall-degree** statement and not one of
2015/310's other consumable claims:

- Nagao's Propositions 2 and 5 are *first fall degree* statements, not
  regularity-degree statements. Assumption 1 of 2015/310 (:602-605) is about
  `d_F4`, a different quantity, so it is not what Nagao imports.
- §4.3's success-probability model, eq. (11) (:394-431), is consumed by this
  program — but by **other** goals. `source_record.yaml` `scope_of_assessment`
  records it as `HEUR-SEMAEV-2015-4.3` in `EXP-RELN-164ad3`, `H-RELN-cfa1a2`,
  `H-RELN-96e3ba`, `GOAL-RELN-001`, `GOAL-ICEX-001`. Not this campaign.
- `inputs/SEMAEV-2015-310/provenance.json` `session_note` records a third,
  separate consumption: `GOAL-DREG-001` "measuring its Assumption 1 quantity".
  Also not this campaign.

### The ambiguity, reported rather than resolved

The card instructed that if the program's own records are ambiguous about which
statement it depends on, that ambiguity is itself the finding. **They are, in
two ways.**

**(1) No record of this campaign cites 2015/310.** `H-SEMBIN-a7e721`'s
`citations` block carries five entries — `DEC-20260916-88ac73`,
`CORR-20260916-96f47d`, `NAGAO-2015-984`, `NAGAO-2013-549`, `H-SEMBIN-c59e50`.
2015/310 is not among them. `EXP-SEMBIN-4fa22c`'s `citations` block carries four
entries and 2015/310 is not among them either; its `dependencies` (:429-441)
name only `inputs/NAGAO-2015-984/paper_fulltext.md`. So the consumed Semaev
statement exists in this campaign's records **only as prose inside a `mechanism`
field**, with no section, equation, page, or line anchor, and no provenance
marking. A reviewer cannot check it against the source without doing what this
task did.

**(2) Within §4.5 there are three candidate statements and they are not the same
claim.** The paraphrase "Semaev's estimate of the FAKE first fall degree" does
not pick between:

- **S-A** (:97, Introduction): "The first fall degree is **proved** to be 4."
  System-level, asserted as proved.
- **S-B** (:598-599, §4.5 body): "Anyway **at least t − 2 of the equations** in
  (5) have the first fall degree 4."  Per-equation, and explicitly partial.
- **S-C** (:602-605, Assumption 1): `d_F4 ≤ 4`.  A different quantity, and
  labelled an assumption.

S-A and S-B differ materially: S-B excludes the terminal equation and, at
t = 2, excludes every equation in the system (see J-4b). Nagao's Proposition 2
is a system-level statement, so what Nagao imports reads as S-A; what Semaev's
body actually asserts is S-B. **I do not resolve which one the campaign means.
The campaign's records do not say.**

One further characterisation point, recorded because it cuts both ways. LINK 1
calls Semaev's quantity the **fake** first fall degree. That is right about
Semaev's *computation* and wrong about Semaev's *definition* — and Nagao says so
in terms at `inputs/NAGAO-2015-984/paper_fulltext.md` :452-459: "In [14], Semaev
says … Considering xuS3(x, u, RX), one can easily have the relation that its Fake
first fall degree d′_F ≤ 4. **He uses the true definition of first fall degree.**"
LINK 1 therefore understates the paper in one direction (Semaev states it under
the true definition and calls it "proved", not "estimated") while correctly
identifying what the argument computes. Details in J-4b/J-4c.

---

## J-4b — What does the argument actually establish?

### The argument, in full

It is six sentences, §4.5 :561-600 (PDF p.10). Reassembled from glyph
coordinates (`reextract.md` F-1):

> We consider the case m = 2 in more detail now. First we take the polynomial
> (14), where all x₁, x₂, x₃ are variables **in V or F₂ⁿ**. Following an idea in
> [19] it is easy to prove that the first fall degree is 4 in this case. Really,
> coordinate Boolean functions which represent S₃(x₁,x₂,x₃) are of total degree
> 3. We denote that fact `deg_{F2} S₃(x₁,x₂,x₃) = 3`. However
> `deg_{F2} x₁S₃(x₁,x₂,x₃) = 3` again because
> `x₁S₃ = x₁³x₂² + x₁³x₃² + x₁x₂²x₃² + x₁²x₂x₃ + Bx₁`
> despite `deg_{F2} x₁ + deg_{F2} S₃ = 4`.

("the case m = 2" is not a typo for p = 2; it refers back to `S_{m+1}` of the
preceding sentence, which at m = 2 is S₃. See `reextract.md`, reading hazard 1.)

### What is PROVED

**B-1. The exhibited fall is correct, and the fall degree is exactly 4 — for the
non-terminal links.** Verified independently in `recheck.py` over F₂⁵, F₂⁷, F₂⁹
(RC-1a–e): `deg_{F2} S₃ = 3`, `deg_{F2} x₁S₃ = 3 < 1 + 3 = 4`, the product is
nonzero, and the printed expansion is an exact identity of descended Boolean
systems. Semaev argues only the `≤` direction. RC-1i supplies the missing lower
bound: the degree-3 parts of the n coordinate polynomials of S₃ are
F₂-linearly independent (rank = n for n = 5, 7, 9), so no constant-multiplier
combination falls at degree 3, and the fake first fall degree of that subsystem
alone is **exactly 4**, not merely at most 4.

**B-2. The witness is uniform, and that is the argument's real strength.** The
multiplier is literally the same object — the variable x₁ — in every instance.
The quantifier order is the strongest available: *for all n, for all V, for all
B, for all non-terminal links, there exists a fall at degree 4, exhibited by one
fixed witness.* This is not a per-instance witness dressed up as a uniform one.
`recheck.py` RC-2 confirms the uniformity across `k = 1..n`, across random
(non-polynomial) subspaces, across the mixed field/subspace shape of system (5),
and — RC-2g — across nonzero coset shifts.

**B-3. Consequently, for t ≥ 3, the descended system (5) has fake first fall
degree ≤ 4.** A fall in a subsystem is a fall in the system; take the other
multipliers zero.

### What is ASSERTED, EXPERIMENTAL, or OMITTED

**B-4. The terminal equation is experimental, not proved.** :591-599:

> "This argument **does not work** for S₃(x₁,x₂,z), where z is a constant from
> F₂ⁿ. … The first fall degree for such polynomials was bounded by **5** in [11].
> **The experiments show it is always 4 again.**"

Confirmed mechanically (RC-1f/g/h): with z constant, `deg_{F2} S₃(x,u,z) = 2`,
`deg_{F2} x·S₃ = 3`, and the bound is `1 + 2 = 3`, so there is no fall. The
argument genuinely stops here, and Semaev says so. **That refusal is a positive
control on the argument**: it discriminates the case it can prove from the case
it cannot, which is the behaviour a sound argument should have.

Two further observations, both from RC-3:

- The gap is **closable by the paper's own method**, with a multiplier the paper
  does not give. Degree-2 field monomials `u³`, `x·u²`, `x²·u` and `x³` all
  produce a fall at degree 4 on S₃(x,u,z) (`deg(m·S₃) = 3 < 2 + 2 = 4`). No
  degree-1 monomial multiplier falls below 4 (RC-3g). So the terminal equation's
  fake first fall degree is ≤ 4 and this is one line of algebra away from what
  Semaev wrote.
- **The multiplier Nagao attributes to Semaev does not work.** Nagao
  (`NAGAO-2015-984` :452-459) writes "Considering xuS3(x, u, RX), one can easily
  have the relation that its Fake first fall degree d′_F ≤ 4." For `m = x·u`,
  `deg_{F2}(m·S₃) = 4`, which equals the bound `2 + 2 = 4`: **no fall** (RC-3a).
  The obstruction is the term `x³u³`, whose Boolean degree is `wt(3) + wt(3) = 4`.
  A looser reading of Nagao's sentence — "degree-2 multipliers give a fall at 4"
  — is TRUE, via `xu²`; the literal single-product reading is not. This is a
  statement about Nagao's text and is flagged, not adjudicated: that paper's
  joints are not mine.

**B-5. The transfer from field level to descended system is asserted, not
stated.** Semaev computes `deg_{F2}` of *field* polynomials and multiplies by a
*field* element x₁. To convert that into a first fall of the *descended Boolean
system*, one needs each coordinate of x₁S₃ to be a combination
`Σ_i (Boolean multiplier of degree deg_{F2} x₁) × (coordinate of S₃)`. That is
Nagao's Lemma 5 (`NAGAO-2015-984` :521-538), attributed there to Nagao [11].
2015/310 states no such lemma and does not flag the step. The step is true; it
is simply not in this paper.

**B-6. The fake → true conversion is absent.** §4.4's definition (:505-518),
reassembled from glyphs (`reextract.md` F-2), reads

> `max_i(deg g_i + deg f_i) = d_ff`, `deg(Σ_i g_i f_i) < d_ff`, `Σ_i g_i f_i ≠ 0`

stated for the system (12) = {f₁,…,f_m} over a field K, with **no field
equations and no reduction modulo them** — i.e. the *true* first fall degree in
Nagao's taxonomy (Definition 5, `NAGAO-2015-984` :398-410). But §4.5 computes
`deg_{F2}`, "the total degree of the coordinate Boolean functions", which are
multilinear by construction — i.e. the *fake* degree (Nagao Definition 6, ibid.
:430-448). **The paper's stated definition and the paper's computation are
different quantities and the paper does not remark on the difference.** Nagao
notices it ("He uses the true definition of first fall degree") and repairs it
with Lemma 4, `d_F ≤ d′_F` (ibid. :510-515), which he obtains from Lemma 3 of
[11] and of which he says "Proof of this Lemma is complicated and not
constructive." **The repair is not in 2015/310.**

(A second, quieter definitional difference, recovered from the PDF and recorded
in `reextract.md` F-2: Semaev's condition is `max_i(deg g_i + deg f_i)`, a *sum
of degrees*, with *equality*; Nagao's Definition 5 is `max_i{deg g_i f_i}`, the
*degree of the product*, with `≥`. In the multilinear ring these can differ.
Generically at the descended level they coincide, so it does not bite on the
argument as given — but a consumer comparing the two papers' numbers should know
they are comparing two formally different definitions.)

**B-7. The step from d_ff to d_F4 is a declared assumption, and Semaev says it
is not generally true.** :518-522:

> "A first fall degree assumption says `d_F4 ≤ d_ff` … **Although not generally
> correct**, the assumption appears correct for the polynomial systems coming
> from (4) and was supported by extensive experiments for relatively small
> parameters in [19, 28]. This is **very likely** correct for (5) as well."

Note also that the two sides are computed on different generating sets:
`d_ff` per the §4.4 definition is over the descents alone, while the `d_F4`
experiments explicitly add the field equations — ":612-613 … n(t−2)+kt field
equations are added." Adding generators can only lower a first fall degree, so
the bound still transfers; recorded because it means the assumption is never
instantiated on one fixed system anywhere in the paper.

**B-8. Assumption 1's universality rests on experiment, and on a stated
"very likely".** Assumption 1 (:602-605) quantifies over all n, all
`2 ≤ m < n`, **any** subspace V of dimension `k = ⌈n/m⌉`, and all `2 ≤ t ≤ m`.
It quantifies over the curve parameter B and over R_X **not at all** — those do
not appear in the statement. The evidence (§4.5.1, Tables 1–2) is 2300 systems
at `n ≤ 21` with a single cell at `n = 40`, `m ≤ 6`, one B per table, and 100
random z per row. The paper's own transition sentence, confirmed verbatim in the
PDF (`reextract.md` F-5, :752-759):

> "We conclude that for all values of n, m and t ≤ m **in the tables**
> Assumption 1 was correct **for randomly chosen z ∈ F₂ⁿ**. So the assumption is
> **very likely to be correct for any values of n, m, t ≤ m**."

### The strongest claim the argument supports

> For every n, every GF(2)-subspace (or coset of one) V ⊆ F₂ⁿ, every curve
> parameter B, and every t ≥ 3, the descended Boolean system of (5) has **fake**
> first fall degree at most 4, exhibited by a single uniform witness; and for the
> non-terminal links taken alone that value is exactly 4.
>
> At t = 2 the argument supports nothing. The **true** first fall degree, and the
> regularity degree `d_F4` that the complexity claim actually needs, are reached
> only by a conversion the paper does not perform (B-6) and an assumption the
> paper says is not generally correct (B-7), evidenced at parameters roughly 20×
> below the ones the FIPS conclusion is drawn at (B-8).

Notice what is **absent** from that sentence: `k`. That absence is J-5.

---

## J-4c — Is there a gap between statement and argument?

**Yes.** It has three components, and they are not the same kind of gap. A
consumer relies on a different side of each.

### GAP-1 — QUANTITY. The heaviest one.

- **Statement** (:97): "The first fall degree is **proved** to be 4", under a
  definition (§4.4) that is the **true** one.
  **Statement** (:602-605, Assumption 1): `d_F4 ≤ 4`.
- **Argument**: the **fake** first fall degree, of a **subset** of the equations.

Two conversions separate them and neither is in this paper: fake → true (B-6,
Nagao's Lemma 4, "complicated and not constructive") and d_ff → d_F4 (B-7, an
assumption Semaev states is "not generally correct").

**Which side must a consumer rely on?** It depends on what the consumer wants:

- A consumer who wants a bound on the **fake** first fall degree of the descended
  chained system may rely on the **argument**. It is sound, uniform, and
  verified here (B-1, B-2). This is the better side, and it is the side the
  hypothesis `H-SEMBIN-a7e721` names in LINK 1.
- A consumer who wants `d_F4 ≤ 4` — which is what every complexity statement in
  the paper, and the FIPS conclusion at :122-124 and :381-384, actually needs —
  must rely on the **statement**, which the argument does not reach. The bridge
  is Assumption 1, and Assumption 1 is an assumption.

### GAP-2 — COVERAGE. The sharpest one, because it is exact.

`:598-599`: "Anyway at least **t − 2** of the equations in (5) have the first
fall degree 4." System (5) has **t − 1** equations (:232-238). So one equation —
the terminal `S₃(u_{t−2}, x_t, R_X)` — is outside the argument at every t.

And at **t = 2**, `t − 2 = 0`: the sentence covers **zero** equations, while
`:240` states "For t = 2 the system consists of only one equation
S₃(x₁,x₂,R_X) = 0". Assumption 1's range is `2 ≤ t ≤ m` and therefore
**includes t = 2** (RC-5a/b/c). At t = 2 the paper's argument for Assumption 1
is empty and the support is entirely experimental — six rows of Table 2, at
(n,m) = (15,4), (15,5), (16,4), (19,3), (21,3), (40,2) (RC-5d).

A consumer taking the "4" at t = 2, or for the terminal link at any t, is
relying on the **statement** and on the paper's experiments, not on any
argument. (RC-3 shows the gap is closable — but by the consumer, not by the
paper.)

### GAP-3 — QUANTIFIER. Disclosed by the paper, but not in the Introduction.

Three slides happen in the sentence at :755-759, and the paper marks the result
"very likely":

1. **typical z → all z.** The experiments sample 100 random `z` per row.
   Assumption 1 has **no quantifier over z or R_X at all**. "For a random z the
   mapping … is a symmetric random mapping" is the §4.3 success model's
   assumption (:400-402), not a claim that the degree behaviour is z-uniform.
2. **tested (n,m) → all (n,m) with 2 ≤ m < n.** Tested: `n ≤ 21` plus one cell
   at `n = 40`, `m ≤ 6`. The FIPS conclusion (:381-384, Table 3) is drawn at
   `n = 409, 571` with `m = 11, 12` — about 20× in n and 2× in m outside the
   data, and Table 3's optimal m grows with n, so the extrapolation is along
   both axes at once.
3. **one V → any subspace V of dimension k.** Semaev himself notes the choice is
   not neutral (:540-546): a low-degree-polynomial V "significantly reduces the
   time and space complexity in comparison with a randomly generated subspace".
   Two rows of Table 1 use a random V, at a single `(n,m,k) = (17,3,6)`.

This gap is **disclosed in the body** — "very likely", "Although not generally
correct" — and that disclosure is to the paper's credit. It is **not** carried
into the Introduction, which says flatly "The first fall degree is proved to be
4" (:97), nor into the abstract's "Under a first fall degree assumption the
regularity degree of the system is at most 4" (:38-39). A consumer reading only
the front matter gets a stronger claim than the body supports.

### One thing that is NOT a gap, recorded because it looks like one

Semaev's argument is often described as leaning on a symmetry that the coset
shifts would destroy. It does not. RC-2g runs the identical exhibition on an
affine descent `x_i = v_i + Σ_j X_ij α_j` with random nonzero `v_i`, in both the
"three shifted subspace variables" and the "two field variables plus one shifted
subspace variable" shapes: the bound is 4, the product degree is 3, and the fall
survives every trial. The reason is structural — squaring over F₂ is F₂-**affine**
on coordinates, not merely F₂-linear, so `deg_{F2}(x²) = deg_{F2}(x)` is
unaffected by a constant shift.

**Scope, stated precisely so this is not over-read.** This concerns the FAKE
(multilinear) degree only, at n = 7, for one curve parameter and nine random
shift triples, with the multiplier taken to be a field variable exactly as on
p.10. It says nothing about the true first fall degree, nothing about `d_F4`,
and nothing about whether any proposition in any paper is true. It is reported
here because it is a fact about the **reach of Semaev's argument**, which is
this joint's subject. **I do not rule on what any campaign should do with it**;
that is outside this task's authority and outside this joint.

---

## J-5 — PROVES-TOO-MUCH CONTROL (required)

### The object

Apply the argument to a parameter regime where its conclusion is known false.
**The paper supplies the object itself.** §4.5.1 closes (:1054-1058, PDF p.13
y=670/656, confirmed at glyph level in `reextract.md` F-4):

> "To conclude the section we should mention that the maximal degree (regularity
> degree) **generally exceeds 4 when k > ⌈n/m⌉** though **the first fall degree
> is still 4**."

That is: at `k > ⌈n/m⌉`, on this same family of systems, measured by this same
author with this same instrument —

- the **premise** of the argument (first fall degree = 4) **holds**; he says so.
- the **conclusion** of the argument (`d_F4 ≤ 4`) is **false**; he says so.

Assumption 1 is protected from this only by carrying `k = ⌈n/m⌉` among its
hypotheses.

### Does the argument still run there?

**Yes, unchanged.** `k` appears nowhere in it.

`recheck.py` RC-2 puts this beyond doubt rather than leaving it as a reading.
Sweeping `k = 1..n` over F₂⁵ and F₂⁷ with `V = {polynomials in α of degree < k}`:

```
F_{2^5}  k=1..5   deg S3=3   bound=4   deg(x1*S3)=3   fall=True   (k=1: deg 2, deeper)
F_{2^7}  k=1..7   deg S3=3   bound=4   deg(x1*S3)=3   fall=True   (k=1: deg 2, deeper)
```

and the same for random subspaces of dimension 2, 3, n−1, n; for the mixed
field/subspace shape of system (5); and for coset-shifted descents. **No value
of k destroys the fall** (RC-2a, RC-2b, RC-2c, RC-2e, RC-2f, RC-2g). At
`n = 7, m = 3` the exceeded regime is `k = 4..7`, all of which the sweep covers
explicitly (RC-2d).

RC-4 explains why, independently: `deg_{F2}(x^a) = popcount(a)`, verified for
`a = 1..39`, because `x^(2^i)` is F₂-linear in the coordinates of x. The whole
exhibition is that one fact about squaring in characteristic 2. It is a property
of the Frobenius, and the dimension of V does not enter it.

### Verdict on the control

**THE CONTROL FAILS — the argument survives its own known-false object.**

The load-bearing consequence is precise, and it is narrower than it may look:

- **Assumption 1 is not refuted.** Its hypothesis `k = ⌈n/m⌉` excludes the
  regime. It is stated correctly.
- **The justification offered for Assumption 1 does not distinguish the regime
  where it is believed from the regime where the author reports it false.** The
  hypothesis that saves the assumption plays no role whatever in the argument
  for it. Everything the paper offers in support of `d_F4 ≤ 4` at `k = ⌈n/m⌉`
  would equally support `d_F4 ≤ 4` at `k = ⌈n/m⌉ + 1`, where the paper says it
  is wrong.
- **Therefore the first fall degree assumption `d_F4 ≤ d_ff` is not merely "not
  generally correct" in the abstract (:519). It is reported false by this
  paper's own experiments, on this paper's own family of systems, one parameter
  step from the regime the FIPS conclusion is drawn in.** The gap `d_F4 − d_ff`
  for these systems is a measured, nonzero quantity somewhere, and nothing in
  the paper explains why it should be zero at `k = ⌈n/m⌉` other than the
  experiments at `n ≤ 21`.

What the control does **not** establish: nothing here measures `d_F4`, at any k.
The falsity of the conclusion at `k > ⌈n/m⌉` is **the paper's own report**,
taken at face value as a statement by the author about his own experiments. This
task performed no measurement and makes no claim about the true value of `d_F4`
anywhere.

### A second object, for contrast

The argument is not indiscriminate. Run against the terminal equation
`S₃(x₁,x₂,z)` — where the multiplier x₁ gives no fall — it **correctly refuses**
(RC-1f/g/h), and Semaev flags the refusal in the text. So the argument has a
working discriminator along the equation-type axis and **none** along the
dim-V axis. That contrast is what makes the k-insensitivity a finding rather
than a generic complaint about upper-bound arguments.

---

## What I could not determine

1. **Which of S-A / S-B the campaign treats as the consumed statement.** The
   records identify it only by paraphrase and no citation block names 2015/310.
   Reported in J-4a rather than resolved by choosing, per the card.
2. **Whether Semaev's §4.4 `d_ff` is intended over the descents alone or over
   the descents together with the field equations.** The definition is stated
   for the system (12) and (12) does not include them; the sentence immediately
   before it (:449-458) does put them into the *Gröbner basis* ideal, and the
   experiments (:612-613) add them. The text does not say which set the `d_ff`
   of Assumption 1's justification is taken over. Not determinable from the
   frozen source.
3. **Which quantity the sentence "The experiments show it is always 4 again"
   (:598) refers to.** It sits in a first-fall-degree paragraph, but **no
   experiment anywhere in 2015/310 measures a first fall degree.** §4.5.1
   measures `d_F4` via MAGMA's F4 "step degree" (:629-636), and Tables 1–2 have
   a `d_F4` column and no `d_ff` column. So the paper's one experimental claim
   about the first fall degree is supported by experiments it describes as
   measuring a different quantity. I cannot determine whether a separate
   unreported measurement is meant.
4. **Which reading of Nagao's "He uses the true definition of first fall degree"
   (`NAGAO-2015-984` :459) is intended.** Reading A: *Semaev states the result
   under the true definition although the available argument gives only the fake
   bound* — supported by the placement, immediately after "Many researchers
   misunderstand the definition … and use … the FAKE version" (:426-428) and
   immediately before "it has no problem to use Fake first fall degree instead of
   use true first fall degree" (:461-463). Reading B: *Semaev correctly uses the
   true definition.* I adopt Reading A and give my grounds in J-4b B-6, and my
   own independent reading of Semaev's text reaches the same place without
   Nagao. But the sentence alone does not settle it.
5. **The "2300 Boolean systems" accounting.** The tables carry 24 rows with
   t = m (12 in Table 1, 12 in Table 2) at 100 random z each, which is 2400, not
   2300 (RC-5f/g). The discrepancy is exactly one row. Which row is not counted,
   or whether one row is a re-report of another (the four n = 17 variants in
   Table 1 and the n = 17 row of Table 2 are the obvious candidates), is not
   determinable from the frozen source. Minor; recorded because it is an exact
   number in the paper.
6. **Whether the `arxiv: 1504.01175` alias in `source_record.yaml` is correct.**
   That record itself flags it as "NOT independently confirmed in this session";
   I did not confirm it either, and no network fetch of arXiv was made.

---

## Inference provenance

```yaml
requested_policy: review-adversarial
resolved_model_id: claude-opus-5 (self-reported by the runtime)
model_verified: false
degraded_requirements:
  - "model_verified: false -- `python3 -m orchestration.adapter doctor --probe`
     has no credentialed backend in this checkout, so the resolved identifier is
     self-reported and is unverified configuration, not an established fact."
fallback_allowed: true
fallback_used: true
fallback_reason: >-
  Declared up front by the task card: no adapter backend is credentialed in this
  checkout, so the runtime-native binding permitted by core rule 16 is the only
  route. No provider, endpoint, or model identifier containing `bedrock` was
  selected or contacted.
degraded_allowed: false
independent_session_required: true
independent_session: true
reasoning_effort: xhigh (policy default for review-adversarial)
```

## Citations

```yaml
citations:
  - ref: SEMAEV-2015-310 (IACR ePrint 2015/310, rev. 2015-04-10)
    provenance: retrieved
    claim: >-
      Section 4.5's first-fall-degree argument (:561-600), Assumption 1
      (:602-605), the Section 4.4 definition and first fall degree assumption
      (:505-522), the experiments and their conclusion (:607-759), the
      k > ceil(n/m) remark (:1054-1058), Assumption 2 (:1240-1248), and the
      Introduction's "proved to be 4" (:97).
    verified_by: >-
      this task, TASK-20260916-64a93b. Frozen full text read in full; every
      formula relied on additionally reassembled from PDF glyph coordinates and
      recorded in reextract.md.
  - ref: NAGAO-2015-984 (IACR ePrint 2015/984)
    provenance: retrieved
    claim: >-
      Definitions 5 and 6 (:398-410, :430-448), the Semaev paragraph (:452-459),
      Lemmas 3/4/5 (:467-538), Proposition 2 with footnote 5 (:587-600, :690),
      Definitions 7/8 (:692-713), Proposition 5 with footnote 6 (:719-729, :844),
      and the identification of [14] as 2015/310 (:956-960).
    verified_by: >-
      this task, TASK-20260916-64a93b. Frozen full text read in full. Used only
      for how the neighbouring literature uses Semaev's quantities; this task
      owns no joint on that paper and adjudicates nothing in it.
  - ref: H-SEMBIN-a7e721
    provenance: internal
    claim: LINK 1 of the mechanism, which names the consumed Semaev statement.
    verified_by: this task, read at ledger/hypotheses/H-SEMBIN-a7e721.yaml
  - ref: EXP-SEMBIN-4fa22c
    provenance: internal
    claim: the frozen contract's objective, dependencies and citations blocks.
    verified_by: this task, read at experiments/EXP-SEMBIN-4fa22c/specification.yaml
  - ref: SRC-SEMAEV-2015-310
    provenance: internal
    claim: >-
      which statements this program recorded as consumed, and by which goals;
      the Table 3 crossover figure n = 302 that RC-6 is therefore NOT blind to.
    verified_by: this task, read at inputs/SEMAEV-2015-310/source_record.yaml
  - ref: >-
      Petit-Quisquater, ASIACRYPT 2012 [19]; Hodges-Petit-Schlather, Finite
      Fields Appl. 30 (2014) [11]; Shantz-Teske [28]; Faugere-Perret-Petit-
      Renault EUROCRYPT 2012 [6]
    provenance: recalled
    claim: >-
      Named ONLY as the references Semaev cites for the d_ff definition, the
      m^2+1 and 5 bounds, and the supporting experiments. NO AGENT IN THIS TASK
      OPENED ANY OF THEM. They are pointers telling a reviewer where to look and
      they support nothing in this report. In particular, [11]'s bound of 5 for
      S_3(x1,x2,z) is reported here only as what 2015/310 says about [11].
    verified_by: null
```

---

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260916-64a93b
  joints_owned: [J-4a, J-4b, J-4c, J-5]
  sources_read:  # the complete, itemised list is attestation.yaml `sources_read`
    - AGENTS.md
    - agents/validator.md
    - templates/research-records.md
    - docs/inventor-protocol.md (headings, and sections 3-4 in full at :73-147)
    - inputs/SEMAEV-2015-310/paper_fulltext.md
    - inputs/SEMAEV-2015-310/eprint-2015-310.pdf
    - inputs/SEMAEV-2015-310/source_record.yaml
    - inputs/SEMAEV-2015-310/provenance.json
    - inputs/SEMAEV-2015-310/tables.yaml
    - inputs/SEMAEV-2015-310/{eprint-2015-310.pdf,paper_fulltext.md}.sha256
    - inputs/NAGAO-2015-984/paper_fulltext.md
    - inputs/NAGAO-2015-984/{eprint-2015-984.pdf,paper_fulltext.md}.sha256
    - experiments/EXP-SEMBIN-4fa22c/specification.yaml
    - ledger/hypotheses/H-SEMBIN-a7e721.yaml
    - coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/ (directory
      listing only, to create this task directory; no file in it was opened)
  read_sibling_reports: false
  blind_from_respected: true
  verdict: breaks
  verdict_scope: >-
    `breaks` is reported on THE J-5 CONTROL AND ON J-4c, for the joints owned:
    a gap between statement and argument is found and named, and the argument
    survives its own known-false object. It is NOT a verdict on Semaev's paper,
    on Nagao's Proposition 5, on H-SEMBIN-a7e721, or on the campaign -- none of
    which this task can see whole, and none of which it has authority over.
```

**Blindness.** None of the five paths in `blind_from` was opened:
`coordination/review/sembin-20260916-e0a0c1/read-plan.yaml`,
`ledger/decisions/DEC-20260916-441cd5.yaml`,
`coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/opening-report.md`,
`ledger/goals/GOAL-SEMBIN-fcb7a2/checkpoints/BATCH-e0a0c1.yaml`, and the sibling
task directory `…/BATCH-e0a0c1/read-nagao-2013-549`. I listed
`…/BATCH-e0a0c1/` once, to create my own task directory, and saw the names
`opening-report.md`, `build_queue.py`, `dispatch_queue.json`, `archives/`,
`claims/`. I opened none of them. `read-nagao-2013-549` did not exist at that
time. I also did not read `tools/`, `research/`, or `coordination/review/`,
per the read scope.

One boundary case, disclosed rather than absorbed:
`experiments/EXP-SEMBIN-4fa22c/specification.yaml` and
`ledger/hypotheses/H-SEMBIN-a7e721.yaml` are both in the read scope the card
grants, and both quote prior findings of this campaign — including
`CORR-20260916-96f47d`'s quantifier correction and the hand algebra of
`coordination/review/sembin-20260916-propquant/coordinator-recheck.py`. I read
those quotations because they are inside files I was told to read. I did **not**
open the referenced files, and no finding in this report depends on them: J-4b's
degree results and the J-5 control were derived from the frozen Semaev text and
from `recheck.py`, both of which are independent of anything that campaign has
computed.
