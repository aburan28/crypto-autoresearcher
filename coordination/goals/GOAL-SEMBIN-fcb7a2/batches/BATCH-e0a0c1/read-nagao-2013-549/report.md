# Blind read of Nagao ePrint 2013/549 — joints J-1, J-2, J-3, and the J-5 control

Task `TASK-20260916-9da6e0`. Goal `GOAL-SEMBIN-fcb7a2`, batch `BATCH-e0a0c1`.
Role: validator, independent session. **Zero runs, zero measurements.** The
arithmetic in `recheck.py` is a hand-check of algebraic steps, mechanised, and
is labelled a recheck throughout; it samples nothing and measures no property
of any research object.

## Inference provenance

```yaml
requested_policy: review-adversarial
reasoning_effort: xhigh (policy default; the runtime does not expose a knob this
                  session can read back, so this is the requested value and not
                  a verified one)
resolved_model_id: claude-opus-5        # SELF-REPORTED by the session; see below
model_verified: false
fallback_used: true
fallback_reason: >-
  No adapter backend is credentialed in this checkout, so the runtime-native
  binding permitted by AGENTS.md core rule 16 is the only route.
  `orchestration.adapter doctor --probe` has no usable backend here, so the
  resolved identifier above is unverified configuration and not an established
  fact. Declared up front in the task card, not discovered afterwards.
degraded_allowed: false
degraded_requirements: [model_verified]
independent_session: true
```

## How to read the line citations

Three files are cited by line and they are not interchangeable.

- `pymupdf NNN` — `inputs/NAGAO-2013-549/paper_fulltext.pymupdf.txt`, the clean
  companion the errata added beside the frozen text. Stable, in the repository.
- `frozen md NNN` — `inputs/NAGAO-*/paper_fulltext.md`, hash-pinned and cited by
  every existing record. Shredded at formulas for 2013/549.
- `2015/984 PDF NNN` — line numbers in a `pymupdf` extraction of
  `inputs/NAGAO-2015-984/eprint-2015-984.pdf` that I made in a scratch directory
  **outside the repository**, because the frozen markdown mangles the passages
  J-3 turns on. It is not a deliverable; the two-line command that reproduces it
  byte-for-byte from the hash-verified PDF is recorded in `reextract.md`.

## Bottom line, before the detail

| joint | verdict | one line |
|---|---|---|
| J-1 | **holds** | The match is 2013/549's **Lemma 2**, not its Lemma 3. The restatement is faithful in content, with three transcription defects. |
| J-2 | **holds** | Lemma 2 is proved, the induction is well-founded, and the proof is complete after filling six write-up defects, none of which needs a new idea. |
| J-3 | **breaks** on Lemma 4 as printed; **holds conditionally** on the form the paper actually uses | Lemma 2 cannot deliver Lemma 4 as written, and Lemma 4 as written is false — counterexample below. It delivers the form with `S_fe` on the **true** side, under one extra hypothesis neither paper states. |
| J-5 | **control PASSES** | The derivation does not go through with `S_fe` outside. It fails at exactly the step whose absence makes the outside form false. |

A second, independent J-5 finding: under the `>=` reading of condition (1)
printed in 2015/984, the inside form is true *without Lemma 3 at all*. A
derivation that succeeds without its main ingredient is a tell that the
reading is wrong, and this is a second way the control bites.

**A terminological warning that affects how J-3 and J-5 should be read
together.** The card distinguishes an INSIDE form (`S_fe` inside the fake
system, which is how Lemma 4 is written) from an OUTSIDE form. I find that
adjoining `S_fe` to the **fake** system changes `d'_F` by nothing at all — every
product `h_j(X_j^p − X_j)` is `0` mod `S_fe`, so all three of Definition 6's
conditions are untouched (`recheck.out` 92–102, exhaustive, both readings). The
placement that decides whether `d_F ≤ d'_F` is true is on the **true** side, and
there Lemma 4 as printed puts `S_fe` outside. On my reading, Lemma 4-as-printed
and the object this program verified false are therefore the same statement.
That is a reading of the definitions, not a ruling on the campaign's naming;
J-3 and J-5 below are each answered on their own terms regardless.

---

# J-1 — which numbered statement of 2013/549 does 2015/984 quote as its Lemma 3?

## Answer

**Lemma 2 of Nagao ePrint 2013/549**, in §2 ("First fall degree assumption").

- Clean extraction `inputs/NAGAO-2013-549/paper_fulltext.pymupdf.txt`, lines
  **303–313** (statement), 314–414 (proof).
