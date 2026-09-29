# Blind textual audit: which quantity does Nagao 2015/984 Proposition 5 bound?

- Role: validator (independent, blind; `review-adversarial`)
- Date: 2026-09-16
- Primary source (the only one relied on): `inputs/NAGAO-2015-984/paper_fulltext.md`,
  sha256 `337fae555450162e56432ee137d0cb4bb20e2bd901c29f69b38a2f949e913218`
  (recomputed; matches `paper_fulltext.md.sha256`). Provenance: `retrieved`,
  read in full by this validator. Line numbers below are line numbers of that
  file. Quotations are verbatim from the extraction, including its ligature and
  glyph artifacts (`ﬁ`, `(cid:48)` = prime, `(cid:80)` = Σ, `(cid:54)=` = ≠,
  `(cid:189)` = brace).
- Compute used: none beyond file reads, one `sha256sum`, directory listings.
- The header comment at lines 1–39 is the extractor's own summary, not the
  paper. I read it but rely on nothing in it; every finding below is anchored
  in the paper body (line 41 onward).

## Notation used in this report

- `G` := the Weil-descended S3 polynomials `{F↓_{v,j} | 1 ≤ j ≤ n, F ∈ EQS3(m,R)}`.
- `S_fe` := the field equations `{X_ij^p − X_ij}`.
- `EQS4 = G ∪ S_fe` (Definition 8, quoted under Q1).
- `d_F(·)` := the TRUE first fall degree of Definition 5.
- `d'_F(·)` := the FAKE first fall degree of Definition 6.

## Q1. Which quantity does Proposition 5 bound?

**Answer.** Proposition 5, as stated, bounds the TRUE first fall degree
`d_F(EQS4)` — the Definition 5 quantity of a generating set that contains the
field equations. The text determines this by (a) its consistent terminology,
(b) the role the bound plays in Proposition 6 / Assumption 1, and (c) the
template of Lemma 6 → Proposition 2 that the proposition copies. However, the
only p = 2 justification the paper offers, directly or by reference, is a bound
on the FAKE quantity (attributed to Semaev) converted into a true bound via
Lemma 4. So: stated about `d_F`; argued via `d'_F ≤ 4` plus `d_F ≤ d'_F`. The
paper never writes the symbol `d_F`, the word "true", or the word "Fake" in
Proposition 5 itself.

### Evidence

**Statement of Proposition 5** (lines 715–729), with its lead-in and footnote
marker:

```
715|Similarly, solving EQS3 reduces to solving EQS4 and its complexity is estimated as
716|
717|follows; 6
718|
719|Proposition 5. First fall degree of EQS4(m,R) is bounded by
720|
721|(cid:189)
722|
723|4
724|3p + 1
725|
726|(p = 2)
727|(p ≥ 3)
728|
729|.
```

**The only justification offered for Proposition 5** is footnote 6 (line 844,
displaced to the end by the extractor):

```
844|6 The situation is the same as the Semaev’s case. So, we omit the proof.
```

**Definition of EQS4** (lines 709–713) — note `∪ Sf e`: the field equations are
inside the generating set:

```
709|Deﬁnition 8 (EQS4). EQS4(m,R) is the equations system obtained by Weil descent from
710|each equations in EQS3(m,R) and ﬁeld equations.
711|i,e., EQS4(m,R) := {F ↓
712|
713|−→v ,j | 1 ≤ j ≤ n, F ∈ EQS3(m,R)} ∪ Sf e where −→v = (v1, .., vN ).
```

EQS3 (lines 692–696), for completeness:

```
692|Deﬁnition 7 (EQS3). EQS3(m,R) consists of the m − 1 equations
693|
694|S3(X1, X2, U1) = 0, S3(U1, X3, U2) = 0, ..., S3(Um−3, Xm−1, Um−2) = 0, S3(Um−2, Xm, x(R)) = 0,
695|
696|where variables Xi moves in Vi and Ui in Fpn.
```

The descended polynomials `F↓` are, by Definition 3, defined already reduced
modulo the field equations (line 262: `xN jαj) mod Sf e.`), and `S_fe` is
defined at lines 232–236:

