# arXiv submission package

This directory is **packaging only**. Nothing here is a second copy of anything:
the manuscript and the verification code are *staged* from their canonical
locations, so the preprint and the experiment cannot drift apart.

```sh
make -f Makefile.arxiv          # stage, compile, guard, tarball
```

That stages `../paper.tex` and the code and data from
`experiments/EXP-SMON-e5cbe6/`, checks the staged `raw-result.json` against its
recorded hash, compiles three passes, and refuses to build the tarball if the
author placeholder is still present, a reference is undefined, or the PDF
contains Type 3 bitmap fonts. Then upload `semaev-monodromy.tar.gz`. Do **not**
upload the PDF — arXiv wants the source.

Tracked in git: `SUBMISSION.md`, `abstract.txt`, `Makefile.arxiv`,
`anc/README.md`. Everything else in this directory is staged or built, and is
gitignored.

The tarball contains exactly:

```
paper.tex           the manuscript, self-contained, no \input, no .bib
anc/README.md
anc/semaev_cover.py field/curve/resultant/factorisation arithmetic, stdlib only
anc/verify.py       the falsification battery of section 8
anc/raw-result.json its output, byte-reproducible at seed 20260807
```

Compilation was verified here: TeX Live 2023, pdfLaTeX, 3 passes, 15 pages,
no errors, no warnings, all fonts embedded Type 1.

---

## YOU MUST DO THREE THINGS BEFORE UPLOADING

### 1. Fill in the author block

`../paper.tex` carries `[AUTHOR NAME] / [affiliation] / [email]` as a visible
placeholder, and it renders on the title page. It is a placeholder rather than a
guess because arXiv requires a real author and inventing one would be a
fabrication. `make check` refuses to build a tarball until it is replaced.
Nothing else in the file needs editing.

### 2. Decide the title — the current one under-describes the paper

The shipped title is

> Conservation and Specialization in Semaev-Based Index Calculus over Prime Fields

which was the working title for the synthesis. It is now slightly **inaccurate in
a way a math.NT reader will notice**: Theorem 3.4 holds over *any* field in *any*
characteristic, and Theorem 4.2 over any finite field. "over Prime Fields"
describes only the index-calculus application in sections 5–7. Suggested
alternative, which keeps the synthesis framing but does not mis-scope the main
theorem:

> The monodromy of Semaev's summation polynomials, and what it fixes in
> index calculus

Your call — `../paper.tex` still carries your original title, unchanged.

### 3. Get the proofs read by someone

Section 9 says, in the paper's own voice, that the arguments have not been
refereed. That is the honest state. The two steps to hand a reader are
**Lemma 2.3** (Artin's theorem for a quotient by a finite group acting faithfully)
and **Lemma 3.2** (properness of the preimage of `E[2]`, specifically in
characteristic 2 where `E[2]` is non-reduced). Both are short. Posting before that
is a normal thing to do with a preprint, but it is a choice, not a default.

---

## Metadata for the web form

**Primary category:** `math.NT` (Number Theory)

**Cross-list:** `cs.CR` (Cryptography and Security)

The main results are arithmetic-geometric statements about a family of
polynomials; the motivation and sections 5–7 are cryptographic. If you would
rather lead with the application, swap them — `cs.CR` primary with `math.NT`
cross-list is equally defensible.

**MSC 2020:** Primary 11G05, 12F10; Secondary 11T71, 14H52, 11Y16
(also in the paper, under the abstract)

**ACM class:** `E.3` (Data Encryption)

**Comments field** (suggested):

```
15 pages. Verification code and data included as ancillary files.
No ECDLP speedup, security reduction, or hardness result is claimed.
```

**License:** CC BY 4.0 is the usual choice for a preprint of this kind. arXiv's
default non-exclusive license also works. Pick deliberately — it cannot be
narrowed later.

---

## Prior-art status, stated exactly

Section 9 makes a *measured* statement rather than a novelty claim, because that
is what the search supports. What was actually read, in full text:

| source | reachable | states Thm 3.4 or 4.2? |
|---|---|---|
| Semaev, arXiv:1504.01175 (2015) | yes | no — no Galois/monodromy/factorization content |
| Kosters–Yeo, arXiv:1503.08001 (2015) | yes | no — no Galois/monodromy/factorization content |
| Amadori–Pintore–Sala, *Finite Fields Appl.* 51 (2018) | yes (Oxford ORA) | no |

All three set up the basic theory of `S_m` in detail and state the degree,
symmetry and absolute irreducibility; none discusses the Galois group, splitting
field, monodromy, or the factorization type of a specialized fibre. Amadori–
Pintore–Sala Theorem 2 is the citable collection of the classical facts, and it
attributes them to Semaev's 2004 preprint. It also supplied one improvement to
the paper: the leading coefficient of `S_m` in its last variable is `S_{m-1}^2`,
which makes half of Proposition 3.9 classical and is now cited as such.

`eprint.iacr.org` returned HTTP 403 to every request from the environment this
was prepared in, so Semaev's original 2004/031 was read only through the three
sources above rather than directly. That did not end up mattering for any
attribution — Amadori–Pintore–Sala restates its content as their Theorem 2 with
attribution — but it is worth knowing, and it is the reason section 9 invites
pointers rather than asserting priority.

## Reproducing the verification

```sh
make -f Makefile.arxiv stage
cd anc && python3 verify.py --out raw-result.json    # ~70 s, no dependencies
```

Deterministic at seed 20260807, and byte-reproducible: nothing
environment-dependent is written into the result file (timing, interpreter and
platform go to stderr). Two consecutive runs were confirmed identical.
sha256 of the shipped `raw-result.json`:
`a7f3cb1265cf110291e8169bcea184374c807372fb7ca3ad841f29eed4b57974`