- Frozen `inputs/NAGAO-2013-549/paper_fulltext.md`, lines **685–708**
  (statement, shredded), 721–945 (proof, shredded).
- PDF `inputs/NAGAO-2013-549/eprint-2013-549.pdf`, page 3 bottom to page 5 top.

I matched on **content**, not on number, as the card required — and the card's
warning was well placed. 2013/549 **has its own Lemma 3** (pymupdf 471–478,
frozen md 1081) and it is a completely different statement: *for a monomial
`m = prod X_i^{e_i}` with `0 <= e_i <= p^{n'}-1`, `deg(wd(m)) = sum_i wt(e_i)`*.
Nothing to do with field-equation multipliers. A reader matching on number
would have read the wrong statement.

## The statement, verbatim

From the PDF (pymupdf 303–313; the frozen markdown renders this as a scatter of
fragments — see `reextract.md`):

> **Lemma 2.** Let `G_1, ..., G_N ∈ F_p[X_1,..,X_N]` be local polynomials and put
> `F := Σ_{i=1}^{N} G_i · (X_i^p − X_i)` and `D := deg F`. So, there are some
> local polynomials `G'_1, ..., G'_N ∈ F_p[X_1,..,X_N]` satisfying
> `F := Σ_{i=1}^{N} G'_i · (X_i^p − X_i)` and `deg G'_i ≤ D − p (i = 1, ..., N)`.

## Every hypothesis it carries

1. `p` is a small prime **or a power of a prime** (§1, pymupdf 58).
2. `G_1, ..., G_N` are *local* polynomials, i.e. in `F_p[X_1,...,X_N]` with
   `N = d·n'` (§1, pymupdf 71–78). One multiplier per variable.
3. `F` is **given as** `Σ_{i=1}^N G_i (X_i^p − X_i)` — equivalently, `F` lies in
   the ideal generated by the field equations `S_fe` (pymupdf 80–82).
4. `D := deg F`, total degree.

That is the complete list. In particular the statement carries **no monomial
order**, **no reducedness condition**, **no bound on `deg G_i`**, and **no
connection to Definition 1** (first fall degree). Lemma 2 is a pure
ideal-membership-and-degree statement; it is used by the first-fall machinery
but does not depend on it.

## Definitions it depends on

- *local polynomial* / *local variable* / `N = d n'` — §1, pymupdf 71–78.
- `S_fe := {X_{i,j}^p − X_{i,j}}` — §1, pymupdf 80–82.
- total degree `deg`.

It does **not** depend on `wd(·)`, `[·]↓_k`, Definition 1, Definition 2
(weight), or Assumption 1/2, all of which are introduced elsewhere in the paper.

## Corroboration that `[11]` is this paper

- 2015/984's reference list: `inputs/NAGAO-2015-984/paper_fulltext.md:946`,
  "11. K. Nagao, Equations System coming from Weil descent and subexponential
  attack for algebraic ..." — 2013/549's exact title (pymupdf 3–4).
- Independent second anchor: 2015/984's **Lemma 5** (PDF 285–295), also
  attributed to `[11]`, is content-identical to 2013/549's **Lemma 9**
  (pymupdf 710–723) — `[m·F]↓_j ≡ Σ_i [α_i·m]↓_j [F]↓_i mod S_fe`, with
  2013/549's basis `w_i` written `α_i`. Two independent citations into the same
  paper, both renumbered, both content-matched.

## Is 2015/984's restatement faithful, weaker, or stronger?

**Faithful in mathematical content — neither weaker nor stronger.** Same
hypothesis, same conclusion, same bound `deg f^new_i ≤ deg F − p`. Three
transcription defects, all confirmed in the PDF (2015/984 PDF 252–267) and so
not extraction artifacts:

- **R-1 (an addition, true but unproved).** 2015/984 prefixes "such that
  `F ≡ 0 mod S_fe`. i.e., There are `f_1,...,f_M` such that `F := Σ_{i=1}^N f_i
  (X_i^p − X_i)`." The "i.e." asserts *reduction to zero ⟺ ideal membership*.
  That is true — the `X_i^p − X_i` have pairwise coprime leading monomials and
  so form a Gröbner basis of the ideal they generate, under any order — but it
  is an addition: 2013/549's Lemma 2 never mentions `mod S_fe`, and neither
  paper proves the equivalence. It is load-bearing for anyone who reaches
  Lemma 2 from a reduction rather than from a representation.