```
232|(1 ≤ i ≤ N, 1 ≤ j ≤ ji). Put the set of ﬁeld equations by
233|
234|Sf e := {X p
235|
236|ij − Xij | 1 ≤ i ≤ N, 1 ≤ j ≤ ji}.
```

**Definition 5 — the TRUE first fall degree** (lines 398–410):

```
398|Deﬁnition 5 (First fall degree). Let K be a ﬁeld and f1, ..., fM ∈ K[X1, ..., XN ]. First
399|fall degree of {f1, ..., fM } is the minimal integer dF satisfying the following.
400|There exists g1, ..., gM ∈ K[X1, ..., XN ] such that
401|1) maxi{deg gifi} ≥ dF ,
402|i=1 gifi) < dF ,
403|2) deg(
404|(cid:80)M
405|
406|(cid:80)M
407|
408|3)
409|
410|i=1 gifi (cid:54)= 0.
```

Reconstructed: `d_F` is the minimal integer such that there exist `g_1..g_M`
with (1) `max_i deg(g_i f_i) ≥ d_F`, (2) `deg(Σ g_i f_i) < d_F`,
(3) `Σ g_i f_i ≠ 0`. Degrees are in the polynomial ring; nothing is reduced.

**Definition 6 — the FAKE first fall degree** (lines 430–448):

```
430|Deﬁnition 6 (Fake ﬁrst fall degree). Let f1, ..., fM ∈ Fp[X1, ..., XN ] and let Sf e := {X p
431|i −
432|Xi | 1 ≤ i ≤ N } be the set of ﬁeld equations Fake ﬁrst fall degree of {f1, ..., fM } ∪ Sf e is the
433|minimal integer d(cid:48)
434|
435|F satisfying the following.
436|
437|There exists g1, ..., gM ∈ K[X1, ..., XN ] such that
438|
439|1) maxi{deg gifi mod Sf e} ≥ dF ,
440|i=1 gifi mod Sf e) < dF ,
441|2) deg(
442|(cid:80)M
443|
444|(cid:80)M
445|
446|i=1 gifi (cid:54)≡ 0 mod Sf e.
447|
448|3)
```

Reconstructed: `d'_F` is the minimal integer such that there exist
`g_1..g_M` (multipliers on the `f_i` only — the field equations get no
multipliers) with (1) `max_i deg(g_i f_i mod S_fe) ≥ d`, (2)
`deg(Σ g_i f_i mod S_fe) < d`, (3) `Σ g_i f_i ≢ 0 mod S_fe`. Degrees are
measured after reduction modulo the field equations. Two textual defects in
this definition as extracted: conditions (1) and (2) are written with `dF`,
not `d'F` (no `(cid:48)`), and the multipliers are drawn from `K[...]`
although `K` is not introduced in this definition. I read both as slips.

The paper introduces Definition 6 as the community's error (lines 426–428):

```
426|Many researchers misunderstand the deﬁnition of ﬁrst fall degree and use this assumption
427|
428|and estimation of the complexity using the following FAKE version.
```

**Why "First fall degree" in Proposition 5 means Definition 5.** Every place
the paper means the Definition 6 quantity it says "Fake": lines 428, 430,
432, 458, 461–462, 513, 580. Unqualified "first fall degree" is used for the
Definition 5 quantity in Assumption 1 (lines 416–417), Lemma 2 (lines
423–424), Lemma 4 (line 510), Lemma 6's statement (lines 540–542),
Proposition 2 (line 587) and Proposition 5 (line 719).

**Why the role of the bound requires the true quantity.** Proposition 5
feeds Proposition 6 (lines 731–742) through "the first fall degree
assumption", which is Assumption 1, stated for `d_F`:

```
416|Assumption 1 {f1, ..., fM } Degree of the polynomial appears in the Gr¨obner basis compu-
417|tation (by F4 algorithm) of {f1, ..., fM } is ≤ dF .
```

```
423|Lemma 2. The complexity of Gr¨obner basis computation (by F4 algorithm) of {f1, ..., fM }
424|is ≤ O(N dF w), where w ∼ 2.7 is the linear algebra constant.
```

