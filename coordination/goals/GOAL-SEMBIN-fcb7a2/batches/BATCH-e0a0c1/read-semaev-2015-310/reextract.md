# Extraction check — `inputs/SEMAEV-2015-310/paper_fulltext.md` against the PDF

Task `TASK-20260916-64a93b`, validator blind read, joint J-4 / J-5.
Written 2026-09-21. **Nothing under `inputs/` was modified.** `paper_fulltext.md`
is hash-pinned and immutable and was read only.

## The question the card posed

`inputs/NAGAO-2013-549/errata-extraction-20260921.md` records a CONFIRMED
extraction defect in a sibling package — 63 of 73 large operators detached from
their operands, so a graded hypothesis reads as a vacuous one. `SEMAEV-2015-310`
was audited and reported as showing **no operator detachment** but **line
splitting**. The card required that any formula this read relies on be checked
against the PDF and the outcome recorded either way.

## Method

No `pdftotext`, `pdfminer`, or `pypdf` was present in this checkout. `pdfminer.six`
20260107 was installed into the session interpreter (`pip install pdfminer.six`);
it writes nothing into the repository and `git status --porcelain` is unaffected.

Two independent passes were made over
`inputs/SEMAEV-2015-310/eprint-2015-310.pdf`:

1. `extract_text` with `LAParams(line_margin=0.5, char_margin=1.5, boxes_flow=None)`
   — deliberately DIFFERENT parameters from the frozen extraction, which used
   `LAParams(line_margin=0.3, char_margin=2.0, boxes_flow=0.5)`. A defect that
   is an artifact of one parameter set will not survive both.
2. A glyph-level pass: every `LTChar` on the page collected with its `(x0, y0)`
   and regrouped by baseline, with superscript and subscript rows re-interleaved
   by `x0`. This is the only way to settle whether a split display is a
   REORDERING (recoverable) or a LOSS (not recoverable).

### Hash verification of the frozen sources

Both sidecars were checked with `sha256sum -c` in this session. All four pass,
so the bytes this read was performed against are the bytes the program pinned:

| file | sidecar | result |
|---|---|---|
| `inputs/SEMAEV-2015-310/eprint-2015-310.pdf` | `d6636436e2e9254d07e2270f61e6d1892de8d0d5f350a1c5232f60cafe39a7db` | OK |
| `inputs/SEMAEV-2015-310/paper_fulltext.md` | `3b3bea4c24c6265e1056b25ad41f6cec77669bcff9117e13e79163de3f68b8f3` | OK |
| `inputs/NAGAO-2015-984/eprint-2015-984.pdf` | (sidecar in package) | OK |
| `inputs/NAGAO-2015-984/paper_fulltext.md` | (sidecar in package) | OK |

This is a read-only integrity check, not a measurement: it re-hashes files
already on disk and runs no experiment. It matters here because the whole
extraction question is whether the text I read is the text the PDF carries, and
a hash mismatch would have made that question moot.

## Finding: line splitting, confirmed. Operator detachment, not found.

The audit's characterisation holds for every passage this read relies on. The
splitting is real and it is severe enough to make one display unreadable in the
frozen text, but **no operator was lost**, and every formula reassembles
uniquely from glyph coordinates.

### F-1 — the load-bearing display, p.10 (`paper_fulltext.md` :574-589)

This is the single formula the whole of J-4b rests on. In the frozen text it
appears as eight fragments in an order that cannot be read:

```
x1S3(x1, x2, x3) = x1[(x1x2 + x1x3 + x2x3)2 + x1x2x3 + B]
1x2
3 + x1x2
3 + x2
2 + x3
= x3
1x2
2x2
1x2x3 + Bx1
```

Reassembled from glyph coordinates (two baselines, y = 460.0 and y = 443.5 on
PDF page 10, superscripts marked `^`, subscripts `_`):

```
x1S3(x1,x2,x3) = x1[(x1x2+x1x3+x2x3)^2 + x1x2x3 + B]
               = x^3_1 x^2_2 + x_1^3 x^2_3 + x_1 x^2_2 x^2_3 + x^2_1 x_2 x_3 + B x_1
```

