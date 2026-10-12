# Idea-generator report: RQ-SSI-1946c9, 2026-10-04

Policy resolution: `research-deep -> anthropic:claude-opus-5 (effort=high)`.
The dispatched subagent inherited the available session model at high effort;
no Bedrock runtime was configured or contacted.  This was a zero-run ideation
session: no experimental result, timing, hardness result, or security claim is
reported.

## Ranked proposals

1. **`IDEA-20261004-edbd24` — control — adaptation — low cost.**  Trace
   secret-dependent decryption operations to determine whether a candidate
   consumes full EndRing knowledge or only a finite torsion-action quotient.
   The proposal requires a reverse reduction from the lowest sufficient
   quotient before accepting a full-EndRing dependency.
2. **`IDEA-20261004-e4c461` — mechanism — adaptation — low compute / medium
   implementation.**  Use a depth-two collision certificate to determine
   whether public evaluation silently requires transported edge labels,
   orientation, or equivalent auxiliary information.
3. **`IDEA-20261004-a09dd4` — composition — speculative — medium cost.**
   Require a negligible-distance bridge from the declared bare-EndRing
   challenge distribution to the structured PKE key distribution, plus a
   polynomial witness pullback.  Otherwise name the restricted structured
   EndRing assumption.

All three are audit or reduction components.  None is a PKE construction and
none has been approved as a hypothesis or experiment.

## Recommended first test

Run `IDEA-20261004-edbd24` on complete toy SÉTA cells.  Trace every
secret-dependent decryption call, normalize changes of torsion basis, replay
using only the degree/torsion-action quotient, and require zero disagreements
over every declared valid toy ciphertext.  Record every arrow in

`End(E) -> oriented/order generators -> rho_N -> minimal decryption state`

as proved, assumed, or missing in both directions.

This test ranks first because it is bounded and low-cost, has a published
positive-control interface, and directly separates “full EndRing is
sufficient to derive a trapdoor” from “recovering the consumed trapdoor is
equivalent to the declared EndRing problem.”  A toy replay establishes only
program factorization, not hardness, security, or an attack.

## Novelty and source audit

The generator read the complete retrieved specifications for SÉTA, SiGamal,
the isogeny UPKE paper, and LIT-SiGamal, then searched the SSI/EndRing proposal
and hypothesis corpus.  The source hashes and precise construction boundaries
are in `primary-source-intake.md` and each proposal's citations.

The mandatory `tools/build_frontier_map.py --match` check was run on each
claim plus mechanism.  Its highest matches were generic ECDLP rows (generic
lower bounds, isogeny-transfer facts, and walk constants), not PKE or EndRing
construction matches.  Because this research question is not an ECDLP
frontier, every proposal records `frontier_map: not_applicable` and instead
lists the applicable retrieved PKE sources and SSI corpus searches.  The match
output is category-mismatched evidence, not a novelty result.

Novelty remains conservative:

- the quotient and label-transport records are `adaptation`;
- the distribution compiler is `speculative`;
- no proposal claims that its audit is absent from all external literature.

## Honest accounting

### Objects considered

1. Reachable secret-operation quotient `Q_A(w)`.
2. Fibers of hidden edge labelings over a canonical public curve view.
3. Distribution bridge `T` together with recovered-witness pullback.

### Dominance

Existing SÉTA, SiGamal, and LIT-SiGamal-family schemes dominate all three
records as constructions and on functionality: the proposals construct no
PKE.  Those schemes do not supply the missing reverse-reduction,
label-transport accounting, or bare-EndRing distribution bridge audited here,
so they do not dominate the proposed diagnostic questions.

### Quantitative state-of-the-art delta

- time exponent: `0`;
- memory exponent: `0`;
- new audit outputs only: number of unresolved witness-ladder reverse arrows,
  conflicting public-view fibers, minimum auxiliary bits, support-mismatch
  mass, distribution distance, and witness-pullback failure count.

### Scoped closures

- Finite-witness sufficiency can close by exact oracle-program substitution.
- Public label transport can close through an explicit orientation/class
  action or a separating transport certificate.
- Rerandomization within a declared structured locus can close through a
  Markov walk on that state graph.
- A plain-EndRing embedding remains open until both distribution distance and
  witness pullback are proved for the exact contracts.

### Open directions

1. Prove or refute quotient-to-EndRing reductions with exact auxiliary data.
2. Determine whether the minimum label-transport data is equivalent to an
   oriented-EndRing variant.
3. Prove structured-graph mixing and projected-fiber weight bounds.
4. Find a pullback-preserving rerandomization that does not publish a path side
   channel.
5. If the scoped single-instance bridge fails, formulate and separately audit
   multi-instance, worst-case, or non-black-box reduction shapes.

## Validation boundary

The three records parse as YAML, pass merge hygiene and `git diff --check`, and
introduce no reported ledger-validator errors.  The full validator still
reports the same 122 repository baseline errors in pre-existing proposals,
handoffs, experiments, runs, and decisions; none names these three proposal
files.  This session did not edit that unrelated baseline debt.