- **R-2 (index count).** The multiplier lists are named `f_1,...,f_M` and
  `f^new_1,...,f^new_M` while both sums run to `N` and the conclusion is stated
  "(i = 1,...,N)". The correct count is `N`, one multiplier per variable.
- **R-3 (symbol collision).** The `f_i` of Lemma 3 are **field-equation
  multipliers**; the `f_1,...,f_M` of Definitions 5 and 6 and of Lemma 4, three
  paragraphs later, are the **generators of the system**. Same symbols, disjoint
  meanings, on the same page. This collision is the most likely route by which a
  reader derives Lemma 4 from Lemma 3 and does not notice which side the field
  equations are on — which is exactly what J-3 turns out to be about.

## Example 1 of 2015/984 is internally inconsistent (found in passing)

2015/984 attaches an Example 1 to its Lemma 3 (PDF 268–276). It is not in
2013/549 and is 2015/984's own. As printed it does not hold together:

| printed line | polynomial |
|---|---|
| `F := (X²+X)(Y²+Y) + (X²+X)(Y²+Z)` | `X²Y + X²Z + XY + XZ` |
| "expanding the formula, we have `F = X²Y+Y²Z+YZ+X²Z+XY²+XZ`" | a **different** polynomial |
| `= (X+Z)(Y²+Y) + (X²+X)(Y+Z)` | equals the printed **expansion**, not the printed `F` |

The first and last lines differ by `XY + XY² + YZ + Y²Z = (X+Z)(Y²+Y)`. Verified
mechanically, `recheck.py` CHECK 1 / `recheck.out` lines 5–34.

Replacing one character — the first factor `(X²+X)` by `(X²+Z)` — makes the
printed expansion and the printed final line both correct, and makes the example
actually illustrate the lemma: the reconstruction's multipliers have degree 2,
above the lemma's `deg F − p = 1`, so it is an instance the lemma has to repair,
whereas the printed `F` collapses to `(X²+X)(Y+Z)` whose multiplier is already
degree 1 and needs no repair. I verified the reconstruction against three of the
four printed lines; I **cannot determine** that it is what the author intended,
only that it is consistent with more of the printed text than the printed text
is with itself. This is a defect in 2015/984, not in 2013/549, and it does not
touch J-1's answer.

**J-1 verdict: holds.** The statement 2015/984 quotes exists upstream, is
2013/549's Lemma 2, and is quoted faithfully in content.

---

# J-2 — is Lemma 2 proved in 2013/549, and is the proof complete on its own terms?

## Answer

**Yes, it is proved** (pymupdf 314–414), and the proof is **complete on its own
terms** once six write-up defects are filled. None of the six needs a new idea;
each is a line. I executed the construction rather than read it: `recheck.py`
CHECK 2, output at `recheck.out` lines 36–79.

## The proof, and the four questions the card asks

**Structure.** Fix a monomial order `>` refining total degree. Let
`𝒢 := {(G_1,...,G_N) : F = Σ G_i(X_i^p − X_i)}`. For `G ∈ 𝒢` let `ψ(G)` be the
largest monomial among `LM(G_i X_i^p)`, `IND(G)` the set of indices attaining it,
`NUM(G) = #IND(G)`. Branch on `NUM(G) = 1` (done directly) versus
`NUM(G) > 1` together with `deg ψ(G) > D` (descend).

**Is the measure well-founded?** **Yes.** The measure is `ψ(G)` under `>`. A
monomial order is by definition a well-ordering of the monomials, so there is no
infinite strictly descending chain of `ψ`-values, and the descent terminates. The
paper says only "from the induction of `ψ(G)`" and never argues this; it is
standard and correct.

**Is there a base case?** **Not stated, but present in effect.** The terminal
tuples are exactly those the construction does not apply to: `NUM(G) = 1`, or
`deg ψ(G) = D`. Since the conclusion asserts only the *existence* of some good
representation, reaching any terminal tuple finishes the proof. My recheck hits
both terminal kinds across four starting tuples (`recheck.out` 46–62).

**Does the inductive step preserve the degree bound?** The induction does not
carry the degree bound through steps — it carries membership in `𝒢` and strict
descent of `ψ`, and the bound is read off at the terminal tuple. Both invariants
verified mechanically at every step of every test tuple: `G^new ∈ 𝒢` (the
combination is unchanged) and `ψ(G^new) < ψ(G)`. The terminal bound
`deg G'_i ≤ D − p` then holds, and did hold in all four cases.

The load-bearing algebraic identity, item (3) of the proof,