i.e.

> x₁·S₃(x₁,x₂,x₃) = x₁³x₂² + x₁³x₃² + x₁x₂²x₃² + x₁²x₂x₃ + Bx₁

**VERDICT: recoverable, and recovered.** Every symbol of the frozen fragments
appears in the reassembly and nothing else does. `recheck.py` RC-1e then
verifies the reassembled identity independently, as an identity of descended
Boolean systems over F₂⁵, F₂⁷ and F₂⁹ — it holds exactly. So the formula this
read relies on is confirmed twice: once as glyphs, once as algebra.

(The only residual ambiguity is cosmetic: for `x_1^3` the sub- and superscript
sit at the same x, so their emission order is arbitrary. It does not change the
monomial.)

### F-2 — the first fall degree definition, §4.4, p.9 (`paper_fulltext.md` :505-518)

This is the passage most at risk of the sibling package's defect, because it
carries two large Σ operators. In the frozen text the display Σ (`(cid:88)`) lands
on :515, AFTER the operand `gifi < df f` on :513, and the inline Σ (`(cid:80)`)
lands on :517.

Glyph-level reassembly (PDF p.9, y = 518.9 / 512.9 / 511.9 / 511.7 / 500.4):

```
max_i(deg g_i + deg f_i) = d_ff ,      deg  Σ_i  g_i f_i  <  d_ff
and  Σ_i g_i f_i  ≠ 0.   A first fall degree assumption says d_F4 ≤ d_ff
```

**VERDICT: the operators are PRESENT and correctly scoped.** Both Σ glyphs are
in the frozen text (`(cid:88)`, `(cid:80)`), merely re-ordered by the extractor.
The definition is not vacuous and reads as it must.

**But the reassembly settles a distinction that matters and that the frozen text
obscures.** Semaev's condition (1) is

> max_i( **deg g_i + deg f_i** ) = d_ff       — a SUM OF DEGREES, with EQUALITY

whereas Nagao 2015/984 Definition 5 (`inputs/NAGAO-2015-984/paper_fulltext.md`
:398-410) writes

> max_i{ **deg g_i f_i** } ≥ d_F              — the DEGREE OF THE PRODUCT, with ≥

In a ring where degree is additive these agree. In the multilinear Boolean ring
they need not, and the difference is exactly the X² → X collapse that this whole
question is about. Recorded here because it is a difference in the two papers'
STATED definitions, recovered from the PDF, not an extraction artifact. It is
carried into `report.md` §J-4b as a reading hazard, not as an error in either
paper: at the descended level the two generically coincide (a product of a
degree-a and a degree-b Boolean polynomial in overlapping variables generically
has degree a+b), so the distinction does not bite on the argument as given.

### F-3 — Assumption 1, p.10 (`paper_fulltext.md` :602-605)

Glyph reassembly (PDF p.10, y = 281.6 … 249.6):

```
Assumption 1  Let q = 2^n and 2 ≤ m < n, k = ⌈n/m⌉.  Also let V be a subspace of
dimension k in F_{2^n}.  Then d_F4 ≤ 4 for a Boolean equation system equivalent
to (5) for any 2 ≤ t ≤ m.
```

**VERDICT: byte-equivalent to the frozen text** once `(cid:100) n / m (cid:101)`
is read as `⌈n/m⌉` and the flattened sub/superscripts are restored. Nothing lost.

### F-4 — the J-5 known-false object, §4.5.1 closing, p.13 (`paper_fulltext.md` :1054-1058)

Glyph reassembly (PDF p.13, y = 670.3 / 661.7 / 656.8 / 653.6):

```
To conclude the section we should mention that the maximal degree(regularity
degree) generally exceeds 4 when k > ⌈n/m⌉ though the first fall degree is
still 4.
```

