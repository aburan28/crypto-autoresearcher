# Experiment Contract: Parity-Repair Complexity Phase Diagram

Date: 2026-07-29

## Hypothesis

For the ordinary known-target setting of Proposition 5.1, write

```text
m=q^a, c=q^(r*a), s_c=q^(s*a), 0<=s<=r<=1.
```

The source and candidate exponents are

```text
S_known=max(10a, (1-3a)/4),
C_known=max(6a, (1+(-3+2r+4s)a)/4).
```

The candidate strictly improves the source bound exactly after

```text
a>1/(43-2r-4s).
```

Its own first-term crossover is

```text
a=1/(27-2r-4s).
```

Without a new cross-target reuse theorem, the crater factor also
multiplies the repaired prefix. The corresponding full-volcano
exponents are

```text
S_full=max(10a, (1-a)/4),
C_full_no_reuse=max((13/2)a, (1+(-1+2r+4s)a)/4).
```

This candidate strictly improves the extrapolated source bound after

```text
a>1/(41-2r-4s),
```

and its own crossover is `a=1/(27-2r-4s)`.

If target-independent reuse of the repaired prefix is later proved, the
hypothetical first term is `6a` and the crossover becomes
`a=1/(25-2r-4s)`. This reuse case is recorded separately and must not be
reported as an established range.

## Status

HEURISTIC COMPLEXITY CONSEQUENCE / EXACT RATIONAL-ARITHMETIC CHECK

## Null hypothesis

Any symbolic equality, crossover, or dominance boundary fails under
exact rational arithmetic, or the claimed improvement appears below its
stated onset.

## Parameters

Evaluate exact fractions for

```text
r in {0, 1/4, 1/2, 3/4, 1}.
s in {0,r}.
```

For each `r`, evaluate points immediately below, at, and above every
registered boundary.

## Metrics

- source and candidate term exponents;
- candidate crossover equality;
- equality at the improvement onset;
- strict improvement immediately above;
- no strict improvement immediately below;
- worst parity-defect case `r=1`;
- subpolynomial parity-defect limit `r=0`.

## Positive controls

- At `(r,s)=(0,0)`, recover onsets `1/43` and `1/41`, the
  known-target and no-reuse crossovers `1/27`, and the hypothetical
  reuse crossover `1/25`.
- At `(r,s)=(1,0)`, recover known-target onset/crossover `1/41,1/25`.
- At `(r,s)=(1,1)`, recover known-target onset/crossover `1/37,1/21`
  and no-reuse full onset/crossover `1/35,1/21`.

## Negative controls

- Below each onset, the candidate must not be marked as a strict
  improvement.
- At each onset, source and candidate exponents must be equal.
- Mutating the candidate-crossover denominator by one must fail the
  equality of the candidate's two terms.

## Success criterion

All exact equalities, sided dominance checks, and mutations pass.

## Falsification criterion

Any failed exact comparison rejects the phase-boundary claim. Passing
does not validate the underlying Kani algorithm, smooth-number
heuristic, field bound, or crater amortization.

## Reproduction command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_parity_repair_phase_diagram.py
```
