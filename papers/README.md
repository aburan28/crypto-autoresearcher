# Papers

Every manuscript generated from this program's results lives here, one
directory per paper. Ledger records (`H-*`, `EV-*`, `DEC-*`, `KN-*`) are the
evidence a paper cites; a paper never edits one.

| directory | title | status |
|---|---|---|
| [`semaev-conservation-specialization/`](semaev-conservation-specialization/) | Conservation and Specialization in Semaev-Based Index Calculus over Prime Fields | manuscript draft (LaTeX), anonymized, not submitted; two blockers in its README |
| [`nagao-lemma4-note/`](nagao-lemma4-note/) | A remark on the "fake first fall degree" of Nagao (ePrint 2015/984) | technical note (Markdown, not typeset), not submitted |
| [`binary-ic-blog/`](binary-ic-blog/) | Why index calculus still can't touch binary elliptic curves (and where it might) | blog draft (Markdown), not for publication until its checklist is done |
| [`nist-seed-split-null/`](nist-seed-split-null/) | Small-prime splitting of the NIST/ANSI prime-field curves: a prime-order null, a cutoff sweep, and a held-out test | manuscript draft (LaTeX, `make check` passes), anonymized, not submitted; PDF awaits artifact-store push; owed items in its README |
| [`first-fall-lean/`](first-fall-lean/) | Machine-checked first-fall-degree reasoning in Weil-descent ECDLP | manuscript draft (LaTeX, `make check` passes), anonymized, not submitted; PDF awaits artifact-store push; owed items in its README |

Conventions shared by every paper here and by the sibling repositories
(`aburan28/cryptanalysis`, `aburan28/crypto`, `aburan28/crypto-autoresearcher`,
`aburan28/ml-cryptanalysis`), as set out in the "Papers" section of `AGENTS.md`:

- one directory per paper, holding the root `.tex` (or the `.md` of a draft not
  yet typeset), its sections and bibliography, a `README.md` (status banner,
  what it says, what it does not say, how to build, reproduction pointers, the
  checklist owed before submission), an `abstract.txt` and the built PDF;
- the build is `paper.mk` in this directory: a paper's `Makefile` sets `TEX`,
  `SECTIONS`, `BIB` and, for figures or other files the build reads, `ASSETS`,
  and includes it (`make`, `make check`, `make arxiv`,
  `make eprint`, `make deanonymize`, `make clean`);
- every number cites a committed artefact in this repository or a sibling
  (`crypto:`, `cryptanalysis:` or `crypto-autoresearcher:` prefix); a stage
  diagnostic is never reported as a speedup; every end-to-end row has verified
  answers; every change is classed as advance, engineering, relabelling or
  accounting;
- `make check` must pass (references and citations resolved, no LaTeX errors,
  no overfull boxes) before a PDF is recommitted, and the PDF is rebuilt
  whenever a cited number, conclusion or figure changes;
- sources are anonymized (`\author{Anonymous}`); `make deanonymize` restores
  the authors from an untracked `AUTHORS` file copied from `AUTHORS.example`.

Add a new paper as a new subdirectory and a row in the table above.