```
(X_{I_i}^p − X_{I_i})·G_{I_i}
   = (X_{I_i}^p − X_{I_i})·(G_{I_i} − LT(G_{I_i}) + LT(G_{I_i})/X_{I_1}^{p−1})
   + (LT(G_{I_i})/X_{I_1}^p)·(X_{I_1}^p − X_{I_1})·(X_{I_i}^p − X_{I_i})
```

is exact, for `p = 2` and `p = 3`, verified at `recheck.out` 38–41. By hand: the
bracket collapses because `(L/A^p)(A^p − A) = L − L/A^{p−1}`.

**Does the proof use a hypothesis the statement does not carry?** **No — but one
choice in it is load-bearing and is invisible in the frozen markdown.** The
graded monomial order is *chosen* inside the proof, and a graded order exists
unconditionally (grevlex), so it is not a hidden hypothesis on the statement. It
is, however, essential: the `NUM(G) = 1` branch concludes `D = deg F = deg ψ(G)`,
which needs `deg ψ(G) ≥ deg G_i + p` for every `i`, and that is precisely what a
graded order buys and a merely lexicographic one does not. This is the passage
`errata-extraction-20260921.md` flags: `paper_fulltext.md` lines 721–734 render
the hypothesis as a per-variable comparison that says nothing, so a reader
confined to the frozen markdown would conclude the proof rests on an empty
condition. It does not. See `reextract.md`.

## The six write-up defects

| # | defect | status |
|---|---|---|
| D-1 | The case split is incomplete: `NUM(G) = 1`, and `NUM(G) > 1 AND deg ψ(G) > D`. The case `NUM(G) > 1` with `deg ψ(G) = D` falls through both branches. | Harmless. `deg ψ(G) ≥ D` always, and when `deg ψ(G) = D` then `deg G_i + p ≤ D` for every `i` and the conclusion is immediate. My recheck terminates in this unhandled case on 2 of 4 tuples (`recheck.out` 57, 61), so it is not a corner case. |
| D-2 | The `NUM(G) = 1` branch asserts `D = deg F = deg ψ(G)` with no argument. | True. `ψ(G)` cannot cancel: against another `G_jX_j^p` because `j ∉ IND` means strictly smaller; against any `G_jX_j` because a graded order makes those strictly smaller in total degree. Needs one sentence. |
| D-3 | Claim 1) is printed `X_{I_1}^p | G_{I_i}` — the **whole** multiplier. | **False as printed.** Witness, from my own test set: `p=2`, `N=2`, `G = (X+Y², Y+X²)`; `IND = {1,2}`, and `X²` does not divide `Y+X²` but does divide its leading term `X²` (`recheck.out` 63–72). What the argument establishes and what identity (3) needs is `X_{I_1}^p | LT(G_{I_i})`, which is true. The step goes through on the LT form. |
| D-4 | Identity (3) is printed "(i = 1, ..., k)". | Valid and used only for `i = 2..k`. For `i = 1` it would require `X_{I_1}^p | LT(G_{I_1})`, which is not guaranteed. |
| D-5 | The display `G^new_{I_1} X^p_{I_1} = ... = Σ_{i=1}^k LT(G_{I_i})X^p_{I_i} = 0`. | False as an equation between polynomials. What vanishes is the **coefficient of `ψ(G)`**, by claim 2). The correct reading is `G^new_{I_1}X^p_{I_1} = (G_{I_1} − LT(G_{I_1}))X^p_{I_1} − Σ_{i≥2} LT(G_{I_i})X_{I_i}`, all of whose monomials are `< ψ(G)`. Presentational. |
| D-6 | Claim 2) prints the same expression on both sides of an equality (`Σ LT(...) = Σ LT(...) = 0`), and the proof writes the ring as `F_p[X_1,...,X_d]` where the statement says `F_p[X_1,...,X_N]`. | Typographic. Claim 2) itself is true and its justification is the case hypothesis `deg ψ(G) > D`: the `ψ(G)`-coefficient of `F` must vanish because `ψ(G)` has degree above `deg F`. |

**J-2 verdict: holds.** Lemma 2 is proved; the induction is well-founded with a
recoverable base case; the inductive step preserves membership in `𝒢` and
strictly decreases the measure, verified mechanically; and no hypothesis absent
from the statement is used. D-3 is a genuine false claim in the printed proof
with an exhibited witness, and it is repaired by weakening it to the leading
term, which is what the rest of the proof uses anyway.

## A version caveat I cannot discharge