**VERDICT: confirmed verbatim.** This sentence is the object the J-5 control is
run against, so it was checked with particular care: the `>` is a `>` and not a
mangled `≥` or `<`, and `⌈n/m⌉` is the split `(cid:100) n (cid:101) / m` of the
frozen text. Confirmed at glyph level.

### F-5 — the quantifier slide, §4.5.1, p.11 (`paper_fulltext.md` :752-759)

Glyph reassembly (PDF p.11, y = 453.5 / 189.8 … 149.2, and p.12 y = 683.9):

```
To fill the tables 2300 Boolean systems each of total degree 3 coming from (5),
where t = m, were solved.  For all of them the maximal total degree attained by
F4 to compute a Gröbner basis was exactly 4.  For t < m the maximal total degree
was smaller or equal to 4.  We conclude that for all values of n, m and t ≤ m in
the tables Assumption 1 was correct for randomly chosen z ∈ F_{2^n}.  So the
assumption is very likely to be correct for any values of n, m, t ≤ m.
```

**VERDICT: confirmed verbatim**, including the sentence boundary between
"…in the tables … for randomly chosen z" and "So the assumption is very likely
to be correct for any values of n, m, t ≤ m", which is where the quantifier
changes and is therefore the sentence J-4c turns on.

### F-6 — the remaining passages relied on

Checked at glyph level and confirmed against the frozen text with no loss:

| passage | frozen text | PDF |
|---|---|---|
| "The first fall degree is proved to be 4." | :97 | p.2 y=385.8 |
| "This argument does not work for S3(x1,x2,z)" + the three degrees | :591-597 | p.10 y=602/605/606 |
| "bounded by 5 in [11]. The experiments show it is always 4 again. Anyway at least t − 2 of the equations in (5) have the first fall degree 4." | :598-599 | p.10 y=608-609 |
| "Although not generally correct, the assumption appears correct for the polynomial systems coming from (4)" | :519-520 | p.9 y=469.5-456.0 |
| "one can define V as any subspace of F2n of dimension k" | :542 | p.9 y=242.3 |
| "The system consists of n(t−1) coordinate equations in n(t−2)+kt variables and n(t−2)+kt field equations are added" | :612-613 | p.10 y=159.6 |
| "solve the system for 100 random z" | :617-618 | p.10-11 |
| eq. (14) S3 = (x1x2+x1x3+x2x3)² + x1x2x3 + B | :534 | p.9 y=321.0 |

## Two reading hazards that are NOT extraction defects

Recorded so a later reader does not spend the same time on them.

1. **"We consider the case m = 2 in more detail now." (:561, PDF p.10 y=607.8).**
   This reads as a typo for "p = 2" until it is read against the preceding
   sentence, which is about `S_{m+1}(x_1,…,x_m,R_X) = 0` and its bound `m²+1`.
   At m = 2 that equation IS `S_3`, so the sentence is correct as printed and
   announces the analysis of the individual links of the chain (5). The `2` is a
   `2` in the PDF. No defect; recorded because the frozen text invites the
   misreading and §4.5 is titled "Characteristic 2".

2. **Tables 1–3 are reflowed column-wise** in `paper_fulltext.md` (:641-751,
   :769-1041, :1159-1235) and are unusable there. This is the documented reason
   `tables.yaml` exists. The six `t = 2` rows this read cites (RC-5d) were taken
   from `tables.yaml`, and the first data row of Table 1 was independently
   confirmed at glyph level (PDF p.11 y=382.4: `12 6 2 0.00 0.0013 4 2.30 257.8`,
   matching `tables.yaml table_1` row 1 exactly).

## Outcome

**No extraction defect was found that affects any formula this read relies on.**
The package shows severe line splitting of displayed mathematics, exactly as the
audit records, and one display (F-1) is unreadable in the frozen text. Both
large Σ operators in the first-fall-degree definition are present and correctly
scoped, so the sibling package's vacuity failure mode does not occur here.

Every formula cited in `report.md` was reassembled from PDF glyph coordinates
before it was relied on, and the load-bearing one (F-1) was additionally
verified as an algebraic identity by `recheck.py` RC-1e.
