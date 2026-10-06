# Addendum 01 to the NA-5 preflight note

**Written:** 2026-09-18, immediately after the note, on the same task.
**Supersedes nothing.** The note's findings stand. This corrects one statement in
it and records what the correction revealed.

## The note's NA-5 status line is WRONG, and here is the correction

`preflight-note.md` closes with "**NA-5 IS NOT DISCHARGED**". That was true when
written and is false now. Merging `origin/main` immediately afterwards brought in
a CONCURRENT LANE'S WORK that discharges it:

- `experiments/EXP-QSP-82a906/specification.yaml` — v1, `status: approved`,
  `source_proposal: IDEA-20260916-b84e2d` (**the same idea NA-5 names**)
- `ledger/hypotheses/H-QSP-411d8f.yaml` — `status: specified`, H1 of
  `H-QSP-645a07` restated as a falsifiable claim at `m = 2` cells
- `ledger/decisions/DEC-20260917-f37ca4.yaml` — the approval
- `ledger/handoffs/TASK-20260917-66ec2b.yaml` — execution handoff to the executor

So NA-5 is discharged **by that lane, not by this one**. This session's own design
dispatch died on an API weekly rate limit before reading any record, which in
hindsight prevented a duplicate contract against the same idea. `H-QSP-e15e15` and
`EXP-QSP-bb346d` remain minted, verified free and **unused**.

This session stopped rather than continuing, per the concurrency rule that another
session on the same goal is not a stop but duplicated work is waste.

## What the collision revealed: THE TWO CONTAINERS DO NOT HAVE THE SAME ENVIRONMENT

`EXP-QSP-82a906`'s `environment.present/absent` block records, measured in ITS
session: `numpy 2.4.4` **present**; `sympy` **absent** ("python import
ModuleNotFoundError"). Measured in THIS session's container the same day
(`out/engines.txt`):

| module | their container | this container |
|---|---|---|
| `numpy` | **2.4.4 present** | **ABSENT** (ModuleNotFoundError) |
| `sympy` | **absent** | **1.14.0 present** |

Both measurements are honest; the containers differ. Two consequences for a
contract that has been approved but **whose `runs/` is still empty**, so both are
amendable before execution rather than after:

### (a) Instrument I2 permits a dependency that may not be there

`I2_python_sylvester` reads "numpy 2.4.4 may be used for arrays". An executor
landing in a container like this one has no numpy, and a permitted-but-absent
dependency is the kind of thing that surfaces as a stage failure rather than as a
clean refusal. Bit-packed integer arithmetic needs no numpy at all — this note's
own `code/preflight_resultant.py` does 32x32 Sylvester determinants over
`F_{2^n}` in pure Python with no imports beyond `time` and `random`.

### (b) The sympy prohibition is RIGHT, but recorded for a container-specific reason

I2 says the implementation "MUST NOT import sympy, sage, galois, flint, or ntl
(all absent or forbidden as a hidden dependency)". The prohibition is correct.
The stated reason — absence — does not travel: in a container where sympy IS
present, "absent" reads as no longer applicable, and the prohibition looks like
portability hygiene rather than a correctness rule.

**The durable reason is that sympy is WRONG for this, not that it is missing.**
`sympy.GF(2**k)` is the ring of integers modulo `2**k`, NOT the field extension
`F_{2^k}` — demonstrated in `code/sympy_domain_trap.py` /
`out/sympy_domain_trap.txt`:

    GF(2**4).characteristic()  ->  16     (a field of order 16 has characteristic 2)
    2 * 8 mod 16               ->  0      (2 is a zero divisor; F_16 has none)
    2 ** -1                    ->  NotInvertible: zero divisor

and sympy is simultaneously CORRECT over the prime field `F_2`, which is what
makes it dangerous: it half-works, so a Sylvester resultant built on
`GF(2**n)` would compute in `Z/2^n` and emit plausible numbers with no error
raised. That is a wrong eliminant degree, which is the experiment's primary
measurement.

Suggested amendment, for that lane to accept or refuse — it is their contract and
this session has no authority over it: restate the prohibition as a correctness
rule with the demonstration cited, and drop or make-optional the numpy permission.

## Scope

Unchanged from the note. Nothing here measures a chain system, an eliminant
degree or `kappa`; nothing licenses any claim about `H-QSP-645a07`, H1, (E) or
`kappa`; `DEC-20260917-793ae2` stands at `weaken`. Routed to the bus as
`MSG-20260918-*` because a contract whose runs have not started can still be
amended cheaply, and after execution it cannot.
