# SSI exact-contract clarification audit

This is a design-only successor for `IDEA-20260806-9c2f80`. It does not add a
new cryptanalytic mechanism and does not authorize an experiment.

## Inputs and protected history

The direct inputs are the immutable `EXP-SSI-fe3f76` specification and the
independent BATCH-6554d6 Validator and Red Team reports. The predecessor,
its ledger decision, evidence, review files, and the global schema registry are
not edited. The current successor is `EXP-SSI-8e589d` and carries explicit
`supersedes: EXP-SSI-fe3f76` lineage.

The exact source parameters remain the two paper-named expressions:
`5*2^248-1` and `27*2^500-1`. Their exact bit lengths are recorded separately
from the conventional security-level labels 256 and 512. The new synthetic
graph diagnostic is deliberately not a toy SSI curve or a prime-field claim.

## What the successor changes

The successor converts the prior residual prose into a frozen design contract:

1. It fixes the extension-field basis, byte version, coefficient order, exact
   field/vertex widths, and a required finite vertex manifest.
2. It makes `T_q` finite-or-infinite by an explicit `L_steps`, common FOE unit,
   counter schema, builder cap, restart cap, and seed streams.
3. It defines an HNF order serialization, branch-specific record layouts, an
   open-addressed index, exact `b_shared`, C middle descriptors, and retained
   versus attempted counts.
4. It states the directed path, HNF pullback, saturation, final output gate,
   and C multi-entry access limit.
5. It gives separate valid semantic nulls for each declared branch and makes
   S=0/singleton-manifest cases explicitly not applicable.
6. It freezes paired replay traces, C pair statistics, and a synthetic graph
   H-ADV-1-R diagnostic with exact squared rational gates.

All of these remain unverified assumptions or design inputs. No result is
inferred from their presence.

## Non-duplication boundary

The generic advice frontier, known-endomorphism database, delta-screen
reparameterization, and three-way pair accounting are inherited mechanisms
from the admitted proposal. Encoding choices and control statistics are
protocol repairs, not novelty claims. The successor cannot support an
all-advice lower bound, a sub-`p^(1/3)` result, an attack, or a security claim.