The served PDF is the **second revision**. Its note (pymupdf 35–38) reads
"Lemma 9 of the first version of this manuscript is false and I delete the
content of §4". The served text has **no Lemma 10** — numbering runs 1–9, then
11 — which is consistent with a deletion, and the served Lemma 9 sits in §3 and
is stated and proved (pymupdf 710–744).

**I cannot determine whether the served Lemma 9 is the statement the note
declares false.** The first revision is not in `inputs/` and is not fetchable
here, so I will not reason about it. Two things I *can* say:

1. This uncertainty **does not touch Lemma 2**, the J-1 match. Lemma 2 is in §2,
   is named by neither revision note, and is proved in the served text.
2. It **does** touch 2015/984's **Lemma 5**, which cites `[11]` for content
   matching the served Lemma 9. That is not my joint; I flag it as a pointer.

---

# J-3 — does Lemma 2 support Lemma 4 in the INSIDE form?

## The two statements, exactly as printed

2015/984 **Lemma 4** (PDF 279–282, frozen md 510–515):

> Let `f_1, ..., f_M ∈ F_p[X_1,...,X_N]`. Put `d_F` by the first fall degree of
> `{f_1,...,f_M}` and put `d'_F` by the Fake first fall degree of
> `{f_1,...,f_M} ∪ S_fe`. Then `d_F ≤ d'_F`.

Note where the union sits: on the **fake** side, and **not** on the true side.

### Which side does "INSIDE" name? A terminological warning

The card names Lemma 4's printed form the **INSIDE** form, `d'_F` taken of
`{f_1..f_M} ∪ S_fe`. That is a faithful description of how Lemma 4 is written,
but I must report that **this placement is inert**. Adjoining `S_fe` to the
*fake* system does not change `d'_F`:

Definition 6 gives multipliers to the system's members and states all three of
its conditions **mod `S_fe`**. A member `X_j^p − X_j` given its own multiplier
`h_j` contributes `h_j(X_j^p − X_j) mod S_fe = 0` — identically, for every `h_j`.
So it contributes `deg = −∞` to condition (1) and nothing to conditions (2) and
(3): all three conditions are unchanged, and so is the minimum over witnesses.
Verified exhaustively on my counterexample under both readings of condition (1)
at `recheck.out` 92–102.

**Consequence for the joint as posed.** "Field equations inside vs outside the
*fake* system" is a distinction without a difference. The placement that
changes the truth value of `d_F ≤ d'_F` is on the **true** side, and on that
side Lemma 4 as printed puts them **outside**. So Lemma 4's printed form and
the form this program has verified false by exhaustive search are, as far as I
can determine, **the same statement** — which is why my J-5 control has real
work to do and is not a formality. I report this; I do not rule on how the
campaign should name its forms.

2015/984 **Definition 5** (true) and **Definition 6** (fake), PDF 212–242. Two
features of the printed definitions, both confirmed in the PDF and therefore
**not extraction artifacts** — this settles the open extraction question
recorded in `CORR-20260916-96f47d.residual_uncertainty`:

- Condition (1) of **both** reads `>= d_F`, not `= d_F`. 2013/549's own
  Definition 1 (pymupdf 204–209) reads `= D_ff` and additionally carries a
  condition 4, `deg(f_i) ≤ D_ff`, which 2015/984 drops.
- Definition 6's conditions (1) and (2) name **`d_F`**, not `d'_F`, so as
  printed the definition of `d'_F` never mentions `d'_F`. The only sensible
  repair is to read them as `d'_F`, and I do so throughout, flagged.

Whether the `>=` and the bare `d_F` are authorial or typesetting I still
**cannot determine** — but they are in the PDF, so the question is now about
Nagao's intent, not about the extractor.

## The derivation, and the hypotheses it consumes

Let `(g_1,...,g_M)` be a fake-fall witness at level `d'`. Put
`P := Σ g_i f_i` and `P̄ := P mod S_fe`.

1. `P̄ ≠ 0` and `deg P̄ < d'` — fake conditions (2) and (3).
2. `R := P − P̄` lies in `⟨S_fe⟩` — **(H2)**: reduction is `F_p`-linear, never
   raises total degree, and `F ≡ 0 mod S_fe ⟺ F ∈ ⟨S_fe⟩`. (This is exactly
   R-1, the equivalence 2015/984 adds and neither paper proves.)
3. `deg R ≤ max(deg P, deg P̄) ≤ max_i deg(g_i f_i)`.
4. **(H1) = 2013/549 Lemma 2** applied to `R` gives `G'_j` with
   `deg G'_j ≤ deg R − p`, hence `deg(G'_j (X_j^p − X_j)) ≤ deg R`.
