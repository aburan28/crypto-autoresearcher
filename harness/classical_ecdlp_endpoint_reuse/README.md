# Classical ECDLP endpoint reuse

This is the implementation and prospective six-arm study for
`EXP-ECDLP-2b4ff1`, following the larger solver-validation study
`EXP-ECDLP-9f7772`. It compares a working classical Bernstein–Lange baseline
with bounded reuse of publicly verified endpoints. Its scientific cohort has
**not run**. The experiment remains `review_required` while its source-bound
isolated execution route and final runtime/input bindings are completed.

The question is whether reuse improves the complete setup-plus-target cost
under the specified endpoint capacity. Correct recovery, measured incremental
improvement, and novelty are separate questions. Endpoint recycling has prior
art; this implementation comparison makes no claim to a new ECDLP exponent.
The broader non-generic search remains active.

The fixed design has 64 fresh ordinary curves, two replicates and 64 public
targets per cell: 8,192 target IDs. Six arms make 768 fresh native child
invocations and 49,152 target-arm cases. The primary comparison is `harvest`
against `static_filled` after all 64 targets, charging setup and final public
verification. The filled control pays to obtain the same number of distinct
endpoints that the candidate arena can hold. Failed and censored outcomes
remain observations.

| Component | Entry point | Scope |
| --- | --- | --- |
| Native solver | `implementation/build.py` | Original static BL/rho plus capped verified-endpoint admission |
| Fresh inputs | `cohort/prepare.py` | Refuses generation before committed source/protocol/lock and post-freeze nonce |
| Public verifier | `verification/verify_public.py` | Independent point equations, answers and reuse transitions; no hidden labels |
| Worker | `execution/worker.py` | Actual source/binary/input checks, fresh children and retained raw outcomes |
| Analysis | `protocol/analysis.py` | Prespecified paired comparisons and curve-cluster uncertainty |
| Design | `../../experiments/EXP-ECDLP-2b4ff1/protocol.json` | Prospective draft; null pins are not a freeze or approval |

Software checks include 783 production checks, 805 sanitizer development
checks, 298 wire-interface checks, 14 cohort tests, 46 public-verifier tests,
18 adapter tests and 10 protocol/analysis tests. The verifier checked 30 fixed
development witnesses across six arms and a separate partial-setup censoring
case. These are software conformance results, not the new comparative study.
Component manifests retain exact source bytes, commands and failed development
attempts. Sanitizer leak detection was disabled as documented in the retained
development logs.

Build a local production executable with:

```sh
python3 harness/classical_ecdlp_endpoint_reuse/implementation/build.py --output /tmp/endpoint_reuse
```

See `execution/README.md` for the code-only image, source pin, protocol freeze,
fresh-input and isolated-worker sequence. A local image build is not a registry
publication or measurement run. The existing GitHub ecbench relay cannot run
this new executable. The exact execution gap is recorded in
`../../problems/classical-ecdlp-endpoint-reuse-isolated-runner-unavailable.md`.

Prior-work inspection and its report/figure/PDF are in
`../../docs/reports/classical-ecdlp-endpoint-reuse-20261026/`. The existing-data
motivation in `analysis/baseline-motivation/` reads the earlier sealed study;
its unsuccessful-attempt count is only an upper bound on reusable endpoints.
No claim record or empirical export for the new study is created by this source
package.