```
731|Proposition 6. Under the ﬁrst fall degree assumption, the complexity of solving EQS4(m,R)
732|is bounded by
733|
734|(cid:189)
735|
736|O((nm)4w)
737|O((nm)(3p+1)w)
738|
739|(p = 2)
740|(p ≥ 3)
```

The exponent `4w` in Proposition 6 is `d_F · w` from Lemma 2 with `d_F ≤ 4`
from Proposition 5. The quantity Proposition 5 bounds is therefore the
quantity Assumption 1 and Lemma 2 are written in, which is `d_F`.

**Why the paper's argument nonetheless establishes only the fake bound.**
Footnote 6 routes Proposition 5 to "the Semaev's case", i.e. Proposition 2
(lines 585–600) with its footnote 5 (line 690):

```
585|From this proposition, we have the following:
586|
587|Proposition 2 (Semaev [14] and its generalization to p ≥ 3). First fall degree of
588|EQS2(m,R)
589|
590|5 is bounded by
591|
592|(cid:189)
593|
594|4
595|3p + 1
596|
597|(p = 2)
598|(p ≥ 3)
```

```
690|5 Assume Sf e ⊆ EQS2(m,R)
```

and the p = 2 case of Proposition 2 is, in the paper's own words, Semaev's,
established for the FAKE quantity (lines 450–459; the extractor interleaved
two lines, reconstruction follows):

```
452|In [14], Semaev says from the equation S3(x, u, RX ) = 0, where x =
453|
454|i=1 xiαi u =
455|i=1 uiαi and RX ∈ Fpn , the relations of low ﬁrst degree do not appears. Considering
456|F ≤ 4. He uses
457|
458|xuS3(x, u, RX ), one can easily have the relation that its Fake ﬁrst fall degree d(cid:48)
459|the true deﬁnition of ﬁrst fall degree.
```

Reconstructed: "In [14], Semaev says from the equation S3(x, u, R_X) = 0,
where x = Σ x_i α_i, u = Σ u_i α_i and R_X ∈ F_{p^n}, the relations of low
first degree do not appears. Considering xu·S3(x, u, R_X), one can easily
have the relation that its Fake first fall degree d'_F ≤ 4. He uses the true
definition of first fall degree." The bridge from fake to true is then
supplied by the next paragraph and Lemma 4 (lines 461–463, 510–515, quoted
under Q2):

```
461|In [11], the author shows the following lemma and it has no problem to use Fake ﬁrst fall
462|
463|degree instead of use true ﬁrst fall degree.
```

The abstract says the same in plainer words (lines 61–63):

```
61|Moreover, using the authors results in [11], in the case of the ﬁeld characteristic ≥ 3,
62|the ﬁrst fall degree of desired equation system is estimated by ≤ 3p + 1. (In p = 2 case,
63|Semaev shows it is ≤ 4. But it is exceptional.)
```

The p ≥ 3 branch follows the identical template: Lemma 6 (lines 540–542)
states a bound on the (true) "first fall degree of ... ∪ Sf e", and its proof
(lines 570–583) bounds the Fake quantity and invokes Lemma 4:

```
540|Lemma 6. Let F = F (X1, ..., Xn) be a polynomial in Fpn[X1, .., Xn]. The ﬁrst fall degree of
541|the equations system {F ↓
542|j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} ∪ Sf e is heuristically ≤ (p − 1)n + deg F .
```

```
580|Fake ﬁrst fall degree of {F ↓
581|from Lemma 4, we have this lemma.
582|
583|j (∈ Fp[{Xij}]) | 1 ≤ j ≤ n} is bounded by ≤ (p − 1)n + deg F and
```

So the paper's pattern is fixed: statements about the true first fall degree,
proofs that bound the fake one and cite Lemma 4. Proposition 5 inherits that
pattern by footnote 6.

**Is there a reading under which Proposition 5 is about `d'_F`?** Only if one
discounts the paper's terminology. Definition 6 attributes the fake quantity
to a set of the form `{f_i} ∪ S_fe`, and EQS4 has exactly that form, so the
*argument* of the phrase "first fall degree of EQS4" does not disambiguate;
only the presence or absence of "Fake" does, and Proposition 5 omits it. A
reader who believes Proposition 5 is about `d'_F` has on their side the fact
that `d'_F ≤ 4` is what the paper's borrowed argument actually delivers. I
consider that a reading of the proof, not of the statement.

