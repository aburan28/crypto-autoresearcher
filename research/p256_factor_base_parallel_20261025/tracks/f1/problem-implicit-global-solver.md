# Certified global implicit solving for the P-256 symmetric Dickson circuit

- **Status:** open
- **Kind:** implementation and proof gap; bounded software resource stop recorded separately
- **Affected work:** TASK-20261025-cfb933; F1 of the committed factor-base plan
- **Next action owner:** Coordinator to assign a follow-on implementation/proof task
- **Last updated:** 2026-10-25

## Problem

No supplied implementation or bound currently solves the joint symmetric Dickson
membership circuit and S4 on P-256 while avoiding both expanded elimination growth
and complete C(N+2,3) backward-state enumeration.

The required input is E/P-256, a public finite target Q, depth k≤96, and a generic
norm-one coset terminal c. The existing short circuit remains a valid input, but
short representation does not certify a global solving bound or a complete ECDLP
algorithm. Canonical base size M includes only actual curve lifts.

## Evidence and uncertainty

- **Observed:** [checks-02/checks.json](checks-02/checks.json) and
  [verification-01.json](verification-01.json) certify finite domains, matched
  actual M=3,7,10 and 27 exact signed solution sets. [forward-01/receipt.json](forward-01/receipt.json)
  retains joint k=1,2 completions and a k=3 30-second watchdog stop under a 2 GiB
  process address-space cap. Commands, adapters, stdout and stderr are retained.
- **Derived:** the generic terminal symmetric membership ideal has length S³ but
  C(S+2,3) geometric points, and is nonreduced for S≥2. The scalar generic fibre
  is unramified; the remaining multiplicities come from the symmetric diagonal.
  See [derivations.md](derivations.md).
- **Suspected explanation:** no claim about the cause of the k=3 software cost;
  expression growth and nilpotents are possible contributors, not isolated causes.
- **Missing capability:** a certified radical/local-algebra treatment integrated
  with solving and a controlled elimination method on the unexpanded circuit.
- **Not established:** a mathematical lower bound for every implicit solver, a
  hardness conclusion, a competitive ECDLP algorithm, or a timing extrapolation.

## What would unblock it

- [ ] Deliver an executable solver taking only E,Q,k,c and the circuit; return
  all signed decompositions with a replayable completeness certificate without
  enumerating every domain triple or storing M dense pair polynomials.
- [ ] Give a justified cost bound in k,M,d including radical/local algebra,
  rejected roots, lift/subgroup checks, setup and failed queries; state assumptions.

These conditions would establish a new scoped relation solver. They would still
leave independent review, matched total-cost experiments, relation independence,
linear algebra and final target attachment as separate obligations.

## Next discriminating step

- **Action:** implement the auxiliary-variable chain with explicit diagonal
  radicalization or local-algebra root extraction; compare its exact elimination
  and state counts with the already fixed k=1,2,3 generic cases.
- **Controls:** unchanged P-256 field and public targets from checks-02; forward
  expanded and complete inverse formulations; ramified and generic terminals.
- **Limits:** use the handoff memory envelope and a declared per-process watchdog;
  scientific timing trials require repository admission and a frozen protocol.
- **Outcomes:** a complete certificate enables deeper implementation validation;
  a watchdog or adapter failure records only that bounded attempt; a proved
  representation bound narrows the exact representation and leaves others open.
- **Recheck trigger:** a radicalization implementation, another algebraic adapter,
  or a new structural lemma for this specific symmetric system.

## Resolution and history

Unresolved. This scoped record is ready for the Coordinator to link into the
repository-level problem index; the track's write scope excludes shared files.
