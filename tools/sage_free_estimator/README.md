# Sage-free lattice-estimator harness

Runs the [lattice-estimator](https://github.com/malb/lattice-estimator) without
Sage, so cost-model work can happen in environments where Sage is unavailable.

## Why

`GOAL-MLKEM-003` was blocked three times on instrument availability: G6K twice
(BATCH-003, BATCH-005) and Sage once — `EXP-MLKEM-015` ran under Sage 10.9 on a
machine this harness does not have, so its numbers could be cited but never
re-derived. That made every later batch argue about archived outputs it could
not recompute.

The estimator's Sage surface turns out to be 27 names, and all but three are
elementary math (`RR`, `log`, `sqrt`, `exp`, `binomial`, `find_root`, `erf`, …).
`shim/sage/all.py` provides them over `mpmath` and `scipy`.

## The control is the whole point

A shim that is subtly wrong produces *plausible* numbers. This campaign has
already lost three batches to exactly that: `KN-FIND-014` rested on a misread
`/k_fft` factor that nobody re-derived until BATCH-008 falsified it.

So the shim asserts nothing on its own authority. It is trusted only insofar as
it reproduces values computed under **real Sage**, archived, and committed
before the shim existed — `RUN-MLKEM-015-001` (`EXP-MLKEM-015`, cited by
`EV-MLKEM-015`).

```
$ PYTHONPATH=tools/sage_free_estimator/shim:<estimator> \
    python3 tools/sage_free_estimator/known_answer_control.py

set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

PASS: every reference value reproduced exactly (delta 0.0)
```

**Exact equality is the bar**, not a tolerance. A shim that merely lands close
is one whose disagreements have not been explained. The control exits non-zero
otherwise, and the harness must not be used for a research claim until it agrees.

## Usage

```sh
git clone https://github.com/malb/lattice-estimator /tmp/le
git -C /tmp/le checkout 3e48ef421ec256afddb3e7d2249a77eab6e9ba12
PYTHONPATH=tools/sage_free_estimator/shim:/tmp/le python3 your_script.py
```

The pin `3e48ef4` is the commit `EXP-MLKEM-015` used. As of 2026-08-03 it is
also the repository's `HEAD`, so a fresh clone lands on it — but pin explicitly
rather than relying on that.

Requires `mpmath` and `scipy`. No Sage, no network at run time.

## Scope and limits — read before citing a result

- **Arora-Gröbner is unavailable.** `PowerSeriesRing` is a stub that raises
  rather than returning a wrong cost. No result from this harness may claim to
  be the *best attack overall* — only the best among the attacks it served.
  For Kyber-sized parameters Arora-GB is not competitive, but that is a claim
  about the literature, not something this harness establishes.
- **`line` is plotting only** and never lies on a cost path.
- **`RealDistribution` implements exactly two CDFs**, chi-squared and beta,
  which are the only ones the estimator calls. Any other kind raises.
- **The control covers `primal_bdd` under `RC.MATZOV`.** Other attacks and cost
  models run, but are not covered by an archived reference. Extending the
  control to a new combination means finding or producing a Sage-computed
  reference for it first — not assuming the shim generalises.
- Precision is `mpmath` at 200 bits where Sage used `RR`; agreement is exact on
  the controlled values, which is evidence for the covered paths and not a proof
  for uncovered ones.
