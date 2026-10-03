# C1 inclusion rules (EXP-BINSTD-7100ec Stage 0)

## In scope
- Files under `ledger/` and `knowledge/` whose text discusses binary /
  characteristic-two / FIPS-sect / Koblitz index-calculus **cost** laws
  (time, relation yield as a multiplicative cost, degree/size laws used as
  cost).
- A filed law is a counterexample to C1 if it reads curve coefficients `a` or
  `b` as an input to the cost expression other than through `lambda_x` / `r`
  (or an explicitly labelled Assumption-1 scalar named as such).

## Out of scope / pre-registered exceptions
- Trace-parity arity constraints `Tr(x)+Tr(a)` that bound admissible arity
  (constraint on `m`, not a multiplicative cost factor) — pre-registered
  exception class per HOLD-B / IDEA-20260922-1a081a review.
- Proposals that are only design text without a filed cost formula.
- Records filed after the Stage-0 freeze timestamp.

## Method
1. Scan `ledger/**/*.yaml` and `knowledge/**/*.md` for binary-IC cost markers.
2. For each candidate, record whether `a`/`b` appear outside `lambda_x` /
   yield / order contexts.
3. Emit `c1-census.json` with `counterexamples` list (possibly empty).