5. Therefore `Σ_i g_i f_i + Σ_j (−G'_j)(X_j^p − X_j) = P̄`, a combination whose
   products all have degree `≤ max_i deg(g_i f_i)` and whose sum `P̄` is nonzero
   of degree `< d'`.
6. Reading off a first fall requires the combination to be a combination **of
   members of the system whose `d_F` is being bounded** — **(H3)**: `S_fe` must
   be *inside* that system, because step 5 puts multipliers on the field
   equations.

**What the derivation actually delivers:**

```
d_F( {f_1..f_M} ∪ S_fe )  ≤  max_i deg( g_i f_i )          [unreduced]
```

To turn that into `≤ d'_F` needs one more hypothesis:

- **(H4)** the witness realising `d'_F` satisfies `max_i deg(g_i f_i) ≤ d'_F` —
  i.e. its products lose no total degree under reduction mod `S_fe`.

**(H4) does not follow from Definition 6**, which bounds only
`deg(g_i f_i mod S_fe)`. The two can differ arbitrarily: with `p = 2`,
`g = X^5`, `f = X`, the product has unreduced degree 6 and reduced degree 1.
Lemma 2 cannot close this gap, because Lemma 2's bound is relative to `deg R`
and `deg R` is itself governed by the unreduced product degree — step 3 above is
where the loss is, and it is upstream of Lemma 2.

## Does it support Lemma 4 as printed? No, and Lemma 4 as printed is false.

Lemma 4 puts the union on the fake side and leaves the true side as
`{f_1,...,f_M}` alone. The derivation cannot produce that: **(H3) fails**,
because the witness it constructs needs the field equations as members. Drop
them and you must add `R` back, and the sum returns to `P`, whose degree is
`deg R` — no fall.

That is not merely a failed derivation. The statement is false:

> **Counterexample, `p = 2`, `F_2[X,Y]`:  `f_1 = X²Y`, `f_2 = XY + X`.**
>
> | quantity | `=` reading (2013/549 Def. 1) | `>=` reading (2015/984 Def. 5/6) |
> |---|---|---|
> | fake `d'_F` of `{f_1,f_2} ∪ S_fe` | **2** | **2** |
> | true `d_F` of `{f_1,f_2}` (`S_fe` outside) | **3** | **3** |
> | true `d_F` of `{f_1,f_2} ∪ S_fe` (`S_fe` inside) | **3** | 2 |
>
> So `d_F = 3 > 2 = d'_F`: **Lemma 4 as printed is false**, under both readings.

Verified in `recheck.py` CHECK 3, output `recheck.out` 81–136. The searches are
**exhaustive, not sampled**: the fake quantities range over all 256 reduced
multiplier pairs (reduction is lossless here because every condition of
Definition 6 is stated mod `S_fe`), and the true `=`-reading quantities are
searched at every `d = 0..4` over every multiplier with `deg(g_s s) ≤ d`. The
`>=`-reading lower bounds, which a bounded search cannot certify, are supplied
by two ring homomorphisms: `X ↦ 0` annihilates both generators, and `Y ↦ 1`
sends `f_1 ↦ X²`, `f_2 ↦ 0`; together they exclude every nonzero element of
degree `≤ 1` from `⟨f_1,f_2⟩`.

The mechanism is visible in the table: `f_1 = X²Y` is **not reduced** mod
`S_fe`. The fake world sees `f_1` as `XY`, of degree 2; the true world sees
degree 3. Everything else follows.

I constructed this counterexample from the definitions before reading
`CORR-20260916-96f47d`. It is a different object from the one recorded there
(`f_1 = X1X2 + X3`, `f_2 = X1 + X2`), and it is stronger in one respect: it also
kills the inside form under the `=` reading, which that one does not.

## Does it support the form the paper actually uses? Yes, conditionally.

**The load-bearing textual finding of this joint.** 2015/984's *only* use of
Lemma 4 is in the proof of its Lemma 6, and there the union sits on the **other
side**:

- Lemma 6's statement (PDF 296–298): "The **first fall degree** of the equations
  system `{F↓_j | 1 ≤ j ≤ n} ∪ S_fe` is heuristically `≤ (p−1)n + deg F`."
  — union on the **true** side.
- Lemma 6's proof (PDF 321–323): "**Fake** first fall degree of
  `{F↓_j | 1 ≤ j ≤ n}` is bounded by `≤ (p−1)n + deg F` and from Lemma 4, we
  have this lemma." — **no** union on the fake side.

