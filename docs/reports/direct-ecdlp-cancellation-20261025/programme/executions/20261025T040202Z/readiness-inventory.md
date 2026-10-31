# Execution readiness inventory

2026-10-25. Read-only inspection of the named programme and its directly cited local source mirrors. No experiment, build, self-test, review gate, or scientific transition was performed by this inventory. This is same-session assistance, not independent review.

## Finding

The programme currently contains **zero end-to-end per-lead scientific launchers**. `READINESS.json` explicitly has `official_experiment_ids: []`, `scientific_approval: false`, and `admission_probe_run: false`. There is no programme runbook, trial plan, executor queue or goal binding. Two C++ development controls can be run now; the report can also be rebuilt. Running those controls is not executing ten scientific experiments.

All paths below are relative to `/workspace/deliverables/non-ic-ecdlp-20261025/programme` unless otherwise stated.

## Existing executable commands

| Command | What it executes | Scope limit |
| --- | --- | --- |
| `./reference/test.sh normal` | Strict compilation and fixed-fixture tagged-reference self-test | Point arithmetic, O(r) enumeration, ring/trace/boundary controls; no Boolean wire circuit or novel solver |
| `./reference/test.sh ubsan` | Same suite with UndefinedBehaviorSanitizer | Same development cases, not another scientific cohort |
| `ASAN_OPTIONS=detect_leaks=0 ./reference/test.sh asan-ubsan` | Same suite with address/undefined-behavior instrumentation | Leak detection is explicitly disabled because the earlier environment could not support it |
| `g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wshadow window-control.cpp -o <fresh-output>/window-control`, then `<fresh-output>/window-control --self-test` | Exact rank/margin fixed-window regression | Known scalar-labelled matrix control, not EC inversion |
| `./build.sh` | Graphviz/Pandoc/XeLaTeX report rendering | Document build only; mutates generated report files in its working directory, so copy sources into a fresh output directory for a replay |

`reference/fixture-discovery.cpp` is an optional three-curve point-count utility, not a discovery/confirmation cohort generator. Its source enumerates only p in {5,17,23}.

## Track-by-track inventory

| Track | Actual scientific launcher in inspected scope | Exact current gap |
| --- | --- | --- |
| D — direct tagged response | None. The existing reference command above implements development controls only. | Missing total Boolean gate/carry circuit, unique-wire checker, frozen rewrite grammar, EC-specific rewrite/constructor and composition rule. D3 also needs a complete solver and matched baselines. |
| L1 — prime-to-p sections | None. | The p²/Hensel/projective formal-group defect diagnostic is specified in prose but not implemented; no calibrated predictor/decoder or scientific fixtures. |
| L2 — EDS / elliptic nets | None. “Runnable diagnostic” in LEADS.md describes an implementable design, not an executable file. | Normalized net/coordinate recurrence and finite 15-monomial predictor are unbound to a program; nonlinear target locator absent. The cited prior Somos sieve is an excluded relation-collection route. |
| L3 — endomorphism observables | None. | No supplied endomorphism/stratum manifest or exact certificate-classification launcher; non-generic observable/decoder absent. Known eigenvalue actions are controls. |
| L4 — matchgate direct successor | None. | Missing gate tensors, exact finite basis-search implementation, all required matchgate identities and a global planar/tag construction. Original IDEA-050's factor-base pipeline is excluded. |
| L5 — radical-ladder target-local successor | None. | Branch/CRT theorem obligation and target-local constructive invariant absent. Original IDEA-111 is theorem-deferred, unimplemented and explicitly gated; its prospective artifact paths are not launchers. |
| L6 — reverse automata | None. | No fixed observable/base diagnostic launcher, public uniform state constructor or target orientation. Original IDEA-070 is rejected/merged; named verifier and theorem paths are prospective. |
| L7 — conditional coefficients | None. | No prefix interpolation diagnostic program or cheap exact coefficient evaluator. Original IDEA-156 says no contract, experiment, run or prospective artifact exists; its IC source path is excluded. Shares D's evaluator bottleneck. |
| L8 — Ax–Katz singleton successor | None. | No polynomial-circuit/degree/receipt audit launcher or exact singleton receipt constructor. Original IDEA-379's source-locator experiment is retired and its IC descent excluded. Shares D's counting bottleneck. |
| L9 — probabilistic lossy projections | None. | The repaired Kummer/group-domain/null/entropy panel is not implemented. Exact fibre records, estimator checks and a propagation decoder remain absent. |

The common scientific gaps are registered input identities and certificates, committed source/input-bound execution plan, lawful lane/ownership/queue, full output/failure archives and the repository's ordinary admission receipts. This inventory does not request or manufacture any approval.

## Source scope

- Inspected programme file inventory, `README.md`, `EXPERIMENTS.md`, `LEADS.md`, `READINESS.json`, `reference/README.md`, `reference/test.sh`, `reference/fixture-discovery.cpp`, and `window-control.md`.
- Inspected the directly cited local IDEA-050/070/111/156/379 source records and four lead rows for p-adic lifts, EDS, generic endomorphism scalar actions and lossy propagation.
- No unrelated experiment portfolio or IC launchers were searched or substituted. Local mirrors are selective; absence here does not prove that no relevant implementation exists anywhere in every repository branch.

The immediately honest execution result can distinguish development controls completed, report build completed, and the ten scientific tracks not executable. An all-ten end-to-end claim would be incorrect on these artifacts.
