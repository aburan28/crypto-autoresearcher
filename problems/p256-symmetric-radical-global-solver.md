# P-256 symmetric membership still lacks a costed global relation solver

- **Status:** `investigating`
- **Kind:** implementation gap; proof gap; bounded process watchdog outcomes
- **Affected work:** [F1](../research/p256_factor_base_parallel_20261025/tracks/f1/report.md), [cubic-divisor continuation](../research/p256_factor_base_parallel_20261025/tracks/f1/cubic-divisor/report.md), TASK-20261025-cfb933 and TASK-20261025-13c38e
- **Next action owner:** Coordinator for a prospective solver study
- **Last updated:** 2026-10-25

## Problem

The P-256 Dickson-coordinate base now has exact symmetric and radical
membership formulations, but neither a general implicit relation solver nor a
bound on its complete cost in base size and chain depth has been established.

The target is the published P-256 prime-order group. A signed base with M
canonical x-coordinates is fixed through a norm-one torus fibre. The current
relation problem has three summands and uses the exact symmetric S4 polynomial.
Constructed solutions certify correctness only.

## Evidence and uncertainty

- **Observed:** F1 retains nine matched domains and 27 complete signed query
  sets. Initial expanded forward solving completes depths 1 and 2; its fixed
  depth-3 attempt reaches a process watchdog. These are actual-field checks,
  not field-size scaling evidence.
- **Derived and checked:** the triple-equal terminal scheme has length S^3
  and C(S+2,3) distinct states. Generic scalar fibres do not eliminate its
  symmetric multiplicities. Cubic-divisor membership removes those
  multiplicities on the distinct-coordinate stratum; repeated-coordinate
  strata are handled separately.
- **New implementation evidence:** the continuation completes the original
  depth-3 target, six complete query sets, 21 exact algebra certificates and
  a separate sparse replay of 386 critical pairs. Three depth-4 watchdog
  outcomes remain unknown. See the immutable per-attempt receipts.
- **Missing capability:** costed complete solving without enumerating the
  entire triple space or expanding exponentially with chain depth.
- **Not established:** a performance advantage, a general lower bound for
  implicit algorithms, a degree-of-regularity bound, or a P-256 ECDLP result.
  Arithmetic witness checks through depth 96 are not complete relation solves.

## What would unblock it

- [ ] Provide a complete solver or explicit conditional cost argument in M,
  arity and depth, including repeated coordinates, rational roots, signs,
  subgroup checks, failed queries and memory.
- [ ] Validate complete sets against the retained finite-domain references,
  including the depth-4 unknowns, with matched controls before any performance
  interpretation.
- [ ] Independently check the algebra and any proposed scaling argument.

These conditions would establish a scoped relation-solving interface. Relation
density, useful rank, linear algebra and target attachment would still require
their own evidence. No official goal or hypothesis transition is made here.

## Next discriminating step

Inspect the unexpanded cubic-remainder circuit and its elimination strategy on
the retained depth-3 and depth-4 inputs. A complete certificate permits a
prospective larger-depth study; a process stop stays unknown; a counterexample
requires an additive correction. Do not rescore or replace the original stops.
Machine protection is the stated per-process memory/watchdog envelope, not a
campaign spending cap. Recheck when a complete extractor or solving-degree
argument is supplied.

## Resolution and history

2026-10-25: opened with the first exact symmetric and cubic-divisor packages.
The auxiliary-isogeny construction has its separate
[existing decomposition problem](pkm-isogeny-chain-factor-base-no-fast-decomposition.md).
Unresolved; publishing this record is not scientific closure.