**Confidence.** High (I would put it near 0.85–0.9) that the text intends the
true quantity. The residual is that the proposition itself is silent and the
paper's evidence for it is a fake-quantity bound.

## Q2. Direction of the inequality, where stated, and whether proven here

**Answer.** `d_F ≤ d'_F`: the true first fall degree is at most the fake one;
the fake quantity is an upper bound on the true one. It is stated as Lemma 4
(lines 510–515). It is NOT proven in this paper. Lemma 4 is offered as a
consequence of Lemma 3, which is attributed to reference [11] (Nagao, ePrint
2013/549), and the paper explicitly declines to give Lemma 3's proof.

### Evidence

```
510|Lemma 4. Let f1, ..., fM ∈ Fp[X1, ..., XN ]. Put dF by the ﬁrst fall degree of {f1, ..., fM } and
511|put d(cid:48)
512|
513|F by the Fake ﬁrst fall degree of {f1, ..., fM } ∪ Sf e. Then dF ≤ d(cid:48)
514|
515|F .
```

Reconstructed: "Put d_F by the first fall degree of {f_1, ..., f_M} and put
d'_F by the Fake first fall degree of {f_1, ..., f_M} ∪ S_fe. Then d_F ≤ d'_F."

Its only support in this text (lines 461–463, 467, 507–508):

```
461|In [11], the author shows the following lemma and it has no problem to use Fake ﬁrst fall
462|
463|degree instead of use true ﬁrst fall degree.
```

```
467|Lemma 3 ([11]). Let F = F (X1, ..., XN ) be a polynomial in Fp[X1, .., XN ] such that F ≡
```

```
507|Proof of this Lemma is complicated and not constructive.
508|From this lemma, we have the following:
```

No derivation of Lemma 4 from Lemma 3 is written out; "From this lemma, we
have the following" is the entire argument. Reference [11] is at lines
946–948:

```
946|11. K. Nagao, Equations System coming from Weil descent and subexponential attack for algebraic
947|
948|curve cryptosystem, https://eprint.iacr.org/2013/549
```

Lemma 3's statement is badly scrambled by the extractor (lines 465–493) but
its content is recoverable from Example 1 (lines 495–505): a polynomial
`F ≡ 0 mod S_fe` can be rewritten as `Σ f_i^new · (X_i^p − X_i)` with
`deg f_i^new ≤ deg F − p`, i.e. membership in the field-equation ideal can
always be certified without degree inflation. That is the ingredient that
lets a cancellation "mod S_fe" be realised as a genuine polynomial-ring
cancellation with field-equation multipliers of controlled degree.

**A note on the left-hand side.** Lemma 4 literally puts `d_F` on
`{f_1..f_M}` *without* the field equations, and `d'_F` on `{f_1..f_M} ∪ S_fe`.
But every application in the paper — Lemma 6 (whose conclusion is about
`{F↓_j} ∪ S_fe`), footnote 5 ("Assume Sf e ⊆ EQS2"), and Definitions 4 and 8
(`∪ Sf e`) — applies it to a true first fall degree of a system that
*contains* the field equations as generators. This matters; see Q4, item 2.
For the purposes of Q3 it does not: adding generators can only lower a true
first fall degree (any fall for `G` is a fall for `G ∪ S_fe` with zero
multipliers on the new generators), so under either reading of Lemma 4's
left-hand side, `d_F(EQS4) = d_F(G ∪ S_fe) ≤ d'_F`.

## Q3. Does a FAKE measurement on a descended EQS4 instance at p = 2 refute or confirm Proposition 5?

Set-up as posed: an instrument computes `d'_F` of one EQS4 instance at p = 2
in the Boolean quotient ring (Macaulay-matrix ranks over GF(2) at successive
degrees). Proposition 5 has no explicit quantifier; I read it, as its use in
Proposition 6 and Theorem 1 requires, as a claim about every EQS4(m,R)
instance (every m, R, curve, V, and coset representatives v_i). A single
instance therefore can refute it and can at most confirm it for that
instance.

