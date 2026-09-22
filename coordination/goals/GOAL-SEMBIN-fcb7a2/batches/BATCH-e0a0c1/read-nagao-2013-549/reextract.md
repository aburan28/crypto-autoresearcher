# Extraction question and its outcome

Task `TASK-20260916-9da6e0`. Written into the task's own write scope, as the
card requires. **No measurement was performed and no frozen artifact was
edited.**

## Question 1 — the one the card anticipated: `inputs/NAGAO-2013-549`

**Question.** Nagao 2013/549's Lemma 2 — the statement 2015/984 quotes as its
Lemma 3 — has a proof whose first line fixes a monomial order. In the frozen
`paper_fulltext.md` (lines 721–734) that line renders as a scatter:

```
Proof. Fix some monomial order > satisfying
fi. For a local
polynomial H 2 Fp[X1, ..., Xd], let LM (H) ...
i when
i >
ei >
X ei
X fi
∑
∏
```

which reads as `X^{e_i} > X^{f_i} when e_i > f_i` — a per-variable comparison
that says nothing. On that reading Lemma 2's proof fixes an order subject to an
empty condition, and its central step (`deg F = deg ψ(G)`) has no support.

**Outcome: ANSWERED BY THE ERRATA ALREADY FILED. No re-extraction work was
re-done.**

`inputs/NAGAO-2013-549/errata-extraction-20260921.md` is a confirmed,
already-filed extraction-defect report for this exact passage. It records that
the operators were **detached from their operands, not dropped** (73 large
operators in both the frozen text and a fresh extraction; 63 standing alone on
their own line), that this package is the clear outlier across every `inputs/`
package holding both a PDF and a markdown, and that the source line reads

```
Proof. Fix some monomial order > satisfying ∏ X_i^{e_i} > ∏ X_i^{f_i}
when ∑ e_i > ∑ f_i.
```

— a **graded** order, refining total degree.

Per the card's instruction, I recorded that rather than repeating the work. What
I did do, because it costs nothing and the errata explicitly disclaims it:

- **Verified the remedy file is what it says it is.**
  `sha256sum inputs/NAGAO-2013-549/paper_fulltext.pymupdf.txt` returns
  `087d38343460919c6a4aad554edf923026ce41b03857e232f232cb76f018278e`, matching
  the errata's recorded hash exactly.
- **Verified every frozen artifact still verifies.** `sha256sum -c` passes for
  `NAGAO-2013-549/paper_fulltext.md`, `NAGAO-2013-549/eprint-2013-549.pdf`,
  `NAGAO-2015-984/paper_fulltext.md` and `NAGAO-2015-984/eprint-2015-984.pdf`.
- **Read the whole clean extraction** (945 lines) rather than only the disputed
  passage. It is intact in every region this read depends on: Definition 1,
  Lemma 2 and its proof, Lemma 9, and the Section-2 passage that states the
  actual first-fall estimate.

**What the errata leaves open, and which this read closes.** The errata says in
terms that it establishes nothing about whether Lemma 2 is correctly proved, and
that whether the graded order is load-bearing for the induction is a reading
task it does not perform. That reading task is J-2, and the answer is **yes, it
is load-bearing**: the `NUM(G) = 1` branch concludes `D = deg F = deg ψ(G)`,
which requires `deg ψ(G) ≥ deg G_i + p` for every `i`, and that is exactly what
a graded order gives and a lexicographic one does not. So the frozen markdown's
rendering is not merely lossy — it deletes the one hypothesis on which the
branch turns. See `report.md` J-2 and `recheck.out` lines 73–79.

**`paper_fulltext.md` was not edited.** It is hash-pinned and immutable and it
still verifies.

## Question 2 — one the card did not anticipate: `inputs/NAGAO-2015-984`

**Question.** J-3 turns entirely on the precise wording of 2015/984's
Definitions 5 and 6 and of Lemmas 3 and 4. In that package's frozen
`paper_fulltext.md` those passages carry `(cid:80)` markers where the summation
signs should be (lines 400–515), the conditions are split across lines out of
order, and in particular:

- condition (1) of Definition 5 reads `>= dF` rather than `= dF`;
- conditions (1) and (2) of **Definition 6** name **`dF`**, not `d'F`, so as
  rendered the definition of `d'_F` never mentions `d'_F`.

