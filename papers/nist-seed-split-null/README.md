# Small-prime splitting of the NIST/ANSI prime-field curves

**Status:** manuscript draft (Markdown, not typeset), anonymized, not
submitted, and not cleared for submission or posting.

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
- `DEVIATIONS.md`, which records D1–D3:
  - D1: runs launched without a resume checkpoint;
  - D2: the 48-bit validation kept no rows (resolved 2026-10-30: rerun with rows, exact reproduction, audited);
  - D3: there is no frozen `experiment.protocol/v1` record and no conforming
    export.

**Change class:** analysis (no advance, engineering, relabelling or
accounting change to any method's cost).

## Build

The draft is not typeset yet. Typesetting means converting to LaTeX with a
`Makefile` that includes `../paper.mk`, and passing `make check`. That
toolchain was not available in the session that wrote the draft.

## Owed before submission

- [ ] Typeset in LaTeX through `paper.mk`; `make check` passes; commit the PDF.
- [ ] Clear D1: push a resume checkpoint before any rerun.
- [x] Rerun the 48-bit validation with per-curve rows retained (clears D2; done 2026-10-30).
- [ ] Run a real-field SEA null, at least 10,000 prime-order curves per field.
- [x] Weighted statistic and L(1, χ) for prime239v1 against the same null:
      `research/nist_seed_lvalue_20261030/` (L̂ = 0.246, 0.25th percentile,
      lowest of 61; §6).
- [ ] Novelty audit: prior analyses of NIST seed curves and of Elkies-prime
      distributions (Shparlinski–Sutherland; Castryck–Hubrechts).
- [ ] Independent review (`review-run`) of `runs/heldout.json` and
      `runs/rows.jsonl`.