Two facts from the text are used throughout:

- (F1) Lemma 4: `d_F ≤ d'_F` (Q2; asserted, proven elsewhere).
- (F2) The paper's stated route to the p = 2 bound is `d'_F ≤ 4`
  (Semaev, lines 452–459) followed by (F1) (lines 461–463), extended to EQS4
  by footnote 6 (line 844).

### Reading A — Proposition 5 bounds the TRUE `d_F(EQS4)` (the reading I hold)

**Observed `d'_F > 4`. Does it refute Proposition 5? No.**

1. Proposition 5 (reading A) asserts `d_F(EQS4) ≤ 4`.
2. The observation asserts `d'_F(EQS4) > 4`.
3. (F1) gives `d_F ≤ d'_F`. The conjunction `d_F ≤ 4 < d'_F` is consistent
   with (F1); nothing forces `d_F` upward. The inequality would have to run
   the other way (`d'_F ≤ d_F`) for a large fake value to push the true value
   above 4, and the paper states it does not.
4. Hence the observation is logically compatible with Proposition 5 and
   refutes nothing about `d_F`.
5. What it *does* contradict is (F2), the paper's justification, for that
   instance: the paper's proof-by-analogy asserts that the Semaev-style
   argument yields `d'_F ≤ 4` for EQS4 ("the situation is the same"). An
   instance with `d'_F > 4` shows the omitted proof cannot go through as
   described for that instance. The correct report is then "Proposition 5's
   conclusion is untouched; the paper's argument for it fails on this
   instance; the proposition stands unproven, not refuted." To refute
   Proposition 5 under reading A one must measure the TRUE quantity: a
   Macaulay computation in the polynomial ring `F_2[X_ij]` with the field
   equations as generator rows and degrees taken before reduction, showing no
   fall at any degree ≤ 4. A Boolean-ring computation cannot do this, for
   the structural reason given in Q4, item 1.

**Observed `d'_F ≤ 4`. Does it confirm Proposition 5? Yes, for that
instance, conditional on Lemma 4.**

1. The observation asserts `d'_F(EQS4) ≤ 4`.
2. (F1): `d_F ≤ d'_F ≤ 4`.
3. Hence `d_F(EQS4) ≤ 4` for this instance — exactly Proposition 5's
   conclusion, for this instance.
4. Conditions: (a) the step uses Lemma 4, which the paper asserts and does
   not prove; anyone relying on the confirmation is relying on [11]. (b) It
   confirms one instance of a universal claim; it does not establish
   Proposition 5. (c) The observation is robust to instrument details in a
   way the `> 4` observation is not: a fall at degree ≤ 4 is a *witness*
   (explicit multipliers whose reduced combination drops degree), and any
   genuine Definition-6 fall at degree d ≤ 4 gives `d'_F ≤ d ≤ 4` because
   `d'_F` is a minimum. Absence of a fall is a completeness claim about a
   search.

### Reading B — Proposition 5 bounds the FAKE `d'_F(EQS4)`

**Observed `d'_F > 4`: refutes Proposition 5**, at that instance, and one
instance suffices against a universal bound — *provided* the instrument's
quantity is the Definition 6 quantity: same generator set `G` (the reduced
descents of Definition 3), multipliers on `G` only, degrees measured after
reduction mod `S_fe`, and the same notion of fall (see Q4, item 3, on the
`≥`/`=` ambiguity and on trivial falls). If the instrument's notion of "fall"
is narrower than Definition 6's (e.g. it counts only new low-degree elements
not already in the lower-degree row space), its value is an upper bound on
the paper's `d'_F`, and "instrument > 4" does not by itself give
"Definition-6 `d'_F` > 4".

**Observed `d'_F ≤ 4`: confirms Proposition 5** for that instance, directly,
no lemma needed.

### Reading C — the text does not determine which quantity

