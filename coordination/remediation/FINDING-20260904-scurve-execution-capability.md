# The execution-capability question 20 SafeCurves goals are blocked on is answerable — and answered

Recorded 2026-09-04 by the standing coordinator session (`coordinator-aes-1`) while running
`/launch-research-harness`. **No goal record is edited, no decision is minted, no batch is
opened.** This settles a shared prerequisite; the 20 decisions it unblocks remain each
goal's own to make.

## The shared gate

`tools/goal_portfolio_health.py` lists 30 goals as *batch complete — needs a Coordinator
checkpoint and the next batch*. Twenty are `GOAL-SCURVE-*`, one per curve, and every one
carries the same `next_action`, verbatim apart from identifiers:

> BATCH-… IS CLOSED. … No task in this batch remains dispatchable and NO criterion cell has
> been adjudicated. ONE ACTION: a Coordinator decision on whether to open a successor batch
> executing the archived audit plan's own first-ranked lane. **That decision must first
> record whether this environment can supply the execution capability the plan assumes** —
> this batch's producer had no shell and performed no arithmetic, so every stated numeric
> relation in the dossier is a transcription plus a pending check.

So twenty decisions are blocked behind one factual question about the environment. The
capsules say the same thing in their own words: *"this session has no arbitrary-precision
arithmetic tool available, and typing a 68-digit decimal by hand would be a fabricated
computation."* That producer was right to refuse.

## The answer: YES, and here is the demonstration

I ran the pending checks for `GOAL-SCURVE-137bd9` (NIST P-224) against its committed
`parameter-capsule.yaml`, using Python integers only — no PARI, no network.

**L-FIELD**

| check | result |
|---|---|
| `p == 2^224 − 2^96 + 1` | **true** |
| `p` probable prime (Miller–Rabin, 64 rounds, seed 20260904) | **true** |
| `p mod 4` | **1** — confirms the capsule's assertion, which it had marked "still to be machine-checked in L-FIELD" |
| `a == p − 3` | **true** |
| `n` probable prime (same test) | **true** |
| `n` trial division < 200000 | no factor, consistent with primality |

**L-BASE**

| check | result |
|---|---|
| `G` satisfies `y² = x³ + ax + b (mod p)` | **true** |
| `n·G = O` under the affine group law | **true** |
| `(n−1)·G` finite, so `ord(G)` is exactly `n` | **true** |
| `#E = n·h` and `t = p + 1 − #E` | `t = 4733100108545601916421827343930821` |
| Hasse: `\|t\| ≤ 2√p` | **true** |

**L-TWIST**

    #E' = 2p + 2 − #E = p + 1 + t
        = 26959946667150639794667015087019635406658024805628224565337410229703
    both forms agree; #E' is odd
    small factors of #E' below 200000:  3² · 11 · 47   (64-digit cofactor remains)

**L-DISC** — `t² − 4p` is negative as required, equal to
`−85437550031088170535288062946642707984656696913911429425696631461483`.

**L-TRANSFER** — no `k ≤ 100` satisfies `p^k ≡ 1 (mod n)`, so the embedding degree admits
no small value in that range.

Every transcription in the capsule that these checks can reach is **correct**, and the
derived quantities the capsule listed as *to be certified* are now computed.

## What this does NOT establish, stated so no successor overreads it

- **Primality is probabilistic.** Miller–Rabin with 64 seeded rounds is overwhelming
  evidence, not a proof. A certificate (ECPP or Pocklington) is a separate lane and is
  OPEN AND UNATTEMPTED.
- **Provenance is untouched.** I checked internal consistency and arithmetic against the
  committed capsule. I did NOT re-retrieve the parameters from a primary source, so nothing
  here speaks to whether the capsule transcribed the right curve. The capsule's own
  two-source agreement is the only provenance evidence, and it stands unexamined by me.
- **The embedding degree is not computed**, only bounded away from `k ≤ 100`. Its exact
  value needs the factorisation of `n − 1`.
- **Twist security is not adjudicated.** The small factors above are reported as measured;
  whether the 64-digit cofactor is prime is unfactored and OPEN AND UNATTEMPTED.
- **Nineteen other curves are unchecked.** Only P-224 was run. The capability finding
  generalises to the environment; the *results* generalise to nothing.
- **No criterion cell is adjudicated** for any goal, exactly as each `next_action` says.

## Consequence for the 20 blocked decisions

The prerequisite each one names — *record whether this environment can supply the execution
capability* — is now recorded, with a worked demonstration rather than an assertion. The
capability exists: arbitrary-precision integer arithmetic, the affine elliptic-curve group
law, probabilistic primality testing, and the Hasse/twist/discriminant/embedding derivations
all ran here in seconds.

**One caveat that belongs in every one of those decisions.** Capability is per-session, not
per-repository. Earlier today, in `GOAL-ECRANK-002 BATCH-e0caa5`, two producer tasks in the
*same batch* reported different environments — one with `cypari 2.5.6 / PARI 2.15.4`, one
with no `gp`, no `cypari`, no `cypari2`, no Sage — and the second could not attempt half its
protocol as a result. Pure-Python arithmetic of the kind used above needs no external
library and is therefore the safe assumption; anything requiring PARI is not, and a handoff
that needs it must say so and be checked at dispatch rather than discovered mid-run.

## Suggested disposition, for each owning goal

1. Record this capability finding in the successor decision, with the caveat above.
2. Scope the first successor batch to lanes that need **only** stdlib arithmetic — L-FIELD,
   L-BASE, L-TWIST, L-DISC are all demonstrably reachable.
3. Treat primality **certificates** and any factorisation lane as separately provisioned,
   since they may want PARI.
4. Re-run the checks above per curve rather than transferring P-224's results.

Nothing here asserts that any curve is safe or unsafe, and no cryptographic claim of any
kind is made. Arithmetic verification of a published parameter set is a transcription check,
not a security evaluation.