That is the exact reverse of Lemma 4's printed placement, and it is the sound
direction — the one the derivation above delivers. The same placement is what
2013/549 itself does. 2013/549 **never states Lemma 4**; it states the specific
estimate (pymupdf 415–418): "From this lemma, the first fall degree of the
equations system, which consists of the following **`n + N` number equations**
`{[f]↓_k} ∪ S_fe`, is heuristically `1 + max_i deg[f]↓_i`." The count `n + N`
makes the `N` field equations *members*, which is (H3) discharged by
construction.

And in that setting **(H4) is discharged too, by explicit bookkeeping rather
than by the fake definition**: Petit et al.'s multipliers have `deg g_i ≤ 1`
(pymupdf 285–290) and the `[f]↓_i` are reduced by construction of `wd(·)`
(pymupdf 88–96), so the unreduced product degree is `≤ 1 + max_i deg[f]↓_i`,
which is the claimed fall level. The same is true in 2015/984's Lemma 6, whose
proof tracks `deg[α_i·m]↓_j = (p−1)n` and `deg[F]↓_i = deg F` on already-reduced
local polynomials.

## Upstream hypotheses the campaign must record as its own dependencies

Anyone invoking `d_F ≤ d'_F` inherits all of these, and none of them is stated
in Lemma 4:

| id | hypothesis | where it comes from | discharged how, in the paper's use |
|---|---|---|---|
| U-1 | `p` prime or prime power; multipliers and generators in `F_p[X_1..X_N]` with `N = d n'` | 2013/549 §1 | by construction |
| U-2 | `F ≡ 0 mod S_fe ⟺ F ∈ ⟨S_fe⟩` | asserted by 2015/984's "i.e." (R-1); proved in neither paper | true (coprime leading monomials), but **unproved upstream** |
| U-3 | `S_fe` is **inside the system whose `d_F` is claimed** | (H3); 2013/549 pymupdf 415–418, 2015/984 PDF 296–298 | by construction in every application |
| U-4 | the fake witness's **unreduced** product degrees are `≤ d'_F` | (H4); stated **nowhere** | by explicit degree bookkeeping (`deg g_i ≤ 1`, reduced `[f]↓_i`) — **not** by Definition 6 |
| U-5 | reduction mod `S_fe` is linear and never raises total degree | implicit throughout | true |
| U-6 | condition (1) read as `=`, not the printed `>=` | see below | **undetermined in the source** |
| U-7 | Definition 6's conditions read `d'_F` where the PDF prints `d_F` | 2015/984 PDF 238, 240 | **a defect in the source**; the repair is forced but is a reading |

U-4 is the one this read adds. It is not a technicality: it is the entire
distance between what Lemma 2 gives and what Lemma 4 claims.

## A cross-check on U-6, reached from a different direction

Under the printed `>=` reading, the inside form is true **and Lemma 3 is not
needed for it**. Given any fake witness, `P̄` is a nonzero element of the
extended ideal of degree `deg P̄`, *any* representation of `R` makes it a legal
combination, and `>=`'s condition (1) is *helped* rather than hurt by large
products — so `d_F(inside) ≤ deg P̄ + 1 ≤ d'_F` with no degree control on the
field-equation multipliers whatsoever. Demonstrated with a deliberately bad
degree-6 multiplier at `recheck.out` 168–176.

So: if Lemma 4 genuinely rests on Lemma 3, the reading cannot be `>=`. This is
an independent corroboration of `EXP-SEMBIN-4fa22c`'s declared equality
convention (`declared_conventions.condition_1`), reached from the upstream
lemma's necessity rather than from Assumption 1's degeneracy. I report the
agreement; I do not rule on the contract.

**J-3 verdict: breaks on Lemma 4 as printed — the derivation fails and the
statement is false. Holds conditionally on the form the paper uses**
(`S_fe` inside the true system, `S_fe` absent from the fake side), with U-4 as
an unstated hypothesis that must be discharged instance by instance.

---

# J-5 — PROVES-TOO-MUCH control

**Object:** the outside form — field equations outside the fake system, which
this program has verified false by exhaustive two-polynomial search over `F_2`.
I re-derived a counterexample of my own for it (above) before reading that
record.

**Outcome: the control PASSES. My derivation does not go through.**

Run on `f_1 = X²Y`, `f_2 = XY + X` with the fake witness `g = (1,1)`
(`recheck.py` CHECK 4, `recheck.out` 139–176):