`CORR-20260916-96f47d.residual_uncertainty` records this as an unresolved
extraction limit: "whether that is in the PDF or is a lost prime glyph is not
determinable from the frozen text alone." Since my J-3 derivation is sensitive
to both, I could not proceed on the frozen markdown.

The errata does **not** answer this — it is scoped to `NAGAO-2013-549` only, and
its own table records `NAGAO-2015-984` as having 0 orphaned operators and 16
ordinary shredded runs. So this question was live and I did the work.

**Outcome: RESOLVED. Both are in the PDF. They are not extraction artifacts.**

Method, with the working copy written **outside the repository** so that nothing
appeared in `git status`:

```
mkdir -p /tmp/val-9da6e0
python3 -c "import pymupdf; d = pymupdf.open(
    '/workspace/inputs/NAGAO-2015-984/eprint-2015-984.pdf'); ..."
```

writing `/tmp/val-9da6e0/n2015.txt`. `pymupdf` 1.28.2 was already present in the
environment (the errata records it being installed for the 2013/549 work);
neither `pdftotext` nor `mutool` is available here, which is the same constraint
that package's `provenance.json` records.

Findings, at PDF line level:

| passage | PDF says |
|---|---|
| Definition 5 cond. (1) | `1) maxi{deg gifi} ≥dF ,` — **`≥`**, and there is **no condition (4)** |
| Definition 6 cond. (1) | `1) maxi{deg gifi mod Sfe} ≥dF ,` — **`≥`**, and **`dF`**, not `d'F` |
| Definition 6 cond. (2) | `2) deg(PM i=1 gifi mod Sfe) < dF ,` — **`dF`**, not `d'F` |
| Lemma 4 | `Put dF by the first fall degree of {f1, ..., fM} and put d′F by the Fake first fall degree of {f1, ..., fM} ∪Sfe. Then dF ≤d′F.` |
| Lemma 6 statement | `The first fall degree of the equations system {F ↓j ...} ∪Sfe is heuristically ≤(p −1)n + deg F.` |
| Lemma 6 proof | `Fake first fall degree of {F ↓j ...} is bounded by ≤(p −1)n + deg F and from Lemma 4, we have this lemma.` |

The last two lines are the substantive result of this re-extraction, and they
are why it was worth doing: the union sits on the **fake** side in Lemma 4's
statement and on the **true** side in Lemma 4's only application. That is not
visible in the shredded markdown and it is the crux of J-3.

For comparison, 2013/549's Definition 1 (clean extraction, lines 204–209) reads
`1) max deg(gifi) = Dff` **and** carries `4) deg(fi) ≤ Dff`. The two papers'
definitions of the same-named quantity genuinely differ, in the source.

**A third pass, at span level.** The Example 1 discrepancy reported in
`report.md` J-1 could plausibly have been a line-grouping artifact, so I read
page 5 through `get_text('dict')` rather than through word grouping, which keeps
superscripts on their own spans and attaches them to the right line:

```
'Let F = (X2 + X)(Y 2 + Y ) + (X2 + X)(Y 2 + Z) ∈F2[X, Y, Z]. From its construction,'
'F ≡0 mod Sfe and expanding the formula, we have F = X2Y +Y 2Z+Y Z+X2Z+XY 2+XZ'
'F can be transformed by F = (X2 + X)(Y 2 + Y ) + (X2 + X)(Y 2 + Z)'
'= (X2 + X)(Y 2 + Y ) + (X2 + X)(Y 2 + Y ) + (X2 + X)(Y 2 + Y ) + (X2 + X)(Y 2 + Z)'
'= (X + Z)(Y 2 + Y ) + (X2 + X)(Y + Z), and F can be written by the sum of smaller degree'
```

Two extractors (pdfminer.six in the frozen file, pymupdf here) and two grouping
modes agree. The inconsistency is in the source, not in the extraction.

**Nothing in `inputs/NAGAO-2015-984` was edited, and no companion file was added
to it.** The working copy lives at `/tmp/val-9da6e0/n2015.txt`, outside the
repository, and is not a deliverable. A reader wanting it back runs the two
lines above against the same hash-verified PDF.

## Where an extraction limit still bites

None, for J-1 and J-2. Both passages this read depends on are intact in the
clean extractions and were cross-read against the PDF.

For J-3 the remaining limits are about **authorship, not extraction**: whether
the `≥` and the bare `d_F` are what Nagao meant is not recoverable from a
correctly extracted text that prints them. Recorded as `CND-2` in
`statement-map.json`.