Then the `> 4` observation refutes Proposition 5 under reading B only and
never under reading A, and the honest report is: "refutes the paper's stated
justification (F2) for this instance; refutes Proposition 5 only if it is
read as a fake-quantity bound; leaves the true-quantity bound open." The
`≤ 4` observation confirms the instance under both readings (via Lemma 4
under A). I do not hold reading C — see Q1 — but the two readings agree on
the confirmation direction and disagree only on the refutation direction,
so the operational consequence of the ambiguity is confined to how a `> 4`
observation may be described.

### Summary table

| observation on one EQS4 instance, p = 2 | reading A (true `d_F`) | reading B (fake `d'_F`) |
| --- | --- | --- |
| `d'_F > 4` | does NOT refute Prop. 5; contradicts the paper's proof route (F2) for that instance | refutes Prop. 5 (if instrument = Definition 6) |
| `d'_F ≤ 4` (witnessed fall) | confirms Prop. 5 for that instance, via Lemma 4 (unproven here) | confirms Prop. 5 for that instance |

## Q4. Things in the passages that bear on the answer and are easy to miss

1. **The field equations are INSIDE the generating set Proposition 5 speaks
   about, and that makes the true quantity strictly weaker than the fake
   one.** Definition 8 (line 713, `∪ Sf e`) and footnote 5 (line 690, "Assume
   Sf e ⊆ EQS2(m,R)") put `S_fe` among the generators. Under Definition 5
   this means the field equations may carry their own multipliers and
   degrees are taken in the polynomial ring before any reduction. Consider a
   reduced cubic `f` over F_2 all of whose cubic monomials are divisible by
   `X_1`, e.g. `f = X_1X_2X_3 + X_1X_4X_5 + (lower)`. Take `g = X_1` on `f`
   and `h_1 = X_2X_3 + X_4X_5` on `X_1^2 + X_1`. Both products have degree 4;
   their sum is `X_1X_2X_3 + X_1X_4X_5 + X_1·(lower)`, of degree 3, and is
   nonzero. That is a true fall at degree 4 under Definition 5 for
   `{f} ∪ S_fe`. In the Boolean ring the same multipliers give
   `X_1 f mod S_fe`, of degree 3 with no drop: it is not a fake fall.
   Degree drops caused purely by `X^2 → X` count toward `d_F` and are
   invisible to `d'_F`. This is the mechanism behind `d_F ≤ d'_F`, and it is
   why a Boolean-ring Macaulay instrument is structurally unable to exhibit
   `d_F > 4`: it never sees the falls that could make `d_F` small. It also
   means Proposition 5 under reading A is a weaker claim than the community's
   `d'_F ≤ 4`. The direction of Lemma 4 is unaffected by inside/outside (see
   the monotonicity remark in Q2), so Q3's conclusions stand either way; what
   changes is the *size* of the gap the `> 4` observation cannot cross.

2. **Lemma 4's literal statement and its use differ on exactly this point,
   and the literal form is false under the standard definition.** Lemma 4
   (line 510) puts `d_F` on `{f_1..f_M}` with the field equations outside.
   Hand-checkable example over F_2: `f_1 = X_1X_2 + X_3`, `f_2 = X_1 + X_2`.
   Fake: `g = (1, X_2)` gives `f_1 + X_2 f_2 ≡ X_2 + X_3 mod S_fe`, reduced
   products of degree 2, combination of degree 1, so `d'_F = 2`. True, field
   equations outside, with condition (1) read as equality: any combination
   with products of degree exactly 2 is `c·f_1 + (a + b_1X_1 + b_2X_2 +
   b_3X_3)·f_2`, whose degree-2 part `c X_1X_2 + b_1 X_1^2 + (b_1+b_2)X_1X_2
   + b_2 X_2^2 + b_3 X_1X_3 + b_3 X_2X_3` vanishes only when
   `b_1 = b_2 = b_3 = c = 0`; so there is no true fall at degree 2, while
   `(X_1+X_2)·f_1 + X_1X_2·f_2 = (X_1+X_2)X_3` is one at degree 3. Thus
   `d_F({f_1,f_2}) = 3 > 2 = d'_F`, contradicting Lemma 4 as written. With
   the field equations inside, `f_1 + X_2 f_2 + 1·(X_2^2 + X_2) = X_2 + X_3`
   is a true fall at degree 2 and the inequality holds. The paper's
   applications (Lemma 6, footnote 5, Definitions 4 and 8) all take the
   inside form, which is the form Q3 needs; a reader who transcribes Lemma 4
   literally and applies it to `G` alone is relying on a false statement.
   (I have not proven the inside form in general under the equality
   definition; I have checked that the argument sketched from Lemma 3 goes
   through when condition (1) is read as `≥`, and that it is exactly the
   inside form the paper uses.)

3. **Condition (1) of both definitions reads `≥ dF`, not `= dF`, and
   Definition 6's conditions name `dF` rather than `d'F`** (lines 401, 439,
   440). Taken literally, `≥` degenerates both quantities: for any nonzero
   ideal element `r` of degree `e` produced by a combination whose products
   have higher degree, every `d` with `e < d ≤ max deg` satisfies the
   conditions, so the minimum is `e + 1`; a zero-dimensional system with a
   unique F_2-solution (the normal case for a descended EQS4) has linear
   elements in its ideal, so the literal true `d_F` would be ≤ 2 and
   Assumption 1 would be false. The paper cannot mean that, and the
   standard definition (recalled: Petit–Quisquater 2012 — `recalled`,
   supports nothing) uses equality. Neither definition excludes trivial
   Koszul-type falls either: with `S_fe` inside, `g_i = X_j^2 + X_j` on a
   cubic `f_i` and `h_j = f_i + 1` on the field equation give
   `Σ = X_j^2 + X_j`, a "fall" from degree 5 to degree 2, so the literal
   true `d_F` of any cubic system ∪ `S_fe` at p = 2 is ≤ 5 and Proposition
   5's bound of 4 sits one degree below a trivial ceiling. Any instrument
   claiming to compute Definition 6 must decide `≥` vs `=` and whether
   trivial falls count; the paper does not say. Whether `≥` is in the PDF or
   is an extraction artifact is not determinable from the frozen text alone;
   I report it as an extraction limit.

4. **The generators are the reduced descents.** Definition 3 defines `F↓`
   with `mod Sf e` (line 262), and line 274 says "(when p = 2 degree 3
   polynomials can be taken)". For the fake quantity the representative is
   irrelevant; for the true quantity it is not (degree before reduction),
   and Definition 3 fixes it as the reduced, degree-3 form at p = 2.

5. **The paper establishes no bound of either kind for EQS4 itself.** The
   p = 2 bound is borrowed from Semaev for the fake quantity (lines 452–459,
   abstract lines 62–63, Proposition 2's title "(Semaev [14] and its
   generalization to p ≥ 3)"), converted with a lemma proven elsewhere
   (lines 461–463, 507), and transferred to EQS4 by footnote 6 with the
   proof omitted (line 844). The p ≥ 3 bound rests on Lemma 6, which is
   stated as holding "heuristically" (line 542) with footnote 4 "We use
   heuristic argument only here" (line 578); Proposition 5 does not carry
   the word "heuristically" though its p ≥ 3 branch inherits it. The
   sentence "He uses the true definition of first fall degree" (line 459)
   is about Semaev's *statement*, not about what Semaev's argument
   delivers, which the preceding sentence identifies as the fake bound.

6. **EQS4 differs from EQS2 by the coset shifts `v_i`** (Definition 8, line
   713; footnote 1, lines 285–290). The shift adds lower-degree terms after
   descent and leaves the top-degree structure of each descended `S3`
   unchanged, which is presumably what footnote 6 relies on; the paper does
   not argue it. An instrument on a "descended EQS4 instance" must include
   the `v_i`; that is part of the instance, not a deviation.

## What I did not read

I confirm that I did not open, grep, or otherwise read any of the following:

- `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`
- `ledger/decisions/DEC-20260915-94855e.yaml`
- `ledger/corrections/CORR-20260915-b7ca0c.yaml`
- `ledger/decisions/DEC-20260913-8d19e5.yaml`
- `ledger/proposals/IDEA-20260913-352163.yaml`
- `knowledge/literature/KN-LIT-c5dceb.md`
- `knowledge/literature/KN-LIT-ebd657.md`
- anything else under `ledger/`, `knowledge/`, `experiments/`, or the other
  `coordination/review/*` directories.

I also did not open `inputs/NAGAO-2013-549/paper_fulltext.md` or
`inputs/SEMAEV-2015-310/paper_fulltext.md` (I listed those directories to
learn that frozen copies exist, nothing more), nor the PDF, `provenance.json`
or `source_record.yaml` in `inputs/NAGAO-2015-984/`. My answers derive from
`inputs/NAGAO-2015-984/paper_fulltext.md` alone, plus hand algebra on toy
examples written in this report. I did not run a solver, an algebra system,
or any CPU-intensive process.

## What would settle any residual ambiguity

1. **Q1 referent.** The text itself has nothing further; the residual is
   authorial intent. The nearest external check is [11] (frozen at
   `inputs/NAGAO-2013-549/`): if Nagao's own definitions there use equality
   and his Lemma 3/4 there is stated with the field equations inside the
   left-hand system, that confirms the paper's "true, with `S_fe` inside"
   convention; if his statement of the first fall degree assumption there is
   in terms of the true quantity, Proposition 5's referent is settled.
   Reading [14] (frozen at `inputs/SEMAEV-2015-310/`) would settle whether
   Semaev's `≤ 4` is stated for the fake or true quantity, which is what
   line 459 gestures at. A `retrieved` reading of either by an agent that
   records itself in `verified_by` is required before either can be cited.
2. **Q3 confirmation direction.** It rests on Lemma 4 in the inside form
   under the equality definition. Either a written proof of
   `d_F(G ∪ S_fe) ≤ d'_F(G ∪ S_fe)` from Lemma 3 (checking that the
   polynomial-ring fall it constructs has maximum product degree exactly
   `d'_F`, not merely `≥ d'_F`), or a direct computation of the true `d_F`
   in the polynomial ring with field-equation rows, would remove the
   dependence.
3. **Instrument fidelity.** A written operationalization of Definition 6
   stating: generator set (reduced descents of Definition 3, with `v_i`),
   multipliers on `G` only, degree after reduction, `=` vs `≥` in condition
   (1), and treatment of trivial falls. Without it, an observed `> 4` cannot
   be equated with "Definition-6 `d'_F > 4`" even under reading B.
4. **Extraction.** Confirming from the PDF glyphs whether condition (1)
   reads `≥` or `=` and whether Definition 6's conditions carry the prime.
   This is a one-line check of the frozen PDF, not a research question.

## Verdict on decidability

- Q1: **decided by the text**, with high confidence (≈ 0.85–0.9): Proposition
  5 bounds the true `d_F` of `G ∪ S_fe`; the paper's supporting argument
  bounds `d'_F` and relies on Lemma 4 to cross.
- Q2: **decided**: `d_F ≤ d'_F` (Lemma 4, lines 510–515), asserted here,
  proven in [11] if anywhere.
- Q3: **decided as a matter of logic given Q1 and Q2**: an observed
  `d'_F > 4` does not refute Proposition 5 (it undermines the paper's
  justification); an observed `d'_F ≤ 4` confirms the instance, conditional
  on Lemma 4. Under the alternative (fake) reading the `> 4` observation
  refutes, subject to instrument fidelity; the `≤ 4` observation confirms
  under both readings.

```yaml
review_attestation:
  task_id: null            # blind textual audit; no TASK id was supplied
  joints_owned:
    - "Nagao 2015/984 Proposition 5: which first-fall-degree quantity it bounds"
    - "Lemma 4 direction and proof status"
    - "Logical consequence of a fake-quantity measurement (> 4 / <= 4) for Proposition 5"
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - inputs/NAGAO-2015-984/paper_fulltext.md
    - inputs/NAGAO-2015-984/paper_fulltext.md.sha256
    - templates/research-records.md   # review_attestation field names only
  read_sibling_reports: false
  blind_from_respected: true
  verdict: holds           # on the joints owned: the inequality runs d_F <= d'_F,
                           # so a fake value > 4 cannot refute a true-quantity bound;
                           # not a verdict on Proposition 5's truth
```
