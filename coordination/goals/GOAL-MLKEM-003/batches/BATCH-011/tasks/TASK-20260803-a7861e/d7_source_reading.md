# D7 source reading: where the source puts the `d_lsc` integral

- Task: `TASK-20260803-a7861e` (executor) | Batch: `BATCH-011` | Goal: `GOAL-MLKEM-003`
- Question settled here: **does the source define `D` with the `d_lsc` integral INSIDE
  `min(1,·)` or OUTSIDE it, and does (4.18) agree with (4.22)?**
- Claim tier: **toy**. No ML-KEM security claim in either direction. AGENTS.md rule 12
  is UNMET and UNWAIVED; `EV-MLKEM-011`, `EV-MLKEM-013`, `EV-MLKEM-017` keep their
  status and nothing here touches them.
- Role boundary: this is an **observation record**. It does not conclude that
  Approximation 4.9 is validated or refuted, that BATCH-010's Check B was or was not
  worth running, or that the BATCH-009 implementation is or is not at fault. Those
  judgements belong to the Red Team and the Coordinator.

---

## 0. Provenance and method

| field | value |
|---|---|
| source document | `experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf` (READ ONLY; never modified) |
| sha256 recomputed at run time | `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` (matches the handoff's expected hash) |
| title / authors (PDF metadata) | *Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber* — Kevin Carrier, Charles Meyer-Hilfiger, Yixin Shen, Jean-Pierre Tillich |
| pages | 37 PDF pages; printed folio = PDF index − 1 throughout (verified page by page in the run log's FOLIO CHECK) |
| extractor | `pypdf` 6.14.2, Python 3.11.15, Linux-6.18.5-x86_64-with-glibc2.39 |
| command | `python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-011/tasks/TASK-20260803-a7861e/extract_pages.py --outdir <scratch>` |
| repo commit at run time | `4f4e46337b1f4ff580e72e5e39909ebb4d6433cb`; tree dirty only in this task's own directory |
| wall clock | 4.47 s; memory cap `ulimit -v 4194304` (4 GB) applied |
| sampling / network | ZERO NEW SAMPLING, NO NETWORK. Text extraction from an already-vendored file only. |

**Quotation convention.** Every quoted block below is the extractor's output,
unedited. Two independent `pypdf` modes are shown for the two decisive equations:

- `plain` — default `extract_text()`, one text object per line, so a display formula
  appears as a vertical token stream in PDF content order;
- `layout` — `extraction_mode="layout"`, which preserves horizontal position, so the
  nesting of a display formula is visible in two dimensions.

C0 control bytes (0x00–0x08, 0x0b–0x1f) occur where a math-font glyph carries no
Unicode mapping; in this document they sit at the **scaled delimiters** of display
formulas. They are rendered `<U+00XX>` rather than stripped. Tab (0x09) is left as a
tab and therefore prints as whitespace. Line numbers are the extractor's, per page and
per mode. No character has been added, removed, or reordered inside a quoted block.

**Quotation self-check.** All 14 line-numbered blocks below were checked back against
the extracted page text programmatically (exact string comparison per line, after the
same escaping, trailing whitespace stripped on both sides), against *every* extracted
(page, mode) pair rather than only the intended one: 14/14 match. Four of them failed
on the first pass — three had been transcribed from a terminal render that silently
dropped invisible C0 delimiter bytes, one carried wrong line numbers — and were
regenerated from the extractor output. That failure and its repair are recorded in
`d7_findings.json` under `provenance.quote_verification`.

---

## 1. Verbatim (4.18) — Model 4.7, definition of `D`

**Locus: PDF page 23, printed page 22, equation (4.18), inside Model 4.7.**

`plain` mode, lines 22–43:

```
  22| Model 4.7. We assume that F (lsc)
  23| gsenu
  24| <U+0000>
  25| G⊤ fsfft
  26| <U+0001>
  27| approximately follows the same distribution asD +
  28| N (0, N/2), where N (0, N/2) denotes a normal distribution with mean0 and standard deviationp
  29| N/2, and
  30| D
  31| △
  32| = N ·
  33| Z ∞
  34| 0
  35| ψlsc(dlsc) ·
  36| <U+0012>
  37| max
  38| i,j : Ni,j =1
  39| (Φdlsc (i, j))
  40| <U+0013>
  41| ddlsc. (4.18)
  42| We recall thatψlsc refers to the probability density function ofN (µlsc, σ2
  43| lsc).
```

`layout` mode, lines 11–18 (same page, same equation):

```
  11| Model4.7.Weassumethat F(lsc)             <U+0000>G⊤fsfft<U+0001>approximatelyfollowsthesamedistributionas D +
  12|                                      gsenu
  13| N(0,N/2),where N(0,N/2)denotesanormaldistributionwithmean 0andstandarddeviation
  14| pN/2,and
  15|                                     Z ∞
  16|                           D △=N·                       i,j :Ni,j=1(Φdlsc(i,j))maxddlsc.              (4.18)
  17|                                      0   ψlsc(dlsc)·
  18| Werecallthat ψlscreferstotheprobabilitydensityfunctionof N(µlsc,σ2lsc).
```

Reading the two modes together, (4.18) is

> D ≜ N · ∫₀^∞ ψ_lsc(d_lsc) · [ max_{i,j : N_{i,j}=1} ( Φ_{d_lsc}(i,j) ) ] dd_lsc

with the scaled bracket pair `<U+0012> … <U+0013>` enclosing exactly
`max_{i,j : N_{i,j}=1}(Φ_{d_lsc}(i,j))`, and `dd_lsc` closing the integral that opens
at `∫₀^∞ ψ_lsc(d_lsc)·`.

**(4.18) contains no `min(1,·)`.** Its only nonlinearity is the `max` over pairs, and
the `d_lsc` integral is **outside** that `max`.

---

## 2. Verbatim (4.22) — Approximation 4.9, `P_wrong`

**Locus: PDF page 23, printed page 22, equation (4.22), inside Approximation 4.9
(Wrong Guess), whose statement opens at (4.21).**

`plain` mode, lines 85–127:

```
  85| Approximation 4.9 (Wrong Guess).If we make the wrong guess(gsenu, fsfft) ̸= (senu, sfft), then
  86| Pwrong
  87| △
  88| = P
  89| <U+0010>
  90| F (lsc)
  91| gsenu
  92| <U+0000>
  93| G⊤ fsfft
  94| <U+0001>
  95| ≥ T
  96| <U+0011>
  97| (4.21)
  98| ≈
  99| Z +∞
 100| −∞
 101| Z +∞
 102| 0
 103| min
 104|
 105| 1,
 106| Z
 107| E(T −t)
 108| λ(x)µ(y)d(x, y)
 109| !
 110| · e
 111| −t2
 112| N − (dlsc−µlsc)2
 113| 2σ2
 114| lsc
 115| πσlsc
 116| √
 117| 2N
 118| ddlsc dt (4.22)
 119| where
 120| E(T − t)
 121| △
 122| =
 123| <U+0008>
 124| (x, y) ∈ R2
 125| + : N · Φdlsc (x, y) ≥ T − t
 126|
 127| , (4.23)
```

(Line 104 is a single space `U+0020` — the opening scaled parenthesis of `min`; line
109 is `!`, the closing scaled parenthesis; line 126 is a tab `U+0009`, the closing
brace of the set in (4.23). Codepoints verified individually.)

`layout` mode, lines 35–46 (same page, same equation):

```
  35| Approximation4.9(WrongGuess).    Ifwemakethewrongguess (gsenu,fsfft)̸= (senu,sfft),then
  36| 
  37|                   △=P          <U+0000>G⊤fsfft<U+0001>≥T
  38|           Pwrong         F(lsc)gsenu                                                                      (4.21)
  39|                      Z  +∞  Z  +∞           Z                          !     −t2
  40|                                                                               N −(dlsc−µlsc)22σ2lsc
  41|                   ≈                       1,                              · e  πσlsc√2N    ddlsc dt   (4.22)
  42|                       −∞     0      min       E(T−t)λ(x)µ(y)d(x,y)
  43| 
  44| where
  45|                           E(T −t) △=<U+0008>(x,y)∈R2+  : N·Φdlsc(x,y)≥T −t	,               (4.23)
  46| 
```

Reading the two modes together, (4.22) is

> P_wrong ≈ ∫_{−∞}^{+∞} ∫₀^{+∞} min( 1, ∫_{E(T−t)} λ(x)µ(y) d(x,y) ) ·
>   e^{ −t²/N − (d_lsc−µ_lsc)²/(2σ²_lsc) } / ( πσ_lsc √(2N) ) dd_lsc dt

The nesting is fixed by the delimiter glyphs and corroborated by the layout mode: the
argument of `min` **closes** (`!`, line 109 plain / the `!` at layout line 39) before
the Gaussian factor `· e^{…}` begins, and the two integrations `dd_lsc dt` are
**outermost**. The `min`'s argument is the region integral
`∫_{E(T−t)} λ(x)µ(y) d(x,y)` alone. `d_lsc` enters that argument only through the
region `E(T−t)` (4.23), which is defined pointwise in `d_lsc` via `Φ_{d_lsc}`.

**Document-wide check.** The standalone token `min` occurs **exactly twice in the
entire 37-page document**: PDF page 23 line 103 (this equation, (4.22)) and PDF page
25 line 8 (equation (4.28), quoted in §4). In neither occurrence does a `d_lsc`
integral appear inside the `min`.

---

## 3. The answer

**(a) Where the source puts the `d_lsc` integral relative to `min(1,·)`.**

- **(4.22): OUTSIDE.** The `d_lsc` integral (`dd_lsc`, with the Gaussian weight in
  `d_lsc`) is one of the two outermost integrations; `min(1,·)` sits inside it, applied
  at each fixed `d_lsc`.
- **(4.18): the question does not literally apply, because (4.18) contains no
  `min(1,·)`.** What (4.18) does place is the `d_lsc` integral **outside the `max`**,
  i.e. the `d_lsc` average is taken *before* any threshold event is formed. The
  threshold is applied afterwards, to `D` itself (through `P(D > T)`), so on (4.18) as
  written the `d_lsc` integral lies **inside** the survival probability — and hence
  inside whatever `min(1,·)` is later used to approximate that survival probability
  (which is what (4.27)–(4.28) do; see §4).

So the compressed phrasing in validator defect D7 — "(4.18) defines `D` with the
`d_lsc` integral INSIDE" — points at a real structural feature of (4.18), but it is
a *derived* description, not a literal reading: no `min(1,·)` appears in (4.18), and
the operator the `d_lsc` integral is literally outside of is the `max`.

**(b) Does (4.18) agree with (4.22)? NO — not as written.**

The two are inconsistent about *when* `d_lsc` is averaged:

- On (4.18), `d_lsc` is integrated out **inside the definition of `D`**. The resulting
  `D` therefore carries no residual `d_lsc` dependence: it is
  `D = N · E_{d_lsc}[ max_{i,j:N_{i,j}=1} Φ_{d_lsc}(i,j) ]`, random only through the
  `N_{i,j}`.
- (4.22), and the justification that produces it, require the opposite order. (4.27)
  writes "the survival function of `D`, knowing that the achieved decoding distance is
  `d_lsc`", i.e. `P(D > T | d_lsc)`, and the closing display of the justification
  (§4) writes `P(D > T) = ∫₀^∞ ψ_lsc(d_lsc) · P(D > T | d_lsc) dd_lsc`. Both presuppose
  `D` conditioned on a single drawn value of `d_lsc`, i.e.
  `D | d_lsc = N · max_{i,j:N_{i,j}=1} Φ_{d_lsc}(i,j)` — the `max` **outside** the
  `d_lsc` integral, which is the reverse of (4.18).

Conditioning on `d_lsc` a quantity in which `d_lsc` has already been integrated out is
ill-typed, and averaging before versus after a threshold is not the same operation
(`x ↦ 1{x > T}` is not affine), so (4.22) is not obtainable from (4.18) as written.
The two positions coincide only if `max` and `∫ ψ_lsc dd_lsc` commute, which is not
argued anywhere in the document and is not true in general.

**This is a disagreement internal to the source, on exactly the point BATCH-010's
Check B is about.** Both sides are quoted above and in §4 so that a reader can see it
without re-extracting anything.

**(c) What this does NOT decide.** Nothing here says which of the two orders the
authors intended, which one their own numerical code implements, whether the
BATCH-009 implementation's `min(1, K̄·L^p)` matches one of them, or what any of that
implies for the BATCH-009 over-prediction. Those are downstream questions and are
deliberately left open.

---

## 4. Supporting loci (the rest of the chain, for the reader's audit)

**(4.17) — PDF page 23 / printed 22, `plain` lines 1–13.** The score approximation
that (4.18) is built from, with the `d_lsc` integral outermost and the *sum* inside:

```
   1| Recall that Approximation 4.6 gives
   2| F (lsc)
   3| gsenu
   4| <U+0000>
   5| G⊤ fsfft
   6| <U+0001>
   7| ≈ N ·
   8| Z ∞
   9| 0
  10| ψlsc(dlsc) ·
  11| X
  12| i,j
  13| Ni,j · Φdlsc (i, j)ddlsc (4.17)
```

**(4.9) — PDF page 20 / printed 19, `layout` lines 20–25.** The same content of
Approximation 4.6 written with the *sum outside* and the `d_lsc` integral inside:

```
  20|                                     Approximation4.6(Second-Level Approximation).     Based on Approximation4.4, As-
  21|                                     sumptions4.2and4.3,andassumingtheGaussianHeuristicholds,wehave
  22|                                                                   <U+0000>G⊤fsfft<U+0001>≈N·X               Z ∞
  23|                                                            F(lsc)gsenu                  Ni,j·
  24|                                                                                    i≥0          0   ψlsc(dlsc)·Φdlsc(i,j)ddlsc             (4.9)
  25|                                                                                    j≥0
```

Observation (mine, flagged as such, not the source's): sum and integral commute, so
(4.9) and (4.17) are consistent with each other. `max` and integral do not commute,
which is where the (4.18)/(4.22) divergence enters.

**(4.26)–(4.29) and the closing display — PDF page 25 / printed 24, `layout` lines
1–18 and plain lines 78–83.** The justification of Approximation 4.9:

```
   1| JustificationofApproximation4.9.            Ontheotherhand,Approximation4.9isobtainedbyesti-
   2| matingthelengthoftheshortvectorsin qΛ(Bglobal)∨+rproj,where rprojisnolongertheshortest
   3| vectorinthelatticecoset.For iand jsmallenough,wecanmaketheapproximationthat
   4| 
   5|                                         P(Ni,j > 0)≈P(Ni,j = 1).                         (4.26)
   6| 
   7| Thus,thesurvivalfunctionof D,knowingthattheachieveddecodingdistanceis dlsc,canbe
   8| approximatedby
   9| 
  10|                             P(D >T |dlsc)≈P(∃(i,j)∈E(T)  : Ni,j > 0)                 (4.27)
  11| 
  12|                                                       1,E X                           (4.28)
  13|                                                ≈ min                      Ni,j
  14|                                                                (i,j)∈E(T)
  15|                                                                (i2,j2)∈N2
  16| 
  17| where
  18|                                E(T) △=<U+0008>(i,j)∈R2+  : N·Φdlsc(i,j)≥T	.                  (4.29)
```

and, `plain` mode lines 78–83 of the same page:

```
  78| Finally, under Model 4.7,Pwrong is the convolution product of the probability density function
  79| of the normal distributionN (0, N/2) and the survival function ofD, that is given by
  80| P (D > T) =
  81| Z ∞
  82| 0
  83| ψlsc(dlsc) · P (D > T| dlsc) ddlsc
```

Note the phrase at line 7 — "the survival function of `D`, **knowing that the achieved
decoding distance is `d_lsc`**" — and the conditional `P(D > T | d_lsc)` at (4.27) and
at line 83. These are the sentences that (4.18) cannot support, and they are the
sentences (4.22) is derived from.

---

## 5. `Φ_{d_lsc}`: **DEFINED IN SOURCE**

BATCH-010 recorded `Φ_{d_lsc}` as UNAVAILABLE (validation report L-3: "the archived
page extracts give Φ only as an undefined symbol"). That is true **of the archived
extract set**, and false of the document.

**Locus: PDF page 20, printed page 19, equation (4.10), immediately under
Approximation 4.6.** `layout` lines 27–34:

```
  27|                                     where
  28|                                                                   Φdlsc(i,j) △=Υβsieve  2π        ·Υnfft     2π        ,                 (4.10)
  29|                                                                                    2     q dlati      2 −1    q dlscj
  30|
  31|
  32|                                                                                                   +∞X  (−1)ℓ(x/2)2ℓ
  33|                                                                   Υn(x) △= Γ (n+1)Jn(x)(x/2)n        =ℓ!Qℓ
  34|                                                                                                   ℓ=0     s=1(n+s),                 (4.11)
```

`plain` mode of the same page, lines 62–87, gives the same two definitions token by
token:

```
  62| where
  63| Φdlsc (i, j)
  64| △
  65| = Υ βsieve
  66| 2
  67| <U+0010>
  68| 2π
  69| q dlati
  70| <U+0011>
  71| · Υ nfft
  72| 2 −1
  73| <U+0010>
  74| 2π
  75| q dlscj
  76| <U+0011>
  77| , (4.10)
  78| Υn(x)
  79| △
  80| = Γ (n + 1)Jn(x)
  81| (x/2)n =
  82| +∞X
  83| ℓ=0
  84| (−1)ℓ(x/2)2ℓ
  85| ℓ! Qℓ
  86| s=1(n + s)
  87| , (4.11)
```

That is:

> Φ_{d_lsc}(i,j) ≜ Υ_{β_sieve/2}( (2π/q) d_lat i ) · Υ_{n_fft/2 − 1}( (2π/q) d_lsc j )
>
> Υ_n(x) ≜ Γ(n+1) J_n(x) / (x/2)^n = Σ_{ℓ≥0} (−1)^ℓ (x/2)^{2ℓ} / ( ℓ! ∏_{s=1}^{ℓ}(n+s) )

with `J_n` the Bessel function (the paper reaches `Υ` from the Fourier transform of a
ball indicator at PDF page 21 / printed 20).

`Φ` occurs on exactly four PDF pages — 20 (twice: in (4.9) and in its definition
(4.10)), 23 (three times: (4.17), (4.18), (4.23)), 24 (once), 25 (once: (4.29)) — so
(4.10) is its only definition and it precedes every use.

**Why BATCH-010 could not see it:** the archived extract set
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/` contains pages 23,
25, 26, 27 and 37, and **not page 20**. The unavailability was a property of the
extract set, not of the document.

---

## 6. `α`: **DEFINED IN SOURCE**

BATCH-010 recorded `α` as UNAVAILABLE with "no numeric value" (L-3). Again true of the
extract set, not of the document.

**Definition locus: PDF page 9, printed page 8, Definition 2.3.** `layout` lines
48–52:

```
  48| Definition2.3(CenteredBinomialDistribution).   ThecenteredbinomialdistributionBαofyisdefinedas Bα ∼Pα
  49| parameter α ∈q0, q−12                            i=1(Xi−Yi)wherethe Xi’sand Yi’sarei.i.d.as<U+0001>.Notethat
  50| uniformover{0,1}.Inparticular,forall i∈J−α,αK,wehaveP(Bα =i) = 2−2α<U+0000> 2αα+i
  51| Bαhasmean 0andstandarddeviation σ △=p           α
  52|                                                 2.
```

`plain` mode, same page, lines 67–82 (token order is cleaner here):

```
  67| Definition 2.3 (Centered Binomial Distribution).The centered binomial distributionBα of
  68| parameter α ∈
  69| q
  70| 0, q−1
  71| 2
  72| y
  73| is defined as Bα ∼ Pα
  74| i=1(Xi − Yi) where the Xi’s and Yi’s are i.i.d. as
  75| uniform over {0, 1}. In particular, for alli ∈ J−α, αK, we haveP (Bα = i) = 2−2α<U+0000> 2α
  76| α+i
  77| <U+0001>
  78| . Note that
  79| Bα has mean 0 and standard deviationσ
  80| △
  81| = p α
  82| 2.
```

i.e. `α ∈ ⟦0, (q−1)/2⟧` is the **parameter of the centered binomial distribution
`B_α`** from which the Kyber-style secret and error coordinates are drawn, and
`B_α` has mean 0 and standard deviation `σ = √(α/2)`.

The document itself ties this `α` to the `α` appearing in (4.19) and (4.22)'s
neighbourhood, so the identification is the source's and not an inference of mine:

- **PDF page 13 / printed 12**, Algorithm 3.1 input, `plain` lines 33–36 verbatim:

  ```
    33| Algorithm 3.1The code based dual attack to solveL WE
    34| Input: a sample (A, b) ∈ Zm×n
    35| q × Zm
    36| q produced by anL WE(q, n, m,Bα, Bα) oracle.
  ```
- **PDF page 24 / printed 23**, first lines of the Justification of Approximation 4.8,
  `plain` lines 1–6 verbatim:

  ```
     1| which has particularly small length. Specifically, the quantities∥P(e,slat)∥q α
     2| 2
     3| and ∥sfft∥q α
     4| 2
     5| approximately
     6| follow a χ-distribution11 with degrees of freedomβsieve and nfft, respectively.
  ```

  (The bare `q` at the end of lines 1 and 3 is the extractor's rendering of a radical
  glyph — the same construction that appears as `p` in `σ △= p α 2` at Definition 2.3
  — so the two quantities are `∥P(e,s_lat)∥` and `∥s_fft∥` normalised by `√(α/2)`,
  which is exactly `B_α`'s standard deviation from Definition 2.3. I flag the glyph
  reading as mine; the tokens `α`, `2`, `χ-distribution`, `β_sieve`, `n_fft` are the
  source's.) The same page then carries the `e^{−α(π d_lsc/q)²}` expansions that
  produce the `exp(−α(πµ_lsc/q)²/(1+2α(πσ_lsc/q)²))/√(1+2α(πσ_lsc/q)²)` factor of
  (4.19), at plain lines 97–112.
- **PDF page 36 / printed 35**, Appendix B, `layout` lines 10–15 verbatim (note that
  `layout` mode drops inter-word spaces in running prose; nothing has been inserted):

  ```
    10|lengthoftheshortestvectorin qΛ(Bglobal)∨ +rproj.Giventhatthecoordinatesof (e,slat,sfft)are
    11|i.i.d.randomvariablesfollowingacenteredbinomialdistributionwithparameter α,weestimate
    12|thelengthof (P(e,slat),sfft)tobe
    13|                                                             q
    14|                                      ∥(P(e,slat),sfft)∥≈       α(βsieve+nfft)
    15|                                                                     2       .                       (B.1)
  ```

**Numeric values given in the document.** Table 5.1, **PDF page 28, printed page 27**,
column `α` (plain lines 13–19):

```
  13| q n α C0 CC CN C0 CC CN
  14| Kyber-512 3329 512 3 AES-128
  15| (143 bits) 115.4 139.2 134.4 121.8 139.5 134.5
  16| Kyber-768 3329 768 2 AES-192
  17| (207 bits) 173.7 196.1 190.6 173.0 195.1 189.8
  18| Kyber-1024 3329 1024 2 AES-256
  19| (272 bits) 241.8 262.4 256.1 239.0 259.7 254.6
```

i.e. `α = 3` for Kyber-512 and `α = 2` for Kyber-768 and Kyber-1024.

**What is still not in the document: `α` for the two archived toy runs.** The Figure
4.1 caption (PDF page 26 / printed 25, plain lines 37–50) lists `q = 241, m = 40,
n = 43/50, n_lat, n_enu, n_fft, k_fft, N, β_bkz, β_sieve, d_lat, µ_lsc, σ_lsc` — and
**no `α`**. Verbatim, plain lines 43–50:

```
  43| data were obtained by running4000 iterations of Algorithm 3.1, with each iteration using an input
  44| (A, b) taken uniformly at random inZm×n
  45| q × Zm
  46| q . The parameters used are:
  47| – on the left: q = 241, m = 40, n = 43, nlat = 35, nenu = 0, nfft = 8, kfft = 3, N = 25971, βbkz = 32,
  48| βsieve = 44, dlat = 42.00, µlsc = 23.94 and σlsc = 3.38,
  49| – on the right: q = 241, m = 40, n = 50, nlat = 42, nenu = 0, nfft = 8, kfft = 3, N = 25970,
  50| βbkz = 35, βsieve = 41, dlat = 58.60, µlsc = 23.87 and σlsc = 3.30.
```

So: **`α` is DEFINED IN SOURCE (Definition 2.3, printed p. 8) and given numerically
only for the three Kyber parameter sets (Table 5.1, printed p. 27). The document does
not state `α` for the `q=241` simulations of Figure 4.1.** The archived vendor data
carries `# alpha_secret=2` and `# alpha_error=2` in the header of the *Pgood* file only
(`experiments/EXP-MLKEM-011/vendor-lock/data/Pgood_q241_…out`; the two *Pwrong* headers
carry no `alpha` field at all). Whether that header field is the paper's `α` is an
identification the document does not make, and I do not make it here.

---

## 7. Correction to a premise of this task's handoff

The handoff states that (4.18) "is **not** among the current extracts". **That is
incorrect.** (4.18) is present, in full, in the already-archived extract
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page23_approx_4_8_4_9.txt`,
at its lines 30–41, byte-identical to the `plain`-mode block quoted in §1 above —
because (4.18) and (4.22) are on the **same PDF page 23**. (4.22) is at lines 98–118 of
the same archived file. Both BATCH-009 and BATCH-010 therefore had (4.18) available;
BATCH-010's validator evidently read it there, which is how D7 was raised.

"Byte-identical" is meant literally and was checked: the archived
`page23_approx_4_8_4_9.txt` and this task's freshly extracted page-23 plain text have
the same sha256, `9afd68154e8210a828180f734b580b19533f482dc7e0e236056869e0cb3e15ed`.
The archived `page25_pwrong_validation.txt` and `page26_fig41.txt` likewise match this
task's page-25 and page-26 plain extractions exactly (`diff` clean). So the extraction
pipeline used here reproduces the archived extracts bit for bit, and the two quoted
loci in §1–§2 are the same bytes BATCH-009 and BATCH-010 worked from.

What the archived extract set genuinely lacked is **PDF page 20** (definition of
`Φ_{d_lsc}` at (4.10) and of `Υ_n` at (4.11)), **PDF page 9** (Definition 2.3 for `α`)
and **PDF page 28** (Table 5.1's numeric `α`). Those three absences, not the absence
of (4.18), are what produced the "UNAVAILABLE" records in BATCH-010's L-3.

Recorded here because the batch was opened on a premise about the extract set that the
extract set does not bear out. The substantive D7 question was still open and is
answered in §3.

---

## 8. Limitations

- **L-1.** This is a text-extraction reading of a PDF. Both `pypdf` modes were used and
  they agree on the two decisive nestings, and the scaled-delimiter glyphs were
  inspected codepoint by codepoint; but no glyph-level rendering or independent PDF
  engine was available in this environment, so the reading rests on `pypdf` alone.
- **L-2.** Only the eight pages listed in `extract_pages.py`'s `PAGES_OF_INTEREST`
  were read line by line. The `Φ` / `α` / `min` searches, however, were run over all
  37 pages of plain-mode text, so the "only definition" and "exactly twice" statements
  are document-wide, subject to L-1.
- **L-3.** Nothing here is a mathematical derivation of one form from the other beyond
  the type-level observation in §3(b). In particular no attempt was made to quantify
  how much the two orders differ numerically; that would be new computation and is out
  of this task's scope.
- **L-4.** Toy tier throughout; `q=241, m=40, n=43/50`. This document establishes
  nothing about ML-KEM security in either direction and must never be cited as bearing
  on it.

## 9. Inference

```yaml
requested_policy: executor-implementation
resolved_model_id: claude-opus-5
fallback_used: true
fallback_reason: >-
  orchestration/model-policies.yaml routes executor-implementation to a
  GPT-5.6-family alias that Claude Code cannot resolve; per CLAUDE.md's model
  policy note the subagent runs on the inherited Claude model and the
  substitution is recorded rather than performed silently.
degraded_allowed: false
degraded_requirements: []
model_verified: false
model_verified_note: >-
  `python3 -m orchestration.adapter doctor --probe` was NOT run; no orchestration
  backend is reachable from this session. Absence recorded, not substituted for.
independent_session: false
```