- `P = X²Y + XY + X`, `P̄ = X`, `R = P − P̄ = Y(X²+X)`, `deg R = 3`.
- Lemma 2 applies and gives `G'_X = Y` with `deg G'_X = 1 ≤ deg R − p = 1`. The
  lemma does its job exactly as advertised.
- **With `S_fe` inside:** `1·f_1 + 1·f_2 + Y·(X²+X) = X`. Products of degree
  `3, 2, 3`; sum of degree 1. A fall at 3. The derivation yields
  `d_F(inside) ≤ 3`, **not** `≤ d'_F = 2` — lossy by exactly the
  reduced/unreduced gap, which is (H4).
- **With `S_fe` outside:** the term `Y·(X²+X)` is not a member of the system.
  The only admissible combination from the same witness is `P` itself: products
  of degree `3, 2`, sum of degree **3**. No drop. **The derivation halts.**

The failure is localised: it is step 6, the single step that uses the field
equations as members, and it is the same step whose absence makes the outside
form false. A derivation that broke somewhere else, or that survived, would have
told me the derivation was wrong. It broke in the right place.

**Second half of the control, which also bites.** Under the `>=` reading the
inside form goes through *without Lemma 3* (above). That is the other kind of
proving-too-much: not an argument surviving where its conclusion is false, but
an argument succeeding without its stated ingredient. It is evidence about the
reading rather than about the derivation, and I record it as such.

---

# What I could not determine, and why

1. **Whether the served Lemma 9 of 2013/549 is the "Lemma 9" the revision note
   declares false.** The first revision is not in `inputs/` and is not fetchable
   here. I decline to reason about it. Does not affect Lemma 2 (§2, unmentioned
   by either note, proved in the served text); does bear on 2015/984's Lemma 5,
   which is not my joint.
2. **Whether the printed `>=` in Definitions 5 and 6, and the bare `d_F` in
   Definition 6's conditions, are authorial or typesetting.** I can now say they
   are **in the PDF** and are not extraction artifacts — which narrows the
   question `CORR-20260916-96f47d` left open — but authorial intent is not
   recoverable from this text.
3. **Whether my one-character reconstruction of Example 1 is what the author
   wrote.** It is consistent with three of the four printed lines; the printed
   text is not consistent with itself. Intent is not determinable.
4. **Nothing in Lemma 2's statement or proof was undeterminable.** The
   `pymupdf` extraction is intact throughout that passage, and I read the PDF
   spans directly for the disputed monomial-order line. No "cannot determine" is
   needed anywhere in J-1 or J-2.

# Limitations

- This is a reading of two frozen texts plus exact hand algebra on two and three
  variables over `F_2` and `F_3`. It is **not a measurement**, not evidence about
  any elliptic curve, and not a claim about any research object.
- It rules on nothing the campaign should do. It does not change a status,
  discharge a joint, or authorise anything.
- Verdicts are on **my joints only** (J-1, J-2, J-3, J-5). I did not see the
  other joints and form no view on the claim as a whole.
- The exhaustive searches in `recheck.py` are exhaustive **within their declared
  bounds** (`d ≤ 4`; multiplier degree bounded by `d − deg s`). The `>=`-reading
  lower bounds rest on the two homomorphism certificates, not on the search.
- I read `inputs/NAGAO-2013-549/errata-extraction-20260921.md`, which the card
  directed me to and which is program-authored. It names Lemma 2 as the
  statement 2015/984 cites, so my J-1 answer was available to me before I
  derived it. I derived it independently by enumerating the numbered statements
  and matching content, and I record the leak rather than claim a blindness I
  did not have. J-2, J-3 and J-5 are untouched by it.
- I read `ledger/corrections/CORR-20260916-96f47d.yaml`, which the card placed in
  scope and which contains the program's prior finding that Lemma 4's literal
  form is false, with its own counterexample. I read it **after** constructing
  mine. Where we agree, treat that as one independent confirmation, not two.
- I opened **no file** in the sibling reader's directory. I did see its five file
  *names*, sizes and mtimes, from an `ls` I ran at the very end to confirm I had
  not modified another task's files. That is metadata and carries no verdict, but
  it is contact with a `blind_from` path and is disclosed in full in
  `attestation.yaml` (`blind_from[].disclosed_contact`) rather than passed over.

```yaml
review_attestation:
  joints_owned: [J-1, J-2, J-3, J-5]
  verdicts:
    J-1: holds
    J-2: holds
    J-3: breaks_as_printed_holds_conditionally_on_usage_form
    J-5: control_passes
  read_sibling_reports: false
  blind_from_respected: true
  sources_read: see attestation.yaml
```
