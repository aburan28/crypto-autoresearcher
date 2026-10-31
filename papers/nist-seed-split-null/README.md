# Small-prime splitting of the NIST/ANSI prime-field curves

**Status:** manuscript draft, typeset in LaTeX (`paper.tex`, `make check`
passes: no LaTeX errors, references and citations resolved, no overfull
boxes, 8 pages). Anonymized, not submitted, and not cleared for submission or
posting. The built PDF (about 320 KB) is not yet in git: it exceeds the 64 KiB
data limit and waits for an artifact-store push (see Build).

## What it says

- The published-low small-prime split-count pattern among the NIST/ANSI seed
  curves survives the prime-order confound, which is worth 0.5–1.4 splits.
- It also survives a correction for the choice of cutoff on the nineteen named
  curves (p ≈ 0.006).
- It **does not replicate** on 42 held-out unpublished draft-eligible curves
  under a test fixed before data (0.574 of 102 pairs, p = 0.29).
- One low outlier remains: prime239v1.

## What it does not say

- It does not claim any ECDLP weakness, mechanism, or designer intent.
- It does not explain why the eleven curves were omitted; the open problem
  `problems/nist-seed-selection-rule-unexplained.md` remains open.
- It does not validate the null over the real fields with large SEA samples.

## Evidence

All of it is in `crypto-autoresearcher:research/nist_seed_split_null_20261029/`:

- scripts, run records, `rows.jsonl` and figures;
- `PROTOCOL.md` (pushed in `bd5d146b` before the held-out data) and
  `protocol.json`;
- `DEVIATIONS.md`, which records D1–D4:
  - D1: runs launched without a resume checkpoint;
  - D2: the 48-bit validation kept no rows (resolved 2026-10-30: rerun with rows, exact reproduction, audited);
  - D3: there is no frozen `experiment.protocol/v1` record and no conforming
    export;
  - D4: that rerun itself had no frozen protocol record or export (a repeat of D3).

**Change class:** analysis (no advance, engineering, relabelling or
accounting change to any method's cost).

## Build

```sh
make            # paper.pdf (pdflatex, bibtex, two more passes)
make check      # rebuild from scratch; fails on errors, unresolved refs, overfull boxes
make eprint     # eprint-submission.zip
make deanonymize  # restores authors from an untracked AUTHORS file
```

Sources: `paper.tex`, `refs.bib`, and `figures/*.pdf`. The figures are
converted with `rsvg-convert` from the study's SVGs
(`research/nist_seed_split_null_20261029/fig_{null,sweep,heldout}.svg`). The
paper needs TeX Live's latex-base, latex-recommended and fonts-recommended
packages.

`paper.pdf` is about 320 KB, over the repository's 64 KiB data limit
(AGENTS.md, "Data files live in the artifact store"). Until someone with
store credentials runs `python3 tools/artifacts/artifacts.py push
papers/nist-seed-split-null/paper.pdf` and commits the `.artifacts.json` and
`.gitignore` it writes, `paper.pdf` is ignored locally and must be rebuilt
with `make`. The earlier Markdown draft, `paper.md`, was replaced by
`paper.tex` and survives in git history.

## Owed before submission

- [x] Typeset in LaTeX through `paper.mk`; `make check` passes (2026-10-30).
- [ ] Push `paper.pdf` to the artifact store (needs store credentials).
- [ ] Clear D1: push a resume checkpoint before any rerun.
- [x] Rerun the 48-bit validation with per-curve rows retained (clears D2; done 2026-10-30).
- [ ] Run a real-field SEA null, at least 10,000 prime-order curves per field.
- [x] Weighted statistic and L(1, χ) for prime239v1 against the same null:
      `research/nist_seed_lvalue_20261030/` (L̂ = 0.246, 0.25th percentile,
      lowest of 61; §6). Independently replicated by
      `research/nist_seed_l1chi_20261030/` (`CROSSCHECK.md`: log L̂ agrees to 3 × 10⁻¹⁴).
- [x] Novelty audit: prior analyses of NIST seed curves and of Elkies-prime
      distributions (`NOVELTY.md`, 2026-10-31: no earlier split-count or
      L(1, χ) test on these curves found; related work added to §1).
- [ ] Independent review (`review-run`) of `runs/heldout.json` and
      `runs/rows.jsonl`.
