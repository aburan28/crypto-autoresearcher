# Extraction errata — `inputs/NAGAO-2013-549`

**Recorded** 2026-09-21 by the coordinator session on
`cursor/semaev-2015-audit-program-5b8b`.
**Status** additive. Nothing in this package is edited. `paper_fulltext.md`,
`eprint-2013-549.pdf` and both `.sha256` files are untouched and still verify.

## What is wrong

`paper_fulltext.md` renders the hypothesis of **Lemma 2's proof** (frozen
markdown lines 721–734) as a scatter of fragments:

```
Proof. Fix some monomial order > satisfying
fi. For a local
polynomial H 2 Fp[X1, ..., Xd], let LM (H) ...
...
i when
i >
ei >
X ei
X fi
∑
∏
```

The PDF says, on one line:

```
Proof. Fix some monomial order > satisfying ∏Xei
i
> ∏Xfi
i
when ∑ei > ∑fi.
```

That is, **∏ X_i^{e_i} > ∏ X_i^{f_i} whenever ∑ e_i > ∑ f_i**: a *graded*
monomial order, refining by total degree.

## Why it matters, and why it is worse than a missing formula

The operators were **not dropped**. `paper_fulltext.md` and a fresh extraction
contain exactly the same counts — 54 `∑` and 19 `∏` in both. They were
**detached from their operands** and scattered onto separate lines.

What survives at lines 726–734 therefore reads as `X^{e_i} > X^{f_i} when
e_i > f_i` — a per-variable comparison, and a vacuous-looking one. A reader
working from the markdown alone sees Lemma 2's proof fixing a monomial order
subject to a condition that says nothing, and can reasonably conclude the proof
rests on nothing.

A *missing* formula announces itself. A formula that silently re-reads as a
weaker hypothesis does not, and the reader cannot tell the difference without
opening the PDF. That is the defect this errata exists to flag.

## Scale, measured

`python3 tools/audit_frozen_extraction.py inputs/NAGAO-2013-549`:

| quantity | value |
|---|---:|
| large operators in frozen markdown | 73 |
| large operators in fresh extraction | 73 |
| operators standing ALONE on their own line | **63** |
| shredded-formula runs | 84 |
| lines inside those runs | 804 |
| frozen markdown length | 2325 lines |
| fresh extraction length | 936 lines |

86% of this paper's large operators are orphaned, and the frozen file is 2.5×
longer than a clean extraction of the same PDF — both signatures of
line-shredded display math throughout.

Two regions matter for what this program reads:

- **Lemma 2's statement and proof** (lines 685–945) — the statement Nagao
  2015/984 cites as its Lemma 3 and declines to reproduce — is broken into
  **ten separate runs** totalling 90 fragment lines. Its largest single run
  (782–815, 19 fragments) ranks 7th of 84 in the paper.
- **Definition 1, the first fall degree itself** (lines 530–564, 18 fragments,
  plus a second run at 593–598) — the definition of the quantity this program
  measures.

Neither is the paper's *worst* region: Sections 3–4 are (lines 1759–1930 carry
runs of 44 and 54 fragments). The point is not a ranking but that both passages
the campaign depends on are shredded throughout.

## Scope of this finding

Confirmed for this package only. The same audit over every `inputs/` package
holding both a PDF and a `paper_fulltext.md` found `NAGAO-2013-549` to be the
clear outlier, and found **nothing dropped** anywhere:

| package | orphaned operators | shredded runs |
|---|---:|---:|
| `NAGAO-2013-549` | **63** | 84 |
| `VOW-1996-PCS` | 2 | 24 |
| `SEMAEV-2015-310` | 0 | 18 |
| `BAILEY-2009-541-ECC2K130` | 0 | 18 |
| `NAGAO-2015-984` | 0 | 16 |
| `NAGAO-2013-548` | 0 | 12 |
| `KARABINA-PDP-2015` | 0 | 4 |

Every package shows some line-splitting of display math -- that is what
PDF-to-text does -- and `NAGAO-2013-549` is distinguished by **operator
detachment**, which is the part that changes how a hypothesis reads. The other
packages' PDFs contain no `∑`/`∏` glyphs at all, so nothing was dropped or
detached in them; their runs are ordinary line-splitting.

A methodological note, because it bears on trusting the numbers above: a first
version of the detector counted any short line as a fragment, which counted
ordinary English words and reported 38 runs. The counts here come from a
tightened rule that requires a digit, a math symbol, or a bare single-letter
variable, and which deliberately **undercounts** -- a purely alphabetic fragment
is missed rather than risk counting prose. `tools/test_audit_frozen_extraction.py`
pins that discrimination.

## Remedy

`paper_fulltext.pymupdf.txt` is added beside the frozen text: a page-delimited
extraction of the same PDF via `pymupdf`, in which the disputed passage appears
intact on one line. It is **supplementary**, not a replacement — the frozen file
remains the hash-pinned artifact every existing record cites, and no record's
citation is changed by this errata.

```
paper_fulltext.pymupdf.txt
  sha256 087d38343460919c6a4aad554edf923026ce41b03857e232f232cb76f018278e
  28116 bytes, pymupdf, 9 pages
```

**Tooling note for this package's provenance.** `provenance.json` records that
`pdftotext` was unavailable when the package was frozen. This environment has
neither `pdftotext` nor `mutool`, and `mupdf-tools` is not installable from its
apt sources; `pip install pymupdf` works and is what produced the file above.
A later reader needing display math from any frozen package should reach for
that rather than trusting a `paper_fulltext.md` at a formula.

## What this errata does NOT establish

- It says **nothing about whether Lemma 2 is correctly proved.** It establishes
  only that the proof's monomial-order hypothesis is graded in the source and is
  unreadable as such in the frozen markdown. Whether the proof is complete, and
  whether the graded order is load-bearing for its induction, are reading tasks
  that this does not perform.
- It does **not** revive the lost blind read that first reported this defect
  (`CORR-20260921-942a62`). That report is gone and is not cited here. The
  finding above was re-established from the frozen PDF directly, with a
  different tool, and stands on the audit command any reader can re-run.
- It changes no record's status and discharges no joint.
