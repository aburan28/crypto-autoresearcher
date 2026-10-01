# Addendum 02 — the window closed, and neither flagged risk materialised

**Written:** 2026-09-30, twelve days after the note and addendum 01.
**Supersedes nothing.** Both earlier documents stand as dated records. This
records what happened next, because addendum 01 carries a time-sensitive claim
that is now false, and a stale warning left unmarked reads as a live one.

## The claim that expired

Addendum 01 and `MSG-20260918-6f8b91` both argue from "the contract's `runs/` is
still EMPTY so both are amendable before execution rather than after". That was
true on 2026-09-18. **It is false now.** `experiments/EXP-QSP-82a906/runs/` holds
five runs:

    RUN-QSP-28ef77   status=completed_valid  valid=True
    RUN-QSP-55bd71   status=completed_valid  valid=True
    RUN-QSP-5ec02a   status=completed_valid  valid=True
    RUN-QSP-c4b336   status=completed_valid  valid=True
    RUN-QSP-c6490f   status=completed_valid  valid=True

The amendment window is shut. Nothing in addendum 01 should now be read as
proposing a change to a contract that has since executed.

## Neither risk bit, and the reason is in their implementation

This is the part worth recording, because a warning that did not fire is easy to
leave looking open. Both were checked against the executed package, not assumed.

**(a) The numpy permission did not become a hard dependency.**
`experiments/EXP-QSP-82a906/implementation/runlib.py:88-91` imports numpy inside
a try/except and records `deps["numpy"] = "not installed"` on failure. numpy is
therefore ENVIRONMENT METADATA in that package, not a requirement, so an executor
in a container without it is unaffected. The permission in `I2_python_sylvester`
was never exercised as a dependency.

**(b) sympy was never imported.** The same file records
`"sympy": "not imported"` (line 102). No implementation file under that
experiment has a top-level `import sympy` or `from sympy`. The `GF(2**k)` trap
demonstrated in this task's `code/sympy_domain_trap.py` had no opportunity to
corrupt an eliminant degree there.

So the two flags were cheap and correctly aimed, and the receiving lane had
already written defensively against both. Recorded as NOT-MATERIALISED rather
than quietly dropped.

## What remains true from the note and addendum 01

- The engine inventory (`out/engines.txt`) and the two demonstrations
  (`code/preflight_resultant.py`, `code/sympy_domain_trap.py`) are unchanged and
  still reproduce. This container on 2026-09-30 still has `sympy 1.14.0` present
  and `numpy` ABSENT, the same divergence from `EXP-QSP-82a906`'s recorded
  environment that addendum 01 reports. **The divergence is durable, not a
  one-day artefact.**
- The durable reason to forbid `sympy.GF(2**k)` as a model of `F_{2^k}` is that
  it is WRONG, not that it is absent. That argument is independent of any
  contract and of any container.
- NA-5 remains discharged by the other lane, not this one. `H-QSP-e15e15` and
  `EXP-QSP-bb346d` remain minted, free and UNUSED.

## What this does NOT say

It says nothing about whether `EXP-QSP-82a906`'s five runs are correct, what they
measured, or what they imply for `kappa`, H1 or (E). This session has not read
their results and is not reviewing them. `valid=True` here is quoted from their
own manifests as evidence that the runs completed, nothing more.
